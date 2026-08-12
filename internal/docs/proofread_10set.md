# Proofread guide — 10-report working set (FY2025)

Status: **all 10 extracted via the hybrid pipeline, both gates PASS/PASS** (`track.py` 10/10).
Canonical output: `extracted/<SYMBOL>.SI_FY2025/` (8 files each). Pure-LLM baselines for
comparison live in `extracted_llm_baseline/` (C38U, HMN, AJBU, BTOU, AW9U, M44U).

## Matrix

| # | Symbol | Trust | Sub-sector | Props | market_valuation (audited) | Src page | Σ recon |
|---|--------|-------|-----------|------:|----------------------------|----------|---------|
| 1 | C38U | CapitaLand Integrated Commercial | SG diversified | 26 | S$25,992,458k | p109 | EXACT |
| 2 | AJBU | Keppel DC | Data centre | 25 | (prior run) | — | 25/25 |
| 3 | BTOU | Manulife US | US office | 7 | (prior run) | — | 7/7 |
| 4 | AW9U | First REIT | Healthcare | 32 | (prior run) | — | 32/32 |
| 5 | HMN | CapitaLand Ascott | Hospitality (stapled) | 104 | S$7,039,919k (REIT grp) | p127–143 | EXACT |
| 6 | DHLU | Daiwa House Logistics | JP logistics | 19 | S$835,157k | p166 | EXACT |
| 7 | UD1U | IREIT Global | EU office | 53 | EUR 804,280k | p179–181 | EXACT |
| 8 | AU8U | CapitaLand China | China retail | 18 | S$4,204,374k / RMB 22,981,000k | p100–102 | EXACT (both) |
| 9 | J69U | Frasers Centrepoint | SG retail | 12 | S$6,449,000k | p149 | EXACT |
| 10 | M44U | Mapletree Logistics | Multi-ccy logistics | 197 | S$13,156,611k | p130–167 | 0.76% gap* |

\* M44U gap = divested partial-year rows with blank value cells (explained in `_notes`).

## Where the LLM did the work (vs deterministic adapter) — proofread these harder

- **profile / performance** — `llm_only` on every report (scattered front-matter / 5-yr
  summary). Spot-check the headline figures (GR, NPI, DPU, unitholders) against the AR.
- **M44U properties (197)** — `llm_only` (facing-page positional split; engine can't join the
  two tables). Highest transcription-risk section in the set — worth the closest read.
- **HMN properties (104)** — adapter-run but large; check the 20 null-valuation rows (8 AU +
  some FR are "Not applicable" in the audited column; 5 BT PPE hotels are block-total only).
- Everything else (properties/top_tenants/trade_mix/financial on the other 8) ran the
  **deterministic adapter** — lower transcription risk, but still verify a few rows vs source.

## Known warns / structural nulls (expected, already explained in each `_notes.json`)

- **C38U** — 1 warn: gross_revenue near-recon 1.89% (Bugis+/Bukit Panjang Plaza aggregated as
  "Other Assets"; per-property NPI not disclosed by CICT).
- **AU8U** — 2 warns: divested CapitaMall Yuhuating partial-year GR/NPI excluded from active sum.
- **HMN** — 1 warn: `lease_expiry_date` null on 24 leasehold rows (only remaining-term-in-years
  disclosed). trade_mix empty = structural (hospitality).
- **DHLU** — concentration is by **NPI not GRI** (`pct_basis=npi`); SFP IP line (S$984m) ≠
  valuation (S$835m) due to IFRS-16 ROU + ARO — valuation figure is correct.
- **All** — per-property NPI/GR/GLA frequently null where the trust only discloses at
  segment/portfolio level (declared in `_notes.columns_never_fillable`).

## Suggested proofread procedure (per report)

1. Open `extracted/<SYM>.SI_FY2025/_notes.json` first — it lists reconciliation, quirks, and
   every structural null with the reason.
2. Verify `market_valuation` total + source page against the audited Portfolio Statement.
3. Eyeball 3–5 property rows (name, valuation, tenure) vs the source page.
4. Check `performance.json` headline figures (GR, NPI, DPU) vs the AR financial highlights.
5. Flag anything off — note the report + field + expected value.
