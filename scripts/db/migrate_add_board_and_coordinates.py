"""Dev-only schema migration (RAW tables). NEVER touches prod.

Adds:
  sgx_reit_profile.board                jsonb   -- [{name, position}] board of the REIT Manager
  sgx_reit_property.coordinate_latitude  numeric
  sgx_reit_property.coordinate_longitude numeric
  sgx_reit_property.coordinate_source    text    -- geocoder id (dropped on prod promote)

Idempotent (ADD COLUMN IF NOT EXISTS). Reads SUPABASE_CONNECTION_STRING (dev only).
DRY by default; pass --write to apply.
"""
import os, sys
import psycopg2
from dotenv import load_dotenv

load_dotenv('.env')
WRITE = '--write' in sys.argv

DDL = [
    ("sgx_reit_profile",  "board",                 "jsonb"),
    ("sgx_reit_property", "coordinate_latitude",   "numeric"),
    ("sgx_reit_property", "coordinate_longitude",  "numeric"),
    ("sgx_reit_property", "coordinate_source",     "text"),
]

conn = psycopg2.connect(os.environ['SUPABASE_CONNECTION_STRING'])
conn.autocommit = False
cur = conn.cursor()

# guardrail: make sure we are NOT pointed at prod (prod is REST-only; this var is dev)
cur.execute("select current_database()")
print("connected db:", cur.fetchone()[0])

for table, col, typ in DDL:
    stmt = f"alter table public.{table} add column if not exists {col} {typ}"
    print(("[WRITE] " if WRITE else "[DRY]   ") + stmt)
    if WRITE:
        cur.execute(stmt)

# verify
for table in ("sgx_reit_profile", "sgx_reit_property"):
    cur.execute(
        "select column_name, data_type from information_schema.columns "
        "where table_name=%s and column_name in "
        "('board','coordinate_latitude','coordinate_longitude','coordinate_source') "
        "order by column_name", (table,))
    print(f"  {table}:", cur.fetchall())

if WRITE:
    conn.commit(); print("COMMITTED (dev only).")
else:
    conn.rollback(); print("DRY RUN — nothing written. Re-run with --write.")
conn.close()
