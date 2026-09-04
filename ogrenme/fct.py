"""
FCT -- GAUSS-CHEBYSHEV-LOBATTO KAPALI FORM (Bab V, 5. madde)

Padişahın tanzim fermanı bu uzvu ``ogrenme/fct.py`` diye adlandırdı.
Burada **yeni bir riyaziyat kurulmuyor**: `kuantum/ceride.py`de ölçülmüş
ve mühürlenmiş FCT motoru bu ad altında dışa verilir. Tekrar yazmak,
ölçülmüş bir şeyi ölçülmemiş bir kopyayla değiştirmek olurdu.

Ölçülmüş hüküm (kütük): GCL düğümlerinde ``XᵀX = I`` **tam** sağlanır ve
şart sayısı ``κ = 1,000000`` çıkar. Eşaralıklı düğüm ise kırmızıdır --
``esaralikli_tasarim`` onu göstermek için durur.
"""
from __future__ import annotations

from typing import Tuple

import numpy as np

from kuantum.ceride import chebyshev_tasarimi

__all__ = ["gauss_chebyshev_lobatto_dugumleri", "hizli_chebyshev_donusumu",
           "chebyshev_degerlendir", "chebyshev_tasarimi",
           "kappa_olc"]


def gauss_chebyshev_lobatto_dugumleri(M: int) -> np.ndarray:
    """``M`` adet GCL düğümü: ``x_k = cos(kπ/(M−1))``."""
    return chebyshev_tasarimi(int(M), "düğüm")


def hizli_chebyshev_donusumu(f: np.ndarray, M: int = 0) -> np.ndarray:
    """Düğümlerdeki değerlerden Chebyshev katsayıları -- kapalı form.

    ``M`` verilmezse dizinin boyundan okunur. Gradyan inişi yoktur:
    tasarım matrisi diküldür, katsayı tek çarpımla çıkar.

    **Bir kayma düzeltildi:** ``M`` derecedir ve GCL düğümü sayısı
    ``M+1``dir. ``M = f.size`` yazılmıştı; motor haklı olarak
    ``M+1 = 130`` düğüm istedi, elde 129 vardı. Derece artık
    ``f.size − 1``dir.
    """
    f = np.asarray(f, float).reshape(-1)
    return chebyshev_tasarimi(int(M) if M else int(f.size) - 1,
                              "katsayı", f=f)


def chebyshev_degerlendir(a: np.ndarray, x: np.ndarray,
                          M: int = 0) -> np.ndarray:
    """Katsayılardan değer -- ``hizli_chebyshev_donusumu``un tersi."""
    a = np.asarray(a, float).reshape(-1)
    return chebyshev_tasarimi(int(M) if M else int(a.size), "değer",
                              a=a, x=np.asarray(x, float))


def kappa_olc(M: int = 64) -> Tuple[float, float]:
    """``κ`` ölçüsü -- **kırmızı yanabildiği** için ölçüdür (H90).

    GCL düğümü ile eşaralıklı düğümün şart sayıları yan yana döner.
    Birincisi 1'e oturmalı, ikincisi patlamalıdır; ikisi de yeşil
    çıkarsa ölçü bozuktur.
    """
    X, _w, _n = chebyshev_tasarimi(int(M), "tasarım")
    kappa_gcl = float(np.linalg.cond(X))
    Xe = chebyshev_tasarimi(int(M), "eşaralıklı")
    kappa_esit = float(np.linalg.cond(Xe))
    return kappa_gcl, kappa_esit


def rapor() -> str:                                      # pragma: no cover
    kg, ke = kappa_olc(64)
    return ("FCT -- GCL kapalı form\n"
            "  κ(GCL)        = %.6f   (1'e oturmalı)\n"
            "  κ(eşaralıklı) = %.3e   (kırmızı kontrol)" % (kg, ke))


if __name__ == "__main__":                               # pragma: no cover
    print(rapor())
