"""
MORSE-EULER TOPOLOJİK MUHASEBE (K27 katı sağlaması)

    Σ_k (−1)^k M_k  ==  χ(X)

``M_k`` bir Morse fonksiyonunun ``k`` indeksli kritik noktalarının
sayısı, ``χ`` ise uzayın Euler karakteristiğidir. Eşitlik **kimliktir**:
sağlanmıyorsa ya kritik noktalar yanlış sayılmıştır ya da ``χ`` yanlış
hesaplanmıştır; hüküm o hâlde Yakîn'e çıkamaz.

===================================================================
IZGARADA MORSE NEDİR
===================================================================

Bir ARC ızgarası ``f(i,j) = renk`` diye bir yükseklik fonksiyonudur.
Kritik noktalar Banchoff'un ayrık Morse teorisiyle sayılır: her hücre
için dört komşuluğunda ``f``nin işaret değiştirme sayısı ``d``
bakılır::

    d = 0 ve komşular küçük  → asgarî   (M₀)
    d = 0 ve komşular büyük  → azamî    (M₂)
    d = 2                    → eyer     (M₁)
    d > 2                    → maymun eyeri (çoklu, M₁'e d/2−1 katkı)

``χ`` ise ızgara kompleksinin ``köşe − kenar + yüz``üdür ve
**müstakil** hesaplanır; iki hesap birbirini denetlesin diye.

**ÖLÇÜ KIRMIZI YANABİLİR.** Kritik nokta sayımı kasten bozulduğunda
eşitlik düşmelidir; ``tahkik_cetveli`` bunu gösterir.
"""
from __future__ import annotations

from typing import Dict, Tuple

import numpy as np

__all__ = ["euler_karakteristigi", "morse_indisleri",
           "morse_euler_denklik_tahkiki", "tahkik_cetveli"]


def euler_karakteristigi(g: np.ndarray) -> int:
    """Izgaranın **seviye kümesi** kompleksinin ``χ``sı.

    Her renk için o rengin işgal ettiği hücrelerden kurulan kompleksin
    ``V − E + F``si toplanır. Tek bir dolu dikdörtgen için ``χ = 1``
    çıkar (bir disk); bir delik açılırsa ``0`` olur.
    """
    g = np.atleast_2d(np.asarray(g, int))
    H, W = g.shape
    toplam = 0
    for renk in np.unique(g):
        M = (g == renk)
        V = int(M.sum())
        # yatay ve dikey kenarlar
        E = int((M[:, :-1] & M[:, 1:]).sum()) + int((M[:-1] & M[1:]).sum())
        # kare yüzler
        F = int((M[:-1, :-1] & M[:-1, 1:] & M[1:, :-1] & M[1:, 1:]).sum())
        toplam += V - E + F
    return int(toplam)


#: Halka sırası: dik ve çapraz komşular **çevrimsel** dizilir. Sıra
#: şarttır; alt-bağın kenarları ancak ardışık konumlar arasında kurulur.
_HALKA: Tuple[Tuple[int, int], ...] = (
    (-1, 0), (-1, 1), (0, 1), (1, 1),
    (1, 0), (1, -1), (0, -1), (-1, -1),
)


def _alt_bag_chi(ped: np.ndarray, i: int, j: int,
                 f: Dict[Tuple[int, int], float]) -> Tuple[int, int]:
    """``(χ(alt bağ), bağdaki köşe sayısı)`` -- Banchoff'un alt bağı.

    Küpsel komplekste ``v``nin bağı şöyledir: **dik** komşu, işgal
    edilmişse bir kenar verir ve bağa girer; **çapraz** komşu ise ancak
    onu içeren ``2×2`` kare tamamen doluysa (yani bir yüz varsa) bağa
    girer. Bağın kenarı, ardışık (dik, çapraz) çifti aynı yüzü
    paylaşıyorsa vardır.

    Alt bağ, bunların ``f`` değeri ``f(v)``den **küçük** olanlarıdır.
    """
    fv = f[(i, j)]
    var = []
    for t, (dy, dx) in enumerate(_HALKA):
        y, x = i + dy, j + dx
        if not ped[y, x]:
            var.append(False)
            continue
        if dy and dx:                          # çapraz: yüz gerekir
            tam = (ped[i, x] and ped[y, j] and ped[y, x])
            var.append(bool(tam) and f[(y, x)] < fv)
        else:
            var.append(f[(y, x)] < fv)
    kose = sum(1 for v in var if v)
    kenar = 0
    for t in range(8):
        u = (t + 1) % 8
        if not (var[t] and var[u]):
            continue
        # ardışık ikiliden biri çapraz olmalı; ortak yüz odur
        dy1, dx1 = _HALKA[t]
        dy2, dx2 = _HALKA[u]
        cy, cx = (dy1 or dy2), (dx1 or dx2)
        if ped[i + cy, j + cx] and ped[i + cy, j] and ped[i, j + cx]:
            kenar += 1
    return int(kose - kenar), int(kose)


def morse_indisleri(g: np.ndarray) -> Dict[int, int]:
    """Banchoff ayrık Morse sayımı: ``{0: M₀, 1: M₁, 2: M₂}``.

    ``i(v) = 1 − χ(alt bağ)`` ve ``Σ_v i(v) = χ`` **kimliktir**.
    Asgarî: alt bağ boş. Azamî: ``i = 1`` fakat alt bağ dolu. Eyer:
    ``i < 1``; maymun eyeri ``M₁``e birden fazla katkı verir.

    **EVVELKİ SAYIM YANLIŞTI VE ÖLÇÜM YAKALADI.** İndeksi komşuluk
    halkasının işaret değişimlerinden okumuştum; dolu bir 5×6
    dikdörtgende ``Σ(−1)^k M_k = 12`` çıkıyordu, halbuki ``χ = 1``.
    Kusur şuydu: halka, bağ değildir -- bağ ``f``ye göre **alt** kısma
    daraltılmalı ve küpsel komplekste çapraz komşu ancak yüz varsa
    bağa girmelidir.
    """
    g = np.atleast_2d(np.asarray(g, int))
    M = {0: 0, 1: 0, 2: 0}
    for renk in np.unique(g):
        A = (g == renk)
        H, W = A.shape
        ped = np.zeros((H + 2, W + 2), bool)
        ped[1:-1, 1:-1] = A
        # Genel (ties'siz) doğrusal yükseklik: f = satır + ε·sütun
        eps = 1.0 / (W + 2.0)
        f = {(y, x): y + eps * x
             for y in range(H + 2) for x in range(W + 2)}
        for y in range(1, H + 1):
            for x in range(1, W + 1):
                if not ped[y, x]:
                    continue
                chi_l, kose = _alt_bag_chi(ped, y, x, f)
                i_v = 1 - chi_l
                if kose == 0:
                    M[0] += 1                  # asgarî   (i = +1)
                elif i_v == 1:
                    M[2] += 1                  # azamî    (i = +1)
                elif i_v < 0:
                    # Eyer: ``i = −k`` ise ``M₁``e ``k`` katkı verir.
                    # Evvelce ``1 − i_v`` yazılmıştı ve iki yanlış
                    # birden yapıyordu: eyerleri bir fazla sayıyor,
                    # üstelik ``i = 0`` olan **düzenli** noktaları da
                    # eyer sayıyordu. Ölçüldü: dolu 5×6 dikdörtgende
                    # ``Σ(−1)^k M_k = −28`` çıkıyordu, χ = 1 iken.
                    M[1] += (-i_v)
                # i_v == 0 → düzenli nokta, kritik değil, katkısı yok
    return M


def morse_euler_denklik_tahkiki(g: np.ndarray, bozarak: int = 0
                                ) -> Tuple[bool, Dict[str, int]]:
    """``Σ(−1)^k M_k == χ`` mi? ``(doğrulandı, rapor)``.

    ``bozarak`` sıfırdan farklıysa ``M₁``e o kadar sahte kritik nokta
    eklenir; ölçünün **kırmızı yanabildiğini** göstermek içindir ve
    hakikî kullanımda daima sıfırdır.
    """
    g = np.atleast_2d(np.asarray(g, int))
    M = morse_indisleri(g)
    M[1] += int(bozarak)
    morse = M[0] - M[1] + M[2]
    chi = euler_karakteristigi(g)
    return bool(morse == chi), {"M0": M[0], "M1": M[1], "M2": M[2],
                                "morse_toplam": int(morse), "chi": int(chi)}


def tahkik_cetveli() -> Dict[str, object]:
    """Yeşil ve kırmızı yan yana -- ölçü ölçü olabilsin diye."""
    dolu = np.ones((5, 6), int)
    delikli = np.ones((5, 6), int)
    delikli[2, 2] = 2
    satir = []
    for ad, g, bozuk in (("dolu dikdörtgen", dolu, 0),
                         ("delikli", delikli, 0),
                         ("dolu (KASTEN BOZUK)", dolu, 3)):
        ok, r = morse_euler_denklik_tahkiki(g, bozarak=bozuk)
        satir.append({"ad": ad, "tahkik": ok, **r})
    return {"satır": satir}


def rapor() -> str:                                      # pragma: no cover
    c = tahkik_cetveli()
    s = ["MORSE-EULER TOPOLOJİK MUHASEBE   Σ(−1)^k M_k == χ", "",
         "  %-22s %6s %6s %6s %8s %6s %8s"
         % ("hâl", "M0", "M1", "M2", "Σ(−1)^k", "χ", "tahkik")]
    for r in c["satır"]:
        s.append("  %-22s %6d %6d %6d %8d %6d %8s"
                 % (r["ad"], r["M0"], r["M1"], r["M2"],
                    r["morse_toplam"], r["chi"], r["tahkik"]))
    s.append("")
    s.append("  Son satır KASTEN bozuktur ve False çıkmalıdır;")
    s.append("  çıkmazsa ölçü kırmızı yanamıyor demektir (H90).")
    return "\n".join(s)


if __name__ == "__main__":                               # pragma: no cover
    print(rapor())
