from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

import numpy as np

__all__ = ["NqsAyari", "ChebyshevKan", "chebyshev_t", "chebyshev_u",
           "gcl_dugumleri", "fct_katsayilari", "nqs_beyani", "nqs_metni"]


@dataclass
class NqsAyari:

    dugum: int = 64
    derece: int = 12
    tohum: int = 0
    havuz_bayti: int = 4
    havuz_haddi: int = 1 << 20


def chebyshev_t(u: np.ndarray, derece: int) -> np.ndarray:
    u = np.asarray(u, float)
    d = int(derece)
    out = np.empty((d + 1,) + u.shape, float)
    out[0] = 1.0
    if d >= 1:
        out[1] = u
    for j in range(1, d):
        out[j + 1] = 2.0 * u * out[j] - out[j - 1]
    return out


def chebyshev_u(u: np.ndarray, derece: int) -> np.ndarray:
    u = np.asarray(u, float)
    d = int(derece)
    out = np.empty((d + 1,) + u.shape, float)
    out[0] = 1.0
    if d >= 1:
        out[1] = 2.0 * u
    for j in range(1, d):
        out[j + 1] = 2.0 * u * out[j] - out[j - 1]
    return out


def gcl_dugumleri(kac: int) -> np.ndarray:
    n = max(2, int(kac))
    j = np.arange(n, dtype=float)
    return np.cos(math.pi * j / (n - 1))


def fct_katsayilari(deger: np.ndarray, derece: int) -> np.ndarray:
    y = np.asarray(deger, float).reshape(-1)
    n = y.size
    u = gcl_dugumleri(n)
    T = chebyshev_t(u, int(derece))
    w = np.full(n, 2.0)
    w[0] = w[-1] = 1.0
    pay = (T * (y * w)[None, :]).sum(axis=1)
    payda = (T * T * w[None, :]).sum(axis=1)
    return pay / np.maximum(payda, 1e-300)


class ChebyshevKan:

    def __init__(self, taban: int, qudit: int,
                 ayar: Optional[NqsAyari] = None) -> None:
        self.ayar = ayar or NqsAyari()
        self.taban = max(2, int(taban))
        self.qudit = max(int(qudit), int(self.ayar.havuz_haddi))
        K = int(self.ayar.dugum)
        D = int(self.ayar.derece)
        r = np.random.default_rng(int(self.ayar.tohum))
        self.C = r.normal(scale=1.0 / math.sqrt(D + 1), size=(K, D + 1))
        self.S = r.normal(scale=1.0 / math.sqrt(D + 1), size=(K, D + 1))
        self.havuz_koordinat = r.normal(scale=1.0, size=self.qudit)
        assert self.havuz_koordinat.size == self.qudit, (
            "tohum havuzu qudit sayısınca olmalı (ferman 2-T)")
        self.havuz_fazi = r.uniform(-1.0, 1.0, size=K)
        self._son_z = 1.0
        self._cagri = 0
        self._asikin = 0

    @property
    def katsayi_adedi(self) -> int:
        return int(self.C.size + self.S.size)

    @property
    def parametre_adedi(self) -> int:
        return int(self.katsayi_adedi + self.havuz_koordinat.size
                   + self.havuz_fazi.size)

    def havuzu_buyut(self, n: int) -> None:
        n = int(n)
        if n <= self.havuz_koordinat.size:
            return
        r = np.random.default_rng(int(self.ayar.tohum) + 1)
        ek = r.normal(scale=1.0, size=n - self.havuz_koordinat.size)
        self.havuz_koordinat = np.concatenate([self.havuz_koordinat, ek])
        self.qudit = int(self.havuz_koordinat.size)

    def _vecih(self, basamak: np.ndarray) -> np.ndarray:
        b = np.asarray(basamak, np.int64)
        x = 2.0 * (b.astype(float) / float(self.taban - 1)) - 1.0
        n = x.shape[-1]
        self.havuzu_buyut(n)
        c = self.havuz_koordinat[:n]
        iz = (x * c[None, :]).sum(axis=-1) / float(n)
        u = iz[..., None] + self.havuz_fazi[None, :]
        return np.clip(u, -1.0, 1.0)

    def genlik(self, basamak: np.ndarray) -> np.ndarray:
        u = self._vecih(basamak)
        D = int(self.ayar.derece)
        T = chebyshev_t(u, D)
        U = chebyshev_u(u, D)
        reel = np.einsum("kj,jnk->n", self.C, T, optimize=True)
        sanal = np.einsum("kj,jnk->n", self.S, U, optimize=True)
        reel = reel - float(reel.max())
        self._cagri += 1
        self._asikin += 1
        buyuk = np.exp(reel)
        ceyrek = np.rint(sanal * 2.0 / math.pi).astype(np.int64) % 4
        doner = np.take(
            np.array([1.0 + 0j, 0.0 + 1j, -1.0 + 0j, 0.0 - 1j]), ceyrek)
        psi = buyuk * doner
        z = float(np.linalg.norm(psi))
        self._son_z = z
        assert z > 0.0 and np.isfinite(z), (
            "NQS genliği tamamen söndü (Z=%r): kapalı form bir durum "
            "üretemedi, sessizce geçilemez (ferman 5)" % (z,))
        return psi / z

    def vektor(self) -> np.ndarray:
        return np.concatenate([self.C.reshape(-1), self.S.reshape(-1),
                               self.havuz_koordinat, self.havuz_fazi])

    def yukle(self, v: np.ndarray) -> None:
        v = np.asarray(v, float).reshape(-1)
        assert v.size == self.parametre_adedi, (
            "NQS parametre vektörü katsayı+havuz ebadında olmalı: "
            "%d ≠ %d" % (v.size, self.parametre_adedi))
        n1 = self.C.size
        n2 = n1 + self.S.size
        n3 = n2 + self.havuz_koordinat.size
        self.C = v[:n1].reshape(self.C.shape).copy()
        self.S = v[n1:n2].reshape(self.S.shape).copy()
        self.havuz_koordinat = v[n2:n3].copy()
        self.havuz_fazi = v[n3:].copy()

    def hazineye(self) -> Dict[str, np.ndarray]:
        return {"nqs.C": self.C.copy(), "nqs.S": self.S.copy(),
                "nqs.havuz_koordinat": self.havuz_koordinat.copy(),
                "nqs.havuz_fazı": self.havuz_fazi.copy()}

    def hazineden(self, agirlik) -> bool:
        if not agirlik:
            return False
        C = agirlik.get("nqs.C")
        S = agirlik.get("nqs.S")
        k = agirlik.get("nqs.havuz_koordinat")
        f = agirlik.get("nqs.havuz_fazı")
        if C is None or S is None or k is None or f is None:
            return False
        C = np.asarray(C, float)
        S = np.asarray(S, float)
        if C.shape != self.C.shape or S.shape != self.S.shape:
            return False
        self.C, self.S = C.copy(), S.copy()
        self.havuz_koordinat = np.asarray(k, float).reshape(-1).copy()
        self.havuz_fazi = np.asarray(f, float).reshape(-1).copy()
        return True

    def beyan(self) -> Dict[str, Any]:
        kat_bayt = self.katsayi_adedi * 8
        havuz_bayt = self.qudit * int(self.ayar.havuz_bayti)
        return {"düğüm": int(self.ayar.dugum),
                "derece": int(self.ayar.derece),
                "katsayı": int(self.katsayi_adedi),
                "katsayı_bayt": int(kat_bayt),
                "qudit": int(self.qudit),
                "havuz_bayt": int(havuz_bayt),
                "parametre": int(self.parametre_adedi),
                "çağrı": int(self._cagri),
                "aşkın_çağrı": int(self._asikin),
                "son_Z": float(self._son_z),
                "taban": int(self.taban)}


def nqs_beyani(kan: Optional[ChebyshevKan]) -> Dict[str, Any]:
    if kan is None:
        return {"düğüm": 0, "derece": 0, "katsayı": 0, "qudit": 0,
                "parametre": 0, "katsayı_bayt": 0, "havuz_bayt": 0,
                "çağrı": 0, "aşkın_çağrı": 0, "son_Z": 0.0,
                "hüküm": "KAN-NQS KURULMADI"}
    return kan.beyan()


def nqs_metni(b: Optional[Dict[str, Any]] = None) -> str:
    d = dict(b or nqs_beyani(None))
    if "hüküm" in d:
        return "  KAN-NQS: %s" % d["hüküm"]
    return "\n".join([
        "  KAN-NQS GENLİĞİ (ferman 2-T: genlik açık dizi değil fonksiyon)",
        "    düğüm × derece : %d × %d   → %d katsayı   = %.1f KB"
        % (d["düğüm"], d["derece"], d["katsayı"],
           d["katsayı_bayt"] / 1e3),
        "    tohum havuzu   : %d qudit   = %.1f MB   (qudit başına 4 bayt)"
        % (d["qudit"], d["havuz_bayt"] / 1e6),
        "    parametre      : %d   (katsayı + havuz)" % d["parametre"],
        "    MERTEBE: genlik ÜRETİMİ O(1) -- katsayı adedi qudit"
        " sayısından bağımsızdır;",
        "    HAVUZ ise O(N)'dir. Toptan O(1) denmez (ferman 5).",
        "    T_j ve U_j TEKRARLAMAYLA hesaplanır: cos/arccos YOK.",
        "    Dıştaki üstel AŞKINDIR ve sayılır: %d çağrı (ferman 2-J)."
        % d["aşkın_çağrı"],
        "    son Z (normalize edilen küme üstünde) : %.6e" % d["son_Z"],
        "    AÇIK DİZİ YOKTUR: q^N genlik hiçbir yerde tutulmaz.",
    ])
