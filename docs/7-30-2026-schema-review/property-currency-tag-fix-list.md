# `sgx_reit_property` — currency-tag audit and fix list

Audited 2026-07-31. Every REIT-year holding at least one non-SGD `market_valuation_currency` tag,
tested both ways against the REIT's own reported `portfolio_value`.

**The fix is NOT uniform.** Some tags are correct and the values need converting; others are wrong
and the values are already SGD. A single blanket operation would destroy one group or the other.

---

## Method

For each REIT-year with non-SGD tags, two hypotheses were tested:

```
H1  values are ALREADY SGD, the tags are spurious   -> sum as-is
H2  values are genuinely NATIVE                      -> sum converted at each tag's rate
```

Whichever lands on the REIT's own `portfolio_value` (itself normalised to SGD from its presentation
currency) is the truth. FX from `quarterly_rates.json` (MAS quarterly rates, nearest quarter to the
FY-end date).

Result: **Group A 17 REIT-years · Group B 7 · unresolved 6.**

---

## GROUP B — tag is WRONG, values already SGD → **STRIP THE TAG, DO NOT CONVERT** (7)

| sym | fy | rows | tags | sum as-is | sum converted | portfolio_value |
|---|---|---|---|---|---|---|
| C2PU | 2024 | 75 | EUR:11, JPY:60, MYR:1 | **2,462,695,000** | 1,841,748,590 | 2,462,695,000 |
| K71U | 2024 | 14 | AUD:7, JPY:1, KRW:1 | **9,531,621,000** | 8,895,740,192 | 9,531,621,000 |
| N2IU | 2023 | 19 | CNY:2, HKD:1, JPY:9, KRW:1 | **16,499,455,000** | 10,158,979,253 | 16,499,500,000 |
| M44U | 2023 | 187 | AUD:14, CNY:43, HKD:9, INR:3, JPY:… | **13,088,234,000** | 4,508,441,295 | 13,183,234,000 |
| A17U | 2024 | 229 | AUD:34, EUR:7, GBP:42, USD:48 | **17,027,180,000** | 18,429,463,962 | 16,758,446,000 |
| A17U | 2025 | 223 | AUD:33, EUR:7, GBP:41, USD:47 | **18,227,043,000** | 19,638,720,904 | 18,202,446,000 |
| BUOU | 2024 | 113 | AUD:1, EUR:1, GBP:1 | **6,928,373,000** | 6,984,784,124 | 6,773,200,000 |

**C2PU, K71U and N2IU match to the dollar** left alone — conclusive.

**M44U is the danger case.** Converting would take its portfolio from **S$13.1bn to S$4.5bn**, an
S$8.6bn loss. Any blanket conversion pass must not touch this group.

### Corroborating evidence, independent of this audit

The transaction rebuild cross-check (`txn_rebuild/_RESULTS.md` §6) hit the same rows from a
different direction, and the discrepancy ratios came out as **exact exchange rates**:

```
M44U Celestica Hub   ratio 3.518   quarterly_rates: 1 SGD = 3.5125 MYR
M44U Linfox          ratio 3.518   "
M44U Zentraline      ratio 3.518   "
M44U Xi'an           ratio 5.398   quarterly_rates: 1 SGD = 5.3619 CNY
M44U Aichi / Toki    ratio 110.9   quarterly_rates: 1 SGD = 112.3  JPY
C2PU MOB Clinics     ratio 3.127   MYR
```

Two methods, same conclusion.

### Fix

Set `market_valuation_currency = 'SGD'` (or NULL) on these rows. **Do not touch the values.**

---

## GROUP A — tags are RIGHT, values are native → **CONVERT** (17)

| sym | fy | rows | tags | sum as-is | sum converted | portfolio_value |
|---|---|---|---|---|---|---|
| BTOU | 2024 | 9 | USD | 1,137,200,000 | **1,546,933,160** | 1,546,933,160 |
| BTOU | 2025 | 7 | USD | 901,403,000 | **1,157,491,592** | 1,157,491,592 |
| CMOU | 2024 | 13 | USD | 1,326,410,000 | **1,804,315,523** | 1,804,315,523 |
| CMOU | 2025 | 13 | USD | 1,325,370,000 | **1,701,907,617** | 1,701,907,617 |
| ODBU | 2024 | 22 | USD | 752,860,000 | **1,024,115,458** | 1,024,115,458 |
| ODBU | 2025 | 22 | USD | 774,250,000 | **994,214,425** | 994,278,630 |
| OXMU | 2024 | 13 | USD | 1,352,070,000 | **1,839,220,821** | 1,839,220,821 |
| OXMU | 2025 | 13 | USD | 1,399,600,000 | **1,797,226,360** | 1,797,226,360 |
| XZL | 2024 | 33 | USD | 728,000,000 | **990,298,400** | 990,298,400 |
| XZL | 2025 | 32 | USD | 714,900,000 | **918,003,090** | 918,003,090 |
| MXNU | 2025 | 148 | GBP | 425,100,000 | **734,912,880** | 734,221,360 |
| SET | 2024 | 105 | EUR | 2,240,947,000 | **3,173,180,952** | 3,160,274,112 |
| SET | 2025 | 96 | EUR | 2,155,023,000 | **3,249,128,177** | 3,253,462,815 |
| UD1U | 2024 | 54 | EUR | 888,208,000 | **1,257,702,528** | 1,213,983,528 |
| UD1U | 2025 | 53 | EUR | 804,280,000 | **1,212,612,956** | 1,203,295,370 |
| ME8U | 2023 | 85 | JPY:1, USD:43 | 7,743,797,000 | **8,438,382,991** | 8,802,200,000 |
| J91U | 2024 | 72 | AUD:18, JPY:2 | 62,260,300,000 | **4,951,576,810** | 4,950,600,000 |

Several match the portfolio total **exactly** after conversion (BTOU, CMOU, ODBU 2024, OXMU, XZL) —
conclusive.

**J91U 2024 is the extreme case**: as-is sums to S$62.3bn, converted to S$4.95bn, against a reported
S$4.95bn. Its AUD/JPY rows are unambiguously native.

### Fix

Convert `market_valuation` to SGD at the FY-end rate, then set the tag to SGD — **but only after
Group B's tags have been stripped**, or the conversion pass will catch them too.

---

## UNRESOLVED — neither hypothesis fits within 5% (6)

| sym | fy | rows | tags | sum as-is | sum converted | portfolio_value | note |
|---|---|---|---|---|---|---|---|
| C38U | 2024 | 26 | AUD:3, EUR:2 | 29,458,705,000 | 29,636,842,018 | 26,034,900,000 | both ~13% high |
| ME8U | 2024 | 99 | USD:13 | 9,801,962,000 | 10,424,628,000 | 9,144,300,000 | both high |
| ME8U | 2025 | 95 | USD:13 | 9,026,073,000 | 9,562,705,860 | 8,315,600,000 | both high |
| DCRU | 2024 | 10 | USD:10 | 1,959,618,000 | 2,665,668,365 | 2,209,263,230 | between the two |
| DCRU | 2025 | 11 | USD:11 | 2,207,226,000 | 2,834,298,907 | 2,346,949,570 | between the two |
| MXNU | 2024 | 10 | GBP:10 | 115,200,000 | 196,692,480 | 710,619,880 | **6x short** |

### RESOLVED 2026-07-31 — none of the six is a currency problem

All six were investigated against their annual reports. Every one is a **scope or basis** mismatch,
not a tagging error. **No currency fix is required for any of them.**

#### ME8U 2024 + 2025 — joint-venture assets excluded from the audited statement

ME8U's 13 US data centres are held via **MRODCT**, a 50%-owned JV. Equity-accounted, so they appear
in the consolidated accounts as a single *"Investment in a joint venture"* line (S$523,743k) and are
**absent from the audited Portfolio Statement**. Our table keeps all 13 as rows.

```
86 consolidated properties  = S$7,975,962,000  = the reported fair value, exactly
13 JV properties (USD, 100% basis)             = correctly absent from that total
99 rows summed                                 = always overshoots
```

Our own `_notes.json` already said so: *"Their absence from the consolidated Portfolio Statement Σ
is correct, not a miss."* The 13 USD tags are **correct**.

Reconcile with `value_basis != 'equity_accounted_jv'`.

#### C38U 2024 — proportionate vs 100% ownership basis

The AR's footnote: *"Includes CICT's **proportionate interests** in CapitaSky (70.0%), ION Orchard
(50.0%), CapitaSpring (45.0%), Gallileo and Main Airport Center (94.9% respectively), and 101-103
Miller Street & Greenwood Plaza (50.0%)."*

We store the 100% value in `market_valuation`; the reported total uses CICT's share — **and the
share figures are already in our `alt_value` column**, matching the AR exactly:

| property | `market_valuation` (100%) | `alt_value` (share) | AR reports |
|---|---|---|---|
| ION Orchard | 3,697,900,000 | 1,848,500,000 | 1,849.0m (50%) |
| CapitaSpring | 2,058,500,000 | 926,300,000 | 926.3m (45%) |
| CapitaSky | 1,263,000,000 | 884,100,000 | 884.1m (70%) |
| Gallileo | 383,226,000 | 363,700,000 | 363.7m (94.9%) |

Substituting `alt_value` takes the 26-row sum from ~S$29.6bn to ~S$26.0bn vs a reported
S$26,034.9m. ION Orchard and CapitaSpring are additionally flagged
`excluded_from_portfolio_statement` in our data. **Nothing to re-extract** — the reconciliation
must use the right column.

#### MXNU 2024 — genuinely incomplete, and correctly so

*"Comprising 149 Properties as at 31 December 2024"*, portfolio value **£416.2 million**. The AR
itemises only the **top 10 by valuation** (p34-37); the other 139 are never individually disclosed
anywhere in the report. Our 10 rows sum to £115.2m — exactly those top-10 cards.

Already documented in our notes: *"The remaining ~139 properties are NOT itemised anywhere in the
AR ... Not a parsing miss."* A source-document limitation. **Nothing to fix.**

> Open question, assumed rather than verified by the investigating agent: why FY2025 holds 148 rows
> when FY2024 holds 10. If FY2025's rows did not come from the AR, that needs its own answer.

#### DCRU 2024 + 2025 — two different metrics that were never meant to reconcile

Every DCRU property row is genuinely USD; **nothing is silently pre-converted**. The gap is that the
two figures being compared come from different disclosures:

- `properties.market_valuation` — 9 majority-owned assets at **100% consolidated** value from the
  audited Note 6, plus the equity-accounted JVs (Digital Osaka 2, and Osaka 3 in FY2025) at their
  **20% share**, flagged `value_basis: "effective_interest"`. Mixed basis by design, each row correct.
- `performance.portfolio_value` — the AR's headline **AUM at ownership/pro-rata share for every
  asset**, from p31, a different table entirely.

The 9 consolidated rows sum to **1,852,018,000 = the audited Note 6 balance exactly**.

The "lands between the two hypotheses" appearance is coincidence: prod's figure is simply
`performance.portfolio_value` FX-converted (1,624,100,000 × ~1.3603 ≈ 2,209,263,230 ✓).

---

## Consequence for the audit method itself

The test used here — *sum of property valuations = reported portfolio value* — holds only for
**wholly-owned, fully-consolidated, fully-disclosed** portfolios. It breaks legitimately on:

- equity-accounted JV rows (ME8U, DCRU)
- proportionate-vs-100% basis (C38U, DCRU)
- partially-disclosed portfolios (MXNU)

The Group A / Group B classification above is still sound — those 24 REIT-years matched one
hypothesis closely, several to the dollar — but before this becomes an automated gate it needs to
filter JV rows, apply ownership, and skip REITs whose ARs disclose only part of the portfolio.

**Also unresolved and worth its own look:** `performance.portfolio_value` is not a consistent
concept across REITs. For ME8U it appears to be an AUM-style figure (9,144,300,000) that matches
neither the audited Portfolio Statement (7,975,962,000) nor the balance sheet (8,080,101,000); for
DCRU it is explicitly at-share AUM. If it means different things per REIT, it should not be used as
a reconciliation target anywhere.

---

## Fix order

1. **Group B first** — strip the spurious tags (7 REIT-years, ~840 rows). Values untouched.
2. **Group A second** — convert (17 REIT-years, ~730 rows). Must run after step 1.
3. **Unresolved** — investigate per REIT against the AR; no blanket rule.
4. Re-run this audit; every REIT-year should then land in Group A or B with <5% error.
5. Only then enable the transaction cross-check invariant
   (`reference_value ≈ property.market_valuation × interest_pct`) as a gate — it cannot be trusted
   until the tags are right.

---

## Related

- `txn_rebuild/_RESULTS.md` §6 — the independent confirmation from the transaction rebuild.
- `docs/7-30-2026-schema-review/performance-normalization.md` — where Group A/B was first identified.
- `scripts/db/build_final_tables.py` — the silent currency fallback
  (`ccy = d.get(ccol) or d.get('currency')`) that lets a missing per-figure tag inherit the row
  currency. Should raise instead. This is how the DCRU 770,936 artifact was produced.
