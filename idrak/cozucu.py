"""Doğrulanabilir ARC çözücüsü: dik dönüşüm DSL'i üzerinde arama.

**Neden bu var.**  Sinir ağı ``D=128``de CPU'da eğitiliyor ve ARC-AGI-2
üzerinde tam ızgara eşleşmesi vermesi beklenemez (cephe modelleri bile
tek haneli yüzdelerde).  Fakat kullanıcının istediği şey açıktır: *en
az bir görev %100 doğru çözülmeli*.  Bunun dürüst yolu, sinir ağının
çıktısını "çözdü" diye yuvarlamak değil, **ispatlanabilir** bir çözücü
kurmaktır.

**Mimarîyle bağı tesadüf değil.**  ARC ızgara dönüşümlerinin çekirdeği
``D₄`` dihedral grubudur (dört dönme, dört yansıma) ve bunlar
``reel.meleke``deki **permütasyon kapılarının** ta kendisidir: hepsi
dik, hepsi norm koruyucu, hepsi tersinir.  Külliyattaki "41 meleke reel
dik kapıdır" tezinin ARC'taki fiilî karşılığı budur.

**Usul.**  Bir görev için:

1. Aday dönüşümler üretilir (``D₄`` × renk eşlemesi × döşeme × kırpma).
2. Her aday, görevin **kendi gösterim çiftlerinin hepsinde** sınanır.
   Bu meşrudur: ARC'ta gösterim çiftleri göreve dâhildir.
3. Bütün gösterim çiftlerini **tam** tutan aday, sınama girdisine
   uygulanır.
4. Hiçbir aday tutmuyorsa **cevap verilmez** (``None``).  Tahmin
   üretip "belki tutar" demek, tam eşleşme ölçütünü sahte kılardı.

Yani bu çözücü ya *ispatlı* cevap verir ya da susar.  Ölçülen sayı,
resmî değerlendirme kümesinde kaç görevin tam çözüldüğüdür.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

from . import arc

__all__ = [
    "D4", "d4_uygula", "Aday", "adaylar", "gorev_coz", "kume_coz",
    "renk_eslemesi_bul", "dogrula",
]

# ── D₄ dihedral grubu: dört dönme + dört yansıma ────────────────────
D4: Dict[str, Callable[[np.ndarray], np.ndarray]] = {
    "birim": lambda g: g,
    "dön90": lambda g: np.rot90(g, 1),
    "dön180": lambda g: np.rot90(g, 2),
    "dön270": lambda g: np.rot90(g, 3),
    "yatay_ayna": lambda g: np.fliplr(g),
    "dikey_ayna": lambda g: np.flipud(g),
    "devrik": lambda g: g.T,
    "ters_devrik": lambda g: np.rot90(g, 2).T,
}


def d4_uygula(g: np.ndarray, ad: str) -> np.ndarray:
    return np.ascontiguousarray(D4[ad](g))


@dataclass
class Aday:
    """Bir aday dönüşüm: ad + uygulayıcı."""
    ad: str
    uygula: Callable[[np.ndarray], Optional[np.ndarray]]


# ══════════════════════════════════════════════════════════════════════
#  Renk eşlemesi
# ══════════════════════════════════════════════════════════════════════

def renk_eslemesi_bul(ciftler: Sequence[Tuple[np.ndarray, np.ndarray]]
                      ) -> Optional[Dict[int, int]]:
    """Şekli koruyan, hücre başına tutarlı bir renk eşlemesi var mı?

    Bütün çiftlerde ``çıktı[i,j] = f(girdi[i,j])`` olacak tek bir ``f``
    aranıyor.  Çelişki çıkarsa ``None`` -- uydurma yapılmıyor.
    """
    f: Dict[int, int] = {}
    for a, b in ciftler:
        if a.shape != b.shape:
            return None
        for x, y in zip(a.reshape(-1), b.reshape(-1)):
            x, y = int(x), int(y)
            if x in f and f[x] != y:
                return None
            f[x] = y
    return f


def _dosemeyi_bul(ciftler: Sequence[Tuple[np.ndarray, np.ndarray]]
                  ) -> Optional[Tuple[int, int]]:
    """Çıktı, girdinin ``(p, q)`` katı bir döşemesi mi?"""
    a, b = ciftler[0]
    if b.shape[0] % a.shape[0] or b.shape[1] % a.shape[1]:
        return None
    p, q = b.shape[0] // a.shape[0], b.shape[1] // a.shape[1]
    if (p, q) == (1, 1):
        return None
    return p, q


def _kirpma_bul(ciftler: Sequence[Tuple[np.ndarray, np.ndarray]]
                ) -> Optional[Callable[[np.ndarray], Optional[np.ndarray]]]:
    """Çıktı, girdinin sıfır olmayan bölgesinin kırpılması mı?"""
    def kirp(g: np.ndarray) -> Optional[np.ndarray]:
        nz = np.argwhere(g != 0)
        if nz.size == 0:
            return None
        (r0, c0), (r1, c1) = nz.min(0), nz.max(0)
        return np.ascontiguousarray(g[r0:r1 + 1, c0:c1 + 1])
    return kirp


# ══════════════════════════════════════════════════════════════════════
#  Aday üretimi
# ══════════════════════════════════════════════════════════════════════

def adaylar(ciftler: Sequence[Tuple[np.ndarray, np.ndarray]]
            ) -> List[Aday]:
    """Görevin gösterim çiftlerine bakarak aday dönüşüm listesi kur.

    Adaylar **görevden türetiliyor** (renk eşlemesi, döşeme katı,
    kırpma kutusu); kör bir arama değil.
    """
    out: List[Aday] = []

    # 1. Saf D₄
    for ad in D4:
        out.append(Aday("D4:" + ad,
                        lambda g, a=ad: d4_uygula(g, a)))

    # 2. D₄ + renk eşlemesi
    f = renk_eslemesi_bul(ciftler)
    if f is not None:
        out.append(Aday("renk_eşlemesi",
                        lambda g, m=f: np.vectorize(
                            lambda v: m.get(int(v), int(v)))(g).astype(
                            np.int64)))
    for ad in D4:
        donuk = [(d4_uygula(a, ad), b) for a, b in ciftler]
        f2 = renk_eslemesi_bul(donuk)
        if f2 is not None:
            out.append(Aday("D4:%s+renk" % ad,
                            lambda g, a=ad, m=f2: np.vectorize(
                                lambda v: m.get(int(v), int(v)))(
                                d4_uygula(g, a)).astype(np.int64)))

    # 3. Döşeme (aynalı ve aynasız)
    pq = _dosemeyi_bul(ciftler)
    if pq is not None:
        p, q = pq
        out.append(Aday("döşeme_%dx%d" % (p, q),
                        lambda g, p=p, q=q: np.tile(g, (p, q))))

        def aynali(g, p=p, q=q):
            satirlar = []
            for i in range(p):
                parca = [g if (i + j) % 2 == 0 else np.fliplr(g)
                         for j in range(q)]
                s = np.hstack(parca)
                satirlar.append(s if i % 2 == 0 else np.flipud(s))
            return np.vstack(satirlar)

        out.append(Aday("aynalı_döşeme_%dx%d" % (p, q), aynali))

    # 4. Kırpma ve kırpma + D₄
    kirp = _kirpma_bul(ciftler)
    if kirp is not None:
        out.append(Aday("kırp", kirp))
        for ad in D4:
            out.append(Aday("kırp+D4:%s" % ad,
                            lambda g, a=ad, k=kirp: (
                                None if k(g) is None
                                else d4_uygula(k(g), a))))

    # 5. Ölçekleme (her hücre p×q bloğa)
    if pq is not None:
        p, q = pq
        out.append(Aday("ölçek_%dx%d" % (p, q),
                        lambda g, p=p, q=q: np.kron(
                            g, np.ones((p, q), dtype=np.int64))))
        # hücre değeri 0 değilse ızgaranın kendisini bas (fraktal)
        def fraktal(g, p=p, q=q):
            if (p, q) != g.shape:
                return None
            h, w = g.shape
            out_ = np.zeros((h * p, w * q), dtype=np.int64)
            for i in range(h):
                for j in range(w):
                    if g[i, j] != 0:
                        out_[i * h:(i + 1) * h, j * w:(j + 1) * w] = g
            return out_
        out.append(Aday("fraktal", fraktal))

    return out


# ══════════════════════════════════════════════════════════════════════
#  Çözme
# ══════════════════════════════════════════════════════════════════════

def dogrula(aday: Aday,
            ciftler: Sequence[Tuple[np.ndarray, np.ndarray]]) -> bool:
    """Aday, **bütün** gösterim çiftlerini tam tutuyor mu?"""
    for a, b in ciftler:
        try:
            c = aday.uygula(a)
        except Exception:
            return False
        if c is None or c.shape != b.shape or not np.array_equal(c, b):
            return False
    return True


def gorev_coz(gorev: arc.Gorev) -> Dict[str, object]:
    """Bir görevi çöz — ya ispatlı cevap ya da ``None``.

    Aday, görevin **gösterim çiftlerinde** doğrulanır; sınama çıktısı
    hiç görülmez.  Neticeyi ayrıca sınama çıktısıyla kıyaslamak
    değerlendirmedir, çözümün parçası değil.
    """
    ad_listesi = adaylar(gorev.egitim)
    tutan = [a for a in ad_listesi if dogrula(a, gorev.egitim)]
    if not tutan:
        return {"görev": gorev.ad, "cevap_verildi": False,
                "kural": None, "aday_sayısı": len(ad_listesi),
                "tam_mı": False}
    kural = tutan[0]
    tahminler, dogru = [], True
    for a, b in gorev.sinama:
        try:
            c = kural.uygula(a)
        except Exception:
            c = None
        tahminler.append(c)
        if c is None or c.shape != b.shape or not np.array_equal(c, b):
            dogru = False
    return {"görev": gorev.ad, "cevap_verildi": True, "kural": kural.ad,
            "tutan_aday": [a.ad for a in tutan],
            "aday_sayısı": len(ad_listesi),
            "tahmin": tahminler, "tam_mı": dogru}


def kume_coz(gorevler: Sequence[arc.Gorev]) -> Dict[str, object]:
    """Bir kümeyi çöz; **tam eşleşme** ile say."""
    sonuc = [gorev_coz(g) for g in gorevler]
    cevaplanan = [r for r in sonuc if r["cevap_verildi"]]
    dogru = [r for r in cevaplanan if r["tam_mı"]]
    return {"görev": len(gorevler),
            "cevap_verilen": len(cevaplanan),
            "tam_çözülen": len(dogru),
            "tam_çözülen_ad": [r["görev"] for r in dogru],
            "yanlış_cevap": len(cevaplanan) - len(dogru),
            "susulan": len(gorevler) - len(cevaplanan),
            "isabet_cevap_verince": (len(dogru) / len(cevaplanan)
                                     if cevaplanan else float("nan")),
            "kümede_oran": len(dogru) / max(len(gorevler), 1),
            "kurallar": sorted({r["kural"] for r in dogru}),
            "ayrıntı": sonuc}


# ══════════════════════════════════════════════════════════════════════
#  Gösterim
# ══════════════════════════════════════════════════════════════════════

def _gosterim() -> str:
    s = []
    egt = arc.yukle_hepsi("training")
    dgr = arc.yukle_hepsi("evaluation")

    s.append("=== Doğrulanabilir çözücü: ya ispat ya sükût ===")
    for ad, kume in (("resmî eğitim (1000)", egt),
                     ("resmî değerlendirme (120)", dgr)):
        r = kume_coz(kume)
        s.append("  %-26s tam çözülen=%3d (%.1f%%)   cevap verilen=%3d"
                 "   yanlış cevap=%2d   susulan=%4d"
                 % (ad, r["tam_çözülen"], 100 * r["kümede_oran"],
                    r["cevap_verilen"], r["yanlış_cevap"], r["susulan"]))
        if r["cevap_verilen"]:
            s.append("  %-26s cevap verince isabet = %.1f%%"
                     % ("", 100 * r["isabet_cevap_verince"]))
        if r["tam_çözülen_ad"]:
            s.append("  %-26s çözülen görevler: %s"
                     % ("", ", ".join(r["tam_çözülen_ad"][:8])
                        + (" …" if len(r["tam_çözülen_ad"]) > 8 else "")))
            s.append("  %-26s kullanılan kurallar: %s"
                     % ("", ", ".join(r["kurallar"])))

    s.append("\n=== Bir çözümün TAM ispatı ===")
    r = kume_coz(dgr)
    if r["tam_çözülen_ad"]:
        ad = r["tam_çözülen_ad"][0]
        g = [x for x in dgr if x.ad == ad][0]
        d = gorev_coz(g)
        s.append("  görev: %s   bulunan kural: %s" % (ad, d["kural"]))
        s.append("  gösterim çiftlerinin HEPSİNDE tutuyor mu? (%d çift)"
                 % len(g.egitim))
        for i, (a, b) in enumerate(g.egitim):
            c = [x for x in adaylar(g.egitim) if x.ad == d["kural"]][0]
            s.append("    çift %d: %s → %s   tam mı? %s"
                     % (i, a.shape, b.shape,
                        bool(np.array_equal(c.uygula(a), b))))
        for i, (a, b) in enumerate(g.sinama):
            s.append("    SINAMA %d: beklenen %s, üretilen %s   TAM MI? %s"
                     % (i, b.shape, d["tahmin"][i].shape,
                        bool(np.array_equal(d["tahmin"][i], b))))
        s.append("  Sözlü algoritma (veri kümesinden):")
        soz = arc.soyutlama_oku(ad)
        if soz:
            for satir in soz.strip().splitlines()[:2]:
                s.append("    " + satir[:92])
    else:
        s.append("  Bu DSL değerlendirme kümesinde hiçbir görevi tam")
        s.append("  çözemedi. Bu bir başarısızlıktır ve öyle yazılıyor.")

    s.append("\n=== Susmak neden şart? ===")
    r2 = kume_coz(egt)
    s.append("  Eğitim kümesinde %d göreve cevap verildi, %d'i doğru."
             % (r2["cevap_verilen"], r2["tam_çözülen"]))
    s.append("  Çözücü, gösterim çiftlerini tutmayan hiçbir kuralı")
    s.append("  kullanmıyor; tutan bir kural yoksa CEVAP VERMİYOR.")
    s.append("  Tahmin üretip 'belki tutar' demek, tam eşleşme")
    s.append("  ölçütünü sahte kılardı.")
    return "\n".join(s)


if __name__ == "__main__":  # pragma: no cover
    print(_gosterim())
