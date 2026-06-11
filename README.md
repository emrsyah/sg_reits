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
| 6. Synthesized production schema v2 | ✅ done (`sgx_reit_schema_v2.md`) |
| 7. Adversarial validation round (6 stress-test trusts) | ✅ passed — see schema doc §10 |
| 8. Ingestion plan (parse routing + extraction + validation) | ✅ done (`ingestion_plan.md`) |
| 9. Bake-off → extraction pilot → DB load | ⬜ next |

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
feedback_reflection.md                    Response to schema review feedback, validated against
                                          9 parsed ARs (terminology aliases, tenant-mix scopes,
                                          GRI vs NPI boundary, standardized-metric strategy)
sgx_reit_schema_v2.md                     FINAL synthesized schema: 14-report evidence + draft
                                          workbook + feedback + v1 proposal + prod conventions
                                          (+ §10 adversarial validation on 6 more trusts)
ingestion_plan.md                         Production parsing/extraction plan: free local pass +
                                          section routing + premium parse on hard pages only +
                                          batch structured extraction + validation invariants
REITS db.xlsx                             Colleague's draft data schema (reference)
```

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
