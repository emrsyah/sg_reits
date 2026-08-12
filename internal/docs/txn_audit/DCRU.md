# DCRU.SI — Digital Core REIT — FY2025 property-transaction audit

FY-end: **2025-12-31**. Rows audited: **1** (acquisition). Figures in USD and JPY as printed.

## Row 1 — Digital Osaka 3 (KIX12) — acquisition of 20% interest (completed)

Acquired via wholly-owned sub *Digital CR Singapore 4 Pte. Ltd.* → *Digital Osaka 3 TMK*; equity-accounted (20% interest, JV/associate structure). Debt-funded.

| Column | JSON value | Verdict | Source |
|---|---|---|---|
| type / status | acquisition / completed | ✅ correct | "completed the acquisition on 25 March 2025" (p31 line 1406); Note "On 26 March 2025, the Group completed the acquisition of a 20.0% equity interest in Digital Osaka 3 TMK" (p186 line 6776) |
| interest_acquired_pct | 20.0 | ✅ correct | p28/p34/p186 (20.0%) |
| completion_date | 2025-03-25 | ✅ correct (AR internally: 25 Mar p31 / "26 March" in the subsidiaries note p186) | p31 line 1406 "completed the acquisition on 25 March 2025" |
| deal_fy_scope | (current_fy) | ✅ completed inside FY2025 (Mar 2025) | p31 |
| consideration | 86,700,000 USD | ✅ correct | "¥13 billion (approximately US$86.7 million)" (p28 line 1228); p34 line 1523 |
| consideration_local | 13,000,000,000 JPY | ✅ correct | "¥13,000 million (approximately US$86.7 million)" (p34 line 1523) |
| valuation | 65,390,000,000 JPY | ✅ correct — **100%-share basis** | "valued at ¥65,390 million (100% share) as at 15 March 2025" by Newmark V&A (p34 line 1525) |
| valuation_basis | Newmark V&A, 100% share, 15 Mar 2025, cost/sales-comparison/income-cap | ✅ correct | p34 line 1525 |
| counterparty | Mitsubishi Corporation | ✅ correct | "from a third-party vendor, Mitsubishi Corporation" (p28 line 1228; p34 line 1523) |
| carrying/gain/net | — | ✅ n/a for acquisition | — |

**Basis-mismatch caution (not a correction):** the **consideration ¥13,000m is for the 20% interest**, while the **valuation ¥65,390m is 100%-share** (≈¥13,078m at 20%). These are on different bases; they must NOT be compared 1:1 as "price vs valuation". The `valuation_basis` field correctly flags "100% share" — keep it explicit so no one reads a spurious ~5× discount. Separately, the AR also prints a **20%-ownership-interest valuation of US$90.0m as at 31 Dec 2025** (p31 line 1388; property page p43 line 2298) and the carrying value of the investment ¥27,383m (p186 line 6778) — different date/basis from the acquisition valuation captured here.

## This-FY timeline

| property | type | date | deal_fy_scope | as-reported gain / premium | funding / use |
|---|---|---|---|---|---|
| Digital Osaka 3 (20% int.) | acquisition (completed) | 2025-03-25 | current_fy | n/a (acquisition); **~1.8% / 180bps DPU accretion** (p28 line 848; p34 line 1525) | **debt-funded** — JPY borrowings incl. inaugural ¥10bn EMTN bond (p28 line 1228; p32 line 1327/1329) |

## Corrections proposed
**None.** All typed values and currency tags verified. valuation correctly tagged 100%-share via `valuation_basis`.

## As-reported profit-from-divestment (raw material)
- N/A — sole transaction is an acquisition. Accretion metric disclosed: **~1.8% (180bps) DPU accretion** (p28/p34).

## Use-of-proceeds / DPU linkage
- Not a divestment → no proceeds to deploy. Acquisition **debt-funded** (US$750m EMTN programme; inaugural ¥10bn EMTN bond; JPY-denominated borrowings), lifting aggregate leverage from 34.0%→37.1% (p32 line 1327/1329/1497). DPU impact: **+1.8% accretion** attributed to the acquisition. `distributed_gain=false` (no divestment).

## Suggestions / coverage gaps
- **Valuation-basis field is essential** for fractional-interest deals (100%-share vs interest-basis) — this row is a model case; enforce it wherever `interest_acquired_pct` < 100.
- **Multiple valuation figures per asset** (acquisition-date 100% JPY appraisal vs year-end 20%-interest US$ valuation) — a `valuation_date` + `valuation_scope` pair would disambiguate.
- **DPU-accretion %** and **funding source (debt/equity)** disclosed but uncaptured; both are high-value for acquisition rows.
- **Ownership vehicle / equity-method flag** (TMK, 20% associate) disclosed — worth a structural tag.
