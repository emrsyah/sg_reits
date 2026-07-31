# `sgx_reit_property_transaction` — AGREED target schema

**Revised 2026-07-31 (v2).** Supersedes v1 of this document and the proposals in
`property-transaction-verification.md` and `transaction-gain-uniform-metric.md`.

The table answers two questions and nothing else:

- **Acquisition** — when, and how much.
- **Divestment** — what it sold for, what that is measured against, and the gain.

---

## What changed from v1, and why

v1 stored `gain_loss_pct` and derived the price from it. **That was backwards.**

Checking all 138 divestments against the annual reports (`txn_rebuild/_COVERAGE_RESULTS.md`):

| the AR discloses | count | % |
|---|---|---|
| basis value (valuation / book value / cost / SPV net assets) | 112/138 | **81%** |
| sale price, per property | 106/138 | **77%** |
| percentage | 53/138 | **38%** |
| both pct + basis → price derivable | 45/138 | 33% |

**A stated percentage exists on only 38% of divestments.** Deriving the price from it covers 33%;
storing the price covers 77%.

And it was circular: our rebuild had `gain_loss_pct` on 120/138 but only **53 disclosed** — the rest
we computed as `(sale_price − basis_value) / basis_value`. Storing the percentage and dropping the
price kept the calculation and discarded its source.

**v2 stores what the reports disclose and derives what they don't.**

---

## Schema

```sql
sgx_reit_property_transaction (
  symbol            text,
  financial_year    smallint,
  deal_id           text,      -- groups multi-property deals AND cross-year duplicates
  transaction_type  text,      -- acquisition | divestment | partial_divestment
  status            text,      -- completed | announced | terminated
  property_name     text,
  counterparty      text,
  completed_date    date,

  -- ACQUISITION
  purchase_price    numeric,

  -- DIVESTMENT
  sale_price        numeric,   -- PRIMARY. disclosed on 77%
  basis_value       numeric,   -- what the price is measured against. disclosed on 81%
  basis             text,      -- valuation | book_value | purchase_price | net_identifiable_assets
  gain_loss_pct     numeric,   -- fallback for rows with no sale price. see below
  interest_pct      numeric    -- stake transacted; null = 100%
)
```

All money fields carry a currency tag. Percentages are fractions (0–1) per the database-wide
normalisation — `0.042`, not `4.2`.

---

## The calculation

**Primary — use this wherever a sale price exists (101/138 rows have both):**

```
gain          = sale_price − basis_value
gain_loss_pct = gain / basis_value
```

**Fallback — only where `sale_price` is null but a percentage was disclosed (17 rows):**

```
gain       = basis_value × gain_loss_pct
sale_price = basis_value × (1 + gain_loss_pct)
```

### `gain_loss_pct` — what goes in it

Store the **AR's stated percentage** where one exists. Leave null otherwise; the derived value is
computed at read time from the two stored figures and labelled as derived.

This keeps the column to disclosed facts only, so "the REIT said 8.4%" is never confused with "we
calculated 8.35%". ME8U Tanglin Halt is the live case: sale 50,600,000 against book value
46,700,000 derives to 8.35%, while the AR states *"an 8.4% premium above book value"*.

---

## Invariants

**1 — same interest basis.** `sale_price`, `basis_value` and `gain_loss_pct` are all on the stake
**actually transacted**. For a 20.2% divestment, `basis_value` is the 20.2% share, not the whole
asset. `interest_pct` records the stake.

**2 — cross-table.** Where `basis = valuation`:
`basis_value ≈ sgx_reit_property.market_valuation × COALESCE(interest_pct, 1)`, compared against
the property's **last appearance** (a divested property leaves the table in the year of sale).
Valuation dates must be comparable — deal valuations are often mid-year.

**3 — grouping.** **Group by `deal_id` before aggregating money.** Rows are per property; money is
per deal.

---

## The basis, and why the label is mandatory

| `basis` | rows | meaning |
|---|---|---|
| `valuation` | 93 | independent valuer, as at a date |
| `book_value` | 21 | carrying amount on the balance sheet |
| `purchase_price` | 4 | original acquisition cost — rare |
| `net_identifiable_assets` | 2 | equity/SPV disposal |

REITs choose the benchmark that flatters them. ME8U's report discloses **both** — valuation S$48.7m
and book value S$46.7m — and quotes the premium against book value (8.4%) because it is the larger
number; against valuation it is 3.9%. Two REITs can both say "20% premium" and mean different
things, so the label is what makes the percentage comparable.

`net_identifiable_assets` also removes the need for a separate structure flag: it *is* the signal
that a row is an equity sale rather than an asset sale.

---

## Worked examples

### 1. Ordinary asset sale — the 73% case

J69U Changi City Point, FY2024:
> *"total divestment consideration of $338.0 million ... after taking into account the independent
> valuation of $325.0 million as at 31 July 2023"*

```
sale_price     338,000,000
basis_value    325,000,000    basis = valuation
-> gain         13,000,000
-> pct               +4.0%
```

### 2. No sale price — fall back to the percentage

J91U FY2025 and HMN's WBF trio disclose a percentage and a valuation but no per-property price:

```
sale_price     null
basis_value     86,782,609    basis = valuation
gain_loss_pct       +15.0%    (AR-stated)
-> gain         13,017,391
-> sale_price   99,800,000    (derived, flag as derived)
```

### 3. Partial stake

```
C38U CapitaSpring Serviced Residence, 45% JV interest
  sale_price     126,000,000
  basis_value    125,325,000    45% share, NOT the whole asset
  interest_pct          0.45
```

### 4. Equity sale

AU8U CapitaMall Shuangjing:
> *"Gain on disposal of subsidiary S$7,309k... net identifiable assets divested S$130,471k"*

```
sale_price     140,720,000
basis_value    130,471,000    basis = net_identifiable_assets
-> gain          10,249,000
```

The AR's own arithmetic: `140,720 − 130,471 + 2,940 (recycled FX reserves) = 7,309`. The FX term is
why an equity-sale gain can never be reproduced from property figures alone — record it in notes.

### 5. Multi-property deal

```
deal_id                        property             sale_price   basis_value
a17u:qld_trio:divestment:2024  77 Logistics Place   64,200,000   62,432,000
a17u:qld_trio:divestment:2024  62 Sandstone Place   64,200,000   62,432,000
a17u:qld_trio:divestment:2024  92 Sandstone Place   64,200,000   62,432,000
```

One S$64.2m consideration and one S$628,000 gain for three properties; `basis_value` is the summed
held-for-sale carrying amount (24,359,000 + 14,345,000 + 23,728,000).

```sql
-- money: group first
SELECT deal_id, MAX(sale_price) - MAX(basis_value) AS gain
FROM   sgx_reit_property_transaction GROUP BY deal_id;     -- 1,768,000, once

-- WRONG: SUM over rows -> triple-counted
```

**Never compute a per-property percentage on these rows.** 92 Sandstone's own carrying value
(23,728,000) exceeds its allocated valuation, so per property it shows a *loss* on a deal that was
an aggregate *gain*.

### 6. Cross-year duplicate — same rule, no extra logic

```
m44u:century:divestment:2023   M44U FY2023 Century
m44u:century:divestment:2023   M44U FY2024 Century
```

One deal reported in two annual reports. Group by `deal_id` → counted once. Affects **11 deals /
22 rows** (M44U ×several, ODBU Albany, UD1U Il·lumina, TS0U Lippo Plaza, N2IU Mapletree Anson,
O5RU 3 Toh Tuck Link) — prod has no signal for this today, so any multi-year sum is overstated.

---

## Aggregate deals — what is real and what is ours to fix

**Genuine (no per-property figures exist anywhere in the AR):**

| deal | note |
|---|---|
| HMN FY2024 WBF trio | one JPY10.7B / S$99.8M for 3 hotels |
| M44U Chee Wah + Subang 1 | Subang 1's Sale Price and Valuation cells are **blank** |

**Single rows already standing for many properties:** BUOU 28 German properties · C2PU MOB
Specialist Clinics · C38U Bukit Panjang Plaza (90 of 91 strata lots) · ME8U Tanglin Halt Cluster ·
ME8U Strategy/Synergy/Woodlands · P40U Wisma Atria (13 strata units, 7 buyers) · T82U Suntec strata
(FY2024 and FY2025).

**Our extraction errors — must be split before load:**

- **J91U FY2025 (8 rows)** — every property has its own price and carrying value
  (46A Tanjong Penjuru 113,500,000 / 111,498,000; 24 Jurong Port Road 68,000,000 / 66,792,000; …).
  Only the 2.0% premium is deal-level. We wrongly collapsed it.
- **SET FY2025 Slovakia (5 properties)** — the AR discloses per-property "Divestment Price" and
  "Valuation" (p43). Only the €70.0m cash consideration and 3.5% premium are portfolio-level.

**QA step (extraction-time, not query-time):** where per-property values exist, confirm they sum to
the deal-level `basis_value`. A17U's trio passes (62,432,000). Skip the check where they don't exist
— never invent a split.

---

## Known defects to fix before load

1. **M44U FY2025 — 6 rows are 1000× too small.** The AR prints *"S$X.X million"*; 1 Genting Lane is
   S$12.3 million, prod holds 12,300. Our extraction error, confirmed at source.
2. **J91U and SET** — de-aggregate as above.
3. **AJBU Kelsterbach FY2024** — the $70.6m sale price *is* disclosed, in the subsequent-events
   note. We captured only the valuation.
4. **J91U 86 & 88 International Road** — shows 41,409 / 42,500 among neighbours in the tens of
   millions. Units or parse error; check.
5. **HMN Courtyard North Ryde** — the AR gives **two different prices** for one deal (AUD109.0M /
   S$95.6M in the Divestment Highlights p9, $48.6M in Note 8). Not our bug; needs a judgement call
   on which the report intends.
6. **ODBU Albany** — the FY2025 AR states *"4.2% Above Purchase Price"* but never prints the
   purchase-price figure; our US$22.9m comes from the FY2024 report. Percentage and basis originate
   in different documents — acceptable, but record it.
7. **Prod `gain_loss_pct` is stale on 61 of 130 rows** (some ×10, some ÷100). Dev is correct
   throughout. **Re-promote before converting to fractions**, or the two defects are
   indistinguishable.

---

## Dropped

`net_sale_proceeds`, `valuation`, `carrying_value`, `gain_on_divestment`, `gain_basis`,
`announced_date`, `transaction_date`, `valuation_date`, `description`, `source_type`,
`announcement_refs`.

`valuation` and `carrying_value` are replaced by the single `basis_value` + `basis` pair.
`gain_on_divestment` is derived. `transaction_date` never disagreed with `completed_date` on any of
the 174 rows where both exist.

---

## Open

- Whether to store a `property_basis_value` (this property's own figure, alongside the deal-level
  one) so the aggregate sum-check is a query rather than a manual step. Would populate on ~10–15
  rows. Recommended but not agreed.
- Promote `deal_id` to prod and make slug generation deterministic — TS0U Lippo Plaza currently has
  two differently-cased slugs across years and will not dedupe until fixed.
