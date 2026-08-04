"""Backfill basis_segment on the FY2025 segmented disclosures the remap missed.

The 2026-08-03 remap tagged only FY2024. FY2025 discloses the same segment splits and
was left NULL, which collapses two separate-denominator tables onto one key:

  T82U FY2025 trade_mix   26 rows summing to 200.0%  <- the exact bug basis_segment exists
                                                        to prevent, still live
  T82U FY2025 top_tenant  20 rows, office + retail untagged
  BUOU FY2025 top_tenant  20 rows, L&I + commercial untagged

Assignments come from the annual reports, not from inference:

  T82U FY2025 AR L961-L1002  "Office Portfolio Business Sector Analysis" (13 sectors,
                             sums to 100.0%) and "Retail Portfolio Business Sector
                             Analysis" (13 sectors, sums to 100.0%). Every category_raw
                             we hold appears in exactly one of the two lists.
  T82U FY2025 AR L1039/L1057 "OFFICE PORTFOLIO - TOP 10 TENANTS" then "RETAIL PORTFOLIO
                             - TOP 10 TENANTS", in that order -> ranks 1-10 / 11-20.
  BUOU FY2025 AR L1678/L1704 "Top 10 L&I Tenants of FLCT by GRI" then "Top 10 Commercial
                             Tenants of FLCT by GRI" -> ranks 1-10 / 11-20.

Rank convention matches FY2024, which is already loaded: ranks stay globally unique
within (symbol, financial_year) and basis_segment labels them. Renumbering the second
table back to 1-10 would collide on the prod PK (symbol, financial_year, rank).

NOT touched, verified as correct rather than missed:
  BUOU FY2025 trade_mix   9 rows summing to 100.0% -- a whole-portfolio breakdown that
                          year, not a segmented one
  AW9U / HMN              11-row tenant lists -- genuine top-11, no split

Usage:
  python scripts/db/fix_fy2025_basis_segment.py            # DRY RUN
  python scripts/db/fix_fy2025_basis_segment.py --write
"""
import os, sys, argparse
import psycopg2
from dotenv import load_dotenv

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(ROOT, ".env"))

# T82U FY2025 AR: Office Portfolio Business Sector Analysis (sums to 100.0%)
T82U_OFFICE = {
    "Banking, Insurance and Financial Services", "Technology, Media and Telecommunications",
    "Consultancy / Services", "Real Estate and Property Services",
    "Energy and Natural Resources", "Trading and Investments", "Manufacturing",
    "Government and Government-Linked Offices", "Shipping and Freight Forwarding",
    "Legal", "Pharmaceutical and Healthcare", "Hospitality / Leisure", "Others",
}
# T82U FY2025 AR: Retail Portfolio Business Sector Analysis (sums to 100.0%)
T82U_RETAIL = {
    "Food and Beverage", "Fashion and Accessories", "Leisure and Entertainment",
    "Kids, Gifts and Hobbies", "Sports and Lifestyle", "Supermarket",
    "Beauty and Personal Care", "Jewellery, Watches and Optical",
    "Electronics and Telecommunications", "Fitness", "Home and Furnishings",
    "Education", "Services",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    cn = psycopg2.connect(os.environ["SUPABASE_CONNECTION_STRING"])
    cur = cn.cursor()

    print("=" * 74)
    print("BACKFILL basis_segment, FY2025" + ("  [--write]" if args.write else "  [DRY RUN]"))
    print("=" * 74)

    # ---- 1. T82U FY2025 trade_mix, by category_raw ----
    cur.execute("""select id, category_raw, pct from sgx_reit_trade_mix
                   where symbol='T82U.SI' and financial_year=2025""")
    rows = cur.fetchall()
    plan, unmatched = [], []
    for _id, raw, pct in rows:
        r = (raw or "").strip()
        if r in T82U_OFFICE:
            plan.append((_id, "office", r, pct))
        elif r in T82U_RETAIL:
            plan.append((_id, "retail", r, pct))
        else:
            unmatched.append((r, pct))

    off = [p for p in plan if p[1] == "office"]
    ret = [p for p in plan if p[1] == "retail"]
    print(f"\nT82U FY2025 trade_mix: {len(rows)} rows")
    print(f"   office {len(off):2d} rows, sum {sum(float(p[3]) for p in off):.1f}%")
    print(f"   retail {len(ret):2d} rows, sum {sum(float(p[3]) for p in ret):.1f}%")
    if unmatched:
        print(f"   !! {len(unmatched)} category_raw NOT in either AR list -- NOT tagged:")
        for r, pct in unmatched:
            print(f"      {r!r} ({pct})")

    # every row must land in exactly one segment, and each must sum to ~100
    ok = (not unmatched
          and abs(sum(float(p[3]) for p in off) - 100) < 0.5
          and abs(sum(float(p[3]) for p in ret) - 100) < 0.5)
    print(f"   check: every row assigned AND each segment sums to 100  ->  {'PASS' if ok else 'FAIL'}")

    # ---- 2/3. rank-ordered top_tenant splits ----
    RANKS = [("T82U.SI", 2025, "office", "retail"),
             ("BUOU.SI", 2025, "logistics_industrial", "commercial")]
    tt_plan = []
    for sym, fy, first, second in RANKS:
        cur.execute("""select rank, client_name from sgx_reit_top_tenant
                       where symbol=%s and financial_year=%s order by rank""", (sym, fy))
        rs = cur.fetchall()
        lo = [r for r in rs if r[0] <= 10]
        hi = [r for r in rs if r[0] > 10]
        print(f"\n{sym} FY{fy} top_tenant: {len(rs)} rows")
        print(f"   ranks 1-10   -> {first:22s} ({len(lo)} rows, e.g. {lo[0][1][:34] if lo else '-'})")
        print(f"   ranks 11-20  -> {second:22s} ({len(hi)} rows, e.g. {hi[0][1][:34] if hi else '-'})")
        if len(lo) != 10 or len(hi) != 10:
            print("   !! expected 10 + 10 -- NOT applying to this symbol")
            ok = False
            continue
        tt_plan.append((sym, fy, first, second))

    if not args.write:
        print("\nDRY RUN -- nothing written.")
        return 0
    if not ok:
        print("\nREFUSING to write: a check failed above.")
        return 1

    try:
        for _id, seg, _raw, _pct in plan:
            cur.execute("update sgx_reit_trade_mix set basis_segment=%s where id=%s", (seg, _id))
        for sym, fy, first, second in tt_plan:
            cur.execute("""update sgx_reit_top_tenant set basis_segment=%s
                           where symbol=%s and financial_year=%s and rank<=10""", (first, sym, fy))
            cur.execute("""update sgx_reit_top_tenant set basis_segment=%s
                           where symbol=%s and financial_year=%s and rank>10""", (second, sym, fy))
        cn.commit()
        print(f"\nAPPLIED: {len(plan)} trade_mix rows, {len(tt_plan) * 20} top_tenant rows.")
        print("Next: rebuild sgx_reit_trade_mix_final and sgx_reit_top_tenant_final.")
    except Exception as exc:
        cn.rollback()
        print(f"\nROLLED BACK -- {exc}")
        raise
    return 0


if __name__ == "__main__":
    sys.exit(main())
