# Schema review — task tracker

**Source:** meeting recap, 2026-07-30. Items are stated as raised in the meeting.
**Scope:** prod data.

Status: `[ ]` open · `[x]` done · `[~]` decided, not yet applied · `[?]` needs decision

Decisions are recorded in `findings-and-recommendations.md` § Conclusions.

---

## sgx_reit_profile

- [x] No issue.

---

## sgx_reit_property

- [~] `gross_lettable_area`, `net_lettable_area`, `gross_floor_area`: how many of these are null in each.
- [~] `effective_date`, `lease_term_years`, `lease_expiry_date`: drop either effective or expiry date.

---

## sgx_reit_top_tenant and sgx_reit_trade_mix

- [ ] `pct_basis`: what are the unique values? we can work from there.

---

## sgx_property_transaction

- [ ] Remove all status that is not "completed".
- [~] `transaction_type` and `transaction_price` (drop `purchase_price` and `sale_price`).
- [~] What is `interest_pct`? Drop if not important.
- [~] Drop `announced_date` and `transaction_date`. Don't see a value here.
- [~] `gain_basis` — is this necessary?
- [~] `valuation_date` and `carrying_value` should be sufficient. Drop `valuation`.
- [~] Where is `gain_on_divestment` be derived from?
  - [x] `transaction_price` − `sgx_reit_property.purchase_price`
  - [x] `transaction_price` − `carrying_value`

> Resolved 2026-07-31 — target schema agreed in `transaction-target-schema-AGREED.md`.
> Divestments are recorded as `gain_loss_pct` + `reference_value` + `reference_basis` +
> `interest_pct` + `deal_id`; acquisitions as `purchase_price` + `completed_date`.

Open work arising:

- [ ] P0 — re-promote to fix 61 stale `gain_loss_pct` rows in prod (dev is correct).
- [ ] Populate `reference_value` / `reference_basis` across 136 divestments.
- [ ] Resolve ~39 rows whose dollar gain reconciles to no formula.
- [ ] Backfill `deal_id` on aggregate deals; make slug generation deterministic (TS0U Lippo Plaza).
- [ ] Promote `deal_id` to prod.
- [ ] Source the 45 divestments missing a percentage or a reference.
- [ ] Add Invariant 1 (internal) + Invariant 2 (cross-table vs `sgx_reit_property`) as gates.
- [ ] Confirm with Evelyn: reported P&L gain leaves the table on equity sales (see doc).

---

## sgx_reit_performance

- [ ] `number_of_shareholder_units` should never be NULL.
- [ ] `distribution_record`: fix data structure. `period_start`, `period_end`, remove `ex_date`, `pay_date`.
- [ ] Drop `distribution_period_months`.
- [ ] `portfolio_occupancy` and `interest_coverage_ratio` are %.
- [ ] `distribution_paid` is from distribution statement, we are using this. Drop `distribution_cash_paid`.
- [ ] `net_distributable_income` — need to clarify what is this.
- [ ] `adjusted_distributable_income` + `distributable_income_opening` = `net_distributable_income`
- [ ] `net_distributable_income` − `distribution_paid` − `distributable_income_closing` = upcoming distribution amount
- [ ] `distribution_pool_other_movements`: confirm that this is a standalone and how is this used.

---

## sgx_reit_top_tenant / sgx_reit_trade_mix — `pct_basis` decision (2026-07-31)

`pct_basis` is to be **shown on the front end**, with the number of variations capped.

**Canonical values to keep (6):**
`headline_rent` · `annualised_rent` · `npi` · `asset_value` · `gross_rental_income` · `gross_revenue`

**Mappings:**

| from | to |
|---|---|
| `base_rental_income` | `gross_rental_income` |
| `cash_rental_income` | `gross_revenue` |
| `committed_gross_rent` | `gross_rental_income` |
| `apartment_rental_income` | `gross_rental_income` |
| `rental_income` | **remove** |
| `revenue` | **remove** |

### Current state in prod (surveyed 2026-07-31)

`sgx_reit_top_tenant` 752 rows / 13 distinct · `sgx_reit_trade_mix` 509 rows / 12 distinct.

| value | top_tenant | trade_mix | disposition |
|---|---|---|---|
| `gri` | 395 | 305 | **NOT IN THE LIST — see Q1** |
| `rental_income` | 105 | 50 | remove — **see Q2** |
| `gross_revenue` | 90 | 41 | keep |
| `cash_rental_income` | 40 | 22 | → `gross_revenue` |
| `npi` | 20 | — | keep |
| `committed_gross_rent` | 20 | 16 | → `gross_rental_income` |
| `headline_rent` | 20 | 20 | keep |
| `rental_income (corporate accounts ... Ascott management contracts only)` | 11 | 20 | **see Q3** |
| `apartment_rental_income (corporate accounts ... Ascott management contracts only)` | 11 | — | → `gross_rental_income`, **see Q3** |
| `gri_logistics_industrial` | 10 | 5 | **see Q4** |
| `gri_commercial` | 10 | 11 | **see Q4** |
| `office_gri` | 10 | 10 | **see Q4** |
| `retail_gri` | 10 | 7 | **see Q4** |
| `asset_value` | — | 2 | keep |

`base_rental_income` and `revenue` do not appear in prod — the mapping for them is forward-looking only.

### Open questions blocking the rewrite

- [ ] **Q1 — `gri` is the largest bucket (700 rows, ~55%) and is not in the list.** Almost certainly
      an abbreviation of gross rental income. Confirm `gri` → `gross_rental_income`.
- [ ] **Q2 — `rental_income` is 155 rows across ~8 REITs** (AJBU, AW9U, CY6U, DCRU, Q5T, UD1U, A17U…).
      "Remove" needs a target: re-map to `gross_rental_income`, or drop the label and leave
      `pct_basis` null, or drop the rows? Deleting the label without a target leaves 155 rows with a
      percentage whose denominator is unknown.
- [ ] **Q3 — HMN's two bases carry a meaningful qualifier**: *"(corporate accounts of properties
      under Ascott management contracts only)"*. The percentages cover only part of the portfolio.
      Collapsing to a bare `gross_rental_income` loses that scope caveat — keep it in a separate
      note/scope field, or accept the loss?
- [ ] **Q4 — the four segment variants must NOT be collapsed** (63 rows, BUOU + T82U). Verified in
      `pct_basis-verification.md`: T82U's AR states *"20.0% of Suntec REIT's total **office** gross
      rental income"* and separately *"15.0% of … total gross **retail** income"* — these are
      **separate denominators, each summing to ~100%**. Flattening them to one
      `gross_rental_income` would make the percentages incomparable and appear to double-count.
      Decide: keep as distinct enum values, or add a `basis_segment` column
      (`office` / `retail` / `commercial` / `logistics_industrial`) alongside the canonical basis.

### Also outstanding on these two tables

- [ ] Apply the 19 mislabelled-row fixes from `pct_basis-verification.md`.
- [ ] Backfill Q5T FY2024 and XZL FY2024.
- [ ] `revenue_pct` / `pct` are already fractions (0–1) — no change under the percentage-normalization
      item below.

---

## Also raised

- [ ] Naming — make sure of what the data is and the naming.
- [ ] Dropping some columns and restructuring/flattening some columns.
- [ ] **All percentage columns to be normalized to 0–1 (fraction), not 0–100.**

### Percentage normalization — current state (surveyed 2026-07-31)

Prod is currently split. Already **fraction (0–1)**, no change needed:

| column | n | range |
|---|---|---|
| `property.occupancy_rate` | 3016 | 0 – 1 |
| `property.ownership` | 2757 | 0.1 – 1 |
| `top_tenant.revenue_pct` | 749 | 0.001 – 0.934 |
| `trade_mix.pct` | 509 | 0.001 – 1 |
| `property_transaction.interest_pct` | 18 | 0.0051 – 1 |

Still **percent (0–100)**, to convert:

| column | n | range |
|---|---|---|
| `performance.aggregate_leverage` | 74 | 22.1 – 60.8 |
| `performance.portfolio_occupancy` | 70 | 67.7 – 100 |
| `performance.cost_of_debt` | 73 | 1.48 – 8.54 |
| `property_transaction.gain_loss_pct` | 130 | see conflict note below |

- [ ] Convert the four above; add them to `FRACTION_FIELDS` in `promote_final_to_prod.py:57`
      (which already performs this transform for the first five).
- [ ] `performance.portfolio_occupancy` (percent) and `property.occupancy_rate` (fraction) are the
      **same concept stored two ways** — must end on one convention.

**Do NOT convert — these are not percentages:**

- `performance.interest_coverage_ratio` (1.36 – 10.1) — a **multiple**, never a percentage.
- `performance.weighted_average_lease_expiry` / `weighted_average_debt_maturity` — **years**.
- `performance.distribution_per_unit` (cents), `net_asset_value_per_unit` (dollars).

**Conflict to resolve first:** `transaction-target-schema-AGREED.md` specifies `gain_loss_pct` in
**percent** ("8.4 means +8.4%"). Under this rule it becomes `0.084`, and the worked examples in that
document need updating. Note `gain_loss_pct` is currently the one field deliberately excluded from
`FRACTION_FIELDS` — and 61 prod rows are stale (see that doc's P0), so **re-promote first, then
convert**, or the two bugs will be impossible to tell apart.
