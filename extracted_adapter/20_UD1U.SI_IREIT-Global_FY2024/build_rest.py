import json
D=r"C:\Users\emirsyah\supertype\s_reits\extracted\UD1U.SI_FY2024"
def w(name,obj): json.dump(obj,open(D+"\\"+name,"w",encoding="utf-8"),ensure_ascii=False,indent=2)
K=1000

financial={
 "symbol":"UD1U.SI","financial_year":2024,"currency":"EUR",
 "income_stmt_metrics":{
   "total_revenue":75573*K,"cost_of_revenue":22068*K,"gross_income":53505*K,
   "operating_income":46190*K,"operating_expense":7315*K,
   "ebit":46190*K,"ebitda":37215*K,
   "pretax_income":10428*K,"income_taxes":1825*K,"net_income":8603*K,
   "non_operating_income_or_loss":-35762*K,
   "interest_expense_non_operating":7412*K,
   "weighted_avg_shares_basic":1344838*K,"diluted_shares_outstanding":1344838*K,
   "net_property_sales":-224*K,"funds_from_operation":28202*K,
   "unitholders":8603*K,"perpetual_security_holders":None,"minorities":None,
   "revenue_breakdown":[
     {"category":"base_rental","amount":51946*K,"class":"Product/Service Sales"},
     {"category":"service_charge","amount":10116*K,"class":"Other income"},
     {"category":"carpark_income","amount":3036*K,"class":"Other income"},
     {"category":"other_income","amount":10475*K,"class":"Other income"},
   ],
   "operating_expense_breakdown":[
     {"category":"management_fee","amount":2942*K,"class":"General & Admin"},
     {"category":"trustee_fee","amount":195*K,"class":"General & Admin"},
     {"category":"administrative_costs","amount":1535*K,"class":"General & Admin"},
     {"category":"other_trust_expenses","amount":2036*K,"class":"Other expenses"},
     {"category":"divestment_acquisition_fees","amount":607*K,"class":"Other expenses"},
   ],
   "_derived":["ebit","ebitda","depreciation","funds_from_operation","capital_expenditure",
               "interest_expense_non_operating","non_operating_income_or_loss","operating_income"],
   "depreciation":19375*K,
 },
 "balance_sheet_metrics":{
   "total_asset":961389*K,"total_equity":528655*K,"total_liabilities":432734*K,
   "total_current_asset":86447*K,"total_non_current_asset":874942*K,
   "total_current_liabilities":29278*K,"total_non_current_liabilities":403456*K,
   "working_capital":57169*K,
 },
 "cash_flow_metrics":{
   "operating_cash_flow":48333*K,"investing_cash_flow":23081*K,
   "financing_cash_flow":-45362*K,"net_cash_flow":26052*K,
   "free_cash_flow":45890*K,"capital_expenditure":2443*K,
 },
 "employee_breakdown":None,
 "line_items":[
   {"statement":"revenue","component":"gross_revenue","amount":75573*K,"label_raw":"Gross revenue (Note 3.2)","source_page":175},
   {"statement":"expense","component":"property_operating_expenses","amount":22068*K,"label_raw":"Property operating expenses (Note 3.3)","source_page":175},
   {"statement":"adjustment","component":"finance_income","amount":1026*K,"label_raw":"Finance income","source_page":175},
   {"statement":"expense","component":"finance_costs","amount":7412*K,"label_raw":"Finance costs (Note 3.4)","source_page":175},
   {"statement":"expense","component":"management_fee_base","amount":2942*K,"label_raw":"Management fees (Note 3.5)","source_page":175},
   {"statement":"expense","component":"trustee_fee","amount":195*K,"label_raw":"Trustee's fees (Note 3.5(b))","source_page":175},
   {"statement":"expense","component":"administrative_costs","amount":1535*K,"label_raw":"Administrative costs","source_page":175},
   {"statement":"expense","component":"trust_expenses","amount":2036*K,"label_raw":"Other trust expenses (Note 3.6)","source_page":175},
   {"statement":"expense","component":"acquisition_divestment_fees","amount":607*K,"label_raw":"Divestment/Acquisition fees and related costs","source_page":175},
   {"statement":"adjustment","component":"fv_derivatives","amount":-10001*K,"label_raw":"Change in fair value of financial derivatives","source_page":175},
   {"statement":"adjustment","component":"fair_value_change_investment_properties","amount":-19375*K,"label_raw":"Change in fair value of investment properties (Note 2.4)","source_page":175},
   {"statement":"adjustment","component":"taxation","amount":-1825*K,"label_raw":"Income tax expense (Note 3.7.1)","source_page":175},
 ],
 "source_page":175,
}
w("financial.json",financial)

# reconciliation check
li=financial["line_items"]
srev=sum(x["amount"] for x in li if x["statement"]=="revenue")
sexp=sum(x["amount"] for x in li if x["statement"]=="expense")
sadj=sum(x["amount"] for x in li if x["statement"]=="adjustment")
print("STR recon:",(srev-sexp+sadj)//K,"= net_income", financial["income_stmt_metrics"]["net_income"]//K)

performance={
 "symbol":"UD1U.SI","financial_year":2024,
 "portfolio_value":857333*K,
 "properties_location":"Germany, Spain, France",
 "gross_revenue":75573*K,"net_property_income":53505*K,
 "net_distributable_income":28409*K,"distribution_paid":25568*K,
 "adjusted_distributable_income":None,"distribution_basis":"partial_retention_for_working_capital",
 "dpu":1.90,
 "distribution_record":[
   {"period":"01/01/2024 to 30/06/2024","dpu":0.96,"ex_date":None,"pay_date":None},
   {"period":"01/07/2024 to 31/12/2024","dpu":0.94,"ex_date":None,"pay_date":None},
 ],
 "number_of_unitholders":None,"number_of_shareholder_units":1344838*K,
 "aggregate_leverage":None,"interest_coverage_ratio":7.6,"cost_of_debt":1.9,
 "weighted_avg_debt_maturity":1.7,"nav_per_unit":0.39,"wale":None,
 "portfolio_occupancy":None,"dpu_period_months":12,
 "currency":"EUR","date":"2024-12-31","source_page":22,
 "flags":[
   "Currency EUR. DPU 1.90 EUR cents (H1 0.96 + H2 0.94). portfolio_value=857,333k = independent valuation total (Note 2.4a); carrying amount incl right-of-use assets = 863,708k. net_distributable_income=28,409k = Amount available for distribution (Consolidated Statement of Distribution p176); 2,841k retained for working capital. nav_per_unit=0.39 EUR (Group NAV attributable to Unitholders, p174). interest_coverage_ratio 7.6x, cost_of_debt 1.9%, wtd avg debt maturity 1.7yr (Financial Review p1075). Country occupancy: Germany 80.9%, Spain 75.4%, France 100.0% (p238-260); blended portfolio occupancy not disclosed as a single figure -> null.",
 ],
 "distributable_income_opening":None,"distribution_cash_paid":25551*K,
 "distributable_income_closing":None,"units_to_be_issued":0,
}
w("performance.json",performance)

profile={
 "symbol":"UD1U.SI","sub_sector":"Diversified","income_model":"conventional",
 "source_page":183,
 "management":{
   "reit_manager":["IREIT Global Group Pte. Ltd."],
   "trustee":["DBS Trustee Limited"],
   "sponsor":["Tikehau Capital","City Developments Limited"],
 },
}
w("profile.json",profile)

tenants=[
 ("Decathlon",20.3),("GMG - Deutsche Telekom",17.8),("B&M",17.1),
 ("Allianz Handwerker Services GmbH",3.9),("ST Microelectronics",3.8),
 ("Westf\u00e4lisch-Lippische Verm\u00f6gensverwaltungsgesellschaft mbH",3.7),
 ("Ebase",3.1),("Land of Hessen",2.8),("DXC Technology",2.2),("GESIF, S.A.U. (CABOT)",2.0),
]
tt=[{"symbol":"UD1U.SI","financial_year":2024,"rank":i+1,"client_name":n,
     "industry":None,"revenue_pct":p,"pct_basis":"gross_rental_income","source_page":47}
    for i,(n,p) in enumerate(tenants)]
w("top_tenants.json",tt)

trade=[
 ("Retail","Other Retail Trades",37.4),
 ("Telecommunications","IT & Telecommunications",17.8),
 ("IT & Electronics","IT & Telecommunications",17.5),
 ("Government","Government Related",6.9),
 ("Financial Services","Financial & Professional Services",5.8),
 ("Real Estate","Infrastructure, Real Estate & Property Services",5.0),
 ("Others","Other Office Trades",9.5),
]
tm=[{"symbol":"UD1U.SI","financial_year":2024,"category":cat,"category_raw":raw,
     "pct":p,"pct_basis":"gri","source_page":47} for raw,cat,p in trade]
w("trade_mix.json",tm)

txn=[{
 "symbol":"UD1U.SI","financial_year":2024,"transaction_type":"divestment","status":"completed",
 "property_name":"Il\u00b7lumina","country":"Spain","transaction_date":"2024-01-31",
 "gross_sale_price":24500*K,"gross_sale_price_currency":"EUR",
 "valuation":24698*K,"valuation_currency":"EUR",
 "carrying_value":24698*K,"carrying_value_currency":"EUR",
 "gain_on_divestment":-224*K,"gain_currency":"EUR",
 "carrying_value_basis":"Note 2.3 (p189): assets held for sale carried at 24,698k (31 Dec 2023); divested for sale consideration 24,500k on 31 Jan 2024; loss on divestment 224k. Loss also appears as add-back in cash flow (p179).",
 "counterparty":"unrelated third party","currency":"EUR","source_page":189,
 "deal_id":"ud1u:illumina:divestment:2024","announced_date":"2023-12-22","completed_date":"2024-01-31",
 "gain_loss_pct":None,"gain_basis":"vs_book_value","valuation_date":"2023-12-31",
 "source_type":"annual_report","sale_price":24500*K,"announcement_refs":None,
 "gain_on_divestment_basis":"Loss of 224k = 24,500k sale consideration - 24,698k carrying (Note 2.3, p189). Il\u00b7lumina (Spain office) reclassified to held-for-sale 31 Dec 2023 following conditional SPA dated 22 Dec 2023; completed 31 Jan 2024.",
}]
w("property_transactions.json",txn)
print("wrote all")
