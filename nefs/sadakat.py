from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

import numpy as np

__all__ = ["SadakatAyari", "parite_maskesi", "parite_dizini",
           "tenakuz_alarmi", "mantiki_degil", "sadakat_uygula",
           "sadakat_beyani", "sadakat_sifirla"]


@dataclass
class SadakatAyari:

    acik: int = 1
    parite_lifi: int = 2
    lif_yapisi: Tuple[int, ...] = (16, 16, 16)

    def __post_init__(self) -> None:
        assert len(self.lif_yapisi) >= 1, "lif yapısı BOŞ olamaz"
        assert 0 <= int(self.parite_lifi) < len(self.lif_yapisi), (
            "parite lifi %d, lif yapısı %r -- aralık dışı"
            % (self.parite_lifi, self.lif_yapisi))


_SAYAC: Dict[str, float] = {"çağrı": 0.0, "yoklanan": 0.0, "alarm": 0.0,
                            "sıfırlanan": 0.0, "ağırlık": 0.0,
                            "artık": 0.0,
                            "kapalı_çağrı": 0.0}

_DIZIN: Dict[Tuple[int, int], np.ndarray] = {}


def parite_maskesi(ayar: Optional[SadakatAyari] = None) -> int:
    a = ayar or SadakatAyari()
    lif = tuple(int(x) for x in a.lif_yapisi)
    for n in lif:
        assert n >= 1 and (n & (n - 1)) == 0, (
            "lif boyu ikinin kuvveti olmalı (parite maskesi bit aralığıdır); "
            "verilen: %r" % (lif,))
    j = int(a.parite_lifi)
    kaydir = 1
    for n in lif[j + 1:]:
        kaydir *= n
    genislik = lif[j]
    return (genislik - 1) * kaydir if kaydir > 1 else (genislik - 1)


def parite_dizini(d: int, ayar: Optional[SadakatAyari] = None) -> np.ndarray:
    a = ayar or SadakatAyari()
    maske = parite_maskesi(a)
    anahtar = (int(d), int(maske))
    hazir = _DIZIN.get(anahtar)
    if hazir is not None:
        return hazir
    k = np.arange(int(d), dtype=np.int64)
    v = (k & np.int64(maske)).astype(np.uint64)
    say = np.zeros(v.shape, np.uint8)
    for _ in range(64):
        if not v.any():
            break
        say ^= (v & np.uint64(1)).astype(np.uint8)
        v >>= np.uint64(1)
    dizin = say.astype(bool)
    _DIZIN[anahtar] = dizin
    return dizin


def tenakuz_alarmi(psi: np.ndarray,
                   ayar: Optional[SadakatAyari] = None
                   ) -> Tuple[float, int]:
    P = np.asarray(psi)
    if P.ndim == 1:
        P = P.reshape(1, -1)
    d = P.shape[-1]
    dizin = parite_dizini(d, ayar)
    guc = np.abs(P) ** 2
    yirtik = guc[..., dizin].sum(axis=-1)
    toplam = guc.sum(axis=-1)
    nispet = float(np.sum(yirtik) / max(float(np.sum(toplam)), 1e-300))
    return nispet, int(np.count_nonzero(yirtik > 1e-30))


def sadakat_uygula(hedef: Any, ayar: Optional[SadakatAyari] = None
                   ) -> Dict[str, Any]:
    a = ayar or SadakatAyari()
    _SAYAC["çağrı"] += 1.0

    yazmac = None
    if isinstance(hedef, np.ndarray):
        psi = hedef
    elif isinstance(getattr(hedef, "genlik", None), np.ndarray) \
            and isinstance(getattr(hedef, "faz", None), np.ndarray):
        m = 16.0
        psi = (np.asarray(hedef.genlik, float)
               * np.exp(2j * math.pi * np.asarray(hedef.faz, float) / m))
        psi = psi.reshape(1, -1)
    else:
        y = getattr(hedef, "y", hedef)
        assert hasattr(y, "psi"), (
            "sadakat_uygula: hedefin genliği bulunamadı (%r)" % type(hedef))
        yazmac = y
        psi = np.asarray(y.psi)

    P = psi if psi.ndim == 2 else psi.reshape(1, -1)
    d = P.shape[-1]
    dizin = parite_dizini(d, a)
    _SAYAC["yoklanan"] += float(int(np.count_nonzero(dizin)))

    once, satir = tenakuz_alarmi(P, a)
    _SAYAC["ağırlık"] += once
    if once > 1e-12:
        _SAYAC["alarm"] += 1.0

    if not int(a.acik):
        _SAYAC["kapalı_çağrı"] += 1.0
        _SAYAC["artık"] += once
        return {"alarm_önce": _bit(once), "alarm_sonra": _bit(once),
                "ağırlık_önce": once, "ağırlık_sonra": once,
                "sıfırlanan": 0, "satır": satir, "açık": False}

    sifirlanan = 0
    if once > 1e-12:
        Q = P.copy()
        Q[..., dizin] = 0.0
        nrm = np.linalg.norm(Q, axis=-1, keepdims=True)
        assert float(np.min(nrm)) > 1e-300, (
            "durumun TAMAMI mantık yırtığı sektöründe -- kod uzayına "
            "izdüşümü sıfır. Bu bir sayı hatası değil, mimarî bir "
            "çöküştür: parite lifi yanlış seçilmiş olmalı.")
        Q = Q / nrm
        sifirlanan = int(np.count_nonzero(dizin))
        _SAYAC["sıfırlanan"] += float(sifirlanan)
        if yazmac is not None:
            yazmac.psi = Q if psi.ndim == 2 else Q.reshape(-1)
        elif isinstance(hedef, np.ndarray) and hedef.ndim == P.ndim:
            hedef[...] = Q.reshape(hedef.shape)
        P = Q

    sonra, _ = tenakuz_alarmi(P, a)
    _SAYAC["artık"] += sonra
    return {"alarm_önce": _bit(once), "alarm_sonra": _bit(sonra),
            "ağırlık_önce": once, "ağırlık_sonra": sonra,
            "sıfırlanan": sifirlanan, "satır": satir, "açık": True}


def mantiki_degil(psi: np.ndarray,
                  ayar: Optional[SadakatAyari] = None) -> np.ndarray:
    a = ayar or SadakatAyari()
    P = np.asarray(psi)
    tek = P.ndim == 1
    Q = P.reshape(1, -1) if tek else P
    d = Q.shape[-1]
    maske = parite_maskesi(a)
    if bin(int(maske)).count("1") % 2 == 1:
        maske = int(maske) & (int(maske) - 1)
    assert maske != 0, (
        "mantıkî olumsuzlama için en az iki basamaklı bir parite lifi "
        "lâzım -- tek basamakta ¬P kod uzayının dışına düşer")
    k = np.arange(d, dtype=np.int64)
    return Q[..., k ^ np.int64(maske)].reshape(P.shape)


def _bit(agirlik: float) -> int:
    return int(float(agirlik) > 1e-12)


def sadakat_beyani() -> Dict[str, Any]:
    c = max(1.0, _SAYAC["çağrı"])
    return {"çağrı": int(_SAYAC["çağrı"]),
            "yoklanan": int(_SAYAC["yoklanan"]),
            "alarm": int(_SAYAC["alarm"]),
            "sıfırlanan": int(_SAYAC["sıfırlanan"]),
            "alarm_nispeti": float(_SAYAC["ağırlık"] / c),
            "artık_nispeti": float(_SAYAC["artık"] / c),
            "kapalı_çağrı": int(_SAYAC["kapalı_çağrı"])}


def sadakat_sifirla() -> None:
    for k in _SAYAC:
        _SAYAC[k] = 0.0
