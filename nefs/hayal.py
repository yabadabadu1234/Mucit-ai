"""
𝒪₂ HAYAL -- **sabit değil, çok kademeli ve destekli depo** (kütük H58).

Kullanıcı hükmü:

> *"Hayal bir depodur evet ama sadece o ağaçların deposu mudur bilmiyorum,
> ve bu depo sabit değildir; sabit tarafları da vardır, anlık olanı vardır,
> sürekli olanı vardır, yenilenebileni vardır. Bunlar zihnin diğer
> melekeleri ile irtibat halindedir; neyi tutacaklarına, neyi
> yenileyeceklerine, anlık olarak ne depo açıp nereye aktaracaklarına
> **kendi karar vermez, destek alır**."*

Bundan çıkan üç şart ve karşılıkları:

1. **Üç kademe.** ``SABİT`` (görev boyunca değişmez -- şahit blokları),
   ``SÜREKLİ`` (yavaş yenilenir -- çıkarılmış münasebetler),
   ``ANLIK`` (tek bir kapı dizisi boyunca yaşar -- çalışma yeri).
2. **Yazma yetkisi dışarıdadır.** ``Hayal`` kendi kendine hiçbir şey
   tahsis etmez; her tahsis bir **destekçi** meleke adıyla yapılır ve
   defterde o isimle durur. Destekçisiz tahsis reddedilir -- bu bir
   sıhhat şartı değil, hükmün kendisidir.
3. **Anlık kademe TEMİZLENİR.** Yardımcı kübit bırakıp gitmek,
   dolaşıklığı çöp olarak orada bırakmaktır ve girişimi (interference)
   öldürür -- Grover devresinin çalışmamasının klasik sebebi budur.
   Onun için anlık kademeye vurulan her kapı **kaydedilir** ve ters
   sırayla eşleniği (``U†``) vurularak geri alınır: *tersinir devre*.

**Neden ters alma şart.** ``|ψ⟩|çöp⟩`` hâlinde çöp kübiti hangi dalı
seçtiğini "bilir"; farklı dallar artık birbirine karışamaz, genlikler
toplanamaz. Çöp temizlenince ``|ψ'⟩|0⟩`` olur ve dallar tekrar
girişebilir. Ölçülür: aşağıda hem geri alma hatası hem de temizlemeden
kalan dolaşıklık raporlanır.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from .agac import AgacYazmaci

__all__ = ["KADEMELER", "Kayit", "Hayal"]

#: Kademeler ve ömürleri.
KADEMELER: Tuple[str, ...] = ("sabit", "sürekli", "anlık")


@dataclass
class Kayit:
    """Bir kapının izi -- geri almak için gereken her şey."""
    cesit: str                                   # "tek" | "çift"
    hucreler: Tuple[Tuple[int, int], ...]
    G: np.ndarray
    destekci: str


@dataclass
class Tahsis:
    ad: str
    kademe: str
    hucreler: Tuple[Tuple[int, int], ...]
    destekci: str


class Hayal:
    """Ağaç yapraklarının tahsis defteri ve anlık kademenin temizleyicisi."""

    def __init__(self, ag: AgacYazmaci) -> None:
        self.ag = ag
        self.defter: Dict[str, Tahsis] = {}
        self.iz: List[Kayit] = []          # yalnız ANLIK kademenin izi
        self.temizlik_hatasi: float = float("nan")

    # -----------------------------------------------------------------
    def ac(self, ad: str, hucreler: Sequence[Tuple[int, int]],
           kademe: str, destekci: str) -> Tahsis:
        """Depo aç. ``destekci`` boşsa **reddedilir** (H58, 2. şart)."""
        if kademe not in KADEMELER:
            raise ValueError("kademe: %s değil" % (KADEMELER,))
        if not destekci:
            raise PermissionError(
                "hayal kendi kendine tahsis edemez; destekçi meleke lazım")
        if ad in self.defter:
            raise KeyError("zaten tahsisli: %s" % ad)
        t = Tahsis(ad, kademe, tuple(map(tuple, hucreler)), destekci)
        self.defter[ad] = t
        return t

    def aktar(self, ad: str, yeni_kademe: str, destekci: str) -> None:
        """Anlık depoyu sürekliye (yahut tersine) taşı -- *"nereye
        aktaracağına kendi karar vermez"*: burada da destekçi şarttır."""
        if not destekci:
            raise PermissionError("aktarma da destekçi ister")
        t = self.defter[ad]
        if t.kademe == "sabit":
            raise PermissionError("sabit kademe taşınmaz")
        t.kademe = yeni_kademe
        t.destekci = destekci

    def kademe_hucreleri(self, kademe: str) -> List[Tuple[int, int]]:
        h: List[Tuple[int, int]] = []
        for t in self.defter.values():
            if t.kademe == kademe:
                h.extend(t.hucreler)
        return h

    # -----------------------------------------------------------------
    def _anlik_mi(self, hucreler: Sequence[Tuple[int, int]]) -> bool:
        anlik = set(self.kademe_hucreleri("anlık"))
        return any(h in anlik for h in hucreler)

    def tek(self, hucre: Tuple[int, int], G: np.ndarray,
            destekci: str = "") -> None:
        self.ag.tek_kapi(hucre, G)
        if self._anlik_mi([hucre]):
            self.iz.append(Kayit("tek", (tuple(hucre),),
                                 np.asarray(G, complex), destekci))

    def cift(self, a: Tuple[int, int], b: Tuple[int, int], G: np.ndarray,
             destekci: str = "") -> None:
        self.ag.cift_kapi(a, b, G)
        if self._anlik_mi([a, b]):
            self.iz.append(Kayit("çift", (tuple(a), tuple(b)),
                                 np.asarray(G, complex), destekci))

    # -----------------------------------------------------------------
    def temizle(self) -> Dict[str, float]:
        """Anlık kademeyi **tersinir olarak** geri al: ``U†`` ters sırayla.

        Netice ölçülür: geri alındıktan sonra anlık hücrelerin dağılımı
        başlangıçtaki hâline dönmeli. Dönmüyorsa ``χ`` yetmemiştir ve
        bu, gizlenmesi değil raporlanması gereken bir kusurdur.
        """
        n = len(self.iz)
        for k in reversed(self.iz):
            Gd = k.G.conj().T
            if k.cesit == "tek":
                self.ag.tek_kapi(k.hucreler[0], Gd)
            else:
                self.ag.cift_kapi(k.hucreler[0], k.hucreler[1], Gd)
        self.iz.clear()
        return {"geri_alınan_kapı": float(n),
                "kesme": float(self.ag.kesme),
                "norm": self.ag.norm()}

    # -----------------------------------------------------------------
    def durum(self) -> Dict[str, object]:
        say = {k: 0 for k in KADEMELER}
        hucre = {k: 0 for k in KADEMELER}
        for t in self.defter.values():
            say[t.kademe] += 1
            hucre[t.kademe] += len(t.hucreler)
        return {"tahsis": say, "hücre": hucre,
                "anlık_iz": len(self.iz),
                "destekçiler": sorted({t.destekci
                                       for t in self.defter.values()})}


# =====================================================================
def _gosterim() -> str:
    from .agac import AgacAyar
    from .ucagac import iki_kademeli_donme

    rng = np.random.default_rng(0)
    s = ["=== 𝒪₂ HAYAL: üç kademeli depo + tersinir temizlik (H58) ==="]

    ag = AgacYazmaci(AgacAyar(h=4, w=4, renk=2, bag=32))
    h = Hayal(ag)
    h.ac("şahitler", [(0, j) for j in range(4)], "sabit", "𝒪₁ Müşahede")
    h.ac("münasebet", [(1, j) for j in range(4)], "sürekli", "𝒪₅ Tecrit")
    h.ac("çalışma", [(2, j) for j in range(4)], "anlık", "𝒪₄ Tertip")
    s.append("  defter: %s" % h.durum())

    s += ["", "--- destekçisiz tahsis reddediliyor mu ---"]
    try:
        h.ac("kaçak", [(3, 0)], "anlık", "")
        s.append("  KUSUR: reddedilmedi")
    except PermissionError as e:
        s.append("  reddedildi: %s" % e)

    s += ["", "--- anlık kademe: kapı vur, sonra tersinir geri al ---"]
    once = np.array([ag.hucre_dagilimi((2, j)) for j in range(4)])
    once_sabit = np.array([ag.hucre_dagilimi((0, j)) for j in range(4)])
    for _ in range(6):
        a = (2, int(rng.integers(4)))
        b = (int(rng.integers(4)), int(rng.integers(4)))
        if a == b:
            continue
        G = np.linalg.qr(rng.normal(size=(4, 4))
                         + 1j * rng.normal(size=(4, 4)))[0]
        h.cift(a, b, G, destekci="𝒪₃ Muhayyile")
    orta = np.array([ag.hucre_dagilimi((2, j)) for j in range(4)])
    s.append("  kapı sonrası anlık hücrelerde âzamî sapma: %.3e"
             % float(np.abs(orta - once).max()))
    r = h.temizle()
    sonra = np.array([ag.hucre_dagilimi((2, j)) for j in range(4)])
    sonra_sabit = np.array([ag.hucre_dagilimi((0, j)) for j in range(4)])
    s.append("  geri alınan kapı: %d   norm=%.9f   toplam kesme=%.2e"
             % (int(r["geri_alınan_kapı"]), r["norm"], r["kesme"]))
    s.append("  temizlik sonrası anlık hücre hatası : %.3e"
             % float(np.abs(sonra - once).max()))
    s.append("  temizlik sonrası SABİT hücre hatası : %.3e"
             % float(np.abs(sonra_sabit - once_sabit).max()))

    s += ["", "--- aktarma: anlık → sürekli (destekçi şartıyla) ---"]
    h.aktar("çalışma", "sürekli", destekci="𝒪₂₉ Teyit")
    s.append("  %s" % h.durum())
    try:
        h.aktar("şahitler", "anlık", destekci="𝒪₄ Tertip")
        s.append("  KUSUR: sabit kademe taşındı")
    except PermissionError as e:
        s.append("  sabit kademe taşınmadı: %s" % e)

    s += ["",
          "Hüküm: hayal kendi kendine tahsis etmiyor (destekçi şart, H58),",
          "üç kademe ayrı duruyor, anlık kademe tersinir devreyle",
          "temizleniyor ve çöp bırakmıyor. Temizlik hatası χ'ya bağlıdır",
          "ve ÖLÇÜLÜP raporlanır; sıfır olduğu iddia edilmez."]
    return "\n".join(s)


if __name__ == "__main__":   # pragma: no cover
    print(_gosterim())
