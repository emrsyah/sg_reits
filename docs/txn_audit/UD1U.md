# UD1U.SI — IREIT Global — FY2025 property-transaction audit

**FY-END:** 2025-12-31 (window 1 Jan–31 Dec 2025; cash-flow header p178 "For the year ended 31 December 2025"). **Rows:** 1 (divestment). **Verdict: row verified correct — carrying_value NULL re-confirmed; deal_fy_scope = prior_year. No corrections.**

Sources: cash-flow statement + Note A **p178**, Statement of Portfolio **p179–181**.

## The deal
**Il·lumina** (Spain) — agreed by conditional promissory SPA on **22 Dec 2023** with an **unrelated (unnamed) third party**; divestment **completed 31 Jan 2024** for a sale consideration of **€24.5 million** (p178 Note A). This is a **FY2024** transaction; it surfaces in the FY2025 report only as the **2024 comparative column** of the cash-flow statement.

## Per-column null/value status
| column | value | verified | source |
|-|-|-|-|
| transaction_type / status | divestment / completed | ✓ | p178 Note A |
| transaction_date | 2024-01-31 | ✓ | p178 Note A "completed … on 31 January 2024" |
| consideration | €24,500,000 | ✓ | p178 Note A "sale consideration of €24.5 million" |
| net_proceeds | €24,500,000 | ✓ (= consideration; see nuance) | p178 CF "Proceeds from disposal of assets/liabilities held for sale" 2024 col = **24,500** |
| gain_on_divestment | −€224,000 (loss) | ✓ | p178 CF add-back "Loss on disposal of assets/liabilities held for sale" 2024 col = **224** |
| carrying_value | **null** | ✓ **RE-CONFIRMED** | not printed anywhere (see below) |
| currency | EUR | ✓ | p178 (EUR'000) |
| counterparty | unnamed unrelated third party | ✓ | p178 Note A "an unrelated third party" |
| valuation | null | ✓ | no independent deal valuation disclosed |

### carrying_value NULL — re-confirmation (Round-8 hardening upheld)
The prior value 24,724,000 was a **derived** figure (proceeds 24,500 + loss 224) and is **not printed** in the FY2025 AR. Re-verified this pass:
1. **Text search** for `24,724` / `24724` across the full report → **zero matches**. The number does not exist in the source.
2. **Statement of Portfolio (p179–181)** lists every held property by geography. The **Spain** section (p179) contains only **Delta Nova IV, Delta Nova VI, Sant Cugat Green, Parc Cugat** — **Il·lumina is absent from both the 2025 AND 2024 carrying columns** (it was divested Jan 2024, so it never appears). No Il·lumina carrying value is printed.
3. **Only two Il·lumina figures are printed** (p178, in the 2024 comparative column): proceeds **€24,500k** and loss **€224k**. No carrying / book value / valuation.
4. Per invariant 3 (never derive; leave carrying null when only sale price/proceeds are printed) → **carrying_value = null is correct.** ✓

*Nuance on net_proceeds:* the €24,500k in the cash-flow "Proceeds from disposal" line **equals** the gross sale consideration (€24.5m, Note A) — no separately-disclosed net-of-cost proceeds exist. So `consideration` and `net_proceeds` carry the same €24.5m; there is no distinct net figure. (Flag, not a correction.)

## This-FY timeline
| property | type | date | deal_fy_scope | as-reported gain/premium | use-of-proceeds |
|-|-|-|-|-|-|
| Il·lumina | divestment | 2024-01-31 | **prior_year** | **loss −€224k** on disposal (p178) | n/a — prior-year comparative; not discussed in FY2025 narrative |

### deal_fy_scope classification (the assignment's explicit question)
**prior_year** — the divestment **completed 31 Jan 2024**, i.e. within **FY2024** (IREIT FY-end 31 Dec). Relative to the FY2025 window (1 Jan–31 Dec 2025) it is a completed earlier-FY deal carried only in the **2024 comparative** column (2025 column shows "-"). It is **NOT** `subsequent_event`: "subsequent" would mean after the FY2025 balance-sheet date (31 Dec 2025). The note's phrase "Subsequent to the reporting date … 31 January 2024" is verbatim carry-over describing the *FY2023* reporting date (31 Dec 2023) and does not make it a FY2025 subsequent event. **No FY2025 acquisitions or divestments occurred** (Statement of Portfolio 2025 vs 2024 shows the same asset set; changes are fair-value movements only).

## Corrections proposed
**None.** transaction_date, consideration (€24.5m), gain (−€224k), currency (EUR), counterparty (unnamed third party) all match p178. carrying_value correctly null.

## Suggestions / raw material for design report
- **DPU linkage:** none — the deal booked a small **loss** (€224k), so no gain to distribute; and it is a prior-year item not featured in FY2025 distribution narrative. `distributed_gain = false`.
- **Use-of-proceeds:** not disclosed in the FY2025 report (prior-year comparative); the €24.5m proceeds were received in FY2024.
- **Coverage / modelling notes:**
  - This row is a **prior-year comparative artefact** — a FY2024 completed deal appearing in a FY2025 filing. A `deal_fy_scope`/as-of-FY flag is essential so downstream FY2025 divestment tallies are **not** inflated by it.
  - `net_proceeds` == `consideration` (both €24.5m); no distinct net-of-cost figure exists — consider nulling one to avoid implying two independent disclosures.
  - **agreement date (22 Dec 2023) and completion date (31 Jan 2024) both printed** (p178 Note A) — table captures only one date.
  - Counterparty genuinely undisclosed ("unrelated third party"); no independent deal valuation disclosed — both correctly null.

```json
{"sym":"UD1U","fy_end":"2025-12-31",
 "corrections":[],
 "confirmed_null":{
   "carrying_value":"RE-CONFIRMED null p178: only proceeds €24,500k + loss €224k printed (2024 comparative); Il·lumina absent from Statement of Portfolio p179-181 (divested Jan 2024); no '24,724' anywhere; prior derived 24,724,000 correctly removed (invariant 3)",
   "valuation":"no independent deal valuation disclosed for Il·lumina",
   "counterparty_name":"genuinely undisclosed — 'an unrelated third party' (p178 Note A)"},
 "timeline":[
   {"property":"Il·lumina","type":"divestment","date":"2024-01-31","scope":"prior_year"}],
 "gain_as_reported":[
   {"property":"Il·lumina","gain_or_premium":"loss −€224k on disposal of assets/liabilities held for sale (2024 comparative)","page":178}],
 "proceeds_use":[
   {"property":"Il·lumina","use":"general","distributed_gain":false,"verbatim":"not disclosed in FY2025 report — prior-year (FY2024) comparative item; deal booked a €224k loss","page":178}],
 "coverage_gaps":[
   "prior-year (FY2024) comparative artefact in a FY2025 filing — deal_fy_scope flag required so FY2025 divestment tallies exclude it",
   "net_proceeds == consideration (both €24.5m); no distinct net-of-cost figure printed",
   "agreement date 22 Dec 2023 and completion date 31 Jan 2024 both printed (p178) but only one date captured",
   "counterparty unnamed and no independent deal valuation — correctly null"]}
```
