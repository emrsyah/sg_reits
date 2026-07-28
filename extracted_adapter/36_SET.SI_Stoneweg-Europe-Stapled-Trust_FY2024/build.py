import json, os, re

AD = "extracted_adapter/36_SET.SI_Stoneweg-Europe-Stapled-Trust_FY2024"
OUT = "extracted/SET.SI_FY2024"
os.makedirs(OUT, exist_ok=True)
SYM="SET.SI"; FY=2024; CUR="EUR"
raw = json.load(open(f"{AD}/props_raw.json"))

CAT = {"Industrial & Logistics":"Industrial & Logistics","Office":"Office","Specialized":"Specialized"}
def tenure_enum(t):
    return "Freehold" if t.strip().lower()=="freehold" else "Leasehold"
def clean_addr(a):
    a=re.sub(r"\s+"," ",a).strip()
    a=re.sub(r"\s+\d{1,2}$","",a)  # strip trailing footnote digit
    return a

props=[]
for r in raw:
    status="held_for_sale" if r["property_name"].startswith("Via della Fortezza") else "active"
    props.append({
      "symbol":SYM,"financial_year":FY,
      "property_name":r["property_name"].strip(),
      "country":r["country"],
      "category":CAT[r["category_raw"]],
      "category_raw":r["category_raw"],
      "address":clean_addr(r["address"]),
      "ownership":100.0,
      "market_valuation":r["market_valuation"],
      "valuation_date":"2024-12-31","currency":CUR,
      "purchase_price":r["purchase_price"],"purchase_price_currency":CUR,
      "purchase_date":r.get("purchase_date"),
      "net_property_income":None,
      "gross_revenue":r["gross_revenue"],"gross_revenue_currency":CUR,
      "npi_pct":None,"occupancy_rate":r["occupancy_rate"],
      "major_tenants":[],"gla":None,"nla":r["nla"],"gfa":None,"area_unit":"sqm",
      "land_tenure":tenure_enum(r["tenure_raw"]),
      "effective_date":None,"lease_term_years":None,"lease_expiry_date":None,
      "tenure_raw":re.sub(r"\s+"," ",r["tenure_raw"]).strip(),
      "lease_type":r.get("lease_type"),
      "status":status,"flags":[],"source_page":r["page"],
    })
json.dump(props, open(f"{OUT}/properties.json","w"), indent=1, ensure_ascii=False)
print("properties:",len(props),"val sum",f"{sum(p['market_valuation'] for p in props):,.0f}")

# ---------- profile ----------
profile={"symbol":SYM,"sub_sector":"Diversified",
  "management":{"reit_manager":["Stoneweg EREIT Management Pte. Ltd."],
    "trustee":["Perpetual (Asia) Limited"],
    "property_manager":["Stoneweg EU Limited"],
    "sponsor":["SWI Group"]},
  "income_model":"conventional","source_page":225}
json.dump(profile, open(f"{OUT}/profile.json","w"), indent=1, ensure_ascii=False)

# ---------- performance ----------
perf={"symbol":SYM,"financial_year":FY,
 "portfolio_value":2231832000,
 "properties_location":"The Netherlands, France, Italy, Germany, Poland, Denmark, Czech Republic, Slovakia, United Kingdom, Finland (pan-European)",
 "gross_revenue":212919000,"net_property_income":131145000,
 "net_distributable_income":79328000,
 "distribution_paid":None,
 "distribution_basis":"full_payout_no_retention_line",
 "distributable_income_opening":44652000,
 "distribution_cash_paid":84094000,
 "distributable_income_closing":39886000,
 "adjusted_distributable_income":None,
 "dpu":14.106,
 "distribution_record":[
   {"period":"1 Jan 2024 to 30 Jun 2024","dpu":7.050,"ex_date":None,"pay_date":None},
   {"period":"1 Jul 2024 to 31 Dec 2024","dpu":7.056,"ex_date":None,"pay_date":None}],
 "number_of_unitholders":4481,
 "number_of_shareholder_units":562392116,
 "units_to_be_issued":0,"dpu_period_months":12,
 "aggregate_leverage":41.2,"interest_coverage_ratio":3.3,"cost_of_debt":3.2,
 "weighted_avg_debt_maturity":None,
 "nav_per_unit":2.03,"wale":5.1,"portfolio_occupancy":93.5,
 "currency":CUR,"date":"2024-12-31","source_page":5,
 "flags":[
   {"type":"leverage_basis","scope":"aggregate_leverage","note":"Aggregate leverage 41.2% (Property Funds Appendix / MAS basis); net gearing 40.2% (after deducting cash)."},
   {"type":"debt_maturity_basis","scope":"weighted_avg_debt_maturity","note":"Year-end weighted-avg debt maturity not cleanly disclosed on a 31-Dec-2024 basis; the 4.2-year figure quoted is PRO-FORMA after the Jan-2025 €500m green bond refinancing of the €450m Nov-2025 bond (which sat as a current liability at year-end). Left null to avoid a post-year-end figure."},
   {"type":"dpu_basis","scope":"dpu","note":"FY2024 DPU 14.106 Euro cents (7.050 for 1H2024 + 7.056 for 2H2024). Distributions DECLARED/paid during the year (Distribution Statement Note B) = €84,094k covering 2H2023 (7.903c) + 1H2024 (7.050c). 100% payout ratio."}]}
json.dump(perf, open(f"{OUT}/performance.json","w"), indent=1, ensure_ascii=False)

# ---------- top_tenants ----------
tt=[("Nationale Nederlanden Nederland B.V.","The Netherlands",4.4),
    ("Agenzia Del Demanio","Italy",2.8),
    ("Essent Nederland B.V.","The Netherlands",2.2),
    ("Uitvoeringsinstituut werknemersverzekeringen, Hoofdkantoor UWV","The Netherlands",2.1),
    ("Kamer van Koophandel","The Netherlands",2.0),
    ("Motorola Solutions Systems Polska Sp. z o.o.","Poland",2.0),
    ("Thorn Lighting","United Kingdom",2.0),
    ("Nationale Stichting tot Exploitatie van Casinospelen in Nederland","The Netherlands",1.9),
    ("Felss Group","Germany",1.5),
    ("Coolblue B.V.","The Netherlands",1.4)]
top=[{"symbol":SYM,"financial_year":FY,"rank":i+1,"client_name":n,
      "industry":None,"revenue_pct":p,"pct_basis":"headline_rent","source_page":45}
     for i,(n,c,p) in enumerate(tt)]
json.dump(top, open(f"{OUT}/top_tenants.json","w"), indent=1, ensure_ascii=False)

# ---------- trade_mix ----------
TM=[("Transportation - Storage",15.1,"Logistics & Supply Chain Management"),
    ("Wholesale - Retail",14.7,"Other Retail Trades"),
    ("Manufacturing",12.5,"Manufacturing"),
    ("Financial - Insurance",11.2,"Financial & Professional Services"),
    ("Others",9.2,"Other Office Trades"),
    ("Professional - Scientific",8.3,"Financial & Professional Services"),
    ("Public Administration",7.3,"Government Related"),
    ("IT - Communication",6.1,"IT & Telecommunications"),
    ("Entertainment",4.5,"Hospitality & Leisure"),
    ("Administrative",4.1,"Other Office Trades"),
    ("Utility",3.6,"Energy, Mining & Resources"),
    ("Construction",3.4,"Infrastructure, Real Estate & Property Services")]
tm=[{"symbol":SYM,"financial_year":FY,"category":cat,"category_raw":rawl,"pct":p,
     "pct_basis":"headline_rent","source_page":45} for rawl,p,cat in TM]
json.dump(tm, open(f"{OUT}/trade_mix.json","w"), indent=1, ensure_ascii=False)

# ---------- financial ----------
ism={"total_revenue":212919000,"cost_of_revenue":81774000,"gross_income":131145000,
 "operating_income":119465000,"operating_expense":11680000,
 "ebit":119465000.0,"ebitda":124644000.0,
 "pretax_income":55707000,"income_taxes":20226000,"net_income":35481000,
 "non_operating_income_or_loss":-63758000,
 "interest_expense_non_operating":41260000.0,
 "weighted_avg_shares_basic":562392000,"diluted_shares_outstanding":562392000,
 "net_property_sales":599000,"funds_from_operation":62559000.0,
 "unitholders":33153000,"perpetual_security_holders":-2328000,"minorities":None,
 "depreciation":27677000,
 "_derived":["operating_income","ebit","ebitda","non_operating_income_or_loss",
   "interest_expense_non_operating","depreciation","funds_from_operation","capital_expenditure"],
 "revenue_breakdown":[
   {"category":"Logistics / Light Industrial","amount":101999000,"class":"Product/Service Sales"},
   {"category":"Office","amount":104791000,"class":"Product/Service Sales"},
   {"category":"'Others'","amount":6129000,"class":"Product/Service Sales"}],
 "operating_expense_breakdown":[
   {"category":"Manager's fees","amount":5431000,"class":"General & Admin"},
   {"category":"Trustee fees","amount":270000,"class":"General & Admin"},
   {"category":"Other trust expenses","amount":5979000,"class":"Other expenses"}]}
bsm={"total_asset":2322159000,"total_equity":1205022000,"total_liabilities":1117137000,
 "working_capital":-449945000,"total_current_asset":77485000,
 "total_non_current_asset":2244674000,"total_current_liabilities":527430000,
 "total_non_current_liabilities":589707000}
cfm={"operating_cash_flow":70740000,"investing_cash_flow":-18254000,
 "financing_cash_flow":-87745000,"net_cash_flow":-35259000,
 "free_cash_flow":27141000.0,"capital_expenditure":43599000.0}
li=[("revenue","gross_revenue",212919000,"Gross revenue"),
    ("expense","property_operating_expense",81774000,"Property operating expense"),
    ("adjustment","other_income",107000,"Other income"),
    ("expense","finance_costs_net",35996000,"Net finance costs"),
    ("expense","management_fee",5431000,"Manager's fees"),
    ("expense","trustee_fee",270000,"Trustee fees"),
    ("expense","other_trust_expenses",5979000,"Other trust expenses"),
    ("adjustment","net_foreign_exchange_gain",1932000,"Net foreign exchange gain"),
    ("adjustment","gain_on_divestments",599000,"Gain/(loss) on divestments"),
    ("adjustment","fair_value_change_investment_properties",-27677000,"Fair value loss – investment properties"),
    ("adjustment","fair_value_change_derivatives",-2723000,"Fair value loss – derivative financial instruments"),
    ("adjustment","income_tax_expense",-20226000,"Income tax expense")]
line_items=[{"statement":s,"component":c,"amount":a,"label_raw":l,"source_page":145} for s,c,a,l in li]
fin={"symbol":SYM,"financial_year":FY,"currency":CUR,"source_page":145,
 "income_stmt_metrics":ism,"balance_sheet_metrics":bsm,"cash_flow_metrics":cfm,
 "employee_breakdown":{"total_employee":None,"permanent_employee":None,
   "contract_employee":None,"others_employee":None},
 "line_items":line_items}
json.dump(fin, open(f"{OUT}/financial.json","w"), indent=1, ensure_ascii=False)

# recon check
srev=sum(x[2] for x in li if x[0]=="revenue")
sexp=sum(x[2] for x in li if x[0]=="expense")
sadj=sum(x[2] for x in li if x[0]=="adjustment")
print("line_items recon:",srev-sexp+sadj,"== net_income 35,481,000?",srev-sexp+sadj==35481000)

# ---------- property_transactions ----------
def txn(prop,country,buyer,sale,val,pct,date,comp="completed",ttype="divestment",cdate=None,adate=None):
    slug=re.sub(r"[^a-z0-9]+","_",prop.lower()).strip("_")
    return {"symbol":SYM,"financial_year":FY,"type":ttype,"transaction_type":ttype,
      "status":comp,"property_name":prop,"country":country,
      "counterparty":buyer,"sale_price":sale,"valuation":val,
      "gain_loss_pct":pct,"gain_basis":"vs_valuation",
      "currency":CUR,"sale_price_currency":CUR,"valuation_currency":CUR,
      "transaction_date":date,"completed_date":cdate,"announced_date":adate,
      "completion_date":cdate,"valuation_date":val and "2024-06-30" or None,
      "deal_id":f"set.si:{slug}:{ttype}:{FY}",
      "source_type":"annual_report","source_page":39,"announcement_refs":None}
tx=[
 txn("Grójecka 5","Poland","Solida Capital Europe",15900000,14800000,7.5,"2024-03-28",cdate="2024-03-28"),
 txn("Grandinkulma","Finland","Revelon OY",5400000,5600000,-3.6,"2024-04-26",cdate="2024-04-26"),
 txn("Lénine","France","IMODEV Group",3100000,3100000,-0.3,"2024-09-30",cdate="2024-09-30"),
 txn("Via Brigata Padova 19","Italy","PDI Europe S.A.",1800000,1500000,24.1,"2024-04-04",cdate="2024-04-04"),
 txn("Via Rampa Cavalcavia 16-18","Italy","Agenzia del Demanio",5900000,4300000,36.6,"2024-12-19",cdate="2024-12-19"),
 txn("Via della Fortezza 8","Italy","TBC (completed to undisclosed purchaser 5 Mar 2025)",15000000,15100000,-0.7,"2025-03-05",comp="announced",ttype="announced_divestment",cdate="2025-03-05",adate="2024-12-31"),
]
for t in tx:
    if t["property_name"]=="Via della Fortezza 8":
        t["valuation_date"]="2024-06-30"
        t["note"]="Held for sale at 31 Dec 2024 (carried at contracted price €15.0m); binding offer entered 2024, notary deed signed & completed 5 Mar 2025."
json.dump(tx, open(f"{OUT}/property_transactions.json","w"), indent=1, ensure_ascii=False)
print("transactions:",len(tx),"sum completed disposal",
      f"{sum(t['sale_price'] for t in tx if t['status']=='completed'):,.0f}")
print("DONE")
