"""Rename the BHG Retail REIT ticker BMOU -> BMGU across the DB and the working tree.

BMOU is not an SGX ticker. BHG Retail REIT trades as BMGU (verified against SGX/REITAS,
2026-07-31). The wrong code was used from the original ingest onward, so it is present in dev,
prod, the annual-report filenames, the parsed folders and the extraction output.

Scope:
  dev   (SUPABASE_CONNECTION_STRING)  every table with a `symbol` column holding 'BMOU%'
                                       -> symbol 'BMOU.SI' becomes 'BMGU.SI'
  prod  (SUPABASE_URL + KEY)           the 6 sgx_reit_* tables -> 'BMOU' becomes 'BMGU'
  files                                active directories renamed + their text contents rewritten

NOT touched (historical records, deliberately left as-is):
  backup/**            point-in-time snapshots; rewriting them destroys their value as a baseline
  docs/**              earlier findings docs are a record of what was believed at the time
  .git/**

Usage:
  python scripts/db/rename_bmou_to_bmgu.py                # DRY RUN (default)
  python scripts/db/rename_bmou_to_bmgu.py --write        # apply everything
  python scripts/db/rename_bmou_to_bmgu.py --write --db-only
  python scripts/db/rename_bmou_to_bmgu.py --write --files-only

DRY BY DEFAULT. Nothing changes without --write.
After applying: re-run the extraction manifest check, then rebuild _final and re-promote.
"""
import os, sys, argparse, glob, shutil
import psycopg2
from dotenv import load_dotenv

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(ROOT, ".env"))

OLD, NEW = "BMOU", "BMGU"
PROD_TABLES = ["sgx_reit_profile", "sgx_reit_performance", "sgx_reit_property",
               "sgx_reit_top_tenant", "sgx_reit_trade_mix", "sgx_reit_property_transaction"]
# Only these trees are rewritten. backup/ and docs/ are historical and stay untouched.
ACTIVE_DIRS = ["annual_reports", "annual_reports_pdf_manual", "extracted", "extracted_adapter",
               "parsed_reports_datalab", "value"]
TEXT_EXT = {".json", ".csv", ".md", ".txt", ".jsonl"}


def parse_args():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--write", action="store_true", help="apply (default: dry run)")
    ap.add_argument("--db-only", action="store_true")
    ap.add_argument("--files-only", action="store_true")
    return ap.parse_args()


def dev_plan(cur):
    cur.execute("""select table_name from information_schema.columns
                    where column_name = 'symbol' and table_schema = 'public'
                    order by table_name""")
    plan = []
    for (t,) in cur.fetchall():
        try:
            cur.execute(f"select count(*) from {t} where symbol like %s", (OLD + "%",))
            n = cur.fetchone()[0]
            if n:
                plan.append((t, n))
        except Exception:
            cur.connection.rollback()
    return plan


def file_plan():
    """Return (dirs_to_rename, files_to_rename, files_to_rewrite)."""
    dirs, files, rewrite = [], [], []
    for d in ACTIVE_DIRS:
        base = os.path.join(ROOT, d)
        if not os.path.isdir(base):
            continue
        for p in glob.glob(os.path.join(base, "**", "*"), recursive=True):
            rel = os.path.relpath(p, ROOT)
            if OLD in os.path.basename(p):
                (dirs if os.path.isdir(p) else files).append(rel)
            if os.path.isfile(p) and os.path.splitext(p)[1].lower() in TEXT_EXT:
                try:
                    with open(p, encoding="utf-8", errors="ignore") as fh:
                        if OLD in fh.read():
                            rewrite.append(rel)
                except OSError:
                    pass
    # deepest paths first so renaming a child never invalidates a queued parent path
    dirs.sort(key=lambda s: s.count(os.sep), reverse=True)
    return dirs, files, sorted(set(rewrite))


def main():
    args = parse_args()
    do_db = not args.files_only
    do_files = not args.db_only

    print("=" * 74)
    print(f"RENAME  {OLD} -> {NEW}   (BHG Retail REIT)" + ("  [--write]" if args.write else "  [DRY RUN]"))
    print("=" * 74)

    dev, prod_counts = [], {}
    if do_db:
        cn = psycopg2.connect(os.environ["SUPABASE_CONNECTION_STRING"])
        cur = cn.cursor()
        dev = dev_plan(cur)
        print(f"\nDEV tables ({sum(n for _, n in dev)} rows across {len(dev)} tables):")
        for t, n in dev:
            print(f"   {t:42s}{n:>6d}")

        from supabase import create_client
        sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])
        print("\nPROD tables:")
        for t in PROD_TABLES:
            try:
                rows = sb.table(t).select("*").eq("symbol", OLD).execute().data
                prod_counts[t] = rows
                print(f"   {t:42s}{len(rows):>6d}")
            except Exception as exc:
                print(f"   {t:42s} ERR {exc}")

    dirs = files = rewrite = []
    if do_files:
        dirs, files, rewrite = file_plan()
        print(f"\nFILES  dirs to rename {len(dirs)} · files to rename {len(files)} · "
              f"files to rewrite {len(rewrite)}")
        for p in dirs + files:
            print(f"   RENAME  {p}")
            print(f"        -> {p.replace(OLD, NEW)}")
        for p in rewrite[:12]:
            print(f"   REWRITE {p}")
        if len(rewrite) > 12:
            print(f"   ... and {len(rewrite) - 12} more")

    if not args.write:
        print("\nDRY RUN — nothing changed. Re-run with --write to apply.")
        return 0

    if do_db:
        try:
            for t, _ in dev:
                cur.execute(f"update {t} set symbol = replace(symbol, %s, %s) "
                            f"where symbol like %s", (OLD, NEW, OLD + "%"))
            cn.commit()
            print(f"\nDEV updated: {len(dev)} tables.")
        except Exception as exc:
            cn.rollback()
            print(f"\nDEV ROLLED BACK — {exc}")
            raise
        # prod is REST and non-transactional: update row by row, report failures loudly
        failed = []
        for t, rows in prod_counts.items():
            for r in rows:
                try:
                    q = sb.table(t).update({"symbol": NEW}).eq("symbol", OLD)
                    if "financial_year" in r and r["financial_year"] is not None:
                        q = q.eq("financial_year", r["financial_year"])
                    q.execute()
                except Exception as exc:
                    failed.append((t, exc))
        print(f"PROD updated: {sum(len(v) for v in prod_counts.values())} rows"
              + (f", {len(failed)} FAILED" if failed else ""))
        for t, exc in failed[:10]:
            print(f"   FAILED {t}: {exc}")

    if do_files:
        for p in rewrite:
            ap_ = os.path.join(ROOT, p)
            with open(ap_, encoding="utf-8") as fh:
                txt = fh.read()
            with open(ap_, "w", encoding="utf-8") as fh:
                fh.write(txt.replace(OLD, NEW))
        for p in files + dirs:                       # files first, then dirs (deepest-first)
            src = os.path.join(ROOT, p)
            dst = os.path.join(ROOT, p.replace(OLD, NEW))
            if os.path.exists(src):
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.move(src, dst)
        print(f"FILES: {len(rewrite)} rewritten, {len(files) + len(dirs)} renamed.")

    print("\nNext: verify the manifest, rebuild _final, re-promote.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
