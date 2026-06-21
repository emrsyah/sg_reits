#!/usr/bin/env python3
"""Upload annual-report PDFs to Cloudflare R2 via the REST API (account token).

Uploads exactly the pdf_r2_key values referenced by reit_report (the reports the cockpit
needs). Idempotent: HEADs each key and skips if already present (same size). Object key =
the PDF filename, e.g. '33_OXMU.SI_Prime-US-REIT_FY2025.pdf'.

Env: CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_API_TOKEN, SUPABASE_CONNECTION_STRING.
Usage: python scripts/db/upload_r2.py            # all reit_report keys
       python scripts/db/upload_r2.py --all-pdfs # every annual_reports/*.pdf
"""
import os, sys, glob, pathlib, requests, psycopg2
from dotenv import load_dotenv

ROOT = pathlib.Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")
ACCT = os.environ["CLOUDFLARE_ACCOUNT_ID"]
TOK  = os.environ["CLOUDFLARE_API_TOKEN"]
BUCKET = os.environ.get("R2_BUCKET", "reits-ar")
H = {"Authorization": f"Bearer {TOK}"}
BASE = f"https://api.cloudflare.com/client/v4/accounts/{ACCT}/r2/buckets/{BUCKET}/objects"

def keys_from_db():
    conn = psycopg2.connect(os.environ["SUPABASE_CONNECTION_STRING"]); cur = conn.cursor()
    cur.execute("select pdf_r2_key from reit_report where pdf_r2_key is not null order by 1")
    ks = [r[0] for r in cur.fetchall()]; conn.close(); return ks

def main():
    if "--all-pdfs" in sys.argv:
        keys = sorted(os.path.basename(p) for p in glob.glob(str(ROOT/"annual_reports"/"*.pdf")))
    else:
        keys = keys_from_db()
    print(f"{len(keys)} object(s) to ensure in r2://{BUCKET}")
    up = skip = miss = 0
    for k in keys:
        local = ROOT / "annual_reports" / k
        if not local.exists():
            print(f"  MISSING local file: {k}"); miss += 1; continue
        size = local.stat().st_size
        url = f"{BASE}/{k}"
        head = requests.head(url, headers=H)
        if head.status_code == 200 and head.headers.get("content-length") == str(size):
            skip += 1; continue
        with open(local, "rb") as f:
            r = requests.put(url, headers={**H, "Content-Type": "application/pdf"}, data=f)
        if r.status_code == 200:
            up += 1; print(f"  ✓ {k}  ({size/1e6:.1f} MB)")
        else:
            print(f"  ✗ {k}  HTTP {r.status_code}: {r.text[:150]}")
    print(f"done. uploaded={up} skipped(existing)={skip} missing={miss}")

if __name__ == "__main__":
    main()
