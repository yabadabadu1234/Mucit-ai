"""Serbest enerji — değişimsel sınır ve onun doğru yönü.

Gizli ``Z``, gözlenen ``X`` için herhangi bir ``q(z)`` dağılımıyla:

.. math::

   \\ln p(x) = \\underbrace{\\mathbb{E}_q[\\ln p(x,z) - \\ln q(z)]}_{\\text{ELBO}}
              + \\underbrace{D_{\\mathrm{KL}}\\bigl(q(z)\\,\\|\\,p(z|x)\\bigr)}_{\\ge 0}

KL negatif olamadığından **ELBO ≤ ln p(x)**.  Serbest enerji
``F = −ELBO`` olarak tarif edilirse:

.. math::  F \\;\\ge\\; -\\ln p(x)

Yani serbest enerji, sürpriz ``−ln p(x)``'in **üst** sınırıdır; onu
azaltmak sürprizi azaltmanın vekilidir.  İşaret ve yön burada kolayca
ters yazılır; bu modül sınırı **ölçerek** doğrular: kapalı formda
hesaplanabilen bir modelde `F ≥ −ln p(x)` her ``q`` için sınanır ve
eşitliğin **ancak** ``q = p(z|x)`` iken tutulduğu gösterilir.

Ayrıca ayrışım kimliği:

.. math::  F = \\underbrace{-\\mathbb{E}_q \\ln p(x|z)}_{\\text{kesinsizlik}}
             + \\underbrace{D_{\\mathrm{KL}}(q(z)\\|p(z))}_{\\text{karmaşıklık}}

İki terim ayrı ayrı hesaplanır ve toplamlarının ``F``ye eşitliği
sayısal olarak sınanır — kimlik iddia edilmez, tartılır.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = [
    "AyrikModel", "kl", "elbo", "serbest_enerji", "ardil", "kanit_log",
    "serbest_enerji_ayrisimi", "sinir_dogrula", "koordinat_inisi",
    "gauss_kl", "gauss_serbest_enerji",
]

EPS = 1e-300


# ══════════════════════════════════════════════════════════════════════
#  Ayrık model: p(z) ve p(x|z) tablolarla
# ══════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class AyrikModel:
    """``K`` gizli hâl, ``N`` gözlem değeri.

    ``pz``: ``(K,)`` önsel.  ``pxz``: ``(K, N)`` şartlı olabilirlik.
    İkisi de satır bazında toplamı 1 olmak zorundadır; kurulurken
    **denetlenir** — normalize edilmemiş bir tablo bütün büyüklükleri
    sessizce bozar.
    """
    pz: np.ndarray
    pxz: np.ndarray

    def __post_init__(self) -> None:
        object.__setattr__(self, "pz", np.asarray(self.pz, float))
        object.__setattr__(self, "pxz", np.asarray(self.pxz, float))
        if self.pz.ndim != 1 or self.pxz.ndim != 2:
            raise ValueError("pz (K,), pxz (K,N) olmalı")
        if self.pxz.shape[0] != self.pz.size:
            raise ValueError("pz ile pxz'nin K'sı uyuşmuyor")
        if abs(self.pz.sum() - 1.0) > 1e-10:
            raise ValueError("pz toplamı 1 değil")
        if np.any(np.abs(self.pxz.sum(axis=1) - 1.0) > 1e-10):
            raise ValueError("pxz satır toplamları 1 değil")
        if np.any(self.pz < 0) or np.any(self.pxz < 0):
            raise ValueError("olasılıklar negatif olamaz")

    @property
    def K(self) -> int:
        return self.pz.size

    @property
    def N(self) -> int:
        return self.pxz.shape[1]

    def ortak(self, x: int) -> np.ndarray:
        """``p(x, z)`` — ``z`` üzerinde vektör."""
        return self.pz * self.pxz[:, x]


def kl(q: np.ndarray, p: np.ndarray) -> float:
    """``D_KL(q‖p) = Σ q ln(q/p)``.

    ``q_i = 0`` olan terimler ``0 ln 0 = 0`` kabulüyle atlanır (limit
    doğrudur).  ``q_i > 0`` iken ``p_i = 0`` ise KL sonsuzdur ve
    ``inf`` döner — büyük bir sayıyla değiştirilmez, çünkü o hâlde
    sınır da anlamını yitirir ve bunun görünmesi gerekir.
    """
    q = np.asarray(q, float)
    p = np.asarray(p, float)
    m = q > 0
    if np.any(p[m] <= 0):
        return float("inf")
    return float(np.sum(q[m] * (np.log(q[m]) - np.log(p[m]))))


def kanit_log(model: AyrikModel, x: int) -> float:
    """``ln p(x)`` — kapalı form (küçük ayrık modelde toplayarak)."""
    return float(np.log(model.ortak(x).sum()))


def ardil(model: AyrikModel, x: int) -> np.ndarray:
    """Tam ardıl ``p(z|x)`` — ELBO'nun sıkı olduğu tek nokta."""
    o = model.ortak(x)
    return o / o.sum()


def elbo(model: AyrikModel, q: np.ndarray, x: int) -> float:
    """``E_q[ln p(x,z) − ln q(z)]``."""
    q = np.asarray(q, float)
    if abs(q.sum() - 1.0) > 1e-9:
        raise ValueError("q normalize değil")
    o = model.ortak(x)
    m = q > 0
    if np.any(o[m] <= 0):
        return float("-inf")
    return float(np.sum(q[m] * (np.log(o[m]) - np.log(q[m]))))


def serbest_enerji(model: AyrikModel, q: np.ndarray, x: int) -> float:
    """``F = −ELBO``.  Sınır: ``F ≥ −ln p(x)``."""
    return -elbo(model, q, x)


def serbest_enerji_ayrisimi(model: AyrikModel, q: np.ndarray, x: int
                            ) -> Dict[str, float]:
    """``F = kesinsizlik + karmaşıklık`` ayrışımı ve sağlaması."""
    q = np.asarray(q, float)
    m = q > 0
    kesinsizlik = -float(np.sum(q[m] * np.log(np.maximum(model.pxz[m, x],
                                                         EPS))))
    karmasiklik = kl(q, model.pz)
    F = serbest_enerji(model, q, x)
    return {
        "kesinsizlik": kesinsizlik,
        "karmaşıklık": karmasiklik,
        "toplam": kesinsizlik + karmasiklik,
        "F": F,
        "ayrışım_sapması": abs(kesinsizlik + karmasiklik - F),
    }


def sinir_dogrula(model: AyrikModel, x: int, deneme: int = 2000,
                  tohum: int = 0) -> Dict[str, object]:
    """``F ≥ −ln p(x)`` sınırını rastgele ``q``larda tartar.

    Ayrıca **eşitlik ancak ardılda** iddiasını sınar: en küçük boşluk
    veren ``q``, tam ardıla ne kadar yakın?
    """
    r = np.random.default_rng(tohum)
    surpriz = -kanit_log(model, x)
    p_zx = ardil(model, x)
    en_kucuk = float("inf")
    en_kucuk_q: Optional[np.ndarray] = None
    ihlal = 0
    for _ in range(deneme):
        q = r.dirichlet(np.ones(model.K))
        F = serbest_enerji(model, q, x)
        bosluk = F - surpriz
        if bosluk < -1e-12:
            ihlal += 1
        if bosluk < en_kucuk:
            en_kucuk, en_kucuk_q = bosluk, q
    F_ardil = serbest_enerji(model, p_zx, x)
    return {
        "sürpriz −ln p(x)": surpriz,
        "ihlal_sayısı": ihlal,
        "en_küçük_boşluk": en_kucuk,
        "ardılda_boşluk": F_ardil - surpriz,
        "en_iyi_q'nun_ardıla_KL'i": kl(en_kucuk_q, p_zx),
        "boşluk = KL(q‖p(z|x)) mi?": abs(en_kucuk - kl(en_kucuk_q, p_zx)),
    }


def koordinat_inisi(model: AyrikModel, x: int, adim: int = 50,
                    tohum: int = 0) -> Dict[str, object]:
    """``F``yi ``q`` üzerinde azaltmak, ardıla yakınsamalı.

    Kapalı çözümü bilinen bir hâlde gradyan inişine gerek yoktur:
    ``F``nin ``q`` üzerindeki asgarisi doğrudan ``q ∝ p(x,z)``dir.
    Yine de iteratif iniş yazılır ki **yakınsadığı yer** bağımsız
    olarak doğrulanabilsin.
    """
    r = np.random.default_rng(tohum)
    q = r.dirichlet(np.ones(model.K))
    o = model.ortak(x)
    tarih: List[float] = []
    for _ in range(adim):
        tarih.append(serbest_enerji(model, q, x))
        # F(q) = −Σq ln o + Σ q ln q ; ∂F/∂q_k = −ln o_k + ln q_k + 1
        # Lagrange ile normalize edilmiş sabit nokta: q ∝ o (yumuşatılmış)
        hedef = o / o.sum()
        q = 0.5 * q + 0.5 * hedef        # sönümlü, tek adımda atlamasın
        q = q / q.sum()
    tarih.append(serbest_enerji(model, q, x))
    return {
        "son_F": tarih[-1],
        "sürpriz": -kanit_log(model, x),
        "ardıla_KL": kl(q, ardil(model, x)),
        "azalıyor_mu": all(tarih[i] >= tarih[i + 1] - 1e-12
                           for i in range(len(tarih) - 1)),
        "tarih": tarih,
    }


# ══════════════════════════════════════════════════════════════════════
#  Gauss hâli — kapalı formül
# ══════════════════════════════════════════════════════════════════════

def gauss_kl(m1: float, s1: float, m2: float, s2: float) -> float:
    """``D_KL(N(m₁,s₁²) ‖ N(m₂,s₂²))`` — kapalı form.

    .. math::  \\ln\\frac{s_2}{s_1} + \\frac{s_1^2 + (m_1-m_2)^2}{2s_2^2}
               - \\frac12
    """
    if s1 <= 0 or s2 <= 0:
        raise ValueError("standart sapmalar pozitif olmalı")
    return float(np.log(s2 / s1) + (s1 ** 2 + (m1 - m2) ** 2)
                 / (2 * s2 ** 2) - 0.5)


def gauss_serbest_enerji(x: float, m_q: float, s_q: float,
                         m_p: float, s_p: float, s_g: float
                         ) -> Dict[str, float]:
    """Doğrusal Gauss modelinde ``F`` ve kapalı ``−ln p(x)``.

    Model: ``z ~ N(m_p, s_p²)``, ``x | z ~ N(z, s_g²)``.  O hâlde
    ``x ~ N(m_p, s_p² + s_g²)`` (kapalı) ve tam ardıl da Gauss'tur.

    ``F = E_q[−ln p(x|z)] + KL(q‖p(z))`` doğrudan hesaplanır:
    ``E_q[(x−z)²] = (x − m_q)² + s_q²``.
    """
    kesinsizlik = (0.5 * np.log(2 * np.pi * s_g ** 2)
                   + ((x - m_q) ** 2 + s_q ** 2) / (2 * s_g ** 2))
    karmasiklik = gauss_kl(m_q, s_q, m_p, s_p)
    F = float(kesinsizlik + karmasiklik)
    s_x = np.sqrt(s_p ** 2 + s_g ** 2)
    surpriz = float(0.5 * np.log(2 * np.pi * s_x ** 2)
                    + (x - m_p) ** 2 / (2 * s_x ** 2))
    # Tam ardıl: hassasiyetler toplanır
    tau = 1 / s_p ** 2 + 1 / s_g ** 2
    m_ardil = (m_p / s_p ** 2 + x / s_g ** 2) / tau
    s_ardil = np.sqrt(1 / tau)
    return {
        "F": F, "sürpriz": surpriz, "boşluk": F - surpriz,
        "KL(q‖ardıl)": gauss_kl(m_q, s_q, m_ardil, s_ardil),
        "ardıl_ortalama": float(m_ardil), "ardıl_sapma": float(s_ardil),
    }


# ══════════════════════════════════════════════════════════════════════
#  Gösterim
# ══════════════════════════════════════════════════════════════════════

def _gosterim() -> str:
    s: List[str] = []
    model = AyrikModel(
        pz=np.array([0.2, 0.5, 0.3]),
        pxz=np.array([[0.7, 0.2, 0.1],
                      [0.1, 0.6, 0.3],
                      [0.3, 0.3, 0.4]]),
    )
    x = 1

    s.append("=== Ayrık model, x=1 ===")
    s.append(f"  ln p(x)   = {kanit_log(model, x):.10f}")
    s.append(f"  tam ardıl = {np.array2string(ardil(model, x), precision=6)}")

    s.append("\n=== Sınır: F ≥ −ln p(x) ===")
    r = sinir_dogrula(model, x, deneme=5000, tohum=1)
    s.append(f"  sürpriz −ln p(x)      = {r['sürpriz −ln p(x)']:.10f}")
    s.append(f"  5000 rastgele q'da ihlal = {r['ihlal_sayısı']}")
    s.append(f"  en küçük boşluk       = {r['en_küçük_boşluk']:.3e}")
    s.append(f"  ardılda boşluk        = {r['ardılda_boşluk']:.3e}"
             "   (sıfır olmalı — sınır orada sıkı)")
    s.append(f"  boşluk = KL(q‖p(z|x)) özdeşliğinin sapması = "
             f"{r['boşluk = KL(q‖p(z|x)) mi?']:.3e}")

    s.append("\n=== Ayrışım: F = kesinsizlik + karmaşıklık ===")
    for ad, q in (("tam ardıl", ardil(model, x)),
                  ("düz q", np.ones(3) / 3),
                  ("keskin q", np.array([0.98, 0.01, 0.01]))):
        a = serbest_enerji_ayrisimi(model, q, x)
        s.append(f"  {ad:10s} kesinsizlik={a['kesinsizlik']:.6f}"
                 f"  karmaşıklık={a['karmaşıklık']:.6f}"
                 f"  F={a['F']:.6f}  sapma={a['ayrışım_sapması']:.2e}")

    s.append("\n=== Koordinat inişi ardıla varıyor mu? ===")
    ki = koordinat_inisi(model, x, adim=60, tohum=7)
    s.append(f"  son F={ki['son_F']:.10f}  sürpriz={ki['sürpriz']:.10f}")
    s.append(f"  ardıla KL = {ki['ardıla_KL']:.3e}"
             f"   F her adımda azaldı mı? {ki['azalıyor_mu']}")

    s.append("\n=== Gauss hâli (kapalı formüllerle) ===")
    for ad, (mq, sq) in (("q = ardıl", (None, None)),
                         ("q = önsel", (0.0, 1.0)),
                         ("q = kaymış", (2.0, 0.3))):
        if mq is None:
            g0 = gauss_serbest_enerji(1.5, 0.0, 1.0, 0.0, 1.0, 0.5)
            mq, sq = g0["ardıl_ortalama"], g0["ardıl_sapma"]
        g = gauss_serbest_enerji(1.5, mq, sq, 0.0, 1.0, 0.5)
        s.append(f"  {ad:10s} F={g['F']:.8f} sürpriz={g['sürpriz']:.8f}"
                 f" boşluk={g['boşluk']:.3e} KL(q‖ardıl)={g['KL(q‖ardıl)']:.3e}")
    s.append("  → boşluk ile KL(q‖ardıl) her satırda aynı sayı; bu,"
             " sınırın ispatındaki özdeşliğin kendisidir.")
    return "\n".join(s)


def rapor() -> str:
    return _gosterim()


if __name__ == "__main__":
    print(rapor())
