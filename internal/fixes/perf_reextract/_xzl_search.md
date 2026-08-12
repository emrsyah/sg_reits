# XZL (Acrophyte Hospitality Trust) — missing distribution tranche search

## FY2024 report (`01_XZL.SI_Acrophyte-Hospitality-Trust_FY2024/full.md`)

### Statement of Distributable Income (p.105)
> line 3264: "For the financial year ended 31 December 2024"
> line 3281: `| **Amount available for distribution** | **10,282** | 19,835 |`
> line 3284: `| **Distribution amount to Stapled Securityholders (after retention)** | **9,254** | 19,835 |`
> line 3285: `| **Distribution per Stapled Security (DPS) (US cents)** | **1.772** | 3.430 |`
> line 3286: `| **Distribution per Stapled Security (DPS) (after retention) (US cents)** | **1.595** | 3.430 |`

This is a single **annual** figure (before-retention 1.772, after-retention 1.595) — it is NOT broken into two half-year rates anywhere in this statement. There is no "1H2024" or "2H2024" column.

### Subsequent Events note 32 (p.178)
> line 5967: "On 27 February 2025, the Managers approved a distribution of 0.848 US cents per Stapled Security for the period from 1 July 2024 to 31 December 2024 to be paid on 28 March 2025."

This is the **2H2024** tranche (0.848 US cents, after-retention basis), declared after FYE and disclosed ONLY here, not in the Distribution Statement. This is almost certainly the "0.848" figure already found by the earlier pass.

### Financial Review narrative (p. ~62)
> line 1691: "the amount available for distribution for 2H2024 and FY2024 was US\$5.9 million and US\$10.3 million, respectively."
> line 1693: "Accordingly, ACRO-HT reported a distributable income of US\$4.9 million for 2H2024 and US\$9.3 million for FY2024."

Only 2H2024 and FY2024 dollar amounts are disclosed narratively. **No 1H2024 dollar figure or rate is stated anywhere** — not computed, not narrated, not in a table.

### Searches that came up empty for FY2024
- `1H2024`, `1H 2024` (interim/half-year distribution context) — no hits except an unrelated "Analyst earnings call for 1H 2024 results" calendar entry (line 1751).
- `0.747` — zero hits anywhere in the file.
- No "first half" distribution rate/dollar figure found in Financial Highlights, Financial Review, or notes.

**Conclusion FY2024:** the 1H2024 tranche (~0.747 US cents, derivable only by subtracting the disclosed 2H2024 0.848 from the disclosed FY2024 after-retention DPS 1.595) is **not disclosed anywhere in the AR as a standalone rate or dollar figure**. Only the annual total (1.595) and the 2H tranche (0.848, subsequent event) are stated. 0.747 would be a derived number, not a reported one — not written here as fact per the task rules.

---

## FY2025 report (`01_XZL.SI_Acrophyte-Hospitality-Trust_FY2025/full.md`)

### Statement of Distributable Income (p. ~104, analogous table)
> line 3241: `| **Distribution amount to Stapled Securityholders (after retention)** | **4,928** | 9,254 |`
> line 3242: `| **Distribution per Stapled Security (DPS) (US cents)** | **0.944** | 1.772 |`
> line 3243: `| **Distribution per Stapled Security (DPS) (after retention) (US cents)** | **0.850** | 1.595 |`

Again a single annual figure — 0.944 before retention, 0.850 after retention for FY2025. No half-year split in this statement.

### Subsequent Events note 29 (p.178)
> line 5844: "Additionally, on 26 February 2026, the Managers approved a distribution of 0.418 US cents per Stapled Security for the period from 1 July 2025 to 31 December 2025 to be paid on 30 March 2026."

This is the **2H2025** tranche (0.418 US cents, after-retention basis) — matches the "0.418" already found.

### Financial Review narrative
> line 1273: "For 2H 2025, US\$2.42 million was available for distribution to Stapled Securityholders. The total distribution (after setting aside the reserves for capital expenditure) for FY2025 was US\$4.9 million. Accordingly, ACRO-HT's DPS for the year was 0.850 US cents."
> line 1691: "For FY2025, 10% of the total amount available for distribution was retained..."

Again, only 2H2025 and FY2025 totals are given in dollars; no explicit 1H2025 dollar or rate figure.

### Searches that came up empty for FY2025
- `0.432` — zero hits anywhere in the file.
- `1H2025`, `1H 2025` — no hits except the unrelated earnings-call calendar entry (line 1746).
- No "first half" distribution rate/dollar figure found anywhere.

**Conclusion FY2025:** same pattern as FY2024. The 1H2025 tranche (~0.432 US cents) is **not disclosed anywhere in the AR**. Only the FY2025 annual total (0.850 after retention) and the 2H2025 subsequent-event tranche (0.418) are stated as rates.

---

## Overall finding

XZL's audited Statement of Distributable Income presents only a **single annual DPS figure** (before and after the 10% retention) — it does not break the year into 1H/2H rates. The **second-half tranche is disclosed once**, as a Subsequent Events note, because it is declared and approved by the Managers only after the financial year-end (27 Feb 2025 for 2H2024; 26 Feb 2026 for 2H2025) and paid ~2 months later (28 Mar 2025; 30 Mar 2026).

The **first-half tranche's per-security rate is never separately disclosed** in either report — not in the Distribution Statement, not in Subsequent Events, not in the Financial Review narrative, not in Financial Highlights. It only exists implicitly as the difference between the annual after-retention DPS and the disclosed 2H tranche:
- FY2024: 1.595 − 0.848 = 0.747 (DERIVED, not disclosed)
- FY2025: 0.850 − 0.418 = 0.432 (DERIVED, not disclosed)

Per the task rules, these derived 0.747 / 0.432 values should NOT be recorded as if they were extracted/disclosed figures. If the schema needs a "1H tranche" field, it should be flagged as **calculated/derived**, not sourced to a specific line, or left null with the annual total (1.595 / 0.850) and the disclosed 2H tranche (0.848 / 0.418) recorded instead.
