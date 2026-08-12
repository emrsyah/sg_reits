# J69U — Frasers Centrepoint Trust (J69U.SI) FY2025 — Forensic Extraction Audit

Auditor: independent verification against source. Navigated the report myself from the TOC: Trust Structure (p5), Glossary (p2), 5-year/financial highlights (pp7-11), Financial Review per-property GR/expenses/NPI table (pp34), Trade mix + Top 10 tenants (p31), Portfolio overview tables (pp68-69), property profile cards (NEX p70-71, Northpoint p72-73, others), Statement of Total Return (p146), Distribution Statement (p147), Portfolio Statement (p149-150), Statement of Financial Position (p145), Gross Revenue Note 16 + Property Expenses Note 17 (p186), Notes 18-21 (pp187-188), Segment note (p205), Statistics of Unitholdings (pp216-217), Substantial Unitholders + EFR use of proceeds (pp217-218), Corporate Information (p221). Did NOT consult any extractor tooling / page-map / anchors.

Source: `parsed_reports_datalab/18_J69U.SI_Frasers-Centrepoint-Trust_FY2025/full.md` (page-anchored `<!-- PAGE N -->`).

Note on page numbering: the markdown `<!-- PAGE N -->` anchors equal the printed PDF page labels in this report, so cited pages below are directly comparable to the extraction's `source_page` values.

---

## 1. Verdict & confidence

**Grade: MINOR ISSUES.**

The KNOWN OPEN ITEM is RESOLVED cleanly: the sponsor-merge miss did NOT survive — `profile.management` correctly lists all four roles including **sponsor = Frasers Property Limited** (confirmed from the Trust Structure diagram p5, the Glossary p2, the Substantial-Unitholders chain p217, and the Y10 divestment-to-Sponsor note p9). All hard financials reconcile to the dollar: the full Statement of Total Return ties to "Total return for the financial year" (199,862k) exactly; gross revenue, property expenses, NPI, per-property GR/NPI, the audited Portfolio-Statement valuation total (6,449,000k), DPU, distributable income, unitholders, trade mix (Σ=100%) and top-tenants (Σ=18.9%) all check out against source.

The defects are: (a) the recurring **`finance_income` mis-bucketed as `statement="revenue"`** in income_components, which breaks the Σrevenue = gross_revenue cross-section tie (the HMN-class bug); (b) the **combined "Northpoint City" GR/NPI (85,573k / 62,264k) wrongly attributed to North Wing alone** when the report discloses it only as a 3-component combined figure (NW+SW+Y10); (c) **two disclosed distribution pay-dates left null** (30 May 2025); (d) a **source_page error** (Notes 16/17 are p186, cited as p187); (e) **no `_notes.inferred[]` array at all** — every back-derived `lease_expiry_date` (and `lease_term_years`) is an unflagged inference; (f) `trade_mix.pct_basis`/`top_tenants.pct_basis` = "gri" omits the disclosed Hougang-Mall-excluded scope; (g) `_notes.reconciliation` mis-states `income_components_revenue_sum`/`_expense_sum` (internally inconsistent with the shipped file).

Tally: **CONFIRMED ≈ 40+** · **DISCREPANCY = 5** · **SUSPECTED-OMISSION = 3** · **UNVERIFIABLE = 1**

---

## 2. Discrepancies

### D1 — income_components: `finance_income` 624k mislabelled `statement="revenue"` (MED, HIGH confidence)
- Extraction: `finance_income` 624,000 tagged `statement: "revenue"`, `source_page: 146`.
- Source (Statement of Total Return, p146): "Gross revenue" (Note 16) = 389,603k comprises ONLY the four Note-16 lines (gross rental 351,360 + gross turnover rental 15,779 + car park 7,880 + Others 14,584). "Finance income" 624 sits **below** Net property income, as a separate line, NOT part of gross revenue.
- Consequence: Σ(income_components where statement=revenue) = 351,360+15,779+7,880+14,584+**624** = **390,227k**, which does NOT equal `performance.gross_revenue` (389,603k). The cross-section tie-out FAILS by exactly 624 = finance_income.
- Fix: re-tag `finance_income` as `statement="adjustment"` (it's a below-NPI income item; the full signed reconciliation already treats it as such — see §5). Do NOT alter the amount. Same defect class as HMN D1.

### D2 — properties: combined "Northpoint City" GR/NPI assigned to North Wing only (MED, HIGH confidence)
- Extraction: `Northpoint City North Wing` carries `gross_revenue` 85,573,000 and `net_property_income` 62,264,000; `Northpoint City South Wing` carries both null.
- Source (Financial Review table p34 footnote 1; Northpoint card p73 footnote 3; portfolio overview p68 footnote 14): the **85,573 / 62,264 figure is the COMBINED Northpoint City** = North Wing + South Wing + Yishun 10 Retail Podium. It is never split by wing. The audited per-property GR/NPI table (p34) lists a single "Northpoint City" line, not separate wings.
- Consequence: North Wing's GR/NPI is overstated (it absorbs South Wing's and Y10's contributions); South Wing's null is correct only because the split is undisclosed, but North Wing's value is fabricated by attribution.
- Fix: set North Wing `gross_revenue`/`net_property_income` to **null** as well (individual wing GR/NPI not separately disclosed, p34), OR record one combined "Northpoint City" row. The combined 85,573/62,264 belongs to the combined asset, not North Wing. `_notes` already acknowledges the limitation but the shipped properties.json contradicts it.

### D3 — distribution_record: two disclosed pay-dates left null (LOW-MED, HIGH confidence)
- Extraction: tranche 1 (6.054c, 1 Oct 2024–31 Mar 2025) and tranche 2 (0.096c, advance, 1–3 Apr 2025) both have `pay_date: null`.
- Source p146 distribution policy (line: "For FY25, the distribution for (a) the first half-year ... and (b) the advanced distribution for the period from 1 April 2025 to 3 April 2025 was made on **30 May 2025**"). Both tranches were paid 30 May 2025.
- Fix: set `pay_date = "2025-05-30"` for both the 6.054c and 0.096c tranches. (Tranche 3 pay_date 2025-11-28 is correctly captured, p147 footnote 2 / p209.)

### D4 — income_components source_page: Notes 16 & 17 lines cite p187, actually p186 (LOW, HIGH confidence)
- Extraction: all Note-16 revenue lines and all Note-17 property-expense lines cite `source_page: 187`.
- Source: Note 16 (Gross revenue) and Note 17 (Property expenses) are printed on **PAGE 186** (`<!-- PAGE 186 -->` precedes both tables; PAGE 187 begins with Note 18 Finance costs). 
- Fix: change `source_page` 187 → **186** for the four revenue lines and the eleven Note-17 expense lines. (The below-NPI items finance_costs/asset_management_fees/etc. cite p146 — defensible, they appear on the Statement of Total Return; their detailed notes are p187.)

### D5 — `_notes.reconciliation` internally inconsistent with the shipped income_components (LOW, HIGH confidence)
- `_notes.reconciliation.income_components_revenue_sum = 389,603` and `income_components_expense_sum = 111,623`, both flagged `*_matches_total_return: true`.
- But the shipped income_components.json tags **finance_income as revenue** (so its revenue rows sum to 390,227, not 389,603) and tags finance_costs/asset_management_fees/valuation/trustee/audit/professional/other_charges as `expense` (so its expense rows sum to ~242,392, not 111,623). The reconciliation note describes numbers that are NOT what the file contains.
- Fix: once D1 is applied, recompute and correct these reconciliation fields (or scope them to "property-level revenue/expense only").

---

## 3. Suspected omissions

### O1 — NEX & Waterway Point GR/NPI are disclosed (100% basis) but left null (LOW-MED, schema home exists)
The portfolio overview (p68) and the JV mall cards disclose per-property GR/NPI on a 100% basis: NEX GR 133,701k / NPI 102,252k (p68, p71); Waterway Point GR 86,183k / NPI 64,484k (p68, p35-area card). The extraction left `gross_revenue`/`net_property_income` null for both JV malls. These are disclosed on a 100%-basis scope (FCT owns 50%), so they don't fold into the consolidated SGD totals, but the blanket null is incomplete. SEVERITY: LOW-MED (capturable with a 100%-basis scope note).

### O2 — South Wing address postal code dropped (LOW, schema home exists)
`Northpoint City South Wing` address = "1 Northpoint Drive" in extraction; source card (p73) gives "**1 Northpoint Drive, Singapore 768019**". North Wing similarly is "930 Yishun Avenue 2" vs source "930 Yishun Avenue 2, Singapore 769098" (p73). Cosmetic. SEVERITY: LOW.

### O3 — trade_mix "% of total NLA" second basis not captured (LOW, no clean schema home)
The trade mix table (p31) discloses both "% of total GRI" and "% of total NLA" per category; only the GRI basis is captured (correct primary basis). The NLA column has no schema home — correctly omitted, flagged here for completeness. SEVERITY: LOW (no home).

---

## 4. Reconciliation results (independently re-computed)

### Statement of Total Return tie-out (Group, p146) — PASS
Using income_components values, correctly bucketed:
- Σ(revenue, four Note-16 lines) = 351,360+15,779+7,880+14,584 = **389,603k** = gross revenue ✓
- Σ(property expenses, Note 17) = 33,736+35,490+14,903+15,495+6,306+1,864+1−3+29+10+3,792 = **111,623k** ✓ → NPI = 389,603 − 111,623 = **277,980k** ✓
- + finance income 624 − finance costs 86,163 − asset mgmt 41,187 − valuation 148 − trustee 1,132 − audit 312 − professional 1,058 − other charges 769 = Net income **147,835k** ✓ (matches p146)
- + share of JV results 62,645 + gain on divestment 128 − FV change of IPs 11,130 − fx loss 3 = Total return before tax **199,475k** ✓
- + taxation 387 = **Total return for the financial year 199,862k** ✓ exact.
- income_components is **complete** for the Group column. The "Loss on divestment of investment in associate" line is 0 in 2025 (immaterial); EPU lines are not income components.

### Cross-section revenue tie (Σ income_components revenue = gross_revenue) — **FAIL**
390,227k ≠ 389,603k; the 624k gap = finance_income mis-bucketed as revenue (D1). After re-tagging finance_income → adjustment, this passes.

### Gross revenue (Note 16, p186) — PASS
351,360 + 15,779 + 7,880 + 14,584 = **389,603k** ✓ = p146 gross revenue ✓ = performance.gross_revenue ✓.

### Property expenses (Note 17, p186) — PASS
Σ11 lines = **111,623k** ✓ = p146 property expenses ✓.

### Per-property GR / NPI (Financial Review table, p34) — PASS
- GR: 97,704 + 85,573(Northpoint combined) + 54,990 + 44,502 + 35,886 + 27,124 + 31,635 + 12,147 + 42(Changi adj) = **389,603k** ✓.
- NPI: 69,931 + 62,264 + 38,932 + 33,335 + 26,075 + 17,118 + 21,715 + 8,358 + 252(Changi adj) = **277,980k** ✓.
- The `_notes` "252k Changi City Point adjustment" gap note is correct (p34 footnote 2: divested 31 Oct 2023, FY25 figures are adjustments). Caveat: the 85,573/62,264 is combined Northpoint, mis-attributed in properties.json (D2).

### Portfolio Statement valuation sum (audited, p149) — PASS
Σ(10 directly-held carrying values) = 1,354,000 + 800,000 + 1,133,000 + 817,000 + 665,000 + 563,000 + 467,000 + 431,000 + 219,000 + 0(Y10 divested) = **6,449,000k** = "Investment properties, at valuation" p149 ✓ = Statement of Financial Position IP line p145 (6,449,000) ✓. NEX & Waterway are equity-accounted "Investment in joint ventures" 1,042,638k (p149), correctly OUTSIDE this total — the JV-vs-consolidated trap was navigated correctly.

### Portfolio_value (Tier A headline) — PASS
performance.portfolio_value = 8,200,000,000 = "aggregate appraised value... approximately $8.2 billion" (p7 highlights, line: includes proportionate share of NEX and Waterway Point). Correct Tier-A figure incl. proportionate JV. ✓ (audited consolidated IPs alone = 6,449.0m; JV at book 1,042.6m; the $8.2bn is the proportionate-appraised headline.)

### Distribution — PASS
DPU 12.113c (p146/p20) = 6.054 (1H) + 6.059 (2H, = 0.096 + 5.963) ✓. Distributions to Unitholders 233,166k (p147) = performance.net_distributable_income ✓ (note: "Distributable income for the financial year" 233,180k is the alternative reading — see §6). Tranches and periods all match p147.

### Trade mix → 100% (p31) — PASS
38.7+15.6+11.5+7.5+6.2+3.2+3.0+2.8+2.4+2.4+1.9+1.9+1.8+1.1 = **100.0%** ✓ (extraction omits the source's "Vacant 0.0%" row — immaterial). pct_basis scope incomplete (see §6).

### Top 10 tenants (p31) — PASS
10 rows, names/percentages/ranks all match p31; Σ = **18.9%** ✓ (matches disclosed "Total for Top 10 18.9%").

### Unitholders — PASS
17,713 (p216, as at 25 Nov 2025) ✓. Units outstanding 2,034,952,990 ✓.

---

## 5. Nulls / inference audit

**Confirmed genuinely absent (correct nulls):**
- `Northpoint City South Wing` GR/NPI/occupancy/GLA/NLA — combined with North Wing in every disclosure (p34, p68, p73); individual figures genuinely not split. Correct null + correct reason in `_notes`. ✓
- `Central Plaza` GLA null — portfolio overview (p68-69) shows GFA blank for Central Plaza, NLA only (171,136 sf). Correct. ✓
- `NEX`/`Waterway Point` market_valuation absent from the audited Portfolio Statement — correct; they're equity-accounted JVs (1,042,638k aggregate, p149). Extraction recorded the 100%-basis card valuations (2,141.0m / 1,331.0m) with `value_basis="joint_venture_100pct"` and noted 50% ownership — reasonable handling. ✓
- `Yishun 10 Retail Podium` market_valuation null, status="divested" — p149 shows "−" for FY25 (FY24 was 34,000); divested 23 Sep 2025 (p9). Correct. ✓

**Wrong / incomplete null-or-attribution reasons:**
- `Northpoint City North Wing` GR/NPI are NOT a correct null-handling — they were filled with the **combined** figure (D2). The truthful state is null (undisclosed split).
- `distribution_record` pay-dates for tranches 1 & 2 are NOT genuinely absent — disclosed as 30 May 2025 (D3).
- NEX/Waterway GR/NPI nulls are over-broad — disclosed on 100% basis (O1).

**Unflagged inferences (HMN-class defect):**
- `_notes.json` has **no `inferred[]` array at all.** Every `lease_expiry_date` in properties.json is **derived/back-calculated** — the Portfolio Statement (p149) and cards disclose only "99-year leasehold from/commencing [date]", never an explicit expiry. e.g. Causeway Point expiry 2094-10-29 = 30 Oct 1995 + 99y; NEX 2107-06-25 = 26 Jun 2008 + 99y. All 12 expiry dates and the uniform `lease_term_years=99` are unflagged inferences. Values are internally consistent (commencement + 99y − 1 day), so low risk, but provenance is understated. Should be recorded in `_notes.inferred[]` with basis "computed from disclosed commencement date + 99-year term; explicit expiry not stated."
- `valuation_date = 2025-09-30` uniform across all rows — correct (Portfolio Statement "As at 30 September 2025") but is an assigned/uniform value.
- `top_tenants.trade_sector` and several `trade_mix.category` canonical mappings are remapped from multi-sector source labels (e.g. NTUC FairPrice source = "Supermarket & Grocers, Food & Beverage, Beauty & Healthcare" → single "Departmental Store/Supermarket"; Courts source "Electrical & Electronics" → "Other Retail Trades") — defensible canonicalisation but unflagged. LOW.

---

## 6. Confirmed-correct highlights (balance)

- **Sponsor-merge issue RESOLVED.** profile.management lists all four roles correctly: reit_manager = Frasers Centrepoint Asset Management Ltd. (p5/p221), trustee = HSBC Institutional Trust Services (Singapore) Limited (p5/p221), property_manager = Frasers Property Retail Management Pte. Ltd. (p5), **sponsor = Frasers Property Limited** (Glossary p2 "Sponsor: Refers to Frasers Property Limited"; ownership chain p217). source_page=5 (Trust Structure) is appropriate. sub_sector="Retail" ✓ (suburban retail malls + one office, primarily retail). income_model="conventional" ✓.
- **All audited FS numbers exact** to the Group column: gross revenue 389,603; property expenses 111,623; NPI 277,980; every below-NPI line; share of JV 62,645; FV change −11,130; tax +387; total return 199,862.
- **Full Statement of Total Return reconciles to total return (199,862k) exactly** — income_components complete, no material line missing.
- **All 12 properties present** with correct categories (Central Plaza correctly = Office), correct 2025 audited valuations for the 10 directly-held (Σ=6,449,000k), Y10 divested handled, NEX/Waterway as JV 100%-basis. Per-property GLA/NLA/occupancy spot-checked against p68-69 — all match (Causeway 629,167/419,782/92.3; Tampines 391,551/278,059/99.8; Hougang 232,782/165,765/73.5; etc.).
- **Tenure** verbatim → tenure_raw, enum Leasehold, commencement dates all match the Portfolio Statement (p149). 
- **Property transactions** correct: NPCSW acquisition agreed value 1,133.0m, completed 26 May 2025 (p8); Y10 divestment 34.5m to Sponsor, completed 23 Sep 2025, gain 128k (p9). 
- **trade_mix scope** (excl. Hougang) and **top-tenant scope** are noted in `_notes` (just not in the pct_basis field).
- **FY-end discipline:** correctly used financial_year=2025 = Oct 2024–Sep 2025, date=2025-09-30 (FY ends 30 Sep, not Dec).

---

## 7. Could NOT verify

- **`property_transactions` acquisition note "$393.2 million total acquisition outlay"** — I could not locate this exact figure in the source within the pages navigated. The disclosed acquisition headline is "$1.17 billion" total (p8) / agreed property value $1,133.0m (p149); the EFR raised $421.3m of which $415.8m funded the NPCSW acquisition pending (p218). The $393.2m may be a net-cash-outlay derivation but is not on the pages read — flag for confirmation; the shipped `consideration` (1,133,000,000 = agreed property value) is itself correct and disclosed.
- **`net_distributable_income` 233,166 vs 233,180** — both are disclosed on p147 ("Distributions to Unitholders 233,166" vs "Distributable income for the financial year 233,180"). 233,166 ties to DPU×units and is defensible; 233,180 is the literal "distributable income for the financial year." Not a defect, but the choice is a judgement call — flag for the schema owner's preferred convention.
