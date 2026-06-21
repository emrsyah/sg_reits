# 02 — Design-thinking process

How the [`03_design_brief.md`](03_design_brief.md) was produced. Recorded so the result is
auditable and the process is repeatable.

## Method

A **full design-thinking run** — *empathize → define → ideate → critique → synthesize* — executed
as a **multi-agent workflow** (one orchestrated script, 14 sub-agents, ~700k tokens). Each phase
was grounded in the research ([`01_research.md`](01_research.md)) and the real `sgx_reit_*` data,
passed to the agents as a shared context block so nothing was invented.

## Inputs locked before the run (stakeholder decisions)

- **Personas to simulate:** SG retail income investor · analyst/advisor/pro **(primary)** ·
  regional/Indonesian investor — *plus* keep it friendly for a REIT-curious beginner regardless of skill.
- **Positioning (depth vs parity):** *let the research decide* — the run was told to derive the
  positioning verdict from persona evidence, not assume it.
- **Run depth:** full multi-phase (not a quick synthesis).

## The five phases

1. **Empathize** — 4 agents, each *being* a persona (the 3 above + a beginner as the inclusivity
   lens). Each produced: context, goals, jobs-to-be-done, current tools & frustrations, the real
   questions they ask before buying/holding/selling, the data they value most (mapped to what we
   actually have), trust factors, a day-in-the-life scenario, and UX needs.
2. **Define** — 1 synthesis agent over all persona outputs → prioritized JTBD, top pain points,
   "how might we" statements, competitive gaps we can own, the **positioning verdict** (decided from
   evidence), must-have data modules, and cross-cutting principles (incl. inclusivity).
3. **Ideate** — 4 agents, each designing the whole product through **one deliberately different lens**,
   to force diversity:
   - **Depth & provenance** — lead with per-property/per-tenant/debt detail + page-cited "see it in the AR."
   - **Comparison & screening** — peer/sub-sector benchmarking that beats the shallow competitor tables.
   - **Education & guided analysis** — teach how to evaluate; glossary-driven; friendly for all levels.
   - **AI & workflow** — natural-language search, watchlists/alerts/exports, grounded plain-English summaries.
4. **Critique** — each concept adversarially stress-tested by an independent reviewer against:
   (1) **data feasibility** (does it need live/daily data we lack, or finer granularity than annual
   reports give?), (2) **redundancy** with competitors, (3) **accessibility** for the beginner. Each
   produced keep/cut/fix calls + a score. Ideate→critique ran as a pipeline (no barrier).
5. **Synthesize** — 1 agent merged define + all critiqued concepts into the single decision-ready
   brief, **and verified the load-bearing data claims against the actual files first**.

## Data-grounding / verification (why the brief is trustworthy)

The synthesis agent independently confirmed against the extraction outputs before writing:
**36 REITs · 8 sub-sector labels (incl. a "Specialized" n=1) · FFO null in all 36 · no per-year
debt-maturity field anywhere.** Those checks killed the most-promised feature (the maturity ladder)
and corrected the taxonomy — i.e. the data constraints drove the product, not wishful UX.

## Reproducibility

- Orchestrated via the Workflow tool; 14 agents; the script encodes the phases, personas, lenses,
  and JSON output schemas. Run ID `wf_0f238e34-fa8` (this session).
- To re-run or extend (e.g. add a persona, re-do ideation after a positioning change): re-invoke the
  workflow; unchanged stages return cached results, only edited/new stages re-run.
