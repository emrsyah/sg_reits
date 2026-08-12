# Phase 3 · Null checking — fill/null by column (regenerated live)

_Regenerated from Supabase **2026-07-02**, after null-recovery rounds 2–5. Supersedes the earlier Stage-A/C snapshot (which pre-dated the recovery work — e.g. it showed `net_property_income` 114 filled and a missing M44U risk block; both are now resolved)._

## TL;DR — where the nulls still are, and why

After rounds 2–5, **every remaining high-null column has been source-verified** as one of: (a) structural non-disclosure, (b) by-design conditional (field only applies to a subset of rows), or (c) data that lives in a dedicated table. There is **no known extraction miss left** — the recoverable per-property tables that were being skipped (ME8U/J85 areas & occupancy, M44U NLA, D5IU ownership, category_raw, txn descriptions) have all been recovered.

### Still heavily null — but VERIFIED structural / by-design (not gaps)
| Column | Null | Why (verified) |
|---|---|---|
| `property.net_property_income` (+`_currency`) | 88% | Disclosed only at business/geographic **segment** level across the corpus (A17U, M44U, MXNU, C2PU, SET, BUOU, O5RU, UD1U … all confirmed segment-only). Per-property NPI genuinely does not exist. |
| `property.npi_pct` | 94% | Derivable only where per-property NPI exists (it mostly doesn't); JVs excluded by design. |
| `property.gfa` | 63% | US-office / logistics / DC REITs disclose only **NLA** (net/rentable area), never GFA — confirmed by full-text checks + area-total reconciliation. Not copied from NLA. |
| `property.lease_term_years` / `lease_expiry_date` | 62% / 73% | Freehold-heavy portfolios (US, AU, EU) — freehold assets have no land-lease term by nature; combined/dual-tenure rows unsplittable. |
| `property.effective_date` | 96% | Land-lease start date rarely disclosed per property. |
| `property.original_currency` / `original_value` | 89% | Audit-trail fields — only populated where a foreign local figure needed capturing. |
| `property.area_unit` | 32% | Only set where an area exists in a non-default unit. |
| `financial.employee_breakdown` | 78% | Externally-managed REITs have no trust-level staff — structural. |
| `performance.adjusted_distributable_income` | 97% | Method-2-only field; 1 real value (M1GU) → **Phase-4 DROP candidate**. |
| `property_transaction.*` (gain, net_proceeds, purchase_price, interest_pct, `*_basis`, `*_currency`) | 30–97% | **By-design conditional**: acquisition fields are null on divestment rows and vice-versa; `interest_pct` only on partial/NCI deals; basis/currency families only where the figure needs them. |

### Lives in a dedicated table (null-on-property by design)
- `property.major_tenants` → `sgx_reit_top_tenant`; `property.gla` (99%) → superseded by `nla`/`gfa`.
- Removed from the property schema after verification: `trade_mix` lives in `sgx_reit_trade_mix`; sale/divestment prices live in `sgx_reit_property_transaction`; property lifecycle stays in `status` (`active` / `divested` / `held_for_sale`).

### Verified source-side non-disclosures (small residual)
- `property.ownership` (14%) — A17U (223, no per-property % column) + D5IU handled; remainder JV/segment.
- `property_transaction.counterparty` (17%, 16 rows) — every one printed as "an unrelated third party" with **no name** (M44U, ODBU, O5RU, TS0U, 8C8U, ME8U, CY6U, UD1U, P40U).
- `top_tenant.industry` (9%, 36 rows) — SET/M1GU/BTOU top-tenant tables have **no per-tenant sector column**; sectors exist only in the aggregate `trade_mix`.
- **`top_tenant.client_name`** — **BUOU rank 13 is NULL** and **N2IU rank 4 = "(Undisclosed tenant)"**: the reports literally withhold the tenant name (BUOU prints "Undisclosed"). ⚠️ This is the "null name" you spotted — it is a genuine source non-disclosure, not an extraction error. `property.property_name` is **100% populated** (0 null/empty/placeholder in 1,653 rows).

### Genuinely recoverable-but-still-open (small)
- `property_transaction` per-figure `carrying_value` / `valuation` / `gross_sale_price` nulls — some are on rows where the report gives only sale price or only valuation; a Tier-1 per-figure pass could chase the rest.
- `property.purchase_price` (6%, ~102 rows) — remaining are IPO-aggregate (XZL), fair-value-model (CRPU), or multi-stage/blended (Westgate, CapitaSpring) — mostly genuine absences.

---

## Stage A — full fill/null by column (live 2026-07-03, post-Wave-10)

_`real` = genuinely-fillable missing values (source prints it but DB is null). After Wave 10, **every table's real residual is 0** — all remaining nulls are structural (row-condition), by-design conditional, source-confirmed absent, or live in a dedicated table. `(+_currency)`/`(+_basis)` rows share the base column's count. New columns since the 2026-07-02 snapshot are tagged **[W9]** (Wave-9 currency scheme)._

### profile — 37 rows
| column | fill | null % | real |
|---|---|---|---|
| symbol / sub_sector / management / income_model / source_page | 37/37 | 0% | 0 |

### performance — 37 rows
| column | fill | null % | real | note |
|---|---|---|---|---|
| portfolio_value, gross_revenue, net_property_income, net_distributable_income, dpu | 37/37 | 0% | 0 | |
| distribution_record, distribution_paid, distribution_basis | 37/37 | 0% | 0 | |
| aggregate_leverage, interest_coverage_ratio, cost_of_debt, nav_per_unit | 37/37 | 0% | 0 | |
| number_of_unitholders, currency, date, properties_location, flags, source_page | 37/37 | 0% | 0 | |
| portfolio_occupancy | 35/37 | 5% | 0 | segment-only (Q5T hotels/SR, 8C8U PBWA/PBSA — no blend) |
| weighted_avg_debt_maturity | 34/37 | 8% | 0 | AW9U/T82U/CY6U = debt-maturity **chart only**, no scalar years |
| wale | 33/37 | 11% | 0 | HMN/Q5T/T82U/CY6U = hotel-subset/segment-only, no portfolio blend |
| adjusted_distributable_income | 1/37 | 97% | 0 | method-2-only; 1 real (M1GU) → **drop candidate** |

### financial — 37 rows
| column | fill | null % | real | note |
|---|---|---|---|---|
| income_stmt_metrics / balance_sheet_metrics / cash_flow_metrics / line_items | 37/37 | 0% | 0 | `balance_sheet_metrics` canonical **8-key** schema 37/37 complete (ME8U's 6 extra keys are optional, not nulls); `income_stmt_metrics.funds_from_operation` sub-key null 37/37 = FFO (US convention) not reported by SGX REITs |
| employee_breakdown | 8/37 | 78% | 0 | externally-managed REITs = structural |

### property — 1,653 rows
| column | fill | null % | real | note |
|---|---|---|---|---|
| property_name, country, category, address, currency, status, source_page, flags, major_tenants | 1653/1653 | 0% | 0 | `major_tenants` = empty array; data → top_tenant table |
| category_raw | 1651/1653 | 0.1% | 0 | BTOU Plaza/Peachtree (divested US offices) |
| land_tenure / tenure_raw | 1651/1653 | 0.1% | 0 | HMN Somerset (divested) + JYEU Parkway (JV interest); **N2IU Pinnacle Gangnam filled W10** |
| valuation_date | 1633/1653 | 1.2% | 0 | divested |
| market_valuation (+_currency **[W9]**) | 1600/1653 | 3.2% | 0 | divested 49 + HMN 4 "Not applicable" |
| purchase_price (+_currency) | 1551/1653 | 6.2% | 0 | whole-symbol no historic cost / prior-yr / IPO-seed |
| gross_revenue (+_currency) | 1532/1653 | 7.3% | 0 | whole-symbol segment-only |
| occupancy_rate | 1468/1653 | 11.2% | 0 | hotels report RevPAR |
| ownership | 1420/1653 | 14.1% | 0 | A17U 232 = whole-symbol (no per-property %); +2 HMN filled W11 |
| nla | 1210/1653 | 26.8% | 0 | hotels (keys) / GFA-REITs whole-symbol |
| area_unit | 1117/1653 | 32.4% | 0 | only set where an area exists |
| lease_term_years | 630/1653 | 61.9% | 0 | freehold + date-only (D5IU) + perpetual (SET) |
| gfa | 619/1653 | 62.6% | 0 | NLA-only REITs; +3 filled W11 (HMN×2, N2IU FJM); **8C8U 14 gfa values are mislabeled Land Area — DQ, unfixed** |
| lease_expiry_date | 447/1653 | 73.0% | 0 | freehold + leasehold disclose **term** not date (deriving forbidden) |
| net_property_income (+_currency) | 192/1653 | 88.4% | 0 | segment-only |
| original_currency / original_value | 184/1653 | 88.9% | 0 | foreign-only audit-trail pair |
| npi_pct | 96/1653 | 94.2% | 0 | segment-only |
| effective_date | 60/1653 | 96.4% | 0 | land-lease start rarely per-property |
| purchase_price_local (+_currency) **[W9]** | 29/1653 | 98.2% | 0 | foreign local-cost pair only (AJBU 17, CY6U 12) |
| gla | 18/1653 | 98.9% | 0 | superseded by nla/gfa |

### property_transaction — 95 rows
| column | fill | null % | real | note |
|---|---|---|---|---|
| property_name, transaction_type, status, currency, source_page, raw | 95/95 | 0% | 0 | |
| description | 93/95 | 2.1% | 0 | |
| transaction_date | 93/95 | 2.1% | 0 | P40U/T82U averaged "during period" strata |
| counterparty | 79/95 | 16.8% | 0 | unnamed "third party" |
| valuation (+_currency) | 74/95 | 22.1% | 0 | by-deal; not always an independent valuation |
| gross_sale_price (+_currency) | 66/95 | 30.5% | 0 | acquisition-null + prior-yr/blended |
| carrying_value (+_currency) | 64/95 | 32.6% | 0 | acquisition-null + not-separately-disclosed |
| carrying_value_basis | 62/95 | 34.7% | 0 | provenance, mirrors carrying_value |
| gain_on_divestment (+_currency) | 28/95 | 70.5% | 0 | divestment-only, aggregate-FS-line only |
| purchase_price (+_currency) | 23/95 | 75.8% | 0 | acquisition-only |
| net_sale_proceeds (+_currency) | 15/95 | 84.2% | 0 | rarely split out per-txn |
| gain_on_divestment_basis | 14/95 | 85.3% | 0 | provenance |
| interest_pct | 5/95 | 94.7% | 0 | partial/NCI deals only |
| net_proceeds_basis | 3/95 | 96.8% | 0 | provenance |

### top_tenant — 384 rows
| column | fill | null % | real | note |
|---|---|---|---|---|
| rank, client_name, revenue_pct, pct_basis, source_page | 383–384/384 | 0–0.3% | 0 | `client_name` now 384/384 (BUOU rank 13 recovered); revenue_pct 1 source-blank |
| industry | 348/384 | 9.4% | 0 | SET/M1GU/BTOU — no per-tenant sector column (see trade_mix) |

### trade_mix — 367 rows · notes — 37 rows
All columns 0% null.

## Wave 6 (2026-07-02) — thin residual pass
Fan-out of 7 Sonnet agents against the genuinely-recoverable remainder; each fill main-agent-verified against source before reload.
- **Filled + reloaded (Supabase):** J91U `number_of_unitholders` = 22,375 (p229; header-swap trap — 806,451,169 is units-in-issue not holders, verified); M44U 4 held-for-sale `market_valuation` (1 Genting Lane 12.3M, 31 Penjuru Lane 7.8M, 8 Tuas View Square 11.18M — SGD front-book Valuation column; Subang 2 9,482,000 SGD per footnote (s), consistent with MY siblings storing mv in SGD). → `number_of_unitholders` 3%→0%; `market_valuation` nulls 57→53.
- **Confirmed genuinely-absent this wave (do NOT re-hunt):**
  - `property_transaction.gain_on_divestment` (34 rows: M44U 14, A17U 9, SET 4, MXNU 4, T82U/XZL/O5RU 1 ea) — divestment gain disclosed **only as an aggregate FS line** (A17U p129 total 19,281; M44U p173 portfolio-level S$27.0m), **no per-property gain column**. Filling would require sale−carrying = a compute/balance violation. STOP.
  - Divested-property `market_valuation`/`purchase_price` (A17U 9, SET 8, most M44U/HMN) — `status=divested` → off-book, no FY-end valuation.
  - HMN 4 active AU hotels `market_valuation` = "Not applicable" per Portfolio Statement p143 (only a combined aggregate for 5 freehold PPE hotels); HMN 3 txn `purchase_price` = blended per acquisition batch (p11); HMN/Q5T/T82U/CY6U `wale` = split-only or MAS-waiver, no portfolio blend; CY6U/AW9U/T82U `weighted_avg_debt_maturity` = chart-only (no printed years); Q5T/8C8U `portfolio_occupancy` = segment-only (no blended); CY6U/T82U core `purchase_price` = combined-card/developed (unsplittable).

## Wave 7 (2026-07-03) — RAG-assisted pass + null-map hardening
RAG-first method (semantic locate → read full.md page/footnote → fill or harden). ScaleDown `/extract` empirically demoted (returns empty on text; PDF-only). 16 Sonnet agents across ~25 reports; main agent verified every fill against source before reload.
- **Filled + reloaded (10 txn per-figure recoveries):**
  - HMN 5 acquisition `valuation` from the printed "Agreed Property Value at Acquisition (S$'million)" column (p56-57: ibis Styles 136.0, Chisun 42.5, Pre de Cort 13.7, Splendide 10.6, Pregio 9.9) + Citadines Central Shinjuku divestment `valuation` 108,647k SGD (p132, the Dec-2024 Portfolio-Statement valuation the "sold 100% above valuation" footnote references).
  - ODBU Wallingford Fair `valuation` US$23.3m (p61, CBRE independent valuation; cross-checked vs p9 "8.2% below valuation").
  - AJBU Kelsterbach `gross_sale_price` EUR 50.0m (p36), AU8U CapitaMall Yuhuating `gross_sale_price` RMB 813.8m (p36 line "sale price of RMB813.8 million"), P40U Wisma Atria Office strata `gross_sale_price` S$41m + `valuation` S$32m (p32 ftnt (8): "approximately S$41 million, compared to the valuation of approximately S$32 million as at 30 June 2024 by CBRE" — a deal-specific valuation an agent had first ruled absent; caught on main-agent source re-verification). → **11 fills; `valuation` 28→20 null, `gross_sale_price` 34→31 null.**
  - **AJBU net_sale_proceeds correction:** the row's `net_sale_proceeds` S$70.6m was the EUR 50.0m consideration CONVERTED (not a true net-of-cost figure — its own basis note said so; the real after-cost S$65,475k is combined with NetCo). Nulled it (gross now correctly holds the EUR 50.0m consideration; true Kelsterbach-only net is undisclosed). Same conflation class as the JYEU fix.
- **Loader fix (systemic):** `scripts/db/load_supabase.py` did not accept the canonical `gross_sale_price`/`gross_sale_price_currency` keys as inputs (only `sale_price`/`consideration` aliases) — every agent that wrote `gross_sale_price` was silently dropped. Added both to the alias lists (currency checked before the row-presentation fallback so foreign EUR/RMB figures aren't mislabeled SGD).
- **Correction (source-cited):** JYEU Parkway Parade `alt_value`=S$4,130k was mislabeled — that figure is Note 7 "Investment in associates" (ARIF3/LLJV/TEJV Jem-fund associates), NOT Parkway Parade. Its correct carrying value (Note 9 "Equity instrument at fair value", S$86,090k) is already in `market_valuation`. Nulled `alt_value`/`alt_basis` + fixed the flag note. (`alt_*` are extraction-JSON-only, not DB columns.)
- **Confirmed genuinely-absent (hardened with fresh page cites in ~24 reports' `_notes.json`, do NOT re-hunt):** `market_valuation` fully exhausted (all 53 nulls divested/off-book or HMN's "N/A" AU hotels); property `purchase_price` stragglers all IPO-seed/staged-JV/dash-in-source (C38U Westgate+CapitaSpring staged, N2IU VivoCity IPO-seed, ME8U/T82U/CY6U dashes, J91U/Changi blended); `occupancy_rate` = hotels report RevPAR not occupancy (Q5T ×13, TS0U, J85), redevelopment/vacant dashes (M44U Subang, A17U Logis Hub), convention-centre "n/m" (T82U), MXNU qualitative-only; `nla` = GFA/bed-count/strata-only, per-property NLA not disclosed (8C8U beds, AW9U/M1GU/AU8U GFA, C2PU/UD1U aggregate-only); txn acquisition `carrying_value`/`gross_sale_price` = by-design; K71U/O5RU/UD1U/XZL/SET/Salesforce/Lippo `valuation` = agreed-price-only / deferred-to-announcement / FVTPL-fund / consideration-only.
- **Flags surfaced (not changed):** UD1U Il·lumina `carrying_value` 24,724k is self-documented as DERIVED (proceeds 24,500 + loss 224) — left as-is (arithmetically exact, no printed alternative), noted; AW9U IPT gross S$25,908k vs net S$22,440k; Q5T two existing `nla` are retail+office sub-component sums (defensible as mixed-use NLA).

## Wave 8 (2026-07-03) — mapping audit (exhausted) + CORRECTNESS sweep
Live DB re-census first (matched Wave-7 numbers exactly — Wave 7 fully landed, zero drift). **Mapping-gap audit (the handoff's "highest expected yield") came up empty:** a full key-inventory scan of every `property_transactions`/`properties`/`performance` JSON key vs what `load_supabase.py` reads showed all remaining unread keys are either redundant with an already-loaded base key (`*_local` foreign audit-trail on AJBU/CY6U/M44U; property `divestment_price` — the sale already lives in the txn table), a schema-shape question (CRPU per-property `trade_mix`), or pure provenance (`*_source_page`, `*_basis`, `valuer`, `note`, `existing_use`, `alt_value`). Nothing of the Wave-7 `gross_sale_price` class (present-but-unaliased) remains. So Wave 8 pivoted to a **correctness sweep** (net≥gross, valuation==carrying, gross==valuation, currency-tag defects) across all 95 txn rows + a thin residual-fill tail. 18 Sonnet agents (one per report with a fill target or a conflation flag); main agent read the cited `full.md` page for **every** change before reload and re-queried the DB to confirm each landed.
- **Filled + reloaded (2 txn `gross_sale_price`):** BTOU Plaza **US$51.8m** (p126 Note 6 "announced the divestment of Plaza … for US$51.8 million less seller credits"; market table p50 500 Plaza Dr $51,750,000) + BTOU Peachtree **US$133.8m** (p126 "divestment of Peachtree for US$133.8 million"; p50 $133,800,000). → `gross_sale_price` 64→66 fill (31→29 null).
- **Corrections (source-cited conflations, same class as Wave-7 JYEU/AJBU):**
  - **AW9U** Imperial Aryaduta `gross_sale_price` S$22,440,000 → **S$25,908,000**. The stored figure was the NET-of-tax proceeds (Note 30 p197 "total sales consideration (net of tax) … $22,440,000" = "Net cash flow on disposal 22,440") conflated into the gross column; the true gross consideration is the Interested-Person-Transactions table p200 "Sales consideration for the divestment of 100% … PT Karya Sentra Sejahtera … S$25,908,000". `net_sale_proceeds` stays 22,440,000 → net<gross now correct.
  - **J69U** Yishun 10 Retail Podium `valuation` S$34,500,000 → **null**. p37: the $34.5m is the "total consideration … negotiated … after taking into account the **average of two independent valuations of $34.0 million and $35.0 million**" — there is no single $34.5m valuation; the extractor put the consideration (=the average) into the valuation column (gross==valuation artefact). Consideration/carrying/gain retained.
  - **UD1U** Il·lumina `carrying_value` S$24,724,000 → **null**. Self-documented DERIVED (proceeds 24,500 + loss 224); `grep` confirms "24,724" appears **nowhere** in full.md (p178 prints only proceeds 24,500 + loss 224). Never-derive → null. (Resolves the Wave-7 flag.)
  - **XZL** Hyatt Place Detroit Livonia `carrying_value` US$10,300,000 → **null**. 10.3m is printed ONLY as the independent valuation (p16 portfolio list; p170 Note 29 "US$10.0 million … 2.9% discount to the independent valuation of US$10.3 million"); year-end held-for-sale balance = 0 (p133), so no per-property carrying was printed — the value was a valuation copy. `valuation`=10.3m + `price`=10.0m retained. → `carrying_value` 66→64 fill; `valuation` 75→74 (J69U null).
- **CONFIRMED-EQUAL, not conflation (14 `valuation==carrying` + 8 `gross==valuation` flags all resolved as genuine, hardened with cites; do NOT re-hunt):** A17U ×5 SG divestments (valuation from divestment table p32 vs carrying from Portfolio-Statement 2024 col p120-121 — genuinely equal; the 4 FOREIGN A17U divestments are **un**equal, proving no blanket-copy), J91U 6 announced + 1 Third Lok Yang (each sold at its 30-Nov-2025 independent valuation, p48; the two non-at-valuation siblings prove no copy), M44U 30 Tuas South Ave 8 / 119 Neythal (fair-value-model equal, p48/p171), MXNU Victoria Rd / Crown Buildings (fair-value model, p26/p148), N2IU Mapletree Anson 765m (last valuation = carrying at disposal, p117/p146), ODBU Albany triple-equality (held-for-sale at CBRE fair value = sale price, p184), O5RU 3 Toh Tuck Link (Level-2 held-for-sale at agreed price = carrying, p192), SET Florence (held-for-sale at contracted price, p240). All fair-value-model REITs legitimately show carrying(prior-val-date)=last independent valuation.
- **Hardened confirmed-absent (do NOT re-hunt):** 8C8U IPO Portfolio + EPIISOD `valuation` (only agreed acquisition price printed; the year-end aggregate S$1,884,420k is a different concept/date, not a deal valuation — left null per never-derive), K71U MBFC T3 (agreed-price-only; the 1,453m already loads as `purchase_price` via the consideration alias), SET AiOnX (FVTPL fund NAV, not a property valuation), TS0U Salesforce Tower + Lippo Plaza (consideration-only), CY6U CyberPearl/CyberVale + 20.2% DC stake (premium-%-only, agreed-value, deal completes next FY), BUOU 28-German (IFRS-10 equity transaction — no property carrying/valuation of the minority stake), M44U 7 prior-year divestment rows (blank valuation both balance dates).
- **Flags for follow-up (not changed):** (a) **Systemic currency scheme** — `purchase_price` stored converted-to-SGD for foreign properties on A17U/AJBU/BUOU/HMN/CY6U/K71U/O5RU/P40U/T82U/8C8U (hundreds of rows) while others store local + `_local`; and RMB(27)-vs-CNY(8) tag inconsistency. Both belong to the open `docs/currency_scheme.md` decision — NOT touched. (b) Several divested/terminated properties still carry a `valuation_date` (and XZL Memphis-terminated a printed price/valuation) where invariant-6 argues for null — minor cleanup, left. (c) J69U `net_sale_proceeds` 34,128k is derived vs printed 34,500k (p151) — flagged, left.


## Wave 9 (2026-07-03) — currency scheme (as-reported basis + value + date)
Full detail in `docs/currency_scheme.md` §"Wave 9 results". Re-census overturned the handoff premise: currency tags were **already ~100% present** (property: 0 missing on all 4 figures; txn: only 7). So Wave 9 = a **non-destructive structural migration (Option B, user-locked)** + ~5 source-cited row fixes, NOT a fill wave. `performance`/`financial` (single presentation ccy + `date`) untouched. Resolves the Wave-8 flag (a).
- **Schema:** +`sgx_reit_property.market_valuation_currency`, `.purchase_price_local`, `.purchase_price_local_currency` (no column dropped; audited SGD + presentation values all retained). `db/schema.sql` + `schema/models.py` updated.
- **Loader (`load_supabase.py`):** (1) `_ccy()` normalizes `RMB → CNY` on write (values unchanged; JSON stays as-reported); (2) fixed per-figure currency-tag guard bug (tag now keys off the resolved value, not a narrower re-lookup) → auto-tagged AJBU/AW9U/C2PU gain=SGD + BTOU Plaza/Peachtree valuation=USD; (3) `_first_date()` takes the first *valid* date alias so a malformed early alias no longer shadows a valid later one; (4) `market_valuation_currency` = local (foreign) else presentation, + surfaces the `purchase_price_local` pair.
- **Verified landed (37 dirs reloaded, live re-query):** RMB **92→0** (all CNY); `market_valuation_currency` **1600/1600**; `purchase_price_local` **29** (AJBU 17 AUD/CNY, CY6U 12 INR — exact source match, `purchase_price` stays presentation SGD); txn currency-tag gaps **7→0**; TS0U Salesforce Tower `transaction_date`=**2026-02-24** (agreement, p175); M44U Chee Wah/Subang `carrying_value_currency`=**SGD** (basis p190). Row counts intact (property 1653, txn 95).
- **Source-cited structural nulls left null** (`_notes.json` key `currency_scheme_wave9_2026_07_03`): P40U Wisma Atria (Office) strata + T82U Suntec City Office strata — both averaged/multi-unit divestments "during the period" with no single as-reported completion date (the only 2 txn rows with money but no date; correct as null).

## Wave 10 (2026-07-03) — DB-first null re-check + structural-null enumeration
Live per-column null census across all 8 relational tables, then each heavy-null (≥30%) column classified **structural (row-condition ⇒ null by design)** vs **real residual (value SHOULD exist)**. Verdict: after Waves 1–9 the DB is **essentially complete**; the real residual was ~15 candidate cells, of which **14 verified genuine-absent** (most already hardened with source-cited `_basis`/`_recovery_note`/`_notes`) and **1 fillable**.

### Structural null rules — enumerated & source-verified (these DISSOLVE; do NOT re-hunt)
- **`lease_expiry_date` (73% null, 1206):** Freehold 969 (no expiry) + **all 234 leasehold disclose tenure as a TERM** ("30+30 years", "99 years / 66 yrs remaining", MXNU/T82U "N-year from <date>"). Only D5IU prints explicit expiry dates (already filled). An expiry date would require deriving `completion + term` → **invariant-3 forbidden** ⇒ structural.
- **`lease_term_years` (62% null, 1023):** Freehold 968 + D5IU 29 (prints expiry date, not term) + SET perpetual/usufruct ⇒ structural.
- **`market_valuation` (53 null):** divested 49 + **HMN 4 active hotels** whose Portfolio Statement (p143) prints "At Valuation = *Not applicable*" (owned via the Ascott BT stapled group; the 2.1/1.9 figures are % of securityholders' funds, not $) ⇒ genuine-absent, not a value.
- **`valuation_date` (20 null):** all divested ⇒ structural.
- **`ownership` (235 null):** A17U 232 = whole-symbol (no per-property % disclosed) ⇒ structural.
- **`nla`/`occupancy_rate` (443/185):** HMN 105 (hotels report keys/RevPAR), data-centre/hotel REITs whole-symbol ⇒ structural.
- **`gross_revenue`/`purchase_price` (121/102):** ODBU/K71U/DHLU whole-symbol segment-only revenue; XZL 31 whole-symbol (no historic cost); M44U 17 prior-year rows ⇒ structural/hardened.
- **`net_property_income`/`npi_pct`/`gla`/`original_*`/`purchase_price_local`/`employee_breakdown`/`adjusted_distributable_income`:** segment-only / NLA-REITs / foreign-only pairs / externally-managed / method-2-only ⇒ structural (confirmed prior waves).
- **txn `net_sale_proceeds` (80)/`gain_on_divestment` (67):** not disclosed per-transaction by most REITs; `*_terminated` deals carry no final figures ⇒ structural.
- **`financial.balance_sheet_metrics` "missing" keys (units_in_issue, investment_properties, nav_per_unit … present 1/37):** the canonical **8-key** BS schema is 37/37 complete; ME8U alone captured 6 optional extras ⇒ **per-report metric-bag variance, not a null**.
- **`financial.funds_from_operation` (key present 37/37, value null 37/37):** FFO is a US-REIT convention SGX REITs do not report ⇒ genuine-absent.

### Real residual — adversarially verified vs `full.md` (14 genuine-absent, all source-cited)
- **txn (already hardened, notes re-confirmed correct):** M44U Chee Wah/Subang 1 `gross_sale_price` — prior-year (FY2023) divestments listed only as a dates table p173, no restated price. UD1U Il·lumina `carrying_value` — Round-8 note: prior 24,724k was derived (proceeds+loss), not printed (grep/RAG/portfolio-stmt confirm absent). XZL Detroit Livonia `carrying_value` — Round-8 note: not separately disclosed, held-for-sale=0 p133, prior 10.3M was valuation conflation. HMN Chisun Kanazawa/Splendide Namba/Pregio Esaka `purchase_price` — each "**not separately priced**" (part of a blended JPY acquisition, p11); valuations shown are Portfolio-Statement carrying, not price.
- **property tenure:** JYEU **Parkway Parade** `land_tenure` — genuine-absent (10% equity-accounted JV interest, reported only at fair value S$86.1M; no tenure token co-occurs with "Parkway" anywhere in the report). HMN Somerset Olympic Tower Tianjin — divested (structural).
- **performance (all segment-only or chart-only ⇒ genuine-absent):** `weighted_avg_debt_maturity` AW9U/T82U/CY6U — only a Debt-Maturity-Profile **bar chart**, no scalar-years text (blending = derivation). `wale` T82U (office 3.80 / retail 2.42 yrs, no blend), CY6U (no scalar, lease-expiry chart only), Q5T (1.34 yrs = commercial-premises subset; hotel master-lease trust), HMN (11 yrs = 28 master-leases subset; management-contract hotels have no lease). `portfolio_occupancy` Q5T (hotels 81.3% / SR 81.5% segment-only), 8C8U (PBWA 97.6% / PBSA 99.1% segment-only) — no reported blend.

### Filled (1) — verified, reloaded, DB-confirmed
- **N2IU The Pinnacle Gangnam `land_tenure`/`tenure_raw` = "Freehold"** — Properties-at-a-Glance factbox p47 (Title cell = Freehold, acquisition 21 Jul 2022). The prior round-2 `_recovery_note` had *already identified* "Freehold" (and correctly left `lease_expiry_date` null) but forgot to set the tenure fields — a genuine extraction miss. `land_tenure` NULL 3→2 (remaining 2 both documented genuine-absent above). QC PASS; row counts intact (property 1653, txn 95).

**Lever status:** null-recovery declared **exhausted** — remaining heavy nulls are structural or source-confirmed absent; the txn `_basis`/`note` and property `_recovery_note` fields already document the genuine-absent cases (Wave 10 re-verified a sample and found the prior hardening correct).

## Wave 11 (2026-07-03) — property high-null adversarial re-verify (NPI, lease, gfa/gla, ownership)
Targeted, suspicious re-audit of the 4 requested property columns. **Loader-miss ruled out first** (corpus-wide): scanned every `properties.json` for keys the rigid property builder (`r.get`, no aliases) never reads — **no synonym key** for `ownership`/`gfa`/`gla`/lease anywhere; the only unread NPI-ish keys (`_npi_rmb_million` AU8U, `_npi_unit` DHLU, `_ema_rental_income_rmb_million` CRPU) are **unit annotations coexisting with a populated canonical `net_property_income`** — not misses. Then fanned out **9 report-auditors over all 37 reports**; main agent verified every proposed fill against the cited `full.md` page before reload.
- **Filled + reloaded + DB-confirmed (5 values, 2 reports):**
  - HMN Somerset Liang Court `gfa`=**13,000 sqm** (p180 "gross floor area of about 13,000 square metres … under development"); HMN Somerset Olympic Tower Tianjin `gfa`=**32,900 sqm** + `ownership`=**100%** (p196 "The Stapled Group owns a 100% interest … gross floor area of about 32,900 square metres"); HMN Citadines Central Shinjuku `ownership`=**100%** (p182 Note 8, Pearl Residence TMK 100% effective interest); N2IU Fujitsu Makuhari (FJM) `gfa`=**657,549 sqft** (p48 ftnt 5 "lettable area is based on a gross floor area of 657,549 square feet"). → `gfa` null 1037→1034, `ownership` null 235→233. Row count intact (1653).
- **net_property_income — 0 fills, GENUINE-ABSENT confirmed for all 21 zero-coverage REITs** (the biggest suspicion). Every one discloses NPI **only at business/geographic SEGMENT level** (A17U 3-segment Note 30; M44U market-segment Note 29; AJBU/CY6U asset-type; UD1U/DCRU/SET/O5RU/ODBU/OXMU/MXNU/J91U geography; HMN/Q5T/XZL/TS0U/C38U/C2PU/8C8U/BUOU/ME8U segment/portfolio). Per-property tables print **Gross Revenue, not NPI**. Partial-coverage gaps (N2IU MBC-I/II combined + Anson divested; K71U MBFC combined-JV; CY6U 3 under-development; J85/J69U footnote-combined; D5IU Grand Palladium dashes) all source-confirmed non-split/absent. NPI is **not a recoverable lever** — deriving from segment÷count is forbidden.
- **lease_expiry_date / lease_term_years — 0 fills, GENUINE-ABSENT.** Every leasehold-null-expiry row discloses tenure as **term (± commencement / remaining term)**, never an explicit expiry DATE (M44U/ME8U/C38U/T82U/MXNU/SET/Q5T); deriving expiry = forbidden. Null-term rows are dual/split-lease (M44U 3, J91U 3) or date-only disclosure (D5IU, DHLU, ODBU) where no single numeric term is printed.
- **gfa/gla — 0 further fills beyond the 3 above, GENUINE-ABSENT.** Overwhelmingly NLA/lettable-area-only portfolios (BUOU/MXNU/UD1U/O5RU/ODBU/OXMU/K71U/DHLU/SET/CMOU/DCRU); AJBU Keppel-DC prints GFA as "–" for the 13 nulls; A17U/ME8U/AU8U/C2PU nulls are divested/decommissioned assets absent from the operational GFA tables. Never copied NLA into gfa.
- **ownership — 0 fills beyond the 2 above, GENUINE-ABSENT.** A17U (232) has **no per-property ownership % column** at all (only subsidiary-level 100% in FS Note 8; a 34% JV sits off the property list) — correctly **not assumed 100%**.
- **Data-quality findings (flagged, NOT changed — need a decision/schema call):**
  - **8C8U `gfa` is mislabeled Land Area.** The p14 "Property Information" table has columns …No. of Beds | **Land Area (sq m)** | Valuation… and **no GFA column**; the 14 `gfa` values (e.g. Westlite Toh Guan 11,685) are the Land-Area figure. Recommend either null them or add a `land_area` column and move them. Left as-is pending decision.
  - Identity labels corrected in agent notes (no data impact — symbols already correct): BUOU = Frasers Logistics & Commercial Trust (not Daiwa House), AJBU = Keppel DC REIT, CY6U = CapitaLand India Trust, **D5IU = Landmark REIT (ex-Lippo Malls Indonesia Retail Trust), not Digital Core**.
  - DCRU Wilhelm-Fay-Strasse NPI = the EMEA segment figure (EMEA = Frankfurt-only, so effectively per-property); left unchanged. JYEU Sky Complex "gross area 78,873 sqm" is called NLA in prose → left null (borderline, not copied).

**Lever status (updated):** per-property **NPI and lease-expiry/term are exhausted** — comprehensively source-confirmed segment-only / term-based across all 37 reports, not recoverable without forbidden derivation. gfa/ownership residuals are divested/undisclosed. Only open item is the 8C8U gfa=Land-Area DQ correction (awaiting decision).

## Recovery history (see memory `phase3-audit-tier0`)
Rounds 2–5 (2026-07-02) recovered: D5IU ownership (29), J69U npi_pct (8), ME8U nla+gfa (26 props), J85 occupancy (20), M44U nla (174), category_raw (93 across 4 REITs), txn descriptions (28) & dates (10), purchase_price (28), scattered valuations/counterparties. All applied to Supabase + gated PASS.
