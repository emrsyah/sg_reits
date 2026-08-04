# SGX REIT production tables

Six tables covering 37 Singapore-listed REITs, FY2023–FY2025.

---

## Conventions


| kind                       | rule                                                                            |
| -------------------------- | ------------------------------------------------------------------------------- |
| money                      | SGD, converted at the MAS quarterly rate nearest the FY end. Stored as `bigint` |
| percentages                | 0–1. `aggregate_leverage` 0.39 means 39%                                        |
| ratios                     | a multiple as printed. `interest_coverage_ratio` 3.6 means 3.6×                 |
| durations                  | years                                                                           |
| areas                      | square metres, `real`                                                           |
| `distribution_per_unit`    | cents                                                                           |
| `net_asset_value_per_unit` | dollars                                                                         |
| `symbol`                   | bare ticker, no `.SI` suffix                                                    |
| `financial_year`           | the declared FY, not the calendar year                                          |


`interest_coverage_ratio`, `weighted_average_lease_expiry`, `weighted_average_debt_maturity`,
`distribution_per_unit` and `net_asset_value_per_unit` are not percentages and are not scaled.

DPU is in cents while NAV is in dollars. Per-unit arithmetic across the two needs `dpu / 100`.

### Declared financial year

Six REITs have non-December year ends: `M44U` `ME8U` `N2IU` `O5RU` `P40U` `JYEU`. `J69U` ends
30 September. For these, FY2024 does not mean calendar 2024. M44U's FY2023 runs April 2023 to
March 2024. Use `sgx_reit_performance.date` to get the actual FY end for any REIT-year.

---

## sgx_reit_profile

One row per REIT. 37 rows.


| column       | type  | fill | what it is                                                                   |
| ------------ | ----- | ---- | ---------------------------------------------------------------------------- |
| `symbol`     | text  | 100% | SGX ticker. Primary key                                                      |
| `sub_sector` | text  | 100% | What the REIT mainly owns                                                    |
| `management` | jsonb | 100% | Who runs it: sponsor, trustee, REIT manager, property manager, master lessee |
| `board`      | jsonb | 100% | Directors and their positions                                                |


`sub_sector`: Diversified 11, Retail 6, Industrial 6, Office 5, Hospitality 4, Data Centre 2,
Healthcare 2, Specialized 1.

---

## sgx_reit_performance

One row per REIT-year. 74 rows: FY2023 ×3, FY2024 ×36, FY2025 ×35.


| column                           | type         | fill | what it is                                                         |
| -------------------------------- | ------------ | ---- | ------------------------------------------------------------------ |
| `symbol`, `financial_year`       | text, bigint | 100% | Key                                                                |
| `date`                           | text         | 100% | Last day of the financial year                                     |
| `source_url`                     | text         | 100% | The annual report this row came from                               |
| `properties_location`            | text         | 100% | Countries the portfolio spans                                      |
| `portfolio_value`                | bigint       | 100% | What the whole portfolio is worth                                  |
| `gross_revenue`                  | bigint       | 100% | Total rent and other income for the year                           |
| `net_property_income`            | bigint       | 100% | Gross revenue less the cost of running the properties              |
| `income_for_year`                | bigint       | 100% | Income available to distribute, before anything is held back       |
| `units_in_issue`                 | bigint       | 100% | Units outstanding at year end                                      |
| `units_to_be_issued`             | bigint       | 55%  | Units promised but not yet issued, e.g. manager fees paid in units |
| `number_of_unitholders`          | bigint       | 100% | How many holders own units                                         |
| `distribution_per_unit`          | double       | 100% | Cents paid per unit for the year (DPU)                             |
| `net_asset_value_per_unit`       | double       | 100% | Net assets divided by units, in dollars (NAV)                      |
| `distribution_record`            | jsonb        | 100% | The year's payouts split into tranches                             |
| `distribution_declared`          | bigint       | 68%  | Total declared for the year                                        |
| `distribution_paid`              | bigint       | 100% | Cash actually paid out during the year                             |
| `distributable_income_opening`   | bigint       | 85%  | Undistributed pool carried in from last year                       |
| `distributable_income_closing`   | bigint       | 88%  | Undistributed pool carried out to next year                        |
| `other_additions`                | bigint       | 27%  | Money added to the pool beyond `income_for_year`                   |
| `amount_retained`                | bigint       | 38%  | Income held back rather than paid out                              |
| `aggregate_leverage`             | double       | 100% | Debt as a share of assets (gearing)                                |
| `cost_of_debt`                   | double       | 99%  | Average interest rate paid on borrowings                           |
| `interest_coverage_ratio`        | double       | 100% | How many times earnings cover interest                             |
| `weighted_average_debt_maturity` | double       | 89%  | Average years until debt falls due                                 |
| `weighted_average_lease_expiry`  | double       | 89%  | Average years until leases expire (WALE)                           |
| `portfolio_occupancy`            | double       | 95%  | Share of space leased across the portfolio                         |


`date` is the FY end. `number_of_unitholders` counts holders; `units_in_issue` counts units.

`distribution_record` is a list of `{dpu, period_start, period_end}`, one per tranche, in cents.

### The distribution rollforward

```
distributable_income_opening
  + income_for_year
  + other_additions
  − distribution_paid
  − amount_retained
  = distributable_income_closing
```

Closes on 62 of 74 rows. Each year's closing is the next year's opening.

`distribution_declared` is what the year earned the right to. `distribution_paid` is cash that
moved during the year, which includes last year's final distribution and excludes this year's.
They are different numbers and 24 rows disclose only the paid figure.

### DPU cross-check

```
distribution_per_unit / 100 × units_in_issue ≈ distribution_declared
```

Within 10% on 44 of 45 rows. It is approximate because DPU accrues per tranche against the unit
count at each record date, while `units_in_issue` is the year-end count. AJBU FY2024 misses by
21% because 148,413,063 new units listed on 18 December 2024, thirteen days before year end.

### Zero versus null

Zero means the REIT declared or paid nothing. BTOU and D5IU suspended distributions; their
rollforwards still close. Null means the report does not publish that line. Do not merge them.

---

## sgx_reit_property

One row per property per REIT-year. 3420 rows: FY2023 ×305, FY2024 ×1494, FY2025 ×1621.
Key is `(symbol, financial_year, property_name)`.


| column                                      | type   | fill | what it is                                   |
| ------------------------------------------- | ------ | ---- | -------------------------------------------- |
| `symbol`, `financial_year`, `property_name` |        | 100% | Key                                          |
| `country`                                   | text   | 100% | Where the property is                        |
| `category`                                  | text   | 100% | Asset type                                   |
| `address`                                   | text   | 97%  | Street address                               |
| `ownership`                                 | real   | 81%  | The REIT's stake in the property             |
| `market_valuation`                          | bigint | 97%  | Appraised value at year end, on a 100% basis |
| `valuation_date`                            | date   | 99%  | When it was valued                           |
| `purchase_price`                            | bigint | 81%  | What the REIT paid for it                    |
| `purchase_date`                             | date   | 67%  | When the REIT bought it                      |
| `gross_revenue`                             | bigint | 87%  | The property's revenue for the year          |
| `net_property_income`                       | bigint | 11%  | Its revenue less its running costs           |
| `occupancy_rate`                            | double | 88%  | Share of its space leased                    |
| `net_lettable_area`                         | real   | 70%  | Floor area that can be leased out            |
| `gross_floor_area`                          | real   | 37%  | Total built area, leasable or not            |
| `land_tenure`                               | text   | 100% | Freehold or leasehold                        |
| `lease_term_years`                          | real   | 39%  | Length of the lease                          |
| `lease_expiry_date`                         | date   | 24%  | When the lease ends                          |
| `status`                                    | text   | 100% | Still held, held for sale, or sold           |
| `latitude`, `longitude`                     | double | 96%  | Map coordinates                              |


`category` (6 values): Industrial &amp; Logistics 1551, Specialized 815, Office 448, Retail 296,
Data Centers 296, Diversified (Commercial) 14.

`status`: active 3326, divested 72, held_for_sale 22. Divested rows carry a name and country and
little else: market valuation on 3 of 72, NLA on 1. 69 of the 72 also appear in
`sgx_reit_property_transaction` with price and date.

`land_tenure`: Freehold 1940, Leasehold 1477.

`country`: 34 values. Singapore 866, United States 458, Japan 367, Australia 348,
United Kingdom 255, China 209, France 175, Germany 126.

`market_valuation` is recorded at 100% of the property as the audited statement prints it.
Multiply by `ownership` for the effective-interest value.

`occupancy_rate` is null on 404 rows, 207 of them HMN, where occupancy is disclosed for the
portfolio rather than per property. 27 rows are genuinely 0. Do not default null to 1.

`lease_expiry_date` holds two different things. For leasehold land it is the land-lease expiry.
For freehold land it is the master-lease expiry to the operator, which is why 28 freehold rows
carry one. 60 rows are master leases, all AW9U.

---

## sgx_reit_top_tenant

One row per tenant per REIT-year. 752 rows: FY2023 ×30, FY2024 ×358, FY2025 ×364.
Key is `(symbol, financial_year, rank)`.


| column                             | type   | fill | what it is                                                               |
| ---------------------------------- | ------ | ---- | ------------------------------------------------------------------------ |
| `symbol`, `financial_year`, `rank` |        | 100% | Key. Rank 1 is the largest tenant                                        |
| `client_name`                      | text   | 100% | Tenant name as the report gives it                                       |
| `industry`                         | text   | 99%  | The tenant's sector                                                      |
| `pct`                              | double | 100% | The tenant's share of whatever `pct_basis` names                         |
| `pct_basis`                        | text   | 100% | What that share is measured against                                      |
| `basis_segment`                    | text   | 11%  | Which part of the portfolio the denominator covers. Null means all of it |


`pct` is the tenant's share of whatever `pct_basis` names, as a fraction.

`pct_basis` (5 values): gross_rental_income 549, gross_revenue 143, annualised_rent 20, npi 20,
headline_rent 20.

`industry` uses the same 15-value list as `sgx_reit_trade_mix.category`. Where an annual report
publishes a per-tenant sector column it is mapped from that; where it does not, the industry is
derived from the tenant's line of business. 4 rows are null because the report withholds the
tenant name.

`basis_segment` is non-null when the percentages run against a segment denominator rather than
the whole portfolio. T82U discloses office and retail tenant tables against separate
denominators, each summing to about 100% within its segment. Ranks stay unique within a
REIT-year: T82U ranks 1–10 are office, 11–20 retail.

---

## sgx_reit_trade_mix

Sector breakdown per REIT-year. 512 rows: FY2023 ×26, FY2024 ×248, FY2025 ×238.
Key is `(symbol, financial_year, category, pct_basis, basis_segment)`.


| column                                              | type   | fill | what it is                                                               |
| --------------------------------------------------- | ------ | ---- | ------------------------------------------------------------------------ |
| `symbol`, `financial_year`, `category`, `pct_basis` |        | 100% | Key                                                                      |
| `pct`                                               | double | 100% | That sector's share of the portfolio                                     |
| `pct_basis`                                         | text   | 100% | What the share is measured against                                       |
| `basis_segment`                                     | text   | 10%  | Which part of the portfolio the denominator covers. Null means all of it |


`category` (15 values): Financial &amp; Professional Services, Other Retail Trades, Infrastructure
Real Estate &amp; Property Services, Other Office Trades, IT &amp; Telecommunications, Government
Related, Healthcare &amp; Wellness, Hospitality &amp; Leisure, Logistics &amp; Supply Chain Management,
Food &amp; Beverages, Fashion &amp; Accessories, Manufacturing, Other Industrial Trades, Energy Mining
&amp; Resources, Departmental Store/Supermarket.

`pct_basis` (5 values): gross_rental_income 419, gross_revenue 69, headline_rent 20,
annualised_rent 2, asset_value 2.

`pct` sums to about 1.0 per `(symbol, financial_year, basis_segment)`. Group by `basis_segment`
before summing. T82U FY2024 and FY2025 each have an office breakdown summing to 1.0 and a retail
breakdown summing to 1.0. Ignoring the segment gives 2.0. BUOU FY2024 splits one portfolio, so
its commercial 0.356 and logistics_industrial 0.644 sum to 1.0 together.

---

## sgx_reit_property_transaction

One row per completed transaction. 172 rows: FY2023 ×18, FY2024 ×68, FY2025 ×86.
Key is `(symbol, financial_year, transaction_type, property_name)`.


| column                                                          | type   | fill | what it is                                                       |
| --------------------------------------------------------------- | ------ | ---- | ---------------------------------------------------------------- |
| `symbol`, `financial_year`, `transaction_type`, `property_name` |        | 100% | Key                                                              |
| `status`                                                        | text   | 100% | Always completed in prod                                         |
| `counterparty`                                                  | text   | 90%  | Who the REIT bought from or sold to                              |
| `completed_date`                                                | date   | 98%  | When the deal closed                                             |
| `interest_pct`                                                  | real   | 99%  | The stake bought or sold. 1.0 is the whole asset                 |
| `transaction_price`                                             | bigint | 99%  | What was paid or received, gross                                 |
| `basis_value`                                                   | bigint | 69%  | The figure the price is measured against                         |
| `basis`                                                         | text   | 70%  | What `basis_value` is                                            |
| `deal_id`                                                       | text   | 8%   | Links rows that share one price. Null means the row stands alone |


`transaction_type` is `acquisition` (62) or `divestment` (110). `status` is always `completed`;
announced and terminated deals stay in dev.

`transaction_price` is the gross consideration, whichever direction the deal runs.
`transaction_type` gives the direction.

`interest_pct` is the stake transacted, as a fraction. 1.0 means the whole asset. One row is
null: AJBU FY2025 covers a 10% interest in one data centre and a 1% interest in another, so no
single value is correct.

`basis` is what `basis_value` measures: valuation 99, book_value 19, purchase_price 3, null 51.
Gains computed on different bases are not comparable.

### Gain is derived, not stored

```
gain     = transaction_price − basis_value
gain_pct = gain / basis_value
```

Both sides are already SGD at the same rate, so the subtraction is valid. Converting a native
difference gives a different answer.

Two rows must not be compared this way. C38U's ION Orchard and J69U's Northpoint City South Wing
carry a price net of assumed debt against a gross property valuation.

### deal_id

Non-null means the price is shared across rows. Group by `deal_id` before summing money, or the
same money counts twice. 13 rows across 5 deals, all multi-property aggregates sold under one
price in one year.

Null means the row stands alone. Cross-year duplicates were collapsed into the year containing
`completed_date`, so no deal appears twice.

Four completed rows have no `completed_date`. They are strata deals sold to different buyers
across the year with no single completion date.

---

## Joining

```
profile              symbol
performance          symbol, financial_year
property             symbol, financial_year, property_name
top_tenant           symbol, financial_year, rank
trade_mix            symbol, financial_year, category, pct_basis, basis_segment
property_transaction symbol, financial_year, transaction_type, property_name
```

`property.property_name` and `property_transaction.property_name` do not reliably match. The
transaction table sometimes names several properties in one string, and divested properties
disappear from the property table the following year.

---

## Known gaps


| what                                     | detail                                                                                                                                      |
| ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| C2PU FY2025 rollforward off by 36,000    | its `income_for_year` is computed rather than printed                                                                                       |
| 3 distribution records cover half a year | A17U FY2025 missing H2, XZL FY2024 and FY2025 missing H1. The other half is announced in the interim results release, not the annual report |
| `property.net_property_income` at 11%    | most reports give NPI for the portfolio, not per property                                                                                   |
| `property.purchase_date` at 67%          | 337 rows disclose a bare year, which cannot be stored in a `date` column                                                                    |


