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

## Stage A — full fill/null by column (live 2026-07-02)

### profile — 37 rows
| column | fill | null % |
|---|---|---|
| symbol / sub_sector / management / income_model / source_page | 37/37 | 0% |

### performance — 37 rows
| column | fill | null % |
|---|---|---|
| portfolio_value, gross_revenue, net_property_income, net_distributable_income, dpu | 37/37 | 0% |
| distribution_record, distribution_paid, distribution_basis | 37/37 | 0% |
| aggregate_leverage, interest_coverage_ratio, cost_of_debt, nav_per_unit | 37/37 | 0% |
| number_of_unitholders | 37/37 | 0% (J91U recovered wave 6) |
| portfolio_occupancy | 35/37 | 5% |
| weighted_avg_debt_maturity | 34/37 | 8% |
| wale | 33/37 | 11% |
| adjusted_distributable_income | 1/37 | 97% ⚠️ (drop candidate) |

### financial — 37 rows
| column | fill | null % |
|---|---|---|
| income_stmt / balance_sheet / cash_flow / line_items | 37/37 | 0% |
| employee_breakdown | 8/37 | 78% ⚠️ (externally-managed = structural) |

### property — 1,653 rows
| column | fill | null % |
|---|---|---|
| property_name, country, category, address, currency, status, land_tenure, tenure_raw | ~1653/1653 | 0% |
| category_raw | 1651/1653 | 0% |
| valuation_date | 1633/1653 | 1% |
| market_valuation | 1600/1653 | 3% (M44U held-for-sale ×4 recovered wave 6; residual = divested/off-book) |
| purchase_price (+_currency) | 1551/1653 | 6% |
| gross_revenue (+_currency) | 1532/1653 | 7% |
| occupancy_rate | 1468/1653 | 11% |
| ownership | 1418/1653 | 14% |
| nla | 1210/1653 | 27% ⚠️ |
| area_unit | 1117/1653 | 32% ⚠️ |
| gfa | 616/1653 | 63% ⚠️ (NLA-only REITs) |
| lease_term_years | 630/1653 | 62% ⚠️ (freehold) |
| lease_expiry_date | 447/1653 | 73% ⚠️ (freehold) |
| net_property_income (+_currency) | 192/1653 | 88% ⚠️ (segment-only) |
| original_currency / original_value | 184/1653 | 89% ⚠️ (audit-trail) |
| npi_pct | 96/1653 | 94% ⚠️ (segment-only) |
| effective_date | 60/1653 | 96% ⚠️ |
| gla | 18/1653 | 99% ⚠️ (superseded by nla/gfa) |
| major_tenants | — | stored as empty array; data → top_tenant table |

### property_transaction — 95 rows
| column | fill | null % |
|---|---|---|
| property_name, transaction_type, transaction_date, status | ~95/95 | 0–3% |
| description | 93/95 | 2% |
| currency | 93/95 | 2% |
| counterparty | 79/95 | 17% (unnamed "third party") |
| valuation | 74/95 | 22% ⚠️ (by-deal; J69U Yishun-10 nulled wave 8 = consideration≠valuation) |
| carrying_value (+_currency/_basis) | 64/95 | 33% ⚠️ (UD1U/XZL-Livonia derived-copies nulled wave 8) |
| gross_sale_price (+_currency) | 66/95 | 31% ⚠️ (divestment-only; BTOU Plaza+Peachtree recovered wave 8; AW9U corrected net→gross) |
| gain_on_divestment (+_currency/_basis) | 14–28/95 | 71–85% ⚠️ (divestment-only) |
| purchase_price (+_currency) | 23–26/95 | 73–76% ⚠️ (acquisition-only) |
| net_sale_proceeds (+_currency/_basis) | 3–16/95 | 83–97% ⚠️ (rarely split out) |
| interest_pct | 5/95 | 95% ⚠️ (partial/NCI deals only) |

### top_tenant — 384 rows
| column | fill | null % |
|---|---|---|
| rank, revenue_pct, pct_basis, source_page | ~384/384 | 0% |
| client_name | 383/384 | 0% (BUOU rank 13 = source "Undisclosed") |
| industry | 348/384 | 9% (SET/M1GU/BTOU — no per-tenant sector; see trade_mix) |

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


## Recovery history (see memory `phase3-audit-tier0`)
Rounds 2–5 (2026-07-02) recovered: D5IU ownership (29), J69U npi_pct (8), ME8U nla+gfa (26 props), J85 occupancy (20), M44U nla (174), category_raw (93 across 4 REITs), txn descriptions (28) & dates (10), purchase_price (28), scattered valuations/counterparties. All applied to Supabase + gated PASS.
