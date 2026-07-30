# `sgx_reit_performance` (PROD) — column spec, defects & clarification plan

**Status:** WORKING DOC (2026-07-30). Scope = the **prod** table only (28 columns, 74 rows,
37 REITs). Raw dev (`sgx_reit_performance`, 33 cols) and `sgx_reit_performance_final` are
referenced only where they explain a prod value. Prepared for the Evelyn/Calvin review.

Every value below was cross-checked against the parsed annual reports
(`parsed_reports_datalab/<n>_<SYM>_<FY>/full.md`). Three REITs were audited field-by-field —
**K71U FY2025** (SGD), **TS0U FY2025** (SGD), **MXNU FY2025** (GBP) — plus targeted checks on
BUOU, J91U, Q5T, OXMU, CMOU, ME8U, AJBU.

---

## 0. Conventions that apply to the whole table

| convention | value | note |
|---|---|---|
| symbol format | **bare ticker, no `.SI`** | Consistent across all 6 prod `sgx_reit_*` tables and `sgx_companies`. `_final` keeps `.SI`; `promote_final_to_prod.py` strips it. Deliberate — not a defect. |
| currency | **all money = SGD** | Foreign reporters converted via MAS quarterly rates (`quarterly_rates.json`, nearest quarter to FY-end). No currency column in prod. |
| financial year | **declared FY** — Jan–Jun year-end maps to X−1 | Verified: 0 of 74 rows disagree with the rule. ME8U ye-2025-03-31 → FY2024, matching the trust's own "FY24/25" label. |
| areas / percentages | percentages are plain numbers (`47.9` = 47.9%) | |
| provenance | stripped on promotion | `flags`, `distribution_basis`, `source_page`, `currency`, `id` stay in dev raw. 71 of 74 raw rows carry page-cited flags that explain their values — prod consumers never see them. |

**FY coverage:** FY2023 × 3 (the Mar-year-end Mapletree trusts), FY2024 × 36, FY2025 × 35.
FY-end months present: Dec 57, Mar 11, Sep 4, Jun 2.

---

## 1. The 28 columns

Fill counts are out of 74.

### 1.1 Keys & provenance

| column | type | what it is | source in AR | fill | status |
|---|---|---|---|---|---|
| `symbol` | text | SGX ticker, no suffix | our catalog | 74 | OK |
| `financial_year` | int | declared FY (see §0) | derived from `date` | 74 | OK — but **needs documenting**; Calvin must not assume FY = calendar year |
| `date` | date | FY-end date | audited statement header | 74 | OK |
| `source_url` | text | R2 link to the AR PDF we parsed | our pipeline | 74 | OK — single host, all `.pdf` |

### 1.2 Portfolio & scale

| column | type | what it is | source in AR | fill | status |
|---|---|---|---|---|---|
| `properties_location` | text | countries the portfolio sits in | AR portfolio section | 74 | **DEFECT D2** — holds a stringified Python list |
| `portfolio_value` | numeric SGD | headline portfolio valuation incl. JV proportionate interests | Portfolio Statement total / valuation commentary | 74 | OK — K71U 11,657,085 ✓, TS0U 5,793.0m ✓, MXNU £424.7m ✓ |
| `gross_revenue` | numeric SGD | **total property income** = revenue + other property income | audited P&L, **derived sum** | 74 | OK but **definition must be published** — see §2 D5 |
| `net_property_income` | numeric SGD | NPI as reported | audited P&L | 74 | OK — MXNU 34,623 = 38,305 − 3,682 ✓ |

### 1.3 Unit counts

| column | type | what it is | source in AR | fill | status |
|---|---|---|---|---|---|
| `number_of_unitholders` | int | **headcount** of unitholders | Statistics of Unitholdings | 72 | 2 missing (AJBU 2024, UD1U 2024) |
| `number_of_shareholder_units` | numeric | **units in issue** at FY-end | Units-in-Issue note + balance sheet | 70 | **DEFECT D3** — 4 missing, all disclosed |
| `units_to_be_issued` | numeric | units committed but not yet issued (Manager fees payable in units) | same note, separate sub-line | 26 | Legitimately sparse **+ under-filled**; needs the null-vs-0 decision |

These three are routinely confused. TS0U FY2025 shows the actual structure:

```
Units in issue          At 31 December            5,524,617   -> number_of_shareholder_units
Units to be issued      Mgmt fees payable in Units    5,272   -> units_to_be_issued
Units in issue and to be issued                   5,524,617
                        (28,418 unitholders        -> number_of_unitholders)
```

### 1.4 Capital-management KPIs — all as-disclosed, all verified

| column | type | what it is | source in AR | fill | K71U / TS0U / MXNU |
|---|---|---|---|---|---|
| `aggregate_leverage` | numeric % | gearing per Property Funds Appendix | Capital Management | 74 | 47.9 / 38.5 / 42.8 |
| `interest_coverage_ratio` | numeric × | ICR per MAS guidelines | Capital Management | 74 | 2.6 / 2.4 / 2.6 |
| `cost_of_debt` | numeric % | weighted-avg all-in cost of debt | Capital Management | 73 | 3.41 / 3.9 / 4.7 |
| `weighted_average_debt_maturity` | numeric yr | WADM / WATM | Capital Management | 66 | 2.4 / 3.3 / 1.8 |
| `weighted_average_lease_expiry` | numeric yr | WALE | lease-expiry section | 66 | 4.4 / 2.2 / 7.2 |
| `portfolio_occupancy` | numeric % | committed / portfolio occupancy | portfolio review | 70 | 96.7 / 95.4 / 98.6 |

Range scan across all 74 rows found **no out-of-range values**. Four apparent outliers were
checked and are all **genuine**, not errors:

- BTOU (Manulife US REIT) leverage **60.8%** FY2024 / **58.4%** FY2025 with ICR 1.7 — real distress,
  distributions suspended.
- D5IU (Landmark REIT) ICR **1.36** FY2024, NAV/unit **S$0.0576** / **S$0.0491** — real.

> **Frontend implication:** these need a "distressed / covenant-breach" presentation path, not a
> data fix. Serving 60.8% leverage with no context reads as a bug to users.

Basis caveats worth surfacing (as-disclosed, but not comparable): MXNU's WALE 7.2y is the
**post-lease-regear pro forma**; the AR states pre-regear WALE would be 2.4y.

### 1.5 Per-unit & distribution timing

| column | type | what it is | source in AR | fill | status |
|---|---|---|---|---|---|
| `distribution_per_unit` | numeric | full-year DPU, **SG cents after FX** | highlights / Distribution Statement | 74 | **DEFECT D1** — integer-rounded for foreign reporters |
| `net_asset_value_per_unit` | numeric SGD | NAV per unit | balance sheet / highlights | 74 | **DEFECT D1** |
| `distribution_record` | jsonb | per-tranche DPU `[{period, dpu, ex_date, pay_date}]` | Distribution Statement lines; `pay_date` from the **Financial Calendar** | 71 | **DEFECT D4** — the worst column in the table |
| `distribution_period_months` | numeric | months the DPU covers (12 = full year) | derived | 67 | OK — min 3.2 = 8C8U IPO stub ✓ |

### 1.6 The distribution block (7 columns)

| column | role | what it is | source line |
|---|---|---|---|
| `distributable_income_opening` | **A** | pool carried in from prior years | "…at beginning of the year" |
| `net_distributable_income` | **B** | generated this year, **before retention** — the cross-REIT comparable | the for-year subtotal |
| `distribution_pool_other_movements` | **O** | the disclosed reconciling line that makes the rollforward close | its own named line |
| `distribution_cash_paid` | **P** | cash actually paid out this year, period-mixed | "Total Unitholders' distribution" |
| `distributable_income_closing` | **E** | pool carried to next year | "…at end of the year" |
| `distribution_paid` | — | *specified as* declared-for-the-year (DPU basis) | **DEFECT D6** |
| `adjusted_distributable_income` | — | *specified as* the fees-in-cash / diluted-DPU sibling | **DEFECT D7** |

**Identity: `A + B + O − P = E`.** Verified exact on K71U FY2025 (107,871 + 212,406 − 276,593 =
43,684), TS0U FY2025 (66,262 + 128,752 − 5,000 − 116,184 = 73,830) and ME8U FY2024
(101,328 + 388,110 + 13,354 − 385,455 = 117,337).

Guard status across prod: **54 pass · 8 break · 12 skipped (nulls)** → **DEFECT D8**.

The cumulative trap, for the record: the AR line *"Income available for distribution"* = **A + B**
and is deliberately **not stored**. K71U and CRPU were both originally loaded with this cumulative
figure and corrected in July.

---

## 2. Confirmed defects

Severity: **P0** = wrong data served to users · **P1** = unusable/ambiguous · **P2** = clarity.

### D1 — P0 · DPU and NAV integer-rounded for every foreign-currency reporter

`scripts/db/build_final_tables.py:30`

```python
return round(float(value) * tbl[ccy]['SGD'])   # round() with no ndigits -> integer
```

Harmless for money in base units; **destroys per-unit figures**. SGD reporters escape via the
early return on line 24, so only the 13 foreign reporters are hit. **28 corrupted values in prod**
(13 DPU + 15 NAV), of which **4 are rounded to zero**:

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

DPU drives yield; NAV drives P/NAV. Both headline metrics.

**Distinguish from genuine zeros** — 5 of the 7 DPU zeros are correct (`distribution_basis =
'suspended'`): BTOU 2024/2025, CMOU 2024, D5IU 2024/2025. Only OXMU 2024 and CMOU 2025 are the bug.

**Fix:** `round(..., 6)` → rebuild `_final` → re-promote. Verified no other field is affected:
raw-vs-final drift on all non-converted columns (leverage, WALE, unit counts) is **0 across 74 rows**.

### D2 — P1 · `properties_location` is a stringified Python list

Prod holds `'[Singapore, Australia, South Korea, Japan]'` — literal brackets, no quotes. Not JSON,
not `text[]`, not comma-separated. `build_final` passes `normalize_locations()`'s list straight into
a `text` column. All 74 rows.

The consumer has to strip `[`/`]` and split on `", "`, and it breaks the moment a country name
contains a comma.

**Fix:** make it `jsonb` (or `text[]`). Raw keeps the richer form (`"United Kingdom (England,
Scotland, Wales)"` → `[United Kingdom]`); the flattening itself is intended.

### D3 — P1 · `number_of_shareholder_units` missing on 4 rows, all disclosed

| row | prod | AR discloses |
|---|---|---|
| AW9U 2024 | NULL | 2,094,447k (Note 16) |
| CMOU 2024 | NULL | 1,044,450k (Note 13) |
| J91U 2024 | NULL | 8,049,164k (Note 18) |
| TS0U 2024 | NULL | 5,492,950k (Note 15) |

All FY2024. Straight extraction misses, no disclosure gap.

**J91U's is load-bearing:** its DPU goes 2.119 (FY2024) → 21.914 (FY2025), a 10.3× jump that looks
like a data error until you see units fall 8,049,164k → 805,035k — ESR-REIT's **10-into-1 unit
consolidation**. Both figures are correct; without the FY2024 unit count the series is unexplainable.

`number_of_unitholders` also missing on AJBU 2024 and UD1U 2024.

### D4 — P1 · `distribution_record` is not consumable

Four separate problems in one jsonb column (170 entries across 71 rows):

1. **`period` has 123 distinct formats.** `1H 2025` · `1 January 2025 to 30 June 2025` ·
   `01/07/2024 to 31/12/2024` · `2025-01-01 to 2025-06-30` · `1Q FY25/26 (1 Apr-30 Jun 2025)` ·
   `FP 2025 (25 Sep 2025 - 31 Dec 2025)`. **This is ours, not the reports'** — AJBU's AR prints
   `1/1/2025 to 30/6/2025` and we stored `2025-01-01 to 2025-06-30`. Losslessly normalisable.
2. **`ex_date` is 0/170 and structurally unobtainable.** It appears in no AR — it's an
   SGX-announcement field. `pay_date` is 27/170, correctly sourced from the AR's **Financial
   Calendar** (verified: AJBU p198 *"Distribution for 1 January 2025 to 30 June 2025 — 15 September
   2025"*), sparse because only some REITs publish one.
3. **Key drift:** 162 entries use `pay_date`, **2 use `payment_date`**, 6 have neither key.
4. **`dpu` is in NATIVE currency while `distribution_per_unit` is FX-converted to SG cents** —
   two DPU representations in one row, different units, no currency tag. Confirmed on DCRU
   (record 3.6 US¢, column 5.0 "SG¢").

Consequence: `sum(record.dpu)` ≠ `distribution_per_unit` on **24 of 63** comparable rows. Three
causes — the currency mismatch above, D1's rounding, and genuine basis-mixing:

**K71U FY2025 has five entries where the AR supports three:**

```
{dpu: null,  period: "1/7/2024 to 31/12/2024"}   <- dpu MISSING (AR: 2.80c)
{dpu: 2.72,  period: "1/1/2025 to 30/6/2025"}    <- cash basis
{dpu: 1.63,  period: "1/7/2025 to 16/10/2025"}   <- cash basis
{dpu: 2.72,  period: "1H 2025"}                  <- DUPLICATE of row 2, declared basis
{dpu: 2.51,  period: "2H 2025"}                  <- declared basis (2.72+2.51 = 5.23 = FY DPU)
```

Cash-basis tranches and declared half-years concatenated into one array. 12 rows have a duplicated
DPU value; some are legitimate (two half-years paying the same rate, e.g. DCRU 1.8 + 1.8), so this
cannot be auto-deduped — it needs period-aware repair. Note the sum-check **misses K71U entirely**
because the null `dpu` excludes the row.

**Fix — flatten to a child table** (this is the "restructuring/flattening" Evelyn asked for):

```sql
create table sgx_reit_distribution (
  symbol          text,
  financial_year  smallint,
  seq             smallint,
  period_label    text,        -- as-disclosed string, kept for audit
  period_start    date,
  period_end      date,
  period_type     text,        -- H1 | H2 | Q1..Q4 | FP | OTHER
  basis           text,        -- declared | cash
  dpu             numeric,     -- SG cents, FX-converted, consistent with distribution_per_unit
  pay_date        date,
  primary key (symbol, financial_year, seq)
);
```

Drop `ex_date` unless we commit to ingesting SGX announcements.

### D5 — P2 · `gross_revenue` is a derived total, not a printed line

MXNU FY2025's `38,305` **appears nowhere in the AR**. It is:

```
Revenue                        36,590
Other property income           1,715
                              ------- 38,305  <- gross_revenue
Property operating expenses    (3,682)
Net property income            34,623  = 38,305 - 3,682  OK
```

Correct and internally consistent, but computed. The same AR prints two *other* "Revenue" figures
(36,590 in the results table, 37,973 in another), so a reviewer checking our number against the
report will conclude it's wrong.

**Fix:** publish the definition — *"total property income = revenue + other property income; the
base from which NPI is derived."* No data change.

### D6 — P0/P1 · `distribution_paid` does not mean what it's specified to mean

Specified as "declared for the year". In practice **14 of 18** `distribution_paid_basis` flags read
verbatim *"cash distributed during FY (period-mixed)"* — i.e. the same thing as
`distribution_cash_paid`.

Across 74 rows: **identical on 32 · differ on 29 · one-null on 13.**

O5RU FY2024's own flag admits it:

> *"MD&A also cites S$78,154k as the for-the-year (declared) distribution — distribution_paid uses
> the audited cash-paid-during-year basis, not the for-year figure."*

Only M1GU 2025 (*"Declared-for-FY basis"*) and OXMU 2024 hold a genuine declared figure. So any
payout ratio built on this column is wrong for ~half the table.

**This is the single most important thing to settle before endpoints are built**, and Evelyn did not
raise it.

### D7 — P1 · `adjusted_distributable_income` means opposite things in different rows

3 rows populated. Same two AR lines, inverted mapping:

| | AR structure | `net_distributable_income` | `adjusted_distributable_income` |
|---|---|---|---|
| BUOU 2024 | Income available 210,337 → +capital distribution 45,178 → **Distributable income 255,515** | 210,337 (*pre*) | **255,515** (*post*) |
| J91U 2024 | Net income available 149,100 → +tax-exempt +capital → **164,064** | 164,064 (*post*) | **149,100** (*pre*) |
| M1GU 2025 | fees-in-cash / diluted-DPU sibling | 39,709 | 43,830 |

The rule actually applied was *"whatever the second disclosed distributable-income line is"* —
which lands on opposite lines depending on how each AR orders its statement. Only M1GU matches the
documented intent. BUOU's own flag notes *"NO 'Adjusted distributable income' label in this AR"* —
the name is ours, not the reports'.

**Fix:** split into two columns with single definitions —
`distributable_income_before_capital_distribution` and `distributable_income_fees_in_cash`.

### D8 — P1 · 8 rollforward breaks, all FY2024, all recoverable from the flags

Every one is `distribution_pool_other_movements` being NULL when the raw flag names the exact
amount, with a page cite. Several flags even claim the value *was* stored (OXMU: *"Captured as
distribution_pool_other_movements = -34,237,000"*) — the FY2024 backfill wrote the note and never
wrote the column. NULL in **both** raw and `_final`.

| row | break (SGD) | flagged reconciling line | native |
|---|---|---|---|
| Q5T 2024 | −16,121,000 | "Distribution of other gains" (Central Square divestment) | +16,121 |
| OXMU 2024 | 46,572,591 | "Amount retained", p140 | −34,237 USD |
| CMOU 2024 | 64,787,008 | "Distribution withheld … 1 Jan-31 Dec 2024", p103 | −47,627 USD |
| CRPU 2024 | 7,385,000 | "Less: Amount retained", p160 | −7,385 |
| J85 2024 | −4,062,000 | retained −6,261 + capital distribution +10,323, p201 | +4,062 |
| M1GU 2024 | 3,994,000 | "Amount retained for working capital", p127-128 | −3,994 |
| BMOU 2024 | 286,000 | "Amount retained" ~S$0.3m, footnote (1) p129 | −286 |
| MXNU 2024 | 2,359,627 | "Amount retained…", Note 25 p166 | −1,382 GBP |

Every diff matches its flagged amount exactly, FX included.

**Mechanical backfill — no AR re-read required.**

### D9 — P2 · `distribution_pool_other_movements` is undefined as a column

Defensible per row, unreadable in aggregate. The 16 populated rows carry three unrelated economics:

- **retention / withholding** (negative, 11 rows): CMOU 2025 −51.9m, OXMU 2025 −26.2m, HMN −23.2m,
  C38U −9.4m/−9.1m, TS0U −5.0m, C2PU −3.0m (capex retention)
- **capital / divestment gains added to the pool** (positive): BUOU +45.2m, ME8U +13.4m/+5.4m
- **corrections / rounding**: AU8U +5.7m, J85 +4.0m

You cannot tell from the value which it is.

**Fix (recommended):** promote retention to its own column `distributable_income_retained` and
restrict `other_movements` to genuine disclosed pool additions. Retention is recoverable — for OXMU
2024 it is exactly `B − distribution_paid` (51,929,452 − 5,356,861 = 46.57m).

### D10 — P2 · dev-side hygiene (does not reach prod, but blocks safe re-work)

1. **`parsed_reports_datalab/` dir labels are one year low for the 3 Mapletree trusts.**
   `27_ME8U…_FY2022/` is ye-2024-03-31 (= FY2023), `…_FY2023/` is ye-2025-03-31 (= FY2024),
   `…_FY2024/` is ye-2026-03-31 (= FY2025). Same on `28_M44U*` and `29_N2IU*`; O5RU / JYEU / P40U
   are correct. **The DB is right, the folders are wrong** — the rename subtracted 2 instead of 1
   (`meta.json.file` still holds the original PDF names). Anyone re-sweeping FY2024 off folder names
   reads the wrong report.
2. **`distribution_basis` was never migrated** to the slim vocabulary the July proposal specified.
   Still the retired 4-value set (`disclosed_after_retention` 39, `full_payout_no_retention_line` 19,
   `not_disclosed_rollforward_only` 11, `suspended` 5) and unreliable — BUOU 2024 is tagged
   `not_disclosed_rollforward_only` although its rollforward is fully disclosed (A 131,812, E 124,747).
3. **Some flags are stale.** K71U 2025's `net_distributable_income_basis` still reads
   *"320,277k = Income available for distribution"*; the column now holds 212,406 after the July fix.
4. **`flags` has internal schema drift** — mostly `{type, scope, note}` dicts, but BUOU 2024 carries
   two bare **strings**, and a few rows have an entire paragraph sitting in the `type` key. ~40
   distinct type values.

---

## 3. Naming proposal

The distribution block currently has three columns whose names don't distinguish them. Proposed set
reads as one coherent sequence:

| now | proposed | why |
|---|---|---|
| `net_distributable_income` | `distributable_income_generated` | "net" implies a subtraction that isn't there; this is the for-year generated figure |
| `distribution_paid` | `distribution_declared_for_year` | forces D6 to be resolved rather than papered over |
| `distribution_cash_paid` | *keep* | already unambiguous |
| `distribution_pool_other_movements` | `distributable_income_other_movements` | matches the A/B/E family |
| — *(new)* | `distributable_income_retained` | see D9 |
| `adjusted_distributable_income` | *split* → `distributable_income_before_capital_distribution` + `distributable_income_fees_in_cash` | see D7 |
| `distributable_income_opening` / `_closing` | *keep* | |

Renames are value-preserving; only D6/D7 change semantics.

---

## 4. Action order

**Mechanical — no decisions needed:**

1. **D1** fix `round(x, 6)` in `build_final_tables.py:30`, rebuild, re-promote. *(P0 — prod is
   serving DPU = 0 for Prime US REIT and KORE, NAV = 0 for Manulife US REIT.)*
2. **D8** backfill the 8 `other_movements` values from the raw flags; re-run the guard → expect 62 pass.
3. **D3** backfill 4 `number_of_shareholder_units` + 2 `number_of_unitholders` from the cited notes.
4. **D2** change `properties_location` to `jsonb`.
5. **D10.1** rename the 6 mislabelled Mapletree parsed dirs **before** any re-sweep.
6. **D4.3** normalise the 2 `payment_date` keys to `pay_date`.

**Needs a decision first:**

7. **D6** what does `distribution_paid` mean? *(recommend: re-read the declared figure for all 74
   rows, keep the two columns genuinely distinct)*
8. **D7** split `adjusted_distributable_income`. *(recommend: yes)*
9. **D9** promote retention to its own column. *(recommend: yes)*
10. **D4** flatten `distribution_record` to `sgx_reit_distribution`; drop `ex_date`. *(recommend: yes)*
11. `units_to_be_issued` — `0` or `NULL` where the AR has no such line? *(recommend: 0, with NULL
    reserved for genuinely undetermined)*
12. **D5** publish the `gross_revenue` definition; also decide whether `distribution_record.dpu`
    becomes SG cents (consistent with `distribution_per_unit`) or keeps a currency tag.

**Presentation, not data:**

13. Distressed-REIT path for BTOU (leverage 60.8%, ICR 1.7, DPU suspended) and D5IU (ICR 1.36,
    NAV S$0.049) — currently indistinguishable from bad data.
14. Basis caveats: MXNU WALE 7.2y is post-regear pro forma (pre-regear 2.4y).
15. Surface a cleaned subset of the raw `flags` as tooltips — they already answer most of Evelyn's
    questions with page cites, and prod consumers currently can't see any of it.
