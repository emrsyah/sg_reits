# Data quality checks

Four layers. The first three are deterministic and run without an LLM; the fourth is the only
one that reads the source PDF.

| layer | scope | gates? | where |
| ----- | ----- | ------ | ----- |
| `validate_schema.py` | one extraction | yes | `.claude/skills/reit-extract/scripts/` |
| `check_extraction.py` | one extraction | yes | `.claude/skills/reit-extract/scripts/` |
| `db_guard.py` | the whole database | yes | `scripts/review/` |
| `reit-audit` skill | one extraction vs its PDF | no | `.claude/skills/reit-audit/` |

---

## db_guard.py

Runs against the dev database and checks invariants that span rows, years and whole columns.
Every defect found in the 2026-07-30 schema review was of that kind, which is why the
per-report gates missed all of them.

```bash
python scripts/review/db_guard.py                  # everything
python scripts/review/db_guard.py --only scale,sums
python scripts/review/db_guard.py --list           # group names
python scripts/review/db_guard.py --quiet          # findings only
python scripts/review/db_guard.py --json           # for CI
```

Exits 1 if anything FAILs. WARNs never fail the run. Read-only: no DDL, no writes.

| group | what it catches |
| ----- | --------------- |
| `scale` | a percentage outside 0–1, or a non-percentage scaled by mistake |
| `enums` | any of 11 controlled vocabularies drifting |
| `mapping` | `category == category_raw` and not canonical, the signature of a skipped alias step |
| `sums` | trade_mix not summing to 100 per segment, NPI above revenue |
| `keys` | duplicate keys, cross-year duplicate deals, a `deal_id` grouping one row |
| `tallies` | the distribution rollforward, `sum(record.dpu) = dpu` |
| `nulls` | a null in a column prod declares NOT NULL |
| `currency` | an untagged money figure, a price and basis in different currencies |
| `coverage` | a REIT-year with no `sgx_reit_performance` row, so no FX anchor |
| `final_sync` | `_final` row count not matching raw, meaning the build did not run |
| `segments` | `basis_segment` tagged in one year but not the next |

### Waivers

`scripts/review/db_guard_waivers.json` holds known findings that are accepted rather than
fixed. A waiver is keyed on `(group, check)` and downgrades that check from FAIL.

The finding is still printed under WAIVED with its full message and reason, so a waiver hides
the failure status but never the evidence. A new row appearing in a waived check still shows
up in the text.

Delete a waiver once the data is fixed. Do not add one to turn a run green without a reason
someone else can check.

---

## check_extraction.py

Per-extraction QC gate. Run it on a directory before loading.

```bash
python .claude/skills/reit-extract/scripts/check_extraction.py extracted/<SYMBOL>_FY<YYYY>
```

Checks files and JSON parsing, provenance, `pct_basis` discipline, units, per-column fill
rates, revenue and NPI reconciliation, enum discipline, and self-consistency between
`tenure_raw` and `lease_expiry_date`.

It also enforces the v2 transaction contract: a retired field carrying a value is a FAIL,
because the loader drops it silently and the value is lost.

**Extractions produced before 2026-08-04 will fail this gate**, and that is correct. They
carry `gain_on_divestment`, `carrying_value`, `valuation`, `net_sale_proceeds`,
`transaction_date`, `revenue_pct` and `gla`. The database was migrated in place; the older
`extracted/` JSON was not. Re-run the gate on anything you intend to re-load.

---

## validate_schema.py

Type and enum contract, from the Pydantic models in `schema/models.py`. A wrong type, bad
enum or malformed shape fails with the exact field path.

```bash
python .claude/skills/reit-extract/scripts/validate_schema.py extracted/<SYMBOL>_FY<YYYY>
```

---

## sanity_scan.py

Deterministic proofreader across the whole `extracted/` set. Flags implausible values,
internal inconsistency and outliers. Always exits 0, so it reports rather than gates.

```bash
python scripts/review/sanity_scan.py            # everything
python scripts/review/sanity_scan.py DHLU UD1U  # just these
```

---

## reit-audit

The LLM forensic auditor, and the only layer that compares against the source PDF. It is the
only thing that catches a wrong-but-plausible value or a false "not disclosed" claim, because
every other layer only sees our own JSON.

Run it on high-risk reports before a scale-up load: stapled trusts, multi-currency portfolios,
and anything with an operator or master-lease structure.

---

## CI

`.github/workflows/db-guard.yml` runs `db_guard.py` on:

- a push to `main` touching `scripts/db/**`, `scripts/review/db_guard*` or `schema/**`
- a pull request touching the same paths
- manual dispatch from the Actions tab, with an optional group filter

Needs one repo secret: `SUPABASE_CONNECTION_STRING`, the direct Postgres URI for dev.

The full report goes to the job summary and is uploaded as an artifact, so a failure is
readable without re-running anything.

---

## Order to run them

```
extract  ->  validate_schema.py  ->  check_extraction.py  ->  load to dev
         ->  db_guard.py  ->  build_final_tables.py  ->  db_guard.py  ->  promote
```

`db_guard.py` twice on purpose: once to catch a bad load before it propagates, once after the
`_final` build to catch anything the build itself introduced. The `scale` group only reads
`_final`, so the second run is the one that sees it.
