# HMN — CapitaLand Ascott Trust (HMN.SI) FY2025 — Forensic Extraction Audit

Auditor: independent verification against source. Navigated the report myself (TOC, Statements of Total Return, Distribution Statement, Portfolio Statements pp.127-145, Note 22/23/24/25, Operations Review pp.28-60, Portfolio Highlights p10-11, Statistics p291-293, Corporate Information p296). Did NOT consult any extractor tooling/page-map.

Sources: `parsed_reports_datalab/06_HMN.SI_CapitaLand-Ascott-Trust_FY2025/full.md` (page-anchored). PDF spot-checks not required — markdown tables parsed cleanly.

---

## 1. Verdict & confidence

**Grade: MINOR ISSUES (bordering on MATERIAL on the null-justification front).**

The extraction is fundamentally sound on the hard numbers: every audited financial-statement figure I re-derived matched the Stapled Group column to the dollar, the full Statement of Total Return reconciles exactly to "Total return for the year" (S$332,623k), all 103 active + 2 divested properties are present with correct 2025 Stapled-Group valuations, and trade_mix / top_tenants / DPU / unitholders all check out. The issues are: (a) two **false / over-broad null justifications** — disclosed acquisition prices and disclosed per-property gross rental income were declared "not disclosed" when they plainly are; (b) an **internal contradiction** in `_notes.json` and `performance.json` over the portfolio_value number (7.9bn vs 7,637,513k vs the sponsor figure); (c) a **revenue-classification slip** in income_components that breaks the cross-section revenue tie-out.

Tally: **CONFIRMED ≈ 30+** · **DISCREPANCY = 4** · **SUSPECTED-OMISSION = 3** · **UNVERIFIABLE = 1**

---

## 2. Discrepancies

### D1 — income_components: `finance_income` & `other_income` mislabelled as `statement="revenue"` (MED)
- Extraction: `finance_income` 6,465k and `other_income` 1,581k are tagged `statement: "revenue"`.
- Source (p114 Statement of Total Return, Stapled Group): "Gross revenue" = 837,584k comprises ONLY the five Note-22 lines (gross rental, hospitality, hotel, deferred-income amort, car park). Finance income and Other income are separate lines *below* gross profit, not part of gross revenue.
- Consequence: Σ(income_components where statement=revenue) = **845,630k**, which does NOT equal `performance.gross_revenue` (837,584k). Difference = 8,046k = exactly finance_income + other_income. **Cross-section check E fails** because of this.
- Note: the full signed reconciliation still balances to total return (see §4), so it's a labelling defect, not a value error. Confidence: HIGH.

### D2 — `performance.portfolio_value` = 7,900,000,000 contradicts `_notes.json`'s own stated value (LOW–MED)
- `performance.json` ships **7,900,000,000**. This is defensible — p21 (line: "The Group's portfolio was revalued at **S$7.9 billion**") is a real disclosed headline.
- BUT `_notes.json` → `reconciliation.portfolio_value_note.performance_portfolio_value` = **7,637,513,000**, and `structural_notes` repeatedly describe "portfolio_value in performance.json (7,637,513,000)". The notes describe a number that is NOT what was shipped. This is an internal inconsistency that will confuse any downstream consumer.
- For the record, the audited Stapled-Group property totals (p143/p144): investment properties + IPUD + BT freehold L&B = **7,637,513k**; adding Robertson House leasehold L&B (337,950k) = **7,975,463k** (≈ S$8.0bn). The 7.9bn headline sits between. Confidence: HIGH that the inconsistency exists.

### D3 — property_transactions: 5 acquisitions have `consideration: null` but prices ARE disclosed (MED–HIGH)
- Extraction set `consideration: null` for all 5 FY2025 acquisitions and `_notes.inferred[]` justifies this as "Acquisition price not separately disclosed in the audited financials pages reviewed."
- Source **p11 "Investments Completed in FY 2025"** discloses:
  - ibis Styles Tokyo Ginza (+ Chisun Budget Kanazawa Ekimae, blended per footnote): **JPY21.0 billion (S$178.5 million)**, NOI yield 4.3%, Jan 2025.
  - Pre de Cort Nishikyogoku + Splendide Namba West + Pregio Esaka South: **JPY4.0 billion (S$34.2 million)** blended, 4.0%, Aug 2025.
- The justification is wrong: the extractor only looked at audited-FS pages and missed the Portfolio Highlights disclosure. At minimum the blended consideration + local-currency figures should have been captured. Confidence: HIGH.

### D4 — Tianjin divestment consideration: headline vs audited figure differ (LOW)
- Extraction: consideration 77,400,000 SGD / 420,000,000 CNY (from p10 headline "RMB420.0m / S$77.4m").
- Note 28 (p213/7820): "completed the divestment of Somerset Olympic Tower Tianjin … for a **consideration of $64.5 million**, which takes into account the **agreed property value of $75.5 million**." The audited consideration (S$64.5m) and agreed value (S$75.5m) differ from the S$77.4m sale-price headline. Not wrong (the S$77.4m = RMB420m sale price is genuinely disclosed) but the audited figures are not noted. Confidence: HIGH the discrepancy exists; LOW severity.

---

## 3. Suspected omissions

### O1 — Per-property Gross Rental Income / RevPAU disclosed throughout the Operations Review (the big one)
The `_notes.columns_never_fillable` declares `properties.gross_revenue` and `properties.net_property_income` as structurally absent ("not disclosed at property level"). **This is false for gross revenue.** The Operations Review (pp.~40-60) carries per-property **Gross Rental Income** and **RevPAU** tables for management-contract (and some master-lease) properties in EVERY major geography, in local currency:
- Australia (AUD'000) line 1640; Australia Hotel Revenue (AUD'000) 1668; Japan (JPY'000) 1850; Singapore (S$'000) 1994; China (RMB'000) 2272; Indonesia (IDR'm) 2372; Europe Hotel Revenue (EUR'000) 2419; France/Spain/etc (EUR'000) 2324/2592; South Korea (KRW'm) 2550; Vietnam (VND'm) 2633.
- Example (China, p43): Citadines Xinghai Suzhou 10,647 RMB'000; Wuhan 10,133; Dalian 33,524; Shenyang 24,975; Tianjin 9,392.
These are local-currency and scoped (mgmt-contract/some master-lease, not the whole portfolio), so they don't map cleanly to an SGD `gross_revenue` column — but the blanket "never disclosed at property level" reason is wrong and should be corrected. SEVERITY: MED (data exists but is awkward to normalise).

### O2 — Per-property unit/keys counts disclosed in prose and acquisition tables (LOW)
`columns_never_fillable`/`data_with_no_home` treat units as portfolio-level only (18,825). In fact per-property unit counts are disclosed: Operations Review prose ("140-unit Quest Sydney Olympic Park", "438-unit Pullman Brisbane", etc.) and the p11 acquisition table ("No. of Units": ibis Ginza 224, Chisun 392, Pre de Cort 85, Splendide 56, Pregio 48). The schema has no keys/units field (only gla/nla), so not capturable — but the "only portfolio-level" claim is inaccurate. SEVERITY: LOW (no schema home).

### O3 — Second portfolio breakdown table not captured: "Portfolio Information by Length of Stay" (LOW)
p27 has a per-year length-of-stay distribution table (FY2025: <1wk 67% / 1wk-1mo 9% / 1-6mo 5% / 6-12mo 12% / >12mo 7%). The extraction correctly *noted* this in `data_with_no_home` as orthogonal to the industry mix — acceptable handling, flagged here only for completeness. Also the contract-type income mix (stable 65% / growth 35%, p26; and p9: hospitality mgmt-contract gross profit S$134.9m, living S$54.7m) is noted but not captured. SEVERITY: LOW (correctly parked).

---

## 4. Reconciliation results (independently re-computed)

### Statement of Total Return tie-out (Stapled Group, p114) — PASS
Using income_components values:
- Σ(revenue lines incl. mis-bucketed finance/other income) = 845,630k
- Σ(expense lines) = 638,132k (of which the first 8 = Direct Expenses 452,283k ✓)
- Σ(adjustments, signed) = +39,688 +135,726 −7,257 −30,213 +99,038 −102 −111,755 = **+125,125k**
- **845,630 − 638,132 + 125,125 = 332,623k = "Total return for the year" (Stapled Group) ✓ exact.**
- Missing lines: "Share of results of associate" (Stapled 2025 = 0) and "Net change in FV of investment securities" (Stapled = 0; REIT-only −155). Both immaterial → income_components is **complete** for the Stapled Group.

### Gross revenue (Note 22, p213) — PASS
653,809 + 23,129 + 154,672 + 425 + 5,549 = **837,584k** = p114 gross revenue ✓ = performance.gross_revenue ✓.

### Direct expenses (Note 23, p213) — PASS
Σ8 lines = **452,283k** ✓. (Note: extraction's `other_direct_expenses` = 32,630 is the Stapled total; the REIT 21,309 + BT 32,709 don't sum to 32,630 — that's an oddity in the *source* table itself, not an extraction error; extraction correctly took the Stapled column figure.)

### Gross profit / NPI — PASS
837,584 − 452,283 = **385,301k** = performance.net_property_income ✓ (hospitality "gross profit" mapped to NPI — reasonable).

### Distribution — PASS
Income available for distribution (p116, Stapled) = **256,708k** = performance.net_distributable_income ✓. DPU 2.526 + 3.576 = **6.102c** (p20), rounds to 6.10c (p116) ✓. Pay dates 29 Aug 2025 / 27 Feb 2026 ✓.

### Portfolio valuation sum — PASS (with classification caveat)
Σ(properties.json market_valuation, 98 valued rows) = **7,202,419k**. Reconciles: p142 total investment properties incl BT IP (7,086,765k) − Right-of-use assets (222,296k, correctly excluded) = 6,864,469k individual IPs; + BT freehold aggregate 550,748k + Robertson 337,950k = **7,753,167k = 7,202,419 + 550,748** (the 5 null-valued BT freehold rows) ✓. The audited "Total investment properties, IPUD and freehold L&B" (p143) = 7,637,513k; incl. Robertson (p144) = 7,975,463k.

### Trade mix — PASS
21+17+13+11+6+6+6+6+5+5+4 = **100%** ✓. Scope footnote (p27): "Based on rental income from corporate accounts of properties under Ascott management contracts only" — present and quoted **verbatim** in pct_basis ✓.

### Top tenants — PASS
11 rows captured (table is headed "Top 10" but lists 11). Values match p27; Σ = 2.4% ✓. Names/sectors match.

### Stapled Group column discipline — PASS
Every financial figure traced to the **Stapled Group** column (gross revenue 837,584 not REIT-only 660,133; gross profit 385,301 not 337,884; finance costs 107,484 not 102,651; etc.). Portfolio values are the 2025 Stapled-Group column, not 2024, not REIT-only. ✓

---

## 5. Nulls / inference audit

**Confirmed genuinely absent (correct nulls):**
- `properties.occupancy_rate`, `gla`, `nla` — portfolio occupancy is only at portfolio level (80%, p25); Portfolio Statement (pp.127-143) has no per-property occupancy or area. ✓ (area metric for this sub-sector is units/keys, correctly not GLA.)
- 5 BT freehold properties' `market_valuation` (Pullman Brisbane/Melbourne/Sydney, Sydney Central, Temple Bar Dublin) — p143 genuinely discloses ONLY the aggregate 550,748k and per-property % of Stapled funds; individual $'000 not given. Correct null + correct reason. ✓
- 2 divested properties (Citadines Central Shinjuku Tokyo, Somerset Olympic Tower Tianjin) — correctly absent from year-end Portfolio Statement, status="divested", value null. ✓ (Shinjuku 2024 value 108,647k correctly noted.)

**Suspect / wrong null justifications:**
- `properties.gross_revenue` "never fillable — not disclosed at property level" → **WRONG** (see O1; disclosed per-property in local currency across the Operations Review).
- `property_transactions[...].consideration` "not disclosed" → **WRONG** for the 5 acquisitions (see D3; p11 discloses blended JPY/SGD prices).
- `performance.number_of_properties` left null with reason "report does not state a single total" → **arguably a miss**: the report states "**103 properties across 16 countries**" no fewer than four times (lines 85, 140, 1313, 2751). 103 = the active property count. A defensible value (103) was available.

**Inferences — reasonableness & unflagged ones:**
- `profile.sponsor`: `_notes.inferred` flags sponsor = "The Ascott Limited" (p16), but the **shipped profile.json lists sponsor = "CapitaLand Investment Limited"**. Internal inconsistency between the note and the file. CLI is the listed intermediate controlling shareholder (p291); The Ascott Limited is the operating sponsor. Either is arguable, but the two artefacts disagree.
- Lease expiry dates (e.g. Quest Sydney Olympic Park `lease_expiry_date` 2111-12-31 from "99 years, 86 remaining") are **derived/back-calculated** and only partly flagged. The source gives only "term / remaining term", never an explicit expiry date — every `lease_expiry_date` and most `lease_term_years` in properties.json are inferred. Only one such inference is flagged in `_notes.inferred`; the systematic derivation of ~50 expiry dates is an **unflagged inference pattern**. Values look internally consistent (2025 + remaining term), so low risk, but provenance is understated.
- `valuation_date` = 2025-12-31 uniform across all rows — correct (Portfolio Statement "As at 31 December 2025") but is an assigned/uniform value, not field-level disclosed per property.

---

## 6. Confirmed-correct highlights (balance)

- **All audited FS numbers exact** to the Stapled Group column: gross revenue, direct expenses, gross profit, every below-the-line item, tax, total return, distributable income, DPU.
- **Full Statement of Total Return reconciles to total return (332,623k) exactly** — no material line missing.
- **All 103 active + 2 divested properties present**, correct countries (16, matches headline), correct categories, correct 2025 Stapled-Group valuations (spot-checked ~15 across AU/CN/FR/JP/SG/UK/US/Vietnam/Korea — all match), Right-of-use assets correctly excluded from the per-property list.
- **BT structure handled correctly**: BT investment properties (Sotetsu Osaka-Namba, ibis Seoul, Sotetsu Seoul) captured with values from p142; Robertson House leasehold PPE captured at 337,950k (p144); BT freehold PPE correctly null. The three-classification trap was navigated correctly.
- **Stapled vs REIT-only vs BT-only** column discipline correct throughout.
- **trade_mix scope footnote and top-tenant scope** captured verbatim — exactly the kind of nuance usually lost.
- **Divestment dates** (Tianjin 15 Apr 2025, Shinjuku 2 Oct 2025) and **acquisition dates** (31 Jan, 27 Aug 2025) all independently confirmed against Note footnotes (pp.132/135) and Note 28 (p213).
- Unitholders 71,313 ✓ (p293); 18,825 units ✓ (p25); RevPAU S$161 ✓ (p8); portfolio occupancy 80% ✓ (p25).

---

## 7. Could NOT verify

- **Per-property NPI / gross profit in SGD**: genuinely not disclosed per property in SGD anywhere (only local-currency gross *rental* income / RevPAU, and portfolio-level gross profit S$385.3m). The null for `properties.net_property_income` stands; the null for `properties.gross_revenue` is wrong only in the *reason* given (local-currency per-property revenue does exist). The exact SGD-equivalent per-property revenue is not derivable from the parse without FX assumptions — left unverifiable.
- **Individual values of the 5 BT freehold hotels** — only the aggregate (550,748k) and per-property % of Stapled funds are disclosed; individual figures are genuinely not in the report. Null is correct and unverifiable by design.
