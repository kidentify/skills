---
name: k-id-server-trust-boundary
description: >
  Companion skill for every k-ID integration — establishes the server as the only place the API key lives, sets up a server-side proxy for all client-bound k-ID calls, enforces `session.permissions[name].enabled === true` on privileged route handlers, and runs pre-flight connectivity checks so test-vs-prod key and URL mismatches are caught before anything else is wired up. Use at the start of any k-ID integration, whenever the user asks where to put the API key, or when diagnosing 401/400 responses that appear to come from client code but are actually environment mismatches. Not a feature skill on its own — pair with k-id-age-gate, k-id-consent-and-challenges, k-id-age-verification, k-id-sessions-and-permissions, or k-id-webhooks.
license: Apache-2.0
metadata:
  version: "1.0.0"
  vendor: k-ID
---

# k-ID Server Trust Boundary

Every k-ID integration has exactly one trust boundary: the API key and
webhook secret live on your server and never reach the browser or a
mobile binary. Everything else — the age gate, the consent screen,
the verification modal — flows through a server proxy that attaches
the key and enforces permissions on privileged routes. Getting this
wrong creates compliance bypass paths and leaks API credentials.

## When to use

Use this skill when the user is:

- Starting a new k-ID integration (always load this first).
- Placing the API key, webhook secret, or base URL in env.
- Building the server proxy through which the browser reaches k-ID.
- Diagnosing 401/400 responses that appear to come from client code
  but are actually test-vs-prod env mismatches.
- Adding `session.permissions` enforcement to a privileged route.
- Writing the pre-flight checklist before first deploy.

Pair this skill with whichever feature skill the user is working on.

## Core steps

### 1. Environment variables — server-only

Required env vars:

```bash
KID_API_KEY=<from Compliance Studio, per-product, server-only>
KID_API_BASE_URL=https://game-api.k-id.com       # prod
# or:
KID_API_BASE_URL=https://game-api.test.k-id.com  # test
KID_WEBHOOK_SECRET=<from Compliance Studio, per-product>
```

Optional but recommended for serverless:

```bash
KID_WEBHOOK_CACHE_URL=redis://...   # idempotency cache for webhooks
```

Rules:

- Never prefix with `NEXT_PUBLIC_`, `VITE_`, `EXPO_PUBLIC_`, etc.
  Anything that reaches the client is a credential leak.
- `.env.local` for dev; production values through your deployment
  platform's secret store.
- **Test and production keys are NOT interchangeable.** A test key
  against prod URL returns 401 with no body. A prod key against test
  URL does too.

Reference:
[`docs.k-id.com/api/authentication`](https://docs.k-id.com/api/authentication).

### 2. Single server proxy for all k-ID traffic

The client never calls `game-api.k-id.com` directly. Instead, one
route on your server (e.g. `/api/kid/[...path]`) receives client
requests and forwards them to k-ID with the API key attached.

Why one proxy instead of one route per endpoint:

- Adding a new k-ID endpoint to your app requires no new server code.
- API key lives in exactly one place.
- Logging, rate-limiting, and error normalization are centralized.

Minimal Next.js App Router example:

```ts
// src/app/api/kid/[...path]/route.ts
export async function POST(
  req: Request,
  { params }: { params: { path: string[] } }
) {
  const path = params.path.join('/');
  const body = await req.text();
  const res = await fetch(`${process.env.KID_API_BASE_URL}/${path}`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.KID_API_KEY!}`,
      'Content-Type': 'application/json',
    },
    body,
  });
  const text = await res.text();
  return new Response(text, {
    status: res.status,
    headers: { 'Content-Type': 'application/json' },
  });
}
```

Restrict which paths are proxiable in production (allowlist). A wide-open
proxy is an abuse vector.

### 3. Pre-flight checklist — run BEFORE shipping

Five checks that catch 90% of "nothing works" tickets:

```bash
# 1. Echo loaded env
node -e "console.log({ key: !!process.env.KID_API_KEY, url: process.env.KID_API_BASE_URL })"

# 2. Smoke-test the key + URL combo directly against k-ID
curl -s -o /dev/null -w "%{http_code}\n" \
  -H "Authorization: Bearer $KID_API_KEY" \
  "$KID_API_BASE_URL/session/get?sessionId=invalid-for-smoke-test"
# 200, 400, or 404 means the key + URL pair is fine; look elsewhere.
# 401 means the key + URL pair is mismatched — fix before continuing.

# 3. Confirm webhook secret with a Test event from Compliance Studio.
# 4. Run permission discovery against a fresh session and diff the slugs
#    your code references.
# 5. Confirm onBrokenLinks/onBrokenAnchors or equivalent link-checking
#    passes if you copied docs URLs into your app copy.
```

Reference: [`docs.k-id.com/concepts/testing`](https://docs.k-id.com/concepts/testing).

### 4. Enforce `session.permissions` on privileged routes

Client-side gated controls are UX; real enforcement lives on the
server. Every route handler that does something privileged:

```ts
export async function POST(req: Request) {
  const { sessionId } = await req.json();
  const session = await fetchKidSession(sessionId);     // via proxy
  if (!session) return new Response('unauthenticated', { status: 401 });

  const required = 'multiplayer_voice_chat';
  const allowed = session.permissions
    .find(p => p.name === required)?.enabled === true;

  if (!allowed) return new Response('forbidden', { status: 403 });

  // ... privileged work ...
}
```

Missing permission means `false`. Do not default to `true` because
the slug wasn't in the array — that's a silent bypass.

### 5. Normalize URL construction — forward slashes only

When building URLs dynamically, always join with forward slashes and
avoid implicit normalizers that strip query strings. Never use `\` —
on Windows CI this sometimes slips in and the resulting URL is valid
per RFC but k-ID rejects it. URLs are not filesystem paths.

### 6. Cache and invalidate session reads wisely

`/session/get` can be called on every request, but it adds latency and
rate-limit exposure. A short (30s) server-side cache keyed by
`sessionId` is usually safe. Invalidate on:

- Any webhook event for that session.
- Any `/session/upgrade` or verification success for that session.
- 401 responses (treat as session invalidation).

## Gotchas

- **API key in client-visible env = compliance bypass.** Leaked keys
  let anyone mint sessions for your product. Server-only, always.
- **Test vs prod key/URL mismatch.** 401 with no error body. Always
  suspect this first when a working integration breaks.
- **Single proxy is an allowlist, not a wildcard.** Expose only the
  endpoints your app actually uses in production.
- **`session.permissions.find(...)?.enabled === true` — missing is
  false.** Never default-allow for slugs not in the array.
- **Webhook secret ≠ API key.** Different values, different purposes.
- **Don't log the API key.** Even redacted "Authorization: Bearer
  sk-..." fragments can leak through error reports and support tickets.
- **Serverless cold starts can invalidate in-memory session caches.**
  Use Redis or similar for any cross-instance cache.
- **URL construction with backslashes** (`\`) is a Windows CI trap.
  Always forward slashes.
- **Don't retry 401 automatically.** A 401 usually means config, not a
  transient error. Retrying masks the real problem.
- **Rate limits are per-key.** Test and prod keys have different
  limits; hitting prod rate-limits from a load test with the prod key
  will affect real users.

## Defaults

- Base URL: `https://game-api.k-id.com` (prod),
  `https://game-api.test.k-id.com` (test).
- Bearer auth header: `Authorization: Bearer ${KID_API_KEY}`.
- Proxy pattern: one Next.js (or equivalent) route handling
  `/api/kid/<path>` for allowlisted paths.
- Session cache: 30s, invalidated on webhook or upgrade.
- 401 behavior: no retry, log env/key status, surface clear error.

## Validation step

Before declaring the integration ready:

1. Searching your client bundle for `KID_API_KEY` returns no matches.
2. Pre-flight curl against `{KID_API_BASE_URL}/session/get` with a
   smoke sessionId returns 200, 400, or 404 — never 401.
3. A privileged route handler rejects requests for sessions lacking the
   required permission with 403 (tested manually or with an integration
   test).
4. Compliance Studio's Test webhook succeeds end-to-end on production.
5. `/session/get` calls go through the server proxy, never directly
   from the client.

## Next steps

Pair with the feature skill for the task at hand:

- [`k-id-age-gate`](../k-id-age-gate/SKILL.md)
- [`k-id-consent-and-challenges`](../k-id-consent-and-challenges/SKILL.md)
- [`k-id-age-verification`](../k-id-age-verification/SKILL.md)
- [`k-id-sessions-and-permissions`](../k-id-sessions-and-permissions/SKILL.md)
- [`k-id-webhooks`](../k-id-webhooks/SKILL.md)

Canonical references:
- [Authentication](https://docs.k-id.com/api/authentication)
- [Error handling](https://docs.k-id.com/api/error-handling)
- [Testing](https://docs.k-id.com/concepts/testing)
- [API overview](https://docs.k-id.com/api/overview)
