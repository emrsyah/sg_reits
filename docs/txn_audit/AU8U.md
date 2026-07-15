# AU8U.SI — CapitaLand China Trust (CLCT) — FY2025 property-transaction audit

**FY-END:** 2025-12-31 (window 1 Jan–31 Dec 2025). **Rows:** 1 (divestment). **Verdict: row verified correct — no corrections. One valuation nuance + a strong DPU-linkage signal captured.**

Sources: divestment narrative **p36**, portfolio valuation table **p28**, Statement of Total Return **p95**, cash-flow + Note B "Net cash inflow on divestment of subsidiary" **p103–104**, distribution top-up notes **p12/p96 (fn1)**, capital management **p29**.

## The deal
CapitaMall Yuhuating (Changsha, China), a mature retail asset, divested to **CapitaLand Commercial C-REIT (CLCR)** — completed **31 Oct 2025** via sale of **100% equity of the SPV** holding the mall, to **Changsha 2023 Consulting & Management Co., Ltd.** (through Changsha Kaiting Consulting & Management Co., Ltd.), each an indirect wholly-owned subsidiary of CapitaLand Mall Asia Ltd (PRC). Interested-person transaction; CLCT retains a 5% strategic stake in CLCR. Sale price **RMB813.8 million** (p36).

## Per-column null/value status
| column | value | verified | source |
|-|-|-|-|
| transaction_type / status | divestment / completed | ✓ | p36 "completed on 31 October 2025" |
| completion_date | 2025-10-31 | ✓ | p36; p95 fn(3) |
| gross_sale_price | RMB 813,800,000 | ✓ | p36 "sale price of RMB813.8 million" |
| gross_sale_price_currency | RMB (→CNY at load) | ✓ | p36 (RMB) |
| valuation | RMB 785,000,000 | ✓ (see nuance) | p28 "Valuation 2024" RMB785.0m; **p95 fn(3) benchmarks the sale against "the valuation as at 31 December 2024"** — the report's own premium benchmark |
| valuation_currency | RMB | ✓ | p28 |
| net_proceeds | S$ 131,644,000 | ✓ | p104 Note B "Net cash inflow" |
| net_proceeds_currency | SGD | ✓ | p103/104 (S$'000) |
| gain_on_divestment | −S$ 11,988,000 (loss) | ✓ | p95 "(Loss)/gain on disposal of subsidiaries (11,988)"; = p104 Note B |
| gain_on_divestment_currency | SGD | ✓ | p95 |
| carrying_value | S$ 144,879,000 | ✓ | p104 Note B "Investment properties 144,879" (IP carrying inside the disposed SPV) |
| carrying_value_currency | SGD | ✓ | p104 |
| counterparty | Changsha 2023 Consulting & Mgmt Co. (CapitaLand Mall Asia subsidiary) | ✓ | p36 (ultimate acquirer CLCR) |

- **gross_sale_price RMB813.8m** — printed verbatim p36. ✓ Currency is RMB (Chinese yuan); normalises to CNY at load. Confirmed.
- **net_proceeds S$131,644k** — this is the **"Net cash inflow"** on the subsidiary disposal (p104 Note B): sale consideration S$139,792k less transaction costs, tax paid and cash of subsidiary divested. It is a genuine net figure (net of costs), correctly labelled net_proceeds; distinct from gross. ✓
- **gain_on_divestment −S$11,988k** — a **LOSS**, correct sign (reduces total return, p95). Per p95 fn(3): "mainly due to the realisation of foreign exchange differences upon divestment, partially offset by the premium over the valuation as at 31 December 2024." The full FY2025 "loss on disposal of subsidiaries" is entirely Yuhuating (only 2025 disposal). ✓
- **carrying_value S$144,879k** — the investment-property carrying inside the disposed SPV (p104 Note B). Distinct from valuation (RMB785.0m / S$145.6m at 31 Dec 2024, p28) and from net assets divested (S$142,300k). No conflation. ✓
- **valuation RMB785.0m** — genuine printed figure (p28 "Valuation 2024") and, importantly, the report's **own** premium benchmark (p95 fn(3)). *Nuance:* p36 also prints two **deal-specific independent valuations** commissioned for the divestment — **Colliers RMB748.0m** and **CBRE RMB780.0m** — which are not captured. See suggestions.

## This-FY timeline
| property | type | date | deal_fy_scope | as-reported gain/premium | use-of-proceeds |
|-|-|-|-|-|-|
| CapitaMall Yuhuating | divestment | 2025-10-31 | current_fy | **loss −S$11,988k** (realised FX); sold RMB813.8m — a premium over the RMB785.0m 31-Dec-2024 valuation (and over deal valuations RMB748m/RMB780m) | reduce leverage / general |

## Corrections proposed
**None.** All typed figures, currency tags, date and counterparty match the source.

## Suggestions / raw material for design report
- **DPU-boost signal (STRONG — capture):** although the Yuhuating divestment itself booked a *loss*, CLCT made a **distribution top-up drawn from PAST divestment gains** to replace the lost income. Verbatim (p12 / p96 fn1 / MD&A): *"In 2025, there is a distribution top-up of approximately the distribution income from CapitaMall Yuhuating, which would have been contributed from 1 April 2025 to 31 December 2025 … It is drawn from **past divestment gains** from CLCT and is funded through debt."* and *"…topped up for 2H 2025 distribution from past divestment gains in the interim to make up for the absence of income from CapitaMall Yuhuating."* → `distributed_gain = true` (capital-gains top-up mechanism), even though this specific deal was a loss.
- **Use-of-proceeds (p36):** *"The net proceeds from this transaction enabled us to strengthen our balance sheet by **reducing leverage**, while enhancing financial flexibility."* Corroborated by aggregate leverage 41.9%→40.7% (p29) and large borrowings repayment in the cash flow. → `use = repay_debt`.
- **Coverage gaps:**
  - **Deal-specific independent valuations not captured** — Colliers **RMB748.0m** and CBRE **RMB780.0m** (p36), two named valuers. The stored `valuation` is instead the 31-Dec-2024 book valuation (RMB785.0m). Consider capturing the deal valuation(s) and/or the valuer names.
  - **SGD gross sale consideration is also printed** — p104 Note B "Sale consideration **139,792**" (S$, = RMB813.8m). Table stores gross in RMB only + net in SGD; the SGD gross exists if a same-currency gross↔net pair is wanted.
  - **Deal structure = SPV/equity sale (subsidiary disposal):** net identifiable assets divested S$142,300k, transaction costs S$4,950k (p104) — not captured.
  - **Interested-person transaction / related-party acquirer (CLCR, sponsor-linked); 5% strategic stake retained** — not flagged.
  - **Partial-year contribution** of Yuhuating (1 Jan–31 Oct 2025: gross revenue ~S$4.0m, NPI ~S$2.5m) included in FY2025 totals — per prior note; useful for like-for-like analysis.

```json
{"sym":"AU8U","fy_end":"2025-12-31",
 "corrections":[],
 "confirmed_null":{
   "deal_valuation_colliers_cbre":"deal-specific independent valuations Colliers RMB748.0m & CBRE RMB780.0m printed p36 but NOT stored; stored valuation is 31-Dec-2024 book valuation RMB785.0m (p28), which is the report's own premium benchmark per p95 fn(3)"},
 "timeline":[
   {"property":"CapitaMall Yuhuating","type":"divestment","date":"2025-10-31","scope":"current_fy"}],
 "gain_as_reported":[
   {"property":"CapitaMall Yuhuating","gain_or_premium":"loss −S$11,988k (realised FX); sold RMB813.8m at a premium over RMB785.0m 31-Dec-2024 valuation (deal valuations RMB748.0m Colliers / RMB780.0m CBRE)","page":95}],
 "proceeds_use":[
   {"property":"CapitaMall Yuhuating","use":"repay_debt","distributed_gain":true,"verbatim":"net proceeds enabled us to strengthen our balance sheet by reducing leverage (p36); AND a 2H-2025 distribution top-up drawn from PAST divestment gains (funded through debt) to replace Yuhuating's lost income (p12/p96 fn1)","page":36}],
 "coverage_gaps":[
   "deal-specific independent valuations Colliers RMB748.0m & CBRE RMB780.0m (p36) + valuer names not captured",
   "SGD gross sale consideration S$139,792k printed p104 but only RMB gross stored",
   "deal structure SPV/equity sale: net assets divested S$142,300k, transaction costs S$4,950k (p104)",
   "interested-person transaction; acquirer CLCR sponsor-linked; 5% strategic stake retained — not flagged",
   "distribution top-up from past divestment gains (DPU booster) — verbatim captured, not modelled in table"]}
```
