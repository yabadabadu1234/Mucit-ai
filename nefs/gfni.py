from __future__ import annotations

import ctypes
import os
import subprocess
from typing import Any, Dict

import numpy as np

__all__ = ["GFNI_C", "derle", "yoklama", "kutuphane", "symplectic_gfni",
           "cpuid"]

GFNI_C = r'''
/* MUCİT-AI -- GALOIS KOMUTLARI. Taklit yok: komutun kendisi. */
#include <immintrin.h>
#include <stddef.h>
#include <stdint.h>
#include <cpuid.h>

/* ---- AES S-box: affine(inverse(x)) -- TEK KOMUT ---------------- */
void mucit_sbox(const uint8_t *in, uint8_t *out, size_t n)
{
    const __m512i A = _mm512_set1_epi64((long long)0xF1E3C78F1F3E7CF8ULL);
    size_t i = 0;
    for (; i + 64 <= n; i += 64) {
        __m512i x = _mm512_loadu_si512((const void *)(in + i));
        _mm512_storeu_si512((void *)(out + i),
            _mm512_gf2p8affineinv_epi64_epi8(x, A, 0x63));
    }
    if (i < n) {
        uint8_t b[64] = {0};
        size_t k, r = n - i;
        for (k = 0; k < r; k++) b[k] = in[i + k];
        __m512i x = _mm512_loadu_si512((const void *)b);
        _mm512_storeu_si512((void *)b,
            _mm512_gf2p8affineinv_epi64_epi8(x, A, 0x63));
        for (k = 0; k < r; k++) out[i + k] = b[k];
    }
}

/* ---- Symplectic süpürme: XOR + AND + POPCOUNT, kayan nokta YOK -
 *
 * Zabıtın (1 TB/s GPU) 1. motorunun CPU mukabili. GPU'da
 * __xor_sync/__popc ne ise burada _mm512_xor_si512 ve
 * _mm512_popcnt_epi64 odur; AVX-512 VPOPCNTDQ yoksa
 * __builtin_popcountll'e iner (o da tek komuttur: POPCNT).
 *
 * Tableau güncellemesi:  X ^= maske ;  Z ^= (X & faz) ;  parite = popcount
 * Dönen: toplam parite (ölçülebilsin diye; iş sessizce kaybolmasın). */
uint64_t mucit_symplectic(uint64_t *X, uint64_t *Z, const uint64_t *maske,
                          const uint64_t *faz, size_t satir, size_t kelime)
{
    uint64_t par = 0;
    size_t r, w;
    for (r = 0; r < satir; r++) {
        uint64_t *xr = X + r * kelime, *zr = Z + r * kelime;
        w = 0;
#if defined(__AVX512F__)
        for (; w + 8 <= kelime; w += 8) {
            __m512i xv = _mm512_loadu_si512((const void *)(xr + w));
            __m512i mv = _mm512_loadu_si512((const void *)(maske + w));
            __m512i fv = _mm512_loadu_si512((const void *)(faz + w));
            __m512i zv = _mm512_loadu_si512((const void *)(zr + w));
            xv = _mm512_xor_si512(xv, mv);
            zv = _mm512_xor_si512(zv, _mm512_and_si512(xv, fv));
            _mm512_storeu_si512((void *)(xr + w), xv);
            _mm512_storeu_si512((void *)(zr + w), zv);
        }
#endif
        for (; w < kelime; w++) {
            xr[w] ^= maske[w];
            zr[w] ^= (xr[w] & faz[w]);
        }
        for (w = 0; w < kelime; w++)
            par += (uint64_t)__builtin_popcountll(zr[w]);
    }
    return par;
}

/* ---- CPUID: bayrak ne diyor (komutun ne yaptığından AYRI) ------ */
void mucit_cpuid(uint32_t *o)
{
    unsigned a, b, c, d;
    __cpuid_count(7, 0, a, b, c, d);
    o[0] = (c >> 8) & 1;    /* GFNI       */
    o[1] = (c >> 9) & 1;    /* VAES       */
    o[2] = (c >> 10) & 1;   /* VPCLMULQDQ */
    o[3] = (b >> 16) & 1;   /* AVX512F    */
    o[4] = (b >> 30) & 1;   /* AVX512BW   */
    o[5] = (b >> 31) & 1;   /* AVX512VL   */
    o[6] = (c >> 1) & 1;    /* AVX512VBMI */
    o[7] = (c >> 14) & 1;   /* VPOPCNTDQ  */
}

/* ---- Yoklama: S-box'ın ilk 64 baytı AES'in cetveline uyuyor mu -
 * Ayrı süreçte koşar; komut yoksa buraya varılmadan SIGILL gelir. */
int mucit_yoklama(void)
{
    static const uint8_t bek[8] = {0x63,0x7c,0x77,0x7b,0xf2,0x6b,0x6f,0xc5};
    uint8_t in[64], out[64];
    int i;
    for (i = 0; i < 64; i++) in[i] = (uint8_t)i;
    mucit_sbox(in, out, 64);
    for (i = 0; i < 8; i++) if (out[i] != bek[i]) return 0;
    return 1;
}
'''

_YOKLAMA_C = r'''
#include <stdio.h>
int mucit_yoklama(void);
void mucit_sbox(const unsigned char*, unsigned char*, unsigned long);
int main(void){
    unsigned char in[256], out[256];
    int i;
    if (!mucit_yoklama()) return 2;
    for (i = 0; i < 256; i++) in[i] = (unsigned char)i;
    mucit_sbox(in, out, 256);
    for (i = 0; i < 256; i++) printf("%02x", out[i]);
    printf("\n");
    return 0;
}
'''

from .derleyici import DERLEME_DIZINI, ORTAK_BAYRAK

BAYRAK = ORTAK_BAYRAK + ["-mgfni", "-mavx512f", "-mavx512bw",
                         "-mavx512vl", "-mpopcnt"]

_ONBELLEK: Dict[str, Any] = {}


def _ozet() -> str:
    from .derleyici import ozet
    return ozet(GFNI_C, BAYRAK, _YOKLAMA_C)


def derle() -> Dict[str, Any]:
    from .derleyici import derle as _derle
    return _derle("gfni", GFNI_C, BAYRAK, _YOKLAMA_C)


def yoklama() -> Dict[str, Any]:
    c = _ONBELLEK.get("yoklama")
    if c is not None:
        return c
    d = derle()
    o: Dict[str, Any] = {"derlendi": bool(d["derlendi"])}
    o.update({k: d[k] for k in ("kaynak_özeti", "derleyici", "bayrak")})
    if not d["derlendi"]:
        o.update({"koşuyor": False, "sebep": "derlenemedi",
                  "derleyici_çıktısı": d.get("derleyici_çıktısı", "")[:400],
                  "cpuid": {}, "cetvel_tuttu": False, "sinyal": None})
        _ONBELLEK["yoklama"] = o
        return o
    r = subprocess.run([d["yoklama_ikilisi"]], capture_output=True, text=True)
    kostu = bool(r.returncode == 0 and len(r.stdout.strip()) == 512)
    o["sinyal"] = int(-r.returncode) if r.returncode < 0 else 0
    o["koşuyor"] = kostu
    o["sebep"] = ("tamam" if kostu else
                  ("SIGILL -- komut bu işlemcide YOK" if r.returncode < 0
                   else "yoklama cetveli tutmadı"))
    o["sbox"] = r.stdout.strip() if kostu else ""
    o["cpuid"] = cpuid() if kostu else {}
    o["cetvel_tuttu"] = kostu and o["sbox"][:16] == "637c777bf26b6fc5"
    _ONBELLEK["yoklama"] = o
    return o


def cpuid() -> Dict[str, bool]:
    lib = kutuphane()
    if lib is None:
        return {}
    buf = (ctypes.c_uint32 * 8)()
    lib.mucit_cpuid(buf)
    ad = ("GFNI", "VAES", "VPCLMULQDQ", "AVX512F", "AVX512BW",
          "AVX512VL", "AVX512VBMI", "VPOPCNTDQ")
    return {a: bool(buf[i]) for i, a in enumerate(ad)}


def kutuphane():
    if "lib" in _ONBELLEK:
        return _ONBELLEK["lib"]
    d = derle()
    lib = None
    if d["derlendi"] and os.path.exists(d["so"]):
        lib = ctypes.CDLL(d["so"])
        u8 = ctypes.POINTER(ctypes.c_uint8)
        u64 = ctypes.POINTER(ctypes.c_uint64)
        lib.mucit_sbox.argtypes = [u8, u8, ctypes.c_size_t]
        lib.mucit_sbox.restype = None
        lib.mucit_symplectic.argtypes = [u64, u64, u64, u64,
                                         ctypes.c_size_t, ctypes.c_size_t]
        lib.mucit_symplectic.restype = ctypes.c_uint64
        lib.mucit_cpuid.argtypes = [ctypes.POINTER(ctypes.c_uint32)]
        lib.mucit_cpuid.restype = None
        lib.mucit_yoklama.argtypes = []
        lib.mucit_yoklama.restype = ctypes.c_int
    _ONBELLEK["lib"] = lib
    return lib


def _p8(a: np.ndarray):
    return a.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8))


def _p64(a: np.ndarray):
    return a.ctypes.data_as(ctypes.POINTER(ctypes.c_uint64))


def symplectic_gfni(X, Z, maske, faz) -> int:
    assert yoklama()["koşuyor"], "GFNI kütüphanesi koşmuyor"
    Xa = np.ascontiguousarray(X, np.uint64)
    Za = np.ascontiguousarray(Z, np.uint64)
    assert Xa.shape == Za.shape and Xa.ndim == 2, "X ve Z (satır, kelime)"
    satir, kelime = Xa.shape
    m = np.ascontiguousarray(np.asarray(maske, np.uint64).reshape(-1))
    f = np.ascontiguousarray(np.asarray(faz, np.uint64).reshape(-1))
    assert m.size == kelime and f.size == kelime, "maske/faz kelime boyunda"
    par = kutuphane().mucit_symplectic(_p64(Xa), _p64(Za), _p64(m), _p64(f),
                                       ctypes.c_size_t(satir),
                                       ctypes.c_size_t(kelime))
    X[...] = Xa
    Z[...] = Za
    return int(par)

