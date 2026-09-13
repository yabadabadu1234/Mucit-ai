from __future__ import annotations

import ctypes
import hashlib
import os
import subprocess
import tempfile
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

__all__ = ["CekirdekAyari", "CEKIRDEK_C", "HAT_TIPI", "derle", "yoklama",
           "kutuphane",
           "Bant", "cekirdek_beyani", "rapor"]


KARO, CIFT, MATCHGATE = 0, 1, 2

HAT_TIPI = np.complex128

CEKIRDEK_C = r'''
/* MUCİT-AI -- KAPI BANDI ÇEKİRDEĞİ.
 * Durum ayrıştırılmış gerçek/sanal iki dizidir; bütün kapılar aynı
 * geçişte, aynı tamponlar üstünde koşar. Tahsis YOKTUR. */
#include <stddef.h>
#include <stdint.h>
#include <string.h>
#if defined(__AVX512F__)
#include <immintrin.h>
#endif

typedef struct {
    int32_t tip;      /* 0 = karo, 1 = cift            */
    int32_t a;        /* karo: on   | cift: bi (2^pi)  */
    int32_t b;        /* karo: n    | cift: bj (2^pj)  */
    int32_t c;        /* karo: ard  | cift: -          */
    int64_t ofset;    /* dizey tamponundaki başlangıç  */
} Kapi;

/* ---- KARO: (N, n, ard) bloğuna n×n dizey ---------------------- */
static void karo_vur(double *re, double *im, size_t B,
                     int on, int n, int ard,
                     const double *Mre, const double *Mim,
                     double *tre, double *tim)
{
    size_t blok = (size_t)B * (size_t)on;
    size_t adim = (size_t)n * (size_t)ard;
    for (size_t g = 0; g < blok; g++) {
        double *xr = re + g * adim, *xi = im + g * adim;
        /* Netice geçici tampona yazılır: kaynak okunmadan bozulmasın. */
        for (int i = 0; i < n; i++) {
            double *ar = tre + (size_t)i * ard, *ai = tim + (size_t)i * ard;
            for (int t = 0; t < ard; t++) { ar[t] = 0.0; ai[t] = 0.0; }
            for (int j = 0; j < n; j++) {
                const double mr = Mre[(size_t)i * n + j];
                const double mi = Mim[(size_t)i * n + j];
                const double *br = xr + (size_t)j * ard;
                const double *bi = xi + (size_t)j * ard;
                int t = 0;
#if defined(__AVX512F__)
                __m512d vmr = _mm512_set1_pd(mr), vmi = _mm512_set1_pd(mi);
                for (; t + 8 <= ard; t += 8) {
                    __m512d br8 = _mm512_loadu_pd(br + t);
                    __m512d bi8 = _mm512_loadu_pd(bi + t);
                    __m512d ar8 = _mm512_loadu_pd(ar + t);
                    __m512d ai8 = _mm512_loadu_pd(ai + t);
                    ar8 = _mm512_fmadd_pd(vmr, br8, ar8);
                    ar8 = _mm512_fnmadd_pd(vmi, bi8, ar8);
                    ai8 = _mm512_fmadd_pd(vmr, bi8, ai8);
                    ai8 = _mm512_fmadd_pd(vmi, br8, ai8);
                    _mm512_storeu_pd(ar + t, ar8);
                    _mm512_storeu_pd(ai + t, ai8);
                }
#endif
                for (; t < ard; t++) {
                    ar[t] += mr * br[t] - mi * bi[t];
                    ai[t] += mr * bi[t] + mi * br[t];
                }
            }
        }
        memcpy(xr, tre, adim * sizeof(double));
        memcpy(xi, tim, adim * sizeof(double));
    }
}

/* ---- ÇİFT: iki bit düzlemine 4×4 dizey, İÇ İÇE düzende --------
 *
 * **AYRIŞTIRMA YOK.** Çift kapı zaten dört ayrı adrese gider; iç içe
 * ``(re,im)`` düzeninde de aynı dörtlüdür. Ayrıştırmak durumu iki
 * kere daha dolaşmak olurdu ve kazanç yerine kayıp verirdi. */
static void cift_ic(double *psi, size_t B, size_t d,
                    int64_t bi, int64_t bj,
                    const double *Gre, const double *Gim)
{
    int64_t lo = bi < bj ? bi : bj;
    int64_t hi = bi < bj ? bj : bi;
    int64_t s[4];
    s[0] = 0; s[1] = bj; s[2] = bi; s[3] = bi + bj;
    for (size_t bt = 0; bt < B; bt++) {
        double *P = psi + bt * 2 * d;
        for (int64_t h = 0; h < (int64_t)d; h += 2 * hi) {
            for (int64_t l = 0; l < hi; l += 2 * lo) {
                for (int64_t t = 0; t < lo; t++) {
                    int64_t x = h + l + t;
                    double vr[4], vi[4];
                    for (int k = 0; k < 4; k++) {
                        vr[k] = P[2 * (x + s[k])];
                        vi[k] = P[2 * (x + s[k]) + 1];
                    }
                    for (int a = 0; a < 4; a++) {
                        double ar = 0.0, ai = 0.0;
                        for (int b = 0; b < 4; b++) {
                            const double gr = Gre[a * 4 + b];
                            const double gi = Gim[a * 4 + b];
                            ar += gr * vr[b] - gi * vi[b];
                            ai += gr * vi[b] + gi * vr[b];
                        }
                        P[2 * (x + s[a])] = ar;
                        P[2 * (x + s[a]) + 1] = ai;
                    }
                }
            }
        }
    }
}

/* ---- MATCHGATE: parite bloğunda, YARIM ÇARPIM ------------------
 *
 * Valiant-Terhal: ``G(A,B)`` pariteyi korur; ``A`` çift pariteli
 * ``{0,3}``, ``B`` tek pariteli ``{1,2}`` altuzayında ayrı döner.
 * Umumî 4×4'te öbek başına 16 karmaşık çarpım vardır; burada 8. */
static void cift_mg(double *psi, size_t B, size_t d,
                    int64_t bi, int64_t bj,
                    const double *Gre, const double *Gim)
{
    int64_t lo = bi < bj ? bi : bj;
    int64_t hi = bi < bj ? bj : bi;
    int64_t s[4];
    s[0] = 0; s[1] = bj; s[2] = bi; s[3] = bi + bj;
    /* A = G[{0,3}×{0,3}] , B = G[{1,2}×{1,2}] */
    const int ci[2] = {0, 3}, ti[2] = {1, 2};
    for (size_t bt = 0; bt < B; bt++) {
        double *P = psi + bt * 2 * d;
        for (int64_t h = 0; h < (int64_t)d; h += 2 * hi) {
            for (int64_t l = 0; l < hi; l += 2 * lo) {
                for (int64_t t = 0; t < lo; t++) {
                    int64_t x = h + l + t;
                    for (int blok = 0; blok < 2; blok++) {
                        const int *ix = blok ? ti : ci;
                        double vr[2], vi[2];
                        for (int k = 0; k < 2; k++) {
                            vr[k] = P[2 * (x + s[ix[k]])];
                            vi[k] = P[2 * (x + s[ix[k]]) + 1];
                        }
                        for (int a = 0; a < 2; a++) {
                            double ar = 0.0, ai = 0.0;
                            for (int b = 0; b < 2; b++) {
                                const double gr = Gre[ix[a] * 4 + ix[b]];
                                const double gi = Gim[ix[a] * 4 + ix[b]];
                                ar += gr * vr[b] - gi * vi[b];
                                ai += gr * vi[b] + gi * vr[b];
                            }
                            P[2 * (x + s[ix[a]])] = ar;
                            P[2 * (x + s[ix[a]]) + 1] = ai;
                        }
                    }
                }
            }
        }
    }
}

/* Çift kapı bandı: ardışık bütün çift kapılar TEK çağrıda.
 * ``tip == 2`` ise matchgate yolu (yarım çarpım). */
void mucit_cift_bant(double *psi, size_t B, size_t d,
                     const Kapi *bant, size_t kapi_sayisi,
                     const double *dre, const double *dim)
{
    for (size_t k = 0; k < kapi_sayisi; k++) {
        const Kapi *g = &bant[k];
        if (g->tip == 2)
            cift_mg(psi, B, d, (int64_t)g->a, (int64_t)g->b,
                    dre + g->ofset, dim + g->ofset);
        else
            cift_ic(psi, B, d, (int64_t)g->a, (int64_t)g->b,
                    dre + g->ofset, dim + g->ofset);
    }
}

/* ---- ÇİFT (ayrıştırılmış düzen) -- kıyas için duruyor ---------- */
static void cift_vur(double *re, double *im, size_t B, size_t d,
                     int64_t bi, int64_t bj,
                     const double *Gre, const double *Gim)
{
    int64_t lo = bi < bj ? bi : bj;
    int64_t hi = bi < bj ? bj : bi;
    /* Taban sırası: a = 2*bit_i + bit_j (uzak_cift ile bir). */
    int64_t s[4];
    s[0] = 0; s[1] = bj; s[2] = bi; s[3] = bi + bj;
    for (size_t bt = 0; bt < B; bt++) {
        double *R = re + bt * d, *I = im + bt * d;
        for (int64_t h = 0; h < (int64_t)d; h += 2 * hi) {
            for (int64_t l = 0; l < hi; l += 2 * lo) {
                for (int64_t t = 0; t < lo; t++) {
                    int64_t x = h + l + t;
                    double vr[4], vi[4];
                    for (int k = 0; k < 4; k++) {
                        vr[k] = R[x + s[k]];
                        vi[k] = I[x + s[k]];
                    }
                    for (int a = 0; a < 4; a++) {
                        double ar = 0.0, ai = 0.0;
                        for (int b = 0; b < 4; b++) {
                            const double gr = Gre[a * 4 + b];
                            const double gi = Gim[a * 4 + b];
                            ar += gr * vr[b] - gi * vi[b];
                            ai += gr * vi[b] + gi * vr[b];
                        }
                        R[x + s[a]] = ar;
                        I[x + s[a]] = ai;
                    }
                }
            }
        }
    }
}

/* ---- BANT: bütün kapılar TEK çağrıda -------------------------- */
void mucit_bant(double *re, double *im, size_t B, size_t d,
                const Kapi *bant, size_t kapi_sayisi,
                const double *dre, const double *dim,
                double *tre, double *tim)
{
    for (size_t k = 0; k < kapi_sayisi; k++) {
        const Kapi *g = &bant[k];
        if (g->tip == 0) {
            karo_vur(re, im, B, g->a, g->b, g->c,
                     dre + g->ofset, dim + g->ofset, tre, tim);
        } else {
            cift_vur(re, im, B, d, (int64_t)g->a, (int64_t)g->b,
                     dre + g->ofset, dim + g->ofset);
        }
    }
}

/* ---- AYRIŞTIR / BİRLEŞTİR: iç içe complex128 <-> iki reel dizi -- */
void mucit_ayristir(const double *psi, double *re, double *im, size_t n)
{
    size_t i = 0;
#if defined(__AVX512F__)
    const __m512i IDXR = _mm512_setr_epi64(0, 2, 4, 6, 8, 10, 12, 14);
    const __m512i IDXI = _mm512_setr_epi64(1, 3, 5, 7, 9, 11, 13, 15);
    for (; i + 8 <= n; i += 8) {
        __m512d a = _mm512_loadu_pd(psi + 2 * i);
        __m512d b = _mm512_loadu_pd(psi + 2 * i + 8);
        _mm512_storeu_pd(re + i, _mm512_permutex2var_pd(a, IDXR, b));
        _mm512_storeu_pd(im + i, _mm512_permutex2var_pd(a, IDXI, b));
    }
#endif
    for (; i < n; i++) { re[i] = psi[2 * i]; im[i] = psi[2 * i + 1]; }
}

void mucit_birlestir(double *psi, const double *re, const double *im,
                     size_t n)
{
    size_t i = 0;
#if defined(__AVX512F__)
    const __m512i LO = _mm512_setr_epi64(0, 8, 1, 9, 2, 10, 3, 11);
    const __m512i HI = _mm512_setr_epi64(4, 12, 5, 13, 6, 14, 7, 15);
    for (; i + 8 <= n; i += 8) {
        __m512d r = _mm512_loadu_pd(re + i);
        __m512d m = _mm512_loadu_pd(im + i);
        _mm512_storeu_pd(psi + 2 * i, _mm512_permutex2var_pd(r, LO, m));
        _mm512_storeu_pd(psi + 2 * i + 8, _mm512_permutex2var_pd(r, HI, m));
    }
#endif
    for (; i < n; i++) { psi[2 * i] = re[i]; psi[2 * i + 1] = im[i]; }
}
'''

from .derleyici import DERLEME_DIZINI, ORTAK_BAYRAK

BAYRAK = ORTAK_BAYRAK + ["-mavx512f", "-mavx512bw", "-mavx512vl",
                         "-mfma", "-funroll-loops"]

_ONBELLEK: Dict[str, Any] = {}
_SAYAC: Dict[str, int] = {"kapı": 0, "boşaltma": 0, "karo": 0, "çift": 0,
                          "numpy_boşaltma": 0}


class CekirdekAyari:

    __slots__ = ("hat", "bant")

    def __init__(self, hat: str = "c", bant: int = 0) -> None:
        self.hat = str(hat)
        self.bant = int(bant)


def _ozet() -> str:
    from .derleyici import ozet
    return ozet(CEKIRDEK_C, BAYRAK)


def derle() -> Dict[str, Any]:
    from .derleyici import derle as _derle
    return _derle("qcekirdek", CEKIRDEK_C, BAYRAK)


class _Kapi(ctypes.Structure):
    _fields_ = [("tip", ctypes.c_int32), ("a", ctypes.c_int32),
                ("b", ctypes.c_int32), ("c", ctypes.c_int32),
                ("ofset", ctypes.c_int64)]


def kutuphane():
    if "lib" in _ONBELLEK:
        return _ONBELLEK["lib"]
    d = derle()
    lib = None
    if d["derlendi"] and os.path.exists(d["so"]):
        lib = ctypes.CDLL(d["so"])
        dp = ctypes.POINTER(ctypes.c_double)
        lib.mucit_bant.argtypes = [dp, dp, ctypes.c_size_t, ctypes.c_size_t,
                                   ctypes.POINTER(_Kapi), ctypes.c_size_t,
                                   dp, dp, dp, dp]
        lib.mucit_bant.restype = None
        lib.mucit_cift_bant.argtypes = [dp, ctypes.c_size_t, ctypes.c_size_t,
                                        ctypes.POINTER(_Kapi),
                                        ctypes.c_size_t, dp, dp]
        lib.mucit_cift_bant.restype = None
        lib.mucit_ayristir.argtypes = [dp, dp, dp, ctypes.c_size_t]
        lib.mucit_ayristir.restype = None
        lib.mucit_birlestir.argtypes = [dp, dp, dp, ctypes.c_size_t]
        lib.mucit_birlestir.restype = None
    _ONBELLEK["lib"] = lib
    return lib


def yoklama() -> Dict[str, Any]:
    c = _ONBELLEK.get("yoklama")
    if c is not None:
        return c
    d = derle()
    o = {"derlendi": bool(d["derlendi"]), "bayrak": d.get("bayrak"),
         "derleyici": d.get("derleyici")}
    if not d["derlendi"]:
        o.update({"koşuyor": False,
                  "sebep": (d.get("derleyici_çıktısı") or "derlenemedi")[:200]})
        _ONBELLEK["yoklama"] = o
        return o
    _kopya = dict(_SAYAC)
    try:
        B, d_ = 2, 16
        r = np.random.default_rng(0)
        psi = (r.normal(size=(B, d_)) + 1j * r.normal(size=(B, d_)))
        M = np.eye(4, dtype=complex)
        b = Bant(B, d_, (4, 4))
        b.karo(0, M)
        v = psi.copy()
        b.bosalt(v)
        o["koşuyor"] = bool(np.max(np.abs(v - psi)) < 1e-12)
        o["sebep"] = "tamam" if o["koşuyor"] else "kimlik kapısı durumu bozdu"
    except Exception as e:
        o.update({"koşuyor": False, "sebep": "%s: %s"
                  % (type(e).__name__, e)})
    _SAYAC.clear()
    _SAYAC.update(_kopya)
    _ONBELLEK["yoklama"] = o
    return o


class Bant:

    __slots__ = ("B", "d", "lif", "bant", "hat", "_kapi", "_dizey",
                 "_re", "_im", "_tre", "_tim", "_tampon")

    def __init__(self, B: int, d: int, lif: Tuple[int, ...],
                 hat: str = "c", bant: int = 0) -> None:
        self.B = int(B)
        self.d = int(d)
        self.lif = tuple(int(x) for x in lif)
        self.hat = str(hat)
        self.bant = int(bant) if int(bant) > 0 else 256
        self._kapi: List[Tuple[int, int, int, int, int]] = []
        self._dizey: List[np.ndarray] = []
        n = self.B * self.d
        self._re = np.zeros(n, np.float64)
        self._im = np.zeros(n, np.float64)
        enb = max(self.lif) if self.lif else 1
        enb_ard = self.d // enb if enb else 1
        self._tre = np.zeros(enb * max(1, enb_ard), np.float64)
        self._tim = np.zeros(enb * max(1, enb_ard), np.float64)
        self._tampon = None

    def _bolum(self, k: int) -> Tuple[int, int]:
        on, ard = 1, 1
        for x in self.lif[:k]:
            on *= int(x)
        for x in self.lif[k + 1:]:
            ard *= int(x)
        return on, ard

    def karo(self, k: int, M) -> None:
        n = int(self.lif[int(k)])
        on, ard = self._bolum(int(k))
        A = np.ascontiguousarray(np.asarray(M, complex).reshape(n, n))
        self._kapi.append((KARO, on, n, ard, len(self._dizey)))
        self._dizey.append(A.reshape(-1))
        _SAYAC["kapı"] += 1
        _SAYAC["karo"] += 1

    def cift(self, bi: int, bj: int, G) -> None:
        from .matchgate import matchgate_mi
        A = np.ascontiguousarray(np.asarray(G, complex).reshape(4, 4))
        mg = bool(matchgate_mi(A)[0])
        self._kapi.append((MATCHGATE if mg else CIFT,
                           int(bi), int(bj), 0, len(self._dizey)))
        self._dizey.append(A.reshape(-1))
        _SAYAC["kapı"] += 1
        _SAYAC["çift"] += 1
        if mg:
            _SAYAC["matchgate"] = _SAYAC.get("matchgate", 0) + 1

    def dolu(self) -> bool:
        return len(self._kapi) >= self.bant

    def bos_mu(self) -> bool:
        return not self._kapi

    def bosalt(self, psi: np.ndarray) -> None:
        if not self._kapi:
            return
        kapilar, dizeyler = self._kapi, self._dizey
        self._kapi, self._dizey = [], []
        _SAYAC["boşaltma"] += 1
        lib = kutuphane() if self.hat == "c" else None
        if lib is None or not yoklama().get("koşuyor"):
            _SAYAC["numpy_boşaltma"] += 1
            self._numpy_bosalt(psi, kapilar, dizeyler)
            return
        assert psi.dtype == np.complex128, (
            "C hattı complex128 ister, %r verildi" % psi.dtype)
        assert psi.flags["C_CONTIGUOUS"], "durum ardışık olmalı"
        dp = ctypes.POINTER(ctypes.c_double)
        p_psi = psi.view(np.float64).ctypes.data_as(dp)
        i = 0
        n_kapi = len(kapilar)
        while i < n_kapi:
            tip = kapilar[i][0]
            if tip == KARO:
                _, on, n, ard, j = kapilar[i]
                self._karo_blas(psi, on, n, ard, dizeyler[j])
                i += 1
                continue
            j0 = i
            while i < n_kapi and kapilar[i][0] in (CIFT, MATCHGATE):
                i += 1
            oberk = kapilar[j0:i]
            duz = np.concatenate([dizeyler[g[4]] for g in oberk])
            dre = np.ascontiguousarray(duz.real)
            dim = np.ascontiguousarray(duz.imag)
            dizi = (_Kapi * len(oberk))()
            for m, (t, a, b, c, _j) in enumerate(oberk):
                dizi[m] = _Kapi(int(t), int(a), int(b), int(c), 16 * m)
            lib.mucit_cift_bant(p_psi, ctypes.c_size_t(self.B),
                                ctypes.c_size_t(self.d), dizi,
                                ctypes.c_size_t(len(oberk)),
                                dre.ctypes.data_as(dp),
                                dim.ctypes.data_as(dp))
            _SAYAC["cift_bant"] = _SAYAC.get("cift_bant", 0) + 1

    def _karo_blas(self, psi, on: int, n: int, ard: int, M) -> None:
        Mx = np.asarray(M).reshape(n, n)
        X = psi.reshape(self.B * on, n, ard)
        if ard == 1:
            Y = X.reshape(-1, n) @ Mx.T
        else:
            Y = np.matmul(Mx, X)
        psi[...] = Y.reshape(self.B, self.d)

    def _numpy_bosalt(self, psi, kapilar, dizeyler) -> None:
        B, d = self.B, self.d
        for tip, a, b, c, j in kapilar:
            M = dizeyler[j]
            if tip == KARO:
                on, n, ard = a, b, c
                X = psi.reshape(B * on, n, ard)
                Mx = M.reshape(n, n)
                if ard == 1:
                    Y = X.reshape(-1, n) @ Mx.T
                else:
                    Y = np.matmul(Mx, X)
                psi[...] = Y.reshape(B, d)
            else:
                bi, bj = a, b
                G = M.reshape(4, 4)
                idx = np.arange(d)
                taban = idx[((idx & bi) == 0) & ((idx & bj) == 0)]
                s = (0, bj, bi, bi + bj)
                V = np.stack([psi[:, taban + k] for k in s], axis=0)
                Y = np.einsum('ab,bxy->axy', G, V)
                for k in range(4):
                    psi[:, taban + s[k]] = Y[k]


def cekirdek_beyani() -> Dict[str, Any]:
    y = yoklama()
    kapi = int(_SAYAC["kapı"])
    bos = int(_SAYAC["boşaltma"])
    return {
        "hat": "c" if y.get("koşuyor") else "numpy",
        "derlendi": bool(y.get("derlendi")),
        "koşuyor": bool(y.get("koşuyor")),
        "sebep": y.get("sebep"),
        "kapı": kapi, "karo": int(_SAYAC["karo"]),
        "çift": int(_SAYAC["çift"]),
        "boşaltma": bos,
        "numpy_boşaltma": int(_SAYAC["numpy_boşaltma"]),
        "bant": 256,
        "matchgate": int(_SAYAC.get("matchgate", 0)),
        "cift_bant": int(_SAYAC.get("cift_bant", 0)),
        "bant_basina_kapi": (float(kapi) / max(1, bos)) if kapi else 0.0,
        "kıyas": ("kapı yok" if not kapi else
                  "%d kapı %d boşaltmada; ardışık çift kapılar %d C "
                  "çağrısında toplandı"
                  % (kapi, bos, int(_SAYAC.get("cift_bant", 0)))),
    }


def rapor(tohum: int = 0) -> str:
    import time
    r = np.random.default_rng(int(tohum))
    B, lif = 128, (16, 16, 16)
    d = int(np.prod(lif))
    psi0 = (r.normal(size=(B, d)) + 1j * r.normal(size=(B, d)))
    psi0 /= np.linalg.norm(psi0, axis=1, keepdims=True)

    def uni(n):
        M = r.normal(size=(n, n)) + 1j * r.normal(size=(n, n))
        q, _ = np.linalg.qr(M)
        return q

    prog = []
    for _ in range(120):
        if r.random() < 0.75:
            k = int(r.integers(0, 3))
            prog.append(("karo", k, uni(lif[k])))
        else:
            p = r.choice(12, size=2, replace=False)
            prog.append(("cift", int(1 << p[0]), int(1 << p[1]), uni(4)))

    def kos(hat):
        b = Bant(B, d, lif, hat=hat)
        v = np.ascontiguousarray(psi0.copy())
        for g in prog:
            if g[0] == "karo":
                b.karo(g[1], g[2])
            else:
                b.cift(g[1], g[2], g[3])
        t0 = time.perf_counter()
        b.bosalt(v)
        return v, time.perf_counter() - t0

    vc, tc = kos("c")
    vn, tn = kos("numpy")
    y = yoklama()
    _, tc = kos("c")
    _, tn = kos("numpy")
    fark = float(np.max(np.abs(vc - vn)))
    norm = float(np.max(np.abs(np.sum(np.abs(vc) ** 2, axis=1) - 1.0)))
    return "\n".join([
        "=== KAPI BANDI ÇEKİRDEĞİ ===", "",
        "  derlendi: %s   koşuyor: %s   (%s)"
        % (y["derlendi"], y["koşuyor"], y["sebep"]),
        "  bayrak  : %s" % y.get("bayrak"),
        "",
        "  B=%d  d=%d  lif=%s  kapı=%d  (karo %d, çift %d)"
        % (B, d, lif, len(prog),
           sum(1 for g in prog if g[0] == "karo"),
           sum(1 for g in prog if g[0] == "cift")),
        "",
        "  C hattı    : %.6f sn" % tc,
        "  numpy hattı: %.6f sn" % tn,
        "  → %.2f× %s" % (tn / max(tc, 1e-12),
                          "hızlı" if tc < tn else "YAVAŞ (ölçü kırmızı)"),
        "",
        "  İKİ HAT BİREBİR AYNI MI: azamî fark %.3e" % fark,
        "  üniterlik (norm hatası)  : %.3e" % norm,
        "",
        "  Gönderim: karo → BLAS (kapı başına 1 zgemm), ardışık çift",
        "  kapıları → tek C çağrısı. Sıra harfiyyen korunur.",
    ])
