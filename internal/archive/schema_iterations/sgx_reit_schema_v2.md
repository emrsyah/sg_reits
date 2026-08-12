# `sgx_reit_*` Production Schema v2 — synthesized proposal

> Synthesis of five inputs:
> 1. **Evidence**: 14 parsed annual reports (LlamaParse agentic), audited for disclosure patterns —
>    CICT, KDC, MLT, First REIT, FEHT, CLAR, FCT, KORE US, Stoneweg Europe, Sasseur, CLCT,
>    Keppel REIT, Elite UK, CLAS Ascott, Centurion. 9 sectors, 6 currencies, 6 income models.
> 2. **Colleague's draft** (`REITS db.xlsx`): REIT Profile / Property / Performance shapes.
> 3. **Colleague's feedback**: terminology precision (tenure, purchase vs effective date,
>    manager roles); tenant mix at property level + aggregate; standardize computed metrics
>    (GRI vs NPI) on our side.
> 4. **Current proposal v1** (`reit_schema_proposal.md`) + reflection (`feedback_reflection.md`).
> 5. **Prod conventions** (`sgx_companies`, `sgx_daily_data`, `sgx_financials_annual`):
>    text `symbol` PKs, typed screener columns + jsonb for nested, derived metrics at API level.

---

## 0. What the 14-report evidence settled

| Question | Answer | Consequence |
|---|---|---|
| Per-property gross revenue / GRI | **11 of 14** disclose it (missing: First REIT, KDC, CLAS) | typed column, expected fill ~79% |
| Per-property NPI | **4 of 14** (FCT, KORE, CLCT, Keppel REIT — the latter on *attributable* basis) | nullable column + `npi_basis` qualifier, never imputed |
| Per-property valuation, tenure, occupancy | ~100% (audited Portfolio Statement is near-universal; CLAS is the one outlier with cost-only listing) | typed columns |
| Acquisition date & purchase price | Most trusts; often **phased** (Rock Square 51%+49%, NEX 25.5%+24.5%, Westpark 3+1 buildings) | events table, not single columns |
| Per-property trade mix | **2 of 14** (CICT, Sasseur) | dual-scope tenant-mix table; aggregation = validation only |
| One NPI definition | **No.** 6 income models: conventional lease, master lease, MCMGI, management contract ("gross profit"), EMA (no NPI exists), FRI (90%+ margin) | `income_model` enum; expense components stored raw; standardized metrics computed in API layer |
| One basis for tenant/lease metrics | **No.** 8+ denominators: GRI, GRI-excl-GTO, gross revenue, rental income, headline rent, cash rental income, committed gross rent, NLA/lettable area | mandatory `basis` column on every percentage |
| One ownership basis | **No.** Keppel REIT reports attributable (incl. JV/associate share: S$215.9M consolidated NPI vs S$381.4M attributable); MAS leverage is proportionate | `ownership_basis` qualifier on financial facts |
| One currency | **No.** SGD, USD, EUR, GBP, RMB (dual-column with disclosed FX 5.499), mixed-currency tables (Centurion: SGD/GBP/AUD rows in one statement) | store local value + currency + SGD value + fx rate |
| One fiscal calendar | **No.** Dec / Mar / Sep FYE + stub periods (Centurion: constituted 12 Aug, income from 25 Sep) + figures that are annualised / pro-forma / forecast (Elite "annualised GRI" vs "actual rental received"; post-regear WALE; Centurion IPO forecast vs actual) | `period_start/end` + `figure_type` |

---

## 1. Design rules (carried from v1, hardened by v2 evidence)

1. **Key on `symbol` text** referencing `sgx_companies` (prod convention; replaces draft's integer `reit_id`).
2. **Never store what prod already has**: price/volume/market cap → `sgx_daily_data`/`sgx_companies`.
3. **Computed metrics live in the API layer**, never as columns: distribution yield, P/NAV,
   NPI margin, standardized NPI, cost ratios. This is the colleague's "standardise the formula
   on our end" point and matches how prod computes yield/P-NAV today. The DB stores the **raw
   audited inputs** (revenue/expense components) those formulas need.
4. **Every percentage carries its `basis`; every fact carries provenance** (`source_page`,
   `extraction_method`, `confidence` where chart-derived).
5. **As-disclosed, not as-wished**: nullable means "this trust doesn't disclose it" (structural),
   and the API documents that (e.g. occupancy is structurally null for master-lease trusts,
   NPI doesn't exist for Sasseur's EMA model).
6. Typed columns for the universal screener core; `jsonb extras` + the facts table for the long
   tail (RevPAU, ADR, PUE, shopper traffic, VIP members, outlet sales, beds pipeline…).

---

## 2. Core reference tables

### 2.1 `sgx_reits` — trust master

```sql
create table sgx_reits (
  symbol             text primary key references sgx_companies(symbol),
  name               text not null,
  structure          text check (structure in ('reit','stapled_trust','business_trust')),
  sub_sector         text,        -- retail|office|industrial|logistics|data_centre|hospitality|
                                  -- healthcare|diversified|lodging|accommodation
  income_model       text check (income_model in
                       ('conventional','master_lease','mcmgi','management_contract',
                        'entrusted_management','fri','mixed')),
                                  -- CLAS = 'mixed' (3 contract types); Sasseur = 'entrusted_management'
  fye_month          smallint,    -- 12, 3 (MLT/CLAR), 9 (FCT)
  reporting_currency text,        -- SGD|USD|EUR|GBP
  listing_date       date,        -- Centurion 2025-09-25; drives stub-period handling
  mandate            text,
  is_active          boolean default true,

  -- ownership (see 2.2): public float is the reliable scalar; substantial holders best-effort
  public_float_pct   numeric,     -- SGX Rule 723-mandated, present in ~all reports → dependable
  sponsor_stake_pct  numeric,     -- sponsor skin-in-the-game; from substantial table where present

  -- who runs / who owns / who governs — jsonb columns, mirroring prod sgx_companies pattern (2.2)
  service_entities   jsonb,       -- manager/sponsor/trustee/lessee/operator  (BUILD — core)
  unitholders        jsonb,       -- substantial (>=5%) holders, best-effort  (BUILD if clean table)
  management         jsonb        -- directors & execs, prod shape            (DEFER for v1)
);
```

### 2.2 Management / ownership — jsonb columns on the master, NOT separate tables

Decision (revised from v1's `sgx_reit_entities`/`sgx_reit_unitholders` tables): these are
**jsonb columns on `sgx_reits`**, one row per REIT, mirroring how prod `sgx_companies` stores
`management`/`shareholders`. Rationale: low cardinality (~5-8 entities/REIT), slow-changing,
mostly display — a separate normalized table only pays off if we build cross-REIT screening on
managers/lessees, which isn't committed for v1. Verified populatable from a single "Trust
Structure" page per report (CICT p9, MLT p22, Sasseur p8, FEHT p6).

**`service_entities`** — array; `role` is a fixed enum (the AR's regulated *defined terms* —
"the Manager", "the Trustee", etc. — normalized to a consistent label; enforced at the
extraction/app layer since jsonb isn't DB-constrained):
```
role      enum   reit_manager|property_manager|operator|master_lessee|entrusted_manager|sponsor|trustee
name      string required
fee_basis string nullable  -- e.g. "0.25% of deposited property + 4.25% of NPI" (CICT p114);
                           -- "2.0% of gross revenue" (MLT p175); "30% of GR" (Sasseur p50).
                           -- Promote to a structured sgx_reit_fees table only if a fee-comparison
                           -- screen is built. NOTE: `is_related_party` was dropped — it is
                           -- ~always true for manager/sponsor (derivable from role) and only
                           -- varies for master_lessee/operator; the useful version is
                           -- related-party *income* exposure, a concentration metric, not a bool.
```

**Ownership — two reliability tiers (verified across 8 reports):**
- `public_float_pct` (scalar, §2.1) is the **dependable** field — SGX Rule 723 mandates it, so it
  appears in every report with a clean number (CICT ~71% p195, MLT 66.42% p230, FEHT 45.07% p236,
  KORE 77.52% p153, DCR 58.7% p218, CLAS ~69.8% p295, Sasseur 42.07% p217, MUST states the rule).
  Lead the ownership story with this.
- `unitholders` (jsonb, best-effort/nullable) — substantial (>=5%) **beneficial** holders, *not*
  the Top-20 (which is custodian nominees: Citibank Nominees 23%, etc.). Present as a clean table
  in ~3 of 5 (CICT p195, MLT p230, KORE p153), as deemed-interest footnotes in others (FEHT
  p237-238), occasionally absent (DCR gives only the float). Extraction rule: **deemed-interest
  rows up an ownership chain are one stake — capture but never sum** (CICT Temasek→Tembusu→Bartley
  all ~21% = a single Temasek holding).
  ```
  name string ; pct numeric (fraction) ; type enum: substantial|sponsor
  ```

**`management`** (deferred) — if built, copy prod `sgx_companies.management` verbatim:
`name, age, position, start_date`. For a REIT the *manager entity* (in service_entities) matters
more than individual directors, so this is the first thing to cut from v1 scope.

---

## 3. Property layer (colleague's Property sheet, upgraded)

### 3.1 `sgx_reit_properties` — identity

```sql
create table sgx_reit_properties (
  property_id     serial primary key,
  symbol          text references sgx_reits(symbol),
  property_name   text not null,
  country         text, city text, address text,
  category        text,           -- retail|office|business_park|logistics|data_centre|hotel|
                                  -- serviced_residence|hospital|outlet_mall|pbwa|pbsa|...
  ownership_pct   numeric default 100,   -- Keppel REIT: 33.3% ORQ; held_via below
  held_via        text check (held_via in ('consolidated','joint_venture','associate'))
                  default 'consolidated', -- JV/associate properties have no carrying value in
                                          -- the group portfolio statement (Keppel REIT MBFC/ORQ)
  income_model    text,           -- property-level override: CLAS mixes 3 models in one trust;
                                  -- Centurion EPIISOD is master-leased while siblings are direct
  -- land tenure (feedback item 1; labels normalized via alias dictionary)
  land_tenure_type   text check (land_tenure_type in ('freehold','leasehold','mixed')),
  tenure_raw         text,        -- 'Part freehold, Part Right of Superficies' (Stoneweg) /
                                  -- '30+30 years' (MLT) — keep verbatim
  land_lease_term_years     numeric,
  land_lease_expiry_date    date, -- CLAR & CLCT give exact dates ('7 Jun 2071', '23 Aug 2044')
  land_lease_remaining_years numeric,  -- snapshot at last report; recompute in API from expiry
  -- capacity
  nla_sqm numeric, gfa_sqm numeric, land_area_sqm numeric,
  capacity_value numeric, capacity_unit text,  -- 18,825 units (CLAS) | 22,382 beds (Centurion)
                                               -- | rooms (FEHT) | MW (KDC)
  status          text default 'active',  -- active|divested|under_development
  unique (symbol, property_name)
);
```

### 3.2 `sgx_reit_property_events` — acquisitions are phased; single columns lose history

```sql
create table sgx_reit_property_events (
  id            serial primary key,
  property_id   int references sgx_reit_properties(property_id),
  event_type    text check (event_type in ('acquisition','stake_increase','divestment',
                   'aei_completion','development_top','lease_regear','master_lease_start')),
  event_date    date,             -- 'Date of legal completion' (MLT) / 'Acquisition date'
                                  -- (CLAR, First REIT, Stoneweg, KORE) — alias-mapped
  stake_pct     numeric,          -- Rock Square: 51% (2018-01-31) then 49% (2020-12-30)
  price         numeric, price_currency text,   -- 'Purchase Price in 2005' (CICT) etc.
  is_post_period boolean default false,         -- EPIISOD 13 Jan 2026, MBFC T3 31 Dec —
                                                -- subsequent-events sections are gold, flag them
  detail        text, source_page int
);
```

### 3.3 `sgx_reit_property_snapshots` — per (property, fiscal_year)

```sql
create table sgx_reit_property_snapshots (
  property_id     int references sgx_reit_properties(property_id),
  fiscal_year     smallint,
  -- valuation: always local + SGD (CLCT dual-columns RMB/SGD with avg rate 5.499 disclosed;
  -- Centurion mixes SGD/GBP/AUD rows in one audited statement)
  valuation       numeric, valuation_currency text, valuation_sgd numeric,
  valuation_per_sqm numeric,      -- CLCT discloses RMB/sqm — useful comparable
  valuation_date  date,           -- 'Latest valuation date' ≠ acquisition date (feedback item 1)
  cap_rate_pct    numeric,        -- Keppel REIT gives per-building cap rates
  -- income (the GRI vs NPI boundary, feedback item 3)
  gross_revenue   numeric,        -- 11/14 disclose; CICT footnote: = GRI + car park + other.
  gross_revenue_currency text,
  gri             numeric,        -- only when separately disclosed (Elite 'Annualised GRI',
                                  -- Centurion 'Gross Rental Income for FP 2025')
  rent_received   numeric,        -- Elite separates 'Actual Rental Received' from annualised
  npi_disclosed   numeric,        -- 4/14 only. NEVER computed/imputed at property level —
                                  -- no trust discloses per-property expenses.
  npi_basis       text check (npi_basis in ('consolidated','attributable')),
                                  -- Keppel REIT per-building NPI is attributable
  ema_rental_income numeric,      -- Sasseur per-outlet (no NPI exists in that model)
  outlet_sales    numeric,        -- Sasseur: tenant sales pool the variable rent draws from
  -- operations
  occupancy_pct   numeric,
  occupancy_type  text check (occupancy_type in ('committed','actual','average')),
                                  -- CICT/FCT/KORE 'committed'; MLT actual; Centurion 'average'
  tenant_count    smallint,       -- CICT, Keppel REIT, Sasseur disclose per property
  shopper_traffic bigint,         -- FCT & Sasseur per-mall
  major_tenants   jsonb,          -- names only, when disclosed
  extras          jsonb,          -- VIP members (Sasseur), per-DC WALE (KDC), RevPAR...
  source_page     int,
  primary key (property_id, fiscal_year)
);
```

---

## 4. REIT-level financials

### 4.1 `sgx_reit_financials` — screener workhorse, one row per (symbol, fiscal_year)

v1 columns kept; v2 adds period precision, ownership basis, and income-model variants:

```sql
create table sgx_reit_financials (
  symbol               text references sgx_reits(symbol),
  fiscal_year          smallint,    -- CY in which FY ends
  fiscal_label         text,        -- 'FY2024/25', 'FP 2025' (Centurion stub)
  period_start         date, period_end date,
  period_type          text check (period_type in ('full_year','stub')) default 'full_year',
                                    -- Centurion FP2025 = 98 income days; do NOT annualise in DB
  -- income & distribution (as reported)
  gross_revenue        numeric,     -- for Sasseur this is EMA rental income (income_model says so)
  net_property_income  numeric,     -- CLAS reports 'gross profit' — store here, model flag
                                    -- disambiguates; null is impossible at REIT level except EMA
  npi_attributable     numeric,     -- Keppel REIT S$381.4m vs consolidated S$215.9m
  share_of_jv_results  numeric,     -- the bridge line
  distributable_income numeric,
  dpu                  numeric,
  dpu_unit             text default 'sgd_cents',  -- Elite UK pays in GBP pence
  -- balance & portfolio
  total_assets numeric, investment_properties numeric, portfolio_value numeric,
  nav_per_unit numeric, units_in_issue bigint,
  -- capital management (MAS-mandated, 14/14 disclosed)
  aggregate_leverage_pct  numeric,
  leverage_basis          text,     -- 'consolidated' | 'proportionate' (Keppel REIT 40.4% incl.
                                    -- share of JV debt) — comparing across trusts needs this
  interest_coverage_x numeric, avg_cost_of_debt_pct numeric,
  pct_fixed_rate_debt numeric, avg_debt_maturity_years numeric,
  total_borrowings numeric, unencumbered_assets_pct numeric,
  -- portfolio aggregates
  property_count smallint, occupancy_pct numeric,
  extras       jsonb,               -- RevPAU+ADR (CLAS), tenant retention (Centurion 79.2%),
                                    -- same-store deltas, portfolio outlet sales (Sasseur)...
  figure_type  text default 'actual' check (figure_type in
                 ('actual','forecast','pro_forma','annualised')),
                                    -- Centurion stores IPO-forecast row beside actual (beat DPU
                                    -- by 6.7%); Elite post-regear metrics are pro_forma
  source_report text, source_pages jsonb,
  updated_on    timestamptz default now(),
  primary key (symbol, fiscal_year, figure_type)
);
```

### 4.2 Revenue & expense components — the raw inputs for **our standardized formulas**

This is the direct implementation of the colleague's standardization point. Every trust's
audited notes break revenue and property expenses differently; we store the lines, canonical-
mapped, and compute standardized NPI / margins / cost ratios in the API layer.

```sql
create table sgx_reit_revenue_components (
  symbol text, fiscal_year smallint,
  component text check (component in ('base_rental','turnover_rent','service_charge',
    'recoveries','car_park','hospitality','hotel_revenue','ema_fixed','ema_variable',
    'dilapidations','other')),
    -- evidence: FCT splits GTO rent ($15.8m); KORE 'recoveries' ($42m = 28% of revenue);
    -- Stoneweg service charges (€44m); Sasseur fixed RMB447.5m + variable RMB211.0m;
    -- Elite dilapidation settlements (£1.6m, one-off — excluded from standardized run-rate)
  amount numeric, currency text,
  component_label_raw text,        -- exact note label, for audit
  source_page int,
  primary key (symbol, fiscal_year, component)
);

create table sgx_reit_expense_components (
  symbol text, fiscal_year smallint,
  component text check (component in ('property_tax','business_tax_vat','utilities',
    'maintenance','property_mgmt_fee','mgmt_reimbursement','marketing','staff',
    'insurance_security','loss_allowance','land_rent','depreciation_ffe',
    'leasing_commission_amort','other')),
    -- evidence of divergence (why standardization must be ours):
    -- utilities = 35% of CLAR's expenses; loss allowance = 36% of KDC's; staff S$133.7m inside
    -- CLAS 'direct expenses'; China adds business tax/VAT (CLCT); KORE buries straight-line
    -- and leasing-commission amortisation in 'other' (reported NPI +3.0%, adjusted +0.3%)
  amount numeric, currency text,
  component_label_raw text,
  source_page int,
  primary key (symbol, fiscal_year, component)
);
```

Non-cash adjusters get first-class treatment (they distort every cross-REIT comparison):

```sql
create table sgx_reit_accounting_adjustments (
  symbol text, fiscal_year smallint,
  adjustment text check (adjustment in ('straight_line_rent','lease_incentive_amort',
    'ema_straight_line','rental_support')),
  amount numeric, currency text, source_page int,
  primary key (symbol, fiscal_year, adjustment)
);
```

---

## 5. Tenants & leases (feedback item 2: dual scope, mandatory basis)

```sql
create table sgx_reit_tenant_mix (
  id serial primary key,
  symbol text, fiscal_year smallint,
  scope text check (scope in ('property','segment','portfolio')),
  property_id int,                 -- CICT (26 properties) & Sasseur (4 outlets) fill this;
                                   -- everyone else portfolio/segment only
  segment text,                    -- CLAR gives mix per segment-geography
  category text,                   -- trade sector label as disclosed
  pct numeric,
  basis text not null check (basis in ('gri','gri_excl_gto','gross_revenue','rental_income',
    'headline_rent','cash_rental_income','committed_gross_rent','nla','outlet_sales')),
    -- Sasseur per-outlet mix is % of SALES, not rent — basis prevents silent apples/oranges
  is_derived boolean default false, -- our roll-up stored beside disclosed figures, never mixed
  source_page int
);

create table sgx_reit_top_tenants (
  symbol text, fiscal_year smallint, rank smallint,
  tenant_name text,                -- null when anonymised (KDC hyperscalers, Sasseur unnamed)
  trade_sector text, properties text[],
  pct numeric, basis text not null,
  pct_nla numeric,                 -- FCT & Keppel REIT disclose both % rent and % NLA
  scope text default 'portfolio',  -- CLAS top-10 corporate clients cover mgmt-contract
                                   -- properties only — scope must say so
  source_page int,
  primary key (symbol, fiscal_year, rank)
);

create table sgx_reit_lease_metrics (
  symbol text, fiscal_year smallint,
  metric text check (metric in ('wale','walb')),   -- Stoneweg WALB 4.0y vs WALE 4.9y
  scope text,                      -- portfolio | segment:<x> | country:<x> | top10_tenants
  basis text not null,             -- nla|gri|cri|lettable_area|rental_income|committed_gross_rent
  years numeric,
  figure_type text default 'actual',  -- Elite: 2.4y actual vs 7.2y pro_forma post-regear
  source_page int,
  primary key (symbol, fiscal_year, metric, scope, basis, figure_type)
);

-- lease expiry ladder: unchanged from v1 (+ basis already there)
create table sgx_reit_lease_expiry (
  symbol text, fiscal_year smallint,
  expiry_fy smallint, is_terminal_bucket boolean,
  basis text, segment text, pct numeric, source_page int,
  primary key (symbol, fiscal_year, expiry_fy, basis, segment)
);

-- lease structure facts the agentic layer needs for "how protected is this income?"
create table sgx_reit_lease_structures (
  id serial primary key,
  symbol text, fiscal_year smallint,
  property_id int,                 -- null = portfolio-level statement
  feature text check (feature in ('turnover_rent_provision','fixed_escalation',
    'cpi_indexation','minimum_rent_guarantee','variable_pct_of_sales','fri','renewal_option')),
  value_pct numeric,               -- Sasseur variable: 4.0/4.5/5.5/5.0% of sales per outlet;
                                   -- fixed escalation 3%/yr; CLCT 90.9% of leases have GTO terms
  coverage_pct numeric, coverage_basis text,
  detail text, source_page int
);
```

## 6. Distributions, debt, segments, fees, concentrations (v1 kept, deltas only)

```sql
-- sgx_reit_distributions: unchanged from v1 + dpu_unit (pence) + figure_type
-- sgx_reit_debt_maturity, sgx_reit_debt_instruments: unchanged from v1
--   (+ leverage_basis lives in financials)

create table sgx_reit_segments (
  symbol text, fiscal_year smallint,
  dimension text check (dimension in ('business','geography','contract_type','lease_type')),
    -- contract_type is new: CLAS reports master_lease/mcmgi/management_contract revenue
    -- (S$113.1m/230.2m/494.3m) and gross profit splits — its only granular P&L
  segment text,
  gross_revenue numeric, npi numeric, segment_assets numeric,
  currency text, source_page int,
  primary key (symbol, fiscal_year, dimension, segment)
);

-- sgx_reit_fees: v1 shape confirmed by stranger-than-expected reality; formula_text is
-- mandatory (Centurion PBWA: 2% gross revenue + 5% NPI; PBSA: flat 4%; Sasseur EM: 30% of GR
-- base + 60% performance split; CLCT Hangzhou: 8.4% of GRI in lieu of commissions)

create table sgx_reit_concentrations (
  id serial primary key,
  symbol text, fiscal_year smallint,
  kind text check (kind in ('tenant','client','geography','sector','lease_expiry_year')),
  description text,                -- 'DWP (UK Government)' / 'one colocation client' /
                                   -- '95.7% of GRI expires 2028 (pre-regear)'
  pct numeric, amount numeric, currency text, source_page int
);
-- evidence this earns a table: Elite 92.3% DWP; KDC one client = $289.1m/65% (notes-only,
-- absent from the portfolio review); Centurion PBWA 79% construction-sector;
-- Sasseur top-10 = 14.4% vs CLAS top-10 = 2.4% — the spread IS the story

-- sgx_reit_valuation_inputs: v1 + nullable property_id (Keppel REIT per-building cap rates)
-- (ownership moved to §2.1/2.2: public_float_pct scalar + unitholders jsonb — the standalone
--  sgx_reit_unitholders table from v1 is dropped)
```

## 7. Long tail + agentic text layer (v1 kept)

```sql
-- canonical metric dictionary feeds both: alias_dict maps raw labels -> canonical keys
sgx_reit_facts (symbol, fiscal_year, metric_key, scope, property_id, value_numeric, value_text,
                unit, currency, basis, figure_type, extraction_method, confidence, source_page)
-- examples now verified in the wild: revpau, adr, occupancy_hotel, shopper_traffic,
-- vip_members, outlet_sales, beds_pipeline, tenant_retention_pct, same_store_npi_growth,
-- like_for_like_npi_growth (Stoneweg), pue, tenant_sales_growth

sgx_reit_doc_chunks (symbol, fiscal_year, report_type, page, section_type, text, embedding)
```

---

## 8. Lineage — who contributed what

| Element | Source |
|---|---|
| Property-centric core, trade-mix/top-tenant JSON instincts, 39-trust universe | colleague's draft |
| symbol keys, typed-columns + jsonb style, computed-at-API rule, no market-data duplication | prod `sgx_*` |
| `land_tenure_*` family, `valuation_date` vs `acquisition` events | her feedback #1 + alias evidence (9 reports) |
| `service_entities`/`management`/`unitholders` as jsonb on master (not tables); `public_float_pct` as reliable ownership scalar | prod `sgx_companies` pattern + ownership disclosure check across 8 reports |
| `tenant_mix.scope` + mandatory `basis` + `is_derived` | her feedback #2, corrected by evidence (2/14 have property level) |
| revenue/expense components, accounting adjustments, standardized formulas in API layer | her feedback #3 + 14-report expense divergence |
| `ownership_basis`/`npi_attributable`/`held_via` | Keppel REIT JV evidence |
| `income_model`, `ema_*`, `gross_profit`-as-NPI mapping, lease_structures | Sasseur / CLAS / Elite evidence |
| `figure_type`, `period_type`, `dpu_unit` | Centurion stub+forecast, Elite pence + pro-forma |
| multi-currency value+ccy+sgd triple, `valuation_per_sqm` | CLCT dual-column + Centurion mixed-currency evidence |
| provenance columns, doc_chunks RAG layer | v1 proposal (agentic requirement) |

## 9. Expected fill rates (14-report sample)

| Block | Fill | Note |
|---|---|---|
| financials core | 100% | stub periods flagged, not annualised |
| properties + snapshots (valuation/tenure/occupancy) | ~95% | CLAS = cost-only listing |
| snapshot gross_revenue | ~79% | missing: First REIT, KDC, CLAS |
| snapshot npi_disclosed | ~29% | FCT, KORE, CLCT, Keppel REIT (attributable) |
| tenant_mix property scope | ~14% | CICT, Sasseur only |
| tenant_mix portfolio scope, top tenants, lease metrics, expiry | 100% | bases vary — captured |
| revenue/expense components | 100% | granularity varies (Stoneweg expenses thin) |
| distributions, debt, fees, segments | 100% | |
| service_entities (manager/sponsor/trustee) | 100% | from Trust Structure page |
| public_float_pct | ~100% | SGX Rule 723-mandated — the reliable ownership field |
| unitholders (substantial, named) | ~60% | clean table ~3/5; deemed-interest footnotes or float-only elsewhere |
| concentrations | ~70% | notes-mining required |

## 10. Validation round — 6 more trusts, schema deliberately stress-tested

After v2 was drafted, 6 previously untouched FY2025 reports were parsed and audited *against* the
schema (CapitaLand India Trust — business trust; Daiwa House Logistics — Japan TMK; Digital Core —
partial-stake data centres; Manulife US — distressed restructuring; Suntec — convention centre +
JVs; United Hampshire — strip retail + self-storage). Corpus now: **20 usable ARs**.

### What survived unchanged

- Audited Portfolio Statement near-universal: 20/20 have per-property tenure + valuation
  (CLAS cost-only is still the lone outlier on valuation).
- `ownership_pct` + `held_via` + attributable qualifiers: exactly fit DCR (Frankfurt associate →
  consolidated mid-period; Osaka 20% associates, "at share" metrics) and Suntec's JV stack.
- `income_model`, dual-scope tenant mix, mandatory `basis`, component tables, `figure_type`,
  events table, segments with `dimension='contract_type'|'business'` — all held. Suntec's
  convention centre lands cleanly in segments (`business='convention'`), not in property P&L.
- Distributions tolerate DPU=0 (Manulife: halted since 2023, statement still published).
- Updated fill rates on the 20-report corpus: per-property gross revenue **~16/20** (new misses:
  MUST, UHREIT — both segment-level only); per-property NPI **7/20** (FCT, KORE, CLCT,
  Keppel REIT, CLINT, Daiwa — all 19 properties!, Suntec direct) — better than the 4/14 estimate.

### Deltas adopted from the validation round

```sql
-- 1. Disclosure-status beats bare NULL (Daiwa: single-tenant gross revenue withheld for
--    tenant confidentiality — a different fact than 'not disclosed')
alter table sgx_reit_property_snapshots add column
  revenue_disclosure text default 'disclosed'
  check (revenue_disclosure in ('disclosed','confidential','not_disclosed'));

-- 2. Third per-property income basis (Suntec JV buildings report 'net income contribution'
--    = share of profit + interest on JV loans; neither consolidated nor attributable NPI)
--    npi_basis: ('consolidated','attributable','net_income_contribution')

-- 3. FX provenance (CLCT prints 5.499; Daiwa prints none — rate must carry its source)
--    add fx_rate_used numeric, fx_rate_source text ('disclosed','inferred','market')
--    wherever local + SGD pairs exist.

-- 4. capacity_unit gains 'kw' (DCR reports customer IT load in kW, not MW);
--    sgx_reit_top_tenants gains credit_rating text (DCR rates every top customer).

-- 5. Distress layer (Manulife): a healthy-REIT schema misses the most newsworthy data.
create table sgx_reit_covenants (
  id serial primary key,
  symbol text, fiscal_year smallint,
  covenant text,                  -- 'unencumbered_gearing_max', 'icr_min', ...
  threshold numeric, actual numeric, status text,  -- compliant|breached|waived|relaxed
  relaxation_expiry date,         -- MUST: 80% cap sunsets 30 Jun 2026
  detail text, source_page int
);
-- plus: sgx_reit_financials.going_concern_uncertainty boolean (auditor's material-uncertainty
-- paragraph); disposal mandates / proceeds targets / sponsor-loan exit premiums →
-- property_events + facts; rent_reversion_pct and new-lease WALE (scope='new_leases') → facts.

-- 6. Development pipeline (CLINT: 6 forward purchases with expected consideration/completion,
--    phased handover; Centurion: beds pipeline) — separate table, not status flags:
create table sgx_reit_developments (
  id serial primary key,
  symbol text, property_id int,   -- null until operational
  project_name text, location text,
  expected_cost numeric, currency text,
  expected_completion text,       -- '2H 2026' granularity as disclosed
  floor_area_sqft numeric, capacity_value numeric, capacity_unit text,
  funding_structure text,         -- CLINT: secured-debt forward funding
  status text, source_page int
);
```

Plus two extraction-rule notes (no DDL): ground/land-lease rent may sit outside property
expenses (UHREIT routes it through distribution adjustments; CLAR books it as right-of-use
lease) — the standardized-NPI formula must look in both places; perpetual securities are
excluded from gearing but included in ICR (CLINT) — formula registry must encode that.

### Conviction verdict

Six adversarial reports produced **zero structural rewrites** — every break was absorbed by a
qualifier column, one small table, or an extraction rule. The three-layer shape (typed core →
qualified satellites → facts/chunks) is stable across 20 trusts, 6 income models, 7 currencies,
healthy and distressed. Schema is ready for the LlamaExtract pilot.

## 11. Open decisions before freeze

1. **Sasseur real AR re-source** — done for FY2023 (this synthesis includes it); fix the FY2024
   catalog link (currently the sustainability report).
2. Whether `sgx_reit_financials.gross_profit` deserves its own column vs mapping CLAS into
   `net_property_income` with `income_model` disambiguating (current choice: map + flag).
3. Conversion policy: store SGD at **disclosed** rates only (CLCT prints 5.499) vs computing from
   `sgx_daily_data`-style FX — recommend disclosed-when-available, else month-end rate, recorded
   in a `fx_rate_used` column.
4. The walkthrough call on her term list (tenure / purchase vs effective date / manager roles)
   against §2.2 and §3 — schema holds them; extraction prompts need her domain notes.
5. Pilot order: extract CICT + FCT + CLCT first (richest property-level disclosure) → validate
   roll-ups (property gross revenue Σ vs reported total; CLCT NPI Σ RMB1,104.6m) → then the
   hard models (Sasseur, CLAS, Keppel REIT).
