"""Assemble the 8-file ME8U.SI FY2025 output from parsed pieces + audited figures."""
import json, os
STEM = "27_ME8U.SI_Mapletree-Industrial-Trust_FY2025_new"
OUT = "extracted/ME8U.SI_FY2025"
SYM, FY = "ME8U.SI", 2025
os.makedirs(OUT, exist_ok=True)
def W(name, obj): json.dump(obj, open(f"{OUT}/{name}.json", "w"), indent=2, ensure_ascii=False)
def k(v): return round(v * 1000)  # $'000 -> absolute

# ---------- profile.json ----------
W("profile", {
    "symbol": SYM, "sub_sector": "Diversified",
    "management": {
        "reit_manager": ["Mapletree Industrial Trust Management Ltd."],
        "trustee": ["DBS Trustee Limited"],
        "sponsor": ["Mapletree Investments Pte Ltd"],
        "property_manager": ["Mapletree Facilities Services Pte. Ltd.",
                             "Mapletree US Management LLC",
                             "Mapletree Management Services Japan Kabushiki Kaisha"],
    },
    "income_model": "conventional", "source_page": 18,
})

# ---------- performance.json ----------
W("performance", {
    "symbol": SYM, "financial_year": FY,
    "portfolio_value": k(8315600),                 # AUM incl JV interests (Key Information, p11)
    "properties_location": "Singapore; United States; Canada; Japan",
    "gross_revenue": k(672991), "net_property_income": k(500353),
    "net_distributable_income": k(363881),          # Amount available for distribution (for-year B), p125
    "distributable_income_opening": k(117337),      # A, p125
    "distribution_cash_paid": k(370206),            # P (Total Unitholders' distribution during year), p125
    "distributable_income_closing": k(111012),      # E, p125
    "distribution_paid": k(362609),                 # for-year declared (DPU 12.71 basis), p32
    "distribution_basis": "disclosed_after_retention",
    "adjusted_distributable_income": None,
    "dpu": 12.71,
    "distribution_record": [
        {"period": "01 Apr 2025 to 30 Jun 2025", "dpu": 3.27, "ex_date": None, "pay_date": None},
        {"period": "01 Jul 2025 to 30 Sep 2025", "dpu": 3.18, "ex_date": None, "pay_date": None},
        {"period": "01 Oct 2025 to 31 Dec 2025", "dpu": 3.17, "ex_date": None, "pay_date": None},
        {"period": "01 Jan 2026 to 31 Mar 2026", "dpu": 3.09, "ex_date": None, "pay_date": None},
    ],
    "number_of_unitholders": 47589,                 # p196 (as at 29 May 2026)
    "number_of_shareholder_units": k(2854187),      # units in issue at end (Note 24a), p179
    "units_to_be_issued": k(816),                   # to be issued (mgmt fees) at end, p179
    "aggregate_leverage": 34.0, "interest_coverage_ratio": 4.0, "cost_of_debt": 3.1,
    "weighted_avg_debt_maturity": 3.4, "nav_per_unit": 1.63, "wale": 4.4,
    "portfolio_occupancy": 91.3,
    "currency": "SGD", "date": "2026-03-31",
    "flags": [
        {"type": "kpi_proportionate_jv_basis", "scope": "aggregate_leverage/interest_coverage_ratio/weighted_avg_debt_maturity",
         "note": "Key financial ratios include MIT's proportionate share of the JV's aggregate debt and deposited property value (report footnote 10, p11)."},
    ],
    "source_page": 11,
})

# ---------- financial.json ----------
ism = {
    "total_revenue": k(672991), "cost_of_revenue": k(172638), "gross_income": k(500353),
    "operating_income": k(439075), "operating_expense": k(61278),
    "ebit": k(345904), "ebitda": k(345951),
    "pretax_income": k(262135), "income_taxes": k(40544), "net_income": k(221591),
    "non_operating_income_or_loss": k(-176940), "interest_expense_non_operating": k(83769),
    "diluted_shares_outstanding": k(2853440), "weighted_avg_shares_basic": k(2852624),
    "net_property_sales": k(2967), "funds_from_operation": None,
    "unitholders": k(211195), "perpetual_security_holders": k(-10198), "minorities": k(-198),
    "depreciation": k(47),
    "_derived": ["operating_income", "operating_expense", "ebit", "ebitda",
                 "non_operating_income_or_loss", "interest_expense_non_operating", "depreciation"],
    "revenue_breakdown": [
        {"category": "Rental income and service charges", "amount": k(643852), "class": "Product/Service Sales"},
        {"category": "Other operating income", "amount": k(29139), "class": "Other income"},
    ],
    "operating_expense_breakdown": [
        {"category": "Manager's base fees", "amount": k(39504), "class": "General & Admin"},
        {"category": "Manager's performance fees", "amount": k(18147), "class": "General & Admin"},
        {"category": "Trustee's fees", "amount": k(983), "class": "General & Admin"},
        {"category": "Other trust expenses", "amount": k(2644), "class": "Other expenses"},
    ],
}
line_items = [
    {"statement": "revenue", "component": "gross_revenue", "amount": k(672991), "label_raw": "Gross revenue", "source_page": 122},
    {"statement": "expense", "component": "property_operating_expenses", "amount": k(172638), "label_raw": "Property operating expenses", "source_page": 122},
    {"statement": "expense", "component": "management_fee_base", "amount": k(39504), "label_raw": "Manager's management fees – Base fees", "source_page": 122},
    {"statement": "expense", "component": "management_fee_performance", "amount": k(18147), "label_raw": "Manager's management fees – Performance fees", "source_page": 122},
    {"statement": "expense", "component": "trustee_fee", "amount": k(983), "label_raw": "Trustee's fees", "source_page": 122},
    {"statement": "expense", "component": "other_trust_expenses", "amount": k(2644), "label_raw": "Other trust expenses", "source_page": 122},
    {"statement": "expense", "component": "finance_costs", "amount": k(84789), "label_raw": "Borrowing costs", "source_page": 122},
    {"statement": "expense", "component": "income_tax", "amount": k(40544), "label_raw": "Income tax expense", "source_page": 122},
    {"statement": "adjustment", "component": "interest_income", "amount": k(1020), "label_raw": "Interest income", "source_page": 122},
    {"statement": "adjustment", "component": "other_income", "amount": k(3041), "label_raw": "Other income", "source_page": 122},
    {"statement": "adjustment", "component": "net_foreign_exchange_gain", "amount": k(1947), "label_raw": "Net foreign exchange gain/(loss)", "source_page": 122},
    {"statement": "adjustment", "component": "fair_value_change_financial_derivatives", "amount": k(875), "label_raw": "Net change in fair value of financial derivatives", "source_page": 122},
    {"statement": "adjustment", "component": "fair_value_change_investment_properties", "amount": k(-131485), "label_raw": "Net change in fair value of investment properties", "source_page": 122},
    {"statement": "adjustment", "component": "gain_on_divestment", "amount": k(2967), "label_raw": "Gain on divestment of investment properties", "source_page": 122},
    {"statement": "adjustment", "component": "share_of_joint_venture", "amount": k(29484), "label_raw": "Share of profit of a joint venture", "source_page": 122},
]
recon = sum(li["amount"] for li in line_items if li["statement"] == "revenue") \
    - sum(li["amount"] for li in line_items if li["statement"] == "expense") \
    + sum(li["amount"] for li in line_items if li["statement"] == "adjustment")
assert recon == ism["net_income"], (recon, ism["net_income"])
W("financial", {
    "symbol": SYM, "financial_year": FY, "currency": "SGD", "source_page": 122,
    "income_stmt_metrics": ism,
    "balance_sheet_metrics": {
        "total_asset": k(7938639), "total_equity": k(5246034), "total_liabilities": k(2692605),
        "working_capital": k(120039 - 528712), "total_current_asset": k(120039),
        "total_non_current_asset": k(7818600), "total_current_liabilities": k(528712),
        "total_non_current_liabilities": k(2163893), "investment_properties": k(7286280),
        "investment_in_joint_venture": k(505151), "net_asset_value_per_unit": 1.63,
        "units_in_issue": k(2855003), "perpetual_securities": k(600837), "non_controlling_interest": k(2547),
    },
    "cash_flow_metrics": {
        "operating_cash_flow": k(433643), "investing_cash_flow": k(494539),
        "financing_cash_flow": k(-936114), "net_cash_flow": k(-7932),
        "free_cash_flow": k(433643 - 64864), "capital_expenditure": k(64864),
    },
    "employee_breakdown": {"total_employee": None, "permanent_employee": None,
                           "contract_employee": None, "others_employee": None},
    "line_items": line_items,
})

# ---------- trade_mix.json (Tenant Diversification by trade sector, GRI), p42 ----------
tm = [
    ("IT & Telecommunications", "Information and Communications", 31.53),
    ("Manufacturing", "Manufacturing", 28.49),
    ("Other Retail Trades", "Wholesale and Retail Trade", 15.10),
    ("Financial & Professional Services", "Financial and Business Services", 13.25),
    ("Healthcare & Wellness", "Other Trade Sectors: Education, Health and Social Services, Arts, Entertainment and Recreation", 4.73),
    ("Infrastructure, Real Estate & Property Services", "Other Trade Sectors: Construction and Utilities", 2.79),
    ("Hospitality & Leisure", "Other Trade Sectors: Accommodation and Food Service", 2.17),
    ("Logistics & Supply Chain Management", "Other Trade Sectors: Transportation and Storage", 1.94),
]
W("trade_mix", [{"symbol": SYM, "financial_year": FY, "category": c, "category_raw": r,
                 "pct": p, "pct_basis": "gri", "source_page": 42} for c, r, p in tm])

# ---------- top_tenants.json (Top 10 Tenants by GRI), p41 ----------
tt = [
    (1, "HP Singapore (Private) Limited", "IT & Telecommunications", 6.5),
    (2, "Global Colocation Provider", "IT & Telecommunications", 4.8),
    (3, "Established Data Centre Operator", "IT & Telecommunications", 4.2),
    (4, "Global Social Media Company", "IT & Telecommunications", 3.1),
    (5, "Equinix Singapore Pte Ltd.", "IT & Telecommunications", 2.5),
    (6, "AT&T Inc.", "IT & Telecommunications", 2.5),
    (7, "The Bank of America Corporation", "Financial & Professional Services", 2.4),
    (8, "Lumen Technologies, Inc.", "IT & Telecommunications", 1.7),
    (9, "Vanderbilt University Medical Center", "Healthcare & Wellness", 1.5),
    (10, "Tierpoint, LLC", "IT & Telecommunications", 1.4),
]
W("top_tenants", [{"symbol": SYM, "financial_year": FY, "rank": r, "client_name": n,
                   "industry": ind, "revenue_pct": p, "pct_basis": "gri", "source_page": 41} for r, n, ind, p in tt])

# ---------- property_transactions.json ----------
W("property_transactions", [
    {"symbol": SYM, "financial_year": FY, "transaction_type": "divestment", "status": "completed",
     "property_name": "2775 Northwoods Parkway, Norcross", "deal_id": "ME8U.SI:2775-northwoods-parkway-norcross:divestment:2025",
     "transaction_date": "2025-05-10", "completed_date": "2025-05-10",
     "sale_price": round(11800000), "sale_price_currency": "USD",
     "counterparty": None, "currency": "USD", "source_type": "annual_report", "source_page": 162,
     "sale_price_basis": "US$11,800,000 (~S$15,300,000); 100% of the property (Note 14, p162)"},
    {"symbol": SYM, "financial_year": FY, "transaction_type": "divestment", "status": "completed",
     "property_name": "The Strategy, The Synergy and Woodlands Central Cluster",
     "deal_id": "ME8U.SI:strategy-synergy-woodlands-central:divestment:2025",
     "transaction_date": "2025-08-15", "completed_date": "2025-08-15",
     "sale_price": round(535300000), "sale_price_currency": "SGD",
     "counterparty": None, "currency": "SGD", "source_type": "annual_report", "source_page": 162,
     "sale_price_basis": "Combined cash consideration S$535,300,000 for three Singapore industrial properties (Note 14, p162)"},
])

# ---------- properties.json ----------
props = json.load(open(f"extracted_adapter/{STEM}/_properties.json"))
W("properties", props)

# ---------- _notes.json ----------
sum_gr_all = sum(p["gross_revenue"] for p in props if p.get("value_basis", "").startswith("consolidated") and p.get("gross_revenue"))
W("_notes", {
    "columns_never_fillable": [
        {"column": "net_property_income", "reason": "MIT discloses NPI only at Group/segment level, not per property (audited Portfolio Statement gives per-property gross revenue, occupancy and valuation only)."},
        {"column": "lease_expiry_date", "reason": "Portfolio Statement discloses 'Remaining term of lease' (years) per property, not an expiry date; kept verbatim in tenure_raw."},
        {"column": "effective_date", "reason": "Land-lease commencement date not disclosed per property (only acquisition/legal-completion date, captured elsewhere)."},
    ],
    "data_with_no_home": [
        "Joint venture MRODCT (Mapletree Rosewood Data Centre Trust): 50% MIT-owned, equity-accounted; holds 13 US data centres (3 fully-fitted hyperscale + 10 powered shell). 100%-basis: net assets S$1,010,302k, gross revenue S$61,456k, profit S$58,969k; MIT carrying value of interest S$505,151k; MIT share of JV results S$29,484k; distributions received S$22,442k (Note 18, p169-170).",
        "Some JV data centres (21744 & 21745 Sir Timothy Drive, 44490 Chillum Place, Ashburn) are held 40% by MIT (MRODCT holds 80%, Digital Realty 20%; MIT holds 50% of MRODCT) (p54 note 4).",
        "Overall portfolio: 2,142 tenants across 3,127 leases; 61.1% MNCs, 38.9% SMEs by GRI (p41). WALE 4.4 years; new/renewal-lease WALE FY25/26 3.3 years.",
        "AUM by geography: North America 46.5%, Singapore 46.3%, Japan 7.2% (p11). AUM by segment: Data Centres 57.3%, General Industrial 24.3%, Hi-Tech & Business Space 18.4%.",
        "Total borrowings S$2,258.9m; distribution yield 6.6%; market cap S$5.54bn as at 31 Mar 2026 (p11, p30-31).",
        "Segment reporting restated effective 1 April 2025 to: Data Centres (Asia), Data Centres (North America), Hi-Tech Buildings & Business Space, General Industrial Buildings (Portfolio Statement footnote 8, p142).",
    ],
    "parsing_traps": [
        "Audited Portfolio Statement is a two-page spread (descriptions on the left page, financials on the right); rows aligned by position after dropping section-header rows. Reconciles exactly: Σ valuation = S$7,183,873k, Σ gross revenue = S$672,991k.",
        "market_valuation for the 86 consolidated properties is Tier-C SGD from the audited Portfolio Statement (p132-143). market_valuation for the 13 equity-accounted JV data centres is the operational-overview US$'000 figure (100% basis, p53/55) — NOT Tier-C — since the JV is absent from the consolidated Portfolio Statement; flagged per row.",
        "trade_mix: the report's top-level 'Other Trade Sectors' (11.63%) is a mixed residual with no single canonical fit, so it is expanded into its four disclosed sub-sectors (Education/Health/Arts, Construction/Utilities, Accommodation/Food, Transport/Storage) which map cleanly; the other four top-level sectors kept as-disclosed. Sums to 100.0%.",
        "top_tenants.industry: the Top-10 table (p41) has no per-tenant trade-sector column; industry assigned from the tenant's known identity (see inferred[]).",
        "Below-NPI income lines (interest income S$1,020k, other income S$3,041k) are correctly bucketed as statement='adjustment', not 'revenue' (confirmed on the audited Statement of Total Return, p122).",
    ],
    "inferred": [
        {"table": "top_tenants", "field": "industry", "scope": "all 10 rows", "value": None,
         "basis": "Top-10 tenants table (p41) has no trade-sector column; industry mapped from each tenant's known business identity to the canonical 15-value taxonomy.", "source_page": 41},
        {"table": "properties", "field": "market_valuation", "scope": "13 JV data-centre rows (ownership<100%)", "value": None,
         "basis": "USD operational-overview valuation (100% basis, p53/55) used because equity-accounted JV assets are absent from the audited Portfolio Statement (Tier-C).", "source_page": 53},
        {"table": "properties", "field": "lease_term_years", "scope": "leasehold rows", "value": None,
         "basis": "Base head-lease term parsed from the Portfolio Statement 'Term of lease' wording (e.g. '30+30 years' -> 30); full verbatim kept in tenure_raw.", "source_page": 132},
    ],
    "reconciliation": {
        "sum_property_gross_revenue": round(sum_gr_all),
        "reported_total_gross_revenue": k(672991),
        "sum_property_npi": None,
        "reported_total_npi": k(500353),
        "note": "Σ gross revenue over all 86 consolidated property rows (incl. divested-in-year partials) = reported Group gross revenue S$672,991k exactly. The gate's active-only sum is ~2.3% lower (S$657,216k) because four properties divested in-year (2775 Northwoods, The Strategy, The Synergy, Woodlands Central) are marked status=divested but their partial-year revenue remains in the Group total. Per-property NPI is not disclosed (only Group/segment); JV (USD) rows excluded from the SGD reconciliation.",
        "portfolio_valuation_check": {"sum_consolidated_active_valuation": 7183873000,
                                      "reported_fair_value_investment_properties": 7183873000},
    },
})
print("wrote 8 files to", OUT)
print("STR recon net_income:", recon)
