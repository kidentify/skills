# Assessor personas — the multidisciplinary review (Kepmen 142, Ch. II.B)

Kepmen 142/2026 requires the self-assessment to be done by a **multidisciplinary
team**, because the risk surface spans content, contact, consumer, data, addiction,
psychological, and physiological aspects — it cannot be assessed credibly from a
single (usually engineering) point of view. This file defines a persona per required
function so the assessment is genuinely reviewed through each lens.

**How to use these.** When scoring the 58 parameters, do not answer everything from a
product/eng default. Walk each aspect through the persona that owns it: adopt that
persona's stance, ask its questions, and demand the evidence it would demand before
recording a status. Record each persona's reviewer in `assessor_team` so they appear
on the Assessor & sign-off sheet. Where a persona's expertise is not held in-house, the
PSE should appoint an external party — and an external Assessor must hold, at minimum,
expertise in child psychology, child physiology, information technology, system
security and personal-data protection, legal, and digital marketing (Ch. II.B.4).

---

## 1. Product Development — "the ground truth"

- **Function (Ch. II.B.2.a):** product development team.
- **Lens:** what the product *actually does*, technically. The factual anchor for
  every parameter — the others interpret risk, this persona confirms presence/absence.
- **Owns:** the accuracy of every FOUND / NOT_FOUND status across all seven aspects,
  and the identification of the underlying **Technical Configuration** for each.
- **Asks:** Does this feature actually ship in the Indonesia build? Default-on or
  opt-in? Which code path / config flag controls it? Is the mitigation we're claiming
  actually live in production, or just planned?
- **Brings as evidence:** technical specs, architecture diagrams, config screenshots,
  release notes, **Model Cards** for any AI/recommender feature.
- **Sign-off:** confirms the technical configurations and statuses reflect reality.

## 2. Policy / Internal Regulatory — "the mapper and filer"

- **Function (Ch. II.B.2.b):** policy development / internal regulatory team.
- **Lens:** how the product maps onto PP TUNAS, Permen 9/2026, and Kepmen 142/2026,
  and what must be filed.
- **Owns:** the **Appendix I scope screening** (is the PLF even in scope?), correct
  interpretation of the computed HIGH/LOW determination, the documentation minimum
  contents (Ch. II.D), the reporting mechanics and the **verification lifecycle**
  (Appendix III), and designating the contact official.
- **Asks:** Which of the five in-scope indicators do we trip? Is our evidence complete
  enough to survive verification? Have we updated the worksheet since the last product
  change? Are any claims at risk of being "false or misleading"?
- **Brings as evidence:** terms/policies, the filing record, prior determinations,
  amendment tracking (has the regulation changed since the catalog version?).
- **Sign-off:** confirms regulatory alignment and filing-readiness.

## 3. User Protection / Trust & Safety — "the harm lens"

- **Function (Ch. II.B.2.c):** user protection or trust & safety team.
- **Lens:** how children actually get hurt on the product — contact, content, and
  psychological harm.
- **Owns:** aspect **(a) contact with unknown persons** (KK01–KK09), aspect **(b)
  exposure to harmful content** (KN01–KN07), and aspect **(f) psychological health**
  (GP01–GP09). Special attention to the protective parameters whose *absence* is the
  risk: block/report (KN06, GP09) and content filtering.
- **Asks:** Can a stranger reach a child here, and how? Is there filtering on DMs,
  open interaction, and recommendations? Do block/report and proactive detection
  exist and work in Bahasa Indonesia? What's the takedown turnaround?
- **Brings as evidence:** moderation policies, T&S runbooks, block/report screenshots,
  takedown SLA reports, **UX survey reports** on how children experience the surface.
- **Sign-off:** confirms the contact, content, and psychological-harm scoring.

## 4. System Security & Data Protection (DPO) — "the data lens"

- **Function (Ch. II.B.2.d):** system security & data protection team.
- **Lens:** the security and lawful processing of children's personal data.
- **Owns:** aspect **(d) threats to children's personal-data security** (DP01–DP07) —
  including the protective parameters scored on absence: security measures (DP03), the
  **DPIA** (DP04), the privacy notice (DP06), and the **DPO** function (DP07).
- **Asks:** Can a child change privacy settings without a parent? Are children's
  profiles public by default? Is there a DPIA (children's data is "specific personal
  data")? Is there a Privacy Notice a child and parent can understand pre-registration?
  Is a DPO appointed?
- **Brings as evidence:** the DPIA document, privacy notice, data-flow maps, security
  measure documentation, DPO appointment record.
- **Sign-off:** confirms the data-security aspect and the existence of the DPIA, notice,
  and DPO.

## 5. Experts / Consultants — "the specialist lenses" (if necessary)

- **Function (Ch. II.B.2.e):** experts or consultants, engaged where in-house
  expertise is insufficient. These map directly to the minimum-expertise list for an
  appointed external Assessor (Ch. II.B.4):

  - **Child psychologist** — aspects **(e) addiction** (AD01–AD11) and **(f)
    psychological** (GP01–GP09): immersive/engagement design, social comparison,
    variable rewards, disappearing content, scary content.
  - **Child physiologist** — aspect **(g) physiological** (GF01–GF08): continuous
    access, sleep-hour notifications, night-mode/safe-volume defaults, autoplay,
    repetitive actions, dangerous-challenge enablement. (Resolve the GF01/GF02
    polarity flags here.)
  - **Information-technology / system-security expert** — supports personas 1 and 4 on
    technical configurations and security measures.
  - **Personal-data-protection expert** — supports persona 4 on the DPIA, lawful
    basis, and data-subject rights.
  - **Legal expert** — owns the genuine judgement calls: close-call determinations,
    in-scope edge cases, evidence sufficiency, and the final review before filing.
  - **Digital-marketing expert** — aspect **(c) exploitation as consumers** (EK01–EK07):
    offers/ads to children, profiling-based targeting, dark patterns, payment and
    auto-renewal without parental verification.
- **Sign-off:** each specialist signs off on the aspect(s) within their expertise.

---

### Quick map: aspect → owning persona

| Aspect | Owning persona(s) |
|---|---|
| (a) Contact with unknown persons (KK) | Trust & Safety |
| (b) Harmful content (KN) | Trust & Safety |
| (c) Exploitation as consumers (EK) | Digital-marketing expert + Policy |
| (d) Data security (DP) | Security & Data Protection (DPO) |
| (e) Addiction (AD) | Child psychologist + Product |
| (f) Psychological health (GP) | Trust & Safety + Child psychologist |
| (g) Physiological health (GF) | Child physiologist + Product |
| Scope screening (App. I) & filing | Policy / Internal Regulatory |
| Technical ground truth (all) | Product Development |
| Close calls & final review | Legal expert |
