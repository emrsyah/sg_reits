import os
from llama_cloud import LlamaCloud

c = LlamaCloud(api_key=os.environ["LLAMA_CLOUD_API_KEY"])
for jid in ["pjb-5zyenfyhwgpx7hryrxvnmy4t8rqj", "pjb-1bszhpcuue88yipkllc3psrnxosm"]:
    r = c.parsing.get(jid, expand=["markdown"])
    pages = r.markdown.pages if r.markdown else []
    first = (pages[0].markdown or "")[:300].replace("\n", " | ") if pages else "(no pages)"
    print(f"{jid}  n_pages={len(pages)}")
    print(f"  first page: {first}")
    print()
