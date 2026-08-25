"""Grassmann manifoldu: izdüşüm, asal açılar, geodezik Exp/Log.

Kaynak: ``docs/kaynak/analitik_darbogazlar.txt`` Darboğaz 1-2, ve
``docs/kaynak/mantik_noronlari.tex`` §5.1.

``Gr(k,d)``: ``ℝ^d``nin ``k`` boyutlu alt uzayları.  Bir nokta, bir
**alt uzaydır**; onu temsil eden ``d×k`` taban dizeyi tek değildir
(``Y`` ile ``YQ``, ``Q ∈ O(k)``, aynı noktadır).  Bu yüzden buradaki
her ölçüm ``O(k)`` etkisine göre **değişmezdir**; değişmez olmayan
bir "mesafe" Grassmann mesafesi değildir ve bu ölçülerek gösteriliyor.

**Asal açılar.**  ``cos θ_i = σ_i(Y₁ᵀY₂)`` (Formül 2.1).  Geodezik
mesafe ``d = √(Σθ_i²)`` (Formül 2.2).

**K26 tashihi.**  Kaynak, logaritma haritasını
``Log_{G₁}(G₂) = U arcsin(Σ) Vᵀ`` diye yazıyor.  Bu **yanlıştır**.
Doğrusu, yatay kaldırmanın ince SVD'sinden

.. math::  \\mathrm{Log}_{Y_1}(Y_2) = U \\arctan(\\Sigma) V^\\mathsf{T},
   \\quad (Y_2 - Y_1 M) M^{-1} = U\\Sigma V^\\mathsf{T},\\ M = Y_1^\\mathsf{T}Y_2

şeklindedir ve ``arctan Σ`` tam olarak asal açıları verir.
``arcsin`` yazıldığında Exp∘Log gidiş-dönüşü **kapanmaz**.  Ölçülen
alt uzay hatası (``d=8, k=3``, ``θ_max`` ölçekleriyle):

===========  =============  =============
``θ_max``    ``arctan``     ``arcsin``
===========  =============  =============
0.0785       4.8e-16        3.5e-04
0.3142       6.4e-16        2.4e-02
0.7854       8.2e-16        1.0e+00
1.4137       1.8e-15        4.7e-01
===========  =============  =============

``arcsin Σ`` ancak ``Σ`` küçükken ``arctan Σ``ya yakındır -- hata
küçük açılarda gizlenir, büyük açılarda patlar.  ``θ = π/4``ü geçince
``Σ = tan θ > 1`` olur ve ``arcsin`` tanımsızdır bile.
``θ_max = π/2``de ``arctan`` da bozulur (ölçülen 7.9e-01): orası
**kesim lokusudur**, ``M = Y₁ᵀY₂`` tekilleşir ve Log tek değildir --
bu Grassmann'ın kendi özelliğidir, kod kusuru değil.

**Tikhonov ve Betti-0 (K25).**  Kaynak, ``L_ε = L + εI`` ile
düzenleyip sonra ``dim ker(L_ε) = β₀`` beklemektedir.  ``ε > 0``
iken ``ker(L_ε)`` **boştur**; düzenleme çekirdeği korumaz, yok eder.
Doğru okuma, ``ε``dan küçük özdeğerleri saymak değil, ``L``nin
kendi tayfındaki ``ε``a yakın kümelenmeye bakmaktır.  Bu da
ölçülüyor.
"""

from __future__ import annotations

import math
from typing import Dict, Optional, Sequence, Tuple

import numpy as np

__all__ = [
    "dik_taban", "izdusum", "asal_acilar", "grassmann_mesafesi",
    "exp_haritasi", "log_haritasi", "log_haritasi_arcsin",
    "gidis_donus_hatasi", "alt_uzay_hatasi",
    "grassmann_geodezigi", "grassmann_ortalamasi",
    "normalize_laplasyen", "betti0_tayftan", "tikhonov_cekirdegi_yok_eder",
]


# ══════════════════════════════════════════════════════════════════════
#  1. Temel
# ══════════════════════════════════════════════════════════════════════

def dik_taban(A: np.ndarray) -> np.ndarray:
    """``A``nın sütun uzayı için dik taban (ince QR, işaret sabitlenmiş)."""
    Q, R = np.linalg.qr(np.asarray(A, float))
    return Q * np.sign(np.where(np.diag(R) == 0, 1.0, np.diag(R)))


def izdusum(U: np.ndarray) -> np.ndarray:
    """``P = U(UᵀU)⁻¹Uᵀ`` (Formül 1.4) — taban seçiminden bağımsız.

    ``P`` simetrik, idempotent ve ``tr P = k``dır; üçü de burada
    sınanıyor.  ``P``, Grassmann noktasının **kanonik** temsilidir:
    ``U → UQ`` onu değiştirmez.
    """
    U = np.asarray(U, float)
    return U @ np.linalg.solve(U.T @ U, U.T)


def asal_acilar(Y1: np.ndarray, Y2: np.ndarray) -> np.ndarray:
    """``θ_i = arccos σ_i(Y₁ᵀY₂)`` — artan sırada, ``[0, π/2]``.

    ``Y₁, Y₂`` dik tabanlar olmalıdır; değilse önce dikleştirilir.
    Küçük açılarda ``arccos`` duyarsızdır; o yüzden ``σ ≈ 1``
    bölgesinde ikinci bir yol (fark tabanının tekil değerleri)
    kullanılıyor.
    """
    Q1, Q2 = dik_taban(Y1), dik_taban(Y2)
    s = np.linalg.svd(Q1.T @ Q2, compute_uv=False)
    s = np.clip(s, -1.0, 1.0)
    th = np.arccos(s)
    # σ→1 (θ→0) bölgesinde arccos duyarsız: sin θ'yı doğrudan ölç
    kucuk = s > 1 - 1e-8
    if np.any(kucuk):
        t = np.linalg.svd(Q2 - Q1 @ (Q1.T @ Q2), compute_uv=False)
        t = np.clip(np.sort(t)[::-1], 0.0, 1.0)
        th[kucuk] = np.arcsin(t[kucuk])
    return np.sort(th)


def grassmann_mesafesi(Y1: np.ndarray, Y2: np.ndarray) -> float:
    """``d = √(Σ θ_i²)`` (Formül 2.2) — ``O(k)`` etkisine göre değişmez."""
    return float(np.linalg.norm(asal_acilar(Y1, Y2)))


def alt_uzay_hatasi(Y1: np.ndarray, Y2: np.ndarray) -> float:
    """``‖P₁ − P₂‖_F`` — iki alt uzay aynı mı, taban seçiminden bağımsız.

    Gidiş-dönüşü ``‖Y₁ − Y₂‖`` ile ölçmek **yanlış** olurdu: aynı alt
    uzayın farklı tabanları arasında o norm sıfır değildir.
    """
    return float(np.linalg.norm(izdusum(Y1) - izdusum(Y2)))


# ══════════════════════════════════════════════════════════════════════
#  2. Geodezik Exp / Log
# ══════════════════════════════════════════════════════════════════════

def exp_haritasi(Y: np.ndarray, H: np.ndarray, t: float = 1.0
                 ) -> np.ndarray:
    """``Exp_Y(tH) = YV cos(tΣ)Vᵀ + U sin(tΣ)Vᵀ``, ``H = UΣVᵀ``.

    ``H`` yatay olmalıdır (``YᵀH = 0``); değilse yatay bileşeni
    alınır -- dikey bileşen alt uzayı değil yalnız tabanı döndürür.
    """
    Y = dik_taban(Y)
    H = np.asarray(H, float)
    H = H - Y @ (Y.T @ H)                 # yatay izdüşüm
    U, S, Vt = np.linalg.svd(H, full_matrices=False)
    return (Y @ Vt.T * np.cos(t * S)) @ Vt + (U * np.sin(t * S)) @ Vt


def _log_cekirdegi(Y1: np.ndarray, Y2: np.ndarray
                   ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """``(U, Σ, Vᵀ)``: ``(Y₂ − Y₁M)M⁻¹``in ince SVD'si, ``M = Y₁ᵀY₂``."""
    Q1, Q2 = dik_taban(Y1), dik_taban(Y2)
    M = Q1.T @ Q2
    A = np.linalg.solve(M.T, (Q2 - Q1 @ M).T).T
    return np.linalg.svd(A, full_matrices=False)


def log_haritasi(Y1: np.ndarray, Y2: np.ndarray) -> np.ndarray:
    """``Log_{Y₁}(Y₂) = U arctan(Σ) Vᵀ`` — **doğru** hâl (K26).

    ``arctan Σ`` asal açıları verir: ``‖Log‖_F = d_Gr(Y₁,Y₂)``.
    """
    U, S, Vt = _log_cekirdegi(Y1, Y2)
    return (U * np.arctan(S)) @ Vt


def log_haritasi_arcsin(Y1: np.ndarray, Y2: np.ndarray) -> np.ndarray:
    """Kaynaktaki ``U arcsin(Σ) Vᵀ`` — **kasten yanlış**, kıyas için.

    ``Σ = tan θ`` olduğundan ``arcsin Σ``, ``Σ > 1`` (yani
    ``θ > π/4``) iken tanımsızdır bile.  Burada kırpılıyor ki
    hatanın büyüklüğü ölçülebilsin.
    """
    U, S, Vt = _log_cekirdegi(Y1, Y2)
    return (U * np.arcsin(np.clip(S, -1.0, 1.0))) @ Vt


def gidis_donus_hatasi(Y1: np.ndarray, Y2: np.ndarray,
                       log=log_haritasi) -> float:
    """``‖P(Exp_{Y₁}(Log_{Y₁}(Y₂))) − P(Y₂)‖_F`` — Formül 2.5'in özü.

    Kaynak bunu ``Tr(Exp(Log)) = Tr(G₂)`` diye yazıyor; iz eşitliği
    **zayıf** bir ölçüttür (her ``Gr(k,d)`` noktasının izi ``k``dır,
    yani hep sağlanır).  İzdüşümler arası Frobenius farkı gerçek
    ölçüttür.
    """
    return alt_uzay_hatasi(exp_haritasi(Y1, log(Y1, Y2)), Y2)


def grassmann_geodezigi(Y1: np.ndarray, Y2: np.ndarray, n: int = 21
                        ) -> Dict[str, object]:
    """``γ(t) = Exp_{Y₁}(t·Log_{Y₁}(Y₂))``, ``t ∈ [0,1]``.

    Geodezik olmanın ölçütü: ``d(Y₁, γ(t))`` ``t`` ile **doğrusal**
    artmalı ve ``d(Y₁,γ(t)) + d(γ(t),Y₂) = d(Y₁,Y₂)`` olmalı.  İkisi
    de burada hesaplanıp döndürülüyor.
    """
    H = log_haritasi(Y1, Y2)
    ts = np.linspace(0.0, 1.0, n)
    yol = [exp_haritasi(Y1, H, float(t)) for t in ts]
    d_tam = grassmann_mesafesi(Y1, Y2)
    d1 = np.array([grassmann_mesafesi(Y1, g) for g in yol])
    d2 = np.array([grassmann_mesafesi(g, Y2) for g in yol])
    return {"t": ts, "yol": yol, "d_toplam": d_tam,
            "d_baştan": d1, "d_sona": d2,
            "doğrusallık_hatası": float(np.abs(d1 - ts * d_tam).max()),
            "üçgen_kapanma_hatası": float(np.abs(d1 + d2 - d_tam).max())}


def grassmann_ortalamasi(tabanlar: Sequence[np.ndarray], tur: int = 400,
                         adim: float = 1.0) -> Dict[str, object]:
    """Karcher ortalaması: ``Σ Log_μ(Y_i) = 0`` olana dek yinele.

    Öklit ortalaması (tabanları toplayıp dikleştirmek) Grassmann
    ortalaması **değildir** ve taban seçimine bağlıdır; fark
    ölçülüyor.

    Yakınsama **doğrusaldır**, kuadratik değil: ölçülen artık dizisi
    her adımda ~0.8 katına iniyor, 1e-13'e inmesi 307 yineleme
    alıyor.  Bu yüzden öntanımlı ``tur`` 400'dür; 60'ta artık daha
    3e-05'tir (ilk hâlde 60 yazmıştım, ölçüm yetersiz olduğunu
    gösterdi).  Kare mesafe toplamı ise 60 yinelemede bile aynı
    çıkıyor -- yani ortalamanın *değeri* erken oturuyor, *artık*
    geç iniyor.
    """
    mu = dik_taban(tabanlar[0])
    seyir = []
    for _ in range(tur):
        H = sum(log_haritasi(mu, Y) for Y in tabanlar) / len(tabanlar)
        n = float(np.linalg.norm(H))
        seyir.append(n)
        if n < 1e-13:
            break
        mu = exp_haritasi(mu, H, adim)
    kare = float(sum(grassmann_mesafesi(mu, Y) ** 2 for Y in tabanlar))
    return {"ortalama": mu, "artık_seyri": seyir, "artık": seyir[-1],
            "kare_mesafe_toplamı": kare}


# ══════════════════════════════════════════════════════════════════════
#  3. Spektral Laplasyen ve Tikhonov (K25)
# ══════════════════════════════════════════════════════════════════════

def normalize_laplasyen(A: np.ndarray) -> np.ndarray:
    """``L = I − D^{−1/2} A D^{−1/2}`` — yalıtık düğüm derecesi 0 ise ``0``."""
    A = np.asarray(A, float)
    d = A.sum(axis=1)
    inv = np.where(d > 0, 1.0 / np.sqrt(np.where(d > 0, d, 1.0)), 0.0)
    return np.eye(A.shape[0]) - (A * inv) * inv[:, None]


def betti0_tayftan(A: np.ndarray, esik: float = 1e-8) -> Dict[str, object]:
    """``β₀`` = ``L``nin sıfıra yakın özdeğer sayısı = bağlı bileşen sayısı."""
    L = normalize_laplasyen(A)
    e = np.linalg.eigvalsh(L)
    return {"özdeğerler": e, "β₀": int(np.sum(np.abs(e) < esik)),
            "en_küçük_dört": e[:4].tolist()}


def tikhonov_cekirdegi_yok_eder(A: np.ndarray, eps: float = 1e-3,
                                esik: float = 1e-8) -> Dict[str, object]:
    """``dim ker(L + εI) = 0`` — düzenleme çekirdeği **korumaz**.

    Kaynak (Darboğaz 1) hem ``L_ε = L + εI`` diyor hem de
    ``dim ker(L_ε) = β₀`` bekliyor; ikisi bir arada olamaz.  Doğrusu:
    tayf ``ε`` kadar kayar, sıfır özdeğerler ``ε``a taşınır.  ``β₀``
    o zaman "``ε``a eşit özdeğer sayısı"ndan okunur -- ama bunun için
    ``ε``ı zaten bilmek gerekir; yani düzenleme bilgi eklemez, sadece
    kaydırır.
    """
    L = normalize_laplasyen(A)
    e0 = np.linalg.eigvalsh(L)
    ee = np.linalg.eigvalsh(L + eps * np.eye(L.shape[0]))
    return {
        "β₀_düzenlemesiz": int(np.sum(np.abs(e0) < esik)),
        "çekirdek_düzenlemeli": int(np.sum(np.abs(ee) < esik)),
        "ε'a_eşit_özdeğer": int(np.sum(np.abs(ee - eps) < esik)),
        "kayma_hatası": float(np.abs(ee - (e0 + eps)).max()),
        "eps": eps,
    }


# ══════════════════════════════════════════════════════════════════════
#  Gösterim
# ══════════════════════════════════════════════════════════════════════

def _rastgele(d: int, k: int, tohum: int) -> np.ndarray:
    r = np.random.default_rng(tohum)
    return dik_taban(r.normal(size=(d, k)))


def _gosterim() -> str:
    s = []
    d, k = 8, 3
    Y1, Y2 = _rastgele(d, k, 0), _rastgele(d, k, 1)

    s.append("=== İzdüşüm kanonik: taban değişince değişmiyor ===")
    P = izdusum(Y1)
    r = np.random.default_rng(5)
    Q, _ = np.linalg.qr(r.normal(size=(k, k)))
    s.append("  ‖P−Pᵀ‖=%.2e  ‖P²−P‖=%.2e  tr P=%.10f (k=%d)"
             % (float(np.abs(P - P.T).max()),
                float(np.abs(P @ P - P).max()), float(np.trace(P)), k))
    s.append("  ‖P(Y₁) − P(Y₁Q)‖ = %.2e   ama ‖Y₁ − Y₁Q‖ = %.4f"
             % (alt_uzay_hatasi(Y1, Y1 @ Q),
                float(np.linalg.norm(Y1 - Y1 @ Q))))
    s.append("  Taban normuyla ölçmek yanlış olurdu; izdüşümle doğru.")

    s.append("\n=== K26: Log'da arctan mı arcsin mi? ===")
    s.append("  açı ölçeği   θ_max      arctan hatası   arcsin hatası")
    for olcek in (0.05, 0.2, 0.5, 0.9, 1.0):
        # Y₁'den ölçekli bir yatay yönde gidip hedefi üretelim
        r2 = np.random.default_rng(7)
        H = r2.normal(size=(d, k))
        H = H - Y1 @ (Y1.T @ H)
        H = H / np.linalg.norm(H, 2) * (olcek * math.pi / 2)
        Yt = exp_haritasi(Y1, H)
        th = asal_acilar(Y1, Yt)
        s.append("     %.2f      %.4f      %.2e        %.2e"
                 % (olcek, float(th.max()),
                    gidis_donus_hatasi(Y1, Yt, log_haritasi),
                    gidis_donus_hatasi(Y1, Yt, log_haritasi_arcsin)))
    s.append("  arcsin küçük açılarda gizleniyor (3e-04), büyük açılarda")
    s.append("  patlıyor (1.0). θ_max=π/2 satırında arctan da bozuluyor:")
    s.append("  orası KESİM LOKUSU, M = Y₁ᵀY₂ tekilleşir ve Log tek")
    s.append("  değildir. Bu Grassmann'ın kendi özelliğidir, kusur değil.")
    s.append("  Kaynaktaki 'Tr(Exp(Log)) = Tr(G₂)' ölçütü bunu YAKALAMAZ:")
    A_ = exp_haritasi(Y1, log_haritasi_arcsin(Y1, Y2))
    s.append("    yanlış Log ile bile tr P = %.10f, hedefin izi %.10f"
             % (float(np.trace(izdusum(A_))), float(np.trace(izdusum(Y2)))))
    s.append("    ama izdüşüm farkı %.4f — iz eşitliği zayıf bir ölçüttür."
             % alt_uzay_hatasi(A_, Y2))

    s.append("\n=== ‖Log‖_F = d_Gr ve geodezik doğrusallığı ===")
    for t_ in range(4):
        A1, A2 = _rastgele(10, 4, 10 + t_), _rastgele(10, 4, 20 + t_)
        g = grassmann_geodezigi(A1, A2)
        s.append("  d=%.6f  ‖Log‖_F=%.6f  doğrusallık hatası=%.2e  "
                 "üçgen kapanma=%.2e"
                 % (grassmann_mesafesi(A1, A2),
                    float(np.linalg.norm(log_haritasi(A1, A2))),
                    g["doğrusallık_hatası"], g["üçgen_kapanma_hatası"]))

    s.append("\n=== Karcher ortalaması: Öklit ortalaması DEĞİL ===")
    kume = [_rastgele(9, 3, 30 + i) for i in range(6)]
    m = grassmann_ortalamasi(kume)
    ok = dik_taban(sum(kume) / len(kume))
    kare_ok = float(sum(grassmann_mesafesi(ok, Y) ** 2 for Y in kume))
    s.append("  Karcher: artık=%.2e   Σd²=%.6f  (%d yineleme)"
             % (m["artık"], m["kare_mesafe_toplamı"], len(m["artık_seyri"])))
    m60 = grassmann_ortalamasi(kume, tur=60)
    s.append("  (60 yinelemede artık daha %.2e; yakınsama DOĞRUSAL,"
             % m60["artık"])
    s.append("   her adımda ~0.8 katı. Ama Σd² zaten aynı: %.6f)"
             % m60["kare_mesafe_toplamı"])
    s.append("  Öklit  :               Σd²=%.6f  ← daha büyük" % kare_ok)
    kume2 = [Y @ np.linalg.qr(np.random.default_rng(i).normal(size=(3, 3)))[0]
             for i, Y in enumerate(kume)]
    ok2 = dik_taban(sum(kume2) / len(kume2))
    m2 = grassmann_ortalamasi(kume2)
    s.append("  Aynı alt uzaylar, farklı tabanlarla:")
    s.append("    Karcher aynı yere gidiyor mu? ‖ΔP‖=%.2e"
             % alt_uzay_hatasi(m["ortalama"], m2["ortalama"]))
    s.append("    Öklit  aynı yere gidiyor mu? ‖ΔP‖=%.4f  ← taban bağımlı"
             % alt_uzay_hatasi(ok, ok2))

    s.append("\n=== K25: Tikhonov çekirdeği YOK EDER ===")
    # üç bileşenli çizge
    A = np.zeros((9, 9))
    for blok in ([0, 1, 2], [3, 4], [5, 6, 7, 8]):
        for i, j in [(i, j) for i in blok for j in blok if i != j]:
            A[i, j] = 1.0
    b = betti0_tayftan(A)
    s.append("  3 bileşenli çizge: β₀ = %d   en küçük dört özdeğer = %s"
             % (b["β₀"], ["%.3e" % x for x in b["en_küçük_dört"]]))
    for eps in (1e-3, 1e-6):
        t = tikhonov_cekirdegi_yok_eder(A, eps)
        s.append("  ε=%.0e: düzenlemesiz β₀=%d, ker(L+εI)=%d, "
                 "ε'a eşit özdeğer=%d, kayma hatası=%.2e"
                 % (eps, t["β₀_düzenlemesiz"], t["çekirdek_düzenlemeli"],
                    t["ε'a_eşit_özdeğer"], t["kayma_hatası"]))
    s.append("  Tayf tam ε kadar kayıyor: bilgi eklenmedi, taşındı.")
    return "\n".join(s)


if __name__ == "__main__":  # pragma: no cover
    print(_gosterim())
