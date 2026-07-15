# A17U — CapitaLand Ascendas REIT (A17U.SI) FY2024 — Forensic Extraction Audit

Auditor: independent verification against source. Navigated the report myself from the TOC — Overview/Highlights (pp.4-11), The Manager's Review & capital management (pp.18-33: leverage/ICR/debt cost/WALE/occupancy, industry mix p33, top-10 customers p34), Investments & Divestments tables (pp.22-28), Portfolio Overview (pp.33-41), Statements of Financial Position (p106/Datalab 108), Consolidated Statement of Total Return (p107/Datalab 109), Distribution Statement (p108/Datalab 110-111), Cash Flow Statement (pp.124-127), Notes 4/5/11/19/20/21/22/24/25/30/31, Portfolio Statement (pp.111-125), Statistics of Unitholdings (p199/Datalab 8866-8890), Report of Trustee / Statement by Manager / General Note 1 (corporate identity). Did NOT consult any extractor tooling, page-map, gather notes, adapter output, or the FY2025 extraction.

Source: `parsed_reports_datalab/05_A17U.SI_CapitaLand-Ascendas-REIT_FY2024/full.md` (page-anchored). Markdown tables parsed cleanly; no PDF spot-check needed.

**Confirmed FYE: financial year ended 31 December 2024.** Every audited statement header reads "Year ended 31 December 2024" / "As at 31 December 2024". The 2024 figures are the **Group** column (first data column), verified against the Group consolidation throughout (not the Trust-only column, e.g. gross revenue 1,523,046 not Trust 10,004,000-basis; investment properties 16,758,446 not Trust 10,004,000).

---

## 1. Verdict & confidence

**Grade: MINOR ISSUES (bordering on CLEAN).**

This is a strong, disciplined extraction. Every audited financial-statement figure I re-derived matched the **Group 2024** column **to the dollar**: the full Consolidated Statement of Total Return reconciles exactly to "Total return for the year" (S$764,107k = `net_income`), all three income identities hold, the balance sheet and cash-flow subtotals tie, gross revenue ties to Note 19, trust expenses tie to Note 22, tax credit ties to Note 24, EPU/DPU/NDI tie to Note 25 and the Distribution Statement, the 23-row customer-industry mix sums to exactly 100.0%, the top-10 customers match p34 verbatim, the 229 property rows sum exactly to Note 4 + Note 5 (16,758,446 + 268,734 = 17,027,180), and all six property transactions match pp.23/28. The task's two flagged risks both resolve in the extraction's favour: `portfolio_value` is correctly on the **owned consolidated-IP** basis (excl. IPUD and the equity-accounted JV), matching the disclosed S$16.8bn headline; and `top_tenants.industry` is correctly null because the source table (p34) discloses only geography, no per-tenant industry.

The only defects are minor: (a) `cash_flow_metrics.net_cash_flow` = the disclosed change-in-cash (−53,838), which does **not** equal the sum of the three activity subtotals (−58,840) because the S$5,002k unrealised-FX-on-cash line has no home; (b) a small internal tension where `property_transactions` records Summerville's S$94.8m estimated development cost as `purchase_price` while `_notes` states that figure "is not an acquisition cost … not used as a purchase_price proxy"; (c) the three-property Australian divestment repeats the S$64.2m **aggregate** sale price in each of its three rows (triple-count risk, but documented). None is material.

Tally: **CONFIRMED ≈ 45** · **DISCREPANCY = 2 (both LOW)** · **SUSPECTED-OMISSION = 2 (LOW)** · **UNVERIFIABLE = 2**

---

## 2. Discrepancies

### D1 — `cash_flow_metrics.net_cash_flow` = −53,838,000 fails the Σ-of-three identity (LOW)
- Extraction: `operating_cash_flow` 947,832k, `investing_cash_flow` −62,463k, `financing_cash_flow` −944,209k, `net_cash_flow` −53,838k.
- Source (Cash Flow Statement, p124/Datalab 5969, and p127/Datalab 6004-6008): the three activity subtotals are correct to the dollar. But 947,832 − 62,463 − 944,209 = **−58,840**, whereas the stored `net_cash_flow` is **−53,838** = the disclosed "Net (decrease) in cash and cash equivalents" (beginning 221,579 → end 167,741). The gap of **+5,002** is the disclosed "Effect of exchange rate changes on cash balances" (p127, line 6007).
- Consequence: `net_cash_flow` ≠ operating+investing+financing by S$5,002k. Depending on the schema's convention this is either (i) correct-as-change-in-cash but breaks the additive identity, or (ii) should be −58,840 with the FX-on-cash effect captured separately. Either way the FX line currently has no home.
- Fix: capture "Effect of exchange rate changes on cash balances" S$5,002k (p127) OR document that `net_cash_flow` is the reported change-in-cash (incl. FX), not the activity sum. Severity LOW. Confidence HIGH.

### D2 — `property_transactions` Summerville `purchase_price` = 94,800,000 contradicts `_notes` guidance (LOW)
- Extraction: the Summerville Logistics Center transaction row carries `purchase_price` 94,800,000 (SGD), `status` "development".
- `_notes.columns_never_fillable` (Summerville): "the report discloses only an estimated investment cost (S$94.8m) … neither is an acquisition cost … **Not used as a purchase_price proxy per schema guidance.**" (Source p23 ONGOING PROJECTS table, line 1562-1563: "Acquisition under Development 94.8".)
- Consequence: the same S$94.8m the notes say is *not* a purchase price is stored as `purchase_price` in the transaction artifact. Defensible as an estimated project cost, but it is internally inconsistent with the extractor's own stated rule and could mislead a consumer treating it as a completed-acquisition price. Severity LOW. Confidence HIGH.

---

## 3. Suspected omissions

### O1 — Top-10 customers' geographical location disclosed but not captured (LOW)
- Source p34 (lines 2081-2092): the top-10 table's third column is "Geographical location of property" (Singapore / USA / UK) — e.g. Singtel/Singapore, Stripe/USA, Entserv/UK. The extraction captures `client_name` and `revenue_pct` but not the geography.
- Whether capturable depends on the schema; `top_tenants` appears to have no geography field, so this is likely no-home. Flagged for completeness. Severity LOW.

### O2 — "Effect of exchange rate changes on cash balances" S$5,002k not captured (LOW)
- Source p127 (line 6007). See D1 — this is the line that breaks the cash-flow additive identity. If the schema expects `net_cash_flow` = Σ activities, this FX line is a genuine omission; otherwise it is a documentation gap. Severity LOW.

---

## 4. Reconciliation results (independently re-computed)

### Statement of Total Return tie-out (Group 2024, p107/Datalab 5266-5292) — PASS (exact)
Using the 13 `line_items`:
- Σ(revenue) = 1,244,634 + 278,412 = **1,523,046**
- Σ(expense) = 473,121 + 86,197 + 12,385 + 271,265 = **842,968**
- Σ(adjustments, signed) = −25,862 + 45,362 + 43,699 − 8,369 + 10,842 + 496 + 17,861 = **+84,029**
- 1,523,046 − 842,968 + 84,029 = **764,107k = "Total return for the year"** = `income_stmt_metrics.net_income` ✓ exact.
- No line missing: the P&L below-NPI lines (base mgmt fee, trust expenses, finance costs net, net FX, gain on disposal, FV derivatives, FV ROU, FV IP/IPUD/IPHS, share of assoc/JV, tax credit) are all present; the "Net income" subtotal (699,578) and per-note detail are correctly not double-counted.

### Three income identities — PASS
- I1  operating_income = gross_income − operating_expense: 1,049,925 − 98,582 = **951,343** ✓ (operating_expense 98,582 = base mgmt fee 86,197 + trust expenses 12,385 ✓).
- I2  ebit = pretax + interest_expense_non_operating: 746,246 + 271,265 = **1,017,511** ✓ (= ebitda; no D&A, reasonable for a REIT).
- I3  net_income = pretax − income_taxes: 746,246 − (−17,861) = **764,107** ✓ (tax credit stored negative). Attribution: unitholders 755,082 + perpetual 9,025 + minorities(null=0) = **764,107** ✓ (p107 attribution split, lines 5290-5291). `minorities` null is correct — the Total Return has no NCI attribution line; the S$671k NCI on the balance sheet is a FY capital contribution (p127 financing), not a profit share.
- interest_expense_non_operating 271,265 = "Finance costs, net" (p107 line 5278, Note 23) — disclosed directly, not derived from gross-minus-income components ✓.
- non_operating_income_or_loss −205,097 = Σ(finance costs net + net FX + gain on disposal + FV derivatives + FV ROU + FV IP + share of assoc/JV) ✓ (951,343 + (−205,097) = 746,246). Internally consistent derived helper.

### total_revenue == gross_revenue == Σ(revenue line_items) — PASS
1,523,046,000 == 1,523,046,000 == 1,523,046,000 ✓. Note 19 (p172): Property rental income 1,244,634 + Other income 278,412 = 1,523,046 ✓. Cross-check E holds — "Other income" is genuinely inside gross revenue per Note 19 (not mis-bucketed below-the-line, unlike the HMN case).

### gross_income == NPI; cost_of_revenue == property opex — PASS
gross_income 1,049,925 = Net property income (p107) ✓; cost_of_revenue 473,121 = Property operating expenses (Note 20) ✓. Segment note (Datalab 8776) confirms total NPI 1,049,925.

### Trust expenses (Note 22, p174) — PASS
Audit 1,135 + Non-audit 45 + Professional 3,820 + Valuation 905 + Trustee 3,307 + Other 3,173 = **12,385** ✓. `operating_expense_breakdown` matches Note 22 line-for-line plus base mgmt fee 86,197; Σ = 98,582 = operating_expense ✓.

### Tax credit (Note 24, p174) — PASS
Current tax 16,579 + deferred reversal (34,440) = **(17,861)** net credit ✓ = `income_taxes` −17,861,000.

### Balance sheet (Group 2024, p106/Datalab 5205-5257) — PASS
total_asset 18,269,010 ✓; total_liabilities 7,960,495 ✓; total_equity 10,308,515 ✓; total_current_asset 350,213 ✓; total_non_current_asset 17,918,797 ✓; total_current_liabilities 1,520,504 ✓; total_non_current_liabilities 6,439,991 ✓; working_capital = 350,213 − 1,520,504 = **−1,170,291** ✓. nav_per_unit 2.27 (Group) ✓; units in issue 4,400,309k = `number_of_shareholder_units` ✓.

### Cash flow (p124/p127) — PASS on subtotals (see D1 for net)
operating 947,832 ✓; investing −62,463 ✓; financing −944,209 ✓; capital_expenditure −227,159 = capital improvement 106,961 + net IPUD payment 108,231 + IPUD acquisition 11,967 ✓. `net_cash_flow` −53,838 = disclosed change in cash (see D1).

### EPU / weighted-avg units (Note 25, p175) — PASS
weighted_avg_shares_basic 4,395,569k ✓ (= 4,395,568 outstanding + 1 mgmt-fee units); diluted = basic ✓ (Note 25(b)).

### Distribution / NDI / DPU — PASS
net_distributable_income 668,833 = "Total amount available for distribution to Unitholders **for the year**" (p108 line 5320; Note 25(c) line 7897) — correctly the FY-generated figure, EXCLUDING the S$327,300 opening carried-forward balance and NOT after-retention ✓. DPU 15.205c ✓ (p107/p108/Note 25). distribution_record: H1 7.524c (01/01–30/06/24, p108 line 5321) + H2 7.681c = **15.205c** ✓ full-year. `distribution_basis` "full_payout_no_retention_line" — correct, the Distribution Statement shows no retention line. `distribution_paid` null is defensible (no single FY2024-income distribution-paid figure; H2 declared post-FYE).

### Portfolio valuation sum (Portfolio Statement, p111-125 / Note 4/5) — PASS (exact)
Σ(properties.json market_valuation, all 229 rows) = **17,027,180,000**. Split: 225 operating IP = **16,758,446k** = "Total Group's investment properties (Note 4)" (Datalab 5882) = balance-sheet Investment properties (line 5209) = `performance.portfolio_value` ✓; 4 IPUD rows = **268,734k** = Note 5 (line 5883) ✓. The equity-accounted JV (1 Science Park Drive, 34% redevelopment) is correctly OUTSIDE these rows (held as Investment in a joint venture 142k / associate 118,456k). **`portfolio_value` basis = owned consolidated IP, matching the disclosed S$16.8bn headline (pp.94/180/1816) — the flagged owned-vs-incl-JV risk is handled correctly.**

### Trade mix (p33 "Customer's Industry Diversification by Gross Rental Income") — PASS (exact 100.0%)
All 23 disclosed industry rows captured, every `pct` matches the source table (Datalab 2037-2059), `category_raw` faithful, `pct_basis` "gri" correct. Σ = 11.8+11.8+10.3+10.2+8.8+8.6+6.1+5.8+4.7+4.0+3.8+3.6+2.6+2.2+2.1+0.9+0.9+0.7+0.5+0.2+0.2+0.1+0.1 = **100.0%** ✓.

### Top tenants (p34) — PASS
10 rows captured, ranks 1-10 contiguous, %s descending, all names + `revenue_pct` match p34 verbatim (Singtel 3.1 … JPMorgan 0.9). `pct_basis` "gross_revenue" correct (table = "by Monthly Gross Revenue"). **`industry` all null is CORRECT — the source table has no industry column (only geography); flagged risk confirmed as a true null, not an omission.** Σ = 16.2% (no aggregate "top-10 = X%" disclosed to check against).

### Property transactions (pp.23/28) — PASS
Australian trio (77 Logistics 25.7 / 62 Sandstone 15.4 / 92 Sandstone 19.3 valuations; aggregate sale S$64.2m; gain S$628k; carrying amounts from Note 11 A$27.0/15.9/26.3m → S$24.359/14.345/23.728m) all match p28 (Datalab 1800-1802) + Note 30 (Datalab 7423-7427) ✓. 21 Jalan Buroh S$112.8m sale / S$67.5m valuation & carrying ✓ (p28 + Portfolio Statement line 5547). Trio + Buroh = 177.0 sale / 127.9 valuation ✓ (matches p28 total and the p10 "S$177m, ~38% premium" prose). Summerville (dev) and DHL Indianapolis (subsequent event, 15 Jan 2025) match p23. No FY2024 completed acquisition exists (Cash Flow "Acquisition of investment properties" 2024 = nil) — correctly none recorded. See D2 for the Summerville `purchase_price` tension.

---

## 5. Nulls / inference audit

**Confirmed genuinely absent (correct nulls):**
- `properties.net_property_income` / `npi_pct` — NPI disclosed only at 3-segment level (Note 31, Datalab 8776), never per property. Property listing (pp.44-69) has GFA/NLA/Gross Revenue/Occupancy only, no NPI column. Correct null + correct reason ✓.
- `properties.ownership` — Portfolio Statement discloses "% of net assets attributable to unitholders" (a weight, not a stake); all 229 rows presented at Group carrying amount. Correct ✓.
- IPUD rows' gross_revenue/occupancy/GFA/NLA — under development at 31 Dec 2024, shown as dashes in the listing (pp.45/50/65). Correct absence ✓.
- `top_tenants.industry` — CORRECT (see §4; p34 has no industry column).
- `income_stmt_metrics.minorities` — CORRECT (no NCI in Total Return attribution; see §4 I3).
- `financial.funds_from_operation` / `cash_flow.free_cash_flow` — not disclosed. Correct ✓.

**`_derived` fields (declared, verified):** operating_income, ebit, ebitda, non_operating_income_or_loss, interest_expense_non_operating — all five correctly listed in `income_stmt_metrics._derived[]`; disclosed inputs transcribed correctly and identities hold (§4). No unflagged derived value found.

**`_notes.inferred[]` is empty** — appropriate; I found no undocumented inference in the 5 files under test. (Property-level `lease_expiry_date`/`lease_term_years` in properties.json are largely disclosed directly in the Portfolio Statement's "Term of Lease / Lease Expiry" columns — e.g. Datalab 5454-5457 — so unlike some peers these are NOT back-calculated inferences.)

**Minor label/mapping nits (not defects):**
- `revenue_breakdown[0].category` = "base_rental" labels Note 19's "Property rental income" — cosmetic; amount 1,244,634 correct.
- trade_mix canonical mapping "Engineering" → "Infrastructure, Real Estate & Property Services" is debatable (Engineering reads more as Manufacturing/industrial services), but `category_raw` "Engineering" is preserved faithfully. LOW.
- properties.json: all 229 rows carry `status` "active", including the 4 IPUD; they are not distinctly flagged as under-development in the row status (though `_notes` documents them and the transaction row uses status "development"). LOW.

---

## 6. Confirmed-correct highlights (balance)

- **Every audited FS figure exact** to the Group 2024 column — gross revenue, opex, NPI, every below-the-line item, finance costs net, tax credit, total return, attribution split, distributable income, DPU, EPU, weighted-avg units, full balance sheet, cash-flow subtotals, capex.
- **Full Statement of Total Return reconciles to 764,107k exactly** — no missing/extra line.
- **Portfolio reconciles to the dollar**: 229 rows → 16,758,446 (operating, Note 4) + 268,734 (IPUD, Note 5) = 17,027,180; JV correctly excluded; `portfolio_value` on the right (owned-IP) basis.
- **Trade mix sums to exactly 100.0%** across all 23 disclosed industries; top-10 customers verbatim.
- **Property transactions** — trio + Buroh divestments, Summerville development, DHL subsequent-event acquisition all correctly sourced and classified; no phantom FY2024 acquisition.
- **Capital metrics** all confirmed: aggregate leverage 37.7% (p19/Note), ICR 3.6x, all-in debt cost 3.7%, debt maturity 3.5y, WALE 3.7y (p31), portfolio occupancy 92.8% (p31), NAV/unit 2.27, unitholders 36,513 (p199), units 4,400,309k.
- **Corporate identity** exact: Manager CapitaLand Ascendas REIT Management Limited, Trustee HSBC Institutional Trust Services (Singapore) Limited, Sponsor CapitaLand Investment Limited (100% owner of the Manager) — all confirmed (Note 1, Report of Trustee, p29 structure chart). sub_sector "Industrial" and income_model "conventional" correct.

---

## 7. Could NOT verify

- `distribution_record[].ex_date` / `pay_date` — null; the pages reviewed (Distribution Statement p108, Note 25) give periods and per-unit amounts but no ex/pay dates. Not disclosed on the audited-statement pages; left null (UNVERIFIABLE from the parse).
- Exact SGD-equivalent per-property gross revenue tie: `_notes` reconciles Σ(225 per-property gross revenue) = S$1,516.3m vs audited S$1,523.046m (~6.7m gap = rounding + divested trio/21 Jalan Buroh + IPUD timing). The per-property figures are as-disclosed 0.1M-precision and not scaled to tie; the residual is explained but not independently closable to the dollar (UNVERIFIABLE by design).

---

### Fix list (page-cited)
1. **financial.json → cash_flow_metrics** (LOW): `net_cash_flow` −53,838,000 = disclosed change-in-cash, ≠ Σ(activities) −58,840,000; the S$5,002k "Effect of exchange rate changes on cash balances" (p127) has no home — capture it or document the convention.
2. **property_transactions.json → Summerville Logistics Center.purchase_price** (LOW): S$94.8m is an **estimated development cost** (p23 "Acquisition under Development 94.8"), which `_notes` itself says is "not an acquisition cost … not used as a purchase_price proxy"; reconcile the artifact with the note (either drop it from `purchase_price` or annotate it as estimated project cost).
3. **property_transactions.json → Australian trio gross_sale_price** (LOW): each of 77 Logistics Place / 62 Sandstone Place / 92 Sandstone Place repeats the **aggregate** S$64.2m (p28 discloses only the trio total); documented in `carrying_value_basis` but carries triple-count risk in any naïve Σ.
4. **top_tenants.json → geography** (LOW, likely no schema home): p34 discloses each customer's property geography (Singapore/USA/UK); not captured.
5. **trade_mix.json → category mapping** (LOW): "Engineering" (p33) mapped to "Infrastructure, Real Estate & Property Services"; consider Manufacturing/Industrial. `category_raw` is correct, so no data loss.
