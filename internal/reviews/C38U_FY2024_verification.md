# C38U — CapitaLand Integrated Commercial Trust (C38U.SI) FY2024 — Forensic Extraction Audit

Auditor: independent verification against source. Navigated the report myself from the Table of Contents (p33) — About Us (p3), Financial Highlights 5-year table (p4), Portfolio Valuation (p22/parse-p22), Financial Review (p23-24), Capital Management (p26-30), Operations Review incl. Top-10 Tenants / Trade Mix (parse-p31-32), Property Details cards (parse-p38-63), the full audited Financial Statements (Statements of Financial Position parse-p103, Statement of Total Return parse-p104, Distribution Statement parse-p105, Movements in Unitholders' Funds parse-p106, Portfolio Statement parse-p107-108, Statement of Cash Flows parse-p109-110), Notes 5/7/25/26/27/28/32/33, and Statistics of Unitholdings (parse-p189). Did **NOT** consult any extractor tooling, page-map, `extracted_adapter/`, `local://fy2024-gather/*`, the extraction skill, or the FY2025 extraction.

Source: `parsed_reports_datalab/09_C38U.SI_CapitaLand-Integrated-Commercial-Trust_FY2024/full.md` (page-anchored). Markdown tables parsed cleanly; no PDF spot-check required.

**Confirmed FYE:** every audited statement header reads **"Year ended 31 December 2024"** / **"As at 31 December 2024"**. All financials verified against the **Group 2024** column (not Trust, not 2023).

---

## 1. Verdict & confidence

**Grade: MINOR ISSUES.**

The extraction is exceptionally clean on the hard numbers. Every audited financial-statement figure I re-derived matched the Group 2024 column **to the dollar**; the full Statement of Total Return reconciles exactly to "Total return for the year" (S$941,777k); the three income-statement identities (I1/I2/I3) hold to the dollar including the **tax credit** convention; the balance sheet, cash flow, distribution, DPU, EPU-units, portfolio-valuation sum, trade_mix (exactly 100%) and top-10 tenants (Σ = disclosed 16.9%) all tie out. The diversified retail+office structure and the ION Orchard / CapitaSpring equity-accounted-JV treatment were navigated correctly — those JV assets are properly held **outside** the consolidated investment-property total.

The single real defect is a **false null with a wrong justification**: `performance.number_of_unitholders` is `null` and the flag asserts it is "NOT DISCLOSED in parsed AR", but the Statistics of Unitholdings table (parse-p189) plainly discloses **85,596** unitholders. One low-severity note-imprecision (ION Orchard valuation description) rounds out the findings.

Tally: **CONFIRMED ≈ 55** · **DISCREPANCY = 1** · **SUSPECTED-OMISSION = 1** · **UNVERIFIABLE = 1**

---

## 2. Discrepancies

### D1 — `performance.number_of_unitholders` = null with a FALSE "not disclosed" justification (MED)
- Extraction: `number_of_unitholders: null`; `performance.flags` states *"number_of_unitholders NOT DISCLOSED in parsed AR."*
- Source (**parse-p189, Statistics of Unitholdings → Distribution of Unitholdings table**): the TOTAL row reads **No. of Unitholders = 85,596** (breakdown: 4,164 / 26,261 / 40,175 / 14,946 / 50 across the five holding-size bands; Σ = 85,596). Issued units 7,298,469,763 also on the same page.
- Consequence: a standard, directly-disclosed field is dropped and the null is defended by a claim that is factually wrong. Downstream consumers will treat unitholder count as unavailable when it is not.
- **Fix:** `performance.json → number_of_unitholders = 85596` (source parse-p189); remove/correct the "NOT DISCLOSED" clause in the flag. Confidence: HIGH.

---

## 3. Suspected omissions

### O1 — `performance.distribution_record` = null (LOW; likely correct)
The parse discloses no per-distribution record/books-closure dates for FY2024 — only the generic policy statement *"Distributions are generally paid within 35 market days after the relevant record date"* (parse-p… line "Investor Relations", ~parse-p30s). The Distribution Statement lists distribution *periods* and per-unit rates but no record dates. Null is defensible; flagged only for completeness. No reliable schema value is recoverable from the parse. SEVERITY: LOW.

---

## 4. Reconciliation results (independently re-computed)

### R1 — Statement of Total Return tie-out (Group 2024, parse-p104) — **PASS (exact)**
Using `financial.line_items` (absolute $, i.e. table figure ×1000):
- Σ(revenue) = gross_revenue **1,586,329**
- Σ(expense) = property opex 432,851 + mgmt base 48,162 + mgmt perf 47,471 + professional 3,175 + valuation 800 + trustee 3,442 + audit 923 + finance costs 345,394 + other 10,586 = **892,804**
- Σ(adjustments, signed, all +) = interest income 12,702 + other income 63 + investment income 9,381 + share of JV 33,756 + FV change IP 153,127 + gain on divestment 32,765 + taxation **+6,458** = **248,252**
- 1,586,329 − 892,804 + 248,252 = **941,777** = "Total return for the year" (parse-p104) = `income_stmt_metrics.net_income` ✓. No missing or extra line. The **tax credit is correctly carried as +6,458** (a credit, added not subtracted).

### R2 — income-statement identities — **PASS (exact)**
- **I1** operating_income = gross_income − operating_expense → 1,153,478 − 114,559 = **1,038,919** ✓ (operating_expense 114,559 = the 7 trust-expense lines, matching `operating_expense_breakdown`).
- **I2** pretax = ebit − interest_expense_non_operating → 1,258,567 − 323,248 = **935,319** ✓ (ebit = operating_income 1,038,919 + JV 33,756 + FV 153,127 + gain 32,765).
- **I3** net_income = pretax − income_taxes → 935,319 − (−6,458) = **941,777** ✓ (tax credit stored NEGATIVE −6,458, so net = pretax + 6,458). Matches Statement of Total Return: 935,319 before tax → 941,777 after +6,458 tax credit.
- **(c)** interest_expense_non_operating **323,248** = finance costs 345,394 − interest income 12,702 − investment income 9,381 − other income 63 (net non-operating finance cost) ✓ — components confirmed on parse-p104.
- **(d)** attribution: unitholders 933,683 + minorities (NCI) 8,094 = **941,777** = net_income ✓; perpetual_security_holders null (CICT has no perpetual securities — correct).

### R3 — total_revenue / NPI / cost_of_revenue — **PASS**
`total_revenue` 1,586,329 == `performance.gross_revenue` 1,586,329 == Σ(line_items where statement=revenue) 1,586,329 ✓. `gross_income` 1,153,478 == NPI (parse-p104) ✓. `cost_of_revenue` 432,851 == property operating expenses (parse-p104) ✓. No finance/other income mis-bucketed as revenue.

### R4 — Balance sheet (parse-p103, Group 2024) — **PASS (exact)**
total_asset 25,513,002 ✓; total_equity 15,722,171 ✓ (incl. NCI 197,715); total_liabilities 9,790,831 ✓; current assets 243,063 ✓; non-current assets 25,269,939 ✓; current liab 1,510,859 ✓; non-current liab 8,279,972 ✓. Cross-checks: 243,063 + 25,269,939 = 25,513,002 ✓; 1,510,859 + 8,279,972 = 9,790,831 ✓; assets − liab = 15,722,171 ✓; working_capital 243,063 − 1,510,859 = **−1,267,796** ✓. nav_per_unit 2.12 = SOFP "NAV per unit attributable to Unitholders" (Group, parse-p103) ✓.

### R5 — Cash flow (parse-p109-110, Group 2024) — **PASS (exact)**
operating 1,044,198 ✓; investing −520,565 ✓; financing −507,975 ✓; net 1,044,198 − 520,565 − 507,975 = **15,658** = "Net increase in cash" ✓; capital_expenditure −178,294 = "Capital expenditure on investment properties" ✓.

### R6 — Distribution / DPU — **PASS**
DPU **10.88c** = Distribution Statement (parse-p105) and 5-yr summary (parse-p4) ✓. `net_distributable_income` **761,592** = the FY-generated subtotal on the Distribution Statement (the line before "Amount available for distribution 1,133,249"; **excludes** the opening carried-forward 371,657 and is **not** after-retention) ✓ — convention correct. `distribution_paid` **752,211** = 761,592 − retention Note B 9,381; matches the headline disclosed distributable income **S$752.2m** (parse-p24/p10) ✓; `distribution_basis = disclosed_after_retention` consistent (NDI − distribution_paid = 9,381 = disclosed retention) ✓.

### R7 — Portfolio valuation sum — **PASS (exact)**
Σ(`properties.market_valuation`, 26 valued rows) = **29,458,705k**. The audited Portfolio Statement (parse-p107) total = **23,702,305k** = SOFP investment-properties line (parse-p103) ✓. Reconciliation: 29,458,705 − ION Orchard 3,697,900 − CapitaSpring 2,058,500 = **23,702,305** ✓ exact. **ION Orchard and CapitaSpring are equity-accounted JVs** — correctly EXCLUDED from the consolidated IP total (they sit inside the SOFP "Joint ventures" line 1,431,840, parse-p103) and correctly flagged in `_notes`. 21 Collyer Quay carries null (dash after 11-Nov-2024 divestment) ✓. `performance.portfolio_value` **26,034,900,000** = Portfolio Valuation grand total S$26,034.9m (proportionate-interest basis, parse-p22) ✓.

### R8 — Trade mix (parse-p32) — **PASS (exact 100%)**
F&B 17.9 + Fin&Prof (Banking/Insurance/Financial) 17.8 + Fashion 8.4 + Healthcare (Beauty&Health) 7.5 + Hospitality 5.1 + Real Estate & Prop Svcs 4.0 + IT&Telco 3.9 + Other Retail 23.2 + Other Office 12.2 = **100.0%** ✓. All 9 categories captured; `pct_basis="gri"` = committed GRI on proportionate interests ✓.

### R9 — Top-10 tenants (parse-p31) — **PASS (exact)**
Ranks 1–10 contiguous, %s descending: RC Hotels 4.9, GIC 1.7, Temasek 1.6, NTUC 1.6, Work Project 1.6, Cold Storage 1.3, BreadTalk 1.2, UNIQLO 1.0, KPMG 1.0, Mizuho 1.0. Σ = **16.9%** = disclosed "top 10 = 16.9%" ✓. Names, ranks, %s and raw sectors all match.

### R10 — EPU weighted-average units (Note 27, parse-p163) — **PASS**
`weighted_avg_shares_basic` 6,864,567,000 = "Weighted average number of units in issue" 6,864,567k ✓; `diluted_shares_outstanding` 6,880,161,000 = diluted weighted avg 6,880,161k ✓. Cross-check: 933,683 / 6,864,567 = 13.60c basic ✓; 933,683 / 6,880,161 = 13.57c diluted ✓.

### R11 — Property transactions (Notes 28/32/33) — **PASS**
- ION Orchard acquisition: purchase_price **1,073,023k** = related-party "acquisition of CRSI shares" 1,073,023 (parse-p187) ✓; interest 50% ✓; counterparty **CLI Singapore Pte. Ltd.** ✓ (parse-p184); valuation 3,697,000k = agreed property value S$3,697.0m 100% basis ✓; note documents S$1,095,215k invested incl. costs and S$1,079,322k net cash outflow — both present in source ✓.
- 21 Collyer Quay divestment: gross 688,000k ✓ (Savills S$688.0m, sale S$688.0m, parse-p10); net proceeds 672,607k ✓ (cash flow parse-p109); gain 32,800k ✓ (Note 33 "net gain S$32.8m"); counterparty **Sun View SG I Pte. Ltd.** ✓ (parse-p10); date 11 Nov 2024 ✓.

---

## 5. Nulls / inference audit

**False null (see D1):** `number_of_unitholders` — **REFUTED**; disclosed 85,596 (parse-p189).

**Confirmed genuinely absent (correct nulls):**
- `perpetual_security_holders` — CICT has no perpetual securities; correctly null.
- `properties.net_property_income` / `npi_pct` — genuinely not disclosed per property. Note 31 Operating Segments (parse-p176-177/182-183) gives NPI only at 3 reportable-segment level (Retail 420,146 / Office 387,646 / Integrated 345,686 / JV share 33,756). Correct null + correct reason ✓.
- ION Orchard / CapitaSpring per-property NPI — equity-accounted; not disclosed. Correct ✓.
- `distribution_record` — no record dates in the parse (see O1). Defensible null.
- 21 Collyer Quay `market_valuation` — dash in Portfolio Statement post-divestment; correct null ✓.

**Inference / derived handling:**
- `_derived[]` correctly declares operating_income, ebit, ebitda (=ebit), non_operating_income_or_loss (−103,600 = −323,248 + 219,648), interest_expense_non_operating as computed — all re-derived and internally consistent (R2). Reasonable approach.
- `income_taxes` sign convention (−6,458 for a credit) correct and consistent with I3 ✓.
- Purchase-price recoveries in `_notes.null_recovery_pass` (agreed property values for Bedok Mall, Asia Square T2, CapitaGreen, CapitaSky, foreign assets in local currency) are legitimately disclosed on the property cards — good null-recovery discipline.

---

## 6. Confirmed-correct highlights (balance)

- **All audited FS numbers exact** to the Group 2024 column: gross revenue, property opex, NPI, every trust-expense line, interest/other/investment income, finance costs, JV share, FV change, gain on divestment, tax **credit +6,458**, total return, attribution split, balance sheet, cash flow, EPU units.
- **Statement of Total Return reconciles to 941,777 exactly** — no line missing/extra; tax-credit sign handled correctly.
- **Equity-accounted JV trap navigated correctly**: ION Orchard (50%) and CapitaSpring (45%) held outside the consolidated IP line; Σ market_valuation ties to 23,702,305k after removing the two JV rows. CapitaSky/Gallileo/MAC consolidated at 100% with NCI flagged — correct.
- **ION Orchard 3,697.9m** (year-end card valuation, parse-p42 "Valuation (S$ million) 3,697.9") vs **3,697.0m** agreed-acquisition value (transactions) — both distinct figures used correctly for their respective fields.
- **KPIs** all match: aggregate leverage 38.5%, ICR 3.1×, cost of debt 3.6%, avg term to maturity 3.9y, WALE 3.3y, committed occupancy 96.7%, DPU 10.88c, units in issue 7,298,470k.
- **Profile** fully corroborated: manager CICTML, trustee HSBC Institutional Trust Services (Singapore), sponsor CapitaLand Investment Limited, property managers CapitaLand Retail Management / CapitaLand Commercial Management / Orchard Turn Developments (parse-p112/139/189), sub_sector Diversified.
- **Trade_mix (100%) and top-10 tenants (16.9%)** captured verbatim on the correct proportionate-GRI basis.

---

## 7. Could NOT verify

- **Per-property SGD NPI** — genuinely undisclosed (segment-only). Null stands; unverifiable by design.
- **Distribution record dates** — not in the parse; `distribution_record` null unverifiable (see O1).
- **21 Collyer Quay carrying value immediately before sale** — not stated in Note 33; `carrying_value` null is correct and unverifiable.
