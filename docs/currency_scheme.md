# Property-table currency scheme — current mapping + uniform target

_2026-07-02. Written because the per-figure currency handling in `sgx_reit_property` is inconsistent (two patterns). This documents the current mapping and the recommended uniform target so it can be executed as one migration. **Proofread layer = NO currency conversion**; every value is as-reported._

## Current mapping (the inconsistency)

Four monetary figures, two different currency mechanisms:

| Figure | Value column holds | Currency mechanism | Non-default rows |
|---|---|---|---|
| `market_valuation` | **presentation** ccy (mostly SGD) | row `currency` **+ paired local columns** `original_value` / `original_currency` | 184 have a local pair |
| `net_property_income` | **as-reported / local** | tag `net_property_income_currency` | 47 ≠ `currency` |
| `gross_revenue` | as-reported / local | tag `gross_revenue_currency` | 214 ≠ `currency` |
| `purchase_price` | as-reported / local | tag `purchase_price_currency` | 399 ≠ `currency` |

- `currency` (row): presentation ccy + default for untagged tags. Values: SGD 1235, EUR 157, GBP 148, USD 113.
- **Problem 1** — `market_valuation` uses a *second value column* for the local figure; the other three use a *tag* on the same column.
- **Problem 2** — within one foreign row the figures sit in different currencies: e.g. AU8U `purchase_price`=RMB but `market_valuation`=SGD (local RMB valuation hidden in `original_value`) → cost vs value not directly comparable.
- **Problem 3** — currency codes not normalized: `RMB` (purchase_price/original) vs `CNY` (npi) both used.

## Recommended uniform target — "as-reported local + per-figure tag" (Option A)

Every monetary figure = the value **as the per-property table reports it** (local for foreign assets) + a sibling `<figure>_currency` tag. `currency` stays as the row-level presentation default. SGD/base-ccy equivalents are re-derived later in the **prod layer** via FX (not here).

Target columns per figure: `market_valuation` + **`market_valuation_currency`** (NEW), `net_property_income` + `net_property_income_currency`, `gross_revenue` + `gross_revenue_currency`, `purchase_price` + `purchase_price_currency`.

**Migration steps:**
1. `ALTER TABLE sgx_reit_property ADD COLUMN market_valuation_currency text;`
2. Populate the tag:
   - Rows with `original_currency` set (184): `market_valuation_currency := original_currency`.
   - Else: `market_valuation_currency := currency`.
3. Make `market_valuation` as-reported/local (uniform with the other three):
   - For the 184 dual rows: `market_valuation := original_value` (the local figure).
   - Other rows already as-reported → unchanged.
4. `ALTER TABLE ... DROP COLUMN original_value, DROP COLUMN original_currency;` (SGD is re-derivable in prod).
5. Currency-code normalize (all `*_currency` in `sgx_reit_property` + `sgx_reit_property_transaction`): `RMB → CNY` (ISO 4217). Check also for other non-ISO codes.
6. Update `schema/models.py`: add `market_valuation_currency`, remove `original_currency`/`original_value`; regenerate `db/schema.sql`; update `scripts/db/load_supabase.py` (the load-time alias `local_currency`/`local_currency_value` → now feed `market_valuation`/`market_valuation_currency`).
7. Reload all 37 dirs; re-measure.

**Trade-off:** loses the audited SGD valuation on the 184 foreign rows (recoverable via FX in prod). If you'd rather KEEP the SGD figure, use the alternative below.

## Alternative — "keep SGD primary + add tag" (Option B, non-destructive)
Only steps 1–2 + 5–6 (skip step 3–4): add `market_valuation_currency` (= `original_currency` else `currency`) and RETAIN `original_value`/`original_currency` as the supplementary local pair. `market_valuation` stays presentation-ccy. Every figure now has a tag, but `market_valuation` remains a different basis from `purchase_price` on foreign rows. Fully reversible; preserves both numbers.

## Status
Not executed — awaiting decision (Option A vs B, and RMB→CNY yes/no). Default recommendation: **Option A + RMB→CNY**.
