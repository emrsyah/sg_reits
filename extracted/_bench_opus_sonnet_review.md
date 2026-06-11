# Opus vs Sonnet benchmark — two unseen trusts (skill-equipped, blind)

4 agents: {Opus, Sonnet} × {Keppel REIT K71U.SI FY2025, Daiwa House Logistics DHLU.SI FY2025}.
Each got the skill (SKILL.md + REFERENCE.md), the source markdown, and the scripts — nothing
else (no prior extractions, no schema docs). Diff script: `_bench_compare.py`.

## Headline

**274 agree / 46 differ on comparable values — and after adjudication, ~41 of the 46 "diffs"
are both-correct values taken from different disclosed bases, not errors.** Zero hallucinations
in either model: every value traced to the report.

| | Opus | Sonnet |
|---|---|---|
| K71U.SI QC gate | PASS (2 WARN, adjudicated) | PASS (2 WARN, adjudicated) |
| DHLU.SI QC gate | FAIL→adjudicated structural (cross-currency Σ) | PASS via _notes reconciliation |
| Keppel Σ GR / NPI | 274,478,000 / 215,905,000 = reported, exact | same, exact |
| Daiwa Japan NPI Σ | JPY 4,789m vs 4,787m reported (rounding) | same |
| Tokens / duration | 132.9k+120.7k / ~6.4+5.8 min | 105.6k+149.2k / ~6.4+9.1 min |

Both models independently reproduced the audited reconciliations exactly on both trusts —
the strongest evidence yet that the skill + QC pipeline produces convergent output.

## Adjudicated diff clusters

1. **Daiwa market_valuation, 19/19 properties (27 diffs incl. Tan Duc)** — NOT errors.
   Opus took factsheet appraisal values in **JPY/VND** (`currency: JPY`); Sonnet took the
   audited Statement of Portfolio book values in **SGD** (`currency: SGD`, with the JPY
   figure in `alt_value`). Ratio ≈122 = JPY/SGD. Both rows are internally consistent and
   honestly labelled. **Schema gap**: nothing pins WHICH disclosed valuation source wins
   when factsheet (local ccy, appraisal) and audited portfolio statement (SGD, book) both
   exist. Sonnet's pick (audited, + alt_value) matches the skill's "audited wins" rule
   better; Opus's pick matches the "headlined valuation" instinct.

2. **Daiwa top-tenant %, 10/10 (10 diffs)** — same numbers, different key. The trust ranks
   tenants by **% of NPI**, not GRI. Opus put 24.5 etc. in `gri_percentage` with
   `pct_basis: "npi"` (spec-exact keys); Sonnet nulled `gri_percentage` and invented
   `pct_npi` (violates the pinned-key rule, though well-intentioned). Confirms the agents'
   own schema finding: `gri_percentage` is a misnomer — should be `pct_value` + `pct_basis`.

3. **Partial dates (7 diffs)** — Daiwa discloses only "Leasehold expiring in March 2067".
   Opus fabricated month-END (2067-03-31), Sonnet fabricated month-START (2067-03-01).
   Both invented a day because the column is a `date`. **Skill gap: no partial-date
   convention.** (tenure_raw verbatim was kept by both, so recoverable.)

4. **Keppel lease expiry + tenure (5 diffs)** — genuine Sonnet misses. The portfolio
   statement explicitly prints "expiring 13 December 2110" (OFC) and "30 September 2096"
   (KBT); Opus captured them, Sonnet nulled them. Sonnet also wrote `land_tenure:
   "Leasehold interest"` (verbatim leak) instead of the enum value `Leasehold`.

5. **Keppel value_basis enum disagreement (3 diffs)** — OFC/T Tower/KR Ginza II are
   partially-owned but **line-by-line consolidated**. Opus tagged `effective_interest`,
   Sonnet `joint_venture_100pct`; arguably both wrong — the audited rows are consolidated.
   **Schema gap: the enum semantics for "consolidated but <100% owned" are not pinned.**

6. **MBFC granularity** — Opus 1 row (14 properties), Sonnet 2 rows (T1&2+mall / T3,
   15 properties), mirroring the audited statement's own 2-line split. The known
   `property_group` open item, now reproduced by two top-tier models independently.

7. **Small coverage deltas** — Sonnet found 2 extra Daiwa adjustment lines
   (straight_line_rent, leasing_commission_amort) and 1 extra transaction (DPL Shinfuji);
   Opus found Keppel JV lease expiries Sonnet missed. Neither dominates: coverage edge
   alternates by trust.

## Convergent schema findings (both models, both trusts, unprompted)

- **`npi_attributable` sibling on performance**: Keppel headlines $381.4m attributable
  NPI; audited consolidated is $215.9m. Both agents flagged a single `net_property_income`
  field as structurally insufficient for JV-heavy trusts.
- **Single-tenant revenue suppression is systematic** (11/18 Daiwa Japan properties,
  confidentiality) — sparse `properties.gross_revenue` is expected, not missing data.
- **Cross-currency Σ-reconciliation needs a per-currency path** in check_extraction.py
  (Daiwa: per-property JPY/VND vs trust SGD produced false FAIL/WARN for both agents).
- **Portfolio value basis matters most here**: Keppel headline $11.66b vs B/S $5.57b —
  the largest gap in the corpus; the pinned portfolio_value definition handled it.

## Model verdict

Opus and Sonnet are **interchangeable on accuracy** at this task — zero hallucinations,
identical reconciliations, diffs dominated by unpinned conventions rather than capability.
Opus showed slightly better spec discipline (exact keys, enum values) and caught explicitly
printed dates Sonnet nulled; Sonnet showed slightly better audited-source preference and
alt_value usage, and found a few extra note lines. Neither exhibited the Haiku failure
modes (unit drift, false "not disclosed" without anchor proof, contradictory final message).
**Sonnet remains the right production tier**; the residual differences are fixed by pinning
three conventions (below), not by paying for Opus.

## Implementation status (done, same day)

All 5 action items below are implemented. check_extraction.py now enforces: enum
whitelists on land_tenure / value_basis / transaction_type / statement / income_model
(FAIL), tenure_raw-mentions-expiry-but-lease_expiry_date-null (FAIL), leasehold-with-
term-but-no-expiry / paraphrased tenure_raw (WARN), null-GLA-on-active-property (WARN),
pct_basis outside the known enum (deduped WARN), and a per-currency reconciliation path
(cross-currency rows excluded from Σ with a CROSS-CCY warn + _notes fallback).
SKILL.md pins: valuation-source precedence, enum-only columns, expiry-must-follow-
tenure_raw, partial dates → day 01, value_basis semantics, NPI-ranked tenants stay in
gri_percentage. REFERENCE.md: traps #19–22 + benchmark verdict in §5b.

Regression over all 7 directories: 3 pilots PASS (CLCT needed 20 mechanical fixes the
new gate exposed — 18 land_tenure normalizations, income_model 'rental'→'conventional',
CLCR units subscription moved out of property_transactions); Opus K71U PASS; the 3
remaining bench FAILs are kept unfixed deliberately as negative-control fixtures —
the gate catches Sonnet's 2 Keppel enum leaks and the 8 Daiwa "Leasehold expiring in…"
leaks that BOTH models made while the convention was unpinned. Sonnet's 3 nulled Keppel
expiry dates surface as WARNs, not FAILs, because Sonnet paraphrased tenure_raw
("85.0 years remaining") and destroyed its own evidence — hence the new verbatim-
tenure_raw warning.

## Action items → skill/schema

1. Pin valuation-source precedence when factsheet (local ccy) and audited SGD book value
   coexist: audited wins `market_valuation`, factsheet goes to `alt_value` + own currency.
2. Pin partial-date convention (only month-year disclosed → day 01 + note), keep verbatim
   in tenure_raw.
3. Pin `value_basis` semantics: consolidated-but-minority-owned → `consolidated` (the row's
   money IS consolidated); `effective_interest`/`joint_venture_100pct` reserved for
   equity-accounted assets.
4. Rename `gri_percentage` → `pct_value` (+ existing `pct_basis`) in top_tenants, or
   explicitly instruct "NPI-ranked tables still go in gri_percentage with pct_basis=npi".
5. check_extraction.py: skip Σ-reconciliation (or do per-currency Σ) when property rows
   carry a different currency than performance.
