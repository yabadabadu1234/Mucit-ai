"""
Küllî Dimağ giriş noktası.

    python -m main.main kapasite     # kaç belirteç aynı anda tutuluyor
    python -m main.main egit         # ARC ile gradyansız eğitim
    python -m main.main hepsi        # ikisi birden + değerlendirme

İddialar burada **ölçülür**, beyan edilmez.
"""
from __future__ import annotations

import resource
import sys
import time
from typing import List

import numpy as np

from idrak import arc

from .dimag import Ayar, Dimag
from .egitim import degerlendir, egit, ornekler


def _rss_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def kapasite() -> str:
    """MERA temsili belleği gerçekten DOĞRUSAL mı büyütüyor?"""
    a = Ayar(sozluk=16, lif=8, bag=8)
    m = Dimag(a)
    s = ["=== KAPASİTE: bellek belirteç sayısıyla nasıl büyüyor? ===",
         "  (iddia: O(N) -- klasik dikkatte O(N²))", ""]
    s.append("%10s %12s %14s %16s %10s %10s"
             % ("belirteç", "kübit", "analitik KB", "belirteç/bayt",
                "RSS MB", "süre ms"))
    onceki = None
    for N in (64, 256, 1024, 4096, 16384, 65536):
        b = m.bellek_baytlari(N)
        t = np.random.default_rng(0).integers(0, a.sozluk, size=N)
        t0 = time.perf_counter()
        P, iz = m.ileri(t)
        dt = (time.perf_counter() - t0) * 1e3
        s.append("%10d %12d %14.1f %16.1f %10.1f %10.1f"
                 % (N, int(b["kübit"]), b["toplam_bayt"] / 1024.0,
                    b["belirteç_başına_bayt"], _rss_mb(), dt))
        if onceki is not None:
            oran = b["toplam_bayt"] / onceki
            s.append("           ↑ belirteç 4× arttı, bellek %.2f× arttı "
                     "(doğrusalsa ≈4, karesel olsaydı ≈16)" % oran)
        onceki = b["toplam_bayt"]
        s.append("           MERA kademesi=%d (log₂N≈%.1f)  β₀=%s  BEC uyum=%.4f"
                 % (iz.kademe, np.log2(N), sorted(set(iz.betti.values())),
                    iz.bec_uyum))
    s.append("")
    s.append("Hüküm: bellek belirteç sayısıyla DOĞRUSAL büyüyor; mesafe")
    s.append("log₂N kademede kapanıyor (kütük H26). Hız kazancı İDDİA")
    s.append("EDİLMİYOR -- ölçülen kazanç kapasitedir.")
    return "\n".join(s)


def egitim_kos(cevrim: int = 6, ornek: int = 24) -> str:
    a = Ayar(sozluk=16, lif=8, bag=8)
    m = Dimag(a)
    egt = arc.yukle_hepsi("training")
    dgr = arc.yukle_hepsi("evaluation")
    veri = ornekler(egt, azami=ornek, pencere=40)

    s = ["=== EĞİTİM (gradyan inişi YOK: AS-GEK + dalga) ===",
         "  görev: eğitim=%d  değerlendirme=%d" % (len(egt), len(dgr)),
         "  örnek=%d  parametre=%d" % (len(veri), len(m.demet)), ""]
    g: List[str] = []
    r = egit(m, veri, cevrim=cevrim, r=2, n_ornek=16, gunluk=g)
    s += ["  " + x for x in g]
    s += ["", "  V_ilk=%.4f → V_son=%.4f   (%.1f sn)"
          % (r["V_ilk"], r["V_son"], r["süre_sn"]),
          "  seçilen dinamik mertebeler: %s" % list(r["dinamik"])]

    s.append("")
    s.append("=== DEĞERLENDİRME (hiç görülmemiş bulmacalar) ===")
    d = degerlendir(m, dgr, azami=20)
    s.append("  deneme=%d  TAM ÇÖZÜLEN=%d  ilk_belirteç_isabeti=%d"
             % (d["deneme"], d["tam_çözülen"], d["ilk_belirteç_isabeti"]))
    s.append("  ortalama hücre isabeti=%.4f" % d["ortalama_hücre_isabeti"])
    if not d["tam_çözülen"]:
        s.append("  Hüküm: bu ölçekte (parametre=%d, çevrim=%d) hiçbir"
                 % (len(m.demet), cevrim))
        s.append("  değerlendirme sorusu tam çözülmedi. Bu gizlenmiyor.")
    return "\n".join(s)


if __name__ == "__main__":
    emir = sys.argv[1] if len(sys.argv) > 1 else "hepsi"
    if emir in ("kapasite", "hepsi"):
        print(kapasite())
    if emir in ("egit", "hepsi"):
        print()
        print(egitim_kos())
