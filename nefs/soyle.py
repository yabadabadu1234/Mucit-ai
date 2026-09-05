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


def _sec(gorev, d) -> tuple:
    """Tutan adaylar arasından **arayarak** seç -- ``tutan[0]`` değil.

    Kütük H230'un açıkça yazdığı borç buydu: *"birden çok aday
    tutuyorsa 'ilkini al' keyfîdir."* Ölçüldü (200 eğitim görevi):
    cevap verilen altı görevin **üçünde** birden çok aday tutuyor.
    Yâni keyfîlik nadir değil, cevapların yarısında.

    Keyfîliği kaldırmanın yolu bir **ölçüt** koymak ve o ölçüte göre
    **aramak**tır. Ölçüt Occam'dır: gösterim çiftlerinin hepsinde
    tutan adaylar arasında **en kısa tarifli olan** seçilir. Bu bir
    tercihtir, hakikat değildir; onun için tarifi burada duruyor ve
    ``ne="seçim"`` ile kırmızıya dönebilir hâlde ölçülüyor.

    Arama ``nefs/ara.py``ya havale edilir (Dürr--Høyer): ``K``yı
    bilmeden ``O(√N)``. Burada yeni riyaziye yoktur; nazırlık
    nazırlığı çağırır.
    """
    from .ara import ara                      # nazırlık nazırlığı çağırır
    tutan = list(d.get("tutan") or [])
    if len(tutan) <= 1:
        return str(d.get("kural")), list(d.get("tahmin") or [])
    # Occam ölçütü: tarif uzunluğu. Kural adı, kuralın **bileşim
    # derinliğinin** yazılı hâlidir; kısası az varsayar.
    bedel = np.array([float(len(str(getattr(a, "ad", a)))) for a in tutan])
    # Grover yazmacı 2^n boyut ister; eksik yerler **erişilmez** bedelle
    # doldurulur, böylece asgarî daima hakiki adaylardan çıkar.
    n = len(tutan)
    tam = 1
    while tam < n:
        tam *= 2
    if tam > n:
        bedel = np.concatenate([bedel, np.full(tam - n, bedel.max() + 1e3)])
    try:
        j = int(ara(bedel, ne="en_iyi", yol="dürr")["x"])
    except Exception:                         # pragma: no cover
        j = int(np.argmin(bedel))
    kural = tutan[j] if 0 <= j < n else tutan[0]
    izgara = []
    for a, _b in gorev.sinama:
        try:
            izgara.append(kural.uygula(a))
        except Exception:                     # pragma: no cover
            izgara.append(None)
    return str(getattr(kural, "ad", kural)), izgara


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
        kural, izgara = _sec(gorev, d)
        c = Cevap(gorev=gorev.ad, sukut=False, sebep="",
                  kural=kural, izgara=izgara,
                  aday_sayisi=int(d.get("aday_sayısı", 0)), tikaniklik=tik)

    if ne == "sukut_mu":
        return c.sukut
    if ne != "cevap":
        raise ValueError("söyleme kipi bilinmiyor: %r" % (ne,))
    return c
