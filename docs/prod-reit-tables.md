# SGX REIT production tables

Six tables covering 37 Singapore-listed REITs, FY2023–FY2025. Every figure comes from an
audited annual report and is traceable to a page.

Source of truth is the dev database. Prod is built by `build_final_tables.py` (dev raw →
`*_final`) then `promote_final_to_prod.py` (`*_final` → prod). Prod holds no provenance
columns: no currency tags, no source pages, no extraction flags.

---

## Conventions

| kind | rule |
|---|---|
| money | SGD, converted at the MAS quarterly rate nearest the FY end. Stored as `bigint` |
| percentages | 0–1. `aggregate_leverage` 0.39 means 39% |
| ratios | a multiple as printed. `interest_coverage_ratio` 3.6 means 3.6× |
| durations | years |
| areas | square metres, `real` |
| `distribution_per_unit` | cents |
| `net_asset_value_per_unit` | dollars |
| `symbol` | bare ticker, no `.SI` suffix |
| `financial_year` | the declared FY, not the calendar year |

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

| column | type | fill | notes |
|---|---|---|---|
| `symbol` | text | 100% | primary key |
| `sub_sector` | text | 100% | 8 values |
| `management` | jsonb | 100% | `{sponsor, trustee, reit_manager, property_manager, master_lessee}`, each a list |
| `board` | jsonb | 100% | `[{name, position}]` |

`sub_sector`: Diversified 11, Retail 6, Industrial 6, Office 5, Hospitality 4, Data Centre 2,
Healthcare 2, Specialized 1.

---

## sgx_reit_performance

One row per REIT-year. 74 rows: FY2023 ×3, FY2024 ×36, FY2025 ×35.

| column | type | fill |
|---|---|---|
| `symbol`, `financial_year` | text, bigint | 100% (key) |
| `date` | text | 100% |
| `source_url` | text | 100% |
| `properties_location` | text | 100% |
| `portfolio_value` | bigint | 100% |
| `gross_revenue` | bigint | 100% |
| `net_property_income` | bigint | 100% |
| `income_for_year` | bigint | 100% |
| `units_in_issue` | bigint | 100% |
| `units_to_be_issued` | bigint | 55% |
| `number_of_unitholders` | bigint | 100% |
| `distribution_per_unit` | double | 100% |
| `net_asset_value_per_unit` | double | 100% |
| `distribution_record` | jsonb | 100% |
| `distribution_declared` | bigint | 68% |
| `distribution_paid` | bigint | 100% |
| `distributable_income_opening` | bigint | 85% |
| `distributable_income_closing` | bigint | 88% |
| `other_additions` | bigint | 27% |
| `amount_retained` | bigint | 38% |
| `aggregate_leverage` | double | 100% |
| `cost_of_debt` | double | 99% |
| `interest_coverage_ratio` | double | 100% |
| `weighted_average_debt_maturity` | double | 89% |
| `weighted_average_lease_expiry` | double | 89% |
| `portfolio_occupancy` | double | 95% |

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

| column | type | fill |
|---|---|---|
| `symbol`, `financial_year`, `property_name` | | 100% (key) |
| `country` | text | 100% |
| `category` | text | 100% |
| `address` | text | 97% |
| `ownership` | real | 81% |
| `market_valuation` | bigint | 97% |
| `valuation_date` | date | 99% |
| `purchase_price` | bigint | 81% |
| `purchase_date` | date | 67% |
| `gross_revenue` | bigint | 87% |
| `net_property_income` | bigint | 11% |
| `occupancy_rate` | double | 88% |
| `net_lettable_area` | real | 70% |
| `gross_floor_area` | real | 37% |
| `land_tenure` | text | 100% |
| `lease_term_years` | real | 39% |
| `lease_expiry_date` | date | 24% |
| `status` | text | 100% |
| `latitude`, `longitude` | double | 96% |

`category` (6 values): Industrial & Logistics 1551, Specialized 815, Office 448, Retail 296,
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

| column | type | fill |
|---|---|---|
| `symbol`, `financial_year`, `rank` | | 100% (key) |
| `client_name` | text | 100% |
| `industry` | text | 99% |
| `pct` | double | 100% |
| `pct_basis` | text | 100% |
| `basis_segment` | text | 11% |

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

| column | type | fill |
|---|---|---|
| `symbol`, `financial_year`, `category`, `pct_basis` | | 100% (key) |
| `pct` | double | 100% |
| `basis_segment` | text | 10% |

`category` (15 values): Financial & Professional Services, Other Retail Trades, Infrastructure
Real Estate & Property Services, Other Office Trades, IT & Telecommunications, Government
Related, Healthcare & Wellness, Hospitality & Leisure, Logistics & Supply Chain Management,
Food & Beverages, Fashion & Accessories, Manufacturing, Other Industrial Trades, Energy Mining
& Resources, Departmental Store/Supermarket.

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

| column | type | fill |
|---|---|---|
| `symbol`, `financial_year`, `transaction_type`, `property_name` | | 100% (key) |
| `status` | text | 100% |
| `counterparty` | text | 90% |
| `completed_date` | date | 98% |
| `interest_pct` | real | 99% |
| `transaction_price` | bigint | 99% |
| `basis_value` | bigint | 69% |
| `basis` | text | 70% |
| `deal_id` | text | 8% |

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

| what | detail |
|---|---|
| `portfolio_value` is not comparable across REITs | ME8U reports AUM-style, DCRU at-share AUM, others the audited portfolio statement. Do not use it to reconcile against the property table |
| 11 rows have no distribution rollforward | those reports do not publish one. CY6U and J91U are business trusts, not REITs |
| C2PU FY2025 rollforward off by 36,000 | its `income_for_year` is computed rather than printed |
| 3 distribution records cover half a year | A17U FY2025 missing H2, XZL FY2024 and FY2025 missing H1. The other half is announced in the interim results release, not the annual report |
| `property.net_property_income` at 11% | most reports give NPI for the portfolio, not per property |
| `property.purchase_date` at 67% | 337 rows disclose a bare year, which cannot be stored in a `date` column |
| 2 divestments carry a price net of disposal costs | BTOU Capitol (110.0 against a 118.0 valuation) and UD1U Il·lumina (24.5 against 24.698). Their gains read low against a gross basis |
| sum of property valuations ≠ `portfolio_value` | JV assets are equity-accounted and absent from the portfolio statement; MXNU itemises only its top 10 of 149 properties |
