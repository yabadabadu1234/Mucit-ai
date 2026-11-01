#!/usr/bin/env python3
import argparse
import concurrent.futures as cf
import csv
import datetime
import io
import json
import os
import sys
import threading
import time
import urllib.parse
import urllib.request
import zipfile

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JETON_ADRESI = "https://icdaccessmanagement.who.int/connect/token"
ARAYUZ = "https://id.who.int/icd/release/11"
VARSAYILAN_CEDVEL = "https://icdcdn.who.int/static/releasefiles/{surum}/SimpleTabulation-ICD-11-MMS-en.zip"


class Arayuz:
    def __init__(self, kimlik, sir, lisan="en"):
        self.kimlik, self.sir, self.lisan = kimlik, sir, lisan
        self.jeton, self.jeton_vakti = None, 0
        self.kilit = threading.Lock()

    def _jeton_al(self):
        veri = urllib.parse.urlencode({
            "client_id": self.kimlik, "client_secret": self.sir,
            "scope": "icdapi_access", "grant_type": "client_credentials",
        }).encode()
        with urllib.request.urlopen(urllib.request.Request(JETON_ADRESI, data=veri), timeout=60) as c:
            cevap = json.load(c)
        self.jeton = cevap["access_token"]
        self.jeton_vakti = time.time() + int(cevap.get("expires_in", 3600)) - 120

    def getir(self, adres):
        adres = adres.replace("http://", "https://", 1)
        for deneme in range(6):
            with self.kilit:
                if not self.jeton or time.time() > self.jeton_vakti:
                    self._jeton_al()
                jeton = self.jeton
            istek = urllib.request.Request(adres, headers={
                "Authorization": "Bearer " + jeton, "Accept": "application/json",
                "Accept-Language": self.lisan, "API-Version": "v2",
            })
            try:
                with urllib.request.urlopen(istek, timeout=60) as c:
                    return json.load(c)
            except Exception as e:
                if deneme == 5:
                    raise
                print(f"tekrar deneniyor ({deneme + 1}): {adres}: {e}", file=sys.stderr)
                time.sleep(2 ** deneme)


def deger(alan):
    if isinstance(alan, dict):
        return alan.get("@value")
    return alan


def arayuzden_indir(a, cikti):
    api = Arayuz(os.environ["ICD_CLIENT_ID"], os.environ["ICD_CLIENT_SECRET"])
    surum = a.surum
    if not surum:
        ust = api.getir(ARAYUZ + "/mms")
        surum = ust["latestRelease"].rstrip("/").split("/")[-2]
    kok_adres = f"{ARAYUZ}/{surum}/mms"
    ara = os.path.join(cikti, "icd11_ara_kayit.jsonl")
    gorulen = {}
    if os.path.exists(ara):
        with open(ara, encoding="utf-8") as f:
            for satir in f:
                k = json.loads(satir)
                gorulen[k["adres"]] = k
        print(f"ara kayıttan {len(gorulen)} unsur okundu, devam ediliyor", file=sys.stderr)

    kok = api.getir(kok_adres)
    sira = [(c, None) for c in kok.get("child", [])]
    yazici = open(ara, "a", encoding="utf-8")
    kilit = threading.Lock()

    def isle(adres, ebeveyn):
        adres = adres.replace("http://", "https://", 1)
        if adres in gorulen:
            return gorulen[adres]
        e = api.getir(adres)
        kayit = {
            "adres": adres,
            "kimlik": adres.split("/mms/")[-1],
            "ebeveyn": ebeveyn,
            "ebeveynler": [p.replace("http://", "https://", 1) for p in e.get("parent", [])],
            "kod": e.get("code") or None,
            "blok": e.get("blockId") or None,
            "kod_araligi": e.get("codeRange") or None,
            "sinif_nevi": e.get("classKind"),
            "ad": deger(e.get("title")),
            "tarif": deger(e.get("definition")),
            "temel_adres": e.get("source"),
            "artik": adres.endswith("/other") or adres.endswith("/unspecified"),
            "cocuklar": [c.replace("http://", "https://", 1) for c in e.get("child", [])],
        }
        with kilit:
            yazici.write(json.dumps(kayit, ensure_ascii=False) + "\n")
            gorulen[adres] = kayit
        return kayit

    with cf.ThreadPoolExecutor(a.isci) as havuz:
        while sira:
            gelecekler = [havuz.submit(isle, ad, eb) for ad, eb in sira]
            sira = []
            for g in gelecekler:
                k = g.result()
                sira.extend((c, k["adres"]) for c in k["cocuklar"])
            print(f"{len(gorulen)} unsur", file=sys.stderr)
    yazici.close()
    return surum, kok_adres, list(gorulen.values())


def cedvelden_oku(a):
    if a.yerel:
        with open(a.yerel, "rb") as f:
            ham = f.read()
        adres = "yerel:" + a.yerel
    else:
        adres = a.cedvel_adresi or VARSAYILAN_CEDVEL.format(surum=a.surum or "2025-01")
        print(f"indiriliyor: {adres}", file=sys.stderr)
        with urllib.request.urlopen(adres, timeout=300) as c:
            ham = c.read()
    if ham[:2] == b"PK":
        z = zipfile.ZipFile(io.BytesIO(ham))
        adlar = [n for n in z.namelist() if n.lower().endswith((".txt", ".tsv"))]
        if not adlar:
            raise SystemExit("Arşivde sekmeyle ayrılmış metin dosyası yok: " + ", ".join(z.namelist()))
        ham = z.read(adlar[0])
    metin_ = ham.decode("utf-8-sig")
    okuyucu = csv.DictReader(io.StringIO(metin_), delimiter="\t")
    kayitlar, yigin = [], []
    for s in okuyucu:
        baslik = s.get("Title") or ""
        derinlik = 0
        while baslik.startswith("- "):
            derinlik += 1
            baslik = baslik[2:]
        adres = (s.get("Linearization URI") or s.get("Linearization (release) URI") or "").strip()
        adres = adres.replace("http://", "https://", 1)
        while yigin and yigin[-1][0] >= derinlik:
            yigin.pop()
        ebeveyn = yigin[-1][1] if yigin else None
        kayit = {
            "adres": adres,
            "kimlik": adres.split("/mms/")[-1] if "/mms/" in adres else adres,
            "ebeveyn": ebeveyn,
            "ebeveynler": [ebeveyn] if ebeveyn else [],
            "kod": (s.get("Code") or "").strip() or None,
            "blok": (s.get("BlockId") or "").strip() or None,
            "kod_araligi": None,
            "sinif_nevi": (s.get("ClassKind") or "").strip() or None,
            "ad": baslik.strip(),
            "tarif": None,
            "temel_adres": (s.get("Foundation URI") or "").strip() or None,
            "artik": (s.get("IsResidual") or "").strip().lower() == "true",
            "bab_no": (s.get("ChapterNo") or "").strip() or None,
        }
        kayitlar.append(kayit)
        yigin.append((derinlik, adres))
    return a.surum, adres, kayitlar


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--surum", help="mesela 2025-01; verilmezse en yenisi")
    p.add_argument("--cedvel-adresi")
    p.add_argument("--yerel", help="önceden indirilmiş SimpleTabulation dosyası (zip yahut txt)")
    p.add_argument("--isci", type=int, default=8)
    p.add_argument("--cikti", default=os.path.join(KOK, "ham"))
    a = p.parse_args()
    os.makedirs(a.cikti, exist_ok=True)

    if not a.yerel and not a.cedvel_adresi and os.environ.get("ICD_CLIENT_ID") and os.environ.get("ICD_CLIENT_SECRET"):
        yol = "resmî uygulama arayüzü"
        surum, adres, kayitlar = arayuzden_indir(a, a.cikti)
    else:
        yol = "resmî neşir cedveli"
        surum, adres, kayitlar = cedvelden_oku(a)

    kimlikler = [k["adres"] for k in kayitlar]
    if len(set(kimlikler)) != len(kimlikler):
        raise SystemExit("Aynı adresli iki unsur çıktı; dosya bozuk olabilir.")

    hedef = os.path.join(a.cikti, "icd11_unsurlar.jsonl")
    with open(hedef + ".yarim", "w", encoding="utf-8") as f:
        for k in kayitlar:
            k.pop("cocuklar", None)
            f.write(json.dumps(k, ensure_ascii=False) + "\n")
    os.replace(hedef + ".yarim", hedef)

    nevi = {}
    for k in kayitlar:
        nevi[k["sinif_nevi"]] = nevi.get(k["sinif_nevi"], 0) + 1
    kunye = {
        "kaynak": "International Classification of Diseases 11th Revision, Mortality and Morbidity Statistics, World Health Organization",
        "yol": yol,
        "adres": adres,
        "surum": surum,
        "indirme_vakti": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "unsur_sayisi": len(kayitlar),
        "kodlu_unsur_sayisi": sum(1 for k in kayitlar if k["kod"]),
        "sinif_nevine_gore": nevi,
    }
    with open(os.path.join(a.cikti, "icd11_kunye.json"), "w", encoding="utf-8") as f:
        json.dump(kunye, f, ensure_ascii=False, indent=2)
    print(json.dumps(kunye, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
