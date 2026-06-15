# BTOU — Manulife US REIT (BTOU.SI) FY2025 — Forensic Extraction Audit

## 1. Method header

Auditor: independent verification against source. I navigated the report myself from the Contents page (file line 51), reading whole sections: Financial & Portfolio Highlights (p8), Financial Review (pp22-24), Operational Review + Divestments + Trade Sector + Top 10 Tenants + Portfolio Valuation (pp25-27), the seven per-property cards with Gross Revenue / NPI bar charts (pp30-36), the audited Consolidated Statement of Comprehensive Income (p103), Distribution Statement (p104), Statement of Portfolio (p107), Gross Revenue / Property Operating Expenses / Other Trust Expenses / Finance / Tax notes (pp138-139), Interested Person Transactions (p92), Statistics of Unitholdings (pp93-94), trust-structure / sponsor prose (p8, p83/p89), and Corporate Information (p151).

I did **NOT** consult the extractor's page-map, anchor list, adapter plans, or any extraction reasoning. The two inputs read were the parsed markdown source of truth (`parsed_reports_datalab/26_BTOU.SI_Manulife-US-REIT_FY2025/full.md`, page-anchored) and the shipped `extracted/BTOU.SI_FY2025/*.json`. PDF spot-checks not required — markdown tables and the per-property cards parsed cleanly (Penn's bar charts came through as inline text, verified directly).

> Note on page numbers: the `<!-- PAGE N -->` anchors in the parse equal the report's printed page numbers (verified: the Statement of Comprehensive Income note ref "15/16" appears under PAGE 138 = "15 GROSS REVENUE"). All page cites below are these anchor/printed numbers.

---

## 2. Verdict & confidence

**Grade: MINOR ISSUES.**

This is a strong, careful extraction. Every audited financial-statement figure I re-derived matches the Group column to the dollar; the full Consolidated Statement of Comprehensive Income reconciles exactly to "Net loss for the year" (US$(87,653)k); all 7 active + 1 held-for-sale + 2 divested properties are present with correct p107 valuations, occupancies, tenures, and correct per-card NLA / GR / NPI / top-3 tenants; the Figueroa held-for-sale trap (audited US$85,703k, not marketing US$98.1m) and the distribution-halt trap (actual DPU = 0, DI/unit 1.44 stored with a note) were both navigated correctly; trade_mix, top_tenants, and unitholders all check out.

The defects are: (a) one **statement-mis-bucketing** bug — `interest_income` is tagged `statement="revenue"`, which breaks the Σrevenue = gross_revenue tie-out and contradicts the extractor's own `_notes` revenue check; (b) **systematic `source_page` imprecision** — all 10 property rows cite p107 for fields (NLA, gross_revenue, NPI, major_tenant, address) that are disclosed only on the per-property cards pp30-36, and profile.json cites p151 for a sponsor and property-manager that do not appear on p151; (c) a **judgment-call divergence** from the §1 invariant on `performance.portfolio_value` (audited Tier-C sum US$901.4m shipped vs the disclosed headline US$913.8m the invariant prefers) — defensible and well-noted, flagged for consistency.

Tally: **CONFIRMED ≈ 35** · **DISCREPANCY = 4** · **SUSPECTED-OMISSION = 2** · **UNVERIFIABLE = 1**

---

## 3. Discrepancies

### D1 — income_components: `interest_income` mislabelled as `statement="revenue"` (MED, HIGH confidence)
- Extraction: `interest_income` 1,385k is tagged `statement: "revenue"` (component `interest_income`, source_page 103).
- Source (p103 Consolidated Statement of Comprehensive Income; p138 Note 15): "Gross revenue" = 113,914k comprises ONLY the four Note-15 lines (rental 61,031 + recoveries 42,035 + car park 9,469 + others 1,379). **Interest income (1,385) sits BELOW "Net property income"**, between NPI and the manager's base fee — it is not part of gross revenue.
- Consequence: Σ(income_components where statement=revenue) = 61,031 + 42,035 + 9,469 + 1,379 + 1,385 = **115,299k**, which does NOT equal `performance.gross_revenue` (113,914k). The difference = exactly 1,385 = interest_income. **The cross-section revenue tie-out (REFERENCE §0.4 / the HMN check) FAILS.**
- This is the same bug class as HMN D1 (finance/other income mis-bucketed as revenue). The full signed P&L still reconciles to net loss (see §5), so it is a labelling defect, not a value error. `interest_income` should be re-tagged (e.g. `statement="adjustment"`, or a non-revenue income bucket) so Σrevenue = 113,914.
- **Internal contradiction reinforcing this:** `_notes.reconciliation.income_components_revenue_check` lists only the 4 Note-15 lines summing to 113,914 and `income_components_revenue_total = 113,914`. The note therefore describes a 4-line revenue set, but the shipped file has 5 `statement=revenue` rows (115,299). The note and the data disagree.

### D2 — Pervasive `source_page` imprecision on properties.json (LOW–MED, HIGH confidence)
- All 10 property rows carry `source_page: 107`. Page 107 (Statement of Portfolio) supports `market_valuation`, `occupancy_rate`, `land_tenure/tenure_raw`, and `status` — those are correct. But it does **NOT** contain `nla`, `gross_revenue`, `net_property_income`, `major_tenant`, or `address`; those come from the per-property cards: Centerpointe p30, Diablo p31, Exchange p32, Figueroa p33, Michelson p34, Penn p35, Phipps p36. The single p107 cite mis-attributes roughly half the fields on every row.
- Consequence: a downstream consumer chasing provenance for, e.g., Michelson NPI 13.6 or NLA 535,175 to p107 will not find it. Values are all correct; only the page anchor is wrong. Severity LOW–MED (provenance integrity).

### D3 — profile.json `source_page` 151 does not support sponsor or property_manager (LOW–MED, HIGH confidence)
- profile.json ships `sponsor = "The Manufacturers Life Insurance Company (Manulife)"` and `property_manager = "John Hancock Life Insurance Company (U.S.A) (JHUSA)"`, both with the object's `source_page = 151`.
- p151 (Corporate Information) names only the Manager, Board, Trustee (DBS), Auditor (E&Y), and Unit Registrar. It names **no sponsor and no property manager.**
- The two values are nonetheless CORRECT, sourced elsewhere: sponsor is stated verbatim on **p8** ("...wholly-owned by the Sponsor, The Manufacturers Life Insurance Company (Manulife)...") and confirmed in the Statistics note (4) **p94**; the property manager JHUSA is established on **p92** (Interested Person Transactions: "John Hancock Life Insurance Company (U.S.A) (JHUSA) ... Property management fee, leasing fees ... 5,799" under the Master Property Management Agreement). So the labels are right but the page anchor is wrong. Severity LOW–MED.

### D4 — performance.portfolio_value diverges from the §1 "headline" invariant (LOW, judgment call, HIGH confidence the divergence exists)
- Extraction ships **901,403,000** (audited Tier C: total investment properties 815,700k p107 + Asset held for sale - Figueroa 85,703k p107), with a clear note.
- REFERENCE §1 says `performance.portfolio_value` = the headline (incl. proportionate JV / marketing figure). The disclosed headline here is **US$913.8m** (p27 valuation table total; also p23 prose). The 913.8m differs from 901.4m solely because Figueroa is carried at its marketing valuation 98.1m in the headline vs its held-for-sale net consideration 85.703m in the audited statement.
- Not "wrong" — using the audited sum is internally consistent with the property rows (Σ market_valuation = 901,403k, see §4) and is arguably the better number. Flagged only because it departs from the stated convention and a reviewer should confirm which the schema wants. The note in performance.json explains the choice transparently. Severity LOW.

---

## 4. Suspected omissions

### O1 — `performance.number_of_properties` not present (LOW, schema home: yes)
- The schema's performance keys (REFERENCE §2) do not list `number_of_properties`, so strictly there is no home — but the report repeatedly states "**seven office buildings**" (p25, p27) for the standing portfolio. If a property-count field exists downstream, 7 (active) was available. Captured implicitly via 7 active property rows; flagged for completeness. Severity LOW.

### O2 — Per-property purchase price / acquisition date / WALE / tenant-count on the cards not captured (LOW, no clean schema home)
- Each card (pp30-36) discloses Acquisition Date, Purchase Price (e.g. Michelson US$317.8m / US$597 psf), WALE by NLA, and No. of Tenants. `property_transactions.json` captures only the two FY2025 divestments (correct — these are historical acquisitions, not FY2025 events). The schema has no per-property acquisition-price / WALE / tenant-count field, so these have no home. Correctly not forced. Severity LOW; noted for the record (could go in `_notes.data_with_no_home` but low value).

> Nothing material is missing. The big extraction risks for this report (held-for-sale dual valuation, distribution halt, bar-chart per-property NPI, sold-in-year partial-year P&L) were all handled.

---

## 5. Reconciliation results (independently re-computed)

### Consolidated Statement of Comprehensive Income tie-out (Group, p103) — PASS
Using income_components values (signed):
- Σ(statement=revenue) = 61,031 + 42,035 + 9,469 + 1,379 + 1,385 = 115,299k
- Σ(statement=expense) = 12,625 + 15,575 + 8,942 + 10,674 + 291 + 12,629 + 2,838 + 180 + 2,008 + 34,608 = 100,370k
- Σ(statement=adjustment, signed) = −11,666 − 83,515 − 3,323 − 4,078 = −102,582k
- **115,299 − 100,370 − 102,582 = −87,653k = "Net loss for the year attributable to Unitholders" (p103) ✓ exact.**
- income_components is **complete** down to net loss — no P&L line missing (interest income, all four FV/disposal/tax lines present).

### Cross-section revenue tie-out (REFERENCE §0.4) — FAIL (see D1)
- Σ(statement=revenue) = 115,299k ≠ `performance.gross_revenue` 113,914k. Gap = 1,385k = interest_income, mis-bucketed.

### Gross revenue note (Note 15, p138) — PASS
61,031 + 42,035 + 9,469 + 1,379 = **113,914k** = p103 gross revenue ✓ = performance.gross_revenue ✓.

### Property operating expenses note (Note 16, p138) — PASS
12,625 + 15,575 + 8,942 + 10,674 + 291 + 12,629 = **60,736k** ✓ = p103 property operating expenses.

### Net property income — PASS
113,914 − 60,736 = **53,178k** = performance.net_property_income ✓ = p103 NPI ✓ = p8 headline 53.2 ✓.

### Distribution / DPU — PASS (with the correct halt handling)
- Distribution Statement (p104): "Income available for distribution ... for the year" = **25,542k** = performance.net_distributable_income ✓ (= p22 DI, p8 headline 25.5).
- Actual "Distribution amount to Unitholders" = **–** and "Distribution per Unit (DPU)" = **–** (zero) on p104. Distributions halted since 2023 (p104 note 1, p23, p140). performance.dpu = 1.44 is the **DI per Unit** (p8 / p22: 25,542 ÷ 1,776,565k units in issue = 1.438 ≈ 1.44 US cents), correctly stored-as-disclosed with an explicit `dpu_note` that actual DPU = 0. `distribution_record = []` correct. ✓
- (Note: p22 footnote 1 confirms DI/Unit = DI ÷ total Units in issue. The 1,776,565k figure is the Distribution-Statement / Statistics units in issue, not the 1,835,124k "units issued and to be issued" used for NAV/EPU — extractor used the right denominator implicitly.)

### Property valuation sum → audited portfolio total — PASS
Σ(properties.json market_valuation, 8 valued rows) = Michelson 230,400 + Exchange 191,400 + Penn 79,800 + Phipps 192,500 + Centerpointe 76,700 + Diablo 44,900 + Figueroa(HFS) 85,703 = 901,403k. (Plaza, Peachtree null — divested.) 
- Reconciles to p107: Total investment properties 815,700k + Asset held for sale - Figueroa 85,703k = **901,403k** ✓ = performance.portfolio_value ✓.
- Headline (p27) = 913.8m (Figueroa at 98.1m marketing); difference fully explained (see D4).

### Per-property GR / NPI sum vs consolidated (sold-in-year gap) — PASS (explained)
- Σ(7 active cards GR) = 9.8 + 3.5 + 25.4 + 11.7 + 22.4 + 15.5 + 17.5 = **105.8m**; consolidated 113.914m. Gap 8.114m = partial-year revenue of Plaza (divested 25 Feb 2025) + Peachtree (divested 27 May 2025). ✓ matches `_notes`.
- Σ(7 active cards NPI) = 4.9 + 1.1 + 10.5 + 0.5 + 13.6 + 8.5 + 10.2 = **49.3m**; consolidated 53.178m; gap 3.878m = same-store NPI 49.3m (p22) + Plaza/Peachtree partial-year. ✓ matches `_notes` and the p22 same-store disclosure.

### Trade mix → 100% — PASS (with a mapping note)
18.3 + 15.3 + 9.6 + 8.9 + 7.7 + 6.5 + 5.9 + 5.4 + 4.4 + 17.9 = **99.9%** ✓ (rounding; matches the p26 donut exactly, 10 listed segments). `pct_basis = gri` ✓ (table titled "Trade Sector by GRI (%)"). `category_raw` verbatim ✓.
- Mapping judgment calls (all defensible, none wrong): "Finance and Insurance"→Banking/Insurance/Financial ✓; "Legal"→Professional Services ✓; "Public Administration"→Government Related ✓; "Information"→IT & Telecommunications ✓; "Transportation and Warehousing"→Logistics ✓; "Retail Trade"→Other Retail Trades ✓; "Real Estate"→Real Estate & Property Services ✓; "Administrative and Support Services", "Grant Giving", and "Other"→Other Office Trades (reasonable; "Grant Giving" = the United Nations Foundation tenant; no cleaner canonical home). The "2025 Leasing Trade Sector" donut (different basis) was correctly parked in `_notes.data_with_no_home`, not mixed in.

### Top 10 tenants → Σ / ranks — PASS
10 rows, ranks 1-10, names + % match p27 exactly; Σ = 8.4+7.4+5.9+5.4+5.3+4.5+4.3+3.6+3.3+3.3 = **51.4%** ✓ (matches the disclosed total). `pct_basis = gri` ✓, `trade_sector = null` correct (table has no sector column).

### Unitholders — PASS
performance.number_of_unitholders = **7,655** = p93 Distribution of Unitholdings TOTAL ✓; as at 16 March 2026 (p93) — correctly post-FY-end, noted.

---

## 6. Nulls / inference audit

**Confirmed genuinely absent (correct nulls + correct reasons):**
- `property.gla` (all rows) — cards disclose **NLA** only ("NLA 422,138 SQ FT" etc.); no GLA anywhere. Correct null + correct `columns_never_fillable` reason. ✓
- `property.lease_term_years / effective_date / lease_expiry_date` (all rows) — all US properties are **Freehold (fee simple)**; no land-lease term exists. Statement of Portfolio "Tenure of Land" = "Freehold" on every row (p107), cards confirm. Correct nulls; the `_notes` reason is accurate. ✓ (Note: tenant-lease WALE exists at portfolio/property level but that is not a land-lease term and has no schema field.)
- `property.trade_mix` (per-property) — only portfolio-level trade mix disclosed (p26). Correct. ✓
- `top_tenant.trade_sector` — p27 table genuinely has no sector column. Correct null (NOT inferred from tenant names — good, that would have needed an `inferred[]` flag). ✓
- `performance.distribution_record = []` — correct; DPU = – (zero), distributions halted (p104). ✓
- Plaza & Peachtree `market_valuation/npi/gross_revenue/occupancy = null`, `status="divested"` — correctly absent from the FY2025 Statement of Portfolio (p107 shows them only in the FY2024 column / as prior held-for-sale). ✓

**Land_tenure = Freehold:** correct and disclosed (p107 column + cards) — NOT an inference. Good.

**Inferences — reasonableness & flagging:**
- `valuation_date = 2025-12-31` uniform on all rows — assigned from the Statement of Portfolio header "As at 31 December 2025" (p107). An assigned/uniform value rather than per-row disclosed, but correct; minor — would ideally be flagged.
- Figueroa `status="held_for_sale"` and value 85,703 — correctly derived from p107 "Asset held for sale - Figueroa 85,703" + p107 footnote 3 (proposed divestment announced 30 Mar 2026, reclassified at estimated net sale consideration). Well-documented in `_notes.parsing_traps`. ✓
- No back-calculated/derived values are passed off as disclosed (unlike the HMN lease-expiry pattern). Clean on this front.

**Wrong/imprecise provenance (not a value or null error, but a defect):** see D2 (property rows over-cite p107) and D3 (profile over-cites p151). These are the BTOU analogue of the HMN false-page issues — the data is right, the page is not.

---

## 7. Confirmed-correct highlights (balance)

- **All audited FS numbers exact** to the Group column: gross revenue 113,914, property opex 60,736, NPI 53,178, every below-NPI line, all four adjustment lines, net loss (87,653), DI 25,542.
- **Full Statement of Comprehensive Income reconciles to net loss (−87,653k) exactly** — no line missing or mis-signed.
- **Held-for-sale trap handled correctly**: Figueroa at the audited net-consideration US$85,703k (not the US$98.1m marketing headline), status `held_for_sale`, with the dual-value captured in `alt_value`/`alt_basis` and the trap documented.
- **Distribution-halt trap handled correctly**: actual DPU = 0 recognised; 1.44 stored as DI/Unit with an explicit note; empty distribution_record.
- **Sold-in-year P&L gap reconciled**: the 8.1m GR / 3.9m NPI gap between the 7 cards and the consolidated total is correctly attributed to Plaza/Peachtree partial-year contribution (matches p22 same-store US$49.3m NPI).
- **All 7 per-property cards correct**: NLA, 2025 GR, 2025 NPI (incl. Penn's inline-text bar chart 15.5 / 8.5), occupancy, valuation, top-3 tenant shares, tenure — every spot-checked value matches pp30-36 / p107.
- **trade_mix (99.9%, p26), top_tenants (Σ51.4%, p27), unitholders (7,655, p93)** all tie out; pct_basis correct; verbatim category_raw.
- **Profile values correct** (Manager, Trustee DBS, Sponsor Manufacturers Life, Property Manager JHUSA, income_model conventional, sub_sector Office) — only the page citation is off (D3).
- **property_transactions**: both FY2025 divestments correct — Plaza (25 Feb 2025, net 40m, val 43.7m, buyer 500 Plaza Ground Lessor LLC) and Peachtree (27 May 2025, net 121m, val 133.4m, buyer SSC VII INVESTOR LLC), all matching p25.

---

## 8. Could NOT verify

- **Exact SGD equivalents** — n/a; this trust reports throughout in **USD** (confirmed p103/p107/p138 all "US$'000"), so there is no FX translation to verify. `currency = "USD"` correct on every record.
- **Penn 2025 GR/NPI precision** — disclosed as inline text "15.9 15.5 15.5" (GR) and "8.9 8.6 8.5" (NPI) on p35 rather than a parsed table; 2025 = 15.5 / 8.5 read directly and consistent with the bar-chart caption. Cannot cross-check against a second source (no per-property table in the audited FS), but internally consistent and matches the inline values. Low risk.
- **Peachtree net consideration 121 vs 123.6** — the p25 Divestments table states net consideration **121** (used); the p25 prose and p8-area narrative say Peachtree was sold for "US$123.6 million in net proceeds". The two figures differ in the source itself (likely gross-of/net-of certain closing adjustments); the extraction took the table figure (121), which is defensible. Genuinely ambiguous in the report — left as-is, flagged.
