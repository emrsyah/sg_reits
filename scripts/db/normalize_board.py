"""Post-extraction normalization sweep for sgx_reit_profile.board (DEV only; prod untouched).

Batches extracted names inconsistently (some kept 'Mr/Ms/Dr', some stripped). This makes
every board uniform:
  - strip leading honorifics (Mr Mrs Ms Mdm Dr Prof Professor) from `name`
  - decode any stray &amp; HTML entities in name/position
  - apply known OCR corrections
  - report coverage + any anomalies

DRY by default; --write to apply.
"""
import os, sys, re, html, json
import psycopg2
from psycopg2.extras import Json
from dotenv import load_dotenv

load_dotenv('.env')
WRITE = '--write' in sys.argv

HONORIFIC = re.compile(r"^\s*(?:(?:Mr|Mrs|Ms|Mdm|Madam|Dr|Prof|Professor|Mr\.|Ms\.|Dr\.)\s+)+", re.I)
# known OCR / spelling corrections (name-as-stored -> corrected), applied per symbol
CORRECTIONS = {
    ("K71U.SI", "Tan Swee Yow"): "Tan Swee Yiow",
}

def clean_name(sym, n):
    n = html.unescape(n).strip()
    n = HONORIFIC.sub("", n).strip()
    return CORRECTIONS.get((sym, n), n)

conn = psycopg2.connect(os.environ['SUPABASE_CONNECTION_STRING']); conn.autocommit = False
cur = conn.cursor()
cur.execute("select current_database()"); print("db:", cur.fetchone()[0], "| mode:", "WRITE" if WRITE else "DRY")

cur.execute("select symbol, board from sgx_reit_profile order by symbol")
rows = cur.fetchall()
total_people = changed_names = 0
with_board = 0
anomalies = []
updates = []
for sym, board in rows:
    if not board:
        anomalies.append(f"{sym}: NO board"); continue
    with_board += 1
    new = []
    dirty = False
    seen = set()
    for p in board:
        total_people += 1
        nm0 = p.get("name", "")
        nm = clean_name(sym, nm0)
        pos = html.unescape(p.get("position", "")).strip()
        if nm != nm0 or pos != p.get("position", ""):
            dirty = True
            if nm != nm0: changed_names += 1
        if not nm or not pos:
            anomalies.append(f"{sym}: empty name/position -> {p}")
        if nm.lower() in seen:
            anomalies.append(f"{sym}: DUPLICATE name '{nm}'")
        seen.add(nm.lower())
        e = {"name": nm, "position": pos}
        if "source_page" in p: e["source_page"] = p["source_page"]
        new.append(e)
    if dirty:
        updates.append((sym, new))

print(f"\nREITs with board: {with_board}/{len(rows)}")
print(f"total people: {total_people} | names to normalize: {changed_names} | rows to rewrite: {len(updates)}")
if anomalies:
    print("\nANOMALIES:")
    for a in anomalies: print("  ", a)
else:
    print("no anomalies (no empties / no in-REIT duplicates)")

if WRITE and updates:
    for sym, new in updates:
        cur.execute("update sgx_reit_profile set board=%s::jsonb where symbol=%s", (Json(new), sym))
    conn.commit(); print(f"\nCOMMITTED: normalized {len(updates)} REITs.")
elif not WRITE:
    conn.rollback(); print("\n(DRY RUN — nothing written.)")
conn.close()
