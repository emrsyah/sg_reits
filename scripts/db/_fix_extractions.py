"""Apply audit-driven fixes to extracted/*.json (dev intermediate). No DB writes.
Idempotent where practical. Prints before/after for each change."""
import json, io

def load(p): return json.load(open(p, encoding="utf-8"))
def save(p, d): json.dump(d, open(p, "w", encoding="utf-8"), indent=2, ensure_ascii=False)

# ---------- M44U P0: divestment 1000x scale ----------
p = "extracted/M44U.SI_FY2025/property_transactions.json"
tx = load(p)
FIELDS = ["sale_price", "valuation", "gain_on_divestment"]
for r in tx:
    if r.get("transaction_type") == "divestment":
        for f in FIELDS:
            v = r.get(f)
            if v is not None and v < 1_000_000:      # guard: only scale the un-scaled ('000) values
                print(f"  M44U txn {r['property_name'][:28]:28} {f}: {v} -> {v*1000}")
                r[f] = v * 1000
save(p, tx)

# ---------- M44U _notes: gain_on_divestment inferred + NLA claim correction ----------
p = "extracted/M44U.SI_FY2025/_notes.json"
n = load(p)
n.setdefault("inferred", []).append({
    "table": "property_transactions", "field": "gain_on_divestment",
    "scope": "all 6 FY25/26 divestments",
    "basis": "derived = sale_price - valuation (premium over independent valuation); AR p49 "
             "discloses Sale Price and Valuation only, no gain line. gain_basis='vs_valuation'.",
    "source_page": 49,
})
for c in n.get("columns_never_fillable", []):
    if "gla" in str(c.get("column", "")).lower():
        c["reason"] = ("GLA/GFA not disclosed per property. NLA (sqm) IS disclosed per property in the "
                       "Property Overview tables (pp. 48-56) and is now captured in properties.net_lettable_area; "
                       "portfolio NLA 8.2m sqm, GFA 8.3m sqm.")
        print(f"  M44U _notes: corrected gla/nla/gfa reason")
save(p, n)

# ---------- N2IU P2: page cite 133 -> 153 (transactions + property flags) ----------
p = "extracted/N2IU.SI_FY2025/property_transactions.json"
tx = load(p)
for r in tx:
    if r.get("source_page") == 133:
        r["source_page"] = 153; print(f"  N2IU txn {r['property_name'][:24]:24} source_page 133 -> 153")
    for k in ("gain_basis_note", "sale_price_basis"):
        if isinstance(r.get(k), str) and "p133" in r[k]:
            r[k] = r[k].replace("p133", "p153"); print(f"  N2IU txn {k}: p133 -> p153")
save(p, tx)

# ---------- N2IU P2: Pinnacle gross_revenue + flag note page fix ----------
p = "extracted/N2IU.SI_FY2025/properties.json"
props = load(p)
for r in props:
    nm = r.get("property_name", "")
    if "Pinnacle" in nm and r.get("gross_revenue") is None:
        r["gross_revenue"] = 12_100_000
        print(f"  N2IU {nm[:24]:24} gross_revenue None -> 12,100,000 (50% effective SGD share, AR p47)")
    for fl in r.get("flags", []):
        note = fl.get("note", "")
        if "p133" in note:
            fl["note"] = note.replace("p133", "p153"); print(f"  N2IU {nm[:24]:24} flag note p133 -> p153")
save(p, props)

# record the Pinnacle inference in N2IU _notes
p = "extracted/N2IU.SI_FY2025/_notes.json"
n = load(p)
n.setdefault("inferred", []).append({
    "table": "properties", "field": "gross_revenue", "property_name": "The Pinnacle Gangnam",
    "value": 12_100_000,
    "basis": "50% effective SGD share from Properties-at-a-Glance card (KRW13,280.8m = S$12.1m); "
             "equity-accounted JV, absent from consolidated Portfolio Statement. NPI taken from same card.",
    "source_page": 47,
})
save(p, n)
print("definite fixes applied.")
