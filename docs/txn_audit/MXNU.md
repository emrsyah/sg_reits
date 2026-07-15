# MXNU.SI — Elite UK REIT — property-transaction audit (FY2025, FY-END 2025-12-31)

Source: `parsed_reports_datalab/14_MXNU.SI_Elite-UK-REIT_FY2025/full.md`.
5 rows: 1 acquisition (3 govt-leased properties) + 4 UK vacant-asset divestments.
**Assignment core check — CONFIRMED:** the 4 divestments share a COMBINED FY2025 net proceeds
**GBP 5,670,000** (Cash Flow, p136) and COMBINED net loss **GBP 80,000** (Statement of Total Return,
p134); neither is split per property, and the JSON correctly stores NO per-deal net_sale_proceeds and
NO per-deal gain_on_divestment. Verified good.

## Per-column null/value status

### Acquisition — Custom House / Merlin House / Priory Court (Elite Phoenix Ltd)
- `purchase_price` GBP 9,200,000 — **correct**. Acquisitions table total "9.2" (p25); narrative "£9.2 million" (p13/p25); IPT Note 32.
- `valuation` GBP 10,700,000 — **correct**. Acquisitions table total valuation "10.7" (p25, Colliers as at 31 Dec 2025; Custom 3.7 / Merlin 2.3 / Priory 4.7).
- `cost_recognised` GBP 9,644,000 — **correct, and correctly distinct from purchase_price**. Note 4 "Acquisition during the year 9,644" (p148); = cash outflow (incl. transaction costs). No gross↔cost conflation.
- `date` 2025-06-01 — **MISLABEL (fix)**. Acquisitions table completion date is **20 Jun 25** (all three, p25). Propose 2025-06-20.
- carrying/gain/net — N/A (acquisition). Correct.

### Divestments (Crown Buildings, Hilden House, St Paul's, Victoria Road)
- `price` (divestment price) — **all correct** vs Divestments table (p26): Crown 0.7, Hilden 3.3, St Paul's 1.6, Victoria 0.3 (£m).
- `valuation` — **all correct** vs Divestments table (p26): Crown 0.6, Hilden 3.1, St Paul's 1.4, Victoria 0.5 (£m).
- `carrying_value` — **PROBLEM (see corrections).** The FY2025 report prints per-property carrying for NONE of the four. Note 4 (p148) prints only two COMBINED figures: `Reclassification to assets held for sale (4,650)` for 2024 (= Hilden + St Paul's) and `Divestments during the year (1,100)` for 2025 (= Crown + Victoria). The JSON's per-property splits come from the **FY2024 Annual Report** (a different document), except **Hilden 3,300 which is a pure derivation** (4,650 − 1,350).
- per-deal `net_sale_proceeds` — **genuinely null** (only combined GBP 5,670,000, p136).
- per-deal `gain_on_divestment` — **genuinely null** (only combined net loss GBP 80,000, p134; only combined "average 5% premium" to valuation, p13/p25).
- `counterparty` — all correct (p26): Trivallis Ltd, Caro Developments Ltd, Abode & Co Holdings Limited, Alex Penman.

## This-FY timeline

| property | type | date | deal_fy_scope | as-reported gain/premium | use-of-proceeds |
|---|---|---|---|---|---|
| Custom House / Merlin House / Priory Court | acquisition | 2025-06-20 | current_fy | bought 7.6% below avg independent valuation (p13); 9.2 vs 10.7 valn (p25) | funded by £4.0m placement + divestment proceeds |
| Crown Buildings, Caerphilly | divestment | 2025-03-03 | current_fy | (combined only) | finance Jun-2025 acq + reduce debt |
| Hilden House, Warrington | divestment | 2025-05-14 | current_fy | (combined only) | net proceeds part-funded Jun-2025 acq (p13) |
| St Paul's House, Chippenham | divestment | 2025-07-18 | current_fy | (combined only) | finance acq + reduce debt |
| Victoria Road, Kirkcaldy | divestment | 2025-07-29 | current_fy | (combined only) | finance acq + reduce debt |

Combined 4-divestment result (as reported): **net loss GBP 80,000** (P&L p134) but **average 5% premium
to valuation** (p13/p25) — two different comparison bases (loss vs book/carrying; premium vs valuation).
NEVER combine these.

## Corrections proposed (page cites — main agent re-verifies)
1. **Acquisition `date` 2025-06-01 → 2025-06-20** (kind: fix). Acquisitions table completion date "20 Jun 25", p25.
2. **Hilden House `carrying_value` 3,300,000 → null** (kind: fix). Derived/balanced figure: combined held-for-sale carrying GBP 4,650k (Note 4, p148) minus St Paul's GBP 1,350k (FY2024 AR, not this report). No per-property carrying is printed in the FY2025 report; the value also circularly equals the sale price GBP 3.3m. Violates the no-derivation invariant.
3. **St Paul's 1,350,000 / Crown 600,000 / Victoria 500,000 `carrying_value` — provenance flag** (kind: fix/verify). Sourced from the **FY2024 Annual Report** portfolio statement (external doc), not the FY2025 report; FY2025 prints only the combined 4,650 (p148) and 1,100 (p148). If same-report provenance is required, these are null-in-this-report; otherwise verify against the FY2024 AR.

## Suggestions / raw material
- **DPU-boost:** none. FY2025 divestments produced a net LOSS (GBP 80k), so no divestment gain was distributed. Proceeds went to the June-2025 acquisition and debt reduction (p13). `distributed_gain=false`.
- **Recoverable:** per-deal completion dates, purchasers, divestment prices and valuations are all cleanly per-deal in the Divestments table (p26). Per-deal net proceeds / gain / carrying are NOT recoverable from this report (combined-only) — do not fabricate them.
- **Coverage:** the report gives premium-to-valuation only as a portfolio average (5%), never per deal; and carrying only as two combined line items (p148).
