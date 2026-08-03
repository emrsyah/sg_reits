#!/usr/bin/env python3
"""Load extracted/<SYM>.SI_FY<YYYY>/ into Supabase Postgres (the sgx_reit_* tables).

Idempotent: singletons upsert on their unique key; list-tables delete-then-insert per
(symbol, financial_year). Also upserts a reit_report row (with pdf_r2_key) per report.

Usage:
  python scripts/db/load_supabase.py                 # all extracted/ dirs
  python scripts/db/load_supabase.py OXMU.SI_FY2025  # one or more dirs
"""
import os, re, json, glob, pathlib, sys
import psycopg2
from psycopg2.extras import execute_values, Json
from dotenv import load_dotenv

ROOT = pathlib.Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")
DSN = os.environ["SUPABASE_CONNECTION_STRING"]

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
def d(v):  # date sanitizer: keep only valid YYYY-MM-DD, else None
    return v if isinstance(v, str) and DATE_RE.match(v) else None
def _first_date(r, *aliases):  # first alias that yields a VALID YYYY-MM-DD (Wave 9: a malformed
    return next((d(r.get(k)) for k in aliases if d(r.get(k))), None)  # early alias no longer shadows a valid later one)
def J(v):  # jsonb wrapper (None stays NULL)
    return Json(v) if v is not None else None

# --- property-transaction alias resolution (table formalized 2026-06-23; mirrors
#     schema/models.py PropertyTransaction). raw keeps the ORIGINAL object; the typed
#     columns are resolved here from the 50+ legacy ad-hoc key names. ---
def _first(r, *aliases):
    for k in aliases:
        v = r.get(k)
        if v not in (None, "", [], {}):
            return v
    return None

# Wave 9 (2026-07-03): currency-code normalization for the FX-join key. RMB is the informal
# name for renminbi; ISO 4217 is CNY. Values are unchanged — only the code label is normalized
# so the downstream date-keyed FX list (ISO-keyed) joins cleanly. The JSON stays as-reported.
CCY_NORM = {"RMB": "CNY"}
def _ccy(v):
    return CCY_NORM.get(v, v) if isinstance(v, str) else v

def _num(v):
    if isinstance(v, (int, float)):
        return v
    if isinstance(v, str):
        s = v.replace(",", "").replace("$", "").strip()
        try:
            return float(s)
        except ValueError:
            return None
    return None

def _pct(v):
    """Parse a percent value -> float in percentage points (e.g. '20.2%' -> 20.2)."""
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        return _num(v.replace("%", ""))
    return None

def _derive_status(ttype_l, explicit):
    """Lifecycle status (completed | announced | terminated) from the deal type / explicit status."""
    if "terminated" in ttype_l:
        return "terminated"
    if "announced" in ttype_l:
        return "announced"
    if isinstance(explicit, str):
        e = explicit.strip().lower()
        if e in ("announced", "pending", "pending_completion", "subsequent_event"):
            return "announced"
        if e == "terminated":
            return "terminated"
        if e in ("completed", "divested", "done"):
            return "completed"
    return "completed"

def txn_row(symbol, fy, r):
    ttype = _first(r, "transaction_type", "type")
    if isinstance(ttype, str):
        ttype = ttype.strip().lower()
    ttype_l = ttype or ""
    # match divestment variants (announced_divestment / partial_divestment / ...), but a
    # *terminated* deal never completed -> no proceeds resolved for it.
    terminated = "terminated" in ttype_l
    acq = ttype_l == "acquisition"
    div = ("divestment" in ttype_l) and not terminated

    # --- money: Phase-1 un-conflation (2026-07-01) ---
    # gross sale price and net-of-cost proceeds are DISTINCT columns (10 divestments disclose both).
    purchase = _num(_first(r, "purchase_price", "acquisition_price", "purchase_consideration",
                           "transaction_price")) if acq else None
    gross = _num(_first(r, "gross_sale_price", "sale_price", "sale_consideration", "divestment_price")) if div else None
    net = _num(_first(r, "net_proceeds", "net_consideration_usd")) if div else None
    amb = _num(_first(r, "consideration", "consideration_sgd", "price", "amount"))  # type-ambiguous
    if amb is not None:
        if acq and purchase is None:   purchase = amb
        elif div and gross is None:    gross = amb   # bare consideration/price = gross sale price
    # Presentation currency of the transaction figures. Phase-3 Tier-0 fix: when no explicit
    # row `currency`, derive it from any stated per-figure transaction currency (all SGD for M44U)
    # rather than from `local_currency`/`currency_local`, which is the ASSET's local ccy (RMB/JPY/MYR)
    # belonging to the *_local amounts — not the currency the deal figures are booked in.
    row_ccy = _first(r, "currency", "sale_price_currency", "gross_sale_price_currency",
                     "net_proceeds_currency", "purchase_price_currency", "valuation_currency",
                     "carrying_value_currency", "currency_local")

    def ccy(*aliases):  # per-figure currency, falling back to the row presentation currency
        return _first(r, *aliases) or row_ccy

    # bind money locals so each per-figure currency tag keys off the RESOLVED value.
    # Wave 9 fix: the old guards re-resolved with a NARROWER alias set than the value above, so a
    # gain from gain_loss/gain_on_disposal or a valuation from gross_valuation_usd loaded with a
    # value but NO currency tag. Now the tag is applied whenever the value itself resolved.
    carrying = _num(_first(r, "carrying_value", "carrying_value_pre"))
    gain = _num(_first(r, "gain_on_divestment", "gain", "gain_on_disposal", "gain_loss",
                       "divestment_gain", "net_gain"))
    valuation = _num(_first(r, "valuation", "appraised_value", "agreed_value",
                            "valuation_at_acquisition", "gross_valuation_usd"))

    return (
        symbol, fy, ttype, _derive_status(ttype_l, _first(r, "status")),
        r.get("property_name"),
        _first_date(r, "transaction_date", "date", "completion_date", "completed_date",
                    "agreement_date", "announced_date", "announcement_date"),
        _first(r, "description", "notes", "note", "detail"),
        purchase, gross, net, carrying, gain, valuation,
        _pct(_first(r, "interest_pct", "interest_acquired_pct", "interest_acquired", "interest_divested")),
        # per-figure currency (Wave 9: RMB->CNY normalized; tag applied whenever the value resolved)
        _ccy(ccy("purchase_price_currency", "consideration_currency") if purchase is not None else _first(r, "purchase_price_currency")),
        _ccy(ccy("gross_sale_price_currency", "sale_price_currency", "consideration_currency") if gross is not None else _first(r, "gross_sale_price_currency", "sale_price_currency")),
        _ccy(ccy("net_proceeds_currency") if net is not None else _first(r, "net_proceeds_currency")),
        _ccy(ccy("carrying_value_currency") if carrying is not None else _first(r, "carrying_value_currency")),
        _ccy(ccy("gain_currency", "gain_on_divestment_currency") if gain is not None else _first(r, "gain_currency", "gain_on_divestment_currency")),
        _ccy(ccy("valuation_currency") if valuation is not None else _first(r, "valuation_currency")),
        # per-figure provenance text
        _first(r, "carrying_value_basis"),
        _first(r, "gain_on_divestment_basis"),
        _first(r, "net_proceeds_basis"),
        _first(r, "counterparty", "buyer", "purchaser", "seller", "vendor"),
        _ccy(row_ccy),
        r.get("source_page"), J(r),
        _first(r, "deal_id"),
        _first_date(r, "announced_date", "announcement_date", "agreement_date"),
        _first_date(r, "completed_date", "completion_date"),
        _pct(_first(r, "gain_loss_pct", "gain_pct", "premium_pct")),
        _first(r, "gain_basis"),
        _first_date(r, "valuation_date"),
        _first(r, "source_type") or "annual_report",
        J(r.get("announcement_refs")) if r.get("announcement_refs") else None,
    )

def load_json(dirpath, name):
    p = pathlib.Path(dirpath) / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None

def pdf_key_for(symbol, fy):
    sym = symbol.split(".")[0]
    hits = glob.glob(str(ROOT / "annual_reports" / f"*_{sym}.SI_*_FY{fy}.pdf"))
    return os.path.basename(hits[0]) if hits else None

def declared_fy(date_str):
    """Declared fiscal year from statement date: Jan-Jun end -> year-1, else year.
    (Mapletree-style: a Mar/Jun-2025 year-end is FY2024.)"""
    y, mth = int(date_str[:4]), int(date_str[5:7])
    return y - 1 if mth <= 6 else y

def load_one(cur, dirpath):
    name = os.path.basename(dirpath.rstrip("/\\"))
    m = re.match(r"^([A-Z0-9]+\.SI)_FY(\d{4})$", name)
    if not m:
        print(f"  SKIP (bad dir name): {name}"); return
    symbol, folder_fy = m.group(1), int(m.group(2))
    # financial_year is authoritative from the report DATE, not the folder label.
    # Guard against a mislabeled folder silently re-introducing the date.year bug.
    _pf = load_json(dirpath, "performance.json")
    _pf = _pf[0] if isinstance(_pf, list) else _pf
    _date = (_pf or {}).get("date")
    if _date:
        fy = declared_fy(_date)
        if fy != folder_fy:
            print(f"  REFUSE {name}: folder says FY{folder_fy} but date {_date} "
                  f"=> declared FY{fy}. Rename the folder to {symbol}_FY{fy}."); return
    else:
        fy = folder_fy
        print(f"  WARN {name}: no performance.json date; trusting folder FY{folder_fy}.")

    # ---- reit_report (inventory) ----
    cur.execute("""insert into reit_report (symbol, financial_year, pdf_r2_key)
                   values (%s,%s,%s)
                   on conflict (symbol, financial_year)
                   do update set pdf_r2_key = excluded.pdf_r2_key""",
                (symbol, fy, pdf_key_for(symbol, fy)))

    # ---- profile (singleton on symbol) ----
    pr = load_json(dirpath, "profile.json")
    if pr:
        cur.execute("""insert into sgx_reit_profile (symbol, sub_sector, management, income_model, source_page)
                       values (%s,%s,%s,%s,%s)
                       on conflict (symbol) do update set
                         sub_sector=excluded.sub_sector, management=excluded.management,
                         income_model=excluded.income_model, source_page=excluded.source_page""",
                    (symbol, pr.get("sub_sector"), J(pr.get("management") or []),
                     pr.get("income_model"), pr.get("source_page")))

    # ---- performance (singleton on symbol,fy) ----
    pf = load_json(dirpath, "performance.json")
    pf = pf[0] if isinstance(pf, list) else pf
    if pf:
        cols = ["portfolio_value","properties_location","gross_revenue","net_property_income",
                "net_distributable_income","distributable_income_opening","distribution_cash_paid",
                "distributable_income_closing","adjusted_distributable_income","distribution_paid","distribution_basis","dpu",
                "number_of_unitholders","number_of_shareholder_units","aggregate_leverage",
                "interest_coverage_ratio","cost_of_debt","weighted_avg_debt_maturity","nav_per_unit",
                "wale","portfolio_occupancy","dpu_period_months","currency","source_page"]
        cur.execute(f"""insert into sgx_reit_performance
            (symbol, financial_year, {','.join(cols)}, distribution_record, date, flags)
            values ({','.join(['%s']*(2+len(cols)+3))})
            on conflict (symbol, financial_year) do update set
            {', '.join(f'{c}=excluded.{c}' for c in cols)},
            distribution_record=excluded.distribution_record, date=excluded.date, flags=excluded.flags""",
            (symbol, fy, *[pf.get(c) for c in cols],
             J(pf.get("distribution_record")), d(pf.get("date")), J(pf.get("flags") or [])))

    # ---- financial (singleton on symbol,fy) ----
    fin = load_json(dirpath, "financial.json")
    fin = fin[0] if isinstance(fin, list) else fin
    if fin:
        cur.execute("""insert into sgx_reit_financial
            (symbol, financial_year, currency, income_stmt_metrics, balance_sheet_metrics,
             cash_flow_metrics, employee_breakdown, line_items, source_page)
            values (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            on conflict (symbol, financial_year) do update set
              currency=excluded.currency, income_stmt_metrics=excluded.income_stmt_metrics,
              balance_sheet_metrics=excluded.balance_sheet_metrics, cash_flow_metrics=excluded.cash_flow_metrics,
              employee_breakdown=excluded.employee_breakdown, line_items=excluded.line_items,
              source_page=excluded.source_page""",
            (symbol, fy, fin.get("currency"), J(fin.get("income_stmt_metrics")),
             J(fin.get("balance_sheet_metrics")), J(fin.get("cash_flow_metrics")),
             J(fin.get("employee_breakdown")), J(fin.get("line_items") or []), fin.get("source_page")))

    # ---- notes (singleton on symbol,fy) ----
    nt = load_json(dirpath, "_notes.json")
    if nt is not None:
        cur.execute("""insert into sgx_reit_notes (symbol, financial_year, notes)
                       values (%s,%s,%s)
                       on conflict (symbol, financial_year) do update set notes=excluded.notes""",
                    (symbol, fy, J(nt)))

    # ---- list tables: delete-then-insert per (symbol,fy) ----
    def reload_list(table, fname, builder, cols):
        rows = load_json(dirpath, fname) or []
        cur.execute(f"delete from {table} where symbol=%s and financial_year=%s", (symbol, fy))
        vals = [builder(r) for r in rows]
        if vals:
            execute_values(cur, f"insert into {table} ({','.join(cols)}) values %s", vals)
        return len(vals)

    n_prop = reload_list("sgx_reit_property", "properties.json",
        lambda r: (symbol, fy, r.get("property_name"), r.get("country"), r.get("category"),
            r.get("category_raw"), r.get("address"), r.get("ownership"), r.get("market_valuation"),
            r.get("purchase_price"),
            (_ccy(r.get("purchase_price_currency") or r.get("currency"))
             if r.get("purchase_price") is not None else None),  # untagged cost = presentation ccy
            # Wave 9: as-reported LOCAL acquisition cost pair (e.g. CY6U INR) when the report prints it
            r.get("purchase_price_local"),
            (_ccy(r.get("purchase_price_local_currency")) if r.get("purchase_price_local") is not None else None),
            d(r.get("valuation_date")), _ccy(r.get("currency")),
            # local/original-currency valuation: A17U uses local_currency/local_currency_value (was not loading)
            _ccy(r.get("original_currency") or r.get("local_currency")),
            (r.get("original_value") if r.get("original_value") is not None else r.get("local_currency_value")),
            # market_valuation is ALWAYS in the row's presentation currency (`currency`); the
            # local/foreign amount is carried separately in original_value/original_currency.
            # (2026-07-08: was mislabeling as original_currency — 0/184 rows had mv==original_value.)
            (_ccy(r.get("currency")) if r.get("market_valuation") is not None else None),
            r.get("net_property_income"),
            # per-figure currency (Phase-3 Tier-0): DHLU etc. report NPI/GR in the asset's local ccy
            # while the row `currency` is the presentation ccy of market_valuation.
            (_ccy(r.get("net_property_income_currency") or r.get("currency"))
             if r.get("net_property_income") is not None else None),
            r.get("gross_revenue"),
            (_ccy(r.get("gross_revenue_currency") or r.get("currency"))
             if r.get("gross_revenue") is not None else None),
            r.get("npi_pct"), r.get("occupancy_rate"),
            # gla column dropped 2026-08-03 (schema review). Extraction JSON may still carry a
            # gla key, so fold it into nla rather than discarding it; nla wins if both are present.
            J(r.get("major_tenants") or []), (r.get("nla") if r.get("nla") is not None else r.get("gla")),
            r.get("gfa"), r.get("area_unit"),
            r.get("land_tenure"), r.get("effective_date"), r.get("lease_term_years"),
            r.get("lease_expiry_date"), r.get("tenure_raw"), r.get("lease_terms_flags"), r.get("status") or "active",
            J(r.get("flags") or []), r.get("source_page"),
            (r.get("purchase_date") or r.get("acquisition_date"))),
        ["symbol","financial_year","property_name","country","category","category_raw","address",
         "ownership","market_valuation","purchase_price","purchase_price_currency",
         "purchase_price_local","purchase_price_local_currency",
         "valuation_date","currency","original_currency","original_value","market_valuation_currency",
         "net_property_income","net_property_income_currency","gross_revenue","gross_revenue_currency","npi_pct","occupancy_rate","major_tenants",
         "nla","gfa","area_unit","land_tenure","effective_date","lease_term_years",
         "lease_expiry_date","tenure_raw","lease_terms_flags","status","flags","source_page","purchase_date"])

    n_tt = reload_list("sgx_reit_top_tenant", "top_tenants.json",
        lambda r: (symbol, fy, r.get("rank"), r.get("client_name"), r.get("industry"),
            r.get("revenue_pct"), r.get("pct_basis"), r.get("source_page")),
        ["symbol","financial_year","rank","client_name","industry","revenue_pct","pct_basis","source_page"])

    n_tm = reload_list("sgx_reit_trade_mix", "trade_mix.json",
        lambda r: (symbol, fy, r.get("category"), r.get("category_raw"), r.get("pct"),
            r.get("pct_basis"), r.get("source_page")),
        ["symbol","financial_year","category","category_raw","pct","pct_basis","source_page"])

    n_txn = reload_list("sgx_reit_property_transaction", "property_transactions.json",
        lambda r: txn_row(symbol, fy, r),
        ["symbol","financial_year","transaction_type","status","property_name","transaction_date",
         "description","purchase_price","sale_price","net_sale_proceeds","carrying_value",
         "gain_on_divestment","valuation","interest_pct",
         "purchase_price_currency","sale_price_currency","net_sale_proceeds_currency",
         "carrying_value_currency","gain_currency","valuation_currency",
         "carrying_value_basis","gain_on_divestment_basis","net_proceeds_basis",
         "counterparty","currency","source_page","raw",
         "deal_id","announced_date","completed_date","gain_loss_pct","gain_basis",
         "valuation_date","source_type","announcement_refs"])

    print(f"  {symbol} FY{fy}: properties={n_prop} top_tenants={n_tt} trade_mix={n_tm} txn={n_txn}")

def main():
    args = sys.argv[1:]
    dirs = ([str(ROOT / "extracted" / a) for a in args] if args
            else sorted(glob.glob(str(ROOT / "extracted" / "*.SI_FY*"))))
    conn = psycopg2.connect(DSN); conn.autocommit = False
    try:
        with conn.cursor() as cur:
            for dp in dirs:
                load_one(cur, dp)
        conn.commit()
        print(f"committed {len(dirs)} report(s).")
    except Exception:
        conn.rollback(); raise
    finally:
        conn.close()

if __name__ == "__main__":
    main()
