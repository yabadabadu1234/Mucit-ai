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
           "yon_indisi", "oteleme_ureteci", "izafi_operator",
           "izgara_kodla", "metin_kodla", "IzafiMevki"]


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


def yon_indisi(ad: str) -> int:
    for i, (a, _, _) in enumerate(YON_ADLARI):
        if a == ad:
            return i
    raise KeyError("bilinmeyen yön: %s" % ad)


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

def oteleme_ureteci(n: int, yon: int = +1) -> np.ndarray:
    """``T̂`` -- ``n`` yuvalı çevrimsel öteleme (permütasyon dizeyi).

    **Çevrimsel** olması kasıtlıdır: uçta durmak bir hudut koymaktır ve
    padişahın hükmü hudut koymamaktır. Çevrimsel öteleme ortogonaldir
    (``T̂ᵀT̂ = I``), tersi ``T̂ᵀ``dir ve ``T̂ⁿ = I``dir -- yani ``n``
    sonlu olsa da *kenar* yoktur, yalnız devir vardır.
    """
    n = int(n)
    if n < 1:
        raise ValueError("n ≥ 1 olmalı")
    T = np.zeros((n, n))
    for i in range(n):
        T[(i + int(yon)) % n, i] = 1.0
    return T


def izafi_operator(nx: int, ny: int, dx: int, dy: int) -> np.ndarray:
    """``𝒟(Δx,Δy) = T̂_x^{Δx} ⊗ T̂_y^{Δy}`` -- iki boyutlu izafî kayma.

    Netice ortogonaldir ve **hiçbir mutlak koordinat taşımaz**: yalnız
    "şu kadar sağ, şu kadar yukarı" bilgisi vardır. Aynı operatör
    ızgaranın her yerinde aynı manaya gelir; genelleme buradan doğar.
    """
    Tx = np.linalg.matrix_power(oteleme_ureteci(nx, +1), int(dx) % int(nx))
    Ty = np.linalg.matrix_power(oteleme_ureteci(ny, +1), int(dy) % int(ny))
    return np.kron(Tx, Ty)


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


def izgara_kodla(g: np.ndarray, k: Optional[Kodlayici] = None,
                 dolgu: int = -1) -> Dict[str, object]:
    """Izgarayı **izafî** komşuluk örüntülerine çevir -- koordinatsız.

    Her hücre için sekiz komşusuna bakılır; ızgaranın dışı ``dolgu``
    ile işaretlenir (bir renk değil, "burada bir şey yok" demektir ve
    ayrı bir semboldür -- kaba sıfırlama değil, ``H14``e uygun).

    Dönen ``dizi``, belirteç dizisidir ve ``<izgara_bas>``,
    ``<satır_ayır>``, ``<izgara_son>`` ile çerçevelenir; yani metinle
    **aynı** akışta taşınır ve aynı melekelerden geçer.
    """
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


def metin_kodla(metin: str, k: Optional[Kodlayici] = None
                ) -> Dict[str, object]:
    """Metni aynı akışa kat -- ``Δ = (+1, 0)`` doğrusal komşulukla.

    ARC ızgarası ile izahat metni ve Python çözüm kodu **aynı** dizide
    yürür; ayrı iki dünya yoktur (padişahın hükmü).
    """
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
        D = izafi_operator(nx, ny, dx, dy)
        dik = float(np.linalg.norm(D.T @ D - np.eye(nx * ny)))
        s.append("     %-10s Δ=(%+d,%+d)  ‖DᵀD−I‖ = %.2e" % (ad, dx, dy, dik))
    Dr = izafi_operator(nx, ny, 1, 0)
    Dl = izafi_operator(nx, ny, -1, 0)
    s.append("     sağ ∘ sol = I : %.2e"
             % float(np.linalg.norm(Dr @ Dl - np.eye(nx * ny))))

    s.append("")
    s.append("  2) Aynı örüntü ızgaranın HER YERİNDE aynı kodlanıyor mu?")
    A = np.zeros((6, 6), int)
    A[1, 1] = 3; A[1, 2] = 5
    B = np.zeros((6, 6), int)
    B[4, 3] = 3; B[4, 4] = 5
    ra = izgara_kodla(A)["izafi"]
    rb = izgara_kodla(B)["izafi"]
    ka = [x.kod() for x in ra if x.merkez == 3][0]
    kb = [x.kod() for x in rb if x.merkez == 3][0]
    s.append("     sol üstteki örüntü : %s" % (ka,))
    s.append("     sağ alttaki örüntü : %s" % (kb,))
    s.append("     AYNI MI: %s   ← mutlak koordinat olsaydı olmazdı"
             % (ka == kb))

    s.append("")
    s.append("  3) Izgara ve metin AYNI akışta")
    g = izgara_kodla(np.array([[1, 2], [3, 4]]))
    m = metin_kodla("kırmızı kare sağa kayar")
    s.append("     ızgara dizisi  : %s" % g["dizi"])
    s.append("     metin dizisi   : %d belirteç (%s)"
             % (len(m["dizi"]), m["kodlayıcı"]))
    s.append("     ikisi de aynı sözlükte; ayrı iki dünya yok.")
    return "\n".join(s)


if __name__ == "__main__":   # pragma: no cover
    print(rapor())
