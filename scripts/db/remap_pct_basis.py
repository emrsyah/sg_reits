"""Remap sgx_reit_top_tenant.pct_basis / sgx_reit_trade_mix.pct_basis onto the
6-value canonical enum agreed in the 2026-07-30 schema review, and populate the
new basis_segment column.

Canonical enum (6):
    headline_rent  annualised_rent  npi  asset_value  gross_rental_income  gross_revenue

basis_segment (nullable): office | retail | commercial | logistics_industrial
    NULL = whole-portfolio. Exists because T82U and BUOU disclose segment tables with
    SEPARATE denominators, each summing to ~100% within the segment. Collapsing them
    to a bare gross_rental_income would make a tenant list appear to sum to 200% --
    and because pct_basis is part of the prod PK, promote_final_to_prod.py would
    literally SUM the two segments' percentages. See docs/7-30-2026-schema-review/
    pct_basis-verification.md sec.1.

Dry by default. --write applies. Anything this script cannot classify from AR
evidence is reported and LEFT UNTOUCHED -- it never guesses a denominator.

Usage:
    /c/Python313/python scripts/db/remap_pct_basis.py                  # preview
    /c/Python313/python scripts/db/remap_pct_basis.py --write          # apply to dev raw
"""
import argparse
import os
import sys
from collections import defaultdict

import psycopg2
from dotenv import load_dotenv

TABLES = ("sgx_reit_top_tenant", "sgx_reit_trade_mix")

CANONICAL = {
    "headline_rent",
    "annualised_rent",
    "npi",
    "asset_value",
    "gross_rental_income",
    "gross_revenue",
}

# ---------------------------------------------------------------------------
# Unconditional remaps: current pct_basis string -> (new_basis, basis_segment, why)
# Keyed on the exact stored string.
# ---------------------------------------------------------------------------
BASIS_MAP = {
    "gri": (
        "gross_rental_income", None,
        'AR wording is literal "gross rental income" / "GRI" across all ~20 REITs using it',
    ),
    "gross_revenue": (
        "gross_revenue", None,
        "already canonical",
    ),
    "headline_rent": (
        "headline_rent", None,
        "already canonical",
    ),
    "npi": (
        "npi", None,
        "already canonical",
    ),
    "asset_value": (
        "asset_value", None,
        "already canonical",
    ),
    "cash_rental_income": (
        "gross_revenue", None,
        "agreed mapping cash_rental_income -> gross_revenue (CMOU/OXMU "
        '"Cash Rental Income (CRI)" = rental income without recoveries)',
    ),
    "committed_gross_rent": (
        "gross_rental_income", None,
        'agreed mapping (K71U "Total Committed Monthly Gross Rent")',
    ),
    "base_rental_income": (
        "gross_rental_income", None,
        "agreed mapping; forward-looking -- not present in dev today",
    ),
    "apartment_rental_income": (
        "gross_rental_income", None,
        "agreed mapping (HMN)",
    ),
    # HMN's two scope-qualified strings. Q3 decision (2026-08-03): accept the loss of
    # the "corporate accounts of properties under Ascott management contracts only"
    # qualifier rather than add a pct_basis_note column.
    "apartment_rental_income (corporate accounts of properties under Ascott management contracts only)": (
        "gross_rental_income", None,
        "Q3: scope qualifier intentionally dropped (HMN FY2024)",
    ),
    "rental_income (corporate accounts of properties under Ascott management contracts only)": (
        "gross_rental_income", None,
        "Q3: scope qualifier intentionally dropped (HMN FY2025)",
    ),
    # Segment variants -> canonical basis + segment. NEVER collapse to a bare value.
    "office_gri": (
        "gross_rental_income", "office",
        'T82U "total office gross rental income" -- own denominator',
    ),
    "retail_gri": (
        "gross_rental_income", "retail",
        'T82U "total gross retail income" -- own denominator',
    ),
    "gri_commercial": (
        "gross_rental_income", "commercial",
        'BUOU "Top 10 Commercial Tenants of FLCT by GRI" -- own denominator',
    ),
    "gri_logistics_industrial": (
        "gross_rental_income", "logistics_industrial",
        'BUOU "Top 10 L&I Tenants of FLCT by GRI" -- own denominator',
    ),
}

# ---------------------------------------------------------------------------
# 'rental_income' is NOT one thing -- it was a catch-all for five distinct metrics.
# Q2 decision: re-map per REIT from the AR evidence. Keyed (symbol, financial_year)
# and applied only to rows currently holding 'rental_income'.
# Entries with new_basis None are UNCLASSIFIED: the AR wording has no home in the
# 6-value enum. They are reported and left untouched.
# ---------------------------------------------------------------------------
RENTAL_INCOME_MAP = {
    ("UD1U", 2025): (
        "gross_rental_income", None,
        '"As a percentage of total gross rental income" (L1631, footnote covers both tables)',
    ),
    ("A17U", 2025): (
        "gross_rental_income", None,
        '"industry mix of customers by gross rental income" (L3700) -- same as FY2024',
    ),
    ("DCRU", 2024): (
        "annualised_rent", None,
        '"Based on annualised rent ... gross rental income for December multiplied by 12" (L1645)',
    ),
    ("DCRU", 2025): (
        "annualised_rent", None,
        '"Based on annualised rent ... gross rental income for December 2025 multiplied by 12" (L1645)',
    ),
    # --- APPROXIMATE (user decision 2026-08-03: "just add to the nearest") -----------
    # These four REITs' AR wording has no exact home in the 6-value enum. Rather than a
    # 7th value, each is mapped to the nearest canonical basis. Each mapping asserts
    # slightly more than the AR says -- flagged as approximate=True and listed
    # separately in the preview so the imprecision stays visible.
    ("Q5T", 2025): (
        "gross_revenue", None,
        '"Percentage of Revenue" / "Trade Sector Mix of Tenants by Revenue (%)". '
        "APPROXIMATE: the AR says Revenue, not *gross* revenue",
    ),
    ("XZL", 2025): (
        "gross_revenue", None,
        '"Percentage of Revenue in FY2025". APPROXIMATE: AR says Revenue, not *gross*',
    ),
    ("CY6U", 2024): (
        "gross_rental_income", None,
        '"Tenant Core Business (By Rental Revenue)"; header "Top 10 Tenants | Rental Revenue". '
        "APPROXIMATE: rental *revenue*, not stated as gross rental income",
    ),
    ("CY6U", 2025): (
        "gross_rental_income", None,
        '"Tenant Core Business (By Rental Revenue)". APPROXIMATE: rental *revenue*, not '
        "stated as gross rental income",
    ),
    ("AJBU", 2024): (
        "gross_rental_income", None,
        '"TOP 10 CLIENTS BY RENTAL INCOME (%)". APPROXIMATE: plain "Rental Income", the AR '
        "does not say gross",
    ),
    ("AJBU", 2025): (
        "gross_rental_income", None,
        '"TOP 10 CLIENTS BY RENTAL INCOME (%) as at 31 December 2025" (L2385). APPROXIMATE: '
        'plain "Rental Income", the AR does not say gross',
    ),
    ("AW9U", 2024): (
        "gross_rental_income", None,
        'plain "Rental Income", "Before recognition of FRS 116 rental straight-lining '
        'adjustments". APPROXIMATE: not stated as gross; the FRS 116 caveat is lost',
    ),
    ("AW9U", 2025): (
        "gross_rental_income", None,
        'plain "Rental Income" + FRS 116 caveat. APPROXIMATE: not stated as gross; the '
        "FRS 116 caveat is lost",
    ),
}


def parse_args():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--write", action="store_true",
                   help="apply the remap to the dev raw tables (default: dry run)")
    p.add_argument("--preview", default="docs/7-30-2026-schema-review/pct_basis-remap-preview.md",
                   help="path to write the preview markdown")
    p.add_argument("--env", default=r"C:\Users\emirsyah\supertype\s_reits\.env")
    return p.parse_args()


def classify(basis, symbol, fy):
    """-> (new_basis, segment, why, status) where status in {change, nochange, unclassified}."""
    if basis == "rental_income":
        hit = RENTAL_INCOME_MAP.get((symbol, fy))
        if hit is None:
            return None, None, f"'rental_income' at {symbol} FY{fy} has no AR-evidence entry", "unclassified"
        new, seg, why = hit
        if new is None:
            return None, None, why, "unclassified"
        return new, seg, why, ("nochange" if new == basis else "change")

    hit = BASIS_MAP.get(basis)
    if hit is None:
        return None, None, f"unknown pct_basis value {basis!r}", "unclassified"
    new, seg, why = hit
    return new, seg, why, ("nochange" if (new == basis and seg is None) else "change")


def main():
    args = parse_args()
    load_dotenv(args.env)
    conn = psycopg2.connect(os.environ["SUPABASE_CONNECTION_STRING"])
    cur = conn.cursor()

    # basis_segment must exist before we can write it.
    cur.execute("""select table_name from information_schema.columns
                   where column_name = 'basis_segment' and table_name = any(%s)""",
                (list(TABLES),))
    have_segment = {r[0] for r in cur.fetchall()}
    missing_segment = set(TABLES) - have_segment

    plan = []            # (table, symbol, fy, old, new, seg, why, status, n)
    unclassified = []
    for tbl in TABLES:
        cur.execute(f"""select replace(symbol,'.SI',''), financial_year, pct_basis, count(*)
                        from {tbl} group by 1,2,3 order by 1,2,3""")
        for symbol, fy, basis, n in cur.fetchall():
            new, seg, why, status = classify(basis, symbol, fy)
            rec = (tbl, symbol, fy, basis, new, seg, why, status, n)
            if status == "unclassified":
                unclassified.append(rec)
            else:
                plan.append(rec)

    changes = [r for r in plan if r[7] == "change"]
    nochange = [r for r in plan if r[7] == "nochange"]

    # ---- summary -----------------------------------------------------------
    lines = []
    w = lines.append
    w("# pct_basis remap -- PREVIEW (nothing applied)\n")
    w("Generated by `scripts/db/remap_pct_basis.py`. Dry run: no rows were modified.\n")
    w("Decisions applied: Q1 `gri` -> `gross_rental_income`; Q2 per-REIT re-map from AR "
      "evidence; Q3 HMN/AW9U scope qualifiers dropped (no note column); Q4 `basis_segment` "
      "column for the 4 segment variants.\n")

    w("## 1. Row impact\n")
    w(f"- rows changing: **{sum(r[8] for r in changes)}**")
    w(f"- rows already canonical: {sum(r[8] for r in nochange)}")
    w(f"- rows UNCLASSIFIED (left untouched): **{sum(r[8] for r in unclassified)}**\n")

    if missing_segment:
        w("> **Blocked on migration.** `basis_segment` does not exist on: "
          + ", ".join(sorted(missing_segment))
          + ". Add it (and to `*_final`, `build_final_tables.py`, and the **prod PK**) "
            "before `--write` can populate segments.\n")

    # ---- resulting enum ----------------------------------------------------
    after = defaultdict(int)
    for r in plan:
        after[(r[4], r[5])] += r[8]
    w("## 2. Resulting enum\n")
    w("| pct_basis | basis_segment | rows |")
    w("|---|---|---|")
    for (b, s), n in sorted(after.items(), key=lambda kv: -kv[1]):
        w(f"| `{b}` | {('`'+s+'`') if s else '_(null)_'} | {n} |")
    bad = {b for b, _ in after} - CANONICAL
    w("")
    w(f"Values outside the agreed 6: {sorted(bad) if bad else '**none**'}\n")

    # ---- changes -----------------------------------------------------------
    w("## 3. Changes\n")
    w("| table | symbol | FY | from | to | segment | rows | evidence |")
    w("|---|---|---|---|---|---|---|---|")
    for tbl, sym, fy, old, new, seg, why, _, n in sorted(changes, key=lambda r: (r[0], r[1], r[2])):
        w(f"| {tbl.replace('sgx_reit_','')} | {sym} | {fy} | `{old}` | `{new}` | "
          f"{('`'+seg+'`') if seg else '' } | {n} | {why} |")

    # ---- unclassified ------------------------------------------------------
    approx = [r for r in changes if "APPROXIMATE" in r[6]]
    w("\n## 4. APPROXIMATE mappings -- imprecision accepted, on the record\n")
    if not approx:
        w("_none_\n")
    else:
        w(f"**{sum(r[8] for r in approx)} rows.** The AR wording for these four REITs has no "
          "exact home in the 6-value enum. Per the 2026-08-03 decision they are mapped to the "
          "nearest canonical basis rather than adding a 7th value. Each asserts slightly more "
          "than its annual report does.\n")
        w("| table | symbol | FY | from | to | rows | what is being assumed |")
        w("|---|---|---|---|---|---|---|")
        for tbl, sym, fy, old, new, _, why, _, n in sorted(approx, key=lambda r: (r[1], r[2], r[0])):
            w(f"| {tbl.replace('sgx_reit_','')} | {sym} | {fy} | `{old}` | `{new}` | {n} | "
              f"{why.split('APPROXIMATE:')[-1].strip()} |")

    if unclassified:
        w("\n### Still unclassified -- left untouched\n")
        w("| table | symbol | FY | current | rows | why |")
        w("|---|---|---|---|---|---|")
        for tbl, sym, fy, old, _, _, why, _, n in sorted(unclassified, key=lambda r: (r[1], r[2], r[0])):
            w(f"| {tbl.replace('sgx_reit_','')} | {sym} | {fy} | `{old}` | {n} | {why} |")

    # ---- known follow-ups --------------------------------------------------
    w("\n## 5. Not handled here (separate work)\n")
    w("- **BUOU FY2025 / T82U FY2025 segment regression.** Both are stored as a single "
      "`gri` although the AR carries the same two-segment structure as FY2024. Splitting "
      "them means assigning each row to office/retail (or commercial/L&I) from the source "
      "tables -- a re-extraction, not a label change. `pct_basis-verification.md` sec.2.")
    w("- **ODBU FY2024** is stored as `gri` but the AR says \"base rental income\". Under the "
      "new enum both land on `gross_rental_income`, so the mislabel is now a no-op. The "
      "distinction is lost either way.")
    w("- **Q5T FY2024 / XZL FY2024 backfill** -- tables exist in the ARs, zero rows loaded.")
    w("- **NLA second basis** (6 REITs disclose GRI *and* NLA) -- still undecided.")

    out = "\n".join(lines) + "\n"
    os.makedirs(os.path.dirname(args.preview), exist_ok=True)
    with open(args.preview, "w", encoding="utf-8") as fh:
        fh.write(out)
    print(out)
    print(f"[preview written] {args.preview}")

    # ---- apply -------------------------------------------------------------
    if not args.write:
        print("\nDRY RUN -- nothing written. Re-run with --write to apply.")
        conn.close()
        return

    needs_seg = any(r[5] for r in changes)
    if needs_seg and missing_segment:
        print(f"\nABORT: basis_segment missing on {sorted(missing_segment)} but "
              f"{sum(r[8] for r in changes if r[5])} rows need a segment. Migrate first.",
              file=sys.stderr)
        conn.close()
        sys.exit(1)

    applied = 0
    for tbl, sym, fy, old, new, seg, _, _, n in changes:
        if seg is not None:
            cur.execute(
                f"update {tbl} set pct_basis=%s, basis_segment=%s "
                f"where replace(symbol,'.SI','')=%s and financial_year=%s and pct_basis=%s",
                (new, seg, sym, fy, old))
        else:
            cur.execute(
                f"update {tbl} set pct_basis=%s "
                f"where replace(symbol,'.SI','')=%s and financial_year=%s and pct_basis=%s",
                (new, sym, fy, old))
        applied += cur.rowcount
    conn.commit()
    print(f"\nAPPLIED to dev raw: {applied} rows updated.")
    print("Next: rebuild _final (build_final_tables.py), then promote.")
    conn.close()


if __name__ == "__main__":
    main()
