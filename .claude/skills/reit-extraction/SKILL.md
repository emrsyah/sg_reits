---
name: reit-extraction
description: Extract structured data from parsed SGX REIT annual reports (markdown from any parser - agentic/cheap LlamaParse, LiteParser, etc.) into the sgx_reit_* schema JSON files, with page provenance and mandatory reconciliation. Use when extracting, re-extracting, or verifying REIT annual report data, when the user mentions extraction against the schema, parsed_reports, or adding a new trust/fiscal year to extracted/.
---

# REIT annual-report extraction

Turn a parsed annual report (markdown) into schema-shaped JSON under
`extracted/<SYMBOL>_FY<YYYY>/`. Target schema: `schema/sgx_reit_schema.md` — the locked
6-table plan of record (`sgx_reit_schema_final.md`/`_v2`/`_v3` are superseded, in `archive/`).

**Intermediate files → 6 final tables.** The 8 JSON files below are the extraction
intermediate; they map to the schema's 6 tables as: `profile→sgx_reit_profile`,
`properties→sgx_reit_property`, `performance→sgx_reit_performance`,
`top_tenants→sgx_reit_top_tenant`, `trade_mix→sgx_reit_trade_mix`,
`income_components→sgx_reit_financial` (renamed). `property_transactions` is **parked**
(the transaction layer is out of scope in the final schema) — keep capturing it for the
audit trail, it just isn't loaded. `_notes` is QC metadata, never loaded.

## Quick start

```bash
# 1. Index the document (parser-agnostic: detects page markers or estimates pages)
python .claude/skills/reit-extraction/scripts/locate.py parsed_reports/<dir>/full.md

# 2. Extract (workflow below) -> write the 8 JSON files

# 3. QC gate - never skip; it has caught real errors (duplicate-row tables)
python .claude/skills/reit-extraction/scripts/check_extraction.py extracted/<SYMBOL>_FY<YYYY>
```

## Workflow

1. **Detect the parser dialect first.** Page markers vary: `<!-- PAGE N -->` (agentic
   LlamaParse), `--- N ---`, `{N}---`, `Page N of M`, or none. `locate.py` handles known
   formats and falls back to char-offset estimates (then mark pages `"p_estimated": true`).
   Tables may be HTML (`<td>`), pipe-markdown, or mangled plaintext — cheap parsers merge
   columns; see REFERENCE.md §4 for recovery tactics.
2. **Build a section map** with `locate.py` / Grep before reading anything linearly.
   The ~10 anchor sections and proven grep patterns are in REFERENCE.md §1.
3. **Extract in trust order**: audited financial statements > audited Portfolio Statement
   > financial review tables > property factsheets > highlights pages. When two pages
   disagree, the audited figure wins and the conflict goes in `_notes.json`.
4. **Apply the conventions** (non-negotiable):
   - amounts in ABSOLUTE units (S$82.8m → 82800000; tables in $'000 → ×1000 — check the
     column header every time)
   - as-disclosed only; NEVER compute, impute, or annualise a figure
   - every record carries `source_page` (int)
   - every percentage carries its basis, in the report's own wording mapped to the
     `pct_basis` enum (REFERENCE.md §3)
   - when a figure exists on both 100% and proportionate basis, capture the basis —
     never just the number (this caused the only diffs in blind verification); on
     property rows set `value_basis` (consolidated | joint_venture_100pct |
     effective_interest) whenever ownership < 100 or the asset is JV/associate-held
   - `performance.portfolio_value` = the headlined portfolio valuation INCLUDING
     proportionate JV interests, not the balance-sheet investment-properties figure
   - dual currency: SGD primary + `*_rmb`/local fields; record any disclosed FX rate
   - `null` = not disclosed — but ONLY after checking the section-map anchors for that
     field (REFERENCE.md §1); record which anchors you checked in the `note`. A blind-run
     audit caught "not disclosed" twice for a figure that was on a mapped page.
   - when two values exist for one fact, store the chosen one AND the alternative
     (`alt_value`, `alt_basis`, conflict note) — annotating only the chosen value's basis
     silently buries the conflict
   - valuation-source precedence: when a property is valued in BOTH an audited statement
     (reporting currency) and a factsheet (local-currency appraisal), the audited figure
     wins `market_valuation`; the factsheet figure goes to `alt_value`/`alt_basis` with
     its own currency named (the Opus/Sonnet benchmark split exactly here on all 19
     Daiwa properties)
   - enum columns hold ONLY their enum values: `land_tenure` is `Freehold` or `Leasehold`
     — "Leasehold interest", "Land title type" wording etc. belongs verbatim in
     `tenure_raw`. The QC gate FAILs anything else
   - if `tenure_raw` mentions an expiry ("expiring 13 December 2110"), `lease_expiry_date`
     MUST be filled — your own verbatim string proves the date is disclosed; the QC gate
     cross-checks this
   - partial dates: when only month-year is disclosed ("expiring March 2067"), use day 01
     (`2067-03-01`) and say so in a note — never silently invent month-end
   - `value_basis` semantics: a consolidated-but-minority-owned property (line-by-line in
     the audited statements, NCI below) is `consolidated`; `joint_venture_100pct` /
     `effective_interest` are reserved for equity-accounted assets
   - top tenants ranked by something other than GRI (e.g. Daiwa ranks by % of NPI) still
     go in `gri_percentage` with `pct_basis` saying what it is — never invent a key
   - use EXACTLY the output field names specified; never bake units into key names
     (`gross_revenue_sgd_million` is a red flag that the value broke the units rule)
5. **Write the 8 files**: `profile, performance, properties, property_transactions,
   top_tenants, trade_mix, income_components, _notes` — exact shapes in REFERENCE.md §2.
   Two fields the final schema requires that older runs omitted: `profile.management`
   (jsonb array `[{role, company_name}]`; roles: reit_manager | property_manager |
   trustee | sponsor | operator | master_lessee) and `trade_mix.category_raw` (the
   verbatim disclosed label, alongside `category` mapped to the schema's canonical enum).
6. **Run `check_extraction.py`** — validates JSON, fill rates, provenance, basis-on-pct,
   and the Σ(property) vs reported-total reconciliations. Fix DIFFs before finishing:
   a non-reconciling sum usually means a duplicate/merged table row, a missed property,
   or a JV property that is equity-accounted (outside the consolidated total).
7. **Fill `_notes.json`** honestly: `columns_never_fillable` (with the structural reason),
   `data_with_no_home` (max ~12 material items — this feeds schema iteration),
   `parsing_traps`, `reconciliation`. The QC gate READS `columns_never_fillable`:
   a null column declared there is reported as INFO instead of WARN, so honest
   declarations are what keep your gate output clean — never declare a column
   structural just to silence a warning.

## Known traps (the ones that produce wrong-but-plausible data)

Full table in REFERENCE.md §3. The five that bite hardest:

| Trap | Rule |
|---|---|
| "Term of lease" in a Portfolio Statement | It is the REIT's LAND lease, not a tenant lease; "Freehold" appears as a literal string in numeric columns |
| "Gross revenue" ≠ GRI | GR = GRI + car park + recoveries + service charges; store under the report's name |
| Same fact, two bases | 100% vs proportionate (valuations), consolidated vs attributable (NPI), incl vs excl GTO (tenant %) |
| Duplicate / merged table rows | Parser artifact; pick the set that reconciles to the audited total, note the artifact |
| Distributable income layering | Headline ≠ distribution-statement subtotal ≠ amount incl. opening balance / top-ups; take the headline, note the layers |

## Self-check before finishing (cheap-model audit findings)

- Any money value < 1,000,000? You almost certainly left it in $'000 or millions — rescale.
- Every `null` must name the anchors checked; every dual-printed figure must carry its
  alternative.
- Your FINAL MESSAGE must be derived by re-reading your written JSON, not from memory —
  one audited run claimed "no dual-basis figures" while its own output contained one.

## Model tiers (measured, 3-trust blind benchmark)

- **Primary extraction: Sonnet-class or better.** Both tiers find the numbers (zero
  hallucinations observed in either); the expensive model's edge is judgment — flagging
  dual-basis conflicts, exhausting the section map before declaring "not disclosed".
- **Cross-check/verification tier: Haiku + this skill + the QC gate** is acceptable
  (71/74 value-accurate, 2–4× faster, ~3× cheaper). The skill transfers conventions to
  cheap models reliably, but NOT judgment — so never let a cheap-model run skip
  `check_extraction.py`, whose reconciliation catches unit drift loudly.

## Scaling & verification

- One agent per report (subagent prompt template: REFERENCE.md §5); reports are 600–850KB,
  never read linearly — chunked Read driven by the section map.
- For neutrality checks, run a blind re-extraction of a stratified sample (no access to
  prior output) and diff — see REFERENCE.md §6.
- After extraction, rebuild the human verification bench: `python scripts/build_verify_html.py`.
