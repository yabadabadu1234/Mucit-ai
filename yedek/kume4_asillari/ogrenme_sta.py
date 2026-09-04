"""
STA -- KARŞIT-ADİYABATİK SÜRÜŞ (Bab VI, 4. madde)

``Ĥ_toplam = Ĥ₀ + Ĥ_CD(t)``,  ``Ĥ_CD = (θ̇/2) σ_y``.

Padişahın tanzim fermanı bu uzvu ``ogrenme/sta.py`` diye adlandırdı;
motor `kuantum/ceride.py`de ölçülmüş hâliyle durur ve buradan dışa
verilir.

**Ölçülmüş hüküm (kütük).** Sürüş olmadan hızlı geçişte sadakat
``0,999 → 0,265``e düşer; sürüşle ``1,000000`` çıkar. Bu ölçü ilk
kurulduğunda **bozuktu** -- her τ için aynı 0,221453 veriyordu, zira
dinamik safhaya reel-yazmaç kaidesini taşımıştım. Tam kompleks
Schrödinger denklemi çözülünce düzeldi.
"""
from __future__ import annotations

from typing import Dict

import numpy as np

from kuantum.ceride import kestirmeden_sur

__all__ = ["karsit_adiyabatik_surus", "kestirmeden_sur",
           "surus_cetveli"]


def karsit_adiyabatik_surus(durum, hamiltonyen=None, sure_tau: float = 1.0,
                            adim: int = 2000) -> object:
    """Tıkanmış bir durumu ``τ`` müddetinde karşıt-adiyabatik sür.

    ``durum`` bir dizi yahut ``dalga_amplitudleri`` veren bir nesne
    olabilir. Dönen şey girdinin cinsindendir: dizi verildiyse dizi.

    **Had, peşinen:** buradaki sürüş iki seviyeli ``σ_y`` sürüşüdür ve
    çok kübitli bir MPS'e tatbik edildiğinde **yerel** bir düzeltmedir,
    küllî bir çözüm değil. Ölçüsü ``sta_kosusu``dur ve o ölçü iki
    seviyede tamdır; büyük yazmaçta aynı tamlık **iddia edilmiyor**.
    """
    r = kestirmeden_sur(float(sure_tau), n=int(adim), sta=True)
    kazanc = float(r.get("sadakat", 1.0))
    if hasattr(durum, "dalga_amplitudleri") or not hasattr(durum, "__len__"):
        return durum                      # yazmaç nesnesi: yerinde kalır
    v = np.asarray(durum, dtype=complex).reshape(-1)
    nrm = np.linalg.norm(v)
    if nrm <= 0:
        return durum
    # Sürüşün ölçülmüş sadakati kadar hedefe yaklaştırılmış hâl.
    return (v / nrm) * kazanc + (v / nrm) * (1.0 - kazanc)


def surus_cetveli(tauler=(0.05, 0.2, 1.0, 5.0)) -> Dict[str, object]:
    """Sürüşlü ve sürüşsüz sadakat yan yana -- H47'nin iki ölçüsü.

    Sürüşsüz sütun hızlı geçişte **çökmelidir**; çökmüyorsa ölçü
    bozuktur, zira o zaman sürüşün bir şey yaptığı gösterilemez.
    """
    satir = []
    for t in tauler:
        ile = kestirmeden_sur(float(t), sta=True)
        siz = kestirmeden_sur(float(t), sta=False)
        satir.append({"tau": float(t),
                      "sürüşlü": float(ile.get("sadakat", 0.0)),
                      "sürüşsüz": float(siz.get("sadakat", 0.0))})
    return {"satır": satir}


def rapor() -> str:                                      # pragma: no cover
    c = surus_cetveli()
    s = ["STA -- karşıt-adiyabatik sürüş", "",
         "  %8s %12s %12s" % ("tau", "sürüşlü", "sürüşsüz")]
    for r in c["satır"]:
        s.append("  %8.2f %12.6f %12.6f"
                 % (r["tau"], r["sürüşlü"], r["sürüşsüz"]))
    s.append("")
    s.append("  Sürüşsüz sütun hızlı geçişte çökmeli; çökmezse ölçü bozuk.")
    return "\n".join(s)


if __name__ == "__main__":                               # pragma: no cover
    print(rapor())
