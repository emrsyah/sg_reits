#!/usr/bin/env python3
"""Apply db/schema.sql to Supabase Postgres. Idempotent. Uses SUPABASE_CONNECTION_STRING."""
import os, sys, pathlib
import psycopg2
from dotenv import load_dotenv

ROOT = pathlib.Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

dsn = os.environ["SUPABASE_CONNECTION_STRING"]
sql = (ROOT / "db" / "schema.sql").read_text(encoding="utf-8")

conn = psycopg2.connect(dsn)
conn.autocommit = True
with conn.cursor() as cur:
    cur.execute(sql)
    cur.execute("""
        select table_name from information_schema.tables
        where table_schema='public' and table_name like 'sgx_reit_%' or table_name like 'reit_%'
        order by table_name
    """)
    tables = [r[0] for r in cur.fetchall()]
conn.close()
print("schema applied. tables present:")
for t in tables:
    print("  ", t)
