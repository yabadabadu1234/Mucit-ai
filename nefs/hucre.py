"""
HÜCRE KAİDELERİ -- çıktı hücresini **yerel desenden** öğrenmek.

===================================================================
NİÇİN: AYNI ŞEKİLLİ GÖREVLER EZİCİ ÇOĞUNLUK
===================================================================

ARC-AGI-2 eğitim kümesinin ilk 200 görevi ölçüldü::

    girdi ile çıktı AYNI şekilde   : 141 / 200   (%70)
    çıktı şekli sabit              : 101
    çıktı girdinin tam katı        : 150
    çıktı ≤ 25 hücre               :  31

Yani görevlerin çoğunda ızgara **yerinde** değişiyor: hücre hücre.
`nefs/kaideler.py`nin bütün-ızgara atomları (döndür, kırp, döşe) bu
aileyi hiç yakalayamaz; `nefs/nesne.py` bir kısmını yakalar (nesneyi
boya/sil) fakat hepsini değil -- "kapalı bölgeyi doldur", "gürültüyü
temizle", "kenar çiz" gibi kaideler nesne değil **komşuluk**
meselesidir.

===================================================================
ÖĞRENİLEN ŞEY
===================================================================

Bir **bağlam** seçilir ve çıktı hücresinin o bağlamdan çıkıp
çıkmadığına bakılır::

    çıktı[i,j] = f( bağlam(girdi, i, j) )

Bağlamlar (dar → geniş):

* ``renk``        -- yalnız kendi rengi (basit renk eşlemesi)
* ``renk+dolu``   -- kendi rengi + kaç komşusu dolu (0–4)
* ``artı``        -- kendi + dört komşu (5'li)
* ``3x3``         -- tam 3×3 desen

``f`` bütün gösterimlerde **çelişkisiz** olmalı; bir tek çelişki o
bağlamı reddettirir. Zorlama yok.

===================================================================
GÖRÜLMEMİŞ DESENDE SUSMAK -- ezber değil istikrâ
===================================================================

Sınama ızgarasında ``f``nin hiç görmediği bir bağlam çıkarsa kaide
**tatbik edilemez** ve ``None`` döner. Bu bir kusur değil, istikrânın
haddidir (`mizan/istikra.py`: *eksik istikrâ hiçbir sonlu ``n`` için
yakîn vermez*). Görülmemiş deseni "en yakınına benzet" diye doldurmak
ezber olurdu ve tam eşleşme ölçütünü sahte kılardı.

**Bu, aşırı uydurmaya karşı asıl tedbirdir ve ölçülür:** bağlam ne
kadar genişse (3×3) o kadar çok görülmemiş desen çıkar, yani kaide o
kadar sık susar. Dar bağlam çok genelleşir fakat az tutar. Arama dar
bağlamdan geniş bağlama gider ve **ilk tutanı** alır -- Occam.
"""
from __future__ import annotations

from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

from .kaideler import ARKA, Kaide

__all__ = ["BAGLAMLAR", "hucre_kaideleri", "kapali_bolgeler"]

Izgara = np.ndarray


def _pad(g: Izgara) -> Izgara:
    """Kenarları ``-1`` ile çevrele: "ızgara dışı" ayrı bir semboldür."""
    return np.pad(g, 1, constant_values=-1)


def _baglam_renk(P: Izgara, i: int, j: int) -> object:
    return int(P[i + 1, j + 1])


def _baglam_renk_dolu(P: Izgara, i: int, j: int) -> object:
    k = [P[i, j + 1], P[i + 2, j + 1], P[i + 1, j], P[i + 1, j + 2]]
    return (int(P[i + 1, j + 1]),
            int(sum(1 for v in k if v > ARKA)))


def _baglam_arti(P: Izgara, i: int, j: int) -> object:
    return (int(P[i + 1, j + 1]), int(P[i, j + 1]), int(P[i + 2, j + 1]),
            int(P[i + 1, j]), int(P[i + 1, j + 2]))


def _baglam_3x3(P: Izgara, i: int, j: int) -> object:
    return tuple(int(v) for v in P[i:i + 3, j:j + 3].reshape(-1))


#: Bağlamlar **dardan genişe** sıralı: Occam bu sırayı takip eder.
BAGLAMLAR: Tuple[Tuple[str, Callable[[Izgara, int, int], object]], ...] = (
    ("renk", _baglam_renk),
    ("renk+dolu", _baglam_renk_dolu),
    ("artı", _baglam_arti),
    ("3x3", _baglam_3x3),
)


def _ogren(ciftler: Sequence[Tuple[Izgara, Izgara]],
           baglam: Callable[[Izgara, int, int], object]
           ) -> Optional[Dict[object, int]]:
    f: Dict[object, int] = {}
    for a, b in ciftler:
        if a.shape != b.shape:
            return None
        P = _pad(np.asarray(a, np.int64))
        B = np.asarray(b, np.int64)
        H, W = B.shape
        for i in range(H):
            for j in range(W):
                k = baglam(P, i, j)
                v = int(B[i, j])
                if k in f:
                    if f[k] != v:
                        return None          # çelişki: bağlam yetmiyor
                else:
                    f[k] = v
    return f or None


def _tatbik(g: Izgara, baglam: Callable[[Izgara, int, int], object],
            f: Dict[object, int]) -> Optional[Izgara]:
    P = _pad(np.asarray(g, np.int64))
    H, W = g.shape
    out = np.zeros((H, W), dtype=np.int64)
    for i in range(H):
        for j in range(W):
            k = baglam(P, i, j)
            if k not in f:
                return None                  # görülmemiş desen: sükût
            out[i, j] = f[k]
    return out


# =====================================================================
#  Kapalı bölge (delik) doldurma -- ARC'de çok sık
# =====================================================================
def kapali_bolgeler(g: Izgara, arka: int = ARKA) -> np.ndarray:
    """Kenara **bağlı olmayan** arka plan hücreleri: kapalı delikler.

    Kenardan taşkın doldurma yapılır; ulaşılamayan arka plan hücreleri
    bir şeklin **içinde** demektir.
    """
    H, W = g.shape
    disar = np.zeros((H, W), bool)
    yigin: List[Tuple[int, int]] = []
    for i in range(H):
        for j in (0, W - 1):
            if g[i, j] == arka and not disar[i, j]:
                disar[i, j] = True
                yigin.append((i, j))
    for j in range(W):
        for i in (0, H - 1):
            if g[i, j] == arka and not disar[i, j]:
                disar[i, j] = True
                yigin.append((i, j))
    while yigin:
        y, x = yigin.pop()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            a, b = y + dy, x + dx
            if (0 <= a < H and 0 <= b < W and not disar[a, b]
                    and g[a, b] == arka):
                disar[a, b] = True
                yigin.append((a, b))
    return (g == arka) & ~disar


def _delik_doldur(g: Izgara, renk: int) -> Optional[Izgara]:
    m = kapali_bolgeler(g)
    if not m.any():
        return None
    out = g.copy()
    out[m] = renk
    return out


def hucre_kaideleri(ciftler: Sequence[Tuple[Izgara, Izgara]]
                    ) -> List[Kaide]:
    """Gösterimlerden **öğrenilen** hücre kaideleri.

    Bağlamlar dardan genişe denenir; tutan her biri döner ve
    `nefs/kaideler.py` Occam'a göre en kısasını seçer.
    """
    out: List[Kaide] = []
    ayni = all(a.shape == b.shape for a, b in ciftler)
    if not ayni or not ciftler:
        return out

    # boyut sınırı: 3×3 bağlam büyük ızgarada pahalıdır
    toplam = sum(int(a.size) for a, _ in ciftler)
    for ad, fn in BAGLAMLAR:
        if ad == "3x3" and toplam > 6000:
            continue
        f = _ogren(ciftler, fn)
        if f is None:
            continue
        out.append(Kaide("hücre[%s]" % ad,
                         lambda g, b=fn, m=f: _tatbik(g, b, m),
                         1, len(f)))

    # Kapalı bölge doldurma: renk çıktıdan alınır (kör değil)
    renkler = set()
    for a, b in ciftler:
        if a.shape == b.shape:
            fark = np.asarray(b)[np.asarray(a) == ARKA]
            renkler |= {int(v) for v in np.unique(fark) if int(v) != ARKA}
    for r in sorted(renkler)[:4]:
        out.append(Kaide("delik_doldur:%d" % r,
                         lambda g, c=r: _delik_doldur(g, c)))
    return out
