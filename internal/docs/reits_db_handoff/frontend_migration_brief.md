# SGX-REIT frontend migration brief: move off raw `sgx_reit_*` -> `sgx_reit_*_final`

For the FE agent. **Goal:** repoint the REIT frontend from the raw `sgx_reit_*` tables to the new
`sgx_reit_*_final` tables, and surface the new fields we added. Inspect the live `*_final` tables
directly to confirm exact shapes — this doc is the map + the "why".

---

## 1. TL;DR — what to change

- **Read from `sgx_reit_*_final`, not `sgx_reit_*`.** The `*_final` tables are a clean, consumer-ready
  projection of the raw tables:
  - **All money is SGD** (foreign REITs already FX-converted; no currency column, no per-figure
    currency tags). Do NOT convert anything in the FE.
  - **All areas are sqm** (sqft converted; no `area_unit`).
  - **Provenance stripped** (no `source_page`, `flags`, `*_basis`, `*_raw`, `_notes`, `line_items`).
  - **Column names expanded** to full words (glossary in section 5).
- The raw tables stay as the audited system-of-record (do not read them in the FE anymore).
- **`sgx_manual_input` is unchanged** and out of scope for this migration.

7 final tables (all keyed `symbol` + `financial_year`, except profile = per trust):
`sgx_reit_profile_final`, `sgx_reit_performance_final`, `sgx_reit_financial_final`,
`sgx_reit_property_final`, `sgx_reit_top_tenant_final`, `sgx_reit_trade_mix_final`,
`sgx_reit_property_transaction_final`.

---

## 2. How the data is produced (context for presenting it well)

- **Source:** each REIT's **audited annual report** (financial statements + notes). Values are
  **as-disclosed** — read verbatim, never computed/imputed unless a rule below says so. Where a
  figure isn't disclosed it is **null** (render "—"/"not disclosed", never 0).
- **Currency:** every REIT's figures normalized to **SGD** using MAS quarterly FX at the period-end
  date. 9 REITs report in a foreign currency natively (USD/EUR/GBP) — already converted. (A handful
  of Vietnam-dong property figures have no FX rate and are null by design.)
- **Areas:** normalized to **sqm**.
- **Coverage:** 47 REIT-years (37 trusts; the 10 largest also have a prior FY). One row per trust
  per financial year.

---

## 3. The tables + key columns (final names; all money SGD, areas sqm)

### `sgx_reit_profile_final` (per trust)
`symbol, sub_sector, management`. `management` (jsonb) is **keyed by role, value is an array of
company names**: `{"reit_manager": [...], "trustee": [...], "sponsor": [...], "property_manager":
[...], "operator": [...], "master_lessee": [...]}` — value is ALWAYS a list (roles repeat, e.g.
several property managers). Roles present vary per trust; iterate the object's entries.

### `sgx_reit_performance_final` (per symbol-year) — the KPI + distribution table
Identity/KPIs: `date` (FY-end), `source_url` (direct link to the annual-report PDF on R2 — use for a "View annual report" action; populated 47/47), `properties_location`, `number_of_unitholders`,
`number_of_shareholder_units`, `aggregate_leverage`, `interest_coverage_ratio`, `cost_of_debt`,
`weighted_average_debt_maturity`, `weighted_average_lease_expiry`, `portfolio_occupancy`,
`net_asset_value_per_unit` (SGD), `distribution_per_unit` (cents), `distribution_period_months`,
`distribution_record` (jsonb: per-period DPU), `portfolio_value`, `gross_revenue`,
`net_property_income` (all SGD).

Distribution block (SGD) — **NEW, present as a story (see section 4):**
`net_distributable_income`, `adjusted_distributable_income`, `distribution_paid`,
`distributable_income_opening`, `distribution_cash_paid`, `distributable_income_closing`,
`distribution_pool_other_movements`, `units_to_be_issued`.

### `sgx_reit_financial_final` (per symbol-year) — the 3 statement blobs (jsonb, SGD)
`income_stmt_metrics`, `balance_sheet_metrics`, `cash_flow_metrics`, `employee_breakdown`.
`income_stmt_metrics` keys include: total_revenue, cost_of_revenue, gross_income (=NPI),
operating_income (=NOI), operating_expense, **ebit, ebitda, depreciation**, pretax_income,
income_taxes, net_income, non_operating_income_or_loss, **interest_expense_non_operating**,
**minorities, perpetual_security_holders** (now negative), unitholders, net_property_sales,
**funds_from_operation**, basic_shares_outstanding, diluted_shares_outstanding,
revenue_breakdown[], operating_expense_breakdown[]. `cash_flow_metrics`:
operating/investing/financing_cash_flow, net_cash_flow, **capital_expenditure** (positive),
free_cash_flow.

### `sgx_reit_property_final` (per symbol-year-property) — the portfolio registry
`property_name, country, category, address, ownership, market_valuation (SGD), purchase_price (SGD),
valuation_date, net_property_income (SGD), gross_revenue (SGD), occupancy_rate,
gross_lettable_area (sqm), net_lettable_area (sqm), gross_floor_area (sqm), land_tenure,
lease_expiry_date, status, purchase_date`.

### `sgx_reit_top_tenant_final` / `sgx_reit_trade_mix_final`
Top tenants by GRI% (`rank, client_name, industry, revenue_pct, pct_basis`) and sector/trade-mix
(`category, pct, pct_basis`). `revenue_pct`/`pct` are 0-100 plain numbers (divide by 100 for a
fraction if needed).

### `sgx_reit_property_transaction_final` (per symbol-year-deal) — acquisitions/divestments
`deal_id, transaction_type, status, property_name, description, counterparty, interest_pct,
announced_date, completed_date, transaction_date, gain_loss_pct, gain_basis, valuation_date,
source_type, announcement_refs, purchase_price, sale_price, net_sale_proceeds, carrying_value,
gain_on_divestment, valuation` (money SGD). Standalone surface — a per-deal table.

---

## 4. NEW fields since the FE was last built — what they mean + how to present

### 4a. Distribution rollforward (the pool "story")
A REIT's distributable income is a **pool** that carries across years. Present as a small waterfall,
not raw numbers:
```
distributable_income_opening  (A)  pool carried in from last year
+ net_distributable_income    (B)  income generated & available this year (before retention)
+ distribution_pool_other_movements  signed: divestment-gain top-ups (+) / retentions (-)
- distribution_cash_paid      (P)  cash actually paid out this year (period-mixed, may incl capital)
= distributable_income_closing (E) pool carried to next year   [= next year's opening]
```
Guard that holds: **A + B + other − P = E**. Also separate:
- `distribution_paid` = amount **declared for the year** (the DPU basis) — use for payout ratio /
  yield. Distinct from `distribution_cash_paid` (actual cash out, cross-period). Don't conflate.
- `adjusted_distributable_income` = fee-in-cash variant (only ~2 REITs; usually null).
- **Label `P > B`** as "paid more than earned this year — drew down the pool", not an error.
- Some REITs suspended/withheld distributions (e.g. CMOU): `distribution_cash_paid` can be ~0 with a
  large negative `distribution_pool_other_movements` (retention). Badge "distributions suspended/
  withheld" rather than showing 0 yield as a bug.

### 4b. Units + diluted DPU
- `number_of_shareholder_units` = units **already issued** at year-end.
- `units_to_be_issued` = units **committed but not yet issued** (Manager fees payable in units).
  **Basic DPU** divides by shareholder units; **diluted DPU** divides by
  `number_of_shareholder_units + units_to_be_issued`. Show both where useful. `units_to_be_issued`
  is null for REITs that don't disclose a separate line.

### 4c. Financial metrics normalized to the analyst convention (REIT-specific)
These now follow the standard REIT treatment (were previously our-derived or missing):
- `ebit` = **Net Operating Income** (NOI) — REIT convention.
- `depreciation` = P&E depreciation + net fair-value change of investment properties (the REIT D&A
  equivalent; can be negative when properties gained value).
- `ebitda` = pretax_income + interest + depreciation.
- `interest_expense_non_operating` = **finance costs as declared** (positive). (Name kept for
  system compatibility; it is really an operating cost for REITs — you may label it "Finance costs"
  in the UI.)
- `funds_from_operation` (FFO) = net_income + depreciation − property-sale gains — "core operations
  before buying/selling property."
- `capital_expenditure` = all investment-property spend from the cash-flow statement, **positive**.
- `minorities` / `perpetual_security_holders` are now **negative** (deductions from total return).

### 4d. Property transactions
`sgx_reit_property_transaction_final` is new to the FE — a per-deal acquisition/divestment feed with
gain %, dates, counterparty, and (where sourced) SGX announcement links (`announcement_refs`,
`source_type`). Good for a "capital recycling / deals" section. Note: selling prices aren't always
disclosed, so some money fields are null.

---

## 5. Column-rename glossary (raw -> final) — update FE field references
| raw | final |
|---|---|
| `dpu` | `distribution_per_unit` |
| `dpu_period_months` | `distribution_period_months` |
| `nav_per_unit` | `net_asset_value_per_unit` |
| `wale` | `weighted_average_lease_expiry` |
| `weighted_avg_debt_maturity` | `weighted_average_debt_maturity` |
| `gla` / `nla` / `gfa` | `gross_lettable_area` / `net_lettable_area` / `gross_floor_area` |
| `financial.weighted_avg_shares_basic` | `income_stmt_metrics.basic_shares_outstanding` |

jsonb blob sub-keys (income_stmt_metrics etc.) keep prod's names — do NOT rename inside blobs.

---

## 6. Migration checklist
1. Swap every query `sgx_reit_<x>` -> `sgx_reit_<x>_final`.
2. Remove any FE-side FX conversion / currency labels (everything is SGD) and any sqft handling.
3. Update renamed field references (section 5).
4. Drop references to provenance columns (source_page/flags/currency/_raw/etc.) — gone in final.
5. Add UI for the new fields: distribution rollforward waterfall (4a), diluted DPU (4b), FFO/EBITDA
   (4c), property-transaction deals feed (4d).
6. Render null as "—/not disclosed", never 0.
7. Verify against the live `*_final` tables (row counts: profile 37, performance 47, financial 47,
   property 2440, top_tenant 504, trade_mix 515, property_transaction 145).

Companion docs (deeper detail): `final_schema_proposal.md` (full schema + currency rule),
`manual_vs_ours_parity.md` (the convention definitions + transcript), `manual_input_mapping.md`.
