# T82U — Suntec REIT (T82U.SI) FY2024 — Forensic Extraction Audit

Auditor: independent verification against source. Navigated the report myself from the TOC — At a Glance (p10), Financial Highlights (p14-15), Manager's Report / Financial Performance (p22-24 incl. Debt Maturity Profile p23), Property Portfolio (portfolio card p26, Business Sector Analysis charts p27, Top-10 tenant tables p28, Lease Expiry / WALE p29), the audited statements (Statement of Financial Position p107, Statement of Total Return p108, Distribution Statements p109-110, Movements in Unitholders' Funds p111-112, Portfolio Statements p113-115, Consolidated Cash Flows p116-117), Note 7 Interests in JV (p142), Note 27 EPU (p161-162), Note 28 Operating Segments (p163), Statistics of Unitholdings (p292), Corporate Information / property-manager notes (Note 24, p120). Did NOT consult any extractor tooling, page-map, gather notes, or the FY2025 extraction.

Source: `parsed_reports_datalab/37_T82U.SI_Suntec-REIT_FY2024/full.md` (page-anchored). Markdown tables parsed cleanly; no PDF spot-checks needed.

**Confirmed FYE: 31 December 2024.** Every financial figure verified against the **Group 2024** column ("For the financial year ended 31 December 2024"), never the Trust-only column (which differs materially, e.g. Trust gross revenue 415,300 vs Group 463,556, Trust NPI 342,669 vs Group 310,759).

---

## 1. Verdict & confidence

**Grade: MINOR ISSUES.**

The extraction is exceptionally strong on the hard numbers. Every audited financial-statement figure I re-derived matched the Group 2024 column **to the dollar**: the full Statement of Total Return reconciles exactly to "Total return for the year after tax" (S$136,154k), all three balance-sheet subtotal tiers tie, the cash-flow statement ties across all three activities, distribution/DPU/NDI all reconcile, and both the two-way and three-way attribution splits are exact. The two nuanced traps flagged for this REIT were navigated correctly: (a) the P&L combines Unitholders + perpetual holders as one line (126,778) and the extractor correctly split off perpetual (14,013 from the Distribution/Movements statements) to book unitholders = 112,765; (b) NDI = 180,923 is the FY-generated distributable income (excl. the S$54,153 opening carry-forward). Finance/other income are correctly bucketed as `adjustment` (NOT `revenue`), so the gross-revenue cross-check that broke on other REITs is CLEAN here.

The remaining issues are **structural/labeling, not value errors**: `trade_mix` merges the Office-GRI and Retail-GRI sector charts into a single list with an identical `pct_basis: "gri"` and no office/retail distinguisher (so the list sums to ~200% and normalized category names collide); `top_tenants` concatenates two separate Top-10 tables (Office and Retail, on different GRI denominators) into a single non-monotonic rank 1-20 with no segment field; and `portfolio_occupancy` = 95.4 adopts the Office figure as the single portfolio occupancy where the report discloses no blended number. All are flagged in `performance.flags`/`_notes`, and every underlying value is transcribed correctly.

Tally: **CONFIRMED ≈ 40** · **DISCREPANCY = 3** · **SUSPECTED-OMISSION = 2** · **UNVERIFIABLE = 1**

---

## 2. Discrepancies

### D1 — `trade_mix`: Office-GRI and Retail-GRI charts merged with one indistinguishable `pct_basis` (MED)
- Extraction: 26 rows, all `pct_basis: "gri"`, `source_page: 27`. Rows 1-13 are the Office chart, rows 14-26 the Retail chart. All 26 values are transcribed **exactly** (verified below).
- Source (p27): TWO separate donut charts — "Office Portfolio Business Sector Analysis (By Gross Rental Income)" and "Retail Portfolio Business Sector Analysis (By Gross Rental Income)" — each a distinct 100% distribution on a *different denominator* (office GRI vs retail GRI), stated as "for the month of December 2024" (p27 narrative lines: office 52.1% top-two, retail 55.1% top-two).
- Consequence: with a single shared `pct_basis` and no segment/portfolio field, (i) the list sums to ~200%; (ii) normalized category names collide across segments — e.g. "Hospitality & Leisure" appears at 0.7 (office, raw "Hospitality/Leisure") AND 7.2 (retail, raw "Leisure and Entertainment"); "IT & Telecommunications" at 27.4 (office TMT) AND 2.8 (retail Electronics); "Healthcare & Wellness" at 1.4 (office Pharma) + 3.4 (retail Beauty) + 3.1 (retail Fitness). A downstream consumer cannot separate them. Also the basis is monthly (Dec-2024) GRI, not annual — `"gri"` understates that.
- Fix direction (from the report): distinguish the two bases (e.g. `pct_basis: "office_gri"` / `"retail_gri"`, or add a `segment` field), matching the two distinct p27 chart titles. Severity MED (structure), confidence HIGH. No value error.

### D2 — `top_tenants`: two Top-10 tables concatenated into a non-monotonic rank 1-20, single `pct_basis` (MED-LOW)
- Extraction: ranks 1-20, all `pct_basis: "gri"`, `source_page: 28`. Ranks 1-10 = Office Top-10; ranks 11-20 = Retail Top-10. Names, sectors and %s all transcribed **exactly**.
- Source (p28): "OFFICE PORTFOLIO — TOP 10 TENANTS" (% of Total Monthly **Office** GRI) and "RETAIL PORTFOLIO — TOP 10 TENANTS" (% of Total Monthly **Retail** GRI) are two independent tables with different denominators (footnote 3: A$1.00=$0.8804, £1.00=$1.7082).
- Consequence: the continuous rank implies one ranking, but rank 11 (Cold Storage 2.2%) > rank 10 (PayPal 1.5%) because they are on different bases — rank order is misleading, and there is no office/retail segment marker. `revenue_pct` values are correct but not comparable across the 1-10 / 11-20 boundary.
- Fix direction (from the report): reset rank per segment (each 1-10) and/or add a segment/basis distinguisher per the two p28 table headings. Severity MED-LOW, confidence HIGH. No value error.

### D3 — `performance.portfolio_occupancy` = 95.4 is the Office figure, not a blended portfolio occupancy (LOW / judgment)
- Extraction: `portfolio_occupancy: 95.4` (flagged "95.4 office (retail 97.9)").
- Source (p10 At a Glance; p26 portfolio card lines: "Committed Occupancy (Office) 95.4% / (Retail) 97.9%"; p23 narrative "office and retail portfolio stood at 95.4% and 97.9% respectively"). The report discloses **no single blended** portfolio occupancy.
- Consequence: a single-figure consumer reads 95.4 as whole-portfolio occupancy when it is Office-only; Retail is materially higher (97.9). Choosing Office over Retail (or an NLA-weighted blend ≈ 95.9 given 4.35m office / 1.00m retail sq ft, p26) is a defensible but undocumented judgment. Severity LOW, confidence HIGH. Flagged in notes.

---

## 3. Suspected omissions

### O1 — `_notes.inferred` is empty `[]` while several `profile`/`performance` values are assigned, not disclosed (LOW)
- `profile.sponsor` = "ESR Group Limited": the report has no explicit "Sponsor" designation for this externally-managed trust; it states the Manager is "a wholly-owned subsidiary of ESR Asset Management Limited … part of the ESR Group" (p18/p26). Sponsor=ESR Group is a reasonable derivation but is an inference not flagged.
- `profile.sub_sector` = "Diversified" and `income_model` = "conventional" are classifications, not disclosed labels.
- `performance.distribution_record[].dpu` Q4 = 1.570: derived (6.192 − 1.511 − 1.531 − 1.580); the Distribution Statement (p109) discloses only Q4-2023 + Q1-Q3-2024 paid distributions (the FY2024 Q4 is "paid subsequent to the reporting date", p109 footnote). Correctly noted in `flags` but not in `inferred[]`.
- Severity LOW: provenance understated; no schema-home issue. `_notes.inferred[]` should carry these.

### O2 — Per-property tenant-mix & per-property top-tenant contributions disclosed on every property card, not captured (LOW)
- Each property card carries its own Business Sector Analysis donut (e.g. Suntec City Office 38.9% TMT, p31; Suntec City Mall 42.6% F&B, p32; 177 Pacific Highway 42.3% TMT, p37; 55 Currie Street Govt 39.8%, p47; Nova / Minster, p52/p55) plus per-property Top-10 tenant contribution % (e.g. Suntec City Office top-10 = 29.5% GRI, p31; Suntec City Mall top-10 = 16.9%, p32).
- These are orthogonal to the portfolio-level office/retail `trade_mix` already captured and there is no per-property tenant-mix schema home, so correctly not forced. Flagged here for completeness. Severity LOW.

---

## 4. Reconciliation results (independently re-computed)

### R1 — Statement of Total Return tie-out (Group 2024, p108) — PASS (exact)
Using `financial.line_items`:
- Σ(revenue) = 463,556
- Σ(expense) = 153,130 + 177,213 + 41,100 + 20,242 + 2,034 + 2,027 + 1,026 + 243 + 2,441 = **399,456**
- Σ(adjustments, signed) = +333 +1,165 +80,498 +19,261 −12,576 −29,994 +14,992 −1,625 = **+72,054**
- 463,556 − 399,456 + 72,054 = **136,154** = "Total return for the year after tax" (p108) = `net_income` ✓ exact.
- No missing/extra line: the 18 line_items map 1:1 to the p108 statement (impairment reversal, other income, JV share, finance income, finance costs, 7 trust expenses, 2 FV changes, divestment gain, tax). Complete.

### R2 — Revenue cross-check — PASS
`total_revenue` 463,556 == `performance.gross_revenue` 463,556 == Σ(line_items where statement=revenue) 463,556 == p108 "Gross revenue" ✓. Finance income (19,261) and Other income (1,165) are correctly tagged `adjustment`, NOT revenue — no mis-bucketing.

### R3 — NPI / property expenses — PASS
`cost_of_revenue` 153,130 = p108 "Property expenses" ✓. `gross_income` 310,759 = p108 "Net property income" (463,556 − 153,130 + 333 impairment reversal) ✓ (gross_income set to NPI per convention; the +333 is embedded here and separately present as an adjustment line — no double count within either representation).

### R4 — Derived-metric identities — PASS (all to the dollar)
- I1 operating_income = gross_income − operating_expense: 310,759 − 69,113 = **241,646** ✓ (operating_expense 69,113 = Σ 7 trust expenses ✓; matches `operating_expense_breakdown` sum).
- I2 ebit = pretax + interest_expense_non_operating: 137,779 + 157,952 = **295,731** = ebit = ebitda ✓.
- I3 net_income = pretax − income_taxes: 137,779 − 1,625 = **136,154** ✓.
- (c) interest_expense_non_operating 157,952 = net finance costs = 177,213 finance costs − 19,261 finance income (p108 "Net finance costs" line) ✓.
- non_operating_income_or_loss −103,867 = pretax − operating_income (137,779 − 241,646) ✓, internally consistent with ebit = operating + non_op + interest.

### R5 — Attribution split (p108 / p109 / p112) — PASS (exact)
`unitholders` 112,765 + `perpetual_security_holders` 14,013 + `minorities` 9,376 = **136,154** = net_income ✓.
The P&L (p108) shows a combined "Unitholders of the Trust and perpetual securities holders" = 126,778 and NCI = 9,376. The perpetual slice 14,013 is taken from the Distribution Statement ("Less: total return attributable to perpetual securities holders (14,013)", p109) and the Perpetual Movements statement (p112) → unitholders = 126,778 − 14,013 = **112,765** ✓. Correctly split.

### R6 — Balance sheet (SoFP Group 2024, p107) — PASS (all tie)
total_asset 10,951,124 ✓; current assets 275,143 ✓; non-current assets 10,675,981 ✓; current liabilities 627,271 ✓; non-current liabilities 3,838,206 ✓; total liabilities 4,465,477 ✓; total_equity/net assets 6,485,647 ✓; working_capital 275,143 − 627,271 = −352,128 ✓. (Perpetual 348,040 and NCI **134,321** also confirmed on p107.)

### R7 — Cash flow (Consolidated, p116-117) — PASS
operating 254,630 ✓; investing 174,731 ✓; financing (414,262) ✓; net_cash_flow 254,630 + 174,731 − 414,262 = **15,099** ✓ (= Σ of three activities; the p117 change-in-cash of 13,420 differs only by the −1,679 FX effect, correctly excluded). capital_expenditure (11,200) = p116 "Capital expenditure on investment properties" ✓.

### R8 — Distribution / DPU / NDI (p109-110, p10) — PASS
- NDI 180,923 = taxable income 30,007 + tax-exempt dividend income 150,916 (p109) = FY-generated, EXCLUDING opening 54,153 ✓. Cross-check: "Amount available for distribution" 235,076 = 54,153 + 180,923 ✓.
- distribution_paid 189,148 = Σ four distributions paid during FY (54,290 + 44,026 + 44,674 + 46,158, p109) ✓ — period-mixed (Q4-2023 + Q1-Q3-2024), consistent with `distribution_basis: "not_disclosed_rollforward_only"`.
- DPU 6.192c (p10, p109) ✓; Σ distribution_record 1.511 + 1.531 + 1.580 + 1.570 = **6.192** ✓ (Q4 1.570 derived).

### R9 — Weighted-average units (Note 27, p161-162) — PASS
weighted_avg_shares_basic 2,915,714 ✓; diluted_shares_outstanding 2,928,194 ✓ (both Group column). EPU cross-check: 112,765 / 2,915,714 = 3.867c basic ✓; / 2,928,194 = 3.851c diluted ✓.

### R10 — Portfolio valuation / AUM — PASS (classification correct)
`_notes` direct-consolidated active market_valuation sum = 7,840,279 = p107 "Investment properties" 7,840,279 ✓; + HFS strata unit 13,126 = 7,853,405 = p115 valuation-table sum ✓. JV rows (ORQ, MBFC, Southgate, Nova) are equity-accounted under "Interests in joint ventures" 2,825,303 (p107) and correctly outside the consolidated IP line. `performance.portfolio_value` 11,752,500,000 = p26 "Valuation S$11,752.5M" (Suntec-interest AUM basis; AUM S$12.1b incl. cash, p10) — real disclosed headline, not the audited consolidated total; consistent with `_notes`. No false-flag.

### R11 — trade_mix per-basis sums — PASS
Office (13 rows): 27.4+24.7+13.2+8.8+5.4+3.9+3.8+3.1+2.7+2.5+1.4+0.7+2.4 = **100.0** ✓ (top-two 27.4+24.7 = 52.1 = p27 narrative ✓). Retail (13 rows): 45.6+9.5+8.8+7.2+4.5+4.0+3.6+3.4+3.1+3.0+2.8+2.4+2.1 = **100.0** ✓ (top-two 45.6+9.5 = 55.1 = p27 narrative ✓). Every value matches the p27 chart tables exactly.

### R12 — top_tenants sums (p28) — PASS
Office ranks 1-10 Σ = 2.5+2.4+2.1+2.1+2.0+2.0+1.9+1.7+1.6+1.5 = **19.8%** = p28 Office "Total 19.8%" ✓. Retail ranks 11-20 Σ = 2.2+2.2+2.2+2.0+1.4+1.3+1.2+1.2+1.1+1.1 = **15.9%** = p28 Retail "Total 15.9%" ✓. All 20 names/sectors/%s match.

---

## 5. Nulls / inference audit

**Confirmed genuinely absent (correct nulls):**
- `performance.wale` = null — CORRECT. The report gives office WALE 3.81y and retail WALE 2.29y separately (p29), never a single blended portfolio WALE.
- `performance.weighted_avg_debt_maturity` = null — CORRECT. Only a Debt Maturity Profile **bar chart** (FY2025-FY2029, p23) is disclosed; no single weighted-average term-to-maturity figure appears in the text. (Total consolidated debt S$4,227m and 58% fixed/hedged are the only capital-management scalars, p23.)
- `properties` JV rows' `net_property_income`/`gross_revenue` = null — CORRECT. Note 7 (p142) gives only JV-level 100% Revenue and total Expenses (Expenses bundles interest/depreciation/tax per footnote), and cards disclose only "Net Income Contribution" (a share-of-profit metric). No attributable property NPI is derivable without fabricating a split; handled correctly.
- `properties` Suntec Singapore `occupancy_rate` = null — CORRECT. Portfolio Statement (p113) shows "n/m" for the convention venue.
- `financial.funds_from_operation`, `cash_flow.free_cash_flow` = null — not disclosed. Correct.

**Understated provenance (see O1):** `_notes.inferred` = `[]` omits sponsor derivation, sub_sector/income_model classification, and the derived Q4 DPU 1.570.

**Correctly declared derived:** the 5 `income_stmt_metrics._derived` fields (operating_income, ebit, ebitda, non_operating_income_or_loss, interest_expense_non_operating) — all verified consistent (R4).

---

## 6. Confirmed-correct highlights (balance)

- **Every audited FS figure exact** to the Group 2024 column — STR (all 18 lines), SoFP (all 3 subtotal tiers), cash flow (all 3 activities), distribution statement, EPU units. Column discipline is clean (Group, never Trust-only).
- **Full STR reconciles to total return (136,154k) exactly** — no missing or extra line.
- **The two REIT-specific traps handled correctly**: (1) combined "Unitholders + perpetual" P&L line split into unitholders 112,765 / perpetual 14,013 via the Distribution & Movements statements; (2) NDI 180,923 = FY-generated (excl. opening 54,153), not the cumulative 235,076 and not after-retention.
- **JV / NCI structure navigated correctly**: share of JV profit 80,498 booked as an adjustment; NCI 134,321 (balance sheet) and 9,376 (attribution) both confirmed; Suntec Singapore 66.3% subsidiary consolidated at 100% with the equity-accounted JVs held outside consolidated IP.
- **Finance income & other income correctly bucketed as `adjustment`, not revenue** — the gross-revenue cross-check is CLEAN (contrast other REITs).
- **trade_mix (26 rows) and top_tenants (20 rows) transcribed value-perfect**; per-basis sums tie to the p27/p28 totals exactly.
- **Scalars all confirmed**: leverage 42.4% (p10/p14), ICR 1.9x (p14), all-in cost of debt 4.06% (p10/p23), NAV/unit 2.046 (p107), units in issue 2,921,418k (p107), unitholders 23,886 (p292), distributable income S$180.9m / DPU 6.192c (p10).

---

## 7. Could NOT verify

- **`property_transactions` per-unit divestment dates** — the FY2024 Suntec City Office strata-unit sales are disclosed only as an aggregate (six units in FY2024 + one completed 6 Jan 2025); no per-unit completion dates exist in the parse. Aggregate handling is reasonable; per-unit dates genuinely unverifiable.
- **`distribution_record` ex-date / pay-date** — the Distribution Statement lists periods and amounts but no ex/pay dates; nulls are unverifiable from the AR (dates live in SGXNet announcements, outside this report).
