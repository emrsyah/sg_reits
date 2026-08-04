-- sgx_reit_performance — distribution-flow restructure
-- Decisions: docs/7-30-2026-schema-review/performance-target-schema-AGREED.md
-- Data:      fixes/perf_reextract/_final.json  (74 rows, gates 63/63 and 41/45)
--
-- Run against DEV (SUPABASE_CONNECTION_STRING). Prod is rebuilt from
-- sgx_reit_performance_final by promote_final_to_prod.py — do NOT alter prod by hand.
--
-- Safe to re-run: every statement is IF EXISTS / IF NOT EXISTS.

begin;

-- ---------------------------------------------------------------- renames
-- "Amount available for distribution" in an AR is opening+income and is the
-- single most common extraction trap. income_for_year says what it is.
alter table sgx_reit_performance rename column net_distributable_income to income_for_year;

-- These two swap roles deliberately. Today the SHORTER name holds the DECLARED
-- figure and the longer one holds cash — backwards, and the direct cause of the
-- AJBU/C2PU/BUOU/T82U defects. Two steps so the names never collide.
alter table sgx_reit_performance rename column distribution_paid      to distribution_declared;
alter table sgx_reit_performance rename column distribution_cash_paid to distribution_paid;

-- "shareholder units" is not REIT vocabulary; SGX says units in issue.
alter table sgx_reit_performance rename column number_of_shareholder_units to units_in_issue;

-- ---------------------------------------------------------------- split
-- distribution_pool_other_movements carried two directions in one signed column:
-- 17 rows negative (retained), 7 positive (added), and J85 netted BOTH into one
-- figure. Split so a retention is never cancelled out by a capital distribution.
alter table sgx_reit_performance add column if not exists amount_retained numeric;
alter table sgx_reit_performance add column if not exists other_additions numeric;
alter table sgx_reit_performance add column if not exists other_additions_label text;

-- ---------------------------------------------------------------- dev-only
-- Part of distribution_paid is settled in UNITS via a Distribution Reinvestment
-- Plan, not cash (C38U FY2024: S$115.5m of S$874.1m). Drives no metric, so it
-- stays in dev as an audit trail and is NOT promoted. It is the only check that
-- reconciles to a second audited statement:
--   distribution_paid − paid_in_units = the cash flow statement's distribution line
--   ME8U  385,455 − 29,754 = 355,701   exact
--   JYEU   85,556 − 13,453 =  72,103   exact
alter table sgx_reit_performance add column if not exists paid_in_units numeric;

-- Five rows print income_for_year NET of a retention deducted inside the build-up
-- (TS0U x2, C2PU x2, P40U). The retention is added back so the column is uniformly
-- pre-retention; this flag marks which values are computed rather than printed.
alter table sgx_reit_performance add column if not exists income_for_year_basis text
  default 'pre_retention_as_printed';

-- The AR's own stated year end. 6 REITs are not December (ME8U/M44U/N2IU/O5RU
-- 31 Mar, J69U/BUOU 30 Sep, P40U/JYEU 30 Jun) and `date` alone has been misread.
alter table sgx_reit_performance add column if not exists fy_end_date date;

-- ---------------------------------------------------------------- drop
-- 4% fill (3 of 74) and NOT_FOUND in all six ARs checked. No REIT publishes a
-- second distributable-income figure; the 3 populated rows contradict each other.
alter table sgx_reit_performance drop column if exists adjusted_distributable_income;

commit;

-- ---------------------------------------------------------------- NOT dropped
-- distribution_pool_other_movements is deliberately LEFT IN PLACE until
-- amount_retained / other_additions are loaded and verified. Drop it only after:
--   select count(*) from sgx_reit_performance
--    where distribution_pool_other_movements is not null
--      and amount_retained is null and other_additions is null;   -- must be 0
--
-- alter table sgx_reit_performance drop column distribution_pool_other_movements;
--
-- units_to_be_issued is KEPT (decision reversed 2026-08-03). With units_in_issue
-- standardised to issued-only it stops double-counting and becomes the component
-- that makes both unit bases derivable:
--   issued_only         = units_in_issue
--   issued_and_issuable = units_in_issue + units_to_be_issued

-- ============================================================================
-- PROD (SUPABASE_URL / SUPABASE_KEY)
-- ============================================================================
-- promote_final_to_prod.py DELETEs then POSTs rows via PostgREST, so the prod
-- table must already have these columns or every insert 400s.
--
-- Run this on prod BEFORE the first promote after this migration.
-- Prod is NOT rebuilt from scratch — it is rewritten per scope — so the renames
-- must be applied here too, not just in dev.

begin;

alter table sgx_reit_performance rename column net_distributable_income to income_for_year;
alter table sgx_reit_performance rename column distribution_paid      to distribution_declared;
alter table sgx_reit_performance rename column distribution_cash_paid to distribution_paid;
alter table sgx_reit_performance rename column number_of_shareholder_units to units_in_issue;

alter table sgx_reit_performance add column if not exists amount_retained numeric;
alter table sgx_reit_performance add column if not exists other_additions numeric;

alter table sgx_reit_performance drop column if exists adjusted_distributable_income;

-- NOT added to prod (dev-only, see the AGREED doc):
--   paid_in_units, income_for_year_basis, other_additions_label, fy_end_date
-- NOT dropped yet: distribution_pool_other_movements — drop only after the split
-- columns are populated and verified, same check as the dev section above.

commit;

-- ---------------------------------------------------------------- afterwards
-- 1. Load fixes/perf_reextract/_final.json into dev sgx_reit_performance
-- 2. python scripts/db/build_final_tables.py          (P0 round(x,6) now applied)
-- 3. Re-run the gates against sgx_reit_performance_final:
--      rollforward   opening + income_for_year + other_additions
--                      − amount_retained − distribution_paid = closing
--                    expect 63/63, tolerance 0.1%
--      declared      distribution_declared
--                      = income_for_year + other_additions − amount_retained
--                    expect 41/45 at 1%; the 4 failures are M1GU x2, ME8U, P40U
--                    and each has a recorded reason
--      tranches      sum(distribution_record.dpu) = distribution_per_unit
--                    expect 63/69; A17U x2, DCRU x2, XZL x2 are structural
-- 4. python scripts/db/promote_final_to_prod.py --write

-- ---------------------------------------------------------------- addendum 2026-08-03
-- other_additions was redefined from POSITIONAL (above/below the AR's subtotal) to
-- ECONOMIC (rent vs money from selling assets). The breakdown is what makes that
-- answerable -- "how much of this payout came from asset sales" needs the line items,
-- not just a total. It was missed in the first cut of this migration.
alter table sgx_reit_performance add column if not exists other_additions_breakdown jsonb;

-- a label with no value is an orphan; clear it
update sgx_reit_performance set other_additions_label = null
 where other_additions is null and other_additions_label is not null;
