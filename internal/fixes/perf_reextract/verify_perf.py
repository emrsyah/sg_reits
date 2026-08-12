"""Verify the re-extracted performance rows.

Three independent passes, none of which trusts the agents:
  1. CITATIONS  every non-null figure must appear near its cited line in full.md
  2. GATES      re-run the rollforward and declared gates ourselves
  3. DIFF       compare against extracted/*/performance.json and rank by impact

Usage:  python verify_perf.py batch*.json
"""
import json, re, sys, glob, os

ROOT = r'C:\Users\emirsyah\orca\workspaces\s_reits\sgx-reit-performance'
PARSED = os.path.join(ROOT, 'parsed_reports_datalab')

# (symbol, declared_fy) -> folder.  Folder labels run one behind for ME8U/M44U/N2IU.
OFFSET = {'ME8U', 'M44U', 'N2IU'}
FOLDER = {}
for d in glob.glob(os.path.join(PARSED, '*_FY20*')):
    b = os.path.basename(d)
    sym = b.split('_')[1].split('.')[0]
    lbl = int(b.rsplit('FY', 1)[1])
    FOLDER[(sym, lbl + 1 if sym in OFFSET else lbl)] = d
    FOLDER[(sym, lbl)] = FOLDER.get((sym, lbl), d)   # tolerate either convention

_cache = {}
def lines(folder):
    if folder not in _cache:
        with open(os.path.join(folder, 'full.md'), encoding='utf-8', errors='replace') as f:
            _cache[folder] = f.read().split('\n')
    return _cache[folder]

def flat(s):
    return re.sub(r'[,\s]', '', re.sub(r'<[^>]+>', '', s))

MONEY = ['opening', 'income_for_year', 'other_additions', 'amount_retained',
         'distribution_paid', 'closing', 'distribution_declared']

def check_citations(r, out):
    key = (r['symbol'], r['financial_year'])
    folder = FOLDER.get(key)
    if not folder:
        out.append((r['symbol'], r['financial_year'], 'ALL', 'NO_FOLDER', str(key))); return
    L = lines(folder)
    for f in MONEY + ['dpu', 'units_in_issue', 'number_of_unitholders']:
        v = r.get(f)
        if v in (None, 0):
            continue
        ln = r.get(f + '_line')
        if not ln:
            out.append((r['symbol'], r['financial_year'], f, 'NO_LINE', str(v))); continue
        win = flat('\n'.join(L[max(0, ln - 5): ln + 5]))
        # money may be printed in thousands, or as an absolute; dpu as-is
        cands = {f"{v:.0f}", f"{v/1000:.0f}", f"{v/1000000:.0f}", f"{v:g}"}
        if not any(c in win for c in cands if c not in ('0',)):
            whole = flat('\n'.join(L))
            where = 'elsewhere' if any(c in whole for c in cands) else 'NOWHERE'
            out.append((r['symbol'], r['financial_year'], f, 'NOT_AT_LINE', f'{v:,} L{ln} ({where})'))

def gates(r):
    g = lambda k: r.get(k) or 0
    res = {}
    if r.get('opening') is not None and r.get('closing') is not None:
        lhs = g('opening') + g('income_for_year') + g('other_additions') \
              - g('amount_retained') - g('distribution_paid')
        res['gate1'] = abs(lhs - r['closing']) <= max(1000, abs(r['closing']) * 0.005)
        res['gate1_gap'] = lhs - r['closing']
    else:
        res['gate1'] = None
    dec = r.get('distribution_declared')
    if dec:
        pred = g('income_for_year') + g('other_additions') - g('amount_retained')
        res['gate2_err'] = (dec - pred) / pred * 100 if pred else None
        res['gate2'] = res['gate2_err'] is not None and abs(res['gate2_err']) < 0.5
    else:
        res['gate2'] = None
    return res

def main(paths):
    recs = []
    for p in paths:
        for pp in glob.glob(p):
            recs.extend(json.load(open(pp, encoding='utf-8')))
    print(f'{len(recs)} rows re-extracted\n')

    cit = []
    for r in recs:
        check_citations(r, cit)
    print(f'--- CITATIONS: {len(cit)} problems')
    for c in cit[:40]:
        print(f'    {c[0]}/{c[1]} {c[2]:24} {c[3]:12} {c[4]}')

    print('\n--- GATES')
    g1f = g2f = 0
    for r in recs:
        res = gates(r)
        r['_g'] = res
        if res['gate1'] is False: g1f += 1
        if res['gate2'] is False: g2f += 1
    n1 = sum(1 for r in recs if r['_g']['gate1'] is not None)
    n2 = sum(1 for r in recs if r['_g']['gate2'] is not None)
    print(f'    gate1 rollforward : {n1-g1f}/{n1} pass   ({g1f} fail)')
    print(f'    gate2 declared    : {n2-g2f}/{n2} pass   ({g2f} fail)')
    for r in recs:
        res = r['_g']
        if res['gate1'] is False:
            print(f"    G1 FAIL {r['symbol']}/{r['financial_year']}  gap {res['gate1_gap']:,.0f}")
        if res['gate2'] is False:
            print(f"    G2 FAIL {r['symbol']}/{r['financial_year']}  err {res['gate2_err']:.2f}%")

    print('\n--- DIFF vs current extracted/')
    MAP = {'opening': 'distributable_income_opening', 'income_for_year': 'net_distributable_income',
           'distribution_paid': 'distribution_cash_paid', 'closing': 'distributable_income_closing',
           'distribution_declared': 'distribution_paid', 'dpu': 'dpu',
           'units_in_issue': 'number_of_shareholder_units'}
    diffs = []
    for r in recs:
        p = os.path.join(ROOT, 'extracted', f"{r['symbol']}.SI_FY{r['financial_year']}", 'performance.json')
        if not os.path.exists(p):
            diffs.append((r['symbol'], r['financial_year'], 'ROW', None, None, 999)); continue
        old = json.load(open(p, encoding='utf-8'))
        for new_k, old_k in MAP.items():
            nv, ov = r.get(new_k), old.get(old_k)
            if nv is None and ov is None: continue
            if ov in (None, 0) and nv: diffs.append((r['symbol'], r['financial_year'], new_k, ov, nv, 100)); continue
            if nv is None or ov in (None, 0): continue
            d = abs(nv - ov) / abs(ov) * 100
            if d > 0.5: diffs.append((r['symbol'], r['financial_year'], new_k, ov, nv, d))
    diffs.sort(key=lambda x: -x[5])
    print(f'    {len(diffs)} material differences (>0.5%)')
    for s, fy, f, ov, nv, d in diffs[:45]:
        o = 'null' if ov is None else f'{ov:,.0f}'
        n = 'null' if nv is None else f'{nv:,.0f}'
        print(f'    {s}/{fy} {f:24} was {o:>18}  now {n:>18}')
    return recs

if __name__ == '__main__':
    main(sys.argv[1:] or ['batch*.json'])
