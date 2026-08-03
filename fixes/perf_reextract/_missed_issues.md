# Missed issues — independent sweep of `fixes/perf_reextract/batch*.json` (74 rows)

Fresh-eyes pass. Everything below was verified against `parsed_reports_datalab/<FOLDER>/full.md`
with a line number. Items already on the known-issues list are excluded.

Legend: **[AR]** = real feature of the annual report, **[EXTR]** = our extraction is wrong or incomplete.

---

## 1. 8C8U/2025 is a **141-day stub financial period**, and its DPU covers only 98 days — **[AR]**

**Rows:** `8C8U / 2025`

The audited statements are headed *"FOR THE FINANCIAL PERIOD FROM 12 AUGUST 2025 (DATE OF
CONSTITUTION) TO 31 DECEMBER 2025"* — `11_8C8U…_FY2025/full.md:3277` (and 3293, 3409, 3439, 3493,
3526, 3560, 3583, 3619, 3642, 5039, 5449).

The DPU is narrower still:

> line 341: *"a DPU of 1.739 Singapore cents **for the period from listing to 31 December 2025**,
> exceeding the IPO forecast of 1.630 Singapore cents by 6.7%"*
> line 1811: *"after annualising the results for the **98-day period from 25 September 2025 to
> 31 December 2025**"*

Consequences for the stored row:
- `income_for_year = 29,995,000` is a 141-day figure, not an annual one.
- `dpu = 1.739` is a 98-day figure. Annualised it is ~6.5c. Any yield, payout-ratio or YoY-growth
  calculation that treats it as a full year is wrong by ~4x.
- The `1.630` comparative at line 1794 is the **IPO forecast**, not a prior year — do not let it leak
  into a time series.
- `distribution_paid = 0` is correct (first distribution falls after year-end).

**Action:** this row needs a period-length / stub flag. It is not an extraction error, but it is the
single most misleading row in the set if consumed as annual.

---

## 1b. D5IU/2025: a **9,005,267,676-unit rights issue** completed 26 Jan 2026 more than doubles the unit base days after the FY cut — **[AR]**

**Row:** `D5IU / 2025` (`units_in_issue = 7,696,809,979`)

`25_D5IU…_FY2025/full.md:1363`:
> *"Upon the approval of the unitholders during an Extraordinary General Meeting held on 8 December
> 2025, the Trust launched a renounceable and non-underwritten rights issue … of **up to
> 9,005,267,676 new units at an issue price of S\$0.007 per unit**. The Rights Issue was **completed
> on 26 January 2026** and the Trust raised approximately S\$63.0 million…"*

The stored FY-end count (7,696,809,979) is correct as at 31 Dec 2025, but the base goes to ~16.7bn
weeks later — a **117-for-100 issue at S$0.007**, i.e. massively dilutive. Any NAV-per-unit or
forward-DPU figure carried off this row is stale on arrival. The same paragraph confirms
distributions remain withheld (*"will adopt a prudent approach by withholding distributions to
Unitholders and perpetual securities holders until there is sustained improvement"*), consistent
with our `suspended` archetype. Also renamed (Lippo Malls → Landmark REIT) effective 27 Mar 2026.

---

## 1c. K71U/2025: the **DPU denominator includes units issued *after* the year end** — **[AR]**

**Row:** `K71U / 2025` (`dpu = 5.23`, `units_in_issue = 4,013,867,000`, `distribution_declared = 212,406,000`)

`23_K71U…_FY2025/full.md:3691`:
> *"**DPU calculated is inclusive of the new Units issued on 19 January 2026** pursuant to the
> Preferential Offering. These new Units have the right to the distributable income from **17 October
> 2025 to 31 December 2025**."*

So the FY2025 DPU is struck on a base that does not exist at any point during FY2025, and it is
stitched across a 17 Oct 2025 private placement. This is **distinct from** the known
"register unit count differs from audited FY-end count" item — that one is about *which* count we
stored; this one is about the DPU denominator being a *post-balance-sheet* number. It explains why
K71U/2025 shows `dpu × units = 209.9m` against `distribution_paid = 276.6m`. Do not reconcile
K71U's DPU against `units_in_issue`: `5.23c × 4,013,867,000 = 209.9m` against a `distribution_paid`
of 276.6m and a `distribution_declared` of 212.4m — the residual is the post-year-end units, not an
extraction error.

---

## 2. `distribution_paid` is **not all cash** — Distribution Reinvestment Plans settle part of it in units — **[AR]**

The spec defines `distribution_paid` as *"the **CASH** total"*. For at least six trusts a material
slice was settled by issuing new units. Only ME8U's DRP is on the known list.

| symbol / row | non-cash portion | our `distribution_paid` | share | evidence |
|---|---|---|---|---|
| M1GU / 2024 | S$4,880,000 (13,266,912 units @ $0.3678) | 27,862,000 | **17.5%** | `03_M1GU…_FY2024/full.md:4992`, 5191, 6219 |
| M44U / 2024 (YE 31 Mar 2025) | S$40,626,000 (31,126,603 units) | 417,743,000 | **9.7%** | `28_M44U…_FY2024/full.md:8084` + units-movement row at :8078 (*"Distribution Reinvestment Plan … 31,127"* in the 2025 column) |
| ODBU / 2025 | US$3.3m + US$4.0m = **US$7.3m** | see row | ~28% | `39_ODBU…_FY2025/full.md:6177`; equity row *"Issue of new Units for DRP … 7,333"* at :6048 |
| ODBU / 2024 | US$0.8m + US$2.6m = **US$3.4m** | see row | ~14% | `39_ODBU…_FY2024/full.md:7018–7021` (1,777,917 @ $0.456 and 6,244,290 @ $0.420); equity row *"…DRP … 3,434"* at :5803 |
| MXNU / 2024, 2025 | DRP applied to the FY's distributions | — | — | `14_MXNU…_FY2024/full.md:6741`, `…FY2025/full.md:5890` |
| JYEU / 2024 | 26.4m new units | — | — | `24_JYEU…_FY2024/full.md:2258` |

Verbatim, M1GU line 4992:
> *"13,266,912 Units (2023: 15,667,005 Units) amounting to approximately \$4,880,000 (2023:
> \$6,427,000) **were issued by the Trust as part payment of distributions** … pursuant to the
> Distribution Reinvestment Plan."*

**Why it matters:** anyone using `distribution_paid` as a cash-outflow proxy (payout ratio, cash
coverage, FCF bridge) is overstating cash out by up to ~28%. It also partly explains the unit-count
growth between years, so DPU-times-units reconciliations drift.

**Action:** either add a `distribution_paid_non_cash` field or a `drp_active` flag. Not an
extraction error — the numbers we stored match the statement — but the field's stated meaning is
wrong for these rows.

---

## 3. AJBU: `dpu × units_in_issue` overshoots `distribution_declared` by 21% — weighted-average base + an advance-distribution stub — **[AR]**

**Rows:** `AJBU / 2024` (and `AJBU / 2025`, 5.5%)

- FY2024: `9.451c × 2,209,075,362 = 208,780,000` vs stored `distribution_declared = 172,733,000`
  (`21_AJBU…_FY2024/full.md:7930`, *"Total amount available for distribution for the year | 172,733"*).
  Implied unit base = 1,827,671,675 — i.e. a **weighted average**, not the FY-end count.
- Cause: a private placement. `…FY2024/full.md:7735` note b: *"Pursuant to the private placement
  announced on 19 November 2024, the Trust issued **334,929,000 new Units** at an issue price of
  \$2.090. The new Units were listed on 28 November 2024."* Units go 1,721,429,811 → 2,209,075,362
  in the year (line 7730).
- Related, and **not on the known list**: AJBU's last FY2024 tranche is a stub —
  `…FY2024/full.md:6371`: *"Distribution of 4.083 cents per Unit for the period from **1/7/2024 to
  27/11/2024** | (70,462)"* — an advance distribution cut off at the placement books-closure date.
  Same class of artefact as the known Q5T/2025 stub, but a different trust and a different year.

**Action:** do **not** derive or validate AJBU's DPU from `declared / units_in_issue`. Flag AJBU/2024
as a placement year.

---

## 3b. J91U's two DPU rows sit on **different unit bases** — the FY2025 report restates FY2024's DPU as 21.190, we store 2.119 — **[AR → our series is broken]**

**Rows:** `J91U / 2024` (dpu 2.119), `J91U / 2025` (dpu 21.914)

The 10:1 consolidation itself is on the known list, but this specific consequence is not. The FY2025
report explicitly restates the prior year:

> `15_J91U…_FY2025/full.md:2463` — *"FY2025 DPU of **21.914 cents** was **3.4% higher than the FY2024
> DPU of 21.190 cents** due to the higher amount available for distribution to Unitholders, partially
> offset by the higher applicable number of ESR-REIT units subsequent to the preferential offering
> completed in 4Q2024…"*

We store `2.119` for FY2024 (the as-reported, pre-consolidation figure) and `21.914` for FY2025
(post-consolidation). Read as a series that is **+934% DPU growth**. The true comparison is
21.190 → 21.914, i.e. **+3.4%**. Both stored values are individually faithful to their own report,
so this is not an extraction error — but the series is unusable until FY2024 carries a
`dpu_restated = 21.190` or a units-basis flag.

Also on J91U/2024, and not on the known list: another advance-distribution stub —
`…FY2024/full.md:2123`: *"Pursuant to the preferential offering which was completed on 11 November
2024, **an advanced distribution for the period from 1 July 2024 to 10 November 2024** was paid on
8 January 2025."*

---

## 4. OXMU changed its **distribution payout policy three times inside FY2025**, and `amount_retained` means something different for OXMU than for everyone else — **[AR]**

**Rows:** `OXMU / 2024`, `OXMU / 2025`

`33_OXMU…_FY2025/full.md:275`:
> *"Total FY2025 DPU comprised the first half FY2025 DPU at **10% payout** of 0.12 US cents, an
> **advanced distribution at 50% payout** of 0.24 US cents per unit for the period from **1 July 2025
> to 5 October 2025**, and a final distribution at **65% payout** of 0.25 US cents per unit for the
> period from 6 October 2025 to 31 December 2025."*

(corroborated at :356 and :629; the stub tranche appears in the audited statement at :5102, and
:621 confirms *"An advanced distribution was paid to eligible Unitholders on 14 November 2025."*)

Consequences:
- OXMU's `amount_retained` — 34,237,000 in FY2024 (**90%** of `income_for_year` 38,175,000, line
  5463) and 20,423,000 in FY2025 (**71%** of 28,726,000, line 5095) — is a **payout-ratio
  set-aside**, not the ~5–10% working-capital retention that the same field means for every other
  trust in the set. Aggregating or averaging `amount_retained` across REITs is meaningless because
  of this.
- The DPU jump 0.29c → 0.61c (+110%) that shows up in the sanity sweep is a **policy change**, not
  earnings growth — `income_for_year` actually *fell* 38,175 → 28,726.
- The FY2025 distribution stream is split across three different payout regimes and includes a
  ~3-month stub period, so OXMU/2025 is not comparable to OXMU/2024 on any per-unit measure.

---

## 4b. CMOU is a **third suspended-distribution trust** and is not archetyped as one — **[AR + EXTR]**

**Rows:** `CMOU / 2024` (dpu 0, declared 0), `CMOU / 2025` (dpu 0.25 — partial resumption)

The known list names only D5IU and BTOU as suspended. CMOU (KORE US REIT, formerly Keppel Pacific
Oak US REIT) suspended distributions too, under a Recapitalisation Plan:

> `22_CMOU…_FY2025/full.md:199` — *"Pursuant to the **Recapitalisation Plan announced on 15 February
> 2024**, KORE **temporarily suspended distributions** for the period starting 2H 2023 through to the
> 2H 2025 distribution that would otherwise be paid in 1H 2026."*
> :179 — *"**Early resumption of distributions in 2H 2025**, ahead of the initial distribution
> timeline of 1H 2026, marking the completion of the Recapitalisation Plan."*

The audited statement shows it plainly (`…FY2025/full.md:4948–4955`):
```
Income available for distribution to Unitholders at the beginning of the year   –        –
Distribution withheld for the financial year 1 Jan 2024 – 31 Dec 2024           –    (47,627)
Distribution withheld for the financial year 1 Jan 2025 – 31 Dec 2025      (40,421)      –
Income available for distribution to Unitholders at the end of the year      2,611       –
```

Two defects follow:
1. **`archetype` is `"rollforward"` on both CMOU rows** while D5IU and BTOU — with the identical
   `dpu = 0, distribution_declared = 0` shape — are `"suspended"`. Any consumer filtering on
   `archetype == "suspended"` silently misses CMOU/2024. Set CMOU/2024 to `suspended` and give
   CMOU/2025 a partial-resumption flag.
2. **`amount_retained` is the *withheld* amount** — 47,627,000 (100% of income) in 2024 and
   40,421,000 (94%) in 2025. Same field-meaning collision as OXMU in item 4: this is not a
   working-capital retention. CMOU's DPU series 0 → 0.25 is a recapitalisation artefact, not growth.

---

## 5. OXMU and MXNU `distribution_declared` nulled although the figure **is printed** — **[EXTR]**

**Rows:** `OXMU / 2024`, `OXMU / 2025`, `MXNU / 2024`, `MXNU / 2025`

The known-issues list says the 26 declared-nulls are *"because the AR does not publish it"*. That is
true for most, but not these four.

OXMU's distribution statement prints an **unlabelled after-retention subtotal** directly beneath
`Amount retained`:

- `33_OXMU…_FY2024/full.md:5464`: `| | **3,938** | **32,200** |` (= 38,175 − 34,237)
- `33_OXMU…_FY2025/full.md:5096`: `| | **8,303** | **3,938** |` (= 28,726 − 20,423)

That line is exactly the spec's GATE 2 definition of declared. Its structure is identical to XZL's,
where the same line **was** recorded (`declared = 9,254 = 10,282 − 1,028`, XZL FY2024 line 3284) —
the only difference is that XZL's row carries a label and OXMU's does not. Inconsistent treatment of
the same shape.

MXNU is the same story and the extractor said so in its own note: *"derived would be 17,072 but
never printed"* (FY2024) / *"not printed; derived would be 18,338"* (FY2025). The retention is
recorded (1,382,000 / 965,000) and the DPS is given *both before and after retention*, so the
declared amount is fully determined.

**Suggested values:** OXMU 3,938,000 / 8,303,000. MXNU: recompute from the after-retention DPS ×
units rather than leaving null.

---

## 5b. TS0U's FY2025 report **contradicts itself** on the size of the FY2024 capital distribution — **[AR contradiction, affects our stored `other_additions`]**

**Row:** `TS0U / 2024` (`other_additions = 5,000,000`, label "Capital distribution")

The same report gives two different amounts for the same item:

> `31_TS0U…_FY2025/full.md:1673` — *"FY 2024 DPU includes the release of **S\$5.0 million** of capital
> distribution from the 50% divestment of OUE Bayfront"*
> `31_TS0U…_FY2025/full.md:825` — *"FY 2024 DPU has been adjusted to exclude the releases of
> **S\$2.5 million** capital distribution from 50% divestment of OUE Bayfront in 2021"*

We stored 5,000,000, which matches the FY2024 audited statement (line 5121) and line 1673. But the
FY2025 report also **restates the FY2024 DPU** to strip this item, so the FY2024 DPU as we store it
(2.06c) is not the figure the FY2025 report uses as its comparative. Flag TS0U/2024 as carrying a
one-off capital distribution inside its DPU.

Same class, verified but lower impact:
- **MXNU/2025** publishes an *adjusted* FY2024 DPU comparative — `14_MXNU…_FY2025/full.md:676`:
  *"FY2024 DPU adjusted based on enlarged equity base for units issued during 2025 and 95% payout
  ratio. On an unadjusted basis, FY2025 DPU increased 5.6% year-on-year."* Our stored MXNU/2024
  `dpu = 2.87` is the unadjusted original — correct, but it will not match the FY2025 report's
  comparative.
- **OXMU/2024** had a **1-for-10 bonus issue** — `33_OXMU…_FY2025/full.md:6086`: *"On 28 March 2024,
  the Trust issued **118,932,077 new Units as a bonus issue** on the basis of 1 bonus unit … for
  every 10 existing Units held."* So OXMU's FY2023 comparatives sit on a pre-bonus base, compounding
  the payout-policy break in item 4.

---

## 6. The mandatory `quotes` block is missing on **74 of 74 rows** — **[EXTR]**

The spec closes with: *"Include a `quotes` entry for at least `income_for_year`,
`distribution_declared`, `amount_retained` and `units_in_issue` wherever non-null"* and
*"I will re-check these mechanically against the file."*

Not one row in any of the seven batch files has a populated `quotes` object. The `*_line` numbers are
present, so verification is possible, but it requires opening every report — the mechanical
line-vs-quote cross-check the spec was designed around cannot be run at all. This is how a
mis-cited line (see item 7) survives undetected.

---

## 7. `fy_end_date` is null on **61 of 74 rows**, including every non-December reporter — **[EXTR]**

Missing on all of: ME8U (3 rows), M44U (3), N2IU (3), P40U, JYEU, J69U (2), BUOU (2), plus 45 others.
These are precisely the rows where TRAP 7 says the folder label is not the year end — e.g.
`28_M44U…_FY2024` is *"Year ended 31 March 2026"* (`full.md:8068`), three folder-labels away from its
own heading. Without `fy_end_date` the only defence against a year-alignment error is the folder
naming convention, and the convention is exactly what TRAP 7 warns is unreliable.

Present on only 13 rows (XZL 2024/25, O5RU 2024/25, M1GU 2024/25, BMGU 2024/25, A17U 2024/25, HMN
2024/25, AU8U 2024) — i.e. batch 1 populated it and the rest did not.

---

## 8. P40U/2024: headline figures cited to the **unaudited Financial Review**, not the audited Distribution Statement — **[EXTR, citation only]**

**Row:** `P40U / 2024`

`income_for_year_line = 4270` and `distribution_declared_line = 4271` both point into the *Financial
Review* table (`35_P40U…_FY2024/full.md:4270–4271`), while `opening_line`/`distribution_paid_line`/
`closing_line` point at the audited Distribution Statement (7268/7277/7278). TRAP 5 says *"Take every
number from the audited financial statements."*

**The values are right** — the audited statement at :7274 gives cumulative `185,121`, minus opening
`97,301` = `87,820`, which matches. So this is a citation defect, not a value defect.

Two genuine oddities that come with it:
- The **audited** statement carries **no retention line at all**. The S$4.0m retention exists only in
  a Financial Review footnote: :4285 *"Approximately S\$4.0 million (FY 2023/24: S\$2.6 million) of
  income available for distribution for FY 2024/25 has been retained for working capital
  requirements."*
- `87,820 − 4,000 = 83,820` vs stored `distribution_declared = 83,785` — a **35,000 residual** that
  the AR does not explain (the "S\$4.0 million" is itself rounded, so the true retention is
  4,035,000). Harmless, but it is why P40U shows up in the gate-2 sweep.

---

## 9. Distribution-**policy** changes mid-series that no field in the schema records — **[AR]**

Each of these is verified verbatim. None is an extraction error; all of them mean a YoY change in
`dpu` / `distribution_declared` is driven by policy, not performance, and nothing in the row says so.

| symbol / rows | change | evidence |
|---|---|---|
| **CRPU / 2024** | distribution **frequency** quarterly → semi-annual | `34_CRPU…_FY2024/full.md:6864`: *"There is a change in the Trust's distribution frequency from quarterly distributions to semi-annual distributions, with effect from the financial year ended 31 December 2024."* |
| **DCRU / 2024 → 2025** | payout **100% → "at least 90%"** | `13_DCRU…_FY2024/full.md:6216`: *"…distribute 100% of distributable income for the financial year ended 31 December 2024. Thereafter, the Trust will distribute at least 90%…"*; `…FY2025/full.md:6472` confirms the 90% wording |
| **M44U / 2025** (YE 31 Mar 2026) | **ceased distributing divestment gains** | `28_M44U…_FY2024/full.md:697`: *"At the start of FY25/26, the Manager deemed it appropriate to **cease the practice of distributing divestment gains**…"* — prior M44U years all embed such gains, so the DPU series has a definitional step |
| **BTOU / 2025** | suspension **extended indefinitely** (previously understood to end 31 Dec 2025) | `26_BTOU…_FY2025/full.md:208`: *"…the lenders have required Manulife US REIT to **keep half-yearly distributions to Unitholders suspended until the later of** the achievement of the Reinstatement Conditions and the period during which the Bank ICR relaxation remains in effect."* |
| **M1GU / 2025** | the ~10% retention of prior years **went to nil** | already in the row's own `gate_note` (note (2) at `03_M1GU…_FY2025/full.md:4418`, *"An amount of nil (2024: \$3,403,000)"*) — so part of the 2.86c → 3.53c rise is payout, not earnings |

---

## 10. Leads from the corporate-action sweep that I have **not** individually re-verified

Recorded so they are not lost, but treat as unconfirmed until checked — do not act on them as
findings:

- **N2IU / 2023** (folder `FY2022`): the MNACT merger year, reported as containing a 3.04c "clean-up
  distribution" on the old base plus three quarters on the enlarged base (1,018,382,531 preferential
  offering units + 885,734,587 consideration units). If true, that row is not a clean 12 months on a
  single base.
- **SET / 2025**: REIT units delisted and **stapled securities** listed 16 Jun 2025 — the metric
  changes from "Units in issue" (562,392k, FY2024) to "Stapled Securities in issue" (556,884k,
  FY2025). 1:1, so magnitudes carry, but the instrument identity does not.
- **C2PU / 2024** and **ME8U / 2024**: caption shift from *"units in issue"* to *"units in issue and
  to be issued"* without re-presenting the prior year — same family as the known N2IU/2025 item, but
  two additional trusts.
- **C2PU / 2024**: S$180m placement 1 Nov 2024 with a 5.00c advance distribution covering 1 Jul –
  31 Oct on the old base.
- **ME8U / 2023**: S$204.8m placement plus a 2.48c advance stub distribution.
- **AJBU**: the issuer publishes both a reported and an **adjusted** DPU (FY2024 9.451 vs 9.504;
  FY2025 10.381 vs 10.629). We store the reported one — worth recording which basis explicitly.
- **N2IU** distribution frequency went **half-yearly → quarterly** from 1 Oct 2022 (the opposite of
  the Mapletree-wide assumption); ME8U and M44U were quarterly throughout.

---

## Things I checked that turned out to be **fine** — do not re-open these

1. **Cross-year continuity, all 33 consecutive-year pairs.** `closing(FY n)` equals `opening(FY n+1)`
   exactly, to the dollar, on every pair. The only break is the already-known J91U (no opening
   balance at all). **Zero new continuity defects.**
2. **Sign sweep.** No negative value in any of `opening / income_for_year / other_additions /
   amount_retained / distribution_paid / closing / distribution_declared / dpu / units_in_issue /
   number_of_unitholders` across all 74 rows.
3. **All 8 suspiciously-round values are genuine printed figures**, not parse artefacts:
   - M1GU/2024 `income_for_year = 35,000,000` — really is 35,584 − 584 tax = **35,000** exactly
     (`03_M1GU…_FY2024/full.md:4968–4969`). Coincidence.
   - M44U/2023 `opening = 110,000,000`, TS0U 5,000,000 ×3, C2PU 3,000,000 ×2, P40U 4,000,000 — all
     appear as printed round disclosures (the last three are policy retentions stated to the nearest
     million in footnotes).
4. **Seven symbols carry an identical `units_in_issue` in both years** (BMGU 519,603k; BTOU
   1,776,565k; CMOU 1,044,450k; D5IU 7,696,809,979; M1GU 1,125,055,242; UD1U 1,344,838k; XZL
   580,103k). Not a copy-paste error — each report explicitly prints a no-movement line, e.g. BMGU
   `FY2025/full.md:6082` *"Total Units in issue at the **beginning and end of year** | 519,603 |
   519,603"*, UD1U `FY2025/full.md:8349` *"Beginning and at end of the year"*, XZL `FY2025/full.md:4755`
   *"…as at 1 January/ 31 December"*.
5. **All 18 non-SGD rows verified against the presentation-currency note.** USD: XZL (`FY2025:3507ff`),
   DCRU (:5880ff), CMOU (:5188ff), BTOU (:5537ff), OXMU (:5385ff), ODBU (:6695). GBP: MXNU
   (`FY2025:6376`, *"presented in Pound Sterling (£)"*). EUR: UD1U (`FY2025:6976`), SET
   (`FY2025:7058`, :9514). No SGD-tagged trust reports in another currency.
6. **TS0U / C2PU / P40U "gate failures" are the documented retention-inside-the-subtotal convention**,
   not errors — the retention sits inside the for-the-year build-up so subtracting it again
   double-counts. Already covered by the known "retention placement varies" item.
7. **XZL `distribution_paid` > `income_for_year`** (15,490 vs 10,282 in FY2024; 7,425 vs 5,476 in
   FY2025). Fine: XZL is a `no_pool` pure-flow statement, so FY cash carries the larger prior-year
   declared tranches (`01_XZL…_FY2024/full.md:3458`). Not a magnitude error.
8. **Every large DPU / income / unit-count YoY swing** flagged by the sweep resolves to a known or
   explained cause: J91U 10.3x DPU + 0.1x units = the known consolidation; OXMU = item 4 above;
   BMGU/UD1U/XZL/BTOU = genuine earnings declines with identical unit counts; M1GU unitholder count
   9,608 → 6,254 is a real register movement dated 2 Mar 2026.
9. **AW9U/2025 units.** The `2,111,058` weighted-average trap was already caught and corrected to
   `2,110,969,000` in the extraction note. Confirmed correct.
10. **Prior-year restatement sweep: clean.** All 37 consecutive-year pairs were re-checked by opening
    the *later* year's report and reading its comparative column against our stored earlier-year
    `opening / income_for_year / distribution_paid / closing`. Every comparative ties to the $'000,
    and no statement line in any report is labelled restated or carries a restatement footnote.
    One candidate (O5RU/2024 `income_for_year` 67,104 vs a comparative 97,393) was raised and
    disproved: 97,393 is the cumulative line (19,234 + 67,104 + 11,055 capital distribution), and
    97,393 − 76,714 = 20,679 = our stored closing. Our value is correct.
11. **BUOU's "layered" presentation** — the report's rollforward runs through 255,515
    (210,337 income + 45,178 capital distribution) rather than the income line alone. We store the
    45,178 as `other_additions` with the label *"Capital distribution: divestment gains 41,700 of
    45,178"*, so the rollforward reconciles. Presentation layering, correctly handled.
12. **All 12 rows where `dpu × units` diverges >15% from `distribution_paid`** are the intended
    declared-vs-paid timing distinction (TRAP 2), not defects. Only AJBU (item 3) diverges against
    *declared*.
