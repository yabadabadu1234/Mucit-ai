from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from matematik.sonsuz_mertebeler_teorisi import (
    TURETIM_SERBESTLIKLERI, buzulme_selalesi, topos_turetimi,
    turetim_beyani)

__all__ = ["HendeseAyari", "gecis_dizeyi", "karsilikli_haber",
           "gromov_delta", "mertebe_sec", "dikey_asansor",
           "hendese_teshisi", "hendese_beyani", "hendese_yukle",
           "hendese_sifirla", "opetopik_kompleks", "hodge_ayrisimi",
           "kan_boynuzu", "izdusum_demeti", "kaide_imzasi"]


_SAYI: Dict[str, int] = {}


_NISPET: Dict[str, float] = {}


_ASKIN: Dict[str, int] = {}


def hendese_sifirla() -> None:
    _SAYI.clear()
    _SAYI.update({"çağrı": 0, "dag_mertebesi": -1, "eğrilik": 0,
                  "asansör_katı": 0, "kafes": 0, "boynuz": 0,
                  "dolu_boynuz": 0, "tıkanma": 0, "dörtlü": 0,
                  "üçgen_ihlâli": 0, "yönlü_kenar": 0,
                  "simetrik_kenar": 0, "şelale_uzay": 0,
                  "şelale_kategori": 0, "şelale_operad": 0,
                  "0-hücre": 0, "1-hücre": 0, "2-hücre": 0, "3-hücre": 0})
    _NISPET.clear()
    _NISPET.update({"δ": 0.0, "haber": 0.0, "sapma": 0.0, "denklik": 0.0,
                    "üçgen_nispeti": 0.0,
                    "𝒮_simetrik": 0.0, "𝒜_yönlü": 0.0, "Ω_yırtık": 0.0,
                    "morfizm": 0.0, "yüksek": 0.0, "arite": 0.0,
                    "yön₁": 0.0, "yön₂": 0.0, "koherans": 0.0,
                    "koherans_evvel": 0.0, "kapanma_nispeti": 0.0,
                    "büzülme": 0.0, "tayf_entropisi": 0.0})
    _ASKIN.clear()
    _ASKIN.update({"log": 0, "exp": 0, "eigh": 0})


hendese_sifirla()


@dataclass
class HendeseAyari:
    azami_alfabe: int = 256
    dortlu_ornek: int = 64
    tohum: int = 0


def _kucuk() -> float:
    return float(np.finfo(float).tiny)


def gecis_dizeyi(w: Sequence[int], n: int) -> np.ndarray:
    y = np.asarray(list(w), np.int64).reshape(-1) % int(n)
    if y.size < 2:
        return np.zeros((int(n), int(n)), float)
    T = np.zeros((int(n), int(n)), float)
    np.add.at(T, (y[:-1], y[1:]), 1.0)
    sat = T.sum(axis=1, keepdims=True)
    return T / np.maximum(sat, 1.0)


def karsilikli_haber(w: Sequence[int], n: int) -> Dict[str, float]:
    y = np.asarray(list(w), np.int64).reshape(-1) % int(n)
    if y.size < 2:
        return {"haber": 0.0, "şart_sapması": 0.0, "haber_haddi": 0.0}
    ortak = np.zeros((int(n), int(n)), float)
    np.add.at(ortak, (y[:-1], y[1:]), 1.0)
    top = max(float(ortak.sum()), 1.0)
    P = ortak / top
    Pi = P.sum(axis=1, keepdims=True)
    Pj = P.sum(axis=0, keepdims=True)
    kucuk = _kucuk()
    sec = P > 0.0
    payda = np.maximum(Pi * Pj, kucuk)
    haber = float(np.sum(P[sec] * np.log(P[sec] / payda[sec])))
    sart = P / np.maximum(Pi, kucuk)
    dolu = np.asarray(Pi).reshape(-1) > 0.0
    sapma = (float(np.mean(np.var(sart[dolu], axis=1)))
             if bool(dolu.any()) else 0.0)
    dolu_n = max(1, int(np.count_nonzero(dolu)))
    return {"haber": haber, "şart_sapması": sapma,
            "haber_haddi": float(np.log(float(dolu_n)))}


def _mesafe(w: Sequence[int], n: int) -> np.ndarray:
    T = gecis_dizeyi(w, n)
    S = T + T.T
    var = S > 0.0
    en_az = float(S[var].min()) if bool(var.any()) else 1.0
    ic = -np.log(np.where(var, S, en_az)) + np.where(var, 0.0, 1.0)
    np.fill_diagonal(ic, 0.0)
    D = ic.copy()
    for k in range(int(n)):
        D = np.minimum(D, D[:, k:k + 1] + D[k:k + 1, :])
    return D


def _dortlular(n: int, kac: int) -> np.ndarray:
    m = int(n)
    assert m >= 4, "Gromov dörtlüsü için en az dört harf lâzım"
    cikan: List[Tuple[int, int, int, int]] = []
    for i in range(m):
        for a in (1, 2, 3):
            j, k, l = (i + a) % m, (i + 2 * a) % m, (i + 3 * a) % m
            if len({i, j, k, l}) == 4:
                cikan.append((i, j, k, l))
            if len(cikan) >= int(kac):
                return np.asarray(cikan, np.int64)
    assert cikan, "determinist dörtlü taraması boş döndü"
    return np.asarray(cikan, np.int64)


def gromov_delta(w: Sequence[int], ayar: Optional[HendeseAyari] = None
                 ) -> Dict[str, float]:
    a = ayar or HendeseAyari()
    y = np.asarray(list(w), np.int64).reshape(-1)
    n = int(min(int(a.azami_alfabe), max(2, int(y.max()) + 1)))
    if n < 4:
        _NISPET["δ"] = 0.0
        _NISPET["üçgen_nispeti"] = 0.0
        _SAYI["üçgen_ihlâli"] = 0
        _SAYI["dörtlü"] = 0
        return {"δ": 0.0, "üçgen_ihlâli": 0.0, "dörtlü": 0, "alfabe": n}
    D = _mesafe(y, n)
    Q = _dortlular(n, int(a.dortlu_ornek))
    i, j, k, l = Q[:, 0], Q[:, 1], Q[:, 2], Q[:, 3]
    s1 = D[i, j] + D[k, l]
    s2 = D[i, k] + D[j, l]
    s3 = D[i, l] + D[j, k]
    en_buyuk = float(np.max(np.abs(s1 - np.maximum(s2, s3))))
    ihlal = int(np.count_nonzero(D[i, k] > D[i, j] + D[j, k]))
    nispet = float(ihlal) / float(Q.shape[0])
    _NISPET["δ"] = en_buyuk
    _NISPET["üçgen_nispeti"] = nispet
    _SAYI["üçgen_ihlâli"] = int(ihlal)
    _SAYI["dörtlü"] = int(Q.shape[0])
    return {"δ": en_buyuk, "üçgen_ihlâli": nispet,
            "dörtlü": int(Q.shape[0]), "alfabe": n}


def opetopik_kompleks(w: Sequence[int], n: int) -> Dict[str, Any]:
    y = np.asarray(list(w), np.int64).reshape(-1) % int(n)
    assert y.size >= 1, "opetopik kompleks için dizi BOŞ olamaz"
    m = int(n)
    sifir = np.unique(y)
    bos = {"0-hücre": int(sifir.size), "1-hücre": 0, "2-hücre": 0,
           "3-hücre": 0, "kenar": np.zeros((m, m), bool),
           "agac": np.zeros((0, 3), np.int64), "mertebe": 0,
           "morfizm": 0.0, "yüksek": 0.0, "arite": 0.0}
    if y.size < 2:
        return bos
    kenar = np.zeros((m, m), bool)
    kenar[y[:-1], y[1:]] = True
    bir = int(np.count_nonzero(kenar))
    agac = (np.unique(np.stack([y[:-2], y[1:-1], y[2:]], axis=1), axis=0)
            if y.size >= 3 else np.zeros((0, 3), np.int64))
    iki = int(agac.shape[0])
    if agac.shape[0] >= 2:
        uc = int(np.unique(np.concatenate([agac[:-1], agac[1:]], axis=1),
                           axis=0).shape[0])
    else:
        uc = 0
    dolu = int(sifir.size)
    morfizm = float(bir) / float(max(1, dolu * dolu))
    yuksek = float(iki) / float(max(1, bir * dolu))
    if iki:
        girdi = float(np.mean(np.unique(agac[:, 2], return_counts=True)[1]))
        cikti = float(np.mean(np.unique(agac[:, :2], axis=0,
                                        return_counts=True)[1]))
    else:
        girdi = cikti = 1.0
    arite = 1.0 - 1.0 / float(max(1.0, girdi * cikti))
    mertebe = 3 if uc else (2 if iki else (1 if bir else 0))
    return {"0-hücre": dolu, "1-hücre": bir, "2-hücre": iki, "3-hücre": uc,
            "kenar": kenar, "agac": agac, "mertebe": int(mertebe),
            "morfizm": float(min(1.0, morfizm)),
            "yüksek": float(min(1.0, yuksek)),
            "arite": float(min(1.0, max(0.0, arite)))}


def hodge_ayrisimi(M: np.ndarray) -> Dict[str, Any]:
    A = np.asarray(M, float)
    sim = 0.5 * (A + A.T)
    ters = 0.5 * (A - A.T)
    s = float(np.sum(sim * sim))
    t = float(np.sum(ters * ters))
    top = s + t
    if top <= 0.0:
        return {"𝒮_simetrik": 0.0, "𝒜_yönlü": 0.0, "kuvvet": 0.0,
                "Π_uzay": sim, "Π_kategori": ters}
    return {"𝒮_simetrik": s / top, "𝒜_yönlü": t / top, "kuvvet": top,
            "Π_uzay": sim, "Π_kategori": ters}


def kan_boynuzu(kenar: np.ndarray) -> Dict[str, Any]:
    E = np.asarray(kenar, bool)
    n = int(E.shape[0])
    bos: List[Tuple[int, int, int]] = []
    dolu = 0
    toplam = 0
    a_i, b_i = np.nonzero(E)
    for a, b in zip(a_i.tolist(), b_i.tolist()):
        for c in np.nonzero(E[b])[0].tolist():
            if c == a:
                continue
            toplam += 1
            if bool(E[a, c]):
                dolu += 1
            else:
                bos.append((int(a), int(b), int(c)))
    if toplam == 0:
        return {"koherans": 0.0, "Ω_yırtık": 0.0, "boynuz": 0,
                "dolu": 0, "boş": [], "mertebe": -1}
    k = float(dolu) / float(toplam)
    return {"koherans": k, "Ω_yırtık": 1.0 - k, "boynuz": int(toplam),
            "dolu": int(dolu), "boş": bos,
            "mertebe": (2 if k > 0.0 else 1)}


def _dag_mertebesi(kenar: np.ndarray) -> int:
    E = np.asarray(kenar, bool)
    kuvvet = E.copy()
    for k in range(1, int(E.shape[0]) + 1):
        if not bool(kuvvet.any()):
            return k
        kuvvet = (kuvvet.astype(np.int64) @ E.astype(np.int64)) > 0
    return -1


def izdusum_demeti(hodge: Dict[str, Any], agac: np.ndarray,
                   n: int) -> Dict[str, np.ndarray]:
    O = np.zeros((int(n), int(n)), float)
    if int(agac.shape[0]):
        np.add.at(O, (agac[:, 0], agac[:, 2]), 1.0)
        np.add.at(O, (agac[:, 1], agac[:, 2]), 1.0)
    return {"Π_uzay": np.asarray(hodge["Π_uzay"], float),
            "Π_kategori": np.asarray(hodge["Π_kategori"], float),
            "Π_operad": O}


def kaide_imzasi(teshis: Dict[str, Any], taban: int) -> str:
    n = int(taban)
    assert n >= 2, "kaide imzası için taban en az iki olmalı"
    k = teshis["koordinat"]
    basamak = [int(round(float(k[a]) * float(n - 1)))
               for a in TURETIM_SERBESTLIKLERI]
    om = teshis["Ω_cebiri"]
    cebir = {"boole": "B", "heyting": "H", "yönlü_kafes": "Y",
             "tayinsiz": "?"}[str(om["cebir"])]
    return ("K" + "-".join("%x" % x for x in basamak) + "/" + cebir
            + "%d" % int(bool(om.get("üçüncü_şık"))))


def mertebe_sec(w: Sequence[int], ayar: Optional[HendeseAyari] = None
                ) -> Dict[str, Any]:
    a = ayar or HendeseAyari()
    y = np.asarray(list(w), np.int64).reshape(-1)
    n = int(min(int(a.azami_alfabe), max(2, int(y.max()) + 1)))
    hb = karsilikli_haber(y, n)
    T = gecis_dizeyi(y, n)
    K = opetopik_kompleks(y, n)
    h1 = hodge_ayrisimi(T)
    agac = np.asarray(K["agac"], np.int64)
    if int(K["2-hücre"]) >= 2:
        kod = agac[:, 0] * n + agac[:, 1]
        _birim, ters = np.unique(kod, return_inverse=True)
        U = np.zeros((int(_birim.size), int(_birim.size)), float)
        np.add.at(U, (ters[:-1], ters[1:]), 1.0)
        h2 = hodge_ayrisimi(U)
    else:
        h2 = {"𝒮_simetrik": 0.0, "𝒜_yönlü": 0.0, "kuvvet": 0.0}
    E0 = np.asarray(K["kenar"], bool)
    cift = E0 & E0.T
    simetrik = int(np.count_nonzero(cift))
    yonlu = int(np.count_nonzero(E0)) - simetrik
    kan = kan_boynuzu(K["kenar"])
    selale = buzulme_selalesi(kan["boş"], K["kenar"].tolist(), agac.tolist())
    tamam = np.asarray(selale["tamamlanan_kenar"], bool)
    kan_sonra = kan_boynuzu(tamam)
    K["kenar"] = tamam
    olcum = {"morfizm": float(K["morfizm"]),
             "yüksek": float(K["yüksek"]),
             "arite": float(K["arite"]),
             "yön₁": float(h1["𝒜_yönlü"]),
             "yön₂": float(h2["𝒜_yönlü"]),
             "koherans": float(kan_sonra["koherans"]),
             "hücre_mertebesi": int(K["mertebe"]),
             "koherans_mertebesi": int(max(0, int(kan_sonra["mertebe"]))),
             "dolu_boynuz": int(kan_sonra["dolu"]),
             "boş_boynuz": int(selale["tıkanma"]),
             "yönlü_kenar": int(yonlu),
             "simetrik_kenar": int(simetrik),
             "şelale": selale}
    tur = topos_turetimi(olcum)
    yirtik = (float(selale["tıkanma"]) / float(kan["boynuz"])
              if int(kan["boynuz"]) else 0.0)
    hodge = np.asarray([h1["𝒮_simetrik"] * (1.0 - yirtik),
                        h1["𝒜_yönlü"] * (1.0 - yirtik), yirtik], float)
    hodge = hodge / max(float(hodge.sum()), _kucuk())
    gr = gromov_delta(y, a)
    egrilik = ("hiperbolik" if gr["δ"] > 0.0 and gr["üçgen_ihlâli"] < 0.5
               else ("düz" if gr["δ"] <= 0.0 else "pozitif"))
    _SAYI["çağrı"] += 1
    _SAYI["dag_mertebesi"] = int(_dag_mertebesi(K["kenar"]))
    _SAYI["eğrilik"] = int({"düz": 0, "hiperbolik": 1,
                            "pozitif": 2}[egrilik])
    _SAYI["kafes"] = int(len(tur["kafes"]))
    _SAYI["boynuz"] = int(kan["boynuz"])
    _SAYI["dolu_boynuz"] = int(kan_sonra["dolu"])
    _SAYI["tıkanma"] = int(selale["tıkanma"])
    _SAYI["şelale_uzay"] = int(selale["uzay"])
    _SAYI["şelale_kategori"] = int(selale["kategori"])
    _SAYI["şelale_operad"] = int(selale["operad"])
    _SAYI["yönlü_kenar"] = int(yonlu)
    _SAYI["simetrik_kenar"] = int(simetrik)
    for ad in ("0-hücre", "1-hücre", "2-hücre", "3-hücre"):
        _SAYI[ad] = int(K[ad])
    _NISPET["haber"] = float(hb["haber"])
    _NISPET["sapma"] = float(np.linalg.norm(T - T.T))
    _NISPET["𝒮_simetrik"] = float(hodge[0])
    _NISPET["𝒜_yönlü"] = float(hodge[1])
    _NISPET["Ω_yırtık"] = float(hodge[2])
    _NISPET["tayf_entropisi"] = float(tur["entropi"])
    _NISPET["koherans_evvel"] = float(kan["koherans"])
    _NISPET["kapanma_nispeti"] = float(selale["kapanma_nispeti"])
    _ASKIN["log"] += 2
    for ad in TURETIM_SERBESTLIKLERI:
        _NISPET[ad] = float(olcum[ad])
    return {"tayf": np.asarray(tur["tayf"], float),
            "kafes": tur["kafes"],
            "katman": tuple(d["ad"] for d in tur["kafes"]),
            "kısıtlama": tuple(int(d["kısıtlama"]) for d in tur["kafes"]),
            "koordinat": tur["koordinat"],
            "tavan": tur["tavan"],
            "hodge": {"𝒮_simetrik": float(hodge[0]),
                      "𝒜_yönlü": float(hodge[1]),
                      "Ω_yırtık": float(hodge[2])},
            "Π": izdusum_demeti(h1, agac, n),
            "Ω_cebiri": tur["Ω_cebiri"], "şelale": selale,
            "hücre": {k: int(K[k]) for k in
                      ("0-hücre", "1-hücre", "2-hücre", "3-hücre")},
            "boynuz": int(kan["boynuz"]), "dolu_boynuz": int(kan["dolu"]),
            "tayf_entropisi": float(tur["entropi"]),
            "tayf_haddi": float(tur["had"]),
            "haber": hb["haber"], "haber_haddi": hb["haber_haddi"],
            "şart_sapması": hb["şart_sapması"],
            "sapma": float(np.linalg.norm(T - T.T)),
            "dag_mertebesi": _dag_mertebesi(K["kenar"]),
            "δ_Gromov": gr["δ"], "üçgen_ihlâli": gr["üçgen_ihlâli"],
            "eğrilik": egrilik, "alfabe": n}


def dikey_asansor(teshis: Dict[str, Any], lif: Sequence[int]
                  ) -> Dict[str, Any]:
    lif = tuple(int(x) for x in lif)
    assert lif, "dikey asansör için lif yapısı BOŞ olamaz"
    ro = np.asarray(teshis["tayf"], float).reshape(-1)
    kis = np.asarray(teshis["kısıtlama"], float).reshape(-1)
    assert ro.size == kis.size and ro.size > 0, (
        "tayf %d, kısıtlama %d -- kafes ile ölçü aynı uzayda olmalı"
        % (ro.size, kis.size))
    kat_sayisi = len(lif)
    en_cok = float(len(TURETIM_SERBESTLIKLERI))
    yer = (en_cok - kis) / en_cok * float(kat_sayisi - 1)
    demet = np.zeros(kat_sayisi, float)
    alt = np.floor(yer).astype(np.int64)
    ust = np.minimum(alt + 1, kat_sayisi - 1)
    pay = yer - alt
    np.add.at(demet, alt, ro * (1.0 - pay))
    np.add.at(demet, ust, ro * pay)
    top = float(demet.sum())
    assert top > 0.0, "lif demeti tamamen söndü -- tayf lifle örtüşmüyor"
    demet = demet / top
    buzulme = float(np.sum(demet * np.arange(kat_sayisi, dtype=float)))
    kat = int(min(max(int(round(buzulme)), 0), kat_sayisi - 1))
    _SAYI["asansör_katı"] = int(kat)
    _NISPET["büzülme"] = float(buzulme)
    return {"kat": kat, "büzülme": buzulme, "demet": demet, "eksen": kat,
            "lif": lif, "taban_boyu": int(lif[kat]),
            "yukarı": tuple(lif[kat:]), "aşağı": tuple(lif[:kat + 1])}


def hendese_teshisi(baglamlar: Sequence[Sequence[int]], lif: Sequence[int],
                    ayar: Optional[HendeseAyari] = None) -> Dict[str, Any]:
    assert baglamlar, "hendese teşhisi için bağlam BOŞ olamaz"
    duz: List[int] = []
    for b in baglamlar:
        duz.extend(int(x) for x in np.asarray(list(b), np.int64).reshape(-1)
                   if int(x) >= 0)
    assert duz, "bağlamların hepsi boş -- teşhis edilecek dizi yok"
    m = mertebe_sec(duz, ayar)
    m["asansör"] = dikey_asansor(m, lif)
    m["basamak"] = len(duz)
    m["türetim_beyanı"] = turetim_beyani()
    return m


def hendese_beyani() -> Dict[str, Any]:
    b: Dict[str, Any] = {k: int(v) for k, v in _SAYI.items()}
    b.update({"aşkın_%s" % k: int(v) for k, v in _ASKIN.items()})
    b["aşkın_toplam"] = int(sum(_ASKIN.values()))
    b.update({k: float(v) for k, v in _NISPET.items()})
    b.update({"türetim_%s" % k: v for k, v in turetim_beyani().items()})
    return b


def hendese_yukle(d: Dict[str, Any]) -> None:
    for k, v in dict(d).items():
        a = str(k)
        if a.startswith("türetim_") or a.startswith("aşkın_"):
            continue
        if a in _SAYI:
            _SAYI[a] = int(v)
        elif a in _NISPET:
            _NISPET[a] = float(v)
