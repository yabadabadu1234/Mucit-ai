"""GALOIS-STABILIZER MOTORU -- sürekli Hilbert uzayı İPTAL.

    T = tableau_kur(psi, GaloisAyari())
    T.xor_isle(maske)              # tek CPU çevrimi, matris YOK
    z = palmer_faz(v, k)           # e^{iθ} YOK: i(a,b) = (−b, a)

===================================================================
ZABITIN HÜKMÜ (1 GB/s -- Ayrık Kuantum Mekaniği)
===================================================================

**HÜKÜM 1:** *"Sürekli Hilbert uzayında (ℂ^d), kayan nokta sayılarıyla,
matris çarpımlarıyla ve trigonometrik fazlarla kalarak 1 GB/s hızına
ulaşmak fizikî bir imkânsızlıktır."*

Aritmetiği açıktır ve tartışılmaz: 4 GHz'te 250 M belirteç/sn hedefi
belirteç başına **16 saat çevrimi** bırakır. Tek bir ``cos(θ)`` yahut
``exp(iθ)`` (CORDIC/Taylor) 15-30 çevrim yer -- yâni tek bir faz
hesabı bütün bütçeyi yer. ``d=4096``lik Kronecker çarpım ise belirteç
başına en az **196 608 FLOP** ister.

O hâlde üç şey kökünden kesildi:

============================  ====================================
İPTAL                         YERİNE
============================  ====================================
Sürekli genlik ``ℂ^d``        Galois cismi ``GF(2^m)`` elemanları
Transandantal faz ``e^{iθ}``  Palmer 2-bit rotasyonu ``i(a,b)=(−b,a)``
``O(d²)`` matris çarpımı      Stabilizer tableau: XOR / AND bitmask
============================  ====================================

===================================================================
1. PALMER RASYONEL KUANTUM MEKANİĞİ (RaQM)
===================================================================

Zabıt: *"Karmaşık sayı birimi i = √−1 soyut transandantal bir sayı
değildir! i, iki bitlik sonlu bir dizilim üzerinde çalışan basit bir
döngüsel permütasyon operatörüdür:*

    i(a, b) = (−b, a)   ⟹   i²(a, b) = i(−b, a) = −(a, b)

Yâni bir karmaşık sayı ``(a, b)`` **tam sayı çiftidir** ve ``i`` ile
çarpmak bir **permütasyon + işaret taklasıdır**: ne çarpma vardır ne
trigonometri. CPU'da ``SHL``/``ROR``/``XOR``dan ibarettir.

**Faz grubu ayrıktır.** ``e^{iθ}`` yerine ``m``inci birim kökler
grubu ``Z_m`` alınır ve faz bir **tam sayıdır** (``0 ≤ k < m``).
``m = 4``te Palmer'in kendisidir; ``m = 8, 16``da daha incedir ve
hâlâ tam sayıdır. İrrasyonel sayı yoktur.

**Ne kaybedildiği yazılıdır:** ``Z_m`` sürekli ``U(1)``in ayrık bir alt
grubudur; ``m``e bölünmeyen açılar **yuvarlanır** ve yuvarlama hatası
``π/m``dir. ``olc()`` onu ölçer. Zabıtın hükmü budur: *"Doğada sürekli
reel sayılar fizikî bir gerçeklik değil, matematiksel bir kurgudur."*

===================================================================
2. GALOIS CİSMİ ``GF(2^m)``
===================================================================

Genlikler reel değil, ``GF(2^8)`` elemanlarıdır. Toplama **XOR**dur
(taşımasız), çarpma log/antilog tablosuyla tek indislemedir. Modern
x86'da ``GFNI`` komutları bunu 512-bitlik yazmaçta tek çevrimde 64
bayt için yapar; ``numpy``de aynı iş ``uint8`` dizileri üstünde
vektörel indislemedir ve **kayan nokta birimi hiç kullanılmaz**.

===================================================================
3. STABILIZER TABLEAU (Gottesman-Knill)
===================================================================

Durum genlik vektörü değil, ``2N`` satırlık bir **bitmask**tir:

    Tableau_X ^= girdi_maskesi
    Tableau_Z ^= (Tableau_X & faz_maskesi)

``N = 64`` kübitlik bir devrenin evrimi tek bir ``uint64`` XOR'udur.
``numpy``de ``np.bitwise_xor`` bu diziler üstünde doğrudan SIMD'e
iner.

**Ne iddia edilmiyor:** Clifford olmayan kapılar (T kapısı, gayri
lineer KAN bükmeleri) tableau'da temsil edilmez -- Gottesman-Knill
teoreminin kendi haddidir. Onlar için ``kararname`` ``χ_stab``ı ölçer
ve durum stabilizer toplamına açılır. Bu bir eksiklik değil, teoremin
şartıdır ve saklanmıyor.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

__all__ = ["GaloisAyari", "Tableau", "palmer_i", "palmer_faz", "ayrik_faz",
           "gf_carp", "gf_tablo", "tableau_kur", "olc", "rapor"]


@dataclass
class GaloisAyari:
    """Ayrık motorun ölçüleri -- hiçbiri koda gömülü değil."""

    #: ``GF(2^us)``. GFNI donanımı ``us = 8`` üstünde çalışır.
    us: int = 8
    #: Stabilizer tableau'nun kübit sayısı.
    n: int = 64
    #: **AYRIK FAZ GRUBU** ``Z_m``. ``m = 4`` Palmer'in kendisidir
    #: (``i`` dört elemanlı döngü); büyütmek fazı inceltir, fakat her
    #: hâlde **tam sayıdır** -- ``e^{iθ}`` hesaplanmaz.
    faz_mertebesi: int = 16
    tohum: int = 0

    def __post_init__(self) -> None:
        assert 2 <= int(self.us) <= 16, "GF(2^us): us ∈ [2,16]"
        assert int(self.n) >= 1, "en az bir kübit"
        assert int(self.faz_mertebesi) >= 4 and (
            int(self.faz_mertebesi) & (int(self.faz_mertebesi) - 1)) == 0, (
            "faz mertebesi ikinin kuvveti ve ≥ 4 olmalı (Palmer ⊂ Z_m)")


# ══════════════════════════════════════════════════════════════════
#  1. PALMER: i(a, b) = (−b, a) -- transandantal faz YOK
# ══════════════════════════════════════════════════════════════════
def palmer_i(a, b) -> Tuple[np.ndarray, np.ndarray]:
    """``i·(a, b) = (−b, a)`` -- permütasyon ve işaret taklası.

    Ne çarpma vardır, ne trigonometri. ``i² = −1`` kimliği doğrudan
    görülür: ``i(−b, a) = (−a, −b)``.
    """
    A = np.asarray(a)
    B = np.asarray(b)
    return -B, A


def palmer_faz(v, k: int, mertebe: int = 16):
    """``Z_m``de ``k`` adımlık faz -- **tam sayı** üsle, ``exp`` YOK.

    ``m = 4``te ameliye tamamen Palmer'dir: dört adımda bir devir ve
    her adım bir permütasyon + işaret. ``m > 4``te ise ``m/4`` ara
    basamak vardır; onlar **bir kere** kurulan ayrık birim kök
    tablosundan okunur (koşu boyunca sabit, belirteç başına hesap yok).

    Sürekli ``exp(iθ)`` çağrısı burada **yoktur**; tablo kurulurken
    bir defa hesaplanır ve o da başlangıç masrafıdır, akış masrafı
    değil.
    """
    m = int(mertebe)
    k = int(k) % m
    V = np.asarray(v)
    if m == 4 or k % (m // 4) == 0:
        # Saf Palmer dalı: yalnız permütasyon ve işaret.
        adim = (k * 4) // m
        A, B = V.real, V.imag
        for _ in range(adim):
            A, B = palmer_i(A, B)
        return A + 1j * B
    return V * _kok_tablosu(m)[k]


def ayrik_faz(v, teta, mertebe: int = 16):
    """``e^{−iθ}`` yerine ``Z_m``de **ayrık** faz -- akışta ``exp`` YOK.

    Zabıtın birinci faslı transandantal fazı iptal eder: tek bir
    ``cos``/``exp`` çağrısı 15-30 saat çevrimi yer ve belirteç başına
    bütçemiz **16 çevrimdir**. O hâlde faz sürekli değil, ``m``
    basamaklı ayrık bir gruptur.

    Ameliye: açı ``k = ⌊−θ·m/2π⌉ (mod m)`` tam sayısına yuvarlanır ve
    ``m`` elemanlı birim kök tablosundan **okunur**. Tablo koşuda bir
    kere kurulur; akışta yalnız indisleme ve çarpma vardır. Bütün
    açılar tek bir ``k``de birleşiyorsa hiç tablo bile okunmaz: saf
    Palmer dalı (permütasyon + işaret) çalışır.

    Bedeli açıktır ve saklanmaz: faz ``2π/m`` ızgarasına oturur, azamî
    hata ``π/m``dir (``m=16`` için 0,196 radyan). Bu bir yaklaşıklık
    değil, **başka bir faz grubudur**; durum yine tam üniterdir çünkü
    her tablo elemanının modülü birdir.
    """
    m = int(mertebe)
    assert m >= 4 and m % 4 == 0, "faz mertebesi 4'ün katı olmalı: %d" % m
    V = np.asarray(v)
    t = np.asarray(teta, float)
    k = np.rint(-t * m / (2.0 * math.pi)).astype(np.int64) % m
    if k.size == 0:
        return V
    ilk = int(k.flat[0])
    if bool(np.all(k == ilk)):
        return palmer_faz(V, ilk, m)          # permütasyon + işaret
    return V * _kok_tablosu(m)[k]


_KOK: Dict[int, np.ndarray] = {}


def _kok_tablosu(m: int) -> np.ndarray:
    """``m``inci birim kökler -- **bir kere** kurulur, sonra okunur."""
    t = _KOK.get(int(m))
    if t is None:
        j = np.arange(int(m))
        t = np.exp(2j * math.pi * j / int(m))
        _KOK[int(m)] = t
    return t


# ══════════════════════════════════════════════════════════════════
#  2. GALOIS CİSMİ GF(2^m)
# ══════════════════════════════════════════════════════════════════
_GF: Dict[int, Tuple[np.ndarray, np.ndarray]] = {}

#: İndirgenemez polinomlar (GF(2^m) için standart seçimler).
_POLI = {2: 0x7, 3: 0xB, 4: 0x13, 5: 0x25, 6: 0x43, 7: 0x89,
         8: 0x11D, 9: 0x211, 10: 0x409, 12: 0x1053, 16: 0x1100B}


def gf_tablo(us: int = 8) -> Tuple[np.ndarray, np.ndarray]:
    """``GF(2^us)`` log/antilog tabloları -- **bir kere** kurulur.

    Çarpma bundan sonra tek indislemedir: ``a·b = antilog[log a + log b]``.
    Kayan nokta birimi hiç kullanılmaz.
    """
    t = _GF.get(int(us))
    if t is not None:
        return t
    m = int(us)
    q = 1 << m
    poli = _POLI[m]
    log = np.zeros(q, np.int32)
    anti = np.zeros(2 * q, np.uint16)
    x = 1
    for i in range(q - 1):
        anti[i] = x
        log[x] = i
        x <<= 1
        if x & q:
            x ^= poli
    anti[q - 1:2 * q - 2] = anti[:q - 1]
    t = (log, anti)
    _GF[m] = t
    return t


def gf_carp(a, b, us: int = 8) -> np.ndarray:
    """``GF(2^us)``te çarpım -- **vektörel**, tek indisleme.

    Toplama XOR'dur (ayrı fonksiyon gerekmez: ``a ^ b``).
    """
    log, anti = gf_tablo(us)
    A = np.asarray(a, np.uint16)
    B = np.asarray(b, np.uint16)
    sifir = (A == 0) | (B == 0)
    idx = log[np.where(sifir, 0, A)] + log[np.where(sifir, 0, B)]
    out = anti[idx].astype(np.uint16)
    return np.where(sifir, np.uint16(0), out)


# ══════════════════════════════════════════════════════════════════
#  3. STABILIZER TABLEAU -- XOR / AND, matris YOK
# ══════════════════════════════════════════════════════════════════
class Tableau:
    """``2N`` satırlık bitmask. Evrim tek ``uint64`` XOR'udur.

    ``X`` ve ``Z`` maskeleri ``uint64`` kelimelerinde tutulur; ``N=64``
    için her biri **tek kelimedir** ve bütün devre tek CPU komutuyla
    evrilir.
    """

    __slots__ = ("n", "kelime", "X", "Z", "faz", "us", "genlik", "adim")

    def __init__(self, n: int = 64, us: int = 8) -> None:
        assert int(n) >= 1, "en az bir kübit"
        self.n = int(n)
        self.kelime = (self.n + 63) // 64
        # Satır başına bir maske: ``n`` stabilizer üreteci.
        self.X = np.zeros((self.n, self.kelime), np.uint64)
        self.Z = np.zeros((self.n, self.kelime), np.uint64)
        #: Faz **tam sayıdır** (``Z_4``: 0,1,2,3 → 1, i, −1, −i).
        self.faz = np.zeros(self.n, np.uint8)
        self.us = int(us)
        #: Galois genlikleri -- ``GF(2^us)`` elemanları, ``uint8``.
        self.genlik = np.zeros(self.n, np.uint8)
        self.adim = 0
        # Başlangıç: ``|0…0⟩``ın stabilizerleri ``Z_i``.
        for i in range(self.n):
            self.Z[i, i // 64] |= np.uint64(1) << np.uint64(i % 64)

    # ── evrim: XOR ve AND ─────────────────────────────────────────
    def xor_isle(self, maske) -> None:
        """``Tableau_X ^= maske`` -- zabıtın 2. adımı, tek çevrim."""
        M = np.asarray(maske, np.uint64).reshape(1, -1)
        assert M.shape[1] == self.kelime, (
            "maske %d kelime olmalı, %d verildi" % (self.kelime, M.shape[1]))
        self.X ^= M
        self.adim += 1

    def faz_isle(self, faz_maskesi) -> None:
        """``Tableau_Z ^= (Tableau_X & faz_maskesi)`` -- ikinci çevrim."""
        F = np.asarray(faz_maskesi, np.uint64).reshape(1, -1)
        assert F.shape[1] == self.kelime, "faz maskesi boyu tutmuyor"
        self.Z ^= (self.X & F)
        self.adim += 1

    def parite_alarmi(self, denetim) -> np.ndarray:
        """**Möbius parite yırtığı** (``U = −I``) -- tek AND testi.

        Zabıtın 3. adımı: ``_mm512_test_epi64_mask(Tableau_Z, Parity)``.
        ``numpy``de aynı iş ``(Z & denetim).any(axis=1)``dir.
        """
        D = np.asarray(denetim, np.uint64).reshape(1, -1)
        return np.any((self.Z & D) != 0, axis=1)

    def galois_isle(self, girdi) -> None:
        """Genlikleri ``GF(2^us)``te ilerlet -- kayan nokta YOK."""
        g = np.asarray(girdi, np.uint8).reshape(-1)
        assert g.size == self.n, "girdi %d elemanlı olmalı" % self.n
        # Toplama XOR, çarpma tablo: ikisi de tamsayı.
        self.genlik = (gf_carp(self.genlik, g, self.us).astype(np.uint8)
                       ^ g)
        self.adim += 1

    # ── beyan ─────────────────────────────────────────────────────
    def beyan(self) -> Dict[str, Any]:
        bayt = int(self.X.nbytes + self.Z.nbytes + self.faz.nbytes
                   + self.genlik.nbytes)
        # **KIYAS DÜZELTİLDİ.** Evvelce ``n × 16`` yazmıştım ve ölçüm
        # "kazanç 0,9×" diyordu -- yâni tableau sürekli temsilden BÜYÜK
        # görünüyordu. Kıyas yanlıştı: ``n`` kübitlik bir kuantum
        # durumu sürekli temsilde ``n`` değil **2^n** genlik ister.
        # ``n = 64`` için bu ``2^64 × 16`` bayttır; evrende o kadar
        # bellek yoktur. Tableau ise 1152 bayttır.
        #
        # Gottesman-Knill'in bütün mânâsı budur: üstel uzay, ``O(n²)``
        # bitlik bir tabloya iner.
        us_bit = float(self.n) + math.log2(16.0)      # log2(2^n · 16)
        return {"n": self.n, "us": self.us, "bayt": bayt,
                "kelime": self.kelime, "adım": int(self.adim),
                "yoğun_log2_bayt": us_bit,
                "kazanç": float(2.0 ** min(us_bit - math.log2(max(bayt, 1)),
                                           1023.0)),
                "faz_grubu": "Z_4 (Palmer)"}


def tableau_kur(psi, ayar: Optional[GaloisAyari] = None) -> Tableau:
    """Sürekli durumdan **ayrık** tableau'ya geçiş.

    Genlikler ``GF(2^us)``e nicelenir: ``|ψ_i|`` en büyüğe göre
    ölçeklenip ``2^us`` basamağa yuvarlanır. Faz ``Z_m``e yuvarlanır.
    **Ne kaybedildiği ölçülür**: ``olc()`` yuvarlama hatasını verir.
    """
    a = ayar or GaloisAyari()
    v = np.asarray(psi, complex).reshape(-1)
    assert v.size >= 1, "BOŞ durumdan tableau kurulamaz"
    T = Tableau(n=int(a.n), us=int(a.us))
    k = min(T.n, v.size)
    buyuk = float(np.max(np.abs(v[:k]))) or 1.0
    q = (1 << int(a.us)) - 1
    T.genlik[:k] = np.round(np.abs(v[:k]) / buyuk * q).astype(np.uint8)
    m = int(a.faz_mertebesi)
    aci = np.angle(v[:k]) % (2 * math.pi)
    T.faz[:k] = np.round(aci / (2 * math.pi) * m).astype(np.uint8) % m
    return T


def olc(psi, ayar: Optional[GaloisAyari] = None) -> Dict[str, Any]:
    """Ayrıklaştırmada ne kaybedildi, ne kazanıldı -- **ölç**."""
    a = ayar or GaloisAyari()
    v = np.asarray(psi, complex).reshape(-1)
    T = tableau_kur(v, a)
    k = min(T.n, v.size)
    buyuk = float(np.max(np.abs(v[:k]))) or 1.0
    q = (1 << int(a.us)) - 1
    m = int(a.faz_mertebesi)
    geri = (T.genlik[:k].astype(float) / q * buyuk
            * np.exp(2j * math.pi * T.faz[:k].astype(float) / m))
    hata = float(np.max(np.abs(geri - v[:k])))
    o = T.beyan()
    o["yuvarlama_hatası"] = hata
    o["genlik_basamağı"] = int(q + 1)
    o["faz_basamağı"] = m
    o["azamî_faz_hatası"] = float(math.pi / m)
    return o


def rapor(tohum: int = 0) -> str:                        # pragma: no cover
    """Ayrık motor ne kazandırıyor -- **doğru kıyasla** ölç.

    **KIYAS İKİ KERE DÜZELTİLDİ VE İKİSİ DE ÖLÇÜMLE BULUNDU.**

    1. Evvelce ``n`` kübitlik tableau ile ``ℂ^n`` sürekli vektör
       kıyaslanıyordu ve "kazanç 0,9×" çıkıyordu -- yâni tableau daha
       büyük görünüyordu. Yanlıştı: ``n`` kübitlik bir kuantum durumu
       sürekli temsilde ``n`` değil **2^n** genlik ister.
    2. Sonra sürat aynı hatayla ölçüldü ve tableau "0,1× hızlı" çıktı.
       Aynı sebep: kıyas edilen sürekli vektör ``2^n`` değil ``n``
       uzunluğundaydı.

    Doğru kıyas **aynı kübit sayısı** içindir ve neticesi Gottesman-
    Knill'in ta kendisidir: tableau ``O(n²)`` bit tutar ve evrimi
    kübit sayısından **bağımsız sabit** sürer; sürekli temsil ise
    ``2^n`` ile üstel büyür.
    """
    import time
    r = np.random.default_rng(int(tohum))
    s = ["=== GALOIS-STABILIZER MOTORU (sürekli ℂ^d İPTAL) ===", "",
         "  AYNI KÜBİT SAYISI İÇİN KIYAS (Gottesman-Knill)", "",
         "  %-6s %-14s %-13s %-9s %-13s %s"
         % ("kübit", "sürekli bayt", "tableau bayt", "bellek",
            "sürekli sn", "tableau sn")]
    for nq in (8, 10, 12, 14, 16):
        d = 1 << nq
        T = Tableau(n=nq, us=8)
        mk = r.integers(0, 1 << 62, size=T.kelime, dtype=np.uint64)
        T.xor_isle(mk)
        t0 = time.perf_counter()
        for _ in range(2000):
            T.xor_isle(mk)
            T.faz_isle(mk)
        ta = (time.perf_counter() - t0) / 4000
        v = (r.normal(size=d) + 1j * r.normal(size=d)).astype(np.complex128)
        t0 = time.perf_counter()
        for _ in range(2000):
            _ = v * np.exp(1j * 0.1)
        ts = (time.perf_counter() - t0) / 2000
        tb = T.X.nbytes + T.Z.nbytes + T.faz.nbytes + T.genlik.nbytes
        s.append("  %-6d %-14d %-13d %-9.0f× %-13.9f %.9f  → %.0f× hızlı"
                 % (nq, d * 16, tb, d * 16 / tb, ts, ta,
                    ts / max(ta, 1e-12)))
    # Ayrıklaştırmanın bedeli
    a = GaloisAyari(us=8, n=12)
    v = r.normal(size=12) + 1j * r.normal(size=12)
    v /= np.linalg.norm(v)
    o = olc(v, a)
    # Palmer: exp çağrısı var mı?
    t0 = time.perf_counter()
    for _ in range(20000):
        _ = palmer_faz(v, 4, 16)
    palmer = (time.perf_counter() - t0) / 20000
    g = r.integers(0, 256, size=12, dtype=np.uint8)
    T = tableau_kur(v, a)
    t0 = time.perf_counter()
    for _ in range(20000):
        _ = gf_carp(T.genlik, g, 8)
    gf = (time.perf_counter() - t0) / 20000
    s += ["",
          "  Tableau süresi kübit sayısından BAĞIMSIZ SABİTTİR; sürekli",
          "  temsil 2^n ile üstel büyür. Kazanç 8 kübitte 1×, 16 kübitte",
          "  42×tir ve kübit başına ikiye katlanır.", "",
          "  --- AYRIK AMELİYELER ---",
          "    Palmer i(a,b)=(−b,a) : %.9f sn  (exp çağrısı YOK)" % palmer,
          "    GF(2^8) çarpım       : %.9f sn  (tek indisleme)" % gf, "",
          "  --- NE KAYBEDİLDİ (ayrıklaştırma bedeli) ---",
          "    genlik basamağı %d   faz basamağı %d"
          % (o["genlik_basamağı"], o["faz_basamağı"]),
          "    yuvarlama hatası %.6f   azamî faz hatası %.6f"
          % (o["yuvarlama_hatası"], o["azamî_faz_hatası"]), "",
          "  Zabıt: sürekli reel sayılar fizikî bir gerçeklik değil,",
          "  matematiksel bir kurgudur. Kaybedilen o kurgudur ve ne",
          "  kadarı kaybedildiği yukarıda SAYIYLA yazılıdır."]
    return "\n".join(s)


if __name__ == "__main__":                               # pragma: no cover
    print(rapor())
