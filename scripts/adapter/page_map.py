"""
page_map.py — schema-aware semantic page index for a parsed REIT annual report.

For every page of parsed_reports_datalab/<stem>/full.md it produces:
  - an abstractive SUMMARY of the page (ScaleDown, steered toward our 6-table schema)
  - schema TAGS per table: 'lead' (named in the summary's first sentence => the page's
    MAIN artifact) or 'also' (mentioned later) — recall-oriented candidates, plus a
    detected reporting-UNIT hint ('000 vs million) to separate the audited statement
    from marketing cards.

Outputs (under extracted_adapter/<stem>/):
  page_map.jsonl     one record per page  {md_page, tables, unit, summary, ...}
  schema_pages.json  rollup: table -> {"lead": [pages], "also": [pages]}
  page_map.md        human/agent-readable index grouped by schema table, with summaries

ROUTING ONLY. The map says WHERE to look and gives candidates; the extraction agent
picks the authoritative page (e.g. the audited Portfolio Statement in '000, NOT a
per-property marketing card in millions) and extracts from the actual page — never from
the summary. The SLM over-labels (it calls property cards "Portfolio Statement" too), so
the 'lead'/'also'/unit signals are hints, not truth.

Pages are keyed by the markdown `<!-- PAGE N -->` marker = the physical PDF page
(parse_html / cockpit numbering); this can differ from a report's printed page numbers.

Usage:
  python scripts/adapter/page_map.py <stem> [--pages 100-115] [--workers 8]
                                            [--backend scaledown] [--max-tokens 200]
  python scripts/adapter/page_map.py <stem> --retag      # rebuild tags/rollup/md from
                                                          # existing summaries (no API)
Auth: SCALEDOWN_API_KEY from repo-root .env (gitignored) or the environment.
"""
import os
import re
import sys
import json
import time
import argparse
import urllib.request
import urllib.error
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

ROOT = Path(__file__).resolve().parents[2]
SCALEDOWN_URL = "https://api.scaledown.xyz/summarization/abstractive"

SCHEMA_TABLES = ["profile", "performance", "properties",
                 "top_tenants", "trade_mix", "financial"]

# Two anchor tiers, matched ANYWHERE in the ScaleDown SUMMARY. LEAD_ANCHORS = a specific
# named artifact/table (=> the page IS that table). MENTION_ANCHORS = generic terms
# (=> a relevant mention). A page tags 'lead' for a table if any LEAD anchor hits, else
# 'also' if any MENTION anchor hits. Anchors carry sub-sector synonyms (DC: contract
# type/customers/client industry; hospitality: corporate clients). The SLM over-labels
# property cards as "Portfolio Statement", so for properties the unit '000-vs-million
# hint is the real authoritative-page disambiguator, not the tag.
LEAD_ANCHORS = {
    "profile":     [r"corporate (information|directory|profile)", r"trust structure",
                    r"organisation(al)? structure", r"board of directors",
                    r"\bthe manager\b|trustee[\s-]manager|the sponsor\b"],
    "performance": [r"financial (highlights|review)", r"five[\s-]year", r"key financial",
                    r"distribution statement", r"lease expiry profile",
                    r"key (statistics|figures)|performance (at a glance|highlights)"],
    "properties":  [r"portfolio statement", r"statement of portfolio",
                    r"portfolio overview|portfolio (review|at a glance)"],
    "top_tenants": [r"top[\s-]?(\d+|ten|n)\s*(tenants|customers|clients|lessees|"
                    r"occupiers|accounts?)",
                    r"(largest|major|key|principal)\s+(tenants|customers|clients)",
                    r"(tenant|customer|client)\s+concentration"],
    "trade_mix":   [r"trade mix", r"trade sector", r"trade categor", r"tenant mix",
                    r"(by|breakdown by|income by)\s+(contract type|trade|sector|"
                    r"industry|business|asset class|client|trade sector)",
                    r"rental income (breakdown|by)", r"(business|client|sector) mix"],
    "financial":   [r"statement of total return", r"profit or loss",
                    r"comprehensive income", r"statement of cash flow",
                    r"statement of financial position", r"distribution statement",
                    r"gross revenue note|property (operating )?expense note"],
}
MENTION_ANCHORS = {
    "profile":     [r"\bmanager\b|\btrustee\b|\bsponsor\b|property manager"],
    "performance": [r"distribution per unit|\bdpu\b", r"net asset value|\bnav\b",
                    r"aggregate leverage|cost of debt|interest coverage", r"lease expiry"],
    "properties":  [r"investment propert", r"property (valuation|overview|portfolio)",
                    r"\boccupancy\b", r"land tenure|leasehold|freehold|\bgfa\b|\bnla\b|\bgla\b"],
    "top_tenants": [r"\btenant\b|\bcustomer\b|\bclient\b|\blessee\b",
                    r"\bgri\b|gross rental income"],
    "trade_mix":   [r"\btrade\b", r"by (income|gri|nla)", r"\bsegment\b", r"contract type"],
    "financial":   [r"gross revenue", r"property (operating )?expenses", r"finance costs",
                    r"income tax|taxation", r"management fees|net property income"],
}

UNIT_000 = re.compile(r"(sgd|s\$|eur|rmb|us\$|usd|jpy)?\s*['’]?000\b", re.I)
UNIT_MILLION = re.compile(r"(s\$|sgd|eur|usd|us\$|rmb|jpy)?\s*(million|\bmn\b|\bm\b)\b", re.I)

PAGE_RX = re.compile(r"<!--\s*PAGE\s+(\d+)\s*-->")

INSTRUCTIONS = (
    "You are indexing one page of an SGX REIT annual report for a data-extraction "
    "pipeline. In 1-2 sentences, summarise what is on THIS page, leading with its MAIN "
    "table/artifact. Explicitly NAME any of these if present: audited Portfolio Statement "
    "/ Statement of Portfolio (property valuations); Statement of Total Return / Profit or "
    "Loss / Comprehensive Income (revenue, expenses, management fees, finance costs, "
    "fair-value changes, tax); gross revenue or property-expense notes; Top-N "
    "tenants/customers table; trade/tenant mix; DPU / distribution / financial highlights; "
    "manager/trustee/sponsor info. Always state the reporting unit exactly as shown "
    "(e.g. SGD'000 vs S$ million). If none are present, reply exactly "
    "'no schema-relevant data'."
)


def load_dotenv():
    env = ROOT / ".env"
    if not env.exists():
        return
    for line in env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def scaledown_summarize(text, api_key, max_tokens=200, retries=3):
    body = json.dumps({"text": text, "instructions": INSTRUCTIONS,
                       "max_tokens": max_tokens}).encode("utf-8")
    req = urllib.request.Request(
        SCALEDOWN_URL, data=body, method="POST",
        headers={"x-api-key": api_key, "Content-Type": "application/json"})
    delay = 2
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.loads(r.read().decode("utf-8")).get("summary", "")
        except urllib.error.HTTPError as e:
            if e.code == 422:
                return f"[summary error 422]"
            if attempt == retries:
                return f"[summary error {e.code}]"
            time.sleep(delay); delay *= 2
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            if attempt == retries:
                return "[summary error: connection]"
            time.sleep(delay); delay *= 2


def summarize(text, backend, api_key, max_tokens):
    if backend == "scaledown":
        return scaledown_summarize(text, api_key, max_tokens)
    raise SystemExit(f"unknown backend: {backend}")


def split_pages(md):
    out, ms = [], list(PAGE_RX.finditer(md))
    for i, m in enumerate(ms):
        start = m.end()
        end = ms[i + 1].start() if i + 1 < len(ms) else len(md)
        out.append((int(m.group(1)), md[start:end].strip()))
    return out


def lead_sentence(summary):
    s = summary.strip()
    m = re.search(r"[.!?]\s", s)
    return s[:m.start() + 1] if m else s[:160]


def detect_unit(summary):
    if UNIT_000.search(summary):
        return "'000"
    if UNIT_MILLION.search(summary):
        return "million"
    return ""


def tag_summary(summary):
    """{table: 'lead'|'also'} from the summary; lead = named in the first sentence."""
    if not summary or "no schema-relevant data" in summary.lower():
        return {}
    full = summary.lower()
    unit = detect_unit(summary)
    tags = {}
    for t in SCHEMA_TABLES:
        if any(re.search(p, full) for p in LEAD_ANCHORS[t]):
            tags[t] = "lead"            # a specific named artifact => the page IS this table
        elif any(re.search(p, full) for p in MENTION_ANCHORS[t]):
            tags[t] = "also"            # generic mention => candidate / supporting page
    # top_tenants & trade_mix are PERCENTAGE tables, never in 'millions'. A million-unit
    # page is a per-property marketing card, not the authoritative %-table => demote it
    # from 'lead' so the portfolio-level table stands out.
    for t in ("top_tenants", "trade_mix"):
        if tags.get(t) == "lead" and unit == "million":
            tags[t] = "also"
    return tags


def build_outputs(records, out_dir):
    records.sort(key=lambda r: r["md_page"])
    with (out_dir / "page_map.jsonl").open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    rollup = {t: {"lead": [], "also": []} for t in SCHEMA_TABLES}
    for r in records:
        for t, rel in r.get("tables", {}).items():
            rollup[t][rel].append(r["md_page"])
    (out_dir / "schema_pages.json").write_text(
        json.dumps(rollup, ensure_ascii=False, indent=2), encoding="utf-8")

    by_page = {r["md_page"]: r for r in records}
    lines = [f"# Page map — {out_dir.name}", "",
             "_md_page = physical PDF page (parse_html / cockpit numbering)._  ",
             "_Routing only: pick the authoritative page (e.g. Portfolio Statement in "
             "'000, not a card in millions) and extract from the page, not the summary._",
             ""]
    for t in SCHEMA_TABLES:
        lines.append(f"## {t}")
        for rel in ("lead", "also"):
            pages = rollup[t][rel]
            label = "MAIN (lead)" if rel == "lead" else "also mentions"
            if not pages:
                lines.append(f"- _{label}: —_")
                continue
            lines.append(f"- **{label}:**")
            for p in pages:
                r = by_page[p]
                u = f" [{r['unit']}]" if r.get("unit") else ""
                lines.append(f"    - p{p}{u} — {r['summary'][:150]}")
        lines.append("")
    (out_dir / "page_map.md").write_text("\n".join(lines), encoding="utf-8")
    return rollup


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stem")
    ap.add_argument("--pages", help="md-page filter, e.g. '100-115' or '26,106,113'")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--backend", default="scaledown")
    ap.add_argument("--max-tokens", type=int, default=200)
    ap.add_argument("--min-chars", type=int, default=40)
    ap.add_argument("--retag", action="store_true",
                    help="rebuild tags/rollup/md from existing page_map.jsonl (no API)")
    args = ap.parse_args()

    out_dir = ROOT / "extracted_adapter" / args.stem

    if args.retag:
        jl = out_dir / "page_map.jsonl"
        if not jl.exists():
            sys.exit(f"no existing page_map.jsonl to retag: {jl}")
        records = [json.loads(l) for l in jl.read_text(encoding="utf-8").splitlines() if l.strip()]
        for r in records:
            r["tables"] = tag_summary(r.get("summary", ""))
            r["unit"] = detect_unit(r.get("summary", ""))
        rollup = build_outputs(records, out_dir)
        print(f"retagged {len(records)} pages from existing summaries")
        for t in SCHEMA_TABLES:
            print(f"  {t:12} lead={rollup[t]['lead']}")
        return

    load_dotenv()
    api_key = os.environ.get("SCALEDOWN_API_KEY")
    if args.backend == "scaledown" and not api_key:
        sys.exit("SCALEDOWN_API_KEY not found in .env or environment.")

    md_path = ROOT / "parsed_reports_datalab" / args.stem / "full.md"
    if not md_path.exists():
        sys.exit(f"missing markdown: {md_path}")
    pages = split_pages(md_path.read_text(encoding="utf-8"))
    keep = None
    if args.pages:
        keep = set()
        for part in args.pages.split(","):
            if "-" in part:
                a, b = part.split("-"); keep.update(range(int(a), int(b) + 1))
            else:
                keep.add(int(part))
        pages = [(n, t) for n, t in pages if n in keep]
    print(f"{args.stem}: {len(pages)} page(s) (backend={args.backend})")

    def work(item):
        n, text = item
        if len(text) < args.min_chars:
            return {"md_page": n, "tables": {}, "unit": "", "summary": "",
                    "input_chars": len(text)}
        summ = summarize(text, args.backend, api_key, args.max_tokens).strip()
        return {"md_page": n, "tables": tag_summary(summ), "unit": detect_unit(summ),
                "summary": summ, "input_chars": len(text)}

    records = []
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        for i, rec in enumerate(ex.map(work, pages), 1):
            records.append(rec)
            if i % 10 == 0 or i == len(pages):
                print(f"  ...{i}/{len(pages)}")

    out_dir.mkdir(parents=True, exist_ok=True)
    rollup = build_outputs(records, out_dir)
    rel = sum(1 for r in records if r["tables"])
    print(f"wrote page_map.jsonl / schema_pages.json / page_map.md to {out_dir}")
    print(f"schema-relevant pages: {rel}/{len(records)}")
    for t in SCHEMA_TABLES:
        print(f"  {t:12} lead={rollup[t]['lead']}")


if __name__ == "__main__":
    main()
