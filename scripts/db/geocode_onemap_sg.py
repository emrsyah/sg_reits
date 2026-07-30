"""Geocode Singapore properties via OneMap (dev DB only; prod untouched).

OneMap search API is free, needs NO token for geocoding, returns WGS-84 lat/long.
  GET https://www.onemap.gov.sg/api/common/elastic/search?searchVal=..&returnGeom=Y&getAddrDetails=Y

Strategy:
  - Geocode DISTINCT addresses once, cached in table `geo_cache`, then fan out to all
    matching sgx_reit_property rows (country='Singapore'). Never re-hit the API for a
    string already in cache.
  - Query priority: address -> fallback property_name (both + 'Singapore').
  - Never fabricate: no/'0 results' match -> leave coordinates NULL (not written).

Writes (dev only):
  geo_cache(query, latitude, longitude, source, confidence, raw, created_at)
  sgx_reit_property.coordinate_latitude/longitude/source  for SG rows that matched.

DRY by default; pass --write to apply. --limit N to cap API calls while testing.
"""
import os, sys, re, json, time, argparse, urllib.parse, urllib.request, urllib.error
import psycopg2
from psycopg2.extras import Json, execute_values
from dotenv import load_dotenv

load_dotenv('.env')
ONEMAP = "https://www.onemap.gov.sg/api/common/elastic/search"
SOURCE = "onemap"
_POSTAL = re.compile(r"\b(\d{6})\b")


def candidates(q):
    """Ordered OneMap search variants for one address, best-key-first.
    OneMap resolves a 6-digit SG postal code most reliably; a trailing
    ', Singapore' / country tail and comma-separated postals hurt matching."""
    cands = []
    m = _POSTAL.search(q)
    if m:
        cands.append(m.group(1))                       # postal code alone (strongest)
    cleaned = re.sub(r",?\s*singapore\b", "", q, flags=re.I).strip(" ,")
    cleaned = re.sub(r"\s+\d{6}$", "", cleaned).strip(" ,")  # drop trailing postal too
    if cleaned and cleaned.lower() != q.lower():
        cands.append(cleaned)
    cands.append(q)                                    # original as last resort
    # de-dupe preserving order
    seen, out = set(), []
    for c in cands:
        if c and c.lower() not in seen:
            seen.add(c.lower()); out.append(c)
    return out


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="apply to dev DB (default: dry run)")
    ap.add_argument("--limit", type=int, default=0, help="cap distinct addresses geocoded (0=all)")
    return ap.parse_args()


def _query_onemap(sv, retries=4):
    url = ONEMAP + "?" + urllib.parse.urlencode(
        {"searchVal": sv, "returnGeom": "Y", "getAddrDetails": "Y", "pageNum": 1})
    for attempt in range(retries):
        req = urllib.request.Request(url, headers={"User-Agent": "s_reits-geocoder/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (429, 502, 503) and attempt < retries - 1:
                time.sleep(2 ** attempt)  # 1,2,4,8s backoff
                continue
            raise


def onemap_search(q):
    """Try ordered variants (postal-first). Return (lat, lng, confidence, raw)
    or (None, None, 'no_match', last_raw). confidence encodes which variant hit."""
    last = None
    for idx, sv in enumerate(candidates(q)):
        data = _query_onemap(sv)
        last = data
        results = data.get("results") or []
        if results:
            top = results[0]
            lat, lng = top.get("LATITUDE"), top.get("LONGITUDE")
            if lat not in (None, "", "NIL") and lng not in (None, "", "NIL"):
                # postal-hit = high; single street/building result = exact; else multi
                if idx == 0 and _POSTAL.fullmatch(sv):
                    conf = "postal"
                elif data.get("found", 0) == 1:
                    conf = "exact"
                else:
                    conf = "multi"
                return float(lat), float(lng), conf, top
        time.sleep(0.2)
    return None, None, "no_match", last


def main():
    args = parse_args()
    conn = psycopg2.connect(os.environ["SUPABASE_CONNECTION_STRING"])
    conn.autocommit = False
    cur = conn.cursor()
    cur.execute("select current_database()")
    print("connected db:", cur.fetchone()[0], "| mode:", "WRITE" if args.write else "DRY")

    # --- geo_cache table (dev) ---
    if args.write:
        cur.execute("""
            create table if not exists public.geo_cache (
                query       text primary key,
                latitude    numeric,
                longitude   numeric,
                source      text,
                confidence  text,
                raw         jsonb,
                created_at  timestamptz default now()
            )""")
        conn.commit()

    # existing cache
    cached = {}
    cur.execute("select to_regclass('public.geo_cache')")
    if cur.fetchone()[0]:
        cur.execute("select query, latitude, longitude, confidence from geo_cache")
        cached = {q: (la, lo, c) for q, la, lo, c in cur.fetchall()}

    # distinct SG queries to geocode: prefer address, fallback property_name
    cur.execute("""
        select distinct coalesce(nullif(trim(address),''), property_name) as q
        from sgx_reit_property
        where country = 'Singapore'
          and coalesce(nullif(trim(address),''), property_name) is not null""")
    queries = [r[0] for r in cur.fetchall()]
    todo = [q for q in queries if q not in cached]
    if args.limit:
        todo = todo[: args.limit]
    print(f"SG distinct queries: {len(queries)} | cached: {len(queries)-len([q for q in queries if q not in cached])} "
          f"| to geocode now: {len(todo)}")

    # --- geocode loop (rate-limit friendly) ---
    new_rows, ok, miss = [], 0, 0
    for i, q in enumerate(todo, 1):
        try:
            lat, lng, conf, raw = onemap_search(q)
        except urllib.error.HTTPError as e:
            print(f"  [{i}] HTTP {e.code} for {q!r} — skipping"); continue
        except Exception as e:
            print(f"  [{i}] ERR {e} for {q!r} — skipping"); continue
        if lat is not None:
            ok += 1
        else:
            miss += 1
        cached[q] = (lat, lng, conf)
        new_rows.append((q, lat, lng, SOURCE, conf, Json(raw)))
        if i <= 15 or i % 50 == 0:
            print(f"  [{i}/{len(todo)}] {conf:7} {str(lat):>10},{str(lng):<10} <- {q[:60]}")
        time.sleep(0.25)  # ~4/s, well under OneMap's ~250/min

    print(f"\ngeocoded now: matched={ok} missed={miss}")

    if args.write and new_rows:
        execute_values(cur,
            "insert into geo_cache (query,latitude,longitude,source,confidence,raw) values %s "
            "on conflict (query) do update set latitude=excluded.latitude, longitude=excluded.longitude, "
            "source=excluded.source, confidence=excluded.confidence, raw=excluded.raw",
            new_rows)
        conn.commit()
        print(f"cached {len(new_rows)} rows in geo_cache")

    # --- fan out cache -> property rows (SG, matched only) ---
    cur.execute("""
        select id, coalesce(nullif(trim(address),''), property_name) as q
        from sgx_reit_property where country = 'Singapore'""")
    prop = cur.fetchall()
    updates = []
    for pid, q in prop:
        hit = cached.get(q)
        if hit and hit[0] is not None:
            updates.append((hit[0], hit[1], SOURCE, pid))
    print(f"\nproperty rows to set coordinates: {len(updates)} of {len(prop)} SG rows")
    if updates:
        print("  sample:", updates[:3])
    if args.write and updates:
        execute_values(cur,
            "update sgx_reit_property as p set coordinate_latitude=v.lat, coordinate_longitude=v.lng, "
            "coordinate_source=v.src from (values %s) as v(lat,lng,src,id) where p.id=v.id::uuid",
            updates, template="(%s,%s,%s,%s)")
        conn.commit()
        print(f"UPDATED {len(updates)} SG property rows (dev only).")

    if not args.write:
        print("\n(DRY RUN — nothing written. Re-run with --write.)")
    conn.close()


if __name__ == "__main__":
    main()
