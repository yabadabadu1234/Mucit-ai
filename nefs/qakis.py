"""
Kübit-yerli küllî akış: 41 meleke, tek dalga, tek ölçüm.

``nefs/akis.py`` (reel ``S`` üzerindeki akış) **yerinde durur** ve 41
sınaması geçmeye devam eder; kullanıcı hükmü böyleydi: "yerinde kalsın,
kübit akışı yanına kurulsun, sonra devralınsın". İkisi aynı girdide
karşılaştırılabilir.

Farkı şudur: burada ``S`` diye bir şey **yoktur**. Nefsin bütün hâli tek
bir kuantum durumudur; 41 melekenin hepsi o duruma vurulan üniter
kapılardır; hiçbiri hiçbir şey okumaz. Hükmün sayısı ancak en sonda,
POVM zayıf ölçümüyle doğar -- ve bir sayı değil **dağılımdır**.

Akış::

    ham duyu E
      → veri kübitlerine kodla (kayıpsız intibak, H14)
      → SÜPERPOZİSYON (yalnız veri; hüküm |0⟩'da kalır)
      → MERA: dolanıklık çözücü + izometri → DOLAŞIKLIK (ölçülür)
      → 41 meleke, üniter kapı olarak, AKIS sırasında
      → BEC faz kilidi -- yalnız tepede (H30)
      → POVM zayıf ölçüm: makam dağılımı + küllî hükümler (H31)
"""
from __future__ import annotations

import math
import time
from dataclasses import replace
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from .qmeleke import QAKIS, QParametre, qmelekeler, qsicil
from .qyazmac import MAKAM_ADLARI, QAyar, QYazmac, donme

__all__ = ["QNefs", "rapor", "bec_faz_kilidi"]


#: Yoğuşmaya (kondensata) **giren** küllî alanlar. Kütük H54, 4. borç:
#: BEC bütün küllî bloğa vurulunca sükûtu boğuyordu. Ölçüldü:
#: ``sukut 0,7924 → 0,0626`` (12,7 kat düşüş), üstelik ``tenakuz
#: 0,3305 → 0,5758`` ve ``P_Şek 0,1553 → 0,2561`` -- yani faz kilidi
#: nefsi hem susamaz hem daha çelişkili kılıyordu.
#:
#: Sebep kavramîdir, sayısal değil. BEC **hükmün ittihadıdır**: bütün
#: parçaların tek bir faza kilitlenmesi. Sükût bir hüküm DEĞİLDİR;
#: tenakuz ve nakz da hüküm değil, hükmün ÖNÜNDEKİ engellerdir. Onları
#: da aynı faza kilitlemek, "bilmiyorum" diyebilme kabiliyetini
#: (kütük H10) faz kilidiyle susturmak demektir. Onun için yoğuşmaya
#: yalnız hüküm taşıyan alanlar girer.
YOGUSAN: Tuple[str, ...] = ("makam", "mizan", "tasdik", "kelam")


def bec_faz_kilidi(q: QYazmac, tur: int = 6, g: float = 0.35) -> None:
    """Gross–Pitaevskii faz kilidi -- **yalnız tepede** (kütük H30).

    ``iħ∂Ψ/∂t = (−∇²/2m + V_gaye + g|Ψ|²)Ψ``. BEC'i her yere boca etmek
    süperpozisyonu öldürür; burada yalnız **küllî hüküm bloğuna**, yani
    nihaî tasdik makamına uygulanır. Veri kübitlerine dokunulmaz;
    dolayısıyla dalga diri kalır.

    Üniter kalması şarttır: doğrusal olmayan ``g|Ψ|²`` terimi burada
    kübit sayısına bağlı **sabit** bir açıya çevrilir (ortalama alan
    yaklaşığı). Gerçek doğrusalsızlık okuma isterdi; bu, onun üniter
    ve okumasız karşılığıdır ve öyle bildirilir.
    """
    alanlar = [(ad, kac) for ad, kac in q.ayar.kulli_alanlar
               if ad in YOGUSAN]
    for t in range(tur):
        # kinetik terim: blok içi komşu bağları
        for ad, kac in alanlar:
            for j in range(kac - 1):
                q.cift(q.kulli(ad, j), _kinetik(0.12))
        # ortalama alan: her kübite aynı faz -- ittihad
        faz = g / (1.0 + t)
        for ad, kac in alanlar:
            for j in range(kac):
                q.tek(q.kulli(ad, j), donme(faz))


def _kinetik(teta: float) -> np.ndarray:
    """``−∇²``in iki kübitlik üniter karşılığı: komşu genlik alışverişi."""
    c, s = math.cos(teta), math.sin(teta)
    G = np.eye(4)
    G[1, 1] = c
    G[1, 2] = -s
    G[2, 1] = s
    G[2, 2] = c
    return G


class QNefs:
    """41 üniter melekeyi tek dalga üzerinde koşturan işletici."""

    def __init__(self, tohum: int = 0, ayar: Optional[QAyar] = None,
                 sira: Sequence[int] = QAKIS) -> None:
        self.p = QParametre(tohum)
        self.ayar = ayar or QAyar(tohum=tohum)
        self.sira = tuple(sira)
        self.s = qsicil()

    # -----------------------------------------------------------------
    def idrak_et(self, E: np.ndarray, bec: bool = True,
                 yigin: int = 0) -> QYazmac:
        """Ham duyudan nihaî hükme -- tek geçiş, hiç okuma yok.

        ``E`` ``(n, d)`` ise tek girdi; ``(B, n, d)`` ise **yığın**:
        ``B`` ayrı girdi aynı anda idrak edilir ve her üye kendi hükmünü
        verir. ``yigin`` açıkça verilirse yazmaç o büyüklükte kurulur
        (aynı girdi ``B`` kere -- yalnız hız ölçümü için).
        """
        E = np.asarray(E, float)
        B = E.shape[0] if E.ndim == 3 else max(1, int(yigin))
        n_satir = E.shape[-2]
        ayar = self.ayar
        if B != ayar.yigin:
            ayar = replace(ayar, yigin=B)
        q = QYazmac(n_satir, ayar)
        q.kodla(E)
        q.superpozisyon()
        q.mera()
        for no in self.sira:
            self.s[no].kosu(q, self.p)
        if bec:
            bec_faz_kilidi(q)
        return q

    # -- eğitim arayüzü ------------------------------------------------
    def __len__(self) -> int:
        """Öğrenilecek açı sayısı. Yer tahsisi ilk koşuda yapılır;
        bu yüzden ``idrak_et`` bir kere çağrılmadan sayı bilinmez ve
        bilinmediği hâlde tahmin edilmez."""
        return len(self.p)

    def vektor(self) -> np.ndarray:
        return self.p.vektor()

    def yukle(self, v: np.ndarray) -> None:
        self.p.yukle(v)


# =====================================================================
def rapor(tohum: int = 0, n: int = 20, d_in: int = 12,
          ayar: Optional[QAyar] = None) -> str:
    rng = np.random.default_rng(tohum)
    E = rng.normal(size=(n, d_in))
    nefs = QNefs(tohum, ayar)
    t0 = time.perf_counter()
    q = nefs.idrak_et(E)
    dt = time.perf_counter() - t0
    o = q.olcumler()

    s = ["=== nefs (KÜBİT): 41 meleke, tek dalga, tek ölçüm ===",
         "",
         "kübit=%d  (satır=%d × %d + küllî %d)   χ=%d   durum=%.1f KB"
         % (q.n, q.n_satir, q.oge, q.ayar.kulli_kubit, q.ayar.bag,
            q.y.bayt / 1024.0),
         "kapı=%d  takas=%d  MPO=%d  toplam kesme=%.3e  %.2f sn"
         % (q.iz.kapi, q.iz.takas, q.iz.supurme, q.iz.kesme, dt),
         "",
         "SÜPERPOZİSYON → DOLAŞIKLIK (ölçülen, iddia edilen değil):",
         "  MERA öncesi entropi = %.6f  (Schmidt = %d)"
         % (q.iz.entropi_once, q.iz.schmidt_once),
         "  MERA sonrası entropi = %.6f  (Schmidt = %d)"
         % (q.iz.entropi_sonra, q.iz.schmidt),
         "  akış sonu entropi    = %.6f" % o["entropi"],
         "  norm hatası          = %.2e" % o["norm_hatası"],
         "",
         "MAKAM DAĞILIMI (POVM zayıf ölçüm -- ÇÖKÜŞ YOK):"]
    for ad in MAKAM_ADLARI:
        p = o["P_" + ad]
        s.append("  %-6s %.4f  %s" % (ad, p, "█" * int(round(40 * p))))
    s += ["",
          "KÜLLÎ HÜKÜMLER (zayıf okuma, [0,1]):"]
    for ad, _ in q.ayar.kulli_alanlar:
        s.append("  %-9s %.4f" % (ad, o[ad]))
    s += ["", "MELEKELERİN İCRA İZİ:"]
    s += ["  " + x for x in q.iz.gunluk]
    return "\n".join(s)


if __name__ == "__main__":   # pragma: no cover
    print(rapor())
