# neimo. lookups for the PP Tunas risk assessment

**Scope of this file (read first).** The *scoring instrument itself* — the 58
parameters, their weights, the YES/NO polarity, and the >50% determination rule — is
**fixed law embedded in `kepmen142_parameters.json`**. Do **not** look those up in
neimo. or paraphrase them. neimo.'s job here is narrower and still essential: ground
the **downstream obligations** a HIGH/LOW profile triggers (age assurance, parental
consent, monetization floors, notices, trust & safety, penalties) and supply the
**verbatim citations** — for the *supplementary* Obligations and Sources tabs, not the
worksheet. Also use it to check whether the regulation has been **amended** since the
embedded catalog version (`lookup_recent_updates` / `lookup_regulation_events`, ID).

This file is the *method* for that grounding. The values neimo. returns are the
*answers*. Never substitute the illustrative numbers below for a live lookup — they
exist only so you know which question each lookup answers.

## The neimo. MCP

neimo. is k-ID's children's-digital-safety regulatory knowledge base (the brand
is always written lowercase with a trailing period: "neimo."). It covers 200+
markets with structured, k-ID-reviewed data. Every figure carries a citation and
a verification status. Use ISO 2-letter codes — Indonesia is `ID`.

The tools you'll use (names are prefixed by the server id in this environment —
search for them by the bare name via ToolSearch if they aren't already loaded):

- `discover_sections(market)` — list every section available for ID. Run first if
  you're unsure a section exists; a wrong section name returns empty.
- `market_profile(market)` — a broad snapshot across all sections (capped ~50
  rows). Good for orientation; follow up with targeted `lookup_regulation` calls.
- `lookup_regulation(market, domain, field?)` — the workhorse. `domain` is a
  section key (see below). Returns rows with `value`, `reference`, and
  `verificationStatus`.
- `search_kb_semantic(query, market?)` / `search_primary_sources(query, countryCodes?)`
  — for enforcement actions or the actual statutory wording when you need it.
- `lookup_recent_updates` / `lookup_regulation_events` — to check whether anything
  has changed recently (useful given how new PP Tunas is).
- `submit_feedback` — only when the user expresses doubt/praise/missing-coverage;
  ask them first, verbatim: "Would you like to share that feedback with the
  neimo. team?"

## Required lookups for market = ID, in order

### 1. The seven mandatory risk factors + DPIA (the spine)
`lookup_regulation(market="ID", domain="processing-requirements-for-kids-teens-personal-data")`

This returns the DPIA obligation and the mandatory self-assessment risk factors.
*Illustrative* (verify live): children's data is "specific personal data"
requiring a DPIA; separately, providers must self-assess on factors (a) unknown-
individual contact, (b) inappropriate-content exposure, (c) consumer exploitation,
(d) data-security risk, (e) addiction potential, (f) psychological-health impact,
(g) physiological impact; HIGH-RISK services cannot be provided to under-16s.
Also returns the default-highest-privacy-settings requirement.

### 2. Age thresholds + age-assurance trigger
`lookup_regulation(market="ID", domain="age-threshold")`

Digital consent age; the alternative/minimum ages tied to the high/low-risk
determination; and "Is there a requirement to deploy Age Assurance?" — historically
yes, level commensurate with risk, data limited to the age-assurance purpose.
Cites PP 17/2025 Art. 9, 22 and Permen 9/2026.

### 3. Parental consent (VPC)
`lookup_regulation(market="ID", domain="parental-consent")`

Whether VPC is required; the approved method(s); recommended methods (e.g. credit
card, ID verification, facial age estimation); high-risk methods to avoid (e.g.
self-declaration); the consent window/opt-in mechanics; the direct-from-child
exception above a certain age; and what must be notified to a parent.

### 4. Dark patterns / covert techniques
`lookup_regulation(market="ID", domain="gaming-restrictions")`

The prohibition on covert methods that push children to over-share data, weaken
privacy, or act against their physical/mental health/welfare. Cites PP 17/2025
Art. 17. (Also tells you whether curfews / spend limits are expressly required —
historically not.)

### 5. Trust & safety — content/conduct factors
`lookup_regulation(market="ID", domain="trust-and-safety")`

Many rows here (CSAM, cyberbullying, fraud, graphic violence, hate speech,
suicide/self-harm, extremism, NCII, adult content) are explicitly described as
high-risk factors the platform must self-assess and report mitigations for.
Surface these under risk factors (a), (b), (f). Also returns content-removal
turnaround, the Bahasa-Indonesia moderation duty, and the local-contact-person
requirement.

### 6. Commercial / monetisation surface
`lookup_regulation(market="ID", domain="monetization-model-s")` and
`lookup_regulation(market="ID", domain="settings")`

Age floors for microtransactions, loot boxes (and the hard gambling prohibition),
player trading, subscriptions, ads to minors; and the per-feature minimum/threshold
ages and age-assurance flags for chat (text/voice/video), forums, profiling,
custom username/avatar, etc. Feeds factor (c) and the obligations sheet.

### 7. Notices, record-keeping, penalties
`lookup_regulation(market="ID", domain="game-notice-s")`
`lookup_regulation(market="ID", domain="record-keeping-and-audit")`
`lookup_regulation(market="ID", domain="penalties-and-enforcement")`

The five mandatory age categories and what must be on a notice; the regulator's
audit/information-request rights and the mandatory-investigation-before-sanction
posture; the criminal + corporate fine exposure (UU PDP Arts. 67–70; PP 17/2025
Art. 40) and the blocking-enforcement precedent.

## Recording citations

For every value you carry into the register, copy neimo.'s `reference` string
verbatim into the Sources sheet — regulation name, article, and URL. The register
is only defensible if each row traces to a citation the developer can show the
regulator. If a row's `reference` is null, note "no citation in neimo. — confirm
with counsel" rather than leaving it blank or inventing one.
