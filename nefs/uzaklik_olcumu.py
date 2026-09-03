"""
Uzak çift kapısı: **takas ağı mı, MPO mu?** -- eşiği ölçüm koyar.

Kütük H41 *"takas ağı kapalı yoldur, MPO kazanır"* diyor; fakat o hüküm
**kesme hatası** üzerine verilmişti ve zincirin gövdesindeki uzun menzil
içindi. Melekelerin çoğu ise KISA mesafede (2-5 kübit) uzak çift
kullanıyor. Kısa mesafede hangisi daha iyi -- bilinmiyordu.

Kullanıcı hükmü: *"ÖLÇÜM karar versin: mesafeye göre eşik koy."*
Bu dosya o ölçümü yapar ve iki şeyi **beraber** raporlar:

* **süre** -- takas ``2·mesafe`` SVD yapar, MPO ``mesafe`` yuvada
  ``χ³D³`` iş yapar; hangisinin ucuz olduğu mesafeye ve ``χ``ye bağlıdır.
* **kesme** -- takas dolaşıklığı sürükler, MPO sürüklemez. Hız uğruna
  doğruluk satılmasın diye ikisi yan yana yazılır.

Hüküm tek bir sayıya (``QYazmac.MPO_ESIGI``) iner ve o sayı burada
ölçülür, elle konmaz.
"""
from __future__ import annotations

import time
from typing import Dict, List, Tuple

import numpy as np

from kuantum.yazmac import dik_iki_kubit
from .zihin_durumu import QAyar, QYazmac

__all__ = ["olc", "rapor"]


def _kur(n_satir: int, k: int, bag: int, tohum: int = 0) -> QYazmac:
    q = QYazmac(n_satir, QAyar(satir_kubiti=k, bag=bag, tohum=tohum))
    q.kodla(np.random.default_rng(tohum).normal(size=(n_satir, k)))
    q.superpozisyon()
    q.mera()
    return q


def olc(mesafeler=(2, 3, 5, 8, 13, 21), bag=(8, 16, 32),
        tur: int = 3, tohum: int = 0) -> List[Dict[str, float]]:
    """Her (mesafe, χ) için iki yolu **aynı durumda** koştur ve karşılaştır."""
    rng = np.random.default_rng(tohum)
    G = dik_iki_kubit(rng.normal(size=6))
    netice: List[Dict[str, float]] = []
    for X in bag:
        for d in mesafeler:
            n_satir = max(2, (d + 6) // 5 + 1)
            a = _kur(n_satir, 4, X, tohum)
            b = _kur(n_satir, 4, X, tohum)
            i, j = 0, d
            if j >= a.kulli("makam", 0):
                continue
            t0 = time.perf_counter()
            for _ in range(tur):
                a.uzak_cift(i, j, G)
            t_takas = (time.perf_counter() - t0) / tur
            t0 = time.perf_counter()
            for _ in range(tur):
                b.uzak_cift_mpo(i, j, G)
            t_mpo = (time.perf_counter() - t0) / tur
            # aynı devreyi iki yoldan geçen durumlar ne kadar ayrışıyor
            fark = float(np.abs(a.y.A - b.y.A).max())
            netice.append({"χ": X, "mesafe": d,
                           "takas_sn": t_takas, "mpo_sn": t_mpo,
                           "kat": t_takas / max(t_mpo, 1e-12),
                           "takas_kesme": a.iz.kesme, "mpo_kesme": b.iz.kesme,
                           "durum_farkı": fark})
    return netice


def rapor() -> str:
    n = olc()
    s = ["=== Uzak çift: takas ağı mı, MPO mu? (eşiği ÖLÇÜM koyar) ===",
         "",
         "  χ    mesafe  takas sn   MPO sn     kat    takas kesme  MPO kesme"]
    for r in n:
        s.append("  %-4d %-7d %-10.5f %-10.5f %-6.2f %-12.2e %.2e"
                 % (r["χ"], r["mesafe"], r["takas_sn"], r["mpo_sn"],
                    r["kat"], r["takas_kesme"], r["mpo_kesme"]))
    # eşik: MPO'nun takastan hızlı olduğu en küçük mesafe (χ başına)
    s += ["", "HÜKÜM (χ başına, MPO'nun kazandığı en küçük mesafe):"]
    for X in sorted({r["χ"] for r in n}):
        kazanan = [r["mesafe"] for r in n if r["χ"] == X and r["kat"] > 1.0]
        s.append("  χ=%-4d  MPO şu mesafeden itibaren hızlı: %s"
                 % (X, min(kazanan) if kazanan else "hiçbirinde"))
    s += ["",
          "Kesme sütunları da beraber okunmalıdır: MPO daha yavaş olsa",
          "bile daha az kesiyorsa uzun menzilde yine tercih edilir (H41).",
          "Hız uğruna doğruluk satılmaz; ikisi yan yana yazılır."]
    return "\n".join(s)


if __name__ == "__main__":   # pragma: no cover
    print(rapor())
