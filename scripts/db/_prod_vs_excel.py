import os, json, urllib.request
import pandas as pd
from dotenv import load_dotenv
load_dotenv('.env')

URL = os.environ["SUPABASE_URL"].rstrip("/")
KEY = os.environ["SUPABASE_KEY"]

def prod_get(path):
    req = urllib.request.Request(URL + "/rest/v1/" + path,
        headers={"apikey": KEY, "Authorization": "Bearer " + KEY, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.load(r)

prod = prod_get("sgx_manual_input?select=symbol,financial_year,date&order=symbol,financial_year")
# prod convention check: is financial_year == date.year ?
def yr(d): return pd.to_datetime(d).year
prod_by_date = {(r["symbol"], str(pd.to_datetime(r["date"]).date())): r["financial_year"] for r in prod if r.get("date")}
mismatch_dyear = [r for r in prod if r.get("date") and r["financial_year"] != yr(r["date"])]
print(f"PROD rows: {len(prod)} ; rows where financial_year != date.year: {len(mismatch_dyear)}")
if mismatch_dyear:
    for r in mismatch_dyear[:20]: print("   FY!=date.year:", r["symbol"], r["financial_year"], r["date"])

def nb_fy(d):
    dt = pd.to_datetime(d); return int(dt.year-1 if dt.month<=6 else dt.year)

EXCEL = ["excel/v2 - SGX - FY 2024 - REIT.xlsx", "excel/v2 - SGX - FY 2025 - REIT.xlsx"]
rows = []
for f in EXCEL:
    xl = pd.ExcelFile(f)
    for sh in xl.sheet_names:
        df = pd.read_excel(f, sheet_name=sh, header=None)
        sym = str(df.iloc[0, 1]); date = str(pd.to_datetime(df.iloc[1, 4]).date())
        rows.append((sym, date, nb_fy(date), yr(date)))

print("\n== Excel rows: symbol | date | notebook_FY(Jan-Jun rule) | date.year | in prod? | prod_FY ==")
new_by_date, inter_by_date, conflicts = [], [], []
for sym, date, nbfy, dy in rows:
    key = (sym, date)
    in_prod = key in prod_by_date
    pfy = prod_by_date.get(key)
    tag = ""
    if in_prod:
        inter_by_date.append((sym, date, pfy))
        if pfy != nbfy: tag = f"  <-- FY CONFLICT (notebook says {nbfy}, prod has {pfy})"
        if pfy != nbfy: conflicts.append((sym, date, nbfy, pfy))
    else:
        new_by_date.append((sym, date, nbfy, dy))
    print(f"  {sym:9} {date}  nb={nbfy}  dyear={dy}  {'IN PROD FY'+str(pfy) if in_prod else 'NEW'}{tag}")

print(f"\n== ALREADY IN PROD (same symbol+date) : {len(inter_by_date)} ==")
for s,d,p in inter_by_date: print(f"   {s:9} {d}  prod_FY={p}")
print(f"\n== NOT IN PROD (candidates to upsert) : {len(new_by_date)} ==")
for s,d,nbfy,dy in new_by_date: print(f"   {s:9} {d}  notebook_FY={nbfy}  date.year={dy}")
print(f"\n== FY-LABEL CONFLICTS (notebook rule != prod's stored FY, same period) : {len(conflicts)} ==")
for s,d,nbfy,pfy in conflicts: print(f"   {s:9} {d}  notebook={nbfy}  prod={pfy}")
