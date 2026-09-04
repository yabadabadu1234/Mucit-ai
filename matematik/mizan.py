"""MÎZÂN ÇİPİ -- mantık, cedel ve epistemik hüküm.

KÜME 7'nin ikinci karargâhı (kütük H226). Sekiz dosya --
``mizan/onerme.py``, ``kiyas.py``, ``cikarim.py``, ``kiplik.py``,
``cokdegerli.py``, ``altyapisal.py``, ``istikra.py``, ``munazara.py``
-- burada birleşti. Terkip üç adımda yapıldı: (a) evvelâ her dosya
**kendi içinde** terkip edildi, (b) sonra dosyalar birleştirildi,
(c) sonra birleşik gövdede **bir daha** terkip edildi. Hiçbir cevher
seçilip imha edilmedi; asılları ``yedek/kume7_asillari/mizan/``
altında şahittir.

**Kök problem.** Sekiz mantık motoru -- önerme mantığı, kıyas,
çıkarım hesapları, Kripke kiplikleri, çok değerli mantıklar,
yapısal-altı mantıklar, istikrâ ve cedel -- her biri kusursuz
çalışıyor fakat sekiz ayrı dosyada duruyordu; hükmün nereden
geldiğini tek yerden okumak mümkün değildi.

**Çipin altı odası.**

1. **Formül ve doğruluk** -- ``Onerme`` (hash-consing düğümleri),
   ``Tablo``: bütün ``2ⁿ`` değerleme **tek bir büyük tam sayının**
   bitlerinde; totoloji, denklik, geçerlilik ve karşı örnek oradan
   okunur.
2. **Kıyas-ı iktiranî** -- ``tutuyor_mu`` (A/E/I/O
   tek bit ameli), 256 monadik modelle **tam** karar, dört şekil,
   varlık faraziyesiyle 24 mûteber darb.
3. **Çıkarım hesapları** -- ``aksiyom`` (şema bir kere yazılır,
   eşleme birleştirmeyle türetilir), Gentzen LK, Dyckhoff G4ip
   (büzülmesiz, sonlanması ispatlı).
4. **Kiplik ve zaman** -- 512 Kripke çerçevesiyle K/T/4/5/B/D
   karşılıkları, ``odev`` (deontik), ``sonra``
   (sonlu iz üstünde LTL; ``G`` ve ``F``, ``U``nun tanımıdır).
5. **Derece ve kalıntı** -- ``derece``: sekiz t-normu ve
   dört kalıntısı tek kapıda; T89 eşlenikliği, Priest LP paratutarlılığı,
   syādvāda; yapısal-altı mantıklar ve ortomodüler kuantum kafesi.
6. **İstikrâ ve cedel** -- ``illet_ara`` (uyuşma/ayrılık/birleşik/eş
   değişim), Laplace ardışıklığı, ICP değişmezliği, Nyāya ve Stoa
   şemaları; men'/nakz/muâraza oyunu ve Gazâlî yakîn mîzânı
   ``min(öncül) · 𝟙[şekil geçerli]``.
"""
from __future__ import annotations

import itertools
import math
import numpy as np
from dataclasses import dataclass, field
from enum import Enum
from functools import lru_cache
from itertools import product
from typing import (Callable, Dict, FrozenSet, Iterable, List, Optional,
                    Sequence, Set, Tuple)
from typing import Callable, Dict, FrozenSet, List, Optional, Sequence, Tuple
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple
from typing import Dict, FrozenSet, Iterable, List, Optional, Sequence, Set, Tuple
from typing import Dict, FrozenSet, Iterable, List, Optional, Sequence, Tuple
from typing import Dict, FrozenSet, List, Optional, Sequence, Set, Tuple
from typing import Dict, List, Optional, Sequence, Set, Tuple


# ====================================================================
#  mizan/onerme.py
# ====================================================================

DOGRU, YANLIS, DEG, DEGIL, VE, VEYA, ISE, ANCAK, XOR = range(9)


KUTU, ELMAS = 9, 10


_ETIKET_ADI = {DOGRU: "⊤", YANLIS: "⊥", DEG: "", DEGIL: "¬", VE: "∧",
               VEYA: "∨", ISE: "→", ANCAK: "↔", XOR: "⊻",
               KUTU: "□", ELMAS: "◇"}


class Onerme:
    """Hash-consing'li önerme düğümü.

    Doğrudan kurulmaz; ``deg``, ``degil``, ``ve`` … kurucuları kullanılır.
    ``kimlik`` süreç içinde tektir ve bellekleme anahtarıdır.
    """

    __slots__ = ("etiket", "ad", "altlar", "kimlik", "_hash", "_degiskenler")

    def __init__(self, etiket: int, ad: Optional[str],
                 altlar: Tuple["Onerme", ...], kimlik: int) -> None:
        self.etiket = etiket
        self.ad = ad
        self.altlar = altlar
        self.kimlik = kimlik
        self._hash = hash((etiket, ad, tuple(a.kimlik for a in altlar)))
        self._degiskenler: Optional[FrozenSet[str]] = None

    # -- protokol -----------------------------------------------------
    def __hash__(self) -> int:
        return self._hash

    def __eq__(self, obur: object) -> bool:
        # hash-consing sayesinde kimlik karşılaştırması YETERLİDİR
        return self is obur

    def __repr__(self) -> str:
        return yaz(self)

    # -- sorgular -----------------------------------------------------
    def degiskenler(self) -> FrozenSet[str]:
        if self._degiskenler is None:
            if self.etiket == DEG:
                self._degiskenler = frozenset({self.ad})       # type: ignore[arg-type]
            else:
                k: set = set()
                for a in self.altlar:
                    k |= a.degiskenler()
                self._degiskenler = frozenset(k)
        return self._degiskenler

    def boyut(self) -> int:
        """AYRI alt formül sayısı (paylaşım sayılmaz)."""
        gorulen: set = set()
        yigin = [self]
        while yigin:
            d = yigin.pop()
            if d.kimlik in gorulen:
                continue
            gorulen.add(d.kimlik)
            yigin.extend(d.altlar)
        return len(gorulen)


_TABLO: Dict[Tuple, Onerme] = {}


def _kur(etiket: int, ad: Optional[str], altlar: Tuple[Onerme, ...]) -> Onerme:
    anahtar = (etiket, ad, tuple(a.kimlik for a in altlar))
    d = _TABLO.get(anahtar)
    if d is None:
        d = Onerme(etiket, ad, altlar, len(_TABLO))
        _TABLO[anahtar] = d
    return d


def tablo_boyu() -> int:
    """Kaç AYRI alt formül kurulmuş? (bellek ölçümü için)"""
    return len(_TABLO)


def dogru() -> Onerme:
    return _kur(DOGRU, None, ())


def yanlis() -> Onerme:
    return _kur(YANLIS, None, ())


def deg(ad: str) -> Onerme:
    return _kur(DEG, ad, ())


def degil(a: Onerme) -> Onerme:
    return _kur(DEGIL, None, (a,))


def ve(*parcalar: Onerme) -> Onerme:
    if not parcalar:
        return dogru()
    d = parcalar[0]
    for p in parcalar[1:]:
        d = _kur(VE, None, (d, p))
    return d


def veya(*parcalar: Onerme) -> Onerme:
    if not parcalar:
        return yanlis()
    d = parcalar[0]
    for p in parcalar[1:]:
        d = _kur(VEYA, None, (d, p))
    return d


def ise(a: Onerme, b: Onerme) -> Onerme:
    return _kur(ISE, None, (a, b))


def ancak(a: Onerme, b: Onerme) -> Onerme:
    return _kur(ANCAK, None, (a, b))


def xor(a: Onerme, b: Onerme) -> Onerme:
    return _kur(XOR, None, (a, b))


def kutu(a: Onerme) -> Onerme:
    """``□A`` -- zorunluluk. Değerlendirmesi ``kiplik.py``dedir."""
    return _kur(KUTU, None, (a,))


def elmas(a: Onerme) -> Onerme:
    """``◇A`` -- imkân. ``◇A ≡ ¬□¬A`` özdeşliği orada sınanır."""
    return _kur(ELMAS, None, (a,))


def yaz(d: Onerme) -> str:
    e = d.etiket
    if e == DEG:
        return d.ad or "?"
    if e in (DOGRU, YANLIS):
        return _ETIKET_ADI[e]
    if e in (DEGIL, KUTU, ELMAS):
        return "%s%s" % (_ETIKET_ADI[e], yaz(d.altlar[0]))
    return "(%s %s %s)" % (yaz(d.altlar[0]), _ETIKET_ADI[e], yaz(d.altlar[1]))


class Tablo:
    """``n`` değişken üzerindeki bütün ``2ⁿ`` değerlemenin taşıyıcısı.

    Bir formülün doğruluk **sütunu**, ``2ⁿ`` bitlik tek bir tam sayıdır.
    ``k``. değişkenin sütunu, ``2^k`` uzunluğunda ardışık blokların
    dönüşümlü tekrarıdır; bu, standart doğruluk tablosu dizilişidir ve
    bir kere kurulup saklanır.
    """

    __slots__ = ("degiskenler", "yer", "n", "maske", "_sutun", "_onbellek")

    def __init__(self, degiskenler: Sequence[str]) -> None:
        self.degiskenler = tuple(sorted(set(degiskenler)))
        self.yer = {ad: i for i, ad in enumerate(self.degiskenler)}
        self.n = len(self.degiskenler)
        if self.n > 20:
            raise ValueError("bit-paralel tablo 20 değişkene kadar; %d verildi"
                             % self.n)
        self.maske = (1 << (1 << self.n)) - 1
        self._sutun: List[int] = [self._degisken_sutunu(k) for k in range(self.n)]
        self._onbellek: Dict[int, int] = {}

    def _degisken_sutunu(self, k: int) -> int:
        """``k``. değişkenin sütunu: ``2^k`` sıfır, ``2^k`` bir, tekrar.

        Yani ``i``. bit, ``(i >> k) & 1`` ise kuruludur -- standart
        doğruluk tablosu dizilişi.

        Desen KATLAYARAK üretilir (``sonuc |= sonuc << genişlik``), tek
        tek tekrarlanarak değil: dönem sayısı ``2^{n-k-1}`` olduğundan
        naif tekrar ``n=20, k=0`` için 524 288 büyük tam sayı işlemi
        ister; katlama ``n-k`` işlem ister. Netice birebir aynıdır.
        """
        blok = (1 << (1 << k)) - 1           # 2^k tane 1
        desen = blok << (1 << k)             # dönemin ÜST yarısı 1
        sonuc = desen
        genislik = 1 << (k + 1)              # bir dönemin bit uzunluğu
        hedef = 1 << self.n
        while genislik < hedef:
            sonuc |= sonuc << genislik
            genislik <<= 1
        return sonuc & self.maske

    # -- değerlendirme ------------------------------------------------
    def sutun(self, d: Onerme) -> int:
        """Formülün bütün değerlemelerdeki doğruluk sütunu."""
        onb = self._onbellek.get(d.kimlik)
        if onb is not None:
            return onb
        e = d.etiket
        if e == DOGRU:
            s = self.maske
        elif e == YANLIS:
            s = 0
        elif e == DEG:
            s = self._sutun[self.yer[d.ad]]                 # type: ignore[index]
        elif e == DEGIL:
            s = ~self.sutun(d.altlar[0]) & self.maske
        elif e in (KUTU, ELMAS):
            raise ValueError(
                "kiplikli formül önermeler tablosunda değerlendirilemez: %s"
                % yaz(d))
        else:
            a = self.sutun(d.altlar[0])
            b = self.sutun(d.altlar[1])
            if e == VE:
                s = a & b
            elif e == VEYA:
                s = a | b
            elif e == ISE:
                s = (~a | b) & self.maske
            elif e == ANCAK:
                s = ~(a ^ b) & self.maske
            else:                                            # XOR
                s = a ^ b
        self._onbellek[d.kimlik] = s
        return s

    def degerle(self, d: Onerme, atama: Dict[str, bool]) -> bool:
        """Tek bir değerlemede doğruluk."""
        i = 0
        for ad, k in self.yer.items():
            if atama.get(ad, False):
                i |= 1 << k
        return bool((self.sutun(d) >> i) & 1)

    def dogru_sayisi(self, d: Onerme) -> int:
        return bin(self.sutun(d)).count("1")


def _tablo_kur(formuller: Iterable[Onerme]) -> Tablo:
    v: set = set()
    for f in formuller:
        v |= f.degiskenler()
    return Tablo(sorted(v) or ["_"])


def hukum(a=None, b=None, oncüller=None, netice=None,
                       ne: str = "geçerli"):
    """DOĞRULUK TABLOSUNDA NE YAZIYOR -- **tek terkip** (kütük H226).

    Küme: ``totoloji_mi``, ``tutarli_mi``, ``denk_mi``, ``gecerli_mi``,
    ``karsi_ornek``. Beş isim, tek amelin duraklarıydı: **bit-paralel
    tabloyu kur, bir maskeyi oku.** Terkipte o maske açıkça görünür:

    ==============  ==============================  ==================
    ``ne``          okunan maske                    hüküm
    ==============  ==============================  ==================
    ``totoloji``    ``süt(a) == maske``             her yerde doğru
    ``tutarlı``     ``süt(a) != 0``                 bir yerde doğru
    ``denk``        ``süt(a) == süt(b)``            her yerde aynı
    ``geçerli``     ``kötü == 0``                   nakız yok
    ``karşı_örnek`` ``kötü``nün en düşük biti       nakzın kendisi
    ==============  ==============================  ==================

    Burada ``kötü = (⋀ öncül) ∧ ¬netice`` -- yani öncülleri doğrulayıp
    neticeyi yalanlayan değerlemelerin maskesi. ``geçerli`` ile
    ``karşı_örnek`` **aynı maskenin** iki okunuşudur: biri sıfır mı
    diye bakar, öteki sıfır değilse ilk tanığı çıkarır. Ayrı
    yazıldıklarında aynı maskeyi iki kere kurup birbirinden sapabilme
    ihtimali vardı.

    Bütün ``2ⁿ`` değerleme **tek bir büyük tam sayının** bitlerindedir;
    tabloyu gezmek yoktur, maske işlemi vardır.

    T37'nin tashihinin fiilî karşılığı ``geçerli``dedir: geçerlilik,
    çelişkisizlik **değil**, gerektirmenin her modelde doğru olmasıdır.
    """
    if ne in ("totoloji", "tutarlı"):
        t = _tablo_kur([a])
        return (t.sutun(a) == t.maske) if ne == "totoloji" else (
            t.sutun(a) != 0)
    if ne == "denk":
        t = _tablo_kur([a, b])
        return t.sutun(a) == t.sutun(b)
    if ne not in ("geçerli", "karşı_örnek"):
        raise ValueError("tablo suâli bilinmiyor: %r" % (ne,))

    t = _tablo_kur(list(oncüller) + [netice])
    on = t.maske
    for p_ in oncüller:
        on &= t.sutun(p_)
    kotu = on & ~t.sutun(netice) & t.maske       # nakız maskesi
    if ne == "geçerli":
        return kotu == 0
    if kotu == 0:
        return None
    i = (kotu & -kotu).bit_length() - 1          # en düşük kurulu bit
    return {ad: bool((i >> k) & 1) for ad, k in t.yer.items()}


# ====================================================================
#  mizan/kiyas.py
# ====================================================================

S, M, P = 0, 1, 2


TERIM_ADI = {S: "S", M: "M", P: "P"}


TUM = (1 << 8) - 1


def _terim_maskesi(t: int) -> int:
    """``t`` terimini sağlayan atomların maskesi."""
    return sum(1 << a for a in range(8) if (a >> t) & 1)


MASKE = (_terim_maskesi(S), _terim_maskesi(M), _terim_maskesi(P))


def tutuyor_mu(m: int, x: int, y: int, bicim: str,
                                   maskeli: bool = False) -> bool:
    """BU HÜKÜM BU MODELDE TUTUYOR MU -- tek terkip (kütük H226).

    Küme: ``_A``, ``_E``, ``_I``, ``_O``. Dört isim, **tek** bit
    ameliydi ve o amel şudur:

        ``var = (m & S(x) & (P(y) yahut ~P(y))) != 0``

    * **kemiyet** (küllî A,E / cüz'î I,O) neyin sorulduğunu söyler:
      küllî böyle bir şeyin **yokluğunu** ister (``== 0``), cüz'î
      **varlığını** (``!= 0``).
    * **keyfiyet** (olumlu A,I / olumsuz E,O) yüklemin **tümleneceğini**
      söyler -- ve iki eksen ``XOR`` ile kenetlenir:
      ``tümlenmiş = (küllî ≠ olumsuz)``. Sebep cebrîdir: bir varlık
      önermesini değillemek keyfiyeti çevirir, zira
      ``¬∃(S ∧ ¬P)`` "her S P'dir" (A), ``¬∃(S ∧ P)`` ise
      "hiçbir S P değildir" (E)dir.

    Yâni dört biçim, iki ikili tercihin çarpımıdır ve Aristo'nun
    karşıtlık murabbaı tam bu iki eksendir. Ayrı ayrı yazıldıklarında
    ne murabba ne de o ``XOR`` görünüyordu.

    ``maskeli=True`` iken ``x`` ve ``y`` terim indisi değil **doğrudan
    maskedir**; aks-i nakîz (``¬P, ¬S``) böyle kurulur ve dört biçim
    orada da ikinci kere yazılmaz.
    """
    if bicim not in ("A", "E", "I", "O"):
        raise ValueError("önerme biçimi bilinmiyor: %r" % (bicim,))
    kulli = bicim in ("A", "E")           # kemiyet: yokluk mu istenir
    olumsuz = bicim in ("E", "O")         # keyfiyet
    mx = x if maskeli else MASKE[x]
    my = y if maskeli else MASKE[y]
    var = (m & mx & (~my if kulli != olumsuz else my)) != 0
    return (not var) if kulli else var


BICIMLER: Tuple[str, ...] = ("A", "E", "I", "O")


BICIM_ADI = {
    "A": "Mûcebe-i Külliyye",
    "E": "Sâlibe-i Külliyye",
    "I": "Mûcebe-i Cüz'iyye",
    "O": "Sâlibe-i Cüz'iyye",
}


SEKIL: Dict[int, Tuple[Tuple[int, int], Tuple[int, int]]] = {
    1: ((M, P), (S, M)),
    2: ((P, M), (S, M)),
    3: ((M, P), (M, S)),
    4: ((P, M), (M, S)),
}


SEKIL_ADI = {
    1: "Şekl-i Evvel (orta terim birincide yüklem, ikincide özne)",
    2: "Şekl-i Sânî (orta terim her iki öncülde yüklem)",
    3: "Şekl-i Sâlis (orta terim her iki öncülde özne)",
    4: "Şekl-i Râbi' (Galenik)",
}


DARB_ADI: Dict[Tuple[int, str], str] = {
    (1, "AAA"): "Barbara", (1, "EAE"): "Celarent", (1, "AII"): "Darii",
    (1, "EIO"): "Ferio", (1, "AAI"): "Barbari", (1, "EAO"): "Celaront",
    (2, "EAE"): "Cesare", (2, "AEE"): "Camestres", (2, "EIO"): "Festino",
    (2, "AOO"): "Baroco", (2, "EAO"): "Cesaro", (2, "AEO"): "Camestros",
    (3, "AAI"): "Darapti", (3, "IAI"): "Disamis", (3, "AII"): "Datisi",
    (3, "EAO"): "Felapton", (3, "OAO"): "Bocardo", (3, "EIO"): "Ferison",
    (4, "AAI"): "Bamalip", (4, "AEE"): "Camenes", (4, "IAI"): "Dimatis",
    (4, "EAO"): "Fesapo", (4, "EIO"): "Fresison", (4, "AEO"): "Camenos",
}


def modeller(bos_olmayan: Iterable[int] = ()) -> List[int]:
    """Verilen terimlerin boş olmadığı bütün modeller (8 bitlik maskeler).

    Faraziye yoksa 256 modelin tamamı döner.
    """
    sart = tuple(bos_olmayan)
    if not sart:
        return list(range(256))
    return [m for m in range(256)
            if all((m & MASKE[t]) != 0 for t in sart)]


_MODEL_ONBELLEK: Dict[FrozenSet[int], List[int]] = {}


def _modeller(sart: FrozenSet[int]) -> List[int]:
    """``modeller`` fonksiyonunun belleklenmiş hâli.

    256 darb-şekil bileşimi aynı model listesini tekrar tekrar ister;
    liste bir kere kurulup paylaşılır. Netice değişmez, yalnız tekrar
    hesap düşer.
    """
    l = _MODEL_ONBELLEK.get(sart)
    if l is None:
        l = modeller(sorted(sart))
        _MODEL_ONBELLEK[sart] = l
    return l


def kiyas_gecerli_mi(sekil: int, darb: str,
               bos_olmayan: Iterable[int] = ()) -> bool:
    """``darb`` (üç harf: büyük öncül, küçük öncül, netice) geçerli mi?"""
    (bx, by), (kx, ky) = SEKIL[sekil]
    B = tutuyor_mu
    fb, fk, fn = (lambda m, x, y, c=c: B(m, x, y, c) for c in darb[:3])
    for m in _modeller(frozenset(bos_olmayan)):
        if fb(m, bx, by) and fk(m, kx, ky) and not fn(m, S, P):
            return False
    return True


def karsi_model(sekil: int, darb: str,
                bos_olmayan: Iterable[int] = ()) -> Optional[int]:
    """Geçersizse öncülleri doğrulayıp neticeyi yalanlayan bir model."""
    (bx, by), (kx, ky) = SEKIL[sekil]
    B = tutuyor_mu
    fb, fk, fn = (lambda m, x, y, c=c: B(m, x, y, c) for c in darb[:3])
    for m in _modeller(frozenset(bos_olmayan)):
        if fb(m, bx, by) and fk(m, kx, ky) and not fn(m, S, P):
            return m
    return None


def model_yaz(m: int) -> str:
    """Modeli okunur biçimde: hangi atomlar boş değil."""
    if m == 0:
        return "{ } (bütün terimler boş)"
    parcalar = []
    for a in range(8):
        if (m >> a) & 1:
            ad = "".join(TERIM_ADI[t] if (a >> t) & 1 else "¬" + TERIM_ADI[t]
                         for t in (S, M, P))
            parcalar.append(ad)
    return "{ " + ", ".join(parcalar) + " }"


def butun_darblar() -> List[Tuple[int, str]]:
    """4 şekil × 4³ darb = 256 bileşim."""
    return [(s, a + b + c)
            for s in (1, 2, 3, 4)
            for a in "AEIO" for b in "AEIO" for c in "AEIO"]


def gecerli_darblar(bos_olmayan: Iterable[int] = ()) -> List[Tuple[int, str]]:
    sart = tuple(bos_olmayan)
    return [(s, d) for (s, d) in butun_darblar() if kiyas_gecerli_mi(s, d, sart)]


def asgari_varlik_faraziyesi(sekil: int, darb: str) -> Optional[FrozenSet[int]]:
    """Darbı geçerli kılan EN KÜÇÜK boş-olmama şartı.

    ``frozenset()`` : faraziyesiz geçerli.
    Tek terimli küme : o terimin boş olmaması yeter.
    ``None``         : üç terim birden boş olmasa dahi geçersiz.
    """
    if kiyas_gecerli_mi(sekil, darb):
        return frozenset()
    for t in (S, M, P):
        if kiyas_gecerli_mi(sekil, darb, (t,)):
            return frozenset({t})
    for ikili in ((S, M), (S, P), (M, P)):
        if kiyas_gecerli_mi(sekil, darb, ikili):
            return frozenset(ikili)
    if kiyas_gecerli_mi(sekil, darb, (S, M, P)):
        return frozenset({S, M, P})
    return None


def aks_gecerli_mi(kaynak: str, hedef: str, ters: bool = True,
                   bos_olmayan: Iterable[int] = ()) -> bool:
    """``kaynak(S,P)`` öncülünden ``hedef`` neticesi çıkar mı?

    ``ters=True`` ise hedefin terimleri ÇEVRİLİR (``P,S``); aks-i müstevî
    budur. ``ters=False`` iken hedef ``(S,P)`` üzerindedir.
    """
    B = tutuyor_mu
    def fk(m, x, y): return B(m, x, y, kaynak)
    def fh(m, x, y): return B(m, x, y, hedef)
    x, y = (P, S) if ters else (S, P)
    for m in _modeller(frozenset(bos_olmayan)):
        if fk(m, S, P) and not fh(m, x, y):
            return False
    return True


def aks_nakiz_gecerli_mi(kaynak: str, hedef: str) -> bool:
    """Aks-i nakîz: ``kaynak(S,P)`` ⟹ ``hedef(¬P, ¬S)``.

    Değillenmiş terimler için maskeler tümleyendir; bit işlemleri aynı
    kalır, yalnız maske değişir.
    """
    B = tutuyor_mu
    mx, my = ~MASKE[P] & TUM, ~MASKE[S] & TUM

    for m in range(256):
        if B(m, S, P, kaynak) and not B(m, mx, my, hedef, maskeli=True):
            return False
    return True


def sorites_gecerli_mi(zincir: Sequence[Tuple[int, int]], n_terim: int,
                       netice: Tuple[int, int],
                       bos_olmayan: Iterable[int] = ()) -> bool:
    """``A₁⊆A₂⊆…⊆A_k ⟹ A₁⊆A_k`` (tümel olumlu zincir).

    ``n_terim`` terim üzerinde ``2^{2^{n}}`` model olurdu; bunun yerine
    ATOM temsili yine kullanılır: atom sayısı ``2^n``, model sayısı
    ``2^{2^n}``. ``n ≤ 4`` için ``2^{16} = 65 536`` model, tam sayımla
    işlenebilir.
    """
    if n_terim > 4:
        raise ValueError("sorites tam sayımı 4 terime kadar")
    atom_sayisi = 1 << n_terim
    maske = [sum(1 << a for a in range(atom_sayisi) if (a >> t) & 1)
             for t in range(n_terim)]
    sart = [maske[t] for t in bos_olmayan]
    for m in range(1 << atom_sayisi):
        if any((m & s) == 0 for s in sart):
            continue
        if all((m & maske[x] & ~maske[y]) == 0 for (x, y) in zincir):
            if (m & maske[netice[0]] & ~maske[netice[1]]) != 0:
                return False
    return True


def _rapor_mizan_kiyas() -> str:
    faraziyesiz = gecerli_darblar()
    faraziyeli = gecerli_darblar((S, M, P))
    fark = [x for x in faraziyeli if x not in faraziyesiz]

    satir = ["=== kıyas-ı iktiranî: tam model sayımı ===",
             "model uzayı: 2⁸ = 256 (tekli yüklem mantığında TAM)",
             "sınanan darb-şekil bileşimi: %d" % len(butun_darblar()),
             "",
             "varlık faraziyesi YOK  → geçerli darb: %d" % len(faraziyesiz),
             "varlık faraziyesi VAR  → geçerli darb: %d" % len(faraziyeli),
             "aradaki fark (faraziyeye MUHTAÇ olanlar): %d" % len(fark),
             ""]
    satir.append("Faraziyeye muhtaç darblar ve muhtaç oldukları terim:")
    for (s, d) in fark:
        asg = asgari_varlik_faraziyesi(s, d)
        terimler = ", ".join(TERIM_ADI[t] for t in sorted(asg or ()))
        satir.append("  %d. şekil %-3s %-10s → %s boş olmamalı"
                     % (s, d, DARB_ADI.get((s, d), "(adsız)"), terimler))
    satir.append("")
    satir.append("Adlandırılmış 24 darbın hepsi faraziyeli listede mi: %s"
                 % all(k in faraziyeli for k in DARB_ADI))
    return "\n".join(satir)


# ====================================================================
#  mizan/cikarim.py
# ====================================================================

def aksiyom(A: Onerme = None, B: Onerme = None,
                     C: Onerme = None, no: int = 1,
                     ne: str = "kur"):
    """HANGİ AKSİYOM ŞEMASI -- tek terkip (kütük H226).

    Küme: ``aksiyom1/2/3`` (şemayı **kuran** üç isim) ve
    ``_esle_aks1/2/3`` + ``_aksiyom_ornegi_mi`` (aynı üç şemayı elle
    **eşleyen** dört isim). Yedi isim, tek amelin iki yönü idi ve
    ikisi birbirinden **kopuktu**: şema değişse eşleyicinin de elle
    değişmesi gerekiyordu; ikisinin ayrı yazılması sessiz bir kayma
    kapısıydı.

    Terkipte şema **bir kere** yazılır, eşleme ondan **türetilir**:
    şema taze meta-değişkenlerle kurulur ve formül ona
    **birleştirme** (unification) ile eşlenir. Böylece eşleyicinin
    şemadan sapması cebren imkânsızdır.

    ==============  ==================================================
    ``ne``          döndürdüğü
    ==============  ==================================================
    ``kur``         ``no``lu şemanın ``A,B,C`` ile örneği
    ``örnek_mi``    ``A`` formülü **herhangi** bir şemanın örneği mi
    ``şema``        ``no``lu şema, meta-değişkenlerle
    ==============  ==================================================

    Şemalar (Łukasiewicz'in klasik üçlüsü):

    1. ``A → (B → A)``                       -- zayıflatma
    2. ``(A → (B → C)) → ((A → B) → (A → C))`` -- dağılma
    3. ``(¬B → ¬A) → (A → B)``               -- transpozisyon (KLASİK)

    Üçüncüsü sezgiselci hesapta **yoktur**; onunla ``¬¬A → A``
    türetilir ve hesap klasikleşir. ``sezgisel_ispatlanabilir``
    (Dyckhoff G4ip) bu farkı ölçer.
    """
    _MD = (deg("#A"), deg("#B"), deg("#C"))

    def sema(k: int, a: Onerme, b: Onerme, c: Onerme) -> Onerme:
        if k == 1:
            return ise(a, ise(b, a))
        if k == 2:
            return ise(ise(a, ise(b, c)), ise(ise(a, b), ise(a, c)))
        if k == 3:
            return ise(ise(degil(b), degil(a)), ise(a, b))
        raise ValueError("aksiyom şeması bilinmiyor: %r" % (k,))

    def birlestir(kalip: Onerme, f: Onerme, bag: dict) -> bool:
        """Kalıptaki meta-değişkenler formülün alt ağaçlarına oturuyor mu?"""
        if kalip in _MD:
            onceki = bag.get(kalip)
            if onceki is None:
                bag[kalip] = f
                return True
            return onceki is f
        if kalip.etiket != f.etiket or len(kalip.altlar) != len(f.altlar):
            return False
        return all(birlestir(u, v, bag)
                   for u, v in zip(kalip.altlar, f.altlar))

    if ne == "şema":
        return sema(no, *_MD)
    if ne == "kur":
        return sema(no, A, B, C)
    if ne == "örnek_mi":
        return any(birlestir(sema(k, *_MD), A, {}) for k in (1, 2, 3))
    raise ValueError("aksiyom kipi bilinmiyor: %r" % (ne,))


AKSIYOM_NOLARI: Tuple[int, ...] = (1, 2, 3)


class HilbertHatasi(Exception):
    pass


def hilbert_denetle(adimlar: Sequence[Tuple[str, object]]) -> Onerme:
    """Bir Hilbert türetimini adım adım DENETLER ve son satırı verir.

    Her adım ya ``("aks", formül)`` ya ``("mp", i, j)`` biçimindedir;
    ``mp`` adımında ``i``. satır ``A``, ``j``. satır ``A → B`` olmalıdır.

    Aksiyom adımları ayrıca **totoloji olduklarına** göre değil, üç
    şemadan birinin örneği olduklarına göre denetlenir -- yoksa denetleyici
    her totolojiyi kabul eder ve hiçbir şey ispatlamış olmaz.
    """
    satirlar: List[Onerme] = []
    for k, adim in enumerate(adimlar):
        if adim[0] == "aks":
            f = adim[1]
            if not isinstance(f, Onerme):
                raise HilbertHatasi("%d. satır: formül bekleniyordu" % k)
            if not aksiyom(f, ne="örnek_mi"):
                raise HilbertHatasi("%d. satır aksiyom şeması değil: %s" % (k, f))
            satirlar.append(f)
        elif adim[0] == "mp":
            i, j = adim[1], adim[2]                       # type: ignore[misc]
            A, imp = satirlar[i], satirlar[j]             # type: ignore[index]
            if imp.etiket != ISE or imp.altlar[0] is not A:
                raise HilbertHatasi(
                    "%d. satır modus ponens değil: %s ile %s" % (k, A, imp))
            satirlar.append(imp.altlar[1])
        else:
            raise HilbertHatasi("%d. satır: bilinmeyen adım %r" % (k, adim[0]))
    if not satirlar:
        raise HilbertHatasi("boş türetim")
    return satirlar[-1]


def ozdeslik_turetimi(A: Onerme) -> List[Tuple[str, object]]:
    """``A → A``ın klasik beş satırlık Hilbert türetimi.

    Aksiyom şemalarından yalnız modus ponens ile; bu, sistemin
    ``A → A``yı aksiyom olarak İSTEMEDİĞİNİN ispatıdır.
    """
    AA = ise(A, A)
    return [
        ("aks", aksiyom(A, AA, A, no=2)),                       # 0
        ("aks", aksiyom(A, AA, no=1)),                          # 1
        ("mp", 1, 0),                                      # 2: (A→(A→A))→(A→A)
        ("aks", aksiyom(A, A, no=1)),                           # 3: A→(A→A)
        ("mp", 3, 2),                                      # 4: A→A
    ]


Sekans = Tuple[FrozenSet[Onerme], FrozenSet[Onerme]]


def _sekans(sol: Sequence[Onerme], sag: Sequence[Onerme]) -> Sekans:
    return (frozenset(sol), frozenset(sag))


class LKAdim:
    """Bir ispat ağacı düğümü: kural adı, sekans, alt ispatlar."""

    __slots__ = ("kural", "sekans", "altlar")

    def __init__(self, kural: str, sekans: Sekans,
                 altlar: Tuple["LKAdim", ...] = ()) -> None:
        self.kural = kural
        self.sekans = sekans
        self.altlar = altlar

    def derinlik(self) -> int:
        return 1 + max((a.derinlik() for a in self.altlar), default=0)

    def dugum_sayisi(self) -> int:
        return 1 + sum(a.dugum_sayisi() for a in self.altlar)


def _yaz_sekans(s: Sekans) -> str:
    sol = ", ".join(sorted(yaz(f) for f in s[0]))
    sag = ", ".join(sorted(yaz(f) for f in s[1]))
    return "%s ⊢ %s" % (sol, sag)


_LK_ONBELLEK: Dict[Sekans, Optional[LKAdim]] = {}


def lk_ispat(sol: Sequence[Onerme], sag: Sequence[Onerme]) -> Optional[LKAdim]:
    """``Γ ⊢ Δ`` için KESMESİZ ispat arar.

    Bütün kurallar tersinir olduğundan geri izleme gerekmez: bir bileşik
    formül seçilir, kuralı uygulanır, alt sekanslar ispatlanır. Ölçü her
    adımda kesin azaldığı için arama sonlanır.

    Bellekleme sekans üzerinedir; aynı alt sekans farklı dallarda tekrar
    tekrar doğar (bilhassa ``L→`` ve ``R∧``'da) ve bir kere çözülmesi
    yeter. Netice değişmez.
    """
    return _lk(_sekans(sol, sag))


def _lk(s: Sekans) -> Optional[LKAdim]:
    onb = _LK_ONBELLEK.get(s)
    if onb is not None or s in _LK_ONBELLEK:
        return onb
    sonuc = _lk_coz(s)
    _LK_ONBELLEK[s] = sonuc
    return sonuc


def _lk_coz(s: Sekans) -> Optional[LKAdim]:
    sol, sag = s
    # aksiyom: ortak formül, solda ⊥, yahut sağda ⊤
    if sol & sag:
        return LKAdim("Aks", s)
    if any(f.etiket == YANLIS for f in sol):
        return LKAdim("L⊥", s)
    if any(f.etiket == DOGRU for f in sag):
        return LKAdim("R⊤", s)

    # bileşik bir formül seç ve kuralını uygula (hepsi tersinir)
    for f in sol:
        e = f.etiket
        if e == DEGIL:
            alt = _lk((sol - {f}, sag | {f.altlar[0]}))
            return LKAdim("L¬", s, (alt,)) if alt else None
        if e == VE:
            a, b = f.altlar
            alt = _lk(((sol - {f}) | {a, b}, sag))
            return LKAdim("L∧", s, (alt,)) if alt else None
        if e == VEYA:
            a, b = f.altlar
            k = sol - {f}
            l = _lk((k | {a}, sag))
            if l is None:
                return None
            r = _lk((k | {b}, sag))
            return LKAdim("L∨", s, (l, r)) if r else None
        if e == ISE:
            a, b = f.altlar
            k = sol - {f}
            l = _lk((k, sag | {a}))
            if l is None:
                return None
            r = _lk((k | {b}, sag))
            return LKAdim("L→", s, (l, r)) if r else None
        if e in (ANCAK, XOR):
            alt = _lk(((sol - {f}) | {_ac(f)}, sag))
            return LKAdim("L%s" % ("↔" if e == ANCAK else "⊻"), s,
                          (alt,)) if alt else None

    for f in sag:
        e = f.etiket
        if e == DEGIL:
            alt = _lk((sol | {f.altlar[0]}, sag - {f}))
            return LKAdim("R¬", s, (alt,)) if alt else None
        if e == VEYA:
            a, b = f.altlar
            alt = _lk((sol, (sag - {f}) | {a, b}))
            return LKAdim("R∨", s, (alt,)) if alt else None
        if e == VE:
            a, b = f.altlar
            k = sag - {f}
            l = _lk((sol, k | {a}))
            if l is None:
                return None
            r = _lk((sol, k | {b}))
            return LKAdim("R∧", s, (l, r)) if r else None
        if e == ISE:
            a, b = f.altlar
            alt = _lk((sol | {a}, (sag - {f}) | {b}))
            return LKAdim("R→", s, (alt,)) if alt else None
        if e in (ANCAK, XOR):
            alt = _lk((sol, (sag - {f}) | {_ac(f)}))
            return LKAdim("R%s" % ("↔" if e == ANCAK else "⊻"), s,
                          (alt,)) if alt else None

    return None                      # yalnız atomlar kaldı ve kesişmiyorlar


def _ac(f: Onerme) -> Onerme:
    """``↔`` ve ``⊻``yi temel bağlaçlara açar."""
    a, b = f.altlar
    if f.etiket == ANCAK:
        return ve(ise(a, b), ise(b, a))
    return ve(veya(a, b), degil(ve(a, b)))


def lk_ispatlanabilir(sol: Sequence[Onerme], sag: Sequence[Onerme]) -> bool:
    return lk_ispat(sol, sag) is not None


def _olcu(f: Onerme) -> int:
    """Dyckhoff'un ağırlığı: her düğüm 1, gerektirmenin öncülü ağırlıklı.

    Bu ölçü, ``L→`` dallarının hepsinde kesin azalır; sonlanmanın delili
    budur.
    """
    e = f.etiket
    if e in (DEG, DOGRU, YANLIS):
        return 1
    if e == DEGIL:
        return _olcu(f.altlar[0]) + 2
    a, b = f.altlar
    if e == ISE:
        return _olcu(a) + _olcu(b) + 1
    if e in (VE, VEYA):
        return _olcu(a) + _olcu(b) + 1
    return _olcu(_ac(f)) + 1


_G4_ONBELLEK: Dict[Tuple[FrozenSet[Onerme], Onerme], bool] = {}


def sezgisel_ispatlanabilir(varsayimlar: Sequence[Onerme],
                            hedef: Onerme) -> bool:
    """``Γ ⇒ G`` sezgisel mantıkta ispatlanabilir mi? (G4ip)"""
    return _g4(frozenset(varsayimlar), hedef)


def _g4(G: FrozenSet[Onerme], hedef: Onerme) -> bool:
    anahtar = (G, hedef)
    onb = _G4_ONBELLEK.get(anahtar)
    if onb is not None:
        return onb
    sonuc = _g4_coz(G, hedef)
    _G4_ONBELLEK[anahtar] = sonuc
    return sonuc


def _g4_coz(G: FrozenSet[Onerme], hedef: Onerme) -> bool:
    # ⊥ solda ise her şey çıkar
    if any(f.etiket == YANLIS for f in G):
        return True
    if hedef.etiket == DOGRU:
        return True
    # eksen: atomik hedef solda duruyorsa
    if hedef in G:
        return True

    # --- tersinir SOL kuralları (öncelikli) --------------------------
    for f in G:
        e = f.etiket
        if e == VE:
            a, b = f.altlar
            return _g4((G - {f}) | {a, b}, hedef)
        if e == VEYA:
            a, b = f.altlar
            k = G - {f}
            return _g4(k | {a}, hedef) and _g4(k | {b}, hedef)
        if e == DEGIL:
            # ¬A ≡ A → ⊥ ; L→ dallarına havale et
            continue
        if e in (ANCAK, XOR):
            return _g4((G - {f}) | {_ac(f)}, hedef)

    # --- L→ : öncülün ŞEKLİNE göre dört dal --------------------------
    for f in G:
        onc = _oncul(f)
        if onc is None:
            continue
        C, B = onc
        k = G - {f}
        ce = C.etiket
        if ce in (DEG, DOGRU):
            # L0→ : C atomik ve zaten solda ise B'yi sal
            if C in G:
                return _g4(k | {B}, hedef)
            continue
        if ce == YANLIS:
            return _g4(k, hedef)          # ⊥→B aşikâr, düşür
        if ce == VE:
            c1, c2 = C.altlar
            return _g4(k | {ise(c1, ise(c2, B))}, hedef)
        if ce == VEYA:
            c1, c2 = C.altlar
            return _g4(k | {ise(c1, B), ise(c2, B)}, hedef)
        if ce == ISE:
            c1, c2 = C.altlar
            return (_g4(k | {ise(c2, B), c1}, c2) and _g4(k | {B}, hedef))
        if ce == DEGIL:
            # (¬D → B) ≡ ((D → ⊥) → B)
            d = C.altlar[0]
            return (_g4(k | {ise(yanlis(), B), d}, yanlis())
                    and _g4(k | {B}, hedef))
        if ce in (ANCAK, XOR):
            return _g4(k | {ise(_ac(C), B)}, hedef)

    # --- tersinir SAĞ kuralı -----------------------------------------
    if hedef.etiket == ISE:
        a, b = hedef.altlar
        return _g4(G | {a}, b)
    if hedef.etiket == DEGIL:
        return _g4(G | {hedef.altlar[0]}, yanlis())
    if hedef.etiket == VE:
        a, b = hedef.altlar
        return _g4(G, a) and _g4(G, b)
    if hedef.etiket in (ANCAK, XOR):
        return _g4(G, _ac(hedef))

    # --- tersinmez SAĞ kuralı: R∨ (geri izleme) ----------------------
    if hedef.etiket == VEYA:
        a, b = hedef.altlar
        return _g4(G, a) or _g4(G, b)

    return False


def _oncul(f: Onerme) -> Optional[Tuple[Onerme, Onerme]]:
    """``f`` bir gerektirme ise ``(öncül, ardıl)``; ``¬A`` ise ``(A, ⊥)``."""
    if f.etiket == ISE:
        return (f.altlar[0], f.altlar[1])
    if f.etiket == DEGIL:
        return (f.altlar[0], yanlis())
    return None


def _rapor_mizan_cikarim() -> str:
    A, B, C = deg("A"), deg("B"), deg("C")
    satir = ["=== çıkarım hesapları ==="]

    son = hilbert_denetle(ozdeslik_turetimi(A))
    satir.append("Hilbert: A→A beş satırda türetildi, denetlendi → %s" % yaz(son))

    ornekler = [
        ("Peirce", ise(ise(ise(A, B), A), A)),
        ("üçüncü hâlin imkânsızlığı", veya(A, degil(A))),
        ("çifte değilleme elemesi", ise(degil(degil(A)), A)),
        ("çifte değilleme girişi", ise(A, degil(degil(A)))),
        ("ex falso", ise(yanlis(), A)),
        ("modus tollens", ise(ve(ise(A, B), degil(B)), degil(A))),
        ("De Morgan (→)", ise(degil(ve(A, B)), veya(degil(A), degil(B)))),
        ("De Morgan (←)", ise(veya(degil(A), degil(B)), degil(ve(A, B)))),
        ("dağılma", ancak(ve(A, veya(B, C)), veya(ve(A, B), ve(A, C)))),
    ]
    satir.append("")
    satir.append("%-28s %-8s %-8s %s" % ("formül", "klasik", "sezgisel", "tablo"))
    for ad, f in ornekler:
        satir.append("%-28s %-8s %-8s %s"
                     % (ad,
                        "✓" if lk_ispatlanabilir([], [f]) else "✗",
                        "✓" if sezgisel_ispatlanabilir([], f) else "✗",
                        "✓" if hukum(f, ne="totoloji") else "✗"))
    return "\n".join(satir)


# ====================================================================
#  mizan/kiplik.py
# ====================================================================

class Cerceve:
    """``⟨W, R⟩``; ``R[w]`` erişilebilir dünyaların bit maskesi."""

    __slots__ = ("n", "R", "tum")

    def __init__(self, n: int, R: Sequence[int]) -> None:
        self.n = n
        self.R = tuple(R)
        self.tum = (1 << n) - 1

    # -- bağıntı şartları ---------------------------------------------
    def yansimali_mi(self) -> bool:
        return all((self.R[w] >> w) & 1 for w in range(self.n))

    def gecisli_mi(self) -> bool:
        for w in range(self.n):
            for v in range(self.n):
                if (self.R[w] >> v) & 1 and (self.R[v] & ~self.R[w] & self.tum):
                    return False
        return True

    def simetrik_mi(self) -> bool:
        return all(not ((self.R[w] >> v) & 1) or ((self.R[v] >> w) & 1)
                   for w in range(self.n) for v in range(self.n))

    def oklidyen_mi(self) -> bool:
        """``wRv ∧ wRu ⟹ vRu``."""
        for w in range(self.n):
            for v in range(self.n):
                if (self.R[w] >> v) & 1 and (self.R[w] & ~self.R[v] & self.tum):
                    return False
        return True

    def seri_mi(self) -> bool:
        return all(self.R[w] != 0 for w in range(self.n))

    def __repr__(self) -> str:
        kenar = ["%d→%d" % (w, v) for w in range(self.n)
                 for v in range(self.n) if (self.R[w] >> v) & 1]
        return "Çerçeve(%d, {%s})" % (self.n, ", ".join(kenar))


def butun_cerceveler(n: int) -> List[Cerceve]:
    """``n`` dünyalı BÜTÜN çerçeveler: ``2^{n²}`` tane."""
    if n > 3:
        raise ValueError("tam çerçeve sayımı 3 dünyaya kadar (2⁹ = 512)")
    cerceveler = []
    for kod in range(1 << (n * n)):
        R = [(kod >> (w * n)) & ((1 << n) - 1) for w in range(n)]
        cerceveler.append(Cerceve(n, R))
    return cerceveler


def dogruluk(f: Onerme, c: Cerceve, V: Dict[str, int]) -> int:
    """Formülün doğru olduğu dünyaların bit maskesi."""
    e = f.etiket
    if e == DOGRU:
        return c.tum
    if e == YANLIS:
        return 0
    if e == DEG:
        return V.get(f.ad, 0)                              # type: ignore[arg-type]
    if e == DEGIL:
        return ~dogruluk(f.altlar[0], c, V) & c.tum
    if e == KUTU:
        alt = dogruluk(f.altlar[0], c, V)
        return sum(1 << w for w in range(c.n)
                   if (c.R[w] & ~alt & c.tum) == 0)
    if e == ELMAS:
        alt = dogruluk(f.altlar[0], c, V)
        return sum(1 << w for w in range(c.n) if c.R[w] & alt)
    a = dogruluk(f.altlar[0], c, V)
    b = dogruluk(f.altlar[1], c, V)
    if e == VE:
        return a & b
    if e == VEYA:
        return a | b
    if e == ISE:
        return (~a | b) & c.tum
    if e == ANCAK:
        return ~(a ^ b) & c.tum
    return a ^ b                                            # XOR


def cerceve_gecerli_mi(f: Onerme, c: Cerceve) -> bool:
    """Formül, çerçevede BÜTÜN değerlemeler ve dünyalarda doğru mu?"""
    degiskenler = sorted(f.degiskenler())
    k = len(degiskenler)
    if k == 0:
        return dogruluk(f, c, {}) == c.tum
    if k * c.n > 12:
        raise ValueError("değerleme sayımı 2¹² ile sınırlı")
    for kod in range(1 << (k * c.n)):
        V = {ad: (kod >> (i * c.n)) & c.tum
             for i, ad in enumerate(degiskenler)}
        if dogruluk(f, c, V) != c.tum:
            return False
    return True


_A = deg("p")


AKSIYOM: Dict[str, Onerme] = {
    "K": ise(kutu(ise(_A, deg("q"))), ise(kutu(_A), kutu(deg("q")))),
    "T": ise(kutu(_A), _A),
    "4": ise(kutu(_A), kutu(kutu(_A))),
    "5": ise(elmas(_A), kutu(elmas(_A))),
    "B": ise(_A, kutu(elmas(_A))),
    "D": ise(kutu(_A), elmas(_A)),
}


SART: Dict[str, Callable[[Cerceve], bool]] = {
    "K": lambda c: True,                     # her çerçevede geçerli
    "T": Cerceve.yansimali_mi,
    "4": Cerceve.gecisli_mi,
    "5": Cerceve.oklidyen_mi,
    "B": Cerceve.simetrik_mi,
    "D": Cerceve.seri_mi,
}


SART_ADI = {"K": "her çerçeve", "T": "yansımalı", "4": "geçişli",
            "5": "Öklidyen", "B": "simetrik", "D": "seri"}


def karsilik_dogrula(ad: str, n: int = 3) -> Dict[str, object]:
    """Aksiyomun geçerli olduğu çerçeveler ile şartı sağlayanlar aynı mı?"""
    f = AKSIYOM[ad]
    sart = SART[ad]
    gecerli, sartli, ayrik = set(), set(), []
    for i, c in enumerate(butun_cerceveler(n)):
        g = cerceve_gecerli_mi(f, c)
        s = sart(c)
        if g:
            gecerli.add(i)
        if s:
            sartli.add(i)
        if g != s:
            ayrik.append((i, c, g, s))
    return {
        "aksiyom": ad,
        "şart": SART_ADI[ad],
        "çerçeve_sayısı": 1 << (n * n),
        "aksiyom_geçerli": len(gecerli),
        "şartı_sağlayan": len(sartli),
        "karşılık_tam": not ayrik,
        "ayrık_örnek": ayrik[:1],
    }


def dual_ozdeslikleri(n: int = 3) -> Dict[str, bool]:
    """``◇A ≡ ¬□¬A`` ve ``□A ≡ ¬◇¬A`` bütün çerçevelerde."""
    A = deg("p")
    d1 = ancak(elmas(A), degil(kutu(degil(A))))
    d2 = ancak(kutu(A), degil(elmas(degil(A))))
    return {
        "◇A ≡ ¬□¬A": all(cerceve_gecerli_mi(d1, c) for c in butun_cerceveler(n)),
        "□A ≡ ¬◇¬A": all(cerceve_gecerli_mi(d2, c) for c in butun_cerceveler(n)),
    }


def odev(a: Onerme, ne: str = "ödev") -> Onerme:
    """BORÇ MU, CAİZ Mİ, YASAK MI -- tek terkip (kütük H226).

    Küme: ``O_``, ``Pm``, ``F_``. Üç isim, ``□``nun etrafına iki değil
    işaretinin **nereye** konduğundan ibaretti:

    ==============  ====================  ==========================
    ``ne``          formül                halkça
    ==============  ====================  ==========================
    ``ödev``        ``□φ``                yapılması gereken
    ``caiz``        ``¬□¬φ``              yapılması yasak olmayan
    ``yasak``       ``□¬φ``               yapılmaması gereken
    ==============  ====================  ==========================

    Deontik ``□`` alethik ``□``dan **seriliği** ile ayrılır (D:
    ``□φ → ◇φ``); refleksiflik (T: ``□φ → φ``) deontik mantıkta
    **istenmez**, zira "ödev olan hep yapılmış olurdu". Serilik şartının
    ihmali bu üç kipin tutarlılığını çökertir ve
    ``deontik_tutarlilik`` bunu ölçer.
    """
    if ne == "ödev":
        return kutu(a)
    if ne == "caiz":
        return degil(kutu(degil(a)))
    if ne == "yasak":
        return kutu(degil(a))
    raise ValueError("deontik kip bilinmiyor: %r" % (ne,))


def deontik_tutarlilik(n: int = 3) -> Dict[str, object]:
    """Deontik mantığın taşıyıcı şartı: ``D`` (serilik).

    ``D`` olmadan ``Oφ ∧ O¬φ`` mümkün olur, yani birbiriyle çelişen iki
    ödev aynı anda yüklenebilir. Serilik bunu imkânsız kılar; aşağıda
    ölçülür.
    """
    A = deg("p")
    celiski = ve(odev(A),
                    odev(degil(A)))
    seri, seri_disi = 0, 0
    for c in butun_cerceveler(n):
        # çelişkili ödev SAĞLANABİLİR mi? (bir değerleme ve dünya bul)
        bulundu = False
        for kod in range(1 << c.n):
            V = {"p": kod}
            if dogruluk(celiski, c, V):
                bulundu = True
                break
        if c.seri_mi():
            seri += int(bulundu)
        else:
            seri_disi += int(bulundu)
    return {
        "seri_çerçevede_çelişkili_ödev": seri,           # 0 olmalı
        "seri_olmayanda_çelişkili_ödev": seri_disi,      # > 0 olmalı
        "D_çelişkili_ödevi_engelliyor": seri == 0,
        "Pm_ve_F_dualleri": all(
            cerceve_gecerli_mi(
                ancak(odev(A, "caiz"),
                      degil(odev(A, "yasak"))), c)
            for c in butun_cerceveler(n)),
    }


class Iz:
    """Sonlu bir zaman izi: ``t = 0,…,L-1`` anlarında değerlemeler."""

    __slots__ = ("L", "V")

    def __init__(self, L: int, V: Dict[str, int]) -> None:
        self.L = L
        self.V = V                     # değişken → anların bit maskesi

    def tum(self) -> int:
        return (1 << self.L) - 1


def ltl_dogruluk(f: Onerme, iz: Iz, isim: str = "") -> int:
    """Formülün doğru olduğu ANLARIN bit maskesi (gelecek işlemcileri)."""
    e = f.etiket
    if e == DOGRU:
        return iz.tum()
    if e == YANLIS:
        return 0
    if e == DEG:
        return iz.V.get(f.ad, 0)                          # type: ignore[arg-type]
    if e == DEGIL:
        return ~ltl_dogruluk(f.altlar[0], iz) & iz.tum()
    a = ltl_dogruluk(f.altlar[0], iz)
    if e in (KUTU, ELMAS):
        raise ValueError("LTL'de □/◇ yerine G/F kullanılır")
    b = ltl_dogruluk(f.altlar[1], iz)
    if e == VE:
        return a & b
    if e == VEYA:
        return a | b
    if e == ISE:
        return (~a | b) & iz.tum()
    if e == ANCAK:
        return ~(a ^ b) & iz.tum()
    return a ^ b


def sonra(a: int, b: int = -1, L: int = 0,
                 ne: str = "kadar") -> int:
    """BUNDAN SONRA NE OLACAK -- tek terkip (kütük H226).

    Küme: ``G`` (daima), ``F`` (bir an), ``U`` (-e kadar). Üçü ayrı
    yazılmıştı; hâlbuki ikisi üçüncüsünün **tanımıdır**:

        ``Fφ ≡ ⊤ U φ``          ``Gφ ≡ ¬(⊤ U ¬φ)``

    Geriye tek çekirdek kalır ve o da **tek geriye doğru taramadır**:

        ``t ∈ φUψ  ⟺  ψ(t) ∨ (φ(t) ∧ t+1 ∈ φUψ)``

    Sonlu iz üstünde bu özyineleme ``L−1``den ``0``a bir taşımayla
    okunur; ``O(L)``dur ve maskeler bit paralel tutulur.

    ==============  ==================================================
    ``ne``          döndürdüğü
    ==============  ==================================================
    ``kadar``       ``a U b``
    ``daima``       ``G a``
    ``biran``       ``F a``
    ==============  ==================================================

    **T88'in tashihli hâli**: "-e kadar"ın alt sınırı **şimdidir**.
    Kaynak metinde alt sınır yoktu (``∀t' < t``), yani sonsuz geçmişte
    de ``φ``nin sağlanması isteniyordu; oysa "-e kadar" şimdiden başlar.
    """
    tum = (1 << L) - 1
    if ne == "daima":
        a, b = tum, (~a) & tum          # G a = ¬(⊤ U ¬a)
    elif ne == "biran":
        a, b = tum, a                   # F a = ⊤ U a
    elif ne != "kadar":
        raise ValueError("zaman kipi bilinmiyor: %r" % (ne,))
    sonuc = 0
    tasima = False
    for t in range(L - 1, -1, -1):
        tasima = bool((b >> t) & 1) or (bool((a >> t) & 1) and tasima)
        if tasima:
            sonuc |= 1 << t
    return (~sonuc) & tum if ne == "daima" else sonuc


def ltl_ozdeslikleri(L: int = 6, deneme: int = 400,
                     tohum: int = 0) -> Dict[str, bool]:
    """``G``, ``F``, ``U`` arasındaki klasik özdeşlikler.

    Rastgele izlerde tam sayımla sınanır; hepsi bit maskesi eşitliğidir,
    yaklaşıklık yoktur.
    """
    import random
    rng = random.Random(tohum)
    tum = (1 << L) - 1
    ozdeslik = {
        "Gφ ≡ ¬F¬φ": True,
        "Fφ ≡ ⊤ U φ": True,
        "φUψ ⟹ Fψ": True,
        "G(φ∧ψ) ≡ Gφ ∧ Gψ": True,
    }
    for _ in range(deneme):
        a, b = rng.randrange(1 << L), rng.randrange(1 << L)
        if sonra(a, L=L, ne="daima") != (~sonra(~a & tum, L=L, ne="biran") & tum):
            ozdeslik["Gφ ≡ ¬F¬φ"] = False
        if sonra(b, L=L, ne="biran") != sonra(tum, b, L):
            ozdeslik["Fφ ≡ ⊤ U φ"] = False
        if sonra(a, b, L) & ~sonra(b, L=L, ne="biran") & tum:
            ozdeslik["φUψ ⟹ Fψ"] = False
        if (sonra(a & b, L=L, ne="daima")
                != sonra(a, L=L, ne="daima")
                & sonra(b, L=L, ne="daima")):
            ozdeslik["G(φ∧ψ) ≡ Gφ ∧ Gψ"] = False
    return ozdeslik


def _rapor_mizan_kiplik() -> str:
    satir = ["=== kiplik: Kripke karşılıkları (3 dünyalı BÜTÜN 512 çerçeve) ===",
             "%-4s %-14s %8s %8s  %s"
             % ("aks", "şart", "geçerli", "şartlı", "karşılık tam")]
    for ad in ("K", "T", "4", "5", "B", "D"):
        r = karsilik_dogrula(ad)
        satir.append("%-4s %-14s %8d %8d  %s"
                     % (ad, r["şart"], r["aksiyom_geçerli"],
                        r["şartı_sağlayan"], r["karşılık_tam"]))
    satir.append("")
    for k, v in dual_ozdeslikleri().items():
        satir.append("dual: %-14s %s" % (k, v))
    satir.append("")
    d = deontik_tutarlilik()
    satir.append("deontik: D çelişkili ödevi engelliyor = %s"
                 % d["D_çelişkili_ödevi_engelliyor"])
    satir.append("deontik: seri OLMAYAN çerçevede çelişkili ödev bulunan = %d"
                 % d["seri_olmayanda_çelişkili_ödev"])
    satir.append("deontik: Pmφ ≡ ¬Fφ dualı = %s" % d["Pm_ve_F_dualleri"])
    satir.append("")
    for k, v in ltl_ozdeslikleri().items():
        satir.append("LTL: %-20s %s" % (k, v))
    return "\n".join(satir)


# ====================================================================
#  mizan/cokdegerli.py
# ====================================================================

TNorm = Callable[[float, float], float]


Kalinti = Callable[[float, float], float]


EPS = 1e-9


def _izgara(n: int = 21) -> List[float]:
    return [k / (n - 1) for k in range(n)]


def derece(a=None, b=None, ne: str = "Łukasiewicz",
                          tur: str = "ve", p: float = 2.0):
    """İKİSİ BİRDEN NE KADAR DOĞRU -- **tek terkip** (kütük H226).

    Küme: sekiz t-normu (``t_lukasiewicz, t_godel, t_carpim, t_zayif,
    t_nilpotent_minimum, t_schweizer_sklar, t_yager, t_dombi``) ve dört
    kalıntısı (``i_lukasiewicz, i_godel, i_carpim,
    i_nilpotent_minimum``). On iki isim, **tek** amelin durakları idi:
    iki dereceli doğruluğu birleştirmek, yahut o birleştirmenin
    **eşleniğini** (kalıntı) almak.

    ==============  ==================================================
    ``tur``         döndürdüğü
    ==============  ==================================================
    ``ve``          ``a ⊗ b`` -- iki önerme birden ne kadar doğru
    ``ise``         ``a → b`` -- kalıntı (Galois eşleniği)
    ``çekirdek``    ``(⊗, →)`` çifti; kalıntısı yoksa ``(⊗, None)``
    ==============  ==================================================

    Adlar: ``Łukasiewicz``, ``Gödel``, ``çarpım``, ``nilpotent min``,
    ``en zayıf``, ``Schweizer-Sklar``, ``Yager``, ``Dombi``. Son üçü
    ``p`` parametresi alır.

    **T89 -- kalıntı eşlenikliği.** ``a → b = min(1, 1−a+b)``
    alındığında eşlenik t-norm ``min(a,b)`` **değildir**; kuvvetli ve
    ``a ⊗ b = max(0, a+b−1)``dir. Bu, kalıntı bağıntısının
    ``a ⊗ b ≤ c ⟺ a ≤ (b → c)`` tek satırından çıkar ve
    ``lukasiewicz_min_ile_bozulur`` bunu karşı örnekle mühürler.
    ``min`` ile eşlenen kalıntı Gödel gerektirmesidir, Łukasiewicz'inki
    değil.

    **T90 (çarpım kalıntısı):** ``min(1, b/a)`` ``a = 0``da tanımsızdır;
    kalıntı biçiminde yazılınca hem tanım kümesi tamamlanır hem ``min``
    gereksizleşir. **T94 (Dombi):** ``a = 0``da ``(1−a)/a`` patlar,
    ``T(0,b) = 0`` dalı açıkça yazılır. **T95 (Schweizer-Sklar):**
    ``max(0,·)`` kesmesi yalnız ``p > 0`` içindir; ``p < 0`` iken
    ``a^p + b^p − 1 > 0`` dâima sağlanır ve kesme yanlış dala götürür.
    """
    def T(a: float, b: float) -> float:
        if ne == "Łukasiewicz":
            return max(0.0, a + b - 1.0)          # KUVVETLİ ve
        if ne == "Gödel":
            return min(a, b)
        if ne == "çarpım":
            return a * b
        if ne == "nilpotent min":
            return min(a, b) if a + b > 1.0 else 0.0
        if ne == "en zayıf":                      # drastic product
            if a == 1.0:
                return b
            if b == 1.0:
                return a
            return 0.0
        if ne == "Schweizer-Sklar":
            if a == 0.0 or b == 0.0:
                return 0.0
            u = a ** p + b ** p - 1.0
            return (max(0.0, u) if p > 0 else u) ** (1.0 / p)
        if ne == "Yager":
            return 1.0 - min(1.0, ((1 - a) ** p + (1 - b) ** p) ** (1.0 / p))
        if ne == "Dombi":
            if a <= 0.0 or b <= 0.0:
                return 0.0
            if a >= 1.0:
                return b
            if b >= 1.0:
                return a
            u = ((1 - a) / a) ** p + ((1 - b) / b) ** p
            return 1.0 / (1.0 + u ** (1.0 / p))
        raise ValueError("t-normu bilinmiyor: %r" % (ne,))

    def I(a: float, b: float) -> float:
        if ne == "Łukasiewicz":
            return min(1.0, 1.0 - a + b)
        if ne == "Gödel":
            return 1.0 if a <= b else b
        if ne == "çarpım":
            return 1.0 if a <= b else b / a       # a > b ≥ 0 ⇒ a > 0
        if ne == "nilpotent min":
            return 1.0 if a <= b else max(1.0 - a, b)
        raise ValueError("bu t-normunun kapalı kalıntısı yazılmadı: %r"
                         % (ne,))

    if tur == "çekirdek":
        return T, (I if ne in KALINTILI else None)
    if tur == "ve":
        return T(float(a), float(b))
    if tur == "ise":
        return I(float(a), float(b))
    raise ValueError("kip bilinmiyor: %r" % (tur,))


KALINTILI: Tuple[str, ...] = ("Łukasiewicz", "Gödel", "çarpım",
                              "nilpotent min")


TNORM_ADLARI: Tuple[Tuple[str, str, float], ...] = (
    ("Łukasiewicz", "Łukasiewicz", 0.0),
    ("Gödel (min)", "Gödel", 0.0),
    ("çarpım", "çarpım", 0.0),
    ("nilpotent min", "nilpotent min", 0.0),
    ("Schweizer-Sklar p=2", "Schweizer-Sklar", 2.0),
    ("Schweizer-Sklar p=0.5", "Schweizer-Sklar", 0.5),
    ("Yager p=2", "Yager", 2.0),
    ("Dombi p=2", "Dombi", 2.0),
    ("en zayıf (drastic)", "en zayıf", 0.0),
)


TNORMLAR: Dict[str, TNorm] = {
    baslik: derece(ne=k, p=pp, tur="çekirdek")[0]
    for baslik, k, pp in TNORM_ADLARI}


KALINTILAR: Dict[str, Tuple[TNorm, Kalinti]] = {
    k: derece(ne=k, tur="çekirdek") for k in KALINTILI}




def tnorm_aksiyomlari(T: TNorm, n: int = 15,
                      tol: float = 1e-9) -> Dict[str, object]:
    """Değişme, birleşme, tekdüzelik, birim ve sınır şartları.

    Birleşme sayısal olarak denetlenir (kesirli üsler yüzünden tam
    eşitlik beklenmez); tolerans açıkça bildirilir.
    """
    g = _izgara(n)
    degisme = birlesme = tekduze = birim = sinir = True
    en_buyuk_birlesme_sapmasi = 0.0
    for a in g:
        if abs(T(a, 1.0) - a) > tol or T(a, 0.0) > tol:
            birim = False
        for b in g:
            if abs(T(a, b) - T(b, a)) > tol:
                degisme = False
            for c in g:
                s = abs(T(T(a, b), c) - T(a, T(b, c)))
                en_buyuk_birlesme_sapmasi = max(en_buyuk_birlesme_sapmasi, s)
                if s > 1e-7:
                    birlesme = False
            if b > a and T(a, 0.5) - T(b, 0.5) > tol:
                tekduze = False
    for a in g:
        if T(0.0, a) > tol or T(a, 0.0) > tol:
            sinir = False
    return {
        "değişme": degisme,
        "birleşme": birlesme,
        "birleşme_azamî_sapma": en_buyuk_birlesme_sapmasi,
        "tekdüzelik": tekduze,
        "birim T(a,1)=a": birim,
        "sınır T(a,0)=0": sinir,
        "t-normu": degisme and birlesme and tekduze and birim and sinir,
    }


def kalinti_saglaniyor_mu(T: TNorm, I: Kalinti, n: int = 21,
                          tol: float = 1e-9) -> Dict[str, object]:
    """``a ⊗ b ≤ c ⟺ a ≤ (b → c)`` ızgarada sınanır."""
    g = _izgara(n)
    ihlal: List[Tuple[float, float, float, str]] = []
    for a in g:
        for b in g:
            for c in g:
                sol = T(a, b) <= c + tol
                sag = a <= I(b, c) + tol
                if sol != sag:
                    ihlal.append((a, b, c, "⇒" if sol else "⇐"))
    return {
        "sağlanıyor": not ihlal,
        "ihlal_sayısı": len(ihlal),
        "ilk_ihlal": ihlal[0] if ihlal else None,
    }


def lukasiewicz_min_ile_bozulur(n: int = 21) -> Dict[str, object]:
    """**T89'un fiilî sağlaması.**

    Łukasiewicz gerektirmesi ``min`` ile eşlenik DEĞİLDİR; bağıntının
    bozulduğu somut bir üçlü gösterilir.
    """
    dogru = kalinti_saglaniyor_mu(derece(ne="Łukasiewicz", tur="çekirdek")[0], derece(ne="Łukasiewicz", tur="çekirdek")[1], n)
    yanlis = kalinti_saglaniyor_mu(derece(ne="Gödel", tur="çekirdek")[0], derece(ne="Łukasiewicz", tur="çekirdek")[1], n)
    return {
        "⊗ = max(0,a+b−1) ile kalıntı sağlanıyor": dogru["sağlanıyor"],
        "⊗ = min ile kalıntı sağlanıyor": yanlis["sağlanıyor"],
        "min ile ihlal sayısı": yanlis["ihlal_sayısı"],
        "min ile ilk ihlal (a,b,c)": yanlis["ilk_ihlal"],
    }


UC_DEGIL = (2, 1, 0)


UC_VE = [[0, 0, 0], [0, 1, 1], [0, 1, 2]]


UC_VEYA = [[0, 1, 2], [1, 1, 2], [2, 2, 2]]


def uc_ise_kleene(a: int, b: int) -> int:
    return UC_VEYA[UC_DEGIL[a]][b]


def uc_ise_lukasiewicz(a: int, b: int) -> int:
    """``a ≤ b`` ise 2; değilse ``2 − (a − b)``."""
    return 2 if a <= b else 2 - (a - b)


def uc_degerli_gecerli_mi(oncüller: Sequence[Callable[[Tuple[int, ...]], int]],
                          netice: Callable[[Tuple[int, ...]], int],
                          n_deg: int, belirlenmis: Tuple[int, ...]) -> bool:
    """Öncüller belirlenmiş değer alırken netice de alıyor mu?"""
    for atama in _uclu_atamalar(n_deg):
        if all(p(atama) in belirlenmis for p in oncüller):
            if netice(atama) not in belirlenmis:
                return False
    return True


def _uclu_atamalar(k: int) -> Iterable[Tuple[int, ...]]:
    if k == 0:
        yield ()
        return
    for kuyruk in _uclu_atamalar(k - 1):
        for v in (0, 1, 2):
            yield (v,) + kuyruk


def lp_patlamiyor() -> Dict[str, object]:
    """Priest'in LP'sinde ``A, ¬A ⊬ B`` -- ex falso İPTAL.

    LP'de ``b`` belirlenmiştir; ``A = b`` iken ``¬A = b`` de belirlenmiş
    olur, fakat ``B = 0`` seçilebilir. Klasik mantıkta (yalnız ``2``
    belirlenmiş) bu imkânsızdır.
    """
    A = lambda v: v[0]
    nA = lambda v: UC_DEGIL[v[0]]
    B = lambda v: v[1]
    lp = uc_degerli_gecerli_mi([A, nA], B, 2, (1, 2))
    klasik_gibi = uc_degerli_gecerli_mi([A, nA], B, 2, (2,))
    # önemsizleşmeme: çelişkiyi doğrulayan ama B'yi yalanlayan bir atama
    tanik = None
    for atama in _uclu_atamalar(2):
        if A(atama) in (1, 2) and nA(atama) in (1, 2) and B(atama) not in (1, 2):
            tanik = atama
            break
    return {
        "LP'de A,¬A ⊨ B": lp,                    # False olmalı
        "klasik belirlenmişle A,¬A ⊨ B": klasik_gibi,   # True olmalı
        "tanık (A,B) değerleri": tanik,
        "önemsizleşmiyor": (not lp) and klasik_gibi,
    }


TEMEL_YUKLEM = ("asti", "nāsti", "avaktavya")


def syadvada_modlari() -> List[Tuple[str, ...]]:
    """**T126'nın tashihli hâli**: yedi mod, üç yüklemin BOŞ OLMAYAN alt
    kümeleridir.

    ``2³ − 1 = 7``; yani "niçin yedi?" sorusunun cevabı türetilir,
    ezberlenmez. Sıralama, klasik ``saptabhaṅgī`` sırasıdır.
    """
    sira = [(0,), (1,), (0, 1), (2,), (0, 2), (1, 2), (0, 1, 2)]
    return [tuple(TEMEL_YUKLEM[i] for i in alt) for alt in sira]


def syadvada_tamlik() -> Dict[str, object]:
    modlar = syadvada_modlari()
    kumeler = {frozenset(m) for m in modlar}
    butun_bos_olmayan = {frozenset(TEMEL_YUKLEM[i] for i in alt)
                         for k in range(1, 4)
                         for alt in _alt_kumeler(3, k)}
    return {
        "mod_sayısı": len(modlar),
        "2³−1": 2 ** 3 - 1,
        "tam_ve_tekrarsız": kumeler == butun_bos_olmayan,
        "modlar": ["·".join(m) for m in modlar],
    }


def _alt_kumeler(n: int, k: int) -> Iterable[Tuple[int, ...]]:
    from itertools import combinations
    return combinations(range(n), k)


def _rapor_mizan_cokdegerli() -> str:
    satir = ["=== çok değerli ve bulanık mantıklar ===",
             "%-24s %-8s %-8s %-9s %-8s %s"
             % ("t-normu", "değişme", "birleşme", "tekdüze", "birim", "t-normu mu")]
    for ad, T in TNORMLAR.items():
        r = tnorm_aksiyomlari(T)
        satir.append("%-24s %-8s %-8s %-9s %-8s %s"
                     % (ad, r["değişme"], r["birleşme"], r["tekdüzelik"],
                        r["birim T(a,1)=a"], r["t-normu"]))
    satir.append("")
    satir.append("Kalıntı bağıntısı  a⊗b ≤ c ⟺ a ≤ (b→c):")
    for ad, (T, I) in KALINTILAR.items():
        r = kalinti_saglaniyor_mu(T, I)
        satir.append("  %-16s %s  (ihlal: %d)"
                     % (ad, r["sağlanıyor"], r["ihlal_sayısı"]))
    satir.append("")
    L = lukasiewicz_min_ile_bozulur()
    satir.append("T89 sağlaması -- Łukasiewicz gerektirmesi:")
    satir.append("  kuvvetli ve ile kalıntı: %s" % L["⊗ = max(0,a+b−1) ile kalıntı sağlanıyor"])
    satir.append("  min ile kalıntı        : %s  (ihlal %d, ilk: %s)"
                 % (L["⊗ = min ile kalıntı sağlanıyor"], L["min ile ihlal sayısı"],
                    L["min ile ilk ihlal (a,b,c)"]))
    satir.append("")
    p = lp_patlamiyor()
    satir.append("Paratutarlı LP: A,¬A ⊨ B → %s   (klasik belirlenmişle → %s)"
                 % (p["LP'de A,¬A ⊨ B"], p["klasik belirlenmişle A,¬A ⊨ B"]))
    satir.append("  önemsizleşmiyor: %s   tanık (A,B) = %s"
                 % (p["önemsizleşmiyor"], p["tanık (A,B) değerleri"]))
    satir.append("")
    s = syadvada_tamlik()
    satir.append("Syādvāda: %d mod = 2³−1 = %d, tam ve tekrarsız: %s"
                 % (s["mod_sayısı"], s["2³−1"], s["tam_ve_tekrarsız"]))
    for m in s["modlar"]:                                    # type: ignore[union-attr]
        satir.append("    syād-" + m)
    return "\n".join(satir)


# ====================================================================
#  mizan/altyapisal.py
# ====================================================================

ATOM, BIR, TENSOR, LOLLIPOP, ILE, ARTI = range(6)


class DFormul:
    """Doğrusal mantık formülü (hash'lenebilir, değişmez)."""

    __slots__ = ("etiket", "ad", "altlar", "_hash")

    def __init__(self, etiket: int, ad: Optional[str],
                 altlar: Tuple["DFormul", ...]) -> None:
        self.etiket = etiket
        self.ad = ad
        self.altlar = altlar
        self._hash = hash((etiket, ad, altlar))

    def __hash__(self) -> int:
        return self._hash

    def __eq__(self, o: object) -> bool:
        return (isinstance(o, DFormul) and o.etiket == self.etiket
                and o.ad == self.ad and o.altlar == self.altlar)

    def __repr__(self) -> str:
        e = self.etiket
        if e == ATOM:
            return self.ad or "?"
        if e == BIR:
            return "1"
        s = {TENSOR: "⊗", LOLLIPOP: "⊸", ILE: "&", ARTI: "⊕"}[e]
        return "(%r %s %r)" % (self.altlar[0], s, self.altlar[1])


def atom(ad: str) -> DFormul:
    return DFormul(ATOM, ad, ())


def bir() -> DFormul:
    return DFormul(BIR, None, ())


def tensor(a: DFormul, b: DFormul) -> DFormul:
    return DFormul(TENSOR, None, (a, b))


def lollipop(a: DFormul, b: DFormul) -> DFormul:
    return DFormul(LOLLIPOP, None, (a, b))


def ile(a: DFormul, b: DFormul) -> DFormul:
    return DFormul(ILE, None, (a, b))


def arti(a: DFormul, b: DFormul) -> DFormul:
    return DFormul(ARTI, None, (a, b))


Baglam = Tuple[DFormul, ...]           # sıralı ve tekrarlı; değişme serbest


def _duzenle(g: Sequence[DFormul]) -> Baglam:
    """Değişme kuralı DÂİMA açık olduğundan bağlam kanonik sıralanır.

    Bu bir kısaltma değil, değişmenin kendisidir: sıralama, çoklu kümeyi
    tek bir kanonik temsile indirger ve bellekleme anahtarı yapar.
    """
    return tuple(sorted(g, key=repr))


def _bolmeler(g: Baglam) -> List[Tuple[Baglam, Baglam]]:
    """Bağlamı iki parçaya ayıran BÜTÜN bölmeler.

    ``⊗R`` ve ``⊸L`` kuralları kaynağı paylaştırır; hangi paylaştırmanın
    işe yarayacağı önceden bilinemez, hepsi denenir. Bölme sayısı
    ``2^{|Γ|}``dır ve küçük formüllerde tüketilebilir.
    """
    n = len(g)
    sonuc = []
    for maske in range(1 << n):
        sol = tuple(g[i] for i in range(n) if (maske >> i) & 1)
        sag = tuple(g[i] for i in range(n) if not (maske >> i) & 1)
        sonuc.append((_duzenle(sol), _duzenle(sag)))
    return sonuc


class Hesap:
    """Yapısal kuralları anahtarlanabilir ardışık hesap.

    ``zayiflatma``: kullanılmayan öncül atılabilir.
    ``buzulme``   : bir öncül birden çok kere kullanılabilir.

    Dört bileşim dört mantık verir:

        (yok, yok)     → doğrusal (linear)
        (var, yok)     → affine
        (yok, var)     → sıkı / relevans-benzeri
        (var, var)     → sezgisel (yapısal kurallar tam)
    """

    def __init__(self, zayiflatma: bool = False, buzulme: bool = False,
                 azami_derinlik: int = 14) -> None:
        self.zayiflatma = zayiflatma
        self.buzulme = buzulme
        self.azami = azami_derinlik
        # olumsuz: (bağlam, hedef) → o hükmün verildiği EN BOL bütçe
        self._onbellek: Dict[Tuple[Baglam, DFormul], int] = {}
        # olumlu: bütçeden bağımsız, ispatı bulunmuş ardışıklar
        self._olumlu: set = set()

    def ispatlanabilir(self, g: Sequence[DFormul], hedef: DFormul) -> bool:
        return self._coz(_duzenle(g), hedef, 0)

    def _coz(self, g: Baglam, hedef: DFormul, d: int) -> bool:
        if d > self.azami:
            return False
        # Derinlik sınırı bir BÜTÇEdir: "kanıtlanamaz" hükmü yalnız o bütçe
        # altında geçerlidir; daha bol bütçeyle başarabilirdi.  Bu yüzden
        # olumsuz sonuç kalan bütçeye göre anahtarlanır.  Olumlu sonuç ise
        # bütçeden bağımsızdır (bulunmuş ispat her bütçede ispattır), o
        # sebeple ayrı ve bütçesiz bir kümede saklanır — hem doğru hem ucuz.
        kalan = self.azami - d
        if (g, hedef) in self._olumlu:
            return True
        onb = self._onbellek.get((g, hedef))
        if onb is not None and onb >= kalan:
            return False
        sonuc = self._coz_iç(g, hedef, d)
        if sonuc:
            self._olumlu.add((g, hedef))
        elif onb is None or kalan > onb:
            self._onbellek[(g, hedef)] = kalan
        return sonuc

    def _coz_iç(self, g: Baglam, hedef: DFormul, d: int) -> bool:
        # --- eksen (identity) ----------------------------------------
        if len(g) == 1 and g[0] == hedef:
            return True
        if self.zayiflatma and hedef in g:
            return True
        # --- 1 ---------------------------------------------------------
        if hedef.etiket == BIR and len(g) == 0:
            return True
        if hedef.etiket == BIR and self.zayiflatma:
            return True
        for i, f in enumerate(g):
            if f.etiket == BIR:
                kalan = _duzenle(g[:i] + g[i + 1:])
                if self._coz(kalan, hedef, d + 1):
                    return True

        # --- sağ kuralları --------------------------------------------
        he = hedef.etiket
        if he == LOLLIPOP:
            a, b = hedef.altlar
            if self._coz(_duzenle(g + (a,)), b, d + 1):
                return True
        if he == TENSOR:
            a, b = hedef.altlar
            for sol, sag in _bolmeler(g):
                if self._coz(sol, a, d + 1) and self._coz(sag, b, d + 1):
                    return True
        if he == ILE:
            a, b = hedef.altlar
            if self._coz(g, a, d + 1) and self._coz(g, b, d + 1):
                return True
        if he == ARTI:
            a, b = hedef.altlar
            if self._coz(g, a, d + 1) or self._coz(g, b, d + 1):
                return True

        # --- sol kuralları --------------------------------------------
        for i, f in enumerate(g):
            kalan = _duzenle(g[:i] + g[i + 1:])
            e = f.etiket
            if e == TENSOR:
                a, b = f.altlar
                if self._coz(_duzenle(kalan + (a, b)), hedef, d + 1):
                    return True
            elif e == LOLLIPOP:
                a, b = f.altlar
                for sol, sag in _bolmeler(kalan):
                    if (self._coz(sol, a, d + 1)
                            and self._coz(_duzenle(sag + (b,)), hedef, d + 1)):
                        return True
            elif e == ILE:
                a, b = f.altlar
                if (self._coz(_duzenle(kalan + (a,)), hedef, d + 1)
                        or self._coz(_duzenle(kalan + (b,)), hedef, d + 1)):
                    return True
            elif e == ARTI:
                a, b = f.altlar
                if (self._coz(_duzenle(kalan + (a,)), hedef, d + 1)
                        and self._coz(_duzenle(kalan + (b,)), hedef, d + 1)):
                    return True

        # --- yapısal kurallar (anahtarlı) ------------------------------
        if self.buzulme:
            for i, f in enumerate(g):
                if self._coz(_duzenle(g + (f,)), hedef, d + 1):
                    return True
        if self.zayiflatma:
            for i in range(len(g)):
                if self._coz(_duzenle(g[:i] + g[i + 1:]), hedef, d + 1):
                    return True
        return False


HESAPLAR = {
    "doğrusal": Hesap(False, False),
    "affine": Hesap(True, False),
    "sıkı": Hesap(False, True),
    "sezgisel": Hesap(True, True),
}


def yapisal_hassasiyet() -> List[Dict[str, object]]:
    """Aynı ardışığın dört mantıktaki ispatlanabilirliği.

    Beklenen ve sınanan olgular:

      * ``A ⊸ (B ⊸ A)`` ZAYIFLATMA ister -- doğrusal ve sıkıda çıkmaz.
      * ``A ⊸ (A ⊗ A)`` BÜZÜLME ister -- doğrusal ve affinede çıkmaz.
      * ``A ⊗ (A ⊸ B) ⊢ B`` yapısal kural İSTEMEZ -- dördünde de çıkar.
    """
    A, B = atom("A"), atom("B")
    ornekler = [
        ("A ⊸ (B ⊸ A)   [zayıflatma ister]", (), lollipop(A, lollipop(B, A))),
        ("A ⊸ (A ⊗ A)   [büzülme ister]", (), lollipop(A, tensor(A, A))),
        ("A ⊗ (A⊸B) ⊢ B [yapısal kural İSTEMEZ]",
         (tensor(A, lollipop(A, B)),), B),
        ("A ⊗ B ⊢ A     [zayıflatma ister]", (tensor(A, B),), A),
        ("A ⊢ A & A     [yapısal kural İSTEMEZ]", (A,), ile(A, A)),
        ("A ⊢ A ⊕ B     [yapısal kural İSTEMEZ]", (A,), arti(A, B)),
    ]
    sonuc = []
    for ad, g, h in ornekler:
        kayit: Dict[str, object] = {"ardışık": ad}
        for mad, hes in HESAPLAR.items():
            kayit[mad] = hes.ispatlanabilir(g, h)
        sonuc.append(kayit)
    return sonuc


def _degiskenler(f: DFormul) -> FrozenSet[str]:
    if f.etiket == ATOM:
        return frozenset({f.ad})                            # type: ignore[arg-type]
    k: Set[str] = set()
    for a in f.altlar:
        k |= _degiskenler(a)
    return frozenset(k)


def degisken_paylasimi(f: DFormul) -> Optional[bool]:
    """``A → B`` biçimindeki bir formülde ``A`` ile ``B`` değişken paylaşıyor mu?

    Relevans mantığı ``R``nin taşıyıcı hususiyeti şudur: ``A → B`` bir
    teoremse ``A`` ile ``B`` en az bir önerme değişkenini paylaşır. Bu,
    "maddî gerektirme paradoksu"nun (``A → (B → A)``) niçin reddedildiğini
    açıklar: orada ``B`` ile ``A`` alâkasızdır.
    """
    if f.etiket != LOLLIPOP:
        return None
    a, b = f.altlar
    return bool(_degiskenler(a) & _degiskenler(b))


def relevans_paradokslari() -> List[Dict[str, object]]:
    A, B = atom("A"), atom("B")
    ornekler = [
        # Paylaşım ölçütü GEREK şarttır, YETER şart değildir: paylaşım
        # sağlansa da formül doğrusalda ispatlanamayabilir.  Üç örnek tam
        # olarak bu üç hâli ayırt etmek için seçildi.
        ("özdeşlik    A ⊸ A            [paylaşır, doğrusal da ispatlar]",
         lollipop(A, A)),
        ("modus ponens A ⊗ (A⊸B) ⊸ B   [paylaşır, doğrusal da ispatlar]",
         lollipop(tensor(A, lollipop(A, B)), B)),
        ("paradoks    A ⊸ (B ⊸ A)      [paylaşır ama doğrusal REDDEDER]",
         lollipop(A, lollipop(B, A))),
        ("paradoks    B ⊸ (A ⊸ A)      [PAYLAŞMAZ; ölçüt tek başına keser]",
         lollipop(B, lollipop(A, A))),
    ]
    sonuc = []
    for ad, f in ornekler:
        sonuc.append({
            "formül": ad,
            "değişken_paylaşımı": degisken_paylasimi(f),
            "doğrusalda_ispatlanabilir": HESAPLAR["doğrusal"].ispatlanabilir((), f),
            "sezgiselde_ispatlanabilir": HESAPLAR["sezgisel"].ispatlanabilir((), f),
        })
    return sonuc


class AltUzay:
    """``ℝⁿ``in bir alt uzayı; ortonormal taban ile temsil edilir."""

    __slots__ = ("n", "T")

    def __init__(self, n: int, uretecler: np.ndarray) -> None:
        self.n = n
        if uretecler.size == 0:
            self.T = np.zeros((n, 0))
        else:
            U, s, _ = np.linalg.svd(uretecler.reshape(n, -1), full_matrices=False)
            r = int(np.sum(s > 1e-10))
            self.T = U[:, :r]

    @property
    def boyut(self) -> int:
        return self.T.shape[1]

    def izdusum(self) -> np.ndarray:
        if self.boyut == 0:
            return np.zeros((self.n, self.n))
        return self.T @ self.T.T

    # -- kafes işlemleri ----------------------------------------------
    def ve(self, o: "AltUzay") -> "AltUzay":
        """Kesişim: iki izdüşümün de sabit bıraktığı vektörler."""
        M = np.vstack([np.eye(self.n) - self.izdusum(),
                       np.eye(self.n) - o.izdusum()])
        _, s, Vt = np.linalg.svd(M)
        cekirdek = Vt[np.sum(s > 1e-10):].T
        return AltUzay(self.n, cekirdek)

    def veya(self, o: "AltUzay") -> "AltUzay":
        """Toplamın kapanışı (sonlu boyutta toplamın kendisi)."""
        return AltUzay(self.n, np.hstack([self.T, o.T]))

    def degil(self) -> "AltUzay":
        """Dik tümleyen."""
        if self.boyut == 0:
            return AltUzay(self.n, np.eye(self.n))
        _, s, Vt = np.linalg.svd(self.T.T)
        r = int(np.sum(s > 1e-10))
        return AltUzay(self.n, Vt[r:].T)

    def icinde_mi(self, o: "AltUzay") -> bool:
        """``self ≤ o``?"""
        if self.boyut == 0:
            return True
        return bool(np.allclose(o.izdusum() @ self.T, self.T, atol=1e-8))

    def esit_mi(self, o: "AltUzay") -> bool:
        return self.icinde_mi(o) and o.icinde_mi(self)

    def __repr__(self) -> str:
        return "AltUzay(boyut=%d)" % self.boyut


def dogru_uzay(n: int, v: Sequence[float]) -> AltUzay:
    return AltUzay(n, np.array(v, dtype=float).reshape(n, 1))


def dagilma_kirilir() -> Dict[str, object]:
    """**T93'ün fiilî sağlaması.**

    ``ℝ²``de ``A = ⟨e₁⟩``, ``B = ⟨e₂⟩``, ``C = ⟨e₁+e₂⟩``:

        B ∨ C = ℝ²,  A ∧ (B∨C) = A          (boyut 1)
        A ∧ B = 0,   A ∧ C = 0,  toplam = 0  (boyut 0)

    Yani dağılma bozulur. Fakat her ortolatiste geçerli olan
    ``(A∧B) ∨ (A∧C) ≤ A ∧ (B∨C)`` eşitsizliği SAĞLANIR -- kaynak
    metindeki "``≠``" işareti bunu gizliyordu.
    """
    A = dogru_uzay(2, [1.0, 0.0])
    B = dogru_uzay(2, [0.0, 1.0])
    C = dogru_uzay(2, [1.0, 1.0])
    sol = A.ve(B.veya(C))
    sag = (A.ve(B)).veya(A.ve(C))
    return {
        "A∧(B∨C) boyutu": sol.boyut,
        "(A∧B)∨(A∧C) boyutu": sag.boyut,
        "eşit_mi": sol.esit_mi(sag),
        "eşitsizlik (A∧B)∨(A∧C) ≤ A∧(B∨C)": sag.icinde_mi(sol),
    }


def dagilma_uyumlu_halde() -> Dict[str, object]:
    """Uyumlu (birbirine dik yahut kapsayan) alt uzaylarda dağılma SAĞLANIR.

    Bu, "``≠``" yazmanın niçin yanlış olduğunun ikinci yüzüdür: bozulma
    genel değil, husûsîdir.
    """
    A = dogru_uzay(3, [1.0, 0.0, 0.0])
    B = dogru_uzay(3, [0.0, 1.0, 0.0])
    C = dogru_uzay(3, [0.0, 0.0, 1.0])
    sol = A.ve(B.veya(C))
    sag = (A.ve(B)).veya(A.ve(C))
    return {"dik üçlüde eşit_mi": sol.esit_mi(sag),
            "iki tarafın da boyutu": (sol.boyut, sag.boyut)}


def ortomoduler_kanun(deneme: int = 200, n: int = 4,
                      tohum: int = 0) -> Dict[str, object]:
    """``A ≤ B ⟹ B = A ∨ (B ∧ A^⊥)``.

    Rastgele iç içe alt uzay çiftlerinde sınanır; kuantum mantığını
    ortolatisten ayıran kanun budur ve dağılmanın yerini tutar.
    """
    rng = np.random.default_rng(tohum)
    ihlal = 0
    denenen = 0
    for _ in range(deneme):
        k = int(rng.integers(1, n))
        Bt = rng.normal(size=(n, k + 1))
        B = AltUzay(n, Bt)
        A = AltUzay(n, B.T[:, :max(1, k - 1)] if B.boyut >= 2 else B.T)
        if not A.icinde_mi(B):
            continue
        denenen += 1
        sag = A.veya(B.ve(A.degil()))
        if not B.esit_mi(sag):
            ihlal += 1
    return {"denenen": denenen, "ihlal": ihlal, "kanun_geçerli": ihlal == 0}


def _rapor_mizan_altyapisal() -> str:
    satir = ["=== yapısal-altı mantıklar ===",
             "%-42s %-9s %-8s %-6s %s"
             % ("ardışık", "doğrusal", "affine", "sıkı", "sezgisel")]
    for k in yapisal_hassasiyet():
        satir.append("%-42s %-9s %-8s %-6s %s"
                     % (k["ardışık"], k["doğrusal"], k["affine"],
                        k["sıkı"], k["sezgisel"]))
    satir.append("")
    satir.append("Relevans: değişken paylaşımı ölçütü")
    for k in relevans_paradokslari():
        satir.append("  %-44s paylaşım=%s  doğrusal=%s"
                     % (k["formül"], k["değişken_paylaşımı"],
                        k["doğrusalda_ispatlanabilir"]))
    satir.append("")
    d = dagilma_kirilir()
    satir.append("Kuantum mantık (ℝ²):")
    satir.append("  A∧(B∨C) boyut=%d   (A∧B)∨(A∧C) boyut=%d   eşit=%s"
                 % (d["A∧(B∨C) boyutu"], d["(A∧B)∨(A∧C) boyutu"], d["eşit_mi"]))
    satir.append("  DÂİMA geçerli eşitsizlik sağlanıyor: %s"
                 % d["eşitsizlik (A∧B)∨(A∧C) ≤ A∧(B∨C)"])
    u = dagilma_uyumlu_halde()
    satir.append("  uyumlu (dik) üçlüde dağılma sağlanıyor: %s" % u["dik üçlüde eşit_mi"])
    o = ortomoduler_kanun()
    satir.append("  ortomodüler kanun: %d denemede %d ihlal → %s"
                 % (o["denenen"], o["ihlal"], o["kanun_geçerli"]))
    return "\n".join(satir)


# ====================================================================
#  mizan/istikra.py
# ====================================================================

def ardisiklik_kaidesi(k: int, n: int, alfa: float = 1.0,
                       beta: float = 1.0) -> float:
    """``P(X_{n+1}=1 | k başarı / n deneme)`` — Beta(α,β) önseliyle.

    Türetme: önsel ``p ~ Beta(α,β)``, gözlem ``k ~ Binom(n,p)``.  Beta
    binom için eşlenik olduğundan ardıl ``Beta(k+α, n−k+β)``, onun da
    beklentisi ``(k+α)/(n+α+β)``.  Bir sonraki denemenin başarı ihtimali
    tam olarak bu beklentidir (Bernoulli'nin ortalaması parametresidir).

    ``α=β=1``: Laplace'ın ``(k+1)/(n+2)`` kaidesi.
    """
    if n < 0 or k < 0 or k > n:
        raise ValueError("0 ≤ k ≤ n olmalı")
    if alfa <= 0 or beta <= 0:
        raise ValueError("α, β > 0 olmalı")
    return (k + alfa) / (n + alfa + beta)


def ardisiklik_dizisi(n_azami: int, alfa: float = 1.0,
                      beta: float = 1.0) -> List[float]:
    """Hep-başarı hâlinde (k=n) ihtimalin n=0..n_azami boyunca seyri."""
    return [ardisiklik_kaidesi(n, n, alfa, beta)
            for n in range(n_azami + 1)]


def tam_istikra_mi(k: int, n: int, alfa: float = 1.0,
                   beta: float = 1.0) -> bool:
    """Eksik istikrâ hiçbir sonlu ``n`` için yakîn (=1) vermez.

    ``β > 0`` olduğu sürece ``(k+α)/(n+α+β) < 1``; ancak ``k=n`` ve
    ``β→0`` sınırında 1'e ulaşılır ki bu da "hiç aksi olamaz" demek olan
    bir önsel koymaktır — yani istikrâdan değil, önselden gelen yakîndir.
    """
    return ardisiklik_kaidesi(k, n, alfa, beta) >= 1.0


@dataclass(frozen=True)
class Ortam:
    """Bir gözlem ortamı: yordayıcı değerleri ve netice.

    ``X``: her satır bir müşahede, her sütun bir yordayıcı.
    ``y``: aynı uzunlukta netice dizisi.
    """
    ad: str
    X: Tuple[Tuple[float, ...], ...]
    y: Tuple[float, ...]

    def __post_init__(self) -> None:
        if len(self.X) != len(self.y):
            raise ValueError("X satır sayısı y ile uyuşmuyor")


def _en_kucuk_kareler(X: Sequence[Sequence[float]],
                      y: Sequence[float],
                      sutunlar: Sequence[int]) -> Tuple[List[float], float]:
    """Seçili sütunlarla sabit terimli EKK; (katsayılar, artık varyansı).

    Normal denklemler ``(AᵀA)β = Aᵀy`` Gauss eliminasyonuyla çözülür.
    Tekil hâlde küçük bir Tikhonov terimi (1e-12) eklenir — bu yalnız
    sayısal tekilliği açar, kat sayıları maddî olarak değiştirmez.
    """
    m = len(y)
    p = len(sutunlar) + 1
    A = [[1.0] + [X[i][j] for j in sutunlar] for i in range(m)]
    G = [[sum(A[i][r] * A[i][c] for i in range(m)) for c in range(p)]
         for r in range(p)]
    b = [sum(A[i][r] * y[i] for i in range(m)) for r in range(p)]
    for r in range(p):
        G[r][r] += 1e-12
    # Gauss — kısmî pivotlama
    for c in range(p):
        piv = max(range(c, p), key=lambda r: abs(G[r][c]))
        if abs(G[piv][c]) < 1e-14:
            continue
        G[c], G[piv] = G[piv], G[c]
        b[c], b[piv] = b[piv], b[c]
        for r in range(p):
            if r == c:
                continue
            f = G[r][c] / G[c][c]
            if f:
                for k in range(c, p):
                    G[r][k] -= f * G[c][k]
                b[r] -= f * b[c]
    beta = [b[r] / G[r][r] if abs(G[r][r]) > 1e-14 else 0.0 for r in range(p)]
    artik = [y[i] - sum(beta[r] * A[i][r] for r in range(p)) for i in range(m)]
    var = sum(e * e for e in artik) / max(1, m - p)
    return beta, var


def _kabul_mu(ortamlar: Sequence[Ortam], sutunlar: Sequence[int],
              tolerans: float) -> bool:
    """Bu yordayıcı kümesi BÜTÜN ortamlarda aynı ilişkiyi mi veriyor?

    Ölçüt: ortamların birleşiminde uydurulan katsayılarla her ortamın
    artıkları, o ortamın kendi içinde uydurulmuş artıklarından belirgin
    biçimde kötü olmamalı.  ``tolerans`` bağıl bir eşiktir.
    """
    hepsi_X = tuple(itertools.chain.from_iterable(o.X for o in ortamlar))
    hepsi_y = tuple(itertools.chain.from_iterable(o.y for o in ortamlar))
    beta, _ = _en_kucuk_kareler(hepsi_X, hepsi_y, sutunlar)
    for o in ortamlar:
        _, kendi_var = _en_kucuk_kareler(o.X, o.y, sutunlar)
        artik = []
        for i in range(len(o.y)):
            satir = [1.0] + [o.X[i][j] for j in sutunlar]
            artik.append(o.y[i] - sum(beta[r] * satir[r]
                                      for r in range(len(beta))))
        ortak_var = sum(e * e for e in artik) / max(1, len(artik))
        if ortak_var > (kendi_var + 1e-9) * (1.0 + tolerans):
            return False
    return True


def degismez_kumeler(ortamlar: Sequence[Ortam], n_yordayici: int,
                     tolerans: float = 0.5) -> List[FrozenSet[int]]:
    """Bütün ortamlarda değişmez kalan yordayıcı kümelerinin listesi."""
    kabul: List[FrozenSet[int]] = []
    for r in range(n_yordayici + 1):
        for alt in itertools.combinations(range(n_yordayici), r):
            if _kabul_mu(ortamlar, alt, tolerans):
                kabul.append(frozenset(alt))
    return kabul


def degismez_kesisim(ortamlar: Sequence[Ortam], n_yordayici: int,
                     tolerans: float = 0.5) -> FrozenSet[int]:
    """Kabul edilen kümelerin **kesişimi** — ICP'nin verdiği hüküm.

    Kesişim boşsa hiçbir yordayıcı hakkında hüküm verilmez.  Bu bir
    kusur değil, usulün kendisidir: değişmezlik delili yoksa illet
    isnadı da yoktur.
    """
    kabul = degismez_kumeler(ortamlar, n_yordayici, tolerans)
    if not kabul:
        return frozenset()
    kesisim = set(kabul[0])
    for k in kabul[1:]:
        kesisim &= k
    return frozenset(kesisim)


@dataclass(frozen=True)
class Nesne:
    ad: str
    vasiflar: FrozenSet[str]


def benzerlik(a: Nesne, b: Nesne) -> float:
    """Jaccard: ``|A∩B| / |A∪B|``.  Boş-boş hâlinde 1 (ikisi de aynı)."""
    birlesim = a.vasiflar | b.vasiflar
    if not birlesim:
        return 1.0
    return len(a.vasiflar & b.vasiflar) / len(birlesim)


def temsil_gucu(a: Nesne, b: Nesne, illet_vasiflari: Iterable[str]) -> float:
    """Analojinin gücü = **illetle alâkalı** vasıflardaki uyuşma oranı.

    Ölçüt kasten yalnız ``illet_vasiflari`` üzerinden hesaplanır: alâkasız
    vasıflarda benzeşmek analojiyi kuvvetlendirmez.  Uyuşma, her illet
    vasfı için "ikisinde de var" veya "ikisinde de yok" hâlleridir —
    yani vasfın müşterek *değeri*, sadece müşterek varlığı değil.
    """
    illet = list(dict.fromkeys(illet_vasiflari))
    if not illet:
        return 0.0
    uyan = sum(1 for v in illet
               if (v in a.vasiflar) == (v in b.vasiflar))
    return uyan / len(illet)


def temsil_hukmu(asil: Nesne, fer: Nesne, illet_vasiflari: Iterable[str],
                 asil_hukmu: bool, esik: float = 1.0
                 ) -> Tuple[Optional[bool], float]:
    """Asıldaki hükmü fer'e taşı — ancak illet tam intibak ederse.

    Dönen: ``(hüküm veya None, güç)``.  Güç eşiğin altındaysa hüküm
    **verilmez** (``None``); klasik usulde de illetin fer'de tahakkuku
    şart koşulur, kısmî benzerlik hüküm doğurmaz.
    """
    g = temsil_gucu(asil, fer, illet_vasiflari)
    return (asil_hukmu if g >= esik else None), g


@dataclass(frozen=True)
class NyayaCikarim:
    """pratijñā / hetu / udāharaṇa / upanaya / nigamana.

    ``sapaksa``: hetu'nun da sādhya'nın da bulunduğu müsbet misaller.
    ``vipaksa``: sādhya'nın bulunmadığı menfî misaller — hetu bunların
    **hiçbirinde** bulunmamalıdır (vyatireka).
    """
    paksa: str            # mevzu ("şu dağ")
    sadhya: str           # isbat edilecek ("ateş var")
    hetu: str             # delil ("duman var")
    sapaksa: FrozenSet[str]
    vipaksa: FrozenSet[str]
    hetu_paksada: bool = True
    hetunun_bulundugu: FrozenSet[str] = frozenset()


def nyaya_degerlendir(c: NyayaCikarim) -> Dict[str, object]:
    """Hetu'nun beş şartını (pañca-rūpa) tek tek dener.

    1. pakṣadharmatā — hetu mevzuda bulunmalı.
    2. sapakṣa-sattva — hetu en az bir müsbet misalde bulunmalı.
    3. vipakṣa-asattva — hetu hiçbir menfî misalde bulunmamalı.
    4. abādhita — netice başka bir kat'î delille çürütülmemiş olmalı.
    5. asatpratipakṣa — eşit kuvvette bir karşı-delil bulunmamalı.

    4 ve 5 dışsal şartlardır; burada girdi olarak alınır, uydurulmaz.
    Hüküm ancak ilk üçü sağlanınca verilir.
    """
    s1 = c.hetu_paksada
    s2 = bool(c.sapaksa & c.hetunun_bulundugu) or (
        not c.hetunun_bulundugu and bool(c.sapaksa))
    s3 = not (c.vipaksa & c.hetunun_bulundugu)
    hata: Optional[str] = None
    if not s1:
        hata = "asiddha (hetu mevzuda yok)"
    elif not s3:
        hata = "savyabhicāra (hetu menfî misalde de var — ıttırad bozuk)"
    elif not s2:
        hata = "sapakṣa'da müsbet misal yok"
    return {
        "pakṣadharmatā": s1,
        "sapakṣa_sattva": s2,
        "vipakṣa_asattva": s3,
        "geçerli": bool(s1 and s2 and s3),
        "hata": hata,
        "nigamana": (f"{c.paksa}: {c.sadhya}" if (s1 and s2 and s3) else None),
    }


def _stoa_semalari() -> List[Tuple[str, List[Onerme], Onerme]]:
    A, B = deg("A"), deg("B")
    return [
        ("1. modus ponens        : A→B, A ⊢ B",
         [ise(A, B), A], B),
        ("2. modus tollens       : A→B, ¬B ⊢ ¬A",
         [ise(A, B), degil(B)], degil(A)),
        ("3. bağdaşmazlık        : ¬(A∧B), A ⊢ ¬B",
         [degil(ve(A, B)), A], degil(B)),
        ("4. ayırıcı (tam)       : A⊻B, A ⊢ ¬B",
         [ve(veya(A, B), degil(ve(A, B))), A], degil(B)),
        ("5. ayırıcı (kalan)     : A⊻B, ¬A ⊢ B",
         [ve(veya(A, B), degil(ve(A, B))), degil(A)], B),
    ]


ANAPODEIKTOI: List[Tuple[str, List[Onerme], Onerme]] = _stoa_semalari()


def anapodeiktos_dogrula(oncul: Sequence[Onerme], netice: Onerme) -> bool:
    """Şemayı doğruluk tablosuyla dene — iddia değil, ölçüm."""
    return hukum(oncüller=list(oncul), netice=netice)


def butun_anapodeiktoslari_dogrula() -> List[Tuple[str, bool]]:
    return [(ad, anapodeiktos_dogrula(o, n)) for ad, o, n in ANAPODEIKTOI]


Vaka = Tuple[FrozenSet[str], bool]   # (mevcut âmiller, netice oldu mu)


USUL_AYRILIK, USUL_BIRLESIK = "ayrılık", "birleşik"


USUL_ESDEGISIM = "eş_değişim"


def illet_ara(vakalar=None, ne: str = "uyuşma", olcumler=None):
    """MİLL'İN İSTİKRÂ USULLERİ -- tek terkip (kütük H226).

    Küme: ``mill_uyusma``, ``mill_ayrilik``, ``mill_birlesik``,
    ``mill_esdegisim``. Dört isim, tek sualin dört yolu idi: *bu
    neticenin illeti hangi âmildir?* İlk üçü aynı iki kümenin
    cebridir ve ayrı yazıldıklarında bu cebir görünmüyordu:

        ``K = ∩{a : netice var}``   (her müsbette bulunan)
        ``M = ∪{a : netice yok}``   (bir menfîde bulunan)
        ``B = ∪{a : netice var}``   (bir müsbette bulunan)

    ==================  ==============================================
    ``ne``              döndürdüğü
    ==================  ==============================================
    ``uyuşma``          ``K`` -- neticenin olduğu BÜTÜN vakalarda ortak
    ``ayrılık``         ``B − M`` -- neticenin olmadığı hiçbir vakada
                        bulunmayan
    ``birleşik``        ``K ∩ (B − M)`` -- hem her müsbette var, hem
                        hiçbir menfîde yok
    ``eş_değişim``      Pearson bağıntı katsayısı (``olcumler``den)
    ==================  ==============================================

    Uyuşma ile ayrılığın farkı elemenin **nereden** geldiğidir: uyuşma
    müsbet vakaları keser, ayrılık menfî vakalarla eler. Netice yokken
    de bulunan bir âmil illet olamaz; bu, ayrılığın tek satırıdır.

    Eş değişim usulünde değişkenlerden biri sabitse ``0`` döner --
    "birlikte değişme yok" hükmü, uydurma bir sayı değil (H10).
    """
    if ne == "eş_değişim":
        n = len(olcumler)
        if n < 2:
            return 0.0
        mx = sum(x for x, _ in olcumler) / n
        my = sum(y for _, y in olcumler) / n
        sxy = sum((x - mx) * (y - my) for x, y in olcumler)
        sxx = sum((x - mx) ** 2 for x, _ in olcumler)
        syy = sum((y - my) ** 2 for _, y in olcumler)
        if sxx < 1e-15 or syy < 1e-15:
            return 0.0
        return sxy / math.sqrt(sxx * syy)

    if ne not in ("uyuşma", "ayrılık", "birleşik"):
        raise ValueError("istikrâ usulü bilinmiyor: %r" % (ne,))

    musbet = [set(a) for a, n in vakalar if n]
    K: Set[str] = set()
    if musbet:
        K = set(musbet[0])
        for a in musbet[1:]:
            K &= a
    if ne == "uyuşma":
        return frozenset(K)
    M: Set[str] = set()
    B: Set[str] = set()
    for a, n in vakalar:
        (B if n else M).update(a)
    ayrilik = B - M
    return frozenset(ayrilik if ne == "ayrılık" else K & ayrilik)


def _rapor_mizan_istikra() -> str:
    s: List[str] = []
    s.append("=== Laplace ardışıklık kaidesi (hep başarı) ===")
    d = ardisiklik_dizisi(10)
    s.append("  n :  " + "  ".join(f"{n:5d}" for n in range(11)))
    s.append("  P :  " + "  ".join(f"{p:.3f}" for p in d))
    s.append(f"  n=1000 → {ardisiklik_kaidesi(1000, 1000):.6f}"
             f"   yakîn mi? {tam_istikra_mi(1000, 1000)}")

    s.append("\n=== Değişmezlik yoluyla istikrâ ===")
    # X0 hakiki illet (y = 2·X0 her ortamda); X1 sahte: 1. ortamda y ile
    # aynı yönde, 2.'de ters yönde gider.  Ortamlar ayrıca y aralığında da
    # ayrışır — ayrışmasalardı boş küme de kabul edilirdi ve ölçüt hiçbir
    # şeyi elemezdi (ICP'nin gücü ortam farkından gelir).
    o1 = Ortam("ortam-1",
               tuple((float(i), float(i)) for i in range(8)),
               tuple(2.0 * i for i in range(8)))
    o2 = Ortam("ortam-2",
               tuple((float(i), float(-i)) for i in range(10, 18)),
               tuple(2.0 * i for i in range(10, 18)))
    kabul = degismez_kumeler([o1, o2], 2)
    s.append("  kabul edilen kümeler: "
             + ", ".join("{" + ",".join(f"X{j}" for j in sorted(k)) + "}"
                         if k else "{}" for k in kabul))
    kes = degismez_kesisim([o1, o2], 2)
    s.append("  kesişim (hüküm): "
             + ("{" + ",".join(f"X{j}" for j in sorted(kes)) + "}"
                if kes else "boş — hüküm verilmez"))

    s.append("\n=== Temsil (analoji) ===")
    hamr = Nesne("şarap", frozenset({"üzümden", "sıvı", "sarhoş_edici", "kırmızı"}))
    nbz = Nesne("nebîz", frozenset({"hurmadan", "sıvı", "sarhoş_edici"}))
    sirke = Nesne("sirke", frozenset({"üzümden", "sıvı", "kırmızı"}))
    for fer in (nbz, sirke):
        h, g = temsil_hukmu(hamr, fer, ["sarhoş_edici"], True)
        s.append(f"  {fer.ad:6s} illet gücü={g:.2f}  hüküm={h}"
                 f"   (kaba benzerlik={benzerlik(hamr, fer):.2f})")
    s.append("  dikkat: sirke şaraba KABA benzerlikte daha yakın olabilir,"
             " illette değil.")

    s.append("\n=== Nyāya beş uzuv ===")
    iyi = NyayaCikarim("dağ", "ateş var", "duman var",
                       frozenset({"mutfak"}), frozenset({"göl"}),
                       True, frozenset({"mutfak"}))
    kotu = NyayaCikarim("dağ", "ateş var", "hava var",
                        frozenset({"mutfak"}), frozenset({"göl"}),
                        True, frozenset({"mutfak", "göl"}))
    for ad, c in (("sahih", iyi), ("savyabhicāra", kotu)):
        r = nyaya_degerlendir(c)
        s.append(f"  {ad:14s} geçerli={r['geçerli']}  hata={r['hata']}")

    s.append("\n=== Stoacı beş anapodeiktos (tablo sağlaması) ===")
    for ad, ok in butun_anapodeiktoslari_dogrula():
        s.append(f"  {ad:38s} {ok}")

    s.append("\n=== Mill usulleri ===")
    vakalar: List[Vaka] = [
        (frozenset({"a", "b", "c"}), True),
        (frozenset({"a", "d", "e"}), True),
        (frozenset({"b", "d", "f"}), False),
        (frozenset({"c", "e", "f"}), False),
    ]
    s.append(f"  uyuşma  = {sorted(illet_ara(vakalar))}")
    s.append(f"  ayrılık = {sorted(illet_ara(vakalar, USUL_AYRILIK))}")
    s.append(f"  birleşik= {sorted(illet_ara(vakalar, USUL_BIRLESIK))}")
    s.append("  eş değişim r = "
             f"{illet_ara(ne=USUL_ESDEGISIM, olcumler=[(1,2),(2,4),(3,6),(4,8)]):.3f}"
             "  (sabit değişkende) "
             f"{illet_ara(ne=USUL_ESDEGISIM, olcumler=[(1,5),(2,5),(3,5)]):.3f}")
    return "\n".join(s)


# ====================================================================
#  mizan/munazara.py
# ====================================================================

MERTEBELER: Tuple[Tuple[float, str], ...] = (
    (1.00, "yakîn"),        # kat'î — aksi muhal
    (0.75, "zann-ı gālib"),  # kuvvetli zan
    (0.50, "zan"),
    (0.25, "şek"),           # iki taraf müsâvî veya altı
    (0.00, "vehim"),         # mercûh taraf
)


def mertebe_adi(y: float) -> str:
    """Yakîn derecesine karşılık gelen klasik mertebe adı."""
    if not 0.0 <= y <= 1.0:
        raise ValueError("yakîn ∈ [0,1] olmalı")
    for esik, ad in MERTEBELER:
        if y >= esik:
            return ad
    return "vehim"


ZANN_I_GALIB_ESIGI: float = 0.75


MAKAM_ADI: Dict[str, str] = {
    "yakîn": "Yakîn", "zann-ı gālib": "Zann-ı gālib", "zan": "Zan",
    "şek": "Şek", "vehim": "Vehim",
}


def makam_tayin(P: float, eps_sek: float = 0.0,
                eps_yakin: float = 0.0) -> str:
    """``mertebe_adi``nın **görünen adla** dönen hâli -- aynı cetvel.

    ``eps_*`` payları **varsayılan olarak sıfırdır**: cetvelde öyle bir
    bant yoktur. Sıfırdan büyük verilirse ``şek``in tabanı aşağı,
    ``yakîn``in tabanı yukarı kaydırılır ve bu artık cetvelin değil
    **çağıranın** hükmüdür; öyle de raporlanır.
    """
    e_sek, e_yakin = float(eps_sek), float(eps_yakin)
    for esik, ad in MERTEBELER:                  # cetvel azalan sırada
        e = float(esik)
        if ad == "yakîn":
            e -= e_yakin
        elif ad == "şek":
            e -= e_sek
        if P >= e:
            return MAKAM_ADI[ad]
    return "Vehim"


def ikili_entropi(P: float) -> float:
    """``−P log P − (1−P) log(1−P)`` -- yakînin belirsizliği."""
    if P <= 0.0 or P >= 1.0:
        return 0.0
    return float(-P * math.log(P) - (1 - P) * math.log(1 - P))


def hukum_agirligi(P: float, makam: str) -> float:
    """``Hüküm = 1·𝕀_yakîn + P·𝕀_zan + 0.5·𝕀_şek`` (+ Vehim için ``P``).

    ``Zann-ı gālib`` de ``P``dir: kuvvetli zan, zannın kendi
    kuvvetiyle tartılır; ``1``e yuvarlanmaz. Yuvarlansaydı, ayırt
    etmek için açtığımız mertebe hemen yakîne katılmış olurdu.
    """
    return {"Yakîn": 1.0, "Zann-ı gālib": P, "Zan": P,
            "Şek": 0.5, "Vehim": P}[makam]


def yakin_gazali(oncul_yakinleri: Sequence[float],
                 sekil_gecerli: bool) -> float:
    """``min_i Yakîn(P_i) · 𝟙[şekil geçerli]``.

    Öncül yoksa (boş liste) netice öncülsüz iddiadır: yakîn 0.  Bu,
    ``min(∅)=+∞`` matematiksel kabulünden kasten ayrılır — burada mîzân
    delil tartar, delilsizlik en yüksek derece olamaz.
    """
    if not sekil_gecerli:
        return 0.0
    if not oncul_yakinleri:
        return 0.0
    for y in oncul_yakinleri:
        if not 0.0 <= y <= 1.0:
            raise ValueError("her yakîn ∈ [0,1] olmalı")
    return min(oncul_yakinleri)


def yakin_zinciri(halkalar: Sequence[Tuple[Sequence[float], bool]]) -> float:
    """Sorites/zincirleme kıyasta yakînin seyri.

    Her halka bir kıyastır; bir öncekinin neticesi sonrakinin öncülüdür.
    Minimum idempotent olduğundan zincir uzunluğu **tek başına** yakîni
    düşürmez — düşüren, araya giren zayıf öncüllerdir.  (Çarpım t-normu
    seçilseydi zincir uzadıkça yakîn kaçınılmaz olarak sıfıra giderdi;
    bu, kat'î öncüllerden kurulu uzun bir ispatı da değersizleştirirdi.)
    """
    tasinan = 1.0
    for onculler, gecerli in halkalar:
        tasinan = yakin_gazali(list(onculler) + [tasinan], gecerli)
        if tasinan == 0.0:
            return 0.0
    return tasinan


class ItirazNevi(Enum):
    MEN = "men'"
    NAKZ = "nakz"
    MUARAZA = "muâraza"


@dataclass(frozen=True)
class Hamle:
    """Bir münâzara hamlesi.

    ``sahip``: "müddeî" veya "muteriz".
    ``nevi``: îtiraz nev'i (müddeî hamlelerinde ``None``).
    ``hedef``: men'/nakz edilen öncülün sırası (men' ve nakz için şart).
    ``delil``: muâraza veya ispat için getirilen öncüller.
    """
    sahip: str
    nevi: Optional[ItirazNevi]
    hedef: Optional[int] = None
    delil: Tuple[Onerme, ...] = ()
    netice: Optional[Onerme] = None
    aciklama: str = ""


def men_mesru_mu(hedef: Optional[int], n_oncul: int,
                 daha_once_men_edilenler: Set[int]) -> Tuple[bool, str]:
    """Men' ancak *mevcut* ve *henüz men edilmemiş* bir öncüle yapılır.

    Aynı öncülü tekrar men etmek "tekrâr-ı men'"dir ve münâzarayı
    sonlandırmaz — usulen reddedilir; yoksa muteriz aynı hamleyi
    sonsuza kadar tekrarlayıp mağlubiyetten kaçınabilirdi.
    """
    if hedef is None:
        return False, "men' bir öncüle taalluk etmeli"
    if not 0 <= hedef < n_oncul:
        return False, "böyle bir öncül yok"
    if hedef in daha_once_men_edilenler:
        return False, "tekrâr-ı men' — bu öncül zaten men edilmişti"
    return True, ""


def nakz_gecerli_mi(onculler: Sequence[Onerme], netice: Onerme
                    ) -> Tuple[bool, Optional[Dict[str, bool]]]:
    """Nakz: delil sûreti aynı kalırken neticenin bâtıl olduğu bir hâl.

    Hesaplanabilir karşılığı doğrudandır — kıyas geçerli **değilse**
    öncülleri doğru, neticeyi yanlış kılan bir değerlendirme vardır ve
    o değerlendirme nakzın ta kendisidir.  Geçerliyse nakz imkânsızdır.

    Dönen: ``(nakz mümkün mü, şâhit değerlendirme)``.
    """
    if hukum(oncüller=list(onculler), netice=netice):
        return False, None
    return True, hukum(oncüller=list(onculler), netice=netice, ne="karşı_örnek")


def muaraza_gecerli_mi(karsi_onculler: Sequence[Onerme],
                       davanin_aksi: Onerme) -> bool:
    """Muâraza ancak getirilen delil dâvânın aksini **ispat ederse** sahih.

    Muteriz burada ispat yükünü üstlenmiştir; delilinin geçerliliği
    müddeîninkiyle aynı ölçütle tartılır — çifte standart yoktur.
    """
    return hukum(oncüller=list(karsi_onculler), netice=davanin_aksi)


@dataclass
class Munazara:
    """Bir münâzaranın hâli ve hükmü.

    ``onculler`` ile ``netice`` müddeînin dâvâsıdır.  ``yakinler``
    öncüllerin başlangıç yakîn dereceleridir; men' edilen bir öncülün
    yakîni, müddeî onu ispat edene kadar **sıfır** sayılır — çünkü
    münâzarada müsellem olmayan öncül delil olarak kullanılamaz.
    """
    onculler: Tuple[Onerme, ...]
    netice: Onerme
    yakinler: Tuple[float, ...]
    tarih: List[Hamle] = field(default_factory=list)
    men_edilenler: Set[int] = field(default_factory=set)
    ispat_edilenler: Set[int] = field(default_factory=set)
    muaraza_kazandi: bool = False

    def __post_init__(self) -> None:
        if len(self.onculler) != len(self.yakinler):
            raise ValueError("her öncül için bir yakîn derecesi lazım")

    # --- hamleler -----------------------------------------------------
    def men_et(self, hedef: int) -> Tuple[bool, str]:
        ok, sebep = men_mesru_mu(hedef, len(self.onculler),
                                 self.men_edilenler)
        if ok:
            self.men_edilenler.add(hedef)
            self.ispat_edilenler.discard(hedef)
            self.tarih.append(Hamle("muteriz", ItirazNevi.MEN, hedef,
                                    aciklama="öncül müsellem değil"))
        return ok, sebep

    def ispat_et(self, hedef: int, delil: Sequence[Onerme]) -> bool:
        """Müddeî men edilen öncülü müstakil delille ispat eder."""
        if hedef not in self.men_edilenler:
            return False
        if not hukum(oncüller=list(delil), netice=self.onculler[hedef]):
            return False
        self.ispat_edilenler.add(hedef)
        self.tarih.append(Hamle("müddeî", None, hedef, tuple(delil),
                                aciklama="men edilen öncül ispat edildi"))
        return True

    def nakz_et(self) -> Tuple[bool, Optional[Dict[str, bool]]]:
        mumkun, sahit = nakz_gecerli_mi(self.onculler, self.netice)
        self.tarih.append(Hamle("muteriz", ItirazNevi.NAKZ,
                                aciklama=f"nakz {'tuttu' if mumkun else 'tutmadı'}"))
        return mumkun, sahit

    def muaraza_et(self, karsi_onculler: Sequence[Onerme]) -> bool:
        aks = degil(self.netice)
        tuttu = muaraza_gecerli_mi(karsi_onculler, aks)
        self.muaraza_kazandi = self.muaraza_kazandi or tuttu
        self.tarih.append(Hamle("muteriz", ItirazNevi.MUARAZA,
                                delil=tuple(karsi_onculler), netice=aks,
                                aciklama=f"muâraza {'tuttu' if tuttu else 'tutmadı'}"))
        return tuttu

    # --- hüküm --------------------------------------------------------
    def gecerli_yakinler(self) -> List[float]:
        """Men edilip ispat edilmemiş öncülün yakîni sıfırdır."""
        return [0.0 if (i in self.men_edilenler
                        and i not in self.ispat_edilenler) else y
                for i, y in enumerate(self.yakinler)]

    def hukum(self) -> Dict[str, object]:
        sekil = hukum(oncüller=list(self.onculler), netice=self.netice)
        y = yakin_gazali(self.gecerli_yakinler(), sekil)
        if self.muaraza_kazandi:
            y = 0.0
        galip = "müddeî" if y > 0.0 else "muteriz"
        return {
            "şekil_geçerli": sekil,
            "yakîn": y,
            "mertebe": mertebe_adi(y),
            "gālip": galip,
            "men_edilen": sorted(self.men_edilenler),
            "ispat_edilen": sorted(self.ispat_edilenler),
            "muâraza_kazandı": self.muaraza_kazandi,
            "hamle_sayısı": len(self.tarih),
        }


def _rapor_mizan_munazara() -> str:
    s: List[str] = []

    s.append("=== Gazâlî mîzânı: yakîn en zayıf öncül kadardır ===")
    for onc, gec in (((1.0, 1.0, 1.0), True), ((1.0, 0.6, 0.9), True),
                     ((1.0, 1.0, 1.0), False), ((), True)):
        y = yakin_gazali(onc, gec)
        s.append(f"  öncüller={str(onc):22s} şekil={str(gec):5s}"
                 f" → yakîn={y:.2f}  ({mertebe_adi(y)})")
    s.append("  zincir [kat'î halkalar ×5]      → "
             f"{yakin_zinciri([((1.0, 1.0), True)] * 5):.2f}"
             "   (uzunluk yakîni düşürmez)")
    s.append("  zincir [ortada 0.6'lık bir halka] → "
             f"{yakin_zinciri([((1.0,), True), ((0.6,), True), ((1.0,), True)]):.2f}")

    s.append("\n=== Münâzara: men' → ispat ===")
    A, B, C = deg("A"), deg("B"), deg("C")
    m = Munazara((ise(A, B), A), B, (0.9, 0.8))
    s.append(f"  başlangıç: {m.hukum()['yakîn']:.2f} ({m.hukum()['mertebe']})")
    ok, sbp = m.men_et(1)
    s.append(f"  muteriz P1'i men' etti (meşru={ok}) → yakîn={m.hukum()['yakîn']:.2f}"
             f"  gālip={m.hukum()['gālip']}")
    ok2, sbp2 = m.men_et(1)
    s.append(f"  aynı öncülü tekrar men': meşru={ok2}  sebep={sbp2!r}")
    ispat = m.ispat_et(1, [ve(A, C)])
    s.append(f"  müddeî A'yı (A∧C)'den ispat etti: {ispat}"
             f" → yakîn={m.hukum()['yakîn']:.2f} gālip={m.hukum()['gālip']}")

    s.append("\n=== Nakz: geçerli kıyas nakzedilemez ===")
    saglam = Munazara((ise(A, B), A), B, (1.0, 1.0))
    bozuk = Munazara((ise(A, B), B), A, (1.0, 1.0))   # tâlîyi vaz' etmek
    for ad, mn in (("modus ponens", saglam), ("tâlîyi vaz'", bozuk)):
        mum, sahit = mn.nakz_et()
        s.append(f"  {ad:14s} nakz mümkün={mum}  şâhit={sahit}")

    s.append("\n=== Muâraza: aksini ispat eden müstakil delil ===")
    mn = Munazara((ise(A, B), A), B, (1.0, 1.0))
    s.append(f"  boş muâraza tuttu mu? {mn.muaraza_et([C])}")
    s.append(f"  ¬B'yi veren delille?  {mn.muaraza_et([degil(B)])}")
    h = mn.hukum()
    s.append(f"  hüküm: yakîn={h['yakîn']:.2f} mertebe={h['mertebe']}"
             f" gālip={h['gālip']} hamle={h['hamle_sayısı']}")
    s.append("  not: muâraza tuttuğunda dâvâ sâkıt olur — çünkü aynı anda"
             " hem B hem ¬B ispatlanmış olur, bu ise öncüllerin"
             " tenâkuzunu gösterir.")
    return "\n".join(s)


# ====================================================================
#  Çipin toplu raporu
# ====================================================================
BOLUMLER = (
    ("KIYAS -- 256 monadik modelle tam karar", "_rapor_mizan_kiyas"),
    ("ÇIKARIM -- Hilbert, LK, G4ip", "_rapor_mizan_cikarim"),
    ("KİPLİK -- 512 Kripke çerçevesi, deontik, LTL", "_rapor_mizan_kiplik"),
    ("ÇOK DEĞERLİ -- t-normlar ve kalıntılar", "_rapor_mizan_cokdegerli"),
    ("YAPISAL-ALTI -- doğrusal, affine, sıkı, kuantum",
     "_rapor_mizan_altyapisal"),
    ("İSTİKRÂ -- Laplace, ICP, Nyāya, Stoa, Mill", "_rapor_mizan_istikra"),
    ("MÜNÂZARA -- men'/nakz/muâraza ve Gazâlî mîzânı",
     "_rapor_mizan_munazara"),
)


def rapor() -> str:                            # pragma: no cover
    """Sekiz odanın ölçümü, sırayla."""
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
