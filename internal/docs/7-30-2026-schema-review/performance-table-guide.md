# `sgx_reit_performance` — how the columns work together

One row per REIT per financial year. 74 rows: FY2023 ×3, FY2024 ×36, FY2025 ×35.
Keyed on `(symbol, financial_year)`.

---

## Conventions

| kind | convention |
|---|---|
| money | **SGD**, converted from the reporting currency at the MAS quarterly rate nearest FY end |
| percentages | **0–1** (`0.39` = 39%) |
| ratios | a multiple, as printed (`interest_coverage_ratio` 3.6 = 3.6×) |
| durations | years (`weighted_average_lease_expiry`, `weighted_average_debt_maturity`) |
| `distribution_per_unit` | **cents** |
| `net_asset_value_per_unit` | **dollars** |

Percentages are normalised once, in `build_final_tables.py` `pct01()`. Promotion to prod is a
pass-through — no layer re-scales anything.

> **⚠ DPU and NAV are in different units.** DPU is cents (`15.005`), NAV is dollars (`2.29`).
> Any per-unit arithmetic mixing them needs `dpu / 100`.

---

## Columns

### Identity

| column | meaning |
|---|---|
| `symbol` | ticker, `.SI` stripped in prod |
| `financial_year` | the **declared** FY. Six REITs have non-December year ends (M44U, ME8U, N2IU, O5RU, P40U, JYEU); J69U ends 30 September |
| `date` | the FY end date — the anchor for every FX conversion |
| `source_url` | the annual report PDF this row was extracted from |

### Scale

| column | meaning | fill |
|---|---|---|
| `portfolio_value` | total portfolio value | 74 |
| `units_in_issue` | units outstanding at FY end (was `number_of_shareholder_units`) | 74 |
| `units_to_be_issued` | units pending issue — manager fees settled in units, DRP allotments | 41 |
| `number_of_unitholders` | count of **holders**, not units | 74 |
| `properties_location` | countries the portfolio spans | 74 |

`units_to_be_issued` is null on 33 rows and that is correct — a REIT with nothing pending has
no figure to report. Null means "none outstanding", not "missing".

### Earnings

| column | meaning | fill |
|---|---|---|
| `gross_revenue` | total revenue | 74 |
| `net_property_income` | revenue less property expenses | 74 |
| `income_for_year` | income available for distribution (was `net_distributable_income`) | 74 |

### Capital and portfolio metrics

| column | unit | fill |
|---|---|---|
| `aggregate_leverage` | 0–1 | 74 |
| `cost_of_debt` | 0–1 | 73 |
| `interest_coverage_ratio` | multiple | 74 |
| `weighted_average_debt_maturity` | years | 66 |
| `weighted_average_lease_expiry` | years | 66 |
| `portfolio_occupancy` | 0–1 | 70 |
| `net_asset_value_per_unit` | dollars | 74 |

### Distribution

| column | meaning | fill |
|---|---|---|
| `distribution_per_unit` | DPU for the year, **cents** | 74 |
| `distribution_declared` | total declared **for** the year | 50 |
| `distribution_paid` | cash actually paid **during** the year | 74 |
| `distributable_income_opening` | pool carried in from last year | 63 |
| `other_additions` | additions to the pool beyond `income_for_year`, split economically (operating vs asset sales) | 20 |
| `amount_retained` | income withheld rather than distributed | 28 |
| `distributable_income_closing` | pool carried out to next year | 65 |
| `distribution_record` | per-tranche breakdown: `dpu`, `period_start`, `period_end` | 74 |

**`declared` ≠ `paid`.** Declared is what the year earned the right to; paid is cash that moved
during the year, which includes last year's final distribution and excludes this year's.

---

## How they fit together

### 0. Where opening and closing come from

Both are **read verbatim from the audited Distribution Statement**, one page-cited line each --
never computed. The extraction spec is explicit that `A + B - P = E` is a **guard, not a
formula**: *"A broken guard = a mis-read line -> fix at the source, never plug."*

That is why 11 rows have no opening or closing: those reports do not present a distribution
rollforward at all. CY6U is the clearest case -- CapitaLand India Trust is a registered
**business trust, not a REIT**, and its statements carry no *"income available for distribution
at the beginning/end of the year"* line. Same for D5IU, XZL, UD1U, 8C8U and J91U. The value is
absent because the disclosure is absent, not because extraction failed.

Note `distribution_basis` (raw only) also has 11 rows marked `not_disclosed_rollforward_only`
-- a **different** 11. Do not confuse the two sets.

### 1. The distribution rollforward

```
distributable_income_opening
  + income_for_year
  + other_additions
  − distribution_paid
  − amount_retained
  = distributable_income_closing
```

A17U FY2025:

```
338,376,000 + 597,294,000 + 80,974,000 − 669,086,000 − 0 = 347,558,000   ✅
```

And `closing` of one year is `opening` of the next, so the pool is traceable across years.

### 2. The DPU bridge

```
distribution_per_unit / 100 × units_in_issue  ≈  distribution_declared
```

It reconciles against **declared**, not paid — 44 of 45 rows within 10%, 39 within 5%, versus
52 of 67 against paid. It is approximate because DPU is declared per tranche against the unit
count at each record date, while `units_in_issue` is the year-end count.

**The one row outside 10% is AJBU FY2024, and it is correct data, not an error.** Keppel DC
REIT raised roughly $1.1bn of equity in Q4 2024 -- a private placement plus a preferential
offering whose **148,413,063 new units listed on 18 December 2024**, thirteen days before year
end. Those units earned almost none of the year's DPU, so multiplying by the year-end count
overstates the implied distribution by 21%. The AR says as much: *"Excluding the impact of the
148,413,063 new Units listed on 18 December 2024 ... the adjusted DPU would have been 9.504
cents."*

The correct denominator is **weighted-average units**, which this table does not store. Treat
G4 as an order-of-magnitude sanity check, and expect any REIT that raised equity mid-year to
miss it.

### 3. `distribution_record` sums to DPU

```
sum(distribution_record[].dpu) = distribution_per_unit
```

66 of 74 rows tally. The record holds only `dpu`, `period_start`, `period_end` — provenance
keys (`line`), `amount` and `pay_date` were dropped as derivable or sparse.

The 5 that do not tally are all **semi-annual payers with only one half captured**, and
`period_start`/`period_end` make it self-evident:

**DCRU FY2024 and FY2025 are fixed** -- both ARs disclose the missing half outright
(*"Announced results for First Half FY 2024: Declared DPU of 1.80 U.S. cents"*, and
*"Delivered DPU of 1.80 U.S. cents for 1H 2025"*), so the tranche was added with that
quote in its `source`. Both now sum to 3.60 US cents = the headline.

**Three cannot be fixed from the annual report, because the figure is not in it:**

```
A17U 2025   has H1 (6.479 + 0.998)   missing H2 Jul-Dec 2025   7.477 of 15.005
XZL  2024   has H2 (0.848)           missing H1 Jan-Jun 2024   1.154 of 2.170
XZL  2025   has H2 (0.418)           missing H1 Jan-Jun 2025   0.537 of 1.091
```

A REIT's annual report prints the full-year DPU plus whichever tranche falls out as a
subsequent event; the other half was announced in the interim results release, which is not
in our corpus. A17U's Note 24(c) computes DPU from the full-year amount (678,268), never from
summing tranches, so the AR has no reason to print the H2 figure.

Subtracting (headline - captured) would produce a number no report states -- that is the
"never balance by assumption" rule, so those three stay short. The precedent for a legitimate
fill is A17U **FY2024**, whose H2 was taken from the **FY2025** AR and carries
`source: "cross-year: disclosed in the FY2025 AR, not the FY2024 AR"`. The same trick will
close A17U FY2025 once the FY2026 report exists.

The gap is machine-detectable: the tranche periods should span the full financial year.

### 4. Zero vs null

They mean different things and must not be collapsed:

- **`0`** — the REIT declared or paid nothing. BTOU (Manulife US REIT) and D5IU (Landmark)
  both suspended distributions; D5IU's AR says *"retaining its cash flow and suspending
  distributions"*. Their rollforwards still close exactly.
- **`null`** — the report does not publish that line. 24 rows have a null
  `distribution_declared` with a positive `distribution_paid`, because those ARs print only
  what was paid.

Defaulting null to 0 would make a suspension indistinguishable from a formatting choice.

---

## Gates

| # | check | result |
|---|---|---|
| G1 | rollforward closes | **62** tally · 11 inputs null · 1 mismatch |
| G2 | `sum(record.dpu)` = `distribution_per_unit` | **66** tally · 3 mismatch · 5 empty record |
| G3 | `net_property_income ≤ gross_revenue` | **0** violations |
| G4 | `dpu/100 × units` ≈ `distribution_declared` | **44 / 45** within 10% |
| G5 | percentages within 0–1 | leverage 0.221–0.608 · cost of debt 0.0148–0.0854 · occupancy 0.677–1.0 |

G2's 5 empty records are the suspended trusts — an empty list is meaningful and is preserved
as `[]`, distinct from `null`.

---

## Known gaps

| what | detail |
|---|---|
| **G1: 11 rows unreconcilable** | `distributable_income_opening` or `_closing` is null, so the rollforward cannot be tested at all |
| **G1: C2PU FY2025 off by 36,000** | `15,562 + 102,781 − 65,436 − 3,000 = 49,907` vs closing `49,871`. FY2024 tallies exactly. Its `income_for_year_basis` is `pre_retention_normalised` — a computed, not printed, figure — so the gap is in our derivation. Not adjusted: a failed check is a signal to investigate, never licence to force a balance |
| **G2: 3 records cover half a year** | A17U FY2025 (missing H2), XZL FY2024/25 (missing H1). The other half is announced in the interim results release, not the AR, so it cannot be extracted from our corpus. DCRU's two were fixed -- its AR states the H1 DPU. See §3 |
| **G1: the 11 unreconcilable rows** | the report publishes no distribution rollforward at all; CY6U and J91U are business trusts, not REITs. Absent disclosure, not failed extraction. See §0 |
| **G4: AJBU FY2024** | equity raised 13 days before year end, so the year-end unit count is the wrong denominator. See §2 |
| **`portfolio_occupancy` null ×4** | 8C8U FY2025, Q5T FY2024/25, UD1U FY2024 |
| **`portfolio_value` is not comparable across REITs** | ME8U's is AUM-style, DCRU's is explicitly at-share AUM, others are the audited portfolio statement. Do **not** use it as a reconciliation target |
| **DPU cents vs NAV dollars** | inconsistent units in one table |

---

## Not in this table

`distribution_period_months` — dropped. `adjusted_distributable_income` — dropped without
replacement. `distribution_cash_paid` → `distribution_paid`,
`distribution_pool_other_movements` → `other_additions`,
`net_distributable_income` → `income_for_year`,
`number_of_shareholder_units` → `units_in_issue`.

`paid_in_units` (DRP settlement) and `income_for_year_basis` (which of the 5 values were
computed rather than printed) exist in **raw only** — audit trail, not investor-facing.
