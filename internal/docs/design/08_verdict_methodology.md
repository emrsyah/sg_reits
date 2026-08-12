# 08 — Distribution-Safety Verdict — methodology (PROPOSAL, needs sign-off)

The hero of the single-REIT detail page ([`03_design_brief.md`](03_design_brief.md) §4A) and the
default sort of the screener (§4C). It de-thrones yield: *"a high yield is a question, not an answer."*

> **STATUS: PROPOSAL.** The *structure* below is ready to build; the **thresholds** are a domain call
> and need the analyst/owner (you) to sign off. Marked ⚠️ where a number must be confirmed. This is a
> **health signal, not investment advice** — that framing is non-negotiable (liability + trust).

---

## 1. Principles

- **Transparent & auditable** — every input is a stored `[REIT-DB]` field with a `source_page`; the
  verdict is a deterministic function of them, fully shown in the "how we computed this" panel. No black box.
- **Signal, not advice** — output is a health band + a sentence, never "buy/sell".
- **Honest under missing data** — never fabricate a green from absent inputs; degrade to lower
  confidence or "insufficient data".
- **Cohort-aware** — sub-sector-sensitive metrics (WALE, occupancy, cost of debt) graded against the
  right cohort where n is large enough; absolute thresholds otherwise.

---

## 2. Inputs (all `sgx_reit_performance`, FY2025 — page-cited)

| Metric | Field | Why it matters |
|---|---|---|
| Gearing | `aggregate_leverage` (%) | Distance to the MAS 50% cap = balance-sheet headroom. |
| Interest coverage | `interest_coverage_ratio` (×) | Can operating income service the debt? |
| Cost of debt | `cost_of_debt` (%) | Refinancing pain in a high-rate world. |
| Debt maturity | `weighted_avg_debt_maturity` (yrs) | Near-term refinancing wall risk. |
| Occupancy | `portfolio_occupancy` (%) | Income reliability at the asset level. |
| WALE | `wale` (yrs) | Income visibility / re-leasing risk (sub-sector-sensitive). |
| Distribution coverage | `net_distributable_income`, `dpu` | Is the payout backed by income? *(see §6 caveat — true coverage needs units-outstanding, which we don't store.)* |

---

## 3. Per-metric rubric — PROPOSED thresholds ⚠️ (confirm before build)

Each metric → **Green / Amber / Red**. Defaults grounded in SG-REIT norms (MAS 50% gearing cap;
MAS ≥1.5× ICR to gear beyond the lower tier) — **tune with the analyst.**

| Metric | 🟢 Green | 🟡 Amber | 🔴 Red |
|---|---|---|---|
| Gearing `aggregate_leverage` | < 38% | 38–43% | > 43% (approaching 50% cap) |
| Interest coverage `interest_coverage_ratio` | ≥ 3.0× | 1.8–3.0× | < 1.8× |
| Cost of debt `cost_of_debt` | < 3.5% | 3.5–4.5% | > 4.5% |
| Debt maturity `weighted_avg_debt_maturity` | > 3.0 yr | 2.0–3.0 yr | < 2.0 yr |
| Occupancy `portfolio_occupancy` | ≥ 96% | 90–96% | < 90% |
| WALE `wale` | cohort-relative (§5) | cohort-relative | cohort-relative |

⚠️ Sign-off items: the exact cut points; whether cost-of-debt should be **cohort/vintage-relative**
(rates move); whether to add a **DPU-trend** check once multi-year data exists.

---

## 4. Banding logic (how the metrics combine)

**Gating (critical) metrics:** Gearing · Interest coverage · Occupancy. **Secondary:** cost of debt ·
debt maturity · WALE.

```
RED   band ("Watch")    if  any GATING metric is 🔴      OR  ≥3 metrics 🟡/🔴 total
AMBER band ("Mixed")    if  any metric is 🔴 (non-gating) OR  ≥2 metrics 🟡
GREEN band ("Stronger") otherwise (no 🔴, ≤1 🟡)
```
- Bands: **Stronger** (🟢) · **Mixed** (🟡) · **Watch** (🔴). Wording is health-signal, not advice.
- The verdict **sentence** is a templated, cited NLG string (deterministic — see §7), e.g.
  *"Stronger: gearing 33% (p.42) sits well below the 50% cap and coverage is 5.1× (p.42); occupancy 97% (p.18)."*
- ⚠️ Sign-off: confirm the gating set and the count thresholds (worst-of vs weighted vs count-based).
  A simple count is the most explainable; a weighted score is finer but harder to justify in the panel.

---

## 5. Cohort-aware grading (sub-sector-sensitive metrics)

WALE, occupancy and cost-of-debt differ structurally by sub-sector (hospitality WALE ≪ healthcare WALE).
- Where the cohort has **n ≥ 5** (Diversified, Industrial, Retail, Office): grade the metric against the
  **cohort median** (e.g. 🟢 ≥ median, 🟡 within 1σ below, 🔴 well below) **instead of** an absolute cut.
- Where **n = 2–4** (Hospitality, Healthcare, Data Centre): use absolute thresholds + print the cohort
  range and n; do not imply statistical precision.
- Where **n = 1** (the "Specialized" outlier, Q1): absolute thresholds only, with a "thin peer set" note.

---

## 6. Suppression, caveats & confidence (honest under edge cases)

| Situation | Detected by | Verdict behaviour |
|---|---|---|
| **Externally/EMA-managed, no per-property NPI** | `profile.income_model`; `notes.columns_never_fillable` | Verdict still valid from portfolio KPIs; **do not** penalize for missing per-property detail; show a note. |
| **One-off equity raise / period split** | `performance.flags` (`dpu_half_year_split`, …) | **Caveat the distribution read**; never render the period split as a DPU cut. |
| **A gating input is NULL** | null field | **Do not** issue a Green. Show "Insufficient data for a full verdict" + which input is missing. |
| **WADM null** (≈4 names: AW9U, CY6U, T82U…) | null `weighted_avg_debt_maturity` | Omit that driver; lower confidence; note it — don't treat null as good. |
| **Dual-currency / partial ownership** | `property.flags`, `original_currency` | Verdict unaffected (portfolio KPIs are as-reported); surface the flag for context. |

**Confidence** = share of the 7 inputs present & page-cited. Render as High / Medium / Low beside the
band so a thin-data verdict never looks as certain as a complete one.

---

## 7. "How we computed this" output contract (what the FE must render)

The verdict object the FE consumes (whether built in a DB view or RSC — see [`07`](07_data_contract_ui.md) §6):

```jsonc
{
  "band": "Stronger | Mixed | Watch",
  "sentence": "templated, cited string",
  "confidence": "High | Medium | Low",
  "drivers": [
    { "metric": "gearing", "value": 33.0, "unit": "%", "grade": "green",
      "threshold": "< 38% (cap 50%)", "source_page": 42, "cohort_median": 36.0 }
    // …one per input, including any "missing"/"suppressed"
  ],
  "caveats": [ { "type": "dpu_half_year_split", "note": "plain-English copy from [EDIT]" } ],
  "methodology_version": "v1"
}
```
- Every driver chip → its value, grade, **threshold**, `source_page` (📄 drill), and cohort median.
- The **band itself carries a methodology note, NOT a `source_page`** (it is derived, not extracted).
- `methodology_version` so a verdict is reproducible after threshold changes.

---

## 8. Worked examples (validate on real data)

- **AJBU (clean, Data Centre):** expect all-green/most-green → **Stronger**, High confidence. Proves the happy path.
- **A17U (edge-case):** `dpu_half_year_split` flag around the Jun-2025 raise + segment-only per-property
  NPI → verdict from portfolio KPIs, **distribution caveat shown**, period split not read as a cut.
  Proves the suppression rules.

These are the same two names recommended for the wireframe — the verdict spec and the prototype validate together.

---

## 9. Sign-off checklist (for the analyst/owner)

- [ ] Confirm/tune every threshold in §3.
- [ ] Confirm the gating metric set + the band-combination rule in §4 (count vs weighted).
- [ ] Confirm cohort-relative vs absolute for WALE / occupancy / cost-of-debt (§5).
- [ ] Confirm the "signal, not advice" disclaimer wording.
- [ ] Decide whether a DPU-trend / coverage-ratio input is added once units-outstanding + multi-year exist.
- [ ] Approve `methodology_version` v1 to unblock the hero build.
