from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import numpy as np

from .gor import Manzara
from .melekeler import QAKIS, QNefs, qsicil
from .zirh import vicdan, zirhla

__all__ = ["Hal", "dusun"]


@dataclass
class Hal:

    manzara: Optional[Manzara] = None
    yazmac: Any = None
    p: Optional[np.ndarray] = None
    gecilen: tuple = ()
    zirh_izi: Any = None
    yasak: Optional[Dict[str, Any]] = None
    mertebe: int = 0

    def __len__(self) -> int:
        return int(self.p.size) if self.p is not None else 0

    def __repr__(self) -> str:
        return ("Hal(meleke=%d, parametre=%d, mertebe=%d)"
                % (len(self.gecilen), len(self), self.mertebe))


def dusun(manzara=None, nefs=None, ayar=None, tohum: int = 0,
          zirhli: bool = True, ne: str = "hal") -> Any:
    if nefs is None:
        nefs = QNefs(tohum, ayar)
    girdi = None
    if manzara is not None and getattr(manzara, "girdi", None) is not None:
        girdi = np.asarray(manzara.girdi, float)
        if girdi.ndim == 1:
            girdi = girdi.reshape(1, -1)
    if girdi is None:
        girdi = np.zeros((2, 4))

    q = nefs.idrak_et(girdi)
    if ne == "yazmaç":
        return q

    izi = None
    if zirhli:
        from idrak.kategori import Uzay
        try:
            d = np.asarray(q.makam_derece_vektoru(), float).reshape(-1)
            okuma = np.concatenate([d, np.zeros_like(d)])
            u = Uzay(yuva=0, mertebe=len(qsicil()), tam_kuruldu=True,
                     denetlendi=True, baglayici=0, tip_ozeti="düşünme")
            _, izi = zirhla(q, u=u, okuma=okuma)
        except Exception:
            izi = None
    try:
        yasak = vicdan(q=q, ne="yasaklar")
    except Exception:
        yasak = None

    if ne != "hal":
        raise ValueError("düşünme kipi bilinmiyor: %r" % (ne,))
    return Hal(manzara=manzara, yazmac=q, p=nefs.vektor(),
               gecilen=tuple(QAKIS), zirh_izi=izi, yasak=yasak,
               mertebe=len(qsicil()))
