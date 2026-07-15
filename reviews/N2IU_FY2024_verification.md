# N2IU — Mapletree Pan Asia Commercial Trust (MPACT, N2IU.SI) FY2023/24 — Forensic Extraction Audit

Auditor: independent verification against source. Navigated the report myself from the TOC — Financial Highlights / 5-year summary (pp.6-7), Letter to Unitholders (pp.13-16), Highlights & Unit Performance (pp.18-20), Financial & Capital Management Review incl. portfolio valuation table (pp.32-37), Portfolio / Tenant Analysis (pp.42-43), Operations Review & property cards (pp.44-65), the audited financial statements (Statements of Profit or Loss p145, Comprehensive Income p146, Financial Position p147, Distribution Statements pp.148-149, Cash Flows pp.150-151, Portfolio Statement pp.152-159), Notes 3-6 (p177), Note 5 finance expenses (p178), Note 9 EPU (p187), Note 18 JV, Note 20/leverage note (p216), Note 31 segment reporting (p220), Corporate Governance / structure (pp.44-45 trust diagram, p11 corporate), Statistics of Unitholdings (pp.227-228), Corporate Directory (pp.231-233). Did NOT consult any extractor tooling, page-map, gather notes, adapter output, or the FY2025 extraction.

Source: `parsed_reports_datalab/29_N2IU.SI_Mapletree-Pan-Asia-Commercial-Trust_FY2024/full.md` (page-anchored).

**Confirmed FYE: 31 March 2024 (FY23/24).** Header on every audited statement reads "For the financial year ended 31 March 2024" / "As at 31 March 2024" (pp.145-151); auditor's report dated 16 May 2024 (p144). All financials verified against the **Group 2024** column (not the MPACT-only trust column, not the 2023 comparative).

Presentation: SGD ('000 tables, verified ×1000). Multi-currency portfolio (SGD/HKD/RMB/JPY/KRW) presented in SGD in the audited statements; per-property local-currency figures appear only in the Operations Review. Perpetual securities + non-controlling interest both present and correctly attributed.

---

## 1. Verdict & confidence

**Grade: MINOR ISSUES.**

The extraction is numerically excellent. Every audited financial-statement figure I re-derived matched the Group 2024 column to the dollar; the full Statement of Total Return reconciles exactly to "Profit for the financial year after tax" of S$583,070k; the balance sheet, cash flow, distribution, DPU, portfolio-valuation sum, trade-mix and top-tenant tables all tie out; and the three trap items the assignment flagged were all handled correctly — the **adjusted ICR (2.9)** basis is chosen and documented, the **rank-6 "Undisclosed Tenant"** is correctly stored as a null row, and the **pharma → Healthcare & Wellness** mapping is defensible. The only real defects are: (a) `financial.revenue_breakdown` is an empty array even though Note 3 (p177) discloses a clean 3-line gross-revenue breakdown — a genuine omission into an existing schema field; and (b) a **wrong page citation** inside `performance.flags` (plain ICR is disclosed on **p216**, not "p219"). Neither touches a headline value.

Tally: **CONFIRMED ≈ 40** · **DISCREPANCY = 1** (LOW, documentation) · **SUSPECTED-OMISSION = 3** (1 MED, 2 LOW) · **UNVERIFIABLE = 1**

---

## 2. Discrepancies

### D1 — `performance.flags` cites plain ICR at "p219"; it is actually disclosed on p216 (LOW, documentation only)
- Extraction flag text: *"interest_coverage_ratio=2.9 = adjusted-ICR basis (plain ICR 3.0, **p219**)"*.
- Source: the leverage/ICR note is on **p216** (`<!-- PAGE 216 -->`, lines 9602-9628): "Interest coverage ratio ('ICR') **3.0 times**" and "Adjusted ICR **2.9 times**". p219 is the operating-expense-ratio / segment area.
- Consequence: none numerically — both ICR values are correct and the chosen value (2.9, adjusted) is right (see §5). A downstream reader chasing the plain-ICR provenance would land on the wrong page. Severity LOW. Confidence HIGH.

*(No value-level discrepancy was found anywhere in the five files under test.)*

---

## 3. Suspected omissions

### O1 — `financial.revenue_breakdown = []` but Note 3 (p177) discloses the gross-revenue breakdown (MED; schema home exists)
- The field exists and is empty. Note 3 "GROSS REVENUE" (p177, Group 2024) discloses:
  - Gross rental income **870,694**; Car parking income **24,817**; Other operating income **62,577**; total **958,088** ✓ (= gross revenue).
  - Plus turnover rental of **S$15,837,000** disclosed within gross rental income (Note 3(a), p177).
- This is disclosed detail dropped into an existing, empty array field. SEVERITY: MED (clear schema home, clean disclosure). Fix: populate `revenue_breakdown` with the three Note-3 categories (×1000).

### O2 — Property-operating-expense category breakdown (Note 4, p177) not captured (LOW; unclear schema home)
- Note 4 (p177, Group 2024) breaks the S$230,159k property operating expenses into 9 lines: operation & maintenance 39,096 · utilities 38,237 · property tax 60,103 · other taxes 4,845 · property & lease management fees 37,382 · staff costs 30,024 · marketing & professional 11,066 · depreciation 1,072 · other operating 8,334.
- `operating_expense_breakdown` only carries the three **trust-level** expenses (base fees / trustee / other trust = 55,600), which is correct for the `operating_expense` line — the Note-4 property-opex categories have no obvious schema home. SEVERITY: LOW. Flagged for completeness.

### O3 — Top-tenant "Property(ies)" column and per-tenant footnotes not captured (LOW; likely no schema home)
- The p43 top-10 table discloses each tenant's property (Google→MBC, BMW→Gateway Plaza, TaSTe→Festival Walk, HSBC→MBC & Festival Walk, Seiko→SMB, HP→HPB, Merrill Lynch→BOAHF, NTT→MBP, Arup→Festival Walk) plus lease-expiry footnotes (Seiko lease expiring 30 Jun 2024; NTT expired 31 Mar 2024). `top_tenants.industry` is null for all rows — the AR does not give a tenant-industry column here, so null is correct. No property/industry field in the tenant schema → not capturable. SEVERITY: LOW.

---

## 4. Reconciliation results (independently re-computed)

### Statement of Total Return tie-out (Group 2024, p145) — PASS (exact)
Using `financial.line_items`:
- Σ(revenue) = **958,088**
- Σ(expense) = 230,159 + 227,994 + 49,848 + 1,819 + 3,933 = **513,753**
- Σ(adjustment, signed) = +2,512 + 4,923 + 2,598 + 141,804 + 6,380 − 19,482 = **+138,735**
- 958,088 − 513,753 + 138,735 = **583,070k = "Profit for the financial year after tax"** (p145, line 7002) ✓ exact = `net_income`.
- Line completeness: performance fees were **nil** for the Group in FY23/24 (p145) → correctly omitted. Dividend income is nil at Group level (MPACT-only item). No missing/extra line.

### Revenue / NPI / opex identities — PASS
- `total_revenue` 958,088 == `performance.gross_revenue` 958,088 == Σ(revenue line_items) 958,088 (p145) ✓. Finance income (2,512) is correctly tagged `adjustment`, NOT revenue — so the revenue cross-check is clean (contrast HMN D1).
- `gross_income` 727,929 == Net property income (p145/p177) ✓.
- `cost_of_revenue` 230,159 == property operating expenses (Note 4, p177) ✓.

### Derived-metric identities (I1–I3) — PASS
- I1: operating_income 672,329 = gross_income 727,929 − operating_expense 55,600 ✓ (opex = base fees 49,848 + trustee 1,819 + other trust 3,933 = 55,600 ✓).
- I2: ebit 828,034 = pretax 602,552 + interest_expense_non_operating 225,482 ✓.
- I3: net_income 583,070 = pretax 602,552 − income_taxes 19,482 ✓ (tax is an expense, stored positive; net = pretax − expense).
- interest_expense_non_operating 225,482 = finance expenses 227,994 − finance income 2,512 (p145; Note 5 p178 confirms finance expenses = 227,994) ✓. Group has no dividend/investment income line to net.
- non_operating_income_or_loss −69,777 = 2,512 − 227,994 + 4,923 + 2,598 + 141,804 + 6,380 ✓.

### Attribution split — PASS
Unitholders 577,940 + Perpetual securities holders 4,804 + Non-controlling interest 326 = **583,070** = net_income (p145, lines 6999-7002) ✓. All three stored positive.

### Balance sheet (p147, Group 2024) — PASS
total_asset 16,662,291 ✓; current assets 200,879 ✓; non-current assets 16,461,412 ✓; current liabilities 1,252,545 ✓; non-current liabilities 5,938,544 ✓; total liabilities 7,191,089 ✓; net assets/equity 9,471,202 ✓; working_capital = 200,879 − 1,252,545 = −1,051,666 ✓; NAV/unit 1.75 ✓; units in issue 5,252,985k ✓.

### Cash flow (p150, Group 2024) — PASS
operating 725,032 ✓; investing −56,295 ✓; financing −719,878 ✓; net = 725,032 − 56,295 − 719,878 = **−51,141** ✓; capital_expenditure −64,798 = "Additions to investment properties" (p150) ✓.

### Distribution & DPU — PASS
- NDI 468,569 = "Amount available for distribution **for the year**" (p148, Group) = 577,940 + Note-A adjustment (−109,371) ✓. Correctly EXCLUDES the S$154,745k opening carried-forward balance and is NOT after-retention — convention correct.
- distribution_paid 465,202 = "Total Unitholders' distribution (incl. capital distribution)" Note B (p148/149) ✓.
- DPU 8.91c (p5/p18/p33; "Total DPU 8.91" line 1671) ✓ = Σ quarters 2.18 + 2.24 + 2.20 + 2.29 (p18 line 1709) ✓. 4Q FY23/24 (2.29c) was declared after balance-sheet date (Note, p223 line 9914) and is correctly included on the declared-for-year DPU basis.
- NDI − distribution_paid = 3,367 (the change in the carried-forward "amount available" balance; 154,745 → 158,112). `distribution_basis="full_payout_no_retention_line"` is accurate — no explicit retention line exists. Minor conceptual note: distribution_paid is on a *paid-during-the-year* basis (includes 4Q FY22/23 2.25c, excludes 4Q FY23/24 2.29c) while DPU/NDI are declared-for-the-year — both correctly labelled in the flag.

### Portfolio valuation sum — PASS (exact)
Σ(properties.json market_valuation) for the 18 audited rows = Singapore (3,358,000 + 2,287,000 + 790,000 + 765,000 + 350,000 + 1,568,000 = **9,118,000**, matches "Singapore properties S$9,118.0m", p33) + Festival Walk 4,270,622 + Gateway 1,140,523 + Sandhill 435,314 + Japan (78,973+23,800+51,477+28,127+164,077+178,501+69,778+318,237+371,426 = 1,284,396) = **16,248,855k** = audited Investment Properties (p147 Note 14 / Portfolio Statement total p159 / segment total p220) ✓ to the dollar. Adding The Pinnacle Gangnam 50%-JV 250,600 → 16,499,455k ≈ the disclosed **S$16,499.5m** headline "Portfolio Property Value" (p7 line 397; p33 line 1760/1786), the ~45k gap being million-level rounding of the TPG line. TPG correctly flagged as an equity-accounted JV outside the consolidated investment-property line.

### Trade mix (p43) — PASS
20 rows, all present, values verbatim; Σ = 13.8+13.8+8.3+7.4+5.8+5.2+4.8+4.1+4.1+3.9+3.4+3.3+2.8+2.3+2.2+2.2+2.1+2.1+2.1+6.4 = **100.0%** ✓, single basis `gri`. Pharmaceutical 2.1% → `category="Healthcare & Wellness"` is a defensible taxonomy mapping (raw "Pharmaceutical" preserved in `category_raw`); Beauty & Health 3.9% also maps to Healthcare & Wellness — two distinct raw rows, no collision. `Others` 6.4% carried as a row. Canonical-category assignments (e.g. Automobile→"Other Office Trades") are subjective but internally consistent and never alter a percentage.

### Top tenants (p43) — PASS
10 ranks, contiguous, descending-ish: Google 6.0 / BMW 3.2 / TaSTe 2.0 / HSBC 2.0 / Seiko 1.8 / **rank-6 null** / HP Japan 1.7 / Merrill Lynch 1.7 / NTT 1.7 / Arup 1.6. Σ(disclosed, excl. rank-6) = 21.7 ≈ disclosed "Total 21.6% (excluding the undisclosed tenant)" (p43 footnote 3; 0.1 rounding) ✓. **Rank 6 correctly stored with client_name/revenue_pct = null** — the source literally prints rank 6 as "Undisclosed Tenant | – | –" (p43 line 2192). This is the correct behaviour (not a data miss).

### EPU / units — PASS
weighted_avg_shares_basic 5,246,391k = "Weighted average number of units outstanding" (Note 9, p187) ✓; EPU 577,940 / 5,246,391 = 11.02c ✓ (p145/p187). Diluted = basic (no dilutive instruments) ✓.

---

## 5. Nulls / inference audit

**Correct / defensible choices:**
- **`interest_coverage_ratio` = 2.9 (adjusted basis)** — both ICR figures are disclosed on p216: plain ICR **3.0** and Adjusted ICR **2.9**. The report's headline presentation uses the adjusted ICR (5-year Financial Highlights table p7 line 409 shows only "Adjusted ICR 2.9"; Letter to Unitholders p14 "adjusted ICR of approximately 2.9 times"; MAS >45% leverage test keys off adjusted ICR ≥2.5, footnote 3 p216). Choosing 2.9 is correct/preferred; the flag documents the plain-ICR alternative (only the page cite is wrong — D1). CONFIRMED.
- `portfolio_value` 16,499,500,000 — a **directly disclosed** headline ("Portfolio Property Value S$16,499.5m", p7/p33), not derived. CONFIRMED.
- `adjusted_distributable_income` null — no separate "adjusted" DI is disclosed; only "Amount available for distribution for the year" (captured as NDI). Correct null.
- `distribution_record[].ex_date / pay_date` null — the Distribution Statement discloses period + DPU + amount, but no ex/pay dates per quarter. See §7.
- `top_tenants.industry` null (all) — no industry column in the p43 table. Correct.
- properties.json `columns_never_fillable` justifications spot-checked and hold: MBC I/II combined NPI (Note 31 p220 groups MBC; property card p46 gives one combined S$186.0m); MBC I/II combined NLA (2,888,738 sq ft combined, p46); VivoCity purchase price N.A. (pre-listing asset, footnote p46/p158); Japan/TPG freehold → no lease term/expiry (p156/p158). These are genuine narrow/absent disclosures, correctly reasoned.

**Notes (not defects):**
- `number_of_shareholder_units` 5,252,985,000 is the 31-Mar-2024 balance-sheet units in issue (p147), while `number_of_unitholders` 31,597 is as at **31 May 2024** (Statistics of Unitholdings, p227, total 31,597 / 5,257,046,281 units). Mixed as-at dates for two related fields; both individually correct and the flag records the 31-May basis for the unitholder count. Low-impact.

**Omitted disclosed data:** `revenue_breakdown` empty despite Note 3 (see O1) — the one clear miss.

---

## 6. Confirmed-correct highlights (balance)

- **Every audited FS figure exact to the Group 2024 column** — gross revenue, property opex, NPI, finance income/expense, each trust expense, all FV/FX/JV lines, tax, total return, attribution split, full balance sheet, full cash flow, distribution statement, DPU.
- **Statement of Total Return reconciles to S$583,070k to the dollar** with no missing/extra line; performance fee correctly recognised as nil.
- **Finance income correctly classified as an adjustment, not revenue** — the revenue cross-check is clean.
- **Portfolio valuation sums exactly** (18 audited rows → 16,248,855k; SG sub-total 9,118,000k matches the report's own split), TPG handled as a clearly-flagged 50% equity-accounted JV record reconciling to the S$16,499.5m headline.
- **Three assignment trap-items all handled correctly**: adjusted-ICR 2.9 basis chosen & documented; rank-6 "Undisclosed Tenant" stored as a null row; pharma→Healthcare & Wellness mapping defensible with raw label preserved.
- **Profile exact**: Manager MPACT Management Ltd. (p44/p231), Trustee DBS Trustee Limited (p44/p231), all four property managers MPMPL / MNAPML / MMSJ / MKM (p11/pp.231-233), Sponsor Mapletree Investments Pte Ltd (p11) — all present and correctly named.
- **Ratios/operational**: aggregate leverage 40.5% (p7/p216), cost of debt 3.35% (p7/p14), WADM 3.0y (p7), WALE 2.4y by GRI (p42), portfolio occupancy 96.1% (p41), NAV/unit 1.75 (p7/p147), unitholders 31,597 (p227) — all confirmed.
- **Multi-currency + perpetual + NCI structure** navigated correctly throughout.

---

## 7. Could NOT verify

- **Per-quarter ex-date / pay-date** for the four FY23/24 distributions — the audited Distribution Statement (pp.148-149) discloses period, DPU and amount but no ex/pay dates; not stated elsewhere in the parse. Nulls are acceptable (not disclosed).
- **Per-property SGD gross revenue / NPI** beyond the audited Portfolio-Statement rows — disclosed only in local currency on the property cards (pp.46-65) or combined at segment level (Note 31, p220); SGD-equivalents are not derivable without FX assumptions. The properties.json handling (local-currency where disclosed, MBC combined) is consistent with what the report actually gives.
