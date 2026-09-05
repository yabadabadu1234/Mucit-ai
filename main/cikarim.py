"""ÇIKARIM -- tahtın ikinci kapısı: **cevabı motor verir.**

===================================================================
PADİŞAHIN FERMANI, İKİNCİ KISIM
===================================================================

*"ARC yalnız llm motoruyla çözülecek, başka herhangi bir şeyle
değil."*

Bu dosya evvelce 927 satırlık bir **görev başına öznitelik
mühendisliğiydi**: `baglam_cikar`, `ozellik`, `nesne_ozellikleri`,
`hendese_adaylari`, `sahit_cogalt`, `_d4`, `_tuval`, `dalga_kur`,
`KulliHukumMotoru`. Elle kurulmuş öznitelikler üstünde her görev için
ayrı bir dalga/ridge öğrenicisi koşuyor, kütük de "ARC görevlerini
fiilen çözen hat budur" diye onu gösteriyordu.

**O hat fermanla tasfiye edildi.** Öğrenilmiş olması onu meşru
kılmıyordu: öznitelikler elle kuruluyordu ve ARC'ye mahsustu; yâni
çözen yine motor değil, benim ARC hakkındaki tahminlerimdi.

Aslı **imha edilmedi**, `yedek/kume9_arc_hileleri/cikarim_dalga.py`
altında duruyor (imha yok, cevher toplama var).

Yerine gelen budur: bağlamı kur, motoru koştur, belirteç belirteç
üret, sükût hakkını sakla. Hepsi `nefs/soyle.py`ye havale edilir --
burada yeni riyaziye yoktur.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import sys                                               # noqa: E402
import time                                              # noqa: E402
from typing import Dict, List, Optional, Sequence        # noqa: E402

import numpy as np                                       # noqa: E402

from nefs.musahede import gorevleri_getir                # noqa: E402

__all__ = ["padisah", "degerlendirme_kosusu", "kos"]


def _motor(ayar=None):
    """Tâlim motorunu kur. Tek yerde; iki kapı aynı nefsi kullansın."""
    from main.egitim import KISA_CPU
    from nefs.melekeler import QNefs
    a = ayar or KISA_CPU
    nefs = QNefs(a.tohum, a.qayar())
    nefs.idrak_et(np.zeros((2, a.satir_kubiti)))
    return nefs, a


def padisah(gorev, nefs=None, ayar=None, **kw) -> Dict[str, object]:
    """Bir göreve cevap ver -- **yalnız motorla**.

    Eski ``padisah`` görev başına dalga öğrenicisi koşturuyordu ve
    ``kw`` ile ``devir``, ``azami_aday``, ``loo_devir`` gibi arama
    bütçeleri alıyordu. Onlar artık yok; imza uyumluluk için ``kw``
    yutar ve **yuttuğunu söyler**.
    """
    from nefs.soyle import soyle
    if nefs is None:
        nefs, ayar = _motor(ayar)
    c = soyle(gorev, nefs=nefs, sozluk=(ayar.sozluk if ayar else 16), **{})
    return {"görev": getattr(gorev, "ad", ""),
            "sükût": bool(c.sukut),
            "sebep": c.sebep,
            "kural": c.kural,
            "belirteç": c.belirtec,
            "güven": float(c.guven),
            "yutulan_ayar": sorted(kw) or None}


def degerlendirme_kosusu(kume: str = "training", azami: int = 24,
                         ayar=None) -> Dict[str, object]:
    """Küme üstünde **tam eşleşme** ölçümü. Ölçüt sert kalır.

    Sınama çıktısı motora hiç gösterilmez; yalnız burada, ölçüm
    anında kıyaslanır. Gösterildiği an ölçü yalan olur.
    """
    from nefs.musahede import gorev_dizisi
    nefs, a = _motor(ayar)
    gorevler = list(gorevleri_getir(kume))[:int(azami)]
    deneme = cozulen = konusan = 0
    hucre: List[float] = []
    t0 = time.perf_counter()
    for g in gorevler:
        r = padisah(g, nefs=nefs, ayar=a)
        deneme += 1
        if r["sükût"]:
            continue
        konusan += 1
        try:
            _, hedef = gorev_dizisi(g)
        except Exception:                                # noqa: BLE001
            continue
        h = [int(x) % a.sozluk for x in hedef]
        u = list(r["belirteç"] or [])
        n = min(len(h), len(u))
        if n:
            hucre.append(sum(1 for i in range(n) if h[i] == u[i]) / n)
        if u[:len(h)] == h:
            cozulen += 1
    return {"küme": kume, "deneme": deneme, "konuşan": konusan,
            "susan": deneme - konusan, "tam_çözülen": cozulen,
            "ortalama_hücre_isabeti":
                float(np.mean(hucre)) if hucre else 0.0,
            "süre_sn": time.perf_counter() - t0}


def kos(kume: str = "training", azami: int = 24) -> str:  # pragma: no cover
    d = degerlendirme_kosusu(kume, azami)
    return "\n".join([
        "=== ÇIKARIM -- motor cevabı (elle kâide YOK) ===", "",
        "  küme            : %s" % d["küme"],
        "  deneme          : %d" % d["deneme"],
        "  konuşan / susan : %d / %d" % (d["konuşan"], d["susan"]),
        "  TAM çözülen     : %d" % d["tam_çözülen"],
        "  hücre isabeti   : %.4f" % d["ortalama_hücre_isabeti"],
        "  süre            : %.1f sn" % d["süre_sn"],
        "",
        "  Elle kurulmuş hiçbir ARC kâidesi kullanılmadı; eski dalga",
        "  öğrenicisi yedek/kume9_arc_hileleri/cikarim_dalga.py'de.",
    ])


if __name__ == "__main__":                               # pragma: no cover
    print(kos(sys.argv[1] if len(sys.argv) > 1 else "training",
              int(sys.argv[2]) if len(sys.argv) > 2 else 24))
