# Q5T (Far East Hospitality Trust) — property-transaction audit — FY-END 2025-12-31

Stem: `16_Q5T.SI_Far-East-Hospitality-Trust_FY2025`. One row: Four Points by Sheraton Nagoya acquisition (first overseas asset). FY2025 window = 2025-01-01…2025-12-31. Physical `<!-- PAGE N -->` cites.

## Per-column null/value status — Four Points by Sheraton Nagoya, Chubu International Airport (FPN) — acquisition
- **transaction_type / date:** acquisition; **completed 25 April 2025** (SPA signed 20 Feb 2025). Correct — "On 25 April 2025, the Trust completed the acquisition … following the signing of the sale and purchase agreement on 20 February 2025" (PAGE 31); "completed on 25 April 2025" (PAGE 112 note (4); PAGE 157 note).
- **purchase_price / `consideration` (6,000,000,000 JPY):** VERIFIED. Property profile "Purchase price (¥ million): 6,000" (PAGE 30); CBRE Nagoya-transactions table "Four Points by Sheraton Nagoya … 6,000,000 (JPY'000)" (≈PAGE 38). Currency JPY, as-reported. Correct. (~S$56.5m per cash flow; stapled-level nuance below.)
- **valuation / `valuation` (7,790,000,000 JPY):** VERIFIED as a genuine **year-end valuation as at 31 Dec 2025**, distinct from purchase. Property profile "Valuation as at 31 Dec 2025 (¥ million): 7,790" (PAGE 30); "The valuation was based on a discounted cash flow method" (PAGE 157 note). Currency JPY, as-reported. Correct. Distinct from the JPY 6,000m purchase (a ~30% year-end uplift).
- **counterparty:** Godo Kaisha Pothos (unrelated third party). Correct — "the Far East H-REIT acquired Four Points by Sheraton Nagoya … from Godo Kaisha Pothos, an unrelated third party" (PAGE 157).
- **gross/net/gain/carrying:** NULL — n/a (acquisition; no divestment figures). Correct.

## This-FY timeline
| property | type | date | deal_fy_scope | as-reported gain/premium | use-of-proceeds |
|---|---|---|---|---|---|
| Four Points by Sheraton Nagoya (FPN) | acquisition | 2025-04-25 (completed) | **current_fy** | n/a (acquisition) — year-end valuation JPY 7,790m vs purchase JPY 6,000m | funded by JPY 3.5bn secured term loans (Nagoya Falcon TMK) + RCF + JPY 0.5bn 4-yr TMK bond (PAGE 186) |

## Corrections proposed
1. **`valuation_basis` valuer attribution — verify/soften "CBRE K.K." (kind=fix, provenance only; figure unchanged).** The AR does NOT name the Japan valuer — the year-end valuation note states only "The valuation was based on a discounted cash flow method" (PAGE 157); the named 31-Dec-2025 valuers are SG&R/HVS and Savills for the **Singapore** properties (PAGE 157). CBRE appears in this report only as the **market-research** author (CBRE market overview, PAGE 33-38). Recommend removing/qualifying the "CBRE K.K." attribution unless confirmed from the acquisition circular. The valuation figure JPY 7,790m is solid.
2. No money-column corrections.

## Suggestions / coverage
- Stapled-security accounting nuance the table cannot express: at the **Stapled Group** level FPN is reclassified to **PPE (land & building) at cost** (S$59,211k, PAGE 157) with an "Adjusted purchase consideration for acquisition of investment property S$10,511k" (PAGE 179), while at the **H-REIT** level it is investment property at valuation (JPY 7,790m). The single `purchase_price`/`valuation` row loses this.
- Both SPA date (20 Feb 2025) and completion date (25 Apr 2025) are printed — table carries one date + note.
- Currency: figures correctly kept in JPY as-reported; SGD approximations (~S$56.5m purchase) live in the note.
- No divestments → no proceeds-use / DPU-gain signal.
