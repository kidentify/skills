# Kepmen 142/2026 — process, evidence, documentation & verification

This file captures the parts of the regulation that surround the scoring instrument:
who assesses, what evidence is required, how results are documented and reported, and
how Komdigi verifies them. All of this is **fixed law** (Kepmen Komdigi No. 142/2026,
Appendices I–III), not something to look up in neimo. The English here is an unofficial
translation; the Bahasa-Indonesia State Gazette text is authoritative.

## In-scope screening (Appendix I)

A PLF must do the risk-level self-assessment if it is "used or accessed by children."
Five indicators; **fulfilling any one is sufficient** to be in scope:

- **A — Terms/policies.** Internal terms, conditions, rules, or policies indicate the
  PLF is intended to be used/accessed by children. (Decision tree: if policies don't
  govern children, or prohibit child use, that affects fulfilment.)
- **B — User composition.** Strong evidence that the routine user base includes a
  significant number of children. "Significant" = non-incidental proportion with a
  pattern of routine access, **at least 25 child users**. Age-data/age-assurance/age-
  estimation mechanisms and public reports of under-age access feed this test.
- **C — Advertising.** The PLF is advertised in a manner directed at children.
- **D — Design.** Design elements attract children: bright colours/high-contrast/
  pastel; cartoon/cute characters/playful avatars; excessive animation (bounce,
  sparkle, confetti); large toy-like icons (candy/stars/rainbows); playful rounded
  typography; impulsive exploratory interaction (instant-feedback taps, minimal text,
  infinite scroll/auto-play, low literacy needed); gamification (points/levels/badges/
  streaks/progress meters, reward chests, daily rewards, loot/mystery-box visuals).
- **E — Similarity.** Substantially similar or identical to a PLF proven to be used/
  accessed by children.

Indicator results are **documented and submitted to the Ministry within 3 working
days** of the assessment, with supporting documents/evidence.

## Assessor (Appendix II, Ch. II.B)

The Assessor should be a **multidisciplinary team** within the PSE — the risk surface
is not just technical. Recommended functions: (a) product development; (b) policy /
internal regulatory; (c) user protection / Trust & Safety; (d) system security & data
protection; (e) experts/consultants if necessary. Headcount is set by PSE need.

If the PSE appoints an **external party** as Assessor, the Assessor must possess, at
minimum, expertise in: child psychology; child physiology; information technology;
system security and personal-data protection; legal; and digital marketing.

## Evidence & completion of the worksheet (Ch. II.C)

Each parameter needs **valid, relevant supporting evidence**, including but not limited
to: **Documents** (operational guidelines, policy standards, technical specs); **Model
Cards** (a standard overview of an AI/ML model — what it does, architecture,
performance, limitations, risks, recommended use); **UX survey reports** (evaluations
of user interaction, emotional response, perception); and/or other relevant forms.

Set each parameter's status to **YES/FOUND** (present in the PLF) or **NO/NOT FOUND**
(not present). Where status is NO/NOT FOUND **because a mitigation exists**, the PSE
must explain the **specific Technical Configuration** implemented (the worksheet's
"Specific Technical Configuration" column). Evidence must clearly show the presence or
absence of each parameter consistent with the reported status — **incomplete evidence
lets the Ministry adjust the result at verification.**

## Documentation of results (Ch. II.D) — minimum contents

(a) identity of the PSE; (b) identification of the PLF assessed; (c) a summary of
results per risk aspect; (d) the risk-level classification from the self-assessment;
(e) the risk management / mitigation measures (specific technical configurations).
Accompanied by the **self-assessment worksheet** plus **evidence and supporting
documents**. This forms part of the report submitted to the Minister.

## Updating (Ch. II.E)

The PSE must **update** the documented results whenever the self-assessment results
change; updates are documented and form part of the report.

## Reporting (Ch. II.F)

Report = the self-assessment worksheet covering all seven aspects (Section A para 2),
with valid supporting evidence, submitted to the **Director General** through the
**Ministry's electronic system**. **False or misleading** statements/data/documents may
lead the Minister to assess the PSE's compliance, impose administrative sanctions,
and/or report to law enforcement. **Legacy PLF** (in service before Permen 9/2026) must
self-assess and report within the stipulated timeframe. The PSE must **designate a
contact official** for submissions.

## Scoring rule (Ch. IV) — for reference

Parameter Risk Score = Risk Weight (%) × status (1 if marked in the weighted column,
else 0). Aspect Risk Score = sum across the aspect's parameters. An aspect is **high
risk when its score > 50%**. The PLF has a **high-risk profile if at least one of the
seven aspects exceeds 50%**. Classification: High > 50; Low ≤ 50. (The build script
implements this exactly; do not hand-compute or override it.)

## Verification of self-assessment results (Appendix III)

1. PSE submits the report + evidence to the Director General; receives an
   acknowledgment of receipt.
2. The Director General **verifies within 14 days** — examining the completeness of
   the report, evidence, and the PSE's identity.
3. Outcome is either "meets completeness" or "does not meet completeness."
4. If incomplete, the Director General may request clarification, revisions, additional
   mitigation, more documents, further explanation of a specific technical
   configuration, and/or test the configuration against the risk profile. The PSE must
   comply **within 7 days**; non-compliance → deemed incomplete.
5. If complete → the Director General **determines the risk profile**.
6. If rejected → reasons issued; the PSE may **resubmit within 3 days**, **no more than
   2 times**. Failing that, the PSE is deemed not to have fulfilled the self-assessment
   obligation.
7. The Ministry notifies the determination **within 3 days**, to the email given at
   submission, and **publishes** the risk profile on the Ministry's official website.

## Each aspect is assessed against five mechanism lenses (Ch. II.A.4)

When deciding a parameter's status, look across: (a) user interaction mechanisms;
(b) content distribution and recommendation systems; (c) personal-data processing
mechanisms; (d) user-interface design; and (e) other features/mechanisms affecting
children's safety, security, and well-being. Risk is identified by locating the
**Technical Configurations** in the PLF tied to each parameter.
