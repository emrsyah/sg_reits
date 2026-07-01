# SGX REIT Database — Review Before Prod Migration

**Purpose:** materials for the call on the current proofread DB before we promote it to the production DB.
**Scope:** FY2025 corpus — **37 annual reports**, all extracted, gated, and loaded to Supabase (+ PDFs in R2).
**Prepared:** 2026-07-01.

---

## 0. The two-layer model (read this first)

We deliberately keep **two layers**. Everything below describes **Layer 1**.

| Layer | What it is | Currency | Conversions | Status |
|---|---|---|---|---|
| **1. Proofread DB** (current) | Source-faithful extraction, exactly as each annual report discloses it | **As-reported** (mixed: SGD, USD, EUR, GBP, AUD, JPY, RMB…) | **None** — we convert nothing | ✅ done, in Supabase |
| **2. Production DB** (next) | Normalised for the frontend | **SGD** (single) + sqft/common units | FX + unit normalisation on top of Layer 1 | ⬜ this migration |

**Core principle:** the proofread layer never balances or converts *by assumption*. Every value is what the report says, with a page citation. All normalisation (currency → SGD, units → sqft) happens in Layer 2 as views/transforms, so we never lose the audit trail.

---

## 1. Overall structure

**8 data tables** (the locked 6-table schema + 2 satellite tables), plus inventory/review tables for the cockpit.

```
reit_report ────────────────┐  (inventory: 1 row per symbol×FY, holds the R2 PDF key)
                             │
 sgx_reit_profile            │  1 row / symbol         — who the REIT is
 sgx_reit_performance        │  1 row / symbol × FY    — headline financials + DPU
 sgx_reit_financial          │  1 row / symbol × FY    — full income statement (1:1 metrics)
 sgx_reit_property           │  N rows / symbol × FY   — every property in the portfolio
 sgx_reit_top_tenant         │  N rows / symbol × FY   — top tenants
 sgx_reit_trade_mix          │  N rows / symbol × FY   — sector/trade breakdown
 sgx_reit_property_transaction  N rows / symbol × FY   — acquisitions & divestments
 sgx_reit_notes              │  1 row / symbol × FY    — per-report audit trail (JSON)
```

### Volume in the current DB
| Table | Rows |
|---|---|
| reports (symbol × FY) | **37** |
| properties | **1,653** |
| top tenants | **384** |
| trade-mix rows | **367** |
| property transactions | **95** (26 acquisitions, 59 completed divestments, 9 announced, 1 terminated) |

**Sub-sectors covered (8):** Data Centre, Diversified, Healthcare, Hospitality, Industrial, Office, Retail, Specialized.

---

## 2. What's in each table

### 2.1 `sgx_reit_profile` — one row per REIT
Identity of the trust.
- `sub_sector` — one of the 8 above.
- `management` (jsonb) — `[{role, company_name}]` (sponsor, manager, trustee…).
- `income_model`, `source_page`.

### 2.2 `sgx_reit_performance` — one row per REIT × FY
Headline numbers an investor scans first.
- **Size/return:** `portfolio_value`, `gross_revenue`, `net_property_income`, `dpu`, `nav_per_unit`.
- **Leverage/risk:** `aggregate_leverage`, `interest_coverage_ratio`, `cost_of_debt`, `weighted_avg_debt_maturity`.
- **Portfolio:** `wale`, `portfolio_occupancy`, `number_of_unitholders`.
- **DPU cross-check block** (added for the distribution audit — see §4):
  - `net_distributable_income` — income available to distribute, **before** capital retention.
  - `adjusted_distributable_income` — distributable income after fee adjustment (DPU method 2); **null** under method 1 (fees paid in units — all 37 are method 1).
  - `distribution_paid` — amount actually distributed/declared for the year. `net_distributable_income − distribution_paid = capital retained`.
  - `distribution_basis` — self-describing tag for how `distribution_paid` was disclosed: `disclosed_after_retention` | `suspended` | `full_payout_no_retention_line` | `not_disclosed_rollforward_only`.
- `distribution_record` (jsonb) — `[{period, dpu, ex_date, pay_date}]`.
- `currency`, `date`, `flags` (jsonb), `source_page`.

### 2.3 `sgx_reit_financial` — one row per REIT × FY
The full income statement, 1:1 with the income-statement-metrics standard (20+ keys).
- `income_stmt_metrics` (jsonb) — incl. `diluted_shares_outstanding` + `weighted_avg_shares_basic` (used for the DPU two-method cross-check).
- `balance_sheet_metrics`, `cash_flow_metrics`, `employee_breakdown` (jsonb).
- `line_items` (jsonb) — `[{statement, component, amount, label_raw, source_page}]` (the raw disclosed lines, kept verbatim).
- `currency`, `source_page`.

### 2.4 `sgx_reit_property` — N rows per REIT × FY
Every property in the portfolio. This is the biggest table (1,653 rows).
- **Identity:** `property_name`, `country`, `category` / `category_raw`, `address`.
- **Value:** `market_valuation` (current fair value), `purchase_price` (**original acquisition cost** — for capital-gain-since-purchase), `purchase_price_currency`, `valuation_date`.
- **Audit-trail currency:** `currency` (presentation), `original_currency` + `original_value` (local ccy when reported separately).
- **Economics:** `net_property_income`, `gross_revenue`, `npi_pct`, `occupancy_rate`.
- **Physical:** `gla`, `nla`, `gfa`, `area_unit` (sqft/sqm as reported).
- **Tenure:** `land_tenure`, `lease_term_years`, `lease_expiry_date`, `tenure_raw`.
- **Lifecycle:** `status` = `active` | `divested` | `held_for_sale`; `divestment_price`.
- `trade_mix` / `major_tenants` (jsonb), `flags`, `source_page`.

### 2.5 `sgx_reit_top_tenant` / `sgx_reit_trade_mix` — N rows per REIT × FY
- Top tenant: `rank`, `client_name`, `industry`, `revenue_pct`, `pct_basis`.
- Trade mix: `category` / `category_raw`, `pct`, `pct_basis`.

### 2.6 `sgx_reit_property_transaction` — N rows per REIT × FY (the one to discuss most)
Acquisitions and divestments during / announced in the year. This table got the deepest scrub — see §3 and §4.
- `transaction_type` — `acquisition` | `divestment` | `announced_divestment` | `partial_divestment` | `divestment_terminated`.
- `property_name`, `transaction_date`, `counterparty`, `status`, `currency`, `source_page`.
- **Money columns:**
  - `purchase_price` — consideration paid (acquisitions).
  - `net_proceeds` — consideration received (divestments). **⚠️ see §4.2 — mostly gross today.**
  - `carrying_value` — the property's book value just before sale (the cost base for the gain).
  - `gain_on_divestment` — disclosed accounting gain (`net_proceeds − carrying_value`).
  - `valuation` — independent appraisal at the deal.
- `raw` (jsonb) — **the full original extracted object**, so alias keys and everything we didn't map to a typed column are never lost.
- Per-value provenance is carried in text `*_basis` fields (e.g. `carrying_value_basis`) — see §5.

### 2.7 `sgx_reit_notes` — one row per REIT × FY
The per-report **audit trail** (jsonb): `columns_never_fillable`, `data_with_no_home`, `parsing_traps`, `inferred`, `reconciliation`. This is where "why is X the way it is" lives.

---

## 3. How the data was produced & QC'd

Pipeline: **Datalab parse → LLM extraction (reit-extract skill) → 2-stage QC gate → load**.

- **Gate 1 — schema (`validate_schema.py`):** type/enum contract via Pydantic. All 8 files validated (transactions now included). **All 37 PASS.**
- **Gate 2 — reconciliation (`check_extraction.py`):** fill-rate, unit sanity, revenue-bucket recon, DPU reconciliation, distribution-basis discipline.
- **Forensic auditor (reit-audit):** independent, adversarial re-read vs source — catches *plausible-but-wrong* values that gates can't (completeness ≠ correctness).
- **Invariant:** **never balance by assumption.** A failed check means investigate the source, not adjust numbers. Every value traces to a `source_page`.

---

## 4. Known issues & how we handle them (the important section)

These are the things to align on before prod. Each has a **note/flag in the DB** so it's not silently baked in.

### 4.1 Currency is mixed (by design, Layer 1)
- Values are as-reported: SGD, USD, EUR, GBP, AUD, JPY, RMB.
- **Prod fix:** convert all to SGD via a documented FX table (period-end for balances, deal-date for proceeds). Preserve `original_currency`/`original_value` for audit.
- **Live example of why it matters:** BUOU **357 Collins** has sale proceeds in **AUD** but carrying value in **SGD** — subtracting them raw is meaningless until both are SGD.

### 4.2 `net_proceeds`: gross vs net
The AR almost never discloses **per-property transaction costs** — only an aggregate "net of costs" cash-flow line covering all deals. So:
- **14 of 66** populated `net_proceeds` are **truly net** (from a per-property/per-subsidiary net line).
- **52 of 66** are actually the **gross sale price** (costs not deducted).
- **Handling:** we will add a `proceeds_basis` flag (`net` | `gross`) auto-derived from the source field, so nobody treats a gross price as net.
- **Clarification for the team:** `net_proceeds` is **not** the gain. `gain = net_proceeds − carrying_value`. net_proceeds is money-in.

### 4.3 `carrying_value` — mixed provenance (documented per row in `carrying_value_basis`)
Recovered for **66 of 68** divestments. But the basis varies:
1. **Prior-year-end fair value** (most) — from the comparative column of the AR or the prior-year AR. It's the last reported book value, not the exact sale-date value (small stub-period drift possible).
2. **Explicit disposal-date carrying** (e.g. M44U Xi'an "carrying value S$13,084,000").
3. **Derived** (UD1U, C2PU, MXNU Hilden, HMN Citadines) = proceeds ± disclosed gain.
- **`carrying_value` ≠ `valuation`.** valuation = a fresh appraisal for the deal; carrying = on-book value. Use *carrying* as the cost base for realized gains.
- **Held-for-sale rows are pre-marked to the sale price** (IFRS 5), so their implied gain is ~0 *by construction* — the real gain was booked earlier as a fair-value change (e.g. O5RU 3 Toh Tuck, SET Florence).
- **A few use an older basis** (M44U Padi/Flexhub = 1 yr older; Chee Wah/Subang = 2 yrs older) — flagged in-row.

### 4.4 Subsidiary / share sales — property carrying ≠ accounting cost base
5 deals (CY6U CyberPearl, AU8U Yuhuating, TS0U Lippo, M44U Xi'an, SET Slovakia) sold the **company that owns the property**, not the property directly.
- The audited gain is struck against the company's **net assets** (property + cash − debt − tax − FX reserve), not the property carrying.
- We store the **property-only carrying** in the field (for property-vs-property comparison) and record the **net-assets figure in `carrying_value_basis`** (that's the one that reconciles to the audited gain).
- So for these 5, `net_proceeds − carrying_value` ≠ audited gain — flag as deal-level/property-level approximation.

### 4.5 Bundled multi-property deals — no fractional split
Some transactions bundle several properties into **one row** (e.g. CY6U CyberPearl **+** CyberVale = 1 row; SET Slovakia = 5 properties; 8C8U IPO = 14 assets).
- The AR discloses consideration/carrying **combined**, so we keep them combined — splitting per property would be an assumption.
- **Per-property carrying** *is* separately available in the portfolio statement if we later need per-property granularity; **per-property sale price is not** (buyer paid one bundle price). So bundled deals are meaningful **only at the deal level**.

### 4.6 Prior-year deals appearing in a FY2025 report
M44U lists **7 divestments** that actually completed in FY23/24 (only *named* in FY2025). We recovered their figures from prior-year ARs and **flagged each** ("PRIOR-YEAR deal… review whether it belongs as an FY2025 row").
- **Decision needed:** keep them tagged, or re-home them to their real completion year. Group by **`transaction_date`**, not `financial_year`, when building the yearly deal list.

### 4.7 Announced vs completed vs terminated
- 9 `announced_divestment` (signed, not yet completed — no gain recognised yet), 1 `divestment_terminated` (deal fell through — no proceeds).
- Handled via `transaction_type` + `status`. Filter these appropriately in any "realized gains" view.

### 4.8 `purchase_price` (cost since acquisition) caveats
- **~95% filled on active** properties (1,512/1,591; 92% of all 1,653) after the Jul-1 recovery pass; the field is for **held** assets (unrealised gain = `(market_valuation − purchase_price)/purchase_price`). The remaining ~5% are documented non-disclosures (fair-value-carried hospitality/EMA portfolios, blended/staged/JV acquisitions, IPO founding assets) — each logged in the report's `_notes.json` `columns_never_fillable`.
- Cost currency is tagged per-property in `purchase_price_currency` (defaults to presentation currency; foreign-cost assets carry their own — e.g. EUR/JPY/USD/GBP).
- **Not** available for most divested properties (they've left the portfolio) — use `carrying_value` for realized gains instead.
- **Excludes later capex/AEI and acquisition costs**, so a heavily-upgraded asset shows an inflated "gain" that's partly reinvestment, not appreciation. Footnote in prod.

### 4.9 Genuinely un-fillable cells (verified, not misses)
- `purchase_price` — 3 (HMN blended-lot acquisitions).
- `net_proceeds` — 2 (M44U Chee Wah + Subang 1, sold as one pair).
- `carrying_value` — 2 (CY6U 20.2% stake — only 100% disclosed; BUOU German NCI — equity transaction, no property carrying).
- `gain_on_divestment` — ~40 (per-property gain almost never disclosed; booked at portfolio/P&L level). **Derive it** as `net_proceeds − carrying_value` in prod rather than expecting it from source.

---

## 5. Audit-trail mechanisms (how we make it inspectable)

Everything questionable is **self-documenting** so a reviewer can trace it:

| Mechanism | Where | What it holds |
|---|---|---|
| `source_page` | every table | the AR page the value came from |
| `*_basis` text fields | transactions (`carrying_value_basis`, `gain_on_divestment_basis`, `net_proceeds_basis`) | plain-English provenance + method + verification date |
| `raw` (jsonb) | property_transaction | the full original object — nothing mapped away is lost |
| `original_currency` / `original_value` | property | local-currency figure when reported separately |
| `flags` (jsonb) | performance, property | per-record edge-case markers |
| `sgx_reit_notes` (jsonb) | 1/report | `columns_never_fillable`, `data_with_no_home`, `parsing_traps`, `inferred`, `reconciliation` |
| `status` / `transaction_type` | property, transaction | lifecycle & deal-type so filtering is explicit |

**Rule of thumb:** if a number needed a judgement call, its reasoning is in a `*_basis` field or in `sgx_reit_notes` — never silent.

---

## 6. The three colleague deliverables — recommended shape

| Deliverable | Source | Cost base | Notes |
|---|---|---|---|
| **D1 — yearly purchase/divest list** | `property_transaction` | — | group by **completion date**, split by type, filter status (completed/announced/terminated) |
| **D2 — capital/property gain %** | two metrics | | |
| &nbsp;&nbsp;• held (unrealised) | `property` | `purchase_price` | `(market_valuation − purchase_price)/purchase_price` — per-FY (valuation moves) |
| &nbsp;&nbsp;• divested (realised) | `property_transaction` | `carrying_value` | `(net_proceeds − carrying_value)/carrying_value`; prefer disclosed `gain` where present |
| **D3 — portfolio timeline** | `property` + `property_transaction` | — | acquisition/divestment events (dated) overlaid on per-FY `status` |

All three run on the **SGD-normalised prod views**, not raw Layer 1.

---

## 7. Open decisions for the call

1. **FX table** — which rates (source, period-end vs deal-date), and confirm the SGD-normalisation approach for Layer 2.
2. **Prior-year M44U deals** — keep flagged in FY2025, or re-home to actual year?
3. **`proceeds_basis` flag** — approve adding it (net vs gross) before prod.
4. **Bundled deals** — keep deal-level, or explode to per-property (carrying only) for the timeline?
5. **`gain_on_divestment`** — agree it's derived (`net_proceeds − carrying_value`), disclosed value preferred where present.
6. **Demo set** — confirm the 10 REITs to wire the frontend against (medium-sized, all 8 sub-sectors) so we test "useful vs nice-in-theory" on real screens.

---

## 8. Status summary

- ✅ 37 reports extracted, both QC gates green (schema PASS ×37).
- ✅ Loaded to Supabase + PDFs in R2.
- ✅ Property-transaction table scrubbed: transaction fields verified against source; carrying_value 66/68, net_proceeds 66/68, purchase_price 23/26 (acq).
- ⬜ Pending before prod: FX/SGD normalisation, `proceeds_basis` flag, resolve the 6 open decisions above, then build the 3 deliverable views.
