#!/usr/bin/env python3
"""parse_html.py - Datalab convert to HTML (or json) for the deterministic-adapter pilot.

HTML preserves multi-row headers, colspans and merged section cells that markdown pipe
tables flatten - so it is a better substrate for deterministic table parsing
(pandas.read_html / BeautifulSoup). Use a tight --page-range; Datalab is per-page paid.

Usage:
  python scripts/adapter/parse_html.py 09_C38U... --page-range 108-112
  python scripts/adapter/parse_html.py 09_C38U... --page-range 108-112 --format json

Output: extracted_adapter/<stem>/portfolio.html (or .json) + _meta.json
"""
import argparse
import inspect
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IN_DIR = ROOT / "annual_reports"
OUT_DIR = ROOT / "extracted_adapter"


def load_dotenv() -> None:
    env = ROOT / ".env"
    if not env.exists():
        return
    for line in env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def build_options(OptCls, **kw):
    accepted = set(inspect.signature(OptCls).parameters)
    known, extra = {}, {}
    for k, v in kw.items():
        if v is None or v == "":
            continue
        (known if k in accepted else extra)[k] = v
    if extra:
        known["additional_config"] = {**(known.get("additional_config") or {}), **extra}
    return OptCls(**known)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("doc")
    ap.add_argument("--page-range", default=None, help="0-based, e.g. 108-112")
    ap.add_argument("--format", default="html", choices=["html", "json"])
    ap.add_argument("--mode", default="balanced", choices=["fast", "balanced", "accurate"])
    args = ap.parse_args()

    load_dotenv()
    if not os.environ.get("DATALAB_API_KEY"):
        sys.exit("DATALAB_API_KEY not found in .env or environment.")
    from datalab_sdk import DatalabClient, ConvertOptions

    fname = args.doc if args.doc.endswith(".pdf") else args.doc + ".pdf"
    src = IN_DIR / fname
    if not src.exists():
        sys.exit(f"missing PDF: {src}")
    out = OUT_DIR / src.stem
    out.mkdir(parents=True, exist_ok=True)

    opts = build_options(
        ConvertOptions,
        output_format=args.format,
        mode=args.mode,
        paginate=True,
        add_block_ids=True,                 # block ids help map cells -> pages later
        disable_image_extraction=True,
        page_range=args.page_range,
    )
    print(f"> datalab convert[{args.mode}] format={args.format} "
          f"pages={args.page_range or 'all'} {fname} ...", flush=True)
    client = DatalabClient()
    result = client.convert(file_path=str(src), options=opts)
    if not getattr(result, "success", False):
        sys.exit(f"! failed: {getattr(result, 'error', 'unknown')}")

    body = result.html if args.format == "html" else (result.json or result.markdown)
    if body is None:
        # SDK may expose the html under a different attr across versions
        body = getattr(result, "output", None) or getattr(result, "content", None)
    ext = "html" if args.format == "html" else "json"
    fp = out / f"portfolio.{ext}"
    if isinstance(body, (dict, list)):
        fp.write_text(json.dumps(body, indent=2, ensure_ascii=False), encoding="utf-8")
    else:
        fp.write_text(str(body), encoding="utf-8")

    cost = getattr(result, "cost_breakdown", None)
    meta = {"file": fname, "format": args.format, "page_range": args.page_range,
            "pages": getattr(result, "page_count", None), "cost_breakdown": cost,
            "checkpoint_id": getattr(result, "checkpoint_id", None)}
    (out / "_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    c = (cost or {}).get("final_cost_cents")
    print(f"+ wrote {fp.relative_to(ROOT)} ({len(str(body)):,} chars)"
          f"{f'  ({c}c)' if c is not None else ''}", flush=True)


if __name__ == "__main__":
    main()
