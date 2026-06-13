# Datalab (Marker/Surya) vs agentic LlamaParse — quality compare

`pipe_table_rows` + `html_table_tags` proxy surviving table structure;
`chars` is raw text volume. Datalab emits clean markdown pipe tables, agentic
emits HTML `<td>` tables — both are structured (unlike LiteParse's flattening).

| Doc | Parser | Pages | Chars | Pipe rows | HTML cells | Cost | Seconds |
|---|---|---:|---:|---:|---:|---:|---:|
| 12_DHLU.SI_Daiwa-House-Logistics-Trust_FY2025 | **datalab:balanced** | 216 | 706,340 | 1,895 | 18 | 65c | 56.4 |
| 12_DHLU.SI_Daiwa-House-Logistics-Trust_FY2025 | agentic | 216 | 765,329 | 0 | 8,351 | — | (cloud) |
| 07_AU8U.SI_CapitaLand-China-Trust_FY2025 | **datalab:balanced** | 180 | 536,857 | 2,233 | 0 | 54c | 48.1 |
| 07_AU8U.SI_CapitaLand-China-Trust_FY2025 | agentic | 180 | 649,603 | 0 | 9,786 | — | (cloud) |