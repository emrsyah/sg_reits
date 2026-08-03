"""Move the 9 surviving sgx_reit_property.gla values into nla, then drop the gla column (dev only).

Agreed in the 2026-07-30 schema review (PR: area fields -> keep nla + gfa, drop gla).

WHY THE MOVE IS SAFE
  - gla is set on 9 rows out of 3420 (0.3%); nla on 2397, gfa on 1249.
  - gla set AND nla set: 0 rows. There is no conflict, so nothing is overwritten and no
    value has to be chosen between two candidates.
  - area_unit is a PER-ROW column and build_final_tables.py applies the same sqft->sqm
    conversion to gla, nla and gfa alike. Moving a value within its own row therefore
    preserves units exactly. (P40U FY2024 is sqft; UD1U FY2025 is sqm.)

The 9 rows:
  P40U FY2024  Plaza Arcade, David Jones Building                        (sqft, Retail)
  UD1U FY2025  Berlin / Bonn / Concor Park / Darmstadt / Muenster /
               Parc Cugat Green / Sant Cugat Green Campus                (sqm, Office)

SEMANTIC NOTE, on the record: GLA (gross lettable) and NLA (net lettable) are not the same
measure in principle -- GLA is the conventional retail metric. This merge accepts that
imprecision for 9 rows in exchange for dropping a column that is 99.7% empty. That trade was
the agreed decision; it is recorded here so it is not mistaken later for an extraction error.

The move NEVER overwrites: any row with both gla and nla set is reported and skipped.

Usage:
  python scripts/db/fix_property_gla_to_nla.py                  # DRY RUN, writes preview
  python scripts/db/fix_property_gla_to_nla.py --write          # move the 9 values only
  python scripts/db/fix_property_gla_to_nla.py --write --drop-column   # move, then DROP gla

--drop-column is deliberately separate: the move is reversible from the preview file, the
DROP is not. Run the move, check the data, then drop.

DRY BY DEFAULT. Dev only: connects solely via SUPABASE_CONNECTION_STRING, never touches prod.
Prod keeps its own gla column; promote_final_to_prod.py does `select *` and sends only prod's
columns, so a dropped dev column simply stops updating prod's -- it does not error.

After applying:
  python scripts/db/build_final_tables.py --only sgx_reit_property_final --write
"""
import os, sys, json, argparse
import psycopg2
from dotenv import load_dotenv

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(ROOT, ".env"))


def parse_args():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--write", action="store_true", help="apply to the dev raw table (default: dry run)")
    ap.add_argument("--drop-column", action="store_true",
                    help="after moving, DROP the gla column (irreversible; requires --write)")
    ap.add_argument("--preview", default=os.path.join(ROOT, "fixes", "property_gla_to_nla_preview.json"))
    return ap.parse_args()


def main():
    args = parse_args()
    cn = psycopg2.connect(os.environ["SUPABASE_CONNECTION_STRING"])
    cur = cn.cursor()

    cur.execute("""select id, symbol, financial_year, property_name, category, area_unit, gla, nla
                   from sgx_reit_property where gla is not null
                   order by symbol, financial_year, property_name""")
    rows = cur.fetchall()

    planned, conflicts = [], []
    for rid, sym, fy, name, cat, unit, gla, nla in rows:
        if nla is not None:
            conflicts.append((sym, fy, name, float(gla), float(nla))); continue
        planned.append({"id": rid, "symbol": sym, "financial_year": fy, "property_name": name,
                        "category": cat, "area_unit": unit, "gla_moved": float(gla)})

    print("=" * 78)
    print("PROPERTY gla -> nla" + ("  [--write]" if args.write else "  [DRY RUN]"))
    print("=" * 78)
    print(f"  rows with gla set        {len(rows)}")
    print(f"  planned moves            {len(planned)}")
    print(f"  conflicts (both set)     {len(conflicts)}   <- skipped, never overwritten")
    print(f"  drop gla column          {'YES' if args.drop_column else 'no'}")

    if planned:
        print(f"\n  {'sym':7s}{'fy':6s}{'unit':6s}{'value':>12s}  property")
        print("  " + "-" * 62)
        for p in planned:
            print(f"  {p['symbol'].split('.')[0]:7s}{str(p['financial_year']):6s}"
                  f"{str(p['area_unit']):6s}{p['gla_moved']:>12,.0f}  {p['property_name'][:36]}")
    if conflicts:
        print(f"\n  !! {len(conflicts)} rows have BOTH gla and nla -- left untouched, decide manually:")
        for c in conflicts:
            print(f"       {c[0]:9s} FY{c[1]} {c[2][:34]:34s} gla={c[3]:,.0f} nla={c[4]:,.0f}")
        print("     Dropping gla would DISCARD those gla values. Resolve before --drop-column.")

    os.makedirs(os.path.dirname(args.preview), exist_ok=True)
    with open(args.preview, "w", encoding="utf-8") as fh:
        json.dump({"planned_moves": planned, "conflicts": [list(c) for c in conflicts]}, fh, indent=2)
    print(f"\n  preview written -> {args.preview}")

    if not args.write:
        print("\n  DRY RUN -- nothing written. Re-run with --write to apply.")
        return
    if args.drop_column and conflicts:
        print("\n  REFUSING to drop gla: unresolved conflicts above would lose data.")
        return

    try:
        for p in planned:
            cur.execute("update sgx_reit_property set nla = gla, gla = null where id = %s", (p["id"],))
        if args.drop_column:
            cur.execute("alter table sgx_reit_property drop column gla")
        cn.commit()
        print(f"\n  APPLIED {len(planned)} moves to the dev raw table."
              + ("  gla column DROPPED." if args.drop_column else ""))
        print("  Prod untouched. Next: build_final_tables.py --only sgx_reit_property_final --write")
    except Exception as exc:
        cn.rollback()
        print(f"\n  ROLLED BACK -- {exc}")
        raise


if __name__ == "__main__":
    sys.exit(main())
