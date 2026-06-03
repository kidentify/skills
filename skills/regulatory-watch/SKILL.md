---
name: regulatory-watch
description: >-
  Keeps any compliance artefact current against regulatory reality. Takes a
  control register, requirements matrix, DPIA legal-basis table, or jurisdiction
  pack (xlsx / csv / docx / md), extracts every (control, jurisdiction, cited
  instrument) triple, checks each against neimo. (k-ID's regulatory KB) with a
  web confirmation pass, and emits a severity-flagged change report: NEW
  requirements, AMENDED thresholds or deadlines, NOW-STALE rows, DEPRECATED
  items. Artefact-agnostic — the UK + Global baselines sheet is one input shape.
  Trigger on "check my compliance sheet for changes", "is this register still
  current", "regulatory watch on [artefact]", "what's changed since we updated
  [doc]", "diff [artefact] against neimo.", or any request to detect regulatory
  drift in a document. Use EVEN IF the user doesn't say "neimo." NOT for building
  a register from scratch (use onboarding skills) or implementing controls in code.
license: Apache-2.0
metadata:
  version: "0.1.0"
  vendor: k-ID
---

# regulatory-watch

## What this is for

Compliance artefacts rot. A control register, a DPIA, a jurisdiction pack — each
one captures the regulatory position *as of the day it was written*. Laws move,
regulators issue guidance, enforcement reshapes interpretation. The artefact
doesn't know. This skill is the standing mechanism that re-checks any such
artefact against the current position and tells you, with citations and a
severity flag, what no longer matches reality.

It is deliberately **artefact-agnostic**. The same logic that watches the UK +
Global baselines sheet watches a Brazil pack, a customer's control matrix, or a
DPIA's legal-basis table. You point it at a file; it figures out the shape.

> **Quality bar.** This skill is shared with k-ID clients. Two operators running
> it on the same artefact on the same day must produce the **same findings** —
> not merely defensible findings. Recall variance and citation drift are the two
> failure modes this version is built to eliminate. Follow the neimo. query
> protocol and the required sweep exactly; they are not suggestions.

## Source-of-truth hierarchy (do not skip)

1. **neimo. (primary).** k-ID's structured regulatory KB across 200+ markets —
   age thresholds, parental consent, data protection, enforcement, plus the
   **Legal Horizons** newsletter archive of recent developments. Every claim,
   threshold, date, and citation in the report MUST come from a neimo. tool
   result in the current session. Never use training data for a regulatory fact.
   Write the brand as **neimo.** (lowercase, trailing period) — never "Neimo".
2. **Named-instrument web confirmation (secondary).** Artefacts cite specific
   instruments (e.g. the Online Safety Act, Ofcom codes, the AADC, COPPA,
   ECA Digital). neimo. is the signal; a targeted `WebSearch` / `web_fetch` of
   the named regulator or legislation page is the confirmation. Use it to
   corroborate a neimo. finding or to date a development — not to manufacture a
   change neimo. doesn't support.
3. **If neimo. returns empty** for a market/topic (`{"rows": []}`, `[]`, or a
   null value field), say so explicitly — "neimo. does not have data for this
   market/topic yet" — and do NOT fall back to memory. Flag the row as
   `UNVERIFIED`, not as `NO CHANGE`.
4. **When neimo. and the web confirmation disagree on a development's status,
   flag the direction explicitly.** Two cases:
   - **`neimo.-lag`** — neimo. is staler than the web (neimo. calls something a
     "Bill" but legislation.gov.uk shows it received Royal Assent and is now an Act;
     neimo. says "proposed" but it is in force). Report **neimo.'s substance as the
     finding**, state the **current status from the web confirmation**, add the
     `neimo.-lag` flag, and route it to the neimo. team. Do NOT silently upgrade
     neimo.'s wording as if neimo. said it; do NOT suppress the finding.
   - **`artefact-lag`** — the artefact is staler than neimo. (the register cites an
     instrument at "draft / consultation" stage but neimo. shows it finalised / in
     force; the OSA-Ofcom-codes case is the canonical example). This is a normal
     AMENDED finding against neimo.; tag it `artefact-lag` so the reader sees the
     register — not neimo. — is the thing behind. Do NOT label this `neimo.-lag`.

## Execution environment (read before step 1)

The skill files and the artefact may live on a VM mount the host-side file tools
(`Read`/`Write`/`Edit`) cannot reach. **Do all artefact ingestion, the parser
run, and the report write through the shell** (bash), using absolute paths. If a
`Read` of the SKILL.md, the parser, or the artefact fails with a path error, that
is expected — switch to `cat`/`python3` in the shell. Write the finished report
to the shell-visible outputs path, not via the host `Write` tool.

## The procedure

### 1. Ingest the artefact into triples

Run `scripts/extract_triples.py <artefact-path> --json /tmp/triples.json` (via
the shell). It handles `.xlsx`, `.csv`, `.tsv`, and falls back to a generic text
scan for `.md` / `.docx`-extracted text. It emits one normalized record per
controllable row:

```
{ control_id, topic, jurisdiction, last_updated, cited_instruments[], control_text }
```

The parser auto-detects the column names it needs. If detection fails it prints
the headers it saw so you can pass an explicit `--map`. Read its summary block
before going further — jurisdictions present, staleness distribution, top cited
instruments. That summary scopes the run.

**Synthetic / non-market jurisdictions.** If a jurisdiction value is not a real
market (e.g. `GLOBAL BASELINE`, `ALL`, `DEFAULT`, `INSTRUCTION`), it is **not** a
neimo. market and cannot be queried as one. The parser already drops
`INSTRUCTION` rows and reports any synthetic jurisdiction separately, and it
**excludes synthetic-jurisdiction rows from the staleness percentage** so the
headline number reflects only checkable rows. Handle synthetic jurisdictions one
of two ways, in this order of preference:
  (a) **Decompose** — if the rows enumerate concrete markets in their instrument
      or control text (e.g. a Global Baseline loot-box row that rolls up ES/FR/BR
      law), check each named market with `lookup_regulation` / `lookup_legal_horizons`.
  (b) **Mark UNVERIFIED en bloc** — if undecomposable, flag the whole class
      UNVERIFIED for human review and do not invent a market for it.

### 2. Decide the check set (tiering)

Tiering only ever *adds* fast-mover re-checks on top of the required baseline
sweep (step 3). It never *subtracts* from it. The baseline sweep is mandatory on
every run; this is what keeps recall constant across operators.

- **Fast-movers** — instruments under active consultation / recent enforcement
  (in 2026 UK terms: OSA + Ofcom codes, the AADC / Children's Code, the
  Children's Wellbeing & Schools Act). Re-checked **every run** on top of the sweep.
- **Standard** — settled statutes (data-protection baselines, consumer law).
  Covered by the baseline sweep.
- **Frozen** — rows whose topic neimo. has no coverage for (e.g. IP / copyright /
  trademark, which neimo. excludes by design). Mark `UNVERIFIED` once and don't
  re-poll weekly.

Staleness (`last_updated` older than the threshold, default 6 months) flags
candidates but does NOT scope the sweep. On artefacts where nearly every row
shares one old date, staleness is binary and useless for tiering — the required
sweep is what does the work.

### 3. Query neimo. — the required protocol

Section names, query shapes, and tool behaviours are **not obvious** and several
are traps. Follow this exactly.

**3a. Discover the real section keys first.**
Call `discover_sections(market)` once per in-scope market. Use **only** the
section keys it returns as the `domain` argument to `lookup_regulation`. Do not
guess. (Common GB section keys, for reference, are: `age-threshold`,
`age-assurance`, `parental-consent`, `settings`, `monetization-model-s`,
`penalties-and-enforcement`, `upcoming-changes`, `data-subject-rights`,
`processing-requirements`, `trust-and-safety` — but always confirm against
`discover_sections`, and note there is **no** `data-protection` section.)

**3b. Run the required baseline sweep per in-scope market.** This is the floor,
not a menu:
- `lookup_legal_horizons(jurisdiction=...)` with **jurisdiction only** — the
  highest-signal call. Anything dated AFTER a row's `last_updated` is a candidate
  change.
- `lookup_regulation(market, domain)` for **every** section key returned by
  `discover_sections` — not a hand-picked subset. This is what catches the
  findings that single runs otherwise miss (e.g. default-setting thresholds in
  `settings`, penalty ceilings in `penalties-and-enforcement`, the DUAA /
  pending-bill items in `upcoming-changes`).
  - **Sweep-completeness rule.** A dedicated `lookup_regulation` call per section
    is the default. A section is considered swept WITHOUT a dedicated call only if
    a `search_kb_semantic` pass in step 3b returned rows from it AND the artefact
    has no control mapping to that section's topic. The high-signal sections must
    ALWAYS get a dedicated call: `age-threshold`, `age-assurance`, `parental-consent`,
    `settings`, `monetization-model-s`, `penalties-and-enforcement`, `upcoming-changes`,
    `trust-and-safety`, `processing-requirements`, `data-subject-rights`. Thin sections
    (e.g. `quick-reference-faq`, `game-notice-s`, `record-keeping-and-audit`,
    `most-common-compliance-errors`, `changes-to-eula-and-privacy-policy`,
    `special-privacy-policy-for-kids-teens`) may be discharged by semantic coverage.
- `search_kb_semantic(query, market)` for each distinct artefact theme
  (age assurance, content moderation, consent, monetization, enforcement, data
  rights), to surface anything the structured sections didn't.

**3c. Tool-behaviour traps — memorise these:**
- `lookup_legal_horizons(query=...)` is a **strict keyword AND-filter** and
  frequently returns **0 even for heavily-covered topics**, or fans out across
  jurisdictions. **Never conclude "no movement" from an empty `query` result.**
  Always run jurisdiction-only first; treat `query` as an optional narrowing
  pass, never as the primary signal. (This trap is the main cause of missed
  Online-Safety-Act findings.)
- `search_kb_semantic` is the **primary** free-text tool. `lookup_online_safety_resources`
  matches **section/row names, not free text** — a natural-language `topic`
  string often returns empty. Reach for `search_kb_semantic` first; use
  `lookup_online_safety_resources` only with a short section/row keyword.
- Some sections return **very large** responses (e.g. GB `settings` ~100k chars)
  that get truncated and spill to a temp file. Two things bite here: (a) **the spill
  file is usually written to a host-side path the shell cannot reach** — do not
  assume `grep` in the shell will find it; and (b) **the spill file is itself often
  capped** (e.g. 50 of ~91 rows, `truncated: true`), so reading it does NOT recover
  the whole section. Recover in this order, and expect to need BOTH steps: (1) read
  the spill file with the host file tool if its path is shown — this gets the first
  tranche of rows; (2) **then** re-query the section's specific feature names with
  `search_kb_semantic(query="<feature> default setting", market=...)` (e.g. "Voice
  Chat", "Public Profile", "Targeted Advertising", "Geolocation", "Friend Requests",
  "Personalized Recommendations") to recover the rows beyond the cap. Step 2 is a
  reliable completion step, not merely a fallback — on a capped section you will
  usually need it. Never skip the section because the spill file was unreachable or
  partial.

Use ISO 2-letter codes for `market` ("GB"/"UK", "BR", "US"); the server
normalises common names. Legal Horizons covers a fixed jurisdiction list — if a
real market isn't in `availableJurisdictions`, fall back to `lookup_regulation` +
web confirmation and mark coverage limited.

### 4. Classify every finding

| Class | Meaning | Severity default |
|---|---|---|
| `NEW` | A requirement/instrument neimo. shows that the artefact lacks | High if enforcement-backed or with a hard deadline; else Medium |
| `AMENDED` | A threshold / deadline / scope the artefact states differently from neimo., OR a row that lacks an instrument neimo. surfaces AND predates the movement | High |
| `STALE` | Row older than threshold AND neimo. shows movement in that area since (use only when there is no instrument/threshold delta to report) | Medium |
| `CONFIRMED` | neimo. agrees; only the `last_updated` date is old | Low (refresh date) |
| `UNVERIFIED` | neimo. has no data for this market/topic | Info (cannot conclude) |
| `DEPRECATED` | Instrument repealed/superseded per neimo. | High |

**Two recurring cases — fixed conventions (do not improvise):**
- **Both NEW and STALE** (the row lacks an instrument neimo. surfaces *and*
  predates the movement): class it **AMENDED**, add a one-line STALE note. Emit
  **one** finding, not two.
- **Current value confirmed, future change pending** (e.g. consent age is 13
  today but a Bill/Act creates a path to 16): emit **one CONFIRMED row** for the
  current value **plus one NEW(horizon) row** for the pending change. This
  pairing is the standard, not optional.

Severity also rises when a development names a hard date (compliance deadline),
cites active enforcement (fines, formal proceedings), or explicitly names the
client's vertical in a "what it means for you" section.

### 5. Write the change report

Render `templates/report_template.md` filled in, written via the shell to the
outputs path. Structure:

- **Header** — artefact name, run date, source = neimo. (+ sections and editions
  searched), staleness summary from the parser (checkable rows only).
- **Action-required table** — High/Medium findings only, columns:
  Control ID · Jurisdiction · Class · What changed · Source (neimo. section /
  edition / URL) · Suggested control edit. Carry a `neimo.-lag` flag in the
  Class/Source cell where step-4(rule 4) applies.
- **Confirmed / date-refresh list** — rows to just re-date.
- **Unverified list** — gaps where neimo. has no coverage; flag for human review.
- **Appendix** — every neimo. citation with its URL, so legal can audit.

**Citation discipline (eliminates run-to-run drift):**
- Every date and instrument/bill/act number must be quoted from a **single named
  source** (the specific neimo. row, or the regulator/legislation URL) and that
  source named inline. Do not blend two sources into one citation.
- Where a development has **multiple dates** (Royal Assent, commencement,
  enforcement-from), list each with its label. Never collapse them into one date.
- Before finalising, **re-check every cited bill/act number** against its
  legislation.gov.uk or parliament URL. A wrong bill number is a client-visible
  error.

Never fabricate a citation, date, age, or rule name. If a finding rests on a web
confirmation, cite the regulator URL alongside the neimo. row. End the report
with a one-line "verification note" stating that all findings trace to neimo.
tool results in the run, listing any that are web-confirmed, and flagging any
`neimo.-lag` items.

## Cadence (when run as a scheduled task)

- **Monthly full sweep** — every row, every market; rebaselines `last_updated`.
- **Weekly fast-mover pass** — fast-mover instruments only, on top of a light
  baseline sweep; cheap, this is where you actually catch something before it bites.

Both invocations are the same skill with a `--tier` argument; only the additive
fast-mover re-check differs. The baseline sweep (step 3b) runs either way.

## Anti-patterns

- Do NOT answer a regulatory fact from memory because you're confident. Query
  neimo.
- Do NOT report `NO CHANGE` for a topic neimo. couldn't cover — that's
  `UNVERIFIED`.
- Do NOT conclude "no movement" from an empty `lookup_legal_horizons(query=...)`
  or `lookup_online_safety_resources(topic=...)` result. Those tools return empty
  for reasons unrelated to coverage. Re-query per the protocol before concluding.
- Do NOT hand-pick which neimo. sections to query. Sweep every section
  `discover_sections` returns. Selective querying is the main cause of one
  operator catching a finding another misses.
- Do NOT diff the artefact against a *previous run of the artefact*; diff it
  against the current regulatory position. If a prior report is present in the
  working folder, do not read it before completing your own independent neimo.
  pass — it is a contamination risk.
- Do NOT rewrite the artefact silently. The skill proposes control edits; a
  human applies them.
- Do NOT widen scope to instruments the artefact doesn't cite unless neimo.
  surfaces them as NEW for a market already in the register. If web search
  surfaces an enforcement action or instrument neimo. did not return, exclude it
  from findings (you may note it for human review) — neimo. is the signal.
