# Phase 3 · Stage B — Categorical value inventory

_Full unique-value listing for every categorical/enum column across the 8 `sgx_reit_*` tables (generated from the live DB). Free-text columns (names, addresses, `*_basis` prose, `category_raw`, `tenure_raw`) and continuous numerics are intentionally excluded._

## ⚠️ What needs checking (decisions for you)

These are the only columns with dirt / ambiguity. Everything below this section is already a clean enum unless listed here.

| # | Column(s) | Issue | Proposed fix |
|---|---|---|---|
| 1 | `property.country` | Duplicate spellings of the same country: `United States`×201 vs `USA`×11; `United Kingdom`×218 vs `The United Kingdom`×7; `The Netherlands`×21 vs `Netherlands`×6 | Collapse each pair to one canonical form (32 → 29 values) |
| 2 | `property.original_currency`, `property.purchase_price_currency`, `txn.valuation_currency` | Same currency under two codes: **`RMB`×70 vs `CNY`×8** | Pick one code (RMB **or** CNY) and normalise all |
| 3 | `top_tenant.pct_basis`, `trade_mix.pct_basis` | `'rental_income (corporate accounts of properties under Ascott management contracts only)'`×11 — a value with a parenthetical caveat baked in | Normalise to `rental_income`; move the caveat to a note/flag |
| 4 | `property.category` vs `profile.sub_sector` | Regional-spelling mismatch: category `Data Centers` vs sub_sector `Data Centre`; also check odd category `Diversified (Commercial)`×6 | Confirm intended spelling & whether `Diversified (Commercial)` is a real 6th category |
| 5 | `profile.income_model` | Value `fri`×1 is a cryptic abbreviation | Confirm meaning / expand label |
| 6 | `pct_basis` (both tables) | Many bases coexist (`gri`, `rental_income`, `gross_revenue`, `cash_rental_income`, `npi`, `committed_gross_rent`, `headline_rent`, `asset_value`) | Confirm this is an intended open vocabulary (not dirt), and that `gri` vs `gross_revenue` are meant to be distinct |

---

## Full inventory

### profile

**`sub_sector`** — 8 distinct

| value | count |
|---|---|
| Diversified | 11 |
| Industrial | 6 |
| Retail | 6 |
| Office | 5 |
| Hospitality | 4 |
| Data Centre | 2 |
| Healthcare | 2 |
| Specialized | 1 |

**`income_model`** — 6 distinct

| value | count |
|---|---|
| conventional | 25 |
| mixed | 7 |
| master_lease | 2 |
| entrusted_management | 1 |
| fri | 1 |
| management_contract | 1 |

### performance

**`currency`** — 4 distinct

| value | count |
|---|---|
| SGD | 28 |
| USD | 6 |
| EUR | 2 |
| GBP | 1 |

**`date`** — 4 distinct

| value | count |
|---|---|
| 2025-12-31 | 29 |
| 2025-03-31 | 4 |
| 2025-06-30 | 2 |
| 2025-09-30 | 2 |

**`distribution_basis`** — 4 distinct

| value | count |
|---|---|
| disclosed_after_retention | 20 |
| full_payout_no_retention_line | 9 |
| not_disclosed_rollforward_only | 6 |
| suspended | 2 |

### financial

**`currency`** — 4 distinct

| value | count |
|---|---|
| SGD | 28 |
| USD | 6 |
| EUR | 2 |
| GBP | 1 |

### property

**`country`** — 32 distinct

| value | count |
|---|---|
| Singapore | 396 |
| United Kingdom | 218 |
| United States | 201 |
| Japan | 172 |
| Australia | 169 |
| France | 89 |
| China | 82 |
| Germany | 63 |
| Indonesia | 47 |
| South Korea | 25 |
| Malaysia | 23 |
| India | 21 |
| The Netherlands | 21 |
| Italy | 19 |
| Vietnam | 18 |
| Denmark | 12 |
| USA | 11 |
| Hong Kong SAR | 10 |
| Finland | 9 |
| Czech Republic | 7 |
| The United Kingdom | 7 |
| Netherlands | 6 |
| Poland | 5 |
| Slovakia | 5 |
| Spain | 5 |
| Ireland | 3 |
| Belgium | 2 |
| Maldives | 2 |
| Philippines | 2 |
| Canada | 1 |
| New Zealand | 1 |
| Switzerland | 1 |

**`category`** — 6 distinct

| value | count |
|---|---|
| Industrial & Logistics | 674 |
| Specialized | 424 |
| Office | 278 |
| Retail | 153 |
| Data Centers | 118 |
| Diversified (Commercial) | 6 |

**`land_tenure`** — 2 distinct

| value | count |
|---|---|
| Freehold | 984 |
| Leasehold | 665 |

**`status`** — 3 distinct

| value | count |
|---|---|
| active | 1591 |
| divested | 50 |
| held_for_sale | 12 |

**`area_unit`** — 2 distinct

| value | count |
|---|---|
| sqm | 533 |
| sqft | 315 |

**`currency`** — 4 distinct

| value | count |
|---|---|
| SGD | 1235 |
| EUR | 157 |
| GBP | 148 |
| USD | 113 |

**`original_currency`** — 2 distinct

| value | count |
|---|---|
| IDR | 29 |
| RMB | 10 |

**`purchase_price_currency`** — 15 distinct

| value | count |
|---|---|
| SGD | 770 |
| EUR | 163 |
| GBP | 163 |
| USD | 124 |
| JPY | 113 |
| RMB | 59 |
| AUD | 36 |
| IDR | 29 |
| KRW | 22 |
| VND | 12 |
| HKD | 10 |
| MYR | 10 |
| CNY | 8 |
| INR | 3 |
| NZD | 1 |

**`valuation_date`** — 4 distinct

| value | count |
|---|---|
| 2025-12-31 | 1166 |
| 2025-03-31 | 327 |
| 2025-09-30 | 126 |
| 2025-06-30 | 14 |

### property_transaction

**`transaction_type`** — 5 distinct

| value | count |
|---|---|
| divestment | 58 |
| acquisition | 26 |
| announced_divestment | 9 |
| divestment_terminated | 1 |
| partial_divestment | 1 |

**`status`** — 3 distinct

| value | count |
|---|---|
| completed | 83 |
| announced | 11 |
| terminated | 1 |

**`currency`** — 5 distinct

| value | count |
|---|---|
| SGD | 41 |
| USD | 8 |
| EUR | 7 |
| GBP | 5 |
| AUD | 2 |

**`purchase_price_currency`** — 6 distinct

| value | count |
|---|---|
| SGD | 18 |
| USD | 3 |
| JPY | 2 |
| AUD | 1 |
| EUR | 1 |
| GBP | 1 |

**`gross_sale_price_currency`** — 5 distinct

| value | count |
|---|---|
| SGD | 38 |
| EUR | 6 |
| USD | 5 |
| GBP | 4 |
| AUD | 1 |

**`net_sale_proceeds_currency`** — 3 distinct

| value | count |
|---|---|
| SGD | 11 |
| USD | 3 |
| EUR | 1 |

**`carrying_value_currency`** — 4 distinct

| value | count |
|---|---|
| SGD | 33 |
| EUR | 6 |
| USD | 5 |
| GBP | 4 |

**`gain_currency`** — 3 distinct

| value | count |
|---|---|
| SGD | 9 |
| EUR | 2 |
| USD | 2 |

**`valuation_currency`** — 7 distinct

| value | count |
|---|---|
| SGD | 34 |
| EUR | 6 |
| GBP | 5 |
| USD | 4 |
| JPY | 3 |
| AUD | 1 |
| RMB | 1 |

### top_tenant

**`pct_basis`** — 8 distinct

| value | count |
|---|---|
| gri | 219 |
| rental_income | 64 |
| gross_revenue | 40 |
| cash_rental_income | 20 |
| rental_income (corporate accounts of properties under Ascott management contracts only) | 11 |
| committed_gross_rent | 10 |
| headline_rent | 10 |
| npi | 10 |

### trade_mix

**`category`** — 15 distinct

| value | count |
|---|---|
| Other Retail Trades | 74 |
| IT & Telecommunications | 38 |
| Financial & Professional Services | 34 |
| Other Industrial Trades | 31 |
| Healthcare & Wellness | 29 |
| Other Office Trades | 29 |
| Infrastructure, Real Estate & Property Services | 24 |
| Food & Beverages | 16 |
| Manufacturing | 16 |
| Hospitality & Leisure | 14 |
| Logistics & Supply Chain Management | 14 |
| Fashion & Accessories | 13 |
| Government Related | 13 |
| Departmental Store/Supermarket | 11 |
| Energy, Mining & Resources | 11 |

**`pct_basis`** — 8 distinct

| value | count |
|---|---|
| gri | 228 |
| rental_income | 56 |
| gross_revenue | 30 |
| cash_rental_income | 17 |
| headline_rent | 12 |
| committed_gross_rent | 11 |
| rental_income (corporate accounts of properties under Ascott management contracts only) | 11 |
| asset_value | 2 |

### jsonb categorical sub-fields

**`profile.management[].role`**

| value | count |
|---|---|
| property_manager | 57 |
| trustee | 41 |
| sponsor | 40 |
| reit_manager | 39 |
| operator | 22 |
| master_lessee | 10 |

**`financial.line_items[].statement`**

| value | count |
|---|---|
| expense | 287 |
| adjustment | 240 |
| revenue | 71 |

_`performance.flags` and `property.flags` are arrays of objects (edge-case markers), not a fixed vocabulary — not inventoried here._