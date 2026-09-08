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
                  "operatörlü_kefe": 0.0, "operatörsüz_kefe": 0.0})


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


def cukur(psi: np.ndarray, H: np.ndarray) -> Dict[str, float]:
    p = np.abs(psi) ** 2
    iz = np.maximum(p.sum(axis=1, keepdims=True), 1e-300)
    p = p / iz
    E = float((p * H[None, :]).sum(axis=1).mean())
    E2 = float((p * (H ** 2)[None, :]).sum(axis=1).mean())
    dE = float(np.sqrt(max(0.0, E2 - E * E)))
    _MECZ["ΔE"] = dE
    return {"⟨H⟩": E, "ΔE": dE, "durak": bool(dE <= 1e-12)}


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


def yaricap(keyf: float, iz_g: float) -> float:
    r = float(keyf) / float(np.sqrt(max(float(iz_g), 1e-300)))
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
    if s.size and float(s.max()) > 0.0:
        v[int(np.argmax(s))] = 1.0
    _MECZ["nakil"] += 1.0
    return v


class Memuriyet:

    def __init__(self, nefs, kayip, kume, sozluk: int,
                 ayar: Optional[MeczAyari] = None) -> None:
        self.nefs = nefs
        self.kayip = kayip
        self.kume = list(kume)
        self.sozluk = int(sozluk)
        self.ayar = ayar or MeczAyari()

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
        return int(bas), int(kac)

    def _durum(self, p: np.ndarray):
        from nefs.qegitim import belirtecleri_kodla, ornek_bol
        self.nefs.yukle(np.asarray(p, float))
        bag = ornek_bol(self.kume[0])[0]
        E = belirtecleri_kodla(list(bag), self.nefs.ayar.veri_lifi,
                               self.nefs.ayar.veri_lifi)
        return self.nefs.idrak_et(E), [int(ornek_bol(o)[1])
                                       for o in self.kume]

    def divan(self, p: np.ndarray, keyf: float) -> Dict[str, Any]:
        q, hedefler = self._durum(p)
        H = hata_operatoru(q, hedefler, int(self.nefs.ayar.veri_lifi))
        psi = np.asarray(q.y.psi, complex)
        ck = cukur(psi, H)
        eg = egim(q, H)
        dv = duvar(eg["metrik"])
        r = yaricap(float(keyf), float(_MECZ["iz_g"]))
        bas, kac = self._harman_yeri(q)
        maske = np.asarray(dv["maske"], float)
        yon = -np.asarray(eg["eğim"], float) * maske
        n = float(np.linalg.norm(yon))
        if ck["durak"] or n <= 1e-300:
            _MECZ["çukur"] += 1.0
            yon = (vadi(eg["metrik"], maske) if not ck["durak"]
                   else nakil(q, maske))
            n = float(np.linalg.norm(yon))
        if n > 0.0:
            yon = yon / n
        return {"yön": yon, "yarıçap": r, "ΔE": ck["ΔE"], "başlangıç": bas,
                "kaç": kac, "⟨H⟩": ck["⟨H⟩"], "duvar": dv,
                "durak": ck["durak"]}

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
            bas, kac = int(d["başlangıç"]), int(d["kaç"])
            _MECZ["kapsanan_parametre"] = float(kac)
            yon = self.kademeye_yay(d["yön"], kac)
            assert yon.size == kac, (
                "yön %d, harman yazmacı %d -- boy tutmuyor"
                % (yon.size, kac))
            if float(np.linalg.norm(yon)) <= 0.0:
                _MECZ["yönsüz_tur"] = _MECZ.get("yönsüz_tur", 0.0) + 1.0
                continue
            aday = p.copy()
            aday[bas:bas + kac] = aday[bas:bas + kac] + d["yarıçap"] * yon
            va = float(np.atleast_1d(self.kayip(aday[None, :]))[0])
            _MECZ["çağrı"] += 1.0
            seyir.append({"V": va, "yarıçap": float(d["yarıçap"]),
                          "ΔE": float(d["ΔE"])})
            if va < v:
                _MECZ["kabul"] += 1.0
                _MECZ["adım_normu"] += float(
                    np.linalg.norm(aday - p))
                p, v = aday, va
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
         "  tur / kayıp çağrısı : %d / %d   (tur başına %.2f çağrı)"
         % (int(b["tur"]), int(b["çağrı"]), 1.0 / max(b["çağrı_başına_tur"],
                                                      1e-9)),
         "  kabul               : %d / %d   (%.1f%%)"
         % (int(b["kabul"]), int(b["tur"]), 100.0 * b["kabul_nispeti"]),
         "  adım normu toplamı  : %.4e" % b["adım_normu"],
         "",
         "  EĞİM   ‖analitik eğim‖ = %.4e   (0 kayıp çağrısı)"
         % b["eğim_normu"],
         "  ÇUKUR  ΔE = %.4e   durak sayısı = %d"
         % (b["ΔE"], int(b["çukur"])),
         "  DUVAR  elenen %d / %d koordinat (%.1f%%)"
         % (int(b["duvar_elenen"]), int(b["duvar_bakılan"]),
            100.0 * b["duvar_nispeti"]),
         "  VADİ   %d kere aşırdı" % int(b["vadi"]),
         "  NAKİL  %d kere sıçrattı" % int(b["nakil"]),
         "  YARIÇAP = keyfiyet / √iz(g_FS) = %.4e   (iz g = %.4e)"
         % (b["yarıçap"], b["iz_g"]),
         "",
         "  operatörlü kefe   : %d  (yönü kurar)" % int(b["operatörlü_kefe"]),
         "  operatörsüz kefe  : %d  (yönü kurmaz, HÜKMÜ verir)"
         % int(b["operatörsüz_kefe"]),
         "  eğimin kapsadığı  : %d / %d parametre (%.2f%%)"
         % (int(b["kapsanan_parametre"]), int(b["toplam_parametre"]),
            100.0 * b["kapsam"])]
    return "\n".join(s)
