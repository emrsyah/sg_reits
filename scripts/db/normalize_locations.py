"""Canonical normalization for properties_location (sgx_reit_performance).

Goal: one country -> one canonical spelling, city/sub-national detail removed,
"[A, B, C]" bracketed text with ", " separators.

Approach (robust to any delimiter , ; / space or none):
  1. strip surrounding [ ] and remove any "(...)" parenthetical (that's where embedded
     cities / state lists / "(12 properties)" live).
  2. replace "/" with a space ("United Kingdom/Europe" -> "United Kingdom Europe").
  3. scan the cleaned text for known country spellings (longest-first, non-overlapping),
     map each to its canonical name, dedupe preserving order.
  4. render "[" + ", ".join(countries) + "]".
Tokens that match no known country (cities, continents like "Europe", "12 properties")
are dropped. Add new countries/variants to CANON below if a future report needs them.
"""
import re

# canonical -> list of accepted spellings (canonical MUST be included). Order within a
# list doesn't matter; the matcher sorts ALL spellings longest-first so multi-word and
# variant spellings win over shorter substrings.
CANON = {
    "Singapore": ["Singapore"],
    "Australia": ["Australia"],
    "China": ["China", "People's Republic of China", "PRC"],
    "Hong Kong SAR": ["Hong Kong SAR", "Hong Kong"],
    "Japan": ["Japan"],
    "South Korea": ["South Korea", "Republic of Korea", "Korea"],
    "India": ["India"],
    "Malaysia": ["Malaysia"],
    "Vietnam": ["Vietnam", "Viet Nam"],
    "Indonesia": ["Indonesia"],
    "Philippines": ["The Philippines", "Philippines"],
    "Maldives": ["Maldives"],
    "New Zealand": ["New Zealand"],
    "United States": ["United States of America", "United States", "U.S.A.", "U.S.", "USA", "US"],
    "Canada": ["Canada"],
    "United Kingdom": ["United Kingdom", "Great Britain", "England", "Scotland", "Wales",
                       "U.K.", "UK"],
    "Netherlands": ["The Netherlands", "Netherlands"],
    "France": ["France"],
    "Germany": ["Germany"],
    "Italy": ["Italy"],
    "Spain": ["Spain"],
    "Ireland": ["Ireland"],
    "Belgium": ["Belgium"],
    "Poland": ["Poland"],
    "Denmark": ["Denmark"],
    "Czech Republic": ["Czech Republic", "Czechia"],
    "Finland": ["Finland"],
    "Slovakia": ["Slovakia", "Slovak Republic"],
    "Switzerland": ["Switzerland"],
}

# spelling -> canonical, and a longest-first alternation for scanning
_SPELL2CANON = {}
for _canon, _spellings in CANON.items():
    for _s in _spellings:
        _SPELL2CANON[_s.lower()] = _canon
_ALL_SPELLINGS = sorted(_SPELL2CANON.keys(), key=len, reverse=True)
_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(s) for s in _ALL_SPELLINGS) + r")\b",
    re.IGNORECASE,
)
_PAREN = re.compile(r"\([^)]*\)")


def normalize_locations(value):
    """Return canonical bracketed text '[A, B, C]', or None if value is None/empty.
    Idempotent: already-normalized '[Singapore, Australia]' round-trips unchanged."""
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    if s.startswith("[") and s.endswith("]"):
        s = s[1:-1]
    s = _PAREN.sub(" ", s)          # drop "(...)" (cities / states / counts)
    s = s.replace("/", " ")          # "United Kingdom/Europe" -> two words
    seen, out = set(), []
    for m in _PATTERN.finditer(s):
        canon = _SPELL2CANON[m.group(1).lower()]
        if canon not in seen:
            seen.add(canon); out.append(canon)
    return "[" + ", ".join(out) + "]"


if __name__ == "__main__":
    # quick self-check on the tricky observed inputs
    tests = [
        "Singapore; Hong Kong SAR; China; Japan; South Korea",
        "The Netherlands, France, Italy, Germany, Poland, Denmark, Czech Republic, United Kingdom, Finland (pan-European)",
        "United Kingdom (England, Scotland, Wales)",
        "Singapore, Australia, United States, United Kingdom/Europe",
        "China (Beijing, Guangzhou, Chengdu, Hohhot, Harbin, Suzhou, Hangzhou, Xi'an, Shanghai, Wuhan, Kunshan)",
        "United States (32 hotels across 17 states)",
        "Singapore Australia",
        "United States of America",
        "The Philippines",
        "[Singapore, Australia]",
        None, "",
    ]
    for t in tests:
        print(f"{t!r:90} -> {normalize_locations(t)!r}")
