# Per-report data inventories (LlamaParse agentic, FY2025 sample)

Detailed findings from one analysis pass per parsed report. Page refs are `<!-- PAGE N -->`
marker numbers in each `full.md`. See `../schema_analysis.md` for the cross-report synthesis.

---

## 09 CapitaLand Integrated Commercial Trust (C38U.SI) — retail/office, SGD, Dec FYE

**Section map:** Highlights p4; Financial Highlights (5-yr) p5; ESG highlights p6; Trust structure p9; Portfolio valuation pp23–24; Financial review (per-property GR/NPI, DPU) pp25–26; Capital management pp27–29; Trading p30; Operations review pp32–38; Property details (22 properties) pp39–64; CG report pp65–89; Risk pp90–95; FS pp97–190 (SoFP p105, Total Return p106, Distribution p107, Portfolio Statement pp109–110, Cash Flows pp111–112, Notes pp113–190); IPT pp191–192; Unitholdings pp193–195.

**Key data:** 5-yr summary FY2021–25 (GR 1,305.1→1,619.2 S$m, NPI, distributable income, total assets, NAV/unit 2.06→2.14, DPU 10.40→11.58¢, MER, leverage, ICR, cost of debt). Per-property valuation + S$psf (p23) with cap-rate ranges by geography (p24: SG retail 4.35–6.20%). Per-property GR AND NPI (pp25–26). Occupancy/WALE by segment, lease expiry 2026–2031+, top 10 tenants (% GRI + trade sector), 18-category trade mix, tenure profile (13% freehold, wtd avg 91 yrs). Debt: leverage 38.6%, S$10.0b borrowings, 74% fixed, ICR 3.7x + sensitivity, maturity profile 2026–2035 by instrument (p29), ratings A3/A−, green financing 63.1%. DPU by sub-period with unit-base footnotes (p26). Top 20 holders (89.03%), Temasek 21.39% deemed, float ~71%. Monthly price/volume + 5-yr trading table (p30). Fees: base 0.25% DP, perf 4.25% NPI, cap 0.70% (pp113–115). Segments: Retail/Office/ID + geography, Note 31 (pp184–187). CEO comp exact (pp79–80). IPT p191. ESG: targets/ratings only — **consumption data in separate SR**.

**Sector-specific:** tenant sales +14.9% psf, shopper traffic +20.5%, occupancy cost 17.0%, rent reversion +6.6% (retail and office), retention 83.7%, office rents psf per building, AEI pipeline with capex/ROI, GTO rent ~7% of GRI.

**Parse quality:** face statements have merged unit rows (`$'000 $'000`) and note numbers fused into labels; Note 5 movement table garbled; duplicate capital-mgmt table (p27); chart-tables missing year headers; footnote superscripts stick to values; heading hierarchy noisy.

---

## 21 Keppel DC REIT (AJBU.SI) — data centres, SGD, Dec FYE

**Section map:** Key figures p4; Financial highlights p8 (**2 years only — no 5-yr table**); Unit price p19; Market review pp21–34; Portfolio review pp35–44 (per-property "At A Glance" pp40–44); Financial review pp45–50; **Sustainability report in-document pp51–94** (GRI pp86–88, IFRS S2 p92, DNV assurance); FS pp96–158 (Portfolio Statement pp110–114, Notes pp115–158); CG report pp159–185; IPT pp189–190; Unitholdings pp191–192; Financial calendar p193.

**Key data:** FY25 vs FY24: GR 441.4/310.3 S$m, NPI 383.3, distributable income 268.1, DPU 10.381/9.451¢ + half-year split; NAV 1.71, adjusted NAV 1.66, leverage 35.3%, ICR 7.5x (+sensitivity), cost of debt 3.0%, 71.2% hedged, debt maturity % by year 2026–2031, 100% unencumbered, no credit rating. 25 properties with address, leasehold expiry, ownership %, land/GFA/lettable sq ft, # clients, **lease type (colocation/single-tenant/shell&core)**, occupancy, attributable GR, purchase price, valuation. WALE by contract type; expiry profile by area AND rental income; rental income by trade sector (Internet Enterprise 69.3%); top 10 clients **anonymised** (top = 42.1%); one client = 66% of revenue (Note 34). Fees: base 0.5% DP, perf 3.5% NPI (p119). Segments by lease type + geography (pp156–158). ESG: Scope 1/2/3 for 2019/2023/2024/2025, energy GJ, water ML, VPPAs, IFRS S2 metrics table p92. Top 20 holders, Temasek 21.21%, float 78.75%. Valuation input ranges APAC/Europe (p154).

**Sector-specific:** lease typology is the core dimension; dual WALE (6.7y area / 4.9y income); PUE only as % improvement; market MW supply/take-up per city (consultant data pp21–34); income support $7.2m; deferred payment liability.

**Parse quality:** donut charts duplicated as twin key-value tables; p39 magazine text became a fake 3-col table repeated twice; KPI callouts parsed as H1 (`# 10.381 cts`); "At A Glance" headers duplicated; debt-maturity table layout confusing (as-at year vs maturity-year axis); only 2 years of financials.

---

## 28 Mapletree Logistics Trust (M44U.SI) — logistics 9 countries, SGD, **March FYE (FY24/25 = YE 31 Mar 2025)**

**Section map:** Financial highlights (5-yr) pp6–7; Unit price pp8–9; Financial review pp33–39; Capital management pp40–43; Portfolio analysis pp46–54; Operations review (1 page/country) pp55–63; Property portfolio pp64–83; CG report pp84–107; FS: P&L p121, SoFP p123, Distribution pp124–125, Cash flows pp126–127, **Portfolio Statements pp130–173 (~180 properties)**, Notes pp174–228; Unitholdings pp229–230; IPT pp231–232.

**Key data:** 5 yrs: GR 727.0 S$m, NPI 625.3, distributable 406.4, DPU 8.053¢, AUM 13.3bn, NAV 1.31, leverage 40.7%, ICR 2.9x, cost of debt 2.7%, perpetuals 582.4. Audited per-property: legal completion date, lease terms, **GR FY24/25 vs FY23/24, occupancy both years, valuation both years + valuer**, % net assets. Occupancy by country; rental reversion by country (China −11.4%, AU +27.9%); top 10 customers (Equinix 3.7%...= 21.7%); 16-sector trade mix; SUA/MTB split by country; lease expiry by NLA and revenue; land lease expiry, freehold 24% NLA, land WALE 41.2y; valuation by country with % variance; acquisition/divestment tables with dual valuations + buyers. Debt by 8 currencies (JPY 28%), 81% fixed, Fitch BBB+, maturity FY25/26–FY31/32+ by instrument, green/SLL 24%, 75% of income hedged. Quarterly DPU with exact periods + payment dates (p113, p124). Top 20 (84.95%), Temasek 33.55%, float 66.42%. Fees: base 0.5% DP, perf 3.6% NPI (p174). Segments = 9 countries, Note 29 (pp221–226). Cap/discount-rate ranges per country, 2 yrs (pp194–195). CEO comp exact S$1,131,668 (p99). ESG: headline KPIs only — **full data in separate SR**.

**Parse quality:** face statements parsed worst of the 5 (page header became table header, unit row collapsed, dash placeholders merged into labels shifting columns); p7 dual-donut garbled; magazine 3-col text duplicated as scrambled table (p51); lease-expiry tables have a duplicated "FY29/30" row (second is likely FY30/31+); Portfolio Statements rowspan-heavy but complete; superscripts inside numerics.

---

## 17 First REIT (AW9U.SI) — healthcare ID/JP/SG, SGD, Dec FYE

**Section map:** Financial highlights pp5–7; Market review pp20–25; Property overview (31 property cards) pp28–44; IR pp45–46; **Sustainability report pp47–90** (ESG data pp77–80, TCFD pp67–76, GRI pp81–88, SASB p89); CG pp91–119; FS pp120–199 (SoFP p126, Total Return p127, Distribution p128, **Portfolio pp135–145**, Notes pp146–199); IPT p200; Unitholdings pp201–203.

**Key data:** 5 yrs: rental income 102.3→100.5 S$m, DPU 2.61→2.17¢, AUM 962→1,023 S$m; ratios: ICR 3.7x, leverage 42.1%, 46.1% fixed, **78.7% social-finance debt**. Per-property cards: type, land area, purchase price (local ccy), land title (freehold/HGB/BOT), **max beds/rooms**, lease term + exact expiry + renewal option, tenant, valuer, GFA, FY25 rental, appraised value local ccy + SGD. Tenant ranking: Siloam 44.3% + Lippo Karawaci 30.7% + MPU 5.7% ≈ 80.7% Lippo-ecosystem. Facility-level debt (CGIF-guaranteed bond 3.25% 2027, social loans, TMK bonds, JPY tranches) with full terms table; covenants (TL/HF ≤1.05, HF ≥S$500m); perps S$33.3m. Quarterly DPU + payment dates (p46, p176). Top 20 (OLH 27.42%), substantial-holder chain ~19 entities up to 45.72% deemed, float 54.13%. Fees: base 0.4% DP, perf 5.0% NPI, Japan AM fee 0.4% (pp146–147). Segments = 3 countries (pp179–180). Discount rates per country incl. restructured vs non-restructured Indonesia split (pp161–163). CEO comp exact S$525,725 (p104). ESG: Scope 2/3, energy GWh, intensities, 2 yrs (pp77–80); no GRESB, no green certs.

**Sector-specific:** restructured MLAs (2021, expiry 31 Dec 2035 + 15-yr option); MPU arrears IDR 89.25bn + settlement disclosure (p44); IDR exposure 82.5% of income, NDF hedging; BOT land titles drive valuation treatment; 100% occupancy by construction (master leases); 6,305 beds/rooms.

**Parse quality:** property-card stat strips sometimes duplicate a *previous* property's table (dedupe by first-table-after-header); appraised-value columns split local/SGD with units on separate rows; relative-return chart parsed with only first/last rows; market-review tables are chart-eyeballed (low precision); FS table headers shredded across 5–7 rows (column order consistent); ESG units rowspan-misattached; OCR soft-hyphen splits ("defi ned").

---

## 16 Far East Hospitality Trust (Q5T.SI) — hospitality, **stapled trust (REIT + BT)**, SGD, Dec FYE

**Section map:** Key highlights (5-yr) p4; Structure p7; Portfolio pp21–30; Industry overview (CBRE) pp33–41; Performance review pp42–45; Capital management p46; IR pp47–49; **Sustainability pp51–84**; CG pp89–125 (remuneration pp107–108, IPT pp112–113); H-BT policies/fees pp126–135; FS pp136–216 (SoFP p149, Total Return pp150–151, Distribution pp152–153, Portfolio pp157–158, Notes pp161–216); **separate Trustee-Manager company FS pp217–233**; Unitholdings pp235–237.

**Key data:** 5 yrs: GR 83.2→111.4 S$m, NPI 96.6, DPU 3.70¢ (0.39¢ from divestment gains), leverage 33.0%, ICR 3.6x, NAV 87.6¢. **FS have 3 entity columns: Stapled Group / H-REIT Group / H-BT Group**; revenue split master-lease rental (86.1) / retail&office (18.3) / hotel revenue (6.8, owner-operated FPN) / carpark. Per-property: rooms, floor area, NLA, FY25 revenue, remaining tenure, valuation, purchase price, **master lessee name**. Commercial: top 10 tenants, F&B 63%, WALE 1.34y. Debt: S$774.8m, 53.5% fixed, cost 3.1%, maturity 2026–2032 SG vs JPY, 64% SLL, unrated, headroom S$925.1m. Per-period DPS with taxable/exempt/capital split. Top 20 (81.39%), Ng Teng Fong estate 40.48% deemed, float 45.07%. Fees: base 0.28% DP, perf 4.0% NPI-or-distributable (lower), Trustee-Manager 10% of H-BT EBIT (nil paid); 60% of fees in units. Segments: hotels&SRs vs commercial (pp210–212). Valuation inputs incl. **RevPAR input $124–276 and price per room $0.47–1.59m** (pp208–209). ESG: full Scope 1/2/3, energy, water, waste, 3 yrs (pp62–65). CEO comp exact S$960,642.

**Sector-specific:** hotel occupancy 81.3% / ADR S$170 / RevPAR S$139; SR occupancy/ADR/RevPAU; corporate-vs-leisure mix; guest nationality mix; 20+20-yr master leases with fixed rent (receivables S$493.3m) vs Japan **GOP-variable rent, no minimum** (stapled-internal lease); CBRE market series (visitor arrivals, market ADR/RevPAR 2014–2025, price-per-room transactions).

**Parse quality:** charts → approximate integer tables (unit-price chart digitized); orphan mis-attached chart table at p32; Portfolio Statement subtotal labels shifted one row from values (p157); debt-maturity 2031 row collapsed (value lost); structure diagram emitted as mermaid with run-together words; running-head H1s repeated ~50×; IPT rowspan offsets.
