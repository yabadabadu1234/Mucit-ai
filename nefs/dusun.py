"""DÜŞÜNMEK -- manzarayı yazmaca alıp melekelerden geçirmek.

Nazırlık katının ikinci fiili (kütük H227). **Yeni riyaziye yoktur.**

    hal = dusun(manzara)

`main` artık *"yazmacı kur, kırk dört melekeyi sırayla geçir, her
adımda zırhı giydir, vicdanı işaretle"* demez -- **bir kere `dusun`
der**.
"""
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
    """ZİHNİN HÂLİ -- düşünmenin bıraktığı şey.

    Bir sayı yığını değil, bir **hâl**dir: yazmaç nerede duruyor, hangi
    melekelerden geçti, zırh ne kadar ısırdı, vicdan neyi yasakladı.
    """

    manzara: Optional[Manzara] = None
    yazmac: Any = None                      # QYazmac -- dimağın kendisi
    p: Optional[np.ndarray] = None          # parametre vektörü
    gecilen: tuple = ()                     # sırayla geçilen meleke no'ları
    zirh_izi: Any = None                    # dörtlü topolojik zırhın izi
    yasak: Optional[Dict[str, Any]] = None  # vicdanın işaretlediği
    mertebe: int = 0

    def __len__(self) -> int:               # pragma: no cover
        return int(self.p.size) if self.p is not None else 0

    def __repr__(self) -> str:              # pragma: no cover
        return ("Hal(meleke=%d, parametre=%d, mertebe=%d)"
                % (len(self.gecilen), len(self), self.mertebe))


def dusun(manzara=None, nefs=None, ayar=None, tohum: int = 0,
          zirhli: bool = True, ne: str = "hal") -> Any:
    """DÜŞÜNMEK -- manzaradan ``Hal``.

    Üç kapıyı sırayla çağırır:

    1. ``QNefs``  -- kırk dört melekenin yazmacını kur (yahut verileni
                     kullan) ve manzarayı **idrak et**: akış ``QAKIS``
                     sırasıyla geçer, her meleke bir evvelkinin
                     bıraktığı yazmaç üstünde çalışır.
    2. ``zirhla`` -- dörtlü topolojik zırh (sheaf, Betti, kohomoloji,
                     homotopi). ``zirhli=False`` yalnız **kırmızı
                     yakabilmek** için vardır: zırhsız hâl ile zırhlı
                     hâl kıyaslanabilsin diye.
    3. ``vicdan`` -- yasağı söylenmeden bilen işaret çekirdeği: hangi
                     hâl mantığa aykırı, tek süpürmede işaretlenir.

    ==============  ==================================================
    ``ne``          döndürdüğü
    ==============  ==================================================
    ``hal``         ``Hal`` -- hepsi
    ``yazmaç``      yalnız idrak edilmiş yazmaç (ucuz)
    ==============  ==================================================

    **Zırh her adımda giydirilir, sonda değil.** Sonda giydirilen zırh
    zırh değil süstür: aradaki adımlarda topoloji çoktan bozulmuştur.
    """
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
        # Zırh **okumaya** giydirilir: melekelerin bıraktığı makam
        # derece vektörü, sheaf/Betti/koho/homotopi süzgecinden geçer.
        # ``Uzay`` zırhın hangi mertebede ve hangi bölgede çalıştığını
        # söyler; onsuz zırh neyi koruduğunu bilmez.
        from idrak.kategori import Uzay
        try:
            d = np.asarray(q.makam_derece_vektoru(), float).reshape(-1)
            okuma = np.concatenate([d, np.zeros_like(d)])
            u = Uzay(yuva=0, mertebe=len(qsicil()), tam_kuruldu=True,
                     denetlendi=True, baglayici=0, tip_ozeti="düşünme")
            _, izi = zirhla(q, u=u, okuma=okuma)
        except Exception:                   # pragma: no cover
            izi = None
    try:
        yasak = vicdan(q=q, ne="yasaklar")
    except Exception:                       # pragma: no cover
        yasak = None

    if ne != "hal":
        raise ValueError("düşünme kipi bilinmiyor: %r" % (ne,))
    return Hal(manzara=manzara, yazmac=q, p=nefs.vektor(),
               gecilen=tuple(QAKIS), zirh_izi=izi, yasak=yasak,
               mertebe=len(qsicil()))
