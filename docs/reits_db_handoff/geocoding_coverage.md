# Property geocoding — coverage & the China gap

**Status (2026-07-28):** property coordinates added to `sgx_reit_property` as three columns
`coordinate_latitude`, `coordinate_longitude`, `coordinate_source` (dev DB; prod gets only
lat/long, not `coordinate_source`). All WGS-84. Misses are left **NULL** — never fabricated.

## Coverage: 3,284 / 3,420 rows = **96%**

| Region | Source | Result |
|---|---|---|
| Singapore | OneMap (`geocode_onemap_sg.py` + `_squeeze.py`) | 850 / 866 (98%) |
| Non-SG | OpenCage (`geocode_opencage_intl.py` + `_squeeze.py`) | ~2,434 (94%) |
| Non-SG residual | Nominatim/OSM (`geocode_nominatim_squeeze.py`) | +1 only |

Confidence tags live in the `geo_cache` table (`exact`, `postal`, `first_block`, OpenCage
numeric `0-10`, `cleanup`, `cleanup_poi` = name-only POI match worth reviewing, `osm:*`).

## Remaining 136 NULL rows (as of 2026-07-28)

| Country | NULL rows | Why |
|---|--:|---|
| **China** | **64** | OSM/OpenCage/Nominatim all lack China street-level data (see below) |
| Indonesia | 18 | sparse / name-only (mall units with no street address) |
| Vietnam | 14 | industrial-park lot addresses ("Lot P1-CN2, … Industrial Park") |
| Japan | 8 | name-only residences |
| Malaysia 5, India 4, Hong Kong 3, others ~4 | ~16 | sparse addresses |
| Singapore | 16 | multi-block sites with no postal ("1, 3 & 5 Kallang Sector") |

## The China gap — needs Amap/Gaode (BLOCKED)

The 64 China rows have valid romanized addresses (e.g. "No. 38 Aidemengdun Road, Daoli
District, Harbin") but **no free WGS-84 geocoder can resolve them** — OpenCage and Nominatim
both draw on OpenStreetMap, whose China coverage is thin. The accurate fix is a China-native
geocoder (**Amap/Gaode** or Baidu), which returns **GCJ-02** coordinates that must be
converted to WGS-84 before storing (libraries: `eviltransform`, `prcoords`).

**BLOCKER:** registering for an Amap API key requires a **Chinese mobile number**, which we
don't have. So China is deferred until we can either (a) obtain an Amap key, (b) use a paid
provider with China coverage (Google — but its ToS forbids storing coords for a non-Google
map), or (c) accept coarse city/district-centroid pins flagged low-confidence.

**Decision (2026-07-28):** ship at 96%, leave the 136 as NULL, revisit China later. Every
NULL is honest — no fabricated or wrong-city pins were stored (the squeeze passes explicitly
reject wrong-country matches and only POI-search name-only rows).

## Scripts (all dev-only, prod untouched, resumable via `geo_cache`)
- `scripts/db/geocode_onemap_sg.py` / `geocode_onemap_sg_squeeze.py` — Singapore (OneMap, free, no key)
- `scripts/db/geocode_opencage_intl.py` / `geocode_opencage_squeeze.py` — non-SG (OpenCage, `GEOCODING_API_KEY`)
- `scripts/db/geocode_nominatim_squeeze.py` — OSM fallback (free, no key)
- `geo_cache(query, latitude, longitude, source, confidence, raw)` — dedup cache; re-runs skip cached, never re-charge APIs.

To resume China work later: add an Amap key path (query Amap `/geocode/geo`, convert GCJ-02→WGS-84,
store `source='amap'`), targeting `sgx_reit_property where country='China' and coordinate_latitude is null`.
