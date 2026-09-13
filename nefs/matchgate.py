from __future__ import annotations

import math
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

import numpy as np

__all__ = ["MatchgateAyari", "matchgate_mi", "matchgate_kur", "pfaffyen",
           "Ortam", "flo_evrimi", "rapor"]

BRAVYI_GOSSET_ALFA = 0.468


@dataclass
class MatchgateAyari:

    mod: int = 24
    kapi: int = 64
    tolerans: float = 1e-9
    kiyas_kubiti: int = 14
    tohum: int = 0


def matchgate_mi(G, tolerans: float = 1e-9
                 ) -> Tuple[bool, np.ndarray, np.ndarray]:
    M = np.asarray(G, complex)
    if M.shape != (4, 4):
        return False, np.eye(2, dtype=complex), np.eye(2, dtype=complex)
    tol = float(tolerans)
    cift, tek = [0, 3], [1, 2]
    A = M[np.ix_(cift, cift)]
    B = M[np.ix_(tek, tek)]
    if (np.max(np.abs(M[np.ix_(cift, tek)])) > tol
            or np.max(np.abs(M[np.ix_(tek, cift)])) > tol):
        return False, A, B
    for X in (A, B):
        if np.max(np.abs(X.conj().T @ X - np.eye(2))) > 1e-8:
            return False, A, B
    if abs(complex(np.linalg.det(A)) - complex(np.linalg.det(B))) > 1e-8:
        return False, A, B
    return True, A, B


def matchgate_kur(A, B) -> np.ndarray:
    A = np.asarray(A, complex).reshape(2, 2)
    B = np.asarray(B, complex).reshape(2, 2)
    G = np.zeros((4, 4), complex)
    for i, x in enumerate((0, 3)):
        for j, y in enumerate((0, 3)):
            G[x, y] = A[i, j]
    for i, x in enumerate((1, 2)):
        for j, y in enumerate((1, 2)):
            G[x, y] = B[i, j]
    return G


def pfaffyen(A) -> float:
    M = np.array(A, float, copy=True)
    n = M.shape[0]
    assert M.shape[0] == M.shape[1], "kare olmalı"
    if n % 2:
        return 0.0
    pf = 1.0
    for k in range(0, n - 2, 2):
        kp = k + 1 + int(np.argmax(np.abs(M[k + 1:, k])))
        if kp != k + 1:
            M[[k + 1, kp], :] = M[[kp, k + 1], :]
            M[:, [k + 1, kp]] = M[:, [kp, k + 1]]
            pf = -pf
        if abs(M[k + 1, k]) < 1e-300:
            return 0.0
        pf *= M[k, k + 1]
        if k + 2 < n:
            tau = M[k, k + 2:] / M[k, k + 1]
            M[k + 2:, k + 2:] += (np.outer(tau, M[k + 2:, k + 1])
                                  - np.outer(M[k + 2:, k + 1], tau))
    return float(pf * M[n - 2, n - 1])


class Ortam:

    __slots__ = ("N", "G", "kapi", "donme_deti")

    def __init__(self, N: int = 24) -> None:
        assert int(N) >= 2, "en az iki mod"
        self.N = int(N)
        self.G = np.zeros((2 * self.N, 2 * self.N), float)
        for j in range(self.N):
            self.G[2 * j, 2 * j + 1] = 1.0
            self.G[2 * j + 1, 2 * j] = -1.0
        self.kapi = 0
        self.donme_deti = 1.0

    def dondur(self, i: int, j: int, teta: float) -> None:
        i, j = int(i) % (2 * self.N), int(j) % (2 * self.N)
        assert i != j, "aynı mod kendisiyle dönmez"
        c, s = math.cos(float(teta)), math.sin(float(teta))
        G = self.G
        ri, rj = G[i].copy(), G[j].copy()
        G[i] = c * ri - s * rj
        G[j] = s * ri + c * rj
        ci, cj = G[:, i].copy(), G[:, j].copy()
        G[:, i] = c * ci - s * cj
        G[:, j] = s * ci + c * cj
        self.kapi += 1
        self.donme_deti *= 1.0

    def antisimetri_hatasi(self) -> float:
        return float(np.max(np.abs(self.G + self.G.T)))

    def gaussluk_hatasi(self) -> float:
        return float(np.max(np.abs(self.G @ self.G + np.eye(2 * self.N))))

    def parite(self) -> float:
        return pfaffyen(self.G)

    def stabilizer_rank(self) -> int:
        return 1 if self.gaussluk_hatasi() < 1e-8 else 0


def flo_evrimi(acilar, ayar: Optional[MatchgateAyari] = None
               ) -> Dict[str, Any]:
    a = ayar or MatchgateAyari()
    t = np.asarray(acilar, float).reshape(-1)
    assert t.size >= 1, "FLO evrimi için en az bir açı lâzım"
    N = max(2, int(a.mod))
    kapi = max(1, int(a.kapi))
    r = np.random.default_rng(int(a.tohum))
    ort = Ortam(N)
    cift = r.integers(0, 2 * N, size=(kapi, 2))
    t0 = time.perf_counter()
    vurulan = 0
    for k in range(kapi):
        i, j = int(cift[k, 0]), int(cift[k, 1])
        if i == j:
            j = (j + 1) % (2 * N)
        ort.dondur(i, j, float(t[k % t.size]))
        vurulan += 1
    sure = time.perf_counter() - t0

    nk = max(4, min(int(a.kiyas_kubiti), 20))
    d = 1 << nk
    psi = (r.normal(size=d) + 1j * r.normal(size=d))
    psi /= np.linalg.norm(psi)
    T = psi.reshape((2,) * nk)
    G4 = np.eye(4, dtype=complex)
    t0 = time.perf_counter()
    for _ in range(min(kapi, 32)):
        X = T.reshape(-1, 4) @ G4.T
        T = X.reshape((2,) * nk)
    yogun = (time.perf_counter() - t0) / max(1, min(kapi, 32))

    chi = ort.stabilizer_rank()
    dal = float(2.0 ** min(BRAVYI_GOSSET_ALFA * vurulan, 1023.0))
    tutan = 0
    for k in range(min(vurulan, 64)):
        th = float(t[k % t.size])
        c, sn = math.cos(th), math.sin(th)
        G = np.zeros((4, 4), complex)
        G[0, 0] = c; G[0, 3] = -sn; G[3, 0] = sn; G[3, 3] = c
        G[1, 1] = c; G[1, 2] = -sn; G[2, 1] = sn; G[2, 2] = c
        oyle, _A, _B = matchgate_mi(G)
        tutan += int(oyle)
    denenen = max(1, min(vurulan, 64))
    return {
        "mod": N, "kapı": vurulan, "chi": chi,
        "matchgate_tutan": tutan, "matchgate_denenen": denenen,
        "matchgate_hepsi": bool(tutan == denenen),
        "kovaryans_hatası": ort.gaussluk_hatasi(),
        "antisimetri_hatası": ort.antisimetri_hatasi(),
        "parite": ort.parite(),
        "parite_korundu": bool(abs(ort.parite() - 1.0) < 1e-6),
        "kapı_sn": float(sure / max(1, vurulan)),
        "toplam_sn": float(sure),
        "bayt": int(ort.G.nbytes),
        "kıyas_kübiti": nk, "yoğun_kapı_sn": float(yogun),
        "hız": float(yogun / max(sure / max(1, vurulan), 1e-12)),
        "kübit_dallanması": dal,
        "alfa": BRAVYI_GOSSET_ALFA,
    }


def rapor(tohum: int = 0) -> str:
    r = np.random.default_rng(int(tohum))
    aci = r.normal(size=97) * 0.7
    s = ["=== MATCHGATE / FLO -- VALIANT-TERHAL DÜALİTESİ ===", "",
         "  İTİRAZ TESCİLLİ: Bravyi-Gosset, χ_stab ~ 2^(%.3f·t)"
         % BRAVYI_GOSSET_ALFA, "",
         "  kapı(t)   χ_stab   Γ²=−I hatası   parite(Pf)   kapı süresi",
         "  " + "-" * 62]
    for t in (8, 64, 256, 1024):
        o = flo_evrimi(aci, MatchgateAyari(mod=24, kapi=t, tohum=int(tohum)))
        s.append("  %6d   %6d   %11.3e   %10.6f   %.9f sn"
                 % (t, o["chi"], o["kovaryans_hatası"], o["parite"],
                    o["kapı_sn"]))
    o = flo_evrimi(aci, MatchgateAyari(mod=24, kapi=1024, tohum=int(tohum)))
    s += ["",
          "  1024 sürekli açılı kapıdan SONRA:",
          "    χ_stab                 : %d   (kübit tabanında %.3e olurdu)"
          % (o["chi"], o["kübit_dallanması"]),
          "    kovaryans %d bayt      (2^%d genlik değil)"
          % (o["bayt"], o["mod"]),
          "    parite korundu         : %s" % o["parite_korundu"], ""]
    s += ["  KAPI SÜRESİ ``N``DEN BAĞIMSIZ MI (O(1) iddiası):",
          "    N       kapı süresi        kovaryans bayt"]
    for N in (8, 24, 64, 128):
        o = flo_evrimi(aci, MatchgateAyari(mod=N, kapi=256, tohum=int(tohum)))
        s.append("    %4d    %.9f sn    %d" % (N, o["kapı_sn"], o["bayt"]))
    s += ["", "    (süre N ile artıyorsa O(1) değil O(N)'dir -- Γ'nın iki",
          "     satır ve iki sütunu dolaşılır; yoğun yolda 2^N dolaşılırdı.)"]
    mg, A, B = matchgate_mi(matchgate_kur(
        np.array([[math.cos(0.3), -math.sin(0.3)],
                  [math.sin(0.3), math.cos(0.3)]], complex),
        np.array([[math.cos(0.3), -math.sin(0.3)],
                  [math.sin(0.3), math.cos(0.3)]], complex)))
    kotu = matchgate_mi(np.eye(4, dtype=complex)[[0, 2, 1, 3]])[0]
    s += ["", "  FORM DENETİMİ:",
          "    G(A,B) matchgate mi        : %s  (doğru)" % mg,
          "    takas kapısı matchgate mi  : %s  (doğru: pariteyi bozar)"
          % kotu]
    return "\n".join(s)
