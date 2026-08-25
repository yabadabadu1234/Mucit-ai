"""idrak — külliyatın mimarisinin fiilî hâli: ARC-AGI-2 üzerinde çalışan model.

Bu paket, risalelerdeki parçaların **birbirine bağlandığı** yerdir:

* ``arc``     — ARC-AGI-2 verisi, belirteçleme, resmî bölme (900/100/120)
* ``kubit``   — reel dik kapılarla ``n`` kübitlik öğrenilebilir yazmaç
* ``model``   — Hartley süzgeci (M29 şartıyla) + KAN kenarı + Cayley dik
  karışım + kübit yazmacı + nedensel çözücü
* ``egitim``  — CPU'da arka planda koşabilen eğitim; ölçüt **tam ızgara
  eşleşmesi**

Varsayılan boyut ``D = 512``; hızlı deneme boyutu ``D = 128``.
"""

__all__ = ["arc", "kubit", "model", "egitim"]
