# DHLU.SI — Daiwa House Logistics Trust — property-transaction audit (FY2025, FY-END 2025-12-31)

Source: `parsed_reports_datalab/12_DHLU.SI_Daiwa-House-Logistics-Trust_FY2025/full.md`.
1 row: acquisition of DPL Gunma Fujioka (DHLT's 19th property, Greater Tokyo).

## Per-column null/value status
- `consideration` JPY 3,990,000,000 — **correct**. "purchase consideration was JPY3,990.0 million" (p51); Note "JPY 3,990.0 million (approximately S$35.4 million)" (p183); property card "JPY 3,990 million".
- `consideration_sgd` SGD 35,400,000 — **correct** ("approximately S$35.4 million", p183).
- `consideration_currency` JPY — **correct**.
- `valuation_at_acquisition` JPY 5,210,000,000 — **correct, and correctly the acquisition-date valuation**. "discount of 23.4% to the independent valuation of JPY5,210.0 million" (p51); footnote: independent valuation as at **31 January 2025**, income approach / DCF (p51). Correctly NOT conflated with the 31 Dec 2025 valuation.
- `vendor` Mitsubishi HC Capital Estate Plus Inc. — **correct** ("from Mitsubishi HC Capital Estate Plus Inc., an unrelated third party", p51).
- `date` 2025-03-24 — **correct**. "On 24 March 2025, DHLT completed the acquisition" (p51); portfolio statement "24 Mar 2025"; Note p183. current_fy.
- carrying / gain / net_proceeds — **N/A (acquisition)**; correctly absent.
- `source_page` 51 — **correct** (main acquisition narrative is on p51).

## This-FY timeline

| property | type | date | deal_fy_scope | as-reported gain/premium | use-of-proceeds |
|---|---|---|---|---|---|
| DPL Gunma Fujioka | acquisition | 2025-03-24 | current_fy | bought at 23.4% discount to independent valuation (JPY3,990m vs JPY5,210m, p51) | financed by borrowings + internal cash |

## Corrections proposed
None. All values verified against source.

## Suggestions / raw material
- **Value-creation raw material (acquisition, not a divestment gain):** the report highlights the 31 Dec 2025
  valuation of **JPY 5,230 million = 31.1% above the JPY 3,990m purchase** (p51 / MD&A bar chart). Two
  valuations are printed (JPY 5,210m at acquisition 31 Jan 2025; JPY 5,230m at year-end 31 Dec 2025) — the
  table captures only the acquisition-date one, which is the correct choice for `valuation_at_acquisition`.
- **DPU linkage:** n/a (acquisition). Financed by borrowings + internal cash; a JPY 3.99 billion loan facility
  was drawn in March 2025 to finance it, maturing 2028 (p184).
- **Coverage gaps:** acquisition structure (DH-CRUX Japan TMK) printed; loan facility detail printed; two
  valuations + discount (23.4%) + uplift (31.1%) printed; green certification (BELS 5-star) printed. Valuer
  NAME is NOT printed (only "independent valuer").
