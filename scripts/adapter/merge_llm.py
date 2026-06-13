#!/usr/bin/env python3
"""merge_llm.py - merge a batched LLM pass back into deterministic records.

Steps 5-6 of the hybrid plan. Takes the deterministic records and an LLM-filled map
{property_name: {field: value}} and fills the fields the plan flagged for the LLM. Run it
once per LLM lane:
  - needs_llm   fields (judgement/combine: ownership, value_basis, component, ...)
  - other_source fields (live elsewhere, e.g. per-property cards: occupancy, gla, nla,
    net_property_income, gross_revenue, major_tenant)

Pass --decision to choose which set this map fills (default: both). Matching is by
NORMALISED name (audited statements use full legal names, cards/marketing use
abbreviations), so "Guangdong Data Centre 1 (Guangdong DC 1)" matches "Guangdong DC 1".
Deterministic values are never overwritten.

Usage:
  python scripts/adapter/merge_llm.py <records.json> <llm_filled.json> <plan.json> \
      [--decision needs_llm|other_source|both] [--out merged.json]
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def norm(s: str) -> str:
    """Normalise a property name for cross-section matching: lowercase alphanumerics,
    and also key on the abbreviation inside quotes/parens if present."""
    s = s or ""
    return "".join(c.lower() for c in s if c.isalnum())


def name_keys(s: str):
    """All match keys for a name: the whole thing + any quoted/paren abbreviation."""
    keys = {norm(s)}
    for m in re.findall(r'[\("“]([^)"”]+)[\)"”]', s or ""):
        keys.add(norm(m))
    return {k for k in keys if k}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("deterministic")
    ap.add_argument("llm_filled")
    ap.add_argument("plan")
    ap.add_argument("--decision", default="both",
                    choices=["needs_llm", "other_source", "both"])
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    det = json.loads(Path(args.deterministic).read_text(encoding="utf-8"))
    llm = json.loads(Path(args.llm_filled).read_text(encoding="utf-8"))
    plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))

    wanted = ({"needs_llm", "other_source"} if args.decision == "both"
              else {args.decision})
    fields = [f for f, s in plan["fields"].items() if s.get("decision") in wanted]

    # index the LLM map by all name keys for fuzzy cross-section matching
    llm_index = {}
    for k, v in llm.items():
        for nk in name_keys(k):
            llm_index[nk] = v

    filled = unmatched = 0
    for rec in det:
        m = {}
        for nk in name_keys(rec.get("property_name", "")):
            if nk in llm_index:
                m = llm_index[nk]
                break
        if not m and any(rec.get(f) in (None, "") for f in fields):
            unmatched += 1
        for f in fields:
            if f in m and m[f] not in (None, "") and rec.get(f) in (None, ""):
                rec[f] = m[f]
                filled += 1
        rec.pop("_warn", None)

    out = Path(args.out) if args.out else Path(args.deterministic).with_name("properties_merged.json")
    out.write_text(json.dumps(det, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"merged {filled} value(s) across {len(fields)} {args.decision} field(s) "
          f"-> {out}" + (f"  ({unmatched} record(s) had no LLM match)" if unmatched else ""))

    # final check
    weird = []
    for r in det:
        mv = r.get("market_valuation")
        if isinstance(mv, (int, float)) and 0 < mv < 1_000_000:
            weird.append((r["property_name"], "valuation < 1m (unit?)", mv))
        if r.get("ownership") is not None and not (0 < r["ownership"] <= 100):
            weird.append((r["property_name"], "ownership out of range", r["ownership"]))
        occ = r.get("occupancy_rate")
        if isinstance(occ, (int, float)) and not (0 <= occ <= 100):
            weird.append((r["property_name"], "occupancy out of range", occ))
    still_null = {f: sum(1 for r in det if r.get(f) in (None, "")) for f in plan["fields"]}
    print("\nfinal-check (fields still null across rows):")
    for f, n in still_null.items():
        if n:
            print(f"  {f:20s} {n}/{len(det)} null   [{plan['fields'][f].get('decision')}]")
    print("\nWEIRD:" if weird else "\nno anomalies.", *([f"\n  {w}" for w in weird] or []))


if __name__ == "__main__":
    main()
