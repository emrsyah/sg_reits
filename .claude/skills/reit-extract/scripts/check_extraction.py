"""check_extraction.py — QC gate for one extracted trust-year directory.

Usage: python check_extraction.py extracted/<SYMBOL>_FY<YYYY>

Checks (exit code 1 if any FAIL):
  1. all 8 files exist and parse as JSON
  2. provenance: every record has a usable source_page
  3. basis discipline: every pct-bearing record carries pct_basis
  4. units sanity: trust-level money fields look absolute (not $'000 / millions)
  5. fill rates per property column (vs expected structural bands)
  6. reconciliation: sum(property gross_revenue/npi) vs reported totals
     (consolidated properties only when value_basis/ownership hints allow;
     rows in a different currency than performance are excluded — cross-currency
     portfolios fall back to the _notes reconciliation)
  7. enum discipline: land_tenure / value_basis / transaction_type / statement /
     income_model hold only their enum values (verbatim wording belongs in *_raw)
  8. self-consistency: tenure_raw that mentions an expiry while lease_expiry_date
     is null => FAIL (the agent's own verbatim proves the date was disclosed)
Warnings don't fail the run; FAILs do.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "schema"))
try:
    import models  # schema/models.py — canonical enums
    TRADE_CATEGORIES = set(models.TRADE_CATEGORIES)
    PROPERTY_CATEGORIES = set(models.PROPERTY_CATEGORIES)
except ImportError:
    TRADE_CATEGORIES = PROPERTY_CATEGORIES = None  # enum checks skipped if unavailable

# financial.json is a single object (1:1 income_stmt_metrics) since Jun17; pre-Jun17
# outputs used income_components.json (a list of note-lines) — both are tolerated here.
FILES = ["profile", "performance", "properties", "property_transactions",
         "top_tenants", "trade_mix", "financial", "_notes"]
PCT_TABLES = {"top_tenants": "pct_basis", "trade_mix": "pct_basis"}
MONEY_MIN = 1_000_000          # trust-level GR/NPI below this => probably $'000 left unscaled

ENUMS = {  # (file, column): allowed values; None always allowed
    ("properties", "land_tenure"): {"freehold", "leasehold"},
    ("properties", "value_basis"): {"consolidated", "joint_venture_100pct",
                                    "effective_interest"},
    ("property_transactions", "transaction_type"): {"acquisition", "divestment"},
    ("profile", "income_model"): {"conventional", "master_lease", "mcmgi",
                                  "management_contract", "entrusted_management",
                                  "fri", "mixed"},
}
KNOWN_PCT_BASIS = {"gri", "gri_excl_gto", "gross_revenue", "rental_income",
                   "headline_rent", "cash_rental_income", "committed_gross_rent",
                   "nla", "outlet_sales", "npi"}
EXPIRY_RX = re.compile(r"expir\w*\b.*\b(19|20|21)\d{2}", re.IGNORECASE | re.DOTALL)

fails, warns, infos = [], [], []


def load(base: Path, name: str):
    p = base / f"{name}.json"
    if not p.exists():
        fails.append(f"missing file: {p.name}")
        return None
    try:
        v = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        fails.append(f"bad JSON in {p.name}: {e}")
        return None
    return v if isinstance(v, list) else [v]


def has_page(rec: dict) -> bool:
    sp = rec.get("source_page")
    if isinstance(sp, int):
        return True
    if isinstance(sp, dict) and sp:
        return True
    return bool(rec.get("p_estimated"))


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    base = Path(sys.argv[1])
    # legacy compat: if a pre-Jun17 dir has income_components.json but no financial.json,
    # fold those note-lines into a synthetic financial object so the checks still run.
    legacy_fin = None
    if not (base / "financial.json").exists() and (base / "income_components.json").exists():
        try:
            legacy_fin = json.loads((base / "income_components.json").read_text("utf-8"))
            warns.append("using legacy income_components.json (no financial.json) — "
                         "re-extract to the 1:1 income_stmt_metrics shape")
        except json.JSONDecodeError:
            legacy_fin = None
    data = {name: load(base, name) for name in FILES if name != "financial"}
    if legacy_fin is not None:
        data["financial"] = [{"line_items": legacy_fin}]
    else:
        data["financial"] = load(base, "financial")
    if any(v is None for v in data.values()):
        report()

    # the agent's own structural-null declarations suppress predictable warns:
    # a warn the gate can predict from _notes is an INFO, not a warn
    notes = data["_notes"][0] if data["_notes"] else {}
    declared_cols = " ".join(
        str(c.get("column", "") if isinstance(c, dict) else c).lower()
        for c in (notes.get("columns_never_fillable") or []))

    def declared(*cols) -> bool:
        return any(c in declared_cols for c in cols)

    # 2. provenance
    for name in FILES:
        if name in ("_notes", "profile", "financial"):
            continue
        missing = sum(1 for r in data[name] if isinstance(r, dict) and not has_page(r))
        if missing:
            fails.append(f"{name}: {missing} record(s) without source_page")
    # financial: the object itself carries source_page, but each line_item should too
    fin0 = data["financial"][0] if data["financial"] else {}
    li_missing = sum(1 for r in (fin0.get("line_items") or [])
                     if isinstance(r, dict) and not has_page(r))
    if li_missing:
        fails.append(f"financial.line_items: {li_missing} line(s) without source_page")

    # 3. basis on percentages
    for name, col in PCT_TABLES.items():
        for r in data[name]:
            if r.get("pct") is not None or r.get("revenue_pct") is not None:
                if not r.get(col):
                    fails.append(f"{name}: record missing {col} "
                                 f"({r.get('client_name') or r.get('category')})")
        unknown = {str(r.get(col)).strip() for r in data[name]
                   if r.get(col) and str(r.get(col)).strip().lower()
                   not in KNOWN_PCT_BASIS}
        for b in sorted(unknown):
            n = sum(1 for r in data[name] if str(r.get(col) or "").strip() == b)
            warns.append(f"{name}: pct_basis '{b}' ({n} rows) not in the known "
                         f"enum — map the footnote wording or extend the enum")
    no_pct = [r.get("rank") for r in data["top_tenants"]
              if r.get("rank") is not None and r.get("revenue_pct") is None]
    if no_pct:
        warns.append(f"top_tenants: revenue_pct null on {len(no_pct)} row(s) "
                     f"(ranks {no_pct[:5]}{'...' if len(no_pct) > 5 else ''}) — if "
                     f"the trust ranks by another basis (e.g. NPI) the value still "
                     f"goes in revenue_pct with pct_basis set; never invent a key")

    # 7. enum discipline — verbatim wording belongs in *_raw, not enum columns
    for (name, col), allowed in ENUMS.items():
        for r in data[name]:
            v = r.get(col)
            if v is None:
                continue
            if str(v).strip().lower() not in allowed:
                who = (r.get("property_name") or r.get("client_name")
                       or r.get("symbol") or "?")
                fails.append(f"{name}.{col}='{v}' ({who}) not in enum "
                             f"{sorted(allowed)} — put the report's wording in the "
                             f"*_raw / note field, keep the enum value here")

    # 7b. category taxonomies (case-SENSITIVE — canonical labels are exact). Verbatim
    # disclosed labels belong in *_raw; `category`/`industry` must be a canonical value.
    if TRADE_CATEGORIES is not None:
        for name, col in (("trade_mix", "category"), ("top_tenants", "industry")):
            for r in data[name]:
                v = r.get(col)
                if v and v not in TRADE_CATEGORIES:
                    fails.append(f"{name}.{col}='{v}' not in the canonical 15-value "
                                 f"trade taxonomy — map via TRADE_ALIASES; keep the "
                                 f"disclosed label in category_raw")
        for r in data["properties"]:
            v = r.get("category")
            if v and v not in PROPERTY_CATEGORIES:
                fails.append(f"properties.category='{v}' ({r.get('property_name')}) not "
                             f"in the canonical 6 {sorted(PROPERTY_CATEGORIES)} — map via "
                             f"PROPERTY_CATEGORY_ALIASES; disclosed type -> category_raw")
    bad_status = [r.get("property_name") for r in data["properties"]
                  if not any(str(r.get("status") or "active").strip().lower()
                             .startswith(e)
                             for e in ("active", "divested", "held_for_sale"))]
    if bad_status:
        warns.append(f"properties.status outside active|divested|held_for_sale "
                     f"on {len(bad_status)} row(s) (e.g. {bad_status[:3]})")

    # 8. self-consistency: tenure_raw proves an expiry was disclosed
    no_expiry, no_area = [], []
    for r in data["properties"]:
        raw = str(r.get("tenure_raw") or "")
        if EXPIRY_RX.search(raw) and r.get("lease_expiry_date") is None:
            fails.append(f"properties: {r.get('property_name')} has "
                         f"lease_expiry_date=null but tenure_raw says "
                         f"'{raw[:70]}' — the date IS disclosed, extract it "
                         f"(month-year only => day 01 + note)")
        elif (str(r.get("land_tenure") or "").lower().startswith("leasehold")
              and r.get("lease_expiry_date") is None
              and ("remaining" in raw.lower() or r.get("lease_term_years")
                   or re.search(r"\d+\s*years", raw, re.IGNORECASE))):
            no_expiry.append(r.get("property_name"))
        if str(r.get("status") or "active").lower().startswith("active") \
                and r.get("gla") is None and r.get("nla") is None and r.get("gfa") is None:
            no_area.append(r.get("property_name"))
    if no_expiry:
        if declared("lease_expiry", "expiry"):
            infos.append(f"lease_expiry_date null on {len(no_expiry)} leasehold "
                         f"row(s) with a term — declared structural in _notes")
        else:
            warns.append(f"{len(no_expiry)} leasehold row(s) with a term but "
                         f"lease_expiry_date=null (e.g. {no_expiry[:3]}) — "
                         f"portfolio statements usually print the expiry; also "
                         f"check tenure_raw is VERBATIM, not paraphrased "
                         f"('X years remaining' suggests the expiry was dropped)")
    if no_area:
        if declared("gla", "nla"):
            infos.append(f"gla/nla null on {len(no_area)} active propert(ies) — "
                         f"declared structural in _notes (e.g. hospitality trusts "
                         f"disclose unit counts, not floor area)")
        else:
            warns.append(f"{len(no_area)} active propert(ies) with gla, nla AND gfa all "
                         f"null (e.g. {no_area[:3]}) — some area metric is ~95-100% "
                         f"disclosed unless sector-structural (use gfa for gross FLOOR "
                         f"area, gla for gross LETTABLE); if structural, declare in "
                         f"columns_never_fillable")

    # 4. unit sanity (trust level)
    perf = data["performance"][0] if data["performance"] else {}
    for f in ("gross_revenue", "net_property_income", "net_distributable_income",
              "portfolio_value", "total_borrowings"):
        v = perf.get(f)
        if isinstance(v, (int, float)) and 0 < v < MONEY_MIN:
            fails.append(f"performance.{f}={v:,} looks like $'000/millions, not absolute")
    props = data["properties"]
    small = [p["property_name"] for p in props
             if isinstance(p.get("market_valuation"), (int, float))
             and 0 < p["market_valuation"] < MONEY_MIN]
    if small:
        warns.append(f"properties with valuation < {MONEY_MIN:,} (unit check): {small[:5]}")

    # 4b. KPI completeness — the 7 as-disclosed capital-management KPIs are widely
    # disclosed by SGX REITs; a null one is often a silent MISS (e.g. AJBU debt tenor
    # 3.3yr was on the same Capital Management page as the captured leverage/ICR but
    # was left null with no structural-absence claim). For each null KPI, decide:
    # mentioned anywhere (flags/_notes/columns_never_fillable) -> INFO (probably a real
    # non-disclosure); silently null -> WARN (grep the source to confirm or fill it).
    KPI_FIELDS = ("aggregate_leverage", "interest_coverage_ratio", "cost_of_debt",
                  "weighted_avg_debt_maturity", "nav_per_unit", "wale",
                  "portfolio_occupancy")
    import json as _json
    mention_hay = (" ".join(str(f.get("scope", "")) + " " + str(f.get("note", ""))
                            for f in (perf.get("flags") or []))
                   + " " + _json.dumps(notes, ensure_ascii=False)
                   + " " + _json.dumps(perf.get("_notes") or {}, ensure_ascii=False)).lower()
    null_kpis = [k for k in KPI_FIELDS if perf.get(k) is None]
    if null_kpis:
        silent = [k for k in null_kpis if k not in mention_hay and k not in declared_cols]
        mentioned = [k for k in null_kpis if k not in silent]
        if mentioned:
            infos.append(f"performance KPI(s) null but noted as non-disclosed: "
                         f"{', '.join(mentioned)}")
        if silent:
            warns.append(f"performance KPI(s) null with NO flag/_notes mention — "
                         f"confirm genuinely not disclosed (grep source) or fill: "
                         f"{', '.join(silent)}")

    # financial is now a single object (1:1 income_stmt_metrics) with our line_items[]
    # audit trail. (load() wraps the object in a 1-element list.)
    fin_obj = data["financial"][0] if data["financial"] else {}
    lines = fin_obj.get("line_items") or []

    # 4b. financial completeness — the audited Statement of Total Return ALWAYS has
    # trust-level lines below NPI (management fees + finance costs, and usually a tax
    # line). If line_items has none of these, only the property revenue/opex notes were
    # captured => the statement is incomplete (the systemic under-capture).
    if lines:
        comps = [str(r.get("component", "")).lower() for r in lines]
        has_finance = any("finance" in c for c in comps)
        has_mgmt = any(("management_fee" in c) or ("manager_fee" in c) for c in comps)
        has_adj = any(r.get("statement") == "adjustment" for r in lines)
        missing = []
        if not has_finance:
            missing.append("finance_costs")
        if not has_mgmt:
            missing.append("management_fee")
        if not has_adj:
            missing.append("adjustment lines (fair-value/JV/tax)")
        if missing and not declared("financial", "income_components", "line_items"):
            warns.append(
                f"financial.line_items likely INCOMPLETE ({len(lines)} lines): missing "
                f"{', '.join(missing)}. Capture the FULL Statement of Total Return "
                f"(all lines below NPI), not just the revenue/opex notes.")
        # line_items statement enum (moved here from ENUMS — it's nested now)
        for r in lines:
            s = r.get("statement")
            if s is not None and str(s).strip().lower() not in {"revenue", "expense",
                                                                "adjustment"}:
                fails.append(f"financial.line_items statement='{s}' not in "
                             f"revenue|expense|adjustment ({r.get('component')})")

    # 4b'. revenue tie-outs. (i) financial.total_revenue must equal
    # performance.gross_revenue (two audited top-lines). (ii) Σ(line_items revenue) must
    # also equal that figure — a mismatch means a below-NPI income line (finance/interest/
    # other income) was mis-bucketed as `revenue`, the recurring mis-classification bug
    # forensic audits found in 8 of the first 10 reports. Tolerance is a small ABSOLUTE
    # figure (rounding between two audited figures is tens of $k); a 0.5%-relative
    # tolerance was too loose and MISSED J69U (624k) / M44U (2,648k).
    gr = (perf or {}).get("gross_revenue")
    ism = fin_obj.get("income_stmt_metrics") or {}
    tr = ism.get("total_revenue")
    if gr and tr and abs(tr - gr) > 50_000:
        fails.append(
            f"RECON REVENUE financial.income_stmt_metrics.total_revenue={tr:,} != "
            f"performance.gross_revenue={gr:,} (gap {tr - gr:,}) — both are the audited "
            f"top line and must tie; reconcile against the source.")
    if lines and (gr or tr):
        anchor = gr or tr
        rev_lines = [r for r in lines if r.get("statement") == "revenue"]
        rev_sum = sum(r.get("amount") or 0 for r in rev_lines)
        if anchor and rev_sum and abs(rev_sum - anchor) > 50_000:
            extra = rev_sum - anchor
            suspects = [r.get("component") for r in rev_lines
                        if any(k in str(r.get("component", "")).lower()
                               for k in ("finance", "interest", "other_income",
                                         "dividend", "fair_value", "fx"))]
            fails.append(
                f"RECON REVENUE Σ(line_items revenue)={rev_sum:,} != gross_revenue/"
                f"total_revenue={anchor:,} (gap {extra:,}). A below-NPI income line is "
                f"likely mis-bucketed as statement='revenue'"
                + (f"; suspects: {', '.join(map(str, suspects))}" if suspects else "")
                + " — it should be statement='adjustment'.")

    # 4b''. breakdown reconciliation — mirrors prod's make_sankey validation
    # (idx_manual_input_extraction): Σ revenue_breakdown ≈ total_revenue and
    # Σ operating_expense_breakdown ≈ operating_expense, within 2%. A gap means a
    # breakdown line was dropped or mis-signed (breakdown amounts are POSITIVE magnitudes).
    for bd_key, tot_key in (("revenue_breakdown", "total_revenue"),
                            ("operating_expense_breakdown", "operating_expense")):
        bd = ism.get(bd_key) or []
        tot = ism.get(tot_key)
        if bd and isinstance(tot, (int, float)) and tot:
            s = sum(i.get("amount") or 0 for i in bd)
            if abs(s / tot - 1) > 0.02:
                warns.append(
                    f"financial.income_stmt_metrics: Σ{bd_key}={s:,.0f} vs {tot_key}="
                    f"{tot:,.0f} ({abs(s/tot-1):.1%} > 2%) — a breakdown line is missing "
                    f"or mis-signed (amounts must be positive magnitudes, like prod).")

    # 4b'''. full Statement-of-Total-Return reconciliation (the line_items are the audit
    # trail that rescues the lossy standardization): Σrevenue − Σexpense + Σadjustment(signed)
    # MUST equal income_stmt_metrics.net_income, to ~50k.
    if lines and ism.get("net_income") is not None:
        srev = sum(r.get("amount") or 0 for r in lines if r.get("statement") == "revenue")
        sexp = sum(r.get("amount") or 0 for r in lines if r.get("statement") == "expense")
        sadj = sum(r.get("amount") or 0 for r in lines if r.get("statement") == "adjustment")
        recon = srev - sexp + sadj
        ni = ism["net_income"]
        if abs(recon - ni) > 50_000:
            fails.append(
                f"RECON STR Σrevenue−Σexpense+Σadjustment={recon:,} != "
                f"income_stmt_metrics.net_income={ni:,} (gap {recon-ni:,}) — a line is "
                f"missing/mis-signed, or net_income is wrong.")

    # 4b''''. cross-consistency: the same audited figure must agree across tables (both are
    # group-level; performance carries the named REIT KPI, financial the standardized bucket).
    for perf_key, ism_key, label in (
            ("gross_revenue", "total_revenue", "gross revenue"),
            ("net_property_income", "gross_income", "NPI")):
        pv = (perf or {}).get(perf_key)
        iv = ism.get(ism_key)
        if isinstance(pv, (int, float)) and isinstance(iv, (int, float)) and \
                abs(pv - iv) > 50_000:
            fails.append(
                f"RECON XTAB {label}: performance.{perf_key}={pv:,} != "
                f"financial.income_stmt_metrics.{ism_key}={iv:,} (gap {pv-iv:,}) — same "
                f"audited figure must agree across tables; investigate the source.")

    # 4b'''''. FFO equal to net_income is unlikely to be a true disclosed FFO (net income
    # includes non-cash fair-value items FFO excludes) — flag to verify it's disclosed, not an alias.
    ffo = ism.get("funds_from_operation")
    if ffo is not None and ism.get("net_income") is not None \
            and abs(ffo - ism["net_income"]) <= 50_000:
        warns.append(
            "financial: funds_from_operation == net_income — verify this is a FFO disclosed in "
            "the report, not an alias of net_income (net income includes non-cash fair-value "
            "items FFO excludes); else set null or list in _derived. SG distributable income "
            "lives in performance.net_distributable_income.")

    # 4c. trade_mix completeness — a trade-mix breakdown should sum to ~100% of its
    # basis. A sum well below 100 means rows were dropped (split/long table). An empty
    # trade_mix is only valid as a declared structural absence (e.g. hospitality).
    tmix = data["trade_mix"]
    if tmix:
        tmsum = sum(r.get("pct") or 0 for r in tmix)
        if not (95 <= tmsum <= 105):
            warns.append(f"trade_mix sums to {tmsum:.1f}% over {len(tmix)} rows "
                         f"(expected ~100%) — rows may be missing or double-counted")
    elif not declared("trade_mix"):
        warns.append("trade_mix is empty and not declared structural in _notes "
                     "(valid only for sub-sectors with no tenant trade mix, e.g. hospitality)")

    # 4d. top_tenants presence — a top-N tenants table is near-universal; empty usually
    # means the section was missed.
    if not data["top_tenants"] and not declared("top_tenants"):
        warns.append("top_tenants is empty and not declared structural — the top-N "
                     "tenants/customers table was likely missed")

    # 4e. inferred-value provenance (REFERENCE §0 #7) — inferred/derived values must be
    # declared in _notes.inferred[] so they aren't mistaken for disclosed data.
    notes = data["_notes"][0] if data["_notes"] else {}
    inferred = notes.get("inferred", []) or []
    inferred_fields = {(str(i.get("table", "")), str(i.get("field", ""))) for i in inferred}
    for i in inferred:
        if not (i.get("table") and i.get("field") and i.get("basis")):
            warns.append(f"_notes.inferred entry missing table/field/basis: {i}")
    # heuristic: a per-property field that is uniform across many rows is usually a portfolio
    # figure applied per-property (inference) — must be declared inferred.
    for field in ("occupancy_rate",):
        vals = [p.get(field) for p in props if isinstance(p.get(field), (int, float))]
        if len(vals) >= 5 and len(set(vals)) == 1 \
                and ("properties", field) not in inferred_fields:
            warns.append(f"properties.{field} is uniform ({vals[0]}) across {len(vals)} rows "
                         f"— if applied from a portfolio figure it's INFERRED; declare it in "
                         f"_notes.inferred[] (or it's coincidence — confirm)")

    # 5. fill rates
    if props:
        keys = sorted({k for p in props for k in p})
        print(f"\nfill rates over {len(props)} properties:")
        for k in keys:
            n = sum(1 for p in props if p.get(k) not in (None, "", [], {}))
            bar = "#" * round(20 * n / len(props))
            print(f"  {k:28s} {n:3d}/{len(props)}  {bar}")

    # 6. reconciliation
    def consolidated(p):
        # JV/associate flags live in value_basis when present, but extractions made
        # before that column existed carry the fact in free text (status/notes) —
        # scan the whole record (trap #9 in REFERENCE.md)
        blob = json.dumps(p).lower()
        if any(t in blob for t in ("joint venture", "joint_venture",
                                   "equity-accounted", "associate")):
            return False
        return "divest" not in str(p.get("status", "active")).lower()

    notes_recon = (data["_notes"][0] if data["_notes"] else {}).get("reconciliation", {})

    def notes_reconciles(stub: str) -> bool:
        # the extracting agent's own reconciliation (built at the report's disclosed
        # granularity, e.g. combined property lines) is authoritative when it agrees
        s = notes_recon.get(f"sum_property_{stub}")
        r = notes_recon.get(f"reported_total_{stub}")
        return (isinstance(s, (int, float)) and isinstance(r, (int, float))
                and r and abs(s / r - 1) < 0.01)

    rep_ccy = str(perf.get("currency") or "").strip().upper()

    def row_ccy(p, field, stub):
        # a field-specific override (e.g. npi_currency) beats the row currency
        c = (p.get(f"{field}_currency") or p.get(f"{stub}_currency")
             or p.get("currency") or rep_ccy)
        return str(c).strip().upper()

    for field, stub in (("gross_revenue", "gross_revenue"),
                        ("net_property_income", "npi")):
        candidates = [p for p in props if consolidated(p)
                      and isinstance(p.get(field), (int, float))]
        vals = [p[field] for p in candidates
                if not rep_ccy or row_ccy(p, field, stub) == rep_ccy]
        skipped_ccy = len(candidates) - len(vals)
        if skipped_ccy:
            note = (f"{field}: {skipped_ccy} row(s) in a different currency than "
                    f"performance ({rep_ccy}) excluded from the row-level sum")
            if notes_reconciles(stub) or notes_reconciles(field):
                warns.append("RECON CROSS-CCY " + note +
                             " - _notes reconciliation agrees at its own "
                             "currency/granularity")
            else:
                warns.append("RECON CROSS-CCY " + note +
                             " - and _notes reconciliation absent/disagrees: add a "
                             "local-currency reconciliation to _notes")
        rep = perf.get(field)
        if vals and isinstance(rep, (int, float)) and rep:
            s = sum(vals)
            d = abs(s / rep - 1)
            line = (f"sum(property.{field}) = {s:,.0f} vs reported {rep:,.0f} "
                    f"(diff {d:.2%}, {len(vals)} props)")
            if d < 0.01:
                print("RECON OK   " + line)
            elif notes_reconciles(stub) or notes_reconciles(field):
                warns.append("RECON VIA NOTES " + line +
                             " - row-level sum diffs but _notes reconciliation agrees "
                             "(combined lines / divested-in-year); verify _notes basis")
            elif d < 0.05:
                warns.append("RECON NEAR " + line +
                             " - check combined lines / JV / divested-in-year")
            else:
                fails.append("RECON DIFF " + line +
                             " - duplicate rows, missed property, or basis mix likely")
        elif isinstance(rep, (int, float)) and not vals:
            if declared(field, stub):
                infos.append(f"no per-property {field} to reconcile — declared "
                             f"structural in _notes")
            else:
                warns.append(f"no per-property {field} to reconcile (if structural"
                             f" — e.g. master lease / EMA — declare it in "
                             f"columns_never_fillable)")

    notes = data["_notes"][0] if data["_notes"] else {}
    for key in ("columns_never_fillable", "data_with_no_home",
                "parsing_traps", "reconciliation"):
        if key not in notes:
            warns.append(f"_notes.json missing '{key}'")

    report()


def report() -> None:
    print()
    for i in dict.fromkeys(infos):
        print("INFO", i)
    for w in dict.fromkeys(warns):
        print("WARN", w)
    for f in dict.fromkeys(fails):
        print("FAIL", f)
    print(f"\n{'GATE: FAIL' if fails else 'GATE: PASS'} "
          f"({len(fails)} fail, {len(set(warns))} warn, {len(set(infos))} info)")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
