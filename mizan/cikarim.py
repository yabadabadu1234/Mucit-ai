"""
Çıkarım hesapları: Hilbert, Gentzen ardışık hesabı (LK) ve sezgisel (G4ip).

Bu dosyanın en kıymetli tarafı, **birbirinden bağımsız iki karar
usulünün** aynı neticeyi vermesidir:

  * ``onerme.totoloji_mi``  -- ANLAMSAL (bit-paralel doğruluk tablosu)
  * ``lk_ispatlanabilir``   -- SÖZDİZİMSEL (ters yönlü LK ispat araması)

İkisi bağımsız yazıldı; ``test_mizan.py`` binlerce formülde uyuştuklarını
sınıyor. Uyuşma, LK'nın önermeler mantığı için **eksiksizliğinin** fiilî
sağlamasıdır. Bir uyuşmazlık ya kurallarda ya tabloda hata demektir.

**Sezgisel hesap.** LJ'nin naif ters yönlü araması ``L→`` kuralında
sonlanmayabilir (öncül tüketilmez, döngü denetimi gerekir). Bunun yerine
Dyckhoff'un **büzülmesiz** hesabı G4ip kuruldu: ``L→`` kuralı, önündeki
gerektirmenin ÖNCÜLÜNÜN şekline göre dört dala ayrılır ve her dalda ölçü
kesin azalır, dolayısıyla arama döngü denetimsiz sonlanır. Sonlanma
``test_mizan.py``de rastgele formüllerle ayrıca sınanıyor.

Klasik ile sezgisel arasındaki fark da böylece **gösterilir**: üçüncü
hâlin imkânsızlığı (``A ∨ ¬A``) ve çifte değilleme elemesi
(``¬¬A → A``) LK'da ispatlanır, G4ip'te ispatlanamaz.
"""
from __future__ import annotations

from typing import Dict, FrozenSet, List, Optional, Sequence, Set, Tuple

from .onerme import (ANCAK, DEG, DEGIL, DOGRU, ISE, Onerme, VE, VEYA, XOR,
                     YANLIS, ancak, deg, degil, dogru, ise, totoloji_mi, ve,
                     veya, xor, yanlis, yaz)

# =====================================================================
#  Hilbert--Łukasiewicz sistemi
# =====================================================================
# Üç aksiyom şeması + tek çıkarım kuralı (modus ponens).


def hilbert_aksiyomu(A: Onerme = None, B: Onerme = None,
                     C: Onerme = None, no: int = 1,
                     ne: str = "kur"):
    """HANGİ AKSİYOM ŞEMASI -- tek terkip (kütük H226).

    Küme: ``aksiyom1/2/3`` (şemayı **kuran** üç isim) ve
    ``_esle_aks1/2/3`` + ``_aksiyom_ornegi_mi`` (aynı üç şemayı elle
    **eşleyen** dört isim). Yedi isim, tek amelin iki yönü idi ve
    ikisi birbirinden **kopuktu**: şema değişse eşleyicinin de elle
    değişmesi gerekiyordu; ikisinin ayrı yazılması sessiz bir kayma
    kapısıydı.

    Terkipte şema **bir kere** yazılır, eşleme ondan **türetilir**:
    şema taze meta-değişkenlerle kurulur ve formül ona
    **birleştirme** (unification) ile eşlenir. Böylece eşleyicinin
    şemadan sapması cebren imkânsızdır.

    ==============  ==================================================
    ``ne``          döndürdüğü
    ==============  ==================================================
    ``kur``         ``no``lu şemanın ``A,B,C`` ile örneği
    ``örnek_mi``    ``A`` formülü **herhangi** bir şemanın örneği mi
    ``şema``        ``no``lu şema, meta-değişkenlerle
    ==============  ==================================================

    Şemalar (Łukasiewicz'in klasik üçlüsü):

    1. ``A → (B → A)``                       -- zayıflatma
    2. ``(A → (B → C)) → ((A → B) → (A → C))`` -- dağılma
    3. ``(¬B → ¬A) → (A → B)``               -- transpozisyon (KLASİK)

    Üçüncüsü sezgiselci hesapta **yoktur**; onunla ``¬¬A → A``
    türetilir ve hesap klasikleşir. ``sezgisel_ispatlanabilir``
    (Dyckhoff G4ip) bu farkı ölçer.
    """
    _MD = (deg("#A"), deg("#B"), deg("#C"))

    def sema(k: int, a: Onerme, b: Onerme, c: Onerme) -> Onerme:
        if k == 1:
            return ise(a, ise(b, a))
        if k == 2:
            return ise(ise(a, ise(b, c)), ise(ise(a, b), ise(a, c)))
        if k == 3:
            return ise(ise(degil(b), degil(a)), ise(a, b))
        raise ValueError("aksiyom şeması bilinmiyor: %r" % (k,))

    def birlestir(kalip: Onerme, f: Onerme, bag: dict) -> bool:
        """Kalıptaki meta-değişkenler formülün alt ağaçlarına oturuyor mu?"""
        if kalip in _MD:
            onceki = bag.get(kalip)
            if onceki is None:
                bag[kalip] = f
                return True
            return onceki is f
        if kalip.etiket != f.etiket or len(kalip.altlar) != len(f.altlar):
            return False
        return all(birlestir(u, v, bag)
                   for u, v in zip(kalip.altlar, f.altlar))

    if ne == "şema":
        return sema(no, *_MD)
    if ne == "kur":
        return sema(no, A, B, C)
    if ne == "örnek_mi":
        return any(birlestir(sema(k, *_MD), A, {}) for k in (1, 2, 3))
    raise ValueError("aksiyom kipi bilinmiyor: %r" % (ne,))


AKSIYOM_NOLARI: Tuple[int, ...] = (1, 2, 3)


class HilbertHatasi(Exception):
    pass


def hilbert_denetle(adimlar: Sequence[Tuple[str, object]]) -> Onerme:
    """Bir Hilbert türetimini adım adım DENETLER ve son satırı verir.

    Her adım ya ``("aks", formül)`` ya ``("mp", i, j)`` biçimindedir;
    ``mp`` adımında ``i``. satır ``A``, ``j``. satır ``A → B`` olmalıdır.

    Aksiyom adımları ayrıca **totoloji olduklarına** göre değil, üç
    şemadan birinin örneği olduklarına göre denetlenir -- yoksa denetleyici
    her totolojiyi kabul eder ve hiçbir şey ispatlamış olmaz.
    """
    satirlar: List[Onerme] = []
    for k, adim in enumerate(adimlar):
        if adim[0] == "aks":
            f = adim[1]
            if not isinstance(f, Onerme):
                raise HilbertHatasi("%d. satır: formül bekleniyordu" % k)
            if not hilbert_aksiyomu(f, ne="örnek_mi"):
                raise HilbertHatasi("%d. satır aksiyom şeması değil: %s" % (k, f))
            satirlar.append(f)
        elif adim[0] == "mp":
            i, j = adim[1], adim[2]                       # type: ignore[misc]
            A, imp = satirlar[i], satirlar[j]             # type: ignore[index]
            if imp.etiket != ISE or imp.altlar[0] is not A:
                raise HilbertHatasi(
                    "%d. satır modus ponens değil: %s ile %s" % (k, A, imp))
            satirlar.append(imp.altlar[1])
        else:
            raise HilbertHatasi("%d. satır: bilinmeyen adım %r" % (k, adim[0]))
    if not satirlar:
        raise HilbertHatasi("boş türetim")
    return satirlar[-1]






def ozdeslik_turetimi(A: Onerme) -> List[Tuple[str, object]]:
    """``A → A``ın klasik beş satırlık Hilbert türetimi.

    Aksiyom şemalarından yalnız modus ponens ile; bu, sistemin
    ``A → A``yı aksiyom olarak İSTEMEDİĞİNİN ispatıdır.
    """
    AA = ise(A, A)
    return [
        ("aks", hilbert_aksiyomu(A, AA, A, no=2)),                       # 0
        ("aks", hilbert_aksiyomu(A, AA, no=1)),                          # 1
        ("mp", 1, 0),                                      # 2: (A→(A→A))→(A→A)
        ("aks", hilbert_aksiyomu(A, A, no=1)),                           # 3: A→(A→A)
        ("mp", 3, 2),                                      # 4: A→A
    ]


# =====================================================================
#  Gentzen ardışık hesabı LK (klasik)
# =====================================================================
Sekans = Tuple[FrozenSet[Onerme], FrozenSet[Onerme]]


def _sekans(sol: Sequence[Onerme], sag: Sequence[Onerme]) -> Sekans:
    return (frozenset(sol), frozenset(sag))


class LKAdim:
    """Bir ispat ağacı düğümü: kural adı, sekans, alt ispatlar."""

    __slots__ = ("kural", "sekans", "altlar")

    def __init__(self, kural: str, sekans: Sekans,
                 altlar: Tuple["LKAdim", ...] = ()) -> None:
        self.kural = kural
        self.sekans = sekans
        self.altlar = altlar

    def derinlik(self) -> int:
        return 1 + max((a.derinlik() for a in self.altlar), default=0)

    def dugum_sayisi(self) -> int:
        return 1 + sum(a.dugum_sayisi() for a in self.altlar)


def _yaz_sekans(s: Sekans) -> str:
    sol = ", ".join(sorted(yaz(f) for f in s[0]))
    sag = ", ".join(sorted(yaz(f) for f in s[1]))
    return "%s ⊢ %s" % (sol, sag)


_LK_ONBELLEK: Dict[Sekans, Optional[LKAdim]] = {}


def lk_ispat(sol: Sequence[Onerme], sag: Sequence[Onerme]) -> Optional[LKAdim]:
    """``Γ ⊢ Δ`` için KESMESİZ ispat arar.

    Bütün kurallar tersinir olduğundan geri izleme gerekmez: bir bileşik
    formül seçilir, kuralı uygulanır, alt sekanslar ispatlanır. Ölçü her
    adımda kesin azaldığı için arama sonlanır.

    Bellekleme sekans üzerinedir; aynı alt sekans farklı dallarda tekrar
    tekrar doğar (bilhassa ``L→`` ve ``R∧``'da) ve bir kere çözülmesi
    yeter. Netice değişmez.
    """
    return _lk(_sekans(sol, sag))


def _lk(s: Sekans) -> Optional[LKAdim]:
    onb = _LK_ONBELLEK.get(s)
    if onb is not None or s in _LK_ONBELLEK:
        return onb
    sonuc = _lk_coz(s)
    _LK_ONBELLEK[s] = sonuc
    return sonuc


def _lk_coz(s: Sekans) -> Optional[LKAdim]:
    sol, sag = s
    # aksiyom: ortak formül, solda ⊥, yahut sağda ⊤
    if sol & sag:
        return LKAdim("Aks", s)
    if any(f.etiket == YANLIS for f in sol):
        return LKAdim("L⊥", s)
    if any(f.etiket == DOGRU for f in sag):
        return LKAdim("R⊤", s)

    # bileşik bir formül seç ve kuralını uygula (hepsi tersinir)
    for f in sol:
        e = f.etiket
        if e == DEGIL:
            alt = _lk((sol - {f}, sag | {f.altlar[0]}))
            return LKAdim("L¬", s, (alt,)) if alt else None
        if e == VE:
            a, b = f.altlar
            alt = _lk(((sol - {f}) | {a, b}, sag))
            return LKAdim("L∧", s, (alt,)) if alt else None
        if e == VEYA:
            a, b = f.altlar
            k = sol - {f}
            l = _lk((k | {a}, sag))
            if l is None:
                return None
            r = _lk((k | {b}, sag))
            return LKAdim("L∨", s, (l, r)) if r else None
        if e == ISE:
            a, b = f.altlar
            k = sol - {f}
            l = _lk((k, sag | {a}))
            if l is None:
                return None
            r = _lk((k | {b}, sag))
            return LKAdim("L→", s, (l, r)) if r else None
        if e in (ANCAK, XOR):
            alt = _lk(((sol - {f}) | {_ac(f)}, sag))
            return LKAdim("L%s" % ("↔" if e == ANCAK else "⊻"), s,
                          (alt,)) if alt else None

    for f in sag:
        e = f.etiket
        if e == DEGIL:
            alt = _lk((sol | {f.altlar[0]}, sag - {f}))
            return LKAdim("R¬", s, (alt,)) if alt else None
        if e == VEYA:
            a, b = f.altlar
            alt = _lk((sol, (sag - {f}) | {a, b}))
            return LKAdim("R∨", s, (alt,)) if alt else None
        if e == VE:
            a, b = f.altlar
            k = sag - {f}
            l = _lk((sol, k | {a}))
            if l is None:
                return None
            r = _lk((sol, k | {b}))
            return LKAdim("R∧", s, (l, r)) if r else None
        if e == ISE:
            a, b = f.altlar
            alt = _lk((sol | {a}, (sag - {f}) | {b}))
            return LKAdim("R→", s, (alt,)) if alt else None
        if e in (ANCAK, XOR):
            alt = _lk((sol, (sag - {f}) | {_ac(f)}))
            return LKAdim("R%s" % ("↔" if e == ANCAK else "⊻"), s,
                          (alt,)) if alt else None

    return None                      # yalnız atomlar kaldı ve kesişmiyorlar


def _ac(f: Onerme) -> Onerme:
    """``↔`` ve ``⊻``yi temel bağlaçlara açar."""
    a, b = f.altlar
    if f.etiket == ANCAK:
        return ve(ise(a, b), ise(b, a))
    return ve(veya(a, b), degil(ve(a, b)))


def lk_ispatlanabilir(sol: Sequence[Onerme], sag: Sequence[Onerme]) -> bool:
    return lk_ispat(sol, sag) is not None


# =====================================================================
#  Sezgisel hesap: Dyckhoff G4ip (büzülmesiz, döngü denetimsiz)
# =====================================================================
def _olcu(f: Onerme) -> int:
    """Dyckhoff'un ağırlığı: her düğüm 1, gerektirmenin öncülü ağırlıklı.

    Bu ölçü, ``L→`` dallarının hepsinde kesin azalır; sonlanmanın delili
    budur.
    """
    e = f.etiket
    if e in (DEG, DOGRU, YANLIS):
        return 1
    if e == DEGIL:
        return _olcu(f.altlar[0]) + 2
    a, b = f.altlar
    if e == ISE:
        return _olcu(a) + _olcu(b) + 1
    if e in (VE, VEYA):
        return _olcu(a) + _olcu(b) + 1
    return _olcu(_ac(f)) + 1


_G4_ONBELLEK: Dict[Tuple[FrozenSet[Onerme], Onerme], bool] = {}


def sezgisel_ispatlanabilir(varsayimlar: Sequence[Onerme],
                            hedef: Onerme) -> bool:
    """``Γ ⇒ G`` sezgisel mantıkta ispatlanabilir mi? (G4ip)"""
    return _g4(frozenset(varsayimlar), hedef)


def _g4(G: FrozenSet[Onerme], hedef: Onerme) -> bool:
    anahtar = (G, hedef)
    onb = _G4_ONBELLEK.get(anahtar)
    if onb is not None:
        return onb
    sonuc = _g4_coz(G, hedef)
    _G4_ONBELLEK[anahtar] = sonuc
    return sonuc


def _g4_coz(G: FrozenSet[Onerme], hedef: Onerme) -> bool:
    # ⊥ solda ise her şey çıkar
    if any(f.etiket == YANLIS for f in G):
        return True
    if hedef.etiket == DOGRU:
        return True
    # eksen: atomik hedef solda duruyorsa
    if hedef in G:
        return True

    # --- tersinir SOL kuralları (öncelikli) --------------------------
    for f in G:
        e = f.etiket
        if e == VE:
            a, b = f.altlar
            return _g4((G - {f}) | {a, b}, hedef)
        if e == VEYA:
            a, b = f.altlar
            k = G - {f}
            return _g4(k | {a}, hedef) and _g4(k | {b}, hedef)
        if e == DEGIL:
            # ¬A ≡ A → ⊥ ; L→ dallarına havale et
            continue
        if e in (ANCAK, XOR):
            return _g4((G - {f}) | {_ac(f)}, hedef)

    # --- L→ : öncülün ŞEKLİNE göre dört dal --------------------------
    for f in G:
        onc = _oncul(f)
        if onc is None:
            continue
        C, B = onc
        k = G - {f}
        ce = C.etiket
        if ce in (DEG, DOGRU):
            # L0→ : C atomik ve zaten solda ise B'yi sal
            if C in G:
                return _g4(k | {B}, hedef)
            continue
        if ce == YANLIS:
            return _g4(k, hedef)          # ⊥→B aşikâr, düşür
        if ce == VE:
            c1, c2 = C.altlar
            return _g4(k | {ise(c1, ise(c2, B))}, hedef)
        if ce == VEYA:
            c1, c2 = C.altlar
            return _g4(k | {ise(c1, B), ise(c2, B)}, hedef)
        if ce == ISE:
            c1, c2 = C.altlar
            return (_g4(k | {ise(c2, B), c1}, c2) and _g4(k | {B}, hedef))
        if ce == DEGIL:
            # (¬D → B) ≡ ((D → ⊥) → B)
            d = C.altlar[0]
            return (_g4(k | {ise(yanlis(), B), d}, yanlis())
                    and _g4(k | {B}, hedef))
        if ce in (ANCAK, XOR):
            return _g4(k | {ise(_ac(C), B)}, hedef)

    # --- tersinir SAĞ kuralı -----------------------------------------
    if hedef.etiket == ISE:
        a, b = hedef.altlar
        return _g4(G | {a}, b)
    if hedef.etiket == DEGIL:
        return _g4(G | {hedef.altlar[0]}, yanlis())
    if hedef.etiket == VE:
        a, b = hedef.altlar
        return _g4(G, a) and _g4(G, b)
    if hedef.etiket in (ANCAK, XOR):
        return _g4(G, _ac(hedef))

    # --- tersinmez SAĞ kuralı: R∨ (geri izleme) ----------------------
    if hedef.etiket == VEYA:
        a, b = hedef.altlar
        return _g4(G, a) or _g4(G, b)

    return False


def _oncul(f: Onerme) -> Optional[Tuple[Onerme, Onerme]]:
    """``f`` bir gerektirme ise ``(öncül, ardıl)``; ``¬A`` ise ``(A, ⊥)``."""
    if f.etiket == ISE:
        return (f.altlar[0], f.altlar[1])
    if f.etiket == DEGIL:
        return (f.altlar[0], yanlis())
    return None


# =====================================================================
#  Rapor
# =====================================================================
def rapor() -> str:
    A, B, C = deg("A"), deg("B"), deg("C")
    satir = ["=== çıkarım hesapları ==="]

    son = hilbert_denetle(ozdeslik_turetimi(A))
    satir.append("Hilbert: A→A beş satırda türetildi, denetlendi → %s" % yaz(son))

    ornekler = [
        ("Peirce", ise(ise(ise(A, B), A), A)),
        ("üçüncü hâlin imkânsızlığı", veya(A, degil(A))),
        ("çifte değilleme elemesi", ise(degil(degil(A)), A)),
        ("çifte değilleme girişi", ise(A, degil(degil(A)))),
        ("ex falso", ise(yanlis(), A)),
        ("modus tollens", ise(ve(ise(A, B), degil(B)), degil(A))),
        ("De Morgan (→)", ise(degil(ve(A, B)), veya(degil(A), degil(B)))),
        ("De Morgan (←)", ise(veya(degil(A), degil(B)), degil(ve(A, B)))),
        ("dağılma", ancak(ve(A, veya(B, C)), veya(ve(A, B), ve(A, C)))),
    ]
    satir.append("")
    satir.append("%-28s %-8s %-8s %s" % ("formül", "klasik", "sezgisel", "tablo"))
    for ad, f in ornekler:
        satir.append("%-28s %-8s %-8s %s"
                     % (ad,
                        "✓" if lk_ispatlanabilir([], [f]) else "✗",
                        "✓" if sezgisel_ispatlanabilir([], f) else "✗",
                        "✓" if totoloji_mi(f) else "✗"))
    return "\n".join(satir)


if __name__ == "__main__":
    print(rapor())
