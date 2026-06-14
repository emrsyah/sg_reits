"""
page_map2.py — classify-based schema page index (ScaleDown /classify), v2 of page_map.py.

Instead of keyword-tagging an abstractive summary, this CLASSIFIES each page against the
6 schema tables (+ none) using rubrics — so routing is sub-sector-agnostic and gives a
probability per table. For sparse/diagram pages (e.g. the Trust Structure page that the
summarizer returned empty for) it falls back to OCR by re-classifying the PDF page image.
Reuses v1 page_map.jsonl summaries (if present) for the human-readable notes — no
re-summarising.

Outputs (under extracted_adapter/<stem>/):
  page_map_v2.jsonl     per page {md_page, top_label, scores, tables, ocr, summary}
  schema_pages_v2.json  rollup: table -> {"lead": [pages], "also": [pages]}
  page_map_v2.md        grouped index with scores + summaries

ROUTING ONLY. top_label = the page's primary table; the agent still reads the page and
picks the authoritative source by unit/playbook. Never extract numbers from this.

Usage:
  python scripts/adapter/page_map2.py <stem> [--pages 1-30] [--workers 6]
                                             [--lead-min 0.30] [--also-min 0.15]
                                             [--no-ocr]
Auth: SCALEDOWN_API_KEY in repo-root .env or the environment.
"""
import os
import re
import sys
import json
import time
import base64
import argparse
import urllib.request
import urllib.error
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

ROOT = Path(__file__).resolve().parents[2]
CLASSIFY_URL = "https://api.scaledown.xyz/classify"
EXTRACT_URL = "https://api.scaledown.xyz/extract"

SCHEMA_TABLES = ["profile", "performance", "properties",
                 "top_tenants", "trade_mix", "financial"]

# Sub-sector-agnostic rubrics (yes/no questions). These REPLACE the v1 keyword anchors.
LABELS = [
    {"name": "profile",
     "rubric": "Does this page identify the REIT's management entities (the manager, "
               "trustee, sponsor, or property manager) or show the trust structure / "
               "corporate information?"},
    {"name": "performance",
     "rubric": "Does this page report headline performance or key statistics — DPU, "
               "distribution, NAV, gearing, a five-year financial summary, or unitholding "
               "statistics?"},
    {"name": "properties",
     "rubric": "Is this the audited Portfolio Statement or a per-property listing showing "
               "property valuations / carrying values?"},
    {"name": "top_tenants",
     "rubric": "Does this page rank the largest tenants, customers, or clients by their "
               "share of gross rental income?"},
    {"name": "trade_mix",
     "rubric": "Does this page break the portfolio down by tenant trade sector, business "
               "type, industry, or contract type as percentages?"},
    {"name": "financial",
     "rubric": "Is this an audited income statement (statement of total return, profit or "
               "loss, or comprehensive income) or a revenue/expense note, showing finance "
               "costs, management fees, fair-value changes or tax?"},
    {"name": "none",
     "rubric": "Is this page narrative, governance, ESG, risk, or otherwise NOT a "
               "financial/portfolio data table?"},
]

PROFILE_ENTITIES = {
    "manager": "The REIT manager company name",
    "trustee": "The trustee company name",
    "sponsor": "The sponsor company name",
    "property_manager": "The property manager company name",
}

PAGE_RX = re.compile(r"<!--\s*PAGE\s+(\d+)\s*-->")
UNIT_000 = re.compile(r"(sgd|s\$|eur|rmb|us\$|usd|jpy)?\s*['’]?000\b", re.I)
UNIT_MILLION = re.compile(r"(s\$|sgd|eur|usd|us\$|rmb|jpy)?\s*(million|\bmn\b)\b", re.I)


def detect_unit(s):
    if not s:
        return ""
    if UNIT_000.search(s):
        return "'000"
    if UNIT_MILLION.search(s):
        return "million"
    return ""


def load_dotenv():
    env = ROOT / ".env"
    if not env.exists():
        return
    for line in env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def _post(url, body, api_key, retries=3):
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, method="POST",
        headers={"x-api-key": api_key, "Content-Type": "application/json"})
    delay = 2
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 422:
                return {"_error": f"422 {e.read()[:120]!r}"}
            if attempt == retries:
                return {"_error": str(e.code)}
            time.sleep(delay); delay *= 2
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            if attempt == retries:
                return {"_error": "connection"}
            time.sleep(delay); delay *= 2


def classify_text(text, api_key):
    return _post(CLASSIFY_URL, {"text": text, "labels": LABELS}, api_key)


def classify_pdf_page(pdf_b64, api_key):
    return _post(CLASSIFY_URL, {"document": pdf_b64,
                                "document_mime_type": "application/pdf",
                                "labels": LABELS}, api_key)


def extract_pdf_page(pdf_b64, api_key):
    return _post(EXTRACT_URL, {"document": pdf_b64,
                               "document_mime_type": "application/pdf",
                               "entities": PROFILE_ENTITIES}, api_key)


def split_pages(md):
    out, ms = [], list(PAGE_RX.finditer(md))
    for i, m in enumerate(ms):
        start = m.end()
        end = ms[i + 1].start() if i + 1 < len(ms) else len(md)
        out.append((int(m.group(1)), md[start:end].strip()))
    return out


def page_pdf_b64(reader, md_page):
    """Extract one physical page (1-based md_page) as a single-page PDF, base64."""
    try:
        from pypdf import PdfWriter
        import io
        w = PdfWriter()
        w.add_page(reader.pages[md_page - 1])
        buf = io.BytesIO()
        w.write(buf)
        return base64.b64encode(buf.getvalue()).decode("ascii")
    except Exception:
        return None


def tags_from_scores(scores, lead_min, also_min):
    tags = {}
    for t in SCHEMA_TABLES:
        s = scores.get(t, 0.0)
        if s >= lead_min:
            tags[t] = "lead"
        elif s >= also_min:
            tags[t] = "also"
    return tags


def build_outputs(records, out_dir, also_min):
    """Score-RANKED rollup: per table, pages with score >= also_min sorted desc.
    The authoritative page is `top` (highest classify score); completeness sections
    (e.g. financial) read down the ranked list."""
    records.sort(key=lambda r: r["md_page"])
    out_dir.mkdir(parents=True, exist_ok=True)
    with (out_dir / "page_map_v2.jsonl").open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    by = {r["md_page"]: r for r in records}
    rollup = {}
    for t in SCHEMA_TABLES:
        ranked = sorted(
            ((r["md_page"], r["scores"].get(t, 0.0)) for r in records
             if r["scores"].get(t, 0.0) >= also_min),
            key=lambda x: -x[1])
        # authoritative audited source = highest-scoring page in '000 (not millions);
        # for the %-tables (top_tenants/trade_mix) just use the top score.
        top_000 = next((p for p, _ in ranked if by[p].get("unit") == "'000"), None)
        rollup[t] = {"top": ranked[0][0] if ranked else None,
                     "top_audited_000": top_000,
                     "ranked": [[p, round(s, 3), by[p].get("unit", "")] for p, s in ranked]}
    (out_dir / "schema_pages_v2.json").write_text(
        json.dumps(rollup, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [f"# Page map v2 (classify) — {out_dir.name}", "",
             "_Per table, pages RANKED by classify score (+ reporting unit). `top` = highest "
             "score; `top_audited_000` = highest-scoring page in '000 (the audited statement, "
             "vs marketing cards in millions)._",
             "_Routing only; confirm the page & extract from it, not from here._", ""]
    for t in SCHEMA_TABLES:
        top = rollup[t]["top"]
        a000 = rollup[t]["top_audited_000"]
        hdr = f"## {t}  — top: {'p'+str(top) if top else 'none'}"
        if a000 and a000 != top:
            hdr += f"  · audited('000): p{a000}"
        lines.append(hdr)
        for p, s, u in rollup[t]["ranked"]:
            r = by[p]
            tag = " OCR" if r.get("ocr") else ""
            uu = f" [{u}]" if u else ""
            lines.append(f"- [{s:.2f}{tag}]{uu} p{p} — {r.get('summary','')[:120]}")
        lines.append("")
    (out_dir / "page_map_v2.md").write_text("\n".join(lines), encoding="utf-8")
    return rollup


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stem")
    ap.add_argument("--pages")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--lead-min", type=float, default=0.30)
    ap.add_argument("--also-min", type=float, default=0.15)
    ap.add_argument("--min-chars", type=int, default=200,
                    help="below this, OCR-fallback the page image")
    ap.add_argument("--no-ocr", action="store_true")
    ap.add_argument("--rebuild", action="store_true",
                    help="rebuild rollup/md from existing page_map_v2.jsonl (no API)")
    args = ap.parse_args()

    if args.rebuild:
        jl = ROOT / "extracted_adapter" / args.stem / "page_map_v2.jsonl"
        if not jl.exists():
            sys.exit(f"no page_map_v2.jsonl to rebuild: {jl}")
        records = [json.loads(l) for l in jl.read_text(encoding="utf-8").splitlines() if l.strip()]
        for r in records:
            r["tables"] = tags_from_scores(r.get("scores", {}), args.lead_min, args.also_min)
            if not r.get("unit"):
                r["unit"] = detect_unit(r.get("summary", ""))
        build_outputs(records, ROOT / "extracted_adapter" / args.stem, args.also_min)
        return

    load_dotenv()
    api_key = os.environ.get("SCALEDOWN_API_KEY")
    if not api_key:
        sys.exit("SCALEDOWN_API_KEY not found in .env or environment.")

    md_path = ROOT / "parsed_reports_datalab" / args.stem / "full.md"
    if not md_path.exists():
        sys.exit(f"missing markdown: {md_path}")
    pages = split_pages(md_path.read_text(encoding="utf-8"))
    if args.pages:
        keep = set()
        for part in args.pages.split(","):
            if "-" in part:
                a, b = part.split("-"); keep.update(range(int(a), int(b) + 1))
            else:
                keep.add(int(part))
        pages = [(n, t) for n, t in pages if n in keep]

    # reuse v1 summaries for notes (no re-summarising)
    v1 = {}
    v1p = ROOT / "extracted_adapter" / args.stem / "page_map.jsonl"
    if v1p.exists():
        for l in v1p.read_text(encoding="utf-8").splitlines():
            if l.strip():
                r = json.loads(l); v1[r["md_page"]] = r.get("summary", "")

    reader = None
    if not args.no_ocr:
        pdf = ROOT / "annual_reports" / f"{args.stem}.pdf"
        if pdf.exists():
            try:
                from pypdf import PdfReader
                reader = PdfReader(str(pdf))
            except Exception as e:
                print(f"(pdf load failed, OCR fallback disabled: {e})")

    print(f"{args.stem}: classify {len(pages)} page(s)  (ocr={'on' if reader else 'off'})")

    def work(item):
        n, text = item
        ocr = False
        res = classify_text(text, api_key) if len(text) >= 1 else {"_error": "empty"}
        sparse = len(text) < args.min_chars
        low = res.get("top_label") in (None, "none")
        if reader is not None and (sparse or low or "_error" in res):
            b64 = page_pdf_b64(reader, n)
            if b64:
                ocr_res = classify_pdf_page(b64, api_key)
                if "_error" not in ocr_res:
                    res = ocr_res; ocr = True
        scores = res.get("scores", {})
        return {"md_page": n, "top_label": res.get("top_label"),
                "scores": {k: round(v, 3) for k, v in scores.items()},
                "tables": tags_from_scores(scores, args.lead_min, args.also_min),
                "unit": detect_unit(text) or detect_unit(v1.get(n, "")),
                "ocr": ocr, "summary": v1.get(n, ""),
                "err": res.get("_error")}

    records = []
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        for i, rec in enumerate(ex.map(work, pages), 1):
            records.append(rec)
            if i % 10 == 0 or i == len(pages):
                print(f"  ...{i}/{len(pages)}")

    out_dir = ROOT / "extracted_adapter" / args.stem
    rollup = build_outputs(records, out_dir, args.also_min)
    errs = sum(1 for r in records if r["err"])
    ocrs = sum(1 for r in records if r["ocr"])
    print(f"wrote *_v2 to {out_dir}  (ocr-fallback used on {ocrs} pages, {errs} errors)")
    for t in SCHEMA_TABLES:
        rk = rollup[t]["ranked"]
        print(f"  {t:12} top=p{rollup[t]['top']}  ({len(rk)} pages "
              f">= {args.also_min})  {rk[:4]}")


if __name__ == "__main__":
    main()
