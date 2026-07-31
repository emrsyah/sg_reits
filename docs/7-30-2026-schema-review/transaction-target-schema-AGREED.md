# `sgx_reit_property_transaction` — AGREED target schema

Decided 2026-07-31. Supersedes the "proposed target shape" in
`property-transaction-verification.md` and the proposal in `transaction-gain-uniform-metric.md`.

The table answers two questions and nothing else:

- **Acquisition** — when, and how much.
- **Divestment** — how much was gained or lost, and against what.

---

## Schema

```sql
sgx_reit_property_transaction (
  symbol             text,
  financial_year     smallint,
  deal_id            text,     -- groups aggregate deals AND cross-year duplicates
  transaction_type   text,     -- acquisition | divestment | partial_divestment
  status             text,     -- completed | announced | terminated
  property_name      text,
  counterparty       text,
  completed_date     date,     -- applies to BOTH directions

  -- ACQUISITION
  purchase_price     numeric,

  -- DIVESTMENT
  gain_loss_pct      numeric,  -- PERCENT, signed. 8.4 means +8.4%; -6.55 means a loss
  reference_value    numeric,  -- the number the pct is measured against
  reference_basis    text,     -- valuation | book_value | purchase_price | net_identifiable_assets
  interest_pct       numeric   -- stake TRANSACTED; null = 100%
)
```

### Dropped

`sale_price`, `net_sale_proceeds`, `valuation`, `carrying_value`, `gain_on_divestment`,
`gain_basis`, `announced_date`, `transaction_date`, `valuation_date`, `description`,
`source_type`, `announcement_refs`.

---

## The calculation

```
gain_or_loss   = reference_value × gain_loss_pct / 100
implied_price  = reference_value × (1 + gain_loss_pct / 100)
```

Three columns are arithmetically complete: the dollar gain and the price both fall out. A negative
percentage is a loss; no separate column or sign convention is needed.

### Invariant 1 — internal

`gain_loss_pct`, `reference_value` and the transaction price are always on the **same interest
basis**: the stake actually transacted. `interest_pct` records what that stake was.

For a 20.2% divestment, `reference_value` is the **20.2% share** of the valuation, not the whole
asset. Storing it at 100% would make `pct × reference_value` the gain on the entire building — a
number the REIT never earned.

### Invariant 2 — cross-table

When `reference_basis = valuation`:

```
reference_value  ≈  sgx_reit_property.market_valuation × COALESCE(interest_pct, 1)
```

compared against the property's **last appearance** in the property table (a divested property is
removed in the year of sale). Two conditions must hold for the check to be fair: the valuation
must be as at a comparable date (deal valuations are often mid-year, not 31 December), and
`interest_pct` must be applied before comparing.

The tie-out target depends on the basis — which is the reason `reference_basis` exists:

| `reference_basis` | ties against |
|---|---|
| `valuation` | `sgx_reit_property.market_valuation` (× interest) |
| `book_value` | carrying amount; **not** the market valuation |
| `purchase_price` | `sgx_reit_property.purchase_price` |
| `net_identifiable_assets` | entity-level figure — **no property-table tie-out** |

### Invariant 3 — grouping

**Group by `deal_id` before aggregating.** Take `reference_value` and `gain_loss_pct` once per
deal, not once per row.

---

## Worked examples

### A — ordinary asset sale

```
deal_id                             symbol fy   property_name       basis      reference_value   pct
j69u:changi_city_point:divest:2024  J69U   2024 Changi City Point   valuation      325,000,000  +4.00
```

> *"total divestment consideration of $338.0 million ... after taking into account the independent
> valuation of $325.0 million as at 31 July 2023"*

```
gain  = 325,000,000 × 4.00/100 =  13,000,000
price = 325,000,000 × 1.04     = 338,000,000
```

### B — aggregate deal (one sale, three properties)

A17U FY2024 sold 77 Logistics Place, 62 Sandstone Place and 92 Sandstone Place for one
consideration of S$64.2m with one disclosed gain of S$628,000. The three rows survive and share a
`deal_id`; the deal-level figures repeat across them.

```
deal_id                        symbol fy   property_name       basis       reference_value   pct
a17u:qld_trio:divestment:2024  A17U   2024 77 Logistics Place  book_value      62,432,000   +1.01
a17u:qld_trio:divestment:2024  A17U   2024 62 Sandstone Place  book_value      62,432,000   +1.01
a17u:qld_trio:divestment:2024  A17U   2024 92 Sandstone Place  book_value      62,432,000   +1.01
```

`reference_value` is the summed carrying amount (24,359,000 + 14,345,000 + 23,728,000), and:

```
gain = 62,432,000 × 1.01/100 = 628,000    ✓ "a gain amounting to $628,000 (A$710,000)"
```

```sql
-- CORRECT
SELECT deal_id, MAX(reference_value) * MAX(gain_loss_pct)/100 AS gain
FROM sgx_reit_property_transaction GROUP BY deal_id;        -- 628,000

-- WRONG (today's behaviour): SUM over rows -> 1,884,000, triple-counted
```

Per-property rows are retained deliberately: you can still ask *"did A17U divest 92 Sandstone
Place?"*, you simply cannot ask what that one property sold for — the report never said. Note
92 Sandstone's carrying value (23,728,000) **exceeds** its valuation (19,300,000), so a per-property
calculation would show a loss on a deal that was an aggregate gain. This is why deal-level grouping
is mandatory, not advisory.

### C — cross-year duplicate

The same deal reported in two consecutive annual reports. Identical `deal_id`, so the same grouping
rule prevents the double-count.

```
deal_id                       symbol fy   property_name  basis      reference_value   pct
m44u:century:divestment:2023  M44U   2023 Century        valuation      14,900,000   +15.38
m44u:century:divestment:2023  M44U   2024 Century        valuation      14,900,000   +15.38
```

Affects M44U (×8), ODBU Albany, UD1U Il·lumina and TS0U Lippo Plaza. Today prod has no signal for
this at all, so any multi-year sum of divestment proceeds is overstated.

### D — equity sale, partial stake

```
deal_id                    symbol fy   property_name           basis      reference_value  pct   interest_pct
cy6u:dc_stake:divest:2025  CY6U   2025 3 data centres (20.2%)  valuation     132,000,000  +3.00  0.202
```

> *"The sale was executed at a 3% premium to their independent valuations."*

```
gain = 132,000,000 × 3.00/100 = 3,960,000     -- on the 20.2% sold
```

Cross-check must be scaled: `132,000,000 ≈ market_valuation × 0.202`.

### E — equity sale with no property-level valuation

AU8U CapitaMall Shuangjing FY2024, structured as a subsidiary disposal:

> *"Gain on disposal of subsidiary S$7,309k... net identifiable assets divested S$130,471k"*

```
basis = net_identifiable_assets   reference_value = 130,471,000   pct = +5.60
gain  = 130,471,000 × 5.60/100 = 7,309,000    ✓ ties to the accounts
```

This is the only basis with **no** property-table tie-out, and the basis value is what signals that.

---

## Convention decisions and their consequences

### Equity sales are recorded on **property economics**, not accounting outcome

Where an equity/subsidiary disposal discloses both, `gain_loss_pct` carries the **property-level**
premium or discount. The REIT's booked P&L figure is **not** stored.

TS0U Lippo Plaza FY2025 is the worked case: the property sold at **+14.86%** over carrying value,
while the accounts booked a **loss of S$26,427,000** driven by recycled FX translation reserves and
tax. Both are correct; they measure different things.

**Accepted cost:** the reported P&L gain leaves the table. This is a real loss of information,
recorded here so it is not discovered later. The reason for the choice is comparability — a column
where half the rows mean *"premium over building value"* and half mean *"gain after FX recycling at
the holding company"* is not comparable across REITs even though every individual value is right.

Today this convention conflict is visible in prod as rows with a positive percentage beside a
negative dollar gain (AU8U Yuhuating, ODBU Albany, XZL Detroit). Those are **not** sign bugs.

### `net_identifiable_assets` replaces a separate structure flag

An earlier proposal added `transaction_structure (asset_sale | equity_sale)`. It is unnecessary:
the basis value already identifies an entity-level measurement. One fewer column.

### `pct_source` (disclosed vs derived) stays in dev only

A majority of these percentages are derived by us, not stated by the REIT — M44U's divestment table
headers are literally **Property | Country | Sale Price | Valuation | Completion Date**, with no
percentage column anywhere. Retain the distinction in dev/raw for provenance; prod does not carry it.

---

## Current data position

Against this schema, using dev `_final` (which is correct — see the prod-staleness note below):

```
divestments                                      136
  gain_loss_pct + a usable reference (ready)      91   (67%)
  reference present, percentage missing           24   (18%)
  neither                                         16   (12%)
  percentage present, reference missing            5    (4%)
```

**This is a rebuild, not a column rename.** `reference_value` / `reference_basis` must be populated
per row from the existing `valuation` / `carrying_value` / `gain_basis` columns, and ~39 of the 53
rows currently holding a dollar gain do **not** reconcile to any formula. Those are resolved during
the fill, not afterwards.

Known genuine gap: **XZL FY2024's three Hyatt divestments.** The AR pools figures across hotels and
across the ACRO-REIT/ACRO-BT sub-entities, never per property. Nothing to extract; those rows will
carry a price only.

---

## P0 — prod `gain_loss_pct` is stale (fix before anything else)

61 of 130 prod rows disagree with dev. The extraction, raw dev table and `_final` all hold the
correct percent value; only prod is wrong.

```
extracted JSON  ->  raw dev  ->  _final  ->  PROD
     8.4             8.4         8.4        84.0    x10    ME8U Tanglin Halt
     1.31            1.31        1.31       0.0131  x0.01  N2IU Mapletree Anson
     0.3             0.3         0.3        3.0     x10    BTOU Peachtree

SAME 69  |  x0.01  50  |  x10  11
```

`promote_final_to_prod.py:56` explicitly excludes `gain_loss_pct` from `FRACTION_FIELDS`
(*"gain_loss_pct is intentionally NOT here"*), so the current pipeline does not cause this — these
rows were written by an earlier pipeline and never re-promoted.

**Re-running the promote script fixes 61 rows with no schema change and no re-extraction.** This is
almost certainly the largest single cause of the table appearing untrustworthy, and it invalidates
two earlier findings in `transaction-gain-uniform-metric.md`: the "two units in one column" split
and the "confirmed 10x error on ME8U" were both prod staleness, not data defects.

---

## Action order

**Before the rebuild:**
1. Re-promote `sgx_reit_property_transaction` to fix the 61 stale `gain_loss_pct` rows.
2. Make the currency fallback in `build_final_tables.py` raise instead of defaulting to the row
   currency (caused the DCRU 770,936 artifact).

**Rebuild:**
3. Populate `reference_value` + `reference_basis` on all 136 divestments from existing columns.
4. Resolve the ~39 non-reconciling rows into: equity-sale (convention above), aggregate (deal_id),
   or genuine extraction error (fix at source with citation).
5. Backfill `deal_id` on aggregate deals (A17U trio, M44U Chee Wah + Subang 1, T82U and P40U strata)
   — roughly 10 rows. Make slug generation deterministic first: TS0U Lippo Plaza currently has two
   different `deal_id`s across years (`TS0U.SI:lippo_plaza:...` vs `ts0u.si:lippo_plaza_shanghai:...`)
   and will not dedupe until that is fixed.
6. Promote `deal_id` to prod.
7. Source the 45 divestments missing a percentage or a reference.
8. Drop the retired columns.

**Gates to add:**
9. Invariant 1 (internal) and Invariant 2 (cross-table) as sanity-scan checks, so this cannot rot
   again silently.
