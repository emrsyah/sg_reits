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
2. LOCATE       locate.py (sub_sector + anchors) + page_map.py (schema -> ALL candidate pages)
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

### Step 2 — Discover THIS report (don't assume)

Your job here is to learn how *this* report is laid out — not to look up a sub-sector
playbook. Per the §0 invariants (`reit-extract/REFERENCE.md`), the only things you may assume
are the schema target + the audited-statement sources; everything else (where each table is,
its shape, units, and whether a field is present) you establish by reading.

```bash
python .claude/skills/reit-extract/scripts/locate.py parsed_reports_datalab/<stem>/full.md
python scripts/adapter/page_map.py <stem>            # ScaleDown summaries (per-page notes)
python scripts/adapter/page_map_classify.py <stem>   # ScaleDown CLASSIFY -> routing (STANDARD)
```
Discovery is two ScaleDown passes (complementary, not duplicates):
- `page_map.py` = abstractive **summary** per page → `page_map.jsonl` (human/agent notes).
- **`page_map_classify.py`** = the **routing standard**: it CLASSIFIES every page against the
  6 tables (sub-sector-agnostic rubrics) and reuses the summaries for readable notes →
  `schema_pages_v2.json` (per table, pages **ranked by score**; `top` = the authoritative page;
  `top_audited_000` = the audited '000 statement vs marketing millions) + `page_map_v2.md`.
  `--rebuild` re-ranks from stored scores (no API). `locate.py` is just a cheap regex pre-pass.

`SCALEDOWN_API_KEY` in `.env`. ScaleDown capabilities: `/summarization/abstractive` (notes),
`/classify` (routing — the standard), `/extract` (pull entities/scalars for profile +
verify-don't-trust cross-checks), `/compress` (shrink narrative context for the LLM lane).

Use it as the **completeness map**: for each schema table, open `schema_pages_v2.json` and
read EVERY candidate page (start at `top`/`top_audited_000`, then down the ranked list) before
deciding what's there — don't stop at the first table (that's how financial.line_items lost its
below-NPI lines).

How to read it (ROUTING, not data — never extract numbers from the map):
- Classify gives a calibrated score per table. The authoritative table = the top-scored page;
  for valuations/financials use `top_audited_000` ('000 audited statement, not a millions card).
- It validated at 100% table-level recall across 7 sub-sectors and **fixes profile** (the
  Trust-Structure page the summariser missed → classify scores it ~1.0). OCR fallback re-reads
  diagram pages if text is sparse.
- What classify CANNOT do is apply judgment that needs the report's content — e.g. is a scoped
  "by-industry" table a real trade_mix (yes, Ascott) or not; is the top-scored "financial"
  page the income statement or a note. **That judgment is yours, made by READING the page —
  not from a sub-sector prior.** Reconcile to the disclosed total to confirm completeness.
- Cross-check at the end: every schema table should map to its candidate page(s); a table with
  candidates but no extracted rows is a missed section; a field you nulled must be absent in
  THIS report (evidence), not "absent per the playbook".
- Pages are `md_page` = physical PDF page (same numbering as `parse_html --page-range`).

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
Record matches/gaps in `status.json`. (When validating a new layout, diff against a pure-LLM
run of the same report to build confidence.)

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
financial, property_transactions, _notes), using `schema/models.py` field names
(`financial_year`, `.SI` symbol, absolute money, `source_page` on every record). NOTE:
financial.json is a SINGLE object (1:1 income_stmt_metrics) with a `line_items[]` audit
trail — NOT a list of note-lines. top_tenant fields are client_name/industry/revenue_pct.

### Step 5 — Gate (never skip)
```bash
python .claude/skills/reit-extract/scripts/validate_schema.py extracted/<SYMBOL>.SI_FY<YYYY>
python .claude/skills/reit-extract/scripts/check_extraction.py extracted/<SYMBOL>.SI_FY<YYYY>
```
Fix every FAIL **at the source, never by plugging numbers** (REFERENCE.md §0 invariant 8). A
gate failure means a value/classification is wrong or a row was merged/missed/double-counted —
go to the report page and fix what it actually says, with a `source_page`. NEVER reclassify,
invent, derive, or adjust a figure just to make a Σ tie out; arithmetic that closes a check is
a signal to investigate, not a fix. If it can't be resolved from the report, leave it flagged
in `_notes` rather than forcing a balance.

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
  page_map.jsonl | schema_pages.json | page_map.md     schema-aware page index (step 2)
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

## Scaling: one agent per AR (author a fresh plan each)

- **One agent per report** (orchestration prompt template in REFERENCE.md §4). Reports are
  independent — run them in parallel.
- **Author a plan PER REPORT — this is the default, not the exception.** Do NOT assume a
  layout from the sponsor or the sub-sector: **same sub-sector ≠ same layout** (different
  sponsors lay out a "retail" or "office" statement completely differently), and **same
  sponsor is only a weak hint** (layouts drift across trusts and across years). What
  generalises across reports is the **engine + the judge/plan step + the gates** — not the
  plans. Plan authoring is cheap (one small LLM pass; the expensive per-row transcription is
  already gone), so just write a fresh plan each time.
- **Reusing a prior plan is an optional shortcut, never a shortcut past verification.** If you
  start from an earlier report's plan, treat it as a guess: re-run `locate.py`, re-inspect the
  table, and re-verify `table_contains` + every column index on THIS report (step 3d) before
  trusting it. A plan that's wrong here must be edited, not forced.
- **The two gates are the safety net** — a plan that doesn't fit (wrong column, missed rows)
  fails reconciliation loudly, so a bad reuse can't pass silently.

## Self-check before finishing
- **Completeness — did I capture ALL disclosed rows/lines, not just the first table?** Row count
  matches the report's stated property/tenant count (note legit gaps, e.g. equity-accounted JVs
  absent from the Portfolio Statement). A long section may span several pages or live partly in a
  segment note / financial review / cards — merge them.
- **financial: the WHOLE Statement of Total Return** — every line below NPI (management fees,
  finance costs, trustee/audit/professional fees, interest/investment income, share of JV,
  fair-value change, divestment gains, tax), not just the revenue/opex notes. Verify
  `Σrevenue − Σexpense + Σadjustment(signed) = Total return for the year`.
- Σ checks reconcile (property valuation/revenue vs totals) within tolerance.
- **Every inferred/derived value is flagged in `_notes.inferred[]`** (occupancy applied from a
  portfolio figure, a category assigned from a name, a value computed as total×pct) — disclosed
  values are never confused with computed ones (REFERENCE §0 #7).
- Both gates green (incl. no "financial.line_items likely INCOMPLETE" warn); `status.json` reflects
  reality; `track.py` shows the AR resolved.
- Money absolute (<1,000,000 trust-level ⇒ unscaled); every record has `source_page`.

## Model
Per-AR agent: **Sonnet** (planning judgement + plan authoring + batched fills are all small
LLM steps; the bulk is deterministic Python). Escalate to a stronger model only for unusually
messy layouts.
