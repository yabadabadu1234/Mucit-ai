import copy
import json
import re
import sys
from collections import Counter

TUR = {"tasavvur", "tasdik", "irade"}
YON = {"onceki", "sonraki", "butun", "mutekellim", "muhatap", "konu"}
DERECE = {"iz-dogrulandi", "hipotez", "rivayet-yoklanmadi"}
AYRISIM = {"ve", "taksim"}


def konum(ref):
    s, a = re.match(r"(\d+):(\d+)", ref).groups()
    return (int(s), int(a))


def denetle(d, kapsam_sure=1, kapsam_ayet=7):
    hata = []
    ihtiyac = {i["id"]: i for i in d["ihtiyaclar"]}
    karar = {k["id"]: k for k in d["kararlar"]}
    if len(ihtiyac) != len(d["ihtiyaclar"]):
        hata.append("tekrar eden ihtiyac kimligi")
    if len(karar) != len(d["kararlar"]):
        hata.append("tekrar eden karar kimligi")

    cocuklu = set()
    for i in ihtiyac.values():
        if i["tur"] not in TUR:
            hata.append(i["id"] + " tur")
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
        if i["id"] in cocuklu or any(x["ust"] and i["id"] in x["ust"] for x in ihtiyac.values()):
            if i.get("ayrisim") not in AYRISIM:
                hata.append(i["id"] + " cocuklu ihtiyacin ayrisimi yok")

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

    pozisyon = {k["id"]: min(konum(r) for r in k["karsilik"]) for k in karar.values()}

    def etkin_onkosul(x, gorulen=frozenset()):
        sonuc = set(ihtiyac[x]["onkosul"])
        for u in ihtiyac[x]["ust"]:
            if u in ihtiyac and u not in gorulen:
                sonuc |= etkin_onkosul(u, gorulen | {x})
        return sonuc

    onde = {k: set() for k in karar}
    for i in ihtiyac.values():
        hedef = hizmet.get(i["id"], [])
        for h in hedef:
            for o in etkin_onkosul(i["id"]):
                for s in hizmet.get(o, []):
                    if s != h:
                        onde[h].add(s)
            if i.get("dogan_karar") and i["dogan_karar"] != h:
                onde[h].add(i["dogan_karar"])
    for kid, gerekliler in onde.items():
        for g in gerekliler:
            if not pozisyon[g] < pozisyon[kid]:
                hata.append("sira: %s once gelmeli ama %s sonra" % (g, kid))

    for k in karar.values():
        for g in k["gerekce"]:
            for a in g.get("atif", []):
                if a not in ihtiyac:
                    continue
                for s in hizmet.get(a, []):
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
            s, a = konum(r)
            if s == kapsam_sure:
                kapsanan.add(a)
    kapsanmayan = [a for a in range(1, kapsam_ayet + 1) if a not in kapsanan]
    for a in kapsanmayan:
        hata.append("sebepsiz ayet %d:%d" % (kapsam_sure, a))

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

    rapor = {
        "ihtiyac": len(ihtiyac),
        "ihtiyac_tur": dict(Counter(i["tur"] for i in ihtiyac.values())),
        "karar": len(karar),
        "gerekce_yon": dict(Counter(g["yon"] for k in karar.values() for g in k["gerekce"])),
        "katiyet": dict(Counter(k["katiyet"] for k in karar.values())),
        "cok_ihtiyacli_karar": [k["id"] for k in karar.values() if len(k["ihtiyac"]) > 1],
        "cok_karsiliklı_karar": [k["id"] for k in karar.values() if len(k["karsilik"]) > 1],
        "taksim_ihtiyac": [i["id"] for i in ihtiyac.values() if i.get("ayrisim") == "taksim"],
        "devredilen": [i["id"] for i in ihtiyac.values() if i.get("devir")],
        "elenen_alternatif": sum(len(k.get("elenen", [])) for k in karar.values()),
        "kapsanmayan_ayet": len(kapsanmayan),
        "kapatilmamis_yaprak": len(acik),
        "gecerli_sira_sayisi": serbest,
        "zorunlu_sira_cifti": sum(len(v) for v in onde.values()),
    }
    return hata, rapor


def sinama(d):
    sonuc = []
    a = copy.deepcopy(d)
    a["kararlar"][2]["gerekce"][1]["yon"] = "onceki"
    a["kararlar"][2]["gerekce"][1]["atif"] = ["I5"]
    sonuc.append(("sonra gelen ihtiyaca 'onceki' gerekcesi", denetle(a)[0]))
    b = copy.deepcopy(d)
    b["kararlar"][1]["gerekce"][0]["atif"] = ["I99"]
    sonuc.append(("bulunmayan ihtiyaca atif", denetle(b)[0]))
    c = copy.deepcopy(d)
    c["kararlar"][5]["karsilik"] = ["1:4"]
    sonuc.append(("talebi sifatlardan once yerlestirmek", denetle(c)[0]))
    e = copy.deepcopy(d)
    e["kararlar"] = [k for k in e["kararlar"] if k["id"] != "K07"]
    sonuc.append(("1:7'yi karsiliksiz birakmak", denetle(e)[0]))
    return sonuc


if __name__ == "__main__":
    d = json.load(open("FATIHA_KARARLAR.json", encoding="utf-8"))
    hata, rapor = denetle(d)
    for k, v in rapor.items():
        print(k, v)
    for h in hata:
        print("HATA", h)
    if "--sinama" in sys.argv:
        for ad, h in sinama(d):
            print("SINAMA", ad, "->", "REDDEDILDI (%d hata)" % len(h) if h else "KABUL EDILDI")
    sys.exit(1 if hata else 0)
