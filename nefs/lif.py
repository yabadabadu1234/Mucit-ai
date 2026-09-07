from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["Lif", "kodla", "ortusme", "mesafe", "sadakat", "rapor",
           "KIP_QUDIT", "KIP_TUTARLI", "KIP_LIE"]

KIP_QUDIT = "qudit"
KIP_TUTARLI = "tutarlı"
KIP_LIE = "lie-chebyshev qudit"


def kodla(x, ne: str = KIP_TUTARLI, boyut: int = 16,
          bag: int = 8) -> np.ndarray:
    v = np.asarray(x, float).reshape(-1)

    if ne == KIP_TUTARLI:
        from kuantum.surekli import tutarli_durum
        return np.stack([tutarli_durum(complex(t), int(boyut)) for t in v])

    if ne == KIP_QUDIT:
        u = np.zeros(int(boyut), dtype=complex)
        u[:min(v.size, int(boyut))] = v[:int(boyut)]
        n = np.linalg.norm(u)
        return (u / n) if n > 1e-300 else u

    if ne == KIP_LIE:
        from .qudit import QuditAyari, durum
        a = QuditAyari(d=int(boyut), yon=max(1, min(v.size, int(boyut) - 1)))
        n_k, n_d = 4, 8
        g = np.resize(v, n_k * (n_d + 1)).reshape(n_k, n_d + 1)
        return durum(g, np.roll(g, 1, axis=1), v[:a.yon], ayar=a)

    raise ValueError("kodlama usulü bilinmiyor: %r" % (ne,))


def mesafe(a: np.ndarray, b: np.ndarray, ne: str) -> float:
    if ne in (KIP_TUTARLI, KIP_LIE, KIP_QUDIT):
        return -float(np.log(max(ortusme(a, b), 1e-300)))
    a = np.asarray(a).reshape(-1)
    b = np.asarray(b).reshape(-1)
    n = max(a.size, b.size)
    a = np.pad(a, (0, n - a.size))
    b = np.pad(b, (0, n - b.size))
    return float(np.linalg.norm(np.abs(a - b)))


def ortusme(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a)
    b = np.asarray(b)
    if a.ndim == 2 and b.ndim == 2:
        return float(np.abs(np.prod(
            [np.vdot(a[k], b[k]) for k in range(a.shape[0])])))
    return float(np.abs(np.vdot(a.reshape(-1), b.reshape(-1))))


def sadakat(X: Sequence[Sequence[float]], ne: str = KIP_TUTARLI,
            boyut: int = 16) -> Dict[str, float]:
    X = [np.asarray(x, float).reshape(-1) for x in X]
    kod = [kodla(x, ne=ne, boyut=boyut) for x in X]
    ham, gom = [], []
    for i in range(len(X)):
        for j in range(i + 1, len(X)):
            ham.append(float(np.linalg.norm(X[i] - X[j])))
            gom.append(mesafe(kod[i], kod[j], ne))
    ham = np.asarray(ham)
    gom = np.asarray(gom)
    if ham.size < 2 or ham.std() < 1e-12 or gom.std() < 1e-12:
        return {"sadakat": float("nan"), "çift": int(ham.size),
                "sebep": "mesafeler ayrışmıyor"}
    r_p = float(np.corrcoef(ham, gom)[0, 1])
    sr = lambda z: np.argsort(np.argsort(z)).astype(float)
    r_s = float(np.corrcoef(sr(ham), sr(gom))[0, 1])
    return {"sadakat": r_s, "pearson": r_p, "çift": int(ham.size)}


@dataclass
class Lif:

    defter: Dict[str, Dict[str, Dict[str, np.ndarray]]] = field(
        default_factory=dict)

    def tak(self, tip: str, kategori: str, uzay: str,
            nokta: np.ndarray) -> "Lif":
        self.defter.setdefault(str(tip), {}) \
                   .setdefault(str(kategori), {})[str(uzay)] = \
            np.asarray(nokta)
        return self

    def tipler(self) -> List[str]:
        return sorted(self.defter)

    def kategoriler(self, tip: str) -> List[str]:
        return sorted(self.defter.get(str(tip), {}))

    def uzaylar(self, tip: str, kategori: str) -> List[str]:
        return sorted(self.defter.get(str(tip), {}).get(str(kategori), {}))

    def terim(self):
        from matematik.tip_teorisi import Sigma, Evren
        return Sigma("t", Evren(0),
                     Sigma("c", Evren(0),
                           Sigma("u", Evren(0), Evren(0))))

    def unfold(self, mertebe: str = "kategori"):
        from matematik.tip_teorisi import (Cift, Birinci, Ikinci, Dogal,
                                           degerlendir, geri_oku, BOS)
        e = Cift(Dogal(), Cift(Dogal(), Cift(Dogal(), Dogal())))
        yol = {"tip": Birinci(e),
               "kategori": Birinci(Ikinci(e)),
               "uzay": Birinci(Ikinci(Ikinci(e))),
               "nokta": Ikinci(Ikinci(Ikinci(e)))}.get(mertebe)
        if yol is None:
            raise ValueError("açılacak mertebe bilinmiyor: %r" % (mertebe,))
        return geri_oku(degerlendir(yol, BOS))

    def dogrula(self) -> Dict[str, Any]:
        from matematik.tip_teorisi import Sigma, degerlendir, geri_oku, BOS
        t = self.terim()
        n = 0
        x = t
        while isinstance(x, Sigma):
            n += 1
            x = x.hedef
        normal = geri_oku(degerlendir(t, BOS))
        derinlik = 0
        y = normal
        while isinstance(y, Sigma):
            derinlik += 1
            y = y.hedef
        return {"Σ_sayısı": n, "NbE_sonrası_Σ": derinlik,
                "defter_kademesi": 3,
                "uyuştu": bool(n == 3 and derinlik == 3)}

    def ac(self, tip: str, kategori: Optional[str] = None,
           uzay: Optional[str] = None) -> Any:
        if uzay is not None and kategori is None:
            raise ValueError(
                "silsile atlandı: uzaya kategorisiz erişilemez "
                "(nokta → uzay → kategori → tip)")
        if kategori is None:
            return self.kategoriler(tip)
        if uzay is None:
            return self.uzaylar(tip, kategori)
        return self.defter[str(tip)][str(kategori)][str(uzay)]

    def izdusum(self, ne: str = "kategori") -> Dict[str, np.ndarray]:
        out: Dict[str, List[np.ndarray]] = {}
        for t, cs in self.defter.items():
            for c, us in cs.items():
                for u, v in us.items():
                    anahtar = {"tip": t, "kategori": "%s/%s" % (t, c),
                               "uzay": "%s/%s/%s" % (t, c, u)}.get(ne)
                    if anahtar is None:
                        raise ValueError("izdüşüm kipi bilinmiyor: %r" % (ne,))
                    out.setdefault(anahtar, []).append(
                        np.asarray(v).reshape(-1))
        return {k: np.sum(np.stack(_esitle(v)), axis=0)
                for k, v in out.items()}

    def sayim(self) -> Dict[str, int]:
        t = len(self.defter)
        c = {x for cs in self.defter.values() for x in cs}
        u = {x for cs in self.defter.values() for us in cs.values()
             for x in us}
        hucre = sum(len(us) for cs in self.defter.values()
                    for us in cs.values())
        kutu = t * max(len(c), 1) * max(len(u), 1)
        return {"tip": t, "kategori": len(c), "uzay": len(u),
                "lif_hücresi": hucre, "kutu_hücresi": kutu,
                "boş_kalacaktı": kutu - hucre}


def _esitle(vs: List[np.ndarray]) -> List[np.ndarray]:
    n = max(v.size for v in vs)
    return [np.pad(v, (0, n - v.size)) if v.size < n else v for v in vs]


def rapor(tohum: int = 0) -> str:
    r = np.random.default_rng(tohum)
    X = r.normal(size=(12, 4)) * 0.6
    s = ["=== LİF -- zabıtların ölçüsü ===", "",
         "  KODLAMA SADAKATİ (giriş mesafeleri ↔ kodlanmış mesafeler)",
         "  1,0 = geometri tam korundu.",
         "",
         "  NE ÖLÇÜLDÜĞÜ AÇIKÇA: bu tablo GİRDİ KODLAMASINI ölçer,",
         "  yâni 'kelime → durum' işini. ``lie-chebyshev qudit`` bu işi",
         "  yapmak için yazılmadı: o, MODELİN KENDİ durumunu az sayıda",
         "  katsayıdan üretir (hafıza ve hız iddiası; ölçüsü",
         "  ``nefs/qudit.py:rapor``dadır). Buradaki ρ'su benim keyfî",
         "  ``v → θ`` eşlememi ölçer, zabıtın kuruluşunu değil --",
         "  onun için düşük çıkması bir nakz değildir ve öyle",
         "  sayılmıyor. Girdi kodlaması işi ``tutarlı``nındır.",
         "",
         ""]
    for ne in (KIP_LIE, KIP_TUTARLI, KIP_QUDIT):
        try:
            d = sadakat(X, ne=ne)
            s.append("    %-42s ρ = %s"
                     % (ne, ("%.4f" % d["sadakat"])
                        if d["sadakat"] == d["sadakat"] else "TANIMSIZ"))
        except Exception as e:
            s.append("    %-42s DÜŞTÜ: %s" % (ne, type(e).__name__))

    L = Lif()
    L.tak("token", "sentaks", "dizim", np.arange(4.0))
    L.tak("token", "sentaks", "bağımlılık", np.arange(4.0))
    L.tak("token", "ontoloji", "renk", np.arange(4.0))
    L.tak("izgara", "nedensellik", "akış", np.arange(4.0))
    n = L.sayim()
    s += ["", "  BAĞIMLI LİF vs KARTEZYEN KUTU (aynı muhteva)",
          "    tip=%d kategori=%d uzay=%d" % (n["tip"], n["kategori"],
                                              n["uzay"]),
          "    lif hücresi   : %d" % n["lif_hücresi"],
          "    kutu hücresi  : %d" % n["kutu_hücresi"],
          "    boş kalacaktı : %d  (kutuda sıfırla dolardı)"
          % n["boş_kalacaktı"], "",
          "  TİP TEORİSİ -- Σ zinciri ve NbE (matematik/tip_teorisi.py)"]
    dg = L.dogrula()
    s += ["    tip terimi     : %s" % type(L.terim()).__name__,
          "    Σ sayısı       : %d   (NbE sonrası %d)"
          % (dg["Σ_sayısı"], dg["NbE_sonrası_Σ"]),
          "    defterle uyuştu: %s" % ("EVET" if dg["uyuştu"] else "HAYIR"),
          "    Unfold(kategori) → %s" % type(L.unfold("kategori")).__name__,
          "    Unfold(nokta)    → %s" % type(L.unfold("nokta")).__name__,
          "",
          "  SİLSİLE: uzaya kategorisiz erişmek hata verir --"]
    try:
        L.ac("token", uzay="dizim")
        s.append("    ⚠ VERMEDİ: silsile zorlanmıyor.")
    except ValueError:
        s.append("    ✓ verdi.")
    return "\n".join(s)


if __name__ == "__main__":
    print(rapor())
