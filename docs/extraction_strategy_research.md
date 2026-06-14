# High-accuracy PDF→schema extraction: strategy research (2025/2026)

> ⚠️ **HISTORICAL — superseded.** Current operational reference: `docs/pipeline_end_to_end.md`
> (assumption-free + discovery-first). This is earlier research; do not treat it as current
> guidance.

> Research brief: best strategies/technologies/libraries/models for a high-accuracy
> (~99% field-level) ingestion pipeline over ~40 SGX REIT annual reports (×3 FYs ≈ 120
> PDFs, 80–400 pages, every issuer a different layout) into a fixed relational schema
> (`sgx_reit_schema.md`) with mandatory page-level provenance and numeric reconciliation.
> Deployment lens: hybrid / cost-tiered, **accuracy as a hard constraint, cost minimized
> under it**, scale small so **accuracy ≫ throughput**.
>
> Method: deep-research harness — 24 sources fetched, 116 claims extracted, 25
> adversarially verified (3-vote, need 2/3 to kill), 19 confirmed / 6 killed. Sources
> mostly Nov 2025–Mar 2026. Generated Jun 13 2026.

---

## TL;DR — verdict: **keep & augment, do not replace**

The current stack (PDF → LlamaParse agentic → Claude agent + `reit-extraction` skill +
`check_extraction.py` reconciliation gate) already embodies the SOTA pattern: premium
parse + frontier LLM + schema-guided extraction + reconciliation gate. Nothing in the
2025/2026 literature beats that *shape*. What's missing are three bolt-ons:

1. **Page-level cost-tiered parse routing** (cheap parse by default; escalate only hard
   tables/pages to agentic) — we currently pay agentic on every page.
2. **Per-field confidence scoring → human-in-the-loop routing** of only the low-confidence tail.
3. **A fact-centric eval harness** on a hand-labeled gold set of *our own* pages — the only
   way to actually *prove* 99%.

**99% is a system property, not a model you can buy.** No source demonstrated 99%
field-level accuracy out of the box. It is reachable only as: reconciliation gates +
per-field confidence routing + targeted human review, *measured* with a numeric/monetary
eval (not text similarity).

---

## ⚠️ Claims that were REFUTED under adversarial review

Read these before trusting any vendor benchmark page.

| Refuted claim | Vote | Why it died |
|---|---|---|
| "LlamaParse Agentic is best overall on ParseBench (84.9%), the only method competitive across all 5 dimensions, beating Textract/Azure DI/Google DocAI/Reducto/Docling + VLMs" | **0-3** | Vendor-self-reported; ParseBench is LlamaIndex's *own* benchmark; methodology concerns re selective competitor reporting |
| "LlamaParse Agentic leads complex-table dimension (90.74%)" | **1-2** | Same vendor-bias problem |
| "Two-agent (Extraction + Text-to-SQL) system matches human annotators ~95%" | **0-3** | Overclaim, single preprint |
| "Per-field trust scoring auto-handles 95–99%, humans review only 1–5%" | **0-3** | The routing *mechanism* is real; the automation % is not established |
| "Multi-stage pipeline achieves high accuracy on 200+ page fiscal docs" | **0-3** | Overclaim of the underlying paper's actual result (84% consistency gate) |

**Implication:** do NOT assume LlamaParse dominates. Benchmark it against Reducto / Azure
Document Intelligence / a VLM on *our own* pages before committing.

---

## Confirmed findings (what to build on)

### 1. No parser wins on everything → routing is justified — *high confidence (3-0)*
ParseBench (~2,000 human-verified enterprise pages incl. finance, 14 methods, 5 dimensions):
*"No method is consistently strong across all five dimensions. VLMs tend to excel at
content-level understanding, while specialized parsers tend to excel at structure- and
layout-aware extraction."* Corroborated by OmniDocBench (CVPR 2025, 1,651 pages, 10 doc
types incl. financial/research reports). Component-level table recognition (TEDS):
RapidTable 82.5 > StructEqTable 75.8 > GOT-OCR 74.9 > PaddleOCR 73.6 — **dedicated table
models beat general OCR.** A hybrid is technically (not just economically) correct.
[ParseBench](https://arxiv.org/html/2604.08538v3) · [OmniDocBench](https://github.com/opendatalab/OmniDocBench)

### 2. Cost-tiered parsing is economically grounded — *medium (3-0, vendor caveat)*
LlamaParse Agentic ~1.2¢/page (84.9% overall, self-reported); Cost-Effective <0.4¢/page
("competitive with Gemini at minimal thinking"). Use the **cost/accuracy tiers for routing
reasoning**, not as a verified accuracy guarantee.
[ParseBench blog](https://www.llamaindex.ai/blog/parsebench) · [tiers doc](https://developers.llamaindex.ai/llamaparse/parse/guides/tiers/)

### 3. Schema-guided structured extraction is the right primitive — *high (3-0)*
Constrained decoding against Pydantic/Zod/JSON-Schema. Engines are benchmarkable —
JSONSchemaBench (~10k real schemas) compares Guidance, Outlines, llama.cpp, XGrammar (open)
+ OpenAI, Gemini (commercial) on efficiency/coverage/quality. **LlamaExtract** uses
user-defined Pydantic/Zod schemas with field descriptions, returns validated objects.
[JSONSchemaBench](https://arxiv.org/abs/2501.10868) · [LlamaExtract](https://developers.llamaindex.ai/python/cloud/llamaextract/examples/extract_data_with_citations/)

### 4. Page-level field citations are a built-in capability — *high (3-0)*
LlamaExtract `cite_sources=True` returns `field_metadata` with `citation` (page numbers +
matching text) and `reasoning` (e.g. "VERBATIM EXTRACTION"), demonstrated on an SEC filing.
This *is* our mandatory page-provenance requirement, off the shelf. **Nuance:** citations
attach at leaf sub-field level, not array-item level.
[citations example](https://developers.llamaindex.ai/python/cloud/llamaextract/examples/extract_data_with_citations/) · [options](https://developers.llamaindex.ai/python/cloud/llamaextract/features/options)

### 5. Reconciliation invariants are the highest-leverage technique — *high (3-0)*
"Information Extraction From Fiscal Documents Using LLMs" (Nov 2025): *"totals at each level
of the hierarchy allow robust internal validation."* This is exactly our "Σ per-property
revenue = audited total" gate. They reached 84% numerical-consistency pass rate on 200+ page
PDFs. **We already do this** in `check_extraction.py` — it is the proven thing.
*Caveat:* domain is government budgets; the sum-of-subitems invariant is domain-general and
transfers cleanly, but specific numbers may not.
[fiscal-docs paper](https://arxiv.org/abs/2511.10659)

### 6. The eval MUST be fact-centric, not text-similarity — *high (3-0)* — **most important for 99%**
FinCriticalED (Nov 2025): 859 financial pages, 9,481 expert-annotated facts. *"A clear gap
between lexical accuracy and factual reliability, with numerical values and monetary units
emerging as the most vulnerable... critical errors concentrating in visually complex,
mixed-layout documents."* Concrete: **MinerU2.5 scored 95.71% ROUGE-1 but collapsed to
54.05% on monetary-unit fact accuracy.** A text-similarity eval will *lie* about accuracy.
(Validates the skill's obsession with `$'000`/millions rescaling and `pct_basis`.)
[FinCriticalED](https://arxiv.org/abs/2511.14998)

### 7. Per-field confidence scoring is the right HITL primitive — *high (3-0)*
Cleanlab **CONSTRUCT/TLM** (Mar 2026): model-agnostic 0–1 trust scores per field; works on
black-box APIs **without logprobs** (so it works on Claude); no labeled data; best
per-document AUROC for error detection vs LLM-as-judge / token-logprob scoring.
*(Note: the "automate 95–99%" framing was refuted — use it to rank/route, not to promise an
automation rate.)*
[CONSTRUCT](https://arxiv.org/pdf/2603.18014)

### 8. Run extraction at T=0; bigger ≠ more reliable — *medium (3-0)*
"LLM Output Drift" (Nov 2025): structured (SQL-style) tasks stay stable at low temperature
while RAG-style tasks drift 25–75%; determinism is task- and model-dependent, not
size-monotonic (Granite-3-8B / Qwen2.5-7B hit 100% consistency at T=0; GPT-OSS-120B only
12.5%). → Pin **T=0**; don't assume the biggest model is the most reproducible across annual
refreshes.
[LLM Output Drift](https://arxiv.org/abs/2511.07585)

### 9. Domain rule injection measurably helps — *medium (2-1, single preprint)*
A multi-agent SEC pipeline (Claude-3.7-Sonnet + rule injection) reported F1 91.2% /
precision 95.3% / unit-error 2.3%; ablating the rules dropped precision to 82.6% and raised
unit-error to 12.9%, period-misalignment 3.1%→15.4%. This is literally what the skill's
conventions block does — keep investing there.
[rule-injection/SEC](https://arxiv.org/html/2505.19197v3)

---

## Recommended reference architecture (for this corpus)

```
                    ┌─ Tier-0 triage (cheap): classify each PAGE
PDF ───────────────►│   easy text/simple table  vs  dense financial table / chart
                    └─ split → route
   easy pages ──► cheap parse  (LlamaParse Cost-Effective <0.4¢/pg, or OSS Docling / MinerU)
   hard pages ──► premium parse (LlamaParse Agentic ~1.2¢/pg)
                  └─ BENCHMARK vs Reducto / Azure DI / a VLM on our own pages FIRST
        │
        ▼
   Schema-guided extraction @ T=0
     - Pydantic schema = the 6 sgx_reit_* tables
     - LlamaExtract cite_sources=True  (built-in page citations)  OR
     - Claude/frontier + constrained decoding for agentic-judgment cases
        │
        ▼
   VERIFICATION STACK   ← this is what buys 99%, not the model
     ├─ reconciliation invariants (Σ subitems = audited total)   ← HAVE (check_extraction.py)
     ├─ unit/basis/fact rules (skill conventions block)          ← HAVE
     ├─ per-field trust score (Cleanlab TLM / 2nd-model disagree) ← ADD
     └─ route low-confidence fields → human review               ← ADD
        ▼
   FACT-CENTRIC EVAL on a hand-labeled gold set of OUR pages     ← ADD (proves 99%)
```

**Cost reality:** the per-page parse figures (0.4–1.2¢) are *one component*; no source
quantified true end-to-end cost once retries, critic passes, re-extraction, and human review
are included. At ~120 docs/year, parse cost is rounding error — the real cost is human review
of the low-confidence tail.

---

## Action plan for this repo

1. **Don't rebuild.** The agent + skill + QC gate is aligned with SOTA; the gap is
   verification breadth + proof, not the backbone.
2. **Build a gold eval set first** — hand-label ~5–10 diverse issuers (seed from the
   already-done C38U + the archived old pilot). Score **numeric/monetary field accuracy**,
   not text overlap. Prerequisite to claiming 99% to stakeholders; also reveals the real
   easy-vs-hard page split for routing.
3. **Add per-field confidence routing** (Cleanlab TLM or second-model disagreement) so
   humans only see the uncertain tail. Operationalizes the skill's existing note that
   cheap-model runs lack *judgment*.
4. **Add tiered parse routing** only *after* the eval shows which pages actually need
   agentic parse.
5. **Pin T=0** for extraction reproducibility across annual refreshes.

---

## Open questions (all require our own data to close)

1. How do these parsers/VLMs perform on **SGX REIT** layouts specifically? Every cited
   benchmark used SEC/US/government docs. A gold eval on 5–10 of our diverse issuers is
   required to validate any tool choice and measure the actual easy/hard page split.
2. Realistic **end-to-end cost per document** under tiering, including retries, critic
   passes, re-extraction, and human-review time — unquantified by any source.
3. Which specific frontier model (Claude, GPT-5, Gemini 2.x/3, Qwen2.5-VL) is most accurate
   AND most deterministic at T=0 on *our* table styles — no source ranks current frontier
   models head-to-head on REIT-style tables.
4. Human-review throughput + inter-annotator agreement needed to build the gold set and
   clear the low-confidence tail at ~120 docs/year — is that staffing available?

---

## Caveats (from the harness)

- **Time-sensitivity:** fast-moving field; treat any leaderboard position as perishable.
- **Source quality:** several pivotal numbers are vendor-self-reported (LlamaParse ParseBench
  figures, Cleanlab AUROC) or single non-peer-reviewed preprints (rule-injection F1 91.2%,
  hierarchical-validation 84%) — good for architecture reasoning, NOT as verified accuracy
  guarantees for our corpus.
- **Domain transfer:** strongest reconciliation/rule-injection evidence is from SEC 10-Ks and
  government budgets, not SGX REIT ARs. The sum-of-subitems invariant transfers cleanly;
  specific F1/precision numbers may not.
- **No silver bullet:** several attractive claims (LlamaParse best-overall; per-field scoring
  alone automates 95–99%; two-agent ~95% = human) were adversarially **refuted**.

---

## Sources

**Primary (peer-reviewed / official docs):**
- ParseBench paper — https://arxiv.org/html/2604.08538v3
- OmniDocBench (CVPR 2025) — https://github.com/opendatalab/OmniDocBench
- FinCriticalED (Nov 2025) — https://arxiv.org/abs/2511.14998
- Information Extraction From Fiscal Documents Using LLMs (Nov 2025) — https://arxiv.org/abs/2511.10659
- Cleanlab CONSTRUCT / TLM (Mar 2026) — https://arxiv.org/pdf/2603.18014
- LLM Output Drift (Nov 2025, AI4F @ ICAIF '25) — https://arxiv.org/abs/2511.07585
- JSONSchemaBench — https://arxiv.org/abs/2501.10868
- Multi-agent SEC extraction + rule injection — https://arxiv.org/html/2505.19197v3
- LlamaExtract citations example — https://developers.llamaindex.ai/python/cloud/llamaextract/examples/extract_data_with_citations/
- LlamaExtract options — https://developers.llamaindex.ai/python/cloud/llamaextract/features/options
- LlamaParse tiers — https://developers.llamaindex.ai/llamaparse/parse/guides/tiers/

**Vendor / blog (use with skepticism):**
- LlamaParse ParseBench blog — https://www.llamaindex.ai/blog/parsebench
- LlamaExtract SEC mining — https://www.llamaindex.ai/blog/mining-financial-data-from-sec-filings-with-llamaextract
- Reducto comparison / vs LlamaParse — https://llms.reducto.ai/document-parser-comparison · https://llms.reducto.ai/reducto-vs-llamaparse
- Unstract LLM structured-extraction comparison — https://unstract.com/blog/comparing-approaches-for-using-llms-for-structured-data-extraction-from-pdfs/
- LLM-OCR real cost — https://parsli.co/blog/real-cost-llm-ocr-document-extraction
- applied-ai PDF parsing benchmark — https://www.applied-ai.com/briefings/pdf-parsing-benchmark/
