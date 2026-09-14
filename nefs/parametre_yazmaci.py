from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

__all__ = ["ParametreAyari", "ParametreYazmaci", "parametre_seviyesi",
           "parametre_beyani", "parametre_metni"]


@dataclass
class ParametreAyari:

    faz_mertebesi: int = 16
    tohum: int = 0
    pay: float = 0.5
    azami_seviye: int = 1 << 20


def parametre_seviyesi(d_veri: int, yigin: int, bellek: Optional[int],
                       pay: float = 0.5, bayt_genlik: int = 16,
                       azami: int = 1 << 20) -> int:
    if int(d_veri) <= 0:
        return int(azami)
    assert bellek is not None and int(bellek) > 0, (
        "parametre yazmacının ebadı ölçülen bellekten türer; bellek "
        "yoklanamadıysa bütçe uydurulmaz (ferman 5-B, 2-S)")
    tavan = float(bellek) * float(pay)
    tek_dilim = float(max(1, int(yigin))) * float(int(d_veri)) * float(
        int(bayt_genlik))
    kac = int(tavan // tek_dilim)
    assert kac >= 1, (
        "müşterek durumun TEK dilimi bile ölçülen belleğe sığmıyor: "
        "yığın %d × veri seviyesi %d × %d bayt = %.1f MB, pay %.1f MB "
        "(ferman 2-S: sığmayan bütçe kurulmaz)"
        % (int(yigin), int(d_veri), int(bayt_genlik), tek_dilim / 1e6,
           tavan / 1e6))
    return min(int(azami), 1 << int(math.floor(math.log2(kac))))


class ParametreYazmaci:

    def __init__(self, d_veri: int, yigin: int, bellek: Optional[int],
                 ayar: Optional[ParametreAyari] = None) -> None:
        self.ayar = ayar or ParametreAyari()
        self.d_veri = int(d_veri)
        self.yigin = max(1, int(yigin))
        self.bellek = None if bellek is None else int(bellek)
        self.d = parametre_seviyesi(self.d_veri, self.yigin, self.bellek,
                                    float(self.ayar.pay),
                                    azami=int(self.ayar.azami_seviye))
        m = int(self.ayar.faz_mertebesi)
        assert m >= 4 and m % 4 == 0, (
            "faz mertebesi dörtün katı olmalı: %d" % m)
        r = np.random.default_rng(int(self.ayar.tohum))
        self.genlik = np.abs(r.normal(scale=1.0, size=self.d))
        self.genlik = self.genlik / max(float(np.linalg.norm(self.genlik)),
                                        1e-300)
        self.faz = r.integers(0, m, size=self.d).astype(np.int64)
        self._yer: Dict[str, Tuple[int, int]] = {}
        self._bas = 0

    @property
    def parametre_adedi(self) -> int:
        return 2 * int(self.d)

    @property
    def genislik(self) -> int:
        return 1

    def __len__(self) -> int:
        return int(self.parametre_adedi)

    def al(self, anahtar: str, n: int) -> np.ndarray:
        return self.aci(anahtar, int(n), 1.0)

    def buyukluk(self, anahtar: str, n: int) -> np.ndarray:
        return self.genlik[self.adres(anahtar, int(n))]

    def aci_adresi(self, anahtar: str, n: int) -> np.ndarray:
        return int(self.d) + self.adres(anahtar, int(n))

    def aci_katsayisi(self) -> float:
        return 2.0 * math.pi

    def adres(self, anahtar: str, n: int) -> np.ndarray:
        n = max(1, int(n))
        if anahtar not in self._yer:
            assert self._bas + n <= self.d, (
                "parametre yazmacı doldu: %r %d seviye istiyor, %d "
                "seviyeden %d kullanıldı. Çare daraltmak değil yazmacı "
                "büyütmektir (ferman 2-S)."
                % (anahtar, n, self.d, self._bas))
            self._yer[anahtar] = (self._bas, n)
            self._bas += n
        bas, kac = self._yer[anahtar]
        return bas + (np.arange(n, dtype=np.int64) % int(kac))

    def aci(self, anahtar: str, n: int, olcek: float = 1.0) -> np.ndarray:
        a = self.adres(anahtar, n)
        m = float(self.ayar.faz_mertebesi)
        return float(olcek) * (2.0 * math.pi) * (
            self.faz[a].astype(float) / m)

    def dilim_acisi(self, anahtar: str, n: int, olcek: float,
                    B_ortak: int) -> np.ndarray:
        a = self.adres(anahtar, n)
        m = float(self.ayar.faz_mertebesi)
        t = np.zeros(self.d, float)
        t[a] = float(olcek) * (2.0 * math.pi) * (
            self.faz[a].astype(float) / m)
        kac = max(1, int(B_ortak) // int(self.d))
        assert kac * self.d == int(B_ortak), (
            "müşterek yığın parametre seviyesinin katı olmalı: %d ∤ %d "
            "-- parametre seviyeleri yığın ekseninde durur (ferman 2-R)"
            % (int(self.d), int(B_ortak)))
        return np.tile(t, kac)

    def dal_agirligi(self, B_ortak: int = 0) -> np.ndarray:
        if int(B_ortak) <= 0:
            return self.genlik.copy()
        kac = max(1, int(B_ortak) // int(self.d))
        return np.tile(self.genlik, kac)

    def defter(self) -> Dict[str, Tuple[int, int]]:
        return dict(self._yer)

    def vektor(self) -> np.ndarray:
        m = float(self.ayar.faz_mertebesi)
        return np.concatenate([self.genlik,
                               self.faz.astype(float) / m])

    def yukle(self, v: np.ndarray) -> None:
        v = np.asarray(v, float).reshape(-1)
        assert v.size == 2 * self.d, (
            "parametre vektörü yazmaç ebadında olmalı: %d ≠ 2·%d"
            % (v.size, self.d))
        g = np.abs(v[:self.d])
        self.genlik = g / max(float(np.linalg.norm(g)), 1e-300)
        m = int(self.ayar.faz_mertebesi)
        self.faz = (np.rint(v[self.d:] * m).astype(np.int64)) % m

    def hazineye(self) -> Dict[str, np.ndarray]:
        return {"parametre.genlik": self.genlik.copy(),
                "parametre.faz": self.faz.copy()}

    def hazineden(self, agirlik) -> bool:
        g = None if agirlik is None else agirlik.get("parametre.genlik")
        f = None if agirlik is None else agirlik.get("parametre.faz")
        if g is None or f is None:
            return False
        g = np.asarray(g, float).reshape(-1)
        f = np.asarray(f, np.int64).reshape(-1)
        if g.size != self.d or f.size != self.d:
            return False
        self.genlik = g / max(float(np.linalg.norm(g)), 1e-300)
        self.faz = f % int(self.ayar.faz_mertebesi)
        return True

    def beyan(self) -> Dict[str, Any]:
        tek = self.yigin * self.d_veri * 16
        return {"seviye": int(self.d),
                "qudit": int(round(math.log2(max(2, self.d)) / 6.0)),
                "kübit": int(round(math.log2(max(2, self.d)))),
                "faz_mertebesi": int(self.ayar.faz_mertebesi),
                "parametre": int(self.parametre_adedi),
                "genlik_parametresi": int(self.d),
                "faz_parametresi": int(self.d),
                "tahsis_edilen_seviye": int(self._bas),
                "müşterek_taşınıyor": False,
                "defter": len(self._yer),
                "veri_seviyesi": int(self.d_veri),
                "yığın": int(self.yigin),
                "müşterek_bayt": int(tek * self.d),
                "ölçülen_bellek": (0 if self.bellek is None
                                   else int(self.bellek)),
                "pay": float(self.ayar.pay),
                "yuva_bütçesi": int(round(math.log2(max(2, self.d))))}


def parametre_beyani(p: Optional[ParametreYazmaci]) -> Dict[str, Any]:
    if p is None:
        return {"seviye": 0, "parametre": 0, "müşterek_bayt": 0,
                "ölçülen_bellek": 0, "tahsis_edilen_seviye": 0,
                "defter": 0, "hüküm": "PARAMETRE YAZMACI KURULMADI"}
    return p.beyan()


def parametre_metni(b: Optional[Dict[str, Any]] = None) -> str:
    d = dict(b or parametre_beyani(None))
    if "hüküm" in d:
        return "  PARAMETRE YAZMACI: %s" % d["hüküm"]
    bos = int(d["seviye"]) - int(d["tahsis_edilen_seviye"])
    return "\n".join([
        "  PARAMETRE YAZMACI (ferman 2-R: parametre de quditir)",
        "    seviye        : %d   (yuva bütçesi %d)"
        % (d["seviye"], d["yuva_bütçesi"]),
        "    QUDİT SAYISI  : %d   (%d kübit)   ← SEVİYE DEĞİL QUDİT."
        % (d.get("qudit", 0), d.get("kübit", 0)),
        "    Yoğun genlik vektöründe seviye = 64^qudit'tir; 4096 seviye"
        " İKİ qudittir, 4096 qudit değil.",
        "    parametre     : %d   = %d genlik + %d faz üssü (Z_%d)"
        % (d["parametre"], d["genlik_parametresi"], d["faz_parametresi"],
           d["faz_mertebesi"]),
        "    tahsis edilen : %d seviye / %d defter kaydı   (boş %d)"
        % (d["tahsis_edilen_seviye"], d["defter"], bos),
        "    müşterek durum: %.1f MB   = yığın %d × veri seviyesi %d"
        "  × parametre seviyesi %d × 16 bayt   ← TAŞINMIYOR, kestirim"
        % (d["müşterek_bayt"] / 1e6, d["yığın"], d["veri_seviyesi"],
           d["seviye"]),
        "    ölçülen bellek: %.1f MB   pay %.2f   (ferman 2-S: hudut"
        " ölçülür, bütçe oraya kadar açılır)"
        % (d["ölçülen_bellek"] / 1e6, d["pay"]),
        "    GENLİK KANADI NORMALİZEDİR (Σ|p|² = 1): parametreler norm"
        " üzerinden birbirine bağlıdır,",
        "    bu yazmaç olmanın şartıdır ve gizlenmez (ferman 2-R).",
    ])
