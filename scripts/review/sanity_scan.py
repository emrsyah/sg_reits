"""
sanity_scan.py — deterministic, no-LLM proofreading aid for the extracted/ set.

It does NOT read the source PDFs, so it cannot tell you "this number disagrees
with the page" (that's the LLM verifier's job). It flags values that are
implausible in isolation, internally inconsistent, or outliers across the set —
the gross errors and structural gaps a human would otherwise hunt for by eye.

Run:  python scripts/review/sanity_scan.py            # all reports in extracted/
      python scripts/review/sanity_scan.py DHLU UD1U  # just these symbols

Output is grouped per report with [FAIL]/[WARN]/[INFO] tags + a final summary.
Always exits 0 (it's a report, not a gate).
"""
import json
import sys
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXTRACTED = ROOT / "extracted"

STATUS_ENUM = {"active", "divested", "held_for_sale"}
ROLE_ENUM = {"reit_manager", "property_manager", "trustee",
             "sponsor", "operator", "master_lessee"}


def load(d, name):
    p = EXTRACTED / d / f"{name}.json"
    try:
        return json.load(open(p, encoding="utf-8"))
    except FileNotFoundError:
        return None


def recon_ok(v):
    """Interpret a _notes.reconciliation flag as ok / not-ok / unknown."""
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        s = v.strip().lower()
        if s in ("pass", "true", "yes", "ok", "reconciles", "reconciled"):
            return True
        if s in ("fail", "false", "no"):
            return False
    return None


def scan_report(d):
    """Return list of (severity, message) for one report dir."""
    sym = d.split(".SI_FY")[0]
    fy = int(d.split("_FY")[-1])
    out = []
    def fail(m): out.append(("FAIL", m))
    def warn(m): out.append(("WARN", m))
    def info(m): out.append(("INFO", m))

    profile = load(d, "profile")
    perf = load(d, "performance")
    props = load(d, "properties") or []
    tenants = load(d, "top_tenants") or []
    mix = load(d, "trade_mix") or []
    income = load(d, "income_components") or []
    notes = load(d, "_notes") or {}

    # ---- invariant: source_page on every record ----
    for name, recs in [("properties", props), ("top_tenants", tenants),
                       ("trade_mix", mix), ("income_components", income)]:
        miss = sum(1 for r in recs if not r.get("source_page"))
        if miss:
            fail(f"{name}: {miss}/{len(recs)} record(s) missing source_page")

    # ---- profile ----
    if profile:
        roles = {m.get("role") for m in profile.get("management", [])}
        for needed in ("reit_manager", "trustee", "sponsor"):
            if needed not in roles:
                warn(f"profile: no '{needed}' in management (almost always disclosed)")
        bad = roles - ROLE_ENUM
        if bad:
            fail(f"profile: unknown management role(s) {sorted(bad)}")
    else:
        fail("profile.json missing")

    # ---- performance ----
    if perf:
        pv = perf.get("portfolio_value")
        gr = perf.get("gross_revenue")
        npi = perf.get("net_property_income")
        dpu = perf.get("dpu")
        nu = perf.get("number_of_unitholders")
        if not pv or pv <= 0:
            warn("performance: portfolio_value missing/zero")
        elif pv < 1e8:
            warn(f"performance: portfolio_value {pv:,.0f} looks too small (scale error? expect absolute $)")
        if gr and npi and npi > gr:
            fail(f"performance: NPI ({npi:,.0f}) > gross_revenue ({gr:,.0f})")
        if dpu in (None, 0):
            info("performance: dpu is null/0 — confirm distribution halted (e.g. US trust), else missing")
        elif dpu and (dpu < 0 or dpu > 50):
            warn(f"performance: dpu {dpu} cents outside typical 0–50 range")
        if not nu or nu <= 0:
            warn("performance: number_of_unitholders missing/zero")
        if str(perf.get("date", "")).split("-")[0] not in ("", str(fy), str(fy + 1)):
            warn(f"performance: date {perf.get('date')} doesn't match financial_year {fy}")
        if not perf.get("currency"):
            warn("performance: currency missing")
    else:
        fail("performance.json missing")

    # ---- properties ----
    active_null_val = 0
    for r in props:
        nm = r.get("property_name", "?")
        occ = r.get("occupancy_rate")
        if occ is not None and (occ < 0 or occ > 100):
            fail(f"properties[{nm}]: occupancy_rate {occ} outside 0–100")
        if occ is not None and 0 < occ <= 1:
            warn(f"properties[{nm}]: occupancy_rate {occ} — fraction not percent? (expect e.g. 95.0)")
        st = r.get("status")
        if st and st not in STATUS_ENUM:
            fail(f"properties[{nm}]: status '{st}' not in {sorted(STATUS_ENUM)}")
        if not r.get("currency"):
            warn(f"properties[{nm}]: currency missing")
        mv = r.get("market_valuation")
        if (st in (None, "active")) and (mv is None):
            active_null_val += 1
    if active_null_val:
        info(f"properties: {active_null_val} active row(s) with null market_valuation "
             f"— OK only if JV/equity-accounted or PPE (check _notes)")

    # ---- trade_mix: sum per pct_basis ----
    if mix:
        groups = {}
        for r in mix:
            groups.setdefault(r.get("pct_basis", "?"), 0.0)
            groups[r["pct_basis"] if r.get("pct_basis") else "?"] = \
                groups.get(r.get("pct_basis", "?"), 0.0) + (r.get("pct") or 0.0)
        for basis, s in groups.items():
            if not (90 <= s <= 110):
                warn(f"trade_mix: pct sums to {s:.1f}% for basis '{basis}' "
                     f"(expect ~100; scoped subset is OK if noted)")
    else:
        info("trade_mix: empty — confirm genuinely absent in this report")

    # ---- top_tenants ----
    if tenants:
        ranks = [r.get("rank") for r in tenants if r.get("rank") is not None]
        if ranks and sorted(ranks) != list(range(1, len(ranks) + 1)):
            warn(f"top_tenants: ranks not 1..N contiguous ({sorted(ranks)})")
        gsum = sum((r.get("gri_percentage") or 0) for r in tenants)
        if gsum > 105:
            fail(f"top_tenants: gri_percentage sums to {gsum:.1f}% (>100)")
        for r in tenants:
            g = r.get("gri_percentage")
            if g is not None and (g < 0 or g > 100):
                fail(f"top_tenants rank {r.get('rank')}: gri_percentage {g} outside 0–100")
    else:
        info("top_tenants: empty — confirm genuinely absent/anonymised")

    # ---- reconciliation flags from _notes ----
    recon = notes.get("reconciliation", {}) if isinstance(notes, dict) else {}
    for key in ("valuation_reconciles", "gross_revenue_reconciles",
                "npi_reconciles", "trade_mix_reconciles", "total_return_check"):
        if key in recon:
            ok = recon_ok(recon[key])
            if ok is False:
                fail(f"_notes.reconciliation.{key} = {recon[key]!r} (does NOT reconcile)")
    return out


def main():
    want = [a.upper() for a in sys.argv[1:]]
    dirs = sorted(p.name for p in EXTRACTED.iterdir()
                  if p.is_dir() and ".SI_FY" in p.name)
    if want:
        dirs = [d for d in dirs if d.split(".SI_FY")[0].upper() in want]

    totals = {"FAIL": 0, "WARN": 0, "INFO": 0}
    # gather cross-report numerics for outlier note
    dpus, nprops = [], []
    for d in dirs:
        perf = load(d, "performance")
        props = load(d, "properties") or []
        if perf and perf.get("dpu"):
            dpus.append((d.split(".SI_FY")[0], perf["dpu"]))
        nprops.append((d.split(".SI_FY")[0], len(props)))

    for d in dirs:
        res = scan_report(d)
        print(f"\n===== {d} =====")
        if not res:
            print("  clean — no flags")
        for sev, msg in sorted(res, key=lambda x: ["FAIL", "WARN", "INFO"].index(x[0])):
            print(f"  [{sev}] {msg}")
            totals[sev] += 1

    # cross-report outliers (light, median ± 3·MAD)
    print("\n===== cross-report outliers =====")
    flagged = False
    for label, series in [("dpu(cents)", dpus)]:
        vals = [v for _, v in series]
        if len(vals) >= 4:
            med = statistics.median(vals)
            mad = statistics.median([abs(v - med) for v in vals]) or 1e-9
            for sym, v in series:
                if abs(v - med) > 3 * mad:
                    print(f"  [INFO] {label}: {sym}={v} far from median {med} (MAD {mad:.2f})")
                    flagged = True
    if not flagged:
        print("  none")

    print(f"\n===== SUMMARY =====")
    print(f"  reports scanned: {len(dirs)}")
    print(f"  FAIL {totals['FAIL']}   WARN {totals['WARN']}   INFO {totals['INFO']}")
    print("  (FAIL = almost certainly wrong; WARN = check; INFO = expected-but-verify)")


if __name__ == "__main__":
    main()
