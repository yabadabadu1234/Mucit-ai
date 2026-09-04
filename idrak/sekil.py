"""Çıktı ızgarasının şeklini **gösterimlerden çıkarmak**.

Neden ayrı bir kip?  Ölçüldü: şekil başı yokken model ürettiği
ızgaraların %96'sını iyi biçimli yapıyor ama **şekli %0** doğru
oluyordu; tam eşleşme imkânsızdı.  Şekil başı eklendikten sonra da
doğrulama şekil isabeti 500 adımda ancak 0.027'ye çıktı.  Bunun
mimarî bir eksiklik mi yoksa eğitim eksikliği mi olduğunu **ölçtüm**:
donuk kodlayıcının havuz vektörü üstünde doğrusal bir yoklama (probe)
satır için 0.325, sütun için 0.338 verdi.  Yani bilgi kısmen orada,
fakat 31 sınıflı bir sınıflandırma olarak öğrenilmesi ağır.

Oysa ARC'ta şekil çoğunlukla **gösterim çiftlerinden cebirle**
çıkarılır.  Resmî kümelerde ölçülen düzenlilik:

======================================  ========  ==========
kaide                                   training  evaluation
======================================  ========  ==========
çıktı şekli = girdi şekli               0.659     0.698
görev içi sabit ORAN kuralı tutuyor     0.820     0.692
görev içi sabit MUTLAK şekil tutuyor    0.413     0.208
======================================  ========  ==========

Bu yüzden şekil, sinir ağına bırakılmadan önce **ispatlı** bir kaide
ile aranır: kaide bütün gösterim çiftlerinde tutuyorsa kullanılır,
tutmuyorsa **sükût edilir** ve sinir ağının şekil başına dönülür.
``idrak.cozucu``'daki "ya ispat ya sükût" ölçütünün aynısı.

Kaide her eksen için **bağımsız** aranır; aday kipler:

* ``sabit``   — çıktı kenarı sabit ``c``
* ``oran``    — çıktı kenarı = girdinin **aynı** kenarının ``p/q``'si
* ``çapraz``  — çıktı kenarı = girdinin **öteki** kenarının ``p/q``'si
  (devrik ve devrik-ölçekleme bu kiple kapanır)

Kesirler ``fractions.Fraction`` ile **tam** tutulur; kayan nokta
yuvarlamasıyla "3.0000001 kat" gibi sahte kaideler kabul edilmez.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["SekilKaidesi", "kesirli_sekil_kaidesi"]


class SekilKaidesi:
    """İki eksenin kaidesi birlikte -- ``(kip, katsayı)`` çifti olarak.

    KÜME 6 tevhidinde (kütük H225) ``EksenKaidesi`` buraya eridi: tek
    eksenin kaidesi bir sınıf olmayı hak edecek kadar hâl tutmuyordu --
    iki alanı (``kip``, ``deger``) ve tek bir metodu vardı, o metot da
    ancak bu sınıfın içinden çağrılıyordu.
    """

    def __init__(self, satir: Tuple[str, object], sutun: Tuple[str, object]):
        self.satir, self.sutun = satir, sutun

    @property
    def ad(self) -> str:
        return "%s|%s" % (self.satir[0], self.sutun[0])

    @staticmethod
    def _eksen(kaide: Tuple[str, object], gs: Tuple[int, int],
               eksen: int) -> Optional[int]:
        kip, deger = kaide
        if kip == "sabit":
            return int(deger)
        kaynak = gs[eksen] if kip == "oran" else gs[1 - eksen]
        pay = Fraction(kaynak) * deger
        if pay.denominator != 1 or pay < 1:
            return None                       # tam sayı değilse sükût
        return int(pay)

    def kestir(self, girdi: np.ndarray, azami_kenar: int = 30
               ) -> Optional[Tuple[int, int]]:
        gs = (int(girdi.shape[0]), int(girdi.shape[1]))
        r = self._eksen(self.satir, gs, 0)
        c = self._eksen(self.sutun, gs, 1)
        if r is None or c is None:
            return None
        if not (1 <= r <= azami_kenar and 1 <= c <= azami_kenar):
            return None                       # ARC sınırı dışı → sükût
        return r, c

    def __repr__(self) -> str:                # pragma: no cover
        return "SekilKaidesi(%r, %r)" % (self.satir, self.sutun)


def kesirli_sekil_kaidesi(ciftler=None, eksen: int = 0, ne: str = "kaide",
                          gorevler=None, azami_kenar: int = 30):
    """ÇIKTININ ŞEKLİ HANGİ KESİRDEN ÇIKIYOR -- tek terkip (kütük H225).

    Küme: ``EksenKaidesi.uygula`` + ``eksen_kaidesi`` + ``sekil_kaidesi``
    + ``kume_olc``. Dördü tek amelin durakları idi: bir eksende bütün
    çiftlerde tutan kaideyi bul, iki ekseni birleştir, kestir, ve
    görmediği çiftte ölç.

    ==============  ==================================================
    ``ne``          döndürdüğü
    ==============  ==================================================
    ``eksen``       tek eksen için ``(kip, katsayı)`` yahut ``None``
    ``kaide``       iki eksenin ``SekilKaidesi``i yahut ``None``
    ``ölç``         kaide ne kadar **kapsıyor**, kapsayınca ne kadar
                    **doğru**
    ==============  ==================================================

    Aday kipler:

    * ``sabit``   -- çıktı kenarı sabit ``c``
    * ``oran``    -- çıktı kenarı = girdinin **aynı** kenarının ``p/q``si
    * ``capraz``  -- çıktı kenarı = girdinin **öteki** kenarının ``p/q``si
      (devrik ve devrik-ölçekleme bu kiple kapanır)

    **Sıralama en dara doğru değil, en bilgilendiriciye doğrudur:**
    önce oran (girdiye bağlı, dolayısıyla genelleyen), sonra çapraz, en
    son sabit. Sebep: 2×2 girdilerden ibaret bir görevde "sabit 2" de
    "oran 1" de tutar; genelleyeni orandır.

    Kesirler ``fractions.Fraction`` ile **tam** tutulur; kayan nokta
    yuvarlamasıyla "3.0000001 kat" gibi sahte kaideler kabul edilmez.

    Kaide bütün gösterim çiftlerinde tutuyorsa kullanılır, tutmuyorsa
    **sükût edilir** -- ``idrak.cozucu``daki "ya ispat ya sükût"
    ölçütünün aynısı.

    ``ölç`` kipinde ölçüm gösterim çiftlerinden kurulup **sınama**
    çiftlerinde denetlenir; yani kaide hiç görmediği çifte uygulanır.
    """
    if ne == "eksen":
        if not ciftler:
            return None
        for kip in ("oran", "capraz"):
            katsayilar = set()
            for a, b in ciftler:
                kaynak = (a.shape[eksen] if kip == "oran"
                          else a.shape[1 - eksen])
                if kaynak == 0:
                    return None
                katsayilar.add(Fraction(int(b.shape[eksen]), int(kaynak)))
            if len(katsayilar) == 1:
                return (kip, katsayilar.pop())
        kenarlar = {int(b.shape[eksen]) for _, b in ciftler}
        if len(kenarlar) == 1:
            return ("sabit", kenarlar.pop())
        return None

    if ne == "kaide":
        sa = kesirli_sekil_kaidesi(ciftler, 0, "eksen")
        su = kesirli_sekil_kaidesi(ciftler, 1, "eksen")
        if sa is None or su is None:
            return None
        return SekilKaidesi(sa, su)

    if ne != "ölç":
        raise ValueError("şekil kaidesinin kipi bilinmiyor: %r" % (ne,))

    kapsanan = dogru = toplam = 0
    kip_sayaci: Dict[str, int] = {}
    for g in gorevler:
        k = kesirli_sekil_kaidesi(g.egitim)
        for a, b in g.sinama:
            toplam += 1
            if k is None:
                continue
            tahmin = k.kestir(a, azami_kenar)
            if tahmin is None:
                continue
            kapsanan += 1
            kip_sayaci[k.ad] = kip_sayaci.get(k.ad, 0) + 1
            if tahmin == (int(b.shape[0]), int(b.shape[1])):
                dogru += 1
    return {"sınama_çifti": toplam, "kapsanan": kapsanan, "doğru": dogru,
            "kapsam": kapsanan / max(toplam, 1),
            "isabet_kapsayınca": dogru / max(kapsanan, 1),
            "kip": dict(sorted(kip_sayaci.items(), key=lambda x: -x[1]))}



def _gosterim() -> str:                        # pragma: no cover
    from . import arc
    s = ["=== Şekil kaidesi: ispatlı kestirim, yoksa sükût ==="]
    for kume in ("training", "evaluation"):
        try:
            g = arc.gorevleri_getir(kume)
        except Exception as e:
            s.append("  %s yüklenemedi: %s" % (kume, e))
            continue
        d = kesirli_sekil_kaidesi(ne="ölç", gorevler=g)
        s.append("  %-10s  görev=%4d  sınama çifti=%4d" % (kume, len(g),
                                                           d["sınama_çifti"]))
        s.append("    kapsam=%.3f   kapsayınca isabet=%.3f   (doğru %d)"
                 % (d["kapsam"], d["isabet_kapsayınca"], d["doğru"]))
        s.append("    kipler: %s" % d["kip"])
    s.append("\n  Kıyas — sinir ağının şekil başı (500 adım, doğrulama):"
             " 0.027")
    s.append("  Kıyas — donuk havuz üstünde doğrusal yoklama: 0.325 / 0.338")
    return "\n".join(s)


if __name__ == "__main__":                     # pragma: no cover
    print(_gosterim())
