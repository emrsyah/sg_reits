"""Derive sgx_reit_property.lease_expiry_date from effective_date + lease_term_years (dev raw).

CONVENTION, STATED AND ASSUMED:  expiry = effective_date + lease_term_years - 1 day

This is an ASSUMPTION, not a disclosure. No annual report for any of these properties states an
expiry date. Read docs before trusting these values:

  - Across the rows where we already hold all three fields, 45 use `start + term` exactly and
    43 use `start + term - 1 day`. The convention is per-issuer, and NONE of the REITs written
    to here have any such validation row.
  - The only direct evidence found in the M44U AR (footnote (k), Toppan) points to minus-1-day.
    Footnote (j) on the same page contradicts it (two leases of 29 and 30 years "both ending in
    September 2031" reconciles under neither convention).
  - Accepted deliberately: these dates may be off by one day. On a 30-99 year land lease that was
    judged immaterial. They are NOT off by more than that, because every excluded case below is
    excluded precisely to keep the error to +/-1 day.

WHAT IS EXCLUDED, AND WHY (these would be WRONG, not merely imprecise):

  T82U            10 rows. Its effective_date is itself manufactured -- the AR states only a year
                  ("Leasehold 99 years from 1989") and the stored day was invented. Those rows have
                  since been corrected to a bare year, so they no longer parse as a date at all.
  dual-lease      Properties sitting on TWO land leases with DIFFERENT start dates (detected from
                  tenure_raw: "Two leases: ...", "Lot X: ... Lot Y: ..."). One row cannot hold two
                  expiries, so any single derived value is arbitrary. e.g. M44U "44 & 46 Changi
                  South Street 1", "Subang Land Parcel".
                  NOTE "30+30 years (1 May 1993)" is NOT dual -- it is one parcel with a renewal
                  option, one start date, 60 years total. Those ARE derived.
  non-integer     A fractional term ("73 years 3 months 13 days") cannot be added as whole years
                  without a second unit-conversion assumption. e.g. M44U "Pulau Sebarok".
  no tenure_raw   If tenure_raw is NULL we cannot rule out a dual lease, so we do not derive.
  MXNU Merlin     AR states "March 2005" -- month only. The stored day was invented, same defect
    House         as T82U. Excluded on the same grounds.

Rows are only ever written where lease_expiry_date IS NULL. Nothing existing is overwritten.

Usage:
  python scripts/db/derive_lease_expiry.py                 # DRY RUN, writes preview
  python scripts/db/derive_lease_expiry.py --write         # apply to the dev raw table

DRY BY DEFAULT. Dev only: connects solely via SUPABASE_CONNECTION_STRING, never touches prod.
After applying:
  python scripts/db/build_final_tables.py --only sgx_reit_property_final --write
"""
import os, sys, json, re, argparse, datetime
import psycopg2
from dotenv import load_dotenv

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(ROOT, ".env"))

SYMBOLS = ("M44U.SI", "MXNU.SI", "C38U.SI")     # T82U deliberately absent -- see docstring
EXCLUDE_NAMES = {("MXNU.SI", "Merlin House, Carmarthen")}
# tenure_raw is NULL here, but the AR was read directly and states a single lease:
# C38U p.43 "| Land Tenure | Leasehold tenure of 99 years with effect from 13 March 2006 |"
SINGLE_LEASE_VERIFIED = {("C38U.SI", "ION Orchard")}
DATE_IN_TEXT = re.compile(r"\d{1,2}\s+\w+\s+\d{4}")   # "16 May 1996"


def parse_args():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--write", action="store_true", help="apply to the dev raw table (default: dry run)")
    ap.add_argument("--preview", default=os.path.join(ROOT, "fixes", "lease_expiry_derived_preview.json"))
    return ap.parse_args()


def is_dual_lease(tenure_raw):
    """True if the row describes two land leases with different start dates."""
    if not tenure_raw:
        return True                                    # unknown -> treat as unsafe
    t = str(tenure_raw)
    if re.search(r"two\s+leases", t, re.I):
        return True
    if len(re.findall(r"\bLot\s+\d+", t, re.I)) > 1:
        return True
    # Drop any trailing "; remaining X years as at 31 Dec 2025" clause first. That reference
    # date is NOT a second lease start, and counting it flagged every MXNU row as dual.
    head = re.split(r";|\bremaining\b|\bas at\b", t, flags=re.I)[0]
    return len(DATE_IN_TEXT.findall(head)) > 1         # more than one start date quoted


def main():
    args = parse_args()
    cn = psycopg2.connect(os.environ["SUPABASE_CONNECTION_STRING"])
    cur = cn.cursor()
    cur.execute(f"""select id, symbol, financial_year, property_name, effective_date,
                           lease_term_years, tenure_raw
                    from sgx_reit_property
                    where symbol in %s
                      and effective_date is not null
                      and lease_term_years is not null
                      and lease_expiry_date is null
                    order by symbol, financial_year, property_name""", (SYMBOLS,))
    rows = cur.fetchall()

    planned, skipped = [], []
    for rid, sym, fy, name, eff, term, traw in rows:
        def skip(why):
            skipped.append({"symbol": sym, "financial_year": fy, "property_name": name,
                            "effective_date": str(eff), "lease_term_years": float(term),
                            "tenure_raw": traw, "reason": why})
        if (sym, name) in EXCLUDE_NAMES:
            skip("AR states month only; stored day was invented"); continue
        try:
            start = datetime.date.fromisoformat(str(eff)[:10])
        except ValueError:
            skip(f"effective_date {eff!r} is not a full date"); continue
        t = float(term)
        if t != int(t):
            skip(f"non-integer term {t}"); continue
        if (sym, name) not in SINGLE_LEASE_VERIFIED and is_dual_lease(traw):
            skip("two land leases with different start dates (or tenure_raw missing)"); continue
        try:
            anniv = start.replace(year=start.year + int(t))
        except ValueError:                              # 29 Feb -> non-leap year
            anniv = start.replace(month=3, day=1, year=start.year + int(t))
        expiry = anniv - datetime.timedelta(days=1)     # STATED CONVENTION: minus one day
        planned.append({"id": rid, "symbol": sym, "financial_year": fy, "property_name": name,
                        "effective_date": str(start), "lease_term_years": t,
                        "derived_lease_expiry_date": expiry.isoformat(), "tenure_raw": traw})

    print("=" * 78)
    print("DERIVE lease_expiry_date  (expiry = start + term - 1 day)"
          + ("  [--write]" if args.write else "  [DRY RUN]"))
    print("=" * 78)
    print(f"  candidate rows              {len(rows)}")
    print(f"  will derive                 {len(planned)}")
    print(f"  excluded                    {len(skipped)}")
    by_reason = {}
    for s in skipped:
        by_reason[s["reason"]] = by_reason.get(s["reason"], 0) + 1
    for why, n in sorted(by_reason.items(), key=lambda kv: -kv[1]):
        print(f"      {n:3d}  {why}")

    if planned:
        print(f"\n  {'sym':7s}{'fy':6s}{'start':12s}{'term':>6s}  {'-> expiry':12s} property")
        print("  " + "-" * 78)
        for p in planned[:15]:
            print(f"  {p['symbol'].split('.')[0]:7s}{str(p['financial_year']):6s}{p['effective_date']:12s}"
                  f"{p['lease_term_years']:>6g}  {p['derived_lease_expiry_date']:12s} {p['property_name'][:32]}")
        if len(planned) > 15:
            print(f"  ... and {len(planned)-15} more (full list in the preview file)")
    if skipped:
        print(f"\n  excluded rows:")
        for s in skipped:
            print(f"      {s['symbol'].split('.')[0]:6s} FY{s['financial_year']} "
                  f"{s['property_name'][:38]:38s} {s['reason'][:44]}")

    os.makedirs(os.path.dirname(args.preview), exist_ok=True)
    with open(args.preview, "w", encoding="utf-8") as fh:
        json.dump({"convention": "expiry = effective_date + lease_term_years - 1 day (ASSUMED)",
                   "planned": planned, "excluded": skipped}, fh, indent=2)
    print(f"\n  preview written -> {args.preview}")

    if not args.write:
        print("\n  DRY RUN -- nothing written. Re-run with --write to apply.")
        return

    try:
        for p in planned:
            cur.execute("""update sgx_reit_property set lease_expiry_date = %s
                           where id = %s and lease_expiry_date is null""",
                        (p["derived_lease_expiry_date"], p["id"]))
        cn.commit()
        print(f"\n  APPLIED {len(planned)} derived expiry dates to the dev raw table. Prod untouched.")
        print("  Next: build_final_tables.py --only sgx_reit_property_final --write")
    except Exception as exc:
        cn.rollback()
        print(f"\n  ROLLED BACK -- {exc}")
        raise


if __name__ == "__main__":
    sys.exit(main())
