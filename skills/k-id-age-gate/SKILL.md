---
name: k-id-age-gate
description: "Implements the k-ID age gate — entry point for any full sessioned k-ID integration (Shape A), covering every regime (COPPA, GDPR-Kids, UK AADC, UK OSA, Brazil ECA Digital, Australia Online Safety). Two approaches: Pattern A (default) builds a fully custom UI and calls /age-gate/check directly — best-looking, most brand-integrated, works on every platform (web, Unity WebGL, consoles, native); Pattern B is a fast-path fallback using the k-ID widget (/widget/generate-age-gate-url or /widget/generate-e2e-url — iframe handles age collection and auto-initiates consent). Covers null-initial age state, platform signals first, IP-based jurisdiction with timezone fallback, and /age-gate/check response shapes (session, challenge, unverified-adult). Use when adding or debugging the gate. Use EVEN IF the user says COPPA, OSA, ECA, or \"age verification\" but means the initial claimed-age check. Not for AgeKit+ (k-id-age-verification P1), post-gate / threshold verification (P2–3), or consent (k-id-consent-and-challenges)."
license: Apache-2.0
metadata:
  version: "1.0.0"
  vendor: k-ID
---

# k-ID Age Gate

The age gate is the entry point to every **sessioned** k-ID
integration (Shape A in the router). It turns an unidentified
visitor into either a session (adult or minor), a pending challenge
(unverified minor who needs parental consent), or an
unverified-adult session (user claims adult but must still pass age
assurance) by calling `/age-gate/check`. Get this wrong and a
sessioned product is non-compliant — before any other feature work
matters.

It works across every jurisdiction k-ID supports: COPPA (US),
GDPR-Kids (EU), UK AADC, UK Online Safety Act, Brazil ECA Digital,
Australia Online Safety, and more. Jurisdictional behaviour comes
from Compliance Studio, not from branching in client code.

### Skip this skill if

You're doing **standalone AgeKit+** (router Shape B) — the product
only needs to prove a user's age once for one decision, with no
persistent session and no permission-management UI. In that case
go straight
to [`k-id-age-verification`](../k-id-age-verification/SKILL.md)
(Pattern 1). No age gate, no `/age-gate/check`, no session.

18+ products where the only compliance requirement is a
single age proof fall into this category. 18+ products that
have persistent users, accounts, permissions, or ongoing
interactions still use the age gate as their entry point.

## When to use

Use this skill when the user is:

- Building or fixing the age gate UI and its submit action.
- Embedding the k-ID age-gate widget in a web app, mobile webview, or
  Unity.
- Calling `/age-gate/check` or deciding what to send in the body.
- Resolving platform age signals (iOS, Android, Unity, store age ranges)
  before showing an age gate.
- Detecting jurisdiction for the age gate (IP + timezone).
- Handling the response — `session`, `challenge`, or an unverified-adult
  session.

For the screen that appears **after** the gate when the user is a minor
needing consent, load `k-id-consent-and-challenges`.
For the screen that appears after an adult is returned unverified
(`ageCategory: "adult"`, `ageVerificationStatus: "unverified"`), load
`k-id-age-verification`.

## Two approaches — custom UX or widget

There are two ways to implement the age gate. Pick one per flow.

### Pattern A — custom age-gate UI (the default)

Build the UI by hand and call
[`POST /age-gate/check`](https://docs.k-id.com/api/endpoints/check-age-gate)
from the server with the collected `dateOfBirth` (or `age`) and
`jurisdiction`. The product owns the slider, labels, copy, and the
branching on the response. The result is a native inline experience
that matches the rest of the product's look, feel, and motion.

**Pattern A wins when**: the product wants the best-looking, most
brand-integrated entry screen, needs non-iframe rendering (Unity
WebGL, consoles, native desktop apps without webviews), or has a
studio-level visual-design bar to meet. This is the default path for
production integrations.

### Pattern B — k-ID age-gate widget (fast-path fallback)

Call [`POST /widget/generate-age-gate-url`](https://docs.k-id.com/api/endpoints/generate-age-gate-url)
from the server, embed the returned URL in an iframe (or open it with
a `redirectUrl`), and listen for the `Widget.AgeGate.Result` and
`Widget.AgeGate.Challenge` DOM events. The widget handles:

- Jurisdiction-appropriate age collection (date picker, slider, or
  platform-account depending on `approvedAgeCollectionMethods` for the
  user's jurisdiction).
- Automatic challenge initiation when the submitted age requires
  parental consent — no extra call from the product.
- Correct regulatory copy per region and language.
- The underlying `/age-gate/check` invocation.

The product's job shrinks to: generate the URL, embed the iframe,
handle the result event. No custom slider, no
`/age-gate/check` call, no jurisdiction detection in client code.

If the product also wants parental consent, data notices, permissions,
and parental preferences handled in the same iframe, use
[`POST /widget/generate-e2e-url`](https://docs.k-id.com/api/endpoints/generate-e-2-eurl)
instead — one widget covers the whole entry flow. See
`k-id-consent-and-challenges` for the consent-flow details.

**Pattern B wins when**: the integration must be small, simple, and
as fast as possible to ship — proofs of concept, internal tools,
early-stage games, hackathons, or products that can accept the
iframe look and prefer minimum code / minimum compliance surface
area.

The rest of this skill is split: the **custom core steps** cover
Pattern A (the default), and the **widget core steps** cover Pattern B.

## Custom core steps (Pattern A)

Follow these in order. Steps 1–4 are prescriptive — exact behavior
matters for compliance and session correctness. Steps 5–6 are UI
and can be adapted to your framework.

### 1. Resolve jurisdiction before rendering the gate

- **Primary**: IP-based detection via your server (MaxMind, Cloudflare
  headers, or equivalent). Store the resulting ISO country code in
  state.
- **Fallback**: `Intl.DateTimeFormat().resolvedOptions().timeZone`
  mapped to a country. Timezone alone is not enough because it's easy
  to spoof and does not distinguish every jurisdiction.
- Persist the detected jurisdiction so it can be passed to
  `/age-gate/check` and to `/age-verification/perform-access-age-verification`
  later.

Reference: [`docs.k-id.com/concepts/jurisdictions`](https://docs.k-id.com/concepts/jurisdictions).

### 2. Resolve platform age signals (mobile and stores)

Before showing any age gate, call the platform age range endpoint when
the platform supplies one (iOS Declared Age Range, Google Play Families,
Unity, etc.).

- Endpoint: `POST /age-gate/get-platform-age-range`.
- If the platform returns a `HIGH`-trust signal for a minor, the signal
  itself determines the session — you do NOT show a slider gate.
- If the platform returns a `LOW`-trust or no signal, show the age gate
  and pass the platform signal in the `/age-gate/check` body.

Reference:
- [`docs.k-id.com/cdk/age-signals/overview`](https://docs.k-id.com/cdk/age-signals/overview)
- [`docs.k-id.com/api/endpoints/get-age-range-for-category`](https://docs.k-id.com/api/endpoints/get-age-range-for-category)

See also `k-id-mobile-native` for OS-side collection.

### 3. Render the age gate — null-initial, slider-style

The single most important rule of a k-ID integration:

```tsx
const [age, setAge] = useState<number | null>(null);
const [hasInteracted, setHasInteracted] = useState(false);

// Display text:
const displayAge = age === null ? '—' : age >= 35 ? '35+' : String(age);

// Submit button:
<button disabled={age === null || !hasInteracted} onClick={onSubmit}>
  Continue
</button>

// Slider onChange:
const onSlide = (value: number) => {
  setAge(value);
  setHasInteracted(true);
};
```

The age starts as `null`, not 0, not 18, not any number. The user must
actively set a value before the submit button enables. This is what
makes the gate a real age gate instead of a formality.

### 4. Call `/age-gate/check` with exactly one age identifier

Build the body on the server, not the client. Send either `dateOfBirth`
(preferred — convert `age` → `YYYY-01-01`) OR `age` directly — never
both. Sending both is rejected with 400.

```http
POST /age-gate/check
Authorization: Bearer <server-only API key>
Content-Type: application/json

{
  "dateOfBirth": "2012-01-01",
  "jurisdiction": "US",
  "platformSignal": { /* optional, from step 2 */ }
}
```

For the full request and response schema, see
[`docs.k-id.com/api/endpoints/check-age-gate`](https://docs.k-id.com/api/endpoints/check-age-gate).

### 5. Handle the three response shapes

| Response | What it means | Next action |
|---|---|---|
| `session.sessionId` with `permissions`, all enabled | User is adult or old enough to proceed with nothing gated | Store session, render the signed-in app |
| `session.sessionId` with a permission carrying `verifiedAgeThreshold` | Session is usable, but a specific permission requires age assurance (for example Brazil ECA Digital loot-boxes at 18, UK OSA 18+ features, Australia social media at 16) | Render the signed-in app; load `k-id-age-verification` when the user taps the gated feature |
| `challenge.challengeId` (no session) | Minor — parental consent needed | Load `k-id-consent-and-challenges` |
| `session` with `ageCategory: "adult"` and `ageVerificationStatus: "unverified"` | Adult whose privileged permissions are withheld pending age verification | Load `k-id-age-verification` |

**Do not synthesize a local session ID.** If the response has no
`session.sessionId`, the correct state is "pending challenge" — not a
fake session. Fake session IDs propagate to privileged endpoints and
cause cascading failures.

### 6. Persist `enteredAge` alongside the session

Keep the raw age the user entered in state. You will need it to re-call
`/age-gate/check` after an expired challenge, or to refresh a session
whose challenge was approved on another device.

## Widget core steps (Pattern B)

### 1. Resolve jurisdiction on the server

Same rule as Pattern A — IP-based detection, timezone fallback.
Widgets require `jurisdiction` in the request body.

### 2. Generate the widget URL from the server

```http
POST /widget/generate-age-gate-url
Authorization: Bearer <server-only API key>
Content-Type: application/json

{
  "jurisdiction": "US-CA",
  "kuid": "12b9fa0e-6d6d-4903-a1fc-f2233027b71d",
  "options": {
    "redirectUrl": "https://yourapp.example/agegate/callback"
  }
}
```

`kuid` is optional — provide the k-ID user ID if the product has one
already, otherwise the widget creates a fresh identity. `redirectUrl`
is optional — without it, the widget runs inline in the iframe and
emits events.

Return the URL to the browser; keep the API key server-side.

### 3. Embed the iframe and listen for events

```tsx
<iframe
  src={ageGateUrl}
  allow="camera; microphone; publickey-credentials-get"
  sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
/>
```

Listen for DOM events emitted by the widget:

- `Widget.AgeGate.Result` with `data.status` and `data.sessionId`
  (plus `data.challengeId` if a challenge was created).
- `Widget.AgeGate.Challenge` with `data.status: "PENDING"` and
  `data.challengeId`.
- `Widget.ExitReview` when the user clicks "Done".

For the full event shapes, see
[`docs.k-id.com/events/dom-events`](https://docs.k-id.com/events/dom-events/overview).

### 4. Act on the result

| Event | Meaning | Next action |
|---|---|---|
| `Widget.AgeGate.Result` with `sessionId` only | User passed, session ready | Store session, render the signed-in app |
| `Widget.AgeGate.Result` with `sessionId` + `challengeId` | Minor — widget has already kicked off a parental-consent challenge | Load `k-id-consent-and-challenges` to poll at the top level of the app; optionally use the e2e widget so the whole flow happens inline |
| `Widget.AgeGate.Challenge` (interim) | Challenge is pending — user is mid-flow | Keep the iframe visible; wait for the final `Result` |

Widgets also surface unverified-adult outcomes in the resulting
session's `ageVerificationStatus` field. After the widget closes, call
`GET /session/get` and check for
`ageVerificationStatus === "unverified"` → load
`k-id-age-verification`.

## Gotchas

Each item below explains why the guidance matters.

### Both patterns

- **Default to custom UI; pick the widget only when the integration
  needs to be small, simple, and fast to ship.** Custom produces the
  best-looking, most-integrated entry screen and works on every
  platform the product targets; the widget is a shortcut that trades
  visual fit for speed-to-integration. The custom path has more
  moving parts than the widget — read the gotchas below before
  choosing.
- **Do not render both at once.** If the product uses the widget, do
  not also build a slider as a fallback — the two paths collect age
  differently and will produce mismatched sessions.
- **Widget URLs are single-use and expire quickly.** Generate fresh
  each time the user reaches the gate. Do not cache them client-side
  across reloads.
- **Widget events only fire on the parent window if same-origin is
  granted.** Use `sandbox="allow-scripts allow-same-origin"` (or
  handle `redirectUrl` instead if the product cannot grant that).

### Custom-only

- **`useState<number | null>(null)` — never `useState(18)`.** A default
  of 18 is a COPPA violation — the gate has no meaningful effect.
- **Send exactly ONE age identifier to `/age-gate/check`.** `dateOfBirth`
  OR `age`, not both. Sending both is rejected with 400 and no
  descriptive body.
- **Jurisdiction must be detected server-side.** Client-only geolocation
  is easy to spoof and does not cover edge-case regions (US state-level
  COPPA 2.0 equivalents). Use IP + timezone on the server.
- **Platform signals resolve BEFORE the gate.** If iOS returns a
  `HIGH`-trust minor signal, the age gate is skipped and the session is
  minted from the signal. Showing a slider anyway asks the user to
  contradict the OS.
- **Never `window.open` or `target="_blank"` for age verification.**
  When the gate returns an unverified adult, `k-id-age-verification`
  opens an iframe modal — do not break out to a new tab here either.
- **Never call `/age-gate/check` from the browser.** The API key is
  server-only. If you're tempted to call it client-side, read
  `k-id-server-trust-boundary` first.
- **`local-${Date.now()}` is not a sessionId.** If the response has no
  session, the user is in a challenge state, not a session state. The
  app renders differently (load `k-id-consent-and-challenges`).
- **Timezone-only jurisdiction detection is not sufficient.** Use IP as
  primary, timezone as fallback. Timezone spoofing is trivial.
- **Store `enteredAge` at gate time.** Later flows (expired challenge
  retry, limited-access session refresh when
  `childLiteAccessEnabled` is true) need to re-call
  `/age-gate/check(enteredAge, jurisdiction)`. Losing the age forces a
  full re-prompt.
- **Age display should cap at "35+"** — exposing exact age above the
  cap is a minor UX leak (looks like you're tracking adult age) with
  no product value.

## Defaults

When the user asks for a "standard k-ID age gate", **default to a
custom UI (Pattern A)**. Custom produces the best-looking,
most-integrated entry screen and works on every platform the product
targets. Drop to the widget (Pattern B) only when the integration
must be small, simple, and as fast as possible to ship.

For a custom UI (Pattern A), use these visual defaults:

- Slider range: 1–99, step 1.
- Display: `'—'` before first interaction; `'35+'` above 35.
- Submit button disabled until `age !== null && hasInteracted`.
- Modal width: 480px max.
- Modal height: `min(720px, calc(100vh - 48px))`.
- Date-of-birth conversion: `YYYY-01-01` based on current year minus age.
- Jurisdiction fallback: `"US"` only if both IP and timezone fail —
  otherwise you mis-apply US rules to non-US users.

## Validation step

After wiring the gate, run the checklist for the pattern you built.

### Pattern A — custom

1. Submit with `age === null` — button is disabled (no network request
   fires).
2. Submit with a slider-set age — receive exactly one of `session`,
   `challenge`, or an unverified-adult `session`. Log the raw response
   for this run.
3. Call `GET /session/get` with the returned `sessionId` and confirm
   `ageCategory`, `jurisdiction`, and `permissions` are populated.
4. Refresh the page — the session persists, or a pending challenge is
   re-entered correctly.

If step 3 returns an empty `permissions` array for what should be a
full-access session, treat it as a configuration or provisioning
issue and re-run discovery (load `k-id-sessions-and-permissions`).

### Pattern B — widget

1. The server can generate an age-gate URL with the correct
   `jurisdiction` and the URL loads in an iframe without CSP errors.
2. The widget emits `Widget.AgeGate.Result` with a `sessionId` after
   a successful age entry.
3. `GET /session/get` with that `sessionId` returns the expected
   `ageCategory`, `jurisdiction`, and `permissions`.
4. A minor age emits `Widget.AgeGate.Challenge` with a `challengeId`
   — the product does not need to call `/age-gate/check` separately.
5. The API key is never reachable from the browser.

## Next steps

- Minor with pending challenge → [`k-id-consent-and-challenges`](../k-id-consent-and-challenges/SKILL.md).
- Unverified adult → [`k-id-age-verification`](../k-id-age-verification/SKILL.md).
- Rendering the post-gate permission-management UI → [`k-id-sessions-and-permissions`](../k-id-sessions-and-permissions/SKILL.md).
- Server-side wiring → [`k-id-server-trust-boundary`](../k-id-server-trust-boundary/SKILL.md).
- Mobile OS age signals → [`k-id-mobile-native`](../k-id-mobile-native/SKILL.md).

Canonical references:
- [Age gate concept](https://docs.k-id.com/concepts/access-features-consent/age-gate)
- [`POST /age-gate/check`](https://docs.k-id.com/api/endpoints/check-age-gate)
- [`POST /widget/generate-age-gate-url`](https://docs.k-id.com/api/endpoints/generate-age-gate-url)
- [`POST /widget/generate-e2e-url`](https://docs.k-id.com/api/endpoints/generate-e-2-eurl)
- [`Widget.AgeGate.Result` event](https://docs.k-id.com/events/dom-events/event-structures/widget-agegate-result)
- [`Widget.AgeGate.Challenge` event](https://docs.k-id.com/events/dom-events/event-structures/widget-agegate-challenge)
- [Custom age gate quickstart](https://docs.k-id.com/get-started/quickstart-guides/custom-age-gate)
- [Choose integration: CDK widgets vs custom UX](https://docs.k-id.com/get-started/choose-integration)
