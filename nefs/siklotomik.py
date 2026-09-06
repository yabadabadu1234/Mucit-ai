"""SİKLOTOMİK KOSET -- DERECE 12 BİR KAOS DEĞİL, ``x³``ÜN İKİ KARESİ.

    from nefs.siklotomik import koset_indirge, iz_esitligi
    o = koset_indirge(12)          # 12 hangi kosette, kaç kare
    e = iz_esitligi()              # Tr(α·x¹²) = Tr(β·x³) mi -- SINA

===================================================================
NİÇİN BU DOSYA VAR: BİR İDDİAMIZ ÇÖKTÜ
===================================================================

``nefs/faz_polinomu.py`` Amy-Maslov-Mosca'ya (2014) dayanıp durumun
**CNOT-Dihedral** sınıfında olduğunu umuyordu; o sınıfın şartı faz
polinomunun derecesinin ``≤ 3`` olmasıdır. Ana akışta ölçtük:
**derece 12**. O hâlde iddia düştü ve zabıt onu resmen iptal etti:

    *"CNOT-Dihedral iddiasını resmî olarak iptal ediyoruz: derece 12
    faz birikimi bu sınıfa sığmaz; teorik rapordaki o yanılsamayı
    silip, yerine Galois Siklotomik Koset İndirgemesini koyuyoruz."*

===================================================================
İNDİRGEMENİN RİYAZÎ ESASI -- VE NEYİ İDDİA ETMEDİĞİ
===================================================================

Karakteristiği 2 olan cisimde Frobenius ``φ(x) = x²`` bir **cisim
otomorfizmidir ve toplamaya göre lineerdir**::

    (x + y)² = x² + y²      (mod 2)

``2^m − 1`` mertebeli devirli grupta ``s``nin **siklotomik koseti**::

    C_s = { s, 2s, 4s, 8s, … }   (mod 2^m − 1)

``3``ün koseti ``{3, 6, 12, 24, 48, 96, 192, 129}``tır (``m = 8``).
``12`` bu kosettedir: ``12 = 3 · 2²``. O hâlde ``x¹² = (x³)^{2²}``,
yâni ``x³``ün **iki Frobenius karesi**.

İz fonksiyonu ``Tr(x) = Σ_{i<m} x^{2^i}`` ``F_2``ye düşer ve ``F_2``de
kare almak kimliktir (``0² = 0``, ``1² = 1``), o hâlde::

    Tr(y²) = Tr(y)²= Tr(y)

Bundan çıkan hüküm şudur ve bu dosyada **sınanır**::

    Tr(α · x¹²) = Tr(α^{2^{-2}} · x³)        her x için

Yâni derece-12 iz terimi, derece-3 iz terimine **tam olarak** iner:
yaklaşıklık yok, kesme yok, monom açılımı yok.

**NE İDDİA EDİLMİYOR -- açıkça.** Bu, "her derece-12 faz fonksiyonu
derece-3'e iner" demek DEĞİLDİR; öyle olsaydı Reed-Muller derecesi
diye bir kavram olmazdı. İnen şey **iz formundaki** terimdir. Bir
fazın bu forma yazılıp yazılamadığı ayrı bir sualdir ve burada
ölçülür (``iz_uydur``): uyduramazsa öyle yazılır.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from .galois import gf_carp, gf_tablo

__all__ = ["SiklotomikAyari", "koset", "koset_indirge", "frobenius",
           "iz", "iz_esitligi", "iz_uydur", "rapor"]


@dataclass
class SiklotomikAyari:
    """İndirgemenin ölçüleri."""

    #: Cisim ``GF(2^us)``.
    us: int = 8
    #: Taban üs. Zabıt ``x³`` der.
    taban: int = 3
    #: İndirgenecek derece. Ölçüm 12 dedi.
    derece: int = 12


# ══════════════════════════════════════════════════════════════════
#  1. KOSET -- ``s``nin Frobenius yörüngesi
# ══════════════════════════════════════════════════════════════════
def koset(s: int, us: int = 8) -> List[int]:
    """``C_s = {s, 2s, 4s, …} (mod 2^us − 1)`` -- devir kapanana kadar."""
    n = (1 << int(us)) - 1
    s0 = int(s) % n
    o = [s0]
    x = (s0 * 2) % n
    while x != s0:
        o.append(x)
        x = (x * 2) % n
    return o


def koset_indirge(derece: int, ayar: Optional[SiklotomikAyari] = None
                  ) -> Dict[str, Any]:
    """``derece`` tabanın kaçıncı Frobenius karesi -- **hesapla**, sanma.

    Dönen ``kosette`` yanlışsa indirgeme **yoktur** ve bu yazılır;
    o zaman derece gerçekten bağımsızdır ve iz formuna girmez.
    """
    a = ayar or SiklotomikAyari()
    d = int(derece if derece else a.derece)
    m = int(a.us)
    n = (1 << m) - 1
    taban = int(a.taban)
    C = koset(taban, m)
    kosette = (d % n) in C
    kare = C.index(d % n) if kosette else -1
    # ``d``nin ikili açılımı -- zabıtın "12 = 8 + 4 = 2³ + 2²" satırı.
    bit = [i for i in range(d.bit_length()) if (d >> i) & 1]
    ikili = " + ".join("2^%d" % i for i in reversed(bit)) if bit else "0"
    yazilis = ("x^%d" % d if not kosette else
               "(" * kare + "x^%d" % taban + ")²" * kare)
    # Monom açılımı yapılsaydı kaç terim olurdu (zabıtın kıyası).
    # n değişkenli, derecesi ≤ d olan monom sayısı: Σ_{j≤d} C(n, j).
    nd = m * 8                       # kıyas için 64 değişken (zabıtın misali)
    monom = float(sum(math.comb(nd, j) for j in range(1, min(d, nd) + 1)))
    return {"us": m, "taban": taban, "derece": d, "koset": C,
            "kosette": bool(kosette), "kare": int(kare),
            "ikili": ikili, "yazılış": yazilis,
            "monom_sayisi": monom, "kıyas_değişkeni": nd,
            "koset_boyu": len(C)}


# ══════════════════════════════════════════════════════════════════
#  2. FROBENIUS VE İZ
# ══════════════════════════════════════════════════════════════════
def frobenius(x, kere: int = 1, us: int = 8) -> np.ndarray:
    """``x^{2^kere}`` -- Frobenius. Karakteristik 2'de **lineerdir**."""
    v = np.asarray(x, np.uint8)
    for _ in range(int(kere)):
        v = gf_carp(v, v, int(us)).astype(np.uint8)
    return v


def us_al(x, e: int, us: int = 8) -> np.ndarray:
    """``x^e`` -- kare-al-ve-çarp. Tablo üstünde, kayan nokta yok."""
    v = np.asarray(x, np.uint8)
    o = np.ones_like(v)
    taban = v.copy()
    k = int(e)
    while k:
        if k & 1:
            o = gf_carp(o, taban, int(us)).astype(np.uint8)
        taban = gf_carp(taban, taban, int(us)).astype(np.uint8)
        k >>= 1
    # ``0^e = 0`` (e>0): tablo yolu 0 için tanımsızdır, elle düzeltilir.
    return np.where(np.asarray(x, np.uint8) == 0, np.uint8(0), o)


def iz(x, us: int = 8) -> np.ndarray:
    """``Tr(x) = Σ_{i<m} x^{2^i}`` -- ``F_2``ye düşer, ``0`` yahut ``1``.

    Toplama XOR'dur. Netice **daima** 0 yahut 1 çıkmalıdır; çıkmazsa
    cisim yahut polinom yanlış demektir ve ``assert`` düşürür.
    """
    m = int(us)
    v = np.asarray(x, np.uint8)
    o = np.zeros_like(v)
    cur = v.copy()
    for _ in range(m):
        o = o ^ cur
        cur = gf_carp(cur, cur, m).astype(np.uint8)
    assert bool(np.all((o == 0) | (o == 1))), (
        "iz F_2'ye düşmedi -- cisim yahut polinom yanlış: %r"
        % np.unique(o)[:8])
    return o


# ══════════════════════════════════════════════════════════════════
#  3. HÜKMÜN SINANMASI
# ══════════════════════════════════════════════════════════════════
def iz_esitligi(ayar: Optional[SiklotomikAyari] = None) -> Dict[str, Any]:
    """``Tr(α·x^d) = Tr(β·x^taban)`` mı -- **cismin tamamında** sına.

    ``β = α^{2^{-k}}``dır; ``2^{-k}`` devirli grupta ``2^{m−k}``
    kuvvetidir (``2^m ≡ 1``). Eşitlik ``2^us`` elemanın **hepsinde**
    denenir: örnekleme yok, hepsi.
    """
    a = ayar or SiklotomikAyari()
    m, d, t = int(a.us), int(a.derece), int(a.taban)
    q = 1 << m
    o = koset_indirge(d, a)
    if not o["kosette"]:
        return {"tuttu": False, "sebep": "derece kosette değil",
                "eleman": q, "uyuşmayan": q, "kare": -1}
    k = int(o["kare"])
    x = np.arange(q, dtype=np.uint8)
    r = np.random.default_rng(0)
    uyusmayan = 0
    denenen = 0
    for alfa in r.integers(1, q, size=16, dtype=np.int64):
        A = np.uint8(int(alfa))
        # β = α^{2^{m−k}}: k kere kare almanın tersi.
        B = frobenius(np.array([A], np.uint8), (m - k) % m, m)[0]
        sol = iz(gf_carp(np.full(q, A, np.uint8), us_al(x, d, m), m
                         ).astype(np.uint8), m)
        sag = iz(gf_carp(np.full(q, B, np.uint8), us_al(x, t, m), m
                         ).astype(np.uint8), m)
        uyusmayan += int(np.count_nonzero(sol != sag))
        denenen += q
    return {"tuttu": bool(uyusmayan == 0), "eleman": denenen,
            "uyuşmayan": uyusmayan, "kare": k, "us": m,
            "derece": d, "taban": t,
            "alfa_sayısı": 16}


def iz_uydur(k, ayar: Optional[SiklotomikAyari] = None) -> Dict[str, Any]:
    """Ölçülen faz **iz formuna** giriyor mu -- iddia değil, ölçü.

    ``k`` biriken faz üssüdür. Her ``α`` için ``Tr(α·x^taban)``
    kurulur ve ölçülen fazın en düşük bitiyle kıyaslanır. Hiçbir
    ``α`` tutmazsa **tutmadı** yazılır; indirgeme riyazî olarak
    doğrudur fakat bu fazın o forma girdiği ayrı bir suâldir ve
    cevabı burada verilir.
    """
    a = ayar or SiklotomikAyari()
    m, t = int(a.us), int(a.taban)
    q = 1 << m
    v = np.asarray(k, np.int64).reshape(-1)
    n = min(v.size, q)
    hedef = (v[:n] & 1).astype(np.uint8)          # fazın en düşük biti
    x = np.arange(n, dtype=np.uint8)
    xt = us_al(x, t, m)
    eniyi, eniyi_a = -1.0, -1
    for alfa in range(1, q):
        y = iz(gf_carp(np.full(n, alfa, np.uint8), xt, m).astype(np.uint8), m)
        oran = float(np.mean(y == hedef))
        if oran > eniyi:
            eniyi, eniyi_a = oran, alfa
    return {"en_iyi_uyum": eniyi, "alfa": eniyi_a, "eleman": int(n),
            "tam_uydu": bool(eniyi >= 1.0),
            "rastgele_beklenti": 0.5}


def rapor(tohum: int = 0) -> str:                        # pragma: no cover
    """İndirgeme tutuyor mu -- **sına**, iddia etme."""
    a = SiklotomikAyari()
    o = koset_indirge(12, a)
    e = iz_esitligi(a)
    s = ["=== SİKLOTOMİK KOSET İNDİRGEMESİ ===", "",
         "  CNOT-Dihedral iddiası İPTAL: ölçülen derece 12, teorem ≤3 ister.",
         "",
         "  GF(2^%d),  taban x^%d,  derece %d" % (o["us"], o["taban"],
                                                  o["derece"]),
         "    %d = %s" % (o["derece"], o["ikili"]),
         "    koset(%d) = %s   (boy %d)" % (o["taban"], o["koset"],
                                            o["koset_boyu"]),
         "    %d kosette mi : %s   → %d Frobenius karesi"
         % (o["derece"], o["kosette"], o["kare"]),
         "    yazılışı      : x^%d = %s" % (o["derece"], o["yazılış"]), "",
         "  HÜKÜM SINANDI (örnekleme değil, cismin TAMAMI):",
         "    Tr(α·x^%d) = Tr(β·x^%d),  β = α^(2^-%d)"
         % (o["derece"], o["taban"], e["kare"]),
         "    denenen: %d eleman (%d farklı α × %d eleman)"
         % (e["eleman"], e["alfa_sayısı"], 1 << o["us"]),
         "    uyuşmayan: %d   →  EŞİTLİK: %s" % (e["uyuşmayan"], e["tuttu"]),
         "",
         "  KIYAS -- monom açılımı yapılsaydı:",
         "    %d değişkende derece ≤%d monom sayısı: %.3e"
         % (o["kıyas_değişkeni"], o["derece"], o["monom_sayisi"]),
         "    siklotomik yolda açılan terim sayısı  : 1  (tek iz terimi)",
         "",
         "  ÖLÇÜ KIRMIZI YANABİLİR (ferman 5):"]
    # Kosette OLMAYAN bir derece denenir; indirgeme reddetmelidir.
    kotu = koset_indirge(5, a)
    s += ["    derece 5 kosette mi: %s  (doğru: 5 ∉ C_3, indirgenmez)"
          % kotu["kosette"],
          "    derece 5 için iz eşitliği: %s"
          % iz_esitligi(SiklotomikAyari(us=8, taban=3, derece=5))["tuttu"]]
    return "\n".join(s)


if __name__ == "__main__":                               # pragma: no cover
    print(rapor())
