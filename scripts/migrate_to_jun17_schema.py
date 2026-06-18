"""migrate_to_jun17_schema.py — migrate existing extracted/ outputs to the Jun 17 schema.

Per-dir, in place (with .premigration.bak backups), for every extracted/<SYM>.SI_FY<YYYY>/:
  - income_components.json (list of note-lines) -> financial.json (1:1 income_stmt_metrics
    object): lines go into line_items; revenue/expense lines also seed
    revenue_breakdown / operating_expense_breakdown; total_revenue = Σ revenue lines;
    gross_income := performance.net_property_income (prod's mapping). The remaining
    standardized buckets (cost_of_revenue/operating_income/ebit/ebitda/...) are left null
    — they need prod's standardization and are filled on re-extraction, not invented here.
  - properties.json   : category -> canonical 6 (+ category_raw = disclosed label)
  - trade_mix.json    : category -> canonical 15 (+ category_raw if absent)
  - top_tenants.json  : tenant_name->client_name, trade_sector->industry (canonical 15),
                        gri_percentage->revenue_pct

Idempotent: re-running is a no-op once financial.json exists / categories are canonical.
Usage: python scripts/migrate_to_jun17_schema.py [extracted/<dir> ...]   (default: all)
"""
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "schema"))
import models  # noqa: E402

EXTRACTED = ROOT / "extracted"
TRADE = set(models.TRADE_CATEGORIES)
TRADE_ALIASES = models.TRADE_ALIASES
PROP = set(models.PROPERTY_CATEGORIES)
PROP_ALIASES = models.PROPERTY_CATEGORY_ALIASES


def read(p):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def write(p, obj):
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def backup(p):
    bak = p.with_suffix(p.suffix + ".premigration.bak")
    if not bak.exists():
        bak.write_text(p.read_text(encoding="utf-8"), encoding="utf-8")


def canon_trade(label):
    """disclosed/old label -> canonical 15 (or None if unmappable)."""
    if not label:
        return None
    if label in TRADE:
        return label
    return TRADE_ALIASES.get(label)


def canon_prop(label):
    if not label:
        return None
    if label in PROP:
        return label
    return PROP_ALIASES.get(label)


def migrate_properties(d):
    p = d / "properties.json"
    rows = read(p)
    if not rows:
        return
    changed = False
    for r in rows:
        cat = r.get("category")
        if cat and cat not in PROP:
            mapped = canon_prop(cat)
            r.setdefault("category_raw", cat)
            r["category"] = mapped          # None if unmappable -> surfaced by the gate
            changed = True
    if changed:
        backup(p)
        write(p, rows)
        print(f"  properties.json: remapped categories")


def migrate_trade_mix(d):
    p = d / "trade_mix.json"
    rows = read(p)
    if not rows:
        return
    changed = False
    for r in rows:
        cat = r.get("category")
        if cat and cat not in TRADE:
            r.setdefault("category_raw", cat)
            r["category"] = canon_trade(cat)
            changed = True
    if changed:
        backup(p)
        write(p, rows)
        print(f"  trade_mix.json: remapped categories")


def migrate_top_tenants(d):
    p = d / "top_tenants.json"
    rows = read(p)
    if not rows:
        return
    changed = False
    for r in rows:
        if "tenant_name" in r and "client_name" not in r:
            r["client_name"] = r.pop("tenant_name"); changed = True
        if "trade_sector" in r and "industry" not in r:
            sec = r.pop("trade_sector")
            r["industry"] = canon_trade(sec) if sec else sec
            if sec and r["industry"] != sec:
                r.setdefault("industry_raw", sec)
            changed = True
        if "gri_percentage" in r and "revenue_pct" not in r:
            r["revenue_pct"] = r.pop("gri_percentage"); changed = True
    if changed:
        backup(p)
        write(p, rows)
        print(f"  top_tenants.json: renamed fields + mapped industry")


def migrate_financial(d):
    fin_p = d / "financial.json"
    ic_p = d / "income_components.json"
    if fin_p.exists() or not ic_p.exists():
        return
    lines = read(ic_p) or []
    perf = read(d / "performance.json") or {}
    sym = lines[0].get("symbol") if lines else perf.get("symbol")
    fy = lines[0].get("financial_year") if lines else perf.get("financial_year")
    ccy = next((l.get("currency") for l in lines if l.get("currency")), None)

    def bd(stmt):
        return [{"category": l.get("component"), "amount": l.get("amount"), "class": None}
                for l in lines if l.get("statement") == stmt]

    rev_sum = sum(l.get("amount") or 0 for l in lines if l.get("statement") == "revenue")
    pages = [l.get("source_page") for l in lines if isinstance(l.get("source_page"), int)]
    income_stmt = {
        # derivable now from the old note-lines:
        "total_revenue": rev_sum or None,
        "gross_income": perf.get("net_property_income"),   # prod maps NPI -> gross_income
        # the rest need prod standardization on re-extraction (left null, NOT invented):
        "cost_of_revenue": None, "operating_income": None, "operating_expense": None,
        "ebit": None, "ebitda": None, "pretax_income": None, "income_taxes": None,
        "net_income": None, "non_operating_income_or_loss": None,
        "interest_expense_non_operating": None, "diluted_shares_outstanding": None,
        "net_property_sales": None, "funds_from_operation": None,
        "unitholders": None, "perpetual_security_holders": None, "minorities": None,
        "revenue_breakdown": bd("revenue"),
        "operating_expense_breakdown": bd("expense"),
    }
    fin = {
        "symbol": sym, "financial_year": fy, "currency": ccy,
        "income_stmt_metrics": income_stmt,
        # not in the old income_components — must be extracted from the audited Statement of
        # Financial Position / Cash Flows on re-extraction:
        "balance_sheet_metrics": None,
        "cash_flow_metrics": None,
        "line_items": [
            {"statement": l.get("statement"), "component": l.get("component"),
             "amount": l.get("amount"), "label_raw": l.get("label_raw"),
             "source_page": l.get("source_page")}
            for l in lines
        ],
        "source_page": Counter(pages).most_common(1)[0][0] if pages else None,
        "_migration": "from income_components.json (Jun17 schema); standardized buckets + "
                      "balance_sheet/cash_flow pending re-extraction",
    }
    backup(ic_p)
    write(fin_p, fin)
    print(f"  financial.json: built from {len(lines)} note-lines "
          f"(total_revenue={rev_sum:,})" if rev_sum else "  financial.json: built")


def migrate_dir(d):
    print(f"{d.name}:")
    migrate_properties(d)
    migrate_trade_mix(d)
    migrate_top_tenants(d)
    migrate_financial(d)


def main():
    if len(sys.argv) > 1:
        dirs = [Path(a) for a in sys.argv[1:]]
    else:
        dirs = sorted(d for d in EXTRACTED.iterdir() if d.is_dir() and ".SI_FY" in d.name)
    for d in dirs:
        migrate_dir(d)
    print(f"\nmigrated {len(dirs)} dir(s).")


if __name__ == "__main__":
    main()
