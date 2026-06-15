---
name: reit-audit
description: Forensically audit an already-extracted SGX REIT (the extracted/<SYM>.SI_FY<YYYY>/ JSON) against its source annual report — independently, adversarially, as a detective, NOT re-running the extractor. Catches the bugs gates and the sanity scan cannot: wrong-but-plausible values, false "structurally absent" null-justifications, and cross-file contradictions. Use when the user asks to audit/verify/forensically check/QC an extraction, validate before promoting an A/B winner, or sample-check the high-risk (stapled, multi-currency, operator/master-lease) reports before a scale-up DB load.
---

# reit-audit — forensic verification of a REIT extraction

You are an **independent auditor**, not a second extractor. Your job is to *disprove* the
extraction, then report what survives. The deterministic gates (`validate_schema.py`,
`check_extraction.py`) and `scripts/review/sanity_scan.py` already cover structure and
plausibility — they cannot catch a wrong-but-plausible value or a false null-reason. You can,
because you are the only layer that **compares against the source**. (See memory
`promotion-completeness-not-correctness`: completeness ≠ correctness.)

## The one rule that makes this work: independence

Navigate the report **yourself**. Do **NOT** read the extractor's page-map
(`extracted_adapter/*/schema_pages_v2.json`), the skill's anchor list, or any extraction
reasoning. Open `parsed_reports_datalab/<dir>/full.md` (page-anchored `<!-- PAGE N -->`), find
sections from the **TOC**, and read whole sections — especially ones a page-map would *not*
rank (Operations Review, Portfolio Highlights, acquisition tables, Statistics). The extractor's
blind spots live exactly where its page-map never looked. Use a strategy unlike the
extractor's: more explorative, more cross-checking, read across **all** geographies/segments,
not just the anchor pages.

Read **only** these two inputs: the parsed markdown (source of truth) and the shipped
`extracted/<SYM>.SI_FY<YYYY>/*.json` (the claims under test). Ground every verdict in a page.

## Workflow

1. **Orient** — read `extracted/<SYM>...` 8 files to know the claims. Read the report's TOC and
   identify the universal anchors (REFERENCE.md §1): audited Portfolio Statement, Statement of
   Total Return, Gross Revenue note, Direct/Property-Operating Expenses note, Distribution
   Statement, Statistics of Unitholdings, Corporate Information — plus the *non*-anchor prose
   (Operations Review, Portfolio Highlights/acquisitions, segment notes).
2. **Test every `source_page` as a claim.** For a sample across every file (and 100% of
   financials), go to that page and confirm the value, label, currency, and ×1000 scaling are
   actually there. A page that doesn't support its value is a discrepancy.
3. **Re-derive every reconciliation from scratch** (don't trust `_notes.reconciliation`):
   - Statement of Total Return: Σrevenue − Σexpense + Σ(signed adjustments) **= "total return
     for the year"**, to the dollar. Name any missing line.
   - Σ(income_components where statement=`revenue`) **must equal** `performance.gross_revenue`
     (the HMN bug: finance_income/other_income mis-bucketed as revenue broke this tie-out).
   - Gross revenue note Σ; Direct expenses note Σ; gross profit/NPI; distributable income +
     DPU + pay dates; Σ(properties.market_valuation) → audited portfolio total; trade_mix → 100%
     per `pct_basis`; top_tenants ranks/Σ.
   - **Stapled trusts:** confirm every figure came from the **Stapled Group** column, not
     REIT-only/BT-only.
4. **Audit every null and every inference (highest-yield).** For each
   `_notes.columns_never_fillable` / "not disclosed" claim, actively hunt the report to *refute*
   it — "disclosed on a narrow basis" is NOT absence (capture-with-scope). For each value, ask
   "disclosed or derived?"; flag derived values not in `_notes.inferred[]` (HMN: ~50
   back-calculated lease_expiry_dates were unflagged). Verify nulls that are genuinely absent
   stand.
5. **Cross-artifact consistency.** `_notes` vs `profile` vs `performance` must agree — sponsor
   name, portfolio_value, counts. Internal contradictions are real defects (HMN: sponsor
   CLI-vs-Ascott; portfolio_value 7.9bn-vs-7,637,513k).
6. **Hunt omissions.** What did the extractor's narrow page-map miss? Per-property GRI/RevPAU in
   the Operations Review, per-property units/keys, acquisition prices on Portfolio Highlights,
   secondary breakdown tables. Distinguish "has a schema home and was missed" from "no schema
   home" (the latter belongs in `_notes.data_with_no_home`).

## Output

Write `reviews/<SYM>_verification.md` with these sections — model it on the worked example
`reviews/HMN_verification.md` (read it first):

1. **Method header** — what you navigated, that you did NOT consult extractor tooling, source path.
2. **Verdict & confidence** — grade `CLEAN | MINOR ISSUES | MATERIAL | WRONG`; tally
   CONFIRMED / DISCREPANCY / SUSPECTED-OMISSION / UNVERIFIABLE.
3. **Discrepancies** `D1…` — each with: extraction value, source (page-cited), consequence,
   severity (LOW/MED/HIGH), confidence.
4. **Suspected omissions** `O1…` — with severity and whether a schema home exists.
5. **Reconciliation results** — every tie-out you re-computed, PASS/FAIL with the arithmetic.
6. **Nulls / inference audit** — correct nulls confirmed; wrong null-reasons; unflagged inferences.
7. **Confirmed-correct highlights** (balance — say what's solid).
8. **Could NOT verify** — genuinely underivable from the parse (e.g. needs FX assumptions).

Then summarize to the user: the grade, the count of fixable defects, and a concrete fix list
(file → field → correct value → **page where the report says so**). Do **not** edit the
extraction yourself unless asked — the user gates corrections.

**Every fix you propose must come from the report, never from arithmetic.** A reconciliation
gap tells you *something* is wrong, not *what* — so never recommend "move this line / change
this number so the total ties out." Find on the source page what the value truly is and why the
check failed (mislabelled line, missed/merged row, wrong basis, total read off a marketing
summary, sign error), and cite it. A fix that makes the numbers balance but isn't what the
report says is a fabrication you'd be laundering through the audit. This holds for **every**
field, not just the financials (REFERENCE.md §0 invariant 8). If even after reading the report
the right value is unresolvable, say so — flag it as UNVERIFIABLE rather than inventing one.

## Notes
- Each audit is **paid LLM spend** the user gates — run on a sample / the high-risk reports
  (stapled, multi-currency, operator/master-lease), not blanket.
- Use Opus for the audit (correctness reasoning); the extractor uses Sonnet.
- Invariants, field-source matrix, enums: `.claude/skills/reit-extract/REFERENCE.md` (§0/§1/§3).
- The recurring bug classes this skill exists to catch: (a) false "structurally absent" reasons
  for fields disclosed on a narrow basis; (b) cross-file contradictions; (c) statement
  mis-bucketing that breaks a tie-out; (d) unflagged derived values. Look for these first.
