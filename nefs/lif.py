from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["Lif", "kodla", "ortusme", "mesafe", "sadakat",
           "harita_kur", "lif_kefesi", "lif_beyani",
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
    sozluk: int = 0
    asansor_kati: int = -1
    uzay_mertebesi: Tuple[int, ...] = ()
    kategori_beyani: str = ""
    tur: int = 0
    doyma: float = 0.0
    islenen: int = 0

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
        from matematik.sonsuz_mertebeler_teorisi import Sigma, Evren
        return Sigma("t", Evren(0),
                     Sigma("c", Evren(0),
                           Sigma("u", Evren(0), Evren(0))))

    def unfold(self, mertebe: str = "kategori"):
        from matematik.sonsuz_mertebeler_teorisi import (Cift, Birinci, Ikinci, Dogal,
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
        from matematik.sonsuz_mertebeler_teorisi import Sigma, degerlendir, geri_oku, BOS
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

    def kopukluk(self, ne: str = "uzay") -> Dict[str, Any]:
        izd = self.izdusum(ne)
        adres = sorted(izd)
        nokta = [np.asarray(izd[k], float).reshape(-1) for k in adres]
        if len(nokta) < 2:
            return {"kopuk": 0, "hücre": len(nokta), "nispet": 0.0,
                    "kopuk_adres": (), "sebep": "tek hücre -- münasebet yok"}
        X = np.stack(_esitle(nokta))
        boy = np.maximum(np.linalg.norm(X, axis=1, keepdims=True), 1e-300)
        G = np.abs((X / boy) @ (X / boy).T)
        np.fill_diagonal(G, 0.0)
        komsu = G.max(axis=1)
        esik = float(np.mean(komsu)) * float(np.mean(komsu > 0.0))
        kopuk = [adres[i] for i in np.flatnonzero(komsu <= esik)]
        return {"kopuk": len(kopuk), "hücre": len(adres),
                "nispet": float(len(kopuk)) / float(len(adres)),
                "eşik": esik, "kopuk_adres": tuple(sorted(kopuk)[:8])}

    def hazineye(self) -> Dict[str, Any]:
        return {"defter": {t: {c: {u: [float(x) for x in
                                       np.asarray(v, float).reshape(-1)]
                                   for u, v in us.items()}
                               for c, us in cs.items()}
                           for t, cs in self.defter.items()},
                "sözlük": int(self.sozluk),
                "asansör_katı": int(self.asansor_kati),
                "uzay_mertebesi": [int(m) for m in self.uzay_mertebesi],
                "tur": int(self.tur)}

    @staticmethod
    def hazineden(d: Optional[Dict[str, Any]] = None) -> "Lif":
        d = dict(d or {})
        L = Lif(sozluk=int(d.get("sözlük", 0)),
                asansor_kati=int(d.get("asansör_katı", -1)),
                uzay_mertebesi=tuple(int(m) for m in
                                     d.get("uzay_mertebesi", ())),
                tur=int(d.get("tur", 0)))
        for t, cs in dict(d.get("defter") or {}).items():
            for c, us in dict(cs).items():
                for u, v in dict(us).items():
                    L.tak(t, c, u, np.asarray(list(v), float))
        return L

    def birik(self, tip: str, kategori: str, uzay: str,
             nokta: np.ndarray) -> "Lif":
        eski = self.defter.get(str(tip), {}).get(str(kategori), {}) \
                          .get(str(uzay))
        yeni = np.asarray(nokta, float).reshape(-1)
        if eski is not None:
            a, b = _esitle([np.asarray(eski, float).reshape(-1), yeni])
            yeni = a + b
        return self.tak(tip, kategori, uzay, yeni)

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



def _dinamik_mertebeler(boylar: Sequence[int]) -> Tuple[int, ...]:
    b = sorted({int(x) for x in boylar})
    assert b, "münasebet haritası için bağlam boyu BOŞ"
    n = len(b)
    return tuple(b[min(n - 1, (i * n) // 10)] for i in range(10))


def _yuva_sec(mertebeler: Sequence[int], boy: int) -> int:
    m = np.asarray(list(mertebeler), np.int64)
    return int(np.argmin(np.abs(m - int(boy))))


def harita_kur(nefs, veri, sozluk: int, hendese: Dict[str, Any],
               munasebet, onceki: Optional[Dict[str, Any]] = None) -> Lif:
    from idrak.kategori import kategori_beyani, uzaylari_kur
    from .hendese import (HendeseAyari, hendese_beyani, hendese_yukle,
                          mertebe_sec)
    from .qegitim import ornek_bol

    veri = list(veri)
    assert veri, "silsile defteri BOŞ veriyle kurulamaz"
    n_v = int(nefs.ayar.veri_lifi)
    assert n_v >= 4, (
        "taşıyıcı tabanı %d -- silsile defteri dörtlü kıyas yapamaz" % n_v)
    M = np.asarray(munasebet.M, float)
    assert M.shape == (n_v, n_v), (
        "müşterek münasebet haritası %s, taşıyıcı tabanı %d -- tek kaynak "
        "olmalı (ferman 1-M)" % (M.shape, n_v))
    bolunmus = [ornek_bol(o) for o in veri]
    uzaylar = uzaylari_kur(
        _dinamik_mertebeler([len(b) for b, _h, _c, _m in bolunmus]))
    mertebeler = [u.mertebe for u in uzaylar]
    ha = HendeseAyari(azami_alfabe=n_v, tohum=int(nefs.ayar.tohum))

    L = Lif.hazineden(onceki)
    klon = hendese_beyani()
    for bag, _hedef, cins, _makam in bolunmus:
        dizi = [int(x) % n_v for x in bag] + [n_v - 1]
        tip = "arc" if str(cins).startswith("arc") else "sözlü"
        kategori = "ℓ%d" % int(mertebe_sec(dizi, ha)["ℓ*"])
        uzay = "uzay%02d" % _yuva_sec(mertebeler, len(bag))
        t = np.unique(np.asarray(dizi, np.int64))
        L.birik(tip, kategori, uzay, M[t, :].sum(axis=0))
    hendese_yukle(klon)
    L.asansor_kati = int(hendese["asansör"]["kat"])
    L.sozluk = int(sozluk)
    L.uzay_mertebesi = tuple(int(m) for m in mertebeler)
    L.kategori_beyani = kategori_beyani(uzaylar)
    L.doyma = float(munasebet.doyma())
    L.islenen = int(munasebet.islenen)
    L.tur = int(L.tur) + 1
    return L


def lif_kefesi(haller: Sequence[np.ndarray],
               baglamlar: Sequence[Sequence[int]],
               cozunurluk: int = 16) -> Dict[str, Any]:
    n = min(len(haller), len(baglamlar))
    if n < 3:
        return {"kayıp": 1.0, "çift": 0, "sadakat": float("nan"),
                "sebep": "münasebet için en az üç örnek gerekir"}
    kac = min(n, max(3, int(cozunurluk)))
    sec = np.linspace(0, n - 1, kac).astype(np.int64)
    sec = np.unique(sec)
    H = np.stack(_esitle([np.asarray(haller[i], complex).reshape(-1)
                          for i in sec]))
    X = np.stack(_esitle([np.asarray(baglamlar[i], float).reshape(-1)
                          for i in sec]))
    H = H / np.maximum(np.linalg.norm(H, axis=1, keepdims=True), 1e-300)
    G = np.abs(H @ H.conj().T)
    D_gom = -np.log(np.maximum(G, 1e-300))
    kare = np.sum(X * X, axis=1)
    D_ham = np.sqrt(np.maximum(
        kare[:, None] + kare[None, :] - 2.0 * (X @ X.T), 0.0))
    ust = np.triu_indices(sec.size, k=1)
    h = D_ham[ust]
    g = D_gom[ust]
    if h.size < 2 or h.std() < 1e-12 or g.std() < 1e-12:
        return {"kayıp": 1.0, "çift": int(h.size), "sadakat": float("nan"),
                "örnek": int(sec.size),
                "sebep": "mesafeler ayrışmıyor -- durum örnekleri ayırmıyor"}
    sr = lambda z: np.argsort(np.argsort(z)).astype(float)
    r_s = float(np.corrcoef(sr(h), sr(g))[0, 1])
    return {"kayıp": float(1.0 - r_s), "sadakat": r_s,
            "pearson": float(np.corrcoef(h, g)[0, 1]),
            "çift": int(h.size), "örnek": int(sec.size),
            "çözünürlük": int(cozunurluk)}


def lif_beyani(lif: Lif) -> str:
    n = lif.sayim()
    k = lif.kopukluk()
    dg = lif.dogrula()
    s = ["=== SİLSİLE DEFTERİ -- MÜŞTEREK HARİTANIN TABAKALANMASI "
         "(nefs/lif.py) ===", "",
         "  TEK KAYNAK (ferman 1-M): noktalar nefs/munasebet.py:Harita.M'den"
         " okunur;",
         "  bu defter o haritayı tip/kategori/uzay silsilesine ayırır, "
         "ikinci bir harita TUTMAZ.",
         "    müşterek haritanın doyması: %.4f   işlenen örnek: %d"
         % (lif.doyma, lif.islenen),
         "",
         "  silsile : nokta → uzay → kategori → tip",
         "  tip     : %s" % ", ".join(lif.tipler()),
         "  sözlük  : %d     asansör katı: %d     biriken tur: %d"
         % (lif.sozluk, lif.asansor_kati, lif.tur),
         "",
         lif.kategori_beyani,
         "",
         "  BAĞIMLI LİF vs KARTEZYEN KUTU (aynı muhteva)",
         "    tip=%d kategori=%d uzay=%d" % (n["tip"], n["kategori"],
                                             n["uzay"]),
         "    lif hücresi   : %d" % n["lif_hücresi"],
         "    kutu hücresi  : %d" % n["kutu_hücresi"],
         "    boş kalacaktı : %d" % n["boş_kalacaktı"],
         "",
         "  KOPUKLUK (ferman 1-Z: kopukluk da çelişkidir)",
         "    hücre %d, kopuk %d, nispet %.4f   (eşik %.6f -- ölçülen)"
         % (k["hücre"], k["kopuk"], k["nispet"], float(k.get("eşik", 0.0)))]
    if k.get("kopuk_adres"):
        s.append("    kopuk adresler: %s" % ", ".join(k["kopuk_adres"]))
    if k.get("sebep"):
        s.append("    sebep: %s" % k["sebep"])
    s += ["",
          "  SONSUZ MERTEBELER -- Σ zinciri ve NbE",
          "    Σ sayısı %d  (NbE sonrası %d)  defterle uyuştu: %s"
          % (dg["Σ_sayısı"], dg["NbE_sonrası_Σ"],
             "EVET" if dg["uyuştu"] else "HAYIR"),
          "    Unfold(kategori) → %s   Unfold(nokta) → %s"
          % (type(lif.unfold("kategori")).__name__,
             type(lif.unfold("nokta")).__name__)]
    return "\n".join(s)
