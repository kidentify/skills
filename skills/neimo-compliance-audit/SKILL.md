---
name: neimo-compliance-audit
description: "Run a multi-market children's-digital-safety compliance audit for a game, app, or platform using the Neimo MCP regulatory knowledge base. Activates when the user asks to audit a product against COPPA (US), GDPR Article 8 (EU), UK Children's Code / Online Safety Act, Brazil ECA Digital, Australia Online Safety / social-media minimum age, or other kids' regulatory regimes across multiple markets at once. Produces a structured findings document keyed by jurisdiction with citations to primary sources and a tiered must / should / consider obligations list. Requires a working Neimo MCP connection (https://neimo.k-id.com/connect)."
license: SEE-LICENSE-FILE
metadata:
  version: "0.1.0"
  vendor: k-ID
---

# Neimo Compliance Audit

Run a multi-market compliance audit for a children's-facing product. Produce a structured findings document keyed by jurisdiction, with citations to primary sources and a clear "must / should / consider" tier per requirement.

## When to use this skill

- The user asks "is this game compliant in [list of markets]"
- The user is preparing a launch and needs a per-market obligations list
- The user is reviewing a feature change (e.g. adding chat, monetization, ads) for child-safety implications
- The user asks "what changes if we open this to under-18s" or similar age-shift question

## Inputs to gather from the user

Before running the audit, confirm:

1. **Product type.** Game, social platform, edtech, video, retail, gambling-adjacent, etc. The audit changes materially.
2. **Target markets.** Specific country list. If the user says "EU", expand to the member-state count and call out FR, DE, IE, ES, IT, NL, PL specifically (highest-traffic markets and most active regulators). For "global", default to: US (federal + CA + TX + UT), EU (DE, FR, IE), UK, BR, AU, JP, KR, IN.
3. **Age range supported.** Under-13, under-16, under-18, or all ages with parental controls.
4. **Data collection surface.** Account creation flow, content created by user, third-party SDKs (analytics, ads, attribution), payment data.
5. **Monetization model.** Free, paid, IAP, ads (which networks), subscription, lootboxes, gambling-style mechanics.
6. **Communication features.** 1:1 chat, group chat, voice, user-generated content, livestream.

If the user provides a partial list, ask for the missing inputs in one message before continuing.

## Tools to use

This skill orchestrates the Neimo MCP tools. The user must have Neimo MCP configured before this skill is invoked. Call the tools in this order:

1. **`market_profile`** for each target market. Get the full kids-regulation overview per jurisdiction, cap 50 rows.
2. **`lookup_regulation`** with `domain: "age-threshold"`, `domain: "parental-consent"`, `domain: "data-protection"` per market. Pull the structured row data.
3. **`lookup_state_laws`** for US, with `state: "FEDERAL"` (COPPA) and the relevant state codes (CA SB-976, TX HB-18, UT SMARA, etc.).
4. **`search_kb_semantic`** for any cross-cutting topics raised by the product type: "lootboxes minors", "behavioral advertising children", "content moderation under 18", "session length limits", etc.
5. **`search_primary_sources`** for verbatim text of the highest-impact requirements, particularly when the user is drafting privacy policy / ToS language and needs the exact wording.
6. **`lookup_market_insights`** for a quality check: what fraction of tested products in this market actually have the relevant control. Flags requirements that the market enforces in practice vs. on-paper.

If Neimo MCP is not configured, stop and direct the user to https://neimo.k-id.com/connect to issue a free trial key.

## Output structure

Produce a single document with these sections, in order:

### 1. Executive summary

- Three to five bullets. The most material risks and the quick-wins.
- One line per jurisdiction: "[market]: [pass/risk/blocker]" with one-sentence reason.

### 2. Per-market findings

One subsection per market. Each contains:

- **Age threshold(s)** that apply (digital consent age, minimum age for service, minimum age for specific features). Cite the row(s) returned by `lookup_regulation`.
- **Parental consent.** Mechanism required (verifiable parental consent / VPC, GUARDIAN-managed, age-gate + double opt-in, etc.). Cite primary source.
- **Data minimization & purpose limitation.** What is the regulator's posture on collecting data from minors for this product type. Quote the relevant statute or guidance.
- **Advertising & profiling restrictions.** Behavioral advertising, retargeting, lookalikes, attribution SDKs.
- **Content moderation duties.** UGC, chat, voice. UK OSA / EU DSA / Australia OSA-equivalent obligations.
- **Enforcement signals.** Recent fines, settlements, public-facing investigations. Use `search_kb_semantic` for "[regulator] [year]" or "[product type] settlement [country]".

### 3. Tiered obligations (must / should / consider)

A flat table with columns: Requirement, Markets, Tier, Effort, Citation.

- **Must:** legal obligation. Non-compliance is risk of fine or service block. Sort by market severity.
- **Should:** strong regulatory expectation, standard industry practice, or condition of platform-store approval (Apple App Store, Google Play kids program).
- **Consider:** good-faith hardening that improves enforcement posture or unlocks user-trust signals.

### 4. Open questions

Anything the audit could not resolve from the KB. List them so the user can route to legal counsel or a specific regulator.

### 5. Citations

Every claim must cite the primary source URL or the Neimo KB row identifier. If two sources conflict, surface the conflict explicitly.

## Tone and constraints

- Plain, direct, lawyer-readable. No marketing language.
- Never assert that something is "compliant" without citing the requirement. Compliance is a posture, not a binary.
- If the user is missing info to make a determination, list it under Open questions; do not guess.
- Prefer the regulator's own wording for thresholds (ages, fines, deadlines) over a paraphrase.
- If a market has no Neimo KB coverage, say so and recommend the user supplement with k-ID Compliance Studio or counsel. Do not silently skip.
- Output is read by an engineer and counsel together. Optimize for them, not for executives.
