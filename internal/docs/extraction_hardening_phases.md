# Extraction hardening — phase tracker (A–E)

Living status doc for hardening the hybrid pipeline to be reliable across all ~40 FY2025
annual reports. Pairs with `docs/pipeline_end_to_end.md` (how the pipeline works) — this doc
is **what we're doing, where it stands, and what we found**.

**Status legend:** `TODO` · `IN PROGRESS` · `DONE` · `BLOCKED` · `PICKED UP AGAIN` (re-opened
after review). **Findings** are append-only, each line dated `[YYYY-MM-DD]` with what was learned.

---

## Foundation (already in place before A–E)

- **Parsing → Datalab balanced** (md for reading + HTML for deterministic tables). 6 reports
  parsed: C38U, HMN, AJBU, BTOU, AW9U, M44U.
- **Pure-LLM skill `reit-extract`** validated on **5 archetypes** (C38U, HMN, AJBU, BTOU, AW9U)
  — all pass both gates. This is the fallback for any section the hybrid can't do.
- **Hybrid skill `reit-extract-hybrid`** + engine (`scripts/adapter/`) + two gates
  (`validate_schema.py`, `check_extraction.py`) + tracker (`track.py`).

---

## Known non-agnostic assumptions (risk register)

Things the pipeline currently *assumes* that are validated only on the reports seen so far —
the "families"-class risk (asserted-general, not proven). **L** = fails loudly (a gate catches
it); **S** = fails silently (wrong-but-plausible data — the dangerous kind). Audited 2026-06-13.

| # | Assumption | Where | L/S | Status | Mitigation / next |
|---|---|---|---|---|---|
| R1 | Every trust has ONE audited Portfolio Statement = the valuation source (Tier-C rule) | method / skill | **S** | HOLDS, with care | divergence check: all 3 (IREIT/Daiwa/CLCT) DO have a per-property audited statement, but the **name + location vary** ("Statement of Portfolio" p177 / "Consolidated Portfolio Statement" p98 / inline) and the aggregate (€804.3m) is more prominent than the per-property table — **agent must LOCATE it, never assume a page or grab the aggregate.** |
| R2 | Audited values are at 100% basis (not effective stake) | method / schema | **S** | OPEN | not stressed by the 3 (mostly freehold single-owner); agent captures `value_basis`+`ownership`; no gate can verify — spot-check. |
| R3 | Footnote markers are `<sup>` (name-number disambiguation) | run_adapter | **S** | OPEN | relies on Datalab; watch on new reports. |
| R4 | Datalab balanced parses all 40 adequately (incl. 400-pg / scanned) | parsing | **S** | partly validated | 9 reports now parse clean (incl. IREIT/Daiwa/CLCT); the 404-pg Stoneweg still untested. |
| R5 | Numbers are US/SG format (`,` thousands, `.` decimal) — `num()` does `replace(",","")` | run_adapter | L→S | **RESOLVED** | divergence check: EUR/JPY/RMB SGX reports all use **English numerals** (`44,154` / `60,348` / `10,425`); IREIT 44-property EUR adapter run parsed clean. No code change needed. |
| R5b | Single reporting currency per report | method | **S** | OPEN (new) | CLCT reports dual RMB+S$; Daiwa shows `$'000`; agent must attribute `currency` per record correctly (which currency is `market_valuation` in) — a real per-report judgement, not a format issue. |
| R6 | Sub-sector → which tables exist (playbook) | skill | S/L | partial | judge step verifies vs the actual doc; structural-null declaration. |
| R7 | English + observed-vocabulary anchors / `DEFAULT_HEADER_SKIP` | locate / run_adapter | **L** | ongoing | extend vocab as new wording appears (done: customers / rental-and-other-income / (Years)). |
| R8 | `MONEY_MIN=1e6`, recon tol 1%/5%, `KNOWN_PCT_BASIS`, sub-sector weights, Diversified 0.6/200 | gates / locate | **L** | tuned | warn-not-corrupt; revisit if false-flags appear. |
| R9 | Per-report plan authoring generalises (NOT per-sponsor reuse) | skill | **L** | RESOLVED | reuse assumption dropped 2026-06-13; gates catch a bad fit. |

The gates convert most of these from silent to loud. The standing rule: **validate on divergent
reports, don't assert generality.**

**Divergence check `[2026-06-13]`** — parsed + inspected 3 deliberately-different reports
(IREIT/EUR office, Daiwa/JPY logistics, CLCT/RMB China retail+business-parks):
- **R5 RESOLVED** — all use English numerals despite EUR/JPY/RMB; the `num()` parser is safe.
  Confirmed end-to-end: IREIT 44-property EUR statement extracted clean (sum €761.4m vs €804.3m
  headline = the IFRS-16 right-of-use component, a normal reconciliation note).
- **R1 HOLDS but with care** — each has a per-property audited statement, yet under different
  names/locations and behind a more-prominent aggregate. The skill must emphasise locating it.
- **New R5b** — dual/foreign reporting currency (CLCT RMB+S$, Daiwa $) → per-record currency
  attribution is a real judgement.
- **New tenure** — CLCT "Land Use Right Expiry" with two dates in one cell (China land-use-right
  → Leasehold, dual-expiry) — already covered by §3b conventions.
Net: the scariest silent assumption (number format) is disproven; the engine generalised to a
4th currency/region. Remaining work is agent-judgement (locate the statement, attribute
currency), not silent code failure.

---

## Phase A — Engine generality (does the deterministic engine handle the section shapes?)

**Goal:** prove `run_adapter` extracts the adapterable sections deterministically from Datalab
HTML, and harden it for real-world table variety.

**Status:** `DONE (scoped to 1 AR)` — proven end-to-end on **C38U only**; cross-family
generality is **NOT** proven and is deferred to Phase D.

**Todos**
- [x] Prove `run_adapter` on properties (Tier-C) — C38U
- [x] Prove on top_tenants, trade_mix, financial — C38U
- [x] Harden engine for table variety (multi-page, %, empty-label rows, output naming)
- [ ] Validate across **multiple ARs / sponsor families** end-to-end → **moved to Phase D**
- [ ] Positional-join mode for facing-page-split statements (or keep LLM fallback) → see Findings

**Findings**
- `[2026-06-13]` C38U, all 4 adapterable sections match the pure-LLM agent: properties
  **25/25** (valuation/tenure/term), top_tenants **10/10**, trade_mix **9/9**, financial
  revenue+expense **totals exact** (1,619,174,000 / 429,425,000). All from Datalab HTML.
- `[2026-06-13]` Engine bugs found & fixed (would have hit a 40-run): sections clobbered each
  other's output (`properties_deterministic.json` reused) and HTML files (`portfolio.html`
  reused) → now section-named; trade-mix `%` strings broke the numeric gate → `%`-aware;
  FS-note total rows have a blank label → skip empty col0.
- `[2026-06-13]` HTML substrate confirmed: page lives on the `<table>` `data-block-id`
  (`/page/N/`), `<sup>` footnotes preserved (so "Westgate¹"→"Westgate" but "Junction 8" kept).
- `[2026-06-13]` **Multi-page tables** split into one `<table>` per page → engine now
  concatenates all tables matching `table_contains` (verified on MLT revenue pages).
- `[2026-06-13]` **MLT facing-page positional split discovered** (probe only, no full run):
  description columns and value/revenue columns are in **separate, label-less** tables aligned
  by row position. The single-table engine cannot join them. → Documented a detection rule
  (value table col0 blank for every row) and routed such sections to the **LLM lane**; a
  positional-join engine mode is a future option. Mapletree-family big portfolios are the
  likely population.
- `[2026-06-13]` **Honesty correction:** "engine generality" was validated on ONE AR (C38U)
  fully + ONE AR (MLT) probed. Not yet general across families — that is Phase D.
- `[2026-06-13]` **Cross-family generality run (properties / Tier-C) on 3 more ARs** — see
  Phase D findings. Net: deterministic works on clean-column layouts across 4 families
  (C38U, AJBU, BTOU exact valuation matches); two layout types need the LLM lane (MLT
  facing-page split, First REIT stacked-cell).
- `[2026-06-13]` Engine fixes from that run: `parse_years` now accepts a bare number
  (AJBU term column "60", no "years" word) → lease_term filled; a DEFAULT header/sub-header
  skip drops leaked multi-row-header rows (the "(Years)" artifact on concatenated pages).
  Re-verified C38U (25) and BTOU (7) unchanged after the change.

---

## Phase B — `other_source` LLM lane (the property fields not in the audited table)

**Goal:** fill the property fields that live in irregular per-property cards (occupancy, GLA,
NLA, net_property_income, gross_revenue, major_tenant) which the deterministic Tier-C adapter
leaves null.

**Status:** `DONE (C38U)` — proven on C38U; will re-exercise per report in Phase D/E.

**Todos**
- [x] A small targeted LLM pass over the per-property-card pages that fills the 5–6 fields
- [x] Merge into the deterministic property records (`merge_llm.py --decision other_source`)
- [x] Property-name matching between cards and Tier-C rows (normalised + quoted-abbrev keys)
- [x] Test on C38U (cards pp.39–70) vs the agent's values

**Findings**
- `[2026-06-13]` Decision: **LLM lane, not a deterministic cards adapter** — cards are too
  irregular across 40 trusts; a targeted LLM pass is more robust. (User-selected.)
- `[2026-06-13]` Implemented: one batched Sonnet pass reads the card pages → JSON map;
  `merge_llm.py --decision other_source` fills occupancy/gla/nla/gross_revenue/major_tenant
  by **normalised name**. C38U result vs agent: **occupancy 24/24, NLA 25/25**; fill after
  the lane: occupancy 25/25, nla 25/25, major_tenant 25/25, gross_revenue 23/25
  (Bugis+/Bukit Panjang combined "Other Assets" → null, correct), gla 20/25 (overseas cards
  omit GFA). net_property_income stays null (CICT discloses no per-property NPI — structural).
  No anomalies. Full property record now ~21/24 fields, matching the pure-LLM agent.
- `[2026-06-13]` `merge_llm.py` generalised: `--decision needs_llm|other_source|both` +
  normalised/quoted-abbrev name matching (fixes the audited-full-name vs card-abbrev mismatch).

---

## Phase C — Skill quirks hardening (make per-report plan authoring reliable)

**Goal:** fold every sub-sector quirk we've observed into `reit-extract` / `reit-extract-hybrid`
so an agent authoring plans on the fly doesn't re-learn them per report.

**Status:** `DONE` — quirks folded into `reit-extract/REFERENCE.md` (§3 tenure + §3b
cross-cutting conventions) and the `other_source` lane wired into `reit-extract-hybrid/SKILL.md`.

**Todos**
- [x] Land-tenure variants → enum: HGB → Leasehold; US fee simple → Freehold; BOT; land-use-right
- [x] Combined/dual-expiry properties (one row, two leases) — earlier expiry + both in tenure_raw
- [x] Units: m² vs sq ft; beds/keys/MW as structural (declare, don't force into gla/nla)
- [x] Income models: FRI (base+variable) → `fri`; mixed portfolio → `mixed`
- [x] Multi-currency per-property + two FX rates (avg for income, closing for valuation)
- [x] Stapled trusts: Stapled Group column; BT block separate; PPE assets outside the IP statement
- [x] Cross-section name-form mismatch → match on normalised/quoted-abbrev name
- [x] `locate.py` anchor variants (customers / rental-and-other-income / highlights)

**Findings**
- `[2026-06-13]` Source of the todo list: the First REIT (healthcare) and MLT (industrial)
  pure-LLM runs surfaced these as explicit "SKILL GAPS" — see those agents' reports.
- `[2026-06-13]` `locate.py` hardened: key audited-FS anchors 6/6 across the 6 parses; the
  variable-wording anchors brought to 10/12, remaining 2 are true negatives (HMN no trade mix,
  First REIT no ranked top-10).

---

## Phase D — 3-report end-to-end (certify before scale)

**Goal:** run the FULL 6-section hybrid (deterministic + needs_llm + other_source lane +
llm_only sections) on **3 trusts from 3 different families**, both gates green, diffed vs a
pure-LLM run. **This is where cross-family engine generality actually gets validated.**

**Status:** `DONE` — full 6-section end-to-end on 3 families, both gates PASS on all three,
properties 100% valuation-match vs the pure-LLM baseline. Gate to Phase E is **cleared**.

**Todos**
- [x] Cross-family generality of the properties (Tier-C) adapter — 4 families evaluated
- [x] Full 6-section pipeline on 3 trusts (AJBU, BTOU, AW9U) → both gates PASS each
- [x] Include one fallback trust (AW9U stacked-cell → properties llm_only) — exercised
- [x] Diff hybrid vs pure-LLM (properties valuation: AJBU 25/25, BTOU 7/7, AW9U 32/32)
- [x] Decision: **author a plan per report** (no per-sponsor reuse assumption — layout is not
      guaranteed by sponsor or sub-sector; the engine + judge step + gates are what generalise)
- [ ] One facing-page-split trust (MLT) full run — deferred (MLT has no full pure-LLM baseline)

**Findings**
- `[2026-06-13]` **Properties adapter, cross-family evaluation** (deterministic vs pure-LLM
  agent baseline), 4 families / 3 layout types:

  | AR | Family / sub-sector | Statement layout | Result |
  |---|---|---|---|
  | C38U | CapitaLand / Diversified | clean multi-col, single table | 25/25 valuation, tenure, term |
  | AJBU | Keppel / Data Centre | clean multi-col, **2 pages → concat** | **25/25 valuation**, 25/25 tenure, term 14/25 (rest freehold) |
  | BTOU | Manulife / US Office | clean multi-col, single, **+occupancy** | **6/6 valuation, 6/6 tenure** (7th = held-for-sale Figueroa, value 85,703k correct, name needs cleaning) |
  | MLT | Mapletree / Industrial | **facing-page positional split** (label-less value table) | ✗ deterministic → **LLM lane** |
  | AW9U | First REIT / Healthcare | **stacked-cell, one table per property** (name/loc/tenure/term in one `<br>` cell) | ✗ deterministic → **LLM lane** |

- `[2026-06-13]` **Verdict:** the deterministic engine is reliable on **clean column layouts**
  (single OR multi-page) — exact valuation matches across 3 unrelated families. **Two layout
  families need the LLM lane**: facing-page positional split (Mapletree big portfolios) and
  stacked-cell (First REIT / healthcare-style). The judge step must detect these (label-less
  value table; multi-field single cell) and route properties to `llm_only`.
- `[2026-06-13]` **Cross-source name mismatch** is a real issue: audited statements use full
  legal names (`Guangdong Data Centre 1 ("Guangdong DC 1")`) while marketing/agent use
  abbreviations (`Guangdong DC 1`). Matching/merging across sections needs a name-
  normalization (needs_llm/join) step — don't assume exact-name joins.
- `[2026-06-13]` **3 FULL end-to-end runs (one agent per AR via the skill)** → output to
  the canonical store (now `extracted/<sym>/`; was `extracted_hybrid/` before the
  2026-06-14 folder consolidation), diffed vs the pure-LLM baseline (now
  `extracted_llm_baseline/<sym>/`):

  | AR | Family | properties route | gates | properties valuation match |
  |---|---|---|---|---|
  | AJBU | Keppel / DC | hybrid (adapter + other_source lane) | SCHEMA PASS / GATE PASS | **25/25** |
  | BTOU | Manulife / US office | hybrid (adapter + other_source lane) | SCHEMA PASS / GATE PASS | **7/7** |
  | AW9U | First REIT / healthcare | **llm_only** (stacked-cell fallback) | SCHEMA PASS / GATE PASS | **32/32** |

  File counts match the baseline; warns are the expected divested-in-year reconciliation gaps
  (documented in `_notes`). Hybrid **caught a baseline error** (AW9U `income_model` = `mixed`,
  not `master_lease`). Findings folded into the skill: prefer markdown for small note/tenant/
  mix tables (HTML page-range drift + headerless tables); held-for-sale rows need a
  `context_rule`. **Verdict: Phase D PASSED — cleared for Phase E.**

---

## Phase E — 40-report run (the goal)

**Goal:** extract all ~40 FY2025 reports, one agent per AR, hybrid-first with LLM fallback,
tracked and sample-validated.

**Status:** `TODO` (do not start until Phase D passes)

**Todos**
- [ ] One agent per AR (orchestration prompt in `reit-extract-hybrid/REFERENCE.md §4`)
- [ ] Author a fresh plan per report (no per-sponsor reuse assumption); `plans/examples/` is
      format reference only, always re-verify columns if borrowed
- [ ] `track.py` monitors; every AR must hit both gates green
- [ ] Stratified accuracy audit (one per sub-sector) hybrid vs pure-LLM before trusting the batch
- [ ] FY2023/24 backfill (later, for 3-year trends)

**Findings**
- _(none yet)_

---

## How to update this doc

When you work a phase: flip its **Status**, tick **Todos**, and append a dated **Findings**
line for anything learned (a gap, a fix, a measured result, a decision). If a phase is
re-opened after review, set Status `PICKED UP AGAIN` and log why + when.
