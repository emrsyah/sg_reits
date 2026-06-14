# Datalab (Marker/Surya) vs agentic LlamaParse — quality compare

`pipe_table_rows` + `html_table_tags` proxy surviving table structure;
`chars` is raw text volume. Datalab emits clean markdown pipe tables, agentic
emits HTML `<td>` tables — both are structured (unlike LiteParse's flattening).

| Doc | Parser | Pages | Chars | Pipe rows | HTML cells | Cost | Seconds |
|---|---|---:|---:|---:|---:|---:|---:|
| 18_J69U.SI_Frasers-Centrepoint-Trust_FY2025 | **datalab:balanced** | 222 | 684,795 | 2,483 | 45 | 67c | 46.4 |
| 18_J69U.SI_Frasers-Centrepoint-Trust_FY2025 | agentic | 222 | 781,332 | 0 | 10,798 | — | (cloud) |