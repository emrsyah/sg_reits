"""Apply Evelyn's meeting conventions to raw sgx_reit_financial (income_stmt_metrics +
cash_flow_metrics), then final is rebuilt separately. DRY by default; --write commits JSON+DB.

Formulas (transcript 2026-07-09):
  ebit    = operating_income (NOI)
  depreciation = P&E depreciation (C/F, +) + net FV change of IP (C/F operating sign)
  ebitda  = pretax_income + interest + depreciation
  interest_expense_non_operating = finance costs (positive magnitude)
  funds_from_operation = net_income + depreciation - net_property_sales
  capital_expenditure  = sum of IP-related investing outflows (positive)
  minorities, perpetual_security_holders -> negative (deduction)
Atoms (dep, fv[C/F-signed], fc, capex) hand-extracted from cf_batch*.md (audited C/F statements).
"""
import os, sys, json, glob
import psycopg2
from psycopg2.extras import Json
from dotenv import load_dotenv

WRITE = "--write" in sys.argv
load_dotenv('.env')

# (sym, fy): (dep_pe, fv_cf_signed, finance_costs, capex_sum)
ATOM = {
 ("C2PU.SI",2024):(0,18037,12147,240976), ("BUOU.SI",2024):(57,40753,65658,96561),
 ("K71U.SI",2024):(21,43479,88546,363333), ("T82U.SI",2024):(611,29994,177213,11200),
 ("J69U.SI",2024):(29,-14661,84168,41630), ("ME8U.SI",2024):(42,210826,106609,432611),
 ("M44U.SI",2024):(0,-1491,145905,1027594), ("N2IU.SI",2024):(1072,-141804,227994,64798),
 ("A17U.SI",2024):(0,-10842,271265,227159), ("C38U.SI",2024):(719,-153127,345394,178294),
 ("D5IU.SI",2025):(2187,23224,56020,19368), ("CRPU.SI",2025):(0,7847,23588,1094),
 ("C2PU.SI",2025):(0,-42026,14642,75698), ("J85.SI",2025):(25299,28478,70873,18643),
 ("BMOU.SI",2025):(132,7235,16087,705), ("M1GU.SI",2025):(0,-25779,20198,2173),
 ("XZL.SI",2025):(31505,0,20983,18811), ("ODBU.SI",2025):(0,-1811,18543,30456),
 ("T82U.SI",2025):(906,16896,137141,21015), ("SET.SI",2025):(0,-11340,47554,45092),
 ("P40U.SI",2024):(0,-18777,42095,10559), ("OXMU.SI",2025):(0,-7442,41338,37482),
 ("TS0U.SI",2025):(51,75826,87769,14036), ("N2IU.SI",2025):(678,-154019,220443,56743),
 ("ME8U.SI",2025):(31,16628,105142,238848), ("JYEU.SI",2024):(0,-46831,66153,15244),
 ("K71U.SI",2025):(9,-339700,90354,367608), ("CMOU.SI",2025):(0,40458,29062,45333),
 ("BUOU.SI",2025):(21,-36885,83000,197750), ("Q5T.SI",2025):(1285,27371,23840,4810),
 ("J91U.SI",2025):(0,125097,84919,46105), ("MXNU.SI",2025):(0,188,14103,9644),
 ("DCRU.SI",2025):(0,-22042,29394,40623), ("8C8U.SI",2025):(0,11383,3916,636638),
 ("DCRU.SI",2024):(0,-251601,25122,10766), ("MXNU.SI",2024):(0,-2442,13127,3668),
 ("CY6U.SI",2025):(2599,-426498,92094,188130), ("A17U.SI",2025):(0,-194619,277812,1883480),
 ("T82U.SI",2025):(906,16896,154588,21015), ("SET.SI",2025):(0,-11340,47554,45092),
 ("AU8U.SI",2025):(612,50507,60076,16619), ("DHLU.SI",2025):(0,-10232,9216,35060),
 ("UD1U.SI",2025):(0,81970,8197,18913), ("M44U.SI",2025):(0,67612,156893,410522),
 ("AW9U.SI",2025):(15,3528,20900,3746), ("BTOU.SI",2025):(0,83515,34608,23673),
 ("AJBU.SI",2025):(0,-161648,48943,1207661), ("HMN.SI",2025):(37472,-135726,107484,274594),
 ("C38U.SI",2025):(584,-68117,314704,285040),
 ("J69U.SI",2025):(29,11130,86163,33033), ("O5RU.SI",2024):(772,11531,37455,25425),
 # FY2024 batch (2026-07-28): 21 reports extracted via reit-extract-hybrid, native currency.
 ("AJBU.SI",2024):(0,-120610,51509,1155300), ("AU8U.SI",2024):(706,89733,65369,16845),
 ("AW9U.SI",2024):(12,9578,22773,5859), ("BMOU.SI",2024):(93,4798,19304,4815),
 ("BTOU.SI",2024):(0,187936,48099,40636), ("CMOU.SI",2024):(0,46663,27571,53630),
 ("CRPU.SI",2024):(0,14164,24710,372), ("CY6U.SI",2024):(2239,-331791,90305,237046),
 ("D5IU.SI",2024):(2326,-29823,77109,22672), ("DHLU.SI",2024):(0,-8483,6630,47365),
 ("HMN.SI",2024):(38215,-51106,105352,345835), ("J85.SI",2024):(22576,-5771,68823,168442),
 ("J91U.SI",2024):(0,220180,78185,544114), ("M1GU.SI",2024):(0,9339,21103,21734),
 ("ODBU.SI",2024):(0,-7450,18880,13528), ("OXMU.SI",2024):(0,15063,36035,38197),
 ("Q5T.SI",2024):(0,12421,30352,3454), ("SET.SI",2024):(0,27677,41260,43599),
 ("TS0U.SI",2024):(61,153570,116711,25829), ("UD1U.SI",2024):(0,19375,7412,2443),
 # XZL: hotels held as PPE; PPE revaluation (-11,925k) treated as IP-FV analogue -> fv=11925 (decision 2026-07-28)
 ("XZL.SI",2024):(29215,11925,22832,20462),
 # O5RU AIMS APAC declared FY2025 (period-end 31 Mar 2026), added 2026-07-28
 ("O5RU.SI",2025):(905,-36636,32897,72709),
}

def n(v):
    try: return None if v is None else float(v)
    except: return None

# our base metrics from raw financial.json
base = {}
for p in glob.glob("extracted/*.SI_FY*/financial.json"):
    d = json.load(open(p, encoding="utf-8"))
    inc = d.get("income_stmt_metrics", {}) or {}
    base[(d["symbol"], d["financial_year"])] = {
        "path": p, "inc": inc,
        "noi": n(inc.get("operating_income")), "pretax": n(inc.get("pretax_income")),
        "ni": n(inc.get("net_income")), "nps": n(inc.get("net_property_sales")),
        "mino": n(inc.get("minorities")), "perp": n(inc.get("perpetual_security_holders")),
    }

computed = {}
for key, atoms in ATOM.items():
    dep, fv, fc, capex = (x * 1000 for x in atoms)  # AR tables are $'000 -> full units
    b = base[key]
    depreciation = dep + fv
    ebit = b["noi"]
    ebitda = (b["pretax"] + fc + depreciation) if b["pretax"] is not None else None
    ffo = (b["ni"] + depreciation - (b["nps"] or 0)) if b["ni"] is not None else None
    computed[key] = {
        "ebit": ebit, "ebitda": ebitda, "depreciation": depreciation,
        "interest_expense_non_operating": float(fc),
        "funds_from_operation": ffo, "capital_expenditure": float(capex),
        "minorities": (-abs(b["mino"]) if b["mino"] is not None else None),
        "perpetual_security_holders": (-abs(b["perp"]) if b["perp"] is not None else None),
    }

# sanity print
print(f"{'sym':9}{'fy':5}{'ebit':>13}{'ebitda':>14}{'deprec':>12}{'FFO':>14}{'capex':>13}")
for key in sorted(computed):
    c = computed[key]
    def s(x): return f"{x:,.0f}" if x is not None else "null"
    print(f"{key[0]:9}{key[1]:<5}{s(c['ebit']):>13}{s(c['ebitda']):>14}{s(c['depreciation']):>12}{s(c['funds_from_operation']):>14}{s(c['capital_expenditure']):>13}")

# validate vs her sgx_manual_input (READ ONLY)
conn = psycopg2.connect(os.environ['SUPABASE_CONNECTION_STRING'])
cur = conn.cursor()
cur.execute("select symbol, financial_year, date from sgx_reit_performance")
yr = {(s, fy): str(d)[:4] for s, fy, d in cur.fetchall()}
cur.execute("select symbol, financial_year, date, income_stmt_metrics, cash_flow_metrics from sgx_manual_input")
her = {}
for s, fyd, d, inc, cf in cur.fetchall():
    her[(s, str(d)[:4])] = (inc or {}, cf or {})

print("\n== validation vs her (fields: ebit, ebitda, interest, ffo, capex, minorities, perps) ==")
def cmp(a, b, tol=0.02):
    a, b = n(a), n(b)
    if a is None or b is None: return "-"
    if a == b: return "EXACT"
    if max(abs(a),abs(b)) and abs(a-b)/max(abs(a),abs(b))<=tol: return "close"
    return "DIFF"
for key in sorted(computed):
    hk = (key[0], yr.get(key))
    if hk not in her: continue
    hinc, hcf = her[hk]
    c = computed[key]
    checks = [("ebit",c["ebit"],hinc.get("ebit")),
              ("ebitda",c["ebitda"],hinc.get("ebitda")),
              ("int",c["interest_expense_non_operating"],hinc.get("interest_expense_non_operating")),
              ("ffo",c["funds_from_operation"],hinc.get("funds_from_operation")),
              ("capex",c["capital_expenditure"],hcf.get("capital_expenditure")),
              ("mino",c["minorities"],hinc.get("minorities")),
              ("perp",c["perpetual_security_holders"],hinc.get("perpetual_security_holders"))]
    res = " ".join(f"{nm}:{cmp(mv,hv)}" for nm,mv,hv in checks)
    print(f"  {key[0]} FY{key[1]}: {res}")

if WRITE:
    for key, c in computed.items():
        b = base[key]
        inc = dict(b["inc"])
        inc["ebit"] = c["ebit"]; inc["ebitda"] = c["ebitda"]
        inc["depreciation"] = c["depreciation"]
        inc["interest_expense_non_operating"] = c["interest_expense_non_operating"]
        inc["funds_from_operation"] = c["funds_from_operation"]
        inc["minorities"] = c["minorities"]
        inc["perpetual_security_holders"] = c["perpetual_security_holders"]
        der = set(inc.get("_derived", []) or [])
        der.update(["ebit","ebitda","depreciation","interest_expense_non_operating",
                    "funds_from_operation","capital_expenditure"])
        inc["_derived"] = sorted(der)
        # write JSON
        d = json.load(open(b["path"], encoding="utf-8"))
        d["income_stmt_metrics"] = inc
        cf = d.get("cash_flow_metrics", {}) or {}
        cf["capital_expenditure"] = c["capital_expenditure"]
        ocf = n(cf.get("operating_cash_flow"))
        cf["free_cash_flow"] = (ocf - c["capital_expenditure"]) if ocf is not None else None
        d["cash_flow_metrics"] = cf
        json.dump(d, open(b["path"], "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        # write DB
        cur.execute("update sgx_reit_financial set income_stmt_metrics=%s, cash_flow_metrics=%s "
                    "where symbol=%s and financial_year=%s",
                    (Json(inc), Json(cf), key[0], key[1]))
    conn.commit()
    print("\nWROTE income_stmt_metrics + cash_flow_metrics for", len(computed), "rows.")
cur.close(); conn.close()
print("WRITE =", WRITE)
