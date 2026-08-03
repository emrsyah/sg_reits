"""Fix three verified sgx_reit_property lease-field bugs (dev raw table).

Each fix below was established by reading the annual report directly and hand-verifying the
quoted text. No value here is derived, inferred, or balanced -- every new value is what the
source document literally states. Rows that do not match the expected current value are
REPORTED AND SKIPPED, never coerced.

  BUG 1  M44U FY2023 "Subang Land Parcel"  lease_term_years 10245 -> 99
         Parse error: the extractor captured a LOT NUMBER as the lease term.
         AR (FY23/24, p.76, Property Portfolio - Malaysia) reads verbatim:
           "Lot 10245: 99 years (1 March 1989)<br>Lot 10246: 99 years (16 May 2012)"
         Corroboration: the same property is 99 in FY2024 and FY2025, so FY2023 is the outlier.
         NOTE (not fixed here): this is TWO land parcels with different starts. One row cannot
         represent both; the second parcel (16 May 2012) is still unrepresented. Same known
         dual-lease limitation as Toppan / 60 Alps Avenue / Nantong.

  BUG 2  T82U FY2024+FY2025, 5 properties/yr  effective_date '<yyyy>-01-01' -> '<yyyy>'
         False precision. The AR states only a YEAR. Verbatim (FY2025 pp.28/37/39):
           "| Title | Leasehold 99 years from 1989 (Remaining lease term of 63 years) |"
           "| Title | Leasehold 99 years from 2001 (Remaining lease term of 75 years) |"
           "| Title | Leasehold 99 years from 2005 (Remaining lease term of 79 years) |"
         There is no day or month anywhere in either AR for these assets; the stored
         '-01-01' was manufactured. effective_date is a TEXT column, so the bare year is
         representable without inventing a day.
         NOTE: Suntec City Mall / Office Towers / Convention Centre are NOT separately tenured
         in the AR -- all three inherit one "SUNTEC CITY" disclosure (99 years from 1989).

  BUG 3  M44U FY2023 "Pulau Sebarok"  lease_term_years 73.25 -> 73.2856
         AR p.62 verbatim: "73 years 3 months 13 days (1 Oct 1997)".
         73.25 encodes "73 years 3 months" and silently drops the 13 days.
         73 + 3/12 + 13/365.25 = 73.2856. This is the one fix that applies a unit conversion
         (months/days -> fractional years) rather than copying a stated figure, so it is gated
         behind --with-pulau-sebarok and is OFF by default. Neither 73.25 nor 73.2856 can
         represent the AR's exact wording in a numeric years column; review before enabling.

Usage:
  python scripts/db/fix_property_lease_fields.py                        # DRY RUN, writes preview
  python scripts/db/fix_property_lease_fields.py --write                # apply bugs 1 and 2
  python scripts/db/fix_property_lease_fields.py --with-pulau-sebarok   # include bug 3

DRY BY DEFAULT. Nothing hits the database without --write. Dev only: this script connects
solely via SUPABASE_CONNECTION_STRING and never touches prod.
After applying: rebuild _final with
  python scripts/db/build_final_tables.py --only sgx_reit_property_final --write
"""
import os, sys, json, argparse
import psycopg2
from dotenv import load_dotenv

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(ROOT, ".env"))

# (symbol, fy, property_name, column, expected_current, new_value, why)
FIXES = [
    ("M44U.SI", 2023, "Subang Land Parcel", "lease_term_years", "10245.0", "99",
     "AR p.76: 'Lot 10245: 99 years (1 March 1989)' -- lot number captured as term"),
]
for _fy in (2024, 2025):
    for _name, _yr in [("Suntec City Mall", "1989"),
                       ("Suntec City Office Towers", "1989"),
                       ("Suntec Singapore Convention & Exhibition Centre", "1989"),
                       ("One Raffles Quay", "2001"),
                       ("MBFC Properties", "2005")]:
        FIXES.append(("T82U.SI", _fy, _name, "effective_date", f"{_yr}-01-01", _yr,
                      f"AR states 'Leasehold 99 years from {_yr}' -- year only, day was manufactured"))

PULAU = ("M44U.SI", 2023, "Pulau Sebarok", "lease_term_years", "73.25", "73.2856",
         "AR p.62: '73 years 3 months 13 days' -- 73 + 3/12 + 13/365.25")


def parse_args():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--write", action="store_true", help="apply to the dev raw table (default: dry run)")
    ap.add_argument("--with-pulau-sebarok", action="store_true",
                    help="also apply BUG 3 (unit conversion, off by default)")
    ap.add_argument("--preview", default=os.path.join(ROOT, "fixes", "property_lease_fields_preview.json"))
    return ap.parse_args()


def main():
    args = parse_args()
    fixes = list(FIXES) + ([PULAU] if args.with_pulau_sebarok else [])

    cn = psycopg2.connect(os.environ["SUPABASE_CONNECTION_STRING"])
    cur = cn.cursor()

    planned, mismatched, missing = [], [], []
    for sym, fy, name, col, expected, new, why in fixes:
        cur.execute(f"""select id, {col}::text from sgx_reit_property
                        where symbol=%s and financial_year=%s and property_name=%s""",
                    (sym, fy, name))
        got = cur.fetchall()
        if not got:
            missing.append((sym, fy, name, col)); continue
        for rid, current in got:
            # normalise numeric text so '99.0' == '99' does not read as a mismatch
            def norm(v):
                try: return f"{float(v):.6f}"
                except (TypeError, ValueError): return v
            if norm(current) != norm(expected):
                mismatched.append((sym, fy, name, col, current, expected)); continue
            planned.append({"id": rid, "symbol": sym, "financial_year": fy, "property_name": name,
                            "column": col, "old_value": current, "new_value": new, "reason": why})

    print("=" * 78)
    print("PROPERTY LEASE-FIELD FIX" + ("  [--write]" if args.write else "  [DRY RUN]"))
    print("=" * 78)
    print(f"  planned changes                    {len(planned)}")
    print(f"  skipped, current value unexpected  {len(mismatched)}")
    print(f"  skipped, row not found             {len(missing)}")
    print(f"  BUG 3 (Pulau Sebarok)              {'INCLUDED' if args.with_pulau_sebarok else 'excluded (default)'}")

    if planned:
        print(f"\n  {'sym':9s}{'fy':6s}{'column':18s}{'old':14s}{'new':12s}property")
        print("  " + "-" * 92)
        for p in planned:
            print(f"  {p['symbol']:9s}{str(p['financial_year']):6s}{p['column']:18s}"
                  f"{str(p['old_value'])[:13]:14s}{str(p['new_value'])[:11]:12s}{p['property_name'][:40]}")
    if mismatched:
        print(f"\n  !! {len(mismatched)} rows hold a value other than the audited one -- NOT touched.")
        print("     The data changed since the audit; re-verify against the AR before forcing:")
        for m in mismatched:
            print(f"       {m[0]:9s} FY{m[1]} {m[2][:36]:36s} {m[3]}: found {m[4]!r}, expected {m[5]!r}")
    if missing:
        print(f"\n  !! {len(missing)} audited rows are absent from the table -- NOT created:")
        for m in missing:
            print(f"       {m[0]:9s} FY{m[1]} {m[2][:44]:44s} {m[3]}")

    os.makedirs(os.path.dirname(args.preview), exist_ok=True)
    with open(args.preview, "w", encoding="utf-8") as fh:
        json.dump({"planned": planned,
                   "skipped_value_mismatch": [list(m) for m in mismatched],
                   "skipped_row_missing": [list(m) for m in missing],
                   "pulau_sebarok_included": args.with_pulau_sebarok}, fh, indent=2)
    print(f"\n  preview written -> {args.preview}")

    if not args.write:
        print("\n  DRY RUN -- nothing written. Re-run with --write to apply.")
        return
    if not planned:
        print("\n  nothing to apply.")
        return

    try:
        for p in planned:
            cur.execute(f"update sgx_reit_property set {p['column']} = %s where id = %s",
                        (p["new_value"], p["id"]))
        cn.commit()
        print(f"\n  APPLIED {len(planned)} rows to the dev raw table. Prod untouched.")
        print("  Next: python scripts/db/build_final_tables.py --only sgx_reit_property_final --write")
    except Exception as exc:
        cn.rollback()
        print(f"\n  ROLLED BACK -- {exc}")
        raise


if __name__ == "__main__":
    sys.exit(main())
