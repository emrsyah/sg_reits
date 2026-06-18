# REITs DB → `sgx_manual_input` mapping

How the SGX REITs extraction (our 6-table DB) relates to prod's `sgx_manual_input`.
For Emir + Gerald. Companion to `schema/sgx_reit_schema.md` (the REIT schema) and
`ref_sgx_manual_input_extraction/idx_manual_input_extraction.py` (prod's existing Excel→
`sgx_manual_input` builder).

## 0. Two targets — don't conflate them

1. **REITs DB** = our **6 tables** (`sgx_reit_profile / property / performance / top_tenant /
   trade_mix / financial`). **Extraction writes here directly.** Source of truth, full granularity.
2. **`sgx_manual_input`** = prod table. **We do NOT push into it directly.** Gerald **derives /
   projects** it FROM the REITs DB later.

So `financial` does not need to "be" `sgx_manual_input`. A `sgx_manual_input` row is assembled
from **several** of our tables; `financial` supplies only the financial-statement portion.

> Flow (Jun 17 meeting): Annual Report → extraction → **REITs DB** → manual verification →
> (Gerald's transform) → `sgx_manual_input` / downstream.

## 1. `sgx_manual_input` row ← REITs DB (the projection)

One `sgx_manual_input` row per `(symbol, financial_year)` is built from
`financial + top_tenant + trade_mix + property + performance`:

| `sgx_manual_input` column | source (REITs DB) | transform |
|---|---|---|
| `symbol`, `financial_year` | any table (key) | copy (both keep the `.SI` suffix — no strip) |
| `income_stmt_metrics` (jsonb) | `financial.income_stmt_metrics` | **copy 1:1** |
| `balance_sheet_metrics` (jsonb) | `financial.balance_sheet_metrics` | **copy 1:1** |
| `cash_flow_metrics` (jsonb) | `financial.cash_flow_metrics` | **copy 1:1** |
| `sankey_component` (jsonb) | `financial.income_stmt_metrics` | **derive** (see §3) |
| `industry_breakdown.top_10_gri%_customers` | `top_tenant` | `[{industry, client_name, revenue_pct÷100}]` |
| `industry_breakdown.gross_rental_income_by_sectors` | `trade_mix` | `{category: pct÷100}` |
| `industry_breakdown.property_portfolio_top_20` | `property` | top-20 by `gross_revenue`; **rename our columns → prod names** (see note below) |
| `industry_breakdown.property_counts_by_country` | `property` | `{country: {category: [count, Σgross_revenue, Σmarket_valuation]}}` |
| `source_url` | `performance.source_url` | copy |
| `date` | `performance.date` | copy (FY-end) |
| `employee_breakdown` | `financial.employee_breakdown` | copy (usually `null` for REITs; prod nulls it too) |
| `updated_on` | — | load timestamp |

**Projection field renames (do these in the transform, NOT in our source columns):**

| `property_portfolio_top_20` field (prod) | our `property` column |
|---|---|
| `name` | `property_name` |
| `valuation` | `market_valuation` |
| `gross_income` | `gross_revenue` |
| `country`, `category`, `occupancy_rate` | same names (no rename) |

Plus the unit conversions: `top_tenant.revenue_pct ÷ 100` (we store 5.0, prod 0.05) and
`trade_mix.pct ÷ 100`.

*Why rename here, not in the source:* (1) our `gross_income` already means **NPI** inside
`financial.income_stmt_metrics`, so renaming `property.gross_revenue → gross_income` would make
one name mean two things across the DB; (2) `market_valuation` deliberately encodes "audited-FS
value, not agreed price" (the §2 valuation rule); (3) `property` is the full per-asset registry,
not just this 6-field summary. So the source keeps clear, unambiguous names and the projection
does the three trivial renames — Gerald's transform is still effectively a copy.

## 2. The three buckets

**🟦 Integrated into `sgx_manual_input` (generic / cross-company):**
`financial.{income_stmt,balance_sheet,cash_flow}_metrics` (copied), `sankey_component`
(derived from financial), `industry_breakdown` (composed from property + top_tenant +
trade_mix), `source_url` + `date` (from performance).

**🟩 Uniquely REIT-specific (lives in REITs DB; `sgx_manual_input` gets only a summary or nothing):**
- `property` — the **full per-property registry** (valuation, NPI, occupancy, tenure, land lease,
  per-property trade_mix). `sgx_manual_input` only takes **top-20 + country counts**.
- `performance` — `portfolio_value, net_property_income, net_distributable_income, dpu,
  distribution_record, number_of_unitholders`. **No home in `sgx_manual_input`** — REIT enrichment.
- `profile` — `sub_sector`, `management` (manager entities). REIT-only.
- `trade_mix` / `top_tenant` as **full tables** (sgx_manual_input only folds them into `industry_breakdown`).

**🟨 Purely ours / internal (never leaves the REITs DB):**
- `financial.line_items` — the audited Statement-of-Total-Return audit trail / reconciliation anchor.
- All `source_page` provenance, `flags`, and `*_raw` columns (`category_raw`, `tenure_raw`, …).

## 3. `sankey_component` is derived, not stored

Prod builds it from `income_stmt_metrics` (`make_sankey_component` in the colab). Reconstruct:
- each `revenue_breakdown[i]` → link `{category} → "Total Revenue"`
- `"Total Revenue" → "Cost of Revenue"` (= `cost_of_revenue`); `"Total Revenue" → "Gross Profit"` (= `gross_income`)
- `"Gross Profit" → "Operating Income"` (= `operating_income`); `"Gross Profit" → "Operating Expense"`
- each `operating_expense_breakdown[i]` → link `"Operating Expense" → {category}`

(Matches the M44U `sankey_component` shape exactly — that's why we don't store it.)

## 4. Conventions we copy from prod (`idx_manual_input_extraction`)

- **Missing → `null`** (`none_value_extractor`). `employee_breakdown = null` when absent — prod does the same.
- **Expense scalars are POSITIVE magnitudes:** `cost_of_revenue`, `operating_expense`,
  `income_taxes`, `interest_expense_non_operating` (prod negates the source). `non_operating_
  income_or_loss` and `net_property_sales` stay **signed**. Breakdown `amount`s positive.
- **Breakdown reconciliation:** `Σ revenue_breakdown ≈ total_revenue`,
  `Σ operating_expense_breakdown ≈ operating_expense`, within **2%** (gate-checked).
- `revenue_pct` unit: we store plain (5.0); prod stores a fraction (0.05) → `÷100` in the
  transform (the only unit conversion, and it's on `top_tenant`).

## 5. Resolved direction (Evelyn, Jun 2026)

- **No hidden REIT schema to mirror — we define it.** Evelyn confirmed: data not already in
  `sgx_manual_input` (the REIT keys `funds_from_operation` / `net_property_sales` / `unitholders` /
  `perpetual_security_holders`, the REIT-shaped `industry_breakdown`) **was never collected before** —
  our batch is the first. So `idx_manual_input_extraction.py` having no REIT branch is expected, and
  **our `sgx_reit_*` schema is the authority** for the REIT shape.
- **Direction is REIT DB → `sgx_manual_input`** ("sgx_manual_input could call the data from REIT db
  instead"). This doc's projection is the canonical transform; prod consumes from us, not vice-versa.
- **AR-absent fields → `null`** (`employee_breakdown`, some balance-sheet / cash-flow lines for
  certain trusts) — consistent with "not collected before"; matches the colab's own null behaviour.
- **FK note (still open, low priority):** `financial` is the sector-agnostic financial-statement
  core; if it ever generalises beyond REITs, re-point its `references sgx_reit_profile(symbol)` at
  the generic company symbol.

## 6. One-line model

> Extraction → **REITs DB (6 tables, full granularity)**. `sgx_manual_input` is a downstream
> projection: 3 financial blobs copied from `financial`, `sankey` derived from it,
> `industry_breakdown` composed from property/top_tenant/trade_mix, `source_url`/`date` from
> performance — while performance KPIs + the full property registry + profile + `line_items`
> stay **uniquely ours**.
