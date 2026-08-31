"""
NESNE KATMANI -- ızgarayı değil, **içindeki nesneleri** dönüştüren kaideler.

===================================================================
NİÇİN: BÜTÜN-IZGARA CEBRİ YETMİYOR, ÖLÇÜLDÜ
===================================================================

`nefs/kaideler.py` atomik ve terkipli bütün-ızgara dönüşümleri arıyor.
Ölçüldü (ARC-AGI-2, ilk 120 eğitim görevi)::

    eski çözücü (tek atom)      : 5 çözüldü
    yeni cebir, derinlik 1      : 7
    yeni cebir, derinlik 2      : 8      (yanlış cevap: 0)

Terkip kazandırıyor fakat **az**. Sebep derinlik değil **cins**tir:
bütün atomlarım ızgaranın tamamına aynı şeyi yapıyor. Halbuki ARC
görevlerinin büyük kısmı *nesneler* hakkındadır:

    "her nesneyi büyüklüğüne göre boya"
    "en çok deliği olan nesneyi seç"
    "küçük nesneleri sil, büyükleri bırak"
    "her nesneyi kendi rengine göre taşı"

Bunların hiçbiri bütün-ızgara dönüşümü değildir; **nesne başına** bir
karar, ve o kararın **nesnenin bir vasfından** çıkmasıdır. Klasik
mantıkta bunun adı vardır ve bu projede zaten kurulu: ``illet``
(sebep-vasıf) ile ``hüküm``ün eşleşmesi -- `mizan/istikra.py`nin
``temsil_hukmu``su tam bunu söyler: *"asıldaki hükmü fer'e taşı --
ancak illet tam intibak ederse."*

===================================================================
KAİDE NASIL ÖĞRENİLİYOR -- uydurma yok
===================================================================

1. Her gösterim çiftinde girdi nesnelere ayrılır.
2. Girdi ile çıktı **aynı şekilde** ise her nesnenin çıktıdaki rengi
   okunur. Böylece ``(vasıf → renk)`` çiftleri toplanır.
3. Bir vasıf ekseni (büyüklük sırası, hücre sayısı, delik sayısı,
   renk) **bütün gösterimlerde çelişkisiz** bir eşleme veriyorsa kaide
   odur. Çelişki varsa o eksen **reddedilir** -- zorlanmaz.
4. Hiçbir eksen tutmuyorsa kaide yok; sükût.

Yani eşleme veriden **çıkarılır**, ezberlenmez: sınama girdisinde
görülmemiş bir vasıf değeri çıkarsa kaide tatbik edilemez ve ``None``
döner. Bu bir kusur değil dürüstlüktür -- istikrânın haddi budur
(`mizan/istikra.py`: eksik istikrâ yakîn vermez).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Sequence, Set, Tuple

import numpy as np

from idrak.cozucu import _bilesenler
from .kaideler import ARKA, Kaide

__all__ = ["Nesne", "nesneleri_cikar", "VASIFLAR", "nesne_kaideleri"]

Izgara = np.ndarray


@dataclass
class Nesne:
    renk: int
    maske: np.ndarray
    kutu: Tuple[int, int, int, int]

    @property
    def hucre(self) -> int:
        return int(self.maske.sum())

    @property
    def en(self) -> int:
        return self.kutu[3] - self.kutu[2] + 1

    @property
    def boy(self) -> int:
        return self.kutu[1] - self.kutu[0] + 1

    @property
    def delik(self) -> int:
        """Kutu alanı − dolu hücre: içi ne kadar boş."""
        return self.en * self.boy - self.hucre

    @property
    def kare_mi(self) -> int:
        return int(self.en == self.boy and self.delik == 0)


def nesneleri_cikar(g: Izgara, arka: int = ARKA) -> List[Nesne]:
    return [Nesne(int(r), m, k) for r, m, k in _bilesenler(g, arka)]


# --- vasıf eksenleri: nesnenin hangi cihetine bakılacak -------------
#
# Her vasıf ``(ad, nesne → anahtar)``. "Sıra" cinsinden olanlar
# nesneleri kendi aralarında sıralar; "mutlak" olanlar tek nesneye
# bakar. İkisi de meşrudur ve ikisi de sınanır.
VASIFLAR: Dict[str, Callable[[Nesne, List[Nesne]], object]] = {
    "hücre": lambda n, hepsi: n.hucre,
    "renk": lambda n, hepsi: n.renk,
    "delik": lambda n, hepsi: n.delik,
    "boy×en": lambda n, hepsi: (n.boy, n.en),
    "kare_mi": lambda n, hepsi: n.kare_mi,
    "büyüklük_sırası": lambda n, hepsi: sorted(
        {x.hucre for x in hepsi}).index(n.hucre),
    "büyüklük_sırası_tersten": lambda n, hepsi: sorted(
        {x.hucre for x in hepsi}, reverse=True).index(n.hucre),
    "aynı_boy_sayısı": lambda n, hepsi: sum(
        1 for x in hepsi if x.hucre == n.hucre),
    # --- ölçümle eklenenler --------------------------------------
    #
    # ``nesne_sil[hücre]`` dört görevde 0,90-0,98 hücre isabetiyle
    # **ıskalıyordu**: aile doğru, vasıf yanlış. Yani "hangi nesne
    # silinir?" sorusunun cevabı büyüklük değil başka bir cihet. Aşağıdaki
    # dört eksen o cihetlerdir ve her biri ARC'de sık görülen bir
    # ayrımı taşır:
    #
    # * **şekil** -- nesnenin renkten soyut sûreti (normalleştirilmiş
    #   maske). "Aynı şekilliler" bir sınıf teşkil eder.
    # * **şekil_tekrarı** -- o sûretten ızgarada kaç tane var. Tekil
    #   olan çoğu zaman istisnadır; ARC istisnayı sever.
    # * **kenarda** -- nesne ızgaranın kenarına değiyor mu. Değen ile
    #   değmeyen ayrımı topolojiktir, keyfî değil.
    # * **renk_çokluğu** -- o rengin ızgaradaki nesne sayısı. "Yalnız
    #   kalan rengi seç" bu eksende görülür.
    "şekil": lambda n, hepsi: _suret(n),
    "şekil_tekrarı": lambda n, hepsi: sum(
        1 for x in hepsi if _suret(x) == _suret(n)),
    "kenarda": lambda n, hepsi: int(n.kutu[0] == 0 or n.kutu[2] == 0),
    "renk_çokluğu": lambda n, hepsi: sum(
        1 for x in hepsi if x.renk == n.renk),
}


def _suret(n: "Nesne") -> Tuple[Tuple[int, ...], ...]:
    """Nesnenin **renkten ve yerden soyut** sûreti: kutusuna kırpılmış
    maske. İki nesne aynı sûretteyse aynı şeydir, nerede ve ne renk
    olduğuna bakılmaz."""
    r0, r1, c0, c1 = n.kutu
    m = n.maske[r0:r1 + 1, c0:c1 + 1]
    return tuple(tuple(int(v) for v in satir) for satir in m)


def _renk_kaidesi_ogren(ciftler: Sequence[Tuple[Izgara, Izgara]],
                        vasif: str) -> Optional[Dict[object, int]]:
    """``vasıf → çıktı rengi`` eşlemesi bütün gösterimlerde tutuyor mu?"""
    f: Dict[object, int] = {}
    gorulen = False
    for a, b in ciftler:
        if a.shape != b.shape:
            return None
        ns = nesneleri_cikar(a)
        if not ns:
            return None
        for n in ns:
            renkler = {int(v) for v in b[n.maske]}
            if len(renkler) != 1:
                return None           # nesne tek renge boyanmamış
            hedef = int(next(iter(renkler)))
            anahtar = VASIFLAR[vasif](n, ns)
            if anahtar in f and f[anahtar] != hedef:
                return None           # çelişki: bu eksen tutmuyor
            f[anahtar] = hedef
            gorulen = True
        # arka plan değişmemeli
        arka_maske = np.ones(a.shape, bool)
        for n in ns:
            arka_maske &= ~n.maske
        if not np.array_equal(a[arka_maske], b[arka_maske]):
            return None
    return f if gorulen else None


def _boya(g: Izgara, vasif: str, f: Dict[object, int],
          aynen: bool = False) -> Optional[Izgara]:
    """``aynen=True``: vasfını bilmediğim nesneye **dokunmam**.

    İki sükût ayrımı için bkz. `nefs/hucre.py`nin ``_tatbik`` şerhi.
    Kısaca: "bu nesneyi bilmiyorum" ile "bu vazifeyi reddediyorum"
    aynı şey değildir; ikisini de ``None`` ile söylemek bırak-birini
    kapısını kör eder, zira ``None`` ne doğrudur ne yanlış.
    """
    ns = nesneleri_cikar(g)
    if not ns:
        return None
    out = g.copy()
    for n in ns:
        anahtar = VASIFLAR[vasif](n, ns)
        if anahtar not in f:
            if aynen:
                continue
            return None               # görülmemiş vasıf: istikrâ yetmez
        out[n.maske] = f[anahtar]
    return out


def _sec_kaidesi_ogren(ciftler: Sequence[Tuple[Izgara, Izgara]],
                       vasif: str, en_buyuk: bool) -> bool:
    """Çıktı, ``vasıf``ta uç olan nesnenin kutusu mu?"""
    for a, b in ciftler:
        ns = nesneleri_cikar(a)
        if not ns:
            return False
        try:
            anahtarlar = [(VASIFLAR[vasif](n, ns), n) for n in ns]
            uc = (max if en_buyuk else min)(anahtarlar, key=lambda x: x[0])[1]
        except Exception:                                # noqa: BLE001
            return False
        r0, r1, c0, c1 = uc.kutu
        kes = a[r0:r1 + 1, c0:c1 + 1]
        if kes.shape != b.shape or not np.array_equal(kes, b):
            return False
    return True


def _sec(g: Izgara, vasif: str, en_buyuk: bool) -> Optional[Izgara]:
    ns = nesneleri_cikar(g)
    if not ns:
        return None
    try:
        anahtarlar = [(VASIFLAR[vasif](n, ns), n) for n in ns]
        uc = (max if en_buyuk else min)(anahtarlar, key=lambda x: x[0])[1]
    except Exception:                                    # noqa: BLE001
        return None
    r0, r1, c0, c1 = uc.kutu
    return g[r0:r1 + 1, c0:c1 + 1]


def _sil_kaidesi_ogren(ciftler: Sequence[Tuple[Izgara, Izgara]],
                       vasif: str) -> Optional[Set[object]]:
    """Hangi vasıf değerine sahip nesneler **siliniyor**?"""
    silinen: Set[object] = set()
    kalan: Set[object] = set()
    for a, b in ciftler:
        if a.shape != b.shape:
            return None
        ns = nesneleri_cikar(a)
        if not ns:
            return None
        for n in ns:
            anahtar = VASIFLAR[vasif](n, ns)
            hedef = {int(v) for v in b[n.maske]}
            if hedef == {ARKA}:
                silinen.add(anahtar)
            elif np.array_equal(a[n.maske], b[n.maske]):
                kalan.add(anahtar)
            else:
                return None           # ne silinmiş ne aynı: başka kaide
    if not silinen or (silinen & kalan):
        return None
    return silinen


def _sil(g: Izgara, vasif: str, silinen: Set[object]) -> Optional[Izgara]:
    ns = nesneleri_cikar(g)
    if not ns:
        return None
    out = g.copy()
    for n in ns:
        if VASIFLAR[vasif](n, ns) in silinen:
            out[n.maske] = ARKA
    return out


def nesne_kaideleri(ciftler: Sequence[Tuple[Izgara, Izgara]]
                    ) -> List[Kaide]:
    """Gösterimlerden **öğrenilen** nesne kaideleri.

    Üç aile: nesneyi vasfına göre **boya**, vasıfta uç olanı **seç**,
    vasfı şu olanları **sil**. Her biri bütün gösterimlerde
    çelişkisizse kabul edilir; çelişki varsa reddedilir.
    """
    out: List[Kaide] = []
    for vasif in VASIFLAR:
        f = _renk_kaidesi_ogren(ciftler, vasif)
        if f:
            out.append(Kaide("nesne_boya[%s]" % vasif,
                             lambda g, v=vasif, m=f: _boya(g, v, m),
                             1, len(f)))
            out.append(Kaide("nesne_boya[%s|aynen]" % vasif,
                             lambda g, v=vasif, m=f: _boya(g, v, m, True),
                             1, len(f)))
        s = _sil_kaidesi_ogren(ciftler, vasif)
        if s:
            out.append(Kaide("nesne_sil[%s]" % vasif,
                             lambda g, v=vasif, m=s: _sil(g, v, m),
                             1, len(s)))
        for buyuk in (True, False):
            if _sec_kaidesi_ogren(ciftler, vasif, buyuk):
                out.append(Kaide("nesne_seç[%s%s]"
                                 % (vasif, "↑" if buyuk else "↓"),
                                 lambda g, v=vasif, b=buyuk: _sec(g, v, b)))
    return out
