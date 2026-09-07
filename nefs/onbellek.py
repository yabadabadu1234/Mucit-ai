from __future__ import annotations

import os
from typing import Any, Dict, Optional, Tuple

import numpy as np

__all__ = ["onbellek_boylari", "yigin_sec", "rapor"]

PAY: float = 0.20

ASGARI: int = 8
AZAMI: int = 4096


def onbellek_boylari() -> Dict[str, int]:
    out = {"L1": 0, "L2": 0, "L3": 0}
    kok = "/sys/devices/system/cpu/cpu0/cache"
    if not os.path.isdir(kok):
        return out
    for ad in sorted(os.listdir(kok)):
        if not ad.startswith("index"):
            continue
        try_yol = os.path.join(kok, ad)
        boy_yol = os.path.join(try_yol, "size")
        tip_yol = os.path.join(try_yol, "level")
        if not (os.path.exists(boy_yol) and os.path.exists(tip_yol)):
            continue
        ham = open(boy_yol).read().strip()
        kademe = open(tip_yol).read().strip()
        carp = 1024 if ham.endswith("K") else (1024 * 1024
                                               if ham.endswith("M") else 1)
        sayi = int(ham.rstrip("KMG") or 0) * carp
        anahtar = "L%s" % kademe
        if anahtar in out:
            out[anahtar] = max(out[anahtar], sayi)
    return out


def yigin_sec(d: int, tip=np.complex64, gpu: bool = False,
              cekirdek: int = 0) -> Dict[str, Any]:
    d = int(d)
    assert d >= 2, "qudit boyutu en az 2 olmalı"
    bayt = int(np.dtype(tip).itemsize)
    o = onbellek_boylari()

    if gpu:
        cek = int(cekirdek) or 7424
        B = int(min(AZAMI, max(ASGARI, 4 * cek // max(1, d // 512))))
        return {"B": B, "yol": "gpu", "sebep":
                "çekirdek doygunluğu (zabıt: B=512+); çekirdek=%d" % cek,
                "önbellek": o, "durum_bayt": B * d * bayt}

    hane = o.get("L3", 0) or o.get("L2", 0)
    if hane <= 0:
        return {"B": 128, "yol": "varsayılan", "sebep":
                "önbellek boyu okunamadı (/sys yok); 128'e düşüldü",
                "önbellek": o, "durum_bayt": 128 * d * bayt}

    B = int(PAY * hane / (d * bayt))
    B = max(ASGARI, min(AZAMI, B))
    B = 1 << int(np.floor(np.log2(B)))
    B = max(ASGARI, B)
    return {"B": int(B), "yol": "cpu-önbellek",
            "sebep": "L3=%.1f MB, pay %.2f, d=%d, %d bayt/genlik"
                     % (hane / 1e6, PAY, d, bayt),
            "önbellek": o, "durum_bayt": int(B) * d * bayt}


def rapor(d: int = 4096) -> str:
    o = onbellek_boylari()
    s = ["=== ÖNBELLEK MİZANI -- yığın boyu donanımdan ===", "",
         "  L1 = %6.0f KB   L2 = %6.0f KB   L3 = %6.0f KB   %s"
         % (o["L1"] / 1024, o["L2"] / 1024, o["L3"] / 1024,
            "" if o["L3"] else "(okunamadı)"), ""]
    for tip in (np.complex64, np.complex128):
        r = yigin_sec(d, tip)
        s.append("  d=%-6d %-11s → B = %-5d  (durum %.1f MB)"
                 % (d, np.dtype(tip).name, r["B"], r["durum_bayt"] / 1e6))
        s.append("      sebep: %s" % r["sebep"])
    g = yigin_sec(d, np.complex64, gpu=True)
    s += ["", "  GPU dalı (zabıtın hükmü): B = %d -- %s"
          % (g["B"], g["sebep"])]
    return "\n".join(s)


if __name__ == "__main__":
    print(rapor())
