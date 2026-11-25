# pp-tunas-risk-assessment — release notes

## 1.0.3

- The Determination sheet warning no longer says GF02 can change every profile.
  It asks counsel to confirm the GF02 polarity.

## 1.0.2

- The catalog follows Kepmen 219/2026, which amends Appendix II of Kepmen 142/2026.
- GF01 now applies its weight when found, and the weight is 23.53, as the gazette prints
  it. Before, it applied 25.53 when not found.
- Kepmen 219 deleted the worksheet instruction that conflicted with the parameter tables.
  The tables are now the only scoring rule.
- GF02 is unchanged: the amended table still prints its weight under NO. The worksheet
  keeps its polarity flag for counsel.
- The Determination sheet warns when a parameter with a polarity flag can change the profile.

## 1.0.1

- The amendment check uses `lookup_recent_updates` and `lookup_legal_horizons`, not an
  internal-only tool that customer MCP clients cannot list.

## 1.0.0

Indonesia PP Tunas (PP No. 17/2025 + Permen No. 9/2026) children's-safety risk-level
self-assessment, implementing the instrument fixed by Kepmen Komdigi No. 142/2026.

- Embedded, version-pinned parameter catalog (`references/kepmen142_parameters.json`):
  all seven aspects and 58 coded Assessment Parameters (KK/KN/EK/DP/AD/GP/GF) with
  their legally-fixed risk weights and YES/NO scoring polarity.
- Deterministic worksheet builder (`scripts/build_self_assessment.py`): the assessor
  supplies per-parameter status + evidence; the script computes Parameter/Aspect Risk
  Scores, the >50% per-aspect flags, and the "any one aspect → HIGH-RISK profile"
  determination per Chapter IV, and warns on unanswered parameters.
- Appendix I in-scope screening (the five indicators; "significant" = ≥25 child users).
- Multidisciplinary Assessor & sign-off (Ch. II.B) with persona definitions
  (`references/assessor_personas.md`) and the external-appointee minimum-expertise list.
- Per-parameter evidence (Documents / Model Cards / UX survey reports) and the
  "Specific Technical Configuration" justification column (Ch. II.C).
- Filing & verification lifecycle documented in `references/kepmen142_process.md`.
- Supplementary, clearly-fenced k-ID layer (remediation/gating matrix, obligations,
  sources) — grounded live in neimo. and labelled as not part of the Komdigi filing.
