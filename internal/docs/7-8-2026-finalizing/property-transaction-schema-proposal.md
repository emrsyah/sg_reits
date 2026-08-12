# PROPOSAL — `sgx_reit_property_transaction` schema (SCHEMA-FIRST)

**Status: DRAFT / awaiting emirsyah go-ahead.** This is the **schema** pass — decide the final shape
of the table. VALUE (where each figure is extracted from) + the actual re-extraction come **after**
the schema is locked. Captured 2026-07-09.

## Why now
Colleagues want per-deal acquisition/divestment data that the **annual report does not fully
disclose**. It lives in SGX **regulatory announcements** ("Asset Acquisitions and Disposals"), which
an S-REIT MUST issue. Two announcement types per deal: a **plan** (proposed) and a **completion**.

### What the colleagues asked to capture (verbatim wishlist)
1. final cash amount received (after deduction of transaction cost)
2. buyer
3. the agreed property sale price
4. property's latest market valuation (during time of sale)
5. property's book value on balance sheet
6. gain/(loss) %

### Grounding — the two sample announcements (MIT / ME8U, Philadelphia data centre)
- **Plan (25 May 2026):** sale price US$14.5m (satisfied in cash); independent valuation US$13.9m
  **as at 31 Mar 2026**; **4.3% premium** over valuation; buyer = "non-interested third-party"
  (**unnamed**); expected completion Q3 2026. **Absent:** book value, transaction cost, net proceeds,
  gain%.
- **Completion (23 Jun 2026):** completion date 22 Jun 2026 + updated portfolio count. **No financial
  figures at all.**

### SOURCE PRECEDENCE — AR-first, announcement as top-up (emirsyah 2026-07-09)
The parsed annual reports already carry most of the wishlist, so the **AR is the default source**;
the SGX announcement supplements. Evidence from the current extracts:
- REITs that publish an **Acquisitions/Divestments summary table** disclose per-deal sale price,
  valuation, valuation date, **buyer**, carrying value, gain, AND net proceeds
  (e.g. M44U p48; J91U p47-48 — the latter even lists announced-but-not-completed deals with buyer +
  premium%).
- FS-note-only REITs (HMN, C38U, ME8U, AU8U, BUOU, CY6U, AJBU) disclose gain / carrying_value /
  net_proceeds / valuation, sometimes without buyer or sale price.
- **Gaps the announcement fills:** (a) JV/NCI deals the AR leaves null (K71U, C38U JV rows);
  (b) deals AFTER the fiscal year / subsequent events with no AR row yet (the MIT Philadelphia deal
  is May-Jun 2026 = FY2027, absent from FY2025 AR); (c) `transaction_cost` / exact net cash.
- Also note: the AR commonly discloses **gain% as a "premium over valuation"** ("3.5% above
  valuation") — this maps directly to `gain_loss_pct` with `gain_basis='vs_valuation'`.

**Rule: per-field source precedence, not a blanket overwrite.** [1] AR fills every field it
discloses; [2] the announcement fills only AR-null fields, no-AR-row deals, and cost/net-cash;
[3] `source_type` per row (`annual_report` default -> `both` when supplemented), and the existing
per-field `*_basis` text records which source each figure came from. Announcement NEVER overwrites a
disclosed AR figure — on conflict, keep AR + flag.

### Fill-rate reality — will this be null-heavy? (measured on 47 files / 145 rows)
Checked against the CURRENT extracts, so this is the real picture, not a guess.
- **Divestments (n=91) already fill well:** counterparty 85.7%, carrying_value 83.5%,
  gross_sale_price 79.1%, valuation 78.0%, any-date 94.5%; gain_abs 40.7%, net_sale_proceeds 20.9%.
- **Acquisitions (n=54):** purchase_price 74.1%, valuation 83.3%, counterparty 90.7%, date 96.3% —
  divestment-only fields are null **structurally** (an acquisition has no sale price/gain/carrying),
  not because of this schema.
- **New columns that start empty and why it's fine:**
  - `gain_loss_pct` 0% and `valuation_date` 11% today, but BOTH are **derivable/liftable** from data
    already present (78-79% of divestments have BOTH sale price and valuation), so they fill in the
    VALUE pass. (`transaction_cost` was 0% -> **DROPPED**; `net_sale_proceeds` already gives "final
    cash", populated only where a net figure is disclosed ~21%.)
  - `source_type` / `announcement_refs` / `announced_date` / `completed_date` are null-by-design for
    AR-only rows; meaningful only when an announcement supplements.
- **Conclusion:** three kinds of null — structural N/A (acquisition vs divestment), null-by-design
  provenance, and genuine not-disclosed. None is schema bloat; an as-disclosed table SHOULD be null
  where the source is silent (§0). No sea of nulls on the fields that matter.

### The three hurdles (Evelyn) and how the schema answers them
| # | Hurdle | Schema/pipeline answer |
|---|---|---|
| H1 | SGX announcements can't be filtered by sector (REITs) | collection concern, NOT schema. Filter by our known REIT issuer list in the fetch pipeline. AR-first shrinks the volume: fetch an announcement when a deal has NO AR row, OR when a wanted field (net cash / buyer / gain%) is still null after the AR — not for deals the AR already covers fully. |
| H2 | No fixed format for the declaration | normalized typed columns for the wishlist + `raw` jsonb (full original) + per-figure `_basis` provenance text. Anything unmapped survives in `raw`. |
| H3 | Info in the plan but not the completion (or vice-versa) | **one row per deal, merged across both announcements**; each field filled from whichever announcement discloses it; provenance per announcement in a new `announcement_refs` jsonb. |

## Current schema (recap)
`PropertyTransaction` (models.py:472) already has: `transaction_type`, `status`
(completed/announced/terminated), `property_name`, `transaction_date`, `purchase_price`,
`gross_sale_price`, `net_sale_proceeds`, `carrying_value`, `gain_on_divestment`, `valuation`,
`interest_pct`, per-figure `*_currency`, per-figure `*_basis`, `counterparty`, `currency`,
`source_page`. Source today = the **annual report**.

### Wishlist -> existing columns (mostly already covered)
| wishlist | existing column | gap |
|---|---|---|
| [1] final cash received (net of costs) | `net_sale_proceeds` | ok — populated ONLY when the report discloses a distinct net-of-cost figure (~21%); else null. `transaction_cost` DROPPED (0% fill, and net proceeds already gives "final cash") |
| [2] buyer | `counterparty` | ok — holds the buyer name, or the disclosed descriptor (e.g. "Non-interested third-party purchaser") when unnamed |
| [3] agreed sale price | `sale_price` (renamed from `gross_sale_price`) | ok — the as-disclosed sale consideration; neutral name (don't claim "gross/before-costs" unless the report says so) |
| [4] latest market valuation at sale | `valuation` | + `valuation_date` (the "as at" date) |
| [5] book value on balance sheet | `carrying_value` | ok |
| [6] gain/(loss) % | (none — only absolute `gain_on_divestment`) | + `gain_loss_pct` + `gain_basis` |

## Proposed schema changes (the DELTA to lock)

### New columns
| column | type | purpose |
|---|---|---|
| `gain_loss_pct` | float | realized gain/(loss) as a signed %; pairs with `gain_basis` |
| `gain_basis` | str enum | what the gain (abs + pct) is measured against: `vs_book_value` \| `vs_valuation` \| `vs_cost`. AR gain is vs book; announcements often quote premium vs valuation. Makes every gain self-describing. |
| `valuation_date` | str (YYYY-MM-DD) | the "as at" date of the cited market valuation |
| `announced_date` | str (YYYY-MM-DD) | date of the PLAN/proposed announcement |
| `completed_date` | str (YYYY-MM-DD) | date completion was announced/effective |
| `source_type` | str enum | `annual_report` (**default**) \| `sgx_announcement` \| `both` — AR-first; `both` when an announcement supplements |
| `announcement_refs` | jsonb list | `[{stage: "plan"\|"completion", date, url, ref, sub_title}]` — the SGX provenance, one entry per announcement (solves H3 + no-fixed-format H2) |
| `deal_id` | str | **stable deal identity** — the join key for merging plan+completion and for dedup vs AR-sourced rows. See normalization below. |

### Renames & drops (honesty + fill — 2026-07-09)
- **Rename `gross_sale_price` -> `sale_price`.** For the ~62 divestments that disclose a single
  consideration, the report rarely states it is "before transaction costs", so "gross" over-claims.
  `sale_price` = the as-disclosed sale consideration. Where a report separately discloses BOTH a gross
  price AND a net figure (the ~10 known cases), `sale_price` holds the gross and `net_sale_proceeds`
  the net — both present, so still distinguishable.
- **Drop `transaction_cost`** (0% fill; `net_sale_proceeds` already delivers "final cash after costs").
- **Keep only fields that fill AND are enough to compute gain honestly:** `sale_price`,
  `carrying_value`, `valuation`, `gain_on_divestment` (+`gain_loss_pct`/`gain_basis`) — gain is
  disclosed (~41%) or derived = `(net_sale_proceeds or sale_price) - carrying_value`, with `gain_basis`
  naming what it's measured against so nothing is mislabeled.

### Kept / clarified
- `transaction_date` stays as the **primary effective date** = `completed_date` if completed, else
  `announced_date`. (Keeps existing views working; the two new dates add lifecycle detail.)
- `status` already covers the plan->completion->terminated lifecycle; `announcement_refs` + the two
  dates add the audit trail.
- `gain_on_divestment` stays (absolute); now always paired with `gain_basis`.
- `valuation` stays (absolute); paired with new `valuation_date`.
- `counterparty` holds the named buyer/seller; when the party is unnamed, store the disclosed
  descriptor verbatim (e.g. "Non-interested third-party purchaser"). No separate type column.
- `raw` jsonb stays as the catch-all for anything the free-form announcement doesn't map (H2).

## Column glossary (final schema — existing + new)

**Identity & lifecycle**
- `symbol`, `financial_year` — which REIT and reporting year the row belongs to.
- `deal_id` *(new)* — stable per-deal key; joins a plan row to its completion, and dedups an
  announcement against the AR row for the same deal.
- `transaction_type` — `acquisition` | `divestment` | `announced_divestment` | `partial_divestment`
  | `divestment_terminated`.
- `status` — lifecycle: `completed` | `announced` | `terminated`.
- `property_name` — the asset transacted.
- `interest_pct` — % ownership stake bought/sold (100 = whole asset; <100 for partial/JV/NCI deals).

**Dates**
- `announced_date` *(new)* — date of the plan/proposed announcement.
- `completed_date` *(new)* — completion/effective date.
- `transaction_date` — primary effective date (= `completed_date` if completed, else `announced_date`);
  kept so existing views keep working.

**Money — acquisition side**
- `purchase_price` — consideration PAID to acquire the asset (buy side).

**Money — divestment side**
- `sale_price` — the **as-disclosed sale consideration** (renamed from `gross_sale_price`). The
  headline transacted price; we do NOT assert "gross / before costs" unless the report says so.
- `net_sale_proceeds` — the **cash the REIT keeps net of transaction costs**, populated ONLY when the
  report discloses a distinct net figure (else null — do NOT derive). Example (CY6U CyberPearl &
  CyberVale): consideration 161,700, disclosed "net sales consideration after divestment expenses"
  159,922 (Note 25a). Counter-example: J69U's net 34,128 is DERIVED (carrying + net gain), so under
  this rule it would be null, not stored as net.

**Valuation & book value**
- `valuation` — the **independent appraised market value** benchmark around the deal (what a valuer
  says it's worth), distinct from the price actually transacted. A "premium/discount to valuation"
  compares `sale_price` to this.
- `valuation_date` *(new)* — the "as at" date of that valuation.
- `carrying_value` — the **book value on the balance sheet** just before divestment; the accounting
  basis the realized gain is measured against.

**Gain / (loss)**
- `gain_on_divestment` — absolute realized gain or loss (signed).
- `gain_loss_pct` *(new)* — the same gain as a signed %.
- `gain_basis` *(new)* — what the gain is measured against: `vs_book_value` (proceeds - carrying;
  the AR/accounting gain) | `vs_valuation` (price - valuation; the "premium over valuation") |
  `vs_cost` (vs original purchase cost). Stops the book gain and the valuation premium being
  conflated — they are different numbers.

**Counterparty**
- `counterparty` — buyer (divestment) or seller (acquisition); holds the disclosed descriptor
  (e.g. "Non-interested third-party purchaser") when the party is unnamed.

**Provenance / currency**
- `source_type` *(new)* — `annual_report` (default) | `sgx_announcement` | `both`.
- `source_page` — AR page for the row's figures.
- `announcement_refs` *(new)* — jsonb list of the SGX announcements (plan + completion) with
  date / url / ref.
- `currency` — row-level presentation currency; the default for any untagged per-figure currency.
- `*_currency` (e.g. `sale_price_currency`, `carrying_value_currency`, `gain_currency`, ...) —
  per-figure currency overrides for deals that mix currencies.
- `*_basis` (e.g. `carrying_value_basis`, `gain_on_divestment_basis`, `net_proceeds_basis`) —
  per-figure provenance / derivation notes (which line/page, or "DERIVED: ...").
- `raw` — the full original extracted object; anything not mapped to a typed column survives here.

### Derivation policy (as-disclosed first)
- Prefer the **disclosed** gain / gain% / net proceeds. If a figure is derived, record it in the
  matching `_basis` text and null nothing silently (REFERENCE §0.8: a failed reconcile = investigate,
  never plug).
- When gain% is NOT disclosed but the inputs are, derive it and flag via `gain_basis`:
  `vs_valuation` = `sale_price - valuation` (the colleagues' "premium over valuation"), or
  `vs_book_value` = `(net_sale_proceeds or sale_price) - carrying_value` (the AR/accounting gain).
  `gain_basis` records which so the two are never conflated.

## Normalization model (one row per deal)
**Deal identity (`deal_id`) — the missing join key.** Today `(symbol, property_name)` is NOT
unique: a property can be acquired then later divested, and tranche/partial divestments repeat the
name. Without a stable key we can neither merge a plan row with its completion row nor dedup an
announcement against an existing AR row (risking double-counted divestments). So:
- `deal_id` is a stable per-deal string. Population, in order of preference:
  1. **Anchor on the PLAN announcement** — its SGX reference (e.g. `SG260525OTHRQWOI`) or URL. The
     completion announcement explicitly back-references the plan ("Further to the press release dated
     25 May 2026"), so completion -> plan is resolvable and both share the plan's `deal_id`.
  2. If no plan announcement (AR-only or completion-only), a **deterministic slug**
     `{symbol}:{normalized_property_name}:{transaction_type}:{effective_year}`.
- **Merge** plan + completion into one row keyed by `deal_id`; fill each field from whichever
  announcement discloses it; keep both in `announcement_refs`; set `status`/dates from the lifecycle.
- **AR <-> announcement reconciliation:** match an announcement to an existing AR row on
  `(symbol, normalized_property_name, transaction_type)` within a fiscal window; on match set
  `source_type='both'` (announcement is the per-deal authority, AR fills gaps); on ambiguous/no
  match, keep separate + flag rather than silently merge (never double-count, never guess).

## Simulation — how rows look under the new schema

### Row A — AR-only divestment (M44U "30 Tuas South Avenue 8", from p48 divestments table + FS note p173)
```json
{
  "deal_id": "M44U.SI:30-tuas-south-ave-8:divestment:2024",
  "symbol": "M44U.SI", "financial_year": 2025,
  "transaction_type": "divestment", "status": "completed",
  "property_name": "30 Tuas South Avenue 8",
  "announced_date": null, "completed_date": "2024-06-14", "transaction_date": "2024-06-14",
  "sale_price": 10500000, "net_sale_proceeds": null,
  "carrying_value": 9500000, "valuation": 9500000, "valuation_date": "2024-01-01",
  "gain_on_divestment": 1000000, "gain_loss_pct": 10.5, "gain_basis": "vs_book_value",
  "counterparty": "Koh Khang Hin Pte. Ltd.",
  "currency": "SGD",
  "source_type": "annual_report", "source_page": 173,
  "announcement_refs": [],
  "raw": {"disclosure_source_page": 48}
}
```
Everything comes from the AR. `gain_loss_pct` 10.5 = (10,500 - 9,500)/9,500; here valuation == carrying,
so `vs_book_value` and `vs_valuation` coincide. `net_sale_proceeds` null (AR discloses no net figure)
— a completion announcement could later fill it and flip `source_type` -> `both`.

### Row B — announcement-only divestment, merged plan+completion (MIT/ME8U Philadelphia; after-FYE, no AR row)
```json
{
  "deal_id": "SG260525OTHRQWOI",
  "symbol": "ME8U.SI", "financial_year": 2027,
  "transaction_type": "divestment", "status": "completed",
  "property_name": "2000 Kubach Road, Philadelphia, Pennsylvania (United States)",
  "announced_date": "2026-05-25", "completed_date": "2026-06-22", "transaction_date": "2026-06-22",
  "sale_price": 14500000, "net_sale_proceeds": null,
  "carrying_value": null, "valuation": 13900000, "valuation_date": "2026-03-31",
  "gain_on_divestment": null, "gain_loss_pct": 4.3, "gain_basis": "vs_valuation",
  "counterparty": "Non-interested third-party purchaser",
  "currency": "USD",
  "source_type": "sgx_announcement", "source_page": null,
  "announcement_refs": [
    {"stage": "plan", "date": "2026-05-25", "ref": "SG260525OTHRQWOI",
     "url": "https://links.sgx.com/1.0.0/corporate-announcements/7WZIGCBZH2IRO9R5/...",
     "sub_title": "Mapletree Industrial Trust Divests Philadelphia Data Centre for US$14.5 million"},
    {"stage": "completion", "date": "2026-06-23", "ref": "SG260623OTHRFJC4",
     "url": "https://links.sgx.com/1.0.0/corporate-announcements/7D5SVWVRCN04ST56/...",
     "sub_title": "Completion of Divestment of Philadelphia Data Centre"}
  ],
  "raw": {"expected_completion": "Q3 2026", "nla_sqft": 124190, "tenure": "freehold", "satisfied_in": "cash"}
}
```
`deal_id` anchors on the plan reference; the completion announcement back-references it, so both share
one row. `valuation` 13,900 + `gain_loss_pct` 4.3 (`vs_valuation`) are the disclosed "4.3% premium above
valuation". `carrying_value` / `net_sale_proceeds` null — book value & any costs are
NOT in either announcement (they'd land in a future AR, flipping `source_type` -> `both`).

### Row C — the "both" merge (conceptual)
Start from Row A (AR-sourced). A later completion announcement discloses net cash S$10,300 and names
the same buyer -> merge on `deal_id`: set `net_sale_proceeds`=10,300, append the announcement to
`announcement_refs`, `source_type` -> `both`. The AR-disclosed `sale_price`/`valuation`/`gain` are
**kept, never overwritten**.

## Open decisions (lock these = schema final)
- [ ] Approve the 8 new columns above (names + types)?
- [ ] `announcement_refs` as a **jsonb list** (recommended, flexible) vs flat
      `plan_url`/`completion_url` columns?
- [ ] Merge plan+completion into **one row** (recommended) vs one row per announcement?
- [ ] gain% derivation denominator when undisclosed: **vs_valuation** (colleagues' formula) vs
      **vs_book_value** (AR convention) — or derive BOTH when inputs allow and store `gain_basis`
      per figure? (default recommendation: store disclosed only; derive vs_valuation with a flag)
- [ ] `deal_id` scheme: anchor on the **plan announcement ref/URL** (recommended) with a
      deterministic slug fallback — approve? And is the `(symbol, property_name, transaction_type,
      window)` AR-reconciliation match acceptable, or do you want announcement rows kept fully
      separate from AR rows (no merge)?
- [ ] Confirm **AR-first per-field precedence** (AR is the default; the announcement fills only
      AR-null fields, deals with no AR row, and net-cash; it NEVER overwrites a disclosed AR
      figure — conflict = keep AR + flag)?
- [ ] Approve **rename `gross_sale_price` -> `sale_price`** and **drop `transaction_cost`**?

## Out of scope here (VALUE pass, after schema locks)
- The SGX-announcement fetch/filter pipeline (H1), the per-field extraction sourcing, and the
  re-extraction/backfill across the corpus (incl. NCI-booked + subsequent-event deals from prior
  session). Tracker #11/#12.
