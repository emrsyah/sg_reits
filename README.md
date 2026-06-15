# S-REITs Data Exploration

Groundwork for the **Singapore REITs feature on [sectors.app](https://sectors.app)**: collect
SGX-listed REIT annual reports, parse them into machine-readable form, analyze what data is
reliably extractable, and design the production schema for a queryable, agentic-AI-ready
financial data layer.

## Pipeline status

| Stage | Status |
|---|---|
| 1. Catalog annual report links (39 trusts, FY2023–FY2025) | ✅ done |
| 2. Download PDFs (~101 of 117 slots; rest unpublished/manual) | ✅ done |
| 3. Parse sample with LlamaParse agentic tier | ✅ 22 reports (20 usable ARs) |
| 4. Extractability analysis + schema design | ✅ done |
| 5. Schema review feedback → evidence-based reflection | ✅ done (`feedback_reflection.md`) |
| 6. Synthesized production schema v2 → locked 6-table schema | ✅ done (`schema/sgx_reit_schema.md`) |
| 7. Adversarial validation round (6 stress-test trusts) | ✅ passed — see schema doc §10 |
| 8. Ingestion plan (parse routing + extraction + validation) | ✅ done (`ingestion_plan.md`) |
| 9. Switch parsing engine to **Datalab** (balanced, cheaper + cleaner tables) | ✅ done (`parsed_reports_datalab/`) |
| 10. Pure-LLM extraction skill, validated on 5 archetypes | ✅ done (`reit-extract`, both gates pass) |
| 11. **Hybrid on-the-fly extraction** (deterministic adapters + LLM judgement) for batch scale | 🔄 piloted (C38U properties); skill = `reit-extract-hybrid` |
| 12. Run full corpus (one agent per AR) → DB load + NL-query layer | ⬜ next |

## Repository layout

```
schema/
  sgx_reit_schema.md            CANONICAL schema — the locked 6-table plan of record
                                (sgx_reit_profile/property/performance/top_tenant/
                                trade_mix/financial + mv_sgx_reit)
  models.py                     Pydantic mirror of the 6 tables — the field contract
                                (shared by the validation gate + extraction)

annual_reports/                 ~101 downloaded PDFs + _manifest.csv  (run dir, root)
parsed_reports/<stem>/          LlamaParse (agentic) output — legacy parses
parsed_reports_datalab/<stem>/  Datalab (balanced) output — CURRENT parser: full.md
                                (page-anchored), pages.jsonl, meta.json (cost+checkpoint)
extracted/<SYMBOL>.SI_FY<YYYY>/ FINAL extraction output — 8 JSON files per trust-year,
                                gated; the canonical store loaded to the DB
extracted_adapter/<stem>/       Hybrid working dir: per-section HTML, plan_<section>.json
                                (LLM-authored), deterministic/merged outputs, status.json

scripts/
  download_reports.py           PDF downloader, naming {id:02d}_{symbol}_{name}_FY{yr}.pdf
  reconcile.py                  Rebuild annual_reports/_manifest.csv, report gaps
  parse_datalab.py              Datalab parser (balanced, token-efficient, checkpoint) → md
  parse_datalab_extract.py      Datalab page_schema structured extraction (A/B harness)
  parse_sample.py               LlamaParse (agentic) batch parser — legacy
  fetch_results.py / list_jobs.py   LlamaCloud job re-fetch / inspect — legacy
  build_verify_html.py          Build the human verification bench HTML from extracted/
  adapter/                      HYBRID on-the-fly extraction engine:
    parse_html.py               Datalab convert → HTML (preserves <sup> + page block-ids)
    run_adapter.py              generic plan engine: plan_<section>.json + HTML → records
    merge_llm.py                merge the batched LLM pass back; anomaly check
    track.py                    progress matrix across all ARs (from status.json)
  review/                       PROOFREADING COCKPIT (Flask): PDF left + extracted records
    app.py                      right; mark ✓/✗/? per record, saved to reviews/<stem>.json
    sanity_scan.py              non-interactive sanity checker over extracted/
    README.md                   install + run details

catalog/
  singapore_reits_annual_reports.md/.json   Catalog of AR links per trust (FY2023–25)

docs/                           Dated analysis / journey-of-record (NOT the live schema):
  schema_analysis.md            Cross-report commonality matrix + generic schema design
  feedback_reflection.md        Response to schema review feedback (validated vs 9 ARs)
  ingestion_plan.md             Production parsing/extraction plan + validation invariants

archive/                        Superseded work, kept for reference (incl. old schema drafts,
                                first 8-table pilot, presentation HTML, reference workbook)

.claude/skills/
  reit-extract/                 Pure-LLM extraction skill (Datalab-tuned): SKILL + REFERENCE
                                + scripts/ (locate.py, validate_schema.py, check_extraction.py)
  reit-extract-hybrid/          Batch-scale skill: one agent per AR authoring its own
                                on-the-fly deterministic plans + LLM judgement; plans/ library
  reit-extraction/              First-gen skill (parser-agnostic) — superseded by the above
```

The pipeline hardcodes the data run-dirs (`annual_reports/`, `parsed_reports*/`,
`extracted/`, `extracted_adapter/`) at the repo root by design. Scripts resolve paths from
their own location (`Path(__file__).parent.parent`), so they work from anywhere, but the
documented convention is to run them from the repo root.

## Extraction approach (current direction)

Parsing now runs on **Datalab (balanced mode)** — cheaper than the agentic LlamaParse tier
(~0.4¢/page) and emits cleaner tables (markdown pipe tables for reading, HTML for
deterministic parsing). The full FY2025 corpus parses for ~$26.

Extraction has two complementary skills, both targeting the locked 6-table schema and gated
by `validate_schema.py` (Pydantic/type+enum) **and** `check_extraction.py` (reconciliation/
units/provenance):

- **`reit-extract` (pure LLM)** — a Sonnet agent reads the parsed markdown and writes the 8
  schema JSON files. **Assumption-free / discovery-first**: it works from a small set of
  *invariants* (the schema target; valuation only from the audited Portfolio Statement in
  `'000`; income = the full Statement of Total Return; absolute money + provenance + reconcile
  to disclosed totals) and **discovers everything else from the report** — where each table is,
  its shape, and whether a field is present. The per-sub-sector notes are *illustrative priors*,
  never rules (reports don't generalise by sub-sector; assuming they do caused real
  under-captures). Best for one-off correctness.

- **`reit-extract-hybrid` (on-the-fly deterministic + LLM)** — the **scaling** path for the
  ~40-report corpus. Per-row LLM transcription is the bottleneck (regenerating 180 property
  rows as output tokens takes minutes), but that data sits in clean tables. So **each AR is
  handled by its own agent that writes that report's extraction *plans* on the fly**:

  1. **Discover** — ScaleDown maps the report to the schema with no assumptions:
     `page_map.py` summarises each page, `page_map_classify.py` **classifies** every page
     against the 6 tables (sub-sector-agnostic rubrics) → `schema_pages_v2.json` ranks the
     candidate pages per table (`top_audited_000` = the audited '000 statement vs marketing
     millions). The agent routes off this, reading every candidate before deciding.
  2. **Judge** (LLM) — per section, sample ~5 rows + the schema and decide each field
     `deterministic` / `needs_llm` / `other_source`, and whether the section is a clean grid
     (`hybrid`) or scattered (`llm_only`).
  3. **Plan** — author `plan_<section>.json` (column→field map + transforms), locating the
     table by header text so it survives layout shifts.
  4. **Run** — a generic, declarative engine (`run_adapter.py`, *not* exec'd codegen) pulls
     every row deterministically.
  5. **Cross-check** — counts + reconciliation + spot-check vs the source.
  6. **LLM pass** — resolve the `needs_llm` fields for all rows in one batched call, then
     **merge back** (`merge_llm.py`), never overwriting deterministic values.
  7. **Assemble + gate + track** — write the 8 final files, run both gates, keep
     `status.json` current (`track.py` shows progress across all ARs).

  A plan is **authored fresh per report** — layout is not guaranteed by sponsor or sub-sector,
  so what generalises is the engine + the judge/plan step + the gates, not the plans (plan
  authoring is cheap once per-row transcription is gone). Reuse is an optional shortcut that
  always re-verifies columns; the gates catch a bad fit.

  *Pilot (C38U properties):* deterministic Tier-C = **25 rows in 0.28 s, 25/25 identical** to
  the pure-LLM agent on valuation/tenure/term; the LLM touched only 2 judgment fields in one
  14 s batched call. ~20× faster, ~6× cheaper, reproducible.

## Parsed sample (stratified by sector/structure/currency)

| Trust | Sector | Pages |
|---|---|---|
| CapitaLand Integrated Commercial Trust (C38U) | Retail + Office | 199 |
| Keppel DC REIT (AJBU) | Data centres | 200 |
| Mapletree Logistics Trust (M44U) | Logistics, March FYE | 235 |
| First REIT (AW9U) | Healthcare | 208 |
| Far East Hospitality Trust (Q5T) | Hospitality, stapled trust | 251 |
| CapitaLand Ascendas REIT (A17U) | Industrial / business space | 212 |
| Frasers Centrepoint Trust (J69U) | Suburban retail, Sept FYE | 222 |
| KORE US REIT (CMOU) | US office, USD | 163 |
| Stoneweg Europe Stapled Trust (SET) | European logistics/office, EUR | 404 |
| Sasseur REIT (CRPU) FY2024 | ⚠ mis-catalogued: sustainability report only | 40 |
| Sasseur REIT (CRPU) FY2023 | China outlet malls, EMA income model | 228 |
| CapitaLand China Trust (AU8U) | China retail/business parks, RMB | 180 |
| Keppel REIT (K71U) | Prime office, JV-heavy (attributable basis) | 228 |
| Elite UK REIT (MXNU) | UK gov-tenanted, GBP, FRI leases | 192 |
| CapitaLand Ascott Trust (HMN) | Global lodging, 3 contract types | 297 |
| Centurion Accommodation REIT (8C8U) | Worker/student dorms, IPO stub period | 83 |
| CapitaLand India Trust (CY6U) | India business trust, INR, dev pipeline | 216 |
| Daiwa House Logistics Trust (DHLU) | Japan logistics, JPY, TMK structures | 216 |
| Digital Core REIT (DCRU) | US/DE/JP data centres, USD, partial stakes | 220 |
| Manulife US REIT (BTOU) | Distressed US office, restructuring | 152 |
| Suntec REIT (T82U) | SG diversified + convention centre, JVs | 199 |
| United Hampshire US REIT (ODBU) | US grocery retail + self-storage, USD | 220 |

Note: the catalogued Sasseur FY2024 "AR" link is actually its sustainability report; the FY2023
AR (parsed above) covers the Entrusted Management Agreement income model instead.

## Key findings (detail in `schema_analysis.md`)

- A **universal core** is present in 5/5 reports: financial highlights, audited statements,
  per-property portfolio statement, capital management (gearing/ICR/debt maturity), per-period
  DPU, unitholder stats, fee formulas, segments, lease expiry, top tenants, cap-rate ranges.
- **Sector long tail** (RevPAR, PUE, beds, tenant sales…) and ESG vary too much for fixed
  columns → canonical-metric fact table + alias dictionary.
- Notes-to-FS tables parse cleanest; face statements are the most fragile; charts come out as
  low-precision tables → every fact needs provenance (page) + confidence.

## Usage

```powershell
pip install requests datalab-python-sdk pandas beautifulsoup4 lxml pydantic openpyxl
# secrets in .env (gitignored): DATALAB_API_KEY=...   (LLAMA_CLOUD_API_KEY for legacy parse)

python scripts/download_reports.py            # fetch PDFs into annual_reports/
python scripts/reconcile.py                   # rebuild manifest, report gaps
python scripts/parse_datalab.py <stem>        # parse to markdown (balanced, ~0.4c/page)

# --- hybrid extraction (per AR) ---
python .claude/skills/reit-extract/scripts/locate.py parsed_reports_datalab/<stem>/full.md
python scripts/adapter/parse_html.py <stem> --page-range A-B    # HTML for the table pages
python scripts/adapter/run_adapter.py extracted_adapter/<stem>/plan_<section>.json
python scripts/adapter/merge_llm.py <det>.json <llm_filled>.json <plan>.json
python .claude/skills/reit-extract/scripts/validate_schema.py  extracted/<SYMBOL>.SI_FY<YYYY>
python .claude/skills/reit-extract/scripts/check_extraction.py extracted/<SYMBOL>.SI_FY<YYYY>
python scripts/adapter/track.py               # progress across all ARs
```

### Proofreading cockpit (manual review)

A Flask tool for human verification: the annual-report **PDF on the left**, the **extracted
records on the right**; mark each record ✓ correct / ✗ false / ? unsure, add notes, and
type per-field **suggested corrections** — all saved to `reviews/<stem>.json`. Suggestions
are recorded alongside the verdict and never modify the canonical `extracted/` JSON.

```powershell
pip install flask                  # only dependency beyond the parse/extract stack
python scripts/review/app.py       # → http://127.0.0.1:5057  (use Chrome or Edge)
```

No build step — it reads `extracted/` and `annual_reports/` at request time. The bundled
server is **local single-user**; see `scripts/review/README.md` for details.

Notes: Datalab is a paid per-page API — validate with `--page-range` before full runs;
`parse_datalab.py` saves a checkpoint (re-extract without re-paying the parse). The skills
drive the agent through the per-section judge → plan → run → cross-check → merge loop; the
commands above are the underlying engine. Legacy LlamaParse (`parse_sample.py`,
`fetch_results.py`) is kept for the existing `parsed_reports/` only.

## Next steps

Hardening phases A–D are done (see `docs/extraction_hardening_phases.md`): the hybrid pipeline
is proven end-to-end on 4 families, both gates green, with deterministic + LLM-lane + llm_only
fallback paths. Remaining:

1. **Phase E — run the full corpus** with one `reit-extract-hybrid` agent per AR (a fresh plan
   authored per report), tracked via `status.json` + `track.py`, both gates green each; a
   stratified accuracy audit (one per sub-sector) hybrid-vs-pure-LLM before trusting the batch.
   Then FY2023/24 backfill for 3-year trends.
2. **Build the positional-join engine mode** (or keep the LLM fallback) for facing-page-split
   statements (Mapletree big portfolios, e.g. MLT).
3. Implement the `sgx_reit_*` tables per `schema/sgx_reit_schema.md`, project the 8-file
   intermediate to exact schema columns, load, and pilot the NL-query layer.
