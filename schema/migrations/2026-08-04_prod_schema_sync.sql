-- PROD schema sync — brings prod in line with dev *_final after the 2026-07-30 schema review.
-- Decisions: docs/7-30-2026-schema-review/  ·  column-by-column: docs/7-30-2026-schema-review/prod-schema-changes.md
--
-- Run against PROD. promote_final_to_prod.py does DATA only — transform_row() emits
-- just the columns prod already has, so any column added in _final is dropped SILENTLY
-- until this migration runs.
--
-- ORDER MATTERS:
--   §1-§5  ADD the new columns          <- run BEFORE the promote
--   then   python scripts/db/promote_final_to_prod.py --write
--   §6     DROP the retired columns     <- run AFTER the promote is verified
--
-- Dropping before the promote would delete data that the promote has not yet replaced.
-- Every statement is IF EXISTS / IF NOT EXISTS, so the file is safe to re-run.


begin;

-- ------------------------------------------------------------------ §1 performance
-- Distribution flow restructured into a rollforward:
--   opening + income_for_year + other_additions - distribution_paid - amount_retained = closing
alter table sgx_reit_performance add column if not exists units_in_issue        numeric;
alter table sgx_reit_performance add column if not exists income_for_year       numeric;
alter table sgx_reit_performance add column if not exists distribution_declared numeric;
alter table sgx_reit_performance add column if not exists amount_retained       numeric;
alter table sgx_reit_performance add column if not exists other_additions       numeric;

comment on column sgx_reit_performance.units_in_issue is
  'Units in issue at FY end. Renamed from number_of_shareholder_units — same figure, '
  'verified identical. Distinct from number_of_unitholders, which counts HOLDERS.';
comment on column sgx_reit_performance.amount_retained is
  'Distributable income withheld from distribution rather than paid out.';
comment on column sgx_reit_performance.other_additions is
  'Additions to the distribution pool beyond income_for_year, split economically: '
  'operating sources vs asset sales.';

-- ------------------------------------------------------------------ §2 property
alter table sgx_reit_property add column if not exists coordinate_source text;

comment on column sgx_reit_property.coordinate_source is
  'Provenance of latitude/longitude, e.g. onemap.';

-- ------------------------------------------------------------------ §3 top_tenant / trade_mix
-- Supersedes §3 of 2026-08-03_basis_segment.sql (folded in here).
-- NULL = whole portfolio. Non-null means the percentages sum to ~100% WITHIN that
-- segment only — T82U discloses office and retail against separate denominators.
alter table sgx_reit_top_tenant add column if not exists basis_segment text;
alter table sgx_reit_trade_mix  add column if not exists basis_segment text;

alter table sgx_reit_top_tenant drop constraint if exists sgx_reit_top_tenant_basis_segment_chk;
alter table sgx_reit_top_tenant add  constraint sgx_reit_top_tenant_basis_segment_chk
  check (basis_segment is null or basis_segment in
         ('office','retail','commercial','logistics_industrial'));

alter table sgx_reit_trade_mix drop constraint if exists sgx_reit_trade_mix_basis_segment_chk;
alter table sgx_reit_trade_mix add  constraint sgx_reit_trade_mix_basis_segment_chk
  check (basis_segment is null or basis_segment in
         ('office','retail','commercial','logistics_industrial'));

-- basis_segment must join the trade_mix key, or T82U's office and retail rows for the
-- same category collide and aggregate_trade_mix() ADDS them (a ~200% trade mix).
-- NULLs never compare equal in a plain PK, so key on a coalesced expression.
drop index if exists sgx_reit_trade_mix_scope_uidx;
create unique index sgx_reit_trade_mix_scope_uidx on sgx_reit_trade_mix
  (symbol, financial_year, category, pct_basis, coalesce(basis_segment, ''));

-- ------------------------------------------------------------------ §4 property_transaction
-- v2: store the PRICE and the BASIS it is measured against; derive the gain.
alter table sgx_reit_property_transaction add column if not exists deal_id     text;
alter table sgx_reit_property_transaction add column if not exists basis_value numeric;
alter table sgx_reit_property_transaction add column if not exists basis       text;

alter table sgx_reit_property_transaction drop constraint if exists sgx_reit_property_transaction_basis_chk;
alter table sgx_reit_property_transaction add  constraint sgx_reit_property_transaction_basis_chk
  check (basis is null or basis in
         ('valuation','book_value','purchase_price','net_identifiable_assets'));

comment on column sgx_reit_property_transaction.deal_id is
  'Grouping key, set ONLY where rows share one price — multi-property aggregates and '
  'cross-year duplicates. NULL means this row stands alone. Counting properties: use '
  'rows. Counting money: group by deal_id first, or the same money is counted twice.';
comment on column sgx_reit_property_transaction.basis_value is
  'The figure sale_price is measured against, same currency and same interest as the '
  'price. gain = sale_price - basis_value.';
comment on column sgx_reit_property_transaction.basis is
  'What basis_value IS: valuation | book_value | purchase_price | net_identifiable_assets. '
  'Gains on different bases are not comparable.';

-- ------------------------------------------------------------------ §5 percentage convention
-- One convention database-wide: every percentage is 0-1. aggregate_leverage,
-- cost_of_debt and portfolio_occupancy were still 0-100; the promote now overwrites
-- them with 0-1 values. NOT percentages and unchanged: interest_coverage_ratio (a
-- multiple), WALE and debt maturity (years), DPU and NAV (money).
comment on column sgx_reit_performance.aggregate_leverage  is 'Fraction 0-1 (0.39 = 39%).';
comment on column sgx_reit_performance.cost_of_debt        is 'Fraction 0-1 (0.035 = 3.5%).';
comment on column sgx_reit_performance.portfolio_occupancy is 'Fraction 0-1 (0.909 = 90.9%).';

commit;


-- ================================================================== §6 DROPS
-- RUN ONLY AFTER promote_final_to_prod.py --write HAS COMPLETED AND BEEN VERIFIED.
-- These columns no longer exist in _final, so nothing will repopulate them.

-- begin;
--
-- -- performance: renamed or redefined by the distribution-flow restructure
-- alter table sgx_reit_performance drop column if exists number_of_shareholder_units;      -- -> units_in_issue
-- alter table sgx_reit_performance drop column if exists net_distributable_income;         -- -> income_for_year
-- alter table sgx_reit_performance drop column if exists distribution_cash_paid;           -- -> distribution_paid
-- alter table sgx_reit_performance drop column if exists adjusted_distributable_income;    -- dropped, not replaced
-- alter table sgx_reit_performance drop column if exists distribution_pool_other_movements;-- -> other_additions
--
-- -- property
-- alter table sgx_reit_property drop column if exists gross_lettable_area;  -- 9 values moved into net_lettable_area
-- alter table sgx_reit_property drop column if exists effective_date;       -- derived into lease_expiry_date first
--
-- -- property_transaction: v1 gain machinery, replaced by basis_value + basis
-- alter table sgx_reit_property_transaction drop column if exists carrying_value;
-- alter table sgx_reit_property_transaction drop column if exists valuation;
-- alter table sgx_reit_property_transaction drop column if exists valuation_date;
-- alter table sgx_reit_property_transaction drop column if exists gain_on_divestment;
-- alter table sgx_reit_property_transaction drop column if exists gain_basis;
-- alter table sgx_reit_property_transaction drop column if exists gain_loss_pct;   -- derive: (sale_price-basis_value)/basis_value
-- alter table sgx_reit_property_transaction drop column if exists net_sale_proceeds;
-- alter table sgx_reit_property_transaction drop column if exists announced_date;
-- alter table sgx_reit_property_transaction drop column if exists transaction_date;-- -> completed_date
-- alter table sgx_reit_property_transaction drop column if exists description;
--
-- commit;
