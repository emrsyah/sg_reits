"""locate.py — parser-agnostic section index for a parsed annual report.

Usage: python locate.py <path-to-full.md> [extra-grep-term ...]

Detects the page-marker dialect, then prints page locations of the standard extraction
anchors (Portfolio Statement, Distribution Statement, Top 10, Trade Mix, ...) plus any
extra terms given. Output: one line per hit -> page, line number, matched text.
"""
import re
import sys
from pathlib import Path

ANCHORS = [
    ("portfolio_statement",  r"portfolio statement"),
    ("total_return",         r"statement(s)? of total return"),
    ("distribution_stmt",    r"distribution statement|available for distribution"),
    ("revenue_note",         r"gross revenue\b"),
    ("expense_note",         r"property (operating )?expenses"),
    ("per_property_table",   r"by property|financial review"),
    ("top_tenants",          r"top (10|ten)"),
    ("trade_mix",            r"trade (mix|sector)"),
    ("occupancy",            r"committed occupancy|occupancy rate"),
    ("tenure",               r"land tenure|land title|term of lease|land use right"),
    ("unitholders",          r"statistics of unitholding"),
    ("transactions",         r"acquisition|divestment|purchase price|legal completion"),
    ("subsequent_events",    r"subsequent event"),
    ("valuation_table",      r"valuation as at|portfolio valuation|appraised value"),
]

MARKER_PATTERNS = [
    ("llamaparse_agentic", re.compile(r"<!--\s*PAGE\s+(\d+)\s*-->", re.I)),
    ("dashes",             re.compile(r"^---+\s*(?:page\s*)?(\d+)\s*---+\s*$", re.I | re.M)),
    ("braces",             re.compile(r"^\{(\d+)\}-+", re.M)),
    ("page_n_of",          re.compile(r"^Page\s+(\d+)\s+of\s+\d+", re.I | re.M)),
]


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    path = Path(sys.argv[1])
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    # detect dialect
    dialect, best = None, []
    for name, pat in MARKER_PATTERNS:
        hits = [(m.start(), int(m.group(1))) for m in pat.finditer(text)]
        if len(hits) > len(best):
            dialect, best = name, hits
    estimated = not best
    if estimated:
        print("! no page markers found -> pages are ESTIMATED (flag p_estimated:true)")
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

    # line start offsets for line numbers
    line_starts, acc = [], 0
    for ln in lines:
        line_starts.append(acc)
        acc += len(ln) + 1

    terms = ANCHORS + [(f"extra:{t}", re.escape(t)) for t in sys.argv[2:]]
    print(f"{'anchor':22s} {'page':>5s} {'line':>7s}  text")
    for name, pattern in terms:
        pat = re.compile(pattern, re.I)
        seen_pages = set()
        for i, ln in enumerate(lines):
            m = pat.search(ln)
            if not m:
                continue
            pg = page_of(line_starts[i])
            if pg in seen_pages:        # one hit per page per anchor keeps output scannable
                continue
            seen_pages.add(pg)
            print(f"{name:22s} {pg:>5d} {i + 1:>7d}  {ln.strip()[:90]}")
        if not seen_pages:
            print(f"{name:22s} {'-':>5s} {'-':>7s}  (no hits)")


if __name__ == "__main__":
    try:
        main()
    except OSError:        # EPIPE when piped into head — output already delivered
        sys.exit(0)
