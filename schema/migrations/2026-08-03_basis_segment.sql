-- sgx_reit_top_tenant / sgx_reit_trade_mix — add basis_segment
-- Decisions: docs/7-30-2026-schema-review/meeting-recap-tracker.md (Q4, 2026-08-03)
-- Evidence:  docs/7-30-2026-schema-review/pct_basis-verification.md §1
--
-- WHY THIS COLUMN EXISTS
-- pct_basis is being capped at 6 canonical values. Four of the values it replaces
-- (office_gri, retail_gri, gri_commercial, gri_logistics_industrial — T82U and BUOU)
-- are NOT the same denominator as whole-portfolio GRI: each segment's percentages sum
-- to ~100% WITHIN that segment. T82U FY2025 L1009-1011:
--     "the top 10 tenants of the office portfolio contributed 20.0% of Suntec REIT's
--      total office gross rental income ... For the retail portfolio ... 15.0% of
--      ... total gross retail income"
-- Folding both into a bare gross_rental_income makes one tenant list appear to sum to
-- 200%. Worse: pct_basis is part of the PROD PK, so promote_final_to_prod.py's
-- aggregate_trade_mix() would literally ADD the two segments' percentages into one row.
-- basis_segment therefore has to be part of the prod PK too — see §3 below.
--
-- NULL = whole-portfolio (the overwhelming majority).
--
-- Run against DEV (SUPABASE_CONNECTION_STRING). *_final is dropped and recreated by
-- build_final_tables.py, so it needs no DDL here — only the raw tables do.
--
-- Safe to re-run: every statement is IF EXISTS / IF NOT EXISTS.

begin;

-- ------------------------------------------------------------------ §1 raw tables
alter table sgx_reit_top_tenant add column if not exists basis_segment text;
alter table sgx_reit_trade_mix  add column if not exists basis_segment text;

comment on column sgx_reit_top_tenant.basis_segment is
  'Portfolio segment the pct_basis denominator is scoped to: office | retail | '
  'commercial | logistics_industrial. NULL = whole portfolio. Non-null means the '
  'percentages sum to ~100% within this segment only and are NOT comparable with '
  'whole-portfolio figures.';
comment on column sgx_reit_trade_mix.basis_segment is
  'Portfolio segment the pct_basis denominator is scoped to: office | retail | '
  'commercial | logistics_industrial. NULL = whole portfolio. Non-null means the '
  'percentages sum to ~100% within this segment only and are NOT comparable with '
  'whole-portfolio figures.';

-- ------------------------------------------------------------------ §2 value guard
-- Keep the vocabulary closed. A typo'd segment silently splits a denominator.
alter table sgx_reit_top_tenant drop constraint if exists sgx_reit_top_tenant_basis_segment_chk;
alter table sgx_reit_top_tenant add  constraint sgx_reit_top_tenant_basis_segment_chk
  check (basis_segment is null or basis_segment in
         ('office','retail','commercial','logistics_industrial'));

alter table sgx_reit_trade_mix drop constraint if exists sgx_reit_trade_mix_basis_segment_chk;
alter table sgx_reit_trade_mix add  constraint sgx_reit_trade_mix_basis_segment_chk
  check (basis_segment is null or basis_segment in
         ('office','retail','commercial','logistics_industrial'));

commit;

-- ------------------------------------------------------------------ §3 PROD — NOT YET RUN
-- The prod sgx_reit_trade_mix PK is (symbol, financial_year, category, pct_basis).
-- basis_segment MUST join it before the remap is promoted, or T82U's office and retail
-- rows for the same category collide and aggregate_trade_mix() sums them.
-- NULLs do not compare equal in a normal PK, so use a unique index on a coalesced
-- expression rather than adding a nullable column to the PK.
--
-- Run separately against PROD, after the dev remap is applied and verified:
--
--   alter table sgx_reit_trade_mix  add column if not exists basis_segment text;
--   alter table sgx_reit_top_tenant add column if not exists basis_segment text;
--
--   drop index if exists sgx_reit_trade_mix_scope_uidx;
--   create unique index sgx_reit_trade_mix_scope_uidx on sgx_reit_trade_mix
--     (symbol, financial_year, category, pct_basis, coalesce(basis_segment, ''));
--
-- promote_final_to_prod.py:227 aggregate_trade_mix() must add basis_segment to its
-- grouping key `k` in the same change, otherwise it aggregates before the index ever
-- sees the rows.
