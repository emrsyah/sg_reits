# reit-extract REFERENCE

Companion to `SKILL.md`. Everything here is distilled from a structural sweep of four
Datalab-parsed archetype reports (FY2025):

| Archetype | Report | sub_sector | Why it's here |
|---|---|---|---|
| SG diversified | CICT (C38U) | Diversified | JV/proportionate vs 100% valuation traps; full table set |
| Hospitality, stapled | CapitaLand Ascott (HMN) | Hospitality | REIT+BT staple; no trade mix; units not GLA; multi-currency |
| Data centre | Keppel DC (AJBU) | Data Centre | anonymised clients; client-type ≠ trade mix; no MW; NCI |
| US office | Manulife US (BTOU) | Office | USD; per-property NPI in bar charts; held-for-sale |

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
| `trade_mix.*` | "Trade Mix" / "Trade Sector by GRI" | DC = client trade sector; hospitality = none |
| `income_components` (revenue) | **Note "Gross Revenue"** | reconciliation anchor = total |
| `income_components` (expense) | **Note "Property Operating Expenses" / "Direct Expenses"** | $'000 |
| Statement of Total Return | audited P&L | NPI = gross revenue − property opex |

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

**top_tenants.json** (list) — symbol, financial_year, rank, tenant_name (null/verbatim
descriptor if anonymised), trade_sector, gri_percentage, pct_basis, source_page.

**trade_mix.json** (list) — symbol, financial_year, category (canonical, §3), category_raw
(verbatim), pct, pct_basis, source_page.

**income_components.json** (list → sgx_reit_financial) — symbol, financial_year, statement
(revenue|expense|adjustment), component (canonical key), amount (absolute), currency,
label_raw (exact note line), source_page.

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

**trade_mix.category** — canonical 19-value taxonomy (from `schema/sgx_reit_schema.md` §5).
Keep the disclosed label verbatim in `category_raw`; map to canonical via:

- TMT / TAMI / Information & Communications Technology / "Information" → **IT &
  Telecommunications**
- F&B / Food & Beverage → **Food & Beverages**
- Supermarket & Grocers / Grocery & Wholesale → **Departmental Store/Supermarket**
- Public Administration / Government agency / "Government" → **Government Related**
- 3PL / Transportation - Storage / Transportation and Warehousing → **Logistics & Supply
  Chain Management**
- Legal / Consultancy / Business Consultancy / Professional - Scientific / Accounting →
  **Professional Services**
- Medical / Pharmaceutical / Healthcare & Life Sciences → **Healthcare, Pharmaceuticals &
  Life Sciences**
- Energy / Natural Resources / Utility / Marine → **Energy & Utilities**
- Engineering / Construction → **Construction & Engineering**
- Finance / Insurance / Banking → **Banking, Insurance & Financial Services**
- retail sub-trades (Jewellery & Watches, Sports, Homeware, Education, Leisure &
  Entertainment, Digital & Appliance, Multi-Concepts…) → **Other Retail Trades** unless a
  baseline category fits
- office long tail with no home → **Other Office Trades**; industrial/logistics long tail
  (chemicals, automobiles, document storage, e-commerce) → **Other Industrial Trades**

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
- No trade mix, no real top-tenant table, no per-property NPI/occupancy, no GLA/NLA →
  declare all structural; size metric is units/keys.
- Income split disclosed by contract type (master lease/MCMGI/MC) and geography → goes in
  `_notes.data_with_no_home`.

**Keppel DC / data centre (AJBU)**
- Clients fully anonymised everywhere ("Fortune Global 500 Company (Hyperscaler)"); top
  client 42.1% of rental income. Put the verbatim descriptor in `tenant_name`.
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
