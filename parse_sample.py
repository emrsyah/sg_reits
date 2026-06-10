#!/usr/bin/env python3
"""Parse a stratified sample of REIT annual reports with LlamaParse (agentic tier).

Outputs per report into parsed_reports/<stem>/:
  - full.md        concatenated page markdown with page separators
  - pages.jsonl    one JSON object per page (page number, markdown, item types)
  - meta.json      job id, page count, timing
"""
import asyncio
import json
import os
import sys
import time
from pathlib import Path

from llama_cloud import AsyncLlamaCloud

ROOT = Path(__file__).resolve().parent
IN_DIR = ROOT / "annual_reports"
OUT_DIR = ROOT / "parsed_reports"
OUT_DIR.mkdir(exist_ok=True)

SAMPLE = [
    "09_C38U.SI_CapitaLand-Integrated-Commercial-Trust_FY2025.pdf",
    "21_AJBU.SI_Keppel-DC-REIT_FY2025.pdf",
    "28_M44U.SI_Mapletree-Logistics-Trust_FY2025.pdf",
    "17_AW9U.SI_First-REIT_FY2025.pdf",
    "16_Q5T.SI_Far-East-Hospitality-Trust_FY2025.pdf",
    "36_SET.SI_Stoneweg-Europe-Stapled-Trust_FY2025.pdf",
    "22_CMOU.SI_KORE-US-REIT_FY2024.pdf",
]

client = AsyncLlamaCloud(api_key=os.environ["LLAMA_CLOUD_API_KEY"])
semaphore = asyncio.Semaphore(3)


async def parse_one(fname: str):
    src = IN_DIR / fname
    stem = src.stem
    out = OUT_DIR / stem
    if (out / "full.md").exists():
        print(f"= skip (done): {fname}", flush=True)
        return {"file": fname, "status": "cached"}
    async with semaphore:
        t0 = time.monotonic()
        try:
            print(f"> upload: {fname} ({src.stat().st_size/1e6:.1f} MB)", flush=True)
            file_obj = await client.files.create(
                file=str(src), purpose="parse", external_file_id=fname
            )
            print(f"> parse:  {fname} (file_id={file_obj.id})", flush=True)
            job = await client.parsing.create(
                file_id=file_obj.id,
                tier="agentic",
                version="latest",
            )
            print(f"> job:    {fname} (job_id={job.id})", flush=True)
            await client.parsing.wait_for_completion(
                job.id, polling_interval=5.0, max_interval=20.0, timeout=7200.0
            )
            result = await client.parsing.get(
                job.id, expand=["markdown", "items"], timeout=300.0
            )
            out.mkdir(exist_ok=True)
            pages = result.markdown.pages if result.markdown else []
            with open(out / "full.md", "w", encoding="utf-8") as f:
                for p in pages:
                    f.write(f"\n\n<!-- PAGE {p.page} -->\n\n")
                    f.write(p.markdown or "")
            with open(out / "pages.jsonl", "w", encoding="utf-8") as f:
                item_pages = result.items.pages if result.items else []
                items_by_page = {p.page: p for p in item_pages}
                for p in pages:
                    ip = items_by_page.get(p.page)
                    types = [i.type for i in ip.items] if ip else []
                    f.write(json.dumps({
                        "page": p.page,
                        "markdown": p.markdown,
                        "item_types": types,
                    }, ensure_ascii=False) + "\n")
            dt = time.monotonic() - t0
            meta = {
                "file": fname,
                "job_id": getattr(result, "id", None),
                "pages": len(pages),
                "seconds": round(dt, 1),
            }
            with open(out / "meta.json", "w", encoding="utf-8") as f:
                json.dump(meta, f, indent=2)
            print(f"+ done:   {fname} - {len(pages)} pages in {dt/60:.1f} min", flush=True)
            return {"file": fname, "status": "ok", **meta}
        except Exception as e:
            print(f"! error:  {fname} - {type(e).__name__}: {e}", flush=True)
            return {"file": fname, "status": "error", "error": str(e)}


async def main():
    results = await asyncio.gather(*[parse_one(f) for f in SAMPLE])
    ok = sum(1 for r in results if r["status"] in ("ok", "cached"))
    print(f"\nFinished: {ok}/{len(SAMPLE)} succeeded")
    with open(OUT_DIR / "_run_summary.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    if ok < len(SAMPLE):
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
