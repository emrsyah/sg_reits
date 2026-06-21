# 05 — Decisions, data-roadmap & open questions

Living tracker. Update as decisions get made and questions get answered.
Source brief: [`03_design_brief.md`](03_design_brief.md).

## Locked decisions

| # | Decision | Date |
|---|---|---|
| D1 | **Positioning: hybrid, depth-led.** Lead with page-cited AR depth; reuse sectors.app's live market-data layer, don't rebuild it. | 2026-06-21 |
| D2 | **Anti-yield-trap posture is a product principle.** Yield never shown alone; always beside its risk drivers. | 2026-06-21 |
| D3 | **The LIVE-vs-ANNUAL seam is per-field and dated**, not just a section divider. | 2026-06-21 |
| D4 | **Beginner UX = collapsed first paint**, not a separate "simple mode." Progressive disclosure throughout. | 2026-06-21 |
| D5 | **MVP = single-REIT detail spine + sub-sector explorer + safety screener (simple default) + glossary/tax.** AI, compare, export, transactions, full financials → later. | 2026-06-21 |
| D6 | **Screener default sort = distribution-safety composite, NOT yield.** | 2026-06-21 |

## Data-roadmap items (features blocked on data we don't yet have)

These are cut from launch **because the data doesn't exist**, not because they're unwanted. Each
needs an extraction/data change before it can be built — feeding back to the extraction pipeline.

| Item | Why blocked | Unblock by |
|---|---|---|
| **Year-by-year debt-maturity ladder** | 0/36 reports have a per-year/per-tranche maturity field; we hold only the `weighted_avg_debt_maturity` scalar. | Add a debt-maturity-schedule extraction field. Until then: refinancing-pressure triad (WADM + cost_of_debt + ICR + gearing). |
| **Multi-year DPU / KPI trend charts** | Data is FY2025-only; `distribution_record` is intra-year splits, not a time series. | Accrue FY2026 (and back-fill prior years) so a real trend exists. |
| **FFO/AFFO metric** | `funds_from_operation` null in 36/36 — SG REITs disclose distributable income, not US-style FFO. | Don't fabricate. Teach NDI as the SG equivalent; revisit only if computing FFO from line-items with a clear "estimate" label. |

## Open questions (resolve before / during build)

| # | Question | Blocks | Owner |
|---|---|---|---|
| Q1 | **Sub-sector taxonomy:** how to handle the 8th "Specialized" label (8C8U, n=1) and the n=1/n=2 cohorts (Healthcare 2, Data Centre 2)? Reclassify into the 7, or redirect single-name cohorts straight to the detail page? | Sub-sector explorer + landing sub-sector map | — |
| Q2 | **Live-layer data contract:** exact ticker-mapping, fields (yield-on-price, P/B, yield-spread vs SG 10Y, SGD/IDR FX), latency, and failure-state behaviour from sectors.app's market layer. | The seam, market-pulse band, P3 net-yield | — |
| Q3 | **R2 PDF deep-link reliability:** presigned URL expiry (3600s) handling, per-report page_offset correctness, #page anchor across mobile browsers. A broken "see source" link breaks the moat's trust. | Provenance click-through (the #1 differentiator) | — |
| Q4 | **Editorial rewrite ownership:** who turns internal-QC notes (IPUD, FRS116, "Note 22") into plain-English flag copy, and who authors the cohort-aware healthy ranges for the glossary? | Anomaly flags, glossary | — |
| Q5 | **Verdict methodology + liability:** exact inputs/thresholds/weights of the Distribution-Safety composite, the "signal not advice" framing, and auto-suppression for EMA/one-off-distorted names (e.g. A17U). | Hero verdict (the spine of the detail page) | — |
| Q6 | **Audience-mix bet:** depth-led assumes enough P2 (analyst) traffic to monetize. What's the fallback if realized traffic skews P1/P3 wanting a fast yield read? | Strategy / go-to-market | — |
| Q7 | **Landing `/` shape:** overview hub (recommended) vs the screener itself? | Landing page ([`04_landing_page.md`](04_landing_page.md)) | — |
| Q8 | **Detail-page URL shape:** `/reit/[ticker]` vs reuse sectors.app's existing `/sgx/[ticker]`? | Routing, live-layer integration | — |

## Recommended next step

Build a **clickable wireframe of the single-REIT detail page** on two contrasting real names —
**clean: AJBU (Data Centre)** · **edge-case: A17U** (Jun-2025 equity-raise DPU split, segment-only
per-property NPI, rounding-delta reconciliation) — plus the `/ → sub-sector → detail` flow. It
proves the moat (provenance click-through), the hardest UX call (the seam + verdict honesty), and
the biggest cut (no ladder) on real data in one artefact, before committing engineering.
