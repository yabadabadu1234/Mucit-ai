"""
Donanım katmanı: **tek kod, iki koşu** -- CPU'da numpy, GPU'da torch.

Neden böyle. Kullanıcı şunu açıkça söyledi: *"Sen GPU tarafındaki
çalışırlığı garanti edemezsin ama en azından CPU'da eğitimin çok kısa
hâli çalışabilmeli."* Bu doğru bir şarttır ve mimarîyi belirler:

* Bütün riyazî çekirdek **numpy** ile yazılır; hiçbir yerde torch
  mecburiyeti yoktur. Torch yoksa her şey aynen koşar, yalnız yavaş.
* Torch **varsa** sıcak döngüler (toplu genlik hesabı, faz orağı,
  örnekleme) cihazlara **parçalanarak** dağıtılır. Bu bir hızlandırmadır,
  bir bağımlılık değil.

**Paralellik nasıl.** Kaggle'ın 4 GPU'su birbirinden bağımsız cihazdır.
Burada model çoğaltılmaz (`DataParallel` değil); **iş** parçalanır:
``N`` örneklik bir yığın 4 parçaya bölünür, her parça kendi cihazında
hesaplanır, netice birleştirilir. Sebebi: bizim ağır işimiz gradyan
değil **örnekleme ve genlik hesabıdır**; bu iş tabiatı gereği
utanmadan paraleldir (embarrassingly parallel) ve cihazlar arası
haberleşme gerektirmez. Gradyan olmadığı için `all_reduce` de yoktur --
kütük H3'ün doğrudan neticesidir.

**Ne iddia edilmiyor.** Bu dosya GPU'da koştuğunu iddia etmez; burada
GPU yoktur ve ölçülememiştir. İddia edilen şudur: torch yoksa numpy
yoluna düşer ve **ölçülmüştür**; torch varsa aynı arayüz cihazlara
dağıtır ve o yol ancak Kaggle'da ölçülebilir. `rapor()` hangi yolda
olduğunu açıkça yazar.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Callable, List, Optional, Tuple

import numpy as np

__all__ = ["Donanim", "donanim", "parcala", "topla_paralel", "rapor"]


def _torch():
    try:
        import torch                                    # noqa: F401
        return torch
    except Exception:
        return None


@dataclass
class Donanim:
    """Eldeki hesap gücünün **ölçülmüş** tarifi -- tahmin değil."""
    torch_var: bool
    cihazlar: Tuple[str, ...]
    vram_gb: Tuple[float, float, ...]
    cekirdek: int
    zorla_cpu: bool

    @property
    def gpu(self) -> int:
        return sum(1 for c in self.cihazlar if c != "cpu")

    @property
    def toplam_vram(self) -> float:
        return float(sum(self.vram_gb))


def donanim(zorla_cpu: Optional[bool] = None) -> Donanim:
    """Eldeki cihazları **yokla**. Ortam değişkeni ``MUCIT_CPU=1`` zorlar."""
    if zorla_cpu is None:
        zorla_cpu = os.environ.get("MUCIT_CPU", "") == "1"
    T = None if zorla_cpu else _torch()
    if T is None or not T.cuda.is_available():
        return Donanim(T is not None, ("cpu",), (0.0,),
                       os.cpu_count() or 1, bool(zorla_cpu))
    n = T.cuda.device_count()
    cih = tuple("cuda:%d" % i for i in range(n))
    vram = tuple(float(T.cuda.get_device_properties(i).total_memory)
                 / 2 ** 30 for i in range(n))
    return Donanim(True, cih, vram, os.cpu_count() or 1, False)


# =====================================================================
def parcala(n: int, k: int) -> List[Tuple[int, int]]:
    """``n`` işi ``k`` cihaza **dengeli** böl: artık ilk parçalara dağılır.

    ``n//k`` ile bölüp kalanı sona eklemek son cihaza ``k−1`` fazla iş
    yükler; 4 cihazda %25'e varan dengesizlik demektir. Kalanı tek tek
    dağıtmak farkı en fazla **bir** işe indirir.
    """
    if k <= 1 or n <= 0:
        return [(0, n)]
    taban, artik = divmod(n, k)
    sinir, bas = [], 0
    for i in range(k):
        son = bas + taban + (1 if i < artik else 0)
        if son > bas:
            sinir.append((bas, son))
        bas = son
    return sinir


def topla_paralel(f: Callable[[np.ndarray, str], np.ndarray],
                  X: np.ndarray, dh: Optional[Donanim] = None
                  ) -> np.ndarray:
    """``X`` yığınını cihazlara böl, ``f(parça, cihaz)`` koş, birleştir.

    Tek cihazda (CPU) bu, ``f(X, "cpu")``dan başka bir şey değildir --
    yani paralellik **hiçbir davranış farkı** doğurmaz, yalnız hızı
    değiştirir. Sınanabilirliğin şartı budur: aynı tohumla aynı netice.
    """
    dh = dh or donanim()
    if len(dh.cihazlar) <= 1:
        return f(X, dh.cihazlar[0])
    parcalar = parcala(len(X), len(dh.cihazlar))
    cikti = [f(X[a:b], dh.cihazlar[i]) for i, (a, b) in enumerate(parcalar)]
    return np.concatenate(cikti, axis=0)


# =====================================================================
def rapor(dh: Optional[Donanim] = None) -> str:
    dh = dh or donanim()
    s = ["donanım: torch=%s  cihaz=%s  çekirdek=%d"
         % (dh.torch_var, ", ".join(dh.cihazlar), dh.cekirdek)]
    if dh.gpu:
        s.append("  VRAM: %s  (toplam %.1f GB)"
                 % (", ".join("%.1f" % v for v in dh.vram_gb),
                    dh.toplam_vram))
        s.append("  yol: TORCH/CUDA -- yığın %d cihaza parçalanacak" % dh.gpu)
    else:
        s.append("  yol: NUMPY/CPU -- ölçülen yol budur; GPU yolu burada")
        s.append("       koşmadı ve koştuğu İDDİA EDİLMİYOR.")
    return "\n".join(s)


if __name__ == "__main__":   # pragma: no cover
    print(rapor())
