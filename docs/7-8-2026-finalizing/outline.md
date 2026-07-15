# Finalizing — Data-Quality Workstream (2026-07-08)

Single tracker for the cross-cutting data-quality / normalization pass across the `sgx_reit_*`

tables. Doing these **one by one**. Tick `[x]` on completion. Items marked **BLOCKED** wait on

inputs from emirsyah (videos / Slack notes / Excel samples) — do NOT start blind.

Legend: every item is a tickable box (`[ ]` todo · `[x]` done). Status shown inline via tags:

**IN PROGRESS**, **BLOCKED** (waits on emirsyah input), **DECISION** (pending call), **MANUAL** (emir).

---

## FROZEN — do NOT touch these REITs from now on

> emirsyah froze these 10 REITs (2026-07-08). Do **not** modify their `sgx_reit_*` rows or
>
> `extracted/<SYM>.SI_FY*/` JSON in any subsequent step — exclude them from every fix/reload/re-extract:
>
> **C38U · A17U · N2IU · M44U · ME8U · J69U · T82U · K71U · BUOU · C2PU**
>
> Impact on §B loader-currency fix: A17U (137), M44U (17), ME8U (1), J69U (1), BUOU (1), C2PU (1),
>
> N2IU (1) are frozen → their mv_ccy mislabels stay as-is; reload only the **non-frozen** affected
>
> symbols (D5IU, AU8U, SET, BMOU, HMN, CRPU, BTOU, J91U, CY6U, AJBU).
>
> **FY2024 caveat (2026-07-09):** the freeze applies to **FY2025** edits by default. FY2024
> extraction/edits of these 10 were explicitly permitted and are now DONE (see §8). Freeze has
> been lifted case-by-case before (NDI, property-txn, and the full FY2024 build + fixes).

## 0. Open decisions (block "finalised" — recommended default = keep-null + document in `_notes`)

- [ ] **DECISION** — **T82U — 4 JV rows** (One Raffles Quay, MBFC Properties, Southgate Complex, Nova Properties).

  Report discloses only an **income contribution** (share of profit excl FV change + JV-loan

  interest), NOT property NPI: ORQ $30.2m / MBFC$38.8m / Southgate $2.4m / Nova$28.6m (total

  $100.0m; `full.md` line 756, p22). Note 7 (p142) gives 100%-JV revenue only.
  - Option A *(current, recommended)*: keep `net_property_income` null, figures in `_notes`.
  - Option B: populate NPI with income-contribution + basis flag (breaks cross-REIT comparability).
  - Option C: populate `gross_revenue` with 100%-JV revenue + flag.
- [ ] **DECISION** — **C38U — Bugis+ &amp; Bukit Panjang Plaza** (both 100%-owned; GR/NPI null). CICT discloses only a

  **combined "Other Assets" = S$63.4m** (FY2024) — financial review p23 + both cards. No per-property

  figure exists.
  - Option A *(current, recommended)*: keep null, combined value in `_notes`.
  - Option B: assign 63.4m to one row. · Option C: split by proxy (inferred — rejected by policy).

---

## 1. Property table — null-checking + other issues (continue)

- [x] **Synthesized emirsyah's 41 property/perf/txn notes** → `property-notes-synthesis.md`

  (buckets: FIX / VERIFY / DISCUSS / CONFIRMED). All notes are on FY2025 data.
- [x] **§A FIX applied** (JSON+DB, 0 schema errors): J69U `gla==gfa` nulled (9); area_unit filled

  report-wide C2PU/ME8U/SET/P40U. CY6U `npi_pct` CLOSED (verified disclosed, staged null NOT applied).
- [x] **§B loader-currency fix applied** — `market_valuation_currency` mislabel (loader bug) fixed in

  `load_supabase.py` + targeted UPDATE on 10 non-frozen symbols (56 rows → mv_ccy=currency). Frozen

  REITs left as-is.
- [x] **§B value-level verified** (11 non-frozen REITs vs ARs → `verify/RESULTS.md`): 9 PASS, no data

  wrong. 8C8U original_* gap + factual fix (#14=AUD) routed to §C coverage. BTOU/AW9U/CY6U resolved.
- [x] **§C audited** (19 non-frozen REITs vs ARs → `verify_c/RESULTS.md`). Applied: `lease_term_years`

  base-term fix J91U 36 / AJBU 3 / JYEU 1 (JSON+DB). item4 area_unit already complete. item8

  store-in-SGD: NO report mislabels (all as-disclosed). item5 DCRU: 9/11 already 100% basis. item6/7

  no action.
- [x] **§C emirsyah decisions applied** (2026-07-08): (a) SCHEMA — `lease_expiry_date`+`effective_date`

  date→text, added `lease_terms_flags` col (models+loader+DB); (b) lease FLAGs — options-inclusive

  kept+flagged (O5RU/M1GU/XZL/CY6U 46 rows), remaining-term nulled+flagged (UD1U/SET 8); (c) effective_date

  = disclosed-only (no derivation); (d) DCRU 2 Osaka JVs left ownership-basis + noted; (e) item9 original_*

  flag-only. purchase_date: DHLU 19/19 filled; CMOU/OXMU/XZL/SET already complete.
- [x] **purchase_date extraction DONE** (10 REITs, sonic agents → `verify_pd/RESULTS.md`): verbatim fills

  applied (ODBU 3, DCRU 3, JYEU 1; DHLU 19 earlier); ~360 rows genuinely NOT disclosed → null (HMN 100,

  MXNU 145, AJBU, UD1U, CY6U, Q5T…). ODBU dates cross-checked vs AR SPV names.
- [x] **IPO/listing-date proxy applied** (emirsyah approved): ODBU 18 @2020-03-12, BMOU 5 @2015-12-11,

  DCRU 6 @2021-12-06, JYEU 2 @2019-10-02 (31 rows); basis noted in each `_notes.inferred[]`. DCRU

  Osaka 2 + BMOU Hefei correctly null. **§1 property table (non-frozen) COMPLETE.**

## 2. EPU vs DPU placement (manual check — doable now, no new input)

- [x] **DPU placement VERIFIED correct** — `performance.dpu` 37/37 filled; no DPU/distribution key

  inside `financial.income_stmt_metrics`. No misplacement.
- [x] **EPU checked** — no EPU is misplaced in `performance`. BUT explicit EPU is **ABSENT from

  financial** — `income_stmt_metrics` has no `eps`/`earnings_per_unit` field (schema doesn't define

  one); only the components (`net_income`/`unitholders` + `weighted_avg_shares_basic`/`diluted`) are

  present, so EPU is currently derivable-only, not stored.
- [x] **DECISION: (A) — leave EPU derivable** from components (emirsyah). §2 CLOSED. Explicit-EPU

  capture, if ever wanted, folds into §4.

## 3. Verify `sgx_reit_performance` against colleagues' statement positions

- [ ] **Ongoing — verify each figure sits at the colleague-specified position** (emirsyah gives the

  positions directly; no separate "A/B/C" doc). Positions given so far VERIFIED correct (2026-07-08):
  - distribution → Distribution Statement, annualised; helpers present: `distribution_basis`
  
    (20 after_retention / 9 full_payout / 6 rollforward_only / 2 suspended), `dpu_period_months`
  
    (35×12mo annualised, 2 stub-period IPOs).
  - portfolio_value → Portfolio Statement total (37/37).
- [x] **unitholders — ALREADY EXTRACTED** (37/37): `number_of_unitholders` (holder headcount) AND

  `number_of_shareholder_units` (units in issue). Both present.
- [x] **C38U distributable-income query RESOLVED** (frozen — no edit): `net_distributable_income`

  860.9m = after-retention FY2025 DI (matches DPU 11.58c), tagged `disclosed_after_retention`. The

  p107 1,119,753 is the cumulative available pool (opening 249,796 + FY2025 869,957) — would

  double-count prior years; correctly NOT used. We are correct.
- [x] **Distribution-position spot-check** (5 REITs, cumulative-pool-trap audit vs Distribution

  Statement, 2026-07-08): AJBU ✅ (268,051 FY-gen, not cumul 332,893; 2.0 ratio = half-yearly timing),

  CMOU ✅ (43,032, opening nil), OXMU ✅ (28,726), C2PU ✅frozen (99,781 not cumul 115,343).
- [x] **K71U ❌→FIXED** (emirsyah lifted freeze): `net_distributable_income` 320,277,000 (cumulative) →

  **212,406,000** (FY-generated, p121); corrected in JSON+DB+`_notes`. `distribution_paid` transposition

  (212,406 vs actual 276,593) left for the distribution_paid semantics review below.
- [x] **Full NDI sweep DONE — all 37 REITs** checked vs Distribution Statement (cumulative-pool trap),

  `verify_dist/`. Result: **34 CORRECT**; 2 cumulative-pool errors FIXED (K71U, **CRPU** 77,219,000→

  77,209,000 — opening $10k); 1 flagged below (J85).
- [x] **NDI CONVENTION DECIDED (emirsyah): BEFORE-retention** ("income available for distribution for

  the year", the gross distributable income — more consistent: 34/37 already this basis; more

  meaningful — heavy-retainers like OXMU show true 28.7m not 8.3m). Locked in models.py. Normalized

  the 3 after-retention outliers → before-retention (JSON+DB+flags): **C38U** 860,900,000→869,957,000,

  **CRPU** 77,209,000→85,666,000, **TS0U** 123,752,000→128,752,000. J85 66,627,000 = before-retention

  (disclosed "total distribution before retention", p-highlights) → already CORRECT, no change. MXNU

  19,303,000 before-retention → CORRECT. `distribution_basis` flag reinterpreted as "retention

  disclosed?" (accurate for all). **All 37 NDI now consistently before-retention.**
- [ ] **DEFERRED DECISION — distribution ROLLFORWARD split + guards** → full plan in
  `distribution-fields-proposal.md` (revised 2026-07-09). Capture the Distribution Statement as
  4 as-disclosed rollforward lines: A `distributable_income_opening`, B `net_distributable_income`
  (=today's NDI, done), P `distribution_cash_paid` (NEW, cross-year cash line), E
  `distributable_income_closing`; plus keep existing `distribution_paid` (= declared-for-year / DPU
  headline) UNCHANGED — it is NOT the cash line and NOT a bug. (The cumulative "available" line =
  A+B is NOT stored — not disclosed verbatim across the corpus; display-derive if needed.) Guards
  G1 `A+B-P=E`, G2 cross-year `E(N)=A(N+1)`; broken guard = investigate
  source, never plug. Drop redundant `disclosed_after_retention`/`full_payout` flag values; keep
  slim flag (suspended / net-loss / rollforward-derived / cash-includes-capital / null-reason).
  **emirsyah to decide execute-or-not + whether to rename `distribution_paid` ->
  `distribution_declared_for_year`.** Until then: `distribution_paid` stays as-is (do NOT overwrite
  to the 276,593 cash figure). NDI (B/before-retention) already normalized + locked.
- [ ] **FY2024 relabels applied (2026-07-09)** — J69U/K71U -> `full_payout_no_retention_line`
  (best-fit; both full/over-payout, no net retention: J69U dist 214,313 > NDI 213,221 = release
  of FY23 retained 1,092). Confirms the enum gap: no clean value for an over-payout/release case.
  The 3-field split above would remove the need for this best-fit.

## 4. Financials cross-check vs Evelyn's manual inputs

- [x] **BLOCKED** — need Evelyn's Excel / manual-input samples + Slack notes on method.
- [x] Cross-check already-extracted `sgx_reit_financial` against Evelyn's version.
- [ ] Re-extract `sgx_reit_financial` after cross-check.
- [ ] **DECISION — attribution-sign normalization.** Pick ONE convention: components-POSITIVE
  (unitholders + perpetual_security_holders + minorities summing to net_income) vs
  deductions-NEGATIVE. FY2024 (10 frozen) uses positive-summing-to-net. **FY2025 is inconsistent
  — known bug:** M44U FY2025 stored perpetual/minorities NEGATIVE (-24,231 / -1,125). Fix when
  FY2025 is touched (freeze -> case-by-case approval). FFO-capture decision also open.
- [x] **Mapletree manual-input divergence RESOLVED (2026-07-09)** — year-label convention, not an
  error. Evelyn's "FY2024" = start-year = our FY2025 (year ended 31 Mar 2025) for M44U/ME8U/N2IU
  (31-Mar FYE). Ours ties to the audited year-ended-Mar-2024. Confirm with Evelyn/emirsyah how
  prod reconciles start-year vs end-year labels for March-FYE trusts.
- [x] **FY2024 financial cross-check DONE** — 7/10 tie exactly (rev + net_income) vs
  `sgx_manual_input`; the 3 divergent (M44U/ME8U/N2IU) = the year-label offset above. QC
  identities I1/I2/I3 + attribution-sum pass in JSON and DB.

## 5. Normalize + re-extract `sgx_reit_property_transaction`

- [ ] **BLOCKED** — normalization rules (e.g. `gain_on_divestment`, etc.) not yet decided — wait for

  the rules from emirsyah (prior AI discussion incomplete).
- [ ] **Subsequent-events + NCI sweep** (broader) — prior session found extraction misses
  NCI-booked and subsequent-event deals. Blocked on the same normalization rules. Optional sweep
  across other REITs' transactions.

## 6. Cross-check property transactions vs SGX Chartbook (manual — emir)

- [x] **MANUAL** (emir). Reference: SGX Research SREIT Property Trusts Chartbook Q4 2025

  ([https://www.reitas.sg/wp-content/uploads/2026/03/SGX-Research-SREIT-Property-Trusts-Chartbook-Q4_2025.pdf](https://www.reitas.sg/wp-content/uploads/2026/03/SGX-Research-SREIT-Property-Trusts-Chartbook-Q4_2025.pdf)).

## 7. Frontend (separate project — out of scope here)

- [ ] Continue frontend track (tracked elsewhere; noted here for completeness).

## 8. FY2024 full record build — 10 frozen REITs (2026-07-09) DONE

FY2024 full record set for all 10 frozen REITs (C38U A17U N2IU M44U ME8U J69U T82U K71U BUOU
C2PU) extracted, independently audited, corrected, upserted. Three rounds:

- [x] **Round 1 — extract.** Created the 5 missing sections each (`financial`, `performance`,
  `trade_mix`, `top_tenants`, `profile`) in `extracted/<SYM>.SI_FY2024/` (property/txn/_notes
  pre-existed). Method: 10 gather `task`-agents wrote verbatim AR tables ->
  `local://fy2024-gather/<SYM>.md`; main agent mapped/validated/wrote/loaded. Financial
  derivation model reverse-engineered + validated: `operating_income = gross_income -
  operating_expense`; `ebit = ebitda = pretax + interest_expense_non_operating`; `income_taxes`
  signed (tax credit negative); `interest_expense_non_operating` = NET finance cost; attribution
  positive-summing-to-net; `_derived[]` set.
- [x] **Round 2 — independent audit.** 10 fresh-context forensic audit-agents (source `full.md` +
  shipped JSON only), `skill://reit-audit` -> `reviews/<SYM>_FY2024_verification.md`. Result:
  **2 CLEAN (J69U, C2PU), 8 MINOR, 0 MATERIAL/WRONG, zero value-level errors on disclosed hard
  numbers.**
- [x] **Round 3 — fixes + upsert.** revenue_breakdown backfill (7), portfolio_value -> audited
  totals (4), false-null fixes (C38U unitholders=85,596; K71U WADM=2.5), ME8U +Canada, M44U
  distribution_record quarterly, A17U net_cash_flow -> Sum(activities), distribution_basis
  relabels (J69U/K71U), pay_dates (J69U/BUOU), BUOU adj_distributable_income=255,515,000,
  T82U/BUOU multi-segment pct_basis, inference flags. QC identities pass in JSON and DB.
- [x] **DB load discipline** — perf + financial UPSERT; trade_mix + top_tenant
  delete-then-reload; **profile deliberately NOT loaded** (symbol-singleton would clobber newer
  FY2025 rows). FY2025 profile source_pages verified preserved.

### 8a. FY2024 residual backlog (contained items)

- [ ] **DECISION — `_notes.inferred[]` migration.** This session's inference flags (ME8U
  tenant-industry; T82U sponsor/sub_sector/Q4-DPU; C2PU 2.38c residual) went into
  `performance.flags` (contained, upserted) to avoid editing prior-session `_notes.json`. Proper
  home is `_notes.inferred[]`; migrating also requires reloading `sgx_reit_notes`.
- [ ] **DECISION — profile-to-DB for FY2024.** K71U FY2024 `profile.json` gained 2 property
  managers (GPT Property Management Pty Limited, Jones Lang LaSalle (VIC) Pty Ltd) but is
  file-only (singleton protection). Broader: profile is symbol-singleton with no financial_year
  — "which year's profile wins" is unresolved.
- [ ] **T82U `revenue_breakdown` gap.** Left empty: visible Group Note-20 line (462,085) doesn't
  reconcile to gross revenue 463,556 (~1,471 gap; likely a 2nd revenue line below line 5574 in
  the parse). Resolve by reading full Note 20; backfill ONLY if it ties exactly.
- [ ] **DECISION — ICR basis convention.** Kept ADJUSTED ICR for M44U (3.1), ME8U (4.3), N2IU
  (2.9) to match FY2025; headline/MAS figures differ (M44U 3.7, ME8U 4.6, N2IU 3.0). Confirm
  adjusted is the intended standard, or switch to headline.
- [ ] **ICR / portfolio_value basis review — WHOLE corpus** (not just these 10) for consistency,
  if the adjusted-ICR / audited-portfolio-total conventions get locked.

---

## Working rules (fixed — do not relitigate)

- **Portfolio valuation** = audited **Portfolio Statement** `investment properties, at valuation`

  total (Tier C, `$'000` ×1000 → absolute). No proportionate / property-roll-up model.
- **As-disclosed only.** Never compute / impute / split a combined figure. If ever derived, flag in

  `_notes.inferred[]`; otherwise leave null with page-checked evidence.
- Keep solutions **minimal**. Do not infer extra scope.
- **Subagent caveat:** shared `eval` kernel across sibling subagents → isolate per-cell state,

  assert-on-load, and run a post-batch cross-contamination check (symbol==dir, no dup `property_name`,

  `financial_year` correct, 0 schema errors) before loading.

## Verify / load reference

- In-process schema validate: `sys.path.insert(0,'schema'); import models; models.Property.model_validate(p)`.
- Load: `python scripts/db/load_supabase.py <SYM>.SI_FY2024 ...` (idempotent; uses `SUPABASE_CONNECTION_STRING`).
- DB verify: query `sgx_reit_property` grouped by symbol for `financial_year=2024`.

