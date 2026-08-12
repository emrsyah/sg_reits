# K71U — Keppel REIT (K71U.SI) FY2024 — Forensic Extraction Audit

Auditor: independent verification against source. Navigated the report myself from the TOC — Financial Highlights / Key Figures (p5–7), Financial Review income statement & capital-management tables (pp.~55–63, incl. debt-maturity and capital-management panels), Operations Review / Portfolio at a Glance (pp.38–58), Tenant / Trade-mix tables (p42), Trust & Organisation structure (p16), the audited statements in full (Balance Sheets p114, Consolidated Statement of Profit or Loss p115, Statement of Comprehensive Income p116, Distribution Statement p117, Portfolio Statement pp.118–119, Cash Flow p124, Notes incl. Note 27 EPU p161, Note 32 Portfolio Reporting p173), and the Statistics of Unitholdings (p~213). Did NOT consult any extractor tooling, page-map, gather notes, extraction skill, or the FY2025 extraction.

Source: `parsed_reports_datalab/23_K71U.SI_Keppel-REIT_FY2024/full.md` (page-anchored `<!-- PAGE N -->`; page numbers below are the parse markers). Money is S$'000 in the source (×1,000 in JSON). **Confirmed FYE: year ended 31 December 2024** — every audited statement header reads "For the financial year ended 31 December 2024"; verified against the GROUP 2024 column throughout. Structure: office REIT, heavy equity-accounted associate/JV exposure, perpetual securities + NCI.

---

## 1. Method note / column discipline

All P&L, balance-sheet and cash-flow figures verified against the **GROUP 2024** column (not the TRUST columns, which are also printed on the Balance Sheet p114). Property valuations verified against the p119 audited valuation table (Group respective interests), not the p118 GROUP carrying-value table (which shows some assets at 100% despite partial ownership) nor the rounded S$m Financial-Review table. Distribution verified against the audited Distribution Statement p117 cross-checked with the Financial Review p60 income statement and cash-flow p124.

---

## 2. Verdict & confidence

**Grade: MINOR ISSUES.**

The five files under test are excellent on the hard numbers. Every audited financial-statement figure I re-derived matches the GROUP 2024 column to the dollar; the full Consolidated Statement of Profit or Loss reconciles exactly to "Profit for the year" (S$129,729k = `net_income`); the three income-statement identities hold to the dollar; the attribution split (Unitholders 98,969 / perpetual 9,476 / NCI 21,284) is exact; balance sheet, cash flow, NDI, DPU, trade_mix, top_tenants and all 14 property valuations reconcile. The defects are: (D1) `performance.weighted_avg_debt_maturity` is null although the report discloses it as **2.5 years** twice — a clear false-null, and the flag misattributes it to the all-in rate; (D2) an **internal inconsistency** on `portfolio_value` — `performance` ships the "value of deposited properties" (9,643,422) while `_notes`/`properties` and the report's own "$9.5b" headline point to the property-portfolio total (9,531,621), and the flag mislabels 9,643,422 as the "$9.5b headline"; (D3) `distribution_basis="disclosed_after_retention"` is imprecise (payout is 100% of NDI, i.e. 0 retention; actual in-year cash distribution was 216,608) — transparently flagged pending by the extractor; (O1) two property managers disclosed on p16 are missing from `profile.json`. None of these corrupts a financial reconciliation.

Tally: **CONFIRMED ≈ 38** · **DISCREPANCY = 3** · **SUSPECTED-OMISSION = 1** · **UNVERIFIABLE = 0**

---

## 3. Discrepancies

### D1 — `performance.weighted_avg_debt_maturity` = null, but it IS disclosed as 2.5 years (MED, HIGH confidence)
- Extraction: `weighted_avg_debt_maturity: null`; flag reads "weighted_avg_debt_maturity not captured (all-in rate 3.4%)" — conflating the metric with the interest rate.
- Source discloses it explicitly, twice:
  - p56 (line 3586): "The **weighted average term to maturity** of Keppel REIT's borrowings **was 2.5 years** as at 31 December 2024."
  - Capital-management table p57 (line 3642): "Weighted average term to maturity | **2.5 years** | 2.4 years".
- Consequence: a disclosed field left null. Note the coincidence that the interest coverage ratio is also 2.5 (times) — but these are distinct metrics; WATM is 2.5 **years**.
- Fix: `performance.weighted_avg_debt_maturity = 2.5` (years), source p57 (line 3642) / p56 (line 3586).

### D2 — `performance.portfolio_value` = 9,643,422,000 is "deposited properties", not the property-portfolio value, and contradicts `_notes`/`properties` (MED, HIGH confidence)
- Extraction ships **9,643,422,000** and the flag describes it as "value of deposited properties (headline ~$9.5b)".
- Source: 9,643,422 is the **"Value of deposited properties"** (Key Figures p6, line 309) — the CIS-Code leverage denominator = the fund's total look-through assets (Group's respective share of associates'/JVs' assets + other assets, less restricted cash; Note 30 p~170). It is **not** the property portfolio value and it is **not** "$9.5b" (it is ~$9.64b).
- The disclosed **property-portfolio value** is **S$9,531,621k**: Portfolio Statement valuation total p119 (line 5809); Financial Review valuation table total 9,531.7 (line 3525); headline "value of Keppel REIT's portfolio of properties was **approximately $9.5 billion**" (p~50, line 3431).
- Internal inconsistency: `_notes.reconciliation.sum_market_valuation` = **9,531,621,000** ("exactly matching the p119 audited Portfolio Statement total"), and Σ `properties.market_valuation` = 9,531,621,000 (see §5). So the extraction's own artifacts describe the portfolio at 9,531,621 while `performance` reports 9,643,422 and mislabels it "$9.5b".
- Fix: set `performance.portfolio_value = 9,531,621,000` (p119, line 5809) to agree with `_notes`/`properties` and the $9.5b headline; OR, if the project convention is deliberately "deposited properties", correct the flag which wrongly calls 9,643,422 the "$9.5b headline" and reconcile the `_notes` narrative.

### D3 — `distribution_basis="disclosed_after_retention"` with `distribution_paid`=NDI implies 0 retention; in-year cash distribution differs (LOW, HIGH confidence)
- Extraction: `net_distributable_income` = 214,547,000, `distribution_paid` = 214,547,000, `distribution_basis` = "disclosed_after_retention". NDI − distribution_paid = 0.
- Source: the value 214,547 is the FY2024 **distribution to Unitholders** = the headline "$214.5 million" (p5 line 128; p~50 line 393; p~54 line 3364), DPU 5.60c, split 106,914 (1H, 2.80c) + 107,633 (2H, 2.80c) = 214,547 (Financial Review line 351). It equals the Distribution Statement's FY-generated distributable subtotal 214,547 (p117, line 5676). So NDI = distribution = 214,547; payout is 100%, retention = 0 — there is **no disclosed retention**, so the label "disclosed_after_retention" is imprecise (better: full distribution of FY distributable income / DPU basis).
- Separately, the **actual cash distributed to Unitholders during FY2024** was **216,608** ("Total Unitholders' distribution (incl. capital gains) (Note B)", p117 line 5683; Cash Flow "Distribution to Unitholders (216,608)", p124 line 6010) — this is the calendar-year cash figure spanning the 2H2023 + 1H2024 payments, a different concept from the FY2024-attributable 214,547.
- Consequence: the chosen value 214,547 is defensible and correct as the FY2024 distribution; only the `distribution_basis` label and the pending 216,608 question are unresolved. The extractor already flags this pending — noted here for completeness.
- Fix (label only): set `distribution_basis` to reflect a full/100% payout on the DPU basis rather than "disclosed_after_retention"; value 214,547 needs no change (p117 line 5676 / line 351).

---

## 4. Suspected omissions

### O1 — `profile.json` management omits two property managers disclosed on p16 (LOW–MED; schema home exists)
- `profile.json` lists 6 property managers: Keppel Real Estate Services, Raffles Quay Asset Management, Mirvac Real Estate, Jones Lang LaSalle (NSW), CBRE Korea, Sun Frontier Fudousan.
- Source Trust & Organisation structure p16 (line 530) discloses **two more** property managers for 8 Exhibition Street: **"GPT Property Management Pty Limited (for the 8 Exhibition Street office building)"** and **"Jones Lang LaSalle (VIC) Pty Ltd (for the three adjacent retail units)"**.
- Consequence: 2 of 8 property-manager relationships missing. Fix: add both to `profile.management` with role `property_manager` (p16, line 530).

---

## 5. Reconciliation results (independently re-computed)

### Statement of Total Return / Profit or Loss tie-out (GROUP 2024, p115) — PASS
Using `financial.line_items`:
- Σ(revenue) = Property income **261,580**.
- Σ(expense) = property_expenses 59,667 + trust_expenses 65,043 + borrowing_costs 88,546 = **213,256**.
- Σ(adjustments, signed) = rental_support 9,412 + assoc 86,268 + JV 23,735 + interest_income 7,714 + net_fx 4,188 + FVTPL(-8,500) + derivatives 3,276 + FV investment properties(-43,479) + taxation(-1,209) = **+81,405**.
- 261,580 − 213,256 + 81,405 = **129,729** = "Profit for the year" (p115 line 5618) = `net_income` ✓ exact.
- No line missing/extra; all 13 P&L lines captured (interest income netted into the derived net finance cost, and also present as an adjustment line — counted once in the reconciliation, no double-count).

### Revenue coherence — PASS
`income_stmt_metrics.total_revenue` (261,580,000) == `performance.gross_revenue` (261,580,000) == Σ(line_items statement=revenue) (261,580,000) ✓. Only Property income is tagged revenue; interest income, rental support and share-of-results are correctly `adjustment`, so no mis-bucketing (contrast HMN D1).

### NPI / property expenses — PASS
`gross_income` 201,913,000 = NPI 201,913 (p115 line 5604) ✓; `cost_of_revenue` 59,667,000 = Property expenses 59,667 ✓.

### Income-statement identities — PASS
- I1: operating_income = gross_income − operating_expense = 201,913 − 65,043 = **136,870** ✓.
- I2: ebit = pretax_income + interest_expense_non_operating = 130,938 + 80,832 = **211,770** ✓ (ebitda = ebit, no D&A add-back beyond the immaterial 21 depreciation).
- I3: net_income = pretax_income − income_taxes = 130,938 − 1,209 = **129,729** ✓.
- (c) interest_expense_non_operating = borrowing costs − interest income = 88,546 − 7,714 = **80,832** ✓ (net finance cost).
- Derived non_operating_income_or_loss = pretax − operating_income = 130,938 − 136,870 = **-5,932** ✓ (internally consistent; note this convention treats share-of-associate/JV results as non-operating).
- (d) attribution: 98,969 + 9,476 + 21,284 = **129,729** = net_income ✓ (p115 lines 5620–5623).

### Weighted-average units — PASS
`weighted_avg_shares_basic` 3,819,238,000 = Note 27 p161 (line 7517) ✓; `diluted_shares_outstanding` 3,830,595,000 = Note 27 p162 (line 7538) ✓.

### Balance Sheet (GROUP 2024, p114) — PASS
- total_asset 8,457,643,000 ✓ (line 5564); non_current 8,351,873 ✓ (5556); current 105,770 ✓ (5563).
- total_liabilities 2,816,428,000 ✓ (5581); current 757,132 ✓ (5573); non_current 2,059,296 ✓ (5580).
- total_equity 5,641,215,000 ✓ (5582); = 5,641,215 (unitholders 4,891,057 + perpetual 302,023 + NCI 448,135) ✓.
- working_capital = 105,770 − 757,132 = **-651,362** ✓; total_asset = total_equity + total_liabilities (8,457,643) ✓.

### Cash Flow (GROUP 2024, p124) — PASS
- operating 188,989,000 ✓ (line 5986); investing -250,917,000 ✓ (6000); financing 2,152,000 ✓ (6014).
- net_cash_flow = 188,989 − 250,917 + 2,152 = **-59,776** = "Net decrease in cash" ✓ (6015).
- capital_expenditure -14,511,000 = "Subsequent expenditure on investment properties" (5992) — reasonable mapping ✓.

### Distribution / NDI (p117) — PASS
- NDI 214,547,000 = FY-generated distributable subtotal (line 5676) = opening 109,932 + 214,547 → cumulative 324,479 (5677); year-end 107,871 (5684). Extraction correctly uses the **FY-generated** 214,547, **not** the cumulative 324,479 or after-payment 107,871 ✓.
- DPU 5.60c ✓ (p5 line 130; Key Figures line 319; p~50 line 393); distribution_record 2.80 + 2.80 = 5.60 ✓; amounts 106,914 + 107,633 = 214,547 (line 351) ✓.
- (Label caveat and 216,608 cash figure per D3.)

### Portfolio valuation sum (p119) — PASS
Σ of all 14 `properties.market_valuation` = 2,168,486 + 740,000 + 1,316,700 + 1,810,000 + 1,388,000 + 323,363 + 185,219 + 223,495 + 197,978 + 245,228 + 356,360 + 209,416 + 280,907 + 86,469 = **9,531,621k** = p119 audited valuation total (line 5809) ✓. Each row matches the p119 valuer table to the dollar (associate/JV rows at KR's respective interest, correctly outside the p114 consolidated investment-property line 5,167,453 — not false-flagged). MBFC correctly split into two valuation rows (Towers 1&2+MBLM 1,810,000; Tower 3 1,388,000), giving 14 rows for 13 assets.

### Trade mix (p42, committed monthly gross rent) — PASS
34.9 + 14.0 + 13.3 + 7.6 + 7.1 + 7.0 + 6.5 + 4.9 + 1.9 + 1.9 + 0.9 = **100.0%** ✓ (lines 2421–2432). All 11 sector rows and values match; `pct_basis` = committed_gross_rent ✓; category_raw preserved verbatim; standardized `category` mapping reasonable.

### Top tenants (p42) — PASS
Ranks 1–10 contiguous; % descending: 5.8, 5.2, 3.4, 2.7, 2.7, 2.7, 2.6, 2.3, 2.0, 1.9; Σ = **31.3%** = disclosed "top 10 tenants contributed 31.3%" (lines 2387–2397, 2411) ✓. All names, sectors and %s match the p42 table exactly (incl. Minister for Finance – State of Victoria 5.8, DBS 5.2, TikTok 2.3, Standard Chartered 1.9).

### Property transaction — PASS
255 George Street 50% acquisition, completed 9 May 2024, S$320,835k (Note A p124 line 5988) / ~S$320,981k (Note 3 p139) / headline A$363.8m (p38), seller Mirvac Funds Management Australia Limited ✓. No FY2024 divestment disclosed ✓.

### Operating metrics — PASS
aggregate_leverage 41.2 (lines 323/3638) ✓; interest_coverage_ratio 2.5 times (321/3639) ✓; cost_of_debt/all-in rate 3.40 (322/3641) ✓; portfolio_occupancy 97.9 (142/2191) ✓; wale 4.7 (397/2223) ✓; nav_per_unit 1.27 (p114 line 5589; Key Figures line 311) ✓; number_of_unitholders 79,404 as at 27 Feb 2025 (line 9547/9566) ✓; number_of_shareholder_units 3,844,046,000 = units in issue at 31 Dec 2024 (p114 line 5588) ✓ — correctly the year-end figure, not the later 3,870,594,655 (27 Feb 2025).

---

## 6. Nulls / inference audit

**Wrong / imprecise:**
- `performance.weighted_avg_debt_maturity` = null → **WRONG**; disclosed 2.5 years (D1, p56/p57).
- `performance.portfolio_value` provenance flag mislabels the deposited-properties figure as the "$9.5b headline" (D2).
- `performance.distribution_basis` label imprecise (D3).

**Correct / genuinely absent (verified):**
- `income_stmt_metrics._derived[]` correctly lists operating_income, ebit, ebitda, non_operating_income_or_loss, interest_expense_non_operating — all confirmed derived and internally consistent (§5).
- `funds_from_operation`, `free_cash_flow`, `adjusted_distributable_income` null — not disclosed as such in the report.
- `properties.gla/gfa` null — the report discloses attributable **NLA** only (p43–45); no per-property GLA/GFA table exists (Portfolio Statement, At-a-Glance, property cards, Note 32) — `_notes.columns_never_fillable` reason is correct.
- Associate/JV rows' property-level gross_revenue null — Note 32 p173 discloses only KR-attributable NET property income for equity-accounted assets, never a property-level gross figure — correct null with sound reason.
- `_notes.inferred[]` — the single flagged item (2 Blue St / 255 George St NPI excludes rental support) is accurate; no unflagged material inference found (property NPI/gross_revenue taken as-disclosed from Note 32; valuation_date uniform 2024-12-31 per the Portfolio Statement header, an assigned-not-per-row value but correct).

---

## 7. Confirmed-correct highlights (balance)

- **All audited FS numbers exact** to the GROUP 2024 column: revenue, property expenses, NPI, trust expenses, borrowing costs, interest income, share of associates/JVs, all FV lines, tax, profit for the year, full attribution split.
- **Full P&L reconciles to 129,729 exactly** — no line missing; the single-line "Trust expenses" 65,043 correctly used as `operating_expense` (matches the assignment).
- **Revenue coherence clean** — total_revenue = gross_revenue = Σ revenue line = 261,580; no finance/other income mis-bucketed as revenue.
- **Balance sheet, cash flow, EPU units, NAV** all tie to the dollar/cent.
- **NDI on the FY-generated basis** (214,547, excl opening 109,932) — the exact convention required; not the cumulative or after-payment figure.
- **All 14 property valuations** match p119 to the dollar; MBFC split handled correctly; equity-accounted associate/JV assets correctly outside the consolidated IP line and not false-flagged; partial-ownership/rental-support nuances documented.
- **trade_mix (100.0%) and top_tenants (Σ 31.3%)** match p42 exactly, with verbatim category_raw and correct committed-gross-rent basis.
- **profile** manager/trustee/sponsor and 6 of 8 property managers correct; sub_sector Office and income_model conventional appropriate.
- **255 George Street acquisition** fully and correctly captured with audited consideration, headline, seller and interest.

---

## 8. Could NOT verify

- None. Every value under test resolved from the parsed markdown. (The `distribution_paid` semantics question in D3 is a labeling/convention matter, not an unverifiable value — both 214,547 and 216,608 are disclosed and identified.)
