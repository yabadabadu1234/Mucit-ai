"""
Kiplik mantıkları: Kripke semantiği, çerçeve karşılıkları, deontik ve zaman.

**Bit-paralel dünya kümesi.** Bir formülün doğruluğu, dünyalar üzerinde
bir ALT KÜMEDİR; bu alt küme ``n`` bitlik bir tam sayıda tutulur. O zaman

    ‖¬A‖ = ~‖A‖ & tüm        ‖A∧B‖ = ‖A‖ & ‖B‖
    ‖□A‖ : w ∈ ‖□A‖ ⟺ R[w] ⊆ ‖A‖   ⟺   R[w] & ~‖A‖ == 0
    ‖◇A‖ : w ∈ ‖◇A‖ ⟺ R[w] ∩ ‖A‖ ≠ ∅

Erişilebilirlik ``R``, dünya başına bir bit maskesi olarak tutulur; ``□``
ve ``◇`` böylece dünya başına **iki** tam sayı işlemine iner.

**Çerçeve karşılıkları TÜRETİLİR, ezberlenmez.** Üç dünyalı bütün
çerçeveler (``2⁹ = 512``) sayılır ve her aksiyomun geçerli olduğu
çerçeveler ile ilgili bağıntı şartını sağlayan çerçeveler kümesi
KARŞILAŞTIRILIR. Eşitlik çıkarsa karşılık teoremi o boyutta
doğrulanmış olur:

    T ⟺ yansımalı      4 ⟺ geçişli      5 ⟺ Öklidyen
    B ⟺ simetrik       D ⟺ seri

Bu, kaynak metinlere uygulanan T85 tashihinin (``α → □◇α`` **B**'dir,
``5`` değil) fiilî sağlamasıdır.
"""
from __future__ import annotations

from itertools import product
from typing import Callable, Dict, FrozenSet, List, Optional, Sequence, Tuple

from .onerme import (ANCAK, DEG, DEGIL, DOGRU, ELMAS, ISE, KUTU, Onerme, VE,
                     VEYA, XOR, YANLIS, ancak, deg, degil, dogru, elmas, ise,
                     kutu, ve, veya, xor, yanlis, yaz)


# =====================================================================
#  Kripke çerçevesi ve modeli
# =====================================================================
class Cerceve:
    """``⟨W, R⟩``; ``R[w]`` erişilebilir dünyaların bit maskesi."""

    __slots__ = ("n", "R", "tum")

    def __init__(self, n: int, R: Sequence[int]) -> None:
        self.n = n
        self.R = tuple(R)
        self.tum = (1 << n) - 1

    # -- bağıntı şartları ---------------------------------------------
    def yansimali_mi(self) -> bool:
        return all((self.R[w] >> w) & 1 for w in range(self.n))

    def gecisli_mi(self) -> bool:
        for w in range(self.n):
            for v in range(self.n):
                if (self.R[w] >> v) & 1 and (self.R[v] & ~self.R[w] & self.tum):
                    return False
        return True

    def simetrik_mi(self) -> bool:
        return all(not ((self.R[w] >> v) & 1) or ((self.R[v] >> w) & 1)
                   for w in range(self.n) for v in range(self.n))

    def oklidyen_mi(self) -> bool:
        """``wRv ∧ wRu ⟹ vRu``."""
        for w in range(self.n):
            for v in range(self.n):
                if (self.R[w] >> v) & 1 and (self.R[w] & ~self.R[v] & self.tum):
                    return False
        return True

    def seri_mi(self) -> bool:
        return all(self.R[w] != 0 for w in range(self.n))

    def __repr__(self) -> str:
        kenar = ["%d→%d" % (w, v) for w in range(self.n)
                 for v in range(self.n) if (self.R[w] >> v) & 1]
        return "Çerçeve(%d, {%s})" % (self.n, ", ".join(kenar))


def butun_cerceveler(n: int) -> List[Cerceve]:
    """``n`` dünyalı BÜTÜN çerçeveler: ``2^{n²}`` tane."""
    if n > 3:
        raise ValueError("tam çerçeve sayımı 3 dünyaya kadar (2⁹ = 512)")
    cerceveler = []
    for kod in range(1 << (n * n)):
        R = [(kod >> (w * n)) & ((1 << n) - 1) for w in range(n)]
        cerceveler.append(Cerceve(n, R))
    return cerceveler


def dogruluk(f: Onerme, c: Cerceve, V: Dict[str, int]) -> int:
    """Formülün doğru olduğu dünyaların bit maskesi."""
    e = f.etiket
    if e == DOGRU:
        return c.tum
    if e == YANLIS:
        return 0
    if e == DEG:
        return V.get(f.ad, 0)                              # type: ignore[arg-type]
    if e == DEGIL:
        return ~dogruluk(f.altlar[0], c, V) & c.tum
    if e == KUTU:
        alt = dogruluk(f.altlar[0], c, V)
        return sum(1 << w for w in range(c.n)
                   if (c.R[w] & ~alt & c.tum) == 0)
    if e == ELMAS:
        alt = dogruluk(f.altlar[0], c, V)
        return sum(1 << w for w in range(c.n) if c.R[w] & alt)
    a = dogruluk(f.altlar[0], c, V)
    b = dogruluk(f.altlar[1], c, V)
    if e == VE:
        return a & b
    if e == VEYA:
        return a | b
    if e == ISE:
        return (~a | b) & c.tum
    if e == ANCAK:
        return ~(a ^ b) & c.tum
    return a ^ b                                            # XOR


def cerceve_gecerli_mi(f: Onerme, c: Cerceve) -> bool:
    """Formül, çerçevede BÜTÜN değerlemeler ve dünyalarda doğru mu?"""
    degiskenler = sorted(f.degiskenler())
    k = len(degiskenler)
    if k == 0:
        return dogruluk(f, c, {}) == c.tum
    if k * c.n > 12:
        raise ValueError("değerleme sayımı 2¹² ile sınırlı")
    for kod in range(1 << (k * c.n)):
        V = {ad: (kod >> (i * c.n)) & c.tum
             for i, ad in enumerate(degiskenler)}
        if dogruluk(f, c, V) != c.tum:
            return False
    return True


# =====================================================================
#  Aksiyomlar ve karşılıkları
# =====================================================================
_A = deg("p")

AKSIYOM: Dict[str, Onerme] = {
    "K": ise(kutu(ise(_A, deg("q"))), ise(kutu(_A), kutu(deg("q")))),
    "T": ise(kutu(_A), _A),
    "4": ise(kutu(_A), kutu(kutu(_A))),
    "5": ise(elmas(_A), kutu(elmas(_A))),
    "B": ise(_A, kutu(elmas(_A))),
    "D": ise(kutu(_A), elmas(_A)),
}

SART: Dict[str, Callable[[Cerceve], bool]] = {
    "K": lambda c: True,                     # her çerçevede geçerli
    "T": Cerceve.yansimali_mi,
    "4": Cerceve.gecisli_mi,
    "5": Cerceve.oklidyen_mi,
    "B": Cerceve.simetrik_mi,
    "D": Cerceve.seri_mi,
}

SART_ADI = {"K": "her çerçeve", "T": "yansımalı", "4": "geçişli",
            "5": "Öklidyen", "B": "simetrik", "D": "seri"}


def karsilik_dogrula(ad: str, n: int = 3) -> Dict[str, object]:
    """Aksiyomun geçerli olduğu çerçeveler ile şartı sağlayanlar aynı mı?"""
    f = AKSIYOM[ad]
    sart = SART[ad]
    gecerli, sartli, ayrik = set(), set(), []
    for i, c in enumerate(butun_cerceveler(n)):
        g = cerceve_gecerli_mi(f, c)
        s = sart(c)
        if g:
            gecerli.add(i)
        if s:
            sartli.add(i)
        if g != s:
            ayrik.append((i, c, g, s))
    return {
        "aksiyom": ad,
        "şart": SART_ADI[ad],
        "çerçeve_sayısı": 1 << (n * n),
        "aksiyom_geçerli": len(gecerli),
        "şartı_sağlayan": len(sartli),
        "karşılık_tam": not ayrik,
        "ayrık_örnek": ayrik[:1],
    }


def dual_ozdeslikleri(n: int = 3) -> Dict[str, bool]:
    """``◇A ≡ ¬□¬A`` ve ``□A ≡ ¬◇¬A`` bütün çerçevelerde."""
    A = deg("p")
    d1 = ancak(elmas(A), degil(kutu(degil(A))))
    d2 = ancak(kutu(A), degil(elmas(degil(A))))
    return {
        "◇A ≡ ¬□¬A": all(cerceve_gecerli_mi(d1, c) for c in butun_cerceveler(n)),
        "□A ≡ ¬◇¬A": all(cerceve_gecerli_mi(d2, c) for c in butun_cerceveler(n)),
    }


# =====================================================================
#  Deontik mantık
# =====================================================================
# T86'nın tashihi burada YAPISAL olarak uygulanır: izin işlemcisi ``Pm``
# adını taşır ve önerme değişkenleriyle çakışmaz.
def borc_mu_caiz_mi_yasak_mi(a: Onerme, ne: str = "ödev") -> Onerme:
    """BORÇ MU, CAİZ Mİ, YASAK MI -- tek terkip (kütük H226).

    Küme: ``O_``, ``Pm``, ``F_``. Üç isim, ``□``nun etrafına iki değil
    işaretinin **nereye** konduğundan ibaretti:

    ==============  ====================  ==========================
    ``ne``          formül                halkça
    ==============  ====================  ==========================
    ``ödev``        ``□φ``                yapılması gereken
    ``caiz``        ``¬□¬φ``              yapılması yasak olmayan
    ``yasak``       ``□¬φ``               yapılmaması gereken
    ==============  ====================  ==========================

    Deontik ``□`` alethik ``□``dan **seriliği** ile ayrılır (D:
    ``□φ → ◇φ``); refleksiflik (T: ``□φ → φ``) deontik mantıkta
    **istenmez**, zira "ödev olan hep yapılmış olurdu". Serilik şartının
    ihmali bu üç kipin tutarlılığını çökertir ve
    ``deontik_tutarlilik`` bunu ölçer.
    """
    if ne == "ödev":
        return kutu(a)
    if ne == "caiz":
        return degil(kutu(degil(a)))
    if ne == "yasak":
        return kutu(degil(a))
    raise ValueError("deontik kip bilinmiyor: %r" % (ne,))


def deontik_tutarlilik(n: int = 3) -> Dict[str, object]:
    """Deontik mantığın taşıyıcı şartı: ``D`` (serilik).

    ``D`` olmadan ``Oφ ∧ O¬φ`` mümkün olur, yani birbiriyle çelişen iki
    ödev aynı anda yüklenebilir. Serilik bunu imkânsız kılar; aşağıda
    ölçülür.
    """
    A = deg("p")
    celiski = ve(borc_mu_caiz_mi_yasak_mi(A),
                    borc_mu_caiz_mi_yasak_mi(degil(A)))
    seri, seri_disi = 0, 0
    for c in butun_cerceveler(n):
        # çelişkili ödev SAĞLANABİLİR mi? (bir değerleme ve dünya bul)
        bulundu = False
        for kod in range(1 << c.n):
            V = {"p": kod}
            if dogruluk(celiski, c, V):
                bulundu = True
                break
        if c.seri_mi():
            seri += int(bulundu)
        else:
            seri_disi += int(bulundu)
    return {
        "seri_çerçevede_çelişkili_ödev": seri,           # 0 olmalı
        "seri_olmayanda_çelişkili_ödev": seri_disi,      # > 0 olmalı
        "D_çelişkili_ödevi_engelliyor": seri == 0,
        "Pm_ve_F_dualleri": all(
            cerceve_gecerli_mi(
                ancak(borc_mu_caiz_mi_yasak_mi(A, "caiz"),
                      degil(borc_mu_caiz_mi_yasak_mi(A, "yasak"))), c)
            for c in butun_cerceveler(n)),
    }


# =====================================================================
#  Zaman mantığı (sonlu iz üzerinde LTL)
# =====================================================================
class Iz:
    """Sonlu bir zaman izi: ``t = 0,…,L-1`` anlarında değerlemeler."""

    __slots__ = ("L", "V")

    def __init__(self, L: int, V: Dict[str, int]) -> None:
        self.L = L
        self.V = V                     # değişken → anların bit maskesi

    def tum(self) -> int:
        return (1 << self.L) - 1


def ltl_dogruluk(f: Onerme, iz: Iz, isim: str = "") -> int:
    """Formülün doğru olduğu ANLARIN bit maskesi (gelecek işlemcileri)."""
    e = f.etiket
    if e == DOGRU:
        return iz.tum()
    if e == YANLIS:
        return 0
    if e == DEG:
        return iz.V.get(f.ad, 0)                          # type: ignore[arg-type]
    if e == DEGIL:
        return ~ltl_dogruluk(f.altlar[0], iz) & iz.tum()
    a = ltl_dogruluk(f.altlar[0], iz)
    if e in (KUTU, ELMAS):
        raise ValueError("LTL'de □/◇ yerine G/F kullanılır")
    b = ltl_dogruluk(f.altlar[1], iz)
    if e == VE:
        return a & b
    if e == VEYA:
        return a | b
    if e == ISE:
        return (~a | b) & iz.tum()
    if e == ANCAK:
        return ~(a ^ b) & iz.tum()
    return a ^ b


def bundan_sonra(a: int, b: int = -1, L: int = 0,
                 ne: str = "kadar") -> int:
    """BUNDAN SONRA NE OLACAK -- tek terkip (kütük H226).

    Küme: ``G`` (daima), ``F`` (bir an), ``U`` (-e kadar). Üçü ayrı
    yazılmıştı; hâlbuki ikisi üçüncüsünün **tanımıdır**:

        ``Fφ ≡ ⊤ U φ``          ``Gφ ≡ ¬(⊤ U ¬φ)``

    Geriye tek çekirdek kalır ve o da **tek geriye doğru taramadır**:

        ``t ∈ φUψ  ⟺  ψ(t) ∨ (φ(t) ∧ t+1 ∈ φUψ)``

    Sonlu iz üstünde bu özyineleme ``L−1``den ``0``a bir taşımayla
    okunur; ``O(L)``dur ve maskeler bit paralel tutulur.

    ==============  ==================================================
    ``ne``          döndürdüğü
    ==============  ==================================================
    ``kadar``       ``a U b``
    ``daima``       ``G a``
    ``biran``       ``F a``
    ==============  ==================================================

    **T88'in tashihli hâli**: "-e kadar"ın alt sınırı **şimdidir**.
    Kaynak metinde alt sınır yoktu (``∀t' < t``), yani sonsuz geçmişte
    de ``φ``nin sağlanması isteniyordu; oysa "-e kadar" şimdiden başlar.
    """
    tum = (1 << L) - 1
    if ne == "daima":
        a, b = tum, (~a) & tum          # G a = ¬(⊤ U ¬a)
    elif ne == "biran":
        a, b = tum, a                   # F a = ⊤ U a
    elif ne != "kadar":
        raise ValueError("zaman kipi bilinmiyor: %r" % (ne,))
    sonuc = 0
    tasima = False
    for t in range(L - 1, -1, -1):
        tasima = bool((b >> t) & 1) or (bool((a >> t) & 1) and tasima)
        if tasima:
            sonuc |= 1 << t
    return (~sonuc) & tum if ne == "daima" else sonuc


def ltl_ozdeslikleri(L: int = 6, deneme: int = 400,
                     tohum: int = 0) -> Dict[str, bool]:
    """``G``, ``F``, ``U`` arasındaki klasik özdeşlikler.

    Rastgele izlerde tam sayımla sınanır; hepsi bit maskesi eşitliğidir,
    yaklaşıklık yoktur.
    """
    import random
    rng = random.Random(tohum)
    tum = (1 << L) - 1
    ozdeslik = {
        "Gφ ≡ ¬F¬φ": True,
        "Fφ ≡ ⊤ U φ": True,
        "φUψ ⟹ Fψ": True,
        "G(φ∧ψ) ≡ Gφ ∧ Gψ": True,
    }
    for _ in range(deneme):
        a, b = rng.randrange(1 << L), rng.randrange(1 << L)
        if bundan_sonra(a, L=L, ne="daima") != (~bundan_sonra(~a & tum, L=L, ne="biran") & tum):
            ozdeslik["Gφ ≡ ¬F¬φ"] = False
        if bundan_sonra(b, L=L, ne="biran") != bundan_sonra(tum, b, L):
            ozdeslik["Fφ ≡ ⊤ U φ"] = False
        if bundan_sonra(a, b, L) & ~bundan_sonra(b, L=L, ne="biran") & tum:
            ozdeslik["φUψ ⟹ Fψ"] = False
        if (bundan_sonra(a & b, L=L, ne="daima")
                != bundan_sonra(a, L=L, ne="daima")
                & bundan_sonra(b, L=L, ne="daima")):
            ozdeslik["G(φ∧ψ) ≡ Gφ ∧ Gψ"] = False
    return ozdeslik


# =====================================================================
#  Rapor
# =====================================================================
def rapor() -> str:
    satir = ["=== kiplik: Kripke karşılıkları (3 dünyalı BÜTÜN 512 çerçeve) ===",
             "%-4s %-14s %8s %8s  %s"
             % ("aks", "şart", "geçerli", "şartlı", "karşılık tam")]
    for ad in ("K", "T", "4", "5", "B", "D"):
        r = karsilik_dogrula(ad)
        satir.append("%-4s %-14s %8d %8d  %s"
                     % (ad, r["şart"], r["aksiyom_geçerli"],
                        r["şartı_sağlayan"], r["karşılık_tam"]))
    satir.append("")
    for k, v in dual_ozdeslikleri().items():
        satir.append("dual: %-14s %s" % (k, v))
    satir.append("")
    d = deontik_tutarlilik()
    satir.append("deontik: D çelişkili ödevi engelliyor = %s"
                 % d["D_çelişkili_ödevi_engelliyor"])
    satir.append("deontik: seri OLMAYAN çerçevede çelişkili ödev bulunan = %d"
                 % d["seri_olmayanda_çelişkili_ödev"])
    satir.append("deontik: Pmφ ≡ ¬Fφ dualı = %s" % d["Pm_ve_F_dualleri"])
    satir.append("")
    for k, v in ltl_ozdeslikleri().items():
        satir.append("LTL: %-20s %s" % (k, v))
    return "\n".join(satir)


if __name__ == "__main__":
    print(rapor())
