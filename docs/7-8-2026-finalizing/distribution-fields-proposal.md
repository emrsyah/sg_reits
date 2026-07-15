# PROPOSAL (NOT executed) — distribution rollforward: explicit fields + arithmetic guards

**Status: DRAFT / awaiting emirsyah go-ahead.** Do NOT implement until approved. Captured
2026-07-08; revised 2026-07-09 (rollforward model + reconciliation guards).

## Context
Today `sgx_reit_performance` holds `net_distributable_income` + `distribution_paid` + a
`distribution_basis` flag. But the Distribution Statement is actually a **rollforward** — an
opening pool, income generated this year, a cumulative available pool, cash paid out during the
year, and a closing pool. Collapsing that into two fields loses the story (e.g. K71U's cash-out of
276,593 across three half-years vs the 212,406 declared for FY2025) and can't be reconciled. This
proposal captures the rollforward **as-disclosed** and adds guards that the lines must tie.

### Two DIFFERENT "distribution" figures — do not conflate (K71U FY2025)
- **212,406** = distribution **declared for FY2025** (= DPU 5.23c × units; Keppel's headline
  "Distribution to Unitholders"). This is what `distribution_paid` currently holds for K71U —
  **defensible, NOT a bug.**
- **276,593** = **cash actually paid out during the year** = the rollforward's "Total Unitholders'
  distribution (incl. capital gains)" line = 2H2024 (107,633) + 1H2025 (105,549) + partial-advance
  2H2025 (63,411) = 7.15c across three different half-years. A cross-year cash-**timing** figure.

They differ by timing + capital-gains top-ups. The rollforward needs the 276,593 line to close
(`available - paid = closing`); the 212,406 declared figure is a separate, FY-aligned headline.
Both are legitimate — this proposal captures each in its own field so neither overwrites the other.

## The rollforward fields (all raw / as-disclosed from the Distribution Statement)

| # | Proposed column | Report line (K71U p121) | Meaning |
|---|---|---|---|
| A | `distributable_income_opening` *(NEW)* | "...at beginning of the year" | prior-year carry-forward pool brought into this year |
| B | `net_distributable_income` *(existing — keep name/value)* | the unlabelled for-year subtotal | income **generated & available** this year, **before** retention |
| P | `distribution_cash_paid` *(NEW)* | "Total Unitholders' distribution (incl. capital gains)" | cash **actually paid out** during the year (cross-period) |
| E | `distributable_income_closing` *(NEW)* | "...at end of the year" | pool carried to next year = **A + B - P** |

Plus the existing **`distribution_paid`** — the distribution **declared for the year** (DPU basis;
K71U = 212,406). **Left as-is** (not renamed, not overwritten). Optionally rename it to
`distribution_declared_for_year` for clarity (a naming decision below), but its VALUE stays.

Naming: kept close to the report but trimmed (`..._opening / _closing`). Adding P as a
**new** column (not repurposing `distribution_paid`) is deliberate — `distribution_paid` already
carries the declared/headline value for many REITs and must not be silently reassigned to the cash
line.

### CANONICAL SOURCE — the audited **Distribution Statement**, nowhere else
All four rollforward lines (A/B/P/E) MUST be read **verbatim from the audited Distribution
Statement** in the financial statements — never from the highlights page, manager's commentary,
press release, DPU tables, `sgx_manual_input`, or a chartbook. Those secondary sources round,
re-label, or use start-year vs end-year FY conventions, which is precisely what creates the
cross-REIT inconsistency this proposal removes. One source, one page-cited line per field, for all
37 REITs. If a REIT's Distribution Statement does not disclose a given line -> that field is null +
`null: not_disclosed` (skip its guard); do NOT backfill it from elsewhere. `distribution_paid`
(declared / DPU headline) likewise comes from its disclosed for-the-year distribution line, not a
highlights figure.

## Guards (the lines MUST reconcile — run on load; a break = investigate the source, never plug)

| # | Guard | Meaning |
|---|---|---|
| G1 | `A + B - P == E` | opening + generated - cash paid == closing — the full rollforward closes (**your "[1] + [2] - paid = end" reconciliation**) |
| G2 (cross-year) | `E(year N) == A(year N+1)` | this year's closing = next year's opening |

`distribution_paid` (declared) is **NOT** in the hard guards — it's FY-aligned, not part of the
cash rollforward. Soft relationship only: `retention ~= B - distribution_paid`.

A broken guard is NOT auto-corrected — it means a mis-extracted line; investigate the source
(REFERENCE §0.8, failed-check = investigate-never-plug). Per-REIT, any of A/B/P/E genuinely not
disclosed -> null + `null: not_disclosed` flag, and that guard is skipped (not forced).

## Worked example — K71U FY2025 (verified, p121, $'000)
```
A  opening (beginning of year)             107,871
B  net_distributable_income (for year)     212,406      (= declared FY2025, DPU 5.23c — no retention)
P  distribution_cash_paid (during year)    276,593      (7.15c across 2H24 + 1H25 + part-2H25)
E  closing    (A + B - P)                    43,684      G1: 107,871 + 212,406 - 276,593 = 43,684 OK
                                                         G2: E(FY2024)=107,871 = A(FY2025) OK
distribution_paid (declared for FY2025)    212,406      (headline; NOT in the cash rollforward)
```
Story now explicit: generated 212,406, cash-paid 276,593, **drew 64,187 out of the opening pool**
(incl. the ~$20m Anniversary capital-gains top-up). None of this is visible in today's two-field
model — and this is the confusion that started this thread: the 320,277 "Income available for
distribution" line is the cumulative pool (= A + B, **not** stored as a field), not the for-year
figure B; and the 276,593 cash line is distinct from the 212,406 declared headline.

## Simulation — generated / declared / cash-paid across 5 real FY2025 reports ($'000)
*(from prior sim; opening/closing populated per-REIT during the AR-read sweep, only K71U
verified end-to-end above)*

| REIT | B generated (before retention) | declared for year (= DPU, current `distribution_paid`) | P cash paid during year | Shape |
|---|---|---|---|---|
| **C38U** (CICT) | 869,957 | 860,874 | 750,125 | retains 9,083; P<declared (2H2025 paid early 2026) |
| **OXMU** (Prime US) | 28,726 | 8,303 | 6,149 | heavy retention (keeps 20.4m); cash 6.1m |
| **M44U** (MLT) | 406,397 | 406,397 | 417,743 | full payout (B=declared); P>B drawing prior-year pool |
| **K71U** (Keppel REIT) | 212,406 | 212,406 | 276,593 | no retention; P>B incl. capital-gains distributions |
| **CMOU** (KORE US) | 43,032 | 2,611 | 2,611 | suspended most of year; resumes 2H only; retains 40.4m |

Patterns: `B=declared=P` simple full-payout · `B>declared` retaining income · `P>B` paying from
carry-forward / adding capital or gains · `P<declared` final tranche paid after year-end.

## Retention / declared (the existing `distribution_paid`, soft)
Voluntary within-year retention (generate more than you commit to pay, e.g. OXMU keeps ~71%) shows
up in the rollforward as the pool growing (`E > A`) and as `B > distribution_paid`(declared). The
declared figure is often **DPU-derived**, so it stays OUT of the hard guards. Decision below whether
to rename it `distribution_declared_for_year` for clarity.

## Slimmed flag (keep, but narrowed)
With A/B/P/E explicit, the retention basis is computable, so the old `disclosed_after_retention`
(20) and `full_payout_no_retention_line` (9) values become **redundant -> drop**. Keep a flag ONLY
for what the numbers can't disambiguate (as-disclosed integrity):

| flag value | when | why needed |
|---|---|---|
| `suspended` | distributions halted (P=0, B>0) | P=0 != "earned nothing" (B>0) |
| `net_loss_no_distribution` | nothing distributable (B=0) | distinguishes real-zero from suspension |
| `rollforward_only` | only the cumulative line disclosed, no clean for-year subtotal | B is **derived** -> lower confidence |
| `cash_includes_capital_or_gains` | P includes non-income distributions (K71U) | explains P>B (not a bug) |
| `null: not_disclosed` (per field) | a rollforward line not disclosed | separates "not disclosed" from "missed"; skips its guard |

Clean full rollforward, all lines disclosed & G1-G2 pass -> flag **null** (no annotation). Net:
only ~8-10 REITs carry a flag instead of all 37.

## What's ALREADY done (independent of this proposal)
- NDI (B) already normalized to before-retention for all 37 + locked in `models.py`. Cumulative-pool
  errors fixed (K71U, CRPU). See outline §3. So `net_distributable_income` is already the B basis
  consistently even if this proposal is NOT executed.

## `adjusted_distributable_income` — KEEP (orthogonal, do NOT delete)
Decision 2026-07-09: the rollforward does **not** subsume `adjusted_distributable_income`. It sits
on a different axis — the **fee-settlement method**, not timing/pool. `net_distributable_income`
(B) is the fees-in-units (basic-DPU) numerator; `adjusted_distributable_income` is the fees-in-cash
(diluted-DPU) sibling, paired with `weighted_avg_shares_basic/diluted` for the basic-vs-diluted
DPU two-method cross-check vs the colleagues' figures (models.py:243, added 2026-06-22). Populated
only when the manager elects fees-in-cash AND a second distributable-income figure is disclosed —
currently 2 REITs (BUOU FY2024 = 255,515 vs distribution_paid 262,580; M1GU FY2025 = 43,830 vs
39,715), null for the rest **by design**. Deleting it would drop the diluted-DPU check for exactly
those cases; null costs nothing elsewhere. -> retain the field as-is.

## If executed — work required
1. `models.py`: add A / P / E columns (keep B and `distribution_paid` as-is); add the G1-G2
   guards to validation; rewrite `distribution_basis` -> slim flag + docs.
2. `load_supabase.py`: map the new columns; run guards on load, refuse/flag on break.
3. DB: add `distributable_income_opening` / `distributable_income_closing` + `distribution_cash_paid`
   columns; migrate flag values. **Do NOT overwrite existing `distribution_paid`.** ("available" =
   A+B is display-derived, not stored — most Distribution Statements don't disclose it verbatim.)
4. One AR-read sweep (all 37): populate A/P/E from each Distribution Statement's actual lines
   (verified per-REIT, never derived) + set slim flags; run G1-G2 and resolve any break at the source.
5. Update any frontend/query references.

## Decision
- [ ] Execute the rollforward split (add A/P/E + guards)? (Y / N / later)
- [ ] Rename existing `distribution_paid` -> `distribution_declared_for_year` for clarity, or leave
      the name? (value stays either way) (rename / leave)

Until decided: `distribution_paid` stays exactly as-is — do NOT normalize or overwrite it. NDI (B /
before-retention) is already normalized + locked.

---

## Frontend presentation — recommended logic

Goal: an investor should grasp "what did the REIT earn, keep, promise, and pay" at a glance, with
the detail available on demand. Present as a **hierarchy** (headline -> context -> detail), never
five raw numbers side by side.

### Tier 1 — headline (always visible)
- **DPU (cents)** + **distribution yield %** — what investors care about first. `dpu` already stored.
- **Payout ratio** = `distribution_paid` (declared) `/ B` -> "distributes X% of distributable
  income, retains the rest." One number that captures the retention story.

### Tier 2 — the distribution rollforward (one expand / secondary card)
Show the flow as a small waterfall so the relationships are visual, not arithmetic (K71U FY2025):
```
 A Opening pool (from prior years)         ░░░░░               107,871
 B + Generated this year                   ██████████████      212,406
   = Available (A + B, display-derived)    ██████████████████  320,277
 P - Cash paid during the year             ────────────────    276,593
 E = Closing pool (to next year)           ███                  43,684   (A + B - P)
```
- Label the growth to the available subtotal as prior-year carry-forward; label `B` as this-year earnings.
- Label the drop to `E` as cash paid; when `P > B`, footnote "paid more than earned this year —
  drew down the pool", NOT a discrepancy.

### Tier 3 — detail / tooltips
- **Opening pool** — distributable income retained from prior years, brought into this year.
- **Generated this year** (`net_distributable_income`) — income generated & available to distribute
  this year, before retention.
- **Available for distribution** — cumulative pool = opening + generated (display-derived, A + B; not a stored field).
- **Declared for the year** (`distribution_paid`) — amount declared for this year (basis of DPU).
- **Cash paid during year** (`distribution_cash_paid`) — actual cash out this period (mixes tranche
  timing; can include capital/gains and prior-year pool).
- **Closing pool** — retained to next year = available - cash paid.

### Case-based rendering (drive off the slim flag + the A/B/P/E relationships)

| Case | Detect by | FE treatment |
|---|---|---|
| **Clean full payout** | `B == distribution_paid`, `E ≈ A`, flag null | Collapse waterfall to "100% payout, no net retention" |
| **Retention** | `B > distribution_paid` / `E > A` | Show retention + payout-ratio badge |
| **Heavy retention** | payout ratio < ~50% | Highlight retention prominently (e.g. OXMU keeps ~71%) — explains low yield vs earnings |
| **Suspended** | flag `suspended` (`P=0`, `B>0`) | Badge **"Distributions suspended"**; show `B` (earned) greyed; yield 0 |
| **Net-loss / nil** | flag `net_loss_no_distribution` (`B=0`) | Badge "No distributable income (net loss)"; distinct from suspended |
| **Paid from pool / gains** | `P > B` (+ flag `paid_from_carry_forward` / `cash_includes_capital_or_gains`) | Footnote on `P`: "includes prior-year pool / capital or gains"; do NOT render as an error |
| **Cash < declared** | `P < distribution_paid` (timing) | Footnote: "final FY tranche paid after year-end" |
| **Rollforward-derived** | flag `rollforward_only` | Show `B` with a subtle "estimated" marker |
| **Partial / stub period** | `dpu_period_months` < 12 | Annotate DPU/yield "for an N-month period (annualise for comparison)" |

### Guardrails (as-disclosed integrity in the UI)
- **Never fabricate a missing field.** Null -> render "—" / "not disclosed", never 0 or a computed
  guess (the slim flag's null-reason explains why).
- **Don't compute retention/payout when a needed field is derived or null** (rollforward cases) —
  show the raw disclosed lines and mark the rest unavailable.
- **Cross-REIT comparisons** should use `B` (before-retention, comparable) or the payout ratio, NOT
  `P` (period-mixed, not comparable across REITs).
- Currency: show in the REIT's presentation currency (`performance.currency`); absolute figures are
  already in base units.
