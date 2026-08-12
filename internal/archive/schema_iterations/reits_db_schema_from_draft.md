# `sgx_reit_*` schema — starting from the `REITS db.xlsx` draft

> Team decision (call, Jun 2026): the colleague's workbook is the **base shape**. This doc
> translates her 6 sheets into production tables with her structure and column names kept,
> and folds in exactly three things from her brief:
>
> 1. **Terminology → parsing rules** — tenure, purchase/effective date, management/manager
>    must be pinned down so the scraper "takes the correct figure".
> 2. **Tenant composition has two sets** — property-level and overall; take property level
>    and aggregate to REIT level (where disclosure allows — see §4).
> 3. **Computed metrics are standardized on our end** — REITs "opt in or opt out a certain
>    particular/item" to make figures look good; our formulas must be one formula for all.
>    Per the call, this applies to **land tenure as well** (remaining term is computed by
>    us from dates, never trusted as a printed snapshot).
>
> Everything from the v2/v3 explorations that is *not* needed to serve these three points
> is deliberately left out of this iteration (§7 lists what's parked and why).

---

## 1. What the draft contains (faithful inventory)

| Sheet | Shape | Becomes |
|---|---|---|
| REIT Profile | id, symbol, name, sub_sector, address, basic/diluted shares, management_company | `sgx_reit_profile` |
| Property | id, country, category, property_name, address, reit_id, ownership, market_valuation, net_property_income, gross_revenue, occupancy_rate, trade_mix (json), major_tenant, gla, nla, effective date, term_of_lease, land tenure | `sgx_reit_property` |
| Portfolio Performance | reit_id, property_portfolio (json: id, purchase_year, purchase_price), gross_revenue/NPI, total_market_value, top_10 (json) | `sgx_reit_performance` + `sgx_reit_property_purchase` |
| REIT Performance | reit_id, market_cap, portfolio_value, properties_location, financials, net distributable income, distribution_record, number_of_unitholders | merged into `sgx_reit_performance` |
| top_10 | tenant_name, trade_sector, gri_percentage | `sgx_reit_top_tenant` |
| Management Profile | company_name, ownership | `sgx_reit_management` |

Two normalizations of her own JSON instincts, in her spirit:
- The purchase list embedded in `property_portfolio` (`{id, purchase_year, purchase_price}`)
  becomes a child table — her draft already models purchases as a *list*, which is exactly
  right: acquisitions are phased (Rock Square 51% in 2018 + 49% in 2020; NEX 25.5% + 24.5%).
- The `top 10 tenant` JSON blob and the `top_10` sheet are the same data; one table.

---

## 2. Core tables (her names, minimal deltas)

### 2.1 `sgx_reit_profile`

```sql
create table sgx_reit_profile (
  reit_id            int unique,                  -- her key, kept for continuity
  symbol             text primary key references sgx_companies(symbol),
                     -- prod join key; her sheet already carries both
  name               text not null,
  sub_sector         text,
  address            text,
  basic_shares       bigint,
  diluted_shares     bigint,
  income_model       text                          -- the one profile addition: tells our
                     -- formulas how to read this trust's income lines (master-lease
                     -- trusts have no occupancy; Sasseur's EMA model has no NPI at all)
);
```

`management_company` moves to `sgx_reit_management` (§2.5) per brief item 1 — "management/
manager" is several roles, not one column.

### 2.2 `sgx_reit_property`

Her column list, with the tenure/date columns restructured so the **computed-on-our-end**
rule applies to land tenure:

```sql
create table sgx_reit_property (
  id                 serial primary key,
  reit_id            int references sgx_reit_profile(reit_id),
  country            text, category text, property_name text, address text,
  ownership          numeric,            -- % stake (Keppel ORQ 33.3%)
  market_valuation   numeric,
  valuation_date     date,               -- NOT the same as effective/purchase date — the
                                         -- reports label it 'Latest valuation date' /
                                         -- 'Valuation as at <date>'
  net_property_income numeric,           -- AS-DISCLOSED ONLY; ~7 of 20 trusts publish it.
                                         -- never computed at property level (no trust
                                         -- discloses per-property expenses) — see §5
  gross_revenue      numeric,            -- ~16/20 disclose; the property's earning
                                         -- potential, per the GRI logic in brief item 3
  occupancy_rate     numeric,
  trade_mix          jsonb,              -- her shape kept: {"Food & Beverages": 33.9, ...}
                                         -- property-level set (brief item 2)
  major_tenant       text,
  gla                numeric, nla numeric,
  -- land tenure block (brief: standardized on our end)
  land_tenure        text,               -- Freehold | Leasehold  (her column)
  effective_date     date,               -- her 'effective date': lease/ownership start
  purchase_date      date,               -- distinct concept — see parsing rules §3
  land_lease_term_years    numeric,      -- the '99' in '64/99'
  land_lease_expiry_date   date,         -- stored when disclosed (CLAR prints exact dates)
  tenure_raw         text                -- verbatim: '64/99', '23/60', '30+30 years',
                                         -- 'Part freehold, Part Right of Superficies' —
                                         -- audit trail for whatever we computed
  -- NOTE: no land_lease_remaining column. Remaining term = computed at query time from
  -- expiry/effective date. A stored 'remaining' goes stale the day after publication and
  -- is exactly the kind of figure a report can present favourably.
);
```

### 2.3 `sgx_reit_property_purchase` — her purchase list, normalized

```sql
create table sgx_reit_property_purchase (
  property_id    int references sgx_reit_property(id),
  purchase_year  smallint,               -- her field; granularity as disclosed
  purchase_date  date,                   -- when the report gives a full date
  purchase_price numeric, currency text,
  stake_pct      numeric                 -- phased deals: 51% + 49%
);
```

### 2.4 `sgx_reit_performance` — her two performance sheets, one row per (reit, FY)

```sql
create table sgx_reit_performance (
  reit_id              int references sgx_reit_profile(reit_id),
  fiscal_year          smallint,
  -- her REIT Performance sheet
  portfolio_value      numeric,
  properties_location  text,
  net_distributable_income numeric,
  distribution_record  jsonb,            -- per-distribution: period, dpu, ex/pay dates
  number_of_unitholders int,
  -- her Portfolio Performance sheet
  gross_revenue        numeric,
  net_property_income  numeric,          -- as reported (their formula)
  total_market_value   numeric,
  dpu                  numeric,
  -- provenance
  source_report text, source_page int,
  primary key (reit_id, fiscal_year)
);
-- market_cap deliberately dropped from her sheet: lives in prod sgx_daily_data already.
```

### 2.5 `sgx_reit_management` — her Management Profile sheet + the role column

Brief item 1: "management/manager" in the reports is several different things. One added
column makes her sheet hold all of them:

```sql
create table sgx_reit_management (
  reit_id      int references sgx_reit_profile(reit_id),
  company_name text,                     -- her column
  ownership    numeric,                  -- her column (sponsor/manager stake)
  role         text check (role in ('reit_manager','property_manager','operator',
                 'master_lessee','trustee','sponsor')),
                 -- CICT alone has 3 property managers split by asset class;
                 -- FEHT has an SG operator + Marriott for Japan;
                 -- a master lessee is a counterparty, not a service provider
  property_id  int                       -- null = portfolio-wide
);
```

### 2.6 `sgx_reit_top_tenant` — her top_10 sheet

```sql
create table sgx_reit_top_tenant (
  reit_id        int references sgx_reit_profile(reit_id),
  fiscal_year    smallint,
  rank           smallint,
  tenant_name    text,                   -- null when the report anonymises (KDC's
                                         -- hyperscalers are unnamed; rank+% still real data)
  trade_sector   text,
  gri_percentage numeric,                -- her column name kept
  pct_basis      text,                   -- see §4 — not every trust's % is GRI
  primary key (reit_id, fiscal_year, rank)
);
```

---

## 3. Brief item 1 — terminology, wired into the parser

The alias dictionary (seeded from 20 parsed ARs) ships as scraper config. The walkthrough
call should review/extend this list — it is the direct answer to *"this has to be then
included in the parsing/scraper so that it takes the correct figure"*:

| Our field | Labels in the wild | Trap the parser must dodge |
|---|---|---|
| `land_tenure` | "Land Tenure" (CICT, KDC) · "Tenure" (CLAR, FCT) · "Land title type" (First REIT) | CICT embeds the start date in prose: "Leasehold tenure of 99 years with effect from 21 Nov 2011" |
| `land_lease_term_years` | "Term of lease" (MLT, KDC, CLAR, FEHT, First REIT) | **"Term of lease" in a portfolio statement = the REIT's land lease, NOT a tenant lease.** MLT writes "30+30 years" (renewal option) |
| remaining term (computed) | "Remaining term of lease" (all) | Freehold rows carry the literal string "Freehold" in numeric columns. We ignore the printed remaining figure and compute from dates |
| `purchase_date` / `purchase_year` | "Date of legal completion" (MLT) · "Acquisition date" (CLAR, First REIT, Stoneweg, KORE) · "Purchase Price in YYYY" (CICT, FCT) | Phased acquisitions → multiple purchase rows, not one |
| `effective_date` | lease commencement / "with effect from" prose | Distinct from purchase date AND from valuation date |
| `valuation_date` | "Latest valuation date" (MLT) · "Valuation as at \<date\>" | Distinct from "Agreed Property Value in YYYY" (CICT historical reference) |
| `role` in management | REIT Manager / Property Manager / Operator / Master Lessee / Trustee / Sponsor | Different roles, different fee bases — never merged into one "manager" |

Extraction always targets the **audited Portfolio Statement** first (an RAP 7 requirement,
present in 20/20 reports) — tenure/term/valuation come from the audited section, not
marketing pages.

---

## 4. Brief item 2 — tenant composition, two sets

Agreed mechanics, with one evidence-based caveat:

- **Property level** → `sgx_reit_property.trade_mix` (her jsonb shape kept).
- **REIT level** → aggregated by us from the property set, stored flagged as derived.
- **Caveat**: only CICT and Sasseur disclose property-level trade mix (2 of 14 audited —
  even FCT, pure retail, gives per-mall top tenants only). So the REIT-level **disclosed**
  set must also be captured for every trust; aggregation is the primary path *where property
  data exists* and a cross-check against the disclosed set (they should reconcile — if they
  don't, the parser flagged the wrong table).

```sql
create table sgx_reit_trade_mix (        -- REIT-level set
  reit_id     int, fiscal_year smallint,
  category    text, pct numeric,
  pct_basis   text,                      -- gri | gri_excl_gto | gross_revenue |
                                         -- rental_income | headline_rent |
                                         -- cash_rental_income | nla | outlet_sales
  is_derived  boolean default false,     -- true = our property-level roll-up;
                                         -- stored beside disclosed, never mixed
  source_page int
);
```

`pct_basis` is the non-negotiable column: the audited trusts use **8 different
denominators** for this percentage (KORE uses cash rental income, Stoneweg headline rent,
Sasseur % of outlet *sales*). Cross-REIT comparison without the basis is silently wrong —
the same reasoning as brief item 3, applied to percentages.

---

## 5. Brief item 3 — GRI/NPI boundary + the standardized formula registry

Her conceptual split holds exactly in the data:

- **GRI / gross revenue → property level.** ~16/20 trusts disclose per-property gross
  revenue; it measures the property's earning potential. (One parser rule: "gross revenue"
  ≠ GRI — CICT footnotes gross revenue = GRI + car park + other; we store what the report
  names and keep GRI separate when separately disclosed.)
- **NPI → REIT level, ours standardized.** Reported NPI is entangled with management and
  accounting choices — they "opt in or opt out a certain particular/item":
  utilities are 35% of CLAR's expenses but immaterial for master-lease trusts; loss
  allowance is 36% of KDC's; KORE buries straight-lining in "other" (reported NPI +3.0%,
  adjusted +0.3% — the gap is purely accounting).

To standardize on our end, we need the raw ingredients. **One structural addition** beyond
her sheets — capture the audited revenue/expense note lines:

```sql
create table sgx_reit_income_component (
  reit_id int, fiscal_year smallint,
  statement text check (statement in ('revenue','expense','adjustment')),
  component text,        -- canonical: base_rental, turnover_rent, service_charge,
                         -- recoveries, car_park, property_tax, utilities, maintenance,
                         -- property_mgmt_fee, marketing, staff, loss_allowance, land_rent,
                         -- straight_line_rent, ... (alias-mapped from the note labels)
  amount numeric, currency text,
  label_raw text,        -- the exact audited note line, for audit
  source_page int,
  primary key (reit_id, fiscal_year, statement, component)
);
```

The **formula registry** then lives in the API layer (same place prod computes yield and
P/NAV today) — versioned, one formula for all 39 trusts:

| Standardized metric | Our formula (over components) | Why theirs can't be trusted as-is |
|---|---|---|
| Standardized NPI | gross revenue − Σ(standard expense set) | each trust's "property expenses" includes different lines |
| Adjusted NPI growth | excl. straight_line_rent, lease_incentive_amort, one-offs | KORE: +3.0% reported vs +0.3% adjusted |
| GRI-only revenue | revenue − car_park − recoveries − service_charge − other | KORE's revenue is 28% recoveries; Stoneweg's includes €44m service charges |
| Cost ratio | standard expense set ÷ gross revenue | comparable only with the same numerator everywhere |
| Distribution yield / P-NAV | prod-style, from sgx_daily_data + our table | already house convention |
| Land lease remaining | expiry (or effective+term) − today, computed at query time | printed "remaining term" is a stale snapshot |

Boundary the data imposes: standardized NPI is computable **only at REIT level** — no trust
discloses per-property expense lines. At property level we offer gross revenue (near-
universal, comparable) and as-disclosed NPI (sparse, flagged). Pretending otherwise would
fabricate data.

---

## 6. Pilot

Same as agreed previously, now against this shape: extract **CICT → FCT → CLCT** (richest
property-level disclosure; CICT exercises trade_mix aggregation since both sets exist),
validate Σ(property gross_revenue) vs the reported total, then stress the hard models
(Sasseur EMA, CLAS management contracts, Keppel REIT JVs).

## 7. Parked (from v2/v3) — revisit only when the pilot demands

- multi-currency value+SGD pairs with fx provenance (needed at CLCT/Centurion, not CICT/FCT)
- figure_type (forecast/pro-forma rows), stub-period flags (Centurion)
- covenant/distress layer (Manulife), developments pipeline (CLINT)
- the generic facts/breakdowns/records surfaces and the dictionary table (v3)
- doc_chunks RAG layer

None of these conflict with the draft-first shape — each is an additive table or column
when (if) the corresponding trust enters scope.

## 8. For the walkthrough call

1. Her term list vs §3 — she may have cases from the other 30 trusts the 20-report audit
   missed.
2. Key choice: keep `reit_id` int as her sheets have it (mapped 1:1 to `symbol` in the
   profile) vs keying everything on `symbol` directly. Recommend: keep both columns,
   FK on whichever the team prefers — zero data difference.
3. Where her CICT property-level NPI values came from (the FY2025 AR pages show gross
   revenue but no per-property NPI) — decides whether that column can be backfilled.
4. Confirm the standard expense set for the standardized-NPI formula (which components are
   in, which are out — esp. land rent, which some trusts route outside property expenses).
