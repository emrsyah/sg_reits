# Re-extraction spec — sgx_reit_performance (distribution flow + units)

Repo: `C:\Users\emirsyah\orca\workspaces\s_reits\sgx-reit-performance`
Reports: `parsed_reports_datalab/<FOLDER>/full.md`

You are re-extracting from scratch. **Do NOT read `extracted/*/performance.json` first** — the whole
point is an independent second opinion. Read the annual report.

---

## Fields

| field | AR source | notes |
|---|---|---|
| `opening` | *"Amount/Income available for distribution at beginning of the year"* | null if the REIT has no pool |
| `income_for_year` | the **for-the-year subtotal** | see TRAP 1 |
| `other_additions` | *"Capital distribution"* / *"Distribution of other gains"* / *"Distribution top-up"* | **positive**. null if absent |
| `amount_retained` | *"Amount retained…"* / *"10% retention"* / *"Distribution withheld"* / *"…after retention"* | **positive magnitude**. see TRAP 3 |
| `distribution_paid` | *"Distributions to Unitholders **during the year**"* — the CASH total | see TRAP 2 |
| `closing` | *"…at end of the year"* | null if no pool |
| `distribution_declared` | the amount **declared in respect of this FY** | see TRAP 2. **null if genuinely not separately disclosed** |
| `dpu` | headline full-year DPU, in cents | as the AR states it |
| `units_in_issue` | units/stapled securities in issue at FY-end | **absolute units**, see TRAP 4 |
| `number_of_unitholders` | *"Statistics of Unitholdings"* total | a count of investors |
| `currency` | the AR's presentation currency | do NOT convert anything |

All money as **absolute values in the AR's own currency** (if the AR prints `$'000`, multiply by
1000). Never convert to SGD.

---

## TRAP 1 — the cumulative trap (most common error)

```
Amount available for distribution at beginning of the year   249,796
  ...build-up...
                                                             869,957   <- income_for_year  ✅
Amount available for distribution to Unitholders           1,119,753   <- opening+income   ❌
```

The signal is the phrase **"for the year"**. The unqualified *"Amount available for distribution"*
line is **cumulative** — using it double-counts the opening balance.

**If the AR prints no subtotal at all** (AJBU does this), derive it: `cumulative − opening`, and set
`income_for_year_derived: true`. Do not leave it null.

---

## TRAP 2 — `distribution_declared` vs `distribution_paid` (THE critical distinction)

This is the single biggest defect in our current data. **22 rows have the declared field defaulted to
the cash figure.** Do not repeat it.

| | meaning | where |
|---|---|---|
| `distribution_paid` | **CASH** that left during the FY. Often includes a **prior-year** tranche and excludes a current-year tranche paid after year-end | the tranche list inside the Distribution Statement |
| `distribution_declared` | the amount **declared in respect of this FY** — ties to the headline DPU | usually the **DPU note**, NOT the distribution statement |

Worked example, AJBU FY2025 — the statement's tranches total `133,531` (cash, includes a Nov–Dec
2024 tranche), but the DPU note on p144 gives *"Total amount available for distribution for the year
= 268,051"*. **Declared is 268,051, not 133,531.**

> **If you cannot find a separately disclosed declared figure, return `null` and say so in
> `declared_note`. DO NOT fall back to the cash figure.** A null is correct and useful; a wrong number
> is not. Some REITs (e.g. M44U) genuinely publish only one line — that is a real null.

---

## TRAP 3 — retention

Wording varies a lot: *"Amount retained"*, *"Amount retained for working capital"*, *"Less: Amount
retained for general corporate and working capital ("Retention")"*, *"Distribution withheld"*,
*"10% retention"*, or **only in a footnote**.

Some REITs (M1GU, OXMU) apply retention to the **opening** balance, not the closing — still record it.

Some disclose DPS **before and after retention** (XZL: 0.944¢ before, 0.850¢ after). Record the
**after-retention** figure as `dpu` and note the other.

**Known to have a 10% policy retention that we previously missed entirely: CY6U, UD1U, XZL.** If one
of these is in your batch, find the retention line.

> **Null means "not disclosed". Never write 0. Never compute it from a gap in the arithmetic.**

---

## TRAP 4 — units (colleague flagged nulls in production)

`units_in_issue` is currently **null on AW9U/2024, CMOU/2024, CMOU/2025, J91U/2024, TS0U/2024** —
and at least CMOU's figure IS in the report. Look harder than the previous pass did.

- Take it from **Note "Units in Issue"** or the balance sheet, at the FY-end date.
- **Scale:** most print `'000`; some (AJBU, D5IU, 8C8U) print actual units. Return `units_in_issue`
  as **absolute units** and state `units_scale` as printed.
- **Watch 4-column layouts**: `| 2025 units '000 | 2025 $'000 | 2024 units '000 | 2024 $'000 |`.
  MXNU's `342,989` is £'000, NOT a unit count.
- If the REIT reports *"Units in issue **and to be issued**"*, take that figure and set
  `units_basis: "issued_and_issuable"`; otherwise `"issued_only"`.

---

## TRAP 5 — the 5-year summary table

Many reports open with a 5-year summary. **Column order is NOT consistent between reports** — AW9U,
O5RU, AU8U, A17U run oldest-first; CRPU, HMN, XZL run newest-first.

Reading the leftmost column blind already produced one wrong figure in an earlier pass.

> **Take every number from the audited financial statements / the DPU note. Never from a summary
> table or a bar chart.** If you must use one, quote its column header to prove which year it is.

---

## TRAP 6 — structural archetypes (a null here is CORRECT)

- **No pool at all:** CY6U, UD1U, XZL — pure flow statements. `opening` and `closing` are
  legitimately null. Set `archetype: "no_pool"`.
- **Suspended:** D5IU (both years), BTOU (both years) — every distribution line is a dash.
  `dpu: 0`, `distribution_declared: 0`. Set `archetype: "suspended"`. This is a real finding.
- **Stapled trusts:** XZL, HMN, J85, Q5T, SET — *"Stapled Securityholders"*. Take the **Stapled
  Group** column and say so.

## TRAP 7 — the folder label is not always the financial year

`27_ME8U…_FY2022` = the AR for **declared FY2023**; ME8U/M44U/N2IU folders run **one behind**.
`02_O5RU…_FY2025` is a year ended **31 March 2026** whose columns are headed *2026*.
J69U and BUOU end **30 September**.

**Report `financial_year` as the DECLARED FY** (what the folder name says), and put the report's own
stated year-end in `fy_end_date`.

---

## Self-check BEFORE you return — run these two gates

```
GATE 1 (rollforward)   opening + income_for_year + other_additions
                         − amount_retained − distribution_paid  ==  closing

GATE 2 (declared)      distribution_declared
                         ==  income_for_year + other_additions − amount_retained
```

Report `gate1_pass` / `gate2_pass` (true / false / "n/a") and `gate_note`.

> **If a gate fails, go back and re-read the statement. A gate failure usually means a line was
> missed — most often the retention.**
>
> **NEVER adjust a number to make a gate pass.** Report the failure with the real figures. A failed
> gate that is honestly reported is far more valuable to me than a balanced one that is invented.
> If the AR genuinely does not balance, say so — that is a finding.

---

## Output

**Every field needs a citation.** I will re-check these mechanically against the file and I will
find it if you paraphrase, guess, or cite the wrong line.

Return STRICT JSON only, an array with one object per report:

```json
[{
  "symbol": "C38U", "financial_year": 2025, "fy_end_date": "2025-12-31",
  "currency": "SGD", "archetype": "rollforward",
  "opening": 249796000,            "opening_line": 5641,
  "income_for_year": 869957000,    "income_for_year_line": 5647,
  "income_for_year_derived": false,
  "other_additions": null,         "other_additions_line": null, "other_additions_label": null,
  "amount_retained": 9083000,      "amount_retained_line": 5656,
  "distribution_paid": 750125000,  "distribution_paid_line": 5655,
  "closing": 360545000,            "closing_line": 5657,
  "distribution_declared": 860874000, "distribution_declared_line": 7100,
  "declared_note": "from the DPU note, not the distribution statement",
  "dpu": 11.58,                    "dpu_line": 5658,
  "units_in_issue": 7611318000,    "units_in_issue_line": 7757, "units_scale": "thousands",
  "units_basis": "issued_only",
  "number_of_unitholders": 91421,  "number_of_unitholders_line": 8801,
  "quotes": {"income_for_year": "|  | 869,957 | 761,592 |", "amount_retained": "| Amount retained for general corporate and working capital purposes (Note B) | (9,083) | (9,381) |"},
  "gate1_pass": true, "gate2_pass": true, "gate_note": "",
  "flags": ["anything odd worth a human look"]
}]
```

Include a `quotes` entry for at least `income_for_year`, `distribution_declared`, `amount_retained`
and `units_in_issue` wherever non-null.
