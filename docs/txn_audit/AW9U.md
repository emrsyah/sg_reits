# AW9U.SI — First REIT — FY2025 property-transaction audit

FY-end: **2025-12-31**. Rows audited: **1** (divestment). All figures SGD. Share/subsidiary disposal (100% of PT Karya Sentra Sejahtera, the holding company of the property).

## Row 1 — Imperial Aryaduta Hotel & Country Club (IAHCC) (divestment, completed)

Completed 4 Dec 2025 via disposal of **100% of PT Karya Sentra Sejahtera (PT KSS)** by indirect subs *Lovage International P/L* + *IAHCC Investment P/L*, to related parties. Non-core legacy asset previously earmarked for disposal.

| Column | JSON value | Verdict | Source |
|---|---|---|---|
| transaction_type / status | divestment / completed | ✅ correct | "completed the disposal of 100% of issued and paid-up share capital of PT Karya Sentra Sejahtera" (Note 30 p197 line 7595); p11 line 389 |
| completion_date | 2025-12-04 | ✅ correct | "On 4 December 2025, the Group has... completed the disposal..." (p197 line 7595) |
| deal_fy_scope | (current_fy) | ✅ completed inside FY2025 window | p197 (contributed ~11 months to FY2025 results, p11 line 395) |
| **consideration (gross_sale_price)** | **25,908,000 SGD** | ✅ correct — GROSS | Interested Person Transactions table: "Sales consideration for the divestment of 100% issued and paid-up share capital of PT Karya Sentra Sejahtera ... S$25,908,000" (p200 line 7698) |
| **net_proceeds** | **22,440,000 SGD** | ✅ correct — NET (of tax) | "for a total sales consideration (net of tax) of $22,440,000" (p197 line 7595); "Net cash flow on disposal of a subsidiary 22,440" (Note 30 p197 line 7612); cash flow "Proceeds from disposal of a subsidiary, net of cash 22,440" (p133 line 5312) |
| carrying_value_pre | 25,627,000 SGD | ✅ correct — carrying amount of net assets disposed | "Carrying amount of net assets disposed 25,627" (Note 30 p197 line 7606) |
| gain_loss (gain_on_divestment) | -7,535,000 SGD | ✅ correct — printed **loss** | "Loss on disposal of a subsidiary (7,535)" (Statement of Total Return p127 line 5114; Note 30 p197 line 7610; cash flow p133 line 5295) — incl. **S$5,193k realised FX-reserve loss** (p129 line 5187; Note 30 p197 line 7609) |
| valuation | null | ✅ confirmed null — no separate deal valuation in AR | p197 (only prior-year FV S$27,723k @31 Dec 2024, a different basis, p140 line 5462) |
| counterparty | PT Abadi Jaya Sakti and PT Tigamitra Ekamulia (related parties) | ✅ correct | p197 line 7595; IPT p200 line 7698 |

### net < gross verification (assignment focus) — ✅ CONFIRMED CORRECT
- **Gross sales consideration = S$25,908,000** (IPT table, p200 line 7698).
- **Net cash flow on disposal (net of tax) = S$22,440,000** (Note 30 p197 line 7612; cash flow p133 line 5312).
- **22,440 < 25,908 → net < gross is CORRECT.** The bridge is genuinely printed in Note 30: the disposal reconciliation shows withholding tax **S$(1,105)k** (p197 line 7611) plus transaction costs (cash S$130k + Manager's divestment fee in units S$130k, p197 lines 7607–7608) between gross and net cash flow. The round-12 fix (moving the S$22,440k *net* figure out of the gross column and placing gross S$25,908k) is **validated**: previously the net figure was conflated into the gross column.

**Loss composition (as-reported, do not derive):** loss on disposal S$(7,535)k = printed directly; it **includes the S$5,193k realisation of the foreign-currency translation reserve** on disposal (p129 line 5187; p197 line 7609). `carrying_value_pre=25,627k` is the **carrying amount of net assets of the disposed subsidiary** — distinct from the property's 31 Dec 2024 fair value S$27,723k (p140) and from FY2024 property carrying; do not conflate these bases.

## This-FY timeline

| property | type | date | deal_fy_scope | as-reported gain / premium | use-of-proceeds |
|---|---|---|---|---|---|
| Imperial Aryaduta H&CC | divestment (completed) | 2025-12-04 | current_fy | **loss S$(7,535)k** (incl. S$5,193k FX-reserve realisation) | not explicitly earmarked in AR — "non-core legacy asset... previously identified for disposal" (p11 line 389) |

## Corrections proposed
**None.** gross S$25,908k / net S$22,440k / carrying S$25,627k / loss S$(7,535)k all verified against Note 30 (p197) + IPT (p200) + Statement of Total Return (p127). `valuation=null` confirmed. The prior gross↔net conflation is already fixed and is correct.

## As-reported profit-from-divestment (raw material)
- **Loss S$(7,535)k** on disposal of subsidiary (p127/p197). No premium/discount % vs valuation is disclosed for the deal (no independent deal valuation in the AR). Note the loss is largely non-cash: S$5,193k is realised FX-reserve, not a cash loss.

## Use-of-proceeds / DPU linkage
- **No explicit use-of-proceeds statement** for the IAHCC divestment in the AR — described only as disposal of a "non-core legacy asset... previously identified for disposal" (p11 line 389). Classify `use=general`.
- **No divestment-gain distribution** — the deal was a *loss*, and nothing distributes it. `distributed_gain=false`. (Distribution policy p185 line 6837 allows distributing *capital receipts* from preference-share redemptions / shareholder-loan repayments at Manager's discretion — unrelated to this divestment.) FY2025 DPU fell to 2.17¢ (FY2024: 2.36¢), partly because IAHCC only contributed ~11 months and Distributable Amount fell 7.1% (p11 line 395) — i.e. the divestment was mildly **dilutive**, not accretive.

## Suggestions / coverage gaps
- **Share/subsidiary-disposal semantics:** three different "carrying/value" bases appear — net assets of subsidiary disposed (25,627), prior-year property fair value (27,723), and no deal valuation. One `carrying_value` column cannot express this; add a `disposal_basis` (asset vs share) flag.
- **Gross vs net-of-tax proceeds** both printed and materially different (25,908 vs 22,440); the S$1,105k withholding tax + S$260k costs bridge is disclosed — worth a `costs_and_tax` capture.
- **Loss decomposition** (S$5,193k of the S$7,535k loss is realised FX reserve) is disclosed — a `fx_reserve_realised` field would flag largely-non-cash losses.
- **Related-party (IPT) tag** and **Manager's divestment fee (S$130k in units)** disclosed — recoverable.
