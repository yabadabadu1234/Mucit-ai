from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from .musahede import Gorev, ayir, bak, genlige_gom, kaide

__all__ = ["Manzara", "gor"]


@dataclass
class Manzara:

    ad: str = ""
    girdi: Optional[np.ndarray] = None
    duyu: Any = None
    sahitler: Optional[List[Any]] = None
    kulli_kaide: Optional[np.ndarray] = None
    genlik: Optional[np.ndarray] = None
    sukut: bool = False

    def __repr__(self) -> str:
        return ("Manzara(%r, şahit=%d, sükût=%s)"
                % (self.ad, len(self.sahitler or []), self.sukut))


def gor(gorev: Optional[Gorev] = None, izgara=None,
        ne: str = "manzara", gom: bool = False) -> Any:
    if izgara is None and gorev is not None:
        izgara = np.asarray(gorev.sinama[0][0] if gorev.sinama
                            else gorev.egitim[0][0])
    if izgara is None:
        raise ValueError("görmek için bir ızgara yahut görev lâzım")
    izgara = np.asarray(izgara)

    duyu = bak(izgara)
    if ne == "duyu":
        return duyu

    if ne == "kalıp":
        raise ValueError(
            "``gor(ne='kalıp')`` İMHA EDİLDİ (ferman 1-P): ızgaranın "
            "ebadını kestiren ayrı bir mimari yoktur. Ebat modelin "
            "yazdığı metinden çıkar.")

    sahitler = None
    kulli = None
    try:
        b = ayir(izgara, ne="bölütle")
        sahitler = list(getattr(b, "sahitler", None) or [])
        if sahitler:
            kulli = kaide(sahitler=sahitler, ne="küllî")
    except Exception:
        sahitler = None

    genlik = None
    if gom:
        genlik = genlige_gom(izgara.astype(float).reshape(-1))[0]

    if ne != "manzara":
        raise ValueError("görüş kipi bilinmiyor: %r" % (ne,))
    return Manzara(
        ad=(gorev.ad if gorev is not None else ""),
        girdi=izgara, duyu=duyu,
        sahitler=sahitler or None,
        kulli_kaide=kulli, genlik=genlik,
        sukut=False,
    )
