"""Build sgx_reit_*_final tables: SGD-normalized, area-sqm, provenance-stripped, renamed.
Spec: docs/reits_db_handoff/final_schema_proposal.md. DRY_RUN previews; set False to create.
"""
import os, json, math, sys
import psycopg2
from psycopg2.extras import Json, execute_values
from dotenv import load_dotenv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from normalize_locations import normalize_locations  # canonical country cleanup for properties_location
load_dotenv('.env')

DRY_RUN = ('--write' not in sys.argv)

# --only sgx_reit_property_final[,...]  -> rebuild just those _final tables, leave the rest alone.
# The script is a flat sequence of drop/create/load sections; without this every run drops and
# recreates all seven tables even when one table's source rows changed. Filtering keeps the
# blast radius equal to the change.
ONLY = set()
for _i, _a in enumerate(sys.argv):
    if _a == '--only' and _i + 1 < len(sys.argv):
        ONLY = {t.strip() for t in sys.argv[_i + 1].split(',') if t.strip()}
def selected(name):
    return not ONLY or name in ONLY

# P1: a per-figure currency tag that is missing falls back to the row-level `currency`. That
# fallback is usually RIGHT (a JPY row's untagged sale price is JPY), so it must not hard-fail --
# but it was silent, which produced the DCRU 770,936 artifact. Every inheritance is now recorded
# and printed; --strict-currency turns them into an abort once the tags have been backfilled.
STRICT_CURRENCY = ('--strict-currency' in sys.argv)
inherited_ccy = []
SQFT_TO_SQM = 0.092903
conn = psycopg2.connect(os.environ['SUPABASE_CONNECTION_STRING']); conn.autocommit = False
cur = conn.cursor()

# ---- FX ----
_rates = json.load(open('quarterly_rates.json', encoding='utf-8'))['quarters']
import pandas as pd
_parsed = sorted((pd.to_datetime(k), k) for k in _rates)
warnings = []
# our extractions use the trade names; MAS publishes the ISO codes. Without this map
# every RMB figure silently NULLed (AU8U and M44U divestment gains, 2026-08-04).
_CCY_ALIAS = {'RMB': 'CNY', 'CNH': 'CNY', 'RM': 'MYR', 'S$': 'SGD', 'SG$': 'SGD',
              'US$': 'USD', 'A$': 'AUD', 'HK$': 'HKD', 'NT$': 'TWD', 'Rmb': 'CNY'}
def to_sgd(value, ccy, date, ctx=''):
    if value is None: return None
    ccy = _CCY_ALIAS.get(ccy, ccy)
    if ccy in (None, '', 'SGD'): return float(value)
    if not date:
        warnings.append(f'{ctx}: no date for {ccy} -> NULLED'); return None
    q = min(_parsed, key=lambda p: abs((p[0] - pd.to_datetime(date)).days))[1]
    tbl = _rates.get(q, {})
    if ccy in tbl and 'SGD' in tbl[ccy]:
        # ndigits is REQUIRED: bare round() truncates to an integer, which destroys
        # per-unit figures for foreign-currency reporters (CMOU dpu 0.25 -> 0,
        # BTOU nav -> 0, MXNU nav 0.69 -> 1). See docs/7-30-2026-schema-review.
        return round(float(value) * tbl[ccy]['SGD'], 6)
    warnings.append(f'{ctx}: no rate for {ccy} @ {q} -> NULLED')
    return None  # never emit raw native as SGD

cur.execute("select symbol,financial_year,date from sgx_reit_performance")
_FYEND = {(s, f): d for s, f, d in cur.fetchall()}
def fy_end(sym, fy):
    return _FYEND.get((sym, fy))

# income_stmt money keys (convert for foreign reporters); NOT: share counts, _derived
ISM_MONEY = {'total_revenue','cost_of_revenue','gross_income','operating_expense','operating_income',
 'non_operating_income_or_loss','pretax_income','income_taxes','net_income','minorities',
 'perpetual_security_holders','unitholders','interest_expense_non_operating','ebit','ebitda',
 'net_property_sales','funds_from_operation'}
ISM_SKIP = {'basic_shares_outstanding','diluted_shares_outstanding','weighted_avg_shares_basic','_derived'}

def conv_blob(blob, ccy, date, kind):
    if blob is None or ccy in (None,'','SGD'): return blob
    b = dict(blob)
    if kind == 'ism':
        for k in list(b):
            if k in ISM_MONEY and isinstance(b[k], (int,float)):
                b[k] = to_sgd(b[k], ccy, date, f'ism.{k}')
        for bd in ('revenue_breakdown','operating_expense_breakdown'):
            if isinstance(b.get(bd), list):
                b[bd] = [{**it, 'amount': to_sgd(it.get('amount'), ccy, date, f'ism.{bd}')} if isinstance(it, dict) else it for it in b[bd]]
    else:  # balance_sheet / cash_flow: all numeric leaves are money
        for k in list(b):
            if isinstance(b[k], (int,float)): b[k] = to_sgd(b[k], ccy, date, f'{kind}.{k}')
    return b

report = {}
def ddl_drop_create(name, cols_sql):
    if DRY_RUN or not selected(name): return
    cur.execute(f'drop table if exists public.{name}')
    cur.execute(f'create table public.{name} ({cols_sql})')

def load(name, cols, rows):
    report[name] = len(rows)
    if not selected(name):
        print(f'[SKIP] {name}: not in --only, left untouched')
        return
    if DRY_RUN:
        print(f'[DRY] {name}: {len(rows)} rows; sample:', rows[0] if rows else None)
        return
    tmpl = '(' + ','.join(['%s']*len(cols)) + ')'
    execute_values(cur, f'insert into public.{name} ({",".join(cols)}) values %s',
                   rows, template=tmpl)

# ===== profile_final =====
def strip_board_prov(board):
    """RAW board = [{name, position, source_page}]. _final/prod keep only name+position."""
    if not isinstance(board, list): return board
    return [{k: v for k, v in d.items() if k != 'source_page'} if isinstance(d, dict) else d
            for d in board]
cur.execute('select symbol,sub_sector,management,board from sgx_reit_profile')
prows = [(s, ss, Json(m) if m is not None else None,
          Json(strip_board_prov(b)) if b is not None else None)
         for s,ss,m,b in cur.fetchall()]
ddl_drop_create('sgx_reit_profile_final',
  'symbol text primary key, sub_sector text, management jsonb, board jsonb')
load('sgx_reit_profile_final', ['symbol','sub_sector','management','board'], prows)

# ===== performance_final =====
PERF_MONEY = ['portfolio_value','gross_revenue','net_property_income','net_distributable_income',
 'adjusted_distributable_income','distribution_paid','distributable_income_opening',
 'distribution_cash_paid','distributable_income_closing']
# Distribution-flow restructure, 2026-08-03. See
# docs/7-30-2026-schema-review/performance-target-schema-AGREED.md
#   dev already carries the new names (migration 2026-08-03_performance_flow.sql),
#   so this block is mostly a pass-through. Two things do NOT cross into _final:
#     paid_in_units        DRP settlement — dev-only audit trail, drives no metric
#     income_for_year_basis  marks the 5 computed (rather than printed) values
cur.execute("""select symbol,financial_year,date,source_url,currency,properties_location,number_of_unitholders,
 units_in_issue,units_to_be_issued,distribution_record,dpu_period_months,
 aggregate_leverage,interest_coverage_ratio,cost_of_debt,weighted_avg_debt_maturity,wale,portfolio_occupancy,
 dpu,nav_per_unit,portfolio_value,gross_revenue,net_property_income,income_for_year,
 distribution_declared,distributable_income_opening,distribution_paid,
 distributable_income_closing,amount_retained,other_additions from sgx_reit_performance""")
cols=['symbol','financial_year','date','source_url','properties_location','number_of_unitholders','units_in_issue',
 'units_to_be_issued','distribution_record','distribution_period_months','aggregate_leverage','interest_coverage_ratio',
 'cost_of_debt','weighted_average_debt_maturity','weighted_average_lease_expiry','portfolio_occupancy',
 'distribution_per_unit','net_asset_value_per_unit','portfolio_value','gross_revenue','net_property_income',
 'income_for_year','distribution_declared','distributable_income_opening','distribution_paid',
 'distributable_income_closing','amount_retained','other_additions']
prows=[]
for r in cur.fetchall():
    (sym,fy,date,src,ccy,ploc,nuh,uii,utbi,drec,dpm,lev,icr,cod,wadm,wale,occ,dpu,nav,
     pv,gr,npi,ify,ddec,dio,dpaid,dic,retained,addns)=r
    def cv(v): return to_sgd(v, ccy, date, f'perf.{sym}')
    def cv_record(rec):
        # distribution_record was passed through UNCONVERTED while distribution_per_unit
        # was converted, so in _final a foreign reporter's tranches and its headline sat
        # in DIFFERENT currencies -- SET FY2025 read 20.188 SGD cents against tranches
        # summing to 13.39 EUR cents, the 1.5077 EUR/SGD rate. Convert the per-unit rate
        # and any amount inside each tranche so sum(record) = dpu survives the layer.
        # an EMPTY list is meaningful -- suspended/withheld trusts declared nothing --
        # so preserve [] and only pass None through as None.
        if rec is None: return None
        out=[]
        for t in rec:
            t=dict(t)
            if t.get('dpu') is not None: t['dpu']=cv(t['dpu'])
            if t.get('amount') is not None: t['amount']=cv(t['amount'])
            out.append(t)
        return out
    prows.append((sym,fy,date,src,normalize_locations(ploc),nuh,
      float(uii) if uii is not None else None,
      float(utbi) if utbi is not None else None,
      Json(cv_record(drec)) if drec is not None else None,
      float(dpm) if dpm is not None else None,
      float(lev) if lev is not None else None, float(icr) if icr is not None else None,
      float(cod) if cod is not None else None, float(wadm) if wadm is not None else None,
      float(wale) if wale is not None else None, float(occ) if occ is not None else None,
      cv(dpu), cv(nav), cv(pv), cv(gr), cv(npi), cv(ify), cv(ddec), cv(dio), cv(dpaid), cv(dic),
      cv(retained), cv(addns)))
ddl_drop_create('sgx_reit_performance_final',
  'symbol text, financial_year smallint, date date, source_url text, properties_location text, number_of_unitholders int, '
  'units_in_issue numeric, units_to_be_issued numeric, distribution_record jsonb, '
  'distribution_period_months numeric, aggregate_leverage numeric, interest_coverage_ratio numeric, '
  'cost_of_debt numeric, weighted_average_debt_maturity numeric, weighted_average_lease_expiry numeric, '
  'portfolio_occupancy numeric, distribution_per_unit numeric, net_asset_value_per_unit numeric, '
  'portfolio_value numeric, gross_revenue numeric, net_property_income numeric, income_for_year numeric, '
  'distribution_declared numeric, distributable_income_opening numeric, distribution_paid numeric, '
  'distributable_income_closing numeric, amount_retained numeric, other_additions numeric, primary key(symbol,financial_year)')
load('sgx_reit_performance_final', cols, prows)

# ===== financial_final =====
cur.execute('select symbol,financial_year,currency,income_stmt_metrics,balance_sheet_metrics,cash_flow_metrics,employee_breakdown from sgx_reit_financial')
frows=[]
for sym,fy,ccy,ism,bs,cf,emp in cur.fetchall():
    d=fy_end(sym,fy)
    ism2=conv_blob(ism,ccy,d,'ism'); bs2=conv_blob(bs,ccy,d,'bs'); cf2=conv_blob(cf,ccy,d,'cf')
    # rename weighted_avg_shares_basic -> basic_shares_outstanding; drop _derived
    if isinstance(ism2,dict):
        if 'weighted_avg_shares_basic' in ism2: ism2['basic_shares_outstanding']=ism2.pop('weighted_avg_shares_basic')
        ism2.pop('_derived', None)
    frows.append((sym,fy, Json(ism2) if ism2 else None, Json(bs2) if bs2 else None,
                  Json(cf2) if cf2 else None, Json(emp) if emp else None))
ddl_drop_create('sgx_reit_financial_final',
  'symbol text, financial_year smallint, income_stmt_metrics jsonb, balance_sheet_metrics jsonb, '
  'cash_flow_metrics jsonb, employee_breakdown jsonb, primary key(symbol,financial_year)')
load('sgx_reit_financial_final', ['symbol','financial_year','income_stmt_metrics','balance_sheet_metrics','cash_flow_metrics','employee_breakdown'], frows)

# ===== property_final =====
cur.execute("""select symbol,financial_year,property_name,country,category,address,ownership,
 market_valuation,purchase_price,valuation_date,net_property_income,net_property_income_currency,
 gross_revenue,gross_revenue_currency,occupancy_rate,nla,gfa,area_unit,land_tenure,effective_date,
 lease_term_years,lease_expiry_date,status,purchase_date,
 coordinate_latitude,coordinate_longitude,coordinate_source from sgx_reit_property""")
prows=[]
for r in cur.fetchall():
    # gla dropped 2026-08-03 (schema review): 9 surviving values moved into nla, column removed.
    (sym,fy,pn,ctry,cat,addr,own,mv,pp,vdate,npi,npic,gr,grc,occ,nla,gfa,au,lt,eff,lty,lexp,st,pdate,
     clat,clng,csrc)=r
    d=fy_end(sym,fy)
    # Rule A: mv, pp already SGD. Rule B: gross/npi in-tag.
    def area(v):
        if v is None: return None
        return round(float(v)*SQFT_TO_SQM) if (au and str(au).lower() in ('sqft','sq ft','square feet')) else float(v)
    prows.append((sym,fy,pn,ctry,cat,addr, float(own) if own is not None else None,
      float(mv) if mv is not None else None, float(pp) if pp is not None else None, vdate,
      to_sgd(npi,npic,d,f'prop.npi.{sym}:{pn}'), to_sgd(gr,grc,d,f'prop.gr.{sym}:{pn}'),
      float(occ) if occ is not None else None, area(nla), area(gfa),
      lt, eff, float(lty) if lty is not None else None, lexp, st, pdate,
      # coordinates: pass-through (not currency/percent, no transform)
      float(clat) if clat is not None else None, float(clng) if clng is not None else None, csrc))
ddl_drop_create('sgx_reit_property_final',
  'symbol text, financial_year smallint, property_name text, country text, category text, address text, '
  'ownership numeric, market_valuation numeric, purchase_price numeric, valuation_date date, '
  'net_property_income numeric, gross_revenue numeric, occupancy_rate numeric, '
  'net_lettable_area numeric, gross_floor_area numeric, land_tenure text, effective_date text, '
  'lease_term_years numeric, lease_expiry_date text, status text, purchase_date text, '
  'coordinate_latitude double precision, coordinate_longitude double precision, coordinate_source text')
load('sgx_reit_property_final', ['symbol','financial_year','property_name','country','category','address','ownership',
 'market_valuation','purchase_price','valuation_date','net_property_income','gross_revenue','occupancy_rate',
 'net_lettable_area','gross_floor_area','land_tenure','effective_date','lease_term_years',
 'lease_expiry_date','status','purchase_date',
 'coordinate_latitude','coordinate_longitude','coordinate_source'], prows)

# ===== top_tenant_final / trade_mix_final =====
# basis_segment: NULL = whole-portfolio. Non-null (office/retail/commercial/
# logistics_industrial) marks a disclosure with its OWN denominator summing to ~100%
# within the segment (T82U, BUOU). It must travel with pct_basis all the way to prod
# and be part of the prod PK -- otherwise aggregate_trade_mix() sums two segments'
# percentages into one row. See docs/7-30-2026-schema-review/pct_basis-verification.md
cur.execute('select symbol,financial_year,rank,client_name,industry,revenue_pct,pct_basis,basis_segment from sgx_reit_top_tenant')
tt=[tuple(x) for x in cur.fetchall()]
ddl_drop_create('sgx_reit_top_tenant_final',
  'symbol text, financial_year smallint, rank int, client_name text, industry text, revenue_pct numeric, pct_basis text, basis_segment text')
load('sgx_reit_top_tenant_final', ['symbol','financial_year','rank','client_name','industry','revenue_pct','pct_basis','basis_segment'], tt)

cur.execute('select symbol,financial_year,category,pct,pct_basis,basis_segment from sgx_reit_trade_mix')
tm=[tuple(x) for x in cur.fetchall()]
ddl_drop_create('sgx_reit_trade_mix_final',
  'symbol text, financial_year smallint, category text, pct numeric, pct_basis text, basis_segment text')
load('sgx_reit_trade_mix_final', ['symbol','financial_year','category','pct','pct_basis','basis_segment'], tm)

# ===== property_transaction_final =====
TXN_MONEY = [('purchase_price','purchase_price_currency','completed_date'),
 ('sale_price','sale_price_currency','completed_date'),
 ('basis_value','basis_currency','completed_date')]
# v2 schema (2026-08-03). carrying_value / valuation / gain_on_divestment / gain_basis /
# net_sale_proceeds / announced_date / transaction_date / valuation_date are DROPPED.
# gain_loss_pct is NOT stored -- it derives from sale_price and basis_value at read time.
cur.execute("""select symbol,financial_year,deal_id,transaction_type,status,property_name,
 counterparty,interest_pct,completed_date,
 purchase_price,purchase_price_currency,purchase_price_scope,
 sale_price,sale_price_currency,sale_price_scope,
 basis_value,basis_currency,basis,
 figures_source,basis_mismatch,source_type,currency
 from sgx_reit_property_transaction""")
FLDS=['symbol','financial_year','deal_id','transaction_type','status','property_name',
 'counterparty','interest_pct','completed_date','purchase_price','purchase_price_currency',
 'purchase_price_scope','sale_price','sale_price_currency','sale_price_scope',
 'basis_value','basis_currency','basis','figures_source','basis_mismatch','source_type','currency']
trows=[]
for r in cur.fetchall():
    d=dict(zip(FLDS,r))
    conv={}
    for fld,ccol,dcol in TXN_MONEY:
        ccy=d.get(ccol)
        if ccy is None and d.get(fld) is not None:
            ccy=d.get('currency')          # P1: inherit, but never silently -- record it
            if ccy not in (None,'','SGD'):
                inherited_ccy.append((d['symbol'], d['financial_year'], d.get('property_name'), fld, ccy))
        rdate=d.get(dcol) or d.get('completed_date') or fy_end(d['symbol'],d['financial_year'])
        conv[fld]=to_sgd(d.get(fld), ccy, rdate, f'txn.{fld}.{d["symbol"]}:{d.get("property_name")}')
    # gain derived AFTER both sides are in SGD, so one rate is applied to both
    gain = (conv['sale_price'] - conv['basis_value']) if (conv['sale_price'] is not None
             and conv['basis_value'] is not None and not d.get('basis_mismatch')) else None
    pct  = (gain / conv['basis_value'] * 100) if (gain is not None and conv['basis_value']) else None
    trows.append((d['symbol'],d['financial_year'],d['deal_id'],d['transaction_type'],d['status'],
      d['property_name'],d['counterparty'],
      float(d['interest_pct']) if d['interest_pct'] is not None else None,
      d['completed_date'],
      conv['purchase_price'],d['purchase_price_scope'],
      conv['sale_price'],d['sale_price_scope'],
      conv['basis_value'],d['basis'],
      round(gain,2) if gain is not None else None,
      round(pct,4) if pct is not None else None,
      d['figures_source'],d['basis_mismatch']))
ddl_drop_create('sgx_reit_property_transaction_final',
  'symbol text, financial_year smallint, deal_id text, transaction_type text, status text, '
  'property_name text, counterparty text, interest_pct numeric, completed_date text, '
  'purchase_price numeric, purchase_price_scope text, sale_price numeric, sale_price_scope text, '
  'basis_value numeric, basis text, gain numeric, gain_loss_pct numeric, '
  'figures_source text, basis_mismatch text')
load('sgx_reit_property_transaction_final', ['symbol','financial_year','deal_id','transaction_type',
 'status','property_name','counterparty','interest_pct','completed_date','purchase_price',
 'purchase_price_scope','sale_price','sale_price_scope','basis_value','basis','gain','gain_loss_pct',
 'figures_source','basis_mismatch'], trows)

if inherited_ccy:
    print(f'\n!! P1: {len(inherited_ccy)} money figures had NO per-figure currency tag and inherited a')
    print('   non-SGD row currency. Each was converted on that assumption -- verify against the AR:')
    for sym, fy, pname, fld, ccy in inherited_ccy:
        print(f'     {sym:9s} FY{fy}  {fld:20s} {ccy}  {str(pname)[:52]}')
    if STRICT_CURRENCY:
        conn.rollback()
        raise SystemExit('ABORTED (--strict-currency): backfill the per-figure currency tags above.')

if DRY_RUN:
    print('\n[DRY RUN] no tables written. Row counts:', report)
    conn.rollback()
else:
    conn.commit(); print('\nCOMMITTED. Row counts:', report)
print('\nFX warnings (NULLed):', len(warnings))
for w in warnings[:20]: print('  ', w)
conn.close()
