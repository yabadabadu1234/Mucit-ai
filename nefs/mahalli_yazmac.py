from __future__ import annotations

import math
from typing import Any, Dict, Optional, Tuple

import numpy as np

__all__ = ["MahalliYazmac", "mahalli_beyani", "mahalli_metni"]


ZIRH_QUDITI = 1 << 20


_MAHALLI: Dict[str, float] = {
    "kuruldu": 0.0, "qudit": 0.0, "taban": 0.0, "yığın": 0.0,
    "bayt": 0.0, "vuruş": 0.0, "dokunulan": 0.0, "seyirci": 0.0,
    "pencere": 0.0, "faz_kayması": 0.0, "tahsis": 0.0, "açık": 1.0}


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
        "    ZIRH %d qudit × taban %d   yığın %d   AKTİF PENCERE %d"
        % (int(d["qudit"]), int(d["taban"]), int(d["yığın"]),
           int(d.get("pencere", 0))),
        "    Zırh SABİTTİR (ferman 2-Ğ): her suâlde yeniden açılmaz,",
        "    adres kaymaz; pencere dışı qudit seyircidir, hesaplanmaz.",
        "    tutulan bellek  : %.3f MB   (qudit başına genlik + faz)"
        % (d["bayt"] / 1e6),
        "    kapı vuruşu     : %d   dokunulan qudit %d   seyirci %d"
        " (%.4f)   tahsis %d kere"
        % (int(d["vuruş"]), int(d["dokunulan"]), int(d["seyirci"]),
           d["seyirci_nispeti"], int(d.get("tahsis", 0))),
        "    biriken faz kayması : %.6e rad   (sürekli U(1))"
        % d["faz_kayması"],
        "    Bu yazmaç `_psi`nin yerine geçmez: `_psi` TEKİL KAVRAM",
        "    LİFİDİR (bir quditin iç anatomisi), bu ise KÜLLÎ yazmacın",
        "    mahallî tensörüdür. İkisi ayrı seviyedir (ferman 2-Ş).",
    ])


class MahalliYazmac:

    def __init__(self, taban: int) -> None:
        self.qudit = int(ZIRH_QUDITI)
        self.taban = max(2, int(taban))
        self.yigin = 0
        self.pencere = 0
        self.hal = np.zeros((0, self.qudit, 2), float)
        _MAHALLI["kuruldu"] = 1.0
        _MAHALLI["qudit"] = float(self.qudit)
        _MAHALLI["taban"] = float(self.taban)

    def hazirla(self, pencere: int, yigin: int) -> None:
        p = max(1, min(int(pencere), self.qudit))
        y = max(1, int(yigin))
        if y > self.yigin:
            self.hal = np.zeros((y, self.qudit, 2), float)
            self.hal[..., 0] = 1.0 / math.sqrt(float(self.qudit))
            self.yigin = y
            _MAHALLI["tahsis"] += 1.0
            _MAHALLI["bayt"] = float(self.hal.nbytes)
        self.pencere = p
        _MAHALLI["pencere"] = float(p)
        _MAHALLI["yığın"] = float(self.yigin)
        _MAHALLI["seyirci"] = float(self.qudit - p)

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
        assert b.shape[0] <= self.yigin and b.shape[1] == self.pencere, (
            "aktif pencere zırhın içinde nefes alır: %r ≠ %r "
            "(ferman 2-Ğ)" % (b.shape, (self.yigin, self.pencere)))
        n = int(self.pencere)
        w = 2.0 * (b.astype(float) / float(self.taban - 1)) - 1.0
        self._koordinat = w
        agirlik = np.asarray(dolu, bool).astype(float)
        norm = np.maximum(np.linalg.norm(agirlik, axis=-1, keepdims=True),
                          1e-300)
        B = int(b.shape[0])
        self.hal[:B, :n, 0] = agirlik / norm
        self.hal[:B, :n, 1] = math.pi * w

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
        h = np.mod(h, max(1, int(self.pencere)))
        kk = np.clip(k, 0, self.qudit - 1)
        B = int(h.shape[0])
        kayma = j.reshape(1, -1) * self.hal[:B, kk, 1]
        satir = np.repeat(np.arange(B), h.shape[1])
        sutun = h.reshape(-1)
        np.add.at(self.hal[..., 1], (satir, sutun), kayma.reshape(-1))
        dokunulan = np.unique(sutun)
        self.hal[:B][:, dokunulan, 1] = np.remainder(
            self.hal[:B][:, dokunulan, 1] + math.pi,
            2.0 * math.pi) - math.pi
        _MAHALLI["vuruş"] += float(k.size)
        _MAHALLI["dokunulan"] = float(dokunulan.size)
        _MAHALLI["faz_kayması"] = float(np.mean(np.abs(kayma)))
        return float(np.mean(np.abs(kayma)))

    def beyan(self) -> Dict[str, float]:
        return mahalli_beyani()
