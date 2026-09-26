from __future__ import annotations

import os
import re
import subprocess
import time
from typing import Any, Dict, Optional

import numpy as np

__all__ = ["cekirdek_sayisi", "onbellekler", "bellek_baytlari",
           "tamsayi_hizi", "bellek_haddi", "gpu_var_mi", "hesap"]


def cekirdek_sayisi() -> int:
    try:
        return max(1, len(os.sched_getaffinity(0)))
    except AttributeError:
        return max(1, int(os.cpu_count() or 1))


def onbellekler() -> Dict[str, Optional[int]]:
    kok = "/sys/devices/system/cpu/cpu0/cache"
    o: Dict[str, Optional[int]] = {"L1d": None, "L2": None, "L3": None}
    if not os.path.isdir(kok):
        return o
    for d in sorted(os.listdir(kok)):
        yol = os.path.join(kok, d)
        if not d.startswith("index"):
            continue
        try:
            with open(os.path.join(yol, "level")) as f:
                sev = int(f.read().strip())
            with open(os.path.join(yol, "type")) as f:
                tip = f.read().strip()
            with open(os.path.join(yol, "size")) as f:
                ham = f.read().strip()
        except OSError:
            continue
        m = re.match(r"(\d+)([KMG]?)", ham)
        if not m:
            continue
        bayt = int(m.group(1)) * {"": 1, "K": 1024, "M": 1024 ** 2,
                                  "G": 1024 ** 3}[m.group(2)]
        ad = ("L1d" if sev == 1 and tip.startswith("Data")
              else ("L%d" % sev if sev > 1 else None))
        if ad in o and o[ad] is None:
            o[ad] = bayt
    return o


def bellek_baytlari() -> Dict[str, Optional[int]]:
    o: Dict[str, Optional[int]] = {"toplam": None, "erişilebilir": None,
                                   "kap_haddi": None, "kaynak": None}
    try:
        with open("/proc/meminfo") as f:
            m = {}
            for satir in f:
                ad, _, kalan = satir.partition(":")
                p = kalan.split()
                if p:
                    m[ad.strip()] = int(p[0]) * 1024
    except OSError:
        return o
    o["toplam"] = m.get("MemTotal")
    o["erişilebilir"] = m.get("MemAvailable", m.get("MemFree"))
    o["kaynak"] = "/proc/meminfo"
    for yol in ("/sys/fs/cgroup/memory.max",
                "/sys/fs/cgroup/memory/memory.limit_in_bytes"):
        try:
            with open(yol) as f:
                v = f.read().strip()
        except OSError:
            continue
        if v.isdigit() and int(v) < (1 << 62):
            o["kap_haddi"] = int(v)
            o["kaynak"] = yol
        break
    return o


def bellek_haddi() -> Optional[int]:
    b = bellek_baytlari()
    aday = [x for x in (b["erişilebilir"], b["kap_haddi"]) if x]
    return int(min(aday)) if aday else None


def tamsayi_hizi(satir: int = 4096, kelime: int = 64,
                 tekrar: int = 20) -> Dict[str, Any]:
    from .gfni import symplectic_gfni, yoklama
    r = np.random.default_rng(0)
    X = r.integers(0, 1 << 62, size=(satir, kelime), dtype=np.uint64)
    Z = r.integers(0, 1 << 62, size=(satir, kelime), dtype=np.uint64)
    m = r.integers(0, 1 << 62, size=kelime, dtype=np.uint64)
    f = r.integers(0, 1 << 62, size=kelime, dtype=np.uint64)
    bayt = float(X.nbytes + Z.nbytes) * 2.0
    donanim_var = bool(yoklama().get("koşuyor"))
    if donanim_var:
        symplectic_gfni(X, Z, m, f)
        t0 = time.perf_counter()
        for _ in range(int(tekrar)):
            symplectic_gfni(X, Z, m, f)
        sure = (time.perf_counter() - t0) / int(tekrar)
        usul = "AVX-512 XOR/AND/POPCNT (C, ctypes)"
    else:
        t0 = time.perf_counter()
        for _ in range(int(tekrar)):
            X ^= m[None, :]
            Z ^= (X & f[None, :])
        sure = (time.perf_counter() - t0) / int(tekrar)
        usul = "numpy bit ameliyeleri"
    return {"usul": usul, "donanım": donanim_var, "bayt": bayt,
            "sn": float(sure), "bant_gb": float(bayt / sure / 1e9),
            "satır": int(satir), "kelime": int(kelime)}


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


def gpu_var_mi() -> Dict[str, Any]:
    o: Dict[str, Any] = {"cupy": False, "torch": False, "nvidia_smi": False,
                         "cihaz": [], "sebep": ""}
    try:
        import cupy
        o["cupy"] = True
    except Exception as e:
        o["sebep"] += "cupy: %s; " % type(e).__name__
    try:
        import torch
        o["torch"] = bool(torch.cuda.is_available())
    except Exception as e:
        o["sebep"] += "torch: %s; " % type(e).__name__
    try:
        r = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total,pcie.link.gen.max,"
             "pcie.link.width.max", "--format=csv,noheader"],
            capture_output=True, text=True, timeout=20)
        if r.returncode == 0 and r.stdout.strip():
            o["nvidia_smi"] = True
            o["cihaz"] = [x.strip() for x in r.stdout.strip().splitlines()]
    except Exception as e:
        o["sebep"] += "nvidia-smi: %s; " % type(e).__name__
    o["var"] = bool(o["cupy"] or o["torch"] or o["nvidia_smi"])
    return o
