# `sgx_reit_*` Production Schema v3 — consolidated proposal

> Consolidation of v2 (`sgx_reit_schema_v2.md`, 25 tables) into **12 physical tables**
> (6 typed core + 4 generic surfaces + dictionary + chunks) with a compatibility view layer.
>
> Nothing from the 20-report evidence base is dropped: every qualifier that survived the
> validation round (`basis`, `figure_type`, `npi_basis`, `revenue_disclosure`, `held_via`,
> fx provenance, the distress layer) carries over. What changes is the **number of physical
> surfaces**, not the information model.

---

## 0. The consolidation thesis

The v2 audit revealed that most of the 25 tables are **four shapes repeated with different
enums**:

| Recurring shape | v2 tables that share it | v3 home |
|---|---|---|
| Audited P&L line item — `(symbol, fy, component, amount, currency, label_raw)` | revenue_components, expense_components, accounting_adjustments | `sgx_reit_components` |
| Compositional breakdown — `(scope, category, pct/amount, basis)` summing to ~100% | tenant_mix, lease_expiry, segments, debt_maturity | `sgx_reit_breakdowns` |
| Named record — an entity/arrangement with a few numbers + verbatim detail | entities, top_tenants, unitholders, debt_instruments, fees, covenants, lease_structures, concentrations | `sgx_reit_records` |
| Scalar metric — `(metric_key, scope, value, basis, figure_type)` | facts, lease_metrics, valuation_inputs | `sgx_reit_facts` |

The typed core (trusts, properties, events, snapshots, financials, distributions) stays
typed — those are the 100%-fill universal facts the screener hits constantly, where
columns and CHECK constraints earn their keep.

The piece that makes generic surfaces safe is **promoting the alias/metric dictionary to a
physical table** (`sgx_reit_dictionary`). It replaces the CHECK-constraint enums lost in the
merge, and it is the agentic superpower: an agent can *read* what every key, basis and
caveat means instead of having that knowledge baked into prompts. Self-describing data.

---

## 1. Design rules (v2 rules carried, three added)

1. **Key on `symbol` text** referencing `sgx_companies` (prod convention).
2. **Never store what prod already has** (price/volume/market cap).
3. **Computed metrics live in the API layer** — the DB stores raw audited inputs.
4. **Every percentage carries its `basis`; every fact carries provenance.**
5. **As-disclosed, not as-wished** — nullable means "this trust doesn't disclose it".
6. Typed columns for the universal core; generic surfaces + jsonb for the long tail.
7. **(new) Every key in a generic surface FKs to the dictionary.** No undocumented
   `component` / `dimension` / `record_type` / `metric_key` / `basis` values can enter the DB.
8. **(new) v2 semantics survive as views.** `sgx_reit_tenant_mix`, `sgx_reit_segments`,
   `sgx_reit_covenants` etc. are recreated as views over the generic surfaces — humans and
   the API keep the friendly names; we maintain 12 tables instead of 25.
9. **(new) Composite-PK guarantees become partial unique indexes.** Same protection
   (one row per `(symbol, fy, component)` etc.), expressed per key-family instead of per table.

---

## 2. The dictionary — governance for the generic surfaces

```sql
create table sgx_reit_dictionary (
  key_family   text not null check (key_family in
                 ('component','dimension','record_type','metric_key','basis',
                  'figure_type','scope_type')),
  key          text not null,
  definition   text not null,
  valid_scopes text[],            -- e.g. {portfolio, segment, property}
  valid_bases  text[],            -- e.g. wale: {nla, gri, cri, lettable_area, ...}
  aliases      jsonb,             -- raw labels seen in the wild -> this key
                                  -- e.g. event_date: ["Date of legal completion" (MLT),
                                  --      "Acquisition date" (CLAR, First REIT, Stoneweg, KORE)]
  caveats      text,              -- the traps, verbatim:
                                  -- "‘Term of lease’ in a portfolio statement = the REIT's
                                  --  land lease, NOT a tenant lease";
                                  -- "perpetual securities excluded from gearing but included
                                  --  in ICR (CLINT)";
                                  -- "ground rent may sit outside property expenses —
                                  --  UHREIT routes it via distribution adjustments"
  formula_note text,              -- for metric_keys that feed standardized formulas
  primary key (key_family, key)
);
```

Seeded from the v2 alias dictionary + the §0/§10 evidence notes. Extraction prompts,
API formula registry and agent system-prompts are all **generated from this table** —
one source of truth for "what does this key mean and where does it not apply".

---

## 3. Typed core — 6 tables

### 3.1 `sgx_reits` — trust master (unchanged from v2)

```sql
create table sgx_reits (
  symbol             text primary key references sgx_companies(symbol),
  name               text not null,
  structure          text check (structure in ('reit','stapled_trust','business_trust')),
  sub_sector         text,
  income_model       text check (income_model in
                       ('conventional','master_lease','mcmgi','management_contract',
                        'entrusted_management','fri','mixed')),
  fye_month          smallint,
  reporting_currency text,
  listing_date       date,
  mandate            text,
  is_active          boolean default true
);
```

Manager/sponsor/trustee/master-lessee roles move to `sgx_reit_records`
(`record_type = 'entity_role'`) — see §4.3.

### 3.2 `sgx_reit_properties` — identity (**absorbs `sgx_reit_developments`**)

```sql
create table sgx_reit_properties (
  property_id     serial primary key,
  symbol          text references sgx_reits(symbol),
  property_name   text not null,
  country         text, city text, address text,
  category        text,
  ownership_pct   numeric default 100,
  held_via        text check (held_via in ('consolidated','joint_venture','associate'))
                  default 'consolidated',
  income_model    text,            -- property-level override (CLAS mixes 3; Centurion EPIISOD)
  land_tenure_type   text check (land_tenure_type in ('freehold','leasehold','mixed')),
  tenure_raw         text,
  land_lease_term_years      numeric,
  land_lease_expiry_date     date,
  land_lease_remaining_years numeric,
  nla_sqm numeric, gfa_sqm numeric, land_area_sqm numeric,
  capacity_value numeric, capacity_unit text,        -- units|beds|rooms|MW|kW
  status          text default 'active' check (status in
                    ('active','divested','under_development','pipeline')),
                  -- 'pipeline' is the developments merge: CLINT's 6 forward purchases and
                  -- Centurion's beds pipeline are property rows that don't exist yet
  extras          jsonb,           -- pipeline rows: {expected_cost, expected_completion,
                                   --  funding_structure, floor_area_sqft, ...}
                                   -- (CLINT: secured-debt forward funding, '2H 2026')
  source_page     int,
  unique (symbol, property_name)
);
```

### 3.3 `sgx_reit_property_events` — unchanged from v2

```sql
create table sgx_reit_property_events (
  id            serial primary key,
  property_id   int references sgx_reit_properties(property_id),
  event_type    text check (event_type in ('acquisition','stake_increase','divestment',
                   'aei_completion','development_top','lease_regear','master_lease_start',
                   'consolidation_change')),
                  -- consolidation_change added: DCR Frankfurt associate -> consolidated
                  -- mid-period; the held_via flag shows current state, the event keeps history
  event_date    date,
  stake_pct     numeric,
  price         numeric, price_currency text,
  is_post_period boolean default false,
  detail        text, source_page int
);
```

### 3.4 `sgx_reit_property_snapshots` — unchanged from v2 (incl. validation deltas)

```sql
create table sgx_reit_property_snapshots (
  property_id     int references sgx_reit_properties(property_id),
  fiscal_year     smallint,
  valuation       numeric, valuation_currency text, valuation_sgd numeric,
  fx_rate_used    numeric, fx_rate_source text
                  check (fx_rate_source in ('disclosed','inferred','market')),
  valuation_per_sqm numeric,
  valuation_date  date,
  cap_rate_pct    numeric,
  gross_revenue   numeric, gross_revenue_currency text,
  revenue_disclosure text default 'disclosed'
                  check (revenue_disclosure in ('disclosed','confidential','not_disclosed')),
  gri             numeric,
  rent_received   numeric,
  npi_disclosed   numeric,
  npi_basis       text check (npi_basis in
                    ('consolidated','attributable','net_income_contribution')),
  ema_rental_income numeric,
  outlet_sales    numeric,
  occupancy_pct   numeric,
  occupancy_type  text check (occupancy_type in ('committed','actual','average')),
  tenant_count    smallint,
  shopper_traffic bigint,
  major_tenants   jsonb,
  extras          jsonb,
  source_page     int,
  primary key (property_id, fiscal_year)
);
```

### 3.5 `sgx_reit_financials` — unchanged from v2 (incl. distress flag)

```sql
create table sgx_reit_financials (
  symbol               text references sgx_reits(symbol),
  fiscal_year          smallint,
  fiscal_label         text,
  period_start         date, period_end date,
  period_type          text check (period_type in ('full_year','stub')) default 'full_year',
  gross_revenue        numeric,
  net_property_income  numeric,     -- CLAS 'gross profit' maps here; income_model disambiguates
  npi_attributable     numeric,
  share_of_jv_results  numeric,
  distributable_income numeric,
  dpu                  numeric,
  dpu_unit             text default 'sgd_cents',
  total_assets numeric, investment_properties numeric, portfolio_value numeric,
  nav_per_unit numeric, units_in_issue bigint,
  aggregate_leverage_pct  numeric,
  leverage_basis          text,
  interest_coverage_x numeric, avg_cost_of_debt_pct numeric,
  pct_fixed_rate_debt numeric, avg_debt_maturity_years numeric,
  total_borrowings numeric, unencumbered_assets_pct numeric,
  property_count smallint, occupancy_pct numeric,
  going_concern_uncertainty boolean default false,
  extras       jsonb,
  figure_type  text default 'actual' check (figure_type in
                 ('actual','forecast','pro_forma','annualised')),
  source_report text, source_pages jsonb,
  updated_on    timestamptz default now(),
  primary key (symbol, fiscal_year, figure_type)
);
```

### 3.6 `sgx_reit_distributions` — per-distribution time series (kept typed)

One more typed table than the back-of-envelope count, and deliberately so: per-distribution
rows (ex-date, pay date, taxable/exempt/capital split) are a clean, high-fill time series
that yield history and the screener query constantly. Squeezing it into `records` would
trade real ergonomics for one table fewer. v2 shape kept, + `dpu_unit` (Elite pence) +
`figure_type`. Tolerates DPU = 0 (Manulife: halted since 2023, statement still published).

```sql
create table sgx_reit_distributions (
  symbol text references sgx_reits(symbol),
  fiscal_year smallint, period_label text,        -- '1H FY2025', 'FP 2025'
  dpu numeric, dpu_unit text default 'sgd_cents',
  ex_date date, pay_date date,
  components jsonb,                               -- taxable / exempt / capital / withheld
  figure_type text default 'actual',
  source_page int,
  primary key (symbol, fiscal_year, period_label, figure_type)
);
```

---

## 4. Generic surfaces — 4 tables

### 4.1 `sgx_reit_components` — every audited P&L line

Merges v2 `revenue_components` + `expense_components` + `accounting_adjustments`
(identical shapes; one discriminator column).

```sql
create table sgx_reit_components (
  symbol      text references sgx_reits(symbol),
  fiscal_year smallint,
  statement   text not null check (statement in ('revenue','expense','adjustment')),
  component   text not null,       -- FK -> dictionary('component', ...)
    -- revenue:    base_rental | turnover_rent | service_charge | recoveries | car_park |
    --             hospitality | hotel_revenue | ema_fixed | ema_variable | dilapidations | other
    -- expense:    property_tax | business_tax_vat | utilities | maintenance |
    --             property_mgmt_fee | mgmt_reimbursement | marketing | staff |
    --             insurance_security | loss_allowance | land_rent | depreciation_ffe |
    --             leasing_commission_amort | other
    -- adjustment: straight_line_rent | lease_incentive_amort | ema_straight_line |
    --             rental_support
  amount      numeric, currency text,
  component_label_raw text,        -- exact note label, for audit
  source_page int,
  primary key (symbol, fiscal_year, statement, component),
  foreign key (component) references sgx_reit_dictionary... -- via (key_family='component', key)
);
```

Evidence carried from v2: FCT GTO rent $15.8m; KORE recoveries $42m (28% of revenue);
Stoneweg €44m service charges; Sasseur RMB447.5m fixed + RMB211.0m variable; Elite £1.6m
one-off dilapidations; utilities = 35% of CLAR's expenses; loss allowance = 36% of KDC's;
KORE's reported NPI +3.0% vs adjusted +0.3%. Standardized NPI / margins / cost ratios are
computed in the API layer **from this one surface**.

### 4.2 `sgx_reit_breakdowns` — anything that distributes over categories

Merges v2 `tenant_mix` + `lease_expiry` + `segments` + `debt_maturity`. The single biggest
agentic win: one query surface answers *"show me any compositional breakdown of this trust"*.

```sql
create table sgx_reit_breakdowns (
  id          bigserial primary key,
  symbol      text references sgx_reits(symbol),
  fiscal_year smallint,
  dimension   text not null,       -- FK -> dictionary('dimension', ...)
    -- trade_sector | lease_expiry_fy | segment_business | segment_geography |
    -- segment_contract_type | segment_lease_type | debt_maturity_fy | currency_exposure
  scope       text not null default 'portfolio'
              check (scope in ('portfolio','segment','property')),
  property_id int references sgx_reit_properties(property_id),
                                   -- CICT (26 properties) & Sasseur (4 outlets) fill this
  segment     text,                -- CLAR: mix per segment-geography
  category    text not null,       -- the bucket label as disclosed
  is_terminal_bucket boolean default false,   -- 'FY2030 and beyond' rows
  pct         numeric, amount numeric, currency text,
  npi         numeric, segment_assets numeric, -- segment-P&L extras (null elsewhere)
  basis       text not null,       -- FK -> dictionary('basis', ...)
    -- gri | gri_excl_gto | gross_revenue | rental_income | headline_rent |
    -- cash_rental_income | committed_gross_rent | nla | outlet_sales | debt_principal
  figure_type text default 'actual',
  is_derived  boolean default false,           -- our roll-up beside disclosed, never mixed
  source_page int
);

-- one disclosed row per cell, derived rows live alongside:
create unique index uq_breakdown_cell on sgx_reit_breakdowns
  (symbol, fiscal_year, dimension, scope, coalesce(property_id,-1),
   coalesce(segment,''), category, basis, figure_type)
  where not is_derived;
create index ix_breakdown_dim on sgx_reit_breakdowns (dimension, symbol, fiscal_year);
```

Everything the v2 evidence demanded survives: dual scope (2/14 trusts have property-level
mix), mandatory `basis` (Sasseur's per-outlet mix is % of **sales**), `is_derived` roll-up
validation, Suntec's convention centre as `dimension='segment_business'`, CLAS's
contract-type P&L as `dimension='segment_contract_type'`, Elite's 95.7%-expires-2028 ladder.

### 4.3 `sgx_reit_records` — named things with attributes

Merges v2 `entities` + `top_tenants` + `unitholders` + `debt_instruments` + `fees` +
`covenants` + `lease_structures` + `concentrations`. All are "a named/ranked entity or
arrangement, a few numbers, verbatim detail". Type-specific fields go in `detail` jsonb —
acceptable because these rows are read by agents and detail pages, not aggregated by
screeners.

```sql
create table sgx_reit_records (
  id          bigserial primary key,
  symbol      text references sgx_reits(symbol),
  fiscal_year smallint,
  record_type text not null,       -- FK -> dictionary('record_type', ...)
    -- entity_role | top_tenant | unitholder | debt_instrument | fee |
    -- covenant | lease_structure | concentration
  property_id int references sgx_reit_properties(property_id),  -- null = portfolio-wide
  name        text,                -- entity / tenant / instrument / project name;
                                   -- NULL when anonymised (KDC hyperscalers) — that is data
  kind        text,                -- the per-type sub-enum, dictionary-governed:
                                   --   entity_role: reit_manager|property_manager|operator|
                                   --     master_lessee|entrusted_manager|trustee|sponsor|valuer
                                   --   lease_structure: turnover_rent_provision|fixed_escalation|
                                   --     cpi_indexation|minimum_rent_guarantee|
                                   --     variable_pct_of_sales|fri|renewal_option
                                   --   concentration: tenant|client|geography|sector|
                                   --     lease_expiry_year
                                   --   covenant: unencumbered_gearing_max|icr_min|...
  rank        smallint,            -- top_tenant / unitholder ordering
  pct         numeric, amount numeric, currency text,
  basis       text,                -- mandatory where pct is set (enforced by trigger/check)
  pct_nla     numeric,             -- FCT & Keppel REIT give both % rent and % NLA
  scope       text default 'portfolio',  -- CLAS top-10 covers mgmt-contract properties only
  is_related_party boolean,        -- Sasseur EM, Centurion CPPL, First REIT lessees
  status      text,                -- covenant: compliant|breached|waived|relaxed
  detail      jsonb,               -- per-type payload:
                                   --   covenant: {threshold, actual, relaxation_expiry}
                                   --     (MUST 80% cap sunsets 2026-06-30)
                                   --   fee: {formula_text} — mandatory verbatim
                                   --     (Centurion PBWA '2% gross revenue + 5% NPI';
                                   --      Sasseur EM '30% of GR base + 60% performance split')
                                   --   top_tenant: {trade_sector, properties[], credit_rating}
                                   --     (DCR rates every top customer)
                                   --   lease_structure: {value_pct, coverage_pct,
                                   --     coverage_basis} (Sasseur 4.0–5.5% of sales/outlet;
                                   --     CLCT 90.9% of leases with GTO terms)
                                   --   debt_instrument: {facility_type, maturity, rate, ...}
  source_page int
);
create index ix_records_type on sgx_reit_records (record_type, symbol, fiscal_year);
create unique index uq_records_rank on sgx_reit_records
  (symbol, fiscal_year, record_type, rank)
  where rank is not null and record_type in ('top_tenant','unitholder');
```

### 4.4 `sgx_reit_facts` — scalar metrics (absorbs `lease_metrics` + `valuation_inputs`)

```sql
create table sgx_reit_facts (
  symbol      text references sgx_reits(symbol),
  fiscal_year smallint,
  metric_key  text not null,       -- FK -> dictionary('metric_key', ...)
    -- wale | walb (lease_metrics merge: Stoneweg WALB 4.0y vs WALE 4.9y)
    -- cap_rate | discount_rate | terminal_yield (valuation_inputs merge;
    --   Keppel REIT per-building cap rates via property_id)
    -- revpau | adr | occupancy_hotel | shopper_traffic | vip_members | outlet_sales |
    -- beds_pipeline | tenant_retention_pct | same_store_npi_growth |
    -- like_for_like_npi_growth | pue | tenant_sales_growth | rent_reversion_pct | ...
  scope       text not null default 'portfolio',
              -- portfolio | segment:<x> | country:<x> | top10_tenants | new_leases
  property_id int references sgx_reit_properties(property_id),
  value_numeric numeric, value_text text,
  unit        text, currency text,
  basis       text,                -- mandatory for wale/walb etc. — dictionary's
                                   -- valid_bases says which metrics require it
  figure_type text default 'actual',   -- Elite WALE 2.4y actual vs 7.2y pro_forma
  extraction_method text, confidence numeric,   -- chart-derived numbers carry confidence
  source_page int,
  primary key (symbol, fiscal_year, metric_key, scope,
               coalesce(property_id,-1), coalesce(basis,''), figure_type)
               -- expressed as a unique index in practice
);
```

Promotion rule unchanged: when a facts metric proves dense and frequently queried (as
`npi_disclosed` did), it graduates to a typed column in the core.

---

## 5. `sgx_reit_doc_chunks` — RAG layer (unchanged)

```sql
create table sgx_reit_doc_chunks (
  symbol text, fiscal_year smallint,
  report_type text, page int, section_type text,
  text text, embedding vector
);
```

Structured tables tell an agent **what**; chunks let it explain **why**, with page-level
citations — concentration narratives, covenant waivers, going-concern language, subsequent
events are prose first.

---

## 6. Compatibility view layer — v2 names survive

```sql
create view v_sgx_reit_tenant_mix as
  select symbol, fiscal_year, scope, property_id, segment, category, pct, basis,
         is_derived, source_page
  from sgx_reit_breakdowns where dimension = 'trade_sector';

create view v_sgx_reit_lease_expiry as
  select symbol, fiscal_year, category as expiry_fy, is_terminal_bucket,
         basis, segment, pct, source_page
  from sgx_reit_breakdowns where dimension = 'lease_expiry_fy';

create view v_sgx_reit_segments as
  select symbol, fiscal_year,
         replace(dimension,'segment_','') as dimension,
         category as segment, amount as gross_revenue, npi, segment_assets,
         currency, source_page
  from sgx_reit_breakdowns where dimension like 'segment_%';

create view v_sgx_reit_top_tenants as
  select symbol, fiscal_year, rank, name as tenant_name,
         detail->>'trade_sector' as trade_sector, pct, basis, pct_nla, scope,
         detail->>'credit_rating' as credit_rating, source_page
  from sgx_reit_records where record_type = 'top_tenant';

create view v_sgx_reit_covenants as
  select symbol, fiscal_year, kind as covenant,
         (detail->>'threshold')::numeric as threshold,
         (detail->>'actual')::numeric    as actual,
         status, (detail->>'relaxation_expiry')::date as relaxation_expiry,
         source_page
  from sgx_reit_records where record_type = 'covenant';

create view v_sgx_reit_entities as
  select symbol, fiscal_year, kind as role, name as entity_name,
         property_id, is_related_party, source_page
  from sgx_reit_records where record_type = 'entity_role';

create view v_sgx_reit_lease_metrics as
  select symbol, fiscal_year, metric_key as metric, scope, basis,
         value_numeric as years, figure_type, source_page
  from sgx_reit_facts where metric_key in ('wale','walb');

-- ...same pattern for fees, unitholders, debt_instruments, concentrations,
--    revenue/expense components (statement filter), valuation_inputs.
```

API code and human queries read the views; the extraction pipeline writes the 4 surfaces.
Partial indexes on `(dimension)` / `(record_type)` / `(metric_key)` keep view queries flat.

---

## 7. v2 → v3 migration map

| v2 table (25) | v3 home (12) | Notes |
|---|---|---|
| sgx_reits | `sgx_reits` | unchanged |
| sgx_reit_entities | `sgx_reit_records` | record_type='entity_role'; role → kind |
| sgx_reit_properties | `sgx_reit_properties` | + status='pipeline', + extras jsonb |
| sgx_reit_developments | `sgx_reit_properties` | pipeline rows; milestones → property_events |
| sgx_reit_property_events | `sgx_reit_property_events` | + 'consolidation_change' (DCR) |
| sgx_reit_property_snapshots | `sgx_reit_property_snapshots` | unchanged incl. validation deltas |
| sgx_reit_financials | `sgx_reit_financials` | unchanged incl. going_concern flag |
| sgx_reit_revenue_components | `sgx_reit_components` | statement='revenue' |
| sgx_reit_expense_components | `sgx_reit_components` | statement='expense' |
| sgx_reit_accounting_adjustments | `sgx_reit_components` | statement='adjustment' |
| sgx_reit_covenants | `sgx_reit_records` | record_type='covenant'; threshold/actual/sunset in detail |
| sgx_reit_tenant_mix | `sgx_reit_breakdowns` | dimension='trade_sector' |
| sgx_reit_lease_expiry | `sgx_reit_breakdowns` | dimension='lease_expiry_fy' |
| sgx_reit_segments | `sgx_reit_breakdowns` | dimension='segment_*' |
| sgx_reit_debt_maturity | `sgx_reit_breakdowns` | dimension='debt_maturity_fy', basis='debt_principal' |
| sgx_reit_top_tenants | `sgx_reit_records` | record_type='top_tenant' |
| sgx_reit_lease_metrics | `sgx_reit_facts` | metric_key ∈ {wale, walb} |
| sgx_reit_lease_structures | `sgx_reit_records` | record_type='lease_structure' |
| sgx_reit_concentrations | `sgx_reit_records` | record_type='concentration' |
| sgx_reit_fees | `sgx_reit_records` | record_type='fee'; formula_text mandatory in detail |
| sgx_reit_debt_instruments | `sgx_reit_records` | record_type='debt_instrument' |
| sgx_reit_unitholders | `sgx_reit_records` | record_type='unitholder' |
| sgx_reit_valuation_inputs | `sgx_reit_facts` | metric_key ∈ {cap_rate, discount_rate, ...} |
| sgx_reit_distributions | `sgx_reit_distributions` | kept typed — high-fill time series |
| sgx_reit_facts / doc_chunks | unchanged | facts gains the merged metric families |
| *(new)* | `sgx_reit_dictionary` | promoted from extraction-side alias dict |

---

## 8. What is traded away, and the mitigations

| Loss | Mitigation |
|---|---|
| Per-table CHECK enums on merged surfaces | FK to `sgx_reit_dictionary` — stronger, actually: definitions + aliases + caveats travel with the constraint |
| Composite PKs (one row per cell) | Partial unique indexes per key-family (§4.2, §4.3) |
| Self-explanatory table names when browsing raw schema | Compatibility views (§6) + dictionary |
| Typed columns for covenant threshold/sunset, fee formulas | jsonb `detail` — these rows feed agents and detail pages, not aggregations; views re-type them |
| Slightly wider rows with many NULLs on generic surfaces | Postgres NULL storage is ~free; partial indexes keep scans narrow |

What is **not** traded away: any qualifier from the 20-report evidence. `basis` remains
NOT NULL on breakdowns; `figure_type`/`period_type` still gate every financial row;
`held_via`/`npi_basis`/`revenue_disclosure`/`fx_rate_source` are untouched in the typed
core; the distress layer survives as covenant records + the going-concern flag.

## 9. Why this is *better* for agentic systems, not just smaller

1. **Four query surfaces instead of seventeen.** An agent answering "what's risky about
   this trust?" hits records (covenants, concentrations, related parties), breakdowns
   (expiry ladder, geography), facts (reversions, WALE) — three queries, not twelve.
2. **The dictionary is machine-readable context.** Tool descriptions, extraction prompts
   and formula caveats generate from one table; the agent can look up what
   `cash_rental_income` means mid-conversation.
3. **Uniform provenance.** Every surface carries `source_page` (+ confidence where
   chart-derived) in the same position — citation plumbing is written once.
4. **New disclosure families need a dictionary row, not a migration.** The stress-test
   lesson generalized: of the 6 v2.1 deltas, 4 would have been dictionary/jsonb additions
   under v3, and only the typed-core ones (fx provenance, revenue_disclosure) would touch DDL.

## 10. Open decisions before freeze (v3-specific, on top of v2 §11)

1. **View naming**: `v_`-prefixed (shown here) vs reusing the bare v2 names. Bare names are
   friendlier but blur the table/view boundary in `psql \d`. Recommend `v_` prefix,
   API uses views exclusively.
2. **`basis` NOT NULL on records**: enforced via CHECK (`pct is null or basis is not null`)
   vs trigger. Recommend the CHECK — declarative and cheap.
3. **Dictionary write path**: who may add keys (migration-only vs a reviewed seed file).
   Recommend keys land via PR-reviewed seed migrations; the extraction pipeline may *propose*
   keys into a staging table but never insert directly.
4. **Debt instruments**: if facility-level analytics grow (hedging, refi walls), promote
   `debt_instrument` records back to a typed table — the promotion rule applies to records
   too, not just facts.
5. Pilot order unchanged from v2: CICT → FCT → CLCT, validate Σ(property gross revenue) and
   CLCT NPI Σ RMB1,104.6m, then the hard models (Sasseur, CLAS, Keppel REIT).
