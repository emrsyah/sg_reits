# XZL (Acrophyte Hospitality Trust) — premise check on "headline DPS = sum of tranches"

Sources: `parsed_reports_datalab/01_XZL.SI_Acrophyte-Hospitality-Trust_FY2024/full.md` (FY24) and
`parsed_reports_datalab/01_XZL.SI_Acrophyte-Hospitality-Trust_FY2025/full.md` (FY25).

## 1. Is headline DPS the sum of tranches, and how is it defined?

FY24, line 1210:
> "The total distribution (after deducting income retained for general corporate and working capital) for FY2024 was lower at US\$9.3 million. Accordingly, ACRO-HT's distribution per Stapled Security ("**DPS**") for the year was 1.595 US cents."

FY25, line 1273:
> "For 2H 2025, US\$2.42 million was available for distribution to Stapled Securityholders. The total distribution (after setting aside the reserves for capital expenditure) for FY2025 was US\$4.9 million. Accordingly, ACRO-HT's DPS for the year was 0.850 US cents."

Headline DPS is explicitly defined as full-year distributable amount (after retention) ÷ securities in issue — i.e. it is inherently the annual total, which by construction equals 1H + 2H. No footnote says it's anything other than the FY sum.

## 2. Basis — before or after 10% retention?

Both years disclose both bases side by side, in the same table:

FY25 report, lines 3241–3243 (FY2025 | FY2024 columns):
> "| Distribution amount to Stapled Securityholders (after retention) | 4,928 | 9,254 |"
> "| Distribution per Stapled Security (DPS) (US cents) | 0.944 | 1.772 |"
> "| Distribution per Stapled Security (DPS) (after retention) (US cents) | 0.850 | 1.595 |"

So the headline figures we're using (1.595, 0.850) are the **after-retention** basis. The half-year tranche announcements found so far are also after-retention:

FY24 report, line 5967:
> "On 27 February 2025, the Managers approved a distribution of 0.848 US cents per Stapled Security for the period from 1 July 2024 to 31 December 2024 to be paid on 28 March 2025."

Cross-check: 2H2024 distributable income after retention = US\$4.9m (line 1693) ÷ ~580.1m securities ≈ 0.845–0.848 cents. Matches 0.848 as an after-retention figure — same basis as the 1.595 headline. **No basis mismatch found for the tranche that has been located.**

## 3. Does 1.595 belong to FY2024?

FY24 report, line 1084 (chart, oldest-first):
> "Values are Nil, 0.355, 3.054, 3.430, and 1.595 respectively" for "FY2020 to FY2024"

FY24 report, line 1122 (table, newest-first):
> "| Distribution per Stapled Security (US cents) | 1.595 | 3.430 | 3.054 | 0.355 | - |"

Both orderings independently place 1.595 at FY2024. Confirmed correct.

## 4. Distribution frequency — is XZL semi-annual?

FY24 report, line 3290:
> "ACRO-REIT's distribution policy is to distribute at least 90% of its distribution income for each financial year on a semi-annual basis and ACRO-BT's distribution policy is to distribute at least 90% of its distribution income for each financial year on a semi-annual basis..."

Corporate calendar confirms two distinct half-year payment events per FY:
FY24 report, lines 1770–1771:
> "| First Half Results Announcement | 7 August 2024 |"
> "| Payment of Distribution (six months ended 30 June 2024) | 27 September 2024 |"

...plus the 2H tranche (line 5967, paid 28 March 2025, i.e. after FY2024's own year-end, in the subsequent-events note of the FY2024 AR). So FY2024 legitimately has two tranches: a 1H tranche paid Sept 2024 (not yet located — this is what the colleague is chasing) and the 2H tranche of 0.848 disclosed as a post-year-end declaration. Same structure repeats for FY2025 (1H paid ~Sept 2025 per FY25 report line 1783; 2H = 0.418, line 5844, declared 26 Feb 2026 for payment 30 Mar 2026). **XZL does pay semi-annually, confirming the "half is missing" reading is structurally correct** — the gap is a real, findable 1H tranche, not evidence the DPS isn't additive.

## 5. Securities count stability

FY24 report, line 5979: "580,102,394 Stapled Securities... in issue as at 19 March 2025."
FY25 report, line 5856: "580,102,394 Stapled Securities... in issue as at 16 March 2026."

Identical count across both year-ends — negligible mid-year issuance (weighted-average share count moves only from 579,792k to 580,103k per the EPS note, line 4918). Not a material driver of any non-additivity.

## 6. Cross-check: distributable income ÷ securities in issue

- FY2024: US\$9.3m (line 1210, after retention) ÷ ~580.1m securities ≈ **1.60 cents** — lands next to the headline 1.595, not near 0.848.
- FY2025: US\$4.9m (line 1273, after retention) ÷ ~580.1m securities ≈ **0.845 cents** — lands next to the headline 0.850, not near 0.418.

This confirms the headline DPS is the full-year distributable-income-per-security figure, and structurally equals 1H tranche + 2H tranche (both after retention, same security count).

## Verdict

**The sum-of-tranches assumption holds.** Headline DPS (1.595 FY2024, 0.850 FY2025) is explicitly defined in the report text as the after-retention, full-year distribution per security, on the same after-retention basis as the disclosed 2H tranches (0.848, 0.418), with a stable security count and a confirmed semi-annual payment policy. The "gap" (0.747 for FY2024, 0.432 for FY2025) is not evidence of a broken premise — it is the 1H tranche that has not yet been located in either report's disclosed text (separate from the 2H tranche buried in each year's subsequent-events note). That hunt is correctly the colleague's task, not a sign the additive model itself is wrong.
