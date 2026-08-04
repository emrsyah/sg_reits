-- PROD: drop distribution_period_months, and slim distribution_record to
-- dpu + period_start + period_end.
--
-- distribution_record is rebuilt by the promote, so the JSON needs no DDL -- run
-- promote_final_to_prod.py --tables sgx_reit_performance --write after this and the
-- old keys (line, amount, pay_date, source) are gone with it.

begin;

alter table sgx_reit_performance drop column if exists distribution_period_months;

commit;
