# Datalab (Marker/Surya) vs agentic LlamaParse — quality compare

`pipe_table_rows` + `html_table_tags` proxy surviving table structure;
`chars` is raw text volume. Datalab emits clean markdown pipe tables, agentic
emits HTML `<td>` tables — both are structured (unlike LiteParse's flattening).

| Doc | Parser | Pages | Chars | Pipe rows | HTML cells | Cost | Seconds |
|---|---|---:|---:|---:|---:|---:|---:|
| 23_K71U.SI_Keppel-REIT_FY2025 | **datalab:balanced** | 228 | 872,722 | 2,997 | 0 | 92.0c | 42.0 |
| 23_K71U.SI_Keppel-REIT_FY2025 | agentic | 228 | 1,002,831 | 0 | 12,410 | — | (cloud) |