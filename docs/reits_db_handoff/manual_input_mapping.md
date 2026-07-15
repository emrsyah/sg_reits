# REITs DB -&gt; `sgx_manual_input` mapping

How the SGX REITs extraction relates to prod's `sgx_manual_input`. Companion to
`final_schema_proposal.md` (the `sgx_reit_*_final` schema) and
`ref_sgx_manual_input_extraction/idx_manual_input_extraction.py` (prod's old Excel-&gt; `sgx_manual_input`
builder, now superseded).

## 0. Three layers

1. **Raw REITs DB** = our **7 tables** — `sgx_reit_profile / performance / financial / property /  top_tenant / trade_mix / property_transaction`. Extraction writes here. Full granularity + audit
rail (provenance, per-figure currency, flags). System of record.
2. **Final tables** = `sgx_reit_*_final` — SGD-normalized, sqm-normalized, provenance-stripped,
enamed clean projection of the raw tables (see `final_schema_proposal.md`). Built by
scripts/db/build_final_tables.py`.
3. `**sgx_manual_input**` = prod's consumer table, one row per `(symbol, financial_year)`. A
ownstream **projection** — we compute it, we do not hand-type it.

> Flow: Annual Report -&gt; extraction -&gt; **raw REITs DB** -&gt; `build_final_tables.py` -&gt;
> `**sgx_reit_*_final**` (SGD, clean) -&gt; projection -&gt; `**sgx_manual_input**`.

The projection now sources from the **final** tables, so it is a pure copy/derive/compose with **no
currency logic** (FX already applied in the final-table build). This supersedes the old Excel-hybrid
`SGX REIT upsert.ipynb` (which typed financials + `distribution_metrics` from
`v2 - SGX - FY20xx - REIT.xlsx` and pulled only property/top_tenant/trade_mix from the DB).

**STATUS (2026-07-14):** `sgx_manual_input` is NOT yet written by us (still fed by the colleague's
notebook) and is intentionally left untouched for now. DONE so far, in RAW + FINAL only:
(1) `units_to_be_issued` + `distribution_pool_other_movements` backfills (section 8);
(2) Evelyn's meeting conventions applied to `sgx_reit_financial` income_stmt_metrics /
cash_flow_metrics (EBIT=NOI; depreciation = C/F P&amp;E dep + net FV change of IP; EBITDA = pretax +
interest + depreciation; interest = finance costs; FFO = net_income + depreciation -
net_property_sales; CAPEX = sum of IP investing outflows, positive; minorities/perps negative) —
see `manual_vs_ours_parity.md` section 5. REMAINING: build the `*_final -> sgx_manual_input`
projection itself (this doc), when approved to write `sgx_manual_input`; define annualized DPU (Muhammad).

## 1. The projection: `sgx_manual_input` &lt;- `sgx_reit_*_final`

One row per `(symbol, financial_year)`, built from `financial_final + top_tenant_final + trade_mix_final + property_final + performance_final`:


| `sgx_manual_input` field                            | &lt;- source                            | transform                                                                                               |
| --------------------------------------------------- | --------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| `symbol`                                            | any table                               | copy (keep `.SI`)                                                                                       |
| `financial_year`                                    | `performance_final.date`                | **DERIVE via FY rule** (see 4) — do NOT copy our `financial_year`                                       |
| `date`                                              | `performance_final.date`                | copy (FY-end)                                                                                           |
| `source_url`                                        | `performance_final.source_url`          | copy (per-year AR PDF link; backfilled from R2 `reit_report.pdf_r2_key`, 47/47)                          |
| `income_stmt_metrics`                               | `financial_final.income_stmt_metrics`   | copy 1:1 (already SGD; `basic_shares_outstanding` already renamed, `_derived` already dropped in final) |
| `balance_sheet_metrics`                             | `financial_final.balance_sheet_metrics` | copy 1:1 (SGD)                                                                                          |
| `cash_flow_metrics`                                 | `financial_final.cash_flow_metrics`     | copy 1:1 (SGD)                                                                                          |
| `employee_breakdown`                                | `financial_final.employee_breakdown`    | copy (usually null)                                                                                     |
| `sankey_component`                                  | `financial_final.income_stmt_metrics`   | derive (see 3)                                                                                          |
| `industry_breakdown.top_10_gri%_customers`          | `top_tenant_final`                      | `[{industry, client_name, revenue_pct/100}]`, top-10 by pct                                             |
| `industry_breakdown.gross_rental_income_by_sectors` | `trade_mix_final`                       | `{category: pct/100}`, sum per category                                                                 |
| `industry_breakdown.property_portfolio_top_20`      | `property_final`                        | top-20 by `gross_revenue` (already SGD); renames below                                                  |
| `industry_breakdown.property_counts_by_country`     | `property_final`                        | `{country: {category: [count, sum gross_revenue, sum market_valuation]}}` (SGD)                         |
| `industry_breakdown.distribution_metrics`           | `performance_final`                     | see 2                                                                                                   |
| `updated_on`                                        | --                                      | load timestamp                                                                                          |


`**property_portfolio_top_20` field renames (in the transform):**


| prod field                                               | our `property_final` column          |
| -------------------------------------------------------- | ------------------------------------ |
| `name`                                                   | `property_name`                      |
| `valuation`                                              | `market_valuation`                   |
| `gross_income`                                           | `gross_revenue`                      |
| `country`, `category`, `occupancy_rate`, `ownership_pct` | same (occupancy_rate/ownership /100) |


Unit conversions in the transform: `top_tenant_final.revenue_pct / 100` (we store 5.0, prod 0.05),
`trade_mix_final.pct / 100`, `occupancy_rate / 100`, `ownership / 100`. **No FX** — final is SGD.

## 2. `industry_breakdown.distribution_metrics` &lt;- `performance_final`

Verified vs the actual FY2024/FY2025 `.xlsx` on C38U (Dec FYE), J69U (Sep FYE), BUOU (fee-adjusted).
**Two name collisions** — the target key does NOT map to the same-named source column:


| target subfield                 | &lt;- source column                                                                                                    | note                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| ------------------------------- | ---------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `adjusted_distributable_income` | `COALESCE(adjusted_distributable_income, net_distributable_income)`                                                    | "for the financial year" — fee-adjusted figure where one exists (BUOU 255,515k, M1GU), else plain for-year NDI (C38U 761,592k, J69U 213,221k). NOT a straight copy of `net_distributable_income`.                                                                                                                                                                                                                                     |
| `distributable_income`          | `distributable_income_opening + adjusted_distributable_income(above) + COALESCE(distribution_pool_other_movements, 0)` | "including retained from previous year" = opening carry (A) + for-year figure + any OTHER printed pool additions/deductions (ME8U FY24/25 divestment-gains +13,354k; C2PU FY2024 capex retention -3,000k; null for most REITs). Formula reproduces the colleague's Excel 17/17 (`manual_vs_ours_parity.md` 4/4a). BUOU 131,812+255,515=387,327; C38U 371,657+761,592=1,133,249; ME8U 101,328+388,110+13,354=502,792. Display-derived. |
| `distribution_paid`             | `distribution_cash_paid` (P)                                                                                           | "including last dividend from last year's final cycle" = cross-year cash line. NOT `performance.distribution_paid` (that is the declared/DPU figure).                                                                                                                                                                                                                                                                                 |
| `end_of_year_distribution`      | `distributable_income_closing` (E)                                                                                     | "amount available at end of year" = rollforward closing.                                                                                                                                                                                                                                                                                                                                                                              |
| `end_of_year_shareholder_units` | `number_of_shareholder_units`                                                                                          | units in issue at year-end, issued-only. C38U 7,298,470k / J69U 1,811,673k match .xlsx.                                                                                                                                                                                                                                                                                                                                               |
| `units_to_be_issued`            | `units_to_be_issued`                                                                                                   | AR "Units to be issued" (mgmt/acq fee units); sum with EOY units for diluted DPU.                                                                                                                                                                                                                                                                                                                                                     |


> The rollforward columns `distribution_cash_paid` / `distributable_income_closing` ARE
> `distribution_paid` / `end_of_year_distribution` here — the rollforward extraction was built for
> this blob.

## 3. `sankey_component` is derived, not stored

From `income_stmt_metrics` (`make_sankey_component` in the notebook):

- each `revenue_breakdown[i]` -&gt; link `{category} -> "Total Revenue"`
- `"Total Revenue" -> "Cost of Revenue"` (`cost_of_revenue`); `-> "Gross Profit"` (`gross_income`)
- `"Gross Profit" -> "Operating Income"` (`operating_income`); `-> "Operating Expense"`
- each `operating_expense_breakdown[i]` -&gt; link `"Operating Expense" -> {category}`

## 4. FY-label offset (transform, not copy)

`sgx_manual_input.financial_year` uses the declared-FY rule: statement date ending **Jan-Jun of X
-&gt; X-1**, **Jul-Dec of X -&gt; X**. Our tables label Jan-Jun (Mar) FYEs differently: M44U/N2IU/ME8U
31-Mar-2025 = our `financial_year=2025` but manual `FY2024`. So the projection MUST (a) derive
target `financial_year` from `date` via the rule, and (b) join child tables by `**year(date)**`
(as the notebook does for property). Never join on our `financial_year`.

## 5. What projects, what stays REIT-only

**Projected (generic / cross-company):** the 3 `financial` metric blobs (copied) + `employee_breakdown`,
`sankey_component` (derived), `industry_breakdown` (composed from property + top_tenant + trade_mix +
performance's distribution_metrics), `source_url` + `date`.

**REIT-only (in the DB, NOT in `sgx_manual_input`):**

- `profile` (sub_sector, management).
- full `property` registry (only top-20 + country counts project).
- `performance` KPIs (portfolio_value, leverage, ICR, WALE, occupancy, NAV, DPU, ...) — enrichment.
- `trade_mix` / `top_tenant` as full tables (only folded into `industry_breakdown`).
- `**property_transaction` (7th table) — does NOT project** (confirmed 2026-07-13). Standalone
acquisition/divestment surface.
- `financial.line_items` and ALL provenance (source_page, flags, `*_basis`, `*_raw`, `raw`, `_notes`).

## 6. Conventions copied from prod (`idx_manual_input_extraction`)

- **Missing -&gt; `null`**; `employee_breakdown = null` when absent (prod does the same).
- **Expense scalars are POSITIVE magnitudes:** `cost_of_revenue`, `operating_expense`, `income_taxes`,
`interest_expense_non_operating`. `non_operating_income_or_loss` / `net_property_sales` stay signed.
Breakdown `amount`s positive.
- **Breakdown reconciliation:** `sum revenue_breakdown ~= total_revenue`,
`sum operating_expense_breakdown ~= operating_expense`, within 2%.
- Fractions: `revenue_pct`/`pct`/`occupancy_rate`/`ownership` stored plain (5.0) -&gt; `/100` in the
transform (prod stores 0.05).

## 7. Target `sgx_manual_input` schema (live shape)

```sql
sgx_manual_input (
  symbol                text     not null,   -- '.SI' suffix
  financial_year        smallint not null,   -- declared FY (section 4 rule)
  date                  date,                -- FY-end statement date
  source_url            text,                -- per-year AR PDF link (from performance_final; R2-backfilled)
  income_stmt_metrics   jsonb,               -- <- financial_final (1:1, SGD)
  balance_sheet_metrics jsonb,               -- <- financial_final (1:1, SGD)
  cash_flow_metrics     jsonb,               -- <- financial_final (1:1, SGD)
  employee_breakdown    jsonb,               -- <- financial_final (usually null)
  sankey_component      jsonb,               -- derived from income_stmt_metrics
  industry_breakdown    jsonb,               -- composed (section 1)
  updated_on            timestamptz not null default now(),
  primary key (symbol, financial_year)
)
```

`industry_breakdown` jsonb sub-keys (canonical order):

```
top_10_gri%_customers          [ {client_name, industry, revenue_pct(0-1)} ]                     <- top_tenant_final
gross_rental_income_by_sectors { category: fraction(0-1) }                                       <- trade_mix_final
property_portfolio_top_20      [ {name, country, category, valuation, gross_income, occupancy_rate(0-1), ownership_pct?} ]  <- property_final (SGD)
property_counts_by_country     { country: { category: [count, sum_gross(SGD), sum_valuation(SGD)] } }  <- property_final
distribution_metrics           { distributable_income, adjusted_distributable_income, distribution_paid,
                                 end_of_year_distribution, end_of_year_shareholder_units, units_to_be_issued }  <- performance_final (section 2)
```

`income_stmt_metrics` keys (21): total_revenue, cost_of_revenue, gross_income, operating_expense,
operating_income, non_operating_income_or_loss, pretax_income, income_taxes, net_income, minorities,
perpetual_security_holders, unitholders, interest_expense_non_operating, ebit, ebitda,
net_property_sales, funds_from_operation, basic_shares_outstanding, diluted_shares_outstanding,
revenue_breakdown[], operating_expense_breakdown[]. `balance_sheet_metrics` (8) / `cash_flow_metrics`
(6) / `employee_breakdown` (4) per the live shape.

## 8. One-line model

> Raw REITs DB (7 tables, full granularity + audit trail) -&gt; `sgx_reit_*_final` (SGD, sqm,
> provenance-stripped, renamed) -&gt; `sgx_manual_input` (per symbol-year projection: 3 financial blobs
> copied, sankey derived, industry_breakdown composed incl. distribution_metrics from performance).
> The projection carries no currency logic; FX lives in the final-table build.

