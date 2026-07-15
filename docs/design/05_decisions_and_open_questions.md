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
| D7 | **REITs DB first.** The whole MVP builds from `sgx_reit_*` alone; prod tables are enrichment, mostly deferred (only optional live price in v1). Prod never overwrites a page-cited value. | 2026-06-21 |

## Prod-data integration (added 2026-06-21 — see [`07`](07_data_contract_ui.md) §5)

Owner: **the user** (data integration). Core stays the REITs DB; prod tables enrich.

| Prod table | Role | Status |
|---|---|---|
| `sgx_daily_data` | live price → derived yield / P-B / market-pulse (the seam's live side) | MVP |
| `sgx_news` | per-REIT + sub-sector news feed; powers "Notable this year" | MVP (list) |
| `sgx_financials_annual` | **multi-year** standard financials (same blob shape as our `sgx_reit_financial`) | Later |
| `sgx_filings` | substantial-holder / insider ownership signal | Later |
| `sgx_short_sell` | market-positioning / sentiment signal | Later |

## Data-roadmap items (features blocked on data we don't yet have)

These are cut from launch **because the data doesn't exist**, not because they're unwanted. Each
needs an extraction/data change before it can be built — feeding back to the extraction pipeline.

| Item | Why blocked | Unblock by |
|---|---|---|
| **Year-by-year debt-maturity ladder** | 0/36 reports have a per-year/per-tranche maturity field; we hold only the `weighted_avg_debt_maturity` scalar. | Add a debt-maturity-schedule extraction field. Until then: refinancing-pressure triad (WADM + cost_of_debt + ICR + gearing). |
| **Fixed/floating debt %** | **No column exists** in `sgx_reit_performance`/schema (brief §4A assumed ~12/36 disclose it). | Add an extraction field, or drop the sub-module. |
| **Multi-year DPU / KPI trend charts** | DPU/gearing/WALE are FY2025-only (`performance` table); `distribution_record` is intra-year splits. | **Standard income/balance/cashflow trends are now PARTIALLY unblocked via prod `sgx_financials_annual`** (labelled prod-sourced, our FY2025 stays authoritative). DPU/gearing/WALE multi-year still need FY2026 extraction. |
| **FFO/AFFO metric** | `funds_from_operation` null in 36/36 — SG REITs disclose distributable income, not US-style FFO. | Don't fabricate. Teach NDI as the SG equivalent; revisit only if computing FFO from line-items with a clear "estimate" label. |
| **DPU coverage ratio** | True coverage needs **units-outstanding**, which we don't store (`number_of_unitholders` = holder count, not units). | Source units-outstanding from prod; until then present NDI + DPU without a computed ratio. |

## Open questions (resolve before / during build)

| # | Question | Blocks | Owner |
|---|---|---|---|
| Q1 | **Sub-sector taxonomy:** how to handle the 8th "Specialized" label (8C8U, n=1) and the n=1/n=2 cohorts (Healthcare 2, Data Centre 2)? Reclassify into the 7, or redirect single-name cohorts straight to the detail page? | Sub-sector explorer + landing sub-sector map | — |
| Q2 | **Live-layer data contract:** exact ticker-mapping, fields (yield-on-price, P/B, yield-spread vs SG 10Y, SGD/IDR FX), latency, and failure-state behaviour from sectors.app's market layer. | The seam, market-pulse band, P3 net-yield | **User** (owns data integration) |
| Q3 | **R2 PDF deep-link reliability:** presigned URL expiry (3600s) handling, per-report page_offset correctness, #page anchor across mobile browsers. A broken "see source" link breaks the moat's trust. | Provenance click-through (the #1 differentiator) | — |
| Q4 | **Editorial rewrite ownership:** who turns internal-QC notes (IPUD, FRS116, "Note 22") into plain-English flag copy, and who authors the cohort-aware healthy ranges for the glossary? | Anomaly flags, glossary | **User** (owns content) |
| Q5 | **Verdict methodology + liability:** thresholds/banding/suppression for the Distribution-Safety verdict. → **Drafted as a proposal in [`08`](08_verdict_methodology.md); needs analyst sign-off (§9 checklist).** | Hero verdict (the spine of the detail page) | **User** (sign-off) |
| Q6 | **Audience-mix bet:** depth-led assumes enough P2 (analyst) traffic to monetize. What's the fallback if realized traffic skews P1/P3 wanting a fast yield read? | Strategy / go-to-market | — |
| Q7 | **Landing `/` shape:** overview hub (recommended) vs the screener itself? | Landing page ([`04_landing_page.md`](04_landing_page.md)) | — |
| Q8 | **Detail-page URL shape:** `/reit/[ticker]` vs reuse sectors.app's existing `/sgx/[ticker]`? | Routing, live-layer integration | — |
| Q9 | **Prod/REIT-DB co-location:** are the `sgx_*` prod tables in the **same Postgres** as `sgx_reit_*` (can JOIN) or a separate DB (need API/FDW/replication)? | Whole data-fetch strategy | **User** |
| Q10 | **Symbol-key normalization:** do prod tables use `.SI`-suffixed symbols like ours, or bare tickers? | Every prod join (news/filings/short/price) | **User** |
| Q11 | **Units-outstanding source** for market cap + DPU coverage (we only store `number_of_unitholders` = holder count). | Market cap, yield accuracy, coverage ratio | **User** |
| Q12 | **`sgx_financials_annual` coverage + reconciliation:** how many prior years for our 36 symbols, and the tolerance/authority rule where prod FY2025 ≠ our page-cited FY2025? | Multi-year financials module | **User** |
| Q13 | **SG 10Y bond yield source** for the yield-spread. | Market-pulse, yield context | **User** |

## Navigation forks (from [`06_ia_and_navigation.md`](06_ia_and_navigation.md) §10)

| # | Fork | Recommendation |
|---|---|---|
| N1 | Mobile primary nav: bottom tab bar vs hamburger | **Bottom tab bar** (thumb-reach for P1) |
| N2 | Density toggle (Simple⇄Analyst) scope | **Global + persistent** |
| N3 | Detail URL: `/reit/[ticker]` vs reuse sectors.app `/sgx/[ticker]` | Open — ties to live-layer integration (also Q8) |
| N4 | "Compare" as a top-level menu item? | **No — tray only**; revisit if analysts ask |
| N5 | Search "Ask" (NL Q&A) in MVP? | **No — palette is jump-only**; Ask is fast-follow |

## Recommended next step

Build a **clickable wireframe of the single-REIT detail page** on two contrasting real names —
**clean: AJBU (Data Centre)** · **edge-case: A17U** (Jun-2025 equity-raise DPU split, segment-only
per-property NPI, rounding-delta reconciliation) — plus the `/ → sub-sector → detail` flow. It
proves the moat (provenance click-through), the hardest UX call (the seam + verdict honesty), and
the biggest cut (no ladder) on real data in one artefact, before committing engineering.
