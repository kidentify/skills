---
name: pp-tunas-risk-assessment
description: >-
  Comprehensive, buildable children's-safety risk assessment for an app, game, or
  platform under Indonesia's PP Tunas (Government Regulation No. 17/2025 + Permen
  9/2026). Pulls every neimo. requirement for Indonesia live (never from memory),
  scores the seven statutory risk factors, derives the HIGH-RISK / LOW-RISK
  determination (HIGH-RISK can't serve under-16s), builds a feature × age gating
  matrix, and maps each gap to the k-ID capability that enforces it (age gate,
  AgeKit+, VPC, verifiedAgeThreshold, session permissions) — producing an Excel risk
  register engineering can act on and file. Use whenever someone wants to assess,
  audit, or scope PP Tunas / PP 17/2025 / Permen 9/2026 / Indonesian
  child-online-protection compliance, asks "are we high or low risk under PP Tunas",
  or wants an Indonesia kids risk assessment, DPIA scoping, or gating matrix.
  Use EVEN IF they don't say "PP Tunas" — if they describe an app reachable by minors
  in Indonesia and want a risk or what-to-build assessment, this is the skill.
license: Apache-2.0
metadata:
  version: "0.1.0"
  vendor: k-ID
---

# PP Tunas Risk Assessment (Indonesia) — comprehensive & buildable

## What this skill is for

PP Tunas — Government Regulation No. 17 of 2025 (PP No. 17/2025) "on Governance of
Electronic System Implementation in Child Protection", with its implementing
Ministerial Regulation No. 9 of 2026 (Permen Komdigi No. 9/2026) — makes every
Electronic System Organizer (ESO / *Penyelenggara Sistem Elektronik*, PSE) whose
product can be reached by children responsible for a lot more than a single
seven-factor checklist. There are two layers:

1. **The mandatory self-assessment** against seven statutory risk factors,
   submitted to Komdigi, yielding a **HIGH-RISK** or **LOW-RISK** determination.
   A HIGH-RISK service may not be provided to users under 16. This sets the
   minimum age the product can legally serve.

2. **A dense, feature-and-age-level obligation surface** that applies on top:
   per-feature age gates and threshold ages (text/voice/video chat, forums,
   profiling, custom username/avatar, links to third-party chat); monetization
   age floors (loot boxes, microtransactions, in-game currency, trading,
   subscriptions, ads to minors, the hard gambling prohibition); verifiable
   parental consent; age assurance commensurate with risk; a DPIA (children's
   data is "specific personal data" under UU PDP Art. 34); default-highest
   privacy; the dark-pattern / covert-technique prohibition; trust & safety
   duties (CSAM, cyberbullying, fraud, graphic violence, hate speech,
   suicide/self-harm, extremism, NCII, adult content, Bahasa-Indonesia
   moderation, takedown SLAs, local contact person); the five mandatory age
   categories and game-rating notice; data-subject rights; record-keeping &
   audit; and penalties.

This skill's job is to surface **all** of that — exhaustively, every neimo. row,
each as its own assessable requirement — and then to tell the developer exactly
**what to build, per feature, per age band, with the specific k-ID capability
that enforces it.** That last part is the point: the technology to solve this
exists, and a risk assessment that stops at "you're high risk" is half a
deliverable. We finish the job by handing engineering a concrete plan.

## The non-negotiable: ground every requirement in a live neimo. lookup

Indonesia's rules are young and moving (PP 17/2025 in 2025, Permen 9/2026 in
2026; thresholds can shift again). **Never state a threshold, age, citation,
deadline, or obligation from memory.** The numbers in this file and its
references are illustrative scaffolding — they tell you *which questions to ask*,
not *what the current answer is*. Pull the live values from neimo. every run.

`references/neimo-lookups.md` lists every section to read and the tool calls to
make. Be exhaustive: enumerate **all** sections via `discover_sections("ID")`
and read each one, because the obligation surface is spread across ~14 sections,
not just the risk-factor section. `references/kid-enforcement-map.md` maps each
obligation/feature to the k-ID capability that enforces it.

If a neimo. lookup returns empty, say so plainly ("neimo. has no data for this
topic yet — confirm with counsel") rather than inventing a value. If the user
expresses doubt or finds a gap, offer the neimo. feedback path verbatim.

## Workflow

**intake → exhaustive neimo. grounding → score the seven factors → derive the
determination → enumerate EVERY obligation as its own line → build the feature ×
age gating matrix → map each gap to a k-ID mechanism → write the register.**
Create a task list so the developer sees progress.

### 1. Intake — understand the product, feature by feature

You need enough detail to place every feature on the gating matrix. Ask in a
couple of grouped, friendly passes (and infer from what's already been said):

- **Reach & current gating.** Designed for children, all-ages, or adults-only?
  What ages actually use it? Any age gate today, and how (self-declaration?
  platform signal?)?
- **Social features, itemised.** Text chat (public / private / DMs), voice chat,
  video chat, forums, friend/stranger matchmaking, links out to third-party chat
  apps. List each one present — they each carry their own age threshold.
- **Identity & profile.** Custom username, custom avatar, public profiles, photo
  /video upload.
- **Content.** UGC? Exposure to violence, sexual/adult content, self-harm,
  gambling-like content? Any rating today?
- **Monetization, itemised.** In-app purchases, in-game currency, loot boxes,
  subscriptions, player trading/marketplace, in-game advertising, sponsored
  content. Who can complete a transaction?
- **Data & profiling.** What's collected? Profiling, behavioural ads, location
  tracking, activity monitoring? Default privacy posture?
- **Engagement mechanics.** Streaks, infinite scroll, autoplay, push loops,
  variable-reward systems (feeds factors e/f and the dark-pattern prohibition).
- **Indonesia operating posture.** Local contact person? Bahasa-Indonesia content
  guidelines? Moderation + takedown process and turnaround?

### 2. Ground in live neimo. data — exhaustively

Run `discover_sections("ID")`, then `lookup_regulation` (or `market_profile` for
breadth) across **every** section. For each requirement you'll assess, capture the
**current value** and the **citation verbatim** (regulation + article + URL). See
`references/neimo-lookups.md`. Do not skip sections because they seem minor — the
exhaustive obligation surface is the user's explicit expectation.

### 3. Score the seven mandatory risk factors

Factors (confirm exact current wording from the neimo. `processing-requirements…`
lookup): (a) contact with unknown individuals; (b) exposure to pornographic /
violent / life-endangering / child-inappropriate content; (c) exploitation of
children as consumers; (d) risks to children's data security; (e) potential to
cause addiction; (f) psychological-health impact; (g) physiological impact.

For each: presence, severity, likelihood, existing mitigation, residual risk,
required mitigation — each tied to the actual feature, not a platitude. Cross-
reference the `trust-and-safety` lookup: CSAM, cyberbullying, fraud, graphic
violence, self-harm, extremism, NCII and adult content are each named high-risk
factors needing documented mitigation reported to the competent authority —
surface them under (a), (b), (f).

### 4. Derive the HIGH / LOW-RISK determination

Apply neimo.'s rule (historically: a high-enough factor makes the service
HIGH-RISK → no under-16s; a LOW-RISK service not designated for children has had
a floor around 13). State the determination, the **minimum serviceable age**, and
the driving factor(s). On a close call, recommend treating it as high-risk
pending Komdigi — the asymmetry of serving under-16s a high-risk service is severe.

### 5. Enumerate EVERY obligation as its own line

This is where the previous version was too thin. Don't collapse the obligation
surface into a handful of rows. Produce a line for **each** discrete requirement
neimo. returns, across all sections, including at least:

- Age assurance (level commensurate with risk; data limited to age-assurance
  purpose only).
- Verifiable Parental Consent (approved method; high-risk methods to avoid such
  as self-declaration; the consent window/opt-in; direct-from-child exception
  above the threshold age).
- DPIA (distinct from the seven-factor self-assessment).
- Default-highest privacy settings for children.
- Dark-pattern / covert-technique prohibition (three limbs: over-collection,
  privacy-weakening, wellbeing-harming nudges).
- Per-feature gating for **each** social/identity feature (see the matrix, step 6).
- Monetization age floors for **each** monetization mechanic, plus the gambling
  prohibition and the parent-must-conclude-transaction rule for under-18 spend.
- Profiling / behavioural-ads / direct-marketing restrictions by age.
- Notices: the five mandatory age categories (3–5, 6–9, 10–12, 13–15, 16–18),
  minimum-age limit, game rating, fee/payment info, location-tracking /
  activity-monitoring disclosure to parents.
- Trust & safety: Bahasa-Indonesia usage guidelines, prohibited-content handling,
  takedown turnaround (24h / 4h for urgent), local contact person, reporting
  named high-risk conduct to the competent authority.
- Data-subject rights (access, deletion, correction, portability, restriction,
  objection).
- Record-keeping & audit (regulator's information-request right; mandatory
  investigation before sanction).
- Penalties / enforcement exposure (criminal + corporate fines; blocking
  precedent) — for context, so stakes are clear.

Each line gets: applies?, current status, gap, **action**, the **k-ID mechanism**
that delivers it (step 7), owner, citation.

### 6. Build the feature × age-band gating matrix

For every feature the product has (and every relevant feature neimo. defines —
text/voice/video chat, forums, links to 3rd-party chat, custom username, custom
avatar, profiling, microtransactions, loot boxes, trading, subscriptions, ads,
direct marketing), produce a matrix row with: **minimum age**, **threshold age**,
**age-assurance required?**, the **k-ID enforcement mechanism**, current status,
and the gap. This is the engineering blueprint — it tells the developer exactly
which gate sits in front of which feature and at what age, and how k-ID enforces
it. Pull the per-feature ages live from the neimo. `settings` and
`monetization-model-s` sections.

### 7. Map each gap to a k-ID mechanism — make it buildable

Read `references/kid-enforcement-map.md`. For every gap and matrix row, name the
specific k-ID capability that closes it, so "what to do next" is concrete:

- **Initial age gate** (`/age-gate/check`) — collect claimed age, detect
  jurisdiction (ID), open a session. The front door for everything.
- **AgeKit+ age assurance** — prove age to a real level of confidence where
  self-declaration won't do; "commensurate with risk" per Art. 22.
- **Verifiable Parental Consent** via the consent/challenge flow — for users under
  the threshold; QR / OTP / email; opt-in; parent concludes under-18 transactions.
- **Session permissions** (`session.permissions`) — gate each feature so chat,
  profiling, marketing, etc. unlock only when allowed for that user's age/consent.
- **`verifiedAgeThreshold` verification** (`/session/upgrade`) — for features with
  a hard threshold age (e.g. 18) that require proven, not claimed, age.
- **Compliance Studio config + Family Connect** — where the org-level baseline,
  per-jurisdiction overrides, and the parent-facing consent experience live.

Express remediation as: *feature → required age/threshold → k-ID mechanism →
build step.* E.g. "Public voice chat → min 16, assurance required → gate behind a
`session.permissions` control unlocked only after AgeKit+ confirms 16+; under-16
sessions see it locked."

### 8. Produce the Excel risk register

Build with `scripts/build_risk_register.py`. It writes a five-sheet `.xlsx`:

- **Summary** — product, date, determination banner, minimum serviceable age,
  driving factors, top next steps.
- **Risk Factors** — one row per statutory factor (a–g), severity-coloured.
- **Feature Gating Matrix** — one row per feature: min age / threshold age /
  assurance required / k-ID mechanism / status / gap. The engineering blueprint.
- **Obligations** — one row per discrete requirement (be exhaustive — expect
  20–35+ rows, not 8): requirement, applies?, status, gap, action, k-ID
  mechanism, owner, citation.
- **Sources** — every neimo. citation, verbatim, with URL.

Pass scored data as JSON (shape documented in the script header / `--help`). Don't
hand-build the workbook — the script keeps every run defensible and identical in
structure.

Save to the outputs folder, present with `present_files`, and close with a short
plain-language read of the determination plus the top two or three things to build
first (by k-ID mechanism) — not a re-listing of the register.

## Mandatory proviso — on every assessment, every time

Every assessment this skill produces is AI-generated and must say so. Include the
following proviso in **both** the chat response **and** the workbook (the Summary
sheet's note line — the build script renders it automatically, but confirm it's
present):

> This risk assessment was generated by AI using neimo. regulatory data. It is a
> structured engineering aid, **not legal advice**, and must be reviewed by a
> qualified risk assessor and/or a qualified attorney before it is relied upon or
> filed. The regulator (Komdigi) makes the final HIGH/LOW-risk determination.

This isn't boilerplate to bury — children's-safety compliance carries criminal and
corporate liability in Indonesia, the rules are new and still settling, and the
seven-factor scoring involves genuine legal judgment. A developer acting on an
un-reviewed AI assessment is exactly the failure mode to guard against. State it
plainly and don't let a run end without it.

## Tone and stance

Be the competent compliance engineer next to the developer, not a billing lawyer.
Explain *why* each requirement matters in product terms, and always close the loop
to *what to build*. Be honest when something is a genuine legal judgment call and
flag it for counsel — and always carry the AI-generated review proviso above.
