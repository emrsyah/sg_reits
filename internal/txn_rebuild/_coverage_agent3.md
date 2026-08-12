# Agent 3 — Divestment Disclosure Coverage (28 divestments)

Source: AR text in `parsed_reports_datalab/<folder>/full.md`. `extracted/*` JSON used only to
locate page numbers. All quotes verbatim below (currency symbols as printed in source, `S\$`
markdown-escaped dollar signs simplified to `S$`/`€`/`US$` etc for readability).

## A17U / FY2025 — folder `05_A17U.SI_..._FY2025` (9 divestments)

CLAR tabulates ALL NINE divestments individually with BOTH sale (divestment) consideration and
independent valuation, in a single table (full.md lines 1874-1882, Portfolio/Divestments
section). Per-property gain in dollars is NOT disclosed — only the aggregate "Gain on disposal of
investment properties" of S$19,281k (Statement of Total Return, p113/full.md L5360) covers all
nine (plus any other IP movements). No per-property gain $ anywhere.

| property_name | sale_price_disclosed | sale_price_scope | pct_disclosed | reference_disclosed | gain_disclosed | notes |
|---|---|---|---|---|---|---|
| 30 Tampines Industrial Avenue 3 | true — "23.0" (S$23.0m), table row | per_property | false (only portfolio-level ~9%) | true — valuation S$22.0m, table col + footnote(2) "Independent valuation" | false (only aggregate S$19,281k) | Divestment table L1875; footnote basis = independent valuation |
| 31 Ubi Road 1 | true — S$30.0m, table row | per_property | false | true — S$29.5m valuation | false | L1878 |
| 10 Toh Guan Road | true — S$84.5m | per_property | false | true — S$79.7m valuation | false | L1880 |
| 9 Changi South Street 3 | true — S$51.5m | per_property | false | true — S$47.5m valuation | false | L1879 |
| 19 & 21 Pandan Avenue | true — S$140.0m | per_property | false | true — S$132.6m valuation | false | L1881 |
| 95 Gilmore Road | true — S$90.0m | per_property | false | true — S$82.2m valuation | false | L1877; carrying value also disclosed elsewhere (S$80,643k / A$93,000k, Note portfolio statement L5687) |
| Astmoor Road | true — S$52.5m | per_property | false | true — S$46.6m valuation | false | L1876; carrying S$48,273k / GBP28,500k (L5723) |
| Parkside | true — S$26.5m | per_property | false | true — S$18.3m valuation | false | L1874; carrying S$18,251k / USD13,600k (L5835) |
| 8700-8770 Nimbus | true — S$8.5m | per_property | false | true — S$7.7m valuation | false | L1882; carrying S$7,381k / USD5,500k (L5842) |

Portfolio-level narrative (L1864, L769): "the Manager completed the divestment of nine properties
across Singapore, the US, Australia and the UK, for a total sale consideration of S$506.5
million. This represents a premium of approximately 9% above the total independent
[valuation]... and about 14% above their aggregate original purchase price" — aggregate pct
disclosed but not attributed per-property.

## BTOU / FY2024 — folder `26_BTOU.SI_..._FY2024` (2 divestments)

| property_name | sale_price_disclosed | sale_price_scope | pct_disclosed | reference_disclosed | gain_disclosed | notes |
|---|---|---|---|---|---|---|
| Capitol (Sacramento, CA) | true — "In October 2024, we divested Capitol in Sacramento, California for a net consideration of approximately US$110 million" (L347); divestments table row "Capitol | Sacramento, California | 110³ | 118.0 | 400 CM OWNER, LLC | 28 October 2024" (L1177) | per_property | false | true — valuation US$118.0m (table col, footnote 3 = independent valuation CBRE) | false per-property (only aggregate FY2024 "loss on disposal of investment property" figure in Statement of Comprehensive Income, not deal-specific per grep) | Net consideration language ("net consideration" not gross); divestment fee US$0.6m payable (Note 1(a)) |
| Plaza (Secaucus, NJ) | true — "In February 2025, we completed the sale of Plaza in Secaucus, New Jersey for a net consideration of approximately US$40 million" (L347); table row "Plaza | Secaucus, New Jersey | 40⁴ | 43.7 | 500 Plaza Ground Lessor LLC | 25 February 2025" (L1178) | per_property | false | true — valuation US$43.7m (Cushman & Wakefield, footnote 4) | not applicable — subsequent event, no FY2024 accounting gain (asset held for sale at 31 Dec 2024, reclassified at carrying US$43,700k, matches valuation) | Subsequent event disclosed within FY2024 AR; sale completed Feb 2025 |

## CY6U / FY2025 — folder `08_CY6U.SI_..._FY2025` (2 divestments) — DECISIVE CASE

Exhaustive search performed across: Manager's/CEO's report narrative, Capital Recycling section
(p35, L2198-2204), portfolio review highlights (L775-945, L1210-1211), Note 25 "Disposal group
classified as held for sale" (financial statements, L6380-6434), segment/associate notes, and a
full-document grep for "premium", "independent valuation", "INR", "3%", "13.7%". **No dollar
figure for either deal's independent valuation appears anywhere in the AR.** Only the enterprise
value/consideration in INR (and SGD-converted) and the premium percentage are disclosed. Note 25
gives cash/asset/liability breakdown of the disposal group and "Net assets of disposal group"
S$155,841k — this is net asset value (accounting), not an independent valuation, and is not
compared to a valuation figure anywhere.

| property_name | sale_price_disclosed | sale_price_scope | pct_disclosed | reference_disclosed | gain_disclosed | notes |
|---|---|---|---|---|---|---|
| CyberPearl (Hyderabad) + CyberVale (Chennai) | true — "divested at an enterprise value of INR 11,031 million (approximately S$161.7 million)" (L2202); Note 25 "Net sales consideration after divestment expenses 159,922" S$'000 (L6407) | aggregate_multi_property (both properties sold together as one enterprise-value transaction, and structurally as two dormant subsidiaries of CITPPL) | true — "The sale was executed at a 3% premium to their independent valuations" (L2202) | **false — no independent valuation DOLLAR figure disclosed anywhere.** Note 25 only shows disposal-group "Net assets of disposal group" S$155,841k (accounting net assets, not valuation) and investment-property carrying value S$138,890k (Note 18/19 cross-ref) — neither is labelled "independent valuation" | true — "Gain on divestment 4,081" S$'000 (Note 25, L6406) vs the S$155,841k net-assets-of-disposal-group base | Percentage-only disclosure of the valuation comparison; no reference dollar figure exists in the AR, so the 3% cannot be tied to a specific valuation number. Counterparty/buyer not named. |
| 20.2% stake in three DC developments (DC Chennai/ITPH, DC Navi Mumbai) | true — "valued at approximately INR 7,021 million (S$99.7 million)" (L2204); also L923 "total consideration of INR 7.0 B (~S$99.7 M)" | aggregate_multi_property (20.2% of three separate subsidiaries/DCs sold as one transaction to CIDCF) | true — "The partial divestment was executed at a 13.7% premium to their independent valuation" (L2204) | **false — no independent valuation DOLLAR figure disclosed anywhere.** SPA/subscription-agreement note (L6429-6433) gives no valuation figure, only structural/ownership description; "Figures are indicative and are subjected to further adjustments" (footnote L945) | false — no gain/loss $ disclosed (deal completed 27 Feb 2026, after FYE; described as indicative) | Counterparty CIDCF named. Post-divestment stake 79.8% disclosed. As at report date, considered a subsequent/near-year-end event; no dollar valuation ever appears despite exhaustive search. |

**CONFIRMED FINDING for the brief's decisive question:** for both CY6U FY2025 divestments, the AR
discloses ONLY a percentage premium (3% and 13.7% respectively) with NO corresponding independent
valuation dollar/INR figure anywhere in the document (verified via full-text grep for
"valuation", "premium", "INR", and manual read of Capital Recycling narrative + Note 25 + SPA
note). This is a genuine percentage-only disclosure case — the price is NOT derivable from a
reference figure because no reference dollar figure is disclosed at all; only the sale
consideration itself and the bare percentage are known.

## DCRU / FY2024 — folder `13_DCRU.SI_..._FY2024` (1 divestment)

| property_name | sale_price_disclosed | sale_price_scope | pct_disclosed | reference_disclosed | gain_disclosed | notes |
|---|---|---|---|---|---|---|
| 2401 & 2403 Walsh Avenue | true — Note 6b/subsequent-events text: "entered into a purchase and sales agreement for the proposed divestment of 2401 Walsh Avenue and 2403 Walsh Avenue at a proposed sale price of US$160.2 million (based on 90% ownership interest)... sold to a third-party at the carrying amount as at 31 December 2023 and sale of the properties was completed on 12 January 2024" (L6348) | aggregate_multi_property (both addresses sold as one deal/one sale price) | false — no premium/discount % stated (sold AT carrying amount = 0% by construction, not stated as a %) | true — reference basis = carrying amount ("sold ... at the carrying amount as at 31 December 2023"); portfolio statement shows Walsh Ave properties with valuation columns nil post-sale (L1077-1078, L1233-1234; carrying figures at L6411-6412: 2401 Walsh $110,000k, 2403 Walsh $68,000k, 100% basis) | true (implicitly zero) — sold at carrying value = nil accounting gain, stated as-is ("sold ... at the carrying amount"), not a derived figure | US$160.2m figure is on a 90% ownership-interest basis (per JV/co-investment structure) vs. the 100%-basis carrying value figures in the portfolio statement (~$178.0m combined per Note 6, matching our extraction's aggregate). Two different bases (90%-interest price vs 100%-basis carrying) — flagged as an internal consistency issue, both figures ARE disclosed, just on different ownership bases. |

## N2IU / FY2024 — folder `29_N2IU.SI_..._FY2023` (1 divestment)

Per brief's folder-offset rule, N2IU declared FY2024 → folder `29_N2IU..._FY2023`.

| property_name | sale_price_disclosed | sale_price_scope | pct_disclosed | reference_disclosed | gain_disclosed | notes |
|---|---|---|---|---|---|---|
| Mapletree Anson | true — "Mapletree Anson was divested to an external party on 31 July 2024 for cash consideration of $775,000,000" (Note 14, L6772); also "MPACT divested non-core asset, Mapletree Anson, at a consideration of S$775.0 million" (L1520) | per_property (single asset) | false — no premium/discount % vs valuation stated in narrative (our extraction's 1.31% is a derived figure, not an AR-quoted %) | true — implied via note that divestment "delivered financial benefits" but explicit valuation $ figure not located in the divestment narrative section searched (L1518-1522, L1893-1895); Note 14 (L6772) states only cash consideration and resulting gain, no separate valuation line in the text searched | true — "resulting in a net gain on divestment of $4,006,000" (L6772); also stated as "S$4.0 million net divestment gain" (L1520) | Currency SGD throughout (domestic Singapore asset). Buyer named: GES Tradewinds Pte. Ltd. (L1895, L111). Gain is vs carrying/book value (accounting), consistent with Note 14 wording "net gain on divestment" — this is the accounting P&L gain, not an independent-valuation premium %. |

## N2IU / FY2025 — folder `29_N2IU.SI_..._FY2024` (3 divestments)

Per brief's folder-offset rule, N2IU declared FY2025 → folder `29_N2IU..._FY2024`.

| property_name | sale_price_disclosed | sale_price_scope | pct_disclosed | reference_disclosed | gain_disclosed | notes |
|---|---|---|---|---|---|---|
| TS Ikebukuro Building (TSI) | true — "TSI was divested on 22 August 2025 for JPY5,400.0 million (S$48.7 million)" (L1551); Note "TSI was divested to an external party on 22 August 2025 for cash consideration of JPY5,400,000,000" (L6576) | per_property | false — no premium/discount % vs valuation stated for TSI specifically (only Festival Walk Tower gets an explicit % — see below) | partial — footnote 1 (L1925) states independent valuations of TSI/ASY as at 31 Mar 2025 were used for SGD comparison purposes but does not print a specific dollar valuation figure for TSI alone in the text located | true — "resulting in a net loss on divestment of $3,093,000" (L6576) | Consideration currency = JPY (5,400.0 million); gain/loss reported in SGD ($3,093,000 loss). Combined TSI+ASY consideration stated as JPY8,730.0m / S$78.7m (L542, L851, L1551) |
| ABAS Shin-Yokohama Building (ASY) | true — "ASY was divested on 28 August 2025 for JPY3,330.0 million (S$30.0 million)" (L1551); Note "ASY was divested to an external party on 28 August 2025 for cash consideration of JPY3,330,000,000" (L6577) | per_property | false | partial — same footnote 1 basis as TSI, no standalone dollar valuation figure for ASY located | true — "resulting in a net gain on divestment of $408,000" (L6577) | Consideration currency = JPY (3,330.0 million); gain in SGD ($408,000 gain) |
| Festival Walk Tower (office component) | true — "Festival Walk Tower was divested on 2 February 2026 for HKD1,960.0 million (S$328.1 million)" (L1551, also L575); "divested to an unrelated third party, CityU Limited, for HKD1,960.0 million (S$328.1 million), in line with its independent valuation (as at 30 November 2025)" (L1921) | per_property (office tower component only — retail mall retained) | true — "The divestment consideration was at a 15.9% discount (in local currency terms) to its purchase price of HKD2,331.9 million (S$406.1 million)" (L1921) | true — TWO references disclosed: (1) independent valuation — "in line with its independent valuation (as at 30 November 2025)" (consideration ≈ valuation, no separate $ delta given, valuer named Knight Frank Petty Limited, DCF + term-and-reversion method, footnote 3 L1929); (2) original purchase price HKD2,331.9m (S$406.1m), footnote 4 | not disclosed as a per-property $ gain/loss in the narrative sections searched (a one-off tax charge of S$8.3m on completion is disclosed, L356/845/1589, but that is tax not divestment gain/loss) | Consideration currency = HKD; comparison % stated "in local currency terms" (HKD2,331.9m vs HKD1,960.0m purchase-price comparison); SGD figures given for both (S$328.1m consideration vs S$406.1m purchase price) but the 15.9% is explicitly a local-currency calc. Buyer named: CityU Limited. Only Festival Walk Tower — of these three — has a stated percentage in the AR narrative. |

## ODBU / FY2024 — folder `39_ODBU.SI_..._FY2024` (2 divestments)

| property_name | sale_price_disclosed | sale_price_scope | pct_disclosed | reference_disclosed | gain_disclosed | notes |
|---|---|---|---|---|---|---|
| Hudson Valley Plaza — Lowe's & Sam's Club buildings | true — "the divestment of Lowe's and Sam's Club properties within Hudson Valley Plaza, New York. The divestment consideration of US$36.5 million" (L1722); also "for a total consideration of US$36.5 million" (L699) | aggregate_multi_property (two buildings, Lowe's + Sam's Club, sold together as one consideration within the larger Hudson Valley Plaza parcel; rest of the plaza retained) | true — "represents an attractive premium of 4.3% over the independent valuation of US$35.0 million as at 30 June 2024, and a 17.5% premium over the purchase price of US$31.1 million" (L1722); also stated in highlights "4.3% over the independent valuation and 17.5% above the purchase price" (L699) and "a 17.5% premium to the purchase price" (L603) | true — TWO references: independent valuation US$35.0m (30 Jun 2024) AND original purchase price US$31.1m, both explicitly named and quantified (L1722) | not disclosed per-property in narrative, but derivable: Statement of Total Return "Gain on divestment of investment properties" is a single-line aggregate of US$2,156k for FY2024 (per our extraction's page-32 cash-flow cite); this is the ONLY completed IP divestment in FY2024 so the aggregate figure is effectively attributable, though the AR does not itself state "gain from this deal = $2,156k" in the property-level narrative text searched | Best-disclosed deal of the batch — both percentage AND both reference bases (valuation + cost) stated explicitly and verbatim. Buyer not named. |
| Albany — Supermarket | true — "the divestment of Albany-Supermarket, New York. The divestment consideration of US$23.8 million" (L1724); Note "completed the divestment of Albany Supermarket for a divestment consideration of US$23.8 million" (L7588) | per_property | true — "is 4.2% higher than the purchase price of US$22.9 million" (L1724) | true — reference = original purchase price US$22.9m (explicit); ALSO carrying value/fair value equals the sale price itself: "classified as an investment property held for divestment and the divestment was completed on 17 January 2025 for a consideration of US$23.8 million, which is also the fair value as at 31 December 2024 based on the independent valuation undertaken by CBRE, Inc." (L6600) — i.e. independent valuation = US$23.8m = sale price exactly (0% premium/discount vs valuation, though only the purchase-price % is stated as a "%") | not disclosed as its own $ figure in FY2024 (transaction/gain falls into FY2025 per our extraction's note; consistent with completion date 17 Jan 2025 being after FYE) | Subsequent event disclosed within the FY2024 AR (transaction completed after 31 Dec 2024 but before report finalization/is a post-balance-date completed divestment held-for-sale at year end). Buyer not named. |

## SET / FY2024 — folder `36_SET.SI_..._FY2024` (6 divestments)

All six are disclosed on a PER-PROPERTY basis, both in the Manager's Report narrative (with the €
premium disclosed in both % and € terms) and in the Portfolio Statement (Divestments) table
(L1823-1837, columns: consideration / valuation / date).

| property_name | sale_price_disclosed | sale_price_scope | pct_disclosed | reference_disclosed | gain_disclosed | notes |
|---|---|---|---|---|---|---|
| Grójecka 5 (Warsaw, Poland) | true — "completed the divestment of Grójecka 5 in Warsaw, Poland, for €15.9 million" (L1798); table "15.9" (L1823) | per_property | true — "representing a 7.5% or €1.1 million premium over the 31 December 2023 independent valuation" (L1798) | true — independent valuation €14.8m (31 Dec 2023, conducted by CBRE), both narrative and table col (L1798, L1823) | true — €1.1 million premium in absolute € terms is itself the implied gain vs valuation (explicitly stated, not derived: "7.5% or €1.1 million premium") | Buyer Solida Capital Europe named |
| Grandinkulma (Vantaa, Finland) | true — "for €5.4 million" (L1802); table "5.4" (L1825) | per_property | true — "which was 3.6% or €0.2 million [lower]" (L1802, text continues off-grep but matches extraction −3.6%) | true — independent valuation €5.6m (implied 30 Jun 2024 basis per table footnote 7; text says "3.6% or €0.2 million" below valuation) | true — €0.2 million disclosed in absolute terms | Buyer Revelon OY (local real estate developer) named |
| Lénine (Paris, France) | true — "for €3.1 million" (L1812); table "3.1" (L1827) | per_property | true — "which was 0.3% or €0.01 million lower than the 30 June 2024 independent valuation" (L1812) | true — independent valuation €3.1m (30 Jun 2024, CBRE) | true — €0.01 million disclosed | Buyer IMODEV Group named |
| Via Brigata Padova 19 (Padova, Italy) | true — "for €1.8 million" (L1808); table "1.8" (L1829) | per_property | true — "reflecting a 24.1% or €0.4 million premium over the 31 December 2023 independent valuation conducted by Savills" (L1808) | true — independent valuation €1.5m (31 Dec 2023, Savills) | true — €0.4 million disclosed | Buyer PDI Europe S.A. named |
| Via Rampa Cavalcavia 16-18 (Mestre, Italy) | true — "for €5.9 million" (L1816); table "5.9" (L1830) | per_property | true — "achieving a 36.6% or €1.6 million premium over the 30 June 2024 independent valuation conducted by Savills" (L1816); also repeated at L7048 ("divested for a consideration of €5.9 million, €1.6 million or 36.6% above the latest valuation in June 2024") | true — independent valuation €4.3m (30 Jun 2024, Savills) | true — €1.6 million disclosed | Buyer Agenzia del Demanio named |
| Via della Fortezza 8 (Florence, Italy) — announced/held-for-sale at FYE, completed 5 Mar 2025 | true — carried "at the contracted selling price of €15.0 million based on a binding offer from a purchaser" (L1732); table "15.0" (L1837) | per_property | true (implied via table, but not narrated in prose the way the other five are) — table shows consideration €15.0m vs valuation €15.1m (implies a small discount, ~−0.7%, matching our extraction's gain_loss_pct) | true — valuation €15.1m in the table (L1837, footnote 7) | not disclosed (deal not yet completed/recognised as of FYE; classified as asset held for sale) | Buyer "TBC" at FYE (completed post-year-end to an undisclosed purchaser per our extraction note); this is the one SET deal where the % is only visible in the table, not spelled out in prose the way the other five are — still counts as disclosed since both figures are printed. |

## T82U / FY2024 — folder `37_T82U.SI_..._FY2024` (1 divestment — aggregate strata-unit deal)

Three figures are genuinely in play in the AR, covering THREE DIFFERENT POPULATIONS of strata
units:

1. **$58.3 million** — the FULL population of strata-unit SALE AGREEMENTS/transactions entered
   into during FY2024 (some completed in FY2024, one completed 6 Jan 2025). Quote: "we divested
   $58.3 million of strata units at Suntec City Office Towers at an average price of 24.5% above
   book value" (L286); footnote clarifies "The transactions in respect of the sale of strata
   units amounting to $58.3 million... were entered into in FY2024. The sale of strata units
   amounting to $41.9 million[7 units], were completed in FY 2024 while the balance strata unit
   sale [1 unit] was completed on 6 January 2025." (L848).
2. **$47.1 million** — the aggregate INDEPENDENT VALUATION of that SAME $58.3m population of
   strata units (i.e., the denominator for the 24.5% figure), footnote 2: "Based on the valuation
   of $47.1 million derived by multiplying the Rate of Lettable Floor Area ($ per square metre)
   per the 31 December 2023 (in respect of the $41.9 million divested in FY2024) and 31 December
   2024 (in respect of the balance strata unit sale completed on 6 January 2025) independent
   valuation reports by the net lettable area of the divested strata units..." (L849).
3. **$34.402 million** — Note 6's narrower population: the SIX strata units that both were
   entered into AND fully COMPLETED within FY2024 (excludes the 7th unit whose sale completed 6
   Jan 2025). Quote: "Suntec REIT had completed the divestment of six (2023: four) strata units
   in Suntec City Office to unrelated third parties. These divested strata units contributed to a
   net gain of $14,992,000 in the financial year ended 31 December 2024" (L4970). Our extraction's
   `carrying_value_basis` (from Note 6 movement schedule) ties $34.402m to these six completed
   units' carrying amount, giving net gain $14.992m — a ~43.6% gain-on-book for that narrower
   population, NOT the 24.5% headline.

**The correct denominator for the disclosed 24.5% is the $47.1 million independent valuation
figure (population = all $58.3m of FY2024-entered strata transactions, 7 units total, whether
completed in FY2024 or 6-Jan-2025)** — this is explicitly what footnote 2 constructs the 24.5%
from. The $34.402m Note 6 carrying amount covers a narrower, six-unit-only, fully-FY2024-completed
population and produces a different (undisclosed-as-a-%) ~43.6% book gain that the AR does not
present as a headline percentage anywhere.

| property_name | sale_price_disclosed | sale_price_scope | pct_disclosed | reference_disclosed | gain_disclosed | notes |
|---|---|---|---|---|---|---|
| Suntec City Office Towers strata units (aggregate) | true — "$58.3 million" (L286, L842) | aggregate_multi_property (7 strata units across the FY2024 sale-agreement population; buyers: Felix Petroleum Pte. Ltd., Internet Sharing Pte. Ltd., Tayen Investment Pte. Ltd., Nuodasi International Trading Pte. Ltd., +1 unnamed for the 7th unit per L848) | true — "an average price of 24.5% above book value" (L286, L842) | true — TWO references disclosed for different populations: (a) $47.1m independent valuation for the $58.3m/7-unit population (footnote 2, L849) — this is the correct denominator for the 24.5%; (b) $34.402m Note 6 carrying amount for the narrower 6-unit-completed-in-FY2024 population (L4970, Note 6) | true (for the narrower 6-unit population only) — "net gain of $14,992,000" (L4970); NOT disclosed for the full $58.3m/7-unit population as a single $ gain figure | AR calls the 24.5% comparison basis "book value" in the headline prose (L286/842) but footnote 2 clarifies the denominator is actually the independent valuation reports ($47.1m), not simple book/carrying value — the AR's own labelling ("book value") is loose relative to its own footnote methodology. Population mismatch across the three cited figures is the key nuance for this deal. |

## UD1U / FY2025 — folder `20_UD1U.SI_..._FY2025` (1 divestment — Il·lumina, technically an FY2024 completion appearing in the FY2025 AR's comparative period)

| property_name | sale_price_disclosed | sale_price_scope | pct_disclosed | reference_disclosed | gain_disclosed | notes |
|---|---|---|---|---|---|---|
| Il·lumina (Spain) | true — "the Group completed the divestment of Il·lumina for a sale consideration of €24.5 million on 31 January 2024" (L6841); cash-flow statement "Proceeds from disposal of assets/liabilities held for sale ... 24,500" (€'000, FY2024 comparative column, L6825) | per_property | false — no premium/discount % stated anywhere located (searched narrative L6841, cash-flow note, occupancy tables at L1699/1716/1730 which only show occupancy %, not price %) | **false — no independent valuation or carrying-value dollar figure disclosed anywhere in the FY2025 AR.** Il·lumina is absent from the FY2025 Statement of Portfolio (divested before the FY2025 period began) and no standalone valuation/carrying figure for it is printed; only the cash-flow "Loss on disposal of assets/liabilities held for sale ... 224" (€'000, L6815) is given | true (absolute € only, no %) — "Loss on disposal of assets/liabilities held for sale" €224,000 (L6815, FY2024 comparative column) | This is a case of sale price + absolute € loss disclosed, but NO reference/valuation figure and NO percentage — i.e., neither pct_disclosed nor reference_disclosed is true, so the deal falls in the "neither disclosed nor derivable" bucket despite having both a sale price and a gain/loss figure. Counterparty unnamed ("unrelated third party", L6841). Agreement dated 22 Dec 2023, completed 31 Jan 2024. |

---

## Counts — Agent 3 batch (28 divestments)

- **Per-property sale price disclosed:** 27 of 28 (all except CY6U's two deals count as
  aggregate_multi_property rather than strict per_property, and DCRU's Walsh Ave is also
  aggregate_multi_property — see scope column). Recount by strict `sale_price_scope`:
  - `per_property`: 23 (A17U ×9, BTOU ×2, N2IU FY2024 ×1, N2IU FY2025 ×3, ODBU Albany ×1, SET ×5
    completed + Via della Fortezza table-only, T82U counted as aggregate not per-property, UD1U
    ×1) — precise tally below.
  - `aggregate_multi_property`: 5 (CY6U ×2, DCRU Walsh Ave ×1, ODBU Hudson Valley Lowe's/Sam's ×1,
    T82U strata ×1)
  - `not_disclosed`: 0
  - **Total with SOME sale price disclosed (per-property or aggregate): 28 of 28**

- **Percentage (premium/discount) disclosed:** 24 of 28
  (A17U: 0/9 per-property, only portfolio-aggregate ~9%; BTOU: 0/2; CY6U: 2/2; DCRU: 0/1; N2IU
  FY2024: 0/1; N2IU FY2025: 1/3 [Festival Walk Tower only]; ODBU: 2/2; SET: 6/6; T82U: 1/1
  [aggregate 24.5%]; UD1U: 0/1)
  → 0+0+2+0+0+1+2+6+1+0 = **12 of 28** (correcting the miscount above — see per-deal table; A17U's
  9 per-property deals have NO per-property %, only a portfolio-wide %)

- **Reference figure disclosed (valuation, book/carrying value, or original purchase price):**
  A17U 9/9, BTOU 2/2, CY6U 0/2, DCRU 1/1, N2IU FY2024 0/1 (not located in narrative), N2IU FY2025
  2/3 (TSI/ASY only partial via footnote, Festival Walk Tower yes explicit), ODBU 2/2, SET 6/6,
  T82U 1/1 (two references for two populations), UD1U 0/1
  → 9+2+0+1+0+2+2+6+1+0 = **23 of 28**

- **BOTH a percentage AND a reference disclosed (price derivable):**
  A17U 0/9, BTOU 0/2, CY6U 0/2 (pct yes, reference no — this is the crux), DCRU 0/1, N2IU FY2024
  0/1, N2IU FY2025 1/3 (Festival Walk Tower), ODBU 2/2, SET 6/6, T82U 1/1, UD1U 0/1
  → 0+0+0+0+0+1+2+6+1+0 = **10 of 28**

- **NEITHER a sale price NOR a derivable pair (pct+reference) — i.e., genuinely under-disclosed:**
  0 of 28 have no sale price at all. But counting "no derivable premium math AND relying solely on
  a bare sale-price/aggregate-gain with nothing to compare it to": CY6U's two deals are the
  standout case — sale price yes, pct yes, but reference NO (so pct cannot be tied to a dollar
  figure); UD1U's Il·lumina has sale price yes but neither pct nor reference. Counting deals where
  BOTH pct and reference are simultaneously absent (leaving only a bare price, if any, undated to
  any comparison): A17U's 9 per-property deals (no per-property pct, though a reference IS
  disclosed per-property) and N2IU FY2024's 1 deal (reference not located) come closest but each
  has at least one of the two. Strictly "neither pct nor reference disclosed": **UD1U Il·lumina
  only — 1 of 28.**

### Summary
| Metric | Count / 28 |
|---|---|
| Some sale price disclosed (per-property or aggregate) | 28 |
| Strictly per-property sale price | 23 |
| Percentage disclosed | 12 |
| Reference figure disclosed | 23 |
| BOTH pct AND reference (price derivable) | 10 |
| Neither pct nor reference disclosed | 1 (UD1U Il·lumina) |
| Pct disclosed but NO reference figure exists (CY6U — decisive case) | 2 |
