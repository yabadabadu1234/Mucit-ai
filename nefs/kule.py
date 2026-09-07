from __future__ import annotations

from typing import List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["kule_kur", "kaba_kademe", "kaba", "ince", "TAVAN"]

TAVAN = 256


def kule_kur(X: np.ndarray) -> List[np.ndarray]:
    x = np.asarray(X, float)
    kademeler = [x]
    while len(x) > 1:
        if len(x) % 2:
            x = np.vstack([x, x[-1:]])
        a, b = x[0::2], x[1::2]
        x = (a + b) / np.sqrt(2.0)
        kademeler.append(x)
    return kademeler


def kaba_kademe(kademeler: Sequence[np.ndarray], tavan: int = TAVAN) -> int:
    for i, k in enumerate(kademeler):
        if len(k) <= tavan:
            return i
    return len(kademeler) - 1


def kaba(X: np.ndarray, tavan: int = TAVAN) -> Tuple[np.ndarray, int, float]:
    n = len(X)
    if n <= tavan:
        return np.asarray(X, float), 0, 0.0
    kademeler = kule_kur(X)
    i = kaba_kademe(kademeler, tavan)
    Y = kademeler[i]
    geri = ince(Y, n, i)
    kayip = float(np.linalg.norm(geri - X) / (np.linalg.norm(X) + 1e-12))
    return Y, i, kayip


def ince(Y: np.ndarray, n: int, kademe: int) -> np.ndarray:
    kat = 2 ** kademe
    G = np.repeat(Y, kat, axis=0)[:n]
    if len(G) < n:
        G = np.vstack([G, np.repeat(Y[-1:], n - len(G), axis=0)])
    return G / (np.sqrt(2.0) ** kademe)


def rapor() -> str:
    import time

    rng = np.random.default_rng(0)
    s = ["KULE -- hiyerarşik taşıyıcı: kazanç ve kayıp", ""]
    s.append("  %-8s %-8s %-10s %-12s %-12s %s"
             % ("satır", "kademe", "kaba satır", "kayıp", "kule sn",
                "n² kıyas"))
    for n in (64, 256, 1024, 4096):
        X = rng.normal(size=(n, 12))
        t0 = time.perf_counter()
        Y, k, kayip = kaba(X, tavan=64)
        t1 = time.perf_counter() - t0
        s.append("  %-8d %-8d %-10d %-12.4f %-12.4f %d kat"
                 % (n, k, len(Y), kayip, t1,
                    (n * n) // max(len(Y) * len(Y), 1)))
    s.append("")
    s.append("  Kayıp SIFIR DEĞİLDİR ve olmamalıdır: ortalama, iki satır")
    s.append("  arasındaki farkı o kademede siler. Sıfır çıksaydı ya kule")
    s.append("  hiç çalışmıyor ya da ölçü kör olurdu.")
    s.append("")
    s.append("  Kule DİK mi? (norm korunuyor mu -- toplam kanadında)")
    X = rng.normal(size=(16, 5))
    kad = kule_kur(X)
    s.append("    ham ‖X‖ = %.6f" % float(np.linalg.norm(X)))
    for i, k in enumerate(kad[:4]):
        s.append("    kademe %d: %2d satır, ‖·‖ = %.6f"
                 % (i, len(k), float(np.linalg.norm(k))))
    s.append("    (norm düşüyor; düşen kısım ATILAN FARK kanadıdır --")
    s.append("     kule izometri değildir ve öyle iddia edilmiyor.)")
    return "\n".join(s)


if __name__ == "__main__":
    print(rapor())
