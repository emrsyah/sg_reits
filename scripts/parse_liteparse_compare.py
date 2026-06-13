#!/usr/bin/env python3
"""Parse a couple of REIT annual-report PDFs with the open-source LiteParse
(local, no cloud) and compare output quality against the existing agentic
LlamaParse parses in parsed_reports/.

LiteParse: https://github.com/run-llama/liteparse  (pip install liteparse)
It is a local parser (PyMuPDF text extraction + optional Tesseract OCR) — no
LLM, no API key, no credits. This is the cheap/fast end of the tiering spectrum
from docs/extraction_strategy_research.md; this script lets you eyeball how much
table/structure fidelity you give up vs the agentic cloud tier.

Output (mirrors parse_sample.py's layout so locate.py / the skill work on it):
  parsed_reports_liteparse/<stem>/
    full.md      page-anchored markdown  (<!-- PAGE N --> separators)
    pages.jsonl  one JSON object per page
    meta.json    parser, page count, timing
  parsed_reports_liteparse/_compare.md   side-by-side metrics vs the agentic parse

Usage (run from anywhere; paths are resolved to the repo root):
  pip install liteparse        # + Tesseract on PATH if you want OCR on scans
  python scripts/parse_liteparse_compare.py                       # default 2 docs
  python scripts/parse_liteparse_compare.py 09_C38U... 28_M44U... # custom stems/files
"""
import json
import re
import sys
import time
from pathlib import Path

# repo root = parent of scripts/ (root-robust regardless of CWD)
ROOT = Path(__file__).resolve().parent.parent
IN_DIR = ROOT / "annual_reports"
AGENTIC_DIR = ROOT / "parsed_reports"          # existing agentic LlamaParse output
OUT_DIR = ROOT / "parsed_reports_liteparse"    # this run; kept separate, never clobbers

# Two docs that already have an agentic parse to compare against. Both are
# table-heavy (audited portfolio statement + financial review) — the case where
# a local parser is most likely to diverge from the agentic tier.
DEFAULT_DOCS = [
    "09_C38U.SI_CapitaLand-Integrated-Commercial-Trust_FY2025.pdf",
    "28_M44U.SI_Mapletree-Logistics-Trust_FY2025.pdf",
]

TABLE_ROW_RX = re.compile(r"^\s*\|.*\|\s*$", re.MULTILINE)  # markdown table rows
HTML_TABLE_RX = re.compile(r"<t[dr]\b", re.IGNORECASE)       # html-style table cells


def page_markdown(page) -> str:
    """Best-effort per-page markdown from a LiteParse page object.

    The docs pin page.page_num + page.text_items but don't fully pin the
    markdown attribute, so try the likely shapes in order and fall back to
    plain text. Printed attributes on the first page help confirm the real API.
    """
    for attr in ("markdown", "md"):
        v = getattr(page, attr, None)
        if isinstance(v, str) and v.strip():
            return v
    for meth in ("to_markdown", "as_markdown"):
        fn = getattr(page, meth, None)
        if callable(fn):
            try:
                v = fn()
                if isinstance(v, str) and v.strip():
                    return v
            except Exception:
                pass
    v = getattr(page, "text", None)
    if isinstance(v, str):
        return v
    items = getattr(page, "text_items", None) or []
    return "\n".join(getattr(i, "text", str(i)) for i in items)


def page_number(page, idx: int) -> int:
    for attr in ("page_num", "page_number", "number", "index"):
        v = getattr(page, attr, None)
        if isinstance(v, int):
            # some parsers are 0-indexed; normalize to 1-based for the marker
            return v + 1 if attr in ("index",) else v
    return idx + 1


def metrics(md: str) -> dict:
    return {
        "chars": len(md),
        "pipe_table_rows": len(TABLE_ROW_RX.findall(md)),
        "html_table_tags": len(HTML_TABLE_RX.findall(md)),
    }


def agentic_full_md(stem: str) -> str | None:
    p = AGENTIC_DIR / stem / "full.md"
    return p.read_text(encoding="utf-8") if p.exists() else None


def parse_one(fname: str) -> dict:
    from liteparse import LiteParse  # imported here so --help works without install

    src = IN_DIR / fname
    if not src.exists():
        print(f"! missing PDF: {src}", flush=True)
        return {"file": fname, "status": "missing_pdf"}
    stem = src.stem
    out = OUT_DIR / stem
    out.mkdir(parents=True, exist_ok=True)

    print(f"> liteparse: {fname} ({src.stat().st_size/1e6:.1f} MB) ...", flush=True)
    t0 = time.monotonic()
    # output_format='markdown' is a documented constructor option; ocr_enabled
    # defaults to True (handles scanned/image pages). Drop dpi/num_workers to taste.
    parser = LiteParse(output_format="markdown", quiet=True)
    result = parser.parse(str(src))
    dt = time.monotonic() - t0

    pages = list(getattr(result, "pages", []) or [])
    if pages:  # one-time API confirmation — what attributes does a page actually expose?
        print(f"  (page attrs: {sorted(a for a in dir(pages[0]) if not a.startswith('_'))})",
              flush=True)

    with open(out / "full.md", "w", encoding="utf-8") as f, \
         open(out / "pages.jsonl", "w", encoding="utf-8") as jf:
        if not pages:  # fall back to whole-doc text if no page split is exposed
            full = getattr(result, "markdown", None) or getattr(result, "text", "") or ""
            f.write(full)
            jf.write(json.dumps({"page": 1, "markdown": full}, ensure_ascii=False) + "\n")
            n_pages = 1
        else:
            for idx, page in enumerate(pages):
                num = page_number(page, idx)
                md = page_markdown(page)
                f.write(f"\n\n<!-- PAGE {num} -->\n\n{md}")
                jf.write(json.dumps({"page": num, "markdown": md}, ensure_ascii=False) + "\n")
            n_pages = len(pages)

    meta = {"file": fname, "parser": "liteparse", "pages": n_pages, "seconds": round(dt, 1)}
    with open(out / "meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    print(f"+ done: {fname} - {n_pages} pages in {dt:.0f}s -> {out.relative_to(ROOT)}",
          flush=True)

    lite_md = (out / "full.md").read_text(encoding="utf-8")
    row = {"file": fname, "status": "ok", **meta, "lite": metrics(lite_md)}
    ag = agentic_full_md(stem)
    if ag is not None:
        ag_pages = len(re.findall(r"<!-- PAGE \d+ -->", ag))
        row["agentic"] = {"pages": ag_pages, **metrics(ag)}
    else:
        print(f"  (no agentic parse at {AGENTIC_DIR/stem}/full.md to compare)", flush=True)
    return row


def write_compare(rows: list[dict]) -> None:
    lines = [
        "# LiteParse (local, open-source) vs agentic LlamaParse — quality compare",
        "",
        "Same PDFs, two parsers. `pipe_table_rows` + `html_table_tags` proxy how much",
        "tabular structure survived (the thing that matters for the audited portfolio /",
        "financial-review tables). `chars` is raw text volume. Eyeball the two `full.md`",
        "files side by side for the real verdict — these numbers only point you at where.",
        "",
        "| Doc | Parser | Pages | Chars | Pipe-table rows | HTML table tags | Seconds |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for r in rows:
        if r.get("status") != "ok":
            lines.append(f"| {r['file']} | — | _{r.get('status')}_ | | | | |")
            continue
        short = r["file"].replace(".pdf", "")
        lm, secs = r["lite"], r["seconds"]
        lines.append(f"| {short} | **liteparse** | {r['pages']} | {lm['chars']:,} | "
                     f"{lm['pipe_table_rows']:,} | {lm['html_table_tags']:,} | {secs} |")
        if "agentic" in r:
            am = r["agentic"]
            lines.append(f"| {short} | agentic | {am['pages']} | {am['chars']:,} | "
                         f"{am['pipe_table_rows']:,} | {am['html_table_tags']:,} | (cloud) |")
    lines += [
        "",
        "## How to read this",
        "- **Far fewer table rows on liteparse** = it flattened tables to plain text;",
        "  expect the audited portfolio statement / financial review to need OCR-table",
        "  recovery or the agentic tier (this is the hybrid-routing call from",
        "  `docs/extraction_strategy_research.md`).",
        "- **Similar chars but lower tables** = text is there, structure is lost.",
        "- **Much lower chars** = missed pages/columns (check scanned pages, OCR).",
        "",
        "Open both to compare a known-hard page (CICT portfolio statement ~p.109):",
        "```",
        "parsed_reports/09_C38U..._FY2025/full.md            # agentic",
        "parsed_reports_liteparse/09_C38U..._FY2025/full.md  # liteparse",
        "```",
    ]
    (OUT_DIR / "_compare.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"\n+ wrote {(OUT_DIR/'_compare.md').relative_to(ROOT)}", flush=True)


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    args = sys.argv[1:]
    docs = []
    for a in (args or DEFAULT_DOCS):
        docs.append(a if a.endswith(".pdf") else a + ".pdf")
    rows = [parse_one(d) for d in docs]
    write_compare(rows)
    ok = sum(1 for r in rows if r.get("status") == "ok")
    print(f"\nFinished: {ok}/{len(docs)} parsed. Compare table: {OUT_DIR/'_compare.md'}")
    sys.exit(0 if ok == len(docs) else 1)


if __name__ == "__main__":
    main()
