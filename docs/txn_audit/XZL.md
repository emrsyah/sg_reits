# XZL.SI — Acrophyte Hospitality Trust (ACRO-HT, stapled) — FY2025 property-transaction audit

FY-end: **2025-12-31**. Rows audited: **3** (2 divestments + 1 terminated). All figures USD. Stapled entity — figures appear at ACRO-REIT / ACRO-BT / Stapled levels; watch which level each figure belongs to.

## Row 1 — Hyatt Place Detroit Auburn Hills (divestment, completed)

| Column | JSON value | Verdict | Source |
|---|---|---|---|
| type / status | divestment / completed | ✅ correct | "one hotel was disposed: Hyatt Place Detroit Auburn Hills for US$6.65 million in September 2025" (p18 line 578) |
| agreement_date | 2025-06-04 | ✅ correct | "On 4 June 2025 (U.S. time), ACRO-HT entered into a conditional purchase and sale agreement with AHM Hospitality LLC... for US$6.65 million" (p10 line 342) |
| completion_date | 2025-09-10 | ✅ correct | "The sale was completed on 10 September 2025 (U.S. time)" (p10 line 342); Note 11 p133 line 4441 |
| deal_fy_scope | (current_fy) | ✅ only FY2025 **completed** disposal | p18/p133 |
| price (gross_sale_price) | 6,650,000 USD | ✅ correct | p10/p18 |
| carrying_value | 6,208,000 USD | ✅ genuine (Stapled level) | Note 11 assets-held-for-sale roll-forward "Sale completed during the financial year (6,208)" Stapled; (5,980) ACRO-REIT (p133 line 4438) |
| gain_on_divestment | -127,000 USD | ⚠️ genuine but entity-level (see note) | "Net loss on disposition of property, plant and equipment (127)" — ACRO-BT column, Statement of Comprehensive Income p98 line 3202; Note 11 |
| valuation | null | ✅ confirmed null | Deal valuation only in the 5 Jun 2025 announcement, not the AR (p10 line 342) |
| counterparty | AHM Hospitality LLC | ✅ correct — AR-named | p10 line 342; Note 11 p133 line 4441 |

**gain/carrying entity nuance (not a correction):** the reported deal loss **US$(127)k** is the *Net loss on disposition of PP&E* booked at **ACRO-BT** level (Stapled column shows "–" because at Stapled level the movement runs through "Net change in fair value of assets held for sale"). `carrying_value=6,208` is the **Stapled**-level held-for-sale carrying removed on completion (ACRO-BT = 793; ACRO-REIT = 5,980). So the reported gain and the reported carrying sit at different consolidation levels; do not reconcile them arithmetically. Only one hotel completed in FY2025, so both the (6,208) roll-forward line and the (127) disposition loss are attributable to Auburn Hills.

## Row 2 — Hyatt Place Detroit Livonia (divestment, completed post-FY)

| Column | JSON value | Verdict | Source |
|---|---|---|---|
| type / status | divestment (announced/agreed; completed post-FY) | ✅ correct | p17 line 562; Note 29 p170 line 5842 |
| agreement_date | 2025-12-08 | ✅ correct | "On 8 December 2025 (U.S. time)... conditional purchase and sale agreement... for US$10.0 million" (p17 line 562; p170 line 5842) |
| completion_date | 2026-03-11 | ✅ correct (AR internally 10 Mar US-time / 11 Mar) | p17 line 562 "completed on 10 March 2026 (U.S. time)"; Note 29 p170 "completed on 11 March 2026" |
| deal_fy_scope | **subsequent_event** | ✅ correct — completed after 2025-12-31 | p170 |
| price (gross_sale_price) | 10,000,000 USD | ✅ correct | p17/p170 |
| valuation | 10,300,000 USD | ✅ correct | "independent valuation of US$10.3 million as of 31 July 2025" (p170 line 5842); year-end portfolio list 10.3 (p16 line 533) |
| carrying_value | **null** | ✅ CONFIRMED null — round-8 removal validated | Note 11 held-for-sale year-end balance = 0 (p133 line 4439) → Livonia NOT reclassified to held-for-sale at 31 Dec 2025; carrying sits in aggregate PP&E, no per-property figure printed |
| gain_on_divestment | null | ✅ confirmed null — subsequent event | p170 |
| counterparty | NJA Management Group LLC | ⚠️ NOT in AR — see flag | AR says only "a purchaser" (p17/p170); "NJA" absent from full.md (from the 10 Dec 2025 announcement) |

**Round-8 fix validated:** the previous `carrying_value=10,300,000` equalled the *independent valuation* (US$10.3m) — a **valuation→carrying conflation**. Removing it is correct: no printed carrying value exists for Livonia (never held-for-sale at year-end). Sale price is a **2.9% discount** to the US$10.3m valuation (p170).

## Row 3 — Hyatt Place Memphis Primacy Parkway (divestment TERMINATED)

| Column | JSON value | Verdict | Source |
|---|---|---|---|
| type / status | divestment_terminated / terminated | ✅ correct | "conditional purchase and sale agreement with Shivam Patel... for US$7.75 million" (p23 line 822); "terminated by the buyer, as announced on SGXNET on 16 March 2026" (p33 line 1293) |
| agreement_date | 2025-12-16 | ✅ correct | "On 16 December 2025 (U.S. time)..." (p23 line 822) |
| completion_date | null | ✅ correct — never completed (terminated) | p33 line 1293 |
| deal_fy_scope | **subsequent_event** | ✅ (see note) | agreement 16 Dec 2025 within FY; deal never completed; termination 16 Mar 2026 post-balance-sheet |
| price | 7,750,000 USD | ✅ correct — conditional agreement price | p23 |
| valuation | 7,700,000 USD | ✅ correct | year-end portfolio list, Memphis 7.7 (p16 line 536) |
| carrying_value | null | ✅ confirmed null — remains in portfolio, never held-for-sale | Note 11 year-end held-for-sale = 0 (p133) |
| gain_on_divestment / net | null | ✅ confirmed null — terminated, no final figures | p33 line 1293 |
| counterparty | Shivam Patel | ✅ correct — AR-named | p23 line 822 |

**Scope note:** none of {current_fy, prior_year, subsequent_event} is a perfect fit for a terminated deal. Classified **subsequent_event** because it never completed and its resolution (termination) is a post-balance-sheet event; the conditional agreement was signed within FY2025 (16 Dec 2025). Consistent with Livonia (agreed within FY, resolved post-FY).

## This-FY timeline

| property | type | date | deal_fy_scope | as-reported gain / premium | use-of-proceeds |
|---|---|---|---|---|---|
| Auburn Hills | divestment (completed) | 2025-09-10 (agr. 2025-06-04) | current_fy | **loss US$(127)k** (PP&E disposition, ACRO-BT) | proceeds "used to fund the capital expenditure needs related to ongoing renovations" (p27 line 1018) |
| Detroit Livonia | divestment (completed) | 2026-03-11 (agr. 2025-12-08) | subsequent_event | **2.9% discount to US$10.3m valuation** (p170); no $ gain in FY2025 | net proceeds "to fund... brand-mandated renovations, pare down borrowings, and/or meet general working capital needs" (p33 line 1291) |
| Memphis Primacy Parkway | divestment_terminated | agr. 2025-12-16 (terminated 2026-03-16) | subsequent_event | none disclosed (terminated) | n/a — deal fell through |

## Corrections proposed
- **None to typed money/label/date columns** — all verified.
- **Flag (sourcing, not a value fix): Row 2 `counterparty="NJA Management Group LLC"` is not verifiable in the AR** (AR says only "a purchaser"; "NJA" absent from full.md). Likely from the 10 Dec 2025 SGXNET announcement. Either annotate the source as the announcement or set to "unnamed in AR". Do NOT silently treat as AR-sourced.
- Minor page-ref hygiene (`source_page`): Row1 says 11 (physical p10), Row2 says 22 (valuation p16 / footnote p17 / Note 29 p170), Row3 says 18 (valuation p16 / PSA p23). Non-critical but worth aligning to physical `<!-- PAGE -->`.

## As-reported profit-from-divestment (raw material)
- Auburn Hills: **US$(127)k loss** on PP&E disposition (p98). No headline gain/premium in AR.
- Livonia: **2.9% discount to independent valuation** US$10.3m (p170). No $ gain (subsequent event).
- Memphis: none (terminated).

## Use-of-proceeds / DPU linkage
- Proceeds directed to **capex / brand-mandated renovations, debt pay-down, and general working capital** (p27 line 1018; p33 line 1291). **No divestment-gain distribution to unitholders** → `distributed_gain=false`. The 26 Feb 2026 distribution of 0.418 US¢/security (p170 line 5844) is the ordinary 2H2025 distribution, unrelated to divestment gains.

## Suggestions / coverage gaps
- **Stapled-entity level tagging:** gain (ACRO-BT) and carrying (Stapled) come from different consolidation levels; a `reporting_entity_level` tag would prevent false gain↔carrying reconciliation.
- **Terminated deals need a first-class status** (present here as `divestment_terminated`) with explicit "no final figures" semantics; and a **discount/premium-to-valuation %** field (Livonia 2.9% discount) is recoverable and currently unrepresentable.
- **Agreement vs completion dates** both printed for all three — table captures both here; keep.
- **Counterparty provenance:** two of three names come from the AR (AHM Hospitality, Shivam Patel); Livonia's comes from an announcement — capture a `counterparty_source`.
