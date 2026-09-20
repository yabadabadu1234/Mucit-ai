from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["hesap", "kronecker", "blok_carp", "faz_cevir", "cekirdek",
           "SEKTOR", "rapor"]


def hesap(ne: str = "oto"):
    ne = str(ne)
    if ne in ("oto", "cupy"):
        try:
            import cupy as cp
            return cp, "cupy", True
        except Exception:
            if ne == "cupy":
                raise RuntimeError("cupy istendi fakat kurulu değil")
    if ne in ("oto", "torch"):
        try:
            import torch
            if torch.cuda.is_available():
                return torch, "torch-cuda", True
            if ne == "torch":
                return torch, "torch-cpu", False
        except Exception:
            if ne == "torch":
                raise RuntimeError("torch istendi fakat kurulu değil")
    if ne in ("oto", "numpy"):
        return np, "numpy", False
    raise ValueError("çekirdek bilinmiyor: %r" % (ne,))


def _bicimle(xp, a):
    if xp is np:
        return np.asarray(a)
    if hasattr(xp, "asarray"):
        return xp.asarray(a)
    return xp.tensor(a)


def kronecker(psi, A, B, C, xp=None):
    xp = xp or np
    a = _bicimle(xp, A)
    b = _bicimle(xp, B)
    c = _bicimle(xp, C)
    na, nb, nc = a.shape[0], b.shape[0], c.shape[0]
    P = _bicimle(xp, psi)
    tek = (P.ndim == 1)
    if tek:
        P = P.reshape(1, -1)
    Bn = P.shape[0]
    T = P.reshape(Bn, na, nb, nc)
    T = xp.einsum("bijk,xi->bxjk", T, a)
    T = xp.einsum("bxjk,yj->bxyk", T, b)
    T = xp.einsum("bxyk,zk->bxyz", T, c)
    out = T.reshape(Bn, na * nb * nc)
    return out.reshape(-1) if tek else out


SEKTOR: Tuple[Tuple[str, int, int], ...] = (
    ("sentaks", 0, 512),
    ("ontoloji", 512, 2560),
    ("mantık", 2560, 4096),
)


def blok_carp(psi, bloklar: Sequence, xp=None, sektor=None):
    xp = xp or np
    P = _bicimle(xp, psi)
    tek = (P.ndim == 1)
    if tek:
        P = P.reshape(1, -1)
    d = P.shape[-1]
    sek = sektor or SEKTOR
    olcek = d / float(sek[-1][2])
    out = xp.zeros_like(P)
    for (ad, i0, i1), M in zip(sek, bloklar):
        i, j = int(i0 * olcek), min(d, int(i1 * olcek))
        if j <= i:
            continue
        m = _bicimle(xp, M)
        out[:, i:j] = P[:, i:j] @ m.T
    return out.reshape(-1) if tek else out


def faz_cevir(psi, teta, xp=None):
    xp = xp or np
    P = _bicimle(xp, psi)
    d = P.shape[-1]
    t = np.asarray(teta, float).reshape(-1)
    if t.size != d:
        from kuantum.qudit import agirlik
        t = agirlik(d, t)
    faz = _bicimle(xp, np.exp(-1j * t))
    return P * faz


_FUSED_KAYNAK = r"""
extern "C" __global__
void lie_chebyshev_fused(
        const float* __restrict__ W,      // (B, d) Cartan ağırlıkları
        const float* __restrict__ cs,     // (n,)   T-serisi katsayıları
        const float* __restrict__ ss,     // (n,)   U-serisi katsayıları
        float2* __restrict__ out,         // (B, d) netice
        const int B, const int d, const int n)
{
    extern __shared__ float sm[];         // SRAM: d float
    const int b = blockIdx.x;
    if (b >= B) return;

    // --- durumu SRAM'e bir kere çek
    for (int i = threadIdx.x; i < d; i += blockDim.x)
        sm[i] = W[b * d + i];
    __syncthreads();

    for (int i = threadIdx.x; i < d; i += blockDim.x) {
        const float x = sm[i];
        const float ikix = 2.0f * x;

        // Clenshaw -- T serisi
        float b1 = 0.0f, b2 = 0.0f, t;
        for (int j = n - 1; j >= 1; --j) { t = cs[j] + ikix * b1 - b2; b2 = b1; b1 = t; }
        const float reel = cs[0] + x * b1 - b2;

        // Clenshaw -- U serisi (kapanış farklı: a0 + 2x b1 - b2)
        b1 = 0.0f; b2 = 0.0f;
        for (int j = n - 1; j >= 1; --j) { t = ss[j] + ikix * b1 - b2; b2 = b1; b1 = t; }
        const float sanal = ss[0] + ikix * b1 - b2;

        const float e = __expf(reel);
        out[b * d + i] = make_float2(e * __cosf(sanal), e * __sinf(sanal));
    }
}
"""


def cekirdek(W, cs, ss, ne: str = "oto") -> Dict[str, Any]:
    W = np.asarray(W, np.float32)
    cs = np.asarray(cs, np.float32).reshape(-1)
    ss = np.asarray(ss, np.float32).reshape(-1)
    B, d = W.shape
    n = cs.size

    if ne in ("oto", "cupy"):
        try:
            import cupy as cp
            mod = cp.RawModule(code=_FUSED_KAYNAK, options=("-use_fast_math",))
            fn = mod.get_function("lie_chebyshev_fused")
            Wg = cp.asarray(W)
            csg, ssg = cp.asarray(cs), cp.asarray(ss)
            out = cp.empty((B, d), cp.complex64)
            iplik = min(256, max(32, d))
            fn((B,), (iplik,),
               (Wg, csg, ssg, out, np.int32(B), np.int32(d), np.int32(n)),
               shared_mem=4 * d)
            return {"psi": out, "çekirdek": "cupy-fused", "gpu": True,
                    "sram_bayt": 4 * d}
        except Exception as exc:
            if ne == "cupy":
                raise
            _son = "%s: %s" % (type(exc).__name__, str(exc)[:60])
    else:
        _son = "denenmedi"

    if ne in ("oto", "torch"):
        try:
            import torch
            aygit = "cuda" if torch.cuda.is_available() else "cpu"
            Wt = torch.as_tensor(W, device=aygit)
            cst = torch.as_tensor(cs, device=aygit)
            sst = torch.as_tensor(ss, device=aygit)
            ikix = 2.0 * Wt
            b1 = torch.zeros_like(Wt); b2 = torch.zeros_like(Wt)
            for j in range(n - 1, 0, -1):
                b1, b2 = cst[j] + ikix * b1 - b2, b1
            reel = cst[0] + Wt * b1 - b2
            b1 = torch.zeros_like(Wt); b2 = torch.zeros_like(Wt)
            for j in range(n - 1, 0, -1):
                b1, b2 = sst[j] + ikix * b1 - b2, b1
            sanal = sst[0] + ikix * b1 - b2
            e = torch.exp(reel - reel.amax(dim=1, keepdim=True))
            psi = torch.complex(e * torch.cos(sanal), e * torch.sin(sanal))
            psi = psi / torch.linalg.vector_norm(psi, dim=1, keepdim=True)
            return {"psi": psi, "çekirdek": "torch-" + aygit,
                    "gpu": aygit == "cuda"}
        except Exception as exc:
            if ne == "torch":
                raise
            _son = "%s: %s" % (type(exc).__name__, str(exc)[:60])

    ikix = 2.0 * W
    b1 = np.zeros_like(W); b2 = np.zeros_like(W)
    for j in range(n - 1, 0, -1):
        b1, b2 = cs[j] + ikix * b1 - b2, b1
    reel = cs[0] + W * b1 - b2
    b1 = np.zeros_like(W); b2 = np.zeros_like(W)
    for j in range(n - 1, 0, -1):
        b1, b2 = ss[j] + ikix * b1 - b2, b1
    sanal = ss[0] + ikix * b1 - b2
    reel = reel - reel.max(axis=1, keepdims=True)
    e = np.exp(reel)
    psi = (e * np.cos(sanal)).astype(np.complex64)
    psi += 1j * (e * np.sin(sanal)).astype(np.complex64)
    psi /= np.maximum(np.linalg.norm(psi, axis=1, keepdims=True), 1e-30)
    return {"psi": psi, "çekirdek": "numpy", "gpu": False,
            "gpu_sebep": _son}


def rapor() -> str:
    import time

    r = np.random.default_rng(0)
    s = ["=== HIZLI -- boyut patlamasının dört tedbiri ===", ""]

    xp, ad, gpu = hesap("oto")
    s += ["  ÇEKİRDEK: %s  (GPU: %s)" % (ad, "EVET" if gpu else "hayır"), ""]

    na = nb = nc = 16
    d = na * nb * nc
    A = r.normal(size=(na, na)); Bm = r.normal(size=(nb, nb))
    C = r.normal(size=(nc, nc))
    psi = r.normal(size=(8, d)) + 1j * r.normal(size=(8, d))
    t0 = time.perf_counter(); kr = kronecker(psi, A, Bm, C); t_kr = time.perf_counter() - t0
    M = np.kron(np.kron(A, Bm), C)
    t0 = time.perf_counter(); yg = psi @ M.T; t_yg = time.perf_counter() - t0
    s += ["  1. KRONECKER LİF AYRIŞIMI (d = 16·16·16 = 4096)",
          "    yoğun ile fark  : %.3e  (0 = birebir aynı mana)"
          % float(np.max(np.abs(kr - yg))),
          "    lifli süre      : %.2f ms" % (1e3 * t_kr),
          "    yoğun süre      : %.2f ms  (%.1f×)" % (1e3 * t_yg, t_yg / max(t_kr, 1e-12)),
          "    FLOP  yoğun     : %d" % (2 * d * d),
          "    FLOP  lifli     : %d  (%.0f× az)"
          % (2 * d * (na + nb + nc), (2 * d * d) / (2 * d * (na + nb + nc))),
          "    operatör belleği: %.1f MB → %.1f KB"
          % (d * d * 4 / 1e6, (na * na + nb * nb + nc * nc) * 4 / 1e3)]

    boy = [j - i for _, i, j in SEKTOR]
    blk = [r.normal(size=(n, n)) for n in boy]
    p2 = r.normal(size=(4, 4096)) + 1j * r.normal(size=(4, 4096))
    t0 = time.perf_counter(); blok_carp(p2, blk); t_bl = time.perf_counter() - t0
    tam = sum(n * n for n in boy)
    s += ["", "  2. BLOK-DİYAGONAL SÜPERSEÇİM",
          "    sektörler       : %s" % ", ".join(
              "%s(%d)" % (a, n) for (a, _, _), n in zip(SEKTOR, boy)),
          "    blok elemanı    : %d" % tam,
          "    yoğun elemanı   : %d" % (4096 * 4096),
          "    tasarruf        : %%%.1f" % (100 * (1 - tam / (4096 * 4096))),
          "    süre            : %.2f ms" % (1e3 * t_bl)]

    p3 = r.normal(size=(64, 4096)) + 1j * r.normal(size=(64, 4096))
    tt = r.normal(size=8)
    t0 = time.perf_counter(); faz_cevir(p3, tt); t_fz = time.perf_counter() - t0
    s += ["", "  3. CARTAN KÖŞEGENİ -- NOKTASAL FAZ",
          "    O(d²) işlem     : %d" % (4096 * 4096),
          "    O(d)  işlem     : %d   (%d× az)" % (4096, 4096),
          "    süre (B=64)     : %.2f ms" % (1e3 * t_fz)]

    W = r.normal(size=(4096, 16)).astype(np.float32)
    cs = r.normal(size=9).astype(np.float32); ss = r.normal(size=9).astype(np.float32)
    t0 = time.perf_counter(); k = cekirdek(W, cs, ss); t_ck = time.perf_counter() - t0
    s += ["", "  4. KAYNAŞIK ÇEKİRDEK (SRAM içinde icra)",
          "    fiilen koşan    : %s" % k["çekirdek"],
          "    GPU mu          : %s" % ("EVET" if k["gpu"] else "HAYIR"),
          "    süre            : %.2f ms" % (1e3 * t_ck)]
    if not k["gpu"]:
        s += ["    GPU sebebi      : %s" % k.get("gpu_sebep", "-"),
              "",
              "    AÇIKÇA: CuPy ham çekirdeği (_FUSED_KAYNAK) ve Torch",
              "    yolu TAM yazılmıştır; bu makinede cupy/torch kurulu",
              "    olmadığı için DERLENMEDİ ve KOŞMADI. 'Çalışıyor'",
              "    denmiyor -- 'yazıldı, denenmedi' deniyor (H100)."]
    return "\n".join(s)
