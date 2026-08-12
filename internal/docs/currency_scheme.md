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

## Wave 9 execution plan (2026-07-03 — re-measured against live DB)

**Re-measurement overturns the handoff's premise.** The handoff expected a large fill campaign ("100s of foreign rows storing converted SGD without a currency tag"). Live census shows currency tags are **already ~100% present**:

| Table / figure | value non-null | currency-tag MISSING | date field |
|---|---|---|---|
| property `market_valuation` | 1600/1653 | 0 (via `currency`; 184 have `original_currency` local pair) | `valuation_date` 1633/1653 |
| property `purchase_price` | 1551/1653 | 0 (all tagged `purchase_price_currency`) | none (no per-property acquisition date) |
| property `net_property_income` | 192 | 0 | FY period |
| property `gross_revenue` | 1532 | 0 | FY period |
| txn `gain_on_divestment` | 28 | **3** (loader bug) | `transaction_date` |
| txn `valuation` | 74 | **2** (loader bug) | `transaction_date` |
| txn `carrying_value` | 64 | **2** (M44U no ccy) | `transaction_date` |
| txn (any money) | — | — | `transaction_date` 92/95 (**3** missing) |
| performance / financial | 37/37 | 0 (single presentation ccy) | `date` 37/37 |

So Wave 9 is **NOT** a fill wave — it is a small structural migration + ~5 source-cited row fixes. `performance` and `financial` are single-currency-per-REIT with a `date` and need **no work**. Scope = `sgx_reit_property` + `sgx_reit_property_transaction` only.

### A. Structural / deterministic (main-agent, NO source re-verification, NO fan-out)
1. **Fix loader currency-tag bug** (`load_supabase.py` lines 121–122): the per-figure currency guards use a NARROWER alias set than the value resolution (lines 111–114). A `gain_on_divestment` resolved from `gain_loss`/`gain_on_disposal`, or a `valuation` from `gross_valuation_usd`, gets a value but **no** currency tag. Fix: apply `ccy(...)` whenever the *resolved value* is non-null (not gated on the 2-alias re-lookup). Auto-fills on reload: gain ccy = SGD for AJBU Kelsterbach / AW9U Imperial Aryaduta / C2PU MOB; valuation ccy = USD for BTOU Plaza / Peachtree. **5 rows, zero source work.**
2. **Add `market_valuation_currency` column** (Problem-1): populate `= original_currency` (the 184 foreign rows) else `= currency`. Gives `market_valuation` an explicit per-figure tag matching the other three figures. Touch `schema/models.py`, `db/schema.sql`, `load_supabase.py`.
3. **Surface historic-cost local pair for `purchase_price`** (Problem-2, cost side): loader currently ignores `purchase_price_local` / `purchase_price_local_currency`. Only **CY6U** carries populated values (18 India rows: SGD cost stored, as-reported **INR** cost dropped, e.g. ITPB 13,670,000,000 INR); AJBU's are null. Add columns `purchase_price_local` + `purchase_price_local_currency` (mirror of `original_value`/`original_currency`). This is the cost-side analog of the valuation local pair.
4. **RMB → CNY normalization** (Problem-3, ISO 4217): `RMB` is not an ISO code; renminbi = `CNY`. Affects property `purchase_price_currency` (59: AU8U, M44U), `original_currency` (27: AU8U, BMOU, CRPU), npi/gr ccy (5), txn (1). Deterministic string rewrite — **VALUE unchanged**, only the code label. Do it at the loader (normalize on write) so re-extraction stays as-reported in the JSON, and note it. (Spot-verify one AR wrote "RMB"/"¥".)

### B. Source-cited gaps (SMALL — main-agent, no fan-out)
5. **M44U `carrying_value_currency`** — Chee Wah + Subang 1 divestments have NO currency in JSON (row `currency` null); the other 15 M44U txns are all `SGD`. Verify the divestment note page → set `SGD`.
### C. Decision — LOCKED 2026-07-03 (user)
- **market_valuation + purchase_price local surfacing → Option B (non-destructive).** Keep the REIT's presentation value as primary; ADD `market_valuation_currency` (A2) + retain/surface the local pair (A3: `original_value`/`original_currency` for valuation, new `purchase_price_local`/`purchase_price_local_currency` for cost). The date-keyed FX reads the local pair (+ `valuation_date`) when present, else the presentation value is already local. Non-destructive, reversible, loses nothing. (Option A rejected: drops the REIT's audited SGD and historic local cost lacks a per-property acquisition date to FX against.)
- **RMB → CNY normalization → YES.** 92 non-ISO `RMB` cells rewritten to ISO 4217 `CNY` (matching the 8 already `CNY`); VALUE unchanged. Spot-verify one AR wrote "RMB"/"¥"; document.

### D. Verify → reload → confirm (per program rules)
QC-gate edited dirs in-process; reload changed dirs; main-agent re-query the DB to confirm every change landed AND re-read each cited `full.md` page before reload; then re-run the census in this doc's table and append a "## Wave 9 results" section + memory update. **Never convert, derive, or invent.**

### Not in scope / known limitations
- `performance` + `financial`: single presentation currency + `date` already present → untouched.
- `purchase_price` (property) has no per-property acquisition-date column and ARs rarely disclose one → historic-cost FX date is a structural gap, documented not filled.
- txn `valuation` figure's own `valuation_date` (M44U has 10 in JSON, unread; the table has only `transaction_date`) — optional future column; the deal `transaction_date` already anchors each row.

## Wave 9 results — EXECUTED & VERIFIED 2026-07-03

All changes applied to Supabase (37 dirs reloaded, "committed 37 report(s)") and re-queried live to confirm they landed. Row counts intact: property 1653, txn 95.

**Schema (Option B, non-destructive):** added `sgx_reit_property.market_valuation_currency`, `.purchase_price_local`, `.purchase_price_local_currency` (DB + `db/schema.sql` migrations + `schema/models.py` Property). No column dropped; the REIT's presentation values and audited SGD are all retained.

**Loader (`scripts/db/load_supabase.py`):**
- `_ccy()` normalizer (`RMB → CNY`) applied to every currency output in `txn_row` + the property builder. VALUES unchanged; JSON stays as-reported ("RMB"), DB stores ISO `CNY`.
- Fixed the currency-tag guard bug: per-figure tags now key off the *resolved* money value, not a narrower re-lookup. Auto-tagged AJBU/AW9U/C2PU gain=SGD, BTOU Plaza/Peachtree valuation=USD.
- `_first_date()` helper: `transaction_date` now takes the first *valid* alias, so a malformed early alias (TS0U `completion_date="2026-03"`) no longer shadows a valid later one (`announcement_date`).
- Property builder: `market_valuation_currency` = local (`original_currency`/`local_currency`, foreign) else `currency`; surfaces `purchase_price_local`/`_currency` (previously unread).

**Verified landed:**
| Check | Result |
|---|---|
| RMB remaining (property + txn) | **0** (was 92 property cells + 1 txn) → all `CNY` |
| `market_valuation_currency` coverage | **1600/1600** (SGD 1008, GBP 189, USD 158, EUR 156, AUD 33, IDR 29, CNY 27) |
| `purchase_price_local` populated | **29** (AJBU 17 AUD/CNY, CY6U 12 INR) — exact match to source JSON; `purchase_price` stays presentation SGD |
| txn currency-tag gaps (gain/valuation/carrying) | **0 missing** (was 7) |
| TS0U Salesforce Tower `transaction_date` | **2026-02-24** (agreement date, status `announced`; source p175 "On 24 February 2026 … entered into a … sale agreement") |
| M44U Chee Wah / Subang 1 `carrying_value_currency` | **SGD** (basis quotes S$6,618k / S$9,265k, FY2023 AR p190) |

**Source-cited structural nulls left null (noted in `_notes.json` key `currency_scheme_wave9_2026_07_03`):**
- P40U Wisma Atria (Office) strata divestment — "divested during the current period" (multi-unit sale across FY2024/25, no single completion date). p141.
- T82U Suntec City Office strata divestment — "$15.4m … divested at an average [price]" (averaged multi-unit sale, no single date). p22.
These are the only 2 txn rows with money but no `transaction_date` and are correct as null (not gaps).

**Net:** currency scheme is now uniform (every monetary figure carries an explicit ISO currency tag; foreign valuation + cost each have an as-reported local sibling; the deal/valuation date anchors the FX lookup). No conversion, derivation, or invention performed.
