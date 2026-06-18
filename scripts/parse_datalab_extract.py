#!/usr/bin/env python3
"""Structured extraction with Datalab's /extract, driven by schema/models.py.

Datalab extracts straight into a schema: client.extract(options=ExtractOptions(
page_schema=<json schema>)) returns ConversionResult.extraction_schema_json.
This script feeds our Pydantic 6-table models (schema/models.py) as that schema,
so Datalab becomes a SECOND extraction engine to A/B against the Claude-agent
pilot in extracted/.

ExtractOptions also takes checkpoint_id, so the efficient flow is:
  1. parse once:   python scripts/parse_datalab.py 09_C38U...   (saves a checkpoint)
  2. extract many: python scripts/parse_datalab_extract.py 09_C38U... --section properties \
                       --checkpoint-id <id-from-parse-meta>     (no re-parse cost)

Where it fits (hybrid strategy): use this for clean, mechanical sections
(properties, top_tenants, trade_mix, profile); keep the Claude agent for the
judgment-heavy parts (dual-basis valuations, combined property lines, JV
reconciliation, distributable-income layering). This is a comparison harness.

Output (mirrors the agent's extracted/ filenames so you can diff directly):
  extracted_datalab/<stem>/<section>.json   the extracted records
  extracted_datalab/<stem>/_meta.json       cost / mode / page_range / checkpoint

Usage:
  python scripts/parse_datalab_extract.py 09_C38U... --section properties --page-range 108-110
  python scripts/parse_datalab_extract.py 09_C38U... --section trade_mix  --page-range 33-35
  python scripts/parse_datalab_extract.py 09_C38U... --section all        # whole doc (costly)
"""
import argparse
import inspect
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IN_DIR = ROOT / "annual_reports"
AGENT_DIR = ROOT / "extracted"                 # Claude-agent pilot output (A/B target)
OUT_DIR = ROOT / "extracted_datalab"
sys.path.insert(0, str(ROOT / "schema"))       # import models.py without packaging


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
    """Construct an options dataclass tolerantly across SDK versions: pass accepted
    kwargs; route the rest to additional_config if the class has one, else drop
    with a note (e.g. ExtractOptions has no additional_config)."""
    accepted = set(inspect.signature(OptCls).parameters)
    known, extra, dropped = {}, {}, []
    for k, v in kw.items():
        if v is None or v == "":
            continue
        if k in accepted:
            known[k] = v
        elif "additional_config" in accepted:
            extra[k] = v
        else:
            dropped.append(k)
    if extra:
        known["additional_config"] = {**(known.get("additional_config") or {}), **extra}
    if dropped:
        print(f"  (note: {OptCls.__name__} ignores {dropped})", flush=True)
    return OptCls(**known)


def page_schema_for(section: str):
    """Build (json_schema, list_key, agent_filename) for a section."""
    from pydantic import create_model
    import models

    model, is_list, agent_file = models.SECTIONS[section]
    if section == "all":
        return model.model_json_schema(), None, agent_file
    if is_list:
        wrapper = create_model("Extract", **{section: (list[model], ...)})
        return wrapper.model_json_schema(), section, agent_file
    return model.model_json_schema(), None, agent_file


def agent_dir_for(stem: str) -> Path | None:
    m = re.search(r"_([A-Za-z0-9]+\.SI)_.*_(FY\d{4})$", stem)
    if not m:
        return None
    d = AGENT_DIR / f"{m.group(1)}_{m.group(2)}"
    return d if d.exists() else None


def main() -> None:
    ap = argparse.ArgumentParser(description="Datalab page_schema extraction A/B.")
    ap.add_argument("doc", help="PDF filename/stem")
    ap.add_argument("--section", default="properties",
                    help="profile | performance | properties | top_tenants | "
                         "trade_mix | financial | all")
    ap.add_argument("--page-range", default=None, help="0-based, e.g. '108-110'")
    ap.add_argument("--mode", default="balanced", choices=["fast", "balanced", "accurate"])
    ap.add_argument("--checkpoint-id", default=None,
                    help="extract against a saved parse checkpoint (no re-parse cost)")
    args = ap.parse_args()

    load_dotenv()
    if not os.environ.get("DATALAB_API_KEY"):
        sys.exit("DATALAB_API_KEY not found in .env or environment.")
    import models
    if args.section not in models.SECTIONS:
        sys.exit(f"--section must be one of: {', '.join(models.SECTIONS)}")
    try:
        from datalab_sdk import DatalabClient, ExtractOptions
    except ImportError:
        sys.exit("datalab_sdk not installed. Try: pip install datalab-python-sdk")

    fname = args.doc if args.doc.endswith(".pdf") else args.doc + ".pdf"
    src = IN_DIR / fname
    if not src.exists() and not args.checkpoint_id:
        sys.exit(f"missing PDF: {src}")
    stem = src.stem
    out = OUT_DIR / stem
    out.mkdir(parents=True, exist_ok=True)

    schema, list_key, agent_file = page_schema_for(args.section)
    opts = build_options(
        ExtractOptions,
        page_schema=schema,
        mode=args.mode,
        page_range=args.page_range,
        checkpoint_id=args.checkpoint_id,
    )

    where = f"checkpoint={args.checkpoint_id}" if args.checkpoint_id else fname
    rng = f" pages={args.page_range}" if args.page_range else " (whole doc)"
    print(f"> datalab extract[{args.mode}] section={args.section}:{rng} {where} ...", flush=True)
    client = DatalabClient()
    kwargs = {"options": opts}
    if not args.checkpoint_id:
        kwargs["file_path"] = str(src)
    result = client.extract(**kwargs)
    if not getattr(result, "success", False):
        sys.exit(f"! failed: {getattr(result, 'error', 'unknown')}")

    data = result.extraction_schema_json
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            sys.exit(f"could not parse extraction_schema_json:\n{str(data)[:500]}")
    if data is None:
        sys.exit("Datalab returned no extraction_schema_json — try a tighter "
                 "--page-range or a different --section.")

    written = {}
    if args.section == "all":
        for key, val in (data or {}).items():
            fn = f"{key}.json"   # financial -> financial.json (Jun17; was income_components.json)
            (out / fn).write_text(json.dumps(val, indent=2, ensure_ascii=False), encoding="utf-8")
            written[fn] = len(val) if isinstance(val, list) else 1
    else:
        payload = data.get(list_key, data) if (isinstance(data, dict) and list_key) else data
        (out / agent_file).write_text(json.dumps(payload, indent=2, ensure_ascii=False),
                                      encoding="utf-8")
        written[agent_file] = len(payload) if isinstance(payload, list) else 1

    cost = getattr(result, "cost_breakdown", None)
    meta = {"file": fname, "parser": f"datalab-extract:{args.mode}", "section": args.section,
            "page_range": args.page_range, "checkpoint_id_in": args.checkpoint_id,
            "cost_breakdown": cost, "written": written}
    (out / "_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    c = (cost or {}).get("final_cost_cents")
    print(f"+ extracted -> {out.relative_to(ROOT)}/  {written}"
          f"{f'  ({c}c)' if c is not None else ''}", flush=True)

    # quick A/B vs the Claude-agent pilot
    ad = agent_dir_for(stem)
    if ad and agent_file and (ad / agent_file).exists():
        try:
            agent_rows = json.loads((ad / agent_file).read_text(encoding="utf-8"))
            n_agent = len(agent_rows) if isinstance(agent_rows, list) else 1
            n_dl = next(iter(written.values()))
            print(f"\nA/B [{agent_file}]: datalab={n_dl}  vs  claude-agent={n_agent}")
            print("  diff field-level accuracy:")
            print(f"    {out / agent_file}")
            print(f"    {ad / agent_file}")
        except Exception:
            pass
    else:
        print("\n(no Claude-agent pilot to A/B against — extraction written only)")


if __name__ == "__main__":
    main()
