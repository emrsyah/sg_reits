# S-REIT Annual Report Extraction Analysis & Schema Proposal

> Based on LlamaParse (agentic tier) parses of 5 FY2025 annual reports, deliberately stratified
> across sector, sponsor, size and structure. Parsed sources in `parsed_reports/<stem>/full.md`
> (page-anchored markdown) and `pages.jsonl` (per-page markdown + item types).

| # | Trust | Sector | Pages | Tables | Notes |
|---|-------|--------|-------|--------|-------|
| 09 | CapitaLand Integrated Commercial Trust | Retail + Office (SG/DE/AU) | 199 | 271 | Large-cap, rated A3/A- |
| 21 | Keppel DC REIT | Data centres (global) | 200 | 203 | Full ESG report in-document |
| 28 | Mapletree Logistics Trust | Logistics (9 countries) | 235 | 227 | March FYE ("FY24/25"), perps |
| 17 | First REIT | Healthcare (ID/JP/SG) | 208 | 224 | Master leases, IDR exposure |
| 16 | Far East Hospitality Trust | Hospitality (SG/JP) | 251 | 183 | **Stapled** trust (REIT + BT) |

Not parsed (LlamaCloud credits exhausted): Stoneweg Europe (EUR) and KORE US (USD). Their
inclusion would mainly stress the multi-currency dimension, which MLT/First REIT already exercise.

---

## 1. What is reliably extractable — commonality matrix

**Present in 5/5 reports** (the dependable core for a universal schema):

| Data block | Typical location | Notes on variation |
|---|---|---|
| Financial highlights (GR, NPI, distributable income, DPU, NAV/unit, total assets, leverage) | front, pp 4–8 | 5-year history in 4/5; KDC gives 2 years only — **history depth is not guaranteed** |
| Full audited statements (SoFP, total return/P&L, distribution statement, movements in funds, cash flows) | back third | always 2 years, Group + Trust columns; stapled trusts have **3 entity columns** (Stapled / REIT / BT) |
| **Audited Portfolio Statement** — per-property carrying value, tenure, lease term/remaining, address, % of net assets | within FS | the single most consistent property-level table across all 5 |
| Marketing per-property profiles (valuation, GFA/NLA, occupancy, revenue, purchase price, major tenants) | portfolio section | field set varies by sector (rooms vs beds vs lettable area) |
| Capital management: aggregate leverage, ICR (+ MAS-mandated ICR sensitivity), avg cost of debt, % fixed/hedged, debt maturity profile by year, unencumbered assets, green/SLL share | dedicated section + borrowings note | ICR sensitivity (−10% EBITDA / +100bps) is in all 5 — a regulatory disclosure, hence universal |
| Debt instrument detail (currency, fixed/floating, rate, maturity, face/carrying value) | borrowings note | facility-level granularity everywhere |
| Distribution per period (DPU ¢, exact period dates, amount) | distribution statement | cadence differs:半 half-yearly (CICT, KDC, FEHT) vs quarterly (MLT, First) |
| Unitholder statistics: units in issue, market cap, size-band distribution, top 20 holders, substantial holders, directors' interests, **free float** | back, near-identical template | as-at date is post-FYE (Feb–May), differs per trust |
| Unit price: monthly close + volume, year high/low, benchmark comparison (STI, FTSE ST REIT) | investor relations | 12 monthly points everywhere |
| Fee structure formulas (base % of deposited property, performance % of NPI, acquisition/divestment %, trustee fee) | Note 1 of FS | rates differ widely: base 0.25–0.5%, perf 3.5–5.0% — formulas are text but highly regular |
| Segment reporting (business and/or geographic): revenue, NPI, assets per segment | notes to FS | segment dimension is sector-specific (asset type vs country vs lease type) |
| Lease expiry profile by year (% of NLA and/or % of rental income) | portfolio review | bucket labels differ (FY vs CY); some split by segment |
| Top ~10 tenants/customers with % of rental income | portfolio review | KDC anonymises names ("Fortune Global 500 Hyperscaler 42.1%") — **names not guaranteed** |
| Valuation inputs: valuers named, cap rate / discount rate **ranges** by country/segment, 2 years | fair-value note | per-property cap rates never disclosed, ranges only |
| Interested person transactions (counterparty, amount) | additional info | clean tables in all 5 |
| Remuneration: CEO exact or banded, per-director fees | CG report | exact CEO S$ in 4/5 |
| WALE | portfolio review | basis varies: by NLA vs by rental income — some give both. **Must store basis** |

**Present but inconsistent (4/5 or structurally divergent):**

- **ESG quantitative data** — full in-report tables (KDC: Scope 1/2/3, GJ, ML, 3–4 yrs; FEHT; First REIT) vs headline-only with separate sustainability report (CICT, MLT). A schema must tolerate absence.
- **5-year summary** — missing in KDC.
- **Rental reversion** — disclosed by CICT (+6.6%), MLT (per country, incl. China −11.4%), KDC (~45%); not meaningful for master-lease trusts (First REIT).
- **Credit rating** — only rated trusts disclose (CICT A3/A−, MLT BBB+); KDC/First/FEHT unrated → nullable.
- **Occupancy** — meaningless under master leases (First REIT reports flat 100%).

**Sector-specific (the long tail — needs a flexible store, not columns):**

| Sector | Metrics seen |
|---|---|
| Retail | tenant sales psf growth, shopper traffic growth, occupancy cost %, rent reversion, GTO rent share, suburban/downtown split |
| Office | avg monthly rent psf, retention rate, expiring rents per building |
| Data centre | lease typology (colocation / single-tenant / shell & core), dual WALE, PUE (relative only), market MW supply/take-up, client concentration (66% one client) |
| Logistics | per-country occupancy/WALE/reversion, SUA vs MTB split, freehold % of NLA, land WALE, multi-currency debt mix |
| Healthcare | beds/rooms capacity, master lease terms + expiry dates + renewal options, tenant arrears disclosure, restructured vs non-restructured leases, BOT land titles |
| Hospitality | occupancy / ADR / RevPAR (and RevPAU for serviced residences), corporate-vs-leisure mix, guest nationality mix, fixed vs GOP-variable master lease rent, market benchmarks |

**Parse-quality findings that drive schema design (consistent across all 5):**

1. Tables come out as HTML `<table>` blocks — mostly machine-parseable, but **audited primary statements are the weakest tables** (merged unit rows "$'000 $'000", note numbers fused into labels, dash placeholders shifting columns). The *notes* tables parse much cleaner than the face statements.
2. Charts are rendered as approximate value tables — usable but low-precision; orphan/duplicated chart-tables appear. **Provenance + confidence flags are necessary**, not optional.
3. Footnote markers stick to numbers ("406.4¹", "11.58²") → numeric cleaning layer required.
4. Repeated running-head H1s and KPI callouts parsed as headings → section detection must use page markers + known titles, not heading hierarchy.
5. Three-column magazine text occasionally becomes scrambled fake tables, sometimes duplicated → table-validity filter needed (reject tables whose cells are prose fragments).
6. Stapled trusts triple the entity dimension; March-FYE trusts label periods "FY24/25" → **period and entity-scope normalization is the hardest cross-trust problem**, not extraction itself.

---

## 2. Schema proposal — agentic financial intelligence suite

Design principles, derived directly from the findings above:

1. **Hybrid star + EAV.** Strongly-typed tables for the 5/5-universal blocks (they are stable and
   query-hot); a canonical-metric fact table for everything numeric (handles KDC's missing 5-year
   table, sector long-tail, ESG variance) so *no report fails to load because a column is absent*.
2. **Every fact carries provenance** (`report_id`, `page`, `extraction_method`, `confidence`).
   Agents must be able to cite ("DPU 11.58¢, CICT AR2025 p.26") and to discount chart-derived numbers.
3. **Normalize periods and scope explicitly.** `fiscal_period` resolves "FY2024/25" vs "FY2025";
   every fact has `entity_scope` (group / trust / stapled / reit / bt) because the same metric
   exists at multiple consolidation levels.
4. **Store as-reported + normalized.** Keep reported currency/unit verbatim AND an SGD-normalized
   value, since MLT reports JPY/RMB debt, First REIT IDR valuations, etc.
5. **A metric dictionary with aliases** ("DPU" = "Distribution per Unit" = "DPS" for stapled trusts)
   so an agent's natural-language query maps deterministically to canonical keys.
6. **A text/RAG layer beside the facts.** Lease narratives, arrears disclosures, strategy and
   covenant text matter to an agent and are not tabular. Page-chunked sections with embeddings,
   linked to the same `report_id`/`page` keys, let agents pivot from a number to its context.

### 2.1 Core reference tables

```sql
-- Listed entity master
trust (
  trust_id            PK,
  name, ticker, sgx_code,
  structure           ENUM('reit','stapled','business_trust'),
  sector              ENUM('retail','office','industrial','logistics','data_centre',
                           'hospitality','healthcare','diversified','specialised'),
  fye_month           INT,            -- 12 = Dec, 3 = Mar: drives period mapping
  reporting_currency  CHAR(3),
  sponsor, manager, trustee,
  listing_date, status
)

-- One row per source document
report (
  report_id PK, trust_id FK,
  report_type   ENUM('annual_report','sustainability_report','results','presentation'),
  fiscal_year   INT,                  -- normalized: calendar year fiscal period ENDS
  fiscal_label  TEXT,                 -- as printed: 'FY2024/25'
  period_start, period_end DATE,
  source_url, file_path, parse_job_id, parsed_at, page_count
)

-- Canonical period spine (annual, half, quarter) so DPU sub-periods join cleanly
fiscal_period (
  period_id PK, trust_id FK,
  period_type ENUM('FY','H1','H2','Q1'..'Q4','custom'),
  start_date, end_date,
  fiscal_year INT
)

-- Metric dictionary: the agent-facing vocabulary
metric (
  metric_key PK,                      -- 'gross_revenue', 'npi', 'dpu', 'aggregate_leverage',
                                      -- 'icr', 'nav_per_unit', 'avg_cost_of_debt', 'wale',
                                      -- 'occupancy', 'revpar', 'scope2_emissions', ...
  label, description,
  category   ENUM('income','balance','distribution','capital_mgmt','portfolio',
                  'trading','esg','sector_kpi','fees','market'),
  default_unit,                       -- 'SGD_thousands','cents','percent','years','x','sqm','tCO2e'
  higher_is_better BOOL NULL,
  aliases JSONB                       -- ['DPS','distribution per unit', ...]
)
```

### 2.2 The universal fact table (EAV core)

```sql
financial_fact (
  fact_id PK,
  trust_id FK, report_id FK, period_id FK,
  metric_key FK,
  entity_scope ENUM('group','trust','stapled','reit','bt') DEFAULT 'group',
  segment_key  TEXT NULL,             -- 'retail','singapore','colocation' → segment table
  value_numeric NUMERIC,
  value_text    TEXT,                 -- for ratings ('A3'), qualitative facts
  unit, currency CHAR(3),
  value_sgd     NUMERIC NULL,         -- normalized
  basis TEXT NULL,                    -- 'by_NLA' vs 'by_rental_income' (WALE!), 'committed' vs 'actual'
  -- provenance & trust
  page INT, section TEXT,
  extraction_method ENUM('table','text','chart_derived','computed'),
  confidence NUMERIC,                 -- chart_derived ⇒ low
  is_restated BOOL DEFAULT FALSE
)
```

This one table absorbs: 5-year highlights (one row per metric-year), capital-management KPIs,
ESG quantities, sector KPIs (RevPAR, tenant-sales growth, PUE), trading stats — and the agent
queries it uniformly: *"aggregate_leverage for all data-centre trusts, FY2025"* is one indexed query.

### 2.3 Strongly-typed satellites (the 5/5 blocks worth real columns)

```sql
-- Property master + per-report snapshot (audited Portfolio Statement = anchor source)
property (
  property_id PK, trust_id FK,
  name, address, city, country,
  property_type, land_tenure ENUM('freehold','leasehold','HGB','BOT'),
  lease_start, land_lease_expiry, acquisition_date, purchase_price, purchase_ccy,
  ownership_pct, status ENUM('active','divested','under_development')
)
property_snapshot (                   -- one row per property per report
  property_id FK, report_id FK,
  valuation, valuation_ccy, valuation_sgd, valuation_date, valuer,
  carrying_value_sgd_k, pct_of_net_assets,
  gfa_sqm, nla_sqm, occupancy_pct,
  gross_revenue, npi,                 -- CICT & MLT disclose per-property revenue/NPI
  capacity_value NUMERIC, capacity_unit TEXT,  -- rooms / beds / MW — sector-agnostic
  remaining_land_lease_years,
  page INT
)

-- Debt: instrument-level (from borrowings note) + maturity buckets (from cap-mgmt chart)
debt_instrument (
  report_id FK, trust_id FK,
  instrument_type ENUM('bank_loan','mtn','bond','tmk_bond','rcf','perp'),
  secured BOOL, currency, nominal_rate_pct, rate_type ENUM('fixed','floating'),
  maturity_year INT, face_value, carrying_value, green_or_sll BOOL, guarantee TEXT, page INT
)
debt_maturity (
  report_id FK, maturity_fy INT, amount_sgd_m, pct_of_total, instrument_breakdown JSONB, page INT
)

-- Distributions: the period spine makes quarterly vs half-yearly cadence uniform
distribution (
  trust_id FK, report_id FK, period_id FK,
  dpu_cents, amount_k, currency,
  components JSONB,                   -- {taxable, tax_exempt, capital, divestment_gains}
  declared_date, ex_date, payment_date,   -- payment dates only in financial calendar; nullable
  page INT
)

-- Lease expiry profile (universal; basis + segment dims handle all variants)
lease_expiry (
  report_id FK, expiry_fy INT, is_terminal_bucket BOOL,  -- '2031 and beyond'
  basis ENUM('nla','gross_rental_income','lettable_area'),
  segment_key TEXT NULL, pct NUMERIC, page INT
)

-- Tenant concentration
tenant_exposure (
  report_id FK, rank INT,
  tenant_name TEXT NULL,              -- NULL when anonymised (KDC)
  tenant_descriptor TEXT,             -- 'Fortune Global 500 (Hyperscaler)'
  pct_of_rental_income, trade_sector, is_related_party BOOL, page INT
)

-- Ownership & float
unitholding (
  report_id FK, as_at_date,
  holder_type ENUM('top20','substantial','director'),
  holder_name, units, pct, direct_or_deemed, rank, page INT
)
-- units_in_issue, market_cap, free_float_pct → financial_fact

-- Segments (business + geographic, one model)
segment_result (
  report_id FK, fiscal_year,
  dimension ENUM('business','geography','lease_type'),
  segment_key TEXT,                   -- 'retail' | 'singapore' | 'colocation'
  gross_revenue, npi, segment_assets, segment_liabilities, fair_value_change, capex, page INT
)

-- Fee structures (slow-changing; enables cross-trust fee comparison agents)
fee_structure (
  trust_id FK, report_id FK,
  fee_type ENUM('base','performance','acquisition','divestment','trustee',
                'property_mgmt','development','trustee_manager'),
  rate_pct, rate_base TEXT,           -- 'deposited_property','npi','transaction_price','EBIT'
  formula_text TEXT, cap_text TEXT, payable_in TEXT, page INT
)

-- Valuation assumptions (ranges by country/segment — never per property)
valuation_input (
  report_id FK, country, segment_key,
  input_type ENUM('cap_rate','discount_rate','terminal_yield','price_per_room','price_psf'),
  low_pct, high_pct, method, valuer, fiscal_year, page INT
)

-- Related-party transactions
ipt (
  report_id FK, counterparty, relationship, nature TEXT, amount_k, currency, page INT
)
```

### 2.4 Text / RAG layer (what makes it *agentic*)

```sql
document_section (
  report_id FK, section_title, page_start, page_end,
  section_type ENUM('chairman_letter','financial_review','capital_mgmt','operations_review',
                    'property_details','cg_report','risk','sustainability','fs_note','other')
)
document_chunk (
  chunk_id PK, report_id FK, section_id FK, page INT,
  text, embedding VECTOR,
  contains_tables BOOL, item_types JSONB    -- from pages.jsonl
)
```

Agent workflow this enables:
- **Structured first**: "Which S-REITs have ICR < 3x and >30% of debt maturing within 2 years?" →
  pure SQL over `financial_fact` + `debt_maturity`.
- **Pivot to narrative**: from any fact, `(report_id, page)` jumps into `document_chunk` for the
  surrounding discussion (e.g. First REIT's MPU arrears story behind its receivables number).
- **Comparable screening**: metric dictionary + `basis` field prevents apples-to-oranges
  (WALE-by-NLA vs WALE-by-income; adjusted vs reported DPU).
- **Citation-grade answers**: every number traces to trust → report → page.

### 2.5 Extraction strategy implied by parse quality

| Priority | Source table in AR | Why |
|---|---|---|
| 1 | Notes to FS (borrowings, segments, fair value, distributions) | cleanest parses, audited |
| 2 | Audited Portfolio Statement | most consistent property-level data across all trusts |
| 3 | Capital management & portfolio review sections | KPI-dense, mostly clean tables |
| 4 | Financial highlights (5-yr) | history depth, but verify against FS (chart-table risk) |
| 5 | Face statements (P&L/SoFP) | parse-fragile: prefer LlamaExtract with schema, validate totals |
| 6 | Chart-derived tables | load with `extraction_method='chart_derived'`, low confidence |

Recommended next step: use **LlamaExtract with Pydantic schemas per block** (it accepts a completed
parse job id as input, so the existing 5 parse jobs can be re-used without re-parsing credits),
starting with the Tier-1/2 sources above, and cross-validate: highlights vs FS, sum of segment
revenue vs total revenue, sum of property valuations vs investment-properties line.

---

## 3. Open questions before building

1. **Scope of corpus**: ARs only, or also half-year results + sustainability reports (needed to fill
   the ESG gap for CICT/MLT)?
2. **History**: backfill FY2023/FY2024 ARs (already downloaded) for 3-year trends per trust?
3. **Storage target**: Postgres (+pgvector) is the natural fit for the hybrid relational/EAV/RAG
   design above; confirm before DDL is finalized.
4. **LlamaCloud credits**: plan limit was hit after ~5 agentic parses (~1,100 pages, plus 2 duplicate
   jobs wasted by SDK timeouts). Parsing the full corpus (~100 PDFs, ~25k pages) on agentic tier
   needs a paid plan or a cheaper tier (cost_effective) for the text-heavy sections with agentic
   reserved for FS pages.
