# Datalab (Marker/Surya) vs agentic LlamaParse — quality compare

`pipe_table_rows` + `html_table_tags` proxy surviving table structure;
`chars` is raw text volume. Datalab emits clean markdown pipe tables, agentic
emits HTML `<td>` tables — both are structured (unlike LiteParse's flattening).

| Doc | Parser | Pages | Chars | Pipe rows | HTML cells | Cost | Seconds |
|---|---|---:|---:|---:|---:|---:|---:|
| 34_CRPU.SI_Sasseur-REIT_FY2024 | **datalab:balanced** | 216 | 631,207 | 1,586 | 0 | 65.0c | 224.1 |
| 34_CRPU.SI_Sasseur-REIT_FY2024 | agentic | 40 | 123,708 | 0 | 1,105 | — | (cloud) |