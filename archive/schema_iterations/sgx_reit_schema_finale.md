# `sgx_reit_*` schema — FINAL (post-meeting, Jun 12 2026)

**6 tables + 1 materialized view.** Keyed on `symbol` (properties keep an integer `id`).
Market cap, price/volume, shares, and standard financial statements are never stored —
fetched from `sgx_companies` / `sgx_daily_data` / `sgx_company_report`.

All computed metrics (yield, P/NAV, standardized NPI, land lease remaining) live in the
API layer as versioned formulas — never as columns.

**Source legend (per field):**

- `src: supabase` — pulled/joined from existing Supabase tables (`sgx_companies`, `sgx_daily_data`, `sgx_company_report`); never re-stored unless tagged otherwise
- `src: AR` — extracted from the annual report (pipeline)
- `src: manual` — manually maintained / classified by us
- `src: hybrid` — extracted, then manually verified or backfilled

---

## 1. sgx_reit_profile

REIT-specific columns only. Everything generic (name, address, listing info, shares,
market cap) stays in `sgx_companies` and is **joined, not copied** — and only **selected
columns** of `sgx_companies` are exposed through the MV, not the whole table.

```sql
create table sgx_reit_profile (
  symbol           text primary key references sgx_companies(symbol),  -- src: supabase
  sub_sector       text,    -- src: manual — dedicated REIT sub-sector list (~7 values):
                            -- Retail | Office | Industrial | Hospitality | Healthcare |
                            -- Data Centre | Diversified
                            -- ⚠ open check: confirm whether sgx_companies.category matches
                            -- this list; if it differs, this REIT-specific value wins
  manager          jsonb    -- src: AR / hybrid — the REIT manager entity
                            -- (e.g. 'CapitaLand Integrated Commercial Trust Management
                            -- Limited'); moved here from the dropped management table
);
```

Parked (not in this iteration): `income_model`, other management roles
(property manager / trustee / sponsor / operator), transaction history.

## 2. sgx_reit_property

One row per (symbol, property, fiscal_year). A property sold to another trust appears
under the buyer's symbol the following year.

**Valuation rule (meeting decision):** `market_valuation` is the figure from the
**audited financial statements** (audited Portfolio Statement / investment-property
note), and `valuation_date` follows the financial-statement valuation date. The agreed
purchase price or agreed JV valuation printed on property marketing pages is ignored.

```sql
create table sgx_reit_property (
  id                  serial primary key,
  symbol              text references sgx_reit_profile(symbol),  -- src: AR
  fiscal_year         smallint,   -- src: AR
  country             text,       -- src: AR
  category            text,       -- src: AR
  property_name       text,       -- src: AR
  address             text,       -- src: AR
  ownership           numeric,    -- src: AR — % stake (kept per meeting)
  value_basis         text default 'consolidated'
                      check (value_basis in
                        ('consolidated','joint_venture_100pct','effective_interest')),
                                  -- src: AR — which basis the audited figure is stated at
  market_valuation    numeric,    -- src: AR — audited FS valuation ONLY (see rule above)
  valuation_date      date,       -- src: AR — the FS valuation date, not page dates
  currency            text,       -- src: AR
  net_property_income numeric,    -- src: AR — as-disclosed only, never computed
  gross_revenue       numeric,    -- src: AR
  occupancy_rate      numeric,    -- src: AR
  trade_mix           jsonb,      -- src: AR — property-level set, sparse (few trusts
                                  -- disclose it); REIT-level mix lives in its own table
  major_tenant        text,       -- src: AR
  gla                 numeric,    -- src: AR
  nla                 numeric,    -- src: AR
  land_tenure         text,       -- src: AR — Freehold | Leasehold
  effective_date      date,       -- src: AR — land-lease start
  lease_term_years    numeric,    -- src: AR — parsed from '64/99' → 99
  lease_expiry_date   date,       -- src: AR — when disclosed
  tenure_raw          text,       -- src: AR — verbatim disclosure (audit trail)
  status              text default 'active',  -- src: hybrid — active | divested |
                                              -- held_for_sale
  source_page         int,        -- provenance
  unique (symbol, property_name, fiscal_year)
);
```

No stored remaining-lease column — computed from dates at query time.
No purchase price / transaction columns — dropped per meeting.

## 3. sgx_reit_performance

One row per (symbol, fiscal_year). Structure follows the existing SGX manual-input /
DB convention **where the same field already exists there** — REIT-specific fields that
the manual-input structure lacks (notably `net_distributable_income` and
`distribution_record`) are added here.

> ⚠ open check: diff this column list against the actual `SGX manual input` table and
> rename columns to match its conventions before the migration is run.

```sql
create table sgx_reit_performance (
  symbol                   text references sgx_reit_profile(symbol),  -- src: AR
  fiscal_year              smallint,  -- src: AR
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
  source_report            text,      -- provenance
  source_page              int,       -- provenance
  primary key (symbol, fiscal_year)
);
-- market_cap / price / standard financials: src: supabase — fetched, never stored here
```

## 4. sgx_reit_top_tenant

```sql
create table sgx_reit_top_tenant (
  symbol         text references sgx_reit_profile(symbol),  -- src: AR
  fiscal_year    smallint,    -- src: AR
  rank           smallint,    -- src: AR
  tenant_name    text,        -- src: AR — null when anonymised (rank + % still data)
  trade_sector   text,        -- src: AR
  gri_percentage numeric,     -- src: AR
  pct_basis      text,        -- src: AR — gri | gri_excl_gto | gross_revenue |
                              -- rental_income | headline_rent | cash_rental_income |
                              -- nla | outlet_sales
  source_page    int,         -- provenance
  primary key (symbol, fiscal_year, rank)
);
```

## 5. sgx_reit_trade_mix

**REIT-level data from the annual report, as disclosed.** Per the meeting: do NOT
derive this by aggregating property-level data — the disclosed percentages may be
based on valuation, rental revenue, tenant count, NLA, etc., so a property roll-up is
not comparable. (The old `is_derived` flag is removed.)

```sql
create table sgx_reit_trade_mix (
  symbol      text references sgx_reit_profile(symbol),  -- src: AR
  fiscal_year smallint,  -- src: AR
  category    text,      -- src: AR
  pct         numeric,   -- src: AR
  pct_basis   text,      -- src: AR — the denominator the trust used (mandatory for
                         -- cross-REIT comparison)
  source_page int,       -- provenance
  primary key (symbol, fiscal_year, category)
);
```

## 6. sgx_reit_financial  *(renamed from `income_component`)*

Raw audited revenue/expense/adjustment note lines — the financial breakdown that feeds
the standardized formulas (standardized NPI, GRI-only revenue, cost ratio) computed in
the API layer.

```sql
create table sgx_reit_financial (
  symbol      text references sgx_reit_profile(symbol),  -- src: AR
  fiscal_year smallint,  -- src: AR
  statement   text check (statement in ('revenue','expense','adjustment')),  -- src: AR
  component   text,      -- src: AR — canonical key (base_rental, turnover_rent,
                         -- recoveries, property_tax, utilities, staff, loss_allowance...)
  amount      numeric,   -- src: AR — audited note line amount
  currency    text,      -- src: AR
  label_raw   text,      -- src: AR — exact audited note line (audit trail)
  source_page int,       -- provenance
  primary key (symbol, fiscal_year, statement, component)
);
```

## mv_sgx_reit

The single queryable surface: **selected** `sgx_companies` columns (not the whole
table) + REIT enrichment.

```sql
create materialized view mv_sgx_reit as
select c.symbol, c.name, c.sector,        -- selected sgx_companies columns only;
                                          -- extend deliberately, column by column
       p.sub_sector, p.manager,
       perf.fiscal_year, perf.portfolio_value, perf.net_property_income,
       perf.dpu, perf.net_distributable_income
from sgx_companies c
join sgx_reit_profile p using (symbol)
left join sgx_reit_performance perf using (symbol);
-- refresh after each extraction run
```

---

## Indexes

Primary keys above already index the main lookup paths (`symbol`, `(symbol,
fiscal_year)`, `(symbol, fiscal_year, rank)`, …). These cover the remaining query
patterns:

```sql
-- property: per-REIT-per-year portfolio pulls, plus cross-REIT screens
create index idx_reit_property_symbol_fy on sgx_reit_property (symbol, fiscal_year);
create index idx_reit_property_country   on sgx_reit_property (country);
create index idx_reit_property_category  on sgx_reit_property (category);
create index idx_reit_property_fy        on sgx_reit_property (fiscal_year);

-- performance: cross-REIT comparisons within a year
create index idx_reit_performance_fy on sgx_reit_performance (fiscal_year);

-- top tenant: 'where is DBS/Amazon a tenant' style lookups
create index idx_reit_top_tenant_name on sgx_reit_top_tenant (tenant_name);

-- trade mix: category screens across REITs
create index idx_reit_trade_mix_category on sgx_reit_trade_mix (category, fiscal_year);

-- financial: component screens across REITs ('utilities cost everywhere')
create index idx_reit_financial_component on sgx_reit_financial (component, fiscal_year);

-- profile: sub-sector filter (small table, but the most common WHERE clause)
create index idx_reit_profile_sub_sector on sgx_reit_profile (sub_sector);

-- MV: unique index enables REFRESH MATERIALIZED VIEW CONCURRENTLY
create unique index idx_mv_sgx_reit on mv_sgx_reit (symbol, fiscal_year);
```

---

## Dropped at the final meeting

- **`sgx_reit_property_transaction`** — transaction/corporate layer out of scope;
  agreed purchase prices and JV deal valuations from property pages are ignored for now.
- **`sgx_reit_management`** — the REIT manager is one `manager` column on the profile;
  the other roles (property manager, trustee, sponsor, operator, master lessee) are
  parked until needed.
- **`income_model`** on the profile — parked per earlier review.
- **`is_derived` trade-mix roll-up** — trade mix is captured as disclosed, REIT-level only.

## Open checks before migration

1. **Sub-sector taxonomy** — compare `sgx_companies` category values for the 39 trusts
   against the ~7-value REIT sub-sector list; if they differ, populate
   `sgx_reit_profile.sub_sector` from the REIT-specific list.
2. **Performance ↔ SGX manual input** — diff `sgx_reit_performance` columns against the
   existing manual-input/DB structure; reuse its column names where the field already
   exists, keep the REIT-specific adds (`net_distributable_income`,
   `distribution_record`).
3. **`gross_revenue` duplication** — confirm whether performance-level gross revenue
   equals `sgx_company_report` revenue; if yes, fetch instead of store.
4. **Extraction cross-check** — compare pipeline output against existing/manual data to
   decide fully-automated vs hybrid collection (target: ~10 extraction results to
   Evelyn by Mon Jun 15 2026).
