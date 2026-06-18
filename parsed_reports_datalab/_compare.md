# Datalab (Marker/Surya) vs agentic LlamaParse — quality compare

`pipe_table_rows` + `html_table_tags` proxy surviving table structure;
`chars` is raw text volume. Datalab emits clean markdown pipe tables, agentic
emits HTML `<td>` tables — both are structured (unlike LiteParse's flattening).

| Doc | Parser | Pages | Chars | Pipe rows | HTML cells | Cost | Seconds |
|---|---|---:|---:|---:|---:|---:|---:|
| 14_MXNU.SI_Elite-UK-REIT_FY2025 | **datalab:balanced** | 192 | 671,308 | 1,512 | 0 | 77c | 56.4 |
| 14_MXNU.SI_Elite-UK-REIT_FY2025 | agentic | 192 | 689,444 | 0 | 7,052 | — | (cloud) |