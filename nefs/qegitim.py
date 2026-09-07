from __future__ import annotations

import time
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from .musahede import gorev_dizisi, gorevleri_getir
from ogrenme.optimize import as_gek_adimi, ayrik_mertebede_sicra

from . import melekeler as mertebe
from .melekeler import QNefs
from .zihin_durumu import QAyar, QYazmac

__all__ = ["kaide_halkasi", "kaide_kefesi", "ornekler", "ornek_bol", "belirtecleri_kodla",
           "adayin_tuttugu",
           "egit", "degerlendir"]


def ornek_bol(o) -> Tuple[List[int], int, str]:
    if len(o) >= 3:
        return list(o[0]), int(o[1]), str(o[2])
    return list(o[0]), int(o[1]), "sözlü"


def belirtecleri_kodla(belirtecler: Sequence[int], kubit: int = 4,
                       sozluk: int = 16, usul: str = "kategorik"
                       ) -> np.ndarray:
    if usul in ("sürekli", "lie"):
        from .lif import kodla, KIP_TUTARLI, KIP_LIE
        ne = KIP_TUTARLI if usul == "sürekli" else KIP_LIE
        X = np.atleast_2d(np.asarray(belirtecler, float))
        cikti = [np.asarray(kodla(x, ne=ne, boyut=int(sozluk))).reshape(-1)
                 for x in X]
        g = max(c.size for c in cikti)
        return np.stack([np.pad(np.real(c), (0, g - c.size)) for c in cikti])
    if usul != "kategorik":
        raise ValueError("kodlama usulü bilinmiyor: %r" % (usul,))

    taban = int(kubit) if int(kubit) >= 2 else int(sozluk)
    t = np.asarray(belirtecler, int).reshape(-1) % taban
    out = np.zeros((t.size, taban))
    out[np.arange(t.size), t] = 1.0
    return out


def kaide_halkasi(gorev, taban: int = 16, basamak: int = 0
                  ) -> Dict[str, Any]:
    from .belirtec import basamak_sayisi, tip_vektoru
    from .kulli_mizan import givens
    from .mukayese import bargmann, istisna_yeri, nesnelestir
    from .musahede import izgara_belirtecle

    ciftler = list(getattr(gorev, "egitim", ()) or ())
    if len(ciftler) < 2:
        return {"K": len(ciftler), "r": 0.0, "Φ": 0.0,
                "küllî": False, "istisna": None,
                "sebep": "numune çifti ikiden az -- halka kurulamaz"}
    tb = max(2, int(taban))
    bs = int(basamak) if int(basamak) > 0 else basamak_sayisi(256, tb)
    hipotez: List[np.ndarray] = []
    for gi, co in ciftler:
        a = tip_vektoru(izgara_belirtecle(gi), tb, bs)
        b = tip_vektoru(izgara_belirtecle(co), tb, bs)
        n = int(max(2, min(tb, max(a.size, b.size))))
        va = np.zeros(n, complex)
        vb = np.zeros(n, complex)
        for i, x in enumerate(a[:n]):
            va[i] = float(x) + 1.0
        for i, x in enumerate(b[:n]):
            vb[i] = float(x) + 1.0
        na = float(np.linalg.norm(va)) or 1.0
        nb = float(np.linalg.norm(vb)) or 1.0
        U = givens(va / na, vb / nb)
        o = bargmann([va / na, U @ (va / na), vb / nb])
        hipotez.append(nesnelestir(o, n))
    h = bargmann(hipotez)
    ist = (istisna_yeri(hipotez) if len(hipotez) >= 3
           else {"istisna": None, "yırtık": False, "sapma": 0.0})
    return {"K": len(hipotez), "r": float(h["r"]), "Φ": float(h["Φ"]),
            "küllî": bool(h["r"] > 0.0 and not h["kopuk"]
                          and not h["tenakuz"]),
            "kopuk": bool(h["kopuk"]),
            "istisna": ist.get("istisna"),
            "yırtık": bool(ist.get("yırtık", False)),
            "sapma": float(ist.get("sapma", 0.0))}


def kaide_kefesi(gorevler, taban: int = 16, basamak: int = 0
                 ) -> Dict[str, Any]:
    o = [kaide_halkasi(g, taban, basamak) for g in list(gorevler)]
    o = [x for x in o if int(x["K"]) >= 2]
    if not o:
        return {"kayıp": 0.0, "görev": 0, "küllî": 0, "yırtık": 0,
                "ortalama_r": 0.0}
    r = np.asarray([x["r"] for x in o], float)
    return {"kayıp": float(np.mean(1.0 - r)), "görev": len(o),
            "küllî": int(sum(1 for x in o if x["küllî"])),
            "yırtık": int(sum(1 for x in o if x["yırtık"])),
            "ortalama_r": float(r.mean()),
            "en_iyi_r": float(r.max()), "en_kötü_r": float(r.min())}


def ornekler(gorevler: Sequence, azami: int = 24, pencere: int = 8,
             sozluk: int = 0, tohum: int = 0, taban: int = 16,
             basamak: int = 0) -> List[Tuple[List[int], int, str]]:
    from .belirtec import basamak_sayisi, tip_vektoru
    from .musahede import soyutlama_oku
    from .belirtec import belirtecle

    rng = np.random.default_rng(tohum)
    tb = max(2, int(taban))
    bs = int(basamak) if int(basamak) > 0 else basamak_sayisi(
        int(sozluk) if int(sozluk) > 0 else tb, tb)
    P = max(1, int(pencere))
    cikti: List[Tuple[List[int], int, str]] = []

    def _zorla(bag_bas, hed_bas, cins: str) -> None:
        akis = list(bag_bas)
        for h in hed_bas:
            pen = akis[-P:] if len(akis) >= P else ([0] * (P - len(akis))
                                                    + akis)
            cikti.append(([int(x) for x in pen], int(h), cins))
            akis.append(int(h))

    for g in gorevler:
        dizi, hedef = gorev_dizisi(g, hedef_indis=0)
        assert len(dizi) > 0, "görev %r BOŞ dizi verdi" % getattr(g, "ad", "")
        bag_bas = tip_vektoru(list(dizi), tb, bs)
        hed_bas = tip_vektoru(list(hedef), tb, bs)
        _zorla(bag_bas, hed_bas, "arc")
        soz = soyutlama_oku(getattr(g, "ad", "") or "")
        if soz:
            soz_bas = tip_vektoru(belirtecle(soz), tb, bs)
            _zorla(bag_bas, soz_bas, "arc_sözlü")
        if len(cikti) >= azami:
            break
    if len(cikti) > int(azami):
        se = rng.choice(len(cikti), size=int(azami), replace=False)
        cikti = [cikti[int(i)] for i in sorted(se)]
    return cikti


def adayin_tuttugu(nefs: QNefs, veri: Sequence[Tuple[List[int], int]],
                   p: Optional[np.ndarray] = None, sozluk: int = 16,
                   lam_mizan: float = 0.25, lam_top: float = 0.1,
                   ne: str = "uygunluk", o=None,
                   cevap_isteniyor: bool = True, baglam=None):
    def kos(bag):
        E = belirtecleri_kodla(bag, nefs.ayar.veri_lifi,
                               nefs.ayar.veri_lifi)
        q = nefs.idrak_et(E)
        return q.beyan(0), q.olcumler()

    def mizan(olc, ister=True):
        ceza = 0.0
        ceza += 1.0 * float(olc.get("tenakuz", 0.0))
        ceza += 1.0 * float(olc.get("nakz", 0.0))
        ceza += 1.0 * (1.0 - float(olc.get("tasdik", 0.0)))
        if ister:
            ceza += 0.5 * float(olc.get("sukut", 0.0))
        ceza += 0.5 * float(olc.get("P_Şek", 0.0))
        return ceza

    if ne == "koş":
        return kos(baglam)
    if ne == "mizan":
        return mizan(o, cevap_isteniyor)
    if ne not in ("uygunluk", "hedef", "ikisi"):
        raise ValueError("aday ölçüsünün kipi bilinmiyor: %r" % (ne,))

    if p is not None:
        nefs.yukle(p)
    if not len(veri):
        return (0.0, 0.0) if ne == "ikisi" else 0.0

    top = 0.0
    ceza = 0.0
    hedef_top = 0.0
    for bag, hedef, _cins in (ornek_bol(o) for o in veri):
        P, olc = kos(bag)
        top -= float(np.log(P[hedef % len(P)] + 1e-12))
        ceza += lam_mizan * mizan(olc)
        ceza -= lam_top * float(olc.get("entropi", 0.0))
        y = np.zeros_like(P)
        y[hedef % len(P)] = 1.0
        hedef_top += float(np.sum((P - y) ** 2))
    V = (top + ceza) / len(veri)
    H = hedef_top / len(veri)
    if ne == "uygunluk":
        return V
    if ne == "hedef":
        return H
    return V, H


def egit(nefs: QNefs, veri: Sequence[Tuple[List[int], int]],
         cevrim: int = 4, r: int = 2, n_ornek: int = 8, izgara: int = 16,
         sozluk: int = 16, ayrik: bool = True, lam_hedef: float = 0.5,
         gama_azami: float = 0.3, tohum: int = 0,
         gunluk: Optional[List[str]] = None) -> Dict[str, object]:
    adayin_tuttugu(nefs, (), sozluk=sozluk, ne="koş", baglam=[0] * 4)
    p = nefs.vektor()
    V0 = adayin_tuttugu(nefs, veri, p, sozluk)
    kayit: List[float] = [V0]
    t0 = time.perf_counter()
    D = tuple(mertebe.DINAMIK)
    gama = 0.0
    tunel: List[float] = []

    for c in range(cevrim):
        _, o = adayin_tuttugu(nefs, (), sozluk=sozluk, ne="koş", baglam=veri[0][0])
        tikanik = float(o.get("tenakuz", 0.0))
        sikisti = c > 0 and kayit[-1] >= kayit[-2] - 1e-9
        if sikisti and tikanik > 0.5:
            gama = min(gama_azami, gama + 0.1)
        elif not sikisti:
            gama = 0.0
        tunel.append(gama)
        if gama > 0.0:
            p = p + gama * np.random.default_rng(tohum + 100 + c).normal(
                scale=0.3, size=len(p))

        p_yeni, tani = as_gek_adimi(
            lambda q: adayin_tuttugu(nefs, veri, q, sozluk), p,
            yaricap=0.5, r=r, izgara=izgara, n_ornek=n_ornek,
            hedef_ceza=lambda q: adayin_tuttugu(nefs, veri[:3], q, sozluk, ne="hedef"),
            lam_hedef=lam_hedef, tohum=tohum + c)
        V_yeni = adayin_tuttugu(nefs, veri, p_yeni, sozluk)
        if V_yeni < kayit[-1]:
            p, V = p_yeni, V_yeni
        else:
            V = kayit[-1]
        kayit.append(V)
        nefs.yukle(p)

        if ayrik:
            _, o = adayin_tuttugu(nefs, (), sozluk=sozluk, ne="koş", baglam=veri[0][0])
            tik = {m: float(o.get("tenakuz", 0.0)) * (1.0 + i * 0.05)
                   for i, m in enumerate(D)}
            adres = ayrik_mertebede_sicra(tikaniklik=tik, mevcut=D, ne="adres")
            aday = list(D)
            aday[int(np.argmax([tik[m] for m in aday]))] = adres

            def E_ayrik(vek: Tuple[int, ...]) -> float:
                mertebe.DINAMIK = tuple(vek)
                return adayin_tuttugu(nefs, veri[:2], p, sozluk)

            D_yeni, _ = ayrik_mertebede_sicra(enerji=E_ayrik, D0=aday, adim=6,
                                        tohum=tohum + c)
            mertebe.DINAMIK = tuple(D_yeni)
            D = tuple(D_yeni)

        if gunluk is not None:
            gunluk.append("çevrim %d: V=%.4f  aktif_özdeğer=%.3f  Γ=%.2f  "
                          "hedef_ceza=%.3f  D=%s"
                          % (c, V, tani["özdeğer_oranı"], gama,
                             tani.get("hedef_cezası", float("nan")),
                             list(D)[:4]))

    nefs.yukle(p)
    return {"V_ilk": V0, "V_son": kayit[-1], "seyir": kayit,
            "süre_sn": time.perf_counter() - t0, "dinamik": D,
            "parametre": len(nefs), "tünel": tunel,
            "tünel_açıldı": float(sum(1 for g in tunel if g > 0.0))}


def _degerlendir_mudrike(nefs, gorevler: Sequence, azami: int,
                         derinlik: int) -> Dict[str, object]:
    from .kulli_kayip import suz as _mudrike

    deneme = cozulen = konusan = yanlis = sukut = 0
    hucre: List[float] = []
    sebepler: Dict[str, int] = {}
    for g in gorevler:
        if deneme >= azami:
            break
        if not getattr(g, "sinama", None) or not getattr(g, "egitim", None):
            continue
        deneme += 1
        r = _mudrike(g, derinlik=derinlik, dalga=True, nefs=nefs)
        if r["sükût"]:
            sukut += 1
            sebepler[r["sebep"]] = sebepler.get(r["sebep"], 0) + 1
            hucre.append(0.0)
            continue
        konusan += 1
        tam = True
        oran = []
        for (a, b), c in zip(g.sinama, r["cevap"]):
            if c is None or c.shape != b.shape:
                tam = False
                oran.append(0.0)
                continue
            e = float(np.mean(c == b))
            oran.append(e)
            if e < 1.0:
                tam = False
        hucre.append(float(np.mean(oran)) if oran else 0.0)
        cozulen += tam
        yanlis += (not tam)
    return {"deneme": deneme, "tam_çözülen": cozulen,
            "konuşan": konusan, "yanlış_cevap": yanlis,
            "sükût": sukut, "atlanan_uzun": 0,
            "sükût_sebepleri": sebepler,
            "ilk_belirteç_isabeti": cozulen,
            "isabet_konuşunca": (cozulen / konusan) if konusan else 0.0,
            "ortalama_hücre_isabeti":
                float(np.mean(hucre)) if hucre else 0.0}


def degerlendir(nefs: QNefs, gorevler: Sequence, azami: int = 8,
                pencere: int = 8, sozluk: int = 16,
                azami_uret: int = 0, ayna=None, mudrike_ile: bool = False,
                derinlik: int = 2) -> Dict[str, object]:
    from .belirtec import basamak_sayisi as _basamak, tip_vektoru as _tip

    if mudrike_ile:
        return _degerlendir_mudrike(nefs, gorevler, azami, derinlik)
    cozulen = isabet = deneme = atlanan = 0
    hucre: List[float] = []
    sukut_sayisi = 0
    for g in gorevler:
        if deneme >= azami:
            break
        dizi, hedef = gorev_dizisi(g, hedef_indis=0)
        assert len(hedef) > 0, "görev %r BOŞ hedef verdi" % getattr(g, "ad", "")
        deneme += 1
        tb = int(nefs.ayar.veri_lifi)
        bs = _basamak(sozluk, tb)
        baglam = [int(x) for x in _tip(dizi, tb, bs)]
        h = [int(x) for x in _tip(hedef, tb, bs)]
        if 0 < azami_uret < len(h):
            atlanan += 1
            deneme -= 1
            continue
        uretilen: List[int] = []
        kac = len(h)
        for _ in range(kac):
            pen = baglam[-pencere:] if len(baglam) >= pencere else \
                ([0] * (pencere - len(baglam)) + baglam)
            P, o = adayin_tuttugu(nefs, (), sozluk=sozluk, ne="koş", baglam=pen)
            if o.get("sukut", 0.0) > 0.8:
                sukut_sayisi += 1
            from nefs.soyle import _sec
            t = _sec(P, ayna)
            uretilen.append(t)
            baglam.append(t)
        n = min(len(h), len(uretilen))
        dogru = sum(1 for i in range(n) if h[i] == uretilen[i])
        hucre.append(dogru / max(n, 1))
        if uretilen[:len(h)] == h:
            cozulen += 1
        if n and uretilen[0] == h[0]:
            isabet += 1
    return {"deneme": deneme, "tam_çözülen": cozulen,
            "atlanan_uzun": atlanan,
            "ölçüt_boş": bool(deneme == 0),
            "ilk_belirteç_isabeti": isabet, "sükût": sukut_sayisi,
            "ortalama_hücre_isabeti":
                float(np.mean(hucre)) if hucre else 0.0}
