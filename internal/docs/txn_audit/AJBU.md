# AJBU.SI — Keppel DC REIT — property-transaction audit (FY2025, FY-END 2025-12-31)

Source: `parsed_reports_datalab/21_AJBU.SI_Keppel-DC-REIT_FY2025/full.md`.
1 row: divestment of Kelsterbach Data Centre (Frankfurt, Germany) to Fortinet GmbH.
**Assignment core checks — CONFIRMED:** Kelsterbach sold for **EUR 50.0m at a 28.2% premium** to its
31 Dec 2024 valuation of EUR 39.0m (Savills UK) — verified on **p36**; and `net_proceeds` is **GENUINELY
NULL** (re-confirmed, see below).

## Per-column null/value status
- `gross_sale_price` EUR 50,000,000 / `transaction_price_local` EUR 50,000,000 — **correct**. "divested to Fortinet GmbH for EUR 50.0 million" (p36); "divested Kelsterbach DC for a consideration of approximately $70.6 million" (p128).
- `transaction_price` SGD 70,600,000 — **correct, and correctly the GROSS consideration** (= EUR 50.0m converted). p128: "consideration of approximately $70.6 million". The round-7 relabel (was previously mislabelled as net) is verified correct — this is gross, not net.
- `valuation` EUR 39,000,000 — **correct**. "28.2% premium to its 31 December 2024 value of EUR 39.0 million by Savills (UK) Limited" (p36). Correctly distinct from sale price.
- `carrying_value_pre` SGD 55,041,000 — **correct**. Portfolio Statement, Kelsterbach 31 Dec 2024 carrying "55,041" (p110); carrying-value bar chart shows 55.0 (2024) / – (2025).
- `gain_loss` SGD 10,825,000 — **correct**. "Gain on divestment of an investment property 10,825" (Statement of Profit or Loss, p103; also cash-flow add-back p107 and distribution statement p109). As-reported accounting gain.
- `net_proceeds` null — **GENUINELY NULL / CORRECT**. No Kelsterbach-only net-of-cost proceeds figure is printed. The cash-flow line "Net proceeds from divestment of investment property **and investment in notes** (Note B) = S$65,475k" (p107) is explicitly COMBINED (Kelsterbach + notes/AU-DC-Note activity), NOT attributable to Kelsterbach alone; Note B prose says only "the net divestment proceeds were used to repay bank borrowings" with no figure (p107). Deriving Kelsterbach net from 65,475 would violate the no-derivation invariant.
- `counterparty` Fortinet GmbH — **correct** ("divested to Fortinet GmbH", p36).
- `completion_date` 2025-03-24 — **correct**. "completed the divestment of Kelsterbach DC on 24 March 2025" (p37 Financial Review; footnote p110; Note p128). current_fy.

## This-FY timeline

| property | type | date | deal_fy_scope | as-reported gain/premium | use-of-proceeds |
|---|---|---|---|---|---|
| Kelsterbach Data Centre | divestment | 2025-03-24 | current_fy | +28.2% premium to EUR 39.0m valn (p36); accounting gain S$10.825m (p103) | net proceeds repaid bank borrowings (p107) |

## Corrections proposed
1. **`net_proceeds_basis` page-cite fix** (kind: fix, provenance only). The basis note says "S$65,475k on p128"; the S$65,475k figure is actually on **p107** (Consolidated Statement of Cash Flows / Note B), not p128. Substance (combined → null) is correct.
2. **`source_page` 108 → p36 (or p128)** (kind: fix, provenance only). Page 108 is Note A (Acquisitions); the Kelsterbach divestment's key pages are p36 (narrative/premium), p103 (gain), p110 (carrying), p128 (consideration S$70.6m).
3. No value corrections — all typed values verified.

## Suggestions / raw material
- **DPU-boost — NO.** The accounting gain S$10.825m is ADJUSTED OUT of distributable income in the
  Distribution Statement (p109: "Gain on divestment of investment property (net of withholding tax) (10,825)";
  footnote: "adjustments of accounting gains on divestments for Kelsterbach DC"). So the capital gain was NOT
  distributed to unitholders. Net proceeds were used to repay bank borrowings (p107); the three FY2025
  divestments (Kelsterbach + Basis Bay + NetCo) "unlock approximately $0.2 billion" for redeployment (p... CEO
  review). `distributed_gain=false`, use=`repay_debt`.
- **Coverage gaps:** valuer (Savills UK) + valuation date (31 Dec 2024) printed; premium % (28.2%) printed;
  gross consideration printed in BOTH EUR (50.0m) and SGD (70.6m); carrying at 31 Dec 2024 (S$55,041k) and
  gain (S$10.825m) printed. Per-deal net proceeds are combined-only (p107) and genuinely unrecoverable.
