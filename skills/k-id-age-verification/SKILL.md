---
name: k-id-age-verification
description: "Implements k-ID age verification and assurance for all three CDK patterns: (1) standalone AgeKit+ with no session (single age-proof — UK OSA 18+, age-restricted downloads, Australia social-media minimum age), (2) unverified-adult verification after the gate in a sessioned integration, (3) per-permission threshold verification (Brazil ECA Digital loot-boxes / targeted ads, UK OSA 18+, Australia social media, any verifiedAgeThreshold regime). Covers /age-verification/perform-access-age-verification (with or without sessionId), /session/upgrade returning CHALLENGE_SESSION_UPGRADE_BY_AGE_ASSURANCE, iframe modal (never window.open), in-app prompt, new-tab return-path detection (server poll + BroadcastChannel + visibility wake), result via webhook or polling, race-free session update. References AgeKit+ waterfall and ConnectID. Use for AgeKit+, unverified sessions, verifiedAgeThreshold, highly effective age assurance, or \"user verified but app never unlocked\". Not the initial gate or consent (see sibling skills)."
license: Apache-2.0
metadata:
  version: "1.0.0"
  vendor: k-ID
---

# k-ID Age Verification and Age Assurance

This skill covers **age assurance** — proving a user's age (or that
they're above a required age) to the standard a regulator requires.
Three concrete patterns show up in k-ID integrations:

1. **Standalone AgeKit+** (no session). The product only needs to
   prove age once, for one decision, with no persistent k-ID session
   and no permission state. Typical for 18+ sites under UK
   OSA, age-restricted downloads, Australia social media minimum-age
   checks, or a single high-risk action. Call
   `/age-verification/perform-access-age-verification` **without** a
   `sessionId`, render the returned URL in an iframe, act on the
   result via webhook or `GET /age-verification/get-status`.
2. **Unverified-adult in a sessioned integration.**
   `/age-gate/check` returns an adult session with
   `ageVerificationStatus === 'unverified'`. The session exists but
   privileged permissions are withheld until the user completes
   verification. Common for COPPA-style "prove you're not a minor"
   gates layered on top of a full k-ID integration.
3. **Per-permission threshold verification** (in a sessioned
   integration). A specific permission carries a
   `verifiedAgeThreshold` (for example `18` for Brazil ECA Digital
   loot-boxes / targeted ads, `12` for Brazil direct marketing, `18`
   for UK OSA 18+ permissions, `16` for Australia social
   media). `/session/upgrade` returns a
   `CHALLENGE_SESSION_UPGRADE_BY_AGE_ASSURANCE`. The whole session
   isn't locked — just that one feature.

All three patterns use the same verification UX primitives (iframe
modal, detection strategies, result via webhook or polling) and the
same k-ID age-assurance methods (ID document, facial age estimation,
AgeKey, credit card, email age estimation, regional providers such
as ConnectID in Australia and Singpass in Singapore). The "highly
effective age assurance" standard from UK OSA maps to the same
endpoints — method selection happens server-side based on
jurisdiction and Compliance Studio configuration, not in client
code.

## When to use

Use this skill when the user is:

- Adding standalone AgeKit+ age assurance to an 18+ site,
  age-restricted download, or single high-risk action (Shape B of
  the router's two integration shapes).
- Building the in-app verification prompt that asks a user to
  verify inside a sessioned integration.
- Calling `/age-verification/perform-access-age-verification` or
  `/age-verification/get-status` in either shape.
- Handling `CHALLENGE_SESSION_UPGRADE_BY_AGE_ASSURANCE` returned by
  `/session/upgrade` for a `verifiedAgeThreshold` permission.
- Implementing polling, webhook handling, or BroadcastChannel
  detection for when the user completes verification.
- Meeting "highly effective age assurance" requirements under the UK
  Online Safety Act, or equivalent thresholds under Brazil ECA
  Digital or Australia's social media age rules.
- Diagnosing reports like "user verified but the app never
  unlocked the feature" or "webhook fired but our app never
  received it".

This skill is the **whole integration** for Pattern 1 (standalone
AgeKit+). For Patterns 2 and 3 it composes with
[`k-id-sessions-and-permissions`](../k-id-sessions-and-permissions/SKILL.md).

## Core steps

### 1. Detect which pattern applies

**Pattern 1 — Standalone AgeKit+ (no session).** The product has no
k-ID session, no age gate, no permission-management UI. The trigger
is a
user-initiated action: they click a button on an 18+ site,
attempt an age-restricted download, or tap "verify" on a social
media sign-up flow. No state to check ahead of time — just call the
verification endpoint when the user starts the flow. See
[AgeKit+ overview](https://docs.k-id.com/agekit-plus/overview).

**Pattern 2 — Unverified adult in a sessioned integration.**
`/age-gate/check` (or `/session/get`) returns:

```json
{
  "session": {
    "sessionId": "...",
    "ageCategory": "adult",
    "ageVerificationStatus": "unverified",
    "permissions": [ /* minor-default permissions */ ]
  }
}
```

The session has real permission data (minor defaults, not emptiness).
Treat the app as operational but with a persistent verification
prompt and locked features until verification completes.

**Pattern 3 — Threshold permission (sessioned).** A specific
permission in `session.permissions` carries a `verifiedAgeThreshold`:

```json
{
  "name": "loot-boxes-paid-gameplay-impacting",
  "enabled": false,
  "managedBy": "PLAYER",
  "verifiedAgeThreshold": 18
}
```

The rest of the session is fine — only this feature is locked until
the user proves they're at or above the threshold. Calling
`/session/upgrade` with this permission returns
`CHALLENGE_SESSION_UPGRADE_BY_AGE_ASSURANCE` (not the standard
consent challenge).

All three patterns feed the same verification UX in steps 2–6. The
trigger differs; the UX does not.

### 2. Call `/age-verification/perform-access-age-verification` correctly

Body shape matters. The age criterion is nested under `criteria`,
never at the top level. `sessionId` is **optional** — include it for
Patterns 2 and 3, omit it for Pattern 1.

**Pattern 1 — Standalone AgeKit+:**

```http
POST /age-verification/perform-access-age-verification
Authorization: Bearer <server-only API key>
Content-Type: application/json

{
  "jurisdiction": "GB",
  "criteria": { "ageCategory": "ADULT" }
}
```

Add optional fields when useful:

- `subject.email` to reuse a prior k-ID verification result if one
  exists for that email (avoids asking the user again).
- `subject.claimedAge` if your product already collected a claimed
  age and wants to inform age estimation.
- `subject.id` (temporary session ID or hashed user ID) to correlate
  multiple attempts for the same user across methods.
- `options.redirectUrl` if verification will open in a browser or
  webview rather than an iframe — k-ID redirects there with
  `verificationId` and `result` query params on completion.

**Patterns 2 and 3 — In a sessioned integration:**

```http
POST /age-verification/perform-access-age-verification
Authorization: Bearer <server-only API key>
Content-Type: application/json

{
  "sessionId": "...",
  "jurisdiction": "US",
  "criteria": { "ageCategory": "ADULT" }
}
```

Top-level `age`, `ageCategory`, or `minimumAge` are rejected with
400 in either shape. All age inputs live inside `criteria`.

Response always includes `id`, `url`, and `shortUrl`. Treat
`shortUrl` as opaque; don't rebuild or re-shorten the full `url`.
For full shape see
[`docs.k-id.com/api/endpoints/perform-access-age-verification`](https://docs.k-id.com/api/endpoints/perform-access-age-verification).

### 3. Show the verification in an iframe modal — never a new tab

```tsx
<Modal width={480} heightClamp="min(720px, calc(100vh - 48px))">
  <Toolbar title="Verify your age" onClose={...} />
  <iframe src={verification.url} style={{ flex: 1, border: 'none' }} />
</Modal>
```

The iframe content **is** the UI. No padding around it, no ornamental
header, no explanatory copy in your modal. Thin toolbar with title and
close (`x`) only.

Never `window.open(verification.url, '_blank')`. Two reasons:

1. On iOS Safari, popup windows are aggressively blocked and the
   verification never starts.
2. Even when the popup works, detection becomes a polling nightmare
   (see step 5).

### 4. Entry component — owns its own state

In a sessioned integration this is the verification prompt (a
banner or card) that offers "Verify to unlock". In a standalone
integration it's whatever button or CTA triggers verification (an
18+ access gate, a
download button, a social sign-up step). Either way:

- **Fetch the URL on-demand** when the modal opens — never pre-fetch
  on parent mount. Pre-fetched URLs go stale across sessions and
  cause multiple simultaneous fetches.
- `verifyId` is `useState`, NOT `useRef`. The polling `useEffect`
  depends on it, and `useRef` mutations do not trigger the effect to
  re-run.
- Use a `cancelled` flag in the `useEffect` cleanup for in-flight
  request cancellation. Do not add a `fetchingRef` guard — it blocks
  re-fetch on modal close-then-reopen.
- The create-verification call is server-side. The browser must
  never see the API key.

### 5. Detect completion — three strategies in parallel

Modal iframe completion can be detected via `postMessage`, but this is
a **hint**, not authoritative. Always back it with a server poll.

When the experience is in a new tab (fallback when iframes are blocked,
for example some enterprise setups), use all three:

1. **Server poll** of `GET /age-verification/get-status?id=<id>` every
   3–5 seconds.
2. **BroadcastChannel** from the k-ID return page back to the app.
   The return page sends a message; the app listens at the top
   level (same place as the polling loop).
3. **Visibility wake** — poll immediately on `visibilitychange` and
   `focus` when the user returns to the app tab.

`get-status` uses query param `id`, NOT `verificationId`. The
wrong param is rejected with 400 and an empty body.

### 6. Post-verify — act on the result, race-free

On completion the handler is always idempotent and closes the modal
before acting on the result:

```ts
const handleSuccess = useCallback(async () => {
  if (resolvedRef.current) return;
  resolvedRef.current = true;
  setModalOpen(false);
  await onVerified();
}, [onVerified]);
```

What `onVerified` does depends on the pattern.

- **Pattern 1 — Standalone AgeKit+.** `onVerified` reads the result
  (PASS / FAIL) from `/age-verification/get-status?id=<id>` or from
  the webhook payload your backend received, and either grants
  access or shows the failure state. There is no session to refresh.
- **Patterns 2 and 3 — Sessioned.** `onVerified` calls
  `GET /session/get` once and adopts the updated session in a single
  step. Do **not** split this into two calls (for example a local
  "clear unverified flag" followed by a network "refresh session") —
  they race and the stale state wins a meaningful fraction of the
  time.

## Gotchas

- **`sessionId` is optional, not required.** Include it in Patterns
  2 and 3 where a k-ID session exists; omit it in Pattern 1
  (standalone AgeKit+). Many integrators assume it's required
  because the sessioned examples always show it — forcing a session
  into a standalone flow adds complexity for nothing.
- **Body for `perform-access-age-verification` is nested.** All
  age inputs go under `criteria` (`criteria.ageCategory`,
  `criteria.minimumAge`). Top-level fields are rejected with 400
  in every pattern.
- **`verifiedAgeThreshold` permissions are never `GUARDIAN`-managed.**
  Parental consent cannot unlock a Brazil loot-box or a UK OSA 18+
  feature — only a successful age assurance can. A consent
  challenge against a threshold permission resolves `PASS` but the
  permission stays locked, so route threshold permissions through
  `/age-verification/perform-access-age-verification`.
- **Verification method selection is server-driven.** Do not hardcode
  "show facial age estimation" or "show ConnectID". The `url`
  returned by `/age-verification/perform-access-age-verification`
  already reflects the correct method for the jurisdiction and
  Compliance Studio configuration. Client code just renders the
  iframe.
- **"Highly effective age assurance" (UK OSA) is a Compliance Studio
  setting, not a client flag.** The skill never hardcodes the OSA
  standard. The verification URL is generated to meet it when the
  jurisdiction is `GB` and the permission requires it. Do not filter
  methods client-side.
- **`/age-verification/get-status` query param is `id`**, not
  `verificationId`. Wrong param returns 400 with an empty body.
- **`window.open` / `target="_blank"` breaks iOS Safari.** Always
  prefer an iframe modal. Treat new-tab as an enterprise fallback,
  not the default. If you must use a browser-based flow (no iframe
  available), set `options.redirectUrl` so k-ID redirects back with
  `verificationId` and `result` query params.
- **`verifyId` MUST be `useState`, not `useRef`.** Polling
  `useEffect` lists it in its dependency array; refs do not cause
  effects to re-run.
- **Do not guard the URL fetch with `fetchingRef`.** It blocks
  legitimate re-fetches when the modal closes and reopens. Use a
  `cancelled` flag in cleanup instead.
- **`postMessage` is a hint, not authoritative.** Always back with a
  server poll against `/age-verification/get-status` or a webhook.
- **Six known new-tab detection failures**, each seen in real
  integrations: popup blocked; tab backgrounded; BroadcastChannel
  unsupported; `window.open` returned `null`; the return page
  doesn't load before close; the user closes the tab before the
  webhook fires. The three-strategy approach in step 5 covers all
  six.
- **One post-verify path, not two.** Whether you're refreshing a
  session or acting on a standalone result, run exactly one handler
  after the idempotency guard fires — never two that could race.
- **`resolvedRef.current` idempotency guard.** The three detection
  strategies can all fire at once. Without the guard, you attempt
  the post-verify step twice and end up with an inconsistent UI.
- **Close the modal BEFORE acting on the result.** Acting first can
  cause the UI to redraw with stale state momentarily.
- **Don't pre-generate verifications.** Create the verification only
  when the user takes the action that starts the flow — never on
  page load or modal mount-and-hide. Pre-generation wastes
  verification counts and breaks k-ID's usage metrics. See
  [best practices](https://docs.k-id.com/agekit-plus/best-practices#when-to-create-verifications).
- **Verification URLs expire after 2 weeks.** If a user abandons and
  returns later, check status first; if the URL is expired, create a
  new one rather than reusing the stale link.
- **Zero padding around the iframe.** The k-ID widget owns the
  visual space. Padding breaks layout and looks off.
- **`shortUrl` is opaque.** Display it as returned. Don't rebuild
  the URL, don't re-shorten, don't decode assumed query params.

## Defaults

- Modal: 480px wide, `min(720px, calc(100vh - 48px))` tall, 16px radius.
- Toolbar: thin (32–40px), title + literal `x` close button.
- Iframe: `flex: 1`, `border: none`, no background.
- Poll interval: 3–5 seconds while the modal is open.
- Wake triggers: `visibilitychange`, `focus`.
- Retry on transient `/get-status` failures: 2 retries, 2s apart.

## Validation step

Confirm end-to-end on real devices.

### Pattern 1 — Standalone AgeKit+

1. Calling `/age-verification/perform-access-age-verification` with
   the target `jurisdiction` and `criteria` (no `sessionId`) returns
   `id`, `url`, `shortUrl`.
2. Loading `url` in an iframe lets the user complete verification
   end-to-end.
3. After completion, either the webhook your backend registered
   fires, or `GET /age-verification/get-status?id=<id>` returns the
   final `PASS` or `FAIL`, and the product acts on it correctly.
4. The API key is never visible in browser network traffic.

### Patterns 2 and 3 — Sessioned

1. Complete verification via iframe modal — the gated feature
   unlocks within 10 seconds of the k-ID widget confirming success.
2. Force the new-tab fallback (iframe blocked by CSP in a test
   environment) — feature still unlocks via poll or BroadcastChannel.
3. Backgrounding the app tab during verification and returning —
   the feature unlocks immediately on focus (visibility wake fires).
4. `GET /session/get` after verification returns the same
   `sessionId` with `ageVerificationStatus: "verified"` and the full
   permissions set.
5. Hitting the verify banner twice rapidly — exactly one modal opens
   (idempotency guard works).

## Next steps

- Rendering permissions after `ageVerificationStatus` flips to `verified` → [`k-id-sessions-and-permissions`](../k-id-sessions-and-permissions/SKILL.md).
- Webhook-driven session refresh (preferred in production) → [`k-id-webhooks`](../k-id-webhooks/SKILL.md).
- Mobile native verification entry points → [`k-id-mobile-native`](../k-id-mobile-native/SKILL.md).
- Server wiring for verification endpoints → [`k-id-server-trust-boundary`](../k-id-server-trust-boundary/SKILL.md).

Canonical references:
- [Age assurance concept](https://docs.k-id.com/concepts/age-assurance)
- [Verification methods](https://docs.k-id.com/concepts/verification-methods)
- [`POST /age-verification/perform-access-age-verification`](https://docs.k-id.com/api/endpoints/perform-access-age-verification)
- [`GET /age-verification/get-status`](https://docs.k-id.com/api/endpoints/get-age-verification-status)
- [Age verification quickstart](https://docs.k-id.com/get-started/quickstart-guides/age-verification)
- [`verification.result` webhook](https://docs.k-id.com/events/webhooks/event-types/verification-result)
- [`verification.revoke` webhook](https://docs.k-id.com/events/webhooks/overview)
