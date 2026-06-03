# Regulatory Watch — Change Report

**Artefact:** {{artefact_name}}
**Run date:** {{run_date}}
**Source of truth:** neimo. ({{sections_and_editions_searched}}){{web_confirmations}}
**Staleness summary:** {{n_checkable}} checkable rows ({{n_synthetic}} synthetic-jurisdiction rows excluded) · oldest {{oldest_date}} · {{n_stale}} stale (> {{stale_months}} mo, {{stale_pct}}% of checkable)

---

## Action required ({{n_action}})

| Control ID | Jurisdiction | Class | What changed | Source | Suggested control edit |
|---|---|---|---|---|---|
{{action_rows}}

> Class cell carries a `neimo.-lag` flag where neimo. is staler than the web-confirmed status (e.g. Bill → Act), or an `artefact-lag` flag where the register is staler than neimo. (e.g. an instrument cited at draft stage that neimo. shows in force). Multi-stage dates (Royal Assent / commencement / enforcement-from) are listed separately in the "What changed" cell, never collapsed.

## Confirmed — refresh date only ({{n_confirmed}})

{{confirmed_list}}

## Unverified — neimo. has no coverage; route to human review ({{n_unverified}})

{{unverified_list}}

---

## Appendix — citations

{{citations}}

**Verification note:** every finding above traces to a neimo. tool result in this run. Web-confirmed findings additionally cite the regulator/legislation URL, with each date labelled to its source. {{lag_note}} No regulatory fact was drawn from model memory; where neimo. returned empty, the row is flagged UNVERIFIED rather than NO CHANGE.
