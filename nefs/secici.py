"""
SEÇİCİ × DÖNÜŞTÜRÜCÜ -- kaide **listesi** değil kaide **çarpımı**.

===================================================================
NİÇİN: SAYILDI VE ARİTMETİK TUTMUYOR
===================================================================

Şu ana kadarki dört katman (`nefs/kaideler.py` bütün-ızgara,
`nefs/nesne.py` nesne, `nefs/hucre.py` yerel bağlam,
`nefs/tamamlama.py` ekleme) bir **katalog**tur: elle yazılmış kaide
aileleri. Ölçüldü (ARC-AGI-2 eğitim 120)::

    tek atom (eski çözücü)                    5
    terkip cebri, derinlik 2                  8
    + nesne + hücre aileleri                  9
    + aynı şekilli dört aile                 12
    + tamamlama katmanı                      13

Yani **her yeni aile ortalama bir görev** kazandırıyor. 120'nin
yarısı için ~50 aile daha yazmak gerekir. Bu bir mimarî değil, bir
angaryadır; üstelik ARC-AGI-2 tam olarak bunu boşa çıkarmak için
tasarlanmıştır -- katalog büyütmek, kataloğun görmediği görevde
hiçbir şey vermez.

===================================================================
KÜLLİ HATA NEREDE: KAPALI KÜME
===================================================================

Kataloğun kusuru büyüklüğü değil **kapalılığı**dır. Model, önceden
yazılmış kaidelerden birini *seçer*; hiç birleştirmez. İnsan zihni
öyle yapmaz: yeni bir bulmaca karşısında hazır bir kaide aramaz,
**yerinde bir kaide kurar** -- ve bunu iki parçadan kurar:

    "**şunlara** (seçici) **şunu** yap (dönüştürücü)"

    "kenara değen nesneleri sil"      = kenardaki_nesneler × sil
    "kapalı boşlukları sarıya boya"   = kapalı_bölgeler × boya(sarı)
    "en büyük nesne hariç her şeyi sil" = en_büyük_değil × sil
    "tek şekilli olanı kırmızıya çevir" = tekil_şekilli × boya(kırmızı)

Bu ayrım keyfî değildir; kataloğun kendisi zaten bunu **örtük**
taşıyordu: ``nesne_sil[vasıf]`` bir seçici ile bir dönüştürücünün
yapışmış hâlidir. Yapışık olduğu için de her yeni terkip elle
yazılmak zorundaydı. Ayırınca çarpım doğar::

    16 seçici × 14 dönüştürücü = 224 kaide, 30 parçadan
    derinlik 2 terkiple                    ≈ 50 000

Yani **parça sayısı doğrusal, kaide sayısı çarpımsal** büyür. Aynı
fikir `nefs/operad.py`nin kompozisyonudur: parçalardan bütün kurmak.

===================================================================
EZBER TEDBİRİ -- niçin bu genişleme tehlikesiz
===================================================================

50 000 kaide arasından gösterimlere uyan birini bulmak, ezberin
**kolaylaşması** demektir. Onun için bu dosya, `nefs/kaideler.py`nin
``capraz_gecerli`` kapısı kurulmadan yazılamazdı: veriden öğrenen her
kaide bırak-birini istikrâsından geçmek zorundadır. Buradaki
seçicilerin ve dönüştürücülerin **çoğu parametresizdir**
(``hipotez=0``): "kenara değen" bir tablo değil bir vasıftır,
ezberlenecek bir şeyi yoktur. Renk taşıyanlarda renk görevin kendi
çıktısından alınır ve ``hipotez`` doğru bildirilir.

Sıra mühimdir ve tesadüf değildir: **evvela ölçüt, sonra genişleme.**
"""
from __future__ import annotations

from typing import Callable, Dict, List, Optional, Sequence, Set, Tuple

import numpy as np

from idrak.cozucu import _bilesenler
from .kaideler import ARKA, Kaide
from .tamamlama import (BAKISIMLAR, YONLER, _kapali_bolgeler,
                        bakisimlar_tutan)

__all__ = ["seciciler", "donusturucular", "carpim_kaideleri"]

Izgara = np.ndarray
Maske = np.ndarray


# ===================================================================
#  SEÇİCİLER -- ızgaradan bir hücre kümesi
# ===================================================================
#
# Her seçici ``ızgara → boole maske``. Hiçbiri renk **öğrenmez**;
# hepsi ızgaranın kendi yapısından okunur. Onun için ``hipotez=0``dır
# ve ezberleyemezler.
def _nesneler(g: Izgara):
    return _bilesenler(np.asarray(g, np.int64), ARKA)


def _bos(g: Izgara) -> Maske:
    return np.zeros(np.asarray(g).shape, bool)


def _uc_nesne(g: Izgara, en_buyuk: bool, haric: bool) -> Maske:
    ns = _nesneler(g)
    if not ns:
        return _bos(g)
    uc = (max if en_buyuk else min)(ns, key=lambda t: int(t[1].sum()))
    m = uc[1].copy()
    if not haric:
        return m
    hepsi = _bos(g)
    for _r, mm, _k in ns:
        hepsi |= mm
    return hepsi & ~m


def _suret(m: Maske, kutu) -> Tuple:
    r0, r1, c0, c1 = kutu
    k = m[r0:r1 + 1, c0:c1 + 1]
    return tuple(tuple(int(v) for v in s) for s in k)


def _sekil_sayisina_gore(g: Izgara, tekil: bool) -> Maske:
    """Sûreti ızgarada **bir kere** geçen nesneler (veya tersi).

    ARC istisnayı sever: "diğerlerine benzemeyeni bul" bu eksendedir
    ve renkten bağımsızdır.
    """
    ns = _nesneler(g)
    if not ns:
        return _bos(g)
    sayim: Dict[Tuple, int] = {}
    for _r, m, k in ns:
        s = _suret(m, k)
        sayim[s] = sayim.get(s, 0) + 1
    out = _bos(g)
    for _r, m, k in ns:
        birdir = sayim[_suret(m, k)] == 1
        if birdir == tekil:
            out |= m
    return out


def _kenardaki(g: Izgara, deger: bool) -> Maske:
    a = np.asarray(g)
    R, C = a.shape
    out = _bos(g)
    for _r, m, (r0, r1, c0, c1) in _nesneler(g):
        deg = (r0 == 0 or c0 == 0 or r1 == R - 1 or c1 == C - 1)
        if deg == deger:
            out |= m
    return out


def _tek_hucrelik(g: Izgara, deger: bool) -> Maske:
    out = _bos(g)
    for _r, m, _k in _nesneler(g):
        if (int(m.sum()) == 1) == deger:
            out |= m
    return out


def _kapali(g: Izgara) -> Maske:
    out = _bos(g)
    for m in _kapali_bolgeler(np.asarray(g, np.int64)):
        out |= m
    return out


def _bakisim_kirigi(g: Izgara) -> Maske:
    """Tutan bakışıma **uymayan** hücreler: bozulmuş olan yer.

    Bakışım tutuyorsa ve bir hücre eşiyle uyuşmuyorsa, bozulan odur.
    Boş olan taraf değil; boşluk uyuşmazlık sayılmaz (bkz.
    `nefs/tamamlama.py`).
    """
    a = np.asarray(g, np.int64)
    adlar = bakisimlar_tutan(a)
    out = _bos(a)
    for ad in adlar:
        h = np.asarray(BAKISIMLAR[ad](a))
        if h.shape != a.shape:
            continue
        out |= (a != ARKA) & (h != ARKA) & (a != h)
    return out


def _renk_maskesi(g: Izgara, c: int) -> Maske:
    return np.asarray(g) == c


def seciciler(ciftler: Sequence[Tuple[Izgara, Izgara]]
              ) -> List[Tuple[str, Callable[[Izgara], Maske]]]:
    """Seçici listesi. Renk seçicileri **görevde geçen** renklerden."""
    out: List[Tuple[str, Callable[[Izgara], Maske]]] = [
        ("hepsi", lambda g: np.ones(np.asarray(g).shape, bool)),
        ("dolu", lambda g: np.asarray(g) != ARKA),
        ("boş", lambda g: np.asarray(g) == ARKA),
        ("kapalı_bölge", _kapali),
        ("en_büyük", lambda g: _uc_nesne(g, True, False)),
        ("en_büyük_hariç", lambda g: _uc_nesne(g, True, True)),
        ("en_küçük", lambda g: _uc_nesne(g, False, False)),
        ("en_küçük_hariç", lambda g: _uc_nesne(g, False, True)),
        ("tekil_şekilli", lambda g: _sekil_sayisina_gore(g, True)),
        ("çoğul_şekilli", lambda g: _sekil_sayisina_gore(g, False)),
        ("kenarda", lambda g: _kenardaki(g, True)),
        ("kenarda_değil", lambda g: _kenardaki(g, False)),
        ("tek_hücrelik", lambda g: _tek_hucrelik(g, True)),
        ("tek_hücrelik_değil", lambda g: _tek_hucrelik(g, False)),
        ("bakışım_kırığı", _bakisim_kirigi),
    ]
    renkler: Set[int] = set()
    for a, _b in ciftler:
        renkler |= {int(v) for v in np.unique(np.asarray(a))}
    for c in sorted(renkler):
        if c == ARKA:
            continue
        out.append(("renk=%d" % c, lambda g, k=c: _renk_maskesi(g, k)))
    return out


# ===================================================================
#  DÖNÜŞTÜRÜCÜLER -- (ızgara, maske) → ızgara
# ===================================================================
def _boya(g: Izgara, m: Maske, c: int) -> Optional[Izgara]:
    out = np.asarray(g, np.int64).copy()
    out[m] = c
    return out


def _en_sik_renk(g: Izgara, m: Maske) -> Optional[int]:
    v = np.asarray(g)[m]
    v = v[v != ARKA]
    if v.size == 0:
        return None
    d, s = np.unique(v, return_counts=True)
    return int(d[s.argmax()])


def _cogunluga_boya(g: Izgara, m: Maske) -> Optional[Izgara]:
    c = _en_sik_renk(g, m)
    if c is None:
        return None
    return _boya(g, m, c)


def _kutu_doldur_maskede(g: Izgara, m: Maske) -> Optional[Izgara]:
    a = np.asarray(g, np.int64)
    out = a.copy()
    for renk, mm, (r0, r1, c0, c1) in _bilesenler(a, ARKA):
        if not (mm & m).any():
            continue
        out[r0:r1 + 1, c0:c1 + 1] = int(renk)
    return out


def _isin_maskeden(g: Izgara, m: Maske, yon: str) -> Optional[Izgara]:
    a = np.asarray(g, np.int64)
    R, C = a.shape
    kaynak = np.argwhere(m & (a != ARKA))
    if kaynak.size == 0 or len(kaynak) > 300:
        return None
    out = a.copy()
    for y, x in kaynak.tolist():
        renk = int(a[y, x])
        for dy, dx in YONLER[yon]:
            v, u = y + dy, x + dx
            while 0 <= v < R and 0 <= u < C and a[v, u] == ARKA:
                out[v, u] = renk
                v += dy
                u += dx
    return out


def _bakisimdan_doldur(g: Izgara, m: Maske) -> Optional[Izgara]:
    a = np.asarray(g, np.int64)
    adlar = bakisimlar_tutan(a)
    if not adlar:
        return None
    out = a.copy()
    for ad in adlar:
        h = np.asarray(BAKISIMLAR[ad](a))
        if h.shape != a.shape:
            continue
        yer = m & (h != ARKA)
        out[yer] = h[yer]
    return out


def donusturucular(ciftler: Sequence[Tuple[Izgara, Izgara]]
                   ) -> List[Tuple[str, Callable[[Izgara, Maske],
                                                 Optional[Izgara]], int]]:
    """``(ad, (ızgara, maske) → ızgara, hipotez)``.

    Renk taşıyanların rengi **çıktılarda geçen** renklerden alınır --
    kör arama değil, görevin kendi ölçüsü. ``hipotez`` orada 1'dir:
    bir sabit seçilmiştir ve bu bildirilir.
    """
    out: List[Tuple[str, Callable[[Izgara, Maske], Optional[Izgara]],
                    int]] = [
        ("sil", lambda g, m: _boya(g, m, ARKA), 0),
        ("çoğunluğa_boya", _cogunluga_boya, 0),
        ("kutu_doldur", _kutu_doldur_maskede, 0),
        ("bakışımdan_doldur", _bakisimdan_doldur, 0),
    ]
    for yon in ("dört", "yatay", "dikey", "çapraz"):
        out.append(("ışın[%s]" % yon,
                    lambda g, m, y=yon: _isin_maskeden(g, m, y), 0))
    cikti_renk: Set[int] = set()
    for _a, b in ciftler:
        cikti_renk |= {int(v) for v in np.unique(np.asarray(b))}
    for c in sorted(cikti_renk):
        out.append(("boya[%d]" % c,
                    lambda g, m, k=c: _boya(g, m, k), 1))
    return out


# ===================================================================
#  ÇARPIM
# ===================================================================
def carpim_kaideleri(ciftler: Sequence[Tuple[Izgara, Izgara]],
                     azami: int = 4000) -> List[Kaide]:
    """Seçici × dönüştürücü çarpımı, ``Kaide`` olarak.

    Çarpımın tamamı üretilir fakat **erken elenir**: ilk gösterimde
    girdiyi hiç değiştirmeyen veya ızgara ölçüsünü bozan terkip
    listeye alınmaz. Böylece `nefs/kaideler.py`nin terkip araması
    ölü dallarla şişmez.
    """
    S = seciciler(ciftler)
    D = donusturucular(ciftler)
    if not ciftler:
        return []
    a0 = np.asarray(ciftler[0][0], np.int64)

    def yap(sf, df):
        def f(g: Izgara) -> Optional[Izgara]:
            g = np.asarray(g, np.int64)
            try:
                m = sf(g)
            except Exception:                            # noqa: BLE001
                return None
            if m is None or m.shape != g.shape or not m.any():
                return None
            try:
                return df(g, m)
            except Exception:                            # noqa: BLE001
                return None
        return f

    out: List[Kaide] = []
    for sad, sf in S:
        for dad, df, hip in D:
            f = yap(sf, df)
            o = f(a0)
            # Hiçbir şey yapmayan terkip kaide değildir: birim zaten var.
            if o is None or o.shape != a0.shape or np.array_equal(o, a0):
                continue
            out.append(Kaide("%s→%s" % (sad, dad), f, 1, hip))
            if len(out) >= azami:
                return out
    return out
