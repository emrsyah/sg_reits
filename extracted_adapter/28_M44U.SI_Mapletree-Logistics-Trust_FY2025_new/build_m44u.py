"""Self-contained M44U.SI FY2025 (declared FY; statement 31 Mar 2026) extraction build.
Deterministic parse of the audited Group Portfolio Statement (physical pp.132-167) +
hardcoded audited-statement figures (verified against source pages). Process-isolated."""
import re, json, os

STEM = "28_M44U.SI_Mapletree-Logistics-Trust_FY2025_new"
MD = f"parsed_reports_datalab/{STEM}/full.md"
OUT = "extracted/M44U.SI_FY2025"
K = 1000

txt = open(MD, encoding="utf-8").read()
parts = re.split(r'<!-- PAGE (\d+) -->', txt)
pages = {int(parts[i]): parts[i+1] for i in range(1, len(parts), 2)}

COUNTRIES = {'Singapore','Australia','China','Hong Kong SAR','India','Japan',
             'Malaysia','South Korea','Vietnam'}

def rows_of(body):
    out = []
    for ln in body.splitlines():
        s = ln.strip()
        if s.startswith('|') and s.endswith('|'):
            out.append([c.strip() for c in s.strip('|').split('|')])
    return out

def clean(s):
    s = re.sub(r'<sup>.*?</sup>', '', s)
    s = re.sub(r'<[^>]+>', '', s)
    return s.replace('\\', '').strip()

def stripfn(nm):
    return re.sub(r'\s*\(([a-z])\)\s*$', '', nm).strip()

def num(s):
    s = s.replace(',', '').strip()
    if s in ('', '—', '–', '-', '**'):
        return None
    try:
        return float(s)
    except ValueError:
        return None

def is_bold_header(c0):
    return c0.startswith('<b>')

# ---- parse Group Portfolio Statement, left (desc) + right (values) paired per page ----
def left_rows(body, cc):
    out = []
    for r in rows_of(body):
        c0 = r[0]
        if is_bold_header(c0):
            nm = clean(c0).replace('(continued)', '').strip()
            if nm in COUNTRIES:
                cc[0] = nm
            continue
        if len(r) >= 5 and c0 and not is_bold_header(c0):
            name, date = clean(c0), clean(r[1])
            if name and date and re.search(r'\d', date):
                out.append({'country': cc[0], 'name': name, 'date': date,
                            'term': clean(r[2]), 'remaining': clean(r[3]),
                            'location': clean(r[4])})
    return out

def right_rows(body):
    out, started = [], False
    for r in rows_of(body):
        if 'valuation at' in ' '.join(r).lower():
            started = True
            continue
        if not started:
            continue
        if all(c.strip('-| ') in ('', '-') for c in r):
            continue
        if len(r) >= 7:
            out.append({'gross': clean(r[1]), 'occ': clean(r[3]),
                        'vdate': clean(r[5]), 'val': clean(r[6])})
    return out

records, cc, pg = [], [None], 132
while pg <= 167:
    body = pages[pg]
    if '### MLT' in body:
        body = body.split('### MLT')[0]
    rws = rows_of(body)
    is_left = any('description of property' in ' '.join(r).lower() for r in rws[:3])
    if not is_left:
        pg += 1
        continue
    L = left_rows(body, cc)
    rb = pages[pg+1]
    if '### MLT' in rb:
        rb = rb.split('### MLT')[0]
    R = right_rows(rb)
    for i, lp in enumerate(L):
        rec = dict(lp)
        rec.update(R[i] if i < len(R) else {})
        rec['src'] = pg
        records.append(rec)
    pg += 2

DIV6 = {"1 Genting Lane", "8 Tuas View Square", "31 Penjuru Lane", "Subang 2",
        "Mapletree Logistics Centre– Yeosu", "Mapletree Logistics Centre – Yeosu",
        "28 Bilston Drive,Barnawartha North, VIC"}
COMPARATIVES = {"119 Neythal Road", "Mapletree Xi'an Logistics Park", "Toki Centre",
                "Aichi Miyoshi Centre", "Flexhub", "Celestica Hub", "Zentraline", "Linfox"}

def parse_term(term):
    t = term.strip()
    if 'freehold' in t.lower():
        return 'Freehold', None, None
    m = re.match(r'\s*(\d+)', t)
    yrs = float(m.group(1)) if m else None
    flag = None
    if '/' in t or re.search(r'\d+\+\d+.*\d+\+\d+', t):
        flag = f"options/dual tenure disclosed: '{t}'; base head-lease term stored"
    tenure = 'Leasehold' if (yrs or 'year' in t.lower()) else None
    return tenure, yrs, flag

def to_iso(d):
    m = re.match(r'(\d{2})/(\d{2})/(\d{4})', d)
    return f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else None

props = []
for r in records:
    nm = stripfn(r['name'])
    if nm in COMPARATIVES:
        continue
    val, occ, gross = num(r.get('val', '')), num(r.get('occ', '')), num(r.get('gross', ''))
    tenure, yrs, tflag = parse_term(r.get('term', ''))
    status = 'divested' if nm in DIV6 else 'active'
    p = {"symbol": "M44U.SI", "financial_year": 2025, "property_name": nm,
         "country": r['country'], "category": "Industrial & Logistics",
         "category_raw": "Logistics Properties", "address": r['location'],
         "ownership": 100.0,
         "market_valuation": int(round(val*K)) if val else None,
         "valuation_date": "2026-03-31" if val else None, "currency": "SGD",
         "net_property_income": None,
         "gross_revenue": int(round(gross*K)) if gross else None,
         "occupancy_rate": occ, "major_tenants": [],
         "land_tenure": tenure, "lease_term_years": yrs,
         "tenure_raw": r.get('term') or None, "lease_expiry_date": None,
         "purchase_date": to_iso(r.get('date', '')),
         "status": status, "flags": [], "source_page": r['src']}
    if tflag:
        p["lease_terms_flags"] = tflag
    if nm == "37 Penjuru Lane":
        p["flags"].append({"type": "nil_valuation", "scope": "property",
            "note": "land lease <1 year remaining; valued nil though still operating (32% occ)"})
    if status == 'divested':
        p["flags"].append({"type": "divested_in_year", "scope": "property",
            "note": "divested during FY25/26; nil valuation at 31/03/2026; partial-year gross revenue"})
    props.append(p)

active = [p for p in props if p['status'] == 'active']
sum_active_gross = sum(p['gross_revenue'] for p in active if p['gross_revenue'])
sum_val = sum(p['market_valuation'] for p in props if p['market_valuation'])

# ---------------- financial (audited Statement of Total Return, Group 2026) ----------
SP = 121  # Statements of Profit or Loss (physical page)
ism = {
 "total_revenue": 708274*K, "cost_of_revenue": 98118*K, "gross_income": 610156*K,
 "operating_income": 515377*K, "operating_expense": 94779*K,
 "ebit": 531420*K, "ebitda": 531420*K, "pretax_income": 380646*K,
 "income_taxes": 101806*K, "net_income": 278840*K,
 "non_operating_income_or_loss": -134731*K, "interest_expense_non_operating": 150774*K,
 "diluted_shares_outstanding": 5130149*K, "weighted_avg_shares_basic": 5098108*K,
 "net_property_sales": 45*K, "funds_from_operation": None,
 "unitholders": 254468*K, "perpetual_security_holders": 22641*K, "minorities": 1731*K,
 "revenue_breakdown": [
   {"category": "Rental income", "amount": 612834*K, "class": "Product/Service Sales"},
   {"category": "Service charges", "amount": 82581*K, "class": "Product/Service Sales"},
   {"category": "Other operating income", "amount": 12859*K, "class": "Other income"}],
 "operating_expense_breakdown": [
   {"category": "Manager's management fees", "amount": 89010*K, "class": "General & Admin"},
   {"category": "Trustee's fees", "amount": 1775*K, "class": "General & Admin"},
   {"category": "Other trust expenses, net", "amount": 3994*K, "class": "Other expenses"}],
 "_derived": ["operating_income", "ebit", "ebitda",
              "non_operating_income_or_loss", "interest_expense_non_operating"],
}
line_items = [
 {"statement": "revenue", "component": "gross_revenue", "amount": 708274*K, "label_raw": "Gross revenue", "source_page": SP},
 {"statement": "expense", "component": "property_expenses", "amount": 98118*K, "label_raw": "Property expenses", "source_page": SP},
 {"statement": "expense", "component": "management_fee_base_and_performance", "amount": 89010*K, "label_raw": "Manager's management fees", "source_page": SP},
 {"statement": "expense", "component": "trustee_fee", "amount": 1775*K, "label_raw": "Trustee's fees", "source_page": SP},
 {"statement": "expense", "component": "finance_costs", "amount": 153306*K, "label_raw": "Borrowing costs", "source_page": SP},
 {"statement": "expense", "component": "income_tax", "amount": 101806*K, "label_raw": "Income tax expense", "source_page": SP},
 {"statement": "adjustment", "component": "interest_income", "amount": 2532*K, "label_raw": "Interest income", "source_page": SP},
 {"statement": "adjustment", "component": "other_trust_expenses_net", "amount": -3994*K, "label_raw": "Other trust (expenses)/income, net", "source_page": SP},
 {"statement": "adjustment", "component": "net_change_fair_value_financial_derivatives", "amount": -32845*K, "label_raw": "Net change in fair value of financial derivatives", "source_page": SP},
 {"statement": "adjustment", "component": "net_movement_value_investment_properties", "amount": 48843*K, "label_raw": "Net movement in the value of investment properties", "source_page": SP},
 {"statement": "adjustment", "component": "gain_on_disposal_of_subsidiaries", "amount": 45*K, "label_raw": "Gain on disposal of subsidiaries", "source_page": SP},
]
financial = {"symbol": "M44U.SI", "financial_year": 2025, "currency": "SGD",
 "income_stmt_metrics": ism,
 "balance_sheet_metrics": {"total_asset": 13694597*K, "total_equity": 7076920*K,
   "total_liabilities": 6617677*K, "working_capital": (397562-393434)*K,
   "total_current_asset": 397562*K, "total_non_current_asset": 13297035*K,
   "total_current_liabilities": 393434*K, "total_non_current_liabilities": 6224243*K},
 "cash_flow_metrics": {"operating_cash_flow": 542145*K, "investing_cash_flow": -52163*K,
   "financing_cash_flow": -482837*K, "net_cash_flow": 7145*K, "free_cash_flow": None,
   "capital_expenditure": 120556*K},
 "employee_breakdown": None, "line_items": line_items, "source_page": SP}

# ---------------- profile / performance ----------------
profile = {"symbol": "M44U.SI", "sub_sector": "Industrial",
 "management": {
   "reit_manager": ["Mapletree Logistics Trust Management Ltd."],
   "trustee": ["HSBC Institutional Trust Services (Singapore) Limited"],
   "sponsor": ["Mapletree Investments Pte Ltd"],
   "property_manager": ["Mapletree Property Management Pte. Ltd."]},
 "income_model": "conventional", "source_page": 24}

performance = {"symbol": "M44U.SI", "financial_year": 2025,
 "portfolio_value": 13076200000,
 "properties_location": "Singapore, Hong Kong SAR, China, Japan, South Korea, Australia, Malaysia, Vietnam, India",
 "gross_revenue": 708274*K, "net_property_income": 610156*K,
 "net_distributable_income": 370067*K,
 "distributable_income_opening": 99868*K, "distribution_cash_paid": 376135*K,
 "distributable_income_closing": 93800*K,
 "distribution_paid": None, "distribution_basis": "full_payout_no_retention_line",
 "dpu": 7.262,
 "distribution_record": [
   {"period": "1Q FY25/26 (1 Apr-30 Jun 2025)", "dpu": 1.812, "ex_date": None, "pay_date": None},
   {"period": "2Q FY25/26 (1 Jul-30 Sep 2025)", "dpu": 1.815, "ex_date": None, "pay_date": None},
   {"period": "3Q FY25/26 (1 Oct-31 Dec 2025)", "dpu": 1.816, "ex_date": None, "pay_date": None},
   {"period": "4Q FY25/26 (1 Jan-31 Mar 2026)", "dpu": 1.819, "ex_date": None, "pay_date": None}],
 "number_of_unitholders": 34600, "number_of_shareholder_units": 5110907*K,
 "aggregate_leverage": 40.6, "interest_coverage_ratio": 2.9, "cost_of_debt": 2.6,
 "weighted_avg_debt_maturity": 3.6, "nav_per_unit": 1.26, "wale": 2.5,
 "portfolio_occupancy": 96.9, "currency": "SGD", "date": "2026-03-31",
 "flags": [{"type": "number_of_unitholders_dated_post_year_end", "scope": "performance",
            "note": "Statistics of Unitholdings as at 29 May 2026 (post FY-end)"}],
 "source_page": 6}

# ---------------- top_tenants / trade_mix ----------------
tt = [("Equinix", 3.7), ("CWT", 3.5), ("Coles Group", 2.1), ("HKTV", 1.8),
      ("S.F. Express", 1.7), ("Coupang Inc.", 1.5), ("Bidvest Group", 1.5),
      ("YCH Group", 1.4), ("Cainiao", 1.3), ("GXO Logistics", 1.2)]
top_tenants = [{"symbol": "M44U.SI", "financial_year": 2025, "rank": i+1,
    "client_name": n, "industry": None, "revenue_pct": p,
    "pct_basis": "gross_revenue", "source_page": 52} for i, (n, p) in enumerate(tt)]

TM = [("F&B", 14, "Food & Beverages"),
      ("Consumer Staples", 15, "Departmental Store/Supermarket"),
      ("Fashion, Apparel & Cosmetics", 6, "Fashion & Accessories"),
      ("Furniture & Furnishings", 3, "Other Retail Trades"),
      ("Automobiles", 6, "Other Industrial Trades"),
      ("Healthcare", 4, "Healthcare & Wellness"),
      ("Retail", 5, "Other Retail Trades"),
      ("Electronics & IT", 10, "IT & Telecommunications"),
      ("Others", 17, "Other Industrial Trades"),
      ("Materials, Construction & Engineering", 6, "Infrastructure, Real Estate & Property Services"),
      ("Oil, Gas, Energy & Marine", 2, "Energy, Mining & Resources"),
      ("Chemicals", 3, "Other Industrial Trades"),
      ("Document Storage", 1, "Other Industrial Trades"),
      ("Commercial Printing", 1, "Other Industrial Trades"),
      ("Information Communication Technology", 4, "IT & Telecommunications"),
      ("Commodities", 3, "Other Industrial Trades")]
trade_mix = [{"symbol": "M44U.SI", "financial_year": 2025, "category": cat,
    "category_raw": raw, "pct": float(p), "pct_basis": "gross_revenue",
    "source_page": 53} for raw, p, cat in TM]

# ---------------- property_transactions ----------------
def divrec(name, ctry, sale, val, date, buyer, localnote):
    gain = round(sale - val, 1)
    return {"symbol": "M44U.SI", "financial_year": 2025, "transaction_type": "divestment",
     "status": "completed", "property_name": name,
     "deal_id": f"M44U.SI:{re.sub(r'[^a-z0-9]+','_',name.lower()).strip('_')}:divestment:2025",
     "transaction_date": date, "completed_date": date,
     "sale_price": int(round(sale*K)), "sale_price_currency": "SGD",
     "valuation": int(round(val*K)), "valuation_currency": "SGD",
     "gain_on_divestment": int(round(gain*K)), "gain_loss_pct": round(gain/val*100, 1),
     "gain_basis": "vs_valuation", "counterparty": buyer, "country": ctry,
     "currency": "SGD", "source_type": "annual_report", "source_page": 49,
     "sale_price_basis": localnote}

property_transactions = [
 divrec("1 Genting Lane", "Singapore", 12.3, 9.1, "2025-05-13", "House of Teak (Singapore) Pte. Ltd.", "S$12.3m consideration"),
 divrec("8 Tuas View Square", "Singapore", 11.2, 8.0, "2025-06-12", "Rapid (S.E.A.) Engineering Pte. Ltd.", "S$11.2m consideration"),
 divrec("31 Penjuru Lane", "Singapore", 7.8, 7.3, "2025-07-15", "Prospa Group Pte. Ltd.", "S$7.8m consideration"),
 divrec("Subang 2", "Malaysia", 9.5, 7.3, "2025-07-17", "Hello Marketing (M) Sdn Bhd", "MYR31.5m (S$9.5m); valuation MYR24.0m (S$7.3m)"),
 divrec("Mapletree Logistics Centre - Yeosu", "South Korea", 7.4, 7.3, "2025-08-29", "DIH Co., Ltd.", "KRW8,000m (S$7.4m); valuation KRW7,900m (S$7.3m)"),
 divrec("28 Bilston Drive, Barnawartha North, Victoria", "Australia", 51.0, 47.6, "2025-10-13", "Exactus Bilston Pty Ltd", "AUD60.0m (S$51.0m); valuation AUD56.0m (S$47.6m)"),
]
property_transactions.append({"symbol": "M44U.SI", "financial_year": 2025,
 "transaction_type": "acquisition", "status": "completed",
 "property_name": "Mapletree (Bhiwandi) Logistics Park",
 "deal_id": "M44U.SI:mapletree_bhiwandi_logistics_park:acquisition:2025",
 "transaction_date": "2026-03-27", "completed_date": "2026-03-27",
 "purchase_price": 53200000, "purchase_price_currency": "SGD",
 "valuation": 54050000, "valuation_currency": "SGD",
 "valuation_basis": "INR3,949 million converted at disclosed rate S$1.00=INR73.06",
 "counterparty": "G10 Asia Holding Pte. Ltd. and Skyper Spaces LLP", "country": "India",
 "currency": "SGD",
 "purchase_price_basis": "INR3,888 million (S$53.2m) at disclosed rate S$1.00=INR73.06",
 "source_type": "annual_report", "source_page": 48})

# ---------------- _notes ----------------
_notes = {
 "columns_never_fillable": [
  {"column": "properties.net_property_income", "reason": "Per-property NPI not disclosed; only portfolio total (S$610.2m) and geographic segment NPI shares given."},
  {"column": "properties.gla / nla / gfa", "reason": "Per-property area not disclosed this FY (FY24/25 per-property overview cards replaced by market-overview sections); NLA/GFA disclosed only at country-segment and portfolio level (portfolio NLA 8.2m sqm, GFA 8.3m sqm)."},
  {"column": "properties.lease_expiry_date", "reason": "Audited Portfolio Statement discloses 'Term of lease' and 'Remaining term of lease' (approx. years), not a per-property expiry date."},
  {"column": "properties.major_tenants", "reason": "Per-property tenant lists not disclosed; only a portfolio-level Top 10 customers table (page 52)."}],
 "data_with_no_home": [
  "Portfolio NLA 8.2m sqm; GFA 8.3m sqm (portfolio-level)",
  "Gross revenue by geography (SG 29.9%, HK 16.9%, China 15.1%, Japan 11.5%, SK 7.5%, Australia 7.0%, Malaysia 6.3%, Vietnam 4.7%, India 1.1%)",
  "Segment NPI shares (SG 29.6%, HK 18.4%, China 13.4%, Japan 11.3%)",
  "SUA vs MTB gross revenue split (SUA 21.1% / MTB 78.9%)",
  "83% of debt fixed-rate; 75% of next-FY income hedged into SGD; 91.4% of debt unsecured; debt headroom S$2,575.0m to 50% limit",
  "Total return since listing 292%",
  "Adjusted DPU excl divestment gains: FY24/25 7.519 cents (FY25/26 unchanged 7.262)"],
 "parsing_traps": [
  "Audited Group Portfolio Statement (physical pp.132-167) splits each spread into a LEFT description table and a RIGHT valuation table; matched 1:1 positionally per page.",
  "8 properties divested in FY24/25 (119 Neythal Road; Xi'an Logistics Park; Toki Centre; Aichi Miyoshi Centre; Flexhub; Celestica Hub; Zentraline; Linfox) still appear in the FY25/26 Portfolio Statement as prior-year comparatives (nil FY25/26 revenue & valuation); EXCLUDED from properties.",
  "6 FY25/26 divestments (nil valuation at 31/03/2026, partial-year gross revenue) captured with status='divested' (excluded from the gross-revenue reconciliation) and in property_transactions.",
  "37 Penjuru Lane: land lease <1 year remaining -> valued nil in the Portfolio Statement though still operating (32% occ, S$1.365m FY25/26 revenue); kept status='active' (part of the 175).",
  "trade_mix is 'Gross Revenue Breakdown by Trade Sector' for the MONTH ended 31 March 2026 (pct_basis=gross_revenue); Electronics & IT and Information Communication Technology both map to IT & Telecommunications (kept as separate rows via category_raw).",
  "Divestment-gains distribution CEASED in FY25/26 (contributed S$27.0m in FY24/25) -> lower amount distributable / DPU; captured as disclosed.",
  "financial uses the GROUP column (2026) = FY25/26; MLT (parent) columns ignored.",
  "net_property_sales set to S$45k (Gain on disposal of subsidiaries, the only explicit disposal gain in the Statement of Profit or Loss); property divestment gains are embedded in the Net movement in value of investment properties line, not separable."],
 "reconciliation": {
  "sum_property_gross_revenue": sum_active_gross,
  "reported_total_gross_revenue": 708274*K,
  "note_gross": "Active-property sum excludes 6 in-year divested rows (S$3.112m partial-year revenue); active+divested sum = 708.274m = reported total.",
  "sum_property_valuation": sum_val,
  "reported_total_valuation": 12994254*K,
  "note_valuation": "Sum of individual property valuations = S$12,994.254m = the audited 'Fair value of investment properties' line; + right-of-use assets S$81.432m + ARO S$0.477m = total investment properties S$13,076.163m (SOFP).",
  "sum_property_npi": None, "reported_total_npi": 610156*K,
  "note_npi": "Per-property NPI not disclosed; portfolio NPI S$610.156m."},
 "inferred": [
  {"table": "properties", "field": "ownership", "scope": "all rows", "value": 100.0,
   "basis": "Consolidated Group Portfolio Statement presents 100% carrying values; per-property ownership % not disclosed. Group carries small non-controlling interests (S$22.88m, ~0.3% of equity) on a few subsidiaries.", "source_page": 123},
  {"table": "properties", "field": "lease_term_years", "scope": "rows with 'X+Y years' tenure",
   "basis": "Stored the base head-lease term X (separable) from disclosed 'X+Y years'; option/dual period noted in lease_terms_flags where ambiguous.", "source_page": 132},
  {"table": "property_transactions", "field": "valuation", "scope": "Mapletree (Bhiwandi) Logistics Park",
   "value": 54050000, "basis": "INR3,949m converted at the disclosed rate S$1.00=INR73.06 (purchase_price S$53.2m disclosed directly).", "source_page": 48}]
}

os.makedirs(OUT, exist_ok=True)
files = {"profile": profile, "performance": performance, "properties": props,
         "property_transactions": property_transactions, "top_tenants": top_tenants,
         "trade_mix": trade_mix, "financial": financial, "_notes": _notes}
for name, obj in files.items():
    with open(f"{OUT}/{name}.json", "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

# self-checks
srev = sum(l['amount'] for l in line_items if l['statement'] == 'revenue')
sexp = sum(l['amount'] for l in line_items if l['statement'] == 'expense')
sadj = sum(l['amount'] for l in line_items if l['statement'] == 'adjustment')
print("wrote", len(files), "files ->", OUT)
print("properties:", len(props), "active:", len(active),
      "divested:", len(props)-len(active))
print("STR recon net_income:", srev-sexp+sadj, "==", ism['net_income'],
      srev-sexp+sadj == ism['net_income'])
print("active gross:", sum_active_gross, "vs 708,274,000 diff",
      708274*K - sum_active_gross, f"({(708274*K-sum_active_gross)/(708274*K)*100:.2f}%)")
print("valuation:", sum_val, "vs 12,994,254,000")
print("trade_mix sum:", sum(t['pct'] for t in trade_mix))
