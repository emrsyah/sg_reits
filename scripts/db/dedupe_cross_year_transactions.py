"""Collapse cross-year duplicate transactions to ONE row, in the year the deal completed.

A deal disclosed in two annual reports currently occupies two rows -- once as announced or
completed in the FY(N) report, again in the FY(N+1) report. deal_id links them, but a
consumer still sees the same property twice and must know to group.

RULE
  keep exactly one row per deal_id, in the financial year that CONTAINS completed_date,
  merged field-by-field so the surviving row is the most complete version.

  financial_year here is the REPORTING year, and six REITs have non-December year ends, so
  the target year is computed from each REIT's own FY-end dates in sgx_reit_performance --
  never assumed from the calendar year of completed_date.

MERGE PRECEDENCE, per field
  1. a value from the row whose status is 'completed' beats one from 'announced'
  2. otherwise the first non-null wins, later report first (it has seen the outcome)
  Announced rows routinely carry the AGREED price; the completed row carries the FINAL one,
  which is why (1) exists. o5ru:3_toh_tuck_link announced 25,006,000 and completed
  24,388,000 -- the completed figure is the fact.

NOT TOUCHED
  Same-year aggregates (hmn:wbf_trio, a17u:qld_trio, hmn:rental_housing_trio,
  hmn:ginza_kanazawa_pair) -- several DISTINCT properties sharing one price in one year.
  Those legitimately stay as multiple rows; deal_id is what groups them.

  Deals with no completed_date on any row (still announced) -- there is no completion year
  to collapse into, so they stay as they are.

Usage:
  python scripts/db/dedupe_cross_year_transactions.py            # DRY RUN
  python scripts/db/dedupe_cross_year_transactions.py --write
"""
import os, sys, argparse, datetime
import psycopg2
from psycopg2.extras import Json
from dotenv import load_dotenv

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(ROOT, ".env"))

MERGE_SKIP = {"id", "symbol", "deal_id", "financial_year"}


def fy_windows(cur):
    """(symbol, financial_year) -> (start, end) from each REIT's own FY-end dates."""
    # the transaction table stores bare tickers, sgx_reit_performance stores SYMBOL.SI
    cur.execute("select symbol, financial_year, date from sgx_reit_performance where date is not null")
    ends = {}
    for sym, fy, d in cur.fetchall():
        ends.setdefault(sym.replace(".SI", ""), {})[fy] = d
    win = {}
    for sym, by_fy in ends.items():
        for fy, end in by_fy.items():
            prev = by_fy.get(fy - 1)
            start = (prev + datetime.timedelta(days=1)) if prev else end.replace(year=end.year - 1) + datetime.timedelta(days=1)
            win[(sym, fy)] = (start, end)
    return win


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    cn = psycopg2.connect(os.environ["SUPABASE_CONNECTION_STRING"])
    cur = cn.cursor()

    cur.execute("""select column_name from information_schema.columns
                   where table_name='sgx_reit_property_transaction' order by ordinal_position""")
    cols = [r[0] for r in cur.fetchall()]

    cur.execute(f"select {','.join(cols)} from sgx_reit_property_transaction")
    rows = [dict(zip(cols, r)) for r in cur.fetchall()]

    by_deal = {}
    for r in rows:
        by_deal.setdefault(r["deal_id"], []).append(r)

    win = fy_windows(cur)
    plans, skipped = [], []

    # A deal can be BOTH a multi-property aggregate and cross-year (m44u:chee_wah_subang_1
    # is 2 properties x 2 report years = 4 rows). Sub-group on property_name so each
    # property collapses on its own; a same-year aggregate then has one row per sub-group
    # and is skipped by the len<2 test below, exactly as intended.
    units = []
    for did, group in by_deal.items():
        names = {r["property_name"] for r in group}
        years = {r["financial_year"] for r in group}
        if len(names) > 1 and len(years) > 1 and len(group) > len(names):
            for nm in names:
                units.append((did, [r for r in group if r["property_name"] == nm]))
        else:
            units.append((did, group))

    for did, group in units:
        if len(group) < 2:
            continue
        years = {r["financial_year"] for r in group}
        names = {r["property_name"] for r in group}
        if len(years) < 2:
            skipped.append((did, f"same-year aggregate, {len(names)} properties")); continue

        comp = [r["completed_date"] for r in group if r["completed_date"]]
        if not comp:
            # still announced in every report -- no completion year to collapse into, but
            # two identical pending rows are still a duplicate. Keep the LATEST report's
            # row (the current state of the deal) and merge the earlier one into it.
            order = sorted(group, key=lambda r: -r["financial_year"])
            merged = dict(order[0]); filled = []
            for r in order[1:]:
                for c in cols:
                    if c not in MERGE_SKIP and merged.get(c) is None and r.get(c) is not None:
                        merged[c] = r[c]; filled.append(c)
            plans.append((did, group[0]["symbol"], sorted(years), order[0]["financial_year"],
                          None, order[0]["id"], [r["id"] for r in order[1:]], merged,
                          sorted(set(filled)), group))
            continue
        cdate = max(comp)
        try:
            cd = datetime.date.fromisoformat(str(cdate)[:10])
        except ValueError:
            skipped.append((did, f"unparseable completed_date {cdate!r}")); continue

        sym = group[0]["symbol"]
        target = None
        for r in group:
            w = win.get((sym, r["financial_year"]))
            if w and w[0] <= cd <= w[1]:
                target = r["financial_year"]; break
        if target is None:
            skipped.append((did, f"completed {cd} falls in no candidate FY window")); continue

        # merge: completed rows first, then later report first
        order = sorted(group, key=lambda r: (r["status"] != "completed", -r["financial_year"]))
        merged = dict(order[0])
        filled = []
        for r in order[1:]:
            for c in cols:
                if c in MERGE_SKIP:
                    continue
                if merged.get(c) is None and r.get(c) is not None:
                    merged[c] = r[c]; filled.append(c)
        keep = [r for r in group if r["financial_year"] == target]
        keep_id = (keep[0] if keep else order[0])["id"]
        merged["financial_year"] = target
        drop_ids = [r["id"] for r in group if r["id"] != keep_id]
        plans.append((did, sym, sorted(years), target, cd, keep_id, drop_ids, merged, sorted(set(filled)), group))

    print("=" * 84)
    print("DEDUPE cross-year transactions" + ("  [--write]" if args.write else "  [DRY RUN]"))
    print("=" * 84)
    print(f"\n  deals to collapse: {len(plans)}   rows removed: {sum(len(p[6]) for p in plans)}")
    for did, sym, years, target, cd, _k, drops, merged, filled, group in plans:
        price = merged.get("sale_price") if merged.get("sale_price") is not None else merged.get("purchase_price")
        print(f"\n  {did}")
        print(f"     years {years} -> keep FY{target}   completed {cd}   drop {len(drops)} row(s)")
        for r in group:
            p = r.get("sale_price") if r.get("sale_price") is not None else r.get("purchase_price")
            mark = "KEEP" if r["financial_year"] == target else "drop"
            print(f"        {mark}  FY{r['financial_year']}  {str(r['status']):10s} price={p}")
        if filled:
            print(f"     fields back-filled from the dropped row: {', '.join(filled)}")
        print(f"     surviving price={price}  status={merged.get('status')}")

    if skipped:
        print(f"\n  left alone ({len(skipped)}):")
        for d, why in skipped:
            print(f"     {d[:58]:58s} {why}")

    if not args.write:
        print("\n  DRY RUN -- nothing written.")
        return 0

    try:
        for did, sym, years, target, cd, keep_id, drops, merged, filled, group in plans:
            sets = [c for c in cols if c not in ("id", "symbol", "deal_id")]
            # jsonb columns (raw, announcement_refs, flags) arrive as dict/list and must be
            # re-wrapped; psycopg2 cannot adapt a bare dict.
            vals = [Json(merged[c]) if isinstance(merged[c], (dict, list)) else merged[c]
                    for c in sets]
            cur.execute(f"update sgx_reit_property_transaction set {','.join(c+'=%s' for c in sets)} where id=%s",
                        vals + [keep_id])
            # id is uuid; psycopg2 sends a text[] so it needs an explicit cast
            cur.execute("delete from sgx_reit_property_transaction where id = any(%s::uuid[])", (drops,))
        cn.commit()
        print(f"\n  APPLIED: {len(plans)} deals collapsed, {sum(len(p[6]) for p in plans)} rows deleted.")
        print("  Next: rebuild _final, then promote.")
    except Exception as exc:
        cn.rollback()
        print(f"\n  ROLLED BACK -- {exc}")
        raise
    return 0


if __name__ == "__main__":
    sys.exit(main())
