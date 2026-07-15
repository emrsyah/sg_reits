# 00 — Frontend agent's guide to this folder

**For:** a fresh frontend agent picking up **reits.sectors.app** (an S-REIT investor product extending
sectors.app). **This is a *reading guide*, not a spec** — the spec is the other docs in this folder.
It tells you what to read, in what order, what's a hard rule, and where to start.

Repo: `C:\Users\emirsyah\supertype\s_reits` · You are in the canonical design base: **`docs/design/`**

---

## 1. What you're building (30 seconds)
A Singapore-REIT investor surface whose moat is **deep, page-cited annual-report fundamentals** (per
property / per tenant / debt profile), with one-tap provenance back to the source PDF — vs shallow
price-only competitor screeners. Positioning is **hybrid, depth-led**. Full direction: read
`README.md` first.

## 2. Read the docs in THIS order (not numeric order)
| Step | File | Why / what you get |
|---|---|---|
| 1 | `README.md` | North star, positioning, **build priority**, personas, folder map. Start here. |
| 2 | `03_design_brief.md` | **What to build** — personas, prioritized JTBD, full IA module list (each tagged MVP/Later + data source), differentiators, UX principles, and the explicit **cuts**. The core. |
| 3 | `06_ia_and_navigation.md` | **How it's structured** — IA object model, global + in-page nav, menu structures, the interaction-pattern catalogue (incl. the provenance drill), responsive behaviour, per-persona journeys. |
| 4 | `07_data_contract_ui.md` | **Engineering contract** — every UI module bound to exact `sgx_reit_*` fields, units/formatting rules, the provenance formula, source taxonomy + authority rule, derived-value compute locations. Your field reference. |
| 5 | `08_verdict_methodology.md` | The Distribution-Safety verdict algorithm (the hero). **PROPOSAL — thresholds pending sign-off**; build the structure, treat numbers as provisional. |
| 6 | `04_landing_page.md` | The `/` page (overview + routing hub) + the implied sitemap. |
| 7 | `05_decisions_and_open_questions.md` | **Check before building each piece** — locked decisions, the **blockers**, the data-roadmap cuts, and the open questions with owners. Living doc. |
| — | `01_research.md`, `02_design_thinking.md` | Background/evidence (the *why*). Read only if you need to justify a decision; skip to ship. |

## 3. The non-negotiable rules (do not violate)
1. **Provenance everywhere.** Every `[REIT-DB]` value drills to its source PDF page in ≤1 action.
   Mechanic in `07_data_contract_ui.md` §2. If `source_page` is null, show "page not attributed" — never fabricate one.
2. **Never invent/impute data.** If a field is null or doesn't exist, render an honest gap
   (`07` §3, `08` §6) — never a zero, a guess, or a derived number passed off as disclosed.
3. **The seam is per-field and dated.** `[REIT-DB]` = FY2025 annual; `[PROD]` = live/history. A live
   yield must never read as live next to a year-old NAV. `07` §1.
4. **Anti-yield-trap.** No view defaults to or leads with yield; yield always sits beside its risk
   drivers. `03` §6, `06` §9.
5. **Progressive disclosure.** Collapsed first paint = the product for beginners; depth unfolds for
   analysts. One surface, density toggle — not two apps. `03` §6.

## 4. Where to start (build priority)
- **REITs DB first.** The entire MVP builds from `sgx_reit_*` **alone** (verdict, refinancing,
  distribution, portfolio/tenant decomposition, provenance). Prod tables are enrichment, mostly
  deferred. `README.md` "Build priority" + `05` D7.
- **First artefact (recommended):** a clickable **single-REIT detail page** on two real names — clean
  **AJBU** (Data Centre) and edge-case **A17U** (Jun-2025 equity-raise DPU split, segment-only NPI).
  This exercises the verdict, the provenance drill, the seam, and the honest-gap handling at once.
- Then: sub-sector explorer → safety screener → landing. (`03` §4 has MVP/Later tags per module.)

## 5. Blocked / pending before you build certain things (see `05`)
- **Verdict thresholds** (`08`, Q5) — build the engine; numbers need analyst sign-off.
- **Live price layer** (Q2, Q9) — needed for yield/P-B; **optional for v1**, ship fundamentals without it.
- **Content/copy** (Q4) — flag plain-English text, glossary ranges, verdict wording: owned by the user, don't write financial copy yourself.
- **Taxonomy** (Q1) — the 8th "Specialized" sub-sector label (n=1) must be resolved before grouping.
- **Prod data integration** (Q9–Q13, user-owned) — does NOT block a REIT-DB-only MVP.

## 6. Do NOT build these (data doesn't exist — `05` data-roadmap)
Year-by-year **debt-maturity ladder** · **fixed/floating debt %** · **multi-year DPU/gearing trend** ·
**FFO** (null 36/36 → teach NDI) · **DPU coverage ratio** (no units-outstanding). Building any of
these means fabricating numbers — don't.

## 7. External references (data shapes & assets)
- `schema/models.py` + `db/schema.sql` — **canonical field names/shapes** for `sgx_reit_*` (the `[REIT-DB]` source).
- `docs/fe_data_contract.md` — live Supabase + R2 wiring. ⚠️ Written for the **internal review cockpit**,
  not this public product; reuse the **data shapes + R2/provenance plumbing**, ignore the cockpit UX.
- `guides_ux/` — colleagues' editorial drafts (S-REIT intro, 7-sub-sector taxonomy, 9-metric glossary) = `[EDIT]` vocabulary/voice source.
- Visual/CSS design system is **already handled in the FE** — this base is non-visual (IA, data, behaviour); don't redesign styling.

## 8. Current state
- Design base `01`–`08` + `05` tracker: **complete and handoff-ready**. No frontend code written yet.
- Extraction is done (36 FY2025 S-REITs); data loaded to Supabase; PDFs in R2 (`reits-ar`).
- Prod-data integration and content/copy are the user's parallel workstreams (flagged, not blocking the core).
