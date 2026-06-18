# reit-extract REFERENCE

Companion to `SKILL.md`. Everything here is distilled from a structural sweep of four
Datalab-parsed archetype reports (FY2025):

| Archetype | Report | sub_sector | Why it's here |
|---|---|---|---|
| SG diversified | CICT (C38U) | Diversified | JV/proportionate vs 100% valuation traps; full table set |
| Hospitality, stapled | CapitaLand Ascott (HMN) | Hospitality | REIT+BT staple; trade mix is a corporate-account industry mix (verify, don't assume absent); units not GLA; multi-currency |
| Data centre | Keppel DC (AJBU) | Data Centre | anonymised clients; client-type ≠ trade mix; no MW; NCI |
| US office | Manulife US (BTOU) | Office | USD; per-property NPI in bar charts; held-for-sale |

> ⚠️ **These four are ILLUSTRATIVE, not a taxonomy.** They show the *range* of layouts that
> exist — they are NOT a set of rules to apply to a new report. Reports do not generalise by
> sub-sector or sponsor. Treat everything below that is sub-sector-specific as *examples of
> variety you might encounter*, never as a precondition. Discover each report from the report.

---

## §0 — Invariants (the ONLY things you may assume; everything else: discover)

These hold for every SGX REIT — they are accounting/SGX structure, not observations:

1. **Task = the schema.** Fill the 6 tables / fields in `schema/models.py`. That defines what
   to look for. (Not "what this sub-sector usually has.")
2. **Valuation source = the audited Portfolio Statement, in `'000`** (Tier C) — never the
   marketing summary (millions) and never the aggregate investment-property line.
3. **Income source = the full Statement of Total Return** — every line down to "total return
   for the year", not just the revenue/opex notes.
4. **Money is absolute** (×1000 from `'000`); **`source_page` on every record**; **currency
   per figure**; **reconcile Σ to the disclosed total** (property valuations → portfolio total;
   trade_mix → 100%; income → total return).
5. **Discover, don't assume.** What each table looks like, where it lives, what units it uses,
   and **whether a field is present or absent is a property of THIS report** — establish it by
   reading (use the page map: classify + summary), never from a sub-sector prior.
6. **Structural absence must be proven from this report**, with evidence — never declared
   because "sub-sector X usually lacks it". "Disclosed on a narrow basis" ≠ absent (capture it,
   scope it).
7. **Disclosed vs inferred — flag every inference.** Prefer disclosed values. You MAY infer or
   derive a value for completeness (compute it; apply a portfolio figure per-property; assign a
   category from a name/known fact) — but it must be FLAGGED, never made to look disclosed.
   Record each in **`_notes.inferred[]`**:
   ```json
   {"table": "properties", "field": "occupancy_rate", "scope": "all active rows",
    "value": 100.0, "basis": "portfolio 'committed occupancy 100%' applied per-property
    (master lease); not disclosed per property", "source_page": 71}
   ```
   (Use `scope` for a whole-field rule, or `rows`/`property_name` for specific records.) Examples
   that MUST be flagged: occupancy=100% applied from a portfolio figure; a top-tenant
   `industry` assigned from the company name when the table has no sector column; a value
   computed as `total × pct`. If you can't justify the inference, leave the field null.

8. **A failed check is a SIGNAL TO INVESTIGATE, never a license to make numbers balance.**
   This applies to EVERY field and EVERY check — not just gross revenue. When a reconciliation
   doesn't tie, two artefacts disagree, a sum is off, an enum is wrong, or a gate FAILs:
   **the value is wrong, or your classification is wrong, or the disclosed total is being read
   off the wrong line — and the answer is in the report.** Go back to the source page, find what
   the report ACTUALLY says, and fix the ROOT CAUSE with a `source_page` citation.
   - **NEVER** invent, plug, reclassify, derive, round, drop, or adjust a value just to make an
     equation close. "It's not logically consistent" is the start of the investigation, not the
     fix. A change that makes the numbers balance but isn't what the report says is a FABRICATION,
     even when the arithmetic now works (e.g. moving an income line `revenue`→`adjustment` only
     because that closes the tie-out, without confirming on the audited statement that the line
     truly sits below NPI).
   - Ask *why* it doesn't balance: a merged/duplicate row? a missed property? a JV asset that's
     equity-accounted (outside the consolidated total)? a below-NPI line mislabelled? the
     disclosed total taken from a marketing summary, not the audited statement? a sign error?
     Each has a different, source-grounded fix.
   - If you genuinely cannot resolve it from the report, leave it null/flagged and say so in
     `_notes` — do NOT force a balance. An honest unresolved gap beats a fabricated tie-out.
   - The deterministic gates DETECT mismatches; they do NOT tell you the right fix. Only the
     report does. (This is the same discipline the `reit-audit` skill applies — every value is a
     claim to confirm against the source.)

Anything in §1/§3b/§4 below that predicts presence/absence/shape from sub-sector or sponsor is
an *observation* (overfit to the 4 reports), not an invariant — use it only as a hint to speed
discovery, and let the report override it every time.

---

## §1 — Where each fact lives (field-source matrix)

Pages are FY2025 examples; use `locate.py` for the actual pages in any report. The
**section names** are stable across the corpus even when page numbers move.

| Fact | Section (stable) | Tier / notes |
|---|---|---|
| `profile.management` | "Corporate Information" (back) + "Trust Structure" (front) | roles named explicitly; operators/master-lessees appear in hospitality footnotes |
| `profile.sub_sector` | derive from content (locate.py guesses) | Diversified when 2 physical classes co-dominate |
| `property.market_valuation` | **audited Portfolio Statement / Statement of Portfolio** | **Tier C, $'000** — the only valid source. LOCATE it (name + page vary: "Portfolio Statement" / "Statement of Portfolio" / "Consolidated Portfolio Statement", often near the back); the FS also prints an **aggregate** investment-property figure that is more prominent — do NOT grab that. Foreign trusts: confirm the reporting currency (EUR/JPY/RMB; some print dual RMB+S$) and set `currency` per row. |
| `property.land_tenure / term / remaining / location` | same audited Portfolio Statement | tenure verbatim → `tenure_raw`; enum → `land_tenure` |
| `property.occupancy_rate` | per-property cards / "At A Glance" / audited stmt (US) | NOT in Tier A; absent for hospitality |
| `property.gla / nla` | per-property cards | hospitality uses units/keys → declare structural |
| `property.gross_revenue` | financial-review by-property table + cards | watch "Other Assets" aggregation (CICT) |
| `property.net_property_income` | **often only segment-level** | per-property NPI absent in CICT/AJBU/HMN; in BTOU bar charts |
| `property.major_tenant` | per-property cards ("top 3 tenants") | |
| `performance.*` | "Financial Highlights" / "5-Year Summary" (front) + audited statements | portfolio_value = headline incl. proportionate JV |
| `performance.number_of_unitholders` | "Statistics of Unitholdings" (back) | dated POST year-end (e.g. late Feb/Mar 2026) |
| `performance.dpu` + distribution_record | "Distribution Statement" + DPU table | US trust may show DI/unit while actual DPU = 0 (halted) |
| `top_tenant.*` | "Top 10 Tenants/Clients" | retail/office rich; DC anonymised; hospitality trivial |
| `trade_mix.*` | "Trade Mix" / "Trade Sector by GRI" / "Portfolio Information by Industry" | DC = client trade sector / "by contract type"; hospitality OFTEN none portfolio-wide but VERIFY — Ascott discloses a corporate-account industry mix (capture it, scoped `pct_basis`). Most industries map to the canonical taxonomy |
| `financial.line_items` (revenue) | **Note "Gross Revenue"** | reconciliation anchor = total |
| `financial.line_items` (expense) | **Note "Property Operating Expenses" / "Direct Expenses"** | $'000 |
| Statement of Total Return | audited P&L → `financial` scalars + line_items | NPI = gross revenue − property opex |

**The universal anchors present in ALL four (and ~all SGX REITs):** audited Portfolio
Statement, Statement of Total Return / Comprehensive Income, Gross Revenue note, Property
Operating/Direct Expenses note, Financial Highlights / 5-Year Summary, Distribution
Statement, Statistics of Unitholdings, Corporate Information. Build the extraction around
these; everything else is sub-sector garnish.

---

## §2 — Output file shapes (field names = schema/models.py)

Eight files in `extracted/<SYMBOL>.SI_FY<YYYY>/`. Field names below are authoritative —
`validate_schema.py` checks them against `schema/models.py`. The **year key is
`financial_year`** everywhere.

**profile.json** (single object)
```json
{ "symbol": "C38U.SI", "sub_sector": "Diversified",
  "management": [{"role": "reit_manager", "company_name": "..."},
                 {"role": "trustee", "company_name": "..."}],
  "income_model": "conventional", "source_page": 9 }
```
roles: reit_manager | property_manager | trustee | sponsor | operator | master_lessee.

**performance.json** (single object) — keys: symbol, financial_year, portfolio_value,
properties_location, gross_revenue, net_property_income, net_distributable_income, dpu
(cents), distribution_record `[{period, dpu, ex_date, pay_date}]`, number_of_unitholders,
currency, date (FY-end YYYY-MM-DD), source_page.

**properties.json** (list) — symbol, financial_year, property_name, country, category,
address, ownership (%), market_valuation (absolute, Tier C), valuation_date, currency,
net_property_income, gross_revenue, occupancy_rate, trade_mix `{cat: pct}` (sparse),
major_tenant, gla, nla, land_tenure (enum), effective_date, lease_term_years,
lease_expiry_date, tenure_raw, status (active|divested|held_for_sale), source_page.
Audit-trail extras (not in the schema, kept for QC): `value_basis`, `alt_value`,
`alt_basis`.

**top_tenants.json** (list) — symbol, financial_year, rank, client_name (null/verbatim
descriptor if anonymised), industry (canonical 15, §3), revenue_pct (plain number, e.g. 5.0),
pct_basis, source_page. *(Renamed Jun17 to match prod: client_name / industry / revenue_pct.)*

**trade_mix.json** (list) — symbol, financial_year, category (canonical 15, §3), category_raw
(verbatim), pct, pct_basis, source_page.

**financial.json** (single object → sgx_reit_financial) — **the sector-agnostic financial-
statement core, 1:1 with prod's three jsonb blobs.** Keys: symbol, financial_year, currency,
source_page, plus three nested blobs (standardize like prod):
- `income_stmt_metrics` { total_revenue (= gross revenue, tie-out anchor), cost_of_revenue
  (= property opex), gross_income (= NPI), operating_income, operating_expense, ebit, ebitda,
  pretax_income, income_taxes, net_income (= total return after tax),
  non_operating_income_or_loss, interest_expense_non_operating (finance costs),
  diluted_shares_outstanding, net_property_sales, funds_from_operation, unitholders,
  perpetual_security_holders, minorities, revenue_breakdown/operating_expense_breakdown
  `[{class, amount, category}]` }
- `balance_sheet_metrics` { total_asset, total_equity, total_liabilities, working_capital,
  total_(non_)current_asset/liabilities } — from the audited Statement of Financial Position
- `cash_flow_metrics` { operating_cash_flow, investing_cash_flow, financing_cash_flow,
  net_cash_flow, free_cash_flow, capital_expenditure } — from the audited Cash Flow Statement
- `employee_breakdown` { total_employee, permanent_employee, contract_employee,
  others_employee } — usually **null** for REITs (externally managed); capture manager headcount
  if disclosed. The one sgx_manual_input blob with no other home → kept here for 1:1 coverage.
- `line_items` `[{statement(revenue|expense|adjustment), component, amount (adjustments
  SIGNED), label_raw, source_page}]` — OUR extension: the full Statement-of-Total-Return audit
  trail / reconciliation anchor (Σrevenue − Σexpense + Σadjustment = income_stmt_metrics.net_income).

NOT here: net_property_income / dpu / NDI / distribution_record (those are performance).

**Standardization formulas (REIT Statement of Total Return → `income_stmt_metrics`).**
A REIT statement doesn't print ebit/ebitda/operating_income — derive them so they MATCH prod
(verified to the dollar against prod's M44U row, all 14 buckets):
- `total_revenue` = gross revenue
- `cost_of_revenue` = property operating expenses (POSITIVE)
- `gross_income` = net property income (NPI)
- `operating_expense` = Σ trust expenses below NPI **before finance** (manager/base+perf fees +
  trustee + other trust expenses; POSITIVE)
- `operating_income` = `gross_income − operating_expense`
- `interest_expense_non_operating` = borrowing/finance costs **− interest income** (NET; POSITIVE)
- `pretax_income` = "profit/total return before tax" (as printed)
- `income_taxes` = tax (POSITIVE)
- `non_operating_income_or_loss` = `pretax_income − operating_income` (SIGNED; this is the net of
  finance income/costs, fair-value changes, JV share, divestment gains — everything between
  operating profit and pre-tax)
- `net_income` = `pretax_income − income_taxes` (= "total return for the year")
- `ebit` = `net_income + income_taxes + interest_expense_non_operating`
- `ebitda` = `ebit + depreciation & amortisation` (≈ ebit for fair-value REITs — no P&L D&A;
  add real D&A for cost-model trusts)
- `funds_from_operation` = **discover it from THIS report** — capture the disclosed FFO/AFFO if the
  trust reports one. Many SG REITs report "distributable income" (→ `performance.net_distributable_
  income`) instead of US-style FFO; when no FFO is disclosed, leave it **null** (do not assume
  absence for a whole class — check each report). Do NOT set FFO = net_income: net income includes
  non-cash fair-value movements and one-off gains/losses that FFO excludes, so the two are not
  equivalent (e.g. M44U net_income absorbs −67.6m property FV + −26.9m derivative FV). If you derive
  FFO yourself (net_income + D&A − fair-value/disposal gains), list it in `_derived`.

**Mark derived fields.** Inside `income_stmt_metrics`, add `"_derived": ["operating_income",
"ebit", "ebitda", "non_operating_income_or_loss", "interest_expense_non_operating"]` — the fields
COMPUTED by the formulas above (vs read off the statement). This honours §0.7 (never let an
inference look disclosed) for the standardized blob; the auditor uses it to separate claims from
computations.
- `net_property_sales` = disclosed divestment gain/loss (0 if none); `unitholders` /
  `perpetual_security_holders` / `minorities` = the "attributable to" lines (prod stores
  perpetual & minorities SIGNED)
- `diluted_shares_outstanding` = **weighted-average** units (the DPU denominator), not issued units
- self-check: `Σrevenue_breakdown ≈ total_revenue`, `Σoperating_expense_breakdown ≈ operating_expense`

**Sign convention (match prod `idx_manual_input_extraction`):** in `income_stmt_metrics`, the
**expense-type scalars are stored as POSITIVE magnitudes** — `cost_of_revenue`,
`operating_expense`, `income_taxes`, `interest_expense_non_operating` (prod negates the source,
so a S$(101,733) opex becomes 101,733). `non_operating_income_or_loss` and `net_property_sales`
stay **signed**. `revenue_breakdown`/`operating_expense_breakdown` `amount`s are positive
magnitudes, and must reconcile: Σrevenue_breakdown ≈ total_revenue, Σoperating_expense_breakdown
≈ operating_expense (within 2% — gate-checked). `line_items` keep their own SIGNED-adjustment
rule (separate from the scalars; they're the audit trail, not pushed to prod).

**property_transactions.json** (list, parked) — capture acquisitions/divestments for the
audit trail; not loaded.

**_notes.json** (object) — columns_never_fillable `[{column, reason}]`, data_with_no_home
`[...]` (≤12), parsing_traps `[...]`, reconciliation
`{sum_property_gross_revenue, reported_total_gross_revenue, sum_property_npi,
reported_total_npi, ...}`.

---

## §3 — Enums & alias dictionaries

**pct_basis enum** (top_tenant + trade_mix): `gri` | `gri_excl_gto` | `gross_revenue` |
`rental_income` | `headline_rent` | `cash_rental_income` | `committed_gross_rent` | `nla` |
`outlet_sales` | `npi`. Map the report's footnote wording; if none fits, add to the enum
(and tell the user) rather than inventing a key. DC/US trusts → `rental_income` /
`cash_rental_income`; CICT → `gri` (excl GTO → `gri_excl_gto`).

**trade_mix.category / top_tenant.industry** — canonical **15-value** taxonomy (Evelyn,
Jun17; `schema/sgx_reit_schema.md` §5; same list both fields). Keep the disclosed label
verbatim in `category_raw`; map to canonical via:

- Finance / Insurance / Banking + Legal / Consultancy / Professional - Scientific /
  Accounting → **Financial & Professional Services**
- Medical / Pharmaceutical / Healthcare & Life Sciences + Beauty / salons → **Healthcare &
  Wellness**
- Real Estate / Property Services + Engineering / Construction → **Infrastructure, Real
  Estate & Property Services**
- Energy / Natural Resources / Utility / Marine + Mining → **Energy, Mining & Resources**
- TMT / TAMI / Information & Communications Technology → **IT & Telecommunications**
- F&B / Food & Beverage → **Food & Beverages**
- Supermarket & Grocers / Grocery & Wholesale → **Departmental Store/Supermarket**
- Public Administration / Government agency → **Government Related**
- 3PL / Transportation - Storage / Warehousing → **Logistics & Supply Chain Management**
- retail sub-trades (Jewellery, Sports, Homeware, Education, Leisure…) → **Other Retail
  Trades**; office long tail → **Other Office Trades**; industrial/logistics long tail
  (chemicals, automobiles, document storage, e-commerce) → **Other Industrial Trades**

(Alias dictionary in code: `models.TRADE_ALIASES`. The old 19-value list is folded into the
15 — Banking+Professional, Beauty+Healthcare/Pharma, RealEstate+Construction, Mining+Energy.)

**property.category** — canonical **6** (Evelyn, Jun17): Industrial & Logistics | Office |
Retail | Data Centers | Specialized | Diversified (Commercial). Disclosed asset type →
`category_raw`; map to canonical via `models.PROPERTY_CATEGORY_ALIASES` (Flatted Factories /
Stack-up Buildings → Industrial & Logistics; Life Sciences / Hi-Tech Buildings / **Business
Space** → Specialized).

**flags** (Property + Performance) — `[{type, scope, note}]`. Don't force a universal rule
for odd cases; flag them for human verification: `dpu_half_year_split`,
`same_property_diff_lease`, `divested_partial_data`, `full_consolidation_partial_ownership`
(100% gross_revenue/NPI on a <100%-owned asset).

**land_tenure**: Freehold | Leasehold only. Verbatim → `tenure_raw`. Mappings:
US "fee simple" / "freehold" → **Freehold**; Indonesia **HGB** ("Hak Guna Bangunan",
right-to-build, state retains title — the report may say "little practical difference from
freehold") → **Leasehold** (it is a fixed-term right); **BOT** (Build-Operate-Transfer)
scheme → **Leasehold**, `lease_expiry_date` = the BOT/MLA expiry; China "land use right" →
**Leasehold**. When a single combined row has **two leases with different expiries**
(e.g. hospital 2035 + hotel 2027), put the **earlier** expiry in `lease_expiry_date` and both
verbatim in `tenure_raw`.

**income_model**: conventional | master_lease | mcmgi | management_contract |
entrusted_management | fri | mixed. Base-rent + variable/performance-rent (e.g. % of gross
operating revenue) = **fri**; a portfolio mixing several (CLAS, First REIT) = **mixed**.

---

## §3b — Cross-cutting conventions (sub-sector quirks)

Folded in from the healthcare (First REIT) and industrial (MLT) runs — apply everywhere:

- **Units / area metric.** GFA/NLA may be **m²** (Indonesia/Japan/most SG) or **sq ft**
  (US, some SG) — keep the disclosed number, note the unit (downstream normalises). When a
  trust's size metric is **beds/keys/rooms** (healthcare, hospitality) or **MW** (data
  centre), `gla`/`nla` are structurally absent → declare in `_notes.columns_never_fillable`;
  put the bed/key/MW count in `_notes.data_with_no_home`. Don't force a non-area metric into
  gla/nla.
- **Multi-currency.** Set `currency` per record. Foreign assets show local currency on the
  cards but reconcile to the reporting currency in the audited statements; trusts disclose
  **two FX rates** (an average rate for income/revenue, a closing rate for valuation) —
  record both in a note when present.
- **Stapled trusts** (CLAS, Far East H-Trust): financials come in 3 columns (REIT / BT /
  **Stapled Group**) — use **Stapled Group**. BT-held properties sit in a separate
  Portfolio-Statement block; PPE-classified assets (e.g. owner-operated hotels) are outside
  the investment-property statement.
- **`number_of_unitholders`** is dated weeks after FY-end (Statistics of Unitholdings) —
  expected, keep the disclosed date.
- **Name forms differ across sections** — audited statements use full legal names, marketing/
  cards use abbreviations. Match/merge on a normalised name (the hybrid `merge_llm.py` keys on
  normalised + quoted-abbreviation forms).

---

## §4 — Quirks catalogue (observed, by report)

> ⚠️ **ILLUSTRATIVE — these are quirks seen in specific reports, NOT rules.** Do not apply
> any of these to a different report, and do not infer presence/absence from them. They exist
> to show the *kinds* of traps that occur (dual-basis valuations, aggregated rows, scoped
> tables, odd tenure wording) so you recognise one when discovery surfaces it on YOUR report.
> Per the §0 invariants, the report you are extracting is the only authority.

**CICT / diversified (C38U)**
- Gallileo/Main Airport Center appear at 100% in the audited Portfolio Statement
  (547,629 / 319,828 $'000) but the trust owns 94.9%; Tier A shows proportionate
  (S$519.7m/303.5m). `market_valuation` = the audited 100% figure; set value_basis =
  consolidated, note the stake.
- ION Orchard / CapitaSky shown at 50% / 70% in Tier A but 100% (1,268,000 $'000) in Tier
  C. Same rule.
- "Other Assets" row in the financial-review table aggregates Bugis+ and Bukit Panjang
  Plaza — get their individual revenue from the per-property cards.
- Bukit Panjang Plaza is in a separate "Asset held for sale" block (divested Feb 2026).
- Per-property NPI is NOT disclosed (only segment Retail/Office/ID). Declare structural.
- Trade-mix table rolls up "Other Retail/Office Trades" then expands them in two sub-tables
  on the same page — don't double-count; capture the top-level 9 categories.

**Ascott / hospitality stapled (HMN)**
- Stapled REIT + BT: financials in 3 columns (REIT Group / BT Group / Stapled Group) —
  use **Stapled Group**. BT properties (marked `*`) sit in a separate Portfolio-Statement
  block (pp. ~142–143).
- Portfolio Listing shows "Agreed Property Value at Acquisition" (historical cost) — NOT
  valuation. Current valuation only in the audited Portfolio Statements ($'000).
- Revenue note splits gross rental income / hospitality income / hotel revenue.
- Often no per-property NPI/occupancy/GLA/NLA (size metric is units/keys) — but VERIFY each
  before declaring structural.
- **Trade mix DOES exist** here: a "Portfolio Information by Industry" table (~p27), % of
  rental income by industry, scoped to *corporate accounts under management contracts only*.
  Capture it as `trade_mix` with `pct_basis="rental_income (corporate accounts, mgmt-contract
  properties only)"` and `category_raw` verbatim; most industries map to the canonical
  taxonomy (Government Related, Banking/Insurance/Financial, IT & Telecommunications, Energy
  & Utilities, Manufacturing, Healthcare…). Do NOT declare it a structural absence.
- Top-tenant table is thin/absent — confirm in the report.
- Income split disclosed by contract type (master lease/MCMGI/MC) and geography → goes in
  `_notes.data_with_no_home`.

**Keppel DC / data centre (AJBU)**
- Clients fully anonymised everywhere ("Fortune Global 500 Company (Hyperscaler)"); top
  client 42.1% of rental income. Put the verbatim descriptor in `client_name`.
- Two parallel "mixes": client trade sector (Internet Enterprise 69.3% …) and contract
  type (Colocation/Single-Tenant/Shell-and-Core). Use the trade-sector one for trade_mix
  (pct_basis = rental_income); contract type → data_with_no_home.
- Per-property "Attributable Gross Revenue" is the REIT's *share*; NPI only at segment
  level. Area = "Attributable Lettable Area (sq ft)", no MW.
- Tier C carrying value for SGP 7/8 exceeds Tier A/B because a S$350m lease extension was
  capitalised. NCI on SGP 3/4/5 and Tokyo DC 3. Basis Bay = held for sale.

**Manulife US / US office (BTOU)**
- USD throughout; DPU in US cents. **Actual DPU = 0 (distributions halted)** but
  "DI per Unit" = 1.44 — store dpu as disclosed and note the halt.
- Per-property NPI & gross revenue come from **bar charts** Datalab rendered as tables;
  Penn's chart wasn't fully parsed (inline values) — verify against the page.
- Figueroa appears both as active (marketing, US$98.1m) and as "asset held for sale"
  (audited, US$85,703k). Use the audited held-for-sale value; status = held_for_sale.
- Plaza & Peachtree sold in-year — absent from FY2025 detail pages but their partial-year
  P&L is in the consolidated total (≈US$3.9m NPI gap when you reconcile).
- Top-10 tenant table has no trade-sector column; `pct_basis = gri`. Tenure "Freehold" on
  all (fee simple). Revenue note line "Recoveries income" = service-charge recoveries.

**General**
- Tier C "Term of Lease" is the REIT's LAND lease; "Freehold"/"Not applicable" appear as
  literal strings in otherwise-numeric columns.
- Foreign assets list local currency in cards but reconcile to reporting currency in the
  audited statements; capture the disclosed FX rate in a note.
- `number_of_unitholders` is dated weeks after FY-end — that's expected, keep the date.

---

## §5 — Subagent prompt template (one agent per report, Sonnet)

```
Extract <TRUST NAME> (<SYMBOL>.SI) FY<YYYY> into the sgx_reit_* schema.

Parsed report: parsed_reports_datalab/<dir>/full.md  (Datalab markdown, <!-- PAGE N -->)
Use the reit-extract skill: .claude/skills/reit-extract/SKILL.md (+ REFERENCE.md).

1. Run scripts/locate.py on full.md. Note the sub_sector guess and anchor pages.
2. Follow the playbook for that sub_sector. Read only the anchor pages (chunked Read).
3. market_valuation comes ONLY from the audited Portfolio Statement (Tier C, $'000 → ×1000).
4. Write the 8 JSON files to extracted/<SYMBOL>.SI_FY<YYYY>/ using schema/models.py field
   names (financial_year, .SI symbol, absolute money, source_page on every record).
5. Run scripts/validate_schema.py AND scripts/check_extraction.py on the output dir; fix
   every FAIL. Fill _notes honestly (declare sub-sector-structural nulls).

Return: counts per file, both gate verdicts, the reconciliation line, and the top 3
judgment calls you made (dual-basis, held-for-sale, structural nulls).
```

## §6 — Neutrality / verification

For an accuracy check, run a blind re-extraction of a stratified sample (one per
sub-sector) with no access to prior output, then diff. Differences cluster on dual-basis
valuations and pct_basis wording — exactly the judgment calls, which is where review time
should go.

**Playbooks are PRIORS, not facts — verify against THIS report.** The sub-sector notes here
say where data *usually* lives and what's *often* absent; they are hints to speed the search,
never a substitute for looking. In particular:
- **Never declare a field/table structurally absent on the playbook's say-so.** Confirm the
  report genuinely doesn't disclose it. Reserve "structural absence" for true non-disclosure —
  NOT for "disclosed on a narrow basis" (e.g. Ascott's corporate-account industry mix is a
  real `trade_mix`, scoped via `pct_basis`, not an absence).
- A playbook absence claim that turns out wrong is an under-capture bug. If you find data the
  playbook said wouldn't exist, capture it (with a scope note) and the claim here is the bug —
  fix it. (Same failure mode as the now-removed "same sub-sector ⇒ same layout" assumption.)
