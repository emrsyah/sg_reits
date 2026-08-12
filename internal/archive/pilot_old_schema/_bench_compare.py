"""Cross-model diff: Opus vs Sonnet benchmark extractions (K71U.SI, DHLU.SI)."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).parent
SCALES = (1, 1000, 1_000_000)

def load(model, sym, name):
    p = ROOT / f"_bench_{model}" / f"{sym}_FY2025" / f"{name}.json"
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        return None

def num_eq(a, b, tol=0.005):
    if a is None or b is None:
        return a is b
    try:
        a, b = float(a), float(b)
    except (TypeError, ValueError):
        return str(a).strip().lower() == str(b).strip().lower()
    if a == b:
        return True
    for s in SCALES:
        for x, y in ((a * s, b), (a, b * s)):
            if y and abs(x - y) / max(abs(x), abs(y)) < tol:
                return True
    return False

def norm_name(n):
    if not n: return ""
    n = n.lower().replace("the ", "").replace("&", "and")
    return "".join(c for c in n if c.isalnum())

def report(sym):
    print(f"\n{'='*70}\n{sym}\n{'='*70}")
    match = diff = 0
    diffs = []

    # performance: field-by-field
    po, ps = load("opus", sym, "performance"), load("sonnet", sym, "performance")
    if isinstance(po, list): po = po[0]
    if isinstance(ps, list): ps = ps[0]
    print("\n-- performance --")
    keys = sorted(set(po) | set(ps))
    for k in keys:
        if k in ("source_page", "source_report", "symbol", "fiscal_year", "distribution_record", "notes", "note", "properties_location"):
            continue
        a, b = po.get(k), ps.get(k)
        if isinstance(a, (dict, list)) or isinstance(b, (dict, list)):
            continue
        if num_eq(a, b):
            match += 1
        else:
            diff += 1; diffs.append(("performance", k, a, b))
            print(f"  DIFF {k}: opus={a}  sonnet={b}")

    # properties: match by normalized name
    prop_o = {norm_name(p.get("property_name")): p for p in load("opus", sym, "properties")}
    prop_s = {norm_name(p.get("property_name")): p for p in load("sonnet", sym, "properties")}
    common = set(prop_o) & set(prop_s)
    only_o = set(prop_o) - set(prop_s); only_s = set(prop_s) - set(prop_o)
    print(f"\n-- properties: opus={len(prop_o)} sonnet={len(prop_s)} matched-by-name={len(common)} --")
    if only_o: print(f"  only-opus:   {sorted(only_o)}")
    if only_s: print(f"  only-sonnet: {sorted(only_s)}")
    for n in sorted(common):
        a, b = prop_o[n], prop_s[n]
        for k in ("market_valuation", "gross_revenue", "net_property_income",
                  "occupancy_rate", "ownership", "gla", "nla", "lease_expiry_date",
                  "land_tenure", "value_basis"):
            va, vb = a.get(k), b.get(k)
            if va is None and vb is None: continue
            if num_eq(va, vb):
                match += 1
            else:
                diff += 1; diffs.append((n, k, va, vb))
                print(f"  DIFF {a.get('property_name')}.{k}: opus={va}  sonnet={vb}")

    # top tenants by rank
    tt_o = {t.get("rank"): t for t in load("opus", sym, "top_tenants")}
    tt_s = {t.get("rank"): t for t in load("sonnet", sym, "top_tenants")}
    print("\n-- top_tenants --")
    for r in sorted(set(tt_o) & set(tt_s)):
        a, b = tt_o[r], tt_s[r]
        same_name = norm_name(a.get("tenant_name")) == norm_name(b.get("tenant_name"))
        same_pct = num_eq(a.get("gri_percentage"), b.get("gri_percentage"))
        if same_name and same_pct:
            match += 1
        else:
            diff += 1
            diffs.append((f"tenant#{r}", "", f"{a.get('tenant_name')}|{a.get('gri_percentage')}", f"{b.get('tenant_name')}|{b.get('gri_percentage')}"))
            print(f"  DIFF rank {r}: opus={a.get('tenant_name')} {a.get('gri_percentage')}  sonnet={b.get('tenant_name')} {b.get('gri_percentage')}")

    # income components by (statement, component)
    ic_o = {(c.get("statement"), c.get("component")): c.get("amount") for c in load("opus", sym, "income_components")}
    ic_s = {(c.get("statement"), c.get("component")): c.get("amount") for c in load("sonnet", sym, "income_components")}
    common_ic = set(ic_o) & set(ic_s)
    print(f"\n-- income_components: opus={len(ic_o)} sonnet={len(ic_s)} shared-keys={len(common_ic)} --")
    if set(ic_o) ^ set(ic_s):
        print(f"  only-opus:   {sorted(set(ic_o)-set(ic_s))}")
        print(f"  only-sonnet: {sorted(set(ic_s)-set(ic_o))}")
    for k in sorted(common_ic):
        if num_eq(ic_o[k], ic_s[k]):
            match += 1
        else:
            diff += 1; diffs.append((str(k), "", ic_o[k], ic_s[k]))
            print(f"  DIFF {k}: opus={ic_o[k]}  sonnet={ic_s[k]}")

    # trade mix by category
    tm_o = {norm_name(t.get("category")): t.get("pct") for t in load("opus", sym, "trade_mix")}
    tm_s = {norm_name(t.get("category")): t.get("pct") for t in load("sonnet", sym, "trade_mix")}
    print(f"\n-- trade_mix: opus={len(tm_o)} sonnet={len(tm_s)} shared={len(set(tm_o)&set(tm_s))} --")
    for k in sorted(set(tm_o) & set(tm_s)):
        if num_eq(tm_o[k], tm_s[k]):
            match += 1
        else:
            diff += 1; diffs.append((k, "trade_mix", tm_o[k], tm_s[k]))
            print(f"  DIFF {k}: opus={tm_o[k]}  sonnet={tm_s[k]}")

    # transactions count
    tx_o, tx_s = load("opus", sym, "property_transactions"), load("sonnet", sym, "property_transactions")
    print(f"\n-- transactions: opus={len(tx_o)} rows, sonnet={len(tx_s)} rows --")

    print(f"\nSCORE {sym}: {match} agree / {diff} differ on comparable values")
    return match, diff, diffs

total_m = total_d = 0
for sym in ("K71U.SI", "DHLU.SI"):
    m, d, _ = report(sym)
    total_m += m; total_d += d
print(f"\n{'='*70}\nTOTAL: {total_m} agree / {total_d} differ")
