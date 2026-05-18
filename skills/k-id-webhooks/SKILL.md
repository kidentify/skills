---
name: k-id-webhooks
description: >
  Implements a k-ID webhook receiver — HMAC-SHA256 signature verification against the RAW request body (not the parsed JSON), timestamp tolerance, idempotency keyed by event ID, and per-event handlers for Challenge.StateChange, Verification.Result, Verification.Revoke, ParentalConsent.Granted, Session.ChangePermissions, Session.Delete, and Test. Use when building or debugging a webhook endpoint for k-ID, when the test webhook returns 401, when events are received but not acted on, or when sessions drift from Family Connect changes. Not for client-side postMessage handling (see k-id-age-verification) and not for in-app polling (see k-id-consent-and-challenges or k-id-sessions-and-permissions).
license: Apache-2.0
metadata:
  version: "1.0.0"
  vendor: k-ID
---

# k-ID Webhooks

Webhooks are how k-ID pushes state changes to your backend: a parent
granting consent on another device, a verification result landing,
permissions changing from Family Connect, a session deleted. If your
webhook endpoint is wrong, sessions drift from reality and features
don't reflect what parents actually approved. This skill covers the
receiver end-to-end.

## When to use

Use this skill when the user is:

- Building a new webhook endpoint for k-ID events.
- Debugging signature verification (`401` responses or the Test event
  looking correct but rejected).
- Adding a new event handler or fixing event fan-out.
- Making the receiver idempotent.
- Propagating webhook state into your app's session store.

## Core steps

### 1. Configure the receiver URL and secret in Compliance Studio

k-ID pushes events to the URL you configure per product in Compliance
Studio under Developer Settings. The webhook secret is generated there
and is **not** the same as your API key. Store it server-side only.

Reference: [`docs.k-id.com/events/webhooks/overview`](https://docs.k-id.com/events/webhooks/overview).

### 2. Verify the signature against the RAW body

Two headers arrive on every request:

- `X-Signature-Timestamp` — UNIX epoch seconds.
- `X-Signature-Hmac-Sha256` — HMAC-SHA256 of
  `timestamp + rawBody`, lowercase hex.

Example (Node.js, Next.js App Router route handler):

```ts
import crypto from 'node:crypto';

export async function POST(req: Request) {
  const ts = req.headers.get('x-signature-timestamp') ?? '';
  const sig = req.headers.get('x-signature-hmac-sha256') ?? '';

  const raw = await req.text();            // RAW body, not req.json()
  const expected = crypto
    .createHmac('sha256', process.env.KID_WEBHOOK_SECRET!)
    .update(ts + raw)
    .digest('hex');

  const ok =
    sig.length === expected.length &&
    crypto.timingSafeEqual(Buffer.from(sig), Buffer.from(expected));

  if (!ok) return new Response('invalid signature', { status: 401 });

  // Timestamp freshness: reject anything older than 5 minutes
  if (Math.abs(Date.now() / 1000 - Number(ts)) > 300) {
    return new Response('stale', { status: 401 });
  }

  const event = JSON.parse(raw);
  await handleEvent(event);
  return new Response('ok', { status: 200 });
}
```

The raw body matters because JSON serialization is not canonical —
`req.json()` followed by `JSON.stringify()` will produce a different
byte sequence (different key order, missing whitespace) and the
signature will not match.

### 3. Idempotency keyed by event ID

k-ID may retry a webhook. Cache event IDs for at least 24 hours.
On a duplicate, return `200` without re-processing.

- Redis with `SETNX` + 86400 TTL is the canonical approach.
- In-memory works for a single instance but loses across restarts —
  adequate for dev, dangerous in production.
- The plan's "persistent webhook cache" env var
  (`KID_WEBHOOK_CACHE_URL`) exists for exactly this.

### 4. Event handlers

Each event type has a distinct effect. Keep handlers thin — update
your session store and move on. Don't do synchronous work that blocks
the 200 response.

| Event | Typical action |
|---|---|
| `Test` | Return 200. No state change. |
| `Challenge.StateChange` | Update stored challenge status; if `PASS`, trigger session rematerialization. |
| `ParentalConsent.Granted` | Refresh affected session (`GET /session/get`). |
| `Verification.Result` | Mark the session as verified and restore full permissions. |
| `Verification.Revoke` | Return the session to the unverified-adult state; clear verified age. |
| `Session.ChangePermissions` | Refresh the session; push down to connected clients. |
| `Session.Delete` | Delete the session from your store; force re-authentication. |
| `AgeAssurance.Result` | Deprecated. Map to `Verification.Result` if you still receive it. |

### 5. Push state into the app

Webhooks live on the backend. Clients must learn about changes
somehow. Two patterns, pick one based on your architecture:

- **Poll-on-focus (default, simplest).** Client polls `/session/get`
  at the top level of the signed-in app on 30s + focus. Webhooks
  update your store; next poll reads the fresh state. Works
  everywhere. See `k-id-sessions-and-permissions`.
- **Server push (WebSocket / SSE).** Broadcast a "session invalidated"
  message on webhook receipt so clients refresh immediately. More
  complex; reserve for apps that already have server push.

### 6. Always return 200 fast

k-ID retries on any non-2xx response. Heavy work (session
re-materialization, fan-out to clients, logging) should happen
asynchronously after `return new Response('ok')`. A slow handler
gets retried and amplifies load.

## Gotchas

- **Verify against RAW body, not parsed-and-re-stringified JSON.**
  Parsing reorders keys and strips whitespace. Signature won't match.
- **`X-Signature-Hmac-Sha256` is lowercase hex.** Comparing uppercase
  hex mismatches. Use `timingSafeEqual` on the decoded bytes or
  normalize to lowercase before comparing strings.
- **Timestamp freshness check (≤5 minutes).** Without it, replayed
  requests with the correct signature succeed.
- **Idempotency by event ID is non-optional.** k-ID retries. Without
  idempotency, the same session change is processed 2–3 times, and
  for delete events you end up deleting a re-created session.
- **Do NOT parse the body with `req.json()` before verifying.** Most
  frameworks consume the body once — parse after verification.
- **Webhook secret is not the API key.** Different value, different
  scope. Don't use the API key for HMAC — it will never match.
- **Return 200 fast.** Heavy work goes async. k-ID retries slow
  handlers and you'll see amplified load for no gain.
- **Test event is the diagnostic.** If Test returns 401, your secret
  or HMAC construction is wrong. Real events will never arrive until
  Test returns 200.
- **`AgeAssurance.Result` is deprecated**; map it to `Verification.Result`
  behavior if you still receive it.
- **Session.Delete is terminal.** Don't try to refresh the session
  after this event — it won't exist. Clear state and treat the user
  as un-sessioned.
- **Serverless cold starts invalidate in-memory caches.** In a
  serverless environment, use Redis or an equivalent persistent cache
  for idempotency. Dev with in-memory is fine; production with
  in-memory is a race bomb.

## Defaults

- Signature: HMAC-SHA256 over `timestamp + rawBody`, lowercase hex,
  compared via `timingSafeEqual`.
- Timestamp skew tolerance: 5 minutes.
- Idempotency cache TTL: 24 hours.
- Invalid signature response: `401 Unauthorized`.
- Unknown event type: log and return `200` (don't 4xx — forward
  compatibility).
- Handler runtime target: <100 ms for the synchronous path.

## Validation step

1. Send a `Test` event from Compliance Studio → endpoint returns 200.
2. Tamper with the signature → endpoint returns 401.
3. Replay the same event twice within a minute → second call returns
   200 without re-processing (check logs).
4. Send a `Verification.Result` for a known unverified-adult session →
   within 30 seconds the client app reflects
   `ageVerificationStatus: verified`.
5. Delete a test session → `Session.Delete` arrives, stored session is
   gone, next `/session/get` returns 404.

## Next steps

- Propagating changes to the client → [`k-id-sessions-and-permissions`](../k-id-sessions-and-permissions/SKILL.md).
- Handling the unverified-adult verification UX → [`k-id-age-verification`](../k-id-age-verification/SKILL.md).
- Consent approvals → [`k-id-consent-and-challenges`](../k-id-consent-and-challenges/SKILL.md).
- Server architecture → [`k-id-server-trust-boundary`](../k-id-server-trust-boundary/SKILL.md).

Canonical references:
- [Webhooks overview](https://docs.k-id.com/events/webhooks/overview)
- [`Challenge.StateChange`](https://docs.k-id.com/events/webhooks/event-types/challenge-statechange)
- [`Verification.Result`](https://docs.k-id.com/events/webhooks/event-types/verification-result)
- [`Verification.Revoke`](https://docs.k-id.com/events/webhooks/overview)
- [`ParentalConsent.Granted`](https://docs.k-id.com/events/webhooks/event-types/parentalconsent-granted)
- [`Session.ChangePermissions`](https://docs.k-id.com/events/webhooks/event-types/session-changepermissions)
- [`Session.Delete`](https://docs.k-id.com/events/webhooks/event-types/session-delete)
- [`Test`](https://docs.k-id.com/events/webhooks/event-types/test)
