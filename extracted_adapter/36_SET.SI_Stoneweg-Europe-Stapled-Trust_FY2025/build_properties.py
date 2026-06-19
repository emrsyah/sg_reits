import json, re

MD = "parsed_reports_datalab/36_SET.SI_Stoneweg-Europe-Stapled-Trust_FY2025/full.md"
lines = open(MD, encoding="utf-8").read().splitlines()

def page_line(n):
    for i,l in enumerate(lines):
        if l.strip()==f"<!-- PAGE {n} -->":
            return i
    raise ValueError(n)

start, end = page_line(174), page_line(186)
region = lines[start:end]

COUNTRIES = {"The Netherlands","France","Italy","Germany","Poland","Denmark",
             "Czech Republic","United Kingdom","Finland","Slovakia"}
CLASSES = {"Logistics / Light Industrial","Office","'Others'"}

def clean(x): return re.sub(r"</?b>","",re.sub(r"<sup>.*?</sup>","",x)).replace("<br>"," ").replace("<br/>"," ").strip()

names=[]; values=[]
cur_country=None; cur_cls=None; cur_page=174
name_pages={174,176,178,180,182,184}; val_pages={175,177,179,181,183,185}
for l in region:
    m=re.match(r"<!-- PAGE (\d+) -->", l.strip())
    if m: cur_page=int(m.group(1)); continue
    if not l.strip().startswith("|"): continue
    cells=[clean(c) for c in l.strip().strip("|").split("|")]
    c0=cells[0]
    if c0 in("Property (by Geography)","Land Tenure"): continue
    if c0 in COUNTRIES and all(x=="" for x in cells[1:]): cur_country=c0; continue
    if c0 in CLASSES and all(x=="" for x in cells[1:]): cur_cls=c0; continue
    if cur_page in name_pages:
        if c0 and not c0.startswith("n/a") and len(cells)>=3 and (cells[1] or cells[2]):
            names.append(dict(country=cur_country,cls=cur_cls,name=c0,location=cells[1],acq=cells[2],page=cur_page))
    if cur_page in val_pages and len(cells)>=6:
        tenure=cells[0]; rem=cells[1]; sert2025=cells[5]
        if tenure=="": continue
        values.append(dict(tenure=tenure,remaining=rem,val=sert2025,page=cur_page))

assert len(names)==len(values), (len(names),len(values))

CAT={"Logistics / Light Industrial":"Industrial & Logistics","Office":"Office","'Others'":"Specialized"}
# divested / held-for-sale footnote map (from pages 178,180,184)
DIVESTED={"Maxima","Cassiopea 1-2-3","Arkońska Business Park",
          "Nove Mesto ONE Industrial Park I","Nove Mesto ONE Industrial Park III",
          "Nove Mesto ONE Industrial Park II","Kosice Industrial Park","Zilina Industrial Park"}
HELD_FOR_SALE={"Purotie 1": 2495}  # carried in current assets at 2,495 (p240)

def tenure_enum(t):
    tl=t.lower()
    if tl=="freehold": return "Freehold"
    return "Leasehold"  # any leasehold/usufruct/right of superficies/part-freehold-part-leasehold

def parse_years(rem):
    rem=rem.replace("Various","").strip()
    m=re.search(r"(\d+\.?\d*)", rem)
    return float(m.group(1)) if m else None

props=[]
for n,v in zip(names,values):
    name=n["name"]
    if set(name)<=set("-") or n["cls"] is None:
        continue
    val=v["val"].replace(",","").replace("–","").strip()
    val_abs=float(val)*1000 if val and val not in("-","") else None
    status="active"; flags=[]
    if name in DIVESTED:
        status="divested"; val_abs=None
    if name in HELD_FOR_SALE:
        status="held_for_sale"; val_abs=float(HELD_FOR_SALE[name])*1000
    cat=CAT[n["cls"]]
    cat_raw=n["cls"]
    if name=="Starhotels Grand Milan":
        flags.append({"type":"asset_type_note","scope":"category","note":"Hotel (480-room) classified by trust under 'Others' segment; mapped to Specialized"})
    rec={
        "symbol":"SET.SI","financial_year":2025,"property_name":name,
        "country":n["country"],"category":cat,"category_raw":cat_raw,
        "address":n["location"],"ownership":100.0,
        "market_valuation":val_abs,"valuation_date":"2025-12-31","currency":"EUR",
        "net_property_income":None,"gross_revenue":None,"npi_pct":None,
        "occupancy_rate":None,"major_tenants":[],
        "gla":None,"nla":None,"gfa":None,
        "land_tenure":tenure_enum(v["tenure"]),
        "effective_date":None,"lease_term_years":None,"lease_expiry_date":None,
        "tenure_raw":v["tenure"] + (f"; remaining term {v['remaining']} years (as disclosed)" if v["remaining"] not in("n/a","") else ""),
        "status":status,"flags":flags,"source_page":v["page"],
    }
    # derive lease_expiry_date from disclosed remaining term (single clean value), flag as inferred
    rem=v["remaining"]
    if rec["land_tenure"]=="Leasehold" and rem not in("n/a","") and "-" not in rem and "Various" not in rem:
        yrs=parse_years(rem)
        if yrs:
            from datetime import date,timedelta
            exp=date(2025,12,31)+timedelta(days=round(yrs*365.25))
            rec["lease_expiry_date"]=exp.isoformat()
            rec["flags"].append({"type":"lease_expiry_derived","scope":"lease_expiry_date",
                "note":f"Derived as 2025-12-31 + remaining term {rem} yrs (Statement of Portfolio discloses remaining-term-years, not an expiry date)."})
    if name=="Central Plaza":
        rec["lease_expiry_date"]="2088-07-31"
        rec["tenure_raw"]="Freehold/leasehold; remaining term 62.6 years; part freehold and part leasehold interest ending 31 July 2088 (footnote 1)"
    props.append(rec)

out="extracted/SET.SI_FY2025/properties.json"
json.dump(props, open(out,"w",encoding="utf-8"), indent=2, ensure_ascii=False)
active=sum(1 for p in props if p["status"]=="active")
tot=sum(p["market_valuation"] or 0 for p in props if p["status"]=="active")
print("rows",len(props),"active",active,"Σ active val",tot, "=2,152,528,000?")
