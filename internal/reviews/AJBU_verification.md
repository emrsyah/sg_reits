# AJBU — Keppel DC REIT (AJBU.SI) FY2025 — Forensic Extraction Audit

Auditor: independent verification against source. Navigated the report myself from the TOC
(Corporate Information p95/anchor, Group Financial Highlights p8, Portfolio Review / At A Glance
pp.36–46, Consolidated Statement of Profit or Loss p103, Comprehensive Income p104, Cash Flows
p107, Note A/B p108, Distribution Statement p109, Portfolio Statement pp.110–111, Notes 20–26
pp.141–143, Statistics of Unitholdings p196, Financial Calendar p193). Did NOT consult any
extractor tooling / page-map / anchor list / reasoning.

Source: `parsed_reports_datalab/21_AJBU.SI_Keppel-DC-REIT_FY2025/full.md` (page-anchored
`<!-- PAGE N -->`; anchor numbers == the report's printed-page numbers for the financials, so
e.g. P&L is anchor/print p103 even though the front TOC lists it at p108 — a print/PDF offset the
extractor handled consistently).

Note: the report's own Manager-section TOC (line 5069+) lists the financial statements at a
~5-page-higher print number (P&L 108, Portfolio Statement 115) than the PAGE anchors (103, 110).
The extraction used the PAGE-anchor numbers throughout, which is the parse convention — internally
consistent.

---

## 1. Verdict & confidence

**Grade: MINOR ISSUES.**

The hard numbers are sound: every audited figure I re-derived (gross revenue 441,362k, NPI
383,260k, distributable income 268,051k, DPU 10.381c, all 25 active/HFS property valuations,
unitholders 25,780, trade_mix Σ=100%, top-10 clients) matches the source to the dollar, and the
full Statement-of-Total-Return signed reconciliation ties to Profit after tax 434,682k exactly.
The two **known open items both resolve cleanly from the source** (see below). The defects are:
(a) the **`_notes.json` reconciliation contradicts the shipped `income_components.json`** — it
describes a different (older) classification (finance income as revenue; finance costs as one net
line) than what was shipped (HMN-class cross-file contradiction); (b) `income_components` carries
the **`cashflow_hedge_reclassification` as a positive `adjustment` while also expensing the gross
Note-22 finance-cost detail** — arithmetically self-cancelling but a double-handling /
mis-classification; (c) several **unflagged inferences** (top-tenant trade_sector assigned to all
10; ~12 lease_expiry_dates / lease_term_years derived from the Portfolio-Statement term columns);
(d) property-level provenance imprecision (occupancy/nla/gross_revenue cite the Portfolio
Statement p110/111 but actually come from the At A Glance cards p40–44).

Tally: **CONFIRMED ≈ 35** · **DISCREPANCY = 5** · **SUSPECTED-OMISSION = 2** · **UNVERIFIABLE = 1**

---

## KNOWN OPEN ITEMS — resolved

### OPEN-1 — Sponsor (partial note flagged "sponsor, source unknown") → RESOLVED: **Keppel Ltd.**, correct as shipped.
`profile.json` ships sponsor = **"Keppel Ltd."** This is correct and well-supported:
- p7 (line 177): "Keppel DC REIT is managed by Keppel DC REIT Management Pte. Ltd. (the Manager)
  and **sponsored by Keppel** …".
- Corporate Information (p95/anchor, line 4959): "**The Manager — Keppel DC REIT Management Pte.
  Ltd. (a member of Keppel Ltd.)**".
- Substantial Unitholders (p192, line 9259): **Keppel Ltd.** deemed-interest 19.31%, holding via
  Keppel DC Investment Holdings / Keppel Management Ltd. / Keppel Capital → the controlling
  sponsor chain. Ultimate parent above Keppel Ltd. is Temasek (21.21%, deemed, line 9258), but
  the report's named sponsor is **Keppel** (= Keppel Ltd.).
- The facility managers for KDC SGP 1–8 are also "100% held by **Keppel Ltd.**" (footnotes p40/41).
**Verdict: sponsor = Keppel Ltd. is CORRECT.** Best single source page for `profile.source_page`
is p7 (line 177, the explicit "sponsored by Keppel") and/or p192; the shipped `source_page: 97`
(Corporate Information) is also defensible since it names "a member of Keppel Ltd." Confidence: HIGH.

### OPEN-2 — `cashflow_hedge_reclassification` (1,949k, tagged adjustment, source_page 142): P&L line or OCI? → RESOLVED: **it is a Note-22 Finance-Costs contra line, NOT OCI.** Current handling is mis-scoped.
- Note 22 FINANCE COSTS (p142, lines 6991–7002):
  ```
  Interest expense for borrowings                       49,121
  Amortisation of – lease charges                          319
                  – capitalised transaction costs       1,452
                                                        50,892
  Cash flow hedges, reclassified from hedging reserve  (1,949)
                                                        48,943
  ```
  The 1,949 is a **credit reducing gross finance costs (50,892) to the net finance-costs line
  (48,943)** that appears in the P&L (p103, line 5302). It is **NOT** an OCI /
  Statement-of-Comprehensive-Income item. (The Comprehensive-Income statement on p104 separately
  shows "Movement in hedging reserve (8,238)" — a different number — confirming 1,949 lives in
  Note 22, not OCI.)
- So the OCI-mis-scope hypothesis is **false**, but the line **is** mis-scoped *within*
  income_components: it is tagged `statement="adjustment"` with a **positive** 1,949 while the
  three gross Note-22 lines (49,121 / 319 / 1,452) are separately booked as `expense`. The net
  effect equals the real P&L finance-cost line (48,943), so the grand total still reconciles — but
  structurally the hedge reclass is a **contra-component of finance costs**, not an
  income-statement adjustment.
- **Recommended handling:** collapse the three gross Note-22 lines + the hedge reclass into a
  single `expense` component `finance_costs = 48,943` (matching the audited P&L line, p103), OR if
  the Note-22 detail is to be preserved, mark `cashflow_hedge_reclassification` as a **negative
  expense (contra to finance_costs)** — never a positive `adjustment`. See D2.

---

## 2. Discrepancies

### D1 — `_notes.json` reconciliation contradicts the shipped `income_components.json` (MED, HIGH conf)
- `_notes.json → reconciliation.income_statement` states: `sum_revenue 456,673`,
  `sum_expense 158,777`, `sum_adjustment_signed 136,786`, with detail
  "Σrev(435168+6194+**15311**=456673) − Σexp(58102+**48943**+680+25485+12107+805+282+12373) …".
  This classification puts **finance income 15,311 inside revenue** and books **finance costs as a
  single net line 48,943** with **no cashflow_hedge line**.
- The shipped `income_components.json` does the OPPOSITE: finance_income 15,311 is
  `statement="adjustment"` (NOT revenue), and finance costs are exploded into the gross Note-22
  detail (49,121 / 319 / 1,452) **plus** a separate `cashflow_hedge_reclassification` adjustment.
- Consequence: the notes describe an extraction that is not the one shipped. A downstream consumer
  reading `_notes.reconciliation` to understand the buckets will be misled. (Same failure mode as
  HMN's `_notes` vs files contradiction.) The *shipped* file is the better classification re the
  Σrevenue tie-out (see R2); `_notes` should be regenerated from the shipped file.

### D2 — `income_components`: `cashflow_hedge_reclassification` mis-classified as positive `adjustment` (LOW–MED, HIGH conf)
- See OPEN-2. The 1,949k is a contra within Note-22 finance costs (p142), not a standalone
  income-statement adjustment. The arithmetic still ties (the gross 50,892 expensed, less 1,949
  added back = net 48,943), but the bucket is wrong. **Fix:** record finance costs as the net P&L
  line `48,943` (expense), dropping the separate hedge adjustment; or tag the hedge line as a
  negative expense. Cite p103 (net line) / p142 (Note 22 build-up).

### D3 — `top_tenants.trade_sector`: all 10 clients labelled "IT & Telecommunications" — an UNFLAGGED inference (LOW, MED conf)
- The Top-10 Clients table (p39, lines 2385–2400) is **anonymised and has NO per-client sector
  column** — only a 3-colour legend ("Internet Enterprise / IT Services / Telecommunications").
  The extractor assigned `trade_sector = "IT & Telecommunications"` to every row. This is a
  reasonable roll-up (the portfolio mix is ~97% IT/Telco) but it is an **inference not present in
  the table** and is **not recorded in `_notes.inferred[]`**. Per §0 invariant 7 it must be
  flagged. (Also note client #5/#6 "Government-linked Connectivity Solutions Provider" and #8
  "Fortune Global 500 Company" plausibly sit in Telecommunications / Financial Services / Corporate
  — the blanket label is a simplification.)

### D4 — properties: occupancy_rate / nla / gross_revenue cite `source_page` 110–111 but are disclosed on the At A Glance cards p40–44 (LOW, HIGH conf)
- Every property row carries `source_page` 110 or 111 (the Portfolio Statement). But the Portfolio
  Statement (pp.110–111) discloses ONLY location, land tenure, term, and carrying value — it has
  **no occupancy, no lettable area, no gross revenue**. Those three fields come from the **At A
  Glance** cards (pp.40–44: e.g. KDC SGP 1 occupancy 53.3%, ALA 109,721 sq ft, Attributable Gross
  Revenue S$16.5m, all on p40, line 2449–2450). The cited page does not support those values →
  provenance defect (values are correct, the page is not). Ideally split provenance or cite p40–44
  for the card-sourced fields.

### D5 — `performance.distribution_record` mixes an FY2024 stub into FY2025 and does not tie to DPU 10.381 (LOW, MED conf)
- Shipped record: `0.819` (28/11/2024–31/12/2024), `5.133` (1H2025), `5.248` (2H2025). The
  `0.819` is a **FY2024 income-period** distribution merely *paid* in early 2025 (it appears in the
  Distribution Statement p109, line 5538 as part of the 2025 cash payments). FY2025's declared DPU
  is **5.133 + 5.248 = 10.381** (Group Financial Highlights p8, lines 393; Financial Review p46
  line 2606). Including 0.819 makes the record sum to 11.200, inconsistent with `dpu = 10.381`.
  - Also `ex_date` is null for all three, and the `0.819` row has a null `pay_date`. The two
    FY2025 pay dates are confirmed: **15 Sep 2025** (1H) and **19 Mar 2026** (2H) — Financial
    Calendar p193, lines 5292/5295 — and match the shipped pay_dates. **Fix:** drop the 0.819 stub
    (or mark it as the prior-year period), so the record's two FY2025 periods sum to the declared
    10.381.

---

## 3. Suspected omissions

### O1 — Per-segment NPI captured only in `_notes`, not surfaced (LOW; no clean schema home)
NPI by contract type (p46): Colocation S$297.9m, Single-Tenant S$58.6m, Shell&Core S$26.8m
(Σ ≈ 383.3m ≈ NPI 383,260k). Per-property NPI is genuinely **not** disclosed (confirmed: absent
from Portfolio Statement, notes, and cards). The segment NPI is correctly parked in
`_notes.data_with_no_home`; `properties.net_property_income` nulls stand. Acceptable handling.

### O2 — Facility managers / operators not captured in `profile.management` (LOW; arguable schema home)
Each property card names a **Facility Manager** (Keppel-owned entities for SG: Keppel DC Singapore
1 Ltd., Keppel DCS3 Services Pte. Ltd.; third parties abroad: Jones Lang LaSalle K.K., Colt DCS
Japan, FRIS Investment Care B.V., NL Asset Management B.V., Keppel DC Services Australia Pty Ltd).
These map loosely to a `property_manager`/`operator` role. The extraction lists only
reit_manager / trustee / sponsor. Capturing the (Keppel-owned) SG facility manager as
`property_manager` would be defensible; current omission is LOW severity (heterogeneous, mostly
third-party).

---

## 4. Reconciliation results (independently re-computed)

### R1 — Statement of Total Return → Profit after tax (p103) — PASS (to the dollar)
Re-derived directly from the audited P&L:
- Gross revenue 441,362 − Property operating expenses 58,102 = **NPI 383,260** ✓ (= performance).
- + Finance income 15,311 − Finance costs 48,943 − Trustees' 680 − Mgr base 25,485 − Mgr perf
  12,107 − Audit 805 − Valuation 282 + Net gains on derivatives 2,350 − Other trust exp 12,373
  = **Profit before divestment/FV 300,246** ✓.
- + Gain on divestment 10,825 + Net change in FV 161,648 = **Profit before tax 472,719** ✓.
- − Tax 38,037 = **Profit after tax 434,682** ✓.

### R2 — Using the shipped `income_components.json` buckets — PASS (but via double-handling)
Σrevenue(435,168+6,194)=441,362; Σexpense(58,102 + Note-22 gross 50,892 + 680+25,485+12,107+805+282
+ Note-24 12,373)=**160,726**; Σadjustment(finance_income 15,311 + cashflow_hedge +1,949 + derivs
2,350 + divestment 10,825 + FV 161,648 − tax 38,037)=**154,046**. 441,362 − 160,726 + 154,046 =
**434,682** ✓. It ties — but only because expensing gross finance costs 50,892 and adding back the
hedge +1,949 nets to the true 48,943 (see D2). The `_notes` reconciliation (D1) reaches the same
434,682 via a DIFFERENT bucketing (finance income in revenue, finance costs net) — proof the two
artefacts disagree.

### R3 — Σ(income_components statement=revenue) vs gross_revenue — PASS
435,168 + 6,194 = **441,362** = `performance.gross_revenue` ✓. (Unlike HMN, finance_income is
correctly NOT in revenue here, so this tie-out holds.)

### R4 — Gross Revenue note (Note 20, p141) — PASS
Rental income 435,168 + Other income 6,194 = **441,362** ✓.

### R5 — Property Operating Expenses (Note 21, p141) — PASS
6,504 + 20,239 + 2,275 + 20,874 + 8,210 = **58,102** ✓.

### R6 — Portfolio valuation Σ → audited total (Portfolio Statement pp.110–111) — PASS
Σ(properties.market_valuation, 25 valued rows incl. Basis Bay HFS 17,092) = **6,150,492k** =
"Total investment properties (including those held for sale) at fair value" (p111, line 5618) =
`performance.portfolio_value` 6,150,492,000 ✓. Kelsterbach correctly carried at null (divested,
2024 value 55,041 shown only as prior-year). Spot-checked ~15 rows vs Portfolio Statement: all
match (incl. KDC SGP 7 750,077 / 8 801,759 = Tier C *incl.* the S$350m lease-extension liability —
correctly NOT the card values 744.0 / 796.0; KDC SGP 5 507,003 not card 497.0; KDC SGP 3 426,000
not card 383.4; KDC SGP 4 590,000 not card 584.1). Tier-C discipline correct.

### R7 — DPU / distributable income (p8, p46) — PASS (with D5 caveat)
Distributable income 268,051k ✓; DPU 10.381c ✓ (1H 5.133 + 2H 5.248). Pay dates 15 Sep 2025 /
19 Mar 2026 ✓ (p193). See D5 re the extra 0.819 FY2024 stub.

### R8 — Trade mix Σ → 100% (p39) — PASS
69.3 + 14.0 + 13.6 + 2.4 + 0.7 = **100.0** ✓, `pct_basis = rental_income` ✓ (clients' trade
sector, p39 line 2368 — the correct mix, NOT the contract-type mix which is correctly parked in
`data_with_no_home`). category_raw verbatim ("Internet Enterprise", "IT Services", etc.) ✓.
Mapping "Corporate" 0.7% → "Other Office Trades" is a stretch (Corporate ≠ office) but harmless.

### R9 — Top-10 clients (p39) — PASS (values), see D3 (sectors)
42.1 / 9.6 / 8.4 / 5.7 / 4.8 / 4.1 / 2.2 / 2.1 / 2.1 / 2.0 — all match p39 verbatim; ranks correct;
extreme top-client concentration (42.1%) captured; anonymised descriptors verbatim ✓.

### R10 — Unitholders — PASS
25,780 (Statistics of Unitholdings, p196 line 9209, "As at 11 March 2026") ✓.

### R11 — Divestment (property_transactions) — PASS
Kelsterbach DC: completion 24 Mar 2025 ✓ (p108/p46); carrying_value_pre 55,041 = 2024 Portfolio
Statement value ✓ (p110 line 5588); gain 10,825 ✓ (p103 line 5311). transaction_price null —
the standalone sale price is not cleanly disclosed (net proceeds 65,475 in cash flows includes a
note subscription); null is defensible.

---

## 5. Nulls / inference audit

**Confirmed genuinely absent (correct nulls):**
- `properties.gla` — cards disclose "Attributable Lettable Area (sq ft)" (placed in `nla`) and a
  *partial/inconsistent* "Gross Floor Area (sq ft)" (only ~14 of 25 properties, parked in
  `_notes.data_with_no_home`). Correct decision: ALA→nla, GFA not forced into gla. ✓ Reason
  text accurate.
- `properties.net_property_income` — genuinely not per-property (only segment NPI, p46). ✓
- `properties.major_tenant` / `trade_mix` — clients fully anonymised under confidentiality
  footnote (p39 line 2421); correct null + correct reason. ✓
- `top_tenants.tenant_name` — anonymised; verbatim descriptors kept. ✓

**Wrong / understated provenance & unflagged inferences:**
- `_notes.reconciliation.income_statement` describes a classification not shipped (D1). Should be
  regenerated.
- `top_tenants.trade_sector` (all 10 → "IT & Telecommunications") is an **unflagged inference**
  (D3) — add to `_notes.inferred[]`.
- `lease_expiry_date` / `lease_term_years` for the leasehold rows are **derived from the Portfolio
  Statement "Term of lease" + the card "Expiring DD Month YYYY"** strings (e.g. KDC SGP 1
  2055-09-30 from "Leasehold (Expiring 30 September 2055)"). The explicit expiry dates DO come from
  the card "Title" lines (verbatim, e.g. p40 line 2441), so they are disclosed, not back-computed —
  but `lease_term_years` (e.g. 60, 70, 999, 199) is read from the PS "Term of lease" column. These
  are sourced, low-risk; `tenure_raw` captured verbatim correctly. Minor: KDC SGP 5
  `lease_term_years = 39` matches the PS "39" (incl. 9-yr extension per footnote 1 p111) — correct.
- `valuation_date = 2025-12-31` uniform — correct (Portfolio Statement "As at 31 December 2025")
  but an assigned/uniform value, not field-level per row. Acceptable.
- `properties.occupancy_rate` per row = card values (p40–44), all confirmed correct (e.g. KDC SGP 1
  53.3%, Gore Hill 80.0%, Basis Bay 40.2%, Amsterdam 95.1%) — but mis-cited to p110/111 (D4).

**DC-specific traps — handled correctly:**
- NCI / sub-100% stakes captured: KDC SGP 3 ownership 90%, SGP 4 99%, SGP 5 99%, Tokyo DC 1/3
  98.47%, Basis Bay 99% — all match the cards. NCI subsidiaries (KDCS3/4/5 LLP, KDCRT2 TMK) noted
  (p143). ✓
- Lease-extension carrying-value inflation: KDC SGP 7 (750,077) and SGP 8 (801,759) Tier-C values
  EXCEED their card valuations (744.0 / 796.0) because the S$350m extension liability is
  capitalised — correctly captured at the higher Tier-C figure with a `parsing_traps` note. ✓
- Basis Bay = `held_for_sale` ✓ (p111 / p42 footnote 13), valued at Tier-C 17,092k. ✓
- Area metric = Attributable Lettable Area (sq ft), no MW — correct. ✓

---

## 6. Confirmed-correct highlights (balance)

- **Sponsor = Keppel Ltd. — correct** (OPEN-1 resolved; p7/p95/p192).
- **All audited financials exact**: gross revenue, NPI, finance income/costs, manager fees, tax,
  Profit after tax (434,682k), distributable income, DPU.
- **Full Statement of Total Return reconciles to Profit after tax to the dollar** (R1) — no missing
  line. Σrevenue tie-out to gross_revenue PASSES (R3, unlike HMN).
- **All 25 active/HFS properties present** with correct countries (10), categories, ownership %,
  Tier-C valuations (S$350m-extension and lease-liability traps navigated), tenure enum + verbatim
  `tenure_raw`; Kelsterbach correctly divested/nulled.
- **Tier-C discipline correct** — Portfolio-Statement carrying values used everywhere, never the
  lower marketing/card valuations.
- **trade_mix uses the clients' trade-sector mix** (not contract type), `pct_basis = rental_income`,
  Σ=100%; contract-type mix correctly parked in `data_with_no_home`.
- **Top-10 anonymised descriptors verbatim**, extreme 42.1% top-client concentration captured.
- **Sub-sector = Data Centre**, income_model = mixed (colocation + single-tenant + shell-and-core +
  master/"Keppel" leases — reasonable), currency SGD per row.
- Unitholders 25,780, FY-end 2025-12-31, pay dates all confirmed.

---

## 7. Could NOT verify

- **Per-property NPI in SGD** — genuinely not disclosed (only segment NPI, p46). Nulls stand;
  unverifiable by design.
- **Kelsterbach standalone sale price** — only net divestment proceeds (65,475k, bundled with a
  note subscription) and the accounting gain (10,825k) are disclosed; a clean disposal
  consideration is not separable from the parse. `transaction_price = null` is defensible.

---

## Fix list (file → field → correct value → page)

1. `_notes.json` → `reconciliation.income_statement` → **regenerate from the shipped
   income_components.json** (finance_income 15,311 is an `adjustment`, not revenue; finance costs
   per Note 22). Current block (sum_revenue 456,673 etc.) describes an unshipped classification.
   Source: p103 (P&L) / p141–142 (Notes 20–24). [D1]
2. `income_components.json` → `cashflow_hedge_reclassification` → **re-class**: either fold Note-22
   into a single `finance_costs` expense = **48,943** (p103 net line), or mark the hedge reclass as
   a **negative expense (contra to finance costs)**, not a positive `adjustment`. Source: p142
   Note 22. [D2 / OPEN-2]
3. `top_tenants.json` → `trade_sector` (all 10 = "IT & Telecommunications") → keep value but **add
   an entry to `_notes.inferred[]`** (table has no per-client sector column; assigned from the
   3-sector legend / portfolio mix). Source: p39. [D3]
4. `properties.json` → `source_page` for `occupancy_rate` / `nla` / `gross_revenue` →
   **p40–44 (At A Glance cards)**, not p110/111 (Portfolio Statement has no such columns).
   Source: pp.40–44. [D4]
5. `performance.json` → `distribution_record` → **drop the 0.819 (28/11/2024–31/12/2024) FY2024
   stub** (or relabel it prior-year) so the FY2025 record = 5.133 + 5.248 = **10.381**, matching
   `dpu`. Source: p8 (line 393) / p46 (line 2606) / p193 pay dates. [D5]
6. (Optional, LOW) `profile.json` → consider adding the Keppel-owned SG `property_manager`
   (e.g. Keppel DCS3 Services Pte. Ltd.) and/or `profile.source_page` = 7 (the explicit
   "sponsored by Keppel"). Source: pp.40–41, p7. [O2 / OPEN-1]

No `extracted/` files were modified. Corrections are gated by the user.
