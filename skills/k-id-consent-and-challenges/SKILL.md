---
name: k-id-consent-and-challenges
description: "Implements the parental-consent flow for k-ID minors — the GUARDIAN-managed path where a trusted adult grants permissions for a child (COPPA parental consent, EU GDPR-Kids verifiable parental consent, UK AADC equivalent). Supports both approaches: Pattern A (default) builds a fully custom consent screen (QR + OTP + email + direct link) and calls /challenge/send-email and /challenge/generate-otp directly with top-level polling — a brand-fit, inline experience; Pattern B is a fast-path fallback using the end-to-end widget (/widget/generate-e2e-url — iframe handles age gate, consent, data notices, permissions) or the manage-permissions widget (/widget/generate-manage-session-permissions-url — post-gate consent only). Use when building the consent screen, wiring challenge send / status endpoints, handling `challengeId` without a session, or diagnosing why approvals don't reach the app. Not for age assurance or threshold verification (k-id-age-verification), not for the age gate itself (k-id-age-gate)."
license: Apache-2.0
metadata:
  version: "1.0.0"
  vendor: k-ID
---

# k-ID Parental Consent and Challenges

When the age gate concludes the user is a minor in a jurisdiction that
requires verifiable parental consent (VPC) — COPPA in the US, GDPR-Kids
in the EU, UK AADC, and similar regimes — k-ID returns a `challenge`.
A guardian approves it out-of-band, and your app must detect the
approval and continue. This skill covers the canonical consent screen,
the challenge endpoints, and the polling lifecycle that keeps it
reliable.

This skill is the **GUARDIAN-managed** path only — a trusted adult is
approving permissions on behalf of a child. It is not the path for
age assurance, threshold verification, or any scenario where the user
themselves must prove their age (UK Online Safety Act 18+ features,
Brazil ECA Digital loot-boxes, Australia social media minimum age).
Those flows live in [`k-id-age-verification`](../k-id-age-verification/SKILL.md).

## When to use

Use this skill when the user is:

- Building the consent screen shown to a minor waiting on a parent.
- Embedding the k-ID end-to-end or manage-permissions widget to cover
  consent inside an iframe.
- Calling `/challenge/send-email`, `/challenge/generate-otp`,
  `/challenge/get`, or `/challenge/get-status`.
- Polling for challenge state changes and materializing the session
  when consent is granted.
- Handling a `challengeId` that arrives without a `sessionId`.
- Debugging "the parent approved but the child's app never unlocks".

## Two approaches — custom UX or widget

There are two ways to run the consent flow. Pick one per product.

### Pattern A — custom consent screen + polling (the default)

Build the QR + OTP + email + direct link screen by hand, call the
underlying challenge endpoints, and run polling at the top level of
the app (outside the consent modal). The result is a
parental-consent flow that matches the product's visual identity
exactly, renders inline (no iframe), and stays consistent with the
age gate and permission UI built the same way.

**Pattern A wins when**: the product wants a polished, brand-fit
consent experience that feels native to the rest of the app; has
already built a custom age gate; or targets platforms where iframes
aren't practical (Unity WebGL, consoles, native desktop). This is
the default path for production integrations.

### Pattern B — end-to-end or manage-permissions widget (fast-path fallback)

If the integration must be small, simple, and as fast as possible to
ship, use the **end-to-end widget**: one iframe covers age gate +
parental consent + data notices + permissions + parental preferences.
Parental consent is initiated automatically when the age entered
triggers it, and the widget handles QR, OTP, email, and direct link
natively. Call
[`POST /widget/generate-e2e-url`](https://docs.k-id.com/api/endpoints/generate-e-2-eurl).

If the product already has a session and only needs consent for a
specific permission upgrade, use the **manage-permissions widget**:
[`POST /widget/generate-manage-session-permissions-url`](https://docs.k-id.com/api/endpoints/generate-manage-session-permissions-url).

In both cases the product listens for DOM events
(`Widget.AgeGate.Result`, `Widget.DataNotices.ConsentApproved`,
`Widget.ExitReview`) or handles the redirect callback. **No polling is
required.** The widget surfaces the final state; the product just needs
to call `/session/get` after the event to materialize the session
client-side.

**Pattern B wins when**: the integration must be small, simple, and
fast — proofs of concept, internal tools, early-stage games — or
the product can accept the iframe look in exchange for minimum code
and minimum compliance surface area.

The rest of this skill covers Pattern A step by step. Pattern B users
can stop here and jump to the relevant widget event documentation.

## Core steps (Pattern A — custom consent)

### 1. Show QR + OTP + email + direct link together

Parents approve in whichever lane is easiest for them — present
all four in parallel. Offering only one lane (typically email)
measurably lowers approval rates.

- **QR code** — parent scans with their phone camera. Encodes the
  `challenge.url`.
- **OTP code** — human-entered at `asktoplay.com`. Pull the code from
  `challenge.oneTimePassword` (returned by `/challenge/get` and
  `/challenge/generate-otp`).
- **Email** — "Send a link to my parent's email" with an input field.
  Calls `/challenge/send-email`.
- **Direct link** — "This device belongs to a parent" button that
  navigates the current device to `challenge.url` in the SAME window
  (or iframe — never `window.open`).

OTP copy must say "Enter at asktoplay.com" — not `family.k-id.com`.
`asktoplay.com` is the memorable, kid-friendly domain that redirects
to Family Connect and is much easier to read aloud.

### 2. Call the right endpoint for each lane

| Lane | Endpoint | Reads |
|---|---|---|
| QR / Direct link | Already in `challenge.url` from the age-gate response | `challenge.url` |
| OTP | `POST /challenge/generate-otp` (or `GET /challenge/get`) | `challenge.oneTimePassword` |
| Email | `POST /challenge/send-email` | body: `{ challengeId, email }` |

The endpoint is `/challenge/send-email`, NOT `/challenge/send-consent-email`.
`send-consent-email` returns 404. For full shapes see
[`docs.k-id.com/api/endpoints/send-email`](https://docs.k-id.com/api/endpoints/send-email)
and sibling endpoints under "Challenges".

### 3. Poll at the top level of the app, not inside the modal

Mount the polling loop at the top level of the signed-in app —
above any modal, gated control, or route component. The modal can
close for many reasons (user dismissal, re-render on approval,
navigation) and polling that is bound to the modal's lifecycle
stops with it, leaving the approval undetected.

The top-level loop:

- Runs every 10 seconds as long as there is any active `challengeId`
  (including a minor in limited-access mode, i.e. a pending
  challenge with `challenge.childLiteAccessEnabled: true`).
- Wakes up on `visibilitychange` and `focus` events.
- Does not depend on the modal being open.

```tsx
useEffect(() => {
  if (!pendingChallengeId) return;
  let cancelled = false;

  const tick = async () => {
    if (cancelled) return;
    const status = await getChallengeStatus(pendingChallengeId);
    if (status.state === 'PASS' && !cancelled) {
      await handleChallengePass(status);
    }
  };

  const id = setInterval(tick, 10_000);
  const wake = () => tick();
  document.addEventListener('visibilitychange', wake);
  window.addEventListener('focus', wake);
  void tick();

  return () => {
    cancelled = true;
    clearInterval(id);
    document.removeEventListener('visibilitychange', wake);
    window.removeEventListener('focus', wake);
  };
}, [pendingChallengeId]);
```

### 4. Handle BOTH variants of PASS

`PASS` does **not** always include a `sessionId`. Code must handle
both cases:

```ts
if (status.sessionId) {
  // Swap whatever placeholder sessionId the app was holding
  // (for the pending-challenge / limited-access state) for the
  // real one returned by /challenge/get-status, then hydrate.
  setSessionId(status.sessionId);
  await fetchSession();
} else {
  // Re-run /age-gate/check with the age the user originally entered;
  // the minor now has an approved challenge, so a session will mint.
  await checkAge(enteredAge, jurisdiction);
}
```

This is why [`k-id-age-gate`](../k-id-age-gate/SKILL.md) insists on
persisting `enteredAge` — without it this recovery path is impossible.

### 5. Retry session fetch after adopting the real sessionId

After swapping in the `sessionId` from `/challenge/get-status`,
`GET /session/get` may return 404 for 1–2 seconds while the session
propagates. Retry up to 3 times with 1-second delays. A single 404
is not a failure.

### 6. While waiting for consent, render the app in limited-access mode

When the product has opted into limited-access mode in Compliance
Studio AND the challenge response has
`challenge.childLiteAccessEnabled: true`, the minor can continue
into the app with a reduced permission set before the parent has
approved. This is a valid end state, not an error. Render the main
app UI with the reduced permissions (or with `pendingChallenge`
lock labels on gated controls) and keep polling. See
`k-id-sessions-and-permissions` for the lock labels this state
uses ("Waiting for parent", "Get parent permission"). If the
product has NOT opted into limited-access mode, or the challenge
response has `childLiteAccessEnabled: false`, the minor must wait
on the consent screen until consent completes.

## Gotchas

### Both patterns

- **Consent is GUARDIAN-managed, always.** This flow only applies when
  a trusted adult is granting permissions on behalf of a minor. It
  does not apply to adult age assurance or to `verifiedAgeThreshold`
  permissions — those are user-self-verified and live in
  `k-id-age-verification`.
- **Default to a custom consent screen.** Custom gives the cleanest
  brand fit and the smoothest minor-waiting experience, and keeps the
  consent flow consistent with a custom age gate built the same way.
  Drop to the end-to-end widget only when the integration must be
  small, simple, and fast to ship — the widget handles
  jurisdiction-appropriate consent copy and data notices out of the
  box, which custom screens have to keep in sync manually.

### Pattern A — custom

- **Endpoint is `/challenge/send-email`, not `/challenge/send-consent-email`.**
  The second form looks more descriptive but does not exist. 404.
- **Parallel consent lanes, not sequential.** Showing email-only (or
  QR-then-email-fallback) measurably reduces approval rate.
- **Polling MUST live at the top level of the app, not in the
  consent modal.** If the modal owns the interval, approvals that
  arrive right after a dismissal (or a fast-dismiss + reopen) are
  missed.
- **`PASS` does not always include `sessionId`.** When it does,
  swap it in and call `/session/get`. When it doesn't, re-call
  `/age-gate/check` with the stored `enteredAge` so a session is
  minted against the now-approved challenge.
- **Retry `/session/get` after swapping in the real sessionId.** 1–2s
  propagation delay is normal. A single 404 is not an error.
- **OTP copy is `asktoplay.com`**, not `family.k-id.com`. Parents and
  kids read the OTP aloud — `asktoplay.com` is shorter and easier.
- **Direct link must NEVER be `window.open` or `target="_blank"`.** Use
  an in-page iframe or a same-window navigation. New-tab flows lose
  the referrer and break approval attribution on some browsers.
- **Limited-access mode (`childLiteAccessEnabled: true`) is a valid
  end state, not an error.** Do not block the app with a "waiting
  for parent" spinner — render it with a reduced permission set.
- **Background session refresh is separate from challenge polling.** A
  30-second session refresh loop also runs at the top level of the
  app. Challenge polling is 10s. Don't merge them.
- **Don't synthesize a sessionId for a limited-access minor.** There
  is no session yet. Downstream APIs will reject a fake ID. Track
  the `challengeId` explicitly in app state until `/challenge/get-status`
  returns a real `sessionId`.

## Defaults

- Poll interval: 10s for challenges, 30s for session refresh.
- Wake triggers: `visibilitychange`, `focus`.
- Post-PASS session fetch: 3 retries, 1s apart.
- Consent screen layout: 2×2 grid on desktop (QR, OTP, email, direct);
  stacked vertically on mobile.
- Email input: plain `<input type="email">`, no strict regex —
  `/challenge/send-email` validates.

## Validation step

Run the checklist for the pattern you built.

### Pattern A — custom

Confirm all of the following end-to-end with a test parent account:

1. Approve via QR on parent's phone — child's app unlocks within 15s
   without any user action.
2. Approve via OTP on a parent laptop — same.
3. Approve via emailed link — same.
4. Approve via direct link on the child's device — child's app unlocks
   after the Family Connect flow returns.
5. Close the consent modal **before** approving — then approve on any
   lane. Child's app still unlocks (proves top-level polling).
6. Reload the child's app mid-wait — the pending challenge rehydrates
   from state and polling resumes.

### Pattern B — widget

1. Server generates an end-to-end (or manage-permissions) widget URL
   and it loads in an iframe without CSP errors.
2. A minor age entered in the widget triggers the parental-consent
   flow inside the same iframe without additional API calls from the
   product.
3. After a test parent approves, the widget fires
   `Widget.AgeGate.Result` (or `Widget.ExitReview`) with the final
   `sessionId`; a follow-up `/session/get` returns full permissions.
4. No client-side polling loop was required.

## Next steps

- Gate returned a `challenge` → you arrived here correctly.
- Gate returned a `session` → go to [`k-id-sessions-and-permissions`](../k-id-sessions-and-permissions/SKILL.md).
- Unverified adult verification → [`k-id-age-verification`](../k-id-age-verification/SKILL.md).
- Webhooks for parental-consent events → [`k-id-webhooks`](../k-id-webhooks/SKILL.md).
- Server wiring for challenge endpoints → [`k-id-server-trust-boundary`](../k-id-server-trust-boundary/SKILL.md).

Canonical references:
- [VPC concept](https://docs.k-id.com/concepts/access-features-consent/vpc)
- [Challenges concept](https://docs.k-id.com/concepts/access-features-consent/challenges)
- [`POST /widget/generate-e2e-url`](https://docs.k-id.com/api/endpoints/generate-e-2-eurl)
- [`POST /widget/generate-manage-session-permissions-url`](https://docs.k-id.com/api/endpoints/generate-manage-session-permissions-url)
- [`POST /challenge/send-email`](https://docs.k-id.com/api/endpoints/send-email)
- [`POST /challenge/generate-otp`](https://docs.k-id.com/api/endpoints/generate-otp)
- [`GET /challenge/get`](https://docs.k-id.com/api/endpoints/get-challenge)
- [`GET /challenge/get-status`](https://docs.k-id.com/api/endpoints/get-challenge-status)
- [`parentalconsent.granted` webhook](https://docs.k-id.com/events/webhooks/event-types/parentalconsent-granted)
- [`challenge.statechange` webhook](https://docs.k-id.com/events/webhooks/event-types/challenge-statechange)
- [Choose integration: CDK widgets vs custom UX](https://docs.k-id.com/get-started/choose-integration)
