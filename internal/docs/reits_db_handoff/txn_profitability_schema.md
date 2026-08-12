# Property-transaction schema — divestment/acquisition profitability & DPU linkage

**Status:** PROPOSAL (not built). Draft 2026-07-03. For review with Evelyn before any schema change.
**Scope:** `sgx_reit_property_transaction` (+ two trust-level fields on `sgx_reit_performance`).
**Evidence base:** verified against all 28 per-report audits in `docs/txn_audit/*.md` (Phase-2 verify pass, 95 rows / 69 divestments across 22 divesting REITs). Every claim below cites the REITs it was observed in.

---

## 0. TL;DR

Three questions we want the transaction table to answer, faithfully:
1. **Timeline** — *when* did each acquisition/divestment happen, and is it a **this-FY** deal, a prior-year audit-trail row, or a post-balance-sheet (subsequent) event?
2. **Profit** — did the REIT make money on a divestment, **exactly as the report states it** (never derived)?
3. **DPU linkage** — were the proceeds/gain used in a way that boosts DPU (distributed to unitholders, or used to pare debt)?

The one rule that drives the whole design: **capture what the report literally prints; never derive one figure from another.** The current data violates this in 13 places (§4), and — more importantly — deriving *cannot* generalize, because "profit on a divestment" is disclosed in several different, non-interchangeable ways (§3).

---

## 1. Existing condition

### 1.1 Current schema (`sgx_reit_property_transaction`, 28 columns)
- **Identity / deal:** `symbol, financial_year, transaction_type, status, property_name, description, transaction_date, counterparty, source_page, raw`
- **Money (5 figures + per-figure currency):** `purchase_price, gross_sale_price, net_sale_proceeds, carrying_value, valuation, gain_on_divestment` — each with a `*_currency` tag
- **Interest:** `interest_pct`
- **Provenance:** `carrying_value_basis, gain_on_divestment_basis, net_proceeds_basis`

95 rows total; **69 are divestments** (58 divestment + 9 announced + 1 partial + 1 terminated), 26 acquisitions.

### 1.2 How profitability is handled today — and why it fails
Profit is currently inferred by comparing the money columns (`gross_sale_price` − `carrying_value`, `net_sale_proceeds` − `gross_sale_price`, etc.). Two problems:

- **It manufactures figures the report never printed.** The Phase-2 audit found **13 `gain`/`carrying` values that are pure arithmetic** (see §4), self-labelled "DERIVED" in their own `_basis` notes.
- **The arithmetic is meaningless for many deals** because the reported result includes things the money columns don't:
  - **transaction costs** (net ≠ gross − nothing),
  - **FX / FCTR recycling** on foreign disposals (AW9U printed **loss S$(7,535)k *includes* S$5,193k realised FX-reserve loss**; TS0U Lippo **loss S$(26.4m)** includes **FCTR +54,614 / tax −32,323**),
  - **the IAS-40 fair-value model** — the uplift is booked as revaluation in prior periods, so at sale the P&L gain can be tiny or negative even when the sale beats the last appraisal.

### 1.3 The coverage gaps (what the reports disclose that we don't capture)
From the 28 audits: per-deal **premium/discount %** (the most common profit signal), the **baseline** that premium is measured against, whether a figure is **per-deal or aggregate**, **disposal structure** (asset vs share/subsidiary), **agreement vs completion dates**, **stake %**, and **use-of-proceeds / gain-distribution**.

---

## 2. Goal 1 — Timeline (small, mostly already works)

`transaction_date` is populated for 93/95 rows and verified accurate. The only addition is a **classifier** so the "this-FY" view is clean.

| field | type | why | source |
|---|---|---|---|
| `deal_fy_scope` | enum `current_fy` \| `prior_year` \| `subsequent_event` | separate this-FY deals from prior-year audit-trail rows and post-balance-sheet events | **derived in loader** from date vs the report's FY window (FY-end per REIT) |
| `agreement_date` | date | reports routinely print **both** an SPA/agreement date and a completion date; we keep only one | HMN Somerset (SPA 22-Oct-2024 / completion 15-Apr-2025), TS0U, XZL, CY6U all print both |
| `completion_date` | date | as above — rename/dualise the single `transaction_date` | — |

Worked examples (verified): M44U = **10 current_fy + 7 prior_year** divestments; J91U = 2 current_fy completed + **8-asset portfolio + hotel = subsequent_event**; CY6U 20.2% stake, TS0U Salesforce, XZL Livonia, 8C8U EPIISOD = subsequent_event; UD1U Il·lumina, TS0U Lippo = prior_year.

---

## 3. Goal 2 — Profit-from-divestment (the crux)

**"Did the REIT profit?" has no single answer in the filings.** Reports disclose it in up to three *non-interchangeable* ways, which can even disagree in sign. Store them separately; never collapse or derive.

### 3.1 The three concepts

**① Premium / discount — "sold X% above the baseline"** (the most commonly disclosed, often the *only* per-deal signal)
- A **percentage**, measured against one of **four baselines** — which one matters:

  | baseline | REITs (verified in md) |
  |---|---|
  | independent **valuation** | A17U, C2PU, CY6U, DHLU, HMN, J91U, K71U, M44U, ME8U, MXNU, N2IU, O5RU, ODBU, SET, XZL (15) |
  | original **purchase price** | A17U (+14%), C2PU (+25.6%), N2IU (+14%), ODBU (+4.2%) |
  | **book value** / carrying | HMN (c.50%/c.100% above book), T82U (19.6% above book) |
  | **net asset value (NAV)** | SET Slovakia (3.5% premium to NAV €67.7m) |

- Frequently disclosed **only in aggregate** across several deals (see §3.3).

**② Accounting gain/loss — the $ recognized in the P&L** (vs *carrying*, using *net* proceeds)
- From the Statement of Total Return / a Note. As-printed only.
- Per-deal examples: HMN S$17,027k / S$82,011k; N2IU S$4,006k; SET Slovakia €1,181k; ODBU Albany −US$684k; AW9U −S$7,535k; M44U Xi'an S$515k.
- Often **aggregate-only**: A17U S$19,281k (+S$3,538k subsidiary); T82U S$4,798k; SET net −€762k.

**③ Disposal structure — how the deal was legally done** (changes how ① and ② must be read)
- Many divestments sell the **shares of a property-holding SPV**, not the asset. The "gain/loss on disposal of a subsidiary" is struck against the **net assets of the disposal group** (property + cash + debt + deferred tax + NCI + FCTR recycling) — **not** the property carrying.
- Verified: TS0U (subsidiary loss incl. FCTR/tax), AW9U (subsidiary loss incl. FX-reserve), A17U Astmoor (subsidiary), SET Slovakia (subsidiary), CY6U (disposal-group net assets), BUOU 28-German (**equity transaction — no P&L gain at all**).

### 3.2 Why ① and ② diverge (and can flip sign) — the SET trap
SET sold "**11% premium to net valuation**" yet booked a **P&L net loss of €762k**. Under IAS-40 fair value, carrying ≈ last valuation (already marked up through prior-period P&L), and the premium references a *different baseline/date* than the carrying, on a *gross* basis, before costs/FX. So a "premium" sale can still book a loss. **You cannot infer profitability from one lens alone.**

### 3.3 The aggregate problem (a known limitation — deferred, not solved here)
15 REITs disclose the premium and/or gain **only at portfolio level**, never per deal (A17U ~9%, M44U 17% avg, MXNU 5%, J91U 8-asset 2.0%, SET blended 11%, T82U avg 19.6%, + HMN, BTOU, K71U, AU8U, J69U, TS0U, XZL, 8C8U, DCRU). A per-row column can't hold a group figure. **Handling for now:** where only an aggregate is printed, leave per-row `premium_pct`/`gain` **null** (never fabricate) — for those deals **per-deal profitability is genuinely not knowable; only the group-level premium/gain is**. Capturing that group number (a `deal_group_id` + aggregate row) is a later add; it doesn't block the deals that *do* disclose per-deal.

### 3.4 Proposed fields — MINIMAL CORE (3 new columns)
The entire profit model is: **`premium_pct` + `premium_basis` + the existing (as-printed) `gain_on_divestment` + a `disposal_basis` flag.** Nothing else is needed to answer "profiting or not?".

| field | type | why / source | null-rule |
|---|---|---|---|
| `premium_pct` | numeric, **signed** (+ above / − below) | the one profit number almost every report prints (§3.1); on an acquisition, negative = bought-below-valuation = accretive | null if none printed |
| `premium_basis` | enum `valuation` \| `book_value` \| `purchase_price` \| `nav` | a bare "+16%" is ambiguous — the four baselines mean very different things (§3.1) | null with `premium_pct` |
| `gain_on_divestment` | numeric — **existing column, no new field** | the accounting $ result, **as-printed only**; null the 13 derived values (§4). Kept separate from `premium_pct` because the two can disagree in sign (§3.2) | null unless the report prints a $ gain/loss |
| `disposal_basis` | enum `asset` \| `share` (default `asset`) | one guard so a share/subsidiary disposal's loss — which carries FCTR/tax, not a clean property result (TS0U, AW9U, CY6U, SET, BUOU) — isn't misread as a property loss | default `asset` |

**Dropped from the earlier draft — deferred, kept here so the verified rationale isn't lost (add only if a concrete need appears):** `premium_scope` / `gain_scope` (per-deal vs aggregate flag — §3.3); `deal_group_id` (attach an aggregate premium/gain to the row-group it covers — §3.3); `premium_valuation_date` (the baseline appraisal date; explains why ① premium and ② accounting gain diverge — §3.2, SET/DHLU print several valuation dates); acquisition `consideration` vs `total_acquisition_cost` split (ODBU/K71U/ME8U each print both — the one concrete error is fixed in §4).

### 3.5 Acquisition side — no separate machinery
`premium_pct` (negative = discount-to-valuation = accretion) already covers the 9 acquisition-accretion REITs (AW9U, DHLU, HMN, ME8U, N2IU, ODBU, SET, T82U, XZL). The only concrete acquisition data error (ODBU Dover: headline consideration vs cash-incl-costs) is fixed in §4 — no new columns.

---

## 4. Data-hygiene ledger (apply regardless of the schema decision)

These are **verified corrections** from the audits — independent of any new column, they fix existing data.

**Derived values → null (13; violate never-derive, self-labelled "DERIVED"):**
- **J91U** `gain_on_divestment` ×11 (each = `sale − valuation`; report gives only % premium; STR shows a net FV *loss*, no gain-on-divestment line)
- **HMN** Citadines `carrying_value` 128,289,000 (= `net_proceeds − gain`; only aggregate carrying S$109,494k printed)
- **MXNU** Hilden `carrying_value` 3,300,000 (= combined 4,650 − St Paul's 1,350 from FY2024 AR; circularly = sale price)

**Value fixes:**
- **J69U** `net_sale_proceeds` 34,128,000 → **34,500,000** (printed; current is a derivation)
- **ODBU** Dover `purchase_price` 17,046,000 → **16,400,000** (headline consideration, not cash-incl-costs)

**Fills (source-printed, currently null):**
- **ME8U** `counterparty` = "Nagayama Tokutei Mokuteki Kaisha" (p32)
- **O5RU** gross carrying 25,006,000 (incl. ROU 618k; net 24,388k already stored)

**Relabels / hygiene (value right, label/provenance wrong):**
- **C2PU** MOB `carrying_value_basis` note falsely says "DERIVED" — value 5,863k IS printed (Note 4 p189); fix the note only
- **O5RU** `transaction_type` → `announced_divestment`; **TS0U** Salesforce `status` field carries a scope value; **BTOU** `gross_valuation_usd` → standard valuation field
- **MXNU** acquisition `date` 2025-06-01 → 2025-06-20 (p25)
- Page-cite fixes (values right): SET ×3, T82U, AJBU, Q5T valuer attribution

**Provenance policy call:** MXNU St Paul's / Crown / Victoria `carrying_value` (1,350 / 600 / 500) come from the **FY2024 Annual Report**, not this report (FY2025 prints only combined 4,650 + 1,100). Decision needed: require same-report provenance (→ null) or keep with a FY2024-AR cite.

---

## 5. Goal 3 — DPU linkage (design locked with Evelyn: trust-level + per-deal)

The data exists in the reports and splits into **two distinct mechanisms** — keep them distinct:
- **Direct:** distribute the gain — "distribution of divestment/capital gains" / capital-gains top-up: J91U (capital distribution **S$17,405k**), ME8U (13,354k), Q5T, AU8U, HMN ("flexibility to distribute past divestment gains").
- **Indirect:** proceeds → repay debt → lower finance cost lifts DPU. N2IU is explicit: proceeds "added to DPU via lower finance costs — **NOT a distribution of the gain**." Also TS0U, MXNU, O5RU.

| level | field | type | why |
|---|---|---|---|
| **txn** (per deal) | `proceeds_use` | enum `repay_debt` \| `fund_acquisition` \| `special_distribution` \| `reinvest` \| `security_buyback` \| `general` | what the report says the proceeds funded (`security_buyback` seen in SET) |
| txn | `proceeds_use_note` | text | verbatim source phrasing + page |
| txn | `distributed_gain` | bool | was the gain distributed to unitholders? |
| **performance** (trust-level) | `capital_distribution` | numeric | the capital-distribution line (where the DPU boost actually lives) |
| performance | `gains_distributed` | numeric | the "distribution of divestment gains" figure (J91U 17,405k, ME8U 13,354k) |

Rationale for the split: whether a gain *boosted DPU* is ultimately a **distribution-statement fact** (trust-level), while *what a specific deal's proceeds funded* is per-deal. Don't let indirect debt-paydown masquerade as a gain distribution.

---

## 6. Loader / provenance notes
- `deal_fy_scope` is **derived** in `load_supabase.py` (date vs FY window) — the only computed field; everything else is copied as-reported from the extraction JSON.
- New value columns follow the existing per-figure `*_currency` convention; RMB→CNY normalization already applies.
- `premium_pct` / `premium_basis` / `disposal_basis` / `proceeds_use` are **new extraction fields** — the extractor must capture them from source (they mostly aren't in the JSON today; that's the coverage gap).
- QC gate (`schema/models.py` `PropertyTransaction`) must add the new optional fields + enum validators.

---

## 7. Open decisions for Evelyn
1. **Aggregate model:** `deal_group_id` (attach aggregate premium/gain to a row-group) vs storing portfolio-level premium/gain on `performance`. (Recommend `deal_group_id` — keeps it in the txn table where the deals are.)
2. **Same-report provenance:** are prior-year-AR-sourced carryings (MXNU ×3, M44U ~15) acceptable, or null-in-this-report?
3. **`gain` vs `premium` primacy:** confirm both are stored independently and neither is ever back-solved from the other (per §3.2).
4. **Overlap with the cockpit:** this is the acquisition/divestment-timeline section Evelyn is reviewing — align field names before build so cockpit verdicts/edits map cleanly.

---

## 8. Non-goals / invariants
- **Never derive, convert, or balance** one figure from another (the 13 defects in §4 are exactly this).
- Do not combine gross with net, or premium-to-valuation with accounting-gain-vs-carrying, in a single number.
- Only fill nulls from the report with a physical-page cite; leave genuinely-absent values null.
