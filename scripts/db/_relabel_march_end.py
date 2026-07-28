"""Relabel March-end SGX REITs from date.year convention to declared-FY (fy=fy-1).

Scope THIS RUN: M44U, ME8U, N2IU, O5RU only (June-end deferred).
Actions:
  (a) UPDATE financial_year=financial_year-1 across raw financial_year-keyed tables.
  (b) Rename extracted/<sym>_FY<Y> folders lowest-year-first and rewrite the
      top-level "financial_year" field in every JSON inside.
EXCLUDES: sgx_manual_input, all *_final (rebuilt separately).

DRY by default; pass --write to commit both DB and folder changes.
"""
import os, sys, json, glob
import psycopg2
from dotenv import load_dotenv

WRITE = "--write" in sys.argv
load_dotenv(".env")

SYMBOLS = (["JYEU.SI", "P40U.SI"] if "--june" in sys.argv
           else ["M44U.SI", "ME8U.SI", "N2IU.SI", "O5RU.SI"])
TABLES = [
    "sgx_reit_performance", "sgx_reit_financial", "sgx_reit_property",
    "sgx_reit_top_tenant", "sgx_reit_trade_mix", "sgx_reit_property_transaction",
    "sgx_reit_notes", "sgx_reit_doc_chunk", "reit_report",
]

conn = psycopg2.connect(os.environ["SUPABASE_CONNECTION_STRING"])
cur = conn.cursor()

def snapshot(label):
    print(f"\n=== {label} ===")
    for t in TABLES:
        cur.execute(
            f"select symbol, financial_year, count(*) from {t} "
            f"where symbol = any(%s) group by symbol, financial_year "
            f"order by symbol, financial_year", (SYMBOLS,))
        rows = cur.fetchall()
        summ = ", ".join(f"{s.split('.')[0]}:FY{fy}={n}" for s, fy, n in rows)
        print(f"  {t:32} {summ}")

snapshot("BEFORE (raw)")

# guard: confirm sgx_manual_input + *_final untouched targets exist
print("\n=== EXCLUDED (should NOT change) ===")
for t in ["sgx_manual_input", "sgx_reit_property_final"]:
    cur.execute(f"select symbol, financial_year, count(*) from {t} "
                f"where symbol = any(%s) group by symbol, financial_year "
                f"order by symbol, financial_year", (SYMBOLS,))
    rows = cur.fetchall()
    print(f"  {t:32} " + ", ".join(f"{s.split('.')[0]}:FY{fy}={n}" for s, fy, n in rows))

if WRITE:
    for t in TABLES:
        total = 0
        # ascending year: vacate target slot before shifting next year (avoids
        # transient unique-constraint collision, checked per-row in Postgres)
        for yr in (2024, 2025):
            cur.execute(
                f"update {t} set financial_year = financial_year - 1 "
                f"where symbol = any(%s) and financial_year = %s", (SYMBOLS, yr))
            total += cur.rowcount
        print(f"  UPDATE {t}: {total} rows")
    conn.commit()
    snapshot("AFTER (raw)")
else:
    print("\n(DRY: no DB UPDATE performed)")

# ---------- folder rename + JSON financial_year rewrite ----------
# rename lowest-year-first to avoid collision
rename_plan = []
for sym in SYMBOLS:
    dirs = sorted(glob.glob(f"extracted/{sym}_FY*"))  # ascending year
    for d in dirs:
        old_fy = int(d.rsplit("_FY", 1)[1])
        new_fy = old_fy - 1
        new_d = f"extracted/{sym}_FY{new_fy}"
        rename_plan.append((d, new_d, old_fy, new_fy))

print("\n=== FOLDER RENAME PLAN ===")
for old, new, ofy, nfy in rename_plan:
    print(f"  {old} -> {new}")

if WRITE:
    for old, new, ofy, nfy in rename_plan:
        if not os.path.isdir(old):
            print(f"  SKIP missing {old}")
            continue
        os.rename(old, new)
        # rewrite financial_year in every JSON inside
        for jf in glob.glob(os.path.join(new, "*.json")):
            with open(jf, "r", encoding="utf-8") as fh:
                obj = json.load(fh)
            if isinstance(obj, dict) and obj.get("financial_year") == ofy:
                obj["financial_year"] = nfy
                with open(jf, "w", encoding="utf-8") as fh:
                    json.dump(obj, fh, indent=2, ensure_ascii=False)
        print(f"  RENAMED {old} -> {new}  (+JSON financial_year {ofy}->{nfy})")
else:
    print("\n(DRY: no folder rename performed)")

cur.close(); conn.close()
