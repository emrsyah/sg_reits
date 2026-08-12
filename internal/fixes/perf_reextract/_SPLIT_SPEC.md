# Spec — split `income_for_year` from `other_additions`

Repo: `C:\Users\emirsyah\orca\workspaces\s_reits\sgx-reit-performance`
Reports: `parsed_reports_datalab/<FOLDER>/full.md`

Everything you need is in the **Distribution Statement** (sometimes "Statement of Distribution" or
"Statements of Distributable Income"). Read the AR; do not copy from `extracted/` or `fixes/`.

---

## What we are separating, and why

The distribution statement builds this year's distributable income out of two very different kinds of
line. We want them apart so a reader can tell **how much of a REIT's payout came from running its
properties, and how much came from something else**.

```
income_for_year   OPERATING     what the properties earned, after tax and non-cash adjustments
other_additions   NON-OPERATING capital distributions, divestment gains, JV distributions,
                                tax-exempt income, released retentions
```

## OPERATING — goes into `income_for_year`

Typically the first block of the statement:

- `Total return attributable to Unitholders` / `Profit after tax attributable to Unitholders`
- `Net tax and other adjustments` / `Distribution adjustments` (the non-cash add-back block —
  management fees paid in units, depreciation, amortisation, fair-value reversals, straight-lining)

## NON-OPERATING — goes into `other_additions`

Any separately named line of this kind, **wherever it sits in the statement**:

- `Tax-exempt income`
- `Capital distribution` / `Capital distributions`
- `Distribution income from joint ventures`
- `Distribution of gains from divestment` / `Distribution of other gains`
- `Distribution top-up`
- `Amount released` (a PRIOR-year retention released back into the pool)

> **Position does not matter.** Some REITs put these ABOVE the distributable-income subtotal (C38U),
> others BELOW it (BUOU). Classify by what the line IS, not where it sits. This is the whole point of
> the exercise.

---

## Worked example — C38U FY2025

```
Total return attributable to Unitholders            937,287   } operating
Net tax and other adjustments (Note A)             (143,751)  }
Tax-exempt income                                     7,885   } non-operating
Capital distributions                                16,208   }
Distribution income from joint ventures              52,328   }
                                                    869,957   <- the AR's subtotal
```

```
income_for_year   =  937,287 − 143,751            =  793,536
other_additions   =  7,885 + 16,208 + 52,328      =   76,421
                                          check:      869,957  = the printed subtotal
```

## Worked example — BUOU FY2024 (already in this shape)

```
Income available for distribution to Unitholders    210,337   <- income_for_year
Capital distribution (Note B)                        45,178   <- other_additions
Distributable income                                255,515   <- subtotal
```

---

## MANDATORY self-check

```
income_for_year + other_additions = the AR's distributable-income subtotal
```

If your two numbers do not add back to the printed subtotal, **you have mis-split something**.
Report `subtotal_printed`, `split_sum`, and `split_matches` (true/false).

> Both figures must be built from **printed lines only**. Never derive one by subtracting from the
> other, and never invent a line. If the statement gives no non-operating lines at all, then
> `other_additions` is **null** and `income_for_year` is simply the printed subtotal — that is the
> common case.

---

## Traps

1. **Do not confuse the CUMULATIVE line.** *"Amount available for distribution"* (unqualified) is
   often `opening + income` and is NOT the subtotal you want. The one you want is the for-the-year
   figure, usually just above it. C38U prints `869,957` then `1,119,753` — the second is cumulative.
2. **Some statements print NO subtotal at all** (AJBU). Then `income_for_year + other_additions`
   must equal `cumulative − opening`. Say so in `note`.
3. **Perpetual securities / CPPU / non-controlling interests** are deducted BEFORE the unitholder
   figure. They are not additions and not retentions — leave them inside the operating block.
4. **`Amount retained` is NOT in scope here** — it is already extracted and must not be double-counted
   into either field. Ignore retention lines entirely, except: if a retention is deducted INSIDE the
   operating block, report `retention_inside_operating: true` so we know the operating figure is net.
5. **Folder labels lie for ME8U, M44U, N2IU** — they run ONE YEAR BEHIND the declared FY
   (`27_ME8U..._FY2022` = declared FY2023, year ended 31 Mar 2024). JYEU `_FY2024` = year ended
   30 Jun 2025. P40U `_FY2024` = year ended 30 Jun 2025. Report `financial_year` as the DECLARED FY.
6. **Suspended trusts** (D5IU x2, BTOU x2) and CMOU/2024 declared nothing — report what the statement
   shows and mark `note`. Zero is fine there if the AR prints a dash or nil.
7. **Currency** — report figures in the AR's own presentation currency and state which. Do not convert.

---

## Output

WRITE to the file path in your task prompt using the Write tool. Do NOT paste JSON in your reply.

```json
[{"symbol":"C38U","financial_year":2025,"currency":"SGD",
  "income_for_year":793536000,"income_for_year_lines":[5642,5643],
  "other_additions":76421000,
  "other_additions_breakdown":[
    {"label":"Tax-exempt income","amount":7885000,"line":5644},
    {"label":"Capital distributions","amount":16208000,"line":5645},
    {"label":"Distribution income from joint ventures","amount":52328000,"line":5646}
  ],
  "subtotal_printed":869957000,"subtotal_line":5647,
  "split_sum":869957000,"split_matches":true,
  "retention_inside_operating":false,
  "quotes":{"income_for_year":"...","subtotal":"..."},
  "note":"","flags":[]}]
```

Then reply with ONE line: `written, N rows, M with split_matches=true, K with other_additions`.
