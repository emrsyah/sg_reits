# ME8U — Mapletree Industrial Trust (ME8U.SI) FY2024 (FY23/24) — Forensic Extraction Audit

Auditor: independent verification against source. Navigated the report myself from the TOC — Statements of Profit or Loss / Comprehensive Income / Financial Position / Distribution (pp118–122), Consolidated Cash Flow (pp123–124), EPU Note 11 (p133-area), Investment Properties Note 15 (pp137–138), JV Note 21, Segment Note 32 (pp197–198), Portfolio Statement (pp126–139), Operations Review (pp32–59), Financial Highlights & Key Ratios (pp10–11, "AUM" p10), Capital Management (pp79–80), Statistics of Unitholdings (p200-area), Report of the Trustee (p110) and Corporate Directory (IBC). I did **NOT** consult any extractor tooling — no page-map, no `local://fy2024-gather/*`, no `extracted_adapter/*`, no FY2025 extraction, no extraction skill.

Sources: `parsed_reports_datalab/27_ME8U.SI_Mapletree-Industrial-Trust_FY2024/full.md` (page-anchored). Markdown tables parsed cleanly; PDF spot-checks not required.

**Confirmed FYE: financial year ended 31 March 2024 (FY23/24).** Every financial figure was verified against the **Group** column (FY23/24), never MIT-only and never the FY22/23 comparative.

---

## 1. Verdict & confidence

**Grade: MINOR ISSUES.**

The extraction is exact on every hard number. Every audited financial-statement figure I re-derived matched the **Group / FY23/24** column to the dollar; the full Statement of Profit or Loss reconciles exactly to "Profit for the financial year" S$120,628k; all three derived-metric identities (I1/I2/I3) hold to the dollar; the attribution split (unitholders 111,036 + perpetual 9,476 + NCI 116 = 120,628) is exact; EPU 3.94c ties to the Note 11 weighted-average units (2,816,874k); balance sheet, cash flow, distribution, DPU 13.43c, NAV 1.76, leverage 38.7%, cost of debt 3.2%, WADM 3.8y, WALE 4.4y, occupancy 92.6%, unitholders 42,552 all confirmed; trade_mix sums to 100% and top_tenants Σ = 29.1% both verbatim; and Σ(properties.market_valuation) = 7,743,797,000 reconciles to Note 15 fair value (net of future lease payments) to **zero difference**.

The residual issues are all basis/labelling judgments plus one concrete geography omission: (a) `performance.properties_location` omits **Canada**, though `properties.json` itself carries a Canadian property (6800 Millcreek Drive, Mississauga, Ontario); (b) `interest_coverage_ratio` ships the *adjusted* ICR (4.3) rather than the "interest coverage ratio for the financial year" (4.6) — both disclosed, choice documented; (c) `portfolio_value` ships the AUM figure (8,906.3m incl. JV interests) rather than the disclosed total portfolio valuation of the 140 properties (8,802.2m) — both disclosed, choice documented but internally inconsistent with `_notes` which calls 8,802.2m the portfolio valuation; (d) `top_tenants.industry` is an **unflagged inference** (report discloses an asset Category, not a tenant business sector).

Tally: **CONFIRMED ≈ 45** · **DISCREPANCY = 3** (D1 MED, D2 LOW, D3 LOW–MED) · **SUSPECTED-OMISSION = 1** (O1 LOW) · **UNVERIFIABLE = 1**

---

## 2. Discrepancies

### D1 — `performance.properties_location` omits Canada (MED)
- Extraction: `properties_location = "Singapore; United States; Japan"` (3 countries).
- Source: the North American portfolio (56 data centres) includes one in **Canada** — property #35 "6800 Millcreek Drive, Mississauga", listed under **Ontario** (p32 line 1510-1512; audited Portfolio Statement p46 line 2822-2823). The report's own North-America map (p32) states "United States **and Canada**".
- Cross-artifact: `properties.json` correctly carries `country: "Canada"` for that row (55 US + 1 Canada + 42 SG-clusters + 1 Japan). So `performance` (3 countries) contradicts `properties` (4 countries).
- Consequence: once the extractor chose to split "North America" into "United States", it should have named Canada too. Downstream geography counts will be wrong by one country.
- Fix: `properties_location = "Singapore; United States; Canada; Japan"`. Severity MED, confidence HIGH.

### D2 — `interest_coverage_ratio = 4.3` is the *adjusted* ICR, not the FY ICR (LOW)
- Extraction: `interest_coverage_ratio = 4.3`; the `flags` correctly note this is the "adjusted-ICR basis (FY-ICR headline 4.6x); mirrors FY2025 adjusted basis."
- Source discloses BOTH (Key Financial Ratios p11, lines 406-407; Capital Management p79-80, lines 4970-4971): "Interest coverage ratio for the financial year = **4.6 times**" and "Adjusted interest coverage ratio (trailing 12 months) = **4.3 times**" (also Note, p ~183 line 9687: "adjusted interest coverage ratio of 4.3 times").
- Consequence: an unqualified `interest_coverage_ratio` field most literally maps to the "interest coverage ratio for the financial year" = 4.6. The 4.3 is the MAS-regulatory adjusted measure (includes proportionate JV borrowings, governs the >45% leverage allowance). The choice is defensible and documented, but the field value differs from the plain headline. Severity LOW (judgment; confirm intended basis), confidence HIGH the two figures exist.

### D3 — `performance.portfolio_value = 8,906,300,000` (AUM) vs disclosed portfolio valuation 8,802.2m (LOW–MED)
- Extraction: `portfolio_value = 8,906,300,000`; flag: "AUM incl JV interests (audited Group IP=7,847,851,000)". This is the disclosed "Assets under management (including interests in joint ventures)" S$8,906.3m (p10 line 339/397).
- Source also discloses the **total portfolio valuation**: "The total valuation of **140 properties** in MIT's portfolio was **S$8,802.2 million**" (Operations Review p32 line 736; Portfolio Review "Total Portfolio 8,802.2" p79 line 4934). The ~104m gap is largely the Osaka Data Centre basis (Tier-C S$377.7m vs full-fit-out JPY52.3b ≈ S$471.5m, p138 note line 7425).
- Cross-artifact: `_notes.parsing_traps` itself describes 8,802.2m as "the S$8.8022b marketing portfolio valuation including JV/right-of-use assets", i.e. the notes treat 8,802.2m as the portfolio valuation, while `performance` ships the AUM 8,906.3m. Internal inconsistency of concept.
- Consequence: the more common "portfolio_value" convention (a revalued property-portfolio total, as used for peers) points to **8,802,200,000**; the AUM is a broader concept. Severity LOW–MED (both disclosed, documented), confidence HIGH.

---

## 3. Suspected omissions

### O1 — `distribution_record` ex_date / pay_date all null (LOW)
All four quarterly rows have `ex_date: null, pay_date: null`. The AR is light on per-quarter ex/pay dates (it tabulates the distribution *periods* and cents only, p121). One dated data point exists — the advance distribution "declared … on 6 June 2023 and paid on 6 July 2023" for 1 Apr–5 Jun 2023 (cash-flow footnote, p123 line 6996) — but a full per-quarter ex/pay-date table is not disclosed in this AR. Null is acceptable; flagged for completeness. Schema home exists (fields present); data largely absent. Severity LOW.

---

## 4. Reconciliation results (independently re-computed)

### R1 — Statement of Total Return tie-out (Group FY23/24, p118) — **PASS (exact)**
Using `financial.line_items` (tax carried as a signed adjustment):
- Σ revenue = 697,332 (gross revenue only).
- Σ expense = 176,289 + 106,609 + 41,849 + 18,838 + 1,054 + 4,655 = **349,294**.
- Σ adjustments (signed) = +4,751 (interest income) +1,778 (FX) +3,492 (divestment gain) −1,879 (FV derivatives) −210,826 (FV loss IP) −8,713 (share of JV) −16,013 (tax) = **−227,410**.
- 697,332 − 349,294 − 227,410 = **120,628** = "Profit for the financial year" (p118) = `net_income` ✓. No line missing or extra (investment income and impairment-loss lines are MIT-only, correctly excluded from Group).

### R2 — total_revenue == gross_revenue == Σ(revenue line_items) — **PASS**
697,332,000 (financial.total_revenue) = 697,332,000 (performance.gross_revenue) = 697,332 (single revenue line, p118) ✓. No finance/other income mis-bucketed into revenue (interest income correctly tagged `adjustment`, not `revenue`).

### R3 — gross_income == NPI; cost_of_revenue == property opex — **PASS**
gross_income 521,043,000 = Net property income 521,043 (p118) ✓; cost_of_revenue 176,289,000 = Property operating expenses 176,289 (p118) ✓. Also cross-checked to Segment Note 32 (p197): Σ segment NPI 32,244+184,769+105,145+29,612+127,307+40,049+1,917 = **521,043** ✓.

### R4 — Derived-metric identities (I1/I2/I3) — **PASS (all exact)**
- operating_expense 66,396 = base 41,849 + perf 18,838 + trustee 1,054 + other-trust 4,655 ✓.
- I1: operating_income 454,647 = gross_income 521,043 − operating_expense 66,396 ✓.
- interest_expense_non_operating 101,858 = borrowing costs 106,609 − interest income 4,751 ✓ (investment income = 0 for Group).
- I2: ebit 238,499 = pretax 136,641 + interest_expense_non_operating 101,858 ✓.
- non_operating_income_or_loss −318,006 = operating_income 454,647 → pretax 136,641 bridge (4,751 −106,609 +1,778 +3,492 −1,879 −210,826 −8,713) = −318,006 ✓.
- I3: net_income 120,628 = pretax 136,641 − income_taxes 16,013 ✓.
- Attribution (d): 111,036 + 9,476 + 116 = 120,628 ✓ (p118).

### R5 — Balance sheet (Group as at 31 Mar 2024, p120) — **PASS**
total_asset 8,664,366 ✓; current 163,737 ✓; non-current 8,500,629 ✓; total_liabilities 3,375,634 ✓; current-liab 224,933 ✓; non-current-liab 3,150,701 ✓; total_equity 5,288,732 = Net assets ✓. working_capital −61,196 = 163,737 − 224,933 ✓. (Equity split cross-checks: unitholders' funds 4,984,582 + perpetual 301,828 + NCI 2,322 = 5,288,732 ✓.)

### R6 — Cash flow (Group FY23/24, p123) — **PASS**
operating 432,784 ✓; investing −353,125 ✓; financing −106,337 ✓; net_cash_flow −26,678 ✓ and = 432,784 − 353,125 − 106,337 ✓. capital_expenditure −432,611 = "Additions to investment properties and IPUD" ✓.

### R7 — Distribution / DPU — **PASS**
NDI 375,069 = "Amount available for distribution" (p121) = FY-generated (111,036 + Note-A 232,190 + JV cash distribution 31,843), correctly **excluding** the opening carried-forward 95,141 ✓ (closing 101,328 = 95,141 + 375,069 + 5,391 divestment-gain distribution − 374,273 ✓). distribution_paid 374,273 = "Total Unitholders' distribution (incl. capital)" Note B (p121/p123) ✓. DPU 13.43c ✓ (p10 line 314; p78 line 4815; MD&A line 732). Quarterly record 3.39 + 3.32 + 3.36 + 3.36 = **13.43** ✓ (1Q = advance 2.48 + 0.91; 4Q 3.36 declared post-FYE per p12 line 872). dpu_period_months 12 ✓.

### R8 — Σ properties.market_valuation → Note 15 — **PASS (exact)**
Σ(85 valued rows) = **7,743,797,000** = Note 15 "Fair value of investment properties (net of future lease payments)" Group 7,743,797 (p138 line 8313) ✓, diff 0. Carrying amount 7,847,851 (p120/Note 15) = fair value + lease liabilities 102,691 + ARO 1,363 ✓. 14 null-valuation rows = 13 MRODCT JV data centres (equity-accounted, individual Tier-C values genuinely absent) + divested Tanglin Halt — correct, source-driven.

### R9 — trade_mix (p34) — **PASS**
32.90 + 27.09 + 15.01 + 14.87 + 10.13 = **100.0** ✓, all `pct_basis: "gri"`, matches the "Tenant Diversification across Trade Sectors (By GRI)" donut verbatim (p34 line 1814-1818). category_raw preserved verbatim.

### R10 — top_tenants (p33) — **PASS**
10 rows, ranks 1–10 contiguous, %s descending (6.0 → 1.7). Names and %s match "Top 10 Tenants (By GRI)" (p33 line 1779-1788) exactly. Σ = **29.1%** = disclosed "top 10 tenants accounted for 29.1%" (p33 line 1765) ✓. `industry_raw` preserves the report's asset Category ("Hi-Tech Buildings" / "Data Centres") verbatim.

---

## 5. Nulls / inference audit

**Correct nulls (confirmed genuinely absent):**
- `properties.net_property_income` / `npi_pct` — NPI disclosed only at 7-segment level (Note 32 p197) and segment charts; no per-property/cluster NPI column, and not computable (Note 4 property opex is Group/MIT totals). `_notes` reason is **correct**.
- 13 MRODCT JV rows `market_valuation` null — equity-accounted; individual audited Tier-C values genuinely not disclosed (only combined Note 21 entity figures). Correct.
- Divested Tanglin Halt nla/gfa/market_valuation null — Portfolio Statement shows "–" for FY2024. Correct.
- `adjusted_distributable_income` null — no separate "adjusted" DI disclosed; the single "Amount available for distribution" is NDI. Correct.

**Inferences / basis notes:**
- `top_tenants[].industry` (e.g. AT&T/Lumen → "IT & Telecommunications", Bank of America → "Financial & Professional Services") is **DERIVED** — the report discloses only an *asset* Category ("Data Centres" / "Hi-Tech Buildings"), not a tenant business sector. The inference is well-reasoned (mapped from tenant identity, internally consistent) and `industry_raw` preserves the disclosed Category, but it is **not flagged** as an inference. Recommend flagging. Severity LOW.
- `trade_mix` normalization: "Wholesale and Retail Trade" → `Other Retail Trades`, "Other Trade Sectors" → `Other Industrial Trades`. The catch-all "Other Trade Sectors" (Education/Health, Construction/Utilities, Transport/Storage, Accommodation/F&B per p34) is not truly "industrial", so `Other Industrial Trades` is a slightly awkward label, but `category_raw` is preserved verbatim. Severity LOW.
- `financial._derived[]` correctly declares the 5 computed fields (operating_income, ebit, ebitda, non_operating_income_or_loss, interest_expense_non_operating) — verified above, no re-flag needed.
- `number_of_shareholder_units` 2,834,670,000 = balance-sheet "Units in issue" 2,834,670k at FYE (Note 27a) — a point-in-time issued figure (the Statistics of Unitholdings total 2,835,380,283 differs slightly, being a later record date). Defensible choice, not flagged; consistent.

---

## 6. Confirmed-correct highlights (balance)

- **All audited FS numbers exact** to the Group / FY23/24 column: gross revenue, property opex, NPI, interest income, borrowing costs, each management/trustee fee, FX, divestment gain, FV derivatives, FV loss on IP (−210,826), share of JV, PBT, tax, profit for the year, and the full attribution split.
- **Full Statement of Total Return reconciles to 120,628 exactly**; segment Note 32 independently corroborates every below-NPI line and the NPI-by-segment total 521,043.
- **Perpetual + NCI handled correctly**: perpetual securities holders 9,476 and non-controlling interests 116 captured as positive attribution components; perpetual 301,828 / NCI 2,322 in equity.
- **EPU 3.94c** ties to Note 11 (profit to unitholders 111,036 ÷ weighted-avg 2,816,874k) ✓.
- **Balance sheet, cash flow, distribution, DPU 13.43c, NAV 1.76, leverage 38.7%, cost of debt 3.2%, WADM 3.8y, WALE 4.4y (by GRI), occupancy 92.6% (overall FY23/24), unitholders 42,552** all independently confirmed.
- **Portfolio valuation** sums to the audited Note 15 fair value (7,743,797k) to the dollar; JV/divested nulls correct.
- **trade_mix & top_tenants** captured verbatim incl. the correct source pages (p34 / p33) and the 29.1% top-10 tie-out.
- **profile**: manager Mapletree Industrial Trust Management Ltd. ✓, trustee **DBS Trustee Limited** ✓, sponsor Mapletree Investments Pte Ltd ✓ — all match the Trust Structure (p16), Report of the Trustee (p110) and Corporate Directory (IBC). sub_sector "Industrial" ✓.
- **property_transactions**: Osaka Data Centre acquisition JPY52.0b, 28 Sep 2023, Suma Tokutei Mokuteki Kaisha, 98.47% effective interest ✓ (p32); Tanglin Halt divestment 27 Mar 2024, sale S$50.6m / net proceeds S$50.192m / gain S$3.492m ✓ (p35/cash-flow).

---

## 7. Could NOT verify

- **Per-quarter ex/pay dates** for the distribution_record — not tabulated in this AR (only the advance-distribution declared/paid dates for the 1 Apr–5 Jun 2023 tranche are given). Left UNVERIFIABLE; null retained (O1).
- **Individual valuations of the 13 MRODCT JV data centres** — only combined Note 21 entity-level figures disclosed; per-property Tier-C values genuinely absent by design. Null correct.

---

## Fix list (concrete, page-cited)

| File | Field | Current | Correct / recommended | Source |
|---|---|---|---|---|
| performance.json | properties_location | "Singapore; United States; Japan" | "Singapore; United States; Canada; Japan" (add Canada) | p32 line 1510-1512 (6800 Millcreek Drive, Mississauga, **Ontario**); Portfolio Statement p46 line 2822-2823; confirmed by properties.json country="Canada" |
| performance.json | interest_coverage_ratio | 4.3 (adjusted, trailing-12m) | Confirm intended basis; the plain "interest coverage ratio for the financial year" = **4.6** | p11 lines 406-407; p79-80 lines 4970-4971 |
| performance.json | portfolio_value | 8,906,300,000 (AUM incl JV) | Consider 8,802,200,000 (disclosed total portfolio valuation of 140 properties); reconcile with `_notes` which labels 8,802.2m the portfolio valuation | p32 line 736; p79 line 4934; `_notes.parsing_traps` |
| top_tenants.json | industry | derived, unflagged | Keep values but flag as inferred (report discloses asset Category only, not tenant business sector) | p33 line 1777-1788 ("Category" column) |

No edits made — fixes gated to the user.
