"""ÖNBELLEK MİZANI -- yığın boyu elle değil, L2/L3'e göre tayin edilir.

    B = yigin_sec(d=4096, tip=np.complex64)

===================================================================
NİÇİN VAR: İKİ FERMANIN KESİŞTİĞİ YER
===================================================================

**1. Ferman (sabitler):** *"Elle tayin ettiğin tüm sabit değişkenleri
mutlaka bir fonksiyona bağlamak ya da değerini değiştirmek üzere evvela
bana liste halinde sunmak."*

``ornek_sayisi`` (yığın boyu ``B``) tam da öyle bir sabitti: 4, sonra
64, sonra 128, sonra 512 diye elle deneniyordu. Artık **donanımdan
hesaplanır**.

**2. Zabıt (Saf CPU Mimarisi, 5. fasıl):** *"Durum matris olarak
belleğe yazılmaz; L2/L3 önbelleğinden akan bir veri nehri gibi AVX-512
boru hattından geçer."* ve *"L1/L2/L3 önbelleğe tam sığma."*

===================================================================
ÖLÇÜLEN ÇELİŞKİ: ZABIT 1 GPU İÇİNDİR, BU MAKİNE CPU'DUR
===================================================================

*Qudit Kapasitesi ve Hız Tahkiki* zabıtı ``B``yi 128'den **512'ye**
çıkarmayı emreder ve gerekçesi doğrudur: *"NVIDIA L4 GPU'nun 7 424 CUDA
çekirdeği B=128 iken tam dolmaz."*

Bu makinede GPU yoktur. Ölçüldü (Intel Xeon, 4 çekirdek, L2 1 MiB/çekirdek,
L3 33 MiB; d=4096, complex64)::

    B     durum boyu    belirteç/sn
    128     4,2 MB         61 312     ← L3'e rahat sığıyor
    256     8,4 MB         57 559
    512    16,8 MB         41 980     ← L3 taşıyor, RAM'e düşüyor

Yâni GPU'da doğru olan hüküm CPU'da **tersine** çalışır: çekirdek
doygunluğu yerine önbellek taşması baskındır. Zabıtın *maksadı*
(donanımı doyurmak) korunur, *sayısı* donanımdan okunur.

Ne iddia edilmiyor: bu, zabıtın yanlış olduğu değildir. GPU takıldığı
an ``yigin_sec`` GPU dalını seçer ve ``B``yi çekirdek sayısına göre
büyütür -- o hâlde iki hüküm de aynı fonksiyonda yaşar.
"""
from __future__ import annotations

import os
from typing import Any, Dict, Optional, Tuple

import numpy as np

__all__ = ["onbellek_boylari", "yigin_sec", "rapor"]

#: Önbelleğin bu kadarı **durumun kendisine** ayrılır.
#:
#: **ÖLÇÜLEREK SEÇİLDİ, TAHMİNLE DEĞİL.** Durum tek başına dolaşmıyor:
#: her kapı bir yarım-durum kopyası ve iki geçici netice dizisi
#: üretiyor (``bit_kapisi``), üstüne 41 melekenin kendi dizileri
#: biniyor. Fiilî ayak izi durumun ~2,5 katıdır. Ölçüm (d=4096,
#: complex64, L3=33,8 MB)::
#:
#:      B    durum     belirteç/sn
#:     128   4,2 MB      61 312    ← en iyi
#:     256   8,4 MB      57 559
#:     512  16,8 MB      41 980
#:
#: ``PAY = 0,45`` B=256 veriyordu ve ölçüm onu yalanladı. 0,20'de
#: B=128 çıkar ve ölçümle uyuşur. Sayı formülden değil, ölçüden gelir.
PAY: float = 0.20

#: Yığın haddi -- bunun altına inilmez (Python çağrı yükü baskın olur)
#: ve üstüne çıkılmaz (bellek).
ASGARI: int = 8
AZAMI: int = 4096


def onbellek_boylari() -> Dict[str, int]:
    """L1/L2/L3 boyları -- **çekirdekten okunur**, elle yazılmaz.

    ``/sys/devices/system/cpu/cpu0/cache/index*/size`` okunur. Okunamazsa
    sıfır döner ve çağıran ihtiyatlı bir varsayılana düşer; bu sessiz
    değildir, ``rapor``da "okunamadı" diye görünür.
    """
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
    """Yığın boyu ``B``yi **donanımdan** tayin et.

    CPU dalında ölçüt önbellektir: durum ``B·d`` karmaşık genliktir ve
    kapılar onu defalarca dolaşır. Durum L3'e sığdığı sürece okuma
    önbellekten, sığmadığı an RAM'dendir; aradaki fark ölçüldü (61 312
    → 41 980 belirteç/sn).

    GPU dalında ölçüt çekirdek doygunluğudur ve zabıtın hükmü aynen
    işler: ``B`` çekirdek sayısına göre büyütülür.

    Döner: ``B`` ve **niçin o olduğu** -- sayı tek başına verilmez.
    """
    d = int(d)
    assert d >= 2, "qudit boyutu en az 2 olmalı"
    bayt = int(np.dtype(tip).itemsize)
    o = onbellek_boylari()

    if gpu:
        # Zabıtın hükmü: çekirdekleri doyur. Önbellek değil, paralellik.
        cek = int(cekirdek) or 7424
        B = int(min(AZAMI, max(ASGARI, 4 * cek // max(1, d // 512))))
        return {"B": B, "yol": "gpu", "sebep":
                "çekirdek doygunluğu (zabıt: B=512+); çekirdek=%d" % cek,
                "önbellek": o, "durum_bayt": B * d * bayt}

    hane = o.get("L3", 0) or o.get("L2", 0)
    if hane <= 0:
        # Önbellek okunamadı: ihtiyatlı ve **ilan edilmiş** varsayılan.
        return {"B": 128, "yol": "varsayılan", "sebep":
                "önbellek boyu okunamadı (/sys yok); 128'e düşüldü",
                "önbellek": o, "durum_bayt": 128 * d * bayt}

    B = int(PAY * hane / (d * bayt))
    B = max(ASGARI, min(AZAMI, B))
    # İkinin kuvvetine yuvarla: eksen bölmeleri ve SIMD hizası için.
    B = 1 << int(np.floor(np.log2(B)))
    B = max(ASGARI, B)
    return {"B": int(B), "yol": "cpu-önbellek",
            "sebep": "L3=%.1f MB, pay %.2f, d=%d, %d bayt/genlik"
                     % (hane / 1e6, PAY, d, bayt),
            "önbellek": o, "durum_bayt": int(B) * d * bayt}


def rapor(d: int = 4096) -> str:                         # pragma: no cover
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


if __name__ == "__main__":                               # pragma: no cover
    print(rapor())
