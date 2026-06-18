"""build_db_examples.py — emit clean, DB-shaped example rows for the 6 sgx_reit_* tables.

For Gerald: "JSON examples for each of the 6 tables that reflect what will actually be
pushed into the DB." Loads an extracted report, validates each record against
schema/models.py (so ONLY real schema fields survive — intermediate audit-trail extras
like value_basis/alt_value are dropped), and writes one file per table to
docs/db_examples/. List tables get a few representative rows; dict tables get the row.

Usage: python scripts/build_db_examples.py [SYMBOL.SI_FYYYYY]   (default: M44U.SI_FY2025)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "schema"))
import models  # noqa: E402

OUT = ROOT / "docs" / "db_examples"
N_LIST = 3  # representative rows for list-shaped tables

# file -> (model, table, is_list)
SPEC = [
    ("profile.json",     models.Profile,            "sgx_reit_profile",     False),
    ("properties.json",  models.Property,           "sgx_reit_property",    True),
    ("performance.json", models.Performance,        "sgx_reit_performance", False),
    ("top_tenants.json", models.TopTenant,          "sgx_reit_top_tenant",  True),
    ("trade_mix.json",   models.TradeMix,           "sgx_reit_trade_mix",   True),
    ("financial.json",   models.FinancialStatement, "sgx_reit_financial",   False),
]


def clean(model, rec, table):
    """Validate -> dump only schema fields. by_alias so FinancialBreakdownItem emits
    `class` (not `cls`), matching prod."""
    obj = model.model_validate(rec)
    d = obj.model_dump(by_alias=True, exclude_none=False)
    if table == "sgx_reit_profile":
        d.pop("income_model", None)  # working metadata; not loaded to DB
    return d


def main():
    rep = sys.argv[1] if len(sys.argv) > 1 else "M44U.SI_FY2025"
    src = ROOT / "extracted" / rep
    if not src.is_dir():
        sys.exit(f"not found: {src}")
    OUT.mkdir(parents=True, exist_ok=True)

    written = []
    for fname, model, table, is_list in SPEC:
        raw = json.loads((src / fname).read_text(encoding="utf-8"))
        if is_list:
            rows = [clean(model, r, table) for r in raw[:N_LIST]]
            payload = rows
            n = f"{len(rows)} of {len(raw)} rows"
        else:
            payload = clean(model, raw, table)
            n = "1 row"
        (OUT / f"{table}.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        written.append(f"  {table}.json  ({n})")
    print(f"wrote db examples from {rep} to {OUT}:")
    print("\n".join(written))


if __name__ == "__main__":
    main()
