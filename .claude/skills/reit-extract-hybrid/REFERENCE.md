# reit-extract-hybrid REFERENCE

Companion to `SKILL.md`. Plan schema + method catalog (§1), per-section adapterability guide
(§2), status.json schema (§3), orchestration prompt (§4). The schema field set, sub-sector
playbooks, and quirks catalogue live in `reit-extract/REFERENCE.md` — read both.

---

## §1 — Plan file schema & method catalog

A plan (`plan_<section>.json`) is declarative; `scripts/adapter/run_adapter.py` is the
generic engine that consumes it (no exec of generated code). Shape:

```json
{
  "section": "properties",
  "source": {
    "html": "extracted_adapter/<stem>/portfolio.html",
    "table_contains": ["Description of Property", "Tenure of Land"],  // locate by header text
    "table_index": 0,                                                 // fallback only
    "value_col": 6      // a row is a DATA row iff this column parses as a number
  },
  "consts": { "symbol": "C38U.SI", "financial_year": 2025, "currency": "SGD",
              "valuation_date": "2025-12-31" },
  "context_rules": [    // carry section-header values down onto following rows
    {"set": "country",  "col0_regex": "^Investment properties in (.+)$", "capture": 1},
    {"set": "country",  "col0_regex": "^Asset held for sale in (.+)$", "capture": 1,
                        "also": {"status": "held_for_sale", "category": null}},
    {"set": "category", "col0_in": ["Retail", "Office", "Integrated Developments"]}
  ],
  "skip_col0_regex": "^(Investment properties|Net assets|Total|Group|...)",  // drop subtotal/header rows
  "fields": { "<field>": { "method": "...", "decision": "deterministic|needs_llm|other_source", ... } }
}
```

**Method catalog** (per field):

| method | params | does |
|---|---|---|
| `const` | `from` | value from `consts` |
| `text` | `col` | cell text (whitespace-collapsed; `<sup>` footnotes already stripped at parse) |
| `enum` | `col`, `allowed` | cell if in `allowed`, else null (+ a row `_warn`) |
| `parse_years` | `col` | "99 years" → 99.0; "nan"/Freehold → null |
| `concat` | `cols`, `sep` | join cells verbatim (e.g. tenure_raw = tenure / term / remaining) |
| `scale` | `col`, `scale` | numeric × scale ($'000 → ×1000); handles "1,234" and "(1,234)" |
| `context` | `from`, `default` | value carried from a `context_rules` header (country/category/status) |
| `page` | — | printed page from the cell/table `data-block-id` (`/page/N/` → N+1) |
| `needs_llm` | `reason` | leave null, add to llm_todo (judgment/combine) |
| `absent_here` | `where` | leave null, add to llm_todo (field lives elsewhere) |

`decision` drives the summary + tracking: `deterministic` (filled by the engine),
`needs_llm` (batched LLM pass fills it), `other_source` (a different table/page fills it).

**Parser notes that make plans robust across reports:**
- `<sup>`/`<sub>` are stripped at parse, so "Westgate¹"→"Westgate" but "Junction 8"
  (name-number) is preserved. Don't add regex footnote-stripping.
- Locate tables by `table_contains` header text — indices shift between reports.
- `value_col` is the row gate: pick the column that is numeric for real data rows and
  blank/None for header/subtotal rows (carrying value, amount, %, rank…).

---

## §2 — Per-section adapterability guide

Whether a section is `hybrid` (adapter) or `llm_only` (scattered), from the 4-archetype
sweep. Always re-confirm on the actual report; this is the prior, not the answer.

| Section | Default method | Where / why |
|---|---|---|
| **properties** (valuation/tenure/address) | **hybrid** | audited Portfolio Statement is one clean grid (Tier C). `value_col` = carrying-value $'000. Deterministic: name, tenure, term, tenure_raw, address, valuation, country/category/status (header-carried), source_page. `needs_llm`: ownership (footnotes), value_basis (JV). `other_source`: occupancy/gla/nla/npi/gross_revenue/major_tenant (per-property cards → a 2nd adapter or LLM). |
| **properties** (operating metrics) | hybrid (2nd adapter) | per-property cards / "At A Glance" — semi-structured; a 2nd plan over the card pages, or LLM if cards are too irregular (hospitality). |
| **top_tenants** | **hybrid** | single ranked table. `value_col` = the % column. `needs_llm`: map `trade_sector` to taxonomy; DC names are anonymised (use verbatim descriptor). Anchor wording varies: "Top 10 Tenants/Customers/Clients" / "by GRI". |
| **trade_mix** | **hybrid** | single table; `value_col` = pct. Watch roll-up + expanded sub-tables (CICT "Other Retail/Office Trades"). `needs_llm`: map `category_raw`→canonical. Hospitality: none (declare structural). DC: client trade-sector, `pct_basis=rental_income`. |
| **financial** (revenue + opex notes) | **hybrid** | the Gross Revenue note and Property Operating/Direct Expenses note are clean 2-col grids ($'000). `value_col` = amount. `needs_llm`: map `label_raw`→canonical `component` key + `statement` (revenue/expense). |
| **performance** | **llm_only** (usually) | headline figures are spread across 5-yr summary + distribution statement + statistics-of-unitholders (3 pages). A few cells, scattered — cheaper to LLM-extract than to author 3 micro-adapters. |
| **profile** | **llm_only** | `management` entities are scattered across front matter + corporate-information; `sub_sector` is judgement (use locate.py guess). Not a grid. |

Rule of thumb: **one clean grid → hybrid; few scattered cells → llm_only.** When `llm_only`,
use the `reit-extract` workflow for that section and mark it `llm_only` in status.json.

### Table-shape taxonomy (decide this in the judge step)

The engine handles some table shapes deterministically and not others. Inspect the section's
HTML tables (`pandas.read_html` / count `<table>` blocks) before committing to `hybrid`:

| Shape | Engine support | What to do |
|---|---|---|
| **Single self-contained table** (label + values in one grid; C38U portfolio statement, top-10, trade-mix, FS notes) | ✅ full | `hybrid` — author a plan, `value_col` = the numeric anchor column |
| **Multi-page, same columns** (one `<table>` per page, each with its own label + value column) | ✅ `run_adapter` concatenates all tables matching `table_contains` | `hybrid` — header text matches every page-table; concat is automatic |
| **Facing-page positional split** (description columns on left page, value/revenue columns on a SEPARATE table with NO label column, aligned by row position — Mapletree big-portfolio statements, e.g. MLT) | ❌ not yet — needs a two-table positional-join mode | `llm_only` for that section for now (the LLM reads the paired pages fine). Detect it: the value table's col0 is blank for every row. |
| **Stacked-cell, one-table-per-property** (name/location/tenure/term all crammed into ONE cell with `<br>` separators; a separate `<table>` per property — First REIT / healthcare-style) | ❌ column extraction can't split the stacked cell | `llm_only` for that section. Detect it: col0 header is a multi-field string ("Description of property / Location / ... / Term of lease") and there is one short table per property. |
| **Per-property cards** (occupancy/area/NPI/major_tenant; irregular) | ❌ deterministic; ✅ LLM lane | LLM lane — small targeted pass over the card pages, merged like the needs_llm pass |

**Detection rule for the judge step:** if the section's value columns sit in a table whose
first column is blank for every data row (no label), it's a positional split → route that
section to `llm_only` (or the positional-join mode once built). One clean labelled grid (even
if spread over many same-shaped pages) → `hybrid`.

---

## §3 — status.json schema (per AR)

```json
{
  "stem": "09_C38U.SI_..._FY2025", "symbol": "C38U.SI", "financial_year": 2025,
  "sub_sector": "Diversified", "template_family": "CapitaLand",
  "parsed": {"markdown": "<path>", "html_pages": "108-112", "checkpoint_id": "..."},
  "sections": {
    "<section>": {
      "status": "planned|run|merged|gated|done|llm_only|skipped",
      "method": "hybrid|llm_only",
      "adapterable": true,
      "plan": "plan_<section>.json",
      "deterministic_fields": [...], "needs_llm_fields": [...], "other_source_fields": [...],
      "rows": 25,
      "cross_check": {"vs": "...", "match": "...", "gaps": [...]},
      "files": {"deterministic": "...", "llm_filled": "...", "merged": "..."},
      "note": "..."
    }
  },
  "final_dir": "extracted/<SYMBOL>.SI_FY<YYYY>",
  "gates": {"schema": "PASS|FAIL", "check": "PASS|FAIL"},
  "updated": "YYYY-MM-DD"
}
```
Status lifecycle per section: `planned → run → merged → gated → done` (or `llm_only` /
`skipped`). `track.py` renders these as OK/G/M/r/p/L/-/. across all ARs.

---

## §4 — Orchestration: one agent per AR

Dispatch one agent per report with this prompt (fill the placeholders):

```
Extract <TRUST> (<SYMBOL>.SI) FY<YYYY> using the reit-extract-hybrid skill.
Stem: <stem>.  Parsed markdown: parsed_reports_datalab/<stem>/full.md

Read and follow:
- .claude/skills/reit-extract-hybrid/SKILL.md (+ REFERENCE.md)
- .claude/skills/reit-extract/REFERENCE.md  (schema field set, sub-sector playbooks, quirks)
- schema/models.py  (authoritative field names)
If a plan exists for this trust's template family in
.claude/skills/reit-extract-hybrid/plans/<family>/, START from it and re-verify columns.

Do the per-AR pipeline: parse (md + HTML for table pages) -> locate -> per section
{judge feasibility -> plan -> run_adapter -> cross-check -> batched LLM pass -> merge},
llm_only fallback for scattered sections -> assemble the 8 files in
extracted/<SYMBOL>.SI_FY<YYYY>/ -> run BOTH gates -> keep extracted_adapter/<stem>/status.json
current.

Return: per-section method + status, rows per section, both gate verdicts, reconciliation
lines, and any layout quirk that broke a reused plan (so the family template can be updated).
```

When a new template family is proven, copy its plans into
`.claude/skills/reit-extract-hybrid/plans/<family>/` so later reports in the family reuse them.

---

## §5 — Scripts (all in `scripts/adapter/`)

| Script | Role |
|---|---|
| `parse_html.py` | Datalab convert → HTML (or json) for the table pages (preserves `<sup>`, page block-ids) |
| `run_adapter.py` | deterministic engine: plan + HTML → records + llm_todo (the on-the-fly extractor) |
| `merge_llm.py` | merge the batched LLM pass back; anomaly check |
| `track.py` | progress matrix across all ARs from their status.json |

Gates (reused from `reit-extract/scripts/`): `validate_schema.py`, `check_extraction.py`.
