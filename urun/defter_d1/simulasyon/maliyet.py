import csv
import pathlib

import guc


def kalem_toplami(p):
    kur = p["genel"]["kur_tl_dolar"]
    alt = sum(k["usd_min"] for k in p["bom"])
    ust = sum(k["usd_max"] for k in p["bom"])
    return alt, ust, alt * kur, ust * kur


def yerlilige_gore(p):
    sonuc = {}
    for k in p["bom"]:
        sonuc.setdefault(k["yerlilik"], [0.0, 0.0, 0])
        sonuc[k["yerlilik"]][0] += k["usd_min"]
        sonuc[k["yerlilik"]][1] += k["usd_max"]
        sonuc[k["yerlilik"]][2] += 1
    return sonuc


def cikarma_tasarrufu(p):
    kur = p["genel"]["kur_tl_dolar"]
    ad_to_kalem = {k["ad"]: k for k in p["bom"]}
    sonuc = {}
    for baslik, adlar in p["cikarilabilir_kalemler"].items():
        alt = sum(ad_to_kalem[a]["usd_min"] for a in adlar)
        ust = sum(ad_to_kalem[a]["usd_max"] for a in adlar)
        sonuc[baslik] = (alt, ust, alt * kur, ust * kur)
    return sonuc


def csv_yaz(p, yol):
    yol = pathlib.Path(yol)
    with yol.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["ad", "adet", "usd_min", "usd_max", "tl_perakende", "yerlilik", "isaret", "not"])
        for k in p["bom"]:
            w.writerow([k["ad"], k["adet"], k["usd_min"], k["usd_max"],
                        "" if k["tl_perakende"] is None else k["tl_perakende"], k["yerlilik"], k["isaret"], k["not"]])


def rapor(p):
    alt, ust, alt_tl, ust_tl = kalem_toplami(p)
    satirlar = []
    satirlar.append("MALZEME LİSTESİ TOPLAMI: %.1f – %.1f dolar (%.0f – %.0f TL, kur %.0f)" % (
        alt, ust, alt_tl, ust_tl, p["genel"]["kur_tl_dolar"]))
    satirlar.append("")
    satirlar.append("%-28s %8s %8s %6s" % ("yerlilik sınıfı", "alt $", "üst $", "kalem"))
    for sinif, (a, u, n) in sorted(yerlilige_gore(p).items()):
        satirlar.append("%-28s %8.1f %8.1f %6d" % (sinif, a, u, n))
    satirlar.append("")
    satirlar.append("ÇIKARILABİLİR KALEMLERİN TASARRUFU:")
    for baslik, (a, u, atl, utl) in cikarma_tasarrufu(p).items():
        satirlar.append("  %-14s %.1f – %.1f dolar (%.0f – %.0f TL)" % (baslik, a, u, atl, utl))
    bulunan = [(k["ad"], k["tl_perakende"]) for k in p["bom"] if k["tl_perakende"] is not None]
    satirlar.append("")
    satirlar.append("YERLİ PERAKENDE TL FİYATI BULUNAN KALEMLER (yalnız %d kalem):" % len(bulunan))
    for ad, tl in bulunan:
        satirlar.append("  %s: %.2f TL (KDV dahil)" % (ad, tl))
    return "\n".join(satirlar)


if __name__ == "__main__":
    p = guc.parametreleri_yukle()
    print(rapor(p))
    csv_yaz(p, guc.KOK / "donanim" / "bom.csv")
