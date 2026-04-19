# k-ID Agent Skills

Agent Skills for integrating k-ID — age-appropriate compliance as a service —
into your app, game, or platform. These skills cover the full range of
jurisdictional regimes a k-ID integration can be configured for:

- **COPPA** (US)
- **GDPR-Kids** (EU)
- **UK AADC** and the **UK Online Safety Act** (highly effective age assurance for 18+ features)
- **Brazil ECA Digital** (loot-boxes and targeted ads at 18, direct marketing at 12)
- **Australia Online Safety Act** (social media minimum age)
- Other regional regimes configured in k-ID Compliance Studio

They follow the open [Agent Skills specification](https://agentskills.io/specification)
and work with 35+ AI coding agents including Claude Code, Cursor, OpenAI
Codex, GitHub Copilot, Gemini CLI, and others.

Canonical reference for API shapes and endpoints remains
[`docs.k-id.com`](https://docs.k-id.com). These skills encode integration
patterns, compliance invariants, and known pitfalls — not API documentation.

## Two integration shapes

The skills cover both k-ID integration shapes. Use whichever matches
your product.

- **Shape A — Full sessioned integration.** Age gate → session →
  (consent | verification | threshold) → permissions. For games,
  social platforms, and multi-feature apps that need persistent
  per-user state and multiple gated features.
- **Shape B — Standalone AgeKit+.** One call to the age-verification
  endpoint, no session, no permission-management UI. For 18+ sites
  (UK OSA), age-restricted downloads, AU social-media minimum-age
  checks, or any single age-proof decision.

The router skill detects which shape applies from the user's request.

## Two UI approaches within Shape A

Within Shape A, there is a second choice: **custom UX workflows**
(build the UI, call the APIs) or **widgets** (pre-built k-ID iframes).

- **Custom UX workflows** (the default). Build the age gate and
  consent UI yourself and call `/age-gate/check`,
  `/challenge/send-email`, etc. directly. Produces the best-looking,
  most brand-integrated experience, renders inline (no iframe), and
  works on every platform k-ID supports — including Unity WebGL,
  consoles, and native desktop apps where iframes aren't practical.
  Recommended for production integrations.
- **Widgets** (fast-path fallback). k-ID publishes drop-in widgets
  for the age gate, the end-to-end flow (age gate + parental consent
  + data notices + permissions + preferences), manage-permissions
  upgrades, and data notices. They carry built-in
  jurisdiction-appropriate age collection, initiate parental-consent
  challenges automatically, and emit DOM events
  (`Widget.AgeGate.Result`, `Widget.AgeGate.Challenge`) to the parent
  window. Choose when the integration must be small, simple, and as
  fast as possible to ship — proofs of concept, internal tools,
  early-stage games.

The `k-id-age-gate` and `k-id-consent-and-challenges` skills cover
both approaches — the router picks the right pattern from the user's
intent. See
[Choose integration](https://docs.k-id.com/get-started/choose-integration)
for the canonical comparison.

## What's in here

Eight skills, designed to work together:

| Skill | Purpose |
|---|---|
| `k-id-integration` | Router. Picks the right shape and sibling skill(s) based on the user's request. |
| `k-id-age-gate` | Entry point for **Shape A** — `/age-gate/check`, jurisdiction detection, correct age-appropriate defaults. |
| `k-id-consent-and-challenges` | **Shape A** only — GUARDIAN-managed parental consent flow for minors (QR + OTP + email) and challenge polling. |
| `k-id-age-verification` | Age verification and assurance for **both shapes** — standalone AgeKit+ (Pattern 1), unverified-adult in a session (Pattern 2), and per-permission threshold (Pattern 3, UK OSA 18+, Brazil ECA Digital, Australia social media age). |
| `k-id-sessions-and-permissions` | **Shape A** only — live permission propagation, `/session/upgrade`, permission-gated UI controls, `verifiedAgeThreshold` handling. |
| `k-id-webhooks` | Webhook signature verification and event handling. Relevant to both shapes. |
| `k-id-server-trust-boundary` | Companion skill: API key placement, server proxy, pre-flight checks. Required for both shapes. |
| `k-id-mobile-native` | Companion skill: iOS/Android/Unity platform age signals and deep links. |

## Install

### Claude Code (plugin marketplace — fastest)

```bash
/plugin marketplace add github.com/kidentify/skills
/plugin install k-id-skills@kidentify
```

### Cursor, Codex, Copilot, Gemini CLI, and most other agents

Clone into your project's `.agents/skills/` directory:

```bash
mkdir -p .agents/skills
git clone --depth 1 https://github.com/kidentify/skills.git .agents/k-id-skills-tmp
cp -r .agents/k-id-skills-tmp/skills/* .agents/skills/
rm -rf .agents/k-id-skills-tmp
```

For tool-specific GUI install paths, slash commands, and verification
steps, see the full install matrix on
[docs.k-id.com/get-started/agent-skills](https://docs.k-id.com/get-started/agent-skills).

### Airgapped or no-git environments

Download the repo as a ZIP via the green "Code" button on GitHub, extract,
and copy the `skills/` contents into your tool's skills directory.

## How it works

The `k-id-integration` router is the first skill that activates on any k-ID
integration request. Based on the user's question, it points the agent at
the right feature skill (age gate, consent, verification, etc.), which in
turn may pull in companion skills (trust boundary, mobile native).

Each skill is self-contained: a `SKILL.md` with invariants and gotchas
inline, plus focused reference material in `references/` when the agent
needs more detail on demand.

## Design principles

- **Doc-first.** API request/response shapes come from
  [`docs.k-id.com`](https://docs.k-id.com). Skills encode patterns and
  pitfalls, not endpoints.
- **Invariants inline, reference on demand.** The highest-value content —
  the rules that prevent real, shipped bugs — lives directly in each
  `SKILL.md`. Detailed reference material is loaded only when needed.
- **Calibrated prescriptiveness.** Exact commands for fragile operations
  (API bodies, signature verification). Higher freedom for UI adaptation.
- **Defaults, not menus.** One recommended path per choice point; escape
  hatches noted where they matter.
- **Validate your work.** Every skill ends with a verification step so
  the agent confirms the integration is actually working.

## Contributing

This repository is closed to external contributions. To report a bug or
request a correction, open an issue on GitHub or email
`developers@k-id.com`.

## License and acceptable use

License: **TBD** — see [`LICENSE`](./LICENSE).

Regardless of the final license, these skills may not be used or modified
to circumvent age verification, parental consent, or other child-protection
controls. See [`ACCEPTABLE_USE.md`](./ACCEPTABLE_USE.md) for the full policy.

## Related

- [k-ID Developer Hub](https://docs.k-id.com) — canonical API reference
- [Agent Skills specification](https://agentskills.io/specification) — format these skills follow
- [Agent Skills client showcase](https://agentskills.io/clients) — compatible AI tools
