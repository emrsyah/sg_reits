# `sgx_reit_performance` — full re-extraction, all 74 rows

Run 2026-08-03. Six sub-agents plus one follow-up re-extracted the distribution flow **from scratch**
against `parsed_reports_datalab/`, forbidden from reading `extracted/*/performance.json` first so the
result is an independent second opinion. Extraction contract:
`PERF_EXTRACT_SPEC.md` (7 traps, 2 self-check gates, mandatory line citations).

Every figure was then re-checked mechanically against the cited line in `full.md`, and both gates were
re-run by us rather than trusted from the agents' own reports.

---

## 1. Headline

```
74 / 74 rows re-extracted

GATE 1  rollforward   63 / 63 pass    0 fail    11 n/a (no_pool + suspended)
GATE 2  declared      37 / 43 pass    6 fail    31 n/a (26 declared null + 5 nil)

units_in_issue null    5  ->  0
amount_retained        24 (conflated)  ->  28 (separated)
other_additions                        ->  14
distribution_declared null             ->  26
```

**The rollforward now closes on every single row where a pool exists.** Zero failures.

---

## 2. The colleague's complaint — resolved, 5 of 5

`number_of_shareholder_units` was null on five rows in production. **None of them was missing from the
annual report.** All five were extraction failures:

| row | now | source |
|---|---|---|
| CMOU/2024 | 1,044,450,000 | Note 13 *"UNITS IN ISSUE"* + balance sheet |
| CMOU/2025 | 1,044,450,000 | Note 13, *"As at 1 January / 31 December"* |
| AW9U/2024 | 2,094,447,000 | Note 16, corroborated on the balance sheet |
| J91U/2024 | 8,049,164,000 | stated **three times** — Note 18, balance sheet, 5-year summary |
| TS0U/2024 | 5,500,064,000 | Note 15 *"Units in issue and to be issued"* |

`units_in_issue` is now **100% populated**.

AW9U/2024 also recovered `opening`, `closing` and `distribution_paid`, all previously null.

> **Correction to an earlier note in this repo:** AW9U's `2,111,058` is the **weighted average** units
> from the EPU note, *not* units in issue. Units in issue at FY2024 year-end is `2,110,969,000`. An
> earlier instruction of ours conflated the two; the agent caught it.

---

## 3. Retention has THREE placements, not one

This is the most important structural finding of the run, and it was not known before.

| placement | REITs | effect on the gate |
|---|---|---|
| **After** the for-the-year subtotal | C38U, CY6U, UD1U, OXMU, MXNU, CRPU, XZL… | subtract it |
| **Inside** the build-up producing the subtotal | **TS0U ×2, C2PU ×2, P40U** | **already deducted — do NOT subtract again** |
| Against the **opening balance** | **M1GU** | does not reduce the year's declared amount at all |

Proof for the middle case — TS0U FY2024 closes **without** subtracting retention:

```
60,813 + 108,660 + 5,000 − 108,211 = 66,262 = closing
```

And OXMU proves the first case in the same run — its agent states the retention *"is a SEPARATE line
printed AFTER the subtotal … so subtracting it is correct and does not double-count (unlike
TS0U/C2PU)."*

> **Schema consequence: `income_for_year` alone is ambiguous.** The same column means pre-retention on
> some REITs and post-retention on others. Either add a `retention_in_subtotal` boolean, or normalise
> every row to pre-retention. **This must be decided before load** — with retention placement
> respected the rollforward is 63/63; without it, 5 rows fail for no real reason.

Note the old extraction stored the **pre-retention** figure (TS0U/2024 `113,660` vs the printed
`108,660`; C2PU/2024 `94,419` vs `91,419`), so the two passes are on different conventions.

---

## 4. `distribution_declared` — the cash-in-declared defect, quantified

Confirmed defects, each with the corrected value and an AR citation:

| row | was (cash) | now (declared) | corroboration |
|---|---|---|---|
| AJBU/2025 | 133,531,000 | **268,051,000** | DPU note p144 |
| AJBU/2024 | *null* | **172,733,000** | DPU note |
| C2PU/2025 | 65,436,000 | **99,781,000** | *"Income for the year available for distribution"* |
| BUOU/2024 | 262,580,000 | **255,515,000** | *"Distributable income"* line |
| BUOU/2025 | 237,992,000 | **224,654,000** | same line |
| T82U/2025 | 191,186,000 | **207,280,000** | narrative *"total distributable income of $207.3 million"* |
| T82U/2024 | 189,148,000 | **180,923,000** | narrative *"$180.9 million"* |
| J91U/2024 | 177,424,000 | **164,064,000** | Note 25(c) |
| J85/2024 | 71,293,000 | **66,850,000** | *"Total distribution (after retention for working capital)"* |
| A17U/2024 | *null* | **668,833,000** | — |
| M1GU ×2, K71U ×2, JYEU, P40U, ME8U ×2 | — | recovered from Financial Highlights / narrative | |

### 26 of 74 rows have a genuinely null `distribution_declared`

M44U (3 years), N2IU (3 years), DCRU ×2, DHLU ×2, MXNU ×2, Q5T ×2, AW9U ×2, ODBU ×2, SET ×2, AU8U,
OXMU ×2 and others **do not publish a declared dollar amount at all** — only a per-unit rate, with the
final tranche declared after year-end.

The agents refused to fall back to the cash figure on every one of them. ODBU spelled out why:

> implied declared ≈ 26.4m vs distributable income 26.9m — *"they are genuinely not the same number
> and I have not invented one."*

**A null here is the correct answer.** Any pipeline that back-fills it from cash recreates the exact
defect this run was built to find.

---

## 5. Retention found where we previously had nothing

```
CY6U/2024   10,149,000     "10% retention"
CY6U/2025   11,885,000     "10% retention"
UD1U/2024    2,841,000     "Amount retained for working capital"  = exactly 10.0% of income
UD1U/2025    1,629,000     = exactly 10.0% of income
P40U/2024    4,000,000     footnote only, not a statement line
CRPU ×2      7,385/8,457   "for the principal amortisation of onshore loans and capital expenditures"
CMOU/2024   47,627,000     "Distribution withheld" — the ENTIRE year's income
```

CY6U's arithmetic is exact: `118,853 − 11,885 = 106,968` = declared.

CMOU is a distinct archetype: not a silent suspension but an explicitly **named** withholding line, so
it is real retention, not an inferred gap.

---

## 6. Warnings from the old docs that were confirmed correct

- **K71U's ~108m "retention" is not retention.** Confirmed: it is the standing pool created by paying
  each half-year tranche one period in arrears. The AR states *"Keppel REIT has distributed 100% of its
  taxable income available for distribution."* Gate 2 passes cleanly with `amount_retained` null.
  **Had we plugged that gap we would have published a false claim.**
- **BTOU's *"Income Available for Distribution per Unit 1.44 US cents"* is not a DPU.** Stored as 0.
- **8C8U's stub period is real**, not a bug.

---

## 7. The 6 remaining gate-2 failures — all reported honestly, none balanced

| row | error | status |
|---|---|---|
| P40U/2024 | −4.59% | AR discloses *"approximately S$4.0 million"*; exact implied 4,035. Agent recorded the **disclosed** figure, not the residual |
| M1GU/2025 | +4.07% | declared 39,715 ≈ income 39,709 — retention applied to the **opening** balance, so it does not reduce the year |
| M1GU/2024 | +3.78% | **matches on neither basis.** Genuine anomaly, needs a human |
| ME8U/2024 | −3.86% | no retention line exists; agent re-read twice and refused to back-solve |
| ME8U/2023 | −0.57% | same |
| J69U/2024 | +0.51% | explained by footnote — S$1,092,000 of FY23-retained tax-exempt income released in FY24 |

**Not one number was adjusted to make a gate pass.** That was the instruction and it held.

---

## 8. Citation audit

11 of ~500 cited figures did not sit at their cited line. **All 11 are explainable, none is an agent
error** — our checker demands a single line, which cannot exist for:

- **derived** values — AJBU, AW9U, JYEU, T82U, O5RU `income_for_year` (no subtotal is printed)
- **composite** values — DHLU `distribution_paid` (sum of two tranche lines), J91U `other_additions`
  (tax-exempt income + capital distribution)
- **narrative** sources — C38U declared, cited to *"S$860.9 million"* where the exact figure is 860,874

---

## 9. Traps the agents caught that we had not documented

- **SET FY2024 changes presentation between years.** Its FY2024 report labels `123,980` *"Income
  available for distribution"* — but it is **cumulative**; the FY2025 report restates the same year as
  `79,328`. Reading the FY2024 label at face value double-counts the opening balance by 44,652.
- **CRPU's distribution statement is on a *declaration* basis, not cash** — so its `77,208` is the
  declared figure, and the true cash figure is never printed.
- **DCRU and ODBU omit the cumulative line**, the opposite of the usual layout — their bare *"Amount
  available for distribution"* IS the for-the-year subtotal. Verified arithmetically both ways.
- **J91U has no opening balance in any year** and never carries its closing residual forward; it also
  deducts only part of the cash paid inside the statement. Its rollforward cannot close by construction.
- **ME8U retained S$29.8m via the Distribution Reinvestment Plan.** Unitholders received the full
  declared distribution — in units, not cash. Correctly **not** recorded as retention, but the schema
  has nowhere to put it. **Open question.**
- **D5IU's register shows 16.7bn units at Mar 2026 vs 7.7bn at FY-end** — a post-year-end issuance.
  The audited FY-end figure was used. Flagged for a human.

---

## 10. Open decisions

> **SUPERSEDED 2026-08-03 by `performance-open-issues.md`.** An adversarial verification pass
> refuted four of the items below. In particular M1GU/2024 and the ME8U residues are **our data
> bugs**, not AR gaps, and the J91U "cash conflict" was a parse artefact. Read that document
> instead; the list below is kept only for history.


1. **`income_for_year` convention** — as-printed plus a `retention_in_subtotal` flag, or normalise
   every row to pre-retention. **Blocks load.** Recommend the flag, per the as-disclosed invariant.
2. **M1GU/2024** — reconciles on no basis. Needs a human read.
3. **DRP scrip retention (ME8U S$29.8m)** — a real economic event with no home in the schema.
4. **ME8U's two unexplained residuals** (2,179 and 15,485) — accept as disclosed, or investigate.

---

## Provenance

Raw re-extraction output: `batch1.json` … `batch6.json` + `batch5b_oxmu.json` in the session
scratchpad. Gates and citation checks were re-run independently by
`verify_perf.py`; the agents' own gate claims were **not** taken on trust.

**Nothing has been written to dev or prod.**
