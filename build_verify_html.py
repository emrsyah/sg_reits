"""Build verify_extraction.html — interactive cross-check bench for pilot extractions.

Embeds every extracted/<symbol>_FY2025/*.json into a single-file HTML where each record
links to its annual-report PDF page and carries verify (correct / wrong / unsure) controls
persisted in localStorage, exportable as JSON.

Re-run after any re-extraction:  python build_verify_html.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).parent
TRUSTS = [
    {"symbol": "C38U.SI", "name": "CapitaLand Integrated Commercial Trust", "short": "CICT",
     "dir": "C38U.SI_FY2025", "pdf": "annual_reports/09_C38U.SI_CapitaLand-Integrated-Commercial-Trust_FY2025.pdf"},
    {"symbol": "J69U.SI", "name": "Frasers Centrepoint Trust", "short": "FCT",
     "dir": "J69U.SI_FY2025", "pdf": "annual_reports/18_J69U.SI_Frasers-Centrepoint-Trust_FY2025.pdf"},
    {"symbol": "AU8U.SI", "name": "CapitaLand China Trust", "short": "CLCT",
     "dir": "AU8U.SI_FY2025", "pdf": "annual_reports/07_AU8U.SI_CapitaLand-China-Trust_FY2025.pdf"},
]
TABLES = ["profile", "performance", "properties", "property_transactions",
          "top_tenants", "trade_mix", "income_components"]

data = []
for t in TRUSTS:
    d = dict(t)
    d["tables"] = {}
    base = ROOT / "extracted" / t["dir"]
    for tb in TABLES:
        p = base / f"{tb}.json"
        if p.exists():
            v = json.loads(p.read_text(encoding="utf-8"))
            d["tables"][tb] = v if isinstance(v, list) else [v]
        else:
            d["tables"][tb] = []
    np_ = base / "_notes.json"
    d["notes"] = json.loads(np_.read_text(encoding="utf-8")) if np_.exists() else {}
    data.append(d)

payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")

template = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Extraction verification bench — 3 trusts vs sgx_reit schema v1.1</title>
<style>
:root{
  --bg:#f4f2ec; --card:#fcfbf7; --ink:#23201a; --ink2:#5a5346; --muted:#94896f;
  --hair:#dcd6c4; --hair2:#c9c0a6;
  --ok:#1e6e4e; --ok-soft:#e0efe6; --bad:#b03a2a; --bad-soft:#f6e3df;
  --uns:#9a6b14; --uns-soft:#f4ecd6; --link:#2d5e8a;
  --mono:'Cascadia Code',ui-monospace,Consolas,monospace;
}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',system-ui,sans-serif;background:var(--bg);color:var(--ink);font-size:14px;line-height:1.5}
a{color:var(--link)}
header{background:var(--ink);color:var(--bg);padding:16px 22px;display:flex;flex-wrap:wrap;gap:16px;align-items:center;position:sticky;top:0;z-index:90}
header h1{font-size:1.05rem;font-weight:600;letter-spacing:.01em}
header .sub{font-family:var(--mono);font-size:.72rem;opacity:.75}
header .spacer{flex:1}
header button{font-family:var(--mono);font-size:.74rem;background:transparent;border:1px solid rgba(255,255,255,.4);color:var(--bg);border-radius:7px;padding:6px 12px;cursor:pointer}
header button:hover{background:rgba(255,255,255,.12)}
.trustbar{display:flex;gap:0;border-bottom:2px solid var(--ink);background:var(--card);position:sticky;top:58px;z-index:80;flex-wrap:wrap}
.trustbar .tb{flex:1;min-width:200px;border:0;background:none;cursor:pointer;padding:12px 16px;text-align:left;border-right:1px solid var(--hair);position:relative}
.trustbar .tb b{display:block;font-size:.95rem}
.trustbar .tb span{font-size:.74rem;color:var(--ink2)}
.trustbar .tb .prog{position:absolute;left:0;bottom:0;height:3px;background:var(--ok);transition:width .3s}
.trustbar .tb.active{background:var(--ink);color:var(--bg)}
.trustbar .tb.active span{color:rgba(255,255,255,.65)}
.tabbar{display:flex;gap:2px;overflow-x:auto;padding:10px 18px 0;background:var(--bg);position:sticky;top:121px;z-index:70;border-bottom:1px solid var(--hair2)}
.tabbar button{font-family:var(--mono);font-size:.74rem;border:1px solid var(--hair2);border-bottom:0;background:var(--card);padding:8px 13px;border-radius:8px 8px 0 0;cursor:pointer;color:var(--ink2);white-space:nowrap}
.tabbar button.active{background:var(--ink);color:var(--bg);border-color:var(--ink)}
.tabbar button .ct{opacity:.6;margin-left:5px}
.tabbar button .vd{margin-left:5px;color:var(--ok)}
.tabbar button.active .vd{color:#8fd4ae}
main{padding:18px 22px 120px;max-width:1500px;margin:0 auto}
.toolrow{display:flex;gap:12px;align-items:center;margin-bottom:14px;flex-wrap:wrap}
.toolrow input[type=search]{font-family:var(--mono);font-size:.8rem;padding:8px 12px;border:1.5px solid var(--ink);border-radius:8px;background:var(--card);width:300px;color:var(--ink)}
.toolrow .fbtn{font-family:var(--mono);font-size:.72rem;border:1px solid var(--hair2);background:var(--card);border-radius:99px;padding:5px 12px;cursor:pointer;color:var(--ink2)}
.toolrow .fbtn.on{border-color:var(--ink);color:var(--ink);font-weight:600}
.toolrow .hint{font-size:.76rem;color:var(--muted);margin-left:auto}

/* record cards (properties / performance) */
.cards{display:grid;gap:14px}
.rec{background:var(--card);border:1px solid var(--hair2);border-left:5px solid var(--hair2);border-radius:10px;overflow:hidden}
.rec.st-ok{border-left-color:var(--ok)} .rec.st-bad{border-left-color:var(--bad)} .rec.st-uns{border-left-color:var(--uns)}
.rec-head{display:flex;gap:12px;align-items:center;padding:10px 16px;border-bottom:1px solid var(--hair);background:linear-gradient(to bottom,rgba(0,0,0,.015),transparent);flex-wrap:wrap}
.rec-head h3{font-size:.95rem;font-weight:700}
.rec-head .meta{font-family:var(--mono);font-size:.7rem;color:var(--muted)}
.rec-head .spacer{flex:1}
.pagelink{font-family:var(--mono);font-size:.72rem;font-weight:600;color:var(--link);border:1px solid currentColor;border-radius:6px;padding:2px 8px;text-decoration:none;white-space:nowrap}
.pagelink:hover{background:var(--link);color:#fff}
.fields{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:1px;background:var(--hair);padding:1px}
.fld{background:var(--card);padding:8px 14px;min-height:54px}
.fld .k{font-family:var(--mono);font-size:.66rem;color:var(--muted);letter-spacing:.04em;display:flex;justify-content:space-between;gap:6px}
.fld .v{font-size:.88rem;margin-top:2px;word-break:break-word}
.fld .v.num{font-family:var(--mono);font-weight:600}
.fld .v.null{color:var(--hair2);font-style:italic;font-weight:400}
.fld .raw{display:block;font-family:var(--mono);font-size:.66rem;color:var(--muted)}
.fld.hit{outline:2px solid var(--uns);outline-offset:-2px;border-radius:4px}
.subtable{font-size:.76rem;border-collapse:collapse;margin-top:4px;width:100%}
.subtable td,.subtable th{border:1px solid var(--hair);padding:2px 7px;text-align:left}
.subtable th{font-family:var(--mono);font-size:.62rem;color:var(--muted);font-weight:500}
.mixlist{margin-top:4px;display:flex;flex-direction:column;gap:2px;max-height:180px;overflow-y:auto}
.mixlist .mi{display:flex;justify-content:space-between;gap:8px;font-size:.78rem;border-bottom:1px dotted var(--hair);padding:1px 0}
.mixlist .mi b{font-family:var(--mono);font-weight:600}

/* verify strip */
.vstrip{display:flex;align-items:center;gap:8px;padding:8px 16px;border-top:1px solid var(--hair);background:rgba(0,0,0,.012)}
.vbtn{font-size:.8rem;border:1.5px solid var(--hair2);background:var(--card);border-radius:7px;padding:4px 12px;cursor:pointer;font-weight:600;color:var(--ink2)}
.vbtn.ok.on{background:var(--ok-soft);border-color:var(--ok);color:var(--ok)}
.vbtn.bad.on{background:var(--bad-soft);border-color:var(--bad);color:var(--bad)}
.vbtn.uns.on{background:var(--uns-soft);border-color:var(--uns);color:var(--uns)}
.vnote{flex:1;font-size:.78rem;border:1px solid var(--hair);border-radius:7px;padding:5px 10px;background:#fff;min-width:160px;color:var(--ink)}
.vnote::placeholder{color:var(--hair2)}

/* row tables */
.rowtbl{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--hair2);border-radius:10px;overflow:hidden}
.rowtbl th{font-family:var(--mono);font-size:.64rem;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);text-align:left;padding:9px 12px;border-bottom:2px solid var(--ink);background:var(--card);position:sticky;top:168px;z-index:10}
.rowtbl td{padding:7px 12px;border-bottom:1px solid var(--hair);vertical-align:top;font-size:.84rem}
.rowtbl tr.st-ok td:first-child{box-shadow:inset 4px 0 0 var(--ok)}
.rowtbl tr.st-bad td:first-child{box-shadow:inset 4px 0 0 var(--bad)}
.rowtbl tr.st-uns td:first-child{box-shadow:inset 4px 0 0 var(--uns)}
.rowtbl td.num{font-family:var(--mono);font-weight:600;text-align:right;white-space:nowrap}
.rowtbl td .raw{display:block;font-family:var(--mono);font-size:.64rem;color:var(--muted);font-weight:400}
.rowtbl .vcell{white-space:nowrap}
.rowtbl .vcell .vbtn{padding:2px 8px;font-size:.74rem}
.rowtbl tr.hit td{background:var(--uns-soft)}
.rowtbl .notecell input{width:130px}

/* notes view */
.notes-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:16px}
.nbox{background:var(--card);border:1px solid var(--hair2);border-radius:10px;padding:14px 18px}
.nbox h4{font-family:var(--mono);font-size:.7rem;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);margin-bottom:10px}
.nbox li{margin:0 0 8px 18px;font-size:.82rem;color:var(--ink2)}
.nbox .recon{font-family:var(--mono);font-size:.78rem}
.nbox .recon div{display:flex;justify-content:space-between;border-bottom:1px dotted var(--hair);padding:3px 0}
.empty{padding:40px;text-align:center;color:var(--muted);font-style:italic}
footer{position:fixed;bottom:0;left:0;right:0;background:var(--ink);color:var(--bg);font-family:var(--mono);font-size:.72rem;padding:8px 22px;display:flex;gap:18px;align-items:center;z-index:95}
footer .pbar{flex:1;height:6px;background:rgba(255,255,255,.15);border-radius:99px;overflow:hidden}
footer .pbar i{display:block;height:100%;background:linear-gradient(90deg,#2f8a5e,#56b083);width:0;transition:width .3s}
footer .bad-ct{color:#e8917f}
@media(max-width:820px){.rowtbl{display:block;overflow-x:auto}}
</style>
</head>
<body>
<header>
  <div><h1>Extraction verification bench</h1>
  <div class="sub">3 trusts · FY2025 · vs sgx_reit_schema_final v1.1 · click p.N to open the AR at that page</div></div>
  <div class="spacer"></div>
  <button id="exportBtn">⭳ export verification JSON</button>
  <button id="resetBtn">reset all</button>
</header>
<div class="trustbar" id="trustbar"></div>
<div class="tabbar" id="tabbar"></div>
<main id="main"></main>
<footer>
  <span id="fstat">0 / 0 checked</span>
  <div class="pbar"><i id="fbar"></i></div>
  <span id="fbad" class="bad-ct"></span>
</footer>

<script>
const DATA = __DATA__;
const TABLE_LABELS = {profile:'Profile', performance:'Performance', properties:'Properties',
  property_transactions:'Transactions', top_tenants:'Top tenants', trade_mix:'Trade mix',
  income_components:'Income components', _notes:'Notes & reconciliation'};
const NUMFMT_SKIP = /(fiscal_year|rank|year|page|count|number_of_leases)/;
let curTrust = 0, curTab = 'properties', filterMode = 'all', query = '';

/* ---------- verification state ---------- */
const LS_KEY = 'sreit_verify_v1';
let V = {};
try { V = JSON.parse(localStorage.getItem(LS_KEY) || '{}'); } catch(e){ V = {}; }
const saveV = () => localStorage.setItem(LS_KEY, JSON.stringify(V));
const rid = (ti,tab,i) => DATA[ti].symbol + '|' + tab + '|' + i;

/* ---------- helpers ---------- */
const esc = s => String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;');
function fmtNum(v, key){
  if (typeof v !== 'number' || NUMFMT_SKIP.test(key)) return esc(v);
  const a = Math.abs(v);
  let disp;
  if (a >= 1e9) disp = (v/1e6).toLocaleString('en-SG',{maximumFractionDigits:1}) + 'm';
  else if (a >= 1e6) disp = (v/1e6).toLocaleString('en-SG',{maximumFractionDigits:2}) + 'm';
  else disp = v.toLocaleString('en-SG',{maximumFractionDigits:3});
  return disp + (a >= 1e6 ? `<span class="raw">${v.toLocaleString('en-SG')}</span>` : '');
}
function pageLink(ti, page){
  if (page == null) return '';
  return `<a class="pagelink" href="${DATA[ti].pdf}#page=${page}" target="_blank" title="open AR at page ${page}">p.${page}</a>`;
}
function renderVal(ti, key, v){
  if (v === null || v === undefined || v === '' ) return '<span class="v null">— null —</span>';
  if (Array.isArray(v)){
    if (v.length && typeof v[0] === 'object'){
      const keys = Object.keys(v[0]);
      return `<table class="subtable"><tr>${keys.map(k=>`<th>${esc(k)}</th>`).join('')}</tr>` +
        v.map(o=>`<tr>${keys.map(k=>`<td>${o[k]==null?'·':esc(typeof o[k]==='number'?o[k].toLocaleString('en-SG'):o[k])}</td>`).join('')}</tr>`).join('') + '</table>';
    }
    return `<span class="v">${v.map(esc).join(', ')}</span>`;
  }
  if (typeof v === 'object'){
    const ent = Object.entries(v);
    return `<div class="mixlist">${ent.map(([k,x])=>`<span class="mi"><span>${esc(k)}</span><b>${esc(x)}${typeof x==='number'?'%':''}</b></span>`).join('')}</div>`;
  }
  const num = typeof v === 'number';
  return `<span class="v ${num?'num':''}">${fmtNum(v,key)}</span>`;
}
function recTitle(tab, r, i){
  return r.property_name || r.tenant_name || r.category || r.component ||
    (r.transaction_type ? `${r.transaction_type}: ${r.property_name||''}` : null) ||
    (tab==='performance' ? 'REIT-level performance' : null) ||
    (tab==='profile' ? 'Profile' : null) || ('record #' + (i+1));
}
function getStatus(id){ return (V[id]||{}).s || ''; }
function matchQuery(r){
  if (!query) return true;
  return JSON.stringify(r).toLowerCase().includes(query);
}
function matchFilter(id){
  const s = getStatus(id);
  if (filterMode==='all') return true;
  if (filterMode==='unchecked') return !s;
  return s === filterMode;
}

/* ---------- render: trust bar / tab bar ---------- */
function trustProgress(ti){
  let tot=0, done=0;
  for (const tab of Object.keys(DATA[ti].tables)){
    DATA[ti].tables[tab].forEach((_,i)=>{ tot++; if (getStatus(rid(ti,tab,i))) done++; });
  }
  return [done,tot];
}
function renderTrustbar(){
  document.getElementById('trustbar').innerHTML = DATA.map((t,i)=>{
    const [d,tot]=trustProgress(i);
    return `<button class="tb ${i===curTrust?'active':''}" onclick="setTrust(${i})">
      <b>${t.short} · ${t.symbol}</b><span>${t.name} — ${d}/${tot} checked</span>
      <span class="prog" style="width:${tot?100*d/tot:0}%"></span></button>`;
  }).join('');
}
function renderTabbar(){
  const t = DATA[curTrust];
  const tabs = Object.keys(TABLE_LABELS);
  document.getElementById('tabbar').innerHTML = tabs.map(tab=>{
    if (tab === '_notes')
      return `<button class="${curTab===tab?'active':''}" onclick="setTab('_notes')">${TABLE_LABELS[tab]}</button>`;
    const rows = t.tables[tab]||[];
    const done = rows.filter((_,i)=>getStatus(rid(curTrust,tab,i))).length;
    return `<button class="${curTab===tab?'active':''}" onclick="setTab('${tab}')">
      ${TABLE_LABELS[tab]}<span class="ct">${rows.length}</span>${done?`<span class="vd">✓${done}</span>`:''}</button>`;
  }).join('');
}

/* ---------- render: main ---------- */
function vstrip(id){
  const st = getStatus(id), note = (V[id]||{}).n || '';
  return `<div class="vstrip">
    <button class="vbtn ok ${st==='ok'?'on':''}" onclick="setSt('${id}','ok')">✓ correct</button>
    <button class="vbtn bad ${st==='bad'?'on':''}" onclick="setSt('${id}','bad')">✗ wrong</button>
    <button class="vbtn uns ${st==='uns'?'on':''}" onclick="setSt('${id}','uns')">? unsure</button>
    <input class="vnote" placeholder="note (what's off, correct value, page...)" value="${esc(note)}"
      onchange="setNote('${id}',this.value)">
  </div>`;
}
function vcell(id){
  const st = getStatus(id);
  return `<td class="vcell">
    <button class="vbtn ok ${st==='ok'?'on':''}" onclick="setSt('${id}','ok')">✓</button>
    <button class="vbtn bad ${st==='bad'?'on':''}" onclick="setSt('${id}','bad')">✗</button>
    <button class="vbtn uns ${st==='uns'?'on':''}" onclick="setSt('${id}','uns')">?</button>
  </td>
  <td class="notecell"><input class="vnote" placeholder="note" value="${esc((V[id]||{}).n||'')}" onchange="setNote('${id}',this.value)"></td>`;
}
function cardView(tab){
  const rows = DATA[curTrust].tables[tab]||[];
  const html = rows.map((r,i)=>{
    const id = rid(curTrust,tab,i);
    if (!matchFilter(id) || !matchQuery(r)) return '';
    const sp = r.source_page;
    const headPage = typeof sp === 'number' ? pageLink(curTrust, sp) : '';
    const fields = Object.entries(r).filter(([k])=>!['source_page','symbol','fiscal_year'].includes(k));
    return `<div class="rec st-${getStatus(id)||'none'}" data-id="${id}">
      <div class="rec-head"><h3>${esc(recTitle(tab,r,i))}</h3>
        <span class="meta">${esc(r.category||'')}${r.country?' · '+esc(r.country):''}</span>
        <div class="spacer"></div>${headPage}</div>
      <div class="fields">${fields.map(([k,v])=>{
        const pg = (typeof sp === 'object' && sp && sp[k]!=null) ? pageLink(curTrust, sp[k]) : '';
        const hit = query && v!=null && String(typeof v==='object'?JSON.stringify(v):v).toLowerCase().includes(query);
        return `<div class="fld ${hit?'hit':''}"><span class="k">${esc(k)}${pg}</span>${renderVal(curTrust,k,v)}</div>`;
      }).join('')}</div>
      ${vstrip(id)}</div>`;
  }).join('');
  return html ? `<div class="cards">${html}</div>` : '<div class="empty">no records match</div>';
}
function tableView(tab){
  const rows = DATA[curTrust].tables[tab]||[];
  if (!rows.length) return '<div class="empty">no records</div>';
  const keys = [...new Set(rows.flatMap(r=>Object.keys(r)))].filter(k=>!['symbol','fiscal_year','source_page'].includes(k));
  const body = rows.map((r,i)=>{
    const id = rid(curTrust,tab,i);
    if (!matchFilter(id) || !matchQuery(r)) return '';
    return `<tr class="st-${getStatus(id)||'none'} ${query&&matchQuery(r)&&query?'':''}">${keys.map(k=>{
      const v = r[k];
      if (v==null) return '<td><span class="v null">·</span></td>';
      const num = typeof v==='number';
      return `<td class="${num?'num':''}">${num?fmtNum(v,k):esc(v)}</td>`;
    }).join('')}<td>${pageLink(curTrust, r.source_page)}</td>${vcell(id)}</tr>`;
  }).join('');
  return `<table class="rowtbl"><thead><tr>${keys.map(k=>`<th>${esc(k)}</th>`).join('')}<th>src</th><th>verify</th><th>note</th></tr></thead><tbody>${body||''}</tbody></table>` + (body?'':'<div class="empty">no records match</div>');
}
function notesView(){
  const n = DATA[curTrust].notes || {};
  const rec = n.reconciliation || {};
  const li = a => (a||[]).map(x=>{
    if (typeof x === 'string') return `<li>${esc(x)}</li>`;
    const title = x.item || x.name || x.column || x.trap || x.issue || '';
    const val = x.value!=null ? ` — <b>${esc(x.value)}</b>` : '';
    const why = x.reason || x.detail || x.note || '';
    const pg = x.page!=null ? ` ${pageLink(curTrust, x.page)}` : (x.source_page!=null ? ` ${pageLink(curTrust, x.source_page)}` : '');
    const rest = Object.entries(x).filter(([k])=>!['item','name','column','trap','issue','value','reason','detail','note','page','source_page'].includes(k))
      .map(([k,v])=>`${esc(k)}: ${esc(typeof v==='object'?JSON.stringify(v):v)}`).join(' · ');
    return `<li><b>${esc(title)}</b>${val}${pg}${why?`<br><span style="color:var(--muted)">${esc(why)}</span>`:''}${rest?`<br><span style="color:var(--muted);font-size:.72rem">${rest}</span>`:''}</li>`;
  }).join('') || '<li>—</li>';
  return `<div class="notes-grid">
    <div class="nbox"><h4>Reconciliation</h4><div class="recon">${Object.entries(rec).map(([k,v])=>`<div><span>${esc(k)}</span><b>${esc(typeof v==='number'?v.toLocaleString('en-SG'):v)}</b></div>`).join('')||'—'}</div></div>
    <div class="nbox"><h4>Data with no home (schema gaps)</h4><ul>${li(n.data_with_no_home)}</ul></div>
    <div class="nbox"><h4>Columns never fillable here</h4><ul>${li(n.columns_never_fillable)}</ul></div>
    <div class="nbox"><h4>Parsing traps hit</h4><ul>${li(n.parsing_traps)}</ul></div>
  </div>`;
}
function render(){
  renderTrustbar(); renderTabbar();
  const tool = curTab==='_notes' ? '' : `<div class="toolrow">
    <input type="search" placeholder="search anything…" value="${esc(query)}" oninput="setQuery(this.value)">
    ${['all','unchecked','ok','bad','uns'].map(f=>`<button class="fbtn ${filterMode===f?'on':''}" onclick="setFilter('${f}')">${{all:'all',unchecked:'unchecked',ok:'✓ correct',bad:'✗ wrong',uns:'? unsure'}[f]}</button>`).join('')}
    <span class="hint">click any <b>p.N</b> to open the PDF at that page</span></div>`;
  const view = curTab==='_notes' ? notesView()
    : (curTab==='properties'||curTab==='performance'||curTab==='profile') ? cardView(curTab) : tableView(curTab);
  document.getElementById('main').innerHTML = tool + view;
  renderFooter();
}
function renderFooter(){
  let tot=0, done=0, bad=0;
  DATA.forEach((t,ti)=>Object.keys(t.tables).forEach(tab=>t.tables[tab].forEach((_,i)=>{
    tot++; const s=getStatus(rid(ti,tab,i)); if(s)done++; if(s==='bad')bad++;
  })));
  document.getElementById('fstat').textContent = `${done} / ${tot} records checked`;
  document.getElementById('fbar').style.width = (tot?100*done/tot:0)+'%';
  document.getElementById('fbad').textContent = bad? `${bad} marked wrong` : '';
}

/* ---------- actions ---------- */
window.setTrust = i => { curTrust=i; render(); window.scrollTo(0,0); };
window.setTab   = t => { curTab=t; render(); window.scrollTo(0,0); };
window.setFilter= f => { filterMode=f; render(); };
window.setQuery = q => { query=q.trim().toLowerCase(); clearTimeout(window._qt); window._qt=setTimeout(render,250); };
window.setSt = (id,s) => { const cur=V[id]||{}; cur.s = (cur.s===s?'':s); V[id]=cur; saveV(); render(); };
window.setNote = (id,n) => { const cur=V[id]||{}; cur.n=n; if(n&&!cur.s)cur.s='uns'; V[id]=cur; saveV(); renderFooter(); renderTrustbar(); renderTabbar(); };

document.getElementById('exportBtn').onclick = () => {
  const out = [];
  DATA.forEach((t,ti)=>Object.keys(t.tables).forEach(tab=>t.tables[tab].forEach((r,i)=>{
    const v=V[rid(ti,tab,i)]; if(!v||(!v.s&&!v.n)) return;
    out.push({symbol:t.symbol, table:tab, index:i, record:recTitle(tab,r,i),
              status:v.s||null, note:v.n||null, source_page:r.source_page??null});
  })));
  const blob = new Blob([JSON.stringify({exported:new Date().toISOString(),results:out},null,2)],{type:'application/json'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob); a.download = 'verification_results.json'; a.click();
};
document.getElementById('resetBtn').onclick = () => {
  if (confirm('Clear ALL verification marks and notes?')){ V={}; saveV(); render(); }
};
render();
</script>
</body>
</html>
"""

html = template.replace("__DATA__", payload)
out = ROOT / "verify_extraction.html"
out.write_text(html, encoding="utf-8")
print(f"written {out} ({out.stat().st_size:,} bytes)")
print("records embedded:", sum(len(v) for d in data for v in d["tables"].values()))
