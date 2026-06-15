# UD1U — IREIT Global (UD1U.SI) FY2025 — Forensic Extraction Audit

## 1. Method header

Independent verification against source. I navigated the report myself from the CONTENTS page (p3): Financial Review / Statement of Total Returns (printed p22), Trust & Manager Structure (p17), Portfolio Summary & Overview / per-property cards + tenant/trade-sector tables (pp.36–86), and the audited Financial Statements — Consolidated Statement of Total Return (p175), Statement of Distribution (p176), Statement of Portfolio (pp.179–181), Note 2.3 Investment Properties (p188), Note 3.1 Operating Segments (p193), Notes 3.2/3.3 Gross Revenue & Property Operating Expenses (p196), related-party / property-manager note (p214 area), and Statistics of Unitholdings (p223). The `<!-- PAGE N -->` markers correspond to the report's printed page numbers, which is the citation scheme the extraction used.

I did NOT consult any extractor tooling, page-map, anchor list, or reasoning. Source: `parsed_reports_datalab/20_UD1U.SI_IREIT-Global_FY2025/full.md`. Reporting currency EUR throughout; the trust is 100%-owned across Germany/Spain/France (no JV / proportionate-stake trap present).

---

## 2. Verdict & confidence

**Grade: MINOR ISSUES.**

This is a clean, careful extraction. Every audited financial-statement figure I re-derived matches to the euro: gross revenue 50,434k, property opex 17,610k, NPI 32,824k, the full Statement of Total Return down to total loss (63,200k), distributable income 14,662k, DPU 1.09c, unitholders 6,494. All 53 properties are present with correct Tier-C carrying values, tenure, leasehold remaining terms, occupancy and per-property GRI traced to the property cards. income_components is bucketed correctly (the recurring HMN finance-income-as-revenue bug is NOT present here — Σrevenue ties exactly to gross_revenue). The extractor even correctly detected and quarantined a genuinely corrupted source chart (the p41 GRI-by-property donut).

The defects are: (a) a **named property manager (Sofidy SAS) omitted** from profile.management; (b) a **cross-file inconsistency** between `performance.portfolio_value` (798,100k = independent valuation, rounded) and Σ(`properties.market_valuation`) (804,280k = audited carrying value incl. ROU) — both defensible individually but they don't tie, and the shipped number is the rounded marketing figure rather than the precise Note-2.3 value; (c) a couple of soft trade-sector / canonical-mapping judgment calls.

Tally: **CONFIRMED ≈ 35+** · **DISCREPANCY = 4** (1 MED, 3 LOW) · **SUSPECTED-OMISSION = 2** · **UNVERIFIABLE = 1**

---

## 3. Discrepancies

### D1 — profile.management omits the named Property Manager "Sofidy SAS" (MED)
- Extraction lists reit_manager, trustee, and two sponsors — but **no `property_manager`**, despite the schema role existing and the Trust Structure diagram (p17, line ~803/818) showing a "PROPERTY MANAGERS" box ("2 Property managers have been appointed pursuant to the property management agreements").
- The related-party transactions note (p214, line 8520) names the property manager explicitly: **"Sofidy SAS as Property Manager"** (Property Manager fees €157k). Note 3.3 (p196) additionally notes "Electro's property manager, which is a wholly-owned subsidiary of Tikehau Capital."
- Consequence: a disclosed management role with a named company is missing. Fix: add `{"role": "property_manager", "company_name": "Sofidy SAS"}` (p214). Confidence: HIGH.

### D2 — performance.portfolio_value (798,100k) does not tie to Σ(properties.market_valuation) (804,280k); uses rounded marketing figure (LOW–MED)
- `performance.portfolio_value` = **798,100,000**, sourced from the p6/p40 marketing highlight (€798.1m). Σ(`properties.market_valuation`) across all 53 rows = **804,280,000** (the audited Statement-of-Portfolio carrying value incl. €6,140k France right-of-use assets, p181/p188).
- Note 2.3 (p188) gives both precisely: **independent valuation 798,140k** vs **carrying amount 804,280k**. So the two artifacts straddle a 6,140k (ROU) gap, and the shipped value is the rounded €798.1m rather than the exact 798,140k.
- This is the HMN-class cross-file inconsistency (portfolio_value-in-performance vs the property-table sum). It is *explainable and documented* in `_notes`, so it is LOW–MED, not MATERIAL — but a downstream consumer reconciling performance against the property table will see a 6.14m discrepancy. The cleanest fix is to make portfolio_value = the audited carrying value **804,280,000** (matches the property-table sum and §0 invariant 2 "valuation source = audited Portfolio Statement"), OR at minimum use the precise independent-valuation **798,140,000** and state the ROU reconciliation. Confidence: HIGH that the inconsistency exists; the "right" number is a documented judgment call (see §8).

### D3 — trade_mix "Real Estate" → "Other Office Trades" mapping is a stretch (LOW)
- The report's Trade Sectors table (p39) row "Real Estate" 4.3% was mapped to canonical **Other Office Trades**. Real Estate is neither an office sub-trade nor a clean fit for any of the 19 canonical values; `category_raw` is preserved verbatim, so this is recoverable, but the canonical bucket is arguable. Acceptable; flagged for the reviewer. Confidence: HIGH the mapping is debatable; LOW severity.

### D4 — top_tenants trade_sector values are all inferred from tenant names (LOW)
- The p39 Top-10 table has **no trade-sector column**; all 10 `trade_sector` values are assigned from company names / the separate Trade-Sectors table. This is correctly and fully disclosed in `_notes.inferred[]` (scope "all 10 rows"), so it is a properly-flagged inference, not a hidden one. A couple are soft (Westfälisch-Lippische → Government Related; OXYGEN DATA CENTER → IT & Telecommunications) but reasonable. No fix required; noted for transparency. Confidence: HIGH.

---

## 4. Suspected omissions

### O1 — Property Manager identity (see D1) (MED, schema home EXISTS)
Sofidy SAS (and the Tikehau-owned manager for Electro) are disclosed property managers with a clear schema home (`profile.management` role `property_manager`). Currently omitted. This is the single most material omission.

### O2 — Per-property GLA for ~all French (Decathlon/B&M) and the two Delta Nova rows (LOW, schema home exists but data is portfolio-level)
`properties.gla` is null for the 44 French properties and the two Delta Nova offices. `_notes.columns_never_fillable` concedes individual French GLA "not read from per-property cards … not fully extracted." The portfolio cards disclose only segment totals (Decathlon 95,500 sqm; B&M 61,756 sqm; Delta Nova IV+VI combined 25,112 sqm) — per-property French GLA is genuinely not in the Statement of Portfolio, and per-property French cards (if any) were not fully extracted. This is an under-capture acknowledgement rather than a false absence; severity LOW. The German/Spanish per-property GLA WAS correctly captured from the cards.

---

## 5. Reconciliation results (independently re-computed)

### Statement of Total Return tie-out (Group, p175) — PASS
Σ(revenue) = 39,119 + 8,412 + 2,626 + 277 = **50,434k** = gross revenue ✓
Σ(property opex) = 949 + 8,207 + 3,434 + 3,231 + 1,789 = **17,610k** ✓
NPI = 50,434 − 17,610 = **32,824k** ✓
Below NPI: +532 (fin inc) −8,197 (fin cost) −1,810 (mgmt base) +0 (perf) −196 (trustee) −1,706 (admin) −2,227 (other trust) +2,290 (FX) +0 (divest) −8,542 (FV deriv) −81,970 (FV inv prop) +5,802 (tax)
32,824 + (−63,200 vs 32,824)… computed: 32,824 +532 −8,197 −1,810 −196 −1,706 −2,227 +2,290 −8,542 −81,970 +5,802 = **−63,200k** = "Total loss for the year attributable to Unitholders" ✓ exact.

### income_components revenue tie-out (the HMN check) — PASS
Σ(income_components where statement="revenue") = 39,119 + 8,412 + 2,626 + 277 = **50,434k** = `performance.gross_revenue` ✓. Finance income, FX gain etc. are correctly tagged `statement="adjustment"`, NOT "revenue". **The HMN bug is absent.**

### Gross Revenue note (3.2, p196) — PASS
39,119 + 8,412 + 2,626 + 277 = **50,434k** ✓ (matches p175 line and the segment-note total).

### Property Operating Expenses note (3.3, p196) — PASS
949 + 8,207 + 3,434 + 3,231 + 1,789 = **17,610k** ✓.

### Segment cross-check (Note 3.1, p193) — PASS
Segment gross revenue 21,351 + 9,685 + 19,398 = 50,434 ✓; segment NPI 10,753 + 5,816 + 16,255 = 32,824 ✓. Confirms the `_notes` segment-NPI figures and the "per-property NPI structurally absent" reason.

### Portfolio valuation sum (Statement of Portfolio, pp.179–181) — PASS (to the carrying-value total)
Germany rows 195,800 + 110,200 + 51,800 + 53,800 + 58,700 = **470,300k** ✓ (= Germany–Total).
Spain rows 23,300 + 34,600 + 44,600 + 24,600 = **127,100k** ✓ (= Spain–Total).
France rows sum to **206,880k** ✓ (= France–Total, incl. 6,140k ROU).
Grand total = **804,280k** = "Investment properties incl. ROU (Note 2.3)" ✓.
Note 2.3 independent valuation = 798,140k; carrying = 804,280k. The property table sums to the **carrying** total — but `performance.portfolio_value` = 798,100k (see D2).

### Distribution (Statement of Distribution, p176) — PASS
DPU 0.71 + 0.38 = **1.09c** ✓; period distributions 9,549 + 5,113 = **14,662k** = Total Unitholders' distribution = `net_distributable_income` ✓. (Report also shows "Amount available for distribution" 16,291k — the extraction chose the actual distribution 14,662k, consistent with the p22 "Distribution to Unitholders" line and the €14.7m narrative.)

### Trade mix → 100% (p39) — PASS
38.3 + 17.7 + 16.9 + 6.6 + 4.9 + 4.3 + 11.3 = **100.0%** ✓. All 7 disclosed rows captured; pct_basis footnote "As a percentage of total gross rental income" present.

### Top-10 tenants (p39) — PASS
All 10 names + percentages match verbatim (Decathlon 20.8 … OXYGEN 2.2). Σ = 77.3% (report states no explicit total). ✓

### Property count — PASS
5 Germany + 4 Spain + 27 Decathlon + 17 B&M = **53** properties; JSON has 53 rows. Matches p4 ("five … four … 44") and the Statement of Portfolio. ✓

---

## 6. Nulls / inference audit

**Correct nulls confirmed:**
- `properties.net_property_income` (all rows) — only segment-level NPI disclosed (Germany 10,753 / Spain 5,816 / France 16,255, p193). Per-property NPI genuinely absent. Reason in `_notes` is CORRECT. ✓
- `properties.nla` — report uses "Total Lettable Area"/GLA basis; no separate NLA. Correct. ✓
- `performance.distribution_record.ex_date / pay_date` — the Statement of Distribution (p176) gives periods + per-period DPU but no ex/pay dates anywhere in the parsed text. Confirmed absent. ✓
- French per-property GLA — genuinely portfolio-level only (see O2). ✓

**Inferences — all properly flagged:**
- occupancy_rate = 100% applied per-property to 27 Decathlon + 17 B&M from the portfolio-summary "100% occupancy" figures (pp.63/79) — flagged in `_notes.inferred[]` with scope and source page. ✓ Correct discipline.
- top_tenants.trade_sector (all 10) — flagged. ✓
- portfolio_value 798,100k — flagged with full reconciliation. ✓ (the value choice is the D2 issue, but the inference IS flagged.)
- Leasehold `lease_expiry_date` for the 4 French leasehold rows (Noyelles-Godault 2034-06-01, Maizières 2042-12-01, Fayet 2052-01-01, Blois 2055-11-01) are **derived** by adding the disclosed remaining term (8.5 / 17.0 / 26.1 / 29.9 yrs as at 31 Dec 2025) to year-end — the report discloses only the remaining term, not an explicit date. Each property `note` says "computed from remaining term … (approximate; exact date not disclosed)" — so the derivation IS disclosed at the row level, though it is not also collected in `_notes.inferred[]`. Minor provenance nit (cite at row level is acceptable). Remaining terms themselves match the Statement of Portfolio exactly. ✓

**No unflagged inferences of concern found.** (Contrast HMN, where ~50 expiry dates were back-calculated without flags.)

---

## 7. Confirmed-correct highlights (balance)

- **All audited FS numbers exact**: gross revenue, opex, NPI, every below-NPI line, tax, total loss, distribution, DPU, NAV, units — all traced to the audited Group column (pp.175–176, 196).
- **income_components bucketing is correct** — revenue lines = the four Note-3.2 lines only; everything below NPI tagged "adjustment". Σrevenue ties to gross_revenue to the euro.
- **All 53 properties present** with correct country, category, address, 100% ownership, Tier-C carrying value, valuation_date 2025-12-31, tenure (49 Freehold / 4 Leasehold) and leasehold remaining terms — all matching the Statement of Portfolio (pp.179–181).
- **Per-property GRI and occupancy** correctly pulled from the property cards (spot-checked Bonn €6.9m/100%, Darmstadt €1.9m/41.3%, Berlin €0.1m/0%) — these match the cards, not the corrupted p41 chart.
- **Excellent trap handling**: the extractor detected that the p41 "GRI by Property" 2025 donut is internally impossible (divested Il·lumina shown at 3.9%; Berlin at 0% occupancy implied high GRI; Darmstadt 0.1% contradicts its 4.6% card figure) and correctly used the property-card absolutes instead, documenting it in both `parsing_traps` and `data_with_no_home`. This is exactly the §0-invariant-8 discipline (a wrong chart is a signal, not a number to copy).
- **Three-tier valuation navigated correctly**: used the audited Statement of Portfolio (Tier C, EUR'000 ×1000), not the p40 € millions marketing bars; ROU inclusion is documented; Concor Park's €80.9m→€58.7m fair-value fall captured with alt_value.
- **profile** roles (reit_manager IREIT Global Group Pte. Ltd., trustee DBS Trustee Limited, sponsors Tikehau Capital + City Developments Limited) all correct and correctly labelled (p4/p5/p17). income_model "conventional" is right (straight CPI-indexed leases, no master-lease/MCMGI). sub_sector "Diversified" is correct (5+4 offices in DE/ES + 44 retail in FR — two physical classes co-dominate).
- **currency EUR**, **date 2025-12-31**, **unitholders 6,494 (as at 12 Mar 2026, p223)** all correct.

---

## 8. Could NOT verify

- **The single "correct" portfolio_value** is a documented judgment call, not a derivable fact: the report headlines €798.1m (marketing), discloses 798,140k (independent valuation) and 804,280k (audited carrying incl. ROU) in Note 2.3. Any of the three is defensible; I flag only that the shipped figure (798,100k) does not tie to the property-table sum (804,280k) and uses the rounded form. Resolving which the schema *wants* is a convention decision for the user, not an arithmetic one.
- **Exact per-property GLA for the 44 French assets and the per-property Delta Nova split** — genuinely not disclosed per property (only portfolio/combined totals). Not derivable from the parse.
- **Per-property NPI in EUR** — only segment-level disclosed; not derivable.

---

## Fix list (file → field → correct value → page)

1. `profile.json` → `management[]` → ADD `{"role": "property_manager", "company_name": "Sofidy SAS"}` → p214 (related-party note "Sofidy SAS as Property Manager"; also Trust Structure diagram p17). **[MED]**
2. `performance.json` → `portfolio_value` → resolve the cross-file tie: set to **804,280,000** (audited carrying value, matches Σ properties.market_valuation and §0 invariant 2) OR keep an independent-valuation basis but use the precise **798,140,000** and reconcile the 6,140k ROU in `_notes` → Note 2.3, p188 / Statement of Portfolio, p181. **[LOW–MED, judgment]**
3. `trade_mix.json` → row "Real Estate" → reconsider canonical mapping (currently "Other Office Trades"; consider leaving uncategorised/other rather than office) → p39. **[LOW, optional]**
4. (Optional provenance) `_notes.json` → `inferred[]` → add the 4 derived French leasehold `lease_expiry_date` values as an explicit inferred entry (already row-noted) → pp.180–181. **[LOW]**

No financial values require correction — every reconciliation passes to the euro.
