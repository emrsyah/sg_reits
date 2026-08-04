"""Finish the property schema review items PR.1 / PR.3 on dev raw.

Three steps, one transaction:

  1. DERIVE the last lease_expiry_date values that effective_date + lease_term_years
     can still produce. The earlier pass left 17; 7 of those carry a full
     commencement date and are derivable. The other 10 are T82U rows whose
     effective_date is a YEAR ONLY ("1989") -- a year cannot produce a
     day-precision expiry, and inventing 01-01 would be fabricating precision.
     Those are reported, never guessed.

  2. DROP effective_date. Everything it could contribute is now in
     lease_expiry_date. See --report for exactly what the drop costs.

  3. DROP gla. It is already empty (its 9 values were moved into nla); this
     removes the column so the schema doc and the database agree.

Usage:
  python scripts/db/finish_property_lease_and_gla.py            # DRY RUN
  python scripts/db/finish_property_lease_and_gla.py --write

DRY BY DEFAULT.
"""
import os, sys, argparse
import psycopg2
from dotenv import load_dotenv

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(ROOT, ".env"))
T = "sgx_reit_property"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    cn = psycopg2.connect(os.environ["SUPABASE_CONNECTION_STRING"])
    cur = cn.cursor()

    # ---- 1. what is still derivable ----
    cur.execute(f"""select id, symbol, financial_year, property_name,
                           effective_date, lease_term_years
                    from {T}
                    where effective_date is not null and lease_term_years is not null
                      and lease_expiry_date is null
                    order by symbol, financial_year""")
    pending = cur.fetchall()

    derivable, year_only = [], []
    for _id, sym, fy, name, eff, term in pending:
        e = str(eff).strip()
        # a full date -- YYYY-MM-DD; anything shorter carries no day
        if len(e) >= 10 and e[4] == "-" and e[7] == "-":
            derivable.append((_id, sym, fy, name, e, term))
        else:
            year_only.append((_id, sym, fy, name, e, term))

    print("=" * 74)
    print("FINISH property lease + gla" + ("  [--write]" if args.write else "  [DRY RUN]"))
    print("=" * 74)
    print(f"\n  rows still missing lease_expiry_date with inputs present: {len(pending)}")
    print(f"    derivable (full commencement date)  {len(derivable)}")
    print(f"    NOT derivable (year-only date)      {len(year_only)}")

    if derivable:
        print("\n  will derive:")
        for _id, sym, fy, name, e, term in derivable:
            print(f"     {sym:9s}FY{fy} {str(name)[:38]:38s} {e} + {term}y")

    if year_only:
        print("\n  will NOT derive -- effective_date is a year, not a date."
              "\n  Dropping effective_date LOSES this commencement year for these rows:")
        for _id, sym, fy, name, e, term in year_only:
            print(f"     {sym:9s}FY{fy} {str(name)[:38]:38s} {e!r} + {term}y")

    cur.execute(f"select count(*) from {T} where gla is not null")
    gla_n = cur.fetchone()[0]
    cur.execute(f"select count(*) from {T} where effective_date is not null")
    eff_n = cur.fetchone()[0]
    print(f"\n  gla non-null rows            {gla_n}   (must be 0 to drop safely)")
    print(f"  effective_date non-null rows {eff_n}   (dropped after derivation)")

    if not args.write:
        print("\n  DRY RUN -- nothing written.")
        return 0
    if gla_n:
        print("\n  REFUSING: gla still holds values; move them into nla first.")
        return 1

    try:
        for _id, sym, fy, name, e, term in derivable:
            # date + interval: Postgres does the calendar arithmetic, not us
            cur.execute(f"""update {T}
                            set lease_expiry_date = (%s::date + (%s || ' years')::interval)::date
                            where id = %s""", (e, str(term), _id))
        cur.execute(f"alter table {T} drop column effective_date")
        cur.execute(f"alter table {T} drop column gla")
        cn.commit()
        print(f"\n  APPLIED: {len(derivable)} expiry dates derived; "
              f"effective_date and gla dropped.")
        print("  Next: rebuild _final (build_final_tables.py still selects effective_date).")
    except Exception as exc:
        cn.rollback()
        print(f"\n  ROLLED BACK -- {exc}")
        raise
    return 0


if __name__ == "__main__":
    sys.exit(main())
