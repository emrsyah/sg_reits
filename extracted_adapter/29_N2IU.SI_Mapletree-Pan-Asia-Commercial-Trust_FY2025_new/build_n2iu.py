"""Standalone N2IU.SI FY2025 (FYE 31 Mar 2026 = declared FY2025) extraction.
Run: python build_n2iu.py   (kernel-independent; eval kernel shared across agents)
All figures verified against the Datalab markdown source pages (cited per record).
"""
import json, os

OUT = "extracted/N2IU.SI_FY2025"
SYM, FY, CCY = "N2IU.SI", 2025, "SGD"
os.makedirs(OUT, exist_ok=True)
def W(name, obj): json.dump(obj, open(f"{OUT}/{name}.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)
def k(v):  return None if v is None else round(v * 1000)        # $'000 -> absolute
def m(v):  return None if v is None else round(v * 1_000_000)   # $ million -> absolute

# ============================ profile.json ============================
W("profile", {
    "symbol": SYM, "sub_sector": "Diversified",
    "management": {
        "reit_manager": ["MPACT Management Ltd."],
        "trustee": ["DBS Trustee Limited"],
        "sponsor": ["Mapletree Investments Pte Ltd"],
        "property_manager": [
            "MPACT Property Management Pte. Ltd. (MPMPL)",
            "Mapletree North Asia Property Management Limited (MNAPML)",
            "Mapletree Management Services Japan Kabushiki Kaisha (MMSJ)",
            "Mapletree Korea Management Co., Ltd. (MKM)",
        ],
    },
    "income_model": "conventional", "source_page": 22,
})

# ============================ performance.json ============================
W("performance", {
    "symbol": SYM, "financial_year": FY,
    "portfolio_value": m(15211.1),                 # Portfolio Property Value incl 50% Pinnacle JV, p5
    "properties_location": "Singapore; Hong Kong SAR; China; Japan; South Korea",
    "gross_revenue": k(867287), "net_property_income": k(654427),
    "net_distributable_income": k(421380),          # B: Amount available for distribution FOR THE YEAR, p110
    "distributable_income_opening": k(141525),      # A, p110
    "distribution_cash_paid": k(422889),            # P: Total Unitholders' distribution during year, p110
    "distributable_income_closing": k(140016),      # E, p110
    "distribution_paid": None,                       # no single for-year DECLARED line (Q4 declared post FY-end)
    "distribution_basis": "not_disclosed_rollforward_only",
    "adjusted_distributable_income": None,
    "dpu": 7.97,                                     # reported FY25/26 DPU (incl one-off tax charge), p4/p17
    "distribution_record": [
        {"period": "1 Jan 2025 - 31 Mar 2025", "dpu": 1.95, "ex_date": None, "pay_date": None},
        {"period": "1 Apr 2025 - 30 Jun 2025", "dpu": 2.01, "ex_date": None, "pay_date": None},
        {"period": "1 Jul 2025 - 30 Sep 2025", "dpu": 2.01, "ex_date": None, "pay_date": None},
        {"period": "1 Oct 2025 - 31 Dec 2025", "dpu": 2.05, "ex_date": None, "pay_date": None},
    ],
    "number_of_unitholders": 31768,                  # p195 (Statistics of Unitholdings, as at 8 Jun 2026)
    "number_of_shareholder_units": 5284369726,       # units in issue, p195
    "aggregate_leverage": 36.5, "interest_coverage_ratio": 3.2, "cost_of_debt": 3.16,
    "weighted_avg_debt_maturity": 3.0, "nav_per_unit": 1.73, "wale": 2.4,
    "portfolio_occupancy": 89.4,
    "currency": CCY, "date": "2026-03-31",
    "flags": [
        {"type": "dpu_period_basis", "scope": "distribution_record",
         "note": "distribution_record lists the four quarterly distributions as disclosed in the audited "
                 "Distribution Statement (p110) on a CASH-PAID basis (periods 1 Jan 2025 to 31 Dec 2025). "
                 "Their sum (8.02 cents) reflects calendar-quarter declaration/payment timing, NOT the "
                 "reported FY25/26 headline DPU of 7.97 cents (which covers the 4 FY25/26 quarters 1 Apr 2025 "
                 "to 31 Mar 2026; the 1 Jan-31 Mar 2026 tranche is declared after FY-end). Underlying DPU "
                 "excluding a one-off S$8.3m divestment-related tax charge = 8.11 cents (p4/p17)."},
        {"type": "distribution_basis_note", "scope": "distribution_paid",
         "note": "distribution_paid (for-year DECLARED) left null: the audited Distribution Statement (p110) "
                 "discloses the rollforward (A opening 141,525k; B for-year available 421,380k; P total cash "
                 "distribution 422,889k; E closing 140,016k) and per-quarter cash tranches, but not a single "
                 "'distribution declared for FY25/26' line. Rollforward A+B-P=E holds: 141,525+421,380-422,889=140,016."},
    ],
    "source_page": 4,
})

# ============================ financial.json ============================
ism = {
    "total_revenue": k(867287), "cost_of_revenue": k(212860), "gross_income": k(654427),
    "operating_income": k(605587), "operating_expense": k(48840),
    "ebit": k(445949), "ebitda": k(446656),
    "pretax_income": k(260741), "income_taxes": k(-4733), "net_income": k(265474),
    "non_operating_income_or_loss": k(-344846), "interest_expense_non_operating": k(185208),
    "diluted_shares_outstanding": k(5284370), "weighted_avg_shares_basic": k(5276248),
    "net_property_sales": k(-12948), "funds_from_operation": None,
    "unitholders": k(261274), "perpetual_security_holders": k(-4375), "minorities": k(-175),
    "depreciation": k(707),
    "_derived": ["operating_income", "operating_expense", "ebit", "ebitda",
                 "non_operating_income_or_loss", "interest_expense_non_operating"],
    "revenue_breakdown": [
        {"category": "Gross rental income", "amount": k(782108), "class": "Product/Service Sales"},
        {"category": "Car parking income", "amount": k(25598), "class": "Other income"},
        {"category": "Other operating income", "amount": k(59581), "class": "Other income"},
    ],
    "operating_expense_breakdown": [
        {"category": "Manager's base management fees", "amount": k(44828), "class": "General & Admin"},
        {"category": "Trustee's fees", "amount": k(1731), "class": "General & Admin"},
        {"category": "Other trust expenses", "amount": k(2281), "class": "Other expenses"},
    ],
}
line_items = [
    {"statement": "revenue", "component": "gross_revenue", "amount": k(867287), "label_raw": "Gross revenue", "source_page": 107},
    {"statement": "expense", "component": "property_operating_expenses", "amount": k(212860), "label_raw": "Property operating expenses", "source_page": 107},
    {"statement": "expense", "component": "finance_costs", "amount": k(186793), "label_raw": "Finance expenses", "source_page": 107},
    {"statement": "expense", "component": "management_fee_base", "amount": k(44828), "label_raw": "Manager's management fees - Base fees", "source_page": 107},
    {"statement": "expense", "component": "trustee_fee", "amount": k(1731), "label_raw": "Trustee's fees", "source_page": 107},
    {"statement": "expense", "component": "other_trust_expenses", "amount": k(2281), "label_raw": "Other trust expenses", "source_page": 107},
    {"statement": "adjustment", "component": "finance_income", "amount": k(1585), "label_raw": "Finance income", "source_page": 107},
    {"statement": "adjustment", "component": "foreign_exchange_gain", "amount": k(1424), "label_raw": "Foreign exchange gain/(loss)", "source_page": 107},
    {"statement": "adjustment", "component": "fair_value_change_financial_derivatives", "amount": k(-43471), "label_raw": "Net change in fair value of financial derivatives", "source_page": 107},
    {"statement": "adjustment", "component": "fair_value_change_investment_properties", "amount": k(-115290), "label_raw": "Net change in fair value of investment properties", "source_page": 107},
    {"statement": "adjustment", "component": "loss_on_divestment", "amount": k(-12948), "label_raw": "Net (loss)/gain on divestment of investment properties", "source_page": 107},
    {"statement": "adjustment", "component": "share_of_jv_profit", "amount": k(10647), "label_raw": "Share of profit of a joint venture", "source_page": 107},
    {"statement": "adjustment", "component": "income_tax_credit", "amount": k(4733), "label_raw": "Income tax credit", "source_page": 107},
]
recon = (sum(li["amount"] for li in line_items if li["statement"] == "revenue")
         - sum(li["amount"] for li in line_items if li["statement"] == "expense")
         + sum(li["amount"] for li in line_items if li["statement"] == "adjustment"))
assert recon == ism["net_income"], (recon, ism["net_income"])
assert sum(b["amount"] for b in ism["revenue_breakdown"]) == ism["total_revenue"]
assert sum(b["amount"] for b in ism["operating_expense_breakdown"]) == ism["operating_expense"]
W("financial", {
    "symbol": SYM, "financial_year": FY, "currency": CCY, "source_page": 107,
    "income_stmt_metrics": ism,
    "balance_sheet_metrics": {
        "total_asset": k(15424898), "total_equity": k(9392838), "total_liabilities": k(6032060),
        "working_capital": k(286012 - 734172), "total_current_asset": k(286012),
        "total_non_current_asset": k(15138886), "total_current_liabilities": k(734172),
        "total_non_current_liabilities": k(5297888), "investment_properties": k(14990064),
        "investment_in_joint_venture": k(109825), "net_asset_value_per_unit": 1.73,
        "units_in_issue": k(5284370), "unitholders_funds": k(9132512),
        "perpetual_securities": k(249110), "non_controlling_interest": k(11216),
    },
    "cash_flow_metrics": {
        "operating_cash_flow": k(586003), "investing_cash_flow": k(305110),
        "financing_cash_flow": k(-891847), "net_cash_flow": k(-734),
        "free_cash_flow": k(586003 - 86589), "capital_expenditure": k(86589),
    },
    "employee_breakdown": {"total_employee": None, "permanent_employee": None,
                           "contract_employee": None, "others_employee": None},
    "line_items": line_items,
})

# ============================ properties.json ============================
# (name, country, category, category_raw, address, ownership, val_k, gr_k, occ, npi_m, nla,
#  tenure(F/L), term_yrs, expiry, rem_yrs, src, pp, pp_ccy, status, value_basis, extra_flags)
F, L = "Freehold", "Leasehold"
P = [
 ("VivoCity","Singapore","Retail","Retail","1 HarbourFront Walk Singapore",100.0,4062000,253228,98.4,190.0,1082644,L,99.0,"2096-09-30","70",121,None,None,"active","consolidated",None),
 ("Mapletree Business City I (MBC I)","Singapore","Specialized","Business Park, Office, Retail","10, 20, 30 Pasir Panjang Road Singapore",100.0,2372000,132464,89.5,None,None,L,99.0,"2096-09-29","70",121,1780.0,"SGD","active","consolidated",
   {"type":"combined_disclosure","scope":"net_property_income/nla","note":"NPI and lettable area disclosed COMBINED with MBC II as 'Mapletree Business City' (NPI S$183.0m, LA 2,885,678 sqft) in Properties at a Glance p46; not split per building."}),
 ("mTower","Singapore","Office","Office and Retail","460 Alexandra Road Singapore",100.0,827000,52363,92.8,40.5,523582,L,99.0,"2096-09-30","70",121,477.2,"SGD","active","consolidated",
   {"type":"partial_property","scope":"property_name","note":"mTower excludes 17th-21st, 33rd and 39th storeys (Portfolio Statement p120)."}),
 ("Bank of America HarbourFront (BOAHF)","Singapore","Office","Office","2 HarbourFront Place Singapore",100.0,360000,20795,100.0,16.3,215963,L,99.0,"2096-09-30","70",121,311.0,"SGD","active","consolidated",None),
 ("Mapletree Business City II (MBC II)","Singapore","Specialized","Business Park, Office, Retail","Part 20, 40, 50, 60, 70, 80 Pasir Panjang Road Singapore",100.0,1670000,96508,88.3,None,None,L,99.0,"2096-09-30","70",121,1550.0,"SGD","active","consolidated",
   {"type":"combined_disclosure","scope":"net_property_income/nla","note":"Held under Mapletree Business City LLP. NPI and lettable area disclosed COMBINED with MBC I as 'Mapletree Business City' in Properties at a Glance p46; not split per building."}),
 ("Festival Walk","Hong Kong SAR","Retail","Retail","No. 80 Tat Chee Avenue, Kowloon Tong, Hong Kong SAR",100.0,3387141,181368,96.8,133.5,588890,L,54.0,"2047-06-30","21",123,23233.1,"HKD","active","consolidated",
   {"type":"partial_divestment","scope":"all","note":"Office component (Festival Walk Tower) divested to an external party on 2 February 2026 (Note 13, p133). Retained retail mall spans 588,890 sqft (p17)."}),
 ("Gateway Plaza","China","Office","Office","No. 18 Xiaguangli, East 3rd Ring Road North, Chaoyang District, Beijing, China",100.0,982565,56021,85.9,44.1,1145896,L,50.0,"2053-02-25","27",123,6353.0,"CNY","active","consolidated",None),
 ("Sandhill Plaza","China","Specialized","Business Park","Blocks 1 to 5 and 7 to 9, No. 2290 Zuchongzhi Road, Pudong New District, Shanghai, China",100.0,384482,16906,76.9,14.7,683115,L,50.0,"2060-02-03","34",123,2427.0,"CNY","active","consolidated",None),
 ("IXINAL Monzen-nakacho Building (MON)","Japan","Office","Office","5-4, Fukuzumi 2-chome, Koto-ku, Tokyo, Japan",100.0,68604,3179,56.3,2.3,73753,F,None,None,None,123,8630.0,"JPY","active","consolidated",None),
 ("Higashi-nihonbashi 1-chome Building (HNB)","Japan","Office","Office","4-6, Higashi-Nihonbashi 1-chome, Chuo-ku, Tokyo, Japan",100.0,22493,1196,100.0,0.9,27996,F,None,None,None,123,2600.0,"JPY","active","consolidated",None),
 ("Makuhari Bay Tower (MBT)","Japan","Office","Office","8, Nakase 1-chome, Mihama-ku, Chiba-shi, Chiba, Japan",100.0,118893,4522,33.9,-0.6,402444,F,None,None,None,123,20500.0,"JPY","active","consolidated",None),
 ("Fujitsu Makuhari Building (FJM)","Japan","Office","Office","9-3, Nakase 1-chome, Mihama-ku, Chiba-shi, Chiba, Japan",100.0,79610,9915,100.0,8.1,657549,F,None,None,None,125,19500.0,"JPY","active","consolidated",
   {"type":"single_tenant_non_renewal","scope":"all","note":"Single tenant Fujitsu Limited ceased to be a tenant after 31 March 2026; lettable area reduces to 329,023 sqft post-departure (p48). NLA 657,549 sqft is the pre-departure single-tenant basis."}),
 ("Omori Prime Building (OPB)","Japan","Office","Office","21-12, Minami-oi 6-chome, Shinagawa-ku, Tokyo, Japan",100.0,61615,3655,100.0,2.4,73168,F,None,None,None,125,7660.0,"JPY","active","consolidated",None),
 ("mBAY POINT Makuhari (MBP)","Japan","Office","Office","6, Nakase 1-chome, Mihama-ku, Chiba-shi, Chiba, Japan",100.0,265099,18713,55.2,5.9,923077,F,None,None,None,125,35500.0,"JPY","active","consolidated",None),
 ("Hewlett-Packard Japan Headquarters Building (HPB)","Japan","Office","Office","2-1, Ojima 2-chome, Koto-ku, Tokyo, Japan",100.0,328562,14845,100.0,12.1,457426,F,None,None,None,125,40700.0,"JPY","active","consolidated",None),
 ("The Pinnacle Gangnam","South Korea","Office","Office","343, Hakdong-ro, Gangnam-gu, Seoul, South Korea",50.0,221000,None,99.9,9.1,478461,F,None,None,None,47,244750.0,"KRW","active","effective_interest",
   {"type":"equity_accounted_jv","scope":"all","note":"Held via 50% effective interest as a joint venture; equity-accounted (Investment in a joint venture S$109,825k, p109), ABSENT from the audited consolidated Portfolio Statement. market_valuation S$221.0m, gross_revenue S$12.1m, NPI S$9.1m are MPACT's 50%-effective-interest figures from Properties at a Glance p47 (SGD equivalents at S$1=KRW1,167.5423); occupancy 99.9% committed. NLA 478,461 sqft is 100% basis. Excluded from Group revenue/NPI/valuation reconciliations."}),
 # ---- divested in FY25/26 (partial-year revenue retained in Group total; no FY-end valuation) ----
 ("TS Ikebukuro Building (TSI)","Japan","Office","Office","63-4, Higashi-Ikebukuro 2-chome, Toshima-ku, Tokyo, Japan",100.0,None,931,None,None,None,F,None,None,None,123,None,None,"divested","consolidated",
   {"type":"divested_partial_data","scope":"all","note":"Divested to an external party on 22 August 2025 for cash consideration JPY5,400,000,000, net loss on divestment S$3,093k (Note 13, p133). FY25/26 gross revenue S$931k (partial year) retained in Group total; no FY-end valuation."}),
 ("ABAS Shin-Yokohama Building (ASY)","Japan","Office","Office","6-1, Shin-Yokohama 2-chome, Yokohama City, Kanagawa, Japan",100.0,None,678,None,None,None,F,None,None,None,123,None,None,"divested","consolidated",
   {"type":"divested_partial_data","scope":"all","note":"Divested to an external party on 28 August 2025 for cash consideration JPY3,330,000,000, net gain on divestment S$408k (Note 13, p133). FY25/26 gross revenue S$678k (partial year) retained in Group total; no FY-end valuation."}),
]
props = []
for (name,ctry,cat,craw,addr,own,valk,grk,occ,npim,nla,ten,term,exp,rem,src,pp,ppccy,status,vbasis,xflag) in P:
    if ten == L:
        tenure_raw = f"Leasehold / {int(term)} years / {rem} years remaining"
    else:
        tenure_raw = "Freehold"
    rec = {
        "symbol": SYM, "financial_year": FY, "property_name": name, "country": ctry,
        "category": cat, "category_raw": craw, "address": addr, "ownership": own,
        "market_valuation": k(valk), "valuation_date": "2026-03-31", "currency": CCY,
        "net_property_income": m(npim), "gross_revenue": k(grk), "npi_pct": None,
        "occupancy_rate": occ, "nla": float(nla) if nla is not None else None,
        "area_unit": "sqft" if nla is not None else None,
        "land_tenure": ten, "lease_term_years": term, "lease_expiry_date": exp,
        "tenure_raw": tenure_raw, "status": status, "value_basis": vbasis,
        "source_page": src,
        "purchase_price": m(pp) if pp is not None else None,
        "purchase_price_currency": ppccy,
    }
    if xflag:
        rec["flags"] = [xflag]
    props.append(rec)
W("properties", props)

# ---- reconciliation sums (SGD, Tier-C audited Portfolio Statement) ----
active_cons = [p for p in props if p["value_basis"] == "consolidated" and p["status"] == "active"]
sum_val = sum(p["market_valuation"] for p in active_cons if p["market_valuation"])
sum_gr_active = sum(p["gross_revenue"] for p in active_cons if p["gross_revenue"])
sum_gr_all = sum(p["gross_revenue"] for p in props if p["value_basis"] == "consolidated" and p["gross_revenue"])
# full disclosed per-property NPI (SGD incl the combined MBC I+II figure of S$183.0m)
sum_npi_full = m(190.0+183.0+40.5+16.3+133.5+44.1+14.7+2.3+0.9-0.6+8.1+2.4+5.9+12.1)
assert sum_val == k(14990064), sum_val
assert sum_gr_all == k(867287), sum_gr_all

# ============================ property_transactions.json ============================
W("property_transactions", [
 {"symbol": SYM, "financial_year": FY, "transaction_type": "divestment", "status": "completed",
  "property_name": "TS Ikebukuro Building (TSI)", "deal_id": "N2IU.SI:ts-ikebukuro:divestment:2025",
  "transaction_date": "2025-08-22", "completed_date": "2025-08-22",
  "sale_price": m(5400.0), "sale_price_currency": "JPY",
  "gain_on_divestment": k(-3093), "gain_loss_pct": None, "gain_basis": "vs_book_value",
  "gain_basis_note": "Disclosed net LOSS on divestment S$3,093k = net sale proceeds - carrying value (Note 13, p133); stored signed (negative = loss).",
  "counterparty": "External party (unnamed)", "currency": "JPY",
  "source_type": "annual_report", "source_page": 133,
  "sale_price_basis": "Cash consideration JPY5,400,000,000 (~S$48.7m portion of the combined TSI+ASY JPY8,730.0m / S$78.7m; p17). Net loss on divestment S$3,093k (Note 13)."},
 {"symbol": SYM, "financial_year": FY, "transaction_type": "divestment", "status": "completed",
  "property_name": "ABAS Shin-Yokohama Building (ASY)", "deal_id": "N2IU.SI:abas-shin-yokohama:divestment:2025",
  "transaction_date": "2025-08-28", "completed_date": "2025-08-28",
  "sale_price": m(3330.0), "sale_price_currency": "JPY",
  "gain_on_divestment": k(408), "gain_loss_pct": None, "gain_basis": "vs_book_value",
  "gain_basis_note": "Disclosed net GAIN on divestment S$408k = net sale proceeds - carrying value (Note 13, p133).",
  "counterparty": "External party (unnamed)", "currency": "JPY",
  "source_type": "annual_report", "source_page": 133,
  "sale_price_basis": "Cash consideration JPY3,330,000,000 (part of the combined TSI+ASY JPY8,730.0m / S$78.7m; p17). Net gain on divestment S$408k (Note 13)."},
 {"symbol": SYM, "financial_year": FY, "transaction_type": "partial_divestment", "status": "completed",
  "property_name": "Festival Walk Tower (office component of Festival Walk)", "deal_id": "N2IU.SI:festival-walk-tower:partial_divestment:2026",
  "transaction_date": "2026-02-02", "completed_date": "2026-02-02",
  "sale_price": m(1960.0), "sale_price_currency": "HKD",
  "gain_on_divestment": k(-10263), "gain_loss_pct": None, "gain_basis": "vs_book_value",
  "gain_basis_note": "Disclosed net LOSS on divestment S$10,263k = net sale proceeds - carrying value (Note 13, p133); consideration in line with independent valuation (p17); stored signed (negative = loss).",
  "counterparty": "External party (unnamed)", "currency": "HKD",
  "source_type": "annual_report", "source_page": 133,
  "sale_price_basis": "Cash consideration HKD1,960,000,000 (~S$328.1m; p17), the office tower only; MPACT retains the Festival Walk retail mall. Net loss on divestment S$10,263k (Note 13)."},
])

# ============================ trade_mix.json (Trade Mix by GRI, p45) ============================
# (canonical_category, category_raw_verbatim, pct)
TM = [
 ("Food & Beverages","F&B",17.2),
 ("IT & Telecommunications","IT Services & Consultancy",14.3),
 ("Fashion & Accessories","Fashion",7.8),
 ("Financial & Professional Services","Banking & Financial Services",6.2),
 ("Departmental Store/Supermarket","Departmental Store / Supermarket / Hypermarket",5.3),
 ("Healthcare & Wellness","Beauty & Health",4.6),
 ("Manufacturing","Machinery / Equipment / Manufacturing",4.2),
 ("Fashion & Accessories","Luxury Jewellery, Watches & Fashion Accessories",4.0),
 ("Government Related","Government Related",3.8),
 ("Other Industrial Trades","Automobile",3.5),
 ("Logistics & Supply Chain Management","Shipping Transport",3.0),
 ("Other Retail Trades","Sports",2.8),
 ("Other Office Trades","Electronics (Office / Business Park)",2.7),
 ("Other Retail Trades","Lifestyle",2.5),
 ("Financial & Professional Services","Professional & Business Services",2.2),
 ("Hospitality & Leisure","Leisure & Entertainment",2.2),
 ("Other Retail Trades","Consumer Electronics",2.2),
 ("Healthcare & Wellness","Pharmaceutical",2.1),
 ("Other Office Trades","Consumer Goods & Services",2.0),
 ("Other Retail Trades","Others (Real Estate/Construction, Convenience & Retail Services, Trading, Education & Enrichment, Optical, Energy, Medical and others)",6.9),
]
assert abs(sum(p for _,_,p in TM) - 100.0) < 1.0, sum(p for _,_,p in TM)  # components rounded to 1dp; report total = 100.0%
W("trade_mix", [{"symbol": SYM, "financial_year": FY, "category": c, "category_raw": r,
                 "pct": p, "pct_basis": "gri", "source_page": 45} for c, r, p in TM])

# ============================ top_tenants.json (Top Ten Tenants by GRI, p45) ============================
# (rank, client_name, industry_canonical, revenue_pct)
TT = [
 (1,"Google Asia Pacific Pte. Ltd.","IT & Telecommunications",6.2),
 (2,"BMW","Other Industrial Trades",3.3),
 (3,"Merrill Lynch Global Services Pte. Ltd.","Financial & Professional Services",2.0),
 (4,"TaSTe","Departmental Store/Supermarket",1.7),
 (5,"Hewlett-Packard Japan, Ltd.","IT & Telecommunications",1.7),
 (6,"Info-Communications Media Development Authority","Government Related",1.7),
 (7,"The Hongkong and Shanghai Banking Corporation Limited","Financial & Professional Services",1.6),
 (8,"(Undisclosed tenant)",None,None),
 (9,"Mapletree Investments Pte Ltd","Infrastructure, Real Estate & Property Services",1.6),
 (10,"NTUC Fairprice Co-operative Ltd.","Departmental Store/Supermarket",1.4),
]
W("top_tenants", [{"symbol": SYM, "financial_year": FY, "rank": r, "client_name": n,
                   "industry": ind, "revenue_pct": p, "pct_basis": "gri", "source_page": 45} for r, n, ind, p in TT])

# ============================ _notes.json ============================
W("_notes", {
    "columns_never_fillable": [
        {"column": "gla / nla (MBC I, MBC II)", "reason": "Lettable area for Mapletree Business City I and II is disclosed COMBINED (2,885,678 sqft as 'Mapletree Business City', Properties at a Glance p46); it cannot be split per building, so both rows carry null gla/nla/gfa. All other active properties have nla."},
        {"column": "net_property_income (MBC I / MBC II)", "reason": "MPACT discloses NPI for Mapletree Business City I and II COMBINED (S$183.0m as 'Mapletree Business City', Properties at a Glance p46); it cannot be split per building, so both rows carry null NPI."},
        {"column": "npi_pct", "reason": "Per-property NPI is disclosed only in the marketing cards (some in local currency), not as a percentage share of portfolio NPI in the audited statements; left null rather than derived."},
        {"column": "effective_date", "reason": "Land-lease commencement date not disclosed per property in a machine-readable way (acquisition dates are in the Portfolio Statement; VivoCity/MBC/Singapore leases commenced 1 Oct 1997)."},
    ],
    "data_with_no_home": [
        "Portfolio: 15 commercial properties across five gateway markets (SG/HK/China/Japan/Korea) with total lettable area 10.2 million sq ft (p17). The audited Portfolio Statement splits Mapletree Business City into MBC I (held under MPACT) and MBC II (held under MBC LLP), so properties.json has 16 active rows (MBC counted twice) + 2 divested (TSI, ASY).",
        "AUM by region (incl 50% Pinnacle): VivoCity SG 27%, MBC SG 27%, Other SG 8%, Festival Walk HK 22%, China 9%, Japan 6%, South Korea 1% (p6). Post-divestment Singapore = 61% of AUM and 66% of NPI.",
        "Japan committed occupancy 75.1% as at 31 Mar 2026 (57.1% post-FJM single-tenant expiry on 31 Mar 2026) (p46/p48).",
        "Gross debt outstanding S$5,685.9m; market cap S$6,971.1m; proportion of fixed-rate debt 75.1%; distribution yield 6.0% at S$1.32 close (p5).",
        "FX (closing, 31 Mar 2026): S$1 = HKD6.1113, RMB5.3839, KRW1,167.5423 (p47); S$1 = JPY124.4818 (p48). SGD strengthened vs HKD/JPY/RMB yoy, a driver of lower overseas contributions (p17).",
        "The Pinnacle Gangnam (South Korea, 50% JV): 100%-basis lettable area 478,461 sqft; MPACT 50% share market_valuation S$221.0m, gross revenue S$12.1m (KRW13,280.8m), NPI S$9.1m (KRW10,070.1m); equity-accounted, MPACT share of JV profit S$10,647k (p107); investment in JV S$109,825k (p109).",
        "Three FY25/26 divestments totalled S$406.8m: TSI + ASY (Japan offices) JPY8,730.0m / S$78.7m; Festival Walk Tower (HK office) HKD1,960.0m / S$328.1m (p17).",
        "Mapletree Anson (Singapore office) was divested in the PRIOR financial year (31 Jul 2024, S$775.0m, gain S$4,006k; Note 13 p133) and is NOT a FY25/26 property or transaction; excluded from properties.json.",
    ],
    "parsing_traps": [
        "Audited Portfolio Statement (Tier-C, SGD $'000) is a two-page spread: property descriptions on p120/p122/p124 (left), financials (gross revenue, occupancy, valuation) on p121/p123/p125 (right); rows aligned by position after dropping section-header/sub-total rows. Reconciles exactly: Sigma valuation (active) = S$14,990,064k = Investment properties - Group; Sigma gross revenue (all incl divested partials) = S$867,287k = Group gross revenue.",
        "market_valuation and gross_revenue for all 15 consolidated properties are the audited SGD $'000 figures (the statement consolidates all overseas assets to SGD; there is NO per-property local-currency valuation in the audited statement). currency = SGD on every row accordingly (multi-currency assets, single SGD reporting currency).",
        "Per-property net_property_income is NOT in the audited Portfolio Statement; it is taken from the 'Properties at a Glance' cards (p46-49), using the disclosed SGD-equivalent figure (e.g. Festival Walk NPI HKD808.2m = S$133.5m). MBC I/II NPI is disclosed combined only.",
        "Below-NPI income lines (finance income S$1,585k, foreign exchange gain S$1,424k, share of JV profit S$10,647k, income tax credit S$4,733k) are correctly bucketed as statement='adjustment' (signed), NOT 'revenue' - confirmed on the audited Statements of Profit or Loss (Group column), p107. Dividend income and impairment loss on subsidiary are MPACT-only (Group = nil) and excluded.",
        "Reported FY25/26 DPU = 7.97 cents (includes a one-off S$8.3m divestment-related tax charge); underlying DPU = 8.11 cents. The Distribution Statement (p110) lists four quarterly cash tranches on a period-mixed basis (1 Jan 2025 - 31 Dec 2025), summing 8.02 cents - a cash-paid timing artefact, not the fiscal-year headline.",
    ],
    "inferred": [
        {"table": "top_tenants", "field": "industry", "scope": "all rows except rank 8", "value": None,
         "basis": "The Top Ten Tenants by GRI table (p45) discloses each tenant's property(ies) but no trade-sector column; industry mapped from each tenant's known business identity to the canonical 15-value taxonomy (e.g. Google/HP -> IT & Telecommunications; Merrill Lynch/HSBC -> Financial & Professional Services; IMDA -> Government Related; NTUC FairPrice/TaSTe -> Departmental Store/Supermarket; BMW -> Other Industrial Trades (automobile); Mapletree Investments -> Infrastructure, Real Estate & Property Services).", "source_page": 45},
        {"table": "top_tenants", "field": "revenue_pct", "rows": [8], "value": None,
         "basis": "Rank 8 is an undisclosed tenant with no % of GRI disclosed (shown as '-' in the table); left null. Top-ten total 21.4% excludes the undisclosed tenant.", "source_page": 45},
        {"table": "trade_mix", "field": "category", "property_name": "Others",
         "value": "Other Retail Trades",
         "basis": "The report's residual 'Others' trade sector (6.9% of GRI) spans Real Estate/Construction, Convenience & Retail Services, Trading, Education, Optical, Energy and Medical across retail/office/business-park; no single canonical fits, mapped to Other Retail Trades as the dominant residual. Verbatim breakdown kept in category_raw.", "source_page": 45},
        {"table": "properties", "field": "occupancy_rate", "property_name": "The Pinnacle Gangnam", "value": 99.9,
         "basis": "Pinnacle is absent from the audited Portfolio Statement (equity-accounted JV); occupancy 99.9% is the committed occupancy from Properties at a Glance p47 (vs the actual/physical occupancy used for consolidated rows).", "source_page": 47},
        {"table": "properties", "field": "market_valuation", "property_name": "The Pinnacle Gangnam", "value": 221000000,
         "basis": "Pinnacle valuation is MPACT's 50%-effective-interest SGD figure (S$221.0m = KRW258,050.0m at S$1=KRW1,167.5423) from Properties at a Glance p47, since the equity-accounted JV is not in the audited Tier-C Portfolio Statement. Reconciles: Sigma consolidated S$14,990.064m + Pinnacle S$221.0m = S$15,211.1m headline portfolio value.", "source_page": 47},
    ],
    "reconciliation": {
        "sum_property_gross_revenue": sum_gr_all,
        "reported_total_gross_revenue": k(867287),
        "sum_property_npi": sum_npi_full,
        "reported_total_npi": k(654427),
        "sum_consolidated_active_valuation": sum_val,
        "reported_investment_properties_group": k(14990064),
        "note": "Gross revenue: Sigma over all consolidated property rows (incl divested-in-year TSI S$931k + ASY S$678k partials) = S$867,287k = Group gross revenue EXACTLY (p107/p125). Active-only Sigma (gate basis, excl divested) = S$865,678k (0.19% lower). NPI: per-property NPI from the marketing cards (SGD equivalents); full disclosed sum incl the combined MBC I+II figure (S$183.0m) = S$653,200k vs Group NPI S$654,427k (0.19% gap absorbs divested-in-year partials and card rounding). Row-level active NPI sum excludes MBC I/II (combined-only, null) so it is lower - _notes reconciliation is authoritative. Valuation: Sigma active consolidated = S$14,990,064k = Investment properties - Group EXACTLY (p125/p109); The Pinnacle Gangnam (50% JV, S$221.0m) is equity-accounted and excluded (its addition gives the S$15,211.1m headline portfolio value).",
        "portfolio_valuation_check": {"sum_consolidated_active_valuation": sum_val,
                                      "reported_fair_value_investment_properties": k(14990064)},
    },
})

print("wrote 8 files to", OUT)
print("STR recon net_income:", recon, "==", ism["net_income"])
print("Sigma valuation (active consolidated):", sum_val, "== 14,990,064,000")
print("Sigma gross revenue (all consolidated):", sum_gr_all, "== 867,287,000")
print("Sigma gross revenue (active consolidated):", sum_gr_active)
print("Sigma NPI full disclosed (incl combined MBC):", sum_npi_full, "vs Group NPI 654,427,000")
print("properties:", len(props), "( active:", len(active_cons)+1, "incl Pinnacle JV; divested: 2 )")
