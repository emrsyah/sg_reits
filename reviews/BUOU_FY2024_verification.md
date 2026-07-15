# BUOU — Frasers Logistics & Commercial Trust (BUOU.SI) FY2024 — Forensic Extraction Audit

Auditor: independent verification against source. Navigated the report myself from the TOC (Financial Highlights / Portfolio value & tenure charts, Operational Review incl. Top-10 L&I and Top-10 Commercial tenant tables and the Portfolio Tenant Sector matrix pp.34-37, Capital Management pp.30-32, audited Statement of Total Return / Distribution Statement / Statements of Financial Position / Cash Flows / Movements pp.200-209, Portfolio Statement pp.208-216, Notes 3/4/5/6/7/9/23/32, Statistics of Unitholdings, Corporate Information). Did NOT consult any extractor tooling, page-map, gather notes, adapter output, or the FY2025 extraction.

Sources: `parsed_reports_datalab/19_BUOU.SI_Frasers-Logistics-and-Commercial-Trust_FY2024/full.md` (Datalab `<!-- PAGE N -->` markers). Markdown tables parsed cleanly; no PDF spot-check required.

**FYE confirmed: "For the year ended 30 September 2024" (STR header, PAGE 202).** All P&L / distribution / cash-flow figures verified against the **Group 2024** column (not Trust-only); balance sheet against **Group 2024**.

Structure: single REIT (no stapling), no perpetual securities, NCI present (S$3,152k). Multi-currency portfolio (AUD/EUR/GBP) presented in SGD; audited carrying amounts are all SGD.

---

## 1. Verdict & confidence

**Grade: MINOR ISSUES** (very close to CLEAN).

Every audited financial-statement figure I re-derived matches the Group 2024 column to the dollar. The full Statement of Total Return reconciles exactly to "Total return for the year" S$150,677k; balance sheet, cash flow, EPU weighted units, distribution/DPU, portfolio valuation sum (S$6,928,373k), the 22-cell trade-mix matrix, and the 20-row top-tenant list all tie out. The three derived-metric identities hold exactly. The two-distribution-line trap (income-available 210,337 vs distributable income 255,515), the trade-mix matrix split, and the L&I(1-10)/Commercial(11-20) tenant ordering were all handled correctly.

The only substantive defect is **`financial.revenue_breakdown` shipped empty `[]`** while Note 3 discloses a clean 3-line by-nature breakdown (rental income / recoverable outgoings / other revenue). Everything else is a low-severity capture nuance (a recoverable distribution pay-date; the disclosed "Distributable income" 255,515 living only in a flag).

Tally: **CONFIRMED ≈ 40** · **DISCREPANCY = 1** · **SUSPECTED-OMISSION = 4** · **UNVERIFIABLE = 2**

---

## 2. Discrepancies

### D1 — `financial.income_stmt_metrics.revenue_breakdown` = `[]` although Note 3 discloses a 3-line breakdown (MED)
- Extraction: `revenue_breakdown: []` (empty). `total_revenue` 446,674,000 is correct, but no component split is captured.
- Source — **Note 3 REVENUE, PAGE 245 (Group 2024, S$'000):** Rental income **361,939**; Recoverable outgoings **83,426**; Other revenue **1,309**; total **446,674**. This is a fully disclosed by-nature breakdown with a schema home (`revenue_breakdown`).
- Consequence: downstream loses the rental-vs-recoverables split (recoverable outgoings are ~18.7% of revenue — material to a revenue-quality view). Note the sibling field `operating_expense_breakdown` WAS populated (mgmt/trustee/trust), so the empty revenue array is an inconsistency, not a policy.
- Fix: populate `revenue_breakdown` with the three Note-3 lines (×1000). Severity MED, confidence HIGH.

---

## 3. Suspected omissions

### O1 — `distribution_record[0].pay_date` left null although Note 23 discloses it (LOW)
- The record period "1 Oct 2023 to 31 Mar 2024" (DPU 3.48c) has `pay_date: null`, but **Note 23 (PAGE 289) states this distribution was "paid on 18 June 2024"** (also Distribution Statement PAGE 203). The H2 period "1 Apr 2024 to 30 Sep 2024" (3.32c) was only declared 6 Nov 2024 and paid post-FYE, so its pay_date is genuinely absent. Fix: `distribution_record[0].pay_date = "2024-06-18"`. `ex_date` is not disclosed in the audited statements. Severity LOW.

### O2 — Disclosed "Distributable income" S$255,515k (the actual DPU basis) has no field, only a flag (LOW)
- The Distribution Statement (PAGE 203) discloses TWO figures: "Income available for distribution to Unitholders" **210,337** (correctly stored as `net_distributable_income`) and **"Distributable income" 255,515** (= 210,337 income-available + 45,178 capital distribution, Note B). The DPU of 6.80c is struck on 255,515 (255,515 / 3,762,202k units ≈ 6.79c), NOT on 210,337. The 255,515 figure lives only in `performance.flags`. If `adjusted_distributable_income` is meant to hold the total FY distributable (income + capital top-up), 255,515 is its natural value; it is currently null. Choice is defensible (there is no "Adjusted distributable income" label in this AR), so LOW severity — flagged for downstream awareness.

### O3 — Note 4 property-operating-expense breakdown (7 lines) not captured (LOW)
- **Note 4, PAGE 245** breaks `cost_of_revenue` (124,700) into Land & property tax 30,363 / Property management fees 16,404 / Property maintenance 40,825 / Professional fees 1,370 / (Reversal of) doubtful receivables (173) / Statutory expenses 12,080 / Other property expenses 23,831. No `cost_of_revenue_breakdown` schema field appears to exist, so likely not capturable — noted for completeness. Severity LOW.

### O4 — `performance.number_of_properties` absent while "112 properties" is stated repeatedly (LOW)
- The report states a portfolio of **112 properties** across five markets (Operational Review PAGE 34; Multinational Presence map PAGE ~11; "104 L&I properties" PAGE ~30). `performance.json` carries no `number_of_properties` value. If the schema supports it, 112 (completed) is the disclosed figure (properties.json additionally carries the Maastricht IPUD as a 113th row). Severity LOW / schema-dependent.

---

## 4. Reconciliation results (independently re-computed)

### Statement of Total Return tie-out (Group 2024, PAGE 202) — PASS
Using `financial.line_items`:
- Σ revenue = **446,674**
- Σ expense = property opex 124,700 + mgmt fees 37,594 + trustee 845 + trust exp 4,690 + finance costs 65,658 = **233,487**
- Σ adjustments (signed) = exchange gains +117 + finance income +1,948 + FV derivatives −122 + FV investment properties −40,753 + tax −23,700 = **−62,510**
- 446,674 − 233,487 − 62,510 = **150,677** = "Total return for the year" (PAGE 202) = `net_income` ✓ exact.
- No missing/extra line. "Gain on divestment" is nil in FY2024 (correctly omitted; `net_property_sales`=0).

### Derived-metric identities — PASS
- I1 operating_income = gross_income − operating_expense: 321,974 − 43,129 = **278,845** ✓ (operating_expense 43,129 = 37,594+845+4,690 ✓).
- I2 ebit = pretax + interest_expense_non_operating: 174,377 + 63,710 = **238,087** ✓ (= ebitda; no D&A). 
- I3 net_income = pretax − income_taxes: 174,377 − 23,700 = **150,677** ✓.
- `non_operating_income_or_loss` −104,468 = 117 + 1,948 − 65,658 − 122 − 40,753 ✓ (all below-NPI items ex-operating-expenses); 278,845 − 104,468 = 174,377 = pretax ✓.
- (c) `interest_expense_non_operating` 63,710 = NET finance cost = finance costs 65,658 − finance income 1,948 (**Note 6, PAGE 246**) ✓.
- (d) attribution: unitholders 147,525 + perpetual (null/0) + minorities 3,152 = **150,677** ✓ (PAGE 202).

### Revenue / NPI / opex (PAGE 202 + Notes 3/4) — PASS
`total_revenue` 446,674 == `performance.gross_revenue` 446,674 == Σ(line_items revenue) 446,674 ✓. `gross_income` 321,974 = Net property income ✓. `cost_of_revenue` 124,700 = property operating expenses (Note 4) ✓. No finance/other income mis-bucketed into revenue.

### Balance Sheet (Group 2024, PAGE 204) — PASS
total_asset 7,136,884 ✓; total_liabilities 2,814,788 ✓; total_equity (net assets) 4,322,096 ✓; current assets 178,206 ✓; non-current assets 6,958,678 ✓; current liab 668,141 ✓; non-current liab 2,146,647 ✓; working_capital 178,206 − 668,141 = −489,935 ✓. NAV/unit 1.13 ✓; units 3,762,202k ✓.

### Cash Flow (Group 2024, PAGE 208) — PASS
operating 311,372 ✓; investing −263,661 ✓; financing −67,375 ✓; net_cash_flow 311,372 − 263,661 − 67,375 = **−19,664** ✓ (= "Net decrease in cash"); capital_expenditure −88,209 ✓.

### EPU weighted units (Note 9, PAGE 248) — PASS
`weighted_avg_shares_basic` 3,752,728 ✓; `diluted_shares_outstanding` 3,762,202 = "Weighted average number of Units (diluted)" ✓ (a genuine diluted-WA figure that coincidentally equals period-end units in issue — not a mislabel).

### Distribution & DPU (PAGE 203, Note 23 PAGE 289) — PASS
- `net_distributable_income` 210,337 = "Income available for distribution to Unitholders" (FY-generated, income-based, BEFORE the 45,178 capital-distribution top-up; excludes opening balance 131,812 and is NOT the cumulative "amount available" 387,327) ✓ — matches the NDI convention.
- `distribution_paid` 262,580 = cash distributions paid during FY2024 (H2-FY2023 3.52c = 131,808 paid 14 Dec 2023 + H1-FY2024 3.48c = 130,772 paid 18 Jun 2024) ✓.
- DPU 6.80c ✓; record 3.48c (Oct'23–Mar'24) + 3.32c (Apr'24–Sep'24, declared 6 Nov 2024, PAGE 295) = 6.80c ✓ — correctly the two in-respect-of-FY2024 half-years, not the paid-during-year periods.
- basis `not_disclosed_rollforward_only` is apt (statement is a rollforward; NDI−paid is negative, no clean retention line).

### Portfolio valuation sum (Portfolio Statement, PAGE 210-216) — PASS
Σ(`properties.json` market_valuation, all 113 rows) = **6,928,373,000** = audited "Total completed investment properties and IPUD" 6,928,373 (Portfolio Statement) = balance-sheet Investment properties 6,928,373 (PAGE 204) ✓ exact. Completed 6,906,337 + Maastricht IPUD 22,036 = 6,928,373 ✓ (matches `_notes` reconciliation). `performance.portfolio_value` 6,773,200 is the disclosed "Portfolio value ($m)" headline (Financial Highlights), which per footnote (a) excludes IPUD/held-for-sale/ROU — difference to the audited 6,928,373 is correctly explained in flags.

### Trade mix matrix (Portfolio Tenant Sector Breakdown by GRI, PAGE 36) — PASS
All **22 non-blank cells** of the L&I × Commercial matrix captured verbatim with correct `pct_basis` (gri_logistics_industrial / gri_commercial). Σ L&I cells = 64.4, Σ Commercial cells = 35.6, combined = **100.0** ✓ (the two bases are shares of TOTAL portfolio GRI, so they sum to 100 jointly, not each). Category mappings (e.g. 3PL→Logistics & Supply Chain, Consumer & Retail→Other Retail Trades, Government-linked→Government Related) are sensible; `category_raw` preserves source labels.

### Top tenants (PAGE 35 L&I, PAGE 36 Commercial) — PASS
20 rows: ranks 1-10 = Top-10 L&I (Hermes 3.6 … Bakker 1.2, Σ=18.2 ≈ disclosed 18.1%), ranks 11-20 = Top-10 Commercial (Services Australia 4.5 … Olympus 0.5, Σ=14.9 = disclosed 14.9%). Every name/country-derived-industry/%/basis matches source. Note: `revenue_pct` is NOT globally monotonic in rank (rank 11 = 4.5% > rank 1 = 3.6%) because it is two segment-scoped Top-10 lists concatenated — see §5.

### Key ratios & counts — PASS
aggregate_leverage 33.0 (PAGE 30-31) ✓; interest_coverage_ratio 5.0 ✓; cost_of_debt 2.8 ✓; weighted_avg_debt_maturity 2.4 ✓; WALE 4.2 ✓; portfolio_occupancy 94.5 (L&I 98.8 / Commercial 87.5) ✓; number_of_unitholders 28,132 (Statistics of Unitholdings) ✓; units 3,762,201,517 → 3,762,202k ✓; properties_location = 5 countries ✓.

### Profile (Statement by Manager PAGE 201, Report of Trustee PAGE 200, Corporate Info) — PASS
reit_manager "Frasers Logistics & Commercial Asset Management Pte. Ltd." ✓; trustee "Perpetual (Asia) Limited" ✓; sponsor "Frasers Property Limited" ✓ (Group is a subsidiary of FPL, PAGE 217); sub_sector "Diversified" and income_model "conventional" both defensible.

### Property transactions (Note 32 PAGE 293, subsequent events PAGE 295) — PASS
Tx1 German 89.9% four-property acquisition: cash paid 174,390 / IP acquired 188,293 / 27 Mar 2024 ✓ (Note 32). Tx2 Maastricht forward-funded (17 Nov 2023, 22,036 carrying) ✓. Tx3 2 Tuas South Link 1 SPA 17 Oct 2024 @ 140.3m ✓ (subsequent). Tx4 28-German 10.1% minority sale €23.3m ≈ S$33.3m, 5 Nov 2024 ✓ (subsequent).

---

## 5. Nulls / inference audit

**Confirmed genuinely absent (correct nulls):**
- `financial.perpetual_security_holders` null — FLCT has no perpetual securities; attribution is unitholders + NCI only (PAGE 202) ✓.
- `properties.net_property_income` / `npi_pct` null on all rows — NPI is disclosed only in aggregate (PAGE 202, 321,974) and by 6-segment geography×asset-class (Note 27), never per property; the operating Property Profile has a per-property Gross Revenue column but NO NPI column. Correct structural null ✓.
- `properties.gla` / `gfa` null — only net lettable area (sqm) disclosed in the Property Profile; `nla` correctly populated. Correct ✓.
- Maastricht IPUD occupancy_rate/gross_revenue null — disclosed as "N.A." / under development at FYE (PAGE 39). Correct ✓.
- `performance.adjusted_distributable_income` null — no "Adjusted distributable income" label in this AR (see O2; defensible).

**Reasonable / correctly-flagged inferences:**
- `properties` local-currency values (Ellesmere GBP 68.0m, Central Park A$365.3m 50% interest, Maastricht EUR 15.4m) recovered from the Developments table (PAGE 39) with market_valuation held at the SGD audited carrying — sound.
- Central Park 50% effective interest: ownership=50 with market_valuation = full consolidated carrying 324,488 — correctly flagged.
- Footnote-(c) ROU leaseholds (Melbourne Airport, Wetherill Park, Port Kembla, Koperstraße Nuremberg): audited carrying > operating Property Profile $m because it includes the right-of-use asset — correctly flagged, audited carrying used.

**Observation (not a defect):** top_tenants `rank` is a synthetic concatenation of two segment-scoped Top-10 lists; there is no field marking rows 1-10 as L&I vs 11-20 as Commercial (recoverable only via `industry`), and `revenue_pct` is therefore not monotonic in rank. Downstream sorting by rank≈% will misorder. Consider a segment tag if the schema allows.

---

## 6. Confirmed-correct highlights

- **Every audited FS figure exact** to the Group 2024 column across STR, balance sheet, cash flow, movements, and Notes 3/4/5/6/7/9/23.
- **Full STR reconciles to total return 150,677 exactly** — no material line missing; tax and net-finance correctly signed.
- **All three derived identities hold to the dollar**; net-finance-cost decomposition confirmed against Note 6.
- **Portfolio valuation sum ties exactly (6,928,373k)** with a clean completed/IPUD split; the 6,773.2m headline vs audited 6,928.4m gap is correctly explained.
- **Trade-mix 22-cell matrix and both Top-10 tenant lists captured verbatim** — exactly the nuance usually mangled; the income-available (210,337) vs distributable-income (255,515) distinction handled correctly.
- **FYE, currency, trustee (Perpetual (Asia)), manager, sponsor, no-perpetual/NCI structure** all correct and internally consistent across profile / performance / _notes.

---

## 7. Could NOT verify

- **Distribution `ex_date`** (both periods) — not disclosed in the audited Distribution Statement or Note 23 (only pay dates); genuinely unavailable from this parse.
- **Per-property NPI in SGD** — genuinely not disclosed at property level (segment-only). Null stands; unverifiable by design.

---

## Fix list (page-cited)
1. `financial.json` → `income_stmt_metrics.revenue_breakdown` → set to the 3 Note-3 lines: Rental income 361,939,000; Recoverable outgoings 83,426,000; Other revenue 1,309,000 (**PAGE 245**). [MED]
2. `performance.json` → `distribution_record[0].pay_date` → `"2024-06-18"` (3.48c H1 distribution "paid on 18 June 2024", **PAGE 289 / PAGE 203**). [LOW]
3. `performance.json` → consider `adjusted_distributable_income` → 255,515,000 ("Distributable income", the DPU basis, **PAGE 203**); currently only in flags. [LOW / judgment]
4. `performance.json` → `number_of_properties` (if schema supports) → 112 (**PAGE 34**). [LOW / schema-dependent]

No changes made — user gates fixes.
