"""Fill the 117 null sgx_reit_top_tenant.industry values.

Checked first: none of the 15 REIT-years involved publishes a per-tenant sector column.
A17U's tables are `Customer | Monthly Gross Revenue (%)`, BTOU's `Tenant | % of Portfolio
GRI`, M44U's `Customer | Gross Revenue (%)`, and so on. (A17U does publish a portfolio-level
"Industry Diversification" chart, but that is trade_mix, not per tenant.) So every value
here is derived from the tenant's own line of business, mapped onto the 15 canonical values
already in the column.

Note this is what the extraction was ALREADY doing for 22 of the 61 populated REIT-years --
A17U FY2025 has industry on all 10 rows from a table with no sector column. This makes the
practice consistent instead of accidental.

4 rows stay NULL because the report withholds the tenant itself and there is nothing to
classify:
    N2IU FY2023 rank 6   'Undisclosed Tenant'
    N2IU FY2024 rank 4   '(Undisclosed tenant)'
    N2IU FY2025 rank 8   '(Undisclosed tenant)'
    MXNU FY2025 rank 7   'Commercial tenant (1)'

Usage:
  python scripts/db/derive_top_tenant_industry.py            # DRY RUN
  python scripts/db/derive_top_tenant_industry.py --write
"""
import os, sys, argparse
import psycopg2
from dotenv import load_dotenv

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(ROOT, ".env"))

CANON = {
    "IT & Telecommunications", "Financial & Professional Services", "Healthcare & Wellness",
    "Other Retail Trades", "Logistics & Supply Chain Management", "Hospitality & Leisure",
    "Departmental Store/Supermarket", "Infrastructure, Real Estate & Property Services",
    "Food & Beverages", "Government Related", "Fashion & Accessories", "Manufacturing",
    "Other Industrial Trades", "Energy, Mining & Resources", "Other Office Trades",
}

IT   = "IT & Telecommunications"
FIN  = "Financial & Professional Services"
HLTH = "Healthcare & Wellness"
RET  = "Other Retail Trades"
LOG  = "Logistics & Supply Chain Management"
HOSP = "Hospitality & Leisure"
DEPT = "Departmental Store/Supermarket"
RE   = "Infrastructure, Real Estate & Property Services"
GOV  = "Government Related"
FASH = "Fashion & Accessories"
MFG  = "Manufacturing"
IND  = "Other Industrial Trades"
NRG  = "Energy, Mining & Resources"

# (symbol, financial_year, rank) -> industry
M = {
 # A17U -- Singapore business/logistics parks
 ("A17U.SI",2024,1):IT,   ("A17U.SI",2024,2):GOV,  ("A17U.SI",2024,3):IT,
 ("A17U.SI",2024,4):FIN,  ("A17U.SI",2024,5):IT,   ("A17U.SI",2024,6):FIN,
 ("A17U.SI",2024,7):IND,  ("A17U.SI",2024,8):FIN,  ("A17U.SI",2024,9):IT,
 ("A17U.SI",2024,10):FIN,
 # BTOU -- US office
 ("BTOU.SI",2024,1):FASH, ("BTOU.SI",2024,2):FIN,  ("BTOU.SI",2024,3):GOV,
 ("BTOU.SI",2024,4):GOV,  ("BTOU.SI",2024,5):FIN,  ("BTOU.SI",2024,6):IT,
 ("BTOU.SI",2024,7):FIN,  ("BTOU.SI",2024,8):HLTH, ("BTOU.SI",2024,9):FIN,
 ("BTOU.SI",2024,10):IT,
 ("BTOU.SI",2025,1):FASH, ("BTOU.SI",2025,2):FIN,  ("BTOU.SI",2025,3):GOV,
 ("BTOU.SI",2025,4):FIN,  ("BTOU.SI",2025,5):GOV,  ("BTOU.SI",2025,6):FIN,
 ("BTOU.SI",2025,7):IT,   ("BTOU.SI",2025,8):LOG,  ("BTOU.SI",2025,9):FIN,
 ("BTOU.SI",2025,10):IT,
 # M1GU -- Singapore industrial / hi-tech
 ("M1GU.SI",2024,1):MFG,  ("M1GU.SI",2024,2):LOG,  ("M1GU.SI",2024,3):LOG,
 ("M1GU.SI",2024,4):HLTH, ("M1GU.SI",2024,5):MFG,  ("M1GU.SI",2024,6):MFG,
 ("M1GU.SI",2024,7):HLTH, ("M1GU.SI",2024,8):MFG,  ("M1GU.SI",2024,9):LOG,
 ("M1GU.SI",2024,10):IT,
 ("M1GU.SI",2025,1):MFG,  ("M1GU.SI",2025,2):LOG,  ("M1GU.SI",2025,3):LOG,
 ("M1GU.SI",2025,4):HLTH, ("M1GU.SI",2025,5):HLTH, ("M1GU.SI",2025,6):MFG,
 ("M1GU.SI",2025,7):MFG,  ("M1GU.SI",2025,8):MFG,  ("M1GU.SI",2025,9):LOG,
 ("M1GU.SI",2025,10):IT,
 # M44U -- pan-Asian logistics
 ("M44U.SI",2023,1):LOG,  ("M44U.SI",2023,2):IT,   ("M44U.SI",2023,3):DEPT,
 ("M44U.SI",2023,4):RET,  ("M44U.SI",2023,5):LOG,  ("M44U.SI",2023,6):RET,
 ("M44U.SI",2023,7):RET,  ("M44U.SI",2023,8):LOG,  ("M44U.SI",2023,9):DEPT,
 ("M44U.SI",2023,10):LOG,
 ("M44U.SI",2025,1):IT,   ("M44U.SI",2025,2):LOG,  ("M44U.SI",2025,3):DEPT,
 ("M44U.SI",2025,4):RET,  ("M44U.SI",2025,5):LOG,  ("M44U.SI",2025,6):RET,
 ("M44U.SI",2025,7):LOG,  ("M44U.SI",2025,8):LOG,  ("M44U.SI",2025,9):LOG,
 ("M44U.SI",2025,10):LOG,
 # N2IU -- Festival Walk / Singapore offices (rank 6 withheld)
 ("N2IU.SI",2023,1):IT,   ("N2IU.SI",2023,2):MFG,  ("N2IU.SI",2023,3):DEPT,
 ("N2IU.SI",2023,4):FIN,  ("N2IU.SI",2023,5):MFG,  ("N2IU.SI",2023,7):IT,
 ("N2IU.SI",2023,8):FIN,  ("N2IU.SI",2023,9):RE,   ("N2IU.SI",2023,10):RE,
 # P40U -- Starhill Global
 ("P40U.SI",2024,1):RE,   ("P40U.SI",2024,2):RE,   ("P40U.SI",2024,3):DEPT,
 ("P40U.SI",2024,4):DEPT,
 # SET -- European commercial
 ("SET.SI",2024,1):FIN,   ("SET.SI",2024,2):GOV,   ("SET.SI",2024,3):NRG,
 ("SET.SI",2024,4):GOV,   ("SET.SI",2024,5):GOV,   ("SET.SI",2024,6):IT,
 ("SET.SI",2024,7):MFG,   ("SET.SI",2024,8):HOSP,  ("SET.SI",2024,9):MFG,
 ("SET.SI",2024,10):RET,
 ("SET.SI",2025,1):FIN,   ("SET.SI",2025,2):NRG,   ("SET.SI",2025,3):GOV,
 ("SET.SI",2025,4):GOV,   ("SET.SI",2025,5):HOSP,  ("SET.SI",2025,6):MFG,
 ("SET.SI",2025,7):IT,    ("SET.SI",2025,8):GOV,   ("SET.SI",2025,9):MFG,
 ("SET.SI",2025,10):RET,
 # UD1U -- European logistics / offices
 ("UD1U.SI",2024,1):RET,  ("UD1U.SI",2024,2):IT,   ("UD1U.SI",2024,3):RET,
 ("UD1U.SI",2024,4):FIN,  ("UD1U.SI",2024,5):MFG,  ("UD1U.SI",2024,6):FIN,
 ("UD1U.SI",2024,7):FIN,  ("UD1U.SI",2024,8):GOV,  ("UD1U.SI",2024,9):IT,
 ("UD1U.SI",2024,10):FIN,
}

WITHHELD = {("N2IU.SI",2023,6), ("N2IU.SI",2024,4), ("N2IU.SI",2025,8), ("MXNU.SI",2025,7)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    cn = psycopg2.connect(os.environ["SUPABASE_CONNECTION_STRING"])
    cur = cn.cursor()

    bad = sorted(set(M.values()) - CANON)
    if bad:
        print("ABORT: values outside the canonical list:", bad)
        return 1

    cur.execute("""select symbol, financial_year, rank, client_name
                   from sgx_reit_top_tenant where industry is null
                   order by symbol, financial_year, rank""")
    rows = cur.fetchall()
    plan, unmapped = [], []
    for sym, fy, rk, name in rows:
        key = (sym, fy, rk)
        if key in WITHHELD:
            continue
        if key in M:
            plan.append((sym, fy, rk, name, M[key]))
        else:
            unmapped.append((sym, fy, rk, name))

    print("=" * 78)
    print("DERIVE top_tenant.industry" + ("  [--write]" if args.write else "  [DRY RUN]"))
    print("=" * 78)
    print(f"\n  null rows        {len(rows)}")
    print(f"  to fill          {len(plan)}")
    print(f"  left null        {len(WITHHELD)}  (tenant identity withheld by the report)")
    print(f"  UNMAPPED         {len(unmapped)}")
    for u in unmapped:
        print(f"     !! {u}")

    from collections import Counter
    print("\n  distribution of the derived values:")
    for k, v in Counter(p[4] for p in plan).most_common():
        print(f"     {k:52s} {v}")
    print("\n  sample:")
    for p in plan[:10]:
        print(f"     {p[0][:5]:6s}{p[1]} {p[2]:<3} {str(p[3])[:44]:44s} -> {p[4]}")

    if not args.write:
        print("\n  DRY RUN -- nothing written.")
        return 0
    if unmapped:
        print("\n  REFUSING to write while rows are unmapped.")
        return 1

    try:
        for sym, fy, rk, _n, ind in plan:
            cur.execute("""update sgx_reit_top_tenant set industry=%s
                           where symbol=%s and financial_year=%s and rank=%s""", (ind, sym, fy, rk))
        cn.commit()
        print(f"\n  APPLIED: {len(plan)} rows.")
        print("  Next: rebuild sgx_reit_top_tenant_final, then promote.")
    except Exception as exc:
        cn.rollback()
        print(f"\n  ROLLED BACK -- {exc}")
        raise
    return 0


if __name__ == "__main__":
    sys.exit(main())
