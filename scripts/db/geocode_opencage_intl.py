"""Geocode all non-Singapore properties via OpenCage (dev DB only; prod untouched).

OpenCage: key in env GEOCODING_API_KEY. Free tier 2,500/day, 1 req/s, results are
permanently storable. Returns WGS-84 everywhere (incl. China -> no GCJ-02 offset).

- Geocode DISTINCT (country, address) once, cached in `geo_cache`, then fan out to all
  matching sgx_reit_property rows (country <> 'Singapore').
- Country field isn't normalized (US/UK/NL variants) -> canonicalize to an ISO country
  code purely for the API `countrycode` filter (improves accuracy); DB column untouched.
- cache key for non-SG = "<iso>|<query>" so it never collides with SG's bare-address keys
  or across countries sharing a property_name.
- Never fabricate: no result / low confidence still stores the coord OpenCage returns but
  records its confidence; a genuine no-match leaves coordinates NULL.

DRY by default; --write to apply. --limit N caps API calls for testing.
"""
import os, sys, json, time, argparse, urllib.parse, urllib.request, urllib.error
import psycopg2
from psycopg2.extras import Json, execute_values
from dotenv import load_dotenv

load_dotenv('.env')
KEY = os.environ['GEOCODING_API_KEY']
API = "https://api.opencagedata.com/geocode/v1/json"
SOURCE = "opencage"

ISO = {
    'united states': 'us', 'usa': 'us', 'united states of america': 'us',
    'australia': 'au', 'united kingdom': 'gb', 'the united kingdom': 'gb',
    'japan': 'jp', 'france': 'fr', 'germany': 'de', 'china': 'cn',
    'indonesia': 'id', 'south korea': 'kr', 'vietnam': 'vn',
    'netherlands': 'nl', 'the netherlands': 'nl', 'italy': 'it', 'india': 'in',
    'malaysia': 'my', 'denmark': 'dk', 'czech republic': 'cz', 'finland': 'fi',
    'hong kong sar': 'hk', 'hong kong': 'hk', 'slovakia': 'sk', 'poland': 'pl',
    'spain': 'es', 'belgium': 'be', 'ireland': 'ie', 'canada': 'ca',
    'philippines': 'ph', 'maldives': 'mv', 'switzerland': 'ch', 'new zealand': 'nz',
}

def iso_of(country):
    if not country:
        return None
    c = country.strip().lower()
    if '/' in c:            # ambiguous e.g. "United Kingdom/Europe" -> no countrycode filter
        return None
    return ISO.get(c)

def cache_key(country, q):
    return f"{iso_of(country) or 'xx'}|{q}"

def opencage(q, iso, retries=4):
    params = {"q": q, "key": KEY, "limit": 1, "no_annotations": 1, "language": "en"}
    if iso:
        params["countrycode"] = iso
    url = API + "?" + urllib.parse.urlencode(params)
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "s_reits-geocoder/1.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (429, 502, 503) and attempt < retries - 1:
                time.sleep(2 ** attempt + 1); continue
            raise
        except Exception:
            if attempt < retries - 1:
                time.sleep(1 + attempt); continue
            raise


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    conn = psycopg2.connect(os.environ["SUPABASE_CONNECTION_STRING"]); conn.autocommit = False
    cur = conn.cursor()
    cur.execute("select current_database()")
    print("db:", cur.fetchone()[0], "| mode:", "WRITE" if args.write else "DRY")

    # existing cache (keys already include the iso| prefix for non-SG)
    cur.execute("select query from geo_cache")
    cached = {r[0] for r in cur.fetchall()}

    cur.execute("""
        select distinct country, coalesce(nullif(trim(address),''), property_name) as q
        from sgx_reit_property
        where country is not null and country <> 'Singapore'
          and coalesce(nullif(trim(address),''), property_name) is not null""")
    work = [(ctry, q, cache_key(ctry, q)) for ctry, q in cur.fetchall()]
    # dedupe by cache key: country-spelling variants (USA / United States) collapse to
    # the same iso|query, and ON CONFLICT can't touch one row twice in a batch.
    seen_k, deduped = set(), []
    for c, q, k in work:
        if k in seen_k:
            continue
        seen_k.add(k); deduped.append((c, q, k))
    todo = [(c, q, k) for c, q, k in deduped if k not in cached]
    if args.limit:
        todo = todo[: args.limit]
    print(f"non-SG distinct: {len(work)} | cached: {len(work)-len([1 for c,q,k in work if k not in cached])} | to geocode: {len(todo)}")

    def flush(rows):
        if not (args.write and rows):
            return
        execute_values(cur,
            "insert into geo_cache (query,latitude,longitude,source,confidence,raw) values %s "
            "on conflict (query) do update set latitude=excluded.latitude, longitude=excluded.longitude, "
            "source=excluded.source, confidence=excluded.confidence, raw=excluded.raw",
            rows)
        conn.commit()

    new_rows, batch, ok, miss = [], [], 0, 0
    for i, (ctry, q, key) in enumerate(todo, 1):
        iso = iso_of(ctry)
        try:
            data = opencage(q, iso)
        except urllib.error.HTTPError as e:
            if e.code == 402:  # OpenCage daily quota exhausted -> stop cleanly, keep progress
                print(f"  [{i}] QUOTA (402) reached — committing progress and stopping. "
                      f"Re-run tomorrow (or with a fresh key) to resume the rest.")
                flush(batch); break
            print(f"  [{i}] HTTP {e.code} for {q[:50]!r}"); continue
        except Exception as e:
            print(f"  [{i}] ERR {e} for {q[:50]!r}"); continue
        results = data.get("results") or []
        g = results[0].get("geometry") if results else None
        if results and g and g.get("lat") is not None and g.get("lng") is not None:
            top = results[0]
            lat, lng = float(g["lat"]), float(g["lng"])
            conf = str(top.get("confidence"))  # OpenCage 0-10 (10=best)
            ok += 1
            row = (key, lat, lng, SOURCE, conf, Json(top))
            if i <= 15 or i % 100 == 0:
                print(f"  [{i}/{len(todo)}] c{conf:>2} {lat:.4f},{lng:.4f} <- {(iso or '--')}|{q[:48]}")
        else:
            miss += 1
            row = (key, None, None, SOURCE, "no_match", Json(data))
            if i <= 15:
                print(f"  [{i}/{len(todo)}] no_match           <- {(iso or '--')}|{q[:48]}")
        new_rows.append(row); batch.append(row)
        if len(batch) >= 50:               # incremental commit -> safe to stop/resume
            flush(batch); print(f"  ...committed {i}/{len(todo)}"); batch = []
        time.sleep(1.05)  # free tier: 1 req/s

    flush(batch)  # final partial batch
    print(f"\ngeocoded now: matched={ok} missed={miss} (cached incrementally)")

    # fan out cache -> non-SG property rows still NULL
    cur.execute("""
        select id, country, coalesce(nullif(trim(address),''), property_name) as q
        from sgx_reit_property where country <> 'Singapore' and coordinate_latitude is null""")
    props = cur.fetchall()
    cur.execute("select query, latitude, longitude from geo_cache where latitude is not null")
    hits = {qq: (la, lo) for qq, la, lo in cur.fetchall()}
    updates = []
    for pid, ctry, q in props:
        h = hits.get(cache_key(ctry, q))
        if h:
            updates.append((h[0], h[1], SOURCE, pid))
    print(f"\nnon-SG property rows to set coordinates: {len(updates)} of {len(props)} still-null rows")
    if updates:
        print("  sample:", updates[:2])
    if args.write and updates:
        execute_values(cur,
            "update sgx_reit_property as p set coordinate_latitude=v.lat, coordinate_longitude=v.lng, "
            "coordinate_source=v.src from (values %s) as v(lat,lng,src,id) where p.id=v.id::uuid",
            updates, template="(%s,%s,%s,%s)")
        conn.commit()
        print(f"UPDATED {len(updates)} non-SG property rows (dev only)")
    if not args.write:
        print("\n(DRY RUN — nothing written.)")
    conn.close()


if __name__ == "__main__":
    main()
