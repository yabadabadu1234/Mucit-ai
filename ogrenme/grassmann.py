
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


def dik_taban(A: np.ndarray) -> np.ndarray:
    Q, R = np.linalg.qr(np.asarray(A, float))
    return Q * np.sign(np.where(np.diag(R) == 0, 1.0, np.diag(R)))


def izdusum(U: np.ndarray) -> np.ndarray:
    U = np.asarray(U, float)
    return U @ np.linalg.solve(U.T @ U, U.T)


def asal_acilar(Y1: np.ndarray, Y2: np.ndarray) -> np.ndarray:
    Q1, Q2 = dik_taban(Y1), dik_taban(Y2)
    s = np.linalg.svd(Q1.T @ Q2, compute_uv=False)
    s = np.clip(s, -1.0, 1.0)
    th = np.arccos(s)
    kucuk = s > 1 - 1e-8
    if np.any(kucuk):
        t = np.linalg.svd(Q2 - Q1 @ (Q1.T @ Q2), compute_uv=False)
        t = np.clip(np.sort(t)[::-1], 0.0, 1.0)
        th[kucuk] = np.arcsin(t[kucuk])
    return np.sort(th)


def grassmann_mesafesi(Y1: np.ndarray, Y2: np.ndarray) -> float:
    return float(np.linalg.norm(asal_acilar(Y1, Y2)))


def alt_uzay_hatasi(Y1: np.ndarray, Y2: np.ndarray) -> float:
    return float(np.linalg.norm(izdusum(Y1) - izdusum(Y2)))


def exp_haritasi(Y: np.ndarray, H: np.ndarray, t: float = 1.0
                 ) -> np.ndarray:
    Y = dik_taban(Y)
    H = np.asarray(H, float)
    H = H - Y @ (Y.T @ H)
    U, S, Vt = np.linalg.svd(H, full_matrices=False)
    return (Y @ Vt.T * np.cos(t * S)) @ Vt + (U * np.sin(t * S)) @ Vt


def _log_cekirdegi(Y1: np.ndarray, Y2: np.ndarray
                   ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    Q1, Q2 = dik_taban(Y1), dik_taban(Y2)
    M = Q1.T @ Q2
    A = np.linalg.solve(M.T, (Q2 - Q1 @ M).T).T
    return np.linalg.svd(A, full_matrices=False)


def log_haritasi(Y1: np.ndarray, Y2: np.ndarray) -> np.ndarray:
    U, S, Vt = _log_cekirdegi(Y1, Y2)
    return (U * np.arctan(S)) @ Vt


def log_haritasi_arcsin(Y1: np.ndarray, Y2: np.ndarray) -> np.ndarray:
    U, S, Vt = _log_cekirdegi(Y1, Y2)
    return (U * np.arcsin(np.clip(S, -1.0, 1.0))) @ Vt


def gidis_donus_hatasi(Y1: np.ndarray, Y2: np.ndarray,
                       log=log_haritasi) -> float:
    return alt_uzay_hatasi(exp_haritasi(Y1, log(Y1, Y2)), Y2)


def grassmann_geodezigi(Y1: np.ndarray, Y2: np.ndarray, n: int = 21
                        ) -> Dict[str, object]:
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


def normalize_laplasyen(A: np.ndarray) -> np.ndarray:
    A = np.asarray(A, float)
    d = A.sum(axis=1)
    inv = np.where(d > 0, 1.0 / np.sqrt(np.where(d > 0, d, 1.0)), 0.0)
    return np.eye(A.shape[0]) - (A * inv) * inv[:, None]


def betti0_tayftan(A: np.ndarray, esik: float = 1e-8) -> Dict[str, object]:
    L = normalize_laplasyen(A)
    e = np.linalg.eigvalsh(L)
    return {"özdeğerler": e, "β₀": int(np.sum(np.abs(e) < esik)),
            "en_küçük_dört": e[:4].tolist()}


def tikhonov_cekirdegi_yok_eder(A: np.ndarray, eps: float = 1e-3,
                                esik: float = 1e-8) -> Dict[str, object]:
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
