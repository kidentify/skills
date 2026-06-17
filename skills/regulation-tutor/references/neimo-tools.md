# neimo. MCP — tool reference for the tutor

neimo. is k-ID's children's-digital-safety regulatory KB, covering 200+ markets
with structured data on age thresholds, parental consent, data protection,
monetization, trust & safety, and enforcement. Read this when you need to pick
the right tool or parse a result.

## Grounding reminder

Every fact you teach must come from one of these tool results in the current
session. If a tool returns empty, say neimo. has no data for that
market/topic — do not fill from memory. Write the brand as **neimo.** (lowercase,
trailing period).

## Market codes

Use ISO 2-letter codes for the `market` argument — "US", "BR", "GB", "AU", "KR",
"JP", "DE". The server normalizes common names but ISO is preferred.

## The row shape you get back

`lookup_regulation` and `market_profile` return rows like:

```json
{
  "market": "BR",
  "section": "Parental Consent",
  "sectionKey": "parental-consent",
  "field": "Are there any recommended method(s) for parental consent?",
  "column": "Response",
  "value": "[\"Credit card verification\",\"Document validation\",\"2 step verification (SMS)\"]",
  "reference": "Art. 14 LGPD [https://...]  ECA Digital, Law No. 15,211 [https://...]",
  "verificationStatus": "kid-reviewed"
}
```

Notes for teaching:
- `value` is the operative fact. It is sometimes a JSON-encoded array inside a
  string (as above) — parse it and present as a clean list.
- `reference` holds one or more primary-source citations with URLs embedded in
  square brackets. Surface these to the learner; they are the proof.
- `verificationStatus` (e.g. `kid-reviewed`) tells the learner how trustworthy
  the row is. Mention it.
- Watch for forward-looking values — references sometimes cite laws with a
  future effective date (e.g. Brazil's ECA Digital, effective 17 March 2026).
  Flag these as pending vs live.

## Tools

| Tool | Use it for |
|---|---|
| `discover_sections(market)` | List available sections for a country. Call first if unsure of section names — wrong names return empty. |
| `lookup_regulation(market, domain, field?)` | The workhorse. One section of one market. `domain` matches flexibly (hyphens/casing ignored). |
| `search_kb_semantic(query, market?)` | Keyword search across the gaming-social-media KB. Best for enforcement actions, settlements, cross-cutting questions. Ranked, returns up to 15 rows. |
| `lookup_online_safety_resources(topic, market?)` | Broad keyword search across ALL neimo. KBs (not just gaming). Use when topic may span KBs or you don't know the section. |
| `market_profile(market)` | Whole-country snapshot, every section. LARGE (100K+ chars) — use sparingly and summarize; never dump into chat. |
| `lookup_legal_horizons(jurisdiction?, query?, publishMonth?)` | k-ID's Legal Horizons newsletter archive — recent regulatory developments and legislative changes. |
| `lookup_regulation_events(...)` | Dated regulatory events / timeline. Good for "what's coming". |
| `compare_regulations(...)` | Same topic across multiple markets — for "how does this differ in X vs Y" teaching turns. |
| `lookup_state_laws(...)` | US state-level laws (e.g. California AADC, state privacy acts). |
| `get_metric_glossary(...)` | Definitions of metrics/terms used in the KB. |
| `lookup_market_insights(...)` | Market context beyond the bare rule. |
| `search_primary_sources(...)` | True semantic (vector) search over downloaded primary-source documents — deeper than `search_kb_semantic` for finding exact passages. |
| `fetch_source_content(...)` | Fetch a live primary-source page. Use when the learner wants the actual text behind a citation. |
| `submit_feedback(...)` | Creates a Zendesk ticket. ONLY call after the learner says yes to "share that feedback with the neimo. team?". |

## Common section keys (gaming-social-media KB)

Coverage varies by market — always confirm with `discover_sections`. Seen in US:

`age-threshold`, `age-assurance`, `parental-consent`,
`special-privacy-policy-for-kids-teens`, `changes-to-eula-and-privacy-policy`,
`game-notice-s`, `record-keeping-and-audit`, `penalties-and-enforcement`,
`settings` (large — includes targeted advertising), `monetization-model-s`,
`data-subject-rights`, `gaming-restrictions`,
`processing-requirements-for-kids-teens-personal-data`, `trust-and-safety`,
`most-common-compliance-errors`, `upcoming-changes`.
