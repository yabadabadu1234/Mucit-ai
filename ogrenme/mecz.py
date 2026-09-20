from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["MeczAyari", "Memuriyet", "hata_operatoru", "uretecler",
           "cukur", "yaricap", "vadi", "nakil",
           "mecz_egit", "mecz_beyani", "mecz_metni", "mecz_sifirla",
           "yetim_bloklar", "adres_beyani"]


_MECZ: Dict[str, float] = {}
_YETIM: List[Tuple[int, str]] = []
_ADRES: Dict[str, Any] = {}


def adres_beyani() -> Dict[str, Any]:
    return dict(_ADRES)


def yetim_bloklar() -> List[Tuple[int, str]]:
    return list(_YETIM)


def mecz_sifirla() -> None:
    _MECZ.clear()
    _MECZ.update({"çağrı": 0.0, "tur": 0.0, "kabul": 0.0,
                  "ölü_adım": 0.0, "diri_adım": 0.0,
                  "p_duyarlılığı": 0.0,
                  "ölü_adım": 0.0, "diri_adım": 0.0,
                  "p_duyarlılığı": 0.0,
                  "adım_normu": 0.0, "eğim_normu": 0.0,
                  "kapsanan_parametre": 0.0, "toplam_parametre": 0.0,
                  "sıralanan": 0.0, "en_dar_sıra": 0.0,
                  "çukur": 0.0, "vadi": 0.0, "nakil": 0.0,
                  "ΔE": 0.0, "yarıçap": 0.0, "iz_g": 0.0,
                  "operatörlü_kefe": 0.0, "operatörsüz_kefe": 0.0,
                  "κ": 0.0, "yarıçap_düzeltmesi": 0.0,
                  "asal_açı": 0.0, "eğrilik": 0.0,
                  "nakil_geçirgenliği": 0.0, "nakil_dizi_boyu": 0.0,
                  "nakil_zinciri": 0.0, "nakil_dagilimi": 0.0,
                  "yönsüz_tur": 0.0, "kapı": 0.0, "üretecsiz": 0.0,
                  "bağ_reddi": 0.0,
                  "ek_durum_ikiz_farkı": 0.0, "üreteç_ikiz_farkı": 0.0,
                  "senet_ileri": 0.0,
                  "keyfiyet": 0.0, "keyfiyet_önceki": 0.0,
                  "keyfiyet_düşüşü": 0.0, "hissedilmeyen_adım": 0.0,
                  "kayıp_çözünürlüğü": 0.0, "r_kullanılan": 0.0,
                  "ΔV_gerçek": 0.0, "ΔV_lineer": 0.0,
                  "tahsis_edilen": 0.0,
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


def hat_egriligi(dv_gercek: float, dv_lineer: float,
                 r: float, v_olcegi: float = 0.0) -> Dict[str, float]:
    r = float(r)
    assert r > 0.0 and r * r > 0.0, (
        "yarıçap eğrilik için fazla küçük (r=%r, r²=%r): karesi taban "
        "altına düşüyor" % (r, r * r))
    cozunurluk = float(np.finfo(float).eps) * abs(float(v_olcegi))
    _MECZ["kayıp_çözünürlüğü"] = cozunurluk
    if (abs(float(dv_gercek)) <= cozunurluk
            or abs(float(dv_lineer)) <= cozunurluk):
        _MECZ["hissedilmeyen_adım"] += 1.0
        _MECZ["κ"] = 0.0
        return {"κ": 0.0, "yarıçap*": 0.0, "hissedilmedi": True,
                "bükey": False}
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


def yaricap(iz_g: float,
            seyir: Optional[Sequence[float]] = None) -> float:
    r = 1.0 / float(np.sqrt(max(float(iz_g), 1e-300)))
    egrilik = 0.0
    if seyir is not None and len(seyir) >= 4:
        from .izgara import bukulme_dizeyi, bukulme_enerjisi, duzenli_uydur
        y = np.asarray(list(seyir), float).reshape(-1)
        t = np.linspace(-1.0, 1.0, y.size)
        G, k = max(4, min(8, y.size - 2)), 3
        u = duzenli_uydur(t, y, G, k)
        S = bukulme_dizeyi(G, k)
        c = np.asarray(u["c"], float).reshape(-1)
        buk = abs(float(bukulme_enerjisi(c, S)))
        artik = float(u["artık"]) ** 2
        egrilik = buk / max(buk + artik, 1e-300)
        _MECZ["eğrilik"] = egrilik
        r = r / (1.0 + egrilik)
    assert r > 0.0 and np.isfinite(r), (
        "YARIÇAP SIFIR YAHUT SONSUZ (%r): iz(g) %.6e, eğrilik nispeti "
        "%.6f. Sıfır yarıçapla adım atılamaz ve sessizce geçilemez "
        "(ferman 5)." % (r, float(iz_g), egrilik))
    _MECZ["yarıçap"] = r
    return r


def vadi(metrik: np.ndarray, maske: np.ndarray) -> np.ndarray:
    m = np.asarray(metrik, float) * np.asarray(maske, float)
    v = np.zeros_like(m)
    if m.size and float(m.max()) > 0.0:
        v[int(np.argmax(m))] = 1.0
    _MECZ["vadi"] += 1.0
    return v




def _zincir(s: np.ndarray, kac: int) -> np.ndarray:
    a = np.asarray(s, float)
    sira = np.argsort(a)[::-1][:max(int(kac), 2)]
    d = a[sira]
    orta = float(np.median(d))
    sap = float(np.median(np.abs(d - orta)))
    if not (sap > 0.0):
        return sira[:min(2, sira.size)]
    tut = sira[d > orta + sap]
    return tut if tut.size >= 2 else sira[:min(2, sira.size)]


def nakil(q, metrik: np.ndarray, maske: np.ndarray) -> np.ndarray:
    from nefs.ara import ara
    s = np.asarray(metrik, float) * np.asarray(maske, float)
    v = np.zeros_like(s)
    _MECZ["nakil"] += 1.0
    if not s.size or float(s.max()) <= 0.0:
        return v
    psi = np.asarray(q.y.psi, complex)
    dizi = np.abs(psi.reshape(psi.shape[0], -1)).sum(axis=0)
    tepe = max(float(dizi.max()), 1e-300)
    kuyu = -dizi / tepe
    bedel = ara(ne="bedel", V=kuyu, E=float(kuyu.mean()),
                genislikler=(1, 2, 4, 8))
    gecirgen = max((float(d["T"]) for d in bedel), default=0.0)
    _MECZ["nakil_geçirgenliği"] = gecirgen
    _MECZ["nakil_dizi_boyu"] = float(dizi.size)
    kac = int(min(max(1, round(gecirgen * float(s.size))), s.size))
    yer = _zincir(s, kac)
    m = int(yer.size)
    dd = np.asarray(s, float)[yer]
    pot = -dd / max(float(np.abs(dd).max()), 1e-300)
    H_kuyu = np.diag(pot.astype(complex))
    H_atlama = np.zeros((m, m), complex)
    if m > 1:
        j = np.arange(m - 1)
        H_atlama[j, j + 1] = 1.0
        H_atlama[j + 1, j] = 1.0
    from kuantum.devre import evrim
    U = evrim(H_kuyu, H_atlama, math.pi * gecirgen)
    psi0 = np.zeros(m, complex)
    psi0[0] = 1.0
    agirlik = np.abs(U @ psi0) ** 2
    _MECZ["nakil_zinciri"] = float(m)
    _MECZ["nakil_dagilimi"] = float(
        -np.sum(agirlik[agirlik > 0] * np.log(agirlik[agirlik > 0])))
    for i, w in zip(yer, agirlik):
        v[int(i)] = float(w)
    n = float(np.linalg.norm(v))
    return v / n if n > 0.0 else v


def _kabul_mizan_kefesi(v_yeni: float, v_eski: float,
                        keyf_yeni: float, keyf_eski: float) -> bool:
    if v_yeni < v_eski:
        return True
    if v_yeni == v_eski and keyf_yeni > keyf_eski:
        return True
    return False


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
        from nefs.melekeler import harman_anahtari
        p = self.nefs.p
        assert hasattr(p, "defter") and hasattr(p, "al"), (
            "mecz harman açısını parametre yazmacından okur; "
            "%s verildi (ferman 2-R)" % type(p).__name__)
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
        from kuantum.qegitim import belirtecleri_kodla, ornek_bol
        self.nefs.yukle(np.asarray(p, float))
        bag = ornek_bol(self.kume[0])[0]
        E = belirtecleri_kodla(list(bag), self.nefs.ayar.veri_lifi,
                               self.nefs.ayar.veri_lifi)
        return self.nefs.idrak_et(E), [int(ornek_bol(o)[1])
                                       for o in self.kume]

    def divan(self, p: np.ndarray) -> Dict[str, Any]:
        from .senet_egimi import (egim_ek_durum, egim_ikiz, egim_uretec,
                                  mahalli_beyani_egim as _mh_beyan,
                                  mahalli_egimi, mutabakat,
                                  senet_kapsami, senet_ileri_sadakati)
        n_par = int(np.asarray(p, float).size)
        from kuantum.qyazmac import SENET_ACIK
        self.nefs.yukle(np.asarray(p, float))
        from kuantum.qegitim import belirtecleri_kodla, ornek_bol
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
        _ADRES.clear()
        _ADRES.update(q.y.adres_beyani())
        _ADRES["lif"] = tuple(int(x) for x in q.y.ayar.lif)
        _ADRES["bağlam"] = int(np.asarray(bag).size)
        from kuantum.parametre_yazmaci import parametre_beyani
        _pq = parametre_beyani(getattr(self.nefs, "pq", None))
        _ADRES["p_qudit"] = _pq.get("qudit", 0)
        _ADRES["p_taban"] = _pq.get("taban", 0)
        _ADRES["p_mahallî"] = _pq.get("mahallî_serbestlik", 0)
        from kuantum.nqs import nqs_beyani
        _k = nqs_beyani(getattr(self.nefs, "kan", None))
        _ADRES["kan_katsayı"] = _k.get("katsayı", 0)
        _ADRES["kan_qudit"] = _k.get("qudit", 0)
        _ADRES["kan_parametre"] = _k.get("parametre", 0)
        _ADRES["kan_KB"] = round(_k.get("katsayı_bayt", 0) / 1e3, 1)
        _ADRES["bellek_MB"] = round(
            _pq.get("ölçülen_bellek", 0) / 1e6, 1)
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
        g_mh, m_mh = mahalli_egimi(
            iz, getattr(self.nefs, "mahalli", None), H,
            int(getattr(q.y, "cephe", 0)), n_par)
        g_ek = g_ek + g_mh
        g_ur = g_ur + g_mh
        metrik = metrik + m_mh
        _MECZ["mahallî_bağ"] = float(_mh_beyan()["bağ"])
        _MECZ["mahallî_kapsanan"] = float(_mh_beyan()["kapsanan"])
        _MECZ["mahallî_eğim_normu"] = float(_mh_beyan()["norm"])
        kap = senet_kapsami(
            iz, n_par, defter=(self.nefs.p.defter()
                               if hasattr(self.nefs.p, "defter") else None),
            tahsis=2 * sum(int(k) for _b, k in
                           (self.nefs.p.defter() or {}).values()),
            kaydirma=int(getattr(self.nefs.p, "d", 0)))
        _YETIM[:] = list(kap.get("yetim", ()))[:6]
        _MECZ["kapı"] = float(kap["kapı"])
        _MECZ["kapsanan_parametre"] = float(kap["kapsanan_parametre"])
        _MECZ["toplam_parametre"] = float(kap["toplam_parametre"])
        _MECZ["tahsis_edilen"] = float(kap["tahsis_edilen"])
        _MECZ["üretecsiz"] = float(kap["üretecsiz"])
        _MECZ["bağ_reddi"] = float(kap.get("bağ_reddi", 0))
        _MECZ["durum_saklaması"] = float(kap["durum_saklaması"])
        _MECZ["eğim_normu"] = float(np.linalg.norm(g_ek))
        _MECZ["iz_g"] = float(metrik.sum())

        sira = np.asarray(metrik, float)
        sira = sira / max(float(sira.max()), 1e-300)
        _MECZ["sıralanan"] = float(sira.size)
        _MECZ["en_dar_sıra"] = float(sira.min()) if sira.size else 0.0
        r = yaricap(float(_MECZ["iz_g"]), seyir=self._seyir)
        yon = -g_ek * sira
        nrm = float(np.linalg.norm(yon))
        if ck["durak"] or nrm <= 1e-300:
            _MECZ["çukur"] += 1.0
            yon = (vadi(metrik, sira) if not ck["durak"]
                   else nakil(q, metrik, sira))
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
                "metrik": metrik, "⟨H⟩": ck["⟨H⟩"], "sıra": sira,
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
        from nefs.keyfiyet import keyfiyet_son
        p = np.asarray(p0, float).copy()
        _MECZ["toplam_parametre"] = float(p.size)
        v = float(np.atleast_1d(self.kayip(p[None, :]))[0])
        _MECZ["çağrı"] += 1.0
        seyir: List[Dict[str, float]] = [{"V": v}]
        keyf = keyfiyet_son()
        for _t in range(max(1, int(self.ayar.tur))):
            _MECZ["tur"] += 1.0
            d = self.divan(p)
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
            keyf_aday = keyfiyet_son()
            _MECZ["r_kullanılan"] = r
            _MECZ["ΔV_gerçek"] = float(va - v)
            _MECZ["ΔV_lineer"] = float(egim_yon * r)
            if va == v:
                _MECZ["ölü_adım"] += 1.0
            else:
                _MECZ["diri_adım"] += 1.0
            _MECZ["p_duyarlılığı"] = float(abs(va - v))
            eg = hat_egriligi(va - v, egim_yon * r, r, max(abs(v), abs(va)))
            seyir.append({"V": va, "yarıçap": r, "ΔE": float(d["ΔE"]),
                          "κ": float(eg["κ"]), "keyfiyet": keyf_aday})
            _MECZ["keyfiyet"] = float(keyf_aday)
            _MECZ["keyfiyet_önceki"] = float(keyf)
            if keyf_aday < keyf:
                _MECZ["keyfiyet_düşüşü"] += 1.0
            kabul_edildi = _kabul_mizan_kefesi(va, v, keyf_aday, keyf)
            if kabul_edildi:
                _MECZ["kabul"] += 1.0
                _MECZ["adım_normu"] += float(np.linalg.norm(aday - p))
                p, v, keyf = aday, va, keyf_aday
                self._r_duzeltme = 0.0
            else:
                self._r_duzeltme = (0.0 if eg.get("hissedilmedi")
                                    else float(eg["yarıçap*"]))
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
    b["kapsam"] = ((b["kapsanan_parametre"] / b["tahsis_edilen"])
                   if b.get("tahsis_edilen") else 0.0)
    _adim = b["ölü_adım"] + b["diri_adım"]
    b["ölü_adım_nispeti"] = (b["ölü_adım"] / _adim) if _adim else 0.0
    b["kayıp_p_den_bağımsız"] = bool(_adim > 0.0
                                     and b["diri_adım"] <= 0.0)
    return b


def mecz_metni(b: Optional[Dict[str, float]] = None) -> str:
    b = b or mecz_beyani()
    _kirmizi = []
    if b.get("kayıp_p_den_bağımsız"):
        _kirmizi = [
            "  ✗ KIRMIZI -- KAYIP PARAMETREDEN BAĞIMSIZ (ferman 5):",
            "    %d adımın %d'i ölü; V(p+rδ) == V(p) BİT BİT AYNI."
            % (int(b["ölü_adım"] + b["diri_adım"]), int(b["ölü_adım"])),
            "    Son ölçülen duyarlılık |ΔV| = %.3e"
            % float(b.get("p_duyarlılığı", 0.0)),
            "    Sebebi ölçüldü: θ_cartan KAN üssüne satır başına TEK"
            " SKALER olarak girer (küresel ayar fazı, ferman 2-Â);",
            "    kaybın bütün terimleri (ρ = M·M†, Re⟨ψ|D|ψ⟩, örtüşme)"
            " küresel faz altında DEĞİŞMEZDİR.",
            "    Bu kanalın kaybı değiştirmesi riyazî olarak"
            " imkânsızdır -- öğrenme o kanattan gelemez.",
            ""]
    return "\n".join(_kirmizi + [_mecz_govde(b)])


def _mecz_govde(b: Dict[str, float]) -> str:
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
         "  DUVAR İLGA EDİLDİ (ferman 1-Ğ): eleme yok, %d koordinat"
         " yalnız SIRALANDI; en dar sıra %.6e"
         % (int(b.get("sıralanan", 0)), b.get("en_dar_sıra", 0.0)),
         "  VADİ   %d kere aşırdı" % int(b["vadi"]),
         "  NAKİL  %d kere sıçrattı" % int(b["nakil"]),
         "         DİZİNİN genliğinden WKB geçirgenliği T = %.4e"
         % b["nakil_geçirgenliği"],
         "         (tek belirteç DEĞİL, %d basamaklık dizinin tamamı --"
         " ferman 1-N-B)" % int(b["nakil_dizi_boyu"]),
         "         SIÇRAMA ZARDAN DEĞİL EVRİMDEN (ferman 2-Ĵ): kuyu ile",
         "         atlama üreteçleri birbiriyle değişmez; sıçrama, %d"
         " halkalı" % int(b.get("nakil_zinciri", 0)),
         "         zincirde Trotter-Suzuki tünelleme evriminin vardığı",
         "         yerdir. Varış dağılımının entropisi %.4f -- sıfıra"
         % b.get("nakil_dagilimi", 0.0),
         "         yakınsa sıçrama tek koordinata çökmüş demektir.",
         "  YARIÇAP = 1 / √iz(g_FS) = %.4e   (iz g = %.4e)"
         % (b["yarıçap"], b["iz_g"]),
         "         keyfiyet yarıçabı NE ÇARPAR NE BÖLER: adımın BOYUNU",
         "         mecz tayin eder, KABULÜNÜ mizan verir.",
         "  KABUL KAPISI  keyfiyet %.6f → %.6f   (%d adımda keyfiyet"
         " düştü -- VETO YOK, keyfiyet mizanda kefedir, ferman 2-Ü)"
         % (b["keyfiyet_önceki"], b["keyfiyet"],
            int(b["keyfiyet_düşüşü"])),
         "         hat eğriliği κ = %.4e   %d kere düzeltti"
         % (b["κ"], int(b["yarıçap_düzeltmesi"])),
         "         HİSSEDİLMEYEN ADIM %d kere: |ΔV| kaybın kendi"
         " çözünürlüğünün (%.3e) altında kaldı."
         % (int(b["hissedilmeyen_adım"]), b["kayıp_çözünürlüğü"]),
         "         Hudut sabit sayı değil, kaybın büyüklüğünden ölçülür",
         "         (ferman 1-J). Bu bir eğrilik değil küçüklük delilidir; yarıçap",
         "         yarıya inmez, İKİYE KATLANIR. Sayı büyükse kayıp",
         "         adımı hissetmiyor demektir (ferman 5).",
         "         seyrin B-spline bükülme enerjisi = %.4e"
         "   (adım boyu ondan kısılır -- Karar 11)" % b["eğrilik"],
         "",
         "  SENET  %d kapı · üretecsiz bağ %d · REDDEDİLEN bağ %d"
         " · durum saklaması %d"
         % (int(b["kapı"]), int(b["üretecsiz"]),
            int(b.get("bağ_reddi", 0)), int(b["durum_saklaması"])),
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
         "  eğimin kapsadığı  : %d / %d tahsis edilen serbestlik (%.2f%%)"
         % (int(b["kapsanan_parametre"]), int(b.get("tahsis_edilen", 0)),
            100.0 * b["kapsam"])]
    return "\n".join(s)
