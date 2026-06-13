#!/usr/bin/env python3
"""merge_llm.py - merge the batched LLM pass back into deterministic records.

Step 5/6 of the hybrid plan: take the deterministic records (needs_llm fields null) and
the LLM-filled map {property_name: {field: value}}, write the merged records, and run a
final sanity check (anything weird?). Only fields the plan flagged needs_llm are filled;
deterministic values are never overwritten.

Usage:
  python scripts/adapter/merge_llm.py <deterministic.json> <llm_filled.json> <plan.json> [--out merged.json]
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("deterministic")
    ap.add_argument("llm_filled")
    ap.add_argument("plan")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    det = json.loads(Path(args.deterministic).read_text(encoding="utf-8"))
    llm = json.loads(Path(args.llm_filled).read_text(encoding="utf-8"))
    plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    llm_fields = [f for f, s in plan["fields"].items() if s.get("decision") == "needs_llm"]

    filled = 0
    for rec in det:
        m = llm.get(rec.get("property_name"), {})
        for f in llm_fields:
            if f in m and rec.get(f) in (None, ""):
                rec[f] = m[f]
                filled += 1
        rec.pop("_warn", None)

    out = Path(args.out) if args.out else Path(args.deterministic).with_name("properties_merged.json")
    out.write_text(json.dumps(det, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"merged {filled} LLM values across {len(llm_fields)} field(s) -> {out}")

    # final check: weird things
    weird = []
    for r in det:
        if isinstance(r.get("market_valuation"), (int, float)) and r["market_valuation"] < 1_000_000:
            weird.append((r["property_name"], "valuation < 1m (unit?)", r["market_valuation"]))
        if r.get("ownership") is not None and not (0 < r["ownership"] <= 100):
            weird.append((r["property_name"], "ownership out of range", r["ownership"]))
        for f in llm_fields:
            if r.get(f) is None:
                weird.append((r["property_name"], f"{f} still null after merge", None))
    still_null = {f: sum(1 for r in det if r.get(f) in (None, "")) for f in plan["fields"]}
    print("\nfinal-check (fields still null across rows):")
    for f, n in still_null.items():
        if n:
            dec = plan["fields"][f].get("decision")
            print(f"  {f:20s} {n}/{len(det)} null   [{dec}]")
    print("\nWEIRD:" if weird else "\nno anomalies.", *([f"\n  {w}" for w in weird] or []))


if __name__ == "__main__":
    main()
