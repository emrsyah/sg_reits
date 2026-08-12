# §B Value-Level Verification — Results (2026-07-08)

11 non-frozen REITs verified against parsed ARs (read-only explore agents). The loader currency-label
fix was already applied; this pass checked whether the stored **values/basis** are right as-disclosed.

**Outcome: no value-level data is wrong.** 9 PASS, 2 DISCUSS (both resolve to no-DB-change here).

| REIT | Verdict | Evidence | Result |
|---|---|---|---|
| AU8U | PASS | p28 valuation table (RMB + S$ cols) | 18/18 match; Yuhuating null correct (divested 31 Oct 2025). |
| BMOU | PASS | p131 Portfolio Statement (RMB'000 + S$'000) | 6/6 match; "two bases" = same valuation in RMB vs SGD. Beijing Wanliu 130% is NCI math, not error. |
| D5IU | PASS | p24 Portfolio Summary (Rp'bn + S$'m) | 29/29 match; consistent ~13,068 IDR/SGD. |
| CRPU | PASS | p159 Statement of Portfolio; p160 "$ = SGD" | 4/4 match. **emirsyah's "on USD" note is wrong — it's SGD.** |
| M1GU | PASS | p127 "presented in Singapore dollars" | Single-ccy SGD; bare "$" = SGD; 17/17 match. |
| BTOU | DISCUSS→no-fix | property pages p30-36 Acquisition Date | Acq date already == `purchase_date` (7/7 exact). Do NOT copy to `effective_date` (diff semantics) — leave null. |
| AW9U | PASS | p43 card fn(1) + p171 policy + Note 16 | "Rental Income" = **gross_revenue** (revenue line, not NPI). DB placement correct (GR filled, NPI null). |
| HMN | PASS | Portfolio Stmt pp127-135 ($'000 = SGD); Key-Market tables pp31-52 | SGD presentation; per-asset GR in local ccy (12 currencies) all correct. |
| J91U | PASS | Portfolio Statistics pp79-85 (A$m / JPY m / S$m headers) | 20 gr_ccy mismatches all legitimate (AUD×18, JPY×2). |
| CY6U | PASS | p25/26 INR-million GR/NPI tables (+ "% contribution to NPI" col) | GR/NPI in INR vs SGD valuation = correct. **`npi_pct` is DISCLOSED (p26), all match → staged npi_pct-null is unwarranted; NOT applied.** |
| 8C8U | DISCUSS | p15-16 local-ccy table; p56 Portfolio Stmt (S$'000) | See below. |

## Resolved held item
- **CY6U `npi_pct → None` (staged edit): CLOSED — not applied.** `npi_pct` is the AR-disclosed
  "% contribution to Net Property Income" (p26), all values verified, sums to 100%, none spurious.

## 8C8U — routed to systematic `original_*` coverage
- **Factual correction:** emirsyah's "#14 is SGD" is wrong. **#14 = Dwell East End Adelaide = AUD**
  (A$63,250'000). The genuinely SGD-basis assets are the **5 Westlite** (Toh Guan, Mandai, Woodlands,
  Juniper, Ubi). Breakdown: 5 SGD + 8 GBP (UK Dwell) + 1 AUD (#14).
- `currency=SGD` is correct for all 14 (matches p56 S$'000). **Gap:** the 9 foreign rows have NULL
  `original_value`/`original_currency`; the local figures ARE disclosed on p15-16 (GBP×8, AUD×1).
  Backfilling them satisfies emirsyah's global "original_* coverage" invariant (AJBU note). **Deferred
  to the systematic `original_*` coverage pass (§C)** rather than a one-off, so all REITs are treated
  uniformly. Local values (in '000, ×1000 for absolute):
  Dwell MSV 106,490 GBP · MSV South 47,260 · The Grafton 14,760 · Weston Court 8,150 · Princess St
  23,400 · Cathedral Campus 20,120 · Archer House 12,350 · Hotwells House 17,380 · East End Adelaide
  63,250 **AUD**.

## Out-of-scope provenance nits (no value impact — flagged for later)
`source_page` on several rows points at the financial-statement Note table rather than the
operational/portfolio-summary page that carries the same figure: D5IU (Note-15 vs p24), AW9U
(Ishiyama/Tsukisamu tagged p141 vs p28-43), J91U (pp147-151 vs Portfolio Statistics pp79-85),
8C8U (p56 vs p15-16 for the local originals). Figures identical; only provenance precision.
