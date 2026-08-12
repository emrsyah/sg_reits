# S-REIT Feature: Draft Review & Production Schema Proposal

> Inputs: (1) colleague's draft `REITS db.xlsx`, (2) verified extractability from 5 LlamaParse-d
> FY2025 annual reports (`schema_analysis.md`, `parsed_reports/_inventories.md`), (3) existing
> `sgx_*` prod schema. Target: sectors.app Singapore — queryable, LLM/agent-ready REIT data layer.

---

## 1. Review of the draft (`REITS db.xlsx`)

What she has (and what's right about it):

| Sheet | Content | Verdict |
|---|---|---|
| **REIT Profile** | 39 REITs: id, symbol, name, sub_sector (all filled); address, shares, management_company (empty) | ✅ Correct universe (matches our 39-trust download manifest). Right instinct to have a REIT master keyed to symbol. |
| **REIT Performance** | market_cap, portfolio_value, properties_location filled; financials, distributable income, distribution_record, unitholders as empty placeholders | ⚠️ Right *fields*, but flat — no time dimension. |
| **Property** | 26 CICT properties: country, category, name, address, reit_id, valuation, gross_revenue, occupancy, trade_mix (JSON), major_tenant, GLA/NLA, lease term, land tenure | ✅ The core insight is right: **property-level data is the differentiator** vs generic stock data. Columns map ~1:1 to what ARs actually disclose. |
| Portfolio Performance / top_10 / valuation_revenue | JSON-blob experiments (top-10 tenants, purchase history) on CICT data | ⚠️ Exploration scratch — the top-10-tenant JSON shape is good and survives below. |

Gaps to fix before this becomes a schema (none of these are criticisms — it's a draft on 1 of 39 REITs):

1. **No time dimension anywhere.** Every number (valuation, occupancy, market cap) is point-in-time
   with no fiscal year/date. ARs give us FY2023–FY2025 per trust; trend queries ("occupancy of
   Westgate over 3 years") are exactly what an agentic product needs. → every fact table below
   carries `fiscal_year` (+ `report_date`).
2. **One row per property loses history.** → split into `property` (identity) + `property_snapshot`
   (per fiscal year).
3. **Fields ARs don't reliably disclose**: per-property NPI is only disclosed by ~2 of 5 trusts
   (CICT, MLT); per-property `major_tenant`/`trade_mix` only for retail trusts. Keep them nullable —
   fill rate will be uneven by design, not by failure.
4. **Fields that don't need building**: market_cap, price, volume already live in `sgx_companies`
   / `sgx_daily_data`. Don't duplicate — join on symbol.
5. **Missing blocks that are verified-extractable from every AR** and are the actual intelligence
   value: capital management/debt (gearing, ICR, cost of debt, maturity ladder), distributions
   (DPU per period + dates), lease expiry profiles, fee structures, segments, valuation cap rates,
   unitholder stats. None appear in the draft yet.
6. **Integer `reit_id` as the key** — prod keys everything on `symbol` (text). Use symbol; it also
   makes the REIT layer a clean satellite of `sgx_companies`.

## 2. What sectors.app context implies

Sectors is API-first, LLM-ready financial data (natural-language query over IDX, now SGX/Malaysia).
So the schema must optimize for: (a) **deterministic NL→SQL mapping** (stable column names, one
obvious table per question type), (b) **cross-REIT screening** (typed columns for hot metrics, not
JSON), (c) **citations** (agents must say "AR2025 p.29"), (d) **graceful sparsity** (39 trusts ×
uneven disclosure). The prod style (typed columns for screeners + `jsonb` for nested/historical) is
actually a good fit — kept below.

## 3. Proposed schema (Postgres, `sgx_reit_*` namespace)

### 3.1 `sgx_reits` — REIT master (her *REIT Profile*, upgraded)

```sql
create table sgx_reits (
  symbol            text primary key references sgx_companies(symbol),
  name              text not null,
  structure         text check (structure in ('reit','stapled_trust','business_trust')),
  sub_sector        text,            -- retail|office|industrial|logistics|data_centre|hospitality|healthcare|diversified|lodging
  fye_month         smallint,        -- 12=Dec, 3=Mar: drives FY labeling (MLT 'FY24/25' -> 2025)
  reporting_currency text,
  manager           text,            -- management_company from her draft
  sponsor           text,
  trustee           text,
  credit_rating     text,            -- 'A3 (Moody's) / A- (S&P)'; null = unrated (3 of 5 sampled)
  mandate           text,            -- investment mandate, free text
  ipo_date          date,
  is_active         boolean default true
);
```

### 3.2 `sgx_reit_financials` — per fiscal year KPIs (her *REIT Performance*, time-dimensioned)

The screener workhorse: one row per (symbol, fiscal_year). Typed columns = the metrics present in
5/5 sampled ARs; `extras` jsonb absorbs the rest. REIT-level income/balance basics may already be
covered by `sgx_financials_annual`; this table holds the **REIT-specific** metrics that generic
financial statements don't have.

```sql
create table sgx_reit_financials (
  symbol               text references sgx_reits(symbol),
  fiscal_year          smallint,      -- normalized: CY in which FY ends
  fiscal_label         text,          -- as printed: 'FY2024/25'
  period_end           date,
  -- income & distribution
  gross_revenue        numeric,       -- S$'000
  net_property_income  numeric,
  distributable_income numeric,
  dpu_cents            numeric,
  adjusted_dpu_cents   numeric,       -- ex divestment gains etc., when disclosed
  -- balance & portfolio
  total_assets         numeric,
  investment_properties numeric,
  portfolio_value      numeric,       -- AUM as reported (her portfolio_value)
  nav_per_unit         numeric,
  units_in_issue       bigint,
  -- capital management (all 5/5 disclosed, incl. MAS-mandated)
  aggregate_leverage_pct  numeric,
  interest_coverage_x     numeric,
  avg_cost_of_debt_pct    numeric,
  pct_fixed_rate_debt     numeric,
  avg_debt_maturity_years numeric,
  total_borrowings        numeric,
  unencumbered_assets_pct numeric,
  green_financing_pct     numeric,
  -- portfolio aggregates
  property_count       smallint,
  occupancy_pct        numeric,       -- portfolio committed occupancy; null for master-lease trusts
  wale_years           numeric,
  wale_basis           text,          -- 'nla' | 'gross_rental_income' — basis differs by trust!
  free_float_pct       numeric,
  extras               jsonb,         -- MER, perpetuals, tenant retention, sector KPIs (RevPAR, tenant sales growth...)
  source_report        text,          -- file/url
  source_pages         jsonb,         -- {'dpu': 26, 'leverage': 27} citation map
  updated_on           timestamptz default now(),
  primary key (symbol, fiscal_year)
);
```

### 3.3 `sgx_reit_properties` + `sgx_reit_property_snapshots` — her *Property* sheet, split

```sql
create table sgx_reit_properties (
  property_id     serial primary key,
  symbol          text references sgx_reits(symbol),
  property_name   text not null,
  country         text, city text, address text,
  category        text,              -- retail|office|industrial|logistics|data_centre|hotel|hospital|...
  ownership_pct   numeric default 100,
  land_tenure     text,              -- freehold | leasehold | HGB | BOT
  land_lease_expiry date,            -- her 'term_of_lease' "85/99" normalized to expiry + original term
  land_lease_original_years numeric,
  acquisition_date date,             -- her 'effective date'
  purchase_price  numeric, purchase_currency text,
  status          text default 'active',  -- active | divested | under_development
  unique (symbol, property_name)
);

create table sgx_reit_property_snapshots (
  property_id     int references sgx_reit_properties(property_id),
  fiscal_year     smallint,
  valuation       numeric,           -- local currency
  valuation_currency text,
  valuation_sgd   numeric,
  gross_revenue   numeric,           -- 5/5 disclose per-property revenue or attributable revenue
  net_property_income numeric,       -- only ~2/5 disclose; nullable by design
  occupancy_pct   numeric,           -- null under master leases (First REIT = structurally 100)
  gfa_sqm numeric, nla_sqm numeric,
  capacity_value  numeric, capacity_unit text,  -- rooms | beds | MW — covers hospitality/healthcare/DC
  major_tenants   jsonb,             -- ['Golden Village', 'NTUC'] when disclosed
  trade_mix       jsonb,             -- {'F&B': 33.9, ...} retail trusts only
  valuer          text,
  source_page     int,
  primary key (property_id, fiscal_year)
);
```

### 3.4 Distributions — verified 5/5, cadence varies (quarterly vs half-yearly)

```sql
create table sgx_reit_distributions (
  symbol        text references sgx_reits(symbol),
  period_start  date, period_end date,
  fiscal_year   smallint,
  dpu_cents     numeric,
  amount        numeric,             -- S$'000
  components    jsonb,               -- {taxable, tax_exempt, capital, divestment_gains}
  declared_date date, ex_date date, payment_date date,  -- payment dates not always tabulated
  source_page   int,
  primary key (symbol, period_end)
);
```
(Complements `sgx_companies.historical_dividends`; this is the authoritative, period-exact version.)

### 3.5 Debt detail — the queries serious users ask ("who refinances in 2026?")

```sql
create table sgx_reit_debt_maturity (
  symbol text, fiscal_year smallint,
  maturity_fy smallint, is_terminal_bucket boolean default false,
  amount numeric, pct_of_total numeric,
  breakdown jsonb,                   -- {'mtn': x, 'bank_loan': y} when split
  source_page int,
  primary key (symbol, fiscal_year, maturity_fy)
);

create table sgx_reit_debt_instruments (   -- from borrowings notes; facility-level
  id serial primary key,
  symbol text, fiscal_year smallint,
  instrument_type text,              -- bank_loan|mtn|bond|tmk_bond|rcf|perpetual
  currency text, nominal_rate_pct numeric, rate_type text,  -- fixed|floating
  maturity_year smallint, face_value numeric, carrying_value numeric,
  secured boolean, green_or_sll boolean,
  source_page int
);
```

### 3.6 Leasing & tenants — her `top_10` JSON, normalized

```sql
create table sgx_reit_lease_expiry (
  symbol text, fiscal_year smallint,
  expiry_fy smallint, is_terminal_bucket boolean,
  basis text,                        -- 'nla' | 'gross_rental_income'
  segment text,                      -- null = portfolio; 'retail'/'office'/'colocation'/country
  pct numeric,
  source_page int,
  primary key (symbol, fiscal_year, expiry_fy, basis, segment)
);

create table sgx_reit_top_tenants (
  symbol text, fiscal_year smallint, rank smallint,
  tenant_name text,                  -- null when anonymised (Keppel DC: 'Hyperscaler')
  tenant_descriptor text,
  trade_sector text,
  pct_of_rental_income numeric,
  source_page int,
  primary key (symbol, fiscal_year, rank)
);
```

### 3.7 Smaller satellites (all verified 5/5-extractable)

```sql
-- segment results: business + geographic, one model
sgx_reit_segments (symbol, fiscal_year, dimension /*business|geography|lease_type*/,
                   segment, gross_revenue, npi, segment_assets, source_page)

-- fee structures: enables "which managers charge perf fee on NPI vs DPU growth?"
sgx_reit_fees (symbol, fiscal_year, fee_type /*base|performance|acquisition|divestment|trustee|property_mgmt*/,
               rate_pct, rate_base /*deposited_property|npi|transaction_price*/, formula_text, source_page)

-- valuation assumptions: cap/discount rate ranges by country+segment (never per-property)
sgx_reit_valuation_inputs (symbol, fiscal_year, country, segment,
                           input_type /*cap_rate|discount_rate|terminal_yield*/,
                           low_pct, high_pct, valuer, method, source_page)

-- ownership: top-20 + substantial holders + free float (mirrors sgx_companies.shareholders style,
-- but normalized; as_at_date is post-FYE and differs per trust)
sgx_reit_unitholders (symbol, as_at_date, holder_type /*top20|substantial|director*/,
                      holder_name, units bigint, pct, direct_or_deemed, rank, source_page)
```

### 3.8 Optional but recommended: catch-all fact table + text layer

For the long tail (ESG quantities, sector KPIs like RevPAR/PUE/tenant-sales, anything new a report
discloses) without schema migrations — and the RAG layer that makes it *agentic*:

```sql
sgx_reit_facts (symbol, fiscal_year, metric_key /*canonical, with alias dict*/,
                segment, value_numeric, value_text, unit, currency, basis,
                extraction_method /*table|text|chart_derived*/, confidence, source_page)

sgx_reit_doc_chunks (symbol, fiscal_year, report_type, page, section_type, text, embedding vector)
```

Every numeric answer can then cite `(symbol, FY, page)` and pivot into the surrounding narrative
(e.g. First REIT's tenant-arrears story behind a receivables number) — the thing
`sgx_companies`-style aggregate tables can't do.

## 4. How it connects to prod (and where it deliberately doesn't)

- `sgx_reits.symbol → sgx_companies.symbol`: profile, live market cap, PE/PB, beta, price history
  (`sgx_daily_data`) come free. **Do not re-store price/volume/market_cap in REIT tables** (the
  draft's `market_cap` column drops out).
- `sgx_financials_annual` keeps generic income/balance/cashflow jsonb; `sgx_reit_financials` holds
  REIT-native metrics (DPU, gearing, ICR, WALE, NPI) that don't exist for ordinary companies.
  Same `(symbol, financial_year)` key shape → trivially joinable.
- Computed metrics (distribution yield, P/NAV) should be **derived at API level** from
  `dpu_cents` / `nav_per_unit` × `sgx_daily_data.close` — never stored stale.

## 5. Reality check: expected fill rates (from the 5-report sample)

| Block | Coverage | Caveat |
|---|---|---|
| sgx_reit_financials core | ~100% | KDC-style reports lack 5-yr history → backfill from older ARs (already downloaded) |
| property + snapshots | ~100% of properties | per-property NPI ~40%, trade_mix/major_tenants mostly retail |
| distributions | 100% | payment dates sometimes only in financial calendar |
| debt maturity + instruments | 100% | bucket labels FY vs CY differ; normalize |
| lease expiry, top tenants | 100% | tenant names anonymised by some (DC), basis varies |
| fees, segments, valuation inputs, unitholders | 100% | — |
| ESG quantities | ~60% in AR | rest in separate sustainability reports → fact table, not columns |
| occupancy/reversion | sector-dependent | structurally null for master-lease trusts — document this in API |

## 6. Suggested next steps

1. Align with colleague: keep her Property/Profile shape, adopt symbol keys + fiscal_year, drop
   market-data duplicates.
2. Build extraction with **LlamaExtract using the existing 5 parse-job IDs** (no re-parse credits)
   with Pydantic schemas mapping 1:1 to the tables above; validate (segments sum to totals,
   property valuations sum to investment-properties line).
3. Top up LlamaCloud credits, parse remaining corpus (FY2023–25 backfill = 3-year trends at launch).
4. Pilot the API/NL-query layer on the 5 done trusts before scaling to 39.
```
