"""Compare dev sgx_reit_*_final (Postgres) vs prod sgx_reit_* (PostgREST).
Schema (columns + data types) + value normalization on a shared (symbol,FY) row.
Read-only. No writes."""
import os, json, urllib.request, psycopg2
from dotenv import load_dotenv
load_dotenv(".env")

DEV = psycopg2.connect(os.environ["SUPABASE_CONNECTION_STRING"]); C = DEV.cursor()
P = os.environ["SUPABASE_URL"].rstrip("/"); K = os.environ["SUPABASE_KEY"]

PAIRS = [  # (dev_final, prod)
    ("sgx_reit_profile_final", "sgx_reit_profile"),
    ("sgx_reit_performance_final", "sgx_reit_performance"),
    ("sgx_reit_property_final", "sgx_reit_property"),
    ("sgx_reit_top_tenant_final", "sgx_reit_top_tenant"),
    ("sgx_reit_trade_mix_final", "sgx_reit_trade_mix"),
    ("sgx_reit_property_transaction_final", "sgx_reit_property_transaction"),
]

def dev_cols(t):
    C.execute("""select column_name, data_type, udt_name from information_schema.columns
                 where table_name=%s order by ordinal_position""", (t,))
    return {r[0]: (r[1], r[2]) for r in C.fetchall()}


_ALIAS = {
    "int2":"smallint","int4":"integer","int8":"bigint","float4":"real","float8":"double precision",
    "bool":"boolean","varchar":"character varying","bpchar":"character","numeric":"numeric",
    "text":"text","jsonb":"jsonb","json":"json","date":"date",
    "timestamp":"timestamp without time zone","timestamptz":"timestamp with time zone",
    "_text":"array","_int4":"array","_numeric":"array",
}
def _loose_eq(dev_udt, prod_typ):
    if prod_typ is None: return False
    d = _ALIAS.get(dev_udt, dev_udt).lower()
    p = str(prod_typ).lower()
    if d == p: return True
    # numeric family: prod openapi often reports 'number'
    numish = {"numeric","real","double precision","integer","bigint","smallint","number"}
    if d in numish and p in numish: return True
    if d.startswith("character") and p.startswith("character"): return True
    if d == "array" or p == "array": return d == "array" and p == "array"
    return False
# prod schema from OpenAPI
r = urllib.request.Request(P+"/rest/v1/", headers={"apikey":K,"Authorization":"Bearer "+K})
DEFS = json.load(urllib.request.urlopen(r)).get("definitions", {})

def prod_cols(t):
    props = DEFS.get(t, {}).get("properties", {})
    out = {}
    for c, meta in props.items():
        typ = meta.get("format") or meta.get("type")
        out[c] = typ
    return out

def prod_get(t, q):
    url = f"{P}/rest/v1/{t}?{q}"
    rq = urllib.request.Request(url, headers={"apikey":K,"Authorization":"Bearer "+K})
    return json.load(urllib.request.urlopen(rq))

def norm_type(dev_udt):
    # crude normalization for comparison display
    return dev_udt

print("="*90)
print("SCHEMA COMPARISON: dev *_final  vs  prod")
print("="*90)
for dv, pr in PAIRS:
    dc = dev_cols(dv); pc = prod_cols(pr)
    dset, pset = set(dc), set(pc)
    print(f"\n### {dv}  <->  {pr}")
    print(f"    dev cols={len(dc)}  prod cols={len(pc)}")
    only_dev = dset - pset
    only_prod = pset - dset
    if only_dev:  print(f"    DEV-ONLY  ({len(only_dev)}): {sorted(only_dev)}")
    if only_prod: print(f"    PROD-ONLY ({len(only_prod)}): {sorted(only_prod)}")
    common = sorted(dset & pset)
    tdiffs = []
    for c in common:
        dtyp = dc[c][1]  # udt_name
        ptyp = pc[c]
        # map prod openapi types to compare loosely
        if not _loose_eq(dtyp, ptyp):
            tdiffs.append((c, dtyp, ptyp))
    if tdiffs:
        print(f"    TYPE DIFFS ({len(tdiffs)}):")
        for c, d, p in tdiffs:
            print(f"        {c:32} dev={d:16} prod={p}")
    else:
        print("    (no type diffs on common columns)")

DEV.close()
