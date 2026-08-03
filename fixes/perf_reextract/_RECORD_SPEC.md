# Spec — restructure `distribution_record`

Repo: `C:\Users\emirsyah\orca\workspaces\s_reits\sgx-reit-performance`
Reports: `parsed_reports_datalab/<FOLDER>/full.md`

Extract the **distribution tranches** for each report. Read the annual report; do not copy from
`extracted/*/performance.json`.

---

## Output shape — per tranche

```jsonc
{
  "period_start": "2025-01-01",   // REAL DATE, ISO. Today this is free text in 3+ formats.
  "period_end":   "2025-06-30",
  "dpu":          5.133,          // cents, as printed
  "basis":        "accrual",      // accrual | cash_paid   <- NEW, the whole point
  "pay_date":     "2025-09-12",   // null if not stated
  "amount":       113729000       // dollar amount if the AR gives one, else null
}
// ex_date is DROPPED. Do not return it.
```

Also return `distribution_period_months` — the months of the reporting financial year that the
headline DPU covers. Normally 12. A stub year is different (8C8U listed Sep 2025 → ~3.2).

---

## `basis` — the field that matters

This is why the restructure exists. Today one array mixes two accounting worlds and
`sum(record) ≠ dpu` on 26 of 74 rows.

| value | meaning |
|---|---|
| `accrual` | the tranche is **in respect of this financial year**. It sums to the headline DPU |
| `cash_paid` | the tranche was **paid during this year but belongs to the PRIOR year** |

Worked examples:

```
AJBU FY2025   0.819c  28/11/2024 – 31/12/2024   -> cash_paid   (a FY2024 period)
              5.133c  01/01/2025 – 30/06/2025   -> accrual
              5.248c  01/07/2025 – 31/12/2025   -> accrual, declared 30 Jan 2026
              accrual sum = 5.133 + 5.248 = 10.381 = headline DPU  ✓

T82U FY2025   1.570c  01/10/2024 – 31/12/2024   -> cash_paid   (Q4 2024)
              then the four FY2025 quarters      -> accrual
```

**A tranche declared AFTER year-end but in respect of a period inside this financial year is
`accrual`** — include it. It usually appears in the Subsequent Events note, and it is often the
missing piece that makes the accrual sum reach the headline DPU.

**Self-check before returning:** `sum(dpu where basis = accrual)` should equal the headline DPU.
Report `accrual_sum`, `headline_dpu`, and `sum_matches` (true/false).

> If it does not match, **say so and leave it unmatched**. Do NOT invent a tranche, re-tag one, or
> adjust a rate to force it. An honestly reported mismatch is far more useful than a balanced lie.
> Explain what you think is missing in `record_note`.

---

## Traps

1. **Period is free text in at least three formats**: `'2025-01-01 to 2025-06-30'`,
   `'1 October 2024 to 31 March 2025'`, `'2H 2025 (1 Jul - 31 Dec 2025)'`. Convert all to ISO dates.
2. **Non-December year ends.** J69U and BUOU end 30 Sep; ME8U, M44U, N2IU, O5RU end 31 Mar; P40U and
   JYEU end 30 Jun. A "prior year" tranche is relative to *that* trust's year end, not December.
3. **Folder labels lie for ME8U, M44U, N2IU** — they run ONE YEAR BEHIND the declared FY
   (`27_ME8U..._FY2022` = declared FY2023, year ended 31 Mar 2024). Report `financial_year` as the
   DECLARED FY. JYEU's `_FY2024` folder is the year ended 30 Jun 2025 → declared FY2024. Same for P40U.
4. **Suspended trusts** — D5IU (both years) and BTOU (both years) declared nothing. Return an empty
   array `[]` with `record_note` explaining. That is a real finding, not a gap. CMOU FY2024 is also
   nil; CMOU FY2025 resumed at 0.25 US cents.
5. **A normal payment lag is not a defect** — HMN's 2H tranche pays 2026-02-27 for an in-year period.
   That is `accrual`, not `cash_paid`. Judge by the PERIOD, never by the pay date.
6. **Currency** — record `dpu` in the unit the AR prints (SGD cents, US cents, EUR cents, GBP pence).
   Do not convert. Note the currency.
7. **J91U completed a 10:1 unit consolidation in May 2025.** Its FY2024 tranche rates are
   pre-consolidation and FY2025 rates post-consolidation — do not sum across the two years.

---

## Rules

- **Every tranche needs a `line` number** pointing at the row you took it from.
- Null means not disclosed. Never write 0 for a missing value.
- Take tranches from the audited Distribution Statement and the Subsequent Events note. Do not use
  5-year summary tables — their column order is not consistent between reports.

## Output

WRITE to the file path given in your task prompt using the Write tool. Do NOT paste JSON in your reply.

```json
[{"symbol":"AJBU","financial_year":2025,"currency":"SGD",
  "distribution_period_months":12,
  "headline_dpu":10.381,"accrual_sum":10.381,"sum_matches":true,
  "distribution_record":[
    {"period_start":"2024-11-28","period_end":"2024-12-31","dpu":0.819,"basis":"cash_paid","pay_date":null,"amount":18091000,"line":5538},
    {"period_start":"2025-01-01","period_end":"2025-06-30","dpu":5.133,"basis":"accrual","pay_date":null,"amount":113729000,"line":5539}
  ],
  "record_note":"","flags":[]}]
```

Then reply with ONE line: `written, N rows, M with sum_matches=true`.
