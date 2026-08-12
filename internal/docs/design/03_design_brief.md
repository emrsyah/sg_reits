# 03 — Product Design Brief — reits.sectors.app

*Supertype's S-REIT vertical extending sectors.app. Decision-ready synthesis, grounded in the 36
FY2025 page-cited annual reports we actually hold. Output of the design-thinking run
([`02_design_thinking.md`](02_design_thinking.md)).*

> The `/` landing page is designed separately in [`04_landing_page.md`](04_landing_page.md).
> Locked decisions, data-roadmap items, and open questions are tracked in
> [`05_decisions_and_open_questions.md`](05_decisions_and_open_questions.md).

---

## 1. Personas

- **P1 — Wei Lim (SG retail income investor):** local, dividend-focused, time-poor; wants a fast,
  honest "is this payout safe?" read and picks between two names in a sub-sector.
- **P2 — Marcus Tan (analyst / serious DIY) — PRIMARY audience:** ranks cohorts professionally,
  lives in per-property/per-tenant detail, abandons any tool over one unreconcilable figure;
  provenance + export are why he switches and stays.
- **P3 — Rangga Wijaya (Indonesian investor seeking SGD exposure):** the market-penetration wedge;
  newer to S-REITs, doesn't know tickers or which sponsors are blue-chip, needs orientation +
  foreign-individual tax/FX context, already trusts sectors.app NL search for IDX.
- **Inclusivity note (Daniel, beginner):** even though the audience skews advanced, the surface must
  stay friendly to a REIT-curious beginner — good defaults, progressive disclosure, every jargon
  term clickable, no dead-ends. **The beginner experience is the *collapsed first paint*, not a
  separate mode.**

## 2. Positioning Verdict

**Hybrid, but depth-led.** Lead with our page-cited annual-report depth as the differentiated core;
reach parity on the live price layer by **reusing sectors.app's existing market-data infra, never
rebuilding it.**

**Why (from evidence, not preference):**
- *Pure parity-first is ruled out:* all four personas already have fast, free, price-derived
  screeners (Fifth Person, YieldSavvy, ShareInvestor, REITsavvy) and uniformly complain they are
  shallow, un-sourced, and cheerlead yield. A me-too screener has no moat.
- *Pure depth-only is ruled out:* every persona needs live yield-on-price / P-B (and FX, for Rangga)
  as the *entry context* that frames the safety read — and they explicitly accept this comes from
  sectors.app's live layer.
- *The decisive signal:* our unique assets — page-level provenance, per-property/per-tenant depth,
  the flags/notes layer, visible reconciliation — are exactly what the PRIMARY audience (Marcus)
  switches tools for and what every persona names as their #1 trust factor.

**The non-negotiable consequence:** a clear, persistent, **dated LIVE-vs-ANNUAL seam.** Our deep
data is FY2025-only and refreshes ~yearly; a live price-yield sitting next to a year-old NAV/gearing
must never read as live. The seam is enforced *per-field* (each fundamental stamped "FY2025 as
reported"), not just as a section divider.

## 3. Prioritized Jobs-To-Be-Done

**High (the core loop — build first):**
1. **Judge whether a distribution is safe / not a yield trap** by reading gearing, ICR, cost of debt,
   debt maturity, occupancy, WALE and DPU coverage *together*. — *All personas. The one job everyone names.*
2. **Verify any number against its annual-report page** (one-tap drill-to-PDF). — *All personas. The moat made visible.*
3. **Understand WHY a yield/DPU is weird** via plain-English flags (rights issues, divestments, EMA
   no-NPI, dual-currency, anonymized tenants). — *All personas.*
4. **Compare REITs within a sub-sector on safety fundamentals**, not headline yield. — *P2 lead; P1/P3 for "good for its cohort."*
5. **Decompose the portfolio asset-by-asset and tenant-by-tenant** to find hidden weakness. — *P2 signature; P3/Daniel "look under the hood" conversion.*

**Medium (round out / retention):**
6. Map refinancing pressure from gearing/ICR/cost-of-debt/WADM. *(A per-year ladder is NOT in our data — see §7.)* — *All personas.*
7. Get oriented on the 7 sub-sectors (defensive vs cyclical, counts, blue-chip sponsors). — *P3, Daniel.*
8. Learn vocabulary in-context (definition + formula + healthy range). — *Daniel, P3, P1.*
9. Foreign-individual SGD after-tax / FX context (90% payout, individual exemption). — *P3 wedge.*
10. Cited export to CSV/Excel with page refs preserved. — *P2 power feature.*
11. Re-check holdings for drift at results time. — *P1/P2/P3; honestly framed as ~yearly, not a live monitor.*

## 4. Recommended Information Architecture

Data-source tag: **[OURS]** = FY2025 page-cited annual data · **[LIVE]** = sectors.app market layer
(labelled + dated) · **[EDIT]** = colleague editorial guides (`guides_ux/`).

### A. Single-REIT detail page (the spine — progressive disclosure top to bottom)

| Module | Contents | Source | When |
|---|---|---|---|
| **Hero: Distribution-Safety Verdict** | Plain-English verdict sentence + Stronger/Mixed/Watch band synthesized from gearing-vs-50%-cap, ICR, cost_of_debt, WADM, occupancy, WALE, NDI-vs-DPU. Live yield/P-B shown beside it inside a dated LIVE frame with "a high yield is a question, not an answer." | [OURS] verdict + drivers; [LIVE] yield/P-B | **MVP** |
| **"How we computed this" panel** | Each driver chip → its own source page + threshold + as-of date. The verdict itself carries a methodology note, NOT a source chip (it is derived, not extracted). | [OURS] | **MVP** |
| **Inline anomaly flags** | Plain-English callouts where the weird number appears (DPU period split around a Jun-2025 raise; EMA no-NPI; dual-currency; anonymized tenants). | [OURS] flags/notes | **MVP** |
| **Refinancing snapshot** | Gearing gauge vs 50% ceiling + WADM + cost_of_debt + ICR as a "refinancing pressure" triad against named thresholds; fixed/floating % only where disclosed (~12/36); explicit "full maturity schedule not disclosed in AR" note. **Not a year-by-year ladder.** | [OURS] | **MVP** |
| **FY2025 distribution detail** | DPU + NDI coverage; distribution_record rendered as *composed FY2025 periods* with the equity-raise flag inline — labelled "FY2025 components," NOT a multi-year trend. | [OURS] | **MVP** |
| **Portfolio decomposition (per-property)** | Sortable table: market_valuation, occupancy_rate, lease_expiry/land_tenure, country, category, GLA/NLA/GFA. NPI/npi_pct as *optional* columns that render "segment-level only — not disclosed per property" where absent. Reconciliation badge (Σ valuations = total investment properties). Each row page-cited. | [OURS] | **MVP** |
| **Tenant concentration + trade-mix** | Top-tenant table (rank, client_name, industry, revenue_pct + pct_basis); top-1/top-10 concentration bar; trade-mix donut with basis; anonymized-tenant flag. | [OURS] | **MVP** |
| **Financials & line_items** | Income statement / balance sheet / cash flow from line_items; gross_revenue audited-anchor badge; line-items-tie-to-net-income reconciliation as pass/explain. **FFO/AFFO: teach NDI as the SG equivalent (FFO is disclosed in 0/36 — do not fabricate).** | [OURS] | **Later** |
| **Profile, transactions & provenance ledger** | sub_sector + management (sponsor/manager/trustee) + income_model; property_transaction; per-field source_page ledger + columns_never_fillable honest gaps; docked R2 PDF reader (presigned, #page anchor, page_offset-corrected). | [OURS] + R2 | **MVP** (ledger + reader) / **Later** (transactions) |

### B. Sub-sector explorer (the on-ramp / front door)

| Module | Contents | Source | When |
|---|---|---|---|
| **7 sub-sector cards** | Defensive↔cyclical axis, name count, dominant sponsors. **Reconcile the 8th label first:** our data has *8* labels including a "Specialized" cohort of n=1 (8C8U) — reclassify into one of the 7 with a note, or label it explicitly and redirect n=1 cohorts straight to the single-name page (no empty cohort screen). | [OURS] profile; [EDIT] outlook copy; [LIVE] cohort yield band | **MVP** |
| **Cohort medians strip** | Median gearing/WALE/occupancy/NAV per cohort — **n-aware:** median+percentile only at n≥5 (Diversified 11, Industrial 6, Retail 5, Office 5); show range + printed n at n=2–4 (Hospitality 4, Healthcare 2, Data Centre 2); suppress at n=1. | [OURS] | **MVP** |

### C. Safety Screener + Head-to-Head Compare

| Module | Contents | Source | When |
|---|---|---|---|
| **Screener (Simple mode default)** | ~6 columns, **default-sorted by Distribution-Safety composite, NOT yield**; yield is the last column with risk drivers adjacent; cohort micro-bar per cell (n-aware). | [OURS] structural; [LIVE] yield/P-B (fenced column group) | **MVP** |
| **Structural filters** | gearing-vs-50%-cap, ICR threshold, cost-of-debt band, WALE floor, WADM, blue-chip sponsor (derived from management — editorial/fragile, flag as such), occupancy floor, country, has-flags. **Income model = multi-value facet (6 values) with result counts, NOT a binary "EMA" filter** (only 1/36 is entrusted_management). | [OURS] | **MVP** (numeric filters) / **Later** (sponsor, income-model facet) |
| **Analyst-density toggle** | Full column set, keyboard sort, export. | [OURS] | **MVP** |
| **Head-to-Head Compare (2–4)** | Line-by-line safety rows shaded vs thresholds; expand into per-property + per-tenant cited rows; warn on cross-cohort comparison. Stacked debt **ladder is cut** — compare on the refinancing triad + lease-expiry profile instead. | [OURS]; [LIVE] yield row fenced | **Later** |
| **Cited export** | Any table → CSV/Excel with source_page preserved. | [OURS] | **Later** |

### D. Education / glossary / tax (cross-cutting)

| Module | Contents | Source | When |
|---|---|---|---|
| **Teach-on-tap glossary** | Tap any jargon term → definition + formula + **cohort-aware** healthy range (a global range mis-teaches; healthcare vs hospitality WALE differ). Tap, not hover (mobile-safe). | [EDIT] | **MVP** |
| **Foreign-individual tax/FX explainer** | 90% payout, individual SG exemption, gross-of-home note, worked SGD net-yield example. Static rule = [EDIT]; the live FX/net-yield step is fenced as "live · indicative" and degrades to "FX unavailable" rather than guessing. | [EDIT] + [LIVE] FX | **MVP** (rule) / **Later** (live net-yield calc) |

### E. AI / NL search

| Module | Contents | Source | When |
|---|---|---|---|
| **Grounded Q&A** | NL questions answered ONLY from our extracted fields + flags; every numeric clause carries a [p.NN] citation; honest "we don't have this field" path tied to columns_never_fillable; reuse sectors.app NL infra (single source for live numbers — link/embed the /sgx page, don't re-render). | [OURS] corpus; [LIVE] infra | **Later** |
| **Auto-summary verdict (NLG)** | Deterministic templated 2–3 sentence verdict over the six KPIs, every sentence cited — auditable, never free-generated. | [OURS] | **Later (fast-follow)** |

> A non-chat browse spine (explorer + screener) must remain equal-weight to any AI bar — a
> REIT-curious beginner who distrusts chatbots needs a path.

## 5. Signature Differentiators (only we can do these)

1. **One-tap provenance on every fundamental field → exact AR PDF page.** 100% source_page coverage
   on property rows (1624/1624), the page_offset plumbing already exists, PDFs are in R2.
   Structurally impossible for price-screener competitors to copy. *This is THE wedge.*
2. **The layer beneath the ratio table** — per-property + per-tenant decomposition with visible
   reconciliation badges (Σ-valuations-tie-to-total; line-items-tie-to-net-income, rounding deltas
   documented). The "look under the hood" conversion moment.
3. **An honest Distribution-Safety verdict that de-thrones yield** — yield framed as "check the risk,"
   never cheerled, every input driver cited and thresholded.
4. **Inline plain-English anomaly flags from the reconciliation/notes layer.** Competitors show the
   weird number silently; we explain it. *(Requires an editorial rewrite — raw notes are internal-QC
   dialect: "IPUD," "FRS116," "Note 22.")*
5. **Cited export** — depth flows into the analyst's model with page refs intact, replacing hours of re-keying.

## 6. UX Principles for Mixed Skill Levels

- **Progressive disclosure is the spine.** First paint of every REIT page = the Safety Verdict
  sentence + band + one-line "why," glanceable on a phone. Depth unfolds downward; the analyst
  reaches density by *expanding*, the beginner stays simple by *not* expanding. Treat the collapsed
  first paint as the actual product for P1/P3.
- **Never cheerlead yield.** Live yield always renders beside its risk drivers with the "a high yield
  is a question, not an answer" frame, for every persona.
- **Peer-relative, but n-aware.** Numbers shown against named thresholds (50% gearing cap, cohort
  WALE/ICR) and the *right* sub-sector cohort — with cohort n printed, percentile only at n≥5, range
  at n=2–4, suppressed at n=1. Don't fabricate statistical precision over a 36-name universe.
- **Teach in-context, tap not hover.** Glossary on tap (hover is invisible on mobile); definition +
  formula + cohort-aware healthy range; advanced users ignore it.
- **Verdict = signal, not advice.** Health-signal framing, "how we computed this" always one tap
  away, auto-caveat or suppress where flags indicate structural distortion (EMA, one-off raise).
  For amber/red, give a "what to watch" next step — no dead-ends.
- **Honest gaps over false precision.** Genuinely-missing fields show a labelled note from
  columns_never_fillable ("EMA model — no per-property NPI disclosed"), never a blank or a fabricated zero.
- **The seam is active, not passive.** Stamp the FY2025 as-reported date on each fundamental driver,
  label our data "refreshes ~yearly," fence live columns under a dated LIVE header — and surface
  "price has moved since the FY2025 report" when live yield diverges materially.
- **Calm, mobile-first, zero-config.** Start from a ticker or a sub-sector and land on the safety read immediately.

## 7. Explicitly CUT / Deferred

**Cut (data does not exist — building these would fabricate numbers, violating our locked
never-compute/impute invariant):**
- **Year-by-year debt-maturity LADDER.** Verified: 0/36 financial files contain any per-year/
  per-tranche maturity field; we hold only the single `weighted_avg_debt_maturity` scalar (null for
  ~4 names: AW9U, CY6U, T82U + one). → Replaced by the **refinancing-pressure triad** (WADM +
  cost_of_debt + ICR + gearing). A true ladder requires a **new extraction field first** — a
  data-roadmap item, not a launch feature. This was the most-promised visual across three lenses
  and is the single biggest overclaim.
- **Multi-year DPU TREND chart.** Data is FY2025-only; `distribution_record` is *intra-year period
  splits*, not a time series. Plotting it naively makes the Jun-2025 equity raise look like a cut. →
  Ship FY2025 distribution as composed periods with the flag inline; defer real trend until FY2026 accrues.
- **FFO/AFFO as a stored field.** `funds_from_operation` is null in 36/36 — SG REITs disclose
  distributable income, not US-style FFO. → Teach NDI as the SG equivalent.

**Deferred (real but secondary, or live-dependent):**
- Full financial line_items, property_transaction, cited export, Head-to-Head Compare → v2 (after
  the safety verdict + provenance + per-property + flags MVP ships).
- Grounded AI Q&A + auto-summary NLG → fast-follow; high eval/QA burden, and a single
  confidently-wrong cited answer damages the whole trust pitch.
- Live net-yield / FX calculation for P3 → fenced as live-layer-dependent; ship the static tax rule now.
- Binary "EMA" filter and global healthy-range thresholds → cut as mis-modeled; replaced by 6-value
  income-model facet and cohort-aware ranges.

## 8. Open Questions & Recommended Next Step

> Tracked and kept current in [`05_decisions_and_open_questions.md`](05_decisions_and_open_questions.md).

**Open questions to resolve before build:**
1. **Taxonomy reconciliation (blocking the explorer):** the 8th "Specialized" label (8C8U, n=1) and
   the n=1/n=2 cohorts (Healthcare, Data Centre) — reclassify, or treat single-name cohorts as direct redirects?
2. **Live-layer contract:** exact ticker-mapping, fields, latency and failure-state behaviour from
   sectors.app's market layer (yield-on-price, P/B, yield-spread vs SG 10Y, SGD/IDR FX).
3. **R2 PDF deep-link reliability:** presigned URL expiry (3600s), per-report page_offset
   correctness, #page anchor behaviour across mobile browsers — a broken "see source" link damages
   the exact trust the moat depends on.
4. **Editorial rewrite ownership:** who converts internal-QC notes (IPUD, FRS116, "Note 22") into
   plain-English flag copy, and who authors cohort-aware healthy ranges?
5. **Verdict methodology + liability:** the exact rule (inputs, thresholds, weights), the "not advice"
   framing, and auto-suppression logic for EMA/one-off-distorted names (e.g. A17U).
6. **Audience-mix bet:** depth-led assumes enough P2 traffic to monetize; fallback if realized
   traffic skews P1/P3 wanting a fast yield read?

**Recommended next step:** Build a **clickable wireframe/prototype of the single-REIT detail page**
for two deliberately contrasting names — one clean (e.g. AJBU / Data Centre) and one full of honest
edge-cases (A17U: Jun-2025 equity-raise DPU split, segment-only per-property NPI, rounding-delta
reconciliation). Prototype the collapsed-first-paint Safety Verdict, one provenance click-through to
the R2 PDF page, and the refinancing-triad-not-ladder treatment. This proves the moat (provenance),
the hardest UX call (the seam + verdict honesty), and the biggest cut (no ladder) on real data in
one artefact — the cheapest way to validate the depth-led bet before committing engineering.
