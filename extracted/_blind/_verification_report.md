# Blind verification report — independent re-extraction vs original pilot

**Method.** Three fresh agents (Sonnet, zero conversation context, no memory, no access to
our extracted JSON or schema docs) were given only the parsed report + a list of facts to
find, for a stratified sample: full trust-level performance block, 5 properties each
(revenue / NPI / valuation / occupancy / tenure), top-3 tenants + basis wording, income
note lines, and key transactions. Their outputs (`extracted/_blind/<symbol>.json`) were
diffed programmatically against the originals.

## Result: 71 / 73 numeric values agree exactly; the 2 diffs are definitional, not errors

| Trust | Compared | Agree | Diff |
|---|---|---|---|
| CICT | 21 | 19 | 2 (both adjudicated below) |
| FCT | 26 | 26 | 0 — incl. all 5 per-property NPIs and the duplicate-row trap (both runs independently picked the row that reconciles) |
| CLCT | 26 | 26 | 0 — incl. dual-currency values and the 5.499 FX rate |

Top-3 tenants: identical names, percentages and basis wording across all three trusts
(CICT: RC Hotels 4.5 / GIC 1.6 / The Work Project 1.6, basis "GRI excl GTO, proportionate";
FCT: NTUC FairPrice 6.0 / BreadTalk 3.2 / Dairy Farm 1.8 on GRI; CLCT: JD.com 1.8 /
POP MART 1.0 / Bestseller 1.0, basis "Total GRI incl GTO").

## Adjudication of the two diffs — both are the report disclosing two true numbers

1. **CICT portfolio value: 27,397.5m (ours) vs 25,601.6m (blind).** Both in the report:
   S$27,397.5m is the portfolio valuation *including proportionate JV interests* (p23);
   S$25,601.6m is audited balance-sheet investment properties (p105). Different
   definitions, both correct. → `sgx_reit_performance.portfolio_value` needs its
   definition pinned (recommend: as-presented portfolio valuation incl. JV proportionate,
   since that is what every trust headlines; B/S figure is fetchable from
   sgx_company_report anyway).
2. **CICT Gallileo valuation: 547.6m (ours) vs 519.7m (blind).** Both in the report:
   S$547.6m is the 100%-basis figure (property factsheet p56 **and** the audited Portfolio
   Statement, $547,629k); S$519.7m is CICT's 94.9% proportionate interest (valuation
   table p23, EUR344.5m × 1.509). Different basis, both correct. → direct, independent
   confirmation of the **`value_basis` column** recommended in `_pilot_schema_fit.md`
   gap #2 — without it, two correct extractions of the same fact disagree.

## Independent confirmations beyond the numbers

- Both runs independently hit the FCT p34 duplicate-row parsing artifact and resolved it
  the same way (the set that reconciles to audited totals).
- Both runs independently flagged the CICT distributable-income layering (S$860.9m
  headline vs S$869,957k distribution-statement subtotal vs S$1,119,753k incl. opening
  balance) and chose the headline figure.
- Both runs independently noted CLCT's S$83.9m distributable income contains a S$5.7m
  top-up vs the S$78.2m distribution-statement figure — a `figure-definition` nuance worth
  an extraction rule.
- CapitaSpring dual revenue (37.7m consolidated-period vs 72.7m 100%-basis full-year) was
  surfaced by both runs — same basis issue as Gallileo.

## Verdict

Zero true extraction errors found in the sample. Every disagreement traced to the report
publishing the same fact on two bases — which is the strongest possible evidence for the
two schema additions already proposed (`value_basis`, pinned `portfolio_value`
definition), and for adding one extraction rule: **when a report shows a figure on both
100% and proportionate basis, capture the basis, never just the number.**
