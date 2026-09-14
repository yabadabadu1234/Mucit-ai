from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

__all__ = ["ParametreAyari", "ParametreYazmaci", "qudit_haddi", "kapasite_basamagi",
           "parametre_beyani", "parametre_metni"]


@dataclass
class ParametreAyari:

    faz_mertebesi: int = 16
    tohum: int = 0
    pay: float = 0.25
    qudit: int = 1 << 20
    qudit_bayti: int = 16


def qudit_haddi(bellek: Optional[int], pay: float = 0.25,
                qudit_bayti: int = 16) -> int:
    assert bellek is not None and int(bellek) > 0, (
        "qudit haddi ölçülen bellekten türer; bellek yoklanamadıysa "
        "bütçe uydurulmaz (ferman 5-B, 2-S)")
    return max(1, int((float(bellek) * float(pay))
                      // float(int(qudit_bayti))))


def kapasite_basamagi(taban: int, qudit: int) -> float:
    return float(qudit) * math.log10(max(2, int(taban)))


class ParametreYazmaci:

    def __init__(self, taban: int, yigin: int, bellek: Optional[int],
                 ayar: Optional[ParametreAyari] = None) -> None:
        self.ayar = ayar or ParametreAyari()
        self.taban = max(2, int(taban) if int(taban) >= 2 else 64)
        self.yigin = max(1, int(yigin))
        self.bellek = None if bellek is None else int(bellek)
        self.hadd = qudit_haddi(self.bellek, float(self.ayar.pay),
                                int(self.ayar.qudit_bayti))
        self.d = min(int(self.ayar.qudit), int(self.hadd))
        assert self.d >= 1, (
            "parametre yazmacına tek qudit bile sığmadı: ölçülen bellek "
            "%r, pay %.2f (ferman 2-S)" % (self.bellek, self.ayar.pay))
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
    def qudit(self) -> int:
        return int(self.d)

    @property
    def mahalli_serbestlik(self) -> int:
        return 2 * int(self.d)

    @property
    def kapasite_basamak(self) -> float:
        return kapasite_basamagi(self.taban, self.d)

    @property
    def genislik(self) -> int:
        return 1

    def __len__(self) -> int:
        return int(self.mahalli_serbestlik)

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
        return {"qudit": int(self.d),
                "taban": int(self.taban),
                "kapasite_basamağı": float(self.kapasite_basamak),
                "mahallî_serbestlik": int(self.mahalli_serbestlik),
                "faz_mertebesi": int(self.ayar.faz_mertebesi),
                "tahsis_edilen_qudit": int(self._bas),
                "defter": len(self._yer),
                "yığın": int(self.yigin),
                "qudit_bayt": int(self.d * int(self.ayar.qudit_bayti)),
                "qudit_haddi": int(self.hadd),
                "ölçülen_bellek": (0 if self.bellek is None
                                   else int(self.bellek)),
                "pay": float(self.ayar.pay)}


def parametre_beyani(p: Optional[ParametreYazmaci]) -> Dict[str, Any]:
    if p is None:
        return {"qudit": 0, "taban": 0, "kapasite_basamağı": 0.0,
                "mahallî_serbestlik": 0, "ölçülen_bellek": 0,
                "tahsis_edilen_qudit": 0, "qudit_haddi": 0,
                "defter": 0, "hüküm": "PARAMETRE YAZMACI KURULMADI"}
    return p.beyan()


def parametre_metni(b: Optional[Dict[str, Any]] = None) -> str:
    d = dict(b or parametre_beyani(None))
    if "hüküm" in d:
        return "  PARAMETRE YAZMACI: %s" % d["hüküm"]
    bos = int(d["qudit"]) - int(d["tahsis_edilen_qudit"])
    return "\n".join([
        "  PARAMETRE YAZMACI (ferman 2-R: parametre de quditir)",
        "    qudit × taban      : %d × %d" % (d["qudit"], d["taban"]),
        "    TAŞIMA KAPASİTESİ  : %d^%d   = 10^%.0f   (%.0f basamaklı)"
        % (d["taban"], d["qudit"], d["kapasite_basamağı"],
           d["kapasite_basamağı"]),
        "    ← KAPASİTE taban^qudit'tir. 'iki kere qudit sayısı' DEĞİL;",
        "      o yalnız MAHALLÎ serbestliktir ve aşağıda ayrı yazar.",
        "    mahallî serbestlik : %d   = %d genlik + %d faz üssü (Z_%d)"
        % (d["mahallî_serbestlik"], d["qudit"], d["qudit"],
           d["faz_mertebesi"]),
        "    tahsis edilen      : %d qudit / %d defter kaydı   (boş %d)"
        % (d["tahsis_edilen_qudit"], d["defter"], bos),
        "    mahallî bellek     : %.1f MB   (qudit başına 16 bayt)"
        % (d["qudit_bayt"] / 1e6),
        "    ölçülen bellek     : %.1f MB   pay %.2f   → qudit haddi %d"
        % (d["ölçülen_bellek"] / 1e6, d["pay"], d["qudit_haddi"]),
        "    q^N HİÇBİR YERDE AÇILMAZ: bellekte q^N sayı tutulmaz,",
        "    genlik fonksiyondan üretilir (ferman 2-T).",
        "    GENLİK KANADI NORMALİZEDİR (Σ|p|² = 1): mahallî genlikler",
        "    norm üzerinden bağlıdır; yazmaç olmanın şartıdır.",
    ])
