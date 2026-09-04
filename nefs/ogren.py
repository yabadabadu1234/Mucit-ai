"""ÖĞRENMEK -- mîzâna göre düzelt, ve haddini bil.

Nazırlık katının beşinci fiili (kütük H227). **Yeni riyaziye yoktur**;
hoca ``ogrenme/optimize.py``dedir.

    yeni_p = ogren(kayip, p0)

`main` artık *"optimize ayarını kur, hocayı çağır, tüneli aç, yokuşu
ölç"* demez -- **bir kere `ogren` der**.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, Optional

import numpy as np

from ogrenme.optimize import OptimizeAyari, had, hoca_egit, yokus

__all__ = ["ogren"]


def ogren(kayip: Optional[Callable] = None, p0=None, ayar=None,
          tur: int = 3, tunel: bool = False, ne: str = "egit",
          **kw) -> Any:
    """ÖĞRENMEK -- kayba göre parametreyi düzelt.

    ==============  ==================================================
    ``ne``          ne yapar
    ==============  ==================================================
    ``egit``        hocayı çağır: gradyansız, deterministik tâlim.
                    Döner ``{"p", "kayıp", "günlük", …}``
    ``yokuş``       hangi yön ne kadar pahalı -- Fisher/Fubini--Study
                    metriği. Tâlimden **evvel** bakılır: bedava
                    görünen yön bedava değildir.
    ``had``         hocanın haddi: NFL üstten, Nesterov alttan.
                    Ölçülen ilerleme haddi kırıyorsa iddia yanlış
                    kurulmuştur, usul hızlı değildir.
    ==============  ==================================================

    **``tunel=True`` bedava değildir.** Tünel kapısı yerel asgarîden
    çıkarır, fakat her sıçrama kayıp çağrısı harcar ve çıkılan yer
    daha kötü olabilir; karar **her zaman gerçek kayıpla** verilir,
    vekil modelle değil. ``ara(ne="bedel")`` kaç deneme edeceğini
    evvelden söyler.

    **Haddini bilmek öğrenmenin parçasıdır.** ``had`` ile ölçülen alt
    sınırın altına inen bir ilerleme rapor edilirse, sevinilmez --
    ölçüm yanlış kurulmuştur diye bakılır. Bu tuzağa bu proje bizzat
    düştü ve ölçüm düzeltti (kütük H227).
    """
    if ne == "yokuş":
        return yokus(**kw)
    if ne == "had":
        return had(**kw)
    if ne != "egit":
        raise ValueError("öğrenme kipi bilinmiyor: %r" % (ne,))

    if kayip is None or p0 is None:
        raise ValueError("öğrenmek için kayıp ve başlangıç lâzım")
    if ayar is None:
        ayar = OptimizeAyari(tur=int(tur), tunel_acik=bool(tunel))
    return hoca_egit(kayip, np.asarray(p0, float), ayar)
