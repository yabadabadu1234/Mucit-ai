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


def rapor() -> str:                                     # pragma: no cover
    """Kendi kendini gösterme (H126): **sözleşme fiilen tutuyor mu?**

    Bir sicil raporu, sicilin uzunluğunu yazmakla yetinemez; asıl iddia
    *"sessizce ``None`` taşıma imkânsızlaşır"*dır ve bu ancak ihlâl
    denenerek gösterilir. Burada kasten bozuk bir meleke koşturulur ve
    sözleşmenin **hata verdiği** görülür; vermezse ölçü kırmızıdır.
    """
    import numpy as np

    from .uzaylar import Durum, Parametreler

    # Sicil, melekeleri TARİF EDEN modüller içe aktarılınca dolar;
    # bu dosya tek başına koşturulunca boştur ve "0 meleke" yazmak
    # yanıltıcı olurdu. Onun için kayıt eden modüller burada çağrılır.
    for m in ("nefs.idrak", "nefs.akil", "nefs.murakabe", "nefs.beyan"):
        try:
            __import__(m)
        except Exception:                          # pragma: no cover
            pass

    s = ["MELEKE SÖZLEŞMESİ VE SİCİLİ", ""]
    sc = sicil()
    s.append("  sicilde kayıtlı meleke : %d" % len(sc))
    if sc:
        k = sorted(sc)
        s.append("  numara aralığı         : 𝒪%d … 𝒪%d" % (k[0], k[-1]))
        bos = [i for i in k if not sc[i].okur and not sc[i].yazar]
        s.append("  sözleşmesi BOŞ olan    : %d" % len(bos))

    s.append("")
    s.append("  Sözleşme fiilen tutuyor mu? (kasten ihlâl edilir)")

    class _Okumayan(Meleke):
        no, ad = 9001, "sınama-okumayan"
        okur = ("olmayan_alan",)

        def uygula(self, d, p):                    # pragma: no cover
            return None

    class _Yazmayan(Meleke):
        no, ad = 9002, "sınama-yazmayan"
        yazar = ("olmayan_alan",)

        def uygula(self, d, p):
            return None

    d, p = Durum(E=np.zeros((2, 2))), Parametreler()
    for m in (_Okumayan(), _Yazmayan()):
        try:
            m.kosu(d, p)
            s.append("    %-22s HATA VERMEDİ  ← KIRMIZI" % m.ad)
        except (ValueError, AttributeError, TypeError) as e:
            s.append("    %-22s reddedildi: %s"
                     % (m.ad, str(e).split(";")[0][:56]))
    return "\n".join(s)


if __name__ == "__main__":   # pragma: no cover
    print(rapor())
