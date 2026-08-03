"""Load fixes/perf_reextract/_final.json into the DEV sgx_reit_performance table.

UPDATE only — never INSERT or DELETE. The re-extraction covered the distribution
flow and units; every other column on the row (portfolio_value, gross_revenue,
NPI, the KPI block, properties_location, source_url) was untouched by it and must
survive.

DEV ONLY. This script reads SUPABASE_CONNECTION_STRING and nothing else, so it
cannot reach prod even by accident.

    python scripts/db/load_perf_reextract.py            # dry run
    python scripts/db/load_perf_reextract.py --write
"""
import argparse, json, os, re, sys
from decimal import Decimal
import psycopg2
from psycopg2.extras import Json

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, 'fixes', 'perf_reextract', '_final.json')

# _final.json key -> dev column
FIELDS = {
    'opening':                    'distributable_income_opening',
    'closing':                    'distributable_income_closing',
    'income_for_year':            'income_for_year',
    'income_for_year_basis':      'income_for_year_basis',
    'other_additions':            'other_additions',
    'other_additions_label':      'other_additions_label',
    'other_additions_breakdown':  'other_additions_breakdown',
    'amount_retained':            'amount_retained',
    'distribution_paid':          'distribution_paid',
    'distribution_declared':      'distribution_declared',
    'paid_in_units':              'paid_in_units',
    'dpu':                        'dpu',
    'distribution_record':        'distribution_record',
    'distribution_period_months': 'dpu_period_months',
    'units_in_issue':             'units_in_issue',
    'units_to_be_issued':         'units_to_be_issued',
    'number_of_unitholders':      'number_of_unitholders',
    'fy_end_date':                'fy_end_date',
    'currency':                   'currency',
}
JSONB = {'distribution_record', 'other_additions_breakdown'}


def conn():
    cs = os.environ.get('SUPABASE_CONNECTION_STRING')
    if not cs:
        env = os.path.join(os.path.dirname(ROOT), '.env')
        for cand in (env, r'C:\Users\emirsyah\supertype\s_reits\.env'):
            if os.path.exists(cand):
                m = re.findall(r'^SUPABASE_CONNECTION_STRING=(.*)$',
                               open(cand, encoding='utf-8').read(), re.M)
                if m:
                    cs = m[-1].strip().strip('"').strip("'")
                    break
    if not cs:
        sys.exit('SUPABASE_CONNECTION_STRING not found — refusing to guess.')
    return psycopg2.connect(cs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true', help='apply (default: dry run)')
    a = ap.parse_args()

    rows = json.load(open(SRC, encoding='utf-8'))
    c = conn()
    cur = c.cursor()

    cur.execute("select column_name from information_schema.columns "
                "where table_name='sgx_reit_performance'")
    have = {r[0] for r in cur.fetchall()}
    missing = sorted(set(FIELDS.values()) - have)
    if missing:
        sys.exit(f'dev table is missing {missing} — run the migration first.')

    cur.execute('select symbol,financial_year from sgx_reit_performance')
    existing = {(s, f) for s, f in cur.fetchall()}

    changed = skipped = 0
    unknown = []
    for r in rows:
        key = (r['symbol'] + '.SI' if not r['symbol'].endswith('.SI') else r['symbol'],
               r['financial_year'])
        # dev stores symbols with or without .SI depending on vintage; try both
        k = key if key in existing else (r['symbol'], r['financial_year'])
        if k not in existing:
            unknown.append(f"{r['symbol']}/{r['financial_year']}")
            continue
        sets, vals = [], []
        for src, col in FIELDS.items():
            if src not in r:
                continue
            v = r[src]
            sets.append(f'{col}=%s')
            vals.append(Json(v) if src in JSONB and v is not None else v)
        if not sets:
            skipped += 1
            continue
        vals += [k[0], k[1]]
        if a.write:
            cur.execute(f'update sgx_reit_performance set {", ".join(sets)} '
                        f'where symbol=%s and financial_year=%s', vals)
        changed += 1

    if unknown:
        print(f'  NOT FOUND in dev ({len(unknown)}): {", ".join(unknown)}')
    print(f'  rows matched: {changed}   skipped: {skipped}')

    if a.write:
        c.commit()
        print('  COMMITTED')
    else:
        c.rollback()
        print('  dry run — nothing written (pass --write to apply)')
    c.close()


if __name__ == '__main__':
    main()
