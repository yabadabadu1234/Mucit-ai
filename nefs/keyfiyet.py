from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np

__all__ = ["KeyfiyetAyari", "keyfiyet", "esik", "keyfiyet_beyani", "keyfiyet_metni",
           "keyfiyet_son", "keyfiyet_sifirla"]


@dataclass
class KeyfiyetAyari:

    acik: int = 1
    azami_tur: int = 8
    taban: float = 0.25


_HAL: Dict[str, float] = {"en_iyi": 0.0, "çağrı": 0.0, "toplam": 0.0,
                          "temiz": 0.0, "kirli": 0.0}
_GECMIS: List[float] = []


def keyfiyet(kefeler: Dict[str, Any],
             sadakat: Optional[Dict[str, Any]] = None,
             ayar: Optional[KeyfiyetAyari] = None) -> Dict[str, Any]:
    a = ayar or KeyfiyetAyari()
    _HAL["çağrı"] += 1.0

    cevrim = max(1, int(kefeler.get("meşru", 0)) + int(kefeler.get("kısır", 0))
                 + int(kefeler.get("tenakuz", 0)) + int(kefeler.get("engel", 0)))
    n_ten = int(kefeler.get("tenakuz", 0))
    n_kis = int(kefeler.get("kısır", 0))
    assert sadakat is None or "artık_nispeti" in sadakat, (
        "sadakat beyanında ``artık_nispeti`` yok -- mantıksızlık hududu "
        "gelen taşmadan okunamaz (ferman 5)")
    tasma = float((sadakat or {}).get("artık_nispeti", 0.0))
    bel_tasma = float(kefeler.get("taşma", 0.0))

    nis_ten = 1.0 - float(n_ten) / cevrim
    nis_kis = 1.0 - float(n_kis) / cevrim
    nis_par = max(0.0, 1.0 - tasma)
    nis_bel = max(0.0, 1.0 - bel_tasma)
    nis_man = nis_par * nis_bel
    nispet = float(nis_ten * nis_kis * nis_man)
    assert 0.0 <= nispet <= 1.0 + 1e-9, "nispet [0,1] dışına çıktı"

    cozunurluk = float(np.finfo(float).eps)
    hudut = {"tenakuz": n_ten, "kısırdöngü": n_kis,
             "mantıksızlık": (int(tasma > cozunurluk)
                              + int(bel_tasma > cozunurluk))}
    temiz = all(v == 0 for v in hudut.values())

    _HAL["toplam"] += nispet
    _HAL["en_iyi"] = max(_HAL["en_iyi"], nispet)
    _HAL["temiz" if temiz else "kirli"] += 1.0
    _GECMIS.append(nispet)
    for ad, v in (("ten", nis_ten), ("kis", nis_kis), ("man", nis_man)):
        _HAL["n_" + ad] = _HAL.get("n_" + ad, 0.0) + float(v)
        _HAL["en_kotu_" + ad] = min(
            _HAL.get("en_kotu_" + ad, 1.0), float(v))
    return {"hudut": hudut, "hudut_temiz": bool(temiz), "nispet": nispet,
            "nispet_tenakuz": nis_ten, "nispet_kısır": nis_kis,
            "nispet_mantık": nis_man, "çevrim": cevrim,
            "parite_taşması": tasma, "belirteç_taşması": bel_tasma,
            "nispet_parite": nis_par, "nispet_belirteç": nis_bel,
            "açık": bool(int(a.acik))}


def esik(tur: int, azami_tur: int,
         ayar: Optional[KeyfiyetAyari] = None) -> float:
    a = ayar or KeyfiyetAyari()
    T = max(1, int(azami_tur))
    kalan = max(0.0, 1.0 - float(tur) / T)
    t = float(a.taban)
    return float(_HAL["en_iyi"] * (t + (1.0 - t) * kalan))


def keyfiyet_beyani() -> Dict[str, Any]:
    c = max(1.0, _HAL["çağrı"])
    g = np.asarray(_GECMIS, float) if _GECMIS else np.zeros(1)
    return {"çağrı": int(_HAL["çağrı"]),
            "en_iyi": float(_HAL["en_iyi"]),
            "ortalama": float(_HAL["toplam"] / c),
            "ortanca": float(np.median(g)),
            "temiz": int(_HAL["temiz"]), "kirli": int(_HAL["kirli"]),
            "temiz_nispeti": float(_HAL["temiz"] / c),
            "son_eşik": float(esik(0, 1)),
            "ort_tenakuz": float(_HAL.get("n_ten", 0.0) / c),
            "ort_kısır": float(_HAL.get("n_kis", 0.0) / c),
            "ort_mantık": float(_HAL.get("n_man", 0.0) / c),
            "en_kötü_tenakuz": float(_HAL.get("en_kotu_ten", 1.0)),
            "en_kötü_kısır": float(_HAL.get("en_kotu_kis", 1.0)),
            "en_kötü_mantık": float(_HAL.get("en_kotu_man", 1.0))}


def keyfiyet_son() -> float:
    return float(_GECMIS[-1]) if _GECMIS else 0.0


def keyfiyet_sifirla() -> None:
    for k in _HAL:
        _HAL[k] = 0.0
    _GECMIS.clear()


def keyfiyet_metni(b=None) -> str:
    d = dict(b if b is not None else keyfiyet_beyani())
    return "\n".join([
        "  KEYFİYET -- ÜÇ KAT'Î HUDUT (ferman 1-I) ve EŞİK FONKSİYONU (1-J)",
        "    ölçüm       : %d      temiz: %d   kirli: %d   (nispet %.4f)"
        % (d["çağrı"], d["temiz"], d["kirli"], d["temiz_nispeti"]),
        "    nispet      : en iyi %.4f   ortanca %.4f   ortalama %.4f"
        % (d["en_iyi"], d["ortanca"], d["ortalama"]),
        "    çarpanlar   : tenakuz %.4f   kısır %.4f   mantık %.4f "
        "(ortalama; 1 = o hudut temiz)"
        % (d.get("ort_tenakuz", 0.0), d.get("ort_kısır", 0.0),
           d.get("ort_mantık", 0.0)),
        "    en kötü hâli: tenakuz %.4f   kısır %.4f   mantık %.4f "
        "← HANGİSİ SIFIRA YAKINSA HUDUT ONDAN KİRLİ"
        % (d.get("en_kötü_tenakuz", 1.0), d.get("en_kötü_kısır", 1.0),
           d.get("en_kötü_mantık", 1.0)),
        "    nispet = (1−tenakuz/çevrim)·(1−kısır/çevrim)·(1−artık) "
        "-- ÇARPIM, ortalama değil: bir hudut kirliyse nispet sıfırdır."])
