"""Havuz — şüphe uzayının açılması, karantina ve hüküm.

Bir iddia geldiğinde derhal kabul veya red edilmez.  Önce **şüphe
uzayı** açılır: iddiayı doğru kılan ve yalanlayan alternatif izahların
hepsi listelenir.  Deliller geldikçe her izahın ihtimali güncellenir.
İddia, ancak *rakiplerinden yeterince ayrıştığında* hükme bağlanır;
ayrışmadıysa **karantinada** kalır — "bilmiyorum" bir cevaptır ve
uydurmaktan üstündür.

Üç mekanizma:

1. **Şüphe uzayı** — hipotez havuzu; her biri bir önsel ve bir
   olabilirlik fonksiyonuyla gelir.  Güncelleme tam Bayes'tir:

   .. math::  P(H_i \\mid D) \\propto P(H_i)\\prod_k P(d_k \\mid H_i)

   Çarpım **log uzayında** yapılır: yüz delilden sonra ham çarpım
   ``1e-300``ün altına düşüp sıfırlanır ve bütün ardıl NaN olur.
   Log-toplam-üstel (``logsumexp``) ile azamî terim dışarı alınarak
   taşma da alttan taşma da engellenir; netice matematiksel olarak
   birebir aynıdır.

2. **Karantina** — hüküm ancak iki şart birden sağlanınca verilir:
   (i) en yüksek ihtimalli hipotezin ardılı ``eşik``in üstünde,
   (ii) ikinciyle arasındaki **log-oran** ``fark_eşiği``nin üstünde.
   Tek başına birincisi yetmez: iki hipotez de 0.49/0.48 ise "birincisi
   0.49" demek hüküm değildir.

3. **Hüküm** — kabul / red / karantina.  Ayrıca hükmün hangi delille
   döndüğü kaydedilir, ki geriye dönük denetlenebilsin.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = [
    "Hipotez", "Hukum", "Havuz", "logsumexp", "log_normalize",
]


def logsumexp(a: Sequence[float]) -> float:
    """``ln Σ exp(a_i)`` — azamî terim dışarı alınarak.

    ``m = max a``; ``ln Σ e^{a_i} = m + ln Σ e^{a_i − m}``.  Üsler artık
    ``≤ 0`` olduğundan taşma imkânsız; en az bir terim tam olarak
    ``e^0 = 1`` olduğundan alttan taşma da toplamı sıfırlayamaz.
    Hepsi ``−inf`` ise netice ``−inf``tir (boş toplam değil, imkânsız
    hâl).
    """
    arr = [float(x) for x in a]
    if not arr:
        return float("-inf")
    m = max(arr)
    if m == float("-inf"):
        return float("-inf")
    return m + math.log(sum(math.exp(x - m) for x in arr))


def log_normalize(log_a: Sequence[float]) -> List[float]:
    """Log uzayında normalize: ``log_a − logsumexp(log_a)``."""
    z = logsumexp(log_a)
    if z == float("-inf"):
        raise ValueError("bütün hipotezler imkânsız — havuz çökmüş")
    return [float(x) - z for x in log_a]


class Hukum(Enum):
    KABUL = "kabul"
    RED = "red"
    KARANTINA = "karantina"


@dataclass
class Hipotez:
    """Bir izah adayı.

    ``log_olabilirlik(d)`` delilin bu hipotez altındaki log
    olasılığını verir.  ``iddiayi_dogrular``: bu izah doğruysa asıl
    iddia da doğru mu?
    """
    ad: str
    log_onsel: float
    log_olabilirlik: Callable[[object], float]
    iddiayi_dogrular: bool = False
    log_ardil: float = field(default=0.0, init=False)

    @property
    def ardil(self) -> float:
        return math.exp(self.log_ardil)


@dataclass
class Havuz:
    """Şüphe uzayı ve onun üzerindeki hüküm mekanizması.

    ``esik``: en yüksek hipotezin ardılı için asgarî değer.
    ``fark_esigi``: birinci ile ikinci arasındaki asgarî **log-oran**
    (nat cinsinden; ``ln 3 ≈ 1.1`` "üç katı" demektir).
    """
    hipotezler: List[Hipotez]
    esik: float = 0.7
    fark_esigi: float = math.log(3.0)
    tarih: List[Dict[str, object]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if len(self.hipotezler) < 2:
            raise ValueError("şüphe uzayı en az iki izah içermeli — "
                             "tek hipotezli havuz şüphe değil, kabuldür")
        if not 0.0 < self.esik <= 1.0:
            raise ValueError("eşik ∈ (0,1]")
        self._normalize()

    def _normalize(self) -> None:
        logs = log_normalize([h.log_onsel for h in self.hipotezler]
                             if not self.tarih
                             else [h.log_ardil for h in self.hipotezler])
        for h, l in zip(self.hipotezler, logs):
            h.log_ardil = l

    # --- güncelleme ---------------------------------------------------
    def delil_ekle(self, delil: object, etiket: str = "") -> Dict[str, object]:
        """Tek bir delille Bayes güncellemesi — hep log uzayında."""
        ham = [h.log_ardil + h.log_olabilirlik(delil)
               for h in self.hipotezler]
        if logsumexp(ham) == float("-inf"):
            raise ValueError(f"delil {etiket!r} bütün izahları imkânsız "
                             "kıldı — şüphe uzayı eksik kurulmuş")
        for h, l in zip(self.hipotezler, log_normalize(ham)):
            h.log_ardil = l
        kayit = {
            "delil": etiket or repr(delil),
            "ardıllar": {h.ad: h.ardil for h in self.hipotezler},
            "hüküm": self.hukum()[0].value,
        }
        self.tarih.append(kayit)
        return kayit

    def deliller_ekle(self, deliller: Sequence[object],
                      etiketler: Optional[Sequence[str]] = None
                      ) -> List[Dict[str, object]]:
        et = etiketler or [f"d{i}" for i in range(len(deliller))]
        return [self.delil_ekle(d, e) for d, e in zip(deliller, et)]

    # --- hüküm --------------------------------------------------------
    def siralama(self) -> List[Hipotez]:
        return sorted(self.hipotezler, key=lambda h: -h.log_ardil)

    def ayrisma(self) -> float:
        """Birinci ile ikinci arasındaki log-oran."""
        s = self.siralama()
        return s[0].log_ardil - s[1].log_ardil

    def hukum(self) -> Tuple[Hukum, Dict[str, object]]:
        """Kabul / red / karantina — iki şartın ikisi de aranır."""
        s = self.siralama()
        bas, ikinci = s[0], s[1]
        ayr = bas.log_ardil - ikinci.log_ardil
        gerekce = {
            "en_yüksek": bas.ad,
            "ardıl": bas.ardil,
            "ikinci": ikinci.ad,
            "ikincinin_ardılı": ikinci.ardil,
            "ayrışma_log_oranı": ayr,
            "eşik_sağlandı": bas.ardil >= self.esik,
            "ayrışma_sağlandı": ayr >= self.fark_esigi,
        }
        if not (gerekce["eşik_sağlandı"] and gerekce["ayrışma_sağlandı"]):
            return Hukum.KARANTINA, gerekce
        return (Hukum.KABUL if bas.iddiayi_dogrular else Hukum.RED), gerekce

    # --- şüphe uzayını genişletme ------------------------------------
    def izah_ekle(self, h: Hipotez, pay: float = 0.1) -> None:
        """Sonradan akla gelen bir izahı havuza al.

        Yeni izaha ihtimal kütlesinin ``pay`` kadarı verilir, kalanı
        mevcutlar arasında **oranları korunarak** paylaştırılır.  Böylece
        yeni bir ihtimalin akla gelmesi, eski deliller yeniden işlenmeden
        de hükmü gevşetebilir — ki doğrusu budur: şüphe uzayı eksikse
        varılan kesinlik sahtedir.
        """
        if not 0.0 < pay < 1.0:
            raise ValueError("pay ∈ (0,1)")
        kalan = math.log1p(-pay)
        for eski in self.hipotezler:
            eski.log_ardil += kalan
        h.log_ardil = math.log(pay)
        self.hipotezler.append(h)
        self.tarih.append({"delil": f"[yeni izah: {h.ad}]",
                           "ardıllar": {x.ad: x.ardil
                                        for x in self.hipotezler},
                           "hüküm": self.hukum()[0].value})

    def ozet(self) -> str:
        s = self.siralama()
        h, g = self.hukum()
        satir = [f"  {x.ad:24s} {x.ardil:.6f}" for x in s]
        satir.append(f"  → hüküm: {h.value.upper()}"
                     f"   (ardıl {g['ardıl']:.3f} eşik {self.esik},"
                     f" ayrışma {g['ayrışma_log_oranı']:.3f}"
                     f" eşik {self.fark_esigi:.3f})")
        return "\n".join(satir)


# ══════════════════════════════════════════════════════════════════════
#  Gösterim
# ══════════════════════════════════════════════════════════════════════

def _bernoulli(p: float) -> Callable[[object], float]:
    """``d=1`` iken ``ln p``, ``d=0`` iken ``ln(1−p)``."""
    lp, lq = math.log(p), math.log1p(-p)
    return lambda d: lp if d else lq


def _havuz_kur() -> Havuz:
    """İddia: 'şu âlet bozuk'. Üç izah."""
    return Havuz([
        Hipotez("âlet bozuk", math.log(0.2), _bernoulli(0.9), True),
        Hipotez("ölçen beceriksiz", math.log(0.3), _bernoulli(0.6), False),
        Hipotez("her şey yolunda", math.log(0.5), _bernoulli(0.1), False),
    ], esik=0.7, fark_esigi=math.log(3.0))


def _gosterim() -> str:
    s: List[str] = []

    s.append("=== Şüphe uzayı: 'âlet bozuk' iddiası ===")
    h = _havuz_kur()
    s.append("  başlangıç (önseller):")
    s.append(h.ozet())

    s.append("\n  deliller birer birer (1 = anormal okuma):")
    for i, d in enumerate([1, 1, 1, 1, 1]):
        k = h.delil_ekle(d, f"okuma{i+1}")
        bas = max(k["ardıllar"].items(), key=lambda t: t[1])
        s.append(f"    {k['delil']:9s} → en yüksek {bas[0]:18s}"
                 f" {bas[1]:.6f}   hüküm: {k['hüküm']}")
    s.append(h.ozet())

    s.append("\n=== Karantina: deliller ayrıştırmıyorsa ===")
    h2 = Havuz([
        Hipotez("A", math.log(0.5), _bernoulli(0.55), True),
        Hipotez("B", math.log(0.5), _bernoulli(0.45), False),
    ], esik=0.7, fark_esigi=math.log(3.0))
    h2.deliller_ekle([1, 1, 0, 1, 0, 1])
    s.append(h2.ozet())
    s.append("  → birinci sırada olmak hüküm için yetmiyor; ayrışma şart.")

    s.append("\n=== Yeni bir izah akla gelirse kesinlik gevşer ===")
    h3 = _havuz_kur()
    h3.deliller_ekle([1] * 6)
    hh, gg = h3.hukum()
    s.append(f"  altı delilden sonra: {hh.value}"
             f"  (ardıl {gg['ardıl']:.6f})")
    h3.izah_ekle(Hipotez("başka bir âlet karıştı", math.log(0.1),
                         _bernoulli(0.95), False), pay=0.35)
    hh2, gg2 = h3.hukum()
    s.append(f"  yeni izah eklenince: {hh2.value}"
             f"  (en yüksek {gg2['en_yüksek']} {gg2['ardıl']:.6f},"
             f" ayrışma {gg2['ayrışma_log_oranı']:.4f})")
    s.append("  → şüphe uzayı eksikken varılan kesinlik sahteydi.")

    s.append("\n=== Log uzayı olmasa ne olurdu? ===")
    hh4 = _havuz_kur()
    hh4.deliller_ekle([1] * 400)
    s.append(f"  400 delil sonrası ardıllar (log uzayında):"
             f" {[f'{x.ardil:.3e}' for x in hh4.siralama()]}")
    s.append("  aynı hesap ham çarpımla, hipotez hipotez:")
    for ad, onsel, p in (("âlet bozuk", 0.2, 0.9),
                         ("ölçen beceriksiz", 0.3, 0.6),
                         ("her şey yolunda", 0.5, 0.1)):
        ham = onsel * (p ** 400)
        s.append(f"    {ad:18s} {onsel}·{p}^400 = {ham:.3e}"
                 f"  {'← SIFIRA düştü' if ham == 0.0 else ''}")
    s.append("  n=400'de üç terimden yalnız BİRİ sıfırlandı; payda hâlâ")
    s.append("  sağlam. Ham çarpımın fiilen çöktüğü yeri arayalım —")
    s.append("  tahmin etmeyip ölçerek:")
    kirilma = None
    for n in range(100, 40001, 20):
        payda = 0.2 * 0.9 ** n + 0.3 * 0.6 ** n + 0.5 * 0.1 ** n
        if payda == 0.0:
            kirilma = n
            break
    s.append(f"    payda ilk defa n≈{kirilma} civarında sıfırlanıyor"
             f"  (0.2·0.9^{kirilma} = {0.2 * 0.9 ** kirilma:.3e})")
    s.append(f"    n={kirilma}'de log uzayındaki ardıl ise tam:")
    hh5 = _havuz_kur()
    hh5.deliller_ekle([1] * kirilma)
    s.append("      " + ", ".join(f"{x.ad}={x.ardil:.6e}"
                                  for x in hh5.siralama()))
    s.append("  Yani ham çarpım birkaç yüz delilde değil, birkaç binde")
    s.append("  çöküyor; ama çöktüğünde ardıl 0/0 = NaN oluyor ve hiçbir")
    s.append("  uyarı vermiyor. Log uzayında böyle bir sınır yok.")

    s.append("\n=== Sınır hâlleri ===")
    try:
        Havuz([Hipotez("tek", 0.0, _bernoulli(0.5), True)])
    except ValueError as e:
        s.append(f"  tek hipotezli havuz reddedildi: {e}")
    h5 = Havuz([Hipotez("A", math.log(0.5), lambda d: float("-inf"), True),
                Hipotez("B", math.log(0.5), lambda d: float("-inf"), False)])
    try:
        h5.delil_ekle(1, "imkânsız")
    except ValueError as e:
        s.append(f"  bütün izahları imkânsız kılan delil: {e}")
    return "\n".join(s)


def rapor() -> str:
    return _gosterim()


if __name__ == "__main__":
    print(rapor())
