---
name: reit-extract-hybrid
description: Batch-scale SGX REIT extraction — one agent per annual report, each authoring its own on-the-fly deterministic extraction plans (HTML tables) and using the LLM only for feasibility judgement + scattered/judgment fields. Use when extracting MANY reports, when speed/cost at scale matters, or when the user asks for the deterministic/adapter/plan-driven pipeline. For a single report where you just want correctness, reit-extract (pure LLM) is fine.
---

# SGX REIT extraction — hybrid (deterministic-first) at batch scale

Extract ~40 annual reports fast and cheap by doing the mechanical 70% deterministically and
spending the LLM only where it earns its keep. Each AR is handled by **its own agent**,
which **writes that report's extraction plans on the fly**, runs a generic engine, and
tracks its own progress.

Target schema: `schema/sgx_reit_schema.md` + `schema/models.py`. Final output: the 8-file
intermediate in `extracted/<SYMBOL>.SI_FY<YYYY>/` (same as `reit-extract`), so the same two
gates validate it.

## Why hybrid

Per-row LLM transcription is the bottleneck — generating 180 property rows as output tokens
takes ~minutes. But that data sits in clean tables. So:

- **Deterministic** (no LLM per row): pull rows from an HTML table you've mapped once.
- **LLM** (once, small): judge whether a section *can* be done deterministically, author the
  column→field plan, and fill the genuinely-hard fields (judgment, scattered, cross-page).

Measured on C38U properties: deterministic Tier-C = **25 rows in 0.28 s, 25/25 identical** to
the pure-LLM agent; the LLM touched only 2 judgment fields in one 14 s batched call. ~20×
faster, ~6× cheaper, reproducible.

## The per-AR pipeline (what each agent does)

```
1. PARSE        markdown (for locating) + HTML (for deterministic tables)
2. LOCATE       locate.py -> sub_sector + anchor pages
3. per SECTION: JUDGE feasibility -> PLAN -> RUN -> CROSS-CHECK -> (LLM pass -> MERGE)
                or fall back to LLM-only for non-adapterable sections
4. ASSEMBLE     write the 8 files to extracted/<SYMBOL>.SI_FY<YYYY>/
5. GATE         validate_schema.py + check_extraction.py
6. TRACK        keep extracted_adapter/<stem>/status.json current throughout
```

### Step 1 — Parse
```bash
python scripts/parse_datalab.py <stem>                       # markdown (balanced, checkpoint)
python scripts/adapter/parse_html.py <stem> --page-range A-B # HTML for the table pages
```
Use `locate.py` (step 2) FIRST to find the table pages, then HTML-parse just those ranges
(Datalab is per-page paid). One HTML file per page-range is fine; name it for the section
group (e.g. `portfolio.html`, `tenants.html`, `financial.html`).

### Step 2 — Locate
```bash
python .claude/skills/reit-extract/scripts/locate.py parsed_reports_datalab/<stem>/full.md
```
Note the `sub_sector` guess (picks the playbook) and the anchor pages for each section.

### Step 3 — Per section: judge → plan → run → cross-check → LLM → merge

**3a. Feasibility judgement (LLM, the gate you asked for).** Sample ~5 rows of the section's
HTML table and read that table's schema fields (`schema/models.py`). Decide, per field, a
**decision**:
- `deterministic` — the value is one cell, or carried from a section header (country/
  category/status), or a trivial transform (×1000, "99 years"→99, enum). The raw value is
  sufficient.
- `needs_llm` — the value needs judgement or combining (dual-basis valuation, ownership from
  footnotes, classification to the canonical taxonomy).
- `other_source` — the field isn't in THIS table; it lives elsewhere (another page / a card
  table) → either a second adapter or the LLM lane.

Then decide the **section method**:
- `hybrid` — there IS a clean single grid for the bulk of fields → write a plan.
- `llm_only` — the data is scattered/narrative/card-shaped with no clean grid (typically
  `profile`, `performance`; sometimes hospitality property tables) → skip the adapter, use
  the `reit-extract` LLM workflow for this section.

REFERENCE.md §2 gives the per-section adapterability guide so you don't re-derive it.

**3b. Author the plan** `extracted_adapter/<stem>/plan_<section>.json` (schema + method
catalog in REFERENCE.md §1). Locate the table by **header text** (`table_contains`), not a
fixed index — positions shift between reports.

**3c. Run the deterministic engine:**
```bash
python scripts/adapter/run_adapter.py extracted_adapter/<stem>/plan_<section>.json
```
It writes `<section>_deterministic.json` + `<section>_deterministic.llm_todo.json`, and
prints rows + per-field fill + the decision tally.

**3d. Cross-check.** Verify the row count against the report's stated count; reconcile sums
(e.g. Σ property valuation vs total) where possible; eyeball 3–5 rows vs the source page.
Record matches/gaps in `status.json`. (For the first report of a template family, diff
against a pure-LLM run of the same report to build confidence.)

**3e. Batched LLM pass + merge (`needs_llm`).** Collect the `needs_llm` fields across ALL rows
and resolve them in ONE call (give the model the row list + the relevant footnotes/source).
Save as `llm_filled_<section>.json`, then:
```bash
python scripts/adapter/merge_llm.py <section>_deterministic.json llm_filled_<section>.json \
    plan_<section>.json --decision needs_llm --out <section>_merged.json
```
`merge_llm.py` fills only the chosen decision's fields (never overwrites deterministic values),
matches by **normalised name** (handles audited-full-name vs card-abbreviation), and runs an
anomaly check.

**3f. `other_source` LLM lane (properties).** The property fields that live in per-property
cards (occupancy_rate, gla, nla, net_property_income, gross_revenue, major_tenant) are too
irregular to parse deterministically across 40 trusts → one batched LLM pass reads the card
pages and returns `{property_name: {field: value}}`. Save as `llm_other_source.json`, then:
```bash
python scripts/adapter/merge_llm.py properties_merged.json llm_other_source.json \
    plan_properties.json --decision other_source --out properties_full.json
```
Fields the trust genuinely doesn't disclose per property (e.g. CICT per-property NPI) stay
null — declare them in `_notes.columns_never_fillable`. (Validated on C38U: occupancy 24/24,
NLA 25/25 vs the pure-LLM agent.)

### Step 4 — Assemble
Combine the merged per-section records into the 8 intermediate files in
`extracted/<SYMBOL>.SI_FY<YYYY>/` (profile, performance, properties, top_tenants, trade_mix,
income_components, property_transactions, _notes), using `schema/models.py` field names
(`financial_year`, `.SI` symbol, absolute money, `source_page` on every record).

### Step 5 — Gate (never skip)
```bash
python .claude/skills/reit-extract/scripts/validate_schema.py extracted/<SYMBOL>.SI_FY<YYYY>
python .claude/skills/reit-extract/scripts/check_extraction.py extracted/<SYMBOL>.SI_FY<YYYY>
```
Fix every FAIL.

### Step 6 — Track (keep current throughout)
Maintain `extracted_adapter/<stem>/status.json` (schema in REFERENCE.md §3) — per-section
status, decisions, cross-check, gate verdicts. Then:
```bash
python scripts/adapter/track.py            # matrix across all ARs
```

## Folder & file naming (fixed conventions)

```
parsed_reports_datalab/<stem>/full.md                  markdown (locating)
extracted_adapter/<stem>/                              per-AR working dir
  portfolio.html | tenants.html | financial.html       HTML table pages (per section group)
  plan_<section>.json                                  the on-the-fly plan (LLM-authored)
  <section>_deterministic.json                         deterministic output
  <section>_deterministic.llm_todo.json                fields deferred to the LLM
  llm_filled_<section>.json                            batched LLM output
  <section>_merged.json                                deterministic + LLM merged
  status.json                                          per-AR tracker
extracted/<SYMBOL>.SI_FY<YYYY>/                        FINAL 8-file output (gated)
```
`<stem>` = the PDF stem, e.g. `09_C38U.SI_CapitaLand-Integrated-Commercial-Trust_FY2025`.
`<section>` ∈ {profile, performance, properties, top_tenants, trade_mix, financial}.

## Scaling: one agent per AR + plan reuse

- **One agent per report** (orchestration prompt template in REFERENCE.md §4). Reports are
  independent — run them in parallel.
- **Plans are per-layout and REUSABLE.** Reports from the same sponsor share templates
  (CapitaLand, Mapletree, Keppel, Frasers…). Seed a new report from the family's prior plan
  in `.claude/skills/reit-extract-hybrid/plans/<family>/` and adjust `table_contains`/columns
  if the layout drifted. The first report of a family costs a full planning pass; the rest
  are near-instant. Always re-verify column indices on the new report (3d) before trusting a
  reused plan.
- **The two gates are the safety net** — a reused plan that drifted (wrong column, missed
  rows) fails reconciliation loudly.

## Self-check before finishing
- Row count matches the report's stated property/tenant count (note legit gaps, e.g. equity-
  accounted JVs absent from the Portfolio Statement).
- Σ checks reconcile (property valuation/revenue vs totals) within tolerance.
- Both gates green; `status.json` reflects reality; `track.py` shows the AR resolved.
- Money absolute (<1,000,000 trust-level ⇒ unscaled); every record has `source_page`.

## Model
Per-AR agent: **Sonnet** (planning judgement + plan authoring + batched fills are all small
LLM steps; the bulk is deterministic Python). Escalate to a stronger model only for unusually
messy layouts.
