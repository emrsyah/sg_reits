# BUOU.SI — Frasers Logistics & Commercial Trust — property-transaction audit (FY2025, FY-END 2025-09-30)

Source: `parsed_reports_datalab/19_BUOU.SI_Frasers-Logistics-and-Commercial-Trust_FY2025/full.md`.
3 rows: acquisition (2 Tuas South Link 1) + divestment (357 Collins St) + partial_divestment (28 German
properties minority-interest sale). FY window = 1 Oct 2024 → 30 Sep 2025.
**Assignment core check — CONFIRMED:** the 28-German partial has carrying_value GENUINELY ABSENT — it is
an IFRS-10 change-in-ownership-interest (NCI sale) recognised directly in equity, not a P&L property
divestment; no property carrying is derecognised and no gain is recognised. Verified good.

## Per-column null/value status

### Acquisition — 2 Tuas South Link 1 (Singapore)
- `purchase_price` SGD 140,300,000 — **correct**. Property Highlights "Purchase Price $140.3 million" (p37).
- `valuation` SGD 143,800,000 — **correct**. "Appraised Value on Acquisition $143.8 million (Knight Frank Pte Ltd)" (p37).
- `date` 2024-11-05 — **correct**. "5 November 2024" (Portfolio Statement p... / narrative "November 2024"), current_fy.
- `counterparty` Diamond Land Pte. Ltd. — **correct** (p37/narrative "purchased from Diamond Land Pte. Ltd.").

### Divestment — 357 Collins Street (Australia)
- `price`/`sale_consideration` AUD 192,100,000 — **correct**. "Divestment Consideration A$192.1 million" (p37).
- `valuation` AUD 191,000,000 — **correct**. "Appraised Value on Divestment A$191.0 million (Savills Valuations Pty Ltd)" (p37); Savills as at 1 Jun 2025.
- `gain_on_divestment` SGD 180,000 — **correct**. "Gain on divestment of investment properties 180" in the Statement of Total Return (p119); it is the ONLY FY2025 IP-divestment gain line, and 357 Collins was the only IP divestment → attribution sound (single printed figure, not derived).
- `carrying_value` SGD 162,052,000 — **correct**. Note 10 investment-property movement "Disposal of investment properties (162,052)"; 357 Collins was the sole IP disposal in FY2025.
- `net_sale_proceeds` — **genuinely null** (per-deal net proceeds not separately disclosed).
- `date` 2025-09-30 — **correct**. "On 30 September 2025, we completed the divestment" (p33); completed on the FY-end date → current_fy.

### Partial divestment — 28 German properties (minority-interest sale)
- `sale_consideration`/`price` SGD 33,414,000 — **correct**. "sale consideration of S$33,414,000" (p177, Note); "€23.2 million (approximately $33.4 million)" (p36); equity statement "Divestment of ownership interests to non-controlling interests ... 33,414" (p122).
- `appraised_value` null — **genuinely absent**. Consideration "took into account the valuations of the properties" (p36) but no separate appraised-value figure is printed.
- `carrying_value` (absent) — **genuinely absent / CORRECT**. IFRS-10 equity transaction (effective interest reduced to 89.9%, a 3.2%–5.0% reduction) recognised in equity; the S$746k difference attributable to Unitholders sits in the equity statement (p122). No property carrying is derecognised.
- `gain_on_divestment` (absent) — **genuinely absent / CORRECT**. Equity transaction; no P&L gain.
- `counterparty` — **correct**: Fraser's Property Investments (Europe) B.V., FPI Netherlands B.V. and Stichting Coeval (existing minority shareholders) (p36).
- `date` 2024-11-28 — **correct** (completed 28 Nov 2024; announced 7 May 2025), current_fy.

## This-FY timeline

| property | type | date | deal_fy_scope | as-reported gain/premium | use-of-proceeds |
|---|---|---|---|---|---|
| 2 Tuas South Link 1 | acquisition | 2024-11-05 | current_fy | bought S$140.3m vs S$143.8m appraised (below valn) | debt-financed |
| 357 Collins Street | divestment | 2025-09-30 | current_fy | +0.6% premium to A$191.0m valn (p33); accounting gain S$180k (p119) | financial flexibility / rebalance to L&I; **gains distributed as capital distribution** |
| 28 German properties | partial_divestment | 2024-11-28 | current_fy | n/a (equity txn); S$746k diff to Unitholders in equity | NCI sale; proceeds to Group |

## Corrections proposed
None. All typed values verified against source; the two genuine nulls (28-German appraised_value and the
absent carrying/gain) are correct.

## Suggestions / raw material
- **DPU-boost — YES.** Capital-distribution note lists component **"(iv) distribution of divestment gains"**
  (p26); FY2025 capital distribution ≈ 0.74–0.80 Singapore cents of the 5.95-cent DPU (p26). So 357 Collins's
  divestment gain WAS distributed to unitholders as a capital distribution → `distributed_gain=true`. Strong
  DPU-linkage signal the table does not capture.
- **Coverage gaps:** valuer names + valuation dates printed (Knight Frank on acquisition; Savills 1 Jun 2025);
  357 Collins consideration also given in SGD-equivalent (≈S$160.4m); 28-German discloses stake reduction
  (to 89.9%, by 3.2–5.0%), equity impact (S$746k), and BOTH announcement (7 May 2025) and completion
  (28 Nov 2024) dates.
- **Recoverable:** none missing at value level; consider capturing the DPU/capital-distribution linkage.
