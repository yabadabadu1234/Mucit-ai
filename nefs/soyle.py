"""SÖYLEMEK -- ya ispat, ya sükût.

Nazırlık katının altıncı ve son fiili (kütük H227). **Yeni riyaziye
yoktur.**

    cevap = soyle(gorev)

Bu nazırlığın öteki beşten farkı şudur: ötekiler bir şey **üretir**,
bu bir şey **esirger**. Modelin susabilmesi, konuşabilmesi kadar
mühimdir; uydurma bir cevap, bilmediğini söylememekten kötüdür (H10).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import numpy as np

from idrak.cozucu import gorev_coz
from .gor import Manzara, gor
from .musahede import ortu

__all__ = ["Cevap", "soyle"]


@dataclass
class Cevap:
    """SÖYLENEN -- yahut susulan.

    ``sukut`` doğruysa ``izgara`` boştur ve ``sebep`` niçin
    susulduğunu söyler. Sükût bir başarısızlık değil bir **hüküm**dür.
    """

    gorev: str = ""
    sukut: bool = True
    sebep: str = ""
    kural: Optional[str] = None
    izgara: Optional[List[np.ndarray]] = None
    aday_sayisi: int = 0
    tikaniklik: Optional[float] = None

    def __repr__(self) -> str:               # pragma: no cover
        return ("Cevap(%r, %s)" % (self.gorev, "SÜKÛT: " + self.sebep
                                   if self.sukut else "kural=" + str(self.kural)))


def soyle(gorev=None, manzara=None, tikaniklik_bak: bool = False,
          ne: str = "cevap") -> Any:
    """SÖYLEMEK -- görevden ``Cevap``, yahut sükût.

    Üç kapıyı sırayla geçer ve **her biri susturabilir**:

    1. ``gor``       -- kalıp bulunamadıysa (``Manzara.sukut``) daha
                        çözücüye gidilmez; çıktının kaç satır kaç sütun
                        olacağını bilmeden cevap verilmez.
    2. ``gorev_coz`` -- aday dönüşümler **gösterim çiftlerinde**
                        doğrulanır; sınama çıktısı hiç görülmez. Tutan
                        aday yoksa sükût.
    3. ``ortu``      -- ``tikaniklik_bak=True`` ise Čech tıkanıklığı
                        okunur: yamalar yapışmıyorsa küllî bir kaide
                        yok demektir ve model susmaya meyleder.

    **Sınama çıktısıyla kıyaslamak değerlendirmedir, çözümün parçası
    değildir.** Çözücü sınama cevabını görmez; gördüğü an ölçüm
    yalan olur.

    ==============  ==================================================
    ``ne``          döndürdüğü
    ==============  ==================================================
    ``cevap``       ``Cevap`` -- söylenen yahut sükût
    ``sukut_mu``    yalnız ``bool`` (ucuz)
    ==============  ==================================================
    """
    if gorev is None:
        raise ValueError("söylemek için bir görev lâzım")
    if manzara is None:
        manzara = gor(gorev)

    if manzara.sukut:
        c = Cevap(gorev=gorev.ad, sukut=True,
                  sebep="kalıp bilinmiyor -- çıktının ebadı kestirilemedi")
        return c.sukut if ne == "sukut_mu" else c

    d = gorev_coz(gorev)
    tik = None
    if tikaniklik_bak:
        try:
            tik = float(ortu(gorev, ne="tıkanıklık")["H1"])
        except Exception:                    # pragma: no cover
            tik = None

    if not d.get("cevap_verildi"):
        c = Cevap(gorev=gorev.ad, sukut=True,
                  sebep="hiçbir aday gösterim çiftlerinin hepsinde tutmadı",
                  aday_sayisi=int(d.get("aday_sayısı", 0)), tikaniklik=tik)
    else:
        c = Cevap(gorev=gorev.ad, sukut=False, sebep="",
                  kural=str(d.get("kural")),
                  izgara=list(d.get("tahmin") or []),
                  aday_sayisi=int(d.get("aday_sayısı", 0)), tikaniklik=tik)

    if ne == "sukut_mu":
        return c.sukut
    if ne != "cevap":
        raise ValueError("söyleme kipi bilinmiyor: %r" % (ne,))
    return c
