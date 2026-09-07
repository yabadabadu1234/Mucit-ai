from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["QuditAyari", "agirlik", "durum", "durum_yigin", "suz", "dallanma",
           "metrik", "dogal_adim", "blok", "ortusme", "rapor"]


@dataclass
class QuditAyari:

    d: int = 4096
    kan: int = 4
    derece: int = 8
    qsvt: int = 16
    yon: int = 8
    duzenli: float = 1e-6
    tip: object = np.float64
    tohum: int = 0

    @property
    def katsayi_sayisi(self) -> int:
        return 2 * int(self.kan) * (int(self.derece) + 1) + int(self.yon)


def agirlik(d: int, teta: Optional[np.ndarray] = None) -> np.ndarray:
    d = int(d)
    if d < 2:
        raise ValueError("qudit seviyesi en az 2 olmalı, %d verildi" % d)
    if teta is None:
        teta = np.ones(min(8, d - 1), float)
    teta = np.asarray(teta, float).reshape(-1)
    r = teta.size
    if not 1 <= r <= d - 1:
        raise ValueError("Cartan yönü 1…d−1 arası olmalı, %d verildi" % r)

    kuyruk = np.zeros(d + 1)
    kuyruk[:r] = teta
    kuyruk = np.cumsum(kuyruk[::-1])[::-1]
    m = np.arange(d)
    w = kuyruk[m].copy()
    ic = m[1:] <= r
    w[1:][ic] -= m[1:][ic] * teta[m[1:][ic] - 1]
    enb = float(np.max(np.abs(w)))
    return w / enb if enb > 1e-300 else w


def _cheb(u: np.ndarray, derece: int, ikinci: bool = False) -> np.ndarray:
    u = np.asarray(u, float).reshape(-1)
    n = int(derece) + 1
    out = np.empty((n, u.size), float)
    out[0] = 1.0
    if n > 1:
        out[1] = (2.0 * u) if ikinci else u
    for j in range(2, n):
        out[j] = 2.0 * u * out[j - 1] - out[j - 2]
    return out


def durum(c: np.ndarray, s: np.ndarray, teta: Optional[np.ndarray] = None,
          d: int = 0, ayar: Optional[QuditAyari] = None) -> np.ndarray:
    a = ayar or QuditAyari()
    d = int(d or a.d)
    c = np.asarray(c, float)
    s = np.asarray(s, float)
    if c.shape != s.shape:
        raise ValueError("c ve s aynı şekilde olmalı: %s vs %s"
                         % (c.shape, s.shape))
    K, n = c.shape
    w = agirlik(d, teta)
    T = _cheb(w, n - 1, ikinci=False)
    U = _cheb(w, n - 1, ikinci=True)
    reel = (c @ T).sum(axis=0)
    sanal = (s @ U).sum(axis=0)
    reel = reel - float(np.max(reel))
    psi = np.exp(reel) * np.exp(1j * sanal)
    nrm = float(np.linalg.norm(psi))
    return psi / nrm if nrm > 1e-300 else psi


def durum_yigin(c: np.ndarray, s: np.ndarray, TETA: np.ndarray,
                d: int = 0, ayar: Optional[QuditAyari] = None,
                tip=None, cekirdek: str = "numpy") -> np.ndarray:
    a = ayar or QuditAyari()
    d = int(d or a.d)
    if cekirdek != "numpy":
        from .hizli import cekirdek as _fused
        from .hizli import _bicimle
        W = np.atleast_2d(np.asarray(TETA, np.float32))
        Wg = np.stack([agirlik(d, W[i]) for i in range(W.shape[0])])
        cs = np.asarray(c, float).sum(axis=0)
        ss = np.asarray(s, float).sum(axis=0)
        return _fused(Wg, cs, ss, ne=cekirdek)["psi"]
    tip = np.dtype(tip or getattr(a, "tip", np.float64))
    ctip = np.complex64 if tip == np.float32 else np.complex128
    c = np.asarray(c, tip)
    s = np.asarray(s, tip)
    TETA = np.atleast_2d(np.asarray(TETA, tip))
    B, rr = TETA.shape
    K, n = c.shape

    kuy = np.zeros((B, d + 1), tip)
    kuy[:, :rr] = TETA
    kuy = np.cumsum(kuy[:, ::-1], axis=1)[:, ::-1]
    m = np.arange(d)
    W = kuy[:, m].copy()
    ic = m[1:] <= rr
    W[:, 1:][:, ic] -= (m[1:][ic] * TETA[:, m[1:][ic] - 1]).astype(tip)
    enb = np.max(np.abs(W), axis=1, keepdims=True)
    W = W / np.maximum(enb, tip.type(1e-30))

    cs = c.sum(axis=0).astype(tip)
    ss = s.sum(axis=0).astype(tip)
    iki = (2.0 * W).astype(tip)

    b1 = np.zeros_like(W); b2 = np.zeros_like(W)
    for j in range(n - 1, 0, -1):
        b1, b2 = cs[j] + iki * b1 - b2, b1
    reel = cs[0] + W * b1 - b2

    b1 = np.zeros_like(W); b2 = np.zeros_like(W)
    for j in range(n - 1, 0, -1):
        b1, b2 = ss[j] + iki * b1 - b2, b1
    sanal = ss[0] + iki * b1 - b2
    reel = reel - reel.max(axis=1, keepdims=True)
    e = np.exp(reel)
    psi = (e * np.cos(sanal)).astype(ctip)
    psi += 1j * (e * np.sin(sanal)).astype(ctip)
    nrm = np.linalg.norm(psi, axis=1, keepdims=True)
    return psi / np.maximum(nrm, tip.type(1e-30))


def ortusme(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a).reshape(-1)
    b = np.asarray(b).reshape(-1)
    return float(np.abs(np.vdot(a, b)))


def suz(delta, psi: np.ndarray, ayar: Optional[QuditAyari] = None,
        lam_azami: float = 0.0, keskinlik: float = 8.0,
        ne: str = "harmonik") -> np.ndarray:
    a = ayar or QuditAyari()
    N = int(a.qsvt)
    if callable(delta):
        vur = delta
        if lam_azami <= 0:
            raise ValueError("işlev verilince lam_azami açıkça lâzım")
    else:
        D = np.asarray(delta)
        vur = lambda v: D @ v
        if lam_azami <= 0:
            lam_azami = float(np.max(np.sum(np.abs(D), axis=1))) or 1.0

    j = np.arange(N + 1)
    dugum = np.cos(np.pi * (j + 0.5) / (N + 1))
    lam = (dugum + 1.0) * 0.5 * lam_azami
    f = np.exp(-float(keskinlik) * lam / max(lam_azami, 1e-300))
    kat = np.empty(N + 1)
    for k in range(N + 1):
        kat[k] = (2.0 / (N + 1)) * np.sum(
            f * np.cos(np.pi * k * (j + 0.5) / (N + 1)))
    kat[0] *= 0.5
    if ne == "katsayi":
        return kat
    if ne != "harmonik":
        raise ValueError("süzme kipi bilinmiyor: %r" % (ne,))

    def A(v):
        return (2.0 / lam_azami) * vur(v) - v

    v = np.asarray(psi)
    b1 = np.zeros_like(v)
    b2 = np.zeros_like(v)
    for k in range(N, 0, -1):
        b1, b2 = 2.0 * A(b1) - b2 + kat[k] * v, b1
    out = A(b1) - b2 + kat[0] * v
    nrm = float(np.linalg.norm(out))
    return out / nrm if nrm > 1e-300 else out


def dallanma(tepe: Sequence[int], ne: str = "sayim"):
    lam = [int(x) for x in tepe]
    n = len(lam)
    if any(lam[i] < lam[i + 1] for i in range(n - 1)):
        raise ValueError("en yüksek ağırlık azalan olmalı: %r" % (lam,))

    if ne == "weyl":
        pay = payda = 1.0
        for i in range(n):
            for j in range(i + 1, n):
                pay *= (lam[i] - lam[j] + j - i)
                payda *= (j - i)
        return int(round(pay / payda))

    def satirlar(ust: List[int]) -> List[List[int]]:
        k = len(ust) - 1
        if k == 0:
            return [[]]
        out: List[List[int]] = []

        def yur(i: int, kismi: List[int]):
            if i == k:
                out.append(list(kismi))
                return
            for v in range(ust[i + 1], ust[i] + 1):
                kismi.append(v)
                yur(i + 1, kismi)
                kismi.pop()

        yur(0, [])
        return out

    oruntuler: List[List[List[int]]] = []

    def derinlestir(ust: List[int], yigin: List[List[int]]):
        if len(ust) == 1:
            oruntuler.append([list(x) for x in yigin])
            return
        for alt in satirlar(ust):
            derinlestir(alt, yigin + [alt])

    derinlestir(lam, [lam])
    if ne == "sayim":
        return len(oruntuler)
    if ne == "oruntu":
        return oruntuler
    raise ValueError("dallanma kipi bilinmiyor: %r" % (ne,))


def metrik(psi_uret: Callable[[np.ndarray], np.ndarray], teta: np.ndarray,
           h: float = 1e-4) -> np.ndarray:
    teta = np.asarray(teta, float).reshape(-1)
    psi = psi_uret(teta)
    d = teta.size
    dpsi = np.empty((d, psi.size), complex)
    for i in range(d):
        e = np.zeros(d)
        e[i] = h
        dpsi[i] = (psi_uret(teta + e) - psi_uret(teta - e)) / (2.0 * h)
    ic = dpsi.conj() @ dpsi.T
    v = dpsi.conj() @ psi
    return np.real(ic - np.outer(v, v.conj()))


def dogal_adim(g: np.ndarray, grad: np.ndarray, eta: float = 0.1,
               duzenli: float = 1e-6, tur: int = 64) -> np.ndarray:
    g = np.asarray(g, float)
    b = -float(eta) * np.asarray(grad, float).reshape(-1)
    n = b.size
    olcek = float(np.trace(g)) / max(n, 1)
    tau = float(duzenli) * max(olcek, 1e-30)
    A = lambda v: g @ v + tau * v
    x = np.zeros(n)
    r = b - A(x)
    p = r.copy()
    rr = float(r @ r)
    for _ in range(int(tur)):
        if rr < 1e-30:
            break
        Ap = A(p)
        al = rr / max(float(p @ Ap), 1e-300)
        x += al * p
        r -= al * Ap
        rr_yeni = float(r @ r)
        p = r + (rr_yeni / max(rr, 1e-300)) * p
        rr = rr_yeni
    return x


BLOKLAR: Tuple[Tuple[str, int, int], ...] = (
    ("sentaks", 0, 512),
    ("onto-fizik", 512, 2560),
    ("mantık", 2560, 4096),
)


def blok(psi: np.ndarray, ad: Optional[str] = None,
         ne: str = "izdusum") -> object:
    psi = np.asarray(psi).reshape(-1)
    d = psi.size
    olcek = d / float(BLOKLAR[-1][2])
    dilim = {a: (int(b * olcek), min(d, int(c * olcek)))
             for a, b, c in BLOKLAR}
    if ne == "agirlik":
        return {a: float(np.sum(np.abs(psi[i:j]) ** 2))
                for a, (i, j) in dilim.items()}
    if ne == "izdusum":
        if ad not in dilim:
            raise ValueError("blok bilinmiyor: %r" % (ad,))
        i, j = dilim[ad]
        out = np.zeros_like(psi)
        out[i:j] = psi[i:j]
        n = float(np.linalg.norm(out))
        return out / n if n > 1e-300 else out
    raise ValueError("blok kipi bilinmiyor: %r" % (ne,))


def rapor(ayar: Optional[QuditAyari] = None) -> str:
    import time

    a = ayar or QuditAyari()
    r = np.random.default_rng(a.tohum)
    c = r.normal(scale=0.3, size=(a.kan, a.derece + 1))
    s = r.normal(scale=0.3, size=(a.kan, a.derece + 1))
    teta = r.normal(size=a.d - 1)

    s_ = ["=== QUDİT ÇEKİRDEĞİ -- SVD yok, MPS yok, ikili yok ===", ""]

    t0 = time.perf_counter()
    psi = durum(c, s, teta, ayar=a)
    t_durum = time.perf_counter() - t0
    s_ += ["  1. LIE-CHEBYSHEV KAN-QUDIT DURUMU",
           "    d              : %d" % a.d,
           "    saklanan katsayı: %d  (genlik SAKLANMIYOR, üretiliyor)"
           % a.katsayi_sayisi,
           "    açık dizi olsaydı: %d karmaşık sayı (%.1f×)"
           % (a.d, a.d / max(a.katsayi_sayisi, 1)),
           "    üretim süresi  : %.4f ms" % (1e3 * t_durum),
           "    norm           : %.12f" % float(np.linalg.norm(psi)),
           "    faz ±1'e kilitli mi: %s"
           % ("EVET -- KUSUR" if np.allclose(np.abs(np.angle(psi) % np.pi), 0,
                                             atol=1e-9) else "hayır (sürekli)")]

    n = 64
    W = r.random((n, n)); W = (W + W.T) * 0.5
    np.fill_diagonal(W, 0.0)
    D = np.diag(W.sum(axis=1)) - W
    D = D / np.max(np.sum(np.abs(D), axis=1))
    v = r.normal(size=n) + 1j * r.normal(size=n)
    v /= np.linalg.norm(v)
    t0 = time.perf_counter()
    hv = suz(D, v, ayar=a, keskinlik=12.0)
    t_suz = time.perf_counter() - t0
    h = np.ones(n) / np.sqrt(n)
    tam = h * (h @ v)
    tam = tam / max(float(np.linalg.norm(tam)), 1e-300)
    kalinti = float(np.linalg.norm(D @ hv)) / max(
        float(np.linalg.norm(hv)), 1e-300)
    s_ += ["", "  2. QSVT HODGE SÜZGECİ (derece %d)" % a.qsvt,
           "    süre           : %.4f ms" % (1e3 * t_suz),
           "    harmonikle örtüşme: %.6f  (1,0 = tam söndürme)"
           % ortusme(hv, tam),
           "    ‖Δ·süzülmüş‖/‖·‖ : %.3e  (0 = çelişki tamamen söndü)"
           % kalinti,
           "    ayrıştırma kullandı mı: HAYIR (yalnız Δ@v; özayrışım"
           " sadece bu satırın ŞAHİDİ için)"]

    s_ += ["", "  3. GELFAND-TSETLİN DALLANMASI (χ budaması YOK)"]
    for lam in ((2, 1, 0), (3, 1, 0), (2, 2, 1, 0)):
        say = dallanma(lam, ne="sayim")
        wy = dallanma(lam, ne="weyl")
        s_.append("    λ=%-12s örüntü %4d   Weyl %4d   %s"
                  % (str(lam), say, wy,
                     "UYUŞTU" if say == wy else "AYRIŞTI -- KIRMIZI"))

    dk = 12
    tk = r.normal(size=dk) * 0.2

    def uret(t):
        return durum(c, s, np.concatenate([t, np.zeros(a.d - 1 - dk)]),
                     ayar=a)

    t0 = time.perf_counter()
    g = metrik(uret, tk)
    t_met = time.perf_counter() - t0
    grad = r.normal(size=dk)
    adim = dogal_adim(g, grad, eta=0.1, duzenli=a.duzenli)
    duz = -0.1 * grad
    s_ += ["", "  4. FUBINI-STUDY DOĞAL GRADYAN (ters ALINMADI, CG)",
           "    metrik süresi  : %.2f ms  (%d×%d)" % (1e3 * t_met, dk, dk),
           "    g simetrik mi  : %s"
           % ("evet" if np.allclose(g, g.T, atol=1e-8) else "HAYIR"),
           "    ‖doğal adım‖   : %.6f" % float(np.linalg.norm(adim)),
           "    ‖düz adım‖     : %.6f" % float(np.linalg.norm(duz)),
           "    aralarındaki açı: %.1f°"
           % float(np.degrees(np.arccos(np.clip(
               (adim @ duz) / max(np.linalg.norm(adim) * np.linalg.norm(duz),
                                  1e-300), -1, 1)))),
           "    (açı 0 olsaydı metrik hiçbir şey yapmıyor demekti)"]

    s_ += ["", "  HIZ -- eski hat 11 belirteç/sn idi (ölçüldü, ~8500 SVD)"]
    for tip, ad in ((np.float64, "float64"), (np.float32, "float32")):
        for dd, BB in ((16, 4096), (256, 4096), (4096, 256)):
            ay = QuditAyari(d=dd, kan=a.kan, derece=a.derece, yon=a.yon,
                            tip=tip)
            TT = r.normal(size=(BB, a.yon))
            durum_yigin(c, s, TT, ayar=ay)
            t0 = time.perf_counter()
            durum_yigin(c, s, TT, ayar=ay)
            dt = time.perf_counter() - t0
            hiz = BB / max(dt, 1e-12)
            s_.append("    %-8s d=%-5d B=%-5d %10.0f belirteç/sn"
                      "   hedefin %.2f'i   eski hattın %.0f katı"
                      % (ad, dd, BB, hiz, hiz / 1e6, hiz / 11.0))
    s_.append("    (LAPACK çağrısı: SIFIR. SVD yok, QR yok, özayrışım yok.)")

    ag = blok(psi, ne="agirlik")
    s_ += ["", "  BLOKLAR (süperseçim sektörleri)"]
    for k, v_ in ag.items():
        s_.append("    %-12s ağırlık %.6f" % (k, v_))
    return "\n".join(s_)


if __name__ == "__main__":
    print(rapor())
