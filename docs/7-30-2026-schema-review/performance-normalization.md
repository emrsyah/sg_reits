# `sgx_reit_performance` — why the numbers don't tally, and how to normalize

Deep verification of every column's provenance across ~25 annual reports, plus a test of the six
identities the table should satisfy. 2026-07-30.

**Conclusion up front:** the columns are, individually, mostly *correct as-disclosed*. The confusion
comes from three things layered on top of them — **currency handling that treats balances like
flows**, **two different definitions sharing one column**, and **KPIs that carry different bases
under one name**. None of that is fixed by re-extraction; it needs a normalization contract.

---

## 1. Identity scorecard — where we stand today

| # | identity | result |
|---|---|---|
| 1 | `opening + generated + other − cash_paid = closing` | 54 pass · **8 break** · 12 not computable |
| 2 | `closing(FY n) = opening(FY n+1)` | 25 pass · **6 break** · 6 n/a |
| 3 | `DPU × units ≈ declared distribution` | **37 of 55** within ±5% |
| 4 | `portfolio_value ≈ Σ property market_valuation` | **45 of 74** within ±5% |
| 5 | `Σ distribution_record.dpu = distribution_per_unit` | **39 of 63** |
| 6 | payout ratio `declared / generated` within 0–1.3 | **74 of 74** ✅ |

Every failure below is explained. Only two are actual data errors.

---

## 2. Identity 1 — the 8 rollforward breaks are a missing column value, nothing more

All 8 close exactly once the disclosed reconciling line is included. Verified verbatim:

| REIT | FY | AR line that closes it | native |
|---|---|---|---|
| Q5T | 2024 | *"Distribution of other gains"* | 16,121 |
| OXMU | 2024 | *"Amount retained"* | (34,237) USD |
| CMOU | 2024 | *"Distribution withheld for the financial year from 1 Jan 2024 to 31 Dec 2024"* | (47,627) USD |
| CRPU | 2024 | *"Less: Amount retained"* | (7,385) |
| J85 | 2024 | *"Less: Amount retained for working capital"* (6,261) **+** *"Add: Capital distribution"* 10,323 | net +4,062 |
| M1GU | 2024 | *"Amount retained for working capital"* — applied to the **opening** balance | (3,994) |
| BMOU | 2024 | *"Amount retained"* | (286) |
| MXNU | 2024 | *"Less: Amount retained for general corporate and working capital ("Retention")"* | (1,382) GBP |

`distribution_pool_other_movements` is simply **NULL** on these rows — a backfill, not a correction.

**M1GU has a structurally different statement**: retention is deducted from the *opening* pool
(15,539 → 11,545 *"after retention"*), not from the year's income. One `O` term still closes it, but
the ordering differs from every other REIT.

### The 12 not-computable rows split three ways — only 2 values are recoverable

| | REITs | verdict |
|---|---|---|
| **Extraction gap** | AW9U FY2024 | A = **12,906** and E = **12,113** are disclosed (p126). Cumulative line 62,222 sits between them — 62,222 − 12,906 = 49,316 = the B we already store. Backfill A and E. |
| **Structural — the AR has no pool balance** | CY6U, UD1U, XZL, J91U | pure flow statements: income → retention → distribution. No opening/closing line exists in **any** year. |
| **Genuinely nil** | D5IU FY2024/2025 | every line is "–"; distributions suspended since FY2023 by a perpetual-securities dividend stopper. |

**J91U is the notable edge:** it computes a closing residual (FY2024: 77,833) but never carries it
into the next year's opening. The AR treats each year as a closed loop — a cross-year identity would
be our invention, not the REIT's.

### An extraction rule worth encoding

The reliable signal distinguishing **B** from the cumulative **A+B** trap is the phrase
**"for the year"**:

- B → *"Income available for distribution to Unitholders **for the year**"*
- A+B → *"Income available for distribution to Unitholders"* (unqualified), one row below

Present in Q5T, OXMU, CMOU, CRPU, J85, M1GU, BMOU. This is exactly the error that hit K71U and CRPU
in July.

### Retention wording is not uniform — six phrasings

*"Amount retained"* · *"Amount retained for working capital"* · *"Less: Amount retained for general
corporate and working capital ("Retention")"* · *"Distribution withheld"* · *"10% retention"* · and
sometimes only in a footnote, never as a statement line. Splitting retention into its own column
needs pattern-matching on `retain|withheld` **plus** footnote review — it cannot be a clean field
extraction.

---

## 3. Identity 2 — all 6 cross-year breaks are pure FX. This is the core design flaw.

Checked in the raw table, in native currency:

| REIT | ccy | closing FY *n* | opening FY *n+1* | |
|---|---|---|---|---|
| BTOU | USD | 112,608,000 | 112,608,000 | ✅ |
| DCRU | USD | 23,405,000 | 23,405,000 | ✅ |
| MXNU | GBP | 8,936,000 | 8,936,000 | ✅ |
| ODBU | USD | 16,594,000 | 16,594,000 | ✅ |
| OXMU | USD | 1,621,000 | 1,621,000 | ✅ |
| SET | EUR | 39,886,000 | 39,886,000 | ✅ |

**Every one tallies perfectly.** In prod they break by exactly the ratio of the two year-end rates:
USD 1.3603 / 1.2841 = 1.0593; GBP 1.7074 / 1.7288 = 0.9876; EUR 1.416 / 1.5077 = 0.9392 — all
matching to four decimals.

**The cause is conceptual.** `distributable_income_closing` is a **balance**. We convert it at the
*period's* rate, as if it were a flow. A pool that did not move in native currency appears to move in
SGD. No re-extraction fixes this; it is inherent to converting stocks at period-specific rates.

**No AR mixes currencies inside its Distribution Statement** — each is wholly in its own presentation
currency. All the cross-currency damage is introduced in our layer, not inherited.

---

## 4. Identity 4 — the currency tag means OPPOSITE things depending on the REIT

This is the most important finding, and it means a blanket "convert everything" fix would **destroy**
data.

1,253 of 3,332 property rows across 18 REITs carry a non-SGD `market_valuation_currency`. I tested
each REIT-year two ways — sum as-is (H1) vs sum converted at each tag's rate (H2) — against
`portfolio_value`:

### Group A — values genuinely native, tags correct, conversion missing → **convert**

Foreign-presentation-currency REITs. H2 matches `portfolio_value` **exactly**:

| REIT | FY | Σ as-is | Σ converted | portfolio_value (SGD) |
|---|---|---|---|---|
| BTOU | 2024 | 1,137,200,000 | **1,546,933,160** | 1,546,933,160 |
| ODBU | 2024 | 752,860,000 | **1,024,115,458** | 1,024,115,458 |
| CMOU | 2024 | 1,326,410,000 | **1,804,315,523** | 1,804,315,523 |
| OXMU | 2024 | 1,352,070,000 | **1,839,220,821** | 1,839,220,821 |
| XZL | 2024 | 728,000,000 | **990,298,400** | 990,298,400 |
| SET | 2025 | 2,155,023,000 | 3,249,128,177 | 3,253,462,815 |
| UD1U | 2025 | 804,280,000 | 1,212,612,956 | 1,203,295,370 |
| MXNU | 2025 | 425,100,000 | 734,912,880 | 734,221,360 |

Confirmed at line level: ODBU's AR Portfolio Statement is headed **US$'000** with Price Chopper Plaza
20,500 / Piscataway 24,100 / Arundel 49,500 — exactly our stored values, and **no SGD column exists
anywhere** in it. Same for MXNU (£'000) and SET (€'000).

### Group B — values ALREADY SGD, tags spurious → **strip the tag, do NOT convert**

SGD-reporting REITs holding overseas assets. Their **audited Portfolio Statement is SGD-only across
all countries**. H1 matches `portfolio_value`; H2 is catastrophically wrong:

| REIT | FY | Σ as-is | Σ converted (wrong) | portfolio_value |
|---|---|---|---|---|
| M44U | 2023 | **13,088,234,000** | 4,508,441,295 | 13,183,234,000 |
| N2IU | 2023 | **16,499,455,000** | 10,158,979,253 | 16,499,500,000 |
| C2PU | 2024 | **2,462,695,000** | 1,841,748,590 | 2,462,695,000 |
| K71U | 2024 | **9,531,621,000** | 8,895,740,192 | 9,531,621,000 |
| A17U | 2024 | 17,027,180,000 | 18,429,463,962 | 16,758,446,000 |
| ME8U | 2024/25 | 9,801,962,000 / 9,026,073,000 | 10,424,628,000 / 9,562,705,860 | 9,144,300,000 / 8,315,600,000 |

M44U is the proof: DB raw has FY2023 tagged across **8 currencies** (CNY 43, JPY 24, KRW 21, MYR 14,
AUD 14, VND 10, HKD 9, INR 3) — but `extracted/M44U.SI_FY2023/properties.json` is **187 of 187 rows
SGD**, and FY2024 is 180 of 180 SGD in the DB too. The tags were introduced downstream of extraction
on FY2023 only. Converting M44U would drop it from S$13.1bn to S$4.5bn.

### Group C — genuinely mixed within one REIT → re-extract

**J91U FY2024** — the 12.58× outlier. Σ converted = **4,951,576,810** vs `portfolio_value`
4,950,600,000 (0.02% apart). Its Australian and Japanese rows came from an *unaudited* front-of-book
**"PORTFOLIO DETAILS"** table quoted in **A$ million / JPY million**, while the audited *"Investment
Properties Portfolio Statements"* presents every property — Singapore, Australia, Japan — in one
**S$'000** column totalling S$4,949,573k. So a yen figure is being added to Singapore dollars.
Cross-check: audited Japan total S$499.191m × ~115.6 ≈ JPY 57.7bn = our stored JPY sum.

**Unresolved (partial coverage):** DCRU FY2024/2025, MXNU FY2024 (10 of 158 rows).

> **The rule: the same `market_valuation_currency` value means "native, convert me" for a
> foreign-presentation REIT and "already SGD, ignore me" for an SGD reporter. A single global
> conversion pass would fix ~9 REITs and corrupt ~8.**

The same `# Rule A: mv, pp already SGD` assumption also governs **1,351** `purchase_price` rows.

### `portfolio_value` itself is not one thing either

| REIT | what it matches |
|---|---|
| J69U FY2024 | audited Portfolio Statement total (JVs **excluded**, equity-accounted) |
| J69U FY2025 | headline *"aggregate appraised value"* **$8.2bn** (JVs **included**) |
| C38U, TS0U, ME8U | headline AUM on a **proportionate-interest** basis (*"Includes MIT's proportionate interest in the joint ventures"*) |
| J91U | audited SGD total |

**J69U changes basis between years** — so "which figure `portfolio_value` matches" is not stable for
the same REIT. And J69U's 1.65× gap has a second cause: NEX ($2,130m) and Waterway Point ($1,320m)
sit in our property table at 100% basis but are excluded from the audited statement entirely.

---

## 5. Identity 3 — DPU × units can never tally with the columns as defined

Two independent causes, both confirmed verbatim:

**High ratios (1.15–1.90) — `distribution_paid` holds cash paid, not declared.** AJBU FY2025: the AR's
*"Total amount available for distribution for the year"* is **$268,051k**; our `distribution_paid` is
**$133,531k**, the cash stream (0.819¢ tail of 2H24 + 5.133¢ 1H25 + 4.209¢ true-up). Same mechanism
verified for C2PU, ODBU, DCRU, J85; XZL is the same in reverse.

**Low ratios (0.92–0.96) — units basis.** Our `number_of_shareholder_units` is **year-end units in
issue** (K71U 4,013,867k = Note 17 closing), but ARs compute DPU on the **weighted average** for the
year. OXMU shows the widest gap: 1,339,055k weighted-average vs 1,437,458k year-end after an Oct-2025
placement.

**AJBU FY2025 reproduces on neither basis** — its DPU carries an ad-hoc pro-rata entitlement
adjustment for Preferential Offering Units issued 22 Oct 2025 (adjusted DPU excluding that effect =
10.629¢ vs reported 10.381¢).

A third basis dimension: **XZL and OXMU disclose before- and after-retention DPU pairs** (XZL 0.944¢
vs 0.850¢).

---

## 6. KPIs are individually correct but not mutually comparable

Every SGD-reporter value I checked matches its AR exactly — C38U 2.14 / 38.6% / 3.0y / 96.9%, K71U
1.28 / 47.9% / 4.4y / 96.7%, TS0U 0.56 / 38.5% / 2.2y / 95.4%, D5IU 0.0491 / 43.54% / 2.9y.
**The KPI block is sound.** But six fields carry different definitions under one name:

| KPI | the divergence |
|---|---|
| `weighted_average_lease_expiry` | TS0U/C38U **GRI**-weighted only; BTOU **NLA**-weighted only; AU8U and J69U disclose **both** and they differ (AU8U 2.1y GRI vs 2.6y NLA) |
| `aggregate_leverage` | MXNU's headline *"leverage"* is **net gearing** 40.7%; the Property Funds Appendix figure is **42.8%**. We store 42.8 — right, but not what the REIT highlights |
| `interest_coverage_ratio` | BTOU carries **two**: CIS-Code 1.7× and a facility-agreement *"Bank ICR"* with a 1.5× floor |
| `cost_of_debt` | BTOU **4.58%** excluding the Sponsor-Lender loan exit premium, **5.25%** including — same label |
| `portfolio_occupancy` | C38U/J69U/TS0U say *"**committed** occupancy"*; BTOU reports plain *"occupancy rate"* / *"same-store occupancy"* |
| as-at date | **J69U's FY ends 30 September** — its FY2025 KPIs are as at 30 Sep 2025, a different calendar point from the Dec-end REITs |

**`interest_coverage_ratio` is a multiple, never a percentage** — confirmed across C38U, J69U, TS0U,
AU8U, BTOU, MXNU, J85. J69U's definition: *"dividing the trailing 12 months' EBITDA (excl. FV changes
of derivatives and investment properties, and FX translation) by the trailing 12 months' interest
expense, borrowing-related fees and distributions on hybrid securities as defined in the CIS Code
issued by MAS"*. If it renders with `%`, 2.6× reads as a REIT about to default.

**MXNU's WALE 7.2y remains the largest pro-forma gap** — *"Before lease regear, WALE would have been
2.4 years"*; the regears were signed Feb 2026, after the balance date.

**NAV per unit has an inconsistent units basis**: K71U and C38U **exclude** units-to-be-issued (C38U:
*"Excludes management fees to be issued in units"*); TS0U and BTOU **include** them. K71U is the only
one with a genuine second line — *"Adjusted net asset value per Unit"* 1.27 vs balance-sheet 1.28,
*"excluding distribution to Unitholders"*. D5IU's S$0.0491 is verified genuine
(S$377,557k ÷ 7,696,809,979 units). One to chase: BTOU's AR divides by **1,835,124k** *"Units issued
and to be issued"* but we store 1,776,565,000 — looks like issued-only.

**REIT-level `gross_revenue` and `net_property_income` tie out exactly** — verified on C38U, J69U,
MXNU, ODBU FY2025, and `GR − property expenses = NPI` holds in all four. No bug at this level.

---

## 7. The normalization proposal

### N1 — Store native, convert at read time, and never convert a balance at a period rate

The single change that fixes Identity 2 and most of Identity 4.

```sql
-- every money column becomes a triple
<field>                numeric,   -- AS-DISCLOSED, in the REIT's presentation currency
<field>_currency       text,      -- MANDATORY, never inferred, never defaulted
-- plus one row-level anchor
fx_rate_to_sgd         numeric,   -- the rate used, stored explicitly
fx_rate_date           date       -- and its as-at date
```

Rules:
1. **Flows** (revenue, NPI, generated, cash paid, declared) convert at the **period's** rate.
2. **Balances** (opening, closing, portfolio_value, NAV, unit counts) convert at the rate of the
   **balance date they belong to** — and a closing balance and the next year's opening balance must
   use the **same** rate, since they are the same money. That alone restores Identity 2.
3. **Never** fall back to a row-level currency when a per-figure tag is missing. This is already
   causing damage: `build_final_tables.py` does `ccy = d.get(ccol) or d.get('currency')`, which
   converted a USD figure at the JPY rate in the transaction table. Make it raise.
4. Publish SGD as **derived columns** (`*_sgd`), keeping as-disclosed values authoritative.

### N2 — Fix `round()` at `build_final_tables.py:30` (P0, still outstanding)

```python
return round(float(value) * tbl[ccy]['SGD'])   # integer rounding
```

28 corrupted per-unit values in prod, 4 rounded to zero. Visible again in this pass: BTOU `nav=0`
(should be 0.24), MXNU `nav=1` (0.69), MXNU `dpu=5` (5.24). One-character fix → `round(x, 6)`.

### N3 — Split the two definitions currently sharing one column

| now | becomes |
|---|---|
| `distribution_paid` (cash on ~45 rows, declared on ~29) | `distribution_declared_for_year` **and** `distribution_cash_paid`, each with a single definition |
| `net_distributable_income` | `distributable_income_generated` — kills the cumulative-trap ambiguity |
| `distribution_pool_other_movements` | `distributable_income_retained` (negative) **+** `distributable_income_other_additions` (positive) |
| `adjusted_distributable_income` | `distributable_income_before_capital_distribution` **+** `distributable_income_fees_in_cash` |
| `number_of_shareholder_units` | keep (year-end) **+ add** `weighted_avg_units` — Identity 3 needs it |

### N4 — Add basis and period tags rather than normalizing values away

| tag | applies to | values |
|---|---|---|
| `portfolio_value_basis` | `portfolio_value` | `audited_statement` · `headline_proportionate` · `headline_incl_jv_100pct` |
| `wale_basis` | `weighted_average_lease_expiry` | `gri` · `nla` |
| `occupancy_basis` | `portfolio_occupancy` | `committed` · `physical` |
| `leverage_basis` | `aggregate_leverage` | `property_funds_appendix` · `net_gearing` |
| `kpi_as_at_date` | the KPI block | actual as-at date (J69U is 30 Sep, not 31 Dec) |
| `is_pro_forma` | any KPI | boolean — MXNU's WALE |

### N5 — Make the identities enforced checks, with each REIT's legitimate exemption recorded

| # | identity | scope |
|---|---|---|
| 1 | `A + B + O − P = E` | all rows where A/B/P/E are non-null; exempt the 4 structural-omission REITs |
| 2 | `closing(n) = opening(n+1)` | **in native currency**, and in SGD once N1 pins the rate |
| 3 | `DPU × weighted_avg_units ≈ declared` | needs N3's new fields |
| 4 | `portfolio_value ≈ Σ property valuations` | only within a matching `portfolio_value_basis`; never across bases |
| 5 | `Σ record.dpu = DPU` | needs the `basis` column on the flattened distribution table |
| 6 | payout ratio in 0–1.3 | already passes 74/74 |

Run them in `promote_final_to_prod.py` and refuse promotion on a new break.

---

## 8. Action order

**Data fixes, no decision needed:**
1. **N2** `round(x, 6)` — prod is serving DPU/NAV of 0 right now.
2. Backfill the 8 `distribution_pool_other_movements` values (§2) — every amount is already page-cited.
3. Backfill AW9U FY2024 `opening` = 12,906 and `closing` = 12,113.
4. Fix N2IU's 3 double-converted gains (raw `gain_currency` → SGD).
5. **Group B tag cleanup** — strip the spurious non-SGD `market_valuation_currency` tags from the
   SGD reporters (M44U FY2023 is the worst) **before** any conversion pass runs, or the conversion
   will corrupt them.
6. **Group A conversion** — apply FX to the genuinely-native property valuations.
7. **J91U FY2024** — re-extract AU/JP valuations from the audited SGD-only Portfolio Statement.
8. Make the currency fallback raise instead of defaulting (§7 N1.3).

**Needs a decision:**
9. N1 — store-native + convert-at-read. The big one; everything else is patching around it.
10. N3 — the column splits.
11. N4 — which basis tags are worth carrying.
12. Whether `portfolio_value` should be pinned to one basis (recommend: audited statement, with the
    headline as a separate `portfolio_value_headline`).
13. D5IU: nil distributions as `0` or `NULL`.

---

## 9. Verification note

Three agents verified ~25 reports here. Their citations were good, but across this and the earlier
`pct_basis` / `gross_revenue` / transaction work they produced **four false "no table exists"
findings** and **two mis-diagnosed root causes** — including the claim that M44U's 8-currency state
"does not exist", when it does exist in the DB for FY2023 while being absent from the extraction JSON
(both halves matter, and only checking both revealed that the tags are downstream). Every
load-bearing number above was re-checked by hand against the AR text or the raw table.

Our own `extracted/*/_notes.json` and the raw dev table repeatedly held the answer already. They
should be the first place checked.
