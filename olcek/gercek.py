"""Bu makinede GERÇEK sürekli ölçüm: 30 sn ve 60 sn pencerelerde GB/sn.

``olcek.hiz`` kâğıt üstündeki modeli ve L4 raporunu tartıyordu.  Bu
modül **bu CPU'da fiilen ne olduğunu** ölçer: kısa atımlar değil,
30--60 saniye sürekli koşan bir iş yükü, ısınma atılarak.

**Neden pencere ölçümü şart.**  Milisaniyelik tek bir ölçüm üç sebeple
yanıltır: (i) ilk çağrıda kütüphane ısınması var, (ii) küçük işler
önbelleğe sığar ve gerçek bant genişliğini göstermez, (iii) termal ve
zamanlayıcı dalgalanması saniye mertebesinde ortaya çıkar.  Burada
ısınma ayrı ölçülüp atılıyor ve pencere boyunca *bütün* atımların
dağılımı (ortanca, p10, p90) veriliyor.

**"10 saniyede 1 GB" iddiası.**  Külliyattaki veri akış risalesi
saniyede exabaytlardan söz ediyordu; L4 raporu ise ``D=512``de
saniyede 106.7 MB veriyor -- yani 1 GB için ~9.4 saniye.  Bu ikincisi
**tutarlı bir hedeftir** ve burada, aynı FLOP modeliyle, bu CPU'da
ne çıktığı ölçülüyor.  GPU yok; beklenen fark ölçülüp yazılıyor.
"""

from __future__ import annotations

import math
import os
import time
from typing import Callable, Dict, List, Optional, Sequence

import numpy as np

from .hiz import (BAYT_TOKEN, FLOP_KATSAYISI, L4_TEPE_TFLOPS, L4_VERIM,
                  flop_token, net_guc, throughput)

__all__ = [
    "surekli_olc", "pencere_cetveli", "gb_icin_sure",
    "l4_ile_kiyas", "isinma_bedeli", "sistem_yuku",
]


def sistem_yuku() -> Dict[str, object]:
    """Ölçüm sırasında makine boş muydu? — 1 dk yük ortalaması.

    **Bu şart yazılmazsa ölçüm yalan olur.**  Ölçüldü: aynı CPU'da
    eğitim koşarken ``D=128, B=64`` atımı 332 ms sürüyordu (0.3
    GFLOP/sn); makine boşken aynı iş misliyle hızlıdır.  Bu yüzden
    her ölçümün yanına yük yazılıyor.
    """
    try:
        y1, y5, y15 = os.getloadavg()
    except OSError:
        y1 = y5 = y15 = float("nan")
    cek = os.cpu_count() or 1
    return {"yük_1dk": y1, "yük_5dk": y5, "çekirdek": cek,
            "çekirdek_başına": y1 / cek,
            "makine_boş_mu": y1 / cek < 0.3,
            "değerlendirme": ("boş" if y1 / cek < 0.3
                              else "YÜKLÜ — ölçüm bu yüzden düşük")}


def _is_yuku(D: int, B: int, meleke: int = 41, tip=np.float32):
    """Bir atım: ``meleke`` adet ``D×D`` çarpımı, ``B`` token yığını."""
    r = np.random.default_rng(0)
    W = [(r.normal(size=(D, D)) / math.sqrt(D)).astype(tip)
         for _ in range(4)]
    X = (r.normal(size=(D, B)) / math.sqrt(D)).astype(tip)

    def atim():
        Y = X
        for k in range(meleke):
            Y = W[k % 4] @ Y
        return Y

    return atim


def surekli_olc(D: int = 128, B: int = 64, saniye: float = 30.0,
                meleke: int = 41, isinma: float = 2.0
                ) -> Dict[str, object]:
    """``saniye`` boyunca kesintisiz koş; ısınmayı **atarak** ölç.

    Dönen değerler: token/sn, GB/sn (ham metin), GFLOP/sn ve atım
    sürelerinin dağılımı.  Sayılar tek bir atımdan değil, pencere
    boyunca biriken **bütün** atımlardan çıkarılır.
    """
    atim = _is_yuku(D, B, meleke)
    # ısınma: bu süre ölçüme GİRMİYOR
    t0 = time.perf_counter()
    isinma_atim = 0
    while time.perf_counter() - t0 < isinma:
        atim()
        isinma_atim += 1
    isinma_sure = time.perf_counter() - t0

    sureler: List[float] = []
    bas = time.perf_counter()
    while time.perf_counter() - bas < saniye:
        a = time.perf_counter()
        Y = atim()
        sureler.append(time.perf_counter() - a)
    gecen = time.perf_counter() - bas

    yuk = sistem_yuku()
    n = len(sureler)
    token = n * B
    flop = n * 2.0 * D * D * B * meleke
    s = np.array(sureler)
    return {
        "D": D, "B": B, "meleke": meleke, "pencere_sn": saniye,
        "gerçek_sn": gecen, "atım": n, "token": token,
        "token_sn": token / gecen,
        "MB_sn": token * BAYT_TOKEN / 1e6 / gecen,
        "GB_sn": token * BAYT_TOKEN / 1e9 / gecen,
        "GFLOP_sn": flop / gecen / 1e9,
        "atım_ms_ortanca": float(np.median(s) * 1e3),
        "atım_ms_p10": float(np.percentile(s, 10) * 1e3),
        "atım_ms_p90": float(np.percentile(s, 90) * 1e3),
        "atım_ms_en_kötü": float(s.max() * 1e3),
        "dalgalanma_p90_p10": float(np.percentile(s, 90)
                                    / max(np.percentile(s, 10), 1e-12)),
        "ısınma_sn": isinma_sure, "ısınma_atım": isinma_atim,
        "sonlu_mu": bool(np.all(np.isfinite(Y))),
        "yük_1dk": yuk["yük_1dk"], "çekirdek": yuk["çekirdek"],
        "makine_boş_mu": yuk["makine_boş_mu"],
        "yük_değerlendirmesi": yuk["değerlendirme"],
    }


def isinma_bedeli(D: int = 128, B: int = 64, atim_sayisi: int = 40
                  ) -> Dict[str, float]:
    """İlk atım ile yerleşik atım arasındaki fark — ısınma ölçülüyor."""
    atim = _is_yuku(D, B)
    t0 = time.perf_counter(); atim(); ilk = time.perf_counter() - t0
    sonra = []
    for _ in range(atim_sayisi):
        t0 = time.perf_counter(); atim(); sonra.append(time.perf_counter() - t0)
    yerlesik = float(np.median(sonra))
    return {"ilk_atım_ms": ilk * 1e3, "yerleşik_ms": yerlesik * 1e3,
            "kat": ilk / max(yerlesik, 1e-12)}


def pencere_cetveli(boyutlar: Sequence[int] = (128, 512),
                    yiginlar: Sequence[int] = (1, 64),
                    pencereler: Sequence[float] = (30.0, 60.0)
                    ) -> List[Dict[str, object]]:
    return [surekli_olc(D, B, p) for D in boyutlar for B in yiginlar
            for p in pencereler]


def gb_icin_sure(MB_sn: float) -> float:
    """1 GB ham metin için gereken saniye."""
    return 1000.0 / max(MB_sn, 1e-12)


def l4_ile_kiyas(olcum: Dict[str, object]) -> Dict[str, object]:
    """Ölçüleni L4 kâğıt modeliyle kıyasla — GPU yok, fark ne kadar."""
    D = int(olcum["D"])
    t = throughput(D)
    return {"D": D,
            "bu_CPU_MB_sn": olcum["MB_sn"],
            "L4_kağıt_MB_sn": t["metin_MB_sn"],
            "kat_fark": t["metin_MB_sn"] / max(float(olcum["MB_sn"]), 1e-12),
            "bu_CPU_1GB_sn": gb_icin_sure(float(olcum["MB_sn"])),
            "L4_kağıt_1GB_sn": gb_icin_sure(t["metin_MB_sn"]),
            "bu_CPU_GFLOP_sn": olcum["GFLOP_sn"],
            "L4_net_GFLOP_sn": net_guc() / 1e9,
            "FLOP_kat_fark": (net_guc() / 1e9)
                             / max(float(olcum["GFLOP_sn"]), 1e-12)}


# ══════════════════════════════════════════════════════════════════════
#  Gösterim
# ══════════════════════════════════════════════════════════════════════

def _gosterim(kisa: bool = False) -> str:
    s = []
    pencere = (5.0,) if kisa else (30.0, 60.0)
    y = sistem_yuku()
    s.append("=== ÖNCE: makine boş mu? ===")
    s.append("  1 dk yük ortalaması = %.2f   çekirdek = %d   "
             "çekirdek başına = %.2f"
             % (y["yük_1dk"], y["çekirdek"], y["çekirdek_başına"]))
    s.append("  değerlendirme: %s" % y["değerlendirme"])
    if not y["makine_boş_mu"]:
        s.append("  ⚠ Aşağıdaki bütün sayılar YÜK ALTINDA ölçüldü ve")
        s.append("    makinenin gerçek kudretinden DÜŞÜKTÜR. Bunu")
        s.append("    yazmadan rapor vermek yanlış olurdu.")

    s.append("\n=== Isınma gerçekten var mı? (ölçülüyor, sonra atılıyor) ===")
    for D in (128, 512):
        i = isinma_bedeli(D)
        s.append("  D=%3d  ilk atım %8.3f ms   yerleşik %8.3f ms   %5.1f kat"
                 % (D, i["ilk_atım_ms"], i["yerleşik_ms"], i["kat"]))
    s.append("  Tek atımlık ölçüm bu yüzden yanıltır; aşağıdaki bütün")
    s.append("  sayılarda ısınma penceresi ÖLÇÜME GİRMİYOR.")

    s.append("\n=== Sürekli pencere ölçümü (bu CPU, GPU yok) ===")
    s.append("    D    B  pencere    atım   token/sn    MB/sn    GFLOP/sn"
             "   1 GB için")
    olcumler = []
    for D in (128, 512):
        for B in (1, 64):
            for p in pencere:
                o = surekli_olc(D, B, p)
                olcumler.append(o)
                s.append("  %4d %4d  %5.0f sn %7d  %9.1f  %7.3f  %9.1f"
                         "   %8.1f sn"
                         % (o["D"], o["B"], o["pencere_sn"], o["atım"],
                            o["token_sn"], o["MB_sn"], o["GFLOP_sn"],
                            gb_icin_sure(float(o["MB_sn"]))))

    s.append("\n=== Dalgalanma: pencere içinde atımlar ne kadar oynuyor? ===")
    s.append("    D    B   ortanca ms    p10 ms    p90 ms   en kötü   p90/p10")
    for o in olcumler:
        if o["pencere_sn"] == max(pencere):
            s.append("  %4d %4d %10.3f %9.3f %9.3f %9.3f    %.2f"
                     % (o["D"], o["B"], o["atım_ms_ortanca"],
                        o["atım_ms_p10"], o["atım_ms_p90"],
                        o["atım_ms_en_kötü"], o["dalgalanma_p90_p10"]))

    s.append("\n=== '10 saniyede 1 GB' hedefine göre neredeyiz? ===")
    s.append("    D    B   bu CPU 1GB   L4 kâğıt 1GB    kat fark")
    for o in olcumler:
        if o["pencere_sn"] == max(pencere):
            k = l4_ile_kiyas(o)
            s.append("  %4d %4d %10.1f sn %12.1f sn %10.0f×"
                     % (o["D"], o["B"], k["bu_CPU_1GB_sn"],
                        k["L4_kağıt_1GB_sn"], k["kat_fark"]))
    s.append("  L4 raporunun D=512 rakamı (106.7 MB/sn) 1 GB'ı 9.4")
    s.append("  saniyede işlemek demektir; yani '10 saniyede 1 GB'")
    s.append("  hedefi kâğıt üstünde TUTARLIDIR. Bu makinede ise GPU")
    s.append("  yok ve fark yukarıdaki kat sütununda duruyor.")

    s.append("\n=== Kübit var mı? — yok, ve olması da beklenmiyor ===")
    s.append("  Bu ölçümlerin hiçbirinde kuantum donanımı kullanılmadı.")
    s.append("  idrak.kubit'teki yazmaç bir KLASİK BENZETİMDİR: n kübit")
    s.append("  2^n genlik demektir ve maliyeti üstel büyür (ölçüldü:")
    s.append("  n=16'da 108 ms). Kazancı hız değil, norm korunumudur.")
    s.append("  Yani 'kübit yapacaksın' isteği mimarî olarak karşılandı,")
    s.append("  fizikî olarak KARŞILANMADI ve karşılanamaz.")
    return "\n".join(s)


if __name__ == "__main__":  # pragma: no cover
    import sys
    print(_gosterim(kisa="--kisa" in sys.argv))
