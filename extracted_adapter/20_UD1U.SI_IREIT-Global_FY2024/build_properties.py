import json, re

SRC = r"C:\Users\emirsyah\supertype\s_reits\parsed_reports_datalab\20_UD1U.SI_IREIT-Global_FY2024\full.md"
lines = open(SRC, encoding="utf-8").read().splitlines()

# Portfolio Statement rows live between the STATEMENT OF PORTFOLIO header (line ~7485) and page 183 notes
start = next(i for i,l in enumerate(lines) if l.strip()=="# STATEMENT OF PORTFOLIO")
end = next(i for i,l in enumerate(lines) if "NOTES TO FINANCIAL STATEMENTS" in l and i>start)
block = lines[start:end]

country = None
props = []
page = 180
skip = {"Germany","Spain","France"}
for l in block:
    if "<!-- PAGE" in l:
        m=re.search(r"PAGE (\d+)", l); page=int(m.group(1))
        continue
    if not l.startswith("|"): continue
    cells=[c.strip() for c in l.strip().strip("|").split("|")]
    c0=cells[0]
    # section header rows for country
    if c0 in ("Germany","Spain","France"):
        # only treat as country header if value cols empty
        country=c0
        continue
    if c0.endswith("- Total") or c0.endswith("- carried forward") or c0.endswith("- brought forward"):
        continue
    if c0.startswith("Investment properties") or c0.startswith("Assets held for sale") or c0.startswith("Other assets") or c0.startswith("Net assets"):
        continue
    if not c0 or c0.startswith("Property") or c0 in ("2024","2023") or "EUR'000" in c0 or c0=="":
        continue
    # expect: name | tenure | location | rem2024 | rem2023 | cv2024 | cv2023 | pct2024 | pct2023
    if len(cells) < 7: continue
    tenure_raw=cells[1]
    location=cells[2]
    rem2024=cells[3]
    cv2024=cells[5].replace(",","")
    if not re.match(r"^\(?\d", cv2024): continue
    val=int(cv2024)*1000
    tenure = "Freehold" if tenure_raw.lower().startswith("free") else "Leasehold"
    term=None
    if tenure=="Leasehold":
        try: term=float(rem2024)
        except: term=None
    cat = "Retail" if country=="France" else "Office"
    props.append({
        "symbol":"UD1U.SI","financial_year":2024,
        "property_name":c0,"country":country,
        "category":cat,"category_raw":("Retail" if country=="France" else "Office"),
        "address":location,
        "purchase_price":None,"purchase_price_currency":None,"purchase_date":None,
        "currency":"EUR","valuation_date":"2024-12-31","status":"active","flags":[],
        "source_page":page,
        "gfa":None,"nla":None,"area_unit":None,
        "gross_revenue":None,"gross_revenue_currency":None,"occupancy_rate":None,
        "market_valuation":val,"original_currency":None,"original_value":None,
        "market_valuation_currency":"EUR",
        "land_tenure":tenure,"tenure_raw":tenure_raw,
        "lease_term_years":term,"lease_expiry_date":None,
    })

# add divested Il·lumina (Spain), sold 31 Jan 2024, not in 2024 portfolio statement
props.append({
    "symbol":"UD1U.SI","financial_year":2024,
    "property_name":"Il\u00b7lumina","country":"Spain",
    "category":"Office","category_raw":"Office",
    "address":"Spain","purchase_price":None,"purchase_price_currency":None,"purchase_date":None,
    "currency":"EUR","valuation_date":"2023-12-31","status":"divested","flags":[],
    "source_page":189,
    "gfa":None,"nla":None,"area_unit":None,
    "gross_revenue":None,"gross_revenue_currency":None,"occupancy_rate":None,
    "market_valuation":24500000,"original_currency":None,"original_value":None,
    "market_valuation_currency":"EUR","land_tenure":"Freehold","tenure_raw":"Freehold",
    "lease_term_years":None,"lease_expiry_date":None,
})

OUT=r"C:\Users\emirsyah\supertype\s_reits\extracted\UD1U.SI_FY2024\properties.json"
json.dump(props, open(OUT,"w",encoding="utf-8"), ensure_ascii=False, indent=2)
active=[p for p in props if p["status"]=="active"]
tot=sum(p["market_valuation"] for p in active)
print("rows:",len(props),"active:",len(active))
print("sum active market_valuation (EUR):",tot)
import collections
print(collections.Counter((p["country"],p["category"]) for p in props))
