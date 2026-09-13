from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["MunasebetAyari", "Harita", "munasebet_kos", "munasebet_beyani",
           "munasebet_metni", "munasebet_sifirla"]


@dataclass
class MunasebetAyari:

    acik: int = 1
    obek: int = 8
    azami_tur: int = 8
    n_v: int = 16
    azami_saniye: float = 0.0


@dataclass
class Harita:

    n_v: int = 16
    M: np.ndarray = field(default_factory=lambda: np.zeros((16, 16)))
    islenen: int = 0

    def __post_init__(self) -> None:
        if self.M.shape != (int(self.n_v), int(self.n_v)):
            self.M = np.zeros((int(self.n_v), int(self.n_v)), float)

    def isle(self, baglam: Sequence[int], nispet: float) -> int:
        t = np.unique(np.asarray(list(baglam), np.int64) % int(self.n_v))
        if t.size < 2:
            return 0
        self.M[np.ix_(t, t)] += float(nispet)
        np.fill_diagonal(self.M, 0.0)
        self.islenen += 1
        return int(t.size * (t.size - 1))

    def zayiflik(self, baglam: Sequence[int]) -> float:
        t = np.unique(np.asarray(list(baglam), np.int64) % int(self.n_v))
        if t.size < 2:
            return 0.0
        alt = self.M[np.ix_(t, t)]
        return float(np.mean(1.0 / (1.0 + alt)))

    def doyma(self) -> float:
        toplam = float(self.M.size - self.n_v)
        if toplam <= 0:
            return 0.0
        return float(np.count_nonzero(self.M) / toplam)

    def hazineye(self) -> Dict[str, np.ndarray]:
        return {"münasebet.M": np.asarray(self.M, float)}

    @staticmethod
    def hazineden(agirlik: Optional[Dict[str, Any]], n_v: int,
                  islenen: int = 0) -> "Harita":
        M = (agirlik or {}).get("münasebet.M")
        if M is None:
            return Harita(n_v=int(n_v))
        M = np.asarray(M, float)
        assert M.shape == (int(n_v), int(n_v)), (
            "HAZİNEDEKİ MÜŞTEREK HARİTA BU AYARA UYMUYOR: %s kayıtlı, "
            "(%d,%d) isteniyor. Taşıyıcı tabanı değişmiş demektir; devam "
            "etmek başka bir haritayı sürdürmek olurdu. Sıfırlayın: "
            "``python -m main.egitim sıfırla``"
            % (M.shape, int(n_v), int(n_v)))
        return Harita(n_v=int(n_v), M=M, islenen=int(islenen))


_SAYAC: Dict[str, float] = {
    "örnek": 0.0, "tur": 0.0, "temizlenen": 0.0, "kirli_kalan": 0.0,
    "bag": 0.0, "kayip_cagrisi": 0.0, "geri_donen": 0.0,
    "denge": 0.0, "saat_kesti": 0.0}


def munasebet_kos(veri: Sequence[Tuple[Sequence[int], int]],
                  p0: np.ndarray,
                  eniyile: Callable[[np.ndarray, Sequence], Tuple],
                  olc: Callable[[np.ndarray, Sequence], Dict[str, Any]],
                  harita: Optional[Harita] = None,
                  ayar: Optional[MunasebetAyari] = None,
                  keyfiyet_ayari=None,
                  dengele: Optional[Callable[[Dict[str, Any]], Any]] = None
                  ) -> Dict[str, Any]:
    from .keyfiyet import esik, keyfiyet
    from .sadakat import sadakat_beyani

    a = ayar or MunasebetAyari()
    h = harita or Harita(n_v=int(a.n_v))
    p = np.asarray(p0, float).copy()
    if not int(a.acik):
        p, c = eniyile(p, list(veri))
        _SAYAC["kayip_cagrisi"] += float(c)
        return {"p": p, "harita": h, "açık": False, "örnek": 0,
                "temizlenen": 0, "kirli_kalan": 0, "tur": 0}

    t0 = time.perf_counter()
    had = float(a.azami_saniye)
    kalan = list(range(len(veri)))
    obek = max(1, int(a.obek))
    temizlenen = kirli = 0
    ugrayis: Dict[int, int] = {}
    while kalan:
        if had > 0.0 and time.perf_counter() - t0 >= had:
            _SAYAC["saat_kesti"] += float(len(kalan))
            kirli += len(kalan)
            break
        zayif = np.asarray([h.zayiflik(veri[i][0]) for i in kalan], float)
        sira = np.argsort(-zayif)[:obek]
        kume_idx = [kalan[int(j)] for j in sira]
        kume = [veri[i] for i in kume_idx]
        for i in kume_idx:
            kalan.remove(i)

        k: Dict[str, Any] = {}
        dokum: Optional[Dict[str, Any]] = None
        for tur in range(max(1, int(a.azami_tur))):
            if dengele is not None:
                if dokum is None:
                    dokum = olc(p, kume)
                dengele(dokum)
                _SAYAC["denge"] += 1.0
            p, c = eniyile(p, kume)
            _SAYAC["kayip_cagrisi"] += float(c)
            _SAYAC["tur"] += 1.0
            dokum = olc(p, kume)
            k = keyfiyet(dokum, sadakat_beyani(), keyfiyet_ayari)
            if k["hudut_temiz"]:
                break
            if k["nispet"] >= esik(tur + 1, int(a.azami_tur),
                                   keyfiyet_ayari):
                break
        assert k, "keyfiyet ölçülmeden küme kapatılamaz"
        from .qegitim import ornek_bol
        for bag, _hed, _cins, _makam in (ornek_bol(o) for o in kume):
            _SAYAC["bag"] += float(h.isle(bag, float(k["nispet"])))
        _SAYAC["örnek"] += float(len(kume))
        if k["hudut_temiz"]:
            temizlenen += 1
            continue
        anahtar = min(kume_idx)
        if anahtar not in ugrayis:
            ugrayis[anahtar] = 1 + int(round(float(k["nispet"])
                                             * max(1, int(a.azami_tur))))
        ugrayis[anahtar] -= 1
        if ugrayis[anahtar] > 0:
            _SAYAC["geri_donen"] += 1.0
            kalan[:0] = kume_idx
        else:
            kirli += 1

    _SAYAC["temizlenen"] += float(temizlenen)
    _SAYAC["kirli_kalan"] += float(kirli)
    return {"p": p, "harita": h, "açık": True,
            "örnek": int(_SAYAC["örnek"]), "temizlenen": temizlenen,
            "kirli_kalan": kirli, "tur": int(_SAYAC["tur"]),
            "doyma": h.doyma()}


def munasebet_beyani() -> Dict[str, Any]:
    k = max(1.0, _SAYAC["temizlenen"] + _SAYAC["kirli_kalan"])
    return {"örnek": int(_SAYAC["örnek"]), "tur": int(_SAYAC["tur"]),
            "temizlenen": int(_SAYAC["temizlenen"]),
            "kirli_kalan": int(_SAYAC["kirli_kalan"]),
            "temizlik_nispeti": float(_SAYAC["temizlenen"] / k),
            "bağ": int(_SAYAC["bag"]),
            "kayıp_çağrısı": int(_SAYAC["kayip_cagrisi"]),
            "geri_dönen": int(_SAYAC["geri_donen"]),
            "denge_çağrısı": int(_SAYAC["denge"]),
            "saat_kesti": int(_SAYAC["saat_kesti"]),
            "küme_başına_tur": float(_SAYAC["tur"] / k)}


def munasebet_sifirla() -> None:
    for k in _SAYAC:
        _SAYAC[k] = 0.0


def munasebet_metni(b: Optional[Dict[str, Any]] = None) -> str:
    d = dict(b if b is not None else munasebet_beyani())
    t = float(d.get("temizlik_nispeti", 0.0))
    hal = ("HİÇBİR KÜME TEMİZLENMEDİ" if t <= 0.0
           else "HEPSİ TEMİZLENDİ" if t >= 1.0 else "kısmen temiz")
    return "\n".join([
        "  MÜNASEBET -- BİR VERİ, HUDUDU TEMİZLENENE KADAR (ferman 1-I)",
        "    işlenen örnek   : %d   (küme başına %.2f tur)"
        % (d["örnek"], d["küme_başına_tur"]),
        "    temizlenen küme : %d      kirli kapanan: %d      → %s"
        % (d["temizlenen"], d["kirli_kalan"], hal),
        "    geri dönen küme : %d   (kirli kalan küme kuyruğun başına "
        "döner; sabır keyfiyetin fonksiyonudur)" % d.get("geri_dönen", 0),
        "    denge çağrısı   : %d   (λ'lar HER TURDA yeniden ölçülür; "
        "0 ise donmuş demektir)" % d.get("denge_çağrısı", 0),
        "    kayıp çağrısı   : %d      müşterek haritaya işlenen bağ: %d"
        % (d["kayıp_çağrısı"], d["bağ"]),
        "    saatin kestiği  : %d küme   (had dolunca kalan kümeler "
        "KİRLİ sayılır, temiz denmez)" % d.get("saat_kesti", 0)])
