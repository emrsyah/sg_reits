# N2IU (Mapletree Pan Asia Commercial Trust / MPACT) — property-transaction audit — FY-END 2025-03-31

Stem: `29_N2IU.SI_Mapletree-Pan-Asia-Commercial-Trust_FY2025`. One row: Mapletree Anson divestment. FY2025 (FY24/25) window = 2024-04-01…2025-03-31. Physical `<!-- PAGE N -->` cites.

## Per-column null/value status — Mapletree Anson (divestment)
- **transaction_type / status:** divestment / completed. Correct.
- **transaction_date:** **completed 31 July 2024.** Correct — repeated throughout (PAGE 41 "completed on 31 July 2024"; PAGE 146 FS note).
- **gross_sale_price (JSON `sale_consideration`/`price` = 775,000,000 SGD):** VERIFIED. "cash consideration of $775,000,000" (PAGE 146 FS Note 14/15); "divestment consideration of S$775.0 million" (PAGE 41); Statement of P/L context (PAGE 107). Correct.
- **net_sale_proceeds (JSON `net_proceeds` = 762,448,000):** VERIFIED. Cash-flow: "Proceeds from divestment of an investment property, **net of transaction costs and transfer of tenants' security deposits** — 762,448" (PAGE 112). Genuinely distinct net figure. Correct.
- **gain_on_divestment (4,006,000):** VERIFIED as-reported. "Net gain on divestment of an investment property — 4,006" (Statement of Profit or Loss, Note 14, PAGE 107); "resulting in a net gain on divestment of $4,006,000" (Note 15 movement, PAGE 146); "S$4.0 million net divestment gain" (PAGE 21). Correct.
- **valuation (765,000,000):** VERIFIED as a **genuine independent valuation** — NOT a carrying copy. "the property's independent valuation of S$765.0 million as at 31 March 2024 … conducted by CBRE Pte. Ltd. using the income capitalisation method and discounted cash flow analysis" (PAGE 41); portfolio valuation table "At valuation as at 31/03/2024 — 765,000" (PAGE 117). Correct.
- **carrying_value (765,000,000):** VERIFIED as a **separately-printed carrying figure.** Investment-property movement note: "Divestment of an investment property (765,000)" (PAGE 146). Correct.
- **valuation == carrying (both 765,000): LEGITIMATE, not a conflation.** The property was carried at fair value, so its 31-Mar-2024 carrying = its 31-Mar-2024 independent valuation (765,000); divested 31-Jul-2024 with no interim revaluation. Both are separately and literally printed (valuation p41/p117; carrying p146). This is a genuine coincidence — the extraction is correct.
- **counterparty:** GES Tradewinds Pte. Ltd. (unrelated third party). Correct — named at PAGE 41 ("divestment to unrelated third party, GES Tradewinds Pte. Ltd."). Note: FS Note (p146) refers only to "an external party"; the buyer name lives at PAGE 41. Prior note documents this.

## This-FY timeline
| property | type | date | deal_fy_scope | as-reported gain/premium | use-of-proceeds |
|---|---|---|---|---|---|
| Mapletree Anson | divestment | 2024-07-31 (completed) | **current_fy** (within FY24/25 2024-04-01…2025-03-31) | Net gain **S$4,006k** (p107/p146); **+S$10.0m (≈+1.3%) above independent valuation S$765.0m**; **+S$95.0m above original purchase price S$680.0m** (p41) | Net proceeds "deployed to reduce debt" / "used to pare down debts" → leverage 40.5%→37.7%, finance costs −3.3% yoy (p6/p14/p41); loans repaid to MPACT TCo using proceeds (p155). **distributed_gain = false** — DPU accretion came from lower finance costs, NOT a distribution of the gain |

## Corrections proposed
- **None.** All money columns verified against source. The apparent valuation==carrying overlap is legitimate (two distinct, separately-printed 765,000 figures).

## Suggestions / coverage
- Report gives **three** as-reported profit framings — accounting net gain (S$4.0m), premium over valuation (+S$10.0m / +1.3%), premium over original purchase price (+S$95.0m / +14%). Our table stores only the accounting net gain. The design report should note these are NON-derivable from each other (net gain 4.0m ≠ consideration−carrying 10.0m because of transaction costs).
- Disclosed but uncaptured: original purchase price S$680.0m (acquired 4 Feb 2013), valuer name (CBRE Pte Ltd) + method (income cap + DCF), the precise net-proceeds label ("net of transaction costs AND transfer of tenants' security deposits").
- Strong DPU-linkage disclosure (repeated "DPU accretive"/"added to DPU") but purely via debt reduction → lower finance costs; no special/capital distribution of the gain.
