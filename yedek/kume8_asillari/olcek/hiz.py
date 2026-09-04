"""Performans muhasebesi: FLOP/token, çatı modeli ve "eşdeğer hız".

Kaynaklar: ``docs/kaynak/l4_gpu_hiz_raporu.md`` ve
``docs/kaynak/veri_akis_hizi.tex``.  İki belge **aynı külliyatta** olup
birbiriyle mertebelerce çelişiyor; bu modül çelişkiyi ölçerek çözüyor.
(Önce "22 mertebe" yazmıştım; ölçüm düzeltti -- gerçek sayılar aşağıda.)

**L4 raporu doğrudur.**  Bütün aritmetiği yeniden hesaplandı ve tuttu:

===========  ==============  ===============  ===============
``D``        FLOP/token      token/sn         ham metin
===========  ==============  ===============  ===============
4096         1.51 GFLOP      416 700          1.67 MB/sn
2048         0.377 GFLOP     1 668 000        6.67 MB/sn
1024         0.094 GFLOP     6 670 000        26.7 MB/sn
512          0.0236 GFLOP    26 680 000       106.7 MB/sn
===========  ==============  ===============  ===============

(``90·D²`` FLOP/token: 41 meleke ``82D²`` + RHT ``4D²`` + KAN ``2D²`` +
Hodge ``2D²``; net güç ``4×242 TFLOPS × 0.65 = 629.2 TFLOPS``.)

**M34 -- raporun yazılmamış şartı.**  Bu rakamlar tepe Tensor Core
gücünün doyurulduğunu, yani **büyük yığın** ile çalışıldığını varsayar.
Yığın ``B=1`` iken her ağırlık bir kere okunup bir kere kullanılır;
aritmetik yoğunluk **1 FLOP/bayt**tır ve iş tamamen **bellek
bağlıdır**.  ~300 GB/sn bant genişliğiyle çatı GPU başına ~3.0e11
FLOP/sn, yani tepe gücün **1/500**'ü.  Şart yazılmazsa rapor tek
cümlelik etkileşimli kullanımda 500 kat iyimser okunur.

**M31/M32/M33 -- veri akış risalesinin üç hatası.**

* ``log₂(10¹²) = 39.86``, dolayısıyla ``log₂²N ≈ 1589`` -- risale
  "``20² = 400``" diyor.  ``20`` hiçbir tabanla çıkmıyor
  (``log₁₀`` → 144, ``ln`` → 764).
* ``N³/log₂²N = 6.29e+32`` -- risale "``1e28``" diyor.
* **Asıl mesele:** ``Efektif Hız = Fizikî Hız × K``.  ``K`` boyutsuz
  bir orandır; bir veri hızıyla çarpımı yine bayt/sn verir ama
  **hiçbir fizikî akışa karşılık gelmez**.  Çip yine saniyede 1.2 TB
  alıyordur.  Doğru ayrım: *eşdeğer klasik iş* (birimi FLOP) ile
  *fizikî veri hızı* (birimi bayt/sn) ayrı büyüklüklerdir.

Çelişkinin ölçülen büyüklüğü:

* Risalenin **yazdığı netice** ``10^18 GB/sn = 1e27 bayt/sn``; aynı
  külliyattaki L4 raporu ``D=512``de ``1.07e8`` bayt/sn veriyor --
  **19 mertebe** fark (``D=4096``te 21 mertebe).
* Risalenin **formülü harfiyen** uygulanırsa (``1.2 TB/sn × K``)
  ``7.55e44`` bayt/sn çıkar -- L4 raporundan **37 mertebe** fark.

Bu modül ayrıca **bu makinede gerçekten ölçüyor**: ``D=128`` ve
``D=512`` için 41 melekelik tam bir geçişin süresi, ulaşılan FLOP/sn
ve tepe gücün yüzde kaçı.
"""

from __future__ import annotations

import math
import time
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = [
    "FLOP_KATSAYISI", "L4_TEPE_TFLOPS", "L4_VERIM", "L4_BANT_GBS",
    "flop_token", "net_guc", "throughput", "l4_cetveli",
    "aritmetik_yogunluk", "cati_modeli", "yigin_esigi",
    "esdegers_hiz_boyut_denetimi", "log_aritmetigi",
    "yerel_olcum",
]

FLOP_KATSAYISI = 90          # 82 (41 meleke) + 4 (RHT) + 2 (KAN) + 2 (Hodge)
L4_TEPE_TFLOPS = 4 * 242.0   # 4 × NVIDIA L4, BF16 dense
L4_VERIM = 0.65
L4_BANT_GBS = 300.0          # GPU başına ~300 GB/sn HBM
BAYT_TOKEN = 4               # UTF-8


def flop_token(D: int, katsayi: int = FLOP_KATSAYISI) -> float:
    """``katsayı · D²`` FLOP — raporun modeli."""
    return float(katsayi) * D * D


def net_guc(tepe_tflops: float = L4_TEPE_TFLOPS,
            verim: float = L4_VERIM) -> float:
    """Kullanılabilir FLOP/sn."""
    return tepe_tflops * 1e12 * verim


def throughput(D: int, tepe_tflops: float = L4_TEPE_TFLOPS,
               verim: float = L4_VERIM) -> Dict[str, float]:
    """Token/sn, ham metin MB/sn, tensör GB/sn."""
    fl = flop_token(D)
    tok = net_guc(tepe_tflops, verim) / fl
    return {"D": D, "flop_token": fl, "token_sn": tok,
            "metin_MB_sn": tok * BAYT_TOKEN / 1e6,
            "tensör_GB_sn": tok * D * 2 / 1e9}


def l4_cetveli(boyutlar: Sequence[int] = (4096, 2048, 1024, 512, 128)
               ) -> List[Dict[str, float]]:
    return [throughput(D) for D in boyutlar]


# ══════════════════════════════════════════════════════════════════════
#  M34: çatı modeli
# ══════════════════════════════════════════════════════════════════════

def aritmetik_yogunluk(D: int, B: int, bayt_agirlik: int = 2,
                       katsayi: int = FLOP_KATSAYISI) -> float:
    """``FLOP / okunan bayt`` — ``B`` token'lık yığın için.

    Ağırlıklar yığın başına bir kere okunur (``katsayı·D²/2`` ağırlık,
    her biri ``bayt_agirlik``); aktivasyon giriş+çıkış ``2·B·D``.
    """
    flop = katsayi * D * D * B
    bayt = (katsayi / 2.0) * D * D * bayt_agirlik + 2.0 * B * D * bayt_agirlik
    return flop / bayt


def cati_modeli(D: int, B: int, bant_GBs: float = L4_BANT_GBS,
                tepe_tflops: float = L4_TEPE_TFLOPS,
                verim: float = L4_VERIM, gpu: int = 4) -> Dict[str, object]:
    """Çatı (roofline): iş FLOP-bağlı mı bellek-bağlı mı?"""
    yog = aritmetik_yogunluk(D, B)
    bellek_cati = bant_GBs * 1e9 * yog
    flop_cati = net_guc(tepe_tflops, verim) / gpu
    return {"D": D, "B": B, "yoğunluk": yog,
            "bellek_çatısı": bellek_cati, "flop_çatısı": flop_cati,
            "ulaşılabilir": min(bellek_cati, flop_cati),
            "bellek_bağlı_mı": bellek_cati < flop_cati,
            "tepe_gücün_kaçta_biri": flop_cati / max(bellek_cati, 1e-30)}


def yigin_esigi(D: int, bant_GBs: float = L4_BANT_GBS,
                tepe_tflops: float = L4_TEPE_TFLOPS,
                verim: float = L4_VERIM, gpu: int = 4) -> int:
    """FLOP-bağlı olmak için gereken en küçük yığın ``B``."""
    B = 1
    while B <= 1 << 22:
        if not cati_modeli(D, B, bant_GBs, tepe_tflops, verim,
                           gpu)["bellek_bağlı_mı"]:
            return B
        B *= 2
    return -1


# ══════════════════════════════════════════════════════════════════════
#  M31/M32/M33: veri akış risalesinin aritmetiği
# ══════════════════════════════════════════════════════════════════════

def log_aritmetigi(N: float = 1e12) -> Dict[str, float]:
    """``log²N`` ve ``N³/log²N`` — risalenin verdiği sayılarla kıyas."""
    l2, l10, ln = math.log2(N), math.log10(N), math.log(N)
    return {"N": N, "log2": l2, "log2_kare": l2 ** 2,
            "log10_kare": l10 ** 2, "ln_kare": ln ** 2,
            "risale_log2_kare": 400.0,
            "N3_bolu_log2kare": N ** 3 / l2 ** 2,
            "N2_bolu_log2kare": N ** 2 / l2 ** 2,
            "risale_K": 1e28}


def esdegers_hiz_boyut_denetimi(fiziki_bayt_sn: float = 1.2e12,
                                K: float = 6.293e32) -> Dict[str, object]:
    """**M33:** bant genişliğini boyutsuz oranla çarpmak ne veriyor?

    Sayı çıkar ama fizikî bir akış **değildir**.  Kıyas için aynı
    hesabın gerçek donanımdaki karşılığı da veriliyor.
    """
    carpim = fiziki_bayt_sn * K
    gercek_512 = throughput(512)["metin_MB_sn"] * 1e6
    gercek_4096 = throughput(4096)["metin_MB_sn"] * 1e6
    return {
        "fizikî_bayt_sn": fiziki_bayt_sn,
        "K": K,
        "çarpım_bayt_sn": carpim,
        "çarpım_GB_sn": carpim / 1e9,
        "gerçek_D512_bayt_sn": gercek_512,
        "gerçek_D4096_bayt_sn": gercek_4096,
        "mertebe_farkı_D512": math.log10(carpim / gercek_512),
        "mertebe_farkı_D4096": math.log10(carpim / gercek_4096),
        "eşdeğer_iş_FLOP": fiziki_bayt_sn * K,   # birimi FLOP, bayt/sn DEĞİL
        "not": "K boyutsuz; çarpım bayt/sn birimini korur ama fizikî "
               "bir akışa karşılık gelmez",
    }


# ══════════════════════════════════════════════════════════════════════
#  Bu makinede gerçek ölçüm
# ══════════════════════════════════════════════════════════════════════

def yerel_olcum(D: int, B: int = 1, tekrar: int = 3,
                meleke: int = 41) -> Dict[str, float]:
    """``meleke`` adet ``D×D`` çarpımı **gerçekten** koş ve süreyi ölç."""
    r = np.random.default_rng(0)
    # Ağırlıklar 1/√D ile ölçekleniyor: 41 ardışık çarpımda float32
    # TAŞIYOR (ölçüldü: overflow → inf/nan) ve süre ölçümü anlamsızlaşır.
    # Ölçek FLOP sayısını değiştirmez, yalnız sayıları sınırda tutar.
    W = [(r.normal(size=(D, D)) / math.sqrt(D)).astype(np.float32)
         for _ in range(4)]
    X = r.normal(size=(D, B)).astype(np.float32)
    Y = X.copy()
    for k in range(meleke):
        Y = W[k % 4] @ Y
    t0 = time.perf_counter()
    for _ in range(tekrar):
        Y = X.copy()
        for k in range(meleke):
            Y = W[k % 4] @ Y
    dt = (time.perf_counter() - t0) / tekrar
    fl = 2.0 * D * D * B * meleke
    return {"D": D, "B": B, "süre_ms": dt * 1e3, "FLOP": fl,
            "FLOP_sn": fl / dt, "GFLOP_sn": fl / dt / 1e9,
            "token_sn": B / dt,
            "sonlu_mu": bool(np.all(np.isfinite(Y)))}


# ══════════════════════════════════════════════════════════════════════
#  Gösterim
# ══════════════════════════════════════════════════════════════════════

def _gosterim() -> str:
    s = []
    s.append("=== L4 raporunun aritmetiği yeniden hesaplandı ===")
    s.append("  net güç = %.1f TFLOPS  (4×242 × %.2f)"
             % (net_guc() / 1e12, L4_VERIM))
    s.append("      D   FLOP/token    token/sn    metin MB/sn   tensör GB/sn"
             "   rapor MB/sn")
    rapor = {4096: 1.67, 2048: 6.67, 1024: 26.68, 512: 106.72}
    for t in l4_cetveli():
        r = rapor.get(int(t["D"]))
        s.append("  %5d   %.3e   %.4e   %10.2f   %11.2f   %s"
                 % (t["D"], t["flop_token"], t["token_sn"],
                    t["metin_MB_sn"], t["tensör_GB_sn"],
                    ("%10.2f ✓" % r) if r else "        —")
                 )
    s.append("  Rapor DOĞRU: hesaplanan ile yazılan birebir tutuyor.")

    s.append("\n=== M34: yazılmamış şart — yığın (batch) ===")
    s.append("      D      B   yoğunluk(FLOP/bayt)   çatı(FLOP/sn)   durum")
    for D in (512, 4096):
        for B in (1, 8, 64, 512, 4096):
            c = cati_modeli(D, B)
            s.append("  %5d  %5d   %16.1f   %.3e   %s"
                     % (D, B, c["yoğunluk"], c["ulaşılabilir"],
                        "bellek-bağlı" if c["bellek_bağlı_mı"]
                        else "FLOP-bağlı"))
    for D in (512, 4096):
        e = yigin_esigi(D)
        c1 = cati_modeli(D, 1)
        s.append("  D=%d: FLOP-bağlı olmak için B ≥ %d;  B=1'de tepe gücün "
                 "1/%.0f'i" % (D, e, c1["tepe_gücün_kaçta_biri"]))
    s.append("  Yani rapordaki rakamlar BÜYÜK YIĞIN varsayar. Tek")
    s.append("  cümlelik etkileşimli kullanımda (B=1) 500 kat iyimser.")

    s.append("\n=== M31/M32: veri akış risalesinin logaritma aritmetiği ===")
    a = log_aritmetigi()
    s.append("  N = 1e12")
    s.append("    log₂N = %.2f  → log₂²N = %.1f     risale: %.0f  ← YANLIŞ"
             % (a["log2"], a["log2_kare"], a["risale_log2_kare"]))
    s.append("    (log₁₀ ile %.0f, ln ile %.0f — hiçbiri 400 vermiyor)"
             % (a["log10_kare"], a["ln_kare"]))
    s.append("    N³/log₂²N = %.3e     risale: %.0e  ← YANLIŞ"
             % (a["N3_bolu_log2kare"], a["risale_K"]))
    s.append("    (N²/log₂²N alınsaydı %.3e; o da 1e28 değil)"
             % a["N2_bolu_log2kare"])

    s.append("\n=== M33: 'Fizikî Hız × K' boyutça geçersiz ===")
    d = esdegers_hiz_boyut_denetimi()
    s.append("  1.2 TB/sn × K = %.3e bayt/sn = %.3e GB/sn"
             % (d["çarpım_bayt_sn"], d["çarpım_GB_sn"]))
    s.append("  Aynı külliyattaki L4 raporu ise:")
    s.append("    D=512  : %.3e bayt/sn   → %.0f mertebe fark"
             % (d["gerçek_D512_bayt_sn"], d["mertebe_farkı_D512"]))
    s.append("    D=4096 : %.3e bayt/sn   → %.0f mertebe fark"
             % (d["gerçek_D4096_bayt_sn"], d["mertebe_farkı_D4096"]))
    s.append("  K boyutsuz bir orandır (işlem/işlem). Bir veri hızıyla")
    s.append("  çarpımı sayı verir ama fizikî akış vermez: çip yine")
    s.append("  saniyede 1.2 TB alıyordur. Doğru ayrım:")
    s.append("    eşdeğer klasik İŞ  → birimi FLOP")
    s.append("    fizikî veri HIZI   → birimi bayt/sn")
    s.append("  İkisi aynı cümlede çarpılamaz.")

    s.append("\n=== Bu makinede GERÇEK ölçüm (GPU yok, CPU) ===")
    s.append("      D      B    süre(ms)    GFLOP/sn    token/sn")
    for D in (128, 512):
        for B in (1, 64):
            m = yerel_olcum(D, B)
            s.append("  %5d  %5d   %9.3f   %9.1f   %10.1f"
                     % (D, B, m["süre_ms"], m["GFLOP_sn"], m["token_sn"]))
    s.append("  Varsayılan boyut 512, hızlı deneme boyutu 128.")
    s.append("  Yığın 1'den 64'e çıkınca token/sn'nin nasıl arttığına")
    s.append("  dikkat: aynı çatı etkisi bu CPU'da da görünüyor.")
    return "\n".join(s)


if __name__ == "__main__":  # pragma: no cover
    print(_gosterim())
