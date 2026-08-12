# REIT Document RAG

Use this when an agent needs source-grounded annual-report context from the parsed FY2025 REIT corpus.

The corpus is already chunked and embedded in Supabase:

- Table: `sgx_reit_doc_chunk`
- Model: `voyage-4-large`
- Dimension: `1024`
- Rows: 9,310 chunks across 37 reports
- Page anchors come from `parsed_reports_datalab/*/full.md` markers like `<!-- PAGE 123 -->`.

## CLI

```powershell
python scripts\rag\search_reit_docs.py "portfolio occupancy" --limit 5
python scripts\rag\search_reit_docs.py "debt maturity" --symbol C38U.SI --context-only
python scripts\rag\search_reit_docs.py "where does OUE disclose occupancy?" --symbol TS0U.SI --prompt
python scripts\rag\search_reit_docs.py "valuation of held for sale properties" --json
```

## Python

```python
from scripts.rag.reit_doc_rag import search_chunks, format_context, build_rag_prompt

chunks = search_chunks("portfolio occupancy", symbol="O5RU.SI", limit=5)
context = format_context(chunks)
prompt = build_rag_prompt("Where is portfolio occupancy disclosed?", chunks)
```

## Citation Rule

Every result includes `symbol`, `financial_year`, `page_start`, `page_end`, and `heading_path`.
When answering, cite like:

```text
O5RU.SI FY2025 p163
```

If the retrieved context does not contain the answer, say the context is insufficient rather than guessing.
