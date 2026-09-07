from __future__ import annotations

import os
import re
import subprocess
import time
from typing import Any, Dict, List, Optional

import numpy as np

__all__ = ["cekirdek_sayisi", "onbellekler", "saat_ghz", "simd_bilgisi",
           "bellek_bandi", "bellek_baytlari", "tamsayi_hizi",
           "bellek_haddi", "gpu_var_mi", "gpu_olcu",
           "donanim", "rapor"]

_ONBELLEK: Dict[str, Any] = {}


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


def saat_ghz() -> Dict[str, Optional[float]]:
    ilan: Optional[float] = None
    try:
        with open("/proc/cpuinfo") as f:
            met = f.read()
        m = re.search(r"model name.*?@\s*([\d.]+)\s*GHz", met)
        if m:
            ilan = float(m.group(1))
        else:
            m = re.search(r"cpu MHz\s*:\s*([\d.]+)", met)
            if m:
                ilan = float(m.group(1)) / 1000.0
    except OSError:
        pass
    x = np.uint64(1)
    n = 3_000_000
    t0 = time.perf_counter()
    for _ in range(n):
        x = x + np.uint64(1)
    sure = time.perf_counter() - t0
    return {"ilan_ghz": ilan, "tur_ns": float(sure / n * 1e9)}


def simd_bilgisi() -> Dict[str, Any]:
    from .gfni import cpuid, olc, yoklama
    y = yoklama()
    o: Dict[str, Any] = {
        "gfni_koşuyor": bool(y.get("koşuyor")),
        "gfni_sebep": y.get("sebep"),
        "cpuid_bayrağı": (y.get("cpuid") or {}),
        "derlendi": bool(y.get("derlendi")),
        "bayrak": y.get("bayrak"),
    }
    o["cpuid_ayrıştı"] = bool(
        o["gfni_koşuyor"] and not (o["cpuid_bayrağı"] or {}).get("GFNI", False))
    o["genişlik_bit"] = 512 if o["gfni_koşuyor"] else None
    g = olc() if o["gfni_koşuyor"] else {}
    o["gfni_gb"] = g.get("gfni_gb")
    o["tablo_gb"] = g.get("tablo_gb")
    o["gfni_hızı"] = g.get("hız")
    return o


def bellek_bandi(bayt: int = 1 << 26, tekrar: int = 5) -> Dict[str, float]:
    n = max(1 << 16, int(bayt) // 8)
    b = np.ones(n, np.float64)
    c = np.full(n, 2.0)
    a = np.empty(n, np.float64)
    s = 3.0
    np.add(b, s * c, out=a)
    t0 = time.perf_counter()
    for _ in range(int(tekrar)):
        np.add(b, s * c, out=a)
    sure = (time.perf_counter() - t0) / int(tekrar)
    trafik = 3.0 * n * 8.0
    return {"bayt": float(trafik), "sn": float(sure),
            "bant_gb": float(trafik / sure / 1e9)}


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


def gpu_olcu(bayt: int = 1 << 26, tekrar: int = 10) -> Dict[str, Any]:
    v = gpu_var_mi()
    o: Dict[str, Any] = {
        "var": bool(v["var"]), "yoklama": v, "kart": None,
        "vram_bant_gb": None, "pcie_bant_gb": None,
        "tamsayı_bant_gb": None, "vram_bayt": None, "ad": None,
        "kütüphane": None}
    if not v["var"]:
        o["sebep"] = ("GPU YOK -- bu makinede VRAM/PCIe ölçülemez. "
                      "Zabıtın rakamları iddiadır, ölçü değildir.")
        return o
    try:
        import cupy as cp
    except Exception:
        o["sebep"] = ("GPU görünüyor fakat ``cupy`` yok: cihaz-içi ölçü "
                      "yapılamadı. Kart listesi ``yoklama``dadır.")
        o["kart"] = len(v["cihaz"]) or None
        return o
    o["kütüphane"] = "cupy"
    o["kart"] = int(cp.cuda.runtime.getDeviceCount())
    ozellik = cp.cuda.runtime.getDeviceProperties(0)
    o["ad"] = ozellik["name"].decode() if isinstance(
        ozellik["name"], bytes) else str(ozellik["name"])
    o["vram_bayt"] = int(ozellik["totalGlobalMem"])
    n = max(1 << 20, int(bayt) // 8)
    a = cp.ones(n, cp.float64)
    b = cp.empty(n, cp.float64)
    cp.cuda.Stream.null.synchronize()
    b[:] = a
    cp.cuda.Stream.null.synchronize()
    t0 = time.perf_counter()
    for _ in range(int(tekrar)):
        b[:] = a
    cp.cuda.Stream.null.synchronize()
    sure = (time.perf_counter() - t0) / int(tekrar)
    o["vram_bant_gb"] = float(2.0 * n * 8 / sure / 1e9)
    h = np.ones(n, np.float64)
    d = cp.empty(n, cp.float64)
    d.set(h)
    cp.cuda.Stream.null.synchronize()
    t0 = time.perf_counter()
    for _ in range(int(tekrar)):
        d.set(h)
    cp.cuda.Stream.null.synchronize()
    o["pcie_bant_gb"] = float(n * 8 / ((time.perf_counter() - t0)
                                       / int(tekrar)) / 1e9)
    X = cp.asarray(np.random.default_rng(0).integers(
        0, 1 << 62, size=(4096, 64), dtype=np.uint64))
    M = cp.asarray(np.random.default_rng(1).integers(
        0, 1 << 62, size=64, dtype=np.uint64))
    X ^= M[None, :]
    cp.cuda.Stream.null.synchronize()
    t0 = time.perf_counter()
    for _ in range(int(tekrar)):
        X ^= M[None, :]
    cp.cuda.Stream.null.synchronize()
    sure = (time.perf_counter() - t0) / int(tekrar)
    o["tamsayı_bant_gb"] = float(2.0 * X.nbytes / sure / 1e9)
    return o


def donanim(yeniden: bool = False) -> Dict[str, Any]:
    if not yeniden and "hepsi" in _ONBELLEK:
        return _ONBELLEK["hepsi"]
    o = {
        "cpu": {
            "çekirdek": cekirdek_sayisi(),
            "önbellek": onbellekler(),
            "saat": saat_ghz(),
            "simd": simd_bilgisi(),
            "bant": bellek_bandi(),
            "bellek": bellek_baytlari(),
            "tamsayı": tamsayi_hizi(),
        },
        "gpu": gpu_olcu(),
    }
    _ONBELLEK["hepsi"] = o
    return o


def rapor() -> str:
    d = donanim()
    c, g = d["cpu"], d["gpu"]
    ob = c["önbellek"]
    sm = c["simd"]
    s = ["=== DONANIM -- HEPSİ YOKLANDI, HİÇBİRİ ELLE YAZILMADI ===", "",
         "  --- CPU ---",
         "    kullanılabilir çekirdek : %d" % c["çekirdek"],
         "    L1d / L2 / L3           : %s / %s / %s"
         % tuple("%d KB" % (v // 1024) if v else "?"
                 for v in (ob["L1d"], ob["L2"], ob["L3"])),
         "    ilan edilen saat        : %s"
         % ("%.2f GHz" % c["saat"]["ilan_ghz"] if c["saat"]["ilan_ghz"]
            else "okunamadı"),
         "    bellek bandı (STREAM)   : %.2f GB/s   (ÖLÇÜLDÜ)"
         % c["bant"]["bant_gb"],
         "    symplectic tamsayı bandı: %.2f GB/s   (%s)"
         % (c["tamsayı"]["bant_gb"], c["tamsayı"]["usul"]),
         "",
         "  --- GALOIS KOMUTLARI (icra ile tayin, bayrakla DEĞİL) ---",
         "    GFNI koşuyor mu : %s   (%s)"
         % (sm["gfni_koşuyor"], sm["gfni_sebep"]),
         "    SIMD genişliği  : %s bit"
         % (sm["genişlik_bit"] or "?"),
         "    GFNI / tablo    : %s"
         % ("%.2f GB/s  vs  %.2f GB/s  →  %.1f× hızlı"
            % (sm["gfni_gb"], sm["tablo_gb"], sm["gfni_hızı"])
            if sm["gfni_gb"] else "ölçülemedi")]
    if sm["cpuid_ayrıştı"]:
        s += ["    ⚠ CPUID 'GFNI yok' diyor, komut KOŞUYOR: bayrak",
              "      maskelenmiş. Karar icradan çıktı, bayraktan değil."]
    s += ["", "  --- GPU ---"]
    if not g["var"]:
        s += ["    GPU YOK. VRAM, PCIe ve cihaz-içi hız **ölçülemedi**.",
              "    Bu makinede o sayılar ``None``dur ve None kalır;",
              "    zabıttaki 300 GB/s / 31,5 GB/s birer **iddiadır**,",
              "    ölçü değildir ve ölçü yerine geçirilmez.",
              "    yoklama: %s" % (g["yoklama"]["sebep"] or "-")]
    else:
        s += ["    kart            : %s × %s" % (g["kart"], g["ad"]),
              "    VRAM            : %s"
              % ("%.1f GB" % (g["vram_bayt"] / 1e9) if g["vram_bayt"]
                 else "?"),
              "    VRAM bandı      : %s   (ÖLÇÜLDÜ)"
              % ("%.1f GB/s" % g["vram_bant_gb"] if g["vram_bant_gb"]
                 else "ölçülemedi"),
              "    PCIe bandı      : %s   (ÖLÇÜLDÜ)"
              % ("%.1f GB/s" % g["pcie_bant_gb"] if g["pcie_bant_gb"]
                 else "ölçülemedi"),
              "    tamsayı bandı   : %s"
              % ("%.1f GB/s" % g["tamsayı_bant_gb"]
                 if g["tamsayı_bant_gb"] else "ölçülemedi")]
    return "\n".join(s)


if __name__ == "__main__":
    print(rapor())
