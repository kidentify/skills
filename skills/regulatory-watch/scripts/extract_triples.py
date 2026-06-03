#!/usr/bin/env python3
"""
extract_triples.py — ingest any compliance artefact into normalized
(control, jurisdiction, cited-instrument) triples for regulatory-watch.

Artefact-agnostic. Auto-detects the relevant columns by header name so the same
parser works on a UK control register, a Brazil pack, a customer matrix, or a
DPIA legal-basis table. Supports .xlsx/.xlsm, .csv/.tsv. For .md/.docx, pass the
extracted text via --text and it does a generic line scan.

Usage:
    python3 extract_triples.py ARTEFACT.xlsx [--sheet NAME] [--stale-months 6]
                                             [--json OUT.json] [--map k=v,...]
                                             [--instruments-only]

Outputs a human summary to stdout and (optionally) JSON records to --json.
Each record: control_id, topic, jurisdiction, last_updated,
             cited_instruments[], control_text, is_stale, is_synthetic_jur

v2 changes (post 9-run reproducibility test):
  - Synthetic jurisdictions (GLOBAL BASELINE / ALL / DEFAULT) are detected,
    reported separately, and EXCLUDED from the staleness percentage so the
    headline number reflects only checkable rows.
  - Instrument parsing cleaned: unicode homoglyphs normalised (Cyrillic ->
    Latin), trailing-colon header fragments ("UK:", "DE:", "Various IP statutes,
    including:") dropped, so the "top cited instruments" summary is usable.
  - --instruments-only debug flag to sanity-check extraction.
"""
import argparse, csv, json, re, sys, unicodedata, datetime as dt
from collections import Counter

# header keyword -> canonical field. First match wins per column.
HEADER_HINTS = {
    "control_id":   ["control id", "control_id", "controlid", "id", "ref", "requirement id"],
    "jurisdiction": ["jurisdiction", "market", "country", "territory", "region"],
    "last_updated": ["last updated", "updated", "last_update", "date", "as of", "review date"],
    "instruments":  ["applicable laws", "laws", "regulation", "legislation", "guidance", "source", "authority"],
    "topic":        ["description", "requirement", "topic", "title", "subject", "area"],
    "control_text": ["control", "measure", "action", "implementation"],
}

# Jurisdiction values that are NOT real markets — cannot be queried in neimo.
SYNTHETIC_JUR = {"global baseline", "global", "all", "default", "baseline",
                 "instruction", "*global", "*instr"}

# Cyrillic / Greek homoglyphs that show up in copy-pasted statute names.
HOMOGLYPHS = {
    "С": "C", "с": "c",   # Cyrillic Es
    "А": "A", "а": "a",   # Cyrillic A
    "Е": "E", "е": "e",   # Cyrillic Ie
    "О": "O", "о": "o",   # Cyrillic O
    "Р": "P", "р": "p",   # Cyrillic Er
    "Х": "X", "х": "x",   # Cyrillic Ha
    "І": "I", "і": "i",   # Cyrillic Byelorussian-Ukrainian I
}

def normalise_homoglyphs(s):
    s = unicodedata.normalize("NFC", s)
    return "".join(HOMOGLYPHS.get(ch, ch) for ch in s)

def detect_columns(headers, override):
    headers_l = [(h or "").strip().lower() for h in headers]
    mapping = {}
    for field, hints in HEADER_HINTS.items():
        for hint in hints:
            for idx, h in enumerate(headers_l):
                if hint in h and idx not in mapping.values():
                    mapping[field] = idx
                    break
            if field in mapping:
                break
    for kv in (override or "").split(","):
        if "=" in kv:
            f, i = kv.split("=", 1)
            mapping[f.strip()] = int(i)
    return mapping

INSTRUMENT_SPLIT = re.compile(r"[\n;]+")
# A line that is a jurisdiction sub-header rather than an instrument, e.g.
# "UK:", "DE:", "Various IP statutes, including:" — ends with a colon and has
# no statutory year / "Act" / "Regulation" / "Code" / "Directive" token.
HEADER_FRAGMENT = re.compile(r":\s*$")
INSTRUMENT_TOKEN = re.compile(r"\b(act|regulation|code|directive|law|bill|order|"
                              r"rules?|principles?|guidance|gdpr|\d{4})\b", re.I)

def parse_instruments(cell):
    if not cell:
        return []
    cell = normalise_homoglyphs(str(cell))
    parts = [p.strip(" -•\t") for p in INSTRUMENT_SPLIT.split(cell)]
    skip = {"", "see laws below per jurisdiction.", "see laws below per territory",
            "n/a", "na", "see laws below per jurisdiction"}
    out, seen = [], set()
    for p in parts:
        pl = p.lower()
        if pl in skip or len(p) < 3:
            continue
        if len(p) <= 3 and p.isupper():            # bare country code e.g. "UK"
            continue
        if HEADER_FRAGMENT.search(p) and not INSTRUMENT_TOKEN.search(p):
            continue                               # "UK:", "Various ..., including:"
        if p not in seen:
            seen.add(p); out.append(p)
    return out

def topic_family(desc):
    if not desc:
        return ""
    return re.split(r"[:\n]", str(desc))[0].strip()[:80]

def is_synthetic(jur):
    j = (jur or "").strip().lower()
    if j in SYNTHETIC_JUR:
        return True
    return any(tok in j for tok in ("global baseline", "*global", "*instr"))

def to_date(v):
    if isinstance(v, (dt.datetime, dt.date)):
        return v.date() if isinstance(v, dt.datetime) else v
    if not v:
        return None
    s = str(v)[:10]
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return dt.datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    return None

def load_rows(path, sheet):
    if path.lower().endswith((".xlsx", ".xlsm")):
        import openpyxl
        wb = openpyxl.load_workbook(path, data_only=True)
        ws = wb[sheet] if sheet else wb[wb.sheetnames[0]]
        rows = list(ws.iter_rows(values_only=True))
        return rows[0], rows[1:]
    delim = "\t" if path.lower().endswith(".tsv") else ","
    with open(path, newline="", encoding="utf-8-sig") as f:
        r = list(csv.reader(f, delimiter=delim))
    return r[0], r[1:]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("artefact")
    ap.add_argument("--sheet")
    ap.add_argument("--stale-months", type=int, default=6)
    ap.add_argument("--json")
    ap.add_argument("--map", help="explicit field=colindex overrides, comma-sep")
    ap.add_argument("--instruments-only", action="store_true",
                    help="print the cleaned instrument list and exit (debug)")
    a = ap.parse_args()

    headers, raw = load_rows(a.artefact, a.sheet)
    m = detect_columns(headers, a.map)
    required = {"jurisdiction"}
    if not required <= set(m):
        print("Could not auto-detect required columns. Headers seen:")
        for i, h in enumerate(headers):
            print(f"  [{i}] {h}")
        print("Pass --map e.g. --map jurisdiction=3,control_id=2,last_updated=0,instruments=6,topic=4")
        sys.exit(2)

    def cell(row, field):
        idx = m.get(field)
        return row[idx] if idx is not None and idx < len(row) else None

    records, jur_c, instr_c = [], Counter(), Counter()
    stale_cut = dt.date.today() - dt.timedelta(days=30 * a.stale_months)
    stale_n = 0           # stale among CHECKABLE (non-synthetic) rows only
    checkable_n = 0
    synthetic_n = 0
    dates = []
    for row in raw:
        if not any(row):
            continue
        jur = (str(cell(row, "jurisdiction")) if cell(row, "jurisdiction") else "").strip()
        if jur.upper() in ("INSTRUCTION", ""):    # skip instruction rows entirely
            continue
        synth = is_synthetic(jur)
        d = to_date(cell(row, "last_updated"))
        if d:
            dates.append(d)
        if not synth:
            checkable_n += 1
            if d and d < stale_cut:
                stale_n += 1
        else:
            synthetic_n += 1
        instrs = parse_instruments(cell(row, "instruments"))
        rec = {
            "control_id": str(cell(row, "control_id") or "").strip(),
            "topic": topic_family(cell(row, "topic")),
            "jurisdiction": jur,
            "last_updated": d.isoformat() if d else None,
            "cited_instruments": instrs,
            "control_text": (str(cell(row, "control_text")) if cell(row, "control_text") else "")[:300],
            "is_stale": bool(d and d < stale_cut),
            "is_synthetic_jur": synth,
        }
        records.append(rec)
        jur_c[jur] += 1
        if not synth:
            for ins in instrs:
                instr_c[ins] += 1

    if a.instruments_only:
        print("Cleaned cited instruments (checkable rows, by frequency):")
        for ins, n in instr_c.most_common(40):
            print(f"   {n:>3}  {ins}")
        return

    total = len(records)
    stale_pct = (100 * stale_n // checkable_n) if checkable_n else 0
    print("=" * 64)
    print(f"ARTEFACT: {a.artefact}")
    print(f"Total controllable rows parsed: {total}")
    print(f"  Checkable (real-market) rows: {checkable_n}")
    print(f"  Synthetic-jurisdiction rows (NOT neimo.-queryable): {synthetic_n}")
    print(f"Jurisdictions: {dict(jur_c)}")
    if dates:
        print(f"last_updated range: {min(dates)} -> {max(dates)}")
    print(f"Stale among CHECKABLE rows (> {a.stale_months} mo, older than "
          f"{stale_cut}): {stale_n} of {checkable_n} ({stale_pct}%)")
    if synthetic_n:
        print(f"NOTE: {synthetic_n} synthetic-jurisdiction rows excluded from the "
              f"staleness %. Decompose to real markets or mark UNVERIFIED en bloc.")
    print("Top cited instruments (checkable rows):")
    for ins, n in instr_c.most_common(12):
        print(f"   {n:>3}  {ins[:70]}")
    print("=" * 64)

    if a.json:
        with open(a.json, "w") as f:
            json.dump(records, f, indent=2)
        print(f"wrote {len(records)} records -> {a.json}")

if __name__ == "__main__":
    main()
