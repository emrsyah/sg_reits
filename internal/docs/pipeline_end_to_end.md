# SGX REIT pipeline — end-to-end reference (assumption-free, discovery-first)

The canonical flow for turning a Datalab-parsed annual report into the `sgx_reit_*` 6-table
schema. This is the **current** strategy (Jun 2026): **assumption-free + ScaleDown discovery
(summary + classify) + deterministic-where-clean / LLM-where-not + provenance-flagged + gated**.

Deep detail lives in the skills — this doc is the map, not a duplicate:
- `.claude/skills/reit-extract/REFERENCE.md` **§0 Invariants** (the philosophy) + §1–§4 (field
  sources, enums, illustrative quirks)
- `.claude/skills/reit-extract-hybrid/SKILL.md` + `REFERENCE.md` (the per-report pipeline)
- `schema/sgx_reit_schema.md` + `schema/models.py` (the target)

---

## 0. The core principle — ASSUME NOTHING, DISCOVER EVERYTHING

Reports do **not** generalise by sub-sector or sponsor. Per-family "playbooks" overfit to a
handful of reports and *suppress* extraction ("sub-sector X doesn't have Y → skip it"). So the
only things an agent may assume are the **invariants**; everything else is **discovered from the
report being extracted**.

**Invariants (assumable — accounting/SGX structure, true for every trust):**
1. The task = the schema (`schema/models.py`).
2. `market_valuation` only from the **audited Portfolio Statement in `'000`** — never the
   marketing summary (millions), never the aggregate investment-property line.
3. Income = the **full Statement of Total Return** (every line down to "total return for the
   year"), not just the revenue/opex notes.
4. Money absolute (×1000 from `'000`); `source_page` on every record; currency per figure;
   **reconcile Σ to the disclosed total** (property valuations→portfolio total; trade_mix→100%;
   income→total return).

**Two hard rules:**
- **Structural absence must be proven from THIS report** (evidence), never declared from a prior.
  "Disclosed on a narrow basis" ≠ absent (capture it, scope it).
- **Disclosed vs inferred:** you may infer/derive for completeness, but flag it in
  `_notes.inferred[]` — never make a computed value look disclosed; else leave null.

Everything labelled per-sub-sector in the skills is an **illustrative prior** (a hint to speed
discovery), never a rule. The report overrides it every time.

---

## 1. Parse — Datalab (balanced)  [PAID, per page — validate ranges first]

```
python scripts/parse_datalab.py "<full-stem>"          # markdown + checkpoint
python scripts/adapter/parse_html.py <stem> --page-range A-B   # HTML for table pages (hybrid)
```
- markdown → `parsed_reports_datalab/<stem>/full.md` (page-anchored `<!-- PAGE N -->`).
- HTML (only the table pages you'll adapt) → `extracted_adapter/<stem>/<group>.html`; preserves
  `<sup>` footnotes + `/page/N/` block-ids that markdown flattens.
- `<stem>` = PDF stem, e.g. `09_C38U.SI_CapitaLand-Integrated-Commercial-Trust_FY2025`.

## 2. Discover — map the report to the schema (NO assumptions)  [ScaleDown, PAID]

Three passes, cheapest→richest. Goal: learn *where each table is, its shape, units, and whether
each field is present* — by reading, not by looking up a family.

```
python .claude/skills/reit-extract/scripts/locate.py parsed_reports_datalab/<stem>/full.md
python scripts/adapter/page_map.py <stem>            # ScaleDown summaries (per-page notes)
python scripts/adapter/page_map_classify.py <stem>   # ScaleDown CLASSIFY -> routing (STANDARD)
```
- `locate.py` — cheap regex pre-pass (sub_sector hint + anchors).
- `page_map.py` — `/summarization/abstractive` per page → `page_map.jsonl` (human/agent notes).
- **`page_map_classify.py` — the routing standard.** `/classify` per page against the 6 tables
  using **sub-sector-agnostic rubrics** → `schema_pages_v2.json`: per table, candidate pages
  **ranked by score**, with `top` (authoritative) and `top_audited_000` (the '000 audited
  statement vs a millions marketing card). Reuses page_map summaries for notes; OCR fallback
  (re-classify the PDF page image) for sparse/diagram pages; `/extract` for profile entities;
  `--rebuild` re-ranks from stored scores with no API.

**What discovery gives vs what the agent must still do:**
- The map = **recall + routing** (which pages hold each table; validated 100% table-level recall
  across 7 sub-sectors; it fixes the profile/Trust-Structure page the summariser missed).
- The agent = **precision by reading**: pick the authoritative page (unit/`top_audited_000`),
  apply schema judgment the classifier can't (is a scoped industry table a real `trade_mix`?
  is this the income *statement* or a *note*?), and reconcile. **Never extract numbers from a
  summary/map — only from the actual page.**

ScaleDown (`SCALEDOWN_API_KEY` in `.env`) = `/summarization/abstractive`, `/classify`,
`/extract`, `/compress` at `api.scaledown.xyz` (header `x-api-key`).

## 3. Route + extract — per section, decided from discovery

For each of the 6 tables, read EVERY candidate page in `schema_pages_v2.json` (start at
`top`/`top_audited_000`, then down the ranked list) — don't stop at the first table.

**Judge each field** (LLM): `deterministic` (one cell / header-carried / trivial transform) /
`needs_llm` (judgement, combining, classify-to-taxonomy) / `other_source` (lives elsewhere).
**Judge the section shape:** clean repeating grid → `hybrid` (deterministic adapter); scattered
/ card / facing-page-split / stacked-cell → `llm_only`.

```
# hybrid: author plan, run the generic engine (NOT exec'd codegen), then batched LLM merge
python scripts/adapter/run_adapter.py extracted_adapter/<stem>/plan_<section>.json
python scripts/adapter/merge_llm.py <section>_deterministic.json llm_filled_<section>.json \
       plan_<section>.json --decision needs_llm --out <section>_merged.json
```

**Completeness (the recurring failure mode):** capture ALL disclosed rows/lines, not the first
table you find. Especially **financial = the WHOLE Statement of Total Return** (below-NPI:
management fees base/perf, finance costs, trustee/audit/professional fees, interest/investment
income, share of JV, fair-value change, divestment gains, tax — `statement="adjustment"` with
**signed** amounts). Verify `Σrevenue − Σexpense + Σadjustment(signed) = total return`.

## 4. Provenance — disclosed vs inferred

Prefer disclosed values. Any inferred/derived value (a portfolio figure applied per-property; a
category assigned from a name; `total × pct`) goes in **`_notes.inferred[]`**
`{table, field, scope/rows, value, basis, source_page}` — or leave the field null. The gate warns
on undeclared inferences (e.g. a per-property field uniform across many rows); the cockpit renders
inferred fields amber so disclosed ≠ computed.

## 5. Assemble + gate (never skip)

Write the 8 intermediate files to `extracted/<SYMBOL>.SI_FY<YYYY>/` (`schema/models.py` field
names: `financial_year`, `.SI` symbol, absolute money, `source_page` everywhere). Then:
```
python .claude/skills/reit-extract/scripts/validate_schema.py extracted/<SYMBOL>.SI_FY<YYYY>
python .claude/skills/reit-extract/scripts/check_extraction.py extracted/<SYMBOL>.SI_FY<YYYY>
```
`check_extraction.py` now also: financial-INCOMPLETE warn (missing finance_costs/management_fee/
adjustment lines); trade_mix sums ~100%; top_tenants present; **inferred-provenance** (undeclared
uniform-fill warn + `_notes.inferred[]` validation). Fix every FAIL.

## 6. Track + proofread

```
python scripts/adapter/track.py                 # matrix across all ARs from status.json
python scripts/review/app.py                     # cockpit -> http://127.0.0.1:5057 (Chrome/Edge)
```
Cockpit: PDF ‖ records side-by-side; page button jumps to `source_page` (+ per-report page-offset
for printed-vs-physical drift); mark correct/false/unsure + notes → `reviews/<dir>.json`;
inferred fields show amber.

## 7. Folder & file map

```
annual_reports/<stem>.pdf                              source PDFs (FY2025 corpus)
parsed_reports_datalab/<stem>/full.md                  parsed markdown (locating + reading)
extracted_adapter/<stem>/                              per-AR working dir
  page_map.jsonl                                       ScaleDown summaries (notes)
  schema_pages_v2.json | page_map_v2.md                CLASSIFY routing (the standard)
  <group>.html                                         HTML table pages (hybrid)
  plan_<section>.json | <section>_*.json               on-the-fly plan + engine outputs
  status.json                                          per-AR tracker
extracted/<SYMBOL>.SI_FY<YYYY>/                        CANONICAL 8-file output (gated)
extracted_llm_baseline/                                pure-LLM baselines (validation)
extracted_mapdriven/                                   discovery-first A/B outputs (pre-promotion)
reviews/<dir>.json                                     proofreading verdicts + notes
scripts/adapter/  page_map.py · page_map_classify.py · parse_html.py · run_adapter.py ·
                  merge_llm.py · track.py
scripts/review/   app.py · index.html                  proofreading cockpit
```

## 8. Status (Jun 2026)

- **10-report FY2025 set** extracted + gated (`docs/proofread_10set.md`). income_components fixed
  across all 10 (full Statement of Total Return, reconciles exactly).
- **Discovery-first validated + promoted:** AJBU, AW9U (recovered `major_tenant` 0→31 + income),
  BTOU, plus C38U/AU8U/M44U (round-1 map-driven). **Not yet discovery-first:** DHLU, UD1U, J69U,
  + a full HMN pass.
- **Assumption cost is real but uneven** — large on master-lease/operator REITs (per-property
  tenant/occupancy wrongly nulled), ~nil on grid-heavy reports already complete.
- Deprecated: the old `reit-extraction` skill (carried the overfit assumptions).

## 9. Run a new report (recipe)

```
1. parse_datalab.py <stem>                              # markdown
2. locate.py + page_map.py + page_map_classify.py       # DISCOVER (no assumptions)
3. per section: read all candidate pages -> judge -> deterministic adapter OR llm_only
   - financial = the WHOLE Statement of Total Return; reconcile to total return
   - flag any inferred value in _notes.inferred[]
4. parse_html.py only for the grid pages you adapt
5. assemble 8 files in extracted/<SYMBOL>.SI_FY<YYYY>/
6. validate_schema.py + check_extraction.py  (fix every FAIL)
7. track.py ; proofread in the cockpit
```
**Golden rule:** the map routes, the report decides, the gates verify — never assume from family,
never let an inference look disclosed.
