#!/usr/bin/env python3
"""Rebuild an accurate manifest from the PDFs actually on disk, and report gaps."""
import os, csv, re

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "annual_reports")

# Reports that genuinely DO NOT exist (entity not listed / FY not yet published) -> expected-absent
NOT_EXIST = {
    (1, 2025), (3, 2025), (4, 2025), (10, 2025), (25, 2025), (32, 2025), (34, 2025),  # FY2025 not yet published
    (11, 2023), (11, 2024),                                                            # Centurion not listed
    (30, 2023), (30, 2024), (30, 2025),                                                # NTT DC not listed / AR not out
    (38, 2023), (38, 2024), (38, 2025),                                                # UI Boustead not listed
}
# Reports that exist but we could not obtain a direct PDF for
KNOWN_GAP = {(29, 2023): "MPACT FY2022/23 AR PDF removed in IR site migration; SGX hash not indexed"}

SYMBOLS = {
    1:"XZL.SI",2:"O5RU.SI",3:"M1GU.SI",4:"BMOU.SI",5:"A17U.SI",6:"HMN.SI",7:"AU8U.SI",8:"CY6U.SI",
    9:"C38U.SI",10:"J85.SI",11:"8C8U.SI",12:"DHLU.SI",13:"DCRU.SI",14:"MXNU.SI",15:"J91U.SI",16:"Q5T.SI",
    17:"AW9U.SI",18:"J69U.SI",19:"BUOU.SI",20:"UD1U.SI",21:"AJBU.SI",22:"CMOU.SI",23:"K71U.SI",24:"JYEU.SI",
    25:"D5IU.SI",26:"BTOU.SI",27:"ME8U.SI",28:"M44U.SI",29:"N2IU.SI",30:"NTDU.SI",31:"TS0U.SI",32:"C2PU.SI",
    33:"OXMU.SI",34:"CRPU.SI",35:"P40U.SI",36:"SET.SI",37:"T82U.SI",38:"UIBU.SI",39:"ODBU.SI",
}

present = {}  # (id, year) -> (filename, size)
pat = re.compile(r"^(\d{2})_([^_]+)_(.+)_FY(\d{4})\.pdf$")
for f in os.listdir(OUT):
    m = pat.match(f)
    if m:
        rid, yr = int(m.group(1)), int(m.group(4))
        present[(rid, yr)] = (f, os.path.getsize(os.path.join(OUT, f)))

rows = []
for rid in range(1, 40):
    for yr in (2023, 2024, 2025):
        key = (rid, yr)
        if key in present:
            fn, sz = present[key]
            rows.append([rid, SYMBOLS[rid], fn, yr, "DOWNLOADED", f"{sz/1_000_000:.1f} MB"])
        elif key in NOT_EXIST:
            rows.append([rid, SYMBOLS[rid], "", yr, "NOT_PUBLISHED", "entity not listed / FY not yet released"])
        elif key in KNOWN_GAP:
            rows.append([rid, SYMBOLS[rid], "", yr, "MISSING", KNOWN_GAP[key]])
        else:
            rows.append([rid, SYMBOLS[rid], "", yr, "MISSING", "no direct PDF obtained"])

with open(os.path.join(OUT, "_manifest.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["id", "symbol", "filename", "fiscal_year", "status", "detail"])
    w.writerows(rows)

dl = sum(1 for r in rows if r[4] == "DOWNLOADED")
nx = sum(1 for r in rows if r[4] == "NOT_PUBLISHED")
ms = sum(1 for r in rows if r[4] == "MISSING")
print(f"Downloaded: {dl} | Not-published/NA: {nx} | Missing: {ms} | Total slots: {len(rows)}")
print(f"Reports that exist and were obtained: {dl} / {dl + ms}")
if ms:
    print("\nMISSING (exist but not obtained):")
    for r in rows:
        if r[4] == "MISSING":
            print(f"  id {r[0]:>2} {r[1]:<9} FY{r[3]} - {r[5]}")
