"""LİSAN VE İKİ BOYUTLU İZAFÎ MEVKİ -- tiktoken + Lie öteleme üreteçleri.

Padişahın hükmü (09-KÜLLÎ-TEŞKİLAT celsesi):

    Tokenizer olarak tiktoken kullanılacak. Durumun içinde tek boyutlu
    değil **iki boyutlu** mevki bilgisi olmalı, umumi için, yalnız ARC
    için değil. Mevki bilgisi sayısal olursa hudutlamak gerekir, bu da
    iyi olmaz; **sembolik** olmalı -- sağında, solunda, yukarısında,
    aşağısında gibi **izafî** tarifler.

===================================================================
NİÇİN MUTLAK KOORDİNAT YASAK
===================================================================

``x = 5, y = 3`` yazmak iki şeyi birden bozar:

1. **Hudut koymak zorunda kalırsın.** ``x`` kaça kadar? 30'a kadarsa
   31. sütun temsil edilemez; 4096'ya kadarsa boş yere 12 kübit yer.
2. **Genelleme ölür.** Bir kuralı ``x = 5``te öğrenen model onu
   ``x = 17``de tanıyamaz; halbuki kural *"sağındaki hücre"* diyordu.

İzafî tarif ikisini de çözer: ``sağ`` her yerde ``sağ``dır ve hiçbir
hudut istemez. Cebri Lie öteleme üreteçleridir::

    T̂_x |x,y⟩ = |x+1,y⟩        T̂_x† |x,y⟩ = |x−1,y⟩
    T̂_y |x,y⟩ = |x,y+1⟩        T̂_y† |x,y⟩ = |x,y−1⟩

    𝒟(Δx,Δy) = T̂_x^{Δx} · T̂_y^{Δy}

**Üç mod, tek cebir** -- ve bu, "umumi için, yalnız ARC için değil"
hükmünün fiilî karşılığıdır::

    metin   : Δ = (+1, 0)                 doğrusal akış
    kod/ağaç: Δ = (girinti, satır)        2D sentaks
    ızgara  : Δ ∈ {−1,0,+1}²              Moore komşuluğu

===================================================================
TİKTOKEN -- padişah tabloyu depoya koydu, ağa ihtiyaç kalmadı
===================================================================

``tiktoken`` kurulu fakat tablo indirmesi bu ortamda ağdan geçmiyordu
(vekil 403 -- H87'nin duvarı). Padişah ``o200k_base.tiktoken``
dosyasını **depo köküne koydu**; artık tablo yerel dosyadan okunur ve
hiçbir ağ çağrısı yapılmaz.

``kodlayici()`` üç kademeli davranır ve hangisine düştüğünü **saklamaz**:

1. Depodaki ``o200k_base.tiktoken`` → ``kaynak = "o200k_yerel"``
2. Ağdan ``tiktoken.get_encoding`` → ``kaynak = "tiktoken"``
3. İkisi de olmazsa belirlenimci bayt kimliği → ``kaynak = "bayt"``

Yedek bir BPE değildir; bayt kimliğidir, sözlüğü 256'dır ve dizileri
uzatır. Rapor hangisinin koştuğunu daima yazar.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["OZEL_BELIRTECLER", "TABLO_ADLARI", "YON_ADLARI", "Kodlayici", "kodlayici",
           "izafi_oteleme", "IzafiMevki"]


#: ARC ve 2D için ilâve edilen özel belirteçler. Numaraları taban
#: sözlüğün **üstünden** başlar; taban değişse de çakışmaz.
OZEL_BELIRTECLER: Tuple[str, ...] = (
    "<renk_0>", "<renk_1>", "<renk_2>", "<renk_3>", "<renk_4>",
    "<renk_5>", "<renk_6>", "<renk_7>", "<renk_8>", "<renk_9>",
    "<izgara_bas>", "<izgara_son>", "<satır_ayır>",
    "<dx_+1>", "<dx_-1>", "<dy_+1>", "<dy_-1>",
    "<aynı_sütun>", "<aynı_satır>",
)

#: İzafî yönler -- **sekiz komşu ve merkez**. Sayı değil ad taşınır.
YON_ADLARI: Tuple[Tuple[str, int, int], ...] = (
    ("merkez", 0, 0),
    ("sağ", 1, 0), ("sol", -1, 0),
    ("yukarı", 0, 1), ("aşağı", 0, -1),
    ("sağ_yukarı", 1, 1), ("sol_yukarı", -1, 1),
    ("sağ_aşağı", 1, -1), ("sol_aşağı", -1, -1),
)




@dataclass
class Kodlayici:
    """tiktoken yahut bayt yedeği -- **hangisi olduğunu saklamaz**."""
    kaynak: str
    taban_sozluk: int
    _enc: object = field(default=None, repr=False)

    @property
    def sozluk(self) -> int:
        return int(self.taban_sozluk) + len(OZEL_BELIRTECLER)

    def ozel(self, ad: str) -> int:
        return int(self.taban_sozluk) + OZEL_BELIRTECLER.index(ad)

    def kodla(self, metin: str) -> List[int]:
        if self._enc is not None:
            return list(self._enc.encode(metin))
        return list(metin.encode("utf-8"))

    def coz(self, idler: Sequence[int]) -> str:
        gercek = [int(i) for i in idler if int(i) < self.taban_sozluk]
        if self._enc is not None:
            return self._enc.decode(gercek)
        return bytes(min(max(i, 0), 255) for i in gercek).decode(
            "utf-8", errors="replace")


#: Depoya konan BPE tablosunun aranacağı yerler (kök ve ``veri/``).
TABLO_ADLARI: Tuple[str, ...] = ("o200k_base.tiktoken",
                                 "veri/o200k_base.tiktoken",
                                 "data/o200k_base.tiktoken")

#: o200k_base'in kendi ayırma deseni (OpenAI'nin tescilli deseni).
_O200K_DESEN = (
    r"""[^\r\n\p{L}\p{N}]?[\p{Lu}\p{Lt}\p{Lm}\p{Lo}\p{M}]*"""
    r"""[\p{Ll}\p{Lm}\p{Lo}\p{M}]+(?i:'s|'t|'re|'ve|'m|'ll|'d)?|"""
    r"""[^\r\n\p{L}\p{N}]?[\p{Lu}\p{Lt}\p{Lm}\p{Lo}\p{M}]+"""
    r"""[\p{Ll}\p{Lm}\p{Lo}\p{M}]*(?i:'s|'t|'re|'ve|'m|'ll|'d)?|"""
    r"""\p{N}{1,3}| ?[^\s\p{L}\p{N}]+[\r\n/]*|\s*[\r\n]+|\s+(?!\S)|\s+"""
)


def _yerel_tablo() -> Optional[str]:
    import os
    kok = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for ad in TABLO_ADLARI:
        yol = os.path.join(kok, ad)
        if os.path.exists(yol):
            return yol
    return None


def kodlayici(tercih: str = "o200k_base") -> Kodlayici:
    """Yerel tabloyu, sonra ağı, sonra bayt yedeğini dene -- ve söyle."""
    yol = _yerel_tablo()
    if yol is not None:
        try:
            import base64
            import tiktoken                   # type: ignore
            ranks: Dict[bytes, int] = {}
            with open(yol, "r", encoding="utf-8") as f:
                for satir in f:
                    if not satir.strip():
                        continue
                    tok, rank = satir.split()
                    ranks[base64.b64decode(tok)] = int(rank)
            enc = tiktoken.Encoding(name="o200k_yerel", pat_str=_O200K_DESEN,
                                    mergeable_ranks=ranks,
                                    special_tokens={})
            return Kodlayici(kaynak="o200k_yerel",
                             taban_sozluk=int(max(ranks.values()) + 1),
                             _enc=enc)
        except Exception:
            pass
    try:
        import tiktoken                       # type: ignore
        enc = tiktoken.get_encoding(tercih)
        return Kodlayici(kaynak="tiktoken", taban_sozluk=int(enc.n_vocab),
                         _enc=enc)
    except Exception:
        return Kodlayici(kaynak="bayt", taban_sozluk=256, _enc=None)


# ══════════════════════════════════════════════════════════════════════
#  İzafî mevki: Lie öteleme üreteçleri
# ══════════════════════════════════════════════════════════════════════

@dataclass
class IzafiMevki:
    """Bir hücrenin **izafî** tarifi: komşularıyla ilişkisi.

    Mutlak ``(x, y)`` tutulmaz. Tutulan, sekiz komşunun her birine
    bakıldığında ne görüldüğüdür -- yani hücrenin **çevresindeki
    örüntü**. Aynı örüntü ızgaranın neresinde olursa olsun aynı
    kodlanır; kural "sol üstte" öğrenilip "sağ altta" tanınabilir.
    """
    merkez: int
    komsu: Tuple[int, ...]

    def kod(self) -> Tuple[int, ...]:
        return (int(self.merkez),) + tuple(int(k) for k in self.komsu)


def izafi_oteleme(nx: int = 0, ny: int = 0, dx: int = 0, dy: int = 0,
                  ne: str = "operator", n: int = 0, adim: int = 1,
                  yon: Tuple[int, int] = (0, 0), g=None, k=None,
                  dolgu: int = -1, metin: str = ""):
    """MUTLAK YER DEĞİL, İZAFÎ KOMŞULUK -- tek terkip (kütük H225).

    Küme: ``yon_indisi`` + ``oteleme_ureteci`` + ``izafi_operator`` +
    ``IzafiMevki.kod`` + ``izgara_kodla`` + ``metin_kodla``. Altısı tek
    fikrin katlarıydı: ``x = 5, y = 3`` gibi **mutlak** koordinat
    genellemeyi öldürür; hüküm ancak **komşuluk örüntüsünden** çıkarsa
    ızgaranın neresinde olursa olsun aynı kalır.

    ==============  ==================================================
    ``ne``          döndürdüğü
    ==============  ==================================================
    ``yön``         ``(dx, dy)`` komşuluk yönünün indisi
    ``üreteç``      ``T̂`` -- ``n`` yuvalı çevrimsel öteleme
    ``operator``    ``𝒟(Δx,Δy) = T̂_x^{Δx} ⊗ T̂_y^{Δy}``
    ``ızgara``      ızgarayı izafî komşuluk örüntülerine çevir
    ``metin``       metni aynı akışa kat -- ``Δ = (+1, 0)`` doğrusal
    ==============  ==================================================

    Öteleme **çevrimseldir** (kenarsız, sınırsız devir) ve permütasyon
    olduğu için ortogonaldir; ``𝒟`` böylece üniter kalır ve normu
    korur.
    """
    if ne == "yön":
        for i, (a, _, _) in enumerate(YON_ADLARI):
            if a == ad:
                return i
        raise KeyError("bilinmeyen yön: %s" % ad)

    if ne == "üreteç":
        n = int(n)
        if n < 1:
            raise ValueError("n ≥ 1 olmalı")
        T = np.zeros((n, n))
        for i in range(n):
            T[(i + int(adim)) % n, i] = 1.0
        return T

    if ne == "operator":
        Tx = np.linalg.matrix_power(
            izafi_oteleme(n=nx, adim=+1, ne="üreteç"), int(dx) % int(nx))
        Ty = np.linalg.matrix_power(
            izafi_oteleme(n=ny, adim=+1, ne="üreteç"), int(dy) % int(ny))
        return np.kron(Tx, Ty)

    if ne == "ızgara":
        k = k or kodlayici()
        G = np.atleast_2d(np.asarray(g, int))
        h, w = G.shape
        dizi: List[int] = [k.ozel("<izgara_bas>")]
        ornek: List[IzafiMevki] = []
        for i in range(h):
            if i:
                dizi.append(k.ozel("<satır_ayır>"))
            for j in range(w):
                dizi.append(k.ozel("<renk_%d>" % (int(G[i, j]) % 10)))
                kom: List[int] = []
                for _, dx, dy in YON_ADLARI[1:]:
                    ii, jj = i - dy, j + dx
                    kom.append(int(G[ii, jj]) if 0 <= ii < h and 0 <= jj < w
                               else int(dolgu))
                ornek.append(IzafiMevki(merkez=int(G[i, j]),
                                        komsu=tuple(kom)))
        dizi.append(k.ozel("<izgara_son>"))
        return {"dizi": dizi, "izafi": ornek, "en": w, "boy": h,
                "kodlayıcı": k.kaynak}

    if ne != "metin":
        raise ValueError("izafî öteleme kipi bilinmiyor: %r" % (ne,))
    k = k or kodlayici()
    return {"dizi": k.kodla(metin), "kodlayıcı": k.kaynak,
            "Δ": (1, 0)}


def rapor() -> str:                                     # pragma: no cover
    s = ["LİSAN VE 2D İZAFÎ MEVKİ", ""]
    k = kodlayici()
    s.append("  kodlayıcı kaynağı : %s   (taban sözlük %d, özel %d, toplam %d)"
             % (k.kaynak, k.taban_sozluk, len(OZEL_BELIRTECLER), k.sozluk))
    if k.kaynak != "tiktoken":
        s.append("  ! tiktoken tablosu bu ortamda ağdan çekilemedi (403);")
        s.append("    aşağıdaki bütün sayılar BAYT YEDEĞİYLEdir.")

    s.append("")
    s.append("  1) İzafî operatörler ortogonal mi, ve mutlak koordinat")
    s.append("     taşımıyor mu?")
    nx, ny = 5, 4
    for ad, dx, dy in YON_ADLARI[1:5]:
        D = izafi_oteleme(ne="operator", h=nx, w=ny, dx=dx, dy=dy)
        dik = float(np.linalg.norm(D.T @ D - np.eye(nx * ny)))
        s.append("     %-10s Δ=(%+d,%+d)  ‖DᵀD−I‖ = %.2e" % (ad, dx, dy, dik))
    Dr = izafi_oteleme(ne="operator", h=nx, w=ny, dx=1, dy=0)
    Dl = izafi_oteleme(ne="operator", h=nx, w=ny, dx=-1, dy=0)
    s.append("     sağ ∘ sol = I : %.2e"
             % float(np.linalg.norm(Dr @ Dl - np.eye(nx * ny))))

    s.append("")
    s.append("  2) Aynı örüntü ızgaranın HER YERİNDE aynı kodlanıyor mu?")
    A = np.zeros((6, 6), int)
    A[1, 1] = 3; A[1, 2] = 5
    B = np.zeros((6, 6), int)
    B[4, 3] = 3; B[4, 4] = 5
    ra = izafi_oteleme(ne="ızgara", g=A)["izafi"]
    rb = izafi_oteleme(ne="ızgara", g=B)["izafi"]
    ka = [x.kod() for x in ra if x.merkez == 3][0]
    kb = [x.kod() for x in rb if x.merkez == 3][0]
    s.append("     sol üstteki örüntü : %s" % (ka,))
    s.append("     sağ alttaki örüntü : %s" % (kb,))
    s.append("     AYNI MI: %s   ← mutlak koordinat olsaydı olmazdı"
             % (ka == kb))

    s.append("")
    s.append("  3) Izgara ve metin AYNI akışta")
    g = izgara_kodla(np.array([[1, 2], [3, 4]]))
    m = izafi_oteleme(ne="metin", metin="kırmızı kare sağa kayar")
    s.append("     ızgara dizisi  : %s" % g["dizi"])
    s.append("     metin dizisi   : %d belirteç (%s)"
             % (len(m["dizi"]), m["kodlayıcı"]))
    s.append("     ikisi de aynı sözlükte; ayrı iki dünya yok.")
    return "\n".join(s)


if __name__ == "__main__":   # pragma: no cover
    print(rapor())


# =====================================================================
#  FERMAN ADIYLA: 2D İZAFÎ MEVKİ VE tiktoken KÖPRÜSÜ
# =====================================================================
class IzafiMevki2D:
    """2D izafî (öteleme değişmez) mevki -- **mutlak koordinat YOK**.

    Bir hücrenin yeri ``(i, j)`` diye değil, komşularına göre
    ``sağında / solunda / üstünde`` diye taşınır. Öteleme üreteçleri
    çevrimsel ve ortogonaldir (``oteleme_ureteci``), yani bu bir Lie
    akışıdır, bir tablo değil.
    """

    def __init__(self, yaricap: int = 1) -> None:
        self.yaricap = int(yaricap)
        self._kod = None

    # -- bağlam ---------------------------------------------------------
    def izgara_donustur(self, g) -> "np.ndarray":
        """Izgarayı izafî bağlam vektörlerine çevir: ``(H·W, 1+komşu)``."""
        from main.cikarim import baglam_cikar
        B = baglam_cikar(g, self.yaricap)
        return B.reshape(-1, B.shape[2]).astype(float)

    def durum_vektoru_kur(self, g) -> "np.ndarray":
        """Izgaradan **tek** dalga vektörü: genlikler normalize."""
        v = self.izgara_donustur(g).reshape(-1)
        n = np.linalg.norm(v)
        return v / n if n > 0 else v

    def ebat_kanunu_coz(self, g):
        """Çıktı ebadını **kanundan** okur; şablon listesi yoktur.

        Tek ızgaradan kanun çözülemez (şahit lazımdır); o hâlde girdi
        ebadı döner ve bu bir varsayım olarak **ilan edilir**.
        """
        import numpy as _np
        a = _np.atleast_2d(_np.asarray(g, int))
        return (int(a.shape[0]), int(a.shape[1]))


def tiktoken_2d_kodla(metin: str, k=None):
    """Metni ``o200k_base`` ile kodla -- kaynağı daima raporlanır."""
    r = metin_kodla(str(metin), k)
    import numpy as _np
    return _np.asarray(r.get("belirtec", r.get("kod", [])), dtype=float)


def tiktoken_2d_coz(kodlar, k=None) -> str:
    """Belirteçlerden metne dön; çözülemeyen belirteç **saklanmaz**."""
    kod = k or kodlayici()
    enc = getattr(kod, "_enc", None)
    dizi = [int(x) for x in np.asarray(kodlar).reshape(-1)]
    if enc is None:
        return " ".join(str(x) for x in dizi)
    try:
        return enc.decode(dizi)
    except Exception:                                    # noqa: BLE001
        return " ".join(str(x) for x in dizi)
