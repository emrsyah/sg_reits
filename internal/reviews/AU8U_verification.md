# AU8U — CapitaLand China Trust (AU8U.SI) FY2025 — Forensic Extraction Audit

## 1. Method header

Independent verification against source. I navigated the report myself from the TOC and read whole
sections — front-book Highlights/Trust Structure (pp.3,8,17), Operations Review (Gross Revenue p26,
NPI p27, Portfolio Valuation p28, Trade Sector by GRI p31, Top-10 Tenants p32, Lease Expiry / WALE /
Occupancy pp.33-35), the audited financial statements (Statement of Total Return p95, Distribution
Statement pp.96-97, Consolidated Portfolio Statement pp.100-102), the expense Notes 19/20/21 (p148),
Note 22 finance (p149), Statistics of Unitholdings (p174), and Corporate Information (IBC). Page
numbers are the report's own `<!-- PAGE N -->` anchors in the parsed markdown.

I did **NOT** consult `extracted_adapter/*`, any page-map, anchor list, or extraction reasoning.

Source: `parsed_reports_datalab/07_AU8U.SI_CapitaLand-China-Trust_FY2025/full.md`.

---

## 2. Verdict & confidence

**Grade: MINOR ISSUES.**

This is a clean, single-currency-reporting (SGD, with RMB preserved), single-country (China)
diversified REIT extraction and it holds up very well on the hard numbers. The full Statement of
Total Return reconciles to "Total return for the year after taxation" (S$5,573k) to the dollar; every
per-property valuation, gross revenue, NPI and occupancy matches the source exactly; the property
valuation sum ties to the audited Portfolio Statement total (S$4,204,374k); trade_mix sums to 100%;
DPU, distributable income and unitholders all confirm. Unlike the HMN audit, `Σrevenue =
gross_revenue` holds and there is **no** portfolio_value contradiction between `_notes` and
`performance`.

The defects are: (a) one **unsupported management role** — `property_manager` is named as
"CapitaLand Investment Limited", which the report never states (it names only "The Property
Managers"); (b) **systematically wrong `source_page`** on a block of income_components (sub-lines
cited to p95 when they live in Notes 19/20/21 on p148); (c) several **page-anchor drifts** and minor
label/basis omissions (top-tenant GTO/effective-interest basis, JD.com trade sector); (d) a couple of
**unflagged inferences** (lease_term_years lower-bound choice, RMB-to-SGD nature of valuations).

Tally: **CONFIRMED ≈ 40+** · **DISCREPANCY = 5** · **SUSPECTED-OMISSION = 3** · **UNVERIFIABLE = 1**

---

## 3. Discrepancies

### D1 — profile: `property_manager` = "CapitaLand Investment Limited (via subsidiaries...)" is not stated by the report (MED)
- Extraction: `{"role":"property_manager","company_name":"CapitaLand Investment Limited (via subsidiaries as Property Managers)"}`.
- Source: the Trust Structure (p17) and the related-party notes (p148, line "...payable to the
  Property Managers and Project Managers") refer **only** to "The Property Managers" generically — no
  single named entity. CLI is named as the **parent of the Manager** and as **"our Sponsor"** (pp.3,
  771, 4393), never as the property manager. Naming CLI here is an inference the report does not
  support and is not recorded in `_notes.inferred[]`.
- Consequence: a management role attributes an entity the report doesn't assign. Either null with a
  "not named" reason, or flag as inferred. Confidence: HIGH. Severity: MED.

### D2 — income_components: wrong `source_page` for the Note-19/20/21 sub-lines (MED)
- Extraction cites `source_page: 95` for `management_fee_base` (10,300), `management_fee_performance`
  (7,313), `trustee_fees`, `audit_fees`, `valuation_fees`, `finance_income`, `fx_gain_realised`,
  `finance_costs`, and all the adjustment lines; and `source_page: 148` for utilities/maintenance/etc.
- Source: p95 (Statement of Total Return) shows these only **aggregated** ("Other property operating
  expenses (Note 19) 55,430"; "Manager's management fees (Note 20) 17,613"; "Other operating
  (expenses)/income (Note 21) (1,120)"). The disaggregated values the extraction shipped come from
  **Note 19 (utilities … others) on p148**, **Note 20 (base S$10.3m / performance S$7.3m) on p148**
  (text, not p95), and **Note 21 (professional fees 287 / others 833) on p148** (extraction said 149).
  Values are all correct; the citations point at a page that does not contain the disaggregated lines.
- Consequence: provenance fails the "every source_page is a claim" test. Confidence: HIGH. Severity: MED.

### D3 — top_tenants: `pct_basis` understates the disclosed basis; JD.com trade sector (LOW-MED)
- Extraction: `pct_basis: "gri"` for all 10 rows; JD.com → `Departmental Store/Supermarket`.
- Source p32 footnotes: (ii) "**Includes both gross rental income and the gross turnover rental income
  (GTO) components**"; (iii) "**Based on CLCT's effective interest** in each property (51% Xinsu, 80%
  AIH, 80% SHZSTPP I & II)". So the basis is GRI **incl. GTO, on effective-interest** — not plain
  `gri`. JD.com's disclosed trade sector is "**Supermarket / E-Commerce**" (it is primarily a
  logistics/e-commerce tenant); mapping it to Departmental Store/Supermarket drops the E-Commerce
  facet. Confidence: HIGH. Severity: LOW-MED (scope wording + one debatable canonical map).

### D4 — performance: `properties_location` lists cities not all in the portfolio / omits some (LOW)
- Extraction `properties_location`: "China (Beijing, Guangzhou, Chengdu, Hohhot, Harbin, Suzhou,
  Hangzhou, Xi'an, Shanghai, Wuhan, Kunshan)". This is a reasonable city list, but Changsha
  (Yuhuating, divested 31 Oct 2025) is correctly excluded while the list is otherwise complete.
  Cross-check vs the property rows: all 11 cities are represented. No error of substance — flagged only
  because the field is a hand-built string not a single disclosed line. Confidence: MED. Severity: LOW.

### D5 — property_transactions: `sale_price_rmb_m` 813.8 cited to p95, not supported there (LOW; parked)
- Extraction: Yuhuating divestment `sale_price_rmb_m: 813.8`, `source_page: 95`.
- Source: p95 shows only "(Loss)/gain on disposal (11,988)"; the narrative (p7/p11 area) says the
  divestment was at "~4% above the 2024 book value" (RMB785m → ~RMB816m) and exit NPI yield 6.2%. The
  precise RMB813.8m figure is not on p95. The transaction table is **parked (not loaded)**, so low
  impact, but the citation does not support the number. Confidence: MED that the citation is wrong.
  Severity: LOW.

---

## 4. Suspected omissions

### O1 — Per-property WALE, lease-expiry %, and per-mall occupancy disclosed but `lease_expiry_date`/derived lease metrics left null (LOW)
- p34 gives per-retail-property Weighted Average Lease Expiry (by GRI and by NLA) and a 2026 lease
  expiry profile; p35 gives per-mall committed occupancy (already captured). `_notes` declares
  `lease_expiry_date` "derivable but not as-disclosed" — correct (the Portfolio Statement gives only
  remaining-term years). No calendar expiry is disclosed, so the null stands. Flagged only to confirm
  the WALE tables were seen and correctly parked. Severity: LOW (no clean schema home).

### O2 — GFA per sq m disclosed (p28) → per-property GFA derivable; `_notes` says GLA/NLA "not disclosed" (LOW)
- p28 Portfolio Valuation prints "Valuation 2025 (in per sq m of GFA) RMB" for every property
  (e.g. CapitaMall Xizhimen 45,032 RMB/sq m). Combined with the RMB valuation this yields per-property
  GFA. So GFA is **derivable**, not absent — the `_notes.columns_never_fillable` reason for `gla`/`nla`
  ("not disclosed per-property") is over-broad. The value isn't disclosed directly and would be an
  inference, so leaving it null is defensible, but the justification should say "derivable from
  valuation ÷ RMB/sq m, not directly disclosed". Severity: LOW.

### O3 — Geographic GRI mix and asset-class GRI mix (p8) not captured (LOW; correctly no home)
- p8 discloses Geographical Diversification by GRI (Beijing 35.1% / Guangzhou 13.9% / Yangtze Delta
  22.9% / Other 28.0%) and Asset-Class by GRI (Retail 69.3% / BP 27.0% / Logistics 3.7%). These have
  no schema home (not a trade-sector mix) and belong in `data_with_no_home`; they are absent there.
  Minor completeness gap. Severity: LOW.

---

## 5. Reconciliation results (independently re-computed)

### Statement of Total Return tie-out (Group, p95) — PASS (exact)
- Σ(statement="revenue") = 276,794 + 26,926 = **303,720k** = `gross_revenue` ✓ (no HMN-class
  mis-bucketing; "Other income" is genuinely above the Gross-revenue subtotal here).
- Σ(statement="expense") = property tax 27,577 + business tax 1,598 + property mgmt 18,220 + Note19
  55,430 + mgmt base 10,300 + mgmt perf 7,313 + trustee 619 + audit 640 + valuation 99 + professional
  287 + other trust 833 + finance costs 60,076 = **182,992k**.
- Σ(adjustments, signed) = finance income +1,487 + fx gain realised +2,055 − loss on disposal 11,988 −
  fair value IP 50,507 − fair value derivatives 1,122 − fx loss unrealised 73 − taxation 55,007 =
  **−115,155k**.
- 303,720 − 182,992 − 115,155 = **5,573k = "Total return for the year after taxation" (p95) ✓ exact.**
- Note 19 internal sum = 10,576+8,458+20,874+12,471+569+914+43+172+1,353 = **55,430k** ✓ (p148).
- Total property operating expenses = 27,577+1,598+18,220+55,430 = **102,825k** ✓ (p95).
- NPI = 303,720 − 102,825 = **200,895k** = `net_property_income` ✓.
- Manager's mgmt fees = 10,300+7,313 = **17,613k** ✓ (Note 20, p148).
- Note 21 = 287 + 833 = **1,120k** ✓ (p148).

### Property valuation sum → audited Portfolio Statement — PASS (exact)
- Retail 8 rows = **2,971,840k** ✓ (p100 "Balance carried forward").
- Business Parks 5 rows = **981,892k** (p101 BP block 3,953,732 − 2,971,840 ✓).
- Logistics 4 rows = **250,642k** (p102 4,204,374 − 3,953,732 ✓).
- Total active = **4,204,374k** = Portfolio Statement / Note 4 total ✓ = `performance.portfolio_value`
  (4,204,374,000) ✓. RMB'000 sum = 22,981,000 ✓ (p102).

### Per-property gross revenue / NPI → segment & group totals — PASS (exact)
- Gross revenue by property (p26): Retail 216,009 (incl Yuhuating 4,027) + BP 78,392 + Logistics 9,319
  = **303,720k** ✓. Each property's value in properties.json matches p26 to the dollar.
- NPI by property (p27): Retail 141,236 + BP 53,526 + Logistics 6,133 = **200,895k** ✓. Each property
  matches p27, including Yuhuating partial-year 2,531k.

### Trade mix → 100% — PASS
- Retail subcats sum 69.3, BP subcats 27.0, Logistics subcats 3.7 (each = its segment header on p31),
  grand total = **100.0%** ✓. All 26 rows captured. `pct_basis="gri"` correct (p31 "Trade Sector by
  GRI").

### Distribution — PASS
- DPU 1H 2.49c (p96) + 2H 2.33c (declared 5 Feb 2026, p174 area) = **4.82c** ✓ (p96 total; p7
  5-Year Summary). Distributable income **S$83.9m** ✓ (p7 line "Distributable Income (S$ million) …
  83.9"; narrative line 779). ex/pay dates not disclosed in the AR → null correct.

### Unitholders — PASS
- **18,075** unitholders (Statistics of Unitholdings, as at 24 Feb 2026, p174) ✓.

---

## 6. Nulls / inference audit

**Confirmed genuinely absent (correct nulls):**
- `distribution_record[].ex_date` / `pay_date` — the AR discloses only the declaration date
  (5 Feb 2026) and policy ("within 35 market days of record date"); no ex/pay dates. Null correct.
- `properties.lease_expiry_date` — Portfolio Statement gives only remaining-term years, no calendar
  expiry. Null correct (the reason is right).
- `properties.major_tenant` / per-property `trade_mix` — disclosed only at portfolio level (top-10
  tenants p32; trade mix p31). Per-property not disclosed. Nulls correct.
- `properties.effective_date` — land-use-right start dates not disclosed. Correct.
- Yuhuating `market_valuation` / `occupancy_rate` — divested 31 Oct 2025, absent from the 31 Dec 2025
  Portfolio Statement (status="divested"); partial-year P&L correctly retained. Correct.

**Over-broad / improvable null reasons:**
- `gla`/`nla` "not disclosed per-property" → **over-broad** (O2): per-sq-m-of-GFA valuation is on p28,
  making GFA derivable. Reason should say "derivable, not directly disclosed".

**Inferences — reasonableness & unflagged ones:**
- `profile.property_manager = CLI` — **unflagged inference / unsupported** (see D1). The report does
  not name CLI as property manager.
- `properties.lease_term_years` — for multi-parcel malls the extraction set the **lower bound** of the
  disclosed range (Xizhimen "40-50" → 40; Wangjing "38-48" → 38) and put the full range in
  `tenure_raw`. This is a defensible convention and IS described in `_notes.parsing_traps`, but it is a
  derived choice not flagged in `_notes.inferred[]`. Low risk.
- `properties.market_valuation` in SGD — the Portfolio Statement prints both RMB'000 and S$'000
  columns; the extraction took the **disclosed S$'000** column (not a computed conversion), so this is
  disclosed, not inferred. Correct. The `_rmb_valuation_000` audit field matches the RMB column. Good.
- `sub_sector = "Diversified"` — judgment call. Retail is 69.3% of GRI (dominant), but Business Parks
  27% + Logistics 3.7% are material and the trust brands across three physical classes. "Diversified"
  is defensible; "Retail" would also be arguable. Low-confidence, no fix proposed.

---

## 7. Confirmed-correct highlights (balance)

- **Statement of Total Return reconciles to total return (S$5,573k) exactly** — no missing/duplicated
  line; revenue/expense/adjustment buckets are correct (the HMN finance/other-income mis-bucketing is
  absent — `Σrevenue = gross_revenue`).
- **All 17 active + 1 divested property present**, correct country/category, exact 2025 S$'000
  valuations from the audited Portfolio Statement (not the marketing summary), with RMB preserved as an
  audit field; consolidated-100% basis for the 51%/80%-owned assets correctly noted with `_value_basis`.
- **Per-property gross revenue, NPI, and committed occupancy all match the source to the dollar/decimal**
  (pp.26-27,35).
- **Portfolio valuation sum, RMB sum, segment subtotals, trade-mix 100%, DPU split, distributable
  income, unitholders** — every tie-out passes.
- **No portfolio_value contradiction** between `performance` (4,204,374,000) and `_notes` — both use
  the audited Portfolio Statement total; the marketing ~S$4.48bn was correctly avoided (explicit
  parsing trap).
- **Currency discipline**: SGD reporting currency per record, RMB closing/average rates noted
  (closing ~5.466, average 5.499 p33).
- **China land-use-right → Leasehold** for every property ✓ (REFERENCE §3); `tenure_raw` verbatim.
- Trustee (HSBC Institutional Trust Services (Singapore) Limited), Manager (CapitaLand China Trust
  Management Limited), and Sponsor (CapitaLand Investment Limited) correctly named (Corporate
  Information IBC; pp.3, 771, 4393).
- Divestment (Yuhuating 31 Oct 2025) and the Shuangjing (Jan 2024) zero-FY2025 handling correct.

---

## 8. Could NOT verify

- **Per-property GFA in absolute terms** — only RMB/sq m of GFA is printed (p28); deriving absolute
  GFA needs the per-sq-m figure and is an inference, left null. Not directly disclosed.
- **Exact RMB813.8m Yuhuating sale price** — the parked transaction figure is not on the cited p95 and
  I could not locate an exact RMB sale-price line in the parsed markdown (narrative gives only "~4%
  above 2024 book value" and exit NPI yield 6.2%). Parked field; flagged as unverifiable from the parse.

---

### Concise fix list (file → field → correct value → page)

| File | Field | Issue / correct value | Page |
|---|---|---|---|
| profile.json | management[property_manager] | Report never names CLI as property manager — set to null with reason "only 'The Property Managers' (project-company subsidiaries) named; no single entity disclosed", OR record as an `_notes.inferred[]` entry | p17 / p148 |
| income_components.json | source_page (mgmt base/perf, trustee, audit, valuation, finance income, fx gain, finance costs, all adjustments) | should cite **p148** (Notes 19/20) and **p95** STR respectively; Note 21 lines cited p149 → **p148** | p95, p148 |
| top_tenants.json | pct_basis (all rows) | "gri incl. GTO, on CLCT's effective interest" (not plain "gri") | p32 (fn ii, iii) |
| top_tenants.json | rank 1 trade_sector | JD.com disclosed as "Supermarket / E-Commerce" — consider Logistics/E-Commerce facet, not only Departmental Store/Supermarket | p32 |
| _notes.json | columns_never_fillable[gla/nla] reason | reword: GFA derivable from p28 RMB/sq m ÷ valuation, "not directly disclosed" (not "not disclosed") | p28 |
| _notes.json | inferred[] | add `lease_term_years` lower-bound-of-range convention | p100-102 |
| property_transactions.json | sale_price_rmb_m source_page | 813.8 not supported on p95; correct/flag the citation (parked) | — |

No financial values require correction — all numbers reconcile to the source.
