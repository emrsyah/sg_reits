# `sgx_reit_property_transaction` — can we get ONE uniform gain metric?

Follow-up to `property-transaction-verification.md`, prompted by the reaction that this table is
confusing and not mature: *"can't we just take sale price − purchase price and get a percentage?"*

Tested empirically against all 206 prod rows (136 divestments, 70 acquisitions), plus three
independent Sonnet passes over the annual reports. Verdict first, evidence after.

---

## Verdict

**The colleague's formula does not work — it has the worst coverage of every option tested (31%).**
But the underlying instinct is right: there *is* one uniform convention. It just isn't
"sale − cost". It is **premium/discount against a stated reference value**, which is what the
annual reports themselves use, universally.

We already have that field (`gain_loss_pct`, 71% of divestments — our best-covered gain signal).
It is currently unusable because it is **stored in two different units, against two different bases,
with no flag saying which**. Fix that, and the table becomes uniform without inventing anything.

---

## 1. Why `sale_price − purchase_price` fails

### Coverage: worst of six options

| candidate | divestment rows | coverage |
|---|---|---|
| `sale − (carrying OR valuation)` | 99/136 | **73%** |
| `gain_loss_pct` | 96/136 | 71% |
| `sale − valuation` | 90/136 | 66% |
| `sale − carrying_value` | 70/136 | 51% |
| disclosed `gain_on_divestment` | 53/136 | 39% |
| **`sale − property.purchase_price`** | **42/136** | **31%** |

The failure is structural, not a filling problem. `purchase_price` is 81% populated across
`sgx_reit_property` (2,774/3,420) — but **a property divested during the year is removed from the
property table**, so precisely the rows we need are the ones that disappear. Only 85 of 136
divestments still match a property row by name; only 55 of those retain a purchase price.

### The annual reports almost never disclose original cost

Checked 10 divested properties across 9 REITs. **1 of 9 disclosed the original purchase price** —
N2IU Mapletree Anson, which states all three bases in one sentence:

> *"The divestment consideration of S$775.0 million exceeded the property's independent valuation of
> S$765.0 million as at 31 March 2024 by S$10.0 million and its **original purchase price of S$680.0
> million by S$95.0 million**."*
> — `parsed_reports_datalab/29_N2IU.SI_Mapletree-Pan-Asia-Commercial-Trust_FY2023/full.md:1897`

Management cited it because S$95m is a better headline than S$10m. For ME8U, C38U, HMN (×2), AU8U,
J69U, T82U, P40U and M44U it is **NOT_FOUND anywhere in the report**.

### And it is the wrong metric under fair-value accounting

Investment properties are remarked to fair value every period (SFRS(I) 1-40). "Book value" therefore
already *equals* the last valuation, not historical cost. The uplift from original cost was booked
through revaluation over the holding period — it is not a divestment gain. Sale minus a 2013
purchase price restates a decade of revaluation as if it were realised in one year.

**This is the argument to give the colleague:** the formula is not merely uncovered, it would
double-count gains already recognised in prior years' revaluation.

---

## 2. What the reports DO use — and it is consistent

Every report frames a divestment as a premium/discount against one stated reference:

> ME8U: *"The sale price represented an 8.4% premium above **book value**"*
> T82U: *"...divested at an average price of **24.5% above book value**"*
> J69U: *"...after taking into account the **independent valuation** of $325.0 million as at 31 July 2023"*
> P40U: *"...compared to the **valuation** of approximately S$32 million as at 30 June 2024 by CBRE Pte. Ltd."*
> HMN: *"The consideration is approximately **50% above the property's carrying value**"*

Two reference bases are in use — independent valuation and book/carrying value — and the REIT picks
one. That choice is real information, not noise. It is already captured in `gain_basis`
(`vs_valuation` 111 · `vs_book_value` 28 · `vs_cost` 1).

---

## 3. Why `gain_loss_pct` is unusable TODAY (the actual root cause of the confusion)

### Defect A — two units in one column

Tested each value against an independent recomputation from `sale_price` and its base:

```
stored as PERCENT  (18 means 18%)    32
stored as FRACTION (0.18 means 18%)  22
ambiguous                            30
not checkable (no sale or no base)   46
```

**Four REITs use both conventions internally: A17U, MXNU, N2IU, SET.** BTOU carries both in the same
financial year — Peachtree as `3`, Plaza as `0.1854`.

| row | stored | means |
|---|---|---|
| M44U 8 Loyang Crescent | `17.3` | 17.3% |
| C2PU MOB Specialist Clinics | `21` | 21% |
| BUOU 357 Collins Street | `0.0058` | 0.58% |
| AU8U CapitaMall Yuhuating | `0.0367` | 3.67% |

Any sort, average or filter over this column is currently meaningless.

### Defect B — a confirmed 10× error

ME8U Tanglin Halt Cluster stores `gain_loss_pct = 84.0`. Its AR:

> *"The sale price represented an **8.4%** premium above book value"*

### Defect C — the base is not recorded in a machine-usable way

Most of the 30 "ambiguous" rows are not unit errors — they are measured against a *different base*
than their siblings. HMN Somerset stores `50.0`, correct against carrying value
(*"approximately 50% above the property's carrying value"*), while neighbouring rows use valuation.
`gain_basis` knows this but is named as though it describes the dollar gain, and is absent on 66 rows.

---

## 4. Why `carrying_value` cannot be silently merged with `valuation`

Where both exist (73 rows), they agree within 2% on 44 of them (60%) — which initially suggested
collapsing them into one reference column. **The provenance evidence says do not**, because
`carrying_value` is at least four incompatible concepts. Our own `carrying_value_basis` notes say so:

| meaning | rows (of 9 checked) | evidence |
|---|---|---|
| Clean prior-FYE book value | 2 | ME8U: *"Book value as at FY2022/2023 year end (31 Mar 2023)"* — disposal was 27 Mar 2024, ~1 year later |
| **Derived from the gain (circular)** | 2 | HMN Citadines: *"DERIVED: net_proceeds 210,300 − gain 82,011 = 128,289"* |
| Aggregate over several properties | 5 | A17U: *"Page 28 discloses only aggregate S$64.2m sale consideration for the trio"*; P40U: *"A total of 13 strata units ... with carrying value of $31.9 million"* |
| Conflated with valuation | 1 | J69U Changi City Point: `carrying_value == valuation == 325,000,000` |
| Subsidiary-disposal figure | 1 | AU8U: gain measured vs *net identifiable assets* S$130,471k, not IP carrying value S$156,570k |

The circular rows matter for verification: on those, `sale − carrying` reproduces the disclosed gain
**by construction**, because the carrying value was back-solved from it. Part of the earlier
"3 rows reconcile to carrying_value" result was this artifact, not confirmation.

Where the two bases genuinely diverge, they diverge a lot:

```
HMN  Somerset Olympic Tower Tianjin   carrying 51,316,000   valuation 75,500,000   -32.0%
T82U Suntec City Office (strata)      carrying 34,402,000   valuation 47,100,000   -27.0%
A17U 92 Sandstone Place               carrying 23,728,000   valuation 19,300,000   +22.9%
```

**Conclusion: keep both as raw inputs, label the base explicitly. Never merge silently.**

---

## 5. Aggregate rows are a separate defect that breaks ANY per-row metric

Three rows pack multiple properties into one record with one shared price:

- **A17U FY2024** — one S$64.2m consideration and one S$628,000 gain for *three* properties, stored
  identically on all three rows. Summing triples both.
- **T82U FY2024** — six strata units, one aggregate carrying amount S$34.402m; a 7th unit
  (S$13.126m) completed post-year-end and is excluded.
- **P40U FY2024** — *"A total of 13 strata units ... divested during the current period"*, no single
  completion date exists.

No choice of base fixes these. They need an `is_aggregate` flag (or splitting), or every portfolio
roll-up silently misstates.

---

## 6. Genuine absences — the honest ceiling

Re-checked the thin rows against source. **Most "gaps" were my own bad query, not missing data** —
BUOU 357 Collins, AW9U Imperial Aryaduta, BTOU Peachtree/Plaza, AU8U Yuhuating, C2PU MOB and the
M44U divestments all have valuation, carrying value and/or gain present in prod. An agent's
resulting "loader bug" conclusion was **false** and is recorded here so it is not repeated.

One genuine disclosure gap confirmed: **XZL FY2024's three Hyatt divestments.** The AR pools the
figures across hotels *and* across the ACRO-REIT/ACRO-BT sub-entities, never per property:

> *"Sale completed during the financial year | (34,373) | (7,675) | (1,904) | (234) | (38,742) | (7,880)"*
> — Note 11 "Assets Held for Sale", p139

Nothing to extract. `sale_price` only is correct for those rows.

**Ceiling: 73% of divestments on `sale − (carrying OR valuation)`, 77% if prior-year property
valuation is allowed as a labelled fallback** (available on 52 rows; agrees with stored carrying
value on 28 of 39 testable — the 11 disagreements are real, e.g. BTOU Plaza 0.75×, ODBU Albany 0.74×,
so it is a fallback, not a substitute).

---

## 7. Proposal — one uniform metric, honestly labelled

Do **not** invent a new derivation. Normalise the one that already has the best coverage, and say
what it is measured against.

### Add / fix

```sql
gain_loss_pct          numeric   -- ONE unit: percent (8.4 means 8.4%). Fix the 22 fractions + ME8U 84.0
gain_loss_pct_basis    text      -- was gain_basis; NOT NULL where gain_loss_pct is set
                                 -- enum: vs_valuation | vs_book_value | vs_cost
gain_loss_pct_source   text      -- NEW: disclosed | derived   (M44U's are derived; label them)
is_aggregate           boolean   -- NEW: row covers multiple properties (A17U, T82U, P40U)
```

### Keep as-is

- `gain_on_divestment` — **as-disclosed only, never derived.** 39% coverage is the truth; 9 of 12
  checked match the AR verbatim. Deriving it is what produced the confusion in the first place.
- `valuation` + `carrying_value` — genuinely different facts; both feed the pct, neither is redundant.
- `net_sale_proceeds` — distinct concept (gross minus disposal costs); always differs where both exist.
- `interest_pct` — several prices are on an attributable basis (AJBU Tokyo DC3 = 98.47%).

### Drop / merge

- `purchase_price` + `sale_price` → **`transaction_price`.** 0% of divestments carry a purchase
  price; 12 acquisitions carry a spurious duplicate `sale_price`, one of them corrupted
  (DCRU 770,936) by the silent currency fallback.
- `announced_date` (26%) and `transaction_date` — `transaction_date` never disagrees with
  `completed_date` on the 174 rows where both exist.

### Result

One column an investor can sort and compare across every REIT — `gain_loss_pct`, in percent, with
its base and its provenance attached — at ~71% coverage rising toward 73–77% once the
derivable rows (BTOU Peachtree/Plaza have valuation + carrying but no pct) are filled.

---

## Action order

**Mechanical, no decision needed:**
1. Normalise `gain_loss_pct` to percent across all 130 rows; fix ME8U Tanglin Halt `84.0` → `8.4`.
2. Backfill `gain_basis` on the rows where it is null but the base is determinable.
3. Flag the three aggregate rows (A17U ×3, T82U, P40U).
4. Merge `purchase_price` + `sale_price` → `transaction_price`; null the 12 spurious acquisition
   sale prices at the extraction layer.
5. Make the currency fallback in `build_final_tables.py` raise instead of defaulting to row currency.

**Needs a decision:**
6. Rename `gain_basis` → `gain_loss_pct_basis` (recommend yes — it does not describe the dollar gain).
7. Add `gain_loss_pct_source` and `is_aggregate` (recommend yes).
8. Allow prior-year property valuation as a labelled fallback base, +4pp coverage (recommend yes,
   clearly marked as derived).
9. Drop `announced_date` + `transaction_date` (recommend yes).

---

## Verification note

Of three sub-agent passes, one produced a **false "loader bug" conclusion** from a faulty premise in
my own prompt. The `gain_loss_pct` unit split, the ME8U 10× error and all coverage figures in this
document were computed directly against prod and hand-checked against AR text.
