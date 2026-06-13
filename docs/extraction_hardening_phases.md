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

**Status:** `TODO`

**Todos**
- [ ] A small targeted LLM pass over the per-property-card pages that fills the 5–6 fields
- [ ] Merge into the deterministic property records (like the `needs_llm` merge), keyed by name
- [ ] Handle property-name matching between the card pages and the Tier-C rows
- [ ] Test on C38U (cards pp.39–70) vs the agent's values

**Findings**
- `[2026-06-13]` Decision: **LLM lane, not a deterministic cards adapter** — cards are too
  irregular across 40 trusts; a targeted LLM pass is more robust. (User-selected.)

---

## Phase C — Skill quirks hardening (make per-report plan authoring reliable)

**Goal:** fold every sub-sector quirk we've observed into `reit-extract` / `reit-extract-hybrid`
so an agent authoring plans on the fly doesn't re-learn them per report.

**Status:** `TODO` (findings accumulating)

**Todos**
- [ ] Land-tenure variants → enum: Indonesia HGB → Leasehold; US fee simple → Freehold; BOT scheme
- [ ] Combined/dual-expiry properties (one row, two leases) — convention
- [ ] Units: m² vs sq ft (`area_unit`); beds/keys as structural (declare, don't force into gla/nla)
- [ ] Income models: FRI / blended master-lease+variable → `mixed`
- [ ] Multi-currency per-property + disclosed FX rates (income vs valuation rates)
- [ ] Stapled trusts: use the Stapled Group column; BT-held properties in a separate block
- [ ] `locate.py` anchor variants already added (customers / rental-and-other-income / highlights)

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

**Status:** `IN PROGRESS` — cross-family generality of the **properties adapter** evaluated on
4 families (below). Full 6-section end-to-end per report still TODO.

**Todos**
- [x] Cross-family generality of the properties (Tier-C) adapter — 4 families evaluated
- [ ] Full 6-section pipeline on 3 trusts (judge/plan/run/cross-check/LLM lane/merge → gates)
- [ ] Include one **facing-page-split** trust (MLT) to exercise the LLM fallback path
- [ ] Stratified diff hybrid vs pure-LLM; record disagreements (expect dual-basis / pct_basis)
- [ ] Save proven plans to `.claude/skills/reit-extract-hybrid/plans/<family>/`

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

---

## Phase E — 40-report run (the goal)

**Goal:** extract all ~40 FY2025 reports, one agent per AR, hybrid-first with LLM fallback,
tracked and sample-validated.

**Status:** `TODO` (do not start until Phase D passes)

**Todos**
- [ ] One agent per AR (orchestration prompt in `reit-extract-hybrid/REFERENCE.md §4`)
- [ ] Plan library accumulates per family; reuse + re-verify columns per report
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
