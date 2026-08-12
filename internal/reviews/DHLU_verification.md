# DHLU — Daiwa House Logistics Trust (DHLU.SI) FY2025 — Forensic Extraction Audit

Auditor: independent verification against source. Navigated the report myself from the CONTENTS (p2/30) and TOC: Corporate Profile p6, Highlights p7, Trust Structure p9, Portfolio Overview pp.26-27, Our Properties (per-property cards) pp.28-46, Operational Review (tenants/trade mix/acquisition/valuation) pp.50-54, Investor Relations calendar p56, Consolidated Statement of Comprehensive Income p162, Distribution Statement p163, Statement of Changes in Unitholders' Funds p164, Statement of Portfolio p166, Notes 17-24 pp.191-193, post-year-end distribution announcement p203, Statistics of Unitholdings pp.205-206. Did NOT consult any extractor tooling / page-map / anchor list / reasoning.

Source: `parsed_reports_datalab/12_DHLU.SI_Daiwa-House-Logistics-Trust_FY2025/full.md` (page-anchored `<!-- PAGE N -->`). Markdown tables parsed cleanly; no PDF spot-check needed.

---

## 1. Verdict & confidence

**Grade: MINOR ISSUES (one MED-severity reconciliation defect: the distribution_record).**

The extraction is strong on the hard financials. Every audited financial-statement figure I re-derived matches the Group column to the dollar: the full Statement of Total Return reconciles exactly to "Total return for the year" S$35,654k; Σrevenue in income_components = gross_revenue (S$57,794k) — **the HMN finance/other-income-as-revenue bug is NOT present here** (Other income is correctly bucketed as an `adjustment`); NPI, gross-revenue note, property-opex note, distributable income, all 19 property valuations from the audited Statement of Portfolio, top-10 tenants, and trade mix all tie out. Currency handling (JPY/VND local per-row, SGD for audited statements; closing FX captured, average FX correctly noted as undisclosed) is handled well for a multi-currency trust. Land-tenure freehold/leasehold enums and tenure_raw are accurate.

The material defect is the **`distribution_record`**: it lists the two half-year distributions *paid during* FY2025 (H2-2024 2.34c + H1-2025 2.24c = 4.58c) instead of the two half-years *attributable to* FY2025 (H1-2025 2.24c + H2-2025 2.09c = 4.33c). The recorded periods sum to 4.58c, which does NOT equal the reported `dpu` of 4.33c, and the H2-2025 distribution (2.09c, announced 27 Feb 2026, p203) is missing. Secondary issues: an unflagged + numerically-off `consideration_sgd` on the acquisition; a small portfolio_value inconsistency (835,200,000 shipped vs 835,157,000 audited/used in _notes); a self-contradicting note typo; and one missing (Vietnam) property-manager role.

Tally: **CONFIRMED ≈ 35** · **DISCREPANCY = 4** · **SUSPECTED-OMISSION = 2** · **UNVERIFIABLE = 1**

---

## 2. Discrepancies

### D1 — `performance.distribution_record` lists distributions PAID in the year, not those attributable to FY2025; sum ≠ reported DPU (MED)
- Extraction: record = [H2-2024 "1 July 2024 to 31 December 2024" 2.34c pay 2025-03-26] + [H1-2025 "1 January 2025 to 30 June 2025" 2.24c pay 2025-09-26]. These sum to **4.58c**.
- Reported `dpu` = **4.33c** (Distribution Statement p163; Financial Review p53: "DPU for FY2025 … 4.33 cents"). 4.58 ≠ 4.33 — the record does not reconcile to the headline.
- Source: the FY2025 DPU is composed of **H1-2025 2.24c** (paid 26 Sep 2025, p56/p163) **+ H2-2025 2.09c** (announced 27 Feb 2026 "for the period from 1 July 2025 to 31 December 2025", **p203 line**), = 4.33c. The H2-2024 2.34c distribution belongs to FY2024; it merely *paid* on 26 Mar 2025 and appears in the Distribution Statement as an opening-balance deduction, not as FY2025 DPU.
- Consequence: the distribution_record misstates which periods make up the financial-year DPU and omits the H2-2025 (2.09c, pay 26 Mar 2026) line. Any downstream "Σ record = DPU" check fails.
- Fix is source-grounded (do NOT just drop a line to balance): replace H2-2024 row with the H2-2025 row. Correct record: {period "1 January 2025 to 30 June 2025", dpu 2.24, pay_date 2025-09-26} + {period "1 July 2025 to 31 December 2025", dpu 2.09, pay_date 2026-03-26}. Severity MED, Confidence HIGH.

### D2 — `property_transactions[0].consideration_sgd` = 35,400,000 is undisclosed AND numerically off; unflagged inference (MED)
- Extraction ships `consideration` 3,990,000,000 JPY (correct, p51/p2260) but also `consideration_sgd` = **35,400,000** with no `_notes.inferred[]` entry.
- Source: the report discloses the consideration **only in JPY** (JPY3,990.0 million, p51). No SGD consideration is published anywhere (grep confirms). JPY3,990m ÷ the disclosed closing rate 122.00 = **S$32.7m**, not S$35.4m — so 35.4m is neither disclosed nor reproducible from any disclosed rate.
- Consequence: a fabricated-looking precise SGD figure presented as if derived. Per REFERENCE §0 inv. 7, an inferred value must be flagged; per inv. 8, an unreconcilable value should be investigated, not invented.
- Fix: set `consideration_sgd` = null (no SGD figure disclosed), OR if retained as a derived convenience value, recompute at the disclosed rate (≈32,700,000) AND add an `_notes.inferred[]` entry citing p6/p51. Preferred: null. Severity MED, Confidence HIGH.

### D3 — `performance.portfolio_value` = 835,200,000 vs audited Tier-C total 835,157,000 used by _notes (LOW)
- `performance.json` ships **835,200,000** (the S$835.2m marketing headline, p6/p7/p51). `_notes.reconciliation` uses and reconciles **835,157,000** (audited Statement of Portfolio total, p166). The two artefacts disagree by S$43k.
- REFERENCE §0 inv. 2 prefers the audited Portfolio Statement value (835,157,000) over the marketing summary (835.2m). The headline is defensible but inconsistent with the trust's own _notes.
- Fix: align both to the audited 835,157,000 (p166), or explicitly document the headline-vs-audited choice in performance.note. Severity LOW, Confidence HIGH.

### D4 — `performance.note` internal typo: "2.34 cents (H2 2024 paid Mar 2026)" (LOW)
- The note text says the 2.34c was "paid Mar 2026"; the `pay_date` field correctly says 2025-03-26, and the IR calendar (p56) confirms 26 March 2025. The note text is self-contradicting (and partly moot once D1 is fixed). Severity LOW, Confidence HIGH.

---

## 3. Suspected omissions

### O1 — `profile.management` omits the Vietnam property manager (LOW)
- p9 Trust Structure discloses **two** property managers: Japan — "Daiwa House Property Management Co., Ltd." (captured) and Vietnam — "**Daiwa House Vietnam Co., Ltd., Ho Chi Minh City Branch**" (not captured). It also names the Japan Asset Manager (Daiwa House Real Estate Investment Management Co., Ltd., captured in income_components note) and the Property Trustee (Sumitomo Mitsui Trust Bank, Limited — holds the 18 Japan properties in trust).
- Schema home exists (`management[]` accepts multiple `property_manager` rows). The Vietnam property_manager is a clean miss; the Property Trustee is arguably also a role worth capturing (Japanese TMK/TK-GK structure). Severity LOW.

### O2 — Per-property GRI/NPI disclosed (local currency) — null-reasons are accurate but worth scoping (LOW)
- The Portfolio Overview p27 discloses per-property NPI (all 19) and per-property Gross Revenue (7 multi-tenanted only) in **local currency** (JPY millions / VND millions). The extraction *did* capture these into `net_property_income`/`gross_revenue` with currency tags, and the single-tenant GR nulls are correctly justified by the confidentiality footnote (note 3, p26/p1110: "Not disclosed for properties with one tenant"). This is handled correctly — flagged here only to confirm the absence reasons stand (they do). No fix. Severity LOW.

---

## 4. Reconciliation results (independently re-computed)

### Statement of Total Return (Group, p162) — PASS (exact)
Using income_components:
- Σrevenue = 51,252 + 6,542 = **57,794** = `gross_revenue` ✓ (no mis-bucketing; Other income is `adjustment`, not revenue).
- Σexpense = property opex 13,595 (= 5,276+3,674+1,201+2,005+1,439 ✓) + mgr fees 2,075 + Japan AM 1,067 + trustee 283 + trust exp 773 + finance 9,216 = **27,009**.
- Σadjustments (signed) = other income +884 + FV inv prop +10,232 + FV deriv −174 + tax −6,073 = **+4,869**.
- 57,794 − 27,009 + 4,869 = **35,654** = "Total return for the year" (p162) ✓ exact.
- NPI check: 57,794 − 13,595 = **44,199** = reported NPI ✓.
- All 15 statement lines present; nothing missing.

### Gross Revenue (Note 18, p191) — PASS
51,252 + 6,542 = **57,794** ✓ = p162 gross revenue ✓ = performance.gross_revenue ✓.

### Property Operating Expenses (Note 19, p191) — PASS
5,276 + 3,674 + 1,201 + 2,005 + 1,439 = **13,595** ✓ = p162 property expenses ✓.

### Distribution / DPU — DI PASS, DPU-record FAIL (see D1)
- Income available for distribution (Distribution Statement p163) = **30,378** = performance.net_distributable_income ✓.
- DPU 4.33c (p163) is correct as a scalar, BUT distribution_record sums to 4.58c ≠ 4.33c — **FAIL** (D1). Correct components: 2.24c (H1-2025) + 2.09c (H2-2025, p203) = 4.33c.

### Portfolio valuation sum (Statement of Portfolio, p166) — PASS
Σ of all 19 audited S$'000 rows = **835,157k** ✓ = audited total (p166) ✓. Reconciles to balance sheet: investment properties S$984,117k (Note 24 p193 / Note 9) − ROU S$133,125k − ARO S$15,835k = **835,157k** (p166) ✓. Marketing headline 835.2m (p6/7/51) rounds to this. (performance ships 835,200,000 — see D3.)

### Per-property valuation spot-checks (card JPY → audited S$ at 122.00) — PASS
- DPL Kawasaki Yako: card JPY21,000m ÷122 = S$172,131k ≈ audited S$172,135k ✓.
- D Project Nagano Suzaka S: card JPY2,720m ÷122 = S$22,295k ≈ audited S$22,296k ✓.
- DPL Gunma Fujioka: audited S$42,870k; card valuation JPY5,230m ÷122 = S$42,869k ✓ (alt_value 5,230m correct; NOT the JPY5,210m acquisition-date valuation).

### Per-property NPI/GR row-mapping (p27 vs JSON) — PASS
The p27 table is ordered by the p26 regional sequence (which differs from JSON row order). Re-mapped by name: every JSON NPI (568, 246, 236, 128, 165, 178, 146, 187, 241, 185, 1248, 290, 209, 305, 170, 123, 54, 110 JPYm; Tan Duc VND 46,886m) matches its p27 row, and the 7 disclosed GR values (801/436/323/1768/402/382/155 JPYm) land on the correct multi-tenant properties; the 12 single-tenant GR nulls match the p27 "–" entries. Σ JPY NPI = 4,789m ≈ Japan NPI JPY4,787m (p53, table-rounding) ✓.

### Trade mix (p50) — PASS
3PL 79.6 + Retail 11.4 + E-commerce 5.8 + Manufacturing 3.3 = **100.1%** (report's own rounding; donut chart p50). pct_basis="gri" matches footnote 3 ("By GRI … monthly rent"). Canonical mapping (3PL→Logistics & Supply Chain Management; Retail/E-commerce→Other Retail Trades; Manufacturing→Other Industrial Trades) reasonable, E-commerce mapping flagged in _notes.inferred ✓.

### Top-10 tenants (p50) — PASS
All 10 names, sectors, and % match p50 exactly; Σ = 66.6% (= disclosed subtotal) ✓. pct_basis="npi" is correct and unusual — matches footnote 4 ("Based on NPI for FY2025 … allocated … by NLA proportion"). Anonymised Tenants A/B/C captured with disclosed sectors ✓.

### Unitholders (p205) — PASS
4,865 unitholders ✓; as at 12 March 2026 ✓; total units 700,739,269 ✓.

### Acquisition (DPL Gunma Fujioka, p51) — mostly PASS (see D2)
date 24 Mar 2025 ✓; consideration JPY3,990m ✓; vendor Mitsubishi HC Capital Estate Plus Inc. ✓; valuation_at_acquisition JPY5,210m ✓ (31 Jan 2025 valuation). Only defect: consideration_sgd (D2). Tan Duc 2 (5 Jul 2024) correctly excluded from FY2025 transactions.

---

## 5. Nulls / inference audit

**Confirmed genuinely absent (correct nulls):**
- `properties.gla` (all 19) — report discloses NLA (sqm), never GLA, for a logistics/industrial trust (p26). Correct. ✓
- `properties.gross_revenue` for the 12 single-tenant rows — note 3 (p26/p1110) explicitly withholds single-tenant GR for confidentiality; matches the p27 "–" entries. Correct null + correct reason. ✓
- `distribution_record[].ex_date` (both) — only payment dates are disclosed (IR calendar p56); ex-dates not in the report. Correct null.
- `properties.lease_term_years` — cards give tenure as "expiring <Month Year>" / "Freehold", not a term in years; null is correct.

**Inferences — flagged correctly:**
- `lease_expiry_date` month-end derivations (Kuki 2034-07-31, Misato 2045-02-28, Kawasaki 2067-03-31, Shinfuji 2065-03-31, Okayama 2067-04-30, Fukuoka 2068-03-31, Okayama 2 2051-11-30, Tan Duc 2058-06-30) — derived from "expiring in <Month Year>" card text, day-of-month set to month-end; **flagged** in `_notes.inferred[]` ✓. (Cross-checked Tan Duc p46 "Leasehold expiring in June 2058" ✓.) Provenance honestly stated.
- `top_tenants.trade_sector` canonical mapping and `trade_mix` E-commerce mapping — flagged ✓.

**Unflagged / wrong inferences:**
- `property_transactions[0].consideration_sgd` = 35,400,000 — **unflagged and not reproducible** from any disclosed FX rate (D2). This is the one genuine inference-flagging defect.

**Other:**
- `valuation_date` 2025-12-31 uniform — correct (Statement of Portfolio "As at 31 December 2025", p166); an assigned uniform value, acceptable.
- `properties.major_tenant` — disclosed in card prose (pp.28-46); the _notes correctly states these are disclosed, not inferred. ✓

---

## 6. Confirmed-correct highlights (balance)

- **All audited FS figures exact** to the Group column: gross revenue, property opex, NPI, every below-NPI line, FV changes, tax, total return, distributable income.
- **Full Statement of Total Return reconciles to S$35,654k exactly** — no missing line; income_components complete (15 lines).
- **No HMN-class mis-bucketing** — Other income (884) sits as `adjustment`, so Σrevenue = gross_revenue cleanly.
- **All 19 properties present** (18 Japan + 1 Vietnam), correct countries, Industrial category, audited Tier-C S$ valuations matching p166 to the dollar, with JPY/VND alt_value cross-checks.
- **Multi-currency discipline**: SGD for audited statements; JPY/VND local per-row for property NPI/GR; closing FX (JPY122.00, VND20,447.50) captured (p6); average FX correctly noted as undisclosed.
- **Land tenure** freehold/leasehold enums + verbatim tenure_raw accurate, incl. the Okayama Hayashima 2 auto-renew footnote and Okayama Hayashima mixed freehold/sub-leasehold note.
- **trade_mix + top_tenants** scope footnotes captured correctly, incl. the unusual NPI (not GRI) basis for top tenants.
- **Sponsor relationship correct**: Daiwa House Industry Co., Ltd. (p6/p206) — REIT Manager is its wholly-owned subsidiary; no sponsor mislabel (unlike HMN).
- Unitholders 4,865, units 700,739,269, occupancy 87.8%, WALE 6.6y, leverage 40.2% all confirmed.

---

## 7. Could NOT verify

- **Per-property SGD-equivalent NPI/GR** — disclosed only in local currency (JPY/VND) per p27; the income statement uses *average* FX rates that are not disclosed per-property, so SGD per-property figures are not derivable from the parse without an FX assumption. The extraction correctly stores local-currency values and excludes them from the SGD gate. UNVERIFIABLE by design (not a defect).

---

## Fix list (file → field → correct value → page)

1. **performance.json → distribution_record** → replace the H2-2024 row (2.34c) with the H2-2025 row; correct record = [{period "1 January 2025 to 30 June 2025", dpu 2.24, pay_date 2025-09-26}, {period "1 July 2025 to 31 December 2025", dpu 2.09, pay_date 2026-03-26}] → sums to 4.33c = reported DPU. **p163 + p203 (2.09c announcement) + p56 (pay dates).** (MED)
2. **property_transactions.json → [0].consideration_sgd** → set to null (no SGD consideration disclosed; only JPY3,990m), or if kept, ≈32,700,000 at disclosed 122.00 AND add `_notes.inferred[]` flag. **p51 (JPY only); p6 (FX rate).** (MED)
3. **performance.json → portfolio_value** → align to audited 835,157,000 (or document the 835.2m headline choice in note). **p166.** (LOW)
4. **performance.json → note** → fix typo "paid Mar 2026" → "paid Mar 2025" for the 2.34c line (moot after fix #1). **p56.** (LOW)
5. **profile.json → management** → add property_manager "Daiwa House Vietnam Co., Ltd., Ho Chi Minh City Branch" (and optionally Property Trustee "Sumitomo Mitsui Trust Bank, Limited"). **p9.** (LOW)
