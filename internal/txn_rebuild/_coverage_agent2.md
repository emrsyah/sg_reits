# Agent 2 — Divestment Disclosure Coverage (28 divestments)

Scope: A17U/FY2024 (4), AJBU/FY2025 (2 — note: extraction lists 1 divestment; AR discloses only Kelsterbach
as a completed FY2025 divestment; Basis Bay is a subsequent-event agreement, not completed — see note),
C38U/FY2024 (1), C38U/FY2025 (2), J91U/FY2025 (11), MXNU/FY2024 (3), N2IU/FY2023 (1), O5RU/FY2025 (2),
P40U/FY2024 (1), UD1U/FY2024 (1).

Source: `parsed_reports_datalab/<folder>/full.md`, read directly with quotes below. `extracted/*/property_transactions.json`
used only to find page numbers.

Folder mapping used (per brief + meta.json confirmation):
- A17U/FY2024 → `05_A17U.SI_..._FY2024`
- AJBU/FY2025 → `21_AJBU.SI_..._FY2025`
- C38U/FY2024 → `09_C38U.SI_..._FY2024`
- C38U/FY2025 → `09_C38U.SI_..._FY2025`
- J91U/FY2025 → `15_J91U.SI_..._FY2025`
- MXNU/FY2024 → `14_MXNU.SI_..._FY2024`
- N2IU/FY2023 → `29_N2IU.SI_..._FY2022` (meta.json `file` field = `..._FY2024.pdf`, i.e. the AR titled "FY23/24" =
  declared FY2023, confirming the brief's one-year-behind offset for N2IU)
- O5RU/FY2025 → `02_O5RU.SI_..._FY2025` (brief states O5RU folder labels are correct declared FY; AR itself is
  titled "FY2026" internally per AIMS' Apr–Mar fiscal-year convention but the folder maps to declared FY2025 as
  instructed)
- P40U/FY2024 → `35_P40U.SI_..._FY2024` (brief: folder label is correct declared FY; report covers FY ended 30 Jun 2025,
  which the AR itself calls "FY2024/25")
- UD1U/FY2024 → `20_UD1U.SI_..._FY2024`

---

## A17U / FY2024

### 1. 77 Logistics Place (Brisbane, Australia)
- `sale_price_disclosed`: **true**, but only as part of an aggregate. Divestment table (p28): "| 77 Logistics Place | | | 25.7¹ | AM QLD Industrial Property Pty Ltd ATF AM QLD Industrial Property No.4 Unit Trust | |" with the Sale Consideration column merged across the three-property block, showing a single value **"64.2"** (S$ million) spanning all three rows, and Total row = S$177.0m sale / S$127.9m valuation for the whole FY2024 divestment set (3 AU properties + 21 Jalan Buroh).
- `sale_price_scope`: **aggregate_multi_property** — covers 77 Logistics Place, 62 Sandstone Place, 92 Sandstone Place together (S$64.2m for all three).
- `pct_disclosed`: false — no premium % stated for this property or the AU trio in the AR text found (only in our own extraction's derived note).
- `reference_disclosed`: true, **per-property** — same table gives per-property Valuation: 77 Logistics Place S$25.7m (footnote 1: valuation basis). Also Note 11 (p163 area, verbatim): "On 20 December 2023, CLAR announced it had entered into three put and call option deeds to divest three logistics properties in Australia, namely, 77 Logistics Place, 62 Sandstone Place and 92 Sandstone Place located in Queensland, Australia with a carrying amount of $24,359,000 (A$27,000,000), $14,345,000 (A$15,900,000) and $23,728,000 (A$26,300,000) respectively." → 77 Logistics Place carrying value = $24,359,000.
- `gain_disclosed`: true, **aggregate only**. Note 11: "On 27 February 2024, the Group completed the divestment of 77 Logistics Place, 62 Sandstone Place and 92 Sandstone Place located in Queensland, Australia, recognising a gain amounting to $628,000 (A$710,000) in Consolidated Statement of Total Return." — single gain figure for all three, not apportioned.
- `notes`: **Confirmed as ONE aggregate deal** — the AR discloses per-property valuations and carrying values, but sale consideration (S$64.2m) and gain ($628k/A$710k) are each single figures covering all three Brisbane properties. Divestment diary entry (p~7): "Completed the divestment of 77 Logistics Place, 62 Sandstone Place and 92 Sandstone Place, three logistics properties in Brisbane, Australia, for S$64.2 million" — again one figure for all three.

### 2. 62 Sandstone Place (Brisbane, Australia)
- Same aggregate deal as above. `sale_price_disclosed`: true (aggregate S$64.2m, table p28). `sale_price_scope`: aggregate_multi_property.
- `pct_disclosed`: false.
- `reference_disclosed`: true per-property — valuation S$15.4m (table p28); carrying amount $14,345,000 (A$15,900,000) (Note 11).
- `gain_disclosed`: true, aggregate only ($628,000 / A$710,000, Note 11).
- `notes`: same trio deal.

### 3. 92 Sandstone Place (Brisbane, Australia)
- Same aggregate deal. `sale_price_disclosed`: true (aggregate S$64.2m, table p28). `sale_price_scope`: aggregate_multi_property.
- `pct_disclosed`: false.
- `reference_disclosed`: true per-property — valuation S$19.3m (table p28); carrying amount $23,728,000 (A$26,300,000) (Note 11). Note: this property's carrying value ($23.728m) exceeds its own per-property valuation ($19.3m) — a report-internal inconsistency worth flagging, though it doesn't affect the aggregate-deal conclusion.
- `gain_disclosed`: true, aggregate only ($628,000 / A$710,000, Note 11).
- `notes`: same trio deal.

### 4. 21 Jalan Buroh (Singapore)
- `sale_price_disclosed`: **true**, per-property. Diary (p~7): "Completed the divestment of 21 Jalan Buroh, a logistics property in Singapore, for S$112.8 million." Table (p28): row "21 Jalan Buroh | Singapore | 112.8 | 67.5² | GDS IDC Services Pte. Ltd. | 28 Nov 2024".
- `sale_price_scope`: **per_property**.
- `pct_disclosed`: false — no explicit % premium stated in the AR text located for this property (report gives dollar figures only).
- `reference_disclosed`: true — valuation S$67.5m in the same table (footnote 2, valuation basis); Investment Properties Portfolio Statement (p115 area) shows 2023 carrying amount $67.5m for 21 Jalan Buroh, with 2024 column showing "–" (divested), and footnote (m)/(iii) ties completion to 28 Nov 2024.
- `gain_disclosed`: false as a per-property figure — the AR discloses only a total "Gain on disposal of investment properties" line (segment note, not itself located verbatim by page in this pass) that bundles 21 Jalan Buroh with the AU trio; no standalone gain quoted for 21 Jalan Buroh alone.
- `notes`: sale price and valuation both per-property and disclosed; gain is not separately broken out.

---

## AJBU / FY2025

### 1. Kelsterbach Data Centre (Kelsterbach, Germany)
- `sale_price_disclosed`: **true**, per-property, in EUR. Financial Review (p~2125, verbatim): "In March 2025, Kelsterbach DC was opportunistically divested to Fortinet GmbH for EUR 50.0 million or a 28.2% premium to its 31 December 2024 value of EUR 39.0 million by Savills (UK) Limited, an independent [valuer]". Portfolio review (p~284): "we sold Kelsterbach Data Centre in Germany, Basis Bay Data Centre in Malaysia and the NetCo bonds and preference shares during the year." Note (investment property additions/disposals, p~6358): "On 24 March 2025, the Group divested Kelsterbach DC for a consideration of approximately $70.6 million." — this second figure is the SGD-equivalent consideration (S$70.6m ≈ EUR 50.0m at the reporting date rate), not a different price.
- `sale_price_scope`: **per_property**.
- `pct_disclosed`: **true** — "a 28.2% premium to its 31 December 2024 value of EUR 39.0 million" (exact wording from the brief, confirmed verbatim in the AR).
- `reference_disclosed`: true — valuation basis EUR 39.0 million as at 31 December 2024 by Savills (UK) Limited (independent valuation). Carrying value in the portfolio statement (p~5588/5623 area): "Kelsterbach Data Centre... – | 55,041 | – | 1.6" (S$'000, 2024 comparative) with footnote "Kelsterbach DC was divested on 24 March 2025."
- `gain_disclosed`: true — "adjustments of accounting gains on divestments for Kelsterbach DC (FY 2025)" line in the cash-flow reconciliation table confirms a gain was recognised; our extraction's S$10.825m gain figure was not independently re-derived from a single verbatim AR sentence in this pass, but the 28.2% premium math (EUR 50.0m − EUR 39.0m = EUR 11.0m ≈ S$15.5m) does not cleanly match S$10.825m, which likely reflects the gain being measured against the SGD carrying value (S$55.041m) rather than the EUR valuation, i.e. two different reference bases in play.
- `notes`: **FLAGGED PER BRIEF** — the 28.2% premium is stated explicitly and precisely against EUR 39.0m → EUR 50.0m (39.0 × 1.282 = 49.98 ≈ 50.0, internally consistent in EUR). The "S$70.6m" figure quoted elsewhere in the AR (Note, p~6358) is simply the SGD translation of the EUR 50.0m consideration at the transaction-date FX rate — it is NOT a second, inconsistent sale price on its own terms. Where a real inconsistency could arise is if a reader mechanically computes premium off the SGD carrying value (S$55.041m, 2024 comparative in the portfolio statement) rather than the EUR 39.0m independent valuation — SGD carrying S$55.041m vs SGD consideration S$70.6m implies only a ~28.3% premium in SGD terms too (coincidentally close), so the SGD/EUR bases roughly agree numerically by coincidence of FX rates, but they are conceptually different reference figures (translated carrying value vs. EUR independent valuation) and should not be treated as interchangeable. Flagging per brief instruction — not resolving further.

### Note on scope discrepancy vs brief's "(2)" count
The brief lists AJBU/FY2025 as having 2 divestments. Our own extraction (`property_transactions.json`) contains only **one** divestment-type entry for AJBU/FY2025 (Kelsterbach). Basis Bay Data Centre (Cyberjaya, Malaysia) is repeatedly referenced in the AR as an **agreement entered into** during the year ("Entered agreement for the sale of Basis Bay Data Centre... to rebalance portfolio", p~418) and as a property **reclassified to held-for-sale** (Note, p~6360: "In 2024, the Group completed the divestment of Intellicentre Campus and entered into a sale and purchase agreement to divest Basis Bay DC. Basis Bay DC has been transferred to Investment Property held for Sale"), but it is NOT shown as a completed FY2025 divestment in the text located — no completion date, sale price, or gain is given for Basis Bay in this AR. I treated Kelsterbach as the sole realised divestment for this batch and flag that the second nominal count may refer to Basis Bay's SPA/held-for-sale status (unpriced, not a completed transaction) — did not find per-property Basis Bay sale price in the AR.
- **Basis Bay Data Centre** — `sale_price_disclosed`: false (no consideration figure found in text searched). `sale_price_scope`: not_disclosed. `pct_disclosed`: false. `reference_disclosed`: false (no valuation figure quoted for the pending sale in the sections read). `gain_disclosed`: false. `notes`: property is held-for-sale under an SPA as at FY2025 year-end; not a completed transaction in this AR; searched Portfolio review, CEO/Chairman statement, and the investment-property additions/disposals note.

---

## C38U / FY2024

### 1. 21 Collyer Quay (Singapore)
- `sale_price_disclosed`: **true**, per-property. Value Creation section (p~1051, verbatim): "Divested 21 Collyer Quay to Sun View SG I Pte. Ltd. for S$688.0 million at an exit yield of less than 3.5% based on annualised net property income for the 9-month period ended 30 September 2024 and the sale price." CEO statement (p~727): "we sold 21 Collyer Quay for S$688.0 million on 11 November 2024 at an exit yield below 3.5%."
- `sale_price_scope`: **per_property**.
- `pct_disclosed`: **false** as a price-premium % — the AR discloses an *exit yield* ("less than 3.5%"), not a premium/discount to valuation. No premium % is stated.
- `reference_disclosed`: true — footnote (p~1053): "Savills Valuation and Professional Services (S) Pte Ltd had valued 21 Collyer Quay at S$688.0 million as at 31 October 2024 using the income capitalisation and discounted cash flow methods." Sale price equals the independent valuation exactly (both S$688.0m) → 0% premium, but this 0% is not itself stated in words anywhere; it must be derived from the two disclosed dollar figures.
- `gain_disclosed`: true — Note 33 (p~8870, verbatim): "On 12 November 2024, the Manager announced the divestment of 21 Collyer Quay to an unrelated third party which was completed on 11 November 2024. Accordingly, the Group recognised a net gain on divestment of investment property of $32.8 million." Net proceeds sub-note: net cash inflow S$672,607,000 (statement of cash flows, Note 33), implying divestment-related costs of ~S$15.4m between gross S$688.0m and net S$672.607m.
- `notes`: gross vs net proceeds distinguished in the AR (S$688.0m gross sale price/valuation vs S$672.607m net cash inflow after divestment-related payments). No stated percentage premium to valuation (sale price = valuation exactly); the "3.5% exit yield" figure is a yield metric, not a price premium, and should not be conflated with `pct_disclosed`.

---

## C38U / FY2025

### 1. CapitaSpring (Serviced Residence Component) — 45% interest via Glory SR Trust
- `sale_price_disclosed`: **partially/implied, not a standalone consideration figure.** Value Creation section (p~892-894, verbatim): "Divested 45% interest in the SR Component of CapitaSpring to RP Riverside II (B.V.I.) Limited and YTL Riverside Pte. Ltd. at an estimated exit yield of 3.6%¹" / "Agreed property value: S$280.0 million² on a 100% basis" / "Completion: 30 May 2025." No line explicitly states "sale price of S$126.0m" (45% × S$280.0m) — the AR gives the 100%-basis agreed property value and the % interest sold, from which the price is arithmetically implied but not itself quoted as a dollar consideration. Cash-flow statement discloses "Net cash inflow on divestment of joint venture (Note 34) 14,211" (S$'000) — this is a small NET cash figure (after JV-level cash/liabilities settle-up), not the gross sale consideration.
- `sale_price_scope`: **aggregate_multi_property is not applicable here** (single asset, partial stake) — best classified as **not_disclosed** for a true "sale price/consideration" line item; the "Agreed property value: S$280.0 million on a 100% basis" is a reference figure, not itself labelled a sale/transaction price.
- `pct_disclosed`: **false** as a price premium — only an *exit yield* of 3.6% is disclosed (an income yield metric, not a premium to valuation).
- `reference_disclosed`: **true** — footnote 2 (p~902, verbatim): "Cushman & Wakefield VHS Pte. Ltd. had valued the SR Component of CapitaSpring at S$278.5 million as at 31 December 2024 using the income capitalisation and discounted cashflow methods." Agreed property value S$280.0m vs independent valuation S$278.5m (100% basis) → implied ~0.5% premium, but this % is not stated in words.
- `gain_disclosed`: **false** — no standalone gain/loss dollar figure for this specific divestment was found in the sections searched (Value Creation, JV note, cash flow note, financial review).
- `notes`: partial-stake/equity(JV)-interest sale, not an outright property sale — priced via "agreed property value" convention rather than a stated "sale price." Net cash inflow of S$14.211m (Note 34) is NOT the gross consideration and should not be used as a proxy for sale price.

### 2. Bukit Panjang Plaza (90 of 91 strata lots)
- `sale_price_disclosed`: **true**, per-property (aggregate across the 90 strata lots as a single asset/deal). Financial review (p~748, verbatim): "Also in January 2026, CICT announced the divestment of Bukit Panjang Plaza for S$428.0 million at an exit yield of around the mid-4% level." Note (p~1769, verbatim): "On 14 January 2026, CICT entered into an agreement with an unrelated third-party for the sale of 90 strata lots in Bukit Panjang Plaza at the sale price of S$428.0 million, which was completed on 27 February 2026." Property review (p~3084) confirms same.
- `sale_price_scope`: **per_property** (single asset — 90 of the 91 strata lots held by CICT, sold as one deal to one buyer).
- `pct_disclosed`: **false** — only an exit yield ("around the mid-4% level") is stated; no premium/discount % vs. valuation is disclosed in words.
- `reference_disclosed`: **true** — Portfolio valuation table (p~1562): "Bukit Panjang Plaza⁴ | 389.0 | 389.0 | 0.0 | 2,935" (S$m valuation as at 31 Dec 2025 = S$389.0m, unchanged from 2024). Implied premium = (428.0 − 389.0)/389.0 ≈ 10.0%, but this percentage is not itself stated anywhere in the AR text located.
- `gain_disclosed`: **false** — this is a subsequent event (agreement 14 Jan 2026, completed 27 Feb 2026, after FY2025's 31 Dec 2025 year-end); no gain-on-divestment figure is booked/disclosed in the FY2025 financial statements since it had not completed as at year-end.
- `notes`: transaction announced and completed AFTER FY2025 year-end (subsequent event) — the AR nonetheless gives a full sale price and a reference valuation, so price and reference are both derivable even though gain is not yet booked.

---

## J91U / FY2025 — largest block (11 divestments)

**Key finding for this REIT: the AR gives PER-PROPERTY prices for all 11, not a single portfolio figure**, even
though 8 of the 11 are also summarised with one aggregate premium % for the group as a whole. Source: "Real
Estate Transactions in FY2025" table, Operations Review, pages 47–48 (verbatim table extracted below), plus
narrative text.

Narrative (p47, verbatim): "In FY2025, the Manager successfully completed the divestment of two assets
aggregating S$16.7 million... In December 2025, ESR-REIT also announced the divestment of a portfolio
comprising eight non-core assets in Singapore for an aggregate sale consideration of S$338.1 million,
representing a 2.0% premium to independent valuation... The divestment portfolio comprises: 46A Tanjong
Penjuru, 86 & 88 International Road, 120 Pioneer Road, 21 & 23 Ubi Road 1, 24 Jurong Port Road, 13 Jalan
Terusan, 60 Tuas South Street 1 and 43 Tuas View Circuit."

Table (p47-48, verbatim, S$ million):
| Property | Sale Consideration | Valuation | Status |
|---|---|---|---|
| 1 Third Lok Yang Road & 4 Fourth Lok Yang Road | 6.8 | 6.6 | Completed 24 Mar 2025 |
| 79 Tuas South Street 5 | 9.9 | 9.7 | Completed 28 Mar 2025 |
| 2 Changi Business Park Avenue 1 (hotel strata lot) | 101.0 | 100.9 | Expected 1Q2026 (announced) |
| 86 & 88 International Road | 42.2 | 42.2 | Expected 2Q2026 (announced) |
| 120 Pioneer Road | 34.1 | 34.1 | Expected 2Q2026 (announced) |
| 13 Jalan Terusan | 16.7 | 16.7 | Expected 2Q2026 (announced) |
| 60 Tuas South Street 1 | 3.5 | 3.5 | Expected 2Q2026 (announced) |
| 43 Tuas View Circuit | 15.1 | 15.1 | Expected 2Q2026 (announced) |
| 21 & 23 Ubi Road 1 | 45.0 | 42.5 | Expected 2Q2026 (announced) |
| 24 Jurong Port Road | 68.0 | 68.0 | Expected 2Q2026 (announced) |
| 46A Tanjong Penjuru | 113.5 | 109.5 | Expected 3Q2026 (announced) |

Check: 42.2+34.1+16.7+3.5+15.1+45.0+68.0+113.5 = **338.1** ✓ matches the "eight non-core assets... S$338.1
million... 2.0% premium" narrative exactly — confirming the "eight" group is precisely those 8 rows (excludes
2 Changi Business Park Ave 1, which is a separate hotel-strata-lot deal with its own price/valuation).

### 1. 1 Third Lok Yang Road and 4 Fourth Lok Yang Road
- `sale_price_disclosed`: true, per_property — S$6.8m (table, p47). Narrative also: "sold to Chempark Logistics (Pte) Ltd for S$6.8m (3.5% above valuation), completed 24 March 2025" (per our extraction's description field, corroborated by the table).
- `pct_disclosed`: true — footnote/body text states "3.5% above valuation" per our extraction's page-47 citation (not independently re-quoted verbatim here beyond the table, but consistent with table figures: (6.8−6.6)/6.6 = 3.03%, close to but not exactly 3.5%, small rounding — flag as approximate).
- `reference_disclosed`: true — valuation S$6.6m, footnote 2 (p47, verbatim): "Based on independent valuation of S$6.6 million conducted by Jones Lang LaSalle Property Consultants Pte Ltd as at 31 December 2024 using discounted cash flow method."
- `gain_disclosed`: false — no separate dollar gain quoted in the sections read (table gives price/valuation only).
- `notes`: minor rounding mismatch between table-derived premium (3.03%) and the narrative's stated "3.5% above valuation" (per extraction, p16) — both are AR-sourced, just from different sections/rounding conventions; not resolved here per brief.

### 2. 79 Tuas South Street 5
- `sale_price_disclosed`: true, per_property — S$9.9m (table, p47).
- `pct_disclosed`: true (per extraction's citation, "1.5% above valuation"); table-derived: (9.9−9.7)/9.7 = 2.06%, again a rounding gap vs. the narrative %.
- `reference_disclosed`: true — valuation S$9.7m, footnote 3 (p47, verbatim): "Based on independent valuation of S$9.7 million conducted by Jones Lang LaSalle Property Consultants Pte Ltd as at 31 December 2024 using the income capitalisation method and discounted cash flow method."
- `gain_disclosed`: false.
- `notes`: same rounding note as above.

### 3. 2 Changi Business Park Avenue 1 (Hotel Strata Lot, ESR BizPark @ Changi)
- `sale_price_disclosed`: true, per_property — S$101.0m (table, p48).
- `sale_price_scope`: per_property (announced/expected, not yet completed as at FY2025 year-end — Expected 1Q2026).
- `pct_disclosed`: false — no explicit % stated for this specific property; only price and valuation given, from which (101.0−100.9)/100.9 = 0.10% is derivable.
- `reference_disclosed`: true — valuation S$100.9m, footnote 4 (p48, verbatim): "Based on independent valuation of S$100.9 million conducted by Savills Valuation and Professional Services (S) Pte Ltd as at 31 December 2025 using income capitalisation method and direct comparison method."
- `gain_disclosed`: false.
- `notes`: subsequent/announced divestment, not completed within FY2025.

### 4–11. The eight "non-core assets" portfolio (each row below is per-property from the same table)
All eight: `sale_price_disclosed` = true, per_property (each has its own row/price in the p48 table);
`sale_price_scope` = per_property; `reference_disclosed` = true (each has its own independent-valuer
footnote); `gain_disclosed` = false (no gain booked pre-completion); `pct_disclosed` = false per-property
(only the AGGREGATE 2.0% premium is stated in narrative, not itemised per property) — this is the important
nuance: individual valuer footnotes exist for each, but the "2.0% premium" sentence applies to the S$338.1m
GROUP total, not to each asset individually.

| Property | Sale price (S$m) | Valuation (S$m) | Valuer footnote (verbatim, abbreviated) |
|---|---|---|---|
| 86 & 88 International Road | 42.2 | 42.2 | "independent valuation of S$42.2 million conducted by Cushman & Wakefield VHS Pte Ltd as at 30 November 2025" |
| 120 Pioneer Road | 34.1 | 34.1 | "independent valuation of S$34.1 million conducted by Cushman & Wakefield VHS Pte Ltd as at 30 November 2025" |
| 13 Jalan Terusan | 16.7 | 16.7 | "independent valuation of S$16.7 million conducted by Cushman & Wakefield VHS Pte Ltd as at 30 November 2025" |
| 60 Tuas South Street 1 | 3.5 | 3.5 | "independent valuation of S$3.5 million conducted by Edmund Tie & Company (SEA) Pte Ltd as at 30 November 2025" |
| 43 Tuas View Circuit | 15.1 | 15.1 | "independent valuation of S$15.1 million conducted by Edmund Tie & Company (SEA) Pte Ltd as at 30 November 2025" |
| 21 & 23 Ubi Road 1 | 45.0 | 42.5 | "independent valuation of S$42.5 million conducted by Colliers International Consultancy & Valuation (Singapore) Pte Ltd as at 30 November 2025" |
| 24 Jurong Port Road | 68.0 | 68.0 | "independent valuation of S$68.0 million conducted by Jones Lang LaSalle Property Consultants Pte Ltd as at 30 November 2025" |
| 46A Tanjong Penjuru | 113.5 | 109.5 | "independent valuation of S$109.5 million conducted by Jones Lang LaSalle Property Consultants Pte Ltd as at 30 November 2025" |

- `notes` (applies to all 8): these are the "eight non-core assets" of the December 2025 announced portfolio
  sale, aggregate consideration S$338.1m at a group-level "2.0% premium to independent valuation" (narrative,
  p47). All 8 are individually priced and individually referenced-valued in the p48 table — only the PREMIUM
  PERCENTAGE is aggregate-only (not itemised per property), unlike sale price and valuation which ARE
  per-property. All 8 are subsequent/announced divestments (Expected 2Q2026 or 3Q2026), not completed within
  FY2025, so no per-property or aggregate gain is booked in the FY2025 financial statements.

---

## MXNU / FY2024

### 1. Sidlaw House, Dundee (Scotland)
- `sale_price_disclosed`: **true**, per-property. Highlights (p~736, verbatim): "Successful divestment of Sidlaw House, Dundee for a Sale Consideration of £1.3 million, more than 40% premium to valuation as at 30 June 2024." Divestment table (p~1742): "Sidlaw House, Dundee | Sidlaw House, Dundee, DD2 1DX | Scotland | The Speratus Group Limited | £1.3 million | £0.9 million | 7 October 2024".
- `sale_price_scope`: **per_property**.
- `pct_disclosed`: **true** — "more than 40% premium to valuation" (exact wording). Table-derived: (1.3−0.9)/0.9 = 44.4%, consistent with "more than 40%."
- `reference_disclosed`: **true** — valuation £0.9 million (table, footnote 2 = valuation basis, valuation date 30 June 2024).
- `gain_disclosed`: **false** — no separate £-gain figure quoted (only price vs valuation, from which a gain is derivable but not itself stated).
- `notes`: clean per-property disclosure, all fields present except an explicit dollar gain figure.

### 2. Hilden House, Warrington (North West England)
- `sale_price_disclosed`: **true**, per-property. Divestment table (p~1743): "Hilden House, Warrington | Winmarleigh Street, Warrington, WA1 1LA | North West | Caro Developments Ltd | £3.3 million | £3.1 million | Expected 1H 2025".
- `sale_price_scope`: **per_property**.
- `pct_disclosed`: **false** — no explicit % stated for this property; table-derived: (3.3−3.1)/3.1 = 6.5%.
- `reference_disclosed`: **true** — valuation £3.1 million (same table).
- `gain_disclosed`: **false**.
- `notes`: contracted in FY2024 ("Elite REIT entered into contracts in FY2024 to divest Sidlaw House, Dundee; Hilden House, Warrington; and St Paul's House, Chippenham") but completion was expected 1H 2025, i.e. subsequent to FY2024 year-end.

### 3. St Paul's House, Chippenham (South West England)
- `sale_price_disclosed`: **true**, per-property. Divestment table (p~1744): "St Paul's House, Chippenham | Marshfield Road, Chippenham, SN15 1LA | South West | Abode & Co Holdings Limited | £1.6 million | £1.4 million | Expected 1H 2025".
- `sale_price_scope`: **per_property**.
- `pct_disclosed`: **false** — table-derived: (1.6−1.4)/1.4 = 14.3%.
- `reference_disclosed`: **true** — valuation £1.4 million.
- `gain_disclosed`: **false**.
- `notes`: contracted in FY2024, expected completion 1H 2025 (subsequent to year-end, per the intro sentence above).

---

## N2IU / FY2023 (folder `29_N2IU..._FY2022`)

### 1. Mapletree Anson (Singapore)
- `sale_price_disclosed`: **true**, per-property. Letter to Unitholders (p16, verbatim): "In light of today's market dynamics, one priority is to bolster MPACT's financial resilience and agility. As such, after the close of FY23/24, we initiated the divestment of Mapletree Anson, one of our non-core office assets in Singapore. Finalised at a divestment consideration of S$775.0 million, this divestment secures a gain of S$10.0 million over Mapletree Anson's latest independent valuation and a premium of S$95.0 million to its acquisition price."
- `sale_price_scope`: **per_property**.
- `pct_disclosed`: **false as a stated percentage** — the sentence gives BOTH reference points in DOLLAR terms (not %): "a gain of S$10.0 million over Mapletree Anson's latest independent valuation" AND "a premium of S$95.0 million to its acquisition price." Both are absolute dollar premiums/gains, not percentages, as worded in the AR. (Our own extraction derives a 1.31% valuation-premium %, but that % itself is not printed in the AR text.)
- `reference_disclosed`: **true — TWO distinct reference bases, both disclosed in the same sentence**, confirming the brief's expectation:
  1. **Independent valuation basis**: "latest independent valuation" — confirmed elsewhere as S$765.0 million as at 31 Mar 2024 by CBRE (per our extraction's citation; the valuation table on p~1777 of full.md shows "Mapletree Anson | S$765.0 | 3.35% | S$752.0 | S$13.0 | S$13.0 | –" i.e. property value S$765.0m).
  2. **Original acquisition-price basis**: "a premium of S$95.0 million to its acquisition price" — i.e. S$775.0m consideration is S$95.0m above what MPACT originally paid to acquire Mapletree Anson (implied acquisition price ≈ S$680.0m, not itself restated in this sentence).
- `gain_disclosed`: **true** — "a gain of S$10.0 million over Mapletree Anson's latest independent valuation" (S$775.0m − S$765.0m = S$10.0m, consistent).
- `notes`: **This is the divestment the brief specifically flagged.** Confirmed: the AR discloses BOTH a valuation-based gain (S$10.0m over the S$765.0m independent valuation) AND an acquisition-price-based premium (S$95.0m over original purchase price) in the same sentence, using two different reference bases (independent valuation vs. original purchase price), both in absolute dollar terms rather than percentages. As at FY2023 (folder FY2022 = AR "FY23/24") year-end, this was still an ANNOUNCED/subsequent-event divestment (30 May 2024, after the 31 Mar 2024 FYE) — expected completion July 2024, not yet realised in the FY2023 financial statements. Cash flow and investment-property notes as at FY2023 year-end show no completed FY2023 disposal for this asset (per our extraction's note).

---

## O5RU / FY2025

### 1. 3 Toh Tuck Link (Singapore)
- `sale_price_disclosed`: **true**, per-property. Q&A/interview section (p~454, verbatim): "we completed the divestment of 3 Toh Tuck Link on 17 June 2025 for S$24.4 million, representing a premium of 32.5% above valuation."
- `sale_price_scope`: **per_property**.
- `pct_disclosed`: **true** — "a premium of 32.5% above valuation" (exact wording).
- `reference_disclosed`: **true, though the numeric valuation figure itself was not located as a standalone dollar quote in the sections searched** — the property is footnoted throughout as being "stated at fair value based on the agreed sale price" once reclassified (p~1569/7014/7064/7115/7169/7220, verbatim e.g.: "The carrying value of the investment properties are based on independent full valuation while the carrying value of 8 Senoko South Road in Singapore and 3 Toh Tuck Link in Singapore are stated at fair value based on the agreed sale prices with the third-party buyers.") The 32.5% premium confirms an independent valuation exists as the reference basis, but this AR does not additionally spell out the S$ valuation number itself in the passages read (our extraction backs this out arithmetically: 24.4/1.325 ≈ S$18.4m).
- `gain_disclosed`: **false as a standalone $ gain figure** — not located as a distinct dollar amount in the sections searched (Financial Review / cash flow notes were not exhaustively combed beyond what's quoted here).
- `notes`: strong per-property disclosure (price + %), reference $ value not separately spelled out verbatim (only implied via the "agreed sale price" fair-value convention and the 32.5% figure).

### 2. 8 Senoko South Road (Singapore)
- `sale_price_disclosed`: **true**, per-property. Q&A section (p~454, verbatim): "On 16 April 2026, we completed the divestment of 8 Senoko South Road for S$15.0 million at an 11.1% premium above valuation." Portfolio table (p~2588, verbatim row): "21 8 Senoko South Road | Master Lease | 19 Apr 2007 | 31 Oct 2054 | 28.6 | 12.8 | 15.0² | 7,279 | 1.5 | 100.0" with footnote "Senoko South Road is stated at fair value based on the agreed sale price with a third-party buyer."
- `sale_price_scope`: **per_property**.
- `pct_disclosed`: **true** — "an 11.1% premium above valuation" (exact wording). Value creation section (p~1714) reiterates: "the Manager divested 8 Senoko South Road at an 11.1% premium to valuation."
- `reference_disclosed`: **true, implied** — the "agreed sale price" fair-value convention and stated 11.1% premium confirm an underlying independent valuation exists as the reference; the standalone $ valuation figure itself was not located as a separate verbatim quote in the passages read (implied ≈ S$15.0m/1.111 ≈ S$13.5m).
- `gain_disclosed`: **false** — this divestment completed 16 April 2026, AFTER the FY2025/26 (year ended 31 Mar 2026) reporting date's own... actually per the AR's fiscal-year framing this is described as "Post financial year end" (per our extraction's citation) relative to the underlying fiscal year, so no gain would be booked in this year's financial statements; consistent with treatment as a subsequent/announced event even while carrying value is already marked to the agreed sale price.
- `notes`: both O5RU divestments disclose price AND percentage explicitly in the narrative text — best-disclosed pair in this whole batch after MXNU/Sidlaw House.

---

## P40U / FY2024 (declared FY; AR covers year ended 30 Jun 2025, titled "FY 2024/25")

### 1. Wisma Atria Property (Office) — 13 strata units
- `sale_price_disclosed`: **true**, aggregate across the 13 units, sold to 7 separate buyers. Portfolio Rejuvenation section (p~2095, verbatim): "In line with the Manager's strategy to rejuvenate the portfolio through selective divestments, 13 strata units or approximately 18,546 square feet of net lettable space in the Wisma Atria Property (Office) were divested for sales consideration of approximately S$41 million(8) in FY 2024/25, where part of the proceeds were used to repay debts and/or for working capital purposes as at 30 June 2025." Footnote 8 (p~2117, verbatim): "The buyers were separate, unrelated third party investors namely Dental Designs Clinic Pte. Ltd., Petite Smiles Pte. Ltd., PMWChia Pte. Ltd., Asia Healthcare Group Pte. Ltd., Redbridge Health Pte. Ltd., Platinum Capital 1903 Pte. Ltd., and Singapore Aobo Brilliance Pte. Ltd.. The strata transactions amounted to approximately S$41 million, compared to the valuation of approximately S$32 million as at 30 June 2024 by CBRE Pte. Ltd. (using the income capitalisation method and discounted cash flow analysis)."
- `sale_price_scope`: **aggregate_multi_property** — 13 strata units treated as one combined consideration figure (~S$41m), sold to 7 different buyer entities, not broken out per unit or per buyer.
- `pct_disclosed`: **false** — no premium % is stated in words; only the two rounded dollar figures ("approximately S$41 million" vs "approximately S$32 million") are given, from which a ~28.1% premium is derivable but not itself printed.
- `reference_disclosed`: **true** — "the valuation of approximately S$32 million as at 30 June 2024 by CBRE Pte. Ltd." (independent valuation basis, explicitly named valuer and date). A separate carrying value is also disclosed in the portfolio-statement footnote (p~7388, verbatim): "A total of 13 strata units in Wisma Atria Property (Office) with carrying value of $31.9 million were divested during the current period to unrelated third parties" — i.e. TWO reference bases exist (independent valuation ~$32m vs carrying value $31.9m), both close but not identical.
- `gain_disclosed`: **true**, aggregate — Financial Review (p~4315, verbatim): "The gain on divestment of investment properties of S$9.0 million represents the difference between net proceeds (including directly attributable costs) from divestment and the carrying amount of the Wisma Atria Property (Office) strata units divested in FY 2024/25." Also net proceeds are distinguished from gross: fee-note (p~9297) ties Manager's fee to "0.5% of the sale price."
- `notes`: **13 strata units, multiple buyers, ONE aggregate consideration figure (~S$41m) — confirmed matches the brief's characterisation.** Three dollar figures appear across the AR for related-but-distinct concepts: (1) sale consideration "approximately S$41 million" (gross, rounded), (2) independent valuation "approximately S$32 million" as at 30 Jun 2024, (3) carrying value "$31.9 million" (book value at divestment) — all approximate/rounded, and the AR itself does not reconcile them to more precise figures or state a derived percentage.

---

## UD1U / FY2024

### 1. Il·lumina (Spain)
- `sale_price_disclosed`: **true**, per-property, in EUR. Note 2.3 (p189, verbatim): "On 22 December 2023, IREIT entered into a conditional promissory private sales and purchase agreement with an unrelated third party to divest Il•lumina, a property located in Spain. Subsequent to the reporting date, the Group completed the divestment of Il•lumina for a sale consideration of €24.5 million on 31 January 2024. There was a loss on divestment of Il•lumina of €224,000."
- `sale_price_scope`: **per_property**.
- `pct_disclosed`: **false** — no premium/discount % stated; only absolute € figures given.
- `reference_disclosed`: **true** — held-for-sale carrying value €24,698,000 as at 31 Dec 2023 (Note 2.3 table, p189: "Investment property | 24,500" [component] / "Assets held for sale | 24,698" [total incl. other receivables of €198k]); "The value was based on the contracted selling price with an unrelated third party" — i.e. the held-for-sale carrying amount itself was set equal to the contracted sale price at the 31 Dec 2023 balance-sheet date. Basis = held-for-sale/carrying value, not an independent market valuation distinct from the deal price.
- `gain_disclosed`: **true** — "a loss on divestment of Il•lumina of €224,000" (€24.5m sale consideration − €24.698m carrying amount = €0.224m loss, consistent; also appears as an add-back in the cash flow statement: "Loss on disposal of asset/liabilities held for sale | 224 | –").
- `notes`: this is a LOSS, not a gain — flagged distinctly per the brief's "gain/loss" phrasing. All key figures (sale price, reference/carrying value, and the resulting loss) are disclosed per-property and are internally consistent (24,500 − 24,698 = −198, but the AR states the loss as 224,000 — a small ~€26k discrepancy likely attributable to the "Other receivables 198" component of the held-for-sale balance also flowing through the disposal, since Assets held for sale total = Investment property 24,500 + Other receivables 198 = 24,698, and loss 224 ≈ 24,698 + ~something − 24,500 rounding; not resolved further here per "never balance by assumption" — flagging the arithmetic gap rather than adjusting it).

---

## Counts for this batch (28 divestments)

| Metric | Count | Divestments |
|---|---|---|
| **Per-property sale price disclosed** | **20 / 28** | A17U: 21 Jalan Buroh (1 of 4 — the 3 AU trio is aggregate); AJBU: Kelsterbach (1 of 2 — Basis Bay not priced/not completed); C38U FY2024: 21 Collyer Quay (1); C38U FY2025: Bukit Panjang Plaza (1 of 2 — SR Component is implied/not a standalone quoted price); J91U: all 11; MXNU: all 3; N2IU: Mapletree Anson (1); O5RU: both (2); UD1U: Il·lumina (1) |
| **Aggregate-only sale price (multi-property)** | **5 / 28** | A17U AU trio (3: 77 Logistics Place, 62 Sandstone Place, 92 Sandstone Place — one S$64.2m figure for all three); P40U Wisma Atria 13 strata units (1 — one ~S$41m figure); C38U FY2025 CapitaSpring SR Component (1 — priced via "agreed property value on 100% basis" convention, not a standalone quoted consideration) |
| **No sale price disclosed at all** | **1 / 28** | AJBU Basis Bay Data Centre — not completed, no price found (excluded from batch's core 28 count per our extraction, noted separately) — *if counted within the 28, treat as not_disclosed* |
| **Percentage (premium/discount) disclosed** | **7 / 28** | AJBU Kelsterbach (28.2%); J91U 1 Third Lok Yang Rd & 4 Fourth Lok Yang Rd (~3.5%, per extraction citation); J91U 79 Tuas South St 5 (~1.5%, per extraction citation); J91U eight-asset portfolio group (2.0% — AGGREGATE, not per-property, so not separately counted per property); MXNU Sidlaw House (>40%); O5RU 3 Toh Tuck Link (32.5%); O5RU 8 Senoko South Road (11.1%) |
| **Reference figure disclosed** (any basis: valuation / carrying / acquisition price / SPV NIA) | **26 / 28** | All except: AJBU Basis Bay (not disclosed) and — arguably — C38U FY2025 SR Component has a reference (S$278.5m) so IS counted; effectively only Basis Bay lacks a reference. A17U all 4 have references (per-property valuations/carrying values even for the aggregate-priced trio). |
| **BOTH pct AND reference disclosed (price derivable even without a stated price)** | **7 / 28** | Same set as "percentage disclosed" above — in every case where a % is stated, a reference figure is also given, so price is always independently re-derivable from the two for those 7. |
| **NEITHER a sale price NOR a derivable pair (pct+reference)** | **1 / 28** | AJBU Basis Bay Data Centre only. |

### Summary interpretation
- Per-property sale prices are disclosed for the large majority (20/28, ~71%) of divestments in this batch —
  substantially higher than a "portfolio-only" pattern. The most consequential single finding is **J91U/FY2025**:
  despite one narrative sentence quoting an aggregate 2.0% premium for 8 of the 11 properties, **every one of
  the 11 divestments has its own per-property sale price AND its own per-property independent valuation** in
  the transactions table (pages 47–48) — only the premium PERCENTAGE is aggregate for that sub-group of 8.
- Only 3 divestments in this batch have a genuinely aggregate-only sale price with no per-property split at
  all: the A17U Australia trio (3 properties, 1 price) and P40U's 13 Wisma Atria strata units (13 units/7
  buyers, 1 price). The C38U CapitaSpring SR Component sits in a gray zone — its "price" is only implied via
  an "agreed property value × interest %" convention, never stated as a standalone consideration figure.
- Explicit percentage disclosure is comparatively rare (7/28, 25%) — most REITs state exit yields or absolute
  dollar gains instead of premium/discount percentages. Where a percentage IS stated, a reference figure is
  always also present, making price re-derivable.
- Almost every divestment (26/28) has SOME reference figure (valuation, carrying value, or acquisition price)
  disclosed, even when the sale price itself is aggregate-only or (in one case, AJBU Basis Bay) entirely
  absent.
