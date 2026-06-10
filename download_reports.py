#!/usr/bin/env python3
"""Download Singapore REIT annual reports (FY2023-FY2025) with standardized naming.

Filename pattern: {id:02d}_{symbol}_{name-slug}_FY{year}.pdf
Year is standardized to the calendar year the fiscal period ENDS
(e.g. Mapletree FY2024/25 -> FY2025, Starhill FY2023/24 -> FY2024).
"""
import csv
import os
import sys
import time

try:
    import requests
except ImportError:
    sys.exit("requests not installed -- run: pip install requests")

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "annual_reports")
os.makedirs(OUT_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept": "application/pdf,*/*",
}

# (id, symbol, name-slug, year, url, kind)
# kind: "pdf" = direct download | "flipbook"/"manual"/"none" = skip, log for manual handling
ENTRIES = [
    (1, "XZL.SI", "Acrophyte-Hospitality-Trust", 2023, "https://investor.acrophytetrust.com/misc/ar2023/index.html", "flipbook"),
    (1, "XZL.SI", "Acrophyte-Hospitality-Trust", 2024, "https://links.sgx.com/1.0.0/corporate-announcements/N8FF4C24L58G1ZSB/840700_ACRO-HT%20Annual%20Report%20FY2024.pdf", "pdf"),
    (1, "XZL.SI", "Acrophyte-Hospitality-Trust", 2025, "", "none"),

    (2, "O5RU.SI", "AIMS-APAC-REIT", 2023, "https://links.sgx.com/1.0.0/corporate-announcements/2IH9K4VJ3OAQG5NH/763037_AA%20REIT%20AR2023_Final.pdf", "pdf"),
    (2, "O5RU.SI", "AIMS-APAC-REIT", 2024, "https://investor.aimsapacreit.com/ar.html", "manual"),
    (2, "O5RU.SI", "AIMS-APAC-REIT", 2025, "https://investor.aimsapacreit.com/newsroom/20250627_070359_O5RU_312U85OOJ7KGIOXV.1.pdf", "pdf"),

    (3, "M1GU.SI", "Alpha-Integrated-REIT", 2023, "https://links.sgx.com/1.0.0/corporate-announcements/M2CUKRPL9L0C8ZIO/792942_Sabana%20Annual%20Report%202023.pdf", "pdf"),
    (3, "M1GU.SI", "Alpha-Integrated-REIT", 2024, "https://links.sgx.com/1.0.0/corporate-announcements/OH7N6UC7IE4H3D03/836302_Sabana%20Annual%20Report%202024.pdf", "pdf"),
    (3, "M1GU.SI", "Alpha-Integrated-REIT", 2025, "", "none"),

    (4, "BMOU.SI", "BHG-Retail-REIT", 2023, "https://bhgreit.listedcompany.com/newsroom/20240404_172252_BMGU_U5H2ZXLQN3CO9T4L.1.pdf", "pdf"),
    (4, "BMOU.SI", "BHG-Retail-REIT", 2024, "https://bhgreit.listedcompany.com/", "manual"),
    (4, "BMOU.SI", "BHG-Retail-REIT", 2025, "", "none"),

    (5, "A17U.SI", "CapitaLand-Ascendas-REIT", 2023, "https://investor.capitaland-ascendasreit.com/misc/CapitaLand-Ascendas-REIT-AR2023.pdf", "pdf"),
    (5, "A17U.SI", "CapitaLand-Ascendas-REIT", 2024, "https://investor.capitaland-ascendasreit.com/misc/CapitaLand-Ascendas-REIT-AR2024.pdf", "pdf"),
    (5, "A17U.SI", "CapitaLand-Ascendas-REIT", 2025, "https://links.sgx.com/1.0.0/corporate-announcements/VLMUR6L61OAEVKHB/881419_CLAR%20-%20AR%202025.pdf", "pdf"),

    (6, "HMN.SI", "CapitaLand-Ascott-Trust", 2023, "https://investor.capitalandascotttrust.com/misc/agm2024/CLAS-FY2023-AR.pdf", "pdf"),
    (6, "HMN.SI", "CapitaLand-Ascott-Trust", 2024, "https://investor.capitalandascotttrust.com/misc/agm2025/CLAS-FY2024-AR.pdf", "pdf"),
    (6, "HMN.SI", "CapitaLand-Ascott-Trust", 2025, "https://links.sgx.com/1.0.0/corporate-announcements/DUALIJNN4ECM6DZL/880333_1_CLAS%20Annual%20Report%202025.pdf", "pdf"),

    (7, "AU8U.SI", "CapitaLand-China-Trust", 2023, "https://investor.clct.com.sg/misc/ar2023.pdf", "pdf"),
    (7, "AU8U.SI", "CapitaLand-China-Trust", 2024, "https://investor.clct.com.sg/misc/ar2024.pdf", "pdf"),
    (7, "AU8U.SI", "CapitaLand-China-Trust", 2025, "https://investor.clct.com.sg/misc/ar2025.pdf", "pdf"),

    (8, "CY6U.SI", "CapitaLand-India-Trust", 2023, "https://investor.clint.com.sg/misc/CapitaLand-India-Trust-AR2023.pdf", "pdf"),
    (8, "CY6U.SI", "CapitaLand-India-Trust", 2024, "https://investor.clint.com.sg/misc/CapitaLand-India-Trust-AR2024.pdf", "pdf"),
    (8, "CY6U.SI", "CapitaLand-India-Trust", 2025, "https://investor.clint.com.sg/misc/CapitaLand-India-Trust-AR2025.pdf", "pdf"),

    (9, "C38U.SI", "CapitaLand-Integrated-Commercial-Trust", 2023, "https://investor.cict.com.sg/misc/ar2023.pdf", "pdf"),
    (9, "C38U.SI", "CapitaLand-Integrated-Commercial-Trust", 2024, "https://investor.cict.com.sg/misc/ar2024.pdf", "pdf"),
    (9, "C38U.SI", "CapitaLand-Integrated-Commercial-Trust", 2025, "https://investor.cict.com.sg/misc/ar2025.pdf", "pdf"),

    (10, "J85.SI", "CDL-Hospitality-Trusts", 2023, "https://links.sgx.com/FileOpen/CDLHT-AR2023.ashx?App=Announcement&FileID=793259", "pdf"),
    (10, "J85.SI", "CDL-Hospitality-Trusts", 2024, "https://links.sgx.com/FileOpen/CDLHT-AR2024.ashx?App=Announcement&FileID=837284", "pdf"),
    (10, "J85.SI", "CDL-Hospitality-Trusts", 2025, "", "none"),

    (11, "8C8U.SI", "Centurion-Accommodation-REIT", 2023, "", "none"),
    (11, "8C8U.SI", "Centurion-Accommodation-REIT", 2024, "", "none"),
    (11, "8C8U.SI", "Centurion-Accommodation-REIT", 2025, "https://investor.careit.com.sg/misc/ar2025/index.html", "flipbook"),

    (12, "DHLU.SI", "Daiwa-House-Logistics-Trust", 2023, "https://investor.daiwahouse-logisticstrust.com/misc/agm2024/DHLT-AR2023.pdf", "pdf"),
    (12, "DHLU.SI", "Daiwa-House-Logistics-Trust", 2024, "https://investor.daiwahouse-logisticstrust.com/newsroom/20250402_075910_DHLU_TZFO19DL0N64JM51.1.pdf", "pdf"),
    (12, "DHLU.SI", "Daiwa-House-Logistics-Trust", 2025, "https://investor.daiwahouse-logisticstrust.com/misc/agm2026/DHLT-AR2025.pdf", "pdf"),

    (13, "DCRU.SI", "Digital-Core-REIT", 2023, "https://s28.q4cdn.com/669718746/files/doc_downloads/2024/AGM/Digital-Core-REIT-Annual-Report-2023-Web.pdf", "pdf"),
    (13, "DCRU.SI", "Digital-Core-REIT", 2024, "https://s28.q4cdn.com/669718746/files/doc_financials/2024/q4/Digital-Core-REIT-Annual-Report-2024.pdf", "pdf"),
    (13, "DCRU.SI", "Digital-Core-REIT", 2025, "https://s28.q4cdn.com/669718746/files/doc_downloads/2026/03/Digital-Core-REIT-Annual-Report-2025.pdf", "pdf"),

    (14, "MXNU.SI", "Elite-UK-REIT", 2023, "https://links.sgx.com/1.0.0/corporate-announcements/5UCI1I1FXTMTOEQV/796199_Elite%20UK%20REIT-Annual%20Report.pdf", "pdf"),
    (14, "MXNU.SI", "Elite-UK-REIT", 2024, "https://links.sgx.com/1.0.0/corporate-announcements/VMUPUDVJEFHVYAJK/838195_Elite%20UK%20REIT-Annual%20Report%202024.pdf", "pdf"),
    (14, "MXNU.SI", "Elite-UK-REIT", 2025, "https://links.sgx.com/1.0.0/corporate-announcements/714GTQTLJ3NYKLBL/880347_Elite%20UK%20REIT-Annual%20Report%202025.pdf", "pdf"),

    (15, "J91U.SI", "ESR-LOGOS-REIT", 2023, "https://esr-reit.listedcompany.com/misc/ar2023/index.html", "flipbook"),
    (15, "J91U.SI", "ESR-LOGOS-REIT", 2024, "https://esr-reit.listedcompany.com/misc/ar2024/index.html", "flipbook"),
    (15, "J91U.SI", "ESR-LOGOS-REIT", 2025, "https://esr-reit.listedcompany.com/misc/ar2025/index.html", "flipbook"),

    (16, "Q5T.SI", "Far-East-Hospitality-Trust", 2023, "https://links.sgx.com/1.0.0/corporate-announcements/OIAFI1WRZLQOPU6A/792621_FEHT%20Annual%20Report%202023.pdf", "pdf"),
    (16, "Q5T.SI", "Far-East-Hospitality-Trust", 2024, "https://links.sgx.com/1.0.0/corporate-announcements/RJ3PQM8FO861S9KO/837004_FEHT%20AR2024.pdf", "pdf"),
    (16, "Q5T.SI", "Far-East-Hospitality-Trust", 2025, "https://links.sgx.com/1.0.0/corporate-announcements/8DT56CN7KLU5ZJX3/878889_FEHT%20AR2025.pdf", "pdf"),

    (17, "AW9U.SI", "First-REIT", 2023, "https://links.sgx.com/FileOpen/Annual%20Report%20FY2023.ashx?App=Announcement&FileID=795422", "pdf"),
    (17, "AW9U.SI", "First-REIT", 2024, "https://links.sgx.com/1.0.0/corporate-announcements/8JJ6RAFULEZQ96TV/838170_First_REIT_Annual_Report.pdf", "pdf"),
    (17, "AW9U.SI", "First-REIT", 2025, "https://links.sgx.com/1.0.0/corporate-announcements/V8ZYLJV6UA0ODE6T/881430_First_REIT_Annual_Report_2025.pdf", "pdf"),

    (18, "J69U.SI", "Frasers-Centrepoint-Trust", 2023, "https://links.sgx.com/FileOpen/FCT%20AR%202023.ashx?App=Announcement&FileID=781334", "pdf"),
    (18, "J69U.SI", "Frasers-Centrepoint-Trust", 2024, "https://links.sgx.com/1.0.0/corporate-announcements/6CLTX7B8ENVEL9UV/828582_Annual_Report_FCT.pdf", "pdf"),
    (18, "J69U.SI", "Frasers-Centrepoint-Trust", 2025, "https://links.sgx.com/FileOpen/FCT%20AR%202025.ashx?App=Announcement&FileID=870392", "pdf"),

    (19, "BUOU.SI", "Frasers-Logistics-and-Commercial-Trust", 2023, "https://links.sgx.com/FileOpen/FLCT_Annual_Report_2023.ashx?App=Announcement&FileID=781334", "pdf"),
    (19, "BUOU.SI", "Frasers-Logistics-and-Commercial-Trust", 2024, "https://flct.frasersproperty.com/misc/FLCT-AR2024.pdf", "pdf"),
    (19, "BUOU.SI", "Frasers-Logistics-and-Commercial-Trust", 2025, "https://flct.frasersproperty.com/misc/FLCT-AR2025.pdf", "pdf"),

    (20, "UD1U.SI", "IREIT-Global", 2023, "https://investor.ireitglobal.com/misc/ar2023.pdf", "pdf"),
    (20, "UD1U.SI", "IREIT-Global", 2024, "https://investor.ireitglobal.com/newsroom/20250402_073227_UD1U_ZQ03BR1CN2DBQC0V.1.pdf", "pdf"),
    (20, "UD1U.SI", "IREIT-Global", 2025, "https://investor.ireitglobal.com/newsroom/20260326_073047_UD1U_TAAV8JQHHQQHBTQR.1.pdf", "pdf"),

    (21, "AJBU.SI", "Keppel-DC-REIT", 2023, "https://www.keppeldcreit.com/en/file/investor-relations/publications/annual-report/kdcr-ar-2023.pdf", "pdf"),
    (21, "AJBU.SI", "Keppel-DC-REIT", 2024, "https://www.keppeldcreit.com/en/file/investor-relations/publications/annual-report/kdcr-ar2024.pdf", "pdf"),
    (21, "AJBU.SI", "Keppel-DC-REIT", 2025, "https://www.keppeldcreit.com/en/file/investor-relations/publications/annual-report/kdcr-ar2025.pdf", "pdf"),

    (22, "CMOU.SI", "KORE-US-REIT", 2023, "https://www.koreusreit.com/file/downloads/2024/keppel-pacific-oak-us-reit-annual-report-2023.pdf", "pdf"),
    (22, "CMOU.SI", "KORE-US-REIT", 2024, "https://www.koreusreit.com/file/downloads/2025/keppel-pacific-oak-us-reit-annual-report-2024.pdf", "pdf"),
    (22, "CMOU.SI", "KORE-US-REIT", 2025, "https://www.koreusreit.com/file/downloads/2026/kore-us-reit-annual-report-2025.pdf", "pdf"),

    (23, "K71U.SI", "Keppel-REIT", 2023, "https://www.keppelreit.com/file/investor-relations/publications/annual-reports/kreit-ar23.pdf", "pdf"),
    (23, "K71U.SI", "Keppel-REIT", 2024, "https://www.keppelreit.com/file/investor-relations/publications/annual-reports/kreit-ar24-website.pdf", "pdf"),
    (23, "K71U.SI", "Keppel-REIT", 2025, "https://www.keppelreit.com/file/investor-relations/publications/annual-reports/keppel-reit-ar25.pdf", "pdf"),

    (24, "JYEU.SI", "Lendlease-Global-Commercial-REIT", 2023, "https://www.lendleaseglobalcommercialreit.com/siteassets/publications/2023/lendlease-ar2023-web.pdf", "pdf"),
    (24, "JYEU.SI", "Lendlease-Global-Commercial-REIT", 2024, "https://links.sgx.com/1.0.0/corporate-announcements/1CV3JP458PTTTDQR/820765_Lendlease%20AR24.pdf", "pdf"),
    (24, "JYEU.SI", "Lendlease-Global-Commercial-REIT", 2025, "https://www.lendleaseglobalcommercialreit.com/siteassets/publications/annual-reports/annual-report-fy2025.pdf", "pdf"),

    (25, "D5IU.SI", "Landmark-REIT", 2023, "https://lmir.listedcompany.com/newsroom/20240403_063456_D5IU_DSINMXMIUKTHJYXY.1.pdf", "pdf"),
    (25, "D5IU.SI", "Landmark-REIT", 2024, "https://lmir.listedcompany.com/newsroom/20250404_064606_D5IU_BP8HE8VLOS2KQTR6.1.pdf", "pdf"),
    (25, "D5IU.SI", "Landmark-REIT", 2025, "", "none"),

    (26, "BTOU.SI", "Manulife-US-REIT", 2023, "https://investor.manulifeusreit.sg/publications.html", "manual"),
    (26, "BTOU.SI", "Manulife-US-REIT", 2024, "https://www.manulifeusreit.sg/assets/pdf/Manulife-AR2024.pdf", "pdf"),
    (26, "BTOU.SI", "Manulife-US-REIT", 2025, "https://investor.manulifeusreit.sg/newsroom/20260414_071310_BTOU_1D8FNAX92XYZKWQ5.1.pdf", "pdf"),

    (27, "ME8U.SI", "Mapletree-Industrial-Trust", 2023, "https://links.sgx.com/1.0.0/corporate-announcements/VU8628XHDTKMM5EV/762868_20230620_MIT%20Annual%20Report_2022_2023.pdf", "pdf"),
    (27, "ME8U.SI", "Mapletree-Industrial-Trust", 2024, "https://links.sgx.com/1.0.0/corporate-announcements/SUBLTCKIESQ86HBG/806807_20240618_%20MIT%20AR2023_2024.pdf", "pdf"),
    (27, "ME8U.SI", "Mapletree-Industrial-Trust", 2025, "https://investor.mapletreeindustrialtrust.com/newsroom/20250625_073214_ME8U_UQG8RIVWFVIRDJZO.1.pdf", "pdf"),

    (28, "M44U.SI", "Mapletree-Logistics-Trust", 2023, "https://links.sgx.com/1.0.0/corporate-announcements/WQEKME6QKGFRE0M7/763652_20230628-MLT-Annual%20Report%202022-23.pdf", "pdf"),
    (28, "M44U.SI", "Mapletree-Logistics-Trust", 2024, "https://links.sgx.com/FileOpen/20240625-MLT-AR2023-24.ashx?App=Announcement&FileID=807491", "pdf"),
    (28, "M44U.SI", "Mapletree-Logistics-Trust", 2025, "https://investor.mapletreelogisticstrust.com/newsroom/20250620_071305_M44U_W4WC665GQ77T049L.1.pdf", "pdf"),

    (29, "N2IU.SI", "Mapletree-Pan-Asia-Commercial-Trust", 2023, "https://investor.mapletreepact.com/investor-resources.html", "manual"),
    (29, "N2IU.SI", "Mapletree-Pan-Asia-Commercial-Trust", 2024, "https://investor.mapletreepact.com/investor-resources.html", "manual"),
    (29, "N2IU.SI", "Mapletree-Pan-Asia-Commercial-Trust", 2025, "https://investor.mapletreepact.com/newsroom/20250627_071024_N2IU_A865ED2W965R9N0P.1.pdf", "pdf"),

    (30, "NTDU.SI", "NTT-DC-REIT", 2023, "", "none"),
    (30, "NTDU.SI", "NTT-DC-REIT", 2024, "", "none"),
    (30, "NTDU.SI", "NTT-DC-REIT", 2025, "", "none"),

    (31, "TS0U.SI", "OUE-REIT", 2023, "https://investor.ouereit.com/misc/OUEREIT_AR2023.pdf", "pdf"),
    (31, "TS0U.SI", "OUE-REIT", 2024, "https://investor.ouereit.com/misc/OUEREIT_AR2024.pdf", "pdf"),
    (31, "TS0U.SI", "OUE-REIT", 2025, "https://investor.ouereit.com/misc/OUE_REIT_Annual_Report_2025.pdf", "pdf"),

    (32, "C2PU.SI", "Parkway-Life-REIT", 2023, "https://links.sgx.com/1.0.0/corporate-announcements/A6OLK2A8MOSEM756/793482_Parkway%20Life%20REIT%20-%20Annual%20Report%20FY2023.pdf", "pdf"),
    (32, "C2PU.SI", "Parkway-Life-REIT", 2024, "https://links.sgx.com/FileOpen/Parkway%20Life%20REIT%20-%20Annual%20Report%202024.ashx?App=Announcement&FileID=837824", "pdf"),
    (32, "C2PU.SI", "Parkway-Life-REIT", 2025, "", "none"),

    (33, "OXMU.SI", "Prime-US-REIT", 2023, "https://www.primeusreit.com/misc/ar2023.pdf", "pdf"),
    (33, "OXMU.SI", "Prime-US-REIT", 2024, "https://www.primeusreit.com/misc/ar2024.pdf", "pdf"),
    (33, "OXMU.SI", "Prime-US-REIT", 2025, "https://www.primeusreit.com/misc/ar2025.pdf", "pdf"),

    (34, "CRPU.SI", "Sasseur-REIT", 2023, "https://links.sgx.com/1.0.0/corporate-announcements/3WR1ZIWDU8A3FD8S/794350_Sasseur_REIT-Annual_Report_FY2023.pdf", "pdf"),
    (34, "CRPU.SI", "Sasseur-REIT", 2024, "https://www.sasseurreit.com/misc/sr2024.pdf", "pdf"),
    (34, "CRPU.SI", "Sasseur-REIT", 2025, "", "none"),

    (35, "P40U.SI", "Starhill-Global-REIT", 2023, "https://starhillglobalreit.listedcompany.com/misc/ar/ar2023.pdf", "pdf"),
    (35, "P40U.SI", "Starhill-Global-REIT", 2024, "https://starhillglobalreit.listedcompany.com/misc/Starhill-Annual-Report-2024.pdf", "pdf"),
    (35, "P40U.SI", "Starhill-Global-REIT", 2025, "https://starhillglobalreit.listedcompany.com/misc/SGREIT-FY2425-Annual-Report.pdf", "pdf"),

    (36, "SET.SI", "Stoneweg-Europe-Stapled-Trust", 2023, "https://investor.stonewegeuropestapledtrust.com.sg/newsroom/20240411_065229_CWCU_GE3FUTSJTR45AHH8.1.pdf", "pdf"),
    (36, "SET.SI", "Stoneweg-Europe-Stapled-Trust", 2024, "https://investor.stonewegeuropestapledtrust.com.sg/newsroom/20250404_203459_CWCU_Q6LA9K39M61IP31G.1.pdf", "pdf"),
    (36, "SET.SI", "Stoneweg-Europe-Stapled-Trust", 2025, "https://investor.stonewegeuropestapledtrust.com.sg/misc/SERT_AR_2025_14_Apr.pdf", "pdf"),

    (37, "T82U.SI", "Suntec-REIT", 2023, "https://suntecreit.listedcompany.com/misc/ar2023/SuntecREITAnnualReport2023.pdf", "pdf"),
    (37, "T82U.SI", "Suntec-REIT", 2024, "https://suntecreit.listedcompany.com/newsroom/20250325_073831_T82U_2BYFMY5WOSSNEU8J.1.pdf", "pdf"),
    (37, "T82U.SI", "Suntec-REIT", 2025, "https://suntecreit.listedcompany.com/newsroom/20260401_074618_T82U_2A9T8NEG2VQBDHNM.1.pdf", "pdf"),

    (38, "UIBU.SI", "UI-Boustead-REIT", 2023, "", "none"),
    (38, "UIBU.SI", "UI-Boustead-REIT", 2024, "", "none"),
    (38, "UIBU.SI", "UI-Boustead-REIT", 2025, "", "none"),

    (39, "ODBU.SI", "United-Hampshire-US-REIT", 2023, "https://investor.uhreit.com/newsroom/20240328_073710_ODBU_7M32I7APVUAXXLKY.1.pdf", "pdf"),
    (39, "ODBU.SI", "United-Hampshire-US-REIT", 2024, "https://investor.uhreit.com/newsroom/20250404_073558_ODBU_SWQ2FKO1ARIMC219.1.pdf", "pdf"),
    (39, "ODBU.SI", "United-Hampshire-US-REIT", 2025, "https://investor.uhreit.com/misc/ar2025.pdf", "pdf"),
]


def download(url, dest):
    """Return (ok, message). ok=True only if a real PDF was saved."""
    for attempt in range(3):
        try:
            r = requests.get(url, headers=HEADERS, timeout=60, stream=True, allow_redirects=True)
            if r.status_code != 200:
                if attempt < 2:
                    time.sleep(2)
                    continue
                return False, f"HTTP {r.status_code}"
            tmp = dest + ".part"
            first = b""
            with open(tmp, "wb") as f:
                for chunk in r.iter_content(8192):
                    if not first:
                        first = chunk[:5]
                    f.write(chunk)
            if not first.startswith(b"%PDF"):
                os.remove(tmp)
                return False, "not a PDF (likely HTML page)"
            os.replace(tmp, dest)
            size = os.path.getsize(dest)
            return True, f"{size/1_000_000:.1f} MB"
        except Exception as e:
            if attempt < 2:
                time.sleep(2)
                continue
            return False, f"error: {e}"
    return False, "failed"


def main():
    manifest = []
    print(f"Output folder: {OUT_DIR}\n")
    for rid, symbol, slug, year, url, kind in ENTRIES:
        fname = f"{rid:02d}_{symbol}_{slug}_FY{year}.pdf"
        dest = os.path.join(OUT_DIR, fname)
        if kind != "pdf":
            reason = {"none": "not published / not applicable",
                      "flipbook": "online flipbook only (no PDF)",
                      "manual": "IR landing page only (no direct PDF)"}[kind]
            print(f"SKIP  {fname:<70} {reason}")
            manifest.append([rid, symbol, slug.replace("-", " "), year, "SKIPPED", reason, url])
            continue
        if os.path.exists(dest):
            print(f"EXIST {fname:<70} already downloaded")
            manifest.append([rid, symbol, slug.replace("-", " "), year, "OK", "already present", url])
            continue
        ok, msg = download(url, dest)
        status = "OK" if ok else "FAILED"
        print(f"{status:<5} {fname:<70} {msg}")
        manifest.append([rid, symbol, slug.replace("-", " "), year, status, msg, url])

    with open(os.path.join(OUT_DIR, "_manifest.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "symbol", "name", "fiscal_year", "status", "detail", "source_url"])
        w.writerows(manifest)

    ok = sum(1 for m in manifest if m[4] == "OK")
    failed = sum(1 for m in manifest if m[4] == "FAILED")
    skipped = sum(1 for m in manifest if m[4] == "SKIPPED")
    print(f"\nDone. Downloaded/present: {ok} | Failed: {failed} | Skipped: {skipped}")
    print(f"Manifest: {os.path.join(OUT_DIR, '_manifest.csv')}")


if __name__ == "__main__":
    main()
