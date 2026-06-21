# reits.sectors.app — Design Base

The single source of truth for the **reits.sectors.app** frontend: the research it stands on,
the design-thinking process that produced it, the product brief, and the open decisions.
Everything in this folder is the foundation we build the frontend from.

**Product:** a Singapore-REIT investor surface that extends **sectors.app** (Supertype's API-first
SEA financial-data platform). It is Supertype's wedge to penetrate the Singapore market from Indonesia.

**Status:** design foundation — no frontend code yet. Created 2026-06-21.

---

## The Direction (north star)

> **Singapore REITs, read from the source.**

- **Positioning — hybrid, but depth-led.** Lead with our **page-cited annual-report depth** (the
  one thing competitors can't copy); reach parity on live price/yield by **reusing sectors.app's
  market-data layer, never rebuilding it.** Full reasoning in [`03_design_brief.md`](03_design_brief.md) §2.
- **The wedge:** one-tap provenance on every fundamental → the exact annual-report PDF page.
  Competitors (Fifth Person, YieldSavvy, ShareInvestor, REITsavvy) are shallow, un-sourced,
  yield-cheerleading price screeners. We go one layer deeper and *cite it*.
- **The anti-yield-trap posture:** a high yield is framed as *a question, not an answer* — every
  surface reads yield beside its risk drivers (gearing, ICR, cost of debt, WADM, occupancy, WALE).
- **The seam (non-negotiable):** our deep data is **FY2025 annual, refreshes ~yearly**; live
  yield/P-B/FX come from sectors.app's live layer. A persistent, **per-field dated LIVE-vs-ANNUAL
  seam** keeps year-old fundamentals from reading as live.

## Personas

| | Persona | One line |
|---|---|---|
| **P1** | Wei Lim — SG retail income investor | Time-poor; wants a fast, honest "is this payout safe?" read. |
| **P2** | Marcus Tan — analyst / serious DIY **(PRIMARY)** | Lives in per-property/per-tenant detail; switches tools for provenance + export. |
| **P3** | Rangga Wijaya — Indonesian investor (the **wedge**) | Wants SGD exposure; needs orientation + foreign-individual tax/FX context. |
| — | Daniel — REIT-curious beginner (inclusivity lens) | The collapsed first paint *is* his product; progressive disclosure, no dead-ends. |

---

## What's in this folder

| File | What it is |
|---|---|
| [`01_research.md`](01_research.md) | The research process + findings (sectors.app DNA, what S-REIT investors track, the competitive field, our differentiator, the business angle) + sources, and the data we actually hold. |
| [`02_design_thinking.md`](02_design_thinking.md) | How the design-thinking run was structured — the 5-phase multi-agent workflow, the personas, the ideation lenses, the data-grounding/verification step. Reproducible. |
| [`03_design_brief.md`](03_design_brief.md) | **The core deliverable** — personas, positioning verdict, prioritized JTBD, full information architecture, signature differentiators, UX principles, explicit cuts, open questions. |
| [`04_landing_page.md`](04_landing_page.md) | The `/` landing page design (market-overview + routing hub) — not covered in the brief; designed separately. |
| [`05_decisions_and_open_questions.md`](05_decisions_and_open_questions.md) | Locked decisions, the data-roadmap items (features we cut because the data doesn't exist yet), the blocking open questions, and the recommended next step. |

## Related, outside this folder

- **`guides_ux/`** (repo root) — colleagues' editorial drafts: S-REIT intro, 7-sub-sector taxonomy,
  9-metric glossary. The product's **vocabulary/voice reference** (tagged `[EDIT]` in the brief).
  Secondary to this folder's design-thinking findings, by the stakeholder's direction.
- **`docs/fe_data_contract.md`** — the live backend contract (Supabase tables + R2 PDFs). Note: it
  was written for the **internal review cockpit**; the *data shapes* and the R2 provenance plumbing
  are reused by this public product, but the cockpit UX is a different surface.
- **`schema/models.py`, `schema/sgx_reit_schema.md`** — canonical data shapes (the `[OURS]` source).

---

## How to use this folder

1. Read this README for the direction, then [`03_design_brief.md`](03_design_brief.md) for the product.
2. Before any build, clear the blockers in [`05_decisions_and_open_questions.md`](05_decisions_and_open_questions.md)
   (taxonomy of the 8th sub-sector label; the live-layer data contract).
3. Recommended next artefact: a clickable wireframe of the single-REIT detail page on two
   contrasting real names (clean: AJBU/Data Centre · edge-case: A17U), plus the `/` flow.
