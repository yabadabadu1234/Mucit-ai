"""
NbE çekirdeği: değerler, kapanışlar ve Kan işlemleri.

Terim seviyesindeki sürümden farkı: **ikame terim ağacını kopyalamaz.**
Bir kapanış ``(terim, ortam)`` çiftidir; aralık ikamesi (``act``) yalnız
ORTAMA uygulanır, gövdeye dokunulmaz. Ortamlar küçük ve paylaşımlıdır;
terim ağaçları ise büyük ve paylaşımsızdı -- kazanç buradan gelir.

Kübik NbE'nin ince yeri şudur: değerlerin aralık ikamesi altında
davranışı. Yerli (native) Python kapanışları bunu bozar; bu yüzden BÜTÜN
kapanışlar ``act`` altında alanlarını dönüştürebilen VERİ KURUCULARIDIR
(``ATuretilmis`` / ``KTuretilmis``: etiket + alanlar + modül seviyesinde
bir fonksiyon; hiçbir yerde yakalayan lambda yoktur).

Nötr terimlerde ``act``, eliminasyonu ACTED özne üzerinde YENİDEN İŞLETİR
(``uygula``, ``yol_uygula``, ``cember_ind`` … akıllı kurucuları çağırarak);
böylece ``i↦0`` ikamesi bir nötrü kanonik hâle getirdiğinde indirgeme
kaçmaz.
"""
from __future__ import annotations

import itertools
from typing import Callable, Dict, List, Optional, Sequence, Set, Tuple

from .aralik import (BIR, DOGRU, SIFIR, YANLIS, Aralik, Kofibrasyon,
                     aralik_esitligi, yuzu_atamaya_cevir)
from . import sozdizim as S
from . import terimler as TR
from .sozdizim import Terim, Yuz

_sayac = itertools.count()


def taze(taban: str = "x") -> str:
    return "%s!%d" % (taban.split("!")[0], next(_sayac))


class CekirdekHatasi(Exception):
    pass


# =====================================================================
#  Ortam
# =====================================================================
class Ortam:
    """Terim değişkenleri → Değer, aralık değişkenleri → Aralık."""

    __slots__ = ("terimler", "araliklar")

    def __init__(self, terimler=None, araliklar=None) -> None:
        self.terimler: Dict[str, "Deger"] = terimler or {}
        self.araliklar: Dict[str, Aralik] = araliklar or {}

    def genislet(self, ad: str, d: "Deger") -> "Ortam":
        y = dict(self.terimler)
        y[ad] = d
        return Ortam(y, self.araliklar)

    def ara_genislet(self, ad: str, r: Aralik) -> "Ortam":
        y = dict(self.araliklar)
        y[ad] = r
        return Ortam(self.terimler, y)

    def act(self, s: Dict[str, Aralik]) -> "Ortam":
        if not s:
            return self
        return Ortam({k: v.act(s) for k, v in self.terimler.items()},
                     {k: v.yerine_koy(s) for k, v in self.araliklar.items()})

    def __repr__(self) -> str:
        return "Ortam(%d terim, %d aralık)" % (len(self.terimler),
                                               len(self.araliklar))


BOS = Ortam()


# =====================================================================
#  Değerler
# =====================================================================
class Deger:
    __slots__ = ()

    def act(self, s: Dict[str, Aralik]) -> "Deger":
        raise NotImplementedError


def _act(x, s):
    if isinstance(x, Aralik):
        return x.yerine_koy(s)
    if isinstance(x, tuple):
        return tuple(_act(y, s) for y in x)
    fn = getattr(x, "act", None)
    return fn(s) if fn is not None else x


class _Basit(Deger):
    """Alansız kanonik değerler."""
    __slots__ = ()

    def act(self, s):
        return self

    def __repr__(self):
        return type(self).__name__


class DDogal(_Basit):
    __slots__ = ()


class DTamsayi(_Basit):
    __slots__ = ()


class DCember(_Basit):
    __slots__ = ()


class DTaban(_Basit):
    __slots__ = ()


class DSfr(_Basit):
    __slots__ = ()


class DEvren(Deger):
    __slots__ = ("seviye",)

    def __init__(self, seviye: int) -> None:
        self.seviye = seviye

    def act(self, s):
        return self


class DPi(Deger):
    __slots__ = ("alan", "kap")

    def __init__(self, alan: Deger, kap: "Kapanis") -> None:
        self.alan, self.kap = alan, kap

    def act(self, s):
        return DPi(self.alan.act(s), self.kap.act(s))


class DSigma(Deger):
    __slots__ = ("alan", "kap")

    def __init__(self, alan: Deger, kap: "Kapanis") -> None:
        self.alan, self.kap = alan, kap

    def act(self, s):
        return DSigma(self.alan.act(s), self.kap.act(s))


class DLam(Deger):
    __slots__ = ("kap",)

    def __init__(self, kap: "Kapanis") -> None:
        self.kap = kap

    def act(self, s):
        return DLam(self.kap.act(s))


class DCift(Deger):
    __slots__ = ("bir", "iki")

    def __init__(self, bir: Deger, iki: Deger) -> None:
        self.bir, self.iki = bir, iki

    def act(self, s):
        return DCift(self.bir.act(s), self.iki.act(s))


class DYolP(Deger):
    __slots__ = ("cizgi", "sol", "sag")

    def __init__(self, cizgi: "ACizgi", sol: Deger, sag: Deger) -> None:
        self.cizgi, self.sol, self.sag = cizgi, sol, sag

    def act(self, s):
        return DYolP(self.cizgi.act(s), self.sol.act(s), self.sag.act(s))


class DYolLam(Deger):
    __slots__ = ("cizgi",)

    def __init__(self, cizgi: "ACizgi") -> None:
        self.cizgi = cizgi

    def act(self, s):
        return DYolLam(self.cizgi.act(s))


class DArd(Deger):
    __slots__ = ("alt",)

    def __init__(self, alt: Deger) -> None:
        self.alt = alt

    def act(self, s):
        return DArd(self.alt.act(s))


class DPoz(Deger):
    __slots__ = ("alt",)

    def __init__(self, alt: Deger) -> None:
        self.alt = alt

    def act(self, s):
        return DPoz(self.alt.act(s))


class DNegArd(Deger):
    __slots__ = ("alt",)

    def __init__(self, alt: Deger) -> None:
        self.alt = alt

    def act(self, s):
        return DNegArd(self.alt.act(s))


class DDongu(Deger):
    """``loop r`` -- r kesinlikle 0/1 değildir (öyleyse DTaban'a çöker)."""
    __slots__ = ("r",)

    def __init__(self, r: Aralik) -> None:
        self.r = r

    def act(self, s):
        return dongu(self.r.yerine_koy(s))


class DYapistir(Deger):
    """``Glue taban [ (yuz, T, denklik) ]``"""
    __slots__ = ("taban", "dallar")

    def __init__(self, taban: Deger, dallar) -> None:
        self.taban, self.dallar = taban, tuple(dallar)

    def act(self, s):
        return yapistir(self.taban.act(s),
                        _dallari_act(self.dallar, s))


class DYapistirTerim(Deger):
    __slots__ = ("dallar", "taban")

    def __init__(self, dallar, taban: Deger) -> None:
        self.dallar, self.taban = tuple(dallar), taban

    def act(self, s):
        return yapistir_terim(_dallari_act(self.dallar, s), self.taban.act(s))


class DHKomp(Deger):
    """S¹ içindeki hcomp -- KANONİK bir değerdir."""
    __slots__ = ("tip", "sistem", "u0")

    def __init__(self, tip: Deger, sistem: "Sistem", u0: Deger) -> None:
        self.tip, self.sistem, self.u0 = tip, sistem, u0

    def act(self, s):
        return komp(ASabit(self.tip.act(s)), self.sistem.act(s), self.u0.act(s))


class DNotr(Deger):
    __slots__ = ("n", "tip")

    def __init__(self, n: "Notr", tip: Deger) -> None:
        self.n, self.tip = n, tip

    def act(self, s):
        return self.n.act(s)


def _dallari_act(dallar, s):
    """Yüzler ikame altında BİRDEN ÇOK yüze açılabilir."""
    yeni = []
    for dal in dallar:
        k = Kofibrasyon([dal[0]]).yerine_koy(s)
        if k.bos_mu():
            continue
        geri = tuple(_act(x, s) for x in dal[1:])
        for f in k.yuzler:
            yeni.append((f,) + geri)
    return tuple(yeni)


# =====================================================================
#  Nötrler -- act ELİMİNASYONU YENİDEN İŞLETİR
# =====================================================================
class Notr:
    __slots__ = ()

    def act(self, s) -> Deger:
        raise NotImplementedError


class NDeg(Notr):
    __slots__ = ("ad", "tip")

    def __init__(self, ad: str, tip: Deger) -> None:
        self.ad, self.tip = ad, tip

    def act(self, s):
        return notr(NDeg(self.ad, self.tip.act(s)), self.tip.act(s))


class NUygula(Notr):
    __slots__ = ("n", "arg")

    def __init__(self, n: Deger, arg: Deger) -> None:
        self.n, self.arg = n, arg

    def act(self, s):
        return uygula(self.n.act(s), self.arg.act(s))


class NBir(Notr):
    __slots__ = ("n",)

    def __init__(self, n: Deger) -> None:
        self.n = n

    def act(self, s):
        return bir(self.n.act(s))


class NIki(Notr):
    __slots__ = ("n",)

    def __init__(self, n: Deger) -> None:
        self.n = n

    def act(self, s):
        return iki(self.n.act(s))


class NYolUygula(Notr):
    __slots__ = ("n", "r")

    def __init__(self, n: Deger, r: Aralik) -> None:
        self.n, self.r = n, r

    def act(self, s):
        return yol_uygula(self.n.act(s), self.r.yerine_koy(s))


class NKomp(Notr):
    __slots__ = ("cizgi", "sistem", "u0")

    def __init__(self, cizgi: "ACizgi", sistem: "Sistem", u0: Deger) -> None:
        self.cizgi, self.sistem, self.u0 = cizgi, sistem, u0

    def act(self, s):
        return komp(self.cizgi.act(s), self.sistem.act(s), self.u0.act(s))


class NCoz(Notr):
    __slots__ = ("taban", "dallar", "govde")

    def __init__(self, taban: Deger, dallar, govde: Deger) -> None:
        self.taban, self.dallar, self.govde = taban, tuple(dallar), govde

    def act(self, s):
        return coz(self.taban.act(s), _dallari_act(self.dallar, s),
                   self.govde.act(s))


class NDogalInd(Notr):
    __slots__ = ("motif", "sfr", "ard", "sayi")

    def __init__(self, motif: "Kapanis", sfr: Deger, ard: "Kapanis2",
                 sayi: Deger) -> None:
        self.motif, self.sfr, self.ard, self.sayi = motif, sfr, ard, sayi

    def act(self, s):
        return dogal_ind(self.motif.act(s), self.sfr.act(s), self.ard.act(s),
                         self.sayi.act(s))


class NTamsayiInd(Notr):
    __slots__ = ("motif", "poz", "neg", "sayi")

    def __init__(self, motif, poz, neg, sayi) -> None:
        self.motif, self.poz, self.neg, self.sayi = motif, poz, neg, sayi

    def act(self, s):
        return tamsayi_ind(self.motif.act(s), self.poz.act(s), self.neg.act(s),
                           self.sayi.act(s))


class NCemberInd(Notr):
    __slots__ = ("motif", "taban_dali", "dongu_dali", "nokta")

    def __init__(self, motif: "Kapanis", taban_dali: Deger,
                 dongu_dali: "ACizgi", nokta: Deger) -> None:
        self.motif, self.taban_dali = motif, taban_dali
        self.dongu_dali, self.nokta = dongu_dali, nokta

    def act(self, s):
        return cember_ind(self.motif.act(s), self.taban_dali.act(s),
                          self.dongu_dali.act(s), self.nokta.act(s))


# =====================================================================
#  Kapanışlar -- hepsi VERİ KURUCUSU
# =====================================================================
class Kapanis:
    """``Deger -> Deger``"""
    __slots__ = ()

    def uygula(self, d: Deger) -> Deger:
        raise NotImplementedError

    def act(self, s) -> "Kapanis":
        raise NotImplementedError


class KSoz(Kapanis):
    __slots__ = ("ad", "terim", "ortam")

    def __init__(self, ad: str, terim: Terim, ortam: Ortam) -> None:
        self.ad, self.terim, self.ortam = ad, terim, ortam

    def uygula(self, d):
        return degerlendir(self.terim, self.ortam.genislet(self.ad, d))

    def act(self, s):
        return KSoz(self.ad, self.terim, self.ortam.act(s))


class KSabit(Kapanis):
    __slots__ = ("deger",)

    def __init__(self, deger: Deger) -> None:
        self.deger = deger

    def uygula(self, d):
        return self.deger

    def act(self, s):
        return KSabit(self.deger.act(s))


class KTuretilmis(Kapanis):
    """Türetilmiş kapanış: etiket + alanlar + modül seviyesi fonksiyon.

    Yakalayan lambda YOKTUR; ``act`` alanları dönüştürüp yeniden kurar.
    """
    __slots__ = ("fn", "alanlar")

    def __init__(self, fn: Callable, alanlar: tuple) -> None:
        self.fn, self.alanlar = fn, alanlar

    def uygula(self, d):
        return self.fn(self.alanlar, d)

    def act(self, s):
        return KTuretilmis(self.fn, tuple(_act(a, s) for a in self.alanlar))


class Kapanis2:
    """İki argümanlı kapanış (ℕ tümevarımının ardıl dalı için)."""
    __slots__ = ("ad1", "ad2", "terim", "ortam")

    def __init__(self, ad1: str, ad2: str, terim: Terim, ortam: Ortam) -> None:
        self.ad1, self.ad2, self.terim, self.ortam = ad1, ad2, terim, ortam

    def uygula(self, a: Deger, b: Deger) -> Deger:
        return degerlendir(self.terim,
                           self.ortam.genislet(self.ad1, a).genislet(self.ad2, b))

    def act(self, s):
        return Kapanis2(self.ad1, self.ad2, self.terim, self.ortam.act(s))


class ACizgi:
    """``Aralik -> Deger``"""
    __slots__ = ()

    def uygula(self, r: Aralik) -> Deger:
        raise NotImplementedError

    def act(self, s) -> "ACizgi":
        raise NotImplementedError


class ASabit(ACizgi):
    __slots__ = ("deger",)

    def __init__(self, deger: Deger) -> None:
        self.deger = deger

    def uygula(self, r):
        return self.deger

    def act(self, s):
        return ASabit(self.deger.act(s))


class ASoz(ACizgi):
    __slots__ = ("ad", "terim", "ortam")

    def __init__(self, ad: str, terim: Terim, ortam: Ortam) -> None:
        self.ad, self.terim, self.ortam = ad, terim, ortam

    def uygula(self, r):
        return degerlendir(self.terim, self.ortam.ara_genislet(self.ad, r))

    def act(self, s):
        return ASoz(self.ad, self.terim, self.ortam.act(s))


class ATuretilmis(ACizgi):
    """Türetilmiş çizgi -- ``KTuretilmis``in aralık mukabili."""
    __slots__ = ("fn", "alanlar")

    def __init__(self, fn: Callable, alanlar: tuple) -> None:
        self.fn, self.alanlar = fn, alanlar

    def uygula(self, r):
        return self.fn(self.alanlar, r)

    def act(self, s):
        return ATuretilmis(self.fn, tuple(_act(a, s) for a in self.alanlar))


class AYeniden(ACizgi):
    """``λr. alt(ifade[ad := r])`` -- yeniden indisleme."""
    __slots__ = ("alt", "ad", "ifade")

    def __init__(self, alt: ACizgi, ad: str, ifade: Aralik) -> None:
        self.alt, self.ad, self.ifade = alt, ad, ifade

    def uygula(self, r):
        return self.alt.uygula(self.ifade.yerine_koy({self.ad: r}))

    def act(self, s):
        s2 = {k: v for k, v in s.items() if k != self.ad}
        return AYeniden(self.alt.act(s), self.ad, self.ifade.yerine_koy(s2))


# =====================================================================
#  Sistem (kısmî eleman)
# =====================================================================
class Sistem:
    """``[(yuz, ACizgi)]`` -- ikame altında yüzler açılabilir."""

    __slots__ = ("dallar",)

    def __init__(self, dallar: Sequence[Tuple[Yuz, ACizgi]]) -> None:
        self.dallar = tuple((frozenset(y), c) for (y, c) in dallar)

    def act(self, s) -> "Sistem":
        return Sistem(_dallari_act(self.dallar, s))

    def ust_yuz(self) -> Optional[ACizgi]:
        for (y, c) in self.dallar:
            if not y:
                return c
        return None

    def bos_mu(self) -> bool:
        return not self.dallar

    def __iter__(self):
        return iter(self.dallar)

    def __len__(self):
        return len(self.dallar)


BOS_SISTEM = Sistem([])


# =====================================================================
#  Eta genişletmesi ve nötr kurucusu
# =====================================================================
def _eta_pi(alanlar, v):
    d, tip = alanlar
    return notr(NUygula(d, v), tip.kap.uygula(v))


def _eta_yol(alanlar, r):
    d, tip = alanlar
    if r.sifir_mi():
        return tip.sol
    if r.bir_mi():
        return tip.sag
    return notr(NYolUygula(d, r), tip.cizgi.uygula(r))


def notr(n: Notr, tip: Optional[Deger]) -> Deger:
    """Nötr değer -- Π/Σ/Yol tiplerinde DERHAL eta genişletilir.

    Böylece geri okuma tipsiz yapılabilir ve eta bedavaya gelir.
    """
    d = DNotr(n, tip)
    if isinstance(tip, DPi):
        return DLam(KTuretilmis(_eta_pi, (d, tip)))
    if isinstance(tip, DSigma):
        b = notr(NBir(d), tip.alan)
        return DCift(b, notr(NIki(d), tip.kap.uygula(b)))
    if isinstance(tip, DYolP):
        return DYolLam(ATuretilmis(_eta_yol, (d, tip)))
    return d


# =====================================================================
#  Eliminatörler
# =====================================================================
def uygula(f: Deger, a: Deger) -> Deger:
    if isinstance(f, DLam):
        return f.kap.uygula(a)
    return DNotr(NUygula(f, a), None)


def bir(d: Deger) -> Deger:
    if isinstance(d, DCift):
        return d.bir
    return DNotr(NBir(d), None)


def iki(d: Deger) -> Deger:
    if isinstance(d, DCift):
        return d.iki
    return DNotr(NIki(d), None)


def yol_uygula(p: Deger, r: Aralik) -> Deger:
    if isinstance(p, DYolLam):
        return p.cizgi.uygula(r)
    return DNotr(NYolUygula(p, r), None)


def dongu(r: Aralik) -> Deger:
    if r.sifir_mi() or r.bir_mi():
        return DTaban()
    return DDongu(r)


def dogal_ind(motif: Kapanis, sfr: Deger, ard: Kapanis2, sayi: Deger) -> Deger:
    if isinstance(sayi, DSfr):
        return sfr
    if isinstance(sayi, DArd):
        return ard.uygula(sayi.alt, dogal_ind(motif, sfr, ard, sayi.alt))
    return notr(NDogalInd(motif, sfr, ard, sayi), motif.uygula(sayi))


def tamsayi_ind(motif: Kapanis, poz: Kapanis, neg: Kapanis,
                sayi: Deger) -> Deger:
    if isinstance(sayi, DPoz):
        return poz.uygula(sayi.alt)
    if isinstance(sayi, DNegArd):
        return neg.uygula(sayi.alt)
    return notr(NTamsayiInd(motif, poz, neg, sayi), motif.uygula(sayi))


def _cember_hedef(alanlar, r):
    """``λr. motif(hfill r)``"""
    motif, hfill = alanlar
    return motif.uygula(hfill.uygula(r))


def _cember_dal(alanlar, r):
    motif, tb, dd, c = alanlar
    return cember_ind(motif, tb, dd, c.uygula(r))


def cember_ind(motif: Kapanis, taban_dali: Deger, dongu_dali: ACizgi,
               nokta: Deger) -> Deger:
    if isinstance(nokta, DTaban):
        return taban_dali
    if isinstance(nokta, DDongu):
        return dongu_dali.uygula(nokta.r)
    if isinstance(nokta, DHKomp) and isinstance(nokta.tip, DCember):
        # S¹ eliminatörü hcomp ile DEĞİŞİR: hedefte comp doğar.
        hfill = dolgu(ASabit(DCember()), nokta.sistem, nokta.u0)
        L = ATuretilmis(_cember_hedef, (motif, hfill))
        sis = Sistem([(y, ATuretilmis(_cember_dal, (motif, taban_dali,
                                                    dongu_dali, c)))
                      for (y, c) in nokta.sistem])
        return komp(L, sis, cember_ind(motif, taban_dali, dongu_dali,
                                       nokta.u0))
    return notr(NCemberInd(motif, taban_dali, dongu_dali, nokta),
                motif.uygula(nokta))


def yapistir(taban: Deger, dallar) -> Deger:
    for (y, T, _e) in dallar:
        if not y:
            return T
    if not dallar:
        return taban
    return DYapistir(taban, dallar)


def yapistir_terim(dallar, taban: Deger) -> Deger:
    for (y, g) in dallar:
        if not y:
            return g
    if not dallar:
        return taban
    return DYapistirTerim(dallar, taban)


def coz(taban: Deger, dallar, govde: Deger) -> Deger:
    for (y, _T, e) in dallar:
        if not y:
            return uygula(bir(e), govde)
    if not dallar:
        return govde
    if isinstance(govde, DYapistirTerim):
        return govde.taban
    return DNotr(NCoz(taban, dallar, govde), taban)


# =====================================================================
#  Türetilmiş çizgiler (hepsi modül seviyesinde fonksiyon + alanlar)
# =====================================================================
def _alan_c(al, r):
    (L,) = al
    return L.uygula(r).alan


def _kap_uyg_c(al, r):
    L, w = al
    return L.uygula(r).kap.uygula(w.uygula(r))


def _uyg_c(al, r):
    c, w = al
    return uygula(c.uygula(r), w.uygula(r))


def _bir_c(al, r):
    (c,) = al
    return bir(c.uygula(r))


def _iki_c(al, r):
    (c,) = al
    return iki(c.uygula(r))


def _alt_c(al, r):
    (c,) = al
    return c.uygula(r).alt


def _geri_dolgu_c(al, r):
    """``w(r) : A(r)``, ``w(1) = v`` -- geriye doğru dolgu."""
    A, v = al
    j = taze("j")
    hat = AYeniden(A, j, r.veya(Aralik.degisken(j).degil()))
    return transp(hat, aralik_esitligi(r, True), v)


def _dolgu_c(al, r):
    L, sistem, u0 = al
    j = taze("j")
    jv = Aralik.degisken(j)
    dallar = [(y, AYeniden(c, j, jv.ve(r))) for (y, c) in sistem]
    for f in aralik_esitligi(r, False).yuzler:
        dallar.append((f, ASabit(u0)))
    return komp(AYeniden(L, j, jv.ve(r)), Sistem(dallar), u0)


def _komp_pi_k(al, v):
    L, sistem, u0 = al
    A = ATuretilmis(_alan_c, (L,))
    w = ATuretilmis(_geri_dolgu_c, (A, v))
    yeni_sis = Sistem([(y, ATuretilmis(_uyg_c, (c, w))) for (y, c) in sistem])
    return komp(ATuretilmis(_kap_uyg_c, (L, w)), yeni_sis,
                uygula(u0, w.uygula(SIFIR)))


def _yolp_cizgi_c(al, i):
    L, j = al
    return L.uygula(i).cizgi.uygula(j)


def _yolp_sol_c(al, i):
    (L,) = al
    return L.uygula(i).sol


def _yolp_sag_c(al, i):
    (L,) = al
    return L.uygula(i).sag


def _yol_uyg_c(al, i):
    c, j = al
    return yol_uygula(c.uygula(i), j)


def _komp_yol_c(al, j):
    L, sistem, u0 = al
    dallar = [(y, ATuretilmis(_yol_uyg_c, (c, j))) for (y, c) in sistem]
    for f in aralik_esitligi(j, False).yuzler:
        dallar.append((f, ATuretilmis(_yolp_sol_c, (L,))))
    for f in aralik_esitligi(j, True).yuzler:
        dallar.append((f, ATuretilmis(_yolp_sag_c, (L,))))
    return komp(ATuretilmis(_yolp_cizgi_c, (L, j)), Sistem(dallar),
                yol_uygula(u0, j))


# =====================================================================
#  Kan işlemleri
# =====================================================================
def _sabit_mi(L: ACizgi) -> bool:
    """MUHAFAZAKÂR sabitlik sınaması: yalnız ispatlanabildiğinde True.

    DİKKAT: ``L(0) == L(1)`` sınaması SAĞLAM DEĞİLDİR (``ua e`` tuzağı);
    burada asla kullanılmaz.
    """
    if isinstance(L, ASabit):
        return True
    if isinstance(L, ASoz):
        return L.ad not in TR.ara_serbest(L.terim)
    if isinstance(L, AYeniden):
        return _sabit_mi(L.alt) or (L.ad not in L.ifade.degiskenler())
    return False


def transp(L: ACizgi, kof: Kofibrasyon, u0: Deger) -> Deger:
    if kof.dogru_mu():
        return u0
    return komp(L, Sistem([(y, ASabit(u0)) for y in kof.yuzler]), u0)


def hkomp(tip: Deger, sistem: Sistem, u0: Deger) -> Deger:
    return komp(ASabit(tip), sistem, u0)


def dolgu(L: ACizgi, sistem: Sistem, u0: Deger) -> ACizgi:
    """``fill`` -- ``fill(0) = u0``, ``fill(1) = comp``."""
    return ATuretilmis(_dolgu_c, (L, sistem, u0))


def komp(L: ACizgi, sistem: Sistem, u0: Deger) -> Deger:
    ust = sistem.ust_yuz()
    if ust is not None:
        return ust.uygula(BIR)
    if sistem.bos_mu() and _sabit_mi(L):
        return u0

    i = taze("i")
    A = L.uygula(Aralik.degisken(i))

    if isinstance(A, DPi):
        return DLam(KTuretilmis(_komp_pi_k, (L, sistem, u0)))

    if isinstance(A, DSigma):
        Aalan = ATuretilmis(_alan_c, (L,))
        bir_sis = Sistem([(y, ATuretilmis(_bir_c, (c,))) for (y, c) in sistem])
        iki_sis = Sistem([(y, ATuretilmis(_iki_c, (c,))) for (y, c) in sistem])
        a_c = dolgu(Aalan, bir_sis, bir(u0))
        return DCift(komp(Aalan, bir_sis, bir(u0)),
                     komp(ATuretilmis(_kap_uyg_c, (L, a_c)), iki_sis, iki(u0)))

    if isinstance(A, DYolP):
        return DYolLam(ATuretilmis(_komp_yol_c, (L, sistem, u0)))

    if isinstance(A, (DDogal, DTamsayi)):
        iv = Aralik.degisken(i)
        govdeler = [c.uygula(iv) for (_, c) in sistem]

        def _ic(alt_u0):
            return komp(ASabit(DDogal()),
                        Sistem([(y, ATuretilmis(_alt_c, (c,)))
                                for (y, c) in sistem]), alt_u0)

        if isinstance(u0, DSfr) and all(isinstance(x, DSfr) for x in govdeler):
            return DSfr()
        if isinstance(u0, DArd) and all(isinstance(x, DArd) for x in govdeler):
            return DArd(_ic(u0.alt))
        if isinstance(u0, DPoz) and all(isinstance(x, DPoz) for x in govdeler):
            return DPoz(_ic(u0.alt))
        if isinstance(u0, DNegArd) and all(isinstance(x, DNegArd)
                                           for x in govdeler):
            return DNegArd(_ic(u0.alt))
        return notr(NKomp(L, sistem, u0), L.uygula(BIR))

    if isinstance(A, DCember):
        if sistem.bos_mu():
            return u0
        return DHKomp(DCember(), sistem, u0)

    if isinstance(A, DEvren):
        from .denklik import komp_evren
        return komp_evren(L, sistem, u0)

    if isinstance(A, DYapistir):
        from .denklik import komp_yapistir
        return komp_yapistir(L, sistem, u0)

    return notr(NKomp(L, sistem, u0), L.uygula(BIR))


# =====================================================================
#  Değerlendirme
# =====================================================================
def _sistem_kur(dallar, ad: str, ortam: Ortam) -> Sistem:
    """Terim yüzlerini ortamdaki aralık bağlarıyla çözer (açılabilir)."""
    yeni = []
    for (y, govde) in dallar:
        k = Kofibrasyon([y]).yerine_koy(ortam.araliklar)
        if k.bos_mu():
            continue
        c = ASoz(ad, govde, ortam)
        for f in k.yuzler:
            yeni.append((f, c))
    return Sistem(yeni)


def _glue_dallari(dallar, ortam: Ortam):
    yeni = []
    for (y, T, e) in dallar:
        k = Kofibrasyon([y]).yerine_koy(ortam.araliklar)
        if k.bos_mu():
            continue
        Tv, ev = degerlendir(T, ortam), degerlendir(e, ortam)
        for f in k.yuzler:
            yeni.append((f, Tv, ev))
    return yeni


def degerlendir(t: Terim, ortam: Ortam) -> Deger:
    if isinstance(t, S.Deg):
        v = ortam.terimler.get(t.ad)
        if v is None:
            raise CekirdekHatasi("bağlı olmayan değişken: %s" % t.ad)
        return v
    if isinstance(t, S.Evren):
        return DEvren(t.seviye)
    if isinstance(t, S.Pi):
        return DPi(degerlendir(t.alan, ortam), KSoz(t.ad, t.hedef, ortam))
    if isinstance(t, S.Sigma):
        return DSigma(degerlendir(t.alan, ortam), KSoz(t.ad, t.hedef, ortam))
    if isinstance(t, S.Lam):
        return DLam(KSoz(t.ad, t.govde, ortam))
    if isinstance(t, S.Uygula):
        return uygula(degerlendir(t.fonk, ortam), degerlendir(t.arg, ortam))
    if isinstance(t, S.Cift):
        return DCift(degerlendir(t.bir, ortam), degerlendir(t.iki, ortam))
    if isinstance(t, S.Birinci):
        return bir(degerlendir(t.cift, ortam))
    if isinstance(t, S.Ikinci):
        return iki(degerlendir(t.cift, ortam))
    if isinstance(t, S.YolP):
        return DYolP(ASoz(t.ad, t.cizgi, ortam),
                     degerlendir(t.sol, ortam), degerlendir(t.sag, ortam))
    if isinstance(t, S.YolLam):
        return DYolLam(ASoz(t.ad, t.govde, ortam))
    if isinstance(t, S.YolUygula):
        return yol_uygula(degerlendir(t.yol, ortam),
                          t.r.yerine_koy(ortam.araliklar))
    if isinstance(t, S.Dogal):
        return DDogal()
    if isinstance(t, S.Sfr):
        return DSfr()
    if isinstance(t, S.Ard):
        return DArd(degerlendir(t.alt, ortam))
    if isinstance(t, S.Tamsayi):
        return DTamsayi()
    if isinstance(t, S.Poz):
        return DPoz(degerlendir(t.alt, ortam))
    if isinstance(t, S.NegArd):
        return DNegArd(degerlendir(t.alt, ortam))
    if isinstance(t, S.Cember):
        return DCember()
    if isinstance(t, S.Taban):
        return DTaban()
    if isinstance(t, S.Dongu):
        return dongu(t.r.yerine_koy(ortam.araliklar))
    if isinstance(t, S.DogalInd):
        return dogal_ind(KSoz(t.ad, t.hedef, ortam),
                         degerlendir(t.sfr_dali, ortam),
                         Kapanis2(t.n_ad, t.rec_ad, t.ard_dali, ortam),
                         degerlendir(t.sayi, ortam))
    if isinstance(t, S.TamsayiInd):
        return tamsayi_ind(KSoz(t.ad, t.hedef, ortam),
                           KSoz(t.poz_ad, t.poz_dali, ortam),
                           KSoz(t.neg_ad, t.neg_dali, ortam),
                           degerlendir(t.sayi, ortam))
    if isinstance(t, S.CemberInd):
        return cember_ind(KSoz(t.ad, t.hedef, ortam),
                          degerlendir(t.taban_dali, ortam),
                          ASoz(t.i_ad, t.dongu_dali, ortam),
                          degerlendir(t.nokta, ortam))
    if isinstance(t, S.Transp):
        return transp(ASoz(t.ad, t.cizgi, ortam),
                      t.kof.yerine_koy(ortam.araliklar),
                      degerlendir(t.u0, ortam))
    if isinstance(t, S.Komp):
        return komp(ASoz(t.ad, t.cizgi, ortam),
                    _sistem_kur(t.dallar, t.ad, ortam),
                    degerlendir(t.u0, ortam))
    if isinstance(t, S.HKomp):
        return komp(ASabit(degerlendir(t.tip, ortam)),
                    _sistem_kur(t.dallar, t.ad, ortam),
                    degerlendir(t.u0, ortam))
    if isinstance(t, S.Yapistir):
        return yapistir(degerlendir(t.taban, ortam),
                        _glue_dallari(t.dallar, ortam))
    if isinstance(t, S.YapistirTerim):
        yeni = []
        for (y, govde) in t.dallar:
            k = Kofibrasyon([y]).yerine_koy(ortam.araliklar)
            if k.bos_mu():
                continue
            gv = degerlendir(govde, ortam)
            for f in k.yuzler:
                yeni.append((f, gv))
        return yapistir_terim(yeni, degerlendir(t.taban_terim, ortam))
    if isinstance(t, S.Coz):
        return coz(degerlendir(t.taban, ortam),
                   _glue_dallari(t.dallar, ortam),
                   degerlendir(t.govde, ortam))
    raise CekirdekHatasi("değerlendirilemeyen terim: %r" % (t,))


# =====================================================================
#  Geri okuma (quote) -- doğrudan ALFA-KANONİK terim üretir
# =====================================================================
def _tv(k: int) -> str:
    return "#%d" % k


def _iv(k: int) -> str:
    return "%%%d" % k


def _ivar(k: int) -> Aralik:
    return Aralik.degisken(_iv(k))


def geri_oku(d: Deger, k: int = 0) -> Terim:
    if isinstance(d, DEvren):
        return S.Evren(d.seviye)
    if isinstance(d, DDogal):
        return S.Dogal()
    if isinstance(d, DTamsayi):
        return S.Tamsayi()
    if isinstance(d, DCember):
        return S.Cember()
    if isinstance(d, DTaban):
        return S.Taban()
    if isinstance(d, DSfr):
        return S.Sfr()
    if isinstance(d, DArd):
        return S.Ard(geri_oku(d.alt, k))
    if isinstance(d, DPoz):
        return S.Poz(geri_oku(d.alt, k))
    if isinstance(d, DNegArd):
        return S.NegArd(geri_oku(d.alt, k))
    if isinstance(d, DDongu):
        return S.Dongu(d.r)
    if isinstance(d, DPi):
        v = notr(NDeg(_tv(k), d.alan), d.alan)
        return S.Pi(_tv(k), geri_oku(d.alan, k), geri_oku(d.kap.uygula(v), k + 1))
    if isinstance(d, DSigma):
        v = notr(NDeg(_tv(k), d.alan), d.alan)
        return S.Sigma(_tv(k), geri_oku(d.alan, k),
                       geri_oku(d.kap.uygula(v), k + 1))
    if isinstance(d, DLam):
        v = notr(NDeg(_tv(k), None), None)
        return S.Lam(_tv(k), geri_oku(d.kap.uygula(v), k + 1))
    if isinstance(d, DCift):
        return S.Cift(geri_oku(d.bir, k), geri_oku(d.iki, k))
    if isinstance(d, DYolP):
        return S.YolP(_iv(k), geri_oku(d.cizgi.uygula(_ivar(k)), k + 1),
                      geri_oku(d.sol, k), geri_oku(d.sag, k))
    if isinstance(d, DYolLam):
        return S.YolLam(_iv(k), geri_oku(d.cizgi.uygula(_ivar(k)), k + 1))
    if isinstance(d, DHKomp):
        r = _ivar(k)
        return S.HKomp(geri_oku(d.tip, k), _iv(k),
                       [(y, geri_oku(c.uygula(r), k + 1))
                        for (y, c) in d.sistem], geri_oku(d.u0, k))
    if isinstance(d, DYapistir):
        return S.Yapistir(geri_oku(d.taban, k),
                          [(y, geri_oku(T, k), geri_oku(e, k))
                           for (y, T, e) in d.dallar])
    if isinstance(d, DYapistirTerim):
        return S.YapistirTerim([(y, geri_oku(g, k)) for (y, g) in d.dallar],
                               geri_oku(d.taban, k))
    if isinstance(d, DNotr):
        return _geri_oku_notr(d.n, k)
    raise CekirdekHatasi("geri okunamayan değer: %r" % (d,))


def _geri_oku_notr(n: Notr, k: int) -> Terim:
    if isinstance(n, NDeg):
        return S.Deg(n.ad)
    if isinstance(n, NUygula):
        return S.Uygula(geri_oku(n.n, k), geri_oku(n.arg, k))
    if isinstance(n, NBir):
        return S.Birinci(geri_oku(n.n, k))
    if isinstance(n, NIki):
        return S.Ikinci(geri_oku(n.n, k))
    if isinstance(n, NYolUygula):
        return S.YolUygula(geri_oku(n.n, k), n.r)
    if isinstance(n, NKomp):
        r = _ivar(k)
        return S.Komp(_iv(k), geri_oku(n.cizgi.uygula(r), k + 1),
                      [(y, geri_oku(c.uygula(r), k + 1))
                       for (y, c) in n.sistem], geri_oku(n.u0, k))
    if isinstance(n, NCoz):
        return S.Coz(geri_oku(n.taban, k),
                     [(y, geri_oku(T, k), geri_oku(e, k))
                      for (y, T, e) in n.dallar], geri_oku(n.govde, k))
    if isinstance(n, NDogalInd):
        v = notr(NDeg(_tv(k), DDogal()), DDogal())
        v1 = notr(NDeg(_tv(k + 1), DDogal()), DDogal())
        v2 = notr(NDeg(_tv(k + 2), None), None)
        return S.DogalInd(_tv(k), geri_oku(n.motif.uygula(v), k + 1),
                          geri_oku(n.sfr, k), _tv(k + 1), _tv(k + 2),
                          geri_oku(n.ard.uygula(v1, v2), k + 3),
                          geri_oku(n.sayi, k))
    if isinstance(n, NTamsayiInd):
        v = notr(NDeg(_tv(k), DTamsayi()), DTamsayi())
        v1 = notr(NDeg(_tv(k + 1), DDogal()), DDogal())
        return S.TamsayiInd(_tv(k), geri_oku(n.motif.uygula(v), k + 1),
                            _tv(k + 1), geri_oku(n.poz.uygula(v1), k + 2),
                            _tv(k + 1), geri_oku(n.neg.uygula(v1), k + 2),
                            geri_oku(n.sayi, k))
    if isinstance(n, NCemberInd):
        v = notr(NDeg(_tv(k), DCember()), DCember())
        return S.CemberInd(_tv(k), geri_oku(n.motif.uygula(v), k + 1),
                           geri_oku(n.taban_dali, k), _iv(k + 1),
                           geri_oku(n.dongu_dali.uygula(_ivar(k + 1)), k + 2),
                           geri_oku(n.nokta, k))
    raise CekirdekHatasi("geri okunamayan nötr: %r" % (n,))


# =====================================================================
#  Bağlam, normal form, tanımsal eşitlik
# =====================================================================
def ortam_kur(baglam: Optional[Dict[str, Terim]] = None) -> Ortam:
    """Serbest değişkenleri, tipi verilmiş nötrlere bağlar."""
    o = BOS
    for ad, tip in (baglam or {}).items():
        try:
            tv = degerlendir(tip, o)
        except CekirdekHatasi:
            tv = None
        o = o.genislet(ad, notr(NDeg(ad, tv), tv))
    return o


def deger(t: Terim, baglam: Optional[Dict[str, Terim]] = None) -> Deger:
    return degerlendir(t, ortam_kur(baglam))


def nf(t: Terim, baglam: Optional[Dict[str, Terim]] = None) -> Terim:
    return geri_oku(deger(t, baglam), 0)


def _esit(a: Terim, b: Terim, derinlik: int = 0) -> bool:
    """Yapısal kıyas + Σ/Π/Yol için şekle dayalı eta."""
    if a == b:
        return True
    if isinstance(a, S.Cift) != isinstance(b, S.Cift):
        ct, obur = (a, b) if isinstance(a, S.Cift) else (b, a)
        return (_esit(ct.bir, S.Birinci(obur), derinlik)
                and _esit(ct.iki, S.Ikinci(obur), derinlik))
    if isinstance(a, S.Lam) != isinstance(b, S.Lam):
        lam, obur = (a, b) if isinstance(a, S.Lam) else (b, a)
        return _esit(lam.govde, S.Uygula(obur, S.Deg(lam.ad)), derinlik + 1)
    if isinstance(a, S.YolLam) != isinstance(b, S.YolLam):
        pl, obur = (a, b) if isinstance(a, S.YolLam) else (b, a)
        return _esit(pl.govde, S.YolUygula(obur, Aralik.degisken(pl.ad)),
                     derinlik + 1)
    if type(a) is not type(b):
        return False
    if isinstance(a, S.Cift):
        return (_esit(a.bir, b.bir, derinlik) and _esit(a.iki, b.iki, derinlik))
    if isinstance(a, S.Uygula):
        return (_esit(a.fonk, b.fonk, derinlik) and _esit(a.arg, b.arg, derinlik))
    if isinstance(a, (S.Birinci, S.Ikinci)):
        return _esit(a.cift, b.cift, derinlik)
    return False


def esdeger_mi(a: Terim, b: Terim,
               baglam: Optional[Dict[str, Terim]] = None) -> bool:
    o = ortam_kur(baglam)
    return _esit(geri_oku(degerlendir(a, o), 0),
                 geri_oku(degerlendir(b, o), 0))


def deger_esit_mi(d1: Deger, d2: Deger, k: int = 0) -> bool:
    return _esit(geri_oku(d1, k), geri_oku(d2, k), k)
