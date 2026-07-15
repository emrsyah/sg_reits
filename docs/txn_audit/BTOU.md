# BTOU.SI — Manulife US REIT — property-transaction audit (FY2025, FY-END 2025-12-31)

Source: `parsed_reports_datalab/26_BTOU.SI_Manulife-US-REIT_FY2025/full.md`.
2 rows: divestments of Plaza (Secaucus, NJ) and Peachtree (Atlanta, GA), both completed in FY2025 under
the MRA disposition programme.
**Assignment core checks — CONFIRMED:** gross_sale_price US$51.8m (Plaza) / US$133.8m (Peachtree) both
verified on **p126** (Notes: "US$51.8 million less seller credits" / "US$133.8 million less seller
credits"); net_consideration and valuation verified on **p25**.

## Per-column null/value status (Divestments table p25; footnotes 2–4)
The p25 table columns are literally **"Net Consideration"** (40 / 121) and **"Valuation"** (43.7 / 133.4).

### Plaza (Secaucus, New Jersey)
- `net_consideration_usd` 40,000,000 — **correct** (p25 "Net Consideration 40"; per PSA subject to closing adj, footnote 2).
- `gross_valuation_usd` 43,700,000 — **value correct** = independent valuation (Cushman & Wakefield of New Jersey, as at 31 Dec 2024, footnote 3, p25). *Field name is a misnomer — this is the "Valuation" column, not a "gross valuation"; it maps to the standard `valuation` column.*
- `gross_sale_price` 51,800,000 — **correct** (p126: "announced the divestment of Plaza on 20 February 2025 for US$51.8 million less seller credits").
- `carrying_value` 43,700,000 — **correct** (held-for-sale carrying at 31 Dec 2024; Note 6 / SoFP p... / portfolio statement p... "Plaza 43,700"). NOTE: equals the valuation 43.7 because a held-for-sale asset is carried at fair value = the 31 Dec 2024 Cushman valuation. Same underlying figure printed under two labels — legitimate, NOT a conflation error.
- `completion_date` 2025-02-25 — **correct** ("completed on 25 February 2025 (U.S. time)"), current_fy.
- `buyer` 500 Plaza Ground Lessor LLC — **correct** (p25). (A third-party market-comps table lists a different naming "Signature Acquisitions" — ignore; the divestment table is authoritative.)

### Peachtree (Atlanta, Georgia)
- `net_consideration_usd` 121,000,000 — **correct** (p25 "Net Consideration 121").
- `gross_valuation_usd` 133,400,000 — **value correct** = valuation (Cushman & Wakefield, as at 28 Apr 2025, footnote 4, p25). Same field-name note as above.
- `gross_sale_price` 133,800,000 — **correct** (p126: "the divestment of Peachtree for US$133.8 million less seller credits").
- `carrying_value` 125,366,000 — **correct** (Note 6 investment-property movement "Disposal of investment properties (125,366)" for 2025; Plaza had already exited via held-for-sale in 2024, so this line is Peachtree's carrying — attribution of a single printed figure, not a derivation).
- `completion_date` 2025-05-27 — **correct** ("completed on 27 May 2025 (U.S. time)"), current_fy.
- `buyer` SSC VII INVESTOR, LLC — **correct** (p25).

### Gain/loss — genuinely null per-deal
No per-deal gain is stored, and none is disclosed: the report prints only a **COMBINED loss on disposal of
investment properties of US$3,323,000** (Statement of Comprehensive Income p103; MD&A p23), stated to arise
"as a result of the transaction costs incurred" (p23). Genuine per-deal null. Do not split.

## This-FY timeline

| property | type | date | deal_fy_scope | as-reported gain/premium | use-of-proceeds |
|---|---|---|---|---|---|
| Plaza | divestment | 2025-02-25 | current_fy | gross US$51.8m vs valn US$43.7m; net cons US$40m; (combined loss) | repay debt (MRA) |
| Peachtree | divestment | 2025-05-27 | current_fy | gross US$133.8m ≈ valn US$133.4m; net cons US$121m; (combined loss) | repay debt (MRA) |

Combined loss on disposal US$3.323m (p103) — transaction-cost driven; NOT split per property.

## Corrections proposed
1. **Field-mapping (relabel):** `gross_valuation_usd` (both rows) should map to the standard `valuation`
   column at load — the source label is simply "Valuation" (footnotes 3/4, p25). Values are correct; the
   "gross_" prefix is misleading. No value change.
2. No value corrections. Money columns all match their source labels.

## Suggestions / raw material
- **Distinct "net proceeds" figures exist but are not captured.** Beyond Net Consideration (40/121, p25),
  the report also prints per-deal NET PROCEEDS: Plaza **US$40.0m**, Peachtree **US$123.6m** (MD&A/CEO review
  p23–24; e.g. "Sold Peachtree for net proceeds of US$123.6 million"), combined **US$163.6m**; and cash-flow
  "Proceeds from disposal ... (net of transaction costs) 161,073" (p107). These are three different "net"
  bases — capturable raw material; the schema currently holds only Net Consideration.
- **DPU-boost — NO.** Distributions were HALTED (p23, "halting of distributions"); there was a net loss.
  Combined net proceeds US$163.6m + US$25.0m cash used to repay debt to meet the MRA Minimum Sale Target
  (p23). `distributed_gain=false`, use=`repay_debt`.
- **Coverage gaps:** valuer (Cushman & Wakefield) + valuation dates (31 Dec 2024 / 28 Apr 2025) printed;
  gross "headline" sale price printed separately (p126) from net consideration (p25); divestment fee US$0.8m
  for Plaza+Peachtree (p110); Tranche-2-Asset classification + MRA target context; preferred-unit redemptions
  tied to each divestment (notes).
