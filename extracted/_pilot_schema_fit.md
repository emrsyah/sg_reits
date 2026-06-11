# Pilot extraction — schema fit report (3 trusts vs `sgx_reit_schema_final.md` v1.1)

Trusts: CICT (C38U.SI, 199pp), FCT (J69U.SI, 222pp), CLCT (AU8U.SI, 180pp) — FY2025.
Output: `extracted/<symbol>_FY2025/{profile,performance,properties,property_transactions,
top_tenants,trade_mix,income_components,_notes}.json`, every value carrying `source_page`.

## 1. Reconciliation (the agreement-rate check) — all three pass

| Trust | Σ per-property gross revenue vs reported | Σ per-property NPI vs reported | Properties |
|---|---|---|---|
| CICT | S$1,619.3m vs S$1,619.174m (rounding only) | n/a — no per-property NPI disclosed | 26 |
| FCT | $389,603k vs $389,603k (exact) | $277,980k vs $277,980k (exact) | 9 + 2 JV |
| CLCT | RMB1,670,000k / S$303,720k (exact, dual-ccy) | RMB1,104,635k / S$200,895k (exact) | 17 + 1 divested |

FCT's parse produced duplicate conflicting rows for 4 malls; only one set summed to the
audited totals — **the reconciliation check caught a real parsing error**, validating §F.

## 2. Fill rates (56 property rows, 3 performance rows)

Performance: **12/12 schema fields filled 3/3** (incl. distribution_record with periods).

Property columns:

| Band | Columns |
|---|---|
| 100% | identity block, land_tenure, tenure_raw, status, source_page |
| 85–98% | ownership, currency, valuation, valuation_date, occupancy, gross_revenue, major_tenant, nla |
| 57–83% | lease_term_years 83%, trade_mix 75% (CICT+CLCT property-level), gla 67%, effective_date 57% |
| 30–48% | net_property_income 48% (FCT+CLCT disclose; CICT doesn't), lease_expiry_date 32%, RMB dual-ccy fields 30% (CLCT only — structural) |

**No column fell below the ~20% drop threshold** (the 1% `purchase_price_note` is an
extractor artifact, not schema). The two priors held: per-property NPI is as-disclosed-only
(CICT has none), property-level trade_mix exists where expected.

## 3. Data with no home — 36 items, heavily clustered

| Cluster | Seen in | Verdict |
|---|---|---|
| **Capital management block**: aggregate leverage, cost of debt, ICR, total borrowings, NAV/unit, total assets, debt maturity | **3/3 trusts** | strongest add candidate — MAS-mandated, always disclosed. Add ~6 typed columns to `sgx_reit_performance` |
| WALE (by GRI and/or NLA, portfolio + segment) | 3/3 | add candidate — needs `basis` if added |
| Rental reversion %, occupancy cost, tenant sales / shopper traffic | 2/3 | hold one more round; candidates for a small `extras jsonb` on performance |
| Perpetual securities (issued/redeemed) | 2/3 | extras jsonb / later |
| Units in issue, market cap | 3/3 | **not added** — prod `sgx_daily_data` (discussion #2) |
| FX rate disclosed (CLCT 5.499) | 1/3 | record in `_notes` for now; becomes a column only when more non-SGD trusts enter |
| Segment NPI (CICT), cap-rate ranges, valuer second opinions | 1–2/3 | parked |

## 4. Schema gaps the pilot actually exposed (not in the contradictions list)

1. **Combined-line / property-group disclosure** — CICT reports Bugis+ & Bukit Panjang
   Plaza only as a merged "Other Assets" line; FCT's audited Portfolio Statement splits
   Northpoint City into two wings while income/NLA are combined. The schema has no way to
   say "this figure belongs to a group of rows." Cheapest fix: nullable
   `property_group` text on `sgx_reit_property`; group-level figures attach to one row
   per group, members reference it.
2. **Ownership/consolidation basis on property figures** — JV properties (FCT NEX &
   Waterway Point; CICT ION) are disclosed at 100% basis but sit OUTSIDE reported gross
   revenue (equity-accounted), and CLCT's tenant/trade percentages are on *effective
   interest* while property GR/NPI are on 100%. Without a flag, Σ(property) double-counts
   against portfolio totals. Cheapest fix: `value_basis` text ('consolidated' |
   'joint_venture_100pct' | 'effective_interest') on `sgx_reit_property`. (This is v2's
   `held_via` returning with pilot evidence behind it.)
3. **Per-record currency variation inside one trust** — CLCT purchase/divestment prices
   are RMB-only while operating figures are SGD-primary. Already handled (currency is
   per-record), but worth an extraction-rule note: never assume trust-level currency.
4. **Turnover rent isn't always in the revenue note** — CICT's contingent rent (S$84.4m)
   appears only in Portfolio Statement notes, so `income_component` extraction must look
   in both places (same lesson as v2's land-rent rule).

## 5. Recommended actions (for team review, not yet applied)

- **Add** to `sgx_reit_performance`: `aggregate_leverage_pct`, `avg_cost_of_debt_pct`,
  `interest_coverage_x`, `total_borrowings`, `nav_per_unit`, `total_assets` (3/3 evidence).
- **Add** to `sgx_reit_property`: `property_group` (gap 1), `value_basis` (gap 2).
- **Add** WALE — either two columns on performance (`wale_years`, `wale_basis`) or wait
  one round; 3/3 disclosed but multi-basis.
- **Keep** everything currently in the schema — nothing earned a drop.
- **Extraction rules**: reconciliation against audited totals is mandatory per run (it
  caught FCT's duplicate rows); turnover rent may live outside the revenue note;
  per-record currency.
- `gross_revenue` on performance: still provisional — pilot couldn't compare vs
  `sgx_company_report` (not available here); carry the check to the DB-side pilot.
