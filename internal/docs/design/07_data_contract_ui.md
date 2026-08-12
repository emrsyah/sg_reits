# 07 — Data contract → UI map (engineering-facing)

Binds every UI module to **exact fields** so the frontend agent never guesses. Source of truth for
shapes: `schema/models.py` + `db/schema.sql` (our REITs DB) and the prod table DDL (sectors.app).
This refines the loose `[OURS]/[LIVE]/[EDIT]` tags in [`03_design_brief.md`](03_design_brief.md) §4.

> **Focus discipline:** the REITs DB (`sgx_reit_*`) is the **authoritative, page-cited core**. Prod
> tables are **enrichment** (breadth, live price, history, news) — they never overwrite a page-cited
> number, and the product's identity stays "read from the source."

---

## 1. Source taxonomy (4 tags) + authority rule

| Tag | Meaning | Tables | Cited? | Refresh |
|---|---|---|---|---|
| **`[REIT-DB]`** | Our extraction — the authoritative core | `sgx_reit_*` (8 tables) | **Yes — `source_page`** | ~yearly |
| **`[PROD]`** | sectors.app existing prod tables — enrichment | `sgx_daily_data`, `sgx_news`, `sgx_financials_annual`, `sgx_filings`, `sgx_short_sell` | No | live / multi-year |
| **`[DERIVED]`** | Computed by combining sources — **must be labelled derived, never shown as disclosed** | e.g. yield, P/B, cohort medians, the safety verdict | n/a | on read |
| **`[EDIT]`** | Editorial guides | `guides_ux/` | n/a | manual |

**Authority rule (the seam, made concrete):**
1. For **FY2025**, a `[REIT-DB]` value **always wins** over any `[PROD]` value and shows its `source_page`.
2. `[PROD]` supplies what we don't hold: **live price**, **prior-year** financials, **news**, **filings**, **short interest**.
3. A `[DERIVED]` value that mixes live + annual (yield, P/B) renders inside a **dated frame**
   ("price live · NAV FY2025"). Never blend silently.

---

## 2. Provenance contract (the wedge — how `📄 p.N` works)

Every `[REIT-DB]` record carries `source_page` (int, nullable). To open the cited page:

```
presigned_R2_url( reit_report.pdf_r2_key )  +  "#page=" + (record.source_page + reit_report.page_offset)
```
- `reit_report` is keyed by `(symbol, financial_year)` → gives `pdf_r2_key` + `page_offset`
  (printed→physical drift correction). Presign server-side (see `docs/fe_data_contract.md` §6).
- `source_page IS NULL` → render the value **without** a 📄 affordance + a muted "page not attributed"
  tooltip. **Never** fabricate a page. (This is also a `columns_never_fillable` candidate.)

---

## 3. Units & formatting conventions (from `models.py` docstring — FE must honour)

| Field kind | Stored as | Render |
|---|---|---|
| Money (valuation, revenue, NPI, NDI…) | **absolute units** (NOT $'000) | currency-aware, `currency` col; prod normalizes to SGD at load |
| Percentages (gearing, occupancy, npi_pct, cost_of_debt, pct…) | **plain number** (`33.9` = 33.9%) | append `%` |
| `dpu` | **cents**, full-year | show as cents or convert to $ for yield |
| `interest_coverage_ratio` | **x (times)** `3.2` | append `×` |
| `weighted_avg_debt_maturity`, `wale`, `lease_term_years` | **years** | append `yrs` |
| `nav_per_unit` | trust **currency**, per unit | currency-aware |
| `top_tenant.revenue_pct` | **plain number** in our table (prod stores `0.05` fraction) | append `%` |
| areas `gla/nla/gfa` | number + `area_unit` (`sqft`\|`sqm`) | show unit; prod → sqft at load |

⚠️ **Two taxonomies, do not conflate:** `profile.sub_sector` = **7-value** REIT classification
(Retail/Office/Industrial/Hospitality/Healthcare/Data Centre/Diversified). `property.category` =
**6-value** asset class (Industrial & Logistics/Office/Retail/Data Centers/Specialized/Diversified
(Commercial)). The 8th "Specialized" label flagged in [`05`](05_decisions_and_open_questions.md) Q1
is an asset-category value leaking into sub-sector usage — resolve before grouping.

---

## 4. Per-module field map (MVP modules)

`P` = `sgx_reit_performance` · `PR` = `sgx_reit_property` · `T` = `sgx_reit_top_tenant` ·
`TM` = `sgx_reit_trade_mix` · `F` = `sgx_reit_financial` · `PF` = `sgx_reit_profile` ·
`TX` = `sgx_reit_property_transaction` · `N` = `sgx_reit_notes`.

### Hero: Distribution-Safety Verdict
| UI element | Field(s) | Tag |
|---|---|---|
| Verdict band + sentence | computed from the drivers below — see [`08_verdict_methodology.md`](08_verdict_methodology.md) | `[DERIVED]` |
| Driver chips | `P.aggregate_leverage` (%), `P.interest_coverage_ratio` (×), `P.cost_of_debt` (%), `P.weighted_avg_debt_maturity` (yrs), `P.portfolio_occupancy` (%), `P.wale` (yrs) — each + `P.source_page` | `[REIT-DB]` |
| DPU coverage | `P.net_distributable_income`, `P.dpu` | `[REIT-DB]` |
| Live yield | `(P.dpu/100) ÷ sgx_daily_data.price × 100` | `[DERIVED]` (PROD+REIT-DB) |
| Price-to-NAV | `sgx_daily_data.price ÷ P.nav_per_unit` | `[DERIVED]` |
| Anomaly flags | `P.flags` jsonb `[{type, scope, note}]` | `[REIT-DB]` + `[EDIT]` copy |

### Refinancing snapshot
| UI element | Field(s) | Tag |
|---|---|---|
| Gearing gauge vs 50% cap | `P.aggregate_leverage` | `[REIT-DB]` |
| Cost of debt / ICR / WADM | `P.cost_of_debt`, `P.interest_coverage_ratio`, `P.weighted_avg_debt_maturity` | `[REIT-DB]` |
| ⚠️ Fixed/floating % | **NO COLUMN EXISTS** — drop or add an extraction field (logged `05`) | — |
| ⚠️ Maturity ladder | **cut** — only the `weighted_avg_debt_maturity` scalar exists | — |

### FY2025 distribution detail
| UI element | Field(s) | Tag |
|---|---|---|
| DPU + NDI coverage | `P.dpu`, `P.net_distributable_income`, `P.number_of_unitholders` | `[REIT-DB]` |
| Composed FY periods | `P.distribution_record` jsonb `[{period, dpu, ex_date, pay_date}]` | `[REIT-DB]` |
| Equity-raise flag | `P.flags` (e.g. `dpu_half_year_split`) | `[REIT-DB]` |

### Portfolio decomposition (one row per property)
| UI element | Field(s) | Tag |
|---|---|---|
| Property table | `PR.property_name`, `PR.country`, `PR.category` (6-value), `PR.market_valuation` + `PR.currency`, `PR.occupancy_rate`, `PR.net_property_income`, `PR.gross_revenue`, `PR.npi_pct`, `PR.land_tenure`, `PR.lease_expiry_date`, `PR.lease_term_years`, `PR.gla/nla/gfa` + `PR.area_unit`, `PR.ownership`, `PR.status`, `PR.divestment_price` — each + `PR.source_page` | `[REIT-DB]` |
| Per-property tenants/mix | `PR.major_tenants` jsonb `[{name, industry, pct}]`, `PR.trade_mix` jsonb `{category: pct}` | `[REIT-DB]` |
| Reconciliation badge | `Σ PR.market_valuation` vs `P.portfolio_value` (tolerance for JV/rounding) | `[DERIVED]` |
| Honest-gap note | `PR.flags`; `N.notes.columns_never_fillable` (e.g. segment-only NPI) | `[REIT-DB]` |

### Tenant concentration + trade-mix
| UI element | Field(s) | Tag |
|---|---|---|
| Top-tenant table | `T.rank`, `T.client_name` (NULL = anonymized → show "Confidential"), `T.industry` (15-value), `T.revenue_pct`, `T.pct_basis`, `T.source_page` | `[REIT-DB]` |
| Top-1/top-10 concentration | `Σ T.revenue_pct` | `[DERIVED]` |
| Trade-mix donut | `TM.category` (15-value), `TM.category_raw`, `TM.pct`, `TM.pct_basis`, `TM.source_page` | `[REIT-DB]` |

### Financials (Later) — **now with multi-year via prod**
| UI element | Field(s) | Tag |
|---|---|---|
| FY2025 statements (authoritative) | `F.income_stmt_metrics` / `F.balance_sheet_metrics` / `F.cash_flow_metrics` jsonb; `F.line_items` `[{statement, component, amount, label_raw, source_page}]` | `[REIT-DB]` |
| Multi-year trend (history) | `sgx_financials_annual` (same blob shape, keyed by `financial_year`) | `[PROD]` |
| FFO | `F.income_stmt_metrics.funds_from_operation` — **null 36/36** → teach NDI as the SG equivalent | `[REIT-DB]` |
| Reconciliation | `Σ line_items (revenue − expense + signed adj)` = `income_stmt_metrics.net_income` | `[DERIVED]` |

### Profile, transactions & provenance ledger
| UI element | Field(s) | Tag |
|---|---|---|
| Profile | `PF.sub_sector`, `PF.management` jsonb `[{role, company_name}]`, `PF.income_model` | `[REIT-DB]` |
| Transactions (Later) | `TX.transaction_type`, `TX.property_name`, `TX.carrying_value`, `TX.net_proceeds`, `TX.gain_on_divestment`, `TX.purchase_price`, `TX.currency`, `TX.raw`, `TX.source_page` | `[REIT-DB]` |
| Provenance ledger / honest gaps | `N.notes` jsonb `{columns_never_fillable, data_with_no_home, parsing_traps, inferred, reconciliation}` | `[REIT-DB]` + `[EDIT]` |
| PDF reader | `reit_report.pdf_r2_key`, `reit_report.page_offset` (§2) | R2 |

### Sub-sector explorer · Screener · Landing market-pulse
| UI element | Field(s) | Tag |
|---|---|---|
| Cohort grouping | `PF.sub_sector` | `[REIT-DB]` |
| Cohort medians (n-aware) | median over `P.*` per sub-sector | `[DERIVED]` |
| Screener columns | `P.*` (structural) + safety composite + yield/PB | `[REIT-DB]` + `[DERIVED]` |
| Market pulse | count `[REIT-DB]`; market cap = `price × units` `[DERIVED]`; avg yield `[DERIVED]`; spread vs SG 10Y `[PROD/external]`; medians `[DERIVED]` | mixed |

---

## 5. Prod-table enrichment modules (secondary to the core)

| Module | Query | Join key | When |
|---|---|---|---|
| **Per-REIT news** | `sgx_news WHERE symbols @> ARRAY[symbol]` order by `timestamp` | `symbols[]` ⊇ symbol | **MVP** (list) / sentiment via `score`,`dimension` Later |
| **Sub-sector / market news** | `sgx_news WHERE sub_sector && [...]` / recent | `sub_sector[]` | Explorer / landing |
| **Ownership & filings** | `sgx_filings WHERE symbol = ?` order by `timestamp` | `symbol` | Later — sponsor stake trend (combine `PF.management`) |
| **Short interest** | `sgx_short_sell WHERE symbol = ?` recent | `symbol`/`name` | Later — positioning mini + screener flag |
| **Live price / yield / P-B** | `sgx_daily_data` latest | `symbol` | **MVP** (the seam) |
| **Multi-year financials** | `sgx_financials_annual WHERE symbol = ?` | `(symbol, financial_year)` | Later — financials trend |

---

## 6. Derived values & compute location (resolves [`05`](05_decisions_and_open_questions.md) Q-D)

These are `[DERIVED]` — decide **where** each is computed (SQL view / loader / FE). Recommendation:
pre-compute the cross-row aggregates in a **DB view**, compute price-dependent values in the FE/RSC
(they change intraday):

| Value | Inputs | Recommended location |
|---|---|---|
| Distribution-safety verdict + band | `P.*` (see `08`) | **DB view or RSC** (deterministic; cache) |
| Live yield, Price/NAV | `sgx_daily_data.price` + `P.dpu`/`P.nav_per_unit` | **RSC** (intraday) |
| Cohort medians / percentiles (n-aware) | `P.*` grouped by `PF.sub_sector` | **DB view** |
| Top-N tenant concentration | `Σ T.revenue_pct` | DB view or FE |
| Σ-valuation reconciliation | `Σ PR.market_valuation` vs `P.portfolio_value` | DB view or FE |
| Market cap, market-pulse aggregates | price × units; medians | RSC |

---

## 7. Open data questions (for the data-integration owner)

1. **Co-location:** are the prod tables (`sgx_*`) in the **same Postgres** as `sgx_reit_*` (can JOIN),
   or a **separate prod DB** (need an API / FDW / replication)? Changes the whole fetch strategy.
2. **Symbol key normalization:** our keys are `.SI`-suffixed (`AJBU.SI`); confirm `sgx_news.symbols[]`,
   `sgx_filings.symbol`, `sgx_short_sell.symbol`, `sgx_financials_annual.symbol`, `sgx_daily_data`
   use the same form, else a mapping table is needed.
3. **Units for market cap:** is units-outstanding available (`income_stmt_metrics.diluted_shares_outstanding`
   or a prod field)? Needed for market cap + correct yield.
4. **Multi-year coverage:** how many prior years does `sgx_financials_annual` actually hold for our 36
   REIT symbols, and do FY2025 prod values reconcile with our page-cited FY2025 (define the tolerance + which wins)?
5. **SG 10Y bond yield** (for the yield-spread) — which prod/external source?
