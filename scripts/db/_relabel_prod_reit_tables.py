"""Relabel financial_year (declared-FY) in PROD sgx_reit_* tables for the 6 H1-end REITs.

Prod is REST-only. Shift financial_year = financial_year - 1 for the affected symbols,
ascending-year (2024->2023 THEN 2025->2024) so a shifted year never collapses onto an
existing one (critical for the list tables that have many rows per (symbol, fy)).

Values are untouched (label-only fix); prod already holds current values from *_final.
DRY by default; --write applies the PATCHes.
"""
import os, sys, json, urllib.request, urllib.error
from collections import Counter
from dotenv import load_dotenv

WRITE = "--write" in sys.argv
load_dotenv(".env")
PURL = os.environ["SUPABASE_URL"].rstrip("/")
PKEY = os.environ["SUPABASE_KEY"]
H = {"apikey": PKEY, "Authorization": "Bearer " + PKEY}

SYMBOLS = ["M44U", "ME8U", "N2IU", "O5RU", "JYEU", "P40U"]   # bare (prod format)
TABLES = ["sgx_reit_performance", "sgx_reit_property", "sgx_reit_top_tenant",
          "sgx_reit_trade_mix", "sgx_reit_property_transaction"]
YEARS = [2024, 2025]   # ascending — vacate target slot first

def counts(table):
    rows = json.load(urllib.request.urlopen(urllib.request.Request(
        f"{PURL}/rest/v1/{table}?select=symbol,financial_year", headers=H)))
    return Counter((r["symbol"], r["financial_year"]) for r in rows if r["symbol"] in SYMBOLS)

def show(label):
    print(f"\n=== {label} ===")
    for t in TABLES:
        c = counts(t)
        s = ", ".join(f"{sym}:FY{fy}={n}" for (sym, fy), n in sorted(c.items()))
        print(f"  {t:32} {s}")

show("BEFORE (prod)")

if WRITE:
    print("\n=== PATCHing (ascending year) ===")
    inlist = "(" + ",".join(SYMBOLS) + ")"
    for yr in YEARS:                       # 2024 first, then 2025
        for t in TABLES:
            url = f"{PURL}/rest/v1/{t}?symbol=in.{inlist}&financial_year=eq.{yr}"
            body = json.dumps({"financial_year": yr - 1}).encode("utf-8")
            req = urllib.request.Request(url, data=body, method="PATCH",
                headers={**H, "Content-Type": "application/json", "Prefer": "return=minimal"})
            try:
                with urllib.request.urlopen(req, timeout=120) as r:
                    print(f"  {t:32} FY{yr}->FY{yr-1}  status={r.status}")
            except urllib.error.HTTPError as e:
                print(f"  {t:32} FY{yr}->FY{yr-1}  HTTP {e.code}: {e.read().decode('utf-8','replace')[:300]}")
    show("AFTER (prod)")
else:
    print("\n(DRY: no PATCH performed)")
