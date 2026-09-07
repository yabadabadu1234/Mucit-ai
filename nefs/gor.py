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

from .musahede import Gorev, ayir, bak, genlige_gom, kaide

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
    # **KALIP KESTİRİMİ İMHA EDİLDİ (ferman 1-P).**
    #
    #     "Bana satır sütun tahmini için ayrı bir mimarinin koştuğunu
    #     söyledin, sil dedim... artık tek bir model var, satır sütun
    #     diye bir şey yok, elimizde sadece bir llm var!!!"
    #
    # Burada ``kalip`` (çıktı kaç satır kaç sütun) ve
    # ``kalip_kaidesi`` duruyordu; ``sukut`` da onlardan doğuyordu.
    # Yâni model konuşmadan evvel **ayrı bir mimari** ızgaranın
    # ebadını kestiriyor, kestiremeyince model susturuluyordu.
    # Ölçüldü ve neticesi buydu: *"kalıp bilinmiyor -- çıktının ebadı
    # kestirilemedi"* iki görevin birinde sükût sebebiydi.
    #
    # Ebat da modelin yazdığı metinden çıkar: model ızgarayı yazar,
    # ``metin_izgara`` okur, okunamazsa **yanlış cevap** sayılır.
    sahitler: Optional[List[Any]] = None    # otonom bölütleme
    kulli_kaide: Optional[np.ndarray] = None  # şahitlerin ortak kaidesi
    genlik: Optional[np.ndarray] = None     # QTT gömmesi
    sukut: bool = False                     # kalıp bulunamadıysa doğru

    def __repr__(self) -> str:              # pragma: no cover
        return ("Manzara(%r, şahit=%d, sükût=%s)"
                % (self.ad, len(self.sahitler or []), self.sukut))


def gor(gorev: Optional[Gorev] = None, izgara=None,
        ne: str = "manzara", gom: bool = False) -> Any:
    """GÖRMEK -- görevden ``Manzara``.

    Beş kapıyı sırayla çağırır ve neticeyi tek nesnede toplar:

    1. ``bak``    -- on beş kanallı mübser duyu (ışık, levn, mekân,
                     bağlantı, doku, nesneler, bu'd, süreklilik,
                     tenâsüb, emsâl, şeffâfiyet, aykırılık…).
    2. (kalıp kestirimi **İMHA EDİLDİ** -- ferman 1-P)
    3. ``ayir``   -- şahitleri otonom bölütle (ayıraç aramadan,
                     medyan + 3·MAD kopmalarından).
    4. ``kaide``  -- şahitlerin ortak kaidesi (Procrustes).
    5. ``gom``    -- ``gom=True`` ise ızgarayı QTT genliğine göm.

    ==============  ==================================================
    ``ne``          döndürdüğü
    ==============  ==================================================
    ``manzara``     ``Manzara`` -- hepsi
    ``duyu``        yalnız ``bak``ın neticesi (ucuz)
    ==============  ==================================================

    **SÜKÛT ARTIK BURADAN BAŞLAMAZ** (ferman 1-P): ebat kestirimi
    imha edildi. Susma hükmü ``nefs/suphe.py``nin teâruz ölçüsünden
    gelir -- yâni modelin kendi hükmünden, ayrı bir mimariden değil.
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

    if ne == "kalıp":
        raise ValueError(
            "``gor(ne='kalıp')`` İMHA EDİLDİ (ferman 1-P): ızgaranın "
            "ebadını kestiren ayrı bir mimari yoktur. Ebat modelin "
            "yazdığı metinden çıkar.")

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
        sahitler=sahitler or None,
        kulli_kaide=kulli, genlik=genlik,
        # **SÜKÛT ARTIK KALIPTAN DOĞMAZ** (ferman 1-P). Manzara
        # görmenin neticesidir; susup susmamaya ``nefs/suphe.py``
        # karar verir (teâruz ölçüsü). Ebadı kestiremediği için
        # susan bir model, hiç konuşmayan bir modeldir.
        sukut=False,
    )
