import re, json

MD = r"parsed_reports_datalab/36_SET.SI_Stoneweg-Europe-Stapled-Trust_FY2024/full.md"
lines = open(MD, encoding="utf-8").read().split("\n")

# page marker map: line index -> printed page
page_at = {}
cur = None
for i, l in enumerate(lines):
    m = re.match(r"<!-- PAGE (\d+) -->", l.strip())
    if m:
        cur = int(m.group(1))
    page_at[i] = cur

def page_for(i):
    return page_at.get(i)

# country header lines (line0-indexed) -> country
country_hdr = []
for i, l in enumerate(lines):
    m = re.match(r"#+ 04 (.+?) ASSETS\s*$", l.strip())
    if m:
        country_hdr.append((i, m.group(1).title().replace("The ", "The ")))

def country_before(idx):
    best = None
    for i, c in country_hdr:
        if i <= idx:
            best = c
    return best

CMAP = {"The Netherlands":"The Netherlands","France":"France","Italy":"Italy",
        "Germany":"Germany","Poland":"Poland","Denmark":"Denmark",
        "Czech Republic":"Czech Republic","Slovakia":"Slovakia",
        "United Kingdom":"United Kingdom","Finland":"Finland"}

# left header lines and right header lines
left_hdrs = [i for i,l in enumerate(lines) if "Acquisition Date | Purchase price" in l]
right_hdrs = [i for i,l in enumerate(lines) if l.startswith("| Valuation as at")]
assert len(left_hdrs)==len(right_hdrs)==10, (len(left_hdrs), len(right_hdrs))

def collect_rows(hdr):
    # skip header + separator, collect contiguous | lines
    out = []
    i = hdr+1
    # skip separator lines like |-|-|
    while i < len(lines):
        l = lines[i].rstrip()
        if l.startswith("|"):
            if re.match(r"^\|[\s\-|]+\|$", l):
                i+=1; continue
            out.append((i, l))
            i+=1
        elif l.strip()=="":
            # allow single blank inside? stop -- tables are contiguous
            break
        else:
            break
    return out

CAT_SUB = {"LOGISTICS / LIGHT INDUSTRIAL":"Industrial & Logistics",
           "OFFICE":"Office", "'OTHERS'":"Specialized", "OTHERS":"Specialized"}

def clean(cell):
    c = re.sub(r"<[^>]+>", "", cell).strip()
    return c

def is_subheader(cells):
    j = clean(cells[0]).upper().strip("'")
    for k in CAT_SUB:
        if j == k.strip("'"):
            return CAT_SUB[k]
    return None

def parse_left(hdr):
    rows = collect_rows(hdr)
    cur_cat = None
    out = []
    for ln, l in rows:
        cells = [c for c in l.split("|")[1:-1]]
        sub = is_subheader(cells)
        if sub:
            cur_cat = sub; continue
        c0 = clean(cells[0])
        if not c0 or c0.lower().startswith("address"): continue
        # strip leading number
        m = re.match(r"^(\d+)\s+(.*)$", c0)
        namecol = m.group(2) if m else c0
        # acquisition date + purchase price are last two non-empty cells
        rest = [clean(c) for c in cells[1:] if clean(c)!=""]
        acq = rest[-2] if len(rest)>=2 else None
        price = rest[-1] if len(rest)>=1 else None
        out.append({"raw_name":namecol, "acq":acq, "price":price, "cat":cur_cat, "line":ln})
    return out

def parse_right(hdr):
    rows = collect_rows(hdr)
    out = []
    for ln, l in rows:
        cells = [clean(c) for c in l.split("|")[1:-1]]
        if is_subheader([cells[0]]): continue
        if not cells[0] or cells[0].lower().startswith("valuation"): continue
        # expect 6 cells: val, area, rev, occ, lease, tenure
        if len(cells) < 6:
            # pad
            cells = cells + [None]*(6-len(cells))
        out.append({"val":cells[0],"area":cells[1],"rev":cells[2],
                    "occ":cells[3],"lease":cells[4],"tenure":cells[5],"line":ln})
    return out

def num(s):
    if s is None: return None
    s = s.replace(",","").replace("€","").replace("%","").strip()
    s = s.replace("(","-").replace(")","")
    try: return float(s)
    except: return None

props = []
for lh, rh in zip(left_hdrs, right_hdrs):
    country = country_before(lh)
    L = parse_left(lh)
    R = parse_right(rh)
    if len(L)!=len(R):
        print(f"!! MISMATCH {country}: left={len(L)} right={len(R)}")
    for li, (a,b) in enumerate(zip(L,R)):
        name = a["raw_name"]
        # name = part before first comma
        pname = name.split(",")[0].strip()
        addr = name
        props.append({
          "country":country, "property_name":pname, "address":addr,
          "category_raw": a["cat"],
          "purchase_price": num(a["price"])*1000 if num(a["price"]) else None,
          "purchase_date": a["acq"],
          "market_valuation": num(b["val"])*1000 if num(b["val"]) else None,
          "nla": num(b["area"]), "gross_revenue": num(b["rev"])*1000 if num(b["rev"]) else None,
          "occupancy_rate": num(b["occ"]),
          "lease_type": b["lease"], "tenure_raw": b["tenure"],
          "page": page_for(b["line"]),
        })
    print(f"{country}: {len(R)} props, val sum {sum(num(x['val']) or 0 for x in R):,.0f}k")

print("TOTAL PROPS:", len(props))
print("TOTAL VAL:", f"{sum(p['market_valuation'] or 0 for p in props):,.0f}")
json.dump(props, open("extracted_adapter/36_SET.SI_Stoneweg-Europe-Stapled-Trust_FY2024/props_raw.json","w"), indent=1, ensure_ascii=False)
