#!/usr/bin/env python3
"""Search embedded SGX REIT annual-report chunks.

Examples:
  python scripts/rag/search_reit_docs.py "where is portfolio occupancy disclosed?"
  python scripts/rag/search_reit_docs.py "portfolio occupancy" --symbol O5RU.SI --context-only
  python scripts/rag/search_reit_docs.py "debt maturity" --json
"""
from __future__ import annotations

import argparse
import pathlib
import sys
import textwrap

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.rag.reit_doc_rag import build_rag_prompt, dumps_payload, format_context, search_chunks


def print_human(query: str, chunks) -> None:
    print(f"Query: {query}")
    print(f"Results: {len(chunks)}")
    for i, chunk in enumerate(chunks, start=1):
        heading = " > ".join(chunk.heading_path) if chunk.heading_path else "Unknown section"
        snippet = " ".join(chunk.text.split())
        print(f"\n{i}. [{chunk.citation}; chunk {chunk.chunk_index}; score {chunk.similarity:.4f}]")
        print(f"   {chunk.report_dir}")
        print(f"   {heading}")
        print("   " + textwrap.shorten(snippet, width=420, placeholder=" ..."))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("--symbol", help="optional ticker filter, e.g. C38U.SI")
    parser.add_argument("--financial-year", type=int)
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--json", action="store_true", help="print JSON payload")
    parser.add_argument("--context-only", action="store_true", help="print citation-formatted context only")
    parser.add_argument("--prompt", action="store_true", help="print a ready-to-use RAG prompt")
    parser.add_argument("--max-chars-per-chunk", type=int, help="truncate context chunks for display")
    args = parser.parse_args()

    chunks = search_chunks(
        args.query,
        symbol=args.symbol,
        financial_year=args.financial_year,
        limit=args.limit,
    )

    if args.json:
        print(dumps_payload(args.query, chunks))
    elif args.context_only:
        print(format_context(chunks, max_chars_per_chunk=args.max_chars_per_chunk))
    elif args.prompt:
        prompt = build_rag_prompt(args.query, chunks)
        if args.max_chars_per_chunk:
            prompt = (
                "Answer the question using only the cited annual-report context below. "
                "Cite report symbol, FY, and page for every factual claim. If the context is insufficient, say what is missing.\n\n"
                f"Question: {args.query}\n\n"
                f"Context:\n{format_context(chunks, max_chars_per_chunk=args.max_chars_per_chunk)}"
            )
        print(prompt)
    else:
        print_human(args.query, chunks)


if __name__ == "__main__":
    main()
