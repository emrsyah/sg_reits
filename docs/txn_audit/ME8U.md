# ME8U.SI — Mapletree Industrial Trust — FY2024/25 property-transaction audit

**FY-END:** 2025-03-31 (window 1 Apr 2024–31 Mar 2025). **Rows:** 1 (1 acquisition, no divestment). **Verdict: date/valuation/counterparty correct; `purchase_price` is populated from the CASH-FLOW acquisition outflow (S$131,341k), NOT the as-reported purchase consideration (JPY14.5bn) — flag as a currency-basis/label nuance (no SGD consideration is printed, so no derivable fill).**

Sources: highlights **p17, p19**; Portfolio Review acquisition detail **p32**; Cash-Flow Statement (acquisition outflow / prior-year divestment gain) **p127**; Portfolio Statement valuation column **p138–139**; property table (address, acquisition date) **p46/p138**.

## Per transaction row — Tokyo Property, acquisition 29-Oct-2024

- **type / date:** acquisition, 29/10/2024 ✓ (p19, p32, p46/p138). Within FY24/25 window → **current_fy**.
- **counterparty:** the report names the vendor as **Nagayama Tokutei Mokuteki Kaisha** (a Japanese TMK) (p32). The JSON has **no counterparty field** → propose FILL: `counterparty = "Nagayama Tokutei Mokuteki Kaisha"` (p32). The JSON `note` already mentions the address (1-7 & 2-1 Nagayama 2-chome, Tama-shi, Tokyo) but not the vendor.
- **purchase_price = 131,341,000 (SGD)** — ⚠ **label nuance.** This is the Cash-Flow Statement line *"Acquisition of investment property (131,341)"* (p127) — the SGD cash outflow, distinct from the acquisition additions line *"Additions to investment properties (107,507)"*. The **as-reported purchase consideration is JPY14.5 billion** (agreed property value, p17/p19/p32); **no SGD equivalent of the JPY14.5bn is printed**, so the cash outflow is the only as-reported SGD acquisition figure. Keeping 131,341k is defensible (it IS a printed SGD acquisition number) but it is a cash-flow figure, not a "consideration" line — recommend a `purchase_price_basis` note. Do NOT convert JPY14.5bn → SGD (prohibited).
- **valuation = 135,272,000 (SGD)** ✓ genuine, but it is the **31 Mar 2025 year-end portfolio valuation** (Portfolio Statement "Valuation as at 31/03/2025", p139), **NOT the acquisition-date independent valuation**. The acquisition-date independent valuation was **JPY15.0 billion** by JLL Morii Valuation & Advisory K.K. (p32), which the JPY14.5bn agreed price was ~**3.3% below**. So the row mixes an acquisition price (proxy) with a year-end valuation — both genuine, but different dates/bases.
- **amount = 135,272,000** = same 31 Mar 2025 valuation (duplicate of `valuation`).
- **currency = SGD** ✓ for the SGD figures; headline consideration/valuation are in JPY (JPY14.5bn / JPY15.0bn) — not captured.
- **divestment/gain/carrying/net columns:** N/A (acquisition). **No FY24/25 divestment** — Cash-Flow "Gain on divestment of investment property" = **– (nil) FY24/25** vs 3,492 in FY23/24 (prior year) (p127). Confirmed no divestment row missing.

## This-FY timeline

| property | type | date | deal_fy_scope | as-reported gain/premium | use-of-funds |
|-|-|-|-|-|-|
| Tokyo Property | acquisition | 2024-10-29 | current_fy | acquired at **~3.3% discount to independent valuation** (JPY14.5bn price vs JPY15.0bn JLL Morii valuation, p32) — accretive | funded by **new borrowings** (interest expense on new borrowings taken to fund the Tokyo Acquisition, p17) |

## Corrections proposed
1. **FILL `counterparty` = "Nagayama Tokutei Mokuteki Kaisha"** (p32) — vendor is named in source, currently absent.
2. **(soft) Add `purchase_price_basis`** noting 131,341k = cash-flow acquisition outflow (p127); headline consideration = JPY14.5bn agreed property value (p32). No $-value change proposed (cannot convert JPY→SGD).

No change to `valuation`/`amount` — 135,272k is the genuine 31 Mar 2025 portfolio valuation (p139); flag only that it is the reporting-date valuation, not the acquisition valuation (JPY15.0bn).

## Suggestions / raw material for design report
- **No divestment ⇒ no divestment-gain/DPU signal** in FY24/25. (Distribution S$386.0m, DPU 13.57¢, +1.0% y/y — driven by Tokyo NPI + repricing, p16/p17; not a divestment-gain distribution.) `distributed_gain = false` (n/a). Note FY23/24 had a divestment gain of S$3,492k (prior year, out of window).
- **Acquisition "value-creation" signal:** acquired at **3.3% discount to independent valuation** (JPY14.5bn vs JPY15.0bn, p32) — the acquisition analogue of a divestment premium; worth capturing for accretion analysis.
- **Coverage gaps:**
  - **Headline consideration is JPY-denominated (JPY14.5bn)**; only the SGD cash outflow (131,341k) and SGD year-end valuation (135,272k) are captured — a `consideration_local`/`consideration_currency` pair (as K71U uses) would preserve the JPY14.5bn.
  - **Acquisition-date independent valuation (JPY15.0bn, JLL Morii)** disclosed (p32) but not captured — distinct from the 31 Mar 2025 valuation.
  - **Effective interest** disclosed: MIT **98.47%**, Sponsor/MIPL **1.53%** (p19 fn) — stake not captured (cash outflow 131,341k may be MIT's share basis).
  - **Vendor name** (Nagayama TMK), **GFA (~319,300 sq ft)**, **WALE (~5 yrs)**, **redevelopment-to-data-centre intent** disclosed (p32) but not captured.

```json
{"sym":"ME8U","fy_end":"2025-03-31",
 "corrections":[
   {"record":"Tokyo Property","field":"counterparty","current":null,"proposed":"Nagayama Tokutei Mokuteki Kaisha","page":32,"kind":"fill","evidence":"'On 29 October 2024, MIT acquired a freehold property in Tokyo from Nagayama Tokutei Mokuteki Kaisha at a purchase consideration of JPY14.5 billion' (p32) — vendor named, currently absent."},
   {"record":"Tokyo Property","field":"purchase_price_basis","current":null,"proposed":"S$131,341k = cash-flow 'Acquisition of investment property' outflow (p127); as-reported headline consideration is JPY14.5bn agreed property value (p32) — no SGD equivalent printed","page":127,"kind":"note","evidence":"Cash-Flow Statement line 'Acquisition of investment property (131,341)' (p127) vs headline JPY14.5bn (p17/p19/p32). purchase_price is a cash-flow figure, not a consideration line; no JPY→SGD conversion permitted."}],
 "confirmed_null":{
   "divestment_columns":"no FY24/25 divestment — Cash-Flow 'Gain on divestment of investment property' = nil FY24/25 (3,492 in FY23/24 prior year), p127",
   "gain_on_divestment":"n/a — acquisition row; no divestment in FY24/25"},
 "timeline":[
   {"property":"Tokyo Property","type":"acquisition","date":"2024-10-29","scope":"current_fy"}],
 "gain_as_reported":[
   {"property":"Tokyo Property","gain_or_premium":"acquired at ~3.3% discount to independent valuation (JPY14.5bn agreed price vs JPY15.0bn JLL Morii valuation)","page":32}],
 "proceeds_use":[
   {"property":"Tokyo Property","use":"fund_acquisition","distributed_gain":false,"verbatim":"interest expense on new borrowings taken to fund the Tokyo Acquisition (p17); acquisition funded via new borrowings","page":17}],
 "coverage_gaps":[
   "headline consideration is JPY14.5bn (agreed property value) — only SGD cash outflow 131,341k + SGD year-end valuation 135,272k captured; no consideration_local/currency preserving JPY",
   "acquisition-date independent valuation JPY15.0bn (JLL Morii, p32) not captured — distinct from 31 Mar 2025 valuation 135,272k",
   "effective interest MIT 98.47% / Sponsor 1.53% (p19) not captured",
   "vendor Nagayama TMK, GFA ~319,300 sqft, WALE ~5yrs, redevelopment intent (p32) not captured",
   "purchase_price = cash-flow outflow (p127), not a consideration line — needs purchase_price_basis"]}
```
