from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

__all__ = ["ParametreAyari", "ParametreYazmaci", "qudit_haddi",
           "parametre_beyani", "parametre_metni",
           "kenet_beyani", "kenet_metni"]


_KENET: Dict[str, float] = {"çağrı": 0.0, "kapısız_çağrı": 0.0,
                            "kapı": 0.0, "seyirci": 0.0,
                            "enerji": 0.0, "faz": 0.0,
                            "gerilim": 0.0, "gerilim_tepesi": 0.0,
                            "ayrı_rezonans": 0.0, "açık": 1.0}


def kenet_beyani() -> Dict[str, float]:
    b = dict(_KENET)
    b["kapı_başına_enerji"] = (b["enerji"] / b["kapı"]) if b["kapı"] else 0.0
    b["seyirci_nispeti"] = ((b["seyirci"] / (b["seyirci"] + b["kapı"]))
                            if (b["seyirci"] + b["kapı"]) else 0.0)
    return b


def kenet_metni(b: Optional[Dict[str, float]] = None) -> str:
    d = dict(b or kenet_beyani())
    return "\n".join([
        "  ÇİFT YAZMAÇ KENETLENMESİ (ferman 2-V: seyirci qudit)",
        "    kenetleme çağrısı  : %d   kapısız %d   (açık: %s)"
        % (int(d["çağrı"]), int(d["kapısız_çağrı"]),
           "evet" if d["açık"] else "HAYIR -- kırmızı"),
        "    temas eden kapı    : %d   seyirci qudit %d   (%.4f seyirci)"
        % (int(d["kapı"]), int(d["seyirci"]), d["seyirci_nispeti"]),
        "    etkileşim enerjisi : %.6e   (kapı başına %.6e)"
        % (d["enerji"], d["kapı_başına_enerji"]),
        "    eklenen sürekli faz: %.6e   rad   (Z_m DEĞİL, U(1))"
        % d["faz"],
        "    REZONANS EŞLEMESİ (ferman 2-Z: bağlam basamağı lağvedildi)",
        "      ölçülen gerilim ortalaması %.6e   tepesi %.6e"
        % (d["gerilim"], d["gerilim_tepesi"]),
        "      kapıların kilitlendiği ayrı rezonans noktası: %d"
        % int(d["ayrı_rezonans"]),
        "      hedef elle yazılmadı: veri manifoldunun kendi geriliminin",
        "      tepesidir; her kodlamada yeniden tayin edilir.",
        "    Parametre veriyi matrisle ezmez: köşegen kontrollü faz",
        "    üsse skaler girer, yığın ekseni açılmaz (yığın boyu 1).",
    ])


@dataclass
class ParametreAyari:

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
        r = np.random.default_rng(int(self.ayar.tohum))
        self.genlik = np.abs(r.normal(scale=1.0, size=self.d))
        self.genlik = self.genlik / max(float(np.linalg.norm(self.genlik)),
                                        1e-300)
        self.faz = r.uniform(-math.pi, math.pi, size=self.d)
        self._yer: Dict[str, Tuple[int, int]] = {}
        self._bas = 0

    @property
    def qudit(self) -> int:
        return int(self.d)

    @property
    def mahalli_serbestlik(self) -> int:
        return 2 * int(self.d)

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
        return 1.0

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
        return float(olcek) * self.faz[self.adres(anahtar, n)]

    def temas_kapilari(self) -> Tuple[np.ndarray, np.ndarray]:
        if not self._yer:
            return (np.zeros(0, np.int64), np.zeros(0, float))
        kontrol = np.concatenate(
            [bas + np.arange(int(kac), dtype=np.int64)
             for (bas, kac) in self._yer.values()])
        return kontrol, self.genlik[kontrol]

    @staticmethod
    def gerilim(koordinat: np.ndarray) -> np.ndarray:
        k = np.asarray(koordinat, float)
        ileri = np.abs(np.diff(k, axis=-1, append=k[..., -1:]))
        geri = np.abs(np.diff(k, axis=-1, prepend=k[..., :1]))
        return ileri + geri

    def rezonans(self, koordinat: np.ndarray, kac: int) -> np.ndarray:
        k = np.asarray(koordinat, float)
        n = int(k.shape[-1])
        g = self.gerilim(k)
        sira = np.argsort(-g, axis=-1)
        return sira[..., np.arange(int(kac)) % n]

    def kenet(self, basamak: np.ndarray) -> Dict[str, np.ndarray]:
        b = np.asarray(basamak, np.int64)
        n = int(b.shape[-1])
        kontrol, bag = self.temas_kapilari()
        if kontrol.size == 0 or not _KENET["açık"]:
            sifir = np.zeros(b.shape[:-1], float)
            _KENET["çağrı"] += 1.0
            if kontrol.size == 0:
                _KENET["kapısız_çağrı"] += 1.0
            return {"enerji": sifir, "faz": sifir}
        w = 2.0 * (b.astype(float) / float(max(1, self.taban - 1))) - 1.0
        duz = w.reshape(-1, n)
        gerilim = self.gerilim(duz)
        hedef = self.rezonans(duz, int(kontrol.size))
        w_t = np.take_along_axis(duz, hedef, axis=-1)
        teta = self.faz[kontrol]
        enerji = (-(w_t * (bag * teta)).sum(axis=-1)).reshape(b.shape[:-1])
        faz = ((w_t * teta).sum(axis=-1)).reshape(b.shape[:-1])
        _KENET["çağrı"] += 1.0
        _KENET["kapı"] = float(kontrol.size)
        _KENET["seyirci"] = float(max(0, self.d - kontrol.size))
        _KENET["enerji"] = float(np.mean(np.abs(enerji)))
        _KENET["faz"] = float(np.mean(np.abs(faz)))
        _KENET["gerilim"] = float(np.mean(gerilim))
        _KENET["gerilim_tepesi"] = float(np.max(gerilim))
        _KENET["ayrı_rezonans"] = float(np.unique(hedef).size)
        return {"enerji": np.asarray(enerji, float),
                "faz": np.asarray(faz, float)}

    def defter(self) -> Dict[str, Tuple[int, int]]:
        return dict(self._yer)

    def vektor(self) -> np.ndarray:
        return np.concatenate([self.genlik, self.faz])

    def yukle(self, v: np.ndarray) -> None:
        v = np.asarray(v, float).reshape(-1)
        assert v.size == 2 * self.d, (
            "parametre vektörü yazmaç ebadında olmalı: %d ≠ 2·%d"
            % (v.size, self.d))
        g = np.abs(v[:self.d])
        self.genlik = g / max(float(np.linalg.norm(g)), 1e-300)
        self.faz = np.remainder(v[self.d:] + math.pi,
                                2.0 * math.pi) - math.pi

    def hazineye(self) -> Dict[str, np.ndarray]:
        return {"parametre.genlik": self.genlik.copy(),
                "parametre.faz": self.faz.copy()}

    def hazineden(self, agirlik) -> bool:
        g = None if agirlik is None else agirlik.get("parametre.genlik")
        f = None if agirlik is None else agirlik.get("parametre.faz")
        if g is None or f is None:
            return False
        g = np.asarray(g, float).reshape(-1)
        f = np.asarray(f, float).reshape(-1)
        if g.size != self.d or f.size != self.d:
            return False
        self.genlik = g / max(float(np.linalg.norm(g)), 1e-300)
        self.faz = np.remainder(f + math.pi, 2.0 * math.pi) - math.pi
        return True

    def beyan(self) -> Dict[str, Any]:
        return {"qudit": int(self.d),
                "taban": int(self.taban),
                "mahallî_serbestlik": int(self.mahalli_serbestlik),
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
        return {"qudit": 0, "taban": 0,
                "mahallî_serbestlik": 0, "ölçülen_bellek": 0,
                "tahsis_edilen_qudit": 0, "qudit_haddi": 0,
                "defter": 0, "hüküm": "PARAMETRE YAZMACI KURULMADI"}
    return p.beyan()


def parametre_metni(b: Optional[Dict[str, Any]] = None) -> str:
    d = dict(b or parametre_beyani(None))
    if "hüküm" in d:
        return "  PARAMETRE YAZMACI: %s" % d["hüküm"]
    return "\n".join([
        "  PARAMETRE YAZMACI  %d qudit × taban %d   (kapasite %d^%d)"
        % (d["qudit"], d["taban"], d["taban"], d["qudit"]),
        "    mahallî serbestlik %d   tahsis %d qudit / %d kayıt"
        % (d["mahallî_serbestlik"], d["tahsis_edilen_qudit"],
           d["defter"]),
        "    mahallî bellek %.1f MB   ölçülen bellek %.1f MB   hadd %d"
        % (d["qudit_bayt"] / 1e6, d["ölçülen_bellek"] / 1e6,
           d["qudit_haddi"]),
    ])
