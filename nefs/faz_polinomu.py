"""FAZ POLİNOMU -- KÖŞEGEN FAZLAR TABLOYU DALLANDIRMAZ.

    from nefs.faz_polinomu import faz_oturt
    o = faz_oturt(k)          # k: |x⟩ ↦ ω^{k(x)}|x⟩  üsleri, Z_m'de
    o["derece"]               # ≤ 3 ise CNOT-Dihedral sınıfındadır

===================================================================
AMY-MASLOV-MOSCA TEOREMİ (2014)
===================================================================

**Zabıt (Non-Clifford Çıkmazı, dördüncü fasıl):** *"Clifford grubuna
sadece köşegen non-Clifford faz kapıları (T-kapıları, Z-rotasyonları,
KAN köşegen fazları) eklendiğinde oluşan grup CNOT-Dihedral gruptur.
Bu gruptaki bütün non-Clifford evrimler, durumu bir stabilizer
toplamına açmadan, n değişkenli tek bir İkili Faz Polinomu olarak
O(n²) bit işlemiyle tam doğrulukla takip edilir."*

Köşegen kapılar ``X`` ile ``Z`` stabilizerlerini birbirine
karıştırmaz; ``Z`` tabanındaki her taban durumu yalnız bir **faz**
kazanır::

    |x⟩  ⟼  ω^{P(x)} |x⟩,     ω = e^{2πi/m},   x ∈ {0,1}ⁿ

ve ``P`` tam sayı katsayılı bir polinomdur::

    P(x) = Σᵢ aᵢxᵢ + Σ_{i<j} b_{ij}xᵢxⱼ + Σ_{i<j<k} c_{ijk}xᵢxⱼx_k  (mod m)

Ardışık iki köşegen faz **değişmelidir**: üsleri ``Z_m``de toplanır.
Yâni yüz faz kapısı, genlik vektörüne yüz kere dokunmak değil, yüz
tamsayı toplamasıdır. ``nefs/qyazmac.py:faz`` bunu böyle yapar ve
biriken üssü ``faz_birikimi()`` ile verir; bu dosya onu polinoma
oturtur.

===================================================================
OTURTMA TAM'DIR -- UYDURMA DEĞİL
===================================================================

``{0,1}ⁿ → Z_m`` olan **her** fonksiyonun altküme (Möbius) açılımı
tektir ve tamdır::

    c_S = Σ_{T ⊆ S} (−1)^{|S|−|T|} k(T)   (mod m)

Dönüşüm birim-üçgenseldir, o hâlde ``Z_m`` üstünde tersinirdir. Yâni
burada bir **en küçük kareler uydurması yoktur**; katsayılar tam
çıkar ve geri dönüşüm (zeta) ``k``yı birebir verir. Ölçülen budur.

**Hüküm derecededir:** ``derece ≤ 3`` ise durum CNOT-Dihedral
sınıfındadır ve tablo dallanmaz. Derece büyükse bu **yazılır**,
örtülmez -- polinom yine tamdır, fakat sınıf iddiası düşer.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, Optional

import numpy as np

__all__ = ["FazAyari", "mobius", "zeta", "faz_oturt", "faz_uygula", "rapor"]

#: Bravyi-Gosset üsteli -- kıyas için (bkz. nefs/matchgate.py).
BRAVYI_GOSSET_ALFA = 0.468


@dataclass
class FazAyari:
    """Faz grubunun ve sınıf iddiasının ölçüleri."""

    #: Faz grubu ``Z_m``. Amy-Maslov-Mosca ``m = 8`` (T mertebesi) için
    #: yazılıdır; ``m`` büyürse faz incelir, teorem değişmez.
    mertebe: int = 8
    #: CNOT-Dihedral sınıfının azamî derecesi. Teoremin kendi haddi 3'tür.
    derece: int = 3


def mobius(k: np.ndarray, m: int) -> np.ndarray:
    """Altküme (Möbius) dönüşümü -- ``Z_m``de, **tam**, ``O(n·2ⁿ)``.

    ``c_S = Σ_{T⊆S} (−1)^{|S|−|T|} k(T)``. Yerinde fark alınarak
    yapılır: ``n`` geçiş, her geçişte ``2ⁿ`` çıkarma.
    """
    c = np.asarray(k, np.int64).copy() % int(m)
    d = c.size
    n = int(round(math.log2(d)))
    assert 1 << n == d, "boy ikinin kuvveti olmalı: %d" % d
    idx = np.arange(d)
    for i in range(n):
        bit = 1 << i
        ust = idx[(idx & bit) != 0]
        c[ust] = (c[ust] - c[ust ^ bit]) % int(m)
    return c


def zeta(c: np.ndarray, m: int) -> np.ndarray:
    """Möbius'un tersi: ``k(S) = Σ_{T⊆S} c_T``. Oturtmayı **sınar**."""
    k = np.asarray(c, np.int64).copy() % int(m)
    d = k.size
    n = int(round(math.log2(d)))
    idx = np.arange(d)
    for i in range(n):
        bit = 1 << i
        ust = idx[(idx & bit) != 0]
        k[ust] = (k[ust] + k[ust ^ bit]) % int(m)
    return k


def faz_oturt(k, ayar: Optional[FazAyari] = None) -> Dict[str, Any]:
    """Biriken faz üssünü polinoma oturt ve **derecesini ölç**.

    ``k`` ``d = 2ⁿ`` uzunluğunda tamsayı dizisidir: ``|x⟩``ın kazandığı
    faz ``ω^{k[x]}``tır. Dönen sözlükte:

    * ``derece``   -- sıfırdan farklı en yüksek dereceli terim.
    * ``tam``      -- ``derece ≤ ayar.derece`` mi (CNOT-Dihedral mi).
    * ``artık``    -- haddi aşan terim sayısı; ``0`` ise sınıf içindedir.
    * ``geri_hata``-- zeta ile geri dönüşün hatası. **0 olmalıdır**;
      değilse oturtma değil, uydurma yapılmış demektir.
    """
    a = ayar or FazAyari()
    m = max(4, int(a.mertebe))
    v = np.asarray(k, np.int64).reshape(-1) % m
    d = v.size
    assert d >= 2, "faz vektörü en az iki elemanlı olmalı"
    n = int(round(math.log2(d)))
    assert 1 << n == d, "faz vektörü boyu ikinin kuvveti olmalı: %d" % d

    c = mobius(v, m)
    geri = zeta(c, m)
    geri_hata = int(np.count_nonzero(geri != v))

    nz = np.nonzero(c)[0]
    if nz.size:
        # Terimin derecesi indisin bit sayısıdır (``x_i`` çarpanları).
        agirlik = np.array([int(bin(int(i)).count("1")) for i in nz])
        derece = int(agirlik.max())
        artik = int(np.count_nonzero(agirlik > int(a.derece)))
    else:
        derece, artik = 0, 0

    # ``t``: hakikaten non-Clifford olan terim sayısı. ``Z_m``de
    # ``m/4``ün katı olan fazlar Clifford'dur (Pauli/S kapıları);
    # T-tipi olanlar değildir. Bravyi-Gosset üsteli **onları** sayar.
    ceyrek = max(1, m // 4)
    t_sayisi = int(np.count_nonzero(c[nz] % ceyrek)) if nz.size else 0
    return {
        "mertebe": m, "boy": int(d), "değişken": n,
        "derece": derece, "terim": int(nz.size),
        "azamî_derece": int(a.derece),
        "tam": bool(derece <= int(a.derece)),
        "artık": artik,
        "geri_hata": geri_hata,
        "katsayı_baytı": int(c.astype(np.int16).nbytes),
        "yoğun_baytı": int(d * 16),
        # Faz polinomu yolunda dallanma daima **birdir**: durum bir
        # tableau ile bir tamsayı dizisidir, stabilizer toplamı değil.
        "dallanma": 1,
        "t_kapısı": t_sayisi,
        "dallanma_kubit": float(2.0 ** min(BRAVYI_GOSSET_ALFA * t_sayisi,
                                           1023.0)),
        "katsayı": c,
    }


def faz_uygula(psi, k, mertebe: int = 8) -> np.ndarray:
    """``|x⟩ ↦ ω^{k(x)}|x⟩`` -- polinomdan genliğe **tek** geçiş.

    Yüz faz kapısı biriktirildikten sonra genliğe **bir kere** dokunmak
    budur; kapı başına dokunmak değil.
    """
    from .galois import ayrik_faz
    m = int(mertebe)
    e = np.asarray(k, np.int64).reshape(-1) % m
    return ayrik_faz(psi, -e * (2.0 * math.pi / m), m)


def rapor(n: int = 12, tohum: int = 0) -> str:           # pragma: no cover
    """Oturtma tam mı, derece ne çıkıyor -- **ölç**."""
    m = 8
    d = 1 << n
    r = np.random.default_rng(int(tohum))
    x = np.arange(d)
    s = ["=== FAZ POLİNOMU -- AMY-MASLOV-MOSCA (2014) ===", "",
         "  Z_%d,  n = %d değişken,  d = %d taban durumu" % (m, n, d), "",
         "  hâl                         derece  terim   tam?   geri hata",
         "  " + "-" * 62]
    # 1. Doğrusal faz: P(x) = Σ aᵢxᵢ -- derece 1 olmalı.
    a = r.integers(0, m, size=n)
    dogrusal = np.zeros(d, np.int64)
    for i in range(n):
        dogrusal += a[i] * ((x >> i) & 1)
    o1 = faz_oturt(dogrusal % m, FazAyari(mertebe=m))
    s.append("  doğrusal (Σaᵢxᵢ)            %6d  %5d   %-5s  %d"
             % (o1["derece"], o1["terim"], o1["tam"], o1["geri_hata"]))
    # 2. İkinci derece: CZ tipi.
    ikinci = dogrusal.copy()
    for i in range(n):
        for j in range(i + 1, n):
            ikinci += int(r.integers(0, m)) * (((x >> i) & 1)
                                               * ((x >> j) & 1))
    o2 = faz_oturt(ikinci % m, FazAyari(mertebe=m))
    s.append("  ikinci derece (CZ)          %6d  %5d   %-5s  %d"
             % (o2["derece"], o2["terim"], o2["tam"], o2["geri_hata"]))
    # 3. Üçüncü derece: CCZ tipi -- teoremin haddi.
    ucuncu = ikinci.copy()
    for i in range(0, n - 2, 3):
        ucuncu += 1 * (((x >> i) & 1) * ((x >> (i + 1)) & 1)
                       * ((x >> (i + 2)) & 1))
    o3 = faz_oturt(ucuncu % m, FazAyari(mertebe=m))
    s.append("  üçüncü derece (CCZ)         %6d  %5d   %-5s  %d"
             % (o3["derece"], o3["terim"], o3["tam"], o3["geri_hata"]))
    # 4. Keyfî faz -- sınıfın DIŞINDA olmalı; ölçü kırmızı yanmalı.
    keyfi = r.integers(0, m, size=d)
    o4 = faz_oturt(keyfi, FazAyari(mertebe=m))
    s.append("  keyfî (rastgele)            %6d  %5d   %-5s  %d"
             % (o4["derece"], o4["terim"], o4["tam"], o4["geri_hata"]))
    s += ["",
          "  ÖLÇÜ KIRMIZI YANABİLİYOR: keyfî faz derece %d verdi ve"
          % o4["derece"],
          "  CNOT-Dihedral sınıfına GİRMEDİ (tam: %s). Yanamayan bir"
          % o4["tam"],
          "  ölçü hiçbir şey ölçmüyor demektir.", "",
          "  DALLANMA:",
          "    faz polinomu yolunda        : %d tablo" % o3["dallanma"],
          "    kübit tabanında (t=%d)      : %.3e stabilizer"
          % (o3["t_kapısı"], o3["dallanma_kubit"]),
          "",
          "  BELLEK (üçüncü derece hâli):",
          "    katsayı dizisi : %d bayt" % o3["katsayı_baytı"],
          "    yoğun faz      : %d bayt" % o3["yoğun_baytı"],
          "",
          "  GERİ DÖNÜŞ HATASI DÖRT HÂLDE DE SIFIR: oturtma bir",
          "  uydurma değil, tam Möbius açılımıdır."]
    return "\n".join(s)


if __name__ == "__main__":                               # pragma: no cover
    print(rapor())
