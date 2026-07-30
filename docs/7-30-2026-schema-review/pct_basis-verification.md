# `pct_basis` — source verification log

Verifying every `pct_basis` value in `sgx_reit_top_tenant` and `sgx_reit_trade_mix` against the
annual reports in `parsed_reports_datalab/`. Started 2026-07-30.

**Method note:** the first round of sub-agents each spawned their own sub-agents and lost citation
fidelity — one returned findings it admitted were not verbatim (and one of those was wrong), two
returned nothing at all. Everything in the CONFIRMED table below was re-read directly from the
report files. Later rounds forbid delegation.

---

## CONFIRMED — read directly from the reports

### Real cross-table basis differences (correct as stored — do NOT normalise these away)

| REIT | FY | top_tenant | trade_mix | AR wording |
|---|---|---|---|---|
| D5IU | 2024, 2025 | `gri` OK | `gross_revenue` OK | *"Top 10 Tenants **by % of Gross Rental Income**"* (L1112/1113) · *"Trade Sector Breakdown **by Gross Revenue**"* (L1142) |
| C2PU | 2024, 2025 | `gross_revenue` OK | `asset_value` OK | *"Based on Gross Revenue as at 31 December 2025"* · *"PORTFOLIO SUMMARY BY ASSET VALUE"*. No literal "trade mix" table exists in either year; the asset-value split (Hospitals/Medical Centres vs Nursing Homes) is the analogue. |
| DHLU | 2024, 2025 | `npi` OK | `gri` OK | table header literally `% of NPI` (L2230) · prose: *"the top tenant contributed 24.5% of the DHLT Portfolio's **NPI** for FY2025"* (L2226) |
| A17U | 2024 | `gross_revenue` OK | `gri` OK | *"Top 10 Customers of CLAR by **Monthly Gross Revenue**"* (FY2024 L2076, FY2025 L2184) · *"industry mix of customers by **gross rental income**"* (FY2024 L2968) |

**Consequence:** `pct_basis` must stay **per-table**. `npi` and `asset_value` are legitimate
disclosed bases, not mislabels.

### Confirmed WRONG — extraction mislabels

| REIT | FY | table | stored | AR actually says | should be |
|---|---|---|---|---|---|
| UD1U | 2025 | both | `rental_income` | *"1 As a percentage of total **gross rental income**"* (L1631; the footnote covers both "TOP 10 TENANTS" L1583 and "TRADE SECTORS" L1610) | `gri` |
| A17U | 2025 | trade_mix | `rental_income` | *"industry mix of customers by **gross rental income**"* (L3700) — same wording as FY2024 | `gri` |
| BUOU | 2025 | both | `gri` (single) | *"Top 10 L&I Tenants of FLCT **by GRI**"* (L1678) + *"Top 10 Commercial Tenants of FLCT **by GRI**"* (L1703) + segment-split *"Portfolio tenant sector breakdown by GRI"* (L1724) | `gri_logistics_industrial` + `gri_commercial` |
| T82U | 2025 | both | `gri` (single) | *"Office Portfolio Business Sector Analysis"* (L961) + *"Retail Portfolio Business Sector Analysis"* (L984), both by GRI | `office_gri` + `retail_gri` |

**BUOU/T82U are extraction regressions, not AR changes** — both reports carry the same segment
structure in FY2025 as FY2024.

**The denominators genuinely differ per segment.** T82U FY2025 L1009-1011: *"The top 10 tenants of
the office portfolio contributed 20.0% of Suntec REIT's total **office** gross rental income"* vs
*"15.0% of Suntec REIT's total gross **retail** income"*.

> **This reverses the earlier recommendation** in `findings-and-recommendations.md`, which proposed
> collapsing `office_gri` / `retail_gri` / `gri_commercial` / `gri_logistics_industrial` into plain
> `gri`. That would be wrong: each segment's percentages are a share of *its own* segment income and
> each set sums to ~100%, so a single label would make the two sets appear to sum to 200%. The fix
> runs the other way — bring FY2025 up to FY2024's per-segment basis.

### Other observations

- **D5IU discloses its top 10 twice** — *"by % of Gross Rental Income"* (L1112) and *"by % of NLA"*
  (L1127). We store only the GRI version. Correct choice, but some REITs offer a second basis we are
  silently selecting between.
- **A17U has multiple sector donut charts** (per geography/segment: Singapore, Australia, US). The
  basis is consistently GRI across them, but whether our single trade_mix row set represents the
  whole portfolio or one geography is a separate open question.

---

## IN PROGRESS

| batch | REITs | status |
|---|---|---|
| non-GRI | HMN, CMOU, OXMU, K71U, SET, CRPU, AJBU, AW9U, CY6U, DCRU, Q5T, XZL | running |
| GRI batch A | 8C8U, AU8U, BMOU, BTOU, C38U, J69U, J85, J91U, JYEU | running |
| GRI batch B | M1GU, MXNU, O5RU, ODBU, P40U, TS0U, ME8U, N2IU | running |

### Open questions these batches must answer

1. **Is `rental_income` a real basis at all?** Two of two checked so far (UD1U, A17U FY2025) turned
   out to be *gross* rental income mislabelled. Six more REITs carry `rental_income`
   (AJBU, AW9U, CY6U, DCRU, Q5T, XZL) — if they go the same way, the value largely disappears from
   the enum.
2. **Is HMN's prose qualifier** — `rental_income (corporate accounts of properties under Ascott
   management contracts only)` — genuinely part of the disclosed basis, or invented by us? And did
   the basis really change between FY2024 (`apartment_rental_income`) and FY2025 (`rental_income`)?
3. **Any more per-segment splits** hiding under a single `gri` (C38U, J69U, N2IU, TS0U are
   candidates)?
4. **Any REIT disclosing tenant concentration by NLA** rather than income, tagged `gri`?
5. **Q5T and XZL coverage** — we have FY2025 rows but no FY2024. Do those tables exist in the FY2024
   reports? And does XZL have a trade-mix table at all (we have tenants but zero trade-mix rows)?

## Then, and only then

Propose the canonical `pct_basis` enum. The shape depends on answers 1-4 — in particular whether the
segment-specific values must be **kept and extended** (per the BUOU/T82U finding) rather than
collapsed, and how many `rental_income` values survive.
