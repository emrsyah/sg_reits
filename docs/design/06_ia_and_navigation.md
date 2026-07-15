# 06 — Information architecture, navigation & interaction model

How users move through reits.sectors.app. Builds on the IA *modules* in
[`03_design_brief.md`](03_design_brief.md) §4 and the sitemap in [`04_landing_page.md`](04_landing_page.md);
this doc adds the **connective tissue** — menu structure, navigation devices, interaction patterns,
wayfinding, and responsive behaviour — every choice traced to a research finding in
[`01_research.md`](01_research.md).

---

## 0. The five design forces (everything below serves these)

| Force | Source | Consequence for navigation |
|---|---|---|
| **Mixed skill on one surface** — advanced majority (P2) + friendly to all (P3/beginner) | persona decision | Progressive disclosure + a density toggle, not separate "pro/simple" apps. |
| **Anti-yield-trap** — yield is a question, not an answer | DBS + every source | No nav default sorts/leads by yield; safety-first ordering everywhere. |
| **The provenance wedge** — one-tap to the AR page | our moat | "See the source" is reachable from *every number* in ≤1 action. |
| **The LIVE/ANNUAL seam** — FY2025 annual vs live price | our data reality | Data-freshness is a first-class, *global* nav element, not buried. |
| **Search-first + browse spine** — sectors.app DNA, but beginners distrust chat | sectors.app + persona | A command palette **and** an equal-weight browse spine; neither replaces the other. |

**Small-universe dividend:** only **36 REITs / 8 sub-sector labels**. The IA can be **shallow & wide
and fully browsable** — no pagination walls, no deep trees. Favour listing over hiding.

---

## 1. IA model (the object model)

Five primary objects; everything is a view over them.

```
Market overview ( / )
      │ routes to
      ├──► REIT  ×36  ──belongs to──► Sub-sector ×7 (+1 to reconcile)
      │      │ has-many: properties, tenants, trade-mix, line-items, flags
      │      └─ every metric ──has──► provenance (AR PDF page)   ◄── the wedge
      ├──► Screener      (filter/rank tool over all 36 REITs)
      ├──► Compare       (transient view over 2–4 REITs)
      └──► Learn         (glossary · how-to-evaluate · tax & FX)
```

- **REIT** is the atomic unit → the detail page is the spine of the whole product.
- **Sub-sector** is a grouping lens *and* the newcomer on-ramp.
- **Screener / Compare** are *tools/views*, not content — Compare is transient (a tray, not a menu item).
- **Learn** is cross-cutting and reachable in-context (glossary on tap), not just a destination.

Depth is **≤3 clicks to any REIT** from anywhere: `overview → sub-sector → REIT`, or `search → REIT`,
or `screener → REIT`.

---

## 2. Global (primary) navigation — the top bar

Deliberately minimal; a 36-name site doesn't need a mega-IA.

```
┌────────────────────────────────────────────────────────────────────────────────────┐
│ ▦ REITs   [ ⌕  Search a REIT or ask…              ⌘K ]   Explore ▾   Screener   Learn ▾ │
│                                       FY2025 · live 21 Jun ▾   ◐ Simple│Analyst   ★   �myacct │
└────────────────────────────────────────────────────────────────────────────────────┘
```

| Slot | Item | Why it's here (research) |
|---|---|---|
| Brand | **▦ REITs → `/`** | Always-home; the market overview. |
| Center | **⌕ Search (palette, ⌘K)** | sectors.app DNA; the fast-jump for P2, the discovery path for P3 who doesn't know tickers. First-class, not an afterthought icon. |
| Primary | **Explore ▾** | Guided browse on-ramp (sub-sector mega-menu) — P3/beginner orientation. |
| Primary | **Screener** | The filter/rank tool — P2's home base. Separate from Explore because it's a *different interaction mode* (rank vs orient). |
| Primary | **Learn ▾** | Glossary / how-to-evaluate / tax & FX — the no-dead-end safety net for newcomers. |
| Utility | **Data-freshness chip** `FY2025 · live <date>` | The **seam made global** — one persistent place that says "fundamentals are FY2025; price is live." Opens a popover explaining it. |
| Utility | **◐ Density: Simple ⇄ Analyst** | The mixed-skill reconciler, global so it persists across pages. Defaults Simple (mobile) / remembers choice (returning P2). |
| Utility | **★ Watchlist · account** | Follow/recall; per-reviewer state. |

**Not in the top bar, on purpose:** Compare (→ a tray), individual REITs (→ search/explore),
"highest yield" (→ never a primary entry; anti-yield-trap).

### Explore ▾ — sub-sector mega-menu
```
Explore ▾
┌───────────────────────────────────────────────────────────┐
│  BY SUB-SECTOR        defensive ◄─────────────► cyclical     │
│   Healthcare (2)   Data Centre (2)   Industrial (6)          │
│   Diversified (11) Retail (5)  Office (5)  Hospitality (4)    │
│  ─────────────────────────────────────────────────────────  │
│   ▸ All 36 REITs        ▸ Compare REITs        ▸ Screener →   │
└───────────────────────────────────────────────────────────┘
```
- Cards ordered on the **defensive↔cyclical axis** (teaches risk posture, not alphabetical).
- Counts printed (n-aware honesty); **single-name cohorts route straight to the REIT** (no empty
  cohort screen) — pending the taxonomy decision (Q1).
- "All 36 REITs" is a flat browsable index — embraces the small universe.

---

## 3. Search — the command palette (first-class navigation device)

Triggered by the top-bar box or `⌘K`/`Ctrl-K`. One input, progressive intent:

```
┌ ⌕  apl|                                              ⌘K ┐
│ REITs                                                    │
│   ● AJBU · AIMS APAC REIT        Industrial · Stronger    │
│   ● A17U · CapitaLand Ascendas   Industrial · Mixed       │
│ Sub-sectors                                               │
│   ▸ Industrial (6)                                        │
│ Ask  (grounded · cites pages)                  [Later]    │
│   “which industrial REITs have gearing under 38%?”        │
│ Jump                                                      │
│   ⚖ Compare …   📖 Glossary: “gearing”   ▦ Screener        │
└──────────────────────────────────────────────────────────┘
```
- **Typeahead by ticker *and* name *and* sub-sector keyword** — critical for P3 (knows "industrial",
  not "A17U"). Each result shows its safety band inline (anti-yield-trap framing from the first glance).
- **Recent / watchlist** on empty state.
- **Ask mode** (grounded NL Q&A) lives here too, but is **`Later`** — MVP routes the palette to
  browse/jump only, so the product is whole without AI. The browse spine (Explore/Screener) stays
  equal-weight; a chat-averse beginner never needs the palette's Ask mode.

---

## 4. Secondary (in-page) navigation — the single-REIT spine

The detail page is long (8 progressive-disclosure modules). It needs its own nav so P2 can teleport
and P1 can stay shallow.

```
┌─ STICKY MINI-HEADER (appears on scroll) ───────────────────────────────────┐
│ AJBU · AIMS APAC REIT     ● Stronger      FY2025      + Compare    ★         │
└─────────────────────────────────────────────────────────────────────────────┘
  Home › Industrial (6) ‹ prev | next ›                    ← breadcrumb + peer switch

  ┌ ANCHOR RAIL (scroll-spy) ┐   ┌ CONTENT ──────────────────────────────────┐
  │ ● Safety verdict          │   │  [Hero verdict + live yield (dated frame)] │
  │   Refinancing             │   │  …                                          │
  │   Distribution            │   │  each metric:  value  📄p.42  (?)           │
  │   Portfolio               │   │                  └─ tap → PDF reader sheet  │
  │   Tenants & trade-mix     │   │                            └─ glossary popover│
  │   Financials      [Later] │   │                                             │
  │   Profile & provenance    │   └─────────────────────────────────────────────┘
  └───────────────────────────┘
```

Four in-page devices:
1. **Anchor rail / scroll-spy** — jump to any section; highlights current. Desktop = left rail;
   mobile = sticky horizontal segmented control. Lets the analyst skip to *Portfolio* in one tap.
2. **Sticky mini-header** — name · ticker · **safety band** · **dated chip** · Compare · ★. Context
   is never lost on a long scroll; the seam date travels with you.
3. **Breadcrumb + peer switcher** — `Home › Industrial (6)` is clickable back to the cohort; `‹ prev |
   next ›` walks peers **without going back to the list** (supports the analyst's "compare across the
   cohort" mental model).
4. **Provenance drill** — the signature interaction (see §5.5), available on every number.

---

## 5. Interaction & navigation patterns (the catalogue)

The named interaction types the product uses, each tied to a persona and a research force.

| # | Pattern | What it does | Where | Primary persona | Grounded in |
|---|---|---|---|---|---|
| 5.1 | **Search-first jump** | Palette typeahead → any REIT/sub-sector/term in 2 keystrokes | Global ⌘K | P2, P3 | sectors.app DNA |
| 5.2 | **Guided browse** | overview → sub-sector → cohort → name | Explore menu, landing map | P3, beginner | orientation need |
| 5.3 | **Filter & rank** | facet filters; **safety-default sort** | Screener | P2 | anti-yield-trap |
| 5.4 | **Progressive disclosure** | expand/collapse sections; **Simple⇄Analyst density toggle** | Everywhere; global toggle | all | mixed-skill on one surface |
| 5.5 | **Provenance drill-down** | tap any metric → docked PDF reader at the cited page (`#page`, offset-corrected) | Every number | P2 (trust); all | the wedge |
| 5.6 | **Lateral peer-switch** | `prev/next` within cohort; "compare to peer" | Detail header | P2 | cohort-relative analysis |
| 5.7 | **Compare tray** | multi-select 2–4 (★-style add) → slide-up compare view | Screener, detail, explore | P2 | head-to-head JTBD |
| 5.8 | **Teach-on-tap** | tap a term → glossary popover (def + formula + cohort-aware range) | Inline on any jargon | beginner, P3 | inclusivity, tap-not-hover |
| 5.9 | **Seam-aware reading** | dated chips; "price moved since FY2025" nudge when live yield diverges | Global chip + per-field | all | the seam |
| 5.10 | **Watchlist & recall** | ★ to follow; re-check at results time (framed ~yearly, not a live monitor) | Global ★ | P1, P2, P3 | honest cadence |

**The Compare tray** (5.7) — persistent, collapsible, transient state, *not* a menu item:
```
                                   ┌──────────────────────────────────┐
…browsing the screener…            │ Compare (2)  AJBU ✕  A17U ✕   ⚖ →  │
                                   └──────────────────────────────────┘  ← docks bottom-right
```
Add from anywhere (screener row, detail header, explore card); opens the §4C compare view; warns on
cross-cohort mixing.

---

## 6. Wayfinding & orientation (no dead-ends)

- **Breadcrumbs** are shallow and clickable: `Home › Industrial (6) › AIMS APAC REIT`.
- **"You are here" cohort context** on the detail page: a mini median strip ("gearing 33% · cohort
  median 36%") so a number is never read in a vacuum.
- **No dead-ends, by rule:**
  - amber/red verdict → a **"what to watch"** link, never a flat stop;
  - genuinely-missing data → a labelled note (`columns_never_fillable`) + link to methodology, never a blank;
  - single-name cohort → redirect to the REIT, never an empty list;
  - empty search → recent/watchlist + "browse by sub-sector" fallback.
- **The data-freshness chip is the global "what am I looking at" anchor** — one click explains the seam everywhere.

---

## 7. Responsive behaviour (mobile-first; P1 commutes, beginners are on phones)

| Element | Desktop | Mobile |
|---|---|---|
| Primary nav | Top bar (Explore ▾ / Screener / Learn ▾) | Logo + ⌕ + ☰; **bottom tab bar**: 🏠 Home · 🧭 Explore · ▦ Screener · ★ Watch (thumb-reachable) |
| Search | Inline box + ⌘K | Full-screen search sheet (tap ⌕) |
| In-page section nav | Left anchor rail (scroll-spy) | Sticky **horizontal** segmented scroll-spy under the mini-header |
| Provenance / PDF | Docked side reader | Full-screen **slide-up sheet**; "back to data" persistent |
| Glossary | Tap → popover | Tap → bottom sheet (**never hover**) |
| Density | Remembers last (often Analyst) | Defaults **Simple**; Analyst opt-in |
| Compare tray | Bottom-right dock | Collapses to a count pill; expands full-screen |

```
mobile bottom tab
┌───────────────────────────────┐
│   🏠      🧭       ▦       ★     │
│  Home  Explore Screener Watch  │
└───────────────────────────────┘
```

---

## 8. Persona journeys mapped onto the nav (proof the structure serves each)

| Persona | Entry | Path through the nav | Devices used |
|---|---|---|---|
| **P1 retail income** (mobile, time-poor) | Bottom-tab Home | curated "Strongest safety" list → tap name → **collapsed verdict** (done) | 5.2, 5.4, 5.9 |
| **P2 analyst** (desktop) | ⌘K or Screener | Screener → filter gearing/ICR, sort **safety** → open name → anchor-jump *Portfolio* → **drill provenance** → add Compare → export | 5.1/5.3/5.5/5.6/5.7 |
| **P3 Indonesian newcomer** | Home overview | Sub-sector map (orient) → cohort → name → **glossary taps** + tax/FX → verdict | 5.2, 5.8, 5.9 |
| **Daniel beginner** | "New to S-REITs? Start here" | Learn → how-to-evaluate → linked example REIT (Simple density) → terms on tap, no jargon wall | 5.4, 5.8 |

Every persona reaches its goal in **≤3 primary navigations**, and none is forced through a chatbot or
a yield-sorted wall.

---

## 9. Navigation design principles (the rules)

1. **Browse spine == AI.** Explore + Screener are always equal-weight to the search palette; the
   product is complete with zero AI.
2. **Safety-first ordering, always.** No default view, list, or sort leads by yield.
3. **Provenance in ≤1 action from any number.** If a metric can't be drilled, it shows *why* (honest gap).
4. **The seam is a navigation citizen.** A global dated chip + per-field dates; never let live and
   annual blur.
5. **Progressive disclosure is how one surface fits all.** Density toggle + expand/collapse, not
   parallel apps.
6. **Favour browsability over hiding.** 36 names → flat indexes, no pagination, peers one tap away.
7. **No dead-ends.** Every amber state, missing field, and empty result offers a next move.
8. **Keyboard-first for P2, thumb-first for P1.** ⌘K + j/k/sort hotkeys on desktop; bottom tabs +
   sheets on mobile.

---

## 10. Open navigation decisions (forks to confirm — added to [`05`](05_decisions_and_open_questions.md))

- **N1 — Mobile primary nav:** bottom tab bar (recommended; thumb-reach for P1) vs hamburger only.
- **N2 — Density toggle scope:** global + persistent (recommended) vs per-page.
- **N3 — Detail URL shape:** `/reit/[ticker]` vs reuse sectors.app's `/sgx/[ticker]` (also Q8 in `05`).
- **N4 — Is "Compare" ever a top-level item?** Recommended: no (tray only) — revisit if analysts ask.
- **N5 — Search "Ask" mode in MVP?** Recommended: ship palette as jump-only; Ask is fast-follow.
