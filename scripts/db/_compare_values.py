"""Value-level normalization diff: dev *_final vs prod, on a shared (symbol,FY).
Read-only."""
import os, json, urllib.request, psycopg2
from dotenv import load_dotenv
load_dotenv(".env")
DEV = psycopg2.connect(os.environ["SUPABASE_CONNECTION_STRING"]); C = DEV.cursor()
P = os.environ["SUPABASE_URL"].rstrip("/"); K = os.environ["SUPABASE_KEY"]
SYM_SI, SYM_BARE, FY = "M44U.SI", "M44U", 2024

def dev_rows(t, where, args):
    C.execute(f"select * from {t} where {where}", args)
    cols = [d[0] for d in C.description]
    return [dict(zip(cols, r)) for r in C.fetchall()]

def prod_rows(t, q):
    rq = urllib.request.Request(f"{P}/rest/v1/{t}?{q}", headers={"apikey":K,"Authorization":"Bearer "+K})
    return json.load(urllib.request.urlopen(rq))

def show(dv, pv, cols):
    for c in cols:
        a = dv.get(c); b = pv.get(c)
        flag = "" if str(a) == str(b) else "   <-- DIFF"
        # compact jsonb
        sa = json.dumps(a, default=str)[:60] if isinstance(a,(dict,list)) else a
        sb = json.dumps(b, default=str)[:60] if isinstance(b,(dict,list)) else b
        print(f"    {c:30} dev={str(sa):42} prod={sb}{flag}")

print("#"*80); print(f"# PERFORMANCE  {SYM_SI} FY{FY}"); print("#"*80)
d = dev_rows("sgx_reit_performance_final","symbol=%s and financial_year=%s",(SYM_SI,FY))
p = prod_rows("sgx_reit_performance", f"symbol=eq.{SYM_BARE}&financial_year=eq.{FY}")
if d and p:
    cols = sorted(set(d[0]) & set(p[0]))
    show(d[0], p[0], cols)

print("\n"+"#"*80); print(f"# PROPERTY (match by property_name)  {SYM_SI} FY{FY}"); print("#"*80)
d = dev_rows("sgx_reit_property_final","symbol=%s and financial_year=%s",(SYM_SI,FY))
p = prod_rows("sgx_reit_property", f"symbol=eq.{SYM_BARE}&financial_year=eq.{FY}")
print(f"  dev rows={len(d)}  prod rows={len(p)}")
if d and p:
    pmap = {r.get("property_name"): r for r in p}
    match = next((r for r in d if r.get("property_name") in pmap), None)
    if match:
        pm = pmap[match["property_name"]]
        print(f"  matched property: {match['property_name']}")
        cols = sorted(set(match) & set(pm))
        show(match, pm, cols)

print("\n"+"#"*80); print(f"# TOP_TENANT (match by rank)  {SYM_SI} FY{FY}"); print("#"*80)
d = dev_rows("sgx_reit_top_tenant_final","symbol=%s and financial_year=%s",(SYM_SI,FY))
p = prod_rows("sgx_reit_top_tenant", f"symbol=eq.{SYM_BARE}&financial_year=eq.{FY}")
print(f"  dev rows={len(d)}  prod rows={len(p)}")
if d and p:
    pmap = {r.get("rank"): r for r in p}
    match = next((r for r in d if r.get("rank") in pmap), None)
    if match:
        pm = pmap[match["rank"]]; cols = sorted(set(match)&set(pm))
        print(f"  matched rank: {match['rank']}"); show(match, pm, cols)

print("\n"+"#"*80); print(f"# TRADE_MIX (match by category)  {SYM_SI} FY{FY}"); print("#"*80)
d = dev_rows("sgx_reit_trade_mix_final","symbol=%s and financial_year=%s",(SYM_SI,FY))
p = prod_rows("sgx_reit_trade_mix", f"symbol=eq.{SYM_BARE}&financial_year=eq.{FY}")
print(f"  dev rows={len(d)}  prod rows={len(p)}")
if d and p:
    pmap = {r.get("category"): r for r in p}
    match = next((r for r in d if r.get("category") in pmap), None)
    if match:
        pm = pmap[match["category"]]; cols = sorted(set(match)&set(pm))
        print(f"  matched category: {match['category']}"); show(match, pm, cols)

print("\n"+"#"*80); print(f"# PROPERTY_TRANSACTION  {SYM_SI} FY{FY}"); print("#"*80)
d = dev_rows("sgx_reit_property_transaction_final","symbol=%s and financial_year=%s",(SYM_SI,FY))
p = prod_rows("sgx_reit_property_transaction", f"symbol=eq.{SYM_BARE}&financial_year=eq.{FY}")
print(f"  dev rows={len(d)}  prod rows={len(p)}")
if d and p:
    cols = sorted(set(d[0]) & set(p[0]))
    show(d[0], p[0], cols)
DEV.close()
