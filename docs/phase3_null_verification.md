# Phase 3 — Null verification results (source-checked, distrusting _notes)

One agent per report re-read the AR to verify each >30%-null column: **MISS** (disclosed, recoverable — `_notes` was wrong), **PARTIAL**, **ABSENT** (genuinely not disclosed), or already-captured. Distrusting `_notes columns_never_fillable`.

**Headline:** the `_notes` "never_fillable" claims are WRONG in ~13 reports — whole per-property tables were skipped. **37/37 verified.** Real recovery surface below.

---

## ★ CONSOLIDATED RECOVERY WORKLIST (all 37 verified)

### Tier A — big per-property economics misses (whole tables skipped; `_notes` was wrong) — HIGH VALUE
| report | recover | where | ccy |
|---|---|---|---|
| SET | gross_revenue, nla, occupancy_rate, lease_term(LH) ×95 | Country-assets tables p80-90 | EUR |
| J91U | gross_revenue, nla, gfa, lease_expiry, lease_term(LH) ×71 | Property Particulars p70-85 | SGD/AUD/JPY |
| ME8U | nla, gfa(partial), lease_term ×99 | Detailed Property Info p44-51 | — |
| C2PU | gross_revenue, gfa ×74 | cards p40-59 | S$/¥/€ |
| N2IU | net_property_income, gross_revenue, nla, lease_expiry, occupancy, npi_pct ×18 | Properties at a Glance p46-49 | S$/HKD/etc |
| AU8U | net_property_income, gross_revenue, npi_pct ×17 | p26-27 | SGD |
| CMOU | net_property_income, gross_revenue, npi_pct ×13 | p37-38 | USD |
| CY6U | net_property_income, gross_revenue ×13, gfa(4) | p25-26 | **INR only** |
| P40U | net_property_income, gross_revenue, nla, npi_pct ×9 (+China gfa/lease) | Property Highlights p28-29 | SGD |
| HMN | gross_revenue ×103 | Operations Review p29-52 | **local ccy** |
| CRPU | net_property_income, gross_revenue, npi_pct, lease_term ×4 | segment Note 23 p194 | SGD |

### Tier B — small/targeted recoveries
| report | recover |
|---|---|
| J69U | NEX/Waterway NPI+GR (100% basis); **gfa remap from `gla` field**; npi_pct; occupancy (S Wing) |
| K71U | npi_pct ×13 (p64/65) |
| TS0U | gfa ×4 non-hotel (p42-48) |
| J85 | gfa ~10, nla 2, occupancy 2 (living assets) |
| C38U | lease_term (ION 99yr), lease_expiry (66 Goulburn) + ION land_tenure/effective_date |
| DCRU | net_property_income (Frankfurt only) |
| XZL | lease_term ×2 (leasehold hotels) |
| AW9U | gross_revenue ×2 (Japan cards) |

### Cross-cutting
- **Per-property NPI/revenue is often in LOCAL currency** (CY6U INR, HMN local, C2PU mixed) → store value + currency using the Tier-0 `net_property_income_currency`/`gross_revenue_currency` cols; don't force SGD.
- **`npi_pct` is derivable** (NPI ÷ portfolio NPI) wherever per-property NPI is recovered — a computation, not a re-extraction.
- **Field-mapping fix**: J69U per-property GFA sits in `gla`; UD1U "lettable area" in `gla` may belong in `nla`. Audit `gla` vs `gfa`/`nla` across all reports.
- **`distribution_paid` policy cluster** (disclosed but deliberately nulled, ~13 reports): clean for-year figures exist for M1GU (39,715) & O5RU (78,154); the rest are period-mixed cash rollforwards. **Decide once**: cash-paid-in-year (recover all) vs for-year-declared (leave most null).

### Confirmed genuinely ABSENT (no action — `_notes` correct)
A17U, BMOU, 8C8U, BUOU, BTOU, MXNU, D5IU, JYEU, Q5T, OXMU, UD1U, T82U, M44U (per-property NPI/nla/gfa), O5RU (per-property NPI), ODBU. Hospitality (HMN/J85/Q5T/XZL) NPI/occupancy/area absent by nature (use RevPAR/keys). Freehold assets: no lease term/expiry by nature.

### Corrections to earlier Stage-C guesses
- CY6U `wale`/`weighted_avg_debt_maturity` genuinely ABSENT (not misses).
- OXMU 71% "retention" is genuine capex retention (correctly handled, not a bug).

---

## Confirmed RECOVERABLE misses (─ `_notes` was wrong)
| report | columns | source | notes |
|---|---|---|---|
| CMOU | net_property_income (13), gross_revenue (13), npi_pct (derive) | NPI-by-asset p38, GR-by-asset p37 (US$m) | reconciles to portfolio totals |
| AU8U | net_property_income (17), gross_revenue (17), npi_pct (derive) | NPI/GR-by-property p26-27 (RMB **and SGD**) | `_notes` wrongly said RMB-only |
| C2PU | gross_revenue (74), gfa (74) | per-property cards p40-59 | gross_revenue mixed ccy (S$/¥/€) → needs per-figure currency |
| CRPU | net_property_income (4), gross_revenue (4), npi_pct (derive), lease_term_years (4) | Note 23 segment p194 (S$'000); Statement of Portfolio p159 | EMA model: NPI≡revenue; lease term already in tenure_raw |
| ME8U | nla (99), gfa (partial — US DCs have none), lease_term_years | Detailed Property Info p44-51 | NPI segment-only (absent) |
| J69U | net_property_income (NEX, Waterway 100% basis), gross_revenue (same), gfa (**remap from `gla`**), npi_pct (derive), occupancy (S Wing) | portfolio overview p68 | South Wing NPI/GR/NLA genuinely combined w/ North Wing |
| AJBU | gfa PARTIAL (13 disclosed already; 12 genuinely "–") | cards p40-44 | not a net gain |

**⚠️ Cross-cutting: `gla` vs `gfa` mapping gap** — J69U's per-property GFA is stored under the `gla` field, not `gfa`. Check whether this misplacement is systemic (gla is 99% null in DB; some reports may have put GFA there or vice-versa).

## Policy-null (disclosed, deliberately nulled for distribution-basis reasons — decide, don't auto-fill)
| report | column | disclosed value | basis reason |
|---|---|---|---|
| AJBU | distribution_paid | S$133,531k (cash, straddles periods) | rollforward mixes prior-yr final |
| AU8U | distribution_paid | S$88,743k cash / 83,900k for-year | full_payout_no_retention_line |
| C2PU | distribution_paid | S$65,436k | full_payout_no_retention_line |

## Confirmed ABSENT / already-captured (no action)
- **BMOU** — all per-property fields already captured & reconcile; adjusted_DI genuinely absent.
- **8C8U** — NPI segment-only (PBWA/PBSA); size = beds not NLA; occupancy per-property already filled; adjusted_DI absent.
- **BUOU** — per-property NPI absent (segment-only); GFA absent (NLA only); lease nulls = freehold; distribution_paid/adjusted_DI absent.
- **BTOU** — NPI/GR already captured; GFA absent (NLA only); freehold → no lease; adjusted_DI absent (distributions halted).

### More recoverable (round 2)
| report | columns | source | notes |
|---|---|---|---|
| AW9U | gross_revenue (2 Japan cards) | property cards p28 (S$0.6m, S$0.4m) | `_notes` wrongly said cards unparsed |
| CY6U | net_property_income (13), gross_revenue (13) — **INR only**; gfa (4 combined rows) | fin review p25-26 (INR m + %) | per-property only in local ccy, not SGD |
| HMN | gross_revenue (103) — **local ccy** (AUD/etc.); wale subset | Operations Review p29-52 | needs per-figure currency + FX |
| DHLU | distribution_paid (policy-null, S$32,032k p205) | Distribution Statement | intentional null, not undisclosed |

### Cross-cutting theme (big): per-property NPI/revenue is often disclosed **only in LOCAL currency**
CY6U (INR), HMN (AUD/local), C2PU (S$/¥/€), DHLU (JPY), AU8U (had SGD too). Recovering these needs the **Tier-1 per-figure NPI/GR currency columns** (already added `net_property_income_currency`/`gross_revenue_currency` in Tier-0). So the recovery pass must store local value + currency, not force SGD.

### Correction to earlier guesses (verified ABSENT, NOT misses)
- **CY6U `wale` & `weighted_avg_debt_maturity`** — genuinely ABSENT (AR gives only lease-expiry-by-revenue-% and debt-maturity-by-year-$; no single weighted-avg-years figure). Overturns the Stage-C "likely miss" flag.

### Policy-null cluster (distribution_paid — disclosed but deliberately nulled for basis reasons)
AJBU, AU8U, C2PU, DHLU, AW9U — all have the cash-distributed figure disclosed; nulled under the Phase-1 distribution-basis harmonization. **Decide once** whether `distribution_paid` should mean cash-paid-in-year (recover all) or for-year-declared (leave null).

---

### Round 3 (post-reset) recoverable
| report | columns | source | notes |
|---|---|---|---|
| **J91U** | gross_revenue, nla, gfa, lease_expiry_date, lease_term (leasehold) — ×71 | **Property Particulars pp70-85** (whole section missed) | biggest single miss; per-country ccy (SGD/AUD/JPY) |
| **N2IU** | net_property_income, gross_revenue, nla, lease_expiry, occupancy, npi_pct (derive) — ×18 | "Properties at a Glance" cards p46-49 | MBC combined (I/II not split); Festival Walk HKD |
| K71U | npi_pct (13) | "Attributable NPI by Property %" p64/65 | MBFC combined |
| DCRU | net_property_income (Frankfurt only) | EMEA segment note | rest freehold/associate |
| C38U | lease_term (ION 99yr), lease_expiry (66 Goulburn) | cards p43, p58 | + ION land_tenure/effective_date bonus |
| M1GU | distribution_paid (39,715 declared) | Manager's Review p20 | NPI segment-only |
| O5RU | distribution_paid (78,154 for-year) | Financial Review p32 | NPI segment-only |
| M44U | distribution_paid (policy call) | Distribution Statement p122 | per-property NPI/nla/gfa absent |
| ODBU | distribution_paid (policy call) | p161 | rest segment-only |

Round-3 ABSENT (verified, nothing recoverable): JYEU (dev-site/freehold/associate).

### Round 4 (batch 2) recoverable
| report | columns | source | notes |
|---|---|---|---|
| **SET** | gross_revenue, nla, occupancy_rate, lease_term (leasehold) — ×95 | **"Country assets" tables p80-90** (whole section missed) | `_notes` wrong on 3 cols |
| **P40U** | net_property_income, gross_revenue, nla, npi_pct (derive) — ×9; gfa + lease_term (China only) | Property Highlights p28-29 | `_notes` wrongly said single-segment |
| TS0U | gfa (4 non-hotel: OUE Bayfront, One Raffles Place, OUE Downtown Office, Mandarin Gallery) | Portfolio Overview p42-48 | NPI segment-only |
| J85 | gfa (~10 assets), nla (2), occupancy (2 living assets) | property cards | hotels use keys (absent) |
| XZL | lease_term (2 leasehold hotels) | footnotes p14 | rest absent-by-nature |

Round-4 ABSENT (nothing recoverable, `_notes` correct): OXMU (single-segment; 71% retention genuine), Q5T (hospitality segment-only), UD1U (geography-segment only; freehold).

### T82U (final) — none cleanly recoverable
JV cards below-NPI only, freehold, NLA-only; wale segment-level (office 3.80/retail 2.42); distribution_paid cash-basis. `_notes` held up.

**✅ ALL 37 VERIFIED.**

---

## ✅ RECOVERY PASS COMPLETE (2026-07-02, applied to Supabase)
28 Sonnet agents (19 property + 9 distribution_paid). All schema-gate PASS; all 37 reloaded. Active-property fill deltas:
| column | before → after |
|---|---|
| gross_revenue | 68% → **95%** |
| occupancy_rate | 81% → **90%** |
| nla | 45% → **63%** |
| gfa | 25% → **37%** |
| net_property_income | 7% → **12%** (rest genuinely segment-only) |
| npi_pct | 1% → **5%** |
| distribution_paid (perf) | 22/37 → **37/37** |
Per-figure currency tags: 1,530 gross_revenue + 192 NPI. `distribution_paid` = cash-paid-in-year basis, each with a `distribution_paid_basis` flag. CY6U NPI/GR normalized to full INR units (×1e6).

### ⚠️ Follow-ups flagged during recovery — RESOLVED in round 2 (2026-07-02)
- **J69U `nla` column-shift** — ✅ RESOLVED: verified all NLA/GFA against source pp.68-69; already correct (fixed in round 1). No change needed.
- **ME8U Tempe** `2055 East Technology Circle` — ✅ FIXED: source p44 Term-of-Lease table = "58 years" with footnote "tenure of underlying land"; it is the sole leasehold among freehold US assets. Corrected `land_tenure`→Leasehold, `tenure_raw`→"58 years"; flag now `tenure_resolved`.
- **J91U 21/23 Ubi Road 1 valuation** — ✅ FIXED: `market_valuation` 41.7m→42.5m. Round-1 mis-read an adjacent row; source p73 valuation table (row: purchase 25.0, rental 4.2) and p2074 divestment footnote 10 both give S$42.5m.
- **Combined-row skips (correct, still null)**: N2IU MBC I/II, J91U 6/8 & 2/4 Changi Business Park, J69U Northpoint City South Wing — re-confirmed unsplittable; noted.
- **`gla`↔`gfa`↔`nla` mapping** — still open (Tier-1/3): P40U David Jones/Plaza/China correctly kept in `gla`/`gfa` (source labels GLA/GFA, not NLA — do NOT move); UD1U lettable area in gla. Systematic normalization deferred.
- **npi_pct not computed for JV assets** (J69U NEX/Waterway, etc.) — correct to leave null (consolidated portfolio NPI excludes equity-accounted JVs).
- **NEW open discrepancies (flagged, NOT changed)**: M44U `Flexhub.gross_revenue`=1,251,000 may be mis-mapped from the MYR125.1m sale price (see M44U `_notes.json`); J69U Northpoint City North Wing stored NPI/GR is actually the combined Northpoint (N+S wing+Yishun10) figure per p34 footnote 1.
