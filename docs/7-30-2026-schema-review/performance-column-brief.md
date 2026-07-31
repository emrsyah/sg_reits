# `sgx_reit_performance` — what each column is, where it comes from, what is wrong

Verified 2026-07-31 against prod (74 rows, 28 columns), our `extracted/*/performance.json` +
`_notes.json`, and the annual report text in `parsed_reports_datalab/`. Three independent Sonnet
passes covered 14 REITs across the distribution statement, the units disclosure, and the DPU
disclosure.

Companion to `performance-normalization.md` (currency/FX and the identity scorecard). This document
answers the different question: **what is each column, and is it uniform across REITs?**

---

## Answers to the questions raised

| # | Question | Answer |
|---|---|---|
| 1 | `distribution_record` doesn't tally with `distribution_period_months` | Confirmed. The array mixes **two accounting bases**. §3 |
| 2 | How is DPU calculated — is it uniform? | The headline number is uniform and correct. The **denominator we store is the wrong one**. §4 |
| 3 | `adjusted_distributable_income` is mostly null | Not a gap — **no annual report discloses it**. Drop. §5 |
| 4 | `distribution_paid` vs `distribution_cash_paid` | **Two genuinely different concepts.** Keep both. §2 |
| 5 | Where do the units figures come from — uniform? | Uniform concept (year-end units in issue), but **not** the DPU denominator. §4 |

---

## 1. The distribution pool — how the seven columns relate

Every REIT publishes a **Distribution Statement** that rolls the pool forward:

```
  distributable_income_opening        amount available at the START of the year
+ net_distributable_income            income generated FOR the year
+ distribution_pool_other_movements   retentions, capital returns, adjustments
- distribution_cash_paid              cash actually disbursed DURING the year
= distributable_income_closing        amount available at the END of the year
```

C38U FY2025 (S$'000), verbatim from the statement on p107:

```
Amount available for distribution ... at beginning of the year      249,796
Total return attributable to Unitholders                            937,287
Net tax and other adjustments (Note A)                             (143,751)
Tax-exempt income                                                     7,885
Capital distributions                                                16,208
Distribution income from joint ventures                              52,328
  -> income for the year                                            869,957
Amount available for distribution to Unitholders                  1,119,753
Distributions to Unitholders during the year [5 tranches]          (750,125)
Amount retained for general corporate and working capital           (9,083)
Amount available for distribution ... at end of the year            360,545
```

```
249,796 + 869,957 − 750,125 − 9,083 = 360,545   ✓
```

The identity balanced **exactly on all six REITs examined** (C38U, A17U, AJBU, M44U, J69U, ME8U).

### The cumulative trap

`Amount available for distribution` (1,119,753) is **opening + income**, a *cumulative* balance —
not the income generated in the year. `net_distributable_income` must be the **869,957** subtotal.
Taking the cumulative line instead double-counts the opening balance. AJBU discloses only the
cumulative figure, so the year's income has to be derived: `332,893 − 64,842 = 268,051`.

---

## 2. `distribution_paid` vs `distribution_cash_paid` — keep both

These are **not duplicates**. They differ because a distribution is *declared* for one period and
*paid* in another.

| column | AR line | basis |
|---|---|---|
| `distribution_cash_paid` | *"Distributions to Unitholders **during the year**"* | **cash** — what left the bank this year, including a tranche declared for last year, excluding one declared this year but paid after year end |
| `distribution_paid` | the **declared-for-the-year** distribution — ties to the reported DPU | **accrual** |

Confirmed distinct:

```
C38U FY2025   declared 860,874   cash 750,125
J69U FY2025   declared 233,166   cash 221,237
ME8U FY2025   declared 362,609   cash 370,206
```

Confirmed identical where there was no timing straddle that year — A17U FY2025, both 669,086.

And legitimately null where the REIT publishes only one line: **M44U's statement has a single
distribution deduction** (*"Total Unitholders' distribution (including capital return)"* 376,135),
so there is no separate declared figure to store. The null is correct.

This explains the direction inconsistency in prod (19 rows where declared > cash, 9 where cash >
declared): it depends on which way the timing straddle fell that year. **It is not an extraction
error.**

> **Rule:** `distribution_cash_paid` is the rollforward component. `distribution_paid` is the
> DPU-basis figure. Never use `distribution_paid` in the opening/closing arithmetic.

### Meeting item — "drop `distribution_cash_paid`"

**Recommend against.** Dropping it breaks the rollforward identity on every REIT, because the
identity closes on the cash line. If only one can survive, it must be `distribution_cash_paid`.

### BUG — AJBU FY2025 `distribution_paid`

Stored as **133,531,000**, identical to `distribution_cash_paid`. Our own `_notes.json` records the
correct methodology and says the cash line was *"deliberately NOT used"* for this field. The AR's
DPU note (p144) gives *"Total amount available for distribution for the year"* = **268,051**.

Looks like a regression where the field was overwritten with the cash value. Fix to
`268,051,000`.

---

## 3. `distribution_record` — the tally problem, explained

**Root cause: the array mixes accrual entries and cash entries.**

Entries are normally the tranches whose *periods* fall inside the financial year, and they sum to
the headline DPU. But some rows also carry a **prior-year tranche that was paid in cash this year**:

```
AJBU FY2025   0.819¢  period 2024-11-28 to 2024-12-31   <- FY2024 period
              5.133¢  period 2025-01-01 to 2025-06-30
              5.248¢  period 2025-07-01 to 2025-12-31
              sum 11.200  vs  dpu 10.381  (excess = exactly 0.819)

T82U FY2025   1.570¢  period 1 Oct - 31 Dec 2024        <- FY2024 period
              + the four FY2025 quarters
              sum 8.605  vs  dpu 7.035  (excess = exactly 1.570)
```

In both cases the **headline DPU is correct** — AJBU's two 2025 tranches sum to 10.381 exactly,
T82U's four quarters to 7.035 exactly. The array is what is contaminated, because it is serving
`distribution_paid` (cash) and `distribution_per_unit` (accrual) simultaneously.

### `sum(record) = dpu` fails on 26 of 65 rows — three causes

| cause | rows | example |
|---|---|---|
| **DPU rounding P0** (see §6) | ~14 | SET sum 13.609 vs dpu **20.000** |
| **Incomplete record** — one tranche captured of two | ~4 | C2PU FY2025 sum 7.650 vs dpu 15.290 (exactly half) |
| **Prior-year cash entry included** | ~8 | AJBU, T82U above |

### `distribution_period_months`

Correct definition: **the months of the reporting financial year that the headline `dpu` covers** —
12 normally, or the stub length in a transition year. *Not* the span of the cash tranches.

Values: `12` on 65 rows, `6` on 1, `3.2` on 1, null on 7.

**8C8U's 3.2 is correct, not a bug.** Its period is `'FP 2025 (25 Sep 2025 - 31 Dec 2025)'` — the
REIT listed in September, so 3.2 months is the real reporting period. (I initially flagged this as
suspicious; it is right.)

**CMOU FY2025 shows `dpu = 0` while its record says 0.25** — that is the rounding P0, not a
suspension.

### Structure

162 of 170 entries use `{dpu, period, ex_date, pay_date}`. Two defects:

- **`ex_date` is null on every row sampled** — carries no information.
- **`period` is free text in at least three formats**: `'2025-01-01 to 2025-06-30'`,
  `'1 October 2024 to 31 March 2025'`, `'2H 2025 (1 Jul - 31 Dec 2025)'`.

This matches the meeting request: split into real `period_start` / `period_end` dates, drop
`ex_date`. **Add a `basis` field** (`accrual` | `cash_paid`) so the mixed entries are explicit and
`sum(record) = dpu` becomes enforceable.

A normal payment lag is **not** a defect: HMN's second-half tranche has `pay_date 2026-02-27`,
declared for FY2025 and paid the following February. The period is in-year.

---

## 4. DPU — is it uniform?

**The headline figure is uniform and correct.** Every REIT reports an annual DPU in cents, and the
tranches sum to it exactly where our record is complete: C38U `5.62+1.35+4.61 = 11.58` ✓,
AJBU `5.133+5.248 = 10.381` ✓, J69U `6.054+0.096+5.963 = 12.113` ✓, HMN `2.526+3.576 = 6.102` ✓.

**The cadence is not uniform**, but this is real-world variation, not a data problem:

```
T82U  quarterly
AJBU, HMN, N2IU  semi-annual
C38U  semi-annual + an "advanced distribution" tranche at the 14 Aug 2025 placement date
J69U  semi-annual with a mid-period split (1-3 Apr 2025 stub around an acquisition)
D5IU  suspended — "no dividends or distributions were declared or paid on the Units"
```

**J69U's financial year ends 30 September**, not December: FY2025 = Oct 2024 – Sep 2025. Twelve
months, but not the same twelve as every other REIT. Any calendar-year comparison must handle it.

### The real problem: we store the wrong denominator

`number_of_shareholder_units` is the **year-end units in issue**. REITs compute DPU on the
**weighted average units during the year**. N2IU states it explicitly — DPU is tied to *"the
weighted average number of the Group's units in issue for such financial year."*

```
        year-end        weighted avg     gap
C38U   7,611,318,000   7,425,129,000   +2.5%
K71U   4,013,867,000   3,903,899,000   +2.8%
TS0U   5,524,617,000   5,508,095,000   +0.3%
M44U   5,110,907,000   5,098,108,000   +0.25%
```

The gap is always in the same direction: management-fee units, placements and DRP issue units
throughout the year, so year-end ≥ average. **`DPU × number_of_shareholder_units` therefore
systematically overstates the distribution** — which is why that identity fails on 18 of 55 rows.

**Fix: keep `number_of_shareholder_units` as year-end, and ADD `weighted_average_units`.** Every one
of the six reports discloses it in the EPU note, so it is extractable.

---

## 5. Column-by-column

Fill rates are out of 74 prod rows.

### Distribution pool

| column | fill | what it is | verdict |
|---|---|---|---|
| `distributable_income_opening` | 85% | pool at start of year | keep |
| `net_distributable_income` | 100% | income generated **for** the year (not cumulative) | keep |
| `adjusted_distributable_income` | **4%** | — | **DROP** — see below |
| `distribution_paid` | 88% | declared for the year; ties to DPU | keep (accrual) |
| `distribution_cash_paid` | 95% | cash disbursed during the year | keep (rollforward) |
| `distributable_income_closing` | 85% | pool at end of year | keep |
| `distribution_pool_other_movements` | 22% | retentions/capital returns | keep — absorbs C38U's −9,083 |

**`adjusted_distributable_income` — drop.** Checked in all six reports: **NOT_FOUND in every one.**
No REIT publishes a second distributable-income figure. All of them pay manager/trustee fees partly
in Units, added back as a non-cash adjustment *inside* the single build-up — only one headline DI
figure is ever published. The 3 populated rows (BUOU, M1GU, J91U) are inconsistent with each other,
sometimes above and sometimes below `net_distributable_income`. This is a genuine absence, not a
coverage gap.

### Units

| column | fill | what it is | verdict |
|---|---|---|---|
| `number_of_shareholder_units` | 95% | **year-end units in issue** | keep + standardise (below) |
| `number_of_unitholders` | 97% | **count of investors**, from "Statistics of Unitholdings" | keep |
| `units_to_be_issued` | 35% | units issuable but not yet issued | keep |
| — | — | `weighted_average_units` | **ADD** |

`number_of_unitholders` verified as a holder count in all six: C38U 91,421 · K71U 75,437 ·
TS0U 28,418 · BUOU 28,759 · N2IU 31,768. BUOU's total ties to the unit (3,790,770,958).

Two definitional inconsistencies to standardise:

- **TS0U and BUOU include "to be issued"/"issuable" units** in the figure (*"Units in issue and to
  be issued"*, *"Total issued and issuable Units"*), while C38U and K71U are issued-only. That
  overlaps `units_to_be_issued` and should be one convention.
- **M44U's `number_of_unitholders` is dated after FY-end** — right concept, wrong date. Already
  flagged in our own `_notes.json`.

### DPU

| column | fill | verdict |
|---|---|---|
| `distribution_per_unit` | 100% | keep — **but see the rounding P0** |
| `distribution_record` | 89% | restructure: real dates, drop `ex_date`, add `basis` |
| `distribution_period_months` | 91% | keep; definition above |

### KPIs and portfolio

`gross_revenue`, `net_property_income`, `portfolio_value` (100%), `aggregate_leverage` (100%),
`cost_of_debt` (99%), `interest_coverage_ratio` (100%), `net_asset_value_per_unit` (100%),
`portfolio_occupancy` (95%), `weighted_average_lease_expiry` (89%),
`weighted_average_debt_maturity` (89%), `properties_location`, `date`, `source_url`.

Two corrections to meeting assertions, both carried over from `performance-normalization.md`:

- **`interest_coverage_ratio` is a multiple, never a percentage** — 7 REITs, zero exceptions.
- **`portfolio_occupancy` is a percentage**, but note some REITs report *committed* occupancy and
  others *physical*; the label does not distinguish them.

---

## 6. P0 — the DPU / NAV rounding bug (still unfixed)

`build_final_tables.py:30`:

```python
return round(float(value) * tbl[ccy]['SGD'])     # <- no ndigits -> integer
```

Any per-unit figure in a foreign presentation currency is rounded to a whole number. Visible in
prod right now:

```
SET  FY2025  record sums to 13.609   dpu stored 20.000
MXNU FY2024  record sums to  2.870   dpu stored  5.000
DCRU FY2025  record sums to  3.600   dpu stored  5.000
UD1U FY2024  record sums to  1.900   dpu stored  3.000
CMOU FY2025  record says     0.25    dpu stored  0
BTOU         nav 0  |  MXNU nav 1  |  MXNU dpu 5
```

**Fix: `round(x, 6)`.** This is a one-character-class change that corrupts headline investor-facing
numbers today, and it accounts for roughly half the `sum(record) ≠ dpu` failures.

---

## Action order

**Mechanical, no decision needed:**
1. **P0** — `round(x, 6)` at `build_final_tables.py:30`; rebuild and re-promote.
2. Fix AJBU FY2025 `distribution_paid` → `268,051,000` (§2).
3. Move the prior-year cash tranches out of `distribution_record` on AJBU and T82U, or tag them
   `basis = cash_paid` (§3).
4. Backfill the incomplete records (C2PU FY2025, J91U FY2025 — each missing one tranche).
5. Re-date M44U `number_of_unitholders` to the FY-end register.

**Needs a decision:**
6. Drop `adjusted_distributable_income` (recommend yes — no REIT discloses it).
7. Add `weighted_average_units` (recommend yes — required to verify DPU at all).
8. Restructure `distribution_record`: `period_start` / `period_end` as dates, drop `ex_date`,
   add `basis`.
9. Standardise `number_of_shareholder_units` on issued-only vs issued-and-issuable.
10. Keep `distribution_cash_paid` (recommend yes — the rollforward closes on it, and the meeting
    proposed dropping it).

**Gates to add:**
11. `opening + income + other − cash_paid = closing`.
12. `sum(distribution_record where basis = accrual) = distribution_per_unit`.
13. `distribution_per_unit × weighted_average_units ≈ distribution_paid`.

---

## Verification note

All fill rates, tally counts and prod values were computed directly against the database. Every
annual-report quotation was produced by a sub-agent working from `parsed_reports_datalab/` and our
own `_notes.json`; the load-bearing claims — the AJBU 268,051 discrepancy, the AJBU/T82U stray
tranches, and the units concept — were cross-checked against the stored data by hand.
