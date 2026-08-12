# 04 — Landing page (`/`)

The brief ([`03_design_brief.md`](03_design_brief.md)) details the detail-page spine, the explorer,
and the screener — but not `/` itself. This is the page that does the most work for the **cold**
visitor (especially P3, the Indonesian wedge, who lands not knowing a single ticker).

## What `/` is

**A market-overview + routing hub — not a screener dump, not a marketing splash.** Competitors
(Fifth Person, YieldSavvy) make the screener *be* the homepage: you land on a wall of yield-sorted
rows. That (a) cheerleads yield — against our whole positioning — and (b) strands P3/beginners who
need orientation first. Our `/` **frames the market before it lists it**, then routes fast. It is
also what `guides_ux/reits_brief.md` was drafted for (market size, indices performance, sub-sector
mix — currently placeholders).

Constraint from the brief still applies: **search + "open full screener" must be one tap above the
fold** so the analyst (P2, primary) never feels slowed down.

## What it shows (above the fold → down)

```
┌─────────────────────────────────────────────────────────────┐
│  reits.sectors.app          [ 🔍 search a REIT / ask… ]       │
│  "Singapore REITs, read from the source."                    │
│  [ Browse by sub-sector ]  [ Open safety screener ]          │
│                              New to S-REITs? → Start here     │
├─────────────────────────────────────────────────────────────┤
│  MARKET PULSE   (as of …)                                     │
│  36 S-REITs · S$__b mkt cap · avg yield _._% (LIVE)           │
│  spread vs SG 10Y +_._%  │  median gearing __% (FY25, OURS)   │
│  median occupancy __% · median WALE _._yrs (FY25, OURS)       │
├─────────────────────────────────────────────────────────────┤
│  SUB-SECTOR MAP   (defensive ◄──────► cyclical)               │
│  [Healthcare 2][DataCtr 2][Industrial 6][Diversified 11]…     │
│   each card: count · median yield band · → explorer           │
├─────────────────────────────────────────────────────────────┤
│  CURATED ENTRY (honest cuts, not "top yield")                 │
│  • Strongest distribution-safety  • Lowest gearing            │
│  • Highest occupancy   • Highest yield — w/ risk drivers shown│
├─────────────────────────────────────────────────────────────┤
│  NOTABLE THIS YEAR (our flags layer)                          │
│  rights issues · divestments · dual-currency · EMA names      │
├─────────────────────────────────────────────────────────────┤
│  LEARN: glossary · how to evaluate an S-REIT · SGD tax & FX   │
└─────────────────────────────────────────────────────────────┘
```

| Module | What / why | Source | When |
|---|---|---|---|
| **Search-first hero** | sectors.app DNA; instant route to any name or NL question. Tagline states the positioning ("read from the source"). | [LIVE] infra | **MVP** |
| **Market Pulse band** | `reits_brief.md` made real: # names + market cap + avg yield + **yield-spread vs SG 10Y** (the context number every guide cites) — *plus* our structural aggregates (median gearing vs 50% cap, occupancy, WALE). Carries the **dated seam** (live vs "FY2025 as reported"). | [LIVE] price aggregates · [OURS] structural medians | **MVP** |
| **Sub-sector map** | The 7 cards on a defensive↔cyclical axis = the primary browse on-ramp *and* orientation for P3/beginner. n-aware (counts shown). Resolve the 8th "Specialized" label here. | [OURS] + [EDIT] | **MVP** |
| **Curated entry lists** | P1's "find income" job *without* yield-trapping: lead with **safety/gearing/occupancy** cuts; include a "highest yield" list but render its **risk drivers inline** so the frame holds. Each routes to a detail page. | [OURS] + [LIVE] yield | **MVP** |
| **Notable this year** | Puts our **flags/notes differentiator on the front door** — "these names did something unusual this year." No competitor can show this. (Needs the editorial rewrite of QC notes.) | [OURS] flags | **Later / fast-follow** |
| **Learn rail** | Glossary + "how to evaluate" + SGD tax/FX — the beginner/P3 path, always present, never blocking. | [EDIT] | **MVP** |
| **Index performance viz** | `reits_brief.md`'s "[Insert plot]" — iEdge S-REIT index performance. Nice-to-have, but **external/live-dependent** data we don't yet hold. | [LIVE]/external | **Later** |

## The one fork worth a decision

**`/` as overview hub** (recommended above — frames, then routes; fits depth-led + the P3 wedge)
**vs. `/` as the screener itself** (competitor pattern — fastest for P2, but yield-forward and cold
for newcomers).

**Recommendation:** overview hub. It's the surface that differentiates us in the first five seconds
and serves the Indonesian-newcomer wedge — with search + "open screener" prominent enough that P2
loses nothing. Flip it only if the audience proves to skew so heavily toward analysts that they just
want the table. *(Status: recommended, not yet locked — see
[`05_decisions_and_open_questions.md`](05_decisions_and_open_questions.md).)*

## Routing / sitemap implied

```
/                      overview + routing hub (this page)
/screener              full safety screener (brief §4C)
/sub-sector/[slug]     sub-sector explorer (brief §4B)
/reit/[ticker]         single-REIT detail spine (brief §4A)   ← or mirror sectors.app's /sgx/[ticker]
/learn                 glossary · how-to-evaluate · tax & FX (brief §4D)
```
*(Detail-page URL shape — `/reit/[ticker]` vs reusing sectors.app's existing `/sgx/[ticker]` — is an
open question tied to the live-layer integration.)*
