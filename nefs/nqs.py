from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

import numpy as np

__all__ = ["NqsAyari", "ChebyshevKan", "chebyshev_t", "chebyshev_u",
           "gcl_dugumleri", "fct_katsayilari", "askin_beyani",
           "nqs_beyani", "nqs_metni",
           "TurGenligi", "turun_genligi", "tur_beyani", "tur_metni"]


@dataclass
class NqsAyari:

    dugum: int = 64
    derece: int = 12
    tohum: int = 0
    havuz_bayti: int = 4
    havuz_haddi: int = 1 << 20


_ASKIN = {"cos": 0, "arccos": 0, "sin": 0, "exp": 0}


def askin_beyani() -> Dict[str, int]:
    return dict(_ASKIN)


def chebyshev_t(u: np.ndarray, derece: int) -> np.ndarray:
    aci = np.arccos(np.clip(np.asarray(u, float), -1.0, 1.0))
    _ASKIN["arccos"] += 1
    j = np.arange(int(derece) + 1, dtype=float)
    _ASKIN["cos"] += 1
    return np.cos(j.reshape((-1,) + (1,) * aci.ndim) * aci[None, ...])


def chebyshev_u(u: np.ndarray, derece: int) -> np.ndarray:
    aci = np.arccos(np.clip(np.asarray(u, float), -1.0, 1.0))
    _ASKIN["arccos"] += 1
    j = np.arange(int(derece) + 1, dtype=float)
    pay = np.sin((j.reshape((-1,) + (1,) * aci.ndim) + 1.0)
                 * aci[None, ...])
    payda = np.sin(aci)[None, ...]
    _ASKIN["sin"] += 2
    tekil = np.abs(payda) < 1e-12
    bol = np.divide(pay, np.where(tekil, 1.0, payda))
    sinir = (j.reshape((-1,) + (1,) * aci.ndim) + 1.0) * np.where(
        np.cos(aci)[None, ...] >= 0.0, 1.0,
        (-1.0) ** j.reshape((-1,) + (1,) * aci.ndim))
    _ASKIN["cos"] += 1
    return np.where(tekil, sinir, bol)


def gcl_dugumleri(kac: int) -> np.ndarray:
    n = max(2, int(kac))
    j = np.arange(n, dtype=float)
    return np.cos(math.pi * j / (n - 1))


def fct_katsayilari(deger: np.ndarray, derece: int) -> np.ndarray:
    y = np.asarray(deger, float).reshape(-1)
    n = y.size
    u = gcl_dugumleri(n)
    T = chebyshev_t(u, int(derece))
    w = np.full(n, 2.0)
    w[0] = w[-1] = 1.0
    pay = (T * (y * w)[None, :]).sum(axis=1)
    payda = (T * T * w[None, :]).sum(axis=1)
    return pay / np.maximum(payda, 1e-300)


class ChebyshevKan:

    def __init__(self, taban: int, qudit: int,
                 ayar: Optional[NqsAyari] = None) -> None:
        self.ayar = ayar or NqsAyari()
        self.taban = max(2, int(taban))
        self.qudit = max(int(qudit), int(self.ayar.havuz_haddi))
        K = int(self.ayar.dugum)
        D = int(self.ayar.derece)
        r = np.random.default_rng(int(self.ayar.tohum))
        self.C = r.normal(scale=1.0 / math.sqrt(D + 1), size=(K, D + 1))
        self.S = r.normal(scale=1.0 / math.sqrt(D + 1), size=(K, D + 1))
        self.havuz_koordinat = r.normal(scale=1.0, size=self.qudit)
        assert self.havuz_koordinat.size == self.qudit, (
            "tohum havuzu qudit sayısınca olmalı (ferman 2-T)")
        self.havuz_fazi = r.uniform(-1.0, 1.0, size=K)
        self._son_z = 1.0
        self._cagri = 0
        self._asikin = 0

    @property
    def katsayi_adedi(self) -> int:
        return int(self.C.size + self.S.size)

    @property
    def parametre_adedi(self) -> int:
        return int(self.katsayi_adedi + self.havuz_koordinat.size
                   + self.havuz_fazi.size)

    def havuzu_buyut(self, n: int) -> None:
        n = int(n)
        if n <= self.havuz_koordinat.size:
            return
        r = np.random.default_rng(int(self.ayar.tohum) + 1)
        ek = r.normal(scale=1.0, size=n - self.havuz_koordinat.size)
        self.havuz_koordinat = np.concatenate([self.havuz_koordinat, ek])
        self.qudit = int(self.havuz_koordinat.size)

    def _vecih(self, basamak: np.ndarray) -> np.ndarray:
        b = np.asarray(basamak, np.int64)
        x = 2.0 * (b.astype(float) / float(self.taban - 1)) - 1.0
        n = x.shape[-1]
        self.havuzu_buyut(n)
        c = self.havuz_koordinat[:n]
        iz = (x * c[None, :]).sum(axis=-1) / float(n)
        u = iz[..., None] + self.havuz_fazi[None, :]
        return np.clip(u, -1.0, 1.0)

    def genlik(self, basamak: np.ndarray, parametre=None,
               yerel_faz=None) -> np.ndarray:
        u = self._vecih(basamak)
        D = int(self.ayar.derece)
        T = chebyshev_t(u, D)
        U = chebyshev_u(u, D)
        reel = np.einsum("kj,jnk->n", self.C, T, optimize=True)
        sanal = np.einsum("kj,jnk->n", self.S, U, optimize=True)
        if parametre is not None:
            k = parametre.kenet(basamak)
            reel = reel - np.asarray(k["enerji"], float).reshape(-1)
            sanal = sanal + np.asarray(k["faz"], float).reshape(-1)
        if yerel_faz is not None:
            y = np.asarray(yerel_faz, float).reshape(-1)
            assert y.size == sanal.size, (
                "mahallî yazmacın fazı konfigürasyon sayısınca olmalı: "
                "%d ≠ %d (ferman 2-Ş)" % (y.size, sanal.size))
            sanal = sanal + y
        reel = reel - float(reel.max())
        self._cagri += 1
        self._asikin += 2
        psi = np.exp(reel + 1j * sanal)
        _ASKIN["exp"] += 2
        z = float(np.linalg.norm(psi))
        self._son_z = z
        assert z > 0.0 and np.isfinite(z), (
            "NQS genliği tamamen söndü (Z=%r): kapalı form bir durum "
            "üretemedi, sessizce geçilemez (ferman 5)" % (z,))
        return psi / z

    def vektor(self) -> np.ndarray:
        return np.concatenate([self.C.reshape(-1), self.S.reshape(-1),
                               self.havuz_koordinat, self.havuz_fazi])

    def yukle(self, v: np.ndarray) -> None:
        v = np.asarray(v, float).reshape(-1)
        assert v.size == self.parametre_adedi, (
            "NQS parametre vektörü katsayı+havuz ebadında olmalı: "
            "%d ≠ %d" % (v.size, self.parametre_adedi))
        n1 = self.C.size
        n2 = n1 + self.S.size
        n3 = n2 + self.havuz_koordinat.size
        self.C = v[:n1].reshape(self.C.shape).copy()
        self.S = v[n1:n2].reshape(self.S.shape).copy()
        self.havuz_koordinat = v[n2:n3].copy()
        self.havuz_fazi = v[n3:].copy()

    def hazineye(self) -> Dict[str, np.ndarray]:
        return {"nqs.C": self.C.copy(), "nqs.S": self.S.copy(),
                "nqs.havuz_koordinat": self.havuz_koordinat.copy(),
                "nqs.havuz_fazı": self.havuz_fazi.copy()}

    def hazineden(self, agirlik) -> bool:
        if not agirlik:
            return False
        C = agirlik.get("nqs.C")
        S = agirlik.get("nqs.S")
        k = agirlik.get("nqs.havuz_koordinat")
        f = agirlik.get("nqs.havuz_fazı")
        if C is None or S is None or k is None or f is None:
            return False
        C = np.asarray(C, float)
        S = np.asarray(S, float)
        if C.shape != self.C.shape or S.shape != self.S.shape:
            return False
        self.C, self.S = C.copy(), S.copy()
        self.havuz_koordinat = np.asarray(k, float).reshape(-1).copy()
        self.havuz_fazi = np.asarray(f, float).reshape(-1).copy()
        return True

    def beyan(self) -> Dict[str, Any]:
        kat_bayt = self.katsayi_adedi * 8
        havuz_bayt = self.qudit * int(self.ayar.havuz_bayti)
        return {"düğüm": int(self.ayar.dugum),
                "derece": int(self.ayar.derece),
                "katsayı": int(self.katsayi_adedi),
                "katsayı_bayt": int(kat_bayt),
                "qudit": int(self.qudit),
                "havuz_bayt": int(havuz_bayt),
                "parametre": int(self.parametre_adedi),
                "çağrı": int(self._cagri),
                "aşkın_çağrı": int(self._asikin),
                "son_Z": float(self._son_z),
                "aşkın_döküm": askin_beyani(),
                "taban": int(self.taban)}


_TUR: Dict[str, float] = {
    "tur": 0.0, "kan_çağrısı": 0.0, "öbek": 0.0, "konfigürasyon": 0.0,
    "kenetsiz": 0.0, "mahallîsiz": 0.0, "saniye": 0.0, "açık": 1.0}


@dataclass
class TurGenligi:

    hal: np.ndarray
    lif: Tuple[int, ...]
    yazmac: Any = None

    @property
    def yigin(self) -> np.ndarray:
        return np.asarray(self.hal, complex).reshape(1, -1)

    def sektor_araliklari(self):
        y = self.yazmac
        assert y is not None, (
            "sektör aralıkları yazmaçtan okunur; ikinci bir cetvel "
            "kurulmaz (ferman 1-M, 2-İ)")
        return [y.sektor(ad) for ad, _ in y.ayar.kulli_alanlar]


def _konfigurasyon_basamaklari(lif: Tuple[int, ...], bas: int,
                               son: int) -> np.ndarray:
    k = np.arange(int(bas), int(son), dtype=np.int64)
    out = np.empty((k.size, len(lif)), np.int64)
    kalan = k
    for i in range(len(lif) - 1, -1, -1):
        n = int(lif[i])
        out[:, i] = kalan % n
        kalan = kalan // n
    return out


def _mahalli_faz(mahalli, bas: int, son: int) -> Optional[np.ndarray]:
    if mahalli is None:
        _TUR["mahallîsiz"] += 1.0
        return None
    kuresel = float(mahalli.kuresel_faz())
    f = np.asarray(mahalli.faz, float)
    if f.ndim == 2:
        f = f[0]
    n = int(son) - int(bas)
    out = np.full(n, kuresel, float)
    ust = min(int(son), int(f.size))
    if ust > int(bas):
        out[:ust - int(bas)] += f[int(bas):ust]
    return out


def _obek_haddi(kan: ChebyshevKan, d: int) -> int:
    from .donanim import bellek_haddi
    bayt = bellek_haddi()
    K = int(kan.ayar.dugum)
    D = int(kan.ayar.derece) + 1
    tek = 2 * K * D * 8 + 64
    assert bayt is None or int(bayt) > 0, (
        "öbek haddi ölçülen bellekten türer; yoklanamayan bellekten "
        "sayı uydurulmaz (ferman 5-B, 1-J)")
    if bayt is None:
        return int(d)
    return int(max(1, min(int(d), (int(bayt) // 8) // max(1, tek))))


def turun_genligi(nefs, q=None) -> TurGenligi:
    import time as _t
    t0 = _t.perf_counter()
    kan = getattr(nefs, "kan", None)
    assert kan is not None, (
        "TURUN GENLİĞİ KAN'DAN GELİR (ferman 2-T): ``nefs.kan`` yok. "
        "Genlik açık dizi olarak saklanmaz, fonksiyondan üretilir.")
    y = getattr(q, "y", None) if q is not None else getattr(nefs, "y", None)
    assert y is not None, (
        "turun genliği yazmacın lif yapısını ister -- yazmaç yok")
    lif = tuple(int(x) for x in y.ayar.lif)
    d = int(np.prod(lif))
    assert int(kan.taban) >= max(lif), (
        "KAN tabanı lifin en büyük basamağını taşımalı: taban %d, lif %r "
        "(ferman 1-M: tek kaynak yazmaçtır)" % (int(kan.taban), lif))
    pq = getattr(nefs, "pq", None)
    if pq is not None and not hasattr(pq, "kenet"):
        raise AssertionError(
            "parametre yazmacında ``kenet`` yok -- kenetlenme sessizce "
            "atlanamaz (ferman 5, 2-R)")
    if pq is None:
        _TUR["kenetsiz"] += 1.0
    mahalli = getattr(nefs, "mahalli", None)
    obek = _obek_haddi(kan, d)
    parcalar = []
    bas = 0
    n_obek = 0
    while bas < d:
        son = min(d, bas + obek)
        basamak = _konfigurasyon_basamaklari(lif, bas, son)
        parcalar.append(kan.genlik(basamak, parametre=pq,
                                   yerel_faz=_mahalli_faz(mahalli, bas, son)))
        n_obek += 1
        bas = son
    psi = (parcalar[0] if n_obek == 1
           else np.concatenate(parcalar).astype(complex))
    nrm = float(np.linalg.norm(psi))
    assert nrm > 0.0, (
        "turun genliği tamamen söndü -- KAN bir durum üretemedi "
        "(ferman 5)")
    psi = psi / nrm
    _TUR["tur"] += 1.0
    _TUR["kan_çağrısı"] = 1.0
    _TUR["öbek"] = float(n_obek)
    _TUR["konfigürasyon"] = float(d)
    _TUR["saniye"] += _t.perf_counter() - t0
    return TurGenligi(hal=np.asarray(psi, complex), lif=lif, yazmac=y)


def tur_beyani() -> Dict[str, Any]:
    b = dict(_TUR)
    b["tur_başına_kan"] = int(b["kan_çağrısı"])
    return b


def tur_metni(b: Optional[Dict[str, Any]] = None) -> str:
    d = dict(b or tur_beyani())
    if not int(d.get("tur", 0)):
        return ("  TURUN GENLİĞİ: HİÇ ÜRETİLMEDİ -- kırmızı (ferman 2-A)")
    return "\n".join([
        "  TURUN GENLİĞİ -- KAN İLK VE SON DEFA (ferman 2-A, 2-T)",
        "    tur %d   TUR BAŞINA KAN ÇAĞRISI %d  (bir olmalı)"
        % (int(d["tur"]), int(d["tur_başına_kan"])),
        "    konfigürasyon %d   boru hattı öbeği %d   %.4f sn"
        % (int(d["konfigürasyon"]), int(d["öbek"]), float(d["saniye"])),
        "    Öbek ölçülen bellekten türer (ferman 5-B); genlik açık dizi",
        "    olarak SAKLANMAZ, turda bir kez üretilir ve bırakılır.",
        "    kenetsiz tur %d   mahallî fazsız tur %d  (ikisi de 0 olmalı)"
        % (int(d["kenetsiz"]), int(d["mahallîsiz"])),
    ])


def nqs_beyani(kan: Optional[ChebyshevKan]) -> Dict[str, Any]:
    if kan is None:
        return {"düğüm": 0, "derece": 0, "katsayı": 0, "qudit": 0,
                "parametre": 0, "katsayı_bayt": 0, "havuz_bayt": 0,
                "çağrı": 0, "aşkın_çağrı": 0, "son_Z": 0.0,
                "hüküm": "KAN-NQS KURULMADI"}
    return kan.beyan()


def nqs_metni(b: Optional[Dict[str, Any]] = None) -> str:
    d = dict(b or nqs_beyani(None))
    if "hüküm" in d:
        return "  KAN-NQS: %s" % d["hüküm"]
    return "\n".join([
        "  KAN-NQS GENLİĞİ (ferman 2-T: genlik açık dizi değil fonksiyon)",
        "    düğüm × derece : %d × %d   → %d katsayı   = %.1f KB"
        % (d["düğüm"], d["derece"], d["katsayı"],
           d["katsayı_bayt"] / 1e3),
        "    tohum havuzu   : %d qudit   = %.1f MB   (qudit başına 4 bayt)"
        % (d["qudit"], d["havuz_bayt"] / 1e6),
        "    parametre      : %d   (katsayı + havuz)" % d["parametre"],
        "    MERTEBE: genlik ÜRETİMİ O(1) -- katsayı adedi qudit"
        " sayısından bağımsızdır;",
        "    HAVUZ ise O(N)'dir. Toptan O(1) denmez (ferman 5).",
        "    T_j = cos(j·arccos u), U_j = sin((j+1)·arccos u)/sin(arccos u)",
        "    HAKİKÎ FONKSİYONLARIYLA hesaplanır; tekrarlama ikamesi"
        " YASAKTIR (ferman 2-U).",
        "    Aşkın çağrı dökümü: %s   (yasak kalktı, muhasebe kalkmadı)"
        % (d.get("aşkın_döküm", {}),),
        "    son Z (normalize edilen küme üstünde) : %.6e" % d["son_Z"],
        "    AÇIK DİZİ YOKTUR: q^N genlik hiçbir yerde tutulmaz.",
    ])
