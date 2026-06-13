#!/usr/bin/env python3
"""Parse REIT annual-report PDFs with Datalab (Marker/Surya cloud API).

Datalab: https://www.datalab.to  ·  SDK: https://github.com/datalab-to/sdk
Outputs mirror parse_sample.py so locate.py / the reit-extraction skill work on
the result unchanged, and so Datalab output sits next to the agentic LlamaParse
parses for a like-for-like quality comparison.

  parsed_reports_datalab/<stem>/
    full.md      page-anchored markdown  (<!-- PAGE N --> separators)
    pages.jsonl  one JSON object per page
    meta.json    parser, mode, pages, seconds, parse_quality_score, cost
  parsed_reports_datalab/_compare.md   metrics vs the agentic parse (when present)

Auth: reads DATALAB_API_KEY from the repo-root .env (gitignored) or the env.

Usage (run from anywhere):
  pip install datalab-python-sdk          # see install note in the README/below
  python scripts/parse_datalab.py                              # default 2 docs, mode=accurate
  python scripts/parse_datalab.py 09_C38U... 28_M44U...        # specific stems/files
  python scripts/parse_datalab.py 09_C38U... --page-range 108-112   # cheap smoke test
  python scripts/parse_datalab.py --mode balanced 13_DCRU...   # fast | balanced | accurate

NOTE: Datalab is a paid, per-page API. Use --page-range first to validate on a
few pages before spending credits on full ~200-page reports.
"""
import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # repo root (script lives in scripts/)
IN_DIR = ROOT / "annual_reports"
AGENTIC_DIR = ROOT / "parsed_reports"            # existing agentic LlamaParse output
OUT_DIR = ROOT / "parsed_reports_datalab"

DEFAULT_DOCS = [
    "09_C38U.SI_CapitaLand-Integrated-Commercial-Trust_FY2025.pdf",
    "28_M44U.SI_Mapletree-Logistics-Trust_FY2025.pdf",
]

# Marker's paginate delimiter is a line like "{0}------------------------------".
PAGE_DELIM_RX = re.compile(r"\n*\{(\d+)\}-{6,}\n*")
TABLE_ROW_RX = re.compile(r"^\s*\|.*\|\s*$", re.MULTILINE)
HTML_TABLE_RX = re.compile(r"<t[dr]\b", re.IGNORECASE)


def load_dotenv() -> None:
    """Minimal .env loader (no python-dotenv dependency). Existing env wins."""
    env = ROOT / ".env"
    if not env.exists():
        return
    for line in env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k, v = k.strip(), v.strip().strip('"').strip("'")
        os.environ.setdefault(k, v)


def split_pages(md: str) -> list[tuple[int, str]]:
    """Split paginated Datalab markdown into (page_number, markdown) pairs.

    Returns 1-based page numbers. Falls back to a single page if no delimiter
    is found (so the parser still produces usable output if the format shifts).
    """
    parts = PAGE_DELIM_RX.split(md)
    if len(parts) < 3:  # no delimiters detected
        return [(1, md.strip())]
    # parts = [pre, idx0, body0, idx1, body1, ...]; 'pre' is usually empty
    pages: list[tuple[int, str]] = []
    pre = parts[0].strip()
    if pre:
        pages.append((1, pre))
    it = iter(parts[1:])
    for idx, body in zip(it, it):
        pages.append((int(idx) + 1, body.strip()))  # marker pages are 0-indexed
    return pages


def metrics(md: str) -> dict:
    return {
        "chars": len(md),
        "pipe_table_rows": len(TABLE_ROW_RX.findall(md)),
        "html_table_tags": len(HTML_TABLE_RX.findall(md)),
    }


def agentic_full_md(stem: str) -> str | None:
    p = AGENTIC_DIR / stem / "full.md"
    return p.read_text(encoding="utf-8") if p.exists() else None


def parse_one(client, ConvertOptions, fname: str, mode: str,
              page_range: str | None) -> dict:
    src = IN_DIR / fname
    if not src.exists():
        print(f"! missing PDF: {src}", flush=True)
        return {"file": fname, "status": "missing_pdf"}
    stem = src.stem
    out = OUT_DIR / stem
    out.mkdir(parents=True, exist_ok=True)

    opts = ConvertOptions(
        output_format="markdown",
        mode=mode,                      # fast | balanced | accurate
        paginate=True,                  # page delimiters -> per-page split
        disable_image_extraction=True,  # text/table fidelity only; no base64 dumps
        **({"page_range": page_range} if page_range else {}),
    )
    rng = f" pages={page_range}" if page_range else ""
    print(f"> datalab[{mode}]:{rng} {fname} ({src.stat().st_size/1e6:.1f} MB) ...", flush=True)
    t0 = time.monotonic()
    try:
        result = client.convert(file_path=str(src), options=opts)
    except Exception as e:
        print(f"! error: {fname} - {type(e).__name__}: {e}", flush=True)
        return {"file": fname, "status": "error", "error": str(e)}
    dt = time.monotonic() - t0

    if not getattr(result, "success", False):
        print(f"! failed: {fname} - {getattr(result, 'error', 'unknown')}", flush=True)
        return {"file": fname, "status": "failed", "error": getattr(result, "error", None)}

    md = result.markdown or ""
    pages = split_pages(md)
    with open(out / "full.md", "w", encoding="utf-8") as f, \
         open(out / "pages.jsonl", "w", encoding="utf-8") as jf:
        for num, body in pages:
            f.write(f"\n\n<!-- PAGE {num} -->\n\n{body}")
            jf.write(json.dumps({"page": num, "markdown": body}, ensure_ascii=False) + "\n")

    meta = {
        "file": fname,
        "parser": f"datalab:{mode}",
        "pages": result.page_count or len(pages),
        "pages_written": len(pages),
        "seconds": round(dt, 1),
        "parse_quality_score": getattr(result, "parse_quality_score", None),
        "runtime": getattr(result, "runtime", None),
        "cost_breakdown": getattr(result, "cost_breakdown", None),
        "page_range": page_range,
    }
    with open(out / "meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    q = meta["parse_quality_score"]
    print(f"+ done: {fname} - {len(pages)} pages in {dt:.0f}s"
          f"{f' (quality {q})' if q is not None else ''} -> {out.relative_to(ROOT)}",
          flush=True)

    row = {"file": fname, "status": "ok", **meta, "datalab_md": metrics(md)}
    if page_range is None:  # only compare full parses against the full agentic parse
        ag = agentic_full_md(stem)
        if ag is not None:
            row["agentic"] = {"pages": len(re.findall(r"<!-- PAGE \d+ -->", ag)),
                              **metrics(ag)}
    return row


def write_compare(rows: list[dict]) -> None:
    full = [r for r in rows if r.get("status") == "ok" and "agentic" in r]
    if not full:
        return
    lines = [
        "# Datalab (Marker/Surya) vs agentic LlamaParse — quality compare",
        "",
        "Same PDFs, two cloud parsers. `pipe_table_rows` + `html_table_tags` proxy how",
        "much tabular structure survived (audited portfolio / financial-review tables);",
        "`chars` is raw text volume. Datalab also returns a `parse_quality_score`.",
        "",
        "| Doc | Parser | Pages | Chars | Pipe rows | HTML cells | Quality | Seconds |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for r in full:
        short = r["file"].replace(".pdf", "")
        d, a = r["datalab_md"], r["agentic"]
        q = r.get("parse_quality_score")
        lines.append(f"| {short} | **datalab:{r['parser'].split(':')[1]}** | {r['pages']} | "
                     f"{d['chars']:,} | {d['pipe_table_rows']:,} | {d['html_table_tags']:,} | "
                     f"{q if q is not None else '—'} | {r['seconds']} |")
        lines.append(f"| {short} | agentic | {a['pages']} | {a['chars']:,} | "
                     f"{a['pipe_table_rows']:,} | {a['html_table_tags']:,} | — | (cloud) |")
    lines += [
        "",
        "Open the same hard page in both to judge table fidelity directly:",
        "```",
        "parsed_reports/09_C38U..._FY2025/full.md            # agentic",
        "parsed_reports_datalab/09_C38U..._FY2025/full.md    # datalab",
        "```",
    ]
    (OUT_DIR / "_compare.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"+ wrote {(OUT_DIR/'_compare.md').relative_to(ROOT)}", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser(description="Parse REIT PDFs with Datalab.")
    ap.add_argument("docs", nargs="*", help="PDF filenames/stems (default: 2 compare docs)")
    ap.add_argument("--mode", default="accurate", choices=["fast", "balanced", "accurate"])
    ap.add_argument("--page-range", default=None,
                    help="0-based range, e.g. '108-112' — cheap smoke test before full runs")
    args = ap.parse_args()

    load_dotenv()
    if not os.environ.get("DATALAB_API_KEY"):
        sys.exit("DATALAB_API_KEY not found in .env or environment.")
    try:
        from datalab_sdk import DatalabClient, ConvertOptions
    except ImportError:
        sys.exit("datalab_sdk not installed. Try: pip install datalab-python-sdk")

    OUT_DIR.mkdir(exist_ok=True)
    docs = [(d if d.endswith(".pdf") else d + ".pdf") for d in (args.docs or DEFAULT_DOCS)]
    client = DatalabClient()  # reads DATALAB_API_KEY from env
    rows = [parse_one(client, ConvertOptions, d, args.mode, args.page_range) for d in docs]
    write_compare(rows)
    ok = sum(1 for r in rows if r.get("status") == "ok")
    print(f"\nFinished: {ok}/{len(docs)} parsed -> {OUT_DIR.relative_to(ROOT)}/")
    sys.exit(0 if ok == len(docs) else 1)


if __name__ == "__main__":
    main()
