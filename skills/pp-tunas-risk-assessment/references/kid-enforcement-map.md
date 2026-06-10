# Mapping PP Tunas obligations → k-ID enforcement mechanisms

The point of this skill is to finish the job: not just "you're high risk" but
"here is exactly what to build, per feature, per age band, and which k-ID
capability enforces it." This file is the lookup table for that mapping. Use it
to fill the **k-ID mechanism** column of the Feature Gating Matrix and the
Obligations sheet, and to phrase the "what to do next" so engineering can act.

Treat the ages here as placeholders — the actual thresholds come from the live
neimo. `settings` / `monetization-model-s` / `age-threshold` lookups. This file
maps *obligation type → mechanism*, which is stable; the *numbers* come from
neimo.

## The k-ID capability vocabulary

- **Age Gate** — `/age-gate/check`. The front door. Collects claimed age, takes
  platform age signals, detects jurisdiction (here, ID), and opens a session with
  a set of permissions. Everything else hangs off this.
- **AgeKit+ age assurance** — proves age to a real confidence level (facial age
  estimation, ID, credit card, reusable AgeKeys) when self-declaration is not good
  enough. This is what satisfies "age assurance commensurate with risk" (PP
  17/2025 Art. 22) and the prohibition on relying on self-declaration.
- **Verifiable Parental Consent (VPC)** — the consent / challenge flow (QR, OTP,
  email, direct link). For users under the threshold age, a guardian grants
  permissions; opt-in; and for under-18s the parent concludes transactions.
- **Session Permissions** — `session.permissions`. One permission per gated
  feature. The app renders/unlocks a feature only when its permission is enabled
  for that user's age + consent state. This is how per-feature gating is enforced.
- **`verifiedAgeThreshold` verification** — `/session/upgrade`. For features with a
  hard threshold age that needs *proven* age (not claimed) — e.g. an 18+ feature.
  Returns a challenge that AgeKit+ satisfies, then unlocks the permission.
- **Compliance Studio + Family Connect** — where the org baseline, per-jurisdiction
  overrides (set ID here), data notices, and the parent-facing consent experience
  are configured. The control plane behind the runtime calls above.

## Obligation → mechanism table

| PP Tunas obligation (verify ages in neimo.) | k-ID mechanism | Build step (phrase like this) |
|---|---|---|
| Determine user is/ isn't a child; set jurisdiction = ID | **Age Gate** (`/age-gate/check`) | Add the age gate at first run; pass platform age signals; jurisdiction → ID. |
| Age assurance commensurate with risk; no self-declaration (Art. 22) | **AgeKit+** | Require AgeKit+ assurance for any age-restricted feature; don't trust claimed age alone. |
| VPC for users under threshold; opt-in within the consent window; parent concludes under-18 transactions (Art. 9) | **VPC / consent flow** | Route under-threshold users through the consent challenge before unlocking; gate checkout behind parent approval. |
| Text chat (public/private) min/threshold age | **Session permission** + **AgeKit+** (+ `verifiedAgeThreshold` at the threshold) | One chat permission, unlocked only at/above the neimo. minimum age with assurance. |
| Voice chat / video chat gating | **Session permission** + **AgeKit+** | Separate permission per modality; lock for under-age sessions. |
| Forums gating | **Session permission** | Permission unlocked at the neimo. minimum age. |
| Links to 3rd-party chat apps | **Session permission** | Gate the outbound link at the neimo. threshold. |
| Custom username / custom avatar (threshold age, often 18) | **`verifiedAgeThreshold`** | Require proven age via `/session/upgrade` before enabling. |
| Profiling / behavioural ads / direct marketing by age (e.g. profiling 18+) | **Session permission** (`verifiedAgeThreshold` for the 18 ones) | Disable profiling/targeted-ads/direct-marketing permissions for under-age sessions. |
| Microtransactions / in-game currency / subscriptions (floor + parent-concludes-under-18) | **Session permission** + **VPC** | Gate purchase flow; for under-18, parent concludes via consent flow. |
| Loot boxes (floor; hard gambling prohibition) | **Session permission** | Lock loot-box permission below the neimo. floor; ensure mechanic isn't gambling. |
| Player trading / marketplace | **Session permission** + **VPC** | Same pattern as purchases. |
| Default-highest privacy settings for children | **Compliance Studio config** | Set child defaults to highest-privacy at the product/jurisdiction level. |
| Dark-pattern / covert-technique prohibition (Art. 17) | **product design** (not a k-ID call) | Remove nudges that over-collect, weaken privacy, or harm wellbeing — flag in design review. |
| Five-age-category + minimum-age + rating notices (Art. 20) | **product UI** + **data notices** (Compliance Studio) | Surface the five bands and rating; wire the data-notice content. |
| Location-tracking / activity-monitoring disclosure to parents | **data notices** + **VPC** | Disclose in the consent flow and parent notice. |
| Trust & safety: Bahasa-ID moderation, takedown SLA, local contact person, report high-risk conduct | **operational** (not a k-ID call) | Stand up moderation + reporting; appoint local contact; document SLAs. |
| DPIA (children's data = specific personal data, UU PDP Art. 34) | **process deliverable** | Complete a DPIA distinct from the seven-factor self-assessment. |
| Data-subject rights (access/deletion/etc.) | **product feature** | Implement the rights endpoints/flows for children's data. |
| Record-keeping & audit; respond to regulator info requests | **process** + **Compliance Studio** evidence | Keep the self-assessment, DPIA, and config history on file. |

When a row's mechanism is "product design", "operational", or "process", say so —
not everything is a k-ID API call, and pretending it is would be dishonest. The
value is in being precise about which is which.
