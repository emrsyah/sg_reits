# SGX REIT Extraction — Progress Tracker

Single source of truth for pipeline state per annual report. Stages:
**Parsed** → **Extracted** → **Guardchecked** (deterministic gates) → **Audited** (forensic LLM, correctness vs source).

Last updated: 2026-06-18.

> **FY2025 scale run in progress** (chunks of 8). Schema gained 7 as-disclosed comparison KPIs
> on `performance` (aggregate_leverage, interest_coverage_ratio, cost_of_debt,
> weighted_avg_debt_maturity, nav_per_unit, wale, portfolio_occupancy) — commit before batch 1.
> **Batch 1 (2026-06-18): the 9 already-parsed trusts re-extracted fresh** (discovery-first,
> reit-extract-hybrid, one agent per AR) — done: AJBU, AU8U, AW9U, BTOU, C38U, DHLU, HMN, J69U
> (M44U was already the pilot). All 8 PASS both gates (0 fail). KPIs captured where disclosed;
> 3 nulls are genuine non-disclosures (AW9U/AJBU debt-maturity-in-years, HMN WALE = MAS waiver).
> J69U sponsor (Frasers Property) now present; AJBU sponsor=Keppel. Income mis-bucketing caught
> + fixed in every report where present. Still TODO this batch: UD1U (parsed, not yet re-done).

## Legend

- **Parsed** — Datalab balanced parse → `parsed_reports_datalab/<dir>/full.md` (page-anchored `<!-- PAGE N -->`).
- **Extracted** — discovery-first hybrid adapter pipeline (`reit-extract-hybrid`, Sonnet) → 8 JSON files in `extracted/<SYM>.SI_FY2025/`. "A/B promoted" = round-2 blind discovery-first re-extraction was run and promoted over the round-1 output.
- **Guardchecked** — deterministic, free, no PDF read: `validate_schema.py` (Pydantic vs `schema/models.py`) + `check_extraction.py` (reconciliations, incl. the **revenue tie-out** rule added 2026-06-15: Σ(income_components revenue) must equal `performance.gross_revenue`). Status = `PASS (fail/warn/info)`. A free plausibility pass (`scripts/review/sanity_scan.py`) also exists.
- **Audited** — independent forensic LLM auditor (`reit-audit` skill, Opus) vs the source report → `reviews/<SYM>_verification.md`. This is the ONLY layer that catches wrong-but-plausible values, false "structurally absent" reasons, and cross-file contradictions (see memory: completeness ≠ correctness).

## Status table

| # | Symbol | Trust | Sub-sector | Parsed | Extracted | Guardchecked | Audited |
|---|--------|-------|-----------|--------|-----------|--------------|---------|
| 06 | HMN.SI  | CapitaLand Ascott Trust          | Hospitality  | ✅ Datalab | ✅ A/B promoted | ✅ PASS (0f/5w) | ✅ MINOR ISSUES — `reviews/HMN_verification.md` (5 fixes applied, commit 86118e5) |
| 07 | AU8U.SI | CapitaLand China Trust           | Diversified  | ✅ Datalab | ✅ hybrid       | ✅ PASS (0f/2w/2i) | ✅ MINOR ISSUES — `reviews/AU8U_verification.md` (0 value errors; 5 provenance/label fixes pending) |
| 09 | C38U.SI | CapitaLand Integrated Commercial | Diversified  | ✅ Datalab | ✅ hybrid       | ✅ PASS (0f/1w/2i) | ✅ MINOR ISSUES — `reviews/C38U_verification.md` (CapitaSpring GR basis + 6 fixes pending) |
| 12 | DHLU.SI | Daiwa House Logistics Trust      | Industrial   | ✅ Datalab | ✅ A/B promoted | ✅ PASS (0f/2w/2i) | ✅ MINOR ISSUES — `reviews/DHLU_verification.md` (distribution_record + 4 fixes pending) |
| 17 | AW9U.SI | First REIT                       | Healthcare   | ✅ Datalab | ✅ hybrid       | ✅ PASS (0f/1w/1i) | ✅ MINOR ISSUES — `reviews/AW9U_verification.md` (4 fixes applied, commit cd8f944) |
| 18 | J69U.SI | Frasers Centrepoint Trust        | Retail       | ✅ Datalab | ✅ A/B promoted | ✅ PASS (0f/0w/1i) | ✅ MINOR ISSUES — `reviews/J69U_verification.md` (sponsor OK; finance_income FIXED + 6 pending) |
| 20 | UD1U.SI | IREIT Global                     | Diversified  | ✅ Datalab | ✅ A/B promoted | ✅ PASS (0f/1w/2i) | ✅ MINOR ISSUES — `reviews/UD1U_verification.md` (add Sofidy PM + 3 fixes pending) |
| 21 | AJBU.SI | Keppel DC REIT                   | Data Centre  | ✅ Datalab | ✅ hybrid       | ✅ PASS (0f/1w/1i) | ✅ MINOR ISSUES — `reviews/AJBU_verification.md` (sponsor=Keppel OK; cashflow-hedge + 5 pending) |
| 26 | BTOU.SI | Manulife US REIT                 | Office       | ✅ Datalab | ✅ hybrid       | ✅ PASS (0f/2w)    | ✅ MINOR ISSUES — `reviews/BTOU_verification.md` (fixes applied, commit cd8f944) |
| 28 | M44U.SI | Mapletree Logistics Trust        | Industrial   | ✅ Datalab | ✅ hybrid       | ✅ PASS (0f/0w/3i) | ✅ MINOR ISSUES — `reviews/M44U_verification.md` (sponsor OK; interest_income FIXED; +txn table & 4 pending) |

Legend: ✅ done · 🔄 running · ⬜ not done. Gate counts = `fail/warn/info` from `check_extraction.py`.

## Notes

- **All 10 forensically audited** (2026-06-15) — every one graded **MINOR ISSUES**: hard numbers
  solid, no fabricated values. All 10 pass both gates with 0 failures. Gates prove *structure &
  reconciliation*; only the forensic audit proves *correctness*.
- **The income mis-bucketing bug is systemic: found in 8 of 10 reports** (all except DHLU, UD1U) —
  a below-NPI income line (finance/interest/investment/fx) tagged `statement="revenue"`. Found in
  HMN, AW9U, BTOU (audit) → AU8U, C38U, AJBU (gate) → **J69U (finance_income 624k), M44U
  (interest_income 2,648k)** (full audits). **All 8 fixed** (`revenue`→`adjustment`), source-cited.
  The AU8U/C38U/AJBU fixes were additionally SOURCE-VERIFIED (AU8U p95; AJBU p103/Note 20; C38U
  p106/Notes 21,23,24) after first being done by arithmetic — lesson: arithmetic that closes a
  tie-out is a *signal*, not a fix; confirm against the report.
- **Gate-tolerance lesson (2026-06-15):** the revenue-tie-out check first used a 0.5% relative
  tolerance and MISSED J69U/M44U (their gaps were under 0.5% of gross_revenue). A real mis-bucket
  is a whole line item, and gross_revenue vs income_components are both audited figures that should
  tie near-exactly — so the tolerance is now a flat **50k absolute**. Re-verified: catches J69U/M44U,
  all 10 still pass post-fix.
- **Fixes APPLIED so far:** HMN (5), AW9U (4), BTOU (4), AU8U/C38U/AJBU (income reclass),
  J69U + M44U (income reclass). **Remaining audit fixes are PENDING user review** — mostly
  provenance (`source_page`), null-reason rewordings, missing `_notes.inferred[]` flags, a few
  value items (C38U CapitaSpring gross_revenue basis, DHLU distribution_record, M44U
  property_transactions table) and judgment calls (portfolio_value basis). See each
  `reviews/<SYM>_verification.md` for the per-report fix list.
- **HMN audit found 4 discrepancies + 3 omissions** despite passing all gates — the canonical
  evidence that gates ≠ correctness (sponsor mislabel, income mis-bucketing, portfolio_value
  contradiction). All fixed. See `reviews/HMN_verification.md`.
- **`reviews/AJBU.SI_FY2025.json` and `reviews/M44U.SI_FY2025.json`** are partial *manual*
  review notes from the Flask cockpit (`scripts/review/app.py`), not forensic audits — both flag
  an unresolved "where is the sponsor" question. AJBU/M44U still need a real audit.
- **Recurring bug classes the auditor targets:** (a) false "structurally absent" reasons for
  fields disclosed on a narrow basis; (b) cross-file contradictions (`_notes` vs `profile` vs
  `performance`); (c) statement mis-bucketing that breaks a revenue tie-out; (d) unflagged
  derived/back-calculated values.
- **J69U known pattern:** sponsor (Frasers Property Ltd) was dropped in discovery-first because
  the agent built `profile` from only the top-ranked Corporate Information page and didn't merge
  the front-matter Trust Structure pages — a profile-merge discipline miss, not a tooling
  failure. Mitigation (profile-merge enforcement + sponsor-present gate) pending before scale-up.
- **Endgame:** scale-up prep → ~20 more ARs → DB load into `sgx_reit_*` tables.
