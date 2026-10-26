import json
import re
import sys
from collections import Counter
from pathlib import Path

KOK = Path(__file__).resolve().parent
SORU = {
    "ne", "nasıl", "kim", "kimin", "kime", "kimden", "kimlerin", "kimler", "kimdir", "nedir", "nereden", "hangi", "neden", "niçin",
    "nerede", "ne", "mi", "mı", "mu", "mü", "ve", "ile", "bir", "bu", "o", "şu", "için", "olan", "olur", "ise", "de", "da", "gibi",
    "her", "çok", "ki", "ya", "ama", "fakat", "daha", "en", "bütün", "diğer", "hâle", "hâli", "hâl", "eder", "ister", "yapar", "başlanır",
    "bulur", "davranır", "uğramıştır", "yoludur", "bekler", "denir", "diler", "hisseder", "nasıldır", "kimlerdir", "yapar",
}


def kelimeler(metin):
    sonuc = []
    for k in re.findall(r"[a-zçğıöşüâîû]+", re.sub(r"'[a-zçğıöşüâîû]*", "", metin.replace("İ", "i").replace("I", "ı").lower())):
        if k not in SORU and len(k) > 2:
            sonuc.append(k)
    return sonuc


def eslesir(a, b):
    n = min(4, len(a), len(b))
    return n >= 3 and a[:n] == b[:n]


def var(k, havuz):
    return any(eslesir(k, h) for h in havuz)


def konum(r):
    s, a = re.match(r"(\d+):(\d+)", r).groups()
    return int(s), int(a)


def meal():
    d = json.load(open(KOK.parent / "nazm_blok.json", encoding="utf-8"))
    return {(v["s"], v["a"]): " ".join(b[1] for b in v["b"]) for v in d.values()}


def cevaplar(d):
    gaye = {g["id"]: g for g in d["gayeler"]}
    cocuk = {}
    for g in d["gayeler"]:
        for u in g["ust"]:
            cocuk.setdefault(u, []).append(g["id"])
    dogrudan = {}
    for k in d["kararlar"]:
        for i in k["gaye"]:
            dogrudan.setdefault(i, set()).update(konum(r) for r in k["karsilik"])

    def kapsam(x, gorulen=frozenset()):
        s = set(dogrudan.get(x, set()))
        for c in cocuk.get(x, []):
            if c not in gorulen:
                s |= kapsam(c, gorulen | {x})
        return s

    return gaye, {i: kapsam(i) for i in gaye}


def denetle(d, mealler):
    gaye, kap = cevaplar(d)
    kok = d["kok_gaye"]
    verilmis_kok = set(kelimeler(gaye[kok]["sual"]))
    sonuc = {}
    for i, g in gaye.items():
        if not kap[i]:
            continue
        ilk = min(kap[i])
        onceki = [mealler[x] for x in sorted(mealler) if x < ilk and x[0] == ilk[0]]
        baglam = set(w for m in onceki for w in kelimeler(m)) | verilmis_kok
        cevap = set(w for x in kap[i] for w in kelimeler(mealler[x]))
        yeni_cevapta, yeni_hicbir = [], []
        for k in kelimeler(g["sual"]):
            if var(k, baglam):
                continue
            (yeni_cevapta if var(k, cevap) else yeni_hicbir).append(k)
        if yeni_cevapta:
            etiket = "cevap sizintisi"
        elif yeni_hicbir:
            etiket = "uydurma"
        else:
            etiket = "yeni mefhum yok"
        odak = kelimeler(g["sual"])
        onde = mealler.get(max((x for x in mealler if x < ilk and x[0] == ilk[0]), default=None), "") if onceki else ""
        cipa = set(kelimeler(onde)) | verilmis_kok
        if not odak:
            alaka = "dayanmaz"
        else:
            say = sum(var(k, cipa) for k in odak)
            alaka = "tam dayanir" if say == len(odak) else ("dayanmaz" if say == 0 else "kismen dayanir")
        sonuc[i] = (etiket, alaka, yeni_cevapta, yeni_hicbir)
    return sonuc


if __name__ == "__main__":
    yol = sys.argv[1] if len(sys.argv) > 1 else KOK / "FATIHA_KARARLAR.json"
    d = json.load(open(yol, encoding="utf-8"))
    s = denetle(d, meal())
    for i, (e, a, yc, yh) in s.items():
        print(i, e, "|", a, "|", yc, yh)
    print("verilmislik", dict(Counter(v[0] for v in s.values())))
    print("capa alakasi", dict(Counter(v[1] for v in s.values())))
