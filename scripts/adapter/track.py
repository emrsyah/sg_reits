#!/usr/bin/env python3
"""track.py - progress tracker across all ARs in the hybrid extraction run.

Each AR agent writes extracted_adapter/<stem>/status.json as it works. This scans them
all and prints a matrix (AR x section) plus gate verdicts, so you can see at a glance what
is done, in-flight, or not started across the ~40-report batch.

Usage:
  python scripts/adapter/track.py                 # print the matrix
  python scripts/adapter/track.py --csv out.csv   # also write a flat CSV

Per-section status values (set by the agent): planned | run | merged | gated | done | llm_only | skipped
"""
import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ADAPTER = ROOT / "extracted_adapter"
SECTIONS = ["profile", "performance", "properties", "top_tenants", "trade_mix", "financial"]
GLYPH = {"done": "OK", "gated": "G", "merged": "M", "run": "r", "planned": "p",
         "llm_only": "L", "skipped": "-", None: ".", "": "."}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=None)
    args = ap.parse_args()

    statuses = []
    for d in sorted(ADAPTER.glob("*/status.json")):
        try:
            statuses.append((d.parent.name, json.loads(d.read_text(encoding="utf-8"))))
        except json.JSONDecodeError:
            print(f"! bad status.json in {d.parent.name}")

    if not statuses:
        print("no status.json files yet under extracted_adapter/")
        sys.exit(0)

    # matrix
    print(f"{'AR (stem)':46s} {'sub_sector':12s} " +
          " ".join(f"{s[:5]:>5s}" for s in SECTIONS) + "  gates")
    print("-" * 110)
    legend_used = set()
    for stem, st in statuses:
        secs = st.get("sections", {})
        cells = []
        for s in SECTIONS:
            v = (secs.get(s) or {}).get("status")
            legend_used.add(v)
            cells.append(f"{GLYPH.get(v, '?'):>5s}")
        g = st.get("gates", {})
        gates = f"{g.get('schema', '?')}/{g.get('check', '?')}" if g else "-"
        print(f"{stem[:46]:46s} {str(st.get('sub_sector',''))[:12]:12s} "
              + " ".join(cells) + f"  {gates}")

    print("\nlegend: OK=done  G=gated  M=merged  r=run  p=planned  L=llm_only  -=skipped  .=not started")
    # counts
    done = sum(1 for _, st in statuses
               if all((st.get("sections", {}).get(s, {}) or {}).get("status") in ("done", "gated", "llm_only", "skipped")
                      for s in SECTIONS))
    print(f"\nARs with all sections resolved: {done}/{len(statuses)}  "
          f"(tracked ARs: {len(statuses)})")

    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["stem", "symbol", "financial_year", "sub_sector"]
                       + SECTIONS + ["schema_gate", "check_gate"])
            for stem, st in statuses:
                secs = st.get("sections", {})
                g = st.get("gates", {})
                w.writerow([stem, st.get("symbol"), st.get("financial_year"),
                            st.get("sub_sector")]
                           + [(secs.get(s, {}) or {}).get("status", "") for s in SECTIONS]
                           + [g.get("schema", ""), g.get("check", "")])
        print(f"+ wrote {args.csv}")


if __name__ == "__main__":
    main()
