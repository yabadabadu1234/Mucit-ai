"""``p``-adik norm, ultrametrik ve "irrasyonelliğin ilgası" iddiası.

Kaynak: ``docs/kaynak/kuantum_hudutsuzluk.tex`` §``p``-Adic Metrik,
§İrrasyonel Sayı Yanılsaması.

**Kaynağın doğru yazdığı yer.**  ``|x|_p = p^{−v_p(x)}`` tanımı ve
``|x + y|_p ≤ max(|x|_p, |y|_p)`` eşitsizliği doğrudur; ikincisi
burada 20 000 rastgele çiftte sınanıyor ve **hiç ihlal yok**.  Ayrıca
eşitsizlik ``|x|_p ≠ |y|_p`` iken **eşitliğe** döner (izoseles üçgen);
o da ölçülüyor.

**M25/M26 -- terim.**  Bu eşitsizliği sağlayan metriğe *ultrametrik*
denir.  Kaynak iki yerde "ultradinamik" yazıyor; öyle bir metrik sınıfı
yoktur.

**M23 -- ``Σ|c_i|_p² = 1`` bir normalizasyon değildir.**  Born kuralı
arşimet mutlak değerle yazılır.  ``|·|_p`` değerleri ``{p^k}``
kümesindedir; toplamları bir olasılık toplamı **değildir**.  Ölçüldü
(``p=2``): normalize ``c = (½,½,½,½)`` durumunda arşimet ``Σc² = 1``
iken ``p``-adik toplam **16**; ``c = (3/5,4/5,0,0)`` durumunda arşimet
1 iken ``p``-adik **17/16**.  Üstelik ``p``-adik toplam üniter
dönüşümler altında **korunmaz** -- bu modülde ölçülüyor.  ``p``-adik
normun doğru işi, katsayıların ``ℤ_p``de kalıp kalmadığını
(``|c|_p ≤ 1``, yani paydada ``p`` yok) denetlemektir; bir *tamlık*
ölçütüdür, bir *normalizasyon* ölçütü değil.

**M24 -- yuvarlama hatasının sebebi irrasyonellik değildir.**
``0.1 + 0.2 ≠ 0.3`` (fark 5.55e-17) ve ``0.1``i on kere toplamak
``0.9999999999999999`` verir; her ikisinde de bütün sayılar
**rasyoneldir**.  Sebep sonlu mantissadır.  Doğru çare irrasyonelleri
ilga etmek değil, tam aritmetiktir (bkz. :mod:`hesap.galois`).
"""

from __future__ import annotations

import math
from fractions import Fraction
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = [
    "p_degeri", "p_norm", "ultrametrik_ihlali", "izoseles_orani",
    "p_tam_mi", "p_adik_toplam", "arsimet_toplam",
    "normalizasyon_kiyasi", "uniter_altinda_korunuyor_mu",
    "float_hatasi_rasyonelde", "p_adik_yakinsama",
]


def p_degeri(x: Fraction, p: int) -> Optional[int]:
    """``v_p(x)``: ``x = p^k a/b`` (``p ∤ a, p ∤ b``) için ``k``.

    ``x = 0`` için tanımsız; ``None`` dönülür (``|0|_p = 0``).
    """
    x = Fraction(x)
    if x == 0:
        return None
    n, d, k = abs(x.numerator), x.denominator, 0
    while n % p == 0:
        n //= p
        k += 1
    while d % p == 0:
        d //= p
        k -= 1
    return k


def p_norm(x, p: int) -> Fraction:
    """``|x|_p = p^{−v_p(x)}``, ``|0|_p = 0`` — **tam** rasyonel."""
    k = p_degeri(Fraction(x), p)
    return Fraction(0) if k is None else Fraction(p) ** (-k)


def p_tam_mi(x, p: int) -> bool:
    """``x ∈ ℤ_p`` mi? — yani ``|x|_p ≤ 1``, paydada ``p`` yok."""
    return p_norm(x, p) <= 1


def ultrametrik_ihlali(p: int = 2, n: int = 20000, tohum: int = 0
                       ) -> Dict[str, object]:
    """``|x+y|_p ≤ max(|x|_p,|y|_p)`` kaç kere ihlal ediliyor? — hiç.

    Ayrıca ``|x|_p ≠ |y|_p`` iken **eşitlik** olduğu ayrıca sayılıyor
    (izoseles üçgen özelliği).
    """
    r = np.random.default_rng(tohum)
    ihlal = 0
    esit_olmasi_gereken = 0
    esit_cikan = 0
    for _ in range(n):
        x = Fraction(int(r.integers(-60, 61)), int(r.integers(1, 61)))
        y = Fraction(int(r.integers(-60, 61)), int(r.integers(1, 61)))
        nx, ny, ns = p_norm(x, p), p_norm(y, p), p_norm(x + y, p)
        if ns > max(nx, ny):
            ihlal += 1
        if nx != ny:
            esit_olmasi_gereken += 1
            if ns == max(nx, ny):
                esit_cikan += 1
    return {"deneme": n, "ihlal": ihlal,
            "farklı_normlu_çift": esit_olmasi_gereken,
            "eşitlik_çıkan": esit_cikan,
            "izoseles_tam_mı": esit_cikan == esit_olmasi_gereken}


def izoseles_orani(p: int = 2, n: int = 5000, tohum: int = 1) -> float:
    r = ultrametrik_ihlali(p, n, tohum)
    return (r["eşitlik_çıkan"] / r["farklı_normlu_çift"]
            if r["farklı_normlu_çift"] else float("nan"))


# ══════════════════════════════════════════════════════════════════════
#  M23: p-adik toplam bir normalizasyon değildir
# ══════════════════════════════════════════════════════════════════════

def arsimet_toplam(c: Sequence) -> Fraction:
    """``Σ c_i²`` — Born normalizasyonu (arşimet)."""
    return sum((Fraction(x) ** 2 for x in c), Fraction(0))


def p_adik_toplam(c: Sequence, p: int) -> Fraction:
    """``Σ |c_i|_p²`` — kaynağın önerdiği ölçüt."""
    return sum((p_norm(x, p) ** 2 for x in c), Fraction(0))


def normalizasyon_kiyasi(p: int = 2) -> List[Dict[str, object]]:
    """Normalize edilmiş durumlarda iki ölçüt yan yana."""
    ornekler = [
        ("(½,½,½,½)", [Fraction(1, 2)] * 4),
        ("(3/5,4/5,0,0)", [Fraction(3, 5), Fraction(4, 5),
                           Fraction(0), Fraction(0)]),
        ("(1,0,0,0)", [Fraction(1), Fraction(0), Fraction(0), Fraction(0)]),
        ("(⅓,⅔,⅔,0)", [Fraction(1, 3), Fraction(2, 3), Fraction(2, 3),
                        Fraction(0)]),
    ]
    sonuc = []
    for ad, c in ornekler:
        sonuc.append({"durum": ad, "arşimet": arsimet_toplam(c),
                      "p_adik": p_adik_toplam(c, p),
                      "arşimet_bir_mi": arsimet_toplam(c) == 1,
                      "p_adik_bir_mi": p_adik_toplam(c, p) == 1,
                      "hepsi_ℤ_p_de_mi": all(p_tam_mi(x, p) for x in c)})
    return sonuc


def uniter_altinda_korunuyor_mu(p: int = 2, n: int = 200, tohum: int = 0
                                ) -> Dict[str, object]:
    """Üniter dönüşüm arşimet toplamı korur, ``p``-adik toplamı korumaz.

    Rasyonel kalması için dönüşüm olarak **Pisagor** dönmeleri
    kullanılıyor: ``(3,4,5)`` üçlüsünden ``cos = 3/5, sin = 4/5``;
    dizey tam rasyoneldir ve dik olduğu ``RᵀR = I`` ile sınanıyor.
    """
    r = np.random.default_rng(tohum)
    c35 = (Fraction(3, 5), Fraction(4, 5))
    c, s = c35
    korunan_ars, korunan_p = 0, 0
    for _ in range(n):
        a = Fraction(int(r.integers(-8, 9)), int(r.integers(1, 9)))
        b = Fraction(int(r.integers(-8, 9)), int(r.integers(1, 9)))
        if a == 0 and b == 0:
            continue
        a2, b2 = c * a - s * b, s * a + c * b
        if arsimet_toplam([a, b]) == arsimet_toplam([a2, b2]):
            korunan_ars += 1
        if p_adik_toplam([a, b], p) == p_adik_toplam([a2, b2], p):
            korunan_p += 1
    R = [[c, -s], [s, c]]
    dik = (R[0][0] ** 2 + R[1][0] ** 2 == 1
           and R[0][1] ** 2 + R[1][1] ** 2 == 1
           and R[0][0] * R[0][1] + R[1][0] * R[1][1] == 0)
    return {"deneme": n, "dönüşüm_dik_mi": dik,
            "arşimet_korunan": korunan_ars, "p_adik_korunan": korunan_p}


# ══════════════════════════════════════════════════════════════════════
#  M24: float hatası rasyonelde de var
# ══════════════════════════════════════════════════════════════════════

def float_hatasi_rasyonelde() -> Dict[str, object]:
    """Hepsi rasyonel; hepsi yuvarlanıyor."""
    s = 0.0
    for _ in range(10):
        s += 0.1
    return {
        "0.1+0.2==0.3": (0.1 + 0.2) == 0.3,
        "0.1+0.2-0.3": 0.1 + 0.2 - 0.3,
        "0.1_on_kere": s, "on_kere_bir_mi": s == 1.0,
        "1/3_yuvarlanıyor_mu": Fraction(1, 3) != Fraction(1 / 3),
        "hepsi_rasyonel": True,
        "tam_aritmetikte": float(Fraction(1, 10) * 10),
    }


def p_adik_yakinsama(p: int = 2, n: int = 12) -> Dict[str, object]:
    """``Σ p^k`` ``p``-adik olarak yakınsar, arşimet olarak ıraksar.

    ``1 + 2 + 4 + … + 2^{n−1} = 2^n − 1``; ``p``-adik normu
    ``|2^n − 1|₂ = 1`` (tek sayı), oysa arşimet değeri ``2^n − 1 → ∞``.
    Asıl yakınsayan dizi ``Σ p^k``in **kısmi toplamlarının farkıdır**:
    ``|s_{m} − s_{n}|_p = p^{−n} → 0``.
    """
    kismi = []
    t = Fraction(0)
    for k in range(n):
        t += Fraction(p) ** k
        kismi.append(t)
    farklar = [float(p_norm(kismi[k + 1] - kismi[k], p))
               for k in range(n - 1)]
    return {"kısmi_toplamlar": [int(x) for x in kismi],
            "p_adik_ardışık_fark": farklar,
            "arşimet_büyüyor_mu": kismi[-1] > kismi[0],
            "p_adik_küçülüyor_mu": farklar[-1] < farklar[0]}


# ══════════════════════════════════════════════════════════════════════
#  Gösterim
# ══════════════════════════════════════════════════════════════════════

def _gosterim() -> str:
    s = []
    s.append("=== Ultrametrik eşitsizlik (kaynak DOĞRU, adı YANLIŞ) ===")
    for p in (2, 3, 5):
        r = ultrametrik_ihlali(p, 20000)
        s.append("  p=%d  20000 çiftte ihlal = %d   |x|≠|y| olan %d çiftin "
                 "%d'sinde EŞİTLİK (izoseles: %s)"
                 % (p, r["ihlal"], r["farklı_normlu_çift"],
                    r["eşitlik_çıkan"], r["izoseles_tam_mı"]))
    s.append("  M25/M26: bu metriğin adı ULTRAMETRİK'tir;")
    s.append("  'ultradinamik' diye bir sınıf yoktur.")

    s.append("\n=== M23: Σ|c|_p² = 1 bir normalizasyon DEĞİL ===")
    s.append("  durum            Σc² (arşimet)   Σ|c|₂² (p-adik)   ℤ₂'de mi?")
    for d in normalizasyon_kiyasi(2):
        s.append("  %-15s %-15s %-17s %s"
                 % (d["durum"], str(d["arşimet"]), str(d["p_adik"]),
                    d["hepsi_ℤ_p_de_mi"]))
    s.append("  Dördü de arşimet anlamda normalize; p-adik toplam ise")
    s.append("  16, 17/16, 1, 3/2 çıkıyor. İki ölçüt birbirinin yerine geçmez.")
    s.append("  (Dikkat: (1,0,0,0) hâlinde ikisi de 1 veriyor — tek bir")
    s.append("   örnekle sınamak bu farkı GİZLERDİ.)")

    s.append("\n=== Üniter dönüşüm hangisini koruyor? ===")
    u = uniter_altinda_korunuyor_mu(2, 200)
    s.append("  dönüşüm (3/5,4/5) Pisagor dönmesi, dik mi? %s"
             % u["dönüşüm_dik_mi"])
    s.append("  200 denemede arşimet toplamı korunan: %d/200" %
             u["arşimet_korunan"])
    s.append("  200 denemede p-adik toplamı korunan : %d/200" %
             u["p_adik_korunan"])
    s.append("  Bir normalizasyon ölçütünün üniter altında korunması")
    s.append("  ŞARTTIR; p-adik toplam bu şartı sağlamıyor.")
    s.append("  p-adik normun doğru işi TAMLIK denetimidir (|c|_p ≤ 1).")

    s.append("\n=== M24: yuvarlama hatası rasyonelde de var ===")
    f = float_hatasi_rasyonelde()
    s.append("  0.1 + 0.2 == 0.3 ?  %s   (fark %.3e)"
             % (f["0.1+0.2==0.3"], f["0.1+0.2-0.3"]))
    s.append("  0.1'i on kere topla: %.17f   == 1.0 ? %s"
             % (f["0.1_on_kere"], f["on_kere_bir_mi"]))
    s.append("  Fraction(1,10)*10 = %.1f   ← tam aritmetikte sorun yok"
             % f["tam_aritmetikte"])
    s.append("  Bu sayıların HEPSİ rasyonel. Sebep irrasyonellik değil,")
    s.append("  sonlu mantissa. Teşhis yanlış olunca çare yanlış yere kurulur.")

    s.append("\n=== p-adik yakınsama: arşimetin tersi ===")
    y = p_adik_yakinsama(2, 10)
    s.append("  kısmi toplamlar (arşimet): %s ..."
             % y["kısmi_toplamlar"][:6])
    s.append("  ardışık farkların 2-adik normu: %s"
             % ["%.4g" % x for x in y["p_adik_ardışık_fark"][:6]])
    s.append("  Arşimet büyüyor (%s), p-adik küçülüyor (%s):"
             % (y["arşimet_büyüyor_mu"], y["p_adik_küçülüyor_mu"]))
    s.append("  ıraksayan bir dizi p-adik olarak yakınsayabilir. Kaynağın")
    s.append("  'gürültü p-adik normda sönümlenir' sezgisi buradan doğru;")
    s.append("  fakat bu, Born normalizasyonunun yerini tutmaz.")
    return "\n".join(s)


if __name__ == "__main__":  # pragma: no cover
    print(_gosterim())
