"""Insert sgx_manual_input rows into PROD (Supabase REST) for a target set of (symbol, FY).
Financials from the colleague's Excel (notebook extract_reit, verbatim); property / top_tenant /
trade_mix from the *_final tables (already SGD-correct — avoids the notebook's market_valuation
double-conversion bug). Prod FY convention now matches the notebook (Jan-Jun -> X-1).

DRY by default; --write POSTs to prod. Restrict to TARGET keys.
"""
import os, sys, re, json, math
import numpy as np
import pandas as pd
import psycopg2
import urllib.request
from dotenv import load_dotenv

WRITE = "--write" in sys.argv
load_dotenv(".env")

EXCEL = ["excel/v2 - SGX - FY 2024 - REIT.xlsx", "excel/v2 - SGX - FY 2025 - REIT.xlsx"]
# the 8 complete rows (symbol, notebook_FY)
TARGET = {("C2PU.SI",2024),("C38U.SI",2025),("A17U.SI",2025),("J69U.SI",2025),
          ("T82U.SI",2025),("K71U.SI",2025),("BUOU.SI",2025),("C2PU.SI",2025)}
# --march: preview the buildable March-end declared-FY rows (Mar-2025 => declared FY2024).
# O5RU absent from Excel; Mar-2026 (declared FY2025) not extracted yet -> excluded.
if "--march" in sys.argv:
    TARGET = {("M44U.SI",2024),("ME8U.SI",2024),("N2IU.SI",2024)}
if "--march2025" in sys.argv:
    TARGET = {("M44U.SI",2025),("ME8U.SI",2025),("N2IU.SI",2025)}

DEV = psycopg2.connect(os.environ["SUPABASE_CONNECTION_STRING"]); DCUR = DEV.cursor()
PURL = os.environ["SUPABASE_URL"].rstrip("/"); PKEY = os.environ["SUPABASE_KEY"]

# ---------- notebook helpers (verbatim) ----------
def none_value_extractor(m):
    return None if (m is None or (isinstance(m, float) and pd.isna(m))) else m
def _int_or_none(v):
    return int(v) if (v is not None and not (isinstance(v, float) and pd.isna(v))) else None
def _reduce_others_keys(df):
    others = df[df.index.str.contains("^[Oo]ther")]
    df = df[~df.index.str.contains("^[Oo]ther")]
    if others.shape[0] > 0:
        df.loc["Others","value"] = int(others["value"].sum()); df.loc["Others","category"] = others["category"].iloc[0]
    return df
def _num(x):
    if not isinstance(x, str): return x
    s = x.strip()
    if s == "" or not any(ch.isdigit() for ch in s): return x
    if re.fullmatch(r"\(?\s*-?[\d,]+(?:\.\d+)?\s*\)?%?", s) is None: return x
    neg = s.startswith("(") and s.rstrip("%").endswith(")")
    core = s.replace("(","").replace(")","").replace(",","").replace("%","").strip()
    try: v = float(core)
    except ValueError: return x
    return -v if neg else v
def financial_year_from_date(date_str):
    d = pd.to_datetime(date_str); return int(d.year - 1 if d.month <= 6 else d.year)
def make_sankey_component(inp):
    lb, org, db, red = "hsl(195, 53%, 79%)","hsl(39, 100%, 50%)","hsl(240, 100%, 50%)","hsl(0, 100%, 50%)"
    links, nodes = [], []
    for rb in inp["revenue_breakdown"]:
        links.append({"source": rb["category"], "target": "Total Revenue", "value": rb["amount"]})
    if inp["gross_income"] >= 0:
        links.append({"source":"Total Revenue","target":"Cost of Revenue","value":inp["cost_of_revenue"]})
        links.append({"source":"Total Revenue","target":"Gross Profit","value":inp["gross_income"]})
        if inp["operating_income"] >= 0:
            links.append({"source":"Gross Profit","target":"Operating Income","value":inp["operating_income"]})
            links.append({"source":"Gross Profit","target":"Operating Expense","value":inp["operating_expense"]})
        else:
            links.append({"source":"Operating Income","target":"Operating Expense","value":-(inp["operating_income"])})
            links.append({"source":"Gross Profit","target":"Operating Expense","value":inp["gross_income"]})
    else:
        links.append({"source":"Total Revenue","target":"Cost of Revenue","value":inp["total_revenue"]})
        links.append({"source":"Gross Profit","target":"Cost of Revenue","value":-(inp["gross_income"])})
        links.append({"source":"Operating Income","target":"Gross Profit","value":-(inp["gross_income"])})
        links.append({"source":"Operating Income","target":"Operating Expense","value":inp["operating_expense"]})
    for oeb in inp["operating_expense_breakdown"]:
        links.append({"source":"Operating Expense","target":oeb["category"],"value":oeb["amount"]})
    for rb in inp["revenue_breakdown"]: nodes.append({"id":rb["category"],"nodeColor":lb})
    nodes += [{"id":"Total Revenue","nodeColor":lb},{"id":"Cost of Revenue","nodeColor":org},
              {"id":"Gross Profit","nodeColor":db if inp["gross_income"]>=0 else red},
              {"id":"Operating Income","nodeColor":db if inp["operating_income"]>=0 else red},
              {"id":"Operating Expense","nodeColor":org}]
    for oeb in inp["operating_expense_breakdown"]: nodes.append({"id":oeb["category"],"nodeColor":org})
    return {"nodes": nodes, "links": links}
def sanitize_for_json(o):
    if isinstance(o, dict): return {k: sanitize_for_json(v) for k,v in o.items()}
    if isinstance(o, list): return [sanitize_for_json(v) for v in o]
    if isinstance(o, float): return None if (math.isnan(o) or math.isinf(o)) else (int(o) if o.is_integer() else o)
    if isinstance(o, (np.generic,)): return sanitize_for_json(o.item())
    return o

_DIST_FIELDS = {"distributable_income":"Distributable income","adjusted_distributable_income":"Adjusted distributable income",
    "distribution_paid":"Distribution paid","end_of_year_distribution":"End-of-year distribution",
    "end_of_year_shareholder_units":"End-of-year shareholder units","units_to_be_issued":"Units to be issued"}

def extract_reit(df):
    df = df.map(_num)
    date = pd.to_datetime(df.iloc[1,4]).strftime("%Y-%m-%d")
    data = df[[0,1]].rename(columns={0:"key",1:"value"}).dropna(subset=["key"]).set_index("key")
    metadata = data.loc["symbol":"currency"].copy().replace({np.nan:None})
    income_stmt = data.loc["total revenue":"FFO"].copy(); income_stmt["value"] = income_stmt["value"].fillna(0)
    revenue_bd = df[[2,3,4]].rename(columns={2:"category",3:"key",4:"value"}).dropna(subset=["key"])
    revenue_bd = revenue_bd.set_index("key").drop(index=["sum","match","Breakdown of: total revenue","Date"], errors="ignore")
    revenue_bd = _reduce_others_keys(revenue_bd); revenue_bd.reset_index(inplace=True)
    expense_bd = df[[5,6,7]].rename(columns={5:"category",6:"key",7:"value"}).dropna(subset=["key"])
    expense_bd = expense_bd.set_index("key").drop(index=["sum","match","Breakdown of: operating expenses"], errors="ignore")
    expense_bd = _reduce_others_keys(expense_bd)
    for ei in list(expense_bd.index):
        if ei in revenue_bd["key"].values or ei == "Others": expense_bd.rename(index={ei: ei+" (expense)"}, inplace=True)
    expense_bd.reset_index(inplace=True); expense_bd["value"] = expense_bd["value"].astype("int")
    bal_sheet = df.iloc[:60,13:15].copy(); bal_sheet.columns=["key","value"]; bal_sheet = bal_sheet.set_index("key")
    col13 = {}
    for k,v in zip(df[13], df[14]):
        if isinstance(k,str) and k.strip() and k.strip() not in col13: col13[k.strip()] = v
    def bs(name): return none_value_extractor(bal_sheet.loc[name].value) if name in bal_sheet.index else None
    def isv(name): return none_value_extractor(income_stmt.loc[name].value) if name in income_stmt.index else None
    basic = col13.get("Weighted average number of ordinary shares in issue (basic)")
    diluted = col13.get("Weighted average number of ordinary shares in issue (diluted)")
    if diluted is None: diluted = bs("Weighted average shares outstanding")
    ebit_cell = income_stmt.loc["ebit"].value; ebitda_cell = income_stmt.loc["ebitda"].value
    dna = income_stmt.loc["depreciation and amortization"].value
    ebitda = ebit_cell + abs(dna) if pd.isna(ebitda_cell) else ebitda_cell
    inp = {"symbol":metadata.loc["symbol"].value,"url":metadata.loc["url"].value,
        "total_revenue":isv("total revenue"),"cost_of_revenue":none_value_extractor(-(income_stmt.loc["cost of revenue"].value)),
        "gross_income":isv("gross income"),"operating_expense":none_value_extractor(-(income_stmt.loc["operating expenses"].value)),
        "operating_income":isv("net operating income"),"non_operating_income_or_loss":isv("net non operating income/(expenses)"),
        "pretax_income":isv("pretax income"),"income_taxes":none_value_extractor(-(income_stmt.loc["tax"].value)),
        "net_income":isv("net income"),"minorities":isv("minorities"),"perpetual_security_holders":isv("perpetual security holders"),
        "unitholders":isv("unitholders"),"interest_expense_non_operating":none_value_extractor(-(income_stmt.loc["non operating interest expense"].value)),
        "ebit":none_value_extractor(ebit_cell),"ebitda":none_value_extractor(ebitda),
        "net_property_sales":isv("gain/(loss) on property sales"),"funds_from_operation":isv("FFO"),
        "basic_shares_outstanding":none_value_extractor(basic),"diluted_shares_outstanding":none_value_extractor(diluted),
        "revenue_breakdown":[{"class":revenue_bd.iloc[i,1],"category":revenue_bd.iloc[i,0],"amount":revenue_bd.iloc[i,2]} for i in range(revenue_bd.shape[0])],
        "operating_expense_breakdown":[{"class":expense_bd.iloc[i,1],"category":expense_bd.iloc[i,0],"amount":int(-(expense_bd.iloc[i,2]))} for i in range(expense_bd.shape[0])]}
    balance_sheet = {"total_current_asset":bs("Current Asset"),"total_non_current_asset":bs("Non-Current Asset"),
        "total_asset":bs("TOTAL ASSET"),"total_current_liabilities":bs("Current Liabilities"),
        "total_non_current_liabilities":bs("Non-Current Liabilities"),"total_liabilities":bs("TOTAL LIABILITIES"),
        "total_equity":bs("TOTAL SHAREHOLDER'S EQUITY"),"working_capital":bs("Working Capital")}
    capex = bs("CAPITAL EXPENDITURE")
    if capex is None and {"Net PP&E (current)","Net PP&E (previous year)","Depreciation expenses (current)"} <= set(bal_sheet.index):
        capex = bal_sheet.loc["Net PP&E (current)"].value - bal_sheet.loc["Net PP&E (previous year)"].value + bal_sheet.loc["Depreciation expenses (current)"].value
    ocf = bs("Cash Flows from Operating Activities")
    cash_flow = {"operating_cash_flow":ocf,"investing_cash_flow":bs("Cash Flows from Investing Activities"),
        "financing_cash_flow":bs("Cash Flows from Financing Activities"),"net_cash_flow":bs("NET INCREASE/DECREASED"),
        "capital_expenditure":none_value_extractor(capex),
        "free_cash_flow":none_value_extractor(ocf-capex if (ocf is not None and capex is not None) else None)}
    distribution_metrics = {k: _int_or_none(col13.get(label)) for k,label in _DIST_FIELDS.items()}
    for k in balance_sheet: balance_sheet[k] = int(balance_sheet[k]) if balance_sheet[k] is not None else None
    for k in ["total_revenue","cost_of_revenue","gross_income","operating_expense","operating_income",
              "non_operating_income_or_loss","pretax_income","income_taxes","net_income","minorities",
              "perpetual_security_holders","unitholders","interest_expense_non_operating","ebit","ebitda",
              "net_property_sales","funds_from_operation","basic_shares_outstanding","diluted_shares_outstanding"]:
        inp[k] = int(inp[k]) if inp[k] is not None else None
    for bd in ["revenue_breakdown","operating_expense_breakdown"]:
        for it in inp[bd]: it["amount"] = int(it["amount"])
    cash_flow = {k:(int(v) if v is not None else None) for k,v in cash_flow.items()}
    employee = None
    loc = np.argwhere(df.values == "TOTAL NUMBER OF EMPLOYEES")
    if len(loc):
        r,c = int(loc[0][0]), int(loc[0][1]); total = df.iloc[r,c+1]
        if pd.notna(total) and total != 0:
            def ev(rr):
                v = df.iloc[rr,c+1]; return int(v) if pd.notna(v) else None
            employee = {"permanent_employee":ev(r-3),"contract_employee":ev(r-2),"others_employee":ev(r-1),"total_employee":int(total)}
    income_copy = inp.copy(); income_copy.pop("symbol"); income_copy.pop("url")
    return {"symbol":inp["symbol"],"financial_year":financial_year_from_date(date),
        "sankey_component":make_sankey_component(inp),"source_url":inp["url"],
        "income_stmt_metrics":income_copy,"balance_sheet_metrics":balance_sheet,"cash_flow_metrics":cash_flow,
        "employee_breakdown":none_value_extractor(employee),
        "updated_on":pd.to_datetime("now").strftime("%Y-%m-%d %H:%M:%S"),"date":date}

# ---------- property / tenant / trademix from *_final (already SGD) ----------
def property_from_final(sym, fy, top_n=20):
    DCUR.execute("select property_name,country,category,ownership,market_valuation,gross_revenue,occupancy_rate "
                 "from sgx_reit_property_final where symbol=%s and financial_year=%s", (sym, fy))
    rows = DCUR.fetchall()
    if not rows: return None, None
    conv = [(n,c,cat,own,mv,gr,occ) for n,c,cat,own,mv,gr,occ in rows]
    conv.sort(key=lambda r: (float(r[5]) if r[5] is not None else float("-inf")), reverse=True)
    top = []
    for name,country,cat,own,mv,gr,occ in conv[:top_n]:
        e = {}
        if country is not None: e["country"]=country
        if cat is not None: e["category"]=cat
        if name is not None: e["name"]=name
        if own is not None and float(own)!=100: e["ownership_pct"]=round(float(own)/100,2)
        if mv is not None: e["valuation"]=int(round(float(mv)))
        if gr is not None: e["gross_income"]=int(round(float(gr)))
        if occ is not None: e["occupancy_rate"]=round(float(occ)/100,2)
        top.append(e)
    counts = {}
    for name,country,cat,own,mv,gr,occ in conv:
        c = country or "Unknown"; k = cat or "Unknown"
        slot = counts.setdefault(c,{}).setdefault(k,[0,0,0])
        slot[0]+=1; slot[1]+=int(round(float(gr))) if gr is not None else 0; slot[2]+=int(round(float(mv))) if mv is not None else 0
    return top, counts
def tenant_from_final(sym, fy, limit=10):
    DCUR.execute("select rank,client_name,industry,revenue_pct from sgx_reit_top_tenant_final where symbol=%s and financial_year=%s",(sym,fy))
    rows = DCUR.fetchall()
    if not rows: return None
    rows.sort(key=lambda r:(r[3] is None, -(float(r[3]) if r[3] is not None else 0.0), r[0]))
    out=[]
    for rank,name,ind,pct in rows[:limit]:
        e={}
        if name is not None: e["client_name"]=name
        if ind is not None: e["industry"]=ind
        e["revenue_pct"]=round(float(pct)/100,2) if pct is not None else None
        out.append(e)
    return out
def trademix_from_final(sym, fy):
    DCUR.execute("select category,pct from sgx_reit_trade_mix_final where symbol=%s and financial_year=%s",(sym,fy))
    rows = DCUR.fetchall()
    if not rows: return None
    agg={}
    for cat,pct in rows:
        if cat is None or pct is None: continue
        agg[cat]=agg.get(cat,0.0)+float(pct)
    if not agg or sum(agg.values())>130: return None
    return {k:round(v/100,2) for k,v in sorted(agg.items(), key=lambda kv:-kv[1])}

def final_fy_for(sym, date):
    """Resolve the financial_year label under which *_final currently stores this
    report, by matching the report DATE in performance_final. Robust to *_final
    being on date.year (pre-rebuild) or declared-FY (post-rebuild)."""
    DCUR.execute("select financial_year from sgx_reit_performance_final "
                 "where symbol=%s and date=%s", (sym, str(pd.to_datetime(date).date())))
    r = DCUR.fetchone()
    return r[0] if r else None

# ---------- build target records ----------
records=[]
for f in EXCEL:
    xl = pd.ExcelFile(f)
    for sh in xl.sheet_names:
        rec = extract_reit(pd.read_excel(f, sheet_name=sh, header=None))
        key = (rec["symbol"], rec["financial_year"])
        if key not in TARGET: continue
        prop_fy = final_fy_for(rec["symbol"], rec["date"])  # *_final label for THIS report (date-matched)
        top, counts = property_from_final(rec["symbol"], prop_fy) if prop_fy is not None else (None, None)
        db_tenant = tenant_from_final(rec["symbol"], prop_fy) if prop_fy is not None else None
        db_trademix = trademix_from_final(rec["symbol"], prop_fy) if prop_fy is not None else None
        ib={}
        if db_tenant is not None: ib["top_10_gri%_customers"]=db_tenant
        if db_trademix is not None: ib["gross_rental_income_by_sectors"]=db_trademix
        if top is not None: ib["property_portfolio_top_20"]=top
        if counts is not None: ib["property_counts_by_country"]=counts
        ib["distribution_metrics"]={k:_int_or_none(  # from excel col13
            None) for k in _DIST_FIELDS}  # placeholder replaced below
        # distribution_metrics already computed in extract? no -> recompute from excel here:
        # (extract_reit didn't attach it; compute inline)
        rec["industry_breakdown"]=ib
        rec["_prop_fy"]=prop_fy; rec["_props"]=len(top) if top else 0
        records.append((key, rec))

# NOTE: distribution_metrics needs the excel col13 values; recompute per sheet cleanly
# (re-read to attach — kept separate to mirror the notebook's _DIST_FIELDS mapping)
def dist_metrics_for(f_sheet):
    f, sh = f_sheet
    df = pd.read_excel(f, sheet_name=sh, header=None).map(_num)
    col13={}
    for k,v in zip(df[13], df[14]):
        if isinstance(k,str) and k.strip() and k.strip() not in col13: col13[k.strip()]=v
    return {k:_int_or_none(col13.get(label)) for k,label in _DIST_FIELDS.items()}

# attach distribution_metrics by re-locating the sheet
sheet_of={}
for f in EXCEL:
    for sh in pd.ExcelFile(f).sheet_names:
        df = pd.read_excel(f, sheet_name=sh, header=None)
        try: sym = str(df.iloc[0,1]); fy = financial_year_from_date(pd.to_datetime(df.iloc[1,4]))
        except Exception: continue
        sheet_of[(sym,fy)] = (f, sh)
for key, rec in records:
    rec["industry_breakdown"]["distribution_metrics"] = dist_metrics_for(sheet_of[key])

records = [(k, sanitize_for_json(r)) for k,r in records]
print(f"target rows built: {len(records)} / {len(TARGET)}")
for key, rec in records:
    ib = rec["industry_breakdown"]
    print(f"  {key[0]:9} FY{key[1]}  date={rec['date']}  props={len(ib.get('property_portfolio_top_20',[]))}  "
          f"ib_keys=[{', '.join(ib.keys())}]  dist={ {k:v for k,v in ib['distribution_metrics'].items() if v is not None} }")

_COLS = ["symbol","financial_year","sankey_component","source_url","income_stmt_metrics",
         "balance_sheet_metrics","cash_flow_metrics","employee_breakdown","industry_breakdown","updated_on","date"]

if not WRITE:
    print("\nDRY RUN — nothing written to prod. Sample income_stmt_metrics (first row):")
    print(json.dumps({k:records[0][1]['income_stmt_metrics'].get(k) for k in
          ['total_revenue','net_income','ebit','ebitda','interest_expense_non_operating','minorities']}, indent=1))
    if "--verify" in sys.argv:
        print("\n--- VERIFY vs PROD (would re-upsert change anything?) ---")
        for key, rec in records:
            sym, fy = key
            q = (f"{PURL}/rest/v1/sgx_manual_input?symbol=eq.{sym.removesuffix('.SI')}&financial_year=eq.{fy}"
                 "&select=financial_year,source_url,income_stmt_metrics,industry_breakdown")
            rq = urllib.request.Request(q, headers={"apikey":PKEY,"Authorization":"Bearer "+PKEY})
            rows = json.load(urllib.request.urlopen(rq))
            if not rows:
                print(f"  {sym:9} FY{fy}  NOT IN PROD (new insert)"); continue
            p = rows[0]
            def prop_n(row): return len((row.get("industry_breakdown") or {}).get("property_portfolio_top_20") or [])
            diffs = []
            for m in ["total_revenue","net_income","ebit","ebitda"]:
                a = rec["income_stmt_metrics"].get(m); b = (p.get("income_stmt_metrics") or {}).get(m)
                if a != b: diffs.append(f"{m}:{b}->{a}")
            if rec["source_url"] != p.get("source_url"): diffs.append("source_url")
            if prop_n(rec) != prop_n(p): diffs.append(f"props:{prop_n(p)}->{prop_n(rec)}")
            print(f"  {sym:9} FY{fy}  {'IDENTICAL (no change)' if not diffs else 'DIFF -> '+', '.join(diffs)}")
else:
    # prod sgx_manual_input keys symbols WITHOUT the .SI suffix; strip only at this
    # boundary (internal rec/TARGET/*_final lookups stay .SI-keyed).
    payload = [{**{c: rec.get(c) for c in _COLS}, "symbol": rec["symbol"].removesuffix(".SI")}
               for _, rec in records]
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(PURL+"/rest/v1/sgx_manual_input", data=body, method="POST",
        headers={"apikey":PKEY,"Authorization":"Bearer "+PKEY,"Content-Type":"application/json",
                 "Prefer":"resolution=merge-duplicates,return=minimal"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            print("PROD insert status:", r.status)
        print(f"Inserted/upserted {len(payload)} rows into prod sgx_manual_input.")
    except urllib.error.HTTPError as e:
        print("HTTP", e.code, "body:", e.read().decode("utf-8","replace")[:800])
DCUR.close(); DEV.close()
