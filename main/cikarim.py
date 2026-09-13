from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import sys
import time
from typing import Dict, List, Optional, Sequence

import numpy as np

from nefs.musahede import gorevleri_getir
from nefs.hafiza import Hafiza
from nefs.sadakat import sadakat_beyani
from nefs.suphe import suphe_beyani
from tanilama.beyan import cikarim_beyani

__all__ = ["padisah", "degerlendirme_kosusu", "hazineden_yukle",
           "hafizayi_yukle", "hazineden_devam", "devam_agirligi", "kos"]


def hazineden_devam(yol: str) -> Dict[str, object]:
    from main import hazine
    tam = yol + hazine.UZANTI
    if not os.path.isfile(tam):
        return {"yüklendi": False, "yol": tam, "tur": 0, "imleç": None,
                "sebep": "hazine yok -- ilk tur"}
    agirlik, ham = hazine.al(yol)
    ust = hazine.ust_coz(ham)
    assert "p" in agirlik, "hazinede ``p`` tensörü yok: %r" % sorted(agirlik)
    p = np.array(agirlik["p"], dtype=float).reshape(-1)
    assert np.all(np.isfinite(p)), "hazinedeki parametrede NaN/Inf var"
    musterek = agirlik.get("münasebet.M")
    harita = ust.get("harita")
    assert harita is None or isinstance(harita, dict), (
        "hazinedeki münasebet haritası sözlük değil (%s)"
        % type(harita).__name__)
    imlec = ust.get("imleç")
    assert imlec is None or isinstance(imlec, dict), (
        "hazinedeki imleç sözlük değil (%s) -- üst veri çözülmemiş "
        "olmalı (main/hazine.py:ust_coz)" % type(imlec).__name__)
    return {"yüklendi": True, "yol": tam, "p": p,
            "tur": int(ust.get("tur", 0) or 0),
            "imleç": imlec or None,
            "harita": harita or None,
            "müşterek": (None if musterek is None
                         else np.array(musterek, dtype=float)),
            "müşterek_işlenen": int(ust.get("müşterek_işlenen", 0) or 0),
            "V_son": ust.get("V_son"),
            "bayt": int(os.path.getsize(tam))}


def devam_agirligi(devam: Dict[str, object], nefs, d: int) -> np.ndarray:
    if not devam.get("yüklendi"):
        return nefs.vektor()
    p = np.asarray(devam["p"], float).reshape(-1)
    assert p.size == d, (
        "HAZİNEDEKİ AĞIRLIK BU AYARA UYMUYOR: %d parametre kayıtlı, %d "
        "isteniyor. Ayar değişmiş demektir; devam etmek başka bir modeli "
        "sürdürmek olurdu. Sıfırlayın: ``python -m main.egitim sıfırla``"
        % (p.size, d))
    nefs.yukle(p)
    devam["kaldığı_kayıp"] = devam.get("V_son")
    return p


def hafizayi_yukle(ayar, dizin: Optional[str] = None) -> "Hafiza":
    from main import hazine
    from main.egitim import hazine_yolu
    yol = hazine_yolu(dizin)
    agirlik, ust = hazine.al(yol)
    h = Hafiza.hazineden(agirlik, ust)
    assert h is not None, "hafıza kurulamadı -- boş bir şey dönemez"
    return h


def hazineden_yukle(nefs, ayar, dizin: Optional[str] = None,
                    ham: bool = False) -> Dict[str, object]:
    from main import hazine
    from main.egitim import hazine_yolu
    if ham:
        return {"yüklendi": False, "sebep": "ham kip istendi", "yol": None}
    yol = hazine_yolu(dizin)
    tam = yol + hazine.UZANTI
    assert os.path.exists(tam), (
        "HAZİNE YOK: %s\n  Evvela tâlimi koşturun (``python -m main.egitim "
        "tâlim``). Eğitilmemiş motorla çıkarım yapıp neticeyi rapora "
        "yazmak ölçüyü yalanlamaktır; onun için burası sessizce "
        "geçilmiyor." % (tam,))
    agirlik, ust = hazine.al(yol)
    assert "p" in agirlik, "hazinede ``p`` tensörü yok: %r" % sorted(agirlik)
    p = np.array(agirlik["p"], dtype=float).reshape(-1)
    assert p.size == len(nefs), (
        "hazinedeki parametre %d, nefsinki %d -- ayar değişmiş olmalı"
        % (p.size, len(nefs)))
    assert np.all(np.isfinite(p)), "hazinedeki parametrede NaN/Inf var"
    nefs.yukle(p)
    return {"yüklendi": True, "yol": tam, "parametre": int(p.size),
            "üst_veri": ust}


def _motor(ayar=None, ham: bool = False):
    from main.egitim import KISA_CPU
    from nefs.melekeler import QNefs
    a = ayar or KISA_CPU
    nefs = QNefs(a.tohum, a.qayar())
    nefs.idrak_et(np.eye(2, a.veri_lifi))
    from nefs.kulli_kayip import kademe_parametreleri_ac
    kademe_parametreleri_ac(nefs.p)
    yuk = hazineden_yukle(nefs, a, ham=ham)
    haf = None if ham else hafizayi_yukle(a)
    if haf is not None:
        yuk["hafıza"] = haf.beyan()
    return nefs, a, yuk, haf


def padisah(gorev, nefs=None, ayar=None, **kw) -> Dict[str, object]:
    from nefs.soyle import soyle
    hafiza = kw.pop("hafiza", None)
    if nefs is None:
        nefs, ayar, _, hafiza = _motor(ayar)
    if ayar is None:
        from main.egitim import KISA_CPU
        ayar = KISA_CPU
    c = soyle(gorev, nefs=nefs, sozluk=int(ayar.sozluk), hafiza=hafiza)
    return {"görev": getattr(gorev, "ad", ""),
            "sükût": bool(c.sukut),
            "sebep": c.sebep,
            "kural": c.kural,
            "belirteç": c.belirtec,
            "güven": float(c.guven),
            "budanan": int(getattr(c, "budanan", 0)),
            "yutulan_ayar": sorted(kw) or None}


def degerlendirme_kosusu(kume: str = "training", azami: int = 24,
                         ayar=None, ham: bool = False) -> Dict[str, object]:
    from nefs.musahede import gorev_dizisi
    nefs, a, yuk, hafiza = _motor(ayar, ham=ham)
    gorevler = list(gorevleri_getir(kume))[:int(azami)]
    assert gorevler, "değerlendirilecek görev BOŞ -- ölçü bir şey ölçmüyor"
    deneme = cozulen = konusan = budanan = 0
    hucre: List[float] = []
    t0 = time.perf_counter()
    for g in gorevler:
        r = padisah(g, nefs=nefs, ayar=a, hafiza=hafiza)
        deneme += 1
        if r["sükût"]:
            continue
        konusan += 1
        budanan += int(r.get("budanan", 0))
        _, hedef = gorev_dizisi(g)
        assert len(hedef) > 0, "görev %r için hedef BOŞ" % getattr(g, "ad", "")
        from nefs.belirtec import basamak_sayisi, tip_vektoru
        _bs = basamak_sayisi(int(a.sozluk), int(a.veri_lifi))
        h = [int(x) for x in tip_vektoru(hedef, int(a.veri_lifi), _bs)]
        u = list(r["belirteç"] or [])
        n = min(len(h), len(u))
        if n:
            hucre.append(sum(1 for i in range(n) if h[i] == u[i]) / n)
        if u[:len(h)] == h:
            cozulen += 1
    sad = sadakat_beyani()
    sup = suphe_beyani()
    assert int(sad["çağrı"]) > 0, (
        "MANTIĞA SADAKAT ÇIKARIMDA KOŞMADI -- 7/24 iddiası düşer.")
    return {"küme": kume, "deneme": deneme, "konuşan": konusan,
            "hazine": yuk, "budanan": budanan,
            "sadakat": sad, "şüphe": sup,
            "susan": deneme - konusan, "tam_çözülen": cozulen,
            "ortalama_hücre_isabeti":
                float(np.mean(hucre)) if hucre else 0.0,
            "süre_sn": time.perf_counter() - t0}


def kos(kume: str = "training", azami: int = 24,
        ham: bool = False) -> str:
    return cikarim_beyani(degerlendirme_kosusu(kume, azami, ham=ham))


if __name__ == "__main__":
    print(kos(sys.argv[1] if len(sys.argv) > 1 else "training",
              int(sys.argv[2]) if len(sys.argv) > 2 else 24))
