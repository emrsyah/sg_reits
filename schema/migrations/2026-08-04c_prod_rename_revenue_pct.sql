-- PROD: sgx_reit_top_tenant.revenue_pct -> pct
--
-- Only 143 of 752 rows were a percentage of revenue; the rest are of
-- gross_rental_income, headline_rent, npi or annualised_rent. pct_basis already
-- states the denominator, and sgx_reit_trade_mix already calls the column pct.
--
-- A RENAME, not a drop -- the values are unchanged and stay 0-1.
--
-- Run this BEFORE the next promote. promote_final_to_prod.py only emits columns prod
-- already has, so without it revenue_pct would be nulled and pct dropped silently.
--
-- After:  python scripts/db/promote_final_to_prod.py --tables sgx_reit_top_tenant,sgx_reit_property_transaction --write

begin;

alter table sgx_reit_top_tenant rename column revenue_pct to pct;

commit;
