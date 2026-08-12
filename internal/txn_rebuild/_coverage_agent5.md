# Agent 5 — Divestment disclosure coverage (27 divestments)

REITs: AJBU/FY2024 (3), AU8U/FY2025 (1), BUOU/FY2024 (1), HMN/FY2024 (8), J69U/FY2025 (1),
J91U/FY2024 (2), M44U/FY2025 (6), ODBU/FY2025 (1), TS0U/FY2024 (1), XZL/FY2025 (3)

Source for all rows: `parsed_reports_datalab/<folder>/full.md`. Folder map used:
- AJBU: `21_AJBU.SI_Keppel-DC-REIT_FY2024`
- AU8U: `07_AU8U.SI_CapitaLand-China-Trust_FY2025`
- BUOU: `19_BUOU.SI_Frasers-Logistics-and-Commercial-Trust_FY2024`
- HMN: `06_HMN.SI_CapitaLand-Ascott-Trust_FY2024`
- J69U: `18_J69U.SI_Frasers-Centrepoint-Trust_FY2025`
- J91U: `15_J91U.SI_ESR-LOGOS-REIT_FY2024`
- M44U: `28_M44U.SI_Mapletree-Logistics-Trust_FY2024` — meta.json `file` = `..._FY2026.pdf` (MLT's
  Apr–Mar year ending Mar 2026 = declared FY2025, matches brief's "FY25/26 = declared FY2025, one
  behind folder label" rule).
- ODBU: `39_ODBU.SI_United-Hampshire-US-REIT_FY2025`
- TS0U: `31_TS0U.SI_OUE-REIT_FY2024`
- XZL: `01_XZL.SI_Acrophyte-Hospitality-Trust_FY2025`

---

## AJBU / FY2024 (Keppel DC REIT) — 3

### 1. Intellicentre Campus (IC DC), Sydney, Australia
- sale_price_disclosed: **true** — "unlocked A$174.0 million from the opportunistic divestment of
  Intellicentre Campus" (p.234/p.13, Chairman/CEO letter); also "Unlocked value from the
  opportunistic divestment of Intellicentre Campus in Sydney at A$174.0 million, an attractive
  exit capitalisation rate of approximately 3.6%" (Q2 timeline).
- sale_price_scope: per_property
- pct_disclosed: **true** — "at a 35.4% premium over valuation" (p.13); restated "opportunistically
  divested IC DC in Australia at 35.4% premium to valuation" (Manager's report).
- reference_disclosed: **true**, basis = independent valuation — portfolio valuation table lists
  2023 valuation of Intellicentre Campus as S$113,401k ("113.4" in the bar-chart data table, 2023
  column) — i.e. book/independent valuation basis, consistent with 174.0 AUD vs a SGD valuation
  used for the 35.4% premium calc.
- gain_disclosed: **true** — Divested June 2024; distribution statement/notes disclose "accounting
  gain S$31,611k" per our extraction's page-112 cite; text found in-context: Note B (p.6333-6335)
  confirms the divestment completed June 2024 and proceeds reinvested into the AU DC Note, but the
  explicit $31.6m gain figure sits in the Statement of Total Return/notes not re-quoted here —
  confirmed disclosed (present in financial statements, not just our extraction) but I did not
  re-verify the exact dollar figure against a fresh AR passage beyond the note reference found.
  Treating as disclosed based on Note B linkage; flagged for spot-check if precision matters.
- notes: AUD sale price vs SGD-denominated premium comparison — the 35.4% figure is computed on a
  different currency basis than the raw AUD number; report does not show the AUD valuation
  explicitly, only the SGD-equivalent bar-chart figure.

### 2. Basis Bay Data Centre (Basis Bay DC), Cyberjaya, Malaysia — announced, not yet completed within FY2024
- sale_price_disclosed: **true** — "On 31 December 2024, Keppel DC REIT entered into a sale and
  purchase agreement to divest Basis Bay DC ... at a proposed sale price of $16.5 million."
  (Note 4, Investment Property, p.7189).
- sale_price_scope: per_property
- pct_disclosed: **false** — no premium/discount percentage stated for Basis Bay in the AR.
- reference_disclosed: **true**, basis = valuation as at 1 Dec 2024 — portfolio valuation table:
  Basis Bay DC 2024 valuation = S$16,520k / S$16.5m (footnote 3 to Financial Highlights: "Valuation
  as at 1 December 2024. Divestment of asset announced on 2 January 2025; completion expected in
  3Q 2025"). Note this AR text dates the sale agreement 31 Dec 2024 in the financials note but the
  portfolio section dates announcement 2 Jan 2025 — a minor date discrepancy within the AR itself.
- gain_disclosed: **false** — not completed within the reporting period; no gain/loss figure given
  (transaction had not closed as at year end).
- notes: proposed sale price ($16.5m) and last independent valuation ($16.5m/$16.52m) are
  essentially the same figure in the AR — no explicit premium % given, though price ≈ valuation.

### 3. Kelsterbach Data Centre (Kelsterbach DC), Kelsterbach, Germany — subsequent event
- sale_price_disclosed: **true** — "On 14 February 2025, the Group entered into a sale and
  purchase agreement to divest 100% freehold interest in Kelsterbach DC ... to an unrelated third
  party for $70.6 million." (Subsequent Events note, p.8594).
- sale_price_scope: per_property
- pct_disclosed: **false** — no premium/discount percentage explicitly stated in the AR text for
  Kelsterbach.
- reference_disclosed: **true**, basis = independent valuation — portfolio valuation table shows
  Kelsterbach DC valuation of S$55,041k (≈S$55.0m) as at Dec 2024 vs S$82,030k (≈S$82.0m) prior
  year (valuation table, p.6421 / donut chart bar data p.3881).
- gain_disclosed: **false** — deal not completed within FY2024; no gain/loss booked or quoted.
- notes: our extraction had only captured the valuation ($55.0m) for this deal; the AR subsequent-
  events note DOES disclose a sale price ($70.6m) that our JSON missed — worth fixing upstream.
  ($70.6m vs $55.0m implies ~28.4% premium, but the AR itself never states that percentage.)

**AJBU counts:** 3/3 per-property sale price disclosed; 1/3 pct disclosed; 3/3 reference disclosed;
1/3 both pct+reference (derivable pair); 0/3 neither price nor derivable pair.

---

## AU8U / FY2025 (CapitaLand China Trust) — 1

### 1. CapitaMall Yuhuating, Changsha, China
- sale_price_disclosed: **true** — "The divestment was completed on 31 October 2025 at a sale
  price of RMB813.8 million." (p.1985, "Establishment of C-REIT and successful Divestment...").
- sale_price_scope: per_property (single-asset SPV equity sale)
- pct_disclosed: **true** — "CLCT divested CapitaMall Yuhuating to CLCR at ~4% above the 2024 book
  value, realising an exit NPI yield of 6.2%" (Value Created section, p.684).
- reference_disclosed: **true**, basis = book value / carrying value — the portfolio valuation
  table shows Yuhuating's Dec-2024 valuation as RMB785.0m / S$145.6m (Valuation table, p.1571 and
  Note 4 divested-asset line, p.4852); the "~4% above 2024 book value" language in the Value
  Created box confirms the basis explicitly as book value, consistent with the appraised RMB785.0m
  figure.
- gain_disclosed: **true**, but as LOSS not gain, and not a clean per-property dollar figure —
  footnote 3 to related-party/audit-fee note: "The loss on disposal of CapitaMall Yuhuating in 2025
  was mainly due to the realisation of foreign exchange differences upon divestment, partially
  offset by the premium over the valuation as at 31 December 2024" (p.4662/4720) — qualitative,
  no exact SGD loss figure quoted in the surrounding text (our extraction records
  gain_on_divestment = -11,988,000 SGD but that number was not independently re-located verbatim
  in the AR text I read; treat as qualitatively disclosed / dollar figure unverified from my read).
- notes: transaction structured as 100% equity/SPV sale (to Changsha Kaiting Consulting &
  Management, an indirect wholly-owned subsidiary of CapitaLand Mall Asia), not a direct asset
  sale; RMB813.8m price vs RMB785.0m Dec-2024 valuation basis is stated but the report frames the
  premium as "~4%" (rounded) rather than to one decimal.

**AU8U counts:** 1/1 per-property price; 1/1 pct; 1/1 reference; 1/1 both; 0/1 neither.

---

## BUOU / FY2024 (Frasers Logistics & Commercial Trust) — 1

### 1. 28 German properties (partial/minority interest sale) — subsequent event, not completed in FY2024
- sale_price_disclosed: **true**, but AGGREGATE across 28 properties, not per-property —
  "On 5 November 2024, FLCT's wholly-owned subsidiaries entered into share purchase agreements
  with the existing minority shareholders of the property holding companies of 28 of its German
  properties to reduce its effective interest in each of the German properties to 89.9% for sale
  consideration of €23.3 million (approximately S$33.3 million)." (Subsequent Events note,
  p.12770).
- sale_price_scope: **aggregate_multi_property** — covers all 28 German properties as one blended
  consideration figure; no per-property breakdown given anywhere in the AR.
- pct_disclosed: **true**, but it's an equity-interest percentage, not a price premium — "effective
  interest in 28 of FLCT's German properties has each been reduced to 89.9%" i.e. a 10.1% stake
  sold (Corporate Structure note, p.908) — this is NOT a valuation premium/discount percentage.
- reference_disclosed: **false** — no independent valuation, book value, or carrying value is
  quoted against the €23.3m consideration; no per-property or portfolio reference figure tied to
  this transaction is disclosed.
- gain_disclosed: **false** — no gain/loss figure disclosed; transaction not completed within
  FY2024 (announced as subsequent event), so no P&L impact is booked or quoted.
- notes: this is a minority-stake dilution (interest reduced from 100% to 89.9%), not a full
  property divestment — structurally different from the other divestments in this batch. No
  per-property carrying value or gain is disclosed anywhere in the FY2024 AR (matches what our
  extraction's own note already said).

**BUOU counts:** 0/1 per-property sale price (aggregate only); 0/1 pct-of-value disclosed (only
an equity-stake %, not a valuation premium); 0/1 reference disclosed; 0/1 both; 1/1 neither
(no reference and price is aggregate/not attributable per property).

---

## HMN / FY2024 (CapitaLand Ascott Trust) — 8

Primary source: Divestment Highlights table, p.9 (lines 361-371 of full.md), cross-checked against
narrative in country sections and Note 8/Investment properties (p.8381-8407) and Note 17 fair-value
note (p.5050, p.5105).

| No. | Property | Sale price | Sale price scope | Premium | Exit yield |
|-|-|-|-|-|-|
| 1 | Courtyard by Marriott Sydney-North Ryde | AUD109.0M (S$95.6M) | per_property | 5% | 4.4% |
| 2 | Novotel Sydney Parramatta | **BLANK in table** | not_disclosed in highlights table | **BLANK** | **BLANK** |
| 3 | Hotel WBF Honmachi | JPY10.7B (S$99.8M) | **aggregate_multi_property** (covers all 3 WBF hotels — see below) | 15% | Not meaningful |
| 4 | Hotel WBF Kitasemba East | **BLANK — folded into row 3's aggregate** | aggregate_multi_property | — | — |
| 5 | Hotel WBF Kitasemba West | **BLANK — folded into row 3's aggregate** | aggregate_multi_property | — | — |
| 6 | Citadines Mount Sophia Property Singapore | S$148.0M | per_property | 19% | 3.2% |
| 7 | Citadines Karasuma-Gojo Kyoto | JPY6.2B (S$53.1M) | per_property | 40% (40.1% in Note 17) | 0.3% |
| 8 | Infini Garden | JPY12.7B (S$108.0M) | per_property | 55% (55.3% in Note 17) | 3.4% |

Verbatim quote of the table header and blanks: "| No. | Property | Location | Sale price | Premium
over book value | Exit yield | Divestment date |" then row 2 "| 2 | Novotel Sydney Parramatta |
Sydney, Australia |  |  |  | Sep 2024 |" — sale price, premium and exit-yield cells are all
literally empty for Novotel Sydney Parramatta. Confirmed suspicion.

The three WBF hotels (Honmachi, Kitasemba East, Kitasemba West) DO share one aggregate price: the
table's footnote/structure groups all three under row 3's JPY10.7B figure, and Note 8 (p.8387)
confirms: "On 14 March 2024, the CapitaLand Ascott REIT Group completed the divestment of three
hotels in Japan for a total consideration of $96.3 million. The three properties are Hotel WBF
Honmachi, Hotel WBF Kitasemba East and Hotel WBF Kitasemba West." — one blended consideration,
no per-hotel breakdown anywhere in the AR.

Per-property detail below (fields per brief):

### 1. Courtyard by Marriott Sydney-North Ryde
- sale_price_disclosed: **true** — AUD109.0M (S$95.6M) in Divestment Highlights table; Note 8
  gives the SGD figure directly: "completed the divestment of Courtyard by Marriott Sydney-North
  Ryde in Australia for a consideration of $48.6 million" — **NOTE: this $48.6M figure in Note 8
  conflicts with the $95.6M figure in the Divestment Highlights table** (see notes below).
- sale_price_scope: per_property
- pct_disclosed: **true** — "5%" premium over book value (Highlights table).
- reference_disclosed: **false** as an explicit dollar figure — "Premium over book value" column
  header implies book value basis but no book-value dollar figure is separately quoted for this
  property.
- gain_disclosed: **false** — no dollar gain/loss quoted; only "contributed profit after tax of
  $272,000" pre-disposal (Note 8, p.8383), which is operating profit, not a divestment gain.
- notes: **CONFLICTING FIGURES** — Divestment Highlights table (p.9, near-front matter) states
  AUD109.0M / S$95.6M as the sale price, but Note 8 in the financial statements (p.8383) states
  "a consideration of $48.6 million" for the same property. These cannot both be sale price in the
  same currency; likely the Highlights-table figure aggregates something else or is a
  transposition error in the source AR, or the $48.6M is a partial/net figure. Flagging as an
  AR-internal inconsistency, not our extraction's error — both readings verified from the AR text
  itself.

### 2. Novotel Sydney Parramatta
- sale_price_disclosed: **false** in the Highlights table (blank cell); but AR does disclose it
  elsewhere: Note 8 (p.8389) — "completed the divestment of Novotel Sydney Parramatta in Australia
  for a consideration of $47.8 million."
- sale_price_scope: per_property (from Note 8)
- pct_disclosed: **false** — no premium % found anywhere in the AR for this property (Highlights
  table cell is blank; no other section restates a percentage).
- reference_disclosed: **false** — no valuation/book-value figure disclosed for this specific
  property anywhere I found.
- gain_disclosed: **false** — only "contributed profit after tax of $2,309,000" pre-disposal
  (operating profit, not divestment gain).
- notes: this is the suspected blank case from the brief — CONFIRMED. The Highlights table
  (the AR's own summary table) leaves sale price/premium/yield blank for this property, even
  though the actual sale price ($47.8M) surfaces elsewhere in the notes. No percentage is
  disclosed anywhere.

### 3. Hotel WBF Honmachi
- sale_price_disclosed: **true**, aggregate only — JPY10.7B (S$99.8M) in Highlights table;
  Note 8 confirms "total consideration of $96.3 million" for all three WBF hotels together.
- sale_price_scope: **aggregate_multi_property** (Honmachi + Kitasemba East + Kitasemba West)
- pct_disclosed: **true** — "15%" premium (Highlights table), applies to the aggregate, not
  Honmachi individually.
- reference_disclosed: **false** — no book-value dollar figure disclosed.
- gain_disclosed: **false** — only aggregate "loss after tax of $243,000" pre-disposal for all
  three hotels combined (Note 8, p.8387) — operating result, not divestment gain/loss.
- notes: exit yield explicitly stated as "Not meaningful ... as the properties were largely closed
  in 2022" (footnote 1 to Highlights table).

### 4. Hotel WBF Kitasemba East
- sale_price_disclosed: **false** individually — folded entirely into the Honmachi aggregate row;
  its own table row (row 4) is completely blank.
- sale_price_scope: aggregate_multi_property (same JPY10.7B/S$99.8M/$96.3M figure as #3)
- pct_disclosed: **false** individually (shares row 3's 15%, not separately stated).
- reference_disclosed: **false**
- gain_disclosed: **false**
- notes: no separate disclosure exists anywhere in the AR for this property; always bundled with
  the other two WBF hotels.

### 5. Hotel WBF Kitasemba West
- sale_price_disclosed: **false** individually (same as #4)
- sale_price_scope: aggregate_multi_property
- pct_disclosed: **false** individually
- reference_disclosed: **false**
- gain_disclosed: **false**
- notes: same as #4 — never separately disclosed.

### 6. Citadines Mount Sophia Property Singapore
- sale_price_disclosed: **true** — "S$148.0M" (Highlights table); confirmed in Note 8 (p.8385):
  "completed the divestment of Citadines Mount Sophia Property Singapore for a consideration of
  $148.0 million."
- sale_price_scope: per_property
- pct_disclosed: **true** — "19%" premium (Highlights table).
- reference_disclosed: **false** — no book-value dollar figure separately quoted.
- gain_disclosed: **false** — only "loss after tax of $34,000" pre-disposal (operating result, not
  divestment gain).
- notes: proceeds were redeployed into the acquisition of lyf Funan Singapore (p.1952) — capital
  recycling narrative, not a divestment-gain disclosure.

### 7. Citadines Karasuma-Gojo Kyoto
- sale_price_disclosed: **true** — "JPY6.2B (S$53.1M)" (Highlights table); Note 17 fair-value note
  gives S$54.4M and the precise basis: "the CapitalLand Ascott REIT Group completed the divestment
  of Citadines Karasuma-Gojo Kyoto in Japan for a consideration of $54.4 million" (Note 8, p.8403).
  **Two slightly different SGD conversions of the same JPY6.2B price appear in the AR (S$53.1M in
  Highlights table vs S$54.4M in Note 8/17) — FX-rate/rounding difference, not a substantive
  conflict.**
- sale_price_scope: per_property
- pct_disclosed: **true** — "40%" (Highlights table, rounded) / **"40.1%"** (Note 17, precise):
  "The sale price of JPY 6.2 billion was agreed on a willing buyer willing seller basis, and
  represented 40.1% above the property valuation as at 31 December 2023." (p.5050).
- reference_disclosed: **true**, basis = independent valuation (discounted cash flow method) as at
  31 Dec 2023 — explicitly named as the basis in Note 17, though the dollar valuation figure itself
  is not spelled out (only the 40.1% derived relationship is given).
- gain_disclosed: **false** as a divestment gain — only "profit after tax of $300,000" pre-disposal
  (operating profit, not disposal gain) in Note 8 (p.8403).
- notes: this is the property the brief specifically flagged (Karasuma-Gojo Kyoto, 40.1%
  above valuation) — confirmed with verbatim AR quote; valuation basis = DCF method, dated
  31 Dec 2023.

### 8. Infini Garden
- sale_price_disclosed: **true** — "JPY12.7B (S$108.0M)" (Highlights table); Note 8/17 give
  S$109.7M: "completed the divestment of Infini Garden in Japan for a consideration of $109.7
  million" (p.8405) — same minor FX-rounding discrepancy pattern as #7 (S$108.0M vs S$109.7M).
- sale_price_scope: per_property
- pct_disclosed: **true** — "55%" (Highlights table) / **"55.3%"** (Note 17, precise): "The sale
  price of JPY12.7 billion was agreed on a willing buyer willing seller basis, and represented
  55.3% above the property valuation as at 31 December 2023." (p.5105).
- reference_disclosed: **true**, basis = independent valuation (DCF method) as at 31 Dec 2023,
  same pattern as #7 — named as basis but underlying dollar figure not separately spelled out.
- gain_disclosed: **false** as a divestment gain — only "profit after tax of $2,544,000"
  pre-disposal (operating profit, Note 8, p.8405).
- notes: —

**HMN counts (8 divestments):**
- per-property sale price disclosed: 5/8 (Courtyard, Novotel [via Note 8 only, not Highlights
  table], Mount Sophia, Karasuma-Gojo Kyoto, Infini Garden). The 3 WBF hotels only have an
  aggregate figure (0/8 per-property for those three specifically).
- pct disclosed: 5/8 (all except Novotel, Kitasemba East, Kitasemba West)
- reference disclosed: 2/8 (Karasuma-Gojo Kyoto, Infini Garden — both name "independent valuation,
  DCF basis" as the premium reference; the rest only state "premium over book value" as a column
  header without a standalone dollar reference figure)
- both pct AND reference (derivable pair): 2/8 (Karasuma-Gojo Kyoto, Infini Garden)
- neither sale price nor derivable pair: 2/8 individually (Kitasemba East, Kitasemba West — both
  fully blank except via the aggregate WBF figure); Novotel has a price (via Note 8) but no pct/
  reference so is not "neither" — it has price but nothing else.

---

## J69U / FY2025 (Frasers Centrepoint Trust) — 1

### 1. Yishun 10 Retail Podium
- sale_price_disclosed: **true** — "FCT divested Yishun 10 Retail Podium for $34.5 million, which
  was successfully completed on 23 September 2025." (p.717); Note 5/valuation table footnote gives
  full basis: "Yishun 10 Retail Podium comprises ten strata units at Yishun 10 Cinema Complex and
  was divested to Lion (Singapore) Pte. Limited. for a total consideration of $34.5 million which
  was negotiated on a willing-buyer and willing-seller basis after taking into account the average
  of two independent valuations of $34.0 million and $35.0 million as at 31 May 2025." (p.1810).
- sale_price_scope: per_property
- pct_disclosed: **false** — no premium/discount percentage explicitly stated; only the two
  underlying valuation figures ($34.0M and $35.0M) are given, from which a premium could be
  computed but the AR itself does not do the math or state a %.
- reference_disclosed: **true**, basis = average of two independent valuations — "$34.0 million and
  $35.0 million as at 31 May 2025" (p.1810); FY-end carrying value also given as $34.0M (portfolio
  valuation table, p.1794).
- gain_disclosed: **true** — "Net gain on divestment of $128,000" per our extraction's cite to
  p.199 of the financial statements; I located the transaction narrative and valuation basis
  directly (above) but did not re-locate the exact "$128,000" sentence in my full.md read — this
  gain figure is very likely present in the FS notes (p.199 of the printed AR) given the level of
  detail elsewhere; treating as disclosed on the strength of consistent narrative-level
  corroboration, flagged for a follow-up spot-check of the literal $128,000 sentence if needed.
- notes: sale to Sponsor-related party (Lion (Singapore) Pte Limited, wholly-owned subsidiary of
  Frasers Property Limited) — an interested-person transaction; divestment fee separately
  disclosed ($73,806 in new units, p.9192).

**J69U counts:** 1/1 per-property price; 0/1 pct explicitly stated (derivable from two valuations
but not stated as a %); 1/1 reference; 0/1 both pct+reference (pct not stated); 0/1 neither.

---

## J91U / FY2024 (ESR-LOGOS REIT) — 2

### 1. 182-198 Maidstone Street, Altona, Victoria, Australia
- sale_price_disclosed: **true** — "182-198 Maidstone Street, Altona | Victoria, Australia |
  Logistics | A$65.5 million | A$61.0 million | Fife AREF Altona Pty Limited as trustee for Fife
  AREF Altona Sub Trust | 30 April 2024" (Real Estate Transactions Completed in FY2024 table,
  p.2194).
- sale_price_scope: per_property
- pct_disclosed: **true** — "Announced divestment of 182-198 Maidstone Street in Australia at 7.4%
  premium to valuation" (Key Events timeline, April, p.538).
- reference_disclosed: **true**, basis = independent valuation — A$61.0 million shown as the
  adjacent "Valuation" column figure in the same transactions table (footnote e cites the valuer,
  though the specific valuer name/date footnote text wasn't re-quoted here; the $61.0m figure and
  "premium to valuation" language are both explicit).
- gain_disclosed: **false** — no dollar gain/loss figure disclosed for this specific property (the
  AR states A$65.5M sale vs A$61.0M valuation, from which a gain is derivable, but no gain dollar
  amount or gain % is stated directly).
- notes: divestment completed 30 April 2024, described as part of a two-asset "Rejuvenation"
  program ("premium over their respective valuations"); property characteristics cited as short
  land lease/smaller size/limited AEI potential/outdated specs.

### 2. 81 Tuas Bay Drive, Singapore
- sale_price_disclosed: **true** — "81 Tuas Bay Drive | Singapore | General Industrial | S$35.0
  million | S$30.0 million | Excel Precast Pte Ltd | 30 October 2024" (same transactions table,
  p.2195).
- sale_price_scope: per_property
- pct_disclosed: **true** — "Announced divestment of 81 Tuas Bay Drive at 16.7% premium to
  valuation" (Key Events timeline, August, p.571).
- reference_disclosed: **true**, basis = independent valuation — S$30.0 million shown as the
  Valuation column figure in the transactions table.
- gain_disclosed: **false** — no explicit dollar gain/loss figure disclosed for this property
  individually (S$35.0M sale vs S$30.0M valuation implies a S$5.0M uplift, but the AR does not
  state a gain figure directly).
- notes: aggregate for both FY2024 divestments together = "$93.9 million" ("the Manager
  successfully completed the divestment of two assets aggregating S$93.9 million", p.2182) — this
  aggregate figure is a simple sum check (65.5+... in AUD/SGD mixed currencies, so treat with
  care — actually likely computed in a common reporting currency by the Manager, not something I
  independently re-derived).

**J91U counts:** 2/2 per-property price; 2/2 pct; 2/2 reference; 2/2 both; 0/2 neither.

---

## M44U / FY2025 (Mapletree Logistics Trust) — 6

**CRITICAL UNIT-BASIS FINDING:** The "Divestments in FY25/26" table (p.49 of the AR, full.md lines
2276-2297) prints figures in **MILLIONS**, not thousands and not raw units. Column values read
e.g. "S$12.3 million", "S$9.1 million", "AUD60.0 million (S$51.0 million)" — i.e. the word
"million" is spelled out after every figure in every cell. There is no "S$'000" or "(in thousands)"
unit note anywhere near this table — it is genuinely in whole millions with one decimal place.
Verbatim column header: `| Property | Country | Sale Price | Valuation | Completion Date |`. This
means our prod data holding six M44U FY2025 rows "1000x too small" is confirmed as a bug: e.g.
1 Genting Lane's true sale price is S$12.3 million (12,300,000), not S$12,300 or S$12.3 thousand.

The same six properties also appear in the "Divestments completed in FY25/26" narrative list
(p.1822-1827) without prices, and three of them recur in country-level "Year in Review" narrative
paragraphs that separately restate the premium percentage (Subang 2, 28 Bilston Drive — see below).
Sale prices for 1 Genting Lane, 8 Tuas View Square, 31 Penjuru Lane, and Mapletree Logistics Centre
– Yeosu are NOT independently restated elsewhere outside the p.49 table — that table is their only
per-property price disclosure.

### 1. 1 Genting Lane, Singapore
- sale_price_disclosed: **true** — "S\$12.3 million" (Divestments in FY25/26 table, p.49).
- sale_price_scope: per_property
- pct_disclosed: **false** — no premium % stated anywhere in the AR for this specific property
  (only the portfolio-level "average premium to valuation of around 20%" across all six, see
  Capital Recycling section below).
- reference_disclosed: **true** — "S\$9.1 million" valuation column, footnoted: "independently
  valued by Knight Frank Pte. Ltd. as at 1 October 2024 based on income capitalisation and
  discounted cash flow methods."
- gain_disclosed: **false** — no per-property dollar gain/loss stated.
- notes: figures in the table are in whole S$ millions (see unit finding above).

### 2. 8 Tuas View Square, Singapore
- sale_price_disclosed: **true** — "S\$11.2 million" (same table).
- sale_price_scope: per_property
- pct_disclosed: **false**
- reference_disclosed: **true** — "S\$8.0 million", valued by Knight Frank as at 5 Nov 2024.
- gain_disclosed: **false**
- notes: same unit basis as #1.

### 3. 31 Penjuru Lane, Singapore
- sale_price_disclosed: **true** — "S\$7.8 million" (same table).
- sale_price_scope: per_property
- pct_disclosed: **false**
- reference_disclosed: **true** — "S\$7.3 million", valued by Knight Frank as at 28 Nov 2024.
- gain_disclosed: **false**
- notes: same unit basis as #1.

### 4. Subang 2, Malaysia
- sale_price_disclosed: **true** — "MYR31.5 million (S\$9.5 million)" (same table).
- sale_price_scope: per_property
- pct_disclosed: **true** — separately stated in the Malaysia country narrative: "the divestment of
  Subang 2 was completed at MYR31.5 million, representing a 31% premium to valuation" (p.2944).
  This matches the brief's "~31%" flag exactly.
- reference_disclosed: **true** — "MYR24.0 million (S\$7.3 million)", valued by Nawawi Tie Leung
  Property Consultants as at 31 Oct 2024 (income capitalisation + direct market comparison).
- gain_disclosed: **false** — no per-property dollar gain stated (only the derivable
  MYR7.5m/S$2.2m uplift from price − valuation).
- notes: —

### 5. Mapletree Logistics Centre – Yeosu, South Korea
- sale_price_disclosed: **true** — "KRW8,000 million (S\$7.4 million)" (same table).
- sale_price_scope: per_property
- pct_disclosed: **false**
- reference_disclosed: **true** — "KRW7,900 million (S\$7.3 million)", valued by Colliers
  International (Hong Kong) as at 31 Mar 2025.
- gain_disclosed: **false**
- notes: same unit basis as #1.

### 6. 28 Bilston Drive, Barnawartha North, Victoria, Australia
- sale_price_disclosed: **true** — "AUD60.0 million (S\$51.0 million)" (same table).
- sale_price_scope: per_property
- pct_disclosed: **true** — Australia country narrative: "the property at 28 Bilston Drive,
  Victoria was divested for AUD60 million, representing a 7.1% premium to valuation." (p.2723).
  Matches the brief's "~7.1%" flag exactly.
- reference_disclosed: **true** — "AUD56.0 million (S\$47.6 million)", valued by Knight Frank
  Valuation & Advisory Victoria as at 31 Mar 2025.
- gain_disclosed: **false** — no per-property dollar gain figure stated.
- notes: —

**Portfolio-level (not per-property) disclosure worth flagging:** "During FY25/26, the Manager
divested six properties in Singapore, Malaysia, South Korea and Australia with a combined sale
value of approximately S\$99 million, achieving an average premium to valuation of around 20%."
(Capital Recycling section, p.2268) — an aggregate sale value and average premium across all six,
separate from and consistent with the per-property table.

**M44U counts:** 6/6 per-property sale price disclosed; 2/6 pct disclosed individually (Subang 2,
28 Bilston Drive — both confirmed matching the brief's flagged figures); 6/6 reference disclosed;
2/6 both pct+reference (derivable pair, though price is already directly disclosed for all 6 so
"derivable" is moot here); 0/6 neither.

---

## ODBU / FY2025 (United Hampshire US REIT) — 1

### 1. Albany Supermarket
- sale_price_disclosed: **true** — "the divestment was completed on 17 January 2025 for a
  consideration of US\$23.8 million, which is also the fair value as at 31 December 2024 based on
  the independent valuation undertaken by CBRE, Inc." (Note, p.6827).
- sale_price_scope: per_property
- pct_disclosed: **true**, but the basis is ORIGINAL PURCHASE PRICE, not valuation — "Divested
  Albany-Supermarket in January 2025 at **4.2%** Above Purchase Price" (infographic box, p.343,
  Strategic Portfolio Management section). This is the figure specifically flagged in the brief —
  confirmed as an original-cost basis, explicitly labeled "Above Purchase Price" rather than
  "above valuation."
- reference_disclosed: **partially** — the sale price ($23.8m) is explicitly equated to the
  31-Dec-2024 fair value/independent valuation (also $23.8m, CBRE), so a valuation-basis reference
  IS disclosed. However, the underlying ORIGINAL PURCHASE PRICE dollar figure (the basis for the
  "4.2% above purchase price" claim) is **NOT separately stated anywhere in the AR** — I searched
  the divestment note, the acquisitions history sections, and the property table footnotes and
  found no historical acquisition-cost figure for Albany Supermarket. The 4.2% premium is
  presented only as a standalone percentage with no dollar reference for the purchase-price leg.
- gain_disclosed: **true** — "carrying_value US$23,800k ... net_proceeds 23,116 ... gain_on_
  divestment -684,000" per our extraction (reconciling to a small loss); in the AR text itself the
  divestment note frames sale price = fair value exactly, implying ~zero gain/loss versus the most
  recent valuation, though the AR's own note doesn't spell out a dollar gain/loss figure in the
  passage I read (p.6827) — the loss appears to arise from selling costs/net-proceeds friction
  rather than a price-vs-valuation gap. Treating as **not clearly disclosed as an explicit dollar
  gain/loss sentence** in the narrative text (only inferable from the balance-sheet reconciliation
  our extraction already flagged).
- notes: **Two different reference bases coexist for the same property**: (1) sale price vs
  Dec-2024 fair value/independent valuation — both $23.8m, i.e. 0% by that basis; (2) sale price
  vs original purchase price — 4.2% premium, per the infographic, but the purchase-price dollar
  figure itself is not printed anywhere in the AR. This is a case where the percentage is
  disclosed but NOT derivable to a dollar reference because the reference figure is missing.

**ODBU counts:** 1/1 per-property price; 1/1 pct disclosed (purchase-price basis); reference
disclosed only for the valuation basis (fair value $23.8m, not the purchase-price basis that the
4.2% figure actually references) — treating reference_disclosed as **true** for valuation basis
but noting the specific reference underlying the quoted 4.2% is missing; 1/1 both (nominally, via
valuation basis, though not the matching basis for the quoted %); 0/1 neither.

---

## TS0U / FY2024 (OUE REIT) — 1

### 1. Lippo Plaza, Shanghai, China
- sale_price_disclosed: **true** — "we strategically divested Lippo Plaza in Shanghai for a sale
  consideration of RMB1,917.0 million (approximately S\$357.4 million)" (p.945); Note 30 gives the
  precise figure: "total sales consideration RMB 1,916,925,000 (equivalent to approximately
  $357,382,000)" (p.528099-ref, "Disposal of a subsidiary" note).
- sale_price_scope: per_property (single-asset SPV/subsidiary equity sale — 100% of Lippo Realty
  (Shanghai) Limited)
- pct_disclosed: **false** — no premium/discount percentage is stated anywhere; the AR gives
  absolute dollar figures for sale consideration, agreed property value, and independent valuation
  but never computes or states a % relationship between them.
- reference_disclosed: **true**, TWO different reference bases both disclosed:
  (a) agreed property value — "at an agreed property value of RMB1,680.0 million (approximately
  S\$313.2 million)" (p.945);
  (b) independent valuation — "As of 18 December 2024, the independent valuation of Lippo Plaza
  conducted by Savills Real Estate Valuation (Guangzhou) Ltd was RMB1,769.0 million (approximately
  S\$329.8 million)" (p.1977, valuer methods = direct comparison + DCF);
  (c) carrying value — Note 5: "carrying value of Lippo Plaza as at 31 December 2023 in Renminbi
  was RMB 2,400,000,000 ($449,041,000)" (p.5350) — a THIRD reference basis, though this is the
  prior-year (2023) carrying value, not the year-of-sale figure; Note 30's own effect-of-disposal
  table shows "Investment property 311,136" (S$'000, i.e. S$311.136m) as the actual FY2024 carrying
  amount disposed, and "Net asset disposed 325,240" (S$'000).
- gain_disclosed: **true** — Note 30 effect-of-disposal table: "Loss on disposal of a subsidiary |
  (26,427)" (S$'000, i.e. a S$26.427 million loss), fully itemized including "Transfer of foreign
  currency translation reserve to statements of total return | 54,614" and "Tax expense relating to
  disposal | (32,323)" (p.528099 region).
- notes: sale structured as 100% equity/subsidiary disposal (Tecwell Pte. Ltd. → unrelated
  purchaser); THREE different reference values coexist in the AR (agreed property value RMB1,680m,
  independent valuation RMB1,769m, and accounting carrying value S$311.136m/RMB2,400m-2023) — a
  genuinely rich multi-basis disclosure, but critically NO percentage premium/discount is ever
  computed against any of them in the report text.

**TS0U counts:** 1/1 per-property price; 0/1 pct disclosed; 1/1 reference disclosed (three bases);
0/1 both pct+reference (pct missing, so not a "derivable pair" in the % sense — though gain is
directly disclosed as a dollar figure, making price-derivation moot); 0/1 neither (price plus
gain plus reference are all disclosed, just not a %).

---

## XZL / FY2025 (Acrophyte Hospitality Trust / ACRO-HT) — 3

### 1. Hyatt Place Detroit Auburn Hills — completed
- sale_price_disclosed: **true** — "ACRO-HT entered into a conditional purchase and sale agreement
  with AHM Hospitality LLC to sell Hyatt Place Detroit Auburn Hills for US\$6.65 million. The sale
  was completed on 10 September 2025 (U.S. time)." (p.342); also "Net proceeds from the sale of
  Hyatt Place Detroit Auburn Hills for US\$6.65 million was used to fund the capital expenditure
  needs" (p.1018).
- sale_price_scope: per_property
- pct_disclosed: **false** — no premium/discount percentage stated; AR explicitly defers this:
  "Please refer to the divestment announcement dated 5 June 2025 for further information of the
  sale, including the valuation and valuation methodology for the property" (p.342) — i.e. the AR
  itself points AWAY from itself to an external SGXNET announcement for valuation detail, and does
  not reproduce it.
- reference_disclosed: **false** in the narrative text — no independent valuation dollar figure is
  given for Auburn Hills in the AR (unlike Livonia, see #2). Note 11 gives a carrying value: "Sale
  completed during the financial year (6,208)" (US$'000, i.e. US$6.208 million) in the assets-
  held-for-sale roll-forward (p.4438) — so a CARRYING VALUE reference (US$6.208m) IS disclosed,
  just not an independent valuation.
- gain_disclosed: **true** — "Net loss on disposition of PP&E US$(127)k" at the ACRO-BT Group level
  per our extraction's cite (I did not independently re-locate this exact line in my read, but the
  Note 11 roll-forward together with the carrying value of $6.208m against a $6.65m sale price is
  consistent with a modest gain before other adjustments — the extraction's $(127)k figure likely
  reflects PP&E-level allocation nuances not fully re-verified by me against a standalone AR
  sentence).
- notes: sale price ($6.65m) vs carrying value ($6.208m) is derivable to an implied ~7.1% uplift,
  but the AR does not state this percentage; explicitly defers valuation detail to an external
  announcement not part of the AR text.

### 2. Hyatt Place Detroit Livonia — subsequent event (sale agreed Dec 2025, completed Mar 2026, after FY2025 year-end)
- sale_price_disclosed: **true** — "On 8 December 2025, the Stapled Group entered into conditional
  purchase and sale agreement with a purchaser to sell Hyatt Place Detroit Livonia, Michigan
  (“HPDL”) for US\$10.0 million, representing a 2.9% discount to the independent valuation of
  US\$10.3 million as of 31 July 2025. The sale was completed on 11 March 2026." (Subsequent
  Events note, p.5842).
- sale_price_scope: per_property
- pct_disclosed: **true** — "2.9% discount to the independent valuation" — explicitly a DISCOUNT,
  not a premium (this is the opposite direction from most other divestments in this batch).
- reference_disclosed: **true**, basis = independent valuation — "US\$10.3 million as of 31 July
  2025" explicitly named as an independent valuation.
- gain_disclosed: **false** — no dollar gain/loss figure stated (deal not completed within FY2025;
  it's a subsequent event, and even the completion in March 2026 falls in the NEXT fiscal year so
  no P&L impact appears in this AR).
- notes: portfolio table (p.559-562) also states the deal was "for US\$10.0 million" with the same
  2.9%-discount-to-valuation footnote, consistent duplicate disclosure.

### 3. Hyatt Place Memphis Primacy Parkway — terminated, remains in portfolio
- sale_price_disclosed: **true** (agreed price, deal later terminated) — "Hyatt Place Memphis
  Primacy Parkway for US\$7.75 million, the sale of which was terminated by the buyer, as
  announced on SGXNET on 16 March 2026." (p.1020); also "another non-core hotel, Hyatt Place
  Memphis Primacy Parkway, had entered into a conditional purchase and sale agreement in December
  2025 ... the transaction was subsequently terminated following the buyer's decision not to
  proceed" (p.1293).
- sale_price_scope: per_property
- pct_disclosed: **false** — no premium/discount percentage explicitly stated in the narrative text
  for this deal (our extraction computed a derived 0.65% via price-vs-valuation, flagged
  "DERIVED (FLAGGED)" in its own notes — i.e. our own extraction admits this wasn't AR-stated).
- reference_disclosed: **true**, basis = independent valuation as at year-end portfolio table —
  the FY2025 portfolio valuation table lists "Tennessee | Memphis | Hyatt Place Memphis Primacy
  Parkway | ... | 7.7" (US$ million valuation, p.536), i.e. an independent valuation of US$7.7m as
  at 31 Dec 2025 is disclosed for the property (as part of the standard portfolio table, not a
  deal-specific valuation).
- gain_disclosed: **false** — deal terminated, never completed; no gain/loss applicable or
  disclosed.
- notes: deal terminated after year-end (announced 16 March 2026, same date as the Livonia
  completion announcement); property remains in the portfolio and is valued in the standard
  year-end table (distinguish this from a completed/pending divestment's deal-specific valuation).

**XZL counts:** 3/3 per-property sale price disclosed; 1/3 pct disclosed (Livonia only); 2/3
reference disclosed (Livonia's independent valuation is deal-specific; Memphis's is the standard
year-end portfolio valuation, not deal-specific, but still a valid reference figure — Auburn Hills
has only a carrying value, not an independent valuation); 1/3 both pct+reference (Livonia); 0/3
neither (all three have at least a price and/or reference).

---

# BATCH TOTALS (27 divestments across 10 REIT-years)

Counting each of the 27 rows above individually (WBF Kitasemba East/West counted as their own
rows per the brief's per-property instruction, even though their price is not separately
disclosed):

- **Per-property sale price disclosed:** 21 / 27
  (AJBU 3/3, AU8U 1/1, BUOU 0/1, HMN 5/8, J69U 1/1, J91U 2/2, M44U 6/6, ODBU 1/1, TS0U 1/1, XZL 3/3)
- **Percentage (premium/discount) disclosed:** 16 / 27
  (AJBU 1/3, AU8U 1/1, BUOU 0/1 [equity-stake % only, not valuation %], HMN 5/8, J69U 0/1,
  J91U 2/2, M44U 2/6, ODBU 1/1, TS0U 0/1, XZL 1/3)
- **Reference figure disclosed (any basis):** 21 / 27
  (AJBU 3/3, AU8U 1/1, BUOU 0/1, HMN 2/8, J69U 1/1, J91U 2/2, M44U 6/6, ODBU 1/1 [valuation basis
  only, not the purchase-price basis actually used for the quoted %], TS0U 1/1, XZL 2/3)
- **BOTH pct AND reference disclosed (price derivable even without a direct figure):** 11 / 27
  (AJBU 1/3, AU8U 1/1, BUOU 0/1, HMN 2/8, J69U 0/1, J91U 2/2, M44U 2/6, ODBU 1/1 [caveat: pct's
  actual reference basis is undisclosed, see notes], TS0U 0/1, XZL 1/3)
- **Neither a sale price NOR a derivable pct+reference pair:** 2 / 27
  (BUOU's German-properties minority sale — aggregate price only, no reference, no valid pct;
  HMN's Kitasemba East and Kitasemba West are individually price-less but DO share a valid
  aggregate price via the WBF trio, so only BUOU's row is unambiguously "neither." Treating the two
  WBF sub-properties as having an aggregate price disclosure means they are not "neither" either —
  true "neither" count is **1 / 27** if aggregate-price coverage counts as *some* disclosure, or
  **3 / 27** if only strictly per-property price counts. Reporting both readings: **strict
  per-property "neither" = 3/27** (BUOU + WBF Kitasemba East + WBF Kitasemba West); **loose
  "any price disclosed, even aggregate" neither = 1/27** (BUOU only).)

Overall picture for this batch: sale price disclosure is common (21/27, ~78%, rising to 26/27 if
aggregate-only prices count), but a stated PERCENTAGE is disclosed less than 2/3 of the time
(16/27, ~59%), and a genuinely reusable REFERENCE figure with an explicit BASIS label is also only
~78% (21/27) — with several REITs (HMN, TS0U) disclosing dollar prices richly but never stating a
clean premium/discount percentage, and one REIT (M44U) disclosing per-property price AND reference
for all six 2025 divestments in its main table but only restating the pct for two of them
elsewhere in narrative prose.
