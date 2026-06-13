# LiteParse (local, open-source) vs agentic LlamaParse — quality compare

Same PDFs, two parsers. `pipe_table_rows` + `html_table_tags` proxy how much
tabular structure survived (the thing that matters for the audited portfolio /
financial-review tables). `chars` is raw text volume. Eyeball the two `full.md`
files side by side for the real verdict — these numbers only point you at where.

| Doc | Parser | Pages | Chars | Pipe-table rows | HTML table tags | Seconds |
|---|---|---:|---:|---:|---:|---:|
| 09_C38U.SI_CapitaLand-Integrated-Commercial-Trust_FY2025 | **liteparse** | 199 | 804,747 | 3 | 0 | 79.9 |
| 09_C38U.SI_CapitaLand-Integrated-Commercial-Trust_FY2025 | agentic | 199 | 734,846 | 0 | 11,545 | (cloud) |
| 28_M44U.SI_Mapletree-Logistics-Trust_FY2025 | **liteparse** | 235 | 1,086,179 | 0 | 0 | 93.8 |
| 28_M44U.SI_Mapletree-Logistics-Trust_FY2025 | agentic | 235 | 998,796 | 0 | 18,451 | (cloud) |

## How to read this
- **Far fewer table rows on liteparse** = it flattened tables to plain text;
  expect the audited portfolio statement / financial review to need OCR-table
  recovery or the agentic tier (this is the hybrid-routing call from
  `docs/extraction_strategy_research.md`).
- **Similar chars but lower tables** = text is there, structure is lost.
- **Much lower chars** = missed pages/columns (check scanned pages, OCR).

Open both to compare a known-hard page (CICT portfolio statement ~p.109):
```
parsed_reports/09_C38U..._FY2025/full.md            # agentic
parsed_reports_liteparse/09_C38U..._FY2025/full.md  # liteparse
```