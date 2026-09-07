from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np

from .kulli_kayip import ezber_mi, sozunde_mi, zayif_halka

__all__ = ["Mizan", "tart"]


@dataclass
class Mizan:

    kayip: float = 0.0
    halka: Optional[int] = None
    ihlal: List[Dict[str, Any]] = field(default_factory=list)
    ezber: Optional[Dict[str, Any]] = None
    sozunde: bool = True
    dokum: Dict[str, float] = field(default_factory=dict)

    def __repr__(self) -> str:
        return ("Mizan(kayıp=%.6g, zayıf_halka=%s, ihlâl=%d, sözünde=%s)"
                % (self.kayip, self.halka, len(self.ihlal), self.sozunde))


def tart(hal=None, olcumler=None, beta: float = 8.0,
         sozlesme: bool = True, ezber: bool = False,
         n_satir: int = 3, chi: int = 16, ne: str = "mizan") -> Any:
    if olcumler is None and hal is not None:
        iz = getattr(hal, "zirh_izi", None)
        olcumler = [float(getattr(iz, a, 0.0) or 0.0)
                    for a in ("sheaf_duzeltme", "betti_ceza",
                              "koho_ceza", "homotopi_sapma")] if iz else [0.0]
    olcumler = [float(x) for x in (olcumler or [0.0])]

    kayip = float(zayif_halka(olcumler, beta=beta, ne="asgarî"))
    if ne == "kayıp":
        return kayip
    halka = int(np.argmin(olcumler)) if olcumler else None

    ihlal: List[Dict[str, Any]] = []
    if sozlesme:
        try:
            for r in sozunde_mi(n_satir=n_satir, chi=chi, ne="hepsi"):
                if r.get("ihlâl") or r.get("kullanılmayan"):
                    ihlal.append(r)
        except Exception:
            pass

    ez = ezber_mi(ne="kıyas") if ezber else None

    if ne != "mizan":
        raise ValueError("tartı kipi bilinmiyor: %r" % (ne,))
    return Mizan(kayip=kayip, halka=halka, ihlal=ihlal, ezber=ez,
                 sozunde=not ihlal,
                 dokum={"ölçü_%d" % i: v for i, v in enumerate(olcumler)})
