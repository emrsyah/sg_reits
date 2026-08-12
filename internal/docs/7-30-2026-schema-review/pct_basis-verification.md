# `pct_basis` — source verification, COMPLETE

Every `pct_basis` value in `sgx_reit_top_tenant` (752 rows) and `sgx_reit_trade_mix` (509 rows),
verified against the annual reports in `parsed_reports_datalab/`. Completed 2026-07-30.
All 37 REITs / 74 REIT-years covered.

**Method note.** The first round of sub-agents each spawned their own sub-agents and lost citation
fidelity — one returned findings it admitted were not verbatim, two returned nothing. Round two
forbade delegation and produced properly cited results. **Every NOT_FOUND and every
"our rows shouldn't exist" claim was then re-checked by hand, and 2 of them were false** (see
§5). Treat agent NOT_FOUND verdicts as unproven until a human grep confirms them.

---

## 1. The canonical enum — 12 bases + 4 segment variants

All verified verbatim in at least one AR. `rental_income` is **not** one thing; it was being used
as a catch-all for five distinct metrics.

| value | AR wording | REITs |
|---|---|---|
| `gri` | "gross rental income" / "GRI" | the bulk — 8C8U, AU8U, BMOU, BTOU, C38U, J69U, J85, J91U, JYEU, M1GU, MXNU, ME8U, N2IU, O5RU, P40U, TS0U, D5IU (tenant), DHLU (trade), A17U (trade), ODBU FY2025 |
| `gross_revenue` | "Gross Revenue" / "Monthly Gross Revenue" | A17U (tenant), C2PU (tenant), CRPU (both), D5IU (trade) |
| `rental_income` | plain "Rental Income" — genuinely not *gross* | AJBU, AW9U, HMN |
| `rental_revenue` | "By Rental Revenue" | CY6U |
| `annualised_rent` | "Annualised Rent" — Dec GRI x 12 | DCRU |
| `revenue` | "Percentage of Revenue" | Q5T, XZL |
| `base_rental_income` | "base rental income" | ODBU FY2024 |
| `cash_rental_income` | "Cash Rental Income (CRI)" = "rental income without recoveries income" | CMOU, OXMU |
| `committed_gross_rent` | "Total Committed Monthly Gross Rent" | K71U |
| `headline_rent` | "% of total headline rent" | SET |
| `npi` | table header literally `% of NPI` | DHLU (tenant) |
| `asset_value` | "PORTFOLIO SUMMARY BY ASSET VALUE" | C2PU (trade) |
| `apartment_rental_income` | "% of Total Apartment Rental Income" | HMN FY2024 (tenant) |
| **segment variants** | | |
| `gri_logistics_industrial` / `gri_commercial` | "Top 10 L&I Tenants of FLCT by GRI" / "Top 10 Commercial Tenants ... by GRI" | BUOU |
| `office_gri` / `retail_gri` | "Office Portfolio Business Sector Analysis" / "Retail ..." | T82U |

### The segment variants must be KEPT and EXTENDED, not collapsed

This **reverses** the recommendation in `findings-and-recommendations.md`. T82U FY2025 L1009-1011:

> *"The top 10 tenants of the office portfolio contributed 20.0% of Suntec REIT's total **office**
> gross rental income ... For the retail portfolio ... 15.0% of Suntec REIT's total gross **retail**
> income"*

Separate denominators. Each segment's percentages sum to ~100% within that segment, so one shared
label would make the two sets appear to sum to 200%.

---

## 2. Confirmed mislabels — 19 rows-worth across 9 REIT-years

| REIT | FY | table | stored | AR says | fix to |
|---|---|---|---|---|---|
| UD1U | 2025 | both | `rental_income` | *"As a percentage of total **gross rental income**"* (L1631, footnote covers both tables) | `gri` |
| A17U | 2025 | trade_mix | `rental_income` | *"industry mix of customers by **gross rental income**"* (L3700) — same as FY2024 | `gri` |
| CY6U | 2024, 2025 | both | `rental_income` | *"Tenant Core Business (By **Rental Revenue**)"*; header `Top 10 Tenants \| Rental Revenue` | `rental_revenue` |
| DCRU | 2024, 2025 | both | `rental_income` | *"Based on **annualised rent** ... computed based on the gross rental income for December 2025 multiplied by 12"* (L1645) | `annualised_rent` |
| Q5T | 2025 | both | `rental_income` | *"Percentage of **Revenue**"*; *"Trade Sector Mix of Tenants by **Revenue** (%)"* | `revenue` |
| XZL | 2025 | top_tenant | `rental_income` | *"Percentage of **Revenue** in FY2025"* | `revenue` |
| ODBU | 2024 | both | `gri` | *"Based on **base rental income** of Grocery & Necessity Properties for the month of December 2024"* (fn 5); *"Based on **base rental income** for the month of December 2024"* (fn 7) | `base_rental_income` |
| BUOU | 2025 | both | `gri` single | two segment tables, both *"by GRI"* (L1678, L1703) | `gri_logistics_industrial` + `gri_commercial` |
| T82U | 2025 | both | `gri` single | *"Office Portfolio Business Sector Analysis"* (L961) + *"Retail ..."* (L984) | `office_gri` + `retail_gri` |

**ODBU is the subtle one:** FY2024 says "base rental income", FY2025 says "gross rental income" for
the same two tables. The disclosure genuinely changed, so FY2025's `gri` is right and only FY2024
needs fixing.

**BUOU/T82U are extraction regressions, not AR changes** — both reports carry the same segment
structure in both years.

---

## 3. Confirmed correct as stored — real cross-table differences

Do **not** normalise these; the AR genuinely uses different denominators for the two tables.

| REIT | top_tenant | trade_mix | evidence |
|---|---|---|---|
| D5IU | `gri` | `gross_revenue` | *"Top 10 Tenants by % of Gross Rental Income"* (L1112) / *"Trade Sector Breakdown by Gross Revenue"* (L1142) |
| C2PU | `gross_revenue` | `asset_value` | *"Based on Gross Revenue as at 31 December 2025"* / *"PORTFOLIO SUMMARY BY ASSET VALUE"*. No literal trade-mix table exists; the asset-value split is the analogue. |
| DHLU | `npi` | `gri` | header `% of NPI` (L2230); *"the top tenant contributed 24.5% of the DHLT Portfolio's NPI"* (L2226) |
| A17U | `gross_revenue` | `gri` | *"Top 10 Customers of CLAR by Monthly Gross Revenue"* (L2184) / *"industry mix of customers by gross rental income"* |

**HMN's prose qualifier is real and the year-over-year change is real.** FY2024 header is *"% of Total
**Apartment** Rental Income"*, FY2025 is *"% of Rental Income"*, both footnoted *"Based on rental
income from corporate accounts of properties under Ascott management contracts only."* We did not
invent it.

---

## 4. `gri` is not homogeneous — scope caveats

Every one of these is correctly labelled `gri`, but the denominators are not comparable
cross-REIT. Worth surfacing rather than hiding.

| REIT | caveat |
|---|---|
| J85 | *"FOR PROPERTIES WITH EXTERNAL LEASES"* — excludes management-contract hotels (W Hotel, Japan/Perth Hotels, etc.) and the self-operated Lowry |
| ODBU | scoped to Grocery & Necessity properties only (excludes the 2 Self-Storage assets); single-month December snapshot |
| C38U | GRI *"includes service charge, advertising & promotional charge ... excludes gross turnover rent"* |
| AU8U | *"Includes both gross rental income and the gross turnover rental income (GTO) components"* — opposite of C38U |
| TS0U | December month only, *"excluding retail turnover rent"* |
| MXNU | *"annualised gross rental income as at 31 December"* |
| BMOU, AU8U, O5RU | month-of-December vs full-year GRI varies (O5RU: *"Based on full year GRI"*) |
| AW9U | *"Before recognition of FRS 116 rental straight-lining adjustments"* |
| HMN | corporate accounts of Ascott-managed properties only |

Two REITs include gross turnover rent and two explicitly exclude it, on the same `gri` label.

---

## 5. Agent false negatives — caught by hand

Both would have caused valid data to be deleted.

| claim | reality |
|---|---|
| **AJBU has no top-10 table in either year; rows should not exist** | FALSE. L2385: *"#### TOP 10 CLIENTS BY RENTAL INCOME (%) as at 31 December 2025"*, first row `Fortune Global 500 Company (Hyperscaler) \| 42.1`, matching our stored 0.421. `rental_income` is correct. The anonymised client names are Keppel DC's own redaction. |
| **J85 NOT_FOUND for both tables, both years** | FALSE. L1226: *"TOP 10 TENANTS BY GROSS RENTAL INCOME FOR PROPERTIES WITH EXTERNAL LEASES"*, column *"% of Total Gross Rental Income"* — 24.2% / 20.3% / 11.0% / 8.2% / 6.8% match our stored values exactly. Trade mix at L1207: *"COMPOSITION OF GROSS RENTAL INCOME FOR PROPERTIES WITH EXTERNAL LEASES"*. Both `gri`, correct. |

Our J85 trade_mix "Hospitality & Leisure 92.0%" = the AR's Hotel 90.3% + Living Assets 1.7% — a
deliberate taxonomy merge, not an error.

**Genuine NOT_FOUND (verified):** XZL trade_mix, both years — no such table exists; XZL has 3
internal master lessees all tagged Hospitality, so there is nothing to break out. Our zero rows are
correct.

---

## 6. Dual-basis disclosures — 6 REITs publish the same table on two bases

The AR gives both an income-basis and an NLA-basis version; we store only the income one. There is
currently no slot for the second.

| REIT | bases disclosed | form |
|---|---|---|
| D5IU | GRI + NLA | two separate charts (L1112, L1127) |
| CMOU | CRI + Committed NLA | two parallel charts, every year |
| JYEU FY2024 | GRI + NLA | two separate tables (L1584, L1559) and two top-10 charts (L1615, L1634) |
| J69U FY2024, FY2025 | GRI + NLA | **both columns in one table** (L1547/1580, L1578/1603) |
| BMOU FY2024, FY2025 | GRI + NLA | two separate donuts with distinct footnotes |
| AU8U FY2025 | GRI + Committed NLA | both columns per mall (L2350+) — FY2024 was GRI-only, so the AR's format changed |

Decision needed: capture the NLA basis as additional rows (`pct_basis = 'nla'`), or document that we
deliberately store income-basis only.

---

## 7. Extraction coverage gaps found (not basis issues)

| REIT | FY | issue |
|---|---|---|
| Q5T | 2024 | *"Top 10 Commercial Premises Tenants"* and *"Trade Sector Mix of Tenants by Revenue"* exist at L2072-2093. **Zero rows loaded.** |
| XZL | 2024 | top-tenant table exists at L197 (*"Percentage of Revenue in FY2024"*). **Zero rows loaded.** |

Both were assumed to be missing-from-AR; they are extraction misses.

---

## 8. Recommendations

1. **Adopt the 12-value enum + 4 segment variants** in §1. Reject the earlier proposal to collapse
   segment variants into `gri`.
2. **Apply the 9 mislabel fixes** in §2 (19 rows).
3. **Keep `pct_basis` per-table** — §3 proves the two tables legitimately differ.
4. **Split HMN's prose qualifier** into a separate `pct_basis_note` column; keep the enum value
   clean. Same for AW9U's FRS 116 note and ODBU's segment scope.
5. **Decide on the NLA second basis** (§6) — capture or explicitly document as out of scope.
6. **Backfill Q5T FY2024 and XZL FY2024** (§7).
7. **Consider a `pct_basis_period` field** (`full_year` / `month_december` / `annualised`) — §4 shows
   `gri` mixes all three, and that difference is invisible today.
