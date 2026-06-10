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
| 3. Parse sample with LlamaParse agentic tier | ✅ 5 of 7 (credits exhausted) |
| 4. Extractability analysis + schema design | ✅ done |
| 5. Structured extraction (LlamaExtract) → DB load | ⬜ next |

## Repository layout

```
singapore_reits_annual_reports.md/.json   Catalog of AR links per trust (FY2023–25)
download_reports.py                       PDF downloader, standardized naming:
                                          {id:02d}_{symbol}_{name}_FY{year}.pdf
reconcile.py                              Rebuilds annual_reports/_manifest.csv from disk,
                                          reports gaps vs expected slots
annual_reports/                           ~101 downloaded PDFs + _manifest.csv

parse_sample.py                           LlamaParse (agentic tier) batch parser, create+poll
fetch_results.py                          Re-fetch completed parse jobs by job_id (free)
list_jobs.py                              Inspect parse jobs on the LlamaCloud account
parsed_reports/<stem>/                    Per report: full.md (page-anchored markdown),
                                          pages.jsonl (per-page markdown + item types), meta.json
parsed_reports/_inventories.md            Per-report data inventories with page references

schema_analysis.md                        Cross-report commonality matrix + generic schema design
reit_schema_proposal.md                   Review of draft workbook + sgx_reit_* production
                                          schema proposal (aligned with prod sgx_* conventions)
REITS db.xlsx                             Colleague's draft data schema (reference)
```

## Parsed sample (all FY2025, stratified by sector/structure)

| Trust | Sector | Pages |
|---|---|---|
| CapitaLand Integrated Commercial Trust (C38U) | Retail + Office | 199 |
| Keppel DC REIT (AJBU) | Data centres | 200 |
| Mapletree Logistics Trust (M44U) | Logistics, March FYE | 235 |
| First REIT (AW9U) | Healthcare | 208 |
| Far East Hospitality Trust (Q5T) | Hospitality, stapled trust | 251 |

Stoneweg Europe (EUR) and KORE US (USD) were planned but blocked on LlamaCloud plan credits.

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
pip install requests llama-cloud openpyxl
$env:LLAMA_CLOUD_API_KEY = "llx-..."

python download_reports.py    # fetch PDFs into annual_reports/
python reconcile.py           # rebuild manifest, report gaps
python parse_sample.py        # parse sample set via LlamaParse agentic tier
```

Notes: parsing a ~250-page report on agentic tier takes several minutes and significant credits;
`parse_sample.py` skips reports already present in `parsed_reports/`. Completed jobs can be
re-downloaded for free with `fetch_results.py` (job IDs are printed by the parse run), and
**LlamaExtract accepts existing parse-job IDs as input** — the next stage needs no re-parsing.

## Next steps

1. LlamaExtract with Pydantic schemas per data block (start from the 5 existing parse jobs),
   cross-validating totals (segments vs revenue, property valuations vs balance sheet).
2. Top up LlamaCloud credits; parse the full corpus incl. FY2023/24 backfill for 3-year trends.
3. Implement `sgx_reit_*` tables per `reit_schema_proposal.md` and pilot the NL-query layer on
   the 5 parsed trusts before scaling to all 39.
