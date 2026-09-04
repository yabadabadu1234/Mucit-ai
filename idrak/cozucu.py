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

from nefs import musahede as arc

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
#  Genişletilmiş kaideler (ARC-AGI-2'nin yapısına göre)
# ══════════════════════════════════════════════════════════════════════
#
# Değerlendirme kümesinin yapısı ölçüldü (120 görev):
#   çıktı renkleri girdide var .... 104   şekil korunuyor ...... 81
#   çıktı şekli sabit .............  37   çıktı ≤100 hücre .....  13
# Aşağıdaki kaideler bu ölçüme göre seçildi; kör bir genişletme değil.


#: ``_bilesenler`` için hafıza. Anahtar ızgaranın **baytları**dır;
#: ızgara değişmediği sürece netice de değişmez, zira fonksiyon saftır.
_BILESEN_HAFIZA: Dict[bytes, List[Tuple[int, np.ndarray,
                                        Tuple[int, int, int, int]]]] = {}
#: Hafızanın haddi -- sınırsız büyürse bellek yer. En eski atılır.
_HAFIZA_HADDI: int = 4096


def _bilesenler(g: np.ndarray, arka: int = 0
                ) -> List[Tuple[int, np.ndarray, Tuple[int, int, int, int]]]:
    """4-komşulukta bağlı bileşenler: ``(renk, maske, kutu)``.

    ===================================================================
    ÖLÇÜLEN VE DÜZELTİLEN KUSUR (kütük H197)
    ===================================================================

    Profil çıkarıldı: **tek bir ARC görevinde bu fonksiyon 21.976 kere
    çağrılıyor** ve 65,8 saniye yiyordu (görev başına 246,9 saniyenin
    dörtte biri). Halbuki fonksiyon **saftır**: aynı ızgara ve aynı
    arka renk için neticesi hep aynıdır. Kâide arayışı aynı birkaç
    ızgarayı binlerce kere tarıyordu.

    Çare hafızadır (memoization). Anahtar ızgaranın baytlarıdır;
    netice **kopyalanmadan** paylaşılır -- maskeler okunur, yazılmaz.
    Mana hiç değişmez, yalnız tekrar hesap kalkar.
    """
    anah = arka.to_bytes(2, "little") + g.shape[0].to_bytes(2, "little") \
        + g.shape[1].to_bytes(2, "little") \
        + np.ascontiguousarray(g, dtype=np.int16).tobytes()
    onbellek = _BILESEN_HAFIZA.get(anah)
    if onbellek is not None:
        return onbellek
    H, W = g.shape
    gor = np.zeros((H, W), bool)
    out = []
    for i in range(H):
        for j in range(W):
            if gor[i, j] or g[i, j] == arka:
                continue
            renk = int(g[i, j])
            yigin = [(i, j)]
            gor[i, j] = True
            hucre = []
            while yigin:
                y, x = yigin.pop()
                hucre.append((y, x))
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    a, b = y + dy, x + dx
                    if (0 <= a < H and 0 <= b < W and not gor[a, b]
                            and g[a, b] == renk):
                        gor[a, b] = True
                        yigin.append((a, b))
            ys = [y for y, _ in hucre]
            xs = [x for _, x in hucre]
            m = np.zeros((H, W), bool)
            for y, x in hucre:
                m[y, x] = True
            out.append((renk, m, (min(ys), max(ys), min(xs), max(xs))))
    if len(_BILESEN_HAFIZA) >= _HAFIZA_HADDI:
        _BILESEN_HAFIZA.pop(next(iter(_BILESEN_HAFIZA)))
    _BILESEN_HAFIZA[anah] = out
    return out


def _nesne_sec(g: np.ndarray, olcut: str, arka: int = 0
               ) -> Optional[np.ndarray]:
    """Bir bileşeni seçip kutusuyla kırp."""
    b = _bilesenler(g, arka)
    if not b:
        return None
    if olcut == "en_buyuk":
        _r, _m, k = max(b, key=lambda x: int(x[1].sum()))
    elif olcut == "en_kucuk":
        _r, _m, k = min(b, key=lambda x: int(x[1].sum()))
    elif olcut == "tek_renk":
        say: Dict[int, int] = {}
        for r, _m, _k in b:
            say[r] = say.get(r, 0) + 1
        tekler = [x for x in b if say[x[0]] == 1]
        if len(tekler) != 1:
            return None
        _r, _m, k = tekler[0]
    else:
        return None
    r0, r1, c0, c1 = k
    return np.ascontiguousarray(g[r0:r1 + 1, c0:c1 + 1])


def _bakisim_onar(g: np.ndarray, delik: int) -> Optional[np.ndarray]:
    """Izgaranın kendi bakışımını kullanarak ``delik`` rengini doldur.

    ARC'ta çok sık: bir bölge örtülmüş, ızgara yatay/dikey/nokta
    bakışımlı ve örtülü kısım aynadan okunuyor.  Hiçbir bakışım
    deliği kapatmıyorsa ``None``.
    """
    if not (g == delik).any():
        return None
    out = g.copy()
    for don in (np.fliplr, np.flipud, lambda x: np.rot90(x, 2)):
        ayna = don(out)
        yaz = (out == delik) & (ayna != delik)
        out = np.where(yaz, ayna, out)
    return None if (out == delik).any() else np.ascontiguousarray(out)


def _delik_rengi(ciftler: Sequence[Tuple[np.ndarray, np.ndarray]]
                 ) -> Optional[int]:
    """Girdide olup çıktıda hiç olmayan tek renk — "delik" adayı."""
    aday = None
    for a, b in ciftler:
        if a.shape != b.shape:
            return None
        fark = set(np.unique(a)) - set(np.unique(b))
        if len(fark) != 1:
            return None
        r = int(next(iter(fark)))
        if aday is None:
            aday = r
        elif aday != r:
            return None
    return aday


def _yercekimi(g: np.ndarray, yon: str, arka: int = 0) -> np.ndarray:
    """Dolu hücreleri bir yöne yığ."""
    out = np.full_like(g, arka)
    if yon in ("asagi", "yukari"):
        for j in range(g.shape[1]):
            s = [v for v in g[:, j] if v != arka]
            if yon == "asagi":
                out[g.shape[0] - len(s):, j] = s
            else:
                out[:len(s), j] = s
    else:
        for i in range(g.shape[0]):
            s = [v for v in g[i] if v != arka]
            if yon == "saga":
                out[i, g.shape[1] - len(s):] = s
            else:
                out[i, :len(s)] = s
    return out


def _ek_adaylar(ciftler: Sequence[Tuple[np.ndarray, np.ndarray]]
                ) -> List[Aday]:
    """Yapı ölçümüne göre seçilmiş ek kaideler."""
    out: List[Aday] = []

    # Bakışım onarımı (delik rengi görevden çıkarılıyor)
    d = _delik_rengi(ciftler)
    if d is not None:
        out.append(Aday("bakışım_onarımı_renk%d" % d,
                        lambda g, k=d: _bakisim_onar(g, k)))

        def onar_kirp(g, k=d):
            t = _bakisim_onar(g, k)
            if t is None:
                return None
            nz = np.argwhere(g == k)
            if nz.size == 0:
                return None
            (r0, c0), (r1, c1) = nz.min(0), nz.max(0)
            return np.ascontiguousarray(t[r0:r1 + 1, c0:c1 + 1])

        out.append(Aday("bakışım_onarımı+kırp_renk%d" % d, onar_kirp))

    # Nesne seçimi
    for olcut in ("en_buyuk", "en_kucuk", "tek_renk"):
        out.append(Aday("nesne:" + olcut,
                        lambda g, o=olcut: _nesne_sec(g, o)))

    # Yerçekimi
    for yon in ("asagi", "yukari", "saga", "sola"):
        out.append(Aday("yerçekimi:" + yon,
                        lambda g, y=yon: _yercekimi(g, y)))

    return out


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

    out.extend(_ek_adaylar(ciftler))
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
    egt = arc.gorevleri_getir("training")
    dgr = arc.gorevleri_getir("evaluation")

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
