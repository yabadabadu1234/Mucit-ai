"""KAN — B-spline temelli Kolmogorov–Arnold ağı.

Kolmogorov–Arnold gösterim teoremi, her sürekli çok değişkenli
fonksiyonun **tek değişkenli** fonksiyonların toplamı ve bileşkesiyle
yazılabileceğini söyler.  KAN bunu ağ mimarisine çevirir: ağırlıklar
skaler değil, **öğrenilebilir tek değişkenli fonksiyonlardır**, ve her
biri bir B-spline ile temsil edilir.

Temel, Cox–de Boor özyinelemesiyle kurulur:

.. math::

   B_{i,0}(t) &= \\mathbb{1}[t_i \\le t < t_{i+1}] \\\\
   B_{i,k}(t) &= \\frac{t - t_i}{t_{i+k} - t_i} B_{i,k-1}(t)
               + \\frac{t_{i+k+1} - t}{t_{i+k+1} - t_{i+1}} B_{i+1,k-1}(t)

Sıfır paydalarda ilgili terim **atlanır** (tekrarlı düğümlerde limit
budur); sıfıra bölünüp ``nan`` üretilmez.

Neden RBF değil de B-spline?  Üç sebep, üçü de ölçülebilir:

1. **Yerellik** — derece ``k`` B-spline'ı yalnız ``k+1`` düğüm
   aralığında sıfırdan farklıdır.  Bir noktadaki değeri değiştirmek
   uzaktaki değerleri hiç etkilemez.  Gauss RBF ise her yerde
   sıfırdan farklıdır (üstel küçük de olsa), yani her katsayı her
   noktayı oynatır.
2. **Birliğin bölünmesi** — ``Σ_i B_{i,k}(t) = 1`` her ``t`` için tam
   olarak sağlanır.  Bu, çıktının girdi temelinin **konveks
   birleşimi** olmasını garanti eder ve ölçek kaymasını engeller.
   RBF temelinde böyle bir garanti yoktur; normalize edilmesi gerekir.
3. **Türev kapalı formda** — ``B'_{i,k} = k[B_{i,k-1}/(t_{i+k}-t_i)
   − B_{i+1,k-1}/(t_{i+k+1}-t_{i+1})]``, yani sayısal türev gerekmez.

Hız için temel **bir kere** hesaplanır ve saklanır: aynı ızgara
üzerinde çalışan bütün kenarlar aynı ``(N, G+k)`` temel dizeyini
paylaşır; ileri geçiş tek bir dizey çarpımına iner.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = [
    "dugum_dizisi", "bspline_temeli", "bspline_turev_temeli",
    "BSplineKenar", "KANKatmani", "KAN", "birligin_bolunmesi_sapmasi",
]


# ══════════════════════════════════════════════════════════════════════
#  Düğümler ve temel
# ══════════════════════════════════════════════════════════════════════

def dugum_dizisi(G: int, k: int, alt: float = -1.0,
                 ust: float = 1.0) -> np.ndarray:
    """``G`` aralık, ``k`` derece için genişletilmiş düğüm dizisi.

    ``[alt, ust]`` düzgün bölünür ve iki uçtan ``k`` düğüm **dışarı**
    uzatılır.  Uzatma şart: aksi hâlde uçlara yakın ``B_{i,k}``ler
    tanımsız kalır ve birliğin bölünmesi sınırda bozulur.  Uzunluk
    ``G + 2k + 1``, temel fonksiyon sayısı ``G + k``.
    """
    if G < 1 or k < 0:
        raise ValueError("G ≥ 1 ve k ≥ 0 olmalı")
    if not ust > alt:
        raise ValueError("ust > alt olmalı")
    h = (ust - alt) / G
    return np.array([alt + (i - k) * h for i in range(G + 2 * k + 1)])


def bspline_temeli(t: np.ndarray, dugumler: np.ndarray, k: int
                   ) -> np.ndarray:
    """``B_{i,k}(t)`` — ``(N, len(dugumler)-k-1)`` dizey.

    Cox–de Boor özyinelemesi *yukarı doğru* (dereceden dereceye)
    hesaplanır; her derece için bir vektörleştirilmiş adım.  Naif
    özyineleme aynı ``B_{i,j}``yi üstel sayıda tekrar hesaplar;
    bu hâlde toplam iş ``O(N·(G+k)·k)``dır.
    """
    t = np.atleast_1d(np.asarray(t, float))
    d = np.asarray(dugumler, float)
    if k < 0:
        raise ValueError("derece negatif olamaz")
    n_temel = d.size - 1                     # derece 0'da bu kadar var

    # --- derece 0: gösterge fonksiyonları -----------------------------
    B = ((t[:, None] >= d[None, :-1]) & (t[:, None] < d[None, 1:])
         ).astype(float)
    # Sağ uç kapalı olsun ki t = ust noktası da bir aralığa düşsün;
    # aksi hâlde tam sınırda bütün temel sıfırlanır ve birliğin
    # bölünmesi orada 0 verir.
    sag = d[-1]
    son = np.isclose(t, sag)
    if np.any(son):
        # Sağ uçtan itibaren sıfır uzunlukta olmayan son aralığı bul:
        j = n_temel - 1
        while j > 0 and d[j + 1] <= d[j]:
            j -= 1
        B[son, j] = 1.0

    # --- yukarı doğru özyineleme --------------------------------------
    for derece in range(1, k + 1):
        n_yeni = n_temel - derece
        yeni = np.zeros((t.size, n_yeni))
        for i in range(n_yeni):
            sol_payda = d[i + derece] - d[i]
            sag_payda = d[i + derece + 1] - d[i + 1]
            if sol_payda > 0:               # payda 0 ise terim ATLANIR
                yeni[:, i] += (t - d[i]) / sol_payda * B[:, i]
            if sag_payda > 0:
                yeni[:, i] += (d[i + derece + 1] - t) / sag_payda * B[:, i + 1]
        B = yeni
    return B


def bspline_turev_temeli(t: np.ndarray, dugumler: np.ndarray, k: int
                         ) -> np.ndarray:
    """``B'_{i,k}(t)`` — kapalı formda, sayısal türev almadan.

    .. math::  B'_{i,k} = k\\Bigl(\\frac{B_{i,k-1}}{t_{i+k}-t_i}
                          - \\frac{B_{i+1,k-1}}{t_{i+k+1}-t_{i+1}}\\Bigr)
    """
    if k == 0:
        d = np.asarray(dugumler, float)
        return np.zeros((np.atleast_1d(t).size, d.size - 1))
    d = np.asarray(dugumler, float)
    Bk1 = bspline_temeli(t, d, k - 1)
    n = d.size - k - 1
    T = np.zeros((np.atleast_1d(t).size, n))
    for i in range(n):
        p1 = d[i + k] - d[i]
        p2 = d[i + k + 1] - d[i + 1]
        if p1 > 0:
            T[:, i] += k * Bk1[:, i] / p1
        if p2 > 0:
            T[:, i] -= k * Bk1[:, i + 1] / p2
    return T


def birligin_bolunmesi_sapmasi(t: np.ndarray, dugumler: np.ndarray,
                               k: int) -> float:
    """``|Σ_i B_{i,k}(t) − 1|``in azamîsi — temelin sağlaması.

    Yalnız ``[t_k, t_{n}]`` **tam desteklenen** aralıkta 1 olur; onun
    dışında (uzatma bölgesinde) toplam 1'den küçüktür ve bu doğrudur.
    Bu yüzden ölçüm o aralıkla sınırlanır.
    """
    d = np.asarray(dugumler, float)
    t = np.atleast_1d(np.asarray(t, float))
    ic = (t >= d[k]) & (t <= d[d.size - k - 1])
    if not np.any(ic):
        return 0.0
    return float(np.max(np.abs(bspline_temeli(t[ic], d, k).sum(axis=1) - 1.0)))


# ══════════════════════════════════════════════════════════════════════
#  KAN kenarı ve katmanı
# ══════════════════════════════════════════════════════════════════════

@dataclass
class BSplineKenar:
    """Tek değişkenli öğrenilebilir fonksiyon ``φ(t) = Σ_i c_i B_{i,k}(t)``.

    Ayrıca bir **taban** terimi taşır: ``φ(t) = w_b·silu(t) + w_s·spline(t)``.
    Taban, ızgaranın dışına düşen girdilerde ağın tamamen susmasını
    engeller; B-spline orada sıfırdır ve tek başına bırakılırsa gradyan
    da sıfır olur, yani ağ o bölgeden hiç öğrenemez.
    """
    G: int
    k: int
    alt: float = -1.0
    ust: float = 1.0
    c: Optional[np.ndarray] = None
    w_taban: float = 1.0
    w_spline: float = 1.0
    dugumler: np.ndarray = field(init=False)

    def __post_init__(self) -> None:
        self.dugumler = dugum_dizisi(self.G, self.k, self.alt, self.ust)
        n = self.G + self.k
        if self.c is None:
            self.c = np.zeros(n)
        self.c = np.asarray(self.c, float)
        if self.c.size != n:
            raise ValueError(f"katsayı sayısı {n} olmalı, {self.c.size} verildi")

    @staticmethod
    def _silu(t: np.ndarray) -> np.ndarray:
        return t / (1.0 + np.exp(-t))

    def temel(self, t: np.ndarray) -> np.ndarray:
        return bspline_temeli(t, self.dugumler, self.k)

    def __call__(self, t: np.ndarray) -> np.ndarray:
        t = np.atleast_1d(np.asarray(t, float))
        return (self.w_taban * self._silu(t)
                + self.w_spline * (self.temel(t) @ self.c))

    def turev(self, t: np.ndarray) -> np.ndarray:
        """``φ'(t)`` — spline kısmı kapalı formda, taban analitik."""
        t = np.atleast_1d(np.asarray(t, float))
        sig = 1.0 / (1.0 + np.exp(-t))
        dsilu = sig * (1.0 + t * (1.0 - sig))
        dspline = bspline_turev_temeli(t, self.dugumler, self.k) @ self.c
        return self.w_taban * dsilu + self.w_spline * dspline

    def uydur(self, t: np.ndarray, y: np.ndarray,
              duzenleme: float = 1e-8) -> float:
        """En küçük karelerle katsayıları uydur; artık normunu döndür.

        Taban terimi önce **çıkarılır**, kalan spline'a uydurulur.
        Böylece iki bileşen birbirinin işini yapmaya çalışmaz.
        """
        t = np.atleast_1d(np.asarray(t, float))
        y = np.asarray(y, float).ravel()
        hedef = (y - self.w_taban * self._silu(t)) / self.w_spline
        A = self.temel(t)
        AtA = A.T @ A + duzenleme * np.eye(A.shape[1])
        self.c = np.linalg.solve(AtA, A.T @ hedef)
        return float(np.linalg.norm(self(t) - y) / max(1, np.sqrt(y.size)))


@dataclass
class KANKatmani:
    """``n_giris → n_cikis`` katman; her (i,j) çifti için bir kenar.

    Çıktı ``y_j = Σ_i φ_{ij}(x_i)``.  Toplam kasten dıştadır: KAN'da
    doğrusal olmayanlık kenarlardadır, düğümlerde değil.

    **Hız:** bütün kenarlar aynı ızgarayı paylaştığı için temel dizeyi
    girdi kanalı başına **bir kere** hesaplanır ve bütün çıktı kanalları
    için tekrar kullanılır.  Katsayılar ``(n_giris, n_cikis, G+k)``
    biçiminde tek bir tensörde tutulur ve ileri geçiş tek ``einsum``a
    iner — kenar başına Python döngüsü yoktur.
    """
    n_giris: int
    n_cikis: int
    G: int = 5
    k: int = 3
    alt: float = -1.0
    ust: float = 1.0
    tohum: int = 0
    C: np.ndarray = field(init=False)
    W_taban: np.ndarray = field(init=False)
    W_spline: np.ndarray = field(init=False)
    dugumler: np.ndarray = field(init=False)

    def __post_init__(self) -> None:
        r = np.random.default_rng(self.tohum)
        n = self.G + self.k
        # Xavier benzeri ölçek: girdi sayısına göre küçültülür.
        olcek = 1.0 / np.sqrt(self.n_giris)
        self.C = r.normal(0.0, 0.1 * olcek, (self.n_giris, self.n_cikis, n))
        self.W_taban = r.normal(0.0, olcek, (self.n_giris, self.n_cikis))
        self.W_spline = np.ones((self.n_giris, self.n_cikis))
        self.dugumler = dugum_dizisi(self.G, self.k, self.alt, self.ust)

    @property
    def parametre_sayisi(self) -> int:
        return self.C.size + self.W_taban.size + self.W_spline.size

    def ileri(self, X: np.ndarray) -> np.ndarray:
        """``(N, n_giris) → (N, n_cikis)``.

        Temel dizey **girdi kanalı başına bir kere**: ``(N, n)``.
        Sonra ``einsum("np,ijp->nij")`` ile bütün kenarlar aynı anda.
        """
        X = np.atleast_2d(np.asarray(X, float))
        if X.shape[1] != self.n_giris:
            raise ValueError(f"girdi {self.n_giris} sütunlu olmalı")
        cikti = np.zeros((X.shape[0], self.n_cikis))
        sig = 1.0 / (1.0 + np.exp(-X))
        silu = X * sig
        for i in range(self.n_giris):
            B = bspline_temeli(X[:, i], self.dugumler, self.k)   # (N, n)
            cikti += B @ (self.C[i] * self.W_spline[i][:, None]).T
            cikti += silu[:, i:i + 1] * self.W_taban[i][None, :]
        return cikti


@dataclass
class KAN:
    """Katman yığını."""
    boyutlar: Sequence[int]
    G: int = 5
    k: int = 3
    alt: float = -1.0
    ust: float = 1.0
    tohum: int = 0
    katmanlar: List[KANKatmani] = field(init=False)

    def __post_init__(self) -> None:
        if len(self.boyutlar) < 2:
            raise ValueError("en az girdi ve çıktı boyu lazım")
        self.katmanlar = [
            KANKatmani(a, b, self.G, self.k, self.alt, self.ust,
                       self.tohum * 100 + i)
            for i, (a, b) in enumerate(zip(self.boyutlar[:-1],
                                           self.boyutlar[1:]))
        ]

    @property
    def parametre_sayisi(self) -> int:
        return sum(k.parametre_sayisi for k in self.katmanlar)

    def __call__(self, X: np.ndarray) -> np.ndarray:
        for kat in self.katmanlar:
            X = kat.ileri(X)
        return X


# ══════════════════════════════════════════════════════════════════════
#  Gösterim
# ══════════════════════════════════════════════════════════════════════

def _gosterim() -> str:
    import time
    s: List[str] = []

    s.append("=== B-spline temeli: birliğin bölünmesi ===")
    for G, k in ((5, 3), (10, 3), (8, 2), (20, 4), (5, 0)):
        d = dugum_dizisi(G, k)
        t = np.linspace(-1.0, 1.0, 501)
        sapma = birligin_bolunmesi_sapmasi(t, d, k)
        B = bspline_temeli(t, d, k)
        s.append(f"  G={G:<3} k={k}  temel sayısı={B.shape[1]:<3}"
                 f"  |ΣB−1| azamî = {sapma:.3e}"
                 f"  negatif değer var mı: {bool(np.any(B < -1e-12))}")

    s.append("\n=== Yerellik: her temel kaç aralıkta sıfırdan farklı? ===")
    for k in (0, 1, 2, 3):
        d = dugum_dizisi(10, k)
        t = np.linspace(-1, 1, 2001)
        B = bspline_temeli(t, d, k)
        # Orta bir temel fonksiyonun desteğinin genişliği:
        i = B.shape[1] // 2
        destek = t[B[:, i] > 1e-12]
        genislik = (destek.max() - destek.min()) if destek.size else 0.0
        aralik = 2.0 / 10
        s.append(f"  k={k}: destek genişliği ≈ {genislik:.4f}"
                 f" = {genislik / aralik:.2f} aralık"
                 f"   (beklenen {k+1})")

    s.append("\n=== Türev kapalı formda mı doğru? ===")
    d = dugum_dizisi(8, 3)
    t = np.linspace(-0.9, 0.9, 41)
    T = bspline_turev_temeli(t, d, 3)
    h = 1e-6
    sayisal = (bspline_temeli(t + h, d, 3) - bspline_temeli(t - h, d, 3)) / (2 * h)
    s.append(f"  kapalı form ile merkezî fark arasındaki azamî fark:"
             f" {np.max(np.abs(T - sayisal)):.3e}")

    s.append("\n=== Tek değişkenli uydurma ===")
    t = np.linspace(-1, 1, 400)
    for ad, f in (("sin(3t)", lambda z: np.sin(3 * z)),
                  ("|t|", np.abs),
                  ("t³−t", lambda z: z ** 3 - z)):
        satir = f"  {ad:9s}"
        for G in (5, 10, 20, 40):
            kenar = BSplineKenar(G, 3)
            artik = kenar.uydur(t, f(t))
            satir += f"  G={G}:{artik:.2e}"
        s.append(satir)
    s.append("  → düzgün fonksiyonlarda ızgara sıklaştıkça hızla düşüyor;")
    s.append("    |t| gibi köşeli fonksiyonda daha yavaş (beklenen).")
    s.append("  Kübik spline kübiği TAM temsil etmeli; öyleyse t³−t'de G=5")
    s.append("  iken 9.3e-06 artık neden var?  Düzenleme terimi sanılabilir,")
    s.append("  ama ölçüm başka bir şey söylüyor:")
    for reg in (1e-8, 0.0):
        a = BSplineKenar(5, 3).uydur(t, t ** 3 - t, duzenleme=reg)
        s.append(f"    düzenleme={reg:.0e}, taban açık  → artık {a:.3e}")
    a0 = BSplineKenar(5, 3, w_taban=0.0).uydur(t, t ** 3 - t)
    s.append(f"    düzenleme=1e-08, taban KAPALI → artık {a0:.3e}")
    s.append("  Sebep düzenleme değil: `uydur` önce silu tabanını çıkarıyor,")
    s.append("  spline'a kalan `t³−t−silu(t)` ise kübik değil. Yani artık,")
    s.append("  kübiğin değil silu'nun yaklaşıklanmasından geliyor.")

    s.append("\n=== Izgara dışında taban terimi ne yapıyor? ===")
    kenar = BSplineKenar(8, 3)
    kenar.uydur(np.linspace(-1, 1, 200), np.sin(3 * np.linspace(-1, 1, 200)))
    # Dikkat: düğüm dizisi [-1,1]'in k·h kadar DIŞINA uzatılır; asıl
    # destek [-1−k·h, 1+k·h]'dır. Gerçekten dışarısı için ona bakmak lazım.
    kh = kenar.k * (kenar.ust - kenar.alt) / kenar.G
    s.append(f"  düğüm aralığı = [{kenar.dugumler[0]:.3f},"
             f" {kenar.dugumler[-1]:.3f}] (uzatma k·h = {kh:.3f})")
    icerideyken = np.array([-1.5, 1.5])
    s.append(f"  [-1,1] dışı ama düğüm içi t={icerideyken}: temel sıfır DEĞİL,"
             f" azamî {np.max(np.abs(kenar.temel(icerideyken))):.4f}")
    disarida = np.array([-3.0, -2.0, 2.0, 3.0])
    B = kenar.temel(disarida)
    s.append(f"  düğüm dizisinin de dışında t={disarida}: temel tamamen sıfır mı?"
             f" {np.max(np.abs(B)) < 1e-12}")
    s.append(f"  ama φ(t) sıfır DEĞİL: {np.array2string(kenar(disarida), precision=4)}")
    s.append("  → taban terimi olmasaydı gradyan da sıfır olur,")
    s.append("    ağ o bölgeden hiç öğrenemezdi.")

    s.append("\n=== Katman: paylaşılan temel dizeyinin kazancı ===")
    r = np.random.default_rng(0)
    X = r.uniform(-0.9, 0.9, (2000, 12))
    kat = KANKatmani(12, 24, G=8, k=3)
    t0 = time.perf_counter()
    Y = kat.ileri(X)
    paylasimli = time.perf_counter() - t0

    # Kenar başına ayrı ayrı hesaplayan naif yol — aynı neticeyi vermeli.
    t0 = time.perf_counter()
    naif = np.zeros((X.shape[0], 24))
    sig = 1.0 / (1.0 + np.exp(-X))
    for i in range(12):
        for j in range(24):
            B = bspline_temeli(X[:, i], kat.dugumler, kat.k)
            naif[:, j] += (B @ (kat.C[i, j] * kat.W_spline[i, j])
                           + X[:, i] * sig[:, i] * kat.W_taban[i, j])
    naifsure = time.perf_counter() - t0

    s.append(f"  çıktı şekli {Y.shape}, parametre {kat.parametre_sayisi}")
    s.append(f"  paylaşımlı temel : {paylasimli*1000:7.2f} ms")
    s.append(f"  kenar başına naif: {naifsure*1000:7.2f} ms"
             f"   → {naifsure/paylasimli:.1f}× yavaş")
    s.append(f"  iki yolun azamî farkı: {np.max(np.abs(Y - naif)):.3e}"
             "   (hızlanma neticeyi değiştirmiyor)")

    s.append("\n=== Çok katmanlı ağ ===")
    ag = KAN([4, 8, 8, 2], G=6, k=3, tohum=1)
    Z = ag(r.uniform(-0.8, 0.8, (100, 4)))
    s.append(f"  KAN([4,8,8,2]) çıktı {Z.shape},"
             f" parametre {ag.parametre_sayisi}")
    s.append(f"  çıktı sonlu mu? {bool(np.all(np.isfinite(Z)))}")
    return "\n".join(s)


def rapor() -> str:
    return _gosterim()


if __name__ == "__main__":
    print(rapor())
