# HMN.SI — CapitaLand Ascott Trust (CLAS) — FY2025 property-transaction audit

**FY-END:** 2025-12-31 (window 1 Jan–31 Dec 2025). **Rows:** 7 (5 acquisition + 2 divestment). **Verdict: 6 rows verified correct; 1 correction — Citadines `carrying_value` is a DERIVED figure (invariant breach) and must be nulled/relabelled.**

Sources: Portfolio Highlights divestment table **p10**, Investments Completed table **p11**, Portfolio Listing "Agreed Property Value at Acquisition" **p56–57**, Portfolio Statements + footnotes (2)–(5) **p132/135/136**, Note 4 Investment Properties **p171**, Note 14 Assets held for sale **p196**, Note 28 Profit From Divestments **p216–217**, Distribution Statement **p116**.

## Per-column null/value status

### Divestments (2)
| property | date | gross (consid.) | valuation | net_proceeds | carrying | gain | counterparty |
|-|-|-|-|-|-|-|-|
| Somerset Olympic Tower Tianjin (China) | 2025-04-15 | S$77.4m / RMB420.0m (p10) | S$75.5m agreed property value (p216) | S$64.5m (p216) | S$51,316k (Note 14, p196) | S$17,027k (Note 28, p217) | Tianjin Yuchuang Consulting Co. Ltd (Note 14 (a), p196) |
| Citadines Central Shinjuku Tokyo (Japan) | 2025-10-02 | S$222.7m / JPY25.0bn (p10) | S$108,647k 31-Dec-2024 val. (p132 fn3) | S$210.3m (p217) | **128,289k — DERIVED ✗** | S$82,011k (Note 28, p217) | ML Estate Co., Ltd (p132 fn3) |

- **gross_sale_price / consideration** — both match the p10 "Divestments Completed in FY 2025" headline deal values (Somerset RMB420.0m/S$77.4m; Citadines JPY25.0bn/S$222.7m). ✓
- **net_proceeds** — Note 28 prints both: Somerset "consideration of **$64.5 million**, which takes into account the agreed property value of $75.5 million" (p216, line 7820); Citadines "consideration of **$210.3 million**" (p217, line 7832). Distinct from the p10 headline. ✓ (Somerset's is explicitly the net subsidiary-sale consideration; Citadines is labelled only "consideration" — a reasonable net read vs the JPY25.0bn/S$222.7m headline.)
- **valuation** — Somerset "agreed property value of $75.5 million" (p216); Citadines 31-Dec-2024 Portfolio-Statement "At Valuation" **108,647** (p132, line 5054), which fn(3) confirms is the valuation the sale price was "100% above". Genuine, distinct from sale price and carrying. ✓
- **carrying_value** —
  - Somerset **51,316k**: source-printed on Note 14 held-for-sale, "Somerset Olympic Tower Tianjin – Investment property **51,316**" (2024 col, p196, line 7059; disposal-group total 66,531). Genuine, NOT derived. ✓
  - Citadines **128,289k**: **DERIVED = net_proceeds 210,300 − gain 82,011** (the JSON `carrying_value_basis` says so verbatim: "DERIVED … no standalone per-property carrying line disclosed"). **This breaches the "never balance one figure from another" invariant and matches NO printed figure.** The only printed carrying-of-disposed-IP is the aggregate Note 4 "Investment properties disposed **(109,494)**" (Stapled Group 2025, p171, line 6270) — and Citadines is the **sole FY2025 investment-property divestment** (Note 28 lists only it under "Divestment of investment properties", p217). **→ correction below.**
- **gain_on_divestment** — Note 28 "Profit from divestments" table (p217, lines 7838–7840): "Gain/(loss) on divestment of assets held for sale **17,027**" (= Somerset, sole 2025 held-for-sale divestment) + "Gain on disposal of investment properties **82,011**" (= Citadines) = **99,038**, tying to the Statement of Total Return (p116, line 4555). Both source-printed. ✓
- **counterparty** — Somerset: Tianjin Yuchuang Consulting Co. Ltd (Note 14(a) p196, SPA dated 22 Oct 2024). Citadines: ML Estate Co., Ltd (p132 fn3 — an unrelated third party warehousing for CapitaLand Japan KK, a related party). ✓

### Acquisitions (5)
| property | date | consideration | valuation (agreed value) | counterparty |
|-|-|-|-|-|
| ibis Styles Tokyo Ginza | 2025-01-31 | JPY21.0bn / S$178.5m **(blended w/ Chisun)** (p11) | S$136.0m (p56) | GKK Godo Kaisha (p132 fn4) |
| Chisun Budget Kanazawa Ekimae | 2025-01-31 | **NULL — not separately priced** | S$42.5m (p56) | GKK Godo Kaisha (p132 fn2) |
| Pre de Cort Nishikyogoku | 2025-08-27 | JPY4.0bn / S$34.2m **(blended w/ Splendide + Pregio)** (p11) | S$13.7m (p57) | HSJPN2 TMK (p135 fn5) |
| Splendide Namba West | 2025-08-27 | **NULL — not separately priced** | S$10.6m (p57) | HSJPN2 TMK (p136 fn5) |
| Pregio Esaka South | 2025-08-27 | **NULL — not separately priced** | S$9.9m (p57) | HSJPN2 TMK (p135 fn5) |

- **purchase_price NULLs (Chisun, Splendide, Pregio) — RE-CONFIRMED genuinely absent.** The p11 "Investments Completed in FY 2025" table (lines 502–506) prints a price ONLY on the lead row of each blended group: row 1 ibis Styles = "JPY21.0 billion (S$178.5 million)" covering rows 1–2; row 3 Pre de Cort = "JPY4.0 billion (S$34.2 million)" covering rows 3–5. **Rows 2 (Chisun), 4 (Splendide), 5 (Pregio) have blank Purchase Price / NOI Yield / Acquisition Date cells** (merged with the lead). No per-property split exists elsewhere (Portfolio Statement p132/135/136 shows only "At Valuation"; Portfolio Listing p56/57 shows only "Agreed Property Value at Acquisition"). ✓ Nulls correct.
- **Caveat on the 2 non-null considerations:** ibis's S$178.5m and Pre de Cort's S$34.2m are **BLENDED multi-property prices** attributed to the lead property, NOT single-asset consideration (`consideration_basis:"blended"` in JSON). Not a data error, but a granularity caveat for downstream use.
- **valuation** — all five = Portfolio Listing "Agreed Property Value at Acquisition (S$'million)": ibis 136.0 (p56, line 2816), Chisun 42.5 (p56, line 2814), Pre de Cort 13.7 (p57, line 2840), Splendide 10.6 (p57, line 2850), Pregio 9.9 (p57, line 2841). Genuine SGD agreed values; distinct from the 31-Dec-2025 Portfolio-Statement carrying (ibis 145,345 / Chisun 47,106, p132). ✓
- **dates** — all confirmed: ibis/Chisun 31 Jan 2025 (fn2/fn4, p132); Citadines 2 Oct 2025 (fn3, p132; Note 28 p217); Somerset 15 Apr 2025 (p216); Pre de Cort/Splendide/Pregio 27 Aug 2025 (fn5, p135, line 5136). ✓
- **counterparty** — all five sellers source-confirmed via Portfolio-Statement footnotes (GKK Godo Kaisha ×2; HSJPN2 TMK ×3). ✓
- **currency tags** — SGD headline + JPY/CNY local, all correct as-reported. ✓

## This-FY timeline

| property | type | date | deal_fy_scope | as-reported gain/premium | use-of-proceeds |
|-|-|-|-|-|-|
| ibis Styles Tokyo Ginza | acquisition | 2025-01-31 | current_fy | n/a (PP blended S$178.5m vs val S$136.0m) | — |
| Chisun Budget Kanazawa Ekimae | acquisition | 2025-01-31 | current_fy | n/a (no PP; val S$42.5m) | — |
| Somerset Olympic Tower Tianjin | divestment | 2025-04-15 | current_fy | **c.50% above book** (p10); "approximately 50% above the property's carrying value" (Note 14a, p196); gain S$17,027k (p217) | reinvested into acquisitions / capital recycling |
| Pre de Cort Nishikyogoku | acquisition | 2025-08-27 | current_fy | n/a (PP blended S$34.2m vs val S$13.7m) | — |
| Splendide Namba West | acquisition | 2025-08-27 | current_fy | n/a (no PP; val S$10.6m) | — |
| Pregio Esaka South | acquisition | 2025-08-27 | current_fy | n/a (no PP; val S$9.9m) | — |
| Citadines Central Shinjuku Tokyo | divestment | 2025-10-02 | current_fy | **c.100% above book** (p10); "100% above the property valuation as at 31 December 2024" (p132 fn3); gain S$82,011k (p217) | reinvested into acquisitions / capital recycling |

All 7 deals completed inside the FY2025 window → **all current_fy.** (CLAS also lists FY2024 divestments in Note 28 for the comparative — Courtyard Sydney, Citadines Mt Sophia, 3 Japan hotels, Novotel Parramatta, Citadines Karasuma-Gojo, Infini Garden — those are prior_year, not in our table.)

## Corrections proposed
1. **Citadines Central Shinjuku Tokyo · `carrying_value` 128,289,000 → null (fix; derived figure).** The stored value is `net_proceeds − gain` (own basis note admits it) and appears nowhere in the report. **Physical evidence:** only aggregate disposed-IP carrying is Note 4 "Investment properties disposed **(109,494)**" (p171, Stapled Group 2025); Citadines is the sole FY2025 IP divestment (Note 28, p217). Main agent to decide **null** vs **fill 109,494** (aggregate = single-deal here, but strictly a per-property line is not printed — recommend null to honour the no-derivation invariant).

## Suggestions / raw material for design report
- **DPU-boost signal present and strong.** CLAS **excludes** divestment profit from ordinary distributable income (Distribution Statement deducts "Profit from divestments **(99,038)**", p116, line 4620) but **explicitly retains discretion to distribute past divestment gains**: "CLAS … has the **flexibility to distribute past divestment gains** to mitigate the impact of the AELs on CLAS' income" (p11, lines 524/526) and "committed to distributing past divestment gains to mitigate the impact of the AEI" for a UK property (p2070). This is a genuine capital-gains-top-up DPU lever — worth a `distributed_gain` / capital-distribution field.
- **Use-of-proceeds** disclosed strategically, not per-deal: "reinvested proceeds from previous divestments into approximately S$210 million of accretive acquisitions" (p3, line 170); FY2025 net divestments ≈ S$300m at "significant premium to book value, unlocking over S$50 million in net gain after tax" (p10, line 474).
- **Coverage gaps:**
  - Blended acquisition prices (JPY21.0bn covers ibis+Chisun; JPY4.0bn covers 3 rental-housing) mean 3 acquisitions have no recoverable per-property purchase price, and 2 carry blended prices mislabellable as single-asset — a `price_is_blended` flag + group id would help.
  - Per-property divestment carrying at disposal is not recoverable for Citadines (only aggregate S$109,494k). Do NOT derive.
  - Both **agreement date and completion date** are disclosed for Somerset (SPA 22 Oct 2024 → completed 15 Apr 2025, p196) but only completion is captured.
  - Valuation basis/method disclosed per deal (income + cost approach for Citadines; DCF for the acquisitions, p132 footnotes) but not captured.
  - Profit-after-tax contribution to date-of-disposal disclosed (Somerset S$1,131k; Citadines S$4,556k, p216–217) — a NAV/earnings-impact datum not captured.

```json
{"sym":"HMN","fy_end":"2025-12-31",
 "corrections":[
   {"record":"Citadines Central Shinjuku Tokyo","field":"carrying_value","current":128289000,"proposed":null,"page":171,"kind":"fix","evidence":"stored value is DERIVED = net_proceeds 210,300 − gain 82,011 (per own basis note); no per-property carrying printed. Only aggregate 'Investment properties disposed (109,494)' Note 4 p171 (Citadines = sole FY2025 IP divestment, Note 28 p217). Recommend null; candidate fill 109,494 if aggregate attribution accepted."}],
 "confirmed_null":{
   "Chisun Budget Kanazawa Ekimae.purchase_price":"genuinely absent — p11 table row 2 has blank Purchase Price cell, merged with lead row ibis Styles (blended JPY21.0bn/S$178.5m); no per-property split anywhere (p56/p132)",
   "Splendide Namba West.purchase_price":"genuinely absent — p11 row 4 blank, part of blended JPY4.0bn/S$34.2m rental-housing price (p11)",
   "Pregio Esaka South.purchase_price":"genuinely absent — p11 row 5 blank, part of blended JPY4.0bn/S$34.2m rental-housing price (p11)"},
 "timeline":[
   {"property":"ibis Styles Tokyo Ginza","type":"acquisition","date":"2025-01-31","scope":"current_fy"},
   {"property":"Chisun Budget Kanazawa Ekimae","type":"acquisition","date":"2025-01-31","scope":"current_fy"},
   {"property":"Somerset Olympic Tower Tianjin","type":"divestment","date":"2025-04-15","scope":"current_fy"},
   {"property":"Pre de Cort Nishikyogoku","type":"acquisition","date":"2025-08-27","scope":"current_fy"},
   {"property":"Splendide Namba West","type":"acquisition","date":"2025-08-27","scope":"current_fy"},
   {"property":"Pregio Esaka South","type":"acquisition","date":"2025-08-27","scope":"current_fy"},
   {"property":"Citadines Central Shinjuku Tokyo","type":"divestment","date":"2025-10-02","scope":"current_fy"}],
 "gain_as_reported":[
   {"property":"Somerset Olympic Tower Tianjin","gain_or_premium":"c.50% above book value (p10 table); gain S$17,027k (Note 28)","page":10},
   {"property":"Citadines Central Shinjuku Tokyo","gain_or_premium":"c.100% above book value (p10 table); 100% above 31-Dec-2024 valuation (p132 fn3); gain S$82,011k (Note 28)","page":10}],
 "proceeds_use":[
   {"property":"__both_divestments__","use":"reinvest","distributed_gain":true,"verbatim":"reinvested proceeds from previous divestments into approximately S$210 million of accretive acquisitions (p3); CLAS has the flexibility to distribute past divestment gains to mitigate the impact of the AELs on CLAS' income (p11)","page":11}],
 "coverage_gaps":[
   "blended multi-property acquisition prices (JPY21.0bn=ibis+Chisun; JPY4.0bn=3 rental-housing) — 3 per-property purchase prices not recoverable; 2 blended prices mislabellable as single-asset",
   "Citadines per-property at-disposal carrying not recoverable (only aggregate S$109,494k, Note 4 p171)",
   "SPA/agreement date vs completion date both printed for Somerset (22 Oct 2024 / 15 Apr 2025) — only completion captured",
   "per-deal valuation method disclosed (income+cost / DCF, p132 footnotes) not captured",
   "profit-after-tax contribution to disposal date disclosed (Somerset S$1,131k; Citadines S$4,556k, p216-217) not captured",
   "divestment gains excluded from ordinary distribution but discretionarily distributable — DPU capital-top-up lever not captured"]}
```
