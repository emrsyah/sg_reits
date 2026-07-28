import re, sys
raw = open('parsed_reports_datalab/29_N2IU.SI_Mapletree-Pan-Asia-Commercial-Trust_FY2025_new/full.md', encoding='utf-8').read()
m = [(x.start(), int(x.group(1))) for x in re.finditer(r'<!--\s*PAGE\s+(\d+)\s*-->', raw)]
P = {}
for i, (pos, n) in enumerate(m):
    e = m[i+1][0] if i+1 < len(m) else len(raw)
    P[n] = re.sub(r'^<!--\s*PAGE\s+\d+\s*-->', '', raw[pos:e])
if __name__ == '__main__':
    args = sys.argv[1:]
    for a in args:
        if '-' in a:
            lo, hi = a.split('-'); rng = range(int(lo), int(hi)+1)
        else:
            rng = [int(a)]
        for pg in rng:
            print(f'==================== PAGE {pg} ====================')
            print(P.get(pg, '<<missing>>'))
