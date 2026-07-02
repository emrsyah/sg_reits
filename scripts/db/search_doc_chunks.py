#!/usr/bin/env python3
"""Search embedded annual-report chunks with Voyage query embeddings.

Usage:
  python scripts/db/search_doc_chunks.py "portfolio occupancy"
  python scripts/db/search_doc_chunks.py "debt maturity" --symbol C38U.SI --limit 5
"""
from __future__ import annotations

import argparse
import os
import pathlib
import textwrap

import psycopg2
from dotenv import load_dotenv

ROOT = pathlib.Path(__file__).resolve().parents[2]
MODEL = "voyage-4-large"
DIMENSION = 1024


def vector_literal(vec: list[float]) -> str:
    return "[" + ",".join(f"{x:.9g}" for x in vec) + "]"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("--symbol", help="optional ticker filter, e.g. C38U.SI")
    parser.add_argument("--financial-year", type=int)
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args()

    load_dotenv(ROOT / ".env")

    import voyageai

    vo = voyageai.Client()
    emb = vo.embed(
        [args.query],
        model=MODEL,
        input_type="query",
        output_dimension=DIMENSION,
    ).embeddings[0]

    conn = psycopg2.connect(os.environ["SUPABASE_CONNECTION_STRING"])
    try:
        with conn.cursor() as cur:
            cur.execute(
                """select symbol, financial_year, report_dir, page_start, page_end,
                          chunk_index, heading_path, similarity, chunk_text
                   from match_sgx_reit_doc_chunks(%s::vector, %s, %s, %s)""",
                (vector_literal(emb), args.limit, args.symbol, args.financial_year),
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    for i, row in enumerate(rows, start=1):
        symbol, fy, report_dir, page_start, page_end, chunk_index, heading_path, similarity, text = row
        heading = " > ".join(heading_path or [])
        snippet = " ".join(text.split())
        print(f"{i}. {symbol} FY{fy} p{page_start}-{page_end} chunk={chunk_index} score={similarity:.4f}")
        print(f"   {report_dir}")
        if heading:
            print(f"   {heading}")
        print("   " + textwrap.shorten(snippet, width=360, placeholder=" ..."))


if __name__ == "__main__":
    main()
