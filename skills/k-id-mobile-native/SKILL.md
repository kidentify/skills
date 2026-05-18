---
name: k-id-mobile-native
description: "Companion skill for iOS, Android, and Unity k-ID integrations — collects platform-supplied age signals (iOS Declared Age Range, Google Play Families, Unity user data) before the age gate, passes them on /age-gate/check with correct trust levels, and renders every k-ID widget URL (age gate, end-to-end, consent, age verification, manage-permissions, data notices) in a system browser — Android **Custom Tabs** or iOS **ASWebAuthenticationSession** (SFSafariViewController also OK). Discourages Android `WebView` / iOS `WKWebView`: no WebAuthn means no k-ID **AgeKeys** — a UX downgrade and a compliance limit where AgeKeys back \"highly effective age assurance\". Uses the universal `redirectUrl` deep-link callback for result delivery; reserves DOM `postMessage` for the WebView fallback. Covers deep-link returns from Family Connect / asktoplay.com and third-party verifier apps. Use for native apps, App Store Accountability Acts, Google Play Families, Unity, AgeKeys, or iOS popup failures. Not for browser-only web."
license: Apache-2.0
metadata:
  version: "1.0.0"
  vendor: k-ID
---

# k-ID Mobile and Native

Native apps (iOS, Android, Unity) get age signals from the OS and the
store, not from headers. They also can't rely on browser iframes and
`window.open` the way a web app can. This skill covers the three
native realities: platform age signals before the age gate, the
correct way to render widget URLs (system browser, **not** embedded
WebView), and the `redirectUrl` deep-link pattern for delivering
widget results back to the app.

## When to use

Use this skill when the user is:

- Building a k-ID integration in a native iOS app (Swift / SwiftUI),
  Android app (Kotlin / Compose), or Unity game.
- Reading iOS Declared Age Range, Google Play Families, or other
  platform age ranges before showing the gate.
- Passing a platform signal to `/age-gate/check` with the correct
  trust level.
- Choosing how to display a k-ID widget URL on mobile — Custom Tabs
  vs `WebView` on Android, `ASWebAuthenticationSession` vs
  `SFSafariViewController` vs `WKWebView` on iOS.
- Diagnosing missing AgeKeys ("why doesn't the AgeKey option
  appear?") — usually caused by embedding the widget in WebView or
  WKWebView, which don't support WebAuthn.
- Wiring a `redirectUrl` deep link so widget results reliably return
  to the app.
- Handling deep-link returns from Family Connect / `asktoplay.com`
  or third-party verification apps (for example ConnectID opening a
  banking app).
- Diagnosing US App Store Accountability Act (Utah, Texas, Louisiana)
  compliance concerns.

For the web-only case where platform signals come from request
headers, the feature skills alone are enough.

## Core steps

### 1. Read the platform age signal as soon as you can

| Platform | Source |
|---|---|
| iOS 18+ | `AppStore.deviceAgeRange` (Declared Age Range API) |
| Android | Google Play Families Service / Play Protect age range |
| Unity | User data from player account service |
| Other stores | Per-platform — document what you have access to |

Read the signal at app start or first protected screen, before
rendering the age gate UI.

Reference:
- [Age signals concept](https://docs.k-id.com/concepts/age-signals)
- [Platform age signals overview](https://docs.k-id.com/cdk/age-signals/overview)
- [Platform details](https://docs.k-id.com/cdk/age-signals/platform-details)

### 2. Classify trust level correctly

Trust level determines whether you skip the age gate or combine the
signal with a user-entered age:

- `HIGH` — platform says "this user is ≤ 12" (or equivalently
  narrowed). Skip the slider, pass the signal to `/age-gate/check`,
  let k-ID mint a minor session.
- `LOW` — platform says "adult" but the declaration is optional /
  self-reported / easy to change. Show the slider AND pass the
  signal; k-ID will compare.
- `UNKNOWN` — no signal at all. Show the slider.

**Never upgrade a LOW-trust adult signal to HIGH on your side.** Let
k-ID decide. The age signal trust taxonomy is policy, not preference.

### 3. Call `/age-gate/get-platform-age-range` when needed

Some platforms require confirming the range server-side before using
it. Run this through your server proxy (see
[`k-id-server-trust-boundary`](../k-id-server-trust-boundary/SKILL.md)) —
never from the mobile binary.

Reference:
[`docs.k-id.com/api/endpoints/get-age-range-for-category`](https://docs.k-id.com/api/endpoints/get-age-range-for-category).

### 4. Pass the signal on `/age-gate/check`

Body includes a `platformSignal` object:

```json
{
  "dateOfBirth": "2012-01-01",
  "jurisdiction": "US",
  "platformSignal": {
    "platform": "ios",
    "ageRange": { "min": 9, "max": 12 },
    "trustLevel": "HIGH"
  }
}
```

The exact schema is on
[`docs.k-id.com/api/endpoints/check-age-gate`](https://docs.k-id.com/api/endpoints/check-age-gate).
Don't invent a shape — fetch the current doc.

### 5. Render widget URLs in a system-browser context — not WebView or WKWebView

Every k-ID widget URL (age gate, end-to-end, consent, age
verification, manage-permissions, data notices) must load in a
system-browser surface that supports **WebAuthn**. This is what
unlocks k-ID **AgeKeys** — FIDO-based reusable age-proof credentials
— which are offered as a verification option inside the widget
whenever they're available. Without WebAuthn the user never sees
AgeKeys and has to re-prove their age with a heavier method every
time.

| Platform | Recommended | Also acceptable | Do not use |
|---|---|---|---|
| Android | **Custom Tabs** (`CustomTabsIntent`) | — | `WebView`; Trusted Web Activity (TWA falls back to Custom Tabs anyway) |
| iOS | **`ASWebAuthenticationSession`** | `SFSafariViewController` | `WKWebView` |
| Unity | Platform-specific plugin that opens Custom Tabs (Android) or `ASWebAuthenticationSession` (iOS) | — | Embedded Unity WebView for widget URLs |

**Why WebView and WKWebView are not recommended:** neither supports
WebAuthn, so neither can create or use AgeKeys. This is a material
UX downgrade (the user loses a one-tap reusable verification option)
and can be a compliance limitation in jurisdictions where AgeKeys
are part of the "highly effective age assurance" story. See
[docs.k-id.com/get-started/quickstart-guides/mobile-apps](https://docs.k-id.com/get-started/quickstart-guides/mobile-apps).

**Also do not use:** external-browser handoffs like
`UIApplication.open(url)` on iOS or a generic `ACTION_VIEW` intent
on Android. They leave the app, don't reliably fire a completion
callback, and can be blocked when the app was launched from a
store-managed container.

**If the integration genuinely must use WebView / WKWebView** (for
example, legacy apps, deep native chrome, or a product that can't
accept Custom Tabs) — document the AgeKeys loss as a known gap, use
the DOM `postMessage` fallback for results (step 6 — widgets emit
`Widget.AgeGate.Result`, `Widget.AgeGate.Challenge`,
`Widget.DataNotices.ConsentApproved`, `Widget.ExitReview`), and tell
the user upfront that AgeKeys will not appear.

### 6. Pass a `redirectUrl` deep link — universal result delivery

Every widget URL accepts an `options.redirectUrl`. When the flow
completes, the widget redirects to that URL with the result as query
params. This is the **recommended** and **universal** result
mechanism — it works with every display method in the table above,
survives the app being backgrounded, and is the only reliable
mechanism for Custom Tabs / `ASWebAuthenticationSession` /
`SFSafariViewController` (which do not expose DOM `postMessage` to
the host app).

```
myapp://vpc-complete?sessionId=608616da-…&result=PASS
myapp://verification-complete?verificationId=7854909b-…&result=PASS
```

Wire it up:

1. Register a deep-link handler in the app
   (`myapp://vpc-complete`, `myapp://verification-complete`, or
   similar).
2. On the server (never the mobile binary — see
   [`k-id-server-trust-boundary`](../k-id-server-trust-boundary/SKILL.md)),
   include `options.redirectUrl` in the widget-URL-generation call
   (`/widget/generate-e2e-url`, `/widget/generate-age-gate-url`,
   `/widget/generate-manage-session-permissions-url`,
   `/age-verification/perform-access-age-verification`).
3. On callback, parse `sessionId` / `verificationId` / `result` and
   **verify server-side** via `/session/get` (CDK) or
   `/age-verification/get-status` (AgeKit+) — never trust the deep
   link alone. See
   [docs.k-id.com/api/endpoints/check-age-gate](https://docs.k-id.com/api/endpoints/check-age-gate)
   and
   [docs.k-id.com/api/endpoints/perform-access-age-verification](https://docs.k-id.com/api/endpoints/perform-access-age-verification)
   for the request and response shapes.

DOM `postMessage` events are available **only** inside WebView /
WKWebView and should be treated as a fallback for those two
surfaces, not a primary design.

### 7. Handle deep-link returns from Family Connect, asktoplay.com, and third-party apps

Family Connect, `asktoplay.com`, and third-party verification apps
(ConnectID opening the user's banking app, for example) all return
to the app via the same `redirectUrl` deep link configured in step 6.
Configure the OS-level handler:

- iOS: Universal Link with an `apple-app-site-association` file on
  the return domain, or a custom URL scheme registered via
  `CFBundleURLTypes` in `Info.plist`.
- Android: Intent filter with `android:autoVerify="true"` on an
  `https` scheme, or a custom scheme in `AndroidManifest.xml`.
- Unity: Platform-specific plugin.

On return, do NOT trust the deep link as authoritative proof of
consent or verification. Use it only as a hint to re-fetch state
from the server. The webhook (see
[`k-id-webhooks`](../k-id-webhooks/SKILL.md)) is authoritative.

Third-party app redirects (ConnectID etc.) require a system-browser
surface — they don't work inside embedded WebView / WKWebView
because the app-to-app handoff needs the full browser context to
redirect back.

### 8. Adapt the verification modal for the chosen surface

The in-app verification-prompt pattern from
[`k-id-age-verification`](../k-id-age-verification/SKILL.md) still
applies, but the surface is a system browser, not an embedded
WebView:

- On iOS, present `ASWebAuthenticationSession` with
  `callbackURLScheme` matching the `redirectUrl` scheme. Hold a
  strong reference to the session; a deallocated session cancels
  the flow without firing the callback.
- On Android, launch `CustomTabsIntent` from the activity; let the
  deep-link intent filter bring the user back.
- Success handler runs when the callback URL fires OR the server
  poll returns verified — whichever happens first.
- Idempotent: prevent double-processing on return-foreground events.

### 9. Background-refresh on foreground

Mobile users background apps constantly. On `applicationDidBecomeActive`
(iOS) / `onResume` (Android), refresh the session. This mirrors the
web's `visibilitychange`/`focus` wake.

## Gotchas

- **Don't embed widget URLs in Android `WebView` or iOS `WKWebView`.**
  Neither supports WebAuthn, so neither can create or use AgeKeys.
  The user loses the one-tap reusable verification path and has to
  re-prove their age with a heavier method every time. Use Custom
  Tabs on Android and `ASWebAuthenticationSession` (or
  `SFSafariViewController`) on iOS. See
  [docs.k-id.com/get-started/quickstart-guides/mobile-apps](https://docs.k-id.com/get-started/quickstart-guides/mobile-apps).
- **"AgeKeys option never appears" is almost always a WebView /
  WKWebView issue.** AgeKeys surface inside the widget only when
  the rendering surface supports WebAuthn. Switch surface first;
  everything else is downstream.
- **Don't upgrade a LOW-trust signal to HIGH.** Trust classification is
  k-ID's call. Self-upgrading is a compliance risk in App Store
  Accountability jurisdictions.
- **Don't call k-ID APIs from the mobile binary directly.** The API
  key in a binary is extractable from the binary. Every widget URL
  (including `redirectUrl`) must be generated server-side via your
  server proxy. See
  [`k-id-server-trust-boundary`](../k-id-server-trust-boundary/SKILL.md).
- **Don't use external-browser handoffs for widget URLs.** iOS
  `UIApplication.open(url)` to Safari and a generic Android
  `ACTION_VIEW` intent both leave the app, don't reliably fire a
  completion callback, and can be blocked in store-managed
  containers. Use Custom Tabs / `ASWebAuthenticationSession`
  instead — they keep the app in context and trigger the
  `redirectUrl` deep link cleanly.
- **Deep-link returns are hints, not proof.** Always refresh session
  state from the server on return (`/session/get` for CDK,
  `/age-verification/get-status` for AgeKit+). Don't mark the user
  as verified based on URL params alone.
- **DOM `postMessage` only works inside WebView / WKWebView.** If
  the plan is to use Custom Tabs or `ASWebAuthenticationSession`,
  wire up `redirectUrl` — `postMessage` will never fire.
- **Third-party verification apps (ConnectID etc.) don't work inside
  WebView / WKWebView.** The banking-app redirect needs a full
  browser context to return. Use Custom Tabs /
  `ASWebAuthenticationSession`.
- **`ASWebAuthenticationSession` must be held in a strong
  reference.** A session that goes out of scope is deallocated and
  the flow cancels without firing the callback — the user sees
  "nothing happens when I tap verify".
- **Don't cache platform age signals across sessions.** Apple and
  Google can change the signal when the user changes their settings.
- **US App Store Accountability Acts (Utah / Texas / Louisiana) make
  platform signals non-optional.** If you're serving those
  jurisdictions, you MUST collect the signal when available —
  skipping it is a legal exposure, not a UX nicety.
- **Unity: open widgets through a platform-specific plugin, not the
  built-in Unity WebView.** Embedded Unity WebView has the same
  WebAuthn / AgeKeys limitation as native WebView / WKWebView, and
  `postMessage` support varies by plugin. Bridge out to Custom Tabs
  (Android) or `ASWebAuthenticationSession` (iOS), and fall back to
  server polling where the plugin path is unreliable.
- **Keep the API proxy URL out of the binary**, or at least treat it
  as public and never assume it's secret. The secret is the API key
  on your server.

## Defaults

- Widget rendering surface:
  - iOS: `ASWebAuthenticationSession` for every widget URL.
    `SFSafariViewController` is acceptable when the app needs a
    more Safari-like chrome. Do **not** default to `WKWebView`.
  - Android: Chrome Custom Tabs (`CustomTabsIntent`) for every
    widget URL. Do **not** default to `WebView` or Trusted Web
    Activity.
  - Unity: platform-specific plugin that bridges to Custom Tabs /
    `ASWebAuthenticationSession`, with server-poll fallback.
- Result delivery: `options.redirectUrl` deep link on every widget
  URL. `postMessage` is a fallback only for the WebView / WKWebView
  case.
- Deep-link handling: refresh session on return; never trust URL
  params as proof.
- Foreground refresh: always on.
- API calls: always via your server proxy.

## Validation step

1. Install on a device that provides a platform age signal (a parent's
   Apple ID with a kid account; Google Family Link). Launch the app —
   the signal is read BEFORE the age gate appears.
2. Verification flow launches in `ASWebAuthenticationSession` (iOS)
   or Chrome Custom Tabs (Android) — **not** `WKWebView` or
   `WebView`.
3. Inside the widget, the AgeKey option is visible as a verification
   method (on a device that supports passkeys / WebAuthn). If it's
   missing, the rendering surface is wrong.
4. Completion returns to the app via the `redirectUrl` deep link
   within a few seconds, with `sessionId` / `verificationId` and
   `result` query parameters. The app calls `/session/get` or
   `/age-verification/get-status` to confirm server-side.
5. Backgrounding the app mid-verification and returning — the session
   shows verified after refresh.
6. Attempting to extract the API key from the compiled binary — it's
   not there (because it's on your server).
7. On a US Accountability Act jurisdiction IP, the platform signal is
   collected and passed to `/age-gate/check`.

## Next steps

- Handling the age-gate response → [`k-id-age-gate`](../k-id-age-gate/SKILL.md).
- Consent for minors → [`k-id-consent-and-challenges`](../k-id-consent-and-challenges/SKILL.md).
- Adult verification → [`k-id-age-verification`](../k-id-age-verification/SKILL.md).
- Server proxy and key placement → [`k-id-server-trust-boundary`](../k-id-server-trust-boundary/SKILL.md).
- Webhook-driven post-verification sync → [`k-id-webhooks`](../k-id-webhooks/SKILL.md).

Canonical references:
- [Mobile apps quickstart](https://docs.k-id.com/get-started/quickstart-guides/mobile-apps)
- [Age signals concept](https://docs.k-id.com/concepts/age-signals)
- [Platform age signals overview](https://docs.k-id.com/cdk/age-signals/overview)
- [Platform details](https://docs.k-id.com/cdk/age-signals/platform-details)
- [`POST /age-gate/check`](https://docs.k-id.com/api/endpoints/check-age-gate)
