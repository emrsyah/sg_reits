# Divestment disclosure coverage — what the annual reports actually publish

All 138 divestments, checked against the annual report text in `parsed_reports_datalab/`
by 5 Sonnet agents (~28 each). Per-agent tables in `_coverage_agent1..5.md`.

**Purpose:** decide whether `sale_price` can be dropped and the price derived from
`gain_loss_pct × reference_value`. That needs real *disclosure* rates, not our extraction's fill
rate — the two are different questions, and prod's 88% `sale_price` fill measures the second.

---

## Result

| what the AR discloses | count | % |
|---|---|---|
| **Reference figure** (valuation / book value / purchase price / SPV net assets) | 112/138 | **81%** |
| **Per-property sale price** | 106/138 | **77%** |
| **Percentage** (premium/discount, stated) | 53/138 | **38%** |
| **Both pct AND reference → price derivable** | 45/138 | **33%** |

Per batch:

| batch | per-property price | reference | pct disclosed | derivable |
|---|---|---|---|---|
| 1 | 18/28 | 16/28 | 7/28 | 7/28 |
| 2 | 20/28 | 26/28 | 7/28 | 7/28 |
| 3 | 23/28 | 23/28 | 12/28 | 10/28 |
| 4 | 24/27 | 26/27 | 11/27 | 10/27 |
| 5 | 21/27 | 21/27 | 16/27 | 11/27 |

> Caveat: agent 1's body text and its summary block disagree (12 vs 7 on pct, 20 vs 16 on
> reference). The lower summary figures are used above, so the pct/reference totals are
> conservative. Agents also differed on whether an aggregate price counts as "disclosed"; the
> per-property column above is the strict reading.

---

## Conclusion: `sale_price` cannot be replaced by the derived price

**A stated percentage exists on only 38% of divestments.** The price is disclosed twice as often.
Deriving price from `pct × reference` covers **33%** of rows — less than half the coverage of
simply storing the disclosed price.

### The circularity problem

Our rebuild has `gain_loss_pct` populated on 120/138, but only **53** are disclosed. The other ~67
we **derived**, as `(sale_price − reference) / reference`.

So on most rows the percentage is a *function of the sale price*. Dropping `sale_price` and keeping
the derived percentage does not remove a redundant column — it removes the **source** and keeps the
**calculation**. If the price is wrong, the percentage is wrong, and nothing remains to check it
against.

### What IS well disclosed

The two disclosed anchors are the **price (77%)** and the **reference (81%)**. The percentage is the
weak link, not the reference.

**Revised recommendation — store what is disclosed, derive what is not:**

```sql
transaction_price   numeric   -- disclosed on 77%
reference_value     numeric   -- disclosed on 81%
reference_basis     text      -- valuation | book_value | purchase_price | net_identifiable_assets
interest_pct        numeric
deal_id             text
gain_loss_pct       numeric   -- DERIVED where not disclosed; flag which
```

This keeps the single comparable metric (the percentage) that motivated the redesign, while
retaining both disclosed anchors so the metric stays auditable. `gain = price − reference`, and
the percentage remains the cross-REIT comparable.

---

## Findings that change the rebuild

### 1. M44U prod values are 1000× too small — confirmed at source

Both agents that checked report the Divestments table prints figures **spelled out in millions**:

> *"MYR26.1 million (S$7.5 million)"*

No thousands multiplier, no unit header. 1 Genting Lane's true price is **S$12.3 million**; prod
holds **12,300**. Six M44U FY2025 rows affected. **Our extraction error, not a report convention.**

### 2. SET Slovakia is NOT one aggregate deal

We recorded it as a single 5-property deal. The AR **does** disclose per-property "Divestment
Price" and "Valuation" for all five (p43). Only the €70.0m cash consideration and the 3.5% premium
(vs €67.7m net equity) are portfolio-level. → `txn_rebuild/SET_FY2025.json` needs splitting.

### 3. AJBU Kelsterbach FY2024 — we missed a disclosed price

The sale price (**$70.6m**) is disclosed in the subsequent-events note. Our extraction captured only
the valuation.

Also resolved: the FY2025 "inconsistency" I flagged is not one. The AR states *"EUR 50.0 million or
a 28.2% premium to its 31 December 2024 value of EUR 39.0 million"* — internally consistent
(39.0 × 1.282 ≈ 50.0). The S$70.6m elsewhere is the SGD translation of the same EUR 50.0m.

### 4. HMN Courtyard North Ryde — the AR contradicts itself

```
Divestment Highlights (p9)   AUD109.0M / S$95.6M
Note 8                        $48.6M
```

Two figures for one deal in one report. This is the 1.967 ratio my identity check flagged — **not
our bug**. Needs a judgement call on which figure the AR intends.

### 5. ODBU Albany — reference comes from a different year's report

The FY2025 AR states *"at 4.2% Above Purchase Price"* verbatim but **never prints the purchase-price
dollar figure**. Our stored US$22.9m came from the FY2024 report. Defensible, but the percentage and
its reference come from two documents.

### 6. CY6U — percentage with no dollar reference (confirmed)

Exhaustive search (Capital Recycling p35, Note 25 disposal-group, full-text grep) found **no
independent-valuation dollar figure anywhere**. Sale prices *are* disclosed (S$161.7m, S$99.7m).

So this is the reverse of the case for dropping `sale_price`: here the price exists and the
reference does not, so `gain = reference × pct` produces nothing while a price column holds real
data.

---

## Confirmed genuine aggregates (per-property split does not exist)

| deal | what is aggregate |
|---|---|
| A17U FY2024 Queensland trio | one S$64.2m price + one $628,000 gain for 3 properties; per-property valuations *are* disclosed |
| P40U FY2024 Wisma Atria | 13 strata units, 7 buyers, one ~S$41m consideration |
| HMN FY2024 WBF trio | one JPY10.7B / S$99.8M price for 3 hotels |
| ME8U FY2025 Singapore cluster | one S$535.3m across 3 properties — table shows one filled row, two blank |
| M44U Chee Wah + Subang 1 | Subang 1's Sale Price and Valuation cells are blank |
| T82U strata (both years) | FY2024 7 units / FY2025 2 units, one aggregate figure each |

J91U FY2025 is **not** an aggregate: all 11 have per-property price and valuation (p47–48). Only a
2.0% premium applies narratively to a sub-group of 8 (verified: the 8 sum to S$338.1m exactly).

---

## Genuine gaps

- **XZL FY2024 Hyatt ×3** — sale prices *are* disclosed per hotel, but valuations and gains are
  pooled across assets and across the ACRO-REIT/ACRO-BT entity split.
- **HMN Novotel Sydney Parramatta** — highlights-table cells genuinely blank; price appears in
  Note 8 ($47.8m) with no percentage anywhere.
- **AJBU Basis Bay** — announced only, unpriced.
- **M44U FY2024 ×7** — prior-year divestments named with completion dates only, no figures.
