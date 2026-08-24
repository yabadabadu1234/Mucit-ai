"""
Meleke (faculty) sözleşmesi ve sicili.

Her meleke, kaynak metindeki ``𝒪ₙ`` operatörünün koşabilir hâlidir:

    girdi uzayları  ──►  meleke  ──►  çıktı uzayları  + ölçümler

``sozlesme`` alanı, melekenin hangi ``Durum`` alanlarını **okuduğunu** ve
hangilerini **yazdığını** bildirir. Bu sadece belge değildir: ``akis.py``
her adımda sözleşmeyi denetler ve okunacak alan boşsa net bir hata verir.
Böylece 41 melekelik zincirde "sessizce ``None`` taşıma" imkânsızlaşır.
"""
from __future__ import annotations

from typing import Callable, Dict, List, Sequence, Tuple

from .uzaylar import Durum, Parametreler


class Meleke:
    """Bütün melekelerin ortak atası."""

    no: int = 0
    ad: str = ""
    okur: Tuple[str, ...] = ()
    yazar: Tuple[str, ...] = ()
    # İhtiyarî okumalar: varsa kullanılır, yoksa melekenin kendi yedeği
    # devreye girer. Bunlar bağımlılık çizgesine KATILMAZ; nefsin
    # devrelerinde tabiî olan geri besleme (ör. 𝒪₇ Mana'nın henüz
    # kurulmamış gayeye bakması) ancak böyle temsil edilebilir.
    ihtiyari: Tuple[str, ...] = ()

    def uygula(self, d: Durum, p: Parametreler) -> None:  # pragma: no cover
        raise NotImplementedError

    # -- sözleşme denetimi -------------------------------------------
    def girdiyi_denetle(self, d: Durum) -> None:
        for alan in self.okur:
            if getattr(d, alan, None) is None:
                raise ValueError(
                    "𝒪%d %s: '%s' alanı boş; bu melekeden önce onu yazan "
                    "meleke koşmamış." % (self.no, self.ad, alan)
                )

    def ciktiyi_denetle(self, d: Durum) -> None:
        for alan in self.yazar:
            if getattr(d, alan, None) is None:
                raise ValueError(
                    "𝒪%d %s: '%s' alanını yazacağını bildirdi, yazmadı."
                    % (self.no, self.ad, alan)
                )

    def kosu(self, d: Durum, p: Parametreler) -> None:
        self.girdiyi_denetle(d)
        self.uygula(d, p)
        self.ciktiyi_denetle(d)

    def __repr__(self) -> str:
        return "𝒪%d %s" % (self.no, self.ad)


_SICIL: Dict[int, Meleke] = {}


def kaydet(sinif):
    """Sınıf dekoratörü: melekeyi numarasıyla sicile yazar."""
    ornek = sinif()
    if ornek.no in _SICIL:
        raise ValueError("𝒪%d iki kere kaydedildi: %s ve %s"
                         % (ornek.no, _SICIL[ornek.no].ad, ornek.ad))
    _SICIL[ornek.no] = ornek
    return sinif


def sicil() -> Dict[int, Meleke]:
    return dict(_SICIL)


def melekeler() -> List[Meleke]:
    return [_SICIL[i] for i in sorted(_SICIL)]
