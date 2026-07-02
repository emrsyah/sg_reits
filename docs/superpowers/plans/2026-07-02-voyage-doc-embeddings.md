# Voyage Doc Embeddings Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Store page-aware Voyage embeddings for `parsed_reports_datalab/*/full.md` in Supabase pgvector.

**Architecture:** Add one idempotent pgvector table for report chunks. Build chunks locally from markdown page anchors, upsert chunk metadata/text by stable hash, then fill missing embeddings in resumable batches.

**Tech Stack:** Python, psycopg2, voyageai, Supabase Postgres, pgvector, Datalab markdown.

---

### Task 1: Schema

**Files:**
- Modify: `db/schema.sql`

- [ ] Add `vector` extension guard.
- [ ] Add `sgx_reit_doc_chunk` with source metadata, chunk text, token count, hash, model, dimension, and `vector(1024)` embedding.
- [ ] Add indexes for report/page lookups and vector search.
- [ ] Add read RLS policy with the existing data tables.

### Task 2: Chunk Builder

**Files:**
- Create: `scripts/db/build_doc_chunks.py`

- [ ] Parse each `parsed_reports_datalab/<report>/full.md`.
- [ ] Split on `<!-- PAGE N -->`.
- [ ] Track `symbol`, `financial_year`, `report_dir`, source path, page, heading path, character offsets.
- [ ] Chunk page-local text at about 1,200 Voyage tokens with 180-token overlap.
- [ ] Avoid splitting inside markdown tables where practical; repeat heading context in stored `chunk_text`.
- [ ] Upsert rows by `chunk_hash`; support `--dry-run`, `--report`, `--reset-report`.

### Task 3: Embedding Runner

**Files:**
- Create: `scripts/db/embed_doc_chunks.py`

- [ ] Select chunks where `embedding is null`.
- [ ] Batch under Voyage's 120k-token request limit and 1,000 inputs.
- [ ] Embed with `voyage-4-large`, `input_type="document"`, 1024 dimensions.
- [ ] Update embeddings and usage metadata transactionally.
- [ ] Support `--limit`, `--report`, `--dry-run`.

### Task 4: Docs And Verification

**Files:**
- Modify: `docs/cockpit_v2_backend.md`

- [ ] Add runbook commands.
- [ ] Run syntax checks.
- [ ] Run chunk dry-run, then load chunk metadata.
- [ ] Do not call Voyage embeddings unless explicitly requested after script setup.
