#!/usr/bin/env python3
"""Fetch completed LlamaParse jobs by job_id (no new credits spent) and save outputs."""
import asyncio
import json
import os
from pathlib import Path

from llama_cloud import AsyncLlamaCloud

ROOT = Path(__file__).resolve().parent.parent  # repo root (script lives in scripts/)
OUT_DIR = ROOT / "parsed_reports"
OUT_DIR.mkdir(exist_ok=True)

JOBS = {
    "28_M44U.SI_Mapletree-Logistics-Trust_FY2025": "pjb-lq2xctcaanx3qy273r2dspqcob4c",
    "09_C38U.SI_CapitaLand-Integrated-Commercial-Trust_FY2025": "pjb-5jo8bds6tcmdoiolhwu01mmo1e3y",
    "21_AJBU.SI_Keppel-DC-REIT_FY2025": "pjb-n2s3pta479wtlyntuo25hopf1jvm",
    "16_Q5T.SI_Far-East-Hospitality-Trust_FY2025": "pjb-5zyenfyhwgpx7hryrxvnmy4t8rqj",
    "17_AW9U.SI_First-REIT_FY2025": "pjb-1bszhpcuue88yipkllc3psrnxosm",
}

client = AsyncLlamaCloud(api_key=os.environ["LLAMA_CLOUD_API_KEY"])


async def fetch(stem: str, job_id: str):
    out = OUT_DIR / stem
    if (out / "full.md").exists():
        print(f"= skip: {stem}")
        return
    try:
        await client.parsing.wait_for_completion(
            job_id, polling_interval=5.0, max_interval=20.0, timeout=7200.0
        )
        result = await client.parsing.get(
            job_id, expand=["markdown", "items"], timeout=300.0
        )
        out.mkdir(exist_ok=True)
        pages = result.markdown.pages if result.markdown else []
        with open(out / "full.md", "w", encoding="utf-8") as f:
            for p in pages:
                f.write(f"\n\n<!-- PAGE {p.page_number} -->\n\n")
                f.write(p.markdown or "")
        item_pages = result.items.pages if result.items else []
        items_by_page = {p.page_number: p for p in item_pages}
        with open(out / "pages.jsonl", "w", encoding="utf-8") as f:
            for p in pages:
                ip = items_by_page.get(p.page_number)
                types = [i.type for i in ip.items] if ip else []
                f.write(json.dumps({
                    "page": p.page_number,
                    "markdown": p.markdown,
                    "item_types": types,
                }, ensure_ascii=False) + "\n")
        with open(out / "meta.json", "w", encoding="utf-8") as f:
            json.dump({"job_id": job_id, "pages": len(pages)}, f, indent=2)
        print(f"+ saved: {stem} ({len(pages)} pages)")
    except Exception as e:
        print(f"! error: {stem} - {type(e).__name__}: {e}")


async def main():
    await asyncio.gather(*[fetch(s, j) for s, j in JOBS.items()])


if __name__ == "__main__":
    asyncio.run(main())
