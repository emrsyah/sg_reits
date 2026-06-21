# Cockpit v2 — backend (Supabase + R2): status & runbook

Single reference for the data backend behind the new Next.js review cockpit. Built
2026-06-19. Companion docs: **`docs/cockpit_nextjs_plan.md`** (architecture + decisions) and
**`docs/fe_data_contract.md`** (the FE spec). Schema source of truth: `schema/models.py` +
`db/schema.sql`.

## What's live
| Layer | State |
|---|---|
| **Supabase Postgres** | 11 tables (`db/schema.sql`), RLS enabled. Loaded all 36 FY2025 reports. |
| **Cloudflare R2** bucket `reits-ar` | 36 annual-report PDFs; object key = PDF filename, matches `reit_report.pdf_r2_key`. |

Row counts after load (verify anytime — see Runbook):
`profile 36 · performance 36 · property 1624 · top_tenant 374 · trade_mix 359 · financial 36 ·
property_transaction 93 · notes 36 · reit_report 36` (all reports have a `pdf_r2_key`).
_(Batch 5 added 6: XZL, M1GU, BMOU, J85, C2PU, CRPU — Jun 19 2026.)_

> **Loader gotcha:** `load_supabase.py` takes dir **names** (`XZL.SI_FY2025`), not paths —
> it prepends `extracted/` internally. Passing `extracted/XZL.SI_FY2025` silently loads only
> the `reit_report` row (file-independent) and 0 data rows.

## Tables
**Data** (one report = one `(symbol, financial_year)`): `sgx_reit_profile` (PK `symbol`),
`sgx_reit_performance`, `sgx_reit_property`, `sgx_reit_top_tenant`, `sgx_reit_trade_mix`,
`sgx_reit_financial`, `sgx_reit_property_transaction`, `sgx_reit_notes`. Nested/list fields are
`jsonb` (management, flags, distribution_record, major_tenants, trade_mix, the three financial
blobs, line_items, notes, txn raw).
**Inventory + review**: `reit_report` (`pdf_r2_key`, `page_offset`), `reit_record_verdict`,
`reit_field_edit`. RLS: authenticated reviewers SELECT data; verdict/edit writes restricted to
`reviewer = auth.uid()`. Service key bypasses RLS (loader uses it).

## Currency & units — two layers (audit trail vs normalized)

This **proofread DB is source-faithful**: every figure is stored **as the report discloses it**, so
a reviewer can tie it back to the page. The **production DB normalizes** (→ SGD, → sqft) at its own
load transform. We do **not** FX-convert or unit-convert in this layer.

**How it's stored** (`sgx_reit_property`):
- `currency` — the **presentation** currency of `market_valuation`, as-reported (USD for a US trust,
  SGD for an SG-reporting trust). This is always the answer to "is this out of SGD?".
- `original_currency` / `original_value` — **AUDIT TRAIL**: the asset's local/transacting currency +
  figure, populated **only when the report prints it separately** from the presentation currency
  (e.g. RMB for a China mall reported in SGD — BMOU, CRPU). null otherwise (single-currency report).
  Never summed with `market_valuation`, never derived.
- `area_unit` — **AUDIT TRAIL**: `'sqft'` | `'sqm'` of `gla`/`nla`/`gfa` as disclosed. Set whenever
  any area is set; areas are stored unit-less otherwise so this is required to interpret them.
- FX rates the report discloses (closing for valuation, average for income) live in
  `sgx_reit_notes.notes → fx_rates: [{pair, closing, average, source_page}]`.

**Prod transform (later, NOT here):**
- area → sqft: `sqm × 10.7639` (fixed factor — lossless, deterministic).
- value → SGD: where `currency = SGD` already, no-op. Where the **presentation** currency is foreign
  (XZL = USD) **prod must source an external FX rate** (e.g. FY-end closing) — the report carries no
  SGD figure, so this conversion is **not free** and must be specified in the prod spec.
- percentages: we store plain numbers (`33.9`); prod stores fractions (`0.339`) — deterministic.
- per-unit: `dpu` is in cents, `nav_per_unit` in dollars — prod standardizes at load.

## Scripts (all idempotent; repo root; read `.env`)
| Script | Role |
|---|---|
| `scripts/db/apply_schema.py` | apply/refresh `db/schema.sql` (safe to re-run) |
| `scripts/db/load_supabase.py [DIR…]` | upsert `extracted/<SYM>.SI_FY<YYYY>/` → Postgres; no args = all dirs. Singletons upsert; list tables delete-then-insert per `(symbol,FY)` |
| `scripts/db/upload_r2.py [--all-pdfs]` | upload PDFs referenced by `reit_report` (or every `annual_reports/*.pdf`) to R2 via REST; HEAD-skips existing |

## Credentials (`.env`)
Already present: `SUPABASE_CONNECTION_STRING`, `SUPABASE_PUBLISHABLE_KEY`, `SUPABASE_SECRET_KEY`,
`CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_API_TOKEN`.
- The **account API token** uploads to R2 (used by `upload_r2.py`) but **cannot presign**.
- The **FE** needs an **R2 API Token** (Cloudflare → R2 → *Manage R2 API Tokens*, Object
  Read/Write on `reits-ar`) → `R2_ACCESS_KEY_ID` / `R2_SECRET_ACCESS_KEY` for presigned GET URLs.

## Runbook
```bash
# (re)apply schema
python scripts/db/apply_schema.py

# load / reload extractions (after a new batch)
python scripts/db/load_supabase.py                 # all
python scripts/db/load_supabase.py OXMU.SI_FY2025  # one report

# ensure PDFs are in R2
python scripts/db/upload_r2.py

# verify row counts
python - <<'PY'
import os,psycopg2; from dotenv import load_dotenv
load_dotenv("C:/Users/emirsyah/supertype/s_reits/.env")
c=psycopg2.connect(os.environ["SUPABASE_CONNECTION_STRING"]).cursor()
for t in ["sgx_reit_profile","sgx_reit_performance","sgx_reit_property","sgx_reit_top_tenant",
          "sgx_reit_trade_mix","sgx_reit_financial","sgx_reit_property_transaction",
          "sgx_reit_notes","reit_report"]:
    c.execute(f"select count(*) from {t}"); print(t, c.fetchone()[0])
PY
```
The FE reads live from Postgres + R2, so reloading data needs **no FE redeploy**.

## FE — what's left for the human
1. Create the **R2 API Token** (above) → add the two `R2_*` keys.
2. Add `NEXT_PUBLIC_SUPABASE_URL` (dashboard) + the publishable/secret keys to the FE env.
3. Build against `docs/fe_data_contract.md` (read query, record-identity model, Server Action
   write contracts, presigned-URL helper, magic-link auth).

## Open items / sequencing
- **Git history rewrite still pending**: PDFs are still committed (`.git` ≈ 1.1 GB). Plan: back
  up PDFs → `git filter-repo` strip `annual_reports/*.pdf` + `.gitignore` → force-push → then
  commit the v2 backend code. (User is sole repo holder; reviewers use the web app — force-push
  is safe.) See `docs/cockpit_nextjs_plan.md` §5.
- **Uncommitted on `main`**: 6 new PDFs, `_manifest.csv`, `scripts/reconcile.py`, `db/schema.sql`,
  `scripts/db/*`, `docs/cockpit_*.md` + `docs/fe_data_contract.md`.
- **3 FY2025 ARs still absent**: Landmark (D5IU, obtainable), NTT DC (NTDU), UI Boustead (UIBU).
- When `reviews/*.json` verdicts exist from the old Flask cockpit, migrate them into
  `reit_record_verdict` / `reit_field_edit` (or start fresh).
