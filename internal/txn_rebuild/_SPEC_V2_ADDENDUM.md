# Rebuild spec v2 — addendum: add `sale_price`, and fix known defects

Read `_SPEC.md` first for the base contract. This addendum revises it.

**Output only. NOTHING is written to any database.** You edit the existing
`txn_rebuild/<SYMBOL>_FY<YEAR>.json` files in place.

---

## Why this pass exists

v1 of the schema stored `gain_loss_pct` and derived the price from it. Checking all 138 divestments
against the annual reports showed that was backwards:

```
basis value disclosed   112/138   81%
sale price disclosed    106/138   77%
percentage disclosed     53/138   38%
```

So **v2 stores the price and derives the gain**. The rebuild files were built to v1 and therefore
have **no `sale_price` field on divestments**. This pass adds it.

---

## Task 1 — add `sale_price` to every divestment row

Add these two fields to each divestment transaction:

```json
"sale_price": 338000000,
"sale_price_currency": "SGD",
"sale_price_scope": "per_property",
"sale_price_citation": "p47: 'total divestment consideration of $338.0 million'"
```

- **`sale_price`** — the **gross consideration** for this property, in the currency the AR states it.
  Do NOT convert. Do NOT use a net-of-costs figure; if the AR only gives net proceeds, record that
  and say so in `sale_price_scope` = `net_proceeds`.
- **`sale_price_currency`** — always tag it. A missing tag has previously caused a silent
  mis-conversion.
- **`sale_price_scope`** — one of:
  - `per_property` — this price is for this property alone
  - `deal_level` — one price covering several properties (repeat it on each row of the deal)
  - `net_proceeds` — the only figure available is net of disposal costs
  - `not_disclosed` — leave `sale_price` null
- **`sale_price_citation`** — a verbatim quote. **No quote → null price.**

### CRITICAL — units

Several REITs print figures spelled out, e.g. *"MYR26.1 million (S$7.5 million)"* or
*"RMB814 million"*. **Record the full number** (26,100,000), never the printed digits (26.1).
A prior extraction stored six M44U rows 1000× too small this way. If a table has a
thousands/millions header, apply it.

### CRITICAL — same interest basis

`sale_price`, `reference_value` and `interest_pct` must all be on the **stake actually transacted**.
For a 20.2% divestment the price is for 20.2%, so the reference must be the 20.2% share too.

---

## Task 2 — de-aggregate two deals we wrongly collapsed

**J91U FY2025** — 8 rows currently share `deal_id`
`j91u:8_asset_non_core_industrial_portfolio:announced_divestment:2025` with a deal-level
`reference_value` of 331,600,000. **This is wrong.** The AR (p47–48) gives each property its own
sale price AND its own carrying value. Split them:

```
46A Tanjong Penjuru       113,500,000 / 111,498,000
24 Jurong Port Road        68,000,000 /  66,792,000
21 & 23 Ubi Road 1         45,000,000 /  41,700,000
120 Pioneer Road           34,100,000 /  33,440,000
13 Jalan Terusan           16,700,000 /  16,383,000
43 Tuas View Circuit       15,100,000 /  14,814,000
60 Tuas South Street 1      3,500,000 /   3,410,000
86 & 88 International Road      VERIFY — currently shows 41,409 / 42,500, which is out of scale
                                with its neighbours. Read the AR and record what it actually says.
```

Give each row its own `deal_id`. Keep the 2.0% aggregate premium in `notes` — it applies to the
group, not per property.

**SET FY2025 Slovakia** — currently one row for 5 properties. The AR (p43) discloses per-property
"Divestment Price" and "Valuation" for all five. Split into 5 rows. Only the €70.0m cash
consideration and the 3.5% premium (vs €67.7m net equity) are portfolio-level — keep those in
`notes`.

---

## Task 3 — targeted fixes

- **M44U FY2025** — verify every `reference_value` and `sale_price` is in **units, not thousands**.
  1 Genting Lane's true price is S$12.3 **million**.
- **AJBU FY2024 Kelsterbach** — the sale price (**$70.6m**) IS disclosed, in the subsequent-events
  note. We captured only the valuation. Add it.
- **HMN FY2024 Courtyard by Marriott Sydney-North Ryde** — the AR gives **two different prices**:
  AUD109.0M / S$95.6M in the Divestment Highlights (p9), and **$48.6M in Note 8**. Record both:
  put the Highlights figure in `sale_price` and quote the Note 8 figure in `notes`. **Do not pick
  one silently** and do not try to reconcile them.

---

## Rules (unchanged, and previously violated)

1. **Do ALL work YOURSELF.** No sub-agents.
2. Answers come from the **annual report text** in `parsed_reports_datalab/<folder>/full.md`.
   Our own JSON is a pointer to page numbers, not evidence.
3. **Never claim "not disclosed" without saying where you searched.**
4. **Never balance by assumption.** A figure that doesn't reconcile is recorded as-is with an
   explanation, never adjusted to make arithmetic work.
5. Always tag currency on every money field.

### Parsed folder mapping

For **M44U, ME8U, N2IU** the folder label is **one declared-FY behind**:

```
28_M44U..._FY2022 = AR "FY23/24" = declared FY2023
28_M44U..._FY2023 = AR "FY24/25" = declared FY2024
28_M44U..._FY2024 = AR "FY25/26" = declared FY2025
```

**O5RU and P40U labels are correct.** Confirm from each folder's `meta.json` `file` field.

---

## Reference

Coverage evidence and the per-REIT disclosure tables: `_COVERAGE_RESULTS.md` and
`_coverage_agent1..5.md`. Agreed schema:
`docs/7-30-2026-schema-review/transaction-target-schema-AGREED.md`.
