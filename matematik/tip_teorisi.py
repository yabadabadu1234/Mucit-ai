"""TİP TEORİSİ ÇİPİ -- kübik tip teorisi, NbE ve HoTT.

KÜME 7'nin birinci karargâhı (kütük H226). On bir dosya --
``omega_kategori_nbe/`` altındaki aralik, sozdizim, terimler,
cekirdek, denklik, denetleyici, kutuphane, turetimler, geometri,
iliskiler, yazdir -- burada birleşti. Terkip üç adımda yapıldı:
(a) her dosya kendi içinde, (b) birleştirme, (c) birleşik gövdede bir
daha. Asılları ``yedek/kume7_asillari/omega_kategori_nbe/`` altında
şahittir.

**Kök problem -- NbE zorunluluğu.** İki tip teorisi sürümü vardı:
eski ``omega_kategori/`` terim seviyesinde ağaç kopyaladığı için
``π₁(S¹) ≅ ℤ`` hesabında tıkanıyor, ``omega_kategori_nbe/`` ise
kapanışlar ve ortamlarla aynı hesabı saniyenin altında bitiriyordu.
Terkipte **yalnız NbE sürümü** alındı; eski sürüm tasfiye edildi.

**İki seviye -- terkibin açığa çıkardığı asıl şey.** ``terimler.py``
ile ``cekirdek.py`` yedi ismi **aynı** yazıyordu (``uygula``,
``transp``, ``hkomp``, ``komp``, ``dolgu``, ``yol_uygula``,
``taze``); ayrı modüllerde durdukları için bu görünmüyordu. İkisi
aynı işlemin iki seviyesidir:

* **terim seviyesi** (``terim_*``) -- ikame ile, ağaç kopyalayarak.
* **değer seviyesi** (öneksiz) -- kapanışlarla, NbE ile.

NbE'nin bütün iddiası budur: değer seviyesi terim seviyesinin yerini
alır. Ön ek, o iddiayı isimde görünür kılar.

**Çipin altı odası.**

1. **Aralık cebri ve yüz kafesi** -- De Morgan aralığı ``I``
   (antizincir DNF normal formu), ``Kofibrasyon`` (yüzler), yüz
   çelişkisi denetimi.
2. **Sözdizim ve terim seviyesi** -- ``Terim`` düğümleri (Π, Σ, Path,
   Transp, Komp, HComp, Glue, ℕ, ℤ, S¹), ``terim_ikame`` ve
   ``terim_*`` işlemleri.
3. **NbE değerlendirme çekirdeği** -- ``Deger`` ve ``Kapanis``
   aileleri, ``Ortam``, ``degerlendir``/``geri_oku``/``nf``,
   ``comp``, ``transp``, ``hcomp``, ``dolgu``; tanımsal eşitlik
   normal formların karşılaştırılmasıdır.
4. **Glue ve Univalence** -- ``GlueHam``, ``denklikle_tamamla``,
   ``ua(e)`` boyunca kayıpsız taşıma, sınırda çöküş
   (``ua e@0 ≡ A``, ``ua e@1 ≡ B``) tanımsal olarak.
5. **Homotopi mertebeleri ve S¹** -- h-seviyeleri (bütün, önerme,
   küme, grupoid), döngü uzayları ``Ωⁿ``, ``dongu_kuvveti(n)`` ve
   ``sarim(donguⁿ) = n`` -- π₁(S¹) ≅ ℤ'nin tam hesabı.
6. **Sentetik diferansiyel geometri ve münasebetler** --
   sonsuz küçükler ``D = {x | x² = 0}``, teğet demeti ``TX = Xᴰ``,
   kotanjant duali, de Rham kompleksi, kritik lokus, demetler ve
   kesitler. Postulatlar **postulat olarak** işaretlidir; hesaplanmış
   gibi sunulmaz.
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import (Any, Callable, Dict, FrozenSet, Iterable, Iterator,
                    List, Optional, Sequence, Set, Tuple, Union)






# ====================================================================
#  omega_kategori_nbe/aralik.py
# ====================================================================

Literal = Tuple[str, bool]


Cumle = FrozenSet[Literal]


def _antizincire_indir(cumleler: Iterable[Cumle]) -> FrozenSet[Cumle]:
    """Yutma kanunu: ``A ∨ (A ∧ B) = A``.

    Bir cümle, başka bir cümlenin üst kümesiyse gereksizdir (daha zayıftır)
    ve atılır. Geriye kapsama sıralamasına göre bir ANTİZİNCİR kalır; bu,
    serbest dağılmalı kafesin kanonik normal formudur.

    Hız: bu fonksiyon çekirdeğin en sıcak noktasıdır (ölçüldü). Uzunluğa
    göre sıralanınca her hakiki alt küme DAHA ÖNCE gelir, dolayısıyla
    yalnız önek taranır; eşit uzunlukta iki farklı cümle birbirinin alt
    kümesi olamaz.
    """
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
    """Serbest De Morgan cebrinin bir elemanı; DNF (cümlelerin birleşimi)."""

    __slots__ = ("cumleler",)

    def __init__(self, cumleler: Iterable[Cumle]) -> None:
        self.cumleler: FrozenSet[Cumle] = _antizincire_indir(cumleler)

    # ---- kurucular -----------------------------------------------------
    @staticmethod
    def degisken(ad: str) -> "Aralik":
        return Aralik([frozenset({(ad, True)})])

    @staticmethod
    def _literal(ad: str, pozitif: bool) -> "Aralik":
        return Aralik([frozenset({(ad, pozitif)})])

    # ---- kafes işlemleri ------------------------------------------------
    def ve(self, obur: "Aralik") -> "Aralik":
        """Meet (∧). Dağıtarak DNF'de kalır."""
        return Aralik(a | b for a in self.cumleler for b in obur.cumleler)

    def veya(self, obur: "Aralik") -> "Aralik":
        """Join (∨)."""
        return Aralik(self.cumleler | obur.cumleler)

    def degil(self) -> "Aralik":
        """De Morgan involüsyonu (~). ``~(⋁ᵢ ⋀ⱼ lᵢⱼ) = ⋀ᵢ ⋁ⱼ ~lᵢⱼ``."""
        sonuc = BIR
        for cumle in self.cumleler:
            if not cumle:          # boş çarpım = 1  =>  ~1 = 0
                return SIFIR
            ayrik = SIFIR
            for (ad, pozitif) in cumle:
                ayrik = ayrik.veya(Aralik._literal(ad, not pozitif))
            sonuc = sonuc.ve(ayrik)
        return sonuc               # boş birleşim = 0  =>  ~0 = 1

    # ---- yerine koyma ---------------------------------------------------
    def yerine_koy(self, atama: Dict[str, "Aralik"]) -> "Aralik":
        """``i ↦ r`` aralık ikamesi. Değişkenler eşzamanlı değiştirilir."""
        # erken çıkış: ikame bu ifadeye hiç dokunmuyorsa kopya üretme
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

    # ---- tanıma ---------------------------------------------------------
    def sifir_mi(self) -> bool:
        return len(self.cumleler) == 0

    def bir_mi(self) -> bool:
        return frozenset() in self.cumleler

    # ---- protokol -------------------------------------------------------
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


SIFIR = Aralik([])                    # 0  (boş birleşim)


BIR = Aralik([frozenset()])           # 1  (boş çarpım içeren birleşim)


Yuz = FrozenSet[Tuple[str, bool]]


def _yuz_celiskili_mi(yuz: Yuz) -> bool:
    gorulen: Dict[str, bool] = {}
    for (ad, deger) in yuz:
        if ad in gorulen and gorulen[ad] != deger:
            return True
        gorulen[ad] = deger
    return False


class Kofibrasyon:
    """Yüz kafesinin bir elemanı: yüzlerin (conjunctive face) birleşimi."""

    __slots__ = ("yuzler",)

    def __init__(self, yuzler: Iterable[Yuz]) -> None:
        temiz = [frozenset(y) for y in yuzler if not _yuz_celiskili_mi(frozenset(y))]
        self.yuzler: FrozenSet[Yuz] = _antizincire_indir(temiz)

    # ---- kurucular -----------------------------------------------------
    @staticmethod
    def atom(ad: str, deger: bool) -> "Kofibrasyon":
        """``(ad = 1)`` eğer deger True ise, aksi hâlde ``(ad = 0)``."""
        return Kofibrasyon([frozenset({(ad, deger)})])

    # ---- kafes işlemleri ------------------------------------------------
    def ve(self, obur: "Kofibrasyon") -> "Kofibrasyon":
        return Kofibrasyon(a | b for a in self.yuzler for b in obur.yuzler)

    def veya(self, obur: "Kofibrasyon") -> "Kofibrasyon":
        return Kofibrasyon(self.yuzler | obur.yuzler)

    # ---- tanıma ---------------------------------------------------------
    def bos_mu(self) -> bool:
        """⊥ mü? (hiçbir yüzde sağlanmıyor)"""
        return len(self.yuzler) == 0

    def dogru_mu(self) -> bool:
        """⊤ mü? (her yerde sağlanıyor)"""
        return frozenset() in self.yuzler

    def kapsiyor_mu(self, yuz: Yuz) -> bool:
        """Verilen yüz üzerinde bu kofibrasyon sağlanıyor mu?

        Yüz bir "kısıt bağlamı"dır; kofibrasyonun cümlelerinden biri onun
        alt kümesiyse (yani o cümlenin şartları zaten dayatılmışsa) sağlanır.
        """
        yuz = frozenset(yuz)
        return any(c <= yuz for c in self.yuzler)

    def yerine_koy(self, atama: Dict[str, Aralik]) -> "Kofibrasyon":
        """Yüzlere aralık ikamesi uygular; ``(i=ε)[i↦r]`` = ``(r=ε)``."""
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


YANLIS = Kofibrasyon([])              # ⊥


DOGRU = Kofibrasyon([frozenset()])    # ⊤


def aralik_esitligi(r: Aralik, deger: bool) -> Kofibrasyon:
    """Aralık kafesinden yüz kafesine köprü: ``(r = deger)`` şartı.

    ``r = ⋁ₖ ⋀ₗ lit`` olmak üzere:
      * ``r = 1``  ⟺  ⋁ₖ ⋀ₗ (lit = 1)
      * ``r = 0``  ⟺  ⋀ₖ ⋁ₗ (lit = 0)
    ve ``(i = 1) = atom(i, True)``, ``(~i = 1) = atom(i, False)``.
    """
    if deger:  # r = 1
        sonuc = YANLIS
        for cumle in r.cumleler:
            carpim = DOGRU
            for (ad, pozitif) in cumle:
                carpim = carpim.ve(Kofibrasyon.atom(ad, pozitif))
            sonuc = sonuc.veya(carpim)
        return sonuc
    # r = 0
    sonuc = DOGRU
    for cumle in r.cumleler:
        ayrik = YANLIS
        for (ad, pozitif) in cumle:
            ayrik = ayrik.veya(Kofibrasyon.atom(ad, not pozitif))
        sonuc = sonuc.ve(ayrik)
    return sonuc


def yuzu_atamaya_cevir(yuz: Yuz) -> Dict[str, Aralik]:
    """Bir yüzü, aralık değişkenleri için somut bir ikameye çevirir."""
    return {ad: (BIR if deger else SIFIR) for (ad, deger) in yuz}


# ====================================================================
#  omega_kategori_nbe/sozdizim.py
# ====================================================================

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
        try:
            return terimi_yaz(self)  # type: ignore[arg-type]
        except Exception:
            return "%s(%s)" % (type(self).__name__,
                               ", ".join(repr(a) for a in self._alanlar()))


class Terim(Dugum):
    __slots__ = ()


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


# ====================================================================
#  omega_kategori_nbe/terimler.py
# ====================================================================

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
                          Taban, Sfr)):
            return
        if isinstance(t, Dongu):
            g.update(t.r.degiskenler() - bagli); return
        if isinstance(t, YolUygula):
            yur(t.yol, bagli); g.update(t.r.degiskenler() - bagli); return
        if isinstance(t, YolLam):
            yur(t.govde, bagli | {t.ad}); return
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
                      Taban, Sfr)):
        return t
    if isinstance(t, Dongu):
        r = t.r.yerine_koy(sigma)
        return Taban() if (r.sifir_mi() or r.bir_mi()) else Dongu(r)
    if isinstance(t, YolUygula):
        return terim_yol_uygula(f(t.yol), t.r.yerine_koy(sigma))
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
    raise TypeError("ara_ikame: bilinmeyen terim %r" % (t,))


def ikame(t: Terim, sigma: Dict[str, Terim]) -> Terim:
    if not sigma:
        return t
    f = lambda x: ikame(x, sigma)
    if isinstance(t, Deg):
        return sigma.get(t.ad, t)
    if isinstance(t, (Evren, Dogal, Tamsayi, Cember, Taban,
                      Sfr, Dongu)):
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
    """``fill^ad`` -- ``ad`` serbest kalır; ``fill@0 = u0``, ``fill@1 = comp``."""
    j = terim_taze("j")
    ikj = {ad: Aralik.degisken(ad).ve(Aralik.degisken(j))}
    yeni_dallar = list(_dallar_ara_ikame(dallar, ikj,
                                         lambda g: ara_ikame(g, ikj)))
    yeni_dallar.append((yuz(**{ad: 0}), u0))
    return terim_komp(j, ara_ikame(cizgi, ikj), yeni_dallar, u0)


# ====================================================================
#  omega_kategori_nbe/cekirdek.py
# ====================================================================

_sayac = itertools.count()


def taze(taban: str = "x") -> str:
    return "%s!%d" % (taban.split("!")[0], next(_sayac))


class CekirdekHatasi(Exception):
    pass


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
        return deger_dongu(self.r.yerine_koy(s))


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


def _sabit_mi(L: ACizgi) -> bool:
    """MUHAFAZAKÂR sabitlik sınaması: yalnız ispatlanabildiğinde True.

    DİKKAT: ``L(0) == L(1)`` sınaması SAĞLAM DEĞİLDİR (``ua e`` tuzağı);
    burada asla kullanılmaz.
    """
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
        return komp_evren(L, sistem, u0)

    if isinstance(A, DYapistir):
        return komp_yapistir(L, sistem, u0)

    return notr(NKomp(L, sistem, u0), L.uygula(BIR))


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
    raise CekirdekHatasi("değerlendirilemeyen terim: %r" % (t,))


def _tv(k: int) -> str:
    return "#%d" % k


def _iv(k: int) -> str:
    return "%%%d" % k


def _ivar(k: int) -> Aralik:
    return Aralik.degisken(_iv(k))


def geri_oku(d: Deger, k: int = 0) -> Terim:
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
    return False


def esdeger_mi(a: Terim, b: Terim,
               baglam: Optional[Dict[str, Terim]] = None) -> bool:
    o = ortam_kur(baglam)
    return _esit(geri_oku(degerlendir(a, o), 0),
                 geri_oku(degerlendir(b, o), 0))


def deger_esit_mi(d1: Deger, d2: Deger, k: int = 0) -> bool:
    return _esit(geri_oku(d1, k), geri_oku(d2, k), k)


# ====================================================================
#  omega_kategori_nbe/kutuphane.py
# ====================================================================

U = Evren(0)


U1 = Evren(1)


def _t(ad: str) -> Terim:
    return Deg(ad)


def refl(a: Terim) -> Terim:
    """``refl a : Path A a a``"""
    return YolLam("_", a)


def ters(A: Terim, a: Terim, b: Terim, p: Terim) -> Terim:
    """``p⁻¹ : Path A b a``"""
    i, j = terim_taze("i"), terim_taze("j")
    return YolLam(i, HKomp(A, j,
        [(yuz(**{i: 0}), terim_yol_uygula(p, Aralik.degisken(j))),
         (yuz(**{i: 1}), a)], a))


def terkip(A: Terim, a: Terim, b: Terim, c: Terim,
           p: Terim, q: Terim) -> Terim:
    """``p ∙ q : Path A a c``"""
    i, j = terim_taze("i"), terim_taze("j")
    return YolLam(i, HKomp(A, j,
        [(yuz(**{i: 0}), a),
         (yuz(**{i: 1}), terim_yol_uygula(q, Aralik.degisken(j)))],
        terim_yol_uygula(p, Aralik.degisken(i))))


def esle(A: Terim, B: Terim, f: Terim, a: Terim, b: Terim, p: Terim) -> Terim:
    """``ap f p : Path B (f a) (f b)``"""
    i = terim_taze("i")
    return YolLam(i, Uygula(f, terim_yol_uygula(p, Aralik.degisken(i))))


def tasi(P: Terim, x: Terim) -> Terim:
    """``transport : Path U A B → A → B``  (``P`` bir tip yoludur)"""
    i = terim_taze("i")
    return Transp(i, terim_yol_uygula(P, Aralik.degisken(i)), YANLIS, x)


def aile_tasi(C: Terim, p: Terim, x: Terim) -> Terim:
    """``C : A → U`` ailesinde ``p : Path A a b`` boyunca taşıma."""
    i = terim_taze("i")
    return Transp(i, Uygula(C, terim_yol_uygula(p, Aralik.degisken(i))),
                    YANLIS, x)


def yol_tumevarimi(A: Terim, a: Terim, C: Terim, d: Terim,
                   b: Terim, p: Terim) -> Terim:
    """J: ``C : (b:A) → Path A a b → U`` ve ``d : C a (refl a)`` verildiğinde
    ``J A a C d b p : C b p``.

    Kübik ispat: ``transp^i (C (p@i) (<j> p@(i∧j))) ⊥ d``.
    """
    i, j = terim_taze("i"), terim_taze("j")
    i_ar, j_ar = Aralik.degisken(i), Aralik.degisken(j)
    kismi_yol = YolLam(j, terim_yol_uygula(p, i_ar.ve(j_ar)))
    cizgi = Uygula(Uygula(C, terim_yol_uygula(p, i_ar)), kismi_yol)
    return Transp(i, cizgi, YANLIS, d)


def kac_mertebeden(X: Terim, n: int = -2) -> Terim:
    """BU TİP KAÇ MERTEBEDEN -- **tek terkip** (kütük H226).

    Küme: ``iz_butun``, ``iz_onerme``, ``iz_kume``, ``iz_grupoid``,
    ``n_mertebe``. Beş isim **tek merdivenin** basamaklarıydı ve
    merdiven zâten ``n_mertebe``nin içinde yazılıydı:

        ``h_{-2}(X) = Σ(x:X). Π(y:X). Path X x y``   (büzülebilir)
        ``h_{n}(X) = Π(x y : X). h_{n-1}(Path X x y)``

    ==========  ====================  ==============================
    ``n``       halkça                eski isim
    ==========  ====================  ==============================
    ``-2``      büzülebilir           ``iz_butun``
    ``-1``      önerme                ``iz_onerme``
    ``0``       küme                  ``iz_kume``
    ``1``       grupoid               ``iz_grupoid``
    ``n``       ``n``-tip             ``n_mertebe``
    ==========  ====================  ==============================

    ``iz_onerme``in ayrı yazılması gerekiyordu, zira özyineleme
    ``-1``de durur: ``h_{-1}(X) = Π(x y). Path X x y`` -- burada
    ``h_{-2}``ye inilmez, aksi hâlde her önerme büzülebilir çıkardı.
    Ayrı isimlerde bu **durak** görünmüyordu; şimdi tek dalda duruyor.
    """
    if n <= -2:
        x, y = terim_taze("x"), terim_taze("y")
        return Sigma(x, X, Pi(y, X, yol(X, _t(x), _t(y))))
    x, y = terim_taze("x"), terim_taze("y")
    ic = yol(X, _t(x), _t(y))
    return Pi(x, X, Pi(y, X, ic if n == -1 else kac_mertebeden(ic, n - 1)))


def dongu_uzayi(A: Terim, a: Terim) -> Terim:
    """``Ω(A,a) = Path A a a``"""
    return yol(A, a, a)


def dongu_uzayi_n(A: Terim, a: Terim, n: int) -> Terim:
    """``Ωⁿ(A,a)`` -- yineli döngü uzayı."""
    if n <= 0:
        return A
    if n == 1:
        return dongu_uzayi(A, a)
    alt = dongu_uzayi_n(A, a, n - 1)
    return yol(alt, refl_n(A, a, n - 1), refl_n(A, a, n - 1))


def refl_n(A: Terim, a: Terim, n: int) -> Terim:
    """``Ωⁿ``nin taban noktası (yineli refl)."""
    nokta = a
    for _ in range(n):
        nokta = refl(nokta)
    return nokta


def lif(A: Terim, B: Terim, f: Terim, b: Terim) -> Terim:
    """``fiber f b = Σ (a:A). Path B (f a) b``"""
    a = terim_taze("a")
    return Sigma(a, A, yol(B, Uygula(f, _t(a)), b))


def iz_denklik(A: Terim, B: Terim, f: Terim) -> Terim:
    """``isEquiv f = Π (b:B). isContr (fiber f b)``"""
    b = terim_taze("b")
    return Pi(b, B, kac_mertebeden(lif(A, B, f, _t(b)), -2))


def denklik_tipi(A: Terim, B: Terim) -> Terim:
    """``Equiv A B = Σ (f : A → B). isEquiv f``"""
    f = terim_taze("f")
    return Sigma(f, ok(A, B), iz_denklik(A, B, _t(f)))


def ozdeslik_denkligi(A: Terim) -> Terim:
    """``idEquiv A : Equiv A A``

    Büzülebilirlik ispatı, tekil-lif büzülmesinin kübik hâlidir:
    ``<i> ( z.2 @ ~i , <j> z.2 @ (~i ∨ j) )``.
    """
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
    """``ua e : Path U A B``

    ``ua e = <i> Glue B [ (i=0) ↦ (A, e), (i=1) ↦ (B, idEquiv B) ]``

    Uçlarda Glue çöker: ``ua e @ 0 = A``, ``ua e @ 1 = B`` (tanımsal).
    """
    i = terim_taze("i")
    return YolLam(i, Yapistir(B, [
        (yuz(**{i: 0}), A, e),
        (yuz(**{i: 1}), B, ozdeslik_denkligi(B)),
    ]))


def cember_rec(hedef: Terim, taban_dali: Terim, dongu_dali_ad: str,
               dongu_dali: Terim, nokta: Terim) -> Terim:
    """Bağımsız (non-dependent) S¹ özyinelemesi."""
    return CemberInd("_", hedef, taban_dali, dongu_dali_ad, dongu_dali, nokta)


def dongu() -> Terim:
    """``dongu : Path S¹ taban taban``"""
    i = terim_taze("i")
    return YolLam(i, Dongu(Aralik.degisken(i)))


def dongu_tersi() -> Terim:
    """``dongu⁻¹ = <i> dongu(~i)`` -- S¹'in KENDİ simetrisi.

    Genel ``ters`` (yol tersleme) bir ``hcomp`` kurar; S¹ döngüsünde ise
    aralık involüsyonu ``~i`` doğrudan ters yolu verir. İkisi de aynı tipin
    sakinidir ve tip denetiminden geçer, fakat sade olan iç içe hcomp
    doğurmadığı için sarım hesabını ÖLÇÜLEN biçimde 245 kat hızlandırır
    (dongu⁻⁵: 27.4 s → 0.11 s).
    """
    i = terim_taze("i")
    return YolLam(i, Dongu(Aralik.degisken(i).degil()))


def dongu_kuvveti(n: int) -> Terim:
    """``dongu`` yolunun ``n`` kez terkibi (n<0 ise ``dongu⁻¹`` ile)."""
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
    """Aynı yol, fakat GENEL ``ters`` ile kurulmuş hâli.

    Yalnız kıyas ve sağlama için tutulur: iki inşanın da aynı sarım
    sayısını vermesi, sadeleştirmenin doğruluğunun sınamasıdır.
    """
    A, a = Cember(), Taban()
    if n == 0:
        return refl(a)
    tek = dongu() if n > 0 else ters(A, a, a, dongu())
    sonuc = tek
    for _ in range(abs(n) - 1):
        sonuc = terkip(A, a, a, a, sonuc, tek)
    return sonuc


def ardil_z() -> Terim:
    """``sucZ : ℤ → ℤ``"""
    n = terim_taze("n")
    m = terim_taze("m")
    # poz k        ↦ poz (k+1)
    # negArd 0     ↦ poz 0
    # negArd (k+1) ↦ negArd k
    neg_dali = DogalInd("_", Tamsayi(), Poz(Sfr()),
                          m, "_r", NegArd(_t(m)), _t(n))
    return Lam("z", TamsayiInd("_", Tamsayi(),
                                   n, Poz(Ard(_t(n))),
                                   n, neg_dali,
                                   _t("z")))


def oncel_z() -> Terim:
    """``predZ : ℤ → ℤ``"""
    n = terim_taze("n")
    m = terim_taze("m")
    # poz 0     ↦ negArd 0
    # poz (k+1) ↦ poz k
    # negArd k  ↦ negArd (k+1)
    poz_dali = DogalInd("_", Tamsayi(), NegArd(Sfr()),
                          m, "_r", Poz(_t(m)), _t(n))
    return Lam("z", TamsayiInd("_", Tamsayi(),
                                   n, poz_dali,
                                   n, NegArd(Ard(_t(n))),
                                   _t("z")))


def izo_denklige(A: Terim, B: Terim, f: Terim, g: Terim,
                 s: Terim, t: Terim) -> Terim:
    """``f : A→B``, ``g : B→A``, ``s : Π b. f(g b) ≡ b``,
    ``t : Π a. g(f a) ≡ a`` verildiğinde ``Denklik A B``.

    Lifin büzülebilirliği, iki lif elemanını birleştiren bir kare (``sq``)
    ve onun ``s`` ile ``B``ye taşınmışı (``sq1``) üzerinden kurulur; bu,
    yarı-eşlenik (half-adjoint) düzeltmesinin kübik hâlidir.
    """
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

    p_yol = YolLam(i, at(fill2, I, BIR))          # p : Path A x0 x1

    sq = HKomp(A, k,
        [(yuz(**{i: 1}), at(fill1, J, Kk.degil())),
         (yuz(**{i: 0}), at(fill0, J, Kk.degil())),
         (yuz(**{j: 0}), gy),
         (yuz(**{j: 1}), terim_yol_uygula(uy(t, at(fill2, I, BIR)),
                                        Kk.degil()))],
        at(fill2, I, J))                             # i, j serbest

    # sq'nun j yönü p0/p1'e göre TERSİNEDİR: fill1 j (~k) ucu g(p1 @ ~j)
    # verir. Bu yüzden sq1'in i-dallarında p @ ~j, ve j=0/j=1 dalları
    # (g y / f (p i)) sırasıyla yer alır.
    sq1 = HKomp(B, k,
        [(yuz(**{i: 1}), terim_yol_uygula(uy(s, terim_yol_uygula(P1, J.degil())),
                                        Kk)),
         (yuz(**{i: 0}), terim_yol_uygula(uy(s, terim_yol_uygula(P0, J.degil())),
                                        Kk)),
         (yuz(**{j: 0}), terim_yol_uygula(uy(s, Y), Kk)),
         (yuz(**{j: 1}), terim_yol_uygula(uy(s, uy(f, terim_yol_uygula(p_yol, I))),
                                        Kk))],
        uy(f, sq))                                   # i, j serbest

    lem = YolLam(i, Cift(
        terim_yol_uygula(p_yol, I),
        YolLam(j, ara_ikame(sq1, {j: J.degil()}))))

    # isEquiv f : Π (y:B). isContr (fiber f y)
    merkez = Cift(gy, uy(s, Y))
    buzme = Lam(z, ikame(lem, {x0: gy, p0: uy(s, Y),
                                   x1: Birinci(_t(z)),
                                   p1: Ikinci(_t(z))}))
    return Cift(f, Lam(y, Cift(merkez, buzme)))


def _z_yol_ispati(dis_govde, ic_sfr, ic_ard, neg_govde) -> Terim:
    """ℤ tümevarımı + poz dalında ℕ tümevarımı ile yol ispatı iskeleti."""
    Z = Tamsayi()
    z, n, m = terim_taze("z"), terim_taze("n"), terim_taze("m")
    poz_dali = DogalInd(m, dis_govde(Poz(_t(m))), ic_sfr,
                          m, "_r", ic_ard(_t(m)), _t(n))
    return Lam("w", TamsayiInd(z, dis_govde(_t(z)),
                                   n, poz_dali,
                                   n, neg_govde(_t(n)),
                                   _t("w")))


def ardil_oncel() -> Terim:
    """``Π b:ℤ. sucZ (predZ b) ≡ b`` -- her hâlde refl ile kapanır."""
    Z = Tamsayi()
    suc, pred = ardil_z(), oncel_z()
    ifade = lambda w: yol(Z, terim_uygula(suc, terim_uygula(pred, w)), w)
    return _z_yol_ispati(
        ifade,
        refl(Poz(Sfr())),
        lambda m: refl(Poz(Ard(m))),
        lambda n: refl(NegArd(n)))


def oncel_ardil() -> Terim:
    """``Π a:ℤ. predZ (sucZ a) ≡ a``"""
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
    """``sucEquiv : Denklik ℤ ℤ``"""
    Z = Tamsayi()
    return izo_denklige(Z, Z, ardil_z(), oncel_z(),
                        ardil_oncel(), oncel_ardil())


def sarmal(nokta: Terim) -> Terim:
    """``helix : S¹ → U``;  ``taban ↦ ℤ``,  ``dongu ↦ ua sucEquiv``."""
    Z = Tamsayi()
    i = terim_taze("i")
    govde = Yapistir(Z, [
        (yuz(**{i: 0}), Z, ardil_denkligi()),
        (yuz(**{i: 1}), Z, ozdeslik_denkligi(Z)),
    ])
    return CemberInd("_", U, Z, i, govde, nokta)


def sarim(p: Terim) -> Terim:
    """``sarim : (Path S¹ taban taban) → ℤ`` -- sarım sayısı."""
    i = terim_taze("i")
    cizgi = sarmal(terim_yol_uygula(p, Aralik.degisken(i)))
    return Transp(i, cizgi, YANLIS, Poz(Sfr()))


# ====================================================================
#  omega_kategori_nbe/denklik.py
# ====================================================================

class EksikKural(NotImplementedError):
    pass


_A0, _AR, _AA, _BB, _FF, _BSC = (Deg("!A0"), Deg("!Ar"), Deg("!A"),
                                 Deg("!B"), Deg("!f"), Deg("!b"))


_DENKLIK_T = denklik_tipi(_A0, _AR)


_IDEQ_T = ozdeslik_denkligi(_A0)


_LIF_T = lif(_AA, _BB, _FF, _BSC)


class GlueHam:
    """Glue'nun HAM bileşenleri.

    ``DYapistir`` değeri ``act`` altında bir yüz ⊤ olunca ``T``ye ÇÖKER;
    hesabın ortasında taban ve dalların kaybolmaması için ham hâlleri
    ayrıca taşınır.
    """

    __slots__ = ("taban", "dallar")

    def __init__(self, taban, dallar) -> None:
        self.taban, self.dallar = taban, tuple(dallar)

    def act(self, s) -> "GlueHam":
        return GlueHam(self.taban.act(s), _dallari_act(self.dallar, s))


def her_i_icin(kof: Kofibrasyon, ad: str) -> Kofibrasyon:
    """``∀ad. kof`` -- ``ad``i kısıtlamayan yüzlerin birleşimi."""
    return Kofibrasyon([y for y in kof.yuzler
                        if all(a != ad for (a, _) in y)])


def _denklik_cizgi(al, r):
    c0, hat = al
    return degerlendir(_DENKLIK_T,
                       BOS.genislet("!A0", c0).genislet("!Ar", hat.uygula(r)))


def cizgi_denkligi(hat: ACizgi) -> Deger:
    """``Denklik hat(0) hat(1)``.

    Özdeşlik denkliğini ``Denklik hat(0) hat(r)`` çizgisi boyunca taşır;
    yalnız Σ/Π/Path'te ``transp`` gerektirir.
    """
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
    """``e : Denklik A B``, ``b : B`` ve kısmî lif elemanı → tam lif elemanı."""
    X = degerlendir(_LIF_T, BOS.genislet("!A", A).genislet("!B", B)
                    .genislet("!f", bir(e)).genislet("!b", b))
    buzuk = uygula(iki(e), b)
    return hkomp(X, Sistem([(y, ATuretilmis(_buzme_c, (iki(buzuk), v)))
                            for (y, v) in kismi]), bir(buzuk))


def _act_cizgi(al, r):
    """``λr. deger.act({ad: r})``"""
    d, ad = al
    return d.act({ad: r})


def _uyg_bir_c(al, r):
    """``λr. (e(r)).1 (c(r))``"""
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
    Ai = hat.uygula(Aralik.degisken(i))          # DYapistir (yüzler i içerebilir)
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

        # (a) ψ üzerinde: (b(1), refl a'1)
        for (yp, c) in sistem:
            k = Kofibrasyon([yp]).yerine_koy(sig)
            if k.bos_mu():
                continue
            for yf in k.yuzler:
                sg = dict(sig)
                sg.update(yuzu_atamaya_cevir(yf))
                kismi.append((yf, DCift(c.uygula(BIR).act(sg),
                                          DYolLam(ASabit(ap1.act(sg))))))

        # (b) δ üzerinde: (t'1, ω)
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


# ====================================================================
#  omega_kategori_nbe/denetleyici.py
# ====================================================================

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
    """Çizgi NORMAL FORMDA sabit mi? (uçların eşitliğine BAKILMAZ)"""
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
        # dongu_dali'nin UÇLARI taban_dalının DEĞERİdir, tipi değil
        tbd = g.d(t.taban_dali)
        cizgi = ikame(t.hedef,
                         {t.ad: Dongu(Aralik.degisken(t.i_ad))})
        denetle(YolLam(t.i_ad, t.dongu_dali),
                DYolP(ASoz(t.i_ad, cizgi, g.ortam), tbd, tbd), g)
        return motif.uygula(g.d(t.nokta))

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
    """``denetle`` ama beklenen tip TERİM olarak verilir."""
    denetle(t, g.d(tip_terim), g)


def _genislet_t(self: Baglam, ad: str, tip_terim: Terim) -> Baglam:
    return self.genislet(ad, self.d(tip_terim))


Baglam.genislet_t = _genislet_t   # type: ignore[attr-defined]


# ====================================================================
#  omega_kategori_nbe/turetimler.py
# ====================================================================

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
    """``A`` içindeki ``n``-morfizmlerin tipi (serbest uçlarla).

    ``n=0`` → ``A``;  ``n=1`` → ``Π x y. Path A x y``;
    ``n=2`` → ``Π x y. Π p q. Path (Path A x y) p q`` ...
    """
    if n <= 0:
        return A
    x, y = terim_taze("x"), terim_taze("y")
    return Pi(x, A, Pi(y, A, morfizm_tipi(yol(A, D(x), D(y)), n - 1)))


def morfizm_uzayi(A: Terim, x: Terim, y: Terim, n: int) -> Terim:
    """``x`` ile ``y`` arasındaki ``n``-morfizm uzayı (n≥1)."""
    if n <= 1:
        return yol(A, x, y)
    raise ValueError("n≥2 için uçları da vermek gerekir; morfizm_tipi kullanın")


def koherens_tipi(A: Terim, n: int) -> Terim:
    """``n``-boyutlu koherensin tipi: ``Ωⁿ``nin bir üst mertebesi.

    "Katı eşitlik değil, bir üst mertebedeki morfizmle eşdeğerlik" iddiası
    tam olarak bu tipin sakinleriyle ifade edilir.
    """
    return morfizm_tipi(A, n + 1)


def kume_tipi() -> Terim:
    """``Küme = Σ (X : U). isSet X`` -- klasik küme kavramı buradan doğar."""
    X = terim_taze("X")
    return Sigma(X, U, kac_mertebeden(D(X), 0))


def onerme_tipi() -> Terim:
    """``Önerme = Σ (X : U). isProp X``"""
    X = terim_taze("X")
    return Sigma(X, U, kac_mertebeden(D(X), -1))


def grupoid_tipi() -> Terim:
    """``Grupoid = Σ (X : U). isGroupoid X``"""
    X = terim_taze("X")
    return Sigma(X, U, kac_mertebeden(D(X), 1))


def n_tip_tipi(n: int) -> Terim:
    """``n``-tiplerin tipi: ``Σ (X:U). n-mertebe X``."""
    X = terim_taze("X")
    return Sigma(X, U, kac_mertebeden(D(X), n))


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
        ("kume", kac_mertebeden(X, 0)),
        ("EksikKural", X),
        ("m", ok(X, ok(X, X))),
        ("birlesme", birlesme),
        ("sol_birim", sol_birim),
    ], sag_birim)


def grup_tipi() -> Terim:
    """Grup: küme + birim + çarpma + ters + kanunlar.

    Kanunlar YOL olarak ifade edilir; küme şartı (0-mertebe) bu yolların
    tekil olmasını, yani klasik cebirdeki "denklem" davranışını sağlar.
    """
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
        ("kume", kac_mertebeden(X, 0)),
        ("EksikKural", X),
        ("m", ok(X, ok(X, X))),
        ("iv", ok(X, X)),
        ("birlesme", birlesme),
        ("sol_birim", sol_birim),
        ("sag_birim", sag_birim),
        ("sol_ters", sol_ters),
    ], sag_ters)


def halka_tipi() -> Terim:
    """Değişmeli halka: toplama grubu + çarpma monoidi + dağılma."""
    X = D("X")
    sf, bir = D("sifir"), D("bir")
    top, carp, eks = D("top"), D("carp"), D("eks")
    x, y, z = D("x"), D("y"), D("z")
    P3 = lambda govde: Pi("x", X, Pi("y", X, Pi("z", X, govde)))
    P1 = lambda govde: Pi("x", X, govde)
    P2 = lambda govde: Pi("x", X, Pi("y", X, govde))
    return sigma_hepsi([
        ("X", U),
        ("kume", kac_mertebeden(X, 0)),
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
    """1-kategori: nesneler + küme-değerli hom + birim + bileşke + kanunlar."""
    Ob, Hom, bir, bil = D("Ob"), D("Hom"), D("bir"), D("bil")
    a, b, c, d = D("a"), D("b"), D("c"), D("d")
    H = lambda u, v: _ikili(Hom, u, v)
    B = lambda u, v, w, f, g: Uygula(Uygula(
        Uygula(Uygula(Uygula(bil, u), v), w), f), g)
    Pab = lambda govde: Pi("a", Ob, Pi("b", Ob, govde))
    hom_kume = Pab(kac_mertebeden(H(a, b), 0))
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
    """``n``-derinlikli globüler tip:

    ``Glob(0) = U``,  ``Glob(k+1) = Σ (Ob : U). (Ob → Ob → Glob(k))``.

    ``n → ∞`` limiti (∞,∞)-kategorinin altında yatan globüler kümedir.
    Sonlu her kesimi burada TEŞKİL EDİLİR ve tip denetiminden geçer;
    limit, sonlu kesimlerin kulesi olarak alınır.
    """
    if n <= 0:
        return U1 if False else U
    Ob = terim_taze("Ob")
    return Sigma(Ob, U, ok(D(Ob), ok(D(Ob), globuler_tip(n - 1))))


def omega_grupoid_kulesi(A: Terim, n: int) -> List[Tuple[int, Terim]]:
    """``A``nın ∞-grupoid kulesinin ilk ``n`` katı: ``(k, k-morfizm tipi)``."""
    return [(k, morfizm_tipi(A, k)) for k in range(n + 1)]


def cember_bilgisi() -> Dict[str, Terim]:
    """S¹: bu çekirdekte TAM olarak imâl edilmiş yegâne HIT.

    Poincaré homotopi hipotezine göre ∞-grupoidler ile topolojik uzaylar
    aynı şeydir; S¹ bunun en küçük ehemmiyetli misalidir.
    """
    S1 = Cember()
    return {
        "uzay": S1,
        "taban": Taban(),
        "dongu": dongu(),
        "Omega": dongu_uzayi(S1, Taban()),
        "Omega2": dongu_uzayi_n(S1, Taban(), 2),
    }


class Postulat:
    """Nesne dilinde İSPATLANMAYAN, aksiyom olarak eklenen sakin.

    Tipi yine de tip denetiminden geçirilir; yani "iyi teşkil edilmiş
    aksiyom" olduğu makine ile doğrulanır. İspatı yoktur.
    """

    __slots__ = ("ad", "tip", "izah")

    def __init__(self, ad: str, tip: Terim, izah: str) -> None:
        self.ad, self.tip, self.izah = ad, tip, izah

    def __repr__(self) -> str:
        return "Postulat(%s)" % self.ad


def sdg_postulatlari() -> List[Postulat]:
    """Sentetik diferansiyel geometrinin (Kock-Lawvere) çekirdek aksiyomları.

    Bunlar POSTULATTIR: hiçbir kübik çekirdek -- bu modül dâhil, Cubical
    Agda dâhil -- pürüzsüz ∞-toposu HESAPLAYAN bir indirgeyici vermez.
    Burada yapılan, aksiyomların TİPLERİNİ makine ile denetlemektir.
    """
    R = D("R")
    hR = D("halka_R")
    # halka_R : bir halka yapısı; R onun taşıyıcısı olsun diye
    # bileşenlerine erişimi kolaylaştıran kısayollar:
    carp = D("carp_R")
    top = D("top_R")
    sf = D("sifir_R")
    d, x, ff, aa, bb = D("d"), D("x"), D("f"), D("a"), D("b")

    # D = Σ (x : R). Path R (x·x) 0   -- birinci mertebeden sonsuz küçükler
    Dtip = Sigma("x", R, yol(R, _ikili(carp, x, x), sf))

    # Kock-Lawvere: her f : D → R, tek bir (a,b) ile f(d) = a + b·d
    kl_govde = Pi("d", Dtip, yol(R, Uygula(ff, d),
        _ikili(top, aa, _ikili(carp, bb, Birinci(d)))))
    kl = Pi("f", ok(Dtip, R),
              kac_mertebeden(sigma_hepsi([("a", R), ("b", R)], kl_govde), -2))

    # Sonsuz küçük şekil kipi (infinitesimal shape modality) ℑ
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
    """Tümel değişmezlik, bu çekirdekte İFADE EDİLİR fakat TAŞIMASI
    hesaplanmaz; dolayısıyla ``ua``yı hesapla kullanmak isteyen, aksiyom
    olarak ``uaBeta``yı eklemek zorundadır."""
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
    """Bu çekirdeğin BİLİNEN eksikleri. Sessiz değil, kütüklü."""
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
    except Exception as EksikKural:  # noqa: BLE001
        return {"ad": ad, "netice": "HATA", "izah": ("%s: %s" % (type(EksikKural).__name__, EksikKural))[:300]}


def dogrula_hepsi_turetimler() -> List[Dict[str, str]]:
    """Bu dosyadaki her türetimi fiilen tip denetiminden geçirir."""
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
            DogalInd("_", Dogal(), dogal_sayi(3), "k", "r",
                       Ard(D("r")), dogal_sayi(2)), dogal_sayi(5))),
        ("ℤ: sucZ(-1)=0", lambda: _esit_dene(
            Uygula(ardil_z(), tam_sayi(-1)), tam_sayi(0))),
    ]
    neticeler = [_dene(ad, f) for ad, f in isler]

    # (C) postulat tipleri iyi teşkil edilmiş mi?
    ps = sdg_postulatlari()
    gp = Baglam()
    for p in ps:
        neticeler.append(_dene("POSTULAT tipi iyi teşkil: %s" % p.ad,
                               lambda p=p, gp=gp: denetle_tip_yardimci(p.tip, gp)))
        gp = gp.genislet_t(p.ad, p.tip)
    ua_p = univalence_postulati()
    neticeler.append(_dene("POSTULAT tipi iyi teşkil: uaBeta",
                           lambda: denetle_tip_yardimci(ua_p.tip, Baglam())))

    # (B) NbE'de HESAPLANAN: uaβ ve π₁(S¹)
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
    """NbE'de ua boyunca taşıma HESAPLANIR; somut sınama dogrula_hepsi_turetimler'de."""
    A, B, EksikKural, x = D("A"), D("B"), D("EksikKural"), D("x")
    g = Baglam.terimlerden({"A": U, "B": U, "EksikKural": denklik_tipi(A, B), "x": A})
    geri_oku(g.d(tasi(ua(A, B, EksikKural), x)))


def _rapor_turetimler() -> str:
    """Dürüst hulâsa: ne hesaplanıyor, ne ifade ediliyor, ne postulat."""
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


# ====================================================================
#  omega_kategori_nbe/geometri.py
# ====================================================================

U = Evren(0)


U1 = Evren(1)


D = Deg


def sdg_baglami() -> Baglam:
    """``R`` ve halka işlemleri postulat olarak eklenmiş bağlam."""
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
    """``D = Σ (x : R). Path R (x·x) 0`` -- birinci mertebeden sonsuz küçükler."""
    x = terim_taze("x")
    return Sigma(x, R, yol(R, _carp(D(x), D(x)), SIFIR_R))


def sifir_sonsuz_kucuk() -> Terim:
    """``0 ∈ D``: sıfırın karesi sıfırdır (halka aksiyomundan gelir;
    burada tanık POSTULAT olarak istenir)."""
    return Cift(SIFIR_R, D("sifir_kare"))


def teget_demeti(X: Terim) -> Terim:
    """``TX := X^D = (D → X)`` -- teğet demeti HARİTALAMA UZAYIDIR.

    Uzayı kurmak, teğetini de kurmaktır: ayrıca bir inşa gerekmez.
    """
    return ok(sonsuz_kucukler(), X)


def teget_izdusum(X: Terim) -> Terim:
    """``π : TX → X``, ``v ↦ v(0)``."""
    v = terim_taze("v")
    return Lam(v, terim_uygula(D(v), sifir_sonsuz_kucuk()))


def teget_lifi(X: Terim, x: Terim) -> Terim:
    """``T_x X = Σ (v : D → X). Path X (v 0) x`` -- ``x``teki teğet uzayı."""
    v = terim_taze("v")
    return Sigma(v, teget_demeti(X),
                   yol(X, terim_uygula(D(v), sifir_sonsuz_kucuk()), x))


class Modul:
    """Bir ``R``-modülün taşıyıcısı ve işlemleri (terimler)."""

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
    """``Mod_R``: ``R`` üzerinde modül yapısının tipi."""
    V, top, sf, eks, sk = D("V"), D("top"), D("sf"), D("eks"), D("sk")
    x, y, z, c, d_ = D("x"), D("y"), D("z"), D("c"), D("d")
    A = lambda a, b: terim_uygula(terim_uygula(top, a), b)
    Sm = lambda c_, a: terim_uygula(terim_uygula(sk, c_), a)
    P = lambda ad, tip, govde: Pi(ad, tip, govde)
    return sigma_hepsi([
        ("V", U),
        ("kume", kac_mertebeden(V, 0)),
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
    """``f : M.V → N.V`` doğrusal mı? (toplamsal + homojen)"""
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
    """``R``nin kendisi bir ``R``-modüldür; skalerler burada yaşar."""
    return Modul(R, TOP, SIFIR_R, D("eks_R"), CARP)


def dual(M: Modul) -> Terim:
    """``M* = Σ (f : V → R). f doğrusal`` -- kotanjant tarafı."""
    f = terim_taze("f")
    return Sigma(f, ok(M.V, R), dogrusal_mi(M, skaler_modulu(), D(f)))


def cok_dogrusal_tip(yuvalar: Sequence[Terim], hedef: Terim) -> Terim:
    """``V₁ → V₂ → … → W`` -- çok-doğrusal dönüşümün TAŞIYICI tipi."""
    sonuc = hedef
    for V in reversed(list(yuvalar)):
        sonuc = ok(V, sonuc)
    return sonuc


def _yuvada_dogrusal(moduller: Sequence[Modul], N: Modul, f: Terim,
                     k: int) -> Terim:
    """``f``nin ``k``ıncı yuvada doğrusal olduğu şartı; öbür yuvalar
    serbest değişken olarak evrensel nicelenir."""
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
    """``(r,s)`` mertebesinden tensörün tipi.

    ``r`` tane KOVEKTÖR (dual eleman) ve ``s`` tane VEKTÖR alıp skaler
    veren çok-doğrusal dönüşüm. Klasik ``T^{⊗r} ⊗ (T*)^{⊗s}`` demetinin
    global kesitinin iç dildeki karşılığı budur.
    """
    yuvalar = [dual(M)] * r + [M.V] * s
    return cok_dogrusal_tip(yuvalar, R)


def tensor_yapisi(M: Modul, r: int, s: int,
                  dualM: Optional[Modul] = None) -> Terim:
    """``(r,s)``-tensör YAPISI: taşıyıcı çok-doğrusal dönüşüm + HER
    yuvada doğrusallık şartı. Tensörü "yalnız bir fonksiyon"dan ayıran
    şart budur.

    ``r > 0`` ise dual yuvalar için ``M*`` üzerinde de bir modül yapısı
    gerekir; ``dualM`` ile verilir (noktasal yapı, burada teşkil edilmez).
    """
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
    """``x`` noktasında ``(r,s)`` tensörlerinin tipi -- teğet lifinden
    doğrudan doğar; ayrıca bir demet inşası GEREKMEZ."""
    Tx = teget_lifi(X, x)
    M = Modul(Tx, D("teget_top"), D("teget_sifir"), D("teget_eks"),
              D("teget_skaler"))
    return tensor_tipi(M, r, s)


def cebir_tipi() -> Terim:
    """``Mod_R`` içindeki monoid nesnesi: ``μ : A⊗A → A``, ``η : 1 → A``.

    ``⊗`` iç dilde çok-doğrusallıkla temsil edildiğinden ``μ`` iki-doğrusal
    bir dönüşümdür; ``η`` bir noktadır (``1 = R``den gelen birim).
    """
    A, top, sf, eks, sk = D("A"), D("top"), D("sf"), D("eks"), D("sk")
    mu, eta = D("mu"), D("eta")
    x, y, z, c = D("x"), D("y"), D("z"), D("c")
    Ad = lambda a, b: terim_uygula(terim_uygula(top, a), b)
    Sm = lambda c_, a: terim_uygula(terim_uygula(sk, c_), a)
    M = lambda a, b: terim_uygula(terim_uygula(mu, a), b)
    P = Pi
    return sigma_hepsi([
        ("A", U),
        ("kume", kac_mertebeden(A, 0)),
        ("top", ok(A, ok(A, A))),
        ("sf", A),
        ("eks", ok(A, A)),
        ("sk", ok(R, ok(A, A))),
        ("mu", ok(A, ok(A, A))),        # μ : A ⊗ A → A
        ("eta", A),                          # η : 1 → A
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
    """Lie cebri: ``[·,·]``, antisimetri, Jacobi.

    Jacobi bir YOL olarak ifade edilir; kümeler mertebesinde bu klasik
    özdeşliktir, daha yüksek mertebede ise ``lie_koherens`` ile bir üst
    mertebeden yol talep edilebilir.
    """
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
        ("kume", kac_mertebeden(V, 0)),
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
    """``sol`` ile ``sag`` arasındaki ``n``inci mertebeden koherens tipi.

    ``n=1``: iki terim arasındaki yol (klasik özdeşlik).
    ``n=2``: iki yol arasındaki yol (özdeşliğin İSPATLARI arasındaki
             koherens) -- "katı eşitlik değil, bir üst mertebeden morfizm"
             iddiasının fiilî karşılığı.
    """
    tip = yol(V, sol, sag)
    nokta = refl(sol)
    for _ in range(n - 1):
        tip, nokta = yol(tip, nokta, nokta), refl(nokta)
    return tip


def alterne_form_tipi(M: Modul, n: int) -> Terim:
    """``n``-form: ``n`` tane vektör alıp skaler veren çok-doğrusal
    dönüşüm (alternelik ayrı bir şart olarak istenir)."""
    return cok_dogrusal_tip([M.V] * n, R)


def form_uzayi(X: Terim, n: int) -> Terim:
    """``Ωⁿ(X) = Π (x:X). (T_x X)ⁿ → R``"""
    x = terim_taze("x")
    return Pi(x, X, alterne_form_tipi(
        Modul(teget_lifi(X, D(x)), D("teget_top"), D("teget_sifir"),
              D("teget_eks"), D("teget_skaler")), n))


def de_rham_postulatlari(X: Terim, n: int) -> List[Postulat]:
    """``d : Ωⁿ → Ωⁿ⁺¹`` ve ``d∘d = 0``.

    POSTULATTIR: dış türevin hesaplanan bir kuralı bu çekirdekte yoktur.
    Tipleri denetlenir; sakinleri aksiyomdur.
    """
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

    # koherens kulesi: 1., 2., 3. mertebe
    a, b = D("a"), D("b")
    gk = g.genislet_t("A", U).genislet_t("a", D("A")).genislet_t("b", D("A"))
    for n in (1, 2, 3):
        neticeler.append(_dene(
            "koherens kulesi mertebe %d : U" % n,
            lambda n=n: denetle_t(koherens_kulesi(D("A"), a, a, n), U, gk)))

    # de Rham postulatlarının tipleri iyi teşkil mi?
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


# ====================================================================
#  omega_kategori_nbe/iliskiler.py
# ====================================================================

U = Evren(0)


U1 = Evren(1)


D = Deg


def bileske(f: Terim, g: Terim) -> Terim:
    """``g ∘ f``"""
    x = terim_taze("x")
    return Lam(x, terim_uygula(g, terim_uygula(f, D(x))))


def geri_cek(f: Terim, P: Terim) -> Terim:
    """``f^* P = λ x. P (f x)`` -- geri çekme (pullback) funktoru."""
    x = terim_taze("x")
    return Lam(x, terim_uygula(P, terim_uygula(f, D(x))))


def toplam_it(X: Terim, Y: Terim, f: Terim, Q: Terim) -> Terim:
    """``Σ_f Q = λ y. Σ (x:X). (Path Y (f x) y) × Q x`` -- sol bitişik."""
    y, x = terim_taze("y"), terim_taze("x")
    return Lam(y, Sigma(x, X,
        carpim(yol(Y, terim_uygula(f, D(x)), D(y)), terim_uygula(Q, D(x)))))


def carpim_it(X: Terim, Y: Terim, f: Terim, Q: Terim) -> Terim:
    """``Π_f Q = λ y. Π (x:X). (Path Y (f x) y) → Q x`` -- sağ bitişik."""
    y, x = terim_taze("y"), terim_taze("x")
    return Lam(y, Pi(x, X,
        ok(yol(Y, terim_uygula(f, D(x)), D(y)), terim_uygula(Q, D(x)))))


def _aile_oku(A: Terim, F1: Terim, F2: Terim) -> Terim:
    """``Π (a:A). F1 a → F2 a`` -- aileler arası dönüşüm."""
    a = terim_taze("a")
    return Pi(a, A, ok(terim_uygula(F1, D(a)), terim_uygula(F2, D(a))))


def bitisiklik_sol_tipi(X: Terim, Y: Terim, f: Terim,
                        Q: Terim, P: Terim) -> Terim:
    """``Denklik (Σ_f Q ⇒ P) (Q ⇒ f^* P)``  --  ``Σ_f ⊣ f^*``"""
    return denklik_tipi(_aile_oku(Y, toplam_it(X, Y, f, Q), P),
                          _aile_oku(X, Q, geri_cek(f, P)))


def bitisiklik_sag_tipi(X: Terim, Y: Terim, f: Terim,
                        P: Terim, Q: Terim) -> Terim:
    """``Denklik (f^* P ⇒ Q) (P ⇒ Π_f Q)``  --  ``f^* ⊣ Π_f``"""
    return denklik_tipi(_aile_oku(X, geri_cek(f, P), Q),
                          _aile_oku(Y, P, carpim_it(X, Y, f, Q)))


def zincir_kurali_tipi(X: Terim, Z: Terim, f: Terim, g: Terim,
                       P: Terim) -> Terim:
    """``Path (X → U) ((g∘f)^* P) (f^* (g^* P))``"""
    return yol(ok(X, U), geri_cek(bileske(f, g), P),
                 geri_cek(f, geri_cek(g, P)))


def zincir_kurali_ispati(X: Terim, Z: Terim, f: Terim, g: Terim,
                         P: Terim) -> Terim:
    """İSPAT: ``refl``. İki taraf da ``λx. P (g (f x))``e indirgenir;
    yani zincir kuralı burada bir teorem değil, morfizm bileşkesinin
    TANIMSAL neticesidir."""
    return refl(geri_cek(bileske(f, g), P))


def monoidal_uyum_tipi(X: Terim, Y: Terim, f: Terim,
                       P: Terim, Q: Terim) -> Terim:
    """``Path (X → U) (f^*(P × Q)) (f^*P × f^*Q)``"""
    y = terim_taze("y")
    carpim_ailesi = Lam(y, carpim(terim_uygula(P, D(y)), terim_uygula(Q, D(y))))
    x = terim_taze("x")
    sag = Lam(x, carpim(terim_uygula(geri_cek(f, P), D(x)),
                            terim_uygula(geri_cek(f, Q), D(x))))
    return yol(ok(X, U), geri_cek(f, carpim_ailesi), sag)


def monoidal_uyum_ispati(X: Terim, Y: Terim, f: Terim,
                         P: Terim, Q: Terim) -> Terim:
    """İSPAT: ``refl`` -- tensör/çarpım yapısı geri çekmede TANIMSAL korunur."""
    y = terim_taze("y")
    carpim_ailesi = Lam(y, carpim(terim_uygula(P, D(y)), terim_uygula(Q, D(y))))
    return refl(geri_cek(f, carpim_ailesi))


def teget_donusumu(f: Terim) -> Terim:
    """``Tf : TX → TY``, ``v ↦ λd. f (v d)`` -- diferansiyel (Jacobian).

    Teğet demeti bir haritalama uzayı olduğundan ``Tf`` ayrıca inşa
    edilmez; ``f`` ile ard arda uygulamadan ibarettir.
    """
    v, d = terim_taze("v"), terim_taze("d")
    return Lam(v, Lam(d, terim_uygula(f, terim_uygula(D(v), D(d)))))


def teget_zincir_tipi(X: Terim, Z: Terim, f: Terim, g: Terim) -> Terim:
    """``Path (TX → TZ) (T(g∘f)) (Tg ∘ Tf)``"""
    TX, TZ = teget_demeti(X), teget_demeti(Z)
    return yol(ok(TX, TZ), teget_donusumu(bileske(f, g)),
                 bileske(teget_donusumu(f), teget_donusumu(g)))


def teget_zincir_ispati(X: Terim, Z: Terim, f: Terim, g: Terim) -> Terim:
    """İSPAT: ``refl`` -- teğet funktoru bileşkeyi TANIMSAL korur."""
    return refl(teget_donusumu(bileske(f, g)))


def ayrik_mi(X: Terim) -> Terim:
    """Ayrıklık ölçütü: ``isSet X`` (0-kesilmişlik)."""
    return kac_mertebeden(X, 0)


def yuksek_morfizmler_onemsiz_tipi(X: Terim) -> Terim:
    """``isSet X → Π (x:X). isContr (Ω(X,x))``

    "Ayrık uzayda bütün yüksek morfizmler önemsizleşir" iddiasının tam
    ifadesi budur.
    """
    x = terim_taze("x")
    return ok(kac_mertebeden(X, 0),
                Pi(x, X, kac_mertebeden(dongu_uzayi(X, D(x)), -2)))


def yuksek_morfizmler_onemsiz_ispati(X: Terim) -> Terim:
    """İSPAT: merkez ``refl x``; büzme, ``isSet``in kendisidir."""
    h, x, p = terim_taze("h"), terim_taze("x"), terim_taze("p")
    return Lam(h, Lam(x, Cift(
        refl(D(x)),
        Lam(p, terim_uygula(terim_uygula(terim_uygula(terim_uygula(D(h), D(x)), D(x)),
                                  refl(D(x))), D(p))))))


def ayrik_uzay_tipi() -> Terim:
    """``Σ (X:U). isSet X`` -- ayrık uzaylar, hiyerarşinin en dip tabakası."""
    X = terim_taze("X")
    return Sigma(X, U, ayrik_mi(D(X)))


def ayrik_postulatlari() -> List[Postulat]:
    """``Π₀ ⊣ Disc ⊣ Γ`` bitişiklik zinciri.

    ``Disc`` iç dilde zaten dâhil etmedir (bir küme bir tiptir); ``Π₀``
    ise küme-kesmesi (set truncation) bir HIT olduğundan ve bu çekirdekte
    genel HIT şeması bulunmadığından POSTULATTIR.
    """
    X = D("X")
    p0 = D("Pi0")
    x = terim_taze("x")
    return [
        Postulat("Pi0", ok(U, U),
                   "Π₀ : bağlantılı bileşenler / küme-kesmesi (0-truncation)."),
        Postulat("Pi0_kume", Pi("X", U, kac_mertebeden(terim_uygula(p0, X), 0)),
                   "Π₀X daima bir kümedir (0-kesilmiştir)."),
        Postulat("Pi0_birim", Pi("X", U, ok(X, terim_uygula(p0, X))),
                   "Birim dönüşüm X → Π₀X."),
    ]


def kritik_lokus(f: Terim) -> Terim:
    """``Crit(f) = Σ (x:R). Π (d:D). Path R (f (x+d)) (f x)``

    SDG'de "türev sıfırdır" şartı budur: fonksiyon sonsuz küçük her
    kaymada değişmiyorsa o nokta kritiktir. Asgari/azami noktalar bu
    alt-uzayın sakinleridir.
    """
    x, d = terim_taze("x"), terim_taze("d")
    kayma = terim_uygula(terim_uygula(TOP, D(x)), Birinci(D(d)))
    return Sigma(x, R, Pi(d, sonsuz_kucukler(),
        yol(R, terim_uygula(f, kayma), terim_uygula(f, D(x)))))


def tikanma_postulati(X: Terim) -> Postulat:
    """Tıkanma (obstruction) sınıfı -- kohomoloji bu çekirdekte yok,
    POSTULATTIR."""
    return Postulat("tikanma", ok(ok(X, U), U),
                      "Bir ailenin global kesitinin varlığına engel olan "
                      "kohomolojik sınıf; sıfırdan farklıysa global inşa "
                      "imkânsızdır (tüylü top tipi haller).")


def evrensel_demet(M: Terim, F: Terim) -> Terim:
    """``E = Σ (w:M). F w`` -- parametre uzayı üzerindeki evrensel demet."""
    w = terim_taze("w")
    return Sigma(w, M, terim_uygula(F, D(w)))


def demet_izdusumu(M: Terim, F: Terim) -> Terim:
    """``π : E → M``"""
    e = terim_taze("e")
    return Lam(e, Birinci(D(e)))


def agirlikta_lif(F: Terim, w: Terim) -> Terim:
    """``X_w = F w`` -- ağırlık ``w``de türetilen uzay (geri çekilmiş lif)."""
    return terim_uygula(F, w)


def kesit_tipi(M: Terim, F: Terim) -> Terim:
    """``Π (w:M). F w`` -- seçim kesiti; "öğrenilmiş ağırlık" budur."""
    w = terim_taze("w")
    return Pi(w, M, terim_uygula(F, D(w)))


def lif_geri_cekme_ispati(M: Terim, F: Terim, w: Terim) -> Terim:
    """``E`` üzerinden ``w``deki lifi geri çekmek ``F w``yi verir --
    ``refl`` ile: parametrik geri çekme TANIMSALDIR."""
    return refl(terim_uygula(F, w))


def kip_postulatlari() -> List[Postulat]:
    """Gayrilineerliği sağlayan kip (modality).

    Doğrusal funktorlar homotopik sınırları korur; gayrilineerlik, araya
    bir kip/kesme/lokalizasyon funktoru koyarak elde edilir. Kip bir HIT
    (kesme) gerektirdiğinden POSTULATTIR.
    """
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
        # 1. geri çekme / itme
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
        # 2. zincir kuralı ve monoidal uyum -- refl ile İSPATLANIR
        ("ZİNCİR KURALI (g∘f)^* ≡ f^*∘g^*  [refl ile İSPAT]",
         lambda: denetle_t(zincir_kurali_ispati(X, Z, f, gg, P),
                         zincir_kurali_tipi(X, Z, f, gg, P), g)),
        ("MONOİDAL UYUM f^*(P×Q) ≡ f^*P × f^*Q  [refl ile İSPAT]",
         lambda: denetle_t(monoidal_uyum_ispati(X, Y, f, PY, QY),
                         monoidal_uyum_tipi(X, Y, f, PY, QY), g)),
        # 3. teğet funktoru
        ("Tf : TX → TY",
         lambda: denetle_t(teget_donusumu(f),
                         ok(teget_demeti(X), teget_demeti(Y)), g)),
        ("TEĞET ZİNCİRİ T(g∘f) ≡ Tg∘Tf  [refl ile İSPAT]",
         lambda: denetle_t(teget_zincir_ispati(X, Z, f, gg),
                         teget_zincir_tipi(X, Z, f, gg), g)),
        # 4. ayrık uzaylar
        ("Ayrık uzay tipi : U₁", lambda: denetle_t(ayrik_uzay_tipi(), U1, g)),
        ("AYRIKTA YÜKSEK MORFİZMLER ÖNEMSİZ  [İSPAT]",
         lambda: denetle_t(yuksek_morfizmler_onemsiz_ispati(X),
                         yuksek_morfizmler_onemsiz_tipi(X), g)),
        # 5. uç haller
        ("Kritik lokus Crit(f) : U",
         lambda: denetle_t(kritik_lokus(D("fR")), U, g)),
        # 6. parametrik demet
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

    # postulat tipleri iyi teşkil mi?
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


# ====================================================================
#  omega_kategori_nbe/yazdir.py
# ====================================================================

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


# ====================================================================
#  Çipin toplu raporu
# ====================================================================
BOLUMLER = (
    ("TÜRETİMLER -- ∞-grupoid kulesi, ℕ, ℤ, S¹, postulatlar",
     "_rapor_turetimler"),
    ("SDG -- sonsuz küçükler, teğet demeti, de Rham", "_rapor_geometri"),
    ("MÜNASEBETLER -- geri çekme, bitişiklik, demetler",
     "_rapor_iliskiler"),
)


def rapor() -> str:                            # pragma: no cover
    """Altı odanın ölçümü, sırayla."""
    s = []
    for baslik, fn in BOLUMLER:
        s.append("")
        s.append("=" * 70)
        s.append("  " + baslik)
        s.append("=" * 70)
        s.append(globals()[fn]())
    return "\n".join(s)


if __name__ == "__main__":                     # pragma: no cover
    print(rapor())
