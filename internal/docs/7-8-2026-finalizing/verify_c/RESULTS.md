# §C Policy-Audit Results (2026-07-08)

19 non-frozen REITs audited (read-only agents) against emirsyah's answers. Snapshots in
`verify_c/<SYM>.json`. Applied fixes are marked ✅; items needing a decision are marked ❓.

## Item 8 — store-in-SGD ("which report uses another ccy though SGD is disclosed?")
**Answer: NONE.** Every REIT stores mv/GR/NPI as-disclosed. Two correct patterns:
- **Foreign-functional REITs** (present in their own ccy; SGD NOT disclosed per-property → correct):
  USD — CMOU, ODBU, OXMU, XZL, BTOU, DCRU; GBP — MXNU; EUR — SET, UD1U.
- **SGD-presentation multi-country** (mv in SGD as disclosed; GR/NPI in SGD where disclosed, else
  local-only because only local is disclosed per-property): HMN, J85, J91U, CY6U, DHLU, AW9U, Q5T,
  AJBU, D5IU, AU8U, BMOU, CRPU. J85/AW9U/Q5T disclose SGD per-asset (stored SGD ✅); HMN/J91U/CY6U/
  DHLU disclose GR/NPI local-only per-asset (stored local ✅; SGD only at segment/aggregate level).
No mislabels. (purchase_price kept verbatim per item 6; `original_*` deferred per item 9.)

## Item 1 — lease_term_years = actual base term (not X+Y / not remaining)
**✅ FIXED (base separable, as-disclosed, applied JSON+DB):**
- **J91U — 36 rows** set to base X (first number of "X+Y", e.g. 60→30, 62→32, 42→30, 32→10). AR
  discloses "X+Y" in Portfolio Statistics tenure (pp132-150).
- **AJBU — 3 rows** (term incl. extension offers, p111 fn1): KDC SGP 5 39→30, SGP 7 70→60, SGP 8 70→60.
- **JYEU — 1 row**: Development site adjacent to 313@somerset 12.997→3 (base 3-yr term, p152).

**❓ FLAG_NOT_SEPARABLE (AR discloses only options-inclusive OR remaining term; base term X NOT
disclosed anywhere — cannot fix as-disclosed):**
- **O5RU — 25 leasehold rows**: p162 fn "Includes the period covered by the relevant options to renew".
- **M1GU — 18 rows**: p122 fn "Includes the period covered by the relevant options to renew".
- **UD1U — 4 rows**: column literally "Remaining Term of Leasehold" — stored = *remaining*, not term.
- **SET — 4 rows**: column "Remaining Term of Leasehold" — stored = remaining.
- **CY6U — 1 row** (CapitaLand DC Navi Mumbai): stored 95 = the renewal length, base not disclosed.
- **XZL — 2 rows**: leaseholds on all-options-exercised basis; base not disclosed.
Decision needed: leave stored value + set a `flags` marker (e.g. `lease_term_basis: options_inclusive`
/ `remaining`), or null them. Recommend: keep value + flag (don't lose data).

**PASS (already base term):** 8C8U, MXNU, Q5T, AW9U (30 not 35), J85 (Hilton Cambridge 125 not 175),
CMOU/ODBU/OXMU/DHLU (freehold → null).

## Items 2 & 3 — lease_expiry_date → string; effective_date fill; purchase_date
**❓ SCHEMA CHANGE (needs go-ahead):** change `lease_expiry_date` and `effective_date` from `date`
to text/string (models.py + loader + DB column) so year-only values fit. Current valid dates all
convert to ISO strings cleanly. **purchase_year column: not needed** (per your call).

**purchase_date (text) — acquisition/purchase dates disclosed, ready to fill (as-disclosed):**
CMOU 13 (p21-22), OXMU 13 (p25-27), DHLU 19 (p166), SET 104 (portfolio even-pages), ODBU 1,
XZL 3 (Marriott 2020-01-17), + others. (Per your correction: acquisition date → `purchase_date`, NOT
effective_date.)

**effective_date (lease commencement year):**
- **Disclosed (as-disclosed fill):** 8C8U (8, already populated), MXNU (6, populated), J85 (12,
  populated), ODBU (1: 2013-05-30). These are genuine.
- **❓ Derivable only (`expiry − term`) — IMPUTED, not disclosed:** O5RU, M1GU, J91U, AJBU, AW9U,
  Q5T, CY6U (partial), etc. **Caveat:** derivation only gives the true commencement when subtracting
  the TOTAL term from the total-term expiry. Where we just fixed lease_term to the BASE (J91U, AJBU
  SGP5/7/8), `expiry − base` gives the WRONG (renewal) commencement — must derive from the ORIGINAL
  total term, or skip. Where lease_term = *remaining* (UD1U, SET), `expiry − remaining` = the 2025
  as-at date (useless). **Decision:** fill effective_date with derived year + mark inferred
  (`flags`/`_notes.inferred[]`) per the as-disclosed policy? Or only fill where genuinely disclosed?

## Item 5 — DCRU ownership-basis valuation
**✅ Already correct for 9 of 11.** The 9 consolidated properties store the 100% fair value (matches
FS Note 6 p182 exactly; e.g. 1500 Space Park Dr DB=101M = 100%, ownership-basis would be 90.9M p47).
**❓ 2 Osaka JVs (20%-owned) are ownership-adjusted** (Osaka 2 = 113.3M, Osaka 3 = 90.0M = 20% share)
and **no 100% year-end valuation is disclosed** (equity-accounted, excluded from Note 6). Only Osaka 3
has a 100% *acquisition* value (¥65,390m @ 15 Mar 2025, different date+ccy). **Decision:** leave the 2
Osaka at ownership-basis + flag (recommended, honors as-disclosed), or none of the above.
purchase_consideration = purchase_price: **confirmed, no action.**

## Item 7 — AW9U freehold-with-lease → EXPLAINED, correct
The "lease" on freehold Japan rows is the **outbound master lease** the trust grants tenants (income
instrument), not a ground lease. `land_tenure=Freehold` + `lease_term_years`/`lease_expiry_date`
(master lease) legitimately coexist. **No fix.** J85 has an analogous freehold-with-restricting-lease
(4 SG hotels) — also fine.

## Item 6 — purchase_price = verbatim → no action. Item 9 — original_*/local_* → flag only, revisit.

## Item 4 — area_unit → **DONE** (0 gap; every non-frozen property with an area figure has area_unit).
