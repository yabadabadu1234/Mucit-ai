#!/usr/bin/env python3
import argparse
import datetime
import gzip
import hashlib
import json
import os
import sys
import urllib.request
import xml.etree.ElementTree as ET

ANA_ADRES = "https://nlmpubs.nlm.nih.gov/projects/mesh/MESH_FILES/xmlmesh/"

KITALAR = {
    "A": "Anatomy",
    "B": "Organisms",
    "C": "Diseases",
    "D": "Chemicals and Drugs",
    "E": "Analytical, Diagnostic and Therapeutic Techniques, and Equipment",
    "F": "Psychiatry and Psychology",
    "G": "Phenomena and Processes",
    "H": "Disciplines and Occupations",
    "I": "Anthropology, Education, Sociology, and Social Phenomena",
    "J": "Technology, Industry, and Agriculture",
    "K": "Humanities",
    "L": "Information Science",
    "M": "Named Groups",
    "N": "Health Care",
    "V": "Publication Characteristics",
    "Z": "Geographicals",
}

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def indir(adres, hedef):
    gecici = hedef + ".yarim"
    with urllib.request.urlopen(adres, timeout=120) as cevap, open(gecici, "wb") as f:
        while True:
            parca = cevap.read(1 << 20)
            if not parca:
                break
            f.write(parca)
    os.replace(gecici, hedef)


def dosya_bul(sene, klasor):
    seneler = [sene] if sene else [datetime.date.today().year + 1 - i for i in range(4)]
    hatalar = []
    for s in seneler:
        for uzanti in ("gz", "xml"):
            ad = f"desc{s}.{uzanti}"
            adres = ANA_ADRES + ad
            hedef = os.path.join(klasor, ad)
            if os.path.exists(hedef):
                return s, adres, hedef
            try:
                print(f"indiriliyor: {adres}", file=sys.stderr)
                indir(adres, hedef)
                return s, adres, hedef
            except Exception as e:
                hatalar.append(f"{adres}: {e}")
    raise SystemExit("Hiçbir dosya indirilemedi:\n" + "\n".join(hatalar))


def metin(dugum, yol):
    e = dugum.find(yol)
    return e.text.strip() if e is not None and e.text else None


def ayristir(dosya):
    acici = gzip.open if dosya.endswith(".gz") else open
    with acici(dosya, "rb") as f:
        for olay, dugum in ET.iterparse(f, events=("end",)):
            if dugum.tag != "DescriptorRecord":
                continue
            kayit = {
                "ui": metin(dugum, "DescriptorUI"),
                "ad": metin(dugum, "DescriptorName/String"),
                "agac_numaralari": [t.text.strip() for t in dugum.findall("TreeNumberList/TreeNumber") if t.text],
                "tarif": None,
                "giris_terimleri": [],
                "tavsif_sinifi": dugum.get("DescriptorClass"),
            }
            for kavram in dugum.findall("ConceptList/Concept"):
                if kavram.get("PreferredConceptYN") == "Y":
                    kayit["tarif"] = metin(kavram, "ScopeNote")
                for terim in kavram.findall("TermList/Term/String"):
                    if terim.text and terim.text.strip() != kayit["ad"]:
                        kayit["giris_terimleri"].append(terim.text.strip())
            kayit["giris_terimleri"] = sorted(set(kayit["giris_terimleri"]))
            yield kayit
            dugum.clear()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--sene", type=int)
    p.add_argument("--yerel", help="önceden indirilmiş desc dosyasının yolu")
    p.add_argument("--cikti", default=os.path.join(KOK, "ham"))
    a = p.parse_args()
    os.makedirs(a.cikti, exist_ok=True)

    if a.yerel:
        sene, adres, dosya = a.sene, "yerel:" + a.yerel, a.yerel
    else:
        indirme_klasoru = os.path.join(a.cikti, "indirilen")
        os.makedirs(indirme_klasoru, exist_ok=True)
        sene, adres, dosya = dosya_bul(a.sene, indirme_klasoru)

    hedef = os.path.join(a.cikti, "mesh_tavsifler.jsonl")
    sayi, agacli, agac_numarasi = 0, 0, 0
    kita_sayilari = {k: 0 for k in KITALAR}
    with open(hedef + ".yarim", "w", encoding="utf-8") as f:
        for k in ayristir(dosya):
            sayi += 1
            if k["agac_numaralari"]:
                agacli += 1
            agac_numarasi += len(k["agac_numaralari"])
            for harf in {t[0] for t in k["agac_numaralari"]}:
                kita_sayilari[harf] = kita_sayilari.get(harf, 0) + 1
            f.write(json.dumps(k, ensure_ascii=False) + "\n")
    os.replace(hedef + ".yarim", hedef)

    with open(dosya, "rb") as f:
        ozet = hashlib.sha256(f.read()).hexdigest()
    kunye = {
        "kaynak": "Medical Subject Headings, National Library of Medicine",
        "adres": adres,
        "sene": sene,
        "indirme_vakti": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "sha256": ozet,
        "tavsif_sayisi": sayi,
        "agacta_yeri_olan_tavsif_sayisi": agacli,
        "agac_numarasi_sayisi": agac_numarasi,
        "kitalar": KITALAR,
        "kita_basina_tavsif_sayisi": kita_sayilari,
    }
    with open(os.path.join(a.cikti, "mesh_kunye.json"), "w", encoding="utf-8") as f:
        json.dump(kunye, f, ensure_ascii=False, indent=2)
    print(json.dumps(kunye, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
