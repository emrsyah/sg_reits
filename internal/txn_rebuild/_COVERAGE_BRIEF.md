# Divestment disclosure-coverage check

For EVERY divestment in your assigned REIT-years, determine what the ANNUAL REPORT itself
actually discloses. We are deciding whether to keep a `sale_price` column or derive the price
from `gain_loss_pct` x `reference_value`. That decision needs real disclosure rates, not our
extraction's fill rate.

## Rules (critical — past agents have violated these)
- Do ALL work YOURSELF. Do NOT spawn, delegate to, or wait on any sub-agent.
- Read the ANNUAL REPORT TEXT in `parsed_reports_datalab/`. Our own
  `extracted/<SYM>.SI_FY<YEAR>/property_transactions.json` and `_notes.json` are a useful
  starting point (they carry page cites) but they are NOT the answer — you are auditing whether
  they match the report.
- Never record "not disclosed" without having searched the report. Past agents produced FALSE
  "no data exists" findings. Search the divestment discussion, the financial review, the
  portfolio statement, the "year in review"/timeline sections, subsequent-events notes, and the
  held-for-sale note.
- Every "disclosed" answer needs a verbatim quote. Every "not disclosed" needs a note on where
  you looked.
- Never infer a number to make something balance.

## PARSED FOLDER MAPPING — read this before opening any file
For M44U, ME8U and N2IU the parsed folder label is ONE declared-FY BEHIND:
    28_M44U..._FY2022 = AR "FY23/24" = declared FY2023
    28_M44U..._FY2023 = AR "FY24/25" = declared FY2024
    28_M44U..._FY2024 = AR "FY25/26" = declared FY2025
Same pattern for ME8U (27_...) and N2IU (29_...). Confirm from each folder's `meta.json` `file`
field. O5RU and P40U folder labels are CORRECT declared FY. All other REITs are unoffset.

## For EACH divestment, record these fields
1. `property_name`
2. `sale_price_disclosed` — true/false. Is a SALE PRICE / CONSIDERATION disclosed for THIS
   property specifically? Quote it, with the currency.
3. `sale_price_scope` — `per_property` | `aggregate_multi_property` | `not_disclosed`.
   If the price covers several properties as one figure, say `aggregate_multi_property` and list
   which properties it covers.
4. `pct_disclosed` — is a premium/discount PERCENTAGE stated? Quote it.
5. `reference_disclosed` — is a reference figure disclosed (independent valuation / book or
   carrying value / original purchase price / SPV net identifiable assets)? Quote it and say
   WHICH basis.
6. `gain_disclosed` — is a dollar gain/loss disclosed? Quote it.
7. `notes` — anything odd: net-vs-gross proceeds, equity/share sale, partial stake, rounded
   percentage, figures in thousands, conflicting figures in different sections.

## Deliverable
A markdown table of every divestment with those columns, then counts for your batch:
  - how many have a per-property sale price disclosed
  - how many have a percentage disclosed
  - how many have a reference figure disclosed
  - how many have BOTH a percentage and a reference (i.e. price is derivable)
  - how many have NEITHER a sale price nor a derivable pair

Write your table to `txn_rebuild/_coverage_agent<N>.md` (N = your agent number) AND return the
counts in your final message. Do NOT write to any database.

## Source of truth — READ THIS
The answer must come from the ANNUAL REPORT TEXT in `parsed_reports_datalab/<folder>/full.md`.
Do NOT answer this question from `txn_rebuild/*.json` or `extracted/*/property_transactions.json`.
Those files are OUR extraction — auditing them against themselves proves nothing. They are useful
only as a pointer to page numbers; the verdict must be grounded in the report text you read.
If you find yourself reporting on our JSON rather than the AR, stop and open the AR.
