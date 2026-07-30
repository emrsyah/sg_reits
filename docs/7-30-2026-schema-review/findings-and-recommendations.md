# Schema review — findings & recommendations

**Companion to `meeting-recap-tracker.md`.** One section per tracker item: what the prod data
actually shows, and what I recommend. Everything here was measured against **prod**
(`SUPABASE_URL` / `SUPABASE_KEY`) on 2026-07-30 and cross-checked against the parsed annual
reports in `parsed_reports_datalab/`.

Verdict tags: ✅ agree · ⚠️ agree with a caveat · ❌ recommend against · 📋 answer to a question

Row counts: profile 37 · performance 74 · property 3,420 · top_tenant 752 · trade_mix 509 ·
property_transaction 206.

---

# sgx_reit_property

## Area fields — null counts 📋

| column | filled | null | % filled |
|---|---|---|---|
| `gross_lettable_area` | **9** | 3,411 | **0.3%** |
| `net_lettable_area` | 2,397 | 1,023 | 70.1% |
| `gross_floor_area` | 1,249 | 2,171 | 36.5% |

**No row has all three.** Combinations: NLA only 1,476 · NLA+GFA 921 · none 686 (20%) ·
GFA only 328 · GLA only 9.

**Recommendation: drop `gross_lettable_area`.** All 9 rows are a labelling stray, not a
convention — UD1U FY2025 (7 rows) and P40U FY2024 (2 rows), and in every case NLA and GFA are
both null:

```
UD1U 2025  Berlin Campus         GLA=79,097  NLA=None  GFA=None
P40U 2024  David Jones Building  GLA=24,071  NLA=None  GFA=None
```

P40U reports NLA on its other 6 properties, so it is inconsistent *within one REIT*. Fold the 9
into `net_lettable_area` (same concept for these assets), then drop the column.

The 686 rows with no area at all are a coverage gap, not a schema question — separate decision.

## `effective_date` / `lease_term_years` / `lease_expiry_date` — which to drop ✅

| column | filled | null |
|---|---|---|
| `effective_date` | 238 | 3,182 (7% filled) |
| `lease_term_years` | 1,346 | 2,074 |
| `lease_expiry_date` | 691 | 2,729 |

**Recommendation: drop `effective_date`, keep `lease_expiry_date` + `lease_term_years`.**

1. **Coverage** — 691 vs 238; expiry is ~3× better populated.
2. **Tenure explains the nulls, correctly.** `effective_date` is set on 237 Leasehold rows and
   exactly **1** Freehold row. A freehold has no lease start, so the nulls are structural rather
   than missing. Same pattern for expiry (663 Leasehold / 28 Freehold).
3. **Relevance** — lease-expiry risk is a screening dimension; lease commencement is not.

Before dropping: 145 rows have `effective_date` but no expiry. Derive
`lease_expiry_date = effective_date + lease_term_years` for those first so the information
survives.

⚠️ **Separate QC item this surfaced:** 28 rows are `land_tenure = 'Freehold'` *with* a
`lease_expiry_date`. Either head-lease/building-lease structures (legitimate — needs a flag) or
mis-tagged tenure. Independent of this decision.

---

# sgx_reit_top_tenant / sgx_reit_trade_mix

## `pct_basis` — unique values 📋

**13 distinct in `top_tenant`, 12 in `trade_mix`:**

| value | top_tenant | trade_mix |
|---|---|---|
| `gri` | 395 | 305 |
| `rental_income` | 105 | 50 |
| `gross_revenue` | 90 | 41 |
| `cash_rental_income` | 40 | 22 |
| `npi` | 20 | — |
| `committed_gross_rent` | 20 | 16 |
| `headline_rent` | 20 | 20 |
| `gri_commercial` | 10 | 11 |
| `office_gri` | 10 | 10 |
| `retail_gri` | 10 | 7 |
| `gri_logistics_industrial` | 10 | 5 |
| `asset_value` | — | 2 |
| `rental_income (corporate accounts of properties under Ascott management contracts only)` | 11 | 20 |
| `apartment_rental_income (corporate accounts of properties under Ascott management contracts only)` | 11 | — |

**Recommendation — three cleanups:**

1. **Two values are prose in an enum field** (the Ascott ones, 42 rows). Split into
   `pct_basis = 'rental_income'` / `'apartment_rental_income'` plus a separate `pct_basis_note`
   text column for the qualifier.
2. **Four values are `gri` with a segment qualifier** — `gri_commercial`, `office_gri`,
   `retail_gri`, `gri_logistics_industrial` (63 rows). Collapse to `gri`; move the segment to its
   own column or drop it (the segment is largely implied by the REIT).
3. **Resulting canonical enum (9 values):** `gri` · `rental_income` · `apartment_rental_income` ·
   `gross_revenue` · `cash_rental_income` · `npi` · `committed_gross_rent` · `headline_rent` ·
   `asset_value`.

The column has to survive in some form: a tenant at "8% of GRI" and one at "8% of asset_value"
are not comparable, and **~47% of rows are on a basis other than `gri`**.

---

# sgx_property_transaction

## Remove all status ≠ "completed" ⚠️

`status`: completed **176** · announced **29** · terminated **1**. Filtering drops 30 rows (14.6%).

**Recommendation: keep the rows, filter in the endpoint/view instead.** Announced-but-not-completed
deals are forward-looking information — often the most interesting rows for an investor. Filtering
at the view costs nothing and keeps the option open.

Either way, this fixes `transaction_type`, which currently **duplicates status**:
`announced_divestment` (19), `announced_acquisition` (1), `divestment_terminated` (1). Completed
rows only ever carry `divestment` / `acquisition` / `partial_divestment`.

## `transaction_type` + `transaction_price` (drop `purchase_price` / `sale_price`) ✅

Near-mutually-exclusive by design, and the merge **fixes a real bug**:

```
acquisition            pp=True  sp=False    44
acquisition            pp=True  sp=True     12   <- BUG: same number in both
divestment             pp=False sp=True    107
partial_divestment     pp=False sp=True      4
```

**12 acquisitions have the identical value written into both columns** — ME8U Osaka Data Centre
(475,072,000 in both), HMN ibis Styles Tokyo Ginza, A17U Summerville Logistics Center, AJBU Keppel
DC Singapore 7 & 8. A single `transaction_price` keyed off `transaction_type` eliminates that class
of error permanently.

31 rows have neither price (mostly the announced ones).

## `interest_pct` ❌ recommend keep

18 filled. **4 are `1`** (=100%, redundant), so **14 rows carry a genuine partial stake**: 0.9847,
0.9949, 0.0051, 0.10, 0.10, 0.55, 0.45, 0.20, 0.75, 0.3333, 0.151, 0.249, 0.199.

Without it, a price for **10% of a building** is indistinguishable from buying the building — a
factual misreading of 14 transactions, including all 4 `partial_divestment` rows and the JV stake
sales. 18 non-null values is cheap to keep and expensive to lose.

Suggest renaming to `interest_transacted_pct` and setting the 4 redundant `1`s to NULL, so
non-null always means "partial".

## Drop `announced_date` and `transaction_date` ✅ zero loss on completed rows

```
transaction_date == completed_date   174
transaction_date only                 19   (the announced/terminated rows)
completed_date only                    0
they differ                            0   <- never
```

`completed_date` is a strict subset of `transaction_date` and they **never disagree**. The 19
`transaction_date`-only rows are exactly the non-completed ones. Keep `completed_date`, drop the
other two.

Loose end: 176 rows are `completed` but only 174 have a `completed_date` — 2 need a backfill.

## `gain_basis` — necessary *today*, unnecessary *after* the derivation change 📋

Values: `vs_valuation` 111 · `vs_book_value` 28 · `vs_cost` 1 · null 66.

While `gain_on_divestment` is a **stored, as-disclosed** figure, `gain_basis` is mandatory — a gain
vs. valuation and a gain vs. book value are different numbers, and comparing them across REITs
without the basis is meaningless.

If the gain is instead **derived on one consistent basis**, every row shares that basis by
construction and **both `gain_basis` and the stored `gain_on_divestment` can go.** Pick one — do
not drop `gain_basis` while keeping as-disclosed gains.

## Drop `valuation`, keep `valuation_date` + `carrying_value` ❌

| field | filled |
|---|---|
| `valuation` | **162** |
| `carrying_value` | 100 |
| both | 89 |
| either | 173 |

1. **It reduces what can be computed.** Across the 117 divestment rows, gain is derivable vs
   *valuation* on **85** rows but vs *carrying_value* on only **68**. Dropping the better-populated
   field costs 17 rows on the exact metric being derived.
2. **`valuation_date` without `valuation` is incoherent** — it is the date *of* that valuation.
   3 rows are already in that broken state.
3. *"Sold at a 5% premium to valuation"* is the headline the ARs print, and it needs `valuation`.

**Recommendation: keep both.** They answer different questions — `carrying_value` → accounting
gain; `valuation` → premium/discount to last independent valuation. Rename `valuation` →
`independent_valuation`, kept paired with `valuation_date`.

## Where `gain_on_divestment` should be derived from — Option B ✅ / Option A ❌

**Option A — `transaction_price − sgx_reit_property.purchase_price`: not viable.** Tested the join
on `(symbol, property_name)`:

```
divestment rows matched to a property row WITH purchase_price:  39
unmatched:                                                      78   (67%)
```

It fails structurally: a property divested during the year is **removed from the property table**,
so the row holding its purchase price is often gone. Unmatched examples: ME8U 'Tanglin Halt
Cluster', M44U 'Century', 'Chee Wah', 'Subang 1', HMN 'Somerset Olympic Tower Tianjin'. A 33%
match rate cannot back a displayed metric.

**Option B — `transaction_price − carrying_value`: use this.** It is the accounting gain the AR
itself reports, derivable on 68 of 117 divestments, and needs no cross-table join.

**Recommendation: derive two metrics, not one:**

- `gain_vs_book = transaction_price − carrying_value` (68 rows) — the accounting gain
- `premium_to_valuation_pct = transaction_price / independent_valuation − 1` (85 rows) — the AR headline

Option A remains worth having as a separate *total uplift since acquisition* metric, but only once
property-level purchase prices survive divestment — a different fix (Phase-2 purchase_price
recovery).

---

# sgx_reit_performance

## `number_of_shareholder_units` should never be NULL ✅

4 nulls, every one disclosed in the AR:

| row | prod | AR discloses |
|---|---|---|
| AW9U 2024 | NULL | 2,094,447k (Note 16) |
| CMOU 2024 | NULL | 1,044,450k (Note 13) |
| J91U 2024 | NULL | 8,049,164k (Note 18) |
| TS0U 2024 | NULL | 5,492,950k (Note 15) |

All FY2024, all extraction misses. Add `number_of_unitholders` to the same pass — null on
AJBU 2024 and UD1U 2024.

**Why J91U's matters more than it looks:** its DPU goes 2.119 (FY2024) → 21.914 (FY2025), a 10.3×
jump that reads as a data error until you see units fall 8,049,164k → 805,035k — ESR-REIT's
**10-into-1 unit consolidation**. Both DPU figures are correct, but without the FY2024 unit count
the series is unexplainable.

## `distribution_record`: `period_start` / `period_end`, remove `ex_date` + `pay_date` ✅ / ⚠️

**Structure: agreed.** `period` is currently free text with **123 distinct formats** across 170
entries, and the inconsistency is **ours, not the reports'** — AJBU's AR prints
`1/1/2025 to 30/6/2025`; we stored `2025-01-01 to 2025-06-30`. Fully parseable, lossless.

- **`ex_date`: zero loss.** 0 of 170 entries, and it appears in no AR — it is an SGX-announcement
  field, not an annual-report field. Drop it.
- **`pay_date`: ⚠️ 27 of 170 are real data**, sourced from the AR's Financial Calendar (verified
  AJBU p198: *"Distribution for 1 January 2025 to 30 June 2025 — 15 September 2025"*). Sparse only
  because not every REIT publishes that calendar. Dropping at 16% coverage is defensible — just
  noting it is real data being discarded, not noise.

**Three defects must be fixed in the same pass or the new structure inherits them:**

1. **Key drift** — 162 entries use `pay_date`, **2 use `payment_date`**, 6 have neither.
2. **`dpu` is in native currency while `distribution_per_unit` is FX-converted to SG cents** — two
   DPU representations in one row, different units, no tag (DCRU: record 3.6 US¢, column 5.0).
   This is why `sum(record.dpu) ≠ distribution_per_unit` on **24 of 63** comparable rows.
3. **K71U FY2025 has 5 entries where the AR supports 3** — cash-basis tranches and declared
   half-years concatenated, one duplicate, one null `dpu`:

```
{dpu: null, period: "1/7/2024 to 31/12/2024"}   <- AR says 2.80c
{dpu: 2.72, period: "1/1/2025 to 30/6/2025"}    <- cash basis
{dpu: 1.63, period: "1/7/2025 to 16/10/2025"}   <- cash basis
{dpu: 2.72, period: "1H 2025"}                  <- DUPLICATE of row 2, declared basis
{dpu: 2.51, period: "2H 2025"}                  <- declared basis (2.72+2.51 = 5.23 = FY DPU)
```

12 rows have a duplicated DPU value; some are legitimate (two half-years paying the same rate,
e.g. DCRU 1.8 + 1.8), so this cannot be auto-deduped.

**→ The flattened table needs a `basis` column (`declared` | `cash`)**, or these two bases keep
getting mixed and no sum will ever reconcile.

Proposed shape:

```sql
create table sgx_reit_distribution (
  symbol          text,
  financial_year  smallint,
  seq             smallint,
  period_label    text,      -- as-disclosed string, kept for audit
  period_start    date,
  period_end      date,
  period_type     text,      -- H1 | H2 | Q1..Q4 | FP | OTHER
  basis           text,      -- declared | cash
  dpu             numeric,   -- SG cents, consistent with distribution_per_unit
  primary key (symbol, financial_year, seq)
);
```

## Drop `distribution_period_months` ✅

Only 2 rows are < 12 (8C8U 2025 = 3.2 months, CMOU 2025 = 6.0); null on 7; the remaining 65 are
just `12`. Near-zero information as a column.

Safe **because of the previous decision** — once `distribution_record` carries typed
`period_start`/`period_end`, the covered period is computable from the tranche dates. **Do the
flatten first, drop this second.**

Keep the stub *signal* available: 8C8U's DPU of 1.739 covers 3.2 months and must not be compared
to a full-year DPU. Once derivable from the dates, the frontend can annotate it.

## `portfolio_occupancy` and `interest_coverage_ratio` are % ⚠️ **half right — ICR is not a percentage**

| column | n | min | max | mean | unit |
|---|---|---|---|---|---|
| `portfolio_occupancy` | 70 | 67.7 | 100.0 | 91.48 | ✅ percent |
| `interest_coverage_ratio` | 74 | **1.36** | **10.1** | **3.38** | ❌ **multiple (×)** |

ICR is a **coverage multiple** — "earnings cover interest 2.6 **times**". K71U's AR: *"an interest
coverage ratio of 2.6 times"*. TS0U's: *"improved to 2.4x"*. MAS sets a **minimum of 1.5×**.

If this renders with a `%` suffix, 2.6× displays as "2.6%" and reads as a REIT about to default.
This needs to reach Calvin explicitly — it is the kind of error that ships silently.

For completeness, the rest of the KPI block: `aggregate_leverage` and `cost_of_debt` **are**
percentages; `weighted_average_debt_maturity` and `weighted_average_lease_expiry` are **years**.

## `distribution_paid` is from the distribution statement, drop `distribution_cash_paid` ⚠️

Both columns come from the Distribution Statement — they are **different lines** of it. Only the
cash line closes the rollforward:

```
A + B + O − P = E   using distribution_cash_paid :  54/62 close
                    using distribution_paid      :  27/62 close
```

The 29 rows where they differ are material:

| row | declared | cash | delta |
|---|---|---|---|
| C38U 2024 | 752,211,000 | 874,072,000 | −121,861,000 |
| C38U 2025 | 860,874,000 | 750,125,000 | +110,749,000 |
| J91U 2025 | 176,076,000 | 90,145,000 | +85,931,000 |
| K71U 2025 | 212,406,000 | 276,593,000 | −64,187,000 |
| 8C8U 2025 | 29,953,000 | **0** | +29,953,000 (IPO stub paid after year-end) |

Complicating it: **`distribution_paid` already holds the cash figure on most rows** — 14 of 18
`distribution_paid_basis` flags read verbatim *"cash distributed during FY (period-mixed)"*, and
the two columns are identical on **32 of 74** rows. O5RU's flag states it outright:

> *"MD&A also cites S$78,154k as the for-the-year (declared) distribution — distribution_paid uses
> the audited cash-paid-during-year basis, not the for-year figure."*

**Recommendation: one column is fine, but define it as the cash line** ("Total Unitholders'
distribution" / total distributions during the year) and **re-extract the 29 divergent rows onto
that definition.** Otherwise the surviving column is cash on ~45 rows and declared on ~29, and the
rollforward stays broken on 27.

If the declared figure is still wanted, it is derivable as
`distribution_per_unit × number_of_shareholder_units` — another reason to fix the 4 null unit counts.

## `net_distributable_income` — clarification 📋

**Distributable income *generated during the financial year*, before any retention.** A **flow**,
not a balance. Read from the for-year subtotal of the audited Distribution Statement.

K71U FY2025, p121, `$'000`:

```
A  opening (pool from prior years)                        107,871
B  the unlabelled for-year subtotal                       212,406   <- net_distributable_income
   "Income available for distribution to Unitholders"      320,277   <- A+B, the CUMULATIVE. NOT stored.
P  "Total Unitholders' distribution (incl capital gains)" (276,593)
E  closing pool                                            43,684
```

**The critical distinction:** `net_distributable_income` is **NOT** the AR line labelled *"Income
available for distribution"* — that line is the cumulative pool including the prior-year carry.
Nearly every row's raw flag warns about this; C2PU 2025's calls it *"the cumulative trap line …
folds in opening carry"*. We were bitten by it: K71U and CRPU were both loaded with the cumulative
figure and corrected in July.

**Proposed rename: `distributable_income_generated`.**

## `adjusted_distributable_income + distributable_income_opening = net_distributable_income` ❌ does not hold

Tested on all 74 prod rows. Only **2 rows** have all three fields non-null, and **both fail**:

```
BUOU 2024:  adj 255,515,000 + open 131,812,000 = 387,327,000   vs NDI 210,337,000   NO
M1GU 2025:  adj  43,830,000 + open  18,683,000 =  62,513,000   vs NDI  39,709,000   NO
```

`adjusted_distributable_income` is non-null on only **3 of 74** rows, so it cannot be a general
rule regardless.

**Two independent reasons it fails:**

1. **The opening carry is not part of the for-year figure.** `opening + NDI` gives the *cumulative*
   pool. Adding opening to anything and calling it NDI reintroduces the cumulative trap above.
2. **`adjusted_distributable_income` has no stable meaning to build a formula on.** It means
   opposite things per row:

| | AR structure | `net_distributable_income` | `adjusted_distributable_income` |
|---|---|---|---|
| BUOU 2024 | Income available 210,337 → +capital distribution 45,178 → **Distributable income 255,515** | 210,337 (*pre*) | **255,515** (*post*) |
| J91U 2024 | Net income available 149,100 → +tax-exempt +capital → **164,064** | 164,064 (*post*) | **149,100** (*pre*) |
| M1GU 2025 | fees-in-cash / diluted-DPU sibling | 39,709 | 43,830 |

The rule actually applied was *"whatever the second disclosed distributable-income line is"*, which
lands on opposite lines depending on how each AR orders its statement. BUOU's own flag notes *"NO
'Adjusted distributable income' label in this AR"* — the name is ours, not the reports'.

**What does hold: `A + B + O − P = E`, on 54 of 62 rows** with all four present. The 8 failures are
a known NULL-backfill bug (all FY2024, each amount already page-cited in the raw flags — see
`performance_column_spec.md` D8). Verified exact on K71U, TS0U, and ME8U FY2024
(101,328 + 388,110 + 13,354 − 385,455 = 117,337).

**Recommendation:** split `adjusted_distributable_income` into two single-meaning columns —
`distributable_income_before_capital_distribution` and `distributable_income_fees_in_cash` — so no
formula has to guess which line it is reading.

## `net_distributable_income − distribution_paid − distributable_income_closing` = upcoming distribution ❌ negative on 48 of 54 rows

| symbol | FY | NDI | distribution_paid | closing | result |
|---|---|---|---|---|---|
| C38U | 2025 | 869,957,000 | 860,874,000 | 360,545,000 | **−351,462,000** |
| A17U | 2025 | 678,268,000 | 669,086,000 | 347,558,000 | **−338,376,000** |
| BUOU | 2024 | 210,337,000 | 262,580,000 | 124,747,000 | **−176,990,000** |
| ME8U | 2024 | 388,110,000 | 385,979,000 | 117,337,000 | **−115,206,000** |

**Why it cannot work: it subtracts a stock from a flow.** `distributable_income_closing` is a
**balance** that already contains the opening carry from prior years; `net_distributable_income` is
one year's **flow**. Subtracting the balance from the flow double-counts the carry-forward — hence
a large negative result for any REIT with a meaningful pool.

**The intended figures are already in the table:**

- **Undistributed pool at year-end** = `distributable_income_closing` (**E**). That *is* the amount
  generated but not yet paid out, carried into next year. No arithmetic needed.
- **Declared but not yet paid** = `distribution_declared_for_year − distribution_cash_paid`.
  8C8U 2025 is the clean case (declared 29,953,000, cash 0 → the whole FY2025 distribution paid
  after year-end); K71U 2025 is the opposite sign (declared 212,406,000, cash 276,593,000 → drew
  64.2m out of the pool).
- **Retention for the year** = `B − declared`.

⚠️ Note the second of these needs **both** distribution columns — so it conflicts directly with
dropping `distribution_cash_paid`. **These two decisions should be made together.**

## `distribution_pool_other_movements` — standalone? how used? 📋

**Not standalone.** It is a term in the identity `A + B + O − P = E`; without it the rollforward
does not close for 16 REIT-years. It holds the *disclosed reconciling line* sitting between
"generated" and "closing" — read verbatim, never derived.

All 16 populated rows, currently carrying **three unrelated economics**:

- **retention / withholding** (negative, 11 rows) — CMOU 2025 −51.9m (*"Distribution withheld…
  RETENTION, Manager reserve, p38"*), OXMU 2025 −26.2m, HMN −23.2m, C38U −9.4m / −9.1m
  (*"Amount retained for general corporate and working capital purposes, Note B p105"*),
  TS0U −5.0m, C2PU −3.0m (capex retention)
- **capital / divestment gains added to the pool** (positive) — BUOU +45.2m (capital distribution),
  ME8U +13.4m (*"Distribution of gains from divestment, incl. Tanglin Halt Cluster"*) / +5.4m
- **corrections / rounding** — AU8U +5.7m, J85 +4.0m

**The problem: the value alone does not say which of the three it is.** −51.9m (money withheld
*from* unitholders) and +45.2m (extra money *to* unitholders) live in one column with no
discriminator.

**Recommendation: split retention into its own column** `distributable_income_retained`, and
restrict `other_movements` to genuine disclosed pool additions. Retention is recoverable — for
OXMU 2024 it is exactly `B − distribution_paid` (51,929,452 − 5,356,861 = 46.57m, matching the AR's
*"Amount retained"* of 34,237k USD). It is also the field that makes payout ratio and retention
rate computable.

---

# Not in the recap — two items that affect this work

## 🔴 P0 — DPU and NAV are integer-rounded in prod for every foreign-currency reporter

`scripts/db/build_final_tables.py:30`

```python
return round(float(value) * tbl[ccy]['SGD'])   # round() with no ndigits -> integer
```

Harmless for money in base units; **destroys per-unit figures**. SGD reporters escape via the early
return on line 24, so only the 13 foreign reporters are hit. **28 corrupted values in prod**
(13 DPU + 15 NAV), 4 of them rounded to **zero**:

| row | raw (native) | prod serves | correct |
|---|---|---|---|
| OXMU 2024 DPU | 0.29 US¢ | **0.0** | 0.39 |
| CMOU 2025 DPU | 0.25 US¢ | **0.0** | 0.32 |
| BTOU 2024 NAV | US$0.23 | **0.0** | 0.31 |
| BTOU 2025 NAV | US$0.19 | **0.0** | 0.24 |
| MXNU 2025 DPU | 3.03p | 5.0 | 5.24 |
| ODBU 2025 DPU | 4.39 US¢ | 6.0 | 5.64 |
| SET 2024 DPU | 14.106 €¢ | 20.0 | 19.97 |
| UD1U 2025 NAV | €0.34 | 1.0 | 0.51 |

DPU drives yield; NAV drives P/NAV. **Distinguish from genuine zeros** — 5 of the 7 DPU zeros are
correct (`distribution_basis = 'suspended'`): BTOU 2024/2025, CMOU 2024, D5IU 2024/2025. Only
OXMU 2024 and CMOU 2025 are the bug.

**Fix:** `round(..., 6)` → rebuild `_final` → re-promote. Verified contained: raw-vs-final drift on
all non-converted columns (leverage, WALE, unit counts) is **0 across 74 rows**.

## `properties_location` format — inherited convention, worth revisiting

Prod holds `'[Singapore, Australia, South Korea, Japan]'` — literal brackets, no quotes; not JSON,
not `text[]`. **This is deliberate, not our bug**: `promote_final_to_prod.py:59` has
`BRACKET_TEXT_FIELDS` with the comment *"prod's bracketed text '[A, B, C]' (NOT a real array)"* —
it matches prod's pre-existing schema.

Still worth raising: the consumer must strip `[` / `]` and split on `", "`, and it breaks if a
country name ever contains a comma. Moving to `jsonb` would be cleaner, but it is a **prod-wide
convention change**, so it needs Evelyn's and Calvin's agreement, not a unilateral fix.

---

# Suggested order of work

**Mechanical — no decision needed:**

1. **P0** `round(x, 6)` in `build_final_tables.py:30`, rebuild, re-promote.
2. Backfill 4 `number_of_shareholder_units` + 2 `number_of_unitholders`.
3. Backfill the 8 `distribution_pool_other_movements` values from the raw flags (closes the guard
   54 → 62).
4. Fold the 9 `gross_lettable_area` values into `net_lettable_area`; drop the column.
5. Derive `lease_expiry_date` for the 145 effective-only rows; then drop `effective_date`.
6. Merge `purchase_price` / `sale_price` → `transaction_price` (fixes the 12 duplicated values).
7. Drop `announced_date` + `transaction_date`; backfill 2 missing `completed_date`.
8. Normalise the 2 `payment_date` keys to `pay_date`.
9. Rename the 6 mislabelled Mapletree dirs in `parsed_reports_datalab/` **before** any re-sweep
   (they are one year low — see `performance_column_spec.md` D10.1).

**Needs a decision:**

10. `distribution_paid` definition + whether `distribution_cash_paid` survives *(decide with #11)*.
11. How "upcoming distribution" is expressed.
12. Split `adjusted_distributable_income`.
13. Split retention out of `distribution_pool_other_movements`.
14. Flatten `distribution_record` → `sgx_reit_distribution` (+ `basis` column).
15. `pct_basis` canonical enum + `pct_basis_note`.
16. `valuation` keep-or-drop; which gain metrics get derived.
17. `interest_pct` keep-or-drop.
18. Whether non-completed transactions are filtered in the table or the view.
19. `units_to_be_issued` — `0` or `NULL` where the AR has no such line.
20. `properties_location` → `jsonb` (prod-wide convention change).

**Presentation, not data:**

21. Distressed-REIT path for BTOU (leverage 60.8%, ICR 1.7, DPU suspended) and D5IU (ICR 1.36,
    NAV S$0.049) — currently indistinguishable from bad data.
22. Basis caveats — MXNU's WALE 7.2y is the post-lease-regear pro forma (pre-regear 2.4y).
23. ICR must render as `×`, never `%`.
