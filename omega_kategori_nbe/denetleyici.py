"""
İki yönlü tip denetleyici -- NbE sürümü.

Terim sürümüyle aynı kurallar; farkı, tiplerin TERİM değil DEĞER olarak
taşınmasıdır. Bağlam hem tip değerlerini hem de değişkenlerin nötr
değerlerini tutar; bir yüze kısıtlama, bağlamın tamamına ``act``
uygulamaktır.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Set, Tuple

from .aralik import (BIR, DOGRU, SIFIR, YANLIS, Aralik, Kofibrasyon,
                     yuzu_atamaya_cevir)
from . import cekirdek as C
from . import sozdizim as S
from . import terimler as TR
from .cekirdek import (ASabit, ASoz, Deger, NDeg, Ortam, degerlendir,
                       geri_oku, notr)
from .sozdizim import Terim, Yuz


class DenetimHatasi(Exception):
    pass


class Baglam:
    __slots__ = ("tipler", "ortam", "aralik")

    def __init__(self, tipler=None, ortam=None, aralik=None) -> None:
        self.tipler: Dict[str, Deger] = dict(tipler or {})
        self.ortam: Ortam = ortam or C.BOS
        self.aralik: Set[str] = set(aralik or ())

    @staticmethod
    def terimlerden(baglam: Dict[str, Terim]) -> "Baglam":
        g = Baglam()
        for ad, tip in baglam.items():
            g = g.genislet(ad, g.d(tip))
        return g

    def genislet(self, ad: str, tipd: Deger) -> "Baglam":
        y = Baglam(self.tipler, self.ortam, self.aralik)
        y.tipler[ad] = tipd
        y.ortam = self.ortam.genislet(ad, notr(NDeg(ad, tipd), tipd))
        return y

    def ara_ekle(self, ad: str) -> "Baglam":
        y = Baglam(self.tipler, self.ortam.ara_genislet(ad,
                                                        Aralik.degisken(ad)),
                   self.aralik)
        y.aralik.add(ad)
        return y

    def kisitla(self, yuz: Yuz) -> "Baglam":
        if not yuz:
            return self
        s = yuzu_atamaya_cevir(yuz)
        return Baglam({a: t.act(s) for a, t in self.tipler.items()},
                      self.ortam.act(s),
                      self.aralik - {a for (a, _) in yuz})

    def d(self, t: Terim) -> Deger:
        return degerlendir(t, self.ortam)

    def esit_mi(self, a: Deger, b: Deger) -> bool:
        return C.deger_esit_mi(a, b)


def _bagdasir(y1: Yuz, y2: Yuz) -> Optional[Yuz]:
    gor: Dict[str, bool] = {}
    for (ad, d) in set(y1) | set(y2):
        if ad in gor and gor[ad] != d:
            return None
        gor[ad] = d
    return frozenset(set(y1) | set(y2))


def _sabit_cizgi_mi(hat, ad_ipucu: str = "i") -> bool:
    """Çizgi NORMAL FORMDA sabit mi? (uçların eşitliğine BAKILMAZ)"""
    k = C.taze("sbt")
    govde = geri_oku(hat.uygula(Aralik.degisken(k)), 0)
    return k not in TR.ara_serbest(govde)


# =====================================================================
#  Tip teşkili
# =====================================================================
def denetle_tip(t: Terim, g: Baglam) -> int:
    T = sentezle(t, g)
    if isinstance(T, C.DEvren):
        return T.seviye
    raise DenetimHatasi("tip bekleniyordu: %s : %s" % (t, geri_oku(T)))


# =====================================================================
#  Sistem denetimi
# =====================================================================
def denetle_sistem(ad: str, cizgi: Terim, dallar, u0: Terim,
                   g: Baglam) -> None:
    gi = g.ara_ekle(ad)
    for (y, govde) in dallar:
        gy = gi.kisitla(y)
        s = yuzu_atamaya_cevir(y)
        denetle(TR.ara_ikame(govde, s), gy.d(TR.ara_ikame(cizgi, s)), gy)
    for m in range(len(dallar)):
        for n in range(m + 1, len(dallar)):
            ortak = _bagdasir(dallar[m][0], dallar[n][0])
            if ortak is None:
                continue
            s = yuzu_atamaya_cevir(ortak)
            go = gi.kisitla(ortak)
            sol = go.d(TR.ara_ikame(dallar[m][1], s))
            sag = go.d(TR.ara_ikame(dallar[n][1], s))
            if not go.esit_mi(sol, sag):
                raise DenetimHatasi("sistem çakışan yüzde uyuşmuyor (%s)"
                                    % sorted(ortak))
    for (y, govde) in dallar:
        s = dict(yuzu_atamaya_cevir(y))
        s[ad] = SIFIR
        gy = g.kisitla(y)
        sol = gy.d(TR.ara_ikame(govde, s))
        sag = gy.d(TR.ara_ikame(u0, yuzu_atamaya_cevir(y)))
        if not gy.esit_mi(sol, sag):
            raise DenetimHatasi("sistem tabanla uyuşmuyor (yüz %s)" % sorted(y))


# =====================================================================
#  Sentez
# =====================================================================
def sentezle(t: Terim, g: Baglam) -> Deger:
    if isinstance(t, S.Deg):
        if t.ad not in g.tipler:
            raise DenetimHatasi("kapsamda olmayan değişken: %s" % t.ad)
        return g.tipler[t.ad]

    if isinstance(t, S.Evren):
        return C.DEvren(t.seviye + 1)

    if isinstance(t, (S.Pi, S.Sigma)):
        sa = denetle_tip(t.alan, g)
        sh = denetle_tip(t.hedef, g.genislet(t.ad, g.d(t.alan)))
        return C.DEvren(max(sa, sh))

    if isinstance(t, S.Uygula):
        ft = sentezle(t.fonk, g)
        if not isinstance(ft, C.DPi):
            raise DenetimHatasi("fonksiyon bekleniyordu: %s" % (t.fonk,))
        denetle(t.arg, ft.alan, g)
        return ft.kap.uygula(g.d(t.arg))

    if isinstance(t, S.Birinci):
        ct = sentezle(t.cift, g)
        if not isinstance(ct, C.DSigma):
            raise DenetimHatasi("çift bekleniyordu")
        return ct.alan

    if isinstance(t, S.Ikinci):
        ct = sentezle(t.cift, g)
        if not isinstance(ct, C.DSigma):
            raise DenetimHatasi("çift bekleniyordu")
        return ct.kap.uygula(C.bir(g.d(t.cift)))

    if isinstance(t, S.YolP):
        gi = g.ara_ekle(t.ad)
        s = denetle_tip(t.cizgi, gi)
        hat = ASoz(t.ad, t.cizgi, g.ortam)
        denetle(t.sol, hat.uygula(SIFIR), g)
        denetle(t.sag, hat.uygula(BIR), g)
        return C.DEvren(s)

    if isinstance(t, S.YolUygula):
        _ara_denetle(t.r, g)
        if isinstance(t.yol, S.YolLam):
            return sentezle(TR.ara_ikame(t.yol.govde, {t.yol.ad: t.r}), g)
        pt = sentezle(t.yol, g)
        if not isinstance(pt, C.DYolP):
            raise DenetimHatasi("yol bekleniyordu: %s" % (t.yol,))
        return pt.cizgi.uygula(t.r)

    if isinstance(t, S.Transp):
        gi = g.ara_ekle(t.ad)
        denetle_tip(t.cizgi, gi)
        hat = ASoz(t.ad, t.cizgi, g.ortam)
        for y in t.kof.yuzler:
            s = yuzu_atamaya_cevir(y)
            if not _sabit_cizgi_mi(hat.act(s)):
                raise DenetimHatasi("transp: çizgi %s yüzünde sabit değil"
                                    % sorted(y))
        denetle(t.u0, hat.uygula(SIFIR), g)
        return hat.uygula(BIR)

    if isinstance(t, S.Komp):
        gi = g.ara_ekle(t.ad)
        denetle_tip(t.cizgi, gi)
        hat = ASoz(t.ad, t.cizgi, g.ortam)
        denetle(t.u0, hat.uygula(SIFIR), g)
        denetle_sistem(t.ad, t.cizgi, t.dallar, t.u0, g)
        return hat.uygula(BIR)

    if isinstance(t, S.HKomp):
        denetle_tip(t.tip, g)
        tv = g.d(t.tip)
        denetle(t.u0, tv, g)
        denetle_sistem(t.ad, t.tip, t.dallar, t.u0, g)
        return tv

    if isinstance(t, S.Yapistir):
        s = denetle_tip(t.taban, g)
        from .kutuphane import denklik_tipi
        for (y, T, e) in t.dallar:
            gy = g.kisitla(y)
            sg = yuzu_atamaya_cevir(y)
            Ty = TR.ara_ikame(T, sg)
            denetle_tip(Ty, gy)
            denetle(TR.ara_ikame(e, sg),
                    gy.d(denklik_tipi(Ty, TR.ara_ikame(t.taban, sg))), gy)
        return C.DEvren(s)

    if isinstance(t, S.Coz):
        denetle(t.govde, g.d(S.Yapistir(t.taban, t.dallar)), g)
        return g.d(t.taban)

    if isinstance(t, S.Dogal):
        return C.DEvren(0)
    if isinstance(t, S.Sfr):
        return C.DDogal()
    if isinstance(t, S.Ard):
        denetle(t.alt, C.DDogal(), g)
        return C.DDogal()
    if isinstance(t, S.Tamsayi):
        return C.DEvren(0)
    if isinstance(t, (S.Poz, S.NegArd)):
        denetle(t.alt, C.DDogal(), g)
        return C.DTamsayi()
    if isinstance(t, S.Cember):
        return C.DEvren(0)
    if isinstance(t, S.Taban):
        return C.DCember()
    if isinstance(t, S.Dongu):
        _ara_denetle(t.r, g)
        return C.DCember()

    if isinstance(t, S.DogalInd):
        motif = C.KSoz(t.ad, t.hedef, g.ortam)
        denetle_tip(t.hedef, g.genislet(t.ad, C.DDogal()))
        denetle(t.sayi, C.DDogal(), g)
        denetle(t.sfr_dali, motif.uygula(C.DSfr()), g)
        gn = g.genislet(t.n_ad, C.DDogal())
        nv = gn.ortam.terimler[t.n_ad]
        gnr = gn.genislet(t.rec_ad, motif.uygula(nv))
        denetle(t.ard_dali, motif.uygula(C.DArd(nv)), gnr)
        return motif.uygula(g.d(t.sayi))

    if isinstance(t, S.TamsayiInd):
        motif = C.KSoz(t.ad, t.hedef, g.ortam)
        denetle_tip(t.hedef, g.genislet(t.ad, C.DTamsayi()))
        denetle(t.sayi, C.DTamsayi(), g)
        gp = g.genislet(t.poz_ad, C.DDogal())
        denetle(t.poz_dali, motif.uygula(C.DPoz(gp.ortam.terimler[t.poz_ad])), gp)
        gn = g.genislet(t.neg_ad, C.DDogal())
        denetle(t.neg_dali,
                motif.uygula(C.DNegArd(gn.ortam.terimler[t.neg_ad])), gn)
        return motif.uygula(g.d(t.sayi))

    if isinstance(t, S.CemberInd):
        motif = C.KSoz(t.ad, t.hedef, g.ortam)
        denetle_tip(t.hedef, g.genislet(t.ad, C.DCember()))
        denetle(t.nokta, C.DCember(), g)
        denetle(t.taban_dali, motif.uygula(C.DTaban()), g)
        # dongu_dali'nin UÇLARI taban_dalının DEĞERİdir, tipi değil
        tbd = g.d(t.taban_dali)
        cizgi = TR.ikame(t.hedef,
                         {t.ad: S.Dongu(Aralik.degisken(t.i_ad))})
        denetle(S.YolLam(t.i_ad, t.dongu_dali),
                C.DYolP(ASoz(t.i_ad, cizgi, g.ortam), tbd, tbd), g)
        return motif.uygula(g.d(t.nokta))

    raise DenetimHatasi("sentezlenemeyen terim: %r" % (t,))


def _ara_denetle(r: Aralik, g: Baglam) -> None:
    eksik = r.degiskenler() - g.aralik
    if eksik:
        raise DenetimHatasi("kapsamda olmayan aralık değişkeni: %s"
                            % ", ".join(sorted(eksik)))


# =====================================================================
#  Denetim
# =====================================================================
def denetle(t: Terim, tip: Deger, g: Baglam) -> None:
    if isinstance(t, S.Lam):
        if not isinstance(tip, C.DPi):
            raise DenetimHatasi("λ için Π bekleniyordu: %s" % geri_oku(tip))
        g2 = g.genislet(t.ad, tip.alan)
        denetle(t.govde, tip.kap.uygula(g2.ortam.terimler[t.ad]), g2)
        return

    if isinstance(t, S.Cift):
        if not isinstance(tip, C.DSigma):
            raise DenetimHatasi("çift için Σ bekleniyordu: %s" % geri_oku(tip))
        denetle(t.bir, tip.alan, g)
        denetle(t.iki, tip.kap.uygula(g.d(t.bir)), g)
        return

    if isinstance(t, S.YolLam):
        if not isinstance(tip, C.DYolP):
            raise DenetimHatasi("<i> için PathP bekleniyordu: %s"
                                % geri_oku(tip))
        gi = g.ara_ekle(t.ad)
        denetle(t.govde, tip.cizgi.uygula(Aralik.degisken(t.ad)), gi)
        sol = g.d(TR.ara_ikame(t.govde, {t.ad: SIFIR}))
        sag = g.d(TR.ara_ikame(t.govde, {t.ad: BIR}))
        if not g.esit_mi(sol, tip.sol):
            raise DenetimHatasi("yolun sol ucu uymuyor: %s ≠ %s"
                                % (geri_oku(sol), geri_oku(tip.sol)))
        if not g.esit_mi(sag, tip.sag):
            raise DenetimHatasi("yolun sağ ucu uymuyor: %s ≠ %s"
                                % (geri_oku(sag), geri_oku(tip.sag)))
        return

    if isinstance(t, S.YapistirTerim):
        if not isinstance(tip, C.DYapistir):
            raise DenetimHatasi("glue için Glue tipi bekleniyordu")
        denetle(t.taban_terim, tip.taban, g)
        esle = {y: (T, e) for (y, T, e) in tip.dallar}
        for (y, govde) in t.dallar:
            if y not in esle:
                raise DenetimHatasi("glue: Glue tipinde olmayan yüz %s"
                                    % sorted(y))
            T, e = esle[y]
            gy = g.kisitla(y)
            sg = yuzu_atamaya_cevir(y)
            gv = gy.d(TR.ara_ikame(govde, sg))
            denetle(TR.ara_ikame(govde, sg), T.act(sg), gy)
            sol = C.uygula(C.bir(e.act(sg)), gv)
            sag = gy.d(TR.ara_ikame(t.taban_terim, sg))
            if not gy.esit_mi(sol, sag):
                raise DenetimHatasi("glue: %s yüzünde e.1 t ≠ a" % sorted(y))
        return

    bulunan = sentezle(t, g)
    if not g.esit_mi(bulunan, tip):
        raise DenetimHatasi("tip uyuşmazlığı:\n  terim   : %s\n  beklenen: %s\n"
                            "  bulunan : %s"
                            % (t, geri_oku(tip), geri_oku(bulunan)))
