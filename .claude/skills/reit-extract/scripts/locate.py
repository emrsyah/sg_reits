"""locate.py - section index + sub-sector classifier for a parsed REIT report.

Usage: python locate.py <path-to-full.md> [extra-grep-term ...]

Tuned for Datalab (Marker/Surya) markdown (page-anchored `<!-- PAGE N -->`, clean pipe
tables) but stays parser-agnostic. Built from a 4-archetype structural sweep
(SG-diversified / hospitality-stapled / data-centre / US-office), so it knows the
patterns those reports actually share:

  * a THREE-TIER valuation disclosure (marketing summary -> per-property detail ->
    AUDITED Portfolio Statement). The audited Portfolio Statement is the canonical
    `market_valuation` source; the other two are alt/operating values. locate.py tags
    all three so the agent reads the right one.
  * sub-sector-conditional tables: trade_mix / top_tenant exist for retail+office,
    degrade to client-type/contract-type for data-centre/hospitality. The classifier
    tells the agent which playbook to use BEFORE it reads 200 pages.

Output: detected dialect, a sub-sector guess with evidence, the audited-FS start page,
then one line per anchor hit -> page, line, matched text.
"""
import re
import sys
from collections import Counter
from pathlib import Path

# anchor -> regex. Order is reading order (front-of-book first, audited notes last).
ANCHORS = [
    # profile / front matter
    ("about_trust",          r"\babout (us|the trust|must|clas)\b|corporate profile"),
    ("trust_structure",      r"trust(?: and organisation)? structure|organisation chart"),
    ("corporate_info",       r"corporate information|corporate directory"),
    ("financial_highlights", r"financial highlights|5[- ]year financial|five[- ]year financial"),
    # property tiers (THREE of them - read the audited one for market_valuation)
    ("valuation_summary",    r"portfolio valuation|valuation as at|appraised value"),       # tier A (marketing)
    ("per_property_detail",  r"property details|at a glance|property information"),          # tier B (operating)
    ("portfolio_statement",  r"portfolio statement|statement of portfolio|investment properties"),  # tier C (AUDITED)
    ("financial_review",     r"financial review|by property|revenue and gross profit"),
    ("occupancy",            r"committed occupancy|occupancy rate|portfolio occupancy"),
    ("tenure",               r"land tenure|tenure of land|land title|term of lease|land use right"),
    ("held_for_sale",        r"held for sale|asset held for sale|held-for-sale"),
    # tenants & mix (sub-sector conditional)
    ("top_tenants",          r"top (10|ten) tenants?|top (10|ten) (corporate )?clients?"),
    ("trade_mix",            r"trade (mix|sector)|tenant.{0,15}mix|business.{0,10}mix"),
    ("client_type",          r"hyperscaler|colocation|contract type|by contract|client.{0,10}trade sector"),
    # performance / distribution
    ("distribution_stmt",    r"distribution statement|available for distribution|income available"),
    ("dpu",                  r"\bdpu\b|distribution per (unit|stapled security)|per unit \(cents\)"),
    ("unitholders",          r"statistics of unitholding|number of unitholders|securityholders"),
    # audited financial statements
    ("financial_position",   r"statement(s)? of financial position|balance sheet"),
    ("total_return",         r"statement(s)? of (total return|comprehensive income|profit or loss)"),
    ("revenue_note",         r"\bgross revenue\b|\bgross rental income\b"),
    ("expense_note",         r"property (operating )?expenses|direct expenses"),
    ("segment_note",         r"segment(al)? (information|reporting)|operating segments"),
    ("nci",                  r"non-controlling interest|minority interest"),
    ("subsequent_events",    r"subsequent event"),
    # corporate actions (parked table, but useful context)
    ("transactions",         r"acquisition|divestment|completion of (the )?(acquisition|sale)"),
]

MARKER_PATTERNS = [
    ("datalab/llamaparse", re.compile(r"<!--\s*PAGE\s+(\d+)\s*-->", re.I)),
    ("dashes",             re.compile(r"^---+\s*(?:page\s*)?(\d+)\s*---+\s*$", re.I | re.M)),
    ("braces",             re.compile(r"^\{(\d+)\}-+", re.M)),
    ("page_n_of",          re.compile(r"^Page\s+(\d+)\s+of\s+\d+", re.I | re.M)),
]

# sub-sector signatures: term -> weight. The classifier sums weighted hits and reports
# the leader + runner-up so the agent can sanity-check (e.g. Diversified vs Retail).
SUBSECTOR_SIGNS = {
    "Data Centre": {r"data centre|data center": 3, r"colocation|colo\b": 3,
                    r"hyperscaler": 3, r"\bMW\b|megawatt": 2, r"shell and core": 2,
                    r"fully-fitted": 2, r"power usage|pue\b": 1},
    "Hospitality": {r"serviced residence": 3, r"revpau|revpar": 3, r"lodging": 2,
                    r"master lease": 1, r"management contract": 1, r"hotel": 1,
                    r"\bkeys\b|number of units|adr\b": 1, r"student accommodation": 2,
                    r"rental housing": 2},
    "Healthcare":  {r"hospital|nursing home": 3, r"healthcare": 2, r"medical centre": 2,
                    r"aged care": 2},
    "Industrial":  {r"logistics|warehouse": 2, r"industrial": 2, r"business park": 2,
                    r"high-?spec|ramp-?up|light industrial": 2, r"\b3pl\b": 1},
    "Office":      {r"\boffice\b": 2, r"\bgrade a\b|grade-a": 2, r"\bwale\b": 1,
                    r"cbd\b": 1, r"net lettable area": 1},
    "Retail":      {r"\bretail\b|shopping (mall|centre)": 2, r"footfall|shopper traffic": 3,
                    r"tenant sales|gto\b|gross turnover": 2, r"trade mix": 1},
}


def classify_subsector(text: str) -> list[tuple[str, int]]:
    low = text.lower()
    scores: Counter = Counter()
    for sector, signs in SUBSECTOR_SIGNS.items():
        for pat, w in signs.items():
            scores[sector] += w * len(re.findall(pat, low))
    ranked = [(s, n) for s, n in scores.most_common() if n]
    return ranked


# physical asset classes that, when 2+ are co-dominant, mean a Diversified trust
PHYSICAL = {"Retail", "Office", "Industrial", "Healthcare", "Data Centre", "Hospitality"}


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    path = Path(sys.argv[1])
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    # detect page-marker dialect
    dialect, best = None, []
    for name, pat in MARKER_PATTERNS:
        hits = [(m.start(), int(m.group(1))) for m in pat.finditer(text)]
        if len(hits) > len(best):
            dialect, best = name, hits
    estimated = not best
    if estimated:
        print("! no page markers -> pages ESTIMATED (flag p_estimated:true)")
        n_pages = max(2, round(len(text) / 3500))
        best = [(int(len(text) * i / n_pages), i + 1) for i in range(n_pages)]
    else:
        print(f"page markers: {dialect} ({len(best)} markers, "
              f"pages {best[0][1]}-{best[-1][1]})")

    offsets = [h[0] for h in best]
    pages = [h[1] for h in best]

    def page_of(pos: int) -> int:
        lo, hi = 0, len(offsets) - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if offsets[mid] <= pos:
                lo = mid
            else:
                hi = mid - 1
        return pages[lo]

    # sub-sector guess
    ranked = classify_subsector(text)
    if ranked:
        lead = ranked[0]
        runner = ranked[1] if len(ranked) > 1 else ("-", 0)
        # Diversified when the runner-up physical class is co-dominant with the leader
        # (e.g. CICT: Retail 672 + Office 407). Tuned so pure trusts that merely mention
        # other classes don't flip (runner must be >=60% of leader AND >=200 absolute).
        diversified = (lead[0] in PHYSICAL and runner[0] in PHYSICAL
                       and runner[1] >= 0.6 * lead[1] and runner[1] >= 200)
        guess = "Diversified" if diversified else lead[0]
        print(f"sub_sector guess: {guess}  "
              f"(top signals: {lead[0]}={lead[1]}, {runner[0]}={runner[1]}"
              f"{'; co-dominant -> Diversified' if diversified else ''})")
        print(f"  full scores: {', '.join(f'{s}={n}' for s, n in ranked)}")

    # audited-FS start: the "Report of the Trustee" heading reliably opens the audited
    # financial-statements section in all archetypes. Skip table-of-contents rows
    # (short, or a `| ... | <pagenum> |` cell) and prose mentions; take the first real
    # heading.
    line_starts, acc = [], 0
    for ln in lines:
        line_starts.append(acc)
        acc += len(ln) + 1
    # the real section opener is a markdown heading ("### Report of the Trustee");
    # table-of-contents entries are pipe rows, so requiring the heading prefix excludes them.
    rot_rx = re.compile(r"^#{1,6}\s*report of the trustee", re.I)
    fs_line = next((i for i, ln in enumerate(lines) if rot_rx.search(ln.strip())), None)
    if fs_line is not None:
        print(f"audited FS section (Report of the Trustee) ~page "
              f"{page_of(line_starts[fs_line])} (line {fs_line + 1}: "
              f"{lines[fs_line].strip()[:70]})")

    # anchor hits
    terms = ANCHORS + [(f"extra:{t}", re.escape(t)) for t in sys.argv[2:]]
    print(f"\n{'anchor':22s} {'pages':>16s}  first-hit text")
    for name, pattern in terms:
        pat = re.compile(pattern, re.I)
        hit_pages, first_text = [], None
        seen = set()
        for i, ln in enumerate(lines):
            if not pat.search(ln):
                continue
            pg = page_of(line_starts[i])
            if pg in seen:
                continue
            seen.add(pg)
            hit_pages.append(pg)
            if first_text is None:
                first_text = ln.strip()[:70]
        if hit_pages:
            shown = ",".join(str(p) for p in hit_pages[:8])
            if len(hit_pages) > 8:
                shown += f",+{len(hit_pages) - 8}"
            print(f"{name:22s} {shown:>16s}  {first_text}")
        else:
            print(f"{name:22s} {'-':>16s}  (no hits)")


if __name__ == "__main__":
    try:
        main()
    except OSError:
        sys.exit(0)
