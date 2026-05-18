---
name: k-id-integration
description: "Router for k-ID integration work. Activates when the user is building, planning, or debugging a k-ID integration, or adding age-appropriate compliance — COPPA (US), GDPR-Kids (EU), UK AADC, UK OSA, Brazil ECA Digital, Australia Online Safety / social-media minimum age, or similar — in an app, game, site, or platform. Also activates on \"age assurance\", \"age verification\", \"AgeKit+\", \"parental consent\", \"age gate\", \"widget\", \"custom age gate\", and \"threshold verification\". Handles both full sessioned integrations (CDK — age gate + sessions + permissions + consent + verification) and standalone AgeKit+ (single age-proof, no persistent session). Within CDK, supports both approaches: fully custom UX (call /age-gate/check and /challenge/* directly, render your own UI — default, most brand-integrated) and pre-built k-ID widgets (age-gate, end-to-end, manage-permissions, data-notices iframes — fast-path fallback). Picks the right sibling skill(s). Not for generic age-rating or Compliance Studio configuration."
license: Apache-2.0
metadata:
  version: "1.0.0"
  vendor: k-ID
---

# k-ID Integration Router

This skill is the entry point for any k-ID integration task. It picks the
right specialized sibling skill and tells the agent to load it.

## When to use

Use this skill when any of the following is true:

- The user says "integrate k-ID", "kidentify", or "add age gate",
  "parental consent", "age verification", "age assurance", or
  "threshold verification".
- The user mentions any age-appropriate compliance regime: COPPA,
  GDPR-Kids, UK AADC, **UK Online Safety Act (OSA)**, **Brazil ECA
  Digital**, **Australia Online Safety / social media minimum age**,
  or similar. These skills cover all of them through a single k-ID
  integration — jurisdictional behaviour is driven by the server-side
  Compliance Studio configuration, not by branching in the app.
- The user references `docs.k-id.com`, Compliance Studio
  (`portal.k-id.com`), Family Connect (`family.k-id.com`), `asktoplay.com`,
  the `game-api.k-id.com` or `game-api.test.k-id.com` hosts, or any
  `/age-gate/`, `/session/`, `/challenge/`, `/age-verification/`, or
  `/webhook` endpoint.
- The user is building anything child-facing, age-restricted, or
  subject to age-threshold gating and asks about compliance without
  naming k-ID.

If the task is strictly about k-ID Compliance Studio configuration
(permission catalog, jurisdiction maps, trusted-adult preferences), this
is a UI task in the portal — not an integration task — and no skill
applies.

## Two integration shapes

Before routing, identify which shape the integration needs. These
require different skills — loading the wrong set wastes the agent's
context.

### Shape A — Full sessioned integration

Use when the product needs any of:

- Persistent per-user sessions across features
- Multiple gated features with per-feature permissions
- Parental consent for minors (COPPA, GDPR-Kids, UK AADC)
- A mix of adult and minor users
- Webhook-driven state changes over time (consent revoke, verification
  revoke, permission changes)

Typical examples: games, social platforms, multi-feature apps,
communication products.

Flow: **age gate → session → (consent | verification | threshold) →
permissions**. Start with `k-id-server-trust-boundary`, then
`k-id-age-gate`, then the feature skills for your flow.

### Shape B — Standalone age assurance (AgeKit+ only)

Use when the product only needs to prove a user's age **once**, for
**one decision**, with no ongoing session or permission state. The
outcome is a single PASS / FAIL.

Typical examples: 18+ sites under UK OSA, age-restricted
downloads, social media minimum-age checks (Australia), a single
high-risk action that needs age assurance.

No age gate. No sessions. No permissions. Just a call to
[`/age-verification/perform-access-age-verification`](https://docs.k-id.com/api/endpoints/perform-access-age-verification),
an iframe for the user to complete verification, and a webhook or
polled status to act on the result.

Flow: **`k-id-server-trust-boundary` → `k-id-age-verification`
(AgeKit+ standalone mode)**. That's it. Webhooks optional.

See [AgeKit+ overview](https://docs.k-id.com/agekit-plus/overview)
for the canonical description.

### Don't mix the two unnecessarily

If the product only needs a single age-proof decision, **do not**
stand up an age gate, a session, and a permission-management UI.
That's thousands of lines of unused code and adds compliance
surface area.
Conversely, if the product needs persistent per-user permissions, a
standalone AgeKit+ call by itself is not enough.

## Two UI approaches (Shape A only)

Within Shape A (full sessioned CDK integration) there is a second
decision: **custom UX workflows** or **widgets**. Both use the same
underlying k-ID compliance engine; the difference is how much of the
UI k-ID renders versus how much the product builds.

### Custom UX workflows — the default, best-integrated experience

Build the UI yourself (age slider, consent screen,
permission-management screen) and call the underlying APIs directly:
[`/age-gate/check`](https://docs.k-id.com/api/endpoints/check-age-gate),
[`/challenge/send-email`](https://docs.k-id.com/api/endpoints/send-email),
[`/challenge/generate-otp`](https://docs.k-id.com/api/endpoints/generate-otp),
[`/session/upgrade`](https://docs.k-id.com/api/endpoints/upgrade-session).
You maintain the compliance logic and regulatory copy; k-ID's
compliance engine still decides outcomes.

**Prefer custom UX** for the cleanest brand fit and the smoothest
player experience. Custom UIs render inline (no iframe), match the
product's look and feel exactly, and integrate natively with the
rest of the flow (single layout, shared components, consistent
motion). They also work on every platform k-ID supports, including
game consoles, Unity WebGL, and native desktop apps where iframes
aren't practical.

### Widgets — fast-path fallback for small, simple integrations

k-ID publishes pre-built widgets that render inside iframes (or
webviews). Each widget carries the built-in compliance logic for its
step: jurisdiction-appropriate age collection, automatic challenge
initiation when parental consent is required, correct language and
layout per region, and first-party handling of regulatory copy.

Available widgets:

- [`/widget/generate-age-gate-url`](https://docs.k-id.com/api/endpoints/generate-age-gate-url)
  — just the age gate.
- [`/widget/generate-e2e-url`](https://docs.k-id.com/api/endpoints/generate-e-2-eurl)
  — end-to-end flow: age gate + parental consent + data notices +
  permissions + parental preferences, one iframe, one redirect.
- [`/widget/generate-manage-session-permissions-url`](https://docs.k-id.com/api/endpoints/generate-manage-session-permissions-url)
  — per-permission upgrade / consent.
- [`/widget/generate-direct-notices-url`](https://docs.k-id.com/api/endpoints/generate-direct-notices-url)
  — data notices and consent.

Widgets emit DOM events to the parent window (`Widget.AgeGate.Result`,
`Widget.AgeGate.Challenge`, `Widget.ExitReview`,
`Widget.DataNotices.ConsentApproved`) — listen for these or use the
`options.redirectUrl` for redirect-based flows.

**Choose widgets** when the integration must be small, simple, and
fast to ship — proofs of concept, internal tools, early-stage games,
or products that can accept the iframe look and want minimum code and
minimum compliance surface area.

### Choose one per flow, not one per product

Custom and widgets can coexist in the same product — for example,
a custom age gate paired with the widget for permission upgrades.
The feature skills explain the fork for each flow.

## Routing rules

Choose the sibling skill whose description best matches the user's
request. If multiple match, load all relevant ones — feature skills
compose.

| User intent | Load this skill |
|---|---|
| **Standalone AgeKit+** — prove age once for a single decision, no session, no permissions (18+ sites, age-restricted downloads, AU social media age check) | `k-id-age-verification` (standalone mode) |
| Age gate UI, `/age-gate/check`, age default, platform age signals, jurisdiction detection | `k-id-age-gate` |
| Parental / guardian consent screen, QR / OTP / email, `/challenge/*`, top-level polling | `k-id-consent-and-challenges` |
| In-session age verification — unverified-adult state, iframe verification, new-tab detection | `k-id-age-verification` |
| **Threshold age assurance** — proving the user is at or above a specific age (UK OSA 18+, Brazil ECA Digital 18+ / 12+, Australia social media 16+) for a specific permission or feature | `k-id-age-verification` + `k-id-sessions-and-permissions` |
| `session.permissions` enforcement, `/session/upgrade`, permission-gated UI controls, permission discovery, `verifiedAgeThreshold` handling | `k-id-sessions-and-permissions` |
| Webhook handler, signature verification, event fan-out | `k-id-webhooks` |

Two companion skills apply across most feature work — load them
alongside the feature skills when the user is touching those
concerns:

| Concern | Load this skill |
|---|---|
| API key placement, server proxy, test vs prod URL, pre-flight connectivity | `k-id-server-trust-boundary` |
| iOS / Android / Unity, platform age signals from the OS, deep links | `k-id-mobile-native` |

## Default first steps for a new k-ID integration

Load skills in this order based on the integration shape.

### Shape A — Full sessioned integration

1. **`k-id-server-trust-boundary`** — get the API key, server proxy,
   and test vs prod URL right before anything else. Test-vs-prod
   mismatches surface later as 400/401 responses against apparently
   correct code.
2. **`k-id-age-gate`** — the entry flow. Everything else assumes you
   have a session.
3. Then whichever of `k-id-consent-and-challenges`,
   `k-id-age-verification`, `k-id-sessions-and-permissions`, or
   `k-id-webhooks` the user's immediate task requires.
4. `k-id-mobile-native` only if the target platform is iOS, Android, or
   Unity — otherwise it's noise.

### Shape B — Standalone AgeKit+

1. **`k-id-server-trust-boundary`** — API key stays on the server; the
   verification call is server-to-server.
2. **`k-id-age-verification`** (standalone mode) — the whole integration
   lives here.
3. **`k-id-webhooks`** if the product needs to act on the result
   server-side (recommended for production); polling works as well.
4. Skip `k-id-age-gate`, `k-id-sessions-and-permissions`, and
   `k-id-consent-and-challenges` entirely unless the product later
   evolves into Shape A.

## Gotchas

- **Parental consent and age assurance are different paths.** Guardian
  consent (`k-id-consent-and-challenges`) unlocks `GUARDIAN`-managed
  permissions for minors. Age assurance (`k-id-age-verification`)
  unlocks `verifiedAgeThreshold` permissions for any user (UK OSA 18+
  features, Brazil loot-boxes, AU social media). A
  `verifiedAgeThreshold` permission is **never** `GUARDIAN`-managed:
  route threshold permissions through `k-id-age-verification`.
  Routing through parental consent returns `PASS` but leaves the
  permission locked.
- **Do not write integration code before calling discovery.** The real
  permission slugs for a product come from `/session/get` on a fresh
  session — hardcoded slugs will be wrong. See
  [`docs.k-id.com/concepts/access-features-consent/permissions`](https://docs.k-id.com/concepts/access-features-consent/permissions).
- **Do not assume a session has a full permissions set.** Unverified-adult
  sessions and limited-access-minor sessions
  (`challenge.childLiteAccessEnabled: true`) are valid end states
  with reduced permissions. Each feature skill explains how to
  render them.
- **Do not route to `k-id-age-verification` for the initial age check.**
  Age verification / age assurance is a separate, heavier flow invoked
  after the age gate. The age gate comes first and always.
- **Do not invent API endpoint shapes.** All request and response
  bodies come from [`docs.k-id.com/api`](https://docs.k-id.com/api/overview).
  When in doubt, the feature skills link to the exact endpoint page.
- **Pick the right integration shape first.** Standing up a full
  sessioned integration for a product that only needs a single age
  check is over-engineering. Standing up only standalone AgeKit+ for a
  product that needs per-user permissions over time is
  under-engineering and will force a rewrite. Confirm the shape with
  the user before coding.
- **Default to custom UX for Shape A.** Custom UIs produce the
  cleanest brand fit, the smoothest player experience, and work on
  every platform (including Unity WebGL, consoles, and native
  desktop apps where iframes aren't practical). Drop to the widget
  when the integration must be small, simple, and as fast as
  possible to ship — not because it's the safer-looking choice.
  Widgets still carry jurisdiction-appropriate age collection and
  challenge-initiation logic out of the box; custom UIs have to be
  wired to the same compliance engine via the feature skills'
  gotchas and defaults — read them before shipping.

## Doc-first contract

Feature skills in this bundle encode patterns and invariants. API request
and response shapes come from [`docs.k-id.com`](https://docs.k-id.com).
Always verify field names against the canonical endpoint reference
before sending a request — the API rejects malformed bodies with 400
and no descriptive body.

## Validation step

Before declaring an integration done, run the checklist for the shape
you built.

### Shape A — Full sessioned integration

1. A fresh session from `/age-gate/check` returns the expected
   `ageCategory`, `jurisdiction`, and `permissions`.
2. A permission-gated UI control for every permission in
   `session.permissions` renders with the correct lock label.
3. The server rejects privileged requests without a valid
   `session.permissions[name].enabled === true` check.

### Shape B — Standalone AgeKit+

1. Calling `/age-verification/perform-access-age-verification` with
   the target `jurisdiction` and `criteria` returns an `id`, `url`,
   and `shortUrl`.
2. Loading the `url` in an iframe lets the user complete verification
   end-to-end.
3. After success, either the webhook fires or
   `/age-verification/get-status?id=<id>` returns the final result —
   and the product acts on PASS / FAIL correctly.
4. The API key is never reachable from the browser.

If any checks fail, load `k-id-server-trust-boundary` and start again
from the pre-flight checklist.

## Next steps

- [`k-id-age-gate`](../k-id-age-gate/SKILL.md)
- [`k-id-consent-and-challenges`](../k-id-consent-and-challenges/SKILL.md)
- [`k-id-age-verification`](../k-id-age-verification/SKILL.md)
- [`k-id-sessions-and-permissions`](../k-id-sessions-and-permissions/SKILL.md)
- [`k-id-webhooks`](../k-id-webhooks/SKILL.md)
- [`k-id-server-trust-boundary`](../k-id-server-trust-boundary/SKILL.md)
- [`k-id-mobile-native`](../k-id-mobile-native/SKILL.md)

Canonical docs: [`docs.k-id.com`](https://docs.k-id.com).
