# Transaction rebuild — results

Re-extraction of `sgx_reit_property_transaction` onto the agreed target schema
(`docs/7-30-2026-schema-review/transaction-target-schema-AGREED.md`), per the contract in
`_SPEC.md`.

**Nothing was written to any database.** Output is `txn_rebuild/<SYMBOL>_FY<YEAR>.json`, 58 files.

Run: 6 extraction agents (all 58 REIT-years, balanced ~34 transactions each), then 3 verification
agents on the rows that came back incomplete or suspect.

---

## 1. Output

```
files                                58
transactions                        208     (prod holds 206)
  acquisitions                       70
  divestments                       138

divestments with all five fields    118/138   86%     (prod equivalent: 67%)
missing reference_currency            0
missing citation                      0
reference_basis outside the enum      0
unparseable files                     0
```

| `reference_basis` | n |
|---|---|
| `valuation` | 93 |
| `book_value` | 21 |
| `purchase_price` | 4 |
| `net_identifiable_assets` | 2 |

| `pct_source` | n |
|---|---|
| `disclosed` | 73 |
| `derived` | 47 |

208 vs prod's 206: aggregate deals are emitted one row per property, so small count differences are
expected. Each delta should be confirmed intentional before any load.

---

## 2. Worked examples

### Ordinary asset sale — percentage stated by the report

```
sym   fy    property                          pct       src   reference_value  cur  basis
AJBU  2024  Intellicentre Campus (IC DC)   +35.40  disclosed     128,500,000  AUD  valuation
AJBU  2025  Kelsterbach Data Centre        +28.20  disclosed      39,000,000  EUR  valuation
HMN   2024  Citadines Karasuma-Gojo Kyoto  +40.10  disclosed   4,425,410,421  JPY  valuation
HMN   2024  Infini Garden                  +55.30  disclosed   8,177,720,542  JPY  valuation
ME8U  2025  2775 Northwoods Parkway        +18.60  disclosed       9,950,000  USD  valuation
```

Currencies are **native and tagged**. This is what prevents the silent mis-conversion that produced
the DCRU 770,936 artifact and the N2IU double-conversion in the current prod table.

### Derived — report gave a price and a reference but no percentage

```
A17U  2025  Parkside                       +44.81   derived      18,300,000  SGD  valuation
A17U  2024  21 Jalan Buroh                 +67.11   derived      67,500,000  SGD  book_value
```

### Partial stake — reference on the same interest basis as the price

```
C38U  2025  CapitaSpring - Serviced Res     +0.54   derived     125,325,000  SGD  int 0.45
CY6U  2025  20.2% stake in 3 data centres  +13.70  disclosed               -       int 0.202
```

### The rare bases — both now populated

```
ODBU  2024  Albany - Supermarket            +4.20  disclosed   22,900,000  USD  purchase_price
ODBU  2024  Hudson Valley Plaza            +17.50  disclosed   31,100,000  USD  purchase_price
N2IU  2025  Festival Walk Tower            -15.90  disclosed 2,331,900,000 HKD  purchase_price
AU8U  2024  CapitaMall Shuangjing           +7.86   derived   130,471,000  SGD  net_identifiable_assets
SET   2025  Slovakia portfolio (5 props)    +3.50  disclosed   67,700,000  EUR  net_identifiable_assets
```

AU8U's `+7.86%` on net identifiable assets reproduces the disclosed S$7,309k gain exactly — the
equity-sale case now works through the same three columns as everything else.

### Grouping

```
a17u:qld_trio:divestment:2024          3 rows, one deal-level +1.01% / 62,432,000
m44u:chee_wah_subang_1:divestment:2023 4 rows across 2 financial years
ts0u:lippo_plaza_shanghai:...:2024     FY2024 + FY2025, +14.86% both
odbu:albany_supermarket:...:2025       FY2024 + FY2025, +4.20% both
n2iu:mapletree_anson:divestment:2024   FY2023 + FY2024, +1.31% both
ud1u:illumina:divestment:2024          FY2024 + FY2025
o5ru:3_toh_tuck_link:divestment:2025   FY2024 + FY2025
```

`GROUP BY deal_id` and each deal counts once — fixing both the A17U triple-count and the cross-year
double-count that prod has no signal for today.

---

## 3. Verification pass — what changed

### T82U's mismatch was a mislabelled basis (fixed)

The prose says *"$58.3 million of strata units … divested at an **average price of 24.5% above book
value**"*, but **footnote 2** discloses the real denominator: an aggregate **independent valuation of
$47.1 million**, computed from per-sqm valuation rates × NLA.

```
58.3 / 47.1    - 1 = +23.8%   matches the disclosed 24.5%
58.3 / 34.402  - 1 = +69%     wrong denominator
```

The $34.402m covers only the **six units completed in FY2024**; the $58.3m covers **all seven** under
agreement, the seventh completing 6 Jan 2025 — a population mismatch, not an error.
Row corrected to `reference_value = 47,100,000 SGD`, `reference_basis` **relabelled to `valuation`**.

T82U FY2025 has the same character of gap (15.4/13.126 = 17.3% vs a disclosed 19.6%, because only one
of two units' carrying values is disclosed). Documented, not fixed.

### ME8U FY2025 recovered (was empty on a false premise)

A first-pass agent concluded no parsed report existed. It does — see §5.

```
2775 Northwoods Parkway   US$11.8m to Flexential LLC, 10 May 2025
                          +18.6% disclosed over JLL valuation US$9.95m
The Strategy / Synergy /  S$535.3m to Brookfield affiliates, 15 Aug 2025
  Woodlands Central       +2.6% disclosed over Savills valuation S$521.5m
```

Both disclosed, with named valuers, counterparties and completion dates.

**Note — two valid bases in one deal.** The Brookfield sale also discloses *+22.1% over original
investment cost of S$438.4m*. Valuation was stored as primary and the cost figure kept in `notes`.
This is the same pattern as C38U Bukit Panjang: a real deal where the report offers two defensible
references and a one-reference-per-row design must choose. Worth tracking how often it recurs.

### M44U `pct_source` — a wrong instruction, corrected

Two extraction agents were told M44U never discloses a premium, based on its divestments-table
headers. That was wrong: the **"Year in Review" timeline** states them explicitly. One agent
overrode the instruction and was right to.

Two FY2025 rows reclassified:

```
Subang 2          30.14 derived -> 31.0 disclosed   "a 31% premium to valuation"
28 Bilston Drive   7.14 derived ->  7.1 disclosed   "a 7.1% premium to valuation"
```

The other four FY2025 rows are confirmed genuinely derived — only portfolio-level averages exist for
them (*"six assets at 20% average premium to valuation"*).

FY2023 and FY2024 were already correct: 6 and 8 disclosed percentages respectively, sourced from the
Year in Review.

### N2IU FY2024 — wrong `source` metadata (fixed)

The `source` field named the FY25/26 report, which covers entirely different properties. The row
content (Mapletree Anson, S$4,006,000, p41) verifiably came from the right report. Metadata-only.

---

## 4. What remains incomplete — and why

Only **2 of 138** rows carry a percentage without a reference, both CY6U FY2025:

> *"divested at an enterprise value of INR 11,031 million (approximately S$161.7 million). The sale
> was executed at a **3% premium to their independent valuations**."*

The one candidate denominator available — the disposal group's carrying value of S$138.89m — was
tested and rejected: `161.7/138.89 − 1 = +16.4%`, not 3%. No per-property valuation table exists in
that report. **Left null, correctly**: a true statement about the disclosure, not a gap.

The remaining fully-null divestments are legitimate:

| rows | reason |
|---|---|
| XZL Hyatt ×3 (FY2024) | AR pools figures across hotels **and** across the ACRO-REIT/ACRO-BT sub-entities |
| AJBU Basis Bay ×2 | announced, not completed; no price disclosed yet |
| BUOU 28 German ×2 | IFRS-10 equity transaction; no P&L divestment |
| HMN Novotel Parramatta | the AR's own divestment table leaves the cells blank for this property |
| M44U FY2024 ×7 | prior-year divestments merely *named* in that report, no figures printed |
| O5RU 3 Toh Tuck Link | only a narrative premium; no valuation figure in the audited statements |

---

## 5. Parsed-folder year mapping (important, affects future work)

For the three Mapletree trusts the parsed folder label is **one declared-FY behind**:

```
28_M44U..._FY2022  =  AR "FY23/24"  (FYE 31 Mar 2024)  =  declared FY2023
28_M44U..._FY2023  =  AR "FY24/25"                     =  declared FY2024
28_M44U..._FY2024  =  AR "FY25/26"                     =  declared FY2025
```

Same for **ME8U** and **N2IU**. Verified from each folder's `meta.json` `file` field and the year each
report states for itself.

**O5RU and P40U are NOT offset** — their folder labels are correct declared FY (O5RU FY2024 =
*"financial year ended 31 March 2025"*). JYEU could not be resolved from its text; no JYEU
transactions were in scope.

All M44U/ME8U/N2IU rebuild files were confirmed built from the correct source. The offset caused one
false "no source exists" conclusion (ME8U FY2025) and one wrong metadata field (N2IU FY2024).

---

## 6. Cross-check against `sgx_reit_property`

Invariant tested: `reference_value ≈ sgx_reit_property.market_valuation × interest_pct` where
`reference_basis = valuation`, and against `purchase_price` where the basis is `purchase_price`.
Both sides normalised to SGD; property matched on its **last appearance** (a divested property is
removed in the year of sale).

```
TIES (<=2%)                        15
close (2-10%)                       4
MISMATCH (>10%)                    19
aggregate deal (deal-level ref)    25   not row-comparable by design
no property row (name match)       28   asset removed from the table
n/a (book_value / NIA / null ref)  43
property row lacks the figure       4
                                  ---
                                  138
```

### Most "mismatches" are a defect in the PROPERTY table, not the rebuild

```
M44U Aichi Miyoshi   ref 15,116,400 SGD   property   136,279 SGD   ratio 110.9  <- JPY/SGD rate
M44U Toki Centre     ref 19,740,240       property   177,964       ratio 110.9
M44U Celestica Hub   ref 12,705,000       property 3,610,942       ratio 3.518  <- MYR/SGD
M44U Linfox          ref 16,940,000       property 4,814,590       ratio 3.518
C2PU MOB Clinics      ref 5,800,000       property 1,854,690       ratio 3.127
```

**Those ratios are exchange rates.** The property rows hold values already in SGD but tagged
JPY/MYR/CNY, so normalising converts them a second time. This independently confirms the **Group B**
finding in `performance-normalization.md` — SGD reporters carrying spurious currency tags — from a
completely different direction, and now names M44U and C2PU specifically.

Two rows are the inverse (`AJBU Kelsterbach SGD/EUR`, `M44U Subang 2 SGD/MYR`): the property row is
tagged SGD where the rebuild correctly holds native currency per the AR.

### Genuine same-currency discrepancies to investigate

```
XZL  Hyatt Place Livonia  13,226,230  vs  13,868,280   0.954
M44U 31 Penjuru Lane       7,300,000  vs   7,800,000   0.936
BTOU Peachtree           171,298,940  vs 211,362,860   0.810
M44U 1 Genting Lane        9,100,000  vs  12,300,000   0.740
M44U 8 Tuas View Square    8,000,000  vs  11,180,000   0.716
```

The shape is consistent with a **valuation-date difference** — a deal valuation struck mid-year
against a 31 December portfolio figure — but 0.72–0.74 is large enough to warrant checking rather
than assuming.

### One join artifact

`T82U Suntec strata — 47,100,000 vs 3,282,874,000`: six strata units matched against the whole
Suntec City Office Towers property row. The join must exclude part-of-property rows.

### Verdict on the invariant

The concept works — **15 clean ties plus 4 near-ties out of 38 genuinely comparable rows** — but it
cannot be enforced as a gate until three things are done:

1. Fix the property table's spurious currency tags (Group B).
2. Exclude aggregate and part-of-property (strata) rows from the join.
3. Set a tolerance that accommodates valuation-date differences, or match on valuation date.

---

## 7. Next steps

**Before any load:**
1. Confirm each of the 2 extra rows vs prod's 206 is an intentional aggregate split, not a duplicate.
2. Decide the percentage unit — the whole database is moving to fraction (0–1); these files are
   `percent` with an explicit `pct_unit` tag, so conversion is unambiguous but must be applied.
3. Resolve the 5 same-currency cross-check discrepancies above.

**Separate workstreams this run has evidence for:**
4. Property-table currency tags (Group B) — now confirmed twice, independently.
5. `deal_id` promotion to prod, and deterministic slug generation.
