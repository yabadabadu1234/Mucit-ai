import copy
import json
import re
import sys
from collections import Counter

TUR = {"tasavvur", "tasdik", "his", "irade", "statu", "celb-i-menfaat", "def-i-mefsedet"}
ZIHNI = {"tasavvur", "tasdik", "his", "irade"}
TASIYICI = {"muhatap", "baskasi"}
UFUK = {"dunya", "ahiret"}
KIP = {"yeni", "hatirlatma", "pekistirme", "duzeltme"}
ILIM_CINSI = {"nazari", "ameli"}
SICIL = json.load(open(__file__.rsplit("/", 1)[0] + "/YON_SICILI.json", encoding="utf-8")) if "/" in __file__ else json.load(open("YON_SICILI.json", encoding="utf-8"))
YON = {x["ad"] for x in SICIL if x["yuva"] == "yon"}
ETKI = {"dahil-etmeme", "miktar", "sira"}
DERECE = {"iz-dogrulandi", "hipotez", "rivayet-yoklanmadi"}
AYRISIM = {"ve", "taksim"}
HAL_KAYNAGI = {"zahir", "farz"}
MIKTAR = {"icaz", "musavat", "itnab"}


def konum(ref):
    s, a = re.match(r"(\d+):(\d+)", ref).groups()
    return (int(s), int(a))


def kapsam_ayetleri(d):
    sonuc = set()
    for r in d.get("kapsam", []):
        s, a, b = re.fullmatch(r"(\d+):(\d+)-(\d+)", r).groups()
        for x in range(int(a), int(b) + 1):
            sonuc.add((int(s), x))
    return sonuc


def denetle(d):
    hata = []
    ihtiyac = {i["id"]: i for i in d["ihtiyaclar"]}
    karar = {k["id"]: k for k in d["kararlar"]}
    kisit = {x["id"]: x for x in d.get("kisitlar", [])}
    kapsam = kapsam_ayetleri(d)
    if len(ihtiyac) != len(d["ihtiyaclar"]):
        hata.append("tekrar eden ihtiyac kimligi")
    if len(karar) != len(d["kararlar"]):
        hata.append("tekrar eden karar kimligi")

    cocuklu = set()
    for i in ihtiyac.values():
        if i["tur"] not in TUR:
            hata.append(i["id"] + " tur")
        if i.get("tasiyici") not in TASIYICI:
            hata.append(i["id"] + " tasiyici")
        if i["tur"] in ZIHNI and i.get("tasiyici") != "muhatap":
            hata.append(i["id"] + " zihni ihtiyacin tasiyicisi muhatap olmak zorunda")
        if not i.get("ufuk") or not set(i["ufuk"]) <= UFUK:
            hata.append(i["id"] + " ufuk")
        if not set(i.get("kip", [])) <= KIP:
            hata.append(i["id"] + " kip")
        if i.get("ilim_cinsi") and (i["ilim_cinsi"] not in ILIM_CINSI or i["tur"] not in {"tasavvur", "tasdik"}):
            hata.append(i["id"] + " ilim_cinsi")
        if i.get("hal_kaynagi") and i["hal_kaynagi"] not in HAL_KAYNAGI:
            hata.append(i["id"] + " hal_kaynagi")
        if not i.get("kapanis_testi") or not i.get("icerik"):
            hata.append(i["id"] + " icerik veya kapanis_testi yok")
        for u in i["ust"]:
            if u not in ihtiyac:
                hata.append(i["id"] + " bulunmayan ust " + u)
            else:
                cocuklu.add(u)
        for o in i["onkosul"]:
            if o not in ihtiyac:
                hata.append(i["id"] + " bulunmayan onkosul " + o)
        if i.get("dogan_karar") and i["dogan_karar"] not in karar:
            hata.append(i["id"] + " bulunmayan dogan_karar")
    for u in cocuklu:
        if ihtiyac[u].get("ayrisim") not in AYRISIM:
            hata.append(u + " cocuklu ihtiyacin ayrisimi yok")

    def dongu(a, yol, kenar):
        if a in yol:
            return True
        return any(dongu(b, yol | {a}, kenar) for b in kenar(a) if b in ihtiyac)

    for a in ihtiyac:
        if dongu(a, frozenset(), lambda x: ihtiyac[x]["ust"]):
            hata.append(a + " ust dongusu")
        if dongu(a, frozenset(), lambda x: ihtiyac[x]["onkosul"]):
            hata.append(a + " onkosul dongusu")

    hizmet = {}
    for k in karar.values():
        for i in k["ihtiyac"]:
            if i not in ihtiyac:
                hata.append(k["id"] + " bulunmayan ihtiyac " + i)
            hizmet.setdefault(i, []).append(k["id"])
        if not k["karsilik"]:
            hata.append(k["id"] + " karsilik yok")
        if k["katiyet"] not in DERECE:
            hata.append(k["id"] + " katiyet")
        if k.get("miktar") and k["miktar"] not in MIKTAR:
            hata.append(k["id"] + " miktar")
        if k.get("miktar") in {"icaz", "itnab"} and not k.get("miktar_sebebi"):
            hata.append(k["id"] + " miktar_sebebi yok")
        if not k.get("neden_bu_kadar"):
            hata.append(k["id"] + " neden_bu_kadar yok")
        if not k["gerekce"]:
            hata.append(k["id"] + " gerekce yok")
        for g in k["gerekce"]:
            if g["yon"] not in YON or not g.get("cumle"):
                hata.append(k["id"] + " gerekce yon veya cumle")
            for a in g.get("atif", []):
                if a not in ihtiyac:
                    hata.append(k["id"] + " bulunmayan atif " + a)
        for s in k.get("kisit", []):
            if s not in kisit:
                hata.append(k["id"] + " bulunmayan kisit " + s)
    for x in kisit.values():
        if x["yon"] not in YON or x["etki"] not in ETKI or not x.get("cumle") or x.get("katiyet") not in DERECE:
            hata.append(x["id"] + " kisit alanlari")

    pozisyon = {k["id"]: min(konum(r) for r in k["karsilik"]) for k in karar.values()}

    def etkin_onkosul(x, gorulen=frozenset()):
        sonuc = set(ihtiyac[x]["onkosul"])
        for u in ihtiyac[x]["ust"]:
            if u in ihtiyac and u not in gorulen:
                sonuc |= etkin_onkosul(u, gorulen | {x})
        return sonuc

    def etkin_dogan(x, gorulen=frozenset()):
        sonuc = {ihtiyac[x]["dogan_karar"]} if ihtiyac[x].get("dogan_karar") else set()
        for u in ihtiyac[x]["ust"]:
            if u in ihtiyac and u not in gorulen:
                sonuc |= etkin_dogan(u, gorulen | {x})
        return sonuc

    onde = {k: set() for k in karar}
    for i in ihtiyac.values():
        for h in hizmet.get(i["id"], []):
            for o in etkin_onkosul(i["id"]):
                for s in hizmet.get(o, []):
                    if s != h:
                        onde[h].add(s)
            for dk in etkin_dogan(i["id"]):
                if dk != h:
                    onde[h].add(dk)
    for kid, gerekliler in onde.items():
        for g in gerekliler:
            if not pozisyon[g] < pozisyon[kid]:
                hata.append("sira: %s once gelmeli ama %s sonra" % (g, kid))

    cocuklar = {}
    for i in ihtiyac.values():
        for u in i["ust"]:
            cocuklar.setdefault(u, []).append(i["id"])

    def soy(x, gorulen=frozenset()):
        sonuc = {x}
        for c in cocuklar.get(x, []):
            if c not in gorulen:
                sonuc |= soy(c, gorulen | {x})
        return sonuc

    for k in karar.values():
        for g in k["gerekce"]:
            for a in g.get("atif", []):
                if a not in ihtiyac:
                    continue
                hizmet_edenler = set(hizmet.get(a, [])) or {s for y in soy(a) for s in hizmet.get(y, [])}
                for s in hizmet_edenler:
                    if s == k["id"]:
                        continue
                    if g["yon"] == "onceki" and not pozisyon[s] < pozisyon[k["id"]]:
                        hata.append("%s onceki gerekce: %s sonra geliyor" % (k["id"], s))
                    if g["yon"] == "sonraki" and not pozisyon[s] > pozisyon[k["id"]]:
                        hata.append("%s sonraki gerekce: %s once geliyor" % (k["id"], s))

    acik = [i for i in ihtiyac if i not in hizmet and i not in cocuklu and not ihtiyac[i].get("devir")]
    for a in acik:
        hata.append(a + " kapatilmamis yaprak ihtiyac")

    kapsanan = set()
    for k in karar.values():
        for r in k["karsilik"]:
            kapsanan.add(konum(r))
    kapsanmayan = sorted(a for a in kapsam if a not in kapsanan)
    for s, a in kapsanmayan:
        hata.append("sebepsiz ayet %d:%d" % (s, a))

    def kokler(x, yol=()):
        if x in yol or not ihtiyac[x]["ust"]:
            return [(x, len(yol))]
        sonuc = []
        for u in ihtiyac[x]["ust"]:
            if u in ihtiyac:
                sonuc += kokler(u, yol + (x,))
        return sonuc

    mesafe = {}
    for k in karar.values():
        mesafe[k["id"]] = max(m for i in k["ihtiyac"] if i in ihtiyac for _, m in kokler(i))
    dis_kok = [r for r in ihtiyac if not ihtiyac[r]["ust"] and ihtiyac[r]["tasiyici"] == "baskasi"]

    kimlikler = list(karar)
    n = len(kimlikler)
    idx = {k: i for i, k in enumerate(kimlikler)}
    on = [sum(1 << idx[x] for x in onde[k]) for k in kimlikler]
    sayim = [0] * (1 << n)
    sayim[0] = 1
    for m in range(1 << n):
        if not sayim[m]:
            continue
        for j in range(n):
            if not m >> j & 1 and on[j] & m == on[j]:
                sayim[m | 1 << j] += sayim[m]
    serbest = sayim[(1 << n) - 1]

    kisim_adaylari = []
    gaye = d.get("gaye_ihtiyaci")
    if gaye in ihtiyac:
        def ust_cocuk(x, yol=()):
            if x in yol:
                return None
            if gaye in ihtiyac[x]["ust"]:
                return x
            for u in ihtiyac[x]["ust"]:
                if u in ihtiyac:
                    r = ust_cocuk(u, yol + (x,))
                    if r:
                        return r
            return None

        sirali = sorted((k for k in karar.values() if all(konum(r) in kapsam for r in k["karsilik"])), key=lambda k: pozisyon[k["id"]])
        onceki_anahtar = None
        for k in sirali:
            anahtar = ust_cocuk(k["ihtiyac"][0])
            ayetler = sorted(konum(r)[1] for r in k["karsilik"])
            if anahtar == onceki_anahtar and kisim_adaylari:
                kisim_adaylari[-1][1] = ayetler[-1]
                kisim_adaylari[-1][2].append(k["id"])
            else:
                kisim_adaylari.append([ayetler[0], ayetler[-1], [k["id"]], anahtar])
            onceki_anahtar = anahtar

    rapor = {
        "ihtiyac": len(ihtiyac),
        "ihtiyac_tur": dict(Counter(i["tur"] for i in ihtiyac.values())),
        "ihtiyac_tasiyici": dict(Counter(i["tasiyici"] for i in ihtiyac.values())),
        "karar": len(karar),
        "gerekce_yon": dict(Counter(g["yon"] for k in karar.values() for g in k["gerekce"])),
        "katiyet": dict(Counter(k["katiyet"] for k in karar.values())),
        "kisit": len(kisit),
        "cok_ihtiyacli_karar": [k["id"] for k in karar.values() if len(k["ihtiyac"]) > 1],
        "cok_karsiliklı_karar": [k["id"] for k in karar.values() if len(k["karsilik"]) > 1],
        "taksim_ihtiyac": [i["id"] for i in ihtiyac.values() if i.get("ayrisim") == "taksim"],
        "devredilen": [i["id"] for i in ihtiyac.values() if i.get("devir")],
        "elenen_alternatif": sum(len(k.get("elenen", [])) for k in karar.values()),
        "kapsanmayan_ayet": len(kapsanmayan),
        "kapatilmamis_yaprak": len(acik),
        "kok_mesafesi_azami": max(mesafe.values()),
        "muhatap_disi_kok": dis_kok,
        "gecerli_sira_sayisi": serbest,
        "zorunlu_sira_cifti": sum(len(v) for v in onde.values()),
        "kisim_adaylari": ["%d-%d %s" % (a, b, "+".join(ks)) for a, b, ks, _ in kisim_adaylari],
    }
    return hata, rapor


def sinama(d):
    sonuc = []

    def k(c, kid):
        return next(x for x in c["kararlar"] if x["id"] == kid)

    def i(c, iid):
        return next(x for x in c["ihtiyaclar"] if x["id"] == iid)

    a = copy.deepcopy(d)
    degisti = False
    for kk in a["kararlar"]:
        for g in kk["gerekce"]:
            if g["yon"] == "sonraki" and g.get("atif") and not degisti:
                g["yon"] = "onceki"
                degisti = True
    sonuc.append(("sonra gelen ihtiyaca 'onceki' gerekcesi", denetle(a)[0]))
    b = copy.deepcopy(d)
    b["kararlar"][1]["gerekce"][0]["atif"] = ["I99"]
    sonuc.append(("bulunmayan ihtiyaca atif", denetle(b)[0]))
    c = copy.deepcopy(d)
    c["ihtiyaclar"][1]["tasiyici"] = "baskasi"
    c["ihtiyaclar"][1]["tur"] = "his"
    sonuc.append(("his ihtiyacini muhatap disina tasimak", denetle(c)[0]))
    e = copy.deepcopy(d)
    e["kararlar"][0]["gerekce"][0]["yon"] = "tahmin"
    sonuc.append(("tanimsiz gerekce yonu", denetle(e)[0]))
    g2 = copy.deepcopy(d)
    g2["kararlar"][0]["gerekce"][0]["yon"] = "muktezayi-hal"
    sonuc.append(("muktezayi-hali unsur (yon) diye yazmak", denetle(g2)[0]))
    f = copy.deepcopy(d)
    f["kararlar"] = [x for x in f["kararlar"] if x["id"] != "K07"]
    sonuc.append(("1:7'nin kararini silmek", denetle(f)[0]))
    m1 = copy.deepcopy(d)
    m1["kararlar"][0]["miktar"] = "uzun"
    sonuc.append(("tanimsiz miktar olcusu", denetle(m1)[0]))
    m2 = copy.deepcopy(d)
    m2["kararlar"][0]["miktar"] = "itnab"
    sonuc.append(("sebepsiz itnab", denetle(m2)[0]))
    m3 = copy.deepcopy(d)
    m3["ihtiyaclar"][1]["hal_kaynagi"] = "belki"
    sonuc.append(("tanimsiz hal kaynagi", denetle(m3)[0]))
    return sonuc


if __name__ == "__main__":
    yol = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "FATIHA_KARARLAR.json"
    d = json.load(open(yol, encoding="utf-8"))
    hata, rapor = denetle(d)
    for kk, v in rapor.items():
        print(kk, v)
    for h in hata:
        print("HATA", h)
    if "--sinama" in sys.argv:
        for ad, h in sinama(d):
            print("SINAMA", ad, "->", "REDDEDILDI (%d hata)" % len(h) if h else "KABUL EDILDI")
    sys.exit(1 if hata else 0)
