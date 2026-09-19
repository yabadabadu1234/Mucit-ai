from __future__ import annotations

import math
from typing import Any, Dict, Optional, Tuple

import numpy as np

__all__ = ["MahalliYazmac", "mahalli_beyani", "mahalli_metni",
           "uzunluk_beyani", "uzunluk_metni", "uzunluk_genligi"]


def uzunluk_genligi(mahalli, pencere: int):
    if mahalli is None:
        _UZUNLUK["bağlanmadı"] = _UZUNLUK.get("bağlanmadı", 0.0) + 1.0
        return None
    cephe = int(getattr(mahalli, "pencere", 0) or 0)
    return mahalli.uzunluk_katmani(cephe, hadd=int(pencere))


ZIRH_QUDITI = 1 << 20


_MAHALLI: Dict[str, float] = {
    "kuruldu": 0.0, "qudit": 0.0, "taban": 0.0, "yığın": 0.0,
    "bayt": 0.0, "vuruş": 0.0, "dokunulan": 0.0, "seyirci": 0.0,
    "pencere": 0.0, "faz_kayması": 0.0, "tahsis": 0.0,
    "kök": 0.0, "cartan_normu": 0.0, "sönüm": 0.0, "açık": 1.0}


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
        "    CARTAN KÖKÜ %d   küresel ayar fazı normu %.6e rad"
        % (int(d.get("kök", 0)), d.get("cartan_normu", 0.0)),
        "    genlik sönümü   : %d qudit   (meleke yalnız faza değil"
        " GENLİĞE de hükmeder -- ferman 2-Û)" % int(d.get("sönüm", 0)),
        "    Kök vektörü BİR MİLYON QUDİTE SERPİLMEZ (ferman 2-Â):",
        "    KAN üssüne küresel rezonans fazı olarak girer.",
        "    BAĞLAM BURADA DURUR (ferman 2-Ĝ): `_psi`nin `yer` ekseni",
        "    kaldırıldı; pencereyi artık yazmacın ebadı değil bu zırh",
        "    hudutlar. Cevap nedensel cepheden okunur (ferman 2-Ê).",
    ])


_UZUNLUK: Dict[str, float] = {
    "kuruldu": 0.0, "hadd": 0.0, "cephe": 0.0, "hüküm": 0.0,
    "entropi": 0.0, "tepe_ihtimali": 0.0, "kuyruk": 0.0,
    "durma_genliği": 0.0, "devam_genliği": 0.0, "açık": 1.0}


def uzunluk_beyani() -> Dict[str, float]:
    return dict(_UZUNLUK)


def uzunluk_metni(b: Optional[Dict[str, float]] = None) -> str:
    d = dict(b or uzunluk_beyani())
    if not d.get("kuruldu"):
        return ("  ÜÇÜNCÜ QUDİT KATMANI (uzunluk): KURULMADI -- kırmızı "
                "(ferman 2-Õ)")
    return "\n".join([
        "  ÜÇÜNCÜ QUDİT KATMANI -- UZUNLUK SÜPERPOZİSYONU (ferman 2-Õ)",
        "    aynı anda 1 … %d belirteçlik çıktı hâlleri taşınır;"
        % int(d["hadd"]),
        "    üst hudut vardır, ALT HUDUT YOKTUR.",
        "    nedensel cephe %d   son durma hükmü %d belirteç"
        % (int(d["cephe"]), int(d["hüküm"])),
        "    ÇIKTIDA ÜST HUDUT YOKTUR (ferman 2-Ó-B): her adımda durma"
        " genliği %.6e ile" % d.get("durma_genliği", 0.0),
        "    devam genliği %.6e tartılır; model uygun gördüğünde durur."
        % d.get("devam_genliği", 0.0),
        "    dağılım entropisi %.6f nat   tepe ihtimali %.6e"
        % (d["entropi"], d["tepe_ihtimali"]),
        "    hadde taşan kuyruk ihtimali %.6e   (ölçü kapatılabilir: %s)"
        % (d["kuyruk"], "açık" if d.get("açık") else "KAPALI"),
        "    Hüküm determinist Fubini-Study okumasıdır, zar atılmaz"
        " (ferman 2-Ĵ).",
    ])


class MahalliYazmac:

    def kok_indisi(self, ad: str) -> int:
        if ad not in self._kok:
            self._kok[ad] = len(self._kok)
            self.cartan = np.concatenate([self.cartan, np.zeros(1)])
        return int(self._kok[ad])

    def cartan_ekle(self, ad: str, aci: float) -> int:
        k = self.kok_indisi(str(ad))
        self.cartan[k] += float(aci)
        self.cartan[k] = (math.remainder(float(self.cartan[k]),
                                         2.0 * math.pi))
        _MAHALLI["kök"] = float(self.cartan.size)
        _MAHALLI["cartan_normu"] = float(np.abs(self.cartan).sum())
        return k

    def cartan_oku(self, ad: str) -> float:
        k = self._kok.get(str(ad))
        return 0.0 if k is None else float(self.cartan[int(k)])

    def kok_agirligi(self) -> np.ndarray:
        n = max(1, int(self.cartan.size))
        return np.arange(1, n + 1, dtype=float) / float(n)

    def kuresel_faz(self) -> float:
        return float(np.dot(self.cartan, self.kok_agirligi()))

    def __init__(self, taban: int) -> None:
        self.qudit = int(ZIRH_QUDITI)
        self._kok: Dict[str, int] = {}
        self.cartan = np.zeros(0, float)
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

    def genlik_sondur(self, hedef: np.ndarray, sonum) -> float:
        h = np.mod(np.asarray(hedef, np.int64).reshape(-1),
                   max(1, int(self.pencere)))
        c = np.asarray(sonum, float).reshape(-1)
        if h.size == 0:
            return 0.0
        c = np.resize(c, h.size)
        self.hal[:, h, 0] = self.hal[:, h, 0] * c[None, :]
        _MAHALLI["sönüm"] += float(h.size)
        return float(np.abs(1.0 - c).mean())

    def uzunluk_katmani(self, cephe: int, hadd: int = 0) -> np.ndarray:
        c = int(cephe) % self.qudit
        L = max(1, min(int(hadd) if int(hadd) > 0 else self.qudit,
                       self.qudit - c))
        g = np.abs(self.hal[:, c:c + L, 0]).mean(axis=0)
        f = self.hal[:, c:c + L, 1].mean(axis=0)
        devam = np.clip(g / max(float(g.max()), 1e-300), 0.0, 1.0)
        dur = np.sqrt(np.maximum(1.0 - devam * devam, 0.0))
        us = np.concatenate([[0.0], np.cumsum(np.log(
            np.maximum(devam, 1e-300)))[:-1]])
        us = us + np.log(np.maximum(dur, 1e-300))
        us = us - float(us.max())
        dal = np.exp(us) * np.exp(1j * np.cumsum(f))
        nrm = float(np.linalg.norm(dal))
        assert nrm > 0.0, (
            "uzunluk katmanı tamamen söndü -- hiçbir çıktı boyu "
            "taşınmıyor (ferman 2-Õ)")
        self._uzunluk = dal / nrm
        self._uzunluk_cephesi = c
        P = np.abs(self._uzunluk) ** 2
        _UZUNLUK["kuruldu"] = 1.0
        _UZUNLUK["hadd"] = float(L)
        _UZUNLUK["cephe"] = float(c)
        _UZUNLUK["entropi"] = float(
            -np.sum(P * np.log(np.maximum(P, 1e-300))))
        _UZUNLUK["tepe_ihtimali"] = float(P.max())
        _UZUNLUK["kuyruk"] = float(
            1.0 - P.sum()) if P.sum() < 1.0 else 0.0
        return self._uzunluk

    def durma_hukmu(self, adim: int) -> bool:
        dal = getattr(self, "_uzunluk", None)
        assert dal is not None, (
            "uzunluk katmanı hiç açılmadı -- durma hükmü verecek bir "
            "hâl yok; üretim susmayan bir döngüye düşerdi (ferman "
            "2-Õ, 2-Ó-B)")
        if not _UZUNLUK.get("açık"):
            return True
        P = np.abs(dal) ** 2
        top = float(P.sum())
        assert top > 0.0, (
            "uzunluk katmanı tamamen söndü -- durma hükmü verilemez "
            "(ferman 2-Õ)")
        k = int(adim)
        if k >= P.size:
            return True
        dur = float(P[k])
        devam = float(P[k + 1:].sum())
        _UZUNLUK["durma_genliği"] = dur / top
        _UZUNLUK["devam_genliği"] = devam / top
        durdu = bool(dur > devam)
        if durdu:
            _UZUNLUK["hüküm"] = float(k + 1)
        return durdu

    def sektor_agirligi(self, ad: str, indis: np.ndarray) -> complex:
        k = self.kok_indisi(str(ad))
        i = np.mod(np.asarray(indis, np.int64).reshape(-1),
                   max(1, int(self.pencere)))
        if i.size == 0:
            return 0j
        agir = float((np.abs(self.hal[:, i, 0]) ** 2).sum()
                     / max(1, self.hal.shape[0]))
        return complex(agir * np.exp(1j * float(self.cartan[k])))

    def beyan(self) -> Dict[str, float]:
        return mahalli_beyani()
