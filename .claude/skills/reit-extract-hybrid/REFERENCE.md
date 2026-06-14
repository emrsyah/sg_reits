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

**When to use the HTML adapter vs read markdown directly (Phase-D lesson):** reserve the
HTML+`run_adapter` path for the **large property statement** (multi-page, multi-column —
where deterministic row extraction earns its keep). For **small, clean 2-column tables**
(Gross-Revenue / expenses notes, top-10 tenants, trade mix) the markdown is just as reliable
and avoids two HTML pitfalls seen in Phase D: (a) `parse_html --page-range` is a **PDF page
index that can drift** from the markdown `<!-- PAGE N -->` numbers (front-matter offset), so
the wrong note can be parsed; (b) **headerless tables** (e.g. anonymised DC client tables)
have no text for `table_contains` to match. Extracting those few rows straight from the
markdown is faster and avoids both. Still validate totals against the audited figure.

**Held-for-sale / divested rows (recurring — add to every property plan):** add a
`context_rule` so a "held for sale" block sets status, e.g.
`{"set":"status","col0_regex":"held for sale","also":{"status":"held_for_sale"}}`, or a
post-step that renames an "Asset held for sale - X" row to "X" + `status=held_for_sale`
(seen on AJBU Basis Bay and BTOU Figueroa). Divested-in-year properties are absent from the
Tier-C statement — add them from the divestment note / context, `status=divested`, and record
the partial-year P&L gap in `_notes.reconciliation`.

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
| **financial** (FULL Statement of Total Return) | **hybrid** | **capture the WHOLE audited Statement of Total Return, not just the revenue/opex notes** (the #1 under-capture bug). It has three layers: (1) Gross Revenue note + Property Operating/Direct Expenses note (clean 2-col $'000 grids) → the `revenue` + property-`expense` detail; (2) every line BELOW NPI on the face of the statement → interest/investment income (`revenue`), management fees base+performance, trustee/audit/professional/valuation fees, finance costs, other trust expenses (`expense`); (3) non-operating lines → share of JV/associate results, net change in fair value of investment properties/derivatives, gain/loss on divestment, taxation → `statement="adjustment"` with the amount **SIGNED** (gains +, charges/tax −). `value_col` = amount. `needs_llm`: map `label_raw`→canonical `component` key + `statement`. **Don't** re-add aggregate "Gross revenue"/"Property operating expenses" rows when their note detail is already captured (double-count). **Completeness self-check: `Σrevenue − Σexpense + Σadjustment(signed)` must equal "Total return for the year".** The gate warns if finance_costs / management_fee / adjustment lines are absent. |
| **performance** | **llm_only** (usually) | headline figures are spread across 5-yr summary + distribution statement + statistics-of-unitholders (3 pages). A few cells, scattered — cheaper to LLM-extract than to author 3 micro-adapters. |
| **profile** | **llm_only** | `management` entities are scattered across front matter + corporate-information; `sub_sector` is judgement (use locate.py guess). Not a grid. |

Rule of thumb: **one clean grid → hybrid; few scattered cells → llm_only.** When `llm_only`,
use the `reit-extract` workflow for that section and mark it `llm_only` in status.json.

**Completeness over convenience (target-driven).** For every section, the question is *"have I
captured ALL the disclosed rows/lines this schema table wants?"* — not *"what did the first
table I found contain?"*. The common failure is stopping at the headline/first table and
under-capturing. Two habits prevent it:
- **Reconcile row/line count to a disclosed total**: properties vs the stated property count;
  trade_mix to 100%; **financial: Σrev − Σexp + Σadj(signed) = Total return for the year**. If
  it doesn't reconcile, rows/lines are missing — the data is split across pages or a section you
  haven't read yet. Go find the continuation (light-medium check, not a deep dive).
- **A long section may span several tables/pages or live partly elsewhere** (segment notes,
  financial review, per-property cards). Pull and merge them; don't take the first grid as the
  whole truth.

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

### Cross-trust quirks observed (canary log — extend as new reports surface more)

These are **data-semantics** quirks (not engine-shape quirks). They don't stop the adapter
running; they change reconciliation and what stays null. Watch for them in the cross-check.

- **JV property absent from the Portfolio Statement** (FCT: NEX, Waterway Point — 50% each).
  Some trusts hold JV/associate properties via a single "Investment in joint ventures" line in
  the audited statement, so the individual property is NOT a row in the Portfolio Statement.
  Its appraised value appears only on the per-property card on a **100% basis**. Record it with
  `value_basis="joint_venture_100pct"` and `source_page` = the card. Σ-reconciliation of the
  Portfolio Statement rows will (correctly) exclude these — do NOT treat the shortfall as a
  miss. (Contrast: CICT keeps JV assets like Gallileo IN the Portfolio Statement at 100% with a
  stake footnote.) Confirm by checking whether the Portfolio-Statement total + JV book value
  ≈ marketing total.
- **Segment-aggregated multi-property rows** (FCT: Northpoint City NW+SW + Yishun 10 reported as
  one segment). When a trust buys a second wing/building mid-year and/or divests in the same
  segment, the audited segment note may collapse several properties into ONE row, making
  per-property GR/NPI unsplittable. Assign the combined figure to the anchor property, null the
  others' GR/NPI, and record the constraint in `_notes`.
- **Non-December fiscal year-end** (FCT: 30 Sep). `financial_year=YYYY` means the year ENDING
  on the trust's FY-end, not 31 Dec. Distribution payment dates can fall after FY-end (normal).
  locate.py's sub_sector guess is unaffected, but get the FY-end right when stamping records and
  reading "2H" distribution lines.
- **SFP line ≠ Statement-of-Portfolio valuation** (DHLU). The balance-sheet "Investment
  properties" line can be INFLATED vs the Portfolio Statement by IFRS-16 ROU assets (ground
  leases) and Asset Retirement Obligations (DHLU: SFP S$984,117k vs valuation S$835,157k, a
  S$148,960k gap). `market_valuation` = the **"Investment properties, at valuation"** figure in
  the Portfolio Statement reconciliation box, NOT the SFP line. The Portfolio Statement usually
  prints the reconciliation explicitly at the bottom.
- **Concentration disclosed by NPI, not GRI** (DHLU). Most trusts give top-tenant / trade-mix %
  by gross rental income; some give it by NPI. Set `pct_basis="npi"` (not `gri`) and don't
  assume the basis — read the table caption/footnote.
- **Dual-currency Portfolio Statement prints both currencies** (CLCT: RMB'000 + S$'000 side by
  side). They are the SAME fact in two currencies — do NOT add them. Canonical figure = the
  SGD consolidated column (matches the audited FS); preserve the local-currency column in an
  audit field (e.g. `_rmb_valuation_000`). Two FX rates exist: closing (valuation) vs average
  (income) — keep them straight.
- **Multi-tier trade-mix (don't double-count)** (CLCT: segment → sub-category). Some trusts give
  a top-level segment breakdown AND a sub-category breakdown that rolls up into it. Capture ONE
  level (usually the leaf sub-categories) so the percentages sum to 100% once; disambiguate
  repeated leaf names (e.g. two "E-commerce" rows) via `category_raw`.
- **Stapled group: dual REIT-vs-BT Portfolio Statement blocks** (HMN/CapitaLand Ascott). The
  business-trust assets (some investment properties + PPE hotels) sit in SEPARATE blocks with
  only a Stapled-Group column (the REIT-Group column is blank/dashes). Reconcile each block to
  its own stated total; PPE hotels may be disclosed only as a block total (per-property null).
  A "Not applicable" valuation cell (HMN: 8 AU + some FR rows) is a legit null, not an error.
- **Under-construction / redevelopment property** (M44U: 5A Joo Koon; MLT Subang parcels). A
  property mid-redevelopment shows zero revenue + zero/low occupancy and possibly a large
  valuation jump on completion — record the figures as-disclosed; this is not a data error.

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
Author this report's plans fresh from its own tables — do NOT assume a layout from the
sponsor or sub-sector. The example plans in .claude/skills/reit-extract-hybrid/plans/examples/
are illustrations of the plan format only; if you borrow one, re-verify table_contains and
every column index on THIS report before trusting it.

Do the per-AR pipeline: parse (md + HTML for table pages) -> locate + page_map.py
(read schema_pages.json so you pull EVERY candidate page per section, not just the first
table) -> per section {judge feasibility -> plan -> run_adapter -> cross-check -> batched
LLM pass -> merge}, llm_only fallback for scattered sections -> assemble the 8 files in
extracted/<SYMBOL>.SI_FY<YYYY>/ -> run BOTH gates -> keep extracted_adapter/<stem>/status.json
current. For `financial`, capture the WHOLE Statement of Total Return (all below-NPI lines),
not just the revenue/opex notes.

Return: per-section method + status, rows per section, both gate verdicts, reconciliation
lines, and any new layout shape worth recording in the table-shape taxonomy (§2).
```

The `plans/examples/` folder holds a few reference plans to show the format — NOT a per-sponsor
library to reuse by default. Layout sameness is not guaranteed by sponsor or type, so the
reliable path is per-report authoring + the gates, not plan reuse.

---

## §5 — Scripts (all in `scripts/adapter/`)

| Script | Role |
|---|---|
| `page_map.py` | schema-aware page index (ScaleDown summary per page → `schema_pages.json` table→pages + `page_map.md`); `--retag` rebuilds tags from existing summaries with no API. Completeness safety net for step 2 |
| `parse_html.py` | Datalab convert → HTML (or json) for the table pages (preserves `<sup>`, page block-ids) |
| `run_adapter.py` | deterministic engine: plan + HTML → records + llm_todo (the on-the-fly extractor) |
| `merge_llm.py` | merge the batched LLM pass back; anomaly check |
| `track.py` | progress matrix across all ARs from their status.json |

Gates (reused from `reit-extract/scripts/`): `validate_schema.py`, `check_extraction.py`.
