"""
Terim seviyesinde İNŞA yardımcıları (indirgeme YOK).

NbE sürümünde indirgeme tamamen değer katmanındadır (``cekirdek.py``).
Bu dosya yalnızca terim KURMAK için lâzım olanları verir: taze isim,
yakalama-önleyici ikame ve ucuz akıllı kurucular (β ve izdüşüm). Hiçbir
Kan işlemi burada AÇILMAZ; ``Komp``/``HKomp``/``Transp`` düğümleri
olduğu gibi kurulur.
"""
from __future__ import annotations

import itertools
from typing import Dict, List, Optional, Sequence, Set, Tuple

from .aralik import BIR, SIFIR, Aralik, Kofibrasyon
from . import sozdizim as S
from .sozdizim import Terim, Yuz

_sayac = itertools.count()


def taze(taban: str = "x") -> str:
    return "%s!%d" % (taban.split("!")[0], next(_sayac))


# =====================================================================
#  Serbest değişkenler
# =====================================================================
_ara_serbest_onb: Dict = {}


def ara_serbest(t: Terim) -> Set[str]:
    onb = _ara_serbest_onb.get(t)
    if onb is not None:
        return onb
    g: Set[str] = set()

    def yuz_ekle(f, bagli):
        for (ad, _) in f:
            if ad not in bagli:
                g.add(ad)

    def yur(t: Terim, bagli: Set[str]) -> None:
        if isinstance(t, (S.Deg, S.Evren, S.Dogal, S.Tamsayi, S.Cember,
                          S.Taban, S.Sfr)):
            return
        if isinstance(t, S.Dongu):
            g.update(t.r.degiskenler() - bagli); return
        if isinstance(t, S.YolUygula):
            yur(t.yol, bagli); g.update(t.r.degiskenler() - bagli); return
        if isinstance(t, S.YolLam):
            yur(t.govde, bagli | {t.ad}); return
        if isinstance(t, S.YolP):
            yur(t.cizgi, bagli | {t.ad}); yur(t.sol, bagli); yur(t.sag, bagli)
            return
        if isinstance(t, S.Transp):
            yur(t.cizgi, bagli | {t.ad})
            for f in t.kof.yuzler:
                yuz_ekle(f, bagli)
            yur(t.u0, bagli); return
        if isinstance(t, S.Komp):
            yur(t.cizgi, bagli | {t.ad})
            for (f, govde) in t.dallar:
                yuz_ekle(f, bagli); yur(govde, bagli | {t.ad})
            yur(t.u0, bagli); return
        if isinstance(t, S.HKomp):
            yur(t.tip, bagli)
            for (f, govde) in t.dallar:
                yuz_ekle(f, bagli); yur(govde, bagli | {t.ad})
            yur(t.u0, bagli); return
        if isinstance(t, S.Yapistir):
            yur(t.taban, bagli)
            for (f, T, e) in t.dallar:
                yuz_ekle(f, bagli); yur(T, bagli); yur(e, bagli)
            return
        if isinstance(t, S.YapistirTerim):
            yur(t.taban_terim, bagli)
            for (f, govde) in t.dallar:
                yuz_ekle(f, bagli); yur(govde, bagli)
            return
        if isinstance(t, S.Coz):
            yur(t.taban, bagli)
            for (f, T, e) in t.dallar:
                yuz_ekle(f, bagli); yur(T, bagli); yur(e, bagli)
            yur(t.govde, bagli); return
        if isinstance(t, S.CemberInd):
            yur(t.hedef, bagli); yur(t.taban_dali, bagli)
            yur(t.dongu_dali, bagli | {t.i_ad}); yur(t.nokta, bagli); return
        for alt in _alt(t):
            yur(alt, bagli)

    yur(t, set())
    if len(_ara_serbest_onb) < 300000:
        _ara_serbest_onb[t] = g
    return g


def _alt(t: Terim) -> List[Terim]:
    if isinstance(t, (S.Pi, S.Sigma)):
        return [t.alan, t.hedef]
    if isinstance(t, S.Lam):
        return [t.govde]
    if isinstance(t, S.Uygula):
        return [t.fonk, t.arg]
    if isinstance(t, S.Cift):
        return [t.bir, t.iki]
    if isinstance(t, (S.Birinci, S.Ikinci)):
        return [t.cift]
    if isinstance(t, (S.Ard, S.Poz, S.NegArd)):
        return [t.alt]
    if isinstance(t, S.DogalInd):
        return [t.hedef, t.sfr_dali, t.ard_dali, t.sayi]
    if isinstance(t, S.TamsayiInd):
        return [t.hedef, t.poz_dali, t.neg_dali, t.sayi]
    return []


# =====================================================================
#  Ucuz akıllı kurucular
# =====================================================================
def uygula(fonk: Terim, arg: Terim) -> Terim:
    if isinstance(fonk, S.Lam):
        return ikame(fonk.govde, {fonk.ad: arg})
    return S.Uygula(fonk, arg)


def birinci(c: Terim) -> Terim:
    return c.bir if isinstance(c, S.Cift) else S.Birinci(c)


def ikinci(c: Terim) -> Terim:
    return c.iki if isinstance(c, S.Cift) else S.Ikinci(c)


def yol_uygula(p: Terim, r: Aralik) -> Terim:
    if isinstance(p, S.YolLam):
        return ara_ikame(p.govde, {p.ad: r})
    return S.YolUygula(p, r)


def uygula_hepsi(f: Terim, *args: Terim) -> Terim:
    for a in args:
        f = uygula(f, a)
    return f


# =====================================================================
#  Aralık ikamesi (yalnız İNŞA; Kan işlemleri açılmaz)
# =====================================================================
def _dallar_ara_ikame(dallar, sigma: Dict[str, Aralik], don) -> List:
    yeni = []
    for dal in dallar:
        k = Kofibrasyon([dal[0]]).yerine_koy(sigma)
        if k.bos_mu():
            continue
        govdeler = tuple(don(x) for x in dal[1:])
        for f in k.yuzler:
            yeni.append((f,) + govdeler)
    return yeni


def ara_ikame(t: Terim, sigma: Dict[str, Aralik]) -> Terim:
    if not sigma:
        return t
    f = lambda x: ara_ikame(x, sigma)
    if isinstance(t, (S.Deg, S.Evren, S.Dogal, S.Tamsayi, S.Cember,
                      S.Taban, S.Sfr)):
        return t
    if isinstance(t, S.Dongu):
        r = t.r.yerine_koy(sigma)
        return S.Taban() if (r.sifir_mi() or r.bir_mi()) else S.Dongu(r)
    if isinstance(t, S.YolUygula):
        return yol_uygula(f(t.yol), t.r.yerine_koy(sigma))
    if isinstance(t, S.Pi):
        return S.Pi(t.ad, f(t.alan), f(t.hedef))
    if isinstance(t, S.Sigma):
        return S.Sigma(t.ad, f(t.alan), f(t.hedef))
    if isinstance(t, S.Lam):
        return S.Lam(t.ad, f(t.govde))
    if isinstance(t, S.Uygula):
        return uygula(f(t.fonk), f(t.arg))
    if isinstance(t, S.Cift):
        return S.Cift(f(t.bir), f(t.iki))
    if isinstance(t, S.Birinci):
        return birinci(f(t.cift))
    if isinstance(t, S.Ikinci):
        return ikinci(f(t.cift))
    if isinstance(t, S.Ard):
        return S.Ard(f(t.alt))
    if isinstance(t, S.Poz):
        return S.Poz(f(t.alt))
    if isinstance(t, S.NegArd):
        return S.NegArd(f(t.alt))
    if isinstance(t, S.YolLam):
        yeni = taze(t.ad)
        return S.YolLam(yeni, f(ara_ikame(t.govde,
                                          {t.ad: Aralik.degisken(yeni)})))
    if isinstance(t, S.YolP):
        yeni = taze(t.ad)
        return S.YolP(yeni, f(ara_ikame(t.cizgi, {t.ad: Aralik.degisken(yeni)})),
                      f(t.sol), f(t.sag))
    if isinstance(t, S.Transp):
        yeni = taze(t.ad)
        return S.Transp(yeni, f(ara_ikame(t.cizgi, {t.ad: Aralik.degisken(yeni)})),
                        t.kof.yerine_koy(sigma), f(t.u0))
    if isinstance(t, S.Komp):
        yeni = taze(t.ad)
        ic = {t.ad: Aralik.degisken(yeni)}
        return S.Komp(yeni, f(ara_ikame(t.cizgi, ic)),
                      _dallar_ara_ikame(t.dallar, sigma,
                                        lambda g: f(ara_ikame(g, ic))),
                      f(t.u0))
    if isinstance(t, S.HKomp):
        yeni = taze(t.ad)
        ic = {t.ad: Aralik.degisken(yeni)}
        return S.HKomp(f(t.tip), yeni,
                       _dallar_ara_ikame(t.dallar, sigma,
                                         lambda g: f(ara_ikame(g, ic))),
                       f(t.u0))
    if isinstance(t, S.Yapistir):
        dallar = _dallar_ara_ikame(t.dallar, sigma, f)
        for (y, T, _e) in dallar:
            if not y:
                return T
        return S.Yapistir(f(t.taban), dallar) if dallar else f(t.taban)
    if isinstance(t, S.YapistirTerim):
        dallar = _dallar_ara_ikame(t.dallar, sigma, f)
        for (y, g) in dallar:
            if not y:
                return g
        return (S.YapistirTerim(dallar, f(t.taban_terim)) if dallar
                else f(t.taban_terim))
    if isinstance(t, S.Coz):
        dallar = _dallar_ara_ikame(t.dallar, sigma, f)
        govde = f(t.govde)
        for (y, _T, e) in dallar:
            if not y:
                return uygula(birinci(e), govde)
        return S.Coz(f(t.taban), dallar, govde) if dallar else govde
    if isinstance(t, S.DogalInd):
        return S.DogalInd(t.ad, f(t.hedef), f(t.sfr_dali), t.n_ad, t.rec_ad,
                          f(t.ard_dali), f(t.sayi))
    if isinstance(t, S.TamsayiInd):
        return S.TamsayiInd(t.ad, f(t.hedef), t.poz_ad, f(t.poz_dali),
                            t.neg_ad, f(t.neg_dali), f(t.sayi))
    if isinstance(t, S.CemberInd):
        yeni = taze(t.i_ad)
        return S.CemberInd(t.ad, f(t.hedef), f(t.taban_dali), yeni,
                           f(ara_ikame(t.dongu_dali,
                                       {t.i_ad: Aralik.degisken(yeni)})),
                           f(t.nokta))
    raise TypeError("ara_ikame: bilinmeyen terim %r" % (t,))


def ikame(t: Terim, sigma: Dict[str, Terim]) -> Terim:
    if not sigma:
        return t
    f = lambda x: ikame(x, sigma)
    if isinstance(t, S.Deg):
        return sigma.get(t.ad, t)
    if isinstance(t, (S.Evren, S.Dogal, S.Tamsayi, S.Cember, S.Taban,
                      S.Sfr, S.Dongu)):
        return t

    def bagla(ad, govde):
        yeni = taze(ad)
        return yeni, ikame(govde, {ad: S.Deg(yeni)})

    if isinstance(t, S.Pi):
        ad2, gv = bagla(t.ad, t.hedef); return S.Pi(ad2, f(t.alan), f(gv))
    if isinstance(t, S.Sigma):
        ad2, gv = bagla(t.ad, t.hedef); return S.Sigma(ad2, f(t.alan), f(gv))
    if isinstance(t, S.Lam):
        ad2, gv = bagla(t.ad, t.govde); return S.Lam(ad2, f(gv))
    if isinstance(t, S.Uygula):
        return uygula(f(t.fonk), f(t.arg))
    if isinstance(t, S.Cift):
        return S.Cift(f(t.bir), f(t.iki))
    if isinstance(t, S.Birinci):
        return birinci(f(t.cift))
    if isinstance(t, S.Ikinci):
        return ikinci(f(t.cift))
    if isinstance(t, S.Ard):
        return S.Ard(f(t.alt))
    if isinstance(t, S.Poz):
        return S.Poz(f(t.alt))
    if isinstance(t, S.NegArd):
        return S.NegArd(f(t.alt))
    if isinstance(t, S.YolP):
        return S.YolP(t.ad, f(t.cizgi), f(t.sol), f(t.sag))
    if isinstance(t, S.YolLam):
        return S.YolLam(t.ad, f(t.govde))
    if isinstance(t, S.YolUygula):
        return yol_uygula(f(t.yol), t.r)
    if isinstance(t, S.Transp):
        return S.Transp(t.ad, f(t.cizgi), t.kof, f(t.u0))
    if isinstance(t, S.Komp):
        return S.Komp(t.ad, f(t.cizgi), [(y, f(g)) for (y, g) in t.dallar],
                      f(t.u0))
    if isinstance(t, S.HKomp):
        return S.HKomp(f(t.tip), t.ad, [(y, f(g)) for (y, g) in t.dallar],
                       f(t.u0))
    if isinstance(t, S.Yapistir):
        return S.Yapistir(f(t.taban), [(y, f(T), f(e)) for (y, T, e) in t.dallar])
    if isinstance(t, S.YapistirTerim):
        return S.YapistirTerim([(y, f(g)) for (y, g) in t.dallar],
                               f(t.taban_terim))
    if isinstance(t, S.Coz):
        return S.Coz(f(t.taban), [(y, f(T), f(e)) for (y, T, e) in t.dallar],
                     f(t.govde))
    if isinstance(t, S.DogalInd):
        ad2, hd = bagla(t.ad, t.hedef)
        n2, r2 = taze(t.n_ad), taze(t.rec_ad)
        ard = ikame(t.ard_dali, {t.n_ad: S.Deg(n2), t.rec_ad: S.Deg(r2)})
        return S.DogalInd(ad2, f(hd), f(t.sfr_dali), n2, r2, f(ard), f(t.sayi))
    if isinstance(t, S.TamsayiInd):
        ad2, hd = bagla(t.ad, t.hedef)
        p2, n2 = taze(t.poz_ad), taze(t.neg_ad)
        pd = ikame(t.poz_dali, {t.poz_ad: S.Deg(p2)})
        nd = ikame(t.neg_dali, {t.neg_ad: S.Deg(n2)})
        return S.TamsayiInd(ad2, f(hd), p2, f(pd), n2, f(nd), f(t.sayi))
    if isinstance(t, S.CemberInd):
        ad2, hd = bagla(t.ad, t.hedef)
        return S.CemberInd(ad2, f(hd), f(t.taban_dali), t.i_ad,
                           f(t.dongu_dali), f(t.nokta))
    raise TypeError("ikame: bilinmeyen terim %r" % (t,))


# =====================================================================
#  Kan düğümü kurucuları (İNŞA; açılım değer katmanında)
# =====================================================================
def transp(ad: str, cizgi: Terim, kof: Kofibrasyon, u0: Terim) -> Terim:
    if kof.dogru_mu():
        return u0
    return S.Transp(ad, cizgi, kof, u0)


def hkomp(tip: Terim, ad: str, dallar, u0: Terim) -> Terim:
    for (y, g) in dallar:
        if not y:
            return ara_ikame(g, {ad: BIR})
    if not dallar:
        return u0
    return S.HKomp(tip, ad, dallar, u0)


def komp(ad: str, cizgi: Terim, dallar, u0: Terim) -> Terim:
    for (y, g) in dallar:
        if not y:
            return ara_ikame(g, {ad: BIR})
    if not dallar and ad not in ara_serbest(cizgi):
        return u0
    return S.Komp(ad, cizgi, dallar, u0)


def dolgu(ad: str, cizgi: Terim, dallar, u0: Terim) -> Terim:
    """``fill^ad`` -- ``ad`` serbest kalır; ``fill@0 = u0``, ``fill@1 = comp``."""
    j = taze("j")
    ikj = {ad: Aralik.degisken(ad).ve(Aralik.degisken(j))}
    yeni_dallar = list(_dallar_ara_ikame(dallar, ikj,
                                         lambda g: ara_ikame(g, ikj)))
    yeni_dallar.append((S.yuz(**{ad: 0}), u0))
    return komp(j, ara_ikame(cizgi, ikj), yeni_dallar, u0)
