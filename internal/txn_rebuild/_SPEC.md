# Transaction rebuild — extraction spec

Re-extraction of `sgx_reit_property_transaction` onto the agreed target schema
(`docs/7-30-2026-schema-review/transaction-target-schema-AGREED.md`).

**Output only. NOTHING is written to any database — not prod, not dev.** Files land in
`txn_rebuild/<SYMBOL>_FY<YEAR>.json`.

---

## What to produce

One JSON file per REIT-year, containing every transaction disclosed in that annual report.

```json
{
  "symbol": "C38U",
  "financial_year": 2025,
  "source": "parsed_reports_datalab/09_C38U.SI_..._FY2025/full.md",
  "transactions": [
    {
      "property_name": "21 Collyer Quay",
      "transaction_type": "divestment",          // acquisition | divestment | partial_divestment
      "status": "completed",                     // completed | announced | terminated
      "counterparty": "…or null",
      "completed_date": "2024-11-15",            // YYYY-MM-DD, or null if not disclosed

      // ACQUISITIONS
      "purchase_price": null,                    // number, or null
      "purchase_price_currency": null,           // "SGD" | "USD" | … ALWAYS tag it

      // DIVESTMENTS — the five fields this rebuild exists for
      "gain_loss_pct": 5.12,                     // SIGNED. See UNITS below.
      "pct_unit": "percent",                     // ALWAYS the literal "percent"
      "pct_source": "derived",                   // "disclosed" if the AR states the %, else "derived"
      "reference_value": 639842000,              // the number the % is measured against
      "reference_currency": "SGD",               // ALWAYS tag it
      "reference_basis": "book_value",           // see BASIS below
      "interest_pct": null,                      // 0.202 for a 20.2% stake; null if 100%
      "deal_id": "c38u:21_collyer_quay:divestment:2024",

      // EVIDENCE — required on every populated numeric field
      "citation": "p136 Note 33: 'the Group recognised a net gain on divestment of investment property of $32.8 million'",
      "notes": "carrying value derived per accounting policy: net proceeds 672,607 - gain 32,765"
    }
  ]
}
```

---

## The five fields

### 1. `gain_loss_pct`

The premium or discount the property sold at, against a stated reference.

- **UNITS: always percent.** `8.4` means +8.4%. A loss is negative: `-6.55`.
  (A later decision may convert the whole database to fractions; `pct_unit` makes that unambiguous.
  Do not pre-convert.)
- If the AR states a percentage, use it verbatim and set `pct_source: "disclosed"`.
- If not, derive `(price − reference_value) / reference_value × 100` and set `"derived"`.
- **Null it** if there is no defensible reference. Do not invent one.

### 2. `reference_basis` — one of exactly four

| value | use when |
|---|---|
| `valuation` | an independent/market valuation of the property |
| `book_value` | carrying amount / book value on the balance sheet |
| `purchase_price` | the REIT's original acquisition cost (rare — ODBU and C2PU disclose it) |
| `net_identifiable_assets` | equity/subsidiary disposal measured against SPV net assets |

### 3. `reference_value`

The number the percentage is measured against, in the basis above.

- **Must be on the SAME interest basis as the price.** For a 20.2% stake, this is the **20.2% share**,
  not the whole asset. Never mix a part-price with a whole-asset reference.
- Record its currency in `reference_currency` — never leave it null, never assume the row currency.

### 4. `interest_pct`

The stake **transacted in this deal** — not the REIT's resulting total holding.
`0.202` for 20.2%. **Null when 100%.** Watch for wording like *"an additional 10% interest…
bringing its total stake to 20%"* → record `0.1`, the increment.

### 5. `deal_id`

`<symbol_lower>:<property_slug>:<type>:<year_deal_completed>`

**Deterministic and lowercase.** This is the grouping key, so it must be identical across rows of
the same deal:

- **Aggregate deals** — one sale covering several properties → every property row gets the **same**
  `deal_id`, and each row repeats the **deal-level** `reference_value` and `gain_loss_pct`.
  Known cases: A17U FY2024 Queensland trio · M44U Chee Wah + Subang 1 · T82U Suntec strata ·
  P40U Wisma Atria strata.
- **Cross-year duplicates** — the same deal reported in two annual reports → the **same** `deal_id`
  in both years, using the year the deal completed. Known cases: M44U (several), ODBU Albany,
  UD1U Il·lumina, TS0U Lippo Plaza.

---

## Rules

1. **Do ALL work YOURSELF.** Do not spawn, delegate to, or wait on any sub-agent.
2. **Read our existing extraction first** — `extracted/<SYMBOL>.SI_FY<YEAR>/property_transactions.json`
   and `_notes.json`. They carry page citations and often already document the tricky cases. Treat
   them as a starting point to be **verified against the report**, not copied blindly.
3. **Every populated numeric field needs a `citation`** quoting the annual report. No quote → null.
4. **Never claim "not disclosed" without reading the report text.** Past agents produced false
   "no data exists" findings that would have deleted valid data.
5. **Never balance by assumption.** If a figure does not reconcile, record it as-is and explain in
   `notes`. Do not adjust a number to make arithmetic work.
6. **Always tag currency** on every money field. A missing currency tag has previously caused a
   silent mis-conversion (DCRU's 770,936 artifact).
7. Prices: capture the **gross consideration**. If the AR computes its percentage on **net proceeds
   after disposal costs**, say so in `notes` — this is known to happen (C38U).
8. If a transaction cannot be represented, still emit the row with nulls plus a `notes` explanation.
   Known genuine gap: **XZL FY2024's three Hyatt divestments** — the AR pools figures across hotels
   and across the ACRO-REIT/ACRO-BT sub-entities, so only a price exists.
