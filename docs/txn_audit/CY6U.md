# CY6U.SI — CapitaLand India Trust (CLINT) — FY2025 property-transaction audit

FY-end: **2025-12-31**. Rows audited: **2** (both divestments). All figures printed in SGD in the source (INR headline shown alongside; JSON keeps the as-reported SGD equivalent).

## Row 1 — CyberPearl, Hyderabad & CyberVale, Chennai (divestment, completed)

Divested via indirect subsidiary CITPPL (dormant subs *CyberVale IT Parks P/L* + *Cyber Pearl Business Parks P/L*). Subsidiary/disposal-group disposal — this is NOT a bare property sale.

| Column | JSON value | Verdict | Source |
|---|---|---|---|
| type / status | divestment / completed | ✅ correct | "completed... 29 September 2025" (p13/p35 line 775/2202); "divestment was completed on 29 September 2025" (Note 25a, p146) |
| transaction_date | 2025-09-29 | ✅ correct | p146 disposal table header "29 September 2025"; p13 line 775 |
| deal_fy_scope | (current_fy) | ✅ completed inside FY2025 window | p146 |
| consideration (gross) | 161,700,000 SGD | ✅ correct | "enterprise value of INR 11,031 million (approximately S$161.7 million)" p35 (line 2202) |
| net_proceeds | 159,922,000 SGD | ✅ correct — genuinely printed | Note 25a "Net sales consideration after divestment expenses 159,922" (p146 line 6407) |
| gain_on_divestment | 4,081,000 SGD | ✅ correct — genuinely printed | Note 25a "Gain on divestment 4,081" (p146 line 6406); also "Gain on disposal group classified as held for sale 4,081" in Statement of Total Return (Note 25) |
| carrying_value | 138,890,000 SGD | ⚠️ genuine but easily misread — see note | Note 25a "Investment properties under construction and investment properties 138,890" @ 29 Sep 2025 (p146 line 6396) |
| valuation | null | ✅ confirmed null | No $ deal valuation printed; only "3% premium to independent valuation" (p35) |
| counterparty | null | ✅ confirmed — buyer not named | p146 line 6384 "were divested together" (no buyer named anywhere) |

**carrying_value nuance (NOT a correction — both figures genuine):** 138,890 is the *investment-properties* line of the disposal group at the disposal date. The gain (4,081) was struck against **Net assets of disposal group S$155,841k**, i.e. 159,922 − 155,841 = 4,081 (p146 lines 6405–6407). So `carrying_value=138,890` does **not** reconcile the gain; the reconciling "carrying" here is the net-asset figure 155,841 (a disposal-group net-asset base, not a property carrying value). The existing `carrying_value_basis` already documents this. Keep 138,890 as the printed property carrying value; do NOT swap in 155,841 (different basis). Related FX item: S$20,252k "Foreign currency translation loss from divestment" was also expensed on completion (p146/p147).

## Row 2 — 20.2% stake in three data-centre developments (DC ITPH, DSRPL/DC Navi Mumbai, DC Chennai) (divestment, completed post-FY)

| Column | JSON value | Verdict | Source |
|---|---|---|---|
| type / status | divestment | ✅ (partial divestment — 20.2% of three subs; CLINT retains 79.8%) | p35 line 2204; p147 Note 25b line 6429 |
| transaction_date | 2026-02-27 | ✅ correct | "completion of the divestment... as announced on SGXNET on 27 February 2026" (p35 line 2256; p36 line 2913) |
| deal_fy_scope | **subsequent_event** | ✅ correct — SPA executed 30 Dec 2025, completed 27 Feb 2026 (after 2025-12-31) | p147 line 6429 "On 30 December 2025... entered into securities purchase and subscription agreements"; completion 27 Feb 2026 |
| consideration (gross) | 99,700,000 SGD | ✅ correct | "approximately INR 7,021 million (S$99.7 million)" p35 line 2204 |
| counterparty | CapitaLand India Data Centre Fund Pte. Ltd. (CIDCF) | ✅ correct | p147 line 6429 |
| net_proceeds | null | ✅ confirmed null — subsequent event, figures "indicative and subject to adjustment" | p16 line 1213 / p15 line 945 |
| gain_on_divestment | null | ✅ confirmed null — no FY2025 gain (post-balance-sheet completion) | p147 |
| carrying_value | null | ✅ confirmed null — see note | p147 Note 25b line 6444–6452 |
| valuation | null | ✅ confirmed null — no independent $ appraisal printed | "13.7% premium to their independent valuation" only (p35 line 2204); disposal group "valued based on the agreed property value with the buyer" (p147 line 6435) |

**carrying_value null is correct.** At 31 Dec 2025 the FULL 100% of the three subsidiaries was classified as a disposal group at fair value (IFRS 5): Investment properties under construction 649,592 + Investment properties 88,930, **Net assets of disposal group 463,350** (p147 lines 6444–6452). No per-20.2%-stake carrying value is printed; taking 20.2% of 463,350 would be a prohibited derivation. Confirm null.

## This-FY timeline

| property | type | date | deal_fy_scope | as-reported gain / premium | use-of-proceeds |
|---|---|---|---|---|---|
| CyberPearl + CyberVale | divestment (completed) | 2025-09-29 | current_fy | **gain S$4.081m**; sold at **3% premium to independent valuation** (p35) | capital-recycling; "improve its gearing" / "enhancing financial flexibility" (p35 line 2202, p13 line 777) — no explicit gain-distribution |
| 20.2% DC stake → CIDCF | partial divestment (completed) | 2026-02-27 (SPA 2025-12-30) | subsequent_event | **13.7% premium to independent valuation** (p35); no $ gain booked in FY2025 | "unlocking value during the development lifecycle while retaining a majority 79.8% stake" (p35 line 2204) |

## Corrections proposed
**None.** All typed values and all nulls verified genuine against the source. `carrying_value=138,890` (Row 1) is retained with the existing basis note (see nuance above).

## As-reported profit-from-divestment (raw material)
- Row 1: **S$4.081m gain** (Note 25a, p146) AND "3% premium to independent valuations" (p35).
- Row 2: **"13.7% premium to their independent valuation"** (p35) — premium-% only; no $ gain in FY2025 (subsequent event).

## Use-of-proceeds / DPU linkage
- Framed as **capital recycling** to "improve gearing" and "enhance financial flexibility" (p13/p35). **No statement that any divestment gain was distributed to unitholders** → `distributed_gain=false` for both rows. (A final dividend of S$7/share = S$7,000,000 at the *Trust company* level, p148 note 16, is unrelated to divestment-gain distribution.)

## Suggestions / coverage gaps
- **Subsidiary-disposal semantics:** for share/subsidiary disposals (both rows), the reconciling "carrying" is *net assets of disposal group* (155,841; 463,350), distinct from the property IP line (138,890). Table has one `carrying_value` column and cannot express both; the basis note is doing the heavy lifting. Consider a `disposal_basis` flag (asset vs share/subsidiary) so gain↔carrying reconciliation is not silently broken.
- **Premium-only disclosure is the norm here:** both deals disclose "% premium to independent valuation" but no independent-valuation $ figure and (Row 2) no $ gain. Our `valuation` and `gain_on_divestment` cannot capture premium-%; a `premium_pct` / `premium_benchmark` field would be recoverable and high-value.
- **Stake %** (20.2% divested / 79.8% retained) and **agreement-vs-completion dates** (SPA 30 Dec 2025 vs completion 27 Feb 2026) are disclosed but not captured.
