from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from matematik.sonsuz_mertebeler_teorisi import (MERTEBE_ADI, Deg,
                                                 rn_adi, rn_sarti)

__all__ = ["Mod", "FockUzayi", "Hamiltonyen", "balyala",
           "fock_beyani", "fock_metni",
           "hamiltonyen_beyani", "hamiltonyen_metni"]

_FOCK_SAYAC: Dict[str, float] = {
    "yaratma": 0.0, "yok_etme": 0.0, "balyalama": 0.0,
    "mertebe_çağrısı": 0.0}

_SON_FOCK: Dict[str, Any] = {}
_SON_TABAN: Dict[str, Any] = {}


def _mertebe_terimi(r: int, n: int) -> str:
    raise AssertionError(
        "MERTEBE UYDURULAMAZ. Bir modun (r, n) mertebesi bir etiket "
        "değildir: taşıyıcısının tipi kurulur ve "
        "matematik.sonsuz_mertebeler_teorisi.denetle_tip ile FİİLEN "
        "denetlenir; tutan en büyük (r, n) mertebedir. İndis modulo "
        "dörtten mertebe çıkmaz (ferman 2-Ā, 5).")


@dataclass
class Mod:

    ad: str
    entropi: float = 0.0
    butce: float = 0.0
    celiski: float = 0.0
    doluluk: int = 1
    r: int = 0
    n: int = 0

    def __post_init__(self) -> None:
        assert str(self.ad), "modun adı boş olamaz (ferman 4)"
        assert int(self.doluluk) >= 1, (
            "doluluk sayısı en az bir olmalı: %r" % (self.doluluk,))
        self.ad = str(self.ad)
        self.entropi = float(self.entropi)
        self.butce = float(self.butce)
        self.celiski = float(self.celiski)
        self.mertebe_adi = _mertebe_terimi(int(self.r), int(self.n))

    @property
    def bedel(self) -> float:
        return math.log2(1.0 + float(self.doluluk))

    @property
    def carpan(self) -> float:
        return (float(self.entropi) * (1.0 + float(self.celiski))
                / (1.0 + float(self.butce)))


class FockUzayi:

    def __init__(self) -> None:
        self.modlar: Dict[str, Mod] = {}
        self.yaratma = 0
        self.yok_etme = 0
        self.balyalama = 0

    def __len__(self) -> int:
        return len(self.modlar)

    def yarat(self, ad: str, entropi: float = 0.0, butce: float = 0.0,
              celiski: float = 0.0, r: int = 0, n: int = 0) -> Mod:
        self.yaratma += 1
        _FOCK_SAYAC["yaratma"] += 1.0
        m = self.modlar.get(str(ad))
        if m is None:
            m = Mod(ad=str(ad), entropi=float(entropi), butce=float(butce),
                    celiski=float(celiski), r=int(r), n=int(n))
            self.modlar[m.ad] = m
            return m
        self.balyalama += 1
        _FOCK_SAYAC["balyalama"] += 1.0
        m.doluluk += 1
        w = 1.0 / float(m.doluluk)
        m.entropi += w * (float(entropi) - m.entropi)
        m.butce += w * (float(butce) - m.butce)
        m.celiski += w * (float(celiski) - m.celiski)
        return m

    def yok_et(self, ad: str) -> bool:
        m = self.modlar.get(str(ad))
        if m is None:
            return False
        self.yok_etme += 1
        _FOCK_SAYAC["yok_etme"] += 1.0
        m.doluluk -= 1
        if m.doluluk <= 0:
            del self.modlar[str(ad)]
        return True

    @property
    def acik(self) -> int:
        return int(self.yaratma - self.balyalama - self.yok_etme)

    @property
    def bedel(self) -> float:
        return float(sum(m.bedel for m in self.modlar.values()))

    @property
    def cizgi_bedeli(self) -> int:
        return int(sum(m.doluluk for m in self.modlar.values()))

    def beyan(self) -> Dict[str, Any]:
        en = max(self.modlar.values(), key=lambda m: m.carpan,
                 default=None)
        o = {"mod": len(self.modlar), "yaratma": int(self.yaratma),
             "yok_etme": int(self.yok_etme),
             "balyalama": int(self.balyalama), "açık": int(self.acik),
             "doluluk_toplamı": int(self.cizgi_bedeli),
             "bedel_log": float(self.bedel),
             "tasarruf": float(self.cizgi_bedeli) - float(self.bedel),
             "en_ağır": (en.ad if en is not None else "yok"),
             "en_ağır_çarpan": (float(en.carpan) if en is not None
                                else 0.0),
             "mertebe": (en.mertebe_adi if en is not None
                         else rn_adi(0, 0))}
        _SON_FOCK.clear()
        _SON_FOCK.update(o)
        return o


class Hamiltonyen:

    def __init__(self, fock: Optional[FockUzayi] = None,
                 beta: Optional[float] = None) -> None:
        self.fock = fock if fock is not None else FockUzayi()
        self.adlar: Tuple[str, ...] = ()
        self.h = np.zeros(0, float)
        self.ham = np.zeros(0, float)
        self.beta = self._beta() if beta is None else float(beta)
        self.tur = 0

    @staticmethod
    def _beta() -> float:
        from .donanim import bellek_haddi
        b = bellek_haddi()
        assert b, (
            "bellek haddi yoklanamadı -- kuplaj şiddeti elle yazılamaz "
            "(ferman 5-B, 1-J)")
        return float(1.0 / (1.0 + math.log2(1.0 + float(b) / 2.0 ** 30)))

    def kefelerden(self, dokum: Dict[str, Any]) -> "Hamiltonyen":
        adlar = tuple(str(a) for a in dokum["artık_adı"])
        h = np.asarray(dokum["artık"], float).reshape(-1)
        ham = np.asarray(dokum.get("ham_artık", h), float).reshape(-1)
        assert h.size == len(adlar), (
            "kefe adedi ile artık adedi tutmuyor: %d ≠ %d"
            % (len(adlar), h.size))
        assert np.all(np.isfinite(h)), "Ĥ terimlerinde NaN/Inf var"
        self.adlar, self.h, self.ham = adlar, h, ham
        self.tur += 1
        top = float(np.abs(h).sum()) or 1.0
        for i, ad in enumerate(adlar):
            p = float(abs(h[i])) / top
            self.fock.yarat(
                ad, entropi=float(-p * math.log(p + 1e-300)),
                butce=float(abs(h[i])), celiski=float(abs(ham[i])),
                r=int(min(len(MERTEBE_ADI) - 1, i % len(MERTEBE_ADI))),
                n=int(min(len(MERTEBE_ADI) - 1,
                          (i // len(MERTEBE_ADI)) % len(MERTEBE_ADI))))
        return self

    def kuplaj(self) -> np.ndarray:
        h = self.h
        V = np.outer(np.abs(h), np.abs(h))
        np.fill_diagonal(V, 0.0)
        return V

    def enerji(self) -> float:
        return float(self.h.sum()
                     + self.beta * 0.5 * float(self.kuplaj().sum()))

    def yavas_mod(self) -> Tuple[int, str, float]:
        assert self.h.size, "Ĥ boş -- evvelâ kefelerden kurulur"
        V = self.kuplaj()
        kutle = V.sum(axis=1)
        ent = np.array([self.fock.modlar[a].entropi
                        if a in self.fock.modlar else 0.0
                        for a in self.adlar], float)
        agir = kutle * ent
        i = int(np.argmax(agir)) if float(agir.max()) > 0.0 else \
            int(np.argmax(kutle))
        return i, self.adlar[i], float(agir[i])

    def taban_durumu(self) -> Dict[str, Any]:
        i, ad, agir = self.yavas_mod()
        V = self.kuplaj()
        alan = self.h + self.beta * V[:, i]
        alan[i] = self.h[i]
        top = float(np.abs(alan).sum()) or 1.0
        pay = np.abs(alan) / top
        konfig = {}
        for j, a in enumerate(self.adlar):
            m = self.fock.modlar.get(a)
            konfig[a] = int(max(1, round(float(pay[j]) * float(
                m.doluluk if m is not None else 1) * len(self.adlar))))
        sonen = int(np.count_nonzero(pay <= float(np.finfo(float).eps)))
        o = {"yavaş_mod": str(ad), "yavaş_ağırlık": float(agir),
             "β": float(self.beta), "enerji": float(self.enerji()),
             "şartlı_enerji": float(alan.sum()),
             "terim": int(self.h.size), "sönen": sonen,
             "konfigürasyon": konfig,
             "tur": int(self.tur),
             "en_dolu": max(konfig, key=konfig.get) if konfig else "yok",
             "kovaryans": float(np.abs(V).sum()
                                / max(1.0, float(V.size - V.shape[0])))}
        _SON_TABAN.clear()
        _SON_TABAN.update(o)
        return o


def balyala(hafiza, fock: FockUzayi) -> Dict[str, Any]:
    kayitlar = list(getattr(hafiza, "kayitlar", []) or [])
    if not kayitlar:
        return {"kayıt": 0, "balya": 0, "doygunluk": 0.0,
                "mertebe": rn_adi(0, 0), "taşınan": 0}
    tasinan = 0
    balyalar: Dict[str, int] = {}
    for k in kayitlar:
        yap = str(getattr(k, "yaprak", "") or "kök")
        hk = float(getattr(k, "hukum", 0.0))
        r = int(min(len(MERTEBE_ADI) - 1, len(yap.split("|")) - 1))
        n = int(min(len(MERTEBE_ADI) - 1, abs(int(round(hk))) ))
        ad = "balya.%s.%d" % (yap.split("|")[0], int(round(hk)))
        m = fock.yarat(ad, entropi=float(getattr(k, "mu", 0.0)),
                       butce=float(k.x.size), celiski=abs(float(
                           getattr(k, "omega", 0.0))), r=r, n=n)
        balyalar[ad] = int(m.doluluk)
        if ad not in yap:
            k.yaprak = (yap + "|" + ad) if getattr(k, "yaprak", "") else ad
            tasinan += 1
    balya = len(balyalar)
    return {"kayıt": len(kayitlar), "balya": int(balya),
            "doygunluk": float(1.0 - balya / float(len(kayitlar))),
            "taşınan": int(tasinan),
            "mertebe": rn_adi(len(MERTEBE_ADI) - 1, len(MERTEBE_ADI) - 1),
            "en_kalabalık": max(balyalar, key=balyalar.get),
            "en_kalabalık_kat": int(max(balyalar.values()))}


def fock_beyani() -> Dict[str, Any]:
    return dict(_SON_FOCK) if _SON_FOCK else {
        "mod": 0, "yaratma": 0, "yok_etme": 0, "balyalama": 0,
        "açık": 0, "doluluk_toplamı": 0, "bedel_log": 0.0,
        "tasarruf": 0.0, "en_ağır": "KOŞMADI", "en_ağır_çarpan": 0.0,
        "mertebe": rn_adi(0, 0)}


def hamiltonyen_beyani() -> Dict[str, Any]:
    return dict(_SON_TABAN) if _SON_TABAN else {
        "yavaş_mod": "KOŞMADI", "yavaş_ağırlık": 0.0, "β": 0.0,
        "enerji": 0.0, "şartlı_enerji": 0.0, "terim": 0, "sönen": 0,
        "konfigürasyon": {}, "tur": 0, "en_dolu": "yok",
        "kovaryans": 0.0}


def fock_metni(b: Optional[Dict[str, Any]] = None) -> str:
    d = b if b is not None else fock_beyani()
    return "\n".join([
        "  FOCK UZAYI -- MESELE SAYISI ÖNCEDEN BİLİNMEZ (ferman 2-Þ)",
        "    mod %d   yaratma a† %d   yok etme a %d   AÇIK %d"
        % (int(d["mod"]), int(d["yaratma"]), int(d["yok_etme"]),
           int(d["açık"])),
        "    balyalama %d   doluluk toplamı %d   bedel log₂ %.3f"
        % (int(d["balyalama"]), int(d["doluluk_toplamı"]),
           float(d["bedel_log"])),
        "    TASARRUF %.3f mod  (tekrar n nüsha değil, tek modun n katı",
        "    -- ferman 2-Ƶ: unutma yok, tecrit var)",
        "    en ağır mod: %s  çarpan %.6e   mertebe %s"
        % (d["en_ağır"], float(d["en_ağır_çarpan"]), d["mertebe"]),
        "    a† ile a farkı sıfır değilse açık mod kalmıştır (ferman 5)."])


def hamiltonyen_metni(b: Optional[Dict[str, Any]] = None) -> str:
    d = b if b is not None else hamiltonyen_beyani()
    k = dict(d.get("konfigürasyon") or {})
    ilk = sorted(k.items(), key=lambda x: -x[1])[:5]
    return "\n".join([
        "  BİRLEŞİK HAMİLTONYEN -- TEK UZAY, ÇOK SERBESTLİK (ferman 2-Þ)",
        "    Ĥ terimi %d   β(ölçülen bellekten) %.6f   tur %d"
        % (int(d["terim"]), float(d["β"]), int(d["tur"])),
        "    enerji %.6e   şartlı enerji %.6e   sönen koordinat %d"
        % (float(d["enerji"]), float(d["şartlı_enerji"]),
           int(d["sönen"])),
        "    YAVAŞ MOD (ölçüldü, elle yazılmadı): %s   ağırlık %.6e"
        % (d["yavaş_mod"], float(d["yavaş_ağırlık"])),
        "    kovaryans (V̂_kuplaj ortalaması) %.6e" % float(d["kovaryans"]),
        "    taban durumu konfigürasyonu (en dolu beş serbestlik):",
        "      " + ("  ".join("%s=%d" % (a, n) for a, n in ilk) or "yok"),
        "    Kefeler HEM kendi sayısını verir HEM Ĥ'in terimidir (şık 3).",
        "    Eleme yoktur: pahalı koordinat söner, kapatılmaz."])
