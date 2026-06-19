# Datalab (Marker/Surya) vs agentic LlamaParse — quality compare

`pipe_table_rows` + `html_table_tags` proxy surviving table structure;
`chars` is raw text volume. Datalab emits clean markdown pipe tables, agentic
emits HTML `<td>` tables — both are structured (unlike LiteParse's flattening).

| Doc | Parser | Pages | Chars | Pipe rows | HTML cells | Cost | Seconds |
|---|---|---:|---:|---:|---:|---:|---:|
| 39_ODBU.SI_United-Hampshire-US-REIT_FY2025 | **datalab:balanced** | 220 | 611,152 | 1,929 | 0 | 88.0c | 46.2 |
| 39_ODBU.SI_United-Hampshire-US-REIT_FY2025 | agentic | 220 | 660,669 | 0 | 7,624 | — | (cloud) |