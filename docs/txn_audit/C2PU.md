# C2PU (Parkway Life REIT / PLife REIT) — property-transaction audit — FY-END 2025-12-31

Stem: `32_C2PU.SI_Parkway-Life-REIT_FY2025`. One row: MOB Specialist Clinics (Malaysia Portfolio) divestment — full exit from Malaysia. FY2025 window = 2025-01-01…2025-12-31. Physical `<!-- PAGE N -->` cites.

## Per-column null/value status — MOB Specialist Clinics, Kuala Lumpur (Malaysia Portfolio) — divestment
- **transaction_type / status:** divestment / completed. Correct.
- **agreement_date / completion_date:** SPA **21 April 2025**; **completed 12 August 2025**. Correct — "On 21 April 2025, the Group entered into a sale and purchase agreement … The disposal … was completed on 12 August 2025" (PAGE 189 Note 4; PAGE 166 portfolio note; PAGE 10 narrative).
- **gross_sale_price / `price` (6,100,000 SGD; `price_raw` RM20.1m ≈ S$6.1m):** VERIFIED (rounded). "for RM20.1 million (approximately S$6.1 million)" (PAGE 10/166/189). Note: the deal is RM-denominated (RM20.1m); the precise SGD booked in the related-party note is **6,088** (see coverage). 6,100,000 = the as-reported rounded S$6.1m. Acceptable.
- **net_proceeds (5,986,000):** VERIFIED. Cash-flow "Net proceeds from disposal of investment property (including divestment related costs) — 5,986" (PAGE 168). Genuinely net-of-cost. Correct.
- **gain_on_disposal (123,000):** VERIFIED as-reported and **precisely printed** (not just the "~$0.1m" narrative). Statement of Total Return "Gain on disposal of investment property — 123" (PAGE 146); mirrored in distribution-adjustment and cash-flow reconciliation lines "(123)". FS Note 4 narrates it as "a net gain on disposal (net of disposal costs and before tax) of approximately $0.1 million" (PAGE 189). Correct.
- **carrying_value (5,863,000): VALUE CORRECT, but the `carrying_value_basis` note is FALSE — see correction #1.** The figure is **genuinely printed**: Note 4 investment-property movement "Disposal of investment property (5,863)" (PAGE 189). It is NOT a derived (net−gain) figure.
- **valuation (5,800,000; RM19.2m ≈ S$5.8m):** VERIFIED as a genuine independent valuation **distinct** from the consideration. "4.6% above the average of latest valuations of RM 19.2 million (approximately S$5.8 million), which were derived using the income approach" (PAGE 10). Correct — not a conflation (RM19.2m valuation ≠ RM20.1m consideration).
- **counterparty:** Pantai Medical Centre Sdn. Bhd. (wholly-owned sub of IHH Healthcare Berhad; IHH is a substantial unitholder → interested-person transaction). Correct (PAGE 10/189).

Internal consistency (all three separately printed): net proceeds 5,986 − carrying 5,863 = gain 123. ✓

## This-FY timeline
| property | type | date | deal_fy_scope | as-reported gain/premium | use-of-proceeds |
|---|---|---|---|---|---|
| MOB Specialist Clinics, KL (Malaysia Portfolio) | divestment | 2025-08-12 (completed); agreement 2025-04-21 | **current_fy** | Net gain on disposal **S$123k** (PAGE 146); **+25.6% premium over original purchase price**; **+4.6% above average valuation RM19.2m** (PAGE 10) | "capital recycling … sharpen focus on core markets, strengthen its balance sheet, and enhance financial flexibility" (PAGE 10) → **use = general/balance-sheet** (no explicit debt-repay or special distribution). **distributed_gain = false** |

## Corrections proposed
1. **MOB Specialist Clinics — fix `carrying_value_basis` provenance (kind=fix; value 5,863,000 UNCHANGED).** The current basis says "DERIVED: net_proceeds 5,986 − gain 123 = 5,863 (no standalone property carrying line)". This is factually wrong: the standalone carrying IS printed — Note 4 movement "Disposal of investment property (5,863)" (PAGE 189). Replace the basis with a cite to that printed line. (Value is right; the derivation justification and the "no standalone line" claim are false — an important audit distinction: correct-by-coincidence with a false rationale.)
2. No money-value corrections.

## Suggestions / coverage
- Disclosed but uncaptured/imprecise: precise SGD consideration **6,088** (related-party transactions note) vs rounded 6,100 — deal is RM-denominated (RM20.1m); consider storing RM20,100,000 as gross with currency RM. Both agreement (21 Apr) and completion (12 Aug) dates printed. Premium framings (+25.6% over cost; +4.6% over valuation), "0.2% of portfolio", "full exit from Malaysia" not captured.
- Buyer is an IHH subsidiary and IHH is a substantial unitholder → interested-person transaction flag not captured.
- DPU-boost: no gain distribution; proceeds framed as balance-sheet strengthening only.
