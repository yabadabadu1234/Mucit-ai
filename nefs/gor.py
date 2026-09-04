"""GÖRMEK -- dış âlemden tek nesne.

Nazırlık katının birinci fiili (kütük H227). **Bu dosyada tek satır
yeni riyaziye yoktur** ve olmamalıdır; nazırlık hesap yapmaz, alt kata
bakar ve gördüğüne bir **isim** verir. İçinde tek yeni formül olan
nazırlık, nazırlık değil çiptir.

Vazifesi şudur: `main` artık *"müşahede et, sonra kalıbı kestir, sonra
şahitleri ayır, sonra kaideyi çöz, sonra genliğe göm"* diye beş kapı
çağırmaz -- **bir kere `gor` der**.

    manzara = gor(gorev)

``Manzara`` bir görevden **görülebilen her şeyi** taşır ve ondan
sonrasına (``dusun``) tek nesne olarak geçer.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from .musahede import Gorev, ayir, bak, genlige_gom, kaide, kalip

__all__ = ["Manzara", "gor"]


@dataclass
class Manzara:
    """Bir görevde **görülen** her şey -- tek nesnede.

    Alanlar ham veri değil **hüküm**dür: ne görüldüğü değil, görülenden
    ne çıkarıldığı. Ham ızgara ``girdi``de durur; gerisi idraktir.
    """

    ad: str = ""
    girdi: Optional[np.ndarray] = None      # ham ızgara
    duyu: Any = None                        # ``bak``ın on beş kanalı
    kalip: Optional[Tuple[int, int]] = None  # çıktı kaç satır kaç sütun
    kalip_kaidesi: str = "sükût"            # o kalıbı hangi kaide verdi
    sahitler: Optional[List[Any]] = None    # otonom bölütleme
    kulli_kaide: Optional[np.ndarray] = None  # şahitlerin ortak kaidesi
    genlik: Optional[np.ndarray] = None     # QTT gömmesi
    sukut: bool = False                     # kalıp bulunamadıysa doğru

    def __repr__(self) -> str:              # pragma: no cover
        return ("Manzara(%r, kalıp=%s [%s], şahit=%d, sükût=%s)"
                % (self.ad, self.kalip, self.kalip_kaidesi,
                   len(self.sahitler or []), self.sukut))


def gor(gorev: Optional[Gorev] = None, izgara=None,
        ne: str = "manzara", gom: bool = False) -> Any:
    """GÖRMEK -- görevden ``Manzara``.

    Beş kapıyı sırayla çağırır ve neticeyi tek nesnede toplar:

    1. ``bak``    -- on beş kanallı mübser duyu (ışık, levn, mekân,
                     bağlantı, doku, nesneler, bu'd, süreklilik,
                     tenâsüb, emsâl, şeffâfiyet, aykırılık…).
    2. ``kalip``  -- çıktı kaç satır kaç sütun olacak. Evvelâ kesirli
                     kaide, sonra cetvel, ikisi de tutmazsa **sükût**.
    3. ``ayir``   -- şahitleri otonom bölütle (ayıraç aramadan,
                     medyan + 3·MAD kopmalarından).
    4. ``kaide``  -- şahitlerin ortak kaidesi (Procrustes).
    5. ``gom``    -- ``gom=True`` ise ızgarayı QTT genliğine göm.

    ==============  ==================================================
    ``ne``          döndürdüğü
    ==============  ==================================================
    ``manzara``     ``Manzara`` -- hepsi
    ``duyu``        yalnız ``bak``ın neticesi (ucuz)
    ``kalıp``       yalnız ``(boyut, kaide_adı)``
    ==============  ==================================================

    **Sükût buradan başlar.** Kalıp bulunamazsa ``Manzara.sukut``
    doğrudur ve ``soyle`` onu görüp susar. Uydurma bir boyut vermek,
    bilmediğini söylememekten kötüdür (H10).
    """
    if izgara is None and gorev is not None:
        izgara = np.asarray(gorev.sinama[0][0] if gorev.sinama
                            else gorev.egitim[0][0])
    if izgara is None:
        raise ValueError("görmek için bir ızgara yahut görev lâzım")
    izgara = np.asarray(izgara)

    duyu = bak(izgara)
    if ne == "duyu":
        return duyu

    boyut, kaide_adi = (None, "sükût")
    if gorev is not None:
        boyut, kaide_adi = kalip(gorev.egitim, izgara)
    if ne == "kalıp":
        return boyut, kaide_adi

    sahitler = None
    kulli = None
    try:
        b = ayir(izgara, ne="bölütle")
        # ``Bolutleme`` bir kayıttır, dizi değil: şahitler onun içindedir.
        sahitler = list(getattr(b, "sahitler", None) or [])
        if sahitler:
            kulli = kaide(sahitler=sahitler, ne="küllî")
    except Exception:                       # pragma: no cover
        sahitler = None                     # şahit çıkmadıysa manzara eksik değil

    genlik = None
    if gom:
        genlik = genlige_gom(izgara.astype(float).reshape(-1))[0]

    if ne != "manzara":
        raise ValueError("görüş kipi bilinmiyor: %r" % (ne,))
    return Manzara(
        ad=(gorev.ad if gorev is not None else ""),
        girdi=izgara, duyu=duyu,
        kalip=(tuple(boyut) if boyut is not None else None),
        kalip_kaidesi=str(kaide_adi),
        sahitler=sahitler or None,
        kulli_kaide=kulli, genlik=genlik,
        sukut=(boyut is None),
    )
