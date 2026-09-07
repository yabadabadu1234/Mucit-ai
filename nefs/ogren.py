from __future__ import annotations

from typing import Any, Callable, Dict, Optional

import numpy as np

from ogrenme.optimize import OptimizeAyari, had, hoca_egit, yokus

__all__ = ["ogren"]


def ogren(kayip: Optional[Callable] = None, p0=None, ayar=None,
          tur: int = 3, tunel: bool = False, ne: str = "egit",
          **kw) -> Any:
    if ne == "yokuş":
        return yokus(**kw)
    if ne == "had":
        return had(**kw)
    if ne != "egit":
        raise ValueError("öğrenme kipi bilinmiyor: %r" % (ne,))

    if kayip is None or p0 is None:
        raise ValueError("öğrenmek için kayıp ve başlangıç lâzım")
    if ayar is None:
        ayar = OptimizeAyari(tur=int(tur), tunel_acik=bool(tunel), **kw)
    return hoca_egit(kayip, np.asarray(p0, float), ayar)
