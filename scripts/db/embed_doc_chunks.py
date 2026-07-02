#!/usr/bin/env python3
"""Embed sgx_reit_doc_chunk rows with Voyage and store pgvector vectors.

The runner is resumable: it selects rows where embedding is null for the target
model/dimension, batches under Voyage request limits, and updates only those rows.

Usage:
  python scripts/db/embed_doc_chunks.py --dry-run
  python scripts/db/embed_doc_chunks.py --limit 500
  python scripts/db/embed_doc_chunks.py --report A17U.SI
"""
from __future__ import annotations

import argparse
import os
import pathlib
import sys
from dataclasses import dataclass

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import execute_values

ROOT = pathlib.Path(__file__).resolve().parents[2]
MODEL = "voyage-4-large"
DIMENSION = 1024
MAX_INPUTS = 1000
MAX_BATCH_TOKENS = 115_000


@dataclass
class PendingChunk:
    id: str
    report_dir: str
    chunk_index: int
    token_count: int
    chunk_text: str


def connect():
    load_dotenv(ROOT / ".env")
    return psycopg2.connect(os.environ["SUPABASE_CONNECTION_STRING"])


def fetch_pending(conn, report: str | None, limit: int | None, include_text: bool) -> list[PendingChunk]:
    where = ["embedding is null", "embedding_model=%s", "embedding_dimension=%s"]
    params: list[object] = [MODEL, DIMENSION]
    if report:
        where.append("(symbol=%s or report_dir=%s)")
        params.extend([report, report])
    text_expr = "chunk_text" if include_text else "''::text as chunk_text"
    sql = f"""
        select id::text, report_dir, chunk_index, token_count, {text_expr}
        from sgx_reit_doc_chunk
        where {' and '.join(where)}
        order by report_dir, chunk_index
    """
    if limit is not None:
        sql += " limit %s"
        params.append(limit)
    with conn.cursor() as cur:
        cur.execute(sql, params)
        return [PendingChunk(*row) for row in cur.fetchall()]


def make_batches(rows: list[PendingChunk], max_inputs: int, max_tokens: int) -> list[list[PendingChunk]]:
    batches: list[list[PendingChunk]] = []
    current: list[PendingChunk] = []
    current_tokens = 0
    for row in rows:
        would_exceed_inputs = len(current) >= max_inputs
        would_exceed_tokens = current and current_tokens + row.token_count > max_tokens
        if would_exceed_inputs or would_exceed_tokens:
            batches.append(current)
            current = []
            current_tokens = 0
        current.append(row)
        current_tokens += row.token_count
    if current:
        batches.append(current)
    return batches


def vector_literal(vec: list[float]) -> str:
    return "[" + ",".join(f"{x:.9g}" for x in vec) + "]"


def update_embeddings(conn, batch: list[PendingChunk], embeddings: list[list[float]]) -> None:
    vals = [
        (row.id, vector_literal(embedding), row.token_count)
        for row, embedding in zip(batch, embeddings, strict=True)
    ]
    with conn.cursor() as cur:
        execute_values(
            cur,
            """update sgx_reit_doc_chunk as c set
                 embedding = v.embedding::vector,
                 embedding_tokens = v.embedding_tokens,
                 embedded_at = now(),
                 updated_at = now()
               from (values %s) as v(id, embedding, embedding_tokens)
               where c.id = v.id::uuid""",
            vals,
        )


def embed_batch(client, batch: list[PendingChunk]):
    texts = [row.chunk_text for row in batch]
    return client.embed(
        texts,
        model=MODEL,
        input_type="document",
        output_dimension=DIMENSION,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", help="symbol or report_dir to embed")
    parser.add_argument("--limit", type=int, help="maximum pending chunks to process")
    parser.add_argument("--dry-run", action="store_true", help="show pending batches without calling Voyage")
    parser.add_argument("--batch-token-limit", type=int, default=MAX_BATCH_TOKENS)
    parser.add_argument("--batch-size", type=int, default=MAX_INPUTS)
    args = parser.parse_args()

    if args.batch_size > MAX_INPUTS:
        sys.exit("--batch-size cannot exceed Voyage's 1000-input request limit")

    conn = connect()
    conn.autocommit = False
    try:
        pending = fetch_pending(conn, args.report, args.limit, include_text=not args.dry_run)
        batches = make_batches(pending, args.batch_size, args.batch_token_limit)
        print(
            f"pending={len(pending)} batches={len(batches)} "
            f"tokens={sum(r.token_count for r in pending):,}"
        )
        for i, batch in enumerate(batches[:10], start=1):
            print(
                f"  batch {i}: chunks={len(batch)} tokens={sum(r.token_count for r in batch):,} "
                f"{batch[0].report_dir}#{batch[0].chunk_index}..{batch[-1].report_dir}#{batch[-1].chunk_index}"
            )
        if args.dry_run or not pending:
            conn.rollback()
            return

        import voyageai

        client = voyageai.Client()
        total_api_tokens = 0
        for i, batch in enumerate(batches, start=1):
            result = embed_batch(client, batch)
            update_embeddings(conn, batch, result.embeddings)
            conn.commit()
            total_api_tokens += int(getattr(result, "total_tokens", 0) or 0)
            print(
                f"embedded batch {i}/{len(batches)}: chunks={len(batch)} "
                f"request_tokens={getattr(result, 'total_tokens', 'unknown')}"
            )
        print(f"done. api_total_tokens={total_api_tokens:,}")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
