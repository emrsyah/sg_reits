"""PATCH prod sgx_reit_property.latitude/longitude ONLY (no other column touched).

Reads coordinates from dev sgx_reit_property_final (coordinate_latitude/longitude,
double precision) and PATCHes them onto existing prod rows matched on the prod PK
(symbol, financial_year, property_name). Unlike promote_final_to_prod.py this does
NOT delete/re-insert rows — every other prod column is left exactly as-is.

Dev symbols carry '.SI'; prod uses the bare ticker.
DRY by default (reports match rate); --write to apply. Idempotent — safe to re-run.
"""
import os, sys, json, argparse, urllib.parse, urllib.request, urllib.error
import psycopg2
from dotenv import load_dotenv

load_dotenv('.env')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    url = os.environ["SUPABASE_URL"].rstrip("/")
    key = os.environ["SUPABASE_KEY"]
    H = {"apikey": key, "Authorization": "Bearer " + key}

    # ---- dev coordinates ----
    dev = psycopg2.connect(os.environ["SUPABASE_CONNECTION_STRING"])
    cur = dev.cursor()
    cur.execute("""
        select symbol, financial_year, property_name,
               coordinate_latitude, coordinate_longitude
        from sgx_reit_property_final
        where coordinate_latitude is not null""")
    devrows = [(s.removesuffix(".SI"), int(fy), pn, float(la), float(lo))
               for s, fy, pn, la, lo in cur.fetchall()]
    dev.close()
    print(f"dev rows with coordinates: {len(devrows)}")

    # ---- prod keys (paged) ----
    prod = {}
    step, off = 1000, 0
    while True:
        q = f"{url}/rest/v1/sgx_reit_property?select=symbol,financial_year,property_name&limit={step}&offset={off}"
        req = urllib.request.Request(q, headers=H)
        page = json.load(urllib.request.urlopen(req, timeout=60))
        if not page:
            break
        for r in page:
            prod[(r["symbol"], int(r["financial_year"]), r["property_name"])] = True
        off += step
        if len(page) < step:
            break
    print(f"prod property rows: {len(prod)}")

    matched = [d for d in devrows if (d[0], d[1], d[2]) in prod]
    missing = [d for d in devrows if (d[0], d[1], d[2]) not in prod]
    print(f"MATCHED (will patch): {len(matched)}   |   no prod row: {len(missing)}")
    if missing:
        print("  examples of unmatched (left alone):")
        for m in missing[:5]:
            print(f"    {m[0]} FY{m[1]} :: {m[2][:60]}")

    if args.limit:
        matched = matched[: args.limit]

    if not args.write:
        print("\n(DRY RUN — nothing written to prod. Re-run with --write.)")
        return

    ok = err = 0
    for i, (sym, fy, pn, la, lo) in enumerate(matched, 1):
        qs = urllib.parse.urlencode({
            "symbol": "eq." + sym,
            "financial_year": "eq." + str(fy),
            "property_name": "eq." + pn,      # urlencode handles &, spaces, commas
        })
        body = json.dumps({"latitude": la, "longitude": lo}).encode("utf-8")
        req = urllib.request.Request(f"{url}/rest/v1/sgx_reit_property?{qs}", data=body,
                                     method="PATCH",
                                     headers={**H, "Content-Type": "application/json",
                                              "Prefer": "return=minimal"})
        try:
            urllib.request.urlopen(req, timeout=60)
            ok += 1
        except urllib.error.HTTPError as e:
            err += 1
            if err <= 5:
                print(f"  ERR {sym} FY{fy} {pn[:40]}: HTTP {e.code} {e.read().decode('utf-8','replace')[:160]}")
        if i % 250 == 0:
            print(f"  ...{i}/{len(matched)} patched")
    print(f"\nPATCH complete: ok={ok} err={err}")

    # verify
    req = urllib.request.Request(
        f"{url}/rest/v1/sgx_reit_property?select=symbol&latitude=not.is.null",
        headers={**H, "Prefer": "count=exact", "Range": "0-0"})
    r = urllib.request.urlopen(req)
    print("prod rows with latitude now (Content-Range):", r.headers.get("Content-Range"))


if __name__ == "__main__":
    main()
