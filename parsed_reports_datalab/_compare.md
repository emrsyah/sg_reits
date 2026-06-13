# Datalab (Marker/Surya) vs agentic LlamaParse — quality compare

`pipe_table_rows` + `html_table_tags` proxy surviving table structure;
`chars` is raw text volume. Datalab emits clean markdown pipe tables, agentic
emits HTML `<td>` tables — both are structured (unlike LiteParse's flattening).

| Doc | Parser | Pages | Chars | Pipe rows | HTML cells | Cost | Seconds |
|---|---|---:|---:|---:|---:|---:|---:|
| 17_AW9U.SI_First-REIT_FY2025 | **datalab:balanced** | 208 | 573,884 | 2,138 | 0 | 63c | 63.4 |
| 17_AW9U.SI_First-REIT_FY2025 | agentic | 208 | 670,628 | 0 | 8,949 | — | (cloud) |
| 28_M44U.SI_Mapletree-Logistics-Trust_FY2025 | **datalab:balanced** | 235 | 697,279 | 2,635 | 0 | 71c | 50.7 |
| 28_M44U.SI_Mapletree-Logistics-Trust_FY2025 | agentic | 235 | 998,796 | 0 | 18,451 | — | (cloud) |