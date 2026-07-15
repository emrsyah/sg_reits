# Adjustment Tracker — data-quality workstream

Master index of every adjustment we intend to make to the `sgx_reit_*` data/schema. One row per
adjustment. Each links to its **detail doc** (or an outline section until it gets its own doc).
Work these one by one; tick `[x]` when fully executed (code + DB + verified).

**Type legend**
- **SCHEMA** — changes `schema/models.py` + DB columns + `load_supabase.py` (add/remove/rename field).
- **VALUE** — changes only *which disclosed line a value is read from* (re-source / correct); no schema change.
- **FLAG** — changes an enum / flag vocabulary.
- **MIGRATE** — moves existing data between fields/tables; no new concept.
- **RE-EXTRACT** — a broader re-run of an extractor across many REITs.
- **DECISION** — a convention/policy call; no code until decided (may then spawn SCHEMA/VALUE work).

**Status legend:** `DRAFT` (proposal written) · `PENDING` (awaiting emirsyah) · `BLOCKED` (needs
external input/rules) · `READY` (actionable now, no blocker) · `RESOLVED` (decided, no action) ·
`DONE` (executed + verified).

**Standing rules (apply to every row):** as-disclosed only, never plug a failed check
(REFERENCE §0.8); FROZEN REITs (C38U A17U N2IU M44U ME8U J69U T82U K71U BUOU C2PU) need
case-by-case approval for FY2025 edits; MAIN agent owns all JSON+DB writes.


## Planned workstreams (sequencing)
Order (emirsyah 2026-07-09): **schema changes first, lock the final shape; VALUE (source) passes
after.**
1. **`sgx_reit_property_transaction`** — **SCHEMA pass, ACTIVE.** New per-deal source = SGX "Asset
   Acquisitions and Disposals" regulatory announcements (plan + completion), not the AR. Lock the
   column delta (see #11 + proposal). Do this **first** because it's the only schema change of the
   three.
2. **`sgx_reit_financial`** — VALUE pass only: **no schema change**, adjust *where each figure is
   extracted from* (correct source line/statement per field). After 1.
3. **`sgx_reit_performance`** — VALUE pass: adjust *where to extract what* per field. (The
   distribution rollforward #1 is the one exception — it also adds columns.) After 1.

---

## Open adjustments

| # | Adjustment | Type | Scope | Status | Detail |
|---|---|---|---|---|---|
| 1 | **Distribution rollforward split** — add A `distributable_income_opening` / P `distribution_cash_paid` / E `distributable_income_closing`; keep B `net_distributable_income` + `distribution_paid`; guard `A+B-P=E` (+ cross-year `E(N)=A(N+1)`). "available" (A+B) NOT stored — not disclosed verbatim | SCHEMA + VALUE + FLAG | all 37 | PENDING (emirsyah) | [distribution-fields-proposal.md](distribution-fields-proposal.md) |
| 2 | **Rollforward source rule** — A/B/P/E read verbatim from the audited **Distribution Statement only** (never highlights/commentary/manual-input/chartbook) | VALUE (rule) | all 37 | PENDING (part of #1) | [distribution-fields-proposal.md §Canonical source](distribution-fields-proposal.md) |
| 3 | **`distribution_paid` rename?** -> `distribution_declared_for_year` (value unchanged) | SCHEMA (rename only) | all 37 | PENDING (emirsyah) | [distribution-fields-proposal.md §Decision](distribution-fields-proposal.md) |
| 4 | **`distribution_basis` -> slim flag** — drop redundant `disclosed_after_retention`/`full_payout`; keep suspended/net-loss/rollforward-only/cash-incl-capital/null-reason | FLAG | all 37 | PENDING (part of #1) | [distribution-fields-proposal.md §Slimmed flag](distribution-fields-proposal.md) |
| 5 | **Attribution-sign normalization** — one convention (components-positive vs deductions-negative); fix known M44U FY2025 negative perpetual/minorities (-24,231/-1,125) | DECISION -> VALUE | corpus; M44U FY2025 first | PENDING (emirsyah; freeze) | [outline.md §4](outline.md) |
| 6 | **T82U `revenue_breakdown` gap** — read full Note 20 to resolve ~1,471 gap (462,085 vs 463,556); backfill only if it ties | VALUE | T82U FY2024 | READY | [outline.md §8a](outline.md) |
| 7 | **`_notes.inferred[]` migration** — move this session's inference flags out of `performance.flags` into `_notes.inferred[]`; reload `sgx_reit_notes` | MIGRATE | 4 REITs (ME8U/T82U/C2PU + ...) | PENDING (emirsyah) | [outline.md §8a](outline.md) |
| 8 | **Profile-to-DB / which-year-wins** — profile is symbol-singleton, no `financial_year`; decide whether FY2024 profile improvements (K71U +2 mgrs) overwrite the DB singleton | DECISION (maybe SCHEMA) | corpus | PENDING (emirsyah) | [outline.md §8a](outline.md) |
| 9 | **ICR basis convention** — adjusted vs headline/MAS (M44U 3.1/3.7, ME8U 4.3/4.6, N2IU 2.9/3.0); lock one | DECISION -> VALUE | corpus | PENDING (emirsyah) | [outline.md §8a](outline.md) |
| 10 | **ICR / portfolio_value basis review** — corpus-wide consistency once #9 + portfolio-total convention locked | VALUE (review) | all 37 | PENDING (after #9) | [outline.md §8a](outline.md) |
| 11 | **`sgx_reit_property_transaction` SCHEMA** (schema-first, ACTIVE) — **AR-first, SGX announcement top-up.** Rename `gross_sale_price`->`sale_price`; add `deal_id`, `gain_loss_pct`, `gain_basis`, `valuation_date`, `announced_date`, `completed_date`, `source_type`, `announcement_refs` (jsonb); DROP `transaction_cost` (0% fill); `net_sale_proceeds` disclosed-only. Per-field precedence, merge deals via `deal_id`. (no valuer/counterparty_type) | SCHEMA | corpus | DRAFT (emirsyah to lock) | [property-transaction-schema-proposal.md](property-transaction-schema-proposal.md) · [outline.md §5](outline.md) |
| 12 | **Property-txn re-extract + subsequent-events/NCI sweep** (VALUE) — after #11 schema locks: fetch/parse SGX announcements, backfill incl. NCI-booked + subsequent-event deals | RE-EXTRACT | corpus | BLOCKED (on #11) | [property-transaction-schema-proposal.md §Out of scope](property-transaction-schema-proposal.md) · [outline.md §5](outline.md) |
| 13 | **§0 T82U 4 JV rows** — income-contribution only (not NPI); keep NPI null + `_notes` (default) or populate+flag | DECISION | T82U | PENDING (default = keep-null) | [outline.md §0](outline.md) · [property-notes-synthesis.md §C](property-notes-synthesis.md) |
| 14 | **§0 C38U Bugis+ / Bukit Panjang Plaza** — only combined "Other Assets" 63.4m disclosed; keep null (default) | DECISION | C38U | PENDING (default = keep-null) | [outline.md §0](outline.md) |
| 15 | **Mapletree manual-input reconciliation** — start-year vs end-year FY label for Mar-FYE trusts; confirm prod handling | DECISION | M44U/ME8U/N2IU | PENDING (confirm w/ Evelyn/emirsyah) | [outline.md §4](outline.md) |
| 16 | **Frozen-REIT `market_valuation_currency` relabel** — loader-bug mv_ccy mislabel fixed for 10 non-frozen; frozen rows deferred under freeze (A17U 137, M44U 17, ME8U 1, J69U 1, BUOU 1, C2PU 1, N2IU 1) | VALUE | 7 frozen REITs | PENDING (freeze) | [property-notes-synthesis.md §A/§B](property-notes-synthesis.md) |
| 17 | **Drop `original_*` / `local_*` property fields** (item9) — emirsyah: likely drop (covered by per-figure `*_currency`; local fields mostly null); flag-only for now | SCHEMA | corpus | PENDING (emirsyah) | [property-notes-synthesis.md §C](property-notes-synthesis.md) |

## Resolved / no-action

| # | Adjustment | Type | Outcome | Detail |
|---|---|---|---|---|
| R1 | **Delete `adjusted_distributable_income`?** | SCHEMA | **KEEP** — orthogonal (fee-settlement axis, diluted-DPU cross-check), not subsumed by rollforward | [distribution-fields-proposal.md §adjusted_distributable_income](distribution-fields-proposal.md) |
| R2 | **NDI convention** | VALUE | DONE — before-retention, locked in models.py; all 37 normalized | [outline.md §3](outline.md) |
| R3 | **EPU placement** | SCHEMA | RESOLVED — leave EPU derivable from components (no field) | [outline.md §2](outline.md) |
| R4 | **§1 property table pass** (non-frozen) — gla/gfa null fix, area_unit report-wide, loader mv_ccy bug + 56-row relabel, purchase/IPO dates, lease-term flags | VALUE + SCHEMA | 39-REIT set | DONE (2026-07-08) | [property-notes-synthesis.md](property-notes-synthesis.md) · [outline.md §1](outline.md) |
| R5 | **FY2024 full record build** (10 frozen REITs) — extract + audit + fix + upsert, Rounds 1-3 | VALUE | 10 frozen | DONE (2026-07-09) | [outline.md §8](outline.md) |

---

## How to use
1. Pick a row (prefer READY, or a PENDING once emirsyah decides).
2. Open its detail doc; if the detail lives only in an outline section and the change is non-trivial,
   spin it into its own `*-proposal.md` and update the link here.
3. Execute (code + DB), verify, then tick `[x]` and move the row to a "Done" note in the detail doc
   and in `outline.md`.
