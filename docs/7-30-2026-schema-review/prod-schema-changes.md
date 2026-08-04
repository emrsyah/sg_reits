# Prod schema changes — 2026-07-30 review

Migration: `schema/migrations/2026-08-04_prod_schema_sync.sql`
Adds run **before** `promote_final_to_prod.py --write`, drops **after**.

`sgx_reit_financial_final` is not promoted — financials live in `sgx_manual_input`.

---

## Database-wide


| change          | detail                                                                                                                                                                                     |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| percentages     | every percentage column is now `0-1`. Normalised once in `build_final_tables.py` `pct01()`; `FRACTION_FIELDS` in the promote script is empty                                               |
| not percentages | `interest_coverage_ratio` (a multiple), `weighted_average_lease_expiry`, `weighted_average_debt_maturity` (years), `distribution_per_unit`, `net_asset_value_per_unit` (money) — unchanged |
| currency        | all money is SGD in `_final`; no `*_currency` column reaches prod                                                                                                                          |
| ticker          | `BMOU` → `BMGU` (BHG Retail REIT)                                                                                                                                                          |


---

## sgx_reit_profile

No change. 4 columns.

---

## sgx_reit_performance


| column                              | change    | note                                                                                               |
| ----------------------------------- | --------- | -------------------------------------------------------------------------------------------------- |
| `units_in_issue`                    | **added** | renamed from `number_of_shareholder_units`, values identical                                       |
| `income_for_year`                   | **added** | renamed from `net_distributable_income`                                                            |
| `distribution_declared`             | **added** |                                                                                                    |
| `amount_retained`                   | **added** | income withheld rather than paid out                                                               |
| `other_additions`                   | **added** | from `distribution_pool_other_movements`, redefined economically: operating sources vs asset sales |
| `number_of_shareholder_units`       | dropped   | → renamed to `units_in_issue`                                                                      |
| `net_distributable_income`          | dropped   | → renamed to `income_for_year`                                                                     |
| `distribution_cash_paid`            | dropped   | → renamed to `distribution_paid`                                                                   |
| `distribution_pool_other_movements` | dropped   | → renamed to `other_additions`                                                                     |
| `adjusted_distributable_income`     | dropped   | not replaced                                                                                       |
| `aggregate_leverage`                | adjusted  | `39.0` → `0.39`                                                                                    |
| `cost_of_debt`                      | adjusted  | `3.5` → `0.035`                                                                                    |
| `portfolio_occupancy`               | adjusted  | `90.9` → `0.909`                                                                                   |
| `number_of_unitholders`             | unchanged | counts HOLDERS, not units                                                                          |


Rollforward: `opening + income_for_year + other_additions − distribution_paid − amount_retained = closing`

---

## sgx_reit_property


| column                | change    | note                                                                                                        |
| --------------------- | --------- | ----------------------------------------------------------------------------------------------------------- |
| `coordinate_source`   | **added** | e.g. `onemap`                                                                                               |
| `gross_lettable_area` | dropped   | 9 values moved into `net_lettable_area` first                                                               |
| `effective_date`      | dropped   | derived into `lease_expiry_date` first (7 final rows); 10 T82U rows were year-only and could not be derived |
| `occupancy_rate`      | unchanged | already `0-1`                                                                                               |
| `ownership`           | unchanged | already `0-1`                                                                                               |


---

## sgx_reit_top_tenant


| column          | change    | note                                                                                |
| --------------- | --------- | ----------------------------------------------------------------------------------- |
| `basis_segment` | **added** | `office` / `retail` / `commercial` / `logistics_industrial`; NULL = whole portfolio |
| `pct_basis`     | adjusted  | remapped to 6 canonical values                                                      |
| `revenue_pct`   | unchanged | already `0-1`                                                                       |


`pct_basis` mapping:


| old                                                                            | new                                     |
| ------------------------------------------------------------------------------ | --------------------------------------- |
| `gri`, `base_rental_income`, `committed_gross_rent`, `apartment_rental_income` | `gross_rental_income`                   |
| `cash_rental_income`                                                           | `gross_revenue`                         |
| `office_gri`, `retail_gri`                                                     | `gross_rental_income` + `basis_segment` |
| `gri_commercial`, `gri_logistics_industrial`                                   | `gross_rental_income` + `basis_segment` |


Canonical set: `headline_rent` · `annualised_rent` · `npi` · `asset_value` · `gross_rental_income` · `gross_revenue`

---

## sgx_reit_trade_mix


| column          | change    | note                       |
| --------------- | --------- | -------------------------- |
| `basis_segment` | **added** | joins the unique key       |
| `pct_basis`     | adjusted  | same remap as `top_tenant` |
| `pct`           | unchanged | already `0-1`              |


Unique index becomes `(symbol, financial_year, category, pct_basis, coalesce(basis_segment,''))`.
Without `basis_segment` in the key, T82U's office and retail rows for the same category collide and are summed into a ~200% total.

Row counts: `_final` 761 → prod 509. Not a loss — rows sharing a canonical category are summed on promotion.

---

## sgx_reit_property_transaction


| column               | change    | note                                                                      |
| -------------------- | --------- | ------------------------------------------------------------------------- |
| `deal_id`            | **added** | set only where rows share one price; NULL = row stands alone              |
| `basis_value`        | **added** | what `sale_price` is measured against                                     |
| `basis`              | **added** | `valuation` / `book_value` / `purchase_price` / `net_identifiable_assets` |
| `carrying_value`     | dropped   | → `basis_value` + `basis`                                                 |
| `valuation`          | dropped   | → `basis_value` + `basis`                                                 |
| `valuation_date`     | dropped   |                                                                           |
| `gain_on_divestment` | dropped   | derive: `sale_price − basis_value`                                        |
| `gain_basis`         | dropped   | → `basis`                                                                 |
| `gain_loss_pct`      | dropped   | derive: `(sale_price − basis_value) / basis_value`                        |
| `net_sale_proceeds`  | dropped   | → `sale_price`                                                            |
| `announced_date`     | dropped   |                                                                           |
| `transaction_date`   | dropped   | → `completed_date`                                                        |
| `description`        | dropped   |                                                                           |
| `interest_pct`       | fixed     | prod AJBU FY2025 KDC SGP 7 &amp; 8 reads `0.0051`, should be `0.51`       |


**Prod holds completed transactions only.** `_final` keeps the full record (212); the promote filters to `status = 'completed'` (185). `announced` deals can be repriced or abandoned and carry no `completed_date`, so their money cannot even be FX-converted.

Prod 206 rows → 185.

The filter runs **after** scopes are grouped, not before. N2IU FY2023 and O5RU FY2024 contain only non-completed rows: filtering first would drop those scope keys, so the promote would never issue their DELETE and stale rows would survive in prod. Grouped first, the scope is visited, emptied, and left empty.

Four completed rows have no `completed_date` — aggregate strata deals sold to different buyers across the year, with no single completion date (P40U Wisma Atria, T82U Suntec City ×2, A17U Manton Wood).

**Gain is derived, not stored.** Verified on all 212 rows: `gain = sale_price − basis_value` and `pct = gain / basis_value` exactly, with no row where one side is present and the other missing.

Both sides are converted to SGD **before** they reach `_final`, so subtracting them uses one rate. Subtracting native amounts and converting the difference gives a different answer.

**Known imprecision:** three rows hold a price net of disposal costs against a gross basis, so their gain reads slightly low — BTOU Capitol (110.0 vs 118.0), BTOU Plaza (40.0 vs 43.7), UD1U Il·lumina (24.5 vs 24.7).

**Do not compare** `purchase_price` with `basis_value` on C38U ION Orchard or J69U Northpoint City South Wing: the price is an equity consideration net of assumed debt, the basis is a gross property valuation.

---

## Column counts


| table                           | prod before | prod after |
| ------------------------------- | ----------- | ---------- |
| `sgx_reit_profile`              | 4           | 4          |
| `sgx_reit_performance`          | 28          | 28         |
| `sgx_reit_property`             | 24          | 23         |
| `sgx_reit_top_tenant`           | 7           | 8          |
| `sgx_reit_trade_mix`            | 5           | 6          |
| `sgx_reit_property_transaction` | 20          | 13         |

---

## Data types

New columns follow prod's existing convention, not dev's `numeric`.

| kind | prod type | examples |
| ---- | --------- | -------- |
| money | `bigint` | `portfolio_value`, `gross_revenue`, `basis_value`, `income_for_year` |
| counts | `bigint` | `units_in_issue`, `number_of_unitholders`, `rank`, `financial_year` |
| percentages, ratios | `double precision` / `real` | `occupancy_rate`, `aggregate_leverage`, `interest_pct` |
| areas | `real` | `net_lettable_area`, `gross_floor_area` |
| dates | `date` | `completed_date`, `lease_expiry_date` |
| labels, ids | `text` | `deal_id`, `basis`, `basis_segment`, `coordinate_source` |

Types assigned to the new columns:

| column | type | matches |
| ------ | ---- | ------- |
| `performance.units_in_issue` | `bigint` | `number_of_shareholder_units` |
| `performance.income_for_year` | `bigint` | `net_distributable_income` |
| `performance.distribution_declared` | `bigint` | money |
| `performance.amount_retained` | `bigint` | money |
| `performance.other_additions` | `bigint` | `distribution_pool_other_movements` |
| `property.coordinate_source` | `text` | label |
| `top_tenant.basis_segment` | `text` | label |
| `trade_mix.basis_segment` | `text` | label |
| `transaction.deal_id` | `text` | id |
| `transaction.basis_value` | `bigint` | `carrying_value`, `valuation` |
| `transaction.basis` | `text` | label |

### Rounding

FX conversion leaves fractions on ~35 money figures. `coerce()` in `promote_final_to_prod.py` now **rounds** into `bigint` instead of `int()`, which truncated toward zero (`1,638,000.9999` → `1,638,000`).

### Known prod inconsistency, not from this review

`property_transaction.purchase_price` is `text` while `sale_price` and every other money column is `bigint`. The promote serializes it as a string to match. Aligning it is a separate decision; the statement is in `§4` of the migration, commented.

### Values nulled on promotion

Prod types some columns `date` where `_final` holds as-reported text. Non-dates cannot be stored and become NULL — this is still a net gain over prod today.

| column | `_final` | promoted | nulled | why |
| ------ | -------- | -------- | ------ | --- |
| `property.purchase_date` | 2643 | 2306 (prod now 2079) | 337 | bare years, e.g. `'2008'` |
| `property.lease_expiry_date` | 838 | 830 (prod now 691) | 8 | bare years |


