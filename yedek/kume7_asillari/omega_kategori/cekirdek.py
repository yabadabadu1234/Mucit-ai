"""
Kübik çekirdek: ikame, zayıf-baş normal form ve Kan işlemleri.

Tasarım: NbE (değerlerle normalleştirme) yerine TERİM SEVİYESİNDE, açık
ikameli bir indirgeyici kullanılır. Sebebi doğrudan doğruluktur: kübik tip
teorisinde değerlerin aralık ikamesi altında davranışı (özellikle yerli
Python kapanışlarının ikamesi) ince bir mesele iken, terim seviyesinde
aralık ikamesi ``Aralik``/``Kofibrasyon`` cebrine devredilerek bedavaya
gelir -- bir yüzün ikame altında birden çok yüze AÇILMASI (meselâ
``(i=0)[i↦j∧k] = (j=0)∨(k=0)``) burada tabii biçimde ele alınır.

ASLİ Kan işlemi ``comp``dır (CCHM sunumu); ``transp``, ``hcomp`` ve
``fill`` ondan türetilir.

Bu dosyadaki indirgeme kuralları, iki yerde bir BAĞLAM'a ihtiyaç duyar:
neutral bir yolun uçta uygulanması (``p @ 0 ↝ sol``) ve neutral bir Glue
teriminin çözülmesi. Bu yüzden ``whnf`` isteğe bağlı bir bağlam alır.
"""
from __future__ import annotations

import itertools
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

from .aralik import (BIR, DOGRU, SIFIR, YANLIS, Aralik, Kofibrasyon,
                     aralik_esitligi)
from . import sozdizim as S
from .sozdizim import Terim, Yuz

_sayac = itertools.count()


def taze(taban: str = "x") -> str:
    return "%s!%d" % (taban.split("!")[0], next(_sayac))


Baglam = Dict[str, Terim]


class TipHatasi(Exception):
    pass


# =====================================================================
#  Önbellek
# =====================================================================
# Terimler değişmez ve hash'lenebilir; bağlamlar da kurulduktan sonra
# değiştirilmez. Bu yüzden (bağlam kimliği, terim) çifti güvenli bir
# anahtardır. Yığılmış comp'larda aynı alt terim defalarca
# normalleştirildiğinden kazanç büyüktür.
_ONBELLEK_SINIRI = 400000
_nf_onb: Dict = {}
_whnf_onb: Dict = {}
_serbest_onb: Dict = {}
_ikame_onb: Dict = {}
_komp_onb: Dict = {}
_baglam_capa: List = []
_baglam_kimlik: Set[int] = set()


def _capala(baglam) -> None:
    """Bağlamı canlı tut ki id() yeniden kullanılmasın."""
    if baglam is not None and id(baglam) not in _baglam_kimlik:
        _baglam_kimlik.add(id(baglam))
        _baglam_capa.append(baglam)


def onbellegi_bosalt() -> None:
    _nf_onb.clear()
    _whnf_onb.clear()
    _serbest_onb.clear()
    _ikame_onb.clear()
    _komp_onb.clear()


# =====================================================================
#  Serbest değişkenler
# =====================================================================
def ara_serbest(t: Terim) -> Set[str]:
    """Terimdeki serbest ARALIK değişkenleri."""
    onb = _serbest_onb.get(t)
    if onb is not None:
        return onb
    g: Set[str] = set()

    def yuzler_ekle(dallar):
        for dal in dallar:
            for (ad, _) in dal[0]:
                g.add(ad)

    def yur(t: Terim, bagli: Set[str]) -> None:
        if isinstance(t, (S.Deg, S.Evren, S.Dogal, S.Tamsayi, S.Cember,
                          S.Taban, S.Sfr)):
            return
        if isinstance(t, S.Dongu):
            g.update(t.r.degiskenler() - bagli)
            return
        if isinstance(t, S.YolUygula):
            yur(t.yol, bagli)
            g.update(t.r.degiskenler() - bagli)
            return
        if isinstance(t, (S.YolLam,)):
            yur(t.govde, bagli | {t.ad})
            return
        if isinstance(t, S.YolP):
            yur(t.cizgi, bagli | {t.ad})
            yur(t.sol, bagli)
            yur(t.sag, bagli)
            return
        if isinstance(t, S.Transp):
            yur(t.cizgi, bagli | {t.ad})
            for f in t.kof.yuzler:
                for (ad, _) in f:
                    if ad not in bagli:
                        g.add(ad)
            yur(t.u0, bagli)
            return
        if isinstance(t, S.Komp):
            yur(t.cizgi, bagli | {t.ad})
            for (f, govde) in t.dallar:
                for (ad, _) in f:
                    if ad not in bagli:
                        g.add(ad)
                yur(govde, bagli | {t.ad})
            yur(t.u0, bagli)
            return
        if isinstance(t, S.HKomp):
            yur(t.tip, bagli)
            for (f, govde) in t.dallar:
                for (ad, _) in f:
                    if ad not in bagli:
                        g.add(ad)
                yur(govde, bagli | {t.ad})
            yur(t.u0, bagli)
            return
        if isinstance(t, S.Yapistir):
            yur(t.taban, bagli)
            for (f, T, e) in t.dallar:
                for (ad, _) in f:
                    if ad not in bagli:
                        g.add(ad)
                yur(T, bagli)
                yur(e, bagli)
            return
        if isinstance(t, S.YapistirTerim):
            yur(t.taban_terim, bagli)
            for (f, govde) in t.dallar:
                for (ad, _) in f:
                    if ad not in bagli:
                        g.add(ad)
                yur(govde, bagli)
            return
        if isinstance(t, S.Coz):
            yur(t.taban, bagli)
            for (f, T, e) in t.dallar:
                for (ad, _) in f:
                    if ad not in bagli:
                        g.add(ad)
                yur(T, bagli)
                yur(e, bagli)
            yur(t.govde, bagli)
            return
        for alt in _alt_terimler(t):
            yur(alt, bagli)

    yur(t, set())
    if len(_serbest_onb) < _ONBELLEK_SINIRI:
        _serbest_onb[t] = g
    return g


def _alt_terimler(t: Terim) -> List[Terim]:
    """Bağlayıcı yapısını umursamadan doğrudan alt terimler."""
    if isinstance(t, S.Pi) or isinstance(t, S.Sigma):
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
    if isinstance(t, S.CemberInd):
        return [t.hedef, t.taban_dali, t.dongu_dali, t.nokta]
    return []


def serbest(t: Terim) -> Set[str]:
    """Terimdeki serbest TERİM değişkenleri."""
    g: Set[str] = set()

    def yur(t: Terim, bagli: Set[str]) -> None:
        if isinstance(t, S.Deg):
            if t.ad not in bagli:
                g.add(t.ad)
            return
        if isinstance(t, (S.Pi, S.Sigma)):
            yur(t.alan, bagli)
            yur(t.hedef, bagli | {t.ad})
            return
        if isinstance(t, S.Lam):
            yur(t.govde, bagli | {t.ad})
            return
        if isinstance(t, S.DogalInd):
            yur(t.hedef, bagli | {t.ad})
            yur(t.sfr_dali, bagli)
            yur(t.ard_dali, bagli | {t.n_ad, t.rec_ad})
            yur(t.sayi, bagli)
            return
        if isinstance(t, S.TamsayiInd):
            yur(t.hedef, bagli | {t.ad})
            yur(t.poz_dali, bagli | {t.poz_ad})
            yur(t.neg_dali, bagli | {t.neg_ad})
            yur(t.sayi, bagli)
            return
        if isinstance(t, S.CemberInd):
            yur(t.hedef, bagli | {t.ad})
            yur(t.taban_dali, bagli)
            yur(t.dongu_dali, bagli)
            yur(t.nokta, bagli)
            return
        if isinstance(t, S.YolP):
            yur(t.cizgi, bagli)
            yur(t.sol, bagli)
            yur(t.sag, bagli)
            return
        if isinstance(t, S.YolLam):
            yur(t.govde, bagli)
            return
        if isinstance(t, S.YolUygula):
            yur(t.yol, bagli)
            return
        if isinstance(t, S.Transp):
            yur(t.cizgi, bagli)
            yur(t.u0, bagli)
            return
        if isinstance(t, S.Komp):
            yur(t.cizgi, bagli)
            for (_, govde) in t.dallar:
                yur(govde, bagli)
            yur(t.u0, bagli)
            return
        if isinstance(t, S.HKomp):
            yur(t.tip, bagli)
            for (_, govde) in t.dallar:
                yur(govde, bagli)
            yur(t.u0, bagli)
            return
        if isinstance(t, S.Yapistir):
            yur(t.taban, bagli)
            for (_, T, e) in t.dallar:
                yur(T, bagli)
                yur(e, bagli)
            return
        if isinstance(t, S.YapistirTerim):
            yur(t.taban_terim, bagli)
            for (_, govde) in t.dallar:
                yur(govde, bagli)
            return
        if isinstance(t, S.Coz):
            yur(t.taban, bagli)
            for (_, T, e) in t.dallar:
                yur(T, bagli)
                yur(e, bagli)
            yur(t.govde, bagli)
            return
        for alt in _alt_terimler(t):
            yur(alt, bagli)

    yur(t, set())
    return g


# =====================================================================
#  Aralık ikamesi
# =====================================================================
def _dallar_ara_ikame(dallar, sigma: Dict[str, Aralik], govde_don) -> List:
    """Sistem dallarına aralık ikamesi; bir yüz birden çok yüze açılabilir."""
    yeni = []
    for dal in dallar:
        y = dal[0]
        k = Kofibrasyon([y]).yerine_koy(sigma)
        if k.bos_mu():
            continue
        govdeler = tuple(govde_don(x) for x in dal[1:])
        for f in k.yuzler:
            yeni.append((f,) + govdeler)
    return yeni


def ara_ikame(t: Terim, sigma: Dict[str, Aralik]) -> Terim:
    """Aralık değişkenlerinin eşzamanlı ikamesi."""
    if not sigma:
        return t
    anahtar = (t, frozenset(sigma.items()))
    onb = _ikame_onb.get(anahtar)
    if onb is not None:
        return onb
    sonuc = _ara_ikame_hesapla(t, sigma)
    if len(_ikame_onb) < _ONBELLEK_SINIRI:
        _ikame_onb[anahtar] = sonuc
    return sonuc


def _ara_ikame_hesapla(t: Terim, sigma: Dict[str, Aralik]) -> Terim:
    f = lambda x: ara_ikame(x, sigma)

    if isinstance(t, (S.Deg, S.Evren, S.Dogal, S.Tamsayi, S.Cember,
                      S.Taban, S.Sfr)):
        return t
    if isinstance(t, S.Dongu):
        return S.Dongu(t.r.yerine_koy(sigma))
    if isinstance(t, S.YolUygula):
        return S.YolUygula(f(t.yol), t.r.yerine_koy(sigma))
    if isinstance(t, S.Pi):
        return S.Pi(t.ad, f(t.alan), f(t.hedef))
    if isinstance(t, S.Sigma):
        return S.Sigma(t.ad, f(t.alan), f(t.hedef))
    if isinstance(t, S.Lam):
        return S.Lam(t.ad, f(t.govde))
    if isinstance(t, S.Uygula):
        return S.Uygula(f(t.fonk), f(t.arg))
    if isinstance(t, S.Cift):
        return S.Cift(f(t.bir), f(t.iki))
    if isinstance(t, S.Birinci):
        return S.Birinci(f(t.cift))
    if isinstance(t, S.Ikinci):
        return S.Ikinci(f(t.cift))
    if isinstance(t, S.Ard):
        return S.Ard(f(t.alt))
    if isinstance(t, S.Poz):
        return S.Poz(f(t.alt))
    if isinstance(t, S.NegArd):
        return S.NegArd(f(t.alt))

    # --- aralık bağlayıcıları: taze isme çevir, sonra ikame et ---
    if isinstance(t, S.YolLam):
        yeni = taze(t.ad)
        govde = ara_ikame(t.govde, {t.ad: Aralik.degisken(yeni)})
        return S.YolLam(yeni, f(govde))
    if isinstance(t, S.YolP):
        yeni = taze(t.ad)
        cizgi = ara_ikame(t.cizgi, {t.ad: Aralik.degisken(yeni)})
        return S.YolP(yeni, f(cizgi), f(t.sol), f(t.sag))
    if isinstance(t, S.Transp):
        yeni = taze(t.ad)
        cizgi = ara_ikame(t.cizgi, {t.ad: Aralik.degisken(yeni)})
        return transp(yeni, f(cizgi), t.kof.yerine_koy(sigma), f(t.u0))
    if isinstance(t, S.Komp):
        yeni = taze(t.ad)
        ic = {t.ad: Aralik.degisken(yeni)}
        cizgi = f(ara_ikame(t.cizgi, ic))
        dallar = _dallar_ara_ikame(t.dallar, sigma,
                                   lambda g: f(ara_ikame(g, ic)))
        return komp(yeni, cizgi, dallar, f(t.u0))
    if isinstance(t, S.HKomp):
        yeni = taze(t.ad)
        ic = {t.ad: Aralik.degisken(yeni)}
        dallar = _dallar_ara_ikame(t.dallar, sigma,
                                   lambda g: f(ara_ikame(g, ic)))
        return hkomp(f(t.tip), yeni, dallar, f(t.u0))
    if isinstance(t, S.Yapistir):
        return yapistir(f(t.taban),
                        _dallar_ara_ikame(t.dallar, sigma, f))
    if isinstance(t, S.YapistirTerim):
        return S.YapistirTerim(_dallar_ara_ikame(t.dallar, sigma, f),
                               f(t.taban_terim))
    if isinstance(t, S.Coz):
        return S.Coz(f(t.taban), _dallar_ara_ikame(t.dallar, sigma, f),
                     f(t.govde))
    if isinstance(t, S.DogalInd):
        return S.DogalInd(t.ad, f(t.hedef), f(t.sfr_dali), t.n_ad, t.rec_ad,
                          f(t.ard_dali), f(t.sayi))
    if isinstance(t, S.TamsayiInd):
        return S.TamsayiInd(t.ad, f(t.hedef), t.poz_ad, f(t.poz_dali),
                            t.neg_ad, f(t.neg_dali), f(t.sayi))
    if isinstance(t, S.CemberInd):
        yeni = taze(t.i_ad)
        dongu = ara_ikame(t.dongu_dali, {t.i_ad: Aralik.degisken(yeni)})
        return S.CemberInd(t.ad, f(t.hedef), f(t.taban_dali), yeni,
                           f(dongu), f(t.nokta))
    raise TipHatasi("ara_ikame: bilinmeyen terim %r" % (t,))


# =====================================================================
#  Terim ikamesi
# =====================================================================
def ikame(t: Terim, sigma: Dict[str, Terim]) -> Terim:
    """Terim değişkenlerinin eşzamanlı, yakalama-önleyici ikamesi."""
    if not sigma:
        return t
    f = lambda x: ikame(x, sigma)

    if isinstance(t, S.Deg):
        return sigma.get(t.ad, t)
    if isinstance(t, (S.Evren, S.Dogal, S.Tamsayi, S.Cember, S.Taban,
                      S.Sfr, S.Dongu)):
        return t

    def bagla(ad: str, govde: Terim) -> Tuple[str, Terim]:
        yeni = taze(ad)
        return yeni, ikame(govde, {ad: S.Deg(yeni)})

    if isinstance(t, S.Pi):
        ad2, govde = bagla(t.ad, t.hedef)
        return S.Pi(ad2, f(t.alan), f(govde))
    if isinstance(t, S.Sigma):
        ad2, govde = bagla(t.ad, t.hedef)
        return S.Sigma(ad2, f(t.alan), f(govde))
    if isinstance(t, S.Lam):
        ad2, govde = bagla(t.ad, t.govde)
        return S.Lam(ad2, f(govde))
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
        return transp(t.ad, f(t.cizgi), t.kof, f(t.u0))
    if isinstance(t, S.Komp):
        return komp(t.ad, f(t.cizgi),
                    [(y, f(g)) for (y, g) in t.dallar], f(t.u0))
    if isinstance(t, S.HKomp):
        return hkomp(f(t.tip), t.ad,
                     [(y, f(g)) for (y, g) in t.dallar], f(t.u0))
    if isinstance(t, S.Yapistir):
        return yapistir(f(t.taban), [(y, f(T), f(e)) for (y, T, e) in t.dallar])
    if isinstance(t, S.YapistirTerim):
        return S.YapistirTerim([(y, f(g)) for (y, g) in t.dallar],
                               f(t.taban_terim))
    if isinstance(t, S.Coz):
        return coz(f(t.taban), [(y, f(T), f(e)) for (y, T, e) in t.dallar],
                   f(t.govde))
    if isinstance(t, S.DogalInd):
        ad2, hedef = bagla(t.ad, t.hedef)
        n2 = taze(t.n_ad)
        r2 = taze(t.rec_ad)
        ard = ikame(t.ard_dali, {t.n_ad: S.Deg(n2), t.rec_ad: S.Deg(r2)})
        return dogal_ind(ad2, f(hedef), f(t.sfr_dali), n2, r2, f(ard),
                         f(t.sayi))
    if isinstance(t, S.TamsayiInd):
        ad2, hedef = bagla(t.ad, t.hedef)
        p2 = taze(t.poz_ad)
        n2 = taze(t.neg_ad)
        pd = ikame(t.poz_dali, {t.poz_ad: S.Deg(p2)})
        nd = ikame(t.neg_dali, {t.neg_ad: S.Deg(n2)})
        return tamsayi_ind(ad2, f(hedef), p2, f(pd), n2, f(nd), f(t.sayi))
    if isinstance(t, S.CemberInd):
        ad2, hedef = bagla(t.ad, t.hedef)
        return cember_ind(ad2, f(hedef), f(t.taban_dali), t.i_ad,
                          f(t.dongu_dali), f(t.nokta))
    raise TipHatasi("ikame: bilinmeyen terim %r" % (t,))


# =====================================================================
#  Akıllı kurucular (indirgeme yapan)
# =====================================================================
def uygula(fonk: Terim, arg: Terim) -> Terim:
    if isinstance(fonk, S.Lam):
        return ikame(fonk.govde, {fonk.ad: arg})
    return S.Uygula(fonk, arg)


def birinci(c: Terim) -> Terim:
    if isinstance(c, S.Cift):
        return c.bir
    return S.Birinci(c)


def ikinci(c: Terim) -> Terim:
    if isinstance(c, S.Cift):
        return c.iki
    return S.Ikinci(c)


def yol_uygula(p: Terim, r: Aralik) -> Terim:
    if isinstance(p, S.YolLam):
        return ara_ikame(p.govde, {p.ad: r})
    return S.YolUygula(p, r)


def _ust_yuz(dallar) -> Optional[Terim]:
    """Bir dalın yüzü ⊤ ise (yani şimdiden sağlanıyorsa) o dalı döndürür."""
    for dal in dallar:
        if not dal[0]:
            return dal[1]
    return None


def yapistir(taban: Terim, dallar) -> Terim:
    """``Glue taban [dallar]``; ⊤ yüzünde doğrudan T'ye çöker."""
    for (y, T, _e) in dallar:
        if not y:
            return T
    if not dallar:
        return taban
    return S.Yapistir(taban, dallar)


def yapistir_terim(dallar, taban_terim: Terim) -> Terim:
    t = _ust_yuz(dallar)
    if t is not None:
        return t
    if not dallar:
        return taban_terim
    return S.YapistirTerim(dallar, taban_terim)


def coz(taban: Terim, dallar, govde: Terim) -> Terim:
    """``unglue``: ⊤ yüzünde denkliğin fonksiyonunu uygular."""
    for (y, _T, e) in dallar:
        if not y:
            return uygula(birinci(e), govde)
    if not dallar:
        return govde
    # TEMBEL komp yüzünden gövde indirgenmemiş gelebilir; Glue'nun
    # β-kuralının (unglue (glue u …) ↝ u) kaçmaması için baş normal
    # forma indiriyoruz.
    g = whnf(govde)
    if isinstance(g, S.YapistirTerim):
        return g.taban_terim
    return S.Coz(taban, dallar, g)


def dogal_ind(ad, hedef, sfr_dali, n_ad, rec_ad, ard_dali, sayi) -> Terim:
    if isinstance(sayi, S.Sfr):
        return sfr_dali
    if isinstance(sayi, S.Ard):
        alt = sayi.alt
        rec = dogal_ind(ad, hedef, sfr_dali, n_ad, rec_ad, ard_dali, alt)
        return ikame(ard_dali, {n_ad: alt, rec_ad: rec})
    return S.DogalInd(ad, hedef, sfr_dali, n_ad, rec_ad, ard_dali, sayi)


def tamsayi_ind(ad, hedef, poz_ad, poz_dali, neg_ad, neg_dali, sayi) -> Terim:
    if isinstance(sayi, S.Poz):
        return ikame(poz_dali, {poz_ad: sayi.alt})
    if isinstance(sayi, S.NegArd):
        return ikame(neg_dali, {neg_ad: sayi.alt})
    return S.TamsayiInd(ad, hedef, poz_ad, poz_dali, neg_ad, neg_dali, sayi)


def cember_ind(ad, hedef, taban_dali, i_ad, dongu_dali, nokta) -> Terim:
    if isinstance(nokta, S.Taban):
        return taban_dali
    if isinstance(nokta, S.Dongu):
        if nokta.r.sifir_mi() or nokta.r.bir_mi():
            return taban_dali
        return ara_ikame(dongu_dali, {i_ad: nokta.r})
    if isinstance(nokta, S.HKomp):
        # S¹ eliminatörü hcomp ile DEĞİŞİR; hedefte bir comp doğar:
        #   S¹ind C b l (hcomp^i [φ↦u] u0)
        #     = comp^i (C (hfill^i [φ↦u] u0)) [φ ↦ S¹ind C b l (u i)]
        #              (S¹ind C b l u0)
        i = taze("i")
        dallar = _dallari_yeniden_adlandir(nokta.dallar, nokta.ad, i)
        hfill = dolgu(i, S.Cember(), dallar, nokta.u0)
        yeni_cizgi = ikame(hedef, {ad: hfill})
        yeni_dallar = [
            (y, cember_ind(ad, hedef, taban_dali, i_ad, dongu_dali, g))
            for (y, g) in dallar]
        taban_sonuc = cember_ind(ad, hedef, taban_dali, i_ad, dongu_dali,
                                 nokta.u0)
        return komp(i, yeni_cizgi, yeni_dallar, taban_sonuc)
    return S.CemberInd(ad, hedef, taban_dali, i_ad, dongu_dali, nokta)


def _dallari_yeniden_adlandir(dallar, eski: str, yeni: str):
    return [(y, ara_ikame(g, {eski: Aralik.degisken(yeni)})) for (y, g) in dallar]


# =====================================================================
#  Kan işlemleri
# =====================================================================
def transp(ad: str, cizgi: Terim, kof: Kofibrasyon, u0: Terim) -> Terim:
    """``transp^ad cizgi kof u0`` = ``comp^ad cizgi [kof ↦ u0] u0``."""
    if kof.dogru_mu():
        return u0
    return komp(ad, cizgi, [(y, u0) for y in kof.yuzler], u0)


def hkomp(tip: Terim, ad: str, dallar, u0: Terim) -> Terim:
    """``hcomp {tip} [dallar] u0`` -- ``tip`` içinde ``ad`` geçmez."""
    return komp(ad, tip, dallar, u0)


def dolgu(ad: str, cizgi: Terim, dallar, u0: Terim) -> Terim:
    """``fill^ad cizgi [dallar] u0`` -- ``ad`` serbest kalan dolgu.

    ``fill@0 = u0`` ve ``fill@1 = comp``.
    """
    j = taze("j")
    i_ar = Aralik.degisken(ad)
    j_ar = Aralik.degisken(j)
    ikj = {ad: i_ar.ve(j_ar)}
    yeni_cizgi = ara_ikame(cizgi, ikj)
    yeni_dallar = _dallar_ara_ikame(dallar, ikj, lambda g: ara_ikame(g, ikj))
    yeni_dallar = list(yeni_dallar) + [(S.yuz(**{ad: 0}), u0)]
    return komp(j, yeni_cizgi, yeni_dallar, u0)


def _ileri(ad: str, cizgi: Terim, r: Aralik, x: Terim) -> Terim:
    """``cizgi(r)`` içindeki ``x``i ``cizgi(1)``e taşır."""
    j = taze("j")
    j_ar = Aralik.degisken(j)
    yeni = ara_ikame(cizgi, {ad: r.veya(j_ar)})
    return transp(j, yeni, aralik_esitligi(r, True), x)


def _geri(ad: str, cizgi: Terim, r: Aralik, v: Terim) -> Terim:
    """``cizgi(1)`` içindeki ``v``yi ``cizgi(r)``ye taşır."""
    j = taze("j")
    j_ar = Aralik.degisken(j)
    yeni = ara_ikame(cizgi, {ad: r.veya(j_ar.degil())})
    return transp(j, yeni, aralik_esitligi(r, True), v)


def komp(ad: str, cizgi: Terim, dallar, u0: Terim,
         baglam: Optional[Baglam] = None) -> Terim:
    """ASLİ Kan işlemi: ``comp^ad cizgi [dallar] u0``."""
    dallar = list(dallar)
    # TEMBEL akıllı kurucu: yalnız UCUZ indirgemeleri yapar, tip yönlü
    # açılımı (_komp_ac) whnf'e bırakır. Bu, iç içe geçmiş Kan
    # işlemlerinin terim ağacını istekten önce şişirmesini engeller.
    for (y, govde) in dallar:
        if not y:                       # ⊤ yüz: dalın 1'deki değeri
            return ara_ikame(govde, {ad: BIR})
    if not dallar and ad not in ara_serbest(cizgi):
        return u0                       # sabit çizgi + boş sistem
    return S.Komp(ad, cizgi, dallar, u0)


def _komp_ac(ad: str, cizgi: Terim, dallar, u0: Terim,
             baglam: Optional[Baglam] = None) -> Terim:
    """``comp``un tip yönlü AÇILIMI -- yalnız whnf tarafından çağrılır."""
    dallar = list(dallar)
    anahtar = (ad, cizgi, tuple(dallar), u0, id(baglam))
    onb = _komp_onb.get(anahtar)
    if onb is not None:
        return onb
    sonuc = _komp_ac_hesapla(ad, cizgi, dallar, u0, baglam)
    if len(_komp_onb) < _ONBELLEK_SINIRI:
        _capala(baglam)
        _komp_onb[anahtar] = sonuc
    return sonuc


def _komp_ac_hesapla(ad: str, cizgi: Terim, dallar, u0: Terim,
                     baglam: Optional[Baglam] = None) -> Terim:

    # (a) Bir dalın yüzü zaten ⊤ ise, o dalın 1'deki değeri neticedir.
    for (y, govde) in dallar:
        if not y:
            return whnf(ara_ikame(govde, {ad: BIR}), baglam)

    A = whnf(cizgi, baglam)

    # (b) Sabit çizgi + boş sistem: özdeşlik.
    #     DİKKAT: "uçları eşitse çizgi sabittir" SAĞLAM DEĞİLDİR --
    #     ua e çizgisinin iki ucu da aynı tip olabilir (ℤ ile ℤ) hâlbuki
    #     çizgi sabit değildir ve taşıma özdeşlik değil sucZ'dir. Sabitlik
    #     ancak NORMAL FORMDA ad'ın serbest geçmemesiyle tespit edilir.
    if not dallar:
        if ad not in ara_serbest(A):
            return u0
        duz = nf(cizgi, baglam)
        if ad not in ara_serbest(duz):
            return u0
        A = whnf(duz, baglam)

    i_ar = Aralik.degisken(ad)

    # ---- Π ----
    if isinstance(A, S.Pi):
        v = taze("v")
        v_t = S.Deg(v)
        # w(i) : A(i), w(1) = v
        w_i = _geri(ad, A.alan, i_ar, v_t)
        w_0 = ara_ikame(w_i, {ad: SIFIR})
        yeni_cizgi = ikame(A.hedef, {A.ad: w_i})
        yeni_dallar = [(y, uygula(g, w_i)) for (y, g) in dallar]
        return S.Lam(v, komp(ad, yeni_cizgi, yeni_dallar,
                             uygula(u0, w_0), baglam))

    # ---- Σ ----
    if isinstance(A, S.Sigma):
        bir_dallar = [(y, birinci(g)) for (y, g) in dallar]
        a_i = dolgu(ad, A.alan, bir_dallar, birinci(u0))
        bir_sonuc = komp(ad, A.alan, bir_dallar, birinci(u0), baglam)
        iki_cizgi = ikame(A.hedef, {A.ad: a_i})
        iki_dallar = [(y, ikinci(g)) for (y, g) in dallar]
        iki_sonuc = komp(ad, iki_cizgi, iki_dallar, ikinci(u0), baglam)
        return S.Cift(bir_sonuc, iki_sonuc)

    # ---- PathP ----
    if isinstance(A, S.YolP):
        j = taze("j")
        j_ar = Aralik.degisken(j)
        ic_cizgi = ara_ikame(A.cizgi, {A.ad: j_ar})
        ic_dallar = [(y, yol_uygula(g, j_ar)) for (y, g) in dallar]
        ic_dallar.append((S.yuz(**{j: 0}), A.sol))
        ic_dallar.append((S.yuz(**{j: 1}), A.sag))
        govde = komp(ad, ic_cizgi, ic_dallar, yol_uygula(u0, j_ar), baglam)
        return S.YolLam(j, govde)

    # ---- veri tipleri (ℕ, ℤ): kurucuya İTİLEREK indirgenir ----
    # DİKKAT: "ayrık olduğu için comp = u0" SAĞLAM DEĞİLDİR -- sistemin
    # i=1'deki değeri tabana yalnız PROPOZİSYONEL eşittir, tanımsal değil.
    # Doğru kural, tabanın kurucusuna göre sistemi bileşenlere dağıtmaktır;
    # bütün dallar aynı kurucuyla başlamıyorsa comp TAKILI kalır.
    if isinstance(A, (S.Dogal, S.Tamsayi)):
        u0w = whnf(u0, baglam)
        govdeler = [whnf(g, baglam) for (_, g) in dallar]
        yuzler = [y for (y, _) in dallar]

        def _ic(ic_tip, alt_u0, altlar):
            return komp(ad, ic_tip, list(zip(yuzler, altlar)), alt_u0, baglam)

        if isinstance(u0w, S.Sfr) and all(isinstance(x, S.Sfr) for x in govdeler):
            return S.Sfr()
        if isinstance(u0w, S.Ard) and all(isinstance(x, S.Ard) for x in govdeler):
            return S.Ard(_ic(S.Dogal(), u0w.alt, [x.alt for x in govdeler]))
        if isinstance(u0w, S.Poz) and all(isinstance(x, S.Poz) for x in govdeler):
            return S.Poz(_ic(S.Dogal(), u0w.alt, [x.alt for x in govdeler]))
        if isinstance(u0w, S.NegArd) and all(isinstance(x, S.NegArd)
                                             for x in govdeler):
            return S.NegArd(_ic(S.Dogal(), u0w.alt, [x.alt for x in govdeler]))
        return S.Komp(ad, cizgi, dallar, u0)

    # ---- S¹ : hcomp KANONİK bir değerdir ----
    if isinstance(A, S.Cember):
        if not dallar:
            return whnf(u0, baglam)
        return S.HKomp(S.Cember(), ad, dallar, u0)

    # ---- U : Glue ile ----
    if isinstance(A, S.Evren):
        from .denklik import cizgi_denkligi
        taban = u0  # comp'un tabanı, kendisi bir tip
        yeni_dallar = []
        for (y, g) in dallar:
            T1 = ara_ikame(g, {ad: BIR})
            # g : ad ↦ U çizgisi; g(0) = u0 (yüz üzerinde).
            # Denklik T1 ≃ taban, çizgiyi TERSİNE kat ederek elde edilir.
            k = taze("k")
            ters = ara_ikame(g, {ad: Aralik.degisken(k).degil()})
            yeni_dallar.append((y, T1, cizgi_denkligi(k, ters)))
        return yapistir(taban, yeni_dallar)

    # ---- Glue ----
    if isinstance(A, S.Yapistir):
        from .denklik import komp_yapistir
        return komp_yapistir(ad, A, dallar, u0, baglam)

    # ---- takılı ----
    return S.Komp(ad, cizgi, dallar, u0)


# =====================================================================
#  Zayıf-baş normal form
# =====================================================================
def whnf(t: Terim, baglam: Optional[Baglam] = None) -> Terim:
    anahtar = (id(baglam), t)
    onb = _whnf_onb.get(anahtar)
    if onb is not None:
        return onb
    sonuc = _whnf_hesapla(t, baglam)
    if len(_whnf_onb) < _ONBELLEK_SINIRI:
        _capala(baglam)
        _whnf_onb[anahtar] = sonuc
    return sonuc


def _whnf_hesapla(t: Terim, baglam: Optional[Baglam] = None) -> Terim:
    while True:
        if isinstance(t, S.Uygula):
            f = whnf(t.fonk, baglam)
            if isinstance(f, S.Lam):
                t = ikame(f.govde, {f.ad: t.arg})
                continue
            return S.Uygula(f, t.arg)
        if isinstance(t, S.Birinci):
            c = whnf(t.cift, baglam)
            if isinstance(c, S.Cift):
                t = c.bir
                continue
            return S.Birinci(c)
        if isinstance(t, S.Ikinci):
            c = whnf(t.cift, baglam)
            if isinstance(c, S.Cift):
                t = c.iki
                continue
            return S.Ikinci(c)
        if isinstance(t, S.YolUygula):
            p = whnf(t.yol, baglam)
            if isinstance(p, S.YolLam):
                t = ara_ikame(p.govde, {p.ad: t.r})
                continue
            # neutral yolun uçta uygulanması: tipinden uç okunur
            if (t.r.sifir_mi() or t.r.bir_mi()) and baglam is not None:
                tip = sentez(p, baglam)
                if tip is not None:
                    tip = whnf(tip, baglam)
                    if isinstance(tip, S.YolP):
                        t = tip.sol if t.r.sifir_mi() else tip.sag
                        continue
            return S.YolUygula(p, t.r)
        if isinstance(t, S.Dongu):
            if t.r.sifir_mi() or t.r.bir_mi():
                return S.Taban()
            return t
        if isinstance(t, S.DogalInd):
            s = whnf(t.sayi, baglam)
            if isinstance(s, (S.Sfr, S.Ard)):
                t = dogal_ind(t.ad, t.hedef, t.sfr_dali, t.n_ad, t.rec_ad,
                              t.ard_dali, s)
                continue
            return S.DogalInd(t.ad, t.hedef, t.sfr_dali, t.n_ad, t.rec_ad,
                              t.ard_dali, s)
        if isinstance(t, S.TamsayiInd):
            s = whnf(t.sayi, baglam)
            if isinstance(s, (S.Poz, S.NegArd)):
                t = tamsayi_ind(t.ad, t.hedef, t.poz_ad, t.poz_dali,
                                t.neg_ad, t.neg_dali, s)
                continue
            return S.TamsayiInd(t.ad, t.hedef, t.poz_ad, t.poz_dali,
                                t.neg_ad, t.neg_dali, s)
        if isinstance(t, S.CemberInd):
            n = whnf(t.nokta, baglam)
            if isinstance(n, (S.Taban, S.Dongu, S.HKomp)):
                yeni = cember_ind(t.ad, t.hedef, t.taban_dali, t.i_ad,
                                  t.dongu_dali, n)
                if yeni != t:
                    t = yeni
                    continue
            return S.CemberInd(t.ad, t.hedef, t.taban_dali, t.i_ad,
                               t.dongu_dali, n)
        if isinstance(t, S.Komp):
            yeni = _komp_ac(t.ad, t.cizgi, t.dallar, t.u0, baglam)
            if yeni == t:
                return t
            t = yeni
            continue
        if isinstance(t, S.HKomp):
            yeni = _komp_ac(t.ad, t.tip, t.dallar, t.u0, baglam)
            if yeni == t:
                return t
            t = yeni
            continue
        if isinstance(t, S.Transp):
            t = transp(t.ad, t.cizgi, t.kof, t.u0)
            continue
        if isinstance(t, S.Coz):
            g = whnf(t.govde, baglam)
            yeni = coz(t.taban, t.dallar, g)
            if yeni == t or yeni == S.Coz(t.taban, t.dallar, g):
                return S.Coz(t.taban, t.dallar, g)
            t = yeni
            continue
        if isinstance(t, S.Yapistir):
            yeni = yapistir(t.taban, t.dallar)
            if yeni == t:
                return t
            t = yeni
            continue
        if isinstance(t, S.YapistirTerim):
            yeni = yapistir_terim(t.dallar, t.taban_terim)
            if yeni == t:
                return t
            t = yeni
            continue
        return t


# =====================================================================
#  Hafif tip sentezi (yalnız takılı terimlerin ucunu açmak için)
# =====================================================================
def sentez(t: Terim, baglam: Baglam) -> Optional[Terim]:
    """Neutral bir terimin tipini çıkarmaya çalışır; başaramazsa None."""
    if isinstance(t, S.Deg):
        return baglam.get(t.ad)
    if isinstance(t, S.Uygula):
        ft = sentez(t.fonk, baglam)
        if ft is None:
            return None
        ft = whnf(ft, baglam)
        if isinstance(ft, S.Pi):
            return ikame(ft.hedef, {ft.ad: t.arg})
        return None
    if isinstance(t, S.Birinci):
        ct = sentez(t.cift, baglam)
        if ct is None:
            return None
        ct = whnf(ct, baglam)
        return ct.alan if isinstance(ct, S.Sigma) else None
    if isinstance(t, S.Ikinci):
        ct = sentez(t.cift, baglam)
        if ct is None:
            return None
        ct = whnf(ct, baglam)
        if isinstance(ct, S.Sigma):
            return ikame(ct.hedef, {ct.ad: birinci(t.cift)})
        return None
    if isinstance(t, S.YolUygula):
        pt = sentez(t.yol, baglam)
        if pt is None:
            return None
        pt = whnf(pt, baglam)
        if isinstance(pt, S.YolP):
            return ara_ikame(pt.cizgi, {pt.ad: t.r})
        return None
    # eliminatörler ve Kan işlemleri: tipleri terimden okunur
    if isinstance(t, S.DogalInd):
        return ikame(t.hedef, {t.ad: t.sayi})
    if isinstance(t, S.TamsayiInd):
        return ikame(t.hedef, {t.ad: t.sayi})
    if isinstance(t, S.CemberInd):
        return ikame(t.hedef, {t.ad: t.nokta})
    if isinstance(t, (S.Komp, S.Transp)):
        return ara_ikame(t.cizgi, {t.ad: BIR})
    if isinstance(t, S.HKomp):
        return t.tip
    if isinstance(t, S.Coz):
        return t.taban
    if isinstance(t, S.YapistirTerim):
        return None
    return None


# =====================================================================
#  Normal form ve tanımsal eşitlik
# =====================================================================
def nf(t: Terim, baglam: Optional[Baglam] = None) -> Terim:
    """Tam normal form (bağlayıcıların altına da iner)."""
    anahtar = (id(baglam), t)
    onb = _nf_onb.get(anahtar)
    if onb is not None:
        return onb
    sonuc = _nf_hesapla(t, baglam)
    if len(_nf_onb) < _ONBELLEK_SINIRI:
        _capala(baglam)
        _nf_onb[anahtar] = sonuc
    return sonuc


def _nf_hesapla(t: Terim, baglam: Optional[Baglam] = None) -> Terim:
    t = whnf(t, baglam)
    f = lambda x: nf(x, baglam)
    if isinstance(t, (S.Deg, S.Evren, S.Dogal, S.Tamsayi, S.Cember,
                      S.Taban, S.Sfr)):
        return t
    if isinstance(t, S.Dongu):
        return t
    if isinstance(t, S.Pi):
        return S.Pi(t.ad, f(t.alan), f(t.hedef))
    if isinstance(t, S.Sigma):
        return S.Sigma(t.ad, f(t.alan), f(t.hedef))
    if isinstance(t, S.Lam):
        return S.Lam(t.ad, f(t.govde))
    if isinstance(t, S.Uygula):
        return S.Uygula(f(t.fonk), f(t.arg))
    if isinstance(t, S.Cift):
        return S.Cift(f(t.bir), f(t.iki))
    if isinstance(t, S.Birinci):
        return S.Birinci(f(t.cift))
    if isinstance(t, S.Ikinci):
        return S.Ikinci(f(t.cift))
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
        return S.YolUygula(f(t.yol), t.r)
    if isinstance(t, S.Komp):
        return S.Komp(t.ad, f(t.cizgi), [(y, f(g)) for (y, g) in t.dallar],
                      f(t.u0))
    if isinstance(t, S.HKomp):
        return S.HKomp(f(t.tip), t.ad, [(y, f(g)) for (y, g) in t.dallar],
                       f(t.u0))
    if isinstance(t, S.Transp):
        return S.Transp(t.ad, f(t.cizgi), t.kof, f(t.u0))
    if isinstance(t, S.Yapistir):
        return S.Yapistir(f(t.taban), [(y, f(T), f(e)) for (y, T, e) in t.dallar])
    if isinstance(t, S.YapistirTerim):
        return S.YapistirTerim([(y, f(g)) for (y, g) in t.dallar],
                               f(t.taban_terim))
    if isinstance(t, S.Coz):
        return S.Coz(f(t.taban), [(y, f(T), f(e)) for (y, T, e) in t.dallar],
                     f(t.govde))
    if isinstance(t, S.DogalInd):
        return S.DogalInd(t.ad, f(t.hedef), f(t.sfr_dali), t.n_ad, t.rec_ad,
                          f(t.ard_dali), f(t.sayi))
    if isinstance(t, S.TamsayiInd):
        return S.TamsayiInd(t.ad, f(t.hedef), t.poz_ad, f(t.poz_dali),
                            t.neg_ad, f(t.neg_dali), f(t.sayi))
    if isinstance(t, S.CemberInd):
        return S.CemberInd(t.ad, f(t.hedef), f(t.taban_dali), t.i_ad,
                           f(t.dongu_dali), f(t.nokta))
    return t


def _kanonik(t: Terim, terim_map: Dict[str, str], ara_map: Dict[str, str],
             derinlik: int = 0) -> Terim:
    """Bağlı isimleri derinliğe göre yeniden adlandırıp alfa-kanonik yapar."""
    k = lambda x, d=None: _kanonik(x, terim_map, ara_map,
                                   derinlik if d is None else d)

    def terim_bagla(ad, govde, d):
        yeni = "#%d" % d
        m2 = dict(terim_map)
        m2[ad] = yeni
        return yeni, _kanonik(govde, m2, ara_map, d + 1)

    def ara_bagla(ad, govdeler, d):
        yeni = "%%%d" % d
        m2 = dict(ara_map)
        m2[ad] = yeni
        return yeni, [_kanonik(g, terim_map, m2, d + 1) for g in govdeler]

    def ara_don(r: Aralik) -> Aralik:
        return r.yerine_koy({eski: Aralik.degisken(yeni)
                             for eski, yeni in ara_map.items()})

    def yuz_don(y):
        return frozenset((ara_map.get(ad, ad), d) for (ad, d) in y)

    if isinstance(t, S.Deg):
        return S.Deg(terim_map.get(t.ad, t.ad))
    if isinstance(t, (S.Evren, S.Dogal, S.Tamsayi, S.Cember, S.Taban, S.Sfr)):
        return t
    if isinstance(t, S.Dongu):
        return S.Dongu(ara_don(t.r))
    if isinstance(t, S.Pi):
        ad, govde = terim_bagla(t.ad, t.hedef, derinlik)
        return S.Pi(ad, k(t.alan), govde)
    if isinstance(t, S.Sigma):
        ad, govde = terim_bagla(t.ad, t.hedef, derinlik)
        return S.Sigma(ad, k(t.alan), govde)
    if isinstance(t, S.Lam):
        ad, govde = terim_bagla(t.ad, t.govde, derinlik)
        return S.Lam(ad, govde)
    if isinstance(t, S.Uygula):
        return S.Uygula(k(t.fonk), k(t.arg))
    if isinstance(t, S.Cift):
        return S.Cift(k(t.bir), k(t.iki))
    if isinstance(t, S.Birinci):
        return S.Birinci(k(t.cift))
    if isinstance(t, S.Ikinci):
        return S.Ikinci(k(t.cift))
    if isinstance(t, S.Ard):
        return S.Ard(k(t.alt))
    if isinstance(t, S.Poz):
        return S.Poz(k(t.alt))
    if isinstance(t, S.NegArd):
        return S.NegArd(k(t.alt))
    if isinstance(t, S.YolP):
        ad, (cizgi,) = ara_bagla(t.ad, [t.cizgi], derinlik)
        return S.YolP(ad, cizgi, k(t.sol), k(t.sag))
    if isinstance(t, S.YolLam):
        ad, (govde,) = ara_bagla(t.ad, [t.govde], derinlik)
        return S.YolLam(ad, govde)
    if isinstance(t, S.YolUygula):
        return S.YolUygula(k(t.yol), ara_don(t.r))
    if isinstance(t, S.Transp):
        ad, (cizgi,) = ara_bagla(t.ad, [t.cizgi], derinlik)
        kof = Kofibrasyon([yuz_don(y) for y in t.kof.yuzler])
        return S.Transp(ad, cizgi, kof, k(t.u0))
    if isinstance(t, S.Komp):
        govdeler = [t.cizgi] + [g for (_, g) in t.dallar]
        ad, yeni = ara_bagla(t.ad, govdeler, derinlik)
        dallar = [(yuz_don(y), yeni[n + 1])
                  for n, (y, _) in enumerate(t.dallar)]
        return S.Komp(ad, yeni[0], dallar, k(t.u0))
    if isinstance(t, S.HKomp):
        govdeler = [g for (_, g) in t.dallar]
        ad, yeni = ara_bagla(t.ad, govdeler, derinlik)
        dallar = [(yuz_don(y), yeni[n]) for n, (y, _) in enumerate(t.dallar)]
        return S.HKomp(k(t.tip), ad, dallar, k(t.u0))
    if isinstance(t, S.Yapistir):
        return S.Yapistir(k(t.taban),
                          [(yuz_don(y), k(T), k(e)) for (y, T, e) in t.dallar])
    if isinstance(t, S.YapistirTerim):
        return S.YapistirTerim([(yuz_don(y), k(g)) for (y, g) in t.dallar],
                               k(t.taban_terim))
    if isinstance(t, S.Coz):
        return S.Coz(k(t.taban),
                     [(yuz_don(y), k(T), k(e)) for (y, T, e) in t.dallar],
                     k(t.govde))
    if isinstance(t, S.DogalInd):
        ad, hedef = terim_bagla(t.ad, t.hedef, derinlik)
        n2 = "#%d" % (derinlik + 1)
        r2 = "#%d" % (derinlik + 2)
        m2 = dict(terim_map)
        m2[t.n_ad] = n2
        m2[t.rec_ad] = r2
        ard = _kanonik(t.ard_dali, m2, ara_map, derinlik + 3)
        return S.DogalInd(ad, hedef, k(t.sfr_dali), n2, r2, ard, k(t.sayi))
    if isinstance(t, S.TamsayiInd):
        ad, hedef = terim_bagla(t.ad, t.hedef, derinlik)
        p2 = "#%d" % (derinlik + 1)
        n2 = "#%d" % (derinlik + 2)
        mp = dict(terim_map); mp[t.poz_ad] = p2
        mn = dict(terim_map); mn[t.neg_ad] = n2
        return S.TamsayiInd(ad, hedef, p2,
                            _kanonik(t.poz_dali, mp, ara_map, derinlik + 3),
                            n2,
                            _kanonik(t.neg_dali, mn, ara_map, derinlik + 3),
                            k(t.sayi))
    if isinstance(t, S.CemberInd):
        ad, hedef = terim_bagla(t.ad, t.hedef, derinlik)
        i2, (dongu,) = ara_bagla(t.i_ad, [t.dongu_dali], derinlik + 1)
        return S.CemberInd(ad, hedef, k(t.taban_dali), i2, dongu, k(t.nokta))
    return t


def kanonik(t: Terim, baglam: Optional[Baglam] = None) -> Terim:
    return _kanonik(nf(t, baglam), {}, {}, 0)


def esdeger_mi(a: Terim, b: Terim, baglam: Optional[Baglam] = None) -> bool:
    """Tanımsal eşitlik: normal formların alfa-kanonik kıyası (+ eta)."""
    if a is b:
        return True
    ka, kb = kanonik(a, baglam), kanonik(b, baglam)
    if ka == kb:
        return True
    return _eta_esit(ka, kb, baglam, 0)


def _eta_esit(a: Terim, b: Terim, baglam, derinlik: int) -> bool:
    """Şekle dayalı eta genişletmesiyle kıyas (Π, Σ, Yol)."""
    if a == b:
        return True
    if isinstance(a, S.Lam) != isinstance(b, S.Lam):
        lam, obur = (a, b) if isinstance(a, S.Lam) else (b, a)
        v = "#eta%d" % derinlik
        return _eta_esit(kanonik(lam.govde if lam.ad == v else
                                 ikame(lam.govde, {lam.ad: S.Deg(v)}), baglam),
                         kanonik(S.Uygula(obur, S.Deg(v)), baglam),
                         baglam, derinlik + 1)
    if isinstance(a, S.YolLam) != isinstance(b, S.YolLam):
        pl, obur = (a, b) if isinstance(a, S.YolLam) else (b, a)
        v = "%%eta%d" % derinlik
        r = Aralik.degisken(v)
        return _eta_esit(kanonik(ara_ikame(pl.govde, {pl.ad: r}), baglam),
                         kanonik(S.YolUygula(obur, r), baglam),
                         baglam, derinlik + 1)
    if isinstance(a, S.Cift) != isinstance(b, S.Cift):
        ct, obur = (a, b) if isinstance(a, S.Cift) else (b, a)
        return (_eta_esit(kanonik(ct.bir, baglam),
                          kanonik(S.Birinci(obur), baglam), baglam, derinlik)
                and _eta_esit(kanonik(ct.iki, baglam),
                              kanonik(S.Ikinci(obur), baglam), baglam, derinlik))
    if type(a) is not type(b):
        return False
    # yapısal, alt terimlerde eta ile
    if isinstance(a, S.Lam):
        return _eta_esit(a.govde, ikame(b.govde, {b.ad: S.Deg(a.ad)}),
                         baglam, derinlik + 1)
    if isinstance(a, S.YolLam):
        return _eta_esit(a.govde,
                         ara_ikame(b.govde, {b.ad: Aralik.degisken(a.ad)}),
                         baglam, derinlik + 1)
    if isinstance(a, S.Cift):
        return (_eta_esit(a.bir, b.bir, baglam, derinlik)
                and _eta_esit(a.iki, b.iki, baglam, derinlik))
    if isinstance(a, S.Uygula):
        return (_eta_esit(a.fonk, b.fonk, baglam, derinlik)
                and _eta_esit(a.arg, b.arg, baglam, derinlik))
    return False
