# `sgx_reit_performance` — verification pass against the annual reports

Verified 2026-07-31 against all 74 rows of `extracted/*/performance.json` and the 32 FY2025 reports in
`parsed_reports_datalab/`. Four Sonnet sub-agents extracted the units figures; **every one of their 32
claims was re-checked mechanically** — the quoted line must exist at the stated line number and
contain the stated number — before any of it was used. 32/32 passed.

Companion to `performance-column-brief.md` and `performance-dpu-brief.md`. Those two answer *what is
each column*. This one answers **which of their claims survive contact with the reports**, and it
corrects four of them.

---

## 0. Corrections to the existing briefs

Read this section before relying on either brief.

| claim | source | verdict |
|---|---|---|
| *"the identity fails on 18 of 55 rows"* | both briefs §4 | ❌ **2 rows are broken.** The rest is denominator-concept noise under 12%. §3 |
| *"year-end ≥ average, always the same direction"* | both briefs §4/§5 | ❌ **False on 5 of 32 REITs.** §4 |
| *"weighted average is the true DPU denominator; without it DPU cannot be verified"* | dpu-brief §5 | ⚠️ **Overstated.** WAU improves the check from 48% to 70%, but 5 REITs stay structurally off. §3 |
| *"SET record sums to 13.609 vs dpu stored 20.000"* | dpu-brief §9 | ⚠️ **Misleading illustration.** Compares a EUR figure to an SGD one. The rounding bug is real; this example overstates it ~20×. §6 |
| *"only 2 of 12 REITs disclose retention, ~20% fill"* | dpu-brief §4 | ⚠️ **Undercounts.** At least 6, and there are two distinct kinds. §5 |

---

## 1. The rollforward — the strongest property in the table

```
distributable_income_opening
  + net_distributable_income
  + distribution_pool_other_movements
  − distribution_cash_paid
  = distributable_income_closing
```

Run against all 74 extracted rows, tolerance `max(1000, 0.5%)`:

```
pass 62    fail 0    rows missing a component 12
```

**62 of 62, zero failures.** The briefs claimed 12/12; the real coverage is five times larger and
still perfect. This is the backbone of the table — every figure is printed and audited, none derived.

Worked example, C38U FY2025 (p107):

```
249,796 + 869,957 − 750,125 − 9,083 = 360,545   ✓
```

### The cumulative trap (confirmed)

*"Amount available for distribution"* (C38U 1,119,753) is `opening + income`, **not** the year's
income. `net_distributable_income` must be the 869,957 subtotal.

**AJBU prints no subtotal at all** — it jumps 64,842 → 332,893. The year's income must be derived:

```
332,893 − 64,842 = 268,051
```

and that figure appears independently in the DPU note on p144 as *"Total amount available for
distribution for the year | 268,051"*. **Two independent paths, exact match.** The design survives a
report that refuses to print the number.

### Four structural archetypes — the rollforward is NOT universal

| archetype | REITs | shape |
|---|---|---|
| **Rollforward** | ~62 rows | opening → income → paid → closing |
| **No carry-forward** | CY6U, UD1U, XZL | build-up straight to "Income to be distributed"; **no opening/closing exists** |
| **Suspended** | D5IU, **BTOU** | distribution lines are dashes |
| **Stapled** | HMN, SET, Q5T, J85, XZL | "Stapled Securityholders"; some print REIT and Group columns side by side |

CapitaLand India (CY6U) has no pool:

```
Ordinary profit before tax              105,918
  ... adjustments ...
Income available for distribution       118,853
10% retention                           (11,885)
Income to be distributed                106,968
```

> **Gate implication:** `distributable_income_opening` / `_closing` are **legitimately null** for
> CY6U, UD1U and XZL. A hard universal rollforward gate fails those three forever, for no reason.
> Skip them explicitly rather than letting them sit as permanent red.

**BTOU is a second suspended REIT** alongside D5IU — no distribution declared for FY2025 or FY2024.
Its *"Income Available for Distribution per Unit 1.44 US cents"* is **not** a declared DPU and must
not be stored as one.

---

## 2. Two real data bugs — both the same fingerprint

Swept all 74 rows for `distribution_paid` disagreeing with `dpu × units` by more than 10%:

```
sym/fy      dpu      declared         cash    implied units   units_in_issue  ratio
AJBU/2025 10.381  133,531,000  133,531,000  1,286,301,898   2,440,733,452   0.53   declared==cash
C2PU/2025  15.29   65,436,000   65,436,000    427,965,991     652,487,000   0.66   declared==cash

2 rows out of 74.
```

**Exactly two rows are wrong, and both carry the identical signature** — `distribution_paid`
overwritten with the cash figure.

### FIX 1 — AJBU FY2025 `distribution_paid` → `268,051,000`

Currently `133,531,000`, which is the cash total from the distribution statement. Our own
`_notes.json` records that the cash line was *"deliberately NOT used"* for this field. The AR's DPU
note (p144) gives **268,051**. Cross-check: `5.133 + 5.248 = 10.381` — the second tranche was
declared 30 January 2026 for the period 1 Jul–31 Dec 2025, i.e. after year-end but in respect of
FY2025.

### FIX 2 — C2PU FY2025 `distribution_paid` → `99,781,000`

**Newly found in this pass.** Parkway Life's distribution statement:

```
Income for the year available for distribution to Unitholders     99,781   ← accrual, for the year
Distributions to Unitholders during the year                      65,436   ← cash
Number of units entitled to distribution ('000)                  652,487
Distribution per unit (cents)                                      15.29
```

```
15.29% × 652,487,000 = 99,765,000   ✓ ties to 99,781
```

We stored **65,436,000** — the cash line. Same error class as AJBU.

> **Detection rule, not a general one:** `distribution_paid == distribution_cash_paid` is *not*
> itself the bug — A17U FY2025 has both legitimately at 669,086 because no timing straddle fell that
> year. The tell is **equality PLUS the `dpu × units` ratio missing badly**.

---

## 3. The DPU identity — a bug detector, not a precision check

`dpu × units ≈ distribution_paid`, using weighted-average units verified against the ARs:

```
                       within 2%      within 5%
year-end units         14/29 (48%)    20/29 (69%)
weighted average       20/30 (67%)    24/30 (80%)
weighted avg + 2 fixes 21/30 (70%)    25/30 (83%)
```

**Adding `weighted_average_units` moves the check from 48% to 70%.** It is worth adding. An earlier
rough pass suggested it made no difference; that pass was polluted by the 5-year-summary trap (§7)
and was wrong.

But it does not close the gap, and the residual is structural:

```
AJBU    +89.7%   ← BUG
C2PU    +52.5%   ← BUG
──────────────── clean empty band ────────────────
AJBU    -11.4%   ← after fix: per-tranche denominators, genuinely irreducible
T82U     +8.2%
ODBU     +6.8%
BUOU     -5.8%
DHLU     -5.5%
AU8U     -4.9%
...remainder under 4%
```

**Both real bugs sit above 50%. Every structural quirk sits below 12%.** Nothing lands in between.

> **Gate recommendation: flag at 20%, not 2%.** At 20% it catches both bugs with zero false
> positives. At 2% it raises nine false alarms against REITs whose data is fine. Precision was never
> achievable here; catching corruption is, and this check is what found the C2PU bug.

### Why AJBU stays off even when fixed

AJBU's DPU is `5.133 + 5.248` — two tranches struck on two different unit bases, either side of a
large mid-year issuance. No single annual average reproduces it. This is correct behaviour by the
REIT, not an error in our data.

T82U is the same shape: FY2025 DPU `7.035 = 1.563 + 1.592 + 1.778 + 2.102`, with Q4 declared after
the reporting date. The `1.570` tranche visible in its statement is **Q4 2024, paid during 2025** —
the accrual/cash contamination that a `basis` tag is meant to make explicit.

---

## 4. Units — three concepts, not two

### `units_entitled_to_distribution` — the actual DPU denominator

Four REITs publish it outright:

```
O5RU   Number of Units entitled to distributions at end of the year ('000)    820,561
M1GU   Number of Units entitled to distributions ('000)                     1,125,055
UD1U   Number of Units entitled to distribution ('000)                       1,344,838
C2PU   Number of units entitled to distribution ('000)                         652,487
```

This is **neither** year-end units **nor** the weighted average. Where disclosed it reconciles DPU
essentially exactly (C2PU 0.02%). For the other 28 REITs the weighted average is the best available
proxy.

### WAU is universally disclosed

**32 of 32 FY2025 reports** state a weighted average number of units in the EPU note. Extractability
is not a constraint.

### The direction claim is false

Both briefs say year-end ≥ average always. It isn't:

```
WAU EXCEEDS year-end on 5 of 32:
  BTOU   1,835,124  vs  1,776,565   +3.30%
  SET      560,947  vs    556,884   +0.73%
  AU8U   1,751,413  vs  1,740,903   +0.60%
  DCRU   1,304,111  vs  1,304,010   +0.01%
  AW9U   2,111,058  vs  2,110,969   +0.00%
```

Two distinct causes:

- **SET repurchased securities** during 2025, so the average genuinely exceeds the closing count.
- **AU8U and DCRU state WAU on an issued-*and-issuable* basis** — AU8U's line reads *"Weighted
  average number of issued and issuable Units"*, DCRU's footnote says *"based on the weighted average
  number of units issued and issuable"* — while their year-end figure is issued-only.

> **Schema consequence:** `units_basis` cannot be a single row-level flag. The weighted-average
> column and the year-end column can sit on **different bases within the same report**. Each unit
> column needs its own basis tag.

Also: **7 REITs issued no units at all** during FY2025 (XZL, BMGU, CMOU, D5IU, M1GU, UD1U, 8C8U), so
WAU and year-end are identical and the ambiguity does not arise.

### The `units_to_be_issued` double-count (confirmed)

BUOU and TS0U bake "to be issued" into their headline; A17U, C38U and ME8U keep it separate; M44U has
no such concept. No flag distinguishes them. Materiality 0.1–0.4%. **Drop the column** — but note
that dropping it does not fix `number_of_shareholder_units` still meaning two different things.

---

## 5. Retention — two kinds, more common than reported

The dpu-brief found 2 of 12. The wider sweep finds at least 6, in **two distinct flavours**:

| REIT | evidence | kind |
|---|---|---|
| C38U | *"Amount retained for general corporate and working capital purposes"* (9,083) | discretionary |
| HMN | *"after retaining S$23.2 million"* (23,200) | discretionary |
| CY6U | *"10% retention"* (11,885) | **policy** |
| XZL | DPS *before* retention 0.944 / *after* 0.850 US cents | **policy** |
| CRPU | *"distribution per Unit would be 5.842 cents... without retention"* | **policy** |
| M1GU | *"at beginning of the year **after retention**"* | **policy** |
| OXMU | *"at end of the year **after retention**"* | **policy** |

A discretionary retention is a management decision this year. A policy retention is a permanent
feature of the trust. Publishing both as a bare `amount_retained` invites a stock reader to
misinterpret the second as a signal.

> **ADD `retention_basis`** → `policy` | `discretionary`.

Note M1GU and OXMU apply retention at the **opening** balance, not the closing — the column cannot
assume position in the statement.

**The hard rule stands unchanged:** populate only where the AR names it. Null means *not disclosed*,
never zero. **Never backfill from the rollforward residual** — K71U's ~108m gap looks exactly like
retention and is a timing artefact. Computing a plug there would publish a false claim that a REIT
withheld S$108m.

---

## 6. P0 — the rounding bug (STILL UNFIXED)

`scripts/db/build_final_tables.py:30`:

```python
return round(float(value) * tbl[ccy]['SGD'])     # no ndigits -> integer
```

Every per-unit figure in a foreign presentation currency is rounded to a whole number.

**Fix: `round(x, 6)`.**

### Correction to how this bug has been illustrated

The dpu-brief presents *"SET record sums to 13.609 vs dpu stored 20.000"* as the headline example.
That comparison is invalid — **13.609 is in EUR cents and 20.000 is in SGD cents.**

SET's actual DPS is **13.390 € cents**. At roughly 1.46 SGD/EUR that is ~**19.55 SGD cents**, which
the bug rounds to `20`. The real error is about 2%, not the ~47% the example implies.

**The bug is still real and still worth fixing** — these are genuinely destroyed:

```
CMOU FY2025   dpu stored 0     (record says 0.25)
BTOU          nav stored 0
MXNU          nav stored 1
```

A value rounded to `0` is not a rounding error, it is a deleted number. But the SET example should
not be quoted; use CMOU or BTOU instead.

---

## 7. Method note — the 5-year-summary trap

Many reports open with a five-year financial summary. **The column order is not consistent between
reports.** AW9U, O5RU, AU8U and A17U run oldest-first (leftmost = FY2021); CRPU, HMN and XZL run
newest-first (leftmost = FY2025).

Reading the leftmost column blind produced a wrong FY2025 figure for First REIT — 1,499,382 instead
of the true 2,111,058 — and that single error was enough to invert the conclusion of an earlier pass
on whether `weighted_average_units` is worth adding.

> **Rule: take units and DPU from the EPU/DPU note inside the audited financial statements, never
> from a summary table.** If a summary table must be used, prove which column is the current year by
> quoting its header.

---

## 8. Other findings worth recording

- **CY6U publishes three per-unit figures** — available `8.74`, declared `7.87`, paid `7.17`. We
  store 7.87, which is correct, but nothing in the schema records that a choice was made among three.
- **J91U completed a 10:1 unit consolidation in May 2025** and restated its FY2024 comparatives.
  Any cross-year unit or DPU comparison for J91U is meaningless unless this is flagged.
- **O5RU's financial year ends 31 March.** The folder is labelled FY2025 under the declared-FY
  convention, but the report's current column is headed *2026*. See the declared-FY note in the
  handoff.
- **Divestment gains are treated in opposite directions.** C38U adds *"Capital distributions"*
  (+16,208); SET strips *"Loss/(Gain) on divestments"* (+762); CY6U strips *"Gain on disposal group
  classified as held for sale"* (−4,081). A fair-value gain is not cash and cannot fund a
  distribution, so most REITs remove it — but C38U's line is a genuine return of capital. **These
  cannot share a column.** If the build-up is ever stored, it must be a labelled list with verbatim
  labels, classified later once ~30 reports have been seen.

---

## 9. Action list

### Mechanical — no decision needed

1. **P0** — `round(x, 6)` at `build_final_tables.py:30`; rebuild and re-promote. §6
2. **FIX 1** — AJBU FY2025 `distribution_paid` → `268,051,000`. §2
3. **FIX 2** — C2PU FY2025 `distribution_paid` → `99,781,000`. §2
4. Tag the prior-year cash tranches in `distribution_record` on AJBU and T82U as `basis = cash_paid`.
5. Backfill the incomplete records (C2PU FY2025, J91U FY2025).
6. Re-date M44U `number_of_unitholders` to the FY-end register.

### Needs a decision

7. ADD `weighted_average_units` — **recommend yes**, 32/32 disclosed, moves the check 48% → 70%.
8. ADD `retention_basis` (`policy` | `discretionary`) — recommend yes. §5
9. ADD `units_entitled_to_distribution` — 4 REITs disclose it; it is the true denominator. §4
10. `units_basis` **per unit column**, not per row. §4
11. DROP `adjusted_distributable_income`, `units_to_be_issued`, `ex_date`.
12. KEEP `distribution_cash_paid` — the rollforward closes on it, 62/62.
13. Flag J91U's unit consolidation and CY6U's three-figure ambiguity.

### Gates

14. Rollforward — **hard gate**, explicitly skipping CY6U, UD1U, XZL (no pool exists).
15. `dpu × units` vs `distribution_paid` — **soft flag at 20%**, never 2%. §3
16. `sum(distribution_record where basis = accrual) = dpu`.

---

## Verification note

Rollforward counts, fill rates and the bug sweep were computed directly against
`extracted/*/performance.json` — 74 rows, no sampling. Units figures came from four sub-agents
working in `parsed_reports_datalab/`, and **all 32 of their claims were re-verified mechanically**
against the cited line numbers before use (32/32 passed). One agent correctly overruled an incorrect
instruction in its own prompt: CRPU's DPU is in Singapore cents, not RMB (*"Based on FY2025
distribution per unit of 6.138 Singapore cents"*, line 1992).

The C2PU bug, the four `units_entitled_to_distribution` disclosures, the five WAU-exceeds-year-end
cases and the SET currency-mismatch correction were each verified by hand against the source
reports.

**Nothing in this pass was written to dev or prod.**
