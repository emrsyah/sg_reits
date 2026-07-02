# Null report by column & AR (>20% null) — post-recovery

> **Round-2 recovery update (2026-07-02, applied to Supabase).** Re-measured live nulls (matched this doc), fanned out 17 Sonnet re-extraction agents scoped to high-yield partial-null anomalies + a few full-null segment-vs-missed checks (verified-structural skipped). Result: most surviving nulls **confirmed genuinely structural** (no new fills) — segment-only NPI, single-tenant confidentiality dashes, hospitality RevPAR, freehold "NA", combined rows, GLA≠NLA, under-development. **Real recoveries:** D5IU `ownership` 29→0 null (28×100% + Lippo Plaza Jogja 68.3%); J69U `npi_pct` 11→3 null (8 derived, JVs left null); MXNU `occupancy_rate` 4→2 null. **Surgical fixes:** ME8U "2055 East Technology Circle, Tempe" tenure Freehold→Leasehold/"58 years"; J91U "21/23 Ubi Road 1" `market_valuation` 41.7m→42.5m; J69U nla column-shift verified already-correct (no change). Open discrepancies flagged, not changed: M44U Flexhub `gross_revenue` (possible sale-price mis-map), J69U Northpoint N-Wing NPI (combined figure). Per-column counts below are the PRE-round-2 snapshot; the deltas above are the only changes since.
>
> **Deliberately out-of-scope in round 2 (not dispatched — marginal & almost-certainly structural):** J85 `net_property_income` (1/23, hospitality), DCRU `gross_revenue` (2/11, data-centre), HMN `gross_revenue` (1/103, hospitality/local-ccy). Left for a future pass if desired.


_Property table = ACTIVE rows only (divested/held-for-sale excluded). Other tables = all rows. Generated live from Supabase (2026-07-02, after the Phase-3 recovery pass)._

**How to read:** each column section lists the AR breakdown as `SYMBOL:nulls` (property & transaction also show `/total`, e.g. `A17U:223/223` = all 223 null).

---

## Orientation — where to actually look

### 🔍 Worth reviewing yourself (mixed disclosure — some ARs have it, some don't)
- **`property.nla` (37%)**, **`property.gfa` (63%)**, **`property.lease_term_years` (62%)**, **`property.lease_expiry_date` (73%)**
  - BUT large chunks of these nulls are **hospitality** (M44U, HMN, XZL, Q5T, J85 → size = rooms/keys, not area) and **freehold** assets (no land-lease term/expiry by nature). Filter those out; the rest is the real review surface.

### ✅ Structural — verified not-disclosed (not gaps)
- **`property.net_property_income` (88%)** & **`property.npi_pct` (95%)** — 21 REITs disclose NPI only at segment/portfolio level (A17U, M44U, MXNU, BUOU, HMN, ME8U, SET, C2PU, J91U, UD1U, XZL, AW9U, O5RU, C38U, AJBU, ODBU, M1GU, 8C8U, OXMU, Q5T, TS0U).
- **`property.trade_mix` (100%)**, **`property.major_tenants` (80%)** — this data lives in the dedicated `sgx_reit_trade_mix` / `sgx_reit_top_tenant` tables; null-on-property is by design.
- **`property.gla` (99%)** — superseded by `nla`/`gfa`. **`property.divestment_price` (100%)** — divestments live in `sgx_reit_property_transaction`.
- **`financial.employee_breakdown` (78%)** — externally-managed REITs have no trust-level staff.
- **`performance.adjusted_distributable_income` (97%)** — method-2-only field; 1 real value (M1GU) → **Phase-4 DROP candidate**.

### ⚙️ By-design conditional (not gaps)
- **All `property_transaction` high-nulls** — acquisition-only fields (`purchase_price`) are null on divestment rows and vice-versa (`carrying_value`, `gross_sale_price`, `net_sale_proceeds`, and the `*_basis` / `*_currency` families). `interest_pct` (95%) = only partial/NCI deals.
- **`property.net_property_income_currency` (88%)**, **`original_currency`/`original_value` (88%)**, **`area_unit` (41%)** — audit-trail fields, only populated on the subset that needs them (e.g. foreign-currency figures). Null = "same as presentation currency" or "no local figure", not missing.
- **`property.effective_date` (96%)**, **`property.flags` (88%)** — edge-case / provenance fields, expected sparse.

---

## performance — 37 rows

### `adjusted_distributable_income` — 36/37 null (97%)
  8C8U:1, A17U:1, AJBU:1, AU8U:1, AW9U:1, BMOU:1, BTOU:1, BUOU:1, C2PU:1, C38U:1, CMOU:1, CRPU:1, CY6U:1, D5IU:1, DCRU:1, DHLU:1, HMN:1, J69U:1, J85:1, J91U:1, JYEU:1, K71U:1, M44U:1, ME8U:1, MXNU:1, N2IU:1, O5RU:1, ODBU:1, OXMU:1, P40U:1, Q5T:1, SET:1, T82U:1, TS0U:1, UD1U:1, XZL:1


## financial — 37 rows

### `employee_breakdown` — 29/37 null (78%)
  8C8U:1, A17U:1, AJBU:1, AU8U:1, AW9U:1, BMOU:1, BTOU:1, C2PU:1, C38U:1, CMOU:1, CRPU:1, CY6U:1, D5IU:1, DCRU:1, DHLU:1, J69U:1, J85:1, J91U:1, K71U:1, M1GU:1, M44U:1, MXNU:1, N2IU:1, O5RU:1, P40U:1, T82U:1, TS0U:1, UD1U:1, XZL:1


## property — 1591 rows (active)

### `net_property_income` — 1404/1591 null (88%)
  A17U:223/223, M44U:176/176, MXNU:148/148, BUOU:113/113, HMN:103/103, ME8U:99/99, SET:95/95, C2PU:74/74, J91U:71/71, UD1U:53/53, XZL:32/32, AW9U:31/31, O5RU:27/27, C38U:25/25, AJBU:24/24, ODBU:22/22, M1GU:18/18, 8C8U:14/14, OXMU:13/13, Q5T:13/13, DCRU:10/11, TS0U:6/6, T82U:4/12, JYEU:2/5, K71U:2/15, N2IU:2/18, CY6U:1/13, D5IU:1/29, J69U:1/11, J85:1/23

### `npi_pct` — 1506/1591 null (95%) — _updated live post-round-2_
  A17U:223/223, M44U:176/176, MXNU:148/148, BUOU:113/113, HMN:103/103, ME8U:99/99, SET:95/95, C2PU:74/74, J91U:71/71, UD1U:53/53, XZL:32/32, AW9U:31/31, D5IU:29/29, O5RU:27/27, C38U:25/25, AJBU:24/24, J85:23/23, ODBU:22/22, DHLU:19/19, M1GU:18/18, N2IU:15/18, 8C8U:14/14, OXMU:13/13, Q5T:13/13, T82U:12/12, DCRU:11/11, BTOU:6/6, TS0U:6/6, JYEU:5/5, J69U:3/11, K71U:2/15, CY6U:1/13

### `trade_mix` — 1587/1591 null (100%)
  A17U:223/223, M44U:176/176, MXNU:148/148, BUOU:113/113, HMN:103/103, ME8U:99/99, SET:95/95, C2PU:74/74, J91U:71/71, UD1U:53/53, XZL:32/32, AW9U:31/31, D5IU:29/29, O5RU:27/27, C38U:25/25, AJBU:24/24, J85:23/23, ODBU:22/22, DHLU:19/19, M1GU:18/18, N2IU:18/18, AU8U:17/17, K71U:15/15, 8C8U:14/14, CMOU:13/13, CY6U:13/13, OXMU:13/13, Q5T:13/13, T82U:12/12, DCRU:11/11, J69U:11/11, P40U:9/9, BMOU:6/6, BTOU:6/6, TS0U:6/6, JYEU:5/5

### `major_tenants` — 1269/1591 null (80%)
  A17U:223/223, M44U:176/176, MXNU:148/148, HMN:103/103, ME8U:99/99, SET:95/95, J91U:71/71, C2PU:60/74, XZL:32/32, D5IU:29/29, O5RU:27/27, AJBU:24/24, J85:23/23, M1GU:18/18, N2IU:18/18, AU8U:17/17, 8C8U:14/14, CY6U:13/13, OXMU:13/13, Q5T:13/13, T82U:12/12, DCRU:11/11, J69U:10/11, BMOU:4/6, TS0U:4/6, DHLU:3/19, JYEU:2/5, ODBU:2/22, P40U:2/9, C38U:1/25, K71U:1/15, UD1U:1/53

### `gla` — 1573/1591 null (99%)
  A17U:223/223, M44U:176/176, MXNU:148/148, BUOU:113/113, HMN:103/103, ME8U:99/99, SET:95/95, C2PU:74/74, J91U:71/71, UD1U:46/53, XZL:32/32, AW9U:31/31, D5IU:29/29, O5RU:27/27, C38U:25/25, AJBU:24/24, J85:23/23, ODBU:22/22, DHLU:19/19, M1GU:18/18, N2IU:18/18, AU8U:17/17, K71U:15/15, 8C8U:14/14, CMOU:13/13, CY6U:13/13, OXMU:13/13, Q5T:13/13, T82U:12/12, DCRU:11/11, P40U:7/9, BMOU:6/6, BTOU:6/6, TS0U:6/6, JYEU:5/5, CRPU:4/4, J69U:2/11

### `nla` — 587/1591 null (37%)
  M44U:176/176, HMN:103/103, C2PU:74/74, UD1U:53/53, XZL:32/32, AW9U:31/31, ME8U:26/99, J85:21/23, M1GU:18/18, 8C8U:14/14, CY6U:13/13, Q5T:5/13, AU8U:4/17, J91U:3/71, P40U:3/9, JYEU:2/5, K71U:2/15, N2IU:2/18, TS0U:2/6, A17U:1/223, J69U:1/11, T82U:1/12

### `gfa` — 1010/1591 null (63%)
  M44U:176/176, MXNU:148/148, BUOU:113/113, HMN:103/103, SET:95/95, ME8U:82/99, UD1U:53/53, XZL:32/32, O5RU:27/27, ODBU:22/22, DHLU:19/19, N2IU:18/18, K71U:15/15, CMOU:13/13, J85:13/23, OXMU:13/13, AJBU:12/24, T82U:12/12, DCRU:11/11, P40U:8/9, BTOU:6/6, C38U:5/25, CY6U:4/13, JYEU:4/5, J91U:3/71, J69U:2/11, A17U:1/223

### `effective_date` — 1533/1591 null (96%)
  A17U:223/223, M44U:176/176, MXNU:142/148, BUOU:113/113, HMN:103/103, ME8U:99/99, SET:95/95, C2PU:71/74, J91U:71/71, UD1U:53/53, XZL:32/32, D5IU:29/29, AW9U:28/31, O5RU:27/27, AJBU:24/24, C38U:24/25, ODBU:22/22, DHLU:18/19, M1GU:18/18, N2IU:18/18, AU8U:17/17, K71U:15/15, CMOU:13/13, CY6U:13/13, OXMU:13/13, Q5T:13/13, DCRU:11/11, J85:11/23, P40U:9/9, T82U:7/12, 8C8U:6/14, BMOU:6/6, BTOU:6/6, CRPU:4/4, JYEU:3/5

### `lease_term_years` — 991/1591 null (62%)
  MXNU:142/148, A17U:120/223, SET:91/95, BUOU:88/113, HMN:79/103, C2PU:70/74, M44U:61/176, ME8U:55/99, UD1U:49/53, XZL:30/32, D5IU:29/29, ODBU:22/22, DHLU:19/19, J91U:19/71, CMOU:13/13, OXMU:13/13, DCRU:11/11, J85:11/23, AJBU:10/24, N2IU:10/18, K71U:8/15, CY6U:7/13, 8C8U:6/14, BTOU:6/6, T82U:6/12, C38U:5/25, P40U:5/9, O5RU:3/27, JYEU:2/5, Q5T:1/13

### `lease_expiry_date` — 1161/1591 null (73%)
  M44U:176/176, MXNU:148/148, A17U:120/223, ME8U:99/99, SET:91/95, BUOU:88/113, HMN:79/103, C2PU:71/74, UD1U:49/53, XZL:30/32, C38U:24/25, ODBU:21/22, J91U:16/71, 8C8U:14/14, CMOU:13/13, OXMU:13/13, Q5T:13/13, DCRU:11/11, DHLU:11/19, J85:11/23, AJBU:10/24, N2IU:10/18, T82U:10/12, CY6U:8/13, K71U:8/15, BTOU:6/6, P40U:5/9, JYEU:3/5, O5RU:3/27

### `divestment_price` — 1591/1591 null (100%)
  A17U:223/223, M44U:176/176, MXNU:148/148, BUOU:113/113, HMN:103/103, ME8U:99/99, SET:95/95, C2PU:74/74, J91U:71/71, UD1U:53/53, XZL:32/32, AW9U:31/31, D5IU:29/29, O5RU:27/27, C38U:25/25, AJBU:24/24, J85:23/23, ODBU:22/22, DHLU:19/19, M1GU:18/18, N2IU:18/18, AU8U:17/17, K71U:15/15, 8C8U:14/14, CMOU:13/13, CY6U:13/13, OXMU:13/13, Q5T:13/13, T82U:12/12, DCRU:11/11, J69U:11/11, P40U:9/9, BMOU:6/6, BTOU:6/6, TS0U:6/6, JYEU:5/5, CRPU:4/4

### `flags` — 1402/1591 null (88%)
  A17U:222/223, M44U:176/176, MXNU:144/148, BUOU:112/113, HMN:103/103, SET:90/95, ME8U:86/99, C2PU:71/74, J91U:55/71, UD1U:53/53, XZL:31/32, AW9U:27/31, AJBU:24/24, D5IU:23/29, C38U:19/25, DHLU:19/19, M1GU:16/18, O5RU:15/27, ODBU:15/22, N2IU:14/18, AU8U:13/17, CMOU:13/13, OXMU:13/13, J69U:11/11, J85:10/23, BTOU:6/6, CRPU:4/4, 8C8U:3/14, BMOU:3/6, JYEU:3/5, K71U:3/15, P40U:2/9, TS0U:2/6, T82U:1/12

### `original_currency` — 1407/1591 null (88%)
  M44U:176/176, MXNU:148/148, BUOU:113/113, HMN:103/103, ME8U:99/99, A17U:95/223, SET:95/95, C2PU:74/74, J91U:71/71, UD1U:53/53, XZL:32/32, AW9U:31/31, O5RU:27/27, C38U:25/25, AJBU:24/24, J85:23/23, ODBU:22/22, DHLU:19/19, M1GU:18/18, N2IU:18/18, K71U:15/15, 8C8U:14/14, CMOU:13/13, CY6U:13/13, OXMU:13/13, Q5T:13/13, T82U:12/12, DCRU:11/11, J69U:11/11, P40U:9/9, BTOU:6/6, TS0U:6/6, JYEU:5/5

### `original_value` — 1407/1591 null (88%)
  M44U:176/176, MXNU:148/148, BUOU:113/113, HMN:103/103, ME8U:99/99, A17U:95/223, SET:95/95, C2PU:74/74, J91U:71/71, UD1U:53/53, XZL:32/32, AW9U:31/31, O5RU:27/27, C38U:25/25, AJBU:24/24, J85:23/23, ODBU:22/22, DHLU:19/19, M1GU:18/18, N2IU:18/18, K71U:15/15, 8C8U:14/14, CMOU:13/13, CY6U:13/13, OXMU:13/13, Q5T:13/13, T82U:12/12, DCRU:11/11, J69U:11/11, P40U:9/9, BTOU:6/6, TS0U:6/6, JYEU:5/5

### `area_unit` — 660/1591 null (41%)
  M44U:176/176, HMN:103/103, ME8U:99/99, SET:95/95, C2PU:74/74, UD1U:46/53, XZL:32/32, J85:12/23, P40U:8/9, CY6U:4/13, J91U:3/71, K71U:2/15, N2IU:2/18, A17U:1/223, J69U:1/11, JYEU:1/5, T82U:1/12

### `net_property_income_currency` — 1404/1591 null (88%)
  A17U:223/223, M44U:176/176, MXNU:148/148, BUOU:113/113, HMN:103/103, ME8U:99/99, SET:95/95, C2PU:74/74, J91U:71/71, UD1U:53/53, XZL:32/32, AW9U:31/31, O5RU:27/27, C38U:25/25, AJBU:24/24, ODBU:22/22, M1GU:18/18, 8C8U:14/14, OXMU:13/13, Q5T:13/13, DCRU:10/11, TS0U:6/6, T82U:4/12, JYEU:2/5, K71U:2/15, N2IU:2/18, CY6U:1/13, D5IU:1/29, J69U:1/11, J85:1/23


## property_transaction — 95 rows

### `description` — 30/95 null (32%)
  A17U:15/15, J91U:11/11, BTOU:2/2, C2PU:1/1, K71U:1/2

### `carrying_value` — 29/95 null (31%)
  A17U:6/15, HMN:5/7, 8C8U:2/2, BUOU:2/3, K71U:2/2, ODBU:2/3, CY6U:1/2, DCRU:1/1, DHLU:1/1, J69U:1/2, ME8U:1/1, MXNU:1/5, Q5T:1/1, SET:1/6, TS0U:1/2, XZL:1/3

### `gain_on_divestment` — 67/95 null (71%)
  M44U:16/17, A17U:15/15, HMN:5/7, MXNU:5/5, SET:5/6, 8C8U:2/2, BTOU:2/2, BUOU:2/3, K71U:2/2, ODBU:2/3, XZL:2/3, CY6U:1/2, DCRU:1/1, DHLU:1/1, J69U:1/2, ME8U:1/1, O5RU:1/1, Q5T:1/1, T82U:1/1, TS0U:1/2

### `purchase_price` — 72/95 null (76%)
  M44U:17/17, J91U:11/11, A17U:9/15, HMN:5/7, SET:5/6, MXNU:4/5, XZL:3/3, BTOU:2/2, BUOU:2/3, CY6U:2/2, AJBU:1/1, AU8U:1/1, AW9U:1/1, C2PU:1/1, J69U:1/2, N2IU:1/1, O5RU:1/1, ODBU:1/3, P40U:1/1, T82U:1/1, TS0U:1/2, UD1U:1/1

### `valuation` — 28/95 null (29%)
  M44U:7/17, HMN:6/7, 8C8U:2/2, CY6U:2/2, TS0U:2/2, AW9U:1/1, BUOU:1/3, K71U:1/2, O5RU:1/1, ODBU:1/3, P40U:1/1, SET:1/6, UD1U:1/1, XZL:1/3

### `counterparty` — 23/95 null (24%)
  HMN:6/7, M44U:6/17, ODBU:3/3, 8C8U:1/2, CY6U:1/2, ME8U:1/1, O5RU:1/1, P40U:1/1, SET:1/6, TS0U:1/2, UD1U:1/1

### `gross_sale_price` — 34/95 null (36%)
  A17U:6/15, HMN:5/7, 8C8U:2/2, BTOU:2/2, K71U:2/2, M44U:2/17, ODBU:2/3, AJBU:1/1, AU8U:1/1, BUOU:1/3, DCRU:1/1, DHLU:1/1, J69U:1/2, ME8U:1/1, MXNU:1/5, P40U:1/1, Q5T:1/1, SET:1/6, TS0U:1/2, XZL:1/3

### `net_sale_proceeds` — 79/95 null (83%)
  M44U:16/17, A17U:15/15, J91U:11/11, SET:6/6, HMN:5/7, MXNU:5/5, BUOU:3/3, XZL:3/3, 8C8U:2/2, K71U:2/2, ODBU:2/3, CY6U:1/2, DCRU:1/1, DHLU:1/1, J69U:1/2, ME8U:1/1, O5RU:1/1, Q5T:1/1, T82U:1/1, TS0U:1/2

### `interest_pct` — 90/95 null (95%)
  M44U:17/17, A17U:15/15, J91U:11/11, HMN:7/7, SET:6/6, MXNU:5/5, BUOU:3/3, ODBU:3/3, XZL:3/3, 8C8U:2/2, BTOU:2/2, CY6U:2/2, J69U:2/2, AJBU:1/1, AU8U:1/1, AW9U:1/1, C2PU:1/1, DHLU:1/1, ME8U:1/1, N2IU:1/1, O5RU:1/1, P40U:1/1, Q5T:1/1, T82U:1/1, UD1U:1/1

### `purchase_price_currency` — 69/95 null (73%)
  M44U:17/17, J91U:11/11, A17U:9/15, SET:5/6, MXNU:4/5, XZL:3/3, BTOU:2/2, BUOU:2/3, CY6U:2/2, HMN:2/7, AJBU:1/1, AU8U:1/1, AW9U:1/1, C2PU:1/1, J69U:1/2, N2IU:1/1, O5RU:1/1, ODBU:1/3, P40U:1/1, T82U:1/1, TS0U:1/2, UD1U:1/1

### `gross_sale_price_currency` — 29/95 null (31%)
  A17U:6/15, HMN:5/7, 8C8U:2/2, K71U:2/2, M44U:2/17, ODBU:2/3, BUOU:1/3, DCRU:1/1, DHLU:1/1, J69U:1/2, ME8U:1/1, MXNU:1/5, Q5T:1/1, SET:1/6, TS0U:1/2, XZL:1/3

### `net_sale_proceeds_currency` — 79/95 null (83%)
  M44U:16/17, A17U:15/15, J91U:11/11, SET:6/6, HMN:5/7, MXNU:5/5, BUOU:3/3, XZL:3/3, 8C8U:2/2, K71U:2/2, ODBU:2/3, CY6U:1/2, DCRU:1/1, DHLU:1/1, J69U:1/2, ME8U:1/1, O5RU:1/1, Q5T:1/1, T82U:1/1, TS0U:1/2

### `carrying_value_currency` — 31/95 null (33%)
  A17U:6/15, HMN:5/7, 8C8U:2/2, BUOU:2/3, K71U:2/2, M44U:2/17, ODBU:2/3, CY6U:1/2, DCRU:1/1, DHLU:1/1, J69U:1/2, ME8U:1/1, MXNU:1/5, Q5T:1/1, SET:1/6, TS0U:1/2, XZL:1/3

### `gain_currency` — 70/95 null (74%)
  M44U:16/17, A17U:15/15, HMN:5/7, MXNU:5/5, SET:5/6, 8C8U:2/2, BTOU:2/2, BUOU:2/3, K71U:2/2, ODBU:2/3, XZL:2/3, AJBU:1/1, AW9U:1/1, C2PU:1/1, CY6U:1/2, DCRU:1/1, DHLU:1/1, J69U:1/2, ME8U:1/1, O5RU:1/1, Q5T:1/1, T82U:1/1, TS0U:1/2

### `valuation_currency` — 30/95 null (32%)
  M44U:7/17, HMN:6/7, 8C8U:2/2, BTOU:2/2, CY6U:2/2, TS0U:2/2, AW9U:1/1, BUOU:1/3, K71U:1/2, O5RU:1/1, ODBU:1/3, P40U:1/1, SET:1/6, UD1U:1/1, XZL:1/3

### `carrying_value_basis` — 33/95 null (35%)
  A17U:6/15, HMN:5/7, 8C8U:2/2, BUOU:2/3, K71U:2/2, ODBU:2/3, AJBU:1/1, AW9U:1/1, CY6U:1/2, DCRU:1/1, DHLU:1/1, J69U:1/2, M44U:1/17, ME8U:1/1, MXNU:1/5, P40U:1/1, Q5T:1/1, SET:1/6, TS0U:1/2, XZL:1/3

### `gain_on_divestment_basis` — 81/95 null (85%)
  M44U:17/17, A17U:15/15, SET:6/6, HMN:5/7, MXNU:5/5, BUOU:3/3, ODBU:3/3, 8C8U:2/2, BTOU:2/2, CY6U:2/2, J69U:2/2, K71U:2/2, TS0U:2/2, XZL:2/3, AJBU:1/1, AU8U:1/1, AW9U:1/1, C2PU:1/1, DCRU:1/1, DHLU:1/1, ME8U:1/1, N2IU:1/1, O5RU:1/1, P40U:1/1, Q5T:1/1, T82U:1/1, UD1U:1/1

### `net_proceeds_basis` — 92/95 null (97%)
  M44U:17/17, A17U:15/15, J91U:11/11, HMN:7/7, SET:6/6, MXNU:5/5, BUOU:3/3, ODBU:3/3, XZL:3/3, 8C8U:2/2, BTOU:2/2, K71U:2/2, TS0U:2/2, AU8U:1/1, AW9U:1/1, C2PU:1/1, CY6U:1/2, DCRU:1/1, DHLU:1/1, J69U:1/2, ME8U:1/1, N2IU:1/1, O5RU:1/1, P40U:1/1, Q5T:1/1, T82U:1/1, UD1U:1/1


---

## AR-first checklist — ALL TABLES

_`null/total` per AR. Property = ACTIVE rows; lease cols = leasehold-only (freehold excluded). `perf nulls`/`fin` = singleton-table gaps; property_transaction in its own table below. Purely-structural property columns (NPI/npi_pct/trade_mix/gla…) omitted — see by-column report._

### property + performance + financial
| AR | sub-sector | active | nla | gfa | lease_term(LH) | lease_expiry(LH) | ownership | perf nulls | fin emp_bd | verify item |
|---|---|---|---|---|---|---|---|---|---|---|
| 8C8U | Specialized | 14 | 14/14 | · | · | 8/8 | · | adjDI, occ | null |  |
| A17U | Industrial | 223 | 1/223 | 1/223 | · | · | 223/223 | adjDI | null |  |
| AJBU | Data Centre | 24 | · | 12/24 | · | · | · | adjDI | null |  |
| AU8U | Diversified | 17 | 4/17 | · | · | · | · | adjDI | null |  |
| AW9U | Healthcare | 31 | 31/31 | · | · | · | · | adjDI, wadm | null |  |
| BMOU | Retail | 6 | · | · | · | · | · | adjDI | null |  |
| BTOU | Office | 6 | · | 6/6 | · | · | · | adjDI | null |  |
| BUOU | Diversified | 113 | · | 113/113 | · | · | · | adjDI | · |  |
| C2PU | Healthcare | 74 | 74/74 | · | · | 1/4 | · | adjDI | null |  |
| C38U | Diversified | 25 | · | 5/25 | · | 19/20 | · | adjDI | null |  |
| CMOU | Office | 13 | · | 13/13 | · | · | · | adjDI | null |  |
| CRPU | Retail | 4 | · | · | · | · | · | adjDI | null |  |
| CY6U | Diversified | 13 | 13/13 | 4/13 | · | · | · | adjDI, wale, wadm | null |  |
| D5IU | Retail | 29 | · | · | 29/29 | · | · | adjDI | null | ownership recovered R2 (28×100% + Jogja 68.3%) |
| DCRU | Data Centre | 11 | · | 11/11 | · | · | · | adjDI | null |  |
| DHLU | Industrial | 19 | · | 19/19 | 8/8 | · | · | adjDI | null |  |
| HMN | Hospitality | 103 | 103/103 | 103/103 | · | · | · | adjDI, wale | · |  |
| J69U | Retail | 11 | 1/11 | 2/11 | · | · | · | adjDI | null | `nla` column-shift: 7 rows (Causeway Pt→White Sands) vs source p68 |
| J85 | Hospitality | 23 | 21/23 | 13/23 | · | · | · | adjDI, occ | null |  |
| J91U | Industrial | 71 | 3/71 | 3/71 | 3/55 | · | · | adjDI, unitholders | null | 6/8 & 2/4 Changi BP combined row; 21/23 Ubi Rd 1 val 42.5 vs 41.7 |
| JYEU | Diversified | 5 | 2/5 | 4/5 | 1/4 | 2/4 | · | adjDI | · |  |
| K71U | Office | 15 | 2/15 | 15/15 | · | · | · | adjDI | null |  |
| M1GU | Industrial | 18 | 18/18 | · | · | · | · | · | null |  |
| M44U | Industrial | 176 | 176/176 | 176/176 | 3/118 | 118/118 | · | adjDI | null |  |
| ME8U | Diversified | 99 | 26/99 | 82/99 | · | 43/43 | · | adjDI | · | Tempe: source lease 58yr vs stored Freehold — resolve tenure_conflict |
| MXNU | Office | 148 | · | 148/148 | · | 6/6 | · | adjDI | null |  |
| N2IU | Diversified | 18 | 2/18 | 18/18 | 1/9 | 1/9 | · | adjDI | null | MBC I/II NPI & nla COMBINED — confirm split rows null |
| O5RU | Industrial | 27 | · | 27/27 | · | · | · | adjDI | null |  |
| ODBU | Retail | 22 | · | 22/22 | 1/1 | · | · | adjDI | · |  |
| OXMU | Office | 13 | · | 13/13 | · | · | · | adjDI | · |  |
| P40U | Retail | 9 | 3/9 | 8/9 | · | · | · | adjDI | null | David Jones & Plaza area 'GLA' → in gla not nla — confirm |
| Q5T | Hospitality | 13 | 5/13 | · | · | 12/12 | · | adjDI, wale, occ | · |  |
| SET | Diversified | 95 | · | 95/95 | 6/10 | 6/10 | · | adjDI | · |  |
| T82U | Diversified | 12 | 1/12 | 12/12 | 1/7 | 5/7 | · | adjDI, wale, wadm | null |  |
| TS0U | Diversified | 6 | 2/6 | · | · | · | · | adjDI | null |  |
| UD1U | Diversified | 53 | 53/53 | 53/53 | · | · | · | adjDI | null | 'Total Lettable Area' in `gla` — move to `nla`? |
| XZL | Hospitality | 32 | 32/32 | 32/32 | · | · | · | adjDI | null |  |

### property_transaction — deal-level gaps per AR
_`acq no purchase_price` / `div no money-in` (neither gross nor net) / `div no carrying` / `no counterparty`. Only ARs with a gap shown._

| AR | txns | acq no purchase_price | div no money-in | div no carrying | no counterparty |
|---|---|---|---|---|---|
| 8C8U | 2 | · | · | · | 1/2 |
| BUOU | 3 | · | · | 1/3 | · |
| CY6U | 2 | · | · | 1/2 | 1/2 |
| HMN | 7 | 3/7 | · | · | 6/7 |
| M44U | 17 | · | 2/17 | · | 6/17 |
| ME8U | 1 | · | · | · | 1/1 |
| O5RU | 1 | · | · | · | 1/1 |
| ODBU | 3 | · | · | · | 3/3 |
| P40U | 1 | · | · | · | 1/1 |
| SET | 6 | · | · | · | 1/6 |
| TS0U | 2 | · | · | · | 1/2 |
| UD1U | 1 | · | · | · | 1/1 |
| XZL | 3 | · | 1/3 | 1/3 | · |

### Tables with NO >20% actionable nulls
- **profile**, **trade_mix**, **notes** — all columns 0% null.
- **top_tenant** — only `industry` 9% (SET/BTOU/M1GU/P40U; verified: tenant tables have no sector column → sectors live in trade_mix).

### Notes
- `perf nulls`: adjDI = adjusted_distributable_income (method-2 only, drop candidate); wale/wadm/occ = hospitality or verified-undisclosed; distRec/unitholders = 1-2 ARs.
- `fin emp_bd`=null → externally-managed REIT, no trust staff (structural).
- Hand back `AR + table.column + finding` and I'll apply.
