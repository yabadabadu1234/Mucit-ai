#!/usr/bin/env python3
import csv
import json
import os
import sys
from collections import Counter

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from karsilik_oku import karsiliklari_oku


def jsonl(yol):
    with open(yol, encoding="utf-8") as f:
        return [json.loads(s) for s in f if s.strip()]


def main(ham=os.path.join(KOK, "ham"), karsilik_klasoru=os.path.join(KOK, "karsiliklar"),
         telif=os.path.join(KOK, "telif")):
    hatalar = []
    mesh = jsonl(os.path.join(ham, "mesh_tavsifler.jsonl"))
    icd = jsonl(os.path.join(ham, "icd11_unsurlar.jsonl"))
    maddeler = jsonl(os.path.join(telif, "tip_lugati.jsonl"))
    kimlikler = {m["kimlik"]: m for m in maddeler}
    if len(kimlikler) != len(maddeler):
        hatalar.append("telifte aynı kimlikli iki madde var")

    mesh_say = Counter()
    icd_say = Counter()
    tekrar = 0
    for m in maddeler:
        tasnifler = [k["tasnif"] for k in m["kaynaklar"]]
        for k in m["kaynaklar"]:
            if k["tasnif"] == "MeSH":
                mesh_say[k["ui"]] += 1
            else:
                icd_say[k["adres"]] += 1
        if "MeSH" in tasnifler:
            tekrar += tasnifler.count("ICD-11")
        if not m["yapi_dugumu"] and not m["kaynaklar"]:
            hatalar.append(f"{m['kimlik']}: kaynaksız madde")

    for t in mesh:
        if mesh_say[t["ui"]] != 1:
            hatalar.append(f"MeSH {t['ui']} telifte {mesh_say[t['ui']]} defa geçiyor")
    for u in icd:
        if icd_say[u["adres"]] != 1:
            hatalar.append(f"ICD-11 {u['adres']} telifte {icd_say[u['adres']]} defa geçiyor")
    fazla = (set(mesh_say) - {t["ui"] for t in mesh}) | (set(icd_say) - {u["adres"] for u in icd})
    if fazla:
        hatalar.append(f"hamda olmayan {len(fazla)} kaynak telifte var")

    icerik = sum(1 for m in maddeler if not m["yapi_dugumu"])
    beklenen = len(mesh) + len(icd) - tekrar
    if icerik != beklenen:
        hatalar.append(f"sayı tutmadı: {icerik} madde, beklenen {len(mesh)} + {len(icd)} - {tekrar} = {beklenen}")

    for m in maddeler:
        for e in m["ebeveynler"]:
            if e not in kimlikler:
                hatalar.append(f"{m['kimlik']}: olmayan ebeveyn {e}")
    koke_ulasan = {"KOK"}
    def ulasir(k, yol):
        if k in koke_ulasan:
            return True
        if k in yol:
            hatalar.append(f"devir: {' -> '.join(list(yol) + [k])}")
            return False
        yol.append(k)
        sonuc = any(ulasir(e, yol) for e in kimlikler[k]["ebeveynler"] if e in kimlikler)
        yol.pop()
        if sonuc:
            koke_ulasan.add(k)
        return sonuc
    sys.setrecursionlimit(100000)
    for k in kimlikler:
        if not ulasir(k, []):
            hatalar.append(f"{k}: köke ulaşmıyor")

    karsiliklar = karsiliklari_oku(karsilik_klasoru)
    bagli = Counter((k["dosya"], k["satir"]) for m in maddeler for k in m["karsiliklar"])
    eslesmeyen = Counter()
    yol = os.path.join(telif, "eslesmeyen_karsiliklar.tsv")
    if os.path.exists(yol):
        with open(yol, encoding="utf-8") as f:
            for s in csv.DictReader(f, delimiter="\t"):
                eslesmeyen[(s["dosya"], s["kimlik"], s["osmanlica"])] += 1
    for k in karsiliklar:
        if bagli[(k["dosya"], k["satir"])] == 1:
            continue
        anahtar = (k["dosya"], k["kimlik"], k["osmanlica"])
        if eslesmeyen[anahtar] > 0:
            eslesmeyen[anahtar] -= 1
            continue
        hatalar.append(f"karşılık düştü: {k['dosya']}:{k['satir']} {k['osmanlica']}")

    rapor = {
        "birinci_tasnif": len(mesh), "ikinci_tasnif": len(icd), "tekrar": tekrar,
        "hesap": f"{len(mesh)} + {len(icd)} - {tekrar} = {beklenen}",
        "telif_madde_sayisi": icerik, "karsilik_satiri": len(karsiliklar),
        "netice": "DOĞRU" if not hatalar else "HATALI",
    }
    print(json.dumps(rapor, ensure_ascii=False, indent=2))
    for h in hatalar[:200]:
        print("HATA:", h)
    if len(hatalar) > 200:
        print(f"... ve {len(hatalar) - 200} hata daha")
    sys.exit(1 if hatalar else 0)


if __name__ == "__main__":
    if len(sys.argv) == 4:
        main(*sys.argv[1:])
    else:
        main()
