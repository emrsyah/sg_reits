-- Cockpit v2 schema — sgx_reit_* (data) + review/inventory tables.
-- Mirrors schema/models.py. Nested/list fields -> jsonb. Idempotent (safe to re-run).
-- Apply: python scripts/db/apply_schema.py   (uses SUPABASE_CONNECTION_STRING)

-- ---------------------------------------------------------------------------
-- DATA TABLES (load target for extracted/; the jun17 "REITs DB = source of truth")
-- ---------------------------------------------------------------------------

create table if not exists sgx_reit_profile (
  symbol        text primary key,
  sub_sector    text,
  management    jsonb not null default '[]',     -- [{role, company_name}]
  income_model  text,
  source_page   int
);

create table if not exists sgx_reit_performance (
  id uuid primary key default gen_random_uuid(),
  symbol text not null,
  financial_year int not null,
  portfolio_value numeric,
  properties_location text,
  gross_revenue numeric,
  net_property_income numeric,
  net_distributable_income numeric,
  adjusted_distributable_income numeric,          -- distributable income AFTER fee adjustment (DPU method 2); null under method 1 (fees in units). Added 2026-06-22
  distribution_paid numeric,                      -- amount distributed/declared to unitholders for the year; net_distributable_income - distribution_paid = capital retained. NULL when no for-year line disclosed (see distribution_basis). Added 2026-06-23
  distribution_basis text,                        -- self-describing tag for distribution_paid: disclosed_after_retention | suspended | full_payout_no_retention_line | not_disclosed_rollforward_only. Added 2026-06-23
  dpu numeric,
  distribution_record jsonb,                      -- [{period, dpu, ex_date, pay_date}]
  number_of_unitholders int,
  aggregate_leverage numeric,
  interest_coverage_ratio numeric,
  cost_of_debt numeric,
  weighted_avg_debt_maturity numeric,
  nav_per_unit numeric,
  wale numeric,
  portfolio_occupancy numeric,
  currency text,
  date date,
  flags jsonb not null default '[]',
  source_page int,
  unique (symbol, financial_year)
);
-- migrations (idempotent — create table above won't alter an existing table)
alter table sgx_reit_performance add column if not exists adjusted_distributable_income numeric;
alter table sgx_reit_performance add column if not exists distribution_paid numeric;
alter table sgx_reit_performance add column if not exists distribution_basis text;

create table if not exists sgx_reit_property (
  id uuid primary key default gen_random_uuid(),
  symbol text not null,
  financial_year int not null,
  property_name text not null,
  country text,
  category text,
  category_raw text,
  address text,
  ownership numeric,
  market_valuation numeric,
  purchase_price numeric,                         -- ORIGINAL acquisition cost as-disclosed; enables (market_valuation - purchase_price)/purchase_price. Added 2026-06-23
  purchase_price_currency text,                   -- currency of purchase_price (foreign assets often disclosed in local ccy; compare vs original_value). Added 2026-06-23
  valuation_date date,
  currency text,                                  -- presentation currency (as-reported; prod -> SGD)
  original_currency text,                         -- AUDIT TRAIL: local/transacting ccy when reported separately (e.g. RMB)
  original_value numeric,                         -- AUDIT TRAIL: market_valuation in original_currency
  net_property_income numeric,
  gross_revenue numeric,
  npi_pct numeric,
  occupancy_rate numeric,
  trade_mix jsonb,                                -- {category: pct}
  major_tenants jsonb not null default '[]',      -- [{name, industry, pct}]
  gla numeric, nla numeric, gfa numeric,
  area_unit text,                                 -- AUDIT TRAIL: 'sqft'|'sqm' of gla/nla/gfa as reported (prod -> sqft)
  land_tenure text,
  effective_date date,
  lease_term_years numeric,
  lease_expiry_date date,
  tenure_raw text,
  status text not null default 'active',
  divestment_price numeric,
  flags jsonb not null default '[]',
  source_page int,
  unique (symbol, financial_year, property_name)
);
-- migrations (idempotent — create table above won't alter an existing table)
alter table sgx_reit_property add column if not exists original_currency text;
alter table sgx_reit_property add column if not exists original_value numeric;
alter table sgx_reit_property add column if not exists purchase_price numeric;
alter table sgx_reit_property add column if not exists purchase_price_currency text;
alter table sgx_reit_property add column if not exists area_unit text;

create table if not exists sgx_reit_top_tenant (
  id uuid primary key default gen_random_uuid(),
  symbol text not null,
  financial_year int not null,
  rank int not null,
  client_name text,
  industry text,
  revenue_pct numeric,
  pct_basis text,
  source_page int,
  unique (symbol, financial_year, rank)
);

create table if not exists sgx_reit_trade_mix (
  id uuid primary key default gen_random_uuid(),
  symbol text not null,
  financial_year int not null,
  category text not null,
  category_raw text,
  pct numeric,
  pct_basis text,
  source_page int
);

create table if not exists sgx_reit_financial (
  id uuid primary key default gen_random_uuid(),
  symbol text not null,
  financial_year int not null,
  currency text,
  income_stmt_metrics jsonb,                      -- incl. diluted_shares_outstanding + weighted_avg_shares_basic (DPU two-method cross-check; added 2026-06-22)
  balance_sheet_metrics jsonb,
  cash_flow_metrics jsonb,
  employee_breakdown jsonb,
  line_items jsonb not null default '[]',         -- [{statement, component, amount, label_raw, source_page}]
  source_page int,
  unique (symbol, financial_year)
);

-- property_transactions.json -> own table (CONFIRMED 2026-06-19). Core cols + raw passthrough.
create table if not exists sgx_reit_property_transaction (
  id uuid primary key default gen_random_uuid(),
  symbol text not null,
  financial_year int not null,
  transaction_type text,                          -- divestment | acquisition | announced_divestment | partial_divestment | divestment_terminated (alias: type)
  status text,                                     -- lifecycle: completed | announced | terminated (derived from transaction_type/explicit status). Repurposed 2026-07-01
  property_name text,
  transaction_date date,                          -- completion/effective date (aliases: date/completion_date/...). Added 2026-06-23
  description text,
  -- money (Phase-1 un-conflation 2026-07-01): gross sale price and net-of-cost proceeds are
  -- now DISTINCT columns (10 divestments disclose both; the old single net_proceeds dropped one).
  purchase_price numeric,                          -- ACQUISITION consideration paid (aliases: price/consideration/amount)
  gross_sale_price numeric,                        -- DIVESTMENT gross sale price / consideration, costs NOT deducted (aliases: sale_price/sale_consideration/price/consideration)
  net_sale_proceeds numeric,                       -- DIVESTMENT proceeds net of transaction costs (aliases: net_proceeds/net_consideration_usd)
  carrying_value numeric,                          -- book value just before divestment (basis for gain)
  gain_on_divestment numeric,
  valuation numeric,                               -- independent appraised value at the deal (Phase-B). Added 2026-06-23
  interest_pct numeric,                            -- % interest acquired/divested for partial/NCI deals. Added 2026-07-01
  -- per-figure currency (Phase-1 2026-07-01): 14 rows mix >=2 currencies across figures
  -- (357 Collins: AUD proceeds + SGD carrying). Each money figure carries its own currency;
  -- falls back to the row `currency` when the AR didn't tag the figure separately.
  purchase_price_currency text,
  gross_sale_price_currency text,
  net_sale_proceeds_currency text,
  carrying_value_currency text,
  gain_currency text,
  valuation_currency text,
  -- per-figure provenance text (Phase-1 2026-07-01): promoted from raw (carrying_value_basis on 62/95 rows)
  carrying_value_basis text,
  gain_on_divestment_basis text,
  net_proceeds_basis text,
  counterparty text,                               -- buyer/seller (Phase-B). Added 2026-06-23
  currency text,                                   -- row-level presentation currency (default for untagged figures)
  source_page int,
  raw jsonb not null default '{}'                 -- full ORIGINAL object (audit trail; loader resolves aliases into the typed cols above; *_local values kept here)
);
-- migrations (idempotent)
alter table sgx_reit_property_transaction add column if not exists transaction_date date;
alter table sgx_reit_property_transaction add column if not exists valuation numeric;
alter table sgx_reit_property_transaction add column if not exists counterparty text;
alter table sgx_reit_property_transaction add column if not exists status text;
-- Phase-1 un-conflation (2026-07-01): split gross vs net, per-figure currency, promote basis fields
alter table sgx_reit_property_transaction add column if not exists gross_sale_price numeric;
alter table sgx_reit_property_transaction add column if not exists net_sale_proceeds numeric;
alter table sgx_reit_property_transaction add column if not exists interest_pct numeric;
alter table sgx_reit_property_transaction add column if not exists purchase_price_currency text;
alter table sgx_reit_property_transaction add column if not exists gross_sale_price_currency text;
alter table sgx_reit_property_transaction add column if not exists net_sale_proceeds_currency text;
alter table sgx_reit_property_transaction add column if not exists carrying_value_currency text;
alter table sgx_reit_property_transaction add column if not exists gain_currency text;
alter table sgx_reit_property_transaction add column if not exists valuation_currency text;
alter table sgx_reit_property_transaction add column if not exists carrying_value_basis text;
alter table sgx_reit_property_transaction add column if not exists gain_on_divestment_basis text;
alter table sgx_reit_property_transaction add column if not exists net_proceeds_basis text;
-- old single money-in column superseded by gross_sale_price + net_sale_proceeds
alter table sgx_reit_property_transaction drop column if exists net_proceeds;

-- _notes.json -> own table (CONFIRMED 2026-06-19). One jsonb blob per (symbol, FY).
create table if not exists sgx_reit_notes (
  id uuid primary key default gen_random_uuid(),
  symbol text not null,
  financial_year int not null,
  notes jsonb not null default '{}',              -- {columns_never_fillable, data_with_no_home, parsing_traps, inferred, reconciliation, ...}
  unique (symbol, financial_year)
);

-- ---------------------------------------------------------------------------
-- INVENTORY + REVIEW TABLES (replace reviews/<stem>.json; one report = one cockpit unit)
-- ---------------------------------------------------------------------------

create table if not exists reit_report (
  id uuid primary key default gen_random_uuid(),
  symbol text not null,
  financial_year int not null,
  pdf_r2_key text,                                -- object key in the R2 bucket
  page_offset int not null default 0,             -- printed -> physical PDF page drift
  unique (symbol, financial_year)
);

create table if not exists reit_record_verdict (
  id uuid primary key default gen_random_uuid(),
  report_id uuid not null references reit_report(id) on delete cascade,
  table_name text not null,                       -- 'sgx_reit_property' | 'sgx_reit_performance' | ...
  record_pk text not null,                        -- the row id (or symbol for profile)
  verdict text check (verdict in ('correct','false','unsure')),
  note text,
  reviewer uuid references auth.users(id),
  updated_at timestamptz not null default now(),
  unique (report_id, table_name, record_pk, reviewer)
);

create table if not exists reit_field_edit (
  id uuid primary key default gen_random_uuid(),
  report_id uuid not null references reit_report(id) on delete cascade,
  table_name text not null,
  record_pk text not null,
  field_name text not null,
  suggested_value jsonb,                          -- the proposed correction; source tables untouched
  reviewer uuid references auth.users(id),
  updated_at timestamptz not null default now(),
  unique (report_id, table_name, record_pk, field_name, reviewer)
);

-- helpful indexes for the cockpit's per-(symbol,FY) reads
create index if not exists idx_property_sy on sgx_reit_property (symbol, financial_year);
create index if not exists idx_perf_sy     on sgx_reit_performance (symbol, financial_year);
create index if not exists idx_toptenant_sy on sgx_reit_top_tenant (symbol, financial_year);
create index if not exists idx_trademix_sy on sgx_reit_trade_mix (symbol, financial_year);
create index if not exists idx_fin_sy      on sgx_reit_financial (symbol, financial_year);
create index if not exists idx_txn_sy      on sgx_reit_property_transaction (symbol, financial_year);
create index if not exists idx_verdict_report on reit_record_verdict (report_id);
create index if not exists idx_edit_report    on reit_field_edit (report_id);

-- ---------------------------------------------------------------------------
-- RLS — data read-only to authed reviewers; verdict/edit writable only by their author.
-- (service key bypasses RLS, so the loader is unaffected.)
-- ---------------------------------------------------------------------------
do $$
declare t text;
begin
  foreach t in array array[
    'sgx_reit_profile','sgx_reit_performance','sgx_reit_property','sgx_reit_top_tenant',
    'sgx_reit_trade_mix','sgx_reit_financial','sgx_reit_property_transaction','sgx_reit_notes',
    'reit_report'
  ] loop
    execute format('alter table %I enable row level security', t);
    execute format('drop policy if exists %I on %I', t||'_read', t);
    execute format($f$create policy %I on %I for select to authenticated using (true)$f$,
                   t||'_read', t);
  end loop;
end $$;

alter table reit_record_verdict enable row level security;
alter table reit_field_edit     enable row level security;

drop policy if exists verdict_read  on reit_record_verdict;
drop policy if exists verdict_write on reit_record_verdict;
drop policy if exists edit_read     on reit_field_edit;
drop policy if exists edit_write    on reit_field_edit;

create policy verdict_read on reit_record_verdict for select to authenticated using (true);
create policy verdict_write on reit_record_verdict for all to authenticated
  using (reviewer = auth.uid()) with check (reviewer = auth.uid());
create policy edit_read on reit_field_edit for select to authenticated using (true);
create policy edit_write on reit_field_edit for all to authenticated
  using (reviewer = auth.uid()) with check (reviewer = auth.uid());
