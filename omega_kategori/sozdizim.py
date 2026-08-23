"""
Kübik tip teorisinin sözdizimi (terimler).

Tasarım kararı: aralık alt-dili için ayrı bir terim ağacı TUTULMAZ. Aralık
ifadeleri doğrudan ``aralik.Aralik`` kafes elemanı olarak, kenar şartları da
``aralik.Kofibrasyon``/``Yuz`` olarak terimlerin içinde taşınır. Böylece
aralık ikamesi ve kanonik form, cebirin kendisi tarafından hâlledilir; terim
katmanında ayrıca aralık normalleştirmesi yapmak gerekmez.

Terimler yapısal olarak karşılaştırılabilir (``__eq__``/``__hash__``);
tanımsal eşitlik, iki terimi alfa-kanonik normal forma indirip
(``cekirdek.esdeger_mi``) kıyaslayarak denetlenir.
"""
from __future__ import annotations

from typing import FrozenSet, Sequence, Tuple

from .aralik import BIR, SIFIR, Aralik, Kofibrasyon

# Bir yüz: {(degisken, deger)} -- deger True ise (i=1), False ise (i=0)
Yuz = FrozenSet[Tuple[str, bool]]


class Dugum:
    """Yapısal eşitlik veren taban sınıf."""

    __slots__ = ()

    def _alanlar(self) -> tuple:
        return tuple(getattr(self, a) for a in self.__slots__)

    def __eq__(self, obur: object) -> bool:
        return type(self) is type(obur) and self._alanlar() == obur._alanlar()

    def __hash__(self) -> int:
        return hash((type(self).__name__, self._alanlar()))

    def __repr__(self) -> str:
        from .yazdir import terimi_yaz
        try:
            return terimi_yaz(self)  # type: ignore[arg-type]
        except Exception:
            return "%s(%s)" % (type(self).__name__,
                               ", ".join(repr(a) for a in self._alanlar()))


class Terim(Dugum):
    __slots__ = ()


# ---------------------------------------------------------------------
#  Çekirdek MLTT
# ---------------------------------------------------------------------
class Deg(Terim):
    """Terim değişkeni."""
    __slots__ = ("ad",)

    def __init__(self, ad: str) -> None:
        self.ad = ad


class Evren(Terim):
    """``U_seviye``"""
    __slots__ = ("seviye",)

    def __init__(self, seviye: int = 0) -> None:
        self.seviye = seviye


class Pi(Terim):
    """``(ad : alan) → hedef``"""
    __slots__ = ("ad", "alan", "hedef")

    def __init__(self, ad: str, alan: Terim, hedef: Terim) -> None:
        self.ad, self.alan, self.hedef = ad, alan, hedef


class Lam(Terim):
    __slots__ = ("ad", "govde")

    def __init__(self, ad: str, govde: Terim) -> None:
        self.ad, self.govde = ad, govde


class Uygula(Terim):
    __slots__ = ("fonk", "arg")

    def __init__(self, fonk: Terim, arg: Terim) -> None:
        self.fonk, self.arg = fonk, arg


class Sigma(Terim):
    """``(ad : alan) × hedef``"""
    __slots__ = ("ad", "alan", "hedef")

    def __init__(self, ad: str, alan: Terim, hedef: Terim) -> None:
        self.ad, self.alan, self.hedef = ad, alan, hedef


class Cift(Terim):
    __slots__ = ("bir", "iki")

    def __init__(self, bir: Terim, iki: Terim) -> None:
        self.bir, self.iki = bir, iki


class Birinci(Terim):
    __slots__ = ("cift",)

    def __init__(self, cift: Terim) -> None:
        self.cift = cift


class Ikinci(Terim):
    __slots__ = ("cift",)

    def __init__(self, cift: Terim) -> None:
        self.cift = cift


# ---------------------------------------------------------------------
#  Kübik çekirdek
# ---------------------------------------------------------------------
class YolP(Terim):
    """``PathP (λ ad. cizgi) sol sag``"""
    __slots__ = ("ad", "cizgi", "sol", "sag")

    def __init__(self, ad: str, cizgi: Terim, sol: Terim, sag: Terim) -> None:
        self.ad, self.cizgi, self.sol, self.sag = ad, cizgi, sol, sag


class YolLam(Terim):
    """``<ad> govde``"""
    __slots__ = ("ad", "govde")

    def __init__(self, ad: str, govde: Terim) -> None:
        self.ad, self.govde = ad, govde


class YolUygula(Terim):
    """``yol @ r``  (r bir aralık kafes elemanı)"""
    __slots__ = ("yol", "r")

    def __init__(self, yol: Terim, r: Aralik) -> None:
        self.yol, self.r = yol, r


class Transp(Terim):
    """``transp (λ ad. cizgi) kof u0``

    ``kof`` doğru olduğu yüzlerde ``cizgi`` sabit olmalıdır; orada transp
    özdeşliktir.
    """
    __slots__ = ("ad", "cizgi", "kof", "u0")

    def __init__(self, ad: str, cizgi: Terim, kof: Kofibrasyon, u0: Terim) -> None:
        self.ad, self.cizgi, self.kof, self.u0 = ad, cizgi, kof, u0


class Komp(Terim):
    """``comp (λ ad. cizgi) [dallar] u0`` -- çekirdeğin ASLİ Kan işlemi.

    ``dallar``: ``((yuz, govde), ...)``; ``govde`` içinde ``ad`` bağlıdır.
    ``transp`` ve ``hcomp`` bundan türetilir.
    """
    __slots__ = ("ad", "cizgi", "dallar", "u0")

    def __init__(self, ad: str, cizgi: Terim,
                 dallar: Sequence[Tuple[Yuz, Terim]], u0: Terim) -> None:
        self.ad, self.cizgi = ad, cizgi
        self.dallar = tuple((frozenset(y), t) for (y, t) in dallar)
        self.u0 = u0


class HKomp(Terim):
    """``hcomp {tip} [dallar] u0`` -- sabit tipte kapak doldurma."""
    __slots__ = ("tip", "ad", "dallar", "u0")

    def __init__(self, tip: Terim, ad: str,
                 dallar: Sequence[Tuple[Yuz, Terim]], u0: Terim) -> None:
        self.tip, self.ad = tip, ad
        self.dallar = tuple((frozenset(y), t) for (y, t) in dallar)
        self.u0 = u0


# ---------------------------------------------------------------------
#  Glue -- tümel değişmezliğin (univalence) hesaplanabilir zemini
# ---------------------------------------------------------------------
class Yapistir(Terim):
    """``Glue taban [dallar]``; ``dallar``: ``((yuz, T, denklik), ...)``

    ``denklik : Denklik T taban`` yani ``Σ (f : T → taban). izDenklik f``.
    """
    __slots__ = ("taban", "dallar")

    def __init__(self, taban: Terim,
                 dallar: Sequence[Tuple[Yuz, Terim, Terim]]) -> None:
        self.taban = taban
        self.dallar = tuple((frozenset(y), t, e) for (y, t, e) in dallar)


class YapistirTerim(Terim):
    """``glue [dallar] taban_terim``"""
    __slots__ = ("dallar", "taban_terim")

    def __init__(self, dallar: Sequence[Tuple[Yuz, Terim]],
                 taban_terim: Terim) -> None:
        self.dallar = tuple((frozenset(y), t) for (y, t) in dallar)
        self.taban_terim = taban_terim


class Coz(Terim):
    """``unglue g`` -- Glue tipinden taban tipe düşürme.

    ``dallar`` yalnız hangi yüzlerde hangi denkliğin uygulanacağını bilmek
    için taşınır (tip bilgisinin terimde kalması gerekir).
    """
    __slots__ = ("taban", "dallar", "govde")

    def __init__(self, taban: Terim,
                 dallar: Sequence[Tuple[Yuz, Terim, Terim]],
                 govde: Terim) -> None:
        self.taban = taban
        self.dallar = tuple((frozenset(y), t, e) for (y, t, e) in dallar)
        self.govde = govde


# ---------------------------------------------------------------------
#  Veri tipleri
# ---------------------------------------------------------------------
class Dogal(Terim):
    """ℕ"""
    __slots__ = ()


class Sfr(Terim):
    __slots__ = ()


class Ard(Terim):
    __slots__ = ("alt",)

    def __init__(self, alt: Terim) -> None:
        self.alt = alt


class DogalInd(Terim):
    """``natInd (λ ad. hedef) sfr_dali (λ n_ad rec_ad. ard_dali) sayi``"""
    __slots__ = ("ad", "hedef", "sfr_dali", "n_ad", "rec_ad", "ard_dali", "sayi")

    def __init__(self, ad: str, hedef: Terim, sfr_dali: Terim,
                 n_ad: str, rec_ad: str, ard_dali: Terim, sayi: Terim) -> None:
        self.ad, self.hedef, self.sfr_dali = ad, hedef, sfr_dali
        self.n_ad, self.rec_ad, self.ard_dali = n_ad, rec_ad, ard_dali
        self.sayi = sayi


class Tamsayi(Terim):
    """ℤ -- ``poz n`` = n,  ``negArd n`` = −(n+1)"""
    __slots__ = ()


class Poz(Terim):
    __slots__ = ("alt",)

    def __init__(self, alt: Terim) -> None:
        self.alt = alt


class NegArd(Terim):
    __slots__ = ("alt",)

    def __init__(self, alt: Terim) -> None:
        self.alt = alt


class TamsayiInd(Terim):
    """``intInd (λ ad. hedef) (λ poz_ad. poz_dali) (λ neg_ad. neg_dali) sayi``"""
    __slots__ = ("ad", "hedef", "poz_ad", "poz_dali", "neg_ad", "neg_dali", "sayi")

    def __init__(self, ad: str, hedef: Terim, poz_ad: str, poz_dali: Terim,
                 neg_ad: str, neg_dali: Terim, sayi: Terim) -> None:
        self.ad, self.hedef = ad, hedef
        self.poz_ad, self.poz_dali = poz_ad, poz_dali
        self.neg_ad, self.neg_dali = neg_ad, neg_dali
        self.sayi = sayi


# ---------------------------------------------------------------------
#  Yüksek tümevarımsal tip: çember (S¹)
# ---------------------------------------------------------------------
class Cember(Terim):
    """S¹"""
    __slots__ = ()


class Taban(Terim):
    __slots__ = ()


class Dongu(Terim):
    """``loop r``; ``r=0`` ve ``r=1`` uçlarında ``taban``."""
    __slots__ = ("r",)

    def __init__(self, r: Aralik) -> None:
        self.r = r


class CemberInd(Terim):
    """``S¹-ind (λ ad. hedef) taban_dali (<i_ad> dongu_dali) nokta``"""
    __slots__ = ("ad", "hedef", "taban_dali", "i_ad", "dongu_dali", "nokta")

    def __init__(self, ad: str, hedef: Terim, taban_dali: Terim,
                 i_ad: str, dongu_dali: Terim, nokta: Terim) -> None:
        self.ad, self.hedef, self.taban_dali = ad, hedef, taban_dali
        self.i_ad, self.dongu_dali, self.nokta = i_ad, dongu_dali, nokta


# ---------------------------------------------------------------------
#  Kolaylık kurucuları
# ---------------------------------------------------------------------
def yuz(**kisitlar: int) -> Yuz:
    """``yuz(i=0, j=1)`` → ``(i=0) ∧ (j=1)``"""
    return frozenset((ad, bool(deger)) for ad, deger in kisitlar.items())


def ar(ad: str) -> Aralik:
    return Aralik.degisken(ad)


def uygula_hepsi(fonk: Terim, *argumanlar: Terim) -> Terim:
    for a in argumanlar:
        fonk = Uygula(fonk, a)
    return fonk


def lam_hepsi(adlar: Sequence[str], govde: Terim) -> Terim:
    for ad in reversed(adlar):
        govde = Lam(ad, govde)
    return govde


def pi_hepsi(baglar: Sequence[Tuple[str, Terim]], hedef: Terim) -> Terim:
    for ad, tip in reversed(baglar):
        hedef = Pi(ad, tip, hedef)
    return hedef


def ok(alan: Terim, hedef: Terim) -> Terim:
    """Bağımsız fonksiyon tipi ``alan → hedef``."""
    return Pi("_", alan, hedef)


def carpim(sol: Terim, sag: Terim) -> Terim:
    """Bağımsız çarpım ``sol × sag``."""
    return Sigma("_", sol, sag)


def dogal_sayi(n: int) -> Terim:
    t: Terim = Sfr()
    for _ in range(n):
        t = Ard(t)
    return t


def tam_sayi(n: int) -> Terim:
    """``tam_sayi(2) = poz 2``, ``tam_sayi(-1) = negArd 0``"""
    if n >= 0:
        return Poz(dogal_sayi(n))
    return NegArd(dogal_sayi(-n - 1))


def yol(tip: Terim, sol: Terim, sag: Terim) -> Terim:
    """``Path tip sol sag = PathP (λ _. tip) sol sag``"""
    return YolP("_", tip, sol, sag)


def refl(terim: Terim) -> Terim:
    return YolLam("_", terim)
