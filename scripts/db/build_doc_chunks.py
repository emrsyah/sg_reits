#!/usr/bin/env python3
"""Build page-aware markdown chunks for Supabase pgvector.

This script does not call the embedding API. It parses
parsed_reports_datalab/<report>/full.md, creates deterministic chunks, and can
upsert them into sgx_reit_doc_chunk. Re-run safely after parser changes: if a
chunk hash changes, the existing embedding is cleared so embed_doc_chunks.py can
refresh it.

Usage:
  python scripts/db/build_doc_chunks.py --dry-run
  python scripts/db/build_doc_chunks.py --load
  python scripts/db/build_doc_chunks.py --report A17U.SI --load
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import re
import sys
from dataclasses import dataclass
from typing import Iterable

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import execute_values

ROOT = pathlib.Path(__file__).resolve().parents[2]
PARSED = ROOT / "parsed_reports_datalab"
MODEL = "voyage-4-large"
DIMENSION = 1024
TARGET_TOKENS = 1200
OVERLAP_TOKENS = 180
REQUEST_TOKEN_LIMIT = 120_000

PAGE_RE = re.compile(r"<!--\s*PAGE\s+(\d+)\s*-->")
REPORT_RE = re.compile(r"^\d+_([A-Z0-9]+\.SI)_.*_FY(\d{4})$")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
IMAGE_RE = re.compile(r"^\s*!\[[^\]]*]\([^)]+\)\s*$")
TABLE_SEP_RE = re.compile(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)+\|?\s*$")


@dataclass
class Block:
    text: str
    page: int
    char_start: int
    char_end: int
    heading_path: tuple[str, ...]
    tokens: int = 0


@dataclass
class Chunk:
    symbol: str
    financial_year: int
    report_dir: str
    source_path: str
    chunk_index: int
    page_start: int
    page_end: int
    char_start: int
    char_end: int
    heading_path: tuple[str, ...]
    chunk_text: str
    token_count: int
    chunk_hash: str


class TokenCounter:
    def __init__(self, model: str = MODEL):
        self.model = model
        self._cache: dict[str, int] = {}
        self._client = None

    def count(self, text: str) -> int:
        if not text:
            return 0
        cached = self._cache.get(text)
        if cached is not None:
            return cached
        if self._client is None:
            try:
                import voyageai
            except ImportError:
                self._client = False
            else:
                self._client = voyageai.Client(api_key=os.environ.get("VOYAGE_API_KEY", "dummy"))
        if self._client:
            try:
                count = int(self._client.count_tokens([text], model=self.model))
            except Exception:
                count = max(1, round(len(text) / 5))
        else:
            count = max(1, round(len(text) / 5))
        self._cache[text] = count
        return count


def pdf_key_for(symbol: str, fy: int) -> str | None:
    sym = symbol.split(".")[0]
    hits = sorted((ROOT / "annual_reports").glob(f"*_{sym}.SI_*_FY{fy}.pdf"))
    return hits[0].name if hits else None


def report_dirs(report_filter: str | None) -> list[pathlib.Path]:
    dirs = []
    for d in sorted(PARSED.iterdir()):
        if not d.is_dir() or not (d / "full.md").exists():
            continue
        m = REPORT_RE.match(d.name)
        if not m:
            continue
        symbol = m.group(1)
        if report_filter and report_filter not in {symbol, d.name}:
            continue
        dirs.append(d)
    return dirs


def normalize_heading(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"[*_`]+", "", text)
    return " ".join(text.strip().split())


def update_heading_path(path: list[str], line: str) -> tuple[str, ...] | None:
    m = HEADING_RE.match(line.strip())
    if not m:
        return None
    level = len(m.group(1))
    title = normalize_heading(m.group(2))
    if not title:
        return None
    del path[level - 1 :]
    while len(path) < level - 1:
        path.append("")
    path.append(title)
    return tuple(x for x in path if x)


def page_slices(text: str) -> Iterable[tuple[int, int, int, str]]:
    matches = list(PAGE_RE.finditer(text))
    for i, match in enumerate(matches):
        page = int(match.group(1))
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        yield page, start, end, text[start:end]


def line_spans(page_text: str, abs_start: int) -> list[tuple[str, int, int]]:
    spans = []
    offset = 0
    for line in page_text.splitlines(keepends=True):
        start = abs_start + offset
        offset += len(line)
        spans.append((line, start, abs_start + offset))
    return spans


def split_page_blocks(
    page: int,
    page_text: str,
    abs_start: int,
    heading_path: list[str],
    keep_image_markdown: bool,
) -> list[Block]:
    blocks: list[Block] = []
    spans = line_spans(page_text, abs_start)
    i = 0

    def add_block(lines: list[tuple[str, int, int]], heading: tuple[str, ...]) -> None:
        raw = "".join(line for line, _, _ in lines)
        text = raw.strip()
        if not text:
            return
        blocks.append(Block(text=text, page=page, char_start=lines[0][1], char_end=lines[-1][2], heading_path=heading))

    while i < len(spans):
        line, start, end = spans[i]
        stripped = line.strip()
        new_heading = update_heading_path(heading_path, stripped)
        heading = new_heading or tuple(x for x in heading_path if x)

        if not keep_image_markdown and IMAGE_RE.match(stripped):
            i += 1
            continue
        if not stripped:
            i += 1
            continue

        if "|" in stripped:
            table_lines = [spans[i]]
            i += 1
            while i < len(spans) and ("|" in spans[i][0].strip() or not spans[i][0].strip()):
                if spans[i][0].strip():
                    table_lines.append(spans[i])
                i += 1
            add_block(table_lines, heading)
            continue

        para = [spans[i]]
        i += 1
        while i < len(spans):
            nxt = spans[i][0].strip()
            if not nxt or "|" in nxt or HEADING_RE.match(nxt) or (not keep_image_markdown and IMAGE_RE.match(nxt)):
                break
            para.append(spans[i])
            i += 1
        add_block(para, heading)

    return blocks


def table_header(text: str) -> str:
    lines = text.splitlines()
    if len(lines) >= 2 and "|" in lines[0] and TABLE_SEP_RE.match(lines[1]):
        return "\n".join(lines[:2])
    return ""


def split_oversized_block(block: Block, counter: TokenCounter, target_tokens: int) -> list[Block]:
    if counter.count(block.text) <= target_tokens:
        block.tokens = counter.count(block.text)
        return [block]

    lines = block.text.splitlines()
    header = table_header(block.text)
    header_lines = header.splitlines() if header else []
    body_lines = lines[len(header_lines) :] if header_lines else lines
    if not header_lines and len(body_lines) == 1:
        body_lines = split_long_line(body_lines[0], counter, target_tokens)
    parts: list[Block] = []
    current: list[str] = []

    for line in body_lines:
        candidate_lines = header_lines + current + [line] if header_lines and current else current + [line]
        candidate = "\n".join(candidate_lines)
        if current and counter.count(candidate) > target_tokens:
            text = "\n".join((header_lines + current) if header_lines else current).strip()
            parts.append(Block(text=text, page=block.page, char_start=block.char_start, char_end=block.char_end, heading_path=block.heading_path, tokens=counter.count(text)))
            current = [line]
        else:
            current.append(line)

    if current:
        text = "\n".join((header_lines + current) if header_lines else current).strip()
        parts.append(Block(text=text, page=block.page, char_start=block.char_start, char_end=block.char_end, heading_path=block.heading_path, tokens=counter.count(text)))
    return parts


def split_long_line(line: str, counter: TokenCounter, target_tokens: int) -> list[str]:
    pieces = [p for p in re.split(r"(?<=[.!?;])\s+", line.strip()) if p]
    if len(pieces) <= 1:
        words = line.strip().split()
        pieces = []
        current: list[str] = []
        for word in words:
            candidate = " ".join(current + [word])
            if current and counter.count(candidate) > target_tokens:
                pieces.append(" ".join(current))
                current = [word]
            else:
                current.append(word)
        if current:
            pieces.append(" ".join(current))
        return pieces or [line]

    chunks: list[str] = []
    current: list[str] = []
    for piece in pieces:
        candidate = " ".join(current + [piece])
        if current and counter.count(candidate) > target_tokens:
            chunks.append(" ".join(current))
            current = [piece]
        else:
            current.append(piece)
    if current:
        chunks.append(" ".join(current))
    return chunks


def chunk_prefix(report_dir: str, pages: tuple[int, int], heading_path: tuple[str, ...]) -> str:
    heading = " > ".join(heading_path) if heading_path else "Unknown section"
    return f"Report: {report_dir}\nPages: {pages[0]}-{pages[1]}\nSection: {heading}\n\n"


def make_chunk(
    symbol: str,
    fy: int,
    report_dir: str,
    source_path: str,
    index: int,
    blocks: list[Block],
    counter: TokenCounter,
) -> Chunk:
    page_start = min(b.page for b in blocks)
    page_end = max(b.page for b in blocks)
    heading_path = blocks[0].heading_path
    body = "\n\n".join(b.text for b in blocks).strip()
    text = chunk_prefix(report_dir, (page_start, page_end), heading_path) + body
    digest = hashlib.sha256(
        json.dumps(
            {
                "model": MODEL,
                "dimension": DIMENSION,
                "symbol": symbol,
                "financial_year": fy,
                "report_dir": report_dir,
                "chunk_index": index,
                "text": text,
            },
            ensure_ascii=False,
            sort_keys=True,
        ).encode("utf-8")
    ).hexdigest()
    return Chunk(
        symbol=symbol,
        financial_year=fy,
        report_dir=report_dir,
        source_path=source_path,
        chunk_index=index,
        page_start=page_start,
        page_end=page_end,
        char_start=min(b.char_start for b in blocks),
        char_end=max(b.char_end for b in blocks),
        heading_path=heading_path,
        chunk_text=text,
        token_count=counter.count(text),
        chunk_hash=digest,
    )


def trailing_overlap(blocks: list[Block], overlap_tokens: int) -> list[Block]:
    total = 0
    kept: list[Block] = []
    for block in reversed(blocks):
        if not kept:
            kept.append(block)
            total += block.tokens
            continue
        if total >= overlap_tokens:
            break
        kept.append(block)
        total += block.tokens
    return list(reversed(kept))


def build_chunks_for_report(
    report_dir: pathlib.Path,
    counter: TokenCounter,
    target_tokens: int,
    overlap_tokens: int,
    keep_image_markdown: bool,
) -> list[Chunk]:
    m = REPORT_RE.match(report_dir.name)
    if not m:
        return []
    symbol, fy = m.group(1), int(m.group(2))
    md_path = report_dir / "full.md"
    text = md_path.read_text(encoding="utf-8", errors="ignore").replace("\x00", "")
    heading_path: list[str] = []
    chunks: list[Chunk] = []
    index = 0

    for page, abs_start, _abs_end, page_text in page_slices(text):
        blocks = split_page_blocks(page, page_text, abs_start, heading_path, keep_image_markdown)
        expanded: list[Block] = []
        for block in blocks:
            expanded.extend(split_oversized_block(block, counter, target_tokens))
        current: list[Block] = []
        current_tokens = 0
        for block in expanded:
            block.tokens = block.tokens or counter.count(block.text)
            if current and current_tokens + block.tokens > target_tokens:
                chunks.append(make_chunk(symbol, fy, report_dir.name, str(md_path.relative_to(ROOT)), index, current, counter))
                index += 1
                current = trailing_overlap(current, overlap_tokens)
                current_tokens = sum(b.tokens for b in current)
            current.append(block)
            current_tokens += block.tokens
        if current:
            chunks.append(make_chunk(symbol, fy, report_dir.name, str(md_path.relative_to(ROOT)), index, current, counter))
            index += 1
    return chunks


def connect():
    load_dotenv(ROOT / ".env")
    return psycopg2.connect(os.environ["SUPABASE_CONNECTION_STRING"])


def upsert_report(cur, symbol: str, fy: int) -> str:
    cur.execute(
        """insert into reit_report (symbol, financial_year, pdf_r2_key)
           values (%s,%s,%s)
           on conflict (symbol, financial_year)
           do update set pdf_r2_key = coalesce(reit_report.pdf_r2_key, excluded.pdf_r2_key)
           returning id""",
        (symbol, fy, pdf_key_for(symbol, fy)),
    )
    return cur.fetchone()[0]


def load_chunks(chunks_by_report: dict[str, list[Chunk]], reset_report: bool) -> None:
    conn = connect()
    conn.autocommit = False
    try:
        with conn.cursor() as cur:
            for report_dir, chunks in chunks_by_report.items():
                if not chunks:
                    continue
                symbol = chunks[0].symbol
                fy = chunks[0].financial_year
                report_id = upsert_report(cur, symbol, fy)
                if reset_report:
                    cur.execute("delete from sgx_reit_doc_chunk where report_dir=%s", (report_dir,))
                vals = [
                    (
                        report_id,
                        c.symbol,
                        c.financial_year,
                        c.report_dir,
                        c.source_path,
                        c.chunk_index,
                        c.page_start,
                        c.page_end,
                        c.char_start,
                        c.char_end,
                        list(c.heading_path),
                        c.chunk_text,
                        c.token_count,
                        c.chunk_hash,
                        MODEL,
                        DIMENSION,
                    )
                    for c in chunks
                ]
                execute_values(
                    cur,
                    """insert into sgx_reit_doc_chunk
                       (report_id, symbol, financial_year, report_dir, source_path, chunk_index,
                        page_start, page_end, char_start, char_end, heading_path, chunk_text,
                        token_count, chunk_hash, embedding_model, embedding_dimension)
                       values %s
                       on conflict (report_dir, chunk_index) do update set
                         report_id=excluded.report_id,
                         symbol=excluded.symbol,
                         financial_year=excluded.financial_year,
                         source_path=excluded.source_path,
                         page_start=excluded.page_start,
                         page_end=excluded.page_end,
                         char_start=excluded.char_start,
                         char_end=excluded.char_end,
                         heading_path=excluded.heading_path,
                         chunk_text=excluded.chunk_text,
                         token_count=excluded.token_count,
                         chunk_hash=excluded.chunk_hash,
                         embedding_model=excluded.embedding_model,
                         embedding_dimension=excluded.embedding_dimension,
                         embedding=case
                           when sgx_reit_doc_chunk.chunk_hash <> excluded.chunk_hash
                             or sgx_reit_doc_chunk.embedding_model <> excluded.embedding_model
                             or sgx_reit_doc_chunk.embedding_dimension <> excluded.embedding_dimension
                           then null else sgx_reit_doc_chunk.embedding end,
                         embedding_tokens=case
                           when sgx_reit_doc_chunk.chunk_hash <> excluded.chunk_hash then null
                           else sgx_reit_doc_chunk.embedding_tokens end,
                         embedded_at=case
                           when sgx_reit_doc_chunk.chunk_hash <> excluded.chunk_hash then null
                           else sgx_reit_doc_chunk.embedded_at end,
                         updated_at=now()""",
                    vals,
                )
                cur.execute(
                    "delete from sgx_reit_doc_chunk where report_dir=%s and chunk_index >= %s",
                    (report_dir, len(chunks)),
                )
                print(f"loaded {report_dir}: {len(chunks)} chunks")
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", help="report dir name or symbol, e.g. A17U.SI")
    parser.add_argument("--target-tokens", type=int, default=TARGET_TOKENS)
    parser.add_argument("--overlap-tokens", type=int, default=OVERLAP_TOKENS)
    parser.add_argument("--dry-run", action="store_true", help="default behavior; build chunks without loading")
    parser.add_argument("--load", action="store_true", help="upsert chunks into Supabase")
    parser.add_argument("--reset-report", action="store_true", help="delete existing chunks for each loaded report before insert")
    parser.add_argument("--keep-image-markdown", action="store_true", help="retain ![](...jpg) markdown lines")
    parser.add_argument("--json", action="store_true", help="print machine-readable summary")
    args = parser.parse_args()

    if args.overlap_tokens >= args.target_tokens:
        sys.exit("--overlap-tokens must be smaller than --target-tokens")

    counter = TokenCounter()
    chunks_by_report: dict[str, list[Chunk]] = {}
    summary = []
    for report_dir in report_dirs(args.report):
        chunks = build_chunks_for_report(
            report_dir,
            counter,
            args.target_tokens,
            args.overlap_tokens,
            args.keep_image_markdown,
        )
        chunks_by_report[report_dir.name] = chunks
        tokens = sum(c.token_count for c in chunks)
        summary.append(
            {
                "report": report_dir.name,
                "chunks": len(chunks),
                "tokens": tokens,
                "max_chunk_tokens": max((c.token_count for c in chunks), default=0),
            }
        )

    totals = {
        "reports": len(summary),
        "chunks": sum(s["chunks"] for s in summary),
        "tokens": sum(s["tokens"] for s in summary),
        "target_tokens": args.target_tokens,
        "overlap_tokens": args.overlap_tokens,
    }
    if args.json:
        print(json.dumps({"totals": totals, "reports": summary}, indent=2))
    else:
        print(
            f"built {totals['chunks']} chunks across {totals['reports']} reports "
            f"({totals['tokens']:,} estimated Voyage tokens)"
        )
        for row in sorted(summary, key=lambda r: r["chunks"], reverse=True)[:10]:
            print(f"  {row['report']}: chunks={row['chunks']} tokens={row['tokens']:,} max={row['max_chunk_tokens']}")

    if args.load:
        load_chunks(chunks_by_report, reset_report=args.reset_report)


if __name__ == "__main__":
    main()
