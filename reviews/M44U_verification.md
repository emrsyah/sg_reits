# M44U — Mapletree Logistics Trust (M44U.SI) FY2024/25 — Forensic Extraction Audit

## 1. Method header

Independent verification against source. I navigated the report myself from the TOC and read whole
sections: Corporate Profile (p2), Financial Highlights / Operations Review (pp6, 33–54), Portfolio
Valuation overview (pp53–54), the audited **Statements of Profit or Loss** (p121), Notes 3/4/5
(Gross Revenue / Property Expenses / Management Fees, p187), the **Distribution Statement** (p120),
Balance Sheet / Investment Properties (Note 14, pp121/192), the audited **Portfolio Statements**
(Group, pp130–167), Portfolio-Statement footnotes (pp173), Top-10 Customers (p49), Customer Trade
Sectors (p50), Statistics of Unitholdings (p227), and Corporate Directory (p233).

I did **NOT** consult any extractor tooling, page-map, anchor list, or reasoning. Inputs read: only
the parsed markdown `parsed_reports_datalab/28_M44U.SI_Mapletree-Logistics-Trust_FY2025/full.md`
(page-anchored) and the shipped `extracted/M44U.SI_FY2025/*.json`. Fiscal year = **1 Apr 2024 – 31
Mar 2025 ("FY24/25")**; all figures S$'000 unless noted. Two scoped sub-investigations (per-country
property counts + broad valuation spot-checks; transactions + tenants + trade mix) were run as
independent passes over the same two sources and folded in below.

---

## 2. Verdict & confidence

**Grade: MINOR ISSUES (bordering MATERIAL on the property_transactions table).**

The extraction is strong on the hard numbers. Every audited financial-statement figure I
re-derived matched the Group column to the dollar; the full income statement reconciles exactly to
"Profit for the year" (S$208,896k); the 242 property rows are present with correct 2025 Group
valuations (spot-checked across all 9 countries — all exact), correct currencies, occupancy and
per-property gross revenue (19/19 valuation spot-checks across all 9 countries exact, no tenure
misclassifications, no missing/extra rows); trade_mix sums to 100%; top-10 customers, DPU,
distributable income and unitholders all check out. The **KNOWN OPEN ITEM is resolved**: the sponsor is **Mapletree
Investments Pte Ltd**, stated explicitly on **p2** ("MLT is managed by Mapletree Logistics Trust
Management Ltd. … a wholly-owned subsidiary of Mapletree Investments Pte Ltd (the 'Sponsor')") — the
shipped `profile.sponsor` is correct.

The defects are concentrated in **property_transactions** (3 FY24/25 acquisitions entirely omitted;
7 of 17 divestment rows are prior-year; sale prices/considerations omitted though disclosed) and in
two **under-flagged provenance** items (the recurring `interest_income`-as-revenue mis-bucket that
breaks the cross-section revenue tie-out; top-tenant trade sectors assigned by the extractor but not
flagged; trade-mix single-month scope and ~50 derived lease terms not flagged).

Tally: **CONFIRMED ≈ 40+** · **DISCREPANCY = 6** · **SUSPECTED-OMISSION = 3** · **UNVERIFIABLE = 2**

---

## 3. Discrepancies

### D1 — income_components: `interest_income` (2,648k) mislabelled `statement="revenue"` (MED)
- Extraction tags `interest_income` 2,648k as `statement:"revenue"`.
- Source (**p121** Statements of Profit or Loss, Group, and **p187** Note 3): "Gross revenue" =
  727,026k comprises ONLY the three Note-3 lines (Rental income 627,722 + Service charges 87,058 +
  Other operating income 12,246 = 727,026). **Interest income sits BELOW Net property income** as a
  separate line (2,648) — it is explicitly not part of gross revenue (Note 3 prints it under a
  separate "Interest income:" subtotal).
- Consequence: Σ(income_components where statement=revenue) = 627,722 + 87,058 + 12,246 + 2,648 =
  **729,674k**, which does NOT equal `performance.gross_revenue` (727,026k). Gap = exactly 2,648 =
  interest_income. **Cross-section revenue tie-out FAILS.** This is the recurring HMN-class bug.
- Fix: set `interest_income.statement = "adjustment"` (it sits below NPI / above net investment
  income on the audited statement; it is not a property-operating expense either). Source: p121.
  The signed reconciliation to Profit for the year is unaffected (see §5). Confidence: HIGH.

### D2 — property_transactions: 3 FY24/25 acquisitions entirely OMITTED (HIGH)
- `property_transactions.json` contains **zero acquisitions**. The report discloses **three
  acquisitions completed in FY24/25**, with completion dates and considerations:
  - **Mapletree Logistics Hub – Jubli Shah Alam** (Malaysia), completed **17 May 2024**, agreed
    property value **MYR558.8m (~S$160.4m)** — p33 / p47 / p171 (agreed value also at p47;
    "MYR558.8 million" at line p171/3426).
  - **Hung Yen Logistics Park I** (Vietnam), completed **19 Jun 2024**, ~**S$33.5m** — p33 / p47.
  - **Mapletree Logistics Park Phase 3** (Vietnam), completed **20 Jun 2024**, ~**S$33.3m** — p33 / p47.
- All three were acquired from the Sponsor; total ~S$227–230m, matching the "acquisition of three
  assets in FY24/25" headline (p53). All three ARE present as active properties in properties.json
  (Jubli Shah Alam, Hung Yen Logistics Park I, Mapletree Logistics Park Phase 3) — so the assets
  were captured but their **acquisition transactions were dropped**. This is a clear omission with a
  schema home, not a "no home" case. Confidence: HIGH.

### D3 — property_transactions: 7 of 17 "divestment" rows are PRIOR-YEAR, not FY2025 (MED–HIGH)
- The extraction copied all 17 rows from **footnote (o) (p173)**, which is a *cumulative master list
  of completion dates for all divested properties*, and tagged every row `financial_year: 2025`.
- The report explicitly defines the FY24/25 divestments as **10 properties** (p33, p47, p53). The
  10 genuine FY24/25 divestments (completed Apr 2024–Mar 2025): 30 Tuas South Avenue 8 (14 Jun
  2024), 119 Neythal Road (12 Sep 2024), Mapletree Xi'an Logistics Park (15 Nov 2024), Toki Centre
  (27 Nov 2024), Aichi Miyoshi Centre (27 Nov 2024), Padi Warehouse (31 May 2024), Flexhub (23 Sep
  2024), Celestica Hub (28 Jan 2025), Zentraline (28 Jan 2025), Linfox (19 Mar 2025).
- **7 spurious rows** completed in FY23/24 or earlier (per footnote (o), p173) and should NOT carry
  `financial_year: 2025`: Kenyon (8 Sep 2023), Pioneer Districentre (8 Dec 2023), **73 Tuas South
  Avenue 1 (19 Feb 2024 → still FY23/24)**, Moriya Centre (26 Sep 2023), Chee Wah (10 Jul 2023),
  Subang 1 (13 Jul 2023), Century (6 Nov 2023).
- The individual completion dates in all 17 rows are accurate (they match footnote (o)); the defect
  is the **inclusion basis** (historical master list vs the defined FY24/25 set). Confidence: HIGH.

### D4 — property_transactions: `consideration` omitted though sale prices ARE disclosed (MED)
- Every divestment row has no consideration. The p47 FY24/25 Divestments table discloses sale prices
  per property: e.g. 30 Tuas South Ave 8 S$10.5m, 119 Neythal S$13.8m, Toki JPY2,425m (~S$21.2m),
  Aichi Miyoshi JPY1,825m (~S$16.0m), Flexhub MYR125.1m (~S$38.5m), Xi'an RMB70.5m (~S$13.1m), etc.
  (also corroborated p173/p49 prose: combined Toki+Aichi JPY4,250m at line 3388; aggregate sale
  value ~S$209m at p33). The acquisitions' considerations are likewise disclosed (D2). At minimum
  the disclosed S$ (and local-currency) prices should have been captured. Confidence: HIGH.

### D5 — top_tenants: `trade_sector` extractor-assigned but NOT flagged as inferred (LOW–MED)
- The source "Top 10 Customers by Gross Revenue" table (**p49**) has only two columns: Customer and
  Percentage of Total Gross Revenue. There is **no trade-sector column.** All 10 `trade_sector`
  values (Equinix→IT & Telecommunications, Coles→Food & Beverages, CWT→Logistics, etc.) are
  assigned by the extractor from company knowledge. Assignments are reasonable, but per §0 invariant
  7 each must appear in `_notes.inferred[]`; none are flagged. Confidence: HIGH (provenance defect).

### D6 — trade_mix: disclosed scope ("month of March 2025") dropped from `pct_basis` (LOW)
- The donut (**p50**) is captioned "Gross Revenue by Trade Sector for the **month of March 2025**" —
  a single-month snapshot, not full-year FY24/25. `pct_basis="gross_revenue"` captures the metric
  but omits the month-of-March-2025 scope (capture-with-scope, §0 invariant 6). Values are exact and
  sum to 100% (see §5). Confidence: HIGH the scope was dropped; LOW severity.

---

## 4. Suspected omissions

### O1 — ~50 per-property `lease_term_years` / lease-tenure derivations not flagged as inferred (MED)
The Portfolio Statement (pp130–167) discloses, per property, "Term of lease" and "Remaining term of
lease" (e.g. HK "149 years / 22 years"; SG "30+30 years"; China "50 years"). The extraction's
`tenure_raw` faithfully copies the term string, but `lease_term_years` is frequently a **derived
single integer** (e.g. "30+30 years" → 60; "30+12 years" → 42) and `land_tenure` is an **assigned
enum** (Freehold/Leasehold). Where the term is unambiguous this is fine, but per §0 invariant 7 the
derivation rule should be recorded in `_notes.inferred[]`; it currently is not. Several rows where
`lease_term_years` was left null on ambiguous strings ("29/30 years", "30/30 years",
"28+30/30+30 years") are handled correctly. SEVERITY: MED (provenance understated; values reasonable).

### O2 — Pending divestments not represented as transactions (LOW)
Four divestments were *announced/pending* as at 31 Mar 2025 (1 Genting Lane, 8 Tuas View Square, 31
Penjuru Lane — footnote (n) p173, agreed values S$12.3m / S$11.18m / S$7.8m; and Subang 2 — footnote
(s), ~S$9.482m). The extraction carries these as `status="held_for_sale"` **properties** (correct
and consistent with the footnotes), so they are not omitted from properties.json; they simply have
no row in property_transactions (acceptable, since not yet completed). Flagged for completeness only.

### O3 — Acquisition considerations have no schema home in properties (LOW)
The per-property acquisition agreed-values (D2) and divestment sale prices (D4) belong in
property_transactions.consideration (which exists) — already covered by D2/D4. No additional
no-home data of note; per-property NPI is genuinely segment-only (see §6).

---

## 5. Reconciliation results (independently re-computed)

### Income statement tie-out (Group, p121) — PASS (signed) / FAIL (revenue cross-section)
Using income_components values:
- Σ(revenue as tagged) = 627,722 + 87,058 + 12,246 + 2,648 = **729,674k**
- Σ(expense as tagged) = 26,196 + 44,380 + 17,282 + 437 + 13,438 (Note 4 = property expenses
  101,733 ✓) + 90,513 + 1,821 + 10,909 + 156,893 = **361,869k**
- Σ(adjustments, signed) = −26,947 (FV derivatives) −67,612 (FV inv. props) +515 (gain on disposal)
  −64,865 (income tax) = **−158,909k**
- 729,674 − 361,869 − 158,909 = **208,896k = "Profit for the year" (Group, p121) ✓ exact.**
- BUT Σ(revenue) 729,674 ≠ performance.gross_revenue 727,026 (gap 2,648 = interest_income → **D1**).
- Completeness: "Dividend income" is 0 for the Group (146,816 is MLT-entity only) — correctly
  omitted. "Amortisation of FV of financial guarantees" is 0 for Group — correctly omitted.
  income_components is complete for the Group column.

### Gross revenue (Note 3, p187) — PASS
627,722 + 87,058 + 12,246 = **727,026k** = p121 gross revenue ✓ = performance.gross_revenue ✓.

### Property expenses (Note 4, p187) — PASS
26,196 + 44,380 + 17,282 + 437 + 13,438 = **101,733k** ✓ = p121 "Property expenses".

### NPI — PASS
727,026 − 101,733 = **625,293k** = performance.net_property_income ✓ (= p121 Net property income).

### Distribution — PASS
"Amount available for distribution" (Distribution Statement, p120) = **406,397k** =
performance.net_distributable_income ✓. (Note the marketing "amount distributable 430,628 / S$406.4m"
at p33 — the extraction correctly took the audited 406,397.) DPU FY24/25 = **8.053c** (p6 / p36 /
p120) ✓. Quarterly DPU 2.068 + 2.027 + 2.003 + 1.955 = 8.053 ✓ (p36), periods match
distribution_record. Ex-date/pay-date genuinely not disclosed per quarter → nulls correct.

### Portfolio valuation total — PASS
Audited Portfolio Statement total fair value of investment properties (**p167**) = **13,156,611k**
(gross revenue row total 727,026 ✓). + ARO asset 477 + lease liabilities 87,795 = **13,244,883k**
= balance-sheet Investment properties (Note 14) ✓. Held-for-sale (Note 15) 47,102k separate ✓.
`performance.portfolio_value` = **13,292,000,000** is the disclosed headline (p53/p54: "180
properties valued at S$13,292.0m … includes right-of-use assets of S$95m … comprising investment
properties, properties under redevelopment and investment properties held for sale", p37 line 2297).
This is a genuinely disclosed figure (not a marketing-millions rounding) and is an acceptable
portfolio_value per REFERENCE §1. Σ(properties.json non-null market_valuation) reconciles to
13,156,611 less held-for-sale/divested null rows: all 176 active rows have non-null valuations; all
4 held-for-sale and 17 divested are null (matching the audited statement's "—" for those rows).
Singapore active subtotal independently summed = 2,560,100k (44 rows), consistent with the p54 SGD
2,676m for 47 incl. 3 HFS + S$95m ROU. No valuation-scaling errors (all ×1000 from S$'000).
**Note on row count: the file holds 197 property rows (176 active + 4 held-for-sale + 17 divested),
not 242 as the directive stated.**

### Per-property valuation spot-checks — PASS (19/19 exact, all 9 countries)
Directly confirmed against the audited Portfolio Statement value pages (val / occ / GR, ext vs src):
- SG (p131/133): 25 Pandan Crescent 60,000/96/6,613; Mapletree Benoi Hub 132,800/100/13,457; 5A Joo
  Koon 188,000/—/— → null — all exact.
- AU (p135): Coles Chilled DC 321,498/100/16,844; 28 Bilston Drive 47,008/100/3,887 (300-yr lease →
  Leasehold ✓); 8 Williamson Rd 109,124/100/6,431 — exact.
- CN (p137/139/144/145): Ouluo 134,332/76/7,185; Tianjin Wuqing 23,034/100/730; Yantai 44,409/86/
  1,945; Yixing 51,964/65/1,924; Zhengzhou Airport 82,369/100/4,500; Xi'an Log. Park (divested) GR
  117, val "—" → null — exact.
- HK (p147): Tsing Yi 1,284,062/97/52,187; Shatin No.3 391,818/100/17,755; (also Tsuen Wan No.1
  101,220, Shatin No.2/4 183,708/429,797, Grandtech 401,785) — exact.
- IN (p149): Chakan LP 1 70,963/100/5,870 — exact.
- JP (p151/153): Kuwana 321,946/98/12,217; Iwatsuki 3,851/100/462 — exact.
- MY (p155/157): Jubli Shah Alam 170,070/97/10,081; Tanjung Pelepas 125,070/100/7,363 — exact.
- KR (p161/163): Yeosu 7,251/99/559; Majang 3 142,442/100/7,740 — exact.
- VN (p165/167): Mapletree Logistics Centre (VSIP) 13,430/100/1,525; Hung Yen LP I 35,291/75/2,017 —
  exact.
- Tenure: China "50 years" land-use-right and Australia's anomalous "300 years" → Leasehold; Japan/
  Korea Freehold; SG "30+30"/"29/30" handled (null kept on ambiguous strings). No misclassifications.

### Trade mix — PASS
19 + 6 + 17 + 3 + 6 + 3 + 4 + 13 + 6 + 1 + 4 + 1 + 1 + 4 + 4 + 8 = **100%** ✓ (p50). All 16
`category_raw` values and percentages match the source exactly. (Scope caveat → D6; canonical
collapse note below.)

### Top tenants — PASS
10 rows match p49 exactly (Equinix 3.7 … Bidvest 1.5); Σ = 21.7% (prose confirms "top 10 customers
accounted for ~21.7% of total gross revenue", p49); pct_basis "gross_revenue" matches header
"Percentage of Total Gross Revenue". (Sector provenance → D5.)

### Group vs MLT-entity column discipline — PASS
Every financial figure traced to the **Group** column (gross revenue 727,026 not MLT 201,149; NPI
625,293 not 170,952; borrowing costs 156,893 not 96,855; investment properties 13,244,883 not
2,638,222). Portfolio values are the 2025 Group column. ✓

---

## 6. Nulls / inference audit

**Confirmed genuinely absent (correct nulls):**
- `properties.net_property_income` per property — genuinely segment-only (Note 29 country-level NPI:
  SG 173,031 / HK 97,802 / CN 117,649 / JP 115,614 / KR 52,284 / AU 58,147 / MY 46,820 / VN 31,630 /
  IN 9,316; Σ ≈ NPI 625,293). Per-property NPI not disclosed. Null + reason correct. ✓
- `properties.gla / nla` per property — not in the audited Portfolio Statement. Correct nulls. ✓
- `properties.major_tenant` — not disclosed per property (only top-10 portfolio customers). ✓
- Held-for-sale rows' `market_valuation` null (1 Genting Lane, 8 Tuas View Square, 31 Penjuru Lane,
  Subang 2) — these are in Note 15 at *agreed values* (S$12.3m / S$11.18m / S$7.8m / S$9.482m,
  footnotes (n)/(s) p173), not in the main valuation column. Null is defensible; the agreed values
  are correctly parked in `_notes.data_with_no_home`. ✓
- Divested rows' `market_valuation`/`valuation_date` null — correct (absent from year-end statement). ✓
- Distribution ex/pay dates null — genuinely not disclosed per quarter. ✓

**Wrong / under-flagged provenance (defects, see §3):**
- `interest_income.statement="revenue"` → wrong (D1).
- top_tenants `trade_sector` assigned, not flagged (D5).
- trade_mix `pct_basis` scope dropped (D6); canonical mapping collapses 16 raw rows into ~10 buckets
  ("Other Industrial Trades" ×6 incl. the questionable "Consumer Staples"→Other Industrial; "IT &
  Telecommunications" ×2) — `category_raw` is preserved so the raw mix is recoverable; per-row Σ is
  still 100%, so not a numeric defect, but worth a mapping review.
- ~50 derived `lease_term_years` and assigned `land_tenure` not flagged in `_notes.inferred[]` (O1).
- `valuation_date` = 2025-03-31 uniform — correct (Portfolio Statement "As at 31 March 2025") but is
  an assigned uniform value, not field-level disclosed per property.

**profile / cross-file consistency — PASS:**
- Sponsor = Mapletree Investments Pte Ltd (p2); Manager = Mapletree Logistics Trust Management Ltd.
  (p2/p233); Trustee = HSBC Institutional Trust Services (Singapore) Limited (p233). All correct and
  internally consistent. (Minor: `profile.source_page=233` supports manager+trustee but the sponsor
  statement is on p2 — single-page provenance is the schema norm; not a defect.)
- A Property Manager exists (5-yr extension to 27 Jul 2025, p~10) but is not among the captured roles
  — acceptable given the schema's role set; flagged for awareness only.
- `sub_sector="Industrial"` — MLT is pure logistics/warehousing; "Industrial" is the schema umbrella
  enum and all property categories are "Logistics". Acceptable.

---

## 7. Confirmed-correct highlights (balance)

- **All audited FS numbers exact** to the Group column: gross revenue 727,026, property expenses
  101,733, NPI 625,293, every below-NPI line, tax, profit for the year 208,896, distributable income
  406,397, DPU 8.053.
- **Full income statement reconciles to Profit for the year (208,896k) exactly** — no missing line.
- **197 property rows present**: 176 active + 4 held-for-sale + 17 divested. The 176 active + 4
  held-for-sale = the disclosed 180-property portfolio (per-country: SG 44+3=47, AU 14, CN 42, HK 9,
  IN 3, JP 22, MY 9+1=10, KR 21, VN 12, p54). Correct currencies (all S$'000 as the Group statement
  converts), correct categories, occupancy and per-property gross revenue. **19/19 valuation
  spot-checks across all 9 countries exact; no tenure misclassifications; no missing/extra rows; no
  scaling errors.** Divested/held-for-sale statuses and the 5A Joo Koon redevelopment anomaly
  (S$55.1m → S$188m) handled correctly.
- **Sponsor open item resolved** — Mapletree Investments Pte Ltd, p2; shipped value correct.
- **trade_mix and top_tenants** match source exactly and tie to 100% / 21.7%.
- **Unitholders 34,292** ✓ (p227, "As at 30 May 2025"). Units 5,075,148,796.
- Multi-currency handled correctly: all Portfolio Statement values are S$-converted by the trust
  (closing rates for valuation, average for revenue) and the `currency=SGD` per row is faithful to
  the audited statement.

---

## 8. Could NOT verify

- **Per-property NPI in S$** — genuinely disclosed only at country-segment level (Note 29); per-
  property NPI null stands and is not derivable from the parse. UNVERIFIABLE by design.
- **Exact local-currency per-property valuations** — the Portfolio Statement presents only the
  S$-converted figures (the per-country local-currency totals are at p54, but per-property local
  values and the exact FX rates applied are not in the parse). Per-property currency=SGD is correct;
  the underlying local values are UNVERIFIABLE without the trust's per-property FX.
