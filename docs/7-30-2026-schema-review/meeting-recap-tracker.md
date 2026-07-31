# Schema review — task tracker

**Source:** meeting recap, 2026-07-30. Items are stated as raised in the meeting.
**Scope:** prod data.

Status: `[ ]` open · `[x]` done · `[~]` decided, not yet applied · `[?]` needs decision

Decisions are recorded in `findings-and-recommendations.md` § Conclusions.

---

## sgx_reit_profile

- [x] No issue.

---

## sgx_reit_property

- [~] `gross_lettable_area`, `net_lettable_area`, `gross_floor_area`: how many of these are null in each.
- [~] `effective_date`, `lease_term_years`, `lease_expiry_date`: drop either effective or expiry date.

---

## sgx_reit_top_tenant and sgx_reit_trade_mix

- [ ] `pct_basis`: what are the unique values? we can work from there.

---

## sgx_property_transaction

- [ ] Remove all status that is not "completed".
- [~] `transaction_type` and `transaction_price` (drop `purchase_price` and `sale_price`).
- [~] What is `interest_pct`? Drop if not important.
- [~] Drop `announced_date` and `transaction_date`. Don't see a value here.
- [~] `gain_basis` — is this necessary?
- [~] `valuation_date` and `carrying_value` should be sufficient. Drop `valuation`.
- [~] Where is `gain_on_divestment` be derived from?
  - [x] `transaction_price` − `sgx_reit_property.purchase_price`
  - [x] `transaction_price` − `carrying_value`

> Resolved 2026-07-31 — target schema agreed in `transaction-target-schema-AGREED.md`.
> Divestments are recorded as `gain_loss_pct` + `reference_value` + `reference_basis` +
> `interest_pct` + `deal_id`; acquisitions as `purchase_price` + `completed_date`.

Open work arising:

- [ ] P0 — re-promote to fix 61 stale `gain_loss_pct` rows in prod (dev is correct).
- [ ] Populate `reference_value` / `reference_basis` across 136 divestments.
- [ ] Resolve ~39 rows whose dollar gain reconciles to no formula.
- [ ] Backfill `deal_id` on aggregate deals; make slug generation deterministic (TS0U Lippo Plaza).
- [ ] Promote `deal_id` to prod.
- [ ] Source the 45 divestments missing a percentage or a reference.
- [ ] Add Invariant 1 (internal) + Invariant 2 (cross-table vs `sgx_reit_property`) as gates.
- [ ] Confirm with Evelyn: reported P&L gain leaves the table on equity sales (see doc).

---

## sgx_reit_performance

- [ ] `number_of_shareholder_units` should never be NULL.
- [ ] `distribution_record`: fix data structure. `period_start`, `period_end`, remove `ex_date`, `pay_date`.
- [ ] Drop `distribution_period_months`.
- [ ] `portfolio_occupancy` and `interest_coverage_ratio` are %.
- [ ] `distribution_paid` is from distribution statement, we are using this. Drop `distribution_cash_paid`.
- [ ] `net_distributable_income` — need to clarify what is this.
- [ ] `adjusted_distributable_income` + `distributable_income_opening` = `net_distributable_income`
- [ ] `net_distributable_income` − `distribution_paid` − `distributable_income_closing` = upcoming distribution amount
- [ ] `distribution_pool_other_movements`: confirm that this is a standalone and how is this used.

---

## Also raised

- [ ] Naming — make sure of what the data is and the naming.
- [ ] Dropping some columns and restructuring/flattening some columns.
