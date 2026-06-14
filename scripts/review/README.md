# Proofreading cockpit

Side-by-side review tool: the annual-report **PDF on the left**, the **extracted records
on the right**. Click a record's `📄 p.N` button to jump the PDF to that page, then mark
the record **✓ correct / ✗ false / ? unsure** and add a note. Everything is saved
automatically and tracked.

## Run

```bash
python scripts/review/app.py
```

Open **http://127.0.0.1:5057** in **Chrome or Edge** (the page-jump uses the native PDF
viewer's `#page=` parameter).

## How it works

- Reads the canonical extractions from `extracted/<SYM>.SI_FY<YYYY>/` (all 8 files,
  flattened into one reviewable list per report) and the matching PDF from
  `annual_reports/`.
- Every record carries its `source_page` (the AR's printed page number). The page button
  navigates the PDF to `source_page + page_offset`.
- **Page offset**: printed page numbers usually differ from the physical PDF page (cover
  pages etc.). Click any page button once, see how far off it is, then set the **page
  offset** box (top bar) so jumps land exactly. The offset is saved per report.
- Verdicts and notes are written to `reviews/<SYM>.SI_FY<YYYY>.json` on every change —
  reload-safe, git-trackable. Re-running the server picks up where you left off.

## Reviews file format

```json
{
  "symbol": "C38U.SI", "financial_year": 2025, "page_offset": 2,
  "items": {
    "properties:3": {"verdict": "false", "note": "valuation should be 1,158.0m", "updated": "..."},
    "top_tenants:0": {"verdict": "correct", "updated": "..."}
  },
  "updated": "..."
}
```

Item id = `<section>:<index>` (e.g. `properties:3`, `profile:0`).

## UI notes

- **Filter** (top right): `all` / `unreviewed` / `false` / `unsure` — to sweep back through
  only the items you flagged.
- **Progress bar** + per-report `reviewed/total` in the dropdown update live.
- The `_notes.json` for each report (reconciliation, quirks, declared nulls) is shown
  collapsed at the top of the right panel for context.
