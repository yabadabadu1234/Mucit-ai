from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["karo_vur", "bant_vur", "faz_vur", "cift_lif_vur",
           "senedi_uygula", "basa_don",
           "bit_turevi_vur", "egim_uretec", "egim_ek_durum", "egim_ikiz",
           "mutabakat", "senet_kapsami", "senet_ileri_sadakati"]


def karo_vur(psi: np.ndarray, lif: Tuple[int, ...], k: int,
             M: np.ndarray) -> np.ndarray:
    B = psi.shape[0]
    T = psi.reshape((B,) + tuple(lif))
    eksen = int(k) + 1
    X = np.moveaxis(T, eksen, -1)
    Y = X @ np.asarray(M, complex).T
    return np.moveaxis(Y, -1, eksen).reshape(B, -1)


def bant_vur(psi: np.ndarray, bi: int, bj: int,
             G: np.ndarray, sifirla: bool = False) -> np.ndarray:
    d = psi.shape[1]
    idx = np.arange(d)
    m0 = idx[((idx & int(bi)) == 0) & ((idx & int(bj)) == 0)]
    yer = (m0, m0 | int(bj), m0 | int(bi), m0 | int(bi) | int(bj))
    G = np.asarray(G, complex).reshape(4, 4)
    a = [psi[:, y] for y in yer]
    out = np.zeros_like(psi) if sifirla else psi.copy()
    for r in range(4):
        out[:, yer[r]] = sum(G[r, c] * a[c] for c in range(4))
    return out


def faz_vur(psi: np.ndarray, q: np.ndarray,
            ters: bool = False) -> np.ndarray:
    e = np.asarray(q, np.int64) % 4
    carpan = np.power(1j, -e if ters else e)
    return psi * carpan


def senedi_uygula(psi: np.ndarray, lif: Tuple[int, ...], kayit,
                  ters: bool = False, es: bool = False) -> np.ndarray:
    tur, yer, G = kayit
    if tur == "karo":
        M = np.asarray(G, complex)
        return karo_vur(psi, lif, int(yer[0]),
                        M.conj().T if ters else M)
    if tur == "bant":
        M = np.asarray(G, complex).reshape(4, 4)
        return bant_vur(psi, int(yer[0]), int(yer[1]),
                        M.conj().T if ters else M)
    if tur == "faz":
        return faz_vur(psi, G, ters=ters)
    if tur == "ölçek":
        n = np.maximum(np.asarray(G, float), 1e-300)
        n = n.reshape(-1, 1) if n.size == psi.shape[0] else n.reshape(1, -1)
        return psi * n if (ters and not es) else psi / n
    if tur == "maske":
        m = np.asarray(G, bool)
        out = psi.copy()
        assert m.shape[-1] == psi.shape[-1], (
            "maske %d, durum %d -- parite dizini yazmaç ebadında olmalı"
            % (m.shape[-1], psi.shape[-1]))
        out[..., m] = 0.0
        return out
    if tur in ("durum", "başlangıç"):
        return np.asarray(G, complex).copy()
    if tur == "sektör":
        i, j = int(yer[0]), int(yer[1])
        M = np.asarray(G, complex)
        out = psi.copy()
        out[:, i:j] = psi[:, i:j] @ (M.conj() if ters else M.T)
        return out
    if tur == "çift_lif":
        ki, kj, bi, bj = (int(yer[0]), int(yer[1]), int(yer[2]),
                          int(yer[3]))
        M = np.asarray(G, complex).reshape(4, 4)
        return cift_lif_vur(psi, lif, ki, kj, bi, bj,
                            M.conj().T if ters else M)
    raise ValueError("senet kaydının türü bilinmiyor: %r" % (tur,))


def cift_lif_vur(psi: np.ndarray, lif: Tuple[int, ...], ki: int, kj: int,
                 bi: int, bj: int, G: np.ndarray) -> np.ndarray:
    B = psi.shape[0]
    T = psi.reshape((B,) + tuple(lif))
    F = np.moveaxis(T, (int(ki) + 1, int(kj) + 1), (-2, -1))
    sekil = F.shape
    F = F.reshape(B, -1, sekil[-2], sekil[-1]).copy()
    ni, nj = sekil[-2], sekil[-1]
    G = np.asarray(G, complex).reshape(4, 4)
    for x in range(ni):
        if x & int(bi):
            continue
        for y in range(nj):
            if y & int(bj):
                continue
            idx = [(x, y), (x, y | int(bj)), (x | int(bi), y),
                   (x | int(bi), y | int(bj))]
            v = np.stack([F[:, :, a, b] for a, b in idx], axis=2)
            v = v @ G.T
            for m, (a, b) in enumerate(idx):
                F[:, :, a, b] = v[:, :, m]
    F = F.reshape(sekil)
    return np.moveaxis(F, (-2, -1),
                       (int(ki) + 1, int(kj) + 1)).reshape(B, -1)


def bit_turevi_vur(psi: np.ndarray, lif: Tuple[int, ...], k: int,
                   alt: int, dG: np.ndarray) -> np.ndarray:
    B = psi.shape[0]
    T = psi.reshape((B,) + tuple(lif))
    n = int(lif[int(k)])
    b = 1 << int(alt)
    if b >= n:
        return np.zeros_like(psi)
    idx = np.arange(n)
    dus = idx[(idx & b) == 0]
    ust = dus | b
    eksen = int(k) + 1
    A = np.take(T, dus, axis=eksen)
    C = np.take(T, ust, axis=eksen)
    out = np.zeros_like(T)
    dd = [slice(None)] * T.ndim
    du = [slice(None)] * T.ndim
    dd[eksen] = dus
    du[eksen] = ust
    dG = np.asarray(dG, complex).reshape(2, 2)
    out[tuple(dd)] = dG[0, 0] * A + dG[0, 1] * C
    out[tuple(du)] = dG[1, 0] * A + dG[1, 1] * C
    return out.reshape(B, -1)


def kosegen_vur(psi: np.ndarray, dizin: np.ndarray,
                deger: np.ndarray) -> np.ndarray:
    out = np.zeros_like(psi)
    i = np.asarray(dizin, np.int64)
    out[:, i] = psi[:, i] * np.asarray(deger, complex)[None, :]
    return out


def _turev_vur(psi: np.ndarray, lif: Tuple[int, ...], turev) -> np.ndarray:
    tur = str(turev[0])
    if tur == "köşegen":
        return kosegen_vur(psi, turev[1], turev[2])
    if tur == "bit":
        return bit_turevi_vur(psi, lif, int(turev[1]), int(turev[2]),
                              turev[3])
    if tur == "karo4":
        return karo_vur(psi, lif, int(turev[1]), turev[2])
    if tur == "bant4":
        return bant_vur(psi, int(turev[1]), int(turev[2]), turev[3],
                        sifirla=True)
    raise ValueError("türev tarifi bilinmiyor: %r" % (tur,))


def senet_kapsami(iz, n_par: int, defter=None,
                  tahsis: int = 0, kaydirma: int = 0) -> Dict[str, Any]:
    kapsanan = {int(b[1]) for b in iz.baglanti}
    fotograf = sum(1 for k in iz.senet if str(k[0]) == "durum")
    o: Dict[str, Any] = {
        "kapı": len(iz.senet), "bağlantı": len(iz.baglanti),
        "durum_saklaması": int(fotograf),
        "kapsanan_parametre": len(kapsanan),
        "toplam_parametre": int(n_par),
        "tahsis_edilen": int(tahsis),
        "üretecsiz": int(iz.uretecsiz),
        "bağ_reddi": int(getattr(iz, "bag_reddi", 0)), "yetim": ()}
    if not defter:
        return o
    yetim = []
    k = int(kaydirma)
    for ad, (bas, kac) in defter.items():
        acik = sum(1 for i in range(int(bas), int(bas) + int(kac))
                   if i not in kapsanan and (k + i) not in kapsanan)
        if acik:
            yetim.append((int(acik), str(ad)))
    yetim.sort(reverse=True)
    o["yetim"] = tuple(yetim)
    return o


def egim_uretec(iz, lif: Tuple[int, ...], psi_son: np.ndarray,
                H: np.ndarray, n_par: int) -> np.ndarray:
    g = np.zeros(int(n_par), float)
    lam = psi_son * H[None, :]
    for (_no, par, olcek, turev) in iz.baglanti:
        dpsi = _turev_vur(psi_son, lif, turev)
        g[int(par)] += 2.0 * float(olcek) * float(
            np.real(np.sum(np.conj(lam) * dpsi)))
    return g


def egim_ek_durum(iz, lif: Tuple[int, ...], psi_son: np.ndarray,
                  H: np.ndarray, n_par: int
                  ) -> Tuple[np.ndarray, np.ndarray]:
    g = np.zeros(int(n_par), float)
    metrik = np.zeros(int(n_par), float)
    bag: Dict[int, List[Tuple[int, float, Any]]] = {}
    for (no, par, olcek, turev) in iz.baglanti:
        bag.setdefault(int(no), []).append((int(par), float(olcek), turev))
    psi = psi_son.copy()
    lam = psi_son * H[None, :]
    for i in range(len(iz.senet) - 1, -1, -1):
        kayit = iz.senet[i]
        if str(kayit[0]) in ("durum", "başlangıç"):
            psi = np.asarray(kayit[2], complex).copy()
            continue
        onceki = senedi_uygula(psi, lif, kayit, ters=True)
        for (par, olcek, turev) in bag.get(i, ()):
            dpsi = _turev_vur(onceki, lif, turev)
            g[int(par)] += 2.0 * float(olcek) * float(
                np.real(np.sum(np.conj(lam) * dpsi)))
            ust = float(np.real(np.sum(np.conj(dpsi) * dpsi)))
            ic = complex(np.sum(np.conj(onceki) * dpsi))
            metrik[int(par)] += (float(olcek) ** 2) * max(
                0.0, ust - abs(ic) ** 2)
        psi = onceki
        lam = senedi_uygula(lam, lif, kayit, ters=True, es=True)
    return g, metrik


def basa_don(iz, lif: Tuple[int, ...],
             psi_son: np.ndarray) -> np.ndarray:
    psi = psi_son.copy()
    for i in range(len(iz.senet) - 1, -1, -1):
        psi = senedi_uygula(psi, lif, iz.senet[i], ters=True)
    return psi


def durum_yerleri(iz) -> List[int]:
    return [i for i, k in enumerate(iz.senet) if str(k[0]) == "durum"]


def senet_ileri_sadakati(iz, lif: Tuple[int, ...],
                         psi_son: np.ndarray) -> float:
    bas = [k[2] for k in iz.senet if str(k[0]) == "başlangıç"]
    if not bas:
        return float("nan")
    psi = np.asarray(bas[0], complex).copy()
    gordu = False
    for kayit in iz.senet:
        if str(kayit[0]) == "başlangıç":
            gordu = True
            continue
        if not gordu or str(kayit[0]) == "durum":
            continue
        psi = senedi_uygula(psi, lif, kayit)
    payda = max(float(np.linalg.norm(psi_son)), 1e-300)
    return float(np.linalg.norm(psi - psi_son) / payda)


def egim_ikiz(iz, lif: Tuple[int, ...], psi_son: np.ndarray,
              H: np.ndarray, yon: np.ndarray) -> float:
    bag: Dict[int, List[Tuple[int, float, Any]]] = {}
    for (no, par, olcek, turev) in iz.baglanti:
        bag.setdefault(int(no), []).append((int(par), float(olcek), turev))
    psi = basa_don(iz, lif, psi_son)
    dpsi = np.zeros_like(psi)
    v = np.asarray(yon, float).reshape(-1)
    for i, kayit in enumerate(iz.senet):
        if str(kayit[0]) in ("durum", "başlangıç"):
            continue
        katki = None
        for (par, olcek, turev) in bag.get(i, ()):
            if int(par) < v.size and v[int(par)] != 0.0:
                ek = (float(olcek) * float(v[int(par)])
                      * _turev_vur(psi, lif, turev))
                katki = ek if katki is None else katki + ek
        psi = senedi_uygula(psi, lif, kayit)
        dpsi = senedi_uygula(dpsi, lif, kayit)
        if katki is not None:
            dpsi = dpsi + katki
    return 2.0 * float(np.real(np.sum(np.conj(psi * H[None, :]) * dpsi)))


def mutabakat(g_uretec: np.ndarray, g_ek: np.ndarray, ikiz: float,
              yon: np.ndarray) -> Dict[str, float]:
    v = np.asarray(yon, float).reshape(-1)
    a = float(np.dot(np.asarray(g_uretec, float), v))
    b = float(np.dot(np.asarray(g_ek, float), v))
    payda = max(abs(ikiz), 1e-30)
    return {"üreteç·yön": a, "ek_durum·yön": b, "ikiz": float(ikiz),
            "ek_durum_ikiz_farkı": abs(b - ikiz) / payda,
            "üreteç_ikiz_farkı": abs(a - ikiz) / payda,
            "üreteç_normu": float(np.linalg.norm(g_uretec)),
            "ek_durum_normu": float(np.linalg.norm(g_ek))}
