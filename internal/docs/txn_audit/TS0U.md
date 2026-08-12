# TS0U (OUE REIT) — property-transaction audit — FY-END 2025-12-31

Stem: `31_TS0U.SI_OUE-REIT_FY2025`. Two rows: 1 divestment (Lippo Plaza Shanghai, FY2024/audit-trail) + 1 acquisition (Salesforce Tower, subsequent event). All physical-page cites are `<!-- PAGE N -->` markers in `full.md`.

## Per-column null/value status

### Row 1 — Lippo Plaza Shanghai (via Lippo Realty (Shanghai) Limited) — divestment
- **transaction_type / status:** divestment / divested (completed). Correct. Disposal of 100% of Lippo Realty (Shanghai) Ltd (subsidiary holding the property). PAGE 121.
- **transaction_date:** announced 20 Dec 2024, **completed 27 Dec 2024**. Correct. PAGE 121.
- **gross_sale_price (JSON `sale_consideration`/`divestment_price` = 357,382,000 SGD):** VERIFIED. "total sales consideration of RMB 1,916,925,000 (equivalent to approximately $357,382,000)" — PAGE 121. Currency: as-reported SGD equivalent of RMB 1,916,925,000 (local RMB kept). Correct.
- **net_sale_proceeds (JSON `net_proceeds` = 299,460,000):** VERIFIED. "Net cash inflow on disposal of a subsidiary 299,460" (effect-of-disposal, PAGE 121); also cash-flow "Disposal of a subsidiary, net of cash disposed 299,460" (PAGE 120). This is a subsidiary-level net cash inflow (net of cash disposed 57,922 and deferred consideration 3,260, plus WHT/costs add-back). Distinct from gross. Correct.
- **carrying_value (311,136,000):** VERIFIED. "Investment property 311,136" line of the effect-of-disposal net-assets table (PAGE 121); corroborated by the investment-property movement note "Disposal of a subsidiary (311,136)". Correct.
- **gain_on_divestment (-26,427,000):** VERIFIED as-reported, but note the label: **"Loss on disposal of a subsidiary (26,427)"** (PAGE 121). This is a SUBSIDIARY-LEVEL loss struck against net assets disposed S$325,242k (which include FCTR recycling +54,614 and tax −32,323), NOT gross−carrying on the property. Do NOT read it as a property gain/loss: 357,382 − 311,136 would wrongly imply a +46.2m "gain". The prior `carrying_value_basis` note documents this correctly.
- **valuation:** NULL — confirmed. No independent property valuation is printed for Lippo Plaza in the disposal note or MD&A; only the RMB sale consideration. Genuine null.

### Row 2 — Salesforce Tower (180 George Street, Sydney) — acquisition (subsequent event)
- **transaction_type / status:** acquisition / `subsequent_event` (see correction). Sale-and-unit agreement 24 Feb 2026; **completed March 2026**. PAGE 175 (agreement); PAGE 18 (completed March 2026).
- **transaction_date:** 24 Feb 2026 (agreement). Correct. PAGE 175.
- **purchase_price (JSON `consideration` = 175,046,000 SGD; `consideration_local` = 195,538,000 AUD):** VERIFIED. "acquire a 19.9% interest in Salesforce Tower for a consideration of A$195,538,000 (equivalent to $175,046,000)" — PAGE 175. Correct.
- **counterparty:** Lendlease target trusts (Circular Quay / Jackson on George / CQT Assets) + Target Trustee. Correct. PAGE 175.
- **valuation / carrying_value / gain / net proceeds:** NULL — confirmed. Acquisition, subsequent event; no valuation/carrying printed.

## This-FY timeline
| property | type | date | deal_fy_scope | as-reported gain/premium | use-of-proceeds |
|---|---|---|---|---|---|
| Lippo Plaza Shanghai | divestment | 2024-12-27 (completed) | **prior_year** (FY2024; before FY2025 window 2025-01-01…2025-12-31) | Loss on disposal of subsidiary **S$26.4m** (PAGE 121); no premium/discount % stated | "Partial net proceeds … utilised to repay loans" → aggregate leverage 38.5% (PAGE 41; PAGE 18). distributed_gain = false (it was a loss) |
| Salesforce Tower (19.9%) | acquisition | 2026-02-24 (agreement); completed 2026-03 | **subsequent_event** (post 31-Dec-2025) | n/a (acquisition) | n/a |

## Corrections proposed
1. **Salesforce Tower — status relabel (low priority).** JSON `status` = `"subsequent_event"` puts a *scope* value in the *status* field. As-reported the deal was **completed** (March 2026, PAGE 18). Propose status = `completed`, deal_fy_scope = `subsequent_event`, transaction_date = 2026-02-24 (agreement) / completion 2026-03. kind=relabel. No money change.
2. No money-column corrections. All figures match source.

## Suggestions / coverage
- Lippo's `gain_on_divestment` is entity-level (incl. FCTR recycling & tax), not a clean property gain — the design report should distinguish "subsidiary-disposal loss" from "property gain/loss". Our table cannot express this today.
- Both announcement (20 Dec 2024) and completion (27 Dec 2024) dates are printed; likewise Salesforce agreement (24 Feb 2026) + completion (Mar 2026) — table captures only one date + note.
- Salesforce discloses a ROFR (right of first refusal) pipeline on further stakes, and trustee-share stake 22.0% alongside the 19.9% unit interest — not captured.
- Local-currency figures (AUD 195,538k; RMB 1,916,925k) are captured in `_local` fields.
- DPU-boost data: Lippo proceeds → debt repayment (indirect DPU/leverage benefit), no gain distribution.
