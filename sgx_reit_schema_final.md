# `sgx_reit_*` — final refined schema (v1.2)

> v1.2 (post-pilot): two changes earned by extraction evidence per §F — `value_basis` on
> property rows, and a pinned definition for `performance.portfolio_value`. Both came out
> of the 3-trust pilot + blind verification, where the only 2 disagreements in 73 sampled
> values were the report printing the same fact on two bases (Gallileo S$547.6m at 100%
> vs S$519.7m at CICT's 94.9% share; portfolio S$27,397.5m incl. JV proportionate vs
> S$25,601.6m balance-sheet investment properties).

> **Inputs, in order of authority:**
> 1. The colleague's `REITS db.xlsx` draft — the base shape.
> 2. The team discussion (Gerald + author, see §0) — decisions on dedup vs sectors DB,
>    keys, and sheet merges.
> 3. Our 20-report parsing exercise — used only as a *diff*: contradictions the reports
>    force, plus a few shallow pickups. Not a mandate (we don't yet know what's reliably
>    extractable); the deep v2/v3 docs stay parked as reference.
>
> **This schema is a starting point.** §F defines how columns earn their place: fill rate
> and agreement rate measured during extraction; drop/add decisions follow the data.

---

## 0. What the discussion settled (synthesized, not verbatim)

| # | Discussion point | Decision | Where it lands here |
|---|---|---|---|
| 1 | REIT profile duplicates `sgx_companies` | Don't widen `sgx_companies` (NULLs for non-REITs); make a **separate REIT table** holding only REIT-specific columns, and a **materialized view** combining it with what sectors DB already has | §D.1 slim profile + §D.9 MV |
| 2 | Market cap & financials live in `sgx_company_report` | Fetch, don't store | dropped from performance; `gross_revenue` kept *provisionally* — flagged to verify in the pilot whether `sgx_company_report` revenue is the same figure (§D.5 note) |
| 3 | `top_10` sheet duplicates the portfolio-performance top-10 column | One place only (the sheets were a manual-Excel fallback if AR scraping fails) | single `sgx_reit_top_tenant` table (§D.6) |
| 4 | `valuation_revenue` sheet duplicates `Property` | Same — manual fallback, not schema | not a table; valuation/revenue live on the property row |
| 5 | Portfolio Performance + REIT Performance | Merge into one | single `sgx_reit_performance` per (symbol, FY) (§D.5) |
| 6 | `id` vs `symbol` | **`symbol`**, like the other sectors tables; properties keep an integer `id` | all tables key on `symbol`; property keeps surrogate `id` |
| 7 | *(open question raised)* Properties can be put up for sale and bought by another REIT | Property↔REIT linkage is **not permanent**. Handled two ways: rows are per (symbol, fiscal_year) — a sold property simply appears under the buyer's symbol next year — and the purchase table becomes a **transaction** table that also records divestments | §D.3 + §D.4 |

## A. Where the parsed reports contradict the draft (minimal fixes only)

| # | Draft assumption | What 20 reports actually do | Minimal fix |
|---|---|---|---|
| 1 | No time axis (snapshot sheets) | Every figure is per fiscal year; FYE differs (Dec/Mar/Sep) | `fiscal_year` on every fact table |
| 2 | One purchase year/price per property | Acquisitions are phased (Rock Square 51%+49%; NEX 25.5%+24.5%) — her own JSON already models a *list* | `property_transaction` child table (normalizing her list; also answers discussion #7) |
| 3 | One `management_company` per REIT | Distinct roles: REIT manager, property manager(s) — CICT has 3 — operator, master lessee, trustee, sponsor | one `role` column on her Management Profile shape |
| 4 | Per-property `net_property_income` fillable | ~7 of 20 trusts disclose it; none disclose per-property expenses, so it can't be computed either | keep column, as-disclosed only, expect ~35% fill |
| 5 | Per-property `trade_mix` fillable | Only CICT & Sasseur disclose property-level mix; every trust publishes a REIT-level set | keep her property `trade_mix` jsonb; add REIT-level table; aggregate property→REIT where possible and reconcile |
| 6 | Percentages comparable across REITs | Different denominators per trust (GRI, gross revenue, cash rental income, NLA, % of outlet sales) | `pct_basis` column wherever a % is stored |
| 7 | `term_of_lease` like "64/99" is a number | It's the **land** lease (not a tenant lease), written as remaining/total strings, "30+30 years", or literally "Freehold" | verbatim `tenure_raw` + parsed term/dates; remaining term **computed, never stored** |
| 8 | Values implicitly SGD | KORE reports USD, Stoneweg EUR, Elite GBP, CLCT carries RMB | `currency` column on money-bearing tables |

*(The draft's market_cap/financials duplication is resolved by discussion #2 rather than listed here.)*

## B. Useful, not yet picked up — kept shallow

- **`valuation_date`** on property — reports distinguish "latest valuation date" from
  purchase/effective date; conflating them is a known trap.
- **`source_page`** on every fact table — one int; any number auditable back to its AR page.
- **`income_model`** on the profile — one nullable text column marking trusts where
  standard formulas don't apply (master-lease trusts have no occupancy; Sasseur's
  entrusted-management model has no NPI at all). Without it, standardized formulas
  silently produce garbage for ~5 of 39 trusts.
- **`sgx_reit_income_component`** (§D.8) — audited revenue/expense note lines; exists
  purely to serve the standardization mechanic. First candidate to simplify if the pilot
  shows the notes are too messy to extract reliably.

## C. The standardization mechanic (the brief, operationalized)

All computed metrics live in **our API layer as one versioned formula per metric** —
never stored, never trusting the report's own computed figure (they opt in/out of line
items; we don't):

| Computed by us | From | Why the printed figure isn't trusted |
|---|---|---|
| Land lease remaining | expiry or (effective_date + term) − today | printed "remaining" is stale the day after publication, and presentable favourably |
| Standardized NPI | gross revenue − Σ(our fixed expense set) from income components | each trust's "property expenses" contains different lines (utilities 35% of one trust's costs, ~0 for another) |
| Adjusted NPI growth | excluding straight-lining / incentive amortisation / one-offs | audited case: +3.0% reported vs +0.3% adjusted — gap purely accounting |
| GRI-only revenue | revenue − car park − recoveries − service charges | "gross revenue" can be ~30% pass-through reimbursements |
| Cost ratio, NPI margin | same components | comparable only with identical numerators |
| Distribution yield, P/NAV | our tables + prod price data | house convention already |
| REIT-level trade mix (derived) | Σ over property `trade_mix`, flagged `is_derived` | cross-check vs the disclosed set; mismatch = parser took the wrong table |

Parsing side: extraction targets the **audited Portfolio Statement** first (present in
20/20 reports); the scraper config carries the terminology rules to be walked through with
her (tenure / purchase vs effective date / manager roles — label→field map in
`reits_db_schema_from_draft.md` §3).

---

## D. The schema — 8 tables + 1 materialized view

### D.1 `sgx_reit_profile` — REIT-specific columns only *(discussion #1, #6)*

Name, address, shares, market cap, financial statements all stay in
`sgx_companies` / `sgx_company_report`. This table holds only what sectors DB doesn't:

```sql
create table sgx_reit_profile (
  symbol           text primary key references sgx_companies(symbol),
  reit_sub_sector  text,           -- Retail | Industrial | Hospitality | Diversified | ...
  income_model     text            -- nullable; pickup B (formula applicability)
);
```

(`management_company` from her sheet → §D.2, since it's several roles, not one.)

### D.2 `sgx_reit_management` *(her Management Profile + fix A3)*

```sql
create table sgx_reit_management (
  symbol       text references sgx_reit_profile(symbol),
  company_name text,
  ownership    numeric,
  role         text,               -- reit_manager | property_manager | operator |
                                   -- master_lessee | trustee | sponsor
  property_id  int,                -- null = portfolio-wide
  source_page  int
);
```

### D.3 `sgx_reit_property` *(her Property sheet + fixes A1, A4, A7, A8 + pickups)*

One row per (symbol, property, fiscal_year). Because rows are per year **under the
owning REIT's symbol**, a property sold to another trust (discussion #7) naturally
re-appears under the buyer's symbol the following year — no ownership gymnastics needed
in the identity model; the transaction table (§D.4) records the sale and the purchase.

```sql
create table sgx_reit_property (
  id                  serial primary key,        -- discussion #6: property keeps int id
  symbol              text references sgx_reit_profile(symbol),
  fiscal_year         smallint,                  -- fix A1
  country text, category text, property_name text, address text,
  ownership           numeric,                   -- % stake
  value_basis         text default 'consolidated'
                      check (value_basis in
                        ('consolidated','joint_venture_100pct','effective_interest')),
                      -- v1.2: which basis the money figures on THIS ROW are stated at.
                      -- JV properties (FCT NEX/Waterway, CICT ION) are disclosed at 100%
                      -- but equity-accounted — outside the consolidated revenue total;
                      -- without this flag Σ(property) double-counts. Blind verification
                      -- proof: Gallileo valuation printed BOTH as 547.6 (100%) and
                      -- 519.7 (94.9% share) — two correct numbers, one column, no basis
                      -- = guaranteed inconsistency.
  market_valuation    numeric,
  valuation_date      date,                      -- pickup B
  currency            text,                      -- fix A8
  net_property_income numeric,                   -- as-disclosed only (fix A4)
  gross_revenue       numeric,
  occupancy_rate      numeric,
  trade_mix           jsonb,                     -- her shape; property-level set
  major_tenant        text,
  gla numeric, nla numeric,
  land_tenure         text,                      -- Freehold | Leasehold
  effective_date      date,
  lease_term_years    numeric,                   -- parsed from '64/99' → 99
  lease_expiry_date   date,                      -- when disclosed
  tenure_raw          text,                      -- verbatim '64/99' / '30+30 years' (fix A7)
  status              text default 'active',     -- active | divested | held_for_sale
  source_page         int,
  unique (symbol, property_name, fiscal_year)
);
-- no land_lease_remaining column: computed (§C)
```

### D.4 `sgx_reit_property_transaction` *(fix A2 + discussion #7 — purchases AND sales)*

```sql
create table sgx_reit_property_transaction (
  property_id      int references sgx_reit_property(id),
  transaction_type text check (transaction_type in ('acquisition','divestment')),
  transaction_year smallint,                     -- her purchase_year granularity
  transaction_date date,                         -- when fully disclosed
  price            numeric, currency text,
  stake_pct        numeric,                      -- phased deals: 51% then 49%
  counterparty     text,                         -- buyer/seller when disclosed —
                                                 -- links a divestment here to an
                                                 -- acquisition under another symbol
  source_page      int
);
```

### D.5 `sgx_reit_performance` *(discussion #2 & #5: sheets merged, sectors-DB items dropped)*

```sql
create table sgx_reit_performance (
  symbol               text references sgx_reit_profile(symbol),
  fiscal_year          smallint,
  portfolio_value      numeric,   -- v1.2 PINNED DEFINITION: the headlined portfolio
                                  -- valuation INCLUDING proportionate JV interests (what
                                  -- every trust leads with, e.g. CICT S$27,397.5m). The
                                  -- balance-sheet investment-properties figure (CICT
                                  -- S$25,601.6m) is a different fact — fetch from
                                  -- sgx_company_report, never stored here.
  properties_location  text,
  gross_revenue        numeric,   -- PROVISIONAL: verify in pilot whether this equals
                                  -- sgx_company_report revenue for trusts; if yes → drop
                                  -- and fetch (discussion #2). Kept for now because the
                                  -- income-component reconciliation sums to this line.
  net_property_income  numeric,   -- as reported (their formula; ours is computed, §C)
  net_distributable_income numeric,
  dpu                  numeric,
  distribution_record  jsonb,     -- her shape: per-period dpu, ex/pay dates
  number_of_unitholders int,
  currency             text,
  source_report text, source_page int,
  primary key (symbol, fiscal_year)
);
-- market_cap, total_market_value, generic financials: fetched from sgx_daily_data /
-- sgx_company_report, never stored here (discussion #2).
```

### D.6 `sgx_reit_top_tenant` *(discussion #3: the single home for top-10)*

```sql
create table sgx_reit_top_tenant (
  symbol         text references sgx_reit_profile(symbol),
  fiscal_year    smallint,
  rank           smallint,
  tenant_name    text,            -- null when the report anonymises (rank+% still data)
  trade_sector   text,
  gri_percentage numeric,         -- her column name
  pct_basis      text,            -- fix A6
  source_page    int,
  primary key (symbol, fiscal_year, rank)
);
```

### D.7 `sgx_reit_trade_mix` *(fix A5 — REIT-level set + our derived aggregate)*

```sql
create table sgx_reit_trade_mix (
  symbol      text references sgx_reit_profile(symbol),
  fiscal_year smallint,
  category    text,
  pct         numeric,
  pct_basis   text,               -- fix A6
  is_derived  boolean default false,  -- true = our property roll-up, beside disclosed
  source_page int
);
```

### D.8 `sgx_reit_income_component` *(pickup B — feeds the standardized formulas)*

```sql
create table sgx_reit_income_component (
  symbol      text references sgx_reit_profile(symbol),
  fiscal_year smallint,
  statement   text check (statement in ('revenue','expense','adjustment')),
  component   text,               -- canonical key, alias-mapped from note labels
  amount      numeric, currency text,
  label_raw   text,               -- exact audited note line
  source_page int,
  primary key (symbol, fiscal_year, statement, component)
);
```

### D.9 `mv_sgx_reit` — the combining view *(discussion #1)*

The MV Gerald described: sectors-DB columns + REIT enrichment, one queryable surface.

```sql
create materialized view mv_sgx_reit as
select c.symbol, c.name, c.sector,                -- whatever sgx_companies provides
       p.reit_sub_sector, p.income_model,
       perf.fiscal_year, perf.portfolio_value, perf.net_property_income,
       perf.dpu, perf.net_distributable_income
       -- + market cap / financials joined from sgx_daily_data / sgx_company_report
from sgx_companies c
join sgx_reit_profile p   using (symbol)
left join sgx_reit_performance perf using (symbol);
-- refresh after each extraction run / daily-data load
```

---

## E. Deliberately NOT here

- Anything sectors DB already has: market cap, price/volume, shares, standard financial
  statements (discussion #1–2).
- Her `valuation_revenue` and standalone `top_10` sheets — manual-fallback artifacts, not
  schema (discussion #3–4).
- The deep v2/v3 machinery: FX provenance, figure_type (forecast/pro-forma), stub-period
  flags, covenants/distress, developments pipeline, lease-expiry ladders, WALE, doc-chunk
  RAG layer, generic surfaces + dictionary. Not contradicted — unproven as *reliably
  extractable at scale*. Each returns only when extraction runs show the data is
  consistently there.

## F. Iteration rule — how the schema earns changes

Pilot (CICT → FCT → CLCT, then one hard model, e.g. Sasseur), tracking per column:

- **fill rate** — % of (symbol, year) rows where extraction produced a value;
- **agreement rate** — for anything cross-checkable: Σ(property gross_revenue) vs reported
  total; derived trade mix vs disclosed set; `gross_revenue` here vs `sgx_company_report`
  revenue (decides the D.5 provisional column).

Then mechanically:
- fill < ~20% after the pilot and not structurally explainable ("master-lease trusts don't
  have occupancy") → **drop or demote to jsonb**;
- a figure we keep finding with no home (FX rates, WALE, lease expiry showed up this way
  in the audit) → **add it then**, one column/table at a time, with evidence;
- a parsed column that keeps disagreeing with its `*_raw` source → fix the parser, not the
  schema.

`_run_summary.json` already exists per extraction run; extend it to report these two rates
per column so drop/add decisions are data, not debate.
