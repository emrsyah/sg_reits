"""Squeeze pass for SG addresses OneMap couldn't match (dev DB only; prod untouched).

The residual misses are multi-block / multi-unit strings OneMap can't parse:
  "1 & 1A Depot Close", "1, 3 & 5 Changi Business Park Crescent",
  "Blk 4008 - 4012 Ang Mo Kio Avenue 10", "87/89 Science Park Drive",
  "No. 12 Marina Boulevard", "Alexandra Technopark 438A/438B/438C Alexandra Road".
A multi-block property is ONE physical site -> geocode the FIRST block + street,
which lands the pin on the correct street. Marked confidence='first_block' (lower
confidence than an exact/postal hit, but a valid map location).

Only re-tries geo_cache rows still NULL; never re-hits already-matched addresses.
DRY by default; --write to apply.
"""
import os, sys, re, json, time, argparse, urllib.parse, urllib.request, urllib.error
import psycopg2
from psycopg2.extras import Json, execute_values
from dotenv import load_dotenv

load_dotenv('.env')
ONEMAP = "https://www.onemap.gov.sg/api/common/elastic/search"
SOURCE = "onemap"

# a block token: 1, 1A, 4008, 438A, 3A
_BLOCK = r"\d+[A-Za-z]?"
# a contiguous number-list: block (sep block)*  with sep in , & / - – and to
_NUMLIST = re.compile(
    rf"({_BLOCK}(?:\s*(?:[,&/–\-]|and|to)\s*{_BLOCK})*)", re.I)


def first_block_query(q):
    """Derive a single-block query from a multi-block string, or None if unmappable."""
    s = re.sub(r",?\s*singapore\b.*$", "", q, flags=re.I).strip(" ,")  # drop country + trailing postal tail
    if re.match(r"^\s*state land", s, re.I):
        return None  # land-lot legal descriptions aren't geocodable
    s = re.sub(r"^\s*(nos?\.|part)\s*", "", s, flags=re.I).strip()      # strip "No."/"Nos."/"Part"
    keep_blk = bool(re.match(r"^\s*blk\b", s, re.I))
    s2 = re.sub(r"^\s*blk\s*", "", s, flags=re.I)
    m = _NUMLIST.search(s2)
    if not m:
        return None
    first = re.match(_BLOCK, m.group(1)).group(0)          # first block only
    street = s2[m.end():].strip(" ,")                       # text after the number-list
    street = street.split(",")[0].strip()                  # keep first street segment only
    if not street:
        return None
    prefix = "Blk " if keep_blk else ""
    return f"{prefix}{first} {street}".strip()


def onemap(sv, retries=4):
    url = ONEMAP + "?" + urllib.parse.urlencode(
        {"searchVal": sv, "returnGeom": "Y", "getAddrDetails": "Y", "pageNum": 1})
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "s_reits-geocoder/1.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (429, 502, 503) and attempt < retries - 1:
                time.sleep(2 ** attempt); continue
            raise
        except Exception:
            if attempt < retries - 1:
                time.sleep(1 + attempt); continue
            raise


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    conn = psycopg2.connect(os.environ["SUPABASE_CONNECTION_STRING"]); conn.autocommit = False
    cur = conn.cursor()
    cur.execute("select current_database()")
    print("connected db:", cur.fetchone()[0], "| mode:", "WRITE" if args.write else "DRY")

    cur.execute("select query from geo_cache where latitude is null order by query")
    misses = [r[0] for r in cur.fetchall()]
    print(f"NULL cache rows to retry: {len(misses)}\n")

    updates, ok, still, skip = [], 0, 0, 0
    for q in misses:
        fb = first_block_query(q)
        if not fb:
            skip += 1
            print(f"  SKIP (unmappable)         <- {q[:55]}")
            continue
        data = onemap(fb)
        results = (data or {}).get("results") or []
        top = results[0] if results else None
        lat = top and top.get("LATITUDE")
        if top and lat not in (None, "", "NIL"):
            ok += 1
            updates.append((q, float(top["LATITUDE"]), float(top["LONGITUDE"]),
                            SOURCE, "first_block", Json(top)))
            print(f"  OK  {top['LATITUDE']:>9},{top['LONGITUDE']:<10} [{fb[:35]}]  <- {q[:45]}")
        else:
            still += 1
            print(f"  miss  (tried '{fb[:35]}')  <- {q[:45]}")
        time.sleep(0.25)

    print(f"\nfirst_block: matched={ok}  still_miss={still}  unmappable_skip={skip}")

    if args.write and updates:
        execute_values(cur,
            "update geo_cache as g set latitude=v.la, longitude=v.lo, source=v.s, "
            "confidence=v.c, raw=v.r from (values %s) as v(q,la,lo,s,c,r) where g.query=v.q",
            updates, template="(%s,%s,%s,%s,%s,%s::jsonb)")
        conn.commit()
        print(f"updated {len(updates)} geo_cache rows")

        # fan out newly-matched cache -> SG property rows still NULL
        cur.execute("""
            select id, coalesce(nullif(trim(address),''), property_name) as q
            from sgx_reit_property
            where country='Singapore' and coordinate_latitude is null""")
        newly = {q for q, _, _, _, _, _ in updates}
        prop_updates = []
        cur2 = conn.cursor()
        cur2.execute("select query, latitude, longitude from geo_cache where confidence='first_block' and latitude is not null")
        fb_hits = {q: (la, lo) for q, la, lo in cur2.fetchall()}
        for pid, q in cur.fetchall():
            if q in fb_hits:
                prop_updates.append((fb_hits[q][0], fb_hits[q][1], SOURCE, pid))
        if prop_updates:
            execute_values(cur,
                "update sgx_reit_property as p set coordinate_latitude=v.lat, coordinate_longitude=v.lng, "
                "coordinate_source=v.src from (values %s) as v(lat,lng,src,id) where p.id=v.id::uuid",
                prop_updates, template="(%s,%s,%s,%s)")
            conn.commit()
            print(f"UPDATED {len(prop_updates)} more SG property rows (dev only)")
    elif not args.write:
        print("\n(DRY RUN — nothing written.)")
    conn.close()


if __name__ == "__main__":
    main()
