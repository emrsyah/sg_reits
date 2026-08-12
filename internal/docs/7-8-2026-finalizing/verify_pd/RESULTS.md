# purchase_date Extraction Results (2026-07-08)

10 gap REITs, `sonic` agents, read-only extraction of per-property acquisition/purchase dates.
**As-disclosed only.** Split into verbatim (applied) / IPO-listing-date proxy (HELD for decision) / null.

## ✅ Applied — verbatim per-property dates (7 new fills, JSON+DB)
- **ODBU** (3): Colonial Square 2021-11-12, Penrose Plaza 2021-11-24, Upland Square 2022-07-28.
  Corroborated by the AR's SPV names ("UH US Colonial Square **2021** LLC", "Penrose **2021**",
  "Upland **2022**") — not a positional artifact. (Dover 2025-08-01 already filled.)
- **DCRU** (3): 200 North Nash St 2024-10-01, 3015 Winona Ave 2024-10-01 (LA ops takeover),
  Wilhelm-Fay-Straße 2024-12-05 (change-of-control). (Osaka 3 2025-03-26 already filled.)
- **JYEU** (1): Jem 2021-08-04 (fund holding Jem acquired, p144 note 8).
- Already-filled (no-op, confirmed correct): CY6U (aVance II 2024, Building Q2 2024, Navi Mumbai 2021),
  Q5T (Nagoya 2025-04-25), MXNU (Custom House/Merlin House/Priory Court 2025-06-20), DHLU (19/19 filled
  earlier), AJBU (Tokyo DC3 2025-11-19, Tokyo DC1 2024, KDC SGP7/8 2024).

## ⏳ HELD — IPO / listing-date proxy (needs emirsyah decision)
These initial-portfolio rows have NO per-property acquisition date printed; the only disclosed date is
the trust's **Listing Date**. The trust acquired the initial portfolio at/around listing, so the
listing date is a defensible `purchase_date` — but it is NOT a literal per-property acquisition date
(borderline vs as-disclosed-only). **Decision: apply listing date as purchase_date, or leave null?**
- **ODBU** ~18 rows → 2020-03-12 (IPO listing)
- **BMOU** 5 rows → 2015-12-11 (Hefei Changjiangxilu = later acquisition, no date → null)
- **DCRU** 6 rows → 2021-12-06 (original US/Canada IPO assets)
- **JYEU** 2 rows → 2019-10-02 (313@somerset, Sky Complex — IPO initial portfolio)
Total ~31 rows.

## ⛔ Not disclosed → left null (as-disclosed)
- **HMN** 100 legacy hospitality rows (only 5 FY2025 acquisitions dated, already filled) — no per-asset
  acquisition dates disclosed.
- **MXNU** 145 UK rows (only 3 FY2025 acquisitions dated, already filled) — no acquisition-date column.
- **AJBU** 22 rows (no per-property date column; only 4 recent acquisitions, already filled).
- **UD1U** 8 Campus/Delta-Nova/Sant-Cugat rows — only building-completion dates disclosed, not acquisition.
- **CY6U** ~15, **Q5T** 12, **DCRU** Digital Osaka 2 — not disclosed.
