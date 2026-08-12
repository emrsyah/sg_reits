# Parity check: colleague's manual `sgx_manual_input` vs our extraction

Programmatic comparison (2026-07-14, `scripts/db/_compare_manual_vs_ours.py`) of the 21
hand-typed `sgx_manual_input` rows (from `v2 - SGX - FY2024/FY2025 - REIT.xlsx` via
`SGX REIT upsert.ipynb`) against our `sgx_reit_financial_final` + `sgx_reit_performance_final`,
joined by `(symbol, statement date)`. 17 rows comparable; 4 not (see 6).

Scope note: her property_portfolio / top-tenant / trade-mix blocks are pulled FROM OUR DB by the
notebook, so they match by construction. What she hand-types (and what this report compares) is:
income_stmt_metrics, balance_sheet_metrics, cash_flow_metrics, distribution_metrics.

## 1. Verdict summary

| Block | Result |
|---|---|
| Balance sheet (8 fields) | **17/17 exact on every field** — same source (B/S as declared), same logic |
| Cash flow O/I/F/net (4 fields) | **17/17 exact** (1 T82U net_cash_flow one-off) — same source |
| Income stmt core (9 fields: revenue..net_income) | **17/17 exact** — same source, same sign conventions |
| Shares basic/diluted | match (1 M44U diluted diff, 2 rounding) — same source (EPU note weighted avg) |
| distribution_paid / end_of_year_distribution | **17/17 exact** — she uses the CASH rollforward lines; our P/E map 1:1 |
| distributable_income / adjusted | 15-16/17 — same logic (A + for-year); 3 value diffs to investigate |
| minorities / perpetual_security_holders | pure **SIGN convention flip** (17/17 magnitude match) |
| capital_expenditure | **SIGN flip + SCOPE divergence** (K71U 24x apart) |
| ebit / ebitda | **DIFFERENT DEFINITIONS** (15/17 differ, by design not by error) |
| interest_expense_non_operating | 13/17 differ — different composition of "finance costs" |
| funds_from_operation | she computes it (all 17), ours all null (as-disclosed policy) |
| units_to_be_issued | she has 16/17, ours all null (A1 backfill pending) |

Bottom line: **the "as declared" blocks are already identical** — same statements, same lines.
Every divergence is in the **calculated figures**, where her rules (from the 2026-07-09 meeting)
and ours differ by chosen definition, sign convention, or as-disclosed policy — not extraction
error. Each needs a one-time convention decision, listed in section 5.

## 2. Field-by-field map: her Excel -> our column

### Sheet cols A/B (income statement) -> `financial_final.income_stmt_metrics`

| Excel row label | our key | parity |
|---|---|---|
| total revenue | total_revenue | exact 17/17 |
| cost of revenue (neg) | cost_of_revenue (positive magnitude) | exact |
| gross income | gross_income | exact |
| operating expenses (neg) | operating_expense (pos) | exact |
| net operating income | operating_income | exact |
| net non operating income/(expenses) | non_operating_income_or_loss (signed) | exact |
| pretax income | pretax_income | exact |
| tax (neg) | income_taxes (pos) | exact |
| net income | net_income | exact |
| minorities (SIGNED, deduction = negative) | minorities (we store positive) | **sign flip** |
| perpetual security holders (signed) | perpetual_security_holders (positive) | **sign flip** |
| unitholders | unitholders | exact (1 T82U FY2025 diff) |
| non operating interest expense | interest_expense_non_operating | **composition differs** (see 3.4) |
| ebit | ebit | **definition differs** (see 3.1) |
| depreciation and amortization | (no field — intermediate only; prod doesn't carry it either) | n/a |
| ebitda | ebitda | **definition differs** (see 3.2) |
| gain/(loss) on property sales | net_property_sales | 14/17 (3 small defs diffs) |
| FFO | funds_from_operation | she computes, ours null (see 3.5) |
| Weighted avg shares (basic) | basic_shares_outstanding | exact |
| Weighted avg shares (diluted) | diluted_shares_outstanding | exact (1 M44U diff) |
| revenue/expense breakdowns (cols C-H) | revenue_breakdown / operating_expense_breakdown | same shape + sum==total guard both sides |

### Sheet col N/O (balance sheet) -> `financial_final.balance_sheet_metrics` — all 8 exact

Current Asset -> total_current_asset; Non-Current Asset -> total_non_current_asset; TOTAL ASSET ->
total_asset; Current/Non-Current Liabilities -> total_current/non_current_liabilities; TOTAL
LIABILITIES -> total_liabilities; TOTAL SHAREHOLDER'S EQUITY -> total_equity; Working Capital ->
working_capital.

### Sheet col N/O (cash flow) -> `financial_final.cash_flow_metrics`

| Excel | ours | parity |
|---|---|---|
| Cash Flows from Operating/Investing/Financing | operating/investing/financing_cash_flow | exact |
| NET INCREASE/DECREASED | net_cash_flow | exact (1 T82U diff) |
| CAPITAL EXPENDITURE (positive) | capital_expenditure (we store negative outflow) | **sign + scope** (see 3.3) |
| (derived OCF - capex) | free_cash_flow | follows capex |

### Sheet col N/O (distribution block) -> `performance_final` (mapping doc section 2)

| Excel | ours | parity |
|---|---|---|
| Distributable income | distributable_income_opening + COALESCE(adjusted_distributable_income, net_distributable_income) | 14 exact + 1 close; 2 diffs (C2PU FY2024 3,000k; ME8U FY2024 13,354k) — investigate |
| Adjusted distributable income | COALESCE(adjusted_distributable_income, net_distributable_income) | 15 exact; C2PU FY2024 3,000k diff |
| Distribution paid | distribution_cash_paid (P) | **exact 17/17** — she uses the cash line |
| End-of-year distribution | distributable_income_closing (E) | **exact 17/17** |
| End-of-year shareholder units | number_of_shareholder_units | 14 exact, 2 rounding; BUOU differs (HER value is wrong — see 4) |
| Units to be issued | units_to_be_issued | ours null (A1 backfill); after backfill this completes |

## 3. The calculated figures — her rule vs ours

### 3.1 EBIT — different definitions (15/17 differ; largest divergence)
- **Her rule (meeting):** EBIT = Net Operating Income, copied. C38U FY2025: 1,072,548 = NOI.
- **Ours:** EBIT = pretax_income + interest_expense (classic add-back, marked `_derived`).
  C38U FY2025: 958,604 + 298,840 = 1,257,444.
- Why they explode apart: our EBIT keeps fair-value gains/losses (they sit in pretax); NOI excludes
  them. K71U FY2025 (big FV gains): hers 149,868 vs ours 603,565.
- Neither is wrong; they answer different questions. DECISION NEEDED (5.1).

### 3.2 EBITDA — different definitions (15/17 differ)
- **Her rule (meeting):** EBITDA = NOI + [C/F "Depreciation" (P&E) + "Net change in fair value of
  investment properties"]. C38U FY2025: 1,072,548 + 584 + 200,760 = 1,273,892.
- **Ours:** EBITDA = our EBIT (no depreciation add-back; IP is not depreciated). = 1,257,444.
- Note: because her D&A includes the FV change and ours keeps FV in EBIT, her EBITDA and our
  EBIT often land close (K71U: her EBITDA 608,103 vs our EBIT 603,565 — gap = P&E dep) — same
  economics reached by different routes, but the stored numbers differ.

### 3.3 CAPEX — sign flip + scope divergence (14/17 differ)
- **Sign:** she stores positive magnitude; we store the signed outflow (negative). Several rows are
  exact after |x|: J69U 33,033 vs -33,033; ME8U 238,848 vs -238,848.
- **Scope:** her rule = "sum ALL investment-property-related payments in investing activities"
  (incl. acquisitions, and evidently JV/associate property funding). Ours is narrower (additions to
  IP). K71U (JV-heavy): hers 335-345m vs ours ~14m. A17U, BUOU also far apart.
- DECISION NEEDED (5.2): align scope definition, and flip sign in the projection.

### 3.4 Interest expense — composition differs (13/17)
Both call it "non operating interest expense" for system compat (meeting: it is really operating
for REITs; name kept for Gerald's codebase). Values differ by small systematic amounts
(C38U FY2025: hers 314,704 vs ours 298,840) — likely lease-liability interest / perp distributions
/ capitalised interest included on one side only. INVESTIGATE composition per side (5.3).

### 3.5 FFO — she computes, we leave null
- Her FFO = net_income + P&E depreciation (verified C38U: 951,424 + 584 = 952,008).
- Ours: null unless the AR discloses FFO (as-disclosed policy; SG REITs disclose distributable
  income instead).
- DECISION NEEDED (5.4): adopt her formula as a `_derived` field in the projection, or keep null.

### 3.6 Distributable income / units — SAME logic, confirmed
- Her "Distributable income" = retained-from-prior-year + for-year figure == our A + COALESCE(adjusted, B). Verified exact on 15/17.
- Her units for DPU = EOY units + units-to-be-issued (both from units-in-issue note) == our
  number_of_shareholder_units + units_to_be_issued (post-backfill). Her EPU units = weighted-avg
  from EPU note == our basic/diluted_shares_outstanding. Same sources, same logic.
- Annualized DPU (period-weighted) — she computes downstream; we deliberately store the raw
  ingredients instead: dpu + dpu_period_months + distribution_record. Methodology owner: Muhammad.

## 4. Value discrepancies — INVESTIGATED (2026-07-14, all 7 resolved vs the ARs)

Manual-FY labels below; for Mar-FYE trusts manual FY2024 = Mar-2025 statement = our FY2025.

| Row | Field | manual | ours | VERDICT (AR-verified) |
|---|---|---|---|---|
| BUOU FY2024 | end_of_year_shareholder_units | 3,563,645k | 3,762,202k | **BOTH WRONG.** AR issued-only = 3,757,818k + units_to_be_issued 4,384k. Ours folded utbi in (B3 fix, frozen-gated); hers matches no AR line. |
| C2PU FY2024 | adjusted/distributable_income | 91,419k | 94,419k | **Structural, both defensible.** AR prints for-year line 91,419 AFTER the S$3.0m/yr capex retention (her value); ours = before-retention 94,419 (95,041-624+2, derived per our B convention, flagged `distribution_rollforward_basis`). Printed cumulative 136,683 = her distributable_income. |
| ME8U FY2024 (Mar-2025) | distributable_income | 502,792k | 489,438k | **Hers faithful to statement.** FY24/25 statement has a THIRD pool addition: "Distribution of gains from divestment 13,354" (p.126 L7226). Hers = A 101,328 + B 388,110 + 13,354. Ours = A + B only (gains line not stored as a field, only in flag prose). |
| T82U FY2025 | unitholders | 196,631k | 159,279k | **HER ERROR.** AR: total return to Unitholders+perps 177,955 LESS perps 18,676 = 159,279 (ours, exact). Hers = 177,955 + 18,676 — perp return added instead of subtracted. |
| T82U FY2025 | net_cash_flow | -36,808k | -35,575k | **Definitional.** Differ by exactly "Effects of exchange rate fluctuations on cash held 1,233" (L4297). Hers includes FX-on-cash; ours = printed net-movement line. Pick one (5). |
| M44U FY2024 (Mar-2025) | diluted_shares_outstanding | 5,084,902k | 5,034,448k | **HER ERROR.** AR EPU note (p.~168 L7490-93): weighted avg 5,034,448, "Diluted EPU is the same as basic ... no dilutive instruments". Ours = printed; hers matches nothing in the AR. |
| A17U FY2024 | net_property_sales | 0 | 45,362k | **HER MISS.** AR prints "Gain on disposal of investment properties 45,362" (L5280). |
| A17U FY2025 | net_property_sales | 19,281k | 22,819k | **Scope.** AR IP-disposal line = 19,281 (hers). Ours (derived) adds "Gain on disposal of a subsidiary 3,538" (p115). Decide entity-disposal inclusion (5). |
| C38U FY2025 | net_property_sales | 0 | 26k | **Scope.** Ours = "Gain on disposal of a joint venture 26"; not an IP disposal. Same decision as above. |

Scoreboard: 3 her errors (T82U unitholders, M44U diluted, A17U FY2024 gain), 1 both wrong (BUOU
units), 5 convention/structural (C2PU retention, ME8U gains line, T82U FX-on-cash, 2x
entity-disposal scope). ZERO cases where our value misreads the AR.

### 4a. Projection refinements these findings force (added to section 5 todos)

- **New raw field `distribution_pool_other_movements`** (signed, $): printed pool
  additions/deductions between B and the distribution rows — ME8U divestment-gains +13,354,
  C2PU capex retention -3,000. Today these live only in flag prose (they are why 2 of the 16
  rollforward-guard WARNs exist). Then
  `distributable_income = A + COALESCE(adjusted, B) + COALESCE(other_movements, 0)`
  reproduces her figure exactly on all 17/17.
- **`net_property_sales` scope**: projection uses the printed "Gain on disposal of investment
  properties" line only; entity-level disposals (subsidiary/JV stakes) excluded (or kept — one
  flag either way; today ours aggregates them via line_items).
- **`net_cash_flow` definition**: with or without "effects of exchange rate fluctuations on cash
  held". Prod/manual appears to include it (T82U); ours is the printed pre-FX line.

## 5. DONE (emirsyah, 2026-07-14): conventions applied to RAW + FINAL (not sgx_manual_input)

Per emirsyah + the full meeting transcript (2026-07-09), the conventions are written into
`sgx_reit_financial.income_stmt_metrics` / `cash_flow_metrics` (raw) and flow to
`sgx_reit_financial_final` on rebuild. **`sgx_manual_input` is NOT touched** (deferred). Atoms
(P&E depreciation, net FV change of IP, IP-capex, finance costs) captured from the 47 audited C/F
statements (`cf_batch*.md`); applied by `scripts/db/_apply_conventions.py`. As-disclosed atoms
remain in `financial.line_items`; the recomputed fields are flagged in `_derived`.

Formulas (transcript-exact — the July-09 summary was incomplete/wrong; these override it):
- [x] **EBIT = NOI** (`income_stmt_metrics.ebit = operating_income`). Validated EXACT vs her on all
      but BUOU/C2PU (their disclosed NOI basis differs — left as our operating_income).
- [x] **depreciation** (new `income_stmt_metrics.depreciation`) = C/F P&E depreciation + C/F net
      change in FV of investment properties (C/F operating sign; "sum them if two, else whichever
      exists"). Removes non-cash FV movements.
- [x] **EBITDA = pretax_income + interest + depreciation** (transcript 3:34, "add back
      depreciation and interest"). Differs from her Excel where she used P&E-dep-only (her error).
- [x] **interest_expense_non_operating = finance costs** (as declared, positive). Validated EXACT
      vs her (gross finance costs); a couple of her rows used net (her inconsistency).
- [x] **FFO = net_income + depreciation - net_property_sales** (transcript 3:34, "before the
      effect of buying/selling property").
- [x] **CAPEX = sum of all IP-related C/F investing outflows** (acquisition of IP + capital
      improvement + additions + IP-under-development + IP-acquisition costs), stored **POSITIVE**;
      FFO/FCF use it as an outflow. Excludes divestment proceeds, JV/associate investments, plant &
      equipment, and generic subsidiary acquisitions (as-labelled rule; her totals are inconsistent
      so DIFFs vs her are expected).
- [x] **minorities / perpetual_security_holders = NEGATIVE** (deduction; Gerald/prod convention).
      Her N2IU minorities +1,527 and T82U perps +18,676 are her sign errors.
- [x] **Distributable income = A + COALESCE(adjusted, B) + distribution_pool_other_movements**;
      **DPU units = end_of_year_shareholder_units + units_to_be_issued**; **EPU units =
      weighted-avg (basic/diluted_shares_outstanding)** — all already done (backfills + mapping §2).
- [ ] **Annualized DPU**: period-weighted, NOT a simple sum — methodology owned by Muhammad; we
      keep the raw ingredients (dpu, dpu_period_months, distribution_record).
- [x] Column names unchanged (Gerald compat). `interest_expense_non_operating` kept despite being
      operating for REITs.

**Caveats (documented, may need refinement):** (1) a few REITs disclose only *net* finance costs
(gross unavailable) -> interest uses net there; (2) CAPEX subsidiary-acquisition inclusion is a
judgment (her own data is inconsistent — BUOU includes it, C38U excludes it); we exclude generic
"acquisition of subsidiaries". (3) Hospitality/PP&E trusts (J85, XZL, HMN, Q5T) use real PP&E
depreciation (no IP), which is large and correct. All 47 rows applied to raw + final.

## 6. Rows not comparable (coverage, not errors)

| manual row | why |
|---|---|
| AJBU FY2024 (Dec-2024) | we never extracted AJBU FY2024 (only FY2025) |
| M44U FY2025 (Mar-2026) | Mar-2026 FYE = our FY2026 — next extraction cycle |
| ME8U FY2025 (Mar-2026) | same |
| N2IU FY2025 (Mar-2026) | same |

## 7. What we have that she does not (keep/drop evaluation)

Her workbook covers ONLY the financial statements + distribution block + GRI breakdowns. Everything
below is ours-only; recommendation per item:

| Ours-only | Keep? | Why |
|---|---|---|
| performance KPIs (dpu, nav, wale, occupancy, leverage, icr, cost_of_debt, debt maturity, portfolio_value, gross_revenue, npi, number_of_unitholders, dpu_period_months, distribution_record, properties_location) | KEEP | REIT-only enrichment; not representable in sgx_manual_input; feeds chartbook/frontend KPIs |
| net_distributable_income (B) as its own field | KEEP | the cross-REIT comparable income figure; her blob only carries it folded into sums |
| distribution_paid (declared, FY-aligned) | KEEP | DPU/yield basis; she only stores the cash line (P) — without ours the declared figure exists nowhere |
| distributable_income_opening (A) | KEEP | needed to compose her "Distributable income" (A + for-year); also G1/G2 guards |
| profile table (sub_sector, managers, income_model) | KEEP | REIT-only; no manual counterpart |
| full property registry (2,440 rows) | KEEP | she consumes top-20 + country counts FROM it |
| top_tenant / trade_mix full tables | KEEP | source of her GRI blocks |
| property_transaction | KEEP | user-confirmed standalone; does not project |
| financial.line_items | KEEP (raw only) | audit reconciliation to net_income; never projects |
| flags / source_page / *_basis / *_raw / _notes | KEEP (raw only) | as-disclosed audit trail; stripped in final |
| currency handling (per-figure FX -> SGD final) | KEEP | she leaves non-SGD unconverted with a warning; ours is strictly better |
| Her-only: D&A cell, Net PP&E rows | no field needed | intermediates for her EBITDA/capex-fallback; prod doesn't store them |

Nothing in our schema is made redundant by her workbook; conversely her workbook's hand-typed
financials are now fully reproducible from our tables once section 5's convention decisions land.
