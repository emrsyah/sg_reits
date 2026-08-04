-- PROD: merge purchase_price + sale_price into transaction_price.
--
-- They are mutually exclusive by construction, verified on all 212 rows: 0 carry both,
-- 66 acquisitions have a purchase price, 135 divestments a sale price, 11 disclose no
-- price. transaction_type already states the direction, so two columns that can never
-- both be populated were a null-heavy way of repeating it.
--
-- Also ends a prod type inconsistency: purchase_price was `text` while sale_price and
-- every other money column is bigint. transaction_price is bigint.
--
-- Run BEFORE the next promote, then:
--   python scripts/db/promote_final_to_prod.py --tables sgx_reit_property_transaction --write

begin;

alter table sgx_reit_property_transaction add column if not exists transaction_price bigint;

-- carry existing values over so the column is never briefly empty; the promote
-- overwrites it immediately afterwards anyway.
update sgx_reit_property_transaction
   set transaction_price = coalesce(nullif(purchase_price,'')::numeric::bigint, sale_price)
 where transaction_price is null;

alter table sgx_reit_property_transaction drop column if exists purchase_price;
alter table sgx_reit_property_transaction drop column if exists sale_price;

commit;
