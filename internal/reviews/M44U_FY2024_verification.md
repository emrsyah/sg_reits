# M44U — Mapletree Logistics Trust (M44U.SI) FY2024 — Forensic Extraction Audit

Auditor: independent verification against source. Navigated the report myself from the TOC — Statements of Profit or Loss / Comprehensive Income / Financial Position / Distribution (pp.113-117), Consolidated Statement of Cash Flows (pp.118-119), Note 3/4/5/6/7 income lines, Note 10 EPU (p.211), Note 14 Investment Properties, Note 29 Segment Information (pp.223-225), Portfolio Statement / Portfolio Review totals (p.161/p.35), Capital Management (pp.41-42), Operations Review incl. quarterly DPU (p.36), Customers/Trade-mix (p.49), Trust Structure (p.22), Corporate/Note-1 constitution (pp.170-171/207/229), Statistics of Unitholdings (p.229). Did NOT consult any extractor tooling, page-map, gather notes, adapter, or the FY2025 extraction.

Source: `parsed_reports_datalab/28_M44U.SI_Mapletree-Logistics-Trust_FY2024/full.md` (page-anchored `<!-- PAGE N -->`). Markdown tables parsed cleanly; no PDF spot-check required.

**FYE confirmed: 31 March 2024** (audited-statement headers "For the financial year ended 31 March 2024", pp.113/115/116/118). All financial figures verified against the **Group 2024** column (not MLT-only, not the 2023 comparative).

---

## 1. Verdict & confidence

**Grade: MINOR ISSUES.**

The five in-scope files (`financial`, `performance`, `trade_mix`, `top_tenants`, `profile`) are excellent on the hard numbers. Every audited figure I re-derived matched the Group 2024 column to the dollar: the full Statement of Profit or Loss reconciles exactly to "Profit for the year" S$330,028k; the three derivation identities hold; the perpetual + NCI attribution (stored positive) sums exactly; balance sheet, cash flow, distribution, EPU, segment NPI, portfolio-valuation sum, trade_mix (Σ=100%), top-10 tenants (Σ=22.0%) and all headline ratios check out; every corporate party is correct.

The issues are all **basis-selection / labelling**, not value errors:
- **`interest_coverage_ratio = 3.1` is the *Adjusted* ICR**, whereas the report's headline "Interest Cover Ratio" is **3.7x** everywhere (D1). The `_notes` flag also mis-describes which figure is the MAS-definition one.
- **`portfolio_value = 13.2bn` is the rounded AUM headline**, mildly inconsistent with the precise portfolio total (13,183,234k) documented in `_notes` and ≠ audited Note-14 IP (13,140,348k) (D2).
- **`distribution_record = null`** with a reason ("no clean FY2024 quarters") that is refuted by the clean quarterly DPU breakdown on p.36 (O1).

Tally: **CONFIRMED ≈ 36** · **DISCREPANCY = 2** · **SUSPECTED-OMISSION = 1** · **UNVERIFIABLE = 1**

---

## 2. Discrepancies

### D1 — `performance.interest_coverage_ratio = 3.1` is the *Adjusted* ICR; the report's headline ICR is 3.7x (MED)
- Extraction ships **3.1** and the `_notes` flag justifies it as "capital-mgmt-note basis … MAS-definition trailing-12m ICR headline was 3.7x."
- Source, this FY2024 report, discloses **two** ratios in the same note:
  - **Interest Cover Ratio = 3.7x** — 5-year summary p6 (line "Interest Cover Ratio (times) … 3.7") with footnote 13 (p6): "*based on a trailing 12 months financial results, **in accordance with the definition from the Monetary Authority of Singapore**.*"; Capital Management p41 (footnote 3: "Ratio of EBITDA over interest expense for a 12-month period"); prose "interest cover ratio of 3.7 times" p16, p41, p42, p47.
  - **Adjusted Interest Cover Ratio = 3.1x** — Capital Management p41 (footnote 4), tied to the MAS Property Funds Appendix leverage-limit condition (min 2.5x, p41 footnote 1); p42 prose "interest cover ratio and adjusted interest cover ratio stood at a healthy 3.7 times and 3.1 times respectively."
- The flag has the labels backwards: it calls 3.7 the "MAS-definition" figure and 3.1 the "note basis," but the report explicitly ties **3.7** to the MAS definition (footnote 13) and labels **3.1** as the *Adjusted* metric. Both come from the same capital-management note.
- Internal-consistency cross-check: the extraction's own `ebitda` (536,105) ÷ interest expense (S$143.6m, p41) = **3.73 ≈ 3.7** — i.e. the extraction's numbers reproduce the headline 3.7, not 3.1.
- Consequence: a consumer reading `interest_coverage_ratio` gets the covenant-adjusted ratio, not the ratio MLT leads with. Recommend **3.7** as the headline value unless the schema explicitly wants the adjusted/covenant ICR (in which case the flag text must be corrected). Severity MED; confidence HIGH.

### D2 — `performance.portfolio_value = 13,200,000,000` is the rounded headline; precise total is 13,183,234k and ≠ audited IP 13,140,348k (LOW)
- Extraction ships **13,200,000,000** = the "S$13.2 billion" AUM headline (p6, p10 line "valued at S$13.2 billion", p35, p182). Genuinely disclosed and repeated — defensible.
- But it is a **rounded** figure. The precise portfolio total is **S$13,183,234k** (Portfolio Review total "SGD 13,183", p35; = active FV 13,045,348 + held-for-sale 42,886 + ROU add-back 95,000, per Portfolio Statement p161). `_notes.reconciliation` itself carries 13,183,234,000 as the "Total portfolio valuation." So performance (13.2bn rounded) is mildly inconsistent with `_notes` (13,183,234k precise).
- Separately, the audited **Note-14 investment properties = 13,140,348k** (p115 / Note 29 segment assets p224) — this is the balance-sheet IP line (excludes the 42,886k held-for-sale in current assets; includes the 95,000k ROU). Neither equals the shipped 13.2bn exactly.
- Consequence: cosmetic imprecision + a documented internal inconsistency (rounded vs precise). Severity LOW; confidence HIGH.

---

## 3. Suspected omissions

### O1 — `performance.distribution_record = null`; a clean quarterly DPU breakdown IS disclosed (LOW–MED)
- `_notes` flag: "distribution_record omitted: rollforward tranches straddle prior-year stubs (not clean FY2024 quarters)."
- That is true only of the **audited Distribution Statement** (p116), whose *cash-paid* tranches are period-mixed (2.268c for 1 Jan–31 Mar 2023 + 0.234c + 2.037c + 2.268c + 2.253c). But the Operations Review **p36** gives a clean by-fiscal-quarter DPU table:
  - 1Q (Apr–Jun) **2.271** · 2Q (Jul–Sep) **2.268** · 3Q (Oct–Dec) **2.253** · 4Q (Jan–Mar) **2.211** · Total **9.003** ✓ (sums exactly to the FY DPU).
- So the premise "no clean FY2024 quarters" is refuted; a per-quarter DPU record is buildable from p36. The one genuine gap is that p36 tabulates DPU only (no per-quarter **record/payment dates**), and the audited statement's dated tranches are the period-mixed cash tranches. Omission is therefore defensible on the *dates*, but the stated reason overreaches. Severity LOW–MED; confidence HIGH.

### O2 — `distribution_basis = "full_payout_no_retention_line"` understates a real S$1,214k retention (LOW)
- NDI 447,149 − distribution_paid 445,935 = **1,214k retained**, which exactly matches the Distribution Statement rollforward (amount available at end 111,214 − beginning 110,000 = 1,214, p116). There *is* a small retention; the statement simply has no explicit "retention" line (it is a rollforward), so the label is not wrong but reads as "no retention." The flag already notes the 1,214 delta. Severity LOW.

---

## 4. Reconciliation results (independently re-computed)

### Statement of Profit or Loss tie-out (Group 2024, p113) — PASS
Using `line_items` (S$'000): revenue 733,889 − expenses (property 98,945 + mgmt 91,166 + trustee 1,831 + other-trust 28,004 + borrowing 145,905 = 365,851) + signed adjustments (interest income +2,935 + FV derivatives +20,671 + net movement IP +1,491 + tax −63,107 = **−38,010**) = **733,889 − 365,851 − 38,010 = 330,028k = "Profit for the year"** ✓ exact. No missing line (Group "Dividend income" and "Amortisation of FV of financial guarantees" are both nil for the Group; correctly excluded).

### total_revenue == gross_revenue == Σ revenue lines — PASS
733,889,000 across all three; interest income correctly tagged `adjustment` (not mis-bucketed as revenue). ✓

### gross_income == NPI; cost_of_revenue == property expenses — PASS
gross_income 634,944 = NPI 634,944 (p113 / Note 29 total p224); cost_of_revenue 98,945 = Property expenses ✓.

### Derivation identities — PASS
- I1: operating_income 513,943 = gross_income 634,944 − operating_expense 121,001 ✓ (operating_expense 121,001 = mgmt 91,166 + trustee 1,831 + other-trust 28,004 = "Unallocated costs" 121,001, Note 29 p224 ✓).
- I2: pretax 393,135 = ebit 536,105 − interest_expense_non_operating 142,970 ✓.
- I3: net_income 330,028 = pretax 393,135 − income_taxes 63,107 ✓.
- (c) interest_expense_non_operating 142,970 = borrowing costs 145,905 − interest income 2,935 (Group dividend income = 0) ✓.
- non_operating_income_or_loss −120,808 = 2,935 + 20,671 + 1,491 − 145,905 ✓ (derived, declared).

### Attribution (positive) — PASS
unitholders 303,135 + perpetual_security_holders 24,340 + minorities 2,553 = **330,028** = net_income ✓ (p113 "Profit attributable to:").

### Balance sheet (p115) — PASS
total_asset 13,812,335 = total_liabilities 6,327,903 + total_equity 7,484,432 ✓; current asset 478,897 / non-current 13,333,438; current liab 621,114 / non-current 5,706,789; working_capital 478,897 − 621,114 = −142,217 ✓. Equity split: unitholders' funds 6,884,841 + perpetual 581,545 + NCI 18,046 = 7,484,432 ✓.

### Cash flow (pp.118-119) — PASS
operating 573,488 + investing (−844,254) + financing 280,615 = **9,849** = net_cash_flow ✓; capital_expenditure −1,027,594 = "Net cash outflow on purchase of and additions to investment properties…" ✓.

### EPU / weighted-avg units (Note 10, p211) — PASS
weighted_avg_shares_basic 4,958,115,000 = "Weighted average number of units … 4,958,115 ('000)"; 303,135 ÷ 4,958,115 = 6.11c = disclosed EPU ✓. number_of_shareholder_units 4,993,959,000 = "Units in issue 4,993,959 ('000)" (p115) ✓.

### Distribution (p116) — PASS (convention correct)
net_distributable_income 447,149 = "Amount available for distribution" (FY-generated, **before** adding opening carry-forward 110,000; NOT the cumulative 557,149; NOT after-retention) ✓. distribution_paid 445,935 = "Total Unitholders' distribution (incl capital return)" Note B ✓. dpu 9.003 ✓; dpu_period_months 12 ✓.

### Portfolio valuation sum — PASS
Σ(properties.json market_valuation, 187 rows: 185 active + 2 held-for-sale) = **13,088,234,000** = active FV 13,045,348k (Portfolio Statement p161) + held-for-sale 42,886k (Note 15 p195) ✓. + ROU add-back 95,000k = **13,183,234k** = Portfolio Review total "SGD 13,183" (p35) ✓. Audited Note-14 IP 13,140,348k = 13,045,348 + 95,000 ROU (HFS sits in current assets) ✓. Country counts (SG 49, China 43, Japan 24, Korea 21, Australia 14, Malaysia 14, Vietnam 10, HK 9, India 3 = 187) match the per-market review tables (China 43 p3304, Japan 24 p3425, Korea 21 p3509, Australia 14 p3265, Malaysia 14 p3466, Vietnam 10 p3552). ✓

### trade_mix (p49) — PASS
16 rows, one per disclosed segment; Σ = 19+18+5+3+6+3+4+13+6+5+2+4+1+1+5+5 = **100%** ✓. All categories & pcts match the p49 "Diversified Customer Trade Sectors" table verbatim (F&B 19, Consumer Staples 18, Electronics & IT 13 = the disclosed top-3, p2932). pct_basis "gross_revenue" ✓ (table titled "by Gross Revenue").

### top_tenants (p49) — PASS
10 rows, ranks 1-10 contiguous, %s descending: CWT 4.0, Equinix 3.5, Coles Group 3.0, JD.com 2.1, S.F. Express 1.9, HKTV 1.8, Coupang 1.6, Bidvest 1.4, Woolworths 1.4, J&T 1.3. Σ = **22.0%** = disclosed "top 10 … approximately 22.0% … no single customer more than 4.0%" (p2930) ✓. All values match the p49 chart/table exactly.

---

## 5. Nulls / inference audit

**Confirmed genuinely absent (correct nulls):**
- `financial.funds_from_operation`, `cash_flow.free_cash_flow`, `employee_breakdown` — not disclosed. ✓
- `top_tenants[].industry` all null — the p49 chart lists customer names only, no sectors. ✓
- `properties.net_property_income` / `npi_pct` — genuinely disclosed **only by geographic segment** (Note 29 p224: Singapore 173,592 … India 6,140, Total 634,944), never per property. I confirmed the audited Portfolio Statement carries per-property *gross revenue* but no per-property NPI/opex column. Correct null + correct reason. ✓ (`_notes.inferred` correctly records that no NPI was imputed.)
- Per-property `gla`/`gfa`, `lease_expiry_date`, freehold `lease_term_years`, Singapore `original_value` — spot-checked against the reasons in `_notes.columns_never_fillable`; all structurally N/A as described. ✓
- Redevelopment/under-development gross-revenue & occupancy nulls (51 Benoi Road p125, Subang Land Parcel p151) — cells are "–"/"—" in the source. ✓

**`_derived[]`** correctly lists the 5 computed income-statement fields; no undisclosed value is presented as disclosed.

**Inference note:** `distribution_basis`, `portfolio_value` (rounded headline) and `interest_coverage_ratio` (adjusted basis) are *interpretive selections* — the first two are documented in `flags`; the ICR basis choice is documented but mis-labelled (see D1).

---

## 6. Confirmed-correct highlights

- **Every audited FS figure exact to the Group 2024 column** — gross revenue, property expenses, NPI, all below-the-line items, finance/interest income, tax, profit for the year, distributable income, DPU, EPU.
- **Full P&L reconciles to S$330,028k** with no missing/extra line.
- **Perpetual + NCI attribution handled correctly and stored positive** (303,135 / 24,340 / 2,553 → 330,028).
- **Portfolio valuation sum reconciles** across all three layers (active / +HFS / +ROU) and correctly separates Note-14 IP from held-for-sale; the Datalab OCR fix on Farrukhnagar (14,82 → 14,826) is documented and consistent with the p161 total.
- **187 properties** across the correct 9 markets, counts matching every per-market review table.
- **Headline ratios all correct**: aggregate_leverage 38.9% (p41), cost_of_debt 2.5% (p6), weighted_avg_debt_maturity 3.8y (p41), wale 3.0y by NLA (p16/p48), portfolio_occupancy 96.0% (p17/p49), nav_per_unit 1.38 (p35/p115), number_of_unitholders 31,888 (p229).
- **Corporate parties all correct**: manager Mapletree Logistics Trust Management Ltd., trustee HSBC Institutional Trust Services (Singapore) Limited (p22/p105), property manager Mapletree Property Management Pte. Ltd. (p22/p170), sponsor Mapletree Investments Pte Ltd (p23/Note 1 p207). sub_sector Industrial / income_model conventional — appropriate for a logistics REIT.
- **trade_mix / top_tenants captured verbatim** incl. the 16th trade-sector row the chart caption ("15 segments") would tempt an extractor to drop.

---

## 7. Could NOT verify

- **Exact derivation of the 3.1 Adjusted ICR** — the report discloses the value (p41) but not the full adjusted numerator/denominator, so I cannot independently reproduce 3.1 to the decimal (I can reproduce the 3.7 headline as EBITDA/interest ≈ 3.73). Marked UNVERIFIABLE; does not change the D1 conclusion that 3.7 is the headline.

---

## 8. Concrete fix list (file → field → correct value → page)

1. `performance.json` → `interest_coverage_ratio` → **3.7** (report headline "Interest Cover Ratio", p6 footnote-13 = MAS definition / p41 / p42), OR keep 3.1 but relabel the flag: 3.7 is the MAS-definition headline, 3.1 is the *Adjusted* ICR (covenant metric). **[MED — decide basis]**
2. `performance.json` → `portfolio_value` → consider **13,183,234,000** (precise Portfolio Review total "SGD 13,183", p35 / p161) instead of the rounded 13,200,000,000, to remove the internal inconsistency with `_notes` (which stores 13,183,234,000). **[LOW]**
3. `performance.json` → `distribution_record` → populate from the p36 quarterly DPU table (1Q 2.271 / 2Q 2.268 / 3Q 2.253 / 4Q 2.211 = 9.003), or correct the flag reason — the "no clean FY2024 quarters" justification is refuted by p36 (per-quarter record/payment dates are the only genuine gap). **[LOW–MED]**
4. `performance.json` → `distribution_basis` label acknowledges the S$1,214k retention (NDI 447,149 − paid 445,935 = rollforward Δ 110,000→111,214), p116. **[LOW, cosmetic]**

No changes to the audited financial-statement numbers, attribution, properties, trade_mix, top_tenants, or profile are warranted — those verify clean.
