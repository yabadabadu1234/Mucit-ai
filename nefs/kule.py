"""
Kule: ana modelin (``nefs/``) kendi kendine uzun pencere tutması.

**Mesele.** ``main/`` modeli 65.536 belirteci 8 MB'ta tutuyor; ana model
1.024 satırda 12,5 saniye yiyor ve ölçüldüğüne göre maliyeti karesel:
64→0,06 sn, 256→3,09 sn, 1024→12,5 sn. Sebep melekelerin kendisi değil,
**satır ekseninin** üç yerde kare alınmasıdır:

* 𝒪₁ Müşahede'nin öz-dikkati      -- ``softmax(QKᵀ/√d)V``  → ``n×n``
* 𝒪₁₁ Tenakuz'un çelişki dizeyi   -- ``C = −S(AᵀA)Sᵀ``     → ``n×n``
* 𝒪₂₂ İllet'in nedensellik çizgesi -- ``A_neden``           → ``n×n``

**Hüküm.** Melekeleri değiştirmek gerekmez; **taşıyıcıyı** değiştirmek
gerekir. ``main/`` modelinin MERA'sı tam olarak bunu yapıyordu: satırları
ikişer ikişer kaba taneleyip ``log₂N`` kademelik bir kule kurmak.
Ana modele nakledilen icat budur -- kübit, dalga yahut faz değil,
**hiyerarşik taşıyıcı**.

    ham satırlar (n)
      → kule: ikişer birleştirme, her kademede yarıya iner
      → tavan altındaki ilk kademe = "kaba görüş" (≤ tavan satır)
      → karesel melekeler kaba görüşte koşar        → O(tavan²), sabit
      → netice ince eksene GERİ YAYILIR (pass-through, Kademe 4)

Böylece bütün maliyet ``O(n·d + tavan²)`` olur: satır sayısında
**doğrusal**.

**Dürüstlük şartı.** Kaba taneleme ortalamadır ve ortalama bilgi kaybeder:
iki satır bir düğümde birleştiğinde aralarındaki fark o kademede
görünmez olur. Kayıp gizlenmez, **ölçülür** (``kule.kayıp``) ve ince
eksen silinmez -- geri yayılım artık bağıdır, yerine geçme değildir
(nizamnamenin "kalıntı ve muhafaza bağlantıları" şartı). Şahit
bölütlemesi de bundan etkilenmez: o ham ``E`` üzerinde yapılır.
"""
from __future__ import annotations

from typing import List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["kule_kur", "kaba_kademe", "kaba", "ince", "TAVAN"]

TAVAN = 256          # karesel melekelerin göreceği azamî satır sayısı


def kule_kur(X: np.ndarray) -> List[np.ndarray]:
    """İkişer kaba tanelemeyle kule. Kademe sayısı ``⌈log₂ n⌉ + 1``.

    Birleştirme **dik**tir: ``(a+b)/√2`` ile ``(a−b)/√2`` çiftinden
    yalnız toplam taşınır, fark ise o kademede ``kayıp`` olarak ölçülür.
    Bu, MERA'nın izometri adımının en sade hâlidir; öğrenilen parametre
    yoktur, çünkü burada yapılan şey öğrenmek değil **taşımaktır**.
    """
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
    """Satır sayısı tavanın altına inen **ilk** kademenin indeksi."""
    for i, k in enumerate(kademeler):
        if len(k) <= tavan:
            return i
    return len(kademeler) - 1


def kaba(X: np.ndarray, tavan: int = TAVAN) -> Tuple[np.ndarray, int, float]:
    """``X``i tavan altına indir; (kaba görüş, kademe, kayıp) döndür.

    ``kayıp``, kaba görüşten ince eksene geri yayıldığında doğan bağıl
    hatadır -- yani ortalamanın sildiği fark. Sıfır değilse ve bu
    saklanırsa, "uzun pencere tutuyoruz" iddiası yalan olurdu.
    """
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
    """Kaba görüşü ince eksene geri yay -- ``n`` satıra.

    Her kaba düğüm, altındaki ``2^kademe`` satıra aynı katkıyı verir
    (ölçek ``√2`` başına düşürülür ki norm mertebesi korunsun). Bu bir
    **artık bağıdır**: melekenin kendi ince hesabının yerine geçmez,
    ona eklenir.
    """
    kat = 2 ** kademe
    G = np.repeat(Y, kat, axis=0)[:n]
    if len(G) < n:                       # tek sayı taşmaları
        G = np.vstack([G, np.repeat(Y[-1:], n - len(G), axis=0)])
    return G / (np.sqrt(2.0) ** kademe)


def rapor() -> str:                                     # pragma: no cover
    """Kendi kendini gösterme (H126): **kazanç ve kayıp yan yana**.

    Kule'nin iddiası ikilidir ve ikisi birden ölçülmezse yalan olur:
    (a) karesel maliyet doğrusala iner, (b) bedeli kaba tanelemenin
    sildiği farktır. İkincisi gizlenirse "uzun pencere tutuyoruz"
    iddiası boş kalır (dosyanın kendi dürüstlük şartı).
    """
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
        # karesel melekenin göreceği iş: kaba görüşte n_kaba², ham n²
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


if __name__ == "__main__":   # pragma: no cover
    print(rapor())
