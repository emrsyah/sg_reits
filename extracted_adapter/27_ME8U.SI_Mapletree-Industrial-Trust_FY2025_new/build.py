"""Standalone ME8U.SI FY2025 (FYE 31 Mar 2026) extraction. Run: python build.py
Kernel-independent (eval kernel is shared with sibling agent)."""
import re, json, os

STEM = "27_ME8U.SI_Mapletree-Industrial-Trust_FY2025_new"
MD = f"parsed_reports_datalab/{STEM}/full.md"
OUT = "extracted/ME8U.SI_FY2025"
SYM, FY, CCY = "ME8U.SI", 2025, "SGD"
os.makedirs(OUT, exist_ok=True)

raw = open(MD, encoding="utf-8").read()
_m = [(x.start(), int(x.group(1))) for x in re.finditer(r'<!--\s*PAGE\s+(\d+)\s*-->', raw)]
PAGES = {}
for i, (pos, n) in enumerate(_m):
    e = _m[i + 1][0] if i + 1 < len(_m) else len(raw)
    PAGES[n] = re.sub(r'^<!--\s*PAGE\s+\d+\s*-->', '', raw[pos:e])
assert len(PAGES) == 201 and max(PAGES) == 201
def P(n): return PAGES.get(n, "")

def parse_tables(txt):
    tables, cur = [], None
    for line in txt.splitlines():
        s = line.strip()
        if s.startswith('|') and s.endswith('|'):
            cells = [c.strip() for c in s.strip('|').split('|')]
            if all(re.fullmatch(r':?-+:?', c or '-') for c in cells): continue
            if cur is None: cur = []
            cur.append(cells)
        else:
            if cur is not None: tables.append(cur); cur = None
    if cur is not None: tables.append(cur)
    return tables
def clean(x): return re.sub(r'<[^>]+>', '', str(x)).replace('\\', '').replace('&amp;', '&').strip()
def num(x):
    x = clean(x).replace(',', '').replace('*', '').strip()
    if x in ('', '-', '–', '—', '**', 'N.A.', 'n.a.'): return None
    try: return float(x)
    except Exception: return None
def to100(v): return None if v is None else round(v * 1000)
def cname(x):  # property-name cleaner: drop numeric footnote superscripts, keep real trailing numbers
    return clean(re.sub(r'<sup>\s*\d+(?:\s*,\s*\d+)*\s*</sup>', '', str(x)))
def dmy(s):
    m = re.match(r'(\d{2})/(\d{2})/(\d{4})', clean(s))
    return f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else None
def nk(s):  # normalized match key
    s = clean(s).lower()
    s = re.sub(r'\s+\d+$', '', s)            # trailing footnote number
    s = s.replace('–', '-').replace('—', '-')
    s = re.sub(r'\s*-\s*', '-', s)
    s = re.sub(r'[^a-z0-9]+', '', s)
    return s

# ---------- 1. Audited Portfolio Statement (consolidated, Tier-C SGD) ----------
CAT = {"Data Centres – North America": ("Data Centers", "Data Centre - North America", "United States"),
       "Data Centres – Asia": ("Data Centers", "Data Centre - Asia", None),
       "Hi-Tech Buildings and Business Space": ("Specialized", "Hi-Tech Buildings and Business Space", "Singapore"),
       "General Industrial Buildings": ("Industrial & Logistics", "General Industrial Buildings", "Singapore")}
def norm_section(name):
    n = clean(name).replace('(continued)', '').strip()
    for k in CAT:
        if k.lower() in n.lower(): return k
    return None
def is_hdr(c):
    n = clean(c[0])
    return bool(n) and not n.lower().startswith(('subtotal', 'total')) and all(clean(x) == '' for x in c[1:])
def is_sub(c): return clean(c[0]).lower().startswith(('subtotal', 'total'))
def left_rows(pn):
    for t in parse_tables(P(pn)):
        if 'description of property' in ' '.join(clean(c) for c in t[0]).lower(): return t[1:]
    return []
def right_rows(pn):
    for t in parse_tables(P(pn)):
        h = ' '.join(clean(c) for c in t[0]).lower()
        if 'gross revenue' in h and ('valuation' in h or 'occupancy' in h):
            body = t[1:]
            if body and any('2026' in clean(c) for c in body[0]) and not any(num(c) for c in body[0]):
                body = body[1:]
            return body
    return []

LEFT, RIGHT = [132, 134, 136, 138, 140, 142], [133, 135, 137, 139, 141, 143]
cons = []
for L, R in zip(LEFT, RIGHT):
    pending, cur = [], None
    for c in left_rows(L):
        if is_hdr(c):
            s = norm_section(c[0]); cur = s if s else cur; continue
        pending.append((cur, c))
    for (sec, lc), rc in zip(pending, right_rows(R)):
        if is_sub(lc): continue
        cons.append(dict(section=sec, name=cname(lc[0]), acq=clean(lc[1]), tenure_raw=clean(lc[2]),
                         remaining=clean(lc[3]), location=clean(lc[4]), gross_revenue=num(rc[0]),
                         occupancy=num(rc[2]), val_date=clean(rc[4]), val26=num(rc[5]), src=R))
assert abs(sum(p['val26'] or 0 for p in cons) - 7183873) < 1, "valuation recon failed"
assert abs(sum(p['gross_revenue'] or 0 for p in cons) - 672991) < 1, "revenue recon failed"

# ---------- 2. Operational NLA/GFA maps ----------
def numbered(c): return bool(re.fullmatch(r'\d+\.?', clean(c[0])))
def desc_tabs(pn): return [t for t in parse_tables(P(pn)) if 'description of property' in ' '.join(clean(c) for c in t[0]).lower()]
def is_blank(c): return all(clean(x) == '' for x in c)

# 2a. NA DC operational (USD): NLA, ownership, USD valuations
left_na = []
for pn in (52, 54):
    ts = desc_tabs(pn)
    if ts:
        for c in ts[0]:
            if numbered(c): left_na.append(clean(c[1]))
usd = []
for pn, brk in ((53, False), (55, True)):
    for t in parse_tables(P(pn)):
        h = ' '.join(clean(c) for c in t[0]).lower()
        if 'nla' in h and 'ownership' in h:
            for c in t[1:]:
                if brk and any('GFA' in clean(x) for x in c): break
                if not is_blank(c): usd.append(c)
usd = [c for c in usd if not (num(c[1]) is None and num(c[0]) and num(c[0]) > 2_000_000)]  # drop subtotal
assert len(left_na) == len(usd), (len(left_na), len(usd))
op_na = {}
for name, c in zip(left_na, usd):
    op_na[nk(name)] = dict(name=cname(name), nla=num(c[0]), ownership=num(c[1]), pp_usd=num(c[2]),
                           val25_usd=num(c[3]), val26_usd=num(c[4]), gr=num(c[5]), occ=num(c[6]))

# 2b. Hi-Tech operational (SGD, GFA/NLA)  p57
op_ht = {}
for t in parse_tables(P(57)):
    h = ' '.join(clean(c) for c in t[0]).lower()
    if 'description of property' in h and 'nla' in h:
        for r in t[1:]:
            if numbered(r):
                op_ht[nk(r[1])] = dict(gfa=num(r[6]), nla=num(r[7]))

# 2c. General Industrial operational (SGD, GFA/NLA)  p60 desc + p61 financial
gi_names = []
for t in desc_tabs(60):
    for r in t:
        if numbered(r): gi_names.append(clean(r[1]))
gi_fin = []
for t in parse_tables(P(61)):
    h = ' '.join(clean(c) for c in t[0]).lower()
    if 'gfa' in h and 'nla' in h and 'valuation' in h:
        for r in t[1:]:
            if num(r[0]) and num(r[0]) < 5_000_000:  # skip subtotal (14,071,632)
                gi_fin.append(r)
op_gi = {}
for name, r in zip(gi_names, gi_fin):
    op_gi[nk(name)] = dict(gfa=num(r[0]), nla=num(r[1]))

# 2d. SG DC + Japan DC NLA/GFA (from p55 sub-tables), matched by name
SGJP_AREA = {
    nk("7 Tai Seng Drive"): (256658, 256658), nk("19 Tai Seng Drive"): (92641, 92641),
    nk("Mapletree Sunview 1"): (241796, 241796), nk("STT Tai Seng 1"): (172945, 144295),
    nk("Osaka Data Centre"): (136928, 136928), nk("Tokyo Property"): (319321, 319321),
}

# ---------- 3. Build property rows ----------
DIVESTED = {nk("2775 Northwoods Parkway, Norcross"), nk("The Strategy"), nk("The Synergy"), nk("Woodlands Central")}
def country_of(loc, sec):
    if sec == "Data Centres – North America":
        m = re.search(r',\s*([^,]+?)(?:,\s*USA)?\s*$', clean(loc))
        return "Canada" if "Mississauga" in loc or "Ontario" in loc else "United States"
    if sec == "Data Centres – Asia":
        return "Japan" if ("Japan" in loc or "Osaka" in loc or "Tokyo" in loc) else "Singapore"
    return "Singapore"
def tenure(traw):
    t = clean(traw)
    if not t or t.lower() in ('n.a.', 'freehold') or 'freehold' in t.lower():
        return "Freehold", None
    m = re.search(r'(\d+(?:\.\d+)?)', t.replace('+', ' ').replace('/', ' '))
    return "Leasehold", (float(m.group(1)) if m else None)

def area_for(name, sec):
    k = nk(name)
    if sec == "Data Centres – North America":
        d = op_na.get(k)
        return (None, d['nla'] if d else None)  # NA DC: NLA only, no GFA
    if sec == "Data Centres – Asia":
        if k in SGJP_AREA: g, n = SGJP_AREA[k]; return (g, n)
        return (None, None)
    if sec == "Hi-Tech Buildings and Business Space":
        d = op_ht.get(k); return (d['gfa'], d['nla']) if d else (None, None)
    if sec == "General Industrial Buildings":
        d = op_gi.get(k); return (d['gfa'], d['nla']) if d else (None, None)
    return (None, None)

properties, unmatched = [], []
for p in cons:
    sec = p['section']; cat, craw, _ = CAT[sec]
    k = nk(p['name']); divested = k in DIVESTED
    lt, lty = tenure(p['tenure_raw'])
    gfa, nla = area_for(p['name'], sec)
    if not divested and nla is None and gfa is None:
        unmatched.append((sec, p['name']))
    rec = dict(symbol=SYM, financial_year=FY, property_name=p['name'],
               country=country_of(p['location'], sec), category=cat, category_raw=craw,
               address=p['location'], ownership=100.0,
               market_valuation=to100(p['val26']), valuation_date=dmy(p['val_date']) or ("2026-03-31" if not divested else None),
               currency=CCY, net_property_income=None, gross_revenue=to100(p['gross_revenue']),
               occupancy_rate=p['occupancy'], major_tenants=[],
               gla=None, nla=nla, gfa=gfa, area_unit=("sqft" if (nla or gfa) else None),
               land_tenure=lt, effective_date=None, lease_term_years=lty, lease_expiry_date=None,
               tenure_raw=(p['tenure_raw'] + (f"; remaining term {p['remaining']}" if p['remaining'] and p['remaining'] not in ('N.A.', '–', '-') else "")),
               status=("divested" if divested else "active"),
               flags=[], source_page=p['src'],
               value_basis="consolidated",
               value_basis_note="Audited Portfolio Statement, S$'000 (Tier-C)")
    properties.append(rec)

# 3b. JV data centres (equity-accounted via MRODCT; NOT in audited Portfolio Statement)
cons_keys = {nk(p['name']) for p in cons}
jv_rows = [(k, d) for k, d in op_na.items() if d['ownership'] and d['ownership'] < 100]
assert len(jv_rows) == 13, len(jv_rows)
for k, d in jv_rows:
    country = "Canada" if "Mississauga" in d['name'] else "United States"
    properties.append(dict(
        symbol=SYM, financial_year=FY, property_name=d['name'],
        country=country, category="Data Centers", category_raw="Data Centre - North America (JV)",
        address=d['name'], ownership=d['ownership'],
        market_valuation=to100(d['val26_usd']), valuation_date="2026-03-31",
        currency="USD", net_property_income=None, gross_revenue=to100(d['gr']),
        gross_revenue_currency="SGD",
        occupancy_rate=d['occ'], major_tenants=[],
        gla=None, nla=d['nla'], gfa=None, area_unit="sqft",
        land_tenure="Freehold", effective_date=None, lease_term_years=None, lease_expiry_date=None,
        tenure_raw="Freehold", status="active",
        flags=[{"type": "equity_accounted_joint_venture", "scope": "property",
                "note": "Held via 50%-owned joint venture MRODCT (equity-accounted); "
                        "excluded from the consolidated Portfolio Statement. Valuation is the "
                        "operational-overview US$'000 figure (100% basis), not Tier-C SGD."}],
        source_page=(53 if nk(d['name']) in {nk(x) for x in left_na[:34]} else 55),
        value_basis="joint_venture_100pct",
        value_basis_note="Equity-accounted JV MRODCT; US$'000 operational-overview valuation (100% basis), not Tier-C",
        purchase_price=to100(d['pp_usd']), purchase_price_currency="USD"))

print(f"properties: {len(properties)} ({len(cons)} consolidated + {len(jv_rows)} JV); unmatched area: {len(unmatched)}")
for u in unmatched: print("  UNMATCHED", u)

# save intermediate for the assembly step
json.dump(properties, open(f"extracted_adapter/{STEM}/_properties.json", "w"), indent=1)
print("wrote _properties.json")
