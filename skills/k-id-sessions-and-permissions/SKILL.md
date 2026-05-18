---
name: k-id-sessions-and-permissions
description: >
  Enforces k-ID permissions correctly on both client and server — renders one permission-gated UI control per `session.permissions` entry (not a hardcoded subset), picks the right lock label for each status and manager (including `verifiedAgeThreshold` permissions such as Brazil ECA Digital loot-boxes / targeted ads at 18, direct marketing at 12, UK Online Safety Act 18+ features, and Australia social media minimum age), calls `/session/upgrade` with the exact body shape, handles the `CHALLENGE_SESSION_UPGRADE_BY_AGE_ASSURANCE` branch for threshold permissions, and runs top-level session refresh plus discovery for the product's real permission slugs. Use when building the post-gate app screen, gating features, adding permission upgrade flows, or enforcing permissions on server endpoints. Not for the initial age gate (see k-id-age-gate) and not for consent polling or age-assurance UX (see k-id-consent-and-challenges or k-id-age-verification).
license: Apache-2.0
metadata:
  version: "1.0.0"
  vendor: k-ID
---

# k-ID Sessions and Permissions

A k-ID session carries a jurisdiction-specific permissions array. The
app's job is to render a gated control for **every** permission in
that array — with the right label — and to let the user request
upgrades correctly. The server's job is to enforce those permissions
on every privileged call. Cutting corners on either side produces
compliance violations that ship and stay shipped.

## When to use

Use this skill when the user is:

- Building the screen that lists features after `/age-gate/check`.
- Writing the permission-gated UI control (sometimes called
  `GatedFeature` or similar in a codebase — it is not a k-ID
  primitive, just the app's wrapper around a locked/unlocked
  feature) and its lock labels.
- Calling `/session/upgrade` or handling its three outcomes
  (approved, challenged, locked).
- Running discovery for real permission slugs (the ones the Compliance
  Studio product actually uses — not the ones from the starter pack).
- Enforcing permissions on server endpoints (the trust boundary — load
  `k-id-server-trust-boundary` too).
- Implementing top-level session refresh that survives visibility
  changes and modal lifecycles.

## Core steps

### 1. Run permission discovery — don't hardcode slugs

The permission slugs in a Compliance Studio product are
product-specific. The starter pack (`send_text`, `play_online`, etc.) is
almost never what a real product ends up with. Discovery means:

1. Create a fresh session via `/age-gate/check` for an adult of the
   target jurisdiction.
2. Inspect `session.permissions` in the response.
3. Use those `name` strings as your slugs — everywhere.

The slugs in one product's documentation or starter pack do not
carry over to another product. A slug that isn't in the discovered
array is not configured for the product and will never enable —
match `session.permissions` exactly.

Reference:
[`docs.k-id.com/concepts/access-features-consent/permissions`](https://docs.k-id.com/concepts/access-features-consent/permissions).

### 2. Render one gated control per permission — iterate the array

Iterate `session.permissions` and render one gated control per
slug. Iterating the array (instead of hardcoding a subset) keeps
the UI in sync as Compliance Studio adds, renames, or reconfigures
permissions.

### 3. Lock labels — by status, manager, and session kind

```
if PROHIBITED                          → "Not available"        → no tap handler (greyed out)
if adult && ageVerificationStatus === "unverified" → "Verify to unlock" → open verification prompt (k-id-age-verification)
if verifiedAgeThreshold && !verified   → "Verify your age"      → open verification prompt (k-id-age-verification)
if !hasRealSession                     → "Waiting for parent"   → no tap handler
if pendingChallenge                    → "Get parent permission" → open consent-request UI
if GUARDIAN-managed                    → "Ask parent"           → open upgrade UI
if PLAYER-managed                      → "Tap to enable"        → open upgrade UI (auto-approves)
if enabled                             → render children
```

The `verifiedAgeThreshold` case applies to permissions gated by age
assurance rather than parental consent — for example Brazil ECA
Digital loot-boxes (18), targeted ads (18), direct marketing (12),
UK Online Safety Act 18+ features, and Australia social media (16).
These permissions are **never** `GUARDIAN`-managed and unlock only
through age assurance. A parental-consent challenge returns `PASS`
but the permission stays locked — route threshold permissions
through [`k-id-age-verification`](../k-id-age-verification/SKILL.md).

For unlocking the enabled case — just `if (enabled) return children;`.
Do NOT add `&& ageVerificationStatus === "verified"` as an extra
guard. Unverified-adult sessions already have the minor-default
permissions baked into `session.permissions`; adding a verification
guard blocks features the minor defaults intentionally allow.

### 4. Call `/session/upgrade` with the EXACT body shape

The parameter name is `requestedPermissions`, not `permissions`. Each
item is `{ name: <slug> }`, not a bare string.

```http
POST /session/upgrade
Authorization: Bearer <server-only API key>
Content-Type: application/json

{
  "sessionId": "...",
  "requestedPermissions": [ { "name": "multiplayer_voice_chat" } ]
}
```

Response has permissions at `data.session.permissions`, NOT
`data.permissions`. Getting this wrong means your code reads `undefined`
and concludes the upgrade failed. For full shape:
[`docs.k-id.com/api/endpoints/upgrade-session`](https://docs.k-id.com/api/endpoints/upgrade-session).

### 5. Handle the four upgrade outcomes

| Outcome | Condition | UI |
|---|---|---|
| `approved` | Returned permissions include the requested slug with `enabled: true` | "Unlocked!" → `refreshSession()` → auto-close |
| `challenged` (consent) | Response includes `challenge.url` or `challenge.challengeId` for a consent challenge | Render k-ID widget iframe; poll `get-challenge-status` at 5s for `PASS` |
| `challenged` (age assurance) | Response includes `CHALLENGE_SESSION_UPGRADE_BY_AGE_ASSURANCE` — the permission has a `verifiedAgeThreshold` and the user hasn't proved age yet | Hand off to `k-id-age-verification` (threshold pattern) — do NOT render the consent widget here |
| `locked` | Permission remains prohibited by parent, jurisdiction, or user age below `verifiedAgeThreshold` | "Not available here" (below threshold) or "Parent turned this off — ask in Family Connect" (guardian-blocked) |

For `challenged`, prefer generating an embedded widget URL via
[`/widget/generate-manage-session-permissions-url`](https://docs.k-id.com/api/endpoints/generate-manage-session-permissions-url)
(embedded experience); fall back to the `challenge.url` returned by
`/session/upgrade` if that fails. Never show an email input on the
upgrade modal — that's a consent-flow responsibility (see
`k-id-consent-and-challenges`).

### 6. Refuse to render an empty-permissions screen

An empty `session.permissions` array for what should be a
full-access adult indicates a configuration or provisioning issue,
not a normal empty state. Show a recovery UI that lets the user
re-run discovery or contact support instead of rendering a
fully-locked screen.

### 7. Top-level session refresh

Mount a 30-second interval at the top level of the signed-in app
(not inside any modal or gated control) that refreshes the session
via `GET /session/get`. Wake it on `visibilitychange` and `focus`.
This propagates:

- Parent-initiated permission changes from Family Connect.
- Age verification completions from other tabs.
- Jurisdiction updates from travel.

### 8. Enforce permissions on the server

Client-side gating is UX. The real enforcement is server-side. Every
privileged route handler:

1. Fetches the session from k-ID (`/session/get` or
   cached-and-invalidated).
2. Confirms `session.permissions.find(p => p.name === required).enabled === true`.
3. Rejects otherwise with `403`.

This boundary is documented in
[`k-id-server-trust-boundary`](../k-id-server-trust-boundary/SKILL.md).

### 9. `refreshSession` with fresh state

`refreshSession` inside a `useCallback` captures stale
`ageVerificationStatus` / `isAgeVerified` values. Sync those into
`useRef`s updated every render, and read the refs inside the
callback. Without this, a refresh right after a verification
completes reads the pre-verification values and returns the session
to the unverified state.

## Gotchas

- **`requestedPermissions: [{ name }]`**, not `permissions: [...]`.
  Other shapes are rejected with 400.
- **Read the response from `data.session.permissions`**, not
  `data.permissions`. The `data.permissions` path is `undefined`
  and produces "upgrade succeeded but UI never updates".
- **Iterate `session.permissions` to render gated controls.** A
  hardcoded subset will drift out of sync as Compliance Studio
  adds or renames permissions.
- **`if (enabled) return children` — don't add an extra
  `ageVerificationStatus === "verified"` guard.** Unverified-adult
  sessions already reflect minor defaults in `session.permissions`;
  an extra guard blocks features the defaults intentionally allow.
- **An empty `session.permissions` for an adult session indicates
  a configuration or provisioning issue.** Surface a recovery UI
  rather than a fully-locked screen.
- **Run discovery to obtain real slugs.** Starter-pack or
  copy-pasted slugs rarely match a product's Compliance Studio
  configuration.
- **`verifiedAgeThreshold` permissions are never `GUARDIAN`-managed.**
  Brazil ECA Digital (loot-boxes, targeted ads, direct marketing), UK
  Online Safety Act 18+ features, and Australia social media minimum
  age all unlock only through age assurance. A parental-consent
  challenge returns `PASS` but leaves the permission locked — route
  these through `k-id-age-verification`.
- **No email input on the upgrade UI.** That's consent-flow UX.
- **`challenged` outcomes prefer the embedded widget URL from
  [`/widget/generate-manage-session-permissions-url`](https://docs.k-id.com/api/endpoints/generate-manage-session-permissions-url)**,
  falling back to `challenge.url` from `/session/upgrade`. Some
  jurisdictions return one, some the other.
- **`PROHIBITED` has no tap handler.** Tapping it does nothing — do
  not open a modal that explains why; use the greyed state to
  communicate "not available".
- **Top-level session refresh at 30s is mandatory.** Without it,
  parent permission changes from Family Connect never reach the UI.
- **Session-refresh functions + stale state.** If the refresh
  function is captured in a closure (e.g. `useCallback`), capture
  `ageVerificationStatus` via a ref synced each render; otherwise
  refresh reads stale values and returns a just-verified user to
  the unverified state.
- **Never bypass gates on the server.** Client-side gating is UX; the
  real check is
  `session.permissions[name].enabled === true` on every privileged
  route.

## Defaults

- Gated-control tap targets: ≥44px tall.
- Lock label font weight: match surrounding text; don't bold.
- Upgrade UI: 480px wide, embedded widget for challenged outcomes.
- Session refresh: 30s + visibility/focus wakes.
- Upgrade challenge poll: 5s.
- Server enforcement: always `session.permissions.find(p => p.name === required).enabled === true`,
  treat missing as false.

## Validation step

Confirm all of the following:

1. Dump `session.permissions` in dev mode — every slug has a rendered
   gated control.
2. Toggle a permission in Compliance Studio — within 30 seconds the
   UI reflects the change (proves background refresh).
3. Tap an `Ask parent` gate — `/session/upgrade` body has
   `requestedPermissions: [{ name }]`; response is parsed from
   `data.session.permissions`.
4. Server: `curl` a privileged route without a valid session — 403.
   With a session lacking the permission — 403. With a session that
   has it — 200.
5. Complete age verification while the app tab is backgrounded —
   focus the tab and the session shows verified within 5 seconds.

## Next steps

- Upgrade produces a challenge → [`k-id-consent-and-challenges`](../k-id-consent-and-challenges/SKILL.md).
- Unverified adult or `verifiedAgeThreshold` → [`k-id-age-verification`](../k-id-age-verification/SKILL.md).
- Server-side enforcement → [`k-id-server-trust-boundary`](../k-id-server-trust-boundary/SKILL.md).
- Live push of changes from parent → [`k-id-webhooks`](../k-id-webhooks/SKILL.md).

Canonical references:
- [Sessions concept](https://docs.k-id.com/concepts/access-features-consent/sessions)
- [Permissions concept](https://docs.k-id.com/concepts/access-features-consent/permissions)
- [`GET /session/get`](https://docs.k-id.com/api/endpoints/get-session)
- [`POST /session/upgrade`](https://docs.k-id.com/api/endpoints/upgrade-session)
- [`POST /session/update-jurisdiction`](https://docs.k-id.com/api/endpoints/update-jurisdiction)
- [`session.changepermissions` webhook](https://docs.k-id.com/events/webhooks/event-types/session-changepermissions)
- [Managing sessions and permissions quickstart](https://docs.k-id.com/get-started/quickstart-guides/managing-sessions-permissions)
