"""Denge — çok failli iktisadî muvazenenin (BGCM) çözümü ve hassasiyeti.

Model: ``n`` fail, her biri kendi faydasını azamîleştiriyor; faaliyeti
``x_i`` ile gösterilir ve diğerlerinin faaliyetine bağlı.  Denge, bütün
faillerin en iyi karşılıklarının **sabit noktası**dır:

.. math::  x_i^\\star = \\arg\\max_{x_i} u_i(x_i, x_{-i}) \\qquad \\forall i

İçsel (interior) bir dengede birinci mertebe şartı sağlanır:

.. math::  F_i(x, \\theta) := \\frac{\\partial u_i}{\\partial x_i}(x, \\theta) = 0

Böylece denge, ``F(x, θ) = 0`` denklem sisteminin köküdür.  Bu modül
üç şeyi yapar:

1. **Kökü bulur** — sönümlü Newton, sayısal Jacobi ile.
2. **Kararlılığı ölçer** — en iyi karşılık dönüşümünün Jacobi'sinin
   spektral yarıçapı ``ρ < 1`` ise denge yerel olarak çekicidir.
3. **Hassasiyeti verir** — *örtük fonksiyon teoremi*:

   .. math::  \\frac{\\partial x^\\star}{\\partial \\theta}
              = -\\bigl(\\partial_x F\\bigr)^{-1}\\,\\partial_\\theta F

   Bu, "parametreyi azıcık oynatırsam denge nereye kayar" sorusunun
   **tam** cevabıdır ve sonlu farkla yeniden çözmekten hem daha hızlı
   hem daha kararlıdır.  ``∂_x F`` tekil ise teoremin şartı sağlanmıyor
   demektir; o hâlde sayı uydurulmaz, ``None`` döner.

Bütün türevler merkezî fark ile alınır (hata ``O(h²)``); adım
``h = ε^{1/3}·max(1,|x|)`` seçilir, ki bu merkezî fark için yuvarlama
ile kesme hatasını dengeleyen mertebedir.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = [
    "Oyun", "merkezi_jakobi", "newton_koku", "denge_bul",
    "spektral_yaricap", "kararli_mi", "ortuk_fonksiyon_turevi",
    "hassasiyet_sonlu_farkla", "en_iyi_karsilik_iterasyonu",
]

EPS = np.finfo(float).eps
_H3 = EPS ** (1.0 / 3.0)


# ══════════════════════════════════════════════════════════════════════
#  Oyun tarifi
# ══════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class Oyun:
    """``n`` failli bir oyun.

    ``F(x, θ)`` birinci mertebe şartlarını verir; içsel dengede sıfırdır.
    ``n`` fail sayısı, ``p`` parametre sayısıdır.
    """
    n: int
    p: int
    F: Callable[[np.ndarray, np.ndarray], np.ndarray]
    ad: str = ""

    def artik(self, x: np.ndarray, teta: np.ndarray) -> float:
        """Birinci mertebe şartlarının ihlali — dengede sıfır."""
        return float(np.linalg.norm(self.F(np.asarray(x, float),
                                           np.asarray(teta, float))))


# ══════════════════════════════════════════════════════════════════════
#  Sayısal türev
# ══════════════════════════════════════════════════════════════════════

def merkezi_jakobi(g: Callable[[np.ndarray], np.ndarray],
                   x: np.ndarray) -> np.ndarray:
    """``g``'nin ``x``teki Jacobi'si, merkezî farkla (hata ``O(h²)``).

    Her koordinat için adım ayrı ölçeklenir: ``h_j = ε^{1/3}·max(1,|x_j|)``.
    Sabit bir ``h`` kullanmak, büyük ve küçük koordinatların bir arada
    bulunduğu hâllerde birinde kesme, diğerinde yuvarlama hatası doğurur.
    """
    x = np.asarray(x, float)
    g0 = np.asarray(g(x), float)
    J = np.empty((g0.size, x.size))
    for j in range(x.size):
        h = _H3 * max(1.0, abs(x[j]))
        arti = x.copy(); arti[j] += h
        eksi = x.copy(); eksi[j] -= h
        # Fiilî adım, kayan noktada yuvarlandıktan sonraki farktır:
        gercek = arti[j] - eksi[j]
        J[:, j] = (np.asarray(g(arti), float)
                   - np.asarray(g(eksi), float)) / gercek
    return J


# ══════════════════════════════════════════════════════════════════════
#  Denge: sönümlü Newton
# ══════════════════════════════════════════════════════════════════════

def newton_koku(g: Callable[[np.ndarray], np.ndarray],
                x0: np.ndarray,
                tol: float = 1e-11,
                azami_adim: int = 100
                ) -> Tuple[np.ndarray, bool, int, float]:
    """``g(x) = 0`` için sönümlü Newton.

    Sönüm (line search) şart: sönümsüz Newton uzak başlangıçlarda
    ıraksayabilir.  Adım, artık normunu **düşürene** kadar yarılanır;
    hiçbir yarılama düşürmüyorsa durulur ve ``yakinsadi=False`` döner —
    yakınsamamış bir sonuç yakınsamış gibi sunulmaz.

    Dönen: ``(x, yakınsadı, adım sayısı, son artık)``.
    """
    x = np.array(x0, float)
    art = float(np.linalg.norm(g(x)))
    for k in range(azami_adim):
        if art < tol:
            return x, True, k, art
        J = merkezi_jakobi(g, x)
        try:
            adim = np.linalg.solve(J, -np.asarray(g(x), float))
        except np.linalg.LinAlgError:
            adim = -np.linalg.lstsq(J, np.asarray(g(x), float), rcond=None)[0]
        t = 1.0
        for _ in range(40):
            yeni = x + t * adim
            yeni_art = float(np.linalg.norm(g(yeni)))
            if yeni_art < art:
                break
            t *= 0.5
        else:
            return x, False, k, art        # hiçbir sönüm düşürmedi
        x, art = yeni, yeni_art
    return x, art < tol, azami_adim, art


def denge_bul(oyun: Oyun, teta: Sequence[float],
              x0: Optional[Sequence[float]] = None,
              tol: float = 1e-11) -> Dict[str, object]:
    """Oyunun içsel dengesini bul ve hâlini bildir."""
    teta = np.asarray(teta, float)
    if teta.size != oyun.p:
        raise ValueError(f"θ boyu {oyun.p} olmalı, {teta.size} verildi")
    baslangic = np.zeros(oyun.n) if x0 is None else np.asarray(x0, float)
    g = lambda x: oyun.F(x, teta)
    x, tamam, adim, art = newton_koku(g, baslangic, tol)
    return {"x": x, "yakınsadı": tamam, "adım": adim, "artık": art,
            "θ": teta}


# ══════════════════════════════════════════════════════════════════════
#  Kararlılık
# ══════════════════════════════════════════════════════════════════════

def spektral_yaricap(M: np.ndarray) -> float:
    """``ρ(M) = max |λ_i|`` — özdeğerlerin azamî mutlak değeri."""
    return float(np.max(np.abs(np.linalg.eigvals(np.asarray(M, float)))))


def kararli_mi(oyun: Oyun, x: np.ndarray, teta: Sequence[float]
               ) -> Dict[str, object]:
    """En iyi karşılık dinamiğinin yerel kararlılığı.

    ``F(x)=0`` sisteminin ``ẋ = F(x)`` akışı olarak kararlılığı,
    ``∂_x F``in özdeğerlerinin **reel kısımlarının negatifliğine**
    bakar (Lyapunov).  Ayrıca en iyi karşılık **iterasyonunun**
    (ayrık zaman) kararlılığı için ``ρ(I + ∂_xF)`` değil, sabit nokta
    dönüşümünün Jacobi'si gerekir; ikisi ayrı sorulardır ve burada
    ikisi de ayrı ayrı bildirilir, biri diğerinin yerine geçmez.
    """
    teta = np.asarray(teta, float)
    J = merkezi_jakobi(lambda z: oyun.F(z, teta), np.asarray(x, float))
    ozd = np.linalg.eigvals(J)
    return {
        "∂ₓF": J,
        "özdeğerler": ozd,
        "akış_kararlı": bool(np.all(ozd.real < -1e-12)),
        "azamî_reel_kısım": float(np.max(ozd.real)),
        "tekil_mi": bool(abs(np.linalg.det(J)) < 1e-12),
    }


def en_iyi_karsilik_iterasyonu(
        en_iyi: Callable[[np.ndarray], np.ndarray],
        x0: Sequence[float], azami: int = 500,
        tol: float = 1e-12) -> Dict[str, object]:
    """``x ← EnİyiKarşılık(x)`` sabit nokta iterasyonu.

    Yakınsarsa dengedir; yakınsamazsa **yakınsamadı** denir.  Ayrıca son
    adımdaki büzülme oranı ölçülür: ``<1`` ise yerel büzülme vardır.
    """
    x = np.asarray(x0, float)
    farklar: List[float] = []
    for k in range(azami):
        y = np.asarray(en_iyi(x), float)
        f = float(np.linalg.norm(y - x))
        farklar.append(f)
        x = y
        if f < tol:
            return {"x": x, "yakınsadı": True, "adım": k + 1,
                    "farklar": farklar,
                    "son_oran": (farklar[-1] / farklar[-2]
                                 if len(farklar) > 1 and farklar[-2] > 0
                                 else 0.0)}
    return {"x": x, "yakınsadı": False, "adım": azami, "farklar": farklar,
            "son_oran": (farklar[-1] / farklar[-2]
                         if len(farklar) > 1 and farklar[-2] > 0 else None)}


# ══════════════════════════════════════════════════════════════════════
#  Hassasiyet — örtük fonksiyon teoremi
# ══════════════════════════════════════════════════════════════════════

def ortuk_fonksiyon_turevi(oyun: Oyun, x: np.ndarray,
                           teta: Sequence[float],
                           tekillik_esigi: float = 1e-10
                           ) -> Optional[np.ndarray]:
    """``∂x*/∂θ = −(∂ₓF)⁻¹ ∂_θF`` — ya da şart sağlanmıyorsa ``None``.

    Örtük fonksiyon teoreminin şartı ``∂ₓF``in tersinir olmasıdır.
    Tekilse denge parametreye göre türevlenebilir bir fonksiyon olmak
    zorunda **değildir**; o hâlde bir sayı uydurmak yerine ``None``
    döndürülür.  Tekillik, koşul sayısıyla ölçülür (determinantla
    değil — determinant ölçekle birlikte patlar).
    """
    x = np.asarray(x, float)
    teta = np.asarray(teta, float)
    Fx = merkezi_jakobi(lambda z: oyun.F(z, teta), x)
    if 1.0 / max(np.linalg.cond(Fx), 1e-300) < tekillik_esigi:
        return None
    Ft = merkezi_jakobi(lambda t: oyun.F(x, t), teta)
    return -np.linalg.solve(Fx, Ft)


def hassasiyet_sonlu_farkla(oyun: Oyun, teta: Sequence[float],
                            x0: Optional[Sequence[float]] = None,
                            h: float = 1e-5) -> np.ndarray:
    """Aynı hassasiyeti dengeyi **yeniden çözerek** hesaplar.

    Örtük fonksiyon teoremiyle çıkanla karşılaştırmak içindir: iki
    bağımsız yol aynı sayıya varmalıdır.  Pahalıdır (her parametre için
    iki tam Newton çözümü), o yüzden asıl yol teoremdir.
    """
    teta = np.asarray(teta, float)
    taban = denge_bul(oyun, teta, x0)["x"]
    D = np.empty((oyun.n, oyun.p))
    for j in range(oyun.p):
        arti = teta.copy(); arti[j] += h
        eksi = teta.copy(); eksi[j] -= h
        xa = denge_bul(oyun, arti, taban)["x"]
        xe = denge_bul(oyun, eksi, taban)["x"]
        D[:, j] = (xa - xe) / (arti[j] - eksi[j])
    return D


# ══════════════════════════════════════════════════════════════════════
#  Gösterim: Cournot oligopolü — dengesi elle de çözülebilir
# ══════════════════════════════════════════════════════════════════════

def cournot(n: int) -> Oyun:
    """``n`` firmalı doğrusal Cournot oyunu.

    Ters talep ``P(Q) = a − b·Q``, maliyet ``c_i·x_i``.  Fayda
    ``u_i = (a − b·Σx)·x_i − c_i x_i``, birinci mertebe şartı:

    .. math::  F_i = a - b\\Bigl(\\sum_j x_j\\Bigr) - b x_i - c_i = 0

    FOC'ları toplayınca ``Q = (na − Σc)/(b(n+1))``, geri koyunca genel
    kapalı çözüm çıkar:

    .. math::  x_i^\\star = \\frac{a - (n+1)c_i + \\sum_j c_j}{b(n+1)}

    Simetrik hâlde (``c_i = c``) bu ``x* = (a−c)/(b(n+1))``e iner.  Bu, sayısal çözümün sağlaması için
    kullanılır — beklenen cevabı bağımsız olarak bilmek şarttır.

    θ = (a, b, c₀, …, c_{n−1}), yani ``p = n + 2``.
    """
    def F(x: np.ndarray, teta: np.ndarray) -> np.ndarray:
        a, b = teta[0], teta[1]
        c = teta[2:]
        Q = float(np.sum(x))
        return a - b * Q - b * x - c

    return Oyun(n=n, p=n + 2, F=F, ad=f"Cournot({n})")


def cournot_kapali_cozum(n: int, a: float, b: float, c: float) -> float:
    """Simetrik Cournot dengesi — kalemle çıkarılan cevap."""
    return (a - c) / (b * (n + 1))


def _gosterim() -> str:
    s: List[str] = []
    n, a, b, c = 4, 10.0, 1.0, 2.0
    oyun = cournot(n)
    teta = np.array([a, b] + [c] * n)

    s.append("=== Cournot dengesi (n=4, a=10, b=1, c=2) ===")
    r = denge_bul(oyun, teta)
    beklenen = cournot_kapali_cozum(n, a, b, c)
    s.append(f"  sayısal x* = {np.array2string(r['x'], precision=10)}")
    s.append(f"  kapalı  x* = {beklenen:.10f}")
    s.append(f"  azamî fark = {np.max(np.abs(r['x'] - beklenen)):.3e}"
             f"   ({r['adım']} Newton adımı, artık {r['artık']:.2e})")

    s.append("\n=== Kararlılık ===")
    k = kararli_mi(oyun, r["x"], teta)
    s.append(f"  ∂ₓF özdeğerlerinin azamî reel kısmı = "
             f"{k['azamî_reel_kısım']:.6f}")
    s.append(f"  akış kararlı mı? {k['akış_kararlı']}   tekil mi? {k['tekil_mi']}")

    s.append("\n=== En iyi karşılık iterasyonu ===")
    def en_iyi(x):
        # x_i = (a − c_i − b·Σ_{j≠i} x_j) / (2b)
        Q = float(np.sum(x))
        return (a - c - b * (Q - x)) / (2 * b)
    it = en_iyi_karsilik_iterasyonu(en_iyi, np.zeros(n))
    s.append(f"  eşzamanlı: yakınsadı={it['yakınsadı']}"
             f" son oran={it['son_oran']:.6f}")
    s.append("  IRAKSIYOR — ve bu bir kusur değil, oyunun kendi hâlidir:")
    s.append("  eşzamanlı en iyi karşılığın Jacobi'si −(n−1)/2·(1−I) yapısında,")
    s.append(f"  spektral yarıçapı (n−1)/2 = {(n - 1) / 2:.1f} > 1 (n≥4 için).")
    s.append("  Newton bu yüzden lazım; yahut sönüm konur:")
    for kappa in (0.5, 0.3):
        sonumlu = lambda x, k=kappa: (1 - k) * x + k * en_iyi(x)
        its = en_iyi_karsilik_iterasyonu(sonumlu, np.zeros(n))
        fark = (np.max(np.abs(its["x"] - r["x"]))
                if its["yakınsadı"] else float("nan"))
        s.append(f"    κ={kappa}: yakınsadı={its['yakınsadı']}"
                 f" adım={its['adım']} oran={its['son_oran']:.4f}"
                 f" Newton'dan fark={fark:.2e}")

    s.append("\n=== Hassasiyet: ∂x*/∂θ ===")
    D = ortuk_fonksiyon_turevi(oyun, r["x"], teta)
    Dsf = hassasiyet_sonlu_farkla(oyun, teta)
    s.append(f"  örtük fonksiyon teoremi ∂x*/∂a = {D[0, 0]:.10f}")
    s.append(f"  sonlu farkla            ∂x*/∂a = {Dsf[0, 0]:.10f}")
    s.append(f"  kapalı çözümden 1/(b(n+1)) = "
             f"{1.0 / (b * (n + 1)):.10f}")
    s.append(f"  iki sayısal yolun azamî farkı = "
             f"{np.max(np.abs(D - Dsf)):.3e}")
    s.append(f"  kendi maliyetine göre ∂x*_0/∂c_0 = {D[0, 2]:.10f}"
             f"   kapalı −n/(b(n+1)) = {-n / (b * (n + 1)):.10f}")

    # Asimetrik hâl: kapalı çözüm x_i = (a − n c_i + Σ_j c_j) / (b(n+1))
    s.append("\n=== Asimetrik maliyetler — kapalı çözümle sağlama ===")
    cc = np.array([1.0, 2.0, 3.0, 4.0])
    teta2 = np.concatenate(([a, b], cc))
    r2 = denge_bul(oyun, teta2)
    # FOC'lar toplanınca Q = (na − Σc)/(b(n+1)); geri koyunca:
    #   x_i = [a − (n+1)c_i + Σc] / (b(n+1))
    kapali = (a - (n + 1) * cc + np.sum(cc)) / (b * (n + 1))
    s.append(f"  sayısal = {np.array2string(r2['x'], precision=8)}")
    s.append(f"  kapalı  = {np.array2string(kapali, precision=8)}")
    s.append(f"  azamî fark = {np.max(np.abs(r2['x'] - kapali)):.3e}")
    D2 = ortuk_fonksiyon_turevi(oyun, r2["x"], teta2)
    s.append(f"  ∂x*_0/∂c_0 = {D2[0, 2]:.10f}"
             f"   kapalı −n/(b(n+1)): {-n / (b * (n + 1)):.10f}")
    s.append(f"  ∂x*_0/∂c_1 = {D2[0, 3]:.10f}"
             f"   kapalı 1/(b(n+1)): {1.0 / (b * (n + 1)):.10f}")

    s.append("\n=== Tekil hâl: teoremin şartı sağlanmazsa ===")
    tekil = Oyun(n=2, p=1, F=lambda x, t: np.array([x[0] + x[1] - t[0],
                                                    x[0] + x[1] - t[0]]))
    s.append("  ∂ₓF tekil (iki denklem aynı) → "
             f"{ortuk_fonksiyon_turevi(tekil, np.array([0.5, 0.5]), [1.0])}")
    s.append("  (sayı uydurulmadı; şart sağlanmadığı bildirildi)")
    return "\n".join(s)


def rapor() -> str:
    return _gosterim()


if __name__ == "__main__":
    print(rapor())
