from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["MeczAyari", "Memuriyet", "hata_operatoru", "uretecler",
           "egim", "cukur", "duvar", "yaricap", "vadi", "nakil",
           "mecz_egit", "mecz_beyani", "mecz_metni", "mecz_sifirla"]


_MECZ: Dict[str, float] = {}


def mecz_sifirla() -> None:
    _MECZ.clear()
    _MECZ.update({"çağrı": 0.0, "tur": 0.0, "kabul": 0.0,
                  "adım_normu": 0.0, "eğim_normu": 0.0,
                  "kapsanan_parametre": 0.0, "toplam_parametre": 0.0,
                  "duvar_elenen": 0.0, "duvar_bakılan": 0.0,
                  "çukur": 0.0, "vadi": 0.0, "nakil": 0.0,
                  "ΔE": 0.0, "yarıçap": 0.0, "iz_g": 0.0,
                  "operatörlü_kefe": 0.0, "operatörsüz_kefe": 0.0,
                  "κ": 0.0, "yarıçap_düzeltmesi": 0.0,
                  "asal_açı": 0.0, "eğrilik": 0.0,
                  "nakil_geçirgenliği": 0.0, "nakil_dizi_boyu": 0.0,
                  "yönsüz_tur": 0.0, "kapı": 0.0, "üretecsiz": 0.0,
                  "ek_durum_ikiz_farkı": 0.0, "üreteç_ikiz_farkı": 0.0,
                  "senet_ileri": 0.0,
                  "durum_saklaması": 0.0})


mecz_sifirla()


@dataclass
class MeczAyari:
    ad: str = "mecz"
    tur: int = 8
    tohum: int = 0
    kademe: int = 0


SEKTOR_AGIRLIGI: Tuple[Tuple[str, float], ...] = (
    ("tenakuz", 1.0), ("nakz", 1.0), ("tasdik", -1.0),
    ("sukut", 0.5), ("makam", 0.5))

OPERATORSUZ_KEFE: Tuple[str, ...] = (
    "kategori", "tip", "çevrim", "monogami", "engel", "gedik",
    "kaide_halkası", "uzay", "zırh.sheaf", "zırh.betti", "zırh.koho",
    "zırh.homotopi", "zırh.nizam")


def hata_operatoru(q, hedefler: Optional[Sequence[int]] = None,
                   taban: int = 0) -> np.ndarray:
    d = int(q.y.d)
    h = np.zeros(d, float)
    for ad, w in SEKTOR_AGIRLIGI:
        i, j = q.y.sektor(ad)
        h[i:j] += float(w)
    _MECZ["operatörlü_kefe"] = float(len(SEKTOR_AGIRLIGI))
    _MECZ["operatörsüz_kefe"] = float(len(OPERATORSUZ_KEFE))
    if hedefler is None or int(taban) < 2:
        return h
    yer = d // int(taban)
    p = np.abs(np.asarray(q.y.psi, complex)) ** 2
    P = p.reshape(p.shape[0], int(taban), yer).sum(axis=2)
    P = P / np.maximum(P.sum(axis=1, keepdims=True), 1e-300)
    hed = np.asarray(list(hedefler), np.int64) % int(taban)
    pay = np.zeros(int(taban), float)
    for b, t in enumerate(hed[:P.shape[0]]):
        pay[int(t)] -= 1.0 / max(float(P[b % P.shape[0], int(t)]), 1e-12)
    h += np.repeat(pay, yer) / max(1, len(hed))
    return h


def uretecler(q) -> List[Tuple[int, int]]:
    from nefs.melekeler import harman_uretecleri
    return harman_uretecleri(tuple(int(x) for x in q.y.ayar.lif))


def _uretec_vur(psi: np.ndarray, lif: Tuple[int, ...],
                f: int, alt: int) -> np.ndarray:
    B = psi.shape[0]
    T = psi.reshape((B,) + lif)
    n = lif[int(f)]
    b = 1 << int(alt)
    if b >= n:
        return np.zeros((B, psi.shape[1]), psi.dtype)
    idx = np.arange(n)
    dus = idx[(idx & b) == 0]
    ust = dus | b
    out = np.zeros_like(T)
    eksen = int(f) + 1
    A = np.take(T, dus, axis=eksen)
    C = np.take(T, ust, axis=eksen)
    dilim_dus = [slice(None)] * T.ndim
    dilim_ust = [slice(None)] * T.ndim
    dilim_dus[eksen] = dus
    dilim_ust[eksen] = ust
    out[tuple(dilim_dus)] = -C
    out[tuple(dilim_ust)] = A
    return out.reshape(B, -1)


def hat_egriligi(dv_gercek: float, dv_lineer: float,
                 r: float) -> Dict[str, float]:
    r = float(r)
    assert r > 0.0, "yarıçap sıfırken eğrilik okunamaz"
    kappa = 2.0 * (float(dv_gercek) - float(dv_lineer)) / (r * r)
    _MECZ["κ"] = float(kappa)
    if kappa <= 0.0:
        return {"κ": float(kappa), "yarıçap*": 2.0 * r, "bükey": False}
    yildiz = -float(dv_lineer) / (kappa * r)
    return {"κ": float(kappa), "yarıçap*": float(abs(yildiz)),
            "bükey": True}


def cukur(psi: np.ndarray, H: np.ndarray,
          onceki: Optional[np.ndarray] = None) -> Dict[str, float]:
    from .grassmann import asal_acilar
    p = np.abs(psi) ** 2
    iz = np.maximum(p.sum(axis=1, keepdims=True), 1e-300)
    p = p / iz
    E = float((p * H[None, :]).sum(axis=1).mean())
    E2 = float((p * (H ** 2)[None, :]).sum(axis=1).mean())
    dE = float(np.sqrt(max(0.0, E2 - E * E)))
    _MECZ["ΔE"] = dE
    kipirti = float("nan")
    if onceki is not None:
        Y1 = np.asarray(onceki, complex).reshape(len(onceki), -1).T
        Y2 = np.asarray(psi, complex).reshape(psi.shape[0], -1).T
        if Y1.shape == Y2.shape and Y1.size:
            aci = asal_acilar(np.real(Y1), np.real(Y2))
            kipirti = float(np.max(aci)) if aci.size else 0.0
            _MECZ["asal_açı"] = kipirti
    durak = bool(dE <= 1e-12) or bool(
        kipirti == kipirti and kipirti <= float(np.arcsin(
            np.sqrt(np.finfo(float).eps))))
    return {"⟨H⟩": E, "ΔE": dE, "durak": durak, "asal_açı": kipirti}


def egim(q, H: np.ndarray) -> Dict[str, Any]:
    psi = np.asarray(q.y.psi, complex)
    lif = tuple(int(x) for x in q.y.ayar.lif)
    Hpsi = psi * H[None, :]
    g: List[float] = []
    met: List[float] = []
    for (f, alt) in uretecler(q):
        Gpsi = _uretec_vur(psi, lif, f, alt)
        g.append(2.0 * float(np.real(np.sum(np.conj(Gpsi) * Hpsi))))
        ust = float(np.real(np.sum(np.conj(Gpsi) * Gpsi)))
        ic = complex(np.sum(np.conj(psi) * Gpsi))
        met.append(max(0.0, ust - abs(ic) ** 2))
    v = np.asarray(g, float)
    m = np.asarray(met, float)
    _MECZ["eğim_normu"] = float(np.linalg.norm(v))
    _MECZ["iz_g"] = float(m.sum())
    return {"eğim": v, "metrik": m}


def duvar(metrik: np.ndarray) -> Dict[str, Any]:
    m = np.asarray(metrik, float)
    if m.size == 0:
        return {"maske": m, "elenen": 0, "bakılan": 0, "nispet": 0.0}
    nispet = m / max(float(m.max()), 1e-300)
    gecen = nispet > float(np.median(nispet)) * 1e-3
    _MECZ["duvar_bakılan"] = float(m.size)
    _MECZ["duvar_elenen"] = float(m.size - int(gecen.sum()))
    return {"maske": gecen.astype(float), "elenen": int(m.size - gecen.sum()),
            "bakılan": int(m.size), "nispet": float(gecen.mean())}


def yaricap(keyf: float, iz_g: float,
            seyir: Optional[Sequence[float]] = None) -> float:
    r = float(keyf) / float(np.sqrt(max(float(iz_g), 1e-300)))
    egrilik = 0.0
    if seyir is not None and len(seyir) >= 4:
        from .izgara import bukulme_dizeyi, bukulme_enerjisi, duzenli_uydur
        y = np.asarray(list(seyir), float).reshape(-1)
        t = np.linspace(-1.0, 1.0, y.size)
        G, k = max(4, min(8, y.size - 2)), 3
        u = duzenli_uydur(t, y, G, k)
        S = bukulme_dizeyi(G, k)
        c = np.asarray(u["c"], float).reshape(-1)
        egrilik = float(bukulme_enerjisi(c, S)) / max(float(y.var()), 1e-300)
        _MECZ["eğrilik"] = egrilik
        r = r / (1.0 + egrilik)
    _MECZ["yarıçap"] = r
    return r


def vadi(metrik: np.ndarray, maske: np.ndarray) -> np.ndarray:
    m = np.asarray(metrik, float) * np.asarray(maske, float)
    v = np.zeros_like(m)
    if m.size and float(m.max()) > 0.0:
        v[int(np.argmax(m))] = 1.0
    _MECZ["vadi"] += 1.0
    return v




def nakil(q, maske: np.ndarray) -> np.ndarray:
    from nefs.ara import ara
    psi = np.asarray(q.y.psi, complex)
    lif = tuple(int(x) for x in q.y.ayar.lif)
    sap: List[float] = []
    for (f, alt) in uretecler(q):
        Gpsi = _uretec_vur(psi, lif, f, alt)
        ust = float(np.real(np.sum(np.conj(Gpsi) * Gpsi)))
        ic = complex(np.sum(np.conj(psi) * Gpsi))
        sap.append(max(0.0, ust - abs(ic) ** 2))
    s = np.asarray(sap, float) * np.asarray(maske, float)
    v = np.zeros_like(s)
    if not s.size or float(s.max()) <= 0.0:
        _MECZ["nakil"] += 1.0
        return v
    dizi_genligi = np.abs(psi.reshape(psi.shape[0], -1)).sum(axis=0)
    kuyu = -dizi_genligi / max(float(dizi_genligi.max()), 1e-300)
    bedel = ara(ne="bedel", V=kuyu, E=float(kuyu.mean()),
                genislikler=(1, 2, 4, 8))
    gecirgen = max((float(d["T"]) for d in bedel), default=0.0)
    _MECZ["nakil"] += 1.0
    _MECZ["nakil_geçirgenliği"] = gecirgen
    _MECZ["nakil_dizi_boyu"] = float(dizi_genligi.size)
    kac = max(1, int(round(gecirgen * float(s.size))))
    for i in np.argsort(s)[::-1][:kac]:
        v[int(i)] = 1.0
    return v / max(float(np.linalg.norm(v)), 1e-300)


class Memuriyet:

    def __init__(self, nefs, kayip, kume, sozluk: int,
                 ayar: Optional[MeczAyari] = None) -> None:
        self.nefs = nefs
        self.kayip = kayip
        self.kume = list(kume)
        self._onceki_psi = None
        self._seyir: List[float] = []
        self.sozluk = int(sozluk)
        self.ayar = ayar or MeczAyari()
        self._r_duzeltme = 0.0

    def _harman_yeri(self, q) -> Tuple[int, int]:
        from nefs.melekeler import QParametre, harman_anahtari
        p = self.nefs.p
        assert isinstance(p, QParametre), (
            "mecz harman yazmacını QParametre defterinden okur; "
            "%s verildi" % type(p).__name__)
        anahtar, _n = harman_anahtari(q, self.nefs.ayar)
        assert anahtar in p._yer, (
            "harman yazmacı defterde YOK: %r -- harman bu lifle hiç "
            "koşmamış olabilir (ferman 2-P). Defterdekiler: %r"
            % (anahtar, sorted(k for k in p._yer
                               if k.startswith("harman/"))[:4]))
        bas, kac = p._yer[anahtar]
        kademe = max(1, int(getattr(self.nefs.ayar,
                                    "harman_kademesi", 1)))
        kullanilan = kademe * len(uretecler(q))
        assert kullanilan <= int(kac), (
            "harman fiilî lifte %d açı ister, yazmaçta %d var"
            % (kullanilan, int(kac)))
        assert int(bas) + kullanilan <= int(self.nefs.p._n), (
            "harman yazmacı parametre vektörünün dışına taşıyor: "
            "%d+%d > %d" % (int(bas), kullanilan, int(self.nefs.p._n)))
        return int(bas), int(kullanilan)

    def _durum(self, p: np.ndarray):
        from nefs.qegitim import belirtecleri_kodla, ornek_bol
        self.nefs.yukle(np.asarray(p, float))
        bag = ornek_bol(self.kume[0])[0]
        E = belirtecleri_kodla(list(bag), self.nefs.ayar.veri_lifi,
                               self.nefs.ayar.veri_lifi)
        return self.nefs.idrak_et(E), [int(ornek_bol(o)[1])
                                       for o in self.kume]

    def divan(self, p: np.ndarray, keyf: float) -> Dict[str, Any]:
        from .senet_egimi import (egim_ek_durum, egim_ikiz, egim_uretec,
                                  mutabakat, senet_kapsami,
                                  senet_ileri_sadakati)
        n_par = int(np.asarray(p, float).size)
        from nefs.qyazmac import SENET_ACIK
        self.nefs.yukle(np.asarray(p, float))
        from nefs.qegitim import belirtecleri_kodla, ornek_bol
        bag = ornek_bol(self.kume[0])[0]
        E = belirtecleri_kodla(list(bag), self.nefs.ayar.veri_lifi,
                               self.nefs.ayar.veri_lifi)
        _eski = bool(SENET_ACIK[0])
        SENET_ACIK[0] = True
        try:
            q = self.nefs.idrak_et(E)
        finally:
            SENET_ACIK[0] = _eski
        iz = q.y.iz
        lif = tuple(int(x) for x in q.y.ayar.lif)
        hedefler = [int(ornek_bol(o)[1]) for o in self.kume]
        H = hata_operatoru(q, hedefler, int(self.nefs.ayar.veri_lifi))
        psi = np.asarray(q.y.psi, complex)
        ck = cukur(psi, H, onceki=self._onceki_psi)
        self._onceki_psi = psi.copy()
        self._seyir.append(float(ck["⟨H⟩"]))
        if len(self._seyir) > 64:
            del self._seyir[:-64]

        g_ek, metrik = egim_ek_durum(iz, lif, psi, H, n_par)
        g_ur = egim_uretec(iz, lif, psi, H, n_par)
        kap = senet_kapsami(iz, n_par)
        _MECZ["kapı"] = float(kap["kapı"])
        _MECZ["kapsanan_parametre"] = float(kap["kapsanan_parametre"])
        _MECZ["toplam_parametre"] = float(kap["toplam_parametre"])
        _MECZ["üretecsiz"] = float(kap["üretecsiz"])
        _MECZ["durum_saklaması"] = float(kap["durum_saklaması"])
        _MECZ["eğim_normu"] = float(np.linalg.norm(g_ek))
        _MECZ["iz_g"] = float(metrik.sum())

        dv = duvar(metrik)
        maske = np.asarray(dv["maske"], float)
        r = yaricap(float(keyf), float(_MECZ["iz_g"]),
                    seyir=self._seyir)
        yon = -g_ek * maske
        nrm = float(np.linalg.norm(yon))
        if ck["durak"] or nrm <= 1e-300:
            _MECZ["çukur"] += 1.0
            yon = (vadi(metrik, maske) if not ck["durak"]
                   else nakil(q, maske))
            nrm = float(np.linalg.norm(yon))
        if nrm > 0.0:
            yon = yon / nrm
        ikz = egim_ikiz(iz, lif, psi, H, yon)
        mt = mutabakat(g_ur, g_ek, ikz, yon)
        _MECZ["senet_ileri"] = float(senet_ileri_sadakati(iz, lif, psi))
        _MECZ["ek_durum_ikiz_farkı"] = float(mt["ek_durum_ikiz_farkı"])
        _MECZ["üreteç_ikiz_farkı"] = float(mt["üreteç_ikiz_farkı"])
        iz.senedi_kapat()
        return {"yön": yon, "yarıçap": r, "ΔE": ck["ΔE"], "eğim": g_ek,
                "metrik": metrik, "⟨H⟩": ck["⟨H⟩"], "duvar": dv,
                "mutabakat": mt, "durak": ck["durak"]}

    def kademeye_yay(self, yon: np.ndarray, kac: int) -> np.ndarray:
        y = np.asarray(yon, float).reshape(-1)
        assert y.size > 0 and int(kac) % y.size == 0, (
            "harman yazmacı %d açı tutuyor, üreteç sayısı %d -- ikisi "
            "kademe katı olmalı (ferman 5: sessiz atlama yok)"
            % (int(kac), y.size))
        kademe = int(kac) // y.size
        return np.tile(y, kademe) / np.sqrt(float(kademe))

    def kos(self, p0: np.ndarray) -> Dict[str, Any]:
        from nefs.keyfiyet import keyfiyet_beyani
        p = np.asarray(p0, float).copy()
        _MECZ["toplam_parametre"] = float(p.size)
        v = float(np.atleast_1d(self.kayip(p[None, :]))[0])
        _MECZ["çağrı"] += 1.0
        seyir: List[Dict[str, float]] = [{"V": v}]
        for _t in range(max(1, int(self.ayar.tur))):
            _MECZ["tur"] += 1.0
            keyf = float((keyfiyet_beyani() or {}).get("en_iyi", 0.0)) or 1.0
            d = self.divan(p, keyf)
            yon = np.asarray(d["yön"], float)
            assert yon.size == p.size, (
                "yön %d, parametre %d -- boy tutmuyor"
                % (yon.size, p.size))
            if float(np.linalg.norm(yon)) <= 0.0:
                _MECZ["yönsüz_tur"] += 1.0
                continue
            r = float(self._r_duzeltme if self._r_duzeltme > 0.0
                      else d["yarıçap"])
            egim_yon = float(np.dot(np.asarray(d["eğim"], float), yon))
            aday = p + r * yon
            va = float(np.atleast_1d(self.kayip(aday[None, :]))[0])
            _MECZ["çağrı"] += 1.0
            eg = hat_egriligi(va - v, egim_yon * r, r)
            seyir.append({"V": va, "yarıçap": r, "ΔE": float(d["ΔE"]),
                          "κ": float(eg["κ"])})
            if va < v:
                _MECZ["kabul"] += 1.0
                _MECZ["adım_normu"] += float(np.linalg.norm(aday - p))
                p, v = aday, va
                self._r_duzeltme = 0.0
            else:
                self._r_duzeltme = float(eg["yarıçap*"])
                _MECZ["yarıçap_düzeltmesi"] += 1.0
        return {"p": p, "V_son": v, "seyir": seyir}


def mecz_egit(nefs, kayip, p0: np.ndarray, kume: Sequence,
              sozluk: int = 0,
              ayar: Optional[MeczAyari] = None) -> Dict[str, Any]:
    return Memuriyet(nefs, kayip, kume, int(sozluk), ayar).kos(p0)


def mecz_beyani() -> Dict[str, float]:
    b = dict(_MECZ)
    b["tarama"] = b["tur"]
    b["kabul_nispeti"] = (b["kabul"] / b["tur"]) if b["tur"] else 0.0
    b["çağrı_başına_tur"] = (b["tur"] / b["çağrı"]) if b["çağrı"] else 0.0
    b["kapsam"] = ((b["kapsanan_parametre"] / b["toplam_parametre"])
                   if b["toplam_parametre"] else 0.0)
    b["duvar_nispeti"] = ((b["duvar_elenen"] / b["duvar_bakılan"])
                          if b["duvar_bakılan"] else 0.0)
    return b


def mecz_metni(b: Optional[Dict[str, float]] = None) -> str:
    b = b or mecz_beyani()
    s = ["=== MECZ -- BEŞ MEMURİYET (ferman 2-P) ===", "",
         "  tur / kayıp çağrısı : %d / %d   (tur başına %s çağrı)"
         % (int(b["tur"]), int(b["çağrı"]),
            ("%.2f" % (b["çağrı"] / b["tur"])) if b["tur"] else "—"),
         "  kabul               : %d / %d   (%.1f%%)"
         % (int(b["kabul"]), int(b["tur"]), 100.0 * b["kabul_nispeti"]),
         "  adım normu toplamı  : %.4e" % b["adım_normu"],
         "",
         "  EĞİM   ‖analitik eğim‖ = %.4e   (0 kayıp çağrısı)"
         % b["eğim_normu"],
         "  ÇUKUR  ΔE = %.4e   durak sayısı = %d"
         % (b["ΔE"], int(b["çukur"])),
         "         Grassmann asal açısı = %.4e   (hâl kıpırdadı mı --"
         " Karar 14/1)" % b["asal_açı"],
         "  DUVAR  elenen %d / %d koordinat (%.1f%%)"
         % (int(b["duvar_elenen"]), int(b["duvar_bakılan"]),
            100.0 * b["duvar_nispeti"]),
         "  VADİ   %d kere aşırdı" % int(b["vadi"]),
         "  NAKİL  %d kere sıçrattı" % int(b["nakil"]),
         "         DİZİNİN genliğinden WKB geçirgenliği T = %.4e"
         % b["nakil_geçirgenliği"],
         "         (tek belirteç DEĞİL, %d basamaklık dizinin tamamı --"
         " ferman 1-N-B)" % int(b["nakil_dizi_boyu"]),
         "  YARIÇAP = keyfiyet / √iz(g_FS) = %.4e   (iz g = %.4e)"
         % (b["yarıçap"], b["iz_g"]),
         "         hat eğriliği κ = %.4e   %d kere düzeltti"
         % (b["κ"], int(b["yarıçap_düzeltmesi"])),
         "         seyrin B-spline bükülme enerjisi = %.4e"
         "   (adım boyu ondan kısılır -- Karar 11)" % b["eğrilik"],
         "",
         "  SENET  %d kapı · üretecsiz bağ %d · durum saklaması %d"
         % (int(b["kapı"]), int(b["üretecsiz"]),
            int(b["durum_saklaması"])),
         "         ileri oynatma sadakati %.3e  (senet TAM mı)"
         % b["senet_ileri"],
         "  MUTABAKAT  ek_durum↔ikiz = %.3e   (ikisi de TAM olmalı)"
         % b["ek_durum_ikiz_farkı"],
         "             üreteç↔ikiz   = %.3e   (derinlik körlüğünün bedeli)"
         % b["üreteç_ikiz_farkı"],
         "",
         "  operatörlü kefe   : %d  (yönü kurar)" % int(b["operatörlü_kefe"]),
         "  operatörsüz kefe  : %d  (yönü kurmaz, HÜKMÜ verir)"
         % int(b["operatörsüz_kefe"]),
         "  eğimin kapsadığı  : %d / %d parametre (%.2f%%)"
         % (int(b["kapsanan_parametre"]), int(b["toplam_parametre"]),
            100.0 * b["kapsam"])]
    return "\n".join(s)
