"""
idrak/kubit.py - Qudit Durum ve Kuantum Kapı Katmanı
"""

import math
import cmath
from typing import List, Tuple, Any
from matematik.temel import KuantumDurum, bargmann_n_nokta, HAS_NUMPY


def norm_korunumu_testi(d: int = 16) -> Tuple[bool, float]:
    """||psi||^2 = 1 norm korunumunun teyidi"""
    v = [complex(math.cos(k), math.sin(k)) for k in range(d)]
    durum = KuantumDurum(v)
    norm_kare = sum(abs(x)**2 for x in durum.v)
    fark = abs(norm_kare - 1.0)
    return fark < 1e-12, fark


def kontrollu_cycle_kapi_testi() -> Tuple[float, float]:
    """n=3 durum için C-CYCLE SWAP testi"""
    d1 = KuantumDurum([complex(1, 0), complex(0, 0)], etiket="q1")
    d2 = KuantumDurum([complex(0.7071, 0), complex(0.7071, 0)], etiket="q2")
    d3 = KuantumDurum([complex(0, 0), complex(1, 0)], etiket="q3")
    r3, phi3, delta3, _ = bargmann_n_nokta([d1, d2, d3])
    p0 = (1.0 + delta3.real) / 2.0
    p1 = (1.0 - delta3.real) / 2.0
    return p0, p1


if __name__ == "__main__":
    basarili, fark = norm_korunumu_testi()
    p0, p1 = kontrollu_cycle_kapi_testi()
    print(f"[idrak.kubit] Norm Korunumu: {basarili} (Sapma: {fark:.2e})")
    print(f"[idrak.kubit] C-CYCLE Testi: P(0)={p0:.4f}, P(1)={p1:.4f}")
