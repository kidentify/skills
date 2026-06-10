---
name: pp-tunas-risk-assessment
description: >-
  Produces Indonesia's PP Tunas child-safety risk-level self-assessment as the
  regulator specifies it (Kepmen 142/2026, under PP 17/2025 and Permen 9/2026).
  Screens whether the product is in scope (Appendix I), scores the seven statutory
  risk aspects across the 58 fixed, coded Assessment Parameters - each with its
  legally-fixed weight and YES/NO status - and computes the deterministic per-aspect
  (>50%) and overall HIGH-RISK / LOW-RISK profile. Records the multidisciplinary
  Assessor team and the per-parameter evidence the law requires, builds the fileable
  worksheet, and adds a clearly-fenced supplementary k-ID layer mapping each gap to
  the control that fixes it. Use whenever someone wants to assess or scope PP Tunas /
  PP 17/2025 / Permen 9/2026 / Indonesian child-online-protection compliance, asks
  'are we high or low risk under PP Tunas', or wants the Indonesia kids self-assessment
  worksheet, risk scoring, or gating matrix - including a product reachable by minors
  in Indonesia when they don't say 'PP Tunas'.
license: Apache-2.0
metadata:
  version: "1.0.0"
  vendor: k-ID
---

# PP Tunas Risk Assessment (Indonesia) — the official Kepmen 142 worksheet

## What this skill is for

PP Tunas — Government Regulation No. 17 of 2025 (PP No. 17/2025) "on Governance of
Electronic System Implementation in Child Protection", with its implementing
Ministerial Regulation No. 9 of 2026 (Permen Komdigi No. 9/2026) — requires every
Electronic System Operator (ESO / *Penyelenggara Sistem Elektronik*, PSE) whose
product, service, or feature (PLF) can be reached by children to conduct a **risk-
level self-assessment** and report it to Komdigi.

That self-assessment is **not** a free-form checklist. The Ministerial Decree
**Kepmen Komdigi No. 142 of 2026** (Appendix II) defines the instrument down to the
cell: seven aspects, **58 coded Assessment Parameters**, each with a **legally-fixed
risk weight**, a binary **YES/FOUND or NO/NOT FOUND** status, and a **deterministic
aggregation rule**. The output is a HIGH-RISK or LOW-RISK profile. Kepmen 142 also
fixes the upstream scoping test (Appendix I), the Assessor composition (Ch. II.B),
the evidence and documentation duties (Ch. II.C–F), and the verification lifecycle
(Appendix III).

**The single most important design fact: the parameters and weights are law, not
judgement.** They are embedded, version-pinned, in `references/kepmen142_parameters.json`
and rendered by `scripts/build_self_assessment.py`. The assessor's only job is to
record, per parameter, whether the technical configuration is present (with
evidence). The script does all scoring and the determination. Do **not** invent
parameters, weights, or scores, and do not turn the binary YES/NO into a qualitative
rating — the instrument is exactly what the catalog defines, and it yields a risk
profile, not an age (see the note on age below).

## A note on age

This worksheet produces a **risk profile** (HIGH-RISK / LOW-RISK) — it does not by
itself set an age limit. Age-related obligations (those attaching to a high-risk
profile, parental-consent thresholds, the five age categories) live in PP 17/2025 /
Permen 9/2026; the skill surfaces them — grounded live in neimo. — in the
*supplementary obligations* tab, kept separate from the risk score.

## What is fixed law vs. what to ground live in neimo.

- **Fixed law (embedded; do not look up, do not paraphrase):** the 58 parameters,
  their codes, weights, the YES/NO scoring polarity, the >50% aspect rule, the
  "any one aspect → HIGH-RISK profile" rule, the Appendix I scoping indicators, the
  Assessor composition, and the verification timelines. These come straight from
  Kepmen 142/2026 and live in `references/kepmen142_parameters.json` and
  `references/kepmen142_process.md`.
- **Ground live in neimo. (never from memory):** the *downstream obligations* a
  HIGH/LOW profile triggers and their current values — age-assurance trigger,
  verifiable parental consent method, the five age categories, monetization age
  floors, trust-and-safety / takedown SLAs, penalties — and **every citation**.
  These are young and moving; pull them fresh and copy the citation verbatim. See
  `references/neimo-lookups.md`. If neimo. returns empty, say so plainly rather than
  inventing a value.

Before filing, also sanity-check the embedded catalog against the current gazette:
the regulation is new and the English text here is an unofficial translation. Use
`lookup_recent_updates` / `lookup_regulation_events` (market `ID`) to check nothing
has been amended since `version: kepmen142-2026-v1`.

## Workflow

**intake → Appendix I scope screening → assemble the multidisciplinary Assessor →
record each of the 58 parameters (status + evidence) → let the script score &
determine → ground downstream obligations live in neimo. → build supplementary
remediation/gating → write the worksheet → explain the result + filing lifecycle.**
Create a task list so the developer sees progress.

### 1. Intake — understand the PLF, feature by feature

You need enough detail to answer all 58 parameters. Ask in a few grouped, friendly
passes (and infer from what's already said): reach & current gating; social
features itemised (DMs, public/private chat, voice, video, forums, recommendations,
account/content discovery, external indexing, message unsend/edit); content &
moderation (UGC, harmful-content exposure, block/report, filtering); monetization
(IAP, currency, loot boxes, subscriptions/auto-renew, payment without parent
verification, ads/offers to children, dark patterns); data & privacy (child-editable
privacy settings, default public visibility, data collection without parental
supervision, DPIA, privacy notice, DPO, security measures); engagement/addiction
(immersive/full-screen design, infinite scroll/autoplay, social metrics, push
notifications, chance/lottery elements, rewards, leaderboards, disappearing content,
difficulty, checkpoints, clear end goals); psychological (comment exposure, scary
content, no time limits, activity-notifications, beauty/voice filters, presence
status); physiological (continuous access, sleep-hour notifications, dark/night
mode, safe volume defaults, autoplay on main feed, repetitive single actions,
dangerous-challenge enablement).

### 2. Appendix I — screen whether the PLF is even in scope

Kepmen 142 Appendix I gives five indicators; **fulfilling any one** puts the PLF in
scope for the assessment: (A) terms/policies indicate it's for children; (B) strong
evidence of a significant number of child users (non-incidental, routine, **≥25
child users**); (C) advertising directed at children; (D) child-attracting design
(bright colours/cartoons/avatars; impulsive exploratory interaction; gamification);
(E) substantially similar to a PLF proven to be used by children. Record each as
Yes/No with a note in the `scope_screening` input; the script renders the screening
sheet and the in-scope verdict. (Indicator results are themselves documented and
submitted to Komdigi within **3 working days** of assessment.)

### 3. Assemble the multidisciplinary Assessor (Ch. II.B) — required, not optional

The law requires the Assessor to be a **multidisciplinary team**, precisely because
the risk surface spans content, contact, consumer, data, addiction, psychological,
and physiological aspects — it must not be assessed from a single (e.g. engineering)
lens. The required functions are:

1. **Product development team** — confirms features / technical configurations.
2. **Policy / internal regulatory team** — aligns to PP TUNAS, Permen 9, Kepmen 142.
3. **User protection / Trust & Safety team** — contact, content, conduct, psych risk.
4. **System security & data protection team** — the data-security aspect, DPIA, DPO.
5. **Experts or consultants (if necessary)**.

If the PSE appoints an **external** party, that Assessor must hold, at minimum,
expertise in **child psychology, child physiology, information technology, system
security and personal-data protection, legal, and digital marketing**. Capture the
team in `assessor_team`; the script renders an Assessor & sign-off sheet keyed to
these functions, with the minimum-expertise note. Actively assess each aspect
through the relevant lens above rather than answering everything from a product/eng
default — e.g. aspects (e) addiction, (f) psychological, (g) physiological need the
T&S / child-development perspective, and aspect (d) needs the security/DPO lens.

Use `references/assessor_personas.md`: a persona per required function — the lens it
owns, the aspects and parameters it scores, the questions it asks, the evidence it
brings, and its sign-off. Adopt each persona when scoring its aspects, and record the
named reviewers in `assessor_team` so they appear on the sign-off sheet. Where a
persona's expertise isn't held in-house, the PSE should appoint an external party (per
the minimum-expertise list).

### 4. Record each of the 58 parameters — status + evidence

For every parameter (use the codes in the catalog), set `status` to **FOUND** or
**NOT_FOUND** based on the real technical configuration in the PLF, and attach an
**evidence** reference. Ch. II.C requires valid supporting evidence per parameter —
documents/specs, **Model Cards** (for AI/recommender features), **UX survey
reports**, or other — and where a parameter is **NOT_FOUND because of a deliberate
mitigation**, an explanation of the specific technical configuration goes in the
`justification` field (the law's "Specific Technical Configuration" column). Missing
evidence lets Komdigi adjust the result at verification, so flag thin evidence.

Mind the scoring polarity (the script handles it; you just report reality): for most
parameters presence is the risk (weight in the YES column), but for **protective**
parameters — block/report (KN06, GP09), security measures/DPIA/privacy notice/DPO
(DP03/04/06/07), checkpoints & clear end goals (AD10/11), safe-volume/night-mode
defaults (several GF) — the weight applies when the control is **absent**. Two
physiological parameters (GF01, GF02) carry a translation-polarity flag; resolve
their YES/NO direction against the Bahasa-Indonesia gazette text before filing.

### 5. Let the script score and determine — don't hand-compute

Run `scripts/build_self_assessment.py`. It computes, per Chapter IV:
Parameter Risk Score = weight × status; Aspect Risk Score = Σ within the aspect;
an aspect is **HIGH RISK when its score > 50%**; the PLF profile is **HIGH-RISK if
at least one of the seven aspects exceeds 50%**. It also counts unanswered
parameters and warns (Komdigi rejects incomplete worksheets). Never override or
"adjust" the computed score — the determination is arithmetic, and the **Director
General makes the final, binding determination** after verification.

### 6. Ground the downstream obligations live in neimo. (supplementary)

A profile is the start, not the end. Pull the obligations the profile triggers —
age assurance, verifiable parental consent, default-highest privacy, the dark-
pattern prohibition, monetization age floors + gambling prohibition, the five age
categories & rating notices, Bahasa-Indonesia moderation + takedown SLAs + local
contact person, data-subject rights, record-keeping, penalties — **live from neimo.**
with verbatim citations (`references/neimo-lookups.md`). These populate the
*Obligations (supp.)* tab.

### 7. Map gaps to k-ID mechanisms — make it buildable (supplementary)

Read `references/kid-enforcement-map.md`. For each gap, name the k-ID capability
that closes it — Age Gate (`/age-gate/check`), AgeKit+ age assurance, Verifiable
Parental Consent, Session Permissions, `verifiedAgeThreshold` (`/session/upgrade`),
Compliance Studio + Family Connect — and phrase remediation as *feature → required
age/threshold → mechanism → build step*. This fills the *Remediation & gating (supp.)*
tab. Be honest where the fix is product design, an operational process, or a
deliverable rather than a k-ID API call.

### 8. Produce the worksheet

Build with `scripts/build_self_assessment.py`, passing the catalog and your
`answers` JSON (shape in the script header / `--help`). It writes:

- **Determination** — identity block, per-aspect scores with >50% flags, the
  computed HIGH/LOW profile, the incomplete-parameter warning, and the proviso.
- **Scope screening (App. I)** — the five indicators + in-scope verdict.
- **One sheet per aspect (KK / KN / EK / DP / AD / GP / GF)** — the worksheet
  proper: code, indicator, technical configuration, parameter, YES/NO ticks, fixed
  weight, the "Specific Technical Configuration" justification, the **evidence**
  reference, the per-parameter calc, and the aspect subtotal.
- **Assessor & sign-off** — the required functions, lens, names, sign-off, and the
  minimum-expertise note.
- **Remediation & gating (supp.)**, **Obligations (supp.)**, **Sources (supp.)** —
  k-ID value-add, visually fenced and labelled **NOT part of the filing**.

Save to the outputs folder, present with `present_files`, and close with the
filing lifecycle (next section) plus the top two or three things to build first by
k-ID mechanism — not a re-listing of the worksheet.

### 9. Explain the filing & verification lifecycle (Appendix III)

So the developer knows what happens after they file: the report is the worksheet
covering all seven aspects, submitted with evidence to the Director General through
Komdigi's electronic system; designate a **contact official**; legacy PLF in service
before Permen 9/2026 must self-assess within the stipulated timeframe; **false or
misleading** statements can trigger sanctions and referral to law enforcement.
On the regulator side: acknowledgment of receipt → verification within **14 days** →
possible clarification/revision requests (ESO responds within **7 days**) → outcome
of complete / not-complete; if rejected, **resubmit within 3 days, max 2 times** →
the Director General **determines the risk profile**, notifies within **3 days**, and
**publishes** it on the Ministry's website. Keep the worksheet, evidence, and DPIA
on file and **update** the worksheet whenever the assessment changes (Ch. II.E).
See `references/kepmen142_process.md` for the full lifecycle.

## Mandatory proviso — on every assessment, every time

Every assessment this skill produces is AI-assisted and must say so. The build
script renders the proviso on the Determination sheet automatically; include it in
the chat response too:

> This worksheet was prepared with AI assistance using the parameter catalog fixed
> in Kepmen 142/2026 and findings supplied by the assessor. The seven-aspect YES/NO
> determinations and the supporting evidence are the assessor's responsibility. It
> is a structured aid, **not legal advice**, and must be reviewed by a qualified,
> multidisciplinary assessor and/or counsel before it is filed. The Director General
> (Komdigi) makes the final, binding HIGH/LOW-risk determination after verification.

Children's-safety compliance carries criminal and corporate liability in Indonesia,
the rules are new and still settling, and false statements in a filing are
explicitly sanctionable. State the proviso plainly; don't let a run end without it.

## Tone and stance

Be the competent compliance engineer next to the developer. The worksheet is the
law's instrument — render it faithfully and let the arithmetic speak. Where you add
value (obligations, gating, k-ID mechanisms), say clearly that it's supplementary
and ground it live in neimo. Be honest about genuine legal judgement calls (the GF
polarity, in-scope edge cases, evidence sufficiency) and flag them for counsel.
