# 01 — Research

The evidence base under the design. Done 2026-06-21 via web search/fetch + reading our own
extracted data and the `guides_ux/` reference drafts.

## Research process

- **External web research** on three fronts: (1) what **sectors.app** is and its product surface,
  (2) what **S-REIT investors actually track**, (3) the **competitive field** of S-REIT tools.
- **Internal grounding** on what data we genuinely hold (the `sgx_reit_*` schema, the FY2025
  extraction outputs) so design choices stay buildable, not wishful.
- The findings then fed the multi-agent design-thinking run (see [`02_design_thinking.md`](02_design_thinking.md)).

## Findings

### 1. sectors.app — the DNA we inherit
API-first SEA financial-data platform by Supertype, covering **IDX + SGX + Bursa**. It already runs
**per-ticker analysis pages** (e.g. `sectors.app/sgx/ov8` for Sheng Siong) with valuation-vs-peers,
intrinsic value, multi-year financials parsed from annual reports, and price performance — plus an
**AI / natural-language search**. So `reits.sectors.app` is a **REIT-specialized vertical on an
existing design language + market-data infra**, not a greenfield build.

### 2. What S-REIT investors track (DBS "ABCD" framework + tool consensus)
Yield & payout frequency · **WALE** · **NAV / price-to-book** · **FFO** · **gearing / aggregate
leverage** · **cost of debt & interest coverage** · **debt-maturity / refinancing risk** ·
**occupancy & rental reversion** · **sub-sector outlook** · **yield spread over the SG 10Y bond**.

> The single most-repeated caution across every source: **a high yield is NOT automatically good** —
> it often signals distribution risk. Context (debt, lease quality, DPU trend, sub-sector) matters
> more than the headline number. This became a core product principle (the anti-yield-trap posture).

### 3. The competitive field
Fifth Person S-REIT Data, YieldSavvy, ShareInvestor REIT Screener, Growbeansprout, REITsavvy.
Almost all are **price-derived screener tables** (yield, P/B, DPU, NAV, gearing, property yield),
fast but **shallow** — they stop at portfolio-level ratios, do **not** surface per-property /
per-tenant / debt-maturity detail, and do **not cite the source**.

### 4. Our differentiator (the gap)
Deep **annual-report fundamentals nobody else surfaces cleanly**, with **page-level provenance** to
the source PDF: per-property valuation/occupancy/NPI, tenant concentration & industry mix, trade-mix
breakdown, land-tenure/lease-expiry, WALE — all citable. Competitors stop at ratios; we go a layer
deeper *and prove it*. Marry that with sectors.app's live price/financials = "screener depth +
annual-report truth."

### 5. The business angle
The goal — penetrate Singapore from Indonesia — implies (at least) **two audiences**: Singapore-local
income investors, and regional (incl. Indonesian) investors seeking SG/SGD exposure. They want
different things, which is why the design-thinking run simulates distinct personas.

## The data we actually hold (the `[OURS]` source)

36 Singapore REITs' **FY2025 annual-report data**, extracted into the `sgx_reit_*` schema, with
**page-level provenance for every field**. Fields: sub-sector / management / income_model; the FY
KPIs (portfolio value, gross revenue, NPI, net distributable income, DPU, distribution record,
unitholders, aggregate leverage/gearing, interest coverage, cost of debt, weighted-avg debt
maturity, NAV/unit, WALE, portfolio occupancy); **per-property** rows (valuation, tenure/lease,
occupancy, NPI, trade-mix, GLA/NLA/GFA, country); top-tenant concentration; trade-mix; full
financial statements + line items; property transactions; extraction notes/flags.

### The seam (a hard design constraint)
- **`[OURS]`** = annual (FY2025), deep, per-property/per-tenant, **page-cited**; refreshes ~yearly.
- **`[LIVE]`** = distribution yield on current price, P/B, daily price performance, yield-spread vs
  SG 10Y, SGD/IDR FX — from **sectors.app's existing market-data layer**, not from us.
- The design must keep these visibly, datedly separate so a live price-yield never reads as live
  beside a year-old NAV/gearing.

### Verified data facts (caught during synthesis — they shape/kill features)
- We hold **8** sub-sector labels, not 7 — there is a `"Specialized"` cohort of **n=1** (8C8U)
  outside the brief's taxonomy. → taxonomy reconciliation is a build blocker.
- **FFO is null in 36/36** — SG REITs disclose distributable income, not US-style FFO. → teach NDI
  as the SG equivalent; never fabricate FFO.
- **No per-year debt-maturity field exists anywhere** — we hold only the single
  `weighted_avg_debt_maturity` scalar (null for ~4 names). → a year-by-year maturity *ladder* is
  uncbuildable today; replaced by a refinancing-pressure triad. (Biggest cut — see brief §7.)

## Sources

- [Sectors — API-first Financial Data for SEA](https://sectors.app/) · [SGX ticker page example (OV8)](https://sectors.app/sgx/ov8) · [Enterprise / database](https://sectors.app/enterprise)
- [DBS — How to Evaluate and Analyse S-REITs (ABCD framework)](https://www.dbs.com.sg/personal/articles/nav/investing/evaluating-reits)
- [Fifth Person — S-REIT Data (LIVE daily)](https://sreit.fifthperson.com/)
- [YieldSavvy — REITs screener](https://app.yieldsavvy.com/)
- [The Singaporean Investor — REIT Screener (ShareInvestor)](https://www.thesingaporeaninvestor.sg/the-reit-screener-powered-by-shareinvestor-a-smarter-way-to-analyse-reits/)
- [Growbeansprout — Singapore REITs](https://growbeansprout.com/reits) · [Best Singapore REITs](https://growbeansprout.com/best-singapore-reits)
