# Decision examples — ours vs Excel vs blind re-extraction vs research

One worked example per disputed field, using the three reports we independently re-extracted
(Suntec **T82U** FY2025, Mapletree Logistics **M44U** FY ended Mar-2025, CICT **C38U** FY2025).
All values in **S$'000**.

**The four inputs:**
- **Ours** = raw `sgx_reit_financial` (our extraction).
- **Excel** = colleague's `extract_reit` (currently feeds `sgx_manual_input`).
- **Blind** = a fresh from-scratch extraction we ran on the annual report following the meeting's
  written rules, with no sight of the other two. *Caveat:* for EBITDA/FFO the blind agent used a
  simplified rule we gave it, so for those two it is **not** the standards benchmark — the "Research"
  row is.
- **Research** = the industry-standard definition (NAREIT for FFO; the SG-REIT convention for EBITDA;
  AFFO logic for capex; IAS 7 for cash flow).

Legend: ✅ = matches the standard / AR · ❌ = wrong or off-standard · ⚪ = convention (either OK).

---

## 1. Genuine errors — one number is simply wrong (ours matches the AR)

### `unitholders` — total return attributable to ordinary unitholders (T82U FY2025)
| Ours | Excel | Blind | Research / AR |
|--:|--:|--:|---|
| **159,279** ✅ | 196,631 ❌ | 159,279 ✅ | AR: 177,955 (unitholders + perps) − 18,676 (perps) = **159,279**. Excel *added* the perps instead of subtracting. |
**Decision: use ours.**

### `diluted_shares_outstanding` — weighted-avg units for EPS (M44U FY24/25, '000 units)
| Ours | Excel | Blind | Research / AR |
|--:|--:|--:|---|
| **5,034,448** ✅ | 5,084,902 ❌ | 5,034,448 ✅ | AR EPU note: "diluted = basic, no dilutive instruments" → **5,034,448**. Excel matches no AR line. |
**Decision: use ours.**

### `interest_expense_non_operating` — finance costs (M44U FY24/25)
| Ours | Excel | Blind | Research / standard |
|--:|--:|--:|---|
| **156,893** ✅ | 154,245 ❌ | 156,893 ✅ | Report the **gross** borrowing cost (156,893). Excel netted off interest income (2,648). Gross is the transparent/standard choice. |
**Decision: use ours (gross).**

---

## 2. Calculated metrics — both are "valid" but a standard exists (ours is standards-aligned)

### `ebitda` — earnings before interest, tax, depreciation, amortisation
| Report | Ours | Excel | Blind | Standard says |
|---|--:|--:|--:|---|
| T82U FY2025 | 357,346 | 357,346 | 265,990 | |
| M44U FY24/25 | 498,266 | 428,006 | 589,662 | |
| C38U FY2025 | 1,205,775 | 1,273,892 | 1,005,015 | |

**Standard (SG REITs):** *"earnings before interest, tax, D&A, **excluding fair-value changes of
investment properties & derivatives and FX."*** Ours removes the fair-value swing exactly as required;
Excel is computed inconsistently row-to-row; the blind number used our simplified `NOI + dep` rule so
it's not the benchmark here.
**Decision: standardize on OURS' EBITDA.**

### `funds_from_operation` (FFO) — recurring "real" earnings
| Report | Net income | Ours | Excel | Blind | Standard says |
|---|--:|--:|--:|--:|---|
| C38U FY2025 | 951,424 | **883,865** ✅ | 952,008 ❌ | 952,008 ❌ | FV **gain** year → FFO should be *below* net income |
| M44U FY24/25 | 208,896 | **276,508** ✅ | 208,896 ❌ | 208,896 ❌ | FV **loss** year → FFO should be *above* net income |
| T82U FY2025 | 180,295 | 193,299 | 193,299 | 181,201 | |

**Standard (NAREIT):** *FFO = net income + depreciation − gains on property sales*, adapted for
fair-value-model REITs by **removing the non-cash revaluation**. The entire purpose is to strip paper
revaluation gains/losses. Ours does this (so FFO correctly sits below net income in a gain year, above
in a loss year). Excel/blind add back only P&E depreciation and leave the revaluation in — so their FFO
≈ net income, which defeats the metric.
**Decision: standardize on OURS' FFO.** *(This reverses my earlier "ours looks buggy" comment — ours is the correct one.)*

---

## 3. Scope / convention items — small amounts, pick one rule and apply everywhere

### `capital_expenditure` — cash spent on the property portfolio
| Report | Ours | Excel | Blind | Standard says |
|---|--:|--:|--:|---|
| T82U FY2025 | **21,015** ✅ | 22,093 | 21,015 ✅ | Excel added a P&E (office equipment) purchase 1,078 |
| M44U FY24/25 | **410,522** ✅ | 453,507 | 410,522 ✅ | Excel included broader items |
| C38U FY2025 | 285,040 | 285,659 | 319,040 | blind added a land tender deposit 34,000 |

**Standard (AFFO recurring capex):** property improvements + development; **exclude** buying whole
companies and office P&E. Ours applies this; Excel over-includes; blind's C38U added a land deposit
(arguable).
**Decision: OURS' scope (IP improvements + development only).** *(Also flags A17U FY2025's ~1.9bn capex as a real error — an acquisition leaked in — to fix separately.)*

### `net_property_sales` — gain on selling buildings (C38U FY2025)
| Ours | Excel | Blind | Standard says |
|--:|--:|--:|---|
| 26 | **0** ✅ | 0 ✅ | Only count direct property disposals; a JV-stake sale (26) is not a property sale |
**Decision: match Excel/blind — direct property disposals only. Drop the 26.**

### `net_cash_flow` — change in the cash balance (T82U FY2025)
| Ours | Excel | Blind | Standard says |
|--:|--:|--:|---|
| −35,575 | **−36,808** ✅ | −36,808 ✅ | IAS 7: the "net (decrease) in cash" subtotal is **before** the FX-on-cash line (+1,233). Ours folds FX in. |
**Decision: align ours to the pre-FX subtotal (−36,808).**

### `perpetual_security_holders` / `minorities` — sign (T82U FY2025)
| Ours | Excel | Blind | Note |
|--:|--:|--:|---|
| −18,676 ⚪ | +18,676 ⚪ | −18,676 ⚪ | Same magnitude; ours stores it negative (a deduction), which is Gerald's/prod convention. |
**Decision: keep ours (negative).**

---

## 4. Scoreboard

| Field | Winner | Basis |
|---|---|---|
| unitholders | **Ours** | AR-verified |
| diluted/basic shares | **Ours** | AR-verified |
| interest (gross) | **Ours** | standard/transparent |
| EBITDA | **Ours** | SG-REIT standard (ex-fair-value) |
| FFO | **Ours** | NAREIT standard (removes revaluation) |
| capex scope | **Ours** | AFFO recurring-capex logic |
| net_property_sales | **Excel/blind** | property disposals only → drop our 26 |
| net_cash_flow | **Excel/blind** | IAS 7 pre-FX subtotal → align ours |
| perps/minorities sign | **Ours** | prod convention |

**Bottom line:** on the calculated metrics, ours is the standards-aligned version. Two small
alignments go the other way (net_cash_flow FX, net_property_sales scope), plus one real bug to fix
(A17U FY2025 capex). Blind re-extraction confirms ours on every as-declared and error case.
