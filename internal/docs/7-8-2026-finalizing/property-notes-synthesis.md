# Property Table — emirsyah's Notes, Synthesized (2026-07-08)

Source: `reit_field_edit` (`table_name='__section_note__'`, 37 PROPERTY notes) + `reit_record_verdict`
(2 property verdicts) + 3 pending property field-edits, all `reviewer='ba1cef72-...c568774'`.
**All notes are on FY2025 property data** (the 39-REIT set). Bucketed into: **FIX** (clear, apply now),
**VERIFY** (check DB value vs a specific AR page, then fix), **DISCUSS** (schema/policy decision
needed this session), **CONFIRMED** (note only confirms a genuine null — no action).

Core recurring bug (grounded): for CNY/IDR REITs, `market_valuation` holds the **SGD-converted**
value and `currency='SGD'` (correct), `original_value`/`original_currency` hold the local figure
(correct) — but `market_valuation_currency` is mislabeled with the **local** currency (CNY/IDR)
instead of SGD. Confirmed on CRPU (4 rows) and D5IU (29 rows). But the same `mv_ccy != currency`
condition also flags legitimately-local valuations elsewhere, so it is **not** a blanket fix —
verify direction per REIT against the cited page.

---

## A. STRAIGHT FIX (unambiguous — apply, then load)

- [x] **Applied 2 of 3 staged field-edits** as report-wide area_unit (see below). **CY6U
  `npi_pct → None`: CLOSED — NOT applied.** Verification (p26 "% contribution to NPI") confirms
  `npi_pct` is AR-disclosed, all values match, sums to 100%, none spurious — the staged null was
  unwarranted. See `verify/RESULTS.md`. *(2026-07-08)*
- [x] **J69U — `gla == gfa` nulled on 9 rows** (JSON + DB). Only `gfa`+`nla` verbatim; `gla` was a
  copy. Verified 0 gla non-null remaining; all null-gla rows also had null gfa. *(2026-07-08)*
- [x] **area_unit filled report-wide** where an area figure exists (staged single-row edits were
  samples; notes state report-wide): C2PU `sqm` (74), ME8U `sqft` (99), SET `sqm` (96), P40U
  `sqft` (8). Rows with no nla/gla/gfa left null by design (C2PU 1, ME8U 1, SET 8). JSON+DB in
  sync, 0 schema errors. *(2026-07-08)*

> **Root-cause finding for §B (loader bug, not data):** `load_supabase.py` lines 245-247 derive
> `market_valuation_currency = original_currency or currency`, but `market_valuation` always holds
> the value in the row's **presentation currency** (`= currency`, usually SGD but USD for
> USD-reporting REITs) — proven: across 184 FY2025 rows with `original_value`, `market_
> valuation` never equals `original_value` (0 counterexamples). So the correct label is always
> `currency`. **APPLIED 2026-07-08:** loader fixed (`market_valuation_currency = currency`) + targeted
> DB UPDATE on the 10 **non-frozen** affected symbols (56 rows relabeled → mv_ccy now = currency;
> value/original pair untouched; 0 remaining mismatches). Frozen REITs (A17U 137, M44U 17, ME8U 1,
> J69U 1, BUOU 1, C2PU 1, N2IU 1) left as-is per freeze. No full reload — targeted UPDATE only.

## B. VERIFY then FIX (currency direction / value must be checked against a named page)

Each = confirm which currency `market_valuation` (or GR/NPI) is actually in per the cited page,
then fix the `*_currency` label (or the value). DB shows `mv_ccy != currency`: A17U 137, D5IU 29,
AU8U 18, M44U 17, SET 8, BMOU 6, HMN 6, CRPU 4, others 1–2.

- [x] **CRPU** (4), **D5IU** (29), **BMOU** (6), **AU8U** (18), **BTOU** (2), **J91U** (2), **CY6U** (2),
  **AJBU** (1), plus SET (8), HMN (6 mv) — all mv_ccy relabeled to `currency` by the loader fix above.
  **VALUE-LEVEL VERIFIED 2026-07-08 (all PASS, see `verify/RESULTS.md`):** AU8U, BMOU, D5IU, CRPU
  all tie to the AR SGD-basis columns exactly. (CRPU: emirsyah's "USD" note was wrong — it's SGD.)
- [x] ~~**C2PU**~~ — **FROZEN, skip.** (was: all should be JPY except mv in SGD, ~p52)
- [x] ~~**C38U**~~ — **FROZEN, skip.** (was: mv p109 "$" SGD/USD vs p23; purchase_price agreed value)
- [x] **M1GU** — PASS. Single-currency SGD ("presented in Singapore dollars", p127); bare "$" = SGD; 17/17 match.
- [x] **HMN** — PASS. Portfolio stmt $'000 = SGD; per-asset GR in local ccy (12 currencies) all correct.
- [x] ~~**J69U**~~ — **FROZEN, skip.** (was: carrying "$" stored SGD, affects NPI/GR labels)
- [x] ~~**ME8U**~~ — **FROZEN, skip.** (was: valuation SGD/USD, p137 vs p46/47, 10309 Wilson Blvd)
- [x] **8C8U** — DISCUSS. `currency=SGD` correct (matches p56). **emirsyah slip: #14 is AUD, not SGD**
  (Dwell East End Adelaide); SGD assets = the 5 Westlite. 9 foreign rows (8 GBP + 1 AUD) missing
  `original_value`/`original_currency` → **routed to §C `original_*` coverage** (values in RESULTS.md).
- [x] **AW9U** — PASS. "Rental income" (p43/Note 16) = **gross_revenue**, not NPI; DB placement correct.
- [x] **BTOU** — PASS/no-fix. Acquisition date already == `purchase_date` (7/7); do NOT copy to
  `effective_date` (different semantics); leave null.
- [x] ~~**A17U (PERFORMANCE note)**~~ — **FROZEN, skip.** (was: how is `portfolio_value` calc'd?)
- [x] **GR/NPI currency mismatches — VERIFIED correct (local ccy as-disclosed):** J91U (AUD×18/JPY×2),
  CY6U (INR GR/NPI vs SGD valuation), HMN (12 currencies). No mislabel. *(Frozen & excluded: C2PU, N2IU.)*

## C. Policy items — emirsyah's answers + audit outcomes (2026-07-08, see `verify_c/RESULTS.md`)

- [x] **item1 `lease_term_years` = actual base term.** DONE. ✅ FIXES (JSON+DB): J91U 36 (X+Y→X),
  AJBU 3 (excl. extensions), JYEU 1 (12.997→3). ✅ FLAG resolved per emirsyah: options-inclusive KEEP
  + `lease_terms_flags` (O5RU 25, M1GU 18, XZL 2, CY6U-Navi 1); remaining-term NULL + `lease_terms_flags`
  (UD1U 4, SET 4). New column `lease_terms_flags` (text) added. PASS: 8C8U, MXNU, Q5T, AW9U, J85, freehold.
- [x] **item2/3 dates.** DONE. ✅ SCHEMA: `lease_expiry_date`+`effective_date` `date`→text (models+
  loader+DB); no purchase_year col. ✅ effective_date = disclosed-only. ✅ purchase_date (10 REITs,
  `verify_pd/RESULTS.md`): verbatim fills (ODBU 3, DCRU 3, JYEU 1, DHLU 19) + IPO/listing-date proxy
  applied per emirsyah (ODBU 18 @2020-03-12, BMOU 5 @2015-12-11, DCRU 6 @2021-12-06, JYEU 2 @2019-10-02;
  basis noted in each `_notes.inferred[]`). ~360 rows genuinely NOT disclosed → null (HMN 100, MXNU 145,
  AJBU, UD1U, most CY6U/Q5T). DCRU Osaka 2 + BMOU Hefei correctly null. 0 schema errors.
- [x] **item4 area_unit** — DONE (0 gap; every non-frozen property with an area figure has area_unit).
- [x] **item5 DCRU valuation** — DONE. purchase_consideration=purchase_price ✅. 9/11 consolidated
  already 100% basis (FS Note 6 p182) ✅. 2 Osaka JVs (20%) left ownership-basis (100% not disclosed)
  + documented in DCRU `_notes.json` → `data_with_no_home` (JSON+DB). Per emirsyah "leave + flag".
- [x] **item6 purchase_price = verbatim** — no action (crossed off).
- [x] **item7 AW9U freehold-with-lease** — EXPLAINED: outbound master lease over freehold land;
  correct as-is. (J85 has an analogous restricting-lease; also fine.) No fix.
- [x] **item8 store-in-SGD** — AUDIT RESULT: **NO report stores a non-SGD ccy where SGD is disclosed.**
  All mv/GR/NPI as-disclosed (foreign-functional reits in own ccy; SGD-presentation reits store SGD
  where disclosed, local where only local disclosed). No action.
- [ ] **item9 `original_*`/`local_*` fields** — emirsyah: likely DROP later (covered by per-figure
  `*_currency`; local fields mostly null). **FLAG only, revisit next.** (8C8U's 9 missing originals =
  moot if dropped.)
- [ ] **T82U MBFC net income contribution** → `outline.md` §0 (frozen; T82U JV rows).

## D. CONFIRMED — no action (note just confirms a genuine null)

- NPI not disclosed at property level (segment/reit only): A17U, AJBU, C38U, K71U, ME8U, MXNU, N2IU?,
  O5RU, SET, TS0U, T82U, DCRU, M1GU, BUOU.
- gla/gfa (and often nla) genuinely undisclosed: CMOU, CY6U, DHLU, J85, J91U, JYEU, K71U, MXNU, O5RU,
  T82U, AU8U (gla), and others as noted.
- **XZL — "done"** (no issues).
- 8C8U EPU on p122/p98 — NOT a path to property NPI (EPU ≠ NPI); leave.

---

## Other-table notes captured (out of property scope, parked)

- **PERFORMANCE:** 8C8U portfolio occupancy (per note); A17U portfolio_value calc → see §B.
- **TRANSACTIONS:** AJBU "recheck, unclear"; AU8U "check purchase price vs property table" + user wants
  **all txns re-evaluated across reits** → maps to `outline.md` §5 (normalize + re-extract txns).

---

### Suggested order of attack
1. **§A fixes** (safe, mechanical) — apply + load.
2. **§B verify** — one REIT at a time against the cited AR page; I read the page, confirm, fix.
3. **§C discuss** — resolve policy with emirsyah, then batch-apply.
