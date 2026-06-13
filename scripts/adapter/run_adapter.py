#!/usr/bin/env python3
"""run_adapter.py - deterministic table extractor driven by an extraction plan.

Consumes a plan (the artifact the planning step writes after sampling rows vs the schema)
and an HTML table, and emits one record per data row WITHOUT any LLM call. Fields the plan
marked `needs_llm` or `absent_here` are left null and collected into a to-do list, so the
LLM only ever touches those (batched), then merges back.

This is a generic engine, NOT generated code: the plan is declarative and inspectable, so
there is no exec() of model-written Python.

Usage:
  python scripts/adapter/run_adapter.py <plan.json>
  python scripts/adapter/run_adapter.py <plan.json> --out records.json

Methods supported per field:
  const  text  enum  parse_years  concat  scale  context  page  needs_llm  absent_here
Output:
  <out>                 the deterministic records (list)
  <out>.llm_todo.json   {field: [{row, property_name, reason}]} for the LLM pass
  prints a summary: rows, per-field fill, decision tally
"""
import argparse
import json
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
FOOTNOTE_RX = re.compile(r"\s+\d{1,2}$")          # trailing superscript footnote number
NUM_RX = re.compile(r"^\(?-?[\d,]+(?:\.\d+)?\)?$")
YEARS_RX = re.compile(r"(\d+(?:\.\d+)?)\s*year", re.I)


def num(s: str):
    s = (s or "").strip()
    if not s or s.lower() in ("nan", "na", "n.a.", "–", "-", "—"):
        return None
    if not NUM_RX.match(s):
        return None
    neg = s.startswith("(") and s.endswith(")")
    v = float(s.strip("()").replace(",", ""))
    return -v if neg else v


def clean(s: str, strip_footnote=False) -> str:
    s = re.sub(r"\s+", " ", (s or "").strip())
    if strip_footnote:
        s = FOOTNOTE_RX.sub("", s).strip()
    return s


PAGE_RX = re.compile(r"/page/(\d+)/")


def block_page(el):
    """Datalab tags blocks with data-block-id like '/page/108/Table/2' (0-based page).
    Page can sit on the element or any ancestor; return the nearest one found."""
    for node in [el, *el.parents]:
        bid = node.get("data-block-id") if hasattr(node, "get") else None
        if bid:
            m = PAGE_RX.search(bid)
            if m:
                return int(m.group(1))
    return None


def pick_table(tables, table_contains, table_index):
    """Prefer locating the table by header text (robust as table positions shift across
    reports); fall back to a fixed index. Returns (table, chosen_index)."""
    if table_contains:
        needles = [table_contains] if isinstance(table_contains, str) else table_contains
        for i, t in enumerate(tables):
            txt = t.get_text(" ", strip=True).lower()
            if all(n.lower() in txt for n in needles):
                return t, i
        sys.exit(f"no table contains {needles!r} ({len(tables)} tables present)")
    if table_index is None or table_index >= len(tables):
        sys.exit(f"table_index {table_index} out of range ({len(tables)} tables)")
    return tables[table_index], table_index


def load_table(html_path: Path, table_index, table_contains=None):
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "lxml")
    tables = soup.find_all("table")
    table, chosen = pick_table(tables, table_contains, table_index)
    if table_contains:
        print(f"  (matched table #{chosen} by header text)")
    # footnote markers are <sup> tags; remove them so "Westgate¹"->"Westgate" while
    # "Junction 8" (a real name) is untouched. Deterministic, no regex guessing.
    for sup in table.find_all(["sup", "sub"]):
        sup.decompose()
    rows = []
    for tr in table.find_all("tr"):
        cells = tr.find_all(["td", "th"])
        if not cells:
            continue
        texts = [clean(c.get_text(" ", strip=True)) for c in cells]
        # per-row page if a cell carries its own block-id, else the table's page
        page = next((block_page(c) for c in cells if block_page(c) is not None), None)
        if page is None:
            page = block_page(table)
        rows.append((texts, page))
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    plan = json.loads((ROOT / args.plan if not Path(args.plan).is_absolute()
                       else Path(args.plan)).read_text(encoding="utf-8"))
    src = plan["source"]
    html_path = ROOT / src["html"] if not Path(src["html"]).is_absolute() else Path(src["html"])
    rows = load_table(html_path, src.get("table_index"), src.get("table_contains"))
    value_col = src["value_col"]
    consts = plan.get("consts", {})
    fields = plan["fields"]
    skip_rx = re.compile(plan["skip_col0_regex"]) if plan.get("skip_col0_regex") else None
    ctx_rules = plan.get("context_rules", [])

    records, llm_todo = [], {}
    ctx = {}                                   # carried country/category/status
    for texts, page in rows:
        col0 = texts[0] if texts else ""
        # context updates
        for rule in ctx_rules:
            hit = False
            if "col0_regex" in rule:
                m = re.match(rule["col0_regex"], col0)
                if m:
                    ctx[rule["set"]] = clean(m.group(rule.get("capture", 0)), True)
                    hit = True
            elif "col0_in" in rule and col0 in rule["col0_in"]:
                ctx[rule["set"]] = col0
                hit = True
            if hit and "also" in rule:
                for k, v in rule["also"].items():
                    ctx[k] = v
        # is this a property (data) row? value_col numeric AND not a skip header
        if value_col >= len(texts) or num(texts[value_col]) is None:
            continue
        if skip_rx and skip_rx.match(col0):
            continue

        rec = {}
        for fname, spec in fields.items():
            m = spec["method"]
            if m == "const":
                rec[fname] = consts.get(spec["from"])
            elif m == "text":
                rec[fname] = clean(texts[spec["col"]], spec.get("strip_footnote", False)) or None
            elif m == "enum":
                v = clean(texts[spec["col"]])
                rec[fname] = v if v in spec["allowed"] else None
                if v and rec[fname] is None:
                    rec.setdefault("_warn", []).append(f"{fname}='{v}' not in enum")
            elif m == "parse_years":
                mm = YEARS_RX.search(texts[spec["col"]] or "")
                rec[fname] = float(mm.group(1)) if mm else None
            elif m == "concat":
                parts = [clean(texts[c]) for c in spec["cols"]
                         if c < len(texts) and clean(texts[c]).lower() not in ("", "nan")]
                rec[fname] = spec.get("sep", " ").join(parts) or None
            elif m == "scale":
                v = num(texts[spec["col"]])
                rec[fname] = v * spec.get("scale", 1) if v is not None else None
            elif m == "context":
                rec[fname] = ctx.get(spec["from"], spec.get("default"))
            elif m == "page":
                rec[fname] = (page + 1) if page is not None else None     # printed page
            elif m in ("needs_llm", "absent_here"):
                rec[fname] = None
                llm_todo.setdefault(fname, []).append(
                    {"row": len(records), "property_name": rec.get("property_name"),
                     "decision": spec["decision"],
                     "reason": spec.get("reason") or spec.get("where")})
        records.append(rec)

    out = Path(args.out) if args.out else (html_path.parent / "properties_deterministic.json")
    out.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")
    (out.parent / (out.stem + ".llm_todo.json")).write_text(
        json.dumps(llm_todo, indent=2, ensure_ascii=False), encoding="utf-8")

    # summary
    print(f"rows extracted: {len(records)}  ->  {out.relative_to(ROOT)}")
    det = [f for f, s in fields.items() if s["decision"] == "deterministic"]
    nl = [f for f, s in fields.items() if s["decision"] == "needs_llm"]
    os_ = [f for f, s in fields.items() if s["decision"] == "other_source"]
    print(f"\ndeterministic fields ({len(det)}): {', '.join(det)}")
    print(f"needs_llm fields ({len(nl)}): {', '.join(nl)}")
    print(f"other_source fields ({len(os_)}): {', '.join(os_)}")
    print("\nfill rate (deterministic fields):")
    for f in det:
        n = sum(1 for r in records if r.get(f) not in (None, "", []))
        print(f"  {f:18s} {n}/{len(records)}")
    warns = [(r.get("property_name"), r["_warn"]) for r in records if r.get("_warn")]
    if warns:
        print("\nwarnings:", warns)


if __name__ == "__main__":
    main()
