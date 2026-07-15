# C2PU — ParkwayLife REIT (C2PU.SI) FY2024 — Forensic Extraction Audit

Auditor: independent verification against source. Navigated the report myself from the TOC (p116/PDF-line 3897): Statements of Financial Position (PDF p63), Statements of Total Return + Distribution Statements (PDF p64), Distribution Note A/B + Statements of Movements (PDF p65), Portfolio Statements (PDF pp66-74), Consolidated Statement of Cash Flows (PDF p75), Notes 15-21 (PDF pp92-94), Note 26 Operating Segments (PDF pp105-106), Statistics of Unitholdings (PDF p210 region), plus the front-half narrative: Overview/Trust Structure (p1-2), Message to Unitholders (p4-6), Financial Highlights (p18), Financial Review (p19), Portfolio Highlights incl. top-10 tenants + asset/geography mix pie charts (p20), Our Portfolio property cards (pp21-31), Significant Events (p33-34), Capital Management (p32-33). Did NOT consult any extractor tooling, page-map, `local://fy2024-gather/*`, `extracted_adapter/`, the FY2025 extraction, or any extraction skill.

Source: `parsed_reports_datalab/32_C2PU.SI_Parkway-Life-REIT_FY2024/full.md` (page-anchored `<!-- PAGE N -->`; marker precedes its page's content). Money is S$'000 in the audited tables, scaled ×1000 to absolute SGD in the JSON.

**Confirmed FYE: year ended 31 December 2024.** Every audited statement carries the header "YEAR ENDED 31 DECEMBER 2024" / "AS AT 31 DECEMBER 2024" and I verified all financials against the **Group** column (2024), never Trust-only.

---

## 1. Verdict & confidence

**Grade: CLEAN.**

This is an exceptionally sound extraction. Every audited financial-statement figure I re-derived matches the Group 2024 column **to the dollar**: the full Statement of Total Return reconciles exactly to "Total return for the year" S$95,041k; the three income identities (I1/I2/I3) hold to the dollar; the balance sheet and cash-flow tie-outs are exact; distribution/NDI/DPU reconcile exactly (NDI 94,419 before retention − 3,000 capex retention = 91,419 distribution_paid); the 75-property valuation sum equals the audited Portfolio total S$2,462,695k **exactly**; trade_mix (asset-type) sums to 100%; the top-10 tenants match name-for-name and %-for-%; and profile / cross-artifact fields agree. The distinguishing traps for this REIT — the before-vs-after-retention NDI convention, the single-class (no perp/NCI) attribution, the asset-type (not retail-sector) trade mix, and the healthcare/master-lease profile — were **all navigated correctly**.

Residual nits are trivial and none is a value error on a disclosed figure: (a) a benign headline-vs-audited inconsistency in `performance.portfolio_value` (2,460,000,000 headline vs 2,462,695,000 audited/`_notes`); (b) one derived distribution-record figure (Nov-Dec DPU 2.38c) not explicitly flagged as inferred; (c) `portfolio_occupancy`=100% is a defensible simplification (Malaysia MOB is 31%, but 0.2% of value); (d) the p20 geographic asset-value pie is not carried in trade_mix (orthogonal; no clean schema home).

Tally: **CONFIRMED ≈ 45** · **DISCREPANCY = 1 (LOW)** · **SUSPECTED-OMISSION = 1 (LOW)** · **UNVERIFIABLE = 1 (LOW)**

---

## 2. Discrepancies

### D1 — `performance.portfolio_value` = 2,460,000,000 is the rounded headline, not the audited figure used elsewhere (LOW)
- `performance.json` ships **2,460,000,000** (headline "approximately S$2.46 billion", p1 line 17 / p18 line 1037 / p19 line 1303).
- BUT `_notes.json` reconciliation and `properties.json` both use **2,462,695,000** = the audited Portfolio Statement total "Total investment properties, at valuation" (PAGE 73, line 4421), and the SFP investment-properties carrying amount is **2,464,764,000** (PAGE 63, line 4043; = valuation 2,462,695 + straight-line/ROU adjustments 2,069).
- All three are genuinely disclosed and the `performance.flags` text explains the choice, so this is defensible — but performance uses a different number from the sister artifacts. Consequence: a downstream consumer joining performance.portfolio_value to Σ(properties) sees a S$2.695m gap. Severity LOW; confidence HIGH the inconsistency exists.

---

## 3. Suspected omissions

### O1 — p20 geographic asset-value mix (65.1% SG / 28.1% Japan / 6.6% France / 0.2% Malaysia) not captured in trade_mix (LOW)
The Portfolio Highlights page carries **two** "by asset value" pie charts (p20, lines 1393-1407): asset-type (65.3% Hospitals & Medical Centres / 34.7% Nursing Homes) — captured — and geography (65.1/28.1/6.6/0.2) — not captured in trade_mix. The geographic split is well-represented instead via `performance.properties_location` and `_notes.by_country` / `properties.json` (SG 1,603,000 / Japan 690,728 / France 163,107 / Malaysia 5,860), so this is correctly parked rather than lost. No clean trade_mix home for a geography basis. Severity LOW.

---

## 4. Reconciliation results (independently re-computed)

### R1 — Statement of Total Return tie-out (Group 2024, PAGE 64, lines 4087-4101) — **PASS (exact)**
Using `financial.line_items`:
- Σ revenue = 144,848 (property rental income) + 420 (other income) = **145,268**
- Σ expense = 8,671 (property exp) + 14,511 (mgmt fees) + 3,569 (trust exp) + 12,147 (finance costs) = **38,898**
- Σ adjustments (signed) = +1,066 (interest income) + 7,159 (fx gain) + 5,178 (fv derivatives) − 18,037 (fv investment properties) − 6,695 (income tax) = **−11,329**
- 145,268 − 38,898 − 11,329 = **95,041k = "Total return for the year" (Group) ✓ exact.**
No missing/extra line. (Note: `interest_income` and `fx_gain` are tagged `statement:"adjustment"` rather than revenue/expense — correct here, since the AR places them below NPI outside gross revenue; the signed sum still reconciles.)

### R2 — Revenue consistency — **PASS**
`income_stmt_metrics.total_revenue` 145,268,000 == `performance.gross_revenue` 145,268,000 == Σ(line_items revenue) 145,268,000 == Note 15 gross revenue total (PAGE 92, line 5709). Property rental income 144,848 + other income 420 = 145,268 per Note 15 — so including other_income in gross revenue is **correct** (it is inside the Note 15 gross-revenue subtotal, not a below-the-line item). ✓

### R3 — NPI / cost_of_revenue — **PASS**
`gross_income` 136,597,000 == NPI 136,597,000 (PAGE 64, line 4089) == `performance.net_property_income`. `cost_of_revenue` 8,671,000 == "Property expenses" 8,671 (Note 16, PAGE 92, line 5727). ✓

### R4 — Income identities I1/I2/I3 — **PASS (exact)**
- I1: operating_income 118,517 = gross_income 136,597 − operating_expense 18,080 (= mgmt 14,511 + trust 3,569). ✓
- I2: ebit 112,817 = pretax 101,736 + interest_expense_non_operating 11,081. ✓
- interest_expense_non_operating 11,081 = net finance cost = finance costs 12,147 (Note 19) − interest income 1,066. ✓
- non_operating_income_or_loss −16,781 = 1,066 − 12,147 + 7,159 + 5,178 − 18,037. ✓ (operating_income 118,517 − 16,781 = pretax 101,736 ✓)
- I3: net_income 95,041 = pretax 101,736 − income_taxes 6,695 (tax is an expense, stored positive). ✓
- (ebitda = ebit 112,817 — no D&A for a fair-valued REIT; the derived EBIT/EBITDA include the fair-value/fx items, a consistent mechanical derivation, correctly listed in `_derived[]`.)

### R5 — Attribution — **PASS**
`unitholders` 95,041,000 = net_income; `perpetual_security_holders` = null, `minorities` = null. Single-class trust — "Total return for the year" is wholly attributable to Unitholders (PAGE 65 Movements, line 4180). ✓

### R6 — EPU / weighted-average units — **PASS**
Basic & diluted EPU 15.51c (PAGE 94, line 5823); weighted-avg units 612,897k (line 5818) = `weighted_avg_shares_basic`/`diluted_shares_outstanding` 612,897,000. 95,041/612,897 = 15.51c ✓.

### R7 — Balance sheet (Group 2024, PAGE 63, lines 4042-4075) — **PASS (all exact)**
total_asset 2,551,147 ✓; total_liabilities 981,195 ✓; total_equity (net assets) 1,569,952 ✓; total_current_asset 70,827 ✓; total_non_current_asset 2,480,320 ✓; total_current_liabilities 58,640 ✓; total_non_current_liabilities 922,555 ✓; working_capital 12,187 = 70,827 − 58,640 ✓. NAV/unit 2.41 ✓; units 652,371k ✓.

### R8 — Cash flow (Group 2024, PAGE 75, lines 4492-4513) — **PASS**
operating 95,786 ✓; investing (239,934) ✓; financing 147,354 ✓; net_cash_flow 3,206 = 95,786 − 239,934 + 147,354 ✓. capital_expenditure −49,103 = "Capital expenditure on investment properties (49,103)" (line 4496) ✓. (Not the Note-26 segment capex 84,523 — correct choice.)

### R9 — Distribution / NDI / DPU (PAGE 64-65) — **PASS (exact)**
- NDI `net_distributable_income` 94,419 = total return 95,041 + distribution adjustments (624) + rollover 2 (lines 4114-4116). This is the FY-generated income available for distribution **before** the 3,000 capex retention and **excluding** the opening carried-forward 45,264 — exactly the required convention. ✓
- distribution_paid 91,419 = "Income for the year available for distribution to Unitholders" (Note B, line 4118/4166), i.e. **after** the 3,000 capex retention (line 4117). ✓
- NDI 94,419 − distribution_paid 91,419 = **3,000 = disclosed capex retention** — matches `distribution_basis:"disclosed_after_retention"`. ✓
- DPU 14.92c full year (line 4129); split 7.54 (1H, line 4124) + 5.00 (advanced 1 Jul–31 Oct, paid 26 Nov 2024, lines 4125/4131) + 2.38 (1 Nov–31 Dec, residual) = 14.92 ✓. pay_date 2024-11-26 for the advanced tranche confirmed (line 4131).

### R10 — Portfolio valuation sum (PAGE 66-74) — **PASS (exact)**
Σ(`properties.json` market_valuation, 75/75 valued) = **2,462,695,000** = audited "Total investment properties, at valuation" S$2,462,695k (line 4421). By country: SG 1,603,000,000 / Japan 690,728,000 / France 163,107,000 / Malaysia 5,860,000 — each matches the Portfolio Statement sub-totals (SG line 4208; France line 4418; Malaysia line 4420; Japan = 2,462,695 − others = 690,728). ✓ 75 rows = 3 SG hospitals + 60 Japan + 11 France + 1 Malaysia (AR "75 properties", p1/p18/p50). ✓

### R11 — Trade mix (asset value, p20, lines 1395-1405) — **PASS**
Hospitals & Medical Centres 65.3% + Nursing Homes 34.7% = **100.0%** ✓. `pct_basis:"asset_value"` correct (pie legend "by asset value"). Correctly the **asset-type** mix (not retail trade sectors); `category` normalised to "Healthcare & Wellness" with `category_raw` preserving the literal labels. ✓

### R12 — Top-10 tenants (p20, lines 1347-1356) — **PASS**
All 10 ranks match name-for-name and %-for-%: Parkway Hospitals Singapore 59.2 / DomusVi Group 8.0 / K.K. Sawayaka Club 5.2 / K.K. Habitation 4.8 / Fuyo Shoji Kabushiki Kaisha 2.1 / K.K. AlphaBetta 1.9 / Miyako Enterprise 1.6 / K.K. BISCOUSS 1.5 / Riei Co. 1.4 / Medical Corporation Kenkou Choju-kai 1.3. Σ = 87.0%. `pct_basis:"gross_revenue"` matches footnote (1) "Based on Gross Revenue as at 31 December 2024" (line 1360). All `industry` → "Healthcare & Wellness" ✓ (correct for a pure healthcare REIT). Ranks contiguous, descending. ✓

### R13 — Note 26 segment sanity (PAGE 105, lines 6698-6699) — **PASS (with source note)**
Segment GR: Hospitals & Medical Centres 101,864 + Nursing Homes 43,404 = 145,268 ✓; segment NPI 98,011 + 38,586 = 136,597 ✓ — ties to the Statement of Total Return. Geographical revenue (line 6744-6747): SG 101,583 + Japan 43,032 + France 372 + Malaysia 281 = 145,268 ✓. (Source oddity, not an extraction error: Note 26's own "Total return after income tax" 95,036 and "before tax" 101,731 are S$5k below the audited statement's 95,041 / 101,736 — an internal rounding in the segment note; the extraction correctly took the Statement-of-Total-Return values.)

---

## 5. Nulls / inference audit

**Confirmed genuinely absent (correct nulls):**
- `perpetual_security_holders`, `minorities` — single-class trust; no perpetual securities, no NCI. Correct. ✓
- `funds_from_operation`, `free_cash_flow`, `adjusted_distributable_income`, `employee_breakdown` — not disclosed / not applicable. Correct. ✓
- `properties.net_property_income` / `npi_pct` / `gla` / `nla` — per-property NPI and lettable area genuinely not disclosed; Note 26 collapses to 2 asset-type segments (GR/NPI only) and 4 geographies (revenue only); Portfolio Statement has no income columns; cards give "Floor Area" (captured as gfa) not GLA. `_notes.columns_never_fillable` evidence is accurate. I actively hunted the Operations Review / Portfolio Highlights / property cards and confirmed NO per-property NPI or lettable-area figure exists. Correct. ✓
- 71 Freehold properties' lease term/expiry — Portfolio Statement shows "N.A." (Freehold); only the 4 Leasehold rows (3 SG hospitals + Orange no Sato Japan) carry terms. Correct. ✓

**Inferences — reasonableness:**
- `_derived[]` correctly declares the 5 computed income-statement fields (operating_income, ebit, ebitda, non_operating_income_or_loss, interest_expense_non_operating); all derive correctly (R4). ✓
- `distribution_record[2].dpu` = **2.38** (1 Nov–31 Dec) is a **derived residual** (14.92 − 7.54 − 5.00); the AR discloses only the full-year 14.92, the 1H 7.54, and the advanced 5.00 as distributions *paid during* 2024 (the Nov-Dec final was declared/paid in 2025). Sound derivation and it sums correctly, but it is not explicitly flagged as inferred. Minor (LOW).
- `performance.portfolio_occupancy` = 100.0 is an assigned simplification: SG/Japan/France committed occupancy 100% (lines 1421/1466/1484), Malaysia MOB Specialist Clinics 31% excl. car park (line 1534). Flagged in `performance.flags`. Defensible given MOB is 0.2% of value. Minor.

---

## 6. Confirmed-correct highlights (balance)

- **All audited FS numbers exact to the Group 2024 column** — gross revenue, property expenses, NPI, mgmt fees, trust expenses, interest income, finance costs, fx gain, both fair-value lines, tax, total return, EPU, every balance-sheet subtotal, every cash-flow subtotal.
- **Full Statement of Total Return reconciles to S$95,041k exactly**, no line missing or extra.
- **NDI convention navigated correctly** — 94,419 before-retention (not the cumulative 136,683 "amount available", not the after-retention 91,419), and NDI − distribution_paid = the disclosed 3,000 capex retention.
- **Single-class attribution correct** — total return wholly to Unitholders, perp/NCI null.
- **All 75 properties present**, correct 4 countries, correct 2024 valuations, sum = audited 2,462,695,000 to the dollar; 4 Leasehold vs 71 Freehold tenure correctly split; France 11-home DomusVi sale-and-leaseback and the Japan HIBISU TK acquisition captured in property_transactions with correct dates (7 Aug 2024 / 20 Dec 2024) and local-currency prices (¥2,446.2m / €111.2m).
- **trade_mix is asset-type by asset value** (not retail sectors) and **top_tenants all Healthcare & Wellness** — the two sub-sector traps for this REIT, handled correctly.
- **profile correct**: sub_sector Healthcare; income_model master_lease with master_lessee **Parkway Hospitals Singapore Pte. Ltd.** (lines 1417/4444); manager Parkway Trust Management Limited; trustee HSBC Institutional Trust Services (Singapore) Limited; sponsor Parkway Holdings Limited (sole shareholder of the Manager, line 2706).
- **Key metrics confirmed**: aggregate leverage 34.8%, ICR 9.8x, all-in cost of debt 1.48%, WADM 3.5y (all line 303); WALE 15.34y by gross revenue (line 1383); NAV/unit 2.41; unitholders 12,750 (line 6801); DPU 14.92c.
- **Cross-artifact consistency**: property count 75, currency SGD, by-country valuations, manager/trustee/sponsor names all agree across `_notes` / `profile` / `performance` / `properties`.

---

## 7. Could NOT verify

- **`distribution_record` ex-dates and the 7.54c / 2.38c pay-dates** — the Distribution Statement discloses only the advanced-tranche pay date (26 Nov 2024); ex-dates and the other pay dates are not on the audited pages I reviewed (they live in SGXNet announcements). Left null — correct, and unverifiable from the parse. (LOW)
- **Note 26 segment S$5k rounding** (95,036 vs 95,041) is a source-internal artefact; the extraction correctly uses the primary-statement 95,041. Not an extraction defect; noted for completeness.
- **`performance.portfolio_value` headline vs audited** (D1) — both figures are genuinely disclosed; which one "should" ship is a schema-convention call, not a value error resolvable from the report.
