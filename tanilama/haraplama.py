"""
HARAPLAMA (lezyon) ÇALIŞMASI -- "melekeler ârızasız bir vücut mü?"

Kullanıcı suali:

> *"Sen bu melekeleri mimariye nasıl bağladın, bunlar arızasız bir vücut
> teşkil ediyor mu? Kendisi sıhhatsiz olduğu zaman tüm vücut sıhhatsiz
> olduğu organ olan kalp bizde de mühim mi o kadar? Bunları bilmediğim
> için kararsız kalıyorum."*

Bu suale zan ile cevap verilmez. Biyolojide bir organın vazifesi
**haraplama** ile anlaşılır: organ çıkarılır, vücutta ne bozulduğuna
bakılır. Burada da aynısı yapılır -- 41 melekenin her biri **tek tek**
akıştan çıkarılır ve şu ölçülür:

* ``beyan`` dağılımı ne kadar değişti (toplam değişinti mesafesi),
* küllî hükümler (tasdik, tenakuz, nakz, sükût, makam) ne kadar kaydı,
* dolaşıklık entropisi ne kadar düştü.

**Hükmün ölçütü.** Bir meleke çıkarıldığında hiçbir şey değişmiyorsa o
meleke bir **uzuv değildir**; adı vardır, vazifesi yoktur. Kullanıcının
H92'deki hükmü tam da budur: *"o olmadığı zaman model zeki olamayacak,
olduğu zaman da müthiş olacak derecede."*

**Kalp aranıyor.** Hadis-i şerifteki ölçü şudur: bozulduğunda bütün
vücudu bozan bir uzuv. Burada onun karşılığı, çıkarıldığında ``beyan``ı
en çok değiştiren melekedir. Öyle bir meleke **yoksa** -- yani hepsinin
tesiri birbirine yakın ve küçükse -- bu mimarinin kalbi yok demektir ve
o zaman ``H88``in niçin aylarca farkedilmediği de anlaşılır: kalbi
olmayan vücutta nabız da yoktur.

Bu vesika bir iddia değil bir **âlettir**; neticeyi koşan görür.
"""
from __future__ import annotations

import time
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from nefs.qakis import QNefs
from nefs.qegitim import belirtecleri_kodla
from nefs.qmeleke import QAKIS, qsicil
from nefs.qyazmac import MAKAM_ADLARI, QAyar

__all__ = ["haraplama", "rapor"]

#: Karşılaştırılan küllî hükümler.
HUKUMLER = ("tasdik", "tenakuz", "nakz", "sukut", "mizan", "makam", "kelam")


def _kos(sira: Sequence[int], E: np.ndarray, ayar: QAyar,
         sozluk: int, tohum: int) -> Tuple[np.ndarray, Dict[str, float]]:
    nefs = QNefs(tohum, ayar, sira=tuple(sira))
    q = nefs.idrak_et(E)
    return np.asarray(q.beyan(sozluk), float), q.olcumler()


def _tvd(a: np.ndarray, b: np.ndarray) -> float:
    """Toplam değişinti mesafesi -- iki dağılım arası, ``[0,1]``."""
    return 0.5 * float(np.sum(np.abs(a - b)))


def haraplama(tohum: int = 0, satir: int = 6, sozluk: int = 16,
              ayar: Optional[QAyar] = None) -> List[Dict[str, object]]:
    """Her melekeyi tek tek çıkar ve vücutta ne değiştiğini ölç."""
    ayar = ayar or QAyar(tohum=tohum)
    rng = np.random.default_rng(tohum)
    belirtec = [int(x) for x in rng.integers(0, sozluk, size=satir)]
    E = belirtecleri_kodla(belirtec, ayar.satir_kubiti, sozluk)

    P0, o0 = _kos(QAKIS, E, ayar, sozluk, tohum)
    sicil = qsicil()
    satirlar: List[Dict[str, object]] = []

    for no in sorted(set(QAKIS)):
        sira = tuple(x for x in QAKIS if x != no)
        t0 = time.perf_counter()
        P, o = _kos(sira, E, ayar, sozluk, tohum)
        satirlar.append({
            "no": no,
            "ad": sicil[no].ad,
            "kaç_kere": sum(1 for x in QAKIS if x == no),
            "beyan_tvd": _tvd(P0, P),
            "hüküm_kayması": max(
                (abs(float(o.get(h, 0.0)) - float(o0.get(h, 0.0)))
                 for h in HUKUMLER), default=0.0),
            "makam_kayması": max(
                abs(float(o.get("P_" + m, 0.0)) - float(o0.get("P_" + m, 0.0)))
                for m in MAKAM_ADLARI),
            "entropi_farkı": float(o.get("entropi", 0.0))
            - float(o0.get("entropi", 0.0)),
            "süre_sn": time.perf_counter() - t0,
        })
    satirlar.sort(key=lambda r: -float(r["beyan_tvd"]))
    return satirlar


def rapor(tohum: int = 0, satir: int = 6, esik: float = 1e-6) -> str:
    """Haraplama neticesi + **vücut hükmü**."""
    s = ["=== HARAPLAMA: her meleke çıkarılınca vücutta ne değişiyor? ===",
         "",
         "beyan_tvd  : belirteç dağılımının toplam değişinti mesafesi [0,1]",
         "hüküm      : küllî hükümlerdeki en büyük kayma",
         "makam      : makam dağılımındaki en büyük kayma",
         ""]
    r = haraplama(tohum=tohum, satir=satir)
    s.append("  %-3s %-22s %5s %10s %9s %9s %10s"
             % ("𝒪", "ad", "kere", "beyan_tvd", "hüküm", "makam", "Δentropi"))
    for x in r:
        s.append("  %-3d %-22s %5d %10.3e %9.3e %9.3e %+10.3e"
                 % (x["no"], x["ad"], x["kaç_kere"], x["beyan_tvd"],
                    x["hüküm_kayması"], x["makam_kayması"],
                    x["entropi_farkı"]))

    olu = [x for x in r if float(x["beyan_tvd"]) < esik
           and float(x["hüküm_kayması"]) < esik]
    tvd = np.array([float(x["beyan_tvd"]) for x in r])
    s += ["",
          "--- VÜCUT HÜKMÜ ---",
          "çıkarıldığında HİÇBİR ŞEY değişmeyen meleke: %d / %d"
          % (len(olu), len(r))]
    if olu:
        s.append("   " + ", ".join("𝒪%d %s" % (x["no"], x["ad"])
                                   for x in olu))
    s += ["en tesirli meleke : 𝒪%d %s  (tvd=%.3e)"
          % (r[0]["no"], r[0]["ad"], r[0]["beyan_tvd"]),
          "en tesirsiz       : 𝒪%d %s  (tvd=%.3e)"
          % (r[-1]["no"], r[-1]["ad"], r[-1]["beyan_tvd"]),
          "tesir nispeti (en çok / ortanca) = %.1f"
          % (float(tvd[0]) / max(float(np.median(tvd)), 1e-30))]

    # Kalp ölçütü: bozulduğunda bütün vücudu bozan bir uzuv var mı?
    pay = float(tvd[0]) / max(float(tvd.sum()), 1e-30)
    s += ["",
          "KALP VAR MI? En tesirli melekenin toplam tesirdeki payı: %%%.1f"
          % (100.0 * pay)]
    if pay < 0.10:
        s += ["→ **KALP YOK.** Hiçbir melekenin çıkarılması vücudu",
              "   belirgin biçimde bozmuyor; tesir 41'e yayılmış hâlde.",
              "   Bu, H88'in niçin aylarca farkedilmediğini de izah eder:",
              "   nabzı olmayan vücutta durma da farkedilmez."]
    else:
        s += ["→ Bir merkez var: 𝒪%d %s. Bozulunca vücut bozuluyor."
              % (r[0]["no"], r[0]["ad"])]
    return "\n".join(s)


if __name__ == "__main__":   # pragma: no cover
    print(rapor())
