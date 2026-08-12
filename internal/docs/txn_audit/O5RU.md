# O5RU.SI — AIMS APAC REIT — FY2025 property-transaction audit

**FY-END:** 2025-03-31 (window 1 Apr 2024–31 Mar 2025). **Rows:** 1 (1 announced/pending divestment). **Verdict: price/carrying/dates/nulls all verified correct; carrying==sale-price is GENUINE (held-for-sale IP stated at agreed sale price). Two soft suggestions: type → `announced_divestment` for taxonomy consistency; capture gross-vs-net (S$25.006m incl ROU).**

Sources: CEO/strategy review + "32.5% premium" **p13, p17, p18**; Portfolio Statement (agreed sale price as valuation) **p53**; Statement of Financial Position (held-for-sale S$25,006k / lease liability S$618k) **p157**; Note 4 held-for-sale footnote (announced 10 Dec 2024) **p164**; investment-property note (completion targeted 1H2025) + fair-value hierarchy (Level 2, agreed sale price) **p192**.

## Per transaction row — 3 Toh Tuck Link, announced 10-Dec-2024

- **type / status:** JSON `divestment` + `pending_completion`. **Facts:** announced 10 Dec 2024, reclassified to *investment property held for sale* at 31 Mar 2025, **targeted completion 1H2025** (post FY-end) (p164, p192). *Soft suggestion:* for taxonomy parity with J91U, `type` could be **`announced_divestment`** (announced-but-not-completed at FY-end); current `divestment`+`pending_completion` conveys the same substance. ✓ substance correct.
- **transaction_date / announced_date:** `announced_date` = 2024-12-10 ✓ ("On 10 December 2024, the Group announced the proposed divestment … at a sale price of S$24.388 million", p164/p192). **deal_fy_scope = subsequent_event** — announcement in-FY, but completion (1H2025) and any gain are **post-31-Mar-2025 FY-end**; held-for-sale on the FY2025 balance sheet, gain NOT recognised in FY2025.
- **price = 24,388,000 (SGD)** ✓ — "sale price of S$24.388 million" (p164, p192). Correct.
- **carrying_value = 24,388,000 (SGD)** ✓ **GENUINE, not a sale-price copy-error.** Held-for-sale investment property is *"stated at fair value based on the agreed sale price with a third-party buyer"* (Level 2 hierarchy, p192; p53 fn2; p164 fn) → the property's fair-value carrying **legitimately equals** the agreed sale price (24,388k). The Fair Value note prints exactly: *"Fair value of investment property held for sale (based on agreed sale price) 24,388"* (p192). So carrying = price = 24,388 is required by the accounting policy, not a conflation.
  - **Gross-vs-net nuance (both printed):** the balance-sheet line *"Investment property held for sale"* = **S$25,006k** (GROSS, incl. right-of-use asset S$618k), with an offsetting *"Liabilities directly associated …"* lease liability **S$618k** (p157/p192). Net = 25,006 − 618 = **24,388** = the recorded carrying (excl ROU). The JSON `carrying_value_basis` already documents this correctly ("net of S$0.618m lease liability, gross S$25.006m").
- **valuation = NULL** — **CONFIRMED genuinely absent.** No independent-valuation dollar figure is printed for 3 Toh Tuck (it is carried at the agreed sale price, Level 2, p192). The only value-vs-valuation signal is the **"32.5% above valuation / 32.5% premium over valuation"** narrative (p13/p17/p18) — a percentage, no pre-sale valuation $ printed. Do NOT back-solve the implied ~S$18.4m valuation. ✓
- **gain_on_divestment = NULL** — **CONFIRMED.** Completion is post-FY, so **no gain recognised in FY2025** — Financial Review + Cash-Flow "Gain on divestment of investment property" = **nil FY2025** (S$637k in FY2024, from 541 Yishun, prior year) (p32 Financial Review; p169 cash-flow). As-reported profit signal is the **32.5% premium over valuation** (p13/p17/p18).
- **counterparty / buyer = NULL** — **CONFIRMED genuinely unnamed.** Source consistently says *"a third-party buyer"* (p53/p126/p164/p192) without naming. ✓
- **net_sale_proceeds = NULL** — confirmed absent (no net-of-cost figure printed for 3 Toh Tuck).
- **currency = SGD** ✓ (Singapore asset).

## This-FY timeline

| property | type | date | deal_fy_scope | as-reported gain/premium | use-of-proceeds |
|-|-|-|-|-|-|
| 3 Toh Tuck Link | announced/pending divestment | announced 2024-12-10 (target completion 1H2025) | subsequent_event | **32.5% above valuation / 32.5% premium** (S$24.4m sale price) (p13/p17/p18) | **repay debt (interim) + may be reinvested** into growth initiatives / AEIs / redevelopment (p13/p17/p18) |

## Corrections proposed
**None (hard).** price, carrying (net & gross bases), announced_date, currency, and all nulls (valuation, gain, counterparty, net proceeds) verified against source.
Soft suggestions: (1) `type` → `announced_divestment` for cross-report taxonomy consistency; (2) capture the gross held-for-sale carrying S$25,006k (incl ROU S$618k) alongside the net S$24,388k.

## Suggestions / raw material for design report
- **DPU / distributed_gain = false** for 3 Toh Tuck (gain not recognised — completion post-FY). No distribution of this divestment's gain disclosed. (For context, prior-year 541 Yishun gain S$637k was recognised in FY2024, out of window; AA REIT's mechanism for distributing capital gains is not detailed for 3 Toh Tuck.)
- **Use-of-proceeds explicitly disclosed:** *"Upon the asset sale, proceeds will be utilised to repay debt in the interim and may be recycled into new growth opportunities"* (p13); *"net proceeds from this divestment may be reinvested to support AA REIT's various growth initiatives"* (p17). Capture as `repay_debt` + `reinvest`.
- **Strong as-reported premium signal:** "**32.5% above valuation**" is one of the largest premia in this batch — high-value raw material for a premium/discount design field, even though the $ valuation is null.
- **Coverage gaps:**
  - **Gross (S$25,006k incl ROU) vs net (S$24,388k) held-for-sale carrying** both printed (p157) — only net captured.
  - **Pre-sale independent valuation** is only expressible as "32.5% above" — the $ figure (~S$18.4m) is NOT printed; a `premium_pct` field would capture the as-reported signal without deriving.
  - **Buyer genuinely unnamed** ("third-party buyer") — correct null, but note the option/agreement structure and buyer identity are undisclosed.
  - **Target completion window (1H2025)** disclosed (p192) but not captured.

```json
{"sym":"O5RU","fy_end":"2025-03-31",
 "corrections":[
   {"record":"3 Toh Tuck Link","field":"type","current":"divestment","proposed":"announced_divestment","page":164,"kind":"relabel","evidence":"Announced 10 Dec 2024, reclassified held-for-sale at 31 Mar 2025, completion targeted 1H2025 (post FY-end) — not completed in FY2025; announced_divestment matches J91U taxonomy. Soft/optional; status 'pending_completion' already conveys substance."},
   {"record":"3 Toh Tuck Link","field":"carrying_value_gross","current":null,"proposed":25006000,"page":157,"kind":"fill","evidence":"Balance-sheet 'Investment property held for sale' = S$25,006k gross (incl ROU S$618k), lease liability S$618k (p157/p192); recorded carrying 24,388k is net-of-ROU. Optional gross-basis capture; net 24,388k is correct as-is."}],
 "confirmed_null":{
   "valuation":"no independent valuation $ printed; property carried at agreed sale price (Level 2, p192); only '32.5% above valuation' % disclosed (p13/p17/p18) — do not back-solve",
   "gain_on_divestment":"completion post-FY (1H2025) → no gain recognised FY2025; Financial Review p32 + cash-flow p169 'Gain on divestment' nil FY2025 (S$637k FY2024, 541 Yishun prior year); as-reported = 32.5% premium",
   "counterparty":"genuinely unnamed — source says 'a third-party buyer' throughout (p53/p126/p164/p192)",
   "net_sale_proceeds":"no net-of-cost proceeds figure printed for 3 Toh Tuck"},
 "timeline":[
   {"property":"3 Toh Tuck Link","type":"announced_divestment","date":"2024-12-10","scope":"subsequent_event"}],
 "gain_as_reported":[
   {"property":"3 Toh Tuck Link","gain_or_premium":"32.5% above valuation / 32.5% premium over valuation (sale price S$24.4m)","page":13}],
 "proceeds_use":[
   {"property":"3 Toh Tuck Link","use":"repay_debt","distributed_gain":false,"verbatim":"Upon the asset sale, proceeds will be utilised to repay debt in the interim and may be recycled into new growth opportunities (p13); net proceeds may be reinvested to support AA REIT's various growth initiatives (p17)","page":13}],
 "coverage_gaps":[
   "gross held-for-sale carrying S$25,006k (incl ROU S$618k) vs net S$24,388k both printed (p157) — only net captured",
   "pre-sale independent valuation expressible only as '32.5% above' — $ figure not printed; a premium_pct field would capture it without deriving",
   "target completion window 1H2025 (p192) not captured",
   "buyer genuinely unnamed + put/call option agreement structure undisclosed"]}
```
