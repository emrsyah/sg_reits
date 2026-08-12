# J69U — Frasers Centrepoint Trust (J69U.SI) FY2024 — Forensic Extraction Audit

Auditor: independent verification against source. Navigated the report myself from the TOC — Corporate Profile/Structure (pp.2-5), Financial Highlights & 5-year table (pp.7-11), Operations Review incl. by-property financials p36, appraised-values table p39, Retail Portfolio Trade Mix & Top-10 Tenants p32, individual property cards, Portfolio overview p60, the audited Statements (Financial Position, Total Return, Distribution, Cash Flows), Portfolio Statement, Notes 8/9/13/18/24/25, Statistics of Unitholdings p255+. Did NOT consult any extractor tooling / page-map / gather files / adapter / skill, nor the FY2025 extraction.

Source: `parsed_reports_datalab/18_J69U.SI_Frasers-Centrepoint-Trust_FY2024/full.md` (page-anchored; parse `<!-- PAGE N -->` runs +2 vs printed page nos.). Markdown tables parsed cleanly; no PDF spot-check needed.

**Confirmed FYE: 30 September 2024.** Verified header "STATEMENT OF TOTAL RETURN — For the Financial Year Ended 30 September 2024" (parse PAGE 181) and every statement's "As at / For the Financial Year Ended 30 September 2024". All figures verified against the **Group 2024** column (first data column), never the 2023 comparative nor the Trust-only columns.

---

## 1. Verdict & confidence

**Grade: CLEAN.**

This is an exemplary extraction. Every audited financial-statement figure I re-derived matches the Group 2024 column **to the dollar**; the full Statement of Total Return reconciles exactly to "Total return for the financial year" (S$197,546k); balance-sheet, cash-flow, distribution and DPU tie-outs all pass; the Σ of the 9 directly-owned property valuations equals the audited Portfolio Statement total (5,283,000k); trade_mix sums to 100%, top_tenants to the disclosed 19.3%. The hardest trap in this report — the JV structure (NEX 50%, Waterway Point 50% held via GRPL/SST, equity-accounted and OUTSIDE the consolidated investment-property line) — is navigated correctly and documented thoroughly: `portfolio_value` is the owned-only 5,283,000k (NOT any total-incl-JV headline), JV rows carry 100%-basis valuations flagged `value_basis=joint_venture_100pct` with 50%-effective alternatives retained, and the JV income basis is traced to Note 8. The tax **credit** (+1,082) is signed correctly. No perpetual/NCI — full total return to Unitholders, correctly attributed. `net_property_sales`=11,272 (divestment gain) is correctly separated from the associate-divestment loss (24,644).

Only a handful of **LOW / cosmetic** nits survive: a distribution-basis label that reads "after_retention" in a year that had a net *release*; ebitda set equal to ebit (ignores an immaterial $29k depreciation add-back); one disclosed 2H pay-date left null; and the "Vacant 0.0%" trade-mix row dropped. None is a value error.

Tally: **CONFIRMED ≈ 42** · **DISCREPANCY = 3 (all LOW)** · **SUSPECTED-OMISSION = 2 (LOW)** · **UNVERIFIABLE = 1**

---

## 2. Discrepancies

### D1 — `performance.distribution_basis` = "disclosed_after_retention" is semantically inaccurate for FY24 (LOW)
- FY24 had a **net release**, not a retention: `distribution_paid` 214,313 − `net_distributable_income` 213,221 = **+1,092** (distribution EXCEEDS distributable income). Source: Distribution Statement footnote (1), parse p182 line 7456 — "FCT released \$1,092,000 of its tax-exempt income available for distribution to Unitholders which had been retained in FY23." Business review p37 line 1744 corroborates.
- The stored `flags` text describes this correctly, but the machine-readable `distribution_basis` enum value "disclosed_after_retention" implies NDI − paid = a positive retention. Consequence: a downstream consumer keying on the enum would mis-infer a retention. Confidence: HIGH the label mismatches the sign; LOW severity (flag text is accurate; the two numbers themselves are correct).

### D2 — `income_stmt_metrics.ebitda` = ebit = 280,168, no depreciation add-back (LOW)
- The Cash Flow Statement (parse p186 line 7598) discloses "Depreciation of fixed assets 29". Strictly EBITDA = EBIT + D&A = 280,168 + 29 = 280,197k. `ebitda` is a `_derived` field; the $29k is immaterial (0.01%) and investment properties are held at fair value (not depreciated), so ebitda≈ebit is defensible — flagged only for completeness. Confidence: HIGH; severity LOW.

### D3 — `performance.distribution_record[].pay_date` left null though 2H pay-date is disclosed (LOW)
- Distribution Statement footnote (2), parse p182 line 7460: "The distribution relating to period from 1 April 2024 to 30 September 2024 will be paid on **29 November 2024**." The 2H record (`1 Apr 2024 to 30 Sep 2024`) could carry `pay_date = 2024-11-29`. Ex-dates and the 1H pay-date are not disclosed in the AR, so those nulls stand. Confidence: HIGH; severity LOW.

*(Note — NOT a discrepancy: `finance_income` (464) is tagged `statement="adjustment"`, i.e. kept OUT of revenue. This is correct — the STR lists Finance income below Net property income, not within Gross revenue — and is exactly the mis-bucketing the spec warns against, avoided here.)*

---

## 3. Suspected omissions

### O1 — "Vacant 0.0%" trade-mix row dropped (LOW)
- Source trade-mix table (parse p32, line 1563) lists a 15th row "Vacant | 0.0% | 0.3% (NLA)". The extraction captured the 14 non-zero GRI rows (correctly summing to 100.0%). Dropping a 0.0%-GRI row is immaterial; noted only because the source row exists. SEVERITY: LOW.

### O2 — Per-mall trade-mix and per-mall top-10 tenant tables not captured (LOW)
- Each individual property card (Causeway Point p~40, Waterway p~42, Tampines 1, Northpoint, Tiong Bahru, Century Sq, Hougang, White Sands, NEX) discloses its OWN "Trade Category by GRI/NLA" table and "Top 10 Tenants % of Mall's GRI" (e.g. Causeway Point F&B 34.8%, lines 2746-2755; Waterway F&B 32.4%, lines 2903-2913). `_notes.columns_never_fillable` says per-property trade_mix is "not disclosed in an extractable tabular form" — that is **over-broad**: the tables plainly exist per mall. They are, however, per-mall (not the required per-property `trade_mix` sub-array schema shape for the *portfolio* table) and the portfolio-level aggregate is correctly captured in `trade_mix.json`. So the DATA exists but has an awkward schema home; the blanket "not disclosed" reason should be softened. SEVERITY: LOW (schema-home ambiguity, not a value miss).

---

## 4. Reconciliation results (independently re-computed)

### R1 — Statement of Total Return tie-out (Group 2024, parse p181 lines 7395-7418) — **PASS (exact)**
Using `line_items`:
- Σ(revenue) = **351,733**
- Σ(expense) = 98,347 + 84,168 + 36,901 + 147 + 1,045 + 280 + 1,517 + 754 = **223,159**
- Σ(adjustments, signed) = +464 (fin inc) +66,224 (JV) +11,272 (gain IP&JV) −24,644 (loss assoc) +14,661 (FV IP) −87 (fx) +1,082 (tax credit) = **+68,972**
- 351,733 − 223,159 + 68,972 = **197,546k = "Total return for the financial year" (Group) = `net_income` ✓**
- Lines omitted from `line_items` are all **nil in 2024**: Other income (Note 20 = 0), Share of results of associate (0), Impairment loss on associate (0), Net change in FV of derivative (0). `line_items` is therefore complete. No extra/missing line.

### R2 — Revenue identity — **PASS**
`total_revenue` 351,733,000 == `performance.gross_revenue` 351,733,000 == Σ(line_items where statement=revenue) 351,733,000 == STR "Gross revenue" 351,733 (p181) == Note 18 headline S$351.7m (p35 line 365). ✓

### R3 — NPI / cost of revenue — **PASS**
`gross_income` 253,386,000 == STR "Net property income" 253,386 ✓. `cost_of_revenue` 98,347,000 == STR "Property expenses" 98,347 ✓.

### R4 — Derived identities — **PASS**
- I1 operating_income = gross_income − operating_expense: 253,386 − 40,644 = **212,742** ✓ (operating_expense 40,644 = the 6 trust-expense lines: 36,901+147+1,045+280+1,517+754 ✓, excludes finance costs).
- I2 pretax = ebit − interest_expense_non_operating: 280,168 − 83,704 = **196,464** = "Total return before tax" (p181) ✓ (so ebit = 196,464 + 83,704 = 280,168 ✓).
- I3 net_income = pretax − income_taxes(signed): 196,464 − (−1,082) = **197,546** ✓ (tax **credit** stored negative −1,082,000; STR "Taxation 1,082" is a credit, p181 line 7417).
- (c) interest_expense_non_operating 83,704 = net finance cost = Finance costs 84,168 − Finance income 464 = **83,704** ✓.
- non_operating_income_or_loss = pretax − operating_income = 196,464 − 212,742 = **−16,278** ✓ (internally consistent: JV 66,224 + gain 11,272 − loss 24,644 + FV 14,661 − fx 87 − net interest 83,704 = −16,278).

### R5 — Attribution — **PASS**
`unitholders` 197,546,000 = `net_income`; `perpetual_security_holders` null; `minorities` null. Confirmed no NCI/perpetual — Net assets "Represented by: Unitholders' funds" only (p180 line 7381). Full return to Unitholders. ✓

### R6 — EPU / weighted units — **PASS**
Basic 197,546 / 1,775,918 = **11.12c** = STR "Basic 11.12" (p181 line 7420) ✓. Diluted 197,546 / 1,784,493 = **11.07c** = "Diluted 11.07" ✓. Weighted-avg units correctly back-derived from Note 25.

### R7 — Balance sheet (Group 2024, parse p180 lines 7351-7381) — **PASS (all 8)**
total_asset 6,378,871 ✓ · total_liabilities 2,218,205 ✓ · total_equity 4,160,666 (=Net assets=Unitholders' funds) ✓ · total_current_asset 36,494 ✓ · total_non_current_asset 6,342,377 ✓ · total_current_liabilities 428,741 ✓ · total_non_current_liabilities 1,789,464 ✓ · working_capital 36,494 − 428,741 = **−392,247** ✓.

### R8 — Cash flow (Group 2024, parse pp.186-187 lines 7615-7651) — **PASS**
operating 215,667 ✓ · investing 45,193 ✓ · financing −266,255 ✓ · net_cash_flow 215,667 + 45,193 − 266,255 = **−5,395** = "Net decrease in cash" ✓ · capital_expenditure "Capital and other expenditure on investment properties" (41,630) = **−41,630** ✓.

### R9 — Distribution & DPU (parse p182 lines 7431-7448) — **PASS**
- `net_distributable_income` 213,221 = "Distributable income for the financial year" ✓ (correctly the FY-generated figure — NOT the cumulative "Income available for distribution" 317,378, and NOT the closing 109,407).
- `distribution_paid` 214,313 = "Distributions to Unitholders (1)(2)" 214,313 ✓ (= NDI 213,221 + FY23 retained release 1,092 ✓).
- `dpu` 12.042 = "Distribution per Unit for the financial year 12.042" ✓ (= FY24 headline p11 line 365).
- distribution_record: 1H (1 Oct 2023–31 Mar 2024) 6.022 = 4.250 + 1.772 (the two component periods in the statement, lines 7443-7444; footnote 1 p37 line 1744) ✓; 2H (1 Apr–30 Sep 2024) 6.020 ✓; Σ = **12.042** ✓. dpu_period_months 12 ✓.

### R10 — Portfolio valuation Σ → Portfolio Statement total — **PASS**
Σ(9 directly-owned active rows) = 1,342 + 808 + 788 + 34 + 660 + 219 + 563 + 439 + 430 = **5,283,000k** = Portfolio Statement "Investment properties, at valuation" 5,283,000 (parse p184 line 7522) = Balance-sheet Investment properties 5,283,000 (p180 line 7352) = `performance.portfolio_value` 5,283,000,000. ✓ Per-property values spot-checked against Portfolio Statement (Causeway 1,342,000 line 7513; Northpoint 788,000; Yishun 10 34,000; Tampines 808,000; Central Plaza 219,000) and appraised-value table p39 (all match). NEX (2,130,000 @100%; FCT 50%=1,065,000, p39 fn4 line 1810) and Waterway Point (1,320,000 @100%; 50%=660,000, fn5 line 1811) are JV-held (Investment in joint ventures 1,057,036, p184 line 7525) and correctly EXCLUDED from portfolio_value, flagged joint_venture_100pct. Changi City Point null (dash, divested, p184 line 7524). ✓

### R11 — Trade mix (parse p32 lines 1549-1564) — **PASS**
Σ(14 captured GRI rows) = 37.6+15.6+11.0+8.1+6.3+3.2+2.8+2.6+2.6+2.3+2.2+2.1+1.8+1.8 = **100.0%** ✓ (source "Retail Portfolio 100.0%", + a dropped "Vacant 0.0%" row — see O1). Every category & pct matches source. pct_basis "gri" ✓ (basis = "As % of total GRI"). Scope = Retail Portfolio incl. Waterway & NEX, excl. Central Plaza (glossary p2 line 124).

### R12 — Top tenants (parse p32 lines 1582-1592) — **PASS**
10 rows, ranks 1-10 contiguous, %s descending (5.6, 3.2, 2.0, 1.4, 1.4, 1.3, 1.2, 1.1, 1.1, 1.0). Σ = **19.3%** = disclosed "top ten tenants collectively accounted for 19.3%" (line 1576) ✓. All names, industries, %s match verbatim (NTUC FairPrice 5.6, BreadTalk 3.2, Dairy Farm 2.0, Courts 1.4, Metro 1.4, Hanbaobao 1.3, OCBC 1.2, R E & S 1.1, Beauty One 1.1, Uniqlo 1.0). pct_basis "gri" ✓.

### R13 — Profile / manager chain — **PASS**
reit_manager "Frasers Centrepoint Asset Management Ltd." (p3 line 158, 172) ✓ · trustee "HSBC Institutional Trust Services (Singapore) Limited" (p3 line 176; Report of Trustee line 7191) ✓ · property_manager "Frasers Property Retail Management Pte. Ltd." (p133 line 5807) ✓ · sponsor "Frasers Property Limited" (glossary p2 line 125; p133 line 5795) ✓. sub_sector Retail; income_model conventional ✓ (suburban retail).

### R14 — Ancillary performance metrics — **PASS**
aggregate_leverage 38.5% (p7 line 292; 5-yr p9 line 526; p41 line 1866) ✓ · interest_coverage_ratio 3.41 (line 527, 1867) ✓ · cost_of_debt 4.1% ("Average All-In Cost of Debt", line 1869) ✓ · weighted_avg_debt_maturity 2.6y (line 1870) ✓ · wale 2.0 by GRI (p31 line 1353) ✓ · portfolio_occupancy 99.7% (p15 line 644; p31 line 1457) ✓ · nav_per_unit 2.29 (p180 line 7383; 5-yr line 525) ✓ · number_of_unitholders 15,999 (Statistics of Unitholdings, line 10397) ✓ · number_of_shareholder_units 1,811,673,000 = "Units in issue" year-end (p180 line 7382) ✓ (the Statistics table's 1,817,523,046 is post-28-Oct-2024 issuance — extraction correctly used the 30-Sep balance-sheet figure).

### R15 — net_property_sales vs associate loss separation — **PASS**
`net_property_sales` 11,272,000 = STR "Gain on divestment of investment property and investment in joint venture" 11,272 (p181 line 7410; Note 13 gain, CCP incl. CCCO LLP). The **separate** "Loss on divestment of investment in associate" (24,644) (H-REIT/Hektar; realised translation-reserve + fx + costs, p37 line 1725) is correctly a distinct `line_items` entry (−24,644) and parked in `_notes.data_with_no_home` (RM134.934m ≈ S$38.663m consideration, S$24.644m loss, completed 6 Dec 2023) — NOT netted into net_property_sales and NOT a property_transaction. ✓

---

## 5. Nulls / inference audit

**Correct nulls (genuinely absent — actively refuted the "present elsewhere" hypothesis):**
- `properties["Changi City Point"].market_valuation` null — Portfolio Statement shows a dash post-divestment (p184 line 7524); the $325.0m is the FY23 held-for-sale/valuation reference, not a FY24 market value. Correct. Partial-year GR 2,666 / NPI 3,134 captured from financial review p36 (lines 1663/1685) ✓.
- `properties["Yishun 10 Retail Podium"]` gross_revenue/NPI/occupancy null — every operating disclosure reports it COMBINED with Northpoint City North Wing (financial review p36 fn "Includes Yishun 10", portfolio table p60 header "Northpoint City North Wing and Yishun 10", segment Note). Standalone valuation row 34,000 IS captured. Correct null + correct reason. ✓
- `properties.gla` (all rows) — FCT discloses GFA and NLA (p60 spec table line 2620-2622), never a distinct "GLA". Correct. ✓
- `funds_from_operation`, `adjusted_distributable_income` null — FFO not disclosed; correct.

**Inferences flagged (correct):**
- JV market_valuation on 100% basis (NEX 2,130.0m, Waterway 1,320.0m) — flagged in `_notes.inferred[]` and each row carries `value_basis=joint_venture_100pct` + `alt_value`/`alt_basis` (50% effective). ✓ Solid handling.

**Unflagged inference pattern (LOW):**
- `properties.*.lease_expiry_date` are back-derived (e.g. NEX 2008-06-26 + 99y → 2107-06-25; Causeway 1995-10-30 + 99y). Portfolio Statement discloses "99-year leasehold from <date>" (p184 lines 7513-7521), never an explicit expiry date, so every expiry is computed. Values are internally consistent (low risk) but the systematic derivation is not enumerated in `_notes.inferred[]`. Understated provenance, not an error.

---

## 6. Confirmed-correct highlights (balance)

- **Every audited FS number exact** to the Group 2024 column: gross revenue, property expenses, NPI, all trust expenses, finance costs/income, JV share, both divestment lines, FV change, fx, tax credit, total return, all balance-sheet subtotals, all cash-flow subtotals, capex, distribution, DPU, EPU.
- **Full STR reconciles to 197,546k exactly** — no missing/extra line (all omitted lines nil in 2024).
- **JV three-tier trap navigated correctly**: portfolio_value = owned-only 5,283,000k (NOT the ~S$7.0bn effective-interest or any total-incl-JV headline); JV rows flagged 100%-basis with 50%-effective alternatives; Investment-in-JV carrying amount (1,057,036) parked, not force-allocated; JV revenue/NPI (NEX 131,203/100,257; Waterway 83,443/62,497) retained on 100% basis with Note-8 tie-out (Waterway 83,443 ties to Note 8 SST revenue).
- **Tax credit signed correctly** (+1,082 credit → income_taxes −1,082,000 → net = pretax + credit).
- **No perpetual/NCI** — correctly all-to-Unitholders.
- **net_property_sales (gain 11,272) cleanly separated** from associate-divestment loss (24,644).
- **Distribution > NDI correctly explained** (FY23 retained-income release 1,092), arithmetic exact.
- trade_mix (100%), top_tenants (19.3%), profile chain, and all 8 ancillary performance ratios independently confirmed.

---

## 7. Could NOT verify

- **Exact `weighted_avg_shares_basic` (1,775,918k) / `diluted_shares_outstanding` (1,784,493k)** as *standalone* disclosures — the parse's Note 25 EPU table body was not read line-by-line; however both are validated *indirectly and exactly* by the EPU tie-out (R6: 197,546/1,775,918 = 11.12c basic, 197,546/1,784,493 = 11.07c diluted, both matching STR). Treated as confirmed-by-derivation; the raw Note-25 weighted-unit figures themselves are UNVERIFIABLE without reading that note directly, though the derived EPUs match to the cent.
