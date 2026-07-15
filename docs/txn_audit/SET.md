# SET.SI — Stoneweg Europe Stapled Trust (SERT) — FY2025 property-transaction audit

**FY-END:** 2025-12-31 (window 1 Jan–31 Dec 2025). **Rows:** 6 (1 acquisition + 5 divestment). **Verdict: all 6 typed values verified correct — no value corrections.** 3 office `carrying_value_basis` page-cites are off by one (datalab split-table); 1 classification nuance (AiOnX = financial asset, not a property). Currency: EUR throughout.

Sources: "Divestments Completed in FY2025" table + fn8/fn9 **p43**, Statement of Portfolio (fair-value columns) **p179/p181**, Note 5 (Loss)/Gain on Divestments **p201–202**, Note 9 Investment Properties + fn(2) **p209**, Note 10 Investment in financial asset (AiOnX) **p214**, Note 17 Assets held for sale **p240**, Manager's/Capital-management report **p35/p42**.

## Per-column null/value status

### Divestments (5) — verified against p43 table + Note 5
| property | ctry | date | gross_sale_price | valuation (date) | carrying (31-Dec-2024) | gain | counterparty |
|-|-|-|-|-|-|-|-|
| Slovakia portfolio (5 log./light-ind.) | SK | 2025-11-11 | €70.0m (p43 fn9; Note 5a p201) | €72.4m (30 Jun 2025) | €72,645k (Note 5a, p201) | €1,181k (Note 5a, p201) | P3 Czech HoldCo a.s. |
| Via della Fortezza 8, Florence | IT | 2025-03-05 | €15.0m (p43) | €15.1m (30 Jun 2024) | €15,000k (Note 17, p240) | **null** | Agenzia del Demanio |
| Arkonska Business Park, Gdansk | PL | 2025-09-17 | €7.8m (p43) | €8.0m (30 Jun 2025) | €7,960k (Portfolio, p181) | **null** | GetResponse Properties Sp. z o.o. |
| Cassiopea 1-2-3, Milan | IT | 2025-11-04 | €11.4m (p43) | €11.0m (30 Jun 2025) | €11,650k (Portfolio, p179) | **null** | Finviar S.r.l. |
| Maxima (Via dell'Amba Aradam 5), Rome | IT | 2025-12-18 | €34.0m (p43) | €25.7m (30 Jun 2025) | €25,240k (Portfolio p179; Note 9 fn2 "€25.2m" p209) | **null** | SEANA S.r.l. |

- **gross_sale_price** — all five match the p43 "Divestments Completed in FY2025" sale-price column and the Note-5 narrative (Slovakia €70.0m final consideration; Florence €15.0m; Arkonska €7.8m; Cassiopea €11.4m; Maxima €34.0m). ✓
- **valuation** — all five match the p43 "Valuation" column (Slovakia €72.4m per fn9; Florence €15.1m; Arkonska €8.0m; Cassiopea €11.0m; Maxima €25.7m). These are independent appraisals; **valuation reference dates differ** (Florence 30 Jun 2024; the rest 30 Jun 2025) and are distinct from carrying. ✓
- **carrying_value** — all five source-printed, NOT conflated with valuation:
  - Slovakia **72,645k** = Note 5(a) "Investment properties **72,645**" in the disposed-subsidiaries carrying table (p201, line 7628). ✓
  - Florence **15,000k** = Note 17 Assets-held-for-sale 2024 column (p240, line 9138); remeasured to the €15.0m contracted price while held for sale. ✓
  - Arkonska **7,960k**, Cassiopea **11,650k**, Maxima **25,240k** = Statement-of-Portfolio 2024 fair-value column, each with a "–" in the 2025 column (derecognised on divestment): Maxima/Cassiopea p179 (lines 6812–6813), Arkonska p181 (line 6884). Maxima independently corroborated by Note 9(a) fn(2) "Maxima, Italy valued at **€25.2 million**" (redevelopment, p209, line 7936). ✓ **(page-cite refinement: JSON basis says p178/p178/p180; physical value rows are p179/p179/p181 — datalab split the wide table across pages. Values correct.)**
- **gain_on_divestment** —
  - Slovakia **1,181k**: source-printed, "Gain on divestment of subsidiaries **1,181**" (Note 5, p201, lines 7615 & 7638). ✓
  - Florence / Arkonska / Cassiopea / Maxima **null — RE-CONFIRMED genuinely absent.** Note 5(b) states the four office/held-for-sale divestments produced a **combined** "(Loss)/Gain on divestment of investment properties & asset held for sale **(1,943)**" (p201–202, line 7616), attributed to transaction costs & divestment fees; **no per-property gain/loss is split** (p202, lines 7650–7657). ✓
- **counterparty** — all five confirmed in the p43 "Purchaser" column and Note 5 narrative. ✓

### Florence held-for-sale — RE-CONFIRMED
Florence is unambiguously the carried-over held-for-sale asset:
- Balance Sheet "Asset held for sale" 2024 = **15,000** (line 6420).
- Note 17 held-for-sale table lists "Via della Fortezza 8, Florence, Italy | (b) | – | 15,000" (2025 nil / 2024 15,000, p240, line 9138).
- Note 17(b): "**In 2024, the property was classified as held for sale** based on a binding offer with an unrelated third party for … €15.0 million. **The divestment was completed on 5 March 2025**" (p240, line 9142).
- Note 5(b)(i): Florence "which was **held for sale at 31 December 2024**" (p202). ✓✓✓

### Acquisition (1)
| property | date | consideration | carrying/FV | counterparty |
|-|-|-|-|-|
| AiOnX (Stoneweg Iona) data-centre development fund | 2025-06-23 | €50.0m subscription (Note 10, p214) | carried FVTPL €70,536k (FV uplift €20,536k) | AiOnX fund — managed by a controlling shareholder of the BT Trustee-Manager (Sponsor, related party) |

- **purchase_price €50.0m** — Note 10(a) "Subscription for units in AiOnX data centre fund **50,000**"; "On 23 June 2025, Stoneweg European BT Group … invested **€50.0 million** in the Stoneweg Iona data-centre fund (subsequently rebranded to AiOnX)" (p214, lines 8106/8115). ✓
- **date 2025-06-23** ✓; **stake 6.6%** (p214). **Classification nuance:** this is an investment in a **financial asset (FVTPL)** held via the Business Trust, NOT a consolidated property acquisition — it never appears in the Portfolio Statement. Row type "acquisition" is defensible as a capital deployment but is a different asset class from the property rows. ✓ (JSON `note` already flags this.)

## This-FY timeline

| property | type | date | deal_fy_scope | as-reported gain/premium | use-of-proceeds |
|-|-|-|-|-|-|
| Via della Fortezza 8, Florence | divestment | 2025-03-05 | current_fy | €15.0m, 0.7% BELOW 30-Jun-2024 valuation (p42) | security buyback + capital recycling |
| AiOnX data-centre fund | acquisition | 2025-06-23 | current_fy | n/a (€50m in; FV €70,536k) | — |
| Arkonska Business Park | divestment | 2025-09-17 | current_fy | €7.8m, 2.0–2.2% BELOW 30-Jun-2025 valuation (p42/Note 5b) | security buyback + capital recycling |
| Cassiopea 1-2-3, Milan | divestment | 2025-11-04 | current_fy | €11.4m, 2.9% above 30-Jun-2025 valuation (p42) | security buyback + capital recycling |
| Slovakia portfolio (5 assets) | divestment | 2025-11-11 | current_fy | €70.0m, 3.5% premium to net asset value €67.7m; gain €1,181k (Note 5a) | security buyback + capital recycling |
| Maxima, Rome | divestment | 2025-12-18 | current_fy | €34.0m, 32.3% above 30-Jun-2025 valuation (p42) | security buyback + capital recycling |

All 6 completed inside FY2025 → **all current_fy.** (Purotie 1, Helsinki is held-for-sale at 31 Dec 2025, completion in 2026 — a `subsequent_event`, correctly NOT in our table.)

## Corrections proposed
**No typed-value corrections.** Three page-cite refinements (`_basis` note only; values verified correct):
1. Maxima `carrying_value_basis` page 178 → **179**.
2. Cassiopea `carrying_value_basis` page 178 → **179**.
3. Arkonska `carrying_value_basis` page 180 → **181**.

## Suggestions / raw material for design report
- **Critical gross↔net / valuation↔carrying trap (headline "gain" ≠ reported gain).** The narrative sells "€140 million of non-core assets … at a blended **11% premium to net valuation**" (p35, line 1546; p42, line 1789), yet the P&L **"(Loss)/Gain on divestments" is a NET LOSS of €762k** (Note 5: subsidiary gain €1,181k − office/HFS loss €1,943k, p201). Under the IAS 40 fair-value model, the premium over carrying is booked as a **fair-value revaluation gain** (separate "€11.3m fair value gain on investment properties" line, p37) — the divestment line captures only transaction costs. Maxima is the extreme case: sold at €34.0m (32.3% above €25.7m valuation, ~€8.3m headline uplift) but per-deal divestment gain is not split and most of the uplift ran through the revaluation line. **Any "as-reported gain" field must distinguish marketing-premium vs P&L divestment gain vs FV revaluation gain.**
- **DPU / use-of-proceeds:** proceeds funded a **~€10m security buyback** completed in FY2025 and "created optionality for accretive acquisitions in FY 2026" (p35, line 1546). **No distribution of divestment gains** to unitholders (there was a net divestment loss). `distributed_gain = false`; a security buyback is a distinct capital-return lever worth a category.
- **Coverage gaps:**
  - Slovakia has THREE printed figures — €71.4m agreed property price, €70.0m final consideration, €72.4m valuation (30 Jun 2025) (p43 fn9) — only the €70.0m consideration + €72.4m valuation are captured.
  - Per-property divestment gain is not recoverable for the 4 office/HFS deals (only combined €1,943k loss). Do NOT derive.
  - **Valuation reference date** differs per deal (Florence 30 Jun 2024 vs others 30 Jun 2025) and by valuer (JLL vs Savills, p42/Note 9 p210) — not captured.
  - Slovakia was a **100% share sale of 5 property companies** (deal structure) with net-cash-flow €67,943k and transaction cost €804k disclosed (Note 5a, p201) — structure & net cash flow not captured.
  - AiOnX FV uplift €20,536k and 6.6% stake / 5 development sites (p214) — a financial-asset acquisition our property-oriented table cannot cleanly represent.

```json
{"sym":"SET","fy_end":"2025-12-31",
 "corrections":[
   {"record":"Maxima, Rome","field":"carrying_value_basis(page)","current":178,"proposed":179,"page":179,"kind":"fix","evidence":"carrying 25,240 printed on Statement of Portfolio 2024 col, physical PAGE 179 (line 6812); value correct, JSON cite off by one"},
   {"record":"Cassiopea 1-2-3, Milan","field":"carrying_value_basis(page)","current":178,"proposed":179,"page":179,"kind":"fix","evidence":"carrying 11,650 printed p179 (line 6813); value correct, cite off by one"},
   {"record":"Arkonska Business Park, Gdansk","field":"carrying_value_basis(page)","current":180,"proposed":181,"page":181,"kind":"fix","evidence":"carrying 7,960 printed p181 (line 6884); value correct, cite off by one"}],
 "confirmed_null":{
   "Via della Fortezza 8, Florence.gain_on_divestment":"per-property gain absent; combined office/HFS loss €1,943k only (Note 5b, p202)",
   "Arkonska Business Park.gain_on_divestment":"per-property gain absent; combined €1,943k loss (Note 5b, p202)",
   "Cassiopea 1-2-3.gain_on_divestment":"per-property gain absent; combined €1,943k loss (Note 5b, p202)",
   "Maxima.gain_on_divestment":"per-property gain absent; combined €1,943k loss; premium over carrying booked as FV revaluation gain, not divestment line (Note 5b/Note 9, p202/p209)"},
 "timeline":[
   {"property":"Via della Fortezza 8, Florence","type":"divestment","date":"2025-03-05","scope":"current_fy"},
   {"property":"AiOnX data centre development fund","type":"acquisition","date":"2025-06-23","scope":"current_fy"},
   {"property":"Arkonska Business Park, Gdansk","type":"divestment","date":"2025-09-17","scope":"current_fy"},
   {"property":"Cassiopea 1-2-3, Milan","type":"divestment","date":"2025-11-04","scope":"current_fy"},
   {"property":"Slovakia portfolio (5 logistics/light industrial properties)","type":"divestment","date":"2025-11-11","scope":"current_fy"},
   {"property":"Maxima, Rome","type":"divestment","date":"2025-12-18","scope":"current_fy"}],
 "gain_as_reported":[
   {"property":"Slovakia portfolio","gain_or_premium":"€70.0m = 3.5% premium to net asset value €67.7m; gain on disposal of subsidiaries €1,181k (Note 5a)","page":201},
   {"property":"Via della Fortezza 8, Florence","gain_or_premium":"0.7% (€0.1m) below 30-Jun-2024 valuation; per-deal gain not split","page":42},
   {"property":"Arkonska Business Park","gain_or_premium":"2.0-2.2% (€0.2m) below 30-Jun-2025 valuation; per-deal gain not split","page":42},
   {"property":"Cassiopea 1-2-3, Milan","gain_or_premium":"2.9% (€0.3m) above 30-Jun-2025 valuation; per-deal gain not split","page":42},
   {"property":"Maxima, Rome","gain_or_premium":"32.3% (€8.3m) above 30-Jun-2025 valuation; per-deal gain not split (uplift mostly booked as FV revaluation gain)","page":42},
   {"property":"__portfolio__","gain_or_premium":"blended '11% premium to net valuations' (p42) BUT P&L (Loss)/Gain on divestments = NET LOSS €762k (Note 5, p201)","page":201}],
 "proceeds_use":[
   {"property":"__all_5_divestments__","use":"reinvest","distributed_gain":false,"verbatim":"These divestments supported the ~€10 million security buyback that the Manager completed in FY 2025 and created optionality for accretive acquisitions in FY 2026 (p35)","page":35}],
 "coverage_gaps":[
   "Slovakia has 3 figures (agreed price €71.4m / consideration €70.0m / valuation €72.4m) — only 2 captured",
   "per-property divestment gain not recoverable for 4 office/HFS deals (only combined €1,943k loss) — do not derive",
   "valuation reference date + valuer (JLL/Savills; Florence 30-Jun-2024 vs others 30-Jun-2025) not captured",
   "Slovakia deal structure = 100% share sale of 5 companies; net cash flow €67,943k, transaction cost €804k (Note 5a) not captured",
   "AiOnX is a financial-asset (FVTPL) investment via Business Trust, not a consolidated property acquisition; FV uplift €20,536k / 6.6% stake not representable",
   "headline premium vs P&L divestment gain vs FV revaluation gain are three different numbers — needs disambiguation"]}
```
