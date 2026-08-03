# `sgx_reit_performance` — target schema (AGREED)

Agreed 2026-08-03. Companion to `transaction-target-schema-AGREED.md`.

**Design goal, in the user's words:** make the **flow of the DPU** clear and **API-ready**. Not
complex — solid.

**Headline: this is a subtraction, not an addition.** 28 columns → **26**. No new columns.

---

## 1. Why nothing is being added

The rollforward already closes on **62 of 62** rows using only columns prod has today:

```
distributable_income_opening
  + net_distributable_income
  + distribution_pool_other_movements
  − distribution_cash_paid
  = distributable_income_closing
```

Zero failures, across two currencies, stapled structures, and a report that prints no subtotal.

**The data was never missing.** What made prod unreadable is three separate things:

1. names that don't say what they mean (`distribution_paid` vs `distribution_cash_paid`)
2. one column carrying two dead concepts (`adjusted_distributable_income`, `units_to_be_issued`)
3. wrong values in a handful of cells (P0 rounding; 2 rows holding the cash figure)

None of those is fixed by adding a column. Adding columns makes them worse.

### Where the verification columns went

An earlier draft proposed adding `weighted_average_units`, `units_entitled_to_distribution`,
`units_basis`, `kpi_as_at_date` and `is_pro_forma`. **All are cut from prod.**

They answer *"is our DPU consistent with our unit count?"* — a question **we** ask before promoting,
never one an API consumer asks. They belong in the dev QC layer, not the published table.

| job | needs | lives in |
|---|---|---|
| show the flow | clear names, honest values | **prod / API** |
| prove the flow is right | weighted-average units, basis tags | **dev only** |

See `performance-verification.md` §3–4 for the evidence behind each; they remain valid findings, just
not published columns.

---

## 2. The target — the distribution flow

```
distributable_income_opening      pool left over from last year
  + income_for_year               what the pool earned this year
  + pool_adjustments              negative = retained · positive = added
  − distribution_paid             cash that actually left the bank
  = distributable_income_closing  carried into next year

  distribution_declared           promised for the year — ties to DPU
  distribution_per_unit           the headline, in cents
  distribution_record             the tranches that make it up
```

### Renames — 4

| now | becomes | why |
|---|---|---|
| `net_distributable_income` | `income_for_year` | kills the cumulative trap. The AR's *"**Amount** available for distribution"* is opening+income; this column must be the **for-the-year subtotal** |
| `distribution_pool_other_movements` | `pool_adjustments` | shorter, honest, sign-carrying |
| `distribution_paid` | `distribution_declared` | it is the declared-for-year figure, the only one that ties to DPU |
| `distribution_cash_paid` | `distribution_paid` | matches the AR line *"Distributions to Unitholders **during the year**"* |

> The last two swap roles deliberately. Today the shorter name (`distribution_paid`) holds the
> *declared* figure and the longer one holds cash — the opposite of what a reader assumes, and the
> direct cause of the two data bugs in §4. After the rename, `distribution_paid` means paid.

Renames are cheap: dev→prod already renames `dpu` → `distribution_per_unit`, `nav_per_unit` →
`net_asset_value_per_unit`, `wale` → `weighted_average_lease_expiry` in `build_final_tables.py`.
One line each, no migration.

### Drops — 2

| column | evidence |
|---|---|
| `adjusted_distributable_income` | 4% fill (3 of 74). **NOT_FOUND in all six ARs checked.** No REIT publishes a second distributable-income figure. The 3 populated rows contradict each other — sometimes above, sometimes below `net_distributable_income` |
| `units_to_be_issued` | 0.1–0.4% materiality. **Double-counts** — BUOU's and TS0U's headline unit figure is literally *"Units in issue and to be issued"*, so the component is already inside it, with no flag distinguishing them from A17U/C38U/ME8U which keep it separate |

> **Conflict resolved.** `performance-normalization.md` N3 proposed *splitting*
> `adjusted_distributable_income` into two columns. Overruled: a column absent from every annual
> report cannot be split into two that are also absent. Drop stands.

### Restructure — 1

`distribution_record` jsonb. Today `period` is free text in at least three formats
(`'2025-01-01 to 2025-06-30'`, `'1 October 2024 to 31 March 2025'`, `'2H 2025 (1 Jul - 31 Dec 2025)'`)
which alone makes it unusable from an API.

```jsonc
{
  "period_start": "2025-01-01",   // real dates, was free text
  "period_end":   "2025-06-30",
  "dpu":          5.133,
  "basis":        "accrual",      // accrual | cash_paid  — NEW
  "pay_date":     "2025-09-12"
  //  ex_date dropped — null on every row sampled
}
```

`basis` is what stops the tally failing. Some rows carry a **prior-year tranche paid in cash this
year** — AJBU's `0.819¢` for Nov–Dec 2024, T82U's `1.570¢` for Q4 2024. In both the headline DPU is
**correct**; the array is contaminated because it serves the cash view and the accrual view at once.
Tagging each entry makes `sum(record where basis = accrual) = dpu` enforceable.

A normal payment lag is **not** a defect: HMN's 2H tranche pays 2026-02-27 for an in-year period.

---

## 3. `pool_adjustments` — the sign convention

**One column, signed.** Verified across the 24 populated rows in `extracted/`:

```
17 negative = retained            7 positive = added
CMOU/2024   -47,627,000           BUOU/2024   +45,178,000
OXMU/2024   -34,237,000           Q5T/2024    +16,121,000
HMN/2025    -23,200,000           ME8U/2024   +13,354,000
C38U/2025    -9,083,000           AU8U/2025    +5,700,000
CRPU/2024    -7,385,000           ME8U/2023    +5,391,000
...                               J85/2024     +4,062,000
```

Fill is **32% (24 of 74)**, not the ~20% the briefs estimated.

> **The name must stay neutral.** Positives are 29% of populated rows — calling this column
> `amount_retained` would mislabel nearly a third of them.

### Accepted cost

**J85 nets two movements into one figure.** Its `+4,062,000` is a retention of `−6,261` *plus* a
capital distribution of `+10,323`. A single signed number cannot show both.

Option B (split into `amount_retained` + `other_additions`) was considered and **rejected**: it buys
one row's worth of precision at the cost of a permanent extra column that is null on 68% of rows.
Split later if the frontend ever needs it — the underlying values are page-cited and recoverable.

### The standing rule — unchanged

Populate **only** where the annual report names it. **Null means "not disclosed", never zero.**

> **Never backfill from the rollforward residual.** K71U shows a ~108m gap that looks exactly like
> retention and is a cumulative-vs-headline timing artefact. Computing a plug there would publish
> *"this REIT held back S$108m"* — false, and the kind of false that gets quoted. A gap that does not
> tally is a signal to read the source, not a licence to compute a balancing figure.

---

## 4. Value fixes (no schema change)

| # | fix | detail |
|---|---|---|
| 1 | **P0 rounding** | `build_final_tables.py:30` — `round(float(value) * tbl[ccy]['SGD'])` has no ndigits, so every per-unit figure in a foreign presentation currency integer-rounds. Prod serves `CMOU dpu 0`, `BTOU nav 0`, `MXNU nav 1` **right now**. Fix: `round(x, 6)` |
| 2 | **AJBU FY2025** | `distribution_declared` → `268,051,000` (holds `133,531,000`, the cash figure). AR p144: *"Total amount available for distribution for the year 268,051"*. Cross-checks: `332,893 − 64,842 = 268,051`, and `5.133 + 5.248 = 10.381` DPU |
| 3 | **C2PU FY2025** | `distribution_declared` → `99,781,000` (holds `65,436,000`, the cash figure). AR: *"Income for the year available for distribution to Unitholders 99,781"*. Ties: `15.29% × 652,487,000 = 99,765,000` |
| 4 | **Re-promote** | `pool_adjustments` — dev/`extracted` has all 24 values including the 8 that `performance-normalization.md` §2 recorded as null in prod. **This is a promotion gap, not an extraction gap** — same shape as the 61 stale `gain_loss_pct` rows. Re-promote, do not re-extract |
| 5 | `distribution_record` | tag AJBU's and T82U's prior-year tranches `basis = cash_paid`; backfill the incomplete records (C2PU FY2025, J91U FY2025) |

> Fixes 2 and 3 are the **only two** rows in all 74 where `distribution_declared` disagrees with
> `dpu × units` by more than 10%. Both share one fingerprint: the declared field overwritten with the
> cash value. **Equality alone is not the bug** — A17U FY2025 legitimately has both at `669,086`
> because no timing straddle fell that year. The tell is equality **plus** a large ratio miss.

---

## 5. Percentage normalisation

Convert to fraction (0–1): `aggregate_leverage`, `portfolio_occupancy`, `cost_of_debt`. Add them to
`FRACTION_FIELDS` in `promote_final_to_prod.py:57`.

**Do NOT convert:**

- `interest_coverage_ratio` — a **multiple** (×), never a percentage. Confirmed across 7 REITs, zero
  exceptions. Rendered with a `%` sign, a 2.6× REIT reads as one about to default.
- `weighted_average_lease_expiry`, `weighted_average_debt_maturity` — **years**
- `distribution_per_unit` — **cents** · `net_asset_value_per_unit` — **dollars**

Note `performance.portfolio_occupancy` (percent) and `property.occupancy_rate` (already a fraction)
are the same concept stored two ways — they must end on one convention.

---

## 6. The API shape

```json
"distribution": {
  "opening":            249796000,
  "income_for_year":    869957000,
  "pool_adjustments":    -9083000,
  "paid":              -750125000,
  "closing":            360545000,

  "declared":           860874000,
  "dpu_cents":              11.58,
  "unpaid_at_year_end": 110749000
}
```

Reads top to bottom as the story, and it adds up.

`unpaid_at_year_end` = `declared − paid`. **Computed at read time, never stored** — it is a
subtraction, and storing it creates a fourth number that can drift out of agreement with the other
three.

---

## 7. Gates

| # | check | severity |
|---|---|---|
| 1 | `opening + income_for_year + pool_adjustments − paid = closing` | **hard gate** — but **skip CY6U, UD1U, XZL**: they have no pool carry-forward in any year, so opening/closing are legitimately null, not missing |
| 2 | `sum(distribution_record where basis = accrual) = distribution_per_unit` | hard, once `basis` exists |
| 3 | `distribution_declared ≈ dpu × units` | **soft flag at 20%, never 2%** |
| 4 | payout ratio `declared / income_for_year` in 0–1.3 | already passes 74/74 |

### Why gate 3 is 20% and not 2%

```
AJBU    +89.7%   ← BUG
C2PU    +52.5%   ← BUG
──────────── clean empty band ────────────
AJBU    -11.4%   ← after fix; per-tranche denominators, irreducible
T82U     +8.2%
ODBU     +6.8%
...remainder under 6%
```

Both real bugs sit above 50%; every structural quirk sits below 12%; nothing lands between. At 20%
the gate catches both bugs with **zero false positives**. At 2% it raises nine false alarms against
REITs whose data is fine. Precision was never achievable — DPU is struck per tranche on different
unit bases — but catching corruption is, and this check is what surfaced the C2PU bug.

---

## 8. Final column list — 26

```
symbol · financial_year · date · source_url · properties_location

number_of_unitholders · number_of_shareholder_units

distribution_per_unit · distribution_record · distribution_period_months

distributable_income_opening · income_for_year · pool_adjustments
distribution_paid · distributable_income_closing · distribution_declared

portfolio_value · gross_revenue · net_property_income

aggregate_leverage · interest_coverage_ratio · cost_of_debt
weighted_average_debt_maturity · weighted_average_lease_expiry
portfolio_occupancy · net_asset_value_per_unit
```

```
28 today  −2 dropped  +0 added  =  26
          4 renamed · 1 restructured · 5 value fixes
```

---

## 9. Known limits — carried forward, not solved here

- **`portfolio_value` is not one concept.** J69U changes basis between years; C38U/TS0U/ME8U publish
  proportionate AUM. **It must not be used as a reconciliation target.** A `portfolio_value_basis`
  tag was proposed and deferred — revisit if the frontend surfaces the number.
- **`number_of_shareholder_units` still means two things** — issued-only at C38U/K71U,
  issued-and-issuable at BUOU/TS0U. Dropping `units_to_be_issued` does not fix this; it needs one
  convention chosen. Not blocking the flow, so deferred.
- **KPI basis divergence** — WALE is GRI-weighted at C38U and NLA-weighted at BTOU; BTOU carries two
  ICRs and two costs of debt under one label each. See `performance-normalization.md` §6 and its N4
  tag proposal. Out of scope for the distribution flow.
- **Currency (N1)** — `performance-normalization.md` proposes store-native + convert-at-read, because
  converting a *balance* at a *period* rate makes a pool that never moved appear to move. All 6
  cross-year breaks tally perfectly in native currency. **That is a larger decision than this
  document and is deliberately not folded in.**

---

## 10. Provenance

Rollforward counts and fill rates computed directly against all 74 rows of
`extracted/*/performance.json`. Annual-report figures verified against `parsed_reports_datalab/`;
units figures came from four sub-agents whose 32 claims were each re-checked mechanically against
cited line numbers (32/32 passed). Evidence in `performance-verification.md`; FX, property-currency
and KPI analysis in `performance-normalization.md`.

**Nothing in this document has been applied to dev or prod.**
