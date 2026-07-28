import json, datetime

OUT = "extracted/D5IU.SI_FY2024"
SYM = "D5IU.SI"; FY = 2024

def iso(d):
    return datetime.datetime.strptime(d, "%d %B %Y").strftime("%Y-%m-%d")

def exp_iso(d):
    return datetime.datetime.strptime(d, "%d %B %Y").strftime("%Y-%m-%d")

# name, acq_date, pp_bn, val_bn, val_sgd_000, gfa, nla, occ, expiry, tenants, gr_m, npi_m, tenure_raw, own
P = [
 ("Kediri Town Square","22 December 2017",345.0,398.2,33407,28688,16824,98.3,"12 August 2044",87,3.7,2.0,"HGB title, expires on 12 August 2044",100.0),
 ("Lippo Mall Kuta","29 December 2016",800.0,244.0,20471,49487,21065,92.4,"22 March 2037",74,2.0,0.1,"HGB title, expires on 22 March 2037",100.0),
 ("Lippo Plaza Batu","7 July 2015",265.0,268.1,22491,30310,19104,98.0,"8 June 2031",83,2.3,1.0,"HGB title, expires on 8 June 2031",100.0),
 ("Lippo Plaza Jogja","22 December 2017",570.0,204.0,17115,66498,21151,71.7,"27 December 2043",45,2.1,0.6,"HGB title, expires on 27 December 2043",68.3),
 ("Lippo Plaza Kramat Jati","15 October 2012",539.6,591.1,49593,65511,32049,77.2,"17 May 2027",84,5.0,2.6,"HGB title, expires on 17 May 2027",100.0),
 ("Mal Lippo Cikarang","19 November 2007",367.2,899.1,75435,41216,30613,96.2,"5 May 2043",182,9.6,6.0,"HGB title, expires on 5 May 2043",100.0),
 ("Plaza Madiun Units","19 November 2007",171.2,225.5,18918,19991,11299,94.7,"9 February 2032",32,2.6,1.4,"HGB title, expires on 9 February 2032",100.0),
 ("Sun Plaza","31 March 2008",967.2,2773.0,232648,166070,71245,90.5,"24 November 2032",264,26.1,19.0,"HGB title, expires on 24 November 2032",100.0),
 ("Depok Town Square Units","19 November 2007",131.5,150.8,12654,13045,12824,48.8,"27 February 2035",3,0.4,0.2,"Strata title constructed on HGB title common land, expires on 27 February 2035",100.0),
 ("Gajah Mada Plaza","19 November 2007",483.3,908.2,76197,86894,29428,73.2,"24 January 2040",124,4.4,1.5,"Strata title constructed on HGB Title common land, expires on 24 January 2040",100.0),
 ("Grand Palladium Units","19 November 2007",134.0,58.8,4927,13730,12305,0.0,"9 November 2028",0,None,None,"Strata title constructed on HGB title common land, expires on 9 November 2028",100.0),
 ("Java Supermall Units","19 November 2007",133.1,132.3,11103,11082,11082,98.8,"24 September 2037",3,1.0,0.9,"Strata title constructed on HGB title common land, expires on 24 September 2037",100.0),
 ("Lippo Mall Kemang","17 December 2014",3540.4,2281.3,191395,150932,57627,89.1,"28 June 2035",217,18.6,10.3,"Strata title constructed on HGB title common land, expires on 28 June 2035",100.0),
 ("Lippo Mall Puri","27 January 2021",3500.0,4233.4,355174,174645,122611,94.8,"15 January 2040",442,38.9,27.9,"Strata title constructed on HGB title common land, expires on 15 January 2040",100.0),
 ("Malang Town Square Units","19 November 2007",130.8,166.9,14000,11065,10402,41.0,"21 April 2033",3,1.3,1.2,"Strata title constructed on HGB title, expires on 21 April 2033",100.0),
 ("Mall WTC Matahari Units","19 November 2007",128.9,78.4,6578,11184,10985,37.7,"8 April 2038",2,0.4,0.1,"Strata title constructed on HGB title common land, expires on 8 April 2038",100.0),
 ("Metropolis Town Square Units","19 November 2007",171.8,76.8,6441,15248,15248,100.0,"27 December 2029",4,0.2,None,"Strata title constructed on HGB title common land, expires on 27 December 2029",100.0),
 ("Palembang Square","14 November 2012",467.0,631.5,52977,44850,31689,63.1,"2 September 2039",117,3.8,2.7,"Strata title constructed on HGB title common land, expires on 2 September 2039",100.0),
 ("Tamini Square","14 November 2012",180.0,130.6,10958,18963,17561,24.2,"25 September 2035",17,0.4,-0.2,"Strata title constructed on HGB title common land, expires on 25 September 2035",100.0),
 ("Bandung Indah Plaza","19 November 2007",611.6,362.8,30433,75868,30361,85.9,"31 December 2030",172,7.5,4.3,"ABS, expires on 31 December 2030",100.0),
 ("Cibubur Junction","19 November 2007",464.2,462.4,38797,66935,31726,87.4,"29 July 2045",100,6.7,3.8,"ABS, expires on 29 July 2045",100.0),
 ("Istana Plaza","19 November 2007",585.3,228.8,19200,47534,27359,56.3,"17 January 2034",38,1.3,0.1,"ABS, expires on 17 January 2034",100.0),
 ("Lippo Mall Nusantara (formerly known as The Plaza Semanggi)","19 November 2007",1013.8,869.0,72907,155122,66640,26.9,"31 March 2054",117,3.2,-1.2,"ABS, expires on 31 March 2054",100.0),
 ("Lippo Plaza Ekalokasari Bogor","19 November 2007",333.0,160.1,13433,58859,28829,70.9,"27 June 2032",47,3.1,0.7,"ABS, expires on 27 June 2032",100.0),
 ("Lippo Plaza Kendari","21 June 2017",310.0,291.6,24463,34831,20807,87.2,"2 November 2042",39,3.5,2.0,"ABS, expires on 2 November 2042",100.0),
 ("Palembang Icon","10 July 2015",790.0,939.6,78832,50889,29410,82.5,"30 April 2040",170,11.9,8.1,"ABS, expires on 30 April 2040",100.0),
 ("Palembang Square Extension","15 October 2012",221.5,274.1,22996,23825,18352,95.5,"25 January 2041",18,3.7,2.0,"ABS, expires on 25 January 2041",100.0),
 ("Plaza Medan Fair","6 December 2011",1042.1,396.7,33278,141866,67567,95.2,"23 July 2027",382,19.1,12.9,"ABS, expires on 23 July 2027",100.0),
 ("Pluit Village","6 December 2011",1593.6,181.0,15185,150905,85866,84.3,"9 June 2027",227,11.8,5.7,"ABS, expires on 9 June 2027",100.0),
]

props = []
for (name,acq,ppbn,valbn,valsgd,gfa,nla,occ,exp,ten,gr,npi,traw,own) in P:
    props.append({
        "symbol":SYM,"financial_year":FY,"property_name":name,"country":"Indonesia",
        "category":"Retail","category_raw":"Retail",
        "address":None,
        "ownership":own,
        "market_valuation":valsgd*1000,
        "purchase_price":round(ppbn*1e9),
        "purchase_price_currency":"IDR",
        "purchase_date":iso(acq),
        "valuation_date":"2024-12-31","currency":"SGD",
        "original_currency":"IDR","original_value":round(valbn*1e9),
        "net_property_income":(round(npi*1e6) if npi is not None else None),
        "gross_revenue":(round(gr*1e6) if gr is not None else None),
        "npi_pct":None,"occupancy_rate":occ,
        "major_tenants":[],
        "gla":None,"nla":float(nla),"gfa":float(gfa),"area_unit":"sqm",
        "land_tenure":"Leasehold","effective_date":None,"lease_term_years":None,
        "lease_expiry_date":exp_iso(exp),"tenure_raw":traw,
        "status":"active","flags":[],"source_page":89,
    })

json.dump(props, open(f"{OUT}/properties.json","w"), indent=1, ensure_ascii=False)
print("properties", len(props), "sum_val", sum(p['market_valuation'] for p in props))
print("sum_gr", sum(p['gross_revenue'] or 0 for p in props), "sum_npi", sum(p['net_property_income'] or 0 for p in props))
