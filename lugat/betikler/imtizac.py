#!/usr/bin/env python3
import csv
import glob
import json
import os
import re
import sys
import unicodedata

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from karsilik_oku import karsiliklari_oku

KITALAR = {
    "A": "Anatomy", "B": "Organisms", "C": "Diseases", "D": "Chemicals and Drugs",
    "E": "Analytical, Diagnostic and Therapeutic Techniques, and Equipment",
    "F": "Psychiatry and Psychology", "G": "Phenomena and Processes",
    "H": "Disciplines and Occupations",
    "I": "Anthropology, Education, Sociology, and Social Phenomena",
    "J": "Technology, Industry, and Agriculture", "K": "Humanities",
    "L": "Information Science", "M": "Named Groups", "N": "Health Care",
    "V": "Publication Characteristics", "Z": "Geographicals",
}


def normallestir(s):
    s = unicodedata.normalize("NFKC", s or "").casefold()
    s = s.replace("’", "'").replace("‘", "'")
    s = re.sub(r"[‐-―-]", " ", s)
    s = re.sub(r"[,;:()\[\]]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def bab_anahtari(no):
    no = str(no).strip()
    return "ICD11-bab:" + (no.lstrip("0") or "0")


def jsonl_oku(yol):
    with open(yol, encoding="utf-8") as f:
        return [json.loads(s) for s in f if s.strip()]


def main(ham=os.path.join(KOK, "ham"), karsilik_klasoru=os.path.join(KOK, "karsiliklar"),
         cikti=os.path.join(KOK, "telif")):
    os.makedirs(cikti, exist_ok=True)
    mesh = jsonl_oku(os.path.join(ham, "mesh_tavsifler.jsonl"))
    icd = jsonl_oku(os.path.join(ham, "icd11_unsurlar.jsonl"))

    maddeler = {}
    def yapi(kimlik, ad, ebeveyn):
        maddeler[kimlik] = {"kimlik": kimlik, "yapi_dugumu": True, "ingilizce": ad,
                            "ebeveynler": [ebeveyn] if ebeveyn else [], "kaynaklar": [],
                            "esanlamlilar": [], "tarif": None, "karsiliklar": []}
    yapi("KOK", "Medical lexicon (merged)", None)
    yapi("MeSH-kok", "Medical Subject Headings", "KOK")
    yapi("ICD11-kok", "International Classification of Diseases, 11th Revision (MMS)", "KOK")
    for harf, ad in KITALAR.items():
        yapi(f"MeSH-kita:{harf}", ad, "MeSH-kok")

    agac_ui = {}
    for t in mesh:
        for n in t["agac_numaralari"]:
            agac_ui[n] = t["ui"]
    for t in mesh:
        ebeveynler = []
        for n in t["agac_numaralari"]:
            if "." in n:
                ust = agac_ui.get(n.rsplit(".", 1)[0])
                ebeveynler.append(f"MeSH:{ust}" if ust else f"MeSH-kita:{n[0]}")
            else:
                ebeveynler.append(f"MeSH-kita:{n[0]}")
        if not t["agac_numaralari"]:
            ebeveynler.append("MeSH-kok")
        maddeler[f"MeSH:{t['ui']}"] = {
            "kimlik": f"MeSH:{t['ui']}", "yapi_dugumu": False, "ingilizce": t["ad"],
            "ebeveynler": sorted(set(ebeveynler)),
            "kaynaklar": [dict(t, tasnif="MeSH")],
            "esanlamlilar": list(t["giris_terimleri"]), "tarif": t.get("tarif"),
            "diger_kavramlar": list(t.get("diger_kavramlar", [])),
            "karsiliklar": [],
        }

    mesh_dizin = {}
    for t in mesh:
        for ad in [t["ad"]] + t["giris_terimleri"]:
            mesh_dizin.setdefault(normallestir(ad), set()).add(t["ui"])
    icd_ad_sayisi = {}
    for u in icd:
        if not u["artik"] and u["ad"]:
            n = normallestir(u["ad"])
            icd_ad_sayisi[n] = icd_ad_sayisi.get(n, 0) + 1
    adaylar, muhtemel = {}, []
    for u in icd:
        if u["artik"] or not u["ad"]:
            continue
        n = normallestir(u["ad"])
        uiler = mesh_dizin.get(n)
        if not uiler:
            continue
        if len(uiler) == 1 and icd_ad_sayisi[n] == 1:
            adaylar.setdefault(next(iter(uiler)), []).append(u)
        else:
            muhtemel.append((u, sorted(uiler), "ad birden fazla tavsife yahut unsura ait"))
    birlesme = {}
    for ui, unsurlar in adaylar.items():
        if len(unsurlar) == 1:
            birlesme[unsurlar[0]["adres"]] = ui
        else:
            for u in unsurlar:
                muhtemel.append((u, [ui], "aynı tavsife birden fazla unsur eşleşti"))

    def icd_kimlik(adres):
        if adres in birlesme:
            return f"MeSH:{birlesme[adres]}"
        return f"ICD11:{adres.split('/mms/')[-1]}"
    for u in icd:
        kimlik = icd_kimlik(u["adres"])
        eb = [icd_kimlik(u["ebeveyn"])] if u.get("ebeveyn") else ["ICD11-kok"]
        kaynak = dict(u, tasnif="ICD-11")
        if u["adres"] in birlesme:
            m = maddeler[kimlik]
            m["kaynaklar"].append(kaynak)
            m["ebeveynler"] = sorted(set(m["ebeveynler"] + eb))
            if u.get("tarif") and not m.get("tarif_icd"):
                m["tarif_icd"] = u["tarif"]
        else:
            maddeler[kimlik] = {
                "kimlik": kimlik, "yapi_dugumu": False, "ingilizce": u["ad"],
                "ebeveynler": eb, "kaynaklar": [kaynak], "esanlamlilar": [],
                "tarif": u.get("tarif"), "karsiliklar": [],
            }
    for m in maddeler.values():
        m["ebeveynler"] = [e for e in m["ebeveynler"] if e != m["kimlik"]] or (["KOK"] if m["kimlik"] != "KOK" else [])

    anahtar = {}
    def ekle(k, kimlik):
        anahtar.setdefault(k, set()).add(kimlik)
    for kimlik, m in maddeler.items():
        ekle(kimlik, kimlik)
        for kay in m["kaynaklar"]:
            if kay["tasnif"] == "MeSH":
                ekle(f"MeSH-ad:{kay['ad']}", kimlik)
                for n in kay["agac_numaralari"]:
                    ekle(f"MeSH-agac:{n}", kimlik)
            else:
                ekle(f"ICD11:{kay['kimlik']}", kimlik)
                if kay.get("kod"):
                    ekle(f"ICD11-kod:{kay['kod']}", kimlik)
                if kay.get("ad"):
                    ekle(f"ICD11-ad:{kay['ad']}", kimlik)
                if kay.get("sinif_nevi") == "chapter" and (kay.get("bab_no") or kay.get("kod")):
                    ekle(bab_anahtari(kay.get("bab_no") or kay.get("kod")), kimlik)
    eslesmeyen = []
    karsiliklar = karsiliklari_oku(karsilik_klasoru)
    uyusmazlik = []
    for k in karsiliklar:
        aranan = bab_anahtari(k["kimlik"][len("ICD11-bab:"):]) if k["kimlik"].startswith("ICD11-bab:") else k["kimlik"]
        hedef = anahtar.get(aranan)
        if hedef and len(hedef) == 1:
            m = maddeler[next(iter(hedef))]
            m["karsiliklar"].append(k)
            if k["ingilizce"] and normallestir(k["ingilizce"]) != normallestir(m["ingilizce"]):
                uyusmazlik.append((k, m))
        else:
            k = dict(k, eslesmeme_sebebi="madde yok" if not hedef else "birden fazla madde")
            eslesmeyen.append(k)

    sirali = sorted(maddeler.values(), key=lambda m: (not m["yapi_dugumu"], m["kimlik"]))
    with open(os.path.join(cikti, "tip_lugati.jsonl"), "w", encoding="utf-8") as f:
        for m in sirali:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")
    with open(os.path.join(cikti, "tip_lugati.tsv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["kimlik", "ingilizce", "osmanlica", "muhur", "ebeveynler", "kaynaklar"])
        for m in sirali:
            k = m["karsiliklar"][-1] if m["karsiliklar"] else {}
            w.writerow([m["kimlik"], m["ingilizce"], k.get("osmanlica", ""), k.get("muhur", ""),
                        " | ".join(m["ebeveynler"]),
                        " + ".join(sorted({x["tasnif"] for x in m["kaynaklar"]}))])
    with open(os.path.join(cikti, "tekrarlar.tsv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["mesh_ui", "mesh_adi", "icd_adresi", "icd_kodu", "icd_adi"])
        for adres, ui in sorted(birlesme.items(), key=lambda x: x[1]):
            u = next(x for x in maddeler[f"MeSH:{ui}"]["kaynaklar"] if x["tasnif"] == "ICD-11")
            w.writerow([ui, maddeler[f"MeSH:{ui}"]["ingilizce"], adres, u.get("kod") or "", u["ad"]])
    with open(os.path.join(cikti, "muhtemel_tekrarlar.tsv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["icd_adresi", "icd_adi", "mesh_uiler", "sebep"])
        for u, uiler, sebep in muhtemel:
            w.writerow([u["adres"], u["ad"], " ".join(uiler), sebep])
    with open(os.path.join(cikti, "eslesmeyen_karsiliklar.tsv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["dosya", "kimlik", "ingilizce", "osmanlica", "muhur", "sebep"])
        for k in eslesmeyen:
            w.writerow([k["dosya"], k["kimlik"], k["ingilizce"], k["osmanlica"], k["muhur"], k["eslesmeme_sebebi"]])

    with open(os.path.join(cikti, "ingilizce_uyusmazligi.tsv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["dosya", "satir", "kimlik", "karsilik_dosyasindaki_ingilizce", "maddedeki_ingilizce", "osmanlica"])
        for k, m in uyusmazlik:
            w.writerow([k["dosya"], k["satir"], m["kimlik"], k["ingilizce"], m["ingilizce"], k["osmanlica"]])

    icerik = [m for m in maddeler.values() if not m["yapi_dugumu"]]
    kunye = {
        "birinci_tasnif_mesh_tavsif": len(mesh),
        "ikinci_tasnif_icd11_unsur": len(icd),
        "tekrar": len(birlesme),
        "muhtemel_tekrar_birlestirilmedi": len(muhtemel),
        "telif_madde_sayisi": len(icerik),
        "yapi_dugumu_sayisi": len(maddeler) - len(icerik),
        "karsilik_satiri": len(karsiliklar),
        "eslesmeyen_karsilik": len(eslesmeyen),
        "ingilizce_uyusmazligi": len(uyusmazlik),
        "karsiligi_olan_madde": sum(1 for m in icerik if m["karsiliklar"]),
    }
    with open(os.path.join(cikti, "imtizac_kunye.json"), "w", encoding="utf-8") as f:
        json.dump(kunye, f, ensure_ascii=False, indent=2)
    print(json.dumps(kunye, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    if len(sys.argv) == 4:
        main(*sys.argv[1:])
    else:
        main()
