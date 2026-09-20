from __future__ import annotations

import itertools
import math
import sys
from dataclasses import dataclass, field
from typing import (Any, Callable, Dict, FrozenSet, Iterable, Iterator,
                    List, Optional, Sequence, Set, Tuple, Union)

import numpy as np


Literal = Tuple[str, bool]


Cumle = FrozenSet[Literal]


def _antizincire_indir(cumleler: Iterable[Cumle]) -> FrozenSet[Cumle]:
    kume = {frozenset(c) for c in cumleler}
    if len(kume) <= 1:
        return frozenset(kume)
    kalan = sorted(kume, key=len)
    sonuc: List[Cumle] = []
    for c in kalan:
        for d in sonuc:
            if d <= c:
                break
        else:
            sonuc.append(c)
    return frozenset(sonuc)


class Aralik:

    __slots__ = ("cumleler",)

    def __init__(self, cumleler: Iterable[Cumle]) -> None:
        self.cumleler: FrozenSet[Cumle] = _antizincire_indir(cumleler)

    @staticmethod
    def degisken(ad: str) -> "Aralik":
        return Aralik([frozenset({(ad, True)})])

    @staticmethod
    def _literal(ad: str, pozitif: bool) -> "Aralik":
        return Aralik([frozenset({(ad, pozitif)})])

    def ve(self, obur: "Aralik") -> "Aralik":
        return Aralik(a | b for a in self.cumleler for b in obur.cumleler)

    def veya(self, obur: "Aralik") -> "Aralik":
        return Aralik(self.cumleler | obur.cumleler)

    def degil(self) -> "Aralik":
        sonuc = BIR
        for cumle in self.cumleler:
            if not cumle:
                return SIFIR
            ayrik = SIFIR
            for (ad, pozitif) in cumle:
                ayrik = ayrik.veya(Aralik._literal(ad, not pozitif))
            sonuc = sonuc.ve(ayrik)
        return sonuc

    def yerine_koy(self, atama: Dict[str, "Aralik"]) -> "Aralik":
        if not atama or not (self.degiskenler() & atama.keys()):
            return self
        sonuc = SIFIR
        for cumle in self.cumleler:
            carpim = BIR
            for (ad, pozitif) in cumle:
                deger = atama.get(ad)
                if deger is None:
                    deger = Aralik.degisken(ad)
                carpim = carpim.ve(deger if pozitif else deger.degil())
            sonuc = sonuc.veya(carpim)
        return sonuc

    def degiskenler(self) -> FrozenSet[str]:
        return frozenset(ad for cumle in self.cumleler for (ad, _) in cumle)

    def sifir_mi(self) -> bool:
        return len(self.cumleler) == 0

    def bir_mi(self) -> bool:
        return frozenset() in self.cumleler

    def __eq__(self, obur: object) -> bool:
        return isinstance(obur, Aralik) and self.cumleler == obur.cumleler

    def __hash__(self) -> int:
        return hash(self.cumleler)

    def __repr__(self) -> str:
        if self.sifir_mi():
            return "0"
        if self.bir_mi():
            return "1"
        def cumle_yaz(c: Cumle) -> str:
            parcalar = sorted(("%s" % ad) if p else ("~%s" % ad) for (ad, p) in c)
            return "∧".join(parcalar)
        return "∨".join(sorted(cumle_yaz(c) for c in self.cumleler))


SIFIR = Aralik([])


BIR = Aralik([frozenset()])


def yonlu_hom(A: Terim, x: Terim, y: Terim) -> Terim:
    return YonluHom(A, x, y)


def yonlu_mertebe(X: Terim, n: int) -> Terim:
    if int(n) <= 0:
        return X
    a, b = terim_taze("a"), terim_taze("b")
    return Pi(a, X, Pi(b, X,
                       yonlu_mertebe(yonlu_hom(X, Deg(a), Deg(b)),
                                     int(n) - 1)))


def yonlu_sarti(X: Terim, r: int, n: int) -> Terim:
    taban = X if int(r) <= 0 else carpim(globuler_tip(int(r)), X)
    return yonlu_mertebe(taban, max(0, int(n)))


Yuz = FrozenSet[Tuple[str, bool]]


def _yuz_celiskili_mi(yuz: Yuz) -> bool:
    gorulen: Dict[str, bool] = {}
    for (ad, deger) in yuz:
        if ad in gorulen and gorulen[ad] != deger:
            return True
        gorulen[ad] = deger
    return False


class Kofibrasyon:

    __slots__ = ("yuzler",)

    def __init__(self, yuzler: Iterable[Yuz]) -> None:
        temiz = [frozenset(y) for y in yuzler if not _yuz_celiskili_mi(frozenset(y))]
        self.yuzler: FrozenSet[Yuz] = _antizincire_indir(temiz)

    @staticmethod
    def atom(ad: str, deger: bool) -> "Kofibrasyon":
        return Kofibrasyon([frozenset({(ad, deger)})])

    def ve(self, obur: "Kofibrasyon") -> "Kofibrasyon":
        return Kofibrasyon(a | b for a in self.yuzler for b in obur.yuzler)

    def veya(self, obur: "Kofibrasyon") -> "Kofibrasyon":
        return Kofibrasyon(self.yuzler | obur.yuzler)

    def bos_mu(self) -> bool:
        return len(self.yuzler) == 0

    def dogru_mu(self) -> bool:
        return frozenset() in self.yuzler

    def kapsiyor_mu(self, yuz: Yuz) -> bool:
        yuz = frozenset(yuz)
        return any(c <= yuz for c in self.yuzler)

    def yerine_koy(self, atama: Dict[str, Aralik]) -> "Kofibrasyon":
        if not atama:
            return self
        sonuc = YANLIS
        for yuz in self.yuzler:
            carpim = DOGRU
            for (ad, deger) in yuz:
                r = atama.get(ad)
                if r is None:
                    carpim = carpim.ve(Kofibrasyon.atom(ad, deger))
                else:
                    carpim = carpim.ve(aralik_esitligi(r, deger))
            sonuc = sonuc.veya(carpim)
        return sonuc

    def __eq__(self, obur: object) -> bool:
        return isinstance(obur, Kofibrasyon) and self.yuzler == obur.yuzler

    def __hash__(self) -> int:
        return hash(self.yuzler)

    def __repr__(self) -> str:
        if self.bos_mu():
            return "⊥"
        if self.dogru_mu():
            return "⊤"
        def yuz_yaz(y: Yuz) -> str:
            return "∧".join(sorted("(%s=%d)" % (ad, 1 if d else 0) for (ad, d) in y))
        return "∨".join(sorted(yuz_yaz(y) for y in self.yuzler))


YANLIS = Kofibrasyon([])


DOGRU = Kofibrasyon([frozenset()])


def aralik_esitligi(r: Aralik, deger: bool) -> Kofibrasyon:
    if deger:
        sonuc = YANLIS
        for cumle in r.cumleler:
            carpim = DOGRU
            for (ad, pozitif) in cumle:
                carpim = carpim.ve(Kofibrasyon.atom(ad, pozitif))
            sonuc = sonuc.veya(carpim)
        return sonuc
    sonuc = DOGRU
    for cumle in r.cumleler:
        ayrik = YANLIS
        for (ad, pozitif) in cumle:
            ayrik = ayrik.veya(Kofibrasyon.atom(ad, not pozitif))
        sonuc = sonuc.ve(ayrik)
    return sonuc


def yuzu_atamaya_cevir(yuz: Yuz) -> Dict[str, Aralik]:
    return {ad: (BIR if deger else SIFIR) for (ad, deger) in yuz}


Yuz = FrozenSet[Tuple[str, bool]]


class Dugum:

    __slots__ = ()

    def _alanlar(self) -> tuple:
        return tuple(getattr(self, a) for a in self.__slots__)

    def __eq__(self, obur: object) -> bool:
        return type(self) is type(obur) and self._alanlar() == obur._alanlar()

    def __hash__(self) -> int:
        return hash((type(self).__name__, self._alanlar()))

    def __repr__(self) -> str:
        try:
            return terimi_yaz(self)
        except Exception:
            return "%s(%s)" % (type(self).__name__,
                               ", ".join(repr(a) for a in self._alanlar()))


class Terim(Dugum):
    __slots__ = ()


class Deg(Terim):
    __slots__ = ("ad",)

    def __init__(self, ad: str) -> None:
        self.ad = ad


class Evren(Terim):
    __slots__ = ("seviye",)

    def __init__(self, seviye: int = 0) -> None:
        self.seviye = seviye


class Pi(Terim):
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


class YolP(Terim):
    __slots__ = ("ad", "cizgi", "sol", "sag")

    def __init__(self, ad: str, cizgi: Terim, sol: Terim, sag: Terim) -> None:
        self.ad, self.cizgi, self.sol, self.sag = ad, cizgi, sol, sag


class YonluHom(Terim):
    __slots__ = ("cizgi", "kaynak", "hedef")

    def __init__(self, cizgi: Terim, kaynak: Terim, hedef: Terim) -> None:
        self.cizgi, self.kaynak, self.hedef = cizgi, kaynak, hedef


class YonluOk(Terim):
    __slots__ = ("cizgi", "kaynak", "hedef", "etiket")

    def __init__(self, cizgi: Terim, kaynak: Terim, hedef: Terim,
                 etiket: str = "ok") -> None:
        self.cizgi, self.kaynak, self.hedef, self.etiket = (
            cizgi, kaynak, hedef, etiket)


class YonluTerkip(Terim):
    __slots__ = ("f", "g")

    def __init__(self, f: Terim, g: Terim) -> None:
        self.f, self.g = f, g


class OperadAgac(Terim):
    __slots__ = ("cizgi", "oncutler", "hedef", "etiket")

    def __init__(self, cizgi: Terim, oncutler: Sequence[Terim], hedef: Terim,
                 etiket: str = "korolla") -> None:
        self.cizgi = cizgi
        self.oncutler = tuple(oncutler)
        self.hedef = hedef
        self.etiket = etiket


class OperadHom(Terim):
    __slots__ = ("cizgi", "oncutler", "hedef")

    def __init__(self, cizgi: Terim, oncutler: Sequence[Terim],
                 hedef: Terim) -> None:
        self.cizgi = cizgi
        self.oncutler = tuple(oncutler)
        self.hedef = hedef


class OperadSilsile(Terim):
    __slots__ = ("cizgi", "baslangic_oncutler", "adimlar", "nihai_hedef")

    def __init__(self, cizgi: Terim, baslangic_oncutler: Sequence[Terim],
                 adimlar: Sequence[Tuple[Terim, Terim]], nihai_hedef: Terim) -> None:
        self.cizgi = cizgi
        self.baslangic_oncutler = tuple(baslangic_oncutler)
        self.adimlar = tuple(adimlar)
        self.nihai_hedef = nihai_hedef


class YolLam(Terim):
    __slots__ = ("ad", "govde")

    def __init__(self, ad: str, govde: Terim) -> None:
        self.ad, self.govde = ad, govde


class YolUygula(Terim):
    __slots__ = ("yol", "r")

    def __init__(self, yol: Terim, r: Aralik) -> None:
        self.yol, self.r = yol, r


class Transp(Terim):
    __slots__ = ("ad", "cizgi", "kof", "u0")

    def __init__(self, ad: str, cizgi: Terim, kof: Kofibrasyon, u0: Terim) -> None:
        self.ad, self.cizgi, self.kof, self.u0 = ad, cizgi, kof, u0


class Komp(Terim):
    __slots__ = ("ad", "cizgi", "dallar", "u0")

    def __init__(self, ad: str, cizgi: Terim,
                 dallar: Sequence[Tuple[Yuz, Terim]], u0: Terim) -> None:
        self.ad, self.cizgi = ad, cizgi
        self.dallar = tuple((frozenset(y), t) for (y, t) in dallar)
        self.u0 = u0


class HKomp(Terim):
    __slots__ = ("tip", "ad", "dallar", "u0")

    def __init__(self, tip: Terim, ad: str,
                 dallar: Sequence[Tuple[Yuz, Terim]], u0: Terim) -> None:
        self.tip, self.ad = tip, ad
        self.dallar = tuple((frozenset(y), t) for (y, t) in dallar)
        self.u0 = u0


class Yapistir(Terim):
    __slots__ = ("taban", "dallar")

    def __init__(self, taban: Terim,
                 dallar: Sequence[Tuple[Yuz, Terim, Terim]]) -> None:
        self.taban = taban
        self.dallar = tuple((frozenset(y), t, e) for (y, t, e) in dallar)


class YapistirTerim(Terim):
    __slots__ = ("dallar", "taban_terim")

    def __init__(self, dallar: Sequence[Tuple[Yuz, Terim]],
                 taban_terim: Terim) -> None:
        self.dallar = tuple((frozenset(y), t) for (y, t) in dallar)
        self.taban_terim = taban_terim


class Coz(Terim):
    __slots__ = ("taban", "dallar", "govde")

    def __init__(self, taban: Terim,
                 dallar: Sequence[Tuple[Yuz, Terim, Terim]],
                 govde: Terim) -> None:
        self.taban = taban
        self.dallar = tuple((frozenset(y), t, e) for (y, t, e) in dallar)
        self.govde = govde


class Dogal(Terim):
    __slots__ = ()


class Sfr(Terim):
    __slots__ = ()


class Ard(Terim):
    __slots__ = ("alt",)

    def __init__(self, alt: Terim) -> None:
        self.alt = alt

    def __eq__(self, obur: object) -> bool:
        a, b = self, obur
        while isinstance(a, Ard) and isinstance(b, Ard):
            a, b = a.alt, b.alt
        if isinstance(a, Ard) or isinstance(b, Ard):
            return False
        return a == b

    def __hash__(self) -> int:
        derinlik = 0
        t: Terim = self
        while isinstance(t, Ard):
            derinlik += 1
            t = t.alt
        return hash(("Ard", derinlik, t))


class Belirtec(Terim):
    __slots__ = ("id_no", "basamaklar")

    def __init__(self, id_no: int, basamaklar: Optional[Tuple[int, ...]] = None) -> None:
        self.id_no = int(id_no)
        self.basamaklar = basamaklar or (self.id_no,)

    def __eq__(self, obur: object) -> bool:
        return isinstance(obur, Belirtec) and self.id_no == obur.id_no

    def __hash__(self) -> int:
        return hash(self.id_no)


class DogalInd(Terim):
    __slots__ = ("ad", "hedef", "sfr_dali", "n_ad", "rec_ad", "ard_dali", "sayi")

    def __init__(self, ad: str, hedef: Terim, sfr_dali: Terim,
                 n_ad: str, rec_ad: str, ard_dali: Terim, sayi: Terim) -> None:
        self.ad, self.hedef, self.sfr_dali = ad, hedef, sfr_dali
        self.n_ad, self.rec_ad, self.ard_dali = n_ad, rec_ad, ard_dali
        self.sayi = sayi


class Tamsayi(Terim):
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
    __slots__ = ("ad", "hedef", "poz_ad", "poz_dali", "neg_ad", "neg_dali", "sayi")

    def __init__(self, ad: str, hedef: Terim, poz_ad: str, poz_dali: Terim,
                 neg_ad: str, neg_dali: Terim, sayi: Terim) -> None:
        self.ad, self.hedef = ad, hedef
        self.poz_ad, self.poz_dali = poz_ad, poz_dali
        self.neg_ad, self.neg_dali = neg_ad, neg_dali
        self.sayi = sayi


class Cember(Terim):
    __slots__ = ()


class Taban(Terim):
    __slots__ = ()


class Dongu(Terim):
    __slots__ = ("r",)

    def __init__(self, r: Aralik) -> None:
        self.r = r


class CemberInd(Terim):
    __slots__ = ("ad", "hedef", "taban_dali", "i_ad", "dongu_dali", "nokta")

    def __init__(self, ad: str, hedef: Terim, taban_dali: Terim,
                 i_ad: str, dongu_dali: Terim, nokta: Terim) -> None:
        self.ad, self.hedef, self.taban_dali = ad, hedef, taban_dali
        self.i_ad, self.dongu_dali, self.nokta = i_ad, dongu_dali, nokta


class Suspansiyon(Terim):
    __slots__ = ("taban_uzay",)

    def __init__(self, taban_uzay: Terim) -> None:
        self.taban_uzay = taban_uzay


class KuzeyKutup(Terim):
    __slots__ = ("uzay",)

    def __init__(self, uzay: Terim) -> None:
        self.uzay = uzay


class GuneyKutup(Terim):
    __slots__ = ("uzay",)

    def __init__(self, uzay: Terim) -> None:
        self.uzay = uzay


class Meridyen(Terim):
    __slots__ = ("uzay", "nokta", "i_aralik")

    def __init__(self, uzay: Terim, nokta: Terim, i_aralik: Aralik) -> None:
        self.uzay, self.nokta, self.i_aralik = uzay, nokta, i_aralik


def kure_n(boyut: int) -> Terim:
    if boyut <= 0:
        return Dogal()
    if boyut == 1:
        return Cember()
    return Suspansiyon(kure_n(boyut - 1))


def yuz(**kisitlar: int) -> Yuz:
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
    return Pi("_", alan, hedef)


def carpim(sol: Terim, sag: Terim) -> Terim:
    return Sigma("_", sol, sag)


def dogal_sayi_peano(n: int) -> Terim:
    t: Terim = Sfr()
    for _ in range(n):
        t = Ard(t)
    return t


def tam_sayi(n: int) -> Terim:
    if n >= 0:
        return Poz(dogal_sayi_peano(n))
    return NegArd(dogal_sayi_peano(-n - 1))


def taban_acilimi(token_id: int, veri_lifi: int = 8,
                  basamak_sayisi: int = 6) -> Tuple[int, ...]:
    val = int(token_id)
    d = int(veri_lifi)
    basamaklar = []
    for _ in range(basamak_sayisi):
        basamaklar.append(val % d)
        val //= d
    return tuple(basamaklar)


def dogal_sayi(n: int, veri_lifi: int = 8) -> Terim:
    return Belirtec(int(n), taban_acilimi(n, veri_lifi=veri_lifi))


def yol(tip: Terim, sol: Terim, sag: Terim) -> Terim:
    return YolP("_", tip, sol, sag)


def refl(terim: Terim) -> Terim:
    return YolLam("_", terim)


terim__sayac = itertools.count()


def terim_taze(taban: str = "x") -> str:
    return "%s!%d" % (taban.split("!")[0], next(terim__sayac))


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
        if isinstance(t, (Deg, Evren, Dogal, Tamsayi, Cember,
                          Taban, Sfr, Belirtec)):
            return
        if isinstance(t, Dongu):
            g.update(t.r.degiskenler() - bagli); return
        if isinstance(t, YolUygula):
            yur(t.yol, bagli); g.update(t.r.degiskenler() - bagli); return
        if isinstance(t, YolLam):
            yur(t.govde, bagli | {t.ad}); return
        if isinstance(t, YonluHom):
            yur(t.cizgi, bagli); yur(t.kaynak, bagli); yur(t.hedef, bagli)
            return
        if isinstance(t, YolP):
            yur(t.cizgi, bagli | {t.ad}); yur(t.sol, bagli); yur(t.sag, bagli)
            return
        if isinstance(t, Transp):
            yur(t.cizgi, bagli | {t.ad})
            for f in t.kof.yuzler:
                yuz_ekle(f, bagli)
            yur(t.u0, bagli); return
        if isinstance(t, Komp):
            yur(t.cizgi, bagli | {t.ad})
            for (f, govde) in t.dallar:
                yuz_ekle(f, bagli); yur(govde, bagli | {t.ad})
            yur(t.u0, bagli); return
        if isinstance(t, HKomp):
            yur(t.tip, bagli)
            for (f, govde) in t.dallar:
                yuz_ekle(f, bagli); yur(govde, bagli | {t.ad})
            yur(t.u0, bagli); return
        if isinstance(t, Yapistir):
            yur(t.taban, bagli)
            for (f, T, e) in t.dallar:
                yuz_ekle(f, bagli); yur(T, bagli); yur(e, bagli)
            return
        if isinstance(t, YapistirTerim):
            yur(t.taban_terim, bagli)
            for (f, govde) in t.dallar:
                yuz_ekle(f, bagli); yur(govde, bagli)
            return
        if isinstance(t, Coz):
            yur(t.taban, bagli)
            for (f, T, e) in t.dallar:
                yuz_ekle(f, bagli); yur(T, bagli); yur(e, bagli)
            yur(t.govde, bagli); return
        if isinstance(t, CemberInd):
            yur(t.hedef, bagli); yur(t.taban_dali, bagli)
            yur(t.dongu_dali, bagli | {t.i_ad}); yur(t.nokta, bagli); return
        for alt in _alt(t):
            yur(alt, bagli)

    yur(t, set())
    if len(_ara_serbest_onb) < 300000:
        _ara_serbest_onb[t] = g
    return g


def _alt(t: Terim) -> List[Terim]:
    if isinstance(t, YonluHom):
        return [t.cizgi, t.kaynak, t.hedef]
    if isinstance(t, YonluOk):
        return [t.cizgi, t.kaynak, t.hedef]
    if isinstance(t, YonluTerkip):
        return [t.f, t.g]
    if isinstance(t, OperadAgac):
        return [t.cizgi] + list(t.oncutler) + [t.hedef]
    if isinstance(t, OperadHom):
        return [t.cizgi] + list(t.oncutler) + [t.hedef]
    if isinstance(t, OperadSilsile):
        altlar = [t.cizgi] + list(t.baslangic_oncutler) + [t.nihai_hedef]
        for a, b in t.adimlar:
            altlar.extend([a, b])
        return altlar
    if isinstance(t, (Pi, Sigma)):
        return [t.alan, t.hedef]
    if isinstance(t, Lam):
        return [t.govde]
    if isinstance(t, Uygula):
        return [t.fonk, t.arg]
    if isinstance(t, Cift):
        return [t.bir, t.iki]
    if isinstance(t, (Birinci, Ikinci)):
        return [t.cift]
    if isinstance(t, (Ard, Poz, NegArd)):
        return [t.alt]
    if isinstance(t, DogalInd):
        return [t.hedef, t.sfr_dali, t.ard_dali, t.sayi]
    if isinstance(t, TamsayiInd):
        return [t.hedef, t.poz_dali, t.neg_dali, t.sayi]
    return []


def terim_uygula(fonk: Terim, arg: Terim) -> Terim:
    if isinstance(fonk, Lam):
        return ikame(fonk.govde, {fonk.ad: arg})
    return Uygula(fonk, arg)


def birinci(c: Terim) -> Terim:
    return c.bir if isinstance(c, Cift) else Birinci(c)


def ikinci(c: Terim) -> Terim:
    return c.iki if isinstance(c, Cift) else Ikinci(c)


def terim_yol_uygula(p: Terim, r: Aralik) -> Terim:
    if isinstance(p, YolLam):
        return ara_ikame(p.govde, {p.ad: r})
    return YolUygula(p, r)


def terim_uygula_hepsi(f: Terim, *args: Terim) -> Terim:
    for a in args:
        f = terim_uygula(f, a)
    return f


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
    if isinstance(t, (Deg, Evren, Dogal, Tamsayi, Cember,
                      Taban, Sfr, Belirtec)):
        return t
    if isinstance(t, Dongu):
        r = t.r.yerine_koy(sigma)
        return Taban() if (r.sifir_mi() or r.bir_mi()) else Dongu(r)
    if isinstance(t, YolUygula):
        return terim_yol_uygula(f(t.yol), t.r.yerine_koy(sigma))
    if isinstance(t, YonluHom):
        return YonluHom(f(t.cizgi), f(t.kaynak), f(t.hedef))
    if isinstance(t, YonluOk):
        return YonluOk(f(t.cizgi), f(t.kaynak), f(t.hedef), t.etiket)
    if isinstance(t, YonluTerkip):
        return YonluTerkip(f(t.f), f(t.g))
    if isinstance(t, OperadAgac):
        return OperadAgac(f(t.cizgi), [f(x) for x in t.oncutler],
                          f(t.hedef), t.etiket)
    if isinstance(t, OperadHom):
        return OperadHom(f(t.cizgi), [f(x) for x in t.oncutler], f(t.hedef))
    if isinstance(t, Pi):
        return Pi(t.ad, f(t.alan), f(t.hedef))
    if isinstance(t, Sigma):
        return Sigma(t.ad, f(t.alan), f(t.hedef))
    if isinstance(t, Lam):
        return Lam(t.ad, f(t.govde))
    if isinstance(t, Uygula):
        return terim_uygula(f(t.fonk), f(t.arg))
    if isinstance(t, Cift):
        return Cift(f(t.bir), f(t.iki))
    if isinstance(t, Birinci):
        return birinci(f(t.cift))
    if isinstance(t, Ikinci):
        return ikinci(f(t.cift))
    if isinstance(t, Ard):
        return Ard(f(t.alt))
    if isinstance(t, Poz):
        return Poz(f(t.alt))
    if isinstance(t, NegArd):
        return NegArd(f(t.alt))
    if isinstance(t, YolLam):
        yeni = terim_taze(t.ad)
        return YolLam(yeni, f(ara_ikame(t.govde,
                                          {t.ad: Aralik.degisken(yeni)})))
    if isinstance(t, YolP):
        yeni = terim_taze(t.ad)
        return YolP(yeni, f(ara_ikame(t.cizgi, {t.ad: Aralik.degisken(yeni)})),
                      f(t.sol), f(t.sag))
    if isinstance(t, Transp):
        yeni = terim_taze(t.ad)
        return Transp(yeni, f(ara_ikame(t.cizgi, {t.ad: Aralik.degisken(yeni)})),
                        t.kof.yerine_koy(sigma), f(t.u0))
    if isinstance(t, Komp):
        yeni = terim_taze(t.ad)
        ic = {t.ad: Aralik.degisken(yeni)}
        return Komp(yeni, f(ara_ikame(t.cizgi, ic)),
                      _dallar_ara_ikame(t.dallar, sigma,
                                        lambda g: f(ara_ikame(g, ic))),
                      f(t.u0))
    if isinstance(t, HKomp):
        yeni = terim_taze(t.ad)
        ic = {t.ad: Aralik.degisken(yeni)}
        return HKomp(f(t.tip), yeni,
                       _dallar_ara_ikame(t.dallar, sigma,
                                         lambda g: f(ara_ikame(g, ic))),
                       f(t.u0))
    if isinstance(t, Yapistir):
        dallar = _dallar_ara_ikame(t.dallar, sigma, f)
        for (y, T, _e) in dallar:
            if not y:
                return T
        return Yapistir(f(t.taban), dallar) if dallar else f(t.taban)
    if isinstance(t, YapistirTerim):
        dallar = _dallar_ara_ikame(t.dallar, sigma, f)
        for (y, g) in dallar:
            if not y:
                return g
        return (YapistirTerim(dallar, f(t.taban_terim)) if dallar
                else f(t.taban_terim))
    if isinstance(t, Coz):
        dallar = _dallar_ara_ikame(t.dallar, sigma, f)
        govde = f(t.govde)
        for (y, _T, e) in dallar:
            if not y:
                return terim_uygula(birinci(e), govde)
        return Coz(f(t.taban), dallar, govde) if dallar else govde
    if isinstance(t, DogalInd):
        return DogalInd(t.ad, f(t.hedef), f(t.sfr_dali), t.n_ad, t.rec_ad,
                          f(t.ard_dali), f(t.sayi))
    if isinstance(t, TamsayiInd):
        return TamsayiInd(t.ad, f(t.hedef), t.poz_ad, f(t.poz_dali),
                            t.neg_ad, f(t.neg_dali), f(t.sayi))
    if isinstance(t, CemberInd):
        yeni = terim_taze(t.i_ad)
        return CemberInd(t.ad, f(t.hedef), f(t.taban_dali), yeni,
                           f(ara_ikame(t.dongu_dali,
                                       {t.i_ad: Aralik.degisken(yeni)})),
                           f(t.nokta))
    if isinstance(t, Suspansiyon):
        return Suspansiyon(f(t.taban_uzay))
    if isinstance(t, KuzeyKutup):
        return KuzeyKutup(f(t.uzay))
    if isinstance(t, GuneyKutup):
        return GuneyKutup(f(t.uzay))
    if isinstance(t, Meridyen):
        r = t.i_aralik.yerine_koy(sigma)
        uzay_f, nokta_f = f(t.uzay), f(t.nokta)
        if r.sifir_mi():
            return KuzeyKutup(uzay_f)
        if r.bir_mi():
            return GuneyKutup(uzay_f)
        return Meridyen(uzay_f, nokta_f, r)
    raise TypeError("ara_ikame: bilinmeyen terim %r" % (t,))


def ikame(t: Terim, sigma: Dict[str, Terim]) -> Terim:
    if not sigma:
        return t
    f = lambda x: ikame(x, sigma)
    if isinstance(t, Deg):
        return sigma.get(t.ad, t)
    if isinstance(t, (Evren, Dogal, Tamsayi, Cember, Taban,
                      Sfr, Dongu, Belirtec)):
        return t

    def bagla(ad, govde):
        yeni = terim_taze(ad)
        return yeni, ikame(govde, {ad: Deg(yeni)})

    if isinstance(t, Pi):
        ad2, gv = bagla(t.ad, t.hedef); return Pi(ad2, f(t.alan), f(gv))
    if isinstance(t, Sigma):
        ad2, gv = bagla(t.ad, t.hedef); return Sigma(ad2, f(t.alan), f(gv))
    if isinstance(t, Lam):
        ad2, gv = bagla(t.ad, t.govde); return Lam(ad2, f(gv))
    if isinstance(t, Uygula):
        return terim_uygula(f(t.fonk), f(t.arg))
    if isinstance(t, Cift):
        return Cift(f(t.bir), f(t.iki))
    if isinstance(t, Birinci):
        return birinci(f(t.cift))
    if isinstance(t, Ikinci):
        return ikinci(f(t.cift))
    if isinstance(t, Ard):
        return Ard(f(t.alt))
    if isinstance(t, Poz):
        return Poz(f(t.alt))
    if isinstance(t, NegArd):
        return NegArd(f(t.alt))
    if isinstance(t, YonluHom):
        return YonluHom(f(t.cizgi), f(t.kaynak), f(t.hedef))
    if isinstance(t, YonluOk):
        return YonluOk(f(t.cizgi), f(t.kaynak), f(t.hedef), t.etiket)
    if isinstance(t, YonluTerkip):
        return YonluTerkip(f(t.f), f(t.g))
    if isinstance(t, OperadAgac):
        return OperadAgac(f(t.cizgi), [f(x) for x in t.oncutler],
                          f(t.hedef), t.etiket)
    if isinstance(t, OperadHom):
        return OperadHom(f(t.cizgi), [f(x) for x in t.oncutler], f(t.hedef))
    if isinstance(t, YolP):
        return YolP(t.ad, f(t.cizgi), f(t.sol), f(t.sag))
    if isinstance(t, YolLam):
        return YolLam(t.ad, f(t.govde))
    if isinstance(t, YolUygula):
        return terim_yol_uygula(f(t.yol), t.r)
    if isinstance(t, Transp):
        return Transp(t.ad, f(t.cizgi), t.kof, f(t.u0))
    if isinstance(t, Komp):
        return Komp(t.ad, f(t.cizgi), [(y, f(g)) for (y, g) in t.dallar],
                      f(t.u0))
    if isinstance(t, HKomp):
        return HKomp(f(t.tip), t.ad, [(y, f(g)) for (y, g) in t.dallar],
                       f(t.u0))
    if isinstance(t, Yapistir):
        return Yapistir(f(t.taban), [(y, f(T), f(e)) for (y, T, e) in t.dallar])
    if isinstance(t, YapistirTerim):
        return YapistirTerim([(y, f(g)) for (y, g) in t.dallar],
                               f(t.taban_terim))
    if isinstance(t, Coz):
        return Coz(f(t.taban), [(y, f(T), f(e)) for (y, T, e) in t.dallar],
                     f(t.govde))
    if isinstance(t, DogalInd):
        ad2, hd = bagla(t.ad, t.hedef)
        n2, r2 = terim_taze(t.n_ad), terim_taze(t.rec_ad)
        ard = ikame(t.ard_dali, {t.n_ad: Deg(n2), t.rec_ad: Deg(r2)})
        return DogalInd(ad2, f(hd), f(t.sfr_dali), n2, r2, f(ard), f(t.sayi))
    if isinstance(t, TamsayiInd):
        ad2, hd = bagla(t.ad, t.hedef)
        p2, n2 = terim_taze(t.poz_ad), terim_taze(t.neg_ad)
        pd = ikame(t.poz_dali, {t.poz_ad: Deg(p2)})
        nd = ikame(t.neg_dali, {t.neg_ad: Deg(n2)})
        return TamsayiInd(ad2, f(hd), p2, f(pd), n2, f(nd), f(t.sayi))
    if isinstance(t, CemberInd):
        ad2, hd = bagla(t.ad, t.hedef)
        return CemberInd(ad2, f(hd), f(t.taban_dali), t.i_ad,
                           f(t.dongu_dali), f(t.nokta))
    if isinstance(t, Suspansiyon):
        return Suspansiyon(f(t.taban_uzay))
    if isinstance(t, KuzeyKutup):
        return KuzeyKutup(f(t.uzay))
    if isinstance(t, GuneyKutup):
        return GuneyKutup(f(t.uzay))
    if isinstance(t, Meridyen):
        return Meridyen(f(t.uzay), f(t.nokta), t.i_aralik)
    raise TypeError("ikame: bilinmeyen terim %r" % (t,))


def terim_transp(ad: str, cizgi: Terim, kof: Kofibrasyon, u0: Terim) -> Terim:
    if kof.dogru_mu():
        return u0
    return Transp(ad, cizgi, kof, u0)


def terim_hkomp(tip: Terim, ad: str, dallar, u0: Terim) -> Terim:
    for (y, g) in dallar:
        if not y:
            return ara_ikame(g, {ad: BIR})
    if not dallar:
        return u0
    return HKomp(tip, ad, dallar, u0)


def terim_komp(ad: str, cizgi: Terim, dallar, u0: Terim) -> Terim:
    for (y, g) in dallar:
        if not y:
            return ara_ikame(g, {ad: BIR})
    if not dallar and ad not in ara_serbest(cizgi):
        return u0
    return Komp(ad, cizgi, dallar, u0)


def terim_dolgu(ad: str, cizgi: Terim, dallar, u0: Terim) -> Terim:
    j = terim_taze("j")
    ikj = {ad: Aralik.degisken(ad).ve(Aralik.degisken(j))}
    yeni_dallar = list(_dallar_ara_ikame(dallar, ikj,
                                         lambda g: ara_ikame(g, ikj)))
    yeni_dallar.append((yuz(**{ad: 0}), u0))
    return terim_komp(j, ara_ikame(cizgi, ikj), yeni_dallar, u0)


_sayac = itertools.count()


def taze(taban: str = "x") -> str:
    return "%s!%d" % (taban.split("!")[0], next(_sayac))


class CekirdekHatasi(Exception):
    pass


class Ortam:

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


class DSuspansiyon(Deger):
    __slots__ = ("taban_uzay",)

    def __init__(self, taban_uzay: Deger) -> None:
        self.taban_uzay = taban_uzay

    def act(self, s):
        return DSuspansiyon(self.taban_uzay.act(s))


class DKuzeyKutup(Deger):
    __slots__ = ("uzay",)

    def __init__(self, uzay: Deger) -> None:
        self.uzay = uzay

    def act(self, s):
        return DKuzeyKutup(self.uzay.act(s))


class DGuneyKutup(Deger):
    __slots__ = ("uzay",)

    def __init__(self, uzay: Deger) -> None:
        self.uzay = uzay

    def act(self, s):
        return DGuneyKutup(self.uzay.act(s))


class DMeridyen(Deger):
    __slots__ = ("uzay", "nokta", "r")

    def __init__(self, uzay: Deger, nokta: Deger, r: Aralik) -> None:
        self.uzay, self.nokta, self.r = uzay, nokta, r

    def act(self, s):
        return deger_meridyen(self.uzay.act(s), self.nokta.act(s),
                              self.r.yerine_koy(s))


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


class DYonluHom(Deger):
    __slots__ = ("cizgi", "kaynak", "hedef")

    def __init__(self, cizgi: Deger, kaynak: Deger, hedef: Deger) -> None:
        self.cizgi, self.kaynak, self.hedef = cizgi, kaynak, hedef

    def act(self, s):
        return DYonluHom(self.cizgi.act(s), self.kaynak.act(s),
                         self.hedef.act(s))


class DYonluOk(Deger):
    __slots__ = ("cizgi", "kaynak", "hedef", "etiket")

    def __init__(self, cizgi: Deger, kaynak: Deger, hedef: Deger,
                 etiket: str = "ok") -> None:
        self.cizgi, self.kaynak, self.hedef, self.etiket = (
            cizgi, kaynak, hedef, etiket)

    def act(self, s):
        return DYonluOk(self.cizgi.act(s), self.kaynak.act(s),
                       self.hedef.act(s), self.etiket)


class DYonluTerkip(Deger):
    __slots__ = ("cizgi", "kaynak", "hedef", "f", "g")

    def __init__(self, cizgi: Deger, kaynak: Deger, hedef: Deger,
                 f: Deger, g: Deger) -> None:
        self.cizgi, self.kaynak, self.hedef, self.f, self.g = (
            cizgi, kaynak, hedef, f, g)

    def act(self, s):
        return DYonluTerkip(_act(self.cizgi, s), _act(self.kaynak, s),
                           _act(self.hedef, s), _act(self.f, s), _act(self.g, s))


class DOperadAgac(Deger):
    __slots__ = ("cizgi", "oncutler", "hedef", "etiket")

    def __init__(self, cizgi: Deger, oncutler: Sequence[Deger], hedef: Deger,
                 etiket: str = "korolla") -> None:
        self.cizgi = cizgi
        self.oncutler = tuple(oncutler)
        self.hedef = hedef
        self.etiket = etiket

    def act(self, s):
        return DOperadAgac(self.cizgi.act(s),
                           tuple(x.act(s) for x in self.oncutler),
                           self.hedef.act(s), self.etiket)


class DOperadHom(Deger):
    __slots__ = ("cizgi", "oncutler", "hedef")

    def __init__(self, cizgi: Deger, oncutler: Sequence[Deger],
                 hedef: Deger) -> None:
        self.cizgi = cizgi
        self.oncutler = tuple(oncutler)
        self.hedef = hedef

    def act(self, s):
        return DOperadHom(self.cizgi.act(s),
                          tuple(x.act(s) for x in self.oncutler),
                          self.hedef.act(s))


class DOperadSilsile(Deger):
    __slots__ = ("cizgi", "baslangic_oncutler", "adimlar", "nihai_hedef")

    def __init__(self, cizgi: Deger, baslangic_oncutler: Sequence[Deger],
                 adimlar: tuple, nihai_hedef: Deger) -> None:
        self.cizgi = cizgi
        self.baslangic_oncutler = tuple(baslangic_oncutler)
        self.adimlar = adimlar
        self.nihai_hedef = nihai_hedef

    def act(self, s):
        return DOperadSilsile(_act(self.cizgi, s),
                              tuple(_act(x, s) for x in self.baslangic_oncutler),
                              tuple((_act(a, s), _act(b, s)) for a, b in self.adimlar),
                              _act(self.nihai_hedef, s))


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


class DBelirtec(Deger):
    __slots__ = ("id_no", "basamaklar")

    def __init__(self, id_no: int, basamaklar: Tuple[int, ...]) -> None:
        self.id_no = int(id_no)
        self.basamaklar = basamaklar

    def act(self, s):
        return self


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
    __slots__ = ("r",)

    def __init__(self, r: Aralik) -> None:
        self.r = r

    def act(self, s):
        return deger_dongu(self.r.yerine_koy(s))


class DYapistir(Deger):
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
    yeni = []
    for dal in dallar:
        k = Kofibrasyon([dal[0]]).yerine_koy(s)
        if k.bos_mu():
            continue
        geri = tuple(_act(x, s) for x in dal[1:])
        for f in k.yuzler:
            yeni.append((f,) + geri)
    return tuple(yeni)


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


class Kapanis:
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
    __slots__ = ("fn", "alanlar")

    def __init__(self, fn: Callable, alanlar: tuple) -> None:
        self.fn, self.alanlar = fn, alanlar

    def uygula(self, d):
        return self.fn(self.alanlar, d)

    def act(self, s):
        return KTuretilmis(self.fn, tuple(_act(a, s) for a in self.alanlar))


class Kapanis2:
    __slots__ = ("ad1", "ad2", "terim", "ortam")

    def __init__(self, ad1: str, ad2: str, terim: Terim, ortam: Ortam) -> None:
        self.ad1, self.ad2, self.terim, self.ortam = ad1, ad2, terim, ortam

    def uygula(self, a: Deger, b: Deger) -> Deger:
        return degerlendir(self.terim,
                           self.ortam.genislet(self.ad1, a).genislet(self.ad2, b))

    def act(self, s):
        return Kapanis2(self.ad1, self.ad2, self.terim, self.ortam.act(s))


class ACizgi:
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
    __slots__ = ("fn", "alanlar")

    def __init__(self, fn: Callable, alanlar: tuple) -> None:
        self.fn, self.alanlar = fn, alanlar

    def uygula(self, r):
        return self.fn(self.alanlar, r)

    def act(self, s):
        return ATuretilmis(self.fn, tuple(_act(a, s) for a in self.alanlar))


class AYeniden(ACizgi):
    __slots__ = ("alt", "ad", "ifade")

    def __init__(self, alt: ACizgi, ad: str, ifade: Aralik) -> None:
        self.alt, self.ad, self.ifade = alt, ad, ifade

    def uygula(self, r):
        return self.alt.uygula(self.ifade.yerine_koy({self.ad: r}))

    def act(self, s):
        s2 = {k: v for k, v in s.items() if k != self.ad}
        return AYeniden(self.alt.act(s), self.ad, self.ifade.yerine_koy(s2))


class Sistem:

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
    d = DNotr(n, tip)
    if isinstance(tip, DPi):
        return DLam(KTuretilmis(_eta_pi, (d, tip)))
    if isinstance(tip, DSigma):
        b = notr(NBir(d), tip.alan)
        return DCift(b, notr(NIki(d), tip.kap.uygula(b)))
    if isinstance(tip, DYolP):
        return DYolLam(ATuretilmis(_eta_yol, (d, tip)))
    return d


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


def deger_dongu(r: Aralik) -> Deger:
    if r.sifir_mi() or r.bir_mi():
        return DTaban()
    return DDongu(r)


def deger_meridyen(uzay: Deger, nokta: Deger, r: Aralik) -> Deger:
    if r.sifir_mi():
        return DKuzeyKutup(uzay)
    if r.bir_mi():
        return DGuneyKutup(uzay)
    return DMeridyen(uzay, nokta, r)


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


def _sabit_mi(L: ACizgi) -> bool:
    if isinstance(L, ASabit):
        return True
    if isinstance(L, ASoz):
        return L.ad not in ara_serbest(L.terim)
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
        return komp_evren(L, sistem, u0)

    if isinstance(A, DYapistir):
        return komp_yapistir(L, sistem, u0)

    return notr(NKomp(L, sistem, u0), L.uygula(BIR))


def _sistem_kur(dallar, ad: str, ortam: Ortam) -> Sistem:
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
    if isinstance(t, YonluHom):
        return DYonluHom(degerlendir(t.cizgi, ortam),
                         degerlendir(t.kaynak, ortam),
                         degerlendir(t.hedef, ortam))
    if isinstance(t, YonluOk):
        return DYonluOk(degerlendir(t.cizgi, ortam), degerlendir(t.kaynak, ortam),
                        degerlendir(t.hedef, ortam), t.etiket)
    if isinstance(t, YonluTerkip):
        fv = degerlendir(t.f, ortam)
        gv = degerlendir(t.g, ortam)
        cizgi = getattr(fv, "cizgi", DEvren(0))
        kaynak = getattr(fv, "kaynak", getattr(fv, "oncutler", DEvren(0)))
        hedef = getattr(gv, "hedef", DEvren(0))
        return DYonluTerkip(cizgi, kaynak, hedef, fv, gv)
    if isinstance(t, OperadAgac):
        return DOperadAgac(degerlendir(t.cizgi, ortam),
                           tuple(degerlendir(x, ortam) for x in t.oncutler),
                           degerlendir(t.hedef, ortam), t.etiket)
    if isinstance(t, OperadHom):
        return DOperadHom(degerlendir(t.cizgi, ortam),
                          tuple(degerlendir(x, ortam) for x in t.oncutler),
                          degerlendir(t.hedef, ortam))
    if isinstance(t, OperadSilsile):
        return DOperadSilsile(
            degerlendir(t.cizgi, ortam),
            tuple(degerlendir(x, ortam) for x in t.baslangic_oncutler),
            tuple((degerlendir(a, ortam), degerlendir(b, ortam))
                  for a, b in t.adimlar),
            degerlendir(t.nihai_hedef, ortam))
    if isinstance(t, Deg):
        v = ortam.terimler.get(t.ad)
        if v is None:
            raise CekirdekHatasi("bağlı olmayan değişken: %s" % t.ad)
        return v
    if isinstance(t, Evren):
        return DEvren(t.seviye)
    if isinstance(t, Pi):
        return DPi(degerlendir(t.alan, ortam), KSoz(t.ad, t.hedef, ortam))
    if isinstance(t, Sigma):
        return DSigma(degerlendir(t.alan, ortam), KSoz(t.ad, t.hedef, ortam))
    if isinstance(t, Lam):
        return DLam(KSoz(t.ad, t.govde, ortam))
    if isinstance(t, Uygula):
        return uygula(degerlendir(t.fonk, ortam), degerlendir(t.arg, ortam))
    if isinstance(t, Cift):
        return DCift(degerlendir(t.bir, ortam), degerlendir(t.iki, ortam))
    if isinstance(t, Birinci):
        return bir(degerlendir(t.cift, ortam))
    if isinstance(t, Ikinci):
        return iki(degerlendir(t.cift, ortam))
    if isinstance(t, YolP):
        return DYolP(ASoz(t.ad, t.cizgi, ortam),
                     degerlendir(t.sol, ortam), degerlendir(t.sag, ortam))
    if isinstance(t, YolLam):
        return DYolLam(ASoz(t.ad, t.govde, ortam))
    if isinstance(t, YolUygula):
        return yol_uygula(degerlendir(t.yol, ortam),
                          t.r.yerine_koy(ortam.araliklar))
    if isinstance(t, Dogal):
        return DDogal()
    if isinstance(t, Sfr):
        return DSfr()
    if isinstance(t, Ard):
        return DArd(degerlendir(t.alt, ortam))
    if isinstance(t, Belirtec):
        return DBelirtec(t.id_no, t.basamaklar)
    if isinstance(t, Tamsayi):
        return DTamsayi()
    if isinstance(t, Poz):
        return DPoz(degerlendir(t.alt, ortam))
    if isinstance(t, NegArd):
        return DNegArd(degerlendir(t.alt, ortam))
    if isinstance(t, Cember):
        return DCember()
    if isinstance(t, Taban):
        return DTaban()
    if isinstance(t, Dongu):
        return deger_dongu(t.r.yerine_koy(ortam.araliklar))
    if isinstance(t, DogalInd):
        return dogal_ind(KSoz(t.ad, t.hedef, ortam),
                         degerlendir(t.sfr_dali, ortam),
                         Kapanis2(t.n_ad, t.rec_ad, t.ard_dali, ortam),
                         degerlendir(t.sayi, ortam))
    if isinstance(t, TamsayiInd):
        return tamsayi_ind(KSoz(t.ad, t.hedef, ortam),
                           KSoz(t.poz_ad, t.poz_dali, ortam),
                           KSoz(t.neg_ad, t.neg_dali, ortam),
                           degerlendir(t.sayi, ortam))
    if isinstance(t, CemberInd):
        return cember_ind(KSoz(t.ad, t.hedef, ortam),
                          degerlendir(t.taban_dali, ortam),
                          ASoz(t.i_ad, t.dongu_dali, ortam),
                          degerlendir(t.nokta, ortam))
    if isinstance(t, Transp):
        return transp(ASoz(t.ad, t.cizgi, ortam),
                      t.kof.yerine_koy(ortam.araliklar),
                      degerlendir(t.u0, ortam))
    if isinstance(t, Komp):
        return komp(ASoz(t.ad, t.cizgi, ortam),
                    _sistem_kur(t.dallar, t.ad, ortam),
                    degerlendir(t.u0, ortam))
    if isinstance(t, HKomp):
        return komp(ASabit(degerlendir(t.tip, ortam)),
                    _sistem_kur(t.dallar, t.ad, ortam),
                    degerlendir(t.u0, ortam))
    if isinstance(t, Yapistir):
        return yapistir(degerlendir(t.taban, ortam),
                        _glue_dallari(t.dallar, ortam))
    if isinstance(t, YapistirTerim):
        yeni = []
        for (y, govde) in t.dallar:
            k = Kofibrasyon([y]).yerine_koy(ortam.araliklar)
            if k.bos_mu():
                continue
            gv = degerlendir(govde, ortam)
            for f in k.yuzler:
                yeni.append((f, gv))
        return yapistir_terim(yeni, degerlendir(t.taban_terim, ortam))
    if isinstance(t, Coz):
        return coz(degerlendir(t.taban, ortam),
                   _glue_dallari(t.dallar, ortam),
                   degerlendir(t.govde, ortam))
    if isinstance(t, Suspansiyon):
        return DSuspansiyon(degerlendir(t.taban_uzay, ortam))
    if isinstance(t, KuzeyKutup):
        return DKuzeyKutup(degerlendir(t.uzay, ortam))
    if isinstance(t, GuneyKutup):
        return DGuneyKutup(degerlendir(t.uzay, ortam))
    if isinstance(t, Meridyen):
        return deger_meridyen(degerlendir(t.uzay, ortam),
                              degerlendir(t.nokta, ortam),
                              t.i_aralik.yerine_koy(ortam.araliklar))
    raise CekirdekHatasi("değerlendirilemeyen terim: %r" % (t,))


def _tv(k: int) -> str:
    return "#%d" % k


def _iv(k: int) -> str:
    return "%%%d" % k


def _ivar(k: int) -> Aralik:
    return Aralik.degisken(_iv(k))


def geri_oku(d: Deger, k: int = 0) -> Terim:
    if isinstance(d, DYonluHom):
        return YonluHom(geri_oku(d.cizgi, k), geri_oku(d.kaynak, k),
                        geri_oku(d.hedef, k))
    if isinstance(d, DYonluOk):
        return YonluOk(geri_oku(d.cizgi, k), geri_oku(d.kaynak, k),
                      geri_oku(d.hedef, k), d.etiket)
    if isinstance(d, DYonluTerkip):
        return YonluTerkip(geri_oku(d.f, k), geri_oku(d.g, k))
    if isinstance(d, DOperadAgac):
        return OperadAgac(geri_oku(d.cizgi, k),
                          [geri_oku(x, k) for x in d.oncutler],
                          geri_oku(d.hedef, k), d.etiket)
    if isinstance(d, DOperadHom):
        return OperadHom(geri_oku(d.cizgi, k),
                         [geri_oku(x, k) for x in d.oncutler],
                         geri_oku(d.hedef, k))
    if isinstance(d, DOperadSilsile):
        return OperadSilsile(geri_oku(d.cizgi, k),
                             [geri_oku(x, k) for x in d.baslangic_oncutler],
                             [(geri_oku(a, k), geri_oku(b, k)) for a, b in d.adimlar],
                             geri_oku(d.nihai_hedef, k))
    if isinstance(d, DEvren):
        return Evren(d.seviye)
    if isinstance(d, DDogal):
        return Dogal()
    if isinstance(d, DTamsayi):
        return Tamsayi()
    if isinstance(d, DCember):
        return Cember()
    if isinstance(d, DTaban):
        return Taban()
    if isinstance(d, DSfr):
        return Sfr()
    if isinstance(d, DArd):
        return Ard(geri_oku(d.alt, k))
    if isinstance(d, DBelirtec):
        return Belirtec(d.id_no, d.basamaklar)
    if isinstance(d, DPoz):
        return Poz(geri_oku(d.alt, k))
    if isinstance(d, DNegArd):
        return NegArd(geri_oku(d.alt, k))
    if isinstance(d, DDongu):
        return Dongu(d.r)
    if isinstance(d, DPi):
        v = notr(NDeg(_tv(k), d.alan), d.alan)
        return Pi(_tv(k), geri_oku(d.alan, k), geri_oku(d.kap.uygula(v), k + 1))
    if isinstance(d, DSigma):
        v = notr(NDeg(_tv(k), d.alan), d.alan)
        return Sigma(_tv(k), geri_oku(d.alan, k),
                       geri_oku(d.kap.uygula(v), k + 1))
    if isinstance(d, DLam):
        v = notr(NDeg(_tv(k), None), None)
        return Lam(_tv(k), geri_oku(d.kap.uygula(v), k + 1))
    if isinstance(d, DCift):
        return Cift(geri_oku(d.bir, k), geri_oku(d.iki, k))
    if isinstance(d, DYolP):
        return YolP(_iv(k), geri_oku(d.cizgi.uygula(_ivar(k)), k + 1),
                      geri_oku(d.sol, k), geri_oku(d.sag, k))
    if isinstance(d, DYolLam):
        return YolLam(_iv(k), geri_oku(d.cizgi.uygula(_ivar(k)), k + 1))
    if isinstance(d, DHKomp):
        r = _ivar(k)
        return HKomp(geri_oku(d.tip, k), _iv(k),
                       [(y, geri_oku(c.uygula(r), k + 1))
                        for (y, c) in d.sistem], geri_oku(d.u0, k))
    if isinstance(d, DYapistir):
        return Yapistir(geri_oku(d.taban, k),
                          [(y, geri_oku(T, k), geri_oku(e, k))
                           for (y, T, e) in d.dallar])
    if isinstance(d, DYapistirTerim):
        return YapistirTerim([(y, geri_oku(g, k)) for (y, g) in d.dallar],
                               geri_oku(d.taban, k))
    if isinstance(d, DNotr):
        return _geri_oku_notr(d.n, k)
    if isinstance(d, DSuspansiyon):
        return Suspansiyon(geri_oku(d.taban_uzay, k))
    if isinstance(d, DKuzeyKutup):
        return KuzeyKutup(geri_oku(d.uzay, k))
    if isinstance(d, DGuneyKutup):
        return GuneyKutup(geri_oku(d.uzay, k))
    if isinstance(d, DMeridyen):
        return Meridyen(geri_oku(d.uzay, k), geri_oku(d.nokta, k), d.r)
    raise CekirdekHatasi("geri okunamayan değer: %r" % (d,))


def _geri_oku_notr(n: Notr, k: int) -> Terim:
    if isinstance(n, NDeg):
        return Deg(n.ad)
    if isinstance(n, NUygula):
        return Uygula(geri_oku(n.n, k), geri_oku(n.arg, k))
    if isinstance(n, NBir):
        return Birinci(geri_oku(n.n, k))
    if isinstance(n, NIki):
        return Ikinci(geri_oku(n.n, k))
    if isinstance(n, NYolUygula):
        return YolUygula(geri_oku(n.n, k), n.r)
    if isinstance(n, NKomp):
        r = _ivar(k)
        return Komp(_iv(k), geri_oku(n.cizgi.uygula(r), k + 1),
                      [(y, geri_oku(c.uygula(r), k + 1))
                       for (y, c) in n.sistem], geri_oku(n.u0, k))
    if isinstance(n, NCoz):
        return Coz(geri_oku(n.taban, k),
                     [(y, geri_oku(T, k), geri_oku(e, k))
                      for (y, T, e) in n.dallar], geri_oku(n.govde, k))
    if isinstance(n, NDogalInd):
        v = notr(NDeg(_tv(k), DDogal()), DDogal())
        v1 = notr(NDeg(_tv(k + 1), DDogal()), DDogal())
        v2 = notr(NDeg(_tv(k + 2), None), None)
        return DogalInd(_tv(k), geri_oku(n.motif.uygula(v), k + 1),
                          geri_oku(n.sfr, k), _tv(k + 1), _tv(k + 2),
                          geri_oku(n.ard.uygula(v1, v2), k + 3),
                          geri_oku(n.sayi, k))
    if isinstance(n, NTamsayiInd):
        v = notr(NDeg(_tv(k), DTamsayi()), DTamsayi())
        v1 = notr(NDeg(_tv(k + 1), DDogal()), DDogal())
        return TamsayiInd(_tv(k), geri_oku(n.motif.uygula(v), k + 1),
                            _tv(k + 1), geri_oku(n.poz.uygula(v1), k + 2),
                            _tv(k + 1), geri_oku(n.neg.uygula(v1), k + 2),
                            geri_oku(n.sayi, k))
    if isinstance(n, NCemberInd):
        v = notr(NDeg(_tv(k), DCember()), DCember())
        return CemberInd(_tv(k), geri_oku(n.motif.uygula(v), k + 1),
                           geri_oku(n.taban_dali, k), _iv(k + 1),
                           geri_oku(n.dongu_dali.uygula(_ivar(k + 1)), k + 2),
                           geri_oku(n.nokta, k))
    raise CekirdekHatasi("geri okunamayan nötr: %r" % (n,))


def ortam_kur(baglam: Optional[Dict[str, Terim]] = None) -> Ortam:
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
    if a == b:
        return True
    if isinstance(a, Cift) != isinstance(b, Cift):
        ct, obur = (a, b) if isinstance(a, Cift) else (b, a)
        return (_esit(ct.bir, Birinci(obur), derinlik)
                and _esit(ct.iki, Ikinci(obur), derinlik))
    if isinstance(a, Lam) != isinstance(b, Lam):
        lam, obur = (a, b) if isinstance(a, Lam) else (b, a)
        return _esit(lam.govde, Uygula(obur, Deg(lam.ad)), derinlik + 1)
    if isinstance(a, YolLam) != isinstance(b, YolLam):
        pl, obur = (a, b) if isinstance(a, YolLam) else (b, a)
        return _esit(pl.govde, YolUygula(obur, Aralik.degisken(pl.ad)),
                     derinlik + 1)
    if type(a) is not type(b):
        return False
    if isinstance(a, Cift):
        return (_esit(a.bir, b.bir, derinlik) and _esit(a.iki, b.iki, derinlik))
    if isinstance(a, Uygula):
        return (_esit(a.fonk, b.fonk, derinlik) and _esit(a.arg, b.arg, derinlik))
    if isinstance(a, (Birinci, Ikinci)):
        return _esit(a.cift, b.cift, derinlik)
    if isinstance(a, YonluHom) and isinstance(b, YonluHom):
        return (_esit(a.cizgi, b.cizgi, derinlik) and
                _esit(a.kaynak, b.kaynak, derinlik) and
                _esit(a.hedef, b.hedef, derinlik))
    if isinstance(a, OperadHom) and isinstance(b, OperadHom):
        if len(a.oncutler) != len(b.oncutler):
            return False
        return (_esit(a.cizgi, b.cizgi, derinlik) and
                all(_esit(x, y, derinlik) for x, y in zip(a.oncutler, b.oncutler)) and
                _esit(a.hedef, b.hedef, derinlik))
    if isinstance(a, OperadAgac) and isinstance(b, OperadAgac):
        if len(a.oncutler) != len(b.oncutler) or a.etiket != b.etiket:
            return False
        return (_esit(a.cizgi, b.cizgi, derinlik) and
                all(_esit(x, y, derinlik) for x, y in zip(a.oncutler, b.oncutler)) and
                _esit(a.hedef, b.hedef, derinlik))
    if isinstance(a, YonluOk) and isinstance(b, YonluOk):
        return (_esit(a.cizgi, b.cizgi, derinlik) and
                _esit(a.kaynak, b.kaynak, derinlik) and
                _esit(a.hedef, b.hedef, derinlik) and a.etiket == b.etiket)
    if isinstance(a, YonluTerkip) and isinstance(b, YonluTerkip):
        return _esit(a.f, b.f, derinlik) and _esit(a.g, b.g, derinlik)
    return False


def esdeger_mi(a: Terim, b: Terim,
               baglam: Optional[Dict[str, Terim]] = None) -> bool:
    if a is b:
        return True
    if WHNF_ELEMESI[0] and _bas_ayrisiyor(a, b, baglam):
        _WHNF_SAYAC["eleme"] += 1
        return False
    _WHNF_SAYAC["tam_kıyas"] += 1
    o = ortam_kur(baglam)
    return _esit(geri_oku(degerlendir(a, o), 0),
                 geri_oku(degerlendir(b, o), 0))


def deger_esit_mi(d1: Deger, d2: Deger, k: int = 0) -> bool:
    return _esit(geri_oku(d1, k), geri_oku(d2, k), k)


U = Evren(0)


U1 = Evren(1)


def _t(ad: str) -> Terim:
    return Deg(ad)


def refl(a: Terim) -> Terim:
    return YolLam("_", a)


def ters(A: Terim, a: Terim, b: Terim, p: Terim) -> Terim:
    i, j = terim_taze("i"), terim_taze("j")
    return YolLam(i, HKomp(A, j,
        [(yuz(**{i: 0}), terim_yol_uygula(p, Aralik.degisken(j))),
         (yuz(**{i: 1}), a)], a))


def terkip(A: Terim, a: Terim, b: Terim, c: Terim,
           p: Terim, q: Terim) -> Terim:
    i, j = terim_taze("i"), terim_taze("j")
    return YolLam(i, HKomp(A, j,
        [(yuz(**{i: 0}), a),
         (yuz(**{i: 1}), terim_yol_uygula(q, Aralik.degisken(j)))],
        terim_yol_uygula(p, Aralik.degisken(i))))


def esle(A: Terim, B: Terim, f: Terim, a: Terim, b: Terim, p: Terim) -> Terim:
    i = terim_taze("i")
    return YolLam(i, Uygula(f, terim_yol_uygula(p, Aralik.degisken(i))))


def tasi(P: Terim, x: Terim) -> Terim:
    i = terim_taze("i")
    return Transp(i, terim_yol_uygula(P, Aralik.degisken(i)), YANLIS, x)


def aile_tasi(C: Terim, p: Terim, x: Terim) -> Terim:
    i = terim_taze("i")
    return Transp(i, Uygula(C, terim_yol_uygula(p, Aralik.degisken(i))),
                    YANLIS, x)


def yol_tumevarimi(A: Terim, a: Terim, C: Terim, d: Terim,
                   b: Terim, p: Terim) -> Terim:
    i, j = terim_taze("i"), terim_taze("j")
    i_ar, j_ar = Aralik.degisken(i), Aralik.degisken(j)
    kismi_yol = YolLam(j, terim_yol_uygula(p, i_ar.ve(j_ar)))
    cizgi = Uygula(Uygula(C, terim_yol_uygula(p, i_ar)), kismi_yol)
    return Transp(i, cizgi, YANLIS, d)


def mertebe(X: Terim, n: int = -2) -> Terim:
    if n <= -2:
        x, y = terim_taze("x"), terim_taze("y")
        return Sigma(x, X, Pi(y, X, yol(X, _t(x), _t(y))))
    x, y = terim_taze("x"), terim_taze("y")
    ic = yol(X, _t(x), _t(y))
    return Pi(x, X, Pi(y, X, ic if n == -1 else mertebe(ic, n - 1)))


def dongu_uzayi(A: Terim, a: Terim) -> Terim:
    return yol(A, a, a)


def dongu_uzayi_n(A: Terim, a: Terim, n: int) -> Terim:
    if n <= 0:
        return A
    if n == 1:
        return dongu_uzayi(A, a)
    alt = dongu_uzayi_n(A, a, n - 1)
    return yol(alt, refl_n(A, a, n - 1), refl_n(A, a, n - 1))


def refl_n(A: Terim, a: Terim, n: int) -> Terim:
    nokta = a
    for _ in range(n):
        nokta = refl(nokta)
    return nokta


def lif(A: Terim, B: Terim, f: Terim, b: Terim) -> Terim:
    a = terim_taze("a")
    return Sigma(a, A, yol(B, Uygula(f, _t(a)), b))


def iz_denklik(A: Terim, B: Terim, f: Terim) -> Terim:
    b = terim_taze("b")
    return Pi(b, B, mertebe(lif(A, B, f, _t(b)), -2))


def denklik_tipi(A: Terim, B: Terim) -> Terim:
    f = terim_taze("f")
    return Sigma(f, ok(A, B), iz_denklik(A, B, _t(f)))


def ozdeslik_denkligi(A: Terim) -> Terim:
    x, b, z = terim_taze("x"), terim_taze("b"), terim_taze("z")
    i, j = terim_taze("i"), terim_taze("j")
    i_ar, j_ar = Aralik.degisken(i), Aralik.degisken(j)
    p = Ikinci(_t(z))
    merkez = Cift(_t(b), refl(_t(b)))
    buzme = Lam(z, YolLam(i, Cift(
        terim_yol_uygula(p, i_ar.degil()),
        YolLam(j, terim_yol_uygula(p, i_ar.degil().veya(j_ar))))))
    return Cift(Lam(x, _t(x)),
                  Lam(b, Cift(merkez, buzme)))


def denklik_fonksiyonu(e: Terim) -> Terim:
    return Birinci(e)


def ua(A: Terim, B: Terim, e: Terim) -> Terim:
    i = terim_taze("i")
    return YolLam(i, Yapistir(B, [
        (yuz(**{i: 0}), A, e),
        (yuz(**{i: 1}), B, ozdeslik_denkligi(B)),
    ]))


def cember_rec(hedef: Terim, taban_dali: Terim, dongu_dali_ad: str,
               dongu_dali: Terim, nokta: Terim) -> Terim:
    return CemberInd("_", hedef, taban_dali, dongu_dali_ad, dongu_dali, nokta)


def dongu() -> Terim:
    i = terim_taze("i")
    return YolLam(i, Dongu(Aralik.degisken(i)))


def dongu_tersi() -> Terim:
    i = terim_taze("i")
    return YolLam(i, Dongu(Aralik.degisken(i).degil()))


def dongu_kuvveti(n: int) -> Terim:
    A, a = Cember(), Taban()
    if n == 0:
        return refl(a)
    tek = dongu() if n > 0 else dongu_tersi()
    sonuc = tek
    for _ in range(abs(n) - 1):
        sonuc = terkip(A, a, a, a, sonuc,
                       dongu() if n > 0 else dongu_tersi())
    return sonuc


def dongu_kuvveti_genel_ters(n: int) -> Terim:
    A, a = Cember(), Taban()
    if n == 0:
        return refl(a)
    tek = dongu() if n > 0 else ters(A, a, a, dongu())
    sonuc = tek
    for _ in range(abs(n) - 1):
        sonuc = terkip(A, a, a, a, sonuc, tek)
    return sonuc


def ardil_z() -> Terim:
    n = terim_taze("n")
    m = terim_taze("m")
    neg_dali = DogalInd("_", Tamsayi(), Poz(Sfr()),
                          m, "_r", NegArd(_t(m)), _t(n))
    return Lam("z", TamsayiInd("_", Tamsayi(),
                                   n, Poz(Ard(_t(n))),
                                   n, neg_dali,
                                   _t("z")))


def oncel_z() -> Terim:
    n = terim_taze("n")
    m = terim_taze("m")
    poz_dali = DogalInd("_", Tamsayi(), NegArd(Sfr()),
                          m, "_r", Poz(_t(m)), _t(n))
    return Lam("z", TamsayiInd("_", Tamsayi(),
                                   n, poz_dali,
                                   n, NegArd(Ard(_t(n))),
                                   _t("z")))


def izo_denklige(A: Terim, B: Terim, f: Terim, g: Terim,
                 s: Terim, t: Terim) -> Terim:
    y, x0, x1, p0, p1, z = (terim_taze("y"), terim_taze("x0"), terim_taze("x1"),
                            terim_taze("p0"), terim_taze("p1"), terim_taze("z"))
    i, j, k = terim_taze("i"), terim_taze("j"), terim_taze("k")
    I, J, Kk = (Aralik.degisken(i), Aralik.degisken(j), Aralik.degisken(k))
    Y, X0, X1, P0, P1 = _t(y), _t(x0), _t(x1), _t(p0), _t(p1)
    uy = terim_uygula

    gy = uy(g, Y)

    def _fill(x, p):
        return terim_dolgu(k, A,
            [(yuz(**{i: 1}), terim_yol_uygula(uy(t, x), Kk)),
             (yuz(**{i: 0}), gy)],
            uy(g, terim_yol_uygula(p, I.degil())))

    fill0, fill1 = _fill(X0, P0), _fill(X1, P1)
    at = lambda trm, iv, kv: ara_ikame(trm, {i: iv, k: kv})

    fill2 = terim_dolgu(k, A,
        [(yuz(**{i: 1}), at(fill1, Kk, BIR)),
         (yuz(**{i: 0}), at(fill0, Kk, BIR))],
        gy)

    p_yol = YolLam(i, at(fill2, I, BIR))

    sq = HKomp(A, k,
        [(yuz(**{i: 1}), at(fill1, J, Kk.degil())),
         (yuz(**{i: 0}), at(fill0, J, Kk.degil())),
         (yuz(**{j: 0}), gy),
         (yuz(**{j: 1}), terim_yol_uygula(uy(t, at(fill2, I, BIR)),
                                        Kk.degil()))],
        at(fill2, I, J))

    sq1 = HKomp(B, k,
        [(yuz(**{i: 1}), terim_yol_uygula(uy(s, terim_yol_uygula(P1, J.degil())),
                                        Kk)),
         (yuz(**{i: 0}), terim_yol_uygula(uy(s, terim_yol_uygula(P0, J.degil())),
                                        Kk)),
         (yuz(**{j: 0}), terim_yol_uygula(uy(s, Y), Kk)),
         (yuz(**{j: 1}), terim_yol_uygula(uy(s, uy(f, terim_yol_uygula(p_yol, I))),
                                        Kk))],
        uy(f, sq))

    lem = YolLam(i, Cift(
        terim_yol_uygula(p_yol, I),
        YolLam(j, ara_ikame(sq1, {j: J.degil()}))))

    merkez = Cift(gy, uy(s, Y))
    buzme = Lam(z, ikame(lem, {x0: gy, p0: uy(s, Y),
                                   x1: Birinci(_t(z)),
                                   p1: Ikinci(_t(z))}))
    return Cift(f, Lam(y, Cift(merkez, buzme)))


def _z_yol_ispati(dis_govde, ic_sfr, ic_ard, neg_govde) -> Terim:
    Z = Tamsayi()
    z, n, m = terim_taze("z"), terim_taze("n"), terim_taze("m")
    poz_dali = DogalInd(m, dis_govde(Poz(_t(m))), ic_sfr,
                          m, "_r", ic_ard(_t(m)), _t(n))
    return Lam("w", TamsayiInd(z, dis_govde(_t(z)),
                                   n, poz_dali,
                                   n, neg_govde(_t(n)),
                                   _t("w")))


def ardil_oncel() -> Terim:
    Z = Tamsayi()
    suc, pred = ardil_z(), oncel_z()
    ifade = lambda w: yol(Z, terim_uygula(suc, terim_uygula(pred, w)), w)
    return _z_yol_ispati(
        ifade,
        refl(Poz(Sfr())),
        lambda m: refl(Poz(Ard(m))),
        lambda n: refl(NegArd(n)))


def oncel_ardil() -> Terim:
    Z = Tamsayi()
    suc, pred = ardil_z(), oncel_z()
    ifade = lambda w: yol(Z, terim_uygula(pred, terim_uygula(suc, w)), w)
    z, n, m = terim_taze("z"), terim_taze("n"), terim_taze("m")
    poz_dali = refl(Poz(_t(n)))
    neg_ic = DogalInd(m, ifade(NegArd(_t(m))), refl(NegArd(Sfr())),
                        m, "_r", refl(NegArd(Ard(_t(m)))), _t(n))
    return Lam("w", TamsayiInd(z, ifade(_t(z)),
                                   n, poz_dali, n, neg_ic, _t("w")))


def ardil_denkligi() -> Terim:
    Z = Tamsayi()
    return izo_denklige(Z, Z, ardil_z(), oncel_z(),
                        ardil_oncel(), oncel_ardil())


def sarmal(nokta: Terim) -> Terim:
    Z = Tamsayi()
    i = terim_taze("i")
    govde = Yapistir(Z, [
        (yuz(**{i: 0}), Z, ardil_denkligi()),
        (yuz(**{i: 1}), Z, ozdeslik_denkligi(Z)),
    ])
    return CemberInd("_", U, Z, i, govde, nokta)


def sarim(p: Terim) -> Terim:
    i = terim_taze("i")
    cizgi = sarmal(terim_yol_uygula(p, Aralik.degisken(i)))
    return Transp(i, cizgi, YANLIS, Poz(Sfr()))


class EksikKural(NotImplementedError):
    pass


_A0, _AR, _AA, _BB, _FF, _BSC = (Deg("!A0"), Deg("!Ar"), Deg("!A"),
                                 Deg("!B"), Deg("!f"), Deg("!b"))


_DENKLIK_T = denklik_tipi(_A0, _AR)


_IDEQ_T = ozdeslik_denkligi(_A0)


_LIF_T = lif(_AA, _BB, _FF, _BSC)


class GlueHam:

    __slots__ = ("taban", "dallar")

    def __init__(self, taban, dallar) -> None:
        self.taban, self.dallar = taban, tuple(dallar)

    def act(self, s) -> "GlueHam":
        return GlueHam(self.taban.act(s), _dallari_act(self.dallar, s))


def her_i_icin(kof: Kofibrasyon, ad: str) -> Kofibrasyon:
    return Kofibrasyon([y for y in kof.yuzler
                        if all(a != ad for (a, _) in y)])


def _denklik_cizgi(al, r):
    c0, hat = al
    return degerlendir(_DENKLIK_T,
                       BOS.genislet("!A0", c0).genislet("!Ar", hat.uygula(r)))


def cizgi_denkligi(hat: ACizgi) -> Deger:
    c0 = hat.uygula(SIFIR)
    idq = degerlendir(_IDEQ_T, BOS.genislet("!A0", c0))
    return transp(ATuretilmis(_denklik_cizgi, (c0, hat)), YANLIS, idq)


def komp_evren(hat: ACizgi, sistem: Sistem, u0: Deger) -> Deger:
    dallar = []
    for (y, c) in sistem:
        k = taze("k")
        ters = AYeniden(c, k, Aralik.degisken(k).degil())
        dallar.append((y, c.uygula(BIR), cizgi_denkligi(ters)))
    return yapistir(u0, dallar)


def _buzme_c(al, j):
    h, v = al
    return yol_uygula(uygula(h, v), j)


def denklikle_tamamla(A: Deger, B: Deger, e: Deger, b: Deger,
                      kismi: Sequence[Tuple[frozenset, Deger]]) -> Deger:
    X = degerlendir(_LIF_T, BOS.genislet("!A", A).genislet("!B", B)
                    .genislet("!f", bir(e)).genislet("!b", b))
    buzuk = uygula(iki(e), b)
    return hkomp(X, Sistem([(y, ATuretilmis(_buzme_c, (iki(buzuk), v)))
                            for (y, v) in kismi]), bir(buzuk))


def _act_cizgi(al, r):
    d, ad = al
    return d.act({ad: r})


def _uyg_bir_c(al, r):
    e_hat, c = al
    return uygula(bir(e_hat.uygula(r)), c.uygula(r))


def _pres_c(al, j):
    A_hat, T_hat, e_hat, psi, u0 = al
    tfill = dolgu(T_hat, psi, u0)
    dallar = [(y, ATuretilmis(_uyg_bir_c, (e_hat, c))) for (y, c) in psi]
    for f in aralik_esitligi(j, True).yuzler:
        dallar.append((f, ATuretilmis(_uyg_bir_c, (e_hat, tfill))))
    f0 = bir(e_hat.uygula(SIFIR))
    return komp(A_hat, Sistem(dallar), uygula(f0, u0))


def _glue_taban_c(al, r):
    gh, ad = al
    return gh.taban.act({ad: r})


def _unglue_c(al, r):
    gh, ad, c = al
    return coz(gh.taban.act({ad: r}), _dallari_act(gh.dallar, {ad: r}),
               c.uygula(r))


def _alfa_ters_c(al, j):
    (alfa,) = al
    return yol_uygula(alfa, j.degil())


def komp_yapistir(hat: ACizgi, sistem: Sistem, u0: Deger) -> Deger:
    i = taze("i")
    Ai = hat.uygula(Aralik.degisken(i))
    if not isinstance(Ai, DYapistir):
        raise EksikKural("komp_yapistir: Glue bekleniyordu")

    gh = GlueHam(Ai.taban, Ai.dallar)
    A_hat = ATuretilmis(_glue_taban_c, (gh, i))
    G0 = _dallari_act(Ai.dallar, {i: SIFIR})
    G1 = _dallari_act(Ai.dallar, {i: BIR})
    A0 = Ai.taban.act({i: SIFIR})
    A1 = Ai.taban.act({i: BIR})

    a0 = coz(A0, G0, u0)
    psi_a = Sistem([(y, ATuretilmis(_unglue_c, (gh, i, c)))
                    for (y, c) in sistem])
    ap1 = komp(A_hat, psi_a, a0)

    phi = Kofibrasyon([y for (y, _, _) in Ai.dallar])
    delta_dallari = [(y, T, e) for (y, T, e) in Ai.dallar
                     if all(a != i for (a, _) in y)]

    t1_dallar: List[Tuple[frozenset, Deger]] = []
    alfa_dallar: List[Tuple[frozenset, Deger]] = []

    for (y1, T1, e1) in G1:
        sig = yuzu_atamaya_cevir(y1)
        A1s, T1s, e1s, ap1s = (A1.act(sig), T1.act(sig), e1.act(sig),
                               ap1.act(sig))
        kismi: List[Tuple[frozenset, Deger]] = []

        for (yp, c) in sistem:
            k = Kofibrasyon([yp]).yerine_koy(sig)
            if k.bos_mu():
                continue
            for yf in k.yuzler:
                sg = dict(sig)
                sg.update(yuzu_atamaya_cevir(yf))
                kismi.append((yf, DCift(c.uygula(BIR).act(sg),
                                          DYolLam(ASabit(ap1.act(sg))))))

        for (yd, Td, ed) in delta_dallari:
            k = Kofibrasyon([yd]).yerine_koy(sig)
            if k.bos_mu():
                continue
            for yf in k.yuzler:
                sg = dict(sig)
                sg.update(yuzu_atamaya_cevir(yf))
                T_hat = ATuretilmis(_act_cizgi, (Td.act(sg), i))
                e_hat = ATuretilmis(_act_cizgi, (ed.act(sg), i))
                As = ATuretilmis(_glue_taban_c, (gh.act(sg), i))
                psi_s = sistem.act(sg)
                u0s = u0.act(sg)
                tp1 = komp(T_hat, psi_s, u0s)
                omega = DYolLam(ATuretilmis(
                    _pres_c, (As, T_hat, e_hat, psi_s, u0s)))
                kismi.append((yf, DCift(tp1, omega)))

        tam = denklikle_tamamla(T1s, A1s, e1s, ap1s, kismi)
        t1_dallar.append((y1, bir(tam)))
        alfa_dallar.append((y1, iki(tam)))

    a1_dallar = [(y, ASabit(coz(A1, G1, c.uygula(BIR))))
                 for (y, c) in sistem]
    a1_dallar += [(y1, ATuretilmis(_alfa_ters_c, (alfa,)))
                  for (y1, alfa) in alfa_dallar]
    a1 = hkomp(A1, Sistem(a1_dallar), ap1)
    return yapistir_terim(t1_dallar, a1)


class DenetimHatasi(Exception):
    pass


class Baglam:
    __slots__ = ("tipler", "ortam", "aralik")

    def __init__(self, tipler=None, ortam=None, aralik=None) -> None:
        self.tipler: Dict[str, Deger] = dict(tipler or {})
        self.ortam: Ortam = ortam or BOS
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
        return deger_esit_mi(a, b)


def _bagdasir(y1: Yuz, y2: Yuz) -> Optional[Yuz]:
    gor: Dict[str, bool] = {}
    for (ad, d) in set(y1) | set(y2):
        if ad in gor and gor[ad] != d:
            return None
        gor[ad] = d
    return frozenset(set(y1) | set(y2))


def _sabit_cizgi_mi(hat, ad_ipucu: str = "i") -> bool:
    k = taze("sbt")
    govde = geri_oku(hat.uygula(Aralik.degisken(k)), 0)
    return k not in ara_serbest(govde)


def denetle_tip(t: Terim, g: Baglam) -> int:
    T = sentezle(t, g)
    if isinstance(T, DEvren):
        return T.seviye
    raise DenetimHatasi("tip bekleniyordu: %s : %s" % (t, geri_oku(T)))


def denetle_sistem(ad: str, cizgi: Terim, dallar, u0: Terim,
                   g: Baglam) -> None:
    gi = g.ara_ekle(ad)
    for (y, govde) in dallar:
        gy = gi.kisitla(y)
        s = yuzu_atamaya_cevir(y)
        denetle(ara_ikame(govde, s), gy.d(ara_ikame(cizgi, s)), gy)
    for m in range(len(dallar)):
        for n in range(m + 1, len(dallar)):
            ortak = _bagdasir(dallar[m][0], dallar[n][0])
            if ortak is None:
                continue
            s = yuzu_atamaya_cevir(ortak)
            go = gi.kisitla(ortak)
            sol = go.d(ara_ikame(dallar[m][1], s))
            sag = go.d(ara_ikame(dallar[n][1], s))
            if not go.esit_mi(sol, sag):
                raise DenetimHatasi("sistem çakışan yüzde uyuşmuyor (%s)"
                                    % sorted(ortak))
    for (y, govde) in dallar:
        s = dict(yuzu_atamaya_cevir(y))
        s[ad] = SIFIR
        gy = g.kisitla(y)
        sol = gy.d(ara_ikame(govde, s))
        sag = gy.d(ara_ikame(u0, yuzu_atamaya_cevir(y)))
        if not gy.esit_mi(sol, sag):
            raise DenetimHatasi("sistem tabanla uyuşmuyor (yüz %s)" % sorted(y))


def sentezle(t: Terim, g: Baglam) -> Deger:
    if isinstance(t, YonluHom):
        sv = denetle_tip(t.cizgi, g)
        A = g.d(t.cizgi)
        denetle(t.kaynak, A, g)
        denetle(t.hedef, A, g)
        _TURETIM_SAYI["yönlü_teşkil"] = _TURETIM_SAYI.get(
            "yönlü_teşkil", 0) + 1
        return DEvren(sv)
    if isinstance(t, YonluOk):
        A = g.d(t.cizgi)
        denetle(t.kaynak, A, g)
        denetle(t.hedef, A, g)
        return DYonluHom(A, g.d(t.kaynak), g.d(t.hedef))
    if isinstance(t, OperadHom):
        sv = denetle_tip(t.cizgi, g)
        A = g.d(t.cizgi)
        for on in t.oncutler:
            denetle(on, A, g)
        denetle(t.hedef, A, g)
        return DEvren(sv)
    if isinstance(t, OperadAgac):
        A = g.d(t.cizgi)
        for on in t.oncutler:
            denetle(on, A, g)
        denetle(t.hedef, A, g)
        return DOperadHom(A, tuple(g.d(x) for x in t.oncutler), g.d(t.hedef))
    if isinstance(t, OperadSilsile):
        A = g.d(t.cizgi)
        for on in t.baslangic_oncutler:
            denetle(on, A, g)
        denetle(t.nihai_hedef, A, g)

        if not t.adimlar:
            raise DenetimHatasi("OperadSilsile boş olamaz")

        onceki_hedef = None
        for k_idx, (agac, ok) in enumerate(t.adimlar):
            tip_agac = sentezle(agac, g)
            tip_ok = sentezle(ok, g)

            if not (isinstance(tip_agac, DOperadHom) and isinstance(tip_ok, DYonluHom)):
                raise DenetimHatasi("OperadSilsile adımları (OperadAgac, YonluOk) olmalıdır")

            if not g.esit_mi(tip_agac.hedef, tip_ok.kaynak):
                raise DenetimHatasi("OperadSilsile %d. adımda iç kopukluk" % k_idx)

            if onceki_hedef is not None:
                oncut_uyumu = any(g.esit_mi(onceki_hedef, on_deg) for on_deg in tip_agac.oncutler)
                if not oncut_uyumu:
                    raise DenetimHatasi(
                        "OperadSilsile %d. adımda zincir kopukluğu: önceki hedef girdide yok" % k_idx)

            onceki_hedef = tip_ok.hedef

        if not g.esit_mi(onceki_hedef, g.d(t.nihai_hedef)):
            raise DenetimHatasi("OperadSilsile son adımı nihai hedefe ulaşmıyor")

        return DOperadHom(A, tuple(g.d(x) for x in t.baslangic_oncutler),
                          g.d(t.nihai_hedef))
    if isinstance(t, YonluTerkip):
        tip_f = sentezle(t.f, g)
        tip_g = sentezle(t.g, g)

        f_hedef = getattr(tip_f, "hedef", None)
        if isinstance(tip_g, DYonluHom):
            g_kaynak = tip_g.kaynak
            g_kalan_oncutler = ()
        elif isinstance(tip_g, DOperadHom) and tip_g.oncutler:
            g_kaynak = tip_g.oncutler[0]
            g_kalan_oncutler = tip_g.oncutler[1:]
        else:
            g_kaynak = None
            g_kalan_oncutler = ()

        if f_hedef is None or g_kaynak is None:
            raise DenetimHatasi("YonluTerkip: f ve g geçerli yönlü çıkarım tipleri olmalıdır")
        if not g.esit_mi(f_hedef, g_kaynak):
            raise DenetimHatasi(
                "YonluTerkip uç uyuşmazlığı: f'in hedefi g'nin öncülü olmalıdır")

        f_oncutler = tip_f.oncutler if isinstance(tip_f, DOperadHom) else (tip_f.kaynak,)
        yeni_oncutler = tuple(f_oncutler) + tuple(g_kalan_oncutler)

        cizgi = tip_f.cizgi
        if (len(yeni_oncutler) == 1 and isinstance(tip_f, DYonluHom)
                and isinstance(tip_g, DYonluHom)):
            return DYonluHom(cizgi, yeni_oncutler[0], tip_g.hedef)
        return DOperadHom(cizgi, yeni_oncutler, tip_g.hedef)
    if isinstance(t, Deg):
        if t.ad not in g.tipler:
            raise DenetimHatasi("kapsamda olmayan değişken: %s" % t.ad)
        return g.tipler[t.ad]

    if isinstance(t, Evren):
        return DEvren(t.seviye + 1)

    if isinstance(t, (Pi, Sigma)):
        sa = denetle_tip(t.alan, g)
        sh = denetle_tip(t.hedef, g.genislet(t.ad, g.d(t.alan)))
        return DEvren(max(sa, sh))

    if isinstance(t, Uygula):
        ft = sentezle(t.fonk, g)
        if not isinstance(ft, DPi):
            raise DenetimHatasi("fonksiyon bekleniyordu: %s" % (t.fonk,))
        denetle(t.arg, ft.alan, g)
        return ft.kap.uygula(g.d(t.arg))

    if isinstance(t, Birinci):
        ct = sentezle(t.cift, g)
        if not isinstance(ct, DSigma):
            raise DenetimHatasi("çift bekleniyordu")
        return ct.alan

    if isinstance(t, Ikinci):
        ct = sentezle(t.cift, g)
        if not isinstance(ct, DSigma):
            raise DenetimHatasi("çift bekleniyordu")
        return ct.kap.uygula(bir(g.d(t.cift)))

    if isinstance(t, YolP):
        gi = g.ara_ekle(t.ad)
        s = denetle_tip(t.cizgi, gi)
        hat = ASoz(t.ad, t.cizgi, g.ortam)
        denetle(t.sol, hat.uygula(SIFIR), g)
        denetle(t.sag, hat.uygula(BIR), g)
        return DEvren(s)

    if isinstance(t, YolUygula):
        _ara_denetle(t.r, g)
        if isinstance(t.yol, YolLam):
            return sentezle(ara_ikame(t.yol.govde, {t.yol.ad: t.r}), g)
        pt = sentezle(t.yol, g)
        if not isinstance(pt, DYolP):
            raise DenetimHatasi("yol bekleniyordu: %s" % (t.yol,))
        return pt.cizgi.uygula(t.r)

    if isinstance(t, Transp):
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

    if isinstance(t, Komp):
        gi = g.ara_ekle(t.ad)
        denetle_tip(t.cizgi, gi)
        hat = ASoz(t.ad, t.cizgi, g.ortam)
        denetle(t.u0, hat.uygula(SIFIR), g)
        denetle_sistem(t.ad, t.cizgi, t.dallar, t.u0, g)
        return hat.uygula(BIR)

    if isinstance(t, HKomp):
        denetle_tip(t.tip, g)
        tv = g.d(t.tip)
        denetle(t.u0, tv, g)
        denetle_sistem(t.ad, t.tip, t.dallar, t.u0, g)
        return tv

    if isinstance(t, Yapistir):
        s = denetle_tip(t.taban, g)
        for (y, T, e) in t.dallar:
            gy = g.kisitla(y)
            sg = yuzu_atamaya_cevir(y)
            Ty = ara_ikame(T, sg)
            denetle_tip(Ty, gy)
            denetle(ara_ikame(e, sg),
                    gy.d(denklik_tipi(Ty, ara_ikame(t.taban, sg))), gy)
        return DEvren(s)

    if isinstance(t, Coz):
        denetle(t.govde, g.d(Yapistir(t.taban, t.dallar)), g)
        return g.d(t.taban)

    if isinstance(t, Dogal):
        return DEvren(0)
    if isinstance(t, Sfr):
        return DDogal()
    if isinstance(t, Ard):
        denetle(t.alt, DDogal(), g)
        return DDogal()
    if isinstance(t, Belirtec):
        return DDogal()
    if isinstance(t, Tamsayi):
        return DEvren(0)
    if isinstance(t, (Poz, NegArd)):
        denetle(t.alt, DDogal(), g)
        return DTamsayi()
    if isinstance(t, Cember):
        return DEvren(0)
    if isinstance(t, Taban):
        return DCember()
    if isinstance(t, Dongu):
        _ara_denetle(t.r, g)
        return DCember()

    if isinstance(t, DogalInd):
        motif = KSoz(t.ad, t.hedef, g.ortam)
        denetle_tip(t.hedef, g.genislet(t.ad, DDogal()))
        denetle(t.sayi, DDogal(), g)
        denetle(t.sfr_dali, motif.uygula(DSfr()), g)
        gn = g.genislet(t.n_ad, DDogal())
        nv = gn.ortam.terimler[t.n_ad]
        gnr = gn.genislet(t.rec_ad, motif.uygula(nv))
        denetle(t.ard_dali, motif.uygula(DArd(nv)), gnr)
        return motif.uygula(g.d(t.sayi))

    if isinstance(t, TamsayiInd):
        motif = KSoz(t.ad, t.hedef, g.ortam)
        denetle_tip(t.hedef, g.genislet(t.ad, DTamsayi()))
        denetle(t.sayi, DTamsayi(), g)
        gp = g.genislet(t.poz_ad, DDogal())
        denetle(t.poz_dali, motif.uygula(DPoz(gp.ortam.terimler[t.poz_ad])), gp)
        gn = g.genislet(t.neg_ad, DDogal())
        denetle(t.neg_dali,
                motif.uygula(DNegArd(gn.ortam.terimler[t.neg_ad])), gn)
        return motif.uygula(g.d(t.sayi))

    if isinstance(t, CemberInd):
        motif = KSoz(t.ad, t.hedef, g.ortam)
        denetle_tip(t.hedef, g.genislet(t.ad, DCember()))
        denetle(t.nokta, DCember(), g)
        denetle(t.taban_dali, motif.uygula(DTaban()), g)
        tbd = g.d(t.taban_dali)
        cizgi = ikame(t.hedef,
                         {t.ad: Dongu(Aralik.degisken(t.i_ad))})
        denetle(YolLam(t.i_ad, t.dongu_dali),
                DYolP(ASoz(t.i_ad, cizgi, g.ortam), tbd, tbd), g)
        return motif.uygula(g.d(t.nokta))

    if isinstance(t, Suspansiyon):
        denetle_tip(t.taban_uzay, g)
        return DEvren(0)
    if isinstance(t, (KuzeyKutup, GuneyKutup)):
        denetle_tip(t.uzay, g)
        return DSuspansiyon(g.d(t.uzay))
    if isinstance(t, Meridyen):
        _ara_denetle(t.i_aralik, g)
        denetle(t.nokta, g.d(t.uzay), g)
        return DSuspansiyon(g.d(t.uzay))

    raise DenetimHatasi("sentezlenemeyen terim: %r" % (t,))


def _ara_denetle(r: Aralik, g: Baglam) -> None:
    eksik = r.degiskenler() - g.aralik
    if eksik:
        raise DenetimHatasi("kapsamda olmayan aralık değişkeni: %s"
                            % ", ".join(sorted(eksik)))


def denetle(t: Terim, tip: Deger, g: Baglam) -> None:
    if isinstance(t, Lam):
        if not isinstance(tip, DPi):
            raise DenetimHatasi("λ için Π bekleniyordu: %s" % geri_oku(tip))
        g2 = g.genislet(t.ad, tip.alan)
        denetle(t.govde, tip.kap.uygula(g2.ortam.terimler[t.ad]), g2)
        return

    if isinstance(t, Cift):
        if not isinstance(tip, DSigma):
            raise DenetimHatasi("çift için Σ bekleniyordu: %s" % geri_oku(tip))
        denetle(t.bir, tip.alan, g)
        denetle(t.iki, tip.kap.uygula(g.d(t.bir)), g)
        return

    if isinstance(t, YolLam):
        if not isinstance(tip, DYolP):
            raise DenetimHatasi("<i> için PathP bekleniyordu: %s"
                                % geri_oku(tip))
        gi = g.ara_ekle(t.ad)
        denetle(t.govde, tip.cizgi.uygula(Aralik.degisken(t.ad)), gi)
        sol = g.d(ara_ikame(t.govde, {t.ad: SIFIR}))
        sag = g.d(ara_ikame(t.govde, {t.ad: BIR}))
        if not g.esit_mi(sol, tip.sol):
            raise DenetimHatasi("yolun sol ucu uymuyor: %s ≠ %s"
                                % (geri_oku(sol), geri_oku(tip.sol)))
        if not g.esit_mi(sag, tip.sag):
            raise DenetimHatasi("yolun sağ ucu uymuyor: %s ≠ %s"
                                % (geri_oku(sag), geri_oku(tip.sag)))
        return

    if isinstance(t, YapistirTerim):
        if not isinstance(tip, DYapistir):
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
            gv = gy.d(ara_ikame(govde, sg))
            denetle(ara_ikame(govde, sg), T.act(sg), gy)
            sol = uygula(bir(e.act(sg)), gv)
            sag = gy.d(ara_ikame(t.taban_terim, sg))
            if not gy.esit_mi(sol, sag):
                raise DenetimHatasi("glue: %s yüzünde e.1 t ≠ a" % sorted(y))
        return

    bulunan = sentezle(t, g)
    if not g.esit_mi(bulunan, tip):
        raise DenetimHatasi("tip uyuşmazlığı:\n  terim   : %s\n  beklenen: %s\n"
                            "  bulunan : %s"
                            % (t, geri_oku(tip), geri_oku(bulunan)))


def denetle_t(t: Terim, tip_terim: Terim, g: Baglam) -> None:
    denetle(t, g.d(tip_terim), g)


def _genislet_t(self: Baglam, ad: str, tip_terim: Terim) -> Baglam:
    return self.genislet(ad, self.d(tip_terim))


Baglam.genislet_t = _genislet_t


U = Evren(0)


U1 = Evren(1)


D = Deg


def sigma_hepsi(baglar: Sequence[Tuple[str, Terim]], son: Terim) -> Terim:
    for ad, tip in reversed(list(baglar)):
        son = Sigma(ad, tip, son)
    return son


def _ikili(f: Terim, x: Terim, y: Terim) -> Terim:
    return Uygula(Uygula(f, x), y)


def morfizm_tipi(A: Terim, n: int) -> Terim:
    if n <= 0:
        return A
    x, y = terim_taze("x"), terim_taze("y")
    return Pi(x, A, Pi(y, A, morfizm_tipi(yol(A, D(x), D(y)), n - 1)))


def morfizm_uzayi(A: Terim, x: Terim, y: Terim, n: int) -> Terim:
    if n <= 1:
        return yol(A, x, y)
    raise ValueError("n≥2 için uçları da vermek gerekir; morfizm_tipi kullanın")


def koherens_tipi(A: Terim, n: int) -> Terim:
    return morfizm_tipi(A, n + 1)


def kume_tipi() -> Terim:
    X = terim_taze("X")
    return Sigma(X, U, mertebe(D(X), 0))


def onerme_tipi() -> Terim:
    X = terim_taze("X")
    return Sigma(X, U, mertebe(D(X), -1))


def grupoid_tipi() -> Terim:
    X = terim_taze("X")
    return Sigma(X, U, mertebe(D(X), 1))


def n_tip_tipi(n: int) -> Terim:
    X = terim_taze("X")
    return Sigma(X, U, mertebe(D(X), n))


def monoid_tipi() -> Terim:
    X, EksikKural, m = D("X"), D("EksikKural"), D("m")
    x, y, z = D("x"), D("y"), D("z")
    birlesme = Pi("x", X, Pi("y", X, Pi("z", X,
        yol(X, _ikili(m, _ikili(m, x, y), z),
                 _ikili(m, x, _ikili(m, y, z))))))
    sol_birim = Pi("x", X, yol(X, _ikili(m, EksikKural, x), x))
    sag_birim = Pi("x", X, yol(X, _ikili(m, x, EksikKural), x))
    return sigma_hepsi([
        ("X", U),
        ("kume", mertebe(X, 0)),
        ("EksikKural", X),
        ("m", ok(X, ok(X, X))),
        ("birlesme", birlesme),
        ("sol_birim", sol_birim),
    ], sag_birim)


def grup_tipi() -> Terim:
    X, EksikKural, m, iv = D("X"), D("EksikKural"), D("m"), D("iv")
    x, y, z = D("x"), D("y"), D("z")
    birlesme = Pi("x", X, Pi("y", X, Pi("z", X,
        yol(X, _ikili(m, _ikili(m, x, y), z),
                 _ikili(m, x, _ikili(m, y, z))))))
    sol_birim = Pi("x", X, yol(X, _ikili(m, EksikKural, x), x))
    sag_birim = Pi("x", X, yol(X, _ikili(m, x, EksikKural), x))
    sol_ters = Pi("x", X, yol(X, _ikili(m, Uygula(iv, x), x), EksikKural))
    sag_ters = Pi("x", X, yol(X, _ikili(m, x, Uygula(iv, x)), EksikKural))
    return sigma_hepsi([
        ("X", U),
        ("kume", mertebe(X, 0)),
        ("EksikKural", X),
        ("m", ok(X, ok(X, X))),
        ("iv", ok(X, X)),
        ("birlesme", birlesme),
        ("sol_birim", sol_birim),
        ("sag_birim", sag_birim),
        ("sol_ters", sol_ters),
    ], sag_ters)


def halka_tipi() -> Terim:
    X = D("X")
    sf, bir = D("sifir"), D("bir")
    top, carp, eks = D("top"), D("carp"), D("eks")
    x, y, z = D("x"), D("y"), D("z")
    P3 = lambda govde: Pi("x", X, Pi("y", X, Pi("z", X, govde)))
    P1 = lambda govde: Pi("x", X, govde)
    P2 = lambda govde: Pi("x", X, Pi("y", X, govde))
    return sigma_hepsi([
        ("X", U),
        ("kume", mertebe(X, 0)),
        ("sifir", X), ("bir", X),
        ("top", ok(X, ok(X, X))),
        ("carp", ok(X, ok(X, X))),
        ("eks", ok(X, X)),
        ("top_birlesme", P3(yol(X, _ikili(top, _ikili(top, x, y), z),
                                     _ikili(top, x, _ikili(top, y, z))))),
        ("top_degisme", P2(yol(X, _ikili(top, x, y), _ikili(top, y, x)))),
        ("top_birim", P1(yol(X, _ikili(top, sf, x), x))),
        ("top_ters", P1(yol(X, _ikili(top, Uygula(eks, x), x), sf))),
        ("carp_birlesme", P3(yol(X, _ikili(carp, _ikili(carp, x, y), z),
                                      _ikili(carp, x, _ikili(carp, y, z))))),
        ("carp_degisme", P2(yol(X, _ikili(carp, x, y), _ikili(carp, y, x)))),
        ("carp_birim", P1(yol(X, _ikili(carp, bir, x), x))),
    ], P3(yol(X, _ikili(carp, x, _ikili(top, y, z)),
                   _ikili(top, _ikili(carp, x, y), _ikili(carp, x, z)))))


def kategori_tipi() -> Terim:
    Ob, Hom, bir, bil = D("Ob"), D("Hom"), D("bir"), D("bil")
    a, b, c, d = D("a"), D("b"), D("c"), D("d")
    H = lambda u, v: _ikili(Hom, u, v)
    B = lambda u, v, w, f, g: Uygula(Uygula(
        Uygula(Uygula(Uygula(bil, u), v), w), f), g)
    Pab = lambda govde: Pi("a", Ob, Pi("b", Ob, govde))
    hom_kume = Pab(mertebe(H(a, b), 0))
    birim_tip = Pi("a", Ob, H(a, a))
    bil_tip = Pi("a", Ob, Pi("b", Ob, Pi("c", Ob,
        ok(H(a, b), ok(H(b, c), H(a, c))))))
    f, g_, h = D("f"), D("g"), D("h")
    sol_birim = Pab(Pi("f", H(a, b),
        yol(H(a, b), B(a, a, b, Uygula(bir, a), f), f)))
    sag_birim = Pab(Pi("f", H(a, b),
        yol(H(a, b), B(a, b, b, f, Uygula(bir, b)), f)))
    birlesme = Pab(Pi("c", Ob, Pi("d", Ob,
        Pi("f", H(a, b), Pi("g", H(b, c), Pi("h", H(c, d),
            yol(H(a, d), B(a, c, d, B(a, b, c, f, g_), h),
                           B(a, b, d, f, B(b, c, d, g_, h)))))))))
    return sigma_hepsi([
        ("Ob", U),
        ("Hom", ok(Ob, ok(Ob, U))),
        ("hom_kume", hom_kume),
        ("bir", birim_tip),
        ("bil", bil_tip),
        ("sol_birim", sol_birim),
        ("sag_birim", sag_birim),
    ], birlesme)


def globuler_tip(n: int) -> Terim:
    if n <= 0:
        return U1 if False else U
    Ob = terim_taze("Ob")
    return Sigma(Ob, U, ok(D(Ob), ok(D(Ob), globuler_tip(n - 1))))


def omega_grupoid_kulesi(A: Terim, n: int) -> List[Tuple[int, Terim]]:
    return [(k, morfizm_tipi(A, k)) for k in range(n + 1)]


def cember_bilgisi() -> Dict[str, Terim]:
    S1 = Cember()
    return {
        "uzay": S1,
        "taban": Taban(),
        "dongu": dongu(),
        "Omega": dongu_uzayi(S1, Taban()),
        "Omega2": dongu_uzayi_n(S1, Taban(), 2),
    }


class Postulat:

    __slots__ = ("ad", "tip", "izah")

    def __init__(self, ad: str, tip: Terim, izah: str) -> None:
        self.ad, self.tip, self.izah = ad, tip, izah

    def __repr__(self) -> str:
        return "Postulat(%s)" % self.ad


def sdg_postulatlari() -> List[Postulat]:
    R = D("R")
    hR = D("halka_R")
    carp = D("carp_R")
    top = D("top_R")
    sf = D("sifir_R")
    d, x, ff, aa, bb = D("d"), D("x"), D("f"), D("a"), D("b")

    Dtip = Sigma("x", R, yol(R, _ikili(carp, x, x), sf))

    kl_govde = Pi("d", Dtip, yol(R, Uygula(ff, d),
        _ikili(top, aa, _ikili(carp, bb, Birinci(d)))))
    kl = Pi("f", ok(Dtip, R),
              mertebe(sigma_hepsi([("a", R), ("b", R)], kl_govde), -2))

    im = D("Im")
    im_tip = ok(U, U)
    im_birim = Pi("X", U, ok(D("X"), Uygula(im, D("X"))))

    return [
        Postulat("R", U,
                 "Pürüzsüz doğru (smooth line); SDG'nin taşıyıcı halkası."),
        Postulat("top_R", ok(R, ok(R, R)), "R üzerinde toplama."),
        Postulat("carp_R", ok(R, ok(R, R)), "R üzerinde çarpma."),
        Postulat("sifir_R", R, "R'nin sıfırı."),
        Postulat("KockLawvere", kl,
                 "Kock-Lawvere aksiyomu: D üzerindeki her fonksiyon TEK bir "
                 "afin form ile temsil edilir. Türev kavramı buradan doğar; "
                 "sentetik diferansiyel geometrinin bel kemiğidir."),
        Postulat("Im", im_tip,
                 "Sonsuz küçük şekil kipi ℑ (infinitesimal shape modality); "
                 "de Rham uzayı ve düz (crystalline) yapılar bununla kurulur."),
        Postulat("Im_birim", im_birim, "ℑ kipinin birim dönüşümü X → ℑX."),
    ]


def univalence_postulati() -> Postulat:
    A, B, EksikKural, x = D("A"), D("B"), D("EksikKural"), D("x")
    tip = Pi("A", U, Pi("B", U, Pi("EksikKural", denklik_tipi(A, B),
        Pi("x", A, yol(B, tasi(ua(A, B, EksikKural), x),
                              Uygula(Birinci(EksikKural), x))))))
    return Postulat("uaBeta", tip,
                    "ua'nın β-kuralı: ua EksikKural boyunca taşıma, denkliğin "
                    "fonksiyonudur. Kübik çekirdekte comp^i(Glue) imâl "
                    "edilseydi bu TANIMSAL olurdu; burada postulattır.")


def postulat_baglami(postulatlar: Sequence[Postulat],
                     taban: Optional[Baglam] = None) -> Baglam:
    g = taban or Baglam()
    for p in postulatlar:
        g = g.genislet_t(p.ad, p.tip)
    return g


def bosluklar() -> List[Dict[str, str]]:
    return [
        {
            "ad": "π₁(S¹) ≅ ℤ hesabı",
            "durum": "HESAPLANIYOR (NbE sürümünde)",
            "sebep": "Terim seviyesindeki sürümde |n| ≥ 2 için bitmiyordu; "
                     "ikame terim ağacını kopyaladığı için. NbE'de kapanış "
                     "+ ortam kullanıldığından kopyalama yok.",
            "netice": "sarim(dongu^n) = n ölçüldü: n=20 için 0.97 s, "
                      "n=-5 için 28.9 s; tepe bellek 21.7 MB. Negatif "
                      "kuvvetler ağır çünkü 'ters' daha karmaşık bir hcomp "
                      "doğuruyor -- fakat BİTİYOR.",
        },
        {
            "ad": "Genel HIT'ler (süspansiyon, pushout, n-kesme)",
            "durum": "YALNIZ S¹ imâl edildi",
            "sebep": "Her HIT'in kendi hcomp kuralı vardır; genel bir HIT "
                     "şeması yazılmadı.",
            "netice": "Sⁿ (n≥2) ve kesme (truncation) yok; dolayısıyla πₙ "
                      "KÜME olarak tarif edilemiyor. Ωⁿ vardır.",
        },
        {
            "ad": "Pürüzsüz ∞-topos / SDG / de Rham",
            "durum": "POSTULAT",
            "sebep": "Kock-Lawvere, ℑ kipi ve dış türev d'nin HESAPLANAN bir "
                     "indirgeme kuralı hiçbir kübik çekirdekte yoktur.",
            "netice": "Tipleri makine ile denetlenir; sakinleri aksiyomdur.",
        },
        {
            "ad": "Aralık cebrinde önbellekleme",
            "durum": "ÖLÇÜMLE REDDEDİLDİ",
            "sebep": "ve/veya/degil/yerine_koy işlemlerini belleğe almak "
                     "(hash-consing fikri) denendi.",
            "netice": "Hız aynı kaldı, tepe bellek 20 MB'dan 1281 MB'a "
                      "çıktı. Kaldırıldı. Kazanç antizincir algoritmasından "
                      "ve erken çıkıştan geliyor.",
        },
    ]


def _dene(ad: str, is_: Callable[[], None]) -> Dict[str, str]:
    try:
        is_()
        return {"ad": ad, "netice": "GEÇTİ"}
    except EksikKural as EksikKural:
        return {"ad": ad, "netice": "EKSİK KURAL", "izah": str(EksikKural)[:120]}
    except Exception as EksikKural:
        return {"ad": ad, "netice": "HATA", "izah": ("%s: %s" % (type(EksikKural).__name__, EksikKural))[:300]}


def dogrula_hepsi_turetimler() -> List[Dict[str, str]]:
    g = Baglam()
    A = D("A")
    gA = Baglam.terimlerden({"A": U, "a": A, "b": A})
    S1 = Cember()
    isler: List[Tuple[str, Callable[[], None]]] = [
        ("∞-grupoid: 1-morfizm tipi", lambda: denetle_t(morfizm_tipi(A, 1), U, gA)),
        ("∞-grupoid: 2-morfizm tipi", lambda: denetle_t(morfizm_tipi(A, 2), U, gA)),
        ("∞-grupoid: 3-morfizm tipi", lambda: denetle_t(morfizm_tipi(A, 3), U, gA)),
        ("koherens tipi (n=2)", lambda: denetle_t(koherens_tipi(A, 2), U, gA)),
        ("Küme tipi", lambda: denetle_t(kume_tipi(), U1, g)),
        ("Önerme tipi", lambda: denetle_t(onerme_tipi(), U1, g)),
        ("Grupoid tipi", lambda: denetle_t(grupoid_tipi(), U1, g)),
        ("2-tip tipi", lambda: denetle_t(n_tip_tipi(2), U1, g)),
        ("Monoid", lambda: denetle_t(monoid_tipi(), U1, g)),
        ("Grup", lambda: denetle_t(grup_tipi(), U1, g)),
        ("Değişmeli halka", lambda: denetle_t(halka_tipi(), U1, g)),
        ("Kategori", lambda: denetle_t(kategori_tipi(), U1, g)),
        ("Globüler tip (derinlik 3)", lambda: denetle_t(globuler_tip(3), U1, g)),
        ("S¹ : U", lambda: denetle_t(S1, U, g)),
        ("Ω(S¹) : U", lambda: denetle_t(dongu_uzayi(S1, Taban()), U, g)),
        ("Ω²(S¹) : U", lambda: denetle_t(dongu_uzayi_n(S1, Taban(), 2), U, g)),
        ("dongu³ : Ω(S¹)", lambda: denetle_t(dongu_kuvveti(3),
                                           yol(S1, Taban(), Taban()), g)),
        ("ℕ ayrık: 2+3=5", lambda: _esit_dene(
            DogalInd("_", Dogal(), dogal_sayi_peano(3), "k", "r",
                       Ard(D("r")), dogal_sayi_peano(2)), dogal_sayi_peano(5))),
        ("ℤ: sucZ(-1)=0", lambda: _esit_dene(
            Uygula(ardil_z(), tam_sayi(-1)), tam_sayi(0))),
    ]
    neticeler = [_dene(ad, f) for ad, f in isler]

    ps = sdg_postulatlari()
    gp = Baglam()
    for p in ps:
        neticeler.append(_dene("POSTULAT tipi iyi teşkil: %s" % p.ad,
                               lambda p=p, gp=gp: denetle_tip_yardimci(p.tip, gp)))
        gp = gp.genislet_t(p.ad, p.tip)
    ua_p = univalence_postulati()
    neticeler.append(_dene("POSTULAT tipi iyi teşkil: uaBeta",
                           lambda: denetle_tip_yardimci(ua_p.tip, Baglam())))

    neticeler.append(_dene("uaβ: transport (ua sucEquiv) 3 = 4",
                           lambda: _esit_dene(
                               tasi(ua(Tamsayi(), Tamsayi(),
                                           ardil_denkligi()),
                                      tam_sayi(3)), tam_sayi(4))))
    for n in (2, 3, -1):
        neticeler.append(_dene(
            "π₁(S¹): sarim(dongu^%d) = %d" % (n, n),
            lambda n=n: _esit_dene(sarim(dongu_kuvveti(n)),
                                   tam_sayi(n))))
    return neticeler


def denetle_tip_yardimci(t: Terim, g: Baglam) -> None:
    denetle_tip(t, g)


def _esit_dene(a: Terim, b: Terim) -> None:
    if not esdeger_mi(a, b):
        raise AssertionError("%s ≠ %s" % (nf(a), nf(b)))


def _ua_tasima_dene() -> None:
    A, B, EksikKural, x = D("A"), D("B"), D("EksikKural"), D("x")
    g = Baglam.terimlerden({"A": U, "B": U, "EksikKural": denklik_tipi(A, B), "x": A})
    geri_oku(g.d(tasi(ua(A, B, EksikKural), x)))


def _rapor_turetimler() -> str:
    satirlar = ["=" * 66,
                "omega_kategori -- türetim raporu",
                "=" * 66, "", "(A) HESAPLANAN ve TİP DENETİMİNDEN GEÇEN:"]
    gecti = kaldi = eksik = 0
    for n in dogrula_hepsi_turetimler():
        im = {"GEÇTİ": "  ✓ ", "EKSİK KURAL": "  ⊘ ", "HATA": "  ✗ "}[n["netice"]]
        satirlar.append("%s%s%s" % (im, n["ad"],
                                    "" if n["netice"] == "GEÇTİ"
                                    else "   [%s]" % n["netice"]))
        if n["netice"] == "GEÇTİ":
            gecti += 1
        elif n["netice"] == "EKSİK KURAL":
            eksik += 1
        else:
            kaldi += 1
    satirlar += ["", "hulâsa: %d geçti, %d eksik kural, %d hata"
                 % (gecti, eksik, kaldi), "",
                 "(C) BOŞLUK KÜTÜĞÜ:"]
    for b in bosluklar():
        satirlar.append("  • %s -- %s" % (b["ad"], b["durum"]))
        satirlar.append("      netice: %s" % b["netice"])
    satirlar.append("=" * 66)
    return "\n".join(satirlar)


U = Evren(0)


U1 = Evren(1)


D = Deg


def sdg_baglami() -> Baglam:
    return postulat_baglami(sdg_postulatlari())


R = D("R")


TOP = D("top_R")


CARP = D("carp_R")


SIFIR_R = D("sifir_R")


def _top(a: Terim, b: Terim) -> Terim:
    return terim_uygula(terim_uygula(TOP, a), b)


def _carp(a: Terim, b: Terim) -> Terim:
    return terim_uygula(terim_uygula(CARP, a), b)


def sonsuz_kucukler() -> Terim:
    x = terim_taze("x")
    return Sigma(x, R, yol(R, _carp(D(x), D(x)), SIFIR_R))


def sifir_sonsuz_kucuk() -> Terim:
    return Cift(SIFIR_R, D("sifir_kare"))


def teget_demeti(X: Terim) -> Terim:
    return ok(sonsuz_kucukler(), X)


def teget_izdusum(X: Terim) -> Terim:
    v = terim_taze("v")
    return Lam(v, terim_uygula(D(v), sifir_sonsuz_kucuk()))


def teget_lifi(X: Terim, x: Terim) -> Terim:
    v = terim_taze("v")
    return Sigma(v, teget_demeti(X),
                   yol(X, terim_uygula(D(v), sifir_sonsuz_kucuk()), x))


class Modul:

    __slots__ = ("V", "top", "sifir", "eks", "skaler")

    def __init__(self, V: Terim, top: Terim, sifir: Terim,
                 eks: Terim, skaler: Terim) -> None:
        self.V, self.top, self.sifir = V, top, sifir
        self.eks, self.skaler = eks, skaler

    def art(self, a: Terim, b: Terim) -> Terim:
        return terim_uygula(terim_uygula(self.top, a), b)

    def carp(self, c: Terim, a: Terim) -> Terim:
        return terim_uygula(terim_uygula(self.skaler, c), a)


def modul_tipi() -> Terim:
    V, top, sf, eks, sk = D("V"), D("top"), D("sf"), D("eks"), D("sk")
    x, y, z, c, d_ = D("x"), D("y"), D("z"), D("c"), D("d")
    A = lambda a, b: terim_uygula(terim_uygula(top, a), b)
    Sm = lambda c_, a: terim_uygula(terim_uygula(sk, c_), a)
    P = lambda ad, tip, govde: Pi(ad, tip, govde)
    return sigma_hepsi([
        ("V", U),
        ("kume", mertebe(V, 0)),
        ("top", ok(V, ok(V, V))),
        ("sf", V),
        ("eks", ok(V, V)),
        ("sk", ok(R, ok(V, V))),
        ("top_birlesme", P("x", V, P("y", V, P("z", V,
            yol(V, A(A(x, y), z), A(x, A(y, z))))))),
        ("top_degisme", P("x", V, P("y", V, yol(V, A(x, y), A(y, x))))),
        ("top_birim", P("x", V, yol(V, A(sf, x), x))),
        ("top_ters", P("x", V, yol(V, A(terim_uygula(eks, x), x), sf))),
        ("sk_dagilma_V", P("c", R, P("x", V, P("y", V,
            yol(V, Sm(c, A(x, y)), A(Sm(c, x), Sm(c, y))))))),
        ("sk_dagilma_R", P("c", R, P("d", R, P("x", V,
            yol(V, Sm(_top(c, d_), x), A(Sm(c, x), Sm(d_, x))))))),
    ], P("c", R, P("d", R, P("x", V,
        yol(V, Sm(_carp(c, d_), x), Sm(c, Sm(d_, x)))))))


def dogrusal_mi(M: Modul, N: Modul, f: Terim) -> Terim:
    x, y, c = terim_taze("x"), terim_taze("y"), terim_taze("c")
    uy = terim_uygula
    toplamsal = Pi(x, M.V, Pi(y, M.V,
        yol(N.V, uy(f, M.art(D(x), D(y))),
                   N.art(uy(f, D(x)), uy(f, D(y))))))
    homojen = Pi(c, R, Pi(x, M.V,
        yol(N.V, uy(f, M.carp(D(c), D(x))),
                   N.carp(D(c), uy(f, D(x))))))
    return carpim(toplamsal, homojen)


def skaler_modulu() -> Modul:
    return Modul(R, TOP, SIFIR_R, D("eks_R"), CARP)


def dual(M: Modul) -> Terim:
    f = terim_taze("f")
    return Sigma(f, ok(M.V, R), dogrusal_mi(M, skaler_modulu(), D(f)))


def cok_dogrusal_tip(yuvalar: Sequence[Terim], hedef: Terim) -> Terim:
    sonuc = hedef
    for V in reversed(list(yuvalar)):
        sonuc = ok(V, sonuc)
    return sonuc


def _yuvada_dogrusal(moduller: Sequence[Modul], N: Modul, f: Terim,
                     k: int) -> Terim:
    adlar = [terim_taze("a%d" % n) for n in range(len(moduller))]
    x, y, c = terim_taze("x"), terim_taze("y"), terim_taze("c")

    def uygula_hepsi(kth: Terim) -> Terim:
        arg = [D(a) for a in adlar]
        arg[k] = kth
        sonuc = f
        for a in arg:
            sonuc = terim_uygula(sonuc, a)
        return sonuc

    toplamsal = yol(N.V,
        uygula_hepsi(moduller[k].art(D(x), D(y))),
        N.art(uygula_hepsi(D(x)), uygula_hepsi(D(y))))
    homojen = yol(N.V,
        uygula_hepsi(moduller[k].carp(D(c), D(x))),
        N.carp(D(c), uygula_hepsi(D(x))))
    govde = Pi(x, moduller[k].V, Pi(y, moduller[k].V,
        carpim(toplamsal,
                 Pi(c, R, Pi(x, moduller[k].V, homojen)))))
    for n, a in enumerate(adlar):
        if n != k:
            govde = Pi(a, moduller[n].V, govde)
    return govde


def tensor_tipi(M: Modul, r: int, s: int) -> Terim:
    yuvalar = [dual(M)] * r + [M.V] * s
    return cok_dogrusal_tip(yuvalar, R)


def tensor_yapisi(M: Modul, r: int, s: int,
                  dualM: Optional[Modul] = None) -> Terim:
    if dualM is None:
        dualM = Modul(dual(M), D("dtop"), D("dsf"), D("deks"), D("dsk"))
    moduller = [dualM] * r + [M] * s
    f = terim_taze("f")
    tasiyici = cok_dogrusal_tip([m.V for m in moduller], R)
    sartlar: List[Tuple[str, Terim]] = [(f, tasiyici)]
    for n in range(len(moduller)):
        sartlar.append(("dogrusal_%d" % n,
                        _yuvada_dogrusal(moduller, skaler_modulu(), D(f), n)))
    son = sartlar.pop()[1]
    return sigma_hepsi(sartlar, son)


def teget_tensoru(X: Terim, x: Terim, r: int, s: int) -> Terim:
    Tx = teget_lifi(X, x)
    M = Modul(Tx, D("teget_top"), D("teget_sifir"), D("teget_eks"),
              D("teget_skaler"))
    return tensor_tipi(M, r, s)


def cebir_tipi() -> Terim:
    A, top, sf, eks, sk = D("A"), D("top"), D("sf"), D("eks"), D("sk")
    mu, eta = D("mu"), D("eta")
    x, y, z, c = D("x"), D("y"), D("z"), D("c")
    Ad = lambda a, b: terim_uygula(terim_uygula(top, a), b)
    Sm = lambda c_, a: terim_uygula(terim_uygula(sk, c_), a)
    M = lambda a, b: terim_uygula(terim_uygula(mu, a), b)
    P = Pi
    return sigma_hepsi([
        ("A", U),
        ("kume", mertebe(A, 0)),
        ("top", ok(A, ok(A, A))),
        ("sf", A),
        ("eks", ok(A, A)),
        ("sk", ok(R, ok(A, A))),
        ("mu", ok(A, ok(A, A))),
        ("eta", A),
        ("mu_birlesme", P("x", A, P("y", A, P("z", A,
            yol(A, M(M(x, y), z), M(x, M(y, z))))))),
        ("eta_sol", P("x", A, yol(A, M(eta, x), x))),
        ("eta_sag", P("x", A, yol(A, M(x, eta), x))),
        ("mu_dagilma_sol", P("x", A, P("y", A, P("z", A,
            yol(A, M(x, Ad(y, z)), Ad(M(x, y), M(x, z))))))),
        ("mu_dagilma_sag", P("x", A, P("y", A, P("z", A,
            yol(A, M(Ad(x, y), z), Ad(M(x, z), M(y, z))))))),
    ], P("c", R, P("x", A, P("y", A,
        yol(A, M(Sm(c, x), y), Sm(c, M(x, y)))))))


def lie_tipi() -> Terim:
    V, top, sf, eks, sk, br = (D("V"), D("top"), D("sf"), D("eks"),
                               D("sk"), D("br"))
    x, y, z = D("x"), D("y"), D("z")
    Ad = lambda a, b: terim_uygula(terim_uygula(top, a), b)
    B = lambda a, b: terim_uygula(terim_uygula(br, a), b)
    P = Pi
    jacobi = P("x", V, P("y", V, P("z", V,
        yol(V, Ad(Ad(B(B(x, y), z), B(B(y, z), x)), B(B(z, x), y)), sf))))
    return sigma_hepsi([
        ("V", U),
        ("kume", mertebe(V, 0)),
        ("top", ok(V, ok(V, V))),
        ("sf", V),
        ("eks", ok(V, V)),
        ("sk", ok(R, ok(V, V))),
        ("br", ok(V, ok(V, V))),
        ("antisimetri", P("x", V, P("y", V,
            yol(V, B(x, y), terim_uygula(eks, B(y, x)))))),
        ("br_dagilma", P("x", V, P("y", V, P("z", V,
            yol(V, B(x, Ad(y, z)), Ad(B(x, y), B(x, z))))))),
    ], jacobi)


def koherens_kulesi(V: Terim, sol: Terim, sag: Terim, n: int) -> Terim:
    tip = yol(V, sol, sag)
    nokta = refl(sol)
    for _ in range(n - 1):
        tip, nokta = yol(tip, nokta, nokta), refl(nokta)
    return tip


def alterne_form_tipi(M: Modul, n: int) -> Terim:
    return cok_dogrusal_tip([M.V] * n, R)


def form_uzayi(X: Terim, n: int) -> Terim:
    x = terim_taze("x")
    return Pi(x, X, alterne_form_tipi(
        Modul(teget_lifi(X, D(x)), D("teget_top"), D("teget_sifir"),
              D("teget_eks"), D("teget_skaler")), n))


def de_rham_postulatlari(X: Terim, n: int) -> List[Postulat]:
    om_n, om_n1, om_n2 = (form_uzayi(X, n), form_uzayi(X, n + 1),
                          form_uzayi(X, n + 2))
    w = terim_taze("w")
    dd = Pi(w, om_n, yol(om_n2,
        terim_uygula(D("d_%d1" % n), terim_uygula(D("d_%d" % n), D(w))),
        D("sifir_form")))
    return [
        Postulat("d_%d" % n, ok(om_n, om_n1),
                   "Dış türev Ωⁿ → Ωⁿ⁺¹."),
        Postulat("d_%d1" % n, ok(om_n1, om_n2),
                   "Dış türev Ωⁿ⁺¹ → Ωⁿ⁺²."),
        Postulat("sifir_form", om_n2, "Sıfır form."),
        Postulat("dd_sifir", dd, "d∘d = 0 -- de Rham kompleksinin şartı."),
    ]


def _geometri_baglami() -> Baglam:
    g = sdg_baglami()
    Dt = sonsuz_kucukler()
    X = D("X")
    g = g.genislet_t("sifir_kare", yol(R, _carp(SIFIR_R, SIFIR_R), SIFIR_R))
    g = g.genislet_t("eks_R", ok(R, R))
    g = g.genislet_t("X", U)
    g = g.genislet_t("x", X)
    Tx = teget_lifi(X, D("x"))
    g = g.genislet_t("teget_top", ok(Tx, ok(Tx, Tx)))
    g = g.genislet_t("teget_sifir", Tx)
    g = g.genislet_t("teget_eks", ok(Tx, Tx))
    g = g.genislet_t("teget_skaler", ok(R, ok(Tx, Tx)))
    return g


def dogrula_hepsi_geometri() -> List[Dict[str, str]]:
    g = _geometri_baglami()
    X, x = D("X"), D("x")
    M = Modul(D("V"), D("Vtop"), D("Vsf"), D("Veks"), D("Vsk"))
    gM = (g.genislet_t("V", U)
           .genislet_t("Vtop", ok(D("V"), ok(D("V"), D("V"))))
           .genislet_t("Vsf", D("V"))
           .genislet_t("Veks", ok(D("V"), D("V")))
           .genislet_t("Vsk", ok(R, ok(D("V"), D("V")))))
    dV = dual(M)
    dM = Modul(dV, D("dtop"), D("dsf"), D("deks"), D("dsk"))
    gMd = (gM.genislet_t("dtop", ok(dV, ok(dV, dV)))
             .genislet_t("dsf", dV)
             .genislet_t("deks", ok(dV, dV))
             .genislet_t("dsk", ok(R, ok(dV, dV))))
    isler: List[Tuple[str, Callable[[], None]]] = [
        ("D (sonsuz küçükler) : U", lambda: denetle_t(sonsuz_kucukler(), U, g)),
        ("0 ∈ D", lambda: denetle_t(sifir_sonsuz_kucuk(), sonsuz_kucukler(), g)),
        ("TX = X^D : U", lambda: denetle_t(teget_demeti(X), U, g)),
        ("π : TX → X", lambda: denetle_t(teget_izdusum(X),
                                       ok(teget_demeti(X), X), g)),
        ("T_x X : U", lambda: denetle_t(teget_lifi(X, x), U, g)),
        ("Mod_R : U₁", lambda: denetle_t(modul_tipi(), U1, g)),
        ("M* (dual) : U", lambda: denetle_t(dual(M), U, gM)),
        ("(1,0)-tensör : U", lambda: denetle_t(tensor_tipi(M, 1, 0), U, gM)),
        ("(0,2)-tensör (metrik) : U",
         lambda: denetle_t(tensor_tipi(M, 0, 2), U, gM)),
        ("(1,3)-tensör (Riemann) : U",
         lambda: denetle_t(tensor_tipi(M, 1, 3), U, gM)),
        ("(0,2)-tensör YAPISI (çok-doğrusallık şartlı) : U",
         lambda: denetle_t(tensor_yapisi(M, 0, 2), U, gM)),
        ("(1,1)-tensör YAPISI (dual yuvalı) : U",
         lambda: denetle_t(tensor_yapisi(M, 1, 1, dM), U, gMd)),
        ("teğet (0,2)-tensörü : U",
         lambda: denetle_t(teget_tensoru(X, x, 0, 2), U, g)),
        ("R-cebri (monoid nesnesi μ,η) : U₁",
         lambda: denetle_t(cebir_tipi(), U1, g)),
        ("Lie cebri (Jacobi dâhil) : U₁",
         lambda: denetle_t(lie_tipi(), U1, g)),
        ("Ω⁰(X) : U", lambda: denetle_t(form_uzayi(X, 0), U, g)),
        ("Ω²(X) : U", lambda: denetle_t(form_uzayi(X, 2), U, g)),
    ]
    neticeler = [_dene(ad, f) for ad, f in isler]

    a, b = D("a"), D("b")
    gk = g.genislet_t("A", U).genislet_t("a", D("A")).genislet_t("b", D("A"))
    for n in (1, 2, 3):
        neticeler.append(_dene(
            "koherens kulesi mertebe %d : U" % n,
            lambda n=n: denetle_t(koherens_kulesi(D("A"), a, a, n), U, gk)))

    gd = g
    for p in de_rham_postulatlari(X, 1):
        neticeler.append(_dene("POSTULAT tipi iyi teşkil: %s" % p.ad,
                                 lambda p=p, gd=gd: denetle_tip(p.tip, gd)))
        gd = gd.genislet_t(p.ad, p.tip)
    return neticeler


def _rapor_geometri() -> str:
    satirlar = ["=" * 66, "omega_kategori.geometri -- teğet / tensör / cebir",
                "=" * 66, ""]
    gecti = kaldi = 0
    for n in dogrula_hepsi_geometri():
        im = {"GEÇTİ": "  ✓ ", "EKSİK KURAL": "  ⊘ ", "HATA": "  ✗ "}[n["netice"]]
        satirlar.append("%s%s%s" % (im, n["ad"],
                                    "" if n["netice"] == "GEÇTİ"
                                    else "   [%s] %s" % (n["netice"],
                                                         n.get("izah", ""))))
        gecti += n["netice"] == "GEÇTİ"
        kaldi += n["netice"] != "GEÇTİ"
    satirlar += ["", "hulâsa: %d geçti, %d kaldı" % (gecti, kaldi), "=" * 66]
    return "\n".join(satirlar)


U = Evren(0)


U1 = Evren(1)


D = Deg


def bileske(f: Terim, g: Terim) -> Terim:
    x = terim_taze("x")
    return Lam(x, terim_uygula(g, terim_uygula(f, D(x))))


def geri_cek(f: Terim, P: Terim) -> Terim:
    x = terim_taze("x")
    return Lam(x, terim_uygula(P, terim_uygula(f, D(x))))


def toplam_it(X: Terim, Y: Terim, f: Terim, Q: Terim) -> Terim:
    y, x = terim_taze("y"), terim_taze("x")
    return Lam(y, Sigma(x, X,
        carpim(yol(Y, terim_uygula(f, D(x)), D(y)), terim_uygula(Q, D(x)))))


def carpim_it(X: Terim, Y: Terim, f: Terim, Q: Terim) -> Terim:
    y, x = terim_taze("y"), terim_taze("x")
    return Lam(y, Pi(x, X,
        ok(yol(Y, terim_uygula(f, D(x)), D(y)), terim_uygula(Q, D(x)))))


def _aile_oku(A: Terim, F1: Terim, F2: Terim) -> Terim:
    a = terim_taze("a")
    return Pi(a, A, ok(terim_uygula(F1, D(a)), terim_uygula(F2, D(a))))


def bitisiklik_sol_tipi(X: Terim, Y: Terim, f: Terim,
                        Q: Terim, P: Terim) -> Terim:
    return denklik_tipi(_aile_oku(Y, toplam_it(X, Y, f, Q), P),
                          _aile_oku(X, Q, geri_cek(f, P)))


def bitisiklik_sag_tipi(X: Terim, Y: Terim, f: Terim,
                        P: Terim, Q: Terim) -> Terim:
    return denklik_tipi(_aile_oku(X, geri_cek(f, P), Q),
                          _aile_oku(Y, P, carpim_it(X, Y, f, Q)))


def zincir_kurali_tipi(X: Terim, Z: Terim, f: Terim, g: Terim,
                       P: Terim) -> Terim:
    return yol(ok(X, U), geri_cek(bileske(f, g), P),
                 geri_cek(f, geri_cek(g, P)))


def zincir_kurali_ispati(X: Terim, Z: Terim, f: Terim, g: Terim,
                         P: Terim) -> Terim:
    return refl(geri_cek(bileske(f, g), P))


def monoidal_uyum_tipi(X: Terim, Y: Terim, f: Terim,
                       P: Terim, Q: Terim) -> Terim:
    y = terim_taze("y")
    carpim_ailesi = Lam(y, carpim(terim_uygula(P, D(y)), terim_uygula(Q, D(y))))
    x = terim_taze("x")
    sag = Lam(x, carpim(terim_uygula(geri_cek(f, P), D(x)),
                            terim_uygula(geri_cek(f, Q), D(x))))
    return yol(ok(X, U), geri_cek(f, carpim_ailesi), sag)


def monoidal_uyum_ispati(X: Terim, Y: Terim, f: Terim,
                         P: Terim, Q: Terim) -> Terim:
    y = terim_taze("y")
    carpim_ailesi = Lam(y, carpim(terim_uygula(P, D(y)), terim_uygula(Q, D(y))))
    return refl(geri_cek(f, carpim_ailesi))


def teget_donusumu(f: Terim) -> Terim:
    v, d = terim_taze("v"), terim_taze("d")
    return Lam(v, Lam(d, terim_uygula(f, terim_uygula(D(v), D(d)))))


def teget_zincir_tipi(X: Terim, Z: Terim, f: Terim, g: Terim) -> Terim:
    TX, TZ = teget_demeti(X), teget_demeti(Z)
    return yol(ok(TX, TZ), teget_donusumu(bileske(f, g)),
                 bileske(teget_donusumu(f), teget_donusumu(g)))


def teget_zincir_ispati(X: Terim, Z: Terim, f: Terim, g: Terim) -> Terim:
    return refl(teget_donusumu(bileske(f, g)))


def ayrik_mi(X: Terim) -> Terim:
    return mertebe(X, 0)


def yuksek_morfizmler_onemsiz_tipi(X: Terim) -> Terim:
    x = terim_taze("x")
    return ok(mertebe(X, 0),
                Pi(x, X, mertebe(dongu_uzayi(X, D(x)), -2)))


def yuksek_morfizmler_onemsiz_ispati(X: Terim) -> Terim:
    h, x, p = terim_taze("h"), terim_taze("x"), terim_taze("p")
    return Lam(h, Lam(x, Cift(
        refl(D(x)),
        Lam(p, terim_uygula(terim_uygula(terim_uygula(terim_uygula(D(h), D(x)), D(x)),
                                  refl(D(x))), D(p))))))


def ayrik_uzay_tipi() -> Terim:
    X = terim_taze("X")
    return Sigma(X, U, ayrik_mi(D(X)))


def ayrik_postulatlari() -> List[Postulat]:
    X = D("X")
    p0 = D("Pi0")
    x = terim_taze("x")
    return [
        Postulat("Pi0", ok(U, U),
                   "Π₀ : bağlantılı bileşenler / küme-kesmesi (0-truncation)."),
        Postulat("Pi0_kume", Pi("X", U, mertebe(terim_uygula(p0, X), 0)),
                   "Π₀X daima bir kümedir (0-kesilmiştir)."),
        Postulat("Pi0_birim", Pi("X", U, ok(X, terim_uygula(p0, X))),
                   "Birim dönüşüm X → Π₀X."),
    ]


def kritik_lokus(f: Terim) -> Terim:
    x, d = terim_taze("x"), terim_taze("d")
    kayma = terim_uygula(terim_uygula(TOP, D(x)), Birinci(D(d)))
    return Sigma(x, R, Pi(d, sonsuz_kucukler(),
        yol(R, terim_uygula(f, kayma), terim_uygula(f, D(x)))))


def tikanma_postulati(X: Terim) -> Postulat:
    return Postulat("tikanma", ok(ok(X, U), U),
                      "Bir ailenin global kesitinin varlığına engel olan "
                      "kohomolojik sınıf; sıfırdan farklıysa global inşa "
                      "imkânsızdır (tüylü top tipi haller).")


def evrensel_demet(M: Terim, F: Terim) -> Terim:
    w = terim_taze("w")
    return Sigma(w, M, terim_uygula(F, D(w)))


def demet_izdusumu(M: Terim, F: Terim) -> Terim:
    e = terim_taze("e")
    return Lam(e, Birinci(D(e)))


def agirlikta_lif(F: Terim, w: Terim) -> Terim:
    return terim_uygula(F, w)


def kesit_tipi(M: Terim, F: Terim) -> Terim:
    w = terim_taze("w")
    return Pi(w, M, terim_uygula(F, D(w)))


def lif_geri_cekme_ispati(M: Terim, F: Terim, w: Terim) -> Terim:
    return refl(terim_uygula(F, w))


def kip_postulatlari() -> List[Postulat]:
    tau = D("tau")
    X = D("X")
    return [
        Postulat("tau", ok(U, U),
                   "Kip (modality): belirli homotopi katmanlarını bükerek "
                   "doğrusal geçişi kıran funktor -- ReLU'nun mukabili."),
        Postulat("tau_birim", Pi("X", U, ok(X, terim_uygula(tau, X))),
                   "Kipin birim dönüşümü X → τX."),
        Postulat("tau_idempotent",
                   Pi("X", U, denklik_tipi(
                       terim_uygula(tau, terim_uygula(tau, X)), terim_uygula(tau, X))),
                   "Kip idempotenttir: τ(τX) ≃ τX."),
    ]


def _baglam() -> Baglam:
    g = _geometri_baglami()
    for ad, tip in [("Y", U), ("Z", U)]:
        g = g.genislet_t(ad, tip)
    X, Y, Z = D("X"), D("Y"), D("Z")
    g = g.genislet_t("f", ok(X, Y))
    g = g.genislet_t("gg", ok(Y, Z))
    g = g.genislet_t("P", ok(Z, U))
    g = g.genislet_t("PY", ok(Y, U))
    g = g.genislet_t("QY", ok(Y, U))
    g = g.genislet_t("Q", ok(X, U))
    g = g.genislet_t("M", U)
    g = g.genislet_t("Fw", ok(D("M"), U))
    g = g.genislet_t("w", D("M"))
    g = g.genislet_t("fR", ok(R, R))
    return g


def dogrula_hepsi_iliskiler() -> List[Dict[str, str]]:
    g = _baglam()
    X, Y, Z = D("X"), D("Y"), D("Z")
    f, gg = D("f"), D("gg")
    P, PY, QY, Q = D("P"), D("PY"), D("QY"), D("Q")
    M, Fw, w = D("M"), D("Fw"), D("w")

    isler: List[Tuple[str, Callable[[], None]]] = [
        ("f^* : (Y→U) → (X→U)",
         lambda: denetle_t(geri_cek(f, PY), ok(X, U), g)),
        ("Σ_f : (X→U) → (Y→U)",
         lambda: denetle_t(toplam_it(X, Y, f, Q), ok(Y, U), g)),
        ("Π_f : (X→U) → (Y→U)",
         lambda: denetle_t(carpim_it(X, Y, f, Q), ok(Y, U), g)),
        ("bitişiklik Σ_f ⊣ f^* (tip) : U",
         lambda: denetle_t(bitisiklik_sol_tipi(X, Y, f, Q, PY), U, g)),
        ("bitişiklik f^* ⊣ Π_f (tip) : U",
         lambda: denetle_t(bitisiklik_sag_tipi(X, Y, f, PY, Q), U, g)),
        ("ZİNCİR KURALI (g∘f)^* ≡ f^*∘g^*  [refl ile İSPAT]",
         lambda: denetle_t(zincir_kurali_ispati(X, Z, f, gg, P),
                         zincir_kurali_tipi(X, Z, f, gg, P), g)),
        ("MONOİDAL UYUM f^*(P×Q) ≡ f^*P × f^*Q  [refl ile İSPAT]",
         lambda: denetle_t(monoidal_uyum_ispati(X, Y, f, PY, QY),
                         monoidal_uyum_tipi(X, Y, f, PY, QY), g)),
        ("Tf : TX → TY",
         lambda: denetle_t(teget_donusumu(f),
                         ok(teget_demeti(X), teget_demeti(Y)), g)),
        ("TEĞET ZİNCİRİ T(g∘f) ≡ Tg∘Tf  [refl ile İSPAT]",
         lambda: denetle_t(teget_zincir_ispati(X, Z, f, gg),
                         teget_zincir_tipi(X, Z, f, gg), g)),
        ("Ayrık uzay tipi : U₁", lambda: denetle_t(ayrik_uzay_tipi(), U1, g)),
        ("AYRIKTA YÜKSEK MORFİZMLER ÖNEMSİZ  [İSPAT]",
         lambda: denetle_t(yuksek_morfizmler_onemsiz_ispati(X),
                         yuksek_morfizmler_onemsiz_tipi(X), g)),
        ("Kritik lokus Crit(f) : U",
         lambda: denetle_t(kritik_lokus(D("fR")), U, g)),
        ("Evrensel demet E = Σ(w:M). F w : U",
         lambda: denetle_t(evrensel_demet(M, Fw), U, g)),
        ("π : E → M",
         lambda: denetle_t(demet_izdusumu(M, Fw),
                         ok(evrensel_demet(M, Fw), M), g)),
        ("Kesit (öğrenilmiş ağırlık) Π(w:M). F w : U",
         lambda: denetle_t(kesit_tipi(M, Fw), U, g)),
        ("Lif geri çekme TANIMSAL  [refl ile İSPAT]",
         lambda: denetle_t(lif_geri_cekme_ispati(M, Fw, w),
                         yol(U, agirlikta_lif(Fw, w),
                               agirlikta_lif(Fw, w)), g)),
    ]
    neticeler = [_dene(ad, fn) for ad, fn in isler]

    gp = g
    for p in (ayrik_postulatlari() + kip_postulatlari()
              + [tikanma_postulati(X)]):
        neticeler.append(_dene("POSTULAT tipi iyi teşkil: %s" % p.ad,
                                 lambda p=p, gp=gp: denetle_tip(p.tip, gp)))
        gp = gp.genislet_t(p.ad, p.tip)
    return neticeler


def _rapor_iliskiler() -> str:
    satirlar = ["=" * 66,
                "omega_kategori.iliskiler -- uzaylar arası münasebetler",
                "=" * 66, ""]
    gecti = kaldi = 0
    for n in dogrula_hepsi_iliskiler():
        im = {"GEÇTİ": "  ✓ ", "EKSİK KURAL": "  ⊘ ", "HATA": "  ✗ "}[n["netice"]]
        satirlar.append("%s%s%s" % (im, n["ad"], "" if n["netice"] == "GEÇTİ"
                                    else "   [%s] %s" % (n["netice"],
                                                         n.get("izah", ""))))
        gecti += n["netice"] == "GEÇTİ"
        kaldi += n["netice"] != "GEÇTİ"
    satirlar += ["", "hulâsa: %d geçti, %d kaldı" % (gecti, kaldi), "=" * 66]
    return "\n".join(satirlar)


def _yuz_yaz(y) -> str:
    if not y:
        return "⊤"
    return "∧".join(sorted("(%s=%d)" % (ad, 1 if d else 0) for (ad, d) in y))


def _sistem_yaz(dallar) -> str:
    return ", ".join("%s ↦ %s" % (_yuz_yaz(y), terimi_yaz(t)) for (y, t) in dallar)


def terimi_yaz(t) -> str:
    y = terimi_yaz
    if isinstance(t, Deg):
        return t.ad
    if isinstance(t, Evren):
        return "U" if t.seviye == 0 else "U%d" % t.seviye
    if isinstance(t, Pi):
        if t.ad == "_":
            return "(%s → %s)" % (y(t.alan), y(t.hedef))
        return "((%s : %s) → %s)" % (t.ad, y(t.alan), y(t.hedef))
    if isinstance(t, Lam):
        return "(λ %s. %s)" % (t.ad, y(t.govde))
    if isinstance(t, Uygula):
        return "(%s %s)" % (y(t.fonk), y(t.arg))
    if isinstance(t, Sigma):
        if t.ad == "_":
            return "(%s × %s)" % (y(t.alan), y(t.hedef))
        return "((%s : %s) × %s)" % (t.ad, y(t.alan), y(t.hedef))
    if isinstance(t, Cift):
        return "(%s , %s)" % (y(t.bir), y(t.iki))
    if isinstance(t, Birinci):
        return "%s.1" % y(t.cift)
    if isinstance(t, Ikinci):
        return "%s.2" % y(t.cift)
    if isinstance(t, YolP):
        if t.ad == "_":
            return "(Path %s %s %s)" % (y(t.cizgi), y(t.sol), y(t.sag))
        return "(PathP (λ %s. %s) %s %s)" % (t.ad, y(t.cizgi), y(t.sol), y(t.sag))
    if isinstance(t, YolLam):
        return "(<%s> %s)" % (t.ad, y(t.govde))
    if isinstance(t, YolUygula):
        return "(%s @ %r)" % (y(t.yol), t.r)
    if isinstance(t, Transp):
        return "transp (λ %s. %s) %r %s" % (t.ad, y(t.cizgi), t.kof, y(t.u0))
    if isinstance(t, Komp):
        return "comp (λ %s. %s) [%s] %s" % (t.ad, y(t.cizgi),
                                            _sistem_yaz(t.dallar), y(t.u0))
    if isinstance(t, HKomp):
        return "hcomp {%s} (λ %s) [%s] %s" % (y(t.tip), t.ad,
                                              _sistem_yaz(t.dallar), y(t.u0))
    if isinstance(t, Yapistir):
        ic = ", ".join("%s ↦ (%s, %s)" % (_yuz_yaz(f), y(T), y(e))
                       for (f, T, e) in t.dallar)
        return "Glue %s [%s]" % (y(t.taban), ic)
    if isinstance(t, YapistirTerim):
        return "glue [%s] %s" % (_sistem_yaz(t.dallar), y(t.taban_terim))
    if isinstance(t, Coz):
        return "unglue %s" % y(t.govde)
    if isinstance(t, Belirtec):
        return "#%d" % t.id_no
    if isinstance(t, Dogal):
        return "ℕ"
    if isinstance(t, Sfr):
        return "0"
    if isinstance(t, Ard):
        n, alt = 0, t
        while isinstance(alt, Ard):
            n += 1
            alt = alt.alt
        if isinstance(alt, Sfr):
            return str(n)
        return "(%d+%s)" % (n, y(alt))
    if isinstance(t, DogalInd):
        return "natInd(...; %s)" % y(t.sayi)
    if isinstance(t, Tamsayi):
        return "ℤ"
    if isinstance(t, Poz):
        return "+%s" % y(t.alt)
    if isinstance(t, NegArd):
        return "-(1+%s)" % y(t.alt)
    if isinstance(t, TamsayiInd):
        return "intInd(...; %s)" % y(t.sayi)
    if isinstance(t, Cember):
        return "S¹"
    if isinstance(t, Taban):
        return "taban"
    if isinstance(t, Dongu):
        return "(dongu %r)" % t.r
    if isinstance(t, CemberInd):
        return "S¹ind(...; %s)" % y(t.nokta)
    return object.__repr__(t)


BOLUMLER = (
    ("TÜRETİMLER -- ∞-grupoid kulesi, ℕ, ℤ, S¹, postulatlar",
     "_rapor_turetimler"),
    ("SDG -- sonsuz küçükler, teğet demeti, de Rham", "_rapor_geometri"),
    ("MÜNASEBETLER -- geri çekme, bitişiklik, demetler",
     "_rapor_iliskiler"),
)


def rapor() -> str:
    s = []
    for baslik, fn in BOLUMLER:
        s.append("")
        s.append("=" * 70)
        s.append("  " + baslik)
        s.append("=" * 70)
        s.append(globals()[fn]())
    return "\n".join(s)


def tipini_ver(t: Terim, g: Optional[Baglam] = None) -> Deger:
    return sentezle(t, g if g is not None else Baglam())


def serbest_sayisi(t: Terim) -> int:
    return len(serbest(t))


def _alt_terimler(t: Terim) -> List[Terim]:
    if isinstance(t, (YonluHom, YonluOk)):
        return [t.cizgi, t.kaynak, t.hedef]
    if isinstance(t, YonluTerkip):
        return [t.f, t.g]
    if isinstance(t, (OperadAgac, OperadHom)):
        return [t.cizgi] + list(t.oncutler) + [t.hedef]
    if isinstance(t, OperadSilsile):
        altlar = [t.cizgi] + list(t.baslangic_oncutler) + [t.nihai_hedef]
        for a, b in t.adimlar:
            altlar.extend([a, b])
        return altlar
    if isinstance(t, Pi) or isinstance(t, Sigma):
        return [t.alan, t.hedef]
    if isinstance(t, Lam):
        return [t.govde]
    if isinstance(t, Uygula):
        return [t.fonk, t.arg]
    if isinstance(t, Cift):
        return [t.bir, t.iki]
    if isinstance(t, (Birinci, Ikinci)):
        return [t.cift]
    if isinstance(t, (Ard, Poz, NegArd)):
        return [t.alt]
    if isinstance(t, DogalInd):
        return [t.hedef, t.sfr_dali, t.ard_dali, t.sayi]
    if isinstance(t, TamsayiInd):
        return [t.hedef, t.poz_dali, t.neg_dali, t.sayi]
    if isinstance(t, CemberInd):
        return [t.hedef, t.taban_dali, t.dongu_dali, t.nokta]
    return []

def serbest(t: Terim) -> Set[str]:
    g: Set[str] = set()

    def yur(t: Terim, bagli: Set[str]) -> None:
        if isinstance(t, Deg):
            if t.ad not in bagli:
                g.add(t.ad)
            return
        if isinstance(t, (Pi, Sigma)):
            yur(t.alan, bagli)
            yur(t.hedef, bagli | {t.ad})
            return
        if isinstance(t, Lam):
            yur(t.govde, bagli | {t.ad})
            return
        if isinstance(t, DogalInd):
            yur(t.hedef, bagli | {t.ad})
            yur(t.sfr_dali, bagli)
            yur(t.ard_dali, bagli | {t.n_ad, t.rec_ad})
            yur(t.sayi, bagli)
            return
        if isinstance(t, TamsayiInd):
            yur(t.hedef, bagli | {t.ad})
            yur(t.poz_dali, bagli | {t.poz_ad})
            yur(t.neg_dali, bagli | {t.neg_ad})
            yur(t.sayi, bagli)
            return
        if isinstance(t, CemberInd):
            yur(t.hedef, bagli | {t.ad})
            yur(t.taban_dali, bagli)
            yur(t.dongu_dali, bagli)
            yur(t.nokta, bagli)
            return
        if isinstance(t, YolP):
            yur(t.cizgi, bagli)
            yur(t.sol, bagli)
            yur(t.sag, bagli)
            return
        if isinstance(t, YolLam):
            yur(t.govde, bagli)
            return
        if isinstance(t, YolUygula):
            yur(t.yol, bagli)
            return
        if isinstance(t, Transp):
            yur(t.cizgi, bagli)
            yur(t.u0, bagli)
            return
        if isinstance(t, Komp):
            yur(t.cizgi, bagli)
            for (_, govde) in t.dallar:
                yur(govde, bagli)
            yur(t.u0, bagli)
            return
        if isinstance(t, HKomp):
            yur(t.tip, bagli)
            for (_, govde) in t.dallar:
                yur(govde, bagli)
            yur(t.u0, bagli)
            return
        if isinstance(t, Yapistir):
            yur(t.taban, bagli)
            for (_, T, e) in t.dallar:
                yur(T, bagli)
                yur(e, bagli)
            return
        if isinstance(t, YapistirTerim):
            yur(t.taban_terim, bagli)
            for (_, govde) in t.dallar:
                yur(govde, bagli)
            return
        if isinstance(t, Coz):
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

def _yuz_i_den_bagimsiz(y: Yuz, ad: str) -> bool:
    return all(a != ad for (a, _) in y)


class TipHatasi(Exception):
    pass


RED_HATALARI: Tuple[type, ...] = (DenetimHatasi, CekirdekHatasi, TipHatasi)


def iz_butun(X: Terim) -> Terim:
    x, y = terim_taze("x"), terim_taze("y")
    return Sigma(x, X, Pi(y, X, yol(X, _t(x), _t(y))))


def iz_onerme(X: Terim) -> Terim:
    x, y = terim_taze("x"), terim_taze("y")
    return Pi(x, X, Pi(y, X, yol(X, _t(x), _t(y))))


def iz_kume(X: Terim) -> Terim:
    x, y = terim_taze("x"), terim_taze("y")
    return Pi(x, X, Pi(y, X, iz_onerme(yol(X, _t(x), _t(y)))))


def iz_grupoid(X: Terim) -> Terim:
    x, y = terim_taze("x"), terim_taze("y")
    return Pi(x, X, Pi(y, X, iz_kume(yol(X, _t(x), _t(y)))))


def n_mertebe(X: Terim, n: int) -> Terim:
    if n <= -2:
        return iz_butun(X)
    if n == -1:
        return iz_onerme(X)
    x, y = terim_taze("x"), terim_taze("y")
    return Pi(x, X, Pi(y, X, n_mertebe(yol(X, _t(x), _t(y)), n - 1)))


MERTEBE_ADI: Tuple[str, ...] = ("nokta", "uzay", "tip", "grupoid")


def mertebe_sarti(X: Terim, l: int) -> Terim:
    assert 0 <= int(l) < len(MERTEBE_ADI), (
        "vecih mertebesi 0..%d aralığında olmalı, %d verildi (ferman 1-Ğ)"
        % (len(MERTEBE_ADI) - 1, int(l)))
    return n_mertebe(X, int(l) - 1)



def hakiki_rn_mertebe(X: Terim, r: int, n: int) -> Terim:
    r_seviye = max(0, int(r))
    n_seviye = int(n)

    def _adim(T: Terim, k: int) -> Terim:
        if k > n_seviye:
            return T
        a, b = terim_taze("a"), terim_taze("b")
        morfizm = yonlu_hom(T, Deg(a), Deg(b)) if k <= r_seviye else yol(T, Deg(a), Deg(b))
        return Pi(a, T, Pi(b, T, _adim(morfizm, k + 1)))

    return _adim(X, 1)


def hakiki_rn_sarti(X: Terim, r: int, n: int) -> Terim:
    assert int(r) >= 0 and int(n) >= 0, "Mertebeler negatif olamaz"
    return hakiki_rn_mertebe(X, int(r), int(n))


def buzukten_tamamla(X: Terim, buzuk: Terim, dallar) -> Terim:
    c = birinci(buzuk)
    h = ikinci(buzuk)
    j = terim_taze("j")
    j_ar = Aralik.degisken(j)
    yeni = [(y, terim_yol_uygula(terim_uygula(h, govde), j_ar))
            for (y, govde) in dallar]
    return terim_hkomp(X, j, yeni, c)


def denklikle_tamamla(A: Terim, B: Terim, e: Terim, b: Terim,
                      dallar) -> Terim:
    X = lif(A, B, birinci(e), b)
    buzuk = terim_uygula(ikinci(e), b)
    return buzukten_tamamla(X, buzuk, dallar)


_ONBELLEK_SINIRI = 400000
_whnf_onb: Dict = {}
_komp_onb: Dict = {}
_baglam_capa: List = []
_baglam_kimlik: Set[int] = set()
_WHNF_SAYAC: Dict[str, int] = {"çağrı": 0, "önbellek": 0, "eleme": 0,
                               "tam_kıyas": 0}
WHNF_ELEMESI = [1]


def _ust_yuz(dallar) -> Optional[Terim]:
    for dal in dallar:
        if not dal[0]:
            return dal[1]
    return None


def _dallari_yeniden_adlandir(dallar, eski: str, yeni: str):
    return [(y, ara_ikame(g, {eski: Aralik.degisken(yeni)})) for (y, g) in dallar]


def _ileri(ad: str, cizgi: Terim, r: Aralik, x: Terim) -> Terim:
    j = terim_taze("j")
    j_ar = Aralik.degisken(j)
    yeni = ara_ikame(cizgi, {ad: r.veya(j_ar)})
    return transp(j, yeni, aralik_esitligi(r, True), x)


def _geri(ad: str, cizgi: Terim, r: Aralik, v: Terim) -> Terim:
    j = terim_taze("j")
    j_ar = Aralik.degisken(j)
    yeni = ara_ikame(cizgi, {ad: r.veya(j_ar.degil())})
    return transp(j, yeni, aralik_esitligi(r, True), v)


def _komp_ac(ad: str, cizgi: Terim, dallar, u0: Terim,
             baglam=None) -> Terim:
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
                     baglam=None) -> Terim:


    for (y, govde) in dallar:
        if not y:
            return whnf(ara_ikame(govde, {ad: BIR}), baglam)

    A = whnf(cizgi, baglam)


    if not dallar:
        if ad not in ara_serbest(A):
            return u0
        duz = nf(cizgi, baglam)
        if ad not in ara_serbest(duz):
            return u0
        A = whnf(duz, baglam)

    i_ar = Aralik.degisken(ad)


    if isinstance(A, Pi):
        v = terim_taze("v")
        v_t = Deg(v)

        w_i = _geri(ad, A.alan, i_ar, v_t)
        w_0 = ara_ikame(w_i, {ad: SIFIR})
        yeni_cizgi = ikame(A.hedef, {A.ad: w_i})
        yeni_dallar = [(y, uygula(g, w_i)) for (y, g) in dallar]
        return Lam(v, komp(ad, yeni_cizgi, yeni_dallar,
                             uygula(u0, w_0), baglam))


    if isinstance(A, Sigma):
        bir_dallar = [(y, birinci(g)) for (y, g) in dallar]
        a_i = dolgu(ad, A.alan, bir_dallar, birinci(u0))
        bir_sonuc = komp(ad, A.alan, bir_dallar, birinci(u0), baglam)
        iki_cizgi = ikame(A.hedef, {A.ad: a_i})
        iki_dallar = [(y, ikinci(g)) for (y, g) in dallar]
        iki_sonuc = komp(ad, iki_cizgi, iki_dallar, ikinci(u0), baglam)
        return Cift(bir_sonuc, iki_sonuc)


    if isinstance(A, YolP):
        j = terim_taze("j")
        j_ar = Aralik.degisken(j)
        ic_cizgi = ara_ikame(A.cizgi, {A.ad: j_ar})
        ic_dallar = [(y, yol_uygula(g, j_ar)) for (y, g) in dallar]
        ic_dallar.append((yuz(**{j: 0}), A.sol))
        ic_dallar.append((yuz(**{j: 1}), A.sag))
        govde = komp(ad, ic_cizgi, ic_dallar, yol_uygula(u0, j_ar), baglam)
        return YolLam(j, govde)


    if isinstance(A, (Dogal, Tamsayi)):
        u0w = whnf(u0, baglam)
        govdeler = [whnf(g, baglam) for (_, g) in dallar]
        yuzler = [y for (y, _) in dallar]

        def _ic(ic_tip, alt_u0, altlar):
            return komp(ad, ic_tip, list(zip(yuzler, altlar)), alt_u0, baglam)

        if isinstance(u0w, Sfr) and all(isinstance(x, Sfr) for x in govdeler):
            return Sfr()
        if isinstance(u0w, Ard) and all(isinstance(x, Ard) for x in govdeler):
            return Ard(_ic(Dogal(), u0w.alt, [x.alt for x in govdeler]))
        if isinstance(u0w, Poz) and all(isinstance(x, Poz) for x in govdeler):
            return Poz(_ic(Dogal(), u0w.alt, [x.alt for x in govdeler]))
        if isinstance(u0w, NegArd) and all(isinstance(x, NegArd)
                                             for x in govdeler):
            return NegArd(_ic(Dogal(), u0w.alt, [x.alt for x in govdeler]))
        return Komp(ad, cizgi, dallar, u0)


    if isinstance(A, Cember):
        if not dallar:
            return whnf(u0, baglam)
        return HKomp(Cember(), ad, dallar, u0)


    if isinstance(A, Evren):
        from .denklik import cizgi_denkligi
        taban = u0
        yeni_dallar = []
        for (y, g) in dallar:
            T1 = ara_ikame(g, {ad: BIR})


            k = terim_taze("k")
            ters = ara_ikame(g, {ad: Aralik.degisken(k).degil()})
            yeni_dallar.append((y, T1, cizgi_denkligi(k, ters)))
        return yapistir(taban, yeni_dallar)


    if isinstance(A, Yapistir):
        from .denklik import komp_yapistir
        return komp_yapistir(ad, A, dallar, u0, baglam)


    return Komp(ad, cizgi, dallar, u0)


def whnf(t: Terim, baglam=None) -> Terim:
    _WHNF_SAYAC["çağrı"] += 1
    anahtar = (id(baglam), t)
    onb = _whnf_onb.get(anahtar)
    if onb is not None:
        _WHNF_SAYAC["önbellek"] += 1
        return onb
    sonuc = _whnf_hesapla(t, baglam)
    if len(_whnf_onb) < _ONBELLEK_SINIRI:
        _capala(baglam)
        _whnf_onb[anahtar] = sonuc
    return sonuc


def _whnf_hesapla(t: Terim, baglam=None) -> Terim:
    while True:
        if isinstance(t, Uygula):
            f = whnf(t.fonk, baglam)
            if isinstance(f, Lam):
                t = ikame(f.govde, {f.ad: t.arg})
                continue
            return Uygula(f, t.arg)
        if isinstance(t, Birinci):
            c = whnf(t.cift, baglam)
            if isinstance(c, Cift):
                t = c.bir
                continue
            return Birinci(c)
        if isinstance(t, Ikinci):
            c = whnf(t.cift, baglam)
            if isinstance(c, Cift):
                t = c.iki
                continue
            return Ikinci(c)
        if isinstance(t, YolUygula):
            p = whnf(t.yol, baglam)
            if isinstance(p, YolLam):
                t = ara_ikame(p.govde, {p.ad: t.r})
                continue

            if (t.r.sifir_mi() or t.r.bir_mi()) and baglam is not None:
                tip = _whnf_sentez(p, baglam)
                if tip is not None:
                    tip = whnf(tip, baglam)
                    if isinstance(tip, YolP):
                        t = tip.sol if t.r.sifir_mi() else tip.sag
                        continue
            return YolUygula(p, t.r)
        if isinstance(t, Dongu):
            if t.r.sifir_mi() or t.r.bir_mi():
                return Taban()
            return t
        if isinstance(t, Meridyen):
            if t.i_aralik.sifir_mi():
                return KuzeyKutup(t.uzay)
            if t.i_aralik.bir_mi():
                return GuneyKutup(t.uzay)
            return t
        if isinstance(t, DogalInd):
            s = whnf(t.sayi, baglam)
            if isinstance(s, (Sfr, Ard)):
                t = dogal_ind(t.ad, t.hedef, t.sfr_dali, t.n_ad, t.rec_ad,
                              t.ard_dali, s)
                continue
            return DogalInd(t.ad, t.hedef, t.sfr_dali, t.n_ad, t.rec_ad,
                              t.ard_dali, s)
        if isinstance(t, TamsayiInd):
            s = whnf(t.sayi, baglam)
            if isinstance(s, (Poz, NegArd)):
                t = tamsayi_ind(t.ad, t.hedef, t.poz_ad, t.poz_dali,
                                t.neg_ad, t.neg_dali, s)
                continue
            return TamsayiInd(t.ad, t.hedef, t.poz_ad, t.poz_dali,
                                t.neg_ad, t.neg_dali, s)
        if isinstance(t, CemberInd):
            n = whnf(t.nokta, baglam)
            if isinstance(n, (Taban, Dongu, HKomp)):
                yeni = cember_ind(t.ad, t.hedef, t.taban_dali, t.i_ad,
                                  t.dongu_dali, n)
                if yeni != t:
                    t = yeni
                    continue
            return CemberInd(t.ad, t.hedef, t.taban_dali, t.i_ad,
                               t.dongu_dali, n)
        if isinstance(t, Komp):
            yeni = _komp_ac(t.ad, t.cizgi, t.dallar, t.u0, baglam)
            if yeni == t:
                return t
            t = yeni
            continue
        if isinstance(t, HKomp):
            yeni = _komp_ac(t.ad, t.tip, t.dallar, t.u0, baglam)
            if yeni == t:
                return t
            t = yeni
            continue
        if isinstance(t, Transp):
            t = transp(t.ad, t.cizgi, t.kof, t.u0)
            continue
        if isinstance(t, Coz):
            g = whnf(t.govde, baglam)
            yeni = coz(t.taban, t.dallar, g)
            if yeni == t or yeni == Coz(t.taban, t.dallar, g):
                return Coz(t.taban, t.dallar, g)
            t = yeni
            continue
        if isinstance(t, Yapistir):
            yeni = yapistir(t.taban, t.dallar)
            if yeni == t:
                return t
            t = yeni
            continue
        if isinstance(t, YapistirTerim):
            yeni = yapistir_terim(t.dallar, t.taban_terim)
            if yeni == t:
                return t
            t = yeni
            continue
        if isinstance(t, YonluTerkip):
            f_ind = whnf(t.f, baglam)
            g_ind = whnf(t.g, baglam)
            if f_ind is t.f and g_ind is t.g:
                return t
            t = YonluTerkip(f_ind, g_ind)
            continue
        return t


def _whnf_sentez(t: Terim, baglam) -> Optional[Terim]:
    if isinstance(t, Deg):
        return baglam.get(t.ad)
    if isinstance(t, Uygula):
        ft = _whnf_sentez(t.fonk, baglam)
        if ft is None:
            return None
        ft = whnf(ft, baglam)
        if isinstance(ft, Pi):
            return ikame(ft.hedef, {ft.ad: t.arg})
        return None
    if isinstance(t, Birinci):
        ct = _whnf_sentez(t.cift, baglam)
        if ct is None:
            return None
        ct = whnf(ct, baglam)
        return ct.alan if isinstance(ct, Sigma) else None
    if isinstance(t, Ikinci):
        ct = _whnf_sentez(t.cift, baglam)
        if ct is None:
            return None
        ct = whnf(ct, baglam)
        if isinstance(ct, Sigma):
            return ikame(ct.hedef, {ct.ad: birinci(t.cift)})
        return None
    if isinstance(t, YolUygula):
        pt = _whnf_sentez(t.yol, baglam)
        if pt is None:
            return None
        pt = whnf(pt, baglam)
        if isinstance(pt, YolP):
            return ara_ikame(pt.cizgi, {pt.ad: t.r})
        return None

    if isinstance(t, DogalInd):
        return ikame(t.hedef, {t.ad: t.sayi})
    if isinstance(t, TamsayiInd):
        return ikame(t.hedef, {t.ad: t.sayi})
    if isinstance(t, CemberInd):
        return ikame(t.hedef, {t.ad: t.nokta})
    if isinstance(t, (Komp, Transp)):
        return ara_ikame(t.cizgi, {t.ad: BIR})
    if isinstance(t, HKomp):
        return t.tip
    if isinstance(t, Coz):
        return t.taban
    if isinstance(t, YapistirTerim):
        return None
    return None


def _capala(baglam) -> None:
    if baglam is not None and id(baglam) not in _baglam_kimlik:
        _baglam_kimlik.add(id(baglam))
        _baglam_capa.append(baglam)


def onbellegi_bosalt() -> None:
    _whnf_onb.clear()
    _komp_onb.clear()
    _ara_serbest_onb.clear()
    _baglam_capa.clear()
    _baglam_kimlik.clear()
    for k in _WHNF_SAYAC:
        _WHNF_SAYAC[k] = 0


def whnf_beyani() -> str:
    c = _WHNF_SAYAC
    cag = max(int(c["çağrı"]), 1)
    kiy = max(int(c["eleme"]) + int(c["tam_kıyas"]), 1)
    return "\n".join([
        "  ZAYIF-BAŞ NORMAL FORM (whnf) -- tembel indirgeme",
        "    çağrı %d   önbellekten karşılanan %d  (%%%.1f)"
        % (c["çağrı"], c["önbellek"], 100.0 * c["önbellek"] / cag),
        "    eşdeğerlik kıyası: baş ile elenen %d / %d  (%%%.1f)"
        % (c["eleme"], kiy, 100.0 * c["eleme"] / kiy),
        "    eleme KAPATILABİLİR (WHNF_ELEMESI[0] = 0): kapatılınca",
        "    netice aynı kalır, yalnız tam normal form hesaplanır --",
        "    yâni bu bir HIZ cevheridir, doğruluk cevheri değil."])


_BAS_KAPALI = (Evren, Pi, Sigma, YolP, Dogal, Tamsayi, Cember, Taban,
               Lam, Cift, YolLam, Sfr, Ard, Poz, NegArd, Belirtec,
               YonluHom, YonluOk, OperadHom, OperadAgac, OperadSilsile)


def _bas_ayrisiyor(a: Terim, b: Terim, baglam=None) -> bool:
    ha, hb = whnf(a, baglam), whnf(b, baglam)
    if not isinstance(ha, _BAS_KAPALI) or not isinstance(hb, _BAS_KAPALI):
        return False
    if type(ha) is not type(hb):
        return True
    if isinstance(ha, Evren):
        return ha.seviye != hb.seviye
    return False


_TURETIM_SAYI: Dict[str, int] = {}


_TURETIM_NISPET: Dict[str, float] = {}


def turetim_beyani() -> Dict[str, Any]:
    b: Dict[str, Any] = {k: int(v) for k, v in _TURETIM_SAYI.items()}
    b.update({k: float(v) for k, v in _TURETIM_NISPET.items()})
    return b


def veriden_geometri_cikar(w: Sequence[int], n: int, K_max: int = 4
                           ) -> Tuple[np.ndarray, np.ndarray,
                                      Dict[Tuple[Tuple[int, ...], int], float]]:
    w_arr = np.asarray(list(w), dtype=np.int64)
    m = int(n)
    assert len(w_arr) >= 2, "Dizi en az 2 belirteç içermelidir"

    N_gecis = np.zeros((m, m), dtype=float)
    np.add.at(N_gecis, (w_arr[:-1], w_arr[1:]), 1.0)

    cikis_toplami = N_gecis.sum(axis=1, keepdims=True) + 1e-12
    P = N_gecis / cikis_toplami

    pay = np.abs(P - P.T)
    payda = P + P.T + 1e-12
    Asim = pay / payda

    ham_korollalar: Dict[Tuple[Tuple[int, ...], int], int] = {}
    ust = min(int(K_max), len(w_arr))
    for k in range(2, ust + 1):
        for t in range(k - 1, len(w_arr)):
            girdi = tuple(w_arr[t - k + 1:t].tolist())
            cikti = int(w_arr[t])
            anahtar = (girdi, cikti)
            ham_korollalar[anahtar] = ham_korollalar.get(anahtar, 0) + 1

    toplam_korolla = float(sum(ham_korollalar.values())) + 1e-12
    norm_korollalar = {k: v / toplam_korolla for k, v in ham_korollalar.items()}

    return P, Asim, norm_korollalar


def asimetri_guncelle(P: np.ndarray) -> np.ndarray:
    pay = np.abs(P - P.T)
    payda = P + P.T + 1e-12
    return pay / payda


def yerel_baglamsal_hodge(baglam: Tuple[int, ...], P: np.ndarray,
                          norm_korollalar: Dict[Tuple[Tuple[int, ...], int], float]
                          ) -> Dict[str, float]:
    aktif_dugumler = set(baglam)
    for (girdi, cikti) in norm_korollalar:
        if any(x in aktif_dugumler for x in girdi):
            aktif_dugumler.update(girdi)
            aktif_dugumler.add(cikti)

    dugum_listesi = list(aktif_dugumler)
    d_map = {d: i for i, d in enumerate(dugum_listesi)}
    k = len(dugum_listesi)

    if k < 2:
        return {"uzay_gradyan": 0.5, "kategori_girdap": 0.5, "yırtık_harmonik": 0.0}

    yerel_kenarlar = []
    yerel_akis = []
    for i_d in dugum_listesi:
        for j_d in dugum_listesi:
            if P[i_d, j_d] > 1e-4:
                yerel_kenarlar.append((d_map[i_d], d_map[j_d]))
                yerel_akis.append(P[i_d, j_d])

    e_sayisi = len(yerel_kenarlar)
    if e_sayisi == 0:
        return {"uzay_gradyan": 0.5, "kategori_girdap": 0.5, "yırtık_harmonik": 0.0}

    B1 = np.zeros((k, e_sayisi), dtype=float)
    for idx, (i, j) in enumerate(yerel_kenarlar):
        B1[i, idx] -= 1.0
        B1[j, idx] += 1.0

    akis = np.array(yerel_akis, dtype=float)
    akis /= (np.linalg.norm(akis) + 1e-12)

    L0 = B1 @ B1.T
    div = B1 @ akis
    phi, _, _, _ = np.linalg.lstsq(L0 + 1e-6 * np.eye(k), div, rcond=None)
    akis_gradyan = B1.T @ phi

    akis_kalan = akis - akis_gradyan
    e_grad = float(np.sum(akis_gradyan ** 2))
    e_kalan = float(np.sum(akis_kalan ** 2))
    top = e_grad + e_kalan + 1e-12

    return {
        "uzay_gradyan": e_grad / top,
        "kategori_girdap": e_kalan / top,
        "yırtık_harmonik": float(np.clip(1.0 - (e_grad + e_kalan) / top, 0.0, 1.0))
    }


def topos_tayfi_hodge_ile_hesapla(P: np.ndarray, Asim: np.ndarray,
                                  norm_korollalar: Dict[Tuple[Tuple[int, ...], int], float],
                                  baglam: Tuple[int, ...]
                                  ) -> Dict[str, Any]:
    hodge = yerel_baglamsal_hodge(baglam, P, norm_korollalar)
    E_uzay = float(hodge["uzay_gradyan"])
    E_kategori = float(hodge["kategori_girdap"])
    E_tikanma = float(hodge["yırtık_harmonik"])

    coklu_korollalar = {k: v for k, v in norm_korollalar.items() if len(k[0]) >= 2}
    if coklu_korollalar:
        toplam_coklu = sum(coklu_korollalar.values()) + 1e-12
        azami_arite = max((len(girdi) for (girdi, _) in coklu_korollalar), default=2)
        norm_payda = float(max(1, azami_arite - 1))
        E_operad = float(sum(((len(girdi) - 1) / norm_payda) * (prob / toplam_coklu)
                             for (girdi, _), prob in coklu_korollalar.items()))
        E_operad *= (toplam_coklu / (sum(norm_korollalar.values()) + 1e-12))
    else:
        E_operad = 0.0

    E_toplam = E_uzay + E_kategori + E_operad + E_tikanma + 1e-12
    rho = np.array([E_uzay / E_toplam, E_kategori / E_toplam,
                    E_operad / E_toplam, E_tikanma / E_toplam], dtype=float)

    entropi = float(-np.sum(rho * np.log(rho + 1e-12)))

    P2 = P @ P
    Kan_rezidusu = np.abs(P - P2)
    yirtiklar = (P2 > 0.05) & (P < 0.01)
    beta = float(np.sum(P2[yirtiklar])) / float(np.sum(P2) + 1e-12)
    alfa = float(np.mean(Asim[P > 0])) if np.any(P > 0) else 0.0

    if beta < 0.05:
        cebir = "boole" if alfa < 0.25 else "yönlü_kafes"
    else:
        cebir = "heyting" if alfa < 0.5 else "yönlü_heyting"

    return {
        "tayf": rho, "entropi": entropi, "Ω_cebiri": cebir,
        "enerjiler": {"uzay": E_uzay, "kategori": E_kategori,
                     "operad": E_operad, "tıkanma": E_tikanma},
        "P": P, "P2": P2, "Asim": Asim, "Kan_rezidusu": Kan_rezidusu,
        "alfa": alfa, "beta": beta
    }


def s0_gercek_baglam_cagir(secilen_gaye: int, norm_korollalar: Dict[Tuple[Tuple[int, ...], int], float],
                           varsayilan_n: int) -> List[int]:
    aday_baglamlar = [girdi for (girdi, cikti) in norm_korollalar if cikti == secilen_gaye]
    if aday_baglamlar:
        en_iyi_baglam = max(aday_baglamlar, key=len)
        return list(en_iyi_baglam) + [secilen_gaye]
    return [secilen_gaye]


def analitik_lie_bargmann_adimi(x: int, y: int, z: int, P: np.ndarray, Asim: np.ndarray
                                ) -> Dict[str, float]:
    p_dongu = P[x, y] * P[y, z] * max(1e-12, P[z, x])
    faz_toplam = np.pi * (Asim[x, y] + Asim[y, z] - Asim[z, x])

    r_bargmann = float(np.sqrt(max(1e-12, p_dongu)))
    phi_bargmann = float(np.angle(np.exp(1j * faz_toplam)))

    ortusme = float(np.clip(np.sqrt(P[x, y] * P[y, z]), 0.0, 1.0))
    tasima_zamani = float(np.arccos(ortusme))

    casimir_degismezi = float(np.cos(tasima_zamani) ** 2)

    return {
        "bargmann_r": r_bargmann,
        "bargmann_phi": phi_bargmann,
        "tasima_zamani": tasima_zamani,
        "casimir_degismezi": casimir_degismezi,
        "tenakuz_mu": bool(abs(abs(phi_bargmann) - np.pi) < 0.5),
        "kisirdongu_mu": bool(abs(phi_bargmann) < 0.5 and r_bargmann > 1e-4)
    }


class Turetilen1Kategori:
    __slots__ = ("nesneler", "ok_siniflari", "bileske_tablosu", "birim_oklar")

    def __init__(self, nesneler: List[int], ok_siniflari: Dict[Tuple[int, int], int],
                 bileske_tablosu: Dict[Tuple[int, int], int],
                 birim_oklar: Dict[int, int]) -> None:
        self.nesneler = nesneler
        self.ok_siniflari = ok_siniflari
        self.bileske_tablosu = bileske_tablosu
        self.birim_oklar = birim_oklar


class TuretilenAyrıkKume:
    __slots__ = ("bilesenler", "eleman_bilesen_haritasi")

    def __init__(self, bilesenler: List[Set[int]]) -> None:
        self.bilesenler = bilesenler
        self.eleman_bilesen_haritasi = {
            el: idx for idx, kume in enumerate(bilesenler) for el in kume
        }


class TuretilenDilimAlemi:
    __slots__ = ("baglam_hedefi", "alemdeki_nesneler", "alem_ici_morfizmler")

    def __init__(self, baglam_hedefi: int, alemdeki_nesneler: List[int],
                 alem_ici_morfizmler: List[Tuple[int, int]]) -> None:
        self.baglam_hedefi = baglam_hedefi
        self.alemdeki_nesneler = alemdeki_nesneler
        self.alem_ici_morfizmler = alem_ici_morfizmler


def turet_dilim_alemi(baglam_hedefi: int, nesneler: List[int],
                      P: np.ndarray) -> TuretilenDilimAlemi:
    hedefe_baglananlar = [x for x in nesneler
                          if P[x, baglam_hedefi] > 0.01 or x == baglam_hedefi]

    alem_morfizmleri = []
    for x in hedefe_baglananlar:
        for y in hedefe_baglananlar:
            if x != y and P[x, y] > 0.05:
                alem_morfizmleri.append((x, y))

    return TuretilenDilimAlemi(baglam_hedefi, hedefe_baglananlar, alem_morfizmleri)


def turet_1_kategori_bolumlemeli(w_baglam: Tuple[int, ...], P: np.ndarray,
                                 silsile_adimlari: List[Tuple[Terim, Terim]]
                                 ) -> Turetilen1Kategori:
    nesneler_kumesi = set(w_baglam)
    for agac, ok_terimi in silsile_adimlari:
        if isinstance(ok_terimi, YonluOk):
            for uc in (ok_terimi.kaynak, ok_terimi.hedef):
                if isinstance(uc, Belirtec):
                    nesneler_kumesi.add(uc.id_no)

    nesneler = sorted(nesneler_kumesi)
    ok_siniflari: Dict[Tuple[int, int], int] = {}
    birim_oklar: Dict[int, int] = {}
    ok_sayaci = 0

    for x in nesneler:
        ok_siniflari[(x, x)] = ok_sayaci
        birim_oklar[x] = ok_sayaci
        ok_sayaci += 1

    for i in nesneler:
        for j in nesneler:
            if i != j and P[i, j] > 0.05:
                ok_siniflari[(i, j)] = ok_sayaci
                ok_sayaci += 1

    ebeveyn_ok = {oid: oid for oid in ok_siniflari.values()}

    def ok_koku(o: int) -> int:
        while ebeveyn_ok[o] != o:
            ebeveyn_ok[o] = ebeveyn_ok[ebeveyn_ok[o]]
            o = ebeveyn_ok[o]
        return o

    for agac, ok_terimi in silsile_adimlari:
        if isinstance(agac, OperadAgac) and isinstance(ok_terimi, YonluOk):
            try:
                x_id = agac.oncutler[-1].id_no if hasattr(agac.oncutler[-1], "id_no") else None
                y_id = agac.hedef.id_no if hasattr(agac.hedef, "id_no") else None
                z_id = ok_terimi.hedef.id_no if hasattr(ok_terimi.hedef, "id_no") else None
                if x_id in nesneler and y_id in nesneler and z_id in nesneler:
                    ok_xy = ok_siniflari.get((x_id, y_id))
                    ok_yz = ok_siniflari.get((y_id, z_id))
                    ok_xz = ok_siniflari.get((x_id, z_id))
                    if ok_xz is not None and ok_xy is not None and ok_yz is not None:
                        ebeveyn_ok[ok_koku(ok_xz)] = ok_koku(ok_xy)
            except AttributeError:
                pass

    for cift, oid in list(ok_siniflari.items()):
        ok_siniflari[cift] = ok_koku(oid)

    bileske_tablosu: Dict[Tuple[int, int], int] = {}
    for (x, y), ok1 in ok_siniflari.items():
        for (y2, z), ok2 in ok_siniflari.items():
            if y == y2 and (x, z) in ok_siniflari:
                bileske_tablosu[(ok1, ok2)] = ok_siniflari[(x, z)]

    return Turetilen1Kategori(nesneler, ok_siniflari, bileske_tablosu, birim_oklar)


def turet_ayrik_kume_funktoriyel(kat: Turetilen1Kategori) -> TuretilenAyrıkKume:
    nesneler = kat.nesneler
    ebeveyn = {x: x for x in nesneler}

    def bul(i: int) -> int:
        while ebeveyn[i] != i:
            ebeveyn[i] = ebeveyn[ebeveyn[i]]
            i = ebeveyn[i]
        return i

    def birlestir(i: int, j: int) -> None:
        kok_i, kok_j = bul(i), bul(j)
        if kok_i != kok_j:
            ebeveyn[kok_i] = kok_j

    for (kaynak, hedef) in kat.ok_siniflari.keys():
        if kaynak != hedef:
            birlestir(kaynak, hedef)

    gruplar: Dict[int, Set[int]] = {}
    for x in nesneler:
        kok = bul(x)
        gruplar.setdefault(kok, set()).add(x)

    return TuretilenAyrıkKume(list(gruplar.values()))


def kategori_sahidi_sentezle(kat: Turetilen1Kategori) -> Terim:
    Ob_terimi = Dogal()
    Hom_terimi = Lam("a", Lam("b", Dogal()))
    hom_kume_ispat = Lam("a", Lam("b", Lam("x", Lam("y", refl(D("x"))))))
    birim_terimi = Lam("x", dogal_sayi(0))
    bileske_terimi = Lam("a", Lam("b", Lam("c", Lam("f", Lam("g", D("g"))))))
    sol_birim_ispat = Lam("a", Lam("b", Lam("f", refl(D("f")))))
    sag_birim_ispat = Lam("a", Lam("b", Lam("f", refl(D("f")))))
    birlesme_ispat = Lam("a", Lam("b", Lam("c", Lam("d", Lam("f", Lam("g", Lam("h", refl(D("h")))))))))

    return Cift(Ob_terimi,
           Cift(Hom_terimi,
           Cift(hom_kume_ispat,
           Cift(birim_terimi,
           Cift(bileske_terimi,
           Cift(sol_birim_ispat,
           Cift(sag_birim_ispat, birlesme_ispat)))))))


def alem_baglami_ac(alem: TuretilenDilimAlemi, ana_baglam: Optional[Baglam] = None) -> Baglam:
    g = ana_baglam or Baglam()
    alem_hedef_ad = "Hedef_%d" % alem.baglam_hedefi
    g = g.genislet(alem_hedef_ad, g.d(Dogal()))

    for obj_id in alem.alemdeki_nesneler:
        obj_ad = "AlemNesne_%d" % obj_id
        g = g.genislet(obj_ad, g.d(Dogal()))
        ok_ad = "Morfizm_%d_%d" % (obj_id, alem.baglam_hedefi)
        g = g.genislet(ok_ad, g.d(yonlu_hom(Dogal(), D(obj_ad), D(alem_hedef_ad))))

    return g


def topos_karakteristik_haritasi_chi(alt_kume_kenarlar: Set[Tuple[int, int]],
                                     P: np.ndarray, Asim: np.ndarray,
                                     Kan_rezidusu: np.ndarray,
                                     omega_cebiri: str) -> Dict[Tuple[int, int], float]:
    n = P.shape[0]
    chi_haritasi: Dict[Tuple[int, int], float] = {}

    for i in range(n):
        for j in range(n):
            if (i, j) not in alt_kume_kenarlar:
                chi_haritasi[(i, j)] = 0.0
                continue

            tikanma = float(Kan_rezidusu[i, j])
            asimetri = float(Asim[i, j])

            if omega_cebiri == "boole":
                chi_haritasi[(i, j)] = 1.0 if tikanma < 0.05 else 0.0
            elif "heyting" in omega_cebiri:
                chi_haritasi[(i, j)] = float(np.clip(1.0 - tikanma, 0.0, 1.0))
            else:
                chi_haritasi[(i, j)] = float(np.clip((1.0 - tikanma) * asimetri, 0.0, 1.0))

    return chi_haritasi


def ayrik_sol_kan_uzantisi(F_alt_fonksiyon: Dict[int, float],
                           alem: TuretilenDilimAlemi,
                           kat: Turetilen1Kategori) -> Dict[int, float]:
    Lan_F: Dict[int, float] = {}

    for y in kat.nesneler:
        aday_degerler = []
        for x in alem.alemdeki_nesneler:
            f_x = F_alt_fonksiyon.get(x, 0.0)
            ok_var = (x, y) in kat.ok_siniflari
            if ok_var:
                aday_degerler.append(f_x * 1.0)
            elif x == y:
                aday_degerler.append(f_x)

        Lan_F[y] = float(max(aday_degerler)) if aday_degerler else 0.0

    return Lan_F


def rezk_tamlastirmasi(kat: Turetilen1Kategori) -> Turetilen1Kategori:
    nesneler = list(kat.nesneler)
    ebeveyn = {x: x for x in nesneler}

    def bul(i: int) -> int:
        while ebeveyn[i] != i:
            ebeveyn[i] = ebeveyn[ebeveyn[i]]
            i = ebeveyn[i]
        return i

    def birlestir(i: int, j: int) -> None:
        kok_i, kok_j = bul(i), bul(j)
        if kok_i != kok_j:
            ebeveyn[kok_i] = kok_j

    for (x, y), ok_xy in kat.ok_siniflari.items():
        if x != y and (y, x) in kat.ok_siniflari:
            ok_yx = kat.ok_siniflari[(y, x)]
            bileske_xy_yx = kat.bileske_tablosu.get((ok_xy, ok_yx))
            bileske_yx_xy = kat.bileske_tablosu.get((ok_yx, ok_xy))

            if (bileske_xy_yx == kat.birim_oklar.get(x) and
                    bileske_yx_xy == kat.birim_oklar.get(y)):
                birlestir(x, y)

    yeni_nesneler_haritasi = {x: bul(x) for x in nesneler}
    univalent_nesneler = sorted(set(yeni_nesneler_haritasi.values()))

    yeni_ok_siniflari: Dict[Tuple[int, int], int] = {}
    for (x, y), oid in kat.ok_siniflari.items():
        rx, ry = yeni_nesneler_haritasi[x], yeni_nesneler_haritasi[y]
        if (rx, ry) not in yeni_ok_siniflari:
            yeni_ok_siniflari[(rx, ry)] = oid

    yeni_birimler = {rx: kat.birim_oklar[rx] for rx in univalent_nesneler if rx in kat.birim_oklar}

    return Turetilen1Kategori(univalent_nesneler, yeni_ok_siniflari,
                              kat.bileske_tablosu, yeni_birimler)


def cech_kohomoloji_engeli_olc(orijinal_baglam: Tuple[int, ...],
                               P: np.ndarray,
                               pencere_boyu: int = 2) -> Dict[str, Any]:
    k = len(orijinal_baglam)
    if k < 3:
        return {"cech_engeli_H1": 0.0, "komutatiftir": True}

    ortuler = [orijinal_baglam[i:i + pencere_boyu] for i in range(k - pencere_boyu + 1)]
    m = len(ortuler)

    bagdasim_kusurlari = []
    for i in range(m - 2):
        u, v, w = ortuler[i][-1], ortuler[i + 1][-1], ortuler[i + 2][-1]
        g_uv = P[u, v]
        g_vw = P[v, w]
        g_uw = P[u, w]

        kusur = abs((g_uv * g_vw) - g_uw)
        bagdasim_kusurlari.append(kusur)

    h1_engeli = float(np.mean(bagdasim_kusurlari)) if bagdasim_kusurlari else 0.0
    return {"cech_engeli_H1": h1_engeli, "komutatiftir": bool(h1_engeli < 0.02)}


def t4_nedensel_cephe_olcumu(psi_intac: np.ndarray, son_token: int,
                             theta_cartan: float, veri_lifi: int = 8,
                             basamak_sayisi: int = 6) -> Dict[str, Any]:
    d = int(veri_lifi)
    cephe_genlikleri = np.zeros(d, dtype=complex)

    for c in range(d):
        faz = theta_cartan * float(c + 1) / float(d)
        psi_idx = c % len(psi_intac)
        cephe_genlikleri[c] = psi_intac[psi_idx] * np.exp(1j * faz)

    born_olasiliklari = np.abs(cephe_genlikleri) ** 2
    born_olasiliklari /= (np.sum(born_olasiliklari) + 1e-12)

    olculen_basamak = int(np.argmax(born_olasiliklari))
    olcum_guveni = float(born_olasiliklari[olculen_basamak])

    return {"nedensel_cephe_basamak": olculen_basamak, "olcum_guveni": olcum_guveni,
            "born_dagilimi": born_olasiliklari}


ZIRH_BOYUTU = 1048576


def qudit_zirhina_gom(kuantum_durum_vektoru: np.ndarray,
                      aktif_dilimler: Dict[str, Tuple[int, int]]
                      ) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
    aktif_boyut = len(kuantum_durum_vektoru)
    if aktif_boyut > ZIRH_BOYUTU:
        raise DenetimHatasi("Aktif pencere zırh boyutunu (1.048.576) aşamaz")

    psi_zirh = np.zeros(ZIRH_BOYUTU, dtype=complex)
    psi_zirh[:aktif_boyut] = kuantum_durum_vektoru

    seyirci_maskesi = np.zeros(ZIRH_BOYUTU, dtype=float)
    seyirci_maskesi[:aktif_boyut] = 1.0

    zirh_metrigi = {
        "zirh_kapasitesi": ZIRH_BOYUTU,
        "aktif_pencere_boyu": aktif_boyut,
        "seyirci_qudit_sayisi": ZIRH_BOYUTU - aktif_boyut,
        "seyirci_oran": float((ZIRH_BOYUTU - aktif_boyut) / ZIRH_BOYUTU)
    }

    return psi_zirh, seyirci_maskesi, zirh_metrigi


class FockKipKuantizasyonu:
    __slots__ = ("kesme_boyutu", "a", "a_dag", "sayi_operatoru")

    def __init__(self, kesme_boyutu: int = 8) -> None:
        self.kesme_boyutu = int(kesme_boyutu)
        N = self.kesme_boyutu

        self.a = np.zeros((N, N), dtype=complex)
        for n_idx in range(1, N):
            self.a[n_idx - 1, n_idx] = np.sqrt(float(n_idx))

        self.a_dag = self.a.conj().T
        self.sayi_operatoru = self.a_dag @ self.a

    def s0_vakum_durumu(self) -> np.ndarray:
        psi_0 = np.zeros(self.kesme_boyutu, dtype=complex)
        psi_0[0] = 1.0
        return psi_0

    def s2_mesele_uyar(self, psi_fock: np.ndarray, sual_enerjisi: float) -> np.ndarray:
        psi_uyarilmis = (self.a_dag @ psi_fock) * np.sqrt(max(1e-6, sual_enerjisi))
        norm = np.linalg.norm(psi_uyarilmis)
        return psi_uyarilmis / (norm + 1e-12) if norm > 1e-12 else psi_fock

    def s5_hukum_sonumle(self, psi_fock: np.ndarray) -> Tuple[np.ndarray, float]:
        psi_sonum = self.a @ psi_fock
        kalan_enerji = float(np.real(psi_fock.conj().T @ (self.sayi_operatoru @ psi_fock)))
        norm = np.linalg.norm(psi_sonum)
        psi_sonum = psi_sonum / (norm + 1e-12) if norm > 1e-12 else self.s0_vakum_durumu()
        return psi_sonum, kalan_enerji


def iki_cins_geometri_cikar(veri: Union[Sequence[int], np.ndarray], n: int,
                            izgara_sekli: Optional[Tuple[int, int]] = None
                            ) -> Tuple[np.ndarray, np.ndarray]:
    m = int(n)
    N_gecis = np.zeros((m, m), dtype=float)

    if izgara_sekli is not None and isinstance(veri, np.ndarray) and veri.ndim == 2:
        satir, sutun = veri.shape
        for r in range(satir):
            for c in range(sutun):
                u = int(veri[r, c]) % m
                if c + 1 < sutun:
                    v_sag = int(veri[r, c + 1]) % m
                    N_gecis[u, v_sag] += 1.0
                    N_gecis[v_sag, u] += 0.5
                if r + 1 < satir:
                    v_alt = int(veri[r + 1, c]) % m
                    N_gecis[u, v_alt] += 1.0
                    N_gecis[v_alt, u] += 0.5
    else:
        w_arr = np.asarray(veri, dtype=np.int64).reshape(-1) % m
        if len(w_arr) >= 2:
            np.add.at(N_gecis, (w_arr[:-1], w_arr[1:]), 1.0)

    cikis_toplami = N_gecis.sum(axis=1, keepdims=True) + 1e-12
    P = N_gecis / cikis_toplami
    pay = np.abs(P - P.T)
    payda = P + P.T + 1e-12
    Asim = pay / payda

    return P, Asim


class DahiliHomNesnesi:
    __slots__ = ("kaynak_nesne", "hedef_nesne", "dahili_id", "degerlendirme_oku")

    def __init__(self, kaynak: int, hedef: int, dahili_id: int) -> None:
        self.kaynak_nesne = kaynak
        self.hedef_nesne = hedef
        self.dahili_id = dahili_id
        self.degerlendirme_oku = (dahili_id, kaynak, hedef)


def ccc_dahili_hom_uzayi_turet(kat: Turetilen1Kategori) -> Dict[Tuple[int, int], DahiliHomNesnesi]:
    dahili_homlar: Dict[Tuple[int, int], DahiliHomNesnesi] = {}
    yeni_id_tabani = max(kat.nesneler, default=0) + 1000

    for a in kat.nesneler:
        for b in kat.nesneler:
            if (a, b) in kat.ok_siniflari or a == b:
                dahili_id = yeni_id_tabani + len(dahili_homlar)
                dahili_homlar[(a, b)] = DahiliHomNesnesi(kaynak=a, hedef=b, dahili_id=dahili_id)

    return dahili_homlar


class QuditParametreYazmaci:
    __slots__ = ("qudit_sayisi", "taban", "quditler")

    def __init__(self, qudit_sayisi: int = 4, taban: int = 8) -> None:
        self.qudit_sayisi = int(qudit_sayisi)
        self.taban = int(taban)
        self.quditler = np.ones((self.qudit_sayisi, self.taban), dtype=complex)
        for q in range(self.qudit_sayisi):
            fazlar = np.linspace(0.0, np.pi, self.taban)
            self.quditler[q] = np.exp(1j * fazlar) / np.sqrt(self.taban)

    def parametre_acilari_oku(self) -> np.ndarray:
        acilar = []
        for q in range(self.qudit_sayisi):
            ortalama_vektor = np.sum(self.quditler[q])
            aci = float(np.angle(ortalama_vektor))
            acilar.append(abs(aci) if abs(aci) > 1e-4 else 0.1)
        return np.array(acilar, dtype=float)

    def kapı_ile_guncelle(self, gradyan_yonu: np.ndarray, adim_boyu: float) -> None:
        for q in range(min(self.qudit_sayisi, len(gradyan_yonu))):
            faz_kaymasi = np.exp(1j * adim_boyu * gradyan_yonu[q])
            self.quditler[q] *= faz_kaymasi
            self.quditler[q] /= (np.linalg.norm(self.quditler[q]) + 1e-12)


def cartan_kok_ve_agirlik_hesapla(a: int, b: int, n: int) -> float:
    rank = max(1, n - 1)
    kok_vektoru = np.zeros(rank, dtype=float)
    if a < rank:
        kok_vektoru[a] += 1.0
    if b < rank:
        kok_vektoru[b] -= 1.0

    agirlik_vektoru = np.array([np.cos(2.0 * np.pi * (k + 1) * (b + 1) / (rank + 1))
                                for k in range(rank)], dtype=float)

    return float(np.dot(kok_vektoru, agirlik_vektoru))


def cok_basamakli_qudit_tensor_durumu(token_id: int, veri_lifi: int = 8,
                                      basamak_sayisi: int = 3) -> np.ndarray:
    d = int(veri_lifi)
    k = int(basamak_sayisi)
    basamaklar = taban_acilimi(token_id, veri_lifi=d, basamak_sayisi=k)

    durum = np.zeros(d, dtype=complex)
    durum[basamaklar[0]] = 1.0

    for b in basamaklar[1:]:
        b_durum = np.zeros(d, dtype=complex)
        b_durum[b] = 1.0
        durum = np.kron(durum, b_durum)

    return durum


class MonoidalKategori:
    __slots__ = ("kategori", "tensor_nesneleri", "tensor_oklari")

    def __init__(self, kategori: Turetilen1Kategori) -> None:
        self.kategori = kategori
        self.tensor_nesneleri: Dict[Tuple[int, int], int] = {}
        self.tensor_oklari: Dict[Tuple[int, int], Tuple[int, int]] = {}
        self._monoidal_yapi_kur()

    def _monoidal_yapi_kur(self) -> None:
        nesneler = self.kategori.nesneler
        n_id = max(nesneler, default=0) + 1

        for a in nesneler:
            for b in nesneler:
                self.tensor_nesneleri[(a, b)] = a * n_id + b

        oklar = self.kategori.ok_siniflari
        for (x, y), ok1 in oklar.items():
            for (u, v), ok2 in oklar.items():
                xu = self.tensor_nesneleri.get((x, u), 0)
                yv = self.tensor_nesneleri.get((y, v), 0)
                self.tensor_oklari[(ok1, ok2)] = (xu, yv)


_ZINCIR_GECIS_ESIGI = 0.01


def silsile_adimlarini_bagla(muhakemeler: List[Dict[str, Any]],
                             orijinal_baglam: Tuple[int, ...],
                             nihai_hedef: int,
                             P: np.ndarray,
                             X_tip: Terim,
                             norm_korollalar: Optional[Dict[Tuple[Tuple[int, ...], int], float]] = None,
                             gecis_esigi: float = _ZINCIR_GECIS_ESIGI) -> List[Tuple[Terim, Terim]]:
    if not muhakemeler:
        return []

    norm_korollalar = norm_korollalar or {}
    adimlar: List[Tuple[Terim, Terim]] = []
    mevcut_oncutler = [dogal_sayi(t) for t in orijinal_baglam]
    k = len(muhakemeler)
    baglam_yol = orijinal_baglam

    for idx, adim in enumerate(muhakemeler):
        y_ara = adim.get("ara_durak")

        if y_ara is None:
            dogrudan_hedef = adim.get("hedef")
            if dogrudan_hedef is None:
                continue
            kaynak_id = int(baglam_yol[-1])
            hedef_id = int(dogrudan_hedef)
            destek = max(float(P[kaynak_id, hedef_id]),
                        float(norm_korollalar.get((baglam_yol, hedef_id), 0.0)))
            if destek < gecis_esigi and kaynak_id != hedef_id:
                return []
            agac = OperadAgac(X_tip, mevcut_oncutler, dogal_sayi(kaynak_id),
                              "agac_dogrudan_%d" % idx)
            ok = YonluOk(X_tip, dogal_sayi(kaynak_id), dogal_sayi(hedef_id),
                        "dogrudan_oku_%d" % idx)
            adimlar.append((agac, ok))
            mevcut_oncutler = tuple(list(mevcut_oncutler[1:]) + [dogal_sayi(hedef_id)])
            continue

        y_ara_id = int(y_ara)
        baglam_yol_sonraki = tuple(list(baglam_yol[1:]) + [y_ara_id])
        if idx == k - 1:
            hedef_id = int(nihai_hedef)
        else:
            sonraki_ara = muhakemeler[idx + 1].get("ara_durak")
            hedef_id = int(sonraki_ara) if sonraki_ara is not None else int(nihai_hedef)

        destek = max(float(P[y_ara_id, hedef_id]),
                    float(norm_korollalar.get((baglam_yol_sonraki, hedef_id), 0.0)))
        if destek < gecis_esigi and y_ara_id != hedef_id:
            return []

        agac = OperadAgac(X_tip, mevcut_oncutler, dogal_sayi(y_ara_id), "agac_hop_%d" % idx)
        ok = YonluOk(X_tip, dogal_sayi(y_ara_id), dogal_sayi(hedef_id), "gecis_oku_%d" % idx)
        adimlar.append((agac, ok))

        mevcut_oncutler = tuple(list(mevcut_oncutler[1:]) + [dogal_sayi(hedef_id)])
        baglam_yol = baglam_yol_sonraki

    return adimlar


def heyting_operatorleri(a: float, b: float, omega_cebiri: str) -> Dict[str, float]:
    val_a = float(np.clip(a, 0.0, 1.0))
    val_b = float(np.clip(b, 0.0, 1.0))

    kesisim = min(val_a, val_b)
    birlesim = max(val_a, val_b)

    if omega_cebiri == "boole":
        impilasyon = 1.0 if (val_a <= val_b) else 0.0
        olumsuzlama = 1.0 - val_a
    else:
        impilasyon = 1.0 if val_a <= val_b else val_b
        olumsuzlama = 1.0 if val_a == 0.0 else 0.0

    return {"kesisim_ve": kesisim, "birlesim_veya": birlesim,
            "impilasyon_gerektirme": impilasyon, "olumsuzlama_degil": olumsuzlama}


def elemanlar_kategorisi_turet(kat: Turetilen1Kategori,
                               tip_fonksiyonu: Dict[int, float]) -> Turetilen1Kategori:
    yeni_nesneler = [x for x in kat.nesneler if tip_fonksiyonu.get(x, 0.0) > 0.05]
    if not yeni_nesneler:
        yeni_nesneler = list(kat.nesneler)

    yeni_ok_siniflari: Dict[Tuple[int, int], int] = {}
    yeni_birimler: Dict[int, int] = {}
    ok_sayaci = 0

    for x in yeni_nesneler:
        yeni_ok_siniflari[(x, x)] = ok_sayaci
        yeni_birimler[x] = ok_sayaci
        ok_sayaci += 1

    for (x, y), oid in kat.ok_siniflari.items():
        if x in yeni_nesneler and y in yeni_nesneler and x != y:
            yeni_ok_siniflari[(x, y)] = ok_sayaci
            ok_sayaci += 1

    yeni_bileske: Dict[Tuple[int, int], int] = {}
    for (x, y), ok1 in yeni_ok_siniflari.items():
        for (y2, z), ok2 in yeni_ok_siniflari.items():
            if y == y2 and (x, z) in yeni_ok_siniflari:
                yeni_bileske[(ok1, ok2)] = yeni_ok_siniflari[(x, z)]

    return Turetilen1Kategori(yeni_nesneler, yeni_ok_siniflari, yeni_bileske, yeni_birimler)


def uc_boyutlu_boynuz_doldur(x: int, y: int, z: int, w: int, P: np.ndarray) -> Dict[str, float]:
    p_xy = float(P[x, y])
    p_yz = float(P[y, z])
    p_zw = float(P[z, w])
    p_xw = float(P[x, w])

    yol_1 = (p_xy * p_yz) * p_zw
    yol_2 = p_xy * (p_yz * p_zw)

    asosiyatiflik_kusuru = float(abs(yol_1 - yol_2))
    kapanis_hatasi = float(abs(p_xw - (p_xy * p_yz * p_zw)))
    toplam_3d_engel = asosiyatiflik_kusuru + kapanis_hatasi

    return {"asosiyatiflik_kusuru": asosiyatiflik_kusuru,
            "dortyuzlu_3d_engel": toplam_3d_engel,
            "uc_hucre_doldu_mu": bool(toplam_3d_engel < 0.05)}


class TemelDegisimFunktoru:
    __slots__ = ("kaynak_hedef_oku", "f_gecis_gucu")

    def __init__(self, kaynak_hedef_oku: Tuple[int, int], f_gecis_gucu: float) -> None:
        self.kaynak_hedef_oku = kaynak_hedef_oku
        self.f_gecis_gucu = float(f_gecis_gucu)

    def sigma_ileri_it(self, alem_A: TuretilenDilimAlemi, alem_B: TuretilenDilimAlemi) -> List[int]:
        itilen_nesneler = []
        for x in alem_A.alemdeki_nesneler:
            if x not in alem_B.alemdeki_nesneler:
                itilen_nesneler.append(x)
        return itilen_nesneler

    def pullback_geri_cek(self, alem_B: TuretilenDilimAlemi, P: np.ndarray) -> List[Tuple[int, float]]:
        A, B = self.kaynak_hedef_oku
        lif_degisimi = []
        for y in alem_B.alemdeki_nesneler:
            lif_agirligi = float(P[y, B] * self.f_gecis_gucu)
            if lif_agirligi > 1e-4:
                lif_degisimi.append((y, lif_agirligi))
        return lif_degisimi


class GrothendieckElek:
    __slots__ = ("hedef_nesne", "elek_oklari", "kapsama_esigi")

    def __init__(self, hedef_nesne: int, elek_oklari: Set[Tuple[int, int]], kapsama_esigi: float = 0.6) -> None:
        self.hedef_nesne = int(hedef_nesne)
        self.elek_oklari = set(elek_oklari)
        self.kapsama_esigi = float(kapsama_esigi)

    def elek_kapanisi_dogrula(self, kat: Turetilen1Kategori) -> bool:
        C = self.hedef_nesne
        for (x, c_hedef) in list(self.elek_oklari):
            if c_hedef != C:
                continue
            for (w, x_giris) in kat.ok_siniflari:
                if x_giris == x and (w, C) not in self.elek_oklari:
                    self.elek_oklari.add((w, C))
        return True

    def ortu_mu(self, P: np.ndarray) -> bool:
        C = self.hedef_nesne
        toplam_ortu_kutlesi = sum(P[x, c] for (x, c) in self.elek_oklari if c == C)
        return bool(toplam_ortu_kutlesi >= self.kapsama_esigi)


def kismi_iz_ve_dolaniklik_entropisi(rho_AB: np.ndarray, d_A: int, d_B: int) -> Tuple[float, np.ndarray]:
    toplam_boyut = d_A * d_B
    if rho_AB.shape[0] < toplam_boyut:
        raise DenetimHatasi("Yoğunluk matrisi alt-sistem boyutlarını karşılamıyor")

    rho_A = np.zeros((d_A, d_A), dtype=complex)
    for j in range(d_B):
        for i1 in range(d_A):
            for i2 in range(d_A):
                idx1 = i1 * d_B + j
                idx2 = i2 * d_B + j
                rho_A[i1, i2] += rho_AB[idx1, idx2]

    iz_A = np.trace(rho_A)
    if abs(iz_A) > 1e-12:
        rho_A /= iz_A

    ozdegerler = np.real(np.linalg.eigvalsh(rho_A))
    ozdegerler = ozdegerler[ozdegerler > 1e-12]
    dolaniklik_entropisi = float(-np.sum(ozdegerler * np.log2(ozdegerler))) if len(ozdegerler) else 0.0

    return dolaniklik_entropisi, rho_A


def opetopik_agac_asila(ana_agac: OperadAgac, asilanan_agac: OperadAgac,
                        yaprak_indeksi: int, X_tip: Terim) -> OperadAgac:
    oncutler_1 = list(ana_agac.oncutler)
    if not (0 <= yaprak_indeksi < len(oncutler_1)):
        raise DenetimHatasi("Geçersiz yaprak indeksi")

    yeni_oncutler = (
        oncutler_1[:yaprak_indeksi] +
        list(asilanan_agac.oncutler) +
        oncutler_1[yaprak_indeksi + 1:]
    )

    yeni_etiket = "%s_asili_%s" % (ana_agac.etiket, asilanan_agac.etiket)
    return OperadAgac(cizgi=X_tip, oncutler=yeni_oncutler, hedef=ana_agac.hedef, etiket=yeni_etiket)


class LawvereCebirselTeorisi:
    __slots__ = ("teori_adi", "islemler", "denklemler")

    def __init__(self, teori_adi: str, islemler: Dict[str, int],
                 denklemler: List[Tuple[str, str]]) -> None:
        self.teori_adi = teori_adi
        self.islemler = islemler
        self.denklemler = denklemler

    def topos_tipine_cevir(self) -> Terim:
        X = D("X")
        baglar: List[Tuple[str, Terim]] = [("X", U), ("kume_sarti", mertebe(X, 0))]

        for op_ad, arite in self.islemler.items():
            op_tip = X
            for _ in range(arite):
                op_tip = ok(X, op_tip)
            baglar.append((op_ad, op_tip))

        birim_adi = next(iter(self.islemler.keys()), "X")
        son_denklem = yol(X, D(birim_adi), D("X"))
        return sigma_hepsi(baglar, son_denklem)

    def model_dogrula(self, tasiyici_kume: List[int], islem_tablolari: Dict[str, Any]) -> bool:
        return bool(len(tasiyici_kume) > 0 and len(islem_tablolari) >= len(self.islemler))


def topos_esitleyici_equalizer(ok1_id: int, ok2_id: int, kat: Turetilen1Kategori) -> List[int]:
    esitleyici_nesneler = []
    for x in kat.nesneler:
        val1 = kat.bileske_tablosu.get((kat.birim_oklar.get(x, 0), ok1_id))
        val2 = kat.bileske_tablosu.get((kat.birim_oklar.get(x, 0), ok2_id))
        if val1 is not None and val1 == val2:
            esitleyici_nesneler.append(x)
    return esitleyici_nesneler


def topos_es_esitleyici_coequalizer(ok1_id: int, ok2_id: int,
                                    kat: Turetilen1Kategori) -> Dict[int, int]:
    ebeveyn = {x: x for x in kat.nesneler}

    def bul(i: int) -> int:
        while ebeveyn[i] != i:
            ebeveyn[i] = ebeveyn[ebeveyn[i]]
            i = ebeveyn[i]
        return i

    for (x, y), oid1 in kat.ok_siniflari.items():
        if oid1 == ok1_id:
            for (x2, y2), oid2 in kat.ok_siniflari.items():
                if oid2 == ok2_id and x == x2:
                    k1, k2 = bul(y), bul(y2)
                    if k1 != k2:
                        ebeveyn[k1] = k2

    return {x: bul(x) for x in kat.nesneler}


def hata_gedik_karanlik_cevrim_borcu(P: np.ndarray, Asim: np.ndarray, Kan_rez: np.ndarray,
                                     dongu_noktalari: Sequence[int]) -> float:
    k = len(dongu_noktalari)
    if k < 2:
        return 0.0

    borc_toplami = 0.0
    for i in range(k):
        u = dongu_noktalari[i]
        v = dongu_noktalari[(i + 1) % k]
        adim_borcu = float(Asim[u, v] * (1.0 - P[u, v]) * Kan_rez[u, v])
        borc_toplami += adim_borcu

    return float(borc_toplami / float(k))


class IkiCezveliHafiza:
    __slots__ = ("suretler_cezvesi", "manalar_cezvesi", "indeks_baglari")

    def __init__(self) -> None:
        self.suretler_cezvesi: Dict[int, np.ndarray] = {}
        self.manalar_cezvesi: Dict[int, np.ndarray] = {}
        self.indeks_baglari: Dict[int, Set[int]] = {}

    def kaydet(self, nesne_id: int, suret: np.ndarray, mana: np.ndarray) -> None:
        self.suretler_cezvesi[nesne_id] = suret / (np.linalg.norm(suret) + 1e-12)
        self.manalar_cezvesi[nesne_id] = np.asarray(mana, dtype=float)

    def cift_yonlu_bagla(self, id1: int, id2: int) -> None:
        self.indeks_baglari.setdefault(id1, set()).add(id2)
        self.indeks_baglari.setdefault(id2, set()).add(id1)


class MutezekkireKuvveti:
    __slots__ = ("hafiza",)

    def __init__(self, hafiza: IkiCezveliHafiza) -> None:
        self.hafiza = hafiza

    def cagir_ve_hatirla(self, aranan_suret: np.ndarray,
                         hedef_mana: Optional[np.ndarray] = None,
                         rezonans_esigi: float = 0.3) -> Optional[int]:
        if not self.hafiza.suretler_cezvesi:
            return None

        q_s = aranan_suret / (np.linalg.norm(aranan_suret) + 1e-12)
        en_iyi_skor = -1e9
        bulunan_id: Optional[int] = None

        for n_id, s_vektor in self.hafiza.suretler_cezvesi.items():
            suret_skoru = float(np.dot(q_s, s_vektor))

            mana_skoru = 0.0
            if hedef_mana is not None and n_id in self.hafiza.manalar_cezvesi:
                m_vektor = self.hafiza.manalar_cezvesi[n_id]
                mana_mesafesi = float(np.linalg.norm(hedef_mana - m_vektor))
                mana_skoru = float(np.exp(-mana_mesafesi))

            toplam_rezonans = suret_skoru + 0.5 * mana_skoru
            if toplam_rezonans > en_iyi_skor:
                en_iyi_skor = toplam_rezonans
                bulunan_id = n_id

        return bulunan_id if en_iyi_skor >= rezonans_esigi else None


class VahimeIslemcisi:
    __slots__ = ("tehdit_esigi",)

    def __init__(self, tehdit_esigi: float = 0.35) -> None:
        self.tehdit_esigi = float(tehdit_esigi)

    def mana_suz(self, son_token: int, hedef_aday: int,
                 P: np.ndarray, Kan_rez: np.ndarray, Asim: np.ndarray) -> Dict[str, Any]:
        gecis_gucu = float(P[son_token, hedef_aday])
        tikanma_tehdidi = float(Kan_rez[son_token, hedef_aday])
        tek_yonlu_baski = float(Asim[son_token, hedef_aday])

        fayda = gecis_gucu * (1.0 - tikanma_tehdidi)
        tehdit = tikanma_tehdidi * tek_yonlu_baski
        aciliyet = float(np.clip(tehdit - fayda, -1.0, 1.0))

        acil_refleks_gerekli = bool(tehdit >= self.tehdit_esigi)

        mana_vektoru = np.array([fayda, tehdit, aciliyet, gecis_gucu], dtype=float)

        return {"mana_vektoru": mana_vektoru, "fayda": fayda, "tehdit": tehdit,
                "acil_refleks": acil_refleks_gerekli,
                "hukum": "TEHDİT_ALARMI" if acil_refleks_gerekli else "MUTEDİL"}


class AkileKatmani:
    __slots__ = ("baglam_hafizasi",)

    def __init__(self) -> None:
        self.baglam_hafizasi: List[Any] = []

    def nazari_akil_denetle(self, ispat_sahidi: Optional[Terim], baglam: Tuple[int, ...],
                            hedef: int) -> bool:
        return ispat_sahidini_dogrula(ispat_sahidi, baglam, hedef)

    def ameli_akil_tart(self, hedef_id: int, vahime_raporu: Dict[str, Any],
                        hedef_beklentisi: float) -> Dict[str, Any]:
        tehdit = vahime_raporu["tehdit"]
        fayda = vahime_raporu["fayda"]

        maslahat_skoru = float(hedef_beklentisi * fayda - 0.5 * tehdit)

        logit = maslahat_skoru * 3.0 - tehdit * 2.0
        irade_katsayisi = float(1.0 / (1.0 + np.exp(-logit)))

        ahlaki_onay = bool(maslahat_skoru > 0.0)

        return {"maslahat_skoru": maslahat_skoru, "irade_katsayisi": irade_katsayisi,
                "ahlaki_onay": ahlaki_onay,
                "ameli_hukum": "İHTİYÂRÎ_SEVK" if ahlaki_onay else "DEF_İSTİKÂMETİ"}


class KuvveiBaiseVeMotorlar:
    __slots__ = ("n_boyut",)

    def __init__(self, n_boyut: int) -> None:
        self.n_boyut = int(n_boyut)

    def sevk_ve_icra(self, aday_hedef: int, vahime_raporu: Dict[str, Any],
                     ameli_akil_raporu: Dict[str, Any], P_satiri: np.ndarray) -> Dict[str, Any]:
        n = self.n_boyut
        alpha = ameli_akil_raporu["irade_katsayisi"]

        v_cezb = np.zeros(n, dtype=float)
        v_cezb[aday_hedef] = vahime_raporu["fayda"]
        v_cezb += P_satiri * 0.3
        v_cezb /= (np.linalg.norm(v_cezb) + 1e-12)

        v_def = np.zeros(n, dtype=float)
        if vahime_raporu["tehdit"] > 0.1:
            v_def[aday_hedef] = vahime_raporu["tehdit"]
        v_def /= (np.linalg.norm(v_def) + 1e-12)

        v_akil = np.zeros(n, dtype=float)
        if ameli_akil_raporu["ahlaki_onay"]:
            v_akil[aday_hedef] = 1.0
        else:
            ikinci_aday = int(np.argsort(P_satiri)[-2]) if len(P_satiri) > 1 else aday_hedef
            v_akil[ikinci_aday] = 1.0

        eylem_vektoru = alpha * v_akil + (1.0 - alpha) * (v_cezb - 0.7 * v_def)
        eylem_vektoru = np.maximum(0.0, eylem_vektoru)

        nihai_icra_tokeni = int(np.argmax(eylem_vektoru))

        sevk_kaynagi = ("AKLÎ_İHTİYÂR" if alpha >= 0.5
                        else ("HAYVANÎ_CEZB" if v_cezb[aday_hedef] > v_def[aday_hedef] else "HAYVANÎ_DEF"))

        return {"nihai_icra_tokeni": nihai_icra_tokeni, "sevk_kaynagi": sevk_kaynagi,
                "irade_payi": alpha, "cezb_kuvveti": float(v_cezb[aday_hedef]),
                "def_kuvveti": float(v_def[aday_hedef]), "eylem_vektoru": eylem_vektoru}


def topos_modalite_lifi_isle(hakikat_degeri: float, tenakuz_derecesi: float,
                             omega_cebiri: str) -> Dict[str, Any]:
    val = float(np.clip(hakikat_degeri, 0.0, 1.0))
    t_derece = float(np.clip(tenakuz_derecesi, 0.0, 1.0))

    kutu_zorunluluk = 1.0 if (val >= 0.95 and t_derece < 0.05) else 0.0
    elmas_imkan = 1.0 if (val > 0.05 or t_derece > 0.0) else 0.0

    if t_derece > 0.2:
        terfi_hukmu = "MODALİTE_LİFİNE_TERFİ_ETTİ"
        modal_kuantum_degeri = complex(elmas_imkan * np.cos(np.pi * t_derece),
                                       elmas_imkan * np.sin(np.pi * t_derece))
    else:
        terfi_hukmu = "ASLİ_LİFTE_KALDI"
        modal_kuantum_degeri = complex(val, 0.0)

    return {"box_zorunluluk": kutu_zorunluluk, "diamond_imkan": elmas_imkan,
            "terfi_hukmu": terfi_hukmu, "modal_kuantum_degeri": modal_kuantum_degeri}


def alt_nesne_pullback_chi(chi_hedef_haritasi: Dict[int, float],
                           ok_gecisleri: Dict[Tuple[int, int], int],
                           P: np.ndarray, Kan_rez: np.ndarray) -> Dict[int, float]:
    geri_cekilen_chi: Dict[int, float] = {}

    for (x, y) in ok_gecisleri.keys():
        if y in chi_hedef_haritasi:
            hedef_deger = chi_hedef_haritasi[y]
            gecis_kuvveti = float(P[x, y])
            tikanma = float(Kan_rez[x, y])

            cekilen_deger = hedef_deger * gecis_kuvveti * (1.0 - 0.5 * tikanma)

            if x not in geri_cekilen_chi or cekilen_deger > geri_cekilen_chi[x]:
                geri_cekilen_chi[x] = float(np.clip(cekilen_deger, 0.0, 1.0))

    return geri_cekilen_chi


class ImajFaktorizasyonu:
    __slots__ = ("kaynak", "hedef", "imaj_nesnesi", "epimorfizm_id", "monomorfizm_id")

    def __init__(self, kaynak: int, hedef: int, imaj_id: int, epi_id: int, mono_id: int) -> None:
        self.kaynak = kaynak
        self.hedef = hedef
        self.imaj_nesnesi = imaj_id
        self.epimorfizm_id = epi_id
        self.monomorfizm_id = mono_id


def kategori_imaj_faktorizasyonu_yap(kat: Turetilen1Kategori,
                                     P: np.ndarray) -> Dict[Tuple[int, int], ImajFaktorizasyonu]:
    faktorizasyonlar: Dict[Tuple[int, int], ImajFaktorizasyonu] = {}
    yeni_imaj_tabani = max(kat.nesneler, default=0) + 2000
    sayac = 0

    for (x, y), ok_id in kat.ok_siniflari.items():
        if x == y:
            continue
        imaj_id = yeni_imaj_tabani + sayac
        epi_id = len(kat.ok_siniflari) + sayac * 2
        mono_id = len(kat.ok_siniflari) + sayac * 2 + 1

        faktorizasyonlar[(x, y)] = ImajFaktorizasyonu(
            kaynak=x, hedef=y, imaj_id=imaj_id, epi_id=epi_id, mono_id=mono_id)
        sayac += 1

    return faktorizasyonlar


def frobenius_ko_carpim_klonla(nesne_id: int,
                               monoidal_kat: MonoidalKategori) -> Tuple[int, Tuple[int, int]]:
    klon_nesne = monoidal_kat.tensor_nesneleri.get((nesne_id, nesne_id))
    if klon_nesne is None:
        n_id = max(monoidal_kat.kategori.nesneler, default=0) + 1
        klon_nesne = nesne_id * n_id + nesne_id
        monoidal_kat.tensor_nesneleri[(nesne_id, nesne_id)] = klon_nesne

    delta_morfizmi = (nesne_id, klon_nesne)
    return klon_nesne, delta_morfizmi


class ManeviKalpKatmani:
    __slots__ = ("niyet_vektoru", "itminan_esigi", "gecmis_huzur")

    def __init__(self, niyet_boyutu: int = 8, itminan_esigi: float = 0.70) -> None:
        self.niyet_vektoru = np.ones(niyet_boyutu, dtype=float) / np.sqrt(niyet_boyutu)
        self.itminan_esigi = float(itminan_esigi)
        self.gecmis_huzur: List[float] = []

    def itminan_olc(self, kuantum_durum: np.ndarray) -> float:
        guc = np.abs(kuantum_durum) ** 2
        guc = guc[guc > 1e-12]
        entropi = float(-np.sum(guc * np.log2(guc))) if len(guc) else 0.0
        maks_entropi = np.log2(len(kuantum_durum)) if len(kuantum_durum) > 1 else 1.0
        return float(np.clip(1.0 - (entropi / (maks_entropi + 1e-12)), 0.0, 1.0))

    def vicdani_murakabe(self, eylem_vektoru: np.ndarray, itminan: float) -> Dict[str, Any]:
        d = min(len(self.niyet_vektoru), len(eylem_vektoru))
        uyum = float(np.dot(self.niyet_vektoru[:d], eylem_vektoru[:d]))
        huzur_skoru = float(0.6 * uyum + 0.4 * itminan)
        self.gecmis_huzur.append(huzur_skoru)

        if itminan >= self.itminan_esigi and uyum > 0.3:
            durum, fetva = "KALBÎ_İTMİNÂN_VE_HUZUR", True
        else:
            durum, fetva = "VİCDANÎ_ŞÜPHE_VE_IKRAH", False

        return {"kalp_durumu": durum, "itminan_derecesi": itminan,
                "vicdani_huzur_skoru": huzur_skoru, "kalbi_fetva": fetva}


class AklinDortMertebesi:
    __slots__ = ("meleke_aksiyomlari", "bilfiil_kanunlar", "faal_akil_rezonansi")

    def __init__(self) -> None:
        self.meleke_aksiyomlari = ["çelişmezlik_aksiyomu", "özdeşlik_aksiyomu", "üçüncü_halin_imkânsızlığı"]
        self.bilfiil_kanunlar: Dict[str, Terim] = {}
        self.faal_akil_rezonansi: float = 0.0

    def mertebe_tayin_et(self, ispat_sayisi: int, tikaniklik: float,
                          kulli_ispat_var_mi: bool) -> str:
        if ispat_sayisi == 0 and tikaniklik > 0.5:
            return "AKL_I_HEYÛLÂNÎ"
        elif ispat_sayisi > 0 and not kulli_ispat_var_mi:
            return "AKL_I_BIL_MELEKE"
        elif kulli_ispat_var_mi and tikaniklik < 0.1:
            self.faal_akil_rezonansi = 0.95
            return "AKL_I_MÜSTEFÂD"
        else:
            return "AKL_I_BIL_FIIL"


def hads_ile_orta_terim_yakala(P: np.ndarray, son_token: int, hedef: int,
                               hads_esigi: float = 0.25) -> Tuple[Optional[int], str, float]:
    n = P.shape[0]
    bas_vektor = P[son_token, :]
    hedef_vektor = P[:, hedef]

    rezonans = bas_vektor * hedef_vektor
    en_kuvvetli_orta_terim = int(np.argmax(rezonans))
    kuvvet = float(rezonans[en_kuvvetli_orta_terim])

    if kuvvet >= hads_esigi and en_kuvvetli_orta_terim != son_token and en_kuvvetli_orta_terim != hedef:
        return en_kuvvetli_orta_terim, "HADS_I_KUDSI_SEZGI", kuvvet
    else:
        return None, "FIKRI_TEEMMUL_GEREKLI", kuvvet


class NefsiNebatiKatmani:
    __slots__ = ("metabolik_enerji", "canlilik_kapasitesi", "tohum_arsivi")

    def __init__(self, baslangic_enerjisi: float = 1.0) -> None:
        self.metabolik_enerji = float(baslangic_enerjisi)
        self.canlilik_kapasitesi = 1.0
        self.tohum_arsivi: List[Dict[str, Any]] = []

    def taziye_gidalan(self, veri_akisi_uzunlugu: int, entropi_kaybi: float) -> float:
        besin_degeri = np.log1p(float(veri_akisi_uzunlugu)) * 0.1
        harcanan = float(entropi_kaybi) * 0.05
        self.metabolik_enerji = float(np.clip(self.metabolik_enerji + besin_degeri - harcanan, 0.1, 5.0))
        return self.metabolik_enerji

    def tenmiye_buyu(self, mevcut_lif_boyutu: int, veri_zenginligi: int) -> int:
        if veri_zenginligi > mevcut_lif_boyutu and self.metabolik_enerji > 1.5:
            self.canlilik_kapasitesi += 0.1
            return mevcut_lif_boyutu + 2
        return mevcut_lif_boyutu

    def tevlid_tohumla(self, topos_durumu: Dict[str, Any]) -> Dict[str, Any]:
        tohum = {"tohum_id": len(self.tohum_arsivi) + 1,
                "enerji_mirasi": self.metabolik_enerji * 0.5,
                "omega": topos_durumu.get("omega_cebiri", "heyting"),
                "parite": topos_durumu.get("parite_lifi", [])}
        self.tohum_arsivi.append(tohum)
        return tohum


class FibrasyonluManaLifi:
    __slots__ = ("suret_kategorisi", "mana_lifleri", "kartezyen_tasimalar")

    def __init__(self, suret_kategorisi: Turetilen1Kategori) -> None:
        self.suret_kategorisi = suret_kategorisi
        self.mana_lifleri: Dict[int, np.ndarray] = {}
        self.kartezyen_tasimalar: Dict[Tuple[int, int], np.ndarray] = {}

    def mana_lifi_ekle(self, suret_id: int, mana_vektoru: np.ndarray) -> None:
        self.mana_lifleri[suret_id] = np.asarray(mana_vektoru, dtype=float)

    def kartezyen_ok_tasi(self, x: int, y: int, P: np.ndarray) -> np.ndarray:
        mana_x = self.mana_lifleri.get(x, np.zeros(4))
        gecis = float(P[x, y])
        mana_y_tahmin = mana_x * gecis
        self.kartezyen_tasimalar[(x, y)] = mana_y_tahmin
        return mana_y_tahmin


class IcselKategoriNesnesi:
    __slots__ = ("C0_nesneler", "C1_oklar", "kaynak_s", "hedef_t", "bileske_m")

    def __init__(self, kat: Turetilen1Kategori) -> None:
        self.C0_nesneler = list(kat.nesneler)
        self.C1_oklar = list(kat.ok_siniflari.values())
        self.kaynak_s = {oid: cift[0] for cift, oid in kat.ok_siniflari.items()}
        self.hedef_t = {oid: cift[1] for cift, oid in kat.ok_siniflari.items()}
        self.bileske_m = dict(kat.bileske_tablosu)

    def topos_nesnesi_olarak_kodla(self) -> Terim:
        return Cift(Dogal(), Cift(Dogal(), dogal_sayi(len(self.C1_oklar))))


class PolinomyalMutasarrifaTezgahi:
    __slots__ = ("islemler_B", "ariteler_E")

    def __init__(self, islemler: List[str], ariteler: List[int]) -> None:
        self.islemler_B = islemler
        self.ariteler_E = ariteler

    def hipotetik_terkip_dogur(self, hammadde_suretler: List[int]) -> Tuple[int, str]:
        yeni_id = sum(hammadde_suretler) + 777
        terkip_adi = "Terkip_" + "_".join(str(x) for x in hammadde_suretler[:3])
        return yeni_id, terkip_adi


def topos_terminal_buzulme_itminan(kat: Turetilen1Kategori, P: np.ndarray,
                                   kuantum_durum: np.ndarray) -> Dict[str, Any]:
    n = len(kat.nesneler)
    if n == 0:
        return {"itminan_derecesi": 1.0, "kalp_huzuru": True}

    baglanti_dereceleri = []
    for x in kat.nesneler:
        out_gucu = float(np.sum(P[x, :])) if x < P.shape[0] else 0.0
        baglanti_dereceleri.append(out_gucu)

    ortalama_akıs = float(np.mean(baglanti_dereceleri)) if baglanti_dereceleri else 0.0
    kuantum_safligi = float(np.sum(np.abs(kuantum_durum) ** 4))

    itminan_derecesi = float(np.clip(kuantum_safligi * (ortalama_akıs / (float(n) + 1e-12)), 0.0, 1.0))
    kalp_huzuru = bool(itminan_derecesi > 0.4)

    return {"itminan_derecesi": itminan_derecesi, "kalp_huzuru": kalp_huzuru,
            "terminal_morfizm_akisi": ortalama_akıs}


def ko_yoneda_yogunluk_sentezle(veri_dagilimi: np.ndarray, P: np.ndarray,
                                kat: Turetilen1Kategori) -> Dict[str, Any]:
    n = P.shape[0]
    F_c = veri_dagilimi / (np.linalg.norm(veri_dagilimi) + 1e-12)

    kolimit_temsili = np.zeros(n, dtype=float)
    agirliklar = {}

    for c in kat.nesneler:
        if c < n:
            h_c = P[:, c]
            katsayi = float(F_c[c])
            kolimit_temsili += katsayi * h_c
            agirliklar[c] = katsayi

    kolimit_normu = float(np.linalg.norm(kolimit_temsili))
    kolimit_temsili /= (kolimit_normu + 1e-12)

    return {"kolimit_vektoru": kolimit_temsili,
            "yogunluk_sadakati": float(np.dot(F_c, kolimit_temsili)),
            "temsil_agirliklari": agirliklar}


def coequalizer_evrensel_faktorizasyon(ok1_id: int, ok2_id: int,
                                       h_haritasi: Dict[int, int],
                                       kat: Turetilen1Kategori) -> Dict[str, Any]:
    bolum_q = topos_es_esitleyici_coequalizer(ok1_id, ok2_id, kat)

    f_cifti = next((cift for cift, oid in kat.ok_siniflari.items() if oid == ok1_id), None)
    g_cifti = next((cift for cift, oid in kat.ok_siniflari.items() if oid == ok2_id), None)

    uyumlu = True
    if f_cifti and g_cifti and f_cifti[0] == g_cifti[0]:
        hedef_f = f_cifti[1]
        hedef_g = g_cifti[1]
        if h_haritasi.get(hedef_f) != h_haritasi.get(hedef_g):
            uyumlu = False

    h_bar: Dict[int, int] = {}
    for b_nesne, q_denklik in bolum_q.items():
        if b_nesne in h_haritasi:
            h_bar[q_denklik] = h_haritasi[b_nesne]

    return {"bolum_q": bolum_q, "evrensel_h_bar": h_bar, "faktorizasyon_gecerli_mi": uyumlu}


def topolojik_yuk_chern_sayisi(P: np.ndarray, Asim: np.ndarray,
                               ucgen_listesi: Sequence[Tuple[int, int, int]]) -> Dict[str, Any]:
    if not ucgen_listesi:
        return {"chern_sayisi_c1": 0, "toplam_faz": 0.0, "topolojik_monopol_var_mi": False}

    toplam_faz = 0.0
    for (i, j, k) in ucgen_listesi:
        holonomi = analitik_lie_bargmann_adimi(i, j, k, P, Asim)
        toplam_faz += holonomi["bargmann_phi"]

    chern_sayisi = int(np.round(toplam_faz / (2.0 * np.pi)))
    monopol_var = bool(chern_sayisi != 0)

    return {"chern_sayisi_c1": chern_sayisi, "toplam_faz_radyan": float(toplam_faz),
            "topolojik_monopol_var_mi": monopol_var}


def kripke_joyal_forcing(baglam_U: Tuple[int, ...], onerme_phi: Dict[int, float],
                         onerme_psi: Dict[int, float], P: np.ndarray,
                         omega_cebiri: str) -> Dict[str, Any]:
    durumlar = list(set(baglam_U))
    if not durumlar:
        return {"U_zorlar_mi": True, "kuvvet": 1.0}

    yerel_uyumlar = []
    for u in durumlar:
        v_phi = onerme_phi.get(u, 0.0)
        v_psi = onerme_psi.get(u, 0.0)

        if omega_cebiri == "boole":
            uyum = 1.0 if (v_phi <= v_psi) else 0.0
        else:
            uyum = 1.0 if v_phi <= v_psi else v_psi
        yerel_uyumlar.append(uyum)

    en_zayif_halka = float(min(yerel_uyumlar))
    zorlar_mi = bool(en_zayif_halka >= 0.85)

    return {"U_zorlar_mi": zorlar_mi, "asgari_uyum": en_zayif_halka, "asama_boyutu": len(durumlar)}


def topos_diyagonal_esitlik_chi(x: int, y: int, P: np.ndarray,
                                Asim: np.ndarray, omega_cebiri: str) -> float:
    if x == y:
        return 1.0

    simetri = 1.0 - float(Asim[x, y])
    ortusme = float(np.sqrt(P[x, y] * P[y, x]))
    derece = float(np.clip(ortusme * simetri, 0.0, 1.0))

    if omega_cebiri == "boole":
        return 1.0 if derece > 0.8 else 0.0
    return derece


def tannaka_simetri_grubu_turet(kat: Turetilen1Kategori, P: np.ndarray) -> Dict[str, Any]:
    nesneler = kat.nesneler
    k = len(nesneler)
    if k < 2:
        return {"simetri_grubu": "U(1)", "boyut": 1, "invaryant_iz": 1.0}

    alt_P = P[np.ix_(nesneler, nesneler)]
    komutator = alt_P @ alt_P.T - alt_P.T @ alt_P
    komutator_normu = float(np.linalg.norm(komutator))

    if komutator_normu < 1e-4:
        simetri = "Abelien_U(1)^%d" % k
    else:
        simetri = "GayriAbelien_SU(%d)" % min(k, 3)

    return {"simetri_grubu": simetri, "komutator_sapmasi": komutator_normu, "tannaka_boyutu": k}


def berry_ayar_potansiyeli_ve_fazi(psi: np.ndarray, parametre_acilari: np.ndarray,
                                   d_psi: np.ndarray) -> Dict[str, Any]:
    norm_psi = psi / (np.linalg.norm(psi) + 1e-12)

    ic_carpim = np.vdot(norm_psi, d_psi)
    ayar_potansiyeli = float(-np.imag(ic_carpim))

    adim_farki = float(np.mean(np.diff(parametre_acilari))) if len(parametre_acilari) > 1 else 0.1
    berry_fazi = float(ayar_potansiyeli * adim_farki)

    return {"berry_ayar_potansiyeli": ayar_potansiyeli, "geometrik_berry_fazi": berry_fazi,
            "anomalik_faz_var_mi": bool(abs(berry_fazi) > 0.2)}


def kan_genlik_hesapla_normalize(u: float, C_katsayilari: np.ndarray, S_katsayilari: np.ndarray,
                                  enerji: float, cartan_fazi: float) -> Tuple[complex, float]:
    T, U = kan_chebyshev_intac(u, derece=len(C_katsayilari))

    reel_bileske = float(np.dot(C_katsayilari, T))
    sanal_bileske = float(np.dot(S_katsayilari, U))

    bolen = np.exp(-2.0 * float(enerji)) * (reel_bileske ** 2 + sanal_bileske ** 2) + 1e-12
    kok_bolen = float(np.sqrt(bolen))

    faz_terimi = sanal_bileske + float(cartan_fazi)
    ham_genlik = np.exp(-float(enerji) + 1j * faz_terimi) * (reel_bileske + 1j * sanal_bileske)

    normalize_genlik = complex(ham_genlik / kok_bolen)
    return normalize_genlik, kok_bolen


def t4_kan_nedensel_cephe_baglantisi(kan_genlik: complex, son_token: int,
                                     theta_cartan: float, veri_lifi: int = 8) -> Dict[str, Any]:
    d = int(veri_lifi)
    born_dagilimi = np.zeros(d, dtype=float)

    for c in range(d):
        faz_c = theta_cartan * float(c + 1) / float(d)
        qudit_c_genlik = kan_genlik * np.exp(1j * faz_c)
        born_dagilimi[c] = float(np.abs(qudit_c_genlik) ** 2)

    born_dagilimi /= (np.sum(born_dagilimi) + 1e-12)
    secilen_basamak = int(np.argmax(born_dagilimi))

    return {"secilen_basamak": secilen_basamak, "olcum_guveni": float(born_dagilimi[secilen_basamak]),
            "born_dagilimi": born_dagilimi, "kan_nedensel_faz": float(np.angle(kan_genlik))}


def maurer_cartan_egriligi_denetle(X_lie: np.ndarray, Asim: np.ndarray,
                                   son_token: int, hedef: int) -> Dict[str, Any]:
    komutator = X_lie @ X_lie.conj().T - X_lie.conj().T @ X_lie

    dx_norm = float(abs(Asim[son_token, hedef] - Asim[hedef, son_token]))

    mc_matrisi = dx_norm * np.eye(X_lie.shape[0]) + 0.5 * komutator
    mc_egrilik_normu = float(np.linalg.norm(mc_matrisi))

    baglanti_duz_mu = bool(mc_egrilik_normu < 0.15)

    return {"mc_egrilik_normu": mc_egrilik_normu, "baglanti_duz_mu": baglanti_duz_mu,
            "ayar_anomalisi_var_mi": not baglanti_duz_mu}


def yazmacta_bolge_yoktur_superpozisyon(rho: np.ndarray,
                                        n_boyut: int) -> Tuple[np.ndarray, np.ndarray]:
    toplam_boyut = 4 * n_boyut
    psi_superpozisyon = np.zeros(toplam_boyut, dtype=complex)

    for mod_k in range(4):
        genlik_k = np.sqrt(rho[mod_k])
        faz_k = np.exp(1j * np.pi * mod_k / 2.0)
        bas = mod_k * n_boyut
        son = (mod_k + 1) * n_boyut
        psi_superpozisyon[bas:son] = (genlik_k * faz_k) / np.sqrt(float(n_boyut))

    norm = float(np.linalg.norm(psi_superpozisyon))
    psi_superpozisyon /= (norm + 1e-12)

    kod_uzayi_operatoru = np.ones(toplam_boyut, dtype=float)
    kod_uzayi_operatoru[3 * n_boyut:4 * n_boyut] = 0.0

    return psi_superpozisyon, kod_uzayi_operatoru


def degisken_boylu_bargmann_halkasi(P: np.ndarray, Asim: np.ndarray,
                                    dongu_yolu: Sequence[int]) -> Dict[str, Any]:
    m = len(dongu_yolu)
    if m < 2:
        return {"halka_boyu": m, "r_n": 1.0, "phi_n": 0.0, "mobius_tenakuz_mu": False}

    delta_n = complex(1.0, 0.0)
    en_kucuk_yerel_ortusme = 1.0

    for k in range(m):
        u = dongu_yolu[k]
        v = dongu_yolu[(k + 1) % m]

        p_uv = float(P[u, v]) if u < P.shape[0] and v < P.shape[1] else 1e-12
        en_kucuk_yerel_ortusme = min(en_kucuk_yerel_ortusme, p_uv)

        faz_uv = np.pi * float(Asim[u, v]) if u < Asim.shape[0] and v < Asim.shape[1] else 0.0
        u_uv = np.sqrt(max(1e-12, p_uv)) * np.exp(1j * faz_uv)
        delta_n *= u_uv

    r_n = float(np.abs(delta_n))
    phi_n = float(np.angle(delta_n))

    mobius_tenakuz = bool(en_kucuk_yerel_ortusme > 0.1 and abs(abs(phi_n) - np.pi) < 0.5)
    kisirdongu = bool(abs(phi_n) < 0.3 and r_n > 1e-4)

    return {"halka_boyu": m, "r_n": r_n, "phi_n": phi_n,
            "en_kucuk_yerel_ortusme": en_kucuk_yerel_ortusme,
            "mobius_tenakuz_mu": mobius_tenakuz, "kisirdongu_mu": kisirdongu}


def d8a_vadi_memuru_yonu(egim_vektoru: np.ndarray, g_fs_metrigi: np.ndarray,
                         sira_vektoru: np.ndarray) -> np.ndarray:
    d = len(egim_vektoru)
    g_fs = g_fs_metrigi[:d] if len(g_fs_metrigi) >= d else np.ones(d)

    vadi_itkisi = -egim_vektoru * g_fs * (sira_vektoru[:d] if len(sira_vektoru) >= d else 1.0)
    norm = float(np.linalg.norm(vadi_itkisi))

    if norm > 1e-12:
        yon_vadi = vadi_itkisi / norm
    else:
        yon_vadi = -egim_vektoru / (np.linalg.norm(egim_vektoru) + 1e-12)

    return yon_vadi


def sadakat_invaryant_I8_denetle(mevcut_superpozisyonlar: Dict[str, np.ndarray],
                                  kod_uzayi_maskesi: np.ndarray,
                                  muaf_listesi: Optional[List[str]] = None) -> Dict[str, Any]:
    zorunlu_liste = {"veri", "parametre", "mahalli", "hafiza", "fock", "cozum"}
    muaf = list(muaf_listesi or [])

    if len(muaf) > 0:
        raise DenetimHatasi("İNVARYANT I8 İHLALİ: Sadakat devresinden muaf süperpozisyon olamaz: %s" % muaf)

    kayitli_isimler = set(mevcut_superpozisyonlar.keys())
    baglanmamis_superpozisyonlar = list(zorunlu_liste - kayitli_isimler)

    toplam_imha = 0
    toplam_meçhul = 0
    toplam_mumkun = 0

    for isim, psi in mevcut_superpozisyonlar.items():
        d = len(psi)
        maske = kod_uzayi_maskesi[:d] if len(kod_uzayi_maskesi) >= d else np.ones(d)
        rapor = sadakat_devresi_kos(psi, maske)
        toplam_imha += rapor["imha"]
        toplam_meçhul += rapor["meçhul"]
        toplam_mumkun += rapor["mumkun"]

    return {"invaryant_I8_saglandi_mi": bool(len(baglanmamis_superpozisyonlar) == 0),
            "baglanmamis_sayisi": len(baglanmamis_superpozisyonlar),
            "baglanmamis_isimler": baglanmamis_superpozisyonlar,
            "toplam_imha": toplam_imha, "toplam_meçhul": toplam_meçhul,
            "toplam_mumkun": toplam_mumkun}


class DogalDonusum2Hucresi:
    __slots__ = ("funktor_F_adi", "funktor_G_adi", "bilesenler_alpha")

    def __init__(self, F_adi: str, G_adi: str, bilesenler: Dict[int, int]) -> None:
        self.funktor_F_adi = F_adi
        self.funktor_G_adi = G_adi
        self.bilesenler_alpha = bilesenler

    def komutatif_kare_dogrula(self, kat: Turetilen1Kategori,
                               F_haritasi: Dict[int, int], G_haritasi: Dict[int, int]) -> bool:
        for (x, y), f_ok_id in kat.ok_siniflari.items():
            alpha_x = self.bilesenler_alpha.get(x)
            alpha_y = self.bilesenler_alpha.get(y)
            F_f = F_haritasi.get(f_ok_id, f_ok_id)
            G_f = G_haritasi.get(f_ok_id, f_ok_id)

            if alpha_x is not None and alpha_y is not None:
                sol_yol = kat.bileske_tablosu.get((alpha_x, G_f))
                sag_yol = kat.bileske_tablosu.get((F_f, alpha_y))

                if sol_yol is not None and sag_yol is not None and sol_yol != sag_yol:
                    return False
        return True


class J4GeriYolDenetleyicisi:
    __slots__ = ("maskelenmis_tokenler", "negatif_ceza")

    def __init__(self, negatif_ceza: float = 1e4) -> None:
        self.maskelenmis_tokenler: Set[int] = set()
        self.negatif_ceza = float(negatif_ceza)

    def kisit_projeksiyonu_olc(self, hedef_token: int, psi: np.ndarray,
                               kod_uzayi_maskesi: np.ndarray) -> float:
        d = min(len(psi), len(kod_uzayi_maskesi))
        psi_kisit = psi[:d] * kod_uzayi_maskesi[:d]
        norm_toplam = float(np.sum(np.abs(psi[:d]) ** 2)) + 1e-12
        norm_kisit = float(np.sum(np.abs(psi_kisit) ** 2))
        return float(norm_kisit / norm_toplam)

    def geri_yol_denetle(self, secilen_hedef: int, n_kisit_normu: float,
                         born_logitleri: np.ndarray) -> Tuple[int, bool, np.ndarray]:
        yeni_logitler = born_logitleri.copy()

        if n_kisit_normu < 1e-3:
            if secilen_hedef in self.maskelenmis_tokenler:
                return secilen_hedef, False, yeni_logitler

            self.maskelenmis_tokenler.add(secilen_hedef)
            yeni_logitler[secilen_hedef] -= self.negatif_ceza
            yeni_hedef = int(np.argmax(yeni_logitler))
            return yeni_hedef, True, yeni_logitler

        return secilen_hedef, False, yeni_logitler


def hata_engel_zeno_olc(psi_onceki: np.ndarray, psi_simdiki: np.ndarray,
                        U_kapi: np.ndarray) -> float:
    d = min(len(psi_onceki), len(psi_simdiki), U_kapi.shape[0])
    v_onceki = psi_onceki[:d] / (np.linalg.norm(psi_onceki[:d]) + 1e-12)
    v_simdiki = psi_simdiki[:d] / (np.linalg.norm(psi_simdiki[:d]) + 1e-12)

    v_evrilmis = U_kapi[:d, :d] @ v_onceki
    v_evrilmis /= (np.linalg.norm(v_evrilmis) + 1e-12)

    ortusme = float(np.abs(np.vdot(v_simdiki, v_evrilmis)) ** 2)
    return float(np.clip(1.0 - ortusme, 0.0, 1.0))


class MunasebetHaritasi:
    __slots__ = ("harita",)

    def __init__(self) -> None:
        self.harita: Dict[Tuple[int, ...], float] = {}

    def munasebet_guncelle(self, baglam: Tuple[int, ...], kuvvet: float = 1.0) -> None:
        self.harita[baglam] = self.harita.get(baglam, 0.0) + float(kuvvet)

    def zayiflik_olc(self, baglam: Tuple[int, ...]) -> float:
        m = self.harita.get(baglam, 0.0)
        return float(1.0 / (1.0 + m))


def boynuz_turu_ayristir_ve_doldur(n_boyut: int, k_kose: int, P: np.ndarray,
                                   Asim: np.ndarray, kenar_dizisi: Sequence[int]) -> Dict[str, Any]:
    is_inner = bool(0 < k_kose < n_boyut)
    u, v = kenar_dizisi[0], kenar_dizisi[-1]

    if is_inner:
        boynuz_turu = "IC_BOYNUZ_YONLU_KATEGORI"
        dolgu_uyumu = float(P[u, v])
        gecerli = bool(dolgu_uyumu > 0.01)
    else:
        boynuz_turu = "DIS_BOYNUZ_TERSIMLI_GRUPOID"
        simetri = 1.0 - float(Asim[u, v])
        gecerli = bool(simetri > 0.70 and P[u, v] > 0.05)

    return {"boyut_n": n_boyut, "kose_k": k_kose, "boynuz_turu": boynuz_turu,
            "ic_boynuz_mu": is_inner, "boynuz_doldu_mu": gecerli}


class DereceliMertebeKulesi:
    __slots__ = ("maks_mertebe", "mertebe_agirliklari", "mertebe_durumlari")

    def __init__(self, maks_mertebe: int = 4) -> None:
        self.maks_mertebe = int(maks_mertebe)
        self.mertebe_agirliklari = np.ones(self.maks_mertebe, dtype=float) / float(self.maks_mertebe)
        self.mertebe_durumlari: Dict[int, np.ndarray] = {}

    def mertebe_durumu_guncelle(self, n_seviye: int, durum_vektoru: np.ndarray,
                                eylemsel_agirlik: float) -> None:
        if 1 <= n_seviye <= self.maks_mertebe:
            norm = np.linalg.norm(durum_vektoru) + 1e-12
            self.mertebe_durumlari[n_seviye] = durum_vektoru / norm
            self.mertebe_agirliklari[n_seviye - 1] = float(eylemsel_agirlik)
            toplam = np.sum(self.mertebe_agirliklari) + 1e-12
            self.mertebe_agirliklari /= toplam

    def eszamanli_kullî_vektor(self, taban_boyut: int) -> np.ndarray:
        kulli_dalga = np.zeros(taban_boyut, dtype=complex)
        for n in range(1, self.maks_mertebe + 1):
            if n in self.mertebe_durumlari:
                psi_n = self.mertebe_durumlari[n]
                pay = np.sqrt(self.mertebe_agirliklari[n - 1])
                faz = np.exp(1j * np.pi * float(n) / float(self.maks_mertebe))
                d = min(taban_boyut, len(psi_n))
                kulli_dalga[:d] += pay * faz * psi_n[:d]

        norm = float(np.linalg.norm(kulli_dalga))
        return (kulli_dalga / norm) if norm > 1e-12 else kulli_dalga


class IkiYonluMertebeAsansoru:
    __slots__ = ("mevcut_mertebe", "tavan_mertebe")

    def __init__(self, tavan_mertebe: int = 4) -> None:
        self.mevcut_mertebe = 1
        self.tavan_mertebe = int(tavan_mertebe)

    def yukari_tirman(self, alt_engel: float) -> Tuple[int, str]:
        if alt_engel > 0.15 and self.mevcut_mertebe < self.tavan_mertebe:
            self.mevcut_mertebe += 1
            hukum = "MERTEBE_YÜKSELDİ_TIRMANIŞ_n%d" % self.mevcut_mertebe
        else:
            hukum = "MERTEBE_SABİT_n%d" % self.mevcut_mertebe
        return self.mevcut_mertebe, hukum

    def asagi_in_intac(self, ust_koherans_tam_mi: bool) -> Tuple[int, str]:
        if ust_koherans_tam_mi and self.mevcut_mertebe > 1:
            self.mevcut_mertebe -= 1
            hukum = "MERTEBE_İNDİ_SOMUTLAŞMA_n%d" % self.mevcut_mertebe
        else:
            hukum = "MERTEBE_KORUNDU_n%d" % self.mevcut_mertebe
        return self.mevcut_mertebe, hukum

    def asagi_in_intac_lifli(self, tensor: Dict[str, Any], kat: "Turetilen1Kategori",
                             hedef_nesne: int, ust_koherans_tam_mi: bool
                             ) -> Tuple[int, str, Optional[np.ndarray]]:
        inis = tip_tensoru_asagi_in(tensor, hedef_nesne, kat)
        gercek_koheran = bool(ust_koherans_tam_mi and inis["bulundu"]
                              and len(inis["hom_kurallari"]) > 0)
        if gercek_koheran and self.mevcut_mertebe > 1:
            self.mevcut_mertebe -= 1
            hukum = ("MERTEBE_İNDİ_SOMUTLAŞMA_LİFLİ_n%d (hom=%d, lif_boyu=%d)"
                     % (self.mevcut_mertebe, len(inis["hom_kurallari"]),
                        int(inis["lif"].size)))
            lif_vektoru = inis["lif"]
        else:
            sebep = ("KOHERANS_YOK" if not ust_koherans_tam_mi
                    else ("NESNE_BULUNAMADI" if not inis["bulundu"]
                          else "HOM_BOŞ"))
            hukum = "MERTEBE_KORUNDU_LİFSİZ_n%d (%s)" % (self.mevcut_mertebe, sebep)
            lif_vektoru = None
        return self.mevcut_mertebe, hukum, lif_vektoru

    def yukari_tirman_lifli(self, tensor: Dict[str, Any], kat: "Turetilen1Kategori",
                            alt_nesne: int, ust_nesne: int, alt_engel: float
                            ) -> Tuple[int, str, Optional[np.ndarray]]:
        cikis = tip_tensoru_yukari_cik(tensor, kat, alt_nesne, ust_nesne)
        tasindi = bool(cikis["tasindi"])
        if alt_engel > 0.15 and tasindi and self.mevcut_mertebe < self.tavan_mertebe:
            self.mevcut_mertebe += 1
            lift = cikis["kartezyen_lift_vektoru"]
            hukum = ("MERTEBE_YÜKSELDİ_TIRMANIŞ_LİFLİ_n%d (morfizm_sınıfı=%s, lif_boyu=%d)"
                     % (self.mevcut_mertebe, str(cikis["morfizm_sinifi"]),
                        int(lift.size)))
            lif_vektoru = lift
        else:
            sebep = ("ENGEL_DÜŞÜK" if alt_engel <= 0.15
                    else (cikis["sebep"] if not tasindi else "TAVANDA"))
            hukum = "MERTEBE_SABİT_LİFSİZ_n%d (%s)" % (self.mevcut_mertebe, sebep)
            lif_vektoru = None
        return self.mevcut_mertebe, hukum, lif_vektoru


def cok_mertebeli_girisim_karari(kule: DereceliMertebeKulesi, n_boyut: int,
                                  yasak: Set[int]) -> Tuple[int, np.ndarray, Dict[str, float]]:
    kulli_psi = kule.eszamanli_kullî_vektor(taban_boyut=n_boyut)

    girisim_olasiliklari = np.abs(kulli_psi) ** 2
    girisim_olasiliklari /= (np.sum(girisim_olasiliklari) + 1e-12)

    for y_idx in yasak:
        if y_idx < n_boyut:
            girisim_olasiliklari[y_idx] = -1e9

    secilen_hedef = int(np.argmax(girisim_olasiliklari))

    katilim_paylari = {}
    for n in range(1, kule.maks_mertebe + 1):
        katilim_paylari["mertebe_%d_payi" % n] = float(kule.mertebe_agirliklari[n - 1])

    return secilen_hedef, girisim_olasiliklari, katilim_paylari


def hakiki_qudit_yogunluk_matrisi(psi_durum: np.ndarray, n_boyut: int) -> Tuple[np.ndarray, float]:
    psi_taban = psi_durum[:n_boyut].copy().astype(complex)
    norm = float(np.linalg.norm(psi_taban))
    if norm > 1e-12:
        psi_taban /= norm
    else:
        psi_taban = np.ones(n_boyut, dtype=complex) / np.sqrt(float(n_boyut))

    rho_saf = np.outer(psi_taban, psi_taban.conj())

    rho_karisik = 0.95 * rho_saf + 0.05 * (np.eye(n_boyut, dtype=complex) / float(n_boyut))
    iz = float(np.real(np.trace(rho_karisik)))
    rho_karisik /= (iz + 1e-12)

    saflik = float(np.real(np.trace(rho_karisik @ rho_karisik)))
    return rho_karisik, saflik


def tekil_karar_hunisi(baglam_son: int, aday_hedef: int, kule_hedefi: int,
                       girisim_olasiliklari: np.ndarray, t4_kan_sonuc: Dict[str, Any],
                       j4_denetleyici: J4GeriYolDenetleyicisi, psi_durum: np.ndarray,
                       kod_uzayi_maskesi: np.ndarray, vahime: VahimeIslemcisi,
                       akile: AkileKatmani, baise_motoru: KuvveiBaiseVeMotorlar,
                       kalp: ManeviKalpKatmani, P: np.ndarray,
                       tayf_bilgisi: Dict[str, Any], Asim: np.ndarray) -> Dict[str, Any]:
    n = P.shape[0]

    kan_basamak = t4_kan_sonuc["secilen_basamak"]
    birlesik_tercih = girisim_olasiliklari.copy()
    if kan_basamak < n:
        birlesik_tercih[kan_basamak] += 0.5 * t4_kan_sonuc["olcum_guveni"]
    birlesik_tercih[aday_hedef] += 0.3
    birlesik_tercih[kule_hedefi] += 0.4
    ilk_oneri = int(np.argmax(birlesik_tercih))

    n_normu = j4_denetleyici.kisit_projeksiyonu_olc(ilk_oneri, psi_durum, kod_uzayi_maskesi)
    j4_hedef, geri_alindi, _ = j4_denetleyici.geri_yol_denetle(ilk_oneri, n_normu, birlesik_tercih)

    vahime_raporu = vahime.mana_suz(son_token=baglam_son, hedef_aday=j4_hedef,
                                    P=P, Kan_rez=tayf_bilgisi["Kan_rezidusu"], Asim=Asim)

    ameli_rapor = akile.ameli_akil_tart(hedef_id=j4_hedef, vahime_raporu=vahime_raporu,
                                        hedef_beklentisi=float(birlesik_tercih[j4_hedef]))

    eylem_raporu = baise_motoru.sevk_ve_icra(aday_hedef=j4_hedef, vahime_raporu=vahime_raporu,
                                             ameli_akil_raporu=ameli_rapor, P_satiri=P[baglam_son])
    icra_adayi = eylem_raporu["nihai_icra_tokeni"]

    itminan_derecesi = kalp.itminan_olc(psi_durum)
    vicdan_raporu = kalp.vicdani_murakabe(eylem_raporu["eylem_vektoru"], itminan_derecesi)

    if vicdan_raporu["kalbi_fetva"]:
        kesin_hedef = icra_adayi
        nihai_durum = "AMELÎ_VE_KALBÎ_MUTABAKAT"
    else:
        kesin_hedef = baglam_son
        nihai_durum = "VİCDANÎ_FREN_SÜKÛT"

    return {"kesin_nihai_hedef": kesin_hedef, "nihai_durum": nihai_durum,
            "j4_geri_alindi": geri_alindi, "vahime_tehdit": vahime_raporu["tehdit"],
            "ameli_irade_payi": ameli_rapor["irade_katsayisi"],
            "sevk_kaynagi": eylem_raporu["sevk_kaynagi"],
            "kalp_fetvasi": vicdan_raporu["kalbi_fetva"], "itminan_derecesi": itminan_derecesi}


def analitik_newton_adimi(V_eski: float, V_lineer_tahmin: float, V_yeni: float,
                          mevcut_yaricap: float, g_fs_izi: float,
                          hudut_keyfiyeti: float) -> float:
    temel_yaricap = hudut_keyfiyeti / (np.sqrt(max(1e-12, g_fs_izi)) + 1e-6)
    r = mevcut_yaricap if mevcut_yaricap > 1e-6 else temel_yaricap

    delta_v_gercek = V_yeni - V_eski
    delta_v_lineer = V_lineer_tahmin - V_eski

    kappa = 2.0 * (delta_v_gercek - delta_v_lineer) / (r ** 2 + 1e-12)

    if kappa > 1e-6:
        yaricap_yildiz = -delta_v_lineer / (kappa * r + 1e-12)
    else:
        yaricap_yildiz = 2.0 * r

    return float(np.clip(yaricap_yildiz, 1e-4, 1.0))


def aklet_operad_doldur(baglam: Tuple[int, ...], tayf_bilgisi: Dict[str, Any],
                        norm_korollalar: Dict[Tuple[Tuple[int, ...], int], float],
                        yasakli_hedefler: Optional[Set[int]] = None
                        ) -> Dict[str, Any]:
    P = tayf_bilgisi["P"]
    P2 = tayf_bilgisi["P2"]
    Asim = tayf_bilgisi["Asim"]
    Kan_rez = tayf_bilgisi["Kan_rezidusu"]
    n = P.shape[0]

    yasak = set(yasakli_hedefler or ())

    son_token = int(baglam[-1]) if baglam else 0
    yasak.add(son_token)

    baglam_sayimlari = np.zeros(n, dtype=float)
    for (girdi, cikti), prob in norm_korollalar.items():
        if girdi == baglam:
            baglam_sayimlari[cikti] += prob

    toplam_baglam_cikis = float(np.sum(baglam_sayimlari))
    if toplam_baglam_cikis > 1e-12:
        P_baglam = baglam_sayimlari / toplam_baglam_cikis
    else:
        P_baglam = np.zeros(n, dtype=float)

    tikaniklik = np.maximum(0.0, P2[son_token] - P_baglam)
    for y_idx in yasak:
        if y_idx < n:
            tikaniklik[y_idx] = 0.0
    toplam_tikaniklik = float(np.sum(tikaniklik))

    if toplam_tikaniklik > 1e-5:
        z = int(np.flatnonzero(tikaniklik == np.max(tikaniklik))[0])
        hedef_turu = "açık_boynuz_çıkarımı"
    else:
        birlesik_akis = 0.5 * P[son_token] + 0.5 * P_baglam
        for y_idx in yasak:
            if y_idx < n:
                birlesik_akis[y_idx] = -1.0
        sirali = np.argsort(birlesik_akis)
        z = int(sirali[-1])
        hedef_turu = "doğrudan_akış"

    dogrudan_guc = max(float(P[son_token, z]), float(P_baglam[z]))
    tikanma = float(Kan_rez[son_token, z])

    hads_orta_terim, hads_durumu, hads_kuvveti = hads_ile_orta_terim_yakala(P, son_token, z)
    if hads_durumu == "HADS_I_KUDSI_SEZGI" and hads_orta_terim not in yasak:
        X_tip = Dogal()
        oncutler_terim = [dogal_sayi(t) for t in baglam]
        agac1 = OperadAgac(X_tip, oncutler_terim, dogal_sayi(hads_orta_terim), "hads_rezonans")
        ok2 = YonluOk(X_tip, dogal_sayi(hads_orta_terim), dogal_sayi(z), "hads_sıçraması")
        ispat_sahidi = YonluTerkip(agac1, ok2)
        return {
            "hüküm": "hads_başarılı", "hedef_türü": hedef_turu, "hedef": z,
            "ara_durak": hads_orta_terim, "türetim_gücü": hads_kuvveti,
            "doğrudan_güç": dogrudan_guc, "ispat_sahidi": ispat_sahidi,
            "kohomolojik_engel": tikanma, "hads_durumu": hads_durumu,
            "hads_kuvveti": hads_kuvveti
        }

    adaylar = []
    for y in range(n):
        if y == son_token or y == z:
            continue
        girdi_y_gucu = norm_korollalar.get((baglam, y), float(P[son_token, y]))
        y_z_gucu = float(P[y, z])
        bileske_guven = girdi_y_gucu * y_z_gucu

        if girdi_y_gucu >= _ZINCIR_GECIS_ESIGI and bileske_guven > 1e-6:
            koherans_cezasi = float(Asim[son_token, y] * Asim[y, z] * tikanma)
            net_skor = bileske_guven * (1.0 - 0.5 * koherans_cezasi)
            holonomi = analitik_lie_bargmann_adimi(son_token, y, z, P, Asim)
            if holonomi["tenakuz_mu"]:
                net_skor *= 0.1
            elif not holonomi["kisirdongu_mu"]:
                net_skor *= 1.2
            adaylar.append((net_skor, y))

    if not adaylar:
        return {
            "hüküm": "tıkanma", "hedef": z, "ara_durak": None,
            "ispat_sahidi": None, "kohomolojik_engel": tikanma,
            "hads_durumu": hads_durumu, "hads_kuvveti": hads_kuvveti
        }

    adaylar.sort(key=lambda item: item[0], reverse=True)
    en_iyi_skor, y_yildiz = adaylar[0]

    X_tip = Dogal()
    oncutler_terim = [dogal_sayi(t) for t in baglam]

    agac1 = OperadAgac(X_tip, oncutler_terim, dogal_sayi(y_yildiz), "operadik_öncül")
    ok2 = YonluOk(X_tip, dogal_sayi(y_yildiz), dogal_sayi(z), "netice_çıkarım")
    ispat_sahidi = YonluTerkip(agac1, ok2)

    if en_iyi_skor > dogrudan_guc:
        norm_korollalar[(baglam, z)] = norm_korollalar.get((baglam, z), 0.0) + en_iyi_skor
        toplam_kutle = sum(norm_korollalar.values())
        for k_korolla in norm_korollalar:
            norm_korollalar[k_korolla] /= toplam_kutle

        g_fs_tahmin = float(1.0 - dogrudan_guc ** 2)
        dinamik_adim = analitik_newton_adimi(
            V_eski=dogrudan_guc,
            V_lineer_tahmin=dogrudan_guc + 0.1,
            V_yeni=en_iyi_skor,
            mevcut_yaricap=0.1,
            g_fs_izi=g_fs_tahmin,
            hudut_keyfiyeti=float(1.0 - tikanma)
        )
        P[son_token, z] = (1.0 - dinamik_adim) * P[son_token, z] + dinamik_adim * en_iyi_skor
        P[son_token] /= (P[son_token].sum() + 1e-12)

        hukum = "türetim_başarılı"
    else:
        hukum = "doğrudan_tasdik"

    return {
        "hüküm": hukum, "hedef_türü": hedef_turu, "hedef": z,
        "ara_durak": y_yildiz, "türetim_gücü": en_iyi_skor,
        "doğrudan_güç": dogrudan_guc, "ispat_sahidi": ispat_sahidi,
        "kohomolojik_engel": tikanma, "hads_durumu": hads_durumu,
        "hads_kuvveti": hads_kuvveti
    }


def ispat_sahidini_dogrula(ispat_sahidi: Optional[Terim], baglam: Tuple[int, ...],
                           hedef: int) -> bool:
    if ispat_sahidi is None:
        return False
    g = Baglam()
    oncutler = [dogal_sayi(t) for t in baglam]
    beklenen_tip = OperadHom(Dogal(), oncutler, dogal_sayi(hedef))
    try:
        denetle_t(ispat_sahidi, beklenen_tip, g)
        return True
    except RED_HATALARI:
        return False


def kaide_ve_imza_hesapla(a: int, b: int, P: np.ndarray, Asim: np.ndarray) -> Dict[str, Any]:
    n = P.shape[0]

    hom_a = P[:, a] / (np.linalg.norm(P[:, a]) + 1e-12)
    hom_b = P[:, b] / (np.linalg.norm(P[:, b]) + 1e-12)
    temas_noktalari = hom_a * hom_b
    tip_temas = float(np.sum(temas_noktalari))
    tip_hudut = float(1.0 - (np.dot(hom_a, hom_b) ** 2))

    ortanca_temas = (float(np.median(temas_noktalari[temas_noktalari > 0]))
                     if np.any(temas_noktalari > 0) else 0.0)
    dokunan = [k for k in range(n) if temas_noktalari[k] > ortanca_temas]

    if dokunan:
        holonomiler = [np.exp(1j * np.pi * (Asim[a, b] + Asim[b, k] - Asim[k, a]))
                       for k in dokunan]
        kat_korunum = float(np.abs(np.mean(holonomiler)))
        arg_holonomiler = [abs(np.angle(h)) for h in holonomiler]
        med_arg = float(np.median(arg_holonomiler))
        cekirdek_orani = float(sum(1 for ag in arg_holonomiler if ag <= med_arg)
                               / len(dokunan))
    else:
        kat_korunum = 1.0
        cekirdek_orani = 1.0

    ortusme = float(np.clip(np.sqrt(P[a, b] * P[b, a]), 0.0, 1.0))
    aci_ab = float(np.arccos(ortusme))
    uzay_casimir = float(np.cos(aci_ab) ** 2)
    uzay_donusum = float(1.0 - uzay_casimir)

    kaide_vektoru = np.array([tip_hudut, tip_temas, kat_korunum, cekirdek_orani,
                              uzay_donusum, uzay_casimir], dtype=float)

    olcek = float(np.median(np.abs(kaide_vektoru - np.median(kaide_vektoru)))) + 1e-6
    imza = tuple(np.round(kaide_vektoru / olcek).astype(int).tolist())

    return {"kaide_vektoru": kaide_vektoru, "imza": imza, "olcek": olcek}


def vecih_hukmu_tayin_et(vecih_ortusmeleri: Sequence[float]) -> Dict[str, Any]:
    if not vecih_ortusmeleri:
        return {"hüküm": "TASDİK", "ihtilaf": 0.0, "ittifak": 1.0}

    dizi = np.array(vecih_ortusmeleri, dtype=float)
    azam_ort = float(np.max(dizi))
    asg_ort = float(np.min(dizi))

    ihtilaf = float(azam_ort - asg_ort)
    ittifak = float(1.0 - ihtilaf)

    if ihtilaf > ittifak:
        hukum = "TENAKUZ"
    elif ittifak > ihtilaf and asg_ort >= ittifak:
        hukum = "KISIRDÖNGÜ"
    else:
        hukum = "TASDİK"

    return {"hüküm": hukum, "ihtilaf": ihtilaf, "ittifak": ittifak,
            "asgari_ortusme": asg_ort}


def sadakat_devresi_kos(psi: np.ndarray, kod_uzayi_maskesi: np.ndarray) -> Dict[str, Any]:
    psi_calisma = psi.copy()
    guc = np.abs(psi_calisma) ** 2

    mantiksiz_maske = (kod_uzayi_maskesi < 0.5) | (~np.isfinite(psi_calisma))
    kod_ici_guc = guc[~mantiksiz_maske]

    if len(kod_ici_guc) > 0:
        ortanca_guc = float(np.median(kod_ici_guc))
        mumkun_maske = (~mantiksiz_maske) & (guc >= ortanca_guc)
        mecul_maske = (~mantiksiz_maske) & (guc > 0.0) & (guc < ortanca_guc)
    else:
        mumkun_maske = np.zeros_like(mantiksiz_maske)
        mecul_maske = np.zeros_like(mantiksiz_maske)

    imha_sayisi = int(np.sum(mantiksiz_maske & (guc > 0.0)))
    psi_calisma[mantiksiz_maske] = 0.0

    yeni_norm = float(np.linalg.norm(psi_calisma))
    psi_suzulen = psi_calisma / yeni_norm if yeni_norm > 1e-12 else psi_calisma

    mecul_sayisi = int(np.sum(mecul_maske))
    mumkun_sayisi = int(np.sum(mumkun_maske))

    fazla_eleme_uyarisi = bool(mecul_sayisi == 0 and mumkun_sayisi > 0)

    return {"psi_suzulen": psi_suzulen, "imha": imha_sayisi, "meçhul": mecul_sayisi,
            "mumkun": mumkun_sayisi, "fazla_eleme_uyarisi": fazla_eleme_uyarisi}


def intac_funktor_tersi(psi: np.ndarray, funktor_agirliklari: np.ndarray) -> np.ndarray:
    F_eslenik = np.conj(funktor_agirliklari)
    d = min(len(psi), len(F_eslenik))
    psi_intac = psi.astype(complex).copy()
    psi_intac[:d] *= F_eslenik[:d]

    norm = float(np.linalg.norm(psi_intac))
    return (psi_intac / norm) if norm > 1e-12 else psi_intac


def kuantum_yogunluk_ve_uhlmann(P: np.ndarray, hedef_durum: np.ndarray) -> Dict[str, Any]:
    PPT = P @ P.T
    iz = float(np.trace(PPT)) + 1e-12
    rho_yogunluk = PPT / iz

    h = hedef_durum / (np.linalg.norm(hedef_durum) + 1e-12)

    uhlmann_sadakati = float(np.real(h.T @ (rho_yogunluk @ h)))
    hata_uzay_capasi = float(1.0 - uhlmann_sadakati)

    return {
        "rho_yogunluk": rho_yogunluk,
        "uhlmann_sadakati": uhlmann_sadakati,
        "hata_uzay_capasi": hata_uzay_capasi
    }


def kuantum_monogami_ve_tenakuz_kefesi(rho_yogunluk: np.ndarray, Asim: np.ndarray,
                                       son_token: int, hedef: int) -> Tuple[float, float]:
    n = rho_yogunluk.shape[0]
    c_idx = (hedef + 1) % n

    d_A, d_B = 2, 2
    if n >= d_A * d_B:
        rho_AB_blok = rho_yogunluk[:d_A * d_B, :d_A * d_B]
        iz_AB = np.trace(rho_AB_blok)
        if abs(iz_AB) > 1e-12:
            rho_AB_blok = rho_AB_blok / iz_AB

        S_A, rho_A = kismi_iz_ve_dolaniklik_entropisi(rho_AB_blok, d_A, d_B)
        S_B, rho_B = kismi_iz_ve_dolaniklik_entropisi(rho_AB_blok.T, d_B, d_A)

        ozdegerler_AB = np.real(np.linalg.eigvalsh(rho_AB_blok))
        ozdegerler_AB = ozdegerler_AB[ozdegerler_AB > 1e-12]
        S_AB = float(-np.sum(ozdegerler_AB * np.log2(ozdegerler_AB))) if len(ozdegerler_AB) else 0.0

        I_AB = float(np.maximum(0.0, S_A + S_B - S_AB))

        I_AC = float(I_AB * abs(rho_yogunluk[son_token, c_idx]))
        I_ABC_sinir = float(S_A + 1e-6)

        hata_monogami = float(np.maximum(0.0, (I_AB + I_AC) - I_ABC_sinir))
    else:
        hata_monogami = 0.0

    faz = np.pi * (Asim[son_token, hedef] + Asim[hedef, c_idx] - Asim[c_idx, son_token])
    U_cevrim = np.array([[np.cos(faz), -np.sin(faz)],
                         [np.sin(faz),  np.cos(faz)]], dtype=float)
    iz_terimi = float(np.trace(np.eye(2) + U_cevrim))
    p_a = float(np.clip(rho_yogunluk[son_token, son_token], 1e-12, 1.0))
    dislama_entropisi = float(-p_a * np.log(p_a))

    hata_tenakuz = float(-np.log((iz_terimi + 1e-6) / (4.0 + 1e-6)) * dislama_entropisi)
    hata_tenakuz = float(np.maximum(0.0, hata_tenakuz))

    return hata_monogami, hata_tenakuz


def cok_boyutlu_kefeler_olc(P: np.ndarray, rho_yogunluk: np.ndarray,
                            uhlmann_sadakati: float, son_token: int,
                            hedef: int, baglam: Tuple[int, ...],
                            Asim: Optional[np.ndarray] = None) -> np.ndarray:
    n = P.shape[0]

    hata_uzay = float(np.clip(1.0 - uhlmann_sadakati, 0.0, 1.0))

    P2 = P @ P
    hata_kategori = float(np.mean((P[son_token] - P2[son_token]) ** 2))

    mesafeler = np.abs(np.arange(n) - hedef)
    kuantum_ortusmeleri = rho_yogunluk[son_token, :]
    sira_mesafe = np.argsort(mesafeler)
    sira_ortusme = np.argsort(-kuantum_ortusmeleri)
    hata_lif = float(np.mean((sira_mesafe - sira_ortusme) ** 2) / (n ** 2 + 1e-12))

    hedef_olasilik = float(rho_yogunluk[hedef, hedef])
    hata_nokta = float(-np.log(np.clip(hedef_olasilik, 1e-6, 1.0)))

    if Asim is None:
        Asim = asimetri_guncelle(P)
    hata_monogami, hata_tenakuz = kuantum_monogami_ve_tenakuz_kefesi(
        rho_yogunluk, Asim, son_token, hedef)

    return np.array([hata_uzay, hata_kategori, hata_lif, hata_nokta,
                     hata_monogami, hata_tenakuz], dtype=float)


def kan_chebyshev_intac(u: float, derece: int = 4) -> Tuple[np.ndarray, np.ndarray]:
    u_kirpik = float(np.clip(u, -0.9999, 0.9999))
    theta = np.arccos(u_kirpik)
    sin_theta = np.sin(theta)

    T = np.array([np.cos(j * theta) for j in range(derece)], dtype=float)
    U = np.array([np.sin((j + 1) * theta) / sin_theta for j in range(derece)], dtype=float)

    return T, U


def kan_genlik_hesapla(u: float, C_katsayilari: np.ndarray, S_katsayilari: np.ndarray,
                       enerji: float, cartan_acisi: float) -> complex:
    T, U = kan_chebyshev_intac(u, derece=len(C_katsayilari))

    reel_kisim = float(np.dot(C_katsayilari, T))
    sanal_kisim = float(np.dot(S_katsayilari, U))

    faz = sanal_kisim + cartan_acisi
    genlik = np.exp(-enerji + 1j * faz) * (reel_kisim + 1j * sanal_kisim)
    return complex(genlik)


def d0_gecit_nedensellik_teftisi(baglam_dizisi: Sequence[int],
                                 baglam_hedef_ciftleri: List[Tuple[Tuple[int, ...], int]],
                                 orijinal_pozisyonlar: Optional[List[int]] = None
                                 ) -> Dict[str, Any]:
    if orijinal_pozisyonlar is None:
        orijinal_pozisyonlar = list(range(len(baglam_hedef_ciftleri)))

    zaman_cevrimi_var = False
    for i in range(1, len(orijinal_pozisyonlar)):
        if orijinal_pozisyonlar[i] <= orijinal_pozisyonlar[i - 1]:
            zaman_cevrimi_var = True
            break

    trivial_kopya_sayisi = sum(
        1 for b_tuple, h in baglam_hedef_ciftleri
        if len(set(b_tuple)) == 1 and b_tuple[0] == h)
    trivial_kopya_orani = trivial_kopya_sayisi / max(1, len(baglam_hedef_ciftleri))
    kelam_ayrismasi_tam = bool(trivial_kopya_orani < 0.9)

    gecit_onayi = bool((not zaman_cevrimi_var) and kelam_ayrismasi_tam)

    return {"gecit_onayi": gecit_onayi, "zaman_cevrimi_var": zaman_cevrimi_var,
            "kelam_ayrismasi_tam": kelam_ayrismasi_tam,
            "trivial_kopya_orani": trivial_kopya_orani}


def d8_hudut_temizligi_denetle(psi: np.ndarray, kod_uzayi_maskesi: np.ndarray,
                               uretilmis_tokenler: Sequence[int], sozluk_boyutu: int,
                               tenakuz_var_mi: bool, kisirdongu_var_mi: bool
                               ) -> Dict[str, Any]:
    n = int(sozluk_boyutu)
    guc = np.abs(psi) ** 2
    toplam_guc = float(np.sum(guc)) + 1e-12

    dis_guc = float(np.sum(guc[kod_uzayi_maskesi < 0.5]))
    parite_tasmasi = float(np.clip(dis_guc / toplam_guc, 0.0, 1.0))

    gecersiz_tokenler = sum(1 for t in uretilmis_tokenler if t < 0 or t >= n)
    belirtec_tasmasi = float(gecersiz_tokenler / max(1, len(uretilmis_tokenler)))

    mantiksizlik = parite_tasmasi + belirtec_tasmasi
    nispet_mantik = float((1.0 - parite_tasmasi) * (1.0 - belirtec_tasmasi))

    hudut_temiz = bool((not tenakuz_var_mi) and (not kisirdongu_var_mi)
                       and (mantiksizlik < 1e-4))

    return {"parite_tasmasi": parite_tasmasi, "belirtec_tasmasi": belirtec_tasmasi,
            "mantiksizlik": mantiksizlik, "nispet_mantik": nispet_mantik,
            "hudut_temiz": hudut_temiz}


def s1_entropi_gradyani_sinir_bul(w: Sequence[int], pencere_boyu: int = 3) -> Tuple[int, int]:
    w_arr = np.asarray(w)
    if len(w_arr) <= pencere_boyu:
        return 0, len(w_arr)

    yerel_entropiler = []
    for i in range(len(w_arr) - pencere_boyu + 1):
        kesit = w_arr[i:i + pencere_boyu]
        _, sayimlar = np.unique(kesit, return_counts=True)
        p = sayimlar / float(len(kesit))
        yerel_entropiler.append(-float(np.sum(p * np.log(p + 1e-12))))

    entropi_dizisi = np.array(yerel_entropiler)
    gradyan = np.abs(np.gradient(entropi_dizisi))

    zirve_idx = int(np.argmax(gradyan))
    return zirve_idx, min(len(w_arr), zirve_idx + pencere_boyu)


def s0_s2_ozerk_gaye_turet(dahili_tenakuzlar: Dict[str, float],
                            dahili_entropiler: Dict[str, float],
                            lambda_reg: float = 0.3) -> str:
    if not dahili_tenakuzlar:
        return "VAKUM_DURUMU"

    gaye_skorlari = {}
    for gaye, e_tenakuz in dahili_tenakuzlar.items():
        entropi = dahili_entropiler.get(gaye, 1.0)
        gaye_skorlari[gaye] = e_tenakuz - lambda_reg * entropi

    return max(gaye_skorlari.items(), key=lambda x: x[1])[0]


_S0_IC_HAL_HAVUZU: Dict[int, Dict[str, Dict[Any, Any]]] = {}


def _s0_havuz_al(n: int) -> Dict[str, Dict[Any, Any]]:
    return _S0_IC_HAL_HAVUZU.setdefault(
        int(n), {"tenakuzlar": {}, "entropiler": {}, "son_norm_korollalar": {}})


_KALICI_HAFIZA_HAVUZU: Dict[str, Any] = {"cartan_kokleri": set(), "balyalar": [], "kayit_arsivi": []}


def s2_dort_sual_teftisi(tikanma_engeli: float,
                         kaide_raporu: Dict[str, Any],
                         s1_odak_kesiti: Tuple[int, ...],
                         geri_yol_var_mi: bool,
                         kulli_ispat_dogrulandi: bool = True) -> Dict[str, Any]:
    mesele_var_mi = bool(tikanma_engeli > 0.04 or not kulli_ispat_dogrulandi)
    kaide_belirli = bool(len(kaide_raporu.get("imza", ())) == 6)
    geri_yol_mumkun = bool(geri_yol_var_mi)
    metin_odakli = bool(len(s1_odak_kesiti) >= 1)

    dort_sual_tam = bool(mesele_var_mi and kaide_belirli and geri_yol_mumkun and metin_odakli)
    rota = "S3_UZAY_AC" if mesele_var_mi else "S6_INTAC_ATLA"

    return {
        "dort_sual_tam_mi": dort_sual_tam,
        "mesele_var_mi": mesele_var_mi,
        "rota": rota,
        "sual_raporu": {
            "mesele_var": mesele_var_mi,
            "kaide_belirli": kaide_belirli,
            "geri_yol_mumkun": geri_yol_mumkun,
            "metin_odakli": metin_odakli
        }
    }


class CokYaprakliRiemannOrtusu:
    __slots__ = ("yapraklar", "monodromi_matrisi")

    def __init__(self, yaprak_isimleri: Sequence[str]) -> None:
        self.yapraklar = list(yaprak_isimleri)
        self.monodromi_matrisi = np.eye(len(self.yapraklar), dtype=int)

    def monodromi_dondur(self, holonomi_fazi: float) -> Tuple[str, np.ndarray]:
        M = len(self.yapraklar)
        if M <= 1:
            return self.yapraklar[0], self.monodromi_matrisi

        kayma = int(np.round(abs(holonomi_fazi) / (np.pi / 2.0))) % M

        sigma = np.zeros((M, M), dtype=int)
        for i in range(M):
            sigma[(i + kayma) % M, i] = 1

        self.monodromi_matrisi = sigma @ self.monodromi_matrisi
        yeni_yaprak_idx = int(np.argmax(self.monodromi_matrisi[:, 0]))
        yeni_yaprak = self.yapraklar[yeni_yaprak_idx]

        return yeni_yaprak, self.monodromi_matrisi


class ToposIcselNNO:
    __slots__ = ("kategori", "sifir_nesne_id", "ardil_ok_id")

    def __init__(self, kat: Turetilen1Kategori) -> None:
        self.kategori = kat
        self.sifir_nesne_id = kat.nesneler[0] if kat.nesneler else 0
        self.ardil_ok_id = kat.ok_siniflari.get((self.sifir_nesne_id, self.sifir_nesne_id), 0)

    def ozyineleme_adimi_hesapla(self, baslangic_degeri: float,
                                 adim_fonksiyonu: Callable[[float], float],
                                 n_adim: int) -> float:
        val = float(baslangic_degeri)
        for _ in range(max(0, int(n_adim))):
            val = float(adim_fonksiyonu(val))
        return val


def zigzag_bitisiklik_sapmasi_olc(P: np.ndarray,
                                  f_gecis_gucu: float) -> Dict[str, Any]:
    F_mat = f_gecis_gucu * P
    G_mat = f_gecis_gucu * P.T

    eta = G_mat @ F_mat
    epsilon = F_mat @ G_mat

    sol_ucgen = (epsilon @ F_mat) @ (F_mat @ eta)
    hata_1 = float(np.linalg.norm(sol_ucgen - F_mat))

    sag_ucgen = (G_mat @ epsilon) @ (eta @ G_mat)
    hata_2 = float(np.linalg.norm(sag_ucgen - G_mat))

    toplam_zigzag_sapmasi = float(hata_1 + hata_2)
    bitisiklik_mesru_mu = bool(toplam_zigzag_sapmasi < 0.25)

    return {
        "zigzag_sapmasi": toplam_zigzag_sapmasi,
        "bitisiklik_mesru_mu": bitisiklik_mesru_mu
    }


def geodezik_bukulme_ve_yaricap_duzelt(temel_yaricap: float,
                                       yon_simdiki: np.ndarray,
                                       yon_onceki: Optional[np.ndarray],
                                       artik_hata: float) -> Tuple[float, float, float]:
    d = len(yon_simdiki)
    v_sim = yon_simdiki / (np.linalg.norm(yon_simdiki) + 1e-12)

    if yon_onceki is not None and len(yon_onceki) == d:
        v_on = yon_onceki / (np.linalg.norm(yon_onceki) + 1e-12)
        bukulme_enerjisi = float(np.sum((v_sim - v_on) ** 2))
    else:
        bukulme_enerjisi = 0.0

    artik_kare = float(artik_hata ** 2)
    egrilik = float(bukulme_enerjisi / (bukulme_enerjisi + artik_kare + 1e-12))

    sonumlenmis_yaricap = float(temel_yaricap / (1.0 + egrilik))

    return sonumlenmis_yaricap, egrilik, bukulme_enerjisi


def j1_j2_j3_faz_kaydirici_ve_norm(born_olasiliklari: np.ndarray,
                                   psi: np.ndarray,
                                   secilen_jeton: int) -> Dict[str, Any]:
    n = len(born_olasiliklari)
    d = min(len(psi), n)

    theta_fazlar = np.pi * born_olasiliklari[:d]

    U_faz = np.diag(np.exp(1j * theta_fazlar))

    P_jeton = np.zeros((d, d), dtype=complex)
    if secilen_jeton < d:
        P_jeton[secilen_jeton, secilen_jeton] = 1.0

    psi_fazli = U_faz @ psi[:d]
    psi_jeton = P_jeton @ psi_fazli
    j3_normu = float(np.sum(np.abs(psi_jeton) ** 2))

    return {
        "j1_theta_fazlar": theta_fazlar,
        "j2_psi_fazli": psi_fazli,
        "j3_jeton_normu": j3_normu,
        "faz_kaymasi_kararli_mi": bool(j3_normu > 1e-5)
    }


def leray_spektral_dizisi_hesapla(cech_h1: float,
                                  hodge_yırtık: float,
                                  asansor_kati: int) -> Dict[str, Any]:
    e2_10 = float(cech_h1)
    e2_01 = float(hodge_yırtık / float(max(1, asansor_kati)))
    d2_diferansiyeli = float(abs(e2_10 - e2_01) * 0.5)
    kulli_h1_engeli = float(np.sqrt(e2_10 ** 2 + e2_01 ** 2) + d2_diferansiyeli)

    return {
        "E2_taban_cech": e2_10,
        "E2_lif_hodge": e2_01,
        "d2_diferansiyeli": d2_diferansiyeli,
        "kulli_leray_engeli": kulli_h1_engeli,
        "spektral_dizi_kapandi_mi": bool(d2_diferansiyeli < 0.05)
    }


def tip_tensoru_blok_boyutlari(kat: "Turetilen1Kategori",
                               taban_boyut: int) -> Dict[int, Tuple[int, int]]:
    nesneler = kat.nesneler
    if not nesneler or taban_boyut <= 0:
        return {}
    agirlik = {x: max(1, sum(1 for (a, b) in kat.ok_siniflari if a == x or b == x))
              for x in nesneler}
    toplam = float(sum(agirlik.values()))
    bloklar: Dict[int, Tuple[int, int]] = {}
    bas = 0
    for i, x in enumerate(nesneler):
        if i == len(nesneler) - 1:
            son = taban_boyut
        else:
            pay = agirlik[x] / toplam
            son = min(taban_boyut, bas + max(1, int(round(pay * taban_boyut))))
        bloklar[x] = (bas, son)
        bas = son
        if bas >= taban_boyut:
            break
    return bloklar


def tip_tensoru_perelomov_dondur(lif0: np.ndarray, teta: np.ndarray) -> np.ndarray:
    from kuantum.qudit import agirlik
    d = int(lif0.size)
    if d < 2 or teta.size == 0:
        return lif0
    w = agirlik(d, teta)
    U = np.exp(-1j * np.pi * w)
    donmus = lif0 * U
    nrm = float(np.linalg.norm(donmus))
    return (donmus / nrm) if nrm > 1e-300 else donmus


def qudit_tip_tensoru_kur(kat: "Turetilen1Kategori", psi: np.ndarray,
                          P: Optional[np.ndarray] = None) -> Dict[str, Any]:
    d = int(len(psi))
    bloklar = tip_tensoru_blok_boyutlari(kat, d)
    lifler: Dict[int, np.ndarray] = {}
    for x, (i, j) in bloklar.items():
        alt = np.asarray(psi[i:j], complex)
        nrm = float(np.linalg.norm(alt))
        alt = (alt / nrm) if nrm > 1e-300 else alt
        if P is not None and alt.size >= 2:
            teta = np.asarray(P[x], float)
            teta = teta[teta > 0.0][:max(1, min(8, alt.size - 1))]
            alt = tip_tensoru_perelomov_dondur(alt, teta)
        lifler[x] = alt
    T, u_boyu, x_boyu = tip_tensoru_3eksen_insa(lifler, list(bloklar))
    return {"bloklar": bloklar, "liflar": lifler,
           "nesneler": list(bloklar), "taban_boyut": d,
           "T": T, "u_boyu": u_boyu, "x_boyu": x_boyu}


def _en_yakin_carpanlar(d: int, en_az: int = 20) -> Tuple[int, int]:
    if d <= 0:
        return (1, 0)
    for u in range(int(np.sqrt(d)), 0, -1):
        if d % u == 0 and (d // u) >= en_az:
            return (u, d // u)
    return (1, d)


def tip_tensoru_3eksen_insa(lifler: Dict[int, np.ndarray], nesneler: List[int],
                            en_az_boyut: int = 20
                            ) -> Tuple[np.ndarray, int, int]:
    if not nesneler:
        return np.zeros((0, 0, 0), complex), 0, 0
    boylar = [int(lifler[x].size) for x in nesneler]
    d_ortak = max(1, min(boylar))
    u_boyu, x_boyu = _en_yakin_carpanlar(d_ortak, en_az_boyut)
    T = np.zeros((len(nesneler), u_boyu, x_boyu), complex)
    for c, nesne in enumerate(nesneler):
        veri = np.asarray(lifler[nesne], complex)[:u_boyu * x_boyu]
        T[c] = veri.reshape(u_boyu, x_boyu)
    return T, u_boyu, x_boyu


def tip_tensoru_morfizm_kanali(tensor: Dict[str, Any], a: int, b: int
                               ) -> Optional[np.ndarray]:
    if a not in tensor["liflar"] or b not in tensor["liflar"]:
        return None
    la = np.asarray(tensor["liflar"][a], complex)
    lb = np.asarray(tensor["liflar"][b], complex)
    if (la.size == 0 or lb.size == 0
            or float(np.linalg.norm(la)) <= 1e-300
            or float(np.linalg.norm(lb)) <= 1e-300):
        return None
    if la.size == lb.size and la.size >= 2:
        from nefs.kulli_mizan import givens
        return givens(la, lb)
    return np.outer(lb, la.conj())


def tip_tensoru_asagi_in(tensor: Dict[str, Any], nesne: int,
                         kat: "Turetilen1Kategori") -> Dict[str, Any]:
    if nesne not in tensor["bloklar"]:
        return {"bulundu": False}
    hom = ccc_dahili_hom_uzayi_turet(kat)
    komsu_hom = {cift: h for cift, h in hom.items()
                if cift[0] == nesne or cift[1] == nesne}
    return {"bulundu": True, "lif": tensor["liflar"][nesne],
           "blok": tensor["bloklar"][nesne], "hom_kurallari": komsu_hom}


def tip_tensoru_yukari_cik(tensor: Dict[str, Any], kat: "Turetilen1Kategori",
                           a: int, b: int) -> Dict[str, Any]:
    if a not in tensor["liflar"] or b not in tensor["liflar"]:
        return {"tasindi": False, "sebep": "NESNE_YOK",
               "kartezyen_lift_vektoru": None, "morfizm_sinifi": None}
    if a != b and (a, b) not in kat.ok_siniflari:
        return {"tasindi": False, "sebep": "MORFIZM_YOK",
               "kartezyen_lift_vektoru": None, "morfizm_sinifi": None}
    M = tip_tensoru_morfizm_kanali(tensor, a, b)
    if M is None:
        return {"tasindi": False, "sebep": "KANAL_YOK",
               "kartezyen_lift_vektoru": None, "morfizm_sinifi": None}
    la = np.asarray(tensor["liflar"][a], complex)
    tasinan = M @ la
    nrm = float(np.linalg.norm(tasinan))
    tasinan = (tasinan / nrm) if nrm > 1e-300 else tasinan
    sinif = kat.ok_siniflari.get((a, b), kat.ok_siniflari.get((a, a)))
    return {"tasindi": True, "sebep": "OK", "kartezyen_lift_vektoru": tasinan,
           "morfizm_sinifi": (int(sinif) if sinif is not None else None)}


def silsile_teshisi_kos(w: Sequence[int], n: int, K_max: int = 4,
                        azami_adim: int = 3) -> Dict[str, Any]:
    from main.egitim import (
        d9_hafiza_yeniden_tertip_ve_alaka, d7_hamiltonyen_nispetleri,
        d8a_mecz_ve_wkb_tunelleme, d10_durma_ve_sukut_yokla, SenetKaydi,
        d8a_senet_ve_egim_mutabakati, d6_cartan_kapi_evrimi, KategorikBalya,
        d9_kume_kapanisi_ve_balyalama, d8a_senet_sadakati_dogrula,
        d4_kapi_tam_tasnif_mercii, d9_dugum_coz_bag_gevset,
        d2_enformasyon_ve_hendese_metrikleri)
    s0_vakum_tetiklendi = False
    s0_secilen_gaye: Optional[int] = None

    if len(w) == 0:
        havuz = _s0_havuz_al(n)
        secilen_gaye = s0_s2_ozerk_gaye_turet(havuz["tenakuzlar"], havuz["entropiler"])
        if secilen_gaye == "VAKUM_DURUMU":
            return {"hata": "S0 VAKUM: İç hâl havuzu boş, özerk gaye üretilemedi",
                    "detay": {"tenakuzlar": {}, "entropiler": {}}}
        s0_vakum_tetiklendi = True
        s0_secilen_gaye = int(secilen_gaye)
        w = s0_gercek_baglam_cagir(s0_secilen_gaye, havuz["son_norm_korollalar"], n)
        if len(w) < 2 or any(t >= n or t < 0 for t in w):
            w = [s0_secilen_gaye, (s0_secilen_gaye + 1) % max(2, n)]

    gecit_raporu = d0_gecit_nedensellik_teftisi(
        w, [((w[i],), w[i + 1]) for i in range(len(w) - 1)])
    if not gecit_raporu["gecit_onayi"]:
        return {"hata": "D0 GEÇİT İHLALİ: Zaman çevrimi veya ezber sızıntısı saptandı",
                "detay": gecit_raporu}

    bas_idx, son_idx = s1_entropi_gradyani_sinir_bul(w, pencere_boyu=min(4, len(w)))
    odak_kesiti = tuple(w[bas_idx:son_idx])

    w_dizi = np.asarray(w)
    if w_dizi.ndim == 2:
        izgara_sekli = w_dizi.shape
        P, Asim = iki_cins_geometri_cikar(w_dizi, n, izgara_sekli=izgara_sekli)
        w = list(w_dizi.reshape(-1))
        _, _, norm_korollalar = veriden_geometri_cikar(w, n, K_max)
    else:
        izgara_sekli = None
        P, Asim, norm_korollalar = veriden_geometri_cikar(w, n, K_max)

    w_arr = list(w)
    k_baglam = min(K_max - 1, len(w_arr) - 1)
    varsayilan_kuyruk = tuple(w_arr[-k_baglam:]) if k_baglam > 0 else (w_arr[-1],)

    if len(odak_kesiti) >= 2 and k_baglam > 0:
        orijinal_baglam = odak_kesiti[-k_baglam:]
    else:
        orijinal_baglam = varsayilan_kuyruk
    baglam = orijinal_baglam

    muhakemeler: List[Dict[str, Any]] = []
    cozulen_hedefler: Set[int] = set()
    tikanma_gecmisi: List[float] = []
    azami_guvenlik_tavani = max(int(azami_adim), 8)

    mertebe_kulesi = DereceliMertebeKulesi(maks_mertebe=4)
    asansor = IkiYonluMertebeAsansoru(tavan_mertebe=4)

    adim = 0
    while True:
        Asim = asimetri_guncelle(P)
        tayf_bilgisi = topos_tayfi_hodge_ile_hesapla(P, Asim, norm_korollalar, baglam)

        anlik_hodge_engeli = float(tayf_bilgisi["enerjiler"]["tıkanma"])
        kat_seviyesi, tirmanis_notu = asansor.yukari_tirman(alt_engel=anlik_hodge_engeli)

        adim_muhakeme = aklet_operad_doldur(baglam, tayf_bilgisi, norm_korollalar,
                                            yasakli_hedefler=cozulen_hedefler)
        adim_muhakeme["asansor_kati"] = kat_seviyesi
        adim_muhakeme["asansor_notu"] = tirmanis_notu

        sahit_gecerli = ispat_sahidini_dogrula(adim_muhakeme["ispat_sahidi"], baglam,
                                               adim_muhakeme["hedef"])
        adim_muhakeme["şahit_doğrulandı"] = sahit_gecerli
        adim_muhakeme["yerel_hodge"] = yerel_baglamsal_hodge(baglam, P, norm_korollalar)
        muhakemeler.append(adim_muhakeme)
        tikanma_gecmisi.append(float(adim_muhakeme["kohomolojik_engel"]))

        cozulen_hedefler.add(adim_muhakeme["hedef"])

        if sahit_gecerli and anlik_hodge_engeli < 0.05:
            kat_seviyesi, inis_notu = asansor.asagi_in_intac(ust_koherans_tam_mi=True)
            adim_muhakeme["asansor_kati"] = kat_seviyesi
            adim_muhakeme["asansor_notu"] = inis_notu

        kefeler_anlik = np.array([adim_muhakeme["kohomolojik_engel"],
                                  adim_muhakeme.get("doğrudan_güç", 0.0),
                                  adim_muhakeme.get("türetim_gücü", 0.0),
                                  float(adim_muhakeme.get("hedef_türü") == "doğrudan_akış")])
        mecz_raporu = d8a_mecz_ve_wkb_tunelleme(
            kefeler_anlik, P, baglam[-1], adim_muhakeme["hedef"],
            Kan_rez=tayf_bilgisi["Kan_rezidusu"], Asim=Asim,
            hedef_beklentisi=float(adim_muhakeme.get("doğrudan_güç", 0.0)))
        adim_muhakeme["mecz_raporu"] = mecz_raporu
        if mecz_raporu["kuyuya_saplandi"]:
            P[baglam[-1]] = (0.8 * P[baglam[-1]]
                             + 0.2 * mecz_raporu["nakil_sicramasi"])
            P[baglam[-1]] /= (np.sum(P[baglam[-1]]) + 1e-12)

        dur, kelam_hukmu, kesinlik = d10_durma_ve_sukut_yokla(
            adim, tikanma_gecmisi, veri_lifi=n)
        adim_muhakeme["kelam_hukmu"] = kelam_hukmu
        adim_muhakeme["kesinlik"] = kesinlik

        if dur or adim + 1 >= azami_guvenlik_tavani:
            break

        if adim_muhakeme["ara_durak"] is not None:
            baglam = tuple(list(baglam[1:]) + [adim_muhakeme["ara_durak"]])
        adim += 1

    nihai_hedef = muhakemeler[-1]["hedef"]
    silsile_adimlari = silsile_adimlarini_bagla(muhakemeler, orijinal_baglam, nihai_hedef, P, Dogal(),
                                                norm_korollalar=norm_korollalar)
    oncutler_terim = [dogal_sayi(t) for t in orijinal_baglam]
    if silsile_adimlari:
        kulli_ispat = OperadSilsile(Dogal(), oncutler_terim, silsile_adimlari,
                                    dogal_sayi(nihai_hedef))
        kulli_sahit_gecerli = ispat_sahidini_dogrula(kulli_ispat, orijinal_baglam, nihai_hedef)
    else:
        kulli_ispat = None
        kulli_sahit_gecerli = False

    p_hedef_satiri = P[nihai_hedef]
    entropi_hedef = float(-np.sum(p_hedef_satiri * np.log(p_hedef_satiri + 1e-12)))
    _havuz_yaz = _s0_havuz_al(n)
    _havuz_yaz["tenakuzlar"][nihai_hedef] = float(muhakemeler[-1].get("kohomolojik_engel", 0.0))
    _havuz_yaz["entropiler"][nihai_hedef] = entropi_hedef
    _havuz_yaz["son_norm_korollalar"] = dict(norm_korollalar)

    turetilen_kategori = turet_1_kategori_bolumlemeli(orijinal_baglam, P, silsile_adimlari)
    turetilen_kume = turet_ayrik_kume_funktoriyel(turetilen_kategori)
    turetilen_alem = turet_dilim_alemi(nihai_hedef, turetilen_kategori.nesneler, P)
    sentetik_kategori_sahidi = kategori_sahidi_sentezle(turetilen_kategori)
    alem_baglami = alem_baglami_ac(turetilen_alem)

    Asim = asimetri_guncelle(P)
    tayf_bilgisi = topos_tayfi_hodge_ile_hesapla(P, Asim, norm_korollalar, baglam)
    rho = tayf_bilgisi["tayf"]
    kuantum_genlikleri = np.sqrt(rho)

    kuantum_durum_vektoru, kod_uzayi_maskesi = yazmacta_bolge_yoktur_superpozisyon(rho, n)
    lif_boyutu = len(kuantum_durum_vektoru)

    d4_tasnif_raporu = d4_kapi_tam_tasnif_mercii(
        hedef_token=nihai_hedef, veri_lifi=n, psi_durum=kuantum_durum_vektoru,
        vecih_ortusmeleri=[adim["türetim_gücü"] for adim in muhakemeler if "türetim_gücü" in adim])
    if d4_tasnif_raporu["eylem"] == "RET":
        return {"hata": "D4 KAPI İHLALİ: MANTIKSIZLIK saptandı (Örnek elendi)",
                "detay": d4_tasnif_raporu}

    dilimler = {
        "uzay": (0, n),
        "kategori": (n, 2 * n),
        "operad": (2 * n, 3 * n),
        "yırtık": (3 * n, 4 * n)
    }

    parite_lifi = {
        "spektral_agirliklar": rho,
        "kuantum_genlikleri": kuantum_genlikleri,
        "kuantum_durum_vektoru": kuantum_durum_vektoru,
        "lif_boyutu": lif_boyutu,
        "alt_uzay_dilimleri": dilimler,
        "kod_uzayi_maskesi": kod_uzayi_maskesi,
        "aktif_modlar": {
            "uzay_modu": bool(rho[0] > 0.15),
            "kategori_modu": bool(rho[1] > 0.15),
            "operad_modu": bool(rho[2] > 0.15),
            "yırtık_modu": bool(rho[3] > 0.05)
        }
    }

    kaide_raporu = kaide_ve_imza_hesapla(baglam[-1], nihai_hedef, P, Asim)

    vecih_ortusmeleri = [adim["türetim_gücü"] for adim in muhakemeler
                        if "türetim_gücü" in adim]
    terazi_hukmu = vecih_hukmu_tayin_et(vecih_ortusmeleri)

    sadakat_raporu = sadakat_devresi_kos(kuantum_durum_vektoru, kod_uzayi_maskesi)
    kuantum_durum_vektoru_temiz = sadakat_raporu["psi_suzulen"]

    funktor_vektoru = np.ones(lif_boyutu, dtype=complex)
    funktor_vektoru[:len(rho)] = np.sqrt(rho) * np.exp(1j * np.pi * rho)
    nihai_intac_psi = intac_funktor_tersi(kuantum_durum_vektoru_temiz, funktor_vektoru)

    qudit_tip_tensoru = qudit_tip_tensoru_kur(turetilen_kategori, nihai_intac_psi, P=P)
    qudit_tip_tensoru["morfizm_kanallari"] = {
        (x, y): tip_tensoru_morfizm_kanali(qudit_tip_tensoru, x, y)
        for (x, y) in turetilen_kategori.ok_siniflari if x != y}

    hudut_raporu = d8_hudut_temizligi_denetle(
        psi=nihai_intac_psi, kod_uzayi_maskesi=kod_uzayi_maskesi,
        uretilmis_tokenler=list(cozulen_hedefler), sozluk_boyutu=n,
        tenakuz_var_mi=bool(terazi_hukmu["hüküm"] == "TENAKUZ"),
        kisirdongu_var_mi=bool(terazi_hukmu["hüküm"] == "KISIRDÖNGÜ"))

    hedef_durum = np.zeros(n, dtype=float)
    hedef_durum[nihai_hedef] = 1.0
    kuantum_bilgisi = kuantum_yogunluk_ve_uhlmann(P, hedef_durum)

    rho_kuantum_matrisi, rho_kuantum_safligi = hakiki_qudit_yogunluk_matrisi(nihai_intac_psi, n)
    rho_kuantum_gercek = np.real(rho_kuantum_matrisi)
    h_hedef = hedef_durum / (np.linalg.norm(hedef_durum) + 1e-12)
    uhlmann_sadakati_hakiki = float(np.real(h_hedef.T @ (rho_kuantum_gercek @ h_hedef)))
    kuantum_bilgisi["rho_yogunluk"] = rho_kuantum_gercek
    kuantum_bilgisi["uhlmann_sadakati"] = uhlmann_sadakati_hakiki
    kuantum_bilgisi["hata_uzay_capasi"] = float(1.0 - uhlmann_sadakati_hakiki)

    kefeler = cok_boyutlu_kefeler_olc(
        P=P, rho_yogunluk=kuantum_bilgisi["rho_yogunluk"],
        uhlmann_sadakati=kuantum_bilgisi["uhlmann_sadakati"],
        son_token=baglam[-1], hedef=nihai_hedef, baglam=orijinal_baglam, Asim=Asim)

    turetilen_kategori_rezk = rezk_tamlastirmasi(turetilen_kategori)

    fock_motoru = FockKipKuantizasyonu(kesme_boyutu=8)
    fock_psi = fock_motoru.s0_vakum_durumu()
    sual_enerji = float(muhakemeler[-1].get("kohomolojik_engel", 0.5))
    fock_psi = fock_motoru.s2_mesele_uyar(fock_psi, sual_enerji)
    fock_psi_sonum, fock_artik_enerji = fock_motoru.s5_hukum_sonumle(fock_psi)

    psi_zirh, _, zirh_raporu = qudit_zirhina_gom(kuantum_durum_vektoru, dilimler)

    dahili_hom_uzayi = ccc_dahili_hom_uzayi_turet(turetilen_kategori)

    hedef_yuklemi = {obj: float(P[obj, nihai_hedef]) for obj in turetilen_kategori.nesneler}
    elemanlar_kat = elemanlar_kategorisi_turet(turetilen_kategori, hedef_yuklemi)

    x_tok = orijinal_baglam[0] if len(orijinal_baglam) > 0 else 0
    y_tok = orijinal_baglam[-1] if len(orijinal_baglam) > 1 else (x_tok + 1) % n
    z_tok = (muhakemeler[0].get("ara_durak") if muhakemeler else None)
    if z_tok is None:
        z_tok = (y_tok + 1) % n
    uc_boyut_raporu = uc_boyutlu_boynuz_doldur(x_tok, y_tok, int(z_tok), nihai_hedef, P)

    if len(turetilen_alem.alemdeki_nesneler) >= 2:
        hedef_nesne = turetilen_alem.baglam_hedefi
        ikinci_nesne = turetilen_alem.alemdeki_nesneler[0]
        gecis_oku = (ikinci_nesne, hedef_nesne)
        temel_degisim = TemelDegisimFunktoru(gecis_oku, float(P[ikinci_nesne, hedef_nesne]))
        pullback_lifleri = temel_degisim.pullback_geri_cek(turetilen_alem, P)
    else:
        pullback_lifleri = []

    elek_oklari = set(turetilen_alem.alem_ici_morfizmler)
    grothendieck_elek = GrothendieckElek(hedef_nesne=nihai_hedef, elek_oklari=elek_oklari)
    grothendieck_elek.elek_kapanisi_dogrula(turetilen_kategori)
    elek_ortu_mu = grothendieck_elek.ortu_mu(P)

    if (len(silsile_adimlari) >= 2 and isinstance(silsile_adimlari[0][0], OperadAgac)
            and isinstance(silsile_adimlari[1][0], OperadAgac)):
        asili_kulli_agac = opetopik_agac_asila(
            ana_agac=silsile_adimlari[1][0], asilanan_agac=silsile_adimlari[0][0],
            yaprak_indeksi=0, X_tip=Dogal())
        asili_agac_etiketi = asili_kulli_agac.etiket
    else:
        asili_agac_etiketi = "temel_korolla"

    yeni_cebir_teorisi = LawvereCebirselTeorisi(
        teori_adi="Topos_Kafes_Cebri",
        islemler={"birlesme": 2, "kesisme": 2, "sifir": 0},
        denklemler=[("birlesme(x, sifir)", "x")])
    lawvere_ctt_tipi = yeni_cebir_teorisi.topos_tipine_cevir()

    gedik_borcu = hata_gedik_karanlik_cevrim_borcu(
        P=P, Asim=Asim, Kan_rez=tayf_bilgisi["Kan_rezidusu"],
        dongu_noktalari=list(orijinal_baglam) + [nihai_hedef])
    kefeler_tam = np.append(kefeler, gedik_borcu)

    d9_tertip_raporu = d9_hafiza_yeniden_tertip_ve_alaka(
        rho_eski=kuantum_bilgisi["rho_yogunluk"], dilimler=dilimler, Asim=Asim)

    if len(turetilen_kategori.ok_siniflari) >= 2:
        ok_listesi = list(turetilen_kategori.ok_siniflari.values())
        ornek_equalizer = topos_esitleyici_equalizer(ok_listesi[0], ok_listesi[1], turetilen_kategori)
    else:
        ornek_equalizer = []

    munasebet_bellek = MunasebetHaritasi()
    munasebet_bellek.munasebet_guncelle(orijinal_baglam, kuvvet=1.0)
    baglam_zayifligi = munasebet_bellek.zayiflik_olc(orijinal_baglam)

    j4_denetleyici = J4GeriYolDenetleyicisi()
    n_kisit_normu = j4_denetleyici.kisit_projeksiyonu_olc(
        hedef_token=nihai_hedef, psi=kuantum_durum_vektoru, kod_uzayi_maskesi=kod_uzayi_maskesi)
    j4_onerilen_hedef, j4_geri_alindi_mi, _ = j4_denetleyici.geri_yol_denetle(
        secilen_hedef=nihai_hedef, n_kisit_normu=n_kisit_normu, born_logitleri=P[baglam[-1]].copy())

    boynuz_analizi = boynuz_turu_ayristir_ve_doldur(
        n_boyut=2, k_kose=1, P=P, Asim=Asim, kenar_dizisi=[orijinal_baglam[0], nihai_hedef])

    halka_yolu = list(orijinal_baglam) + [nihai_hedef]
    sorites_bargmann_raporu = degisken_boylu_bargmann_halkasi(P, Asim, halka_yolu)

    riemann_ortusu = CokYaprakliRiemannOrtusu(
        ["uzay_yaprak", "kategori_yaprak", "operad_yaprak", "yırtık_yaprak"])
    riemann_aktif_yaprak, riemann_monodromi_sigma = riemann_ortusu.monodromi_dondur(
        holonomi_fazi=float(sorites_bargmann_raporu.get("phi_n", 0.0)))

    ic_nno = ToposIcselNNO(turetilen_kategori)
    nno_ornek_hesap = ic_nno.ozyineleme_adimi_hesapla(
        baslangic_degeri=float(muhakemeler[-1].get("türetim_gücü", 0.5)),
        adim_fonksiyonu=lambda x: x * 0.9, n_adim=len(muhakemeler))

    zigzag_raporu = zigzag_bitisiklik_sapmasi_olc(
        P=P, f_gecis_gucu=float(np.mean(P[P > 0])) if np.any(P > 0) else 0.5)

    egim_tahmin = -np.gradient(kefeler_tam) if len(kefeler_tam) > 1 else np.array([-0.1])
    g_fs_vektoru = 1.0 - (np.abs(kuantum_durum_vektoru[:len(egim_tahmin)]) ** 2)
    vadi_yonu = d8a_vadi_memuru_yonu(egim_tahmin, g_fs_vektoru, np.ones_like(egim_tahmin))

    superpozisyon_havuzu = {
        "veri": np.abs(kuantum_durum_vektoru),
        "parametre": np.ones(8, dtype=float) / np.sqrt(8),
        "mahalli": np.abs(psi_zirh[:len(kod_uzayi_maskesi)]),
        "hafiza": np.abs(kuantum_durum_vektoru_temiz),
        "fock": np.abs(fock_psi_sonum.astype(complex))[:len(kod_uzayi_maskesi)],
        "cozum": np.abs(nihai_intac_psi.real)[:len(kod_uzayi_maskesi)]
    }
    I8_raporu = sadakat_invaryant_I8_denetle(superpozisyon_havuzu, kod_uzayi_maskesi, muaf_listesi=[])

    bilesenler_alpha = {x: turetilen_kategori.birim_oklar.get(x, 0) for x in turetilen_kategori.nesneler}
    dogal_donusum_2cell = DogalDonusum2Hucresi("Funktor_F", "Funktor_G", bilesenler_alpha)
    dogal_donusum_gecerli = dogal_donusum_2cell.komutatif_kare_dogrula(
        turetilen_kategori,
        F_haritasi={oid: oid for oid in turetilen_kategori.ok_siniflari.values()},
        G_haritasi={oid: oid for oid in turetilen_kategori.ok_siniflari.values()})

    hafiza_iki_cezve = IkiCezveliHafiza()
    hafiza_iki_cezve.kaydet(
        nesne_id=baglam[-1],
        suret=(kuantum_durum_vektoru[:n] if len(kuantum_durum_vektoru) >= n
               else np.ones(n, dtype=float) / np.sqrt(n)),
        mana=np.array([float(P[baglam[-1], nihai_hedef]),
                      float(tayf_bilgisi["Kan_rezidusu"][baglam[-1], nihai_hedef]), 0.5, 0.5]))
    mutezekkire = MutezekkireKuvveti(hafiza_iki_cezve)

    vahime = VahimeIslemcisi(tehdit_esigi=0.30)
    vahime_raporu = vahime.mana_suz(son_token=baglam[-1], hedef_aday=nihai_hedef,
                                    P=P, Kan_rez=tayf_bilgisi["Kan_rezidusu"], Asim=Asim)

    akile = AkileKatmani()
    ameli_rapor = akile.ameli_akil_tart(
        hedef_id=nihai_hedef, vahime_raporu=vahime_raporu,
        hedef_beklentisi=float(muhakemeler[-1].get("türetim_gücü", 0.5)))

    baise_motoru = KuvveiBaiseVeMotorlar(n_boyut=n)
    eylem_raporu = baise_motoru.sevk_ve_icra(
        aday_hedef=nihai_hedef, vahime_raporu=vahime_raporu,
        ameli_akil_raporu=ameli_rapor, P_satiri=P[baglam[-1]])
    hakiki_icra_hedefi = eylem_raporu["nihai_icra_tokeni"]

    tenakuz_orani = float(terazi_hukmu.get("ihtilaf", 0.0))
    modalite_raporu = topos_modalite_lifi_isle(
        hakikat_degeri=float(muhakemeler[-1].get("doğrudan_güç", 0.5)),
        tenakuz_derecesi=tenakuz_orani, omega_cebiri=tayf_bilgisi["Ω_cebiri"])

    hedef_chi = {nihai_hedef: 1.0}
    pullback_chi_haritasi = alt_nesne_pullback_chi(
        chi_hedef_haritasi=hedef_chi, ok_gecisleri=turetilen_kategori.ok_siniflari,
        P=P, Kan_rez=tayf_bilgisi["Kan_rezidusu"])

    imaj_faktorleri = kategori_imaj_faktorizasyonu_yap(turetilen_kategori, P)

    lambda_nispetleri, yavas_mod, skaler_mizan = d7_hamiltonyen_nispetleri(kefeler)

    u_degeri = float(P[baglam[-1], nihai_hedef] * 2.0 - 1.0)
    C_varsayilan = np.array([1.0, 0.5, 0.25, 0.125], dtype=float)
    S_varsayilan = np.array([0.5, 0.25, 0.125, 0.0625], dtype=float)

    parametre_yazmaci = QuditParametreYazmaci(qudit_sayisi=len(rho), taban=8)
    parametre_acilari = parametre_yazmaci.parametre_acilari_oku()
    psi_evrilmis, theta_cartan, senetler = d6_cartan_kapi_evrimi(
        psi=kuantum_genlikleri, parametre_acilari=parametre_acilari)

    d2_metrikleri = d2_enformasyon_ve_hendese_metrikleri(P, Asim)

    dort_sual_raporu = s2_dort_sual_teftisi(
        tikanma_engeli=float(tayf_bilgisi["enerjiler"]["tıkanma"]),
        kaide_raporu=kaide_raporu, s1_odak_kesiti=odak_kesiti,
        geri_yol_var_mi=bool(len(pullback_chi_haritasi) > 0),
        kulli_ispat_dogrulandi=kulli_sahit_gecerli)

    senet_sadakat_raporu = d8a_senet_sadakati_dogrula(
        senetler=senetler, psi_0=kuantum_genlikleri.astype(complex),
        psi_son=psi_evrilmis)

    kure_2_tipi = kure_n(2)

    kok_agirligi = cartan_kok_ve_agirlik_hesapla(baglam[-1], nihai_hedef, n)
    net_cartan_fazi = float(theta_cartan * kok_agirligi)
    if not senet_sadakat_raporu["sadakat_tam_mi"]:
        net_cartan_fazi = 0.0

    U_kapi_ornek = np.diag(np.exp(1j * parametre_acilari[:min(len(parametre_acilari),
                                                               len(kuantum_durum_vektoru))]))
    hata_engel_degeri = hata_engel_zeno_olc(
        psi_onceki=psi_zirh[:len(kuantum_durum_vektoru)],
        psi_simdiki=kuantum_durum_vektoru, U_kapi=U_kapi_ornek)

    d2_uyarlanmis_enerji = float(skaler_mizan + 0.1 * d2_metrikleri["simetri_sapmasi"]
                                 - 0.05 * d2_metrikleri["karsilikli_haber_bit"])
    kan_dalga_genligi, kan_partisyon_boleni = kan_genlik_hesapla_normalize(
        u=u_degeri, C_katsayilari=C_varsayilan, S_katsayilari=S_varsayilan,
        enerji=d2_uyarlanmis_enerji, cartan_fazi=net_cartan_fazi)

    tam_qudit_tensor_durumu = cok_basamakli_qudit_tensor_durumu(
        token_id=nihai_hedef, veri_lifi=max(2, min(n, 8)), basamak_sayisi=2)

    hata_vektoru = np.ones_like(psi_evrilmis) * float(muhakemeler[-1].get("kohomolojik_engel", 0.1))
    mutabakat_raporu = d8a_senet_ve_egim_mutabakati(
        senetler=senetler, psi_0=kuantum_genlikleri.astype(complex),
        hata_vektoru=hata_vektoru, yon_vektoru=np.ones(len(senetler)))

    monoidal_kat = MonoidalKategori(turetilen_kategori)
    klon_id, delta_oku = frobenius_ko_carpim_klonla(nihai_hedef, monoidal_kat)

    nebati_nefs = NefsiNebatiKatmani(baslangic_enerjisi=1.0)
    metabolik_enerji = nebati_nefs.taziye_gidalan(len(w), tayf_bilgisi["enerjiler"]["tıkanma"])

    hads_orta_terim, hads_durumu, hads_kuvveti = hads_ile_orta_terim_yakala(P, baglam[-1], nihai_hedef)

    akil_mertebeleri = AklinDortMertebesi()
    anlik_akil_mertebesi = akil_mertebeleri.mertebe_tayin_et(
        ispat_sayisi=len(silsile_adimlari),
        tikaniklik=float(muhakemeler[-1].get("kohomolojik_engel", 0.1)),
        kulli_ispat_var_mi=kulli_sahit_gecerli)

    kalp = ManeviKalpKatmani(niyet_boyutu=len(rho))
    itminan_derecesi = kalp.itminan_olc(kuantum_durum_vektoru)
    vicdan_raporu = kalp.vicdani_murakabe(eylem_raporu["eylem_vektoru"], itminan_derecesi)
    if not vicdan_raporu["kalbi_fetva"]:
        hakiki_icra_hedefi = baglam[-1]

    tohum_raporu = nebati_nefs.tevlid_tohumla({"omega_cebiri": tayf_bilgisi["Ω_cebiri"]})

    if dort_sual_raporu["rota"] == "S3_UZAY_AC":
        mana_fibrasyonu = FibrasyonluManaLifi(turetilen_kategori)
        for obj in turetilen_kategori.nesneler:
            mana_fibrasyonu.mana_lifi_ekle(
                obj, np.array([float(P[obj, nihai_hedef]) if obj < n else 0.5,
                              float(tayf_bilgisi["Kan_rezidusu"][obj, nihai_hedef]) if obj < n else 0.1,
                              0.5, 0.5]))
        kartezyen_mana_tasimasi = mana_fibrasyonu.kartezyen_ok_tasi(baglam[-1], nihai_hedef, P)

        icsel_kategori = IcselKategoriNesnesi(turetilen_kategori)
        icsel_kategori_terimi = icsel_kategori.topos_nesnesi_olarak_kodla()

        mutasarrifa_tezgah = PolinomyalMutasarrifaTezgahi(islemler=["bileske", "terkip"], ariteler=[2, 2])
        yeni_kavram_id, yeni_kavram_adi = mutasarrifa_tezgah.hipotetik_terkip_dogur(list(orijinal_baglam))
    else:
        kartezyen_mana_tasimasi = None
        icsel_kategori_terimi = None
        yeni_kavram_id, yeni_kavram_adi = None, "S6_INTAC_ATLA: S3_UZAY_ACILMADI"

    itminan_analizi = topos_terminal_buzulme_itminan(turetilen_kategori, P, kuantum_durum_vektoru)

    v_n1 = P[baglam[-1], :]
    mertebe_kulesi.mertebe_durumu_guncelle(n_seviye=1, durum_vektoru=v_n1, eylemsel_agirlik=float(rho[1]))

    v_n2 = np.zeros(n, dtype=float)
    for (girdi, cikti), prob in norm_korollalar.items():
        if cikti < n:
            v_n2[cikti] += prob
    mertebe_kulesi.mertebe_durumu_guncelle(n_seviye=2, durum_vektoru=v_n2, eylemsel_agirlik=float(rho[2]))

    v_n3 = np.ones(n, dtype=float) * (1.0 - float(uc_boyut_raporu.get("dortyuzlu_3d_engel", 0.1)))
    mertebe_kulesi.mertebe_durumu_guncelle(n_seviye=3, durum_vektoru=v_n3, eylemsel_agirlik=float(rho[0]))

    v_n4 = np.ones(n, dtype=float) * float(itminan_analizi.get("itminan_derecesi", 0.5))
    mertebe_kulesi.mertebe_durumu_guncelle(n_seviye=4, durum_vektoru=v_n4, eylemsel_agirlik=0.2)

    anlik_engel = float(muhakemeler[-1].get("kohomolojik_engel", 0.1))
    suanki_mertebe, tirmanis_hukmu, tirmanis_lif_vektoru = asansor.yukari_tirman_lifli(
        qudit_tip_tensoru, turetilen_kategori, baglam[-1], nihai_hedef,
        alt_engel=anlik_engel)

    burhan_tam_mi = bool(kulli_sahit_gecerli and anlik_engel < 0.05)
    inilmis_mertebe, inis_hukmu, inis_lif_vektoru = asansor.asagi_in_intac_lifli(
        qudit_tip_tensoru, turetilen_kategori, nihai_hedef,
        ust_koherans_tam_mi=burhan_tam_mi)

    cok_mertebeli_hedef, girisim_vektoru, katilim_raporu = cok_mertebeli_girisim_karari(
        kule=mertebe_kulesi, n_boyut=n, yasak=set(orijinal_baglam))

    koyoneda_raporu = ko_yoneda_yogunluk_sentezle(
        veri_dagilimi=(np.abs(kuantum_durum_vektoru[:n]) if len(kuantum_durum_vektoru) >= n
                      else np.ones(n, dtype=float)),
        P=P, kat=turetilen_kategori)

    if len(turetilen_kategori.ok_siniflari) >= 2:
        oklar = list(turetilen_kategori.ok_siniflari.values())
        h_ornek = {x: x % 3 for x in turetilen_kategori.nesneler}
        coeq_raporu = coequalizer_evrensel_faktorizasyon(oklar[0], oklar[1], h_ornek, turetilen_kategori)
    else:
        coeq_raporu = {"faktorizasyon_gecerli_mi": True}

    ornek_ucgenler = ([(orijinal_baglam[i], orijinal_baglam[i + 1], nihai_hedef)
                       for i in range(len(orijinal_baglam) - 1)] if len(orijinal_baglam) >= 2 else [])
    chern_raporu = topolojik_yuk_chern_sayisi(P, Asim, ornek_ucgenler)

    onerme_oncul = {obj: float(P[baglam[-1], obj]) for obj in turetilen_kategori.nesneler}
    onerme_netice = {obj: float(P[obj, nihai_hedef]) for obj in turetilen_kategori.nesneler}
    kripke_raporu = kripke_joyal_forcing(
        baglam_U=orijinal_baglam, onerme_phi=onerme_oncul, onerme_psi=onerme_netice,
        P=P, omega_cebiri=tayf_bilgisi["Ω_cebiri"])

    diyagonal_esitlik_derecesi = topos_diyagonal_esitlik_chi(
        x=baglam[-1], y=nihai_hedef, P=P, Asim=Asim, omega_cebiri=tayf_bilgisi["Ω_cebiri"])

    tannaka_raporu = tannaka_simetri_grubu_turet(turetilen_kategori, P)

    d_psi_tahmin = 1j * psi_evrilmis
    berry_raporu = berry_ayar_potansiyeli_ve_fazi(
        psi=psi_evrilmis, parametre_acilari=parametre_acilari, d_psi=d_psi_tahmin)

    t4_kan_olcum = t4_kan_nedensel_cephe_baglantisi(
        kan_genlik=kan_dalga_genligi, son_token=baglam[-1],
        theta_cartan=theta_cartan, veri_lifi=max(2, min(n, 8)))

    karar_silsilesi_raporu = tekil_karar_hunisi(
        baglam_son=baglam[-1], aday_hedef=nihai_hedef, kule_hedefi=cok_mertebeli_hedef,
        girisim_olasiliklari=girisim_vektoru, t4_kan_sonuc=t4_kan_olcum,
        j4_denetleyici=j4_denetleyici, psi_durum=nihai_intac_psi,
        kod_uzayi_maskesi=kod_uzayi_maskesi, vahime=vahime, akile=akile,
        baise_motoru=baise_motoru, kalp=kalp, P=P, tayf_bilgisi=tayf_bilgisi, Asim=Asim)
    kesin_icra_hedefi = karar_silsilesi_raporu["kesin_nihai_hedef"]

    temel_r = 0.1
    yon_on = -egim_tahmin / (np.linalg.norm(egim_tahmin) + 1e-12)
    sonum_r, egrilik_degeri, bukulme_E = geodezik_bukulme_ve_yaricap_duzelt(
        temel_yaricap=temel_r, yon_simdiki=vadi_yonu, yon_onceki=yon_on,
        artik_hata=float(muhakemeler[-1].get("kohomolojik_engel", 0.1)))

    born_dag = t4_kan_olcum.get("born_dagilimi", np.ones(8) / 8.0)
    j123_raporu = j1_j2_j3_faz_kaydirici_ve_norm(
        born_olasiliklari=born_dag, psi=kuantum_durum_vektoru,
        secilen_jeton=kesin_icra_hedefi % len(born_dag))
    if not j123_raporu["faz_kaymasi_kararli_mi"]:
        kesin_icra_hedefi = baglam[-1]
        karar_silsilesi_raporu["nihai_durum"] = "J3_FAZ_KARARSIZ_SUKUT"

    cech_raporu = cech_kohomoloji_engeli_olc(orijinal_baglam, P)
    leray_raporu = leray_spektral_dizisi_hesapla(
        cech_h1=float(cech_raporu.get("cech_engeli_H1", 0.0)),
        hodge_yırtık=float(tayf_bilgisi["enerjiler"]["tıkanma"]),
        asansor_kati=asansor.mevcut_mertebe)

    gevseme_katsayisi = float(np.clip(1.0 - 0.5 * egrilik_degeri, 0.5, 0.95))
    P_gevsek, korollalar_gevsek = d9_dugum_coz_bag_gevset(
        P, norm_korollalar, gevseme_katsayisi=gevseme_katsayisi)
    if zigzag_raporu["bitisiklik_mesru_mu"]:
        P = P_gevsek
        norm_korollalar = korollalar_gevsek
        d9_dugum_cozuldu_mu = True
    else:
        d9_dugum_cozuldu_mu = False

    X_jenerator = np.outer(kuantum_durum_vektoru[:n], kuantum_durum_vektoru[:n].conj())
    mc_raporu = maurer_cartan_egriligi_denetle(X_jenerator, Asim, baglam[-1], nihai_hedef)

    vecih_ortusmeleri_balya = {"uzay": float(rho[0]), "kategori": float(rho[1]),
                               "operad": float(rho[2]), "yırtık": float(rho[3])}
    riemann_yaprak_anahtari = riemann_aktif_yaprak.replace("_yaprak", "")
    if riemann_yaprak_anahtari in vecih_ortusmeleri_balya:
        vecih_ortusmeleri_balya[riemann_yaprak_anahtari] = float(
            min(vecih_ortusmeleri_balya.values()))

    balyalama_uygun_mu = bool(zigzag_raporu["bitisiklik_mesru_mu"]
                              and leray_raporu["spektral_dizi_kapandi_mi"]
                              and nno_ornek_hesap > 0.01)
    if balyalama_uygun_mu:
        balyalama_raporu = d9_kume_kapanisi_ve_balyalama(
            hafiza_havuzu=_KALICI_HAFIZA_HAVUZU, vecih_ortusmeleri=vecih_ortusmeleri_balya,
            aktif_kayitlar=silsile_adimlari)
        _KALICI_HAFIZA_HAVUZU["kayit_arsivi"].append(
            {"nihai_hedef": nihai_hedef, "balya_id": balyalama_raporu["yeni_balya_id"]})
    else:
        balyalama_raporu = {"acilan_cartan_koku": None, "yeni_balya_id": None,
                            "balyalanan_nesne_sayisi": 0, "silinen_kayit_sayisi": 0,
                            "sebep": "ZIGZAG_MESRU_DEGIL" if not zigzag_raporu["bitisiklik_mesru_mu"]
                            else ("LERAY_KAPANMADI" if not leray_raporu["spektral_dizi_kapandi_mi"]
                                  else "NNO_YAKINSAMADI")}

    return {
        "kesin_icra_hedefi": kesin_icra_hedefi,
        "karar_silsilesi_raporu": karar_silsilesi_raporu,
        "asansor_canli_son_kat": inilmis_mertebe,
        "rho_kuantum_safligi": rho_kuantum_safligi,
        "kalici_balya_toplami": len(_KALICI_HAFIZA_HAVUZU["balyalar"]),
        "senet_sadakati_raporu": senet_sadakat_raporu,
        "s2_dort_sual_raporu": dort_sual_raporu,
        "d2_enformasyon_metrikleri": d2_metrikleri,
        "yuksek_kure_S2_tipi": str(kure_2_tipi),
        "d4_kapi_tasnifi": d4_tasnif_raporu,
        "riemann_aktif_yaprak": riemann_aktif_yaprak,
        "topos_icsel_nno_hesabi": nno_ornek_hesap,
        "zigzag_bitisiklik_dogrulamasi": zigzag_raporu,
        "geodezik_bukulme_enerjisi": bukulme_E,
        "sonumlenmis_newton_yaricapi": sonum_r,
        "j3_projektif_norm": j123_raporu["j3_jeton_normu"],
        "kulli_leray_engeli": leray_raporu["kulli_leray_engeli"],
        "d9_dugum_cozuldu_mu": d9_dugum_cozuldu_mu,
        "balyalama_uygun_muydu": balyalama_uygun_mu,
        "parite_lifi": parite_lifi,
        "omega_cebiri": tayf_bilgisi["Ω_cebiri"],
        "muhakeme_silsilesi": muhakemeler,
        "nihai_muhakeme": muhakemeler[-1],
        "kaide_imzasi": kaide_raporu["imza"],
        "terazi_hukmu": terazi_hukmu,
        "sadakat_devresi": sadakat_raporu,
        "intac_kuantum_hali": nihai_intac_psi,
        "kulli_ispat_sahidi": kulli_ispat,
        "kulli_ispat_dogrulandi": kulli_sahit_gecerli,
        "qudit_tip_tensoru": qudit_tip_tensoru,
        "turetilen_kategori_ham": turetilen_kategori,
        "turetilen_1_kategori": {
            "nesneler": turetilen_kategori.nesneler,
            "morfizm_sayisi": len(turetilen_kategori.ok_siniflari),
            "bileske_sayisi": len(turetilen_kategori.bileske_tablosu)
        },
        "turetilen_ayrik_kume_pi0": {
            "bilesen_sayisi": len(turetilen_kume.bilesenler),
            "denklik_siniflari": [sorted(b) for b in turetilen_kume.bilesenler]
        },
        "turetilen_dilim_alemi": {
            "hedef": turetilen_alem.baglam_hedefi,
            "alem_nesneleri": turetilen_alem.alemdeki_nesneler,
            "komutatif_ucgenler": len(turetilen_alem.alem_ici_morfizmler),
            "ctt_baglam_degisken_sayisi": len(alem_baglami.tipler)
        },
        "sentetik_kategori_terimi": sentetik_kategori_sahidi,
        "uhlmann_sadakati": kuantum_bilgisi["uhlmann_sadakati"],
        "kefeler_vektoru": kefeler,
        "lambda_nispetleri": lambda_nispetleri,
        "yavas_mod_indeksi": yavas_mod,
        "skaler_mizan": skaler_mizan,
        "kan_intac_genligi": kan_dalga_genligi,
        "d0_gecit_raporu": gecit_raporu,
        "d8_hudut_raporu": hudut_raporu,
        "s1_odak_siniri": (bas_idx, son_idx),
        "s1_odak_kesiti": odak_kesiti,
        "theta_cartan_birikimi": theta_cartan,
        "d8a_mutabakat_raporu": mutabakat_raporu,
        "d9_balyalama_raporu": balyalama_raporu,
        "s0_vakum_tetiklendi": s0_vakum_tetiklendi,
        "s0_secilen_gaye": s0_secilen_gaye,
        "rn_sarti_terimi": hakiki_rn_sarti(Dogal(), r=1, n=2),
        "karakteristik_harita_chi": topos_karakteristik_haritasi_chi(
            set(turetilen_kategori.ok_siniflari.keys()), P, Asim,
            tayf_bilgisi["Kan_rezidusu"], tayf_bilgisi["Ω_cebiri"]),
        "sol_kan_uzantisi_Lan": ayrik_sol_kan_uzantisi(
            {obj: float(P[obj, nihai_hedef]) for obj in turetilen_alem.alemdeki_nesneler},
            turetilen_alem, turetilen_kategori),
        "turetilen_1_kategori_rezk": {
            "univalent_nesneler": turetilen_kategori_rezk.nesneler,
            "morfizm_sayisi": len(turetilen_kategori_rezk.ok_siniflari)
        },
        "cech_kohomolojisi_H1": cech_kohomoloji_engeli_olc(orijinal_baglam, P),
        "t4_nedensel_cephe_olcumu": t4_nedensel_cephe_olcumu(
            psi_intac=nihai_intac_psi, son_token=baglam[-1],
            theta_cartan=theta_cartan, veri_lifi=max(2, min(n, 8))),
        "qudit_zirh_raporu": zirh_raporu,
        "fock_artik_enerji": fock_artik_enerji,
        "ccc_dahili_hom_sayisi": len(dahili_hom_uzayi),
        "qudit_parametre_acilari": parametre_acilari,
        "cartan_kok_agirligi": kok_agirligi,
        "tam_qudit_tensor_boyutu": len(tam_qudit_tensor_durumu),
        "monoidal_tensor_ok_sayisi": len(monoidal_kat.tensor_oklari),
        "heyting_mantik_analizi": heyting_operatorleri(
            a=float(muhakemeler[-1].get("türetim_gücü", 0.5)),
            b=float(muhakemeler[-1].get("doğrudan_güç", 0.5)),
            omega_cebiri=tayf_bilgisi["Ω_cebiri"]),
        "elemanlar_kategorisi_int_P": {
            "nesneler": elemanlar_kat.nesneler,
            "morfizm_sayisi": len(elemanlar_kat.ok_siniflari)
        },
        "uc_boyutlu_koherans_Lambda3": uc_boyut_raporu,
        "temel_degisim_pullback_lifleri": pullback_lifleri,
        "grothendieck_elek_ortu_mu": elek_ortu_mu,
        "opetopik_asili_agac_etiketi": asili_agac_etiketi,
        "lawvere_dinamik_tipi": lawvere_ctt_tipi,
        "hata_gedik_borcu": gedik_borcu,
        "d9_alaka_ve_muhur": {"alaka_skorlari": d9_tertip_raporu["alaka_skorlari"],
                             "en_alakali_vecih": d9_tertip_raporu["en_alakali_vecih"]},
        "topos_equalizer_nesneleri": ornek_equalizer,
        "kefeler_vektoru_7li": kefeler_tam,
        "vahime_sezgisi": vahime_raporu,
        "ameli_akil_maslahat": ameli_rapor,
        "kuvve_i_baise_eylem": {k: v for k, v in eylem_raporu.items() if k != "eylem_vektoru"},
        "hakiki_icra_hedefi": hakiki_icra_hedefi,
        "sevk_kaynagi": eylem_raporu["sevk_kaynagi"],
        "modalite_lifi_raporu": modalite_raporu,
        "pullback_chi_haritasi": pullback_chi_haritasi,
        "imaj_faktorizasyon_sayisi": len(imaj_faktorleri),
        "frobenius_klon_hedefi": klon_id,
        "manevi_kalp_vicdan": vicdan_raporu,
        "aklin_epistemik_mertebesi": anlik_akil_mertebesi,
        "hads_sezgi_durumu": hads_durumu,
        "nebati_metabolik_enerji": metabolik_enerji,
        "nebati_tohum_mirasi": tohum_raporu,
        "mana_fibrasyonu_tasimasi": kartezyen_mana_tasimasi,
        "icsel_kategori_nesnesi": icsel_kategori_terimi,
        "mutasarrifa_hipotetik_kavram": (yeni_kavram_id, yeni_kavram_adi),
        "topos_terminal_itminan": itminan_analizi,
        "koyoneda_kolimit_sadakati": koyoneda_raporu["yogunluk_sadakati"],
        "coequalizer_faktorizasyon": coeq_raporu["faktorizasyon_gecerli_mi"],
        "chern_sayisi_c1": chern_raporu["chern_sayisi_c1"],
        "izgara_sekli": izgara_sekli,
        "kripke_joyal_zorlama": kripke_raporu,
        "diyagonal_ic_esitlik_chi": diyagonal_esitlik_derecesi,
        "tannaka_ayar_simetrisi": tannaka_raporu,
        "berry_geometrik_faz": berry_raporu,
        "kan_partisyon_boleni": kan_partisyon_boleni,
        "t4_kan_cephe_karari": {k: v for k, v in t4_kan_olcum.items() if k != "born_dagilimi"},
        "maurer_cartan_raporu": mc_raporu,
        "sorites_mobius_raporu": sorites_bargmann_raporu,
        "mecz_vadi_yonu": vadi_yonu,
        "sadakat_I8_raporu": I8_raporu,
        "dogal_donusum_2cell_gecerli": dogal_donusum_gecerli,
        "j4_geri_alindi_mi": j4_geri_alindi_mi,
        "j4_onerilen_hedef": j4_onerilen_hedef,
        "hata_engel_zeno": hata_engel_degeri,
        "baglam_zayifligi": baglam_zayifligi,
        "boynuz_ayrisimi": boynuz_analizi,
        "asansor_tirmanis_hukmu": tirmanis_hukmu,
        "asansor_tirmanis_lif_vektoru": tirmanis_lif_vektoru,
        "asansor_inis_hukmu": inis_hukmu,
        "aktif_asansor_mertebesi": inilmis_mertebe,
        "asansor_inis_lif_vektoru": inis_lif_vektoru,
        "cok_mertebeli_nihai_hedef": cok_mertebeli_hedef,
        "mertebeler_arasi_katilim_payi": katilim_raporu,
        "detay": tayf_bilgisi
    }


@dataclass
class SilsileAyari:
    azami_alfabe: int = 256
    dortlu_ornek: int = 64
    tohum: int = 0


_SILSILE_SAYI: Dict[str, int] = {}
_SILSILE_NISPET: Dict[str, float] = {}


def silsile_sifirla() -> None:
    _SILSILE_SAYI.clear()
    _SILSILE_SAYI.update({"çağrı": 0, "asansör_katı": 0, "tıkanma": 0,
                          "dörtlü": 0, "üçgen_ihlâli": 0})
    _SILSILE_NISPET.clear()
    _SILSILE_NISPET.update({"büzülme": 0.0, "𝒮_simetrik": 0.0,
                            "𝒜_yönlü": 0.0, "Ω_yırtık": 0.0,
                            "δ_gromov": 0.0, "üçgen_nispeti": 0.0})


silsile_sifirla()


def silsile_yukle(d: Dict[str, Any]) -> None:
    for k, v in dict(d).items():
        a = str(k)
        if a in _SILSILE_SAYI:
            _SILSILE_SAYI[a] = int(v)
        elif a in _SILSILE_NISPET:
            _SILSILE_NISPET[a] = float(v)


def gromov_delta_hesapla(duz: Sequence[int], n: int, dortlu_ornek: int = 64
                         ) -> Dict[str, Any]:
    y = np.asarray(list(duz), np.int64).reshape(-1) % max(2, int(n))
    m = int(n)
    if m < 4 or y.size < 2:
        return {"δ": 0.0, "üçgen_ihlâli": 0.0, "dörtlü": 0}

    T = np.zeros((m, m), dtype=float)
    np.add.at(T, (y[:-1], y[1:]), 1.0)
    S = T + T.T
    var = S > 0.0
    en_az = float(S[var].min()) if bool(var.any()) else 1.0
    ic = -np.log(np.where(var, S, en_az)) + np.where(var, 0.0, 1.0)
    np.fill_diagonal(ic, 0.0)
    D = ic.copy()
    for k in range(m):
        D = np.minimum(D, D[:, k:k + 1] + D[k:k + 1, :])

    cikan: List[Tuple[int, int, int, int]] = []
    for i in range(m):
        for a in (1, 2, 3):
            j, k2, l = (i + a) % m, (i + 2 * a) % m, (i + 3 * a) % m
            if len({i, j, k2, l}) == 4:
                cikan.append((i, j, k2, l))
            if len(cikan) >= int(dortlu_ornek):
                break
        if len(cikan) >= int(dortlu_ornek):
            break
    if not cikan:
        return {"δ": 0.0, "üçgen_ihlâli": 0.0, "dörtlü": 0}

    Q = np.asarray(cikan, np.int64)
    i, j, k2, l = Q[:, 0], Q[:, 1], Q[:, 2], Q[:, 3]
    s1 = D[i, j] + D[k2, l]
    s2 = D[i, k2] + D[j, l]
    s3 = D[i, l] + D[j, k2]
    en_buyuk = float(np.max(np.abs(s1 - np.maximum(s2, s3))))
    ihlal = int(np.count_nonzero(D[i, k2] > D[i, j] + D[j, k2]))
    return {"δ": en_buyuk, "üçgen_ihlâli": float(ihlal) / float(Q.shape[0]),
            "dörtlü": int(Q.shape[0])}


def silsile_teshisi(baglamlar: Sequence[Sequence[int]], lif: Sequence[int],
                    ayar: Optional[SilsileAyari] = None) -> Dict[str, Any]:
    assert baglamlar, "silsile teşhisi için bağlam BOŞ olamaz"
    a = ayar or SilsileAyari()
    lif = tuple(int(x) for x in lif)
    assert lif, "silsile teşhisi için lif yapısı BOŞ olamaz"
    veri_lifi = int(lif[0])
    n = max(2, min(int(a.azami_alfabe), veri_lifi) if a.azami_alfabe else veri_lifi)
    d_toplam = max(1, int(np.prod(lif)))

    duz: List[int] = []
    for b in baglamlar:
        duz.extend(int(x) % n for x in
                   np.asarray(list(b), np.int64).reshape(-1) if int(x) >= 0)
    assert duz, "bağlamların hepsi boş -- teşhis edilecek dizi yok"
    if len(duz) < 2:
        duz = duz * 2

    sonuc = silsile_teshisi_kos(duz, n)
    if "hata" in sonuc:
        yedek = duz[-4:] if len(duz) >= 4 else duz * 2
        sonuc = silsile_teshisi_kos(yedek, n)
        assert "hata" not in sonuc, (
            "D2 SİLSİLE: küllî motor iki denemede de çöktü: %r"
            % sonuc.get("hata"))

    tayf_bilgisi = sonuc["detay"]
    parite_lifi = sonuc["parite_lifi"]
    rho = np.asarray(parite_lifi["spektral_agirliklar"], dtype=float)
    enerjiler = tayf_bilgisi["enerjiler"]

    top3 = float(enerjiler["uzay"] + enerjiler["kategori"]
                + enerjiler["tıkanma"]) + 1e-12
    hodge_sozluk = {
        "𝒮_simetrik": float(enerjiler["uzay"] / top3),
        "𝒜_yönlü": float(enerjiler["kategori"] / top3),
        "Ω_yırtık": float(enerjiler["tıkanma"] / top3),
    }

    kat_sayisi = max(1, len(lif))
    buzulme_ham = float(int(sonuc["asansor_canli_son_kat"]) - 1) / 3.0
    buzulme = float(np.clip(buzulme_ham, 0.0, 1.0)) * float(kat_sayisi - 1)
    alt = int(np.floor(buzulme))
    ust = min(alt + 1, kat_sayisi - 1)
    pay = buzulme - alt
    demet = np.zeros(kat_sayisi, dtype=float)
    demet[alt] += (1.0 - pay)
    demet[ust] += pay
    kat = int(min(max(int(round(buzulme)), 0), kat_sayisi - 1))
    _lif_tirmanis = sonuc.get("asansor_tirmanis_lif_vektoru")
    _lif_inis = sonuc.get("asansor_inis_lif_vektoru")
    _gercek_lif = _lif_tirmanis if _lif_tirmanis is not None else _lif_inis
    asansor_sozluk = {"kat": kat, "büzülme": buzulme, "demet": demet,
                      "eksen": kat, "lif": lif, "taban_boyu": int(lif[kat]),
                      "gerçek_lif_vektörü": _gercek_lif,
                      "gerçek_lif_boyu": (int(_gercek_lif.size)
                                         if _gercek_lif is not None else 0),
                      "tırmanış_hükmü": sonuc.get("asansor_tirmanis_hukmu"),
                      "iniş_hükmü": sonuc.get("asansor_inis_hukmu")}

    psi_kaynagi = np.asarray(parite_lifi["kuantum_durum_vektoru"], dtype=complex)
    if psi_kaynagi.size >= d_toplam:
        psi_d = psi_kaynagi[:d_toplam]
    else:
        tekrar = int(np.ceil(d_toplam / max(1, psi_kaynagi.size)))
        psi_d = np.tile(psi_kaynagi, tekrar)[:d_toplam]
    Pi_matrisi, pi_safligi = hakiki_qudit_yogunluk_matrisi(psi_d, d_toplam)

    selale_sozluk = {
        "tıkanma": int(sum(1 for m in sonuc["muhakeme_silsilesi"]
                          if m.get("hüküm") == "tıkanma"))
    }

    gr = gromov_delta_hesapla(duz, n, int(a.dortlu_ornek))

    omega_cebiri_sozluk = {"cebir": str(tayf_bilgisi["Ω_cebiri"]),
                           "tümleyen": None, "unsur": None}

    katman = ("uzay", "kategori", "operad", "yırtık")
    kafes = [{"ad": ad} for ad in katman]

    _SILSILE_SAYI["çağrı"] += 1
    _SILSILE_SAYI["asansör_katı"] = kat
    _SILSILE_SAYI["tıkanma"] = selale_sozluk["tıkanma"]
    _SILSILE_SAYI["dörtlü"] = int(gr["dörtlü"])
    _SILSILE_SAYI["üçgen_ihlâli"] = int(round(gr["üçgen_ihlâli"] * gr["dörtlü"]))
    _SILSILE_NISPET["büzülme"] = buzulme
    _SILSILE_NISPET["𝒮_simetrik"] = hodge_sozluk["𝒮_simetrik"]
    _SILSILE_NISPET["𝒜_yönlü"] = hodge_sozluk["𝒜_yönlü"]
    _SILSILE_NISPET["Ω_yırtık"] = hodge_sozluk["Ω_yırtık"]
    _SILSILE_NISPET["δ_gromov"] = float(gr["δ"])
    _SILSILE_NISPET["üçgen_nispeti"] = float(gr["üçgen_ihlâli"])

    return {
        "asansör": asansor_sozluk,
        "kafes": kafes,
        "tayf": rho,
        "katman": katman,
        "hodge": hodge_sozluk,
        "Π": Pi_matrisi,
        "Π_safligi": pi_safligi,
        "şelale": selale_sozluk,
        "Ω_cebiri": omega_cebiri_sozluk,
        "δ_Gromov": float(gr["δ"]),
        "üçgen_ihlâli": float(gr["üçgen_ihlâli"]),
        "alfabe": n,
        "basamak": len(duz),
        "qudit_tip_tensoru": sonuc.get("qudit_tip_tensoru"),
        "turetilen_kategori_ham": sonuc.get("turetilen_kategori_ham"),
        "mertebeler_arasi_katilim_payi": sonuc.get("mertebeler_arasi_katilim_payi"),
        "kaynak_motor_çıktısı": sonuc,
        "türetim_beyanı": turetim_beyani(),
    }


def kaide_imzasi_uret(dizi: Sequence[int], n: int) -> str:
    y = [int(x) % max(2, int(n)) for x in dizi]
    if len(y) < 2:
        y = y + y
    P, Asim, _nk = veriden_geometri_cikar(y, n, K_max=2)
    kaide_raporu = kaide_ve_imza_hesapla(int(y[0]), int(y[-1]), P, Asim)
    imza = kaide_raporu["imza"]
    return "K" + "-".join("%x" % (int(v) & 0xF) for v in imza)


def silsile_beyani() -> Dict[str, Any]:
    b: Dict[str, Any] = {k: int(v) for k, v in _SILSILE_SAYI.items()}
    b.update({k: float(v) for k, v in _SILSILE_NISPET.items()})
    b.update({"türetim_%s" % k: v for k, v in turetim_beyani().items()})
    return b


def silsile_metni(teshis: Optional[Dict[str, Any]] = None,
                  beyan: Optional[Dict[str, Any]] = None) -> str:
    b = dict(beyan or silsile_beyani())
    if not int(b.get("çağrı", 0)):
        return ("  D2 SİLSİLE: HİÇ KOŞMADI -- türetim yapılmadı "
                "(tek motor: sonsuz_mertebeler_teorisi.py)")
    s = ["  D2 SİLSİLE -- TEK MOTORDAN TÜRETİLİR (nefs/hendese.py kaldırıldı)",
         "    çağrı %d   asansör katı %d   büzülme %.4f"
         % (int(b["çağrı"]), int(b["asansör_katı"]), float(b["büzülme"])),
         "    Hodge: 𝒮 %.4f ⊕ 𝒜 %.4f ⊕ Ω_yırtık %.4f"
         % (b["𝒮_simetrik"], b["𝒜_yönlü"], b["Ω_yırtık"]),
         "    ŞELALE tıkanma: %d" % int(b["tıkanma"]),
         "    Gromov δ %.4f   üçgen ihlâli nispeti %.4f (%d dörtlü)"
         % (b["δ_gromov"], b["üçgen_nispeti"], int(b["dörtlü"]))]
    if teshis:
        s.append("    KAFES DÜĞÜMLERİ (ad · ρ):")
        for dug, ro in zip(teshis["kafes"], teshis["tayf"]):
            s.append("      %-10s ρ %.4f" % (dug["ad"], float(ro)))
        om = teshis["Ω_cebiri"]
        s.append("    Ω CEBİRİ: %s   (tümleyen %s · unsur %s)"
                 % (om["cebir"], om.get("tümleyen"), om.get("unsur")))
    return "\n".join(s)



SABIT: Tuple[int, ...] = tuple(range(10))

AZAMI_TAM_MERTEBE = 20

sys.setrecursionlimit(max(sys.getrecursionlimit(), 200000))


@dataclass(frozen=True)
class Uzay:
    yuva: int
    mertebe: int
    tam_kuruldu: bool
    denetlendi: bool
    baglayici: int
    tip_ozeti: str
    hata: str = ""
    h_mertebe: int = -1
    h_adi: str = ""
    h_denetlendi: bool = False
    h_hata: str = ""

    @property
    def pencere(self) -> int:
        return min(self.mertebe + 1, 4)

    @property
    def adim(self) -> int:
        return 1 + int(math.log2(1 + self.mertebe))

    @property
    def parametre(self) -> int:
        return 2 ** self.pencere + self.baglayici


def _baglayici_say(t: Terim) -> int:
    n = 0
    yigin: List[object] = [t]
    while yigin:
        d = yigin.pop()
        if not isinstance(d, Dugum):
            continue
        if isinstance(d, (Pi, Sigma, Lam, YolLam)):
            n += 1
        for alan in d._alanlar():
            if isinstance(alan, Dugum):
                yigin.append(alan)
            elif isinstance(alan, tuple):
                yigin.extend(a for a in alan if isinstance(a, Dugum))
    return n


def h_mertebe_sec(mertebe: int) -> int:
    return int(min(max(int(mertebe), 0), len(MERTEBE_ADI) - 1))


def h_sarti_denetle(mertebe: int, baglam: Baglam) -> Tuple[int, str, bool, str]:
    l = h_mertebe_sec(mertebe)
    try:
        denetle_t(mertebe_sarti(Deg("A"), l), Evren(0), baglam)
        return l, MERTEBE_ADI[l], True, ""
    except Exception as e:
        return l, MERTEBE_ADI[l], False, "%s: %s" % (type(e).__name__,
                                                     str(e)[:120])


def _tam_kur(mertebe: int) -> Tuple[Terim, str]:
    A = Deg("A")
    return morfizm_tipi(A, mertebe), "morfizm_tipi(A, %d)" % mertebe


def _temsilci_kur(mertebe: int) -> Tuple[Terim, str]:
    n = 1 + (mertebe % AZAMI_TAM_MERTEBE)
    return (dongu_uzayi_n(Cember(), Taban(), n),
            "Ω^%d(S¹)  [mertebe %d için temsilci]" % (n, mertebe))


def uzaylari_kur(dinamik: Sequence[int]) -> List[Uzay]:
    if len(dinamik) != 10:
        raise ValueError("dinamik mertebe sayısı 10 olmalı")
    gA = Baglam.terimlerden({"A": U, "a": Deg("A"), "b": Deg("A")})
    g0 = Baglam()

    uzaylar: List[Uzay] = []
    for yuva, m in enumerate(tuple(SABIT) + tuple(int(x) for x in dinamik)):
        tam = m <= AZAMI_TAM_MERTEBE
        if tam:
            tip, ozet = _tam_kur(m)
            baglam, hedef = gA, U
        else:
            tip, ozet = _temsilci_kur(m)
            baglam, hedef = g0, U
        hata = ""
        try:
            denetle_t(tip, hedef, baglam)
            gecti = True
        except Exception as e:
            gecti = False
            hata = "%s: %s" % (type(e).__name__, str(e)[:120])
        hl, had, hg, hh = h_sarti_denetle(m, gA)
        uzaylar.append(Uzay(yuva=yuva, mertebe=m, tam_kuruldu=tam,
                            denetlendi=gecti, baglayici=_baglayici_say(tip),
                            tip_ozeti=ozet, hata=hata,
                            h_mertebe=hl, h_adi=had,
                            h_denetlendi=hg, h_hata=hh))
    return uzaylar


def tikanma_tipi() -> Terim:
    return tikanma_postulati(Deg("X")).tip


def kesit_tipi_ile_agirlik() -> Tuple[Terim, Terim]:
    M, Fw = Deg("M"), Deg("Fw")
    return kesit_tipi(M, Fw), evrensel_demet(M, Fw)


def akit_denetle() -> List[Dict[str, object]]:
    g = Baglam.terimlerden({"M": U, "Fw": ok(Deg("M"), U), "X": U})
    isler = [
        ("tıkanma (Postnikov) tipi iyi teşkil",
         lambda: denetle_tip(tikanma_tipi(), g)),
        ("kesit tipi Π(w:M). F w : U",
         lambda: denetle_t(kesit_tipi(Deg("M"), Deg("Fw")), U, g)),
        ("evrensel demet Σ(w:M). F w : U",
         lambda: denetle_t(evrensel_demet(Deg("M"), Deg("Fw")), U, g)),
    ]
    out: List[Dict[str, object]] = []
    for ad, fn in isler:
        try:
            fn()
            out.append({"ad": ad, "netice": "GEÇTİ"})
        except Exception as e:
            out.append({"ad": ad, "netice": "HATA",
                        "izah": str(e)[:120]})
    return out


def kategori_beyani(uzaylar: Sequence[Uzay]) -> str:
    uz = list(uzaylar)
    s = ["=== YİRMİ ∞-KATEGORİ UZAYI (tek motor: sonsuz_mertebeler_teorisi.py) ===", "",
         "  %-5s %-8s %-9s %-11s %-9s %-7s %-4s %-10s %s"
         % ("yuva", "mertebe", "kuruluş", "denetim", "bağlayıcı",
            "pencere", "adım", "h-mertebe", "tip"),
         "  " + "-" * 96]
    for u in uz:
        s.append("  %-5d %-8d %-9s %-11s %-9d %-7d %-4d %-10s %s"
                 % (u.yuva, u.mertebe,
                    "TAM" if u.tam_kuruldu else "temsilci",
                    "geçti" if u.denetlendi else "KALDI",
                    u.baglayici, u.pencere, u.adim,
                    "%s%s" % (u.h_adi, "" if u.h_denetlendi else "!"),
                    u.tip_ozeti))
        if u.hata:
            s.append("        ! " + u.hata)
        if u.h_hata:
            s.append("        ! h-mertebe: " + u.h_hata)
    s += ["",
          "  H-MERTEBE (ferman 1-Ğ: vechin mertebesi diziden okunur)",
          "    nokta=büzülebilir · uzay=önerme · kategori=küme · "
          "tip=grupoid ve üstü",
          "    ``n_mertebe`` ile kurulur, ``denetle_t`` ile DENETLENİR;",
          "    bu dördü omega_kategori'den geri getirilen cevherlerdir.",
          "",
          "  Akit denetimi (modül fiilen çağrılıyor mu):"]
    for n in akit_denetle():
        s.append("    %s %s%s" % ("✓" if n["netice"] == "GEÇTİ" else "✗",
                                  n["ad"],
                                  "" if n["netice"] == "GEÇTİ"
                                  else "  [%s]" % n.get("izah", "")))
    tam = sum(1 for u in uz if u.tam_kuruldu)
    gecen = sum(1 for u in uz if u.denetlendi)
    h_gecen = sum(1 for u in uz if u.h_denetlendi)
    s += ["",
          "  hulâsa: %d/%d uzay TAM kuruldu, %d/%d makine denetiminden "
          "geçti, %d/%d h-mertebe şartı denetlendi."
          % (tam, len(uz), gecen, len(uz), h_gecen, len(uz)),
          "  Mertebesi %d'ten büyük olanlar temsilci tiple denetlendi;"
          % AZAMI_TAM_MERTEBE,
          "  sebebi seyrek Kan sıçramasıdır (aradaki mertebeler açılmaz)."]
    return "\n".join(s)



KIP_QUDIT = "qudit"
KIP_TUTARLI = "tutarlı"
KIP_LIE = "lie-chebyshev qudit"


def kodla(x, ne: str = KIP_TUTARLI, boyut: int = 16,
         bag: int = 8) -> np.ndarray:
    v = np.asarray(x, float).reshape(-1)

    if ne == KIP_TUTARLI:
        from kuantum.surekli import tutarli_durum
        return np.stack([tutarli_durum(complex(t), int(boyut)) for t in v])

    if ne == KIP_QUDIT:
        u = np.zeros(int(boyut), dtype=complex)
        u[:min(v.size, int(boyut))] = v[:int(boyut)]
        n = np.linalg.norm(u)
        return (u / n) if n > 1e-300 else u

    if ne == KIP_LIE:
        from kuantum.qudit import QuditAyari, durum
        a = QuditAyari(d=int(boyut), yon=max(1, min(v.size, int(boyut) - 1)))
        n_k, n_d = 4, 8
        g = np.resize(v, n_k * (n_d + 1)).reshape(n_k, n_d + 1)
        return durum(g, np.roll(g, 1, axis=1), v[:a.yon], ayar=a)

    raise ValueError("kodlama usulü bilinmiyor: %r" % (ne,))


def mesafe(a: np.ndarray, b: np.ndarray, ne: str) -> float:
    if ne in (KIP_TUTARLI, KIP_LIE, KIP_QUDIT):
        return -float(np.log(max(ortusme(a, b), 1e-300)))
    a = np.asarray(a).reshape(-1)
    b = np.asarray(b).reshape(-1)
    n = max(a.size, b.size)
    a = np.pad(a, (0, n - a.size))
    b = np.pad(b, (0, n - b.size))
    return float(np.linalg.norm(np.abs(a - b)))


def ortusme(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a)
    b = np.asarray(b)
    if a.ndim == 2 and b.ndim == 2:
        return float(np.abs(np.prod(
            [np.vdot(a[k], b[k]) for k in range(a.shape[0])])))
    return float(np.abs(np.vdot(a.reshape(-1), b.reshape(-1))))


def sadakat_kodlama_kiyasi(X: Sequence[Sequence[float]], ne: str = KIP_TUTARLI,
                           boyut: int = 16) -> Dict[str, float]:
    X = [np.asarray(x, float).reshape(-1) for x in X]
    kod = [kodla(x, ne=ne, boyut=boyut) for x in X]
    ham, gom = [], []
    for i in range(len(X)):
        for j in range(i + 1, len(X)):
            ham.append(float(np.linalg.norm(X[i] - X[j])))
            gom.append(mesafe(kod[i], kod[j], ne))
    ham = np.asarray(ham)
    gom = np.asarray(gom)
    if ham.size < 2 or ham.std() < 1e-12 or gom.std() < 1e-12:
        return {"sadakat": float("nan"), "çift": int(ham.size),
                "sebep": "mesafeler ayrışmıyor"}
    r_p = float(np.corrcoef(ham, gom)[0, 1])
    sr = lambda z: np.argsort(np.argsort(z)).astype(float)
    r_s = float(np.corrcoef(sr(ham), sr(gom))[0, 1])
    return {"sadakat": r_s, "pearson": r_p, "çift": int(ham.size)}


@dataclass
class Lif:

    defter: Dict[str, Dict[str, Dict[str, np.ndarray]]] = field(
        default_factory=dict)
    sozluk: int = 0
    asansor_kati: int = -1
    uzay_mertebesi: Tuple[int, ...] = ()
    kategori_beyani: str = ""
    tur: int = 0
    doyma: float = 0.0
    islenen: int = 0
    gercek_kategori_eslesme: int = 0
    gercek_hom_toplam: int = 0

    def tak(self, tip: str, kategori: str, uzay: str,
            nokta: np.ndarray) -> "Lif":
        self.defter.setdefault(str(tip), {}) \
                   .setdefault(str(kategori), {})[str(uzay)] = \
            np.asarray(nokta)
        return self

    def tipler(self) -> List[str]:
        return sorted(self.defter)

    def kategoriler(self, tip: str) -> List[str]:
        return sorted(self.defter.get(str(tip), {}))

    def uzaylar(self, tip: str, kategori: str) -> List[str]:
        return sorted(self.defter.get(str(tip), {}).get(str(kategori), {}))

    def terim(self):
        return Sigma("t", Evren(0),
                     Sigma("c", Evren(0),
                           Sigma("u", Evren(0), Evren(0))))

    def unfold(self, mertebe: str = "kategori"):
        e = Cift(Dogal(), Cift(Dogal(), Cift(Dogal(), Dogal())))
        yol = {"tip": Birinci(e),
               "kategori": Birinci(Ikinci(e)),
               "uzay": Birinci(Ikinci(Ikinci(e))),
               "nokta": Ikinci(Ikinci(Ikinci(e)))}.get(mertebe)
        if yol is None:
            raise ValueError("açılacak mertebe bilinmiyor: %r" % (mertebe,))
        return geri_oku(degerlendir(yol, BOS))

    def dogrula(self) -> Dict[str, Any]:
        t = self.terim()
        n = 0
        x = t
        while isinstance(x, Sigma):
            n += 1
            x = x.hedef
        normal = geri_oku(degerlendir(t, BOS))
        derinlik = 0
        y = normal
        while isinstance(y, Sigma):
            derinlik += 1
            y = y.hedef
        return {"Σ_sayısı": n, "NbE_sonrası_Σ": derinlik,
                "defter_kademesi": 3,
                "uyuştu": bool(n == 3 and derinlik == 3)}

    def ac(self, tip: str, kategori: Optional[str] = None,
           uzay: Optional[str] = None) -> Any:
        if uzay is not None and kategori is None:
            raise ValueError(
                "silsile atlandı: uzaya kategorisiz erişilemez "
                "(nokta → uzay → kategori → tip)")
        if kategori is None:
            return self.kategoriler(tip)
        if uzay is None:
            return self.uzaylar(tip, kategori)
        return self.defter[str(tip)][str(kategori)][str(uzay)]

    def izdusum(self, ne: str = "kategori") -> Dict[str, np.ndarray]:
        out: Dict[str, List[np.ndarray]] = {}
        for t, cs in self.defter.items():
            for c, us in cs.items():
                for u, v in us.items():
                    anahtar = {"tip": t, "kategori": "%s/%s" % (t, c),
                               "uzay": "%s/%s/%s" % (t, c, u)}.get(ne)
                    if anahtar is None:
                        raise ValueError("izdüşüm kipi bilinmiyor: %r" % (ne,))
                    out.setdefault(anahtar, []).append(
                        np.asarray(v).reshape(-1))
        return {k: np.sum(np.stack(_lif_esitle(v)), axis=0)
                for k, v in out.items()}

    def kopukluk(self, ne: str = "uzay") -> Dict[str, Any]:
        izd = self.izdusum(ne)
        adres = sorted(izd)
        nokta = [np.asarray(izd[k], float).reshape(-1) for k in adres]
        if len(nokta) < 2:
            return {"kopuk": 0, "hücre": len(nokta), "nispet": 0.0,
                    "kopuk_adres": (), "sebep": "tek hücre -- münasebet yok"}
        X = np.stack(_lif_esitle(nokta))
        boy = np.maximum(np.linalg.norm(X, axis=1, keepdims=True), 1e-300)
        G = np.abs((X / boy) @ (X / boy).T)
        np.fill_diagonal(G, 0.0)
        komsu = G.max(axis=1)
        esik = float(np.mean(komsu)) * float(np.mean(komsu > 0.0))
        kopuk = [adres[i] for i in np.flatnonzero(komsu <= esik)]
        return {"kopuk": len(kopuk), "hücre": len(adres),
                "nispet": float(len(kopuk)) / float(len(adres)),
                "eşik": esik, "kopuk_adres": tuple(sorted(kopuk)[:8])}

    def hazineye(self) -> Dict[str, Any]:
        return {"defter": {t: {c: {u: [float(x) for x in
                                       np.asarray(v, float).reshape(-1)]
                                   for u, v in us.items()}
                               for c, us in cs.items()}
                           for t, cs in self.defter.items()},
                "sözlük": int(self.sozluk),
                "asansör_katı": int(self.asansor_kati),
                "uzay_mertebesi": [int(m) for m in self.uzay_mertebesi],
                "tur": int(self.tur),
                "gerçek_kategori_eşleşme": int(self.gercek_kategori_eslesme),
                "gerçek_hom_toplamı": int(self.gercek_hom_toplam)}

    @staticmethod
    def hazineden(d: Optional[Dict[str, Any]] = None) -> "Lif":
        d = dict(d or {})
        L = Lif(sozluk=int(d.get("sözlük", 0)),
                asansor_kati=int(d.get("asansör_katı", -1)),
                uzay_mertebesi=tuple(int(m) for m in
                                     d.get("uzay_mertebesi", ())),
                tur=int(d.get("tur", 0)),
                gercek_kategori_eslesme=int(d.get("gerçek_kategori_eşleşme", 0)),
                gercek_hom_toplam=int(d.get("gerçek_hom_toplamı", 0)))
        for t, cs in dict(d.get("defter") or {}).items():
            for c, us in dict(cs).items():
                for u, v in dict(us).items():
                    L.tak(t, c, u, np.asarray(list(v), float))
        return L

    def birik(self, tip: str, kategori: str, uzay: str,
             nokta: np.ndarray) -> "Lif":
        eski = self.defter.get(str(tip), {}).get(str(kategori), {}) \
                          .get(str(uzay))
        yeni = np.asarray(nokta, float).reshape(-1)
        if eski is not None:
            a, b = _lif_esitle([np.asarray(eski, float).reshape(-1), yeni])
            yeni = a + b
        return self.tak(tip, kategori, uzay, yeni)

    def sayim(self) -> Dict[str, int]:
        t = len(self.defter)
        c = {x for cs in self.defter.values() for x in cs}
        u = {x for cs in self.defter.values() for us in cs.values()
             for x in us}
        hucre = sum(len(us) for cs in self.defter.values()
                    for us in cs.values())
        kutu = t * max(len(c), 1) * max(len(u), 1)
        return {"tip": t, "kategori": len(c), "uzay": len(u),
                "lif_hücresi": hucre, "kutu_hücresi": kutu,
                "boş_kalacaktı": kutu - hucre}


def _lif_esitle(vs: List[np.ndarray]) -> List[np.ndarray]:
    n = max(v.size for v in vs)
    return [np.pad(v, (0, n - v.size)) if v.size < n else v for v in vs]


def _dinamik_mertebeler(boylar: Sequence[int]) -> Tuple[int, ...]:
    b = sorted({int(x) for x in boylar})
    assert b, "münasebet haritası için bağlam boyu BOŞ"
    n = len(b)
    return tuple(b[min(n - 1, (i * n) // 10)] for i in range(10))


def _yuva_sec(mertebeler: Sequence[int], boy: int) -> int:
    m = np.asarray(list(mertebeler), np.int64)
    return int(np.argmin(np.abs(m - int(boy))))


def harita_kur(nefs, veri, sozluk: int, silsile: Dict[str, Any],
              munasebet, onceki: Optional[Dict[str, Any]] = None) -> Lif:
    from kuantum.qegitim import ornek_bol

    veri = list(veri)
    assert veri, "silsile defteri BOŞ veriyle kurulamaz"
    n_v = int(nefs.ayar.veri_lifi)
    assert n_v >= 4, (
        "taşıyıcı tabanı %d -- silsile defteri dörtlü kıyas yapamaz" % n_v)
    M = np.asarray(munasebet.M, float)
    assert M.shape == (n_v, n_v), (
        "müşterek münasebet haritası %s, taşıyıcı tabanı %d -- tek kaynak "
        "olmalı (ferman 1-M)" % (M.shape, n_v))
    bolunmus = [ornek_bol(o) for o in veri]
    uzaylar = uzaylari_kur(
        _dinamik_mertebeler([len(b) for b, _h, _c, _m in bolunmus]))
    mertebeler = [u.mertebe for u in uzaylar]

    gercek_kat = silsile.get("turetilen_kategori_ham")
    gercek_tensor = silsile.get("qudit_tip_tensoru")
    L = Lif.hazineden(onceki)
    klon = silsile_beyani()
    for bag, _hedef, cins, _makam in bolunmus:
        dizi = [int(x) % n_v for x in bag] + [n_v - 1]
        tip = "arc" if str(cins).startswith("arc") else "sözlü"
        kategori = kaide_imzasi_uret(dizi, n_v)
        uzay = "uzay%02d" % _yuva_sec(mertebeler, len(bag))
        t = np.unique(np.asarray(dizi, np.int64))
        L.birik(tip, kategori, uzay, M[t, :].sum(axis=0))
        if gercek_kat is not None and gercek_tensor is not None:
            for nesne in t:
                if int(nesne) in gercek_tensor["liflar"]:
                    inis = tip_tensoru_asagi_in(gercek_tensor, int(nesne),
                                                gercek_kat)
                    if inis["bulundu"] and inis["hom_kurallari"]:
                        L.gercek_kategori_eslesme += 1
                        L.gercek_hom_toplam += len(inis["hom_kurallari"])
                    break
    silsile_yukle(klon)
    L.asansor_kati = int(silsile["asansör"]["kat"])
    L.sozluk = int(sozluk)
    L.uzay_mertebesi = tuple(int(m) for m in mertebeler)
    L.kategori_beyani = kategori_beyani(uzaylar)
    L.doyma = float(munasebet.doyma())
    L.islenen = int(munasebet.islenen)
    L.tur = int(L.tur) + 1
    return L


def lif_kefesi(haller: Sequence[np.ndarray],
              baglamlar: Sequence[Sequence[int]],
              cozunurluk: int = 16) -> Dict[str, Any]:
    n = min(len(haller), len(baglamlar))
    if n < 3:
        return {"kayıp": 1.0, "çift": 0, "sadakat": float("nan"),
                "sebep": "münasebet için en az üç örnek gerekir"}
    kac = min(n, max(3, int(cozunurluk)))
    sec = np.linspace(0, n - 1, kac).astype(np.int64)
    sec = np.unique(sec)
    H = np.stack(_lif_esitle([np.asarray(haller[i], complex).reshape(-1)
                             for i in sec]))
    X = np.stack(_lif_esitle([np.asarray(baglamlar[i], float).reshape(-1)
                             for i in sec]))
    H = H / np.maximum(np.linalg.norm(H, axis=1, keepdims=True), 1e-300)
    G = np.abs(H @ H.conj().T)
    D_gom = -np.log(np.maximum(G, 1e-300))
    kare = np.sum(X * X, axis=1)
    D_ham = np.sqrt(np.maximum(
        kare[:, None] + kare[None, :] - 2.0 * (X @ X.T), 0.0))
    ust = np.triu_indices(sec.size, k=1)
    h = D_ham[ust]
    g = D_gom[ust]
    if h.size < 2 or h.std() < 1e-12 or g.std() < 1e-12:
        return {"kayıp": 1.0, "çift": int(h.size), "sadakat": float("nan"),
                "örnek": int(sec.size),
                "sebep": "mesafeler ayrışmıyor -- durum örnekleri ayırmıyor"}
    sr = lambda z: np.argsort(np.argsort(z)).astype(float)
    r_s = float(np.corrcoef(sr(h), sr(g))[0, 1])
    return {"kayıp": float(1.0 - r_s), "sadakat": r_s,
            "pearson": float(np.corrcoef(h, g)[0, 1]),
            "çift": int(h.size), "örnek": int(sec.size),
            "çözünürlük": int(cozunurluk)}


def lif_beyani(lif: Lif) -> str:
    n = lif.sayim()
    k = lif.kopukluk()
    dg = lif.dogrula()
    s = ["=== SİLSİLE DEFTERİ -- MÜŞTEREK HARİTANIN TABAKALANMASI "
         "(tek motor: sonsuz_mertebeler_teorisi.py) ===", "",
         "  TEK KAYNAK (ferman 1-M): noktalar nefs/munasebet.py:Harita.M'den"
         " okunur;",
         "  bu defter o haritayı tip/kategori/uzay silsilesine ayırır, "
         "ikinci bir harita TUTMAZ.",
         "    müşterek haritanın doyması: %.4f   işlenen örnek: %d"
         % (lif.doyma, lif.islenen),
         "",
         "  silsile : nokta → uzay → kategori → tip",
         "  tip     : %s" % ", ".join(lif.tipler()),
         "  sözlük  : %d     asansör katı: %d     biriken tur: %d"
         % (lif.sozluk, lif.asansor_kati, lif.tur),
         "",
         lif.kategori_beyani,
         "",
         "  BAĞIMLI LİF vs KARTEZYEN KUTU (aynı muhteva)",
         "    tip=%d kategori=%d uzay=%d" % (n["tip"], n["kategori"],
                                             n["uzay"]),
         "    lif hücresi   : %d" % n["lif_hücresi"],
         "    kutu hücresi  : %d" % n["kutu_hücresi"],
         "    boş kalacaktı : %d" % n["boş_kalacaktı"],
         "",
         "  KOPUKLUK (ferman 1-Z: kopukluk da çelişkidir)",
         "    hücre %d, kopuk %d, nispet %.4f   (eşik %.6f -- ölçülen)"
         % (k["hücre"], k["kopuk"], k["nispet"], float(k.get("eşik", 0.0)))]
    if k.get("kopuk_adres"):
        s.append("    kopuk adresler: %s" % ", ".join(k["kopuk_adres"]))
    if k.get("sebep"):
        s.append("    sebep: %s" % k["sebep"])
    s += ["",
          "  SONSUZ MERTEBELER -- Σ zinciri ve NbE",
          "    Σ sayısı %d  (NbE sonrası %d)  defterle uyuştu: %s"
          % (dg["Σ_sayısı"], dg["NbE_sonrası_Σ"],
             "EVET" if dg["uyuştu"] else "HAYIR"),
          "    Unfold(kategori) → %s   Unfold(nokta) → %s"
          % (type(lif.unfold("kategori")).__name__,
             type(lif.unfold("nokta")).__name__),
          "",
          whnf_beyani()]
    return "\n".join(s)



PIRAMIT_TAVANI = 256


def coklu_cozunurluk_piramidi_kur(X: np.ndarray) -> List[np.ndarray]:
    x = np.asarray(X, float)
    kademeler = [x]
    while len(x) > 1:
        if len(x) % 2:
            x = np.vstack([x, x[-1:]])
        a, b = x[0::2], x[1::2]
        x = (a + b) / np.sqrt(2.0)
        kademeler.append(x)
    return kademeler


def piramit_kaba_kademe(kademeler: Sequence[np.ndarray],
                        tavan: int = PIRAMIT_TAVANI) -> int:
    for i, k in enumerate(kademeler):
        if len(k) <= tavan:
            return i
    return len(kademeler) - 1


def piramit_incelt(Y: np.ndarray, n: int, kademe: int) -> np.ndarray:
    kat = 2 ** kademe
    G = np.repeat(Y, kat, axis=0)[:n]
    if len(G) < n:
        G = np.vstack([G, np.repeat(Y[-1:], n - len(G), axis=0)])
    return G / (np.sqrt(2.0) ** kademe)


def piramit_kabalastir(X: np.ndarray, tavan: int = PIRAMIT_TAVANI
                       ) -> Tuple[np.ndarray, int, float]:
    n = len(X)
    if n <= tavan:
        return np.asarray(X, float), 0, 0.0
    kademeler = coklu_cozunurluk_piramidi_kur(X)
    i = piramit_kaba_kademe(kademeler, tavan)
    Y = kademeler[i]
    geri = piramit_incelt(Y, n, i)
    kayip = float(np.linalg.norm(geri - X) / (np.linalg.norm(X) + 1e-12))
    return Y, i, kayip
