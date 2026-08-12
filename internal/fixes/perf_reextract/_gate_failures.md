# Gate-failure investigation — 10 rows (2026-08-03)

Reports: `parsed_reports_datalab/<FOLDER>/full.md`. All line numbers refer to that file's `full.md`.

---

## GATE 2 — distribution_declared vs income_for_year + other_additions − amount_retained

### M1GU/2024 — VERDICT: CONFIRMED

Folder: `03_M1GU.SI_Alpha-Integrated-REIT_FY2024`

Distribution Statement (audited), lines 4949–4990:

```
4949 | Amount available for distribution to Unitholders at beginning of the year | 15,539
4950 | Amount retained for working capital | (3,994)(1)
4951 | Amount available for distribution to Unitholders at beginning of the year after retention | 11,545
4963 | Income available for distribution to Unitholders for the year before tax | 35,584
4964 | Tax expense | (584)
4965 | Income available for distribution to Unitholders for the year after tax | 35,000
4966 | Total amount available for distribution to Unitholders for the year | 46,545
```
`46,545 = 11,545 (opening after retention) + 35,000 (income after tax)` — confirms 3,994 is netted against the OPENING balance, not the current year's income.

```
4988 | Amount retained for working capital(2) | 3,403
4994 | (2) An amount of approximately $3,403,000 (2023: $3,271,000), before tax deductions, has been retained for working capital and pertains to distributions for the period from 1 January 2024 to 31 December 2024
```
Footnote (2) explicitly ties 3,403 to the calendar-year period, i.e. this is the deduction relevant to FY2024's declared distribution.

Reconciliation using the BEFORE-TAX income base and the FOR-THE-YEAR retention:
`35,584 − 3,403 = 32,181` vs. stated "Total distribution amount declared to Unitholders" of `32,177` (line 818) — a 4 (0.01%) residual, not the ~1,200 gap the 3,994/after-tax pairing produces.

FY2025 report (`03_M1GU.SI_Alpha-Integrated-REIT_FY2025`, lines 4375–4414) proves the pattern cleanly: retention "for the period" is disclosed as **nil** for 2025 (line 4411, footnote 2), and income before tax for the year is 39,713 (line 4389) — DPU-derived declared distribution for FY2025 is exactly 39,713 (1,125,055k units × 3.53c, lines 4412–4414), an exact match with zero retention.

**Conclusion:** the 3,994 (opening-balance retention, relates to 2H2023/1H2024 periods already settled) must NOT be used in the GATE 2 formula. Use income-BEFORE-TAX (35,584 for FY2024) and the FOR-THE-YEAR retention footnoted at 3,403 (FY2024) / nil (FY2025).

### M1GU/2025 — VERDICT: CONFIRMED (see above, same evidence)

`03_M1GU.SI_Alpha-Integrated-REIT_FY2025`, lines 4375–4414: opening retention is 1,546 (relates to 2H2024, already reflected in the FY2024 closing balance), current-year retention is nil, income before tax for the year is 39,713 — declared distribution exactly equals income before tax with no retention, confirming the same field-pairing rule as FY2024.

### ME8U/2024 — VERDICT: CONFIRMED

Folder: `27_ME8U.SI_Mapletree-Industrial-Trust_FY2024`

Financial Review (declared basis):
```
1447 | Distribution to Unitholders | 385,979 | 362,609 | (6.1)
```
Audited Distribution Statement (rollforward / paid basis):
```
6498 | Total Unitholders' distribution (including capital distribution) (Note B) | (370,206) | (385,455)
6537 | | (370,206) | (385,455)
```
`385,455` appears only in the audited rollforward as cash actually distributed during the financial year (straddles declaration periods, since one half-year's distribution is declared in one FY and paid in the next). `385,979` appears only in the narrative Financial Review as the amount **declared for the year**. The two figures come from different statements with different bases (declared-for-year vs. paid-in-year) — they are not meant to tie, and our stored value (385,979, declared basis) is the correct one for `distribution_declared`.

### P40U/2024 — VERDICT: CONFIRMED

Folder: `35_P40U.SI_Starhill-Global-REIT_FY2024` (offset reporter; "FY2024" = year ended 30 June 2025 per declared-FY convention; current column in this AR)

Financial Review note:
```
4279 | (1) Approximately S$4.0 million (FY 2023/24: S$2.6 million) of income available for distribution for FY 2024/25 has been retained for working capital requirements.
```
The audited Distribution Statement (lines 7261–7280) has **no line item for "amount retained" at all** — it is a pure opening/closing rollforward:
```
7268 | Income available for distribution at the beginning of the year | 97,301
7272 | Income available for distribution | 185,121
7277 | (distributions during the year) | (83,179)
7278 | Income available for distribution at the end of the year | 101,942
```
Retention is never isolated as a line item or exact number anywhere in either the Financial Review or the audited statements — only the rounded narrative "approximately S$4.0 million." The 4,035 figure (= Income available for distribution 87,820 − Income to be distributed 83,785, line 4270/4271) is a **derived** number, not a disclosed one. Confirmed: the AR genuinely does not print an exact retained figure.

---

## GATE 3 — sum(distribution_record.dpu) vs headline DPU

### A17U/2024 — VERDICT: CONFIRMED

Folder: `05_A17U.SI_CapitaLand-Ascendas-REIT_FY2024`. Statement of Movements in Unitholders' Funds, FY2024 column only shows:
```
5321 | Distribution of 7.524 cents per unit for the period from 01/01/24 to 30/06/24 | (330,829)
5322 | Distribution of 7.441 cents per unit for the period from 01/07/23 to 31/12/23 | (326,928)
```
No 2H2024 (Jul–Dec 2024) distribution line, and `Subsequent Events` note 32 (lines 8856–8862) discloses only a property acquisition and a unit issuance for a divestment fee — no distribution declaration. Grep for "7.681" and "01/07/24"/"1 July 2024 to 31 December 2024" in this file returns **no matches**. FY2024 headline DPU is 15.205 cents (line 735) = 7.524 + 7.681, but the 7.681 tranche (2H2024) is confirmed absent from the FY2024 AR entirely — it is declared in Feb 2025, after this AR's cutoff.

### A17U/2025 — VERDICT: CONFIRMED (with new finding)

Folder: `05_A17U.SI_CapitaLand-Ascendas-REIT_FY2025`. The 7.681 tranche does surface here, paid in FY2025:
```
5404 | Distribution of 7.681 cents per unit for the period from 01/07/24 to 31/12/24 | (338,005)
```
confirming it belongs to FY2024 entitlement but lands in the FY2025 cash-movement table (same mechanism as A17U/2024). For the missing FY2025 second half (7.528c, 1 Jul–31 Dec 2025): grepped "7.528" and "01/07/25" across the entire FY2025 `full.md` — **no matches anywhere**, not even in a subsequent-events note (the FY2025 AR has no equivalent late-breaking distribution announcement text at all, unlike FY2024's report which had none either — CLAR's AR is finalized before the 2H declaration each year). Confirmed: 7.528 appears nowhere in the FY2025 AR — not even as a subsequent event.

### DCRU/2024 — VERDICT: CONFIRMED

Folder: `13_DCRU.SI_Digital-Core-REIT_FY2024`. Only one tranche is in the FY2024 audited distribution statement:
```
5368 | Distribution of 3.58 (2023: 3.84) US cents per unit for the period from 1 July 2023 to 30 June 2024 (2023: 1 July 2022 to 30 June 2023) | (42,590) | (43,001)
```
This single payment straddles the calendar FY (half falls in 2023, half in 2024). The next tranche is only announced after year-end:
```
1099 | The current distribution of 1.80 U.S. cents for the period from 1 July 2024 to 31 December 2024 will be paid on or before 31 March 2025.
7543 | On 12 February 2025, the Manager announced a distribution of 1.80 US cents per Unit for the period from 1 July 2024 to 31 December 2024.
```
No quarterly or monthly DPU split is disclosed anywhere in the report (checked all Q1–Q4 references — all are portfolio/leasing stats, never DPU). There is no way, from this AR alone, to allocate the 3.58c straddling tranche between calendar-2023 and calendar-2024. Confirmed no split is possible from disclosed data.

### DCRU/2025 — VERDICT: CONFIRMED (same mechanism)

Folder: `13_DCRU.SI_Digital-Core-REIT_FY2025`, line 5555:
```
Distribution of 3.60 (2024: 3.58) US cents per unit for the period from 1 July 2024 to 30 June 2025 (2024: 1 July 2023 to 30 June 2024) | (46,779) | (42,590)
```
Same straddling-tranche structure repeats; line 1251 confirms the next (2H2025) tranche is again deferred to a post-year-end announcement. No split given.

### XZL/2024 — VERDICT: CONFIRMED (refutation attempt failed)

Folder: `01_XZL.SI_Acrophyte-Hospitality-Trust_FY2024`. Tried to find a 1H2024 rate via (a) a distribution-record/statement table with per-period cents, (b) any "period from 1 January 2024" or "0.747" text. Neither exists:
- No distribution-statement table with dated tranches exists in this AR at all (grepped "cents per Stapled Security for the period", "Distributions paid" — only one hit, the 2H figure below).
- Only figures disclosed: annual DPS before/after retention (lines 3285–3286: 1.772 / 1.595) and the post-year-end 2H tranche:
```
5967 | On 27 February 2025, the Managers approved a distribution of 0.848 US cents per Stapled Security for the period from 1 July 2024 to 31 December 2024 to be paid on 28 March 2025.
```
1H2024 (0.747 after retention, or 0.924 before) is never printed; it can only be derived by subtracting the disclosed 2H figure from the disclosed annual figure, which the task explicitly forbids presenting as disclosed. Confirmed: the two earlier agents' conclusion holds — 1H is never disclosed, only annual + 2H are.

### XZL/2025 — VERDICT: CONFIRMED (same mechanism)

Folder: `01_XZL.SI_Acrophyte-Hospitality-Trust_FY2025`. Same structure: annual DPS before/after retention (lines 3242–3243: 0.944 / 0.850) and only the 2H2025 tranche as a subsequent event:
```
5844 | Additionally, on 26 February 2026, the Managers approved a distribution of 0.418 US cents per Stapled Security for the period from 1 July 2025 to 31 December 2025 to be paid on 30 March 2026.
```
1H2025 (0.432) never appears anywhere in the FY2025 AR. Confirmed absent.

---

## Summary of verdicts

| Row | Verdict |
|---|---|
| M1GU/2024 | CONFIRMED |
| M1GU/2025 | CONFIRMED |
| ME8U/2024 | CONFIRMED |
| P40U/2024 | CONFIRMED |
| A17U/2024 | CONFIRMED |
| A17U/2025 | CONFIRMED |
| DCRU/2024 | CONFIRMED |
| DCRU/2025 | CONFIRMED |
| XZL/2024 | CONFIRMED |
| XZL/2025 | CONFIRMED |
