"""SÖYLEMEK -- ya motorun ürettiği, ya sükût.

Nazırlık katının altıncı ve son fiili. **Yeni riyaziye yoktur.**

    cevap = soyle(gorev, nefs=motor)

===================================================================
PADİŞAHIN FERMANI: ARC'Yİ MOTOR ÇÖZER, BAŞKA HİÇBİR ŞEY DEĞİL
===================================================================

Bu dosya evvelce ``idrak/cozucu.py``yi çağırıyordu: elle yazılmış ARC
kâideleri (yerçekimi, bakışım onarımı, delik rengi, döşeme, kırpma,
renk eşlemesi). O dosya tasfiye edildi ve sebebi tektir:

    Çözen motor değildi. Çözen, o dosyaya elle yazılmış tahminlerdi.
    Motor kenarda duruyor, cevabı kâide cebri veriyor, netice ise
    "model ARC'yi çözdü" diye okunuyordu. Bu bir gösteriştir.

Kütük H133'te bunun tersi bir hüküm vardı: dil modeli yolu kapatılmış,
"padişah tam da olmamaya yemin ettiği şeyi yapıyordu: bir dil modeli"
denmişti. **O hüküm iptal edildi.** Bu proje bir dil modeli projesidir;
ARC de dil modeliyle çözülecektir. H133'ün cebri (``0,95¹⁰⁰ ≈ 0,006``)
yanlış değildi -- fakat o, motoru terk etmenin değil, motoru
**büyütmenin** gerekçesidir: 8 belirteçlik pencere ve 16 sembollük
sözlük bir kusurdur, dil modeli olmak kusur değildir.

O hâlde söylemek şudur: bağlamı kur, motoru koştur, belirteç belirteç
üret. Sükût yine mümkündür ve yine bir hükümdür (H10) -- fakat artık
sükûtu da motor verir (``adayin_tuttugu``un ``sukut`` alanı), elle
yazılmış bir şart değil.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import numpy as np

from .gor import Manzara, gor
from .musahede import gorev_dizisi, ortu

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
    belirtec: Optional[List[int]] = None
    guven: float = 0.0


def soyle(gorev=None, manzara=None, tikaniklik_bak: bool = False,
          nefs=None, pencere: int = 8, sozluk: int = 16,
          azami_uret: int = 0, sukut_esigi: float = 0.8,
          ne: str = "cevap") -> Any:
    """SÖYLEMEK -- görevden ``Cevap``, yahut sükût. **Motorla.**

    İki kapı vardır ve her biri susturabilir:

    1. ``gor`` -- kalıp bulunamadıysa (``Manzara.sukut``) çıktının kaç
       satır kaç sütun olacağı bilinmiyor demektir; üretime girilmez.
    2. ``adayin_tuttugu`` -- motorun kendi **sükût** alanı eşiği
       aşarsa model bilmediğini söyler. Bu bir şart değil bir ölçümdür.

    ``nefs`` verilmezse motor yoktur ve **sükût edilir**. Motorsuz
    cevap vermek, tasfiye edilen kâide cebrine geri dönmek olurdu.

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

    def _bitir(c: "Cevap"):
        if ne == "sukut_mu":
            return c.sukut
        if ne != "cevap":
            raise ValueError("söyleme kipi bilinmiyor: %r" % (ne,))
        return c

    if manzara.sukut:
        return _bitir(Cevap(
            gorev=gorev.ad, sukut=True,
            sebep="kalıp bilinmiyor -- çıktının ebadı kestirilemedi"))

    if nefs is None:
        return _bitir(Cevap(
            gorev=gorev.ad, sukut=True,
            sebep="motor verilmedi -- kâide cebriyle cevap vermek yasak"))

    tik = None
    if tikaniklik_bak:
        try:
            tik = float(ortu(gorev, ne="tıkanıklık")["H1"])
        except Exception:                    # pragma: no cover
            tik = None

    from .qegitim import adayin_tuttugu
    try:
        dizi, hedef = gorev_dizisi(gorev, hedef_indis=0)
    except Exception as exc:                 # pragma: no cover
        return _bitir(Cevap(gorev=gorev.ad, sukut=True, tikaniklik=tik,
                            sebep="bağlam kurulamadı: %s"
                                  % type(exc).__name__))

    h = [int(x) % int(sozluk) for x in hedef]
    if 0 < int(azami_uret) < len(h):
        return _bitir(Cevap(gorev=gorev.ad, sukut=True, tikaniklik=tik,
                            sebep="hedef hadde sığmıyor (%d belirteç)"
                                  % len(h)))

    baglam = [int(x) % int(sozluk) for x in dizi]
    uretilen: List[int] = []
    sukutlar: List[float] = []
    guvenler: List[float] = []
    for _ in range(len(h)):
        pen = (baglam[-pencere:] if len(baglam) >= pencere
               else [0] * (pencere - len(baglam)) + baglam)
        P, o = adayin_tuttugu(nefs, (), sozluk=int(sozluk), ne="koş",
                              baglam=pen)
        P = np.asarray(P, float).reshape(-1)
        sukutlar.append(float(o.get("sukut", 0.0)))
        guvenler.append(float(P.max()) if P.size else 0.0)
        t = int(np.argmax(P))
        uretilen.append(t)
        baglam.append(t)

    # **SÜKÛTU MOTOR VERİR.** Ortalama sükût alanı eşiği aşarsa model
    # bilmediğini söylüyor demektir ve söylenmez. Eşik ayarlanabilir
    # ve kapatılabilir (H90); elle yazılmış bir kâide değildir.
    ort_sukut = float(np.mean(sukutlar)) if sukutlar else 1.0
    if ort_sukut > float(sukut_esigi):
        return _bitir(Cevap(
            gorev=gorev.ad, sukut=True, tikaniklik=tik,
            belirtec=uretilen, guven=float(np.mean(guvenler or [0.0])),
            sebep="motorun sükût alanı %.3f > %.3f"
                  % (ort_sukut, float(sukut_esigi))))

    return _bitir(Cevap(
        gorev=gorev.ad, sukut=False, sebep="",
        kural="motor (belirteç üretimi)",
        izgara=[np.asarray(uretilen, int)],
        belirtec=uretilen,
        guven=float(np.mean(guvenler or [0.0])),
        aday_sayisi=0, tikaniklik=tik))
