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

FILES = ["profile", "performance", "properties", "property_transactions",
         "top_tenants", "trade_mix", "income_components", "_notes"]
PCT_TABLES = {"top_tenants": "pct_basis", "trade_mix": "pct_basis"}
MONEY_MIN = 1_000_000          # trust-level GR/NPI below this => probably $'000 left unscaled

ENUMS = {  # (file, column): allowed values; None always allowed
    ("properties", "land_tenure"): {"freehold", "leasehold"},
    ("properties", "value_basis"): {"consolidated", "joint_venture_100pct",
                                    "effective_interest"},
    ("property_transactions", "transaction_type"): {"acquisition", "divestment"},
    ("income_components", "statement"): {"revenue", "expense", "adjustment"},
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
    data = {name: load(base, name) for name in FILES}
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
        if name in ("_notes", "profile"):
            continue
        missing = sum(1 for r in data[name] if isinstance(r, dict) and not has_page(r))
        if missing:
            fails.append(f"{name}: {missing} record(s) without source_page")

    # 3. basis on percentages
    for name, col in PCT_TABLES.items():
        for r in data[name]:
            if r.get("pct") is not None or r.get("gri_percentage") is not None:
                if not r.get(col):
                    fails.append(f"{name}: record missing {col} "
                                 f"({r.get('tenant_name') or r.get('category')})")
        unknown = {str(r.get(col)).strip() for r in data[name]
                   if r.get(col) and str(r.get(col)).strip().lower()
                   not in KNOWN_PCT_BASIS}
        for b in sorted(unknown):
            n = sum(1 for r in data[name] if str(r.get(col) or "").strip() == b)
            warns.append(f"{name}: pct_basis '{b}' ({n} rows) not in the known "
                         f"enum — map the footnote wording or extend the enum")
    no_pct = [r.get("rank") for r in data["top_tenants"]
              if r.get("rank") is not None and r.get("gri_percentage") is None]
    if no_pct:
        warns.append(f"top_tenants: gri_percentage null on {len(no_pct)} row(s) "
                     f"(ranks {no_pct[:5]}{'...' if len(no_pct) > 5 else ''}) — if "
                     f"the trust ranks by another basis (e.g. NPI) the value still "
                     f"goes in gri_percentage with pct_basis set; never invent a key")

    # 7. enum discipline — verbatim wording belongs in *_raw, not enum columns
    for (name, col), allowed in ENUMS.items():
        for r in data[name]:
            v = r.get(col)
            if v is None:
                continue
            if str(v).strip().lower() not in allowed:
                who = (r.get("property_name") or r.get("component")
                       or r.get("symbol") or "?")
                fails.append(f"{name}.{col}='{v}' ({who}) not in enum "
                             f"{sorted(allowed)} — put the report's wording in the "
                             f"*_raw / note field, keep the enum value here")
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
                and r.get("gla") is None and r.get("nla") is None:
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
            warns.append(f"{len(no_area)} active propert(ies) with both gla and "
                         f"nla null (e.g. {no_area[:3]}) — area is ~95-100% "
                         f"disclosed unless sector-structural; if structural, "
                         f"declare gla/nla in columns_never_fillable")

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

    # 4b. financial completeness — the audited Statement of Total Return ALWAYS has
    # trust-level lines below NPI (management fees + finance costs, and usually a tax
    # line). If income_components has none of these, only the property revenue/opex
    # notes were captured => the statement is incomplete (the systemic under-capture).
    fin = data["income_components"]
    if fin:
        comps = [str(r.get("component", "")).lower() for r in fin]
        has_finance = any("finance" in c for c in comps)
        has_mgmt = any(("management_fee" in c) or ("manager_fee" in c) for c in comps)
        has_adj = any(r.get("statement") == "adjustment" for r in fin)
        missing = []
        if not has_finance:
            missing.append("finance_costs")
        if not has_mgmt:
            missing.append("management_fee")
        if not has_adj:
            missing.append("adjustment lines (fair-value/JV/tax)")
        if missing and not declared("income_components"):
            warns.append(
                f"income_components likely INCOMPLETE ({len(fin)} lines): missing "
                f"{', '.join(missing)}. Capture the FULL Statement of Total Return "
                f"(all lines below NPI), not just the revenue/opex notes.")

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
