# `sgx_reit_performance` — the DPU cluster: what it is, what to keep, what to drop

Verified 2026-07-31 against prod (74 rows) and the annual report text in `parsed_reports_datalab/`.
Four independent Sonnet passes covering **18 REITs**: the distribution statement lines, the units
disclosure, the DPU disclosure, the pool rollforward + retention, and what REITs put in their own
investor highlights pages.

Scope: the distribution/DPU columns only. Leverage, ICR, occupancy and the portfolio KPIs are out of
scope here — see `performance-column-brief.md` and `performance-normalization.md`.

---

## 1. What this cluster is for

One question:

> **A REIT earned money this year. How much reached unitholders, and how much per unit?**

A REIT does not distribute accounting profit. It distributes a separately-computed pool that behaves
like a bank account carrying a balance year to year:

```
  opening balance     left over from last year          distributable_income_opening
+ earned this year    the pool generated in the FY      net_distributable_income
- retained            deliberately held back            (today inside other_movements)
- paid out            cash that actually left           distribution_cash_paid
= closing balance     carried into next year            distributable_income_closing
```

**Why a balance exists at all:** REITs must distribute ≥90% of taxable income for tax transparency,
but the final tranche is declared near year-end and paid *after* it. There is always income in
transit. That residue is the opening/closing balance — not a discretionary reserve.

---

## 2. The source of the confusion — three different "amounts paid"

Three numbers all look like "the distribution". They are genuinely different, and each has exactly
one job:

| column | C38U FY2025 | what it is | its one job |
|---|---|---|---|
| `net_distributable_income` | 869,957 | what the pool **earned** | numerator of the payout ratio |
| `distribution_paid` | 860,874 | what was **declared for** the FY | ties to DPU |
| `distribution_cash_paid` | 750,125 | what **left the bank** in the FY | closes the rollforward |

Declared ≠ cash paid because of **timing**. Earned ≠ declared because of **retention**.

Drop the wrong one and something specific breaks. The meeting proposed dropping
`distribution_cash_paid`; that would break the rollforward on every REIT, because the identity closes
on the cash line, never the declared one.

This also explains the direction inconsistency in prod — 19 rows where declared > cash, 9 where
cash > declared. It depends which way the year-end straddle fell. **Not an extraction error.**

---

## 3. The rollforward is audited, citable, and it closes

All 12 REITs examined publish explicit opening and closing balance lines. **We derived nothing.**

```
BUOU  124,747 + 224,654 - 237,992                = 111,409  OK
K71U  107,871 + 212,406 - 276,593                =  43,684  OK
N2IU  141,525 + 421,380 - 422,889                = 140,016  OK
T82U   45,928 + 207,280 - 191,186                =  62,022  OK
SET    39,886 +  74,787 -  76,431                =  38,242  OK
HMN   134,789 + 256,708 - 231,247 - 23,200(ret)  = 137,050  OK
C38U  249,796 + 869,957 - 750,125 -  9,083(ret)  = 360,545  OK
```

**12 REITs, zero failures.** This is the strongest integrity property in the whole table, and the
reason to keep the pool columns even though no REIT puts them on its highlights page.

### The cumulative trap

*"Amount available for distribution"* (C38U 1,119,753) is **opening + income**, a cumulative
balance — not the year's income. `net_distributable_income` must be the **869,957** subtotal.
AJBU publishes only the cumulative figure, so the year's income must be derived:
`332,893 - 64,842 = 268,051`.

---

## 4. Retention — real, but occasional

Only **2 of 12** REITs publish an explicit retention line:

> HMN: *"Amount retained for asset enhancement initiatives and/or for general corporate and working
> capital purposes = (23,200)"* — confirmed in narrative: *"Total distribution was S$233.5 million,
> after retaining S$23.2 million"*
>
> C38U: *"Amount retained for general corporate and working capital purposes"* — (9,083)

The other ten distribute the full for-year pool, and their rollforwards close with **no residual**.

### ADD `amount_retained` — with a hard rule

Populate **only** where the annual report names it. Expect ~20% fill. **Null means "not disclosed",
never zero.**

> **Do NOT backfill it from the rollforward residual.** K71U shows a ~108m gap that looks like
> retention and is not — it is a cumulative-vs-headline timing artefact. Computing a plug there
> would publish "this REIT held back S$108m", which is false. This is the standing invariant: a gap
> is a signal to investigate the source, not a licence to compute a balancing figure.

Retention is the only *named* movement found across 12 REITs, so `amount_retained` can largely
replace the generic `distribution_pool_other_movements`, which today mixes retention with capital
returns and adjustments under one unhelpful label.

---

## 5. Units — the denominator problem

`number_of_shareholder_units` is the **year-end units in issue**. REITs compute DPU on the
**weighted average during the year**. N2IU states it outright — DPU is tied to *"the weighted average
number of the Group's units in issue for such financial year."*

```
        year-end        weighted avg     gap
C38U   7,611,318,000   7,425,129,000   +2.5%
K71U   4,013,867,000   3,903,899,000   +2.8%
TS0U   5,524,617,000   5,508,095,000   +0.3%
M44U   5,110,907,000   5,098,108,000   +0.25%
```

Always the same direction — fee units, placements and DRP issue units throughout the year, so
year-end >= average. **`DPU x number_of_shareholder_units` systematically overstates**, which is why
that identity fails on 18 of 55 rows.

**ADD `weighted_average_units`.** Every report discloses it in the EPU note. Without it, DPU cannot
be verified against anything.

### `units_to_be_issued` — DROP

It is **management fees payable in units but not yet allotted**:

> A17U: *"Management fees payable in Units | 555"*
> C38U: *"- payment of management fees | 14,120"*
> ME8U: *"Units to be issued at end of the year as settlement of Manager's management fees | 816"*

Three incompatible disclosure structures, with **no flag telling them apart**:

| REITs | structure | our `number_of_shareholder_units` |
|---|---|---|
| A17U, C38U, ME8U | separate line on top of a base issued figure | **excludes** it — complementary, correct |
| BUOU, TS0U | headline IS *"units in issue and to be issued"* | **already includes** it — **double-count** |
| M44U | concept does not exist; fee units go straight to issued | correctly null |

BUOU's balance sheet line is literally `Units in issue and to be issued ('000) | 3,790,771` — the
figure we store as `number_of_shareholder_units` — while we *also* store the 12,578 component
separately.

Materiality is **0.1-0.4%** of units outstanding (BUOU 12.6M/3.79B; TS0U 5.3M/5.52B). It matters only
for diluted per-unit maths, which REITs already publish separately. 35% populated, ambiguous
relationship to its neighbour, negligible signal → **drop**.

**Independent of that decision:** `number_of_shareholder_units` still means two different things
across REITs (issued-only vs issued-and-issuable). That must be standardised either way.

### `number_of_unitholders` — keep

Verified as a **count of investors**, from the "Statistics of Unitholdings" total row in all six
checked: C38U 91,421 · K71U 75,437 · TS0U 28,418 · BUOU 28,759 · N2IU 31,768. BUOU ties to the unit
(3,790,770,958).

One fix: **M44U's figure is dated after FY-end** — right concept, wrong date. Already flagged in our
own `_notes.json`.

---

## 6. `adjusted_distributable_income` — DROP

**4% populated (3 of 74), and NOT_FOUND in all six annual reports checked.**

No REIT publishes a second distributable-income figure. All of them pay manager/trustee fees partly
in units, added back as a non-cash adjustment *inside* the single build-up — only one headline DI
figure is ever published. The three populated rows contradict each other, sometimes above and
sometimes below `net_distributable_income`:

```
BUOU FY2024  adj 255,515,000   net_di 210,337,000
J91U FY2024  adj 149,100,000   net_di 164,064,000
```

This is a genuine absence, not a coverage gap. (Note: AJBU does publish an *"Adjusted DPU"* of
10.629 cents — a per-unit concept, not this column.)

---

## 7. `distribution_record` — restructure

**Root cause of the tally failure: the array mixes two accounting bases.** It normally holds this
year's tranches, but some rows also carry a prior-year tranche that was *paid in cash* this year:

```
AJBU FY2025   0.819c  period 2024-11-28 to 2024-12-31   <- FY2024 period
              5.133c  period 2025-01-01 to 2025-06-30
              5.248c  period 2025-07-01 to 2025-12-31
              sum 11.200 vs dpu 10.381   (excess = exactly 0.819)

T82U FY2025   1.570c  period 1 Oct - 31 Dec 2024        <- FY2024 period
              + the four FY2025 quarters
              sum 8.605 vs dpu 7.035     (excess = exactly 1.570)
```

The **headline DPU is correct in both** — AJBU's two 2025 tranches sum to 10.381 exactly, T82U's four
quarters to 7.035 exactly. The array is contaminated because it serves `distribution_paid` (cash) and
`distribution_per_unit` (accrual) at the same time.

`sum(record) = dpu` fails on **26 of 65** rows:

| cause | rows |
|---|---|
| DPU rounding P0 (§9) | ~14 |
| prior-year cash tranche included | ~8 |
| incomplete record — one tranche of two captured | ~4 |

Changes: `period_start` / `period_end` as **real dates** (today `period` is free text in 3+ formats),
**drop `ex_date`** (null on every row sampled), **add `basis`** (`accrual` | `cash_paid`).

A normal payment lag is **not** a defect — HMN's 2H tranche has `pay_date 2026-02-27`, declared for
FY2025 and paid the following February. The period is in-year.

### `distribution_period_months`

Definition: **the months of the reporting financial year that the headline `dpu` covers** — 12
normally, or the stub length in a transition year. *Not* the span of the cash tranches.

**8C8U's `3.2` is correct**, not a bug: its period is `'FP 2025 (25 Sep 2025 - 31 Dec 2025)'` and the
REIT listed in September. **CMOU's `dpu = 0`** against a record of 0.25 is the rounding P0, not a
suspension.

Cadence is genuinely non-uniform, and that is real-world variation rather than a data problem:
T82U quarterly · AJBU/HMN/N2IU semi-annual · C38U semi-annual plus an advanced tranche at the
14 Aug 2025 placement · J69U semi-annual with a mid-period split · D5IU suspended.
**J69U's financial year ends 30 September** — FY2025 = Oct 2024 to Sep 2025.

---

## 8. What REITs themselves lead with

Surveyed the front "Financial Highlights" / "At a Glance" pages of six REITs:

| metric | in how many highlights sections |
|---|---|
| **Distribution per Unit** | **6 of 6** — always first, always in cents |
| **Total distributable income / distribution to unitholders** | **6 of 6** |
| NAV per unit | 5 of 6 |
| Distribution yield | 2 of 6 (AJBU 4.61%, K71U 5.4%) |
| Units in issue | 1 of 6 (AJBU only) |
| Number of unitholders | 0 of 6 |
| Pool rollforward / retained amounts | **0 of 6** — notes-level detail only |

**Read this as layering, not as a delete list.** DPU and total distribution are the irreducible pair.
The pool rollforward is what makes those two numbers *verifiable*, so it stays in the data even
though it belongs behind a detail view rather than on a summary card.

---

## 9. P0 — the DPU rounding bug (still unfixed)

`build_final_tables.py:30`:

```python
return round(float(value) * tbl[ccy]['SGD'])     # no ndigits -> integer
```

Every per-unit figure in a foreign presentation currency is rounded to a whole number:

```
SET  FY2025  record sums to 13.609   dpu stored 20.000
MXNU FY2024  record sums to  2.870   dpu stored  5.000
DCRU FY2025  record sums to  3.600   dpu stored  5.000
UD1U FY2024  record sums to  1.900   dpu stored  3.000
CMOU FY2025  record says     0.25    dpu stored  0
BTOU nav 0  |  MXNU nav 1  |  MXNU dpu 5
```

**Fix: `round(x, 6)`.** It corrupts headline investor-facing numbers today and causes roughly half
the `sum(record) != dpu` failures.

---

## 10. Verdict — keep / add / drop

### KEEP (7)

| column | why |
|---|---|
| `distribution_per_unit` | the headline metric; 6/6 REITs lead with it |
| `distribution_record` | restructured — see §7 |
| `distribution_period_months` | needed to interpret stub years (8C8U 3.2, J69U Sep year-end) |
| `net_distributable_income` | what the pool earned; payout-ratio numerator |
| `distribution_paid` | declared for the year; the only column that ties to DPU |
| `distribution_cash_paid` | closes the rollforward on 12/12 REITs |
| `distributable_income_opening` / `_closing` | audited AR figures, not derived |
| `number_of_shareholder_units` | keep, but standardise issued-only vs issued-and-issuable |
| `number_of_unitholders` | clean holder count |

### ADD (2)

| column | why |
|---|---|
| `weighted_average_units` | the true DPU denominator; without it DPU cannot be verified |
| `amount_retained` | explicit retention only (~20% fill); replaces the vague `other_movements` |

### DROP (3)

| column | why |
|---|---|
| `adjusted_distributable_income` | 4% fill, NOT_FOUND in all 6 ARs, 3 rows mutually inconsistent |
| `units_to_be_issued` | 0.1-0.4% materiality, double-counts inside `number_of_shareholder_units` on 2 of 6 REITs, no flag |
| `ex_date` (inside `distribution_record`) | null on every row sampled |

Net: **28 columns → 27**, but the cluster becomes verifiable rather than merely present.

---

## Action order

**Mechanical, no decision needed:**
1. **P0** — `round(x, 6)` at `build_final_tables.py:30`; rebuild and re-promote.
2. Fix AJBU FY2025 `distribution_paid` → `268,051,000` (currently equals the cash figure; our own
   `_notes.json` says the cash line was *"deliberately NOT used"*).
3. Move the prior-year cash tranches out of `distribution_record` on AJBU and T82U, or tag them
   `basis = cash_paid`.
4. Backfill the incomplete records (C2PU FY2025, J91U FY2025 — each missing one tranche).
5. Re-date M44U `number_of_unitholders` to the FY-end register.

**Needs a decision:**
6. Drop `adjusted_distributable_income`, `units_to_be_issued`, `ex_date`.
7. Add `weighted_average_units` and `amount_retained`.
8. Restructure `distribution_record` (real dates + `basis`).
9. Standardise `number_of_shareholder_units` on issued-only vs issued-and-issuable.

**Gates to add:**
10. `opening + income + other - cash_paid - retained = closing`
11. `sum(record where basis = accrual) = distribution_per_unit`
12. `distribution_per_unit x weighted_average_units ≈ distribution_paid`

---

## Verification note

Fill rates, tally counts and prod values were computed directly against the database. Annual-report
quotations came from sub-agents working in `parsed_reports_datalab/` and our own `_notes.json`; the
load-bearing claims — the AJBU 268,051 discrepancy, the AJBU/T82U stray tranches, the BUOU/TS0U
double-count, and the K71U false-retention warning — were cross-checked against stored data by hand.
