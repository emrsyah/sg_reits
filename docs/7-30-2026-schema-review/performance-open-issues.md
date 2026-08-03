# `sgx_reit_performance` — open issues after adversarial verification

2026-08-03. **Supersedes §10 of `performance-reextraction-results.md`**, which was written before this
verification pass and got three things wrong.

Two independent agents were run against the 74 re-extracted rows: one told to **refute** my
explanations of seven anomalies, one told to find what we had **missed**. Raw output:
`fixes/perf_reextract/_adversarial_findings.md` and `_missed_issues.md`.

---

## 0. Corrections to my own earlier claims

Read this first. Four items I reported as open problems were not problems, or were my errors.

| I claimed | Verdict | What is actually true |
|---|---|---|
| **M1GU/2024 "reconciles on no basis"** | ❌ **my data bug** | We paired the *opening-balance* retention (3,994) with the *after-tax* income (35,000). The AR's FY2024 retention is **3,403**, stated **before tax**, so it nets against the **before-tax** income **35,584**: `35,584 − 3,403 = 32,181` vs declared `32,177`. Independently: `1,125,055k units × 2.86¢ = 32,177` |
| **ME8U declares less than it earns, 3 years, unexplained** | ❌ **my basis error** | Our `distribution_declared` came from the Financial Review (**declared** basis); I reconciled it against the audited statement (**paid** basis). Two different bases. The audited pool ties exactly: `101,328 + 388,110 + 13,354 − 385,455 = 117,337`. Perpetual securities and NCI were checked and are **not** the cause — both sit above the Unitholder line |
| **8C8U/2025 42,000 gap — rounding explanation fails** | ❌ **my rejection was wrong** | The policy is quoted verbatim: distributions are rounded down to 3 decimals **per distribution type**, not on the aggregate. 3 types × 0.001¢ ≥ the 0.002438¢ needed. The earlier agent was right |
| **J91U "two conflicting cash figures"** | ❌ **premise wrong + parse artefact** | Neither figure is cash. `167,921` = distributions to Unitholders; `168,003` = an equity-movement subtotal. The 82 = manager fees in units (+15,231) − buyback (13,615) − issue costs (1,698). The illusion came from **row labels shifted by one row in the Datalab markdown** around L5217–5221 |

**Confirmed as originally stated:** D5IU, K71U and Q5T register-vs-audited unit gaps — all the same
phenomenon, the Statistics of Unitholdings page is dated 6–10 weeks after year end. See §4.

---

## 1. Real extraction errors — fix before load

### E1. OXMU `distribution_declared` wrongly nulled — 2 rows

The AR **does** print it, as an unlabelled subtotal directly under the retention line:

```
Income available for distribution      38,175
Amount retained                       (34,237)
                                        3,938      <- FY2024 declared
```

`38,175 − 34,237 = 3,938`; FY2025 `28,726 − 20,423 = 8,303`. The OXMU agent called this
*"an intermediate cumulative subtotal"* — **wrong**: cumulative would be `3,011 + 38,175 − 34,237 =
6,949`.

This is the **same structure as XZL**, where we did record it. We treated identical layouts two
different ways.

```
OXMU/2024  distribution_declared  null -> 3,938,000
OXMU/2025  distribution_declared  null -> 8,303,000
```

MXNU is reported to have the same shape and needs the same check.

### E2. M1GU/2024 wrong retention and wrong income basis — 1 row

```
amount_retained   3,994,000 -> 3,403,000    (FY2024 retention, not the opening-balance appropriation)
income_for_year  35,000,000 -> 35,584,000   (before tax, to match the before-tax retention)
```

Raises a convention we have never decided: **is `income_for_year` before or after tax?** M1GU is the
only REIT where it visibly matters, but the column must mean one thing.

### E3. CMOU archetyped `rollforward`, but distributions were suspended

Suspended under the Recapitalisation Plan of 15 Feb 2024. D5IU and BTOU are archetyped `suspended`;
CMOU is not. **Any filter on `archetype` silently misses it.**

### E4. J91U DPU series is broken across the 10:1 consolidation

We store FY2024 DPU `2.119`; the FY2025 report restates it as `21.190`. A two-year chart reads
**+934%** instead of **+3.4%**. Either store the restated comparative or carry a
`restated_for_consolidation` flag — a frontend plotting this today would publish a false chart.

---

## 2. Schema problems — these block load

### S1. 🔴 `distribution_paid` is not all cash

Part of it is settled in **units** via Distribution Reinvestment Plans:

```
M1GU/2024   S$4.88m    17.5% of the "paid" figure
M44U/2024   S$40.6m     9.7%
ODBU/2025   US$7.3m
ODBU/2024   US$3.4m
ME8U        S$29.8m    (already known)
plus MXNU and JYEU
```

The column is named *paid* and the API will present it as cash that left the trust. On M1GU nearly a
fifth of it never did. **Either rename the column or add `paid_in_units`.**

### S2. `income_for_year` has three possible meanings

pre-retention / post-retention (5 rows) / pre-tax vs post-tax (M1GU). Needs
`retention_in_subtotal` **and** a tax-basis decision. Unchanged from the target schema doc, now with a
second dimension.

### S3. `distribution_declared` mixes two bases

ME8U's value is on the **declared-for-the-year** basis from the Financial Review; other REITs' come
from the audited statement on a **paid/recognised** basis. Both are defensible; storing them in one
column without a flag is not. Needs `declared_basis`.

### S4. `units_basis` is mixed — 46 `issued_only` vs 28 `issued_and_issuable`

`units_in_issue` is now 100% populated but not on one convention, so `DPU × units` compares unlike
things across REITs.

### S5. `amount_retained` conflates two different things

OXMU's "retention" is a **payout-ratio set-aside** (90%, then 71% of income, changed three times
inside FY2025) — economically different from C38U's working-capital retention. Both land in one
column.

### S6. Five policy changes with nowhere to record them

CRPU quarterly → semi-annual · DCRU payout 100% → 90% · M44U ceased distributing divestment gains ·
BTOU suspension extended indefinitely · M1GU retention → nil.

---

## 3. 🔴 Process defect — my doing

```
quotes        empty on 74 / 74 rows
fy_end_date   null on 61 / 74, including every non-December reporter
```

I instructed the agents to drop `quotes` to keep the payload small, then stripped the field myself
when saving batches 2–6. **The mechanical citation re-check that the spec mandates cannot be
reproduced from the saved files.**

The verification I ran *was* real — it executed while the data was still complete — but nobody can
re-run it from `fixes/perf_reextract/` as it stands. The quotes survive only in the agent transcripts.

**Fix:** re-emit the rows with `quotes` and `fy_end_date` before this is treated as a finished
artefact. Cheap now, impossible later once the transcripts age out.

---

## 4. Confirmed non-issues — do not re-open

Verified by an agent explicitly hunting for problems, and cross-checked independently:

| | result |
|---|---|
| Cross-year continuity `closing(n) = opening(n+1)` | **33/33 tie to the dollar** (my own pass: 32/32) |
| Prior-year restatements | **37 comparative columns, zero restated** |
| Negative values | none |
| Suspicious round numbers | all 8 genuine — M1GU's 35,000,000 really is `35,584 − 584` |
| Identical unit counts across years (7 symbols) | all confirmed *"beginning and end of year"* |
| Non-SGD currency tags | all 18 verified against the presentation-currency note |
| TS0U / C2PU / P40U gate arithmetic | the documented retention-inside-subtotal convention |
| XZL `paid > income` | correct for a no-pool flow statement |
| `dpu × units` divergences (12) | intended declared-vs-paid timing |
| Register vs audited unit counts | post-year-end issuance — D5IU rights issue ties **exactly**: `7,696,809,979 + 9,005,267,676 = 16,702,077,655` |
| K71U 1.63¢ stub | private placement for the Top Ryde City acquisition; cut-off is the day before the placement units were issued |
| Q5T 0.47¢ stub to 19 Aug | earn-out issuance of 25,746,652 securities on 20 Aug 2025 (Oasia Hotel Downtown) — **not** a privatisation |

**Rule worth encoding:** never reconcile the Statistics of Unitholdings register against a Note. The
register is dated weeks after year end. Add a `('000)` scale check on unit notes at the same time —
that combination alone would have pre-empted three of the seven anomalies.

---

## 5. Priority

**Before load — blocking:**
1. Decide `income_for_year`: retention placement **and** tax basis (S2)
2. Decide `units_basis` convention (S4)
3. Fix OXMU ×2 and M1GU declared/retention (E1, E2)
4. Re-emit with `quotes` + `fy_end_date` (§3)

**Before the frontend shows anything:**
5. `distribution_paid` naming or `paid_in_units` (S1) — currently misleading
6. J91U DPU restatement (E4) — a chart today would be false

**Then:**
7. `declared_basis` flag (S3), CMOU archetype (E3), `amount_retained` split (S5), policy-change
   fields (S6)

---

## Provenance

Adversarial and missed-issue passes: `fixes/perf_reextract/_adversarial_findings.md`,
`_missed_issues.md`. Every claim in those files carries a line number. The two contested items —
OXMU's `3,938` and the M1GU reconciliation — were re-verified by hand against the source reports
before being accepted here.

**Nothing has been written to dev or prod.**
