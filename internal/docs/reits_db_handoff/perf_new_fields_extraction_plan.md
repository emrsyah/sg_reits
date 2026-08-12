# `sgx_reit_performance` cross-check + new-fields extraction plan

_Created 2026-07-06. Prompted by the Evelyn sync (performance data + DPU cross-check) ahead of a
new extraction wave. This doc is the durable record of (a) the cross-check findings, (b) the
colleague questions answered, and (c) the plan for the fields being added. `memory://` is
unavailable in this project — this file is the record._

Scope note: cross-check + schema plumbing **and the extraction wave are now DONE** — see
"## WAVE EXECUTED" at the bottom. The reload regenerated property `id`s (§6); the 28 handkeyed
cockpit `purchase_date` edits were preserved (not deleted), now orphaned/un-joinable as accepted.

---

## 1. DPU — is it annualized?

**33 / 37 are full-year (12-month) declared DPU** (verified via `distribution_record` period spans
+ `flags`). Two are structurally sub-annual; two are zero:

| Symbol | DPU | Period | Status |
|---|---|---|---|
| **8C8U** | 1.739¢ | 25 Sep–31 Dec 2025 (97-day IPO stub) | NOT annualized — `flags` = `stub_ipo_period` ("Not a full year. P&L covers a partial period only."). |
| **CMOU** | 0.25 US¢ | 2H-2025 only (1 Jul–31 Dec) | NOT annualized — distributions suspended 2H2023–1H2025; resumed mid-year, so FY2025 DPU is 6-month by design. |
| BTOU, D5IU | 0 | — | Suspended (N/A). |

**Can they be computed/annualized? No — and shouldn't.** Both would require deriving from a
partial-period P&L (8C8U) or inventing income management chose not to distribute (CMOU) — violates
the no-derive rule and would mislead. Both already carry explanatory `flags`.

**Recommendation:** do not mutate the DPU value. If machine-readable filtering is wanted, add a
metadata column `dpu_period_months` (int) or `dpu_annualized` (bool) rather than changing DPU.
(Not yet added — pending decision.)

Internal validation: `net_distributable_income ÷ weighted_avg_shares_basic ≈ DPU` for all
non-retention REITs (e.g. CRPU 6.149 vs 6.138; J91U 21.916 vs 21.914). The gaps are exactly the
`disclosed_after_retention` cases (K71U computes 8.20 vs 5.23 paid → ~36% retained; CY6U's 10%
retention) — confirming Evelyn's DPU method-1/method-2 logic holds.

## 2. `distribution_record` → reverse-calc shareholder units

Possible (`units ≈ distribution_paid ÷ (dpu/100)`; `distribution_paid` is a total $, `dpu` is
per-unit cents) **but fragile.** Tested: lands cleanly (`distpaid/basic ≈ dpu`) for ~24 REITs
(8C8U 1.742 vs 1.739; CRPU 6.148 vs 6.138; CMOU exact 0.25) but **breaks on the 13
`not_disclosed_rollforward_only` / partial-record REITs** where `distribution_paid` and `dpu` sit
on different period bases — AJBU reverse-calcs 5.84¢ vs stored 10.381¢, C2PU 10.03¢ vs 15.29¢.

**Decision:** do NOT reverse-calc as source of truth. Units-in-issue is disclosed directly in every
AR — extract it (§5, Field B). Reverse-calc is a validation cross-check only.

## 3. Weighted-avg units (basic/diluted) — location

**Already extracted, all 37, in `sgx_reit_financial.income_stmt_metrics` (jsonb)** — keys
`weighted_avg_shares_basic` + `diluted_shares_outstanding`. Full coverage, no nulls. 23 have
basic==diluted, 14 differ (real dilution). **Not on the performance table** — a cross-table join is
needed for the DPU cross-check.

Naming note: `diluted_shares_outstanding` actually holds the *weighted-avg diluted* figure from the
EPU note (values track basic). A rename to `weighted_avg_shares_diluted` was proposed but
**deferred — no renaming for now** (user decision, 2026-07-06).

## 4. `purchase_date` on the portfolio table — CONFIRMED GAP → added

`sgx_reit_property` had no `purchase_date`; the extraction schema had no such key. The only existing
data is the **cockpit** (`reit_field_edit`): 28 `purchase_date` entries against `sgx_reit_property`
(all 26 of C38U's properties + 2 of A17U's), hand-keyed, mixed granularity (full dates `2023-02-02`
*and* bare years `2011`, `2022`). This is the "custom field from db" the user referred to.

**Done this session:** added `sgx_reit_property.purchase_date date` (schema.sql migration + live
DB). Extraction planned (§5, Field A) for **all 37 REITs** (no exclusions — user override
2026-07-06). Sources also accept an `acquisition_date` key (loader alias wired). Cockpit handkeyed
data is **not** harvested/loaded (user: "no need to load from the handkeyed, as long as it doesn't
replace the hand keyed"); adding the column does not touch `reit_field_edit` (verified: 28 edits
intact).

## 5. `number_of_shareholder_units` (units in issue) — CONFIRMED NEW → added

Trust-level closing units in issue — distinct from `weighted_avg_shares_basic` (an average, on
financial) and `number_of_unitholders` (headcount of holders). Was nowhere in the DB (except ME8U,
which happens to carry `units_in_issue` inside `balance_sheet_metrics`).

**Done this session:** added `sgx_reit_performance.number_of_shareholder_units numeric` (schema.sql
migration + live DB; user confirmed **trust-level**, and confirmed the **name**
`number_of_shareholder_units` over `units_in_issue`). Extraction planned (§5, Field B).

## 6. `aggregate_leverage` — is it gearing? verbatim? rename? (colleague Q)

Grounded against A17U primary source (`full.md`, p133): _"the total borrowings and deferred payments
(together the 'aggregate leverage') of a property fund should not exceed 50.0% of the Deposited
Property"_ (MAS CIS-Code Property Funds Appendix 6). ICR note (same page): trailing-12m adjusted
EBITDA ÷ (interest + borrowing fees + perp/hybrid distributions).

**a) Is it the gearing ratio?** Colloquially yes — CLAR uses them interchangeably (prose "gearing
39.0%"; table "Aggregate Leverage 39.0%"). **Not universally identical:** SET reports "aggregate
leverage 42.4% (MAS basis)" vs "net gearing 38.0% (EMTN)". *Net* gearing (net of cash) ≠ *aggregate*
leverage (gross).

**b) How does each REIT compute it? Comparable?** **Yes, comparable** — the headline is the MAS
regulatory metric (total borrowings + deferred payments ÷ Deposited Property; 50% cap), mandated for
every S-REIT. Our verbatim values are the same regulated figure. Minor scope nuances (proportionate
associate borrowings/assets included; ROU/derivatives excluded from "Adjusted Deposited Property").

**c) Rename to `gearing_ratio`?** **No — keep `aggregate_leverage`.** It's the precise regulatory
term; "gearing" is looser (could be net). Renaming risks conflation.

### Colleague's specific formula question
> _"differences between net gearing and gearing/gross — correlated with: `(total_debt − cash OR
> deferred payment) / total_assets`; we do not have cash so replace it with
> `gearing_ratio = total_debt/total_assets`?"_

**Yes, correlated in intent — but do NOT compute it to replace `aggregate_leverage`.**
- Aggregate leverage IS essentially a **gross** gearing (no cash netting): borrowings (+ deferred
  payments) ÷ deposited property. The colleague's `total_debt/total_assets` (gross, since no cash)
  is the same *family*. Net gearing is the cash-netted variant (SET: 38.0% net vs 42.4% aggregate).
- **But our data cannot reproduce it accurately.** We have no clean `total_debt`/`total_borrowings`
  field — only `total_liabilities` (includes payables, deferred tax, derivatives, lease
  liabilities). And `total_asset` ≠ MAS "Deposited Property". Computed `total_liabilities/total_asset`
  diverges from the verbatim `aggregate_leverage` by **mean 5.9 pts, max 17.2 pts** (CRPU 25.1 vs
  42.3; CY6U 39.6 vs 55.2; K71U 47.9 vs 39.8). So a computed proxy would be materially wrong.
- **Verdict:** keep extracting `aggregate_leverage` verbatim (it's the exact disclosed regulatory
  number; deriving violates the no-derive rule). If a computed cross-check is ever wanted, first add
  a verbatim `total_borrowings`/`gross_debt` field (extracted from the capital-management section),
  then compute — never from `total_liabilities`.

## 7. `interest_coverage_ratio` — EBIT/interest or verbatim?

**Verbatim; NOT EBIT/interest.** MAS CIS-Code definition (A17U p133): trailing-12m adjusted EBITDA
(excl. FV changes of derivatives/investment properties & FX) ÷ trailing-12m (interest expense +
borrowing-related fees + perp/hybrid distributions). Min 1.5x. **No change needed** (user confirmed).

---

## Schema changes applied this session (idempotent migrations, no reload)

| Table | Column | Type | Notes |
|---|---|---|---|
| `sgx_reit_property` | `purchase_date` | `date` | acquisition/purchase date; loader accepts `purchase_date` or `acquisition_date` |
| `sgx_reit_performance` | `number_of_shareholder_units` | `numeric` | closing units in issue (trust-level) |

Files touched: `db/schema.sql` (2 migration lines), `schema/models.py` (Property + Performance
fields), `scripts/db/load_supabase.py` (perf cols + property builder/cols). Verified: live DB has
both columns; models validate; existing A17U extractions re-validate 232/232; loader compiles.

## Extraction wave plan (GATED — not started)

**Field A — `purchase_date`** (property, all 37 REITs, no exclusions):
- Source: portfolio statement / property overview — "acquisition date", "date of acquisition",
  "completion date", "date of purchase". Capture as YYYY-MM-DD verbatim.
- **Year-only disclosures** (common for older assets): leave `purchase_date` null, note the year in
  `flags` (do NOT fabricate a day/month). ← confirm this handling.
- Do NOT derive from `valuation_date`. Never invent.

**Field B — `number_of_shareholder_units`** (performance, all 37):
- Source: Statement of Movements in Unitholders' Funds / "units in issue" note — closing units
  outstanding at period end, absolute count, verbatim. Do NOT reverse-calc from `distribution_paid`/DPU.

**Method:** per-report agents, batch ≤9 concurrent, "do ALL work yourself; no sub-agents". Main
agent verifies each proposed value vs source (page cite) before reload; re-query DB after reload to
confirm each landed. QC gate + validate in-process.

**Reload caveat (§6 issue):** populating these columns needs a property reload, which (delete-then-
insert) regenerates every property `id` → orphans cockpit `record_pk` edits. Already-observed: only
30 of 105 property field-edits currently resolve (75 already orphaned by Waves 9–11 reloads); the 28
`purchase_date` cockpit edits still resolve but would orphan on the next property reload. User
accepts orphaning (handkeyed rows are not deleted, just un-joinable). Optional hardening (deferred):
switch property loader to `INSERT … ON CONFLICT (symbol, financial_year, property_name) DO UPDATE`
(preserves `id`) + a stale-row sweep.

## Open decisions
1. `purchase_date` year-only handling: null+flag (proposed) vs a `purchase_date_raw`/precision column.
2. DPU annualization metadata column (`dpu_period_months`/`dpu_annualized`) — add or rely on `flags`.
3. Loader `id`-stability hardening (§6) — do it before the reload, or accept cockpit orphaning.
4. Go-ahead to spawn the extraction wave (Fields A + B, all 37).

## Reminder (user-requested)
Next after this: **cross-check `sgx_reit_property_transaction` (95 rows) against what SGX actually
discloses** (exchange acquisition/divestment announcements vs our txn rows).

Also: cockpit `reit_field_edit` grew 39 → 140 and `reit_record_verdict` 29 → 81 since the last
handoff (reviewers actively adding) — relevant to the parked "apply cockpit edits back" task.

---

## WAVE EXECUTED (2026-07-06)

All three fields extracted (9 agents, one patch JSON per REIT at `docs/new_fields_audit/<SYM>.json`),
verified, applied to `extracted/*/{properties,performance}.json`, QC-gated (259 files, 0 invalid),
and reloaded (37 reports committed). DB re-query confirms:

- `sgx_reit_property.purchase_date`: **1272 / 1653** filled (77%). Stored as-disclosed TEXT.
- `sgx_reit_performance.number_of_shareholder_units`: **37 / 37**.
- `sgx_reit_performance.dpu_period_months`: **37 / 37** — 8C8U = 3.2 (98-day IPO stub, source-verified
  p4), CMOU = 6 (2H-only post-suspension, source-verified p119), all others 12.

### Verification performed
- Structural: 0 property-name mismatches across all 37 (every property present).
- Plausibility: closing `number_of_shareholder_units` vs `income_stmt_metrics.weighted_avg_shares_basic`
  ratios all in 0.968–1.073 (expected closing-vs-average band; no outliers).
- Source spot-checks: C38U units 7,611,318k = exact (p105); A17U units from Note 17 (p175); both DPU
  stubs verified verbatim; sample purchase_dates matched source (A17U "4 Sep 2013"; C38U Westgate
  "2011"; MXNU 2025-06-20). ~1272 individual dates were not each eyeballed — structural + plausibility
  + targeted source checks were the bar.

### purchase_date coverage by REIT
| Symbol | filled/total | % |
|---|---|---|
| 8C8U.SI | 14/14 | 100% |
| A17U.SI | 232/232 | 100% |
| AJBU.SI | 4/26 | 15% |
| AU8U.SI | 17/18 | 94% |
| AW9U.SI | 32/32 | 100% |
| BMOU.SI | 0/6 | 0% |
| BTOU.SI | 7/9 | 78% |
| BUOU.SI | 114/114 | 100% |
| C2PU.SI | 74/75 | 99% |
| C38U.SI | 26/26 | 100% |
| CMOU.SI | 13/13 | 100% |
| CRPU.SI | 4/4 | 100% |
| CY6U.SI | 4/18 | 22% |
| D5IU.SI | 29/29 | 100% |
| DCRU.SI | 1/11 | 9% |
| DHLU.SI | 3/19 | 16% |
| HMN.SI | 5/105 | 5% |
| J69U.SI | 11/12 | 92% |
| J85.SI | 23/23 | 100% |
| J91U.SI | 71/73 | 97% |
| JYEU.SI | 0/5 | 0% |
| K71U.SI | 15/15 | 100% |
| M1GU.SI | 18/18 | 100% |
| M44U.SI | 197/197 | 100% |
| ME8U.SI | 100/100 | 100% |
| MXNU.SI | 3/148 | 2% |
| N2IU.SI | 18/19 | 95% |
| O5RU.SI | 28/28 | 100% |
| ODBU.SI | 1/22 | 5% |
| OXMU.SI | 13/13 | 100% |
| P40U.SI | 7/9 | 78% |
| Q5T.SI | 1/13 | 8% |
| SET.SI | 104/104 | 100% |
| T82U.SI | 0/12 | 0% |
| TS0U.SI | 6/6 | 100% |
| UD1U.SI | 45/53 | 85% |
| XZL.SI | 32/32 | 100% |

Zero-coverage (AR discloses no per-property acquisition date): **BMOU, JYEU, T82U**. Low-coverage
(only recent acquisitions dated; seed/IPO assets undated): MXNU 3/148, HMN 5/105, DHLU 3/19,
ODBU 1/22, Q5T 1/13, DCRU 1/11, CY6U 4/18, AJBU 4/26. These are genuine non-disclosures, not misses.

### Known caveats (follow-up candidates, not blocking)
1. **Mixed `purchase_date` formats** — as-disclosed text is heterogeneous: full ISO ("2013-09-04"),
   verbatim ("4 Sep 2013"), month-year ("2025-01"), bare year ("2011"), and a few compound
   multi-date strings (staged/multi-tranche assets, e.g. A17U/M44U/K71U). A later normalization pass
   could canonicalize, but risks DD/MM ambiguity — deferred.
2. **`number_of_shareholder_units` basis varies slightly by REIT** — most agents took closing "units
   in issue" (excl. to-be-issued); a few took "issued and to be issued". Differences are <0.3% and
   each patch documents its choice. Standardize to issued-only if strict comparability is needed.
3. **Cockpit orphaning (accepted)** — the reload regenerated property `id`s; the 28 handkeyed
   `purchase_date` cockpit edits (+ other property edits) survive in `reit_field_edit` but their
   `record_pk` no longer resolves. Loader `ON CONFLICT … DO UPDATE` id-stability fix remains the
   optional hardening if cockpit round-tripping is later wanted.

### Files
Agent patches: `docs/new_fields_audit/*.json` (37). Extraction JSON + DB updated. Uncommitted.
