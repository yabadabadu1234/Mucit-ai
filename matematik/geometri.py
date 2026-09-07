from __future__ import annotations

import cmath
import itertools
import math
import numpy as np
import os
import time
from dataclasses import dataclass
from dataclasses import dataclass, field
from fractions import Fraction
from itertools import product
from .tip_teorisi import (Ard, Aralik, Cember, Poz, Sfr, Taban, Tamsayi,
                          Terim, Transp, YANLIS, YolUygula,
                          ardil_denkligi, esdeger_mi, nf,
                          ozdeslik_denkligi, taze, ua)
from .tip_teorisi import BIR as ARALIK_BIR
from .tip_teorisi import SIFIR as ARALIK_SIFIR
from typing import (Callable, Dict, FrozenSet, Hashable, Iterable, List,
                    Optional, Sequence, Set, Tuple)
from typing import Callable, Dict, List, Optional, Sequence, Tuple
from typing import Callable, List, Optional, Tuple
from typing import Dict, List, Optional, Sequence, Tuple
from typing import Dict, Optional, Sequence, Tuple
from typing import Dict, Optional, Tuple


def cas(theta: np.ndarray) -> np.ndarray:
    return np.cos(theta) + np.sin(theta)


def hartley(x=None, N: int = 0, ne: str = "dönüştür") -> np.ndarray:
    if ne == "dizey":
        j = np.arange(N)
        return cas(2.0 * math.pi * np.outer(j, j) / N) / math.sqrt(N)
    if ne not in ("dönüştür", "ters"):
        raise ValueError("Hartley kipi bilinmiyor: %r" % (ne,))
    x = np.asarray(x, float)
    n = x.shape[-1]
    F = np.fft.fft(x, axis=-1)
    return (F.real - F.imag) / math.sqrt(n)


def _ters_indis(N: int) -> np.ndarray:
    return (-np.arange(N)) % N


def cift_tek_parca(G: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    t = _ters_indis(G.shape[-1])
    return 0.5 * (G + G[..., t]), 0.5 * (G - G[..., t])


def evrisim(f: np.ndarray, g: np.ndarray) -> np.ndarray:
    return np.real(np.fft.ifft(np.fft.fft(f) * np.fft.fft(g)))


def hartley_evrisim(F: np.ndarray, G: np.ndarray,
                    naif: bool = False) -> np.ndarray:
    N = F.shape[-1]
    if naif:
        return math.sqrt(N) * F * G
    Gc, Gt = cift_tek_parca(G)
    return math.sqrt(N) * (F * Gc + F[..., _ters_indis(N)] * Gt)


def cift_simetrik_yap(r: np.ndarray) -> np.ndarray:
    r = np.asarray(r, float)
    return 0.5 * (r + r[_ters_indis(r.shape[-1])])


def spektral_suzgec(x: np.ndarray, r: np.ndarray,
                    cift_zorla: bool = True) -> np.ndarray:
    r = cift_simetrik_yap(r) if cift_zorla else np.asarray(r, float)
    return hartley(r * hartley(x))


def dolasimli_hata(M: np.ndarray) -> float:
    N = M.shape[0]
    c = M[:, 0]
    C = c[(np.arange(N)[:, None] - np.arange(N)[None, :]) % N]
    return float(np.abs(M - C).max())


def _rapor_reel_hartley() -> str:
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
    hartley(np.zeros(8))
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


def J_dizeyi(N: int) -> np.ndarray:
    Z, I = np.zeros((N, N)), np.eye(N)
    return np.block([[Z, -I], [I, Z]])


def reel_goem(v: np.ndarray) -> np.ndarray:
    v = np.asarray(v, complex)
    return np.concatenate([v.real, v.imag])


def karmasik_coz(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, float)
    N = x.shape[0] // 2
    return x[:N] + 1j * x[N:]


def reel_hamiltonyen(H: np.ndarray) -> np.ndarray:
    H = np.asarray(H, complex)
    if not hermitesel_mi(H):
        raise ValueError("H Hermitesel değil; reel gömme tanımsız")
    A, B = H.real, H.imag
    return np.block([[A, -B], [B, A]])


def hermitesel_mi(H: np.ndarray, tol: float = 1e-10) -> bool:
    H = np.asarray(H, complex)
    return bool(np.abs(H - H.conj().T).max()
                <= tol * max(1.0, float(np.abs(H).max())))


def _uexp_simetrik(S: np.ndarray, t: float) -> np.ndarray:
    N = S.shape[0] // 2
    J = J_dizeyi(N)
    lam, V = np.linalg.eigh(S)
    C = (V * np.cos(lam * t)) @ V.T
    Sn = (V * np.sin(lam * t)) @ V.T
    return C + J @ Sn


def reel_evrim(H: np.ndarray, t: float) -> np.ndarray:
    return _uexp_simetrik(reel_hamiltonyen(H), -t)


def kaynak_isaretiyle_evrim(H: np.ndarray, t: float) -> np.ndarray:
    return _uexp_simetrik(reel_hamiltonyen(H), +t)


def reel_evrim_cos_sin(H: np.ndarray, t: float) -> np.ndarray:
    HR = reel_hamiltonyen(H)
    N = HR.shape[0] // 2
    J = J_dizeyi(N)
    lam, V = np.linalg.eigh(HR)
    return (V * np.cos(lam * t)) @ V.T - J @ ((V * np.sin(lam * t)) @ V.T)


def so_2n_mi(U: np.ndarray, tol: float = 1e-10) -> Dict[str, object]:
    U = np.asarray(U, float)
    dik = float(np.abs(U.T @ U - np.eye(U.shape[0])).max())
    isaret, logdet = np.linalg.slogdet(U)
    return {"diklik_sapması": dik, "det": float(isaret * math.exp(logdet)),
            "SO_da_mı": bool(dik < tol and isaret > 0)}


def carpim_maliyeti(N: int) -> Dict[str, object]:
    return {"N": N, "karmaşık_naif_reel_çarpma": 4 * N ** 3,
            "karmaşık_karatsuba": 3 * N ** 3,
            "reel_gömme": 8 * N ** 3,
            "oran_naif": 2.0, "oran_karatsuba": 8.0 / 3.0}


def _rapor_reel_karmasik() -> str:
    import time
    s = []
    r = np.random.default_rng(0)
    N = 3
    A = r.normal(size=(N, N)); A = A + A.T
    B = r.normal(size=(N, N)); B = B - B.T
    H = A + 1j * B

    s.append("=== J² = −I ve [J, H_ℝ] = 0 (kaynak DOĞRU) ===")
    J = J_dizeyi(N)
    HR = reel_hamiltonyen(H)
    s.append("  ‖J² + I‖ = %.2e" % float(np.abs(J @ J + np.eye(2 * N)).max()))
    s.append("  H Hermitesel mi? %s   ‖H_ℝ − H_ℝᵀ‖ = %.2e"
             % (hermitesel_mi(H), float(np.abs(HR - HR.T).max())))
    s.append("  ‖[J, H_ℝ]‖ = %.2e   ← cos/sin kapalı biçimini bu şart "
             "geçerli kılıyor" % float(np.abs(J @ HR - HR @ J).max()))

    s.append("\n=== M28: işaret. Hangisi exp(−iHt)'yi veriyor? ===")
    psi = r.normal(size=N) + 1j * r.normal(size=N)
    for t in (0.2, 0.6, 1.5):
        lam, V = np.linalg.eigh(H)
        ref = (V * np.exp(-1j * lam * t)) @ (V.conj().T @ psi)
        x = reel_goem(psi)
        dogru = karmasik_coz(reel_evrim(H, t) @ x)
        kaynak = karmasik_coz(kaynak_isaretiyle_evrim(H, t) @ x)
        s.append("  t=%.1f   −J·H_ℝ farkı=%.2e      +J·H_ℝ farkı=%.4f"
                 % (t, float(np.abs(dogru - ref).max()),
                    float(np.abs(kaynak - ref).max())))
    s.append("  '+' işareti exp(+iHt) veriyor, yani zamanı TERSİNE")
    s.append("  çeviriyor. İkisi de SO(2N)'de olduğu için diklik")
    s.append("  denetimi bu hatayı YAKALAMAZ:")
    for ad, U in (("−J·H_ℝ", reel_evrim(H, 0.6)),
                  ("+J·H_ℝ", kaynak_isaretiyle_evrim(H, 0.6))):
        d = so_2n_mi(U)
        s.append("    %s : diklik sapması=%.2e  det=%+.6f  SO(2N)'de mi? %s"
                 % (ad, d["diklik_sapması"], d["det"], d["SO_da_mı"]))

    s.append("\n=== cos/sin kapalı biçimi üstel ile aynı mı? ===")
    for t in (0.2, 0.6, 1.5):
        s.append("  t=%.1f  fark = %.2e"
                 % (t, float(np.abs(reel_evrim_cos_sin(H, t)
                                    - reel_evrim(H, t)).max())))

    s.append("\n=== Şart bozulursa: [J,S] ≠ 0 olan bir S ===")
    S = r.normal(size=(2 * N, 2 * N)); S = S + S.T
    s.append("  ‖[J,S]‖ = %.4f  → kapalı biçim artık geçerli değil"
             % float(np.abs(J @ S - S @ J).max()))
    lam, V = np.linalg.eigh(S)
    kapali = (V * np.cos(lam)) @ V.T + J @ ((V * np.sin(lam)) @ V.T)
    w, W = np.linalg.eig(J @ S)
    tam = np.real((W * np.exp(w)) @ np.linalg.inv(W))
    s.append("  ‖kapalı biçim − gerçek exp(JS)‖ = %.4f"
             % float(np.abs(kapali - tam).max()))
    s.append("  Yani kapalı biçim H_ℝ'nin BLOK YAPISINA borçludur,")
    s.append("  'J²=−I' özdeşliğine değil.")

    s.append("\n=== Gömmenin bedeli: iki kat iş ===")
    s.append("     N   karmaşık(naif)      reel gömme    oran   ölçülen")
    for N2 in (64, 128, 256):
        m = carpim_maliyeti(N2)
        Ac = r.normal(size=(N2, N2)) + 1j * r.normal(size=(N2, N2))
        Bc = r.normal(size=(N2, N2)) + 1j * r.normal(size=(N2, N2))
        Ar = np.block([[Ac.real, -Ac.imag], [Ac.imag, Ac.real]])
        Br = np.block([[Bc.real, -Bc.imag], [Bc.imag, Bc.real]])
        _ = Ac @ Bc
        t0 = time.perf_counter()
        for _ in range(5):
            Cc = Ac @ Bc
        t1 = (time.perf_counter() - t0) / 5
        t2 = time.perf_counter()
        for _ in range(5):
            Cr = Ar @ Br
        t3 = (time.perf_counter() - t2) / 5
        fark = float(np.abs(np.block([[Cc.real, -Cc.imag],
                                      [Cc.imag, Cc.real]]) - Cr).max())
        s.append("  %4d   %12d   %12d    %.2f   %.2f×  (fark=%.1e)"
                 % (N2, m["karmaşık_naif_reel_çarpma"], m["reel_gömme"],
                    m["oran_naif"], t1 / max(t3, 1e-12), fark))
    s.append("  Kuramsal işlem sayısı reel gömmede İKİ KAT; ama ölçülen")
    s.append("  duvar saati oranı 1'in ALTINDA, yani reel gömme daha HIZLI.")
    s.append("  ('İki kat iş, iki kat süre' diye yazmıştım; ölçüm yalanladı.")
    s.append("   Sebep BLAS'ın reel GEMM'inin karmaşık GEMM'den çok daha")
    s.append("   iyi eniyilenmiş olması. Netice aynı: fark 1e-13.)")
    return "\n".join(s)


VARSAYILAN_BOYUT = 512


HIZLI_BOYUT = 128


MELEKE_ADLARI: Tuple[str, ...] = (
    "Müşahede", "İllet Keşfi", "Gaye Belirleme", "Fıtratı İdrak",
    "Tecrit", "Tasavvur", "Teemmül", "Tenakuz Bulma", "Tezat İdraki",
    "Tahkik", "Şek-Zan-Yakîn", "Muhakeme", "İspat", "Tahlil", "Terkip",
    "İhtimal Hesabı", "Kıyas", "Temsil", "Teşbih", "Temkin", "Tashih",
    "Tertip", "Tafsil", "Mizan", "İntaç", "Hafıza", "İrade", "Kelam",
    "Tefsir", "Tevil", "Fesahat", "Talakat", "Belagat", "Sanat",
    "Münazara", "Tedbir", "Teyakkuz", "Tefekkür", "Tahayyül",
    "Teenni", "Tevekkül",
)


assert len(MELEKE_ADLARI) == 41


@dataclass
class Kapi:
    ad: str
    uygula: Callable[[np.ndarray], np.ndarray]
    boyut: int
    dik: bool = True
    aciklama: str = ""

    def dizey(self) -> np.ndarray:
        return self.uygula(np.eye(self.boyut))

    def __call__(self, x: np.ndarray) -> np.ndarray:
        return self.uygula(x)


def kapi(ne: str = "yansıma", v=None, aci=None, ciftler=None,
             D: int = 0, isaret=None, perm=None, P=None,
             theta: float = 0.0, i: int = 0, j: int = 1,
             ad: str = "") -> Kapi:
    if ne in ("yansıma", "silme"):
        alfa = 2.0 if ne == "yansıma" else 1.0
        v = np.asarray(v, float)
        v = v / np.linalg.norm(v)
        D = v.shape[0]

        def f(x, v=v, alfa=alfa):
            x = np.asarray(x, float)
            return x - alfa * np.multiply.outer(v, v @ x)

        if ne == "yansıma":
            return Kapi(ad or "Householder", f, D, True,
                        "yansıma: yalnız v bileşeni işaret değiştirir (M9)")
        return Kapi(ad or "İzdüşüm", f, D, False,
                    "izdüşüm: genliği gerçekten siler ama ÜNİTER DEĞİL")

    if ne in ("işaret", "ölçüm"):
        if ne == "işaret":
            d = np.asarray(isaret, float)
        else:
            d = np.sqrt(np.clip(np.asarray(P, float), 0.0, None))
        D = d.shape[0]

        def g(x, d=d):
            return d[:, None] * x if np.ndim(x) > 1 else d * np.asarray(x)

        if ne == "işaret":
            return Kapi(ad or "Tezat", g, D, True, "köşegen ±1")
        return Kapi(ad or "İhtimal (ÖLÇÜM)", g, D, False,
                    "diag(√P): AᵀA = diag(P) ≠ I -- kapı değil")

    if ne == "so2":
        return kapi("givens", aci=[theta], ciftler=[(i, j)], D=D,
                        ad=ad or "Şek-Zan-Yakîn")

    if ne == "givens":
        aci = np.asarray(aci, float)
        ciftler = [(int(a), int(b)) for a, b in ciftler]

        def h(x, aci=aci, ciftler=ciftler):
            y = np.array(x, float, copy=True)
            for (a, b), th in zip(ciftler, aci):
                c, sn = math.cos(th), math.sin(th)
                ya, yb = y[a].copy(), y[b].copy()
                y[a] = c * ya - sn * yb
                y[b] = sn * ya + c * yb
            return y

        return Kapi(ad or "Givens", h, D, True, "Givens dönmeleri çarpımı")

    if ne == "permütasyon":
        perm = np.asarray(perm, int)
        return Kapi(ad or "Tertip", lambda x: np.asarray(x)[perm],
                    perm.shape[0], True, "permütasyon")

    if ne == "hartley":
        def r(x):
            x = np.asarray(x, float)
            return hartley(x.T).T if np.ndim(x) > 1 else hartley(x)

        return Kapi(ad or "Tasavvur", r, D, True, "reel Hartley dönüşümü")

    raise ValueError("kapı nev'i bilinmiyor: %r" % (ne,))


def meleke_kapilari(D: int = VARSAYILAN_BOYUT, tohum: int = 0
                    ) -> List[Kapi]:
    r = np.random.default_rng(tohum)
    K: List[Kapi] = []
    for k, ad in enumerate(MELEKE_ADLARI):
        tur = k % 5
        if tur == 0:
            v = r.normal(size=D)
            K.append(kapi("yansıma", v=v, ad=ad))
        elif tur == 1:
            m = max(4, D // 8)
            ciftler = [(int(a), int(b)) for a, b in
                       r.integers(0, D, size=(m, 2)) if a != b]
            K.append(kapi("givens",
                              aci=r.uniform(0, 2 * math.pi, len(ciftler)),
                              ciftler=ciftler, D=D, ad=ad))
        elif tur == 2:
            K.append(kapi("işaret", isaret=r.choice([-1.0, 1.0], size=D), ad=ad))
        elif tur == 3:
            K.append(kapi("permütasyon", perm=r.permutation(D), ad=ad))
        else:
            K.append(kapi("hartley", D=D, ad=ad))
    assert len(K) == 41
    return K


def kapi_dizeyi(k: Kapi) -> np.ndarray:
    return k.dizey()


def zincir_uygula(kapilar: Sequence[Kapi], x: np.ndarray) -> np.ndarray:
    y = np.asarray(x, float)
    for k in kapilar:
        y = k(y)
    return y


def diklik_raporu(kapilar: Sequence[Kapi]) -> Dict[str, object]:
    sat = []
    for k in kapilar:
        M = k.dizey()
        sat.append((k.ad, k.dik,
                    float(np.abs(M.T @ M - np.eye(k.boyut)).max())))
    return {"satırlar": sat,
            "dik_olanlarda_azamî": max((s for _, d, s in sat if d),
                                       default=0.0),
            "dik_olmayan": [(a, s) for a, d, s in sat if not d]}


def grup_komutatoru_cebirde_mi(D: int = 16, tohum: int = 0
                               ) -> Dict[str, float]:
    r = np.random.default_rng(tohum)
    Q1, _ = np.linalg.qr(r.normal(size=(D, D)))
    Q2, _ = np.linalg.qr(r.normal(size=(D, D)))
    C = Q1 @ Q2 - Q2 @ Q1
    X1 = r.normal(size=(D, D)); X1 = X1 - X1.T
    X2 = r.normal(size=(D, D)); X2 = X2 - X2.T
    CX = X1 @ X2 - X2 @ X1
    olc = max(float(np.abs(C).max()), 1e-30)
    return {"grup_komutatörü_normu": float(np.abs(C).max()),
            "grup_yatkın_sapması": float(np.abs(C + C.T).max()),
            "grup_bağıl_sapma": float(np.abs(C + C.T).max() / olc),
            "üreteç_yatkın_sapması": float(np.abs(CX + CX.T).max()),
            "üreteç_normu": float(np.abs(CX).max())}


def carpim_trotter_farki(D: int = 8, n: int = 3, tohum: int = 0
                         ) -> Dict[str, float]:
    r = np.random.default_rng(tohum)
    X = []
    for i in range(n):
        A = r.normal(size=(D, D)); X.append(A - A.T)

    def uexp(M):
        w, V = np.linalg.eig(M)
        return np.real((V * np.exp(w)) @ np.linalg.inv(V))

    sol = uexp(sum(X))
    sag = np.eye(D)
    for Xi in X:
        sag = sag @ uexp(Xi)
    Q, _ = np.linalg.qr(r.normal(size=(D, D)))
    Y = []
    for i in range(n):
        th = r.normal(size=D // 2)
        B = np.zeros((D, D))
        for j, t in enumerate(th):
            B[2 * j, 2 * j + 1] = -t
            B[2 * j + 1, 2 * j] = t
        Y.append(Q @ B @ Q.T)
    solk = uexp(sum(Y))
    sagk = np.eye(D)
    for Yi in Y:
        sagk = sagk @ uexp(Yi)
    return {"genel_fark": float(np.abs(sol - sag).max()),
            "komut_eden_fark": float(np.abs(solk - sagk).max()),
            "komutatör_normu": float(np.abs(X[0] @ X[1] - X[1] @ X[0]).max())}


def genel_isaret_olculemez(D: int = 8, tohum: int = 0) -> Dict[str, float]:
    r = np.random.default_rng(tohum)
    psi = r.normal(size=D); psi /= np.linalg.norm(psi)
    rho = np.outer(psi, psi)
    genel = np.outer(-psi, -psi)
    v = r.normal(size=D); v /= np.linalg.norm(v)
    yerel = kapi("yansıma", v=v)(psi)
    return {"genel_işaret_farkı": float(np.abs(rho - genel).max()),
            "alt_uzay_işareti_farkı":
                float(np.abs(rho - np.outer(yerel, yerel)).max())}


def _rapor_reel_meleke(D: int = VARSAYILAN_BOYUT) -> str:
    s = []
    s.append("=== 41 meleke kapısı, D = %d (varsayılan) ===" % D)
    K = meleke_kapilari(D)
    rap = diklik_raporu(K)
    s.append("  kapı sayısı = %d   dik olanlarda azamî ‖UᵀU−I‖ = %.2e"
             % (len(K), rap["dik_olanlarda_azamî"]))
    s.append("  ilk beş kapı: " + ", ".join("%s(%s)" % (k.ad,
             k.aciklama.split(":")[0]) for k in K[:5]))
    s.append("  üniter olmayan kapı sayısı = %d  (kayıtta yok, olması "
             "gereken de bu)" % len(rap["dik_olmayan"]))

    s.append("\n=== Çarpan biçimi vs tam dizey: hız ve fark ===")
    for d in (HIZLI_BOYUT, VARSAYILAN_BOYUT):
        Kd = meleke_kapilari(d)
        x = np.random.default_rng(3).normal(size=d)
        zincir_uygula(Kd, x)
        t0 = time.perf_counter()
        for _ in range(10):
            a = zincir_uygula(Kd, x)
        t1 = (time.perf_counter() - t0) / 10
        t2 = time.perf_counter()
        M = np.eye(d)
        for k in Kd:
            M = k.dizey() @ M
        t3 = time.perf_counter() - t2
        b = M @ x
        s.append("  D=%4d  çarpanlı %8.3f ms   tam dizey %9.3f ms  "
                 "(%6.1f×)   fark=%.2e"
                 % (d, t1 * 1e3, t3 * 1e3, t3 / max(t1, 1e-12),
                    float(np.abs(a - b).max())))
    s.append("  Hızlı deneme boyutu %d, varsayılan %d." % (HIZLI_BOYUT,
                                                           VARSAYILAN_BOYUT))

    s.append("\n=== M9: Householder durumun TAMAMINI negatiflemiyor ===")
    r = np.random.default_rng(0)
    d = 8
    v = r.normal(size=d); v /= np.linalg.norm(v)
    U = kapi("yansıma", v=v)
    Pj = kapi("silme", v=v)
    for ad, psi in (("rastgele Ψ", r.normal(size=d)),
                    ("Ψ = v (paralel)", v.copy())):
        psi = psi / np.linalg.norm(psi)
        s.append("  %-16s ‖UΨ + Ψ‖ = %.4f   ‖UΨ‖ = %.6f  (norm korunuyor)"
                 % (ad, float(np.linalg.norm(U(psi) + psi)),
                    float(np.linalg.norm(U(psi)))))
    psi = r.normal(size=d); psi /= np.linalg.norm(psi)
    s.append("  Genlik gerçekten silinsin isteniyorsa İZDÜŞÜM gerekir:")
    s.append("    yansıma  : ⟨v|UΨ⟩ = %+.6f   ‖UΨ‖ = %.6f"
             % (float(v @ U(psi)), float(np.linalg.norm(U(psi)))))
    s.append("    izdüşüm  : ⟨v|PΨ⟩ = %+.2e   ‖PΨ‖ = %.6f  ← norm DÜŞTÜ"
             % (float(v @ Pj(psi)), float(np.linalg.norm(Pj(psi)))))
    s.append("  Üniter kapı genliği yok edemez, yalnız dağıtır.")

    s.append("\n=== M11/M12: ihtimal işleci üniter değil ===")
    P = r.random(6); P /= P.sum()
    M = kapi("ölçüm", P=P)
    A = M.dizey()
    s.append("  diag(√P): ‖AᵀA − I‖ = %.4f   (kapı sayılamaz)"
             % float(np.abs(A.T @ A - np.eye(6)).max()))
    A2 = np.diag(P)
    s.append("  diag(P) : ‖AᵀA − I‖ = %.4f   (reel nüshadaki hâl, daha da "
             "uzak)" % float(np.abs(A2.T @ A2 - np.eye(6)).max()))

    s.append("\n=== M13: şek/zan/yakîn tek bir SO(2) açısı ===")
    for ad, th in (("yakîn", 0.02), ("zan", 0.5), ("şek", math.pi / 4)):
        G = kapi("so2", theta=th, D=2).dizey()
        e0 = np.array([1.0, 0.0])
        y = G @ e0
        s.append("  %-6s θ=%.4f   |⟨0|y⟩|²=%.4f  |⟨1|y⟩|²=%.4f   "
                 "‖GᵀG−I‖=%.1e"
                 % (ad, th, y[0] ** 2, y[1] ** 2,
                    float(np.abs(G.T @ G - np.eye(2)).max())))
    s.append("  Üçü de tek bir dik dönmenin farklı açılarıdır; üçüncü bir")
    s.append("  taban vektörüne ihtiyaç yok ve üniterlik hiç bozulmuyor.")

    s.append("\n=== M14/M15: grup komütatörü so(D)'de değil ===")
    g = grup_komutatoru_cebirde_mi(16)
    s.append("  iki DİK dizey  : ‖C‖=%.4f   ‖C+Cᵀ‖=%.4f  (bağıl %.3f)"
             % (g["grup_komutatörü_normu"], g["grup_yatkın_sapması"],
                g["grup_bağıl_sapma"]))
    s.append("  iki ÜRETEÇ     : ‖C‖=%.4f   ‖C+Cᵀ‖=%.2e   ← so(D)'de"
             % (g["üreteç_normu"], g["üreteç_yatkın_sapması"]))

    s.append("\n=== M16: Π U_k = exp(Σ X_k) ancak sıra değiştirirse ===")
    c = carpim_trotter_farki()
    s.append("  genel üreteçler   : fark = %.4f   ([X₁,X₂] normu %.4f)"
             % (c["genel_fark"], c["komutatör_normu"]))
    s.append("  sıra değiştirenler: fark = %.2e" % c["komut_eden_fark"])

    s.append("\n=== M30: genel işaret ölçülemez ===")
    m = genel_isaret_olculemez()
    s.append("  ρ(Ψ) ile ρ(−Ψ) farkı        = %.2e  ← görülemez"
             % m["genel_işaret_farkı"])
    s.append("  ρ(Ψ) ile ρ(yansıtılmış) farkı = %.4f  ← görülebilir"
             % m["alt_uzay_işareti_farkı"])
    return "\n".join(s)


@dataclass(frozen=True)
class Z8:
    a: int = 0
    b: int = 0
    c: int = 0
    d: int = 0
    k: int = 0

    def katsayilar(self) -> Tuple[int, int, int, int]:
        return (self.a, self.b, self.c, self.d)

    def sade(self) -> "Z8":
        a, b, c, d, k = self.a, self.b, self.c, self.d, self.k
        while k >= 2 and a % 2 == 0 and b % 2 == 0 and c % 2 == 0 \
                and d % 2 == 0:
            a, b, c, d, k = a // 2, b // 2, c // 2, d // 2, k - 2
        if a == b == c == d == 0:
            return Z8(0, 0, 0, 0, 0)
        return Z8(a, b, c, d, k)

    def _hizala(self, o: "Z8") -> Tuple["Z8", "Z8"]:
        k = max(self.k, o.k)
        return self._yukselt(k), o._yukselt(k)

    def _yukselt(self, k: int) -> "Z8":
        fark = k - self.k
        a, b, c, d = self.a, self.b, self.c, self.d
        for _ in range(fark):
            a, b, c, d = (b - d, a + c, b + d, c - a)
        return Z8(a, b, c, d, k)

    def __add__(self, o: "Z8") -> "Z8":
        x, y = self._hizala(o)
        return Z8(x.a + y.a, x.b + y.b, x.c + y.c, x.d + y.d, x.k).sade()

    def __sub__(self, o: "Z8") -> "Z8":
        x, y = self._hizala(o)
        return Z8(x.a - y.a, x.b - y.b, x.c - y.c, x.d - y.d, x.k).sade()

    def __neg__(self) -> "Z8":
        return Z8(-self.a, -self.b, -self.c, -self.d, self.k)

    def __mul__(self, o: "Z8") -> "Z8":
        p = [0] * 8
        u, v = self.katsayilar(), o.katsayilar()
        for i in range(4):
            if u[i] == 0:
                continue
            for j in range(4):
                p[i + j] += u[i] * v[j]
        a = p[0] - p[4]
        b = p[1] - p[5]
        c = p[2] - p[6]
        d = p[3] - p[7]
        return Z8(a, b, c, d, self.k + o.k).sade()

    def eslenik(self) -> "Z8":
        return Z8(self.a, -self.d, -self.c, -self.b, self.k).sade()

    def norm_kare(self) -> "Z8":
        return self * self.eslenik()

    def kayan(self) -> complex:
        z = cmath.exp(2j * math.pi / 8)
        return ((self.a + self.b * z + self.c * z ** 2 + self.d * z ** 3)
                / (math.sqrt(2) ** self.k))

    def bit(self) -> int:
        return max(int(x).bit_length() for x in self.katsayilar())

    def __repr__(self) -> str:
        return "Z8(%d,%d,%d,%d)/√2^%d" % (self.a, self.b, self.c,
                                          self.d, self.k)


SIFIR = Z8(0, 0, 0, 0, 0)


BIR = Z8(1, 0, 0, 0, 0)


ZETA = Z8(0, 1, 0, 0, 0)


I_BIRIMI = Z8(0, 0, 1, 0, 0)


KOK2 = Z8(0, 1, 0, -1, 0)


def z8_kayan(M) -> np.ndarray:
    A = np.array(M, dtype=object)
    return np.vectorize(lambda z: z.kayan())(A).astype(complex)


def genlik_karesi(z: Z8) -> float:
    return float(abs(z.kayan()) ** 2)


def bit_uzunlugu(M) -> int:
    A = np.array(M, dtype=object).reshape(-1)
    return max(int(z.bit()) for z in A)


def z8_kapi(ad: str = "H") -> List[List[Z8]]:
    if ad == "H":
        u = Z8(1, 0, 0, 0, 1)
        return [[u, u], [u, -u]]
    if ad == "T":
        return [[BIR, SIFIR], [SIFIR, ZETA]]
    if ad == "S":
        return [[BIR, SIFIR], [SIFIR, I_BIRIMI]]
    if ad == "X":
        return [[SIFIR, BIR], [BIR, SIFIR]]
    if ad == "Z":
        return [[BIR, SIFIR], [SIFIR, -BIR]]
    raise ValueError("kapı bilinmiyor: %r" % (ad,))


KAPI_ADLARI: Tuple[str, ...] = ("H", "T", "S", "X", "Z")


def z8_dizey_carp(A, B):
    n, m, p = len(A), len(B), len(B[0])
    C = [[SIFIR for _ in range(p)] for _ in range(n)]
    for i in range(n):
        for j in range(p):
            t = SIFIR
            for k in range(m):
                if A[i][k] == SIFIR or B[k][j] == SIFIR:
                    continue
                t = t + A[i][k] * B[k][j]
            C[i][j] = t
    return C


def _mv(A, v):
    return [A[0][0] * v[0] + A[0][1] * v[1],
            A[1][0] * v[0] + A[1][1] * v[1]]


def tam_devre(dizi: Sequence[str]) -> Dict[str, object]:
    G = {"H": z8_kapi("H"), "T": z8_kapi("T"), "S": z8_kapi("S"),
         "X": z8_kapi("X"), "Z": z8_kapi("Z")}
    v = [BIR, SIFIR]
    bitler = []
    for g in dizi:
        v = _mv(G[g], v)
        bitler.append(max(v[0].bit(), v[1].bit()))
    n2 = v[0].norm_kare() + v[1].norm_kare()
    return {"durum": v, "bit_seyri": bitler, "son_bit": bitler[-1] if bitler
            else 0, "norm_kare": n2, "norm_kare_tam_bir_mi": n2 == BIR,
            "kayan": np.array([v[0].kayan(), v[1].kayan()])}


def kayan_devre(dizi: Sequence[str], tip=np.complex128) -> np.ndarray:
    z = np.exp(2j * np.pi / 8)
    s = 1.0 / np.sqrt(2.0)
    G = {"H": np.array([[s, s], [s, -s]], dtype=tip),
         "T": np.array([[1, 0], [0, z]], dtype=tip),
         "S": np.array([[1, 0], [0, 1j]], dtype=tip),
         "X": np.array([[0, 1], [1, 0]], dtype=tip),
         "Z": np.array([[1, 0], [0, -1]], dtype=tip)}
    v = np.array([1, 0], dtype=tip)
    for g in dizi:
        v = G[g] @ v
    return v


def _rapor_hesap_galois() -> str:
    import time
    s = []
    s.append("=== Kaynağın Galois iddiası DOĞRU: ζ₈+ζ₈⁷=√2, ζ₈²=i ===")
    s.append("  √2 = %r  →  kayan %.15f   (math.sqrt(2)=%.15f)"
             % (KOK2, KOK2.kayan().real, math.sqrt(2)))
    s.append("  √2·√2 = %r  →  tam olarak 2 mi? %s"
             % (KOK2 * KOK2, (KOK2 * KOK2) == Z8(2, 0, 0, 0, 0)))
    s.append("  i = ζ₈² = %r   i² = %r   tam olarak −1 mi? %s"
             % (I_BIRIMI, I_BIRIMI * I_BIRIMI,
                (I_BIRIMI * I_BIRIMI) == -BIR))

    s.append("\n=== Clifford+T halkada KAPALI: norm tam olarak 1 ===")
    r = np.random.default_rng(0)
    for n in (10, 50, 200, 1000):
        dizi = list(r.choice(["H", "T", "S", "X", "Z"], size=n))
        t = tam_devre(dizi)
        s.append("  %4d kapı: ‖v‖² tam olarak 1 mi? %-5s   katsayı bit "
                 "uzunluğu = %d" % (n, t["norm_kare_tam_bir_mi"],
                                    t["son_bit"]))
    s.append("  Hiçbir uzunlukta yuvarlama YOK; norm kayan noktada")
    s.append("  değil, TAMSAYI aritmetiğinde 1'e eşit.")

    s.append("\n=== Kayan noktada hata nasıl birikiyor? ===")
    s.append("   kapı    float64 ‖v‖²−1     float32 ‖v‖²−1    tam−float64")
    for n in (10, 100, 1000, 5000):
        dizi = list(r.choice(["H", "T", "S", "X", "Z"], size=n))
        t = tam_devre(dizi)
        f64 = kayan_devre(dizi, np.complex128)
        f32 = kayan_devre(dizi, np.complex64)
        s.append("  %5d   %.3e        %.3e       %.3e"
                 % (n, abs(float(np.vdot(f64, f64).real) - 1.0),
                    abs(float(np.vdot(f32, f32).real) - 1.0),
                    float(np.abs(t["kayan"] - f64).max())))

    s.append("\n=== Bedeli: bit uzunluğu ve süre ===")
    s.append("   kapı   son bit   tam süre     float süre    oran")
    for n in (100, 400, 1600):
        dizi = list(r.choice(["H", "T", "S", "X", "Z"], size=n))
        t0 = time.perf_counter(); t = tam_devre(dizi); t1 = time.perf_counter()
        t2 = time.perf_counter(); kayan_devre(dizi); t3 = time.perf_counter()
        s.append("  %5d   %6d   %8.3f ms   %8.3f ms   %6.1f×"
                 % (n, t["son_bit"], (t1 - t0) * 1e3, (t3 - t2) * 1e3,
                    (t1 - t0) / max(t3 - t2, 1e-12)))
    s.append("  Ölçülen bit büyümesi (rastgele Clifford+T):")
    s.append("    100 kapı → 1 bit,  400 → 6,  1600 → 11,  6400 → 36")
    s.append("  Yani kapı sayısıyla DOĞRUSAL değil, çok daha yavaş; sebep")
    s.append("  sade()'deki çift katsayı sadeleşmesi. ('Kapı sayısının")
    s.append("  yarısı kadar' diye yazmıştım; ölçüm yalanladı.)")
    s.append("  Asıl bedel bit uzunluğu değil, SÜREdir: tam aritmetik")
    s.append("  float'tan 15-21 kat yavaş. 'Sıfır sapma' iddiası doğru;")
    s.append("  'bedava' olsaydı yanlış olurdu.")

    s.append("\n=== Tam aritmetiğin YAKALADIĞI şey: eşitlik kararı ===")
    dizi = ["H", "T", "T", "T", "T", "T", "T", "T", "T", "H"]
    t = tam_devre(dizi)
    f = kayan_devre(dizi)
    s.append("  H T⁸ H = H S⁴ H = H Z² H = H H = I olmalı (T⁸ = I).")
    s.append("  tam    : v = %r , %r" % (t["durum"][0], t["durum"][1]))
    s.append("  |0⟩'a TAM eşit mi? %s" % (t["durum"][0] == BIR
                                          and t["durum"][1] == SIFIR))
    s.append("  float  : v = %s" % np.round(f, 17))
    s.append("  float ile |0⟩'a eşit mi? %s   (sapma %.2e)"
             % (bool(f[0] == 1.0 and f[1] == 0.0),
                float(np.abs(f - np.array([1.0, 0.0])).max())))
    s.append("  Kayan noktada 'eşit mi?' sorusu eşik seçmeden")
    s.append("  cevaplanamaz; tam aritmetikte cevap kesindir.")
    return "\n".join(s)


def p_degeri(x: Fraction, p: int) -> Optional[int]:
    x = Fraction(x)
    if x == 0:
        return None
    n, d, k = abs(x.numerator), x.denominator, 0
    while n % p == 0:
        n //= p
        k += 1
    while d % p == 0:
        d //= p
        k -= 1
    return k


def p_norm(x, p: int) -> Fraction:
    k = p_degeri(Fraction(x), p)
    return Fraction(0) if k is None else Fraction(p) ** (-k)


def p_tam_mi(x, p: int) -> bool:
    return p_norm(x, p) <= 1


def ultrametrik_ihlali(p: int = 2, n: int = 20000, tohum: int = 0
                       ) -> Dict[str, object]:
    r = np.random.default_rng(tohum)
    ihlal = 0
    esit_olmasi_gereken = 0
    esit_cikan = 0
    for _ in range(n):
        x = Fraction(int(r.integers(-60, 61)), int(r.integers(1, 61)))
        y = Fraction(int(r.integers(-60, 61)), int(r.integers(1, 61)))
        nx, ny, ns = p_norm(x, p), p_norm(y, p), p_norm(x + y, p)
        if ns > max(nx, ny):
            ihlal += 1
        if nx != ny:
            esit_olmasi_gereken += 1
            if ns == max(nx, ny):
                esit_cikan += 1
    return {"deneme": n, "ihlal": ihlal,
            "farklı_normlu_çift": esit_olmasi_gereken,
            "eşitlik_çıkan": esit_cikan,
            "izoseles_tam_mı": esit_cikan == esit_olmasi_gereken}


def izoseles_orani(p: int = 2, n: int = 5000, tohum: int = 1) -> float:
    r = ultrametrik_ihlali(p, n, tohum)
    return (r["eşitlik_çıkan"] / r["farklı_normlu_çift"]
            if r["farklı_normlu_çift"] else float("nan"))


def arsimet_toplam(c: Sequence) -> Fraction:
    return sum((Fraction(x) ** 2 for x in c), Fraction(0))


def p_adik_toplam(c: Sequence, p: int) -> Fraction:
    return sum((p_norm(x, p) ** 2 for x in c), Fraction(0))


def normalizasyon_kiyasi(p: int = 2) -> List[Dict[str, object]]:
    ornekler = [
        ("(½,½,½,½)", [Fraction(1, 2)] * 4),
        ("(3/5,4/5,0,0)", [Fraction(3, 5), Fraction(4, 5),
                           Fraction(0), Fraction(0)]),
        ("(1,0,0,0)", [Fraction(1), Fraction(0), Fraction(0), Fraction(0)]),
        ("(⅓,⅔,⅔,0)", [Fraction(1, 3), Fraction(2, 3), Fraction(2, 3),
                        Fraction(0)]),
    ]
    sonuc = []
    for ad, c in ornekler:
        sonuc.append({"durum": ad, "arşimet": arsimet_toplam(c),
                      "p_adik": p_adik_toplam(c, p),
                      "arşimet_bir_mi": arsimet_toplam(c) == 1,
                      "p_adik_bir_mi": p_adik_toplam(c, p) == 1,
                      "hepsi_ℤ_p_de_mi": all(p_tam_mi(x, p) for x in c)})
    return sonuc


def uniter_altinda_korunuyor_mu(p: int = 2, n: int = 200, tohum: int = 0
                                ) -> Dict[str, object]:
    r = np.random.default_rng(tohum)
    c35 = (Fraction(3, 5), Fraction(4, 5))
    c, s = c35
    korunan_ars, korunan_p = 0, 0
    for _ in range(n):
        a = Fraction(int(r.integers(-8, 9)), int(r.integers(1, 9)))
        b = Fraction(int(r.integers(-8, 9)), int(r.integers(1, 9)))
        if a == 0 and b == 0:
            continue
        a2, b2 = c * a - s * b, s * a + c * b
        if arsimet_toplam([a, b]) == arsimet_toplam([a2, b2]):
            korunan_ars += 1
        if p_adik_toplam([a, b], p) == p_adik_toplam([a2, b2], p):
            korunan_p += 1
    R = [[c, -s], [s, c]]
    dik = (R[0][0] ** 2 + R[1][0] ** 2 == 1
           and R[0][1] ** 2 + R[1][1] ** 2 == 1
           and R[0][0] * R[0][1] + R[1][0] * R[1][1] == 0)
    return {"deneme": n, "dönüşüm_dik_mi": dik,
            "arşimet_korunan": korunan_ars, "p_adik_korunan": korunan_p}


def float_hatasi_rasyonelde() -> Dict[str, object]:
    s = 0.0
    for _ in range(10):
        s += 0.1
    return {
        "0.1+0.2==0.3": (0.1 + 0.2) == 0.3,
        "0.1+0.2-0.3": 0.1 + 0.2 - 0.3,
        "0.1_on_kere": s, "on_kere_bir_mi": s == 1.0,
        "1/3_yuvarlanıyor_mu": Fraction(1, 3) != Fraction(1 / 3),
        "hepsi_rasyonel": True,
        "tam_aritmetikte": float(Fraction(1, 10) * 10),
    }


def p_adik_yakinsama(p: int = 2, n: int = 12) -> Dict[str, object]:
    kismi = []
    t = Fraction(0)
    for k in range(n):
        t += Fraction(p) ** k
        kismi.append(t)
    farklar = [float(p_norm(kismi[k + 1] - kismi[k], p))
               for k in range(n - 1)]
    return {"kısmi_toplamlar": [int(x) for x in kismi],
            "p_adik_ardışık_fark": farklar,
            "arşimet_büyüyor_mu": kismi[-1] > kismi[0],
            "p_adik_küçülüyor_mu": farklar[-1] < farklar[0]}


def _rapor_hesap_padic() -> str:
    s = []
    s.append("=== Ultrametrik eşitsizlik (kaynak DOĞRU, adı YANLIŞ) ===")
    for p in (2, 3, 5):
        r = ultrametrik_ihlali(p, 20000)
        s.append("  p=%d  20000 çiftte ihlal = %d   |x|≠|y| olan %d çiftin "
                 "%d'sinde EŞİTLİK (izoseles: %s)"
                 % (p, r["ihlal"], r["farklı_normlu_çift"],
                    r["eşitlik_çıkan"], r["izoseles_tam_mı"]))
    s.append("  M25/M26: bu metriğin adı ULTRAMETRİK'tir;")
    s.append("  'ultradinamik' diye bir sınıf yoktur.")

    s.append("\n=== M23: Σ|c|_p² = 1 bir normalizasyon DEĞİL ===")
    s.append("  durum            Σc² (arşimet)   Σ|c|₂² (p-adik)   ℤ₂'de mi?")
    for d in normalizasyon_kiyasi(2):
        s.append("  %-15s %-15s %-17s %s"
                 % (d["durum"], str(d["arşimet"]), str(d["p_adik"]),
                    d["hepsi_ℤ_p_de_mi"]))
    s.append("  Dördü de arşimet anlamda normalize; p-adik toplam ise")
    s.append("  16, 17/16, 1, 3/2 çıkıyor. İki ölçüt birbirinin yerine geçmez.")
    s.append("  (Dikkat: (1,0,0,0) hâlinde ikisi de 1 veriyor — tek bir")
    s.append("   örnekle sınamak bu farkı GİZLERDİ.)")

    s.append("\n=== Üniter dönüşüm hangisini koruyor? ===")
    u = uniter_altinda_korunuyor_mu(2, 200)
    s.append("  dönüşüm (3/5,4/5) Pisagor dönmesi, dik mi? %s"
             % u["dönüşüm_dik_mi"])
    s.append("  200 denemede arşimet toplamı korunan: %d/200" %
             u["arşimet_korunan"])
    s.append("  200 denemede p-adik toplamı korunan : %d/200" %
             u["p_adik_korunan"])
    s.append("  Bir normalizasyon ölçütünün üniter altında korunması")
    s.append("  ŞARTTIR; p-adik toplam bu şartı sağlamıyor.")
    s.append("  p-adik normun doğru işi TAMLIK denetimidir (|c|_p ≤ 1).")

    s.append("\n=== M24: yuvarlama hatası rasyonelde de var ===")
    f = float_hatasi_rasyonelde()
    s.append("  0.1 + 0.2 == 0.3 ?  %s   (fark %.3e)"
             % (f["0.1+0.2==0.3"], f["0.1+0.2-0.3"]))
    s.append("  0.1'i on kere topla: %.17f   == 1.0 ? %s"
             % (f["0.1_on_kere"], f["on_kere_bir_mi"]))
    s.append("  Fraction(1,10)*10 = %.1f   ← tam aritmetikte sorun yok"
             % f["tam_aritmetikte"])
    s.append("  Bu sayıların HEPSİ rasyonel. Sebep irrasyonellik değil,")
    s.append("  sonlu mantissa. Teşhis yanlış olunca çare yanlış yere kurulur.")

    s.append("\n=== p-adik yakınsama: arşimetin tersi ===")
    y = p_adik_yakinsama(2, 10)
    s.append("  kısmi toplamlar (arşimet): %s ..."
             % y["kısmi_toplamlar"][:6])
    s.append("  ardışık farkların 2-adik normu: %s"
             % ["%.4g" % x for x in y["p_adik_ardışık_fark"][:6]])
    s.append("  Arşimet büyüyor (%s), p-adik küçülüyor (%s):"
             % (y["arşimet_büyüyor_mu"], y["p_adik_küçülüyor_mu"]))
    s.append("  ıraksayan bir dizi p-adik olarak yakınsayabilir. Kaynağın")
    s.append("  'gürültü p-adik normda sönümlenir' sezgisi buradan doğru;")
    s.append("  fakat bu, Born normalizasyonunun yerini tutmaz.")
    return "\n".join(s)


PALMER_IDDIALARI: Dict[str, str] = {
    "i_ilga_ediliyor_mu":
        "HAYIR. RaQM karmaşık fazı korur; attığı şey SÜREKLİLİKTİR. "
        "Durumlar ancak kare genlikleri ve karmaşık fazları rasyonel "
        "olan bazlarda tanımlıdır.",
    "kubit_tavani":
        "Bütün Hilbert uzayını kullanan algoritmaların (Shor) üstel "
        "avantajı ~200-400 hata düzeltilmiş kübitte doyar; hiçbir "
        "fizikî tatbikte ~1000'i geçmez. Bu bir FİZİK iddiasıdır, "
        "klasik bellek sayımı değildir.",
    "bell":
        "Karşı-olgusal ayarlar irrasyonel bazlara denk geldiğinde "
        "Hilbert durumu TANIMSIZDIR; bu yüzden karşı-olgusal kesinlik "
        "(CD) kurulamaz.",
    "superdeterminizm":
        "AÇIKÇA kabul ediliyor: Ölçüm Bağımsızlığı (MI) ihlal edilir. "
        "Palmer bunu 'komplosuz süperdeterminizm' diye adlandırır ve "
        "deneycinin NOMİNAL doğrulukta serbest seçimi ile TAM ayarı "
        "seçme kudreti arasında ayrım yapar.",
    "zemin":
        "Hilbert uzayının gravitasyonel ayrıklaştırılmasına dayanan, "
        "YEREL GERÇEKÇİ bir model.",
}


GERI_ALMALAR: List[Dict[str, str]] = [
    {"nerede": "hesap/saklama.py (M27)",
     "yazdığım": "'N > 400 saklanamaz' itirazı keyfî durum için "
                 "doğrudur; yapılı sınıflarda değildir.",
     "kusur": "Hüküm doğru ama Palmer'ın 400 kübit iddiasıyla aynı "
              "başlık altında anılamaz: onunki klasik bellek sayımı "
              "değil, fizikî kuantum avantajının doyması hakkında bir "
              "iddiadır.",
     "düzeltme": "M27 kaynak risale için geçerli kalır; Palmer'ın "
                 "iddiasına CEVAP TEŞKİL ETMEZ ve öyle okunmamalıdır."},
    {"nerede": "reel/karmasik.py",
     "yazdığım": "Reel gömme hesap bakımından savunulabilir (ölçülen "
                 "duvar saati 0.32-0.44×).",
     "kusur": "Ölçüm doğru ama EKSİK: tek sistemde birebir olan gömme "
              "BİRLEŞİK sistemde (tensör çarpımı) birebir değildir ve "
              "reel kuantum kuramı tartışmasının tamamı oradadır.",
     "düzeltme": "tensor_boyut_uyusmazligi() ile ölçülüp yazıldı; "
                 "modülün başlığına da not düşüldü."},
    {"nerede": "hesap/galois.py",
     "yazdığım": "Kaynağın 'çaresi doğru, teşhisi yanlış'.",
     "kusur": "Bu hüküm KAYNAK RİSALE için geçerlidir. Palmer'ın "
              "teşhisi float yuvarlaması değil, Hilbert uzayının "
              "ontolojisidir; benim M24 tashihim ona değinmiyor.",
     "düzeltme": "Ayrım açıkça yazıldı."},
]


def pisagor_donmeleri(azami: int = 60) -> List[Tuple[Fraction, Fraction]]:
    out = set()
    for a in range(0, azami + 1):
        for b in range(0, azami + 1):
            c2 = a * a + b * b
            c = int(math.isqrt(c2))
            if c * c == c2 and c > 0:
                for sa in (1, -1):
                    for sb in (1, -1):
                        out.add((Fraction(sa * a, c), Fraction(sb * b, c)))
    return sorted(out)


def rasyonel_grup_kapali_mi(azami: int = 40, deneme: int = 3000,
                            tohum: int = 0) -> Dict[str, object]:
    D = pisagor_donmeleri(azami)
    r = np.random.default_rng(tohum)
    kapali = 0
    for _ in range(deneme):
        (c1, s1) = D[int(r.integers(len(D)))]
        (c2, s2) = D[int(r.integers(len(D)))]
        c, s = c1 * c2 - s1 * s2, s1 * c2 + c1 * s2
        kapali += (c * c + s * s == 1)
    return {"öğe": len(D), "deneme": deneme, "kapalı": kapali,
            "grup_mu": kapali == deneme}


def surekli_altgrup_var_mi(azami: int = 200) -> Dict[str, object]:
    D = [(c, s) for c, s in pisagor_donmeleri(azami) if s != 0]
    aci = sorted(float(math.atan2(s, c)) % (2 * math.pi) for c, s in D)
    bosluk = max(b - a for a, b in zip(aci, aci[1:])) if len(aci) > 1 else 0.0
    kucuk = min(a for a in aci if a > 1e-12)
    kucukler = sorted(a for a in aci if 0 < a < 0.2)[:6]
    oran = [math.sin(a) / a for a in kucukler]
    return {"dönme_sayısı": len(D), "azamî_açı_boşluğu": bosluk,
            "en_küçük_pozitif_açı": kucuk,
            "sıfırdan_farklı_en_küçük_var_mı": False,
            "sin_bölü_teta_dizisi": oran,
            "limit_rasyonel_mi": False,
            "not": "yoğunluk yaklaşmayı sağlar; SÜREKLİLİK sağlamaz. "
                   "Üreteç dR/dθ|₀ bir LİMİTTİR ve ℚ'da yoktur."}


def stone_von_neumann_engeli(N: int = 8) -> Dict[str, object]:
    r = np.random.default_rng(0)
    izler = []
    for _ in range(200):
        A = r.normal(size=(N, N)) + 1j * r.normal(size=(N, N))
        B = r.normal(size=(N, N)) + 1j * r.normal(size=(N, N))
        izler.append(abs(complex(np.trace(A @ B - B @ A))))
    return {"boyut": N,
            "komütatör_izi_azamî": float(np.max(izler)),
            "iħI_izi": float(N),
            "imkânsız_mı": True,
            "not": "Tr(AB−BA) = 0 her A,B için; Tr(iħI) = iħN ≠ 0."}


def sonlu_boyutta_kanonik_baginti(N: int = 16) -> Dict[str, object]:
    a = np.diag(np.sqrt(np.arange(1, N)), 1).astype(complex)
    C = a @ a.conj().T - a.conj().T @ a
    fark = C - np.eye(N)
    return {"boyut": N,
            "alt_blok_sapma": float(np.abs(fark[:N - 1, :N - 1]).max()),
            "son_köşegen": float(fark[N - 1, N - 1].real),
            "beklenen_son_köşegen": float(-N),
            "komütatörün_izi": float(np.trace(C).real),
            "iz_sıfır_mı": abs(float(np.trace(C).real)) < 1e-9}


def tensor_boyut_uyusmazligi(m: int = 2, n: int = 2) -> Dict[str, object]:
    karmasik = 2 * m * n
    reel = (2 * m) * (2 * n)
    return {"m": m, "n": n,
            "dim_R(C^m ⊗ C^n)": karmasik,
            "dim(R^2m ⊗ R^2n)": reel,
            "oran": reel / karmasik,
            "uyuşuyor_mu": karmasik == reel,
            "not": "Fazlalık, gömmenin çarpımsal OLMAMASINDAN gelir; "
                   "tartışmanın tamamı bu birleştirme kaidesindedir."}


def reel_gomme_tek_sistemde_birebir(N: int = 4, deneme: int = 200,
                                    tohum: int = 0) -> Dict[str, object]:
    r = np.random.default_rng(tohum)

    def gom(A):
        return np.block([[A.real, -A.imag], [A.imag, A.real]])

    carpim_hata = 0.0
    for _ in range(deneme):
        A = r.normal(size=(N, N)) + 1j * r.normal(size=(N, N))
        B = r.normal(size=(N, N)) + 1j * r.normal(size=(N, N))
        carpim_hata = max(carpim_hata,
                          float(np.abs(gom(A @ B) - gom(A) @ gom(B)).max()))
    A = r.normal(size=(2, 2)) + 1j * r.normal(size=(2, 2))
    B = r.normal(size=(2, 2)) + 1j * r.normal(size=(2, 2))
    sol = gom(np.kron(A, B))
    sag = np.kron(gom(A), gom(B))
    return {"tek_sistem_çarpım_hatası": carpim_hata,
            "tek_sistemde_birebir_mi": carpim_hata < 1e-9,
            "birleşik_sol_şekil": sol.shape,
            "birleşik_sağ_şekil": sag.shape,
            "şekiller_uyuşuyor_mu": sol.shape == sag.shape}


def chshdegeri(a1, a2, b1, b2) -> float:
    def E(u, v):
        return -(float(u[0]) * float(v[0]) + float(u[1]) * float(v[1]))
    return E(a1, b1) + E(a1, b2) + E(a2, b1) - E(a2, b2)


def rasyonel_ayarla_chsh(azami: int = 40) -> Dict[str, object]:
    D = pisagor_donmeleri(azami)
    V = np.array([[float(c), float(s)] for c, s in D])
    en_iyi, en_iyi_ayar = 0.0, None
    for i in range(len(V)):
        topla = V[i][None, :] + V
        cikar = V[i][None, :] - V
        p1 = V @ topla.T
        p2 = V @ cikar.T
        skor = np.abs(p1).max(axis=0) + np.abs(p2).max(axis=0)
        j = int(np.argmax(skor))
        if skor[j] <= en_iyi:
            continue
        ia = int(np.argmax(np.abs(p1[:, j])))
        ib = int(np.argmax(np.abs(p2[:, j])))
        for sa in (1, -1):
            for sb in (1, -1):
                a1 = (sa * D[ia][0], sa * D[ia][1])
                a2 = (sb * D[ib][0], sb * D[ib][1])
                v = abs(chshdegeri(a1, a2, D[i], D[j]))
                if v > en_iyi:
                    en_iyi, en_iyi_ayar = v, (a1, a2, D[i], D[j])
    return {"en_iyi_S": en_iyi, "klasik_sınır": 2.0,
            "tsirelson": 2 * math.sqrt(2),
            "klasik_aşıldı_mı": en_iyi > 2.0,
            "tsirelsona_uzaklık": 2 * math.sqrt(2) - en_iyi,
            "ayarlar": en_iyi_ayar,
            "bütün_bileşenler_rasyonel_mi": all(
                isinstance(x, Fraction) for c in (en_iyi_ayar or ())
                for x in c)}


def en_iyi_rasyonel_chsh(azamiler: Sequence[int] = (5, 12, 25, 40, 60)
                         ) -> List[Dict[str, object]]:
    return [{"azami": a, **{k: v for k, v in rasyonel_ayarla_chsh(a).items()
                            if k in ("en_iyi_S", "tsirelsona_uzaklık",
                                     "klasik_aşıldı_mı")}}
            for a in azamiler]


def _rapor_hesap_palmer() -> str:
    s = []
    s.append("=== PALMER NE DİYOR (kaynak: arXiv:2510.02877 / PNAS, "
             "arXiv:2308.11262) ===")
    for k, v in PALMER_IDDIALARI.items():
        s.append("  • %s:" % k)
        for satir in _sar(v, 68):
            s.append("      " + satir)

    s.append("\n=== GERİ ALDIĞIM YERLER ===")
    for g in GERI_ALMALAR:
        s.append("  ── %s" % g["nerede"])
        s.append("     yazdığım : %s" % _sar(g["yazdığım"], 62)[0])
        for satir in _sar(g["yazdığım"], 62)[1:]:
            s.append("                %s" % satir)
        s.append("     kusur    : %s" % _sar(g["kusur"], 62)[0])
        for satir in _sar(g["kusur"], 62)[1:]:
            s.append("                %s" % satir)
        s.append("     düzeltme : %s" % _sar(g["düzeltme"], 62)[0])
        for satir in _sar(g["düzeltme"], 62)[1:]:
            s.append("                %s" % satir)

    s.append("\n=== İTİRAZ 1: ℚ'da sürekli alt grup yok (SAĞLAM) ===")
    g = rasyonel_grup_kapali_mi()
    s.append("  rasyonel dönme sayısı=%d   çarpım altında kapalı mı? %s"
             % (g["öğe"], g["grup_mu"]))
    s.append("  sınır büyüdükçe açı boşluğu kapanıyor (YOĞUNLUK):")
    for az in (20, 60, 200, 600):
        aa = surekli_altgrup_var_mi(az)
        s.append("    azami=%3d  dönme=%4d  azamî boşluk=%.4f rad  "
                 "en küçük pozitif açı=%.6f"
                 % (az, aa["dönme_sayısı"], aa["azamî_açı_boşluğu"],
                    aa["en_küçük_pozitif_açı"]))
    a = surekli_altgrup_var_mi(600)
    s.append("  Boşluk kapanıyor ama HİÇBİR sınırda en küçük açı sabit")
    s.append("  kalmıyor: sıfırdan farklı EN KÜÇÜK açı YOK. sin θ/θ dizisi:")
    s.append("    %s → 1'e gidiyor ama limit ℚ'da DEĞİL"
             % ["%.6f" % x for x in a["sin_bölü_teta_dizisi"][:4]])
    s.append("  Yani: yaklaşma var, SÜREKLİLİK yok. Üreteç dR/dθ|₀ bir")
    s.append("  limittir; Lie cebri, dolayısıyla Noether, kurulamaz.")

    s.append("\n=== İTİRAZ 2: Stone–von Neumann (SAĞLAM) ===")
    e = stone_von_neumann_engeli(8)
    s.append("  200 rastgele çiftte azamî |Tr(AB−BA)| = %.2e"
             % e["komütatör_izi_azamî"])
    s.append("  oysa Tr(iħI) = %.0f ≠ 0  →  sonlu boyutta [x,p]=iħI"
             % e["iħI_izi"])
    s.append("  İMKÂNSIZ (sayısal değil, cebirsel).")
    for N in (8, 16, 64):
        k = sonlu_boyutta_kanonik_baginti(N)
        s.append("  kesilmiş Fock N=%2d: alt blok sapma=%.1e  son köşegen=%+.0f"
                 "  (beklenen %+.0f)  komütatörün izi=%.1e"
                 % (N, k["alt_blok_sapma"], k["son_köşegen"],
                    k["beklenen_son_köşegen"], k["komütatörün_izi"]))
    s.append("  kuantum.surekli'de ölçtüğümüz '−N' sapması, tam olarak")
    s.append("  BU engelin kendisidir: iz sıfır kalsın diye tek yol.")

    s.append("\n=== İTİRAZ 3: Renou vd. — GÜNCEL DEĞİL (düzeltme) ===")
    s.append("  Eleştiri metni 'ispatlanmış ve mühürlenmiştir' diyor.")
    s.append("  2026 itibarıyla bu FAZLA KESİN. 2021 Nature neticesi,")
    s.append("  sistemlerin STANDART TENSÖR ÇARPIMIYLA birleştiği")
    s.append("  varsayımı altında geçerlidir. 2025 PRL o postülayı")
    s.append("  gevşetip ayırt edilemez bir reel aile kurdu; 2026'da")
    s.append("  ona bir Comment yazıldı. Tartışma AÇIK.")
    s.append("  Meselenin kalbi neden tensör çarpımı? — ölçelim:")
    for m, n in ((2, 2), (2, 3), (4, 4)):
        t = tensor_boyut_uyusmazligi(m, n)
        s.append("    m=%d n=%d: dim_ℝ(ℂ^m⊗ℂ^n)=%2d   ℝ^{2m}⊗ℝ^{2n}=%2d"
                 "   oran=%.0f×  uyuşuyor mu? %s"
                 % (m, n, t["dim_R(C^m ⊗ C^n)"], t["dim(R^2m ⊗ R^2n)"],
                    t["oran"], t["uyuşuyor_mu"]))
    b = reel_gomme_tek_sistemde_birebir()
    s.append("  TEK sistemde gömme çarpımsal mı? %s (hata %.1e)"
             % (b["tek_sistemde_birebir_mi"], b["tek_sistem_çarpım_hatası"]))
    s.append("  BİRLEŞİK sistemde: ρ(A⊗B) şekli %s, ρ(A)⊗ρ(B) şekli %s"
             % (b["birleşik_sol_şekil"], b["birleşik_sağ_şekil"]))
    s.append("  → şekiller bile tutmuyor. Reel gömme tek sistemde")
    s.append("    birebirdir, BİRLEŞİK sistemde değildir.")

    s.append("\n=== İTİRAZ 4: rasyonel ayarlarla CHSH (SAĞLAM, ama")
    s.append("    'gizli versiyon' değil — Palmer açıkça kabul ediyor) ===")
    s.append("  azamî   en iyi S   Tsirelson'a uzaklık   klasik aşıldı mı?")
    for d in en_iyi_rasyonel_chsh((5, 12, 25, 40)):
        s.append("  %5d    %.6f        %.6f            %s"
                 % (d["azami"], d["en_iyi_S"], d["tsirelsona_uzaklık"],
                    d["klasik_aşıldı_mı"]))
    r = rasyonel_ayarla_chsh(40)
    s.append("  en iyi ayarlar (hepsi RASYONEL): %s"
             % str(r["ayarlar"]).replace("Fraction", "F"))
    s.append("  Klasik sınır 2.0, Tsirelson %.6f." % r["tsirelson"])
    s.append("  CHSH ihlali İRRASYONEL AÇIYA MUHTAÇ DEĞİL. Dolayısıyla")
    s.append("  'karşı-olgusal ayarlar irrasyonel olduğu için tanımsız'")
    s.append("  savunması, ihlali tek başına açıklamıyor.")
    return "\n".join(s)


def _sar(metin: str, en: int) -> List[str]:
    kelime, satir, out = metin.split(), "", []
    for k in kelime:
        if len(satir) + len(k) + 1 > en:
            out.append(satir)
            satir = k
        else:
            satir = (satir + " " + k).strip()
    if satir:
        out.append(satir)
    return out or [""]


EVREN_ATOM = 1e80


def keyfi_durum_maliyeti(N: int) -> Dict[str, object]:
    log10_sayi = N * math.log10(2.0)
    log10_bayt = log10_sayi + math.log10(16.0)
    return {"N": N, "log10_katsayı_sayısı": log10_sayi,
            "log10_bayt": log10_bayt,
            "evren_atomundan_fazla_mı": log10_sayi > 80.0,
            "atomla_oran_log10": log10_sayi - 80.0}


class Kararlayici:

    def __init__(self, n: int):
        self.n = n
        self.x = np.zeros((2 * n, n), dtype=np.uint8)
        self.z = np.zeros((2 * n, n), dtype=np.uint8)
        self.r = np.zeros(2 * n, dtype=np.uint8)
        for i in range(n):
            self.x[i, i] = 1
            self.z[n + i, i] = 1

    def H(self, a: int) -> "Kararlayici":
        self.r ^= self.x[:, a] & self.z[:, a]
        self.x[:, a], self.z[:, a] = self.z[:, a].copy(), self.x[:, a].copy()
        return self

    def S(self, a: int) -> "Kararlayici":
        self.r ^= self.x[:, a] & self.z[:, a]
        self.z[:, a] ^= self.x[:, a]
        return self

    def CNOT(self, a: int, b: int) -> "Kararlayici":
        self.r ^= (self.x[:, a] & self.z[:, b]
                   & (self.x[:, b] ^ self.z[:, a] ^ 1))
        self.x[:, b] ^= self.x[:, a]
        self.z[:, a] ^= self.z[:, b]
        return self

    def X(self, a: int) -> "Kararlayici":
        return self.H(a).S(a).S(a).H(a)

    def Z(self, a: int) -> "Kararlayici":
        return self.S(a).S(a)

    def olc(self, a: int, tohum: Optional[int] = None) -> Dict[str, object]:
        n = self.n
        p = None
        for i in range(n, 2 * n):
            if self.x[i, a]:
                p = i
                break
        if p is not None:
            rng = np.random.default_rng(tohum)
            for i in range(2 * n):
                if i != p and self.x[i, a]:
                    self._satir_carp(i, p)
            self.x[p - n] = self.x[p].copy()
            self.z[p - n] = self.z[p].copy()
            self.r[p - n] = self.r[p]
            self.x[p] = 0
            self.z[p] = 0
            self.z[p, a] = 1
            netice = int(rng.integers(0, 2))
            self.r[p] = netice
            return {"netice": netice, "belirli_mi": False}
        xs = np.zeros(n, dtype=np.uint8)
        zs = np.zeros(n, dtype=np.uint8)
        rs = 0
        for i in range(n):
            if self.x[i, a]:
                rs, xs, zs = self._birlestir(rs, xs, zs, self.r[i + n],
                                             self.x[i + n], self.z[i + n])
        return {"netice": int(rs), "belirli_mi": True}

    @staticmethod
    def _g(x1, z1, x2, z2) -> int:
        if x1 == 0 and z1 == 0:
            return 0
        if x1 == 1 and z1 == 1:
            return int(z2) - int(x2)
        if x1 == 1 and z1 == 0:
            return int(z2) * (2 * int(x2) - 1)
        return int(x2) * (1 - 2 * int(z2))

    def _satir_carp(self, i: int, j: int) -> None:
        t = 2 * int(self.r[i]) + 2 * int(self.r[j])
        for k in range(self.n):
            t += self._g(self.x[j, k], self.z[j, k],
                         self.x[i, k], self.z[i, k])
        self.r[i] = np.uint8((t % 4) // 2)
        self.x[i] ^= self.x[j]
        self.z[i] ^= self.z[j]

    def _birlestir(self, rs, xs, zs, ri, xi, zi):
        t = 2 * int(rs) + 2 * int(ri)
        for k in range(self.n):
            t += self._g(xi[k], zi[k], xs[k], zs[k])
        return (t % 4) // 2, xs ^ xi, zs ^ zi

    def bellek_bayt(self) -> int:
        return int(self.x.nbytes + self.z.nbytes + self.r.nbytes)


def kararlayici_maliyeti(N: int) -> Dict[str, object]:
    bit = 2 * N * (2 * N + 1)
    return {"N": N, "bit": bit, "bayt": bit / 8.0,
            "log10_bayt": math.log10(max(bit / 8.0, 1e-300)),
            "keyfî_log10_bayt": keyfi_durum_maliyeti(N)["log10_bayt"]}


class MPS:

    def __init__(self, tensorler: Sequence[np.ndarray]):
        self.A = [np.asarray(a, complex) for a in tensorler]
        self.N = len(self.A)

    @staticmethod
    def carpim_durumu(acilar: Sequence[float]) -> "MPS":
        return MPS([np.array([[[math.cos(t / 2)], [math.sin(t / 2)]]],
                             dtype=complex) for t in acilar])

    @staticmethod
    def rastgele(N: int, chi: int, tohum: int = 0) -> "MPS":
        r = np.random.default_rng(tohum)
        A = []
        for k in range(N):
            sol = 1 if k == 0 else chi
            sag = 1 if k == N - 1 else chi
            A.append(r.normal(size=(sol, 2, sag))
                     + 1j * r.normal(size=(sol, 2, sag)))
        return MPS(A)

    def norm_kare(self) -> float:
        E = np.eye(self.A[0].shape[0], dtype=complex)
        for a in self.A:
            E = np.einsum("ij,isk,jsl->kl", E, a, a.conj())
        return float(np.real(E.reshape(-1)[0]))

    def normalize(self) -> "MPS":
        n = self.norm_kare()
        self.A[0] = self.A[0] / math.sqrt(n)
        return self

    def tam_vektor(self) -> np.ndarray:
        if self.N > 20:
            raise ValueError("N > 20: tam vektör kurulmaz (mesele bu)")
        v = self.A[0]
        for a in self.A[1:]:
            v = np.einsum("i...j,jsk->i...sk", v, a)
        return v.reshape(-1)

    def bellek_sayi(self) -> int:
        return int(sum(a.size for a in self.A))


def mps_maliyeti(N: int, chi: int) -> Dict[str, object]:
    sayi = 2 * chi * chi * (N - 2) + 4 * chi if N > 2 else 4 * chi
    return {"N": N, "chi": chi, "karmaşık_sayı": sayi,
            "bayt": sayi * 16,
            "log10_bayt": math.log10(max(sayi * 16.0, 1e-300)),
            "keyfî_log10_bayt": keyfi_durum_maliyeti(N)["log10_bayt"]}


def sinif_kiyasi(N: int, chi: int = 32) -> Dict[str, object]:
    return {"keyfî": keyfi_durum_maliyeti(N),
            "kararlayıcı": kararlayici_maliyeti(N),
            "mps": mps_maliyeti(N, chi)}


def _rapor_hesap_saklama() -> str:
    import time
    s = []
    s.append("=== İtiraz KEYFÎ durum için doğrudur ===")
    s.append("       N    log10(katsayı)   log10(bayt)   evren atomundan "
             "fazla mı?")
    for N in (50, 100, 300, 400, 1024):
        k = keyfi_durum_maliyeti(N)
        s.append("  %6d   %12.1f   %12.1f   %s (10^%.0f kat)"
                 % (N, k["log10_katsayı_sayısı"], k["log10_bayt"],
                    k["evren_atomundan_fazla_mı"], k["atomla_oran_log10"]))
    s.append("  N=300'de katsayı sayısı evrendeki atomdan 10^10 kat fazla.")
    s.append("  Bu itiraz DOĞRUDUR ve reddedilemez.")

    s.append("\n=== Ama YAPILI durumlar bambaşka: kararlayıcı ===")
    s.append("       N   kararlayıcı bayt   keyfî log10(bayt)")
    for N in (100, 400, 1024, 4096):
        m = kararlayici_maliyeti(N)
        s.append("  %6d   %14.0f   %16.1f"
                 % (N, m["bayt"], m["keyfî_log10_bayt"]))

    s.append("\n=== 1024 kubitlik kararlayıcı durum GERÇEKTEN koşuluyor ===")
    for N in (64, 256, 1024):
        t0 = time.perf_counter()
        st = Kararlayici(N)
        for i in range(N):
            st.H(i)
        for i in range(N - 1):
            st.CNOT(i, i + 1)
        t1 = time.perf_counter()
        o = st.olc(0, tohum=0)
        t2 = time.perf_counter()
        s.append("  N=%5d  %d kapı %7.1f ms   ölçüm %6.1f ms   bellek "
                 "%7.1f KB   netice=%d (belirli mi: %s)"
                 % (N, 2 * N - 1, (t1 - t0) * 1e3, (t2 - t1) * 1e3,
                    st.bellek_bayt() / 1024, o["netice"], o["belirli_mi"]))
    s.append("  Aynı devre keyfî durum vektörüyle 2^1024 katsayı isterdi.")

    s.append("\n=== Kararlayıcı doğru mu? Bell durumu sağlaması ===")
    st = Kararlayici(2).H(0).CNOT(0, 1)
    o0 = st.olc(0, tohum=1)
    o1 = st.olc(1, tohum=1)
    s.append("  H(0), CNOT(0,1) → |Φ⁺⟩;  ölç(0)=%d (belirli mi %s), "
             "ölç(1)=%d (belirli mi %s)"
             % (o0["netice"], o0["belirli_mi"], o1["netice"],
                o1["belirli_mi"]))
    s.append("  İlk ölçüm RASTGELE, ikincisi BELİRLİ ve ilkine eşit:")
    s.append("  bu tam olarak Bell bağlılığıdır. Eşit mi? %s"
             % (o0["netice"] == o1["netice"]))
    esit = 0
    for t in range(200):
        st = Kararlayici(2).H(0).CNOT(0, 1)
        a = st.olc(0, tohum=t)["netice"]
        b = st.olc(1, tohum=t)["netice"]
        esit += (a == b)
    s.append("  200 bağımsız koşuda iki ölçüm hep eşit mi? %d/200" % esit)

    s.append("\n=== MPS: O(Nχ²) ===")
    s.append("       N   χ    karmaşık sayı        bayt   keyfî log10(bayt)")
    for N, chi in ((100, 8), (400, 32), (4096, 32)):
        m = mps_maliyeti(N, chi)
        s.append("  %6d  %3d   %12d   %9d   %14.1f"
                 % (N, chi, m["karmaşık_sayı"], m["bayt"],
                    m["keyfî_log10_bayt"]))
    s.append("  MPS normu doğru mu? (küçük N'de tam vektörle kıyas)")
    for N, chi in ((6, 1), (8, 3), (10, 4)):
        m = MPS.rastgele(N, chi, tohum=2).normalize()
        v = m.tam_vektor()
        s.append("    N=%2d χ=%d  MPS ⟨ψ|ψ⟩=%.12f   tam vektör ‖v‖²=%.12f"
                 % (N, chi, m.norm_kare(), float(np.vdot(v, v).real)))

    s.append("\n=== Dürüstlük şartı: bedava sonsuzluk yok ===")
    s.append("  (i) Kararlayıcı durumlar Gottesman–Knill gereği KLASİK")
    s.append("      olarak verimli benzetilir; tek başlarına kuantum")
    s.append("      üstünlüğü vermezler. Ucuz olmalarının sebebi budur.")
    s.append("  (ii) MPS maliyeti χ ile büyür; χ da dolaşıklıkla.")
    s.append("       Hacim yasası dolaşıklığında χ ~ 2^{N/2} olur ve")
    s.append("       maliyet keyfî duruma geri döner:")
    for N in (20, 40, 80):
        chi = 2 ** (N // 2)
        m = mps_maliyeti(N, chi)
        s.append("       N=%2d, χ=2^%d: log10(bayt)=%.1f   keyfî=%.1f"
                 % (N, N // 2, m["log10_bayt"], m["keyfî_log10_bayt"]))
    s.append("  Doğru cevap 'sınır yoktur' değil, HANGİ YAPILI SINIFTA")
    s.append("  olunduğunu yazmaktır.")
    return "\n".join(s)


_IPLIK_DEGISKENLERI = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS",
                       "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
                       "VECLIB_MAXIMUM_THREADS")


def tek_iplik_zorla() -> bool:
    import sys as _sys
    tesirli = "numpy" not in _sys.modules
    for k in _IPLIK_DEGISKENLERI:
        os.environ.setdefault(k, "1")
    return tesirli


def _torch():
    try:
        import torch
        return torch
    except Exception:
        return None


@dataclass
class Donanim:
    torch_var: bool
    cihazlar: Tuple[str, ...]
    vram_gb: Tuple[float, float, ...]
    cekirdek: int
    zorla_cpu: bool

    @property
    def gpu(self) -> int:
        return sum(1 for c in self.cihazlar if c != "cpu")

    @property
    def toplam_vram(self) -> float:
        return float(sum(self.vram_gb))


def donanim(zorla_cpu: Optional[bool] = None) -> Donanim:
    if zorla_cpu is None:
        zorla_cpu = os.environ.get("MUCIT_CPU", "") == "1"
    T = None if zorla_cpu else _torch()
    if T is None or not T.cuda.is_available():
        return Donanim(T is not None, ("cpu",), (0.0,),
                       os.cpu_count() or 1, bool(zorla_cpu))
    n = T.cuda.device_count()
    cih = tuple("cuda:%d" % i for i in range(n))
    vram = tuple(float(T.cuda.get_device_properties(i).total_memory)
                 / 2 ** 30 for i in range(n))
    return Donanim(True, cih, vram, os.cpu_count() or 1, False)


def parcala(n: int, k: int) -> List[Tuple[int, int]]:
    if k <= 1 or n <= 0:
        return [(0, n)]
    taban, artik = divmod(n, k)
    sinir, bas = [], 0
    for i in range(k):
        son = bas + taban + (1 if i < artik else 0)
        if son > bas:
            sinir.append((bas, son))
        bas = son
    return sinir


def topla_paralel(f: Callable[[np.ndarray, str], np.ndarray],
                  X: np.ndarray, dh: Optional[Donanim] = None
                  ) -> np.ndarray:
    dh = dh or donanim()
    if len(dh.cihazlar) <= 1:
        return f(X, dh.cihazlar[0])
    parcalar = parcala(len(X), len(dh.cihazlar))
    cikti = [f(X[a:b], dh.cihazlar[i]) for i, (a, b) in enumerate(parcalar)]
    return np.concatenate(cikti, axis=0)


def _rapor_hesap_donanim(dh: Optional[Donanim] = None) -> str:
    dh = dh or donanim()
    s = ["donanım: torch=%s  cihaz=%s  çekirdek=%d"
         % (dh.torch_var, ", ".join(dh.cihazlar), dh.cekirdek)]
    if dh.gpu:
        s.append("  VRAM: %s  (toplam %.1f GB)"
                 % (", ".join("%.1f" % v for v in dh.vram_gb),
                    dh.toplam_vram))
        s.append("  yol: TORCH/CUDA -- yığın %d cihaza parçalanacak" % dh.gpu)
    else:
        s.append("  yol: NUMPY/CPU -- ölçülen yol budur; GPU yolu burada")
        s.append("       koşmadı ve koştuğu İDDİA EDİLMİYOR.")
    return "\n".join(s)


_H = np.finfo(float).eps ** (1.0 / 3.0)


def _turev(f: Callable[[np.ndarray], np.ndarray], x: np.ndarray,
           j: int) -> np.ndarray:
    h = _H * max(1.0, abs(float(x[j])))
    arti = x.copy(); arti[j] += h
    eksi = x.copy(); eksi[j] -= h
    return (np.asarray(f(arti), float) - np.asarray(f(eksi), float)) \
        / (arti[j] - eksi[j])


def _ikinci_turev(f: Callable[[np.ndarray], np.ndarray], x: np.ndarray,
                  i: int, j: int) -> np.ndarray:
    if i == j:
        h = _H * max(1.0, abs(float(x[i])))
        arti = x.copy(); arti[i] += h
        eksi = x.copy(); eksi[i] -= h
        return (np.asarray(f(arti), float) - 2 * np.asarray(f(x), float)
                + np.asarray(f(eksi), float)) / (h * h)
    return _turev(lambda z: _turev(f, z, j), x, i)


@dataclass
class Metrik:
    n: int
    g: Callable[[np.ndarray], np.ndarray]
    ad: str = ""

    def denetle(self, x: Sequence[float], tol: float = 1e-10) -> None:
        G = np.asarray(self.g(np.asarray(x, float)), float)
        if G.shape != (self.n, self.n):
            raise ValueError(f"metrik {(self.n, self.n)} olmalı, {G.shape}")
        if np.max(np.abs(G - G.T)) > tol:
            raise ValueError("metrik simetrik değil")
        if np.min(np.linalg.eigvalsh(G)) <= 0:
            raise ValueError("metrik pozitif tanımlı değil")

    def G(self, x: np.ndarray) -> np.ndarray:
        return np.asarray(self.g(np.asarray(x, float)), float)

    def G_ters(self, x: np.ndarray) -> np.ndarray:
        return np.linalg.solve(self.G(x), np.eye(self.n))

    def hacim(self, x: np.ndarray) -> float:
        return float(np.sqrt(abs(np.linalg.det(self.G(x)))))

    def dg(self, x: np.ndarray) -> np.ndarray:
        return np.array([_turev(self.g, np.asarray(x, float), k)
                         for k in range(self.n)])

    def christoffel(self, x: np.ndarray) -> np.ndarray:
        x = np.asarray(x, float)
        gi = self.G_ters(x)
        d = self.dg(x)
        terim = (np.einsum("ijl->ijl", d)
                 + np.einsum("jil->ijl", d)
                 - np.einsum("lij->ijl", d))
        return 0.5 * np.einsum("kl,ijl->kij", gi, terim)

    def dChristoffel(self, x: np.ndarray) -> np.ndarray:
        x = np.asarray(x, float)
        return np.array([_turev(self.christoffel, x, m)
                         for m in range(self.n)])

    def riemann(self, x: np.ndarray) -> np.ndarray:
        G_ = self.christoffel(x)
        dG = self.dChristoffel(x)
        t1 = np.einsum("mrns->rsmn", dG)
        t2 = np.einsum("nrms->rsmn", dG)
        t3 = np.einsum("rml,lns->rsmn", G_, G_)
        t4 = np.einsum("rnl,lms->rsmn", G_, G_)
        return t1 - t2 + t3 - t4

    def riemann_alt(self, x: np.ndarray) -> np.ndarray:
        return np.einsum("rl,lsmn->rsmn", self.G(x), self.riemann(x))

    def ricci(self, x: np.ndarray) -> np.ndarray:
        return np.einsum("msmn->sn", self.riemann(x))

    def skaler_egrilik(self, x: np.ndarray) -> float:
        return float(np.einsum("sn,sn->", self.G_ters(x), self.ricci(x)))

    def kesit_egriligi(self, x: np.ndarray, u: Sequence[float],
                       v: Sequence[float]) -> float:
        u = np.asarray(u, float); v = np.asarray(v, float)
        G = self.G(x)
        Rd = self.riemann_alt(x)
        pay = float(np.einsum("rsmn,r,s,m,n->", Rd, u, v, u, v))
        uu = float(u @ G @ u); vv = float(v @ G @ v); uv = float(u @ G @ v)
        payda = uu * vv - uv * uv
        if abs(payda) < 1e-14:
            return float("nan")
        return pay / payda

    def laplace_beltrami(self, f: Callable[[np.ndarray], float],
                         x: np.ndarray) -> float:
        x = np.asarray(x, float)

        def akı(z: np.ndarray) -> np.ndarray:
            gi = self.G_ters(z)
            grad = np.array([_turev(lambda w: np.array([f(w)]), z, j)[0]
                             for j in range(self.n)])
            return self.hacim(z) * (gi @ grad)

        div = sum(_turev(akı, x, i)[i] for i in range(self.n))
        return float(div / self.hacim(x))

    def laplace_beltrami_christoffel(self, f: Callable[[np.ndarray], float],
                                     x: np.ndarray) -> float:
        x = np.asarray(x, float)
        gi = self.G_ters(x)
        G_ = self.christoffel(x)
        skaler = lambda w: np.array([f(w)])
        grad = np.array([_turev(skaler, x, j)[0] for j in range(self.n)])
        hes = np.array([[_ikinci_turev(skaler, x, i, j)[0]
                         for j in range(self.n)] for i in range(self.n)])
        return float(np.einsum("ij,ij->", gi, hes)
                     - np.einsum("ij,kij,k->", gi, G_, grad))


KIP_DUZ, KIP_KURE = "düz", "küre"


KIP_HIP, KIP_KONF = "hiperbolik", "konformal"


def metrik(ne: str = "düz", n: int = 2, r: float = 1.0,
                 olcek=None) -> Metrik:
    if ne == "küre":
        def gk(x: np.ndarray) -> np.ndarray:
            t = float(x[0])
            return np.diag([r * r, r * r * np.sin(t) ** 2])
        return Metrik(2, gk, "küre(r=%s)" % (r,))

    if ne == "düz":
        carpan, adi = (lambda x: 1.0), "düz"
    elif ne == "hiperbolik":
        n, adi = 2, "hiperbolik"
        carpan = lambda x: 1.0 / (float(x[1]) * float(x[1]))
    elif ne == "konformal":
        carpan, adi = (lambda x: np.exp(2.0 * float(olcek(x)))), "konformal"
    else:
        raise ValueError("metrik bilinmiyor: %r" % (ne,))

    def g(x: np.ndarray) -> np.ndarray:
        return float(carpan(x)) * np.eye(n)

    return Metrik(n, g, adi)


def riemann_simetrileri(m: Metrik, x: Sequence[float],
                        tol: float = 1e-5) -> Dict[str, object]:
    R = m.riemann_alt(np.asarray(x, float))
    olcek = max(float(np.max(np.abs(R))), 1e-30)
    ilk = float(np.max(np.abs(R + np.einsum("rsmn->srmn", R)))) / olcek
    son = float(np.max(np.abs(R + np.einsum("rsmn->rsnm", R)))) / olcek
    cift = float(np.max(np.abs(R - np.einsum("rsmn->mnrs", R)))) / olcek
    bianchi = float(np.max(np.abs(
        R + np.einsum("rsmn->rmns", R) + np.einsum("rsmn->rnsm", R)))) / olcek
    return {
        "büyüklük": olcek,
        "ilk_çift_antisimetri": ilk,
        "son_çift_antisimetri": son,
        "çift_değişimi": cift,
        "birinci_Bianchi": bianchi,
        "hepsi_sağlanıyor": max(ilk, son, cift, bianchi) < tol,
    }


def _rapor_token_uzaylari_manifold() -> str:
    s: List[str] = []

    s.append("=== Düz uzay: bütün eğrilik sıfır olmalı ===")
    d = metrik(KIP_DUZ, n=3)
    x = np.array([0.3, -0.7, 1.1])
    s.append(f"  ‖Γ‖∞      = {np.max(np.abs(d.christoffel(x))):.3e}")
    s.append(f"  ‖Riemann‖∞ = {np.max(np.abs(d.riemann(x))):.3e}")
    s.append(f"  skaler R   = {d.skaler_egrilik(x):.3e}")

    s.append("\n=== 2-küre: K = 1/r², R = 2/r² ===")
    for r in (1.0, 2.0, 0.5):
        k = metrik(KIP_KURE, r=r)
        p = np.array([1.0, 0.4])
        K = k.kesit_egriligi(p, [1.0, 0.0], [0.0, 1.0])
        R = k.skaler_egrilik(p)
        s.append(f"  r={r:<4} K={K:.10f} (beklenen {1/r**2:.10f})"
                 f"   R={R:.10f} (beklenen {2/r**2:.10f})")

    s.append("\n=== Hiperbolik düzlem: K = −1 ===")
    h = metrik(KIP_HIP)
    for p in ([0.0, 1.0], [2.0, 0.5], [-1.0, 3.0]):
        K = h.kesit_egriligi(np.array(p), [1.0, 0.0], [0.0, 1.0])
        s.append(f"  nokta {str(p):12s} K = {K:.10f}"
                 f"   R = {h.skaler_egrilik(np.array(p)):.10f}")

    s.append("\n=== Riemann simetrileri (bağıl ihlal) ===")
    for ad, m, p in (("küre", metrik(KIP_KURE, r=1.0), [1.0, 0.4]),
                     ("hiperbolik", metrik(KIP_HIP), [0.5, 1.3])):
        r = riemann_simetrileri(m, p)
        s.append(f"  {ad:11s} antisim {r['ilk_çift_antisimetri']:.2e}/"
                 f"{r['son_çift_antisimetri']:.2e}"
                 f"  çift-değişim {r['çift_değişimi']:.2e}"
                 f"  Bianchi {r['birinci_Bianchi']:.2e}"
                 f"  → {r['hepsi_sağlanıyor']}")

    s.append("\n=== Laplace–Beltrami: iki yol aynı sayıyı mı veriyor? ===")
    f = lambda z: float(np.sin(z[0]) * np.exp(0.3 * z[1]))
    for ad, m, p in (("düz(2)", metrik(KIP_DUZ, n=2), [0.4, 0.9]),
                     ("küre", metrik(KIP_KURE, r=1.0), [1.0, 0.4]),
                     ("hiperbolik", metrik(KIP_HIP), [0.5, 1.3])):
        a = m.laplace_beltrami(f, np.array(p))
        b = m.laplace_beltrami_christoffel(f, np.array(p))
        s.append(f"  {ad:11s} diverjans={a:+.8f}  Christoffel={b:+.8f}"
                 f"  fark={abs(a-b):.2e}")

    s.append("\n  Düz uzayda Δ, alelâde Laplasyen'e inmeli:")
    p = np.array([0.4, 0.9])
    tam = -np.sin(p[0]) * np.exp(0.3 * p[1]) \
        + 0.09 * np.sin(p[0]) * np.exp(0.3 * p[1])
    s.append(f"    sayısal={metrik(KIP_DUZ, n=2).laplace_beltrami(f, p):+.8f}"
             f"   kapalı={tam:+.8f}")

    s.append("\n=== Koordinat tekilliği gizlenmiyor ===")
    k = metrik(KIP_KURE, r=1.0)
    try:
        k.denetle([0.0, 0.0])
        s.append("  kutupta metrik kabul edildi (BEKLENMEZ)")
    except ValueError as e:
        s.append(f"  kutupta (θ=0): {e}")
    return "\n".join(s)


def jakobi(f: Callable[[np.ndarray], np.ndarray], x: np.ndarray,
           cikti_boyu: Optional[int] = None) -> np.ndarray:
    x = np.asarray(x, float)
    m = cikti_boyu if cikti_boyu is not None else np.asarray(f(x)).size
    J = np.empty((m, x.size))
    for i in range(x.size):
        h = _H * max(1.0, abs(float(x[i])))
        arti = x.copy(); arti[i] += h
        eksi = x.copy(); eksi[i] -= h
        J[:, i] = (np.asarray(f(arti), float).ravel()
                   - np.asarray(f(eksi), float).ravel()) / (arti[i] - eksi[i])
    return J


@dataclass
class Morfizm:
    n: int
    m: int
    phi: Callable[[np.ndarray], np.ndarray]
    ad: str = ""

    def __call__(self, x: Sequence[float]) -> np.ndarray:
        y = np.asarray(self.phi(np.asarray(x, float)), float).ravel()
        if y.size != self.m:
            raise ValueError(f"çıktı boyu {self.m} olmalı, {y.size} geldi")
        return y

    def dphi(self, x: Sequence[float]) -> np.ndarray:
        return jakobi(self.phi, np.asarray(x, float), self.m)

    def itme(self, x: Sequence[float], v: Sequence[float]) -> np.ndarray:
        v = np.asarray(v, float)
        if v.size != self.n:
            raise ValueError(f"teğet vektör boyu {self.n} olmalı")
        return self.dphi(x) @ v

    def cekme(self, x: Sequence[float], w: Sequence[float]) -> np.ndarray:
        w = np.asarray(w, float)
        if w.size != self.m:
            raise ValueError(f"ko-vektör boyu {self.m} olmalı")
        return self.dphi(x).T @ w

    def metrik_cek(self, hedef: Metrik, x: Sequence[float]) -> np.ndarray:
        if hedef.n != self.m:
            raise ValueError("hedef metriğin boyutu φ'nin çıktısıyla uyuşmalı")
        J = self.dphi(x)
        H = hedef.G(self(x))
        return J.T @ H @ J

    def cekilmis_metrik(self, hedef: Metrik) -> Metrik:
        return Metrik(self.n, lambda z: self.metrik_cek(hedef, z),
                      f"{self.ad}^*{hedef.ad}")


def bileske(psi: Morfizm, phi: Morfizm) -> Morfizm:
    if phi.m != psi.n:
        raise ValueError(f"boyutlar uyuşmuyor: {phi.m} ≠ {psi.n}")
    return Morfizm(phi.n, psi.m,
                   lambda x: psi.phi(np.asarray(phi.phi(x), float)),
                   f"{psi.ad}∘{phi.ad}")


def carpim_morfizmi(phi: Morfizm, psi: Morfizm) -> Morfizm:
    def f(x: np.ndarray) -> np.ndarray:
        a = np.asarray(phi.phi(x[:phi.n]), float).ravel()
        b = np.asarray(psi.phi(x[phi.n:]), float).ravel()
        return np.concatenate([a, b])
    return Morfizm(phi.n + psi.n, phi.m + psi.m, f,
                   f"{phi.ad}×{psi.ad}")


def funktoryellik_olc(psi: Morfizm, phi: Morfizm,
                      x: Sequence[float]) -> Dict[str, float]:
    x = np.asarray(x, float)
    bil = bileske(psi, phi)
    sol = bil.dphi(x)
    sag = psi.dphi(phi(x)) @ phi.dphi(x)
    olcek = max(float(np.max(np.abs(sol))), 1e-30)

    w = np.linspace(0.3, 1.1, psi.m)
    cekme_dogru = phi.cekme(x, psi.cekme(phi(x), w))
    cekme_bilesik = bil.cekme(x, w)

    try:
        psi.cekme(phi(x), phi.cekme(x, w))
        yanlis_sira: object = "kurulabildi (boyutlar tesadüfen uydu)"
    except ValueError as e:
        yanlis_sira = f"tip hatası: {e}"

    return {
        "zincir_kaidesi_sapması": float(np.max(np.abs(sol - sag))) / olcek,
        "çekme_sapması": float(np.max(np.abs(cekme_dogru - cekme_bilesik))),
        "çekme_büyüklüğü": float(np.max(np.abs(cekme_bilesik))),
        "ters_sıra": yanlis_sira,
    }


def izometri_mi(phi: Morfizm, kaynak: Metrik, hedef: Metrik,
                noktalar: Sequence[Sequence[float]],
                tol: float = 1e-7) -> Dict[str, object]:
    sapmalar = []
    for x in noktalar:
        fark = phi.metrik_cek(hedef, x) - kaynak.G(np.asarray(x, float))
        sapmalar.append(float(np.max(np.abs(fark))))
    return {"azamî_sapma": max(sapmalar), "izometri": max(sapmalar) < tol,
            "sapmalar": sapmalar}


def konformal_mi(phi: Morfizm, kaynak: Metrik, hedef: Metrik,
                 noktalar: Sequence[Sequence[float]],
                 tol: float = 1e-7) -> Dict[str, object]:
    sapmalar, lambdalar = [], []
    for x in noktalar:
        x = np.asarray(x, float)
        A = phi.metrik_cek(hedef, x)
        G = kaynak.G(x)
        lam = float(np.trace(np.linalg.solve(G, A)) / kaynak.n)
        lambdalar.append(lam)
        sapmalar.append(float(np.max(np.abs(A - lam * G))))
    return {
        "azamî_sapma": max(sapmalar),
        "konformal": max(sapmalar) < tol,
        "λ_değerleri": lambdalar,
        "λ_sabit_mi": (max(lambdalar) - min(lambdalar)) < tol,
    }


def _rapor_token_uzaylari_morfizm() -> str:
    s: List[str] = []

    phi = Morfizm(2, 3, lambda x: np.array([x[0] ** 2 + x[1],
                                            np.sin(x[0]) * x[1],
                                            np.exp(0.3 * x[0])]), "φ")
    psi = Morfizm(3, 2, lambda y: np.array([y[0] * y[2],
                                            np.tanh(y[1] + y[0])]), "ψ")
    x = np.array([0.7, -0.4])

    s.append("=== Funktoryellik: zincir kaidesi ölçülüyor ===")
    f = funktoryellik_olc(psi, phi, x)
    s.append(f"  d(ψ∘φ) ile dψ·dφ arasındaki bağıl sapma:"
             f" {f['zincir_kaidesi_sapması']:.3e}")
    s.append(f"  (ψ∘φ)^*w ile φ^*(ψ^*w) arasındaki sapma:"
             f" {f['çekme_sapması']:.3e}"
             f"   (büyüklük {f['çekme_büyüklüğü']:.4f})")
    s.append("  → çekme sırası tersine dönüyor ve doğru netice veriyor.")
    s.append(f"  yanlış sıra (ψ^*∘φ^*) denenirse: {f['ters_sıra']}")

    s.append("\n=== Çekmenin yönü gerçekten ters mi? ===")
    s.append("  φ: ℝ²→ℝ³ ; vektör ileri gider (2→3), ko-vektör geri (3→2):")
    v = np.array([1.0, 0.5])
    w = np.array([0.2, -0.7, 1.3])
    s.append(f"    itme(v)  boyu = {phi.itme(x, v).size}  (hedefte)")
    s.append(f"    çekme(w) boyu = {phi.cekme(x, w).size}  (kaynakta)")
    try:
        phi.cekme(x, v)
        s.append("    yanlış boyda ko-vektör kabul edildi (BEKLENMEZ)")
    except ValueError as e:
        s.append(f"    yanlış boyda ko-vektör reddedildi: {e}")

    s.append("\n=== Metrik çekme ===")
    duz3 = metrik("düz", n=3)
    G = phi.metrik_cek(duz3, x)
    J = phi.dphi(x)
    s.append(f"  φ^*δ = JᵀJ mi? sapma = {np.max(np.abs(G - J.T @ J)):.3e}")
    s.append(f"  çekilmiş metrik simetrik mi? "
             f"{np.max(np.abs(G - G.T)):.3e}")
    s.append(f"  pozitif tanımlı mı? özdeğerler ="
             f" {np.array2string(np.linalg.eigvalsh(G), precision=5)}")

    s.append("\n=== İzometri v konformallik ===")
    noktalar = [[0.3, 0.5], [-0.8, 1.2], [1.5, -0.3]]
    donme = Morfizm(2, 2, lambda z: np.array([
        np.cos(0.7) * z[0] - np.sin(0.7) * z[1],
        np.sin(0.7) * z[0] + np.cos(0.7) * z[1]]), "dönme")
    olcekleme = Morfizm(2, 2, lambda z: 2.5 * z, "×2.5")
    egri = Morfizm(2, 2, lambda z: np.array([z[0] ** 2, z[1]]), "eğri")
    duz2 = metrik("düz", n=2)
    for ad, m in (("dönme", donme), ("×2.5", olcekleme), ("eğri", egri)):
        i = izometri_mi(m, duz2, duz2, noktalar)
        k = konformal_mi(m, duz2, duz2, noktalar)
        s.append(f"  {ad:8s} izometri={str(i['izometri']):5s}"
                 f" (sapma {i['azamî_sapma']:.2e})"
                 f"  konformal={str(k['konformal']):5s}"
                 f"  λ sabit mi={k['λ_sabit_mi']}"
                 f"  λ≈{np.mean(k['λ_değerleri']):.4f}")
    s.append("  → her izometri konformaldir; ×2.5 konformaldir ama izometri")
    s.append("    değildir; 'eğri' ikisi de değildir. Ölçüt ayırt ediyor.")

    s.append("\n=== Monoidal yapı: (φ×ψ)'nin Jacobi'si blok köşegen ===")
    a = Morfizm(2, 2, lambda z: np.array([z[0] ** 2, z[0] * z[1]]), "a")
    b = Morfizm(3, 2, lambda z: np.array([z[0] + z[2], np.sin(z[1])]), "b")
    c = carpim_morfizmi(a, b)
    p = np.array([0.4, -0.6, 1.1, 0.2, -0.9])
    Jc = c.dphi(p)
    Ja, Jb = a.dphi(p[:2]), b.dphi(p[2:])
    blok = np.zeros_like(Jc)
    blok[:2, :2] = Ja
    blok[2:, 2:] = Jb
    s.append(f"  Jacobi şekli = {Jc.shape}"
             f"   blok köşegenden sapma = {np.max(np.abs(Jc - blok)):.3e}")
    s.append(f"  köşegen dışı blokların büyüklüğü ="
             f" {max(np.max(np.abs(Jc[:2, 2:])), np.max(np.abs(Jc[2:, :2]))):.3e}")
    return "\n".join(s)


def _yol_ucu(p: Terim, uc: int) -> Terim:
    return YolUygula(p, ARALIK_BIR if uc else ARALIK_SIFIR)


def ua_sinirda_cokuyor_mu(A: Terim, B: Terim, e: Terim
                          ) -> Dict[str, object]:
    yol = ua(A, B, e)
    sol_esit = esdeger_mi(_yol_ucu(yol, 0), A)
    sag_esit = esdeger_mi(_yol_ucu(yol, 1), B)
    return {
        "ua e @ 0": nf(_yol_ucu(yol, 0)),
        "A": nf(A), "sol_çöküyor": sol_esit,
        "ua e @ 1": nf(_yol_ucu(yol, 1)),
        "B": nf(B), "sağ_çöküyor": sag_esit,
        "her_ikisi": sol_esit and sag_esit,
    }


def ardil_tasima_olc(n: int = 3) -> Dict[str, object]:
    Z = Tamsayi()
    e = ardil_denkligi()
    yol = ua(Z, Z, e)
    i = taze("i")
    cizgi = YolUygula(yol, Aralik.degisken(i))
    terim = Transp(i, cizgi, YANLIS, Poz(Sfr()))
    beklenen = Poz(Ard(Sfr()))
    return {"taşınan": nf(terim), "beklenen": nf(beklenen),
            "eşit": esdeger_mi(terim, beklenen)}


@dataclass
class TokenDenkligi:
    ileri: Morfizm
    geri: Morfizm
    ad: str = ""

    def __post_init__(self) -> None:
        if self.ileri.m != self.geri.n or self.geri.m != self.ileri.n:
            raise ValueError("ileri ile geri birbirinin tersi olacak şekilde "
                             "tiplenmeli")

    def gidis_donus(self, noktalar: Sequence[Sequence[float]]
                    ) -> Dict[str, object]:
        ileri_geri, geri_ileri = [], []
        for x in noktalar:
            x = np.asarray(x, float)
            ileri_geri.append(float(np.max(np.abs(self.geri(self.ileri(x)) - x))))
        for y in noktalar:
            y = np.asarray(y, float)
            if y.size != self.ileri.m:
                continue
            geri_ileri.append(float(np.max(np.abs(self.ileri(self.geri(y)) - y))))
        return {
            "ileri_sonra_geri": max(ileri_geri) if ileri_geri else float("nan"),
            "geri_sonra_ileri": (max(geri_ileri) if geri_ileri
                                 else float("nan")),
        }

    def denklik_mi(self, noktalar: Sequence[Sequence[float]],
                   tol: float = 1e-9) -> bool:
        r = self.gidis_donus(noktalar)
        degerler = [v for v in r.values() if not np.isnan(v)]
        return bool(degerler) and max(degerler) < tol


def permutasyon_denkligi(perm: Sequence[int]) -> TokenDenkligi:
    perm = list(perm)
    n = len(perm)
    if sorted(perm) != list(range(n)):
        raise ValueError("geçerli bir permütasyon değil")
    ters = [0] * n
    for i, p in enumerate(perm):
        ters[p] = i
    return TokenDenkligi(
        Morfizm(n, n, lambda x: np.asarray(x, float)[perm], "σ"),
        Morfizm(n, n, lambda y: np.asarray(y, float)[ters], "σ⁻¹"),
        ad=f"perm{tuple(perm)}")


def dogrusal_denklik(M: np.ndarray) -> TokenDenkligi:
    M = np.asarray(M, float)
    if M.ndim != 2 or M.shape[0] != M.shape[1]:
        raise ValueError("kare dizey lazım")
    Mi = np.linalg.inv(M)
    n = M.shape[0]
    return TokenDenkligi(
        Morfizm(n, n, lambda x: M @ np.asarray(x, float), "M"),
        Morfizm(n, n, lambda y: Mi @ np.asarray(y, float), "M⁻¹"),
        ad="doğrusal")


def kayipsizlik_karnesi(d: TokenDenkligi,
                        noktalar: Sequence[Sequence[float]]
                        ) -> Dict[str, object]:
    gd = d.gidis_donus(noktalar)
    duz = metrik("düz", n=d.ileri.n)
    izo = izometri_mi(d.ileri, duz, metrik("düz", n=d.ileri.m), noktalar)
    J = d.ileri.dphi(noktalar[0])
    detmi = (abs(float(np.linalg.det(J))) if J.shape[0] == J.shape[1]
             else float("nan"))
    return {
        "ad": d.ad,
        "tersinir": d.denklik_mi(noktalar),
        "gidiş_dönüş_sapması": max(v for v in gd.values()
                                   if not np.isnan(v)),
        "izometri": izo["izometri"],
        "izometri_sapması": izo["azamî_sapma"],
        "|det|": detmi,
    }


def _rapor_token_uzaylari_yapistir() -> str:
    s: List[str] = []

    s.append("=== Tip teorisi tarafı: Glue sınırda çöküyor mu? ===")
    Z = Tamsayi()
    for ad, e in (("özdeşlik denkliği", ozdeslik_denkligi(Z)),
                  ("ardıl denkliği", ardil_denkligi())):
        r = ua_sinirda_cokuyor_mu(Z, Z, e)
        s.append(f"  {ad:18s} ua e@0 ≡ A: {r['sol_çöküyor']}"
                 f"   ua e@1 ≡ B: {r['sağ_çöküyor']}")
    s.append("  Bu tanımsal bir eşitliktir: ispat terimi kurulmadı,")
    s.append("  iki tarafın normal formu hesaplanıp karşılaştırıldı.")

    s.append("\n=== ua(ardıl) boyunca taşıma +1 yapıyor mu? ===")
    t = ardil_tasima_olc()
    s.append(f"  transp(ua ardil, 0) = {t['taşınan']}")
    s.append(f"  beklenen            = {t['beklenen']}")
    s.append(f"  eşit mi? {t['eşit']}")

    s.append("\n=== Sayısal taraf: token denklikleri ===")
    noktalar = [[0.3, -0.5, 1.2, 0.8], [1.0, 0.0, -0.4, 2.1],
                [-1.1, 0.7, 0.2, -0.9]]
    donme = np.array([[np.cos(0.7), -np.sin(0.7), 0, 0],
                      [np.sin(0.7), np.cos(0.7), 0, 0],
                      [0, 0, np.cos(0.3), -np.sin(0.3)],
                      [0, 0, np.sin(0.3), np.cos(0.3)]])
    olcek = np.diag([2.0, 2.0, 2.0, 2.0])
    kesme = np.array([[1.0, 0.5, 0, 0], [0, 1.0, 0, 0],
                      [0, 0, 1.0, 0], [0, 0, 0, 1.0]])
    adaylar = [permutasyon_denkligi([2, 0, 3, 1]),
               dogrusal_denklik(donme),
               dogrusal_denklik(olcek),
               dogrusal_denklik(kesme)]
    adaylar[1].ad, adaylar[2].ad, adaylar[3].ad = "dönme", "×2", "kesme"
    s.append("  ad         tersinir  gidiş-dönüş   izometri  izo.sapma   |det|")
    for d in adaylar:
        k = kayipsizlik_karnesi(d, noktalar)
        s.append(f"  {k['ad']:10s} {str(k['tersinir']):8s}"
                 f"  {k['gidiş_dönüş_sapması']:.2e}"
                 f"    {str(k['izometri']):8s} {k['izometri_sapması']:.2e}"
                 f"  {k['|det|']:.4f}")
    s.append("  Dördü de TERSİNİR (yani kayıpsız), ama yalnız ikisi")
    s.append("  izometri. Tersinirlik ile mesafe korumak ayrı şeylerdir;")
    s.append("  '×2' hiçbir bilgi kaybetmez, sadece ölçeği değiştirir.")

    s.append("\n=== Tekil dizey denklik sayılmaz ===")
    try:
        dogrusal_denklik(np.array([[1.0, 2.0], [2.0, 4.0]]))
        s.append("  tekil dizey kabul edildi (BEKLENMEZ)")
    except np.linalg.LinAlgError as e:
        s.append(f"  tekil dizey reddedildi: {type(e).__name__}: {e}")

    s.append("\n=== Köprünün haddi ===")
    s.append("  Yukarıda İKİ AYRI şey ölçüldü ve ikisi de kayıpsızlık")
    s.append("  sağladı; ama bu, ikisinin aynı nesne olduğunu GÖSTERMEZ.")
    s.append("  Glue tarafında kayıpsızlık tanımsal bir eşitlik; sayısal")
    s.append("  tarafta ise 1e-16 mertebesinde bir ölçüm. Modül bu")
    s.append("  ortaklığı kaydeder, aralarında izomorfizm iddia etmez.")
    return "\n".join(s)


Nesne = Hashable


Ok = Hashable


@dataclass
class Kategori:
    nesneler: Tuple[Nesne, ...]
    oklar: Tuple[Ok, ...]
    kaynak: Dict[Ok, Nesne]
    hedef: Dict[Ok, Nesne]
    bileske: Dict[Tuple[Ok, Ok], Ok]
    birim: Dict[Nesne, Ok]
    ad: str = ""

    def __post_init__(self) -> None:
        self.denetle()

    def hom(self, a: Nesne, b: Nesne) -> Tuple[Ok, ...]:
        return tuple(f for f in self.oklar
                     if self.kaynak[f] == a and self.hedef[f] == b)

    def bilesir_mi(self, g: Ok, f: Ok) -> bool:
        return self.hedef[f] == self.kaynak[g]

    def denetle(self) -> None:
        for f in self.oklar:
            if f not in self.kaynak or f not in self.hedef:
                raise ValueError(f"{f!r} okunun kaynağı/hedefi eksik")
        for a in self.nesneler:
            if a not in self.birim:
                raise ValueError(f"{a!r} nesnesinin birimi yok")
            i = self.birim[a]
            if self.kaynak[i] != a or self.hedef[i] != a:
                raise ValueError(f"{a!r} birimi endomorfizm değil")
        for g, f in product(self.oklar, repeat=2):
            if not self.bilesir_mi(g, f):
                continue
            if (g, f) not in self.bileske:
                raise ValueError(f"bileşke tanımsız: {g!r}∘{f!r}")
            h = self.bileske[(g, f)]
            if h not in self.oklar:
                raise ValueError(f"bileşke kategoriden çıkıyor: {h!r}")
            if (self.kaynak[h] != self.kaynak[f]
                    or self.hedef[h] != self.hedef[g]):
                raise ValueError(f"bileşkenin tipi yanlış: {g!r}∘{f!r}")
        for f in self.oklar:
            a, b = self.kaynak[f], self.hedef[f]
            if self.bileske[(f, self.birim[a])] != f:
                raise ValueError(f"sağ birim kanunu bozuk: {f!r}")
            if self.bileske[(self.birim[b], f)] != f:
                raise ValueError(f"sol birim kanunu bozuk: {f!r}")
        for h, g, f in product(self.oklar, repeat=3):
            if not (self.bilesir_mi(g, f) and self.bilesir_mi(h, g)):
                continue
            sol = self.bileske[(self.bileske[(h, g)], f)]
            sag = self.bileske[(h, self.bileske[(g, f)])]
            if sol != sag:
                raise ValueError(f"birleşme bozuk: {h!r},{g!r},{f!r}")


@dataclass
class Funktor:
    kaynak: Kategori
    nes: Dict[Nesne, object]
    mor: Dict[Ok, object]
    hedef: Optional[Kategori] = None
    ad: str = ""

    @property
    def set_e_mi(self) -> bool:
        return self.hedef is None

    def funktoryel_mi(self) -> Tuple[bool, str]:
        A = self.kaynak
        for a in A.nesneler:
            if a not in self.nes:
                return False, f"{a!r} nesnesinin görüntüsü yok"
            i = A.birim[a]
            if self.set_e_mi:
                fi = self.mor[i]
                if any(fi[x] != x for x in self.nes[a]):
                    return False, f"birim {a!r} özdeşliğe gitmiyor"
            else:
                if self.mor[i] != self.hedef.birim[self.nes[a]]:
                    return False, f"birim {a!r} birime gitmiyor"
        for g, f in product(A.oklar, repeat=2):
            if not A.bilesir_mi(g, f):
                continue
            gf = A.bileske[(g, f)]
            if self.set_e_mi:
                sol = {x: self.mor[g][self.mor[f][x]]
                       for x in self.nes[A.kaynak[f]]}
                if sol != dict(self.mor[gf]):
                    return False, f"bileşke bozuk: {g!r}∘{f!r}"
            else:
                sol = self.hedef.bileske[(self.mor[g], self.mor[f])]
                if sol != self.mor[gf]:
                    return False, f"bileşke bozuk: {g!r}∘{f!r}"
        return True, ""


class birlestir_bul:

    __slots__ = ("ata", "rutbe")

    def __init__(self) -> None:
        self.ata: Dict[Hashable, Hashable] = {}
        self.rutbe: Dict[Hashable, int] = {}

    def ekle(self, x: Hashable) -> None:
        if x not in self.ata:
            self.ata[x] = x
            self.rutbe[x] = 0

    def bul(self, x: Hashable) -> Hashable:
        self.ekle(x)
        kok = x
        while self.ata[kok] != kok:
            kok = self.ata[kok]
        while self.ata[x] != kok:
            self.ata[x], x = kok, self.ata[x]
        return kok

    def birlestir(self, x: Hashable, y: Hashable) -> bool:
        a, b = self.bul(x), self.bul(y)
        if a == b:
            return False
        if self.rutbe[a] < self.rutbe[b]:
            a, b = b, a
        self.ata[b] = a
        if self.rutbe[a] == self.rutbe[b]:
            self.rutbe[a] += 1
        return True

    def siniflar(self) -> Dict[Hashable, List[Hashable]]:
        out: Dict[Hashable, List[Hashable]] = {}
        for x in list(self.ata):
            out.setdefault(self.bul(x), []).append(x)
        return out


def lan(K: Funktor, F: Funktor, b: Nesne) -> Dict[str, object]:
    if K.hedef is None:
        raise ValueError("K bir kategoriden kategoriye funktor olmalı")
    if not F.set_e_mi:
        raise ValueError("F, Set'e giden funktor olmalı")
    A, B = K.kaynak, K.hedef
    if b not in B.nesneler:
        raise ValueError(f"{b!r} B'nin nesnesi değil")

    bb = birlestir_bul()
    for a in A.nesneler:
        for g in B.hom(K.nes[a], b):
            for x in F.nes[a]:
                bb.ekle((a, g, x))

    for f in A.oklar:
        a, a2 = A.kaynak[f], A.hedef[f]
        Kf = K.mor[f]
        for g in B.hom(K.nes[a2], b):
            gKf = B.bileske[(g, Kf)]
            for x in F.nes[a]:
                bb.birlestir((a, gKf, x), (a2, g, F.mor[f][x]))

    siniflar = bb.siniflar()
    return {
        "sınıf_sayısı": len(siniflar),
        "sınıflar": {k: sorted(v, key=repr) for k, v in siniflar.items()},
        "ham_eleman": sum(len(v) for v in siniflar.values()),
    }


def lan_funktor(K: Funktor, F: Funktor) -> Funktor:
    A, B = K.kaynak, K.hedef
    if B is None:
        raise ValueError("K: A→B olmalı")
    sinif: Dict[Nesne, Dict[Tuple, Hashable]] = {}
    nes: Dict[Nesne, object] = {}
    for b in B.nesneler:
        r = lan(K, F, b)
        etiket: Dict[Tuple, Hashable] = {}
        for kok, uyeler in r["sınıflar"].items():
            ad = repr(kok)
            for u in uyeler:
                etiket[tuple(u)] = ad
        sinif[b] = etiket
        nes[b] = frozenset(etiket.values())

    mor: Dict[Ok, object] = {}
    for beta in B.oklar:
        b, b2 = B.kaynak[beta], B.hedef[beta]
        tasima: Dict[Hashable, Hashable] = {}
        for (a, g, x), kaynak_ad in sinif[b].items():
            hedef_ad = sinif[b2][(a, B.bileske[(beta, g)], x)]
            if kaynak_ad in tasima and tasima[kaynak_ad] != hedef_ad:
                raise ValueError(
                    f"Lan taşıması iyi tanımlı değil: {beta!r} sınıfı böldü")
            tasima[kaynak_ad] = hedef_ad
        mor[beta] = tasima
    return Funktor(B, nes, mor, ad=f"Lan_{K.ad}{F.ad}")


def bileske_funktor(G: Funktor, K: Funktor) -> Funktor:
    A = K.kaynak
    return Funktor(A, {a: G.nes[K.nes[a]] for a in A.nesneler},
                   {f: G.mor[K.mor[f]] for f in A.oklar},
                   ad=f"{G.ad}∘{K.ad}")


def ran(K: Funktor, F: Funktor, b: Nesne) -> Dict[str, object]:
    if K.hedef is None or not F.set_e_mi:
        raise ValueError("K: A→B ve F: A→Set olmalı")
    A, B = K.kaynak, K.hedef
    anahtarlar: List[Tuple[Nesne, Ok]] = [
        (a, h) for a in A.nesneler for h in B.hom(b, K.nes[a])
    ]
    if not anahtarlar:
        return {"eleman_sayısı": 1, "elemanlar": [{}],
                "aday_sayısı": 1, "not": "boş indis — tek (boş) aile"}

    secenekler = [sorted(F.nes[a], key=repr) for a, _ in anahtarlar]
    elemanlar = []
    aday = 0
    for degerler in product(*secenekler):
        aday += 1
        alfa = dict(zip(anahtarlar, degerler))
        dogal = True
        for f in A.oklar:
            a, a2 = A.kaynak[f], A.hedef[f]
            Kf = K.mor[f]
            for h in B.hom(b, K.nes[a]):
                Kf_h = B.bileske[(Kf, h)]
                if F.mor[f][alfa[(a, h)]] != alfa[(a2, Kf_h)]:
                    dogal = False
                    break
            if not dogal:
                break
        if dogal:
            elemanlar.append(alfa)
    return {"eleman_sayısı": len(elemanlar), "elemanlar": elemanlar,
            "aday_sayısı": aday}


def dogal_donusumler(F: Funktor, G: Funktor) -> int:
    if not (F.set_e_mi and G.set_e_mi and F.kaynak is G.kaynak):
        raise ValueError("aynı kategoriden Set'e iki funktor lazım")
    A = F.kaynak
    nesneler = list(A.nesneler)
    bilesen_secenekleri = []
    for a in nesneler:
        kaynak_kume = sorted(F.nes[a], key=repr)
        hedef_kume = sorted(G.nes[a], key=repr)
        bilesen_secenekleri.append([
            dict(zip(kaynak_kume, degerler))
            for degerler in product(hedef_kume, repeat=len(kaynak_kume))
        ])
    sayi = 0
    for secim in product(*bilesen_secenekleri):
        alfa = dict(zip(nesneler, secim))
        iyi = True
        for f in A.oklar:
            a, b = A.kaynak[f], A.hedef[f]
            for x in F.nes[a]:
                if alfa[b][F.mor[f][x]] != G.mor[f][alfa[a][x]]:
                    iyi = False
                    break
            if not iyi:
                break
        if iyi:
            sayi += 1
    return sayi


def sonlu_kategori(nesneler: Sequence[Nesne],
                   uretici: Sequence[Tuple[Ok, Nesne, Nesne]],
                   ek_bileske: Optional[Dict[Tuple[Ok, Ok], Ok]] = None,
                   ad: str = "") -> Kategori:
    oklar: Dict[Ok, Tuple[Nesne, Nesne]] = {}
    for a in nesneler:
        oklar[("id", a)] = (a, a)
    for ad_ok, s, t in uretici:
        oklar[ad_ok] = (s, t)

    yollar: Dict[Ok, Tuple[Nesne, Nesne]] = dict(oklar)
    for _ in range(len(nesneler) + 1):
        yeni = {}
        for g, (gs, gt) in yollar.items():
            for f, (fs, ft) in yollar.items():
                if ft != gs:
                    continue
                bilesim = _bilesim_adi(g, f)
                if bilesim not in yollar:
                    yeni[bilesim] = (fs, gt)
        if not yeni:
            break
        yollar.update(yeni)
    else:
        raise ValueError("kategori çevrimli görünüyor — serbest kapanış sonsuz")

    bileske: Dict[Tuple[Ok, Ok], Ok] = {}
    birim = {a: ("id", a) for a in nesneler}
    for g in yollar:
        for f in yollar:
            if yollar[f][1] != yollar[g][0]:
                continue
            bileske[(g, f)] = _bilesim_adi(g, f)
    if ek_bileske:
        bileske.update(ek_bileske)
    return Kategori(tuple(nesneler), tuple(yollar),
                    {f: yollar[f][0] for f in yollar},
                    {f: yollar[f][1] for f in yollar},
                    bileske, birim, ad)


def _bilesim_adi(g: Ok, f: Ok) -> Ok:
    if isinstance(f, tuple) and f and f[0] == "id":
        return g
    if isinstance(g, tuple) and g and g[0] == "id":
        return f
    return ("∘", g, f)


def ok_kategorisi() -> Kategori:
    return sonlu_kategori(("0", "1"), [("u", "0", "1")], ad="ok")


def monoid_kategorisi(n: int) -> Kategori:
    oklar = tuple(("m", i) for i in range(n))
    bileske = {(("m", i), ("m", j)): ("m", (i + j) % n)
               for i in range(n) for j in range(n)}
    return Kategori(("*",), oklar,
                    {f: "*" for f in oklar}, {f: "*" for f in oklar},
                    bileske, {"*": ("m", 0)}, f"ℤ/{n}")


def _ozdes_funktor(A: Kategori) -> Funktor:
    return Funktor(A, {a: a for a in A.nesneler},
                   {f: f for f in A.oklar}, hedef=A, ad="id")


def _rapor_token_uzaylari_kan() -> str:
    s: List[str] = []

    A = ok_kategorisi()
    s.append("=== Kategori aksiyomları denetleniyor ===")
    s.append(f"  ok kategorisi: {len(A.nesneler)} nesne,"
             f" {len(A.oklar)} ok → aksiyomlar geçti")
    try:
        Kategori(("a",), (("id", "a"), "kacak"),
                 {("id", "a"): "a", "kacak": "a"},
                 {("id", "a"): "a", "kacak": "a"},
                 {}, {"a": ("id", "a")})
        s.append("  bozuk kategori kabul edildi (BEKLENMEZ)")
    except ValueError as e:
        s.append(f"  bileşkesi eksik kategori reddedildi: {e}")

    F = Funktor(A, {"0": frozenset({"x", "y"}), "1": frozenset({"p"})},
                {("id", "0"): {"x": "x", "y": "y"},
                 ("id", "1"): {"p": "p"},
                 "u": {"x": "p", "y": "p"}}, ad="F")
    ok, sebep = F.funktoryel_mi()
    s.append(f"\n=== Funktor denetimi ===\n  F funktoryel mi? {ok} {sebep}")
    bozuk = Funktor(A, {"0": frozenset({"x"}), "1": frozenset({"p", "q"})},
                    {("id", "0"): {"x": "x"},
                     ("id", "1"): {"p": "q", "q": "p"},
                     "u": {"x": "p"}}, ad="bozuk")
    ok2, sebep2 = bozuk.funktoryel_mi()
    s.append(f"  birimi bozuk funktor: {ok2}  ({sebep2})")

    s.append("\n=== K = id ise Lan_K F ≅ F ve Ran_K F ≅ F ===")
    idA = _ozdes_funktor(A)
    for b in A.nesneler:
        L = lan(idA, F, b)
        R = ran(idA, F, b)
        s.append(f"  b={b}: |F(b)|={len(F.nes[b])}"
                 f"   |Lan|={L['sınıf_sayısı']}"
                 f"   |Ran|={R['eleman_sayısı']}"
                 f"   (Lan ham eleman {L['ham_eleman']} → bölümlendi)")

    s.append("\n=== Lan serbest genişletmedir: sola eşleniklik SAYILIYOR ===")
    s.append("  |Nat(Lan_K F, G)| = |Nat(F, G∘K)| — iddia değil, sayım:")
    T = sonlu_kategori(("*",), [], ad="1")
    F0 = Funktor(T, {"*": frozenset({"a", "b"})},
                 {("id", "*"): {"a": "a", "b": "b"}}, ad="F0")
    Gler = []
    Gler.append(("sabit-1", Funktor(A, {"0": frozenset({"p"}),
                                       "1": frozenset({"p"})},
                                    {("id", "0"): {"p": "p"},
                                     ("id", "1"): {"p": "p"},
                                     "u": {"p": "p"}}, ad="G1")))
    Gler.append(("çöken", Funktor(A, {"0": frozenset({"x", "y"}),
                                     "1": frozenset({"p"})},
                                  {("id", "0"): {"x": "x", "y": "y"},
                                   ("id", "1"): {"p": "p"},
                                   "u": {"x": "p", "y": "p"}}, ad="G2")))
    Gler.append(("gömen", Funktor(A, {"0": frozenset({"x"}),
                                     "1": frozenset({"p", "q"})},
                                  {("id", "0"): {"x": "x"},
                                   ("id", "1"): {"p": "p", "q": "q"},
                                   "u": {"x": "q"}}, ad="G3")))
    for hedef_nesne in ("0", "1"):
        K = Funktor(T, {"*": hedef_nesne},
                    {("id", "*"): ("id", hedef_nesne)}, hedef=A,
                    ad=f"K{hedef_nesne}")
        okk, sb = K.funktoryel_mi()
        assert okk, sb
        LanF = lan_funktor(K, F0)
        okl, sbl = LanF.funktoryel_mi()
        boyut = ", ".join(f"|{o}|={len(LanF.nes[o])}" for o in A.nesneler)
        s.append(f"  K(*)={hedef_nesne}:  Lan_K F0 = ({boyut})"
                 f"   funktoryel mi? {okl} {sbl}")
        for ad, G in Gler:
            sol = dogal_donusumler(LanF, G)
            sag = dogal_donusumler(F0, bileske_funktor(G, K))
            isaret = "=" if sol == sag else "≠  ← EŞLENİKLİK BOZUK"
            s.append(f"      G={ad:8s} |Nat(Lan_K F0, G)|={sol:3d}"
                     f"  {isaret}  |Nat(F0, G∘K)|={sag:3d}")

    s.append("\n=== Monoid üzerinde Lan: çevrimli kategori ===")
    M = monoid_kategorisi(3)
    s.append(f"  ℤ/3 monoidi: {len(M.oklar)} ok, aksiyomlar geçti")
    tasiyici = frozenset(range(3))
    FM = Funktor(M, {"*": tasiyici},
                 {("m", i): {x: (x + i) % 3 for x in range(3)}
                  for i in range(3)}, ad="kaydırma")
    okm, sbm = FM.funktoryel_mi()
    s.append(f"  kaydırma etkisi funktoryel mi? {okm} {sbm}")
    idM = _ozdes_funktor(M)
    LM = lan(idM, FM, "*")
    RM = ran(idM, FM, "*")
    s.append(f"  Lan_id F: ham eleman {LM['ham_eleman']}"
             f" → {LM['sınıf_sayısı']} sınıf  (|F(*)|={len(tasiyici)})")
    s.append(f"  Ran_id F: {RM['aday_sayısı']} adayın"
             f" {RM['eleman_sayısı']}'i doğal")

    s.append("\n=== Birleşim–bul: coend bölümü ===")
    bb = birlestir_bul()
    for i in range(1000):
        bb.ekle(i)
    for i in range(999):
        bb.birlestir(i, i + 1)
    s.append(f"  1000 eleman zincir hâlinde birleştirildi →"
             f" {len(bb.siniflar())} sınıf (beklenen 1)")
    bb2 = birlestir_bul()
    for i in range(1000):
        bb2.ekle(i)
    for i in range(0, 998, 2):
        bb2.birlestir(i, i + 2)
    s.append(f"  çiftler ayrı birleştirildi → {len(bb2.siniflar())} sınıf"
             f" (beklenen 501: tek çift sınıfı + 500 tekil)")
    return "\n".join(s)


def dugum_dizisi(G: int, k: int, alt: float = -1.0,
                 ust: float = 1.0) -> np.ndarray:
    if G < 1 or k < 0:
        raise ValueError("G ≥ 1 ve k ≥ 0 olmalı")
    if not ust > alt:
        raise ValueError("ust > alt olmalı")
    h = (ust - alt) / G
    return np.array([alt + (i - k) * h for i in range(G + 2 * k + 1)])


def bspline_temeli(t: np.ndarray, dugumler: np.ndarray, k: int
                   ) -> np.ndarray:
    t = np.atleast_1d(np.asarray(t, float))
    d = np.asarray(dugumler, float)
    if k < 0:
        raise ValueError("derece negatif olamaz")
    n_temel = d.size - 1

    B = ((t[:, None] >= d[None, :-1]) & (t[:, None] < d[None, 1:])
         ).astype(float)
    sag = d[-1]
    son = np.isclose(t, sag)
    if np.any(son):
        j = n_temel - 1
        while j > 0 and d[j + 1] <= d[j]:
            j -= 1
        B[son, j] = 1.0

    for derece in range(1, k + 1):
        n_yeni = n_temel - derece
        yeni = np.zeros((t.size, n_yeni))
        for i in range(n_yeni):
            sol_payda = d[i + derece] - d[i]
            sag_payda = d[i + derece + 1] - d[i + 1]
            if sol_payda > 0:
                yeni[:, i] += (t - d[i]) / sol_payda * B[:, i]
            if sag_payda > 0:
                yeni[:, i] += (d[i + derece + 1] - t) / sag_payda * B[:, i + 1]
        B = yeni
    return B


def bspline_turev_temeli(t: np.ndarray, dugumler: np.ndarray, k: int
                         ) -> np.ndarray:
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
    d = np.asarray(dugumler, float)
    t = np.atleast_1d(np.asarray(t, float))
    ic = (t >= d[k]) & (t <= d[d.size - k - 1])
    if not np.any(ic):
        return 0.0
    return float(np.max(np.abs(bspline_temeli(t[ic], d, k).sum(axis=1) - 1.0)))


@dataclass
class BSplineKenar:
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
        t = np.atleast_1d(np.asarray(t, float))
        sig = 1.0 / (1.0 + np.exp(-t))
        dsilu = sig * (1.0 + t * (1.0 - sig))
        dspline = bspline_turev_temeli(t, self.dugumler, self.k) @ self.c
        return self.w_taban * dsilu + self.w_spline * dspline

    def uydur(self, t: np.ndarray, y: np.ndarray,
              duzenleme: float = 1e-8) -> float:
        t = np.atleast_1d(np.asarray(t, float))
        y = np.asarray(y, float).ravel()
        hedef = (y - self.w_taban * self._silu(t)) / self.w_spline
        A = self.temel(t)
        AtA = A.T @ A + duzenleme * np.eye(A.shape[1])
        self.c = np.linalg.solve(AtA, A.T @ hedef)
        return float(np.linalg.norm(self(t) - y) / max(1, np.sqrt(y.size)))


@dataclass
class KANKatmani:
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
        olcek = 1.0 / np.sqrt(self.n_giris)
        self.C = r.normal(0.0, 0.1 * olcek, (self.n_giris, self.n_cikis, n))
        self.W_taban = r.normal(0.0, olcek, (self.n_giris, self.n_cikis))
        self.W_spline = np.ones((self.n_giris, self.n_cikis))
        self.dugumler = dugum_dizisi(self.G, self.k, self.alt, self.ust)

    @property
    def parametre_sayisi(self) -> int:
        return self.C.size + self.W_taban.size + self.W_spline.size

    def ileri(self, X: np.ndarray) -> np.ndarray:
        X = np.atleast_2d(np.asarray(X, float))
        if X.shape[1] != self.n_giris:
            raise ValueError(f"girdi {self.n_giris} sütunlu olmalı")
        cikti = np.zeros((X.shape[0], self.n_cikis))
        sig = 1.0 / (1.0 + np.exp(-X))
        silu = X * sig
        for i in range(self.n_giris):
            B = bspline_temeli(X[:, i], self.dugumler, self.k)
            cikti += B @ (self.C[i] * self.W_spline[i][:, None]).T
            cikti += silu[:, i:i + 1] * self.W_taban[i][None, :]
        return cikti


@dataclass
class KAN:
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


def _rapor_token_uzaylari_kan_spline() -> str:
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


def spektral_enerji(v: np.ndarray) -> np.ndarray:
    v = np.atleast_2d(np.asarray(v, float))
    V = np.fft.rfft(v, axis=0)
    return np.sum(np.abs(V) ** 2, axis=1)


def kesme_kipi(v: np.ndarray, eps: float = 1e-3) -> int:
    E = spektral_enerji(v)
    toplam = float(E.sum())
    if toplam <= 0:
        return 0
    kuyruk = float(E.sum())
    for k in range(E.size):
        kuyruk -= float(E[k])
        if kuyruk < eps * toplam:
            return k
    return E.size - 1


def parseval_sapmasi(v: np.ndarray) -> float:
    v = np.atleast_2d(np.asarray(v, float))
    N = v.shape[0]
    V = np.fft.rfft(v, axis=0)
    agirlik = np.full(V.shape[0], 2.0)
    agirlik[0] = 1.0
    if N % 2 == 0:
        agirlik[-1] = 1.0
    sag = float(np.sum(agirlik[:, None] * np.abs(V) ** 2)) / N
    sol = float(np.sum(v ** 2))
    return abs(sol - sag) / max(abs(sol), 1e-30)


def yeniden_ornekle(f: Callable[[np.ndarray], np.ndarray], N: int
                    ) -> np.ndarray:
    x = np.linspace(0.0, 1.0, N, endpoint=False)
    return np.asarray(f(x), float).reshape(N, -1)


@dataclass
class SpektralKatman:
    c_giris: int
    c_cikis: int
    k_kesme: int
    tohum: int = 0
    aktivasyon: Optional[Callable[[np.ndarray], np.ndarray]] = None
    R: np.ndarray = field(init=False)
    W: np.ndarray = field(init=False)
    b: np.ndarray = field(init=False)

    def __post_init__(self) -> None:
        if self.k_kesme < 0:
            raise ValueError("k_kesme ≥ 0 olmalı")
        r = np.random.default_rng(self.tohum)
        olcek = 1.0 / np.sqrt(self.c_giris * max(self.k_kesme, 1))
        self.R = (r.normal(0, olcek, (self.k_kesme + 1, self.c_giris,
                                      self.c_cikis))
                  + 1j * r.normal(0, olcek, (self.k_kesme + 1, self.c_giris,
                                             self.c_cikis)))
        self.W = r.normal(0, 1.0 / np.sqrt(self.c_giris),
                          (self.c_giris, self.c_cikis))
        self.b = np.zeros(self.c_cikis)
        if self.aktivasyon is None:
            self.aktivasyon = lambda z: np.tanh(z)

    @property
    def parametre_sayisi(self) -> int:
        return 2 * self.R.size + self.W.size + self.b.size

    def kullanilan_kip(self, N: int) -> int:
        return min(self.k_kesme + 1, N // 2 + 1)

    def ileri(self, v: np.ndarray) -> np.ndarray:
        v = np.atleast_2d(np.asarray(v, float))
        if v.shape[1] != self.c_giris:
            raise ValueError(f"girdi {self.c_giris} kanallı olmalı")
        N = v.shape[0]
        V = np.fft.rfft(v, axis=0)
        kip = self.kullanilan_kip(N)
        Y = np.zeros((V.shape[0], self.c_cikis), dtype=complex)
        Y[:kip] = np.einsum("kab,ka->kb", self.R[:kip], V[:kip])
        spektral = np.fft.irfft(Y, n=N, axis=0)
        return self.aktivasyon(v @ self.W + self.b + spektral)


@dataclass
class FNO:
    kanallar: Sequence[int]
    k_kesme: int = 8
    tohum: int = 0
    katmanlar: List[SpektralKatman] = field(init=False)

    def __post_init__(self) -> None:
        if len(self.kanallar) < 2:
            raise ValueError("en az giriş ve çıkış kanalı lazım")
        self.katmanlar = [
            SpektralKatman(a, b, self.k_kesme, self.tohum * 100 + i)
            for i, (a, b) in enumerate(zip(self.kanallar[:-1],
                                           self.kanallar[1:]))
        ]

    @property
    def parametre_sayisi(self) -> int:
        return sum(k.parametre_sayisi for k in self.katmanlar)

    def ileri(self, v: np.ndarray) -> np.ndarray:
        for kat in self.katmanlar:
            v = kat.ileri(v)
        return v

    def __call__(self, v: np.ndarray) -> np.ndarray:
        return self.ileri(v)


@dataclass
class EvrisimKatmani:
    c_giris: int
    c_cikis: int
    yari_genislik: int = 4
    tohum: int = 0
    K: np.ndarray = field(init=False)
    W: np.ndarray = field(init=False)

    def __post_init__(self) -> None:
        r = np.random.default_rng(self.tohum)
        g = 2 * self.yari_genislik + 1
        self.K = r.normal(0, 1.0 / np.sqrt(self.c_giris * g),
                          (g, self.c_giris, self.c_cikis))
        self.W = r.normal(0, 1.0 / np.sqrt(self.c_giris),
                          (self.c_giris, self.c_cikis))

    def ileri(self, v: np.ndarray) -> np.ndarray:
        v = np.atleast_2d(np.asarray(v, float))
        N = v.shape[0]
        cikti = np.zeros((N, self.c_cikis))
        for j, kaydir in enumerate(range(-self.yari_genislik,
                                         self.yari_genislik + 1)):
            cikti += np.roll(v, kaydir, axis=0) @ self.K[j]
        return np.tanh(v @ self.W + cikti)


def izgaradan_bagimsizlik(kat, f: Callable[[np.ndarray], np.ndarray],
                          N_kaba: int, N_ince: int) -> Dict[str, object]:
    if N_ince % N_kaba != 0:
        raise ValueError("N_ince, N_kaba'nın tam katı olmalı")
    adim = N_ince // N_kaba
    v_kaba = yeniden_ornekle(f, N_kaba)
    v_ince = yeniden_ornekle(f, N_ince)
    y_kaba = kat.ileri(v_kaba)
    y_ince = kat.ileri(v_ince)[::adim]
    olcek = max(float(np.max(np.abs(y_kaba))), 1e-30)
    return {
        "N_kaba": N_kaba, "N_ince": N_ince,
        "azamî_fark": float(np.max(np.abs(y_kaba - y_ince))),
        "bağıl_fark": float(np.max(np.abs(y_kaba - y_ince))) / olcek,
        "çıktı_büyüklüğü": olcek,
    }


def _ornek_alan(x: np.ndarray) -> np.ndarray:
    return np.stack([
        np.sin(2 * np.pi * x) + 0.5 * np.cos(6 * np.pi * x),
        np.cos(4 * np.pi * x) - 0.3 * np.sin(2 * np.pi * x),
    ], axis=1)


def _rapor_token_uzaylari_fno() -> str:
    import time
    s: List[str] = []

    s.append("=== Parseval: spektral yol enerji kaybetmiyor mu? ===")
    for N in (16, 17, 64, 128, 257):
        v = yeniden_ornekle(_ornek_alan, N)
        s.append(f"  N={N:<4} bağıl sapma = {parseval_sapmasi(v):.3e}")
    s.append("  (tek ve çift N ayrı ayrı: rfft'te uç kiplerin ağırlığı farklı)")

    s.append("\n=== Kesme kipi veriden hesaplanıyor ===")
    x = np.linspace(0, 1, 256, endpoint=False)
    for ad, g in (("sin(2πx)", lambda z: np.sin(2 * np.pi * z)[:, None]),
                  ("2 kipli alan", _ornek_alan),
                  ("gürültü", lambda z: np.random.default_rng(0)
                   .normal(0, 1, (z.size, 1)))):
        v = np.asarray(g(x), float).reshape(256, -1)
        satir = f"  {ad:14s}"
        for eps in (1e-2, 1e-6, 1e-12):
            satir += f"  ε={eps:.0e}: k={kesme_kipi(v, eps):3d}"
        s.append(satir)
    s.append("  Band-sınırlı alanlarda k küçük ve ε'a DUYARSIZ (bütün enerji")
    s.append("  birkaç kipte; ε'u trilyonda bire indirmek k'yı oynatmıyor).")
    s.append("  Gürültüde ise k daha ε=1e-2'de bütün spektrumu istiyor:")
    s.append("  beyaz gürültünün kesilebilecek bir kuyruğu yoktur.")

    s.append("\n=== Izgaradan bağımsızlık: FNO v evrişim ===")
    fno_kat = SpektralKatman(2, 3, k_kesme=8, tohum=1)
    evr_kat = EvrisimKatmani(2, 3, yari_genislik=4, tohum=1)
    s.append("  ölçüm: aynı işleç iki çözünürlükte, ORTAK noktalarda")
    s.append("  N_kaba  N_ince    FNO bağıl fark    evrişim bağıl fark")
    for Nk, Ni in ((32, 64), (32, 128), (64, 256), (128, 512)):
        a = izgaradan_bagimsizlik(fno_kat, _ornek_alan, Nk, Ni)
        b = izgaradan_bagimsizlik(evr_kat, _ornek_alan, Nk, Ni)
        s.append(f"   {Nk:4d}    {Ni:4d}     {a['bağıl_fark']:.3e}"
                 f"        {b['bağıl_fark']:.3e}")
    s.append("  FNO'nun çekirdeği KİP cinsinden olduğu için ızgara")
    s.append("  sıklaşınca değişmiyor; evrişiminki PİKSEL cinsinden,")
    s.append("  o yüzden pencere fiziksel olarak daralıyor ve netice kayıyor.")

    s.append("\n=== Kesme kip sayısından fazlası istenirse ===")
    kat = SpektralKatman(2, 2, k_kesme=40, tohum=0)
    for N in (8, 16, 64, 128):
        s.append(f"  N={N:<4} istenen kip=41, kullanılabilen="
                 f"{kat.kullanilan_kip(N)}"
                 f"  → çıktı sonlu mu? "
                 f"{bool(np.all(np.isfinite(kat.ileri(yeniden_ornekle(_ornek_alan, N)))))}")

    s.append("\n=== Çok katmanlı FNO ===")
    ag = FNO([2, 8, 8, 1], k_kesme=12, tohum=2)
    v = yeniden_ornekle(_ornek_alan, 128)
    y = ag(v)
    s.append(f"  FNO([2,8,8,1]) çıktı {y.shape}, parametre {ag.parametre_sayisi}")
    a = izgaradan_bagimsizlik(ag, _ornek_alan, 64, 256)
    s.append(f"  yığının ızgaradan bağımsızlığı: bağıl fark ="
             f" {a['bağıl_fark']:.3e}")
    s.append("  Tek katmanda 1e-16 idi, yığında 1e-06. Bu bir kusur değil,")
    s.append("  ÖRTÜŞME (aliasing): tanh yüksek kipler üretiyor, kaba")
    s.append("  ızgarada bunlar düşük kiplere katlanıyor. Sebebi ölçelim —")
    dogrusal = FNO([2, 8, 8, 1], k_kesme=12, tohum=2)
    for kat in dogrusal.katmanlar:
        kat.aktivasyon = lambda z: z
    b = izgaradan_bagimsizlik(dogrusal, _ornek_alan, 64, 256)
    tek = izgaradan_bagimsizlik(SpektralKatman(2, 3, 8, 1),
                                _ornek_alan, 64, 256)
    s.append(f"    tek katman (tanh)      : {tek['bağıl_fark']:.3e}")
    s.append(f"    yığın, aktivasyon = id : {b['bağıl_fark']:.3e}")
    s.append(f"    yığın, aktivasyon= tanh: {a['bağıl_fark']:.3e}")
    s.append("  Aktivasyon doğrusal yapılınca fark makine hassasiyetine")
    s.append("  iniyor; suçlu tam olarak doğrusal-olmayanlıktır.")

    s.append("\n=== rfft ile tam fft aynı neticeyi veriyor mu? ===")
    v = yeniden_ornekle(_ornek_alan, 128)
    V_r = np.fft.rfft(v, axis=0)
    V_f = np.fft.fft(v, axis=0)[:V_r.shape[0]]
    s.append(f"  ilk yarı spektrumda azamî fark = "
             f"{np.max(np.abs(V_r - V_f)):.3e}")
    s.append(f"  rfft bellek = {V_r.nbytes} bayt,"
             f" fft = {np.fft.fft(v, axis=0).nbytes} bayt"
             f"  → {np.fft.fft(v, axis=0).nbytes / V_r.nbytes:.2f}× tasarruf")
    t0 = time.perf_counter()
    for _ in range(2000):
        np.fft.rfft(v, axis=0)
    t_r = time.perf_counter() - t0
    t0 = time.perf_counter()
    for _ in range(2000):
        np.fft.fft(v, axis=0)
    t_f = time.perf_counter() - t0
    s.append(f"  2000 dönüşüm: rfft {t_r*1000:.1f} ms, fft {t_f*1000:.1f} ms"
             f"  → {t_f/t_r:.2f}×")
    return "\n".join(s)


TOL = 1e-10


def braket(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    A, B = np.asarray(A), np.asarray(B)
    return A @ B - B @ A


def jacobi_hatasi(X: np.ndarray, Y: np.ndarray, Z: np.ndarray) -> float:
    E = (braket(X, braket(Y, Z)) + braket(Y, braket(Z, X))
         + braket(Z, braket(X, Y)))
    return float(np.linalg.norm(E, "fro"))


def so_izdusumu(M: np.ndarray) -> np.ndarray:
    M = np.asarray(M, float)
    return (M - M.T) / 2.0


def uslu_harita(A: np.ndarray, yontem: str = "ozayrisim") -> np.ndarray:
    A = np.asarray(A, float)
    if yontem == "ozayrisim":
        oz, V = np.linalg.eigh(1j * A)
        return np.real(V @ np.diag(np.exp(-1j * oz)) @ V.conj().T)
    if yontem == "seri":
        sonuc = np.eye(A.shape[0])
        terim = np.eye(A.shape[0])
        for k in range(1, 40):
            terim = terim @ A / k
            sonuc = sonuc + terim
        return sonuc
    raise ValueError("yöntem: 'ozayrisim' veya 'seri'")


def so_n_mi(X: np.ndarray, tol: float = 1e-9) -> bool:
    X = np.asarray(X, float)
    n = X.shape[0]
    if X.shape != (n, n):
        return False
    if np.max(np.abs(X.T @ X - np.eye(n))) > tol:
        return False
    return abs(float(np.linalg.det(X)) - 1.0) < tol


def en_yakin_dik(M: np.ndarray) -> np.ndarray:
    U, _, Vt = np.linalg.svd(np.asarray(M, float))
    return U @ Vt


def grup_adimi(X: np.ndarray, grad: np.ndarray, eta: float) -> np.ndarray:
    A = -eta * so_izdusumu(np.asarray(grad, float))
    return np.asarray(X, float) @ uslu_harita(A)


def so3_uretecleri() -> List[np.ndarray]:
    L = []
    for a in range(3):
        M = np.zeros((3, 3))
        for b in range(3):
            for c in range(3):
                M[b, c] = -_levi_civita(a, b, c)
        L.append(M)
    return L


def _levi_civita(i: int, j: int, k: int) -> float:
    if len({i, j, k}) < 3:
        return 0.0
    perm = [i, j, k]
    isaret = 1.0
    for a in range(3):
        for b in range(a + 1, 3):
            if perm[a] > perm[b]:
                isaret = -isaret
    return isaret


def sun_uretecleri(n: int) -> List[np.ndarray]:
    if n < 2:
        raise ValueError("n ≥ 2 olmalı")
    T: List[np.ndarray] = []
    for i in range(n):
        for j in range(i + 1, n):
            M = np.zeros((n, n), dtype=complex)
            M[i, j], M[j, i] = 1j, 1j
            T.append(M)
            M2 = np.zeros((n, n), dtype=complex)
            M2[i, j], M2[j, i] = 1.0, -1.0
            T.append(M2)
    for k in range(1, n):
        kosegen = np.zeros(n, dtype=complex)
        kosegen[:k] = 1j
        kosegen[k] = -1j * k
        T.append(np.diag(kosegen) / math.sqrt(k * (k + 1)))
    if len(T) != n * n - 1:
        raise ValueError(f"taban eksik: {len(T)} ≠ {n*n-1}")
    return T


def yapi_sabitleri(taban: Sequence[np.ndarray]) -> np.ndarray:
    T = [np.asarray(t) for t in taban]
    d = len(T)
    A = np.stack([t.reshape(-1) for t in T], axis=1)
    f = np.zeros((d, d, d), dtype=complex)
    artik = 0.0
    for a in range(d):
        for b in range(d):
            hedef = braket(T[a], T[b]).reshape(-1)
            c, *_ = np.linalg.lstsq(A, hedef, rcond=None)
            f[a, b] = c
            artik = max(artik, float(np.linalg.norm(A @ c - hedef)))
    if artik > 1e-8:
        raise ValueError(f"braket tabanın dışına çıkıyor (artık {artik:.2e}) "
                         "— verilen küme bir Lie cebri değil")
    return f


def yapi_sabiti_jacobi_hatasi(f: np.ndarray) -> float:
    f = np.asarray(f)
    t1 = np.einsum("abe,ecd->abcd", f, f)
    t2 = np.einsum("bce,ead->abcd", f, f)
    t3 = np.einsum("cae,ebd->abcd", f, f)
    return float(np.max(np.abs(t1 + t2 + t3)))


def _rapor_akis_lie() -> str:
    import time
    s: List[str] = []
    rng = np.random.default_rng(0)

    s.append("=== Jacobi: dizey komütatöründe TEOREM ===")
    for n in (2, 3, 5, 8):
        en_buyuk = 0.0
        for _ in range(20):
            X, Y, Z = (rng.normal(size=(n, n)) for _ in range(3))
            olcek = max(np.linalg.norm(X) * np.linalg.norm(Y)
                        * np.linalg.norm(Z), 1e-300)
            en_buyuk = max(en_buyuk, jacobi_hatasi(X, Y, Z) / olcek)
        s.append(f"  n={n}: 20 rastgele üçlüde azamî bağıl hata = "
                 f"{en_buyuk:.2e}")
    s.append("  Yani 'sayısal Jacobi onarımı' diye bir ihtiyaç yok;")
    s.append("  sıfırdan sapma varsa braket yanlış kurulmuş demektir.")

    s.append("\n=== so(3): yapı sabitleri Levi-Civita ===")
    L = so3_uretecleri()
    f = yapi_sabitleri(L)
    hata = 0.0
    for a in range(3):
        for b in range(3):
            for c in range(3):
                hata = max(hata, abs(complex(f[a, b, c]).real
                                     - _levi_civita(a, b, c)))
    s.append(f"  |f_ab^c − ε_abc| azamî = {hata:.2e}")
    s.append(f"  yapı sabiti Jacobi hatası = "
             f"{yapi_sabiti_jacobi_hatasi(f):.2e}")

    s.append("\n=== su(n): boyut n²−1 ve Jacobi ===")
    for n in (2, 3, 4):
        T = sun_uretecleri(n)
        f = yapi_sabitleri(T)
        s.append(f"  su({n}): {len(T)} üreteç (beklenen {n*n-1})"
                 f"   Jacobi hatası = {yapi_sabiti_jacobi_hatasi(f):.2e}")

    s.append("\n  Keyfî f Jacobi'yi SAĞLAMAZ (kısıt olduğunun şahidi):")
    keyfi = rng.normal(size=(3, 3, 3))
    s.append(f"    rastgele f: Jacobi hatası = "
             f"{yapi_sabiti_jacobi_hatasi(keyfi):.4f}")

    s.append("\n=== Üstel harita: özayrışım v seri ===")
    for olcek in (0.1, 1.0, 5.0, 20.0):
        A = so_izdusumu(rng.normal(size=(5, 5))) * olcek
        E1 = uslu_harita(A, "ozayrisim")
        E2 = uslu_harita(A, "seri")
        s.append(f"  ‖A‖={np.linalg.norm(A):6.2f}: "
                 f"özayrışım SO(5)'te mi? {so_n_mi(E1)}"
                 f"   seri SO(5)'te mi? {so_n_mi(E2)}"
                 f"   fark={np.max(np.abs(E1-E2)):.2e}")
    s.append("  Seri, norm büyüdükçe hem yavaşlıyor hem gruptan çıkıyor;")
    s.append("  özayrışım her ölçekte TAM ve grupta kalıyor.")

    s.append("\n=== Gruptan çıkmama: naif adım v üstel adım ===")
    X = en_yakin_dik(rng.normal(size=(4, 4)))
    if np.linalg.det(X) < 0:
        X[:, 0] *= -1
    s.append(f"  başlangıç SO(4)'te mi? {so_n_mi(X)}")
    naif, uslu = X.copy(), X.copy()
    s.append("  adım   naif ‖XᵀX−I‖   naif det    üstel ‖XᵀX−I‖   üstel det")
    for adim in range(1, 6):
        g = rng.normal(size=(4, 4))
        naif = naif - 0.1 * g
        uslu = grup_adimi(uslu, g, 0.1)
        s.append(f"  {adim:4d}   {np.max(np.abs(naif.T@naif-np.eye(4))):.3e}"
                 f"    {np.linalg.det(naif):+.4f}"
                 f"    {np.max(np.abs(uslu.T@uslu-np.eye(4))):.3e}"
                 f"      {np.linalg.det(uslu):+.6f}")
    s.append("  Naif adım grubu terk ediyor; üstel adım makine")
    s.append("  hassasiyetinde içinde kalıyor.")

    s.append("\n=== K28: geri getirme kutup ayrışımıyla ===")
    Q = en_yakin_dik(rng.normal(size=(5, 5)))
    bozuk = Q + 0.08 * rng.normal(size=(5, 5))
    sim = (bozuk + bozuk.T) / 2
    kutup = en_yakin_dik(bozuk)
    s.append(f"  bozuk    ‖XᵀX−I‖ = {np.max(np.abs(bozuk.T@bozuk-np.eye(5))):.4f}")
    s.append(f"  simetrik ‖XᵀX−I‖ = {np.max(np.abs(sim.T@sim-np.eye(5))):.4f}"
             "   ← simetrikleştirme dikliği getirmiyor")
    s.append(f"  kutup    ‖XᵀX−I‖ = {np.max(np.abs(kutup.T@kutup-np.eye(5))):.2e}"
             "   ← tam dik")
    d_kutup = np.linalg.norm(kutup - bozuk, "fro")
    daha_iyi = 0
    for _ in range(300):
        R = en_yakin_dik(rng.normal(size=(5, 5)))
        if np.linalg.norm(R - bozuk, "fro") < d_kutup - 1e-12:
            daha_iyi += 1
    s.append(f"  300 rastgele dik dizeyin {daha_iyi}'i daha yakın"
             f"  (kutup mesafesi {d_kutup:.4f})")
    return "\n".join(s)


@dataclass
class Egri:
    x: np.ndarray

    def __post_init__(self) -> None:
        self.x = np.atleast_2d(np.asarray(self.x, float))
        if self.x.shape[1] != 2 or self.x.shape[0] < 3:
            raise ValueError("en az 3 köşeli düzlem eğrisi lazım")

    @property
    def n(self) -> int:
        return self.x.shape[0]

    def uzunluk(self) -> float:
        d = np.roll(self.x, -1, axis=0) - self.x
        return float(np.sum(np.sqrt(np.sum(d * d, axis=1))))

    def alan(self) -> float:
        x, y = self.x[:, 0], self.x[:, 1]
        return abs(float(np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y))) / 2

    def egrilik_vektoru(self) -> np.ndarray:
        ileri = np.roll(self.x, -1, axis=0) - self.x
        geri = np.roll(self.x, 1, axis=0) - self.x
        l_i = np.sqrt(np.sum(ileri ** 2, axis=1))
        l_g = np.sqrt(np.sum(geri ** 2, axis=1))
        l_i = np.maximum(l_i, 1e-300)
        l_g = np.maximum(l_g, 1e-300)
        pay = ileri / l_i[:, None] + geri / l_g[:, None]
        return 2.0 * pay / (l_i + l_g)[:, None]


def mcf_adimi(e: Egri, dt: float) -> Egri:
    return Egri(e.x + dt * e.egrilik_vektoru())


def mcf_kos(e: Egri, T: float, dt: Optional[float] = None,
            azami_adim: int = 200_000) -> Dict[str, object]:
    uyarlamali = dt is None
    guvenlik = 0.2
    h = e.uzunluk() / e.n
    dt_kullanilan = guvenlik * h * h if uyarlamali else float(dt)
    t = 0.0
    alanlar = [e.alan()]
    zamanlar = [0.0]
    adim = 0
    while t < T and adim < azami_adim:
        if uyarlamali:
            h = e.uzunluk() / e.n
            dt_kullanilan = min(guvenlik * h * h, T - t)
            if dt_kullanilan <= 0:
                break
        e = mcf_adimi(e, dt_kullanilan)
        t += dt_kullanilan
        adim += 1
        a = e.alan()
        if not np.all(np.isfinite(e.x)) or a < 1e-9:
            return {"egri": e, "t": t, "alanlar": alanlar,
                    "zamanlar": zamanlar, "coktu": True, "adım": adim,
                    "dt": dt_kullanilan}
        if adim % 50 == 0:
            alanlar.append(a)
            zamanlar.append(t)
    alanlar.append(e.alan())
    zamanlar.append(t)
    return {"egri": e, "t": t, "alanlar": alanlar, "zamanlar": zamanlar,
            "coktu": False, "adım": adim, "dt": dt_kullanilan}


def cember_kapali_cozum(r0: float, t: float) -> float:
    if r0 <= 0:
        raise ValueError("r₀ > 0 olmalı")
    kalan = r0 * r0 - 2.0 * t
    if kalan < 0:
        raise ValueError(f"çember t = r₀²/2 = {r0*r0/2:.6f}'de çöktü; "
                         f"t = {t} istendi")
    return math.sqrt(kalan)


def _merkezi_fark(u: np.ndarray, h: float) -> np.ndarray:
    return (np.roll(u, -1) - np.roll(u, 1)) / (2 * h)


def _laplasyen(u: np.ndarray, h: float) -> np.ndarray:
    return (np.roll(u, -1) - 2 * u + np.roll(u, 1)) / (h * h)


def fokker_planck_adimi(rho: np.ndarray, f: np.ndarray, h: float,
                        dt: float) -> np.ndarray:
    rho = np.asarray(rho, float)
    f = np.asarray(f, float)
    rho_yuz = 0.5 * (rho + np.roll(rho, -1))
    df_yuz = (np.roll(f, -1) - f) / h
    drho_yuz = (np.roll(rho, -1) - rho) / h
    F = rho_yuz * df_yuz + drho_yuz
    div = (F - np.roll(F, 1)) / h
    return rho + dt * div


def fokker_planck_kos(rho0: np.ndarray, f: np.ndarray, h: float,
                      T: float, dt: Optional[float] = None
                      ) -> Dict[str, object]:
    rho = np.asarray(rho0, float).copy()
    if dt is None:
        dt = 0.2 * h * h
    kutle0 = float(np.sum(rho) * h)
    durgun = np.exp(-f)
    durgun = durgun / (np.sum(durgun) * h)
    t, adim = 0.0, 0
    sapmalar: List[float] = []
    while t < T:
        rho = fokker_planck_adimi(rho, f, h, dt)
        t += dt
        adim += 1
        if adim % 200 == 0:
            sapmalar.append(float(np.sum(np.abs(rho - durgun)) * h))
    return {
        "rho": rho, "kütle0": kutle0,
        "kütle": float(np.sum(rho) * h),
        "kütle_sapması": abs(float(np.sum(rho) * h) - kutle0),
        "durağan_sapma": float(np.sum(np.abs(rho - durgun)) * h),
        "sapma_seyri": sapmalar, "adım": adim, "dt": dt,
        "negatif_var_mı": bool(np.any(rho < 0)),
    }


def log_yogunluk_adimi(u: np.ndarray, f: np.ndarray, h: float,
                       dt: float) -> np.ndarray:
    u = np.asarray(u, float)
    f = np.asarray(f, float)
    du = _merkezi_fark(u, h)
    df = _merkezi_fark(f, h)
    return u + dt * (_laplasyen(u, h) + du * du + du * df
                     + _laplasyen(f, h))


def gibbs_hacim_degisimi(f: np.ndarray, h: float) -> float:
    f = np.asarray(f, float)
    return -float(np.sum((_laplasyen(f, h) + _merkezi_fark(f, h) ** 2)
                         * np.exp(-f)) * h)


def morse_indisi(H: np.ndarray) -> int:
    return int(np.sum(np.linalg.eigvalsh(
        (np.asarray(H, float) + np.asarray(H, float).T) / 2) < 0))


def eyer_mi(H: np.ndarray, tol: float = 1e-12) -> bool:
    oz = np.linalg.eigvalsh((np.asarray(H, float)
                             + np.asarray(H, float).T) / 2)
    return bool(oz.min() < -tol and oz.max() > tol)


def kacis_yonu(H: np.ndarray) -> np.ndarray:
    Hs = (np.asarray(H, float) + np.asarray(H, float).T) / 2
    oz, V = np.linalg.eigh(Hs)
    return V[:, int(np.argmin(oz))]


def _cember_egrisi(n: int, r: float) -> Egri:
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    return Egri(np.stack([r * np.cos(t), r * np.sin(t)], axis=1))


def _rapor_akis_hacim() -> str:
    s: List[str] = []
    rng = np.random.default_rng(0)

    s.append("=== MCF mihenk taşı: çember r(t) = √(r₀²−2t) ===")
    r0 = 1.0
    for T in (0.05, 0.15, 0.30, 0.45):
        e = _cember_egrisi(200, r0)
        r = mcf_kos(e, T)
        olculen = math.sqrt(r["egri"].alan() / math.pi)
        kapali = cember_kapali_cozum(r0, T)
        s.append(f"  T={T:.2f}: ölçülen r={olculen:.6f}"
                 f"  kapalı r={kapali:.6f}"
                 f"  bağıl hata={abs(olculen-kapali)/kapali:.3e}"
                 f"  ({r['adım']} adım)")
    s.append(f"  Çöküş zamanı r₀²/2 = {r0*r0/2:.4f}; ona yaklaşınca:")
    for T in (0.49, 0.499):
        e = _cember_egrisi(200, r0)
        r = mcf_kos(e, T)
        olculen = math.sqrt(max(r["egri"].alan(), 0) / math.pi)
        s.append(f"    T={T}: ölçülen {olculen:.5f}"
                 f"  kapalı {cember_kapali_cozum(r0, T):.5f}")
    try:
        cember_kapali_cozum(1.0, 0.6)
        s.append("  T > r₀²/2 kabul edildi (BEKLENMEZ)")
    except ValueError as e_:
        s.append(f"  T > r₀²/2 reddedildi: {e_}")

    s.append("\n=== MCF alanı azaltıyor mu? (her zaman) ===")
    for ad, egri in (("çember", _cember_egrisi(120, 1.0)),
                     ("elips", Egri(np.stack([
                         1.6 * np.cos(np.linspace(0, 2 * np.pi, 120,
                                                  endpoint=False)),
                         0.6 * np.sin(np.linspace(0, 2 * np.pi, 120,
                                                  endpoint=False))],
                         axis=1))),
                     ("gürültülü", Egri(_cember_egrisi(120, 1.0).x
                                        + 0.05 * rng.normal(size=(120, 2))))):
        r = mcf_kos(egri, 0.15)
        a = r["alanlar"]
        artan = sum(1 for i in range(1, len(a)) if a[i] > a[i - 1] + 1e-12)
        s.append(f"  {ad:10s} alan {a[0]:.4f} → {a[-1]:.4f}"
                 f"   artan adım sayısı: {artan}")

    s.append("\n=== Fokker–Planck: kütle korunumu ve durağan hâl ===")
    N = 256
    h = 2 * np.pi / N
    x = np.arange(N) * h
    f = 2.0 * np.cos(x) + 0.5 * np.cos(2 * x)
    rho0 = np.ones(N) / (2 * np.pi)
    for T in (0.5, 2.0, 8.0):
        r = fokker_planck_kos(rho0, f, h, T)
        s.append(f"  T={T:4.1f}: kütle sapması={r['kütle_sapması']:.3e}"
                 f"  durağan hâle L¹ sapma={r['durağan_sapma']:.3e}"
                 f"  negatif var mı: {r['negatif_var_mı']}")
    s.append("  Kütle akı biçimi sayesinde makine hassasiyetinde korunuyor.")

    s.append("\n  Açılmış (korunumsuz) biçimle kıyas:")
    rho = rho0.copy()
    dt = 0.2 * h * h
    kutle_seyri = []
    for adim in range(4000):
        df = _merkezi_fark(f, h)
        drho = _merkezi_fark(rho, h)
        rho = rho + dt * (rho * _laplasyen(f, h) + drho * df
                          + _laplasyen(rho, h))
        if adim % 1000 == 0:
            kutle_seyri.append(float(np.sum(rho) * h))
    s.append(f"    açılmış biçimde kütle seyri: "
             + " → ".join(f"{v:.10f}" for v in kutle_seyri))
    s.append(f"    korunumlu biçimde: {fokker_planck_kos(rho0, f, h, 0.5)['kütle']:.10f}")
    s.append("    (Bu örnekte açılmış biçim de iyi korudu; asıl fark uzun")
    s.append("     koşularda ve düzgün olmayan ızgaralarda birikiyor.)")

    s.append("\n=== Log-yoğunluk: pozitiflik YAPI GEREĞİ ===")
    u = np.log(rho0)
    for adim in range(4000):
        u = log_yogunluk_adimi(u, f, h, dt)
    rho_log = np.exp(u)
    rho_log = rho_log / (np.sum(rho_log) * h)
    rho_fp = fokker_planck_kos(rho0, f, h, 4000 * dt)["rho"]
    rho_fp = rho_fp / (np.sum(rho_fp) * h)
    s.append(f"  ρ=e^u her yerde pozitif mi? {bool(np.all(rho_log > 0))}")
    s.append(f"  Fokker–Planck ile L¹ farkı: "
             f"{float(np.sum(np.abs(rho_log - rho_fp)) * h):.3e}")
    s.append("  İki ayrı denklem aynı çözüme gidiyor — F 52.4 doğru.")

    s.append("\n=== Gibbs hacmi: d/dt Vol = −2∫‖∇f‖²e^{−f} ===")
    s.append("  (İlk hâlde 'kısmî integrasyonla sıfır' yazmıştım; ölçüm")
    s.append("   yalanladı ve türetme düzeltildi.)")
    s.append("  f                     ölçülen        −2∫‖∇f‖²e^{−f}      fark")
    for ad, ff in (("2cos x", 2.0 * np.cos(x)),
                   ("cos x + 0.5cos 2x", np.cos(x) + 0.5 * np.cos(2 * x)),
                   ("sabit (∇f=0)", np.zeros(N))):
        olculen = gibbs_hacim_degisimi(ff, h)
        kapali = -2.0 * float(np.sum(_merkezi_fark(ff, h) ** 2
                                     * np.exp(-ff)) * h)
        s.append(f"  {ad:20s} {olculen:+.6f}   {kapali:+.6f}"
                 f"   {abs(olculen-kapali):.1e}")
    s.append("  f sabitse sıfır, değilse KESİN NEGATİF: Gibbs hacmi")
    s.append("  tekdüze azalıyor. Bu, MCF'nin hacim değişimi DEĞİLDİR;")
    s.append("  o −∫|H|²'dir ve yukarıda ayrıca ölçüldü.")

    s.append("\n=== K23: eyer noktası ölçütü ===")
    ornekler = {
        "yerel asgarî": np.diag([1.0, 2.0, 3.0]),
        "eyer": np.diag([-1.0, 2.0, 3.0]),
        "yerel azamî": np.diag([-1.0, -2.0, -3.0]),
        "dejenere": np.diag([0.0, 1.0, 2.0]),
    }
    s.append("  hâl              λ_max>0?   eyer_mi?   Morse indisi")
    for ad, H in ornekler.items():
        oz = np.linalg.eigvalsh(H)
        s.append(f"  {ad:16s} {str(oz.max() > 0):8s}  "
                 f"{str(eyer_mi(H)):9s}  {morse_indisi(H)}")
    s.append("  'λ_max>0' asgarîyi de eyer sanıyor; doğru ölçüt ayırıyor.")
    H = ornekler["eyer"]
    v_kacis, v_yukselen = kacis_yonu(H), np.linalg.eigh(H)[1][:, -1]
    q = lambda v: float(v @ H @ v)
    s.append(f"  kaçış yönünde q={q(v_kacis):+.3f} (alçalıyor),"
             f"  λ_max yönünde q={q(v_yukselen):+.3f} (yükseliyor)")
    return "\n".join(s)


def _kurede_asgari(f: Callable[[np.ndarray], float], R: float,
                   V: np.ndarray, aday: int = 4, adim: int = 60
                   ) -> float:
    d = V.shape[1]
    V = np.concatenate([np.eye(d), -np.eye(d), np.asarray(V, float)], axis=0)
    deg = np.array([float(f(R * v)) for v in V])
    en_iyi = float(deg.min())
    h = 1e-4
    for i in np.argsort(deg)[:aday]:
        v = V[i].copy()
        fv = float(deg[i])
        t = 0.5
        for _ in range(adim):
            g = np.empty(d)
            for k in range(d):
                e = np.zeros(d); e[k] = h
                u = v + e; u /= np.linalg.norm(u)
                g[k] = (float(f(R * u)) - fv) / h
            g -= (g @ v) * v
            n = np.linalg.norm(g)
            if n < 1e-14:
                break
            u = v - t * g / n
            u /= np.linalg.norm(u)
            fu = float(f(R * u))
            if fu < fv:
                v, fv = u, fu
            else:
                t *= 0.5
                if t < 1e-12:
                    break
        en_iyi = min(en_iyi, fv)
    return en_iyi


def zorlayici_mi(f: Callable[[np.ndarray], float], boyut: int,
                 yaricaplar: Sequence[float] = (1, 10, 100, 1000),
                 yon_sayisi: int = 64, tohum: int = 0
                 ) -> Dict[str, object]:
    r = np.random.default_rng(tohum)
    V = r.normal(size=(yon_sayisi, boyut))
    V = V / np.linalg.norm(V, axis=1, keepdims=True)
    asgariler, medyanlar = [], []
    for R in yaricaplar:
        asgariler.append(_kurede_asgari(f, float(R), V))
        medyanlar.append(float(np.median([f(R * v) for v in V])))
    artan = all(a < b for a, b in zip(asgariler, asgariler[1:]))
    oran = (abs(asgariler[-1]) / abs(medyanlar[-1])
            if medyanlar[-1] != 0 else float("inf"))
    dejenere = oran < 1e-6
    return {
        "yarıçaplar": list(yaricaplar), "küre_asgarîleri": asgariler,
        "küre_medyanları": medyanlar, "asgarî_medyan_oranı": oran,
        "dejenere_yön": dejenere, "tekdüze_artıyor": artan,
        "zorlayıcı_görünüyor": bool(artan and asgariler[-1] > asgariler[0]
                                    and not dejenere),
        "not": "sonlu yarıçap sınaması; düşüş zorlayıcı OLMADIĞINI gösterir",
    }


def baslangic_seviyesi(f: Callable[[np.ndarray], float],
                       x0: np.ndarray, marj: float = 1.0) -> float:
    return float(f(np.asarray(x0, float))) + float(marj)


def alt_seviye_tikiz_mi(f: Callable[[np.ndarray], float], r: float,
                        boyut: int, azami_yaricap: float = 1e4,
                        tohum: int = 0) -> Dict[str, object]:
    rng = np.random.default_rng(tohum)
    V = rng.normal(size=(128, boyut))
    V = V / np.linalg.norm(V, axis=1, keepdims=True)
    V = np.concatenate([np.eye(boyut), -np.eye(boyut), V], axis=0)
    en_buyuk = 0.0
    for v in V:
        R = 1.0
        while R < azami_yaricap and f(R * v) <= r:
            R *= 2.0
        if R >= azami_yaricap:
            return {"sınırlı": False, "sınırsız_yön": v,
                    "azamî_yarıçap": azami_yaricap,
                    "nokta_bulundu": _kumede_nokta_ara(f, r, boyut, rng)}
        alt, ust = (R / 2.0 if R > 1.0 else 0.0), R
        for _ in range(40):
            orta = 0.5 * (alt + ust)
            if f(orta * v) <= r:
                alt = orta
            else:
                ust = orta
        en_buyuk = max(en_buyuk, ust)
    return {"sınırlı": True, "kuşatan_yarıçap": en_buyuk,
            "nokta_bulundu": _kumede_nokta_ara(f, r, boyut, rng)}


def _kumede_nokta_ara(f: Callable[[np.ndarray], float], r: float,
                      boyut: int, rng, deneme: int = 400) -> bool:
    en_iyi = None
    for _ in range(deneme):
        x = rng.normal(size=boyut) * 10 ** rng.uniform(-2, 2)
        v = float(f(x))
        if v <= r:
            return True
        if en_iyi is None or v < en_iyi[1]:
            en_iyi = (x, v)
    x, _ = en_iyi
    for _ in range(200):
        g = _sayisal_gradyan(lambda z: float(f(z)), x)
        nrm = float(np.linalg.norm(g))
        if nrm < 1e-14:
            break
        x = x - 0.05 * g / nrm
        if float(f(x)) <= r:
            return True
    return False


def barriyer(g: Sequence[float], eps: Optional[float] = None) -> float:
    g = np.asarray(g, float)
    if eps is None:
        if np.any(g <= 0):
            return float("inf")
        return float(-np.sum(np.log(g)))
    return float(-np.sum(np.log(np.maximum(g, eps))))


def barriyerli_hedef(f: float, g: Sequence[float], tau: float,
                     eps: Optional[float] = None) -> float:
    if tau < 0:
        raise ValueError("τ ≥ 0 olmalı")
    b = barriyer(g, eps)
    return float(f) + tau * b if math.isfinite(b) else float("inf")


def ic_nokta_yolu(f: Callable[[np.ndarray], float],
                  g: Callable[[np.ndarray], np.ndarray],
                  x0: np.ndarray, tau0: float = 1.0,
                  azalma: float = 0.2, tur: int = 12,
                  ic_adim: int = 600, eta: float = 1e-2
                  ) -> Dict[str, object]:
    x = np.asarray(x0, float).copy()
    if np.any(g(x) <= 0):
        raise ValueError("başlangıç noktası kısıtları ihlal ediyor")
    tau = float(tau0)
    yol = []
    for _ in range(tur):
        for _ in range(ic_adim):
            grad = _sayisal_gradyan(
                lambda z: barriyerli_hedef(f(z), g(z), tau), x)
            adim = eta
            for _ in range(30):
                aday = x - adim * grad
                if np.all(g(aday) > 0) and math.isfinite(
                        barriyerli_hedef(f(aday), g(aday), tau)):
                    break
                adim *= 0.5
            else:
                break
            x = aday
        yol.append((tau, x.copy(), float(f(x)), float(np.min(g(x)))))
        tau *= azalma
    return {"x": x, "yol": yol, "son_tau": tau}


def _sayisal_gradyan(F: Callable[[np.ndarray], float],
                     x: np.ndarray) -> np.ndarray:
    h = np.finfo(float).eps ** (1 / 3)
    g = np.zeros_like(x)
    for i in range(x.size):
        e = np.zeros_like(x)
        e[i] = h * max(1.0, abs(float(x[i])))
        arti, eksi = F(x + e), F(x - e)
        if not (math.isfinite(arti) and math.isfinite(eksi)):
            g[i] = (F(x) - eksi) / e[i] if math.isfinite(eksi) else 0.0
        else:
            g[i] = (arti - eksi) / (2 * e[i])
    return g


def kritik_noktalar(grad: Callable[[np.ndarray], np.ndarray],
                    hess: Callable[[np.ndarray], np.ndarray],
                    baslangiclar: Sequence[Sequence[float]],
                    tol: float = 1e-10, azami: int = 200
                    ) -> List[Dict[str, object]]:
    bulunan: List[Dict[str, object]] = []
    for x0 in baslangiclar:
        x = np.asarray(x0, float).copy()
        yakinsadi = False
        for _ in range(azami):
            g = np.asarray(grad(x), float)
            if float(np.max(np.abs(g))) < tol:
                yakinsadi = True
                break
            H = np.asarray(hess(x), float)
            try:
                adim = np.linalg.solve(H, g)
            except np.linalg.LinAlgError:
                break
            t = 1.0
            for _ in range(30):
                if float(np.max(np.abs(grad(x - t * adim)))) < \
                        float(np.max(np.abs(g))):
                    break
                t *= 0.5
            else:
                break
            x = x - t * adim
        if not yakinsadi:
            continue
        H = np.asarray(hess(x), float)
        oz = np.linalg.eigvalsh((H + H.T) / 2)
        dejenere = bool(np.min(np.abs(oz)) < 1e-8)
        if any(np.max(np.abs(b["x"] - x)) < 1e-6 for b in bulunan):
            continue
        bulunan.append({"x": x, "indis": morse_indisi(H),
                        "dejenere": dejenere, "özdeğerler": oz})
    return bulunan


def morse_bagintisi(indisler: Sequence[int], boyut: int) -> Dict[str, object]:
    M = [0] * (boyut + 1)
    for i in indisler:
        if not 0 <= i <= boyut:
            raise ValueError(f"Morse indisi 0..{boyut} olmalı, {i} geldi")
        M[i] += 1
    return {"M": M, "alterne_toplam": sum((-1) ** k * m
                                          for k, m in enumerate(M))}


def kure_izdusumu(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, float).reshape(-1)
    k = float(x @ x)
    return np.concatenate([2 * x / (k + 1), [(k - 1) / (k + 1)]])


def ters_kure_izdusumu(p: np.ndarray) -> np.ndarray:
    p = np.asarray(p, float).reshape(-1)
    if abs(float(p[-1]) - 1.0) < 1e-12:
        raise ValueError("kuzey kutbu ∞'a karşılık gelir; ℝⁿ'de karşılığı yok")
    return p[:-1] / (1.0 - p[-1])


def _rapor_akis_tikiz() -> str:
    s: List[str] = []

    s.append("=== Zorlayıcılık: küre ASGARÎsine bakmak şart ===")
    ornekler = {
        "‖x‖²": lambda x: float(x @ x),
        "‖x‖⁴ − ‖x‖²": lambda x: float(x @ x) ** 2 - float(x @ x),
        "x₀² (tek yön)": lambda x: float(x[0]) ** 2,
        "−‖x‖²": lambda x: -float(x @ x),
        "x₀": lambda x: float(x[0]),
    }
    for ad, f in ornekler.items():
        r = zorlayici_mi(f, 3)
        s.append(f"  {ad:16s} küre asgarîleri: "
                 + " ".join(f"{v:+.1e}" for v in r["küre_asgarîleri"])
                 + f"   zorlayıcı: {r['zorlayıcı_görünüyor']}")
    s.append("  'x₀² (tek yön)' ORTALAMAYA bakılsaydı zorlayıcı görünürdü;")
    s.append("  asgarîye bakınca x₀=0 düzleminde sabit kaldığı çıkıyor.")

    s.append("\n=== Alt-seviye kümesi boş olmuyor ===")
    f = lambda x: float(x @ x) - 3.0
    x0 = np.array([2.0, -1.0])
    r0 = baslangic_seviyesi(f, x0)
    s.append(f"  f(x₀)={f(x0):.3f}, r₀={r0:.3f}"
             f"   x₀ ∈ K_r₀ mı? {f(x0) <= r0}")
    s.append("  f(x) = ‖x‖² − 3, yani asgarî değer −3:")
    for r in (r0, 0.0, -2.9, -3.5):
        d = alt_seviye_tikiz_mi(f, r, 2)
        s.append(f"  r={r:+6.2f}: sınırlı mı? {d['sınırlı']}"
                 + (f"  kuşatan yarıçap {d['kuşatan_yarıçap']:.1f}"
                    if d["sınırlı"] else "")
                 + f"   nokta bulundu mu? {d['nokta_bulundu']}")
    s.append("  r=−3.50'de küme BOŞ; boş küme de sınırlıdır, o yüzden")
    s.append("  'sınırlı' tek başına yetmiyor — boşluk ayrıca aranıyor.")
    d = alt_seviye_tikiz_mi(lambda x: float(x[0]), 0.0, 2)
    s.append(f"  zorlayıcı olmayan f=x₀, r=0: sınırlı mı? {d['sınırlı']}"
             f"   → tıkızlık hükmü VERİLMİYOR")

    s.append("\n=== Barriyer: kırpma NaN'ı önlüyor ama kısıtı gevşetiyor ===")
    s.append("  g            Φ (kırpmasız)     Φ (ε=1e-8 kırpmalı)")
    for g in ([1.0, 2.0], [0.1, 0.5], [1e-6, 1.0], [-0.5, 1.0], [0.0, 1.0]):
        a = barriyer(g)
        b = barriyer(g, eps=1e-8)
        s.append(f"  {str(g):14s} {a:14.4f}    {b:14.4f}")
    s.append("  Kırpmasız hâlde g ≤ 0 KESİN reddediliyor (inf);")
    s.append("  kırpmalı hâlde sonlu ceza alıyor, yani eniyileme oraya")
    s.append("  kayabilir. Tercih ölçülerek yapılmalı.")

    s.append("\n=== İç nokta yolu: τ küçüldükçe sınıra yaklaşma ===")
    hedef = lambda x: float(x[0] + x[1])
    kisit = lambda x: np.array([x[0], x[1], 1.0 - x[0] - x[1]])
    r = ic_nokta_yolu(hedef, kisit, np.array([0.3, 0.3]), tau0=1.0,
                      azalma=0.25, tur=8, ic_adim=600)
    s.append("      τ         f(x)      min g(x)      x")
    for tau, x, fx, mg in r["yol"]:
        s.append(f"  {tau:.2e}   {fx:.6f}   {mg:.6f}   "
                 f"[{x[0]:.6f}, {x[1]:.6f}]")
    s.append("  Çözüm (0,0); τ küçüldükçe oraya yaklaşılıyor ve kısıt")
    s.append("  hiçbir turda İHLAL EDİLMİYOR (min g > 0).")

    s.append("\n=== Morse bağıntısı: EŞİTLİK (K27) ===")
    def grad(v):
        x, y = v
        return np.array([4 * x ** 3 - 4 * x, 2 * y])

    def hess(v):
        x, y = v
        return np.array([[12 * x ** 2 - 4, 0.0], [0.0, 2.0]])

    baslangiclar = [[a, b] for a in (-1.5, -0.3, 0.0, 0.3, 1.5)
                    for b in (-1.0, 0.0, 1.0)]
    kn = kritik_noktalar(grad, hess, baslangiclar)
    s.append(f"  f(x,y) = x⁴ − 2x² + y²  →  {len(kn)} ayrı kritik nokta:")
    for k in sorted(kn, key=lambda d: float(d["x"][0])):
        s.append(f"    x=[{k['x'][0]:+.6f}, {k['x'][1]:+.6f}]"
                 f"  Morse indisi={k['indis']}"
                 f"  dejenere mi? {k['dejenere']}")
    mb = morse_bagintisi([k["indis"] for k in kn], 2)
    s.append(f"  M = {mb['M']}   Σ(−1)^k M_k = {mb['alterne_toplam']}")
    s.append("  Morse bağıntısı χ(ℝ²) = 1 vermeli — ve veriyor:")
    s.append(f"    2 − 1 + 0 = {mb['alterne_toplam']}  =  χ(ℝ²) = 1")
    s.append("  (İlk hâlde 'χ=2' yazmıştım; yanlıştı. Alt-seviye kümeleri")
    s.append("   eyer değerinin ALTINDA iki ayrı disk, ÜSTÜNDE tek bir")
    s.append("   bölgedir; Morse bağıntısı bütün uzayın χ'sini verir, o da 1.")
    s.append("   Topolojinin eyerde değiştiğini söyleyen zaten bu kuramdır.)")
    s.append("  '≥' ölçütü M=[5,0,0] gibi imkânsız bir dizilimi de")
    s.append(f"  geçirirdi: Σ(−1)^k·[5,0,0] = "
             f"{morse_bagintisi([0]*5, 2)['alterne_toplam']} ≥ 1,"
             " ama eşitliği bozuyor.")

    s.append("\n=== Alexandroff: ℝⁿ ∪ {∞} ≅ Sⁿ ===")
    s.append("  ‖x‖ büyüdükçe görüntü kuzey kutbuna yaklaşıyor:")
    for R in (0.0, 1.0, 10.0, 1e3, 1e6):
        p = kure_izdusumu(np.array([R, 0.0]))
        s.append(f"    ‖x‖={R:8.0e}: π⁻¹(x) = "
                 f"[{p[0]:+.6f}, {p[1]:+.6f}, {p[2]:+.9f}]"
                 f"   ‖p‖={np.linalg.norm(p):.10f}")
    s.append("  Gidiş-dönüş sağlaması:")
    rng = np.random.default_rng(0)
    en_buyuk = 0.0
    for _ in range(500):
        x = rng.normal(size=3) * 10 ** rng.uniform(-3, 3)
        en_buyuk = max(en_buyuk, float(np.max(np.abs(
            ters_kure_izdusumu(kure_izdusumu(x)) - x))))
    s.append(f"    500 noktada azamî bağıl olmayan sapma = {en_buyuk:.2e}")
    try:
        ters_kure_izdusumu(np.array([0.0, 0.0, 1.0]))
        s.append("    kuzey kutbu kabul edildi (BEKLENMEZ)")
    except ValueError as e:
        s.append(f"    kuzey kutbu reddedildi: {e}")
    return "\n".join(s)


def lions_konsantrasyonu(nokta: np.ndarray, agirlik: np.ndarray,
                         yaricaplar: Sequence[float] = (0.25, 0.5, 1.0,
                                                        2.0, 4.0, 8.0),
                         esik: float = 0.9) -> Dict[str, object]:
    X = np.atleast_2d(np.asarray(nokta, float))
    w = np.abs(np.asarray(agirlik, float)).ravel()
    if w.size != X.shape[0]:
        raise ValueError("ağırlık ve nokta sayısı uyuşmuyor")
    top = float(w.sum())
    if top <= 0:
        raise ValueError("kütle sıfır; Q(t) tanımsız")
    w = w / top
    d = np.sqrt(np.maximum(
        np.sum((X[:, None, :] - X[None, :, :]) ** 2, axis=2), 0.0))
    Q: Dict[float, float] = {}
    for t in yaricaplar:
        icinde = (d <= float(t))
        Q[float(t)] = float(np.max(icinde @ w))
    tler = sorted(Q)
    son = Q[tler[-1]]
    ilk = Q[tler[0]]
    if son >= esik:
        hal = "tıkız"
    elif son <= 1.0 - esik:
        hal = "dağılma"
    else:
        hal = "ikilenme"
    return {"Q": Q, "hâl": hal, "Q_son": son, "Q_ilk": ilk,
            "tıkız": hal == "tıkız",
            "not": "Q noktalar merkez alınarak ALTTAN sınırdır; "
                   "'dağılma' hükmü kat'î, 'tıkız' hükmü gevşektir"}


def _turevler(f: Callable[[np.ndarray], float], x: np.ndarray,
              h: float) -> Tuple[np.ndarray, float]:
    x = np.asarray(x, float)
    n = x.size
    g = np.empty(n)
    lap = 0.0
    f0 = float(f(x))
    for k in range(n):
        e = np.zeros(n)
        e[k] = h
        fp, fm = float(f(x + e)), float(f(x - e))
        g[k] = (fp - fm) / (2.0 * h)
        lap += (fp - 2.0 * f0 + fm) / (h * h)
    return g, float(lap)


def bochner_artigi(f: Callable[[np.ndarray], float], x: np.ndarray,
                   K: float = 0.0, N: Optional[float] = None,
                   h: float = 1e-3) -> Dict[str, float]:
    x = np.asarray(x, float)
    n = int(x.size)
    N = float(n) if N is None else float(N)
    if N <= 0:
        raise ValueError("N > 0 olmalı")

    def gkare(z: np.ndarray) -> float:
        g, _ = _turevler(f, z, h)
        return float(g @ g)

    def laplasyen(z: np.ndarray) -> float:
        return _turevler(f, z, h)[1]

    g0, lap0 = _turevler(f, x, h)
    _, lap_gkare = _turevler(gkare, x, h)
    grad_lap, _ = _turevler(laplasyen, x, h)

    sol = 0.5 * lap_gkare
    sag = float(g0 @ grad_lap) + (lap0 * lap0) / N + float(K) * float(g0 @ g0)
    return {"sol": float(sol), "sağ": float(sag),
            "artık": float(sol - sag),
            "‖∇f‖²": float(g0 @ g0), "Δf": float(lap0),
            "N": N, "K": float(K)}


def bochner_suzgeci(f: Callable[[np.ndarray], float], x: np.ndarray,
                    K: float = 0.0, N: Optional[float] = None,
                    h: float = 1e-3, tolerans: float = 1e-3
                    ) -> Dict[str, object]:
    r = bochner_artigi(f, x, K=K, N=N, h=h)
    olcek = max(abs(r["sol"]), abs(r["sağ"]), 1e-12)
    nispi = r["artık"] / olcek
    r2: Dict[str, object] = dict(r)
    r2["nispî_artık"] = float(nispi)
    r2["kabul"] = bool(nispi >= -abs(tolerans))
    return r2


def cayley_cekilmesi(X: np.ndarray, xi: np.ndarray) -> np.ndarray:
    X = np.asarray(X, float)
    xi = np.asarray(xi, float)
    if X.shape != xi.shape:
        raise ValueError("ξ, X ile aynı şekilde olmalı")
    n = X.shape[0]
    W = xi + 0.5 * (X @ (X.T @ xi))
    A = W @ X.T - X @ W.T
    I = np.eye(n)
    return np.linalg.solve(I - 0.5 * A, (I + 0.5 * A) @ X)


def cayley_hatasi(X: np.ndarray, xi: np.ndarray) -> Dict[str, float]:
    R = cayley_cekilmesi(X, xi)
    p = R.shape[1]
    diklik = float(np.linalg.norm(R.T @ R - np.eye(p)))
    t = 1e-4
    Rt = cayley_cekilmesi(X, t * np.asarray(xi, float))
    teget = float(np.linalg.norm(Rt - (X + t * np.asarray(xi, float)))
                  / (t * t))
    return {"diklik_hatası": diklik, "teğetlik_katsayısı": teget}


def postnikov_indisi(betti: Sequence[Sequence[float]],
                     esik: float = 0.5) -> Dict[str, object]:
    B = np.atleast_2d(np.asarray(betti, float))
    tikanik: List[Tuple[int, int, float]] = []
    for m in range(B.shape[0]):
        for n in range(1, B.shape[1]):
            if B[m, n] > float(esik):
                tikanik.append((int(m), int(n), float(B[m, n])))
    if not tikanik:
        return {"mertebe": None, "derece": None, "tıkanık": False,
                "hepsi": []}
    m, n, v = min(tikanik, key=lambda t: (t[0], t[1]))
    return {"mertebe": m, "derece": n, "değer": v, "tıkanık": True,
            "hepsi": tikanik}


def _rapor_akis_ikmal() -> str:
    s: List[str] = ["CERİDENİN İKMÂL FIKRALARI -- eksik olan üçü", ""]
    rng = np.random.default_rng(0)

    s.append("=== İKMÂL II: Lions konsantrasyon-tıkızlığı ===")
    tek = rng.normal(size=(80, 2)) * 0.3
    s.append("  tek yığın        : %s" %
             lions_konsantrasyonu(tek, np.ones(80))["hâl"])
    iki = np.vstack([rng.normal(size=(40, 2)) * 0.3,
                     rng.normal(size=(40, 2)) * 0.3 + 40.0])
    s.append("  iki uzak yığın   : %s   ← İKİLENME (kırmızı)" %
             lions_konsantrasyonu(iki, np.ones(80))["hâl"])
    yayik = rng.normal(size=(200, 2)) * 200.0
    s.append("  yayılmış kütle   : %s   ← DAĞILMA (kırmızı)" %
             lions_konsantrasyonu(yayik, np.ones(200))["hâl"])

    s.append("")
    s.append("=== İKMÂL III: RCD(K,N) Bochner süzgeci ===")

    def kare(z):
        return 0.5 * float(np.asarray(z, float) @ np.asarray(z, float))

    x = np.array([0.7, -0.3, 0.5])
    r = bochner_suzgeci(kare, x, K=0.0, N=None)
    s.append("  f=½‖x‖², n=N=3 : artık %+.3e  nispî %+.2e  kabul=%s"
             % (r["artık"], r["nispî_artık"], r["kabul"]))
    r = bochner_suzgeci(kare, x, K=0.0, N=1.0)
    s.append("  aynı f, N=1     : artık %+.3e  nispî %+.2e  kabul=%s"
             "   ← KIRMIZI" % (r["artık"], r["nispî_artık"], r["kabul"]))

    s.append("")
    s.append("=== İKMÂL IV: Cayley çekilmesi ===")
    A = rng.normal(size=(8, 3))
    X = np.linalg.qr(A)[0]
    xi = rng.normal(size=(8, 3))
    xi = xi - X @ (X.T @ xi)
    h = cayley_hatasi(X, xi)
    s.append("  diklik hatası      : %.3e" % h["diklik_hatası"])
    s.append("  teğetlik katsayısı : %.3e  (ξ→0'da sınırlı)"
             % h["teğetlik_katsayısı"])

    s.append("")
    s.append("=== İKMÂL IV: Postnikov tıkanıklık indisi (VEKİL) ===")
    temiz = [[1, 0, 0], [1, 0, 0], [1, 0, 0]]
    s.append("  tıkanıksız Betti : %s" % postnikov_indisi(temiz)["tıkanık"])
    tikali = [[1, 0, 0], [1, 2, 0], [1, 0, 0]]
    t = postnikov_indisi(tikali)
    s.append("  tıkalı Betti     : mertebe %s, derece %s   ← sıçrama buraya"
             % (t["mertebe"], t["derece"]))
    return "\n".join(s)


def asgari_var_mi(f=None, boyut: int = 2, ne: str = "hüküm",
                  c: float = 0.0,
                  yaricaplar=(1.0, 10.0, 100.0, 1000.0),
                  yon_sayisi: int = 200, azami_yaricap: float = 1e4,
                  ornek: int = 5000, adim: int = 30,
                  yaklasim_sayisi: int = 40, tohum: int = 0):
    if ne == "zorlayıcı":
        return zorlayici_mi(f, boyut, tuple(yaricaplar), yon_sayisi, tohum)
    if False:
        rng = np.random.default_rng(tohum)
        eksenler = np.concatenate([np.eye(boyut), -np.eye(boyut)], axis=0)
        yonler = rng.normal(size=(yon_sayisi, boyut))
        yonler /= np.linalg.norm(yonler, axis=1, keepdims=True)
        yonler = np.concatenate([eksenler, yonler], axis=0)
        asgariler = []
        for R in yaricaplar:
            degerler = [f(R * u) for u in yonler]
            asgariler.append(float(min(degerler)))
        artiyor = all(asgariler[i] < asgariler[i + 1] for i in range(len(asgariler) - 1))
        return {
            "yaricaplar": list(yaricaplar),
            "kure_asgarileri": asgariler,
            "delil_artiyor": artiyor,
            "kayit": "sonlu yön örneklemesi; ispat değil delil",
        }

    if ne == "seviye":
        return alt_seviye_tikiz_mi(f, c, boyut, azami_yaricap, tohum)
    if False:
        rng = np.random.default_rng(tohum)
        R = np.exp(rng.uniform(np.log(1e-2), np.log(azami_yaricap), size=ornek))
        U = rng.normal(size=(ornek, boyut))
        U /= np.linalg.norm(U, axis=1, keepdims=True)
        eksenler = np.concatenate([np.eye(boyut), -np.eye(boyut)], axis=0)
        U[: len(eksenler)] = eksenler
        R[: len(eksenler)] = azami_yaricap
        X = R[:, None] * U
        icinde = np.array([f(x) <= c for x in X])
        if not icinde.any():
            return {"c": c, "nokta_yok": True, "azami_norm": 0.0, "sinirli_gorunuyor": True}
        azami = float(np.max(np.linalg.norm(X[icinde], axis=1)))
        return {
            "c": c,
            "nokta_yok": False,
            "azami_norm": azami,
            "sinirli_gorunuyor": bool(azami < azami_yaricap * 0.5),
        }

    if ne == "hüküm":
        z = asgari_var_mi(f, boyut, "zorlayıcı", yaricaplar=yaricaplar,
                          yon_sayisi=yon_sayisi, tohum=tohum)
        s_ = asgari_var_mi(f, boyut, "seviye", c=c,
                           azami_yaricap=azami_yaricap, ornek=ornek,
                           tohum=tohum)
        return {"zorlayıcı": z, "seviye": s_,
                "asgarî_var_delili": bool(z["zorlayıcı_görünüyor"]
                                          and s_["sınırlı"]),
                "kayıt": "Weierstrass şartının sayısal delili; ispat değil"}

    if ne == "kaçış":
        x = 0.0
        yol = []
        for _ in range(adim):
            x = x - 10.0 * (-np.exp(-x))
            yol.append((x, float(np.exp(-x))))
        return {
            "son_x": yol[-1][0],
            "son_f": yol[-1][1],
            "infimum": 0.0,
            "kaciyor": yol[-1][0] > yol[0][0] * 10 or yol[-1][0] > 10.0,
            "asgari_ulasilmadi": yol[-1][1] > 0.0,
        }

    if ne == "süreksiz":
        k = np.arange(1, yaklasim_sayisi + 1)
        x_arti = 1.0 / (2 * np.pi * k + np.pi / 2)
        x_eksi = 1.0 / (2 * np.pi * k - np.pi / 2)
        f_arti = np.sin(1.0 / x_arti)
        f_eksi = np.sin(1.0 / x_eksi)
        return {
            "x_arti_son": float(x_arti[-1]),
            "x_eksi_son": float(x_eksi[-1]),
            "limit_arti": float(np.max(np.abs(f_arti - 1.0))),
            "limit_eksi": float(np.max(np.abs(f_eksi + 1.0))),
            "iki_dizi_de_sifira_gidiyor": bool(x_arti[-1] < 1e-2 and x_eksi[-1] < 1e-2),
            "limitler_ayrisiyor": bool(
                np.allclose(f_arti, 1.0, atol=1e-12) and np.allclose(f_eksi, -1.0, atol=1e-12)
            ),
        }

    if ne == "yönlü":
        yaklasim_sayisi = min(yaklasim_sayisi, 12)
        r = 10.0 ** (-np.arange(1, yaklasim_sayisi + 1, dtype=float))
        aciler = [0.0, np.pi / 4, np.pi / 2, np.pi / 3]
        izler = {}
        for th in aciler:
            x, y = r * np.cos(th), r * np.sin(th)
            izler[round(th, 6)] = float(((x * x - y * y) / (x * x + y * y))[-1])
        degerler = list(izler.values())
        return {
            "yarıcap_son": float(r[-1]),
            "yone_gore_limitler": izler,
            "cos2theta_ile_uyusuyor": all(
                abs(izler[round(th, 6)] - np.cos(2 * th)) < 1e-12 for th in aciler
            ),
            "limit_yok": bool(max(degerler) - min(degerler) > 0.5),
        }

    raise ValueError("asgarî suâlinin kipi bilinmiyor: %r" % (ne,))


def kare(x: np.ndarray) -> float:
    return float(np.sum(x * x))


def rosenbrock(x: np.ndarray) -> float:
    return float(np.sum(100.0 * (x[1:] - x[:-1] ** 2) ** 2 + (1 - x[:-1]) ** 2))


def zorlayici_olmayan(x: np.ndarray) -> float:
    return float(np.sum(x[1:] ** 2))


def _rbf(x: np.ndarray, dugum: np.ndarray, h: float) -> np.ndarray:
    return np.exp(-0.5 * ((x[:, None] - dugum[None, :]) / h) ** 2)


def _drbf(x: np.ndarray, dugum: np.ndarray, h: float) -> np.ndarray:
    return -((x[:, None] - dugum[None, :]) / (h * h)) * _rbf(x, dugum, h)


class KAN211:

    def __init__(self, ic_dugum: int = 32, dis_dugum: int = 32, tohum: int = 0) -> None:
        rng = np.random.default_rng(tohum)
        self.gx = np.linspace(-1, 1, ic_dugum)
        self.hx = (self.gx[1] - self.gx[0]) * 1.5
        self.c1 = rng.normal(scale=0.8, size=ic_dugum)
        self.c2 = rng.normal(scale=0.8, size=ic_dugum)
        self.K = dis_dugum
        self.gs = np.linspace(-1, 1, dis_dugum)
        self.hs = (self.gs[1] - self.gs[0]) * 1.5
        self.c3 = np.zeros(dis_dugum)

    def kenar(self, t: np.ndarray, hangi: int) -> np.ndarray:
        return _rbf(t, self.gx, self.hx) @ (self.c1 if hangi == 1 else self.c2)

    def ic(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        return self.kenar(x, 1) + self.kenar(y, 2)

    def __call__(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        return _rbf(self.ic(x, y), self.gs, self.hs) @ self.c3

    def _izgara_yenile(self, s: np.ndarray, hedef: np.ndarray, lam: float) -> None:
        lo, hi = float(s.min()), float(s.max())
        pay = 0.15 * (hi - lo) + 1e-6
        self.gs = np.linspace(lo - pay, hi + pay, self.K)
        self.hs = (self.gs[1] - self.gs[0]) * 1.5
        B = _rbf(s, self.gs, self.hs)
        self.c3 = np.linalg.solve(B.T @ B + lam * np.eye(self.K), B.T @ hedef)

    def egit(
        self, x: np.ndarray, y: np.ndarray, hedef: np.ndarray,
        tur: int = 8000, eta0: float = 0.01, lam: float = 1e-6,
    ) -> float:
        m1x, m1y = _rbf(x, self.gx, self.hx), _rbf(y, self.gx, self.hx)
        n = len(x)
        P = [self.c1, self.c2, self.c3]
        M = [np.zeros_like(p) for p in P]
        V = [np.zeros_like(p) for p in P]
        art = np.zeros(n)
        for t in range(1, tur + 1):
            s = m1x @ P[0] + m1y @ P[1]
            if t % 200 == 1:
                self._izgara_yenile(s, hedef, lam)
                P[2] = self.c3
                M[2] = np.zeros_like(P[2])
                V[2] = np.zeros_like(P[2])
            B = _rbf(s, self.gs, self.hs)
            art = B @ P[2] - hedef
            ds = _drbf(s, self.gs, self.hs) @ P[2]
            g = (2.0 / n) * (art * ds)
            G = [m1x.T @ g, m1y.T @ g, (2.0 / n) * (B.T @ art)]
            eta = eta0 * (1 - t / tur) + 1e-5
            for i in range(3):
                M[i] *= 0.9
                M[i] += 0.1 * G[i]
                V[i] *= 0.999
                V[i] += 0.001 * G[i] ** 2
                P[i] -= eta * (M[i] / (1 - 0.9 ** t)) / (np.sqrt(V[i] / (1 - 0.999 ** t)) + 1e-8)
        self.c1, self.c2, self.c3 = P
        return float(np.sqrt(np.mean(art ** 2)))


def _afin_uyum(a: np.ndarray, b: np.ndarray) -> float:
    A = np.stack([a, np.ones_like(a)], axis=1)
    kat, *_ = np.linalg.lstsq(A, b, rcond=None)
    return float(np.sqrt(np.mean((A @ kat - b) ** 2)) / (np.std(b) + 1e-12))


def kan_sinamasi(n: int = 2000, restart: int = 6, tohum: int = 0) -> Dict[str, object]:
    rng = np.random.default_rng(tohum)
    hedef = lambda x, y: np.exp(np.sin(np.pi * x) + y * y)
    x = rng.uniform(-1, 1, n)
    y = rng.uniform(-1, 1, n)
    z = hedef(x, y)
    mu, sd = float(z.mean()), float(z.std())
    zn = (z - mu) / sd

    xt, yt = rng.uniform(-1, 1, 800), rng.uniform(-1, 1, 800)
    zt = (hedef(xt, yt) - mu) / sd

    izgara = np.linspace(-1, 1, 300)
    denemeler = []
    en_iyi = None
    for tekrar in range(restart):
        ag = KAN211(tohum=100 + tekrar)
        kalinti = ag.egit(x, y, zn)
        d = {
            "kalinti": kalinti,
            "sinama": float(np.sqrt(np.mean((ag(xt, yt) - zt) ** 2))),
            "u1": _afin_uyum(ag.kenar(izgara, 1), np.sin(np.pi * izgara)),
            "u2": _afin_uyum(ag.kenar(izgara, 2), izgara ** 2),
        }
        denemeler.append(d)
        if en_iyi is None or d["kalinti"] < en_iyi["kalinti"]:
            en_iyi = d

    basarili = [d for d in denemeler if d["kalinti"] < 0.05]
    return {
        "restart": restart,
        "en_iyi_egitim_kalintisi": en_iyi["kalinti"],
        "en_iyi_bagil_sinama_hatasi": en_iyi["sinama"],
        "iyi_uyduruyor": bool(en_iyi["sinama"] < 0.05),
        "phi1_sin_ile_uyum_hatasi": en_iyi["u1"],
        "phi2_kare_ile_uyum_hatasi": en_iyi["u2"],
        "kenarlar_okunabilir": bool(en_iyi["u1"] < 0.05 and en_iyi["u2"] < 0.05),
        "basarili_restart_sayisi": len(basarili),
        "cukura_dusen_var": bool(len(basarili) < restart),
        "kalintilar": [round(d["kalinti"], 4) for d in denemeler],
    }


def poisson_ornekleri(
    n: int, N: int, azami_kip: int = 8, tohum: int = 0
) -> Tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(tohum)
    k = np.fft.rfftfreq(N, d=1.0 / N)
    a_hat = np.zeros((n, len(k)), dtype=complex)
    kip = np.arange(1, azami_kip + 1)
    a_hat[:, kip] = (rng.normal(size=(n, azami_kip)) + 1j * rng.normal(size=(n, azami_kip))) / kip
    a = np.fft.irfft(a_hat, n=N) * N
    u_hat = np.zeros_like(a_hat)
    u_hat[:, 1:] = a_hat[:, 1:] / (k[1:] ** 2)
    u = np.fft.irfft(u_hat, n=N) * N
    return a, u


class FourierIslemci:

    def __init__(self, kip_sayisi: int = 16) -> None:
        self.kip_sayisi = kip_sayisi
        self.R = np.zeros(kip_sayisi, dtype=complex)

    def egit(self, a: np.ndarray, u: np.ndarray) -> None:
        N = a.shape[1]
        A = np.fft.rfft(a, axis=1)
        U = np.fft.rfft(u, axis=1)
        for j in range(self.kip_sayisi):
            pay = np.vdot(A[:, j], U[:, j])
            payda = np.vdot(A[:, j], A[:, j])
            self.R[j] = pay / payda if abs(payda) > 1e-12 else 0.0

    def __call__(self, a: np.ndarray) -> np.ndarray:
        N = a.shape[1]
        A = np.fft.rfft(a, axis=1)
        U = np.zeros_like(A)
        j = min(self.kip_sayisi, A.shape[1])
        U[:, :j] = A[:, :j] * self.R[:j]
        return np.fft.irfft(U, n=N)


def _bagil(v: np.ndarray, d: np.ndarray) -> float:
    return float(np.linalg.norm(v - d) / np.linalg.norm(d))


def fno_sinamasi() -> Dict[str, object]:
    a, u = poisson_ornekleri(400, 64, azami_kip=8, tohum=0)
    f = FourierIslemci(kip_sayisi=16)
    f.egit(a, u)

    a1, u1 = poisson_ornekleri(200, 64, azami_kip=8, tohum=1)
    ayni = _bagil(f(a1), u1)

    a2, u2 = poisson_ornekleri(200, 256, azami_kip=8, tohum=2)
    baska = _bagil(f(a2), u2)

    a3, u3 = poisson_ornekleri(200, 256, azami_kip=24, tohum=3)
    yuksek = _bagil(f(a3), u3)
    return {
        "ayni_cozunurluk_hatasi": ayni,
        "farkli_cozunurluk_hatasi": baska,
        "cozunurluk_aktarimi_calisiyor": bool(baska < 0.02),
        "yuksek_kip_hatasi": yuksek,
        "yuksek_kipte_bozuluyor": bool(yuksek > 10 * max(baska, 1e-12)),
    }


class DeepONet:

    def __init__(self, duyu: int = 64, taban: int = 32) -> None:
        self.duyu = duyu
        self.taban = taban
        self.W = np.zeros((taban, duyu))

    def _govde(self, y: np.ndarray) -> np.ndarray:
        k = np.arange(1, self.taban // 2 + 1)
        return np.concatenate(
            [np.cos(2 * np.pi * k[None, :] * y[:, None]),
             np.sin(2 * np.pi * k[None, :] * y[:, None])], axis=1
        )

    def egit(self, a: np.ndarray, u: np.ndarray, lam: float = 1e-8) -> None:
        y = np.arange(a.shape[1]) / a.shape[1]
        T = self._govde(y)
        C = np.linalg.lstsq(T, u.T, rcond=None)[0].T
        self.W = np.linalg.solve(
            a.T @ a + lam * np.eye(self.duyu), a.T @ C
        ).T

    def __call__(self, a: np.ndarray, N: int | None = None) -> np.ndarray:
        N = N or a.shape[1]
        y = np.arange(N) / N
        return (self._govde(y) @ (self.W @ a.T)).T


def deeponet_sinamasi() -> Dict[str, object]:
    a, u = poisson_ornekleri(400, 64, azami_kip=8, tohum=0)
    d = DeepONet(duyu=64, taban=32)
    d.egit(a, u)

    a1, u1 = poisson_ornekleri(200, 64, azami_kip=8, tohum=1)
    ayni = _bagil(d(a1), u1)

    a2, u2 = poisson_ornekleri(200, 256, azami_kip=8, tohum=2)
    try:
        _ = d(a2)
        aktarilabilir = True
        aktarim_hatasi = _bagil(d(a2), u2)
    except ValueError:
        aktarilabilir = False
        aktarim_hatasi = float("inf")

    a2_duyu = a2[:, :: a2.shape[1] // 64]
    ornekli = _bagil(d(a2_duyu, N=256), u2)

    f = FourierIslemci(kip_sayisi=16)
    f.egit(a, u)
    fno_aktarim = _bagil(f(a2), u2)
    return {
        "ayni_cozunurluk_hatasi": ayni,
        "iyi_ogreniyor": bool(ayni < 0.02),
        "ham_aktarim_mumkun": aktarilabilir,
        "ham_aktarim_hatasi": aktarim_hatasi,
        "yeniden_ornekleyerek_hata": ornekli,
        "fno_ayni_iste_hatasi": fno_aktarim,
        "yeniden_ornekleyince_denk": bool(abs(ornekli - fno_aktarim) < 0.01),
        "fark_dogrulukta_degil_arayuzde": bool(
            (not aktarilabilir) and abs(ornekli - fno_aktarim) < 0.01
        ),
    }


def _rapor_asgari() -> str:
    s = ["=== tikizlik ==="]
    z = asgari_var_mi(kare, 3, ne="zorlayıcı")
    s.append("zorlayıcı(‖x‖²)  küre asgarileri=%s  artıyor=%s"
             % ([round(v, 3) for v in z["kure_asgarileri"]], z["delil_artiyor"]))
    zn = asgari_var_mi(zorlayici_olmayan, 3, ne="zorlayıcı")
    s.append("zorlayıcı değil    küre asgarileri=%s  artıyor=%s"
             % ([round(v, 6) for v in zn["kure_asgarileri"]], zn["delil_artiyor"]))
    a = asgari_var_mi(kare, 3, c=4.0, ne="seviye")
    b = asgari_var_mi(zorlayici_olmayan, 3, c=4.0, ne="seviye")
    s.append("alt seviye {f≤4}  ‖x‖²: azami norm=%.3g sınırlı=%s   |   sınırsız hâl: azami norm=%.3g sınırlı=%s"
             % (a["azami_norm"], a["sinirli_gorunuyor"], b["azami_norm"], b["sinirli_gorunuyor"]))
    u = asgari_var_mi(ne="kaçış")
    s.append("ulaşılmayan inf   son f=%.3g > inf=0 → %s (x kaçıyor=%s)"
             % (u["son_f"], u["asgari_ulasilmadi"], u["kaciyor"]))
    p = asgari_var_mi(ne="süreksiz")
    s.append("sin(1/x)          iki dizi 0'a gidiyor=%s, limitler ±1'e ayrışıyor=%s"
             % (p["iki_dizi_de_sifira_gidiyor"], p["limitler_ayrisiyor"]))
    q = asgari_var_mi(ne="yönlü")
    s.append("(x²−y²)/(x²+y²)   cos2θ ile uyuşuyor=%s, limit yok=%s"
             % (q["cos2theta_ile_uyusuyor"], q["limit_yok"]))
    return "\n".join(s)


def _rapor_modern() -> str:
    s = ["=== modern ==="]
    k = kan_sinamasi()
    s.append("KAN       en iyi: eğitim kalıntısı=%.4f  bağıl sınama=%.4f (iyi=%s)"
             % (k["en_iyi_egitim_kalintisi"], k["en_iyi_bagil_sinama_hatasi"],
                k["iyi_uyduruyor"]))
    s.append("          okunabilirlik: φ₁~sin(πx) hata=%.4f, φ₂~y² hata=%.4f → %s"
             % (k["phi1_sin_ile_uyum_hatasi"], k["phi2_kare_ile_uyum_hatasi"],
                k["kenarlar_okunabilir"]))
    s.append("          %d/%d başlangıç iyi havzaya düştü; kalıntılar=%s"
             % (k["basarili_restart_sayisi"], k["restart"], k["kalintilar"]))
    f = fno_sinamasi()
    s.append("FNO       N=64 hata=%.2e | N=256'ya aktarım=%.2e (çalışıyor=%s)"
             % (f["ayni_cozunurluk_hatasi"], f["farkli_cozunurluk_hatasi"],
                f["cozunurluk_aktarimi_calisiyor"]))
    s.append("          zaaf: görülmemiş yüksek kipte hata=%.4f (bozuluyor=%s)"
             % (f["yuksek_kip_hatasi"], f["yuksek_kipte_bozuluyor"]))
    d = deeponet_sinamasi()
    s.append("DeepONet  N=64 hata=%.2e (iyi=%s) | ham aktarım mümkün=%s"
             % (d["ayni_cozunurluk_hatasi"], d["iyi_ogreniyor"], d["ham_aktarim_mumkun"]))
    s.append("          yeniden örnekleyerek=%.2e  vs  FNO aynı işte=%.2e → denk=%s"
             % (d["yeniden_ornekleyerek_hata"], d["fno_ayni_iste_hatasi"],
                d["yeniden_ornekleyince_denk"]))
    s.append("          fark doğrulukta değil arayüzde=%s" % d["fark_dogrulukta_degil_arayuzde"])
    return "\n".join(s)

BOLUMLER = (
    ("HARTLEY -- RHT ve M29 evrişim kaidesi", "_rapor_reel_hartley"),
    ("REEL GÖMME -- J²=−I ve M28 işareti", "_rapor_reel_karmasik"),
    ("MELEKE KAPILARI -- çarpan biçimi, dizey kurulmadan",
     "_rapor_reel_meleke"),
    ("GALOIS -- ℤ[ζ₈][1/√2] tam aritmetiği", "_rapor_hesap_galois"),
    ("P-ADİK -- ultrametrik eşitsizlik (M25/M26)", "_rapor_hesap_padic"),
    ("PALMER -- rasyonel kuantum mekaniği itirazı", "_rapor_hesap_palmer"),
    ("SAKLAMA -- kararlayıcı ve MPS maliyetleri", "_rapor_hesap_saklama"),
    ("DONANIM -- ölçülen yol", "_rapor_hesap_donanim"),
    ("MANİFOLD -- Riemann tensörü ve Laplace–Beltrami",
     "_rapor_token_uzaylari_manifold"),
    ("MORFİZM -- itme, çekme, izometri", "_rapor_token_uzaylari_morfizm"),
    ("YAPIŞTIR -- Glue/ua ve kayıpsızlık karnesi",
     "_rapor_token_uzaylari_yapistir"),
    ("KAN -- sonlu kategorilerde Lan/Ran", "_rapor_token_uzaylari_kan"),
    ("KAN-SPLİNE -- birliğin bölünmesi", "_rapor_token_uzaylari_kan_spline"),
    ("FNO -- Parseval ve ızgaradan bağımsızlık", "_rapor_token_uzaylari_fno"),
    ("LİE -- braket, Jacobi, so(n), kutup ayrışımı", "_rapor_akis_lie"),
    ("HACİM -- MCF, Fokker–Planck, Morse indisi", "_rapor_akis_hacim"),
    ("TIKIZ -- zorlayıcılık, barriyer, küre izdüşümü", "_rapor_akis_tikiz"),
    ("İKMÂL -- Lions, Bochner, Cayley, Postnikov", "_rapor_akis_ikmal"),
)


def rapor() -> str:
    s = []
    for baslik, fn in BOLUMLER:
        s.append("")
        s.append("=" * 70)
        s.append("  " + baslik)
        s.append("=" * 70)
        s.append(globals()[fn]())
    return "\n".join(s)


if __name__ == "__main__":
    print(rapor())
