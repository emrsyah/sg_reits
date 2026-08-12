# Haiku blind extraction vs original (and vs Sonnet blind run)

Same protocol as the Sonnet blind verification (zero context, no access to our outputs,
same stratified item lists), run on **Haiku**. Outputs: `extracted/_blind_haiku/<symbol>.json`.

## Scorecard (74 compared values)

| | raw | after unit normalization |
|---|---|---|
| Match | 52 | **71** |
| Real disagreement | 16 | **1** |
| Not found by Haiku | 6 | 2 |

The 19 "diffs" that vanished on normalization: Haiku reported all CLCT values in **RMB /
SGD millions** instead of absolute units (it even named its keys `_sgd_million`), ignoring
the explicit absolute-units instruction. Values themselves were exactly right — 10/10
property figures match our RMB fields ×1e6, 4/4 trust-level match ×1e6.

## The genuine differences

1. **CapitaSpring gross revenue (CICT)**: Haiku took S$72.7m (100%-basis full-year from
   the factsheet) where the consolidated figure is S$37.7m. Both numbers are printed in
   the AR (trap #7, dual basis) — Sonnet picked the consolidated figure *and* flagged the
   other; Haiku picked one without noting the conflict.
2. **Number of unitholders**: Haiku reported "not disclosed" for both CICT and FCT.
   It is disclosed (CICT p.193, FCT p.216, Statistics of Unitholdings) — Sonnet found
   both. A findability miss, not a hallucination.

No hallucinated values were detected: everything Haiku returned exists in the report.

## Side notes

- Haiku ran ~2–4× faster (110–222s vs 430–830s) at roughly a third of the per-token cost.
- It found the hard stuff: the 5.499 FX rate footnote, FCT's per-property NPIs, the exact
  audited Note 21 revenue lines, Rock Square's 51%+49% phases, the Yuhuating divestment.
- Failure modes are convention adherence (units) and conflict awareness (didn't flag
  dual-basis figures), not accuracy.

## Follow-up: Haiku WITH the reit-extraction skill (CICT re-run)

One more run (`extracted/_blind_haiku_skilled/C38U.SI.json`): same blind item list, but the
agent was told to read SKILL.md + REFERENCE.md first. Scored against the three failure modes:

| Failure mode | Unskilled Haiku | Skilled Haiku |
|---|---|---|
| Units convention | broke it (CLCT in millions) | **followed** — absolute units throughout, verbatim tenure_raw captured per skill convention |
| Dual-basis CapitaSpring | silently picked 72.7m | **half-fixed** — still picked 72.7m, but now annotated "On 100% basis; commercial component from 26 Aug onwards"; did NOT surface the 37.7m consolidated alternative, and its final message wrongly claimed "no dual-basis figures encountered" |
| Unitholders (p.193) | "not disclosed" | **still missed** — despite the skill's section map explicitly listing Statistics of Unitholdings |

Plus one regression: skilled run reported the CapitaSpring acquisition price as "not
disclosed" where the unskilled run had found S$1,045m/S$1.9b agreed value.

Net: the skill reliably transfers **conventions** (units, verbatim strings, per-record
basis notes) but does not fully transfer **judgment** (surfacing conflicts, exhausting the
section map before declaring "not disclosed") to the cheap model.

## Verdict

- **Original extraction further confirmed**: two independent models, blind, agree with it
  on essentially every sampled value (Sonnet 71/73, Haiku 71/74 normalized).
- **Haiku is usable as a cheap cross-check finder**, provided outputs go through unit
  normalization and the QC gate; reconciliation checks would catch its unit drift
  automatically (Σ in millions vs reported absolute fails loudly).
- **For production extraction, Sonnet-class or better**: the value of the expensive model
  isn't finding numbers — both find them — it's *convention discipline and trap awareness*
  (flagging dual-basis figures instead of silently picking one), which is exactly what the
  schema's qualifier columns depend on.
