# `sgx_reit_*` schema

8 tables + 1 materialized view. Keyed on `symbol` (properties keep an integer `id`).
Market cap, price/volume, shares, and standard financial statements are never stored —
fetched from `sgx_companies` / `sgx_daily_data` / `sgx_company_report`.

All computed metrics (yield, P/NAV, standardized NPI, land lease remaining, derived trade
mix) live in the API layer as versioned formulas — never as columns.

## sgx_reit_profile

REIT-specific columns only; everything else lives in sectors DB.

```sql
create table sgx_reit_profile (
  symbol           text primary key references sgx_companies(symbol),
  reit_sub_sector  text,        -- Retail | Industrial | Hospitality | Diversified | ...
  income_model     text         -- conventional | master_lease | mcmgi |
                                -- management_contract | entrusted_management | fri | mixed
                                -- our classification (not an official label), derived from
                                -- the lease/contract structures the AR itself describes;
                                -- set once per trust, tells formulas how to read its
                                -- income lines

);
```

## sgx_reit_management

```sql
create table sgx_reit_management (
  symbol       text references sgx_reit_profile(symbol),
  company_name text,
  ownership    numeric,
  role         text,            -- reit_manager | property_manager | operator |
                                -- master_lessee | trustee | sponsor
  property_id  int,             -- null = portfolio-wide
  source_page  int
);
```

## sgx_reit_property

One row per (symbol, property, fiscal_year). A property sold to another trust appears
under the buyer's symbol the following year.

```sql
create table sgx_reit_property (
  id                  serial primary key,
  symbol              text references sgx_reit_profile(symbol),
  fiscal_year         smallint,
  country             text,
  category            text,
  property_name       text,
  address             text,
  ownership           numeric,   -- % stake
  value_basis         text default 'consolidated'
                      check (value_basis in
                        ('consolidated','joint_venture_100pct','effective_interest')),
  market_valuation    numeric,
  valuation_date      date,      -- "as at" date of the latest independent valuation
                                 -- (usually FYE); applies to every property, not only JV
  currency            text,
  net_property_income numeric,   -- as-disclosed only, never computed
  gross_revenue       numeric,
  occupancy_rate      numeric,
  trade_mix           jsonb,     -- {"Food & Beverages": 33.9, ...} property-level set
  major_tenants       jsonb,     -- top/anchor tenant names for this property, as disclosed
  gla                 numeric,
  nla                 numeric,
  land_tenure         text,      -- Freehold | Leasehold
  effective_date      date,      -- land-lease commencement ("with effect from ...")
  lease_term_years    numeric,
  lease_expiry_date   date,      -- as disclosed only (never derived; some reports print
                                 -- expiry without start date, or dual expiries)
  tenure_raw          text,      -- verbatim tenure string from the report, kept for audit
  status              text default 'active',  -- active | divested | held_for_sale
  source_page         int,
  unique (symbol, property_name, fiscal_year)
);
```

No stored remaining-lease column — computed from dates at query time.

## sgx_reit_property_transaction

One row per phase (phased acquisitions are common).

```sql
create table sgx_reit_property_transaction (
  property_id      int references sgx_reit_property(id),
  transaction_type text check (transaction_type in ('acquisition','divestment')),
  transaction_year smallint,
  transaction_date date,
  price            numeric,
  currency         text,
  stake_pct        numeric,
  counterparty     text,
  source_page      int
);
```

## sgx_reit_performance

One row per (symbol, fiscal_year).

```sql
create table sgx_reit_performance (
  symbol                   text references sgx_reit_profile(symbol),
  fiscal_year              smallint,
  portfolio_value          numeric,  -- headlined portfolio valuation incl. JV
                                     -- proportionate interests (pinned definition)
  properties_location      text,
  gross_revenue            numeric,
  net_property_income      numeric,  -- as reported
  net_distributable_income numeric,
  dpu                      numeric,  -- cents
  distribution_record      jsonb,    -- [{period, dpu, ex_date, pay_date}]
  number_of_unitholders    int,
  currency                 text,
  source_report            text,
  source_page              int,
  primary key (symbol, fiscal_year)
);
```

## sgx_reit_top_tenant

```sql
create table sgx_reit_top_tenant (
  symbol         text references sgx_reit_profile(symbol),
  fiscal_year    smallint,
  rank           smallint,
  tenant_name    text,        -- null when anonymised
  trade_sector   text,
  gri_percentage numeric,
  pct_basis      text,        -- gri | gri_excl_gto | gross_revenue | rental_income |
                              -- headline_rent | cash_rental_income | nla | outlet_sales
  source_page    int,
  primary key (symbol, fiscal_year, rank)
);
```

## sgx_reit_trade_mix

REIT-level set; `is_derived = true` marks our property-level roll-up stored beside the
disclosed figures.

```sql
create table sgx_reit_trade_mix (
  symbol      text references sgx_reit_profile(symbol),
  fiscal_year smallint,
  category    text,
  pct         numeric,
  pct_basis   text,
  is_derived  boolean default false,
  source_page int
);
```

## sgx_reit_income_component

Raw audited revenue/expense note lines — the inputs for standardized formulas.

```sql
create table sgx_reit_income_component (
  symbol      text references sgx_reit_profile(symbol),
  fiscal_year smallint,
  statement   text check (statement in ('revenue','expense','adjustment')),
  component   text,            -- canonical key (base_rental, turnover_rent, recoveries,
                               -- property_tax, utilities, staff, loss_allowance, ...)
  amount      numeric,
  currency    text,
  label_raw   text,            -- exact audited note line
  source_page int,
  primary key (symbol, fiscal_year, statement, component)
);
```

## mv_sgx_reit

```sql
create materialized view mv_sgx_reit as
select c.symbol, c.name, c.sector,
       p.reit_sub_sector, p.income_model,
       perf.fiscal_year, perf.portfolio_value, perf.net_property_income,
       perf.dpu, perf.net_distributable_income
from sgx_companies c
join sgx_reit_profile p using (symbol)
left join sgx_reit_performance perf using (symbol);
```
