#!/usr/bin/env python3
"""Build the official PP Tunas self-assessment worksheet (Kepmen 142/2026) as .xlsx.

The instrument is fully specified by law: Appendix II of Ministerial Decree
No. 142/2026 defines seven aspects, 58 coded Assessment Parameters, each with a FIXED
risk weight, a binary YES/NO status, and a deterministic aggregation rule. None of
that is a judgement call, so the script does not ask the model to invent rows or
scores. It:

  1. loads the frozen parameter catalog (references/kepmen142_parameters.json),
  2. takes ONLY the assessor's per-parameter status + justification as input,
  3. computes every Parameter Risk Score, Aspect Risk Score, the >50% aspect
     high-risk flags, and the overall HIGH/LOW-RISK profile, exactly per Chapter IV,
  4. renders the worksheet sheet-per-aspect in the order the law prints them,
  5. appends k-ID's *supplementary, non-regulatory* tabs (Remediation & gating,
     Obligations, Sources) clearly fenced off so no one mistakes them for the filing.

SCORING (Kepmen 142, Appendix II, Chapter IV)
---------------------------------------------
  Parameter Risk Score = weight% x status, where status = 1 when the assessor marks
  the parameter in its *weighted column* (YES for risk-bearing parameters; NO for
  protective parameters where ABSENCE of the control is the risk), else 0.
  Aspect Risk Score    = sum of Parameter Risk Scores in that aspect.
  Aspect is HIGH RISK  when Aspect Risk Score > 50%.
  PLF profile is HIGH-RISK if AT LEAST ONE aspect exceeds 50%.
  The Director General makes the final, binding determination after verification.

INPUT JSON SHAPE
----------------
{
  "product": {
    "pse_name": "Acme Inc.",                  # Identity of PSE / ESO
    "plf_name": "Acme Chat",                   # Product, Service, or Feature
    "assessment_date": "2026-06-10",
    "assessor": "Multidisciplinary team (Product, T&S, Legal, Security)",
    "summary": "Free social app with public voice chat, open to all ages..."
  },
  "answers": {
    # key = parameter code; value = the assessor's finding.
    # "status": "FOUND" or "NOT_FOUND" — the real-world presence of the technical
    #           configuration in the PLF. The script maps this to the worksheet's
    #           YES/NO columns and decides whether the weight applies, using the
    #           catalog's weight_column. You answer about reality; the script scores.
    # "justification": the law's "Specific Technical Configuration" column.
    # "evidence": supporting proof reference (Document / Model Card / UX survey /
    #           other) — Ch. II.C requires evidence per parameter.
    "KK01": {"status": "FOUND",     "justification": "",                       "evidence": "Recommender spec REC-2026-03"},
    "KN06": {"status": "FOUND",     "justification": "Block/report in v4.2.",  "evidence": "Screenshots; T&S policy s.4"},
    "DP04": {"status": "NOT_FOUND", "justification": "DPIA done 2026-05.",      "evidence": "DPIA-2026-014"}
    # ... ideally one entry per parameter; unanswered parameters render blank and
    #     are flagged as incomplete (the regulator rejects incomplete worksheets).
  },

  # Appendix I in-scope screening (OPTIONAL, keys A-E); any one "Yes" => in scope:
  "scope_screening": {
    "A": {"fulfilled": "No",  "note": "ToS sets 13+; no child-directed wording."},
    "D": {"fulfilled": "Yes", "note": "Cartoon avatars + gamified streaks."}
  },

  # Assessor team (Ch. II.B); matched by leading keyword of the required function:
  "assessor_team": [
    {"function": "Product", "name": "...", "title": "...", "aspects_reviewed": "all", "date": "", "signature": ""},
    {"function": "Trust & Safety", "name": "...", "title": "...", "aspects_reviewed": "a,b,f", "date": "", "signature": ""}
  ],

  # ---- everything below is OPTIONAL and SUPPLEMENTARY (k-ID value-add) ----
  "remediation": [
    {"feature": "Voice chat (public)", "min_age": "16", "threshold_age": "18",
     "assurance_required": "Yes", "kid_mechanism": "Session permission + AgeKit+",
     "status": "Ungated", "gap": "No age check before voice chat."}
  ],
  "obligations": [
    {"requirement": "Age assurance", "applies": "Yes", "current_status": "Not implemented",
     "gap": "No age check at signup.", "action": "Deploy assurance commensurate with risk.",
     "kid_mechanism": "Age Gate + AgeKit+", "owner": "Eng",
     "citation": "PP 17/2025 Art. 22 (confirm live via neimo.)"}
  ],
  "sources": [
    {"topic": "Risk instrument", "regulation": "Kepmen 142/2026", "article": "Appendix II",
     "url": "https://...", "verification": "embedded (fixed law)"}
  ]
}

USAGE
-----
    python build_self_assessment.py --in answers.json \
        --catalog references/kepmen142_parameters.json \
        --out "PP_Tunas_Self_Assessment_Worksheet.xlsx"

Requires openpyxl (pip install openpyxl --break-system-packages).
"""
import argparse
import json
import os
import sys

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

# ---- palette -------------------------------------------------------------
NAVY = "1F2A44"
SLATE = "33415C"
PAPER = "F4F6FA"
WHITE = "FFFFFF"
RISK_FILL = "F4CCCC"      # weight applied (risk counted)
SAFE_FILL = "D9EAD3"      # weight not applied (mitigated / control present)
BLANK_FILL = "FCE5CD"     # unanswered — incomplete
HIGH_BANNER = "CC0000"
LOW_BANNER = "38761D"
AMBER = "FFF2CC"
SUPP_FILL = "EAD1DC"      # supplementary-tab marker (visually distinct from worksheet)

THIN = Side(style="thin", color="C8CFDC")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
WRAP = Alignment(wrap_text=True, vertical="top")
CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)

PROVISO = (
    "AI-ASSISTED DRAFT — REVIEW REQUIRED. This worksheet was prepared with AI "
    "assistance using the parameter catalog fixed in Kepmen 142/2026 and findings "
    "supplied by the assessor. The seven-factor YES/NO determinations and the "
    "supporting evidence are the assessor's responsibility. It is a structured aid, "
    "NOT legal advice, and must be reviewed by a qualified, multidisciplinary "
    "assessor and/or counsel before it is filed. The Director General (Komdigi) "
    "makes the final, binding HIGH/LOW-risk determination after verification."
)


# ---- Appendix I: in-scope screening indicators (verbatim from Kepmen 142) --
SCOPE_INDICATORS = [
    ("A", "Terms, conditions, rules, or internal policies indicate the PLF is intended to be used/accessed by children."),
    ("B", "Strong evidence that the user composition routinely accessing the PLF consists of children (a 'significant number' = a non-incidental proportion with routine access, at least 25 child users)."),
    ("C", "Advertisements for the PLF are directed at children."),
    ("D", "Design elements are created/presented to attract children (bright colours/cartoons/avatars; impulsive exploratory interaction; gamification)."),
    ("E", "The PLF is substantially similar or identical to PLF proven to be used/accessed by children."),
]

# ---- Chapter II.B: required Assessor functions (multidisciplinary team) -----
ASSESSOR_FUNCTIONS = [
    ("Product development team", "Confirms PLF features, technical configurations, and planned changes are reflected accurately."),
    ("Policy development / internal regulatory team", "Aligns the assessment with internal policy and PP TUNAS / Permen 9/2026 / Kepmen 142/2026."),
    ("User protection / Trust & Safety team", "Assesses contact, content, psychological, and conduct risks and mitigations."),
    ("System security & data protection team", "Reviews the personal-data security aspect, the DPIA, privacy notice, and DPO function."),
    ("Experts or consultants (if necessary)", "Engaged where in-house expertise is insufficient (see minimum-expertise note below)."),
]
ASSESSOR_MIN_EXPERTISE = (
    "Where the PSE appoints an external party as Assessor, the Assessor shall possess, at a minimum, "
    "expertise in: child psychology; child physiology; information technology; system security and "
    "Personal Data protection; legal expertise; and digital marketing expertise. (Kepmen 142/2026, App. II, Ch. II.B.4)"
)


def _hdr(cell, fill=SLATE):
    cell.font = Font(bold=True, color=WHITE, size=10)
    cell.fill = PatternFill("solid", fgColor=fill)
    cell.alignment = CENTER
    cell.border = BORDER


def _weight_applies(status, weight_column):
    """The weight counts when the assessor's real-world finding lands in the
    column where the law prints the weight.

    Risk-bearing parameter (weight under YES): weight applies when FOUND.
    Protective parameter   (weight under NO):  weight applies when NOT_FOUND
                                               (absence of the control IS the risk)."""
    if status not in ("FOUND", "NOT_FOUND"):
        return None  # unanswered
    if weight_column == "YES":
        return status == "FOUND"
    return status == "NOT_FOUND"


def _score_aspect(aspect, answers):
    rows, subtotal, incomplete = [], 0.0, 0
    for p in aspect["parameters"]:
        ans = answers.get(p["code"], {})
        status = ans.get("status")
        applies = _weight_applies(status, p["weight_column"])
        if applies is None:
            incomplete += 1
            score = None
        else:
            score = round(p["weight"], 2) if applies else 0.0
            subtotal += score
        rows.append({"p": p, "status": status,
                     "justification": ans.get("justification", ""),
                     "evidence": ans.get("evidence", ""),
                     "applies": applies, "score": score})
    return rows, round(subtotal, 2), incomplete


def _yn_marks(status, weight_column):
    """Return (yes_mark, no_mark) ticks for the worksheet's YES / NO columns."""
    if status == "FOUND":
        return "✓", ""
    if status == "NOT_FOUND":
        return "", "✓"
    return "", ""


def build(data, catalog, out_path):
    wb = Workbook()
    p = data.get("product", {})
    answers = data.get("answers", {})

    # ===== Sheet 1: Summary & Determination ==============================
    ws = wb.active
    ws.title = "Determination"
    ws.merge_cells("A1:F1")
    t = ws["A1"]
    t.value = ("PP TUNAS — Self-Assessment Worksheet on Risk Levels of Products, "
               "Services, and Features (PLF)")
    t.font = Font(bold=True, color=WHITE, size=13)
    t.fill = PatternFill("solid", fgColor=NAVY)
    t.alignment = CENTER
    ws.row_dimensions[1].height = 32
    ws.merge_cells("A2:F2")
    s = ws["A2"]
    s.value = ("Instrument fixed by Kepmen Komdigi No. 142/2026, Appendix II — "
               "implementing PP No. 17/2025 (PP TUNAS) and Permen No. 9/2026.")
    s.font = Font(italic=True, color=WHITE, size=9)
    s.fill = PatternFill("solid", fgColor=SLATE)
    s.alignment = CENTER

    meta = [
        ("Identity of PSE / ESO", p.get("pse_name", "")),
        ("Product, Service, or Feature (PLF)", p.get("plf_name", "")),
        ("Date of completion", p.get("assessment_date", "")),
        ("Assessor (multidisciplinary team)", p.get("assessor", "")),
        ("PLF summary", p.get("summary", "")),
    ]
    r = 4
    for label, val in meta:
        c = ws.cell(r, 1, label)
        c.font = Font(bold=True)
        c.fill = PatternFill("solid", fgColor=PAPER)
        c.border = BORDER
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=6)
        v = ws.cell(r, 2, val)
        v.alignment = WRAP
        v.border = BORDER
        r += 1

    # ---- compute every aspect -------------------------------------------
    r += 1
    th = ws.cell(r, 1, "Risk profile by aspect (Aspect Risk Score = sum of weighted parameters; HIGH if > 50%)")
    th.font = Font(bold=True, size=11)
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=6)
    r += 1
    for i, h in enumerate(["Aspect", "Code", "Aspect Risk Score (%)", "Classification", "Incomplete params"], 1):
        _hdr(ws.cell(r, i, h))
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=1)  # keep layout simple
    r += 1

    any_high = False
    any_incomplete = 0
    aspect_results = []
    for aspect in catalog["aspects"]:
        rows, subtotal, incomplete = _score_aspect(aspect, answers)
        high = subtotal > 50
        any_high = any_high or high
        any_incomplete += incomplete
        aspect_results.append((aspect, rows, subtotal, incomplete, high))

        ws.cell(r, 1, f"({aspect['key']}) {aspect['title']}").alignment = WRAP
        ws.cell(r, 2, aspect["code_prefix"]).alignment = CENTER
        sc = ws.cell(r, 3, subtotal)
        sc.alignment = CENTER
        sc.fill = PatternFill("solid", fgColor=RISK_FILL if high else SAFE_FILL)
        cl = ws.cell(r, 4, "HIGH RISK" if high else "Low risk")
        cl.alignment = CENTER
        cl.font = Font(bold=True, color=(HIGH_BANNER if high else LOW_BANNER))
        inc = ws.cell(r, 5, incomplete if incomplete else "")
        inc.alignment = CENTER
        if incomplete:
            inc.fill = PatternFill("solid", fgColor=BLANK_FILL)
        for cc in range(1, 6):
            ws.cell(r, cc).border = BORDER
        r += 1

    # ---- overall determination banner -----------------------------------
    r += 1
    result = "HIGH-RISK" if any_high else "LOW-RISK"
    banner = HIGH_BANNER if any_high else LOW_BANNER
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=6)
    b = ws.cell(r, 1, f"COMPUTED RISK PROFILE: {result}   "
                      f"(HIGH-RISK if any single aspect exceeds 50%)")
    b.font = Font(bold=True, color=WHITE, size=13)
    b.fill = PatternFill("solid", fgColor=banner)
    b.alignment = CENTER
    ws.row_dimensions[r].height = 28
    r += 1
    if any_incomplete:
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=6)
        w = ws.cell(r, 1, f"WARNING: {any_incomplete} parameter(s) are unanswered. "
                          f"Komdigi rejects incomplete worksheets — answer every parameter before filing.")
        w.font = Font(bold=True, color="9C0006", size=10)
        w.fill = PatternFill("solid", fgColor=BLANK_FILL)
        w.alignment = WRAP
        w.border = BORDER
        r += 1
    r += 1
    ws.merge_cells(start_row=r, start_column=1, end_row=r + 1, end_column=6)
    note = ws.cell(r, 1, PROVISO)
    note.font = Font(bold=True, italic=True, color="9C0006", size=9)
    note.fill = PatternFill("solid", fgColor=AMBER)
    note.alignment = WRAP
    note.border = BORDER
    ws.row_dimensions[r].height = 44

    ws.column_dimensions["A"].width = 40
    ws.column_dimensions["B"].width = 10
    ws.column_dimensions["C"].width = 18
    ws.column_dimensions["D"].width = 16
    ws.column_dimensions["E"].width = 16
    ws.column_dimensions["F"].width = 14

    # ===== Sheet 2: Appendix I — in-scope screening =====================
    wss = wb.create_sheet("Scope screening (App. I)")
    wss.merge_cells("A1:D1")
    h = wss["A1"]
    h.value = ("Appendix I — Is the PLF 'used or accessed by children'? "
               "Fulfilling ANY ONE indicator puts the PLF in scope for this assessment.")
    h.font = Font(bold=True, color=WHITE, size=10)
    h.fill = PatternFill("solid", fgColor=NAVY)
    h.alignment = CENTER
    wss.row_dimensions[1].height = 30
    for i, c in enumerate(["Indicator", "Description", "Fulfilled? (Yes/No)", "Evidence / note"], 1):
        _hdr(wss.cell(2, i, c))
    for i, w in enumerate([10, 60, 16, 34], 1):
        wss.column_dimensions[get_column_letter(i)].width = w
    scope = data.get("scope_screening", {})
    any_scope = False
    rr = 3
    for code, desc in SCOPE_INDICATORS:
        sd = scope.get(code, {})
        ful = str(sd.get("fulfilled", "")).strip()
        if ful.lower() in ("yes", "true", "y", "1"):
            any_scope = True
        wss.cell(rr, 1, code).alignment = CENTER
        wss.cell(rr, 2, desc).alignment = WRAP
        fc = wss.cell(rr, 3, ful)
        fc.alignment = CENTER
        if ful.lower() in ("yes", "true", "y", "1"):
            fc.fill = PatternFill("solid", fgColor=RISK_FILL)
        wss.cell(rr, 4, sd.get("note", "")).alignment = WRAP
        for cc in range(1, 5):
            wss.cell(rr, cc).border = BORDER
        rr += 1
    rr += 1
    wss.merge_cells(start_row=rr, start_column=1, end_row=rr, end_column=4)
    verdict = ("IN SCOPE — the risk-level self-assessment is required."
               if any_scope else
               "Screening recorded — if no indicator is fulfilled, document the basis; "
               "Komdigi may still assess in-scope status at verification.")
    vc = wss.cell(rr, 1, verdict)
    vc.font = Font(bold=True, color=WHITE)
    vc.fill = PatternFill("solid", fgColor=(HIGH_BANNER if any_scope else SLATE))
    vc.alignment = WRAP
    vc.border = BORDER
    wss.row_dimensions[rr].height = 26

    # ===== One sheet per aspect (the worksheet proper) ===================
    for aspect, rows, subtotal, incomplete, high in aspect_results:
        title = f"{aspect['code_prefix']} — ({aspect['key']})"
        wsa = wb.create_sheet(title[:31])
        wsa.merge_cells("A1:I1")
        h = wsa["A1"]
        h.value = f"Aspect ({aspect['key']}): {aspect['title']}"
        h.font = Font(bold=True, color=WHITE, size=11)
        h.fill = PatternFill("solid", fgColor=NAVY)
        h.alignment = CENTER
        wsa.row_dimensions[1].height = 26

        cols = ["Code", "Assessed Indicator", "Technical Configuration",
                "Assessment Parameter", "YES", "NO", "Risk Weight (%)",
                "Specific Technical Configuration (justification)",
                "Evidence (Doc / Model Card / UX survey)", "Risk Score Calc"]
        for i, c in enumerate(cols, 1):
            _hdr(wsa.cell(2, i, c))
        widths = [8, 24, 20, 38, 6, 6, 12, 30, 24, 13]
        for i, w in enumerate(widths, 1):
            wsa.column_dimensions[get_column_letter(i)].width = w

        rr = 3
        for row in rows:
            pr = row["p"]
            yes_m, no_m = _yn_marks(row["status"], pr["weight_column"])
            wsa.cell(rr, 1, pr["code"])
            wsa.cell(rr, 2, pr["indicator"])
            wsa.cell(rr, 3, pr["technical_configuration"])
            wsa.cell(rr, 4, pr["assessment_parameter"])
            wsa.cell(rr, 5, yes_m)
            wsa.cell(rr, 6, no_m)
            # show the weight in the column the law uses, as a hint
            wsa.cell(rr, 7, f"{pr['weight']:.2f}  (in {pr['weight_column']} col)")
            wsa.cell(rr, 8, row["justification"])
            wsa.cell(rr, 9, row["evidence"])
            sc_val = ("" if row["score"] is None else row["score"])
            sc = wsa.cell(rr, 10, sc_val)
            if row["applies"] is True:
                sc.fill = PatternFill("solid", fgColor=RISK_FILL)
            elif row["applies"] is False:
                sc.fill = PatternFill("solid", fgColor=SAFE_FILL)
            else:
                sc.fill = PatternFill("solid", fgColor=BLANK_FILL)
            for cc in range(1, 11):
                cell = wsa.cell(rr, cc)
                cell.border = BORDER
                cell.alignment = CENTER if cc in (1, 5, 6, 7, 10) else WRAP
            if pr.get("polarity_flag"):
                fcell = wsa.cell(rr, 4)
                fcell.value = pr["assessment_parameter"] + "  [⚠ POLARITY: " + pr["polarity_flag"] + "]"
                fcell.font = Font(color="9C0006")
            rr += 1

        # subtotal row
        wsa.merge_cells(start_row=rr, start_column=1, end_row=rr, end_column=9)
        tcell = wsa.cell(rr, 1, f"ASPECT RISK SCORE  —  {'HIGH RISK (> 50%)' if high else 'Low risk (<= 50%)'}")
        tcell.font = Font(bold=True, color=WHITE)
        tcell.fill = PatternFill("solid", fgColor=(HIGH_BANNER if high else LOW_BANNER))
        tcell.alignment = Alignment(horizontal="right", vertical="center")
        tot = wsa.cell(rr, 10, subtotal)
        tot.font = Font(bold=True)
        tot.alignment = CENTER
        tot.fill = PatternFill("solid", fgColor=(RISK_FILL if high else SAFE_FILL))
        for cc in range(1, 11):
            wsa.cell(rr, cc).border = BORDER
        wsa.freeze_panes = "A3"

    # ===== Assessor & sign-off (Chapter II.B) ===========================
    wsm = wb.create_sheet("Assessor & sign-off")
    wsm.merge_cells("A1:G1")
    h = wsm["A1"]
    h.value = ("Assessor — multidisciplinary team (Kepmen 142/2026, App. II, Ch. II.B). "
               "The scope of risk to children spans content, contact, consumer, data, "
               "addiction, psychological, and physiological aspects, so the assessment "
               "must not be done from a single (e.g. engineering) perspective.")
    h.font = Font(bold=True, color=WHITE, size=10)
    h.fill = PatternFill("solid", fgColor=NAVY)
    h.alignment = WRAP
    wsm.row_dimensions[1].height = 44
    cols = ["Required function (Ch. II.B.2)", "Why this lens is required", "Name",
            "Title / org", "Aspects reviewed", "Date", "Signature / approval"]
    for i, c in enumerate(cols, 1):
        _hdr(wsm.cell(2, i, c))
    for i, w in enumerate([30, 38, 18, 20, 22, 12, 18], 1):
        wsm.column_dimensions[get_column_letter(i)].width = w
    team = {t.get("function", ""): t for t in data.get("assessor_team", [])}
    rr = 3
    for func, why in ASSESSOR_FUNCTIONS:
        # fuzzy match input by leading keyword
        match = {}
        for k, v in team.items():
            if k and (k.lower() in func.lower() or func.split()[0].lower() in k.lower()):
                match = v
                break
        wsm.cell(rr, 1, func).font = Font(bold=True)
        wsm.cell(rr, 2, why).alignment = WRAP
        wsm.cell(rr, 3, match.get("name", ""))
        wsm.cell(rr, 4, match.get("title", ""))
        wsm.cell(rr, 5, match.get("aspects_reviewed", "")).alignment = WRAP
        wsm.cell(rr, 6, match.get("date", ""))
        wsm.cell(rr, 7, match.get("signature", ""))
        for cc in range(1, 8):
            cell = wsm.cell(rr, cc)
            cell.border = BORDER
            if cell.alignment.wrap_text is None:
                cell.alignment = WRAP
        rr += 1
    rr += 1
    wsm.merge_cells(start_row=rr, start_column=1, end_row=rr + 1, end_column=7)
    me = wsm.cell(rr, 1, ASSESSOR_MIN_EXPERTISE)
    me.font = Font(italic=True, color="660000", size=9)
    me.fill = PatternFill("solid", fgColor=AMBER)
    me.alignment = WRAP
    me.border = BORDER
    wsm.row_dimensions[rr].height = 40

    # ===== Supplementary tabs (k-ID value-add — NOT part of the filing) ==
    def _supp_banner(wsx, ncols, text):
        wsx.merge_cells(start_row=1, start_column=1, end_row=1, end_column=ncols)
        c = wsx.cell(1, 1, text)
        c.font = Font(bold=True, color="660000", size=10)
        c.fill = PatternFill("solid", fgColor=SUPP_FILL)
        c.alignment = CENTER
        c.border = BORDER
        wsx.row_dimensions[1].height = 26

    SUPP_TAG = ("SUPPLEMENTARY — k-ID engineering aid, NOT part of the Kepmen 142 "
                "self-assessment submission to Komdigi.")

    rem = data.get("remediation", [])
    if rem:
        wsx = wb.create_sheet("Remediation & gating (supp.)")
        cols = ["Feature", "Minimum age", "Threshold age", "Age assurance required?",
                "k-ID enforcement mechanism", "Current status", "Gap"]
        _supp_banner(wsx, len(cols), SUPP_TAG)
        for i, c in enumerate(cols, 1):
            _hdr(wsx.cell(2, i, c))
        widths = [26, 12, 13, 16, 30, 16, 30]
        for i, w in enumerate(widths, 1):
            wsx.column_dimensions[get_column_letter(i)].width = w
        rr = 3
        for f in rem:
            vals = [f.get("feature", ""), f.get("min_age", ""), f.get("threshold_age", ""),
                    f.get("assurance_required", ""), f.get("kid_mechanism", ""),
                    f.get("status", ""), f.get("gap", "")]
            for i, v in enumerate(vals, 1):
                cell = wsx.cell(rr, i, v)
                cell.border = BORDER
                cell.alignment = CENTER if i in (2, 3, 4) else WRAP
            rr += 1
        wsx.freeze_panes = "A3"

    obl = data.get("obligations", [])
    if obl:
        wsx = wb.create_sheet("Obligations (supp.)")
        cols = ["PP Tunas obligation", "Applies?", "Current status", "Gap",
                "Action", "k-ID mechanism", "Owner", "Citation"]
        _supp_banner(wsx, len(cols), SUPP_TAG + "  Ground every citation in a live neimo. lookup.")
        for i, c in enumerate(cols, 1):
            _hdr(wsx.cell(2, i, c))
        widths = [26, 9, 20, 26, 28, 24, 10, 32]
        for i, w in enumerate(widths, 1):
            wsx.column_dimensions[get_column_letter(i)].width = w
        rr = 3
        for o in obl:
            vals = [o.get("requirement", ""), o.get("applies", ""), o.get("current_status", ""),
                    o.get("gap", ""), o.get("action", ""), o.get("kid_mechanism", ""),
                    o.get("owner", ""), o.get("citation", "")]
            for i, v in enumerate(vals, 1):
                cell = wsx.cell(rr, i, v)
                cell.border = BORDER
                cell.alignment = CENTER if i in (2, 7) else WRAP
            rr += 1
        wsx.freeze_panes = "A3"

    src = data.get("sources", [])
    if src:
        wsx = wb.create_sheet("Sources (supp.)")
        cols = ["Topic", "Regulation", "Article", "Source URL", "Verification"]
        _supp_banner(wsx, len(cols), SUPP_TAG)
        for i, c in enumerate(cols, 1):
            _hdr(wsx.cell(2, i, c))
        widths = [26, 26, 18, 50, 18]
        for i, w in enumerate(widths, 1):
            wsx.column_dimensions[get_column_letter(i)].width = w
        rr = 3
        for sdat in src:
            vals = [sdat.get("topic", ""), sdat.get("regulation", ""), sdat.get("article", ""),
                    sdat.get("url", ""), sdat.get("verification", "")]
            for i, v in enumerate(vals, 1):
                cell = wsx.cell(rr, i, v)
                cell.border = BORDER
                cell.alignment = WRAP
            rr += 1
        wsx.freeze_panes = "A3"

    wb.save(out_path)
    return out_path, result, any_incomplete, aspect_results


def main():
    ap = argparse.ArgumentParser(description="Build the PP Tunas (Kepmen 142) self-assessment worksheet .xlsx")
    ap.add_argument("--in", dest="infile", required=True, help="Assessor answers JSON")
    ap.add_argument("--catalog", dest="catalog",
                    default=os.path.join(os.path.dirname(__file__), "..", "references", "kepmen142_parameters.json"),
                    help="Path to kepmen142_parameters.json")
    ap.add_argument("--out", dest="outfile", required=True, help="Output .xlsx path")
    args = ap.parse_args()
    with open(args.infile, encoding="utf-8") as fh:
        data = json.load(fh)
    with open(args.catalog, encoding="utf-8") as fh:
        catalog = json.load(fh)
    path, result, incomplete, _ = build(data, catalog, args.outfile)
    print(f"Wrote {path}")
    print(f"Computed profile: {result}" + (f"  ({incomplete} parameter(s) unanswered)" if incomplete else ""))


if __name__ == "__main__":
    sys.exit(main())
