# SGX REIT pipeline — end-to-end reference

*How we go from an annual-report PDF to gated `sgx_reit_*` JSON. Personal reference for the
parsing + extraction flow as it stands (Jun 2026). Canonical schema: `schema/sgx_reit_schema.md`
+ `schema/models.py`.*

---

## 0. The shape of the problem

~40 SGX REITs × up to 3 fiscal years ≈ ~120 heterogeneous PDFs (200–400 pages each, different
layouts, currencies, sub-sectors). Goal: high-accuracy structured data in 6 tables. Two hard
truths drive every design choice:

1. **Three-tier valuation** — every report prints each property's value up to 3× on different
   bases (marketing summary in millions / per-property card at 100% / **audited Portfolio
   Statement in $'000**). Only the audited tier is `market_valuation`.
2. **Sub-sector changes which tables exist** — `trade_mix`/`top_tenant` are retail/office facts;
   data-centre uses client-type, hospitality uses contract-type. Don't force-fit.

And one performance truth: **per-row LLM transcription is the bottleneck** — making an LLM
regenerate 180 property rows as output tokens takes minutes. The pipeline is built to avoid that.

---

## 1. Parsing — Datalab (balanced)

We parse with **Datalab Marker/Surya, balanced mode**. Cheaper than agentic LlamaParse
(~0.4¢/page vs ~1.2¢) and cleaner tables. Full FY2025 corpus ≈ $26.

```bash
# markdown — for the agent to READ / locate sections
python scripts/parse_datalab.py <stem>
#   -> parsed_reports_datalab/<stem>/full.md  (page-anchored <!-- PAGE N -->)
#                                  pages.jsonl, meta.json (cost + checkpoint_id)

# HTML — for DETERMINISTIC table parsing (hybrid path), on the table pages only
python scripts/adapter/parse_html.py <stem> --page-range A-B
#   -> extracted_adapter/<stem>/portfolio.html  (preserves <sup> footnotes, /page/N/ block-ids)
```

Defaults: balanced, `token_efficient_markdown`, `save_checkpoint` (re-extract later without
re-paying the parse), images off. **Datalab is paid per page — always validate with
`--page-range` before a full run.**

Why two formats: markdown is best for an LLM to scan; **HTML is best for deterministic parsing**
because it preserves multi-row headers, merged section cells, and `<sup>` footnote markers that
markdown pipe tables flatten.

`<stem>` = the PDF stem, e.g. `09_C38U.SI_CapitaLand-Integrated-Commercial-Trust_FY2025`.

---

## 2. Locate — map the document before reading it

```bash
python .claude/skills/reit-extract/scripts/locate.py parsed_reports_datalab/<stem>/full.md
```

Prints: page-marker dialect, a **sub_sector guess** (keyword-weighted; Retail+Office co-dominant
⇒ Diversified), the **audited-FS start page**, and the page list for every anchor section
(Portfolio Statement, Gross Revenue note, Top-10 Tenants, Trade Mix, Distribution Statement,
Statistics of Unitholdings, Corporate Information, …). The agent reads only those pages
(chunked), never 200 pages linearly. The sub_sector picks the **playbook**.

---

## 3. Extraction — two paths

Both target the same 8-file intermediate and pass the same two gates. Choose by goal:

| Path | Skill | When |
|---|---|---|
| **Pure LLM** | `reit-extract` | one-off correctness; scattered sections |
| **Hybrid on-the-fly** | `reit-extract-hybrid` | batch scale; sections that are clean tables |

The **8-file intermediate** (in `extracted/<SYMBOL>.SI_FY<YYYY>/`): `profile, performance,
properties, top_tenants, trade_mix, income_components, property_transactions, _notes`. Maps to
the 6 schema tables (`income_components→sgx_reit_financial`); `property_transactions` is parked,
`_notes` is QC metadata. Field names follow `schema/models.py` exactly — year key is
**`financial_year`**, symbols carry `.SI`, money is **absolute** ($'000 → ×1000).

### 3A. Pure-LLM path (`reit-extract`)

A Sonnet agent reads the parsed markdown and writes the 8 files, following: three-tier valuation
rule (audited Portfolio Statement only), source precedence (audited wins conflicts), per-sub-sector
playbook, and the conventions (absolute money, `pct_basis` on every %, enums clean with verbatim
in `*_raw`, dual-basis captured). Validated on 5 archetypes (C38U, HMN, AJBU, BTOU, AW9U) — all
pass both gates.

### 3B. Hybrid on-the-fly path (`reit-extract-hybrid`) — the scaling design

**One agent per AR**, each authoring that report's extraction **plans on the fly**. Per section,
the loop is:

```
JUDGE  →  PLAN  →  RUN  →  CROSS-CHECK  →  LLM PASS  →  MERGE
```

**1. Judge (LLM).** Sample ~5 rows of the section's HTML table + read the schema fields. Decide:
- each **field** → `deterministic` (one cell / header-carried / trivial transform) /
  `needs_llm` (judgement or combine) / `other_source` (lives in a different table/page);
- the **section** → `hybrid` (a clean grid exists → write a plan) or `llm_only` (scattered →
  use the pure-LLM workflow for this section). *This is the feasibility gate.*
  Prior (confirm per report): properties / top_tenants / trade_mix / financial = hybrid;
  profile / performance = llm_only.

**2. Plan.** Author `extracted_adapter/<stem>/plan_<section>.json` — a **declarative** column→field
map (located by header text, not index) with a method per field. Methods: `const, text, enum,
parse_years, concat, scale, context (carry section headers down), page, needs_llm, absent_here`.

**3. Run (deterministic, no LLM per row).**
```bash
python scripts/adapter/run_adapter.py extracted_adapter/<stem>/plan_<section>.json
#   -> <section>_deterministic.json  +  <section>_deterministic.llm_todo.json
```
A generic engine consumes the plan (it is **not** exec'd generated code). It locates the table by
header text, strips `<sup>` footnotes (so "Westgate¹"→"Westgate" but "Junction 8" name-number is
kept), carries country/category/status section-headers down onto rows, and gates data rows on a
numeric `value_col`.

**4. Cross-check.** Row count vs the report's stated count; reconcile sums (Σ valuation/revenue vs
total); spot-check 3–5 rows vs the source page. Record matches + legit gaps (e.g. equity-accounted
JVs absent from the Portfolio Statement) in `status.json`.

**5. LLM pass (batched).** Resolve the `needs_llm` fields for ALL rows in ONE call (give the model
the row list + the relevant footnotes), save `llm_filled_<section>.json`.

**6. Merge.**
```bash
python scripts/adapter/merge_llm.py <section>_deterministic.json llm_filled_<section>.json plan_<section>.json
#   -> <section>_merged.json   (fills only needs_llm fields; runs an anomaly check)
```
`other_source` fields stay null until their own adapter/LLM pass fills them.

**Author a plan per report.** Layout is NOT guaranteed by sponsor or sub-sector (same type ≠
same layout across sponsors; same sponsor only a weak hint). What generalises is the engine +
the judge/plan step + the gates — not the plans. Plan authoring is cheap (the expensive per-row
transcription is already gone), so write a fresh plan each time. Reusing a prior plan (see
`plans/examples/`) is an optional shortcut that must always re-verify `table_contains` + columns
on the actual report; the gates catch a bad fit loudly.

---

## 4. Assemble + gate (never skip)

Combine the merged per-section records into the 8 files in `extracted/<SYMBOL>.SI_FY<YYYY>/`, then:

```bash
python .claude/skills/reit-extract/scripts/validate_schema.py  extracted/<SYMBOL>.SI_FY<YYYY>
python .claude/skills/reit-extract/scripts/check_extraction.py extracted/<SYMBOL>.SI_FY<YYYY>
```

- **validate_schema.py** — Pydantic type/enum contract against `schema/models.py`. Caught the
  `fiscal_year`→`financial_year` rename.
- **check_extraction.py** — reconciliation (Σ property vs reported totals, cross-currency aware),
  unit sanity (<1,000,000 trust-level ⇒ unscaled), provenance (`source_page` on every record),
  `pct_basis` discipline, enum discipline, fill rates. Reads `_notes.columns_never_fillable` so
  declared sub-sector-structural nulls become INFO not WARN.

Both must read `... PASS`. Fix every FAIL.

---

## 5. Track (batch progress)

Each AR agent keeps `extracted_adapter/<stem>/status.json` current (per-section status + method +
decisions + cross-check + gate verdicts). Then:

```bash
python scripts/adapter/track.py            # matrix: AR × section status + gates
```
Status lifecycle per section: `planned → run → merged → gated → done` (or `llm_only` / `skipped`).

---

## 6. Folder & file map

```
parsed_reports_datalab/<stem>/full.md                    markdown (locating)
extracted_adapter/<stem>/                                hybrid working dir
  portfolio.html | tenants.html | financial.html         HTML table pages
  plan_<section>.json                                    on-the-fly plan (LLM-authored)
  <section>_deterministic.json (+ .llm_todo.json)        deterministic output
  llm_filled_<section>.json                              batched LLM output
  <section>_merged.json                                  merged
  status.json                                            per-AR tracker
extracted/<SYMBOL>.SI_FY<YYYY>/                          FINAL 8-file output (gated, DB-loaded)
```

---

## 7. What's proven vs scaffolded

- ✅ **Parsing** — Datalab balanced, 6 reports parsed.
- ✅ **Pure-LLM extraction** — 5 archetypes, both gates pass.
- ✅ **Hybrid properties (Tier-C)** — C38U pilot: **25 rows in 0.28 s, 25/25 identical** to the
  LLM agent on valuation/tenure/term; LLM touched only `ownership`+`value_basis` in one 14 s
  batched call. ~20× faster, ~6× cheaper, reproducible.
- 🔄 **Scaffolded, not yet run** — the `top_tenants` / `trade_mix` / `financial` adapters (all
  clean grids); the per-property-cards adapter (occupancy/gla/nla/npi); full-corpus run.

---

## 8. Key learnings baked into the tooling

- **HTML > markdown** for deterministic parsing (multi-row headers, merged cells, `<sup>`).
- **Datalab page** lives on the `<table>` block-id (`/page/N/`), not per-row; `source_page` = N+1.
- **Locate tables by header text**, not index — positions shift between reports.
- **Footnote vs name-number**: strip `<sup>` tags, never a trailing-digit regex.
- **The gates are the safety net** — a plan that doesn't fit (wrong column, missed rows) fails
  reconciliation loudly.
- **Field-name discipline**: `financial_year` (not `fiscal_year`), `.SI` symbols, absolute money.

---

## 9. Run a new report (quick recipe)

```bash
python scripts/parse_datalab.py <stem>                                   # 1. parse md
python .claude/skills/reit-extract/scripts/locate.py parsed_reports_datalab/<stem>/full.md  # 2. locate
python scripts/adapter/parse_html.py <stem> --page-range <table-pages>   # 3. HTML
# 4. per section: judge -> plan_<section>.json -> run_adapter -> cross-check -> llm pass -> merge_llm
# 5. assemble 8 files in extracted/<SYMBOL>.SI_FY<YYYY>/
python .claude/skills/reit-extract/scripts/validate_schema.py  extracted/<SYMBOL>.SI_FY<YYYY>
python .claude/skills/reit-extract/scripts/check_extraction.py extracted/<SYMBOL>.SI_FY<YYYY>
python scripts/adapter/track.py                                          # 6. progress
```

Skills (read these for the detail): `.claude/skills/reit-extract-hybrid/SKILL.md` (+ REFERENCE) and
`.claude/skills/reit-extract/SKILL.md` (+ REFERENCE — schema field set, sub-sector playbooks,
quirks catalogue).
