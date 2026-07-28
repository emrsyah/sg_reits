"""Project dev sgx_reit_*_final  ->  sgx_manual_input  (pure OURS, no Excel, no FX).

Implements docs/reits_db_handoff/manual_input_mapping.md. Supersedes the Excel-hybrid
prod_upsert_manual_input.py / SGX REIT upsert.ipynb: financials now come from our own
financial_final (already SGD, Evelyn-locked conventions), not the colleague's workbook.

One row per (symbol, financial_year), composed from:
  income_stmt_metrics  <- financial_final.income_stmt_metrics  (copy 1:1, DROP 'depreciation'
                          which is ours-only and not a manual_input key)
  balance_sheet_metrics/cash_flow_metrics/employee_breakdown <- financial_final (copy)
  sankey_component     <- derived from income_stmt (make_sankey_component, verbatim from notebook)
  source_url/date      <- performance_final
  financial_year       <- DERIVE from performance_final.date via the declared-FY rule (Jan-Jun -> X-1)
  industry_breakdown   <- composed:
      top_10_gri%_customers          <- top_tenant_final   (top-10 by revenue_pct, /100)
      gross_rental_income_by_sectors <- trade_mix_final    ({category: pct/100}, summed per category)
      property_portfolio_top_20      <- property_final     (top-20 by gross_revenue; renamed; /100 pcts)
      property_counts_by_country     <- property_final     ({country:{category:[n, sum_gross, sum_val]}})
      distribution_metrics           <- performance_final  (section 2 formulas)

Children are keyed by the SAME declared FY as financial_final (build_final makes every *_final
table declared-FY consistent), so we join on financial_year directly.

prod sgx_manual_input keys symbols WITHOUT '.SI' -> stripped only at the write boundary.

Usage:
  python scripts/db/build_manual_input_from_final.py                 # DRY, all REIT (symbol,fy)
  python scripts/db/build_manual_input_from_final.py --symbols C38U,M44U
  python scripts/db/build_manual_input_from_final.py --fy 2024 --verify   # diff vs prod
  python scripts/db/build_manual_input_from_final.py --symbols C38U --write   # upsert to prod
DRY by default; nothing hits prod without --write.
"""
import os, sys, json, math, argparse, datetime, decimal, urllib.request, urllib.error
import psycopg2
from dotenv import load_dotenv
load_dotenv(".env")


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbols", help="comma list of .SI or bare tickers (default: all in financial_final)")
    ap.add_argument("--fy", type=int, help="single DECLARED financial_year")
    ap.add_argument("--verify", action="store_true", help="diff each built row vs current prod")
    ap.add_argument("--write", action="store_true", help="upsert to prod sgx_manual_input")
    ap.add_argument("--limit-preview", type=int, default=2)
    return ap.parse_args()


def declared_fy(date):
    d = datetime.date.fromisoformat(str(date)[:10])
    return d.year - 1 if d.month <= 6 else d.year


def jnum(v):
    if isinstance(v, decimal.Decimal):
        f = float(v)
        return int(f) if f.is_integer() else f
    return v


def sanitize(o):
    if isinstance(o, dict):
        return {k: sanitize(v) for k, v in o.items()}
    if isinstance(o, list):
        return [sanitize(v) for v in o]
    if isinstance(o, decimal.Decimal):
        return jnum(o)
    if isinstance(o, float):
        return None if (math.isnan(o) or math.isinf(o)) else (int(o) if o.is_integer() else o)
    return o


# --- sankey (verbatim from SGX REIT upsert.ipynb / prod_upsert_manual_input.py) ---
def make_sankey_component(inp):
    lb, org, db, red = "hsl(195, 53%, 79%)", "hsl(39, 100%, 50%)", "hsl(240, 100%, 50%)", "hsl(0, 100%, 50%)"
    links, nodes = [], []
    for rb in inp["revenue_breakdown"]:
        links.append({"source": rb["category"], "target": "Total Revenue", "value": rb["amount"]})
    if inp["gross_income"] >= 0:
        links.append({"source": "Total Revenue", "target": "Cost of Revenue", "value": inp["cost_of_revenue"]})
        links.append({"source": "Total Revenue", "target": "Gross Profit", "value": inp["gross_income"]})
        if inp["operating_income"] >= 0:
            links.append({"source": "Gross Profit", "target": "Operating Income", "value": inp["operating_income"]})
            links.append({"source": "Gross Profit", "target": "Operating Expense", "value": inp["operating_expense"]})
        else:
            links.append({"source": "Operating Income", "target": "Operating Expense", "value": -(inp["operating_income"])})
            links.append({"source": "Gross Profit", "target": "Operating Expense", "value": inp["gross_income"]})
    else:
        links.append({"source": "Total Revenue", "target": "Cost of Revenue", "value": inp["total_revenue"]})
        links.append({"source": "Gross Profit", "target": "Cost of Revenue", "value": -(inp["gross_income"])})
        links.append({"source": "Operating Income", "target": "Gross Profit", "value": -(inp["gross_income"])})
        links.append({"source": "Operating Income", "target": "Operating Expense", "value": inp["operating_expense"]})
    for oeb in inp["operating_expense_breakdown"]:
        links.append({"source": "Operating Expense", "target": oeb["category"], "value": oeb["amount"]})
    for rb in inp["revenue_breakdown"]:
        nodes.append({"id": rb["category"], "nodeColor": lb})
    nodes += [{"id": "Total Revenue", "nodeColor": lb}, {"id": "Cost of Revenue", "nodeColor": org},
              {"id": "Gross Profit", "nodeColor": db if inp["gross_income"] >= 0 else red},
              {"id": "Operating Income", "nodeColor": db if inp["operating_income"] >= 0 else red},
              {"id": "Operating Expense", "nodeColor": org}]
    for oeb in inp["operating_expense_breakdown"]:
        nodes.append({"id": oeb["category"], "nodeColor": org})
    return {"nodes": nodes, "links": links}


# --- industry_breakdown parts from *_final ---
def top_tenants(cur, sym, fy, limit=10):
    cur.execute("select rank,client_name,industry,revenue_pct from sgx_reit_top_tenant_final "
                "where symbol=%s and financial_year=%s", (sym, fy))
    rows = cur.fetchall()
    if not rows:
        return None
    rows.sort(key=lambda r: (r[3] is None, -(float(r[3]) if r[3] is not None else 0.0), r[0]))
    out = []
    for rank, name, ind, pct in rows[:limit]:
        e = {}
        if name is not None: e["client_name"] = name
        if ind is not None: e["industry"] = ind
        e["revenue_pct"] = round(float(pct) / 100, 2) if pct is not None else None
        out.append(e)
    return out


def trade_mix(cur, sym, fy):
    cur.execute("select category,pct from sgx_reit_trade_mix_final where symbol=%s and financial_year=%s", (sym, fy))
    rows = cur.fetchall()
    if not rows:
        return None
    agg = {}
    for cat, pct in rows:
        if cat is None or pct is None:
            continue
        agg[cat] = agg.get(cat, 0.0) + float(pct)
    if not agg or sum(agg.values()) > 130:  # ambiguous multi-segment (e.g. T82U office+retail) -> omit
        return None
    return {k: round(v / 100, 2) for k, v in sorted(agg.items(), key=lambda kv: -kv[1])}


def properties(cur, sym, fy, top_n=20):
    cur.execute("select property_name,country,category,ownership,market_valuation,gross_revenue,occupancy_rate "
                "from sgx_reit_property_final where symbol=%s and financial_year=%s", (sym, fy))
    rows = cur.fetchall()
    if not rows:
        return None, None
    conv = [(n, c, cat, own, mv, gr, occ) for n, c, cat, own, mv, gr, occ in rows]
    conv.sort(key=lambda r: (float(r[5]) if r[5] is not None else float("-inf")), reverse=True)
    top = []
    for name, country, cat, own, mv, gr, occ in conv[:top_n]:
        e = {}
        if country is not None: e["country"] = country
        if cat is not None: e["category"] = cat
        if name is not None: e["name"] = name
        if own is not None and float(own) != 100: e["ownership_pct"] = round(float(own) / 100, 2)
        if mv is not None: e["valuation"] = int(round(float(mv)))
        if gr is not None: e["gross_income"] = int(round(float(gr)))
        if occ is not None: e["occupancy_rate"] = round(float(occ) / 100, 2)
        top.append(e)
    counts = {}
    for name, country, cat, own, mv, gr, occ in conv:
        c = country or "Unknown"; k = cat or "Unknown"
        slot = counts.setdefault(c, {}).setdefault(k, [0, 0, 0])
        slot[0] += 1
        slot[1] += int(round(float(gr))) if gr is not None else 0
        slot[2] += int(round(float(mv))) if mv is not None else 0
    return top, counts


def distribution_metrics(perf):
    """Section 2 of the mapping doc. perf = dict of the performance_final distribution columns."""
    def n(x): return jnum(x) if x is not None else None
    adj_src = perf.get("adjusted_distributable_income")
    ndi = perf.get("net_distributable_income")
    adjusted = n(adj_src) if adj_src is not None else n(ndi)
    opening = n(perf.get("distributable_income_opening"))
    pool = n(perf.get("distribution_pool_other_movements")) or 0
    dist_inc = None
    if opening is not None and adjusted is not None:
        dist_inc = opening + adjusted + pool
    return {
        "distributable_income": dist_inc,
        "adjusted_distributable_income": adjusted,
        "distribution_paid": n(perf.get("distribution_cash_paid")),
        "end_of_year_distribution": n(perf.get("distributable_income_closing")),
        "end_of_year_shareholder_units": n(perf.get("number_of_shareholder_units")),
        "units_to_be_issued": n(perf.get("units_to_be_issued")),
    }


PERF_DIST_COLS = ["date", "source_url", "adjusted_distributable_income", "net_distributable_income",
                  "distributable_income_opening", "distribution_pool_other_movements",
                  "distribution_cash_paid", "distributable_income_closing",
                  "number_of_shareholder_units", "units_to_be_issued"]


def build(cur, symbols, fy):
    where, args = [], []
    if symbols:
        where.append("f.symbol = ANY(%s)"); args.append(symbols)
    if fy is not None:
        where.append("f.financial_year = %s"); args.append(fy)
    sql = ("select f.symbol, f.financial_year, f.income_stmt_metrics, f.balance_sheet_metrics, "
           "f.cash_flow_metrics, f.employee_breakdown, " + ", ".join("p." + c for c in PERF_DIST_COLS) +
           " from sgx_reit_financial_final f "
           "join sgx_reit_performance_final p on p.symbol=f.symbol and p.financial_year=f.financial_year")
    if where:
        sql += " where " + " and ".join(where)
    sql += " order by f.symbol, f.financial_year"
    cur.execute(sql, args)
    cols = [d[0] for d in cur.description]
    records = []
    for row in cur.fetchall():
        r = dict(zip(cols, row))
        ism = dict(r["income_stmt_metrics"] or {})
        ism.pop("depreciation", None)          # ours-only, not a manual_input key
        ism = {k: jnum(v) for k, v in ism.items()}
        perf = {c: r[c] for c in PERF_DIST_COLS}
        date = str(perf["date"])[:10]
        fy_declared = declared_fy(date)         # derive from date per the rule (== f.financial_year)
        top, counts = properties(cur, r["symbol"], r["financial_year"])
        ib = {}
        t = top_tenants(cur, r["symbol"], r["financial_year"])
        if t is not None: ib["top_10_gri%_customers"] = t
        tm = trade_mix(cur, r["symbol"], r["financial_year"])
        if tm is not None: ib["gross_rental_income_by_sectors"] = tm
        if top is not None: ib["property_portfolio_top_20"] = top
        if counts is not None: ib["property_counts_by_country"] = counts
        ib["distribution_metrics"] = distribution_metrics(perf)
        rec = {
            "symbol": r["symbol"],  # keep .SI internally; strip at write
            "financial_year": fy_declared,
            "date": date,
            "source_url": perf["source_url"],
            "income_stmt_metrics": ism,
            "balance_sheet_metrics": {k: jnum(v) for k, v in (r["balance_sheet_metrics"] or {}).items()},
            "cash_flow_metrics": {k: jnum(v) for k, v in (r["cash_flow_metrics"] or {}).items()},
            "employee_breakdown": r["employee_breakdown"],
            "sankey_component": make_sankey_component(ism),
            "industry_breakdown": ib,
        }
        records.append(sanitize(rec))
    return records


def prod_get(sym_bare, fy):
    URL = os.environ["SUPABASE_URL"].rstrip("/"); KEY = os.environ["SUPABASE_KEY"]
    q = (f"{URL}/rest/v1/sgx_manual_input?symbol=eq.{sym_bare}&financial_year=eq.{fy}"
         "&select=income_stmt_metrics,balance_sheet_metrics,cash_flow_metrics,industry_breakdown,source_url")
    req = urllib.request.Request(q, headers={"apikey": KEY, "Authorization": "Bearer " + KEY})
    rows = json.load(urllib.request.urlopen(req, timeout=60))
    return rows[0] if rows else None


def main():
    a = parse_args()
    symbols = None
    if a.symbols:
        symbols = [s if s.endswith(".SI") else s + ".SI" for s in a.symbols.split(",")]
    dev = psycopg2.connect(os.environ["SUPABASE_CONNECTION_STRING"]); cur = dev.cursor()
    records = build(cur, symbols, a.fy)
    print(f"built {len(records)} sgx_manual_input rows from *_final  (mode={'WRITE' if a.write else 'DRY'})")

    for rec in records[: (10**9 if (a.write or a.verify) else a.limit_preview)]:
        bare = rec["symbol"].removesuffix(".SI")
        ib_keys = ", ".join(rec["industry_breakdown"].keys())
        line = f"  {bare:8} FY{rec['financial_year']} date={rec['date']} ib=[{ib_keys}]"
        if a.verify:
            p = prod_get(bare, rec["financial_year"])
            if p is None:
                print(line + "  -> NOT IN PROD (new insert)")
            else:
                diffs = []
                if set(rec["income_stmt_metrics"]) != set(p.get("income_stmt_metrics") or {}):
                    o = set(rec["income_stmt_metrics"]); q = set(p.get("income_stmt_metrics") or {})
                    diffs.append(f"ism_keys(+{sorted(o-q)}/-{sorted(q-o)})")
                for m in ["total_revenue", "net_income", "ebit", "ebitda", "funds_from_operation"]:
                    ov = rec["income_stmt_metrics"].get(m); pv = (p.get("income_stmt_metrics") or {}).get(m)
                    if ov != pv: diffs.append(f"{m}:{pv}->{ov}")
                print(line + ("  IDENTICAL" if not diffs else "  DIFF: " + ", ".join(diffs)))
        else:
            print(line)

    if a.write:
        URL = os.environ["SUPABASE_URL"].rstrip("/"); KEY = os.environ["SUPABASE_KEY"]
        cols = ["symbol", "financial_year", "date", "source_url", "income_stmt_metrics",
                "balance_sheet_metrics", "cash_flow_metrics", "employee_breakdown",
                "sankey_component", "industry_breakdown"]
        payload = [{**{c: rec[c] for c in cols}, "symbol": rec["symbol"].removesuffix(".SI")} for rec in records]
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(URL + "/rest/v1/sgx_manual_input", data=body, method="POST",
              headers={"apikey": KEY, "Authorization": "Bearer " + KEY, "Content-Type": "application/json",
                       "Prefer": "resolution=merge-duplicates,return=minimal"})
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                print("PROD upsert status:", r.status, "rows:", len(payload))
        except urllib.error.HTTPError as e:
            print("HTTP", e.code, e.read().decode("utf-8", "replace")[:600])
    else:
        print("\n(DRY — nothing written. Add --write to upsert to prod; --verify to diff vs prod.)")
    cur.close(); dev.close()


if __name__ == "__main__":
    main()
