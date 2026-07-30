"""Cleanup+retry squeeze for non-SG addresses OpenCage missed (dev DB only; prod untouched).

The residual misses are: multi-lot industrial addresses ("Lot Nos. 205 & 211 ...",
"Plot No. P-12 ..."), name-only POIs (malls/residences with no street), and rows whose
country label was wrong (US-labelled address actually in Canada) so the countrycode filter
blocked the match. For each still-null property we try, in order:
  1) full address + country, FREEFORM (no countrycode lock)  -> catches mislabels
  2) lot/plot/unit-stripped address + country                -> catches industrial parks
  3) property_name + country (POI search)                    -> catches name-only malls
First hit wins, stored in geo_cache under the SAME iso|query key (confidence='cleanup')
so the normal fan-out picks it up. Never fabricate: still-no-match stays NULL.

DRY by default; --write to apply.
"""
import os, sys, re, json, time, argparse, urllib.parse, urllib.request, urllib.error
import psycopg2
from psycopg2.extras import Json, execute_values
from dotenv import load_dotenv

load_dotenv('.env')
KEY = os.environ['GEOCODING_API_KEY']
API = "https://api.opencagedata.com/geocode/v1/json"
SOURCE = "opencage"

ISO = {
    'united states':'us','usa':'us','united states of america':'us','australia':'au',
    'united kingdom':'gb','the united kingdom':'gb','japan':'jp','france':'fr','germany':'de',
    'china':'cn','indonesia':'id','south korea':'kr','vietnam':'vn','netherlands':'nl',
    'the netherlands':'nl','italy':'it','india':'in','malaysia':'my','denmark':'dk',
    'czech republic':'cz','finland':'fi','hong kong sar':'hk','hong kong':'hk','slovakia':'sk',
    'poland':'pl','spain':'es','belgium':'be','ireland':'ie','canada':'ca','philippines':'ph',
    'maldives':'mv','switzerland':'ch','new zealand':'nz',
}
# canonical display name to append to freeform queries
DISPLAY = {'usa':'United States','us':'United States','gb':'United Kingdom','nl':'Netherlands','hk':'Hong Kong'}

def iso_of(country):
    if not country: return None
    c = country.strip().lower()
    return None if '/' in c else ISO.get(c)

def display_country(country):
    c = (country or '').strip()
    cl = c.lower().replace('the ', '')
    if '/' in c: c = c.split('/')[0].strip()          # "United Kingdom/Europe" -> "United Kingdom"
    iso = iso_of(country)
    return DISPLAY.get(iso, c) if iso else c

def cache_key(country, q):
    return f"{iso_of(country) or 'xx'}|{q}"

def clean_address(addr):
    if not addr: return None
    s = addr
    # drop leading company-name prefix like "KSH Distriparks Pvt. Ltd., "
    s = re.sub(r'^[^,]*(?:Pvt\.?\s*Ltd\.?|Sdn\.?\s*Bhd\.?|Pte\.?\s*Ltd\.?)[^,]*,\s*', '', s, flags=re.I)
    # remove Lot/Plot number-lists: "Lot Nos. 205 & 211", "Plot No. P-12", "Lot 2-30, 2-32, 2-34"
    s = re.sub(r'\b(?:Lot|Plot)\s*(?:Nos?\.?)?\s*[\w\-]+(?:\s*[,&]\s*[\w\-]+)*\s*,?\s*', '', s, flags=re.I)
    # remove standalone leading "No. 18", "No.1," unit tokens
    s = re.sub(r'\bNos?\.?\s*[\w\-]+\s*,?\s*', '', s, flags=re.I)
    # drop trailing " Units"
    s = re.sub(r'\bunits?\b', '', s, flags=re.I)
    s = re.sub(r'\s*,\s*,+', ', ', s)          # collapse empty comma segments
    s = re.sub(r'\s{2,}', ' ', s).strip(' ,')
    return s or None

def candidates(country, address, pname):
    """Return list of (query, kind). kind='addr' for street-address queries (trustworthy),
    'poi' for property-name search — used ONLY when there's no address, since a generic
    name can confidently match a same-named place in the wrong city."""
    dc = display_country(country)
    out = []
    if address and address.strip():
        base = address.strip()
        out.append((f"{base}, {dc}" if dc.lower() not in base.lower() else base, 'addr'))
        cl = clean_address(base)
        if cl and cl.lower() != base.lower():
            out.append((f"{cl}, {dc}" if dc.lower() not in cl.lower() else cl, 'addr'))
    else:  # name-only row: POI search is the only option
        if pname and pname.strip():
            out.append((f"{pname.strip()}, {dc}" if dc.lower() not in pname.lower() else pname.strip(), 'poi'))
    seen, uniq = set(), []
    for c, k in out:
        if c and c.lower() not in seen:
            seen.add(c.lower()); uniq.append((c, k))
    return uniq

def opencage(q, iso, retries=4):
    params = {"q": q, "key": KEY, "limit": 1, "no_annotations": 1, "language": "en"}
    if iso:
        params["countrycode"] = iso            # keep country lock -> no wrong-country matches
    url = API + "?" + urllib.parse.urlencode(params)
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "s_reits-geocoder/1.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 402: raise
            if e.code in (429,502,503) and attempt < retries-1:
                time.sleep(2**attempt + 1); continue
            raise
        except Exception:
            if attempt < retries-1: time.sleep(1+attempt); continue
            raise

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    conn = psycopg2.connect(os.environ["SUPABASE_CONNECTION_STRING"]); conn.autocommit = False
    cur = conn.cursor()
    cur.execute("select current_database()"); print("db:", cur.fetchone()[0], "| mode:", "WRITE" if args.write else "DRY")

    # distinct still-null non-SG (country, address, pname), keyed for cache update
    cur.execute("""
        select distinct country, address, property_name,
               coalesce(nullif(trim(address),''), property_name) as q
        from sgx_reit_property
        where country <> 'Singapore' and coordinate_latitude is null
          and coalesce(nullif(trim(address),''), property_name) is not null""")
    work = cur.fetchall()
    if args.limit: work = work[:args.limit]
    print(f"still-null distinct addresses to retry: {len(work)}\n")

    def flush(rows):
        if args.write and rows:
            execute_values(cur,
                "insert into geo_cache (query,latitude,longitude,source,confidence,raw) values %s "
                "on conflict (query) do update set latitude=excluded.latitude, longitude=excluded.longitude, "
                "source=excluded.source, confidence=excluded.confidence, raw=excluded.raw",
                rows); conn.commit()

    batch, ok, miss = [], 0, 0
    for i,(ctry, addr, pname, q) in enumerate(work, 1):
        key = cache_key(ctry, q)
        iso = iso_of(ctry)
        hit = None
        try:
            for cand, kind in candidates(ctry, addr, pname):
                data = opencage(cand, iso)
                res = data.get("results") or []
                top = res[0] if res else None
                g = top.get("geometry") if top else None
                conf = top.get("confidence", 0) if top else 0
                cc = (top.get("components", {}).get("country_code") or "") if top else ""
                # accept only: has geometry, confidence>=5 (skip coarse region blobs),
                # and returned country matches expected iso (guards wrong-country hits)
                if g and g.get("lat") is not None and conf and int(conf) >= 5 \
                   and (not iso or cc.lower() == iso):
                    tag = "cleanup" if kind == 'addr' else "cleanup_poi"
                    hit = (float(g["lat"]), float(g["lng"]), str(conf), top, cand, tag); break
                time.sleep(1.05)
        except urllib.error.HTTPError as e:
            if e.code == 402:
                print(f"  [{i}] QUOTA (402) — committing and stopping."); flush(batch); break
            print(f"  [{i}] HTTP {e.code}"); continue
        except Exception as e:
            print(f"  [{i}] ERR {e}"); continue
        if hit:
            ok += 1
            batch.append((key, hit[0], hit[1], SOURCE, hit[5], Json(hit[3])))
            print(f"  OK  c{hit[2]:>2} [{hit[5]:11}] {hit[0]:.4f},{hit[1]:.4f}  [{hit[4][:42]}]")
        else:
            miss += 1
            print(f"  miss  <- {q[:60]}")
        if len(batch) >= 25: flush(batch); batch = []
        time.sleep(1.05)
    flush(batch)
    print(f"\ncleanup retry: matched={ok} miss={miss}")

    # fan out newly-matched cache -> still-null non-SG property rows
    cur.execute("""select id, country, coalesce(nullif(trim(address),''), property_name) q
                   from sgx_reit_property where country<>'Singapore' and coordinate_latitude is null""")
    props = cur.fetchall()
    cur.execute("select query, latitude, longitude from geo_cache where latitude is not null")
    hits = {qq:(la,lo) for qq,la,lo in cur.fetchall()}
    upd = [(hits[cache_key(c,q)][0], hits[cache_key(c,q)][1], SOURCE, pid)
           for pid,c,q in props if cache_key(c,q) in hits]
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
