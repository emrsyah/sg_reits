"""validate_schema.py - validate an extracted trust-year against schema/models.py.

Usage: python validate_schema.py extracted/<SYMBOL>_FY<YYYY>

Complements check_extraction.py (which does reconciliation / fill-rate / units). This
script enforces the TYPE-and-enum contract: it loads the Pydantic models that mirror the
locked 6-table schema and validates every record, so a wrong type, a bad enum, or a
malformed shape fails loudly with the exact field path.

It maps the 8-file extraction intermediate onto the 6 schema models:
  profile.json            -> Profile        (single object)
  performance.json        -> Performance    (single object)
  properties.json         -> Property       (list)
  top_tenants.json        -> TopTenant      (list)
  trade_mix.json          -> TradeMix       (list)
  income_components.json  -> FinancialLine  (list)
property_transactions.json and _notes.json are intermediate-only (no schema table) and
are skipped. Extra fields in the intermediate (value_basis, alt_value, ...) are ignored
by Pydantic - this validates the schema-bound fields without rejecting the audit trail.

Exit code 1 if any record fails validation.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]      # repo root (.claude/skills/<name>/scripts/this)
sys.path.insert(0, str(ROOT / "schema"))

try:
    import models  # schema/models.py
    from pydantic import ValidationError
except ImportError as e:
    sys.exit(f"cannot import schema/models.py or pydantic: {e}\n"
             f"(pip install pydantic; ensure {ROOT / 'schema' / 'models.py'} exists)")

# extraction filename -> (model, is_list). Mirrors models.SECTIONS but keyed by the
# intermediate filenames the agent actually writes.
FILE_MODEL = {
    "profile.json":           (models.Profile,       False),
    "performance.json":       (models.Performance,   False),
    "properties.json":        (models.Property,      True),
    "top_tenants.json":       (models.TopTenant,     True),
    "trade_mix.json":         (models.TradeMix,      True),
    "income_components.json": (models.FinancialLine, True),
}


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    base = Path(sys.argv[1])
    if not base.is_dir():
        sys.exit(f"not a directory: {base}")

    total_ok = total_err = 0
    for fname, (model, is_list) in FILE_MODEL.items():
        p = base / fname
        if not p.exists():
            print(f"WARN  {fname} missing")
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"FAIL  {fname}: invalid JSON - {e}")
            total_err += 1
            continue
        records = data if isinstance(data, list) else [data]
        ok = err = 0
        for i, rec in enumerate(records):
            if not isinstance(rec, dict):
                print(f"FAIL  {fname}[{i}]: not an object")
                err += 1
                continue
            try:
                model.model_validate(rec)
                ok += 1
            except ValidationError as e:
                err += 1
                who = (rec.get("property_name") or rec.get("tenant_name")
                       or rec.get("category") or rec.get("component")
                       or rec.get("symbol") or f"index {i}")
                for line in e.errors():
                    loc = ".".join(str(x) for x in line["loc"])
                    print(f"FAIL  {fname} [{who}] .{loc}: {line['msg']} "
                          f"(got {line.get('input')!r})")
        total_ok += ok
        total_err += err
        flag = "OK  " if err == 0 else "FAIL"
        print(f"{flag}  {fname:24s} {ok} valid"
              f"{f', {err} invalid' if err else ''}")

    print(f"\nSCHEMA: {'FAIL' if total_err else 'PASS'} "
          f"({total_ok} valid, {total_err} invalid)")
    sys.exit(1 if total_err else 0)


if __name__ == "__main__":
    main()
