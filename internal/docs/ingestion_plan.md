# S-REIT Ingestion Plan — parsing & extraction for production

> ⚠️ **HISTORICAL — superseded.** Current operational reference: `docs/pipeline_end_to_end.md`
> (assumption-free + discovery-first). This is an earlier planning snapshot; do not treat it as
> current guidance.

> Scope: how ~120 backfill annual reports (~36k pages) and ~39 reports/year (~12k pages)
> get from PDF → validated rows in the `sgx_reit_*` schema (`sgx_reit_schema_v2.md`).
> Grounded in: 22 reports already parsed on LlamaParse agentic tier, 20 of them audited
> section-by-section; plus a June-2026 tooling/pricing survey (sources at bottom).
> Deliberately not over-specified — bake-off results decide the open choices.

---

## 1. What our exploration established (the constraints that shape the design)

1. **Value is concentrated.** The schema consumes ~50–70 pages per report (highlights,
   property profiles, capital management, audited portfolio statement + FS notes, unitholder
   stats). The other ~70% of pages matter only as plain text for the RAG chunk layer.
2. **Section headers are near-standardized.** "Portfolio Statement", "Notes to the Financial
   Statements", "Statement of Total Return", "Capital Management", "Statistics of
   Unitholdings" located every target section across 20 very different trusts — heuristic
   routing is viable and auditable.
3. **Only the premium parse tier is a real cost.** June-2026 reality: classifying every
   backfill page with a cheap batch LLM ≈ $1–11 *total*; the full extraction backfill ≈
   $10–80 *total*. Parsing tier selection is the only lever that matters financially.
4. **Frontier LLMs parse well but hallucinate on dense financial tables** (transposed
   amounts, dropped rows). 2026 consensus = dedicated parser for must-trust tables, LLM for
   the rest — which is exactly the routed design below.
5. **Provenance and validation are non-negotiable** (schema requires source pages; roll-up
   invariants exist and were verified, e.g. CLCT Σ property NPI = reported RMB 1,104.6m).

## 2. Pipeline

```
PDF registry ──► Stage 1: free local pass ──► Stage 2: routed premium parse ──► Stage 3:
(hash, slots)     text + section map           hard pages only                  extraction
                        │                                                          │
                        └──► RAG chunks (free text)              Stage 4: validate & load
```

### Stage 0 — registry (exists)
`download_reports.py` + `_manifest.csv` already standardize naming and slots. Add: content
hash per PDF (idempotency), and persist every parse job ID (LlamaParse re-fetch is free —
this recovered two full reports during exploration).

### Stage 1 — free local pass (every page, $0)
- **Text + page map**: PyMuPDF (note: AGPL — fine for an internal pipeline; pdfplumber/MIT is
  the swap if legal objects). Output: per-page text, TOC, candidate headings.
- **LiteParse** (LlamaIndex's open-sourced parse engine, Rust, local, May 2026) and/or
  **Docling** (Apache 2.0, ~1–3s/page CPU, page+bbox provenance) as the free *structured*
  pass — they handle easy/medium tables and produce the markdown for RAG chunks.
- **Section classification**: keyword/heading heuristics first (deterministic, auditable);
  pages the heuristics can't place go to a cheap batch LLM (Gemini Flash-Lite class,
  ~500 tokens/page). Expected LLM share ~20–30% of pages; backfill cost ≈ **$1–3**.
- Output: a **section map** per report (section_type → page ranges) — itself stored, since
  it doubles as the citation index for the doc-chunk layer.

### Stage 2 — routed premium parse (~40–60 pages/report instead of ~250)
Only pages mapped to hard-table sections (portfolio statement, property profile tables,
debt/lease ladders, segment notes) go to a paid parser. Candidates, pending bake-off (§3):

| Rung | Option | Cost | Why it's on the ladder |
|---|---|---|---|
| Mid | Mistral OCR 3 (batch) | ~$1/1k pages | price disruptor; flat rate incl. tables |
| Mid | Gemini Flash native PDF (batch) | ~$1–4/1k pages | cheapest "good"; needs validation guardrails |
| High | **LlamaParse agentic** (current baseline) | 10 credits/page; **10k free credits/month** | proven on our corpus; steady state (~12k pages/yr) fits inside the monthly free allowance if spread out |
| High | **Reducto** | ~$15–60/1k; ~15k starter credits | strongest financial-table reputation; starter credits ≈ most of our routed backfill |

Not pursuing: Extend.ai ($300/mo floor, no free tier — its human-in-loop review concept is
noted for later, not its pricing); Marker/Datalab self-hosted (revenue-capped weights);
Chunkr managed (company pivoted — self-host only if ever needed).

### Stage 3 — extraction (per-block, structured outputs, batch)
- ~10–12 extractors, one per schema block, each fed **only its mapped section** (5–30 pages
  of markdown) — not the whole document. Pydantic/JSON-schema enforced via native structured
  outputs (mature on all three providers in 2026; guarantees shape, not truth).
- The alias dictionary and basis rules from `feedback_reflection.md` / schema §0 are baked
  into each extractor prompt ("'Term of lease' in a portfolio statement = land lease";
  "record the basis verbatim"; "no page citation → return null, never guess";
  "withheld-for-confidentiality ≠ missing").
- Model routing by block difficulty: cheap tier for regular tables (distributions, debt
  ladders, unitholder stats); stronger tier for portfolio statements and the exotic models
  (Sasseur EMA, CLAS contract types, Manulife covenants). Everything on **batch APIs (50%
  off)** — extraction is inherently async.
- Backfill cost at these volumes: **~$10–80 total** — choose models on accuracy, not price.
- LlamaExtract remains the fallback option (it accepts our existing parse-job IDs), but
  in-house extractors are preferred for prompt control and retry logic.

### Stage 4 — validation & load
- **Invariants** (all verified to exist during exploration): Σ per-property gross revenue ≈
  reported total; Σ segment NPI = consolidated NPI; gross revenue − expense components =
  NPI; distribution periods sum to FY DPU; property valuations vs balance-sheet line.
- **Schema-level enforcement**: a percentage without a `basis`, or a fact without a
  `source_page`, is a rejected row — not a warning.
- Failures → one retry with the validation error in the prompt → small human-review queue
  (at 39 trusts this is genuinely manageable; pilot will size it).
- Load to Postgres `sgx_reit_*`; RAG chunks from Stage-1 text with the section map as
  metadata.

## 3. Bake-off before committing (zero new parsing spend)

We hold an unusual asset: **22 agentic-parsed reports = free ground truth.** Plan:

1. Sample ~30 hard pages (portfolio statements, property profiles across 6+ trusts).
2. Run LiteParse, Docling, Mistral OCR 3, and Reducto (starter credits) on those pages.
3. Score against the agentic baseline: cell-level table fidelity + whether Stage-3
   extractors produce identical validated rows (the only metric that actually matters).
4. Decide the Stage-2 ladder: if a mid-rung passes extraction-equivalence on hard pages,
   the premium rung shrinks further; if not, LlamaParse-agentic-within-free-credits vs
   Reducto is the head-to-head.

Same method sizes Stage 1: run the heuristic section mapper over all 22 parsed reports
today and measure section-detection accuracy before writing any new code.

## 4. Cost picture (order of magnitude; verify pricing before budgeting — see §6)

| Stage | Backfill (~36k pages) | Steady state (~12k pages/yr) |
|---|---|---|
| 1. Local pass + routing LLM | ~$1–3 | <$1 |
| 2. Premium parse (routed ~7–9k pages) | ~$10–150 depending on rung mix | possibly **$0** (inside LlamaParse monthly free credits) |
| 3. Extraction (batch) | ~$10–80 | ~$5–25 |
| 4. Validation/load | compute only | compute only |
| **Total** | **≈ $25–250** | **≈ $5–30/yr** |

Versus the naive approach we started with (agentic on every page): backfill alone would be
~36k pages × 10 credits ≈ $360+ *if credits were purchasable at list* — and in practice it
exhausted free plans four times for 22 documents. The routed design is ~75–80% cheaper at
the parse stage and nearly free at steady state.

## 5. Deliberately undecided (pilot/bake-off resolves these)

- Which mid-rung parser (Mistral vs Gemini-native) and whether the premium rung is
  LlamaParse or Reducto — §3 decides with data.
- Exact extraction model per block — decided by pilot accuracy on CICT/FCT/CLCT, then
  acceptance-tested on Sasseur/CLAS/Manulife.
- Orchestration/infra (queue, scheduling, where it runs) — premature until the pilot's
  shape is known.
- Human-review tooling — start with a spreadsheet/issue queue; only consider platforms
  (e.g. Extend-style HITL) if volume proves it.

## 6. Known risks / verify-first items

- **Pricing figures above come from June-2026 web research (some via search snippets, not
  fetched pages)** — re-verify LlamaParse free-credit terms, Reducto starter credits, and
  Mistral OCR batch pricing on the official pages before budgeting.
- LiteParse is one month old — treat as bake-off candidate, not foundation, until it proves
  itself on our hard pages.
- Licensing: PyMuPDF AGPL (internal use OK, but confirm with policy); MinerU's custom
  Apache-based license unread; Marker weights revenue-capped (excluded).
- LLM-parsed tables (Gemini/Mistral rungs) must never bypass Stage-4 validation — the
  hallucination failure mode is silent and the invariants are the only guard.

---

*Pricing/benchmark sources: LlamaParse pricing & LiteParse announcement (llamaindex.ai),
Reducto pricing/RD-TableBench (reducto.ai), Mistral OCR 3 (mistral.ai), Gemini batch pricing
(ai.google.dev), Anthropic pricing & structured outputs (platform.claude.com), Docling
(LF AI & Data / arXiv 2408.09869), OmniDocBench (CVPR 2025), Applied AI State of PDF Parsing
(2026), Extend pricing (extend.ai), Tensorlake/Datalab/Upstage/Unstructured official pricing
pages.*
