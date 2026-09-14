from __future__ import annotations

import math
from typing import Any, Dict, Optional, Tuple

import numpy as np

__all__ = ["MahalliYazmac", "mahalli_beyani", "mahalli_metni"]


_MAHALLI: Dict[str, float] = {
    "kuruldu": 0.0, "qudit": 0.0, "taban": 0.0, "yığın": 0.0,
    "bayt": 0.0, "vuruş": 0.0, "dokunulan": 0.0, "seyirci": 0.0,
    "faz_kayması": 0.0, "açık": 1.0}


def mahalli_beyani() -> Dict[str, float]:
    b = dict(_MAHALLI)
    b["seyirci_nispeti"] = ((b["seyirci"] / b["qudit"])
                            if b["qudit"] else 0.0)
    return b


def mahalli_metni(b: Optional[Dict[str, float]] = None) -> str:
    d = dict(b or mahalli_beyani())
    if not d.get("kuruldu"):
        return "  MAHALLÎ YAZMAÇ: KURULMADI -- kırmızı (ferman 2-Ş)"
    return "\n".join([
        "  MAHALLÎ YAZMAÇ (ferman 2-Ş: donanım kanadı, ayrık qudit)",
        "    qudit × taban   : %d × %d   yığın %d"
        % (int(d["qudit"]), int(d["taban"]), int(d["yığın"])),
        "    tutulan bellek  : %.3f MB   (qudit başına genlik + faz)"
        % (d["bayt"] / 1e6),
        "    kapı vuruşu     : %d   dokunulan qudit %d   seyirci %d"
        " (%.4f)"
        % (int(d["vuruş"]), int(d["dokunulan"]), int(d["seyirci"]),
           d["seyirci_nispeti"]),
        "    biriken faz kayması : %.6e rad   (sürekli U(1))"
        % d["faz_kayması"],
        "    Bu yazmaç `_psi`nin yerine geçmez: `_psi` TEKİL KAVRAM",
        "    LİFİDİR (bir quditin iç anatomisi), bu ise KÜLLÎ yazmacın",
        "    mahallî tensörüdür. İkisi ayrı seviyedir (ferman 2-Ş).",
    ])


class MahalliYazmac:

    def __init__(self, qudit: int, taban: int, yigin: int = 1) -> None:
        self.qudit = max(1, int(qudit))
        self.taban = max(2, int(taban))
        self.yigin = max(1, int(yigin))
        self.hal = np.zeros((self.yigin, self.qudit, 2), float)
        self.hal[..., 0] = 1.0 / math.sqrt(float(self.qudit))
        _MAHALLI["kuruldu"] = 1.0
        _MAHALLI["qudit"] = float(self.qudit)
        _MAHALLI["taban"] = float(self.taban)
        _MAHALLI["yığın"] = float(self.yigin)
        _MAHALLI["bayt"] = float(self.hal.nbytes)

    @property
    def genlik(self) -> np.ndarray:
        return self.hal[..., 0]

    @property
    def faz(self) -> np.ndarray:
        return self.hal[..., 1]

    def koordinat(self) -> np.ndarray:
        return self._koordinat

    def yerlestir(self, basamak: np.ndarray, dolu: np.ndarray) -> None:
        b = np.asarray(basamak, np.int64)
        assert b.shape == (self.yigin, self.qudit), (
            "mahallî yazmaç bağlam kadardır: %r ≠ %r -- doldurma yoktur "
            "(ferman 2-O)" % (b.shape, (self.yigin, self.qudit)))
        w = 2.0 * (b.astype(float) / float(self.taban - 1)) - 1.0
        self._koordinat = w
        agirlik = np.asarray(dolu, bool).astype(float)
        norm = np.maximum(np.linalg.norm(agirlik, axis=-1, keepdims=True),
                          1e-300)
        self.hal[..., 0] = agirlik / norm
        self.hal[..., 1] = math.pi * w

    def kapilari_vur(self, kontrol: np.ndarray, hedef: np.ndarray,
                     bag: np.ndarray) -> float:
        k = np.asarray(kontrol, np.int64).reshape(-1)
        h = np.asarray(hedef, np.int64)
        j = np.asarray(bag, float).reshape(-1)
        assert k.size == j.size, (
            "her kapının bir bağ kuvveti olmalı: %d kontrol, %d bağ"
            % (k.size, j.size))
        if not _MAHALLI["açık"] or k.size == 0:
            return 0.0
        h = h if h.ndim == 2 else np.broadcast_to(
            h.reshape(1, -1), (self.yigin, h.size))
        kontrol_fazi = np.take_along_axis(
            self.hal[..., 1], np.clip(k, 0, self.qudit - 1).reshape(1, -1)
            * np.ones((self.yigin, 1), np.int64), axis=-1)
        kayma = j.reshape(1, -1) * kontrol_fazi
        yeni = self.hal[..., 1].copy()
        np.add.at(yeni, (np.repeat(np.arange(self.yigin), h.shape[1]),
                         h.reshape(-1)), kayma.reshape(-1))
        self.hal[..., 1] = np.remainder(yeni + math.pi,
                                        2.0 * math.pi) - math.pi
        dokunulan = int(np.unique(h).size)
        _MAHALLI["vuruş"] += float(k.size)
        _MAHALLI["dokunulan"] = float(dokunulan)
        _MAHALLI["seyirci"] = float(max(0, self.qudit - dokunulan))
        _MAHALLI["faz_kayması"] = float(np.mean(np.abs(kayma)))
        return float(np.mean(np.abs(kayma)))

    def beyan(self) -> Dict[str, float]:
        return mahalli_beyani()
