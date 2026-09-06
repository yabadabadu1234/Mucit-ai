"""KARARNAME -- durumun Clifford çerçevesine ne kadar yakın olduğu.

    k = kararname(psi, mertebe=8)
    k["chi"]            # χ_stab -- kaç stabilizer durumu lâzım
    k["clifforda_yakın"]

===================================================================
ZABITIN 2. USULÜ (Saf CPU 2026 Mimarisi)
===================================================================

    *"Qudit uzayında genelleştirilmiş Pauli grubu (X_d, Z_d) ve Clifford
    kapıları altında durumlar üstel bellek gerektirmez; yalnızca O(N²)
    büyüklüğünde bir Stabilizer Tablosu (Tableau) ile polinom zamanda
    tam doğrulukla simüle edilir... Herhangi bir keyfî durum |Ψ⟩,
    en az sayıda stabilizer durumunun süperpozisyonu (Stabilizer Rank:
    χ_stab) olarak temsil edilir."*

    *"Stabilizer tablosu üzerinde Clifford kapılarını çalıştırmak matris
    çarpımı değil; saf bit seviyesinde XOR, AND ve modulo-d tamsayı
    aritmetiğidir!"*

===================================================================
NİÇİN "KARARNAME": HÜKMÜ NE VERİR
===================================================================

Bu uzuv bir **karar** verir ve o kararın adı dosyaya yazılıdır:
*bu durum bit aritmetiğiyle taşınabilir mi, taşınamaz mı?*

``χ_stab`` küçükse (durum birkaç stabilizer durumunun toplamıysa)
yazmaç yoğun ``ℂ^d`` yerine bir **tableau** ile taşınabilir ve bütün
kapılar XOR/AND'e iner. Büyükse taşınamaz ve yoğun hat kalır.

===================================================================
NASIL ÖLÇÜLÜR (ve ne kadarı ölçülür)
===================================================================

Tam ``χ_stab``ı bulmak NP-zordur; burada **alt sınır değil üst sınır**
aranır ve nasıl arandığı yazılıdır:

1. Qudit Weyl-Heisenberg tabanı kurulur: ``|φ_{a,b}⟩`` durumları
   ``Z^a X^b`` yörüngesinden çıkar (``d`` seviyeli genelleştirilmiş
   Pauli). Bunlar stabilizer durumlarıdır.
2. ``mertebe`` kadar taban durumu **açgözlü ortogonal izdüşümle**
   seçilir: her adımda kalıntıyı en çok azaltan taban alınır (matching
   pursuit).
3. ``χ`` = kalıntının eşiğin altına indiği adım sayısıdır.

**NE İDDİA EDİLMİYOR.** Bu, ``χ_stab``ın kendisi değil, seçilen taban
ailesi içindeki **üst sınırıdır**; başka bir Clifford çerçevesinde daha
küçük çıkabilir. Açgözlü seçim de en iyiyi garanti etmez. İkisi de
saklanmıyor: dönen sözlükte ``üst_sınır`` diye yazılı.

**BU DOSYA KARAR MERCİİDİR, MOTOR DEĞİLDİR** ve öyle olması
kasıtlıdır: kapılar ``nefs/tdd.py``nin graf motorunda vurulur. Kararname
o motora *hangi temsille* gidileceğini söyler -- ``χ`` küçükse durum
zaten graf motorunda birkaç düğüme çöker (ikisi de aynı yapıyı, özdeş
alt blokları, kullanır). Yâni burada ikinci bir motor yoktur; tek motor
vardır ve bu, onun karar mercii.
"""
from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

import numpy as np

__all__ = ["kararname", "rapor"]


# ``weyl_tabani`` İMHA EDİLDİ: rastgele havuz kuruyordu ve aday
# analitik bulunduğu için (bkz. ``kararname``) çağıranı kalmadı.
# Çağrılmayan bir fonksiyonu "ileride lâzım olur" diye bırakmak,
# yasaklanan yarım iştir.

def kararname(psi, mertebe: int = 8, esik: float = 1e-3,
              tohum: int = 0) -> Dict[str, Any]:
    """``χ_stab``ın ÜST SINIRI -- durum bit aritmetiğine iner mi?

    Açgözlü ortogonal izdüşüm (matching pursuit): her adımda kalıntıyı
    en çok azaltan stabilizer durumu seçilir ve kalıntıdan çıkarılır.

    ``mertebe = 0`` ile kapatılır ve karar verilmez -- ölçü kırmızı
    yanabilir.
    """
    v = np.asarray(psi, complex).reshape(-1)
    d = int(v.size)
    assert d >= 2, "karar verilecek durum en az iki genlikli olmalı"
    nrm = float(np.linalg.norm(v))
    assert nrm > 0.0, "BOŞ durum hakkında karar verilemez"
    v = v / nrm
    if int(mertebe) <= 0:
        return {"chi": 0, "örtüşme": 0.0, "üst_sınır": True,
                "clifforda_yakın": False, "kalıntı": 1.0,
                "aday": 0, "kapalı": True}

    # **ADAY RASTGELE SEÇİLMEZ, ANALİTİK BULUNUR.**
    #
    # Evvelce havuz ``weyl_tabani`` ile **rastgele** dolduruluyordu ve
    # ölçüm onu yalanladı: ``|5⟩`` saf bir stabilizer durumu olduğu
    # hâlde örtüşme ``0,031`` çıkıyordu -- çünkü 256 taban arasından
    # ``|5⟩``i rastgele tutturma şansı ``1/256``dır. Açgözlü seçim
    # doğruydu, havuz yanlıştı.
    #
    # İki stabilizer ailesinin en iyi adayı **kapalı formda** bilinir:
    #   Z özdurumları (taban)   : argmax_j |ψ_j|
    #   X özdurumları (Fourier) : argmax_j |(Fψ)_j|
    # Her adımda ikisi de hesaplanır ve büyüğü alınır. ``O(d log d)``
    # ve o iki aile içinde **kesin en iyisi**.
    kalinti = v.copy()
    secilen: List[int] = []
    kats: List[complex] = []
    jj = np.arange(d)
    for _ in range(int(mertebe)):
        # Z ailesi: taban vektörleri |j⟩
        iz = int(np.argmax(np.abs(kalinti)))
        c_z = complex(kalinti[iz])
        # X ailesi: Fourier vektörleri ω^{aj}/√d
        F = np.fft.fft(kalinti) / math.sqrt(d)
        ix = int(np.argmax(np.abs(F)))
        c_x = complex(np.conj(F[ix]))
        if abs(c_z) >= abs(c_x):
            if abs(c_z) < 1e-12:
                break
            taban = np.zeros(d, complex)
            taban[iz] = 1.0
            kat = c_z
        else:
            if abs(c_x) < 1e-12:
                break
            taban = np.exp(2j * math.pi * ix * jj / d) / math.sqrt(d)
            kat = complex(np.vdot(taban, kalinti))
        secilen.append(iz if abs(c_z) >= abs(c_x) else (d + ix))
        kats.append(kat)
        kalinti = kalinti - kat * taban
        if float(np.linalg.norm(kalinti)) < float(esik):
            break
    kal = float(np.linalg.norm(kalinti))
    ortusme = float(max(0.0, 1.0 - kal ** 2))
    return {"chi": len(secilen), "örtüşme": ortusme,
            "kalıntı": kal, "aday": 2 * d,
            "üst_sınır": True, "kapalı": False,
            "clifforda_yakın": bool(kal < float(esik)),
            "katsayı": np.asarray(kats, complex)}


def rapor(d: int = 256, tohum: int = 0) -> str:          # pragma: no cover
    """Hangi durum Clifford'a yakın, hangisi değil -- **ölç**."""
    r = np.random.default_rng(int(tohum))
    j = np.arange(d)
    haller = {
        "taban |5⟩ (stabilizer)": np.eye(1, d, 5, dtype=complex).reshape(-1),
        "Fourier |+⟩ (stabilizer)": np.exp(2j * math.pi * 3 * j / d)
        / math.sqrt(d),
        "iki stabilizer toplamı": (np.eye(1, d, 5, dtype=complex).reshape(-1)
                                   + np.exp(2j * math.pi * 3 * j / d)
                                   / math.sqrt(d)),
        "gürültü (Haar)": r.normal(size=d) + 1j * r.normal(size=d),
    }
    s = ["=== KARARNAME -- stabilizer rank üst sınırı ===", "",
         "  d = %d   mertebe haddi = 8" % d, ""]
    for ad, v in haller.items():
        v = np.asarray(v, complex).reshape(-1)
        v = v / (np.linalg.norm(v) or 1.0)
        k = kararname(v, mertebe=8, tohum=tohum)
        s.append("  %-26s χ ≤ %2d   örtüşme %.6f   kalıntı %.2e   "
                 "Clifford'a yakın: %s"
                 % (ad, k["chi"], k["örtüşme"], k["kalıntı"],
                    k["clifforda_yakın"]))
    s += ["", "  Gürültüde χ küçük ÇIKMAZ ve bu gizlenmiyor: keyfî bir",
          "  durum Clifford çerçevesine oturmaz. χ bir vaat değil,",
          "  durumun yapısının neticesidir. Ayrıca dönen sayı χ'nin",
          "  kendisi değil ÜST SINIRIDIR (açgözlü seçim, sabit aile)."]
    return "\n".join(s)


if __name__ == "__main__":                               # pragma: no cover
    print(rapor())
