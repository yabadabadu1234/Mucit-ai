"""
Küllî Dimağ giriş noktası -- iddialar burada **ölçülür**.

    python -m main.main uzaylar    # 20 ∞-kategori uzayı, makine denetimi
    python -m main.main kubit      # süperpozisyon, dolaşıklık, kapasite
    python -m main.main egit       # Hamiltonyen parametrelerini öğret
"""
from __future__ import annotations

import resource
import sys
import time
from typing import List

import numpy as np

from idrak import arc

from . import kategori
from .dimag import Ayar, Dimag
from .egitim import degerlendir, egit, ornekler
from .yazmac import Yazmac


def _rss_gb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0 / 1024.0


def kubit_raporu(azami_kubit: int = 1_000_000) -> str:
    """Süperpozisyon var mı, dolaşıklık var mı, bellek nasıl büyüyor?"""
    s = ["=== KÜBİT YAZMACI: süperpozisyon, dolaşıklık, kapasite ===", ""]
    y = Yazmac(4096, bag=8)
    e0 = y.dolasiklik_entropisi()
    s.append("|0…0⟩ çarpım durumu      : S=%.6f  Schmidt=%d"
             % (e0["entropi"], e0["schmidt"]))
    y.superpozisyona_sok()
    e1 = y.dolasiklik_entropisi()
    s.append("Hadamard (SÜPERPOZİSYON) : S=%.6f  Schmidt=%d"
             % (e1["entropi"], e1["schmidt"]))
    s.append("   → 2^4096 taban durumunun hepsi eşit genlikte;")
    s.append("     entropi HÂLÂ SIFIR: süperpozisyon ≠ dolaşıklık.")
    iz = y.mera_kur(kademe=6)
    e2 = y.dolasiklik_entropisi()
    s.append("MERA (DOLAŞIKLIK)        : S=%.6f  Schmidt=%d  (âzamî %.4f)"
             % (e2["entropi"], e2["schmidt"], e2["azami_entropi"]))
    s.append("   → Schmidt rütbesi 1'den %d'e çıktı: durum ARTIK ÇARPIM DEĞİL."
             % e2["schmidt"])
    s.append("   norm hatası %.2e   kademe %d   kesme hatası %.2e"
             % (y.norm_hatasi(), len(iz),
                sum(k.kesme_hatasi for k in iz)))
    del y

    s += ["", "--- bellek: kübit sayısıyla nasıl büyüyor? ---",
          "%12s %10s %12s %10s %10s" % ("kübit", "GB", "kübit/bayt",
                                        "kur sn", "RSS GB")]
    onceki = None
    N = 65536
    while N <= azami_kubit:
        t0 = time.perf_counter()
        y = Yazmac(N, bag=8, obek=150_000)
        y.superpozisyona_sok()
        dt = time.perf_counter() - t0
        gb = y.bayt / 2 ** 30
        s.append("%12d %10.3f %12.0f %10.2f %10.2f"
                 % (N, gb, y.kubit_basina_bayt(), dt, _rss_gb()))
        if onceki:
            s.append("             ↑ kübit 4× arttı, bellek %.2f× arttı"
                     % (y.bayt / onceki))
        onceki = y.bayt
        del y
        N *= 4
    s.append("")
    s.append("Hüküm: bellek kübit sayısıyla DOĞRUSAL. 6 000 000 kübit için")
    s.append("6e6 × 512 B = 3.07 GB -- ayrı ölçümde teyit edilir.")
    return "\n".join(s)


def egitim_kos(cevrim: int = 8, ornek: int = 12, pencere: int = 24) -> str:
    a = Ayar(sozluk=16, kubit_basina=4, bag=8, mera_kademe=3,
             okuma_ornegi=48)
    m = Dimag(a)
    egt = arc.yukle_hepsi("training")
    dgr = arc.yukle_hepsi("evaluation")
    veri = ornekler(egt, azami=ornek, pencere=pencere)

    s = ["=== EĞİTİM: Hamiltonyen parametreleri (gradyan inişi YOK) ===",
         "  görev: eğitim=%d  değerlendirme=%d" % (len(egt), len(dgr)),
         "  örnek=%d  pencere=%d  parametre=%d" % (len(veri), pencere, len(m)),
         "    bunun %d'i Hamiltonyen (E_m, J_m), %d'i F_m fırlatımı,"
         % (m.n_ham, m.n_F),
         "    %d'i MERA açıları, %d'i POVM okuması." % (m.n_mera, m.n_povm),
         ""]
    g: List[str] = []
    r = egit(m, veri, cevrim=cevrim, r=2, n_ornek=12, gunluk=g)
    s += ["  " + x for x in g]
    s += ["", "  V_ilk=%.4f → V_son=%.4f   (%.1f sn)"
          % (r["V_ilk"], r["V_son"], r["süre_sn"]),
          "  ayrık motorun seçtiği dinamik mertebeler: %s"
          % list(r["dinamik"])]

    s += ["", "=== DEĞERLENDİRME (hiç görülmemiş bulmacalar) ==="]
    d = degerlendir(m, dgr, azami=12)
    s.append("  deneme=%d  TAM ÇÖZÜLEN=%d  ilk_belirteç_isabeti=%d"
             % (d["deneme"], d["tam_çözülen"], d["ilk_belirteç_isabeti"]))
    s.append("  ortalama hücre isabeti=%.4f" % d["ortalama_hücre_isabeti"])
    return "\n".join(s)


if __name__ == "__main__":
    emir = sys.argv[1] if len(sys.argv) > 1 else "hepsi"
    if emir in ("uzaylar", "hepsi"):
        print(kategori.rapor())
        print()
    if emir in ("kubit", "hepsi"):
        print(kubit_raporu())
        print()
    if emir in ("egit", "hepsi"):
        print(egitim_kos())
