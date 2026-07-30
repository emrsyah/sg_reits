# `sgx_reit_property_transaction` — verification & recommendations

Answers to the 2026-07-30 meeting questions on this table. 206 prod rows, 30 REITs.
Verified against `parsed_reports_datalab/`, our own `extracted/*/property_transactions.json` +
`_notes.json`, and the raw dev table (which carries 36 columns vs prod's 20).

---

## Summary of answers

| # | Meeting item | Verdict |
|---|---|---|
| 1 | Remove all status ≠ "completed" | Works, but keep the rows and filter in a view — see §1 |
| 2 | `transaction_type` + `transaction_price` (drop `purchase_price`/`sale_price`) | **Agreed** — and it fixes a confirmed bug (§2) |
| 3 | What is `interest_pct`? Drop if not important | **Do not drop.** It is the stake *transacted*, and several prices are on an attributable basis (§3) |
| 4 | Drop `announced_date` and `transaction_date` | Agreed in principle, but 10 completed rows would have no date, and most of those nulls are structural (§4) |
| 5 | Is `gain_basis` necessary? | **The question is aimed at the wrong column** — it describes `gain_loss_pct`, not the dollar gain (§5) |
| 6 | `valuation_date` + `carrying_value` sufficient; drop `valuation` | **Recommend against** — loses independent-valuer provenance the ARs themselves use (§6) |
| 7 | Derive `gain_on_divestment` from price − property purchase_price, or price − carrying_value | **Neither works.** The ARs disclose the gain directly and it is already correct in 9 of 12 checked rows (§7) |

---

## 1. Remove all status ≠ "completed"

`status`: completed **176** · announced **29** · terminated **1**. Filtering drops 30 rows (14.6%).

**Recommendation: keep the rows, filter in the endpoint/view.** Announced-but-not-completed deals are
forward-looking information, often the most interesting rows for an investor. Filtering in a view
costs nothing and keeps the option.

Either way this cleans up `transaction_type`, which currently **duplicates status**:
`announced_divestment` (19), `announced_acquisition` (1), `divestment_terminated` (1). Completed rows
only ever carry `divestment` / `acquisition` / `partial_divestment`.

⚠️ **Data-integrity issues to fix regardless of the filter decision:**
- **8 non-completed rows carry a `completed_date`** — contradictory.
- **A duplicate transaction across two financial years.** TS0U's Lippo Plaza divestment is stored
  twice with the same `sale_price` of 357,382,000:
  - FY2024 "Lippo Plaza", `deal_id = TS0U.SI:lippo_plaza:divestment:2024`
  - FY2025 "Lippo Plaza Shanghai (via Lippo Realty (Shanghai) Limited)",
    `deal_id = ts0u.si:lippo_plaza_shanghai:divestment:2024`

  Both `status = completed`, both the same 2024 deal — our own notes say the FY2025 copy was kept
  "for audit-trail context". The `deal_id`s differ in slug and casing, so **`deal_id` does not dedupe
  them**. Any sum over divestment proceeds double-counts this deal.

## 2. Merge `purchase_price` + `sale_price` → `transaction_price` — agreed, and it fixes a bug

12 rows have both populated. **All 12 are acquisitions and none has a genuine second price.** The bug
is upstream of the DB — `extracted/*/property_transactions.json` already writes
`sale_price = purchase consideration` on acquisition rows (e.g. ME8U Osaka Data Centre stores
`"purchase_price": 52000000000, "sale_price": 52000000000` while the AR says only *"purchase
consideration of JPY52.0 billion"*).

**Root cause is two-part, and the second part is the more damaging:**

In raw, all 12 rows have `sale_price_currency = NULL` while `purchase_price_currency` is set. And
`build_final_tables.py` does:

```python
ccy = d.get(ccol) or d.get('currency')     # per-figure currency falls back to the ROW currency
```

So a NULL per-figure currency silently inherits the row currency:

| row | purchase_price | its currency | row currency | result |
|---|---|---|---|---|
| ME8U Osaka DC | 52,000,000,000 | JPY | JPY | both convert identically → harmless-looking duplicate |
| MXNU Custom House | 9,200,000 | GBP | GBP | identical duplicate |
| SET AiOnX | 50,000,000 | EUR | EUR | identical duplicate |
| **DCRU Digital Osaka 3** | 86,700,000 | **USD** | **JPY** | `sale_price` converted with the **JPY** rate → **770,936** |

DCRU is the same bug, only visible because the per-figure currency differs from the row currency.
There is no second price, no fee and no deposit — the AR discloses one consideration
(*"¥13,000 million (approximately US$86.7 million)"*).

**Fix:** null `sale_price` on acquisition rows at the extraction layer, merge to one
`transaction_price`, and **make the currency fallback fail loudly instead of silently defaulting to
the row currency.** The fallback will mis-convert any future figure whose currency tag is missing.

## 3. `interest_pct` — do not drop

**It is the stake transacted in that deal, not the REIT's resulting total stake.** Decisive evidence,
DCRU Digital Osaka 2: *"acquired an **additional 10%** equity interest in the Osaka Data Centre...
**bringing its total stake to 20%**"* — we store `0.1`, the increment. Same pattern at HMN
(*"the **remaining 10% stake** in Standard at Columbia"*) and K71U (*"acquiring an **additional
one-third interest** in Marina Bay Financial Centre Tower 3"*).

All 18 values verified against the ARs; every one matches. The odd-looking AJBU figures are genuine
vehicle interests, quoted verbatim: *"98.47% **effective interest**"*, *"99.49% of the **economic
interest**"*, *"remaining **0.51% economic interest**"* — Keppel DC structures Japan/Singapore
acquisitions through TMK trusts where a co-investor retains the balance.

DCRU's two Wilhelm-Fay-Straße rows (0.249, 0.151) are confirmed as **two separate tranches of the
same asset**: April 2024 (24.9%, from Digital Realty, held as associate) and December 2024 (15.1%,
reclassifying to subsidiary).

**Why dropping it would actively mislead:** several prices are on an **attributable** basis, not 100%.
AJBU Tokyo DC3's 683,000,000 is explicitly the *"Attributable (98.47%) basis"* (100% basis is
JPY 82.1bn); C38U CapitaSpring Commercial's price is *"55% of the agreed property value of S$1.9
billion"*. Without `interest_pct` a reader takes those as whole-asset prices.

Suggested: rename to `interest_transacted_pct` and null the 4 redundant `1`s so non-null always
means partial. Note two of those four (A17U's UK land, and Summerville) are **inferred** 100% — the
ARs never state a percentage; the other two (J69U *"100.0% interest"*, TS0U *"100% issued and
paid-up capital"*) are explicit.

## 4. Drop `announced_date` and `transaction_date`

Data supports it, with one correction to an earlier count I gave:

```
transaction_date == completed_date   174      they differ   0   (never)
completed rows WITHOUT completed_date  10     of those, no date at all   9
non-completed rows WITH completed_date  8     (contradictory)
```

`completed_date` never disagrees with `transaction_date`, so dropping both is safe **for rows that
have a completion date**. The exposure is the 10 completed rows left dateless — and most of those
nulls turn out to be **structural, not missing**:

- **P40U Wisma Atria office strata** — *"13 strata units or approximately 18,546 sq ft ... divested
  for sales consideration of approximately S$41 million in FY 2024/25"*. Thirteen separate sales in
  one row; **no single completion date exists.**
- **T82U FY2024 Suntec strata** — *"sale of strata units amounting to $41.9 million ... completed in
  FY 2024 while the balance strata unit sale was completed **on 6 January 2025**"*, to four different
  buyers. One row aggregating ≥4 deals with different dates, one of them outside the FY.
- **A17U Summerville FY2024** — a development project, *"under development"*, target completion
  4Q 2025. It had not completed, so null is correct for that year.
- **XZL Hyatt Place Pittsburgh Airport** — genuinely a load gap: the AR gives
  *"subsequently completed on **25 March 2024**"* and our extraction already holds `"2024-03"`.
- **XZL Philadelphia / Shelton, T82U FY2025, DCRU Wilhelm-Fay tranche** — the ARs disclose only
  month or FY granularity (*"in July 2024"*, *"in April 2024"*, *"in FY 2025"*). No day exists.

**Recommendation:** drop the two columns, but first (a) backfill XZL Pittsburgh's 25 Mar 2024,
(b) accept month/FY-granularity nulls as real, and (c) treat the strata rows as aggregates — either
split them per unit or flag them, because a single `completed_date` is not a meaningful field for
them.

## 5. Is `gain_basis` necessary? — it describes the *percentage*, not the gain

| | count |
|---|---|
| rows with `gain_basis` | 140 |
| ...that also have `gain_loss_pct` | 130 |
| ...that have **no** `gain_on_divestment` | **91** |
| ...that are **acquisitions** | **34** |

An acquisition cannot have a divestment gain, and all 34 have `gain_on_divestment = NULL`. On those
rows `gain_basis` is qualifying the **premium or discount paid vs valuation**. Our own extraction
notes state the mechanism outright:

> M44U: *"vs_valuation, **derived** (purchase_price − valuation)/valuation"*
> C38U ION Orchard: *"**DERIVED** vs_valuation (**not disclosed** as a premium %)"*

**So `gain_basis` is necessary — but it belongs to `gain_loss_pct`, and it should be renamed to say
so** (`gain_loss_pct_basis`). Values are `vs_valuation` 111 · `vs_book_value` 28 · `vs_cost` 1 ·
null 66.

**One mistag found:** P40U Wisma Atria is tagged `vs_valuation`, but its own AR footnote defines the
base as carrying amount — *"represents the difference between net proceeds (including directly
attributable costs) from divestment and the **carrying amount**"*. Should be `vs_book_value`.

## 6. Drop `valuation`, keep `valuation_date` + `carrying_value` — recommend against

Coverage: `valuation` 162 rows · `carrying_value` 100 · both 89 · either 173. And
`valuation_date` with no `valuation` is already incoherent on 3 rows.

**The ARs themselves frame these deals against a named independent valuation:**

- C38U: *"**Savills** Valuation and Professional Services (S) Pte Ltd had valued 21 Collyer Quay at
  S$688.0 million **as at 31 October 2024** using the income capitalisation and discounted cash flow
  methods"*
- ME8U: *"The **independent valuation** of the Tanglin Halt Cluster was S$48.7 million as at
  31 December 2023"*, and separately *"**book value** of S$46.7 million"*, with *"an **8.4% premium
  above book value**"*
- BTOU: *"**Cushman & Wakefield** valued the property at US$133.4 million **as at 28 April 2025**"*
- P40U: *"the valuation of approximately S$32 million **as at 30 June 2024 by CBRE Pte. Ltd.**"*

Who valued it, as at when, by which method — `carrying_value` cannot carry any of that.

**Only 2 of 12 checked rows disclose both an independent valuation and a separately-labelled carrying
value** for the same deal (ME8U Tanglin Halt, HMN Citadines Shinjuku). Everywhere else the AR picks
one framing, so dropping either column loses rows outright.

**However, a populated `valuation` is not always an AR-disclosed independent figure.** Three failure
modes found:

| REIT | what our `valuation` actually is |
|---|---|
| AU8U CapitaMall Shuangjing | a **copy artifact** — 156,443,600 is a converted echo of the agreed price (RMB 842.0m); the AR's own valuation figure is 156,907 |
| AJBU IC DC | an FX-converted **prior-year** Portfolio Statement figure; no valuer cited in the divestment section |
| T82U Suntec strata | explicitly **derived**: *"derived by multiplying the Rate of Lettable Floor Area per the 31 December 2023 and 31 December 2024 independent valuation reports"* — a blended benchmark, not an as-at valuation |

**Recommendation: keep `valuation`, rename it `independent_valuation`, and add a `valuation_basis`
column** (this does not exist today — raw has `carrying_value_basis`,
`gain_on_divestment_basis` and `net_proceeds_basis`, but no valuation equivalent) to separate
"AR-disclosed independent valuation" from "derived / converted / copied".

Two suspicions of mine that the evidence **refuted**, worth recording:
- C38U's `valuation == sale_price` is **genuine** — Savills valued it at exactly the price it sold
  for. Not an extraction copy.
- HMN Citadines Shinjuku's ~2x premium to valuation is **real** — valuation dated 31 Dec 2024, sale
  Oct 2025, against a genuine Tokyo hospitality re-rating. Not stale and not mis-currencied.

## 7. Deriving `gain_on_divestment` — neither formula works

I tested the stored gain against both proposals on the 42 rows where it is computable:

```
gain == sale_price − carrying_value :   3
gain == sale_price − valuation      :   6
reconciles to NEITHER               :  33
```

**But the stored gains are correct.** 9 of 12 rows checked against the ARs **match verbatim** — ME8U
3,492,000 · HMN 17,027,000 and 82,011,000 · T82U 14,992,000 · C38U 32.8m · J69U 11,272,000 · AU8U
7,309,000 · AJBU 31,611,000 · P40U 9,044,000. They simply aren't reproducible from the columns we
store, for four structural reasons:

1. **The AR's base is the carrying amount at the *disposal date***, after any final fair-value
   mark-up — not the prior-period-end `carrying_value` we hold. P40U's footnote is the clearest
   statement: *"the difference between **net proceeds (including directly attributable costs)** from
   divestment and the **carrying amount**"*.
2. **The AR nets off disposal costs**; our `sale_price` is usually the **gross** consideration.
   C38U: 688,000 − 15,393 divestment-related payments = 672,607 net proceeds.
3. **Some deals are equity disposals, not asset sales.** AU8U CapitaMall Shuangjing's 7,309k is a
   *gain on disposal of subsidiary* = consideration 140,720 − net identifiable assets 130,471 +
   recycled FX translation reserves 2,940. No property-level `price − carrying_value` can produce it.
4. **Part of the economic gain often sits in revaluation, not the divestment line.** Our own note:
   *"most of the EUR8.3m premium over carrying was booked as a **fair-value revaluation gain, NOT in
   the divestment line**; per-property divestment gain **NOT disclosed**"*.

Our `carrying_value_basis` notes also show the base is not uniform:
*"Prior-FY carrying (fair-value model): FY2024 AR last individual valuation 31/03/2023 col — already
held-for-sale at 31/03/2024 ... **One balance-date older**."*

**Recommendation: keep `gain_on_divestment` as-disclosed. Do not derive it.** Instead derive the two
things that *are* reliably computable and label them as derived:
- `premium_to_valuation_pct = transaction_price / independent_valuation − 1` (85 divestment rows)
- `gain_vs_book = transaction_price − carrying_value` (68 rows) — **as a separate, clearly-named
  derived field**, never overwriting the disclosed gain

And on option (A) specifically — `transaction_price − sgx_reit_property.purchase_price` — it is not
viable at all: the join on `(symbol, property_name)` matches only **39 of 117** divestment rows (67%
unmatched), because a property divested during the year is removed from the property table. Examples:
ME8U 'Tanglin Halt Cluster', M44U 'Century', 'Chee Wah', HMN 'Somerset Olympic Tower Tianjin'.

---

## Bugs found

### B1 — P1 · `gain_on_divestment` double-FX-converted on 3 N2IU rows

The gains were captured as the AR's **SGD** figures but tagged with the row's local currency, so
`build_final` converted an already-SGD number.

| property | raw gain | raw `gain_currency` | prod value | AR discloses |
|---|---|---|---|---|
| TS Ikebukuro Building | −3,093,000 | **JPY** | −26,891 | net loss S$3,093,000 |
| ABAS Shin-Yokohama | 408,000 | **JPY** | 3,547 | net gain S$408,000 |
| Festival Walk Tower | −10,263,000 | **HKD** | −1,693,395 | net loss S$10,263,000 |

Ratios confirm: 3,093,000 / 26,891 ≈ 115.0 (JPY/SGD); 10,263,000 / 1,693,395 ≈ 6.06 (HKD/SGD).
The `sale_price` values *are* genuinely local (¥5.4bn, HK$1.96bn) — the AR gave consideration in
local currency and the gain in SGD, which is the trap.

**Fix in raw** (`gain_currency` → SGD on those 3 rows), then rebuild. Not a `build_final` defect.

**Scope checked:** of 11 foreign-currency-tagged gain rows, only these 3 look wrong (gain/sale ratios
0.01–0.57%); ODBU, OXMU, SET, UD1U, XZL sit at a plausible 0.9–5.9%. One to confirm: DCRU FY2024
"2401 & 2403 Walsh Avenue" has `gain = 0` exactly against a US$178m sale.

### B2 — P1 · A17U FY2024 aggregate gain triple-counted

AR Note 11: *"On 27 February 2024, the Group completed the divestment of 77 Logistics Place, 62
Sandstone Place and 92 Sandstone Place located in Queensland, Australia, recognising a gain amounting
to **$628,000 (A$710,000)**."*

One gain and one S$64.2m consideration for **three properties**, stored identically on all three
rows. Our own `carrying_value_basis` note already says it: *"sale consideration and gain are
aggregate for the three properties, not per-property."* Summing triples both figures.

### B3 — P1 · Silent currency fallback (§2)

`ccy = d.get(ccol) or d.get('currency')` mis-converts any figure whose per-figure currency tag is
missing. Caused the DCRU 770,936 artifact and will recur.

### B4 — P2 · TS0U Lippo Plaza stored twice across FY2024 and FY2025 (§1)

### B5 — P2 · 8 non-completed rows carry a `completed_date` (§1)

---

## Prod is missing the columns that would answer most of this

Raw has **36** columns, `_final` **23**, prod **20**. Prod never sees:

| column | in final? | why it matters |
|---|---|---|
| `deal_id` | ✅ final, ✗ prod | Filled on 171/206 and **shared across rows of one multi-property deal** (`m44u:flexhub:divestment:2024` spans 2 rows). This is the mechanism for the A17U aggregate problem — and Calvin cannot use it. |
| `carrying_value_basis` | ✗ | free-text provenance; documents the stale-balance-date issue |
| `gain_on_divestment_basis` | ✗ | documents which gains are aggregates or non-derivable |
| `net_proceeds_basis` | ✗ | documents whether net proceeds are disclosed or derived |
| per-figure currencies (6 cols) | ✗ | `purchase_price_currency`, `sale_price_currency`, … |

`source_type` is `'annual_report'` on all 206 rows — no information today, though it is the natural
hook if SGX announcements are ever ingested. `announcement_refs` is filled on 1 row.

**Recommendation: promote `deal_id` to prod.** It is the cheapest fix for aggregate/multi-property
deals and for detecting duplicates like B4 — though note the two TS0U rows have differently-slugged
`deal_id`s, so slug generation needs to be deterministic for it to work as a dedupe key.

---

## Proposed target shape

```sql
sgx_reit_property_transaction (
  symbol, financial_year,
  deal_id                       text,     -- PROMOTE from final; groups multi-property deals
  transaction_type              text,     -- acquisition | divestment | partial_divestment
  status                        text,     -- keep all rows; filter in the view
  property_name                 text,
  counterparty                  text,
  description                   text,
  interest_transacted_pct       numeric,  -- was interest_pct; stake TRANSACTED, null when 100%
  completed_date                date,     -- drop announced_date + transaction_date
  transaction_price             numeric,  -- merged purchase_price + sale_price
  net_sale_proceeds             numeric,  -- after disposal costs; keep, it is a distinct concept
  independent_valuation         numeric,  -- was valuation; KEEP
  valuation_date                date,
  valuation_basis               text,     -- NEW: disclosed | derived | converted | copied
  carrying_value                numeric,
  gain_on_divestment            numeric,  -- as-disclosed; NOT derived
  gain_loss_pct                 numeric,
  gain_loss_pct_basis           text      -- was gain_basis; it qualifies the PCT, not the gain
)
```

Derived at the API/view layer, clearly labelled as derived:
`premium_to_valuation_pct`, `gain_vs_book`.

---

## Action order

**Mechanical, no decision needed:**
1. **B1** retag `gain_currency` → SGD on the 3 N2IU rows; rebuild and re-promote.
2. **B3** make the currency fallback raise instead of defaulting to the row currency.
3. **B2** de-aggregate or flag the A17U three-row divestment.
4. **B4** remove the duplicate TS0U Lippo Plaza row.
5. **B5** clear `completed_date` on the 8 non-completed rows.
6. Retag P40U `gain_basis` → `vs_book_value` (§5).
7. Backfill XZL Hyatt Place Pittsburgh Airport `completed_date` = 2024-03-25.
8. Null `sale_price` on acquisition rows in `extracted/*/property_transactions.json`, then merge to
   `transaction_price`.

**Needs a decision:**
9. Keep vs drop `valuation` (§6) — recommend keep + `valuation_basis`.
10. Promote `deal_id` to prod (recommend yes).
11. Filter non-completed rows in the table or in a view (recommend view).
12. Strata-unit aggregate rows: split per unit, or flag as aggregate (§4).
13. Rename `gain_basis` → `gain_loss_pct_basis` (§5).

---

## Verification note

Sub-agents produced well-cited evidence here, but across this and the earlier `pct_basis` /
`gross_revenue` work they generated **four false "no table exists" findings** (AJBU, J85, SET) and one
mis-diagnosed root cause (the DCRU 770,936, attributed to `build_final` when it originates in a NULL
currency tag in raw). Every load-bearing claim above was re-checked by hand against the AR text or the
raw table. Our own `extracted/*/_notes.json` repeatedly contained the answer already — it should be
the first place checked, not the last.
