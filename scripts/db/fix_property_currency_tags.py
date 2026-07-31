"""Fix sgx_reit_property.market_valuation_currency tags (dev raw table).

Two disjoint fixes, established by the audit in
docs/7-30-2026-schema-review/property-currency-tag-fix-list.md:

  GROUP B  tag is WRONG, the value is already SGD
           -> set market_valuation_currency = 'SGD'.  VALUE IS NOT TOUCHED.

  GROUP A  tag is RIGHT, the value is native
           -> convert market_valuation to SGD at the FY-end rate, then set the tag to 'SGD'.

ORDER MATTERS. Group B must be retagged before any conversion pass runs, or the conversion
catches it too -- converting M44U FY2023 would take it from S$13.1bn to S$4.5bn.
This script does both in the right order in one transaction, so ordering is handled.

NOT TOUCHED (verified scope/basis mismatches, NOT currency bugs -- see the fix list doc):
  ME8U 2024/2025  equity-accounted JV rows absent from the audited Portfolio Statement
  C38U 2024       we hold 100% values; the AR reports the proportionate share (already in alt_value)
  MXNU 2024       the AR itemises only 10 of 149 properties
  DCRU 2024/2025  properties (Note 6) and performance.portfolio_value (p31 AUM) are different metrics

FX: quarterly_rates.json (MAS quarterly), nearest quarter to the REIT's FY-end date, matching
the convention in build_final_tables.py.

Usage:
  python scripts/db/fix_property_currency_tags.py                 # DRY RUN (default), writes a preview
  python scripts/db/fix_property_currency_tags.py --write         # apply to the dev raw table

DRY BY DEFAULT. Nothing hits the database without --write.
After applying: rebuild _final and re-promote, then re-run the audit.
"""
import os, sys, json, argparse, collections
import psycopg2
import pandas as pd
from dotenv import load_dotenv

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(ROOT, ".env"))

# (symbol, financial_year) -- from the audit. Symbols are bare; the raw table stores '<SYM>.SI'.
GROUP_B = [  # tag spurious, value already SGD -> retag only
    ("C2PU", 2024), ("K71U", 2024), ("N2IU", 2023), ("M44U", 2023),
    ("A17U", 2024), ("A17U", 2025), ("BUOU", 2024),
]
GROUP_A = [  # value native -> convert then retag
    ("BTOU", 2024), ("BTOU", 2025), ("CMOU", 2024), ("CMOU", 2025),
    ("ODBU", 2024), ("ODBU", 2025), ("OXMU", 2024), ("OXMU", 2025),
    ("XZL", 2024), ("XZL", 2025), ("MXNU", 2025), ("SET", 2024), ("SET", 2025),
    ("UD1U", 2024), ("UD1U", 2025), ("ME8U", 2023), ("J91U", 2024),
]
SKIP = {("ME8U", 2024), ("ME8U", 2025), ("C38U", 2024), ("MXNU", 2024),
        ("DCRU", 2024), ("DCRU", 2025)}


def parse_args():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--write", action="store_true", help="apply to the dev raw table (default: dry run)")
    ap.add_argument("--preview", default=os.path.join(ROOT, "fixes", "property_currency_preview.json"))
    return ap.parse_args()


def load_rates():
    with open(os.path.join(ROOT, "quarterly_rates.json"), encoding="utf-8") as fh:
        q = json.load(fh)["quarters"]
    return q, sorted((pd.to_datetime(k), k) for k in q)


def make_rate_fn(rates, quarters):
    def rate(ccy, date):
        if ccy in (None, "", "SGD"):
            return 1.0
        c = "CNY" if ccy == "RMB" else ccy          # our data uses RMB; MAS publishes CNY
        q = min(quarters, key=lambda p: abs((p[0] - pd.to_datetime(date)).days))[1]
        return rates.get(q, {}).get(c, {}).get("SGD")
    return rate


def main():
    args = parse_args()
    rates, quarters = load_rates()
    rate = make_rate_fn(rates, quarters)

    cn = psycopg2.connect(os.environ["SUPABASE_CONNECTION_STRING"])
    cur = cn.cursor()
    cur.execute("select symbol, financial_year, date from sgx_reit_performance")
    fy_end = {(s.split(".")[0], f): d for s, f, d in cur.fetchall()}

    cur.execute("""select id, symbol, financial_year, property_name,
                          market_valuation, market_valuation_currency
                   from sgx_reit_property
                   where market_valuation is not null
                     and market_valuation_currency is not null
                     and market_valuation_currency <> 'SGD'
                   order by symbol, financial_year, property_name""")
    rows = cur.fetchall()

    planned, skipped, unclassified, no_rate = [], [], [], []
    for rid, sym, fy, name, mv, ccy in rows:
        key = (sym.split(".")[0], fy)
        if key in SKIP:
            skipped.append((key, name, ccy)); continue
        if key in GROUP_B:
            planned.append({"id": rid, "symbol": sym, "financial_year": fy, "property_name": name,
                            "group": "B", "old_currency": ccy, "new_currency": "SGD",
                            "old_value": float(mv), "new_value": float(mv), "rate": None})
        elif key in GROUP_A:
            d = fy_end.get(key)
            r = rate(ccy, d) if d else None
            if r is None:
                no_rate.append((key, name, ccy)); continue
            planned.append({"id": rid, "symbol": sym, "financial_year": fy, "property_name": name,
                            "group": "A", "old_currency": ccy, "new_currency": "SGD",
                            "old_value": float(mv), "new_value": round(float(mv) * r, 2), "rate": r})
        else:
            unclassified.append((key, name, ccy))

    # ---------- report ----------
    byg = collections.Counter(p["group"] for p in planned)
    print("=" * 78)
    print("PROPERTY CURRENCY-TAG FIX" + ("  [--write]" if args.write else "  [DRY RUN]"))
    print("=" * 78)
    print(f"  rows with a non-SGD tag           {len(rows)}")
    print(f"  planned changes                   {len(planned)}   (Group B retag {byg['B']}, Group A convert {byg['A']})")
    print(f"  skipped (scope/basis, not currency){len(skipped):>4d}")
    print(f"  unclassified (NOT in the audit)   {len(unclassified)}")
    print(f"  no FX rate available              {len(no_rate)}")

    agg = collections.defaultdict(lambda: {"n": 0, "old": 0.0, "new": 0.0, "grp": ""})
    for p in planned:
        a = agg[(p["symbol"].split(".")[0], p["financial_year"])]
        a["n"] += 1; a["old"] += p["old_value"]; a["new"] += p["new_value"]; a["grp"] = p["group"]
    print(f"\n  {'sym':6s}{'fy':6s}{'grp':5s}{'rows':>6s}{'sum before':>18s}{'sum after':>18s}")
    print("  " + "-" * 59)
    for k in sorted(agg, key=lambda k: (agg[k]["grp"], k)):
        a = agg[k]
        print(f"  {k[0]:6s}{str(k[1]):6s}{a['grp']:5s}{a['n']:>6d}{a['old']:>18,.0f}{a['new']:>18,.0f}")

    if unclassified:
        print(f"\n  !! {len(unclassified)} rows carry a non-SGD tag but are in NEITHER group and NOT skipped.")
        print("     These were not covered by the audit and are left untouched. Investigate:")
        for k, name, ccy in sorted(set((k, n, c) for k, n, c in unclassified))[:20]:
            print(f"       {k[0]:6s} FY{k[1]}  {str(name)[:44]:44s} {ccy}")
    if no_rate:
        print(f"\n  !! {len(no_rate)} rows have no FX rate for their currency/date -- left untouched:")
        for k, name, ccy in sorted(set((k, n, c) for k, n, c in no_rate))[:20]:
            print(f"       {k[0]:6s} FY{k[1]}  {str(name)[:44]:44s} {ccy}")

    os.makedirs(os.path.dirname(args.preview), exist_ok=True)
    with open(args.preview, "w", encoding="utf-8") as fh:
        json.dump({"planned": planned,
                   "skipped_scope_cases": sorted(set((f"{k[0]}", k[1]) for k, _, _ in skipped)),
                   "unclassified": sorted(set((f"{k[0]}", k[1], c) for k, _, c in unclassified)),
                   "no_rate": sorted(set((f"{k[0]}", k[1], c) for k, _, c in no_rate))},
                  fh, indent=2)
    print(f"\n  preview written -> {args.preview}")

    if not args.write:
        print("\n  DRY RUN -- nothing written. Re-run with --write to apply.")
        return

    # ---------- apply: Group B first, then Group A, one transaction ----------
    try:
        for grp in ("B", "A"):
            for p in [x for x in planned if x["group"] == grp]:
                cur.execute("""update sgx_reit_property
                                  set market_valuation = %s, market_valuation_currency = 'SGD'
                                where id = %s""", (p["new_value"], p["id"]))
        cn.commit()
        print(f"\n  APPLIED {len(planned)} rows (Group B retagged first, then Group A converted).")
        print("  Next: rebuild _final, re-promote, then re-run the audit.")
    except Exception as exc:
        cn.rollback()
        print(f"\n  ROLLED BACK -- {exc}")
        raise


if __name__ == "__main__":
    sys.exit(main())
