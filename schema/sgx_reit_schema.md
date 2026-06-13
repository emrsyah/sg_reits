# `sgx_reit_*` schema

**6 tables + 1 materialized view.** Keyed on `symbol` (properties keep an integer `id`).
Market cap, price/volume, shares, and standard financial statements are never stored —
fetched from `sgx_companies` / `sgx_daily_data` / `sgx_company_report`.

All computed metrics (yield, P/NAV, standardized NPI, land lease remaining) live in the
API layer as versioned formulas — never as columns.

**Decision**

| # | Decision | Where it lands |
|---|---|---|
| 1 | Only 6 REIT tables shipped | `sgx_reit_property_transaction` dropped (corporate/transaction layer out of scope for now) |
| 2 | REIT manager is part of the profile, not a separate table | `sgx_reit_management` dropped; `management` **jsonb** column on `sgx_reit_profile` (manager entities + roles; distinct from prod's people-level `sgx_companies.management`; normalize later only if cross-REIT manager/fee screening becomes a feature) |
| 3 | `income_component` name unclear — it holds the financial breakdown, not just income | renamed **`sgx_reit_financial`** |
| 4 | Trade mix is REIT-level data from the annual report; do NOT assume it aggregates from property level (denominators differ: valuation / rental revenue / tenant count) | `is_derived` flag removed from `sgx_reit_trade_mix`; disclosed figures only |
| 5 | Property valuation = market valuation from the **audited financial statements**; ignore agreed purchase price / agreed JV valuation from property pages | note on `market_valuation` + `valuation_date` |
| 6 | Every table documents its data source per field | `src:` tags below |
| 7 | Indexes added for query speed | §Indexes |

**Source legend (per field):**

- `src: supabase` — pulled/joined from existing Supabase tables (`sgx_companies`, `sgx_daily_data`, `sgx_company_report`); never re-stored unless tagged otherwise
- `src: AR` — extracted from the annual report (pipeline)

Only these two for now. Whether any field needs manual collection (or extracted +
manually verified) is decided after the extraction cross-check vs existing data.

---

## 1. sgx_reit_profile

REIT-specific columns only. Everything generic (name, address, listing info, shares,
market cap) stays in `sgx_companies` and is **joined, not copied** — and only **selected
columns** of `sgx_companies` are exposed through the MV, not the whole table.

```sql
create table sgx_reit_profile (
  symbol           text primary key references sgx_companies(symbol),  -- src: supabase
  sub_sector       text,    -- src: AR — classified into the dedicated REIT sub-sector
                            -- list (~7 values):
                            -- Retail | Office | Industrial | Hospitality | Healthcare |
                            -- Data Centre | Diversified
                            -- sgx_companies.sub_sector confirmed DIFFERENT (e.g. 'Hotel
                            -- & Motel') — this REIT-specific value wins, sourced from AR.
                            -- cheap to verify later: one value per trust, eyeball-able
  management       jsonb    -- src: AR — replaces the dropped management table;
                            -- holds the manager ENTITIES (companies + roles):
                            -- [{"role": "reit_manager",
                            --   "company_name": "CapitaLand Integrated Commercial
                            --                    Trust Management Limited"}, ...]
                            -- roles: reit_manager | property_manager | trustee |
                            --        sponsor | operator | master_lessee
                            -- NOT the same as sgx_companies.management, which holds
                            -- PEOPLE ({age, name, position, start_date}) — the two are
                            -- complementary; people-level data stays in prod.
                            -- normalize into a table later only if cross-REIT
                            -- manager/fee screening becomes a feature
);
```

Parked (not in this iteration): `income_model`, transaction history.

## 2. sgx_reit_property

One row per (symbol, property, financial_year). A property sold to another trust appears
under the buyer's symbol the following year.

**Valuation rule (meeting decision):** `market_valuation` is the figure from the
**audited financial statements** (audited Portfolio Statement / investment-property
note), and `valuation_date` follows the financial-statement valuation date. The agreed
purchase price or agreed JV valuation printed on property marketing pages is ignored.

```sql
create table sgx_reit_property (
  id                  serial primary key,
  symbol              text references sgx_reit_profile(symbol),  -- src: AR
  financial_year         smallint,   -- src: AR
  country             text,       -- src: AR
  category            text,       -- src: AR
  property_name       text,       -- src: AR
  address             text,       -- src: AR
  ownership           numeric,    -- src: AR — % stake (kept per meeting)
  market_valuation    numeric,    -- src: AR — audited FS valuation ONLY (see rule above);
                                  -- convention: recorded at 100% of the property as the
                                  -- audited FS prints it; effective-interest value =
                                  -- market_valuation × ownership, computed in API layer
  valuation_date      date,       -- src: AR — the FS valuation date, not page dates
  currency            text,       -- src: AR
  net_property_income numeric,    -- src: AR — as-disclosed only, never computed
  gross_revenue       numeric,    -- src: AR
  occupancy_rate      numeric,    -- src: AR
  trade_mix           jsonb,      -- src: AR — property-level set, sparse (few trusts
                                  -- disclose it); REIT-level mix lives in its own table;
                                  -- keys use the same canonical 19-value category list
  major_tenant        text,       -- src: AR
  gla                 numeric,    -- src: AR
  nla                 numeric,    -- src: AR
  land_tenure         text,       -- src: AR — Freehold | Leasehold
  effective_date      date,       -- src: AR — land-lease start
  lease_term_years    numeric,    -- src: AR — parsed from '64/99' → 99
  lease_expiry_date   date,       -- src: AR — when disclosed
  tenure_raw          text,       -- src: AR — verbatim disclosure (audit trail)
  status              text default 'active',  -- src: AR — active | divested |
                                              -- held_for_sale
  source_page         int,        -- provenance
  unique (symbol, property_name, financial_year)
);
```

No stored remaining-lease column — computed from dates at query time.
No purchase price / transaction columns — dropped per meeting.

## 3. sgx_reit_performance

One row per (symbol, financial_year). Conventions aligned with `sgx_manual_input`
(verified against its actual structure): `financial_year smallint` as the year key,
`date` for the FY-end date, `source_url` for the source report link. REIT-specific
fields the manual-input structure lacks (`net_distributable_income`,
`distribution_record`, `dpu`, `portfolio_value`) are added here.

Generic financials (revenue/EBIT/balance-sheet/cash-flow) are NOT duplicated — they
already live in `sgx_manual_input.income_stmt_metrics` / `balance_sheet_metrics` /
`cash_flow_metrics` jsonb per (symbol, financial_year).

```sql
create table sgx_reit_performance (
  symbol                   text references sgx_reit_profile(symbol),  -- src: AR
  financial_year              smallint,  -- src: AR
  portfolio_value          numeric,   -- src: AR — headlined portfolio valuation incl. JV
                                      -- proportionate interests (pinned definition)
  properties_location      text,      -- src: AR
  gross_revenue            numeric,   -- src: AR — verify vs sgx_company_report revenue;
                                      -- if identical, drop and fetch instead
  net_property_income      numeric,   -- src: AR — as reported
  net_distributable_income numeric,   -- src: AR — REIT-specific add (meeting)
  dpu                      numeric,   -- src: AR — cents
  distribution_record      jsonb,     -- src: AR — [{period, dpu, ex_date, pay_date}]
                                      -- REIT-specific add (meeting)
  number_of_unitholders    int,       -- src: AR
  currency                 text,      -- src: AR
  date                     date,      -- src: AR — FY-end date (manual-input convention)
  source_url               text,      -- provenance (manual-input convention)
  source_page              int,       -- provenance
  primary key (symbol, financial_year)
);
-- market_cap / price / standard financials: src: supabase — fetched from sgx_companies /
-- sgx_manual_input (income_stmt/balance_sheet/cash_flow_metrics jsonb), never stored here
```

## 4. sgx_reit_top_tenant

```sql
create table sgx_reit_top_tenant (
  symbol         text references sgx_reit_profile(symbol),  -- src: AR
  financial_year    smallint,    -- src: AR
  rank           smallint,    -- src: AR
  tenant_name    text,        -- src: AR — null when anonymised (rank + % still data)
  trade_sector   text,        -- src: AR — same canonical 19-value list as
                              -- sgx_reit_trade_mix.category (one taxonomy everywhere)
  gri_percentage numeric,     -- src: AR
  pct_basis      text,        -- src: AR — gri | gri_excl_gto | gross_revenue |
                              -- rental_income | headline_rent | cash_rental_income |
                              -- nla | outlet_sales
  source_page    int,         -- provenance
  primary key (symbol, financial_year, rank)
);
```

## 5. sgx_reit_trade_mix

**REIT-level data from the annual report, as disclosed.** Per the meeting: do NOT
derive this by aggregating property-level data — the disclosed percentages may be
based on valuation, rental revenue, tenant count, NLA, etc., so a property roll-up is
not comparable. (The old `is_derived` flag is removed.)

**Category enum** — Eve's baseline 14, plus 5 additions earned by a sweep of all 22
parsed reports (each addition is >5% of at least one trust's mix and has no clean home
in the baseline). The disclosed label is kept verbatim in `category_raw`; the
extraction pipeline maps it to the canonical `category` via an alias dictionary.

```sql
create table sgx_reit_trade_mix (
  symbol         text references sgx_reit_profile(symbol),  -- src: AR
  financial_year smallint,  -- src: AR
  category       text check (category in (
                   -- Eve's baseline 14
                   'Food & Beverages',
                   'Banking, Insurance & Financial Services',
                   'Beauty & Health',
                   'Fashion & Accessories',
                   'Hospitality & Leisure',
                   'Real Estate & Property Services',
                   'IT & Telecommunications',
                   'Other Office Trades',
                   'Other Retail Trades',
                   'Logistics & Supply Chain Management',
                   'Manufacturing',
                   'Government Related',
                   'Mining & Resources',
                   'Departmental Store/Supermarket',
                   -- additions (22-report evidence)
                   'Healthcare, Pharmaceuticals & Life Sciences',
                   'Professional Services',
                   'Construction & Engineering',
                   'Energy & Utilities',
                   'Other Industrial Trades'
                 )),       -- src: AR — mapped to canonical via alias dictionary
  category_raw   text,     -- src: AR — verbatim disclosed label (audit trail; allows
                           -- remapping without re-extraction)
  pct            numeric,  -- src: AR
  pct_basis      text,     -- src: AR — the denominator the trust used (mandatory for
                           -- cross-REIT comparison)
  source_page    int,      -- provenance
  primary key (symbol, financial_year, category)
);
```

Why each addition (evidence from the parsed reports):

| Addition | Evidence | Why baseline can't hold it |
|---|---|---|
| Healthcare, Pharmaceuticals & Life Sciences | First REIT ~89% healthcare; KORE 'Medical and Healthcare' 8.5%; Suntec 'Pharmaceutical and Healthcare'; CLINT 'Healthcare & Pharmaceutical'; biomedical sciences (CLAR/CLCT science parks) | 'Beauty & Health' is a *retail* trade (salons, pharmacies) — hospital/pharma tenants are a different thing |
| Professional Services | KORE 22.6%; Manulife 'Legal' 15.3%; Suntec 'Consultancy/Services' 14.5%; Stoneweg 'Professional - Scientific' 9.4%; Keppel 'Legal' + 'Accounting and consultancy' | dominant sector in US/office trusts; burying 15–23% weights in 'Other Office Trades' destroys the signal |
| Construction & Engineering | Centurion ~79% (worker-accommodation tenants); CLAR 'Engineering' ~12%; CLCT 4.8%; MLT 'Materials, Construction & Engineering'; Stoneweg 'Construction' | no baseline category covers it at all |
| Energy & Utilities | Keppel 'Energy, natural resources, shipping and marine' 7.7%; Suntec 'Energy and Natural Resources'; Stoneweg 'Utility' | 'Mining & Resources' is extraction, not power/utilities; reports merge them under energy |
| Other Industrial Trades | MLT/DHLT/CLAR long tail: 3PL, chemicals, automobiles, document storage, commodities, e-commerce | baseline only has Office and Retail catch-alls — industrial/logistics trusts have nowhere to put their tail |

Mapping notes for the alias dictionary (synonyms, NOT new categories):
'TMT' / 'TAMI' / 'Information & Communications Technology' → IT & Telecommunications;
'F&B' / 'Food & Beverage' → Food & Beverages; 'Supermarket & Grocers' / 'Grocery &
Wholesale' → Departmental Store/Supermarket; 'Public Administration' / 'Government
agency' → Government Related; '3PL' / 'Transportation - Storage' → Logistics & Supply
Chain Management; retail sub-trades (Jewellery & Watches, Sports Apparel, Homeware,
Education, Leisure & Entertainment...) → Other Retail Trades unless a baseline
category fits.

Structurally out of scope (leave the table EMPTY for these, don't force-fit):
hospitality/accommodation trusts (CLAS, FEHT, Centurion) disclose income by contract
type/geography, not trade sectors; data-centre trusts (KDC, Digital Core) disclose
customer types (hyperscaler/colocation). Those are different facts, not a trade mix —
the CLAS pilot extraction proved this by emitting contract types as 'categories'.

## 6. sgx_reit_financial  *(renamed from `income_component`)*

Raw audited revenue/expense/adjustment note lines — the financial breakdown that feeds
the standardized formulas (standardized NPI, GRI-only revenue, cost ratio) computed in
the API layer.

```sql
create table sgx_reit_financial (
  symbol      text references sgx_reit_profile(symbol),  -- src: AR
  financial_year smallint,  -- src: AR
  statement   text check (statement in ('revenue','expense','adjustment')),  -- src: AR
  component   text,      -- src: AR — canonical key (base_rental, turnover_rent,
                         -- recoveries, property_tax, utilities, staff, loss_allowance...)
  amount      numeric,   -- src: AR — audited note line amount
  currency    text,      -- src: AR
  label_raw   text,      -- src: AR — exact audited note line (audit trail)
  source_page int,       -- provenance
  primary key (symbol, financial_year, statement, component)
);
```

## mv_sgx_reit

The single queryable surface: **selected** `sgx_companies` columns (not the whole
table) + REIT enrichment.

```sql
create materialized view mv_sgx_reit as
select c.symbol, c.name, c.sector,        -- selected sgx_companies columns only;
                                          -- extend deliberately, column by column
       p.sub_sector, p.management,
       perf.financial_year, perf.portfolio_value, perf.net_property_income,
       perf.dpu, perf.net_distributable_income
from sgx_companies c
join sgx_reit_profile p using (symbol)
left join sgx_reit_performance perf using (symbol);
-- refresh after each extraction run
```

---

## Indexes

Primary keys above already index the main lookup paths (`symbol`, `(symbol,
financial_year)`, `(symbol, financial_year, rank)`, …). These cover the remaining query
patterns:

```sql
-- property: per-REIT-per-year portfolio pulls, plus cross-REIT screens
create index idx_reit_property_symbol_fy on sgx_reit_property (symbol, financial_year);
create index idx_reit_property_country   on sgx_reit_property (country);
create index idx_reit_property_category  on sgx_reit_property (category);
create index idx_reit_property_fy        on sgx_reit_property (financial_year);

-- performance: cross-REIT comparisons within a year
create index idx_reit_performance_fy on sgx_reit_performance (financial_year);

-- top tenant: 'where is DBS/Amazon a tenant' style lookups
create index idx_reit_top_tenant_name on sgx_reit_top_tenant (tenant_name);

-- trade mix: category screens across REITs
create index idx_reit_trade_mix_category on sgx_reit_trade_mix (category, financial_year);

-- financial: component screens across REITs ('utilities cost everywhere')
create index idx_reit_financial_component on sgx_reit_financial (component, financial_year);

-- profile: sub-sector filter (small table, but the most common WHERE clause)
create index idx_reit_profile_sub_sector on sgx_reit_profile (sub_sector);

-- MV: unique index enables REFRESH MATERIALIZED VIEW CONCURRENTLY
create unique index idx_mv_sgx_reit on mv_sgx_reit (symbol, financial_year);
```

---

## Dropped at the final meeting

- **`sgx_reit_property_transaction`** — transaction/corporate layer out of scope;
  agreed purchase prices and JV deal valuations from property pages are ignored for now.
- **`sgx_reit_management`** — folded into the profile as a `management` jsonb (all
  roles: REIT manager, property manager, trustee, sponsor, operator, master lessee);
  normalize later only if manager/fee screening becomes a feature.
- **`value_basis`** on property — existed to disambiguate the same property printed at
  100% vs effective stake (Gallileo: S$547.6m vs S$519.7m at 94.9%). Superseded by the
  audited-FS-only valuation rule + kept `ownership` (effective value is computable).
  If the extraction cross-check finds trusts whose audited statements print effective
  stake instead of 100%, revisit.
- **`income_model`** on the profile — parked per earlier review.
- **`is_derived` trade-mix roll-up** — trade mix is captured as disclosed, REIT-level only.

## Open checks before migration

1. ~~**Sub-sector taxonomy**~~ — RESOLVED: some of `sgx_companies` category uses a different
   taxonomy (e.g. 'Hotel & Motel'), so `sub_sector` is populated from AR extraction
   against the ~7-value REIT list. Verification is cheap (one value per trust) — spot-
   check after the extraction run.
2. ~~**Performance ↔ SGX manual input**~~ — RESOLVED: `sgx_manual_input` is one row per
   (symbol, financial_year) with jsonb metric blobs. Conventions adopted:
   `financial_year` (replacing our `fiscal_year` everywhere), `date` (FY-end),
   `source_url`. Generic financials stay in its jsonb blobs — not duplicated here.
3. **`gross_revenue` duplication** — evidence so far: CICT FY2024
   `income_stmt_metrics.total_revenue` = 1,586,329,000 = the AR's gross revenue, so the
   figure DOES already exist in `sgx_manual_input`. Kept for now because (a) manual
   input is manually maintained and our pipeline should not depend on it being filled,
   and (b) the AR figure is the reconciliation anchor for `sgx_reit_financial`
   (components must sum to it). Revisit after the cross-check.
4. **Extraction cross-check** — compare pipeline output against existing/manual data to
   decide fully-automated vs hybrid collection (target: ~10 extraction results to
   Evelyn by Mon Jun 15 2026). See mapping below.
5. ~~**`management` jsonb shape**~~ — RESOLVED: `sgx_companies.management` holds PEOPLE
   (directors/execs: {age, name, position, start_date}), a different concept from our
   manager ENTITIES — no shape to mirror; our [{role, company_name}] shape stands.
6. **Symbol format** — `sgx_companies` stores symbols WITHOUT the `.SI` suffix
   (`K71U`, `H13`) while `sgx_manual_input` uses `C38U.SI` WITH it. Our extraction
   output also uses `.SI`. The `sgx_reit_*` tables FK into `sgx_companies(symbol)`, so
   they must use the suffix-less format — normalize (`strip '.SI'`) at ingestion, and
   strip it when joining against `sgx_manual_input` for the cross-check.

## Cross-check mapping: `sgx_manual_input` ↔ `sgx_reit_*`

`sgx_manual_input.industry_breakdown` already holds manually-collected versions of our
REIT data — this is the ground truth to compare the ~10 extraction runs against:

| `sgx_manual_input` (jsonb path) | Cross-checks against | Notes |
|---|---|---|
| `industry_breakdown.top_10_gri%_customers` (industry, client_name, revenue_pct) | `sgx_reit_top_tenant` | their `revenue_pct` is a fraction (0.05), ours `gri_percentage` — pick one unit and stick to it |
| `industry_breakdown.gross_rental_income_by_sectors` ({category: fraction}) | `sgx_reit_trade_mix` | their categories = Eve's 14-value list |
| `industry_breakdown.property_portfolio_top_20` (name, country, category, valuation, gross_income, occupancy_rate, ownership_pct) | `sgx_reit_property` | top-20 only; full portfolio is our table's superset |
| `industry_breakdown.property_counts_by_country` | derivable from `sgx_reit_property` | count/sum per (country, category) |
| `sankey_component.links` + `income_stmt_metrics.revenue_breakdown` / `operating_expense_breakdown` | `sgx_reit_financial` | their categories ('Gross rental', 'Car park', 'Management fees'...) map to our canonical `component` keys |
| `income_stmt_metrics.total_revenue` | `sgx_reit_performance.gross_revenue` | reconciliation anchor |
