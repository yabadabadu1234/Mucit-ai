"""
İki yönlü (bidirectional) tip denetleyici.

``denetle(t, T)``  : ``t``nin ``T`` tipinde olduğunu doğrular.
``sentezle(t)``    : ``t``nin tipini çıkarır.

Sistemler (kofibrasyon üzerinde tanımlı kısmî elemanlar) üç şartla denetlenir:
  1. her dal, kendi yüzüne KISITLANMIŞ bağlamda doğru tipte olmalı,
  2. çakışan yüzlerde dallar birbiriyle UYUŞMALI,
  3. her dal, ``i=0``da tabanla UYUŞMALI.
Bu üçü sağlanmadan Kan işlemi teşkil edilemez; kübik tutarlılığın bel kemiği
budur.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Set, Tuple

from .aralik import (BIR, DOGRU, SIFIR, YANLIS, Aralik, Kofibrasyon,
                     yuzu_atamaya_cevir)
from . import cekirdek as K
from . import sozdizim as S
from .sozdizim import Terim, Yuz


class DenetimHatasi(Exception):
    pass


class Baglam:
    """Terim tipleri + kapsamdaki aralık değişkenleri."""

    __slots__ = ("tipler", "aralik")

    def __init__(self, tipler: Optional[Dict[str, Terim]] = None,
                 aralik: Optional[Set[str]] = None) -> None:
        self.tipler: Dict[str, Terim] = dict(tipler or {})
        self.aralik: Set[str] = set(aralik or ())

    def genislet(self, ad: str, tip: Terim) -> "Baglam":
        y = Baglam(self.tipler, self.aralik)
        y.tipler[ad] = tip
        return y

    def aralik_ekle(self, ad: str) -> "Baglam":
        y = Baglam(self.tipler, self.aralik)
        y.aralik.add(ad)
        return y

    def kisitla(self, yuz: Yuz) -> "Baglam":
        """Bir yüze kısıtla: kapsamdaki bütün tiplere ikame uygulanır."""
        if not yuz:
            return self
        sigma = yuzu_atamaya_cevir(yuz)
        y = Baglam({ad: K.ara_ikame(t, sigma) for ad, t in self.tipler.items()},
                   self.aralik - {ad for (ad, _) in yuz})
        return y

    def esit_mi(self, a: Terim, b: Terim) -> bool:
        return K.esdeger_mi(a, b, self.tipler)

    def wh(self, t: Terim) -> Terim:
        return K.whnf(t, self.tipler)


def _kof(yuzler: Sequence[Yuz]) -> Kofibrasyon:
    return Kofibrasyon(yuzler)


def _bagdasir_mi(y1: Yuz, y2: Yuz) -> Optional[Yuz]:
    birlesim = set(y1) | set(y2)
    gorulen: Dict[str, bool] = {}
    for (ad, d) in birlesim:
        if ad in gorulen and gorulen[ad] != d:
            return None
        gorulen[ad] = d
    return frozenset(birlesim)


# =====================================================================
#  Tip teşkili
# =====================================================================
def denetle_tip(t: Terim, g: Baglam) -> int:
    """``t``nin bir tip olduğunu doğrular ve tümel seviyesini döndürür."""
    T = sentezle(t, g)
    T = g.wh(T)
    if isinstance(T, S.Evren):
        return T.seviye
    raise DenetimHatasi("tip bekleniyordu, bulunan: %s : %s" % (t, T))


# =====================================================================
#  Sistem denetimi
# =====================================================================
def denetle_sistem(ad: str, cizgi: Terim, dallar: Sequence[Tuple[Yuz, Terim]],
                   u0: Terim, g: Baglam) -> None:
    gi = g.aralik_ekle(ad)
    # 1. her dal kendi yüzünde doğru tipte
    for (y, govde) in dallar:
        gy = gi.kisitla(y)
        sigma = yuzu_atamaya_cevir(y)
        denetle(K.ara_ikame(govde, sigma), K.ara_ikame(cizgi, sigma), gy)
    # 2. çakışan yüzlerde uyuşma
    for m in range(len(dallar)):
        for n in range(m + 1, len(dallar)):
            ortak = _bagdasir_mi(dallar[m][0], dallar[n][0])
            if ortak is None:
                continue
            sigma = yuzu_atamaya_cevir(ortak)
            go = gi.kisitla(ortak)
            sol = K.ara_ikame(dallar[m][1], sigma)
            sag = K.ara_ikame(dallar[n][1], sigma)
            if not go.esit_mi(sol, sag):
                raise DenetimHatasi(
                    "sistem çakışan yüzde uyuşmuyor: %s ile %s (yüz %s)"
                    % (sol, sag, sorted(ortak)))
    # 3. taban ile uyuşma (ad = 0)
    for (y, govde) in dallar:
        sigma = dict(yuzu_atamaya_cevir(y))
        sigma[ad] = SIFIR
        gy = g.kisitla(y)
        sol = K.ara_ikame(govde, sigma)
        sag = K.ara_ikame(u0, yuzu_atamaya_cevir(y))
        if not gy.esit_mi(sol, sag):
            raise DenetimHatasi(
                "sistem tabanla uyuşmuyor (yüz %s): %s ≠ %s"
                % (sorted(y), sol, sag))


# =====================================================================
#  Sentez
# =====================================================================
def sentezle(t: Terim, g: Baglam) -> Terim:
    if isinstance(t, S.Deg):
        if t.ad not in g.tipler:
            raise DenetimHatasi("kapsamda olmayan değişken: %s" % t.ad)
        return g.tipler[t.ad]

    if isinstance(t, S.Evren):
        return S.Evren(t.seviye + 1)

    if isinstance(t, (S.Pi, S.Sigma)):
        sa = denetle_tip(t.alan, g)
        sh = denetle_tip(t.hedef, g.genislet(t.ad, t.alan))
        return S.Evren(max(sa, sh))

    if isinstance(t, S.Uygula):
        ft = g.wh(sentezle(t.fonk, g))
        if not isinstance(ft, S.Pi):
            raise DenetimHatasi("fonksiyon bekleniyordu: %s : %s" % (t.fonk, ft))
        denetle(t.arg, ft.alan, g)
        return K.ikame(ft.hedef, {ft.ad: t.arg})

    if isinstance(t, S.Birinci):
        ct = g.wh(sentezle(t.cift, g))
        if not isinstance(ct, S.Sigma):
            raise DenetimHatasi("çift bekleniyordu: %s" % (ct,))
        return ct.alan

    if isinstance(t, S.Ikinci):
        ct = g.wh(sentezle(t.cift, g))
        if not isinstance(ct, S.Sigma):
            raise DenetimHatasi("çift bekleniyordu: %s" % (ct,))
        return K.ikame(ct.hedef, {ct.ad: K.birinci(t.cift)})

    if isinstance(t, S.YolP):
        gi = g.aralik_ekle(t.ad)
        s = denetle_tip(t.cizgi, gi)
        denetle(t.sol, K.ara_ikame(t.cizgi, {t.ad: SIFIR}), g)
        denetle(t.sag, K.ara_ikame(t.cizgi, {t.ad: BIR}), g)
        return S.Evren(s)

    if isinstance(t, S.YolUygula):
        _aralik_denetle(t.r, g)
        ic = g.wh(t.yol)
        if isinstance(ic, S.YolLam):
            # <i> gövde @ r : doğrudan indirgenip gövdenin tipi sentezlenir
            return sentezle(K.ara_ikame(ic.govde, {ic.ad: t.r}), g)
        pt = g.wh(sentezle(t.yol, g))
        if not isinstance(pt, S.YolP):
            raise DenetimHatasi("yol bekleniyordu: %s : %s" % (t.yol, pt))
        return K.ara_ikame(pt.cizgi, {pt.ad: t.r})

    if isinstance(t, S.Transp):
        gi = g.aralik_ekle(t.ad)
        denetle_tip(t.cizgi, gi)
        # kof üzerinde çizgi SABİT olmalı
        for y in t.kof.yuzler:
            sigma = yuzu_atamaya_cevir(y)
            kisitli = K.nf(K.ara_ikame(t.cizgi, sigma), gi.kisitla(y).tipler)
            if t.ad in K.ara_serbest(kisitli):
                raise DenetimHatasi(
                    "transp: çizgi %s yüzünde sabit değil" % sorted(y))
        denetle(t.u0, K.ara_ikame(t.cizgi, {t.ad: SIFIR}), g)
        return K.ara_ikame(t.cizgi, {t.ad: BIR})

    if isinstance(t, S.Komp):
        gi = g.aralik_ekle(t.ad)
        denetle_tip(t.cizgi, gi)
        denetle(t.u0, K.ara_ikame(t.cizgi, {t.ad: SIFIR}), g)
        denetle_sistem(t.ad, t.cizgi, t.dallar, t.u0, g)
        return K.ara_ikame(t.cizgi, {t.ad: BIR})

    if isinstance(t, S.HKomp):
        denetle_tip(t.tip, g)
        denetle(t.u0, t.tip, g)
        denetle_sistem(t.ad, t.tip, t.dallar, t.u0, g)
        return t.tip

    if isinstance(t, S.Yapistir):
        s = denetle_tip(t.taban, g)
        for (y, T, e) in t.dallar:
            gy = g.kisitla(y)
            sigma = yuzu_atamaya_cevir(y)
            Ty = K.ara_ikame(T, sigma)
            denetle_tip(Ty, gy)
            from .kutuphane import denklik_tipi
            denetle(K.ara_ikame(e, sigma),
                    denklik_tipi(Ty, K.ara_ikame(t.taban, sigma)), gy)
        return S.Evren(s)

    if isinstance(t, S.Coz):
        denetle(t.govde, K.yapistir(t.taban, t.dallar), g)
        return t.taban

    if isinstance(t, S.Dogal):
        return S.Evren(0)
    if isinstance(t, S.Sfr):
        return S.Dogal()
    if isinstance(t, S.Ard):
        denetle(t.alt, S.Dogal(), g)
        return S.Dogal()
    if isinstance(t, S.Tamsayi):
        return S.Evren(0)
    if isinstance(t, S.Poz):
        denetle(t.alt, S.Dogal(), g)
        return S.Tamsayi()
    if isinstance(t, S.NegArd):
        denetle(t.alt, S.Dogal(), g)
        return S.Tamsayi()
    if isinstance(t, S.Cember):
        return S.Evren(0)
    if isinstance(t, S.Taban):
        return S.Cember()
    if isinstance(t, S.Dongu):
        _aralik_denetle(t.r, g)
        return S.Cember()

    if isinstance(t, S.DogalInd):
        denetle_tip(t.hedef, g.genislet(t.ad, S.Dogal()))
        denetle(t.sayi, S.Dogal(), g)
        denetle(t.sfr_dali, K.ikame(t.hedef, {t.ad: S.Sfr()}), g)
        gn = g.genislet(t.n_ad, S.Dogal())
        gnr = gn.genislet(t.rec_ad, K.ikame(t.hedef, {t.ad: S.Deg(t.n_ad)}))
        denetle(t.ard_dali, K.ikame(t.hedef, {t.ad: S.Ard(S.Deg(t.n_ad))}), gnr)
        return K.ikame(t.hedef, {t.ad: t.sayi})

    if isinstance(t, S.TamsayiInd):
        denetle_tip(t.hedef, g.genislet(t.ad, S.Tamsayi()))
        denetle(t.sayi, S.Tamsayi(), g)
        gp = g.genislet(t.poz_ad, S.Dogal())
        denetle(t.poz_dali, K.ikame(t.hedef, {t.ad: S.Poz(S.Deg(t.poz_ad))}), gp)
        gn = g.genislet(t.neg_ad, S.Dogal())
        denetle(t.neg_dali,
                K.ikame(t.hedef, {t.ad: S.NegArd(S.Deg(t.neg_ad))}), gn)
        return K.ikame(t.hedef, {t.ad: t.sayi})

    if isinstance(t, S.CemberInd):
        denetle_tip(t.hedef, g.genislet(t.ad, S.Cember()))
        denetle(t.nokta, S.Cember(), g)
        denetle(t.taban_dali, K.ikame(t.hedef, {t.ad: S.Taban()}), g)
        # dongu_dali : PathP (λ i. hedef[dongu i]) taban_dali taban_dali
        cizgi = K.ikame(t.hedef, {t.ad: S.Dongu(Aralik.degisken(t.i_ad))})
        denetle(S.YolLam(t.i_ad, t.dongu_dali),
                S.YolP(t.i_ad, cizgi, t.taban_dali, t.taban_dali), g)
        return K.ikame(t.hedef, {t.ad: t.nokta})

    raise DenetimHatasi("sentezlenemeyen terim: %r" % (t,))


def _aralik_denetle(r: Aralik, g: Baglam) -> None:
    eksik = r.degiskenler() - g.aralik
    if eksik:
        raise DenetimHatasi("kapsamda olmayan aralık değişkeni: %s"
                            % ", ".join(sorted(eksik)))


# =====================================================================
#  Denetim
# =====================================================================
def denetle(t: Terim, tip: Terim, g: Baglam) -> None:
    T = g.wh(tip)

    if isinstance(t, S.Lam):
        if not isinstance(T, S.Pi):
            raise DenetimHatasi("λ için Π bekleniyordu, bulunan: %s" % (T,))
        govde = K.ikame(t.govde, {t.ad: S.Deg(t.ad)})
        denetle(govde, K.ikame(T.hedef, {T.ad: S.Deg(t.ad)}),
                g.genislet(t.ad, T.alan))
        return

    if isinstance(t, S.Cift):
        if not isinstance(T, S.Sigma):
            raise DenetimHatasi("çift için Σ bekleniyordu, bulunan: %s" % (T,))
        denetle(t.bir, T.alan, g)
        denetle(t.iki, K.ikame(T.hedef, {T.ad: t.bir}), g)
        return

    if isinstance(t, S.YolLam):
        if not isinstance(T, S.YolP):
            raise DenetimHatasi("<i> için PathP bekleniyordu: %s" % (T,))
        cizgi = K.ara_ikame(T.cizgi, {T.ad: Aralik.degisken(t.ad)})
        denetle(t.govde, cizgi, g.aralik_ekle(t.ad))
        sol = K.ara_ikame(t.govde, {t.ad: SIFIR})
        sag = K.ara_ikame(t.govde, {t.ad: BIR})
        if not g.esit_mi(sol, T.sol):
            raise DenetimHatasi("yolun sol ucu uymuyor: %s ≠ %s" % (sol, T.sol))
        if not g.esit_mi(sag, T.sag):
            raise DenetimHatasi("yolun sağ ucu uymuyor: %s ≠ %s" % (sag, T.sag))
        return

    if isinstance(t, S.YapistirTerim):
        if not isinstance(T, S.Yapistir):
            raise DenetimHatasi("glue için Glue tipi bekleniyordu: %s" % (T,))
        denetle(t.taban_terim, T.taban, g)
        eslesme = {y: (Tt, e) for (y, Tt, e) in T.dallar}
        for (y, govde) in t.dallar:
            if y not in eslesme:
                raise DenetimHatasi("glue: Glue tipinde olmayan yüz %s"
                                    % sorted(y))
            Tt, e = eslesme[y]
            gy = g.kisitla(y)
            sigma = yuzu_atamaya_cevir(y)
            denetle(K.ara_ikame(govde, sigma), K.ara_ikame(Tt, sigma), gy)
            sol = K.uygula(K.birinci(K.ara_ikame(e, sigma)),
                           K.ara_ikame(govde, sigma))
            sag = K.ara_ikame(t.taban_terim, sigma)
            if not gy.esit_mi(sol, sag):
                raise DenetimHatasi(
                    "glue: %s yüzünde e.1 t ≠ a  (%s ≠ %s)"
                    % (sorted(y), sol, sag))
        return

    # sentezle-ve-karşılaştır
    bulunan = sentezle(t, g)
    if not g.esit_mi(bulunan, tip):
        raise DenetimHatasi("tip uyuşmazlığı:\n  terim   : %s\n  beklenen: %s\n"
                            "  bulunan : %s" % (t, K.nf(tip, g.tipler),
                                                K.nf(bulunan, g.tipler)))


def tipini_ver(t: Terim, g: Optional[Baglam] = None) -> Terim:
    """Kolaylık: terimi denetleyip normalleştirilmiş tipini döndürür."""
    g = g or Baglam()
    return K.nf(sentezle(t, g), g.tipler)
