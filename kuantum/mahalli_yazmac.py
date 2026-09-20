from __future__ import annotations

import math
from typing import Any, Dict, Optional, Sequence, Tuple

import numpy as np

__all__ = ["MahalliYazmac", "mahalli_beyani", "mahalli_metni",
           "uzunluk_beyani", "uzunluk_metni", "uzunluk_genligi"]


def uzunluk_genligi(mahalli, pencere: int):
    if mahalli is None:
        _UZUNLUK["bağlanmadı"] = _UZUNLUK.get("bağlanmadı", 0.0) + 1.0
        return None
    dal = getattr(mahalli, "_uzunluk", None)
    assert dal is not None, (
        "UZUNLUK KATMANI HİÇ AÇILMADI -- intâc onu kurar (ferman 2-Õ); "
        "burada ikinci defa kurmak çift başlılıktır (ferman 1-M).")
    return dal


ZIRH_QUDITI = 1 << 20


_MAHALLI: Dict[str, float] = {
    "kuruldu": 0.0, "qudit": 0.0, "taban": 0.0, "yığın": 0.0,
    "seviye": 0.0,
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
        "    TAŞIYICI ℂ^{N×q}: qudit başına q seviyeli mahallî durum"
        " (ferman 2-V)",
        "    tutulan bellek  : %.3f MB   (%d seviye × 16 bayt)"
        % (d["bayt"] / 1e6, int(d.get("seviye", 0))),
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

    def seviye_fazi(self, taban: Optional[int] = None) -> np.ndarray:
        q = int(self.taban if taban is None else taban)
        v = np.zeros(q, float)
        if not self._kok:
            return v
        for ad, k in self._kok.items():
            v[int(k) % q] += float(self.cartan[int(k)])
        _MAHALLI["seviye_fazı"] = float(np.abs(v).sum())
        _MAHALLI["seviye_kökü"] = float(len(self._kok))
        return v

    def kuresel_faz(self) -> float:
        return float(np.dot(self.cartan, self.kok_agirligi()))

    def __init__(self, taban: int) -> None:
        self.qudit = int(ZIRH_QUDITI)
        self._kok: Dict[str, int] = {}
        self.cartan = np.zeros(0, float)
        self.taban = max(2, int(taban))
        self.yigin = 0
        self.pencere = 0
        self.hal = np.zeros((0, self.qudit, self.taban), complex)
        _MAHALLI["kuruldu"] = 1.0
        _MAHALLI["qudit"] = float(self.qudit)
        _MAHALLI["taban"] = float(self.taban)

    def hazirla(self, pencere: int, yigin: int) -> None:
        p = max(1, min(int(pencere), self.qudit))
        y = max(1, int(yigin))
        if y > self.yigin:
            gereken = int(y) * int(self.qudit) * int(self.taban) * 16
            from nefs.donanim import bellek_haddi
            had = bellek_haddi()
            assert had is None or gereken <= int(had), (
                "MAHALLÎ ZIRH ÖLÇÜLEN BELLEĞE SIĞMIYOR: %d qudit × %d "
                "seviye × 16 bayt × %d yığın = %.2f GB, ölçülen hadd "
                "%.2f GB (ferman 2-S, 2-I: bütçe ölçülür, sığmayan bütçe "
                "kurulmaz)"
                % (self.qudit, self.taban, y, gereken / 1e9,
                   float(had or 0) / 1e9))
            self.hal = np.zeros((y, self.qudit, self.taban), complex)
            self.hal[..., 0] = 1.0 / math.sqrt(float(self.qudit))
            self.yigin = y
            _MAHALLI["tahsis"] += 1.0
            _MAHALLI["bayt"] = float(self.hal.nbytes)
            _MAHALLI["seviye"] = float(self.taban)
        self.pencere = p
        _MAHALLI["pencere"] = float(p)
        _MAHALLI["yığın"] = float(self.yigin)
        _MAHALLI["seyirci"] = float(self.qudit - p)

    @property
    def genlik(self) -> np.ndarray:
        return np.linalg.norm(self.hal, axis=-1)

    @property
    def faz(self) -> np.ndarray:
        return np.angle(self.hal.sum(axis=-1))

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
        seviye = np.mod(b, self.taban)
        self.hal[:B, :n, :] = 0.0
        satir = np.repeat(np.arange(B), n)
        sutun = np.tile(np.arange(n), B)
        self.hal[satir, sutun, seviye.reshape(-1)] = (
            (agirlik / norm).reshape(-1)
            * np.exp(1j * math.pi * w.reshape(-1)))

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
        kontrol_fazi = np.angle(self.hal[:B, kk, :].sum(axis=-1))
        kayma = j.reshape(1, -1) * kontrol_fazi
        satir = np.repeat(np.arange(B), h.shape[1])
        sutun = h.reshape(-1)
        donme = np.exp(1j * kayma.reshape(-1))
        np.multiply.at(self.hal, (satir, sutun), donme[:, None])
        dokunulan = np.unique(sutun)
        _MAHALLI["vuruş"] += float(k.size)
        _MAHALLI["dokunulan"] = float(dokunulan.size)
        _MAHALLI["faz_kayması"] = float(np.mean(np.abs(kayma)))
        return float(np.mean(np.abs(kayma)))

    def _seviye_operatoru(self, M: np.ndarray, cins: str) -> np.ndarray:
        A = np.zeros((self.taban, self.taban), float)
        S = np.asarray(M, float)
        k = int(min(self.taban, S.shape[0]))
        A[:k, :k] = S[:k, :k]
        nrm = float(np.linalg.norm(A))
        if nrm <= 0.0:
            return np.eye(self.taban, dtype=complex)
        A = A / nrm
        if cins == "uzay":
            w, V = np.linalg.eigh(0.5 * (A + A.T))
            _MAHALLI["aşkın_eigh"] = _MAHALLI.get("aşkın_eigh", 0.0) + 1.0
            _MAHALLI["aşkın_exp"] = _MAHALLI.get("aşkın_exp", 0.0) + 1.0
            return (V * np.exp(1j * w)) @ V.conj().T
        if cins == "kategori":
            w, V = np.linalg.eigh(1j * (0.5 * (A - A.T)))
            _MAHALLI["aşkın_eigh"] = _MAHALLI.get("aşkın_eigh", 0.0) + 1.0
            _MAHALLI["aşkın_exp"] = _MAHALLI.get("aşkın_exp", 0.0) + 1.0
            return (V * np.exp(-1j * w)) @ V.conj().T
        return A.astype(complex)

    def modlari_vur(self, izdusum: Dict[str, np.ndarray],
                    pay: Sequence[float]) -> Dict[str, float]:
        p = np.asarray(list(pay), float).reshape(-1)
        assert p.size == 3, (
            "dereceli devir üç bileşenlidir (𝒮_simetrik, 𝒜_yönlü, "
            "Ω_yırtık); %d verildi (ferman 2-Ā-B)" % p.size)
        assert self.yigin > 0 and self.pencere > 0, (
            "MODLAR BOŞ ZIRHA VURULAMAZ -- evvelâ hazırlanır (ferman 2-A)")
        p = np.maximum(p, 0.0)
        top = float(p.sum())
        assert top > 0.0, (
            "HODGE PAYLARI TAMAMEN SÖNDÜ -- üç bileşenin toplamı sıfır; "
            "bu, hendesenin ölçülmediğinin delilidir (ferman 5)")
        p = p / top
        n = int(self.pencere)
        sinir = np.cumsum(np.rint(p * float(n)).astype(np.int64))
        sinir[-1] = n
        evvel = float(np.linalg.norm(self.hal[:, :n, :]))
        adlar = ("uzay", "kategori", "operad")
        anahtar = ("Π_uzay", "Π_kategori", "Π_operad")
        sayim: Dict[str, float] = {}
        bas = 0
        for ad, ah, son in zip(adlar, anahtar, sinir.tolist()):
            son = int(min(max(son, bas), n))
            sayim["mod_%s" % ad] = float(son - bas)
            if son > bas:
                U = self._seviye_operatoru(izdusum[ah], ad)
                dilim = self.hal[:, bas:son, :]
                self.hal[:, bas:son, :] = dilim @ U.T
            bas = son
        sonra = self.hal[:, :n, :]
        nrm = np.linalg.norm(sonra, axis=-1, keepdims=True)
        canli = nrm > 0.0
        assert bool(canli.any()), (
            "DERECELİ DEVİR AKTİF PENCEREYİ TAMAMEN SÖNDÜRDÜ -- "
            "izdüşüm demeti yanlış kurulmuş (ferman 5)")
        self.hal[:, :n, :] = np.where(canli, sonra / np.where(canli, nrm,
                                                              1.0), sonra)
        sayim["mod_vuruş"] = float(n)
        sayim["mod_norm_evvel"] = evvel
        sayim["mod_norm_sonra"] = float(np.linalg.norm(self.hal[:, :n, :]))
        _MAHALLI.update(sayim)
        _MAHALLI["mod_çağrı"] = _MAHALLI.get("mod_çağrı", 0.0) + 1.0
        return sayim

    def genlik_sondur(self, hedef: np.ndarray, sonum) -> float:
        h = np.mod(np.asarray(hedef, np.int64).reshape(-1),
                   max(1, int(self.pencere)))
        c = np.asarray(sonum, float).reshape(-1)
        if h.size == 0:
            return 0.0
        c = np.resize(c, h.size)
        self.hal[:, h, :] = self.hal[:, h, :] * c[None, :, None]
        _MAHALLI["sönüm"] += float(h.size)
        return float(np.abs(1.0 - c).mean())

    def uzunluk_katmani(self, cephe: int, hadd: int = 0) -> np.ndarray:
        c = int(cephe) % self.qudit
        L = max(1, min(int(hadd) if int(hadd) > 0 else self.qudit,
                       self.qudit - c))
        dilim = self.hal[:, c:c + L, :]
        g = np.linalg.norm(dilim, axis=-1).mean(axis=0)
        f = np.angle(dilim.sum(axis=-1)).mean(axis=0)
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

    def kok_seviyesi(self, ad: str) -> int:
        return int(self.kok_indisi(str(ad)) % int(self.taban))

    def sektor_yigini(self, ad: str) -> np.ndarray:
        assert self.yigin > 0 and self.pencere > 0, (
            "SEKTÖR AĞIRLIĞI BOŞ ZIRHTAN OKUNAMAZ -- evvelâ `hazirla` "
            "koşar (ferman 2-A, 2-Ö)")
        s = self.kok_seviyesi(ad)
        n = int(self.pencere)
        _MAHALLI["sektör_okuma"] = _MAHALLI.get("sektör_okuma", 0.0) + 1.0
        return np.sum(np.abs(self.hal[:, :n, s]) ** 2, axis=1)

    def sektor_agirligi(self, ad: str,
                        indis: Optional[np.ndarray] = None) -> complex:
        k = self.kok_indisi(str(ad))
        w = self.sektor_yigini(ad)
        agir = float(w.mean()) if w.size else 0.0
        return complex(agir * np.exp(1j * float(self.cartan[k])))

    def kulli_agirlik(self) -> float:
        assert self.yigin > 0 and self.pencere > 0, (
            "KÜLLÎ AĞIRLIK BOŞ ZIRHTAN OKUNAMAZ (ferman 2-A)")
        n = int(self.pencere)
        _MAHALLI["küllî_okuma"] = _MAHALLI.get("küllî_okuma", 0.0) + 1.0
        return float(np.sum(np.abs(self.hal[:, :n, :]) ** 2))

    def kok_dagilimi(self, ad: str) -> np.ndarray:
        s = self.kok_seviyesi(ad)
        n = int(self.pencere)
        p = np.abs(self.hal[:, :n, s]) ** 2
        top = p.sum(axis=1, keepdims=True)
        canli = top > 0.0
        return np.where(canli, p / np.where(canli, top, 1.0),
                        1.0 / float(max(1, n)))

    def kok_kapisi(self, ad: str, M: np.ndarray) -> int:
        assert self.yigin > 0 and self.pencere > 0, (
            "KÖK KAPISI BOŞ ZIRHA VURULAMAZ (ferman 2-A)")
        s = self.kok_seviyesi(ad)
        A = np.asarray(M, complex)
        assert A.ndim == 2 and A.shape[0] == A.shape[1], (
            "kök kapısı kare olmalı, %r verildi" % (A.shape,))
        n = int(self.pencere)
        g = int(min(A.shape[0], self.taban))
        bas = int(s)
        son = int(min(self.taban, bas + g))
        k = son - bas
        if k < 2:
            _MAHALLI["kök_düşen"] = _MAHALLI.get("kök_düşen", 0.0) + 1.0
            return 0
        self.hal[:, :n, bas:son] = (self.hal[:, :n, bas:son]
                                    @ A[:k, :k].T)
        _MAHALLI["kök_kapısı"] = _MAHALLI.get("kök_kapısı", 0.0) + 1.0
        return k

    def kok_donmesi(self, ad: str, aci: np.ndarray) -> int:
        assert self.yigin > 0 and self.pencere > 0, (
            "KÖK DÖNMESİ BOŞ ZIRHA VURULAMAZ (ferman 2-A)")
        a = np.asarray(aci, float).reshape(-1)
        if a.size == 0:
            return 0
        s = self.kok_seviyesi(ad)
        n = int(self.pencere)
        cift = int(min(a.size, (int(self.taban) - s) // 2))
        if cift < 1:
            _MAHALLI["kök_düşen"] = _MAHALLI.get("kök_düşen", 0.0) + 1.0
            return 0
        a = a[:cift]
        c, sn = np.cos(a), np.sin(a)
        u = self.hal[:, :n, s:s + 2 * cift:2]
        v = self.hal[:, :n, s + 1:s + 2 * cift:2]
        self.hal[:, :n, s:s + 2 * cift:2] = c * u - sn * v
        self.hal[:, :n, s + 1:s + 2 * cift:2] = sn * u + c * v
        _MAHALLI["kök_dönmesi"] = _MAHALLI.get("kök_dönmesi", 0.0) + 1.0
        _MAHALLI["aşkın_cos"] = _MAHALLI.get("aşkın_cos", 0.0) + 1.0
        _MAHALLI["aşkın_sin"] = _MAHALLI.get("aşkın_sin", 0.0) + 1.0
        return 2 * cift

    def senet_dilimi(self) -> np.ndarray:
        if self.yigin <= 0 or self.pencere <= 0:
            return np.zeros((0, 0), complex)
        n = int(self.pencere)
        _MAHALLI["senet_bandı"] = _MAHALLI.get("senet_bandı", 0.0) + 1.0
        _MAHALLI["senet_baytı"] = (_MAHALLI.get("senet_baytı", 0.0)
                                   + float(self.hal[:, :n, :].nbytes))
        return np.asarray(self.hal[:, :n, :], complex).copy()

    def beyan(self) -> Dict[str, float]:
        return mahalli_beyani()
