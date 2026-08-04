-- PROD schema sync — 2026-07-30 schema review.
-- Column-by-column detail: docs/7-30-2026-schema-review/prod-schema-changes.md
--
-- ORDER MATTERS:
--   §1-§3  add            <- run BEFORE the promote
--   then   python scripts/db/promote_final_to_prod.py --write
--   §5     drop           <- run AFTER the promote is verified
--
-- promote_final_to_prod.py does DATA only, and only for columns prod already has, so a
-- new column is dropped silently until §1-§3 run. Dropping before the promote would
-- delete data the promote has not yet replaced.
--
-- Types follow prod's convention: money and counts bigint, percentages double precision
-- /real, areas real, dates date. Safe to re-run.

begin;

-- §1 performance
alter table sgx_reit_performance add column if not exists units_in_issue        bigint;
alter table sgx_reit_performance add column if not exists income_for_year       bigint;
alter table sgx_reit_performance add column if not exists distribution_declared bigint;
alter table sgx_reit_performance add column if not exists amount_retained       bigint;
alter table sgx_reit_performance add column if not exists other_additions       bigint;

-- §2 top_tenant / trade_mix
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

-- basis_segment must join the key: T82U discloses office and retail against separate
-- denominators, so without it the two collide on one key and their percentages are
-- summed into a ~200% trade mix. NULLs never compare equal in a plain PK, hence coalesce.
drop index if exists sgx_reit_trade_mix_scope_uidx;
create unique index sgx_reit_trade_mix_scope_uidx on sgx_reit_trade_mix
  (symbol, financial_year, category, pct_basis, coalesce(basis_segment, ''));

-- §3 property_transaction
alter table sgx_reit_property_transaction add column if not exists deal_id     text;
alter table sgx_reit_property_transaction add column if not exists basis_value bigint;
alter table sgx_reit_property_transaction add column if not exists basis       text;

alter table sgx_reit_property_transaction drop constraint if exists sgx_reit_property_transaction_basis_chk;
alter table sgx_reit_property_transaction add  constraint sgx_reit_property_transaction_basis_chk
  check (basis is null or basis in
         ('valuation','book_value','purchase_price','net_identifiable_assets'));

commit;

-- §4 pre-existing inconsistency, unrelated to this review: purchase_price is text while
-- every other money column is bigint. The promote serializes it as a string to match.
-- Aligning it is a separate decision:
--
--   alter table sgx_reit_property_transaction
--     alter column purchase_price type bigint using nullif(purchase_price,'')::numeric::bigint;


-- ================================================================== §5 DROPS
-- RUN ONLY AFTER promote_final_to_prod.py --write HAS COMPLETED AND BEEN VERIFIED.
-- These columns are gone from _final, so nothing will repopulate them.

-- begin;
--
-- alter table sgx_reit_performance drop column if exists number_of_shareholder_units;      -- -> units_in_issue
-- alter table sgx_reit_performance drop column if exists net_distributable_income;         -- -> income_for_year
-- alter table sgx_reit_performance drop column if exists distribution_cash_paid;           -- -> distribution_paid
-- alter table sgx_reit_performance drop column if exists distribution_pool_other_movements;-- -> other_additions
-- alter table sgx_reit_performance drop column if exists adjusted_distributable_income;    -- dropped, not replaced
--
-- alter table sgx_reit_property drop column if exists gross_lettable_area;  -- 9 values moved into net_lettable_area
-- alter table sgx_reit_property drop column if exists effective_date;       -- derived into lease_expiry_date first
--
-- alter table sgx_reit_property_transaction drop column if exists carrying_value;     -- -> basis_value + basis
-- alter table sgx_reit_property_transaction drop column if exists valuation;          -- -> basis_value + basis
-- alter table sgx_reit_property_transaction drop column if exists valuation_date;
-- alter table sgx_reit_property_transaction drop column if exists gain_on_divestment; -- derive: sale_price - basis_value
-- alter table sgx_reit_property_transaction drop column if exists gain_basis;         -- -> basis
-- alter table sgx_reit_property_transaction drop column if exists gain_loss_pct;      -- derive: gain / basis_value
-- alter table sgx_reit_property_transaction drop column if exists net_sale_proceeds;  -- -> sale_price
-- alter table sgx_reit_property_transaction drop column if exists announced_date;
-- alter table sgx_reit_property_transaction drop column if exists transaction_date;   -- -> completed_date
-- alter table sgx_reit_property_transaction drop column if exists description;
--
-- commit;
