from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Tuple

import numpy as np

__all__ = ["Kayit", "Hafiza", "TASDIK", "TEVAKKUF", "CERH", "rapor"]

TASDIK = 1.0
TEVAKKUF = 0.5
CERH = 0.0

_SONUM_PAYI: Dict[float, float] = {TASDIK: 0.25, TEVAKKUF: 1.0, CERH: 0.10}


@dataclass
class Kayit:

    x: np.ndarray
    omega: float
    hukum: float
    mu: float
    dogum: int = 0
    yaprak: str = ""

    def __post_init__(self) -> None:
        self.x = np.asarray(self.x).reshape(-1)
        nrm = float(np.linalg.norm(self.x))
        assert nrm > 0.0, "BOŞ kavram hafızaya nakşedilemez"
        self.x = self.x / nrm
        assert self.hukum in (TASDIK, TEVAKKUF, CERH), (
            "hüküm damgası üçünden biri olmalı: %r" % (self.hukum,))
        assert -1.0000001 <= self.omega <= 1.0000001, (
            "holonomi izi [−1,1] dışında: %r" % (self.omega,))


class Hafiza:

    def __init__(self, kapasite: int = 256, yazma: float = 0.05,
                 sonum: float = 0.02, zeno_esigi: float = 0.35,
                 zeno_tepe: float = 0.9, ayniyet: float = 0.98,
                 buhar: float = 1e-4, mu_asgari: float = 1e-3,
                 tohum: int = 0) -> None:
        assert int(kapasite) >= 1, "hafıza kapasitesi en az 1 olmalı"
        assert 0.0 < float(yazma) <= 1.0, "yazma oranı (0,1] olmalı"
        assert 0.0 <= float(sonum) < 1.0, "sönüm [0,1) olmalı"
        self.kapasite = int(kapasite)
        self.yazma = float(yazma)
        self.sonum = float(sonum)
        self.zeno_esigi = float(zeno_esigi)
        self.zeno_tepe = float(zeno_tepe)
        self.ayniyet = float(ayniyet)
        self.buhar = float(buhar)
        self.mu_asgari = float(mu_asgari)
        assert 0.0 < self.zeno_tepe <= 1.0, "zeno tepe nispeti (0,1]"
        assert 0.0 < self.ayniyet <= 1.0, "ayniyet eşiği (0,1]"
        self.tohum = int(tohum)
        self.kayitlar: List[Kayit] = []
        self.budama = 0
        self.tertip = 0
        self.adim = 0

    def klon(self) -> "Hafiza":
        import copy
        y = copy.copy(self)
        y.kayitlar = [copy.copy(k) for k in self.kayitlar]
        return y

    def yaz(self, x, omega: float, hukum: float) -> Kayit:
        self.adim += 1
        e = self.yazma
        for k in self.kayitlar:
            k.mu *= (1.0 - e)
        y = Kayit(x=x, omega=float(omega), hukum=float(hukum), mu=e,
                  dogum=self.adim)
        for k in self.kayitlar:
            if (k.hukum == y.hukum
                    and abs(complex(np.vdot(k.x, y.x))) > self.ayniyet):
                k.mu += y.mu
                return k
        self.kayitlar.append(y)
        self._tasfiye()
        return y

    def _tasfiye(self) -> None:
        if self.sonum > 0.0:
            for k in self.kayitlar:
                k.mu *= (1.0 - self.sonum * _SONUM_PAYI[k.hukum])
        self.kayitlar = [k for k in self.kayitlar if k.mu > self.buhar]
        if len(self.kayitlar) > self.kapasite:
            self.kayitlar.sort(key=lambda k: k.mu, reverse=True)
            self.kayitlar = self.kayitlar[:self.kapasite]
        assert len(self.kayitlar) <= self.kapasite

    def oku(self, x) -> Dict[str, float]:
        v = np.asarray(x).reshape(-1)
        nrm = float(np.linalg.norm(v))
        assert nrm > 0.0, "boş durumla hafıza okunamaz"
        v = v / nrm
        out = {"tasdik": 0.0, "tevakkuf": 0.0, "cerh": 0.0, "toplam": 0.0}
        ad = {TASDIK: "tasdik", TEVAKKUF: "tevakkuf", CERH: "cerh"}
        for k in self.kayitlar:
            if k.x.size != v.size:
                continue
            ort = float(abs(np.vdot(k.x, v)) ** 2) * k.mu
            out[ad[k.hukum]] += ort
            out["toplam"] += ort
        return out

    def taban_degistir(self, x, yaprak: str, omega: float = 0.0
                       ) -> Dict[str, Any]:
        from .mukayese import swap_testi
        v = np.asarray(x).reshape(-1)
        nrm = float(np.linalg.norm(v))
        assert nrm > 0.0, "boş durumla taban değiştirilemez"
        v = v / nrm
        tasinan = 0
        for k in self.kayitlar:
            if k.x.size != v.size:
                continue
            s = swap_testi(k.x.astype(complex), v.astype(complex))
            if float(s["örtüşme"]) < self.zeno_esigi:
                continue
            eski = k.yaprak
            k.yaprak = (eski + "|" + str(yaprak)) if eski else str(yaprak)
            k.omega = float(omega) if omega else k.omega
            tasinan += 1
        self.tertip += 1
        return {"yaprak": str(yaprak), "taşınan": int(tasinan),
                "tertip": int(self.tertip), "silinen": 0}

    def zeno(self, x) -> Optional[np.ndarray]:
        v = np.asarray(x, float).reshape(-1)
        nrm = float(np.linalg.norm(v))
        if nrm <= 0.0:
            return None
        v = v / nrm
        maske = np.ones(v.size, bool)
        vuran = False
        for k in self.kayitlar:
            if k.hukum != CERH or k.x.size != v.size:
                continue
            ort = float(abs(np.vdot(k.x, v)) ** 2)
            if ort < self.zeno_esigi or k.mu < self.mu_asgari:
                continue
            g = np.abs(np.asarray(k.x)).astype(float)
            maske &= ~(g >= g.max() * self.zeno_tepe)
            vuran = True
        if not vuran or maske.all():
            return None
        self.budama += int(np.count_nonzero(~maske))
        return maske

    def beyan(self) -> Dict[str, Any]:
        say = {TASDIK: 0, TEVAKKUF: 0, CERH: 0}
        for k in self.kayitlar:
            say[k.hukum] += 1
        return {"kayıt": len(self.kayitlar), "tasdik": say[TASDIK],
                "tevakkuf": say[TEVAKKUF], "cerh": say[CERH],
                "budama": int(self.budama), "adım": int(self.adim),
                "tertip": int(self.tertip),
                "yapraklı": sum(1 for k in self.kayitlar if k.yaprak),
                "kütle": float(sum(k.mu for k in self.kayitlar))}

    def hazineye(self) -> Dict[str, np.ndarray]:
        if not self.kayitlar:
            return {}
        m = max(k.x.size for k in self.kayitlar)
        X = np.zeros((len(self.kayitlar), m), complex)
        for i, k in enumerate(self.kayitlar):
            X[i, :k.x.size] = k.x
        return {
            "hafıza.x": X,
            "hafıza.omega": np.array([k.omega for k in self.kayitlar], float),
            "hafıza.hüküm": np.array([k.hukum for k in self.kayitlar], float),
            "hafıza.mu": np.array([k.mu for k in self.kayitlar], float),
            "hafıza.doğum": np.array([k.dogum for k in self.kayitlar],
                                     np.int64)}

    @classmethod
    def hazineden(cls, agirlik: Mapping[str, Any],
                  ust_veri: Optional[Mapping[str, Any]] = None) -> "Hafiza":
        u = dict(ust_veri or {})
        h = cls(kapasite=int(float(u.get("hafıza_kapasitesi", 256))),
                yazma=float(u.get("hafıza_yazma", 0.05)),
                sonum=float(u.get("hafıza_sönümü", 0.02)),
                zeno_esigi=float(u.get("zeno_eşiği", 0.35)),
                zeno_tepe=float(u.get("zeno_tepe", 0.9)))
        if "hafıza.x" not in agirlik:
            return h
        X = np.asarray(agirlik["hafıza.x"])
        om = np.asarray(agirlik["hafıza.omega"], float).reshape(-1)
        hk = np.asarray(agirlik["hafıza.hüküm"], float).reshape(-1)
        mu = np.asarray(agirlik["hafıza.mu"], float).reshape(-1)
        dg = np.asarray(agirlik.get(
            "hafıza.doğum", np.zeros(om.size)), np.int64).reshape(-1)
        assert X.shape[0] == om.size == hk.size == mu.size, (
            "hafıza tensörlerinin boyları tutmuyor")
        for i in range(X.shape[0]):
            h.kayitlar.append(Kayit(x=X[i], omega=float(om[i]),
                                    hukum=float(hk[i]), mu=float(mu[i]),
                                    dogum=int(dg[i])))
        h.adim = int(dg.max()) if dg.size else 0
        return h


def rapor(tohum: int = 0) -> str:
    r = np.random.default_rng(int(tohum))
    m = 16
    h = Hafiza(kapasite=64, yazma=0.2, sonum=0.02)

    safsata = np.zeros(m)
    safsata[3] = 1.0
    safsata[7] = 0.95
    h.yaz(safsata, omega=-1.0, hukum=CERH)
    mesru = np.zeros(m)
    mesru[1] = 1.0
    h.yaz(mesru, omega=0.2, hukum=TASDIK)

    P = np.full(m, 1.0 / m)
    P[3] = 0.5
    P[7] = 0.4
    P = P / P.sum()
    mask = h.zeno(np.sqrt(P))
    kesik = 0 if mask is None else int(np.count_nonzero(~mask))

    Q = np.full(m, 1.0 / m)
    Q[11] = 0.6
    Q = Q / Q.sum()
    mask2 = h.zeno(np.sqrt(Q))
    kesik2 = 0 if mask2 is None else int(np.count_nonzero(~mask2))

    k = h.oku(np.sqrt(P))
    zan = np.zeros(m)
    zan[5] = 1.0
    h.yaz(zan, omega=1.0, hukum=TEVAKKUF)
    mu0 = [x.mu for x in h.kayitlar if x.hukum == TEVAKKUF][0]
    for _ in range(50):
        h._tasfiye()
    kalan = [x.mu for x in h.kayitlar if x.hukum == TEVAKKUF]
    mu1 = kalan[0] if kalan else 0.0

    return "\n".join([
        "=== KUANTUM ASOSİYATİF HAFIZA (ρ) ===", "",
        "  kayıt : %r" % (h.beyan(),), "",
        "  ZENO BUDAMASI",
        "    cerhedilmiş yola girildi : %d belirteç kesildi  %s"
        % (kesik, "ÇALIŞTI" if kesik > 0 else "⚠ HİÇ KESMEDİ"),
        "    alâkasız yola girildi    : %d belirteç kesildi  %s"
        % (kesik2, "doğru (kesmemeli)" if kesik2 == 0
           else "⚠ KÖR KESİYOR"),
        "",
        "  ASOSİYATİF ÇAĞRIŞIM (𝒦 = Tr ρ|ψ⟩⟨ψ|)",
        "    cerh=%.4f  tasdik=%.4f  tevakkuf=%.4f"
        % (k["cerh"], k["tasdik"], k["tevakkuf"]),
        "",
        "  LIOUVILLE SÖNÜMÜ (delilsiz zan buharlaşır)",
        "    tevakkuf μ: %.6f → %.6f  (50 tasfiye sonra)" % (mu0, mu1),
    ])
