# FE data contract — Next.js cockpit ↔ Supabase + R2

Backend is **live**: schema applied, all 30 FY2025 reports loaded, PDFs in R2 bucket `reits-ar`.
This is everything the Next.js app needs. Source of truth for shapes: `schema/models.py` +
`db/schema.sql`.

## 1. Environment variables (FE)
```
NEXT_PUBLIC_SUPABASE_URL=https://<project-ref>.supabase.co        # from Supabase dashboard
NEXT_PUBLIC_SUPABASE_ANON_KEY=<SUPABASE_PUBLISHABLE_KEY>          # the publishable key (already in .env)
SUPABASE_SERVICE_KEY=<SUPABASE_SECRET_KEY>                        # server-only (never NEXT_PUBLIC_)
# R2 — for presigned PDF URLs (server-side only):
S3_ENDPOINT=https://<account_id>.r2.cloudflarestorage.com   # already created
R2_BUCKET=reits-ar
R2_ACCESS_KEY_ID=<32-char value>     # ⚠️ the SHORTER (32-char) key
R2_SECRET_ACCESS_KEY=<64-char value> # ⚠️ the LONGER (64-char) key — do NOT swap these
```
The Supabase **publishable/anon key** is safe in the browser (RLS enforces access). The
**service key** and **R2 secret** are server-only (Server Components / Server Actions / route
handlers) — never expose them to the client.

## 2. Tables (read with the anon key; RLS = authenticated can SELECT all data tables)
Data (one cockpit "report" = one `(symbol, financial_year)`):
- `sgx_reit_profile` (PK `symbol`) — `sub_sector`, `management` jsonb `[{role, company_name}]`, `income_model`, `source_page`
- `sgx_reit_performance` — the 7 KPIs + dpu/`distribution_record` jsonb + `flags` jsonb + `date`, `source_page`
- `sgx_reit_property` — one row per property; `market_valuation`, tenure, occupancy, `major_tenants` jsonb, `trade_mix` jsonb, `flags` jsonb, `source_page`
- `sgx_reit_top_tenant` — `rank`, `client_name`, `industry`, `revenue_pct`, `pct_basis`, `source_page`
- `sgx_reit_trade_mix` — `category`, `category_raw`, `pct`, `pct_basis`, `source_page`
- `sgx_reit_financial` — `income_stmt_metrics` / `balance_sheet_metrics` / `cash_flow_metrics` / `employee_breakdown` jsonb blobs + `line_items` jsonb + `source_page`
- `sgx_reit_property_transaction` — `transaction_type`, amounts, `raw` jsonb, `source_page`
- `sgx_reit_notes` — `notes` jsonb (columns_never_fillable / parsing_traps / inferred / reconciliation …)

Inventory + review:
- `reit_report` (PK `id`, unique `(symbol, financial_year)`) — `pdf_r2_key`, `page_offset`
- `reit_record_verdict` — `(report_id, table_name, record_pk, reviewer)` unique; `verdict ∈ correct|false|unsure`, `note`
- `reit_field_edit` — `(report_id, table_name, record_pk, field_name, reviewer)` unique; `suggested_value` jsonb

## 3. Reading one report (RSC)
```ts
// reports/[symbol]/[fy]/page.tsx  — parallel selects, all by (symbol, financial_year)
const [report, profile, perf, props, tenants, trade, fin, txn, notes] = await Promise.all([
  sb.from('reit_report').select('*').eq('symbol', symbol).eq('financial_year', fy).single(),
  sb.from('sgx_reit_profile').select('*').eq('symbol', symbol).single(),
  sb.from('sgx_reit_performance').select('*').eq('symbol', symbol).eq('financial_year', fy).single(),
  sb.from('sgx_reit_property').select('*').eq('symbol', symbol).eq('financial_year', fy).order('property_name'),
  sb.from('sgx_reit_top_tenant').select('*').eq('symbol', symbol).eq('financial_year', fy).order('rank'),
  sb.from('sgx_reit_trade_mix').select('*').eq('symbol', symbol).eq('financial_year', fy),
  sb.from('sgx_reit_financial').select('*').eq('symbol', symbol).eq('financial_year', fy).single(),
  sb.from('sgx_reit_property_transaction').select('*').eq('symbol', symbol).eq('financial_year', fy),
  sb.from('sgx_reit_notes').select('*').eq('symbol', symbol).eq('financial_year', fy).single(),
])
```
Reports list page: `select symbol, financial_year, pdf_r2_key from reit_report order by symbol`,
join verdict counts for a progress %.

## 4. Record identity (for verdicts / edits)
Every reviewable card needs a stable `(table_name, record_pk)`:
- list/financial/perf/txn/notes rows → `table_name` = the table, `record_pk` = the row's `id` (uuid).
- profile → `table_name='sgx_reit_profile'`, `record_pk = symbol` (it has no `id`).
A verdict/edit references `report_id` (from `reit_report.id`) + `table_name` + `record_pk`.
Flatten the 9 query results into one ordered list of cards, each carrying that identity + the
field set + each field's `source_page`.

## 5. Writes (Server Actions, service key OR anon-with-RLS; set `reviewer = auth.uid()`)
```ts
'use server'
// upsert a verdict
await sb.from('reit_record_verdict').upsert({
  report_id, table_name, record_pk, verdict, note, reviewer: user.id
}, { onConflict: 'report_id,table_name,record_pk,reviewer' })
// upsert a suggested field correction (source tables stay untouched)
await sb.from('reit_field_edit').upsert({
  report_id, table_name, record_pk, field_name, suggested_value, reviewer: user.id
}, { onConflict: 'report_id,table_name,record_pk,field_name,reviewer' })
// set page offset
await sb.from('reit_report').update({ page_offset }).eq('id', report_id)
```

## 6. PDF pane — presigned R2 URL (server-side; needs R2 S3 keys YOU create)
Create an **R2 API Token** (Cloudflare dash → R2 → *Manage R2 API Tokens* → Create, with
Object Read/Write on bucket `reits-ar`). It yields an **Access Key ID** + **Secret Access Key** —
put them in `R2_ACCESS_KEY_ID` / `R2_SECRET_ACCESS_KEY`. (The account API token already in `.env`
can upload but **cannot** presign — presigning needs these S3 keys.)
```ts
// lib/r2.ts (server only)
import { S3Client, GetObjectCommand } from '@aws-sdk/client-s3'
import { getSignedUrl } from '@aws-sdk/s3-request-presigner'
const r2 = new S3Client({
  region: 'auto',
  endpoint: process.env.S3_ENDPOINT!,   // https://<account_id>.r2.cloudflarestorage.com
  credentials: { accessKeyId: process.env.R2_ACCESS_KEY_ID!, secretAccessKey: process.env.R2_SECRET_ACCESS_KEY! },
})
export const pdfUrl = (key: string) =>
  getSignedUrl(r2, new GetObjectCommand({ Bucket: process.env.R2_BUCKET, Key: key }), { expiresIn: 3600 })
```
Render: `<iframe src={`${signedUrl}#page=${source_page + report.page_offset}`} />` (Chrome/Edge
native PDF viewer honours `#page=`). `page_offset` corrects printed-vs-physical drift — keep the
top-bar control that writes `reit_report.page_offset`.

## 7. Auth
Supabase Auth, email magic-link. Gate the app behind a session; pass `auth.uid()` as `reviewer`
on every write. RLS already restricts verdict/edit writes to `reviewer = auth.uid()` and data
tables to SELECT-only for authenticated users.

## 8. Re-loading data after new extractions
`python scripts/db/load_supabase.py [DIR…]` re-upserts (idempotent); `python scripts/db/upload_r2.py`
ensures PDFs. The FE needs no redeploy — it reads live.
```
```
