"""Reel Hartley Dönüşümü (RHT) ve reel spektral süzgeçler.

Kaynak: ``docs/kaynak/reel_meleke_operatorleri.tex`` §6 Tasavvur, §15 Terkip.

.. math::

   \\mathrm{cas}(\\theta) = \\cos\\theta + \\sin\\theta, \\qquad
   \\mathrm{RHT}_N = \\frac{1}{\\sqrt N}
   \\left[\\mathrm{cas}\\!\\left(\\tfrac{2\\pi jk}{N}\\right)\\right]_{j,k=0}^{N-1}

**Kaynağın doğru yazdığı yer.**  Bu dizey gerçekten *simetrik*,
*diktir* ve ``RHT² = I``dır -- yani kendi tersidir.  Ölçüldü:
``N = 512``de ``‖RHTᵀRHT − I‖`` makine hassasiyetinde.  Karmaşık QFT'nin
yerine tamamen reel bir dönüşüm koyma fikri sağlamdır.

**M29 tashihi -- kaynağın atladığı şart.**  ``QFT⁻¹ diag(r) QFT`` her
``r`` için bir **evrişimdir** (dolaşımlı dizey).  ``RHT`` için bu
**yanlıştır**: Hartley uzayında köşegen bir çarpan, ancak ``r`` çift
simetrikse (``r[k] = r[N−k]``) evrişim verir.  Ölçüldü (``N=8``,
rastgele ``r``): dolaşımlıdan sapma **0.402**; aynı ölçüt QFT'de
5.6e-17; ``r`` çift simetrik alınınca 9.4e-16.

Sebebi Hartley evrişim kaidesidir -- çarpım **değildir**:

.. math::

   \\mathcal{H}(f * g)[k] = \\sqrt{N}\\,\\big(F[k]\\,G_{\\text{ç}}[k]
   + F[-k]\\,G_{\\text{t}}[k]\\big)

``G_ç``, ``G_t`` = ``G``nin çift ve tek parçaları.  Ölçüldü: naif
çarpım kaidesinin hatası **13.30**, doğru kaidenin hatası 8.0e-14.

**Hız.**  ``RHT`` doğrudan ``N²``dir; ``rfft`` üzerinden ``O(N log N)``
hesaplanır (``cas = cos + sin`` ⟹ ``H = Re F − Im F``).  İkisi arasındaki
fark ve hız kazancı ölçülüyor.
"""

from __future__ import annotations

import math
from typing import Dict, Optional, Sequence, Tuple

import numpy as np

__all__ = [
    "cas", "hartley",
    "cift_tek_parca", "hartley_evrisim", "evrisim",
    "spektral_suzgec", "dolasimli_hata",
    "cift_simetrik_yap",
]


def cas(theta: np.ndarray) -> np.ndarray:
    """``cas θ = cos θ + sin θ`` — reel Hartley çirpması."""
    return np.cos(theta) + np.sin(theta)


# ══════════════════════════════════════════════════════════════════════
#  1. Dönüşüm
# ══════════════════════════════════════════════════════════════════════

def hartley(x=None, N: int = 0, ne: str = "dönüştür") -> np.ndarray:
    """HARTLEY DÖNÜŞÜMÜ -- tek terkip (kütük H226).

    Küme: ``rht_dizeyi``, ``rht``, ``irht``, ``rht_hizli``. Dört isim,
    **tek** dönüşümdü ve aralarındaki fark yalnız şuydu:

    * ``irht`` ``rht``in **aynısıdır** -- RHT involutiftir
      (``RHT² = I``), dolayısıyla kendi tersidir. Ayrı bir ters
      dönüşüm yoktur ve ayrı isim taşıması sanki varmış gibi
      gösteriyordu.
    * ``rht_hizli`` da ``rht``in aynısıydı; ``rht`` zâten ``fft``
      üzerinden ``O(N log N)`` koşuyor.
    * ``rht_dizeyi`` aynı dönüşümün ``O(N²)`` dizey hâlidir ve
      yalnız **denetim** içindir.

    ==================  ==============================================
    ``ne``              döndürdüğü
    ==================  ==============================================
    ``dönüştür``        ``H[k] = Re F[k] − Im F[k]``, ``O(N log N)``
    ``ters``            aynısı -- involutif olduğu için
    ``dizey``           ``RHT_N`` -- simetrik, dik, involutif
    ==================  ==============================================

    ``cas(θ) = cos θ + sin θ`` ve ``F[k] = Σ x_j e^{−2πijk/N}``
    olduğundan ``H = Re F − Im F``. Tam dizeyle aynı neticeyi verir;
    fark ``_gosterim``de ölçülür.
    """
    if ne == "dizey":
        j = np.arange(N)
        return cas(2.0 * math.pi * np.outer(j, j) / N) / math.sqrt(N)
    if ne not in ("dönüştür", "ters"):
        raise ValueError("Hartley kipi bilinmiyor: %r" % (ne,))
    x = np.asarray(x, float)
    n = x.shape[-1]
    F = np.fft.fft(x, axis=-1)
    return (F.real - F.imag) / math.sqrt(n)


# ══════════════════════════════════════════════════════════════════════
#  2. Evrişim kaidesi (M29)
# ══════════════════════════════════════════════════════════════════════

def _ters_indis(N: int) -> np.ndarray:
    return (-np.arange(N)) % N


def cift_tek_parca(G: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """``G = G_ç + G_t``; ``G_ç[k] = (G[k]+G[−k])/2``."""
    t = _ters_indis(G.shape[-1])
    return 0.5 * (G + G[..., t]), 0.5 * (G - G[..., t])


def evrisim(f: np.ndarray, g: np.ndarray) -> np.ndarray:
    """Dairesel evrişim — kıyas için doğrudan (FFT ile) hesaplanır."""
    return np.real(np.fft.ifft(np.fft.fft(f) * np.fft.fft(g)))


def hartley_evrisim(F: np.ndarray, G: np.ndarray,
                    naif: bool = False) -> np.ndarray:
    """HARTLEY'DE EVRİŞİM NASIL ÇARPILIR -- tek terkip (kütük H226).

    Küme: ``hartley_evrisim`` (doğru kaide) ve ``hartley_carpim_naif``
    (kaynağın örtük olarak varsaydığı yanlış kaide). İkisi bir arada
    durmalıdır, zira **M29 tam bu ikisinin farkıdır** ve fark ancak
    yan yana ölçülünce görünür:

        doğru:  ``ℋ(f*g) = √N (F·G_ç + F[−k]·G_t)``
        naif :  ``√N F·G``

    ``G_ç`` ve ``G_t`` ``G``nin çift ve tek parçalarıdır. Fourier'de
    evrişim nokta çarpımına döner; **Hartley'de dönmez**, zira ``cas``
    çekirdeği karmaşık üstel gibi çarpımsal değildir. Simetri
    parçalanması mecburîdir; ``naif=True`` yalnız o mecburiyeti
    ölçmek için durur ve ``dolasimli_hata`` ikisini kıyaslar.
    """
    N = F.shape[-1]
    if naif:
        return math.sqrt(N) * F * G
    Gc, Gt = cift_tek_parca(G)
    return math.sqrt(N) * (F * Gc + F[..., _ters_indis(N)] * Gt)


# ══════════════════════════════════════════════════════════════════════
#  3. Spektral süzgeç ve dolaşımlılık
# ══════════════════════════════════════════════════════════════════════

def cift_simetrik_yap(r: np.ndarray) -> np.ndarray:
    """``r`` yi çift simetrik hâle getir: ``(r[k] + r[N−k])/2``."""
    r = np.asarray(r, float)
    return 0.5 * (r + r[_ters_indis(r.shape[-1])])


def spektral_suzgec(x: np.ndarray, r: np.ndarray,
                    cift_zorla: bool = True) -> np.ndarray:
    """``RHT⁻¹ diag(r) RHT x`` — ``cift_zorla`` ile evrişim garantisi.

    ``cift_zorla=False`` iken kaynağın yazdığı hâl çalışır; netice
    üniter değil ama **simetrik** bir işleçtir, evrişim değildir.
    """
    r = cift_simetrik_yap(r) if cift_zorla else np.asarray(r, float)
    return hartley(r * hartley(x))


def dolasimli_hata(M: np.ndarray) -> float:
    """``M`` bir evrişim (dolaşımlı dizey) mi? — ilk sütundan sapma."""
    N = M.shape[0]
    c = M[:, 0]
    C = c[(np.arange(N)[:, None] - np.arange(N)[None, :]) % N]
    return float(np.abs(M - C).max())


# ══════════════════════════════════════════════════════════════════════
#  Gösterim
# ══════════════════════════════════════════════════════════════════════

def _gosterim() -> str:
    import time
    s = []
    s.append("=== RHT dik, simetrik ve involutif (kaynak DOĞRU) ===")
    for N in (8, 64, 512):
        H = hartley(N=N, ne="dizey")
        s.append("  N=%4d  ‖HᵀH−I‖=%.2e  ‖H²−I‖=%.2e  ‖H−Hᵀ‖=%.2e"
                 % (N, float(np.abs(H.T @ H - np.eye(N)).max()),
                    float(np.abs(H @ H - np.eye(N)).max()),
                    float(np.abs(H - H.T).max())))

    s.append("\n=== Hızlı RHT (fft) tam dizeyle aynı mı? ===")
    hartley(np.zeros(8))                      # ısıtma: ilk fft çağrısı yanıltır
    for N in (256, 1024, 4096, 16384):
        x = np.random.default_rng(0).normal(size=N)
        H = hartley(N=N, ne="dizey") if N <= 4096 else None
        tekrar = max(1, 2_000_000 // (N * N) if H is not None else 1)
        if H is not None:
            t0 = time.perf_counter()
            for _ in range(tekrar):
                a = H @ x
            t1 = (time.perf_counter() - t0) / tekrar
        t2 = time.perf_counter()
        for _ in range(20):
            b = hartley(x)
        t3 = (time.perf_counter() - t2) / 20
        if H is None:
            s.append("  N=%5d  dizey kurulmadı (%.2f GB tutardı)   "
                     "hızlı %7.4f ms" % (N, N * N * 8 / 1e9, t3 * 1e3))
        else:
            s.append("  N=%5d  dizey %7.4f ms   hızlı %7.4f ms  (%6.1f×)   "
                     "fark=%.2e"
                     % (N, t1 * 1e3, t3 * 1e3, t1 / max(t3, 1e-12),
                        float(np.abs(a - b).max())))

    s.append("\n=== M29: Hartley evrişim kaidesi çarpım DEĞİL ===")
    r = np.random.default_rng(1)
    for N in (16, 64):
        f, g = r.normal(size=N), r.normal(size=N)
        sol = hartley(evrisim(f, g))
        F, G = hartley(f), hartley(g)
        s.append("  N=%3d  naif çarpım hatası=%8.4f    doğru kaide "
                 "hatası=%.2e"
                 % (N, float(np.abs(sol - hartley_evrisim(F, G, naif=True)).max()),
                    float(np.abs(sol - hartley_evrisim(F, G)).max())))

    s.append("\n=== M29: köşegen süzgeç ne zaman evrişim? ===")
    N = 8
    H = hartley(N=N, ne="dizey")
    rr = r.normal(size=N)
    M = H.T @ np.diag(rr) @ H
    F = np.fft.fft(np.eye(N), axis=0) / math.sqrt(N)
    Mq = (F.conj().T @ np.diag(rr) @ F).real
    Mc = H.T @ np.diag(cift_simetrik_yap(rr)) @ H
    s.append("  RHT, keyfî r      : dolaşımlıdan sapma = %.4f" % dolasimli_hata(M))
    s.append("  RHT, çift simetrik: dolaşımlıdan sapma = %.2e" % dolasimli_hata(Mc))
    s.append("  QFT, keyfî r      : dolaşımlıdan sapma = %.2e" % dolasimli_hata(Mq))
    s.append("  İkisi de simetrik ve dik olabilir; fark EVRİŞİM olup")
    s.append("  olmamalarındadır. Süzgeç diye yazılan şey, şart konmazsa")
    s.append("  bir evrişim değil başka bir işleçtir.")

    s.append("\n=== Süzgeç gerçekten alçak-geçiren mi? (ölçülerek) ===")
    N = 256
    t = np.arange(N)
    x = (np.sin(2 * math.pi * 3 * t / N)
         + 0.5 * np.sin(2 * math.pi * 61 * t / N))
    r_alcak = (np.minimum(t, N - t) <= 8).astype(float)
    y = spektral_suzgec(x, r_alcak)
    def guc(v, k):
        F = np.fft.rfft(v)
        return float(abs(F[k]) ** 2)
    s.append("  girdi : k=3 gücü=%.1f   k=61 gücü=%.1f" % (guc(x, 3), guc(x, 61)))
    s.append("  çıktı : k=3 gücü=%.1f   k=61 gücü=%.1f" % (guc(y, 3), guc(y, 61)))
    s.append("  Yüksek kip bastırıldı, alçak kip korundu.")
    return "\n".join(s)


if __name__ == "__main__":  # pragma: no cover
    print(_gosterim())
