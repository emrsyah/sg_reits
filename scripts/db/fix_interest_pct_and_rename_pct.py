"""Make interest_pct mean ONE thing, and rename top_tenant.revenue_pct -> pct.

INTEREST_PCT
  Until now null carried two meanings: "100%, by convention" and "not disclosed".
  That convention is unwritten, so a reader cannot tell them apart -- and it was
  already leaking: three partial_divestment rows were null, which is impossible by
  definition. After this, interest_pct is the stake actually transacted and null
  means only "genuinely not determinable".

  Backfill to 1.0: every divestment/acquisition whose property_name carries no stake
  language. Checked by regex over property_name only (notes are prose and produce
  false positives). 180 candidates, exactly 1 flagged -- see AJBU below.

  Three partial_divestment rows resolved from their own citations:
    BUOU 2025  0.101  same deal as BUOU FY2024 -- shares sold to existing minority
                      shareholders reducing FLCT to 89.9% of each of 28 German
                      properties; FY2024 recorded EUR23.3m, FY2025 EUR23.2m on completion
    N2IU 2025  1.0    Festival Walk Tower: 100% of the OFFICE COMPONENT was divested.
                      "partial" here means part of a property, not a part-stake.
    ODBU 2024  1.0    Lowe's and Sam's Club buildings within Hudson Valley Plaza --
                      again 100% of the named assets.

  LEFT NULL deliberately:
    AJBU 2025  "remaining 10.0% interest in KDC SGP 3 and 1.0% interest in KDC SGP 4"
               -- two different stakes collapsed into one row, so no single value is
               correct. Fixing it means splitting the row, which is a separate change.

REVENUE_PCT -> PCT
  Only 143 of 752 rows are a percentage of revenue; the rest are of gross_rental_income,
  headline_rent, npi or annualised_rent. The name asserts a basis the column does not
  have, and pct_basis already states it. sgx_reit_trade_mix already calls it pct.

Usage:
  python scripts/db/fix_interest_pct_and_rename_pct.py            # DRY RUN
  python scripts/db/fix_interest_pct_and_rename_pct.py --write
"""
import os, sys, re, argparse
import psycopg2
from dotenv import load_dotenv

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(ROOT, ".env"))

STAKE_RX = re.compile(
    r"(\d+(?:\.\d+)?\s*%)|\b(stake|remaining|minority|majority|partial|equity interest|interest in)\b",
    re.I)

# (symbol, financial_year, property_name LIKE) -> interest_pct, with the reason
RESOLVED = [
    ("BUOU", 2025, "28 German properties%",              0.101,
     "same deal as FY2024: minority shares bought back, FLCT to 89.9% of each"),
    ("N2IU", 2025, "Festival Walk Tower%",               1.0,
     "100% of the office component; 'partial' = part of a property, not a part-stake"),
    ("ODBU", 2024, "Hudson Valley Plaza%",               1.0,
     "100% of the two named buildings within the plaza"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    cn = psycopg2.connect(os.environ["SUPABASE_CONNECTION_STRING"])
    cur = cn.cursor()

    print("=" * 76)
    print("interest_pct backfill + revenue_pct rename" + ("  [--write]" if args.write else "  [DRY RUN]"))
    print("=" * 76)

    # ---- interest_pct: whole transactions ----
    cur.execute("""select id, symbol, financial_year, property_name, transaction_type
                   from sgx_reit_property_transaction
                   where interest_pct is null
                     and transaction_type in ('divestment','acquisition')""")
    rows = cur.fetchall()
    whole = [r for r in rows if not STAKE_RX.search(r[3] or "")]
    flagged = [r for r in rows if STAKE_RX.search(r[3] or "")]
    print(f"\ninterest_pct -> 1.0 on whole divestments/acquisitions: {len(whole)} of {len(rows)}")
    print(f"  left null, property_name carries stake language: {len(flagged)}")
    for r in flagged:
        print(f"     {r[1]} FY{r[2]}  {str(r[3])[:66]}")

    # ---- interest_pct: the three resolved partials ----
    print(f"\npartial_divestment rows resolved from their citations:")
    resolved_ids = []
    for sym, fy, like, val, why in RESOLVED:
        cur.execute("""select id, property_name from sgx_reit_property_transaction
                       where symbol=%s and financial_year=%s and property_name like %s
                         and interest_pct is null""", (sym, fy, like))
        got = cur.fetchall()
        for _id, pn in got:
            resolved_ids.append((_id, val))
            print(f"   {sym} FY{fy} -> {val}   {str(pn)[:52]}")
            print(f"       {why}")
        if not got:
            print(f"   {sym} FY{fy} -> no matching null row (already set?)")

    cur.execute("""select count(*) from sgx_reit_property_transaction
                   where transaction_type='partial_divestment' and interest_pct is null""")
    print(f"\n  partial_divestment still null after this: "
          f"{cur.fetchone()[0] - len(resolved_ids)} (target 0)")

    # ---- rename ----
    cur.execute("""select column_name from information_schema.columns
                   where table_name='sgx_reit_top_tenant' and column_name in ('revenue_pct','pct')""")
    have = {r[0] for r in cur.fetchall()}
    print(f"\nsgx_reit_top_tenant: revenue_pct present={('revenue_pct' in have)} "
          f"pct present={('pct' in have)}")

    if not args.write:
        print("\nDRY RUN -- nothing written.")
        return 0

    try:
        for r in whole:
            cur.execute("update sgx_reit_property_transaction set interest_pct=1.0 where id=%s", (r[0],))
        for _id, val in resolved_ids:
            cur.execute("update sgx_reit_property_transaction set interest_pct=%s where id=%s", (val, _id))
        if "revenue_pct" in have and "pct" not in have:
            cur.execute("alter table sgx_reit_top_tenant rename column revenue_pct to pct")
        cn.commit()
        print(f"\nAPPLIED: {len(whole)} rows -> 1.0, {len(resolved_ids)} partials resolved, "
              f"revenue_pct renamed to pct.")
        print("Next: build_final_tables.py + promote (both reference revenue_pct).")
    except Exception as exc:
        cn.rollback()
        print(f"\nROLLED BACK -- {exc}")
        raise
    return 0


if __name__ == "__main__":
    sys.exit(main())
