# AW9U — First REIT (AW9U.SI) FY2025 — Forensic Extraction Audit

## 1. Method header

Independent verification against source. I navigated the report myself from the TOC and read whole sections — **not** the extractor's page-map, anchor list, or reasoning. Sections read: Financial Highlights (pp.5-7), Letter to Unitholders / portfolio overview (pp.8-11), key statistics banner (p18), Trust Structure (p19), property cards / Operations Review (pp.28-44), Investor Relations & Financial Calendar (p46), About First REIT / sponsor disclosure (p49), audited **Statements of Total Return / Distribution / Movement** (pp.127-130), **Statements of Portfolio** (pp.136-145), revenue/expense/finance notes 16-22 (pp.173-175), distribution note 24 (p189 area), subsequent events note 32 (p199), IPT (p200), and Statistics of Unitholdings (p201).

Source: `parsed_reports_datalab/17_AW9U.SI_First-REIT_FY2025/full.md` (page-anchored `<!-- PAGE N -->`). Did NOT consult any extractor tooling. All financial reconciliations re-derived from scratch.

---

## 2. Verdict & confidence

**Grade: MINOR ISSUES.**

The extraction is strong on the audited numbers: all 30 active property valuations match the Statements of Portfolio to the dollar, the portfolio total (S$1,022,619k) reconciles exactly, the full Statement of Total Return reconciles to total return (S$28,982k) to the dollar, gross revenue / NPI / DPU / unitholders all check out, the healthcare size-metric handling (GFA + beds/rooms, no NLA) is correct, and the HGB/BOT→Leasehold tenure mapping is right. The defects are: (a) a **revenue-classification slip** (`finance_income` tagged `statement="revenue"`) that breaks the Σrevenue tie-out — the exact HMN bug; (b) **disclosed per-property lease-expiry dates were overridden by wrong back-calculated land-title dates**; (c) **a disclosed value left null** (4Q2025 DPU = 0.52¢); (d) **systematic unflagged inferences** (all `lease_expiry_date` / `lease_term_years`, the trade_sector on top-tenant rank 2).

Tally: **CONFIRMED ≈ 28** · **DISCREPANCY = 4** · **SUSPECTED-OMISSION = 2** · **UNVERIFIABLE = 1**

---

## 3. Discrepancies

### D1 — income_components: `finance_income` mislabelled `statement="revenue"` (MED, HIGH confidence)
- Extraction: `finance_income` 269,000 tagged `statement: "revenue"`.
- Source (Note 18, p174; Statement of Total Return, p127): Finance income sits **below** "Net property and other income", it is not part of gross revenue. Gross revenue (Note 16, p173) = rental income 100,526 + dividend income from share trading 5 = **100,531k**.
- Consequence: Σ(income_components where statement=`revenue`) = 100,526 + 5 + 269 = **100,800k**, which does NOT equal `performance.gross_revenue` (100,531k). The Σrevenue=gross_revenue invariant fails by exactly the finance-income line. This is the recurring HMN mis-bucketing class.
- Fix: set finance_income `statement="adjustment"` (or `expense`-side income line); it is correctly signed in the full tie-out either way, so total return still reconciles. Labelling defect, not a value error.

### D2 — Per-property `lease_expiry_date` overridden by wrong inferred land-title dates (MED, HIGH confidence)
- Singapore property cards disclose the **actual master-lease expiry** explicitly:
  - Precious Homes @ Bukit Merah — card (p~30): **"Lease Expiry Date: 10 April 2027"** (Lease Term 10 years). Extraction shipped `lease_expiry_date = 2032-04-21` (back-calculated from the 30-yr land title from 2002). WRONG.
  - Precious Homes @ Bukit Panjang — card: **"Lease Expiry Date: 10 April 2027"**. Extraction shipped `2033-05-13`. WRONG.
- The extractor conflated the **land-title tenure** (30/99-yr leasehold) with the **lease term**. The Portfolio Statement's "Term of lease / Remaining term of lease" columns are explicitly the *master-lease* terms (note (a)/(b), p143: "the entire tenure of the master lease terms"), and the cards disclose the lease expiry date outright. The shipped values are inferred land-title dates, not the disclosed lease dates.
- Consequence: WALE-relevant lease expiries are wrong for at least the 3 SG rows; the Indonesia/Japan rows are also derived (see N-audit), not disclosed.
- Severity MED (a disclosed value was replaced by a wrong derived one).

### D3 — 4Q2025 DPU left null though disclosed (LOW–MED, HIGH confidence)
- Extraction: `distribution_record[3].dpu = null` (period 1 Oct–31 Dec 2025).
- Source: Note 32 subsequent events (p199, item iii): **"On 5 February 2026, the Manager declared a distribution of 0.52 cents per unit, amounting to $11,028,000, in respect of the period from 1 October 2025 to 31 December 2025."**
- The four declared FY2025 DPUs are 0.58 + 0.55 + 0.52 + 0.52 = **2.17¢** = `performance.dpu` (p128) ✓. The 4Q figure is disclosed and should be 0.52, not null.
- Severity LOW–MED (the total is right; only the per-quarter breakdown is incomplete).

### D4 — top_tenants rank 2 `trade_sector` is an unflagged inference (LOW, HIGH confidence)
- Extraction: PT Lippo Karawaci Tbk → `trade_sector: "Real Estate & Property Services"`.
- Source (p5): the "Rental Income by Tenant Mix" table has **no trade-sector column** — only tenant name and %. Every `trade_sector` in top_tenants.json is assigned from the tenant name / business, i.e. an inference, and none is recorded in `_notes.inferred[]`. (The §0 invariant requires top-tenant sector assigned from a name to be flagged.)
- Severity LOW (assignments are reasonable), but provenance is understated.

---

## 4. Suspected omissions

### O1 — Per-property disclosed lease expiry dates / land-title detail on the cards (MED)
The property cards (pp.28-44) disclose, per property, **Land Title**, **Remaining Land Title Tenure**, **Lease Term**, and an explicit **Lease Expiry Date** (e.g. Bukit Merah "10 April 2027"; "Remaining Land Title Tenure 6.3 years"). These are exactly the fields the extraction back-calculated incorrectly. They have a schema home (`lease_expiry_date`, `lease_term_years`, `tenure_raw`) and should have been used as the *disclosed* source rather than inferred. SEVERITY: MED (data exists, has a home, was bypassed in favour of a wrong inference).

### O2 — Distribution record/ex dates not captured (LOW)
`distribution_record` has all `ex_date = null`. The report does not print record/ex dates in the audited statements; only payment dates (p46 Financial Calendar) are disclosed. The nulls are therefore defensible — flagged only for completeness; no schema-fillable ex-date is in the parse. SEVERITY: LOW (genuine non-disclosure of ex-dates).

---

## 5. Reconciliation results (independently re-computed)

### Statement of Total Return tie-out (Group, p127) — PASS
- Revenue (Note 16): rental 100,526 + dividend 5 = **100,531** = gross_revenue ✓
- Property operating expenses (Note 17): 1,428 + 311 + 930 + 236 + 286 = **3,191** ✓ → NPI 100,531 − 3,191 = **97,340** = net_property_income ✓
- Below NPI: +finance income 269 − mgmt fees 8,502 − asset mgmt 1,008 − trustee 341 − finance costs 20,900 − other expenses 4,647 = **net income 62,211** ✓
- Adjustments: FV loss IP −3,528 − loss on disposal of subsidiary 7,535 + FV gain derivatives 473 − FX loss 8,308 = **before tax 43,313** ✓
- − income tax 14,331 = **total return for the year 28,982** ✓ exact (attributable: 27,326 unitholders + 1,656 perpetual securities).
- income_components captures every STR line; complete for the Group column.

### Σ income_components revenue = gross_revenue — **FAIL** (see D1)
100,526 + 5 + 269 (finance income mis-bucketed) = 100,800 ≠ 100,531. Drop finance income from the revenue bucket → 100,531 = PASS.

### Gross revenue note (Note 16, p173) — PASS
100,526 + 5 = **100,531k** ✓ (incl. variable rent 3,926 and straight-lining 7,446 per note).

### Property operating expenses (Note 17, p173) — PASS — **3,191k**.

### Distribution + DPU (p128 / p199) — PASS (with D3 gap)
Distributable amount FY2025 = **45.8M** (p6) = net_distributable_income ✓. DPU 2.17¢ (p128) ✓. Quarterly 0.58 + 0.55 + 0.52 + 0.52 = 2.17 ✓ (4Q null in extraction — D3). Pay dates 26 Jun / 25 Sep / 18 Dec 2025 / 30 Mar 2026 ✓ (p46).

### Σ properties.market_valuation → portfolio total — PASS
Σ(30 active valued rows) = **1,022,619k** = Portfolio Statement total (p143) ✓. Spot-checked ~20 rows across SG/Indonesia/Japan against pp.136-143 — all exact. Imperial Aryaduta = nil (divested, p140) ✓; performance.portfolio_value 1,022,619,000 ✓ (also matches AUM headline 1,022.6M, p7).

### Trade mix → 100% — PASS
89.4 + 5.6 + 5.0 = **100%** (p5) ✓. pct_basis footnote: "Before recognition of FRS 116 rental straight-lining adjustments" (p5 note 2) — captured as `rental_income` (scope wording could be tightened but acceptable).

### Top tenants — PASS
All 11 tenants captured, ranks/percentages match p5 exactly; Σ = 100% ✓ (report lists all 11 — First REIT has only 11 tenants).

---

## 6. Nulls / inference audit

**Confirmed genuinely absent (correct nulls):**
- `properties.nla` — Portfolio Statement uses **Gross floor area in m²** only; cards confirm GFA, no NLA. Correct structural null with correct reason (p136-143). ✓
- `properties.net_property_income` (per property) — only Group NPI (97,340) is audited; no segment/per-property NPI table exists. Correct null. ✓
- `properties.occupancy_rate` per-property — only portfolio "total committed occupancy 100%" (p18). Correctly **inferred** and flagged in `_notes.inferred`. ✓
- Imperial Aryaduta valuation null (divested Dec 2025, nil in Portfolio Statement p140). ✓
- `ex_date` nulls — record/ex dates not disclosed (see O2). ✓

**Wrong / understated provenance:**
- **All `lease_expiry_date` and `lease_term_years` are derived/inferred, and none is flagged in `_notes.inferred`** (only occupancy is flagged). The SG dates are wrong vs the disclosed card dates (D2); the Indonesia "2035-12-31" dates are the extractor's pick of the first 15-yr master-lease term end, while the Portfolio Statement states "15+15 years / 25 years remaining" (i.e. ~2050 if extendable) — a judgment call, but unflagged. Same unflagged-inference class as HMN's ~50 back-calculated expiries.
- top_tenants `trade_sector` — assigned from tenant identity, not a disclosed column; unflagged (D4).
- `valuation_date = 2025-12-31` uniform — correct ("As at 31 December 2025") but assigned, not per-row disclosed.

**Tenure mapping — CORRECT:** HGB → Leasehold, BOT → Leasehold, Japan Freehold ✓, with dual-lease rows (Manado hospital 2035 + hotel 2027; Kupang/Baubau hospital + mall) carrying the earlier expiry and both terms verbatim in `tenure_raw` per REFERENCE §3. Well handled.

---

## 7. Confirmed-correct highlights

- **All 30 active property valuations exact** to the Statements of Portfolio (pp.136-143); portfolio total 1,022,619k reconciles to the dollar.
- **Full Statement of Total Return reconciles to total return 28,982k exactly** — every line present, perpetual-securities split correct.
- **Gross revenue, NPI, distributable income, DPU 2.17¢, unitholders 12,773** (p201, dated 13 Mar 2026) all correct.
- **Healthcare sub-sector handled correctly**: no NLA (GFA only), beds/rooms (6,305 total) parked in `data_with_no_home`, income_model = master_lease, occupancy inference flagged.
- **Multi-currency handled**: all carrying values taken in SGD from the audited Portfolio Statement; both FX rate pairs (avg + closing, JPY and IDR) recorded in `_notes`.
- **Tenure**: HGB/BOT→Leasehold mapping correct; dual-expiry combined rows handled with earlier expiry + verbatim raw.
- **Sponsors correct**: OUE Limited (60%) + OUE Healthcare Limited (40%) jointly the Sponsors (p49); manager/trustee correct; cross-file consistent with `_notes`.
- **Divestment** (Imperial Aryaduta, 4 Dec 2025, loss on disposal 7,535k, carrying value 27,723k FY2024) captured in property_transactions and properties with status=divested.

---

## 8. Could NOT verify

- **Per-property NPI in SGD** — genuinely not disclosed anywhere (only Group NPI). The null stands.
- **Per-property gross_revenue exactness** — the per-property figures are the property-card "FY2025 Rental Income" in S$ millions rounded to 1 d.p. (marketing, before FRS 116 straight-lining); they sum to ~100.4M vs audited 100,531k. The ~131k gap is rounding and the gap explanation in `_notes` is correct. Exact per-property SGD revenue is not derivable. (The extraction transparently flags these as card-derived.)
- **Exact Indonesia master-lease expiry years** — the Portfolio Statement says "25 years remaining" (extendable HGB) while the front matter implies first-term ends ~2035; without a single explicit per-property expiry in the audited statement, the precise date is a judgment call, not verifiable to the day.
