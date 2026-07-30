# `sgx_reit_property.gross_revenue` — what is it actually?

Question raised 2026-07-30: is the per-property `gross_revenue` column really **gross revenue**
(rent + car park + recoveries + other income) or is it **gross rental income** (rent only)? If it is
rental-only we rename the column; if not we need to normalise, tag, or drop it.

All 37 REITs checked against `parsed_reports_datalab/`, cross-referenced with our own extraction
flags and `_notes.json`. Fill rate: **2,966 of 3,420 rows (86.7%)** — by far the best-populated
property metric (property-level NPI is only 10.8%).

---

## Answer: it is not one thing. There are four revenue bases, plus two orthogonal problems.

**Renaming the column to `gross_rental_income` would be factually wrong for the majority of REITs.**

---

## 1. True GROSS REVENUE — rent + non-rental income (majority)

Each verified against an audited note whose components sum exactly to the per-property table total.

| REIT | AR's own definition |
|---|---|
| **C38U** | *"Gross revenue comprises **GRI, car park income and other income**"* — footnote on every property card. Note 21: GRI 1,514,171 + Car park 40,243 + Other 64,760 = 1,619,174 |
| **A17U** | *"Includes **gross rental income, car park income and other income**"* — repeated footnote |
| **M44U** | Note 3: Rental income + Service charges + Other operating income; *"other operating income mainly includes **car park income and sale of electricity generated from solar panel**"* |
| **BUOU** | Note 3: Rental 383,348 + **Recoverable outgoings** 87,523 + Other 615 = 471,486 |
| **AU8U** | Gross rental income 276,794 + Other income 26,926 = 303,720; *"Based on 100.0% stake"* |
| **BMOU** | Gross rental income 49,779 + Other income 5,327 = 55,106 |
| **D5IU** | Note 4: Rental 108,178 + **Car park 6,566** + **Service charge and utilities recovery 78,644** + Other 1,171 = 194,559 |
| **P40U** | Note 17: Property rental 186,870 + **Turnover rental 2,240** + Other 2,987 = 192,097 |
| **N2IU** | Note 3: GRI 819,556 + **Car parking 25,160** + Other operating 64,125 = 908,841 |
| **CY6U** | Base rent + *"Operations, maintenance and utilities income"* + *"Car park and other operating income"* |
| **CMOU** | Rental + **Recoveries** + Other operating — per-property sum matches Note total exactly (150.2m) |
| **OXMU** | Rental + **Recoveries** + Other operating (incl. parking) — sums exactly to 133.3m |
| **JYEU** | Rental + **turnover rent** + other property income *"includes car park income"* |
| **DCRU** | Rental 110,312 + Colocation 9,538 + **Utilities reimbursements 36,611** + Other recovery 19,691 |
| **SET** | Lease revenue 167,489 + **Service charge 42,330** + Other property revenue 3,100 |
| **AJBU** | *"**Attributable** Gross Revenue"* — Rental 305,696 + Other 4,591. **Proportionate, not 100%** |
| **Q5T** | Master lease rental + Retail/office revenue + Hotel revenue + **Carpark** and other income |
| **T82U** | Gross rental income 470,899 of 471,606 total — technically gross revenue but **~99.8% rent** |

**Not one REIT excludes car park income** where it is itemised. The exclusions found were of
*gross turnover rent* and *JV revenue* — see §4.

## 2. True GRI — rent only

| REIT | AR wording |
|---|---|
| **UD1U** | per-property *"Gross Rental Income (€ million)"*. Note 3.2 confirms REIT-level = Rental 39,119 + Service charge 8,412 + **Carpark 2,626** + Other 277 = 50,434 |
| **M1GU** | per-property GRI sums almost exactly to the audited *"Property rental income"* line (72,961), while REIT-level adds *"Other operating income"* 40,347 |
| **C2PU** | *"Based on gross rental per annum, **excluding C-Tax and other income**"* |
| **DHLU** | *"GRI based on **monthly rent** as at 31 December"* |
| **AW9U** | *"Rental Income"*, *"Without FRS 116 Adjustment on rental straight-lining"* |
| **8C8U** | *"Gross Rental Income for FP 2025"* |
| **MXNU** | per-property *"Gross Rental Income"*; REIT-level adds *"Other property income"* £1,715k, disclosed only at portfolio level |

## 3. Two further bases

**Hotel operating revenue** — **XZL**: per-property *"Revenue"* is stapled-group hotel operating
revenue. Its master leases are internal (REIT → BT) and eliminated on consolidation, so no
arm's-length rental figure exists per property.

**Mixed within one REIT — needs a ROW-level tag, not a per-REIT one:**

- **HMN**: *"Gross Rental Income"* for master-leased assets, *"Hotel Revenue"* for
  management-contract assets, in the same table
- **J85**: *"Gross Rental Revenue"* vs *"Gross Hotel Revenue"*, split by lease structure

**A misnomer — CRPU (Sasseur):** the REIT earns **"EMA rental income"** (Fixed + Variable) from the
Entrusted Manager under the Entrusted Management Agreement; the Entrusted Manager bears all
operating costs and retains the outlet's actual gross revenue (*"GR = Total rental receivable +
Income from permissible investments"*), which is disclosed **nowhere** per outlet. The only
per-outlet dollar figure is Note 23 segment *"EMA rental income"*. Storing that as `gross_revenue`
is a misnomer even though the total reconciles at 1.000.

---

## 4. The bigger problem: ownership basis is inconsistent, sometimes WITHIN one REIT-year

This is independent of the GRI question and explains every ratio above 1.0 (per-property sum vs
REIT-level figure).

| REIT | ratio | mechanism |
|---|---|---|
| **J69U** | **1.61 / 1.56** | Mall pages report JV malls (NEX, Waterway Point, Northpoint City South Wing) at *"100.0% basis"* though FCT holds 50%, while the audited Group total **excludes those JVs entirely** (equity-accounted). Second, smaller mismatch: mall pages *"exclude gross turnover rent"*, Group Note 18 includes it. |
| **DCRU** | **1.50** | Our own flag: *"Digital Osaka 3 — gross_revenue = 'Revenue for the year' at **100% (associate entity level)** ... NOT at the Group's 20% ownership share (**unlike sibling consolidated properties whose gross_revenue is at ownership share**)"* |
| **TS0U** | **1.25** | OUE Bayfront at *"100% interest"* of the LLP; One Raffles Place at *"81.54% interest"* of OUB Centre — **neither matches TS0U's true effective interest** (50% and 67.95%), and neither is in the consolidated Note 17 total |
| **ME8U** | **1.17** | Per-property table includes 13 North America JV data centres at *"MIT's 50% interest"*, but audited Note 3 Group Gross Revenue **excludes MRODCT entirely** |
| **C38U** | 1.01 / 1.06 | Mixed within the REIT: CapitaSpring *"on 45.0% basis"*, ION Orchard *"on 50.0% basis"*, CapitaSky *"100% basis"* though CICT owns 70% |
| **BMOU** | 1.000 | Beijing Wanliu at 100% though the Trust owns 60.0% |
| **AJBU** | 0.98 | Explicitly *"**Attributable** Gross Revenue"* — proportionate by design |
| **K71U** | 1.000 | One Raffles Quay and MBFC (33.3% associates) **structurally excluded** — no revenue figure disclosed for them anywhere, only attributable NPI |

**Consequence: summing `gross_revenue` across a REIT's properties is not currently a valid
operation**, regardless of the rental-vs-total question.

## 5. And a third axis: period

- **DHLU**: *"GRI based on **monthly rent as at 31 December**"* — a point-in-time monthly figure
- **C38U, D5IU, N2IU** etc.: full financial year
- **MXNU**: *"**annualised** gross rental income"*

Same problem as `pct_basis`. Even the GRI values are not mutually summable.

---

## 6. Ratios below 1.0 — all explained, no data wrong

| REIT | ratio | explanation |
|---|---|---|
| **DHLU** | 0.61 / 0.69 | **Tenant confidentiality**, stated in the AR: *"Not disclosed for properties with one tenant as DHLT is bound by confidentiality obligations ... these tenants did not consent to the disclosure of the gross rental income attributed to their tenancies."* |
| **M1GU** | 0.64 / 0.66 | Per-property GRI vs REIT-level total revenue — genuine basis difference (§2) |
| **UD1U** | 0.83 | Per-property rental component only; REIT-level adds service charge + carpark + other (§2) |
| **C2PU** | 0.83 | Per-property excludes C-Tax and other income by definition (§2) |
| **K71U** | 1.000 on 9 of 29 rows | ORQ/MBFC excluded from Property income entirely |
| **SET** | 0.99 / 0.96 | Full coverage (95 properties) — see §7 |

## 7. Coverage: two verdicts

- **ODBU — correctly empty.** Its audited Portfolio Statement carries only fair value and % of net
  assets; no per-property income figure exists anywhere in either year. Our 0 of 44 rows is right.
- **J91U — OPEN PROVENANCE QUESTION.** Our own `_notes.json` says *"Per-property gross revenue not
  disclosed; only country-segment level (Note 33, p223)"*, and the FY2025 per-property tables show
  **valuation only**. Yet **68 FY2025 rows are populated** (Singapore 48, Australia 18, Japan 2).
  The Singapore values are all round to 0.1 (0.5m, 3.5m, 34.2m) while Australian ones are exact
  (773,730) — suggesting a S$-million source for one and a note for the other. **Needs
  investigation before these 68 values are trusted.**

---

## 8. Recommendation

**Do not rename. Do not attempt to normalise. Tag instead.**

1. **`gross_revenue` is already the correct name** for ~19 of 37 REITs, which genuinely disclose
   gross revenue per an audited note. Renaming to `gross_rental_income` would make those wrong.
2. **GR → GRI conversion is not possible as-disclosed.** It needs the car park / recoveries / other
   income split per property. No AR publishes that at property level — C38U gives the *definition*
   but never the split. Any conversion would be an estimate, which breaks the as-disclosed rule
   (REFERENCE §0.8).
3. **Dropping it costs the best-populated column in the table** (86.7% vs NPI's 10.8%).

**Proposed: three tags, all as-disclosed, no value changes.**

| tag | values | why |
|---|---|---|
| `gross_revenue_basis` | `gross_revenue` · `gri` · `hotel_revenue` · `ema_rental_income` | §1-3. **Must be per-row** — HMN and J85 mix bases inside one portfolio |
| `gross_revenue_ownership_basis` | `100pct` · `proportionate` · `attributable` | §4. The larger comparability problem |
| `gross_revenue_period` | `full_year` · `month_december` · `annualised` | §5 |

This keeps every figure verbatim and tells consumers exactly when a cross-REIT or intra-REIT sum is
invalid — which is currently invisible.

**Also fix, independent of the tags:**
- **DCRU FY2025 Digital Osaka 3** — restate to the Group's 20% share to match its siblings, or tag it.
- **J91U** — resolve the provenance question in §7.
- **CRPU** — relabel as `ema_rental_income`; it is not gross revenue in any sense.

---

## 9. Verification-process note

The sub-agents produced good cited evidence but generated **four false "no table exists" findings**
across this and the `pct_basis` work — AJBU, J85, and SET (agent claimed only Top-10 properties
disclosed; our own note says *"SUPERSEDED — WRONG. Per-property gross revenue IS disclosed ... in
all 9 country asset-summary tables pp.80-90 ... Filled for all 95 active properties"*). Each would
have deleted valid data. The failure mode is consistent: find one table, conclude no others exist.

**Rule going forward: never act on an agent NOT_FOUND without a human grep, and check our own
`_notes.json` first — it frequently already records the answer.**
