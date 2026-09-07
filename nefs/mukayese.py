from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["Vecih", "VECIHLER", "vecih_kur", "uyanik_vecihler",
           "bargmann", "hipotez_halkasi", "swap_testi", "simplisiyal", "istisna_yeri",
           "choi", "nesnelestir", "spektrum", "hata_payi",
           "zorunlu", "mumkun", "kiplik", "paylar_olc",
           "mukayese_beyani", "mukayese_metni", "sayac"]

_SAYAC: Dict[str, int] = {"bargmann": 0, "swap": 0, "spektrum": 0,
                          "hata_payı": 0, "nesne": 0, "choi": 0}


def sayac() -> Dict[str, int]:
    return dict(_SAYAC)


@dataclass(frozen=True)
class Vecih:

    ad: str
    izdusum: Optional[Callable[[np.ndarray], np.ndarray]] = None
    agirlik: float = 1.0

    def gor(self, x: np.ndarray) -> np.ndarray:
        v = np.asarray(x, complex).reshape(-1)
        if self.izdusum is None:
            return v
        u = np.asarray(self.izdusum(v), complex).reshape(-1)
        return u


def _dilim(bas: int, son: int) -> Callable[[np.ndarray], np.ndarray]:
    def _f(v: np.ndarray) -> np.ndarray:
        w = np.zeros_like(v)
        w[bas:son] = v[bas:son]
        return w
    return _f


def _genlik(v: np.ndarray) -> np.ndarray:
    return np.abs(v).astype(complex)


def _faz(v: np.ndarray) -> np.ndarray:
    n = np.abs(v)
    return np.where(n > 1e-300, v / np.maximum(n, 1e-300), 0.0)


def _fark(v: np.ndarray) -> np.ndarray:
    return np.diff(v, prepend=v[:1])


VECIHLER: Tuple[Vecih, ...] = (
    Vecih("zât", None),
    Vecih("şiddet", _genlik),
    Vecih("cihet", _faz),
    Vecih("değişim", _fark),
)


def vecih_kur(sektorler: Sequence[Tuple[str, Tuple[int, int]]]
              ) -> Tuple[Vecih, ...]:
    out: List[Vecih] = list(VECIHLER)
    for ad, (i, j) in sektorler:
        if int(j) > int(i):
            out.append(Vecih("alan.%s" % ad, _dilim(int(i), int(j))))
    return tuple(out)


def _normalize(V: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(V, axis=-1, keepdims=True)
    return V / np.maximum(n, 1e-300)


def uyanik_vecihler(durumlar: Sequence[np.ndarray],
                    vecihler: Optional[Sequence[Vecih]] = None,
                    taban: float = 0.0) -> List[Vecih]:
    D = [np.asarray(x, complex).reshape(-1) for x in durumlar]
    assert D, "mukayese için en az bir durum lâzım"
    vs = list(vecihler if vecihler is not None else VECIHLER)
    eps = float(np.finfo(np.asarray(D[0]).dtype).eps
                if np.iscomplexobj(D[0]) else np.finfo(float).eps)
    had = float(taban) if float(taban) > 0.0 else math.sqrt(eps)
    canli: List[Vecih] = []
    for v in vs:
        M = _normalize(np.stack([v.gor(x) for x in D]))
        if not np.all(np.isfinite(M)):
            continue
        G = M @ M.conj().T
        w = np.linalg.eigvalsh(0.5 * (G + G.conj().T)).real
        rank = int(np.count_nonzero(w > had * max(1.0, float(w.max()))))
        if rank >= 2:
            canli.append(v)
    return canli


def bargmann(durumlar: Sequence[np.ndarray],
             vecih: Optional[Vecih] = None) -> Dict[str, Any]:
    _SAYAC["bargmann"] += 1
    v = vecih or VECIHLER[0]
    D = [v.gor(x) for x in durumlar]
    n = len(D)
    assert n >= 2, "mukayese en az iki kutup ister"
    M = _normalize(np.stack(D))
    carpim = complex(1.0)
    baglar: List[float] = []
    for k in range(n):
        c = complex(np.vdot(M[k], M[(k + 1) % n]))
        baglar.append(float(abs(c)))
        carpim *= c
    r = float(abs(carpim))
    fi = float(np.angle(carpim)) if r > 0.0 else 0.0
    return {"vecih": v.ad, "n": int(n), "Δ": carpim, "r": r, "Φ": fi,
            "bağ": baglar, "kopuk": bool(min(baglar) <= 1e-12),
            "tenakuz": bool(r > 0.0 and abs(abs(fi) - math.pi) < 0.5),
            "kısır": bool(r > 0.0 and abs(fi) < 1e-9)}


def hipotez_halkasi(haller: Sequence[np.ndarray],
                    cinsler: Optional[Sequence[str]] = None,
                    vecih: Optional[Vecih] = None) -> Dict[str, Any]:
    H = [np.asarray(h, complex).reshape(-1) for h in haller]
    ad = ([str(c) for c in cinsler] if cinsler is not None
          else ["hepsi"] * len(H))
    assert len(ad) == len(H), (
        "hipotez sayısı %d, cins sayısı %d -- hâl ile cins ayrışmış"
        % (len(H), len(ad)))
    grup: Dict[str, List[int]] = {}
    for i, c in enumerate(ad):
        grup.setdefault(c, []).append(i)
    dokum: Dict[str, Any] = {}
    toplam = 0.0
    halka = ten = kis = kop = 0
    for c, idx in sorted(grup.items()):
        if len(idx) < 3:
            continue
        b = bargmann([H[i] for i in idx], vecih)
        d = (float(1.0 - float(b["r"])) + float(bool(b["tenakuz"]))
             + float(bool(b["kısır"])) + float(bool(b["kopuk"])))
        dokum[c] = {"hipotez": len(idx), "r": float(b["r"]),
                    "Φ": float(b["Φ"]), "tenakuz": bool(b["tenakuz"]),
                    "kısır": bool(b["kısır"]), "kopuk": bool(b["kopuk"]),
                    "Δ_K": float(d)}
        toplam += d
        halka += 1
        ten += int(bool(b["tenakuz"]))
        kis += int(bool(b["kısır"]))
        kop += int(bool(b["kopuk"]))
    return {"Δ_K": (toplam / halka) if halka else 0.0, "halka": int(halka),
            "tenakuz": int(ten), "kısır": int(kis), "kopuk": int(kop),
            "grup": dokum}


def swap_testi(a: np.ndarray, b: np.ndarray,
               vecih: Optional[Vecih] = None) -> Dict[str, Any]:
    _SAYAC["swap"] += 1
    v = vecih or VECIHLER[0]
    M = _normalize(np.stack([v.gor(a), v.gor(b)]))
    c = complex(np.vdot(M[0], M[1]))
    ortusme = float(abs(c) ** 2)
    return {"vecih": v.ad, "örtüşme": ortusme,
            "fark": float(0.5 * (1.0 - ortusme)),
            "faz": float(np.angle(c)) if abs(c) > 0.0 else 0.0,
            "ayniyet": bool(ortusme >= 1.0 - 1e-9),
            "dik": bool(ortusme <= 1e-12)}


def simplisiyal(durumlar: Sequence[np.ndarray],
                vecih: Optional[Vecih] = None) -> Dict[str, Any]:
    v = vecih or VECIHLER[0]
    D = [v.gor(x) for x in durumlar]
    n = len(D)
    assert n >= 3, "simplisiyal ayrışım en az üç kutup ister"
    M = _normalize(np.stack(D))
    ucgen: List[Dict[str, Any]] = []
    toplam = 0.0
    for k in range(1, n - 1):
        c = (complex(np.vdot(M[0], M[k]))
             * complex(np.vdot(M[k], M[k + 1]))
             * complex(np.vdot(M[k + 1], M[0])))
        f = float(np.angle(c)) if abs(c) > 0.0 else 0.0
        toplam += f
        ucgen.append({"köşe": (0, k, k + 1), "r": float(abs(c)), "Φ": f})
    kalan = float((toplam + math.pi) % (2.0 * math.pi) - math.pi)
    return {"vecih": v.ad, "üçgen": ucgen, "Φ_toplam": kalan,
            "üçgen_sayısı": len(ucgen)}


def istisna_yeri(durumlar: Sequence[np.ndarray],
                 vecih: Optional[Vecih] = None) -> Dict[str, Any]:
    s = simplisiyal(durumlar, vecih)
    ucgen = s["üçgen"]
    if not ucgen:
        return {"vecih": s["vecih"], "istisna": None, "sapma": 0.0}
    sapma = [abs(float(u["Φ"])) for u in ucgen]
    i = int(np.argmax(sapma))
    ort = float(np.median(sapma))
    return {"vecih": s["vecih"], "üçgen": ucgen,
            "istisna": int(ucgen[i]["köşe"][1]),
            "sapma": float(sapma[i]), "ortanca_sapma": ort,
            "yırtık": bool(sapma[i] > 3.0 * max(ort, 1e-12))}


def choi(kanal: np.ndarray) -> Dict[str, Any]:
    _SAYAC["choi"] += 1
    E = np.asarray(kanal, complex)
    assert E.ndim == 2 and E.shape[0] == E.shape[1], (
        "Choi için kare bir kanal dizeyi lâzım")
    d = int(E.shape[0])
    v = E.reshape(-1) / math.sqrt(d)
    rho = np.outer(v, v.conj())
    iz = float(np.real(np.trace(rho)))
    return {"ρ": rho, "d": d, "iz": iz,
            "saflık": float(np.real(np.trace(rho @ rho)))}


def nesnelestir(netice: Dict[str, Any], boy: int) -> np.ndarray:
    _SAYAC["nesne"] += 1
    boy = max(2, int(boy))
    v = np.zeros(boy, complex)
    r = float(netice.get("r", 0.0))
    fi = float(netice.get("Φ", 0.0))
    baglar = [float(x) for x in (netice.get("bağ") or [r])]
    for i, b in enumerate(baglar[:boy]):
        v[i] = b * np.exp(1j * fi * (i + 1) / max(1, len(baglar)))
    if not np.any(np.abs(v) > 0.0):
        v[0] = 1.0
    return v / np.linalg.norm(v)


def spektrum(Y: Sequence[np.ndarray],
             vecihler: Optional[Sequence[Vecih]] = None,
             azami_n: int = 0, tohum: int = 0) -> Dict[str, Any]:
    _SAYAC["spektrum"] += 1
    D = [np.asarray(x, complex).reshape(-1) for x in Y]
    m = len(D)
    assert m >= 2, "spektrum en az iki kutup ister"
    canli = uyanik_vecihler(D, vecihler)
    ust = int(azami_n) if int(azami_n) >= 2 else m
    ust = int(min(ust, m))
    r = np.random.default_rng(int(tohum))
    halkalar: List[Dict[str, Any]] = []
    for v in canli:
        for n in range(2, ust + 1):
            idx = (list(range(n)) if n == m
                   else [int(i) for i in r.choice(m, size=n, replace=False)])
            o = bargmann([D[i] for i in idx], v)
            o["indis"] = idx
            if o["kopuk"]:
                continue
            halkalar.append(o)
    return {"vecih": [v.ad for v in canli],
            "uyanık_vecih": len(canli), "aday_vecih": len(
                list(vecihler if vecihler is not None else VECIHLER)),
            "halka": halkalar, "halka_sayısı": len(halkalar),
            "tenakuz": sum(1 for h in halkalar if h["tenakuz"]),
            "kısır": sum(1 for h in halkalar if h["kısır"]),
            "en_kuvvetli": (max(halkalar, key=lambda h: h["r"])
                            if halkalar else None)}


def hata_payi(adlar: Sequence[str], artik: Sequence[float]
              ) -> Dict[str, Any]:
    _SAYAC["hata_payı"] += 1
    a = np.asarray(list(artik), float).reshape(-1)
    assert a.size == len(adlar), (
        "hata vektörü %d, ad %d -- bileşen kayboldu" % (a.size, len(adlar)))
    top = float(np.abs(a).sum())
    if top <= 0.0:
        return {"pay": {}, "açı": {}, "toplam": 0.0, "hâkim": None,
                "hâkim_payı": 0.0}
    birim = a / top
    kutup = np.zeros_like(a)
    kutup[int(np.argmax(np.abs(a)))] = 1.0
    aci: Dict[str, float] = {}
    pay: Dict[str, float] = {}
    for i, ad in enumerate(adlar):
        pay[str(ad)] = float(birim[i])
        e = np.zeros_like(a)
        e[i] = 1.0
        s = swap_testi(a.astype(complex), e.astype(complex))
        aci[str(ad)] = float(math.acos(
            float(np.clip(math.sqrt(max(s["örtüşme"], 0.0)), -1.0, 1.0))))
    h = int(np.argmax(np.abs(a)))
    return {"pay": pay, "açı": aci, "toplam": top,
            "hâkim": str(adlar[h]), "hâkim_payı": float(abs(birim[h])),
            "dağılım": float(-np.sum(
                np.abs(birim)[np.abs(birim) > 0]
                * np.log(np.abs(birim)[np.abs(birim) > 0])))}


def zorunlu(onerme: np.ndarray, sahitler: Sequence[np.ndarray],
            vecihler: Optional[Sequence[Vecih]] = None) -> Dict[str, Any]:
    return kiplik(onerme, sahitler, vecihler)["zorunlu"]


def mumkun(onerme: np.ndarray, sahitler: Sequence[np.ndarray],
           vecihler: Optional[Sequence[Vecih]] = None) -> Dict[str, Any]:
    return kiplik(onerme, sahitler, vecihler)["mümkün"]


def kiplik(onerme: np.ndarray, sahitler: Sequence[np.ndarray],
           vecihler: Optional[Sequence[Vecih]] = None) -> Dict[str, Any]:
    _SAYAC["kiplik"] = _SAYAC.get("kiplik", 0) + 1
    S = [np.asarray(x, complex).reshape(-1) for x in sahitler]
    assert S, "kiplik için en az bir şahit dünya lâzım"
    canli = uyanik_vecihler(S + [np.asarray(onerme, complex).reshape(-1)],
                            vecihler)
    dunya: Dict[str, float] = {}
    for v in canli:
        en = 0.0
        for w in S:
            en = max(en, float(swap_testi(onerme, w, v)["örtüşme"]))
        dunya[v.ad] = en
    if not dunya:
        return {"dünya": {}, "zorunlu": {"doğru": False, "nispet": 0.0},
                "mümkün": {"doğru": False, "nispet": 0.0},
                "erişilen": 0}
    d = np.asarray(list(dunya.values()), float)
    eps = math.sqrt(float(np.finfo(float).eps))
    tutan = d > eps
    return {"dünya": dunya, "erişilen": int(len(dunya)),
            "zorunlu": {"doğru": bool(np.all(tutan)),
                        "nispet": float(d.min())},
            "mümkün": {"doğru": bool(np.any(tutan)),
                       "nispet": float(d.max())}}


def paylar_olc(adlar: Sequence[str], artik: Sequence[float]
               ) -> Dict[str, float]:
    _SAYAC["pay"] = _SAYAC.get("pay", 0) + 1
    a = np.asarray(list(artik), float).reshape(-1)
    n = a.size
    assert n == len(adlar), "pay ölçüsü: ad ile artık sayısı tutmuyor"
    if n < 3 or not np.any(np.abs(a) > 0.0):
        return {str(ad): 1.0 / max(n, 1) for ad in adlar}
    E = np.eye(n, dtype=complex)
    v = a.astype(complex)
    rez = np.zeros(n, float)
    for i in range(n):
        halka = [v, E[i], v - complex(np.vdot(E[i], v)) * E[i]]
        if float(np.linalg.norm(halka[2])) <= 1e-300:
            continue
        o = bargmann(halka)
        rez[i] = float(o["r"])
    top = float(rez.sum())
    if top <= 0.0:
        return {str(ad): 1.0 / n for ad in adlar}
    return {str(adlar[i]): float(rez[i] / top) for i in range(n)}


def mukayese_beyani(spek: Optional[Dict[str, Any]] = None,
                    hata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return {"sayaç": sayac(), "spektrum": spek, "hata": hata}


def mukayese_metni(o: Dict[str, Any]) -> str:
    s = ["  MUKAYESE MOTORU (nefs/mukayese.py) -- çok vazifeli uzuv"]
    c = o.get("sayaç") or {}
    s.append("    çağrı: " + "  ".join("%s %d" % (k, v)
                                       for k, v in sorted(c.items())))
    sp = o.get("spektrum")
    if sp:
        s += ["    VECİH SPEKTRUMU (mertebe = hangi vecihten bakıldığı):",
              "      uyanık vecih : %d / %d   (%s)"
              % (sp["uyanık_vecih"], sp["aday_vecih"],
                 ", ".join(sp["vecih"]) or "yok"),
              "      halka        : %d   tenakuz %d   kısır %d"
              % (sp["halka_sayısı"], sp["tenakuz"], sp["kısır"])]
        e = sp.get("en_kuvvetli")
        if e:
            s.append("      en kuvvetli  : %s  n=%d  r=%.4f  Φ=%+.4f"
                     % (e["vecih"], e["n"], e["r"], e["Φ"]))
    h = o.get("hata")
    if h and h.get("pay"):
        ust = sorted(h["pay"].items(), key=lambda x: -abs(x[1]))[:5]
        s += ["    HATA PAYI VE AÇISI (ferman 1-V'nin vektörü üstünde):",
              "      hâkim bileşen: %s  (%%%.2f)"
              % (h["hâkim"], 100.0 * h["hâkim_payı"]),
              "      dağılım (entropi): %.4f  -- 0'a yakın = tek kefe "
              "her şeyi yiyor" % h.get("dağılım", 0.0),
              "      " + "  ".join("%s %%%.1f∠%.2f"
                                   % (k, 100.0 * v, h["açı"].get(k, 0.0))
                                   for k, v in ust)]
    return "\n".join(s)
