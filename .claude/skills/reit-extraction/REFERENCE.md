# reit-extraction — reference

Evidence base: 20 parsed FY2023–FY2025 ARs audited for disclosure patterns; full pilot on
CICT/FCT/CLCT (287 records, Σ-reconciled) + blind re-extraction verification (71/73 exact,
2 diffs = basis ambiguity, 0 extraction errors). Stats quoted below come from that corpus.

## 1. Navigation playbook — section anchors

Grep these (case-insensitive) to build the section map; do NOT read the file linearly.

| Section | Grep patterns that worked | What it yields |
|---|---|---|
| Audited Portfolio Statement | `Portfolio Statement` | per-property tenure, term, valuation, sometimes acquisition date — present in 20/20 reports; the single most trustworthy table |
| Statement of Total Return / income statement | `Statement of Total Return`, `Gross revenue` | trust-level GR, NPI (audited) |
| Distribution Statement | `Distribution Statement`, `available for distribution` | distributable income (watch layering, §3) |
| Revenue / expense notes | `Gross revenue` near `Note`, `Property operating expenses`, `property expenses` | income_components lines |
| Financial review / per-property tables | `Financial Review`, `by Property`, `Gross Revenue` + `NPI` headers | per-property GR/NPI (~16/20 and ~7/20 disclose) |
| Top tenants | `Top 10`, `top ten` | names, %, basis footnote (read the footnote VERBATIM) |
| Trade mix | `Trade Mix`, `Trade Sector`, `tenant.*business`, `Portfolio Lease Profile` | portfolio (always) and per-property (CICT, Sasseur only) |
| Property factsheets | property names; `Committed Occupancy`, `Land Tenure`, `Property Information` | occupancy, tenure raw strings, major tenants |
| Unitholder statistics | `Statistics of Unitholdings`, `Distribution of` | number_of_unitholders — ALWAYS present, in the last ~10% of the document, as-at date post-FYE. Two blind runs wrongly called this "not disclosed"; grep before concluding absence |
| Transactions | `Acquisition`, `Divestment`, `Purchase Price`, `legal completion`, `subsequent` | phased stakes, prices, counterparties; CHECK subsequent-events sections |

Page markers by parser: `<!-- PAGE N -->` (agentic LlamaParse) · `--- N ---` / `{N}---`
(other LlamaParse modes) · `Page N of M` (some pdf2md tools) · none (estimate:
`page ≈ N_pages × char_offset / total_chars`, flag `p_estimated`).

## 2. Output file shapes (mirror `sgx_reit_schema_final.md` §D)

All amounts absolute units; percentages plain numbers (33.9 not 0.339); every record has
`source_page`. `extracted/<SYMBOL>_FY<YYYY>/`:

- `profile.json` — `{symbol, reit_sub_sector, income_model}`. income_model ∈ conventional |
  master_lease | mcmgi | management_contract | entrusted_management | fri | mixed.
- `performance.json` — one object: symbol, fiscal_year, portfolio_value,
  properties_location, gross_revenue, net_property_income, net_distributable_income,
  dpu (cents), distribution_record (array of {period, dpu, ex_date, pay_date} — dates are
  usually NOT in ARs; null them), number_of_unitholders, currency, source_page (int or
  {field: page} map). portfolio_value = the headlined portfolio valuation INCL. JV
  proportionate interests (pinned definition; B/S investment-properties figure differs).
- `properties.json` — array: symbol, fiscal_year, country, category, property_name,
  address, ownership (pct), value_basis (consolidated | joint_venture_100pct |
  effective_interest — REQUIRED whenever ownership < 100 or the property is JV/associate-
  held; says which basis the row's money figures are stated at), market_valuation,
  valuation_date, currency,
  net_property_income (as-disclosed only), gross_revenue, occupancy_rate, trade_mix
  (object {category: pct}, per-property only), major_tenant, gla, nla, area_unit,
  land_tenure, effective_date, lease_term_years, lease_expiry_date, tenure_raw (VERBATIM),
  status (active|divested|held_for_sale), source_page. Dual-currency trusts add
  `*_rmb`-style siblings.
- `property_transactions.json` — array: property_name, transaction_type
  (acquisition|divestment), transaction_year, transaction_date, price, currency,
  stake_pct, counterparty, source_page. One row PER PHASE (NEX 25.5%+24.5%,
  Rock Square 51%+49%). Include historical "Purchase Price in YYYY" rows.
- `top_tenants.json` — array: symbol, fiscal_year, rank, tenant_name (null if anonymised —
  rank+% are still data), trade_sector, gri_percentage, pct_basis, pct_nla (when both
  disclosed, e.g. FCT), source_page.
- `trade_mix.json` — REIT-level disclosed set: symbol, fiscal_year, category, pct,
  pct_basis, is_derived:false, source_page. (Derived roll-ups are computed later, never
  during extraction.)
- `income_components.json` — array: symbol, fiscal_year, statement
  (revenue|expense|adjustment), component (canonical key below), amount, currency,
  label_raw (EXACT note line), source_page.
  Canonical components — revenue: base_rental, turnover_rent, service_charge, recoveries,
  car_park, hospitality, ema_fixed, ema_variable, dilapidations, other; expense:
  property_tax, business_tax_vat, utilities, maintenance, property_mgmt_fee,
  mgmt_reimbursement, marketing, staff, insurance_security, loss_allowance, land_rent,
  depreciation_ffe, leasing_commission_amort, other; adjustment: straight_line_rent,
  lease_incentive_amort, rental_support.
- `_notes.json` — `{columns_never_fillable:[{column,reason}], data_with_no_home:
  [{item,value,page}], parsing_traps:[...], reconciliation:{sum_property_gross_revenue,
  reported_total_gross_revenue, sum_property_npi, reported_total_npi, property_count,
  fx_rate_disclosed}}`.

## 3. Trap table (each produced a real near-miss in the corpus)

| # | Trap | Evidence | Rule |
|---|---|---|---|
| 1 | "Term of lease" = land lease | MLT, KDC, CLAR portfolio statements | never map to tenant WALE; "30+30 years" = renewal option, keep verbatim in tenure_raw |
| 2 | Freehold as string in numeric cols | all freehold rows | expect non-numeric values in term/remaining columns |
| 3 | Tenure label aliases | "Land Tenure" (CICT/KDC), "Tenure" (CLAR/FCT), "Land title type" (First REIT) | same field; CICT embeds start date in prose ("99 years with effect from 21 Nov 2011") |
| 4 | gross revenue ≠ GRI | CICT footnote (GR = GRI + car park + other); KORE 28% recoveries; Stoneweg €44m service charges | store under the report's name; GRI only when separately disclosed |
| 5 | % basis varies per trust | 9 denominators seen: gri, gri_excl_gto, gross_revenue, rental_income, headline_rent, cash_rental_income, committed_gross_rent, nla, outlet_sales | copy the footnote wording, map to enum; Sasseur trade mix is % of SALES |
| 6 | GTO in/out of tenant % | CICT top-10 EXCLUDES GTO; CLCT INCLUDES it | the footnote decides — read it every time |
| 7 | 100% vs proportionate values | Gallileo 547.6 (100%, audited PS) vs 519.7 (94.9% share, valuation table) — BOTH printed | capture basis; prefer audited PS figure + STORE the other as alt_value. Hotspot: property factsheets print 100%-basis full-year figures while the financial review prints consolidated-period ones (CapitaSpring 72.7 vs 37.7 — a mid-year-acquired property; both blind cheap-model runs picked the factsheet figure) |
| 8 | Consolidated vs attributable NPI | Keppel REIT 215.9 vs 381.4 | qualify which one you stored |
| 9 | JV properties outside totals | FCT NEX/Waterway, CICT ION: disclosed at 100% but equity-accounted | exclude from Σ-reconciliation vs consolidated total; note it |
| 10 | Combined property lines | CICT "Other Assets" (2 malls merged); FCT Northpoint wings (split in PS, combined income) | extract at the granularity disclosed; note the grouping |
| 11 | Duplicate table rows | FCT p34 (4 malls duplicated with different values) | reconcile to audited total; the non-reconciling set is the artifact |
| 12 | Distributable income layering | CICT: 860.9 headline vs 869.957 subtotal vs 1,119.753 incl. opening balance; CLCT: 83.9 incl 5.7 top-up vs 78.2 statement | take headline, document layers in note |
| 13 | Acquisition date aliases | "Date of legal completion" (MLT) ≡ "Acquisition date" (others); "Purchase Price in YYYY" (CICT/FCT) | one transactions row per phase |
| 14 | Occupancy type | committed (CICT/FCT/KORE) vs actual (MLT) vs average (Centurion) | record what the header says |
| 15 | Unitholders as-at date | always a post-FYE date (Feb/Nov) | fine — it's the disclosed figure; keep its page |
| 16 | Dual currency | CLCT dual-columns RMB/SGD, rate 5.499 in a footnote; transaction prices RMB-only | currency per record, never per trust; record disclosed FX |
| 17 | Stub periods / forecasts | Centurion FP2025 = 98 days + IPO forecast columns | never annualise; label which column you took |
| 18 | Income model changes meaning | Sasseur EMA: no NPI exists; CLAS: "gross profit" plays NPI's role; master-lease: no occupancy | set profile.income_model; null is structural, explain in _notes |
| 19 | Two valuation sources, two currencies | Daiwa: factsheets value each property in JPY (appraisal), audited Statement of Portfolio in SGD (book) — Opus and Sonnet each picked a different one for all 19 properties | audited reporting-currency figure wins market_valuation; local-ccy appraisal → alt_value with its currency |
| 20 | Partial dates | "Leasehold expiring in March 2067" (Daiwa) — one model invented month-end, the other day 01 | day 01 + note; verbatim stays in tenure_raw |
| 21 | No Portfolio Statement at all | Daiwa has none — per-property data lives in factsheets (JPY) + a parser-scrambled Statement of Portfolio | fall back factsheets + financial review; say in _notes which source replaced the PS |
| 22 | Single-tenant revenue suppression | Daiwa: 11/18 Japan properties redact GR for confidentiality | structural null (industrial/BTS pattern), record once in columns_never_fillable |

## 4. Parser-dialect recovery tactics

- **HTML tables** (`<td>`): grep the value, then read ±40 lines for the row context.
- **Merged columns** (cheap parsers): CLCT's trade-sector table arrived with two lists in
  one cell — recover by splitting on the known segment subtotals and verifying each
  sub-list sums to its subtotal. Generalize: find an internal checksum before trusting a
  mangled table.
- **Split rows across pages**: re-grep the property name; factsheet pages repeat figures.
- **No page markers**: extract anyway with estimated pages + `p_estimated:true`; the
  verification bench tolerates ±2 pages for human lookup.

## 5. Subagent prompt template (one report per agent)

Include, in this order: (1) absolute path to the parsed md + size + marker format;
(2) trust name, symbol, FYE, currency; (3) the 8 output files with field lists (§2);
(4) the conventions block from SKILL.md step 4 verbatim; (5) "prefer audited statements
over highlights; note conflicts"; (6) "FINAL MESSAGE: counts per file + reconciliation
numbers + top 3 schema-fit findings only". Reports are 180–230 pages; agents must Grep
then Read chunks, never read linearly. Expect ~100–200k tokens per report.

## 5b. Lessons from the two-model blind benchmark (Sonnet + Haiku, 3 trusts)

- Cheap models follow **conventions** when told (units, verbatim strings, basis notes)
  but do not acquire **judgment** from instructions: they pick one side of a dual-printed
  figure without surfacing the other, and declare "not disclosed" without exhausting the
  section map. Mitigate with: explicit alt_value requirement, null-needs-proof rule,
  and the mandatory QC gate. Do not rely on a skill alone to upgrade a cheap model.
- Subagent prompts must pin **exact output key names** — both blind runs invented their
  own keys (one encoded units into key names), which breaks programmatic comparison.
- A final-message summary can contradict the agent's own written output; treat the JSON
  file as the deliverable and the message as unverified commentary.
- Opus vs Sonnet (2 unseen trusts, 320 values): interchangeable on accuracy — zero
  hallucinations either side, identical Σ-reconciliations; 41/46 diffs were unpinned
  conventions (valuation source, partial dates, value_basis semantics — since pinned,
  traps #19/#20). Residual errors: Sonnet 5 (nulled printed expiry dates ×3, enum leak
  ×2 — both now QC FAILs), Opus 1 (missed a GLA). Paying for Opus does not buy accuracy
  here; pinned conventions + the QC gate do.

## 6. Blind verification protocol

To verify without anchoring: spawn a fresh agent (no access to prior output or schema
docs) with only the source file + a stratified item list (trust-level block, ~5 properties
× 4 figures, top-3 tenants + basis wording, 2–3 note lines, key transactions). Diff
programmatically with scale tolerance (×1000 unit mismatches are reporting-unit, not
errors). Adjudicate every diff against the source before calling it an error — in the
pilot, 2/2 diffs were the report printing the same fact on two bases (trap #7/#12),
i.e. schema findings, not mistakes.

## 7. Expected fill (don't chase what isn't there)

Per-property: tenure/valuation/occupancy ~95–100%; gross revenue ~80% (misses: First
REIT, KDC, CLAS, MUST, UHREIT); NPI ~35–48% (FCT, KORE, CLCT, Keppel, CLINT, Daiwa,
Suntec only); trade_mix ~10–75% depending on corpus (CICT & Sasseur only, but CICT alone
is 26 properties). Trust-level performance block: 100%. A null in these bands is
structural — record the reason once in `columns_never_fillable`, don't keep hunting.
