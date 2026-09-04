"""TARTMAK -- hâl ne kadar doğru, kim sözünde durmadı.

Nazırlık katının dördüncü fiili (kütük H227). **Yeni riyaziye yoktur.**

    mizan = tart(hal, hedef)

`main` artık *"küllî kaybı hesapla, sözleşmeyi denetle, ezberi ölç,
hükmü oku"* diye dört kapı çağırmaz -- **bir kere `tart` der**.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np

from .kulli_kayip import ezber_mi, sozunde_mi, zayif_halka

__all__ = ["Mizan", "tart"]


@dataclass
class Mizan:
    """TARTININ NETİCESİ -- tek sayı değil, bir **döküm**.

    Bir kayıp sayısı hangi uzvun bozduğunu söylemez; mîzân söyler.
    """

    kayip: float = 0.0                       # zayıf halkaya göre toplam
    halka: Optional[int] = None              # en zayıf halka hangisi
    ihlal: List[Dict[str, Any]] = field(default_factory=list)
    ezber: Optional[Dict[str, Any]] = None
    sozunde: bool = True                     # hiç ihlâl yok mu
    dokum: Dict[str, float] = field(default_factory=dict)

    def __repr__(self) -> str:               # pragma: no cover
        return ("Mizan(kayıp=%.6g, zayıf_halka=%s, ihlâl=%d, sözünde=%s)"
                % (self.kayip, self.halka, len(self.ihlal), self.sozunde))


def tart(hal=None, olcumler=None, beta: float = 8.0,
         sozlesme: bool = True, ezber: bool = False,
         n_satir: int = 3, chi: int = 16, ne: str = "mizan") -> Any:
    """TARTMAK -- ``Hal``den ``Mizan``.

    Üç kapıyı çağırır:

    1. ``zayif_halka`` -- ölçüleri **yumuşak asgarî** ile topla.
       Zincir en zayıf halkası kadardır; ortalama almak zayıf halkayı
       güçlülerin arkasına saklar. ``β`` yumuşaklığı ayarlar:
       ``β → ∞`` katı asgarî, ``β → 0`` ortalama.
    2. ``sozunde_mi`` -- her meleke ilân ettiği bölgede mi kaldı.
       Bir uzuv ilân etmediği yere dokunduysa kayıp düşse bile
       **ihlâl** vardır; ucuz gelen doğru cevap borç bırakır.
    3. ``ezber_mi``   -- ``ezber=True`` ise ezber ile öğrenmenin farkı
       ölçülür (pahalıdır, her turda çağrılmaz).

    ==============  ==================================================
    ``ne``          döndürdüğü
    ==============  ==================================================
    ``mizan``       ``Mizan`` -- hepsi
    ``kayıp``       yalnız tek sayı (ucuz; tâlim döngüsünün içi)
    ==============  ==================================================

    **Sözleşme denetimi kaybın parçası değil, şahididir.** Kayıp
    "ne kadar yanlış" der; sözleşme "kim haddini aştı" der. İkisi
    karıştırılırsa haddini aşan uzuv düşük kayıpla aklanır.
    """
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
        except Exception:                    # pragma: no cover
            pass

    ez = ezber_mi(ne="kıyas") if ezber else None

    if ne != "mizan":
        raise ValueError("tartı kipi bilinmiyor: %r" % (ne,))
    return Mizan(kayip=kayip, halka=halka, ihlal=ihlal, ezber=ez,
                 sozunde=not ihlal,
                 dokum={"ölçü_%d" % i: v for i, v in enumerate(olcumler)})
