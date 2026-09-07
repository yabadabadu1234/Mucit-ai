from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

import math

import numpy as np

from .galois import ayrik_faz
from .matchgate import matchgate_mi

__all__ = ["QuditAyar", "QuditYazmac", "Iz"]


class Iz:

    def __init__(self) -> None:
        self.kapi = 0
        self.kesme = 0.0
        self.defter: List[Tuple[str, str]] = []

    def not_dus(self, meleke: str, mesaj: str = "") -> None:
        self.defter.append((str(meleke), str(mesaj)))


@dataclass
class QuditAyar:

    d: int = 4096
    lif: Tuple[int, ...] = (16, 16, 16)
    yigin: int = 1
    kulli_alanlar: Tuple[Tuple[str, int], ...] = (
        ("makam", 3), ("mizan", 4), ("tenakuz", 2), ("tasdik", 2),
        ("sukut", 1), ("nakz", 2), ("kelam", 4), ("kaide", 12),
        ("orak", 1), ("gaye", 2), ("tertip", 4),
    )
    yerel_yuva: int = 1
    tip: object = np.complex128
    tohum: int = 0
    motor: str = "galois"
    faz_mertebesi: int = 16
    hat: str = "c"
    hat_bandi: int = 0

    def __post_init__(self):
        if int(np.prod(self.lif)) != int(self.d):
            raise ValueError("lifler çarpımı d'ye eşit olmalı: %s ≠ %d"
                             % (self.lif, self.d))


class QuditYazmac:

    def __init__(self, ayar: Optional[QuditAyar] = None,
                 veri_lifi: int = 4,
                 n: Optional[int] = None, bag: Optional[int] = None,
                 tohum: int = 0, tip=None, obek: Optional[int] = None,
                 yigin: Optional[int] = None) -> None:
        if ayar is None and n is not None:
            k = int(np.ceil(np.log2(max(int(n), 2))))
            k = int(min(max(k, 1), 20))
            ayar = QuditAyar(d=1 << k, lif=(1 << k,), tohum=int(tohum),
                             yigin=int(yigin or 1))
            veri_lifi = k
        self.ayar = ayar or QuditAyar()
        a = self.ayar
        self._veri_lifi = int(veri_lifi)
        ns, carp = 0, 1
        for _x in tuple(a.lif):
            if carp >= int(veri_lifi):
                break
            carp *= int(_x)
            ns += 1
        self._n_satir = max(1, ns)
        self._yuva_onbellek: Dict[int, Tuple[int, int]] = {}
        self._ikinin_kuvveti = all(
            (int(x) & (int(x) - 1)) == 0 for x in tuple(self.ayar.lif))
        self._bolum_onbellek: Dict[int, Tuple[int, int]] = {}
        self._gecerli_onbellek: Dict[int, bool] = {}
        self._adres_np: Optional[Tuple[np.ndarray, np.ndarray,
                                       np.ndarray]] = None
        self._veri_yuvasi = max(1, int(a.lif[0]).bit_length() - 1)
        self._satir_yuva = self._veri_yuvasi + int(self.ayar.yerel_yuva)
        self._dusen_kapi = 0
        self._matchgate_kapi = 0
        r = np.random.default_rng(int(a.tohum))
        self.B = int(a.yigin)
        self.d = int(a.d)
        self._seviye = int(round(math.log2(self.d)))
        assert 2 ** self._seviye == self.d, (
            "bit düzlemi ikinin kuvvetini ister: d=%d" % self.d)
        self._bekleyen: Dict[int, np.ndarray] = {}
        from .qcekirdek import Bant
        self._bant = Bant(int(a.yigin), int(a.d), tuple(a.lif),
                          hat=str(a.hat), bant=int(a.hat_bandi))
        self._faz_bekleyen: Optional[np.ndarray] = None
        self._faz_toplam = np.zeros(int(a.d), np.int64)
        self._psi = np.full((self.B, self.d), 1.0 / np.sqrt(self.d),
                            dtype=a.tip)
        self._sadakat_log = 0.0
        self._kapi = 0
        self.iz = Iz()
        self.bag = 0
        toplam = sum(p for _, p in a.kulli_alanlar)
        self._sektor: Dict[str, Tuple[int, int]] = {}
        bas = 0
        for ad, pay in a.kulli_alanlar:
            gen = max(1, int(round(self.d * pay / toplam)))
            self._sektor[ad] = (bas, min(self.d, bas + gen))
            bas += gen
        if bas < self.d:
            ad = a.kulli_alanlar[-1][0]
            i, _ = self._sektor[ad]
            self._sektor[ad] = (i, self.d)

    @property
    def n(self) -> int:
        return self._n_satir * (self._veri_lifi
                                + int(self.ayar.yerel_yuva)) + self.d

    @property
    def A(self) -> np.ndarray:
        return self.lifli

    def tekil_yogunluklar(self, yuvalar: Sequence[int]) -> np.ndarray:
        idx = [int(y) for y in np.asarray(yuvalar, np.intp).reshape(-1)]
        if not idx:
            return np.zeros((self.B, 0, 2, 2))
        lif = tuple(self.ayar.lif)
        T = self.lifli
        out = np.zeros((self.B, len(idx), 2, 2), complex)
        for m, y in enumerate(idx):
            k, alt = self._lif_no(y)
            if not (0 <= k < len(lif)):
                out[:, m] = np.eye(2) * 0.5
                continue
            n = lif[k]
            b = 1 << int(alt)
            if b >= n:
                out[:, m] = np.eye(2) * 0.5
                continue
            X = np.moveaxis(T, k + 1, -1).reshape(self.B, -1, n)
            m0 = np.array([x for x in range(n) if not (x & b)])
            m1 = m0 | b
            a0, a1 = X[:, :, m0], X[:, :, m1]
            out[:, m, 0, 0] = np.sum(np.abs(a0) ** 2, axis=(1, 2))
            out[:, m, 1, 1] = np.sum(np.abs(a1) ** 2, axis=(1, 2))
            c = np.sum(a0 * a1.conj(), axis=(1, 2))
            out[:, m, 0, 1] = c
            out[:, m, 1, 0] = c.conj()
        iz = out[:, :, 0, 0] + out[:, :, 1, 1]
        return out / np.maximum(iz[:, :, None, None].real, 1e-300)

    def yuva_yogunluklari(self, yuvalar=None) -> np.ndarray:
        if yuvalar is None:
            yuvalar = list(range(min(8, self.d)))
        return self.tekil_yogunluklar(yuvalar)

    def blok_dagilimi(self, bas: int, kac: int) -> np.ndarray:
        k, alt = self._lif_no(int(bas))
        k = min(int(k), len(self.ayar.lif) - 1)
        n = self.ayar.lif[k]
        X = np.moveaxis(self.lifli, k + 1, -1).reshape(self.B, -1, n)
        p = np.sum(np.abs(X) ** 2, axis=1)
        m = min(1 << int(kac), n)
        parca = np.array_split(np.arange(n), m)
        P = np.stack([p[:, i].sum(axis=1) for i in parca], axis=1)
        return P / np.maximum(P.sum(axis=1, keepdims=True), 1e-300)

    def olcumler_yigin(self) -> Dict[str, np.ndarray]:
        o = self.olcumler()
        return {k: np.atleast_1d(np.asarray(v, float))
                for k, v in o.items()}

    def makam_derece_vektoru(self) -> np.ndarray:
        i, j = self.sektor("makam")
        return np.linspace(0.0, 1.0, j - i)

    def makam_dagilimi(self) -> np.ndarray:
        i, j = self.sektor("makam")
        p = np.abs(self.psi[:, i:j]) ** 2
        return p / np.maximum(p.sum(axis=1, keepdims=True), 1e-300)

    @property
    def lifli(self) -> np.ndarray:
        return self.psi.reshape((self.B,) + tuple(self.ayar.lif))

    def norm(self) -> np.ndarray:
        return np.sum(np.abs(self.psi) ** 2, axis=1)

    def normalize(self) -> np.ndarray:
        n = np.sqrt(np.maximum(self.norm(), 1e-300))
        self.psi = self.psi / n[:, None]
        return n

    def norm_hatasi(self) -> float:
        return float(np.max(np.abs(self.norm() - 1.0)))

    def sadakat(self) -> float:
        return 1.0

    def sadakat_kapi_basina(self, kapi: int = 1) -> float:
        return 1.0

    def ic_carpim(self, other=None) -> np.ndarray:
        o = self.psi if other is None else np.asarray(other)
        return np.sum(np.conj(self.psi) * o, axis=1)

    def supurme(self, *a, **k) -> None:
        self.iz.not_dus("süpürme", "quditte süpürme yok -- işlem yok")

    def takas(self, *a, **k) -> None:
        self.iz.not_dus("takas", "quditte takas yok -- işlem yok")

    def genlik(self, idx) -> np.ndarray:
        return self.psi[:, int(idx)]

    def deger(self, idx) -> np.ndarray:
        return self.genlik(idx)

    def parametre(self) -> int:
        return int(self.d * 2)

    def bayt(self) -> int:
        return int(self.psi.nbytes)

    def superpozisyona_sok(self) -> None:
        self.superpozisyon()

    def harman_kur(self, *a, **k) -> None:
        self.iz.not_dus("harman_kur", "qudit lif üniterleri kullanılır")

    def tek_kapi(self, G, yuvalar) -> None:
        for y in np.atleast_1d(np.asarray(yuvalar)).reshape(-1):
            self.tek(int(y), G)

    def tek_kapi_yuva(self, yuva: int, G) -> None:
        self.tek(int(yuva), G)

    def cift_kapi(self, G, ofset: int = 0, alt=None, ust=None) -> None:
        self.cift(int(ofset), G)

    def cift_kapi_yuva(self, i: int, j: int, G) -> None:
        self.uzak_cift(int(i), int(j), G)

    def tek_kapi_yigin(self, yuvalar, G) -> None:
        self.tek_yigin(yuvalar, G)

    def cift_kapi_yigin(self, sol_yuvalar, G) -> None:
        G = np.asarray(G)
        m = len(list(sol_yuvalar))
        if G.ndim == 2:
            G = np.broadcast_to(G, (m,) + G.shape)
        for y, g in zip(sol_yuvalar, G):
            self.cift(int(y), g)

    def sadakat_log(self) -> float:
        return float(self._sadakat_log)

    def lif_kapisi(self, k: int, G: np.ndarray) -> None:
        raise NotImplementedError(
            "``lif_kapisi`` imha edildi: n×n kapı graf motoruna geçmez. "
            "Bit düzlemi kapılarını kullanın (``tek``, ``cift``, "
            "``bit_kapisi``). Lif %d, kapı %r." % (k, np.shape(G)))

    def _bit(self, k: int, alt: int) -> int:
        _on, ard = self._bolum(int(k))
        return int(math.log2(ard)) + int(alt)

    def sektor_agirligi(self, ad: str) -> np.ndarray:
        i, j = self.sektor(ad)
        return np.sum(np.abs(self.psi[:, i:j]) ** 2, axis=1)


    def _eksen(self, k: int, alt: int) -> int:
        lif = tuple(self.ayar.lif)
        if not (0 <= int(k) < len(lif)):
            return 0
        n = int(lif[int(k)])
        if (1 << int(alt)) >= n:
            return 0
        return self._seviye - self._bit(int(k), int(alt))

    def _duzlem(self, T: np.ndarray, eksen: int, bit: int) -> np.ndarray:
        return T[(slice(None),) * eksen + (int(bit),)]

    def _bit_gorunumu(self) -> np.ndarray:
        T = self.psi.reshape((self.B,) + (2,) * self._seviye)
        assert np.shares_memory(T, self.psi), (
            "bit görünümü kopya çıktı -- kapı duruma vurmazdı")
        return T


    @property
    def psi(self) -> np.ndarray:
        if (self._bekleyen or self._faz_bekleyen is not None
                or not self._bant.bos_mu()):
            self._bosalt()
        return self._psi

    @psi.setter
    def psi(self, v) -> None:
        self._bekleyen.clear()
        self._faz_bekleyen = None
        self._psi = np.asarray(v)

    def _karolari_banda(self) -> None:
        if not self._bekleyen:
            return
        bekleyen, self._bekleyen = self._bekleyen, {}
        for k in sorted(bekleyen):
            self._bant.karo(int(k), bekleyen[k])

    def _bosalt(self) -> None:
        self._karolari_banda()
        if not self._bant.bos_mu():
            self._psi = np.ascontiguousarray(self._psi)
            self._bant.bosalt(self._psi)
        self._faz_indir()

    def _faz_indir(self) -> None:
        k = self._faz_bekleyen
        if k is None:
            return
        self._faz_bekleyen = None
        m = int(self.ayar.faz_mertebesi)
        if not np.any(k):
            return
        self._psi = np.asarray(
            ayrik_faz(self._psi, -k * (2.0 * math.pi / m), m),
            self._psi.dtype)

    def faz_birikimi(self) -> np.ndarray:
        return self._faz_toplam.copy()

    def _karo_indir(self, k: int, M: np.ndarray) -> None:
        n = int(self.ayar.lif[int(k)])
        on, ard = self._bolum(int(k))
        X = self._psi.reshape(self.B * on, n, ard)
        M = np.asarray(M, complex)
        if ard == 1:
            Y = X.reshape(-1, n) @ M.T
        else:
            Y = np.matmul(M, X)
        self._psi = np.ascontiguousarray(
            Y.reshape(self.B, self.d), dtype=self._psi.dtype)

    def _karo_vur(self, k: int, M: np.ndarray) -> None:
        self._faz_indir()
        M = np.asarray(M, complex)
        eski = self._bekleyen.get(int(k))
        self._bekleyen[int(k)] = M if eski is None else M @ eski
        self._kapi += 1
        self.iz.kapi += 1

    def _bit_kapisi_lifli(self, k: int, alt: int, G: np.ndarray) -> None:
        if self._eksen(k, alt) <= 0:
            self._dusen_kapi += 1
            return
        n = int(self.ayar.lif[int(k)])
        self._karo_vur(k, self._gomulu(n, int(alt), G))

    def _cift_kapisi_lifli(self, ki: int, ai: int, kj: int, aj: int,
                           G: np.ndarray) -> None:
        ei = self._eksen(ki, ai)
        ej = self._eksen(kj, aj)
        if ei <= 0 or ej <= 0 or ei == ej:
            self._dusen_kapi += 1
            return
        G = np.asarray(G, complex).reshape(4, 4)
        if int(ki) == int(kj):
            n = int(self.ayar.lif[int(ki)])
            bi, bj = 1 << int(ai), 1 << int(aj)
            M = np.eye(n, dtype=complex)
            for x in range(n):
                if (x & bi) or (x & bj):
                    continue
                idx = [x, x | bj, x | bi, x | bi | bj]
                for a in range(4):
                    for b in range(4):
                        M[idx[a], idx[b]] = G[a, b]
            self._karo_vur(int(ki), M)
            return
        self._faz_indir()
        self._karolari_banda()
        bi = 1 << int(self._seviye - ei)
        bj = 1 << int(self._seviye - ej)
        if matchgate_mi(G)[0]:
            self._matchgate_kapi += 1
        self._bant.cift(bi, bj, G)
        self._kapi += 1
        self.iz.kapi += 1

    def bit_kapisi(self, k: int, alt: int, G: np.ndarray) -> None:
        self._bit_kapisi_lifli(k, alt, G)

    def faz(self, teta) -> None:
        t = np.asarray(teta, float).reshape(-1)
        if t.size != self.d:
            from .qudit import agirlik
            t = np.asarray(agirlik(self.d, t), float).reshape(-1)
        m = int(self.ayar.faz_mertebesi)
        if str(self.ayar.motor) != "galois":
            self._bosalt()
            self._psi = self._psi * np.exp(-1j * t)
            self._kapi += 1
            return
        k = (np.rint(-t * m / (2.0 * math.pi)).astype(np.int64) % m)
        self._faz_toplam = (self._faz_toplam + k) % m
        if self._bekleyen:
            self._bosalt()
        self._faz_bekleyen = (k if self._faz_bekleyen is None
                              else (self._faz_bekleyen + k) % m)
        self._kapi += 1

    def sektor_kapisi(self, ad: str, M: np.ndarray) -> None:
        i, j = self.sektor(ad)
        M = np.asarray(M)
        if M.shape != (j - i, j - i):
            raise ValueError("sektör kapısı %s olmalı, %s verildi"
                             % ((j - i, j - i), M.shape))
        self.psi[:, i:j] = self.psi[:, i:j] @ M.T
        self._kapi += 1

    def sektor(self, ad: str) -> Tuple[int, int]:
        if ad not in self._sektor:
            raise ValueError("küllî alan bilinmiyor: %r" % (ad,))
        return self._sektor[ad]

    def alan_degeri(self, ad: str):
        v = self.sektor_agirligi(ad)
        return float(v[0]) if self.B == 1 else v

    def olcumler(self) -> Dict[str, float]:
        p = np.abs(self.psi) ** 2
        out: Dict[str, float] = {}
        for ad in self._sektor:
            i, j = self._sektor[ad]
            v = np.sum(p[:, i:j], axis=1)
            out[ad] = float(v[0]) if self.B == 1 else v
        e = self.dolasiklik_entropisi()
        out["entropi"] = float(e["entropi"])
        out["norm_hatası"] = self.norm_hatasi()
        return out

    def dolasiklik_entropisi(self, kesit: int = 1) -> Dict[str, float]:
        lif = tuple(self.ayar.lif)
        kesit = int(np.clip(kesit, 1, len(lif) - 1))
        sol = int(np.prod(lif[:kesit]))
        sag = int(np.prod(lif[kesit:]))
        M = self.psi.reshape(self.B, sol, sag)
        rho = np.einsum("bij,bkj->bik", M, M.conj())
        iz = np.einsum("bii->b", rho).real
        rho = rho / np.maximum(iz, 1e-300)[:, None, None]
        w = np.linalg.eigvalsh(rho)
        w = np.clip(w.real, 1e-300, None)
        S = -np.sum(w * np.log(w), axis=1)
        return {"entropi": float(np.mean(S)),
                "entropi_yigin": S,
                "schmidt": float(min(sol, sag)),
                "kesit": kesit}

    def beyan(self, sozluk: int = 0) -> np.ndarray:
        i, j = self.sektor("kelam")
        taban = int(sozluk) if int(sozluk) >= 2 else int(self.ayar.lif[0])
        assert taban <= (j - i), (
            "kelâm sektörü %d genlik, taban %d -- taban sektörden büyük "
            "olamaz; sözlük geçilmiş olabilir (ferman 1-N)"
            % (j - i, taban))
        p = np.abs(self.psi[:, i:j]) ** 2
        parca = np.array_split(np.arange(j - i), taban)
        P = np.stack([p[:, idx].sum(axis=1) for idx in parca], axis=1)
        return P / np.maximum(P.sum(axis=1, keepdims=True), 1e-300)

    def povm(self, ad: str) -> Tuple[float, float]:
        i, j = self.sektor(ad)
        v = self.psi[:, i:j]
        yari = (j - i) // 2 or 1
        z = float(np.mean(np.sum(np.abs(v[:, :yari]) ** 2, axis=1)
                          - np.sum(np.abs(v[:, yari:]) ** 2, axis=1)))
        x = float(np.mean(2.0 * np.real(
            np.sum(v[:, :yari] * v[:, yari:yari * 2].conj(), axis=1))))
        return z, x

    def kodla(self, belirtecler: Sequence[int], sozluk: int = 16) -> None:
        t = np.asarray(belirtecler, int).reshape(-1) % int(sozluk)
        i, j = self.sektor("kelam")
        parca = np.array_split(np.arange(i, j), int(sozluk))
        self.psi = np.zeros((self.B, self.d), dtype=self.ayar.tip)
        for b in range(self.B):
            tb = t[b % t.size]
            idx = parca[int(tb)]
            u = np.arange(idx.size) - (idx.size - 1) / 2.0
            zarf = np.exp(-(u ** 2) / max(idx.size, 1))
            self.psi[b, idx] = zarf * np.exp(1j * u * (1.0 + tb))
        self.normalize()

    def superpozisyon(self) -> None:
        self.psi = np.full((self.B, self.d), 1.0 / np.sqrt(self.d),
                           dtype=self.ayar.tip)


    def _lif_no(self, yuva: int) -> Tuple[int, int]:
        y = int(yuva)
        c = self._yuva_onbellek.get(y)
        if c is not None:
            return c
        ns = self._n_satir
        satir_yuva = self._satir_yuva
        if y < ns * satir_yuva:
            c = (y // satir_yuva, y % satir_yuva)
        else:
            o = y - ns * satir_yuva
            c = (len(self.ayar.lif), o)
            for k in range(ns, len(self.ayar.lif)):
                w = int(self.ayar.lif[k]).bit_length() - 1
                if o < w:
                    c = (k, o)
                    break
                o -= w
        self._yuva_onbellek[y] = c
        return c

    def gecerli(self, yuva: int) -> bool:
        y = int(yuva)
        c = self._gecerli_onbellek.get(y)
        if c is not None:
            return c
        k, alt = self._lif_no(y)
        lif = tuple(self.ayar.lif)
        c = bool(0 <= k < len(lif) and (1 << int(alt)) < int(lif[k]))
        self._gecerli_onbellek[y] = c
        return c

    def _adres_dizileri(self):
        if self._adres_np is None:
            ns = self._n_satir
            satir_yuva = self._veri_lifi + int(self.ayar.yerel_yuva)
            lif = tuple(self.ayar.lif)
            n = ns * satir_yuva + sum(
                int(x).bit_length() - 1 for x in lif[ns:])
            k = np.empty(n, np.int64)
            alt = np.empty(n, np.int64)
            gec = np.empty(n, bool)
            for y in range(n):
                kk, aa = self._lif_no(y)
                k[y] = kk
                alt[y] = aa
                gec[y] = self.gecerli(y)
            self._adres_np = (gec, k, alt)
        return self._adres_np

    def gecerli_toplu(self, yuvalar) -> np.ndarray:
        y = np.asarray(yuvalar, np.int64).reshape(-1)
        gec, _k, _a = self._adres_dizileri()
        icinde = (y >= 0) & (y < gec.size)
        out = np.zeros(y.size, bool)
        out[icinde] = gec[y[icinde]]
        return out

    def lif_no_toplu(self, yuvalar) -> Tuple[np.ndarray, np.ndarray]:
        y = np.asarray(yuvalar, np.int64).reshape(-1)
        gec, k, a = self._adres_dizileri()
        icinde = (y >= 0) & (y < gec.size)
        kk = np.full(y.size, -1, np.int64)
        aa = np.full(y.size, -1, np.int64)
        kk[icinde] = k[y[icinde]]
        aa[icinde] = a[y[icinde]]
        return kk, aa

    def veri(self, i: int, j: int) -> int:
        return int(i) * self._satir_yuva + int(j)

    @property
    def n_satir(self) -> int:
        return int(self._n_satir)

    @property
    def veri_yuvasi(self) -> int:
        return int(self._veri_yuvasi)

    def veri_izgara(self, sutun=None, satir=None) -> np.ndarray:
        i = (np.arange(self._n_satir) if satir is None
             else np.asarray(satir, np.int64).reshape(-1))
        j = (np.arange(self._veri_yuvasi) if sutun is None
             else np.asarray(sutun, np.int64).reshape(-1))
        return (i[:, None] * self._satir_yuva + j[None, :]).reshape(-1)

    def yerel(self, i: int) -> int:
        return self.veri(i, self._veri_yuvasi)

    def kulli(self, ad: str, j: int = 0) -> int:
        i, _ = self.sektor(ad)
        return self._n_satir * self._satir_yuva + i + int(j)

    def yereller(self) -> List[int]:
        return [self.yerel(i) for i in range(self._n_satir)]

    def bolge_var(self, ad: str) -> bool:
        return ad in self._sektor

    def not_dus(self, meleke: str, mesaj: str = "") -> None:
        self.iz.not_dus(meleke, mesaj)

    def kanonikle(self) -> None:
        self.iz.not_dus("kanonikle", "quditte kanoniklik yok -- işlem yok")

    def _gomulu(self, n: int, alt: int, G: np.ndarray) -> np.ndarray:
        G = np.asarray(G, complex).reshape(2, 2)
        M = np.eye(n, dtype=complex)
        b = 1 << int(alt)
        if b >= n:
            return M
        for x in range(n):
            if x & b:
                continue
            y = x | b
            M[x, x] = G[0, 0]; M[x, y] = G[0, 1]
            M[y, x] = G[1, 0]; M[y, y] = G[1, 1]
        return M

    def tek(self, yuva: int, G: np.ndarray) -> None:
        if not self.gecerli(yuva):
            self._dusen_kapi += 1
            return
        k, alt = self._lif_no(yuva)
        self.bit_kapisi(k, alt, G)

    def tek_yigin(self, yuvalar: Sequence[int], G) -> None:
        G = np.asarray(G)
        if G.ndim == 2:
            G = np.broadcast_to(G, (len(yuvalar), 2, 2))
        sira: List[Tuple[int, int]] = []
        birik: Dict[Tuple[int, int], np.ndarray] = {}
        yv = np.asarray([int(y) for y in yuvalar], np.int64)
        gec = self.gecerli_toplu(yv)
        kk, aa = self.lif_no_toplu(yv)
        self._dusen_kapi += int((~gec).sum())
        for idx in np.flatnonzero(gec):
            g = G[int(idx)]
            anahtar = (int(kk[idx]), int(aa[idx]))
            g2 = np.asarray(g, complex).reshape(2, 2)
            if anahtar in birik:
                birik[anahtar] = g2 @ birik[anahtar]
            else:
                birik[anahtar] = g2
                sira.append(anahtar)
        for anahtar in sira:
            self.bit_kapisi(anahtar[0], anahtar[1], birik[anahtar])

    def cift(self, yuva: int, G: np.ndarray) -> None:
        self.uzak_cift(int(yuva), int(yuva) + 1, G)

    def _bolum(self, k: int) -> Tuple[int, int]:
        c = self._bolum_onbellek.get(int(k))
        if c is not None:
            return c
        lif = tuple(self.ayar.lif)
        on = 1
        for x in lif[:k]:
            on *= int(x)
        ard = 1
        for x in lif[k + 1:]:
            ard *= int(x)
        c = (on, ard)
        self._bolum_onbellek[int(k)] = c
        return c

    def cift_bit_kapisi(self, ki: int, ai: int, kj: int, aj: int,
                        G: np.ndarray) -> None:
        self._cift_kapisi_lifli(ki, ai, kj, aj, G)

    def uzak_cift(self, i: int, j: int, G: np.ndarray) -> None:
        if not (self.gecerli(i) and self.gecerli(j)):
            self._dusen_kapi += 1
            return
        G = np.asarray(G, complex).reshape(4, 4)
        ki, ai = self._lif_no(int(i))
        kj, aj = self._lif_no(int(j))
        lif = tuple(self.ayar.lif)
        if self._ikinin_kuvveti:
            self.cift_bit_kapisi(ki, ai, kj, aj, G)
            return
        if ki == kj:
            n = lif[ki]
            bi, bj = 1 << ai, 1 << aj
            if bi >= n or bj >= n or bi == bj:
                return
            M = np.eye(n, dtype=complex)
            for x in range(n):
                if (x & bi) or (x & bj):
                    continue
                idx = [x, x | bj, x | bi, x | bi | bj]
                for a in range(4):
                    for b in range(4):
                        M[idx[a], idx[b]] = G[a, b]
            self.lif_kapisi(ki, M)
            return
        ni, nj = lif[ki], lif[kj]
        bi, bj = 1 << ai, 1 << aj
        if bi >= ni or bj >= nj:
            return
        T = self.lifli
        T = np.moveaxis(T, (ki + 1, kj + 1), (-2, -1))
        sekil = T.shape
        F = T.reshape(-1, ni, nj)
        Mi = np.eye(ni, dtype=complex)
        Mj = np.eye(nj, dtype=complex)
        for x in range(ni):
            if x & bi:
                continue
            for y in range(nj):
                if y & bj:
                    continue
                idx = [(x, y), (x, y | bj), (x | bi, y), (x | bi, y | bj)]
                v = np.stack([F[:, a, b] for a, b in idx], axis=1)
                v = v @ G.T
                for m, (a, b) in enumerate(idx):
                    F[:, a, b] = v[:, m]
        T = F.reshape(sekil)
        self.psi = np.moveaxis(T, (-2, -1), (ki + 1, kj + 1)).reshape(
            self.B, self.d)
        self._kapi += 1
        self.iz.kapi += 1

    def mpo_uygula(self, W, D: int = 2, bas: int = 0, son=None,
                   sol_sinir=None, sag_sinir=None) -> float:
        if not isinstance(W, dict) or not W:
            return 0.0
        lif = tuple(self.ayar.lif)
        sira: List[Tuple[int, int]] = []
        birik: Dict[Tuple[int, int], np.ndarray] = {}
        for yuva, Wk in W.items():
            Wk = np.asarray(Wk)
            k, alt = self._lif_no(int(yuva))
            if Wk.ndim == 4:
                G = Wk[0, :, :, 0]
            elif Wk.ndim == 2 and Wk.shape == (2, 2):
                G = Wk
            else:
                continue
            if not self.gecerli(int(yuva)):
                self._dusen_kapi += 1
                continue
            G = np.asarray(G, complex).reshape(2, 2)
            if not np.any(G):
                continue
            if (abs(G[0, 0] - 1.0) < 1e-12 and abs(G[1, 1] - 1.0) < 1e-12
                    and abs(G[0, 1]) < 1e-12 and abs(G[1, 0]) < 1e-12):
                continue
            anahtar = (int(k), int(alt))
            g2 = np.asarray(G, complex).reshape(2, 2)
            if anahtar in birik:
                birik[anahtar] = g2 @ birik[anahtar]
            else:
                birik[anahtar] = g2
                sira.append(anahtar)
        for anahtar in sira:
            self.bit_kapisi(anahtar[0], anahtar[1], birik[anahtar])
        self.normalize()
        return 0.0

    def mpo_uygula_hizli(self, *a, **k) -> float:
        return self.mpo_uygula(*a, **k)

    def mpo_topla(self, alan: str, acilar=None, duraklar=None, j: int = 0
                  ) -> None:
        if alan not in self._sektor:
            return
        a = np.asarray(acilar if acilar is not None else [0.0],
                       float).reshape(-1)
        i, jj = self.sektor(alan)
        u = np.arange(jj - i)
        faz = np.exp(1j * (a.mean() * (u + 1.0) / max(jj - i, 1)))
        self.psi[:, i:jj] = self.psi[:, i:jj] * faz
        self._kapi += 1
        self.iz.kapi += 1
        return 0.0

    def mpo_dagit(self, alan: str, acilar=None, duraklar=None, j: int = 0
                  ) -> None:
        if alan not in self._sektor:
            return
        a = np.asarray(acilar if acilar is not None else [0.0],
                       float).reshape(-1)
        self.faz(np.full(min(8, self.d - 1), -float(a.mean())))
        return 0.0

    def uret(self, baglam: Sequence[int], teta=None, sozluk: int = 16
             ) -> np.ndarray:
        bag = list(np.asarray(baglam, int).reshape(-1) % int(sozluk))
        if not bag:
            raise ValueError("üretim için bağlam lâzım")
        self.kodla([bag[0]], sozluk=sozluk)
        for k, t in enumerate(bag[1:], start=1):
            aci = np.full(min(8, self.d - 1),
                          (t + 1.0) / (k + 1.0), dtype=float)
            self.faz(aci)
        if teta is not None:
            T = np.asarray(teta, float).reshape(-1)
            lif = tuple(self.ayar.lif)
            gerek = sum(n * n for n in lif)
            T = np.resize(T, gerek)
            bas = 0
            for k, n in enumerate(lif):
                Ak = T[bas:bas + n * n].reshape(n, n)
                bas += n * n
                A = Ak - Ak.T
                I = np.eye(n)
                G = np.linalg.solve(I + A, I - A)
                self.lif_kapisi(k, G)
        return self.beyan(sozluk)

    def rapor(self) -> str:
        o = self.olcumler()
        s = ["=== QUDİT YAZMACI (MPS'in yerine) ===", "",
             "  d              : %d  (%.1f KB, TAM tutulur)"
             % (self.d, self.d * 16 / 1024),
             "  lifler         : %s" % (self.ayar.lif,),
             "  yığın          : %d" % self.B,
             "  norm hatası    : %.3e" % self.norm_hatasi(),
             "  entropi (kesit): %.6f" % o["entropi"],
             "  vurulan kapı   : %d" % self._kapi,
             "  sadakat log    : %.1f  (kesme yok → tam sıfır)"
             % self.sadakat_log(),
             "", "  SEKTÖRLER (eski küllî alanların yerine):"]
        for ad, (i, j) in self._sektor.items():
            s.append("    %-9s [%4d–%4d]  ağırlık %.6f"
                     % (ad, i, j, float(np.ravel(o[ad])[0])))
        return "\n".join(s)
