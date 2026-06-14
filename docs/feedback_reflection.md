# Reflection on schema feedback — evidence from 9 parsed annual reports

> ⚠️ **HISTORICAL — superseded.** Current operational reference: `docs/pipeline_end_to_end.md`
> (assumption-free + discovery-first). This is an earlier reflection snapshot; do not treat it
> as current guidance.

Response to the review feedback on `reit_schema_proposal.md`, grounded in a re-examination of the
5 originally parsed reports plus 4 newly parsed ones (CapitaLand Ascendas, Frasers Centrepoint,
KORE US, Stoneweg Europe). One more file (Sasseur "FY2024") turned out to be a mis-catalogued
**sustainability report**, not the AR — see Open items.

The expanded sample now covers: integrated commercial (CICT), data centres (KDC), logistics
(MLT), healthcare master-lease (First REIT), hospitality stapled (FEHT), big industrial (CLAR),
pure suburban retail (FCT), US office in USD (KORE), European logistics/office stapled in EUR
(Stoneweg). 9 sectors/structures, 4 currencies, 3 fiscal-year ends.

---

## 1. Terminology (tenure, purchase/effective date, manager/management) — **agree, and the alias dictionary is now seeded**

The feedback is right that these terms are ambiguous and the parser must be told exactly which
figure to take. The same concept appears under different labels per report, and near-identical
labels mean different things:

| Concept | Labels found in the wild | Trap |
|---|---|---|
| Land tenure | "Land Tenure" (CICT, KDC), "Tenure" (CLAR, FCT, Stoneweg PS), "Land title type" (First REIT) | CICT embeds the start date in prose: "Leasehold tenure of 99 years with effect from 21 Nov 2011" |
| Land lease term | "Term of lease" (MLT, KDC, CLAR, FEHT, First REIT) | **"Term of lease" in a portfolio statement = the REIT's land lease, NOT a tenant lease.** MLT also writes "30+30 years" (renewal option). |
| Land lease remaining | "Remaining term of lease" (all), CLAR adds explicit "Lease expiry" date column | Freehold rows carry the literal string "Freehold" in numeric columns |
| Acquisition date | "Date of legal completion" (MLT), "Acquisition date" (First REIT, CLAR, Stoneweg, KORE), FCT/CICT give "Purchase Price in YYYY" / phased stakes | FCT/CICT acquisitions can be **phased** (e.g. NEX 25.5% in 2023 + 24.5% in 2024) — needs to support multiple (date, stake, price) events per property |
| Valuation date | "Latest valuation date" (MLT), "Valuation as at \<date\>" (others), KORE names the valuer (Kroll) | Distinct from acquisition date and from "Agreed Property Value in YYYY" (CICT historical reference) |
| Management entities | REIT Manager / Property Manager(s) (CICT has 3, by asset class) / "Operator" (FEHT SG + Marriott JP) / "Master Lessee" (FEHT, First REIT) / "Entrusted Manager" (Sasseur) | These are different roles with different fee bases — one `manager` column can't hold them. Model as a role-typed link table. |

**Schema delta:** `sgx_reit_properties` gains `land_tenure_type`, `land_lease_term_years`,
`land_lease_expiry_date`, `land_lease_remaining_years` (+ `tenure_raw` for strings like
"Part freehold, Part Right of Superficies" — real example from Stoneweg's Haagse Poort), and an
`sgx_reit_property_events` table for phased acquisitions (event_type: acquisition/divestment/AEI,
date, stake_pct, price, currency). Management roles move to `sgx_reit_entities`
(symbol, role ∈ {reit_manager, property_manager, operator, master_lessee, trustee, sponsor,
entrusted_manager}, entity_name, scope: portfolio or property_id).

Good news: the **audited Portfolio Statement** (an RAP 7 requirement) reliably carries
tenure/term/remaining-term per property in every report that has one, and CLAR/Stoneweg/First REIT
put the acquisition date there too — so this is extractable from the most trustworthy section,
not from marketing pages.

---

## 2. Tenant composition: "two sets, take property level and aggregate" — **half-confirmed; the schema must hold both levels, aggregation only works for one trust**

Verified across all 9 reports:

| Trust | Portfolio-level trade mix | **Per-property trade mix** | Basis |
|---|---|---|---|
| CICT | ✅ | ✅ per-property tables for all 26 properties | % committed GRI, excl. GTO |
| FCT (pure retail!) | ✅ | ❌ (per-mall top tenants only) | % GRI and % NLA |
| CLAR | ✅ per segment-geography | ❌ | % GRI ("customer industry") |
| MLT | ✅ (16 sectors) | ❌ | % gross revenue, March month |
| KDC | ✅ (contract type, hyperscaler %) | ❌ (per-DC top customers, unquantified) | % rental income / lettable area |
| First REIT | ✅ (3 sectors) | ❌ | % rental income |
| Stoneweg | ✅ (12 sectors) | ❌ | % **headline rent** |
| KORE | ✅ (TAMI etc.) | ❌ | % **cash rental income (CRI)** |
| FEHT | n/a (master-lease hotels) | n/a | — |

So the "two sets" observation is correct **for CICT** (and there both sets exist and share the
same basis, so bottom-up aggregation is checkable). Everywhere else only the portfolio set
exists — even FCT, a pure retail REIT, doesn't give per-mall trade mix. Aggregating property →
REIT can't be the pipeline's primary path; it's a **validation bonus** where both levels exist.

**Schema delta:** one table, two scopes —
`sgx_reit_tenant_mix(symbol, fiscal_year, scope ∈ {property, segment, portfolio}, property_id
nullable, category, pct, basis, source_page)`. `basis` is mandatory and an enum
(`gri`, `gri_excl_gto`, `gross_revenue`, `rental_income`, `headline_rent`, `cash_rental_income`,
`nla`) because the 9 trusts use 7 different denominators — cross-REIT comparisons must be
basis-aware or they're wrong. Where both scopes exist (CICT), an `is_derived` flag lets us also
store our computed roll-up next to the disclosed one and diff them.

Same treatment for lease metrics: WALE appears by NLA, by GRI, by CRI, by lettable area, by
rental income — and Stoneweg adds **WALB** (lease-break) as a separate metric. So:
`sgx_reit_lease_metrics(symbol, fy, scope, property_id?, metric ∈ {wale, walb}, basis, years)`.

---

## 3. GRI vs NPI and standardized computation — **agree, with one sharper boundary the data imposes**

The conceptual split (GRI = the property's earning potential → property level; NPI = entangled
with management/financial choices) matches the disclosures almost exactly:

**Per-property gross revenue is broadly available — 7 of 9 trusts disclose it** (CICT, MLT — in
the *audited* portfolio statement with 2 years, FEHT, FCT, CLAR, Stoneweg, KORE; missing only in
First REIT and KDC). **Per-property NPI is rare — 2 of 9** (FCT and KORE only). So
`sgx_reit_property_snapshots` gets `gross_revenue` (expected fill ~78%) and a *nullable*
`npi_disclosed` (~22% fill, stored as-reported, never imputed).

One definitional trap the parser must respect: **"gross revenue" ≠ GRI.** CICT footnotes it
explicitly: gross revenue = GRI + car park + other income; FCT separates GTO rent from base GRI;
KORE's gross revenue is 28% "recoveries income" (US tax/opex reimbursements); Stoneweg's includes
€44m of recoverable service charges; KDC's is ~52% contingent/variable rent. The per-property
figure most reports give is *gross revenue*, not GRI — store it under that name and keep the
component split at REIT level.

**On standardizing computed metrics on our side: fully agree, and the data supports it — at REIT
level.** Every report has an audited Gross Revenue note and Property Expenses note, but the line
items differ exactly as she said ("opt in or opt out a certain particular/item"):

- Utilities: 35% of CLAR's property expenses vs. immaterial for master-lease trusts
- Loss allowance for doubtful receivables: 36% of KDC's property expenses (Guangdong exposure)
- Marketing: retail-only (CICT, FCT)
- Property management fees + reimbursements: separated by FCT (S$14.9m + S$15.5m), bundled elsewhere
- Non-cash straight-lining / lease-incentive amortisation: inside KORE's "other property expenses"
  (their *adjusted* NPI grew 0.3% vs 3.0% reported — the gap is purely accounting)

So the design is: **store raw audited components, compute standardized metrics in our layer.**
Two component tables:
`sgx_reit_revenue_components(symbol, fy, component ∈ {base_rental, turnover_rent, service_charge,
recoveries, car_park, other}, amount)` and
`sgx_reit_property_expense_components(symbol, fy, component ∈ {property_tax, utilities,
maintenance, property_mgmt_fee, mgmt_reimbursement, marketing, staff, insurance_security,
loss_allowance, land_rent, depreciation, other}, amount)`. Standardized NPI, NPI margin,
GRI-only revenue, cost ratios etc. are then **computed, versioned formulas at the API layer** —
same place prod already computes yield/P-NAV for sgx_companies, so it fits house convention.

The boundary: a *standardized* NPI is only computable at **REIT level**, because no trust
discloses per-property expense line items. At property level we can offer gross revenue
(comparable, near-universal) and as-reported NPI (sparse, flagged). That's not a schema weakness —
it's what the disclosure floor allows, and pretending otherwise would fabricate data.

---

## 4. Other findings from the new parses worth carrying into the schema

- **Committed vs actual occupancy** are different numbers (CICT/FCT/KORE report "committed");
  snapshots need an `occupancy_type` qualifier.
- **Concentration risk lives in the notes, not the tables**: KDC's FS note discloses one client =
  $289.1m of $441.4m revenue (~65%) — nowhere in the portfolio review. Add
  `sgx_reit_concentrations(symbol, fy, kind, description, pct, amount, source_page)`.
- **Stapled trusts** mid-restructuring produce odd columns: Stoneweg's BT entity ran only from
  21 May 2025, so its three statement columns cover different periods. `entity_scope` +
  `period_start/period_end` on financial facts (already in the proposal) handles this; flagging
  here as a confirmed real case, not a hypothetical.
- **Retail operational KPIs**: FCT gives per-mall shopper traffic; tenant sales are portfolio-only.
  Goes in the long-tail metric table, scope-aware, not as fixed columns.
- **Per-property purchase price** is disclosed by FCT, CICT, KORE, Stoneweg — supports the
  acquisition-events table rather than a single column.

## 5. Open items for the call

1. **Her CICT per-property NPI source** — the FY2025 AR property pages show gross revenue but no
   per-property NPI. Worth asking where the draft workbook's `net_property_income` values came
   from (an earlier AR year? results slides? estimate?), since that decides whether
   `npi_disclosed` can be backfilled for CICT.
2. **Walkthrough of her term list** (tenure, purchase/effective date, management/manager) against
   the alias dictionary in §1 — the dictionary is seeded from 9 reports but she may have cases
   from the other 30 trusts.
3. **Agree the standardized-formula registry**: which computed metrics, which exact formula, and
   that they live in the API layer (consistent with how prod computes yield/P-NAV) rather than as
   stored columns.
4. **Sasseur**: the catalogued "FY2024 AR" link is actually the sustainability report — re-source
   the real AR (its Entrusted Management Agreement / EMA income model is the single most unusual
   revenue structure among the 39 trusts and should be schema-tested before freeze).
