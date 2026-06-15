# C38U — CapitaLand Integrated Commercial Trust (C38U.SI) FY2025 — Forensic Extraction Audit

## 1. Method header

Independent verification against source. I navigated the report myself from the TOC — Financial Highlights (PAGE 5), Portfolio Valuation / Tier-A table + Financial Review by-property (PAGE 23–25), Trust Structure (PAGE 9/11), Top 10 Tenants + Trade Mix (PAGE 33–34), per-property cards (PAGE 35–60), audited Statement of Total Return (PAGE 106), Distribution Statement + DPU breakdown (PAGE 9 / 107), audited Portfolio Statement (PAGE 109–110), Notes 21–26 (PAGE 158–161), Statistics of Unitholdings (PAGE 193), Corporate Information (PAGE 198). I did **NOT** consult any extractor tooling, page-map, or anchor list.

Source: `parsed_reports_datalab/09_C38U.SI_CapitaLand-Integrated-Commercial-Trust_FY2025/full.md` (page-anchored `<!-- PAGE N -->`). Note: the parse covers PDF pages 1–199; markdown PAGE N = the report's printed page number. Markdown tables parsed cleanly; no PDF spot-check needed.

---

## 2. Verdict & confidence

**Grade: MINOR ISSUES.**

The hard numbers are excellent. Every audited financial-statement figure I re-derived matched the Group column to the dollar; the full Statement of Total Return reconciles exactly to "Total return for the year" (S$951,424k); the three-tier valuation trap (Gallileo/MAC/CapitaSky/Miller St at audited 100% $'000, ION Orchard correctly null as an equity-accounted JV) was navigated **correctly** — all 25 audited property valuations match the Portfolio Statement and sum to the stated total. trade_mix sums to 100%, top_tenants and DPU/distribution/unitholders all check out.

The defects are: (a) one **per-property revenue value on the wrong basis** (CapitaSpring 72.7 card-basis mixed into an otherwise Financial-Review-basis column); (b) several **false / over-broad null-justifications** in `_notes` (effective_date and lease_expiry_date declared structurally absent, but the per-property cards disclose the lease commencement dates; ION Orchard tenure declared absent but disclosed on its card); (c) **omitted property_manager roles** in profile (three are named in the Trust Structure); (d) a scattering of **unflagged inferences** (top-tenant trade_sector remaps; NLA-vs-GFA basis) and minor **provenance slips** (income_components below-NPI lines cite p113 not p106; ION card cited p39 not p43).

Tally: **CONFIRMED ≈ 40+** · **DISCREPANCY = 6** · **SUSPECTED-OMISSION = 4** · **UNVERIFIABLE = 1**

---

## 3. Discrepancies

### D1 — properties: CapitaSpring `gross_revenue` = 72,700,000 is the card basis, inconsistent with the rest of the column (MED)
- Extraction: CapitaSpring `gross_revenue` = 72,700,000.
- Source: **Financial Review by-property table (PAGE 25)** discloses CapitaSpring FY2025 gross revenue = **37.7** (S$ million; period 26 Aug–31 Dec 2025, the consolidated figure that ties into segment subtotals Retail 607.8 / Office 525.3 / ID 486.1 = group total 1,619.2). The **property card (PAGE 47)** separately shows **72.7**, but on a different basis — footnote 3: "includes revenue from the serviced residence up to its divestment on 30 May 2025" (i.e. full-year incl. the divested SR Component).
- Every OTHER property in the column was taken from the Financial Review table (37.7-basis). Mixing CapitaSpring's 72.7 in is internally inconsistent: it overstates the consolidated per-property revenue by ~35.0.
- Correct value for consistency: **37,700,000** (PAGE 25). If the card figure is preferred it must be flagged with its basis. Confidence: HIGH.

### D2 — properties: ION Orchard `gross_revenue` = 130,800,000 is on a 50% basis, unflagged (LOW–MED)
- Extraction: ION Orchard `gross_revenue` = 130,800,000, with no basis note (the row only carries `value_basis: "joint_venture_100pct"` on the null market_valuation).
- Source (PAGE 43): the card labels Gross Revenue **"(50% basis)"** = 130.8 — this is CICT's 50% share, whereas every other property's gross_revenue is 100%-basis. ION is an equity-accounted JV, so this revenue is NOT part of consolidated group revenue at all. Value is real but the basis (50% / equity-accounted) is unflagged. Confidence: HIGH.

### D3 — `_notes.columns_never_fillable`: `effective_date` declared structurally absent — FALSE (MED)
- `_notes` reason: "Land-lease start date not disclosed in the Portfolio Statement; only Remaining Term of Lease is given."
- Source: the per-property **cards** disclose lease commencement dates verbatim, e.g. Tampines Mall "Leasehold tenure of 99 years **with effect from 1 September 1992**" (PAGE 44), CapitaSpring "…**with effect from 1 February 1982**" (PAGE 47), ION Orchard "…**with effect from 13 March 2006**" (PAGE 43). Most SG assets carry these. The justification scopes the search to the Portfolio Statement only; the data exists in cards and `effective_date` (and therefore an as-disclosed `lease_expiry_date`) is fillable for most SG properties. Confidence: HIGH.

### D4 — `_notes.columns_never_fillable`: `lease_expiry_date` "computable but not as-disclosed" — partly FALSE (LOW–MED)
- Given the disclosed commencement date + 99-year term (D3), the expiry is a deterministic, as-disclosed derivation (e.g. Tampines 1 Sep 1992 + 99 = 31 Aug 2091), not an inference. The "not as-disclosed" framing understates what the cards provide. Confidence: MED.

### D5 — `_notes.data_with_no_home` "ION Orchard tenure details" / properties ION `land_tenure`=null — FALSE null-reason (MED)
- `_notes`: "Not in the audited Portfolio Statement so market_valuation and land_tenure are null."
- Source (PAGE 43): ION Orchard card discloses "Land Tenure: **Leasehold tenure of 99 years with effect from 13 March 2006**." `land_tenure` should be "Leasehold", `tenure_raw` the verbatim string, `lease_expiry_date` ≈ 2105-03-12. (market_valuation null is correct — equity-accounted JV absent from the Portfolio Statement.) Also ION `address` is null but the card states "2 Orchard Turn." Confidence: HIGH.

### D6 — income_components: below-NPI lines cite `source_page` 113; actual page is 106 (LOW)
- The Statement of Total Return is on **PAGE 106** (markdown); interest/investment income, management/professional/valuation/trustee/audit fees, finance costs, JV share, FV change, gain on divestment, taxation are all cited as p113. (Notes 23/24/25 sit on PAGE 158–159.) The revenue/opex lines correctly cite p159 (Notes 21/22). Provenance defect only — values are all correct. Confidence: HIGH.

---

## 4. Suspected omissions

### O1 — profile.management: three `property_manager` roles omitted (MED, schema home exists)
The Trust Structure (PAGE 11) names the property managers explicitly: **CapitaLand Retail Management Pte Ltd**, **CapitaLand Commercial Management Pte. Ltd.**, and **Orchard Turn Developments Pte. Ltd. (OTD)** (OTD manages ION Orchard). Note 28 (PAGE 161) confirms property management fees are payable to CapitaLand Retail Management and CapitaLand Commercial Management. The schema supports `role: "property_manager"`; all three are missing from profile.management.

### O2 — performance.number_of_properties not set; the report supports a value (LOW)
Not shipped. The portfolio is enumerable: 21 properties in the audited Portfolio Statement (20 active + 1 held-for-sale) plus ION Orchard (equity-accounted JV) = 22 properties under management (the Trust Structure lists 11 retail + 10 office + 5 ID with overlaps). A defensible count was available; left null.

### O3 — Per-property NPI genuinely segment-only — null is CORRECT (no omission)
Confirmed: NPI is disclosed only at segment level (Retail/Office/ID, PAGE 25–26 bar charts) and the audited statement gives a single group NPI (1,189,749k). `net_property_income` null per property is a TRUE structural absence. The `_notes` reason is correct here.

### O4 — value_basis / alt_value missing on the four consolidated-but-part-owned assets (LOW, audit-trail extras)
Gallileo (94.9%), Main Airport Center (94.9%), CapitaSky (70%), 101-103 Miller St (50%) are carried at the audited 100% $'000 (correct), but only ION Orchard carries a `value_basis`. The dual-basis audit-trail extras (`value_basis="consolidated"`, `alt_value`=Tier-A proportionate from PAGE 23) are absent on these four. Not schema-required, but the REFERENCE quirk note expects them.

---

## 5. Reconciliation results (independently re-computed)

### Statement of Total Return tie-out (Group, PAGE 106) — PASS
Using income_components:
- Σ(revenue) = 1,514,171 + 40,243 + 64,760 = **1,619,174k** ✓ (= performance.gross_revenue ✓; the HMN mis-bucketing bug does NOT occur — interest/investment income correctly tagged `adjustment`).
- Σ(expense lines, all) = property opex 429,425 + mgmt base 53,434 + perf 52,193 + professional 1,981 + valuation 587 + trustee 3,654 + audit 882 + finance 314,704 + other_trust 4,470 = **861,330k**.
- Σ(adjustments, signed) = interest 6,781 + investment 9,083 + JV share 116,753 + FV change 68,117 + gain on divestment JV 26 + taxation (−7,180) = **+193,580k**.
- **1,619,174 − 861,330 + 193,580 = 951,424k = "Total return for the year" (Group) ✓ exact.**
- No line missing. (Note: extraction maps "Gain on divestment of a joint venture" 26 correctly; FY2024-only "Gain on divestment of investment property" 32,765 correctly absent.)

### NPI — PASS (with rounding note)
1,619,174 − 429,425 = **1,189,749k** (audited, PAGE 106). performance.net_property_income ships **1,189,700,000** (the rounded headline 1,189.7m, PAGE 5). Off by 49k due to using the marketing-rounded figure rather than the audited $'000. LOW severity (consistent with how gross_revenue/DI were taken), but the audited 1,189,749,000 is the more precise value.

### Gross Revenue note (Note 21, PAGE 159) — PASS
1,514,171 + 40,243 + 64,760 = **1,619,174k** ✓.

### Property Operating Expenses (Note 22, PAGE 159) — PASS
141,300 + 65,525 + 51,429 + 32,231 + 35,018 + 94,768 + 584 + 513 + 326 + 7,731 = **429,425k** ✓ (all 10 lines match).

### Portfolio valuation sum (audited Portfolio Statement, PAGE 109) — PASS
Σ(24 valued investment-property rows) = **25,601,573k** ✓ = "Investment properties, at valuation" line. + Bukit Panjang Plaza (held for sale) 390,885k = **25,992,458k**, matching the `_notes` reconciliation. ION Orchard correctly excluded (equity-accounted JV, market_valuation null). Every individual valuation matches the Portfolio Statement to the dollar.

### Distribution / DPU — PASS
DPU 11.58c (PAGE 5/107) ✓. distribution_record tranches 5.62 (1 Jan–30 Jun) + 1.35 (1 Jul–13 Aug) + 4.61 (14 Aug–31 Dec) = **11.58c** ✓ — disclosed verbatim on PAGE 9 (the DPU breakdown table), periods match exactly. Distributable income 860.9m (PAGE 5) ✓ = net_distributable_income. (Note: the Distribution Statement PAGE 107 shows the first two tranches aggregated as "Cumulative Distribution of 6.97 cents 01/01–13/08"; 5.62+1.35 = 6.97, consistent.) ex_date/pay_date null — correctly not in the AR.

### Trade mix (PAGE 34) — PASS
18.7 + 17.8 + 8.0 + 7.6 + 5.0 + 4.1 + 4.0 + 22.0 + 12.8 = **100.0** ✓. Top-level 9 categories captured; the "Other Office Trades" (12.8) and "Other Retail Trades" (22.0) sub-tables correctly NOT double-counted. (Sub-totals check: Other Office 2.9+2.4+2.3+1.6+1.5+1.2+0.9 = 12.8 ✓; Other Retail 3.5+2.7+2.6+2.3+2.3+2.0+1.7+1.4+1.4+1.2+0.9 = 22.0 ✓.)

### Top 10 tenants (PAGE 33) — PASS
10 rows; % values match exactly; Σ = 16.0% (matches the disclosed total) ✓. Names match verbatim.

### Portfolio value headline — PASS
performance.portfolio_value 27,397,500,000 = the Portfolio Valuation grand total **27,397.5m** (PAGE 23), the proportionate-interest headline incl. JV stakes — exactly the intended "headline incl. proportionate JV." ✓ (Distinct from total assets 27,431.3m and audited investment properties 25,601.6m.)

---

## 6. Nulls / inference audit

**Confirmed genuinely absent (correct nulls):**
- `properties.net_property_income` — segment-only NPI; true structural absence (PAGE 25–26). ✓
- ION Orchard `market_valuation` — equity-accounted JV, absent from the audited Portfolio Statement. ✓
- Bugis+ and Bukit Panjang Plaza `gross_revenue` — aggregated as "Other Assets" (65.7) in the Financial Review (PAGE 25), no individual split disclosed. ✓ correct null + reason.
- distribution_record `ex_date`/`pay_date` — not in the AR (in separate distribution announcements). ✓

**Wrong / over-broad null-justifications:**
- `effective_date` "not disclosed" → **WRONG** (D3; commencement dates are on the cards).
- `lease_expiry_date` "not as-disclosed" → **partly WRONG** (D4; derivable from disclosed commencement + term).
- ION Orchard `land_tenure`/`tenure_raw`/`address` null → **WRONG** (D5; disclosed on the card PAGE 43).

**Inferences — reasonableness & unflagged ones:**
- top_tenants `trade_sector` were **remapped** from the source labels to canonical values without being flagged in `_notes.inferred[]`: RC Hotels "Hotel" → "Hospitality & Leisure"; KPMG "Business Consultancy" → "Professional Services"; GIC/Temasek/Mizuho "Financial Services" → "Banking, Insurance & Financial Services"; NTUC "Supermarket / Beauty & Health / F&B / Education / Warehouse" (multi-sector) → "Departmental Store/Supermarket". Reasonable remaps, but per invariant 7 each is an inference that should be flagged.
- trade_mix `pct_basis`="gri" — the chart footnote only says "Based on CICT's proportionate interests" (PAGE 34); the lease-expiry/top-tenant footnotes say "GRI… excludes GTO". `gri` is defensible; `gri_excl_gto` (top_tenants explicitly "excludes GTO", PAGE 33) would be more precise for top_tenants. Minor.
- `valuation_date` = 2025-12-31 uniform — correct (Portfolio Statement "As at 31 December 2025") but an assigned/uniform value.
- properties `gla`/`nla` are GFA(sq ft)/NLA(sq ft) from the cards; basis (GFA, not strictly "gla") is unflagged but consistent.

---

## 7. Confirmed-correct highlights (balance)

- **Three-tier valuation trap navigated correctly** — the single most error-prone area for CICT. All 24 active + 1 held-for-sale `market_valuation` figures match the **audited Portfolio Statement $'000** exactly (NOT the Tier-A marketing millions, NOT proportionate). Gallileo 547,629 / MAC 319,828 / CapitaSky 1,268,000 / Miller St 271,054 all at audited 100%; ION Orchard correctly null. Σ = 25,992,458k ties to the statement.
- **Full Statement of Total Return reconciles to 951,424k exactly** — no missing line, correct revenue/expense/adjustment bucketing (no HMN-style mis-bucket).
- **Notes 21 & 22 reconcile exactly** (1,619,174k revenue; 429,425k opex).
- **All per-property gross_revenue except CapitaSpring** match the Financial Review table (PAGE 25): Tampines 82.8, IMM 95.5, Raffles City 251.8, Gallileo 6.8, etc. — all verified.
- **GLA/NLA/occupancy/major_tenant** spot-checked against cards (Tampines GFA 507,300 / NLA 356,000 / occ 100 / Golden Village; ION GFA 945,400 / NLA 624,200 / occ ~98) — all correct.
- **Ownership %** correct: CapitaSky 70, Miller St 50, Gallileo/MAC 94.9, ION 50.
- **held_for_sale** Bukit Panjang Plaza correctly flagged (status, value 390,885k, divestment 90/91 strata lots S$428.0m completed 27 Feb 2026, PAGE 109/23).
- **CapitaSpring reclassification** (ID→Office after the 55% step-up) correctly handled.
- **portfolio_value, gross_revenue, DPU, distributable income, unitholders (91,421, PAGE 193, dated 27 Feb 2026 post year-end), management (Manager/Trustee), sub_sector (Diversified), income_model (conventional), sponsor (CLI, confirmed PAGE 175 "its Sponsor, CLI")** all correct.
- **FX rates captured** in `_notes` (EUR1=S$1.509, AUD1=S$0.848 closing) — matches PAGE 23–24 footnotes.

---

## 8. Could NOT verify

- **Per-property NPI in S$** — genuinely not disclosed at property level anywhere (segment-only). Null stands; unverifiable by design.
- **Individual gross_revenue for Bugis+ and Bukit Panjang Plaza** — aggregated as "Other Assets" 65.7 (PAGE 25); the cards do not split them. Null is correct; not derivable from the parse.

---

## Fix list (file → field → correct value → page)

| # | File | Field | Correct value | Page |
|---|---|---|---|---|
| D1 | properties.json | CapitaSpring `gross_revenue` | 37,700,000 (consolidated, PAGE-25 basis) — or flag the 72.7 card basis | 25 |
| D2 | properties.json | ION Orchard `gross_revenue` | 130,800,000 is **50%-basis / equity-accounted** — add basis flag (or null for consolidated consistency) | 43 |
| D3 | _notes.json + properties.json | `effective_date` (SG props) | disclosed on cards (e.g. Tampines "w.e.f. 1 Sep 1992") — remove "never fillable" reason, populate | 43–60 |
| D4 | _notes.json + properties.json | `lease_expiry_date` | derivable as-disclosed (commencement + term) | 43–60 |
| D5 | properties.json | ION Orchard `land_tenure`/`tenure_raw`/`address`/`lease_expiry_date` | Leasehold / "99 years w.e.f. 13 March 2006" / "2 Orchard Turn" / ≈2105-03-12 | 43 |
| D6 | income_components.json | below-NPI lines `source_page` | 106 (Statement of Total Return), not 113 | 106 |
| O1 | profile.json | management (add 3 `property_manager`) | CapitaLand Retail Management Pte Ltd; CapitaLand Commercial Management Pte. Ltd.; Orchard Turn Developments Pte. Ltd. (OTD) | 11 |
| O2 | performance.json | number_of_properties | 21 audited (20 active + 1 HFS) + ION JV = 22 (defensible) | 109 / 11 |
| (note) | performance.json | net_property_income | audited 1,189,749,000 (vs rounded 1,189,700,000) | 106 |
| (note) | top_tenants.json | trade_sector remaps | flag as inferred in `_notes.inferred[]` | 33 |
