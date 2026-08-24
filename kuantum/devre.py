"""Devre — durum vektörü simülatörü ve spektral işleçler.

Bir ``n`` kübitlik durum ``2^n`` karmaşık genlikten ibarettir.  Kapı
uygulamak, prensipte ``2^n × 2^n`` bir dizeyle çarpmaktır; fakat **öyle
yapılmaz**.  Bir ``k``-kübit kapısı yalnız ``k`` indise dokunur, geri
kalan ``n−k`` indis seyircidir.  Durumu ``(2^k, 2^{n-k})`` biçiminde
görüp yalnız ilk eksene çarpmak aynı neticeyi verir ve

* zaman: ``O(2^n · 2^k)`` yerine tam dizeyin ``O(4^n)``i,
* bellek: ``2^n × 2^n`` dizey hiç kurulmaz.

Fark ölçülüyor ve iki yolun **birebir aynı** durumu verdiği sınanıyor;
hızlanma neticeyi değiştirmiyor.

Ayrıca:

* **QFT** -- hem doğrudan dizeyle hem kapı kapı (Hadamard + kontrollü
  faz + ters çevirme) kurulur; ikisi karşılaştırılır.
* **QPE** -- bir üniterin özdeğer fazını okur; kesin temsil edilebilen
  fazlarda **tam** cevap verir ve o hâl ayrıca sınanır.
* **Trotter–Suzuki** -- ``e^{-i(A+B)t}`` ayrıştırması; 1. ve 2. mertebe
  hatalarının ``O(t²/n)`` ve ``O(t³/n²)`` gittiği ölçülür.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

from .kapilar import (CNOT, H, I2, X, Y, Z, U1, esdeger_mi, kontrollu,
                      uniter_mi, yerlestir)

__all__ = [
    "Durum", "Devre", "qft_dizeyi", "qft_devresi", "iqft_dizeyi",
    "faz_kestirimi", "trotter", "suzuki2", "hadamard_testi",
    "walsh_hadamard", "olcum_dagilimi",
]


# ══════════════════════════════════════════════════════════════════════
#  Durum
# ══════════════════════════════════════════════════════════════════════

@dataclass
class Durum:
    """``n`` kübitlik saf hâl; genlikler ``(2^n,)``.

    ``q_0`` en anlamlı bit (bkz. :mod:`kuantum.kapilar`).
    """
    n: int
    v: np.ndarray = field(default=None, repr=False)

    def __post_init__(self) -> None:
        if self.v is None:
            self.v = np.zeros(2 ** self.n, dtype=complex)
            self.v[0] = 1.0
        self.v = np.asarray(self.v, dtype=complex).reshape(-1)
        if self.v.size != 2 ** self.n:
            raise ValueError(f"genlik sayısı {2**self.n} olmalı")

    @property
    def norm(self) -> float:
        return float(np.linalg.norm(self.v))

    def normalize(self) -> "Durum":
        nrm = self.norm
        if nrm < 1e-300:
            raise ValueError("sıfır vektör normalize edilemez")
        self.v = self.v / nrm
        return self

    def uygula(self, U: np.ndarray, kubitler: Sequence[int]) -> "Durum":
        """Kapıyı **tam dizey kurmadan** uygular.

        Durum ``(2^k, 2^{n-k})`` biçimine getirilir; kapı yalnız ilk
        eksene çarpılır.  Bunun için hedef kübitler önce en anlamlı
        konuma taşınır (eksen permütasyonu), sonra geri alınır.
        ``np.transpose`` görünüm döndürdüğü için taşıma bedava değildir
        ama ``2^n × 2^n`` dizey kurmaktan çok ucuzdur.
        """
        k = len(kubitler)
        if U.shape != (2 ** k, 2 ** k):
            raise ValueError(f"U {2**k}×{2**k} olmalı")
        if len(set(kubitler)) != k or any(not 0 <= q < self.n
                                          for q in kubitler):
            raise ValueError("kübit indisleri geçersiz")
        kalan = [q for q in range(self.n) if q not in kubitler]
        sira = list(kubitler) + kalan
        T = self.v.reshape([2] * self.n)
        T = np.transpose(T, sira)                 # hedefler öne
        T = T.reshape(2 ** k, -1)
        T = U @ T
        T = T.reshape([2] * self.n)
        ters = np.argsort(sira)
        self.v = np.transpose(T, ters).reshape(-1)
        return self

    def uygula_tam_dizey(self, U: np.ndarray,
                         kubitler: Sequence[int]) -> "Durum":
        """Aynı işi ``2^n × 2^n`` dizey kurarak yapar — kıyas içindir."""
        G = yerlestir(U, kubitler, self.n)
        self.v = G @ self.v
        return self

    def olasiliklar(self) -> np.ndarray:
        return np.abs(self.v) ** 2

    def kopya(self) -> "Durum":
        return Durum(self.n, self.v.copy())


def olcum_dagilimi(d: Durum, kubitler: Sequence[int]) -> np.ndarray:
    """Seçili kübitlerin marjinal ölçüm dağılımı."""
    k = len(kubitler)
    kalan = [q for q in range(d.n) if q not in kubitler]
    T = d.v.reshape([2] * d.n)
    T = np.transpose(T, list(kubitler) + kalan).reshape(2 ** k, -1)
    return np.sum(np.abs(T) ** 2, axis=1)


# ══════════════════════════════════════════════════════════════════════
#  Devre
# ══════════════════════════════════════════════════════════════════════

@dataclass
class Devre:
    """Kapı listesi; ``n`` kübit üzerinde sırayla uygulanır."""
    n: int
    adimlar: List[Tuple[np.ndarray, Tuple[int, ...], str]] = \
        field(default_factory=list)

    def ekle(self, U: np.ndarray, kubitler: Sequence[int],
             ad: str = "") -> "Devre":
        if not uniter_mi(U):
            raise ValueError(f"'{ad or 'kapı'}' üniter değil")
        self.adimlar.append((np.asarray(U, complex),
                             tuple(kubitler), ad))
        return self

    def kosur(self, d: Optional[Durum] = None) -> Durum:
        d = d if d is not None else Durum(self.n)
        for U, q, _ in self.adimlar:
            d.uygula(U, q)
        return d

    def dizey(self) -> np.ndarray:
        """Devrenin tam ``2^n × 2^n`` dizeyi — kıyas ve tahlil için."""
        M = np.eye(2 ** self.n, dtype=complex)
        for U, q, _ in self.adimlar:
            M = yerlestir(U, q, self.n) @ M
        return M

    @property
    def kapi_sayisi(self) -> int:
        return len(self.adimlar)


# ══════════════════════════════════════════════════════════════════════
#  QFT
# ══════════════════════════════════════════════════════════════════════

def qft_dizeyi(n: int) -> np.ndarray:
    """``QFT_N |j⟩ = N^{-1/2} Σ_k ω^{jk} |k⟩``, ``ω = e^{2πi/N}``."""
    N = 2 ** n
    j = np.arange(N)
    return np.exp(2j * np.pi * np.outer(j, j) / N) / np.sqrt(N)


def iqft_dizeyi(n: int) -> np.ndarray:
    return qft_dizeyi(n).conj().T


def qft_devresi(n: int, ters_cevir: bool = True) -> Devre:
    """QFT'yi kapı kapı kurar: H + kontrollü faz + SWAP.

    Kübit ``j`` için: ``H`` uygula, sonra ``k > j`` için ``CU_1``
    ile ``2π/2^{k-j+1}`` fazı ekle.  Sonunda kübit sırası **tersine
    döner**; ``ters_cevir=True`` bunu SWAP'larla düzeltir.

    Ters çevirmeyi unutmak sessiz bir hatadır: devre üniter kalır,
    hatta çoğu testten geçer, ama bit sırası ters okunur.  Bu yüzden
    aşağıda dizey hâliyle **birebir** karşılaştırılıyor.
    """
    d = Devre(n)
    for j in range(n):
        d.ekle(H, [j], f"H{j}")
        for k in range(j + 1, n):
            aci = 2 * np.pi / (2 ** (k - j + 1))
            d.ekle(kontrollu(U1(aci)), [k, j], f"CU1({k}->{j})")
    if ters_cevir:
        for j in range(n // 2):
            d.ekle(_swap(), [j, n - 1 - j], f"SWAP{j}")
    return d


def _swap() -> np.ndarray:
    return np.array([[1, 0, 0, 0], [0, 0, 1, 0],
                     [0, 1, 0, 0], [0, 0, 0, 1]], dtype=complex)


def walsh_hadamard(n: int) -> np.ndarray:
    """``H^{⊗n} = 2^{-n/2} Σ_{x,y} (-1)^{x·y} |y⟩⟨x|``."""
    M = np.array([[1.0 + 0j]])
    for _ in range(n):
        M = np.kron(M, H)
    return M


# ══════════════════════════════════════════════════════════════════════
#  Faz kestirimi (QPE)
# ══════════════════════════════════════════════════════════════════════

def faz_kestirimi(U: np.ndarray, ozvektor: np.ndarray,
                  m: int) -> Dict[str, object]:
    """``U|ψ⟩ = e^{2πiφ}|ψ⟩`` iken ``φ``yi ``m`` bitle okur.

    Kayıt: ``m`` sayaç kübiti + ``ψ``nin kübitleri.  Sayaçlara Hadamard,
    sonra kontrollü ``U^{2^j}``, sonra ters QFT.

    ``φ``, ``m`` bitle **tam** temsil edilebiliyorsa netice kesindir
    (tek bir sonuç 1 olasılıkla çıkar); aksi hâlde dağılır ve en yakın
    bit dizisi en yüksek olasılığı alır.  İki hâl de ölçülüyor.
    """
    if not uniter_mi(U):
        raise ValueError("U üniter olmalı")
    d_psi = U.shape[0]
    n_psi = int(round(math.log2(d_psi)))
    if 2 ** n_psi != d_psi:
        raise ValueError("U'nun boyutu 2'nin kuvveti olmalı")
    psi = np.asarray(ozvektor, complex).reshape(-1)
    psi = psi / np.linalg.norm(psi)

    n = m + n_psi
    v = np.zeros(2 ** n, dtype=complex)
    # |0…0⟩ ⊗ |ψ⟩
    v[:d_psi] = psi
    d = Durum(n, v)
    for j in range(m):
        d.uygula(H, [j])
    # kontrollü U^{2^j};  j = m-1 en düşük anlamlı sayaç biti
    for j in range(m):
        us = 2 ** (m - 1 - j)
        Uk = np.linalg.matrix_power(U, us)
        d.uygula(kontrollu(Uk), [j] + list(range(m, n)))
    # sayaçlara ters QFT
    d.uygula(iqft_dizeyi(m), list(range(m)))

    dag = olcum_dagilimi(d, list(range(m)))
    en_iyi = int(np.argmax(dag))
    return {
        "dağılım": dag,
        "en_olası_bit": en_iyi,
        "φ_tahmini": en_iyi / 2 ** m,
        "en_olası_olasılık": float(dag[en_iyi]),
        "durum": d,
    }


# ══════════════════════════════════════════════════════════════════════
#  Trotter–Suzuki
# ══════════════════════════════════════════════════════════════════════

def _uexp(M: np.ndarray, t: float) -> np.ndarray:
    """``exp(-i t M)`` — Hermitesel ``M`` için özayrışımla (tam)."""
    oz, V = np.linalg.eigh(M)
    return V @ np.diag(np.exp(-1j * t * oz)) @ V.conj().T


def trotter(A: np.ndarray, B: np.ndarray, t: float, n: int) -> np.ndarray:
    """1. mertebe: ``(e^{-iAt/n} e^{-iBt/n})^n``.  Hata ``O(t²/n)``."""
    if n < 1:
        raise ValueError("n ≥ 1 olmalı")
    adim = _uexp(A, t / n) @ _uexp(B, t / n)
    return np.linalg.matrix_power(adim, n)


def suzuki2(A: np.ndarray, B: np.ndarray, t: float, n: int) -> np.ndarray:
    """2. mertebe: ``(e^{-iAt/2n} e^{-iBt/n} e^{-iAt/2n})^n``.

    Hata ``O(t³/n²)``.  Simetrik olduğu için tek mertebeli terimler
    birbirini götürür; kazanç buradan gelir ve ölçülür.
    """
    if n < 1:
        raise ValueError("n ≥ 1 olmalı")
    yari = _uexp(A, t / (2 * n))
    adim = yari @ _uexp(B, t / n) @ yari
    return np.linalg.matrix_power(adim, n)


def hadamard_testi(U: np.ndarray, psi: np.ndarray,
                   sanal: bool = False) -> float:
    """``Re⟨ψ|U|ψ⟩`` (veya ``Im``) — tek yardımcı kübitle.

    Devre: yardımcıya ``H``, kontrollü ``U``, (sanal için ``S†``),
    tekrar ``H``.  Yardımcıda ``0`` görme olasılığı
    ``(1 + Re⟨U⟩)/2``dir; oradan ``Re⟨U⟩`` okunur.
    """
    psi = np.asarray(psi, complex).reshape(-1)
    psi = psi / np.linalg.norm(psi)
    n_psi = int(round(math.log2(psi.size)))
    n = 1 + n_psi
    v = np.zeros(2 ** n, dtype=complex)
    v[:psi.size] = psi
    d = Durum(n, v)
    d.uygula(H, [0])
    d.uygula(kontrollu(U), [0] + list(range(1, n)))
    if sanal:
        d.uygula(np.diag([1, -1j]).astype(complex), [0])
    d.uygula(H, [0])
    p0 = float(olcum_dagilimi(d, [0])[0])
    return 2 * p0 - 1


# ══════════════════════════════════════════════════════════════════════
#  Gösterim
# ══════════════════════════════════════════════════════════════════════

def _gosterim() -> str:
    import time
    s: List[str] = []
    rng = np.random.default_rng(0)

    s.append("=== Kapı uygulaması: eksen görünümü v tam dizey ===")
    s.append("  iki yol AYNI durumu vermeli; fark yalnız maliyette")
    for n in (6, 10, 14, 18):
        v = rng.normal(size=2 ** n) + 1j * rng.normal(size=2 ** n)
        v /= np.linalg.norm(v)
        d1, d2 = Durum(n, v.copy()), Durum(n, v.copy())
        t0 = time.perf_counter()
        for _ in range(20):
            d1.uygula(CNOT, [0, n - 1])
        hizli = time.perf_counter() - t0
        if n <= 12:
            t0 = time.perf_counter()
            for _ in range(20):
                d2.uygula_tam_dizey(CNOT, [0, n - 1])
            yavas = time.perf_counter() - t0
            fark = float(np.max(np.abs(d1.v - d2.v)))
            s.append(f"  n={n:2d}: eksen {hizli*1000:8.2f} ms   "
                     f"tam dizey {yavas*1000:9.2f} ms"
                     f"   ({yavas/hizli:6.1f}×)   fark={fark:.2e}")
        else:
            bellek = (2 ** n) ** 2 * 16 / 1e9
            s.append(f"  n={n:2d}: eksen {hizli*1000:8.2f} ms   "
                     f"tam dizey kurulmadı — {bellek:.1f} GB tutardı")

    s.append("\n=== QFT: dizey ile devre aynı mı? ===")
    for n in (1, 2, 3, 4, 5):
        D = qft_devresi(n).dizey()
        M = qft_dizeyi(n)
        s.append(f"  n={n}: kapı sayısı {qft_devresi(n).kapi_sayisi:3d}"
                 f"   ‖devre−dizey‖∞ = {np.max(np.abs(D - M)):.2e}"
                 f"   üniter mi? {uniter_mi(D)}")
    s.append("  SWAP'sız hâl (bit sırası ters):")
    for n in (3, 4):
        D = qft_devresi(n, ters_cevir=False).dizey()
        M = qft_dizeyi(n)
        s.append(f"    n={n}: fark = {np.max(np.abs(D - M)):.4f}"
                 f"   — üniter ama YANLIŞ ({uniter_mi(D)})")

    s.append("\n=== QFT köşegen değildir (K8 tashihi) ===")
    for n in (2, 3):
        M = qft_dizeyi(n)
        kd = np.max(np.abs(M - np.diag(np.diag(M))))
        s.append(f"  n={n}: köşegen dışı azamî = {kd:.4f}"
                 f"   (köşegen olsaydı 0 olurdu)")

    s.append("\n=== Faz kestirimi ===")
    for m in (3, 4, 6):
        # φ = 3/8 = 0.011₂ — 3 bitle TAM temsil edilebilir
        fi = 3 / 8
        U = np.diag([np.exp(2j * np.pi * fi), 1.0]).astype(complex)
        r = faz_kestirimi(U, np.array([1.0, 0.0]), m)
        s.append(f"  m={m}: φ=3/8 → tahmin {r['φ_tahmini']:.6f}"
                 f"   olasılık {r['en_olası_olasılık']:.6f}")
    # Tam temsil edilemeyen faz
    fi = 1 / 3
    U = np.diag([np.exp(2j * np.pi * fi), 1.0]).astype(complex)
    for m in (4, 6, 8):
        r = faz_kestirimi(U, np.array([1.0, 0.0]), m)
        s.append(f"  m={m}: φ=1/3 → tahmin {r['φ_tahmini']:.6f}"
                 f"   olasılık {r['en_olası_olasılık']:.4f}"
                 f"   hata {abs(r['φ_tahmini'] - fi):.6f}")
    s.append("  Tam temsil edilen fazda olasılık 1; edilemeyende dağılıyor")
    s.append("  ama en yakın bit dizisi baskın kalıyor — beklenen budur.")

    s.append("\n=== Trotter–Suzuki hata mertebeleri ===")
    A = np.array([[1.0, 0.4], [0.4, -0.6]])
    B = np.array([[0.2, -0.9], [-0.9, 0.5]])
    t = 1.0
    tam = _uexp(A + B, t)
    s.append("   n    1.mertebe hata   oran    2.mertebe hata   oran")
    onceki1 = onceki2 = None
    for n in (2, 4, 8, 16, 32):
        h1 = float(np.max(np.abs(trotter(A, B, t, n) - tam)))
        h2 = float(np.max(np.abs(suzuki2(A, B, t, n) - tam)))
        o1 = f"{onceki1/h1:6.2f}" if onceki1 else "     -"
        o2 = f"{onceki2/h2:6.2f}" if onceki2 else "     -"
        s.append(f"  {n:3d}    {h1:.3e}   {o1}    {h2:.3e}   {o2}")
        onceki1, onceki2 = h1, h2
    s.append("  1. mertebede n iki katına çıkınca hata ~2×,")
    s.append("  2. mertebede ~4× düşüyor: O(1/n) ve O(1/n²).")

    s.append("\n=== Hadamard testi ===")
    rng2 = np.random.default_rng(5)
    for _ in range(3):
        psi = rng2.normal(size=2) + 1j * rng2.normal(size=2)
        psi /= np.linalg.norm(psi)
        U = np.linalg.qr(rng2.normal(size=(2, 2))
                         + 1j * rng2.normal(size=(2, 2)))[0]
        re = hadamard_testi(U, psi)
        im = hadamard_testi(U, psi, sanal=True)
        tam_deger = complex(np.vdot(psi, U @ psi))
        s.append(f"  ölçülen {re:+.6f}{im:+.6f}i   "
                 f"tam {tam_deger.real:+.6f}{tam_deger.imag:+.6f}i"
                 f"   fark {abs(complex(re, im) - tam_deger):.2e}")
    return "\n".join(s)


def rapor() -> str:
    return _gosterim()


if __name__ == "__main__":
    print(rapor())
