"""Promote dev sgx_reit_*_final  ->  prod sgx_reit_* (PostgREST).

Encodes the transforms established by scripts/db/_compare_final_vs_prod.py +
_compare_values.py (dev *_final vs prod, verified same-report on M44U FY2024):

  symbol            .SI stripped -> bare ticker            (all tables)
  percent -> fraction (value / 100), fields:
      property.occupancy_rate, property.ownership,
      top_tenant.revenue_pct, trade_mix.pct,
      property_transaction.interest_pct
  properties_location  "A, B, C" / "A; B; C" (text) -> "[A, B, C]" (bracketed text,
                       prod's stored format; separators normalized to ", ")   (performance)
  date columns      coerced to 'YYYY-MM-DD' or NULL per prod column type
  text-typed numerics (e.g. property_transaction.purchase_price) -> string
  dev-only columns  (deal_id, source_type, announcement_refs) -> DROPPED
                    (prod schema is the target; we only send prod's columns)

NOT transformed (kept as-is, verified): all money & areas (absolute), non-pct KPIs
(aggregate_leverage, cost_of_debt, portfolio_occupancy, ICR, WALE, NAV, DPU, ...),
and property_transaction.gain_loss_pct (prod stores it as a plain percent, NOT a
fraction).

sgx_reit_financial_final has NO prod counterpart (financials live in
sgx_manual_input) -> it is not promoted here.

Write model (prod is REST-only, non-transactional):
  - profile:      scope = symbol           -> DELETE then POST (re-insert)
  - all others:   scope = (symbol, fy)     -> DELETE then POST (re-insert)
  This mirrors dev's delete-then-insert-per-scope semantics. NOTE: DELETE and POST
  are separate REST calls; a failure between them leaves that scope empty until re-run.

Usage:
  python scripts/db/promote_final_to_prod.py                          # DRY, all rows
  python scripts/db/promote_final_to_prod.py --symbols M44U,ME8U,N2IU --fy 2025
  python scripts/db/promote_final_to_prod.py --symbols M44U,ME8U,N2IU --fy 2025 --write
  python scripts/db/promote_final_to_prod.py --tables sgx_reit_property --fy 2025 --write

Read dev = direct Postgres; write prod = REST GET/DELETE/POST (service key).
DRY by default; nothing hits prod without --write.
"""
import os, sys, re, json, argparse, datetime, decimal, urllib.request, urllib.error
import psycopg2
from dotenv import load_dotenv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from normalize_locations import normalize_locations

# ---------- config ----------
PAIRS = [  # (dev_final, prod, scope_cols)
    ("sgx_reit_profile_final",              "sgx_reit_profile",              ["symbol"]),
    ("sgx_reit_performance_final",          "sgx_reit_performance",          ["symbol", "financial_year"]),
    ("sgx_reit_property_final",             "sgx_reit_property",             ["symbol", "financial_year"]),
    ("sgx_reit_top_tenant_final",           "sgx_reit_top_tenant",           ["symbol", "financial_year"]),
    ("sgx_reit_trade_mix_final",            "sgx_reit_trade_mix",            ["symbol", "financial_year"]),
    ("sgx_reit_property_transaction_final", "sgx_reit_property_transaction", ["symbol", "financial_year"]),
]
# percent (dev) -> fraction (prod): divide by 100. (gain_loss_pct is intentionally NOT here.)
FRACTION_FIELDS = {"occupancy_rate", "ownership", "revenue_pct", "pct", "interest_pct"}
# text "A, B, C" / "A; B; C" -> prod's bracketed text "[A, B, C]" (NOT a real array)
BRACKET_TEXT_FIELDS = {"properties_location"}


def parse_args():
    ap = argparse.ArgumentParser(description="Promote dev sgx_reit_*_final -> prod sgx_reit_*.")
    ap.add_argument("--symbols", help="comma list of .SI or bare tickers (default: all)")
    ap.add_argument("--fy", type=int, help="single financial_year to promote (default: all)")
    ap.add_argument("--tables", help="comma list of prod table names to limit to (default: all)")
    ap.add_argument("--write", action="store_true", help="apply to prod (default: dry run)")
    ap.add_argument("--limit-preview", type=int, default=1, help="sample rows to print in dry run")
    return ap.parse_args()


# ---------- json coercion ----------
def jsonable(v):
    if isinstance(v, decimal.Decimal):
        f = float(v)
        return int(f) if f.is_integer() else f
    if isinstance(v, (datetime.date, datetime.datetime)):
        return v.isoformat()[:10]
    return v


_DATE_RX = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_DATE_FMTS = ("%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y", "%d-%m-%Y", "%d %b %Y", "%d %B %Y")
_DATE_DROPS = []  # (col, raw) for dev values that are NOT valid dates -> nulled (can't cast to prod date)

def to_date_str(v):
    """Return a strict 'YYYY-MM-DD' or None. Non-date text (bare years, prose) -> None,
    because prod's column is typed `date` and Postgres rejects a non-date string."""
    if v is None:
        return None
    if isinstance(v, (datetime.date, datetime.datetime)):
        return v.isoformat()[:10]
    s = str(v).strip()
    if not s:
        return None
    head = s[:10]
    if _DATE_RX.match(head):
        try:
            datetime.date.fromisoformat(head); return head
        except ValueError:
            pass
    for fmt in _DATE_FMTS:
        try:
            return datetime.datetime.strptime(s, fmt).date().isoformat()
        except ValueError:
            continue
    return None


def coerce(col, ptype, v):
    """Transform one dev value to its prod representation."""
    if v is None:
        return None
    if col == "symbol":
        return str(v).removesuffix(".SI")
    if col in FRACTION_FIELDS:
        return round(float(v) / 100.0, 8)
    if col in BRACKET_TEXT_FIELDS:
        # canonical country normalization: strip cities/parentheticals, unify variants,
        # dedupe, "[A, B, C]" (see normalize_locations.py)
        return normalize_locations(v)
    if ptype == "date":
        ds = to_date_str(v)
        if ds is None and v is not None:
            _DATE_DROPS.append((col, str(v)))
        return ds
    if ptype in ("text", "character varying", "character"):
        # text-typed numerics (e.g. purchase_price) must serialize as string
        return jsonable(v) if isinstance(v, (dict, list)) else str(jsonable(v))
    if ptype in ("numeric", "real", "double precision", "number"):
        return float(v)
    if ptype in ("integer", "bigint", "smallint"):
        return int(v)
    if ptype == "boolean":
        return bool(v)
    # jsonb / json / array -> pass through (already json-serializable dict/list)
    return jsonable(v)


# ---------- prod REST ----------
class Prod:
    def __init__(self):
        self.url = os.environ["SUPABASE_URL"].rstrip("/")
        self.key = os.environ["SUPABASE_KEY"]
        self.h = {"apikey": self.key, "Authorization": "Bearer " + self.key}

    def defs(self):
        req = urllib.request.Request(self.url + "/rest/v1/", headers=self.h)
        return json.load(urllib.request.urlopen(req)).get("definitions", {})

    def col_types(self, table, defs):
        props = defs.get(table, {}).get("properties", {})
        return {c: (m.get("format") or m.get("type")) for c, m in props.items()}

    def _scope_query(self, scope):
        parts = []
        for k, val in scope.items():
            parts.append(f"{k}=eq.{val}")
        return "&".join(parts)

    def count(self, table, scope):
        q = self._scope_query(scope)
        req = urllib.request.Request(f"{self.url}/rest/v1/{table}?{q}&select=count", headers=self.h)
        try:
            return json.load(urllib.request.urlopen(req))[0]["count"]
        except Exception:
            return None

    def delete(self, table, scope):
        q = self._scope_query(scope)
        req = urllib.request.Request(f"{self.url}/rest/v1/{table}?{q}", method="DELETE",
                                     headers={**self.h, "Prefer": "return=minimal"})
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.status

    def insert(self, table, rows):
        body = json.dumps(rows).encode("utf-8")
        req = urllib.request.Request(f"{self.url}/rest/v1/{table}", data=body, method="POST",
                                     headers={**self.h, "Content-Type": "application/json",
                                              "Prefer": "return=minimal"})
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.status


# ---------- dev read + transform ----------
def dev_read(cur, final_table, symbols_si, fy):
    where, args = [], []
    if symbols_si:
        where.append("symbol = ANY(%s)"); args.append(symbols_si)
    if fy is not None:
        # profile has no financial_year column
        cur.execute("select 1 from information_schema.columns where table_name=%s and column_name='financial_year'",
                    (final_table,))
        if cur.fetchone():
            where.append("financial_year = %s"); args.append(fy)
    sql = f"select * from {final_table}"
    if where:
        sql += " where " + " and ".join(where)
    cur.execute(sql, args)
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def transform_row(row, prod_types):
    out = {}
    for col, ptype in prod_types.items():
        out[col] = coerce(col, ptype, row.get(col))
    return out


def scope_of(prod_row, scope_cols):
    return {k: prod_row[k] for k in scope_cols}


def aggregate_trade_mix(rows):
    """Prod sgx_reit_trade_mix PK = (symbol, financial_year, category, pct_basis).
    Dev *_final can hold several rows collapsing to the same canonical category
    (distinct category_raw). Sum their pct into one row to satisfy the PK
    (matches the original prod promotion, which stores aggregated categories)."""
    agg = {}
    for r in rows:
        k = (r.get("symbol"), r.get("financial_year"), r.get("category"), r.get("pct_basis"))
        if k in agg:
            if r.get("pct") is not None:
                agg[k]["pct"] = round((agg[k].get("pct") or 0) + r["pct"], 8)
        else:
            agg[k] = dict(r)
    return list(agg.values())


def main():
    args = parse_args()
    load_dotenv(".env")
    symbols_si = None
    if args.symbols:
        symbols_si = [s if s.endswith(".SI") else s + ".SI" for s in args.symbols.split(",")]
    only_tables = set(args.tables.split(",")) if args.tables else None

    dev = psycopg2.connect(os.environ["SUPABASE_CONNECTION_STRING"]); cur = dev.cursor()
    prod = Prod(); defs = prod.defs()

    print("=" * 88)
    print(f"PROMOTE dev *_final -> prod   mode={'WRITE' if args.write else 'DRY RUN'}"
          f"  symbols={args.symbols or 'ALL'}  fy={args.fy or 'ALL'}")
    print("=" * 88)

    for final_table, prod_table, scope_cols in PAIRS:
        if only_tables and prod_table not in only_tables:
            continue
        prod_types = prod.col_types(prod_table, defs)
        rows = dev_read(cur, final_table, symbols_si, args.fy)
        _dstart = len(_DATE_DROPS)
        prod_rows = [transform_row(r, prod_types) for r in rows]
        if prod_table == "sgx_reit_trade_mix":
            prod_rows = aggregate_trade_mix(prod_rows)

        # group by scope for delete-then-insert
        scopes = {}
        for pr in prod_rows:
            key = tuple(scope_of(pr, scope_cols).items())
            scopes.setdefault(key, []).append(pr)

        print(f"\n### {final_table} -> {prod_table}")
        print(f"    dev rows selected: {len(rows)}   scopes: {len(scopes)}   "
              f"(prod cols sent: {len(prod_types)})")
        dropped = [c for c in (rows[0].keys() if rows else []) if c not in prod_types]
        if dropped:
            print(f"    dev-only cols DROPPED: {sorted(dropped)}")
        nulled = _DATE_DROPS[_dstart:]
        if nulled:
            from collections import Counter as _C
            byc = _C(c for c, _ in nulled)
            ex = "; ".join(f"{c}: e.g. {raw!r}" for c, raw in nulled[:3])
            print(f"    WARN non-date text NULLED for prod `date` cols {dict(byc)} -> {ex}")

        for key, group in list(scopes.items())[: (10**9 if args.write else 50)]:
            scope = dict(key)
            existing = prod.count(prod_table, scope)
            print(f"    scope {scope}: dev->{len(group)} rows | prod currently={existing}")

        if args.limit_preview and prod_rows and not args.write:
            print("    sample transformed row:")
            print("      " + json.dumps(prod_rows[0], ensure_ascii=False)[:600])

        if args.write:
            for key, group in scopes.items():
                scope = dict(key)
                try:
                    dstat = prod.delete(prod_table, scope)
                    istat = prod.insert(prod_table, group)
                    print(f"    WROTE scope {scope}: delete={dstat} insert={istat} rows={len(group)}")
                except urllib.error.HTTPError as e:
                    print(f"    ERROR scope {scope}: HTTP {e.code} {e.read().decode('utf-8','replace')[:300]}")

    if not args.write:
        print("\n(DRY RUN — nothing written to prod. Re-run with --write to apply.)")
    dev.close()


if __name__ == "__main__":
    main()
