# Adversarial verification — seven open items

Adversarial pass against the parsed ARs in `parsed_reports_datalab/<FOLDER>/full.md`.
All line numbers refer to those `full.md` files.

---

## 1. M1GU / FY2024 — the 1,171,000 "reconciles on no basis"

**VERDICT: REFUTED.** It reconciles exactly, to within a 4k rounding residue. The gap is an artefact of pairing the *wrong retention* with the *wrong income line*.

File: `03_M1GU.SI_Alpha-Integrated-REIT_FY2024/full.md` (Sabana Industrial REIT, YE 31 Dec 2024)

Distribution Statement, L4949–4966:

```
4949 | Amount available for distribution to Unitholders at beginning of the year | 15,539 | 16,128 |
4950 | Amount retained for working capital | (3,994)^(1) | – |
4951 | ...at beginning of the year after retention | 11,545 | 16,128 |
4963 | Income available for distribution to Unitholders for the year before tax | 35,584 | 33,714 |
4964 | Tax expense | (584) | (556) |
4965 | Income available for distribution to Unitholders for the year after tax | 35,000 | 33,158 |
4966 | Total amount available for distribution to Unitholders for the year | 46,545 | 49,286 |
```

L4987–4990:
```
4987 | Amount available for distribution to Unitholders at end of the year | 18,683 | 15,539 |
4988 | Amount retained for working capital ^(2) | 3,403 | 3,271 |
4989 | Number of Units entitled to distributions ('000) (Note 11) | 1,125,055 | 1,111,788 |
4990 | Distribution per Unit (cents) | 2.86 | 2.76 |
```

Footnotes:
- L4968 (the 3,994): *"An amount of approximately $2,715,000, after tax deductions, has been retained for working capital and pertains to distributions for the period from 1 July 2023 to 31 December 2023. Additionally, approximately $1,279,000, after tax deductions, is retained ... 1 January 2024 to 30 June 2024."*
- L4994 (the 3,403): *"An amount of approximately $3,403,000 (2023: $3,271,000), **before tax deductions**, has been retained for working capital and pertains to distributions for the period from **1 January 2024 to 31 December 2024**."*

### Is `income_for_year = 35,000,000` the right line?
**Yes.** It is not a suspicious round number — it is 35,584 − 584 (tax) = exactly 35,000 (L4963–4965). Coincidence, verified arithmetically.

### What the 1,171,000 actually is
Two independent basis mismatches:

1. **Wrong retention.** 3,994 is the retention struck out of the **opening** balance (2,715 for 2H2023 + 1,279 for 1H2024, both *after tax*). The retention that belongs to FY2024 income is **3,403** (L4988/L4994, *before tax*, "pertains to ... 1 January 2024 to 31 December 2024"). Difference: 3,994 − 3,403 = **591**.
2. **Wrong income basis.** The 3,403 is stated *before* tax, so it must be netted against the *before-tax* income 35,584, not 35,000. Difference: **584** (the tax expense, L4964).

Reconciliation:
```
35,584 (before tax)  − 3,403 (FY2024 retention, before tax) = 32,181
declared per AR                                             = 32,177   (residue 4, rounding)
gate as run: 35,000 − 3,994                                 = 31,006
32,177 − 31,006 = 1,171  =  584 (tax) + 591 (retention-basis) − 4 (rounding)
```

Independent check that 32,177 is real and not the residual of anything: 1,125,055k units × 2.86 c = **32,176.6k → 32,177** (L4989–4990). So `distribution_declared` is DPU × units-entitled, and the AR's narrative agrees — L842: *"Total distribution amount declared to Unitholders increased by 5.4% y-o-y to $32.2 million, **after approximately 10% of the total income available for distribution was retained** for prudent capital management ... in connection with the internalisation."* (see also L4458, L818: `Total distribution amount declared to Unitholders | 32,177`).

**Action:** the gate `declared = income − retained` is fine, but for M1GU it must use `income_before_tax (35,584)` and `retention_for_the_year (3,403)`. Recording `amount_retained = 3,994` mislabels an opening-balance appropriation as a current-year retention. That is a data bug, not an unexplained AR gap.

---

## 2. ME8U (Mapletree Industrial Trust) — "residue stays in the pool with no named retention"

**VERDICT: REFUTED** (on two counts), with one narrow reading of the claim surviving.

Folder labels run one year behind: `FY2022` = YE 31 Mar 2024, `FY2023` = YE 31 Mar 2025, `FY2024` = YE 31 Mar 2026.

### (a) There *is* a named retention — it is a named audited balance
Audited Distribution Statements roll the pool forward explicitly:

- `27_..._FY2022/full.md` L6874 header (YE 31 Mar 2024); L6881 opening `95,141`; L6885 `375,069`; L6886 `Distribution of gains from divestment 5,391`; L6897 `(374,273)`; L6898 closing `101,328`
- `27_..._FY2023/full.md` L7214 header (YE 31 Mar 2025); L7221 opening `101,328`; L7225 `388,110`; L7226 divestment-gain top-up `13,354`; L7237 `(385,455)`; L7238 closing `117,337`
- `27_..._FY2024/full.md` L6476 `## DISTRIBUTION STATEMENTS`, L6478 `For the financial year ended 31 March 2026`; L6483 opening `117,337`; L6487 `Amount available for distribution 363,881`; L6498 `Total Unitholders' distribution (including capital distribution) (Note B) (370,206)`; L6499 closing `111,012`

Pool: **95,141 → 101,328 → 117,337 → 111,012**, and it ties exactly (117,337 + 363,881 − 370,206 = 111,012).

Narrow reading that survives: there is **no purposed** retention line (nothing labelled "retained for working capital / capex / general corporate purposes"). "Retained" appears nowhere in a distribution context in any of the three files. If the claim meant "no *purposed* retention", it holds; if it meant "no named retention at all", it is wrong.

### (b) Perpetual securities exist but are NOT the explanation
S$300m 3.15% perpetuals issued 11 May 2021 (`FY2023/full.md` L9709–9723, note 27(b); carried 301,802/301,828 at L7203). Perp distributions are deducted **above** the Unitholder line, so they cannot account for the residue:
- `FY2023/full.md` L5100–5102: `Amount available for distribution 384,545 | 397,560` → `- to perpetual securities holders 9,476 | 9,450` → `- to Unitholders 375,069 | 388,110`
- `FY2024/full.md` L1444–1446: `397,560 | 374,079` → `- to Unitholders 388,110 | 363,881` → `- to perpetual securities holders 9,450 | 10,198`

No NCI distribution line appears in the Distribution Statements (NCI appears only in the equity statement, `FY2024/full.md` L6626). No JV adjustment line.

### (c) The `distribution_declared` figures are on a DIFFERENT basis from the audited statement — this is the more important finding

| Declared FY | Financial Review "Distribution to Unitholders" (what was recorded) | Audited "Total Unitholders' distribution" |
|---|---|---|
| FY23/24 | 378,281 (`FY2023` L5103) | 374,273 (`FY2022` L6897) |
| FY24/25 | 385,979 (`FY2023` L5103; `FY2024` L1447) | 385,455 (`FY2023` L7237) |
| FY25/26 | 362,609 (`FY2024` L1447) | 370,206 (`FY2024` L6498) |

The audited statement is on a **recognised/paid-during-the-year** basis and lags one quarter — FY25/26's four component lines (L6490–6497) run `01 Jan 2025–31 Mar 2025` through `01 Oct 2025–31 Dec 2025`. The Financial Review row is the **declared-for-the-year** (Apr–Mar) amount. Differences: 4,008 / 524 / (7,597).

**Consequence:** the residues 2,179 / 15,485 / 1,272 are declared-basis minus earned, so they do **not** tie to the audited pool movement. E.g. FY24/25 the pool actually rose 101,328 → 117,337 = +16,009 = 388,110 + 13,354 − 385,455. Taking the Financial Review row is defensible for a "declared for the year" field, but it must be flagged as declared-basis and never reconciled against the audited rollforward.

---

## 3. 8C8U (Centurion Accommodation REIT) / FY2025 — the 42,000 gap

**VERDICT: REFUTED** — the earlier agent's rounding explanation is substantially right; the test that "failed" applied the rounding at the wrong level.

File: `11_8C8U.SI_Centurion-Accommodation-REIT_FY2025/full.md`

The gap is disclosed as an explicit line pair, L1791–1794:
```
1791 | Amount available for distribution to Unitholders | 29,995 | 28,079 | 6.8 |
1792 | Amount to be distributed to Unitholders          | 29,953 | 28,079 | 6.7 |
1793 | Units in issue and to be issued (Actual) | 1,722,435,558 | 1,722,542,192 |
1794 | Distribution per Unit (S cents) | 1.739 | 1.630 | 6.7 |
```
1,722,435,558 × 1.739c = **29,953,154 → 29,953**. So DPU is struck on the *to be distributed* figure, and the 42 is the round-down residue, confirming the direction of travel.

The mechanism is stated verbatim at **L3060**:
> *"CAREIT's distribution policy is to distribute 100.0% of CAREIT's Annual Distributable Income (as defined in the Trust Deed) ... **after rounding down the distribution per Unit of each distribution type to the nearest three decimal places**."*

Note *"each distribution type"*. Applied to the aggregate, 29,995/1,722,435,558 = 1.7414294c → round down 1.741 → 29,987.6, residue only 8. The AR prints 1.739, i.e. 0.002438c below the aggregate figure — that requires round-down applied **separately to ≥3 distribution types** (Singapore taxable income, tax-exempt income, capital/other-gains), each losing up to 0.001c. 3 × 0.001 = 0.003 ≥ 0.002438. Consistent.

**Set-aside / reserve check: none exists.** The audited Distribution Statement (L3491–3510) stops at `Amount available for distribution to Unitholders 29,995` (L3501) with the opening and closing pool lines blank (L3497, L3502) — first period, constituted 12 Aug 2025 (L3493). There is no retention, reserve or set-aside line anywhere. 29,953 appears *only* in the Financial Review and the highlights page (L143), never in the audited statements.

**Residual uncertainty:** the AR does not disclose the per-distribution-type split, so the exact 42 cannot be re-derived line-by-line from the AR alone (that breakdown lives in the SGX results announcement of 23 Feb 2026, referenced at L2116). Verdict is REFUTED on mechanism, UNRESOLVED on the exact arithmetic split.

---

## 4. J91U (ESR-LOGOS REIT) / FY2025 — "two different cash figures", 167,921 vs 168,003

**VERDICT: REFUTED — the premise is wrong. Neither number is a cash figure.**

File: `15_J91U.SI_ESR-LOGOS-REIT_FY2025/full.md`

Actual cash, Note 11 (L7108–7117):
```
7113 | Cash and bank balances in the statement of financial position | 60,289 | 83,945 | 8,189 | 8,834 |
7114 | Less: Restricted cash | (14,361) | (13,731) |
7115 | Cash and cash equivalents in the statement of cash flows | 45,928 | 70,214 |
7117 The restricted cash pertains to cash reserves of certain entities which is required to be maintained based on agreements with the banks...
```
L5961 (SoCF): `Cash and cash equivalents at 31 December (Note 11) | 45,928 | 70,214`.

Where the two disputed numbers actually live:
- **167,921** = distributions to Unitholders — L5183 `Total distributions to Unitholders during the financial year | 167,921 | 177,424` and L5951 (financing cash flows) `Distributions paid to Unitholders | (167,921) | (177,424)`.
- **168,003** = L5221 `Net decrease in Unitholders' funds resulting from Unitholders' transactions | (168,003) | (71,130)` — an equity-movement subtotal in the Statement of Movements in Unitholders' Funds.

The 82 is therefore **not** a cash reconciling item; it is the net of the *non-distribution* unitholder transactions:
```
Management fees paid in Units  (L5215)   +15,231
Unit buy-back                  (L5217)   (13,615)
Equity issue costs                        (1,665) + (33)
                                          -------
                                            (82)
(82) + (167,921) = (168,003)
```
and the funds statement ties: 2,213,895 + 5,602 + 4,146 − 168,003 = 2,055,640 (L5211–5213, L5222). The 2024 column ties identically to (71,130).

**Caveat on the parse:** in the Datalab markdown the row labels around L5217–5221 are shifted by one row relative to their values (L5219 reads `- Unit buy-back | (167,921)`), which is almost certainly what created the "two cash figures" impression. Treat that table's labels as unreliable and re-derive from the arithmetic above.

**Correct usage:** 167,921 for distributions/DPU and financing cash flow; 168,003 is an equity subtotal only and must never be loaded as a distribution or cash field; 45,928 is cash and cash equivalents (SoCF), 60,289 is balance-sheet cash and bank balances.

---

## 5. D5IU (Landmark REIT, ex-Lippo Malls Indonesia Retail Trust) / FY2025 — 16,702,077,655 vs 7,696,809,979

**VERDICT: CONFIRMED — post-year-end issuance, and it ties to the unit exactly.**

File: `25_D5IU.SI_Landmark-REIT_FY2025/full.md` (YE 31 Dec 2025)

```
4098 (Note 22, Units in issue) | At beginning and end of year | 7,696,809,979 | 7,696,809,979 |
```
Zero movement during FY2025.

Note 35, Events after the reporting year (header L4800 `Year ended 31 December 2025`), L4802–4804:
> `#### Rights Issues`
> *"Pursuant to the results of the renounceable and non-underwritten rights issue announced on 21 January 2026, the Trust has on **26 January 2026** raised up to approximately S$63.0 million through the issue of up to **9,005,267,676 new units** at an issue price of **S$0.007 per unit**."*

Basis: L423 — *"on the basis of 117 rights units for every 100 existing units"*, proceeds primarily to repay loans (repeated in MD&A at L2359).

```
7,696,809,979 + 9,005,267,676 = 16,702,077,655   ← exact, no residual
```

Register date is after the allotment: L5006–5008 `# STATISTICS OF UNITHOLDINGS` / `As at 16 March 2026`; L5019 `| TOTAL | 9,007 | 100.00 | 16,702,077,655 | 100.00 |`. L5002 confirms the audited figure: *"the issued and subscribed units as at 31 December 2025 is an aggregate of 7,696,809,979 units."*

Also noted: name change Lippo Malls Indonesia Retail Trust → Landmark REIT effective 27 March 2026 (L4812).

---

## 6. K71U (Keppel REIT) / FY2025 — 4,955,086,896 vs 4,013,867,000, and the 1.63c stub

**VERDICT: CONFIRMED (post-year-end issuance), with one scale trap to flag.**

File: `23_K71U.SI_Keppel-REIT_FY2025/full.md`

### Scale trap
L5989: `| Units in issue ('000) | 17 | 4,013,867 | 3,844,046 | 4,013,867 | 3,844,046 |` — Note 17 is in **thousands**. Anyone comparing the raw "4,013,867" against 4.955bn sees a false 1000× gap. The 4,013,867,000 used in the extract is the correctly rescaled figure.

### The residual 941,219,896 units
- L8434 (events after the reporting date): *"On **19 January 2026**, the Manager announced the issuance of **923,189,327 new Units, pursuant to the Preferential Offering**. On 20 January 2026, the gross proceeds received from the Preferential Offering amounting to $886,262,000 were used to repay the equity bridge loans..."*
- Remainder ≈ 18,030,569 units = ordinary manager-fee unit issuances between 19 Jan and the register date. L7550: *"During the current financial year, 54,866,902 (2024: 61,492,415) Units were issued at unit prices ranging from $0.8507 to $0.9981 ... as payment of management fees to the Manager."*
- Register: L9928/L9934 `As at 27 February 2026` / `4,955,086,896 Units (Voting rights: 1 vote per Unit)`.
- In-year movement, L7542–7544 (thousands): `– Issuance of units in connection with a private placement | 114,954` → `At 31 December 2025 | 4,013,867`.

### Why the stub stops at 16 October 2025 — YES, a corporate action
L1348:
> *"2H 2025 DPU was 2.51 cents, comprising an **advanced distribution of 1.63 cents for the period from 1 July to 16 October 2025, pursuant to the Private Placement launched in conjunction with the acquisition of Top Ryde City Shopping Centre**, and DPU of 0.88 cents for the period from 17 October to 31 December 2025."*

L6481 (Note C): *"114,954,000 (2024: nil) Units were issued on **17 October 2025** pursuant to the private placement launched..."* — the cut-off is exactly the day before the placement units were issued, so new units do not dilute pre-placement holders' accrued entitlement. Standard advanced/clean-up distribution mechanics.

Supporting: L505 *"we raised $113 million through a Private Placement in October 2025"*; L674 *"Announcement dated 8 October 2025 on 'Launch of Private Placement to Raise Gross Proceeds of No Less Than Approximately S$113.0 million'"*; L3606/L3610 `Advanced Distribution to Unitholders | 25 November 2025` with `Distribution for the period from 1 July 2025 to 16 October 2025`; L6083 `Distribution of 1.63 cents per Unit for the period from 1/7/2025 to 16/10/2025 | (63,411) | –`.

L3691 adds an overlay worth capturing: *"DPU calculated is inclusive of the new Units issued on 19 January 2026 pursuant to the Preferential Offering. These new Units have the right to the distributable income from 17 October 2025 to 31 December 2025."*

FY2025's three tranches: 1H 2025 (paid 15 Sep 2025); advanced stub 1 Jul–16 Oct 2025 @ 1.63c (paid 25 Nov 2025); 17 Oct–31 Dec 2025 @ 0.88c (paid 25 Mar 2026).

---

## 7. Q5T (Far East Hospitality Trust) / FY2025 — 0.47c stub ending 19 August 2025

**VERDICT: CONFIRMED that it is a corporate action — but NOT a privatisation or a placement. It is an earn-out unit issuance.**

File: `16_Q5T.SI_Far-East-Hospitality-Trust_FY2025/full.md`

The stub itself, L5393: `| Distribution of 0.47 cents per Stapled Security for the period from 1 July 2025 to 19 August 2025 | (9,511) | – |`

Cause — new Stapled Securities issued **20 August 2025**:
- L5650 (SoCF, significant non-cash transactions): *"On **20 August 2025, 25,746,652 Stapled Securities amounting to $15,000,000 was issued to Far East SOHO Pte. Ltd. for the Earn-out Amount in relation to the acquisition of Oasia Hotel Downtown** as the Earn-out Event Condition has been met as disclosed in Note 11."*
- L6591 (units-in-issue note, fuller): *"...as the Earn-out Event Condition whereby the net property income of the property of at least $9.9 million per annum for both 2023 and 2024 was met."*
- L6580: `| Earn-out Amount for acquisition of investment property | 25,747 | 25,747 | 25,747 | - | - | - |`

The clock restarts on 20 August, confirming the advanced/clean-up structure — L7614 (Note 27, Subsequent Events): *"On 12 February 2026, the REIT Manager declared a distribution of $29,771,000 or $0.0145 per Stapled Security to Stapled Securityholders in respect of the period from **20 August 2025 to 31 December 2025**."*

No scheme, privatisation, delisting, placement or preferential offering — none of those terms appear in the report. The three FY2025-period distributions are 1.78c (1H), 0.47c (stub), 1.45c (20 Aug–31 Dec, declared post-year-end).

---

## Cross-cutting takeaways

1. **M1GU and ME8U are data bugs, not AR mysteries.** M1GU pairs an opening-balance retention with an after-tax income line; ME8U takes a declared-basis Financial Review row and reconciles it against a paid-basis audited statement. Both need a basis flag on the field.
2. **J91U item 4 was a parse artefact** — shifted row labels in the Datalab markdown produced a phantom "two cash figures" problem. Worth checking other trusts' Statement of Movements tables for the same shift.
3. **Register vs audited unit counts (D5IU, K71U, Q5T, and the K71U stub) are all the same phenomenon**: the Statistics of Unitholdings page is dated 6–10 weeks after year end and includes post-year-end issuances. A generic rule — never reconcile the register against the Note — plus a `('000)` scale check on unit-count notes, would have caught 5, 6 and the K71U false gap automatically.
