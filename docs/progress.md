# SGX REIT Extraction — Progress Tracker

Single source of truth for pipeline state per annual report. Stages:
**Parsed** → **Extracted** → **Guardchecked** (deterministic gates) → **Audited** (forensic LLM, correctness vs source).

Last updated: 2026-06-15.

## Legend

- **Parsed** — Datalab balanced parse → `parsed_reports_datalab/<dir>/full.md` (page-anchored `<!-- PAGE N -->`).
- **Extracted** — discovery-first hybrid adapter pipeline (`reit-extract-hybrid`, Sonnet) → 8 JSON files in `extracted/<SYM>.SI_FY2025/`. "A/B promoted" = round-2 blind discovery-first re-extraction was run and promoted over the round-1 output.
- **Guardchecked** — deterministic, free, no PDF read: `validate_schema.py` (Pydantic vs `schema/models.py`) + `check_extraction.py` (reconciliations, incl. the **revenue tie-out** rule added 2026-06-15: Σ(income_components revenue) must equal `performance.gross_revenue`). Status = `PASS (fail/warn/info)`. A free plausibility pass (`scripts/review/sanity_scan.py`) also exists.
- **Audited** — independent forensic LLM auditor (`reit-audit` skill, Opus) vs the source report → `reviews/<SYM>_verification.md`. This is the ONLY layer that catches wrong-but-plausible values, false "structurally absent" reasons, and cross-file contradictions (see memory: completeness ≠ correctness).

## Status table

| # | Symbol | Trust | Sub-sector | Parsed | Extracted | Guardchecked | Audited |
|---|--------|-------|-----------|--------|-----------|--------------|---------|
| 06 | HMN.SI  | CapitaLand Ascott Trust          | Hospitality  | ✅ Datalab | ✅ A/B promoted | ✅ PASS (0f/5w) | ✅ MINOR ISSUES — `reviews/HMN_verification.md` (5 fixes applied, commit 86118e5) |
| 07 | AU8U.SI | CapitaLand China Trust           | Diversified  | ✅ Datalab | ✅ hybrid       | ✅ PASS (0f/2w/2i) | ⬜ not yet |
| 09 | C38U.SI | CapitaLand Integrated Commercial | Diversified  | ✅ Datalab | ✅ hybrid       | ✅ PASS (0f/1w/2i) | ⬜ not yet |
| 12 | DHLU.SI | Daiwa House Logistics Trust      | Industrial   | ✅ Datalab | ✅ A/B promoted | ✅ PASS (0f/2w/2i) | ⬜ deterministic scan only |
| 17 | AW9U.SI | First REIT                       | Healthcare   | ✅ Datalab | ✅ hybrid       | ✅ PASS (0f/1w/1i) | ✅ MINOR ISSUES — `reviews/AW9U_verification.md` (4 disc / 2 omit; fixes pending) |
| 18 | J69U.SI | Frasers Centrepoint Trust        | Retail       | ✅ Datalab | ✅ A/B promoted | ✅ PASS (0f/0w/1i) | ⬜ not yet |
| 20 | UD1U.SI | IREIT Global                     | Diversified  | ✅ Datalab | ✅ A/B promoted | ✅ PASS (0f/1w/2i) | ⬜ deterministic scan only |
| 21 | AJBU.SI | Keppel DC REIT                   | Data Centre  | ✅ Datalab | ✅ hybrid       | ✅ PASS (0f/1w/1i) | ⬜ partial manual notes only |
| 26 | BTOU.SI | Manulife US REIT                 | Office       | ✅ Datalab | ✅ hybrid       | ✅ PASS (0f/2w)    | ✅ MINOR ISSUES — `reviews/BTOU_verification.md` (4 disc / 2 omit; fixes pending) |
| 28 | M44U.SI | Mapletree Logistics Trust        | Industrial   | ✅ Datalab | ✅ hybrid       | ✅ PASS (0f/0w/3i) | ⬜ not yet |

Legend: ✅ done · 🔄 running · ⬜ not done. Gate counts = `fail/warn/info` from `check_extraction.py`.

## Notes

- **All 10 pass both gates with 0 failures** (verified 2026-06-15). Warnings are mostly known
  narrow-disclosure / scope items, not errors. Gates prove *structure & reconciliation*, NOT
  *correctness* — only the forensic audit does that.
- **Audit is paid LLM spend the user gates** → run on a sample / high-risk reports (stapled,
  multi-currency, operator/master-lease), not blanket. Currently auditing the two highest-risk
  un-audited reports: **BTOU** (USD, distributions possibly halted, held-for-sale traps) and
  **AW9U** (healthcare, master-lease, IDR multi-currency).
- **The income mis-bucketing bug is systemic: found in 5 of 10 reports.** The forensic audits
  caught it in HMN, AW9U, BTOU; the new revenue-tie-out gate check then caught it in **AU8U**
  (finance_income + fx_gain_realised) and **C38U** (interest_and_other_income + investment_income)
  and re-confirmed **AJBU** (finance_income). All 5 fixed by reclassifying the below-NPI income
  line(s) `revenue`→`adjustment` — the audited `gross_revenue` uniquely determines the correct
  split per report. **AU8U/C38U/AJBU got only this one fix via the gate; they are NOT yet
  forensically audited** (other bug classes may remain).
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
