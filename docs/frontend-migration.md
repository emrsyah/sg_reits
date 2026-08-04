# Frontend migration: old prod → new prod

What changed in the six `sgx_reit_*` tables. Work through the breaking changes first, then
the value changes, then the row-count changes.

Full column reference: `docs/prod-reit-tables.md`.

---

## 1. Renamed columns

Old name gone, new name holds the same values.

| table | old | new |
| ----- | --- | --- |
| performance | `number_of_shareholder_units` | `units_in_issue` |
| performance | `net_distributable_income` | `income_for_year` |
| performance | `distribution_cash_paid` | `distribution_paid` |
| performance | `distribution_pool_other_movements` | `other_additions` |
| property | `gross_lettable_area` | `net_lettable_area` |
| top_tenant | `revenue_pct` | `pct` |
| transaction | `transaction_date` | `completed_date` |
| transaction | `net_sale_proceeds` | `transaction_price` |

`property.gross_lettable_area` held 9 values; they moved into `net_lettable_area`.

---

## 2. Deleted columns

| table | column | what to do |
| ----- | ------ | ---------- |
| performance | `adjusted_distributable_income` | No replacement. Remove from the UI |
| performance | `distribution_period_months` | Remove |
| property | `effective_date` | Use `lease_expiry_date`, which was derived from it |
| transaction | `purchase_price`, `sale_price` | Both merged into `transaction_price` |
| transaction | `carrying_value`, `valuation`, `valuation_date` | Use `basis_value` + `basis` |
| transaction | `gain_on_divestment`, `gain_loss_pct`, `gain_basis` | Derive. See §5 |
| transaction | `announced_date` | Removed |
| transaction | `description` | Removed |

---

## 3. New columns

| table | column | what it is |
| ----- | ------ | ---------- |
| performance | `distribution_declared` | Total declared for the year, distinct from `distribution_paid` |
| performance | `amount_retained` | Income held back rather than paid out |
| top_tenant | `basis_segment` | Which part of the portfolio the percentage denominator covers |
| trade_mix | `basis_segment` | Same |
| transaction | `basis_value` | The figure the price is measured against |
| transaction | `basis` | What `basis_value` is: valuation, book_value or purchase_price |
| transaction | `deal_id` | Links rows that share one price |

---

## 4. Values changed scale

**Three columns went from 0–100 to 0–1.** Anything formatting them as an already-multiplied
percentage now needs `× 100`.

| column | was | now |
| ------ | --- | --- |
| `performance.aggregate_leverage` | 39.0 | 0.39 |
| `performance.cost_of_debt` | 3.5 | 0.035 |
| `performance.portfolio_occupancy` | 90.9 | 0.909 |

Every percentage in the database is now 0–1. Already on that scale and unchanged:
`property.occupancy_rate`, `property.ownership`, `top_tenant.pct`, `trade_mix.pct`,
`transaction.interest_pct`.

**Not percentages, do not scale:** `interest_coverage_ratio` (a multiple),
`weighted_average_lease_expiry` and `weighted_average_debt_maturity` (years),
`distribution_per_unit` (cents), `net_asset_value_per_unit` (dollars).

**One value was wrong and is now fixed.** `transaction.interest_pct` for AJBU FY2025
Keppel DC Singapore 7 & 8 read `0.0051`; it is `0.51`.

---

## 5. Gain is no longer stored

`gain_on_divestment` and `gain_loss_pct` are gone. Compute them:

```js
const gain    = row.transaction_price - row.basis_value
const gainPct = gain / row.basis_value        // a fraction, ×100 to display
```

Both sides are SGD at the same rate, so the subtraction is valid.

`basis` says what the gain is measured against. A gain against `valuation` and one against
`book_value` are not comparable, so show the basis wherever you show the percentage.

Skip the calculation when `basis_value` is null (53 of 172 rows).

**Two rows must not use this formula.** C38U's ION Orchard and J69U's Northpoint City South
Wing carry a price net of assumed debt against a gross property valuation. Filter them out or
suppress the percentage.

---

## 6. `distribution_record` shape changed

Was:

```json
{"dpu": 6.479, "line": 5403, "amount": 285110000, "pay_date": null,
 "period_start": "2025-01-01", "period_end": "2025-06-05"}
```

Now:

```json
{"dpu": 6.479, "period_start": "2025-01-01", "period_end": "2025-06-05"}
```

`line`, `amount` and `pay_date` are gone. `amount` is recomputable as `dpu / 100 × units_in_issue`.

---

## 7. Row counts changed

| table | was | now | why |
| ----- | --- | --- | --- |
| transaction | 206 | 172 | Announced and terminated deals removed; cross-year duplicates collapsed |
| trade_mix | 509 | 512 | T82U FY2025 office and retail now split correctly |
| performance | 74 | 74 | unchanged |
| property | 3420 | 3420 | unchanged |
| top_tenant | 752 | 752 | unchanged |
| profile | 37 | 37 | unchanged |

**Transactions are completed only.** `status` is always `completed`. Announced deals no longer
appear, so a "pending transactions" view has no data source in prod.

**The same property no longer appears twice.** A deal disclosed in two annual reports used to
produce two rows. It is now one row, in the year it completed.

---

## 8. Aggregation rules that changed

### Group by `deal_id` before summing transaction money

13 rows across 5 deals share one price between several properties. Summing
`transaction_price` without grouping counts that money twice.

```sql
select coalesce(deal_id, property_name) as deal, max(transaction_price)
from sgx_reit_property_transaction
group by 1
```

Counting properties uses rows. Counting money groups by `deal_id` first.

### Group by `basis_segment` before summing `trade_mix.pct`

`pct` sums to 1.0 per `(symbol, financial_year, basis_segment)`, not per REIT-year.

T82U FY2024 and FY2025 each publish an office breakdown summing to 1.0 and a retail breakdown
summing to 1.0. Ignoring `basis_segment` gives 2.0 and a broken chart.

BUOU FY2024 is the opposite case: its commercial 0.356 and logistics_industrial 0.644 split one
portfolio and sum to 1.0 together.

Same rule for `top_tenant`. T82U ranks 1–10 are office, 11–20 retail, against separate
denominators.

---

## 9. Cleaned values

| column | change |
| ------ | ------ |
| `property.category` | Now exactly 6 values. ME8U FY2023 previously leaked 5 raw labels: Flatted Factories, Hi-Tech Buildings, Business Park Buildings, Light Industrial Buildings, Stack-up/Ramp-up Buildings |
| `top_tenant.pct_basis`, `trade_mix.pct_basis` | Now 5 values. `gri`, `rental_income`, `cash_rental_income`, `committed_gross_rent`, `office_gri`, `retail_gri`, `gri_commercial`, `gri_logistics_industrial` are gone. The segment ones moved into `basis_segment` |
| `top_tenant.industry` | Null on 4 rows instead of 117 |
| `profile.symbol` | `BMOU` is now `BMGU` (BHG Retail REIT) |

---

## 10. Null handling

**Do not default null to zero in the distribution columns.** Zero and null mean different
things. Zero means the REIT declared or paid nothing, which is a fact worth showing: BTOU and
D5IU suspended distributions. Null means the report does not publish that line.

**Do not default `property.occupancy_rate` to 1.** 404 rows are null, mostly HMN, where
occupancy is disclosed for the portfolio rather than per property. 27 rows are genuinely 0.

**`transaction.interest_pct` null no longer means 100%.** It is now 1.0 explicitly. One row is
null because it covers two different stakes.

---

## Checklist

- [ ] Rename the 8 columns in §1
- [ ] Remove the deleted columns in §2 from queries and UI
- [ ] Multiply `aggregate_leverage`, `cost_of_debt`, `portfolio_occupancy` by 100 for display
- [ ] Replace stored gain with the computed one, and show `basis` alongside it
- [ ] Drop `line`, `amount`, `pay_date` from `distribution_record` handling
- [ ] Group by `deal_id` before summing transaction money
- [ ] Group by `basis_segment` before summing `pct`
- [ ] Remove any "announced transactions" view
- [ ] Check null handling against §10
