# From atoms to `sgx_manual_input` — how our financials are built and projected

A single narrative connecting the whole chain: **annual report → extraction (raw) → the 4
cash-flow "atoms" + locked conventions → `financial_final` → the `sgx_manual_input` projection.**
Written as the working knowledge + lessons for anyone touching `build_manual_input_from_final.py`,
`build_final_tables.py`, `_apply_conventions.py`, or the financial extraction. Companion to
`manual_input_mapping.md` (the field-by-field table) and `final_schema_proposal.md`.

---

## 1. The one-line model

```
Annual Report PDF
  -> Datalab parse (parsed_reports_datalab/<stem>/full.md, page-anchored)
  -> extraction (reit-extract-hybrid) -> RAW sgx_reit_* (7 tables, native currency, full provenance)
  -> _apply_conventions.py : the 4 atoms -> derived metrics (EBIT/EBITDA/depreciation/FFO/capex)
  -> build_final_tables.py : SGD-normalized, sqm, provenance-stripped, renamed  -> sgx_reit_*_final
  -> build_manual_input_from_final.py : compose one row per (symbol, declared FY) -> sgx_manual_input
```

Two golden rules that explain almost every design choice downstream:

- **RAW is the system of record** — native currency, every figure with provenance (page, `*_basis`,
  `*_raw`, flags), `line_items`. Nothing is thrown away here.
- **Each later layer is a pure projection of the one before it.** `_final` adds FX + cleanup;
  `sgx_manual_input` composes/derives. No layer re-reads the annual report; no layer invents numbers.

---

## 2. The "atom" thing — why financial metrics are *computed*, not read

Our headline financial metrics (EBIT, EBITDA, depreciation, FFO, capex) **cannot be read off any
single line** of an annual report, and different trusts present them differently. So instead of
trusting a report's own "EBITDA" cell, we capture **four raw building blocks** — the *atoms* — from
the audited **cash-flow statement + notes**, and *derive* everything from them under one locked
convention. This makes every REIT comparable and every derived number auditable.

The 4 atoms `(dep_pe, fv_cf_signed, finance_costs, capex_sum)`:

| atom | what it is | where |
| --- | --- | --- |
| `dep_pe` | depreciation of property & equipment | C/F operating add-back (0 for pure-IP REITs) |
| `fv_cf_signed` | net fair-value change of investment properties, **cash-flow signed** | C/F operating add-back |
| `finance_costs` | **gross** finance costs (do NOT net off interest income) | finance-costs note total |
| `capex_sum` | Σ of ALL IP-related investing outflows **including acquisitions** | C/F investing |

They live in the `ATOM` dict in `scripts/db/_apply_conventions.py`, keyed `("SYM.SI", declared_fy)`,
in `$'000`. They exist for **reproducibility**: any derived value can be re-derived and checked.

### The locked derivation (Evelyn's meeting conventions, 2026-07)
```
ebit                           = operating_income (= NOI)          # for REITs, EBIT is populated with NOI
depreciation                   = dep_pe + fv_cf_signed             # can be NEGATIVE in a revaluation-gain year
ebitda                         = pretax_income + finance_costs + depreciation
interest_expense_non_operating = finance_costs (gross, positive)
funds_from_operation (FFO)     = net_income + depreciation - net_property_sales   # NAREIT-style
capital_expenditure            = capex_sum (positive; includes acquisitions)
```
Signs: expense scalars POSITIVE; `minorities` & `perpetual_security_holders` **negative** (deductions,
so `net_income + stored_perp + stored_minorities = unitholders`); `non_operating` & `net_property_sales`
SIGNED. Scope: `net_property_sales` = **direct IP disposals only** (exclude subsidiary/JV-stake sales —
those stay in `line_items` as signed adjustments).

**Consequences that look like bugs but are correct:**
- FFO legitimately sits **below** net income in a revaluation-*gain* year and **above** in a *loss* year.
- `depreciation` (and thus EBITDA) can be negative when the FV-of-IP swing dominates.
- Big capex (e.g. > S$1bn) is correct when the year included property acquisitions.

### Sub-cases learned the hard way
- **Hotel trusts on the PPE revaluation model** (e.g. XZL/Acrophyte): hotels are *depreciated* AND
  *revalued* through a "Revaluation of PPE" P&L line. Treat that PPE revaluation as the IP-FV
  analogue → put it in `fv_cf_signed`, so FFO/EBITDA strip it like any real-estate revaluation
  (NAREIT). See `reit-extract-hybrid` REFERENCE §6.
- **Presentation currency ≠ asset currency.** Several China/Japan/India trusts (AU8U, CRPU, DHLU,
  CY6U) *present* their audited statements in **SGD**; foreign currencies appear only in per-asset
  disclosures. Always read the statement header — never assume from where the assets are.

---

## 3. `_final` — the clean, SGD projection

`build_final_tables.py` turns RAW into `sgx_reit_*_final`. What it does that matters downstream:

- **FX to SGD, per figure, date-aware.** `to_sgd(value, ccy, date)` picks the nearest quarter in
  `quarterly_rates.json` and multiplies. **If a currency/quarter has no rate it NULLs the value —
  it never emits raw native as SGD.** (This is why VND lines were NULL until we added VND rates from
  the MAS `Exchange Rates.csv`; RMB is normalized to CNY at load.) Non-money fields (share counts,
  ratios, `_derived`) are not converted.
- **Renames to prod names** and **drops `_derived`** in `income_stmt_metrics`; e.g. RAW
  `weighted_avg_shares_basic` → `basic_shares_outstanding` here. So `_final` is already prod-shaped.
- **`properties_location` normalization** (moved into `build_final` 2026-07): strips cities/counts/
  parentheticals, unifies country variants (Netherlands/UK/...), any delimiter → `", "`, renders
  `"[A, B, C]"`. Backed by `normalize_locations.py`'s `CANON` — **add missing countries there** or
  they are silently dropped (Slovakia + Switzerland were such gaps).
- Everything stays **declared-FY** labeled (see §5).

**Lesson:** `_final` is the right join surface for the manual_input projection — SGD, renamed,
declared-FY. But it still carries one ours-only extra: `depreciation` (see §4).

---

## 4. The `sgx_manual_input` projection — mapping + lessons

`build_manual_input_from_final.py` composes one row per `(symbol, declared FY)` from
`financial_final + performance_final + property_final + top_tenant_final + trade_mix_final`.
Full field table is in `manual_input_mapping.md`; the load-bearing points and lessons:

- **`income_stmt_metrics`** = copy of `financial_final.income_stmt_metrics` **minus `depreciation`**.
  `sgx_manual_input` has a fixed 21-key income-statement shape with **no `depreciation`** key; `final`
  carries it as an ours-only derived field, so the projection must drop it. `basic_shares_outstanding`
  is included (some existing prod rows omit it — ours is the more complete superset).
- **`balance_sheet_metrics` / `cash_flow_metrics` / `employee_breakdown`** = copy 1:1 (keys already match).
- **`sankey_component`** = derived from `income_stmt_metrics` via `make_sankey_component` (verbatim from
  the old notebook — kept identical so the frontend Sankey renders the same).
- **`industry_breakdown`** composed:
  - `top_10_gri%_customers` ← `top_tenant_final` (top-10 by `revenue_pct`, stored as `/100` fraction)
  - `gross_rental_income_by_sectors` ← `trade_mix_final` (`{category: pct/100}`, **summed** per canonical
    category; **omit** when the sum > 130%, i.e. ambiguous office+retail like T82U)
  - `property_portfolio_top_20` ← `property_final` (top-20 by SGD `gross_revenue`; renames
    `property_name→name`, `market_valuation→valuation`, `gross_revenue→gross_income`; `occupancy_rate`/
    `ownership` → `/100`)
  - `property_counts_by_country` ← `property_final` (`{country:{category:[count, ΣSGD gross, ΣSGD val]}}`)
  - `distribution_metrics` ← `performance_final` (see the formulas below — **name collisions**, do not
    copy same-named columns)
- **`distribution_metrics`** (the subtle one, verified vs the colleague's `.xlsx`):
  - `adjusted_distributable_income` = `COALESCE(adjusted_distributable_income, net_distributable_income)`
  - `distributable_income` = `distributable_income_opening + adjusted(above) + COALESCE(distribution_pool_other_movements, 0)`
  - `distribution_paid` = `distribution_cash_paid` (cross-year cash line — NOT `performance.distribution_paid`)
  - `end_of_year_distribution` = `distributable_income_closing`
  - `end_of_year_shareholder_units` = `number_of_shareholder_units`; `units_to_be_issued` = `units_to_be_issued`

### Values will differ from the old Excel — on purpose
When you `--verify` against existing prod rows, **as-declared figures match to the dollar**, but
`ebit` / `ebitda` / `funds_from_operation` / `interest_expense_non_operating` differ. That is the
Evelyn-convention (§2) vs the old Excel formulas — **ours is authoritative**. Do not "fix" ours toward
the Excel.

### This projection *fixes* two Excel-era prod errors at the source
Because financials now come from our verified `sgx_reit_financial` rather than a hand-filled Excel:
- **AJBU** was mapped to **Keppel Ltd** (the parent) financials in the dev Excel copy — our projection
  uses the real Keppel DC REIT numbers. (AJBU was never in prod `sgx_manual_input`; only the dev copy.)
- **ME8U FY2024** carries the wrong `source_url` (an FCT link) in prod — ours overwrites it with the
  correct `performance_final.source_url`.

---

## 5. The FY-offset trap (first-half fiscal-year-ends)

`sgx_manual_input.financial_year` = **declared FY**: statement ending **Jan–Jun of X → X-1**, **Jul–Dec
of X → X**. So a **March**-FYE trust (M44U/ME8U/N2IU/O5RU) ending 31-Mar-2026 is declared **FY2025**;
a **June**-FYE trust (JYEU/P40U) ending 30-Jun-2025 is **FY2024**.

- Filenames in `annual_reports/` use the **company** AR-year label (e.g. `..._FY2026.pdf` = the Mar-2026
  report), while `parsed_reports_datalab/`, `extracted/`, the DB and `_final` all use the **declared
  FY**. Expect an offset of 1 between the PDF name and everything downstream for these reporters.
- Our `_final` tables are **all declared-FY consistent**, so the projection joins children on
  `financial_year` directly and derives the target FY from `performance_final.date` (both agree).
- Verified: 0 declared-FY mismatches in dev and prod across every March/June reporter.

---

## 6. Two separate prod destinations — don't conflate them

There are **two** prod write paths and they are independent:

1. **`sgx_reit_*` (6 tables)** ← `promote_final_to_prod.py` from `*_final`. Transforms: strip `.SI`;
   percent→fraction (`occupancy_rate`, `ownership`, `revenue_pct`, `pct`, `interest_pct`; **not**
   `gain_loss_pct`); `properties_location` → bracketed canonical text; dates → strict `YYYY-MM-DD` or
   NULL; some numerics stored as text; trade_mix **aggregated** to the PK `(symbol, fy, category,
   pct_basis)`; dev-only columns dropped. `sgx_reit_financial` has **no** prod counterpart here.
2. **`sgx_manual_input` (1 table)** ← `build_manual_input_from_final.py` (this doc). A per-`(symbol,fy)`
   projection incl. the financial blobs. This is a **general SGX-company table** (banks/airlines/
   conglomerates + REITs), of which our REITs are a subset.

Promoting `sgx_reit_*` does **not** feed `sgx_manual_input` and vice-versa. The manual_input projection
reads dev `*_final` directly, not prod `sgx_reit_*`.

---

## 7. Gotchas checklist (bit us at least once)

- **Never emit native as SGD.** Missing FX rate → NULL, not the raw number. Add rates (VND from MAS
  `Exchange Rates.csv`) then rebuild.
- **`depreciation` must be dropped** in the manual_input income-statement (ours-only key).
- **Add new countries to `normalize_locations.CANON`** or they vanish from `properties_location`.
- **trade_mix > 130%** → ambiguous multi-segment; omit `gross_rental_income_by_sectors`, don't sum to ~200%.
- **`distribution_paid` name collision**: manual_input's `distribution_paid` = `distribution_cash_paid`,
  NOT `performance.distribution_paid`.
- **Read the statement header for currency.** Asset location ≠ presentation currency.
- **Re-derive before promoting** if a row shows `funds_from_operation = null` (e.g. M44U/ME8U/N2IU
  FY2025) — the atoms exist; run `_apply_conventions`.
- **`sgx_manual_input` financials are NOT auto-filled from ours yet** in prod — the projection exists
  (`--dry`/`--verify` validated) but has not been run with `--write`.

---

## 8. Files

| file | role |
| --- | --- |
| `scripts/db/_apply_conventions.py` | `ATOM` dict + Evelyn's derivation → RAW `sgx_reit_financial` |
| `scripts/db/build_final_tables.py` | RAW → `sgx_reit_*_final` (FX, sqm, rename, location normalize) |
| `scripts/db/normalize_locations.py` | canonical `properties_location` cleanup (`CANON`) |
| `scripts/db/build_manual_input_from_final.py` | `*_final` → `sgx_manual_input` projection (this doc) |
| `scripts/db/promote_final_to_prod.py` | `*_final` → prod `sgx_reit_*` (the OTHER, separate path) |
| `docs/reits_db_handoff/manual_input_mapping.md` | the field-by-field mapping table |
| `quarterly_rates.json` / `Exchange Rates.csv` | FX rates (incl. VND) for `build_final` |
