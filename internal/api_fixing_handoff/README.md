# `sgx_reit_performance` — the DPU flow and its gates

2026-08-03. Numbers below are from `sgx_reit_performance_final` in dev, not asserted.

---

## The chain

Two separate tracks. **The pool closes on cash; the declaration closes on DPU.**
That is why `distribution_paid` and `distribution_declared` are different columns.

```
POOL (money)
  distributable_income_opening     left over from last year
  + income_for_year                operating income this year — rent, incl. tax-exempt
                                   overseas/dividend income and JV distributions
  + other_additions                NON-operating: capital distributions, divestment
                                   gains, sponsor top-ups, released retentions
  − amount_retained                held back, leaves the pool
  − distribution_paid              cash that actually left the bank
  = distributable_income_closing   carried into next year

DECLARATION
  distribution_declared            declared FOR this year — ties to DPU
  distribution_record              the tranches that make it up
  distribution_per_unit            headline DPU, in cents

UNITS
  units_in_issue                   issued at FY-end
  units_to_be_issued               owed but not yet issued
```

`issued_and_issuable = units_in_issue + units_to_be_issued`

### Where the operating / non-operating line sits

Classify by **economic source**, never by the label's position in the statement.

```
income_for_year   = total return attributable to Unitholders
                    − net tax and other adjustments
                    + tax-exempt income          overseas property income, exempted dividends
                    + JV / associate distributions

other_additions   = capital distribution · distribution from capital · capital gains
                    distribution · divestment gains · distribution of other gains ·
                    distribution top-up · amount released · coupon interest
```

Tax-exempt income and JV distributions are rent arriving through a tax or ownership
wrapper — they are the properties performing. `other_additions` is reserved for what the
properties did **not** earn: sale proceeds, sponsor support, and prior-year money returning.

20 rows carry an `other_additions`, S$419m in total, all capital in nature.

---

## GATE 1 — rollforward · **63/63** · HARD, 0.1%

```
opening + income_for_year + other_additions − amount_retained − distribution_paid = closing
```

Every figure is printed and audited. A failure means a row was misread. **Blocks promotion.**

**11 exempt, all legitimate:**

| | rows | why |
|---|---|---|
| no pool | XZL ×2, CY6U ×2, UD1U ×2, 8C8U | pure flow statements — no opening/closing exists in any year |
| suspended | D5IU ×2 | every distribution line is a dash |
| structural | J91U ×2 | never carries its closing balance into the next year |

---

## GATE 2 — declared · **41/45** · SOFT, 1%

```
distribution_declared = income_for_year + other_additions − amount_retained
```

Everything that entered the pool this year, less what was held back.

**29 n/a** — 24 rows where the AR publishes no declared figure at all (a null is the correct
answer there), plus 5 suspended.

**4 failures, all confirmed structural:**

```
M1GU ×2    retention is struck against the OPENING balance, not this year's income
ME8U       declared is on the Financial Review basis; the statement is on a paid basis
P40U       the AR only says "approximately S$4.0 million"; the exact figure is 4,035
```

> **Do not make this a hard gate.** A REIT that deliberately declares less than it earned will
> always fail it, and that is a payout policy, not a defect. Its value is detection — this gate is
> what found the AJBU and C2PU bugs, where the cash figure had been stored as declared.

---

## GATE 3 — tranches · **63/69** · HARD, 0.02 cents

```
sum(distribution_record.dpu) = distribution_per_unit
```

The array holds **only tranches in respect of this financial year**. Prior-year tranches are
dropped, not tagged, so no filter is needed. A tranche declared after year end but covering an
in-year period is KEPT — judge by the period, never the pay date.

**6 failures, three different limits of what the ARs publish:**

```
A17U ×2    the 2H tranche appears only in the NEXT year's report
DCRU ×2    one tranche straddles the year end and cannot be split
XZL  ×2    the 1H tranche rate is never disclosed at all
```

For the latest year of any semi-annual REIT this gate is structurally unreachable.

---

## GATE 4 — cash reconciliation · dev only · not yet automated

```
distribution_paid − paid_in_units = the distribution line in the cash flow statement
```

The **strongest** check we have, because it reconciles against a *second audited statement*
rather than deriving one line from another in the same table.

```
ME8U   385,455 − 29,754 = 355,701   exact
JYEU    85,556 − 13,453 =  72,103   exact
```

Verified by hand on 2 rows. To automate it, the cash flow distribution line needs extracting for
the 12 rows that have a DRP.

---

## Summary

| gate | severity | result | blocks promote |
|---|---|---|---|
| 1 rollforward | hard, 0.1% | **63/63** | yes |
| 2 declared | soft, 1% | 41/45 | no — review only |
| 3 tranches | hard, 0.02c | 63/69 | yes, minus the 6 known |
| 4 cash | dev only | 2/2 by hand | not yet |

---

## Rules that keep this honest

1. **Null means not disclosed. Never write 0**, and never infer a value from a gap. K71U shows a
   ~108m hole that looks exactly like retention and is not — the AR says it distributed 100%.
   Filling it would have published a false claim.
2. **A failed gate is a signal to open the report**, never a licence to compute a balancing figure.
3. **Judge a tranche by its period, not its pay date.**
4. **`distribution_paid` is not all cash** — 12 rows settle part of it in units via a DRP
   (C38U FY2024: S$115.5m of S$874.1m). `paid_in_units` records it, dev-side.
5. **Never reconcile the Statistics of Unitholdings register against a Note** — the register is
   dated weeks after year end and includes post-year-end issuance.

Full evidence: `docs/7-30-2026-schema-review/`. Extraction output and agent reports:
`fixes/perf_reextract/`.
