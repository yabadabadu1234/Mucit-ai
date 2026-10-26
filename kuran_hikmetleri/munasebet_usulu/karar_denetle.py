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
BAG = {"teyid", "tevlid", "tarif", "karisik"}
BAG_TUR = {"teyid": "tasdik", "tevlid": "irade", "tarif": "tasavvur"}
SUAL_TURU = {"ne", "nasil", "neden", "hakkinda_ne", "paralel", "nereden", "kim"}
KIFAYE = {"tam", "kismi"}
HASR = {"akli", "nakli"}
CEVAP = {"dogrudan", "odaksiz", "cevaplamaz"}
ISARET = {"edat", "iltifat", "emir", "isaret_zamiri", "yok"}


def sadelestir(m):
    import unicodedata

    m = m.replace("\u0671", "\u0627").replace("\u0640", "")
    return "".join(c for c in unicodedata.normalize("NFD", m) if unicodedata.category(c) != "Mn")


def blok_tablosu():
    d = json.load(open(__file__.rsplit("/", 1)[0] + "/../nazm_blok.json", encoding="utf-8"))
    return {(v["s"], v["a"]): v["b"] for v in d.values()}


def blok_ref(r):
    a, b = r.split("#")
    s, ay = a.split(":")
    return (int(s), int(ay)), int(b)


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
    gaye = {i["id"]: i for i in d["gayeler"]}
    karar = {k["id"]: k for k in d["kararlar"]}
    kisit = {x["id"]: x for x in d.get("kisitlar", [])}
    kapsam = kapsam_ayetleri(d)
    if len(gaye) != len(d["gayeler"]):
        hata.append("tekrar eden gaye kimligi")
    if len(karar) != len(d["kararlar"]):
        hata.append("tekrar eden karar kimligi")

    cocuklu = set()
    for i in gaye.values():
        if i["tur"] not in TUR:
            hata.append(i["id"] + " tur")
        if i.get("tasiyici") not in TASIYICI:
            hata.append(i["id"] + " tasiyici")
        if i["tur"] in ZIHNI and i.get("tasiyici") != "muhatap":
            hata.append(i["id"] + " zihni gayein tasiyicisi muhatap olmak zorunda")
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
            if u not in gaye:
                hata.append(i["id"] + " bulunmayan ust " + u)
            else:
                cocuklu.add(u)
        for o in i["onkosul"]:
            if o not in gaye:
                hata.append(i["id"] + " bulunmayan onkosul " + o)
        if i.get("dogan_karar") and i["dogan_karar"] not in karar:
            hata.append(i["id"] + " bulunmayan dogan_karar")
    for u in cocuklu:
        if gaye[u].get("ayrisim") not in AYRISIM:
            hata.append(u + " cocuklu gayein ayrisimi yok")

    def dongu(a, yol, kenar):
        if a in yol:
            return True
        return any(dongu(b, yol | {a}, kenar) for b in kenar(a) if b in gaye)

    for a in gaye:
        if dongu(a, frozenset(), lambda x: gaye[x]["ust"]):
            hata.append(a + " ust dongusu")
        if dongu(a, frozenset(), lambda x: gaye[x]["onkosul"]):
            hata.append(a + " onkosul dongusu")

    hizmet = {}
    for k in karar.values():
        for i in k["gaye"]:
            if i not in gaye:
                hata.append(k["id"] + " bulunmayan gaye " + i)
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
                if a not in gaye:
                    hata.append(k["id"] + " bulunmayan atif " + a)
        for s in k.get("kisit", []):
            if s not in kisit:
                hata.append(k["id"] + " bulunmayan kisit " + s)
    for x in kisit.values():
        if x["yon"] not in YON or x["etki"] not in ETKI or not x.get("cumle") or x.get("katiyet") not in DERECE:
            hata.append(x["id"] + " kisit alanlari")

    pozisyon = {k["id"]: min(konum(r) for r in k["karsilik"]) for k in karar.values()}

    def etkin_onkosul(x, gorulen=frozenset()):
        sonuc = set(gaye[x]["onkosul"])
        for u in gaye[x]["ust"]:
            if u in gaye and u not in gorulen:
                sonuc |= etkin_onkosul(u, gorulen | {x})
        return sonuc

    def etkin_dogan(x, gorulen=frozenset()):
        sonuc = {gaye[x]["dogan_karar"]} if gaye[x].get("dogan_karar") else set()
        for u in gaye[x]["ust"]:
            if u in gaye and u not in gorulen:
                sonuc |= etkin_dogan(u, gorulen | {x})
        return sonuc

    onde = {k: set() for k in karar}
    for i in gaye.values():
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

    def atalar(x, yol=frozenset()):
        s = {x}
        for u in gaye[x]["ust"]:
            if u in gaye and u not in yol:
                s |= atalar(u, yol | {x})
        return s

    def en_yakin_gorulen(x, gorulen, yol=frozenset()):
        if x in gorulen:
            return {x}
        s = set()
        for u in gaye[x]["ust"]:
            if u in gaye and u not in yol:
                s |= en_yakin_gorulen(u, gorulen, yol | {x})
        return s

    sag_sinir_ihlali = []
    gorulen = set()
    cephe = set()
    for k in sorted(karar.values(), key=lambda x: pozisyon[x["id"]]):
        for i in k["gaye"]:
            if i not in gaye:
                continue
            for a in en_yakin_gorulen(i, gorulen):
                if a not in cephe:
                    sag_sinir_ihlali.append("%s:%s->%s" % (k["id"], i, a))
        yeni = set()
        for i in k["gaye"]:
            if i in gaye:
                yeni |= atalar(i)
        gorulen |= yeni
        cephe = yeni

    cocuklar = {}
    for i in gaye.values():
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
                if a not in gaye:
                    continue
                hizmet_edenler = set(hizmet.get(a, [])) or {s for y in soy(a) for s in hizmet.get(y, [])}
                for s in hizmet_edenler:
                    if s == k["id"]:
                        continue
                    if g["yon"] == "onceki" and not pozisyon[s] < pozisyon[k["id"]]:
                        hata.append("%s onceki gerekce: %s sonra geliyor" % (k["id"], s))
                    if g["yon"] == "sonraki" and not pozisyon[s] > pozisyon[k["id"]]:
                        hata.append("%s sonraki gerekce: %s once geliyor" % (k["id"], s))

    acik = [i for i in gaye if i not in hizmet and i not in cocuklu and not gaye[i].get("devir")]
    for a in acik:
        hata.append(a + " kapatilmamis yaprak gaye")

    kapsanan = set()
    for k in karar.values():
        for r in k["karsilik"]:
            kapsanan.add(konum(r))
    kapsanmayan = sorted(a for a in kapsam if a not in kapsanan)
    for s, a in kapsanmayan:
        hata.append("sebepsiz ayet %d:%d" % (s, a))

    def kokler(x, yol=()):
        if x in yol or not gaye[x]["ust"]:
            return [(x, len(yol))]
        sonuc = []
        for u in gaye[x]["ust"]:
            if u in gaye:
                sonuc += kokler(u, yol + (x,))
        return sonuc

    mesafe = {}
    for k in karar.values():
        mesafe[k["id"]] = max(m for i in k["gaye"] if i in gaye for _, m in kokler(i))
    dis_kok = [r for r in gaye if not gaye[r]["ust"] and gaye[r]["tasiyici"] == "baskasi"]

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
    kok = d.get("kok_gaye")
    if kok in gaye:
        def ust_cocuk(x, yol=()):
            if x in yol:
                return None
            if kok in gaye[x]["ust"]:
                return x
            for u in gaye[x]["ust"]:
                if u in gaye:
                    r = ust_cocuk(u, yol + (x,))
                    if r:
                        return r
            return None

        sirali = sorted((k for k in karar.values() if all(konum(r) in kapsam for r in k["karsilik"])), key=lambda k: pozisyon[k["id"]])
        onceki_anahtar = None
        for k in sirali:
            anahtar = ust_cocuk(k["gaye"][0])
            ayetler = sorted(konum(r)[1] for r in k["karsilik"])
            if anahtar == onceki_anahtar and kisim_adaylari:
                kisim_adaylari[-1][1] = ayetler[-1]
                kisim_adaylari[-1][2].append(k["id"])
            else:
                kisim_adaylari.append([ayetler[0], ayetler[-1], [k["id"]], anahtar])
            onceki_anahtar = anahtar

    def hakimler(x, yol=frozenset()):
        sonuc = set()
        for u in gaye[x]["ust"]:
            if u in gaye and u not in yol:
                sonuc |= {u} | hakimler(u, yol | {x})
        return sonuc

    ilk = sorted(karar.values(), key=lambda x: pozisyon[x["id"]])[0]["gaye"][0]
    taban = kok if kok in gaye else next((r for r, _ in kokler(ilk)), None)
    yigin = [taban] if taban in gaye else []
    islem = Counter()
    azami_derinlik = len(yigin)
    for k in sorted(karar.values(), key=lambda x: pozisyon[x["id"]]):
        g = k["gaye"][0]
        if g not in gaye:
            continue
        ata = hakimler(g)
        sira = [j for j, t in enumerate(yigin) if t == g or t in ata]
        if not sira:
            erken = [y for y in yigin if g in etkin_onkosul(y)]
            islem["geri_donus_kesintisi" if erken else "kesinti"] += 1
            yigin.append(g)
        else:
            j = sira[-1]
            kaldirilan = len(yigin) - 1 - j
            if yigin[j] == g:
                islem["ayni" if kaldirilan == 0 else "donus"] += 1
                islem["pop"] += kaldirilan
                del yigin[j + 1:]
            else:
                islem["pop"] += kaldirilan
                del yigin[j + 1:]
                yigin.append(g)
                islem["push"] += 1
        azami_derinlik = max(azami_derinlik, len(yigin))

    karisik_ust = sorted(
        c["id"] for c in gaye.values() for u in c["ust"] if u in gaye and gaye[u]["tur"] in {"tasdik", "irade"} and c["tur"] != gaye[u]["tur"]
    )

    s2 = Counter()
    if d.get("sema") == 2:
        bt = blok_tablosu()

        def ayet_of(r):
            a_, b_ = re.match(r"(\d+):(\d+)", r).groups()
            return (int(a_), int(b_))

        def blok_gecerli(ref):
            try:
                ay, n = blok_ref(ref)
            except ValueError:
                return None
            return (ay, n) if ay in bt and 0 <= n < len(bt[ay]) else None

        tum_blok = {}
        for k in karar.values():
            sonuc = set()
            for r in k["karsilik"]:
                ay = ayet_of(r)
                if ay not in bt:
                    hata.append(k["id"] + " blok tablosunda yok " + r)
                    continue
                sonuc |= {(ay, n) for n in range(len(bt[ay]))}
            tum_blok[k["id"]] = sonuc

        dogrudan_poz = {}
        for k in karar.values():
            for gi, refs in k.get("odak", {}).items():
                for r in refs:
                    b = blok_gecerli(r)
                    if b:
                        dogrudan_poz.setdefault(gi, []).append(b)

        def ilk_cevap(x, gorulen=frozenset()):
            adaylar = list(dogrudan_poz.get(x, []))
            for c in cocuklar.get(x, []):
                if c not in gorulen:
                    r = ilk_cevap(c, gorulen | {x})
                    if r:
                        adaylar.append(r)
            return min(adaylar) if adaylar else None

        for g in gaye.values():
            gi = g["id"]
            if not g.get("mevzu") or not g.get("sual"):
                hata.append(gi + " mevzu veya sual yok")
            for u in g["ust"]:
                b = g.get("ust_bag", {}).get(u)
                if not b:
                    hata.append(gi + " ust_bag eksik " + u)
                    continue
                if b.get("bag") not in BAG or b.get("sual_turu") not in SUAL_TURU:
                    hata.append(gi + " ust_bag alanlari " + u)
                    continue
                tg, tu = g["tur"], gaye[u]["tur"]
                if b["bag"] == "karisik":
                    if tg == tu:
                        hata.append(gi + " ayni turde karisik bag " + u)
                    if not b.get("gerekce"):
                        hata.append(gi + " karisik bag gerekcesiz " + u)
                elif not (tg == tu == BAG_TUR[b["bag"]]):
                    hata.append(gi + " bag turu ile gaye turleri uyusmuyor " + u)
                s2["bag_" + b["bag"]] += 1
            if gi in cocuklu:
                kf = g.get("kifaye")
                if not kf or kf.get("yeter") not in KIFAYE or kf.get("katiyet") not in DERECE:
                    hata.append(gi + " kifaye eksik")
                else:
                    s2["kifaye_" + kf["yeter"]] += 1
                    if kf["yeter"] == "kismi" and not kf.get("varsayilan_malumat"):
                        hata.append(gi + " kismi kifayede varsayilan malumat yok")
                sira = g.get("alt_sira", [])
                if sorted(sira) != sorted(cocuklar.get(gi, [])):
                    hata.append(gi + " alt_sira cocuklarin dizilisi degil")
                else:
                    for c in sira:
                        for o in gaye[c]["onkosul"]:
                            if o in sira and sira.index(o) > sira.index(c):
                                hata.append(gi + " alt_sira onkosulu bozuyor " + o + " " + c)
            if g.get("ayrisim") == "taksim":
                sk = g.get("sikler", [])
                if sorted(x["gaye"] for x in sk) != sorted(cocuklar.get(gi, [])):
                    hata.append(gi + " siklar cocuklara esit degil")
                hs = g.get("hasr", {})
                if hs.get("usul") not in HASR or not hs.get("gerekce"):
                    hata.append(gi + " hasr eksik")
                else:
                    s2["hasr_" + hs["usul"]] += 1
            for o in g.get("oncul", []):
                if o["gaye"] not in gaye or o["gaye"] not in etkin_onkosul(gi):
                    hata.append(gi + " oncul onkosul degil " + o["gaye"])
                s2["oncul"] += 1
            c = g.get("capa")
            if not c:
                hata.append(gi + " capa yok")
            elif c.get("ayet") != "kok":
                cb = blok_gecerli("%s#%s" % (c.get("ayet", ""), c.get("blok", "x")))
                ic = ilk_cevap(gi)
                if not cb:
                    hata.append(gi + " capa blogu gecersiz")
                elif ic and not cb < ic:
                    hata.append(gi + " capa cevaptan sonra")
                s2["capa_blok"] += 1
            else:
                s2["capa_kok"] += 1

        for k in karar.values():
            ki = k["id"]
            tum = tum_blok[ki]
            odak = k.get("odak")
            if not odak or set(odak) != set(k["gaye"]):
                hata.append(ki + " odak her gaye icin yok")
                continue
            kapsanan = set()
            for gi, refs in odak.items():
                if not refs:
                    hata.append(ki + " odak bos " + gi)
                for r in refs:
                    b = blok_gecerli(r)
                    if not b or b not in tum:
                        hata.append(ki + " odak blogu karsilikta degil " + r)
                    else:
                        kapsanan.add(b)
            for f in k.get("fon", []):
                b = blok_gecerli(f["blok"])
                if not b or b not in tum:
                    hata.append(ki + " fon blogu karsilikta degil")
                    continue
                if f["blok"] in odak.get(f["gaye"], []):
                    hata.append(ki + " fon ile odak ayni blok " + f["blok"])
                kapsanan.add(b)
                s2["fon"] += 1
            for m in k.get("mesele_disi", []):
                b = blok_gecerli(m["blok"])
                if not b or b not in tum:
                    hata.append(ki + " mesele disi blogu karsilikta degil")
                    continue
                kapsanan.add(b)
                s2["mesele_disi"] += 1
                if m.get("alt_gaye"):
                    ag = m["alt_gaye"]
                    hizmet_eden = [x for x in karar.values() if ag in x["gaye"]]
                    bagli = any(
                        any(t["kaynak"] == m["blok"] for t in x.get("tekrar", [])) or any(ayet_of(r) == b[0] for r in x["karsilik"])
                        for x in hizmet_eden
                    )
                    if ag not in gaye or not bagli:
                        hata.append(ki + " mesele disi alt gayeye baglanmiyor " + m["blok"])
                elif not m.get("devir"):
                    hata.append(ki + " mesele disi ne alt gayeye ne devire bagli " + m["blok"])
            if kapsanan != tum:
                hata.append(ki + " bloklar kapsanmadi %d/%d" % (len(kapsanan & tum), len(tum)))
            for t in k.get("tekrar", []):
                b1, b0 = blok_gecerli(t["blok"]), blok_gecerli(t["kaynak"])
                if not b1 or not b0 or not b0 < b1:
                    hata.append(ki + " tekrar konumu gecersiz")
                elif sadelestir(bt[b1[0]][b1[1]][0]) != sadelestir(bt[b0[0]][b0[1]][0]):
                    hata.append(ki + " tekrar metinleri ayni degil " + t["blok"])
                s2["tekrar"] += 1
            for pr in k.get("paralel", []):
                ust_kumeleri = {tuple(sorted(gaye[x]["ust"])) for x in pr["gayeler"] if x in gaye}
                if len(pr["gayeler"]) < 2 or len(ust_kumeleri) != 1 or any(x not in k["gaye"] for x in pr["gayeler"]):
                    hata.append(ki + " paralel gayeler kardes degil")
                s2["paralel"] += 1
            if k.get("isaret", {}).get("tur") not in ISARET:
                hata.append(ki + " isaret turu")
            else:
                s2["isaret_" + k["isaret"]["tur"]] += 1
            dr = k.get("daraltma")
            if dr:
                if not blok_gecerli(dr["blok"]) or blok_gecerli(dr["blok"]) not in tum or not dr.get("elenen_ihtimaller"):
                    hata.append(ki + " daraltma eksik")
                s2["daraltma"] += 1
            cu = k.get("cevap_uygunlugu", {})
            if set(cu) != set(k["gaye"]) or not set(cu.values()) <= CEVAP:
                hata.append(ki + " cevap uygunlugu eksik")
            else:
                for v in cu.values():
                    s2["cevap_" + v] += 1
                    if v == "cevaplamaz":
                        hata.append(ki + " cevaplamayan karar")

    rapor = {
        "gaye": len(gaye),
        "gaye_tur": dict(Counter(i["tur"] for i in gaye.values())),
        "gaye_tasiyici": dict(Counter(i["tasiyici"] for i in gaye.values())),
        "karar": len(karar),
        "gerekce_yon": dict(Counter(g["yon"] for k in karar.values() for g in k["gerekce"])),
        "katiyet": dict(Counter(k["katiyet"] for k in karar.values())),
        "kisit": len(kisit),
        "cok_gayeli_karar": [k["id"] for k in karar.values() if len(k["gaye"]) > 1],
        "cok_karsiliklı_karar": [k["id"] for k in karar.values() if len(k["karsilik"]) > 1],
        "taksim_gaye": [i["id"] for i in gaye.values() if i.get("ayrisim") == "taksim"],
        "devredilen": [i["id"] for i in gaye.values() if i.get("devir")],
        "elenen_alternatif": sum(len(k.get("elenen", [])) for k in karar.values()),
        "kapsanmayan_ayet": len(kapsanmayan),
        "kapatilmamis_yaprak": len(acik),
        "kok_mesafesi_azami": max(mesafe.values()),
        "muhatap_disi_kok": dis_kok,
        "gecerli_sira_sayisi": serbest,
        "zorunlu_sira_cifti": sum(len(v) for v in onde.values()),
        "sag_sinir_ihlali": sag_sinir_ihlali,
        "sema": d.get("sema", 1),
        "sema2": dict(s2),
        "yigin_islemleri": dict(islem),
        "yigin_azami_derinlik": azami_derinlik,
        "karisik_ust_kenar": karisik_ust,
        "kisim_adaylari": ["%d-%d %s" % (a, b, "+".join(ks)) for a, b, ks, _ in kisim_adaylari],
    }
    return hata, rapor


def sinama(d):
    sonuc = []

    def k(c, kid):
        return next(x for x in c["kararlar"] if x["id"] == kid)

    def i(c, iid):
        return next(x for x in c["gayeler"] if x["id"] == iid)

    a = copy.deepcopy(d)
    degisti = False
    for kk in a["kararlar"]:
        for g in kk["gerekce"]:
            if g["yon"] == "sonraki" and g.get("atif") and not degisti:
                g["yon"] = "onceki"
                degisti = True
    sonuc.append(("sonra gelen gayea 'onceki' gerekcesi", denetle(a)[0]))
    b = copy.deepcopy(d)
    b["kararlar"][1]["gerekce"][0]["atif"] = ["I99"]
    sonuc.append(("bulunmayan gayea atif", denetle(b)[0]))
    c = copy.deepcopy(d)
    c["gayeler"][1]["tasiyici"] = "baskasi"
    c["gayeler"][1]["tur"] = "his"
    sonuc.append(("his gayeini muhatap disina tasimak", denetle(c)[0]))
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
    r0 = len(denetle(d)[1]["sag_sinir_ihlali"])
    s1 = copy.deepcopy(d)
    for x in s1["gayeler"]:
        if x["id"] == "I6":
            x["ust"] = ["I1d"]
    r1 = len(denetle(s1)[1]["sag_sinir_ihlali"])
    sonuc.append(("kapanmis alt agaca donus (sag sinir) ihlali artti %d -> %d" % (r0, r1), ["sag sinir"] if r1 > r0 else []))
    m3 = copy.deepcopy(d)
    m3["gayeler"][1]["hal_kaynagi"] = "belki"
    sonuc.append(("tanimsiz hal kaynagi", denetle(m3)[0]))
    y1 = copy.deepcopy(d)
    for x in y1["gayeler"]:
        if x["id"] == "I6":
            x["ust"] = []
    k0 = denetle(d)[1]["yigin_islemleri"].get("kesinti", 0)
    k1 = denetle(y1)[1]["yigin_islemleri"].get("kesinti", 0)
    sonuc.append(("hicbir hakimi olmayan seyir (yigin kesintisi) %d -> %d" % (k0, k1), ["yigin kesintisi"] if k1 > k0 else []))
    if d.get("sema") == 2:
        def g_(c, x):
            return next(y for y in c["gayeler"] if y["id"] == x)

        def k_(c, x):
            return next(y for y in c["kararlar"] if y["id"] == x)

        def dene(ad, degistir):
            c = copy.deepcopy(d)
            degistir(c)
            sonuc.append((ad, denetle(c)[0]))

        dene("ust_bag silindi", lambda c: g_(c, "I1a")["ust_bag"].clear())
        dene("tur ile bag uyusmuyor (his altina tarif)", lambda c: g_(c, "H1")["ust_bag"]["I0"].update(bag="tarif"))
        dene("karisik bag gerekcesiz", lambda c: g_(c, "I2")["ust_bag"]["I0"].pop("gerekce"))
        dene("kifaye silindi", lambda c: g_(c, "I1").pop("kifaye"))
        dene("kismi kifayede malumat yok", lambda c: g_(c, "I0")["kifaye"].update(varsayilan_malumat=[]))
        dene("alt_sira onkosulu bozuyor", lambda c: g_(c, "I1").update(alt_sira=["I1a", "I1d", "I1b", "I1c"]))
        dene("taksimde hasr yok", lambda c: g_(c, "I4").pop("hasr"))
        dene("sikler cocuklara esit degil", lambda c: g_(c, "I4").update(sikler=g_(c, "I4")["sikler"][:2]))
        dene("oncul onkosul degil", lambda c: g_(c, "I4").update(onkosul=[]))
        dene("capa cevaptan sonra", lambda c: g_(c, "I1a").update(capa={"ayet": "1:3", "blok": 0}))
        dene("odak bos", lambda c: k_(c, "K06")["odak"].update(I5=[]))
        dene("blok kapsanmadi", lambda c: k_(c, "K07")["odak"].update(I4c=[]))
        dene("tekrar metinleri ayni degil", lambda c: k_(c, "K03")["tekrar"][0].update(kaynak="1:2#0"))
        dene("mesele disi alt gayeye baglanmiyor", lambda c: k_(c, "K01")["mesele_disi"][0].update(alt_gaye="I1c"))
        dene("paralel gayeler kardes degil", lambda c: k_(c, "K07")["paralel"][0].update(gayeler=["I4b", "I3b"]))
        dene("cevaplamayan karar", lambda c: k_(c, "K06")["cevap_uygunlugu"].update(I5="cevaplamaz"))
        dene("fon ile odak ayni blok", lambda c: k_(c, "K08").update(fon=[{"blok": "2:2#0", "gaye": "I6"}]))
        dene("isaret turu tanimsiz", lambda c: k_(c, "K05")["isaret"].update(tur="belki"))
    return sonuc


def agac_yaz(d):
    bt = blok_tablosu()
    gaye = {g["id"]: g for g in d["gayeler"]}
    cocuk = {}
    for g in d["gayeler"]:
        for u in g["ust"]:
            cocuk.setdefault(u, []).append(g["id"])
    satirlar = []

    def cevap(k, gi, derinlik):
        odak = set(k["odak"][gi])
        md = {m["blok"] for m in k.get("mesele_disi", [])}
        fon = {f["blok"] for f in k.get("fon", [])}
        parcalar = []
        for ay in dict.fromkeys((int(r.split(":")[0]), int("".join(c for c in r.split(":")[1] if c.isdigit()))) for r in k["karsilik"]):
            for n, blk in enumerate(bt[ay]):
                ref = "%d:%d#%d" % (ay[0], ay[1], n)
                if ref in odak:
                    parcalar.append("[" + blk[1] + "]F")
                elif ref in md:
                    parcalar.append("(" + blk[1] + ")MD")
                elif ref in fon:
                    parcalar.append("{" + blk[1] + "}BG")
        satirlar.append("> " * derinlik + "A %s %s: %s" % (k["id"], ",".join(k["karsilik"]), " ".join(parcalar)))

    def yaz(gi, derinlik, gorulen):
        g = gaye[gi]
        satirlar.append("> " * derinlik + "Q %s {%s}" % (gi, g["sual"]))
        for k in d["kararlar"]:
            if gi in k["gaye"] and gi in k.get("odak", {}):
                cevap(k, gi, derinlik + 1)
        for c in g.get("alt_sira", cocuk.get(gi, [])):
            if c not in gorulen:
                yaz(c, derinlik + 1, gorulen | {gi})

    for k in d["gayeler"]:
        if not k["ust"]:
            yaz(k["id"], 0, frozenset())
    return "\n".join(satirlar)


if __name__ == "__main__":
    yol = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "FATIHA_KARARLAR.json"
    d = json.load(open(yol, encoding="utf-8"))
    hata, rapor = denetle(d)
    for kk, v in rapor.items():
        print(kk, v)
    for h in hata:
        print("HATA", h)
    if "--sinama" in sys.argv and any(g["id"] == "I1a" for g in d["gayeler"]):
        for ad, h in sinama(d):
            print("SINAMA", ad, "->", "REDDEDILDI (%d hata)" % len(h) if h else "KABUL EDILDI")
    if "--agac" in sys.argv:
        print(agac_yaz(d))
    sys.exit(1 if hata else 0)
