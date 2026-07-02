"""Reusable RAG helpers for SGX REIT annual-report chunks.

The helpers assume `sgx_reit_doc_chunk` has already been loaded and embedded
with `scripts/db/build_doc_chunks.py` + `scripts/db/embed_doc_chunks.py`.
"""
from __future__ import annotations

import json
import os
import pathlib
from dataclasses import asdict, dataclass
from typing import Any

import psycopg2
from dotenv import load_dotenv

ROOT = pathlib.Path(__file__).resolve().parents[2]
MODEL = "voyage-4-large"
QUERY_MODEL = "voyage-4"
DIMENSION = 1024


@dataclass
class RagChunk:
    symbol: str
    financial_year: int
    report_dir: str
    page_start: int
    page_end: int
    chunk_index: int
    heading_path: list[str]
    similarity: float
    text: str

    @property
    def citation(self) -> str:
        page = f"p{self.page_start}" if self.page_start == self.page_end else f"p{self.page_start}-{self.page_end}"
        return f"{self.symbol} FY{self.financial_year} {page}"

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["citation"] = self.citation
        return data


def load_env() -> None:
    load_dotenv(ROOT / ".env")


def vector_literal(vec: list[float]) -> str:
    return "[" + ",".join(f"{x:.9g}" for x in vec) + "]"


def embed_query(query: str, model: str = QUERY_MODEL, dimension: int = DIMENSION) -> list[float]:
    import voyageai

    load_env()
    client = voyageai.Client()
    return client.embed(
        [query],
        model=model,
        input_type="query",
        output_dimension=dimension,
    ).embeddings[0]


def search_chunks(
    query: str,
    *,
    symbol: str | None = None,
    financial_year: int | None = None,
    limit: int = 8,
    query_embedding: list[float] | None = None,
) -> list[RagChunk]:
    load_env()
    embedding = query_embedding if query_embedding is not None else embed_query(query)
    conn = psycopg2.connect(os.environ["SUPABASE_CONNECTION_STRING"])
    try:
        with conn.cursor() as cur:
            cur.execute(
                """select symbol, financial_year, report_dir, page_start, page_end,
                          chunk_index, heading_path, similarity, chunk_text
                   from match_sgx_reit_doc_chunks(%s::vector, %s, %s, %s)""",
                (vector_literal(embedding), limit, symbol, financial_year),
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    return [
        RagChunk(
            symbol=row[0],
            financial_year=row[1],
            report_dir=row[2],
            page_start=row[3],
            page_end=row[4],
            chunk_index=row[5],
            heading_path=list(row[6] or []),
            similarity=float(row[7]),
            text=row[8],
        )
        for row in rows
    ]


def format_context(chunks: list[RagChunk], *, max_chars_per_chunk: int | None = None) -> str:
    blocks = []
    for chunk in chunks:
        heading = " > ".join(chunk.heading_path) if chunk.heading_path else "Unknown section"
        text = chunk.text.strip()
        if max_chars_per_chunk and len(text) > max_chars_per_chunk:
            text = text[: max_chars_per_chunk - 3].rstrip() + "..."
        blocks.append(
            f"[{chunk.citation}; chunk {chunk.chunk_index}; score {chunk.similarity:.4f}]\n"
            f"Section: {heading}\n"
            f"{text}"
        )
    return "\n\n---\n\n".join(blocks)


def build_rag_prompt(query: str, chunks: list[RagChunk]) -> str:
    context = format_context(chunks)
    return (
        "Answer the question using only the cited annual-report context below. "
        "Cite report symbol, FY, and page for every factual claim. If the context is insufficient, say what is missing.\n\n"
        f"Question: {query}\n\n"
        f"Context:\n{context}"
    )


def result_payload(query: str, chunks: list[RagChunk]) -> dict[str, Any]:
    return {
        "query": query,
        "results": [chunk.to_dict() for chunk in chunks],
        "context": format_context(chunks),
        "rag_prompt": build_rag_prompt(query, chunks),
    }


def dumps_payload(query: str, chunks: list[RagChunk]) -> str:
    return json.dumps(result_payload(query, chunks), ensure_ascii=False, indent=2)
