#!/usr/bin/env python3
"""Parse REIT annual-report PDFs with Datalab (Marker/Surya cloud API).

Datalab: https://www.datalab.to  ·  SDK: https://github.com/datalab-to/sdk
Outputs mirror parse_sample.py so locate.py / the reit-extraction skill work on
the result unchanged, and so Datalab output sits next to the agentic LlamaParse
parses for a like-for-like quality comparison.

  parsed_reports_datalab/<stem>/
    full.md      page-anchored markdown  (<!-- PAGE N --> separators)
    pages.jsonl  one JSON object per page
    meta.json    parser, mode, pages, seconds, quality, cost, checkpoint_id
  parsed_reports_datalab/_compare.md   metrics vs the agentic parse (when present)

Defaults are the measured sweet spot for these documents (see the chat / research):
  mode=balanced (0.4c/page, table fidelity == accurate on the FY tables),
  + save_checkpoint (parse once, run extraction later without re-paying the parse),
  + token_efficient_markdown (leaner markdown -> cheaper downstream extraction),
  + image extraction off (we only need text/tables).

Auth: reads DATALAB_API_KEY from the repo-root .env (gitignored) or the env.

Usage (run from anywhere):
  pip install datalab-python-sdk
  python scripts/parse_datalab.py                                  # default 2 docs, balanced
  python scripts/parse_datalab.py 13_DCRU... --mode accurate
  python scripts/parse_datalab.py 12_DHLU... --use-llm --page-range 95-115  # hard tables
  python scripts/parse_datalab.py 09_C38U... --extras chart_understanding,table_row_bboxes

NOTE: Datalab is a paid per-page API. Use --page-range to validate cheaply first.
"""
import argparse
import inspect
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

PAGE_DELIM_RX = re.compile(r"\n*\{(\d+)\}-{6,}\n*")   # Marker paginate delimiter
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
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def build_options(ConvertOptions, **kw):
    """Construct ConvertOptions tolerantly: kwargs the SDK doesn't expose directly
    (e.g. the beta use_llm / format_lines) are routed into additional_config so the
    script keeps working across SDK versions instead of throwing TypeError."""
    accepted = set(inspect.signature(ConvertOptions).parameters)
    known, extra = {}, {}
    for k, v in kw.items():
        if v is None or v == "":
            continue
        (known if k in accepted else extra)[k] = v
    if extra:
        known["additional_config"] = {**(known.get("additional_config") or {}), **extra}
    return ConvertOptions(**known)


def split_pages(md: str) -> list[tuple[int, str]]:
    parts = PAGE_DELIM_RX.split(md)
    if len(parts) < 3:
        return [(1, md.strip())]
    pages: list[tuple[int, str]] = []
    if parts[0].strip():
        pages.append((1, parts[0].strip()))
    it = iter(parts[1:])
    for idx, body in zip(it, it):
        pages.append((int(idx) + 1, body.strip()))  # marker pages are 0-indexed
    return pages


def metrics(md: str) -> dict:
    return {"chars": len(md),
            "pipe_table_rows": len(TABLE_ROW_RX.findall(md)),
            "html_table_tags": len(HTML_TABLE_RX.findall(md))}


def agentic_full_md(stem: str) -> str | None:
    p = AGENTIC_DIR / stem / "full.md"
    return p.read_text(encoding="utf-8") if p.exists() else None


def parse_one(client, opts, mode_label: str, page_range: str | None, fname: str) -> dict:
    src = IN_DIR / fname
    if not src.exists():
        print(f"! missing PDF: {src}", flush=True)
        return {"file": fname, "status": "missing_pdf"}
    stem = src.stem
    out = OUT_DIR / stem
    out.mkdir(parents=True, exist_ok=True)

    rng = f" pages={page_range}" if page_range else ""
    print(f"> datalab[{mode_label}]:{rng} {fname} ({src.stat().st_size/1e6:.1f} MB) ...",
          flush=True)
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
        "file": fname, "parser": f"datalab:{mode_label}",
        "pages": result.page_count or len(pages), "pages_written": len(pages),
        "seconds": round(dt, 1),
        "parse_quality_score": getattr(result, "parse_quality_score", None),
        "runtime": getattr(result, "runtime", None),
        "cost_breakdown": getattr(result, "cost_breakdown", None),
        "checkpoint_id": getattr(result, "checkpoint_id", None),  # reuse for extraction
        "page_range": page_range,
    }
    (out / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    cost = (meta["cost_breakdown"] or {}).get("final_cost_cents")
    ckpt = f" ckpt={meta['checkpoint_id']}" if meta["checkpoint_id"] else ""
    print(f"+ done: {fname} - {len(pages)} pages in {dt:.0f}s"
          f"{f' ({cost}c)' if cost is not None else ''}{ckpt} -> {out.relative_to(ROOT)}",
          flush=True)

    row = {"file": fname, "status": "ok", **meta, "datalab_md": metrics(md)}
    if page_range is None:
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
        "# Datalab (Marker/Surya) vs agentic LlamaParse — quality compare", "",
        "`pipe_table_rows` + `html_table_tags` proxy surviving table structure;",
        "`chars` is raw text volume. Datalab emits clean markdown pipe tables, agentic",
        "emits HTML `<td>` tables — both are structured (unlike LiteParse's flattening).",
        "",
        "| Doc | Parser | Pages | Chars | Pipe rows | HTML cells | Cost | Seconds |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for r in full:
        short = r["file"].replace(".pdf", "")
        d, a = r["datalab_md"], r["agentic"]
        cost = (r.get("cost_breakdown") or {}).get("final_cost_cents", "—")
        lines.append(f"| {short} | **{r['parser']}** | {r['pages']} | {d['chars']:,} | "
                     f"{d['pipe_table_rows']:,} | {d['html_table_tags']:,} | {cost}c | "
                     f"{r['seconds']} |")
        lines.append(f"| {short} | agentic | {a['pages']} | {a['chars']:,} | "
                     f"{a['pipe_table_rows']:,} | {a['html_table_tags']:,} | — | (cloud) |")
    (OUT_DIR / "_compare.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"+ wrote {(OUT_DIR/'_compare.md').relative_to(ROOT)}", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser(description="Parse REIT PDFs with Datalab.")
    ap.add_argument("docs", nargs="*", help="PDF filenames/stems (default: 2 compare docs)")
    ap.add_argument("--mode", default="balanced", choices=["fast", "balanced", "accurate"],
                    help="default balanced — measured sweet spot for these docs")
    ap.add_argument("--page-range", default=None, help="0-based, e.g. '108-112' (cheap test)")
    ap.add_argument("--extras", default=None,
                    help="comma list: chart_understanding,table_row_bboxes,extract_links,...")
    ap.add_argument("--use-llm", action="store_true",
                    help="beta LLM pass for hard tables/forms (~2x cost) — use on hard docs")
    ap.add_argument("--no-checkpoint", action="store_true",
                    help="don't save a checkpoint (default: save, for cheap re-extraction)")
    ap.add_argument("--no-token-efficient", action="store_true",
                    help="emit standard markdown instead of token-efficient")
    ap.add_argument("--images", action="store_true", help="keep image extraction on")
    args = ap.parse_args()

    load_dotenv()
    if not os.environ.get("DATALAB_API_KEY"):
        sys.exit("DATALAB_API_KEY not found in .env or environment.")
    try:
        from datalab_sdk import DatalabClient, ConvertOptions
    except ImportError:
        sys.exit("datalab_sdk not installed. Try: pip install datalab-python-sdk")

    OUT_DIR.mkdir(exist_ok=True)
    opts = build_options(
        ConvertOptions,
        output_format="markdown",
        mode=args.mode,
        paginate=True,
        disable_image_extraction=not args.images,
        save_checkpoint=not args.no_checkpoint,
        token_efficient_markdown=not args.no_token_efficient,
        extras=args.extras,
        use_llm=True if args.use_llm else None,   # routed via additional_config if needed
        page_range=args.page_range,
    )
    docs = [(d if d.endswith(".pdf") else d + ".pdf") for d in (args.docs or DEFAULT_DOCS)]
    client = DatalabClient()
    rows = [parse_one(client, opts, args.mode, args.page_range, d) for d in docs]
    write_compare(rows)
    ok = sum(1 for r in rows if r.get("status") == "ok")
    print(f"\nFinished: {ok}/{len(docs)} parsed -> {OUT_DIR.relative_to(ROOT)}/")
    sys.exit(0 if ok == len(docs) else 1)


if __name__ == "__main__":
    main()
