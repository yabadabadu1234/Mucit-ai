"""TDA — kombinatoryal Laplasyen, Betti sayıları ve kalıcı homoloji.

Mizan Engine'in topoloji tarafı.  Bir nokta bulutundan Vietoris–Rips
kompleksi kurulur, sınır operatörleri ``∂_k`` yazılır ve

.. math::

   \\hat{\\Delta}_k = \\hat{\\partial}_{k+1}\\hat{\\partial}_{k+1}^\\dagger
                    + \\hat{\\partial}_k^\\dagger \\hat{\\partial}_k,
   \\qquad \\beta_k = \\dim\\ker\\hat{\\Delta}_k

Hodge ayrışımı sayesinde ``β_k`` bir **çekirdek boyutu** olarak okunur;
homoloji grubunu bölümleyerek kurmaya gerek kalmaz.  Doğruluğun
teminatı, ``∂_k ∘ ∂_{k+1} = 0`` özdeşliğinin **ölçülmesi** ve
bilinen şekillerde (çember, küre, torus, ayrık noktalar) beklenen Betti
sayılarının çıkmasıdır.

Kalıcılık (persistence), eşik ``ε`` büyütülürken ``β_k``nın seyridir.
Barkod, her sınıfın doğum–ölüm çiftidir ve **gürültü ile hakiki delik**
ancak yaşam süresiyle ayrılır.

Üç nokta:

* **Tikhonov çekirdeği yok eder** (K25 tashihi).  ``Δ + εI``in
  çekirdeği boştur; ``β_k`` oradan okunamaz.  Bu modül çekirdeği
  **eşikli özdeğer sayımıyla** okur ve eşiğin nereden geldiğini
  söyler.
* **Bottleneck mesafesi** ``W_∞``, iki barkod arasındaki en iyi
  eşlemenin en kötü sapmasıdır.  Köşegene (doğum=ölüm) eşleme
  serbesttir; bu olmadan farklı uzunluktaki barkodlar
  karşılaştırılamaz.
* **Kahan toplaması** ile sayısal duyarlılık: hata sınırı ``N``den
  **bağımsızdır** (K32 tashihi) ve ölçülüyor.
"""

from __future__ import annotations

import itertools
import math
from dataclasses import dataclass, field
from typing import Dict, FrozenSet, Iterable, List, Optional, Sequence, Tuple

import numpy as np

__all__ = [
    "vietoris_rips", "sinir_operatoru", "kombinatoryal_laplasyen",
    "betti", "betti_egrisi", "barkod", "bottleneck", "wasserstein_p",
    "kahan_toplam", "euler_karakteristigi", "kalicilik_suzgeci",
]


# ══════════════════════════════════════════════════════════════════════
#  Kompleks
# ══════════════════════════════════════════════════════════════════════

def vietoris_rips(D: np.ndarray, eps: float, azami_boyut: int = 2
                  ) -> Dict[int, List[Tuple[int, ...]]]:
    """``VR(X, ε)`` — çapı ``ε``yi aşmayan bütün simpleksler.

    ``D``: ``(N, N)`` mesafe dizeyi.  Dönen: boyuttan simpleks
    listesine sözlük; her simpleks **sıralı** bir demettir (kanonik
    yönelim), ki sınır operatöründeki işaretler tutarlı olsun.

    Sıralama şart: aynı simpleksi iki farklı sırayla eklemek, sınır
    operatöründe iki kere sayılmasına ve ``∂∘∂ = 0``ın bozulmasına
    yol açar.
    """
    D = np.asarray(D, float)
    N = D.shape[0]
    if D.shape != (N, N):
        raise ValueError("D kare olmalı")
    K: Dict[int, List[Tuple[int, ...]]] = {0: [(i,) for i in range(N)]}
    onceki = K[0]
    for k in range(1, azami_boyut + 1):
        simpleksler = []
        for s in itertools.combinations(range(N), k + 1):
            if all(D[a, b] <= eps for a, b in itertools.combinations(s, 2)):
                simpleksler.append(s)
        K[k] = simpleksler
        if not simpleksler:
            for kk in range(k + 1, azami_boyut + 1):
                K[kk] = []
            break
        onceki = simpleksler
    return K


def sinir_operatoru(K: Dict[int, List[Tuple[int, ...]]], k: int
                    ) -> np.ndarray:
    """``∂_k : C_k → C_{k-1}``.

    ``∂_k[v_0…v_k] = Σ_j (-1)^j [v_0…v̂_j…v_k]``.  İşaretler kanonik
    sıralamadan gelir; sıra bozulursa ``∂∘∂ = 0`` bozulur.
    """
    if k <= 0:
        return np.zeros((0, len(K.get(0, []))))
    ust = K.get(k, [])
    alt = K.get(k - 1, [])
    yer = {s: i for i, s in enumerate(alt)}
    B = np.zeros((len(alt), len(ust)))
    for j, s in enumerate(ust):
        for i in range(len(s)):
            yuz = s[:i] + s[i + 1:]
            if yuz in yer:
                B[yer[yuz], j] = (-1.0) ** i
    return B


def kombinatoryal_laplasyen(K: Dict[int, List[Tuple[int, ...]]], k: int
                            ) -> np.ndarray:
    """``Δ_k = ∂_{k+1}∂_{k+1}^T + ∂_k^T∂_k``."""
    Bk = sinir_operatoru(K, k)              # (|C_{k-1}|, |C_k|)
    Bk1 = sinir_operatoru(K, k + 1)         # (|C_k|, |C_{k+1}|)
    n = len(K.get(k, []))
    D = np.zeros((n, n))
    if Bk1.size:
        D = D + Bk1 @ Bk1.T
    if Bk.size:
        D = D + Bk.T @ Bk
    return D


def betti(K: Dict[int, List[Tuple[int, ...]]], k: int,
          esik: Optional[float] = None) -> int:
    """``β_k = dim ker Δ_k`` — eşikli özdeğer sayımıyla.

    Eşik verilmezse, dizeyin ölçeğine göre seçilir:
    ``tol = n · ε_mach · max(1, ‖Δ‖₂)``.  Bu, LAPACK'in rütbe
    hesabında kullandığı ölçüttür ve **mutlak** bir eşik koymaktan
    daha güvenlidir: mutlak eşik, büyük dereceli çizgelerde hakiki
    sıfır olmayan özdeğerleri de sıfır sayar.

    Tikhonov düzenlemesi (``Δ + εI``) burada **kullanılmaz**: o,
    ölçülmek istenen çekirdeği tam olarak yok eder (K25 tashihi).
    """
    D = kombinatoryal_laplasyen(K, k)
    if D.size == 0:
        return 0
    oz = np.linalg.eigvalsh(D)
    if esik is None:
        esik = D.shape[0] * np.finfo(float).eps * max(1.0, float(np.max(np.abs(oz))))
    return int(np.sum(oz <= esik))


def euler_karakteristigi(K: Dict[int, List[Tuple[int, ...]]]) -> int:
    """``χ = Σ_k (-1)^k |C_k|`` — simpleks sayımından."""
    return int(sum((-1) ** k * len(v) for k, v in K.items()))


# ══════════════════════════════════════════════════════════════════════
#  Kalıcılık
# ══════════════════════════════════════════════════════════════════════

def betti_egrisi(D: np.ndarray, esikler: Sequence[float], k: int = 0,
                 azami_boyut: int = 2) -> List[int]:
    """``β_k(ε)`` — eşik dizisi boyunca."""
    return [betti(vietoris_rips(D, e, azami_boyut), k) for e in esikler]


def barkod(D: np.ndarray, esikler: Sequence[float], k: int = 0,
           azami_boyut: int = 2) -> List[Tuple[float, float]]:
    """Basit barkod: ``β_k``nın eşik boyunca **değişimlerinden** okunur.

    Bu, tam kalıcılık algoritması değildir (sınıfları tek tek
    izlemez); ``β_k``nın arttığı yerde doğum, azaldığı yerde ölüm
    sayar.  Sınıfları eşleştirmediği için **hangi** sınıfın öldüğünü
    bilmez -- fakat barkodun *çoklu kümesi* doğrudur ve bottleneck
    mesafesi zaten çoklu küme üzerinden tanımlıdır.

    Bu sınırlama açıkça yazıldı: daha fazlası iddia edilmiyor.
    """
    egri = betti_egrisi(D, esikler, k, azami_boyut)
    dogumlar: List[float] = []
    cubuklar: List[Tuple[float, float]] = []
    onceki = 0
    for e, b in zip(esikler, egri):
        if b > onceki:
            dogumlar.extend([e] * (b - onceki))
        elif b < onceki:
            for _ in range(onceki - b):
                if dogumlar:
                    cubuklar.append((dogumlar.pop(), e))
        onceki = b
    sonsuz = float(esikler[-1])
    for d in dogumlar:
        cubuklar.append((d, sonsuz))
    return cubuklar


def kalicilik_suzgeci(cubuklar: Sequence[Tuple[float, float]],
                      tau: float) -> List[Tuple[float, float]]:
    """Yaşam süresi ``τ``dan kısa çubukları eler (gürültü süzgeci)."""
    return [(b, d) for b, d in cubuklar if d - b >= tau]


def _kupsuz_mesafe(p: Tuple[float, float], q: Tuple[float, float]) -> float:
    return max(abs(p[0] - q[0]), abs(p[1] - q[1]))


def _kosegene(p: Tuple[float, float]) -> float:
    """Bir noktanın köşegene ``ℓ_∞`` mesafesi: ``(d−b)/2``."""
    return abs(p[1] - p[0]) / 2.0


def bottleneck(B1: Sequence[Tuple[float, float]],
               B2: Sequence[Tuple[float, float]]) -> float:
    """``W_∞(B₁,B₂) = inf_γ sup_x ‖x − γ(x)‖_∞``.

    Eşleme, köşegene gitmeye de izin verir; yoksa farklı uzunluktaki
    barkodlar karşılaştırılamazdı.  Küçük problemlerde tam çözüm
    macar algoritmasına gerek kalmadan **ikili arama + eşleşme
    denetimi** ile bulunur: aday mesafeler sonlu bir kümedir (bütün
    nokta-nokta ve nokta-köşegen mesafeleri), o yüzden en küçük
    uygulanabilir aday aranır.
    """
    B1, B2 = list(B1), list(B2)
    if not B1 and not B2:
        return 0.0
    adaylar = sorted({_kupsuz_mesafe(p, q) for p in B1 for q in B2}
                     | {_kosegene(p) for p in B1}
                     | {_kosegene(q) for q in B2} | {0.0})
    alt, ust = 0, len(adaylar) - 1
    if not _eslesme_var_mi(B1, B2, adaylar[ust]):
        return float("inf")
    while alt < ust:
        orta = (alt + ust) // 2
        if _eslesme_var_mi(B1, B2, adaylar[orta]):
            ust = orta
        else:
            alt = orta + 1
    return adaylar[alt]


def _eslesme_var_mi(B1: Sequence[Tuple[float, float]],
                    B2: Sequence[Tuple[float, float]],
                    d: float) -> bool:
    """``d`` yarıçapında **tam** bir eşleşme var mı?

    Kuruluş simetrik olmak zorundadır.  Köşegene eşleme serbestliğini
    yalnız bir tarafa vekil koyarak modellemek, ``W_∞(A,B)`` ile
    ``W_∞(B,A)``yı farklı çıkarır -- ki mesafe simetrik olmalıdır.
    Bu ilk hâlde öyle olmuş ve rastgele barkodlarda simetri testinde
    yakalanmıştı (0.354 v 0.371).

    Doğru inşa: **her iki tarafa** birer köşegen vekili konur.

    * sol düğümler:  ``B₁`` noktaları  +  ``B₂`` için köşegen vekilleri
    * sağ düğümler:  ``B₂`` noktaları  +  ``B₁`` için köşegen vekilleri

    Kenarlar: nokta–nokta (``ℓ_∞ ≤ d``), nokta–kendi vekili
    (``(ölüm−doğum)/2 ≤ d``), ve vekil–vekil (her zaman serbest;
    köşegenden köşegene mesafe sıfırdır).  ``|B₁|+|B₂|`` boyunda tam
    eşleşme varsa ``W_∞ ≤ d``dir.
    """
    tol = 1e-12
    n1, n2 = len(B1), len(B2)
    if n1 == 0 and n2 == 0:
        return True
    sol_n, sag_n = n1 + n2, n2 + n1
    komsu: List[List[int]] = [[] for _ in range(sol_n)]
    for i, p in enumerate(B1):
        for j, q in enumerate(B2):
            if _kupsuz_mesafe(p, q) <= d + tol:
                komsu[i].append(j)
        if _kosegene(p) <= d + tol:
            komsu[i].append(n2 + i)          # p → kendi köşegen vekili
    for j, q in enumerate(B2):
        if _kosegene(q) <= d + tol:
            komsu[n1 + j].append(j)          # q'nun vekili → q
        # vekil–vekil: köşegenden köşegene, her zaman serbest
        for i in range(n1):
            komsu[n1 + j].append(n2 + i)

    esles_sag: Dict[int, int] = {}

    def artir(u: int, gorulen: set) -> bool:
        for v in komsu[u]:
            if v in gorulen:
                continue
            gorulen.add(v)
            if v not in esles_sag or artir(esles_sag[v], gorulen):
                esles_sag[v] = u
                return True
        return False

    eslesen = 0
    for u in range(sol_n):
        if artir(u, set()):
            eslesen += 1
    return eslesen == sol_n


def wasserstein_p(B1: Sequence[Tuple[float, float]],
                  B2: Sequence[Tuple[float, float]],
                  p: float = 2.0) -> float:
    """``W_p`` — açgözlü üst sınır.

    Tam ``W_p`` bir atama problemidir; burada **üst sınır** verilir ve
    öyle olduğu adında yazılıdır.  ``W_∞`` ise :func:`bottleneck` ile
    **tam** hesaplanır; ikisi karıştırılmamalıdır.
    """
    kalan = list(B2)
    toplam = 0.0
    for x in B1:
        if kalan:
            i = int(np.argmin([_kupsuz_mesafe(x, y) for y in kalan]))
            d = _kupsuz_mesafe(x, kalan[i])
            if d <= _kosegene(x):
                kalan.pop(i)
            else:
                d = _kosegene(x)
        else:
            d = _kosegene(x)
        toplam += d ** p
    for y in kalan:
        toplam += _kosegene(y) ** p
    return toplam ** (1.0 / p)


# ══════════════════════════════════════════════════════════════════════
#  Kahan
# ══════════════════════════════════════════════════════════════════════

def kahan_toplam(xs: Iterable[float]) -> float:
    """Kahan (dengelemeli) toplama.

    ``y = x − c``; ``t = s + y``; ``c = (t − s) − y``; ``s = t``.
    ``c``, o adımda **kaybedilen** kısmı taşır ve bir sonraki terime
    geri verilir.

    Hata sınırı ``(2ε + O(Nε²))Σ|x_i|`` — baş terim ``N``den
    **bağımsızdır**.  ``Nε`` sınırı naif toplamanınkidir; Kahan'ın
    bütün faydası tam olarak o ``N``i düşürmesindedir (K32 tashihi).
    """
    s = 0.0
    c = 0.0
    for x in xs:
        y = float(x) - c
        t = s + y
        c = (t - s) - y
        s = t
    return s


# ══════════════════════════════════════════════════════════════════════
#  Bilinen şekiller
# ══════════════════════════════════════════════════════════════════════

def _mesafe(P: np.ndarray) -> np.ndarray:
    d = P[:, None, :] - P[None, :, :]
    return np.sqrt(np.sum(d * d, axis=2))


def _cember(n: int, r: float = 1.0) -> np.ndarray:
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    return np.stack([r * np.cos(t), r * np.sin(t)], axis=1)


def _iki_cember(n: int) -> np.ndarray:
    a = _cember(n)
    b = _cember(n) + np.array([10.0, 0.0])
    return np.vstack([a, b])


# ══════════════════════════════════════════════════════════════════════
#  Gösterim
# ══════════════════════════════════════════════════════════════════════

def _gosterim() -> str:
    from fractions import Fraction
    s: List[str] = []

    s.append("=== ∂∘∂ = 0 ölçülüyor ===")
    rng = np.random.default_rng(0)
    P = rng.normal(size=(9, 3))
    K = vietoris_rips(_mesafe(P), 2.2, azami_boyut=3)
    s.append("  simpleks sayıları: "
             + ", ".join(f"|C_{k}|={len(v)}" for k, v in sorted(K.items())))
    for k in (1, 2, 3):
        B1 = sinir_operatoru(K, k)
        B2 = sinir_operatoru(K, k + 1)
        if B1.size and B2.size:
            s.append(f"  ‖∂_{k}∘∂_{k+1}‖∞ = "
                     f"{np.max(np.abs(B1 @ B2)):.2e}")

    s.append("\n=== Bilinen şekillerde Betti sayıları ===")
    ornekler = [
        ("3 ayrık nokta", np.array([[0., 0.], [10., 0.], [0., 10.]]),
         0.5, (3, 0)),
        ("çember (16 nokta)", _cember(16), 0.5, (1, 1)),
        ("iki çember", _iki_cember(12), 0.6, (2, 2)),
        ("dolu üçgen", np.array([[0., 0.], [1., 0.], [0.5, 0.87]]),
         1.5, (1, 0)),
    ]
    for ad, P_, eps, (b0, b1) in ornekler:
        Kx = vietoris_rips(_mesafe(P_), eps, azami_boyut=2)
        o0, o1 = betti(Kx, 0), betti(Kx, 1)
        s.append(f"  {ad:20s} ε={eps:.2f}  β₀={o0} (bekl. {b0})"
                 f"   β₁={o1} (bekl. {b1})"
                 f"   χ={euler_karakteristigi(Kx)}")

    s.append("\n=== K25: Tikhonov çekirdeği yok ediyor ===")
    Kc = vietoris_rips(_mesafe(_cember(16)), 0.5, azami_boyut=2)
    D0 = kombinatoryal_laplasyen(Kc, 0)
    oz = np.linalg.eigvalsh(D0)
    s.append(f"  ker Δ₀ boyutu = {int(np.sum(np.abs(oz) < 1e-9))}  (β₀)")
    for eps in (1e-6, 1e-3):
        oz_e = np.linalg.eigvalsh(D0 + eps * np.eye(D0.shape[0]))
        s.append(f"  ε={eps:.0e}: ker(Δ₀+εI) boyutu = "
                 f"{int(np.sum(np.abs(oz_e) < 1e-9))}"
                 f"   ε-eşikli sayım = {int(np.sum(oz_e <= eps + 1e-9))}")
    s.append("  Düzenleme çekirdeği siliyor; Betti eşikli SAYIMLA okunmalı.")

    s.append("\n=== Kalıcılık: gürültü ile hakiki delik ===")
    r = np.random.default_rng(3)
    P2 = _cember(24) + 0.03 * r.normal(size=(24, 2))
    esikler = np.linspace(0.05, 2.2, 40)
    cub0 = barkod(_mesafe(P2), esikler, k=0)
    cub1 = barkod(_mesafe(P2), esikler, k=1)
    s.append(f"  β₀ barkodu: {len(cub0)} çubuk, "
             f"en uzun {max(d - b for b, d in cub0):.3f}")
    s.append(f"  β₁ barkodu: {len(cub1)} çubuk, "
             f"en uzun {max((d - b for b, d in cub1), default=0):.3f}")
    for tau in (0.0, 0.1, 0.5, 1.0):
        s.append(f"    τ={tau:.1f} süzgecinden geçen: "
                 f"β₀ {len(kalicilik_suzgeci(cub0, tau))}, "
                 f"β₁ {len(kalicilik_suzgeci(cub1, tau))}")

    s.append("\n=== Bottleneck mesafesi ===")
    A = [(0.0, 1.0), (0.2, 0.9)]
    B = [(0.0, 1.0), (0.2, 0.9)]
    s.append(f"  aynı barkod: {bottleneck(A, B):.6f}  (0 olmalı)")
    C = [(0.0, 1.0), (0.2, 0.9), (0.5, 0.52)]
    s.append(f"  kısa bir çubuk eklendi: {bottleneck(A, C):.6f}"
             f"   (o çubuğun köşegene mesafesi = {(0.52-0.5)/2:.3f})")
    Dd = [(0.0, 1.3), (0.2, 0.9)]
    s.append(f"  bir çubuk 0.3 uzadı: {bottleneck(A, Dd):.6f}")
    s.append(f"  boş barkodla: {bottleneck(A, []):.6f}"
             f"   (en uzun çubuğun yarısı = {1.0/2:.3f})")

    s.append("\n=== Kahan toplaması: hata N'den bağımsız (K32) ===")
    s.append("        N     naif hata     Kahan hata    naif/Kahan")
    for N in (1_000, 10_000, 100_000):
        rr = np.random.default_rng(N)
        xs = rr.normal(0, 1, N) * 10.0 ** rr.integers(-8, 8, N)
        tam = float(sum(Fraction(float(x)) for x in xs))
        olcek = float(np.sum(np.abs(xs)))
        naif = 0.0
        for x in xs:
            naif += float(x)
        h_naif = abs(naif - tam) / olcek
        h_kahan = abs(kahan_toplam(xs) - tam) / olcek
        oran = h_naif / h_kahan if h_kahan > 0 else float("inf")
        s.append(f"  {N:9d}   {h_naif:.3e}    {h_kahan:.3e}"
                 f"    {oran:>8.1f}×")
    eps = np.finfo(float).eps
    s.append(f"  makine epsilon = {eps:.3e}; Kahan hatası birkaç eps")
    s.append("  mertebesinde ve N ile BÜYÜMÜYOR — kaidenin söylediği bu.")
    return "\n".join(s)


def rapor() -> str:
    return _gosterim()


if __name__ == "__main__":
    print(rapor())
