# Phase 3 — Findings Ledger (audit + normalization)

**Purpose:** running record of everything found while auditing the proofread DB for (A) conflation/breaking-down cases (like the Stage-1 `net_proceeds` → `gross_sale_price` + `net_sale_proceeds` split), (B) categorical normalization, (C) disclosed-but-unhomed data, (D) null classification (miss vs structural), (E) suspect/wrong values. This is a **read-only** audit — findings here feed later apply-passes. Re-run freely; append, don't overwrite.

**Finding categories:** `A=conflation/split` · `B=normalize categorical` · `C=data-with-no-home` · `D=null classification` · `E=suspect value`

Last updated: 2026-07-01 (all 7 per-table auditors complete).

---

## CONSOLIDATED WORKLIST (synthesis of all 7 audits)

### Tier 0 — data-integrity bugs — ✅ ALL DONE (2026-07-01, applied to Supabase)
1. ✅ **A17U 128 local valuations now load** — loader aliases `local_currency`/`local_currency_value` → `original_currency`/`original_value` (128 loaded, incl. 33 AUD). AU8U `_rmb_valuation_000` (×1000) promoted to original_value/RMB (17 rows). CRPU EMA RMB left (NPI-side, Tier-1).
2. ✅ **DHLU per-figure NPI/GR currency** — added `net_property_income_currency`+`gross_revenue_currency` columns (schema+model+loader, default row ccy); DHLU now JPY-tagged (18 NPI / 7 GR).
3. ✅ **M44U txn currency** — resolver now derives row ccy from explicit per-figure currencies (NOT `local_currency`, which is the asset-local ccy); 15 rows now SGD (2 remain null = the combined MYR pair with no money figures — correct).
4. ✅ **M44U 6 metrics recovered** (verified vs source): leverage 40.7, ICR 2.9, NAV 1.31, WADM 3.8, WALE 2.8(NLA), cost_of_debt **2.7** (audit's 3.57% was an intercompany-loan rate — corrected), +occupancy 96.2.
5. ✅ **M1GU adjusted_distributable_income = 43,830,000** (p20). *Follow-up (Tier-1): M1GU `net_distributable_income` holds the DECLARED amount not income-available — basis fix.*
6. ✅ **C2PU sponsor = IHH Healthcare Berhad** added (Parkway Pantai is only intermediate holdco).
7. ✅ **BTOU note fixed** — corrected to "stored dpu=0; 1.44 is DI-per-unit". *Follow-up (Tier-2): add `di_per_unit` home.*
8. ✅ **J69U trade fixed** (Fashion & Accessories; Leisure & Entertainment→Hospitality & Leisure), **J91U Self-Storage unified** → Infrastructure/RE/Property Services; 3 TRADE_ALIASES added for determinism.

### Tier 1 — conflation / breaking-down (the "like Stage 1" work)
- **Per-figure currency** (recurs like the txn split): property `net_property_income_currency` + `gross_revenue_currency` + fix `original_value`; (txn already done).
- **Basis flags** where one number hides mixed bases: property `value_basis` (consolidated/JV-100%/effective-interest) → typed column; performance `distributable_income_basis`, `wale_basis`, `icr_basis`, `cost_of_debt_basis`, `leverage_basis`; `dpu_is_full_year`.
- **Tenure breaking-down**: property `tenure_raw` → `land_lease_remaining_years` + `master_lease{term,remaining,expiry}`.
- **Capacity**: property `capacity_value`+`capacity_unit` (keys/rooms/beds/MW/kW) — stop coercing into gfa.
- **txn `transaction_type` → `direction` + status + partial flag** (non-orthogonal today).
- **financial `line_items.statement`** too coarse below NPI → add `finance_cost`/`tax` (or a `category` sub-field); + one canonical statement per component.
- **distribution_record.period** → typed {start,end,label}, split declared vs paid, de-dup K71U.

### Tier 2 — homeless disclosed data → NEW tables / columns
- **New tables** (each a distinct breakdown dimension): `sgx_reit_lease_expiry`, `sgx_reit_geographic_mix`, `sgx_reit_wale_segment` (or wale_breakdown jsonb).
- **New performance columns**: fixed_rate/hedge %, gross_borrowings(+ccy), distribution_yield, credit_rating, rental_reversion_pct, perpetual_securities(+distribution), debt_headroom, di_per_unit, hospitality KPIs (RevPAR/ADR/AOR) jsonb, distribution_components{taxable,tax_exempt,capital}.
- **New profile columns**: listing_date, sponsor_stake_pct, externally_managed, structure(reit|stapled|bt), fee_structure jsonb, fy_end, country_of_incorporation, isin; add `trustee_manager` role.
- **New property**: independent_valuation (`alt_value`, 50 rows) + basis; gross_revenue_pct.
- **New txn**: valuer, valuation_date, agreement_date, per-figure source pages, remaining *_basis (valuation/consideration), *_local amounts.

### Tier 3 — categorical normalization
- `country`: USA/United States, The UK/UK, The Netherlands/Netherlands.
- **`RMB`→`CNY`** (recurs in property.original_currency, property/txn currency cols) — one code.
- `pct_basis` (top_tenant + trade_mix): normalize Ascott string → `rental_income` + note; add `pct_basis_family` (RENT/REVENUE/NET); keep `asset_value` class-tagged distinct.
- `category_raw` dedup (Data Centre/Centres, Logistics variants, case); `Data Centers`(property) vs `Data Centre`(sub_sector) spelling.
- `income_model`: expand `fri`, drop unused `mcmgi`; `sub_sector`: add `Specialized` to enum; `Diversified` mix rollup.
- `line_items.component`: 224 names → canonical lexicon.

### Drop candidates (Phase 4)
- performance `adjusted_distributable_income` (100% null — AFTER recovering M1GU); `distribution_record.ex_date`/`pay_date` (89/89 null).
- property `existing_use` (== category_raw verbatim); collapse 7 empty-shell `employee_breakdown` objects → null.

### Cross-cutting themes
- **Per-figure currency + basis conflation** is the dominant pattern (same as Stage 1) — appears in property (currency+value_basis) and performance (5 basis flags).
- **RMB/CNY** and **pct_basis** dirt span multiple tables — normalize once, centrally.
- **"Data-with-no-home" is large** — points to 3 new breakdown tables + a batch of performance/profile columns, not just tweaks.
- **Verified-correct-don't-touch**: SPV-disposal gains (≠ proceeds−carrying), negative income_taxes (=credits), 100%-summing top-tenant lists (concentrated portfolios), hospitality nulls (NPI/occupancy/area — use RevPAR/keys).

---

## Detailed per-table findings

---

## Already established (Stage 1 + Stage A/B/C)

### property_transaction (Stage 1 — DONE, applied)
- **A** `net_proceeds` split into `gross_sale_price` + `net_sale_proceeds` (11 rows had both). ✅ applied
- **A** single row `currency` → 6 per-figure currency columns (14 mixed-currency rows). ✅ applied
- **A** `carrying_value_basis`/`gain_on_divestment_basis`/`net_proceeds_basis` promoted from raw. ✅ applied
- **A** `transaction_type` lifecycle split → derived `status` (completed/announced/terminated). ✅ applied
- Open: whether `transaction_type` should further split type vs partial (interest_pct now carries stake).

### Stage B — categorical dirt (from docs/phase3_categorical_inventory.md)
- **B** `property.country`: `USA`×11 vs `United States`×201; `The United Kingdom`×7 vs `United Kingdom`×218; `Netherlands`×6 vs `The Netherlands`×21 → collapse each pair.
- **B** currency code `RMB`×70 vs `CNY`×8 (property.original_currency, property.purchase_price_currency, txn.valuation_currency) → pick one.
- **B** `pct_basis` (top_tenant + trade_mix): `'rental_income (corporate accounts …Ascott…)'`×11 → normalize to `rental_income` + move caveat to a note.
- **B** `property.category` `Data Centers` vs `profile.sub_sector` `Data Centre` (spelling); odd `Diversified (Commercial)`×6 — confirm.
- **B** `profile.income_model` `fri`×1 cryptic — confirm meaning.
- **B?** `pct_basis` open vocabulary (`gri` vs `gross_revenue` vs `rental_income` …) — confirm intended distinctions.

### Stage C — nulls needing judgment (from docs/phase3_null_checking.md)
- **D/E** `performance` risk block all null for **M44U** (aggregate_leverage, interest_coverage_ratio, cost_of_debt, nav_per_unit, wale, weighted_avg_debt_maturity), no note → likely EXTRACTION MISS.
- **D** `top_tenant.industry`: SET×10 (all blank), N2IU×1, MXNU×1 — SET likely a miss.
- **D** `property.ownership`: HMN 2 props unexplained.
- **D** `performance.adjusted_distributable_income` 100% null by design → Phase-4 DROP candidate.

---

## Fan-out findings (per-table auditors)

### profile
**A — conflation / split**
- `management`: stapled-trust **BT trustee-manager inconsistently role-tagged** — `trustee` in HMN/Q5T/XZL but `reit_manager` in J85/SET (same governance entity). → add `trustee_manager` role (or `component: reit|bt`), apply to the 5 stapled trusts.
- `management`: **multi-party crammed into one entry** — e.g. AU8U PM `"CapitaLand Investment Limited (via subsidiaries…)"`; XZL master_lessee = 3 SPVs in one string; parentheticals in `company_name`. → split into rows, move qualifiers to a note field.
- `management`: **non-schema `_role_note` keys** (HMN ×3) silently dropped on load. → add optional `note` to ManagerEntity.
- `income_model`: scalar `mixed` (×7) **hides which properties are master-lease vs conventional** — real per-property model stored nowhere. → multi-value or record on property.
- `sub_sector`: `Diversified` (×11) **collapses real asset composition**; office/retail/industrial split only implicit in property.category. → add derived `sub_sector_mix` / rollup.

**B — normalize categorical**
- `sub_sector`: value `Specialized` (8C8U) is **outside the documented 7-value enum**. → add to enum or `sub_sector_raw`.
- `sub_sector`: `Data Centre` (profile) vs `Data Centers` (property.category) spelling drift.
- `income_model`: `fri` cryptic (J85, =fixed-rental-income); enum lists unused `mcmgi`. → expand `fri`, drop/define `mcmgi`.
- `management.role`: role set otherwise clean (6 controlled values).

**C — data-with-no-home** (proposed new profile columns): `listing_date`/`constitution_date`; `sponsor_stake_pct`; `externally_managed` bool; `fee_structure` jsonb (base/perf/property/acq/divest fee bases); `corporate_actions`/manager-change events (T82U manager acquired by Acrophyte, post-FY); `structure` = reit|stapled|business_trust (HMN/J85/SET/Q5T/XZL stapled); `fy_end`, `country_of_incorporation`, `isin`; optional `valuers`.

**D — null / coverage**
- `management` sponsor missing on 2/37: **C2PU = genuine MISS** (Parkway Life AR names Sponsor = Parkway Pantai/IHH, 84 mentions) → add; M1GU legitimately sponsorless (Volare takeover) → annotate.
- `property_manager` partial coverage (M44U/MXNU/AW9U/AJBU/C2PU/CRPU…) — treat as "verify" not "complete". trustee + reit_manager present on all 37.

**E — suspect**
- **C2PU missing Sponsor** (clearest error, confirmed vs source).
- HMN sponsor now correct (The Ascott Ltd) — just remove non-schema `_role_note`.
- Debatable single sub_sector on mixed trusts: ME8U (big DC weight) tagged Diversified; ODBU (grocery-retail **+ self-storage**) tagged Retail (storage dropped).
- J85 has 11 `operator` entries (hotel brands) — verify not just passing brand mentions.

### trade_mix
**A — conflation / split**
- **Non-unique grain**: 29/37 REITs have duplicate `(category, pct_basis)` after raw→canonical collapse (many raw lines → one canonical). Consumers MUST `GROUP BY … SUM(pct)`. → document grain; keep `category_raw` as true identity; consider `raw_rank`/line-order column.
- **T82U crams TWO breakdowns in one table (sums 200%)**: Office tenant-industry mix (13 rows ~100%) + Retail trade-sector mix (13 rows ~100%), all `pct_basis='gri'`, no separator. → add optional `segment` column (office|retail). (Only REIT needing it — a full `dimension` enum is over-engineering.)
- Cross-dimension conflation otherwise LOW — table is genuinely trade-sector/tenant-industry only (no geography rows mixed in).

**B — normalize categorical**
- `pct_basis` Ascott string ×11 (HMN) → `rental_income` + caveat to note (same as top_tenant).
- `pct_basis` 8 values fragment the denominator: rent variants (`rental_income`/`cash_rental_income`/`committed_gross_rent`/`headline_rent`) → add normalized `pct_basis` enum + keep `pct_basis_raw`. **`asset_value` (C2PU ×2) is % of value not income — must not pool with the 365 income-based rows.**
- `category` itself clean (367/367 in the 15 canonical; variants only in verbatim `category_raw`).

**C — data-with-no-home** (each wants its OWN table/dimension, NOT trade_mix): **lease-expiry profile %** (8C8U, N2IU) → `sgx_reit_lease_expiry`; **WALE-by-segment** (A17U geo, AJBU contract-type, J85 lease-type…) → `wale_breakdown` jsonb or `sgx_reit_wale_segment`; **geographic mix %** (8C8U, BUOU, CY6U, SET) → `sgx_reit_geographic_mix`; **tenant-type/lease-structure mix** (O5RU multi vs master-lease, 8C8U PBWA/PBSA) → mix table w/ discriminator.

**D — coverage**: XZL 0 rows = structural (single-sector hospitality, no trade mix disclosed) — OK. Otherwise 36/37 populated, ~0 column nulls.

**E — suspect**
- **J69U systematically under-classifies** `Fashion & Accessories` and `Leisure & Entertainment` raws → `Other Retail Trades` (everyone else maps them to dedicated canonicals). → fix + add to `TRADE_ALIASES`.
- `Self-Storage` inconsistently mapped: J91U→Logistics vs ODBU→Infrastructure. → pick one, add alias.
- T82U 200% sum = the A conflation above (not a bad value).
- D5IU `'All Other Sectors'` 30.7% residual bucket — note-flag.

### financial
**Health: GOOD** — all 37 carry the full 20 income + 8 BS + 6 CF keys; **line_items foot to net_income to the dollar 37/37**; NPI identity holds 37/37; **revenue mis-bucketing fully resolved** (0 finance/interest/FV/fx lines tagged revenue). `_derived` flags working (computed never masquerades as disclosed).

**A — conflation / split**
- `line_items.statement` **3-value vocab (revenue/expense/adjustment) too coarse below NPI** — finance-cost, tax, fair-value, divestment-gain all crammed into `adjustment` (240 lines, 108 components). → add `finance_cost`/`tax` values or a `category` sub-field.
- ISM `non_operating_income_or_loss` collapses finance income/FV/fx/JV/divestment-gain into one signed key — granularity survives only in `line_items` → treat line_items as authoritative below-NPI breakdown.
- ME8U alone stuffs 6 extra keys into `balance_sheet_metrics` (investment_properties, NCI, perpetuals…) — inconsistent shape vs other 36.
- O5RU `service_charge_land_rent_property_tax` bundles 3 revenue concepts in one component.
- `cost_of_revenue_breakdown` non-canonical key in only 3/37.

**B — normalize categorical**
- `line_items.statement` **same component classified under 2 different statements across reports**: finance_costs = expense in 30 but adjustment in ~23; tax = adjustment in 32 but expense in ~19; also mgmt/trustee/other fees span 2. → one canonical statement per component.
- `line_items.component` **224 distinct names for a small concept set** — heavy drift (finance_costs/finance_cost/finance_expenses; trustee_fee/fees; income_tax/income_taxes/tax_expense/taxation; car_park/carpark; repairs variants). → canonical-key lexicon + lint.
- `currency` clean (row-level, matches presentation; functional-ccy figures correctly parked in notes).

**C — data-with-no-home**: perpetual securities balance + NCI (AW9U/BMOU/ME8U) → BS keys; segment gross-rev/NPI splits (AU8U/AJBU/8C8U) → segment table; investment-properties-under-development (A17U) + JV/equity-accounted asset values (C38U ION) → BS sub-keys/property; adjusted/cash NPI ex-straight-line (CMOU/CRPU) → optional `adjusted_npi`; FX rates avg/closing (~8 reports) → optional fx-rates jsonb.

**D — null classification**
- `employee_breakdown` 29/37 null + **7 empty-shell objects (all sub-fields None)** → collapse to null (schema's own rule: null when total_employee==0); only ODBU has a real value (13). Structural (externally managed).
- `funds_from_operation` 0/37 — SG REITs report distributable income not FFO. Structural — ensure downstream doesn't treat null FFO as missing.
- minorities 22/37, perpetual_security_holders 19/37 — null where no NCI/perps (structural).

**E — suspect (all verified faithful, convention notes only)**
- `income_taxes` **negative in 7 reports** (CMOU/J69U/N2IU/O5RU/TS0U/UD1U/XZL) = genuine **tax credits** (reconciles; line_items carry opposite sign). Schema says "positive magnitude" → **document that negative = credit; don't flip the sign.**
- J69U `bad_debts_recovered` −3,000 under expense = recovery (negative expense) — faithful.

### property_transaction (Stage-1 already done; this = residual)
**A — conflation / split still present**
- **Local-currency amounts orphaned in raw** (33 occ): `consideration_local`(12), `sale_price_local`(10), `valuation_local`(8), `transaction_price_local`(1), `sale_price_rmb_m`(1, wrong scale=millions). These are the AR *headline* native figures (M44U JPY/MYR, DCRU JPY13bn, AU8U RMB813.8m); typed cols hold only SGD-equiv. → add `*_local` numeric + local ccy, or `local_amounts` jsonb. **(NOTE: earlier we chose to leave *_local in raw — this audit argues the headline native figure deserves a home. Revisit.)**
- `valuer` name unmapped (10); `valuation_date` (appraisal date, distinct from transaction_date) unmapped (10). → add columns.
- Per-figure source pages orphaned: `deal_source_page`(15), `disclosure_source_page`(10), `counterparty_source_page`(4) → promote (mirror the *_basis promotion).
- Remaining basis text left in raw: `valuation_basis`(5), `consideration_basis`(3), `txn_basis`(1) — inconsistent (3 basis fields typed, 3 not).
- `transaction_type` **non-orthogonal**: `partial_divestment` encodes NCI-ness that acquisitions carry via `interest_pct` instead (K71U/TS0U/DCRU partial buys are plain `acquisition`). → split `direction` (acq|div) + `status` for lifecycle + interest_pct-driven partial flag.
- `cost_recognised` (acq cost incl. stamp duty, MXNU GBP9.644m vs 9.2m consideration) unmapped.
- `agreement_date` (signing, 4 rows) collapsed into `transaction_date` (completion) — for terminated XZL Memphis, agreement fills the completion slot. → separate column.

**B — normalize**: **RMB vs CNY** again (HMN currency_local=CNY vs AU8U/TS0U/M44U=RMB). → ISO `CNY`.

**C — data-with-no-home**: valuer, valuation_date, per-figure source pages, valuation/consideration basis (above); BUOU German NCI **equity-recognized ownership change** (→89.9%, S$0.746m to unitholders in equity not P&L) — no home for resulting-interest % / equity impact.

**D — null classification**
- purchase_price 3 nulls = structural (HMN blended). carrying_value ~29 null = structural (acquisitions; M44U combined-pair NOT_RECOVERABLE). gain 28 populated, rest structural.
- **MISS (mechanical)**: all 10 M44U rows have row `currency`=NULL and `carrying_value_currency`=NULL because resolver reads `currency_local` but NOT `local_currency` (M44U uses the latter). All M44U figures are SGD. → fix resolver fallback to also read `local_currency`.

**E — suspect (verified faithful — do NOT "fix")**
- **`gain` ≠ proceeds − carrying for SPV/subsidiary disposals** (12 rows): AU8U Yuhuating (−11.99m, FX recycling), CY6U CyberPearl (+4.08m vs net assets), TS0U Lippo (−26.43m), HMN Somerset Tianjin, M44U Xi'an — gain struck vs **net assets disposed incl. FCTR**, not IP carrying. → **never derive gain = proceeds−carrying**; keep as-disclosed, flag SPV rows.
- BUOU 357 Collins cross-currency (gross AUD vs carrying SGD) — correctly tagged; margin math across cols invalid.
- MXNU `cost_recognised` row has `property_name`=null (94/95) — minor fill miss, recoverable from note.

### top_tenant
**A — conflation / split**
- `revenue_pct` not comparable REIT-to-REIT (8 denominators). → add derived `pct_basis_family` (RENT/REVENUE/NET); keep raw.
- **Trade-GROUP rows in a named-tenant table**: HMN r1 "Government entities…"; MXNU "Commercial tenant (1)"/"Healthcare tenant (1)" (the `(n)`=count, sector inside name). → `is_group`/anonymised flag.
- **Anonymised placeholders as names**: DHLU "Tenant A/B/C", N2IU "(Undisclosed tenant)", BUOU r13 null. → `anonymised` flag not free-text.
- `client_name` carries parentheticals/roll-ups (AW9U "…and subsidiaries", P40U "YTL Group (4 entities)") — split entity vs qualifier, low priority.

**B — normalize**: `pct_basis` Ascott string ×11 → `rental_income` + note (caveat is load-bearing: HMN top-11 only sums 2.4% because scope is tiny). The 8 bases are genuinely distinct (not spelling variants) → keep raw + add `pct_basis_family`. `industry` 16 values all canonical, no variants.

**C — data-with-no-home**: per-tenant WALE (DHLU, BUOU) → `wale_years` + REIT `top10_wale`; per-tenant/by-NLA ranking (D5IU, J91U) → `revenue_pct_nla` or `basis='nla'` sibling; per-tenant country (SET has a Country col!, CY6U) → `tenant_country`; portfolio lease counts (ME8U 2232 tenants/3349 leases) → REIT-level; top-N concentration subtotal (DHLU 66.6%) → `top10_concentration_pct`.

**D — null classification**
- `industry` **36 nulls (more than thought)**: SET(10), BTOU(10), M1GU(10), P40U(4), MXNU(1), N2IU(1). **ALL genuine NON-DISCLOSURE** (verified: SET tenant table has rank/name/country/% only — no sector column; sectors live in each's `trade_mix`). → leave null, mark provenance; do NOT infer. **(Overturns the earlier "SET likely a miss" guess.)**
- client_name 1 null (BUOU r13), revenue_pct 1 null (N2IU anonymised) — both faithful.

**E — suspect (all faithful)**
- No top-N sum >100%. XZL/AW9U/MXNU sum to 100% because the "top-N" IS the whole tenant base (concentrated); flag as full-list. DWP alone = MXNU 92.3%.
- **BUOU & T82U carry 20 rows = two segments' top-10s merged into a global 1–20 rank**; per-segment rank/label only in non-schema `_segment`/`_segment_rank` keys → decide whether to persist `segment`/`segment_rank` (else two independent lists silently merged).
- No subtotal rows masquerading as clients.

### property (biggest table — highest-severity items)
**A — conflation / split**
- **⚠️ Per-figure currency on `net_property_income`/`gross_revenue`** — DHLU all 19 rows: `currency`=SGD, `market_valuation` SGD, but NPI=568,000,000 & GR=801,000,000 are **JPY** (Tan Duc 2 = VND), tagged only in non-schema `*_currency` keys. `npi_pct=npi/valuation` = garbage. → add typed `net_property_income_currency` + `gross_revenue_currency` (mirror purchase_price_currency), default to row currency.
- **`market_valuation` basis conflation** — non-schema `value_basis` (251 rows): consolidated(225)/joint_venture_100pct(17)/effective_interest(9) + PPE-cost-model hotels. Some are 100%-of-JV while ownership<100 (C38U CapitaSky 100% basis/70% owned). → promote `value_basis` to a typed column so JV values aren't summed as consolidated.
- **`tenure_raw` crams** original term + remaining term + expiry + master-lease structure + jurisdiction; `land_tenure` (Freehold/Leasehold) + `lease_term_years`/`lease_expiry_date` capture only part. → add `land_lease_remaining_years` + `master_lease` sub-object; keep tenure_raw.
- **`gla`/`nla`/`gfa`/`area_unit` force heterogeneous size concepts** — hospitality=keys/rooms, accommodation=beds, DC=MW/IT-load; proxies shoved into gfa (8C8U land→gfa, CY6U owned-floor→gfa). → add `capacity_value` + `capacity_unit` (keys/rooms/units/beds/MW/kW); stop coercing into gfa.
- **`divestment_price`** mixed lifecycle + currency (BUOU 357 Collins=AUD; O5RU held_for_sale=estimated-net basis). → folded out of `sgx_reit_property`; use `status` for lifecycle and `sgx_reit_property_transaction` for sale/proceeds figures.

**B — normalize**
- `country`: USA/United States, The UK/UK, The Netherlands/Netherlands (same as before).
- `category_raw` (85): case/format dup pairs — `Data Centre`/`Data Centres`, `Logistics`/`Logistics & Industrial`, `General Industrial`/`General industrial`, `Nursing Home`/`Nursing home`. → normalized lookup (category(6) already clean).
- `tenure_raw`: case dups `Freehold`(687)/`freehold`(117), `Freehold, Not applicable`(71).
- `original_currency`={IDR,RMB} vs `local_currency`={USD,GBP,AUD,EUR} — two parallel fields, same concept; RMB→CNY.

**C — data-with-no-home**
- **⚠️ DATA LOSS**: A17U's 128 local **AUD** valuations sit in non-schema `local_currency`/`local_currency_value` and **do NOT load** (loader only knows `original_value`). Also `_rmb_valuation_000`(AU8U), `_npi_rmb_million`, `_ema_rental_income_rmb_million`(CRPU). → consolidate all into `original_currency`/`original_value` + new per-figure ccy cols.
- **Tier-B independent valuation**: `alt_value`/`alt_basis` (50 rows: DHLU JPY independent vs SGD audited carrying, BTOU/DCRU/JYEU/UD1U) — no home. → `independent_valuation` + ccy + basis, or `valuation_tiers` jsonb.
- Capacity/operational: `_rooms`(XZL), `_year_last_renovation`, beds/keys/MW, RevPAR/ADR/occupancy — new capacity cols + optional `operating_metrics` jsonb.
- per-property GR% (CMOU/CY6U/ME8U segment donuts) → `gross_revenue_pct`.
- Redundant to DROP: `existing_use`(C2PU 71 == category_raw verbatim); standardize purchase-price provenance onto existing typed cols.

**D — null classification (mostly STRUCTURAL, documented)**
- NPI 93% null, npi_pct 99%, gla 99%, trade_mix 99.8%, nla 55%, gfa 75% — all sub-sector structural, aligned with `columns_never_fillable`. Not misses.
- occupancy 19% null; the 12 `0.0` = documented vacancy/redevelopment (not a fraction bug; all 0–100 scale).
- lease_expiry 77%/lease_term 63% — freehold nulls correct; C38U gives "remaining term" not expiry (computable, not printed).
- ownership 16% — mostly directly-held 100% not restated. market_valuation 3.8% null = JV/equity-accounted/redevelopment absent from audited Portfolio Statement (structural).

**E — suspect**
- DHLU NPI/GR raw JPY/VND beside SGD valuation = **mis-labelled** (root cause = A#1); corrupts any ratio/aggregation.
- `category='Diversified (Commercial)'` (6 rows: C38U Raffles City/Funan/Plaza Sing/Atrium, JYEU Jem) = ad-hoc 7th category — decide canonical or remap.
- UD1U p41 GRI donut has an AR-level error (swaps divested Il·lumina) — extraction correctly used card figures; no bad value landed.
- JYEU legitimately mixes sqm & sqft within one report (per-row `area_unit` correct) — confirms area_unit must stay per-row, never report-level.

### performance
**A — conflation / split**
- **`net_distributable_income` vs `distribution_paid` on DIFFERENT bases** → retention formula breaks: Q5T negative (−7,426k), K71U 33.7%, CMOU 93.9%, OXMU 71.1%. Causes: Q5T NDI excludes capital-gains top-up in distribution_paid; K71U NDI is a rollforward total (opening balance 107,871k contaminates); M1GU NDI holds declared amount not available-income. → add `distributable_income_basis`; standardize NDI = "income available for distribution"; only compute retention where bases match.
- **`wale` mixes by-NLA vs by-GRI/revenue** with no flag (JYEU stored 7.2 NLA though 4.9 GRI exists; AU8U 2.1 GRI vs 2.6 NLA). → add `wale_basis`.
- **`interest_coverage_ratio`** incl/excl perpetual distributions (CY6U, O5RU) → `icr_basis`.
- **`cost_of_debt`** all-in vs excl-amortisation (BMOU 4.2 vs 5.0 incl; OXMU excl) → `cost_of_debt_basis`.
- **`aggregate_leverage`** gross aggregate-leverage vs net-gearing (MXNU/XZL/CY6U store gross but note net) → `leverage_basis`.
- **`dpu`** stub/part-year not comparable to full-year (8C8U 1.739 = post-listing stub) → `dpu_is_full_year` flag.
- **`distribution_record.period`** 4 inconsistent free-text formats + K71U double-lists overlapping segmentations + A17U/T82U mix paid-in-year vs declared-for-year → normalize to {period_start, period_end, label} + split declared vs paid.
- **`distribution_record.ex_date`/`pay_date` DEAD** — 89/89 null across all 37 (ARs don't disclose per-tranche dates) → drop from jsonb shape.
- Per-figure currency NOT needed here (each row single-currency) — negative finding.

**B — normalize**: `distribution_basis` clean (4 enum values) — only fix the **mislabels** (K71U→rollforward, Q5T/CMOU not "retention"). `currency`, `date` clean.

**C — data-with-no-home** (disclosed by ~all, propose new columns): `fixed_rate_debt_pct`/hedge ratio; `gross_borrowings` + ccy; `distribution_yield`; `credit_rating`; `rental_reversion_pct`; `perpetual_securities` + `perpetual_distribution`; `debt_headroom`; `di_per_unit` (distributable-income/unit, distinct from paid dpu); hospitality KPIs RevPAR/ADR/AOR (occupancy substitute for hospitality) → jsonb; `distribution_components` jsonb {taxable, tax_exempt, capital}.

**D — null classification / MISSES**
- **M44U = CONFIRMED MISS (recover 6):** aggregate_leverage **40.7%**, ICR **2.9x**, nav **S$1.31**, WADM **3.8y**, wale **2.8 NLA/2.7 rev** (all parsed **p5**); cost_of_debt **3.57%** (Note 18, **p198**). + portfolio_occupancy likely on same dashboard.
- **M1GU = MISS:** `adjusted_distributable_income` **S$43.83m** (adjusted DPU 3.90c, p20) — not captured.
- wale other nulls: HMN/Q5T genuine N/A (hospitality); **T82U miss** (WALE by segment office 3.80/retail 2.42, p27); **CY6U likely miss**.
- portfolio_occupancy: M44U/8C8U possible miss; J85/Q5T N/A (hospitality).
- **`adjusted_distributable_income` DROP candidate** — but recover M1GU first (it's a real method-2 disclosure).
- distribution_paid 15 nulls well-classified (deliberate basis). J91U unitholders 1 null — low-pri recover.

**E — suspect**
- Q5T/K71U/CMOU spurious "retention" = basis artifacts (A) — individually source-correct, pair not subtractable. CMOU = partial-year (suspended then resumed), reclassify.
- **BTOU audit-trail defect**: stored dpu=0.0 (correct, suspended) but `_notes` claims "Stored dpu=1.44" → fix note; move 1.44 to `di_per_unit`.
- D5IU cost_of_debt 8.17% outlier (IDR debt) — spot-check. OXMU 71% retention — verify.
