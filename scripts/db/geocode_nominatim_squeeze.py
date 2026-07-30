"""Nominatim (OpenStreetMap) fallback for addresses OpenCage still missed (dev only; prod untouched).

Raw OSM/Nominatim parses queries differently than OpenCage and occasionally resolves
addresses OpenCage can't. Free, no key. Respects Nominatim policy: <=1 req/s, real
User-Agent, cache results. Same safety as the OpenCage squeeze: country-locked
(countrycodes=), returned-country validated, POI-name search only for name-only rows.

Only retries the still-NULL non-SG property rows. Stores source='nominatim'
(confidence 'osm:<type>' / 'osm_poi:<type>'). DRY by default; --write to apply.
"""
import os, sys, time, json, argparse, urllib.parse, urllib.request, urllib.error
import psycopg2
from psycopg2.extras import Json, execute_values
from dotenv import load_dotenv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# reuse the exact cleaning / candidate / key helpers from the OpenCage squeeze
from geocode_opencage_squeeze import clean_address, candidates, cache_key, iso_of

load_dotenv('.env')
NOMINATIM = "https://nominatim.openstreetmap.org/search"
SOURCE = "nominatim"
UA = "s_reits-geocoder/1.0 (contact: muhammademir48@gmail.com)"  # Nominatim requires a real UA


def nominatim(q, iso, retries=3):
    params = {"q": q, "format": "jsonv2", "limit": 1, "addressdetails": 1}
    if iso:
        params["countrycodes"] = iso
    url = NOMINATIM + "?" + urllib.parse.urlencode(params)
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (429, 502, 503) and attempt < retries - 1:
                time.sleep(3 * (attempt + 1)); continue
            raise
        except Exception:
            if attempt < retries - 1:
                time.sleep(2); continue
            raise


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    conn = psycopg2.connect(os.environ["SUPABASE_CONNECTION_STRING"]); conn.autocommit = False
    cur = conn.cursor()
    cur.execute("select current_database()"); print("db:", cur.fetchone()[0], "| mode:", "WRITE" if args.write else "DRY")

    cur.execute("""
        select distinct country, address, property_name,
               coalesce(nullif(trim(address),''), property_name) as q
        from sgx_reit_property
        where country <> 'Singapore' and coordinate_latitude is null
          and coalesce(nullif(trim(address),''), property_name) is not null""")
    work = cur.fetchall()
    if args.limit: work = work[:args.limit]
    print(f"still-null distinct to try via OSM: {len(work)}\n")

    def flush(rows):
        if args.write and rows:
            execute_values(cur,
                "insert into geo_cache (query,latitude,longitude,source,confidence,raw) values %s "
                "on conflict (query) do update set latitude=excluded.latitude, longitude=excluded.longitude, "
                "source=excluded.source, confidence=excluded.confidence, raw=excluded.raw",
                rows); conn.commit()

    batch, ok, miss = [], 0, 0
    for i, (ctry, addr, pname, q) in enumerate(work, 1):
        key = cache_key(ctry, q); iso = iso_of(ctry); hit = None
        try:
            for cand, kind in candidates(ctry, addr, pname):
                res = nominatim(cand, iso)
                top = res[0] if res else None
                cc = (top.get("address", {}).get("country_code") or "") if top else ""
                if top and top.get("lat") and (not iso or cc.lower() == iso):
                    typ = top.get("type", "?")
                    tag = (f"osm:{typ}" if kind == 'addr' else f"osm_poi:{typ}")
                    hit = (float(top["lat"]), float(top["lon"]), tag, top, cand); break
                time.sleep(1.1)  # Nominatim: <=1 req/s
        except urllib.error.HTTPError as e:
            print(f"  [{i}] HTTP {e.code} — stopping to respect policy"); flush(batch); break
        except Exception as e:
            print(f"  [{i}] ERR {e}"); continue
        if hit:
            ok += 1
            batch.append((key, hit[0], hit[1], SOURCE, hit[2], Json(hit[3])))
            print(f"  OK  [{hit[2]:16}] {hit[0]:.4f},{hit[1]:.4f}  <- {hit[4][:45]}")
        else:
            miss += 1
            print(f"  miss  <- {q[:60]}")
        if len(batch) >= 20: flush(batch); batch = []
        time.sleep(1.1)
    flush(batch)
    print(f"\nOSM retry: matched={ok} miss={miss}")

    cur.execute("""select id, country, coalesce(nullif(trim(address),''), property_name) q
                   from sgx_reit_property where country<>'Singapore' and coordinate_latitude is null""")
    props = cur.fetchall()
    cur.execute("select query, latitude, longitude from geo_cache where latitude is not null")
    hits = {qq: (la, lo) for qq, la, lo in cur.fetchall()}
    upd = [(hits[cache_key(c, q)][0], hits[cache_key(c, q)][1], SOURCE, pid)
           for pid, c, q in props if cache_key(c, q) in hits]
    print(f"non-SG rows to newly set: {len(upd)}")
    if args.write and upd:
        execute_values(cur,
            "update sgx_reit_property as p set coordinate_latitude=v.lat, coordinate_longitude=v.lng, "
            "coordinate_source=v.src from (values %s) as v(lat,lng,src,id) where p.id=v.id::uuid",
            upd, template="(%s,%s,%s,%s)")
        conn.commit(); print(f"UPDATED {len(upd)} rows (dev only)")
    if not args.write: print("\n(DRY RUN — nothing written.)")
    conn.close()


if __name__ == "__main__":
    main()
