"""
Proofreading cockpit for the SGX REIT extractions.

Side-by-side PDF (left) + extracted records (right). Click a record's page
button to jump the PDF there; mark each record correct / false / unsure and
add notes. Everything is persisted to reviews/<dir>.json and survives reloads.

Run:  python scripts/review/app.py        (then open http://127.0.0.1:5057)
Use Chrome or Edge — the page-jump relies on the native PDF viewer's #page=.
"""
import json
import glob
import datetime
from pathlib import Path
from flask import Flask, jsonify, request, send_file, Response, abort

ROOT = Path(__file__).resolve().parents[2]          # repo root
EXTRACTED = ROOT / "extracted"
ANNUAL = ROOT / "annual_reports"
REVIEWS = ROOT / "reviews"
REVIEWS.mkdir(exist_ok=True)

# Sections that hold reviewable records, in display order.
LIST_SECTIONS = ["properties", "top_tenants", "trade_mix",
                 "income_components", "property_transactions"]
DICT_SECTIONS = ["profile", "performance"]
ALL_SECTIONS = DICT_SECTIONS + LIST_SECTIONS         # _notes shown separately, read-only

app = Flask(__name__)


def report_dirs():
    """All extracted report dirs like 'C38U.SI_FY2025'."""
    return sorted(d.name for d in EXTRACTED.iterdir()
                  if d.is_dir() and ".SI_FY" in d.name)


def parse_dir(dirname):
    """'C38U.SI_FY2025' -> ('C38U', 2025)."""
    sym = dirname.split(".SI_FY")[0]
    fy = int(dirname.split("_FY")[-1])
    return sym, fy


def pdf_path_for(dirname):
    sym, fy = parse_dir(dirname)
    hits = glob.glob(str(ANNUAL / f"*_{sym}.SI_*_FY{fy}.pdf"))
    return Path(hits[0]) if hits else None


def load_section(dirname, name):
    f = EXTRACTED / dirname / f"{name}.json"
    if not f.exists():
        return None
    return json.loads(f.read_text(encoding="utf-8"))


def review_file(dirname):
    return REVIEWS / f"{dirname}.json"


def load_review(dirname):
    f = review_file(dirname)
    if f.exists():
        return json.loads(f.read_text(encoding="utf-8"))
    sym, fy = parse_dir(dirname)
    return {"symbol": f"{sym}.SI", "financial_year": fy,
            "page_offset": 0, "items": {}, "updated": None}


def save_review(dirname, data):
    data["updated"] = datetime.datetime.now().isoformat(timespec="seconds")
    review_file(dirname).write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def build_records(dirname):
    """Flatten every reviewable record into {id, section, source_page, fields}."""
    records = []
    for name in ALL_SECTIONS:
        data = load_section(dirname, name)
        if data is None:
            continue
        if isinstance(data, dict):                   # profile / performance
            records.append({
                "id": f"{name}:0", "section": name, "index": 0,
                "source_page": data.get("source_page"),
                "title": name,
                "fields": data,
            })
        elif isinstance(data, list):
            for i, rec in enumerate(data):
                records.append({
                    "id": f"{name}:{i}", "section": name, "index": i,
                    "source_page": rec.get("source_page"),
                    "title": _record_title(name, rec),
                    "fields": rec,
                })
    return records


def _record_title(section, rec):
    for k in ("property_name", "tenant_name", "category", "component",
              "transaction_type", "name"):
        if rec.get(k):
            return str(rec[k])
    if section == "income_components":
        return f"{rec.get('statement', '')}: {rec.get('component', '')}"
    return section


def counts(dirname, records):
    rv = load_review(dirname)["items"]
    c = {"total": len(records), "correct": 0, "false": 0,
         "unsure": 0, "reviewed": 0}
    for r in records:
        v = rv.get(r["id"], {}).get("verdict")
        if v in ("correct", "false", "unsure"):
            c[v] += 1
            c["reviewed"] += 1
    return c


@app.route("/")
def index():
    return send_file(Path(__file__).parent / "index.html")


@app.route("/api/reports")
def api_reports():
    out = []
    for d in report_dirs():
        recs = build_records(d)
        out.append({
            "dir": d,
            "symbol": parse_dir(d)[0],
            "financial_year": parse_dir(d)[1],
            "has_pdf": pdf_path_for(d) is not None,
            "counts": counts(d, recs),
        })
    return jsonify(out)


@app.route("/api/report/<dirname>")
def api_report(dirname):
    if dirname not in report_dirs():
        abort(404)
    return jsonify({
        "dir": dirname,
        "symbol": parse_dir(dirname)[0],
        "financial_year": parse_dir(dirname)[1],
        "has_pdf": pdf_path_for(dirname) is not None,
        "records": build_records(dirname),
        "notes": load_section(dirname, "_notes"),
        "review": load_review(dirname),
    })


@app.route("/api/review/<dirname>", methods=["POST"])
def api_save(dirname):
    if dirname not in report_dirs():
        abort(404)
    body = request.get_json(force=True)
    rv = load_review(dirname)
    if "page_offset" in body:
        rv["page_offset"] = int(body["page_offset"])
    if "item_id" in body:
        item = rv["items"].setdefault(body["item_id"], {})
        if "verdict" in body:
            item["verdict"] = body["verdict"]          # correct|false|unsure|None
            if body["verdict"] is None:
                item.pop("verdict", None)
        if "note" in body:
            item["note"] = body["note"]
            if not body["note"]:
                item.pop("note", None)
        item["updated"] = datetime.datetime.now().isoformat(timespec="seconds")
        if not item:                                   # cleaned out -> drop
            rv["items"].pop(body["item_id"], None)
    save_review(dirname, rv)
    recs = build_records(dirname)
    return jsonify({"ok": True, "counts": counts(dirname, recs),
                    "review": rv})


@app.route("/pdf/<dirname>")
def pdf(dirname):
    p = pdf_path_for(dirname)
    if not p or not p.exists():
        abort(404)
    # conditional=True enables range requests; the explicit cache header lets the
    # browser keep the bytes so the forced re-navigation on each page-jump is
    # instant (no re-download, no revalidation round-trip).
    resp = send_file(p, mimetype="application/pdf", conditional=True)
    resp.cache_control.no_cache = None        # send_file sets this; clear it
    resp.cache_control.public = True
    resp.cache_control.max_age = 86400
    resp.expires = None
    return resp


if __name__ == "__main__":
    print("Proofreading cockpit -> http://127.0.0.1:5057  (use Chrome/Edge)")
    app.run(host="127.0.0.1", port=5057, debug=False)
