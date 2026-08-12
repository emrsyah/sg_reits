# ODBU.SI — United Hampshire US REIT (UHREIT) — FY2025 property-transaction audit

FY-end: **2025-12-31**. Rows audited: **3** (1 divestment + 2 acquisitions). All figures USD.

## Row 1 — Dover Marketplace (acquisition, completed)

| Column | JSON value | Verdict | Source |
|---|---|---|---|
| transaction_type / status | acquisition / completed | ✅ correct | "On 1 August 2025, UHREIT completed the acquisition of Dover Marketplace" (p38 line 1874) |
| transaction_date | 2025-08-01 | ✅ correct | p38 line 1874; portfolio footnote (p35 line 1749) |
| deal_fy_scope | (current_fy) | ✅ completed inside FY2025 | p38 |
| purchase_consideration | 16,400,000 USD | ✅ correct — headline consideration | "purchase consideration of approximately US$16.4 million represents an ~4.8% discount to the independent valuation of US$17.2 million" (p18 line 692; p16 line 592) |
| price | 17,046,000 USD | ⚠️ this is TOTAL acquisition cash outflow (incl. costs), NOT the headline consideration | Cash flow "Acquisition of investment property and related assets and liabilities (17,046)" (p165 line 6143); Note 7 "Acquisition (including acquisition cost) 17,046" (p184 line 6804) |
| valuation | 17,200,000 USD | ✅ correct (Newmark V&A) | p18/p16; valuation table 17,200 (p35 line 1735); portfolio statement 17,200 (p167 line 6210) |
| carrying/net/gain | — | ✅ n/a for acquisition | — |
| counterparty | null | ✅ confirmed — seller not named | p38 |

**Relabel flag:** ensure the canonical `purchase_price` column = **US$16,400k** (headline consideration), **not** US$17,046k. The 17,046 figure is the total acquisition **cash outflow including acquisition costs** (cash-flow / Note 7), a different quantity. If the loader maps `price`→purchase_price, it overstates the consideration by US$0.646m. Both figures are genuine; the label matters.

## Row 2 — Albany Supermarket (divestment, completed) — TRIPLE-EQUALITY case

| Column | JSON value | Verdict | Source |
|---|---|---|---|
| transaction_type / status | divestment / completed | ✅ correct | "Divestment of Albany – Supermarket was completed on 17 January 2025" (p35 line 1747; Note 7 p184 line 6827) |
| transaction_date | 2025-01-17 | ✅ correct | p35/p184 |
| deal_fy_scope | (current_fy) | ✅ completed inside FY2025 window (Jan 2025) | p184 |
| sale_consideration (gross_sale_price) | 23,800,000 USD | ✅ correct | "completed on 17 January 2025 for a consideration of US$23.8 million, which is also the fair value as at 31 December 2024" (Note 7 p184 line 6827) |
| valuation | 23,800,000 USD | ✅ correct — CBRE fair value @31 Dec 2024 | "...which is also the fair value as at 31 December 2024 based on the independent valuation undertaken by CBRE, Inc." (p184 line 6827) |
| carrying_value | 23,800,000 USD | ✅ correct — held-for-divestment carrying | "Investment property held for divestment 23,800" @31 Dec 2024 (portfolio statement p167 line 6218; Note 7 roll-forward "Divestment (23,800)" p184 line 6817) |
| net_proceeds | 23,116,000 USD | ✅ correct — genuinely printed | Cash flow "Divestment of investment properties and related assets and liabilities 23,116" (p165 line 6145) |
| gain_on_divestment | -684,000 USD | ✅ correct — **printed, not derived** | "(Loss)/gain on divestment of investment properties (684)" Statement of Total Return (p30 line 1482; also p185 line 5971/6016, segment note p... line 7462) |
| counterparty | null | ✅ confirmed — buyer not named | p184 |

**Triple-equality is GENUINE:** held-for-divestment **carrying US$23,800k** = **CBRE fair value @31 Dec 2024 US$23,800k** = **gross sale consideration US$23,800k** — all three literally printed and equal (p167, p184). The **loss US$(684)k** is separately printed in the Statement of Total Return (p30) — it is NOT a derived figure; the accompanying arithmetic (net proceeds 23,116 − carrying 23,800 = −684) merely explains why a headline-flat sale still books a loss (selling/transaction costs bridge gross 23,800 → net 23,116). Marketing framing says the sale was **"4.2% above purchase price"** (i.e. original IPO cost, p9 line 342 / p16 line 592) — an as-reported *premium vs cost* that coexists with the *accounting loss vs carrying*. Both are true; capture both.

## Row 3 — Wallingford Fair Shopping Center (acquisition, completed post-FY)

| Column | JSON value | Verdict | Source |
|---|---|---|---|
| transaction_type / status | acquisition | ✅ correct | "On 14 January 2026... completed the acquisition of Wallingford Fair Shopping Center for a cash consideration of US$21.4 million" (p38 line 1886; Note 33 subsequent events p211 line 7807) |
| financial_year / scope | 2026 → **subsequent_event** | ✅ correct — completed after 2025-12-31 | p38/p211 |
| transaction_date | 2026-01-14 | ✅ correct | p38/p211 |
| price (purchase_price) | 21,400,000 USD | ✅ correct | p38/p211/p16 |
| valuation | 23,300,000 USD | ✅ correct (CBRE V&A @25 Nov 2025) | "independent valuation... by CBRE Valuation & Advisory Services as at 25 November 2025" (p9 footnote line 3091); "8.2% below its independent valuation" (p16 line 592; p9 line 358) |
| carrying/net/gain | null | ✅ n/a — acquisition (subsequent event) | — |
| counterparty | null | ✅ confirmed — seller not named | p38/p211 |

## This-FY timeline

| property | type | date | deal_fy_scope | as-reported gain / premium | use-of-proceeds |
|---|---|---|---|---|---|
| Albany Supermarket | divestment (completed) | 2025-01-17 | current_fy | **loss US$(684)k** vs carrying; **"4.2% above purchase price"** (p9/p16) | proceeds "successfully redeployed capital into higher-yielding assets" (Dover + Wallingford) — capital recycling (p16 line 592) |
| Dover Marketplace | acquisition (completed) | 2025-08-01 | current_fy | **4.8% below independent valuation** US$17.2m (p18) — DPU-accretive | funded by Albany recycling; debt-neutral |
| Wallingford Fair | acquisition (completed) | 2026-01-14 | subsequent_event | **8.2% below independent valuation** US$23.3m (p9/p16) — DPU-accretive | capital recycling |

## Corrections proposed
- **Dover `purchase_price` should = US$16,400k (headline consideration), not US$17,046k** (total cash outflow incl. acquisition costs). `{"record":"Dover Marketplace","field":"purchase_price","current":17046000,"proposed":16400000,"page":184,"kind":"relabel"}`. Retain 17,046 as a separate acquisition-cash/carrying figure if the schema supports it.
- No other corrections — Albany triple-equality and all nulls verified genuine.

## As-reported profit-from-divestment (raw material)
- Albany: **US$(684)k loss** (Statement of Total Return, p30) AND **"4.2% above purchase price"** (p9/p16). (Only investment-property divestment in FY2025, so the whole (684) line is Albany.)
- Dover / Wallingford (acquisitions): discounts to valuation **4.8%** / **8.2%** (accretion signal).

## Use-of-proceeds / DPU linkage
- **Capital recycling explicit:** Albany proceeds "successfully redeployed capital into higher-yielding assets" → Dover + Wallingford (p16 line 592). Both acquisitions labelled **"DPU-accretive"** (p9 lines 334/349/358; p18 line 692).
- **No distribution of the divestment result** (it was a loss anyway) → `distributed_gain=false`. DPU growth is driven by redeployment into higher-yielding assets, not gain distribution. UHREIT reports "third consecutive period of DPU growth" (p16 line 556) — attributable to recycling, not a special distribution.

## Suggestions / coverage gaps
- **Two acquisition-consideration figures printed per acquisition** (headline vs cash-incl-costs) — schema should distinguish `purchase_consideration` from `total_acquisition_cost`.
- **Discount/premium-to-valuation %** (Dover 4.8%, Wallingford 8.2%, Albany 4.2% above cost) and **DPU-accretive flag** are disclosed for every deal — highly recoverable, currently uncaptured.
- **Valuer name + valuation date** disclosed per deal (Newmark for Dover; CBRE @25 Nov 2025 for Wallingford; CBRE @31 Dec 2024 for Albany) — recoverable.
- **Triple-equality** (carrying = fair value = sale price) plus a separate printed loss is a clean case for keeping `carrying_value`, `valuation`, `gross_sale_price`, `net_sale_proceeds`, `gain_on_divestment` as *independent* columns — do not derive any from the others.
