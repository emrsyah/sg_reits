# Plan — Cockpit v2: Next.js + Supabase + Cloudflare R2

**Status:** PLAN (for review — no code yet). **Date:** 2026-06-19.
Replaces the local Flask cockpit (`scripts/review/app.py`) with a hosted, fast,
multi-reviewer web app, and does the planned `sgx_reit_*` DB load at the same time.

## 1. Why (root cause of "too slow")
Measured today:
- **`annual_reports/` = 1.3 GB, 101 PDFs, all committed to git → `.git` = 1.1 GB.**
- **`extracted/` = 2.4 MB (241 tiny JSON files).** `parsed_reports_datalab/` = 40 MB.

So the data is trivial; the weight is **PDFs in git**. Every VPS deploy does
`git reset --hard origin/main` over a 1.1 GB repo, and the Flask app streams 10–35 MB
PDFs per page view. A Next.js rewrite alone won't fix that — the fix is **PDFs out of git
→ object storage**, and **structured data → Postgres**. The frontend rewrite is for UX
(no full-page reloads, instant verdict writes).

## 2. Target architecture
- **Frontend/host:** Next.js (App Router) on **Vercel**. Server Components read data;
  Server Actions write verdicts/edits. No separate API server.
- **Data:** **Supabase Postgres** — the 6 `sgx_reit_*` tables (this IS the planned DB load,
  the jun17 "REITs DB = source of truth" endgame) + the review/verdict tables.
- **PDFs:** **Cloudflare R2** (S3-compatible, free egress). One-time upload of the 101 PDFs;
  served via CDN with `#page=N`. Removed from the git repo.
- **Auth:** Supabase Auth (email magic-link) so verdicts are per-reviewer — the current
  README explicitly flags multi-reviewer as "not yet wired up."
- **Retire:** Flask app, the `reit-review` systemd unit, the `deploy-review.yml` GH Action,
  and the VPS. (Keep `scripts/review/` until cutover is verified, then archive it.)

```
Browser ──> Vercel (Next.js RSC + Server Actions)
                 │  read/write (Supabase JS client, RLS)
                 ▼
            Supabase Postgres  ── sgx_reit_* (data) + reit_report / *_verdict / *_edit (review)
                 │  signed URL
                 ▼
            Cloudflare R2  ── <stem>.pdf   (iframe src=…#page=N+offset)
```

## 3. Postgres schema (mirrors schema/models.py — DDL sketch, refine at build)
Nested/list fields → `jsonb`; scalars → typed columns. One canonical row-PK per table so
review verdicts can reference any record.

```sql
-- one row per trust
create table sgx_reit_profile (
  symbol text primary key,
  sub_sector text,
  management jsonb default '[]',          -- [{role, company_name}]
  income_model text,
  source_page int
);

-- one row per (symbol, financial_year)
create table sgx_reit_performance (
  id uuid primary key default gen_random_uuid(),
  symbol text not null, financial_year int not null,
  portfolio_value numeric, properties_location text,
  gross_revenue numeric, net_property_income numeric, net_distributable_income numeric,
  dpu numeric, distribution_record jsonb, number_of_unitholders int,
  aggregate_leverage numeric, interest_coverage_ratio numeric, cost_of_debt numeric,
  weighted_avg_debt_maturity numeric, nav_per_unit numeric, wale numeric,
  portfolio_occupancy numeric, currency text, date date,
  flags jsonb default '[]', source_page int,
  unique (symbol, financial_year)
);

-- one row per (symbol, property, financial_year)
create table sgx_reit_property (
  id uuid primary key default gen_random_uuid(),
  symbol text not null, financial_year int not null, property_name text not null,
  country text, category text, category_raw text, address text, ownership numeric,
  market_valuation numeric, valuation_date date, currency text,
  net_property_income numeric, gross_revenue numeric, npi_pct numeric, occupancy_rate numeric,
  major_tenants jsonb default '[]',
  gla numeric, nla numeric, gfa numeric,
  land_tenure text, effective_date date, lease_term_years numeric, lease_expiry_date date,
  tenure_raw text, status text default 'active',
  flags jsonb default '[]', source_page int,
  unique (symbol, financial_year, property_name)
);

create table sgx_reit_top_tenant (
  id uuid primary key default gen_random_uuid(),
  symbol text not null, financial_year int not null, rank int not null,
  client_name text, industry text, revenue_pct numeric, pct_basis text, source_page int,
  unique (symbol, financial_year, rank)
);

create table sgx_reit_trade_mix (
  id uuid primary key default gen_random_uuid(),
  symbol text not null, financial_year int not null,
  category text not null, category_raw text, pct numeric, pct_basis text, source_page int
);

-- one row per (symbol, financial_year); three prod-1:1 blobs + our line_items
create table sgx_reit_financial (
  id uuid primary key default gen_random_uuid(),
  symbol text not null, financial_year int not null, currency text,
  income_stmt_metrics jsonb, balance_sheet_metrics jsonb,
  cash_flow_metrics jsonb, employee_breakdown jsonb,
  line_items jsonb default '[]', source_page int,
  unique (symbol, financial_year)
);
```

Review layer (replaces `reviews/<stem>.json`):
```sql
create table reit_report (              -- one per (symbol, FY) = one cockpit unit
  id uuid primary key default gen_random_uuid(),
  symbol text not null, financial_year int not null,
  pdf_r2_key text,                      -- e.g. '01_XZL.SI_..._FY2025.pdf'
  page_offset int default 0,            -- printed→physical PDF page drift
  unique (symbol, financial_year)
);
create table reit_record_verdict (      -- one per reviewed record
  id uuid primary key default gen_random_uuid(),
  report_id uuid references reit_report(id),
  table_name text not null,             -- 'sgx_reit_property' | 'sgx_reit_performance' | …
  record_pk text not null,              -- the row id (or 'symbol' for profile)
  verdict text check (verdict in ('correct','false','unsure')),
  note text, reviewer uuid references auth.users(id),
  updated_at timestamptz default now(),
  unique (report_id, table_name, record_pk, reviewer)
);
create table reit_field_edit (          -- suggested correction per field (source untouched)
  id uuid primary key default gen_random_uuid(),
  report_id uuid references reit_report(id),
  table_name text not null, record_pk text not null, field_name text not null,
  suggested_value jsonb, reviewer uuid references auth.users(id),
  updated_at timestamptz default now(),
  unique (report_id, table_name, record_pk, field_name, reviewer)
);
```
RLS: `sgx_reit_*` read-only to authed reviewers; verdict/edit rows writable only by their
`reviewer = auth.uid()`. Suggested corrections still **never touch** the `sgx_reit_*` source
— same guarantee as today, now enforced by table separation + RLS.

## 4. Loader: extracted/ → Supabase  (`scripts/load_supabase.py`)
- Walk `extracted/<SYM>.SI_FY<YYYY>/`, validate each file with the existing
  `schema/models.py` Pydantic models (reuse the gate's validation), then upsert into the
  6 tables (`on conflict … do update`, keyed by the `unique` constraints above).
- Nested/list fields → dump to jsonb verbatim. `_notes.json` and
  `property_transactions.json` aren't in the 6-table schema — load `_notes` into a small
  `reit_notes` jsonb table (or skip for v1); decide `property_transactions` placement
  (likely a `reit_property_transaction` table, or fold into property where status=divested).
- Idempotent: re-runnable after each extraction batch. This is also the **endgame DB load**.
- Connect via Supabase service-role key (server-side only) or `psql`/`supabase-py`.

## 5. PDF migration: git → R2  (`scripts/upload_pdfs_r2.py` + history scrub)
1. Upload all `annual_reports/*.pdf` to an R2 bucket (key = filename). Set `pdf_r2_key` on
   each `reit_report` row.
2. Stop tracking PDFs in git: add `annual_reports/*.pdf` to `.gitignore`; `git rm --cached`.
3. **Shrink history** (the 1.1 GB): `git filter-repo --path-glob 'annual_reports/*.pdf' --invert-paths`
   (or BFG). This rewrites history → force-push + everyone re-clones once. ONE-TIME, coordinate
   it. Keep a full local/backup copy of the PDFs first.
4. Frontend fetches a short-lived **signed URL** from R2 (or a public bucket if acceptable)
   and renders `<iframe src="{url}#page={source_page + page_offset}">`.
   - Keep the **page-offset** mechanism (printed vs physical page drift) — now stored in
     `reit_report.page_offset`, editable from the top bar like today.

## 6. Next.js app structure (App Router)
```
app/
  (auth)/login/              magic-link sign-in (Supabase Auth)
  reports/page.tsx           list of (symbol, FY) with review progress %
  reports/[symbol]/[fy]/page.tsx   the cockpit:
      ├─ <PdfPane/>          iframe to R2 signed URL, #page jump, offset control
      └─ <RecordList/>       8 sections flattened; per-record ✓/✗/? + note + field edits
  api / actions:
      getReport()            RSC: join the 6 tables for (symbol,FY) → flattened records
      setVerdict()           Server Action → upsert reit_record_verdict
      setFieldEdit()         Server Action → upsert reit_field_edit
      setPageOffset()        Server Action → update reit_report
lib/supabase/ (server + browser clients), lib/flatten.ts (rows → reviewable cards)
```
- Match today's UX: PDF left, records right, `📄 p.N` jump, ✓/✗/? verdicts, per-field
  suggested correction with the `✎ N` badge, autosave. Add: real auth, per-reviewer
  verdicts, a portfolio-wide progress dashboard, instant writes (no reload).
- PDF rendering: native iframe `#page=` is simplest and matches current behaviour
  (Chrome/Edge). If cross-browser is needed later, swap to `react-pdf` / `pdf.js`.

## 7. Phasing (suggested order; each independently shippable)
1. **R2 + history scrub** — biggest speed win; unblocks everything. (one-time, coordinate)
2. **Supabase schema + loader** — `sgx_reit_*` live; verify counts vs `extracted/`. (= DB load endgame)
3. **Next.js read-only cockpit** — list + PDF pane + record view from Postgres. Parity check
   vs the Flask app on a few reports.
4. **Auth + write path** — verdicts/edits/offset as Server Actions + RLS; migrate any existing
   `reviews/*.json` verdicts into the tables.
5. **Cutover** — point reviewers at Vercel; retire Flask unit + `deploy-review.yml` + VPS.

## 8. Decisions — CONFIRMED 2026-06-19
- **R2 access: signed-URL only** (private bucket). Frontend mints a short-lived signed URL
  per PDF view; no public bucket.
- **`property_transactions.json` + `_notes.json`: own tables** — add `reit_property_transaction`
  and `reit_notes` (jsonb) to the loader + schema (not folded into property, not deferred).
- **History rewrite: YES — full `git filter-repo` + `git push --force`.** The user is the only
  one with a git clone; proofread reviewers use the web cockpit (no repo access), so the
  force-push is non-disruptive. Back up the 1.3 GB of PDFs first, then rewrite → `.git` drops to
  a few MB. (One-time; user re-clones once.)
- **Auth: email magic-link (Supabase Auth), multiple reviewers** — verdicts/edits are
  per-reviewer (`reviewer = auth.uid()`).
- **PDF inventory:** `reit_report` becomes the runtime inventory (holds `pdf_r2_key` +
  `page_offset`); `reconcile.py`/`_manifest.csv` stays as the *acquisition* tracker.
  (DONE 2026-06-19: `reconcile.py` NOT_EXIST set updated — the 6 manually-sourced ARs removed;
  remaining FY2025 gaps = 25 Landmark / 30 NTT DC / 38 UI Boustead.)

## 9. Still to resolve later (not blocking)
- Where do `reit_notes` rows attach (per report, or per record)? Decide when wiring the loader.
- Migrate any existing `reviews/*.json` verdicts into `reit_record_verdict`/`reit_field_edit`,
  or start verdicts fresh in the new app?
