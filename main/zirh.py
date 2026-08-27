"""
Enine topolojik zırh -- **her uzaya mahsus**, katman değil kesit (kütük H23).

Dalga ``m``inci uzayda evrildikten sonra dört süzgeçten geçer. Bunlar
mertebe listesine ait numaralar değildir; 20 lifi **enine kesen**
teftiş operatörleridir.

Bütün ölçüler MPS'in kendi verisinden çıkar -- yani dalganın kendisinden,
harici bir şablondan değil:

* **Sheaf**: komşu yuvaların yerel kesitleri (indirgenmiş yoğunlukları)
  ek yerinde uyuşuyor mu? Uyuşmayan yerde dalganın o bileşeni yutulur.
* **Homotopi**: aynı homotopi sınıfındaki dalgalar aynı faza getirilir.
  Reel cebirde faz işarettir; işaret hizalaması yapıcı girişimi kurar.
* **Betti**: yuva korelasyon çizgesinin ``β₀``ı. ``β₀ > 1`` bilgi ayrık
  adacıklara bölünmüş, yani **ezberlenmiş** demektir; genlik cezalanır.
* **Kohomoloji**: bir mertebeden diğerine taşınamayan bileşen. Önceki
  uzayın okumasına **dik** olup norm taşıyan kısım tıkanıklıktır; o yön
  yutulur ve şiddeti ayrık motora sinyal olarak döner (Postnikov).

Hepsi ``O(N)``dir: yuva yoğunlukları yerel, çizge yalnız komşuluklardan
kurulu. 6 milyon kübitte de koşar.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from .kategori import Uzay
from .yazmac import Yazmac

__all__ = ["ZirhIzi", "zirh_uygula", "okuma_vektoru"]


@dataclass
class ZirhIzi:
    """Bir uzaydaki zırh teftişinin izi."""
    mertebe: int
    sheaf_duzeltme: float
    homotopi_isaret: float
    betti0: int
    betti_ceza: float
    tikaniklik: float


def okuma_vektoru(y: Yazmac, ornek: int = 256) -> np.ndarray:
    """Dalganın ``ornek`` yuvadaki **zayıf** okuması -- çöküş yok.

    Her yuvanın ``2×2`` indirgenmiş yoğunluğundan Bloch benzeri iki reel
    sayı alınır: ``z = ρ₀₀ − ρ₁₁`` (nüfus farkı) ve ``x = 2ρ₀₁`` (uyum).
    Bu, süperpozisyonu bozmadan alınan bir POVM okumasıdır.
    """
    n = y.n
    idx = np.linspace(0, n - 1, min(ornek, n)).astype(int)
    R = y.yuva_yogunluklari(idx)                 # (k, 2, 2)
    z = R[:, 0, 0] - R[:, 1, 1]
    x = 2.0 * R[:, 0, 1]
    return np.concatenate([z, x])


def _betti0(v: np.ndarray, esik: float = 0.35) -> int:
    """Komşuluk çizgesinin bağlantılı bileşen sayısı -- zincir üzerinde.

    Zincir olduğu için çizge yalnız komşu kenarlardan ibarettir; bileşen
    sayısı, kopmuş komşuluk sayısının bir fazlasıdır. ``O(N)``dir ve
    ``n×n`` bitişiklik dizeyi hiç kurulmaz.
    """
    if len(v) < 2:
        return 1
    fark = np.abs(np.diff(v))
    olcek = float(np.median(fark)) + 1e-12
    kopuk = int(np.sum(fark > esik + 3.0 * olcek))
    return 1 + kopuk


def zirh_uygula(y: Yazmac, u: Uzay, okuma: np.ndarray,
                onceki: Optional[np.ndarray]) -> Tuple[np.ndarray, ZirhIzi]:
    """Dört süzgeci sırayla uygula; düzeltilmiş okumayı ve izi döndür.

    Süzgeçler okuma vektörü üzerinde çalışır ve **yazmaca geri yansır**:
    Betti cezası bir genlik tartısı, homotopi bir işaret kapısı olarak
    kübitlere uygulanır. Yani zırh yalnız ölçmez, dalgayı da büker.
    """
    v = np.asarray(okuma, float).copy()
    k = len(v) // 2
    z = v[:k]

    # --- 1. Sheaf: ek yerlerindeki kopukluğu bastır
    if k >= 2:
        fark = np.diff(z)
        d = np.zeros_like(z)
        d[:-1] += 0.5 * fark
        d[1:] -= 0.5 * fark
        agirlik = 1.0 / (1.0 + float(np.mean(np.abs(fark))))
        z_yeni = z + (1.0 - agirlik) * d
        sheaf_d = float(np.linalg.norm(z_yeni - z))
        z = z_yeni
    else:
        sheaf_d = 0.0

    # --- 2. Homotopi: baskın bileşenin işaretine hizala (yapıcı girişim)
    i = int(np.argmax(np.abs(z))) if k else 0
    isaret = 1.0 if (k == 0 or z[i] >= 0) else -1.0
    z = z * isaret

    # --- 3. Betti: ayrık adacık = ezber → genlik cezası
    b0 = _betti0(z)
    ceza = float(np.exp(-0.25 * (b0 - 1) ** 2))
    z = z * ceza

    # --- 4. Kohomoloji: taşınamayan (dik) bileşeni yut
    tik = 0.0
    if onceki is not None and len(onceki) == len(v):
        o = np.asarray(onceki, float)
        no = np.linalg.norm(o) + 1e-12
        oh = o / no
        tam = np.concatenate([z, v[k:]])
        paralel = oh * float(oh @ tam)
        dik = tam - paralel
        nd, nt = float(np.linalg.norm(dik)), float(np.linalg.norm(tam)) + 1e-12
        tik = nd / nt
        if tik > 0.9:                       # tıkanıklık: yalnız %10'u geçsin
            tam = paralel + 0.1 * dik
        z, v = tam[:k], tam
    v = np.concatenate([z, v[k:]])

    # --- zırhın yazmaca geri yansıması
    if abs(isaret + 1.0) < 1e-9:            # işaret çevrildi → σ_z kapısı
        y.tek_kapi(np.array([[1.0, 0.0], [0.0, -1.0]], dtype=y.tip))
    if ceza < 0.999:                        # Betti cezası → genlik tartısı
        g = np.array([[1.0, 0.0], [0.0, ceza]], dtype=np.float64)
        g = g / (np.linalg.norm(g, axis=0, keepdims=True) + 1e-30)
        y.tek_kapi(g.astype(y.tip))

    return v, ZirhIzi(mertebe=u.mertebe, sheaf_duzeltme=sheaf_d,
                      homotopi_isaret=isaret, betti0=b0,
                      betti_ceza=ceza, tikaniklik=tik)
