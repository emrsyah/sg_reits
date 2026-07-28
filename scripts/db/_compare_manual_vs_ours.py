"""Cross-check: colleague's Excel financials (what feeds sgx_manual_input via extract_reit)
   vs our raw sgx_reit_financial, for the 10 pilot REITs.

All 10 pilots report SGD -> compare native vs native (no FX). Join on (symbol, statement date),
NOT financial_year (March-FYE trusts are label-offset). Classifies every field diff as:
  EXACT | CONVENTION (expected by-design divergence) | DISCREPANCY (needs attention).

Read-only. Usage: python scripts/db/_compare_manual_vs_ours.py
"""
import os, re, sys
import numpy as np
import pandas as pd
import psycopg2
from dotenv import load_dotenv
load_dotenv(".env")

EXCEL = ["excel/v2 - SGX - FY 2024 - REIT.xlsx", "excel/v2 - SGX - FY 2025 - REIT.xlsx"]
PILOTS = {"C38U","A17U","N2IU","M44U","ME8U","J69U","T82U","K71U","BUOU","C2PU"}

# ---- Excel extract (financials only; verbatim logic from prod_upsert_manual_input.extract_reit) ----
def none_value_extractor(m):
    return None if (m is None or (isinstance(m, float) and pd.isna(m))) else m
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

ISM_KEYS = ["total_revenue","cost_of_revenue","gross_income","operating_expense","operating_income",
    "non_operating_income_or_loss","pretax_income","income_taxes","net_income","minorities",
    "perpetual_security_holders","unitholders","interest_expense_non_operating","ebit","ebitda",
    "net_property_sales","funds_from_operation","basic_shares_outstanding","diluted_shares_outstanding"]

def excel_extract(df):
    df = df.map(_num)
    date = pd.to_datetime(df.iloc[1,4]).strftime("%Y-%m-%d")
    data = df[[0,1]].rename(columns={0:"key",1:"value"}).dropna(subset=["key"]).set_index("key")
    metadata = data.loc["symbol":"currency"].copy().replace({np.nan:None})
    symbol = metadata.loc["symbol"].value; currency = metadata.loc["currency"].value
    income_stmt = data.loc["total revenue":"FFO"].copy(); income_stmt["value"] = income_stmt["value"].fillna(0)
    bal_sheet = df.iloc[:60,13:15].copy(); bal_sheet.columns=["key","value"]; bal_sheet = bal_sheet.set_index("key")
    def bs(name): return none_value_extractor(bal_sheet.loc[name].value) if name in bal_sheet.index else None
    def isv(name): return none_value_extractor(income_stmt.loc[name].value) if name in income_stmt.index else None
    col13 = {}
    for k,v in zip(df[13], df[14]):
        if isinstance(k,str) and k.strip() and k.strip() not in col13: col13[k.strip()] = v
    basic = col13.get("Weighted average number of ordinary shares in issue (basic)")
    diluted = col13.get("Weighted average number of ordinary shares in issue (diluted)")
    if diluted is None: diluted = bs("Weighted average shares outstanding")
    ebit_cell = income_stmt.loc["ebit"].value; ebitda_cell = income_stmt.loc["ebitda"].value
    dna = income_stmt.loc["depreciation and amortization"].value
    ebitda = ebit_cell + abs(dna) if pd.isna(ebitda_cell) else ebitda_cell
    ism = {"total_revenue":isv("total revenue"),"cost_of_revenue":none_value_extractor(-(income_stmt.loc["cost of revenue"].value)),
        "gross_income":isv("gross income"),"operating_expense":none_value_extractor(-(income_stmt.loc["operating expenses"].value)),
        "operating_income":isv("net operating income"),"non_operating_income_or_loss":isv("net non operating income/(expenses)"),
        "pretax_income":isv("pretax income"),"income_taxes":none_value_extractor(-(income_stmt.loc["tax"].value)),
        "net_income":isv("net income"),"minorities":isv("minorities"),"perpetual_security_holders":isv("perpetual security holders"),
        "unitholders":isv("unitholders"),"interest_expense_non_operating":none_value_extractor(-(income_stmt.loc["non operating interest expense"].value)),
        "ebit":none_value_extractor(ebit_cell),"ebitda":none_value_extractor(ebitda),
        "net_property_sales":isv("gain/(loss) on property sales"),"funds_from_operation":isv("FFO"),
        "basic_shares_outstanding":none_value_extractor(basic),"diluted_shares_outstanding":none_value_extractor(diluted)}
    ism = {k:(int(v) if v is not None else None) for k,v in ism.items()}
    balance_sheet = {"total_current_asset":bs("Current Asset"),"total_non_current_asset":bs("Non-Current Asset"),
        "total_asset":bs("TOTAL ASSET"),"total_current_liabilities":bs("Current Liabilities"),
        "total_non_current_liabilities":bs("Non-Current Liabilities"),"total_liabilities":bs("TOTAL LIABILITIES"),
        "total_equity":bs("TOTAL SHAREHOLDER'S EQUITY"),"working_capital":bs("Working Capital")}
    balance_sheet = {k:(int(v) if v is not None else None) for k,v in balance_sheet.items()}
    capex = bs("CAPITAL EXPENDITURE")
    if capex is None and {"Net PP&E (current)","Net PP&E (previous year)","Depreciation expenses (current)"} <= set(bal_sheet.index):
        capex = bal_sheet.loc["Net PP&E (current)"].value - bal_sheet.loc["Net PP&E (previous year)"].value + bal_sheet.loc["Depreciation expenses (current)"].value
    ocf = bs("Cash Flows from Operating Activities")
    cash_flow = {"operating_cash_flow":ocf,"investing_cash_flow":bs("Cash Flows from Investing Activities"),
        "financing_cash_flow":bs("Cash Flows from Financing Activities"),"net_cash_flow":bs("NET INCREASE/DECREASED"),
        "capital_expenditure":none_value_extractor(capex),
        "free_cash_flow":none_value_extractor(ocf-capex if (ocf is not None and capex is not None) else None)}
    cash_flow = {k:(int(v) if v is not None else None) for k,v in cash_flow.items()}
    return symbol, currency, date, ism, balance_sheet, cash_flow

# fields where our-vs-excel divergence is expected (see manual_vs_ours_parity.md section 3/5)
CONVENTION = {
    "ebit":"EBIT def (ours=NOI vs her add-back)","ebitda":"EBITDA def differs",
    "interest_expense_non_operating":"finance-cost composition differs",
    "minorities":"SIGN convention (ours negative)","perpetual_security_holders":"SIGN convention (ours negative)",
    "funds_from_operation":"FFO policy (ours derived/null)","net_property_sales":"disposal-scope differs",
    "capital_expenditure":"CAPEX sign+scope (ours signed outflow)","free_cash_flow":"follows capex",
}
def norm_our_ism(ism):
    d = dict(ism or {})
    if "weighted_avg_shares_basic" in d: d["basic_shares_outstanding"] = d.pop("weighted_avg_shares_basic")
    d.pop("_derived",None); d.pop("depreciation",None)
    return d

def classify(field, a, b):  # a=excel(ref), b=ours
    if a == b: return "EXACT", ""
    # sign-only match
    if field in ("minorities","perpetual_security_holders","capital_expenditure","free_cash_flow") \
       and a is not None and b is not None and a == -b:
        return "CONVENTION", CONVENTION[field]+" [sign-flip, |match|]"
    if field in CONVENTION: return "CONVENTION", CONVENTION[field]
    return "DISCREPANCY", ""

conn = psycopg2.connect(os.environ["SUPABASE_CONNECTION_STRING"]); cur = conn.cursor()
# build (symbol, date) -> our financial blobs
cur.execute("""select f.symbol,p.date,f.currency,f.income_stmt_metrics,f.balance_sheet_metrics,f.cash_flow_metrics
  from sgx_reit_financial f join sgx_reit_performance p on p.symbol=f.symbol and p.financial_year=f.financial_year""")
OURS = {}
for sym,date,ccy,ism,bs,cf in cur.fetchall():
    OURS[(sym.removesuffix('.SI'), str(date))] = (ccy, norm_our_ism(ism), bs or {}, cf or {})
conn.close()

BLOCKS = [("income_stmt", ISM_KEYS), ("balance_sheet", None), ("cash_flow", None)]
summary = []; discrepancies = []
seen = set()
for f in EXCEL:
    xl = pd.ExcelFile(f)
    for sh in xl.sheet_names:
        try: sym, ccy_x, date, ism_x, bs_x, cf_x = excel_extract(pd.read_excel(f, sheet_name=sh, header=None))
        except Exception as e:
            continue
        base = sym.removesuffix('.SI')
        if base not in PILOTS: continue
        if (base,date) in seen: continue
        seen.add((base,date))
        key = (base, date)
        if key not in OURS:
            summary.append((base,date,ccy_x,"NO MATCH IN OURS",0,0,0)); continue
        ccy_o, ism_o, bs_o, cf_o = OURS[key]
        ex=conv=disc=0
        excel_blocks = {"income_stmt":ism_x,"balance_sheet":bs_x,"cash_flow":cf_x}
        our_blocks   = {"income_stmt":ism_o,"balance_sheet":bs_o,"cash_flow":cf_o}
        for bn,_ in BLOCKS:
            xb=excel_blocks[bn]; ob=our_blocks[bn]
            for fld in xb:
                a=xb.get(fld); b=ob.get(fld)
                verdict,note = classify(fld,a,b)
                if verdict=="EXACT": ex+=1
                elif verdict=="CONVENTION": conv+=1
                else:
                    disc+=1
                    discrepancies.append((base,date,f"{bn}.{fld}",a,b,note))
        summary.append((base,date,f"{ccy_x}/{ccy_o}","OK",ex,conv,disc))

print("="*94)
print("CROSS-CHECK: Excel (feeds sgx_manual_input) vs raw sgx_reit_financial — 10 pilot REITs")
print("="*94)
print(f"{'SYM':6}{'DATE':12}{'CCY':10}{'STATUS':16}{'EXACT':>6}{'CONV':>6}{'DISC':>6}")
print("-"*94)
for base,date,ccy,status,ex,conv,disc in sorted(summary):
    print(f"{base:6}{date:12}{ccy:10}{status:16}{ex:>6}{conv:>6}{disc:>6}")

print("\n"+"="*94)
print(f"REAL DISCREPANCIES (excel-ref vs ours), {len(discrepancies)} total — these need attention:")
print("="*94)
if not discrepancies:
    print("  NONE. Every non-exact field is an expected convention/sign divergence.")
for base,date,field,a,b,note in discrepancies:
    print(f"  {base:6} {date}  {field:42} excel={a}  ours={b}")
