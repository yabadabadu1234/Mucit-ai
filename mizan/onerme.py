"""
Önerme temsili: hash-consing'li formül düğümleri ve **tam** doğruluk tablosu.

İki tasarım kararı, ikisi de ölçülebilir gerekçeye dayanıyor:

**1. Hash-consing (yapısal paylaşım).** Aynı alt formül bir kere kurulur;
ikinci kuruluş aynı nesneyi geri verir. Bunun üç neticesi var:

  * eşitlik ``is`` ile, yani O(1) -- ağaç karşılaştırması yok,
  * bellek, formül sayısıyla değil AYRI alt formül sayısıyla büyür,
  * bellekleme (memoization) formül ``kimlik``iyle anahtarlanabilir.

**2. Bit-paralel doğruluk tablosu.** Bir formülün $n$ değişken üzerindeki
BÜTÜN $2^n$ değerlemedeki doğruluğu, tek bir $2^n$ bitlik tam sayıda
tutulur. O zaman:

    ¬A  ↦  ~a & maske        A∧B  ↦  a & b        A∨B  ↦  a | b

Yani bütün tablo, düğüm başına **bir** tam sayı işlemiyle hesaplanır;
değerleme başına ayrı geçiş yoktur. Klasik yol düğüm başına $2^n$ adım
ister; bu yol $2^n$ biti tek işlemde çevirir. Ölçüldü ve
``test_mizan.py``de kıyaslanıyor.

Bu bir yaklaşıklık DEĞİLDİR: tablo tamdır, totoloji kararı kesindir.
"""
from __future__ import annotations

from typing import Dict, FrozenSet, Iterable, List, Optional, Sequence, Tuple

# --- düğüm etiketleri -------------------------------------------------
DOGRU, YANLIS, DEG, DEGIL, VE, VEYA, ISE, ANCAK, XOR = range(9)
# Kiplik işlemcileri: önermeler mantığına ait DEĞİLDİR; ``Tablo`` onları
# reddeder ve ``kiplik.py``ye havale eder. Aynı düğüm tablosunu
# paylaşmaları, hash-consing'in kiplikli formüllerde de işlemesi
# içindir.
KUTU, ELMAS = 9, 10

_ETIKET_ADI = {DOGRU: "⊤", YANLIS: "⊥", DEG: "", DEGIL: "¬", VE: "∧",
               VEYA: "∨", ISE: "→", ANCAK: "↔", XOR: "⊻",
               KUTU: "□", ELMAS: "◇"}


class Onerme:
    """Hash-consing'li önerme düğümü.

    Doğrudan kurulmaz; ``deg``, ``degil``, ``ve`` … kurucuları kullanılır.
    ``kimlik`` süreç içinde tektir ve bellekleme anahtarıdır.
    """

    __slots__ = ("etiket", "ad", "altlar", "kimlik", "_hash", "_degiskenler")

    def __init__(self, etiket: int, ad: Optional[str],
                 altlar: Tuple["Onerme", ...], kimlik: int) -> None:
        self.etiket = etiket
        self.ad = ad
        self.altlar = altlar
        self.kimlik = kimlik
        self._hash = hash((etiket, ad, tuple(a.kimlik for a in altlar)))
        self._degiskenler: Optional[FrozenSet[str]] = None

    # -- protokol -----------------------------------------------------
    def __hash__(self) -> int:
        return self._hash

    def __eq__(self, obur: object) -> bool:
        # hash-consing sayesinde kimlik karşılaştırması YETERLİDİR
        return self is obur

    def __repr__(self) -> str:
        return yaz(self)

    # -- sorgular -----------------------------------------------------
    def degiskenler(self) -> FrozenSet[str]:
        if self._degiskenler is None:
            if self.etiket == DEG:
                self._degiskenler = frozenset({self.ad})       # type: ignore[arg-type]
            else:
                k: set = set()
                for a in self.altlar:
                    k |= a.degiskenler()
                self._degiskenler = frozenset(k)
        return self._degiskenler

    def boyut(self) -> int:
        """AYRI alt formül sayısı (paylaşım sayılmaz)."""
        gorulen: set = set()
        yigin = [self]
        while yigin:
            d = yigin.pop()
            if d.kimlik in gorulen:
                continue
            gorulen.add(d.kimlik)
            yigin.extend(d.altlar)
        return len(gorulen)


# =====================================================================
#  Hash-consing tablosu
# =====================================================================
_TABLO: Dict[Tuple, Onerme] = {}


def _kur(etiket: int, ad: Optional[str], altlar: Tuple[Onerme, ...]) -> Onerme:
    anahtar = (etiket, ad, tuple(a.kimlik for a in altlar))
    d = _TABLO.get(anahtar)
    if d is None:
        d = Onerme(etiket, ad, altlar, len(_TABLO))
        _TABLO[anahtar] = d
    return d


def tablo_boyu() -> int:
    """Kaç AYRI alt formül kurulmuş? (bellek ölçümü için)"""
    return len(_TABLO)


# --- kurucular --------------------------------------------------------
def dogru() -> Onerme:
    return _kur(DOGRU, None, ())


def yanlis() -> Onerme:
    return _kur(YANLIS, None, ())


def deg(ad: str) -> Onerme:
    return _kur(DEG, ad, ())


def degil(a: Onerme) -> Onerme:
    return _kur(DEGIL, None, (a,))


def ve(*parcalar: Onerme) -> Onerme:
    if not parcalar:
        return dogru()
    d = parcalar[0]
    for p in parcalar[1:]:
        d = _kur(VE, None, (d, p))
    return d


def veya(*parcalar: Onerme) -> Onerme:
    if not parcalar:
        return yanlis()
    d = parcalar[0]
    for p in parcalar[1:]:
        d = _kur(VEYA, None, (d, p))
    return d


def ise(a: Onerme, b: Onerme) -> Onerme:
    return _kur(ISE, None, (a, b))


def ancak(a: Onerme, b: Onerme) -> Onerme:
    return _kur(ANCAK, None, (a, b))


def xor(a: Onerme, b: Onerme) -> Onerme:
    return _kur(XOR, None, (a, b))


def kutu(a: Onerme) -> Onerme:
    """``□A`` -- zorunluluk. Değerlendirmesi ``kiplik.py``dedir."""
    return _kur(KUTU, None, (a,))


def elmas(a: Onerme) -> Onerme:
    """``◇A`` -- imkân. ``◇A ≡ ¬□¬A`` özdeşliği orada sınanır."""
    return _kur(ELMAS, None, (a,))


def yaz(d: Onerme) -> str:
    e = d.etiket
    if e == DEG:
        return d.ad or "?"
    if e in (DOGRU, YANLIS):
        return _ETIKET_ADI[e]
    if e in (DEGIL, KUTU, ELMAS):
        return "%s%s" % (_ETIKET_ADI[e], yaz(d.altlar[0]))
    return "(%s %s %s)" % (yaz(d.altlar[0]), _ETIKET_ADI[e], yaz(d.altlar[1]))


# =====================================================================
#  Bit-paralel doğruluk tablosu
# =====================================================================
class Tablo:
    """``n`` değişken üzerindeki bütün ``2ⁿ`` değerlemenin taşıyıcısı.

    Bir formülün doğruluk **sütunu**, ``2ⁿ`` bitlik tek bir tam sayıdır.
    ``k``. değişkenin sütunu, ``2^k`` uzunluğunda ardışık blokların
    dönüşümlü tekrarıdır; bu, standart doğruluk tablosu dizilişidir ve
    bir kere kurulup saklanır.
    """

    __slots__ = ("degiskenler", "yer", "n", "maske", "_sutun", "_onbellek")

    def __init__(self, degiskenler: Sequence[str]) -> None:
        self.degiskenler = tuple(sorted(set(degiskenler)))
        self.yer = {ad: i for i, ad in enumerate(self.degiskenler)}
        self.n = len(self.degiskenler)
        if self.n > 20:
            raise ValueError("bit-paralel tablo 20 değişkene kadar; %d verildi"
                             % self.n)
        self.maske = (1 << (1 << self.n)) - 1
        self._sutun: List[int] = [self._degisken_sutunu(k) for k in range(self.n)]
        self._onbellek: Dict[int, int] = {}

    def _degisken_sutunu(self, k: int) -> int:
        """``k``. değişkenin sütunu: ``2^k`` sıfır, ``2^k`` bir, tekrar.

        Yani ``i``. bit, ``(i >> k) & 1`` ise kuruludur -- standart
        doğruluk tablosu dizilişi.

        Desen KATLAYARAK üretilir (``sonuc |= sonuc << genişlik``), tek
        tek tekrarlanarak değil: dönem sayısı ``2^{n-k-1}`` olduğundan
        naif tekrar ``n=20, k=0`` için 524 288 büyük tam sayı işlemi
        ister; katlama ``n-k`` işlem ister. Netice birebir aynıdır.
        """
        blok = (1 << (1 << k)) - 1           # 2^k tane 1
        desen = blok << (1 << k)             # dönemin ÜST yarısı 1
        sonuc = desen
        genislik = 1 << (k + 1)              # bir dönemin bit uzunluğu
        hedef = 1 << self.n
        while genislik < hedef:
            sonuc |= sonuc << genislik
            genislik <<= 1
        return sonuc & self.maske

    # -- değerlendirme ------------------------------------------------
    def sutun(self, d: Onerme) -> int:
        """Formülün bütün değerlemelerdeki doğruluk sütunu."""
        onb = self._onbellek.get(d.kimlik)
        if onb is not None:
            return onb
        e = d.etiket
        if e == DOGRU:
            s = self.maske
        elif e == YANLIS:
            s = 0
        elif e == DEG:
            s = self._sutun[self.yer[d.ad]]                 # type: ignore[index]
        elif e == DEGIL:
            s = ~self.sutun(d.altlar[0]) & self.maske
        elif e in (KUTU, ELMAS):
            raise ValueError(
                "kiplikli formül önermeler tablosunda değerlendirilemez: %s"
                % yaz(d))
        else:
            a = self.sutun(d.altlar[0])
            b = self.sutun(d.altlar[1])
            if e == VE:
                s = a & b
            elif e == VEYA:
                s = a | b
            elif e == ISE:
                s = (~a | b) & self.maske
            elif e == ANCAK:
                s = ~(a ^ b) & self.maske
            else:                                            # XOR
                s = a ^ b
        self._onbellek[d.kimlik] = s
        return s

    def degerle(self, d: Onerme, atama: Dict[str, bool]) -> bool:
        """Tek bir değerlemede doğruluk."""
        i = 0
        for ad, k in self.yer.items():
            if atama.get(ad, False):
                i |= 1 << k
        return bool((self.sutun(d) >> i) & 1)

    def dogru_sayisi(self, d: Onerme) -> int:
        return bin(self.sutun(d)).count("1")


def _tablo_kur(formuller: Iterable[Onerme]) -> Tablo:
    v: set = set()
    for f in formuller:
        v |= f.degiskenler()
    return Tablo(sorted(v) or ["_"])


# --- karar usulleri ---------------------------------------------------
def totoloji_mi(d: Onerme) -> bool:
    t = _tablo_kur([d])
    return t.sutun(d) == t.maske


def tutarli_mi(d: Onerme) -> bool:
    t = _tablo_kur([d])
    return t.sutun(d) != 0


def denk_mi(a: Onerme, b: Onerme) -> bool:
    t = _tablo_kur([a, b])
    return t.sutun(a) == t.sutun(b)


def gecerli_mi(oncüller: Sequence[Onerme], netice: Onerme) -> bool:
    """``P₁,…,Pₙ ⊨ Q``: öncüllerin doğru olduğu HER değerlemede netice de
    doğru mu?

    Bu, T37'nin tashihinin fiilî karşılığıdır: geçerlilik, çelişkisizlik
    değil, gerektirmenin her modelde doğru olmasıdır.
    """
    t = _tablo_kur(list(oncüller) + [netice])
    on = t.maske
    for p in oncüller:
        on &= t.sutun(p)
    return (on & ~t.sutun(netice) & t.maske) == 0


def karsi_ornek(oncüller: Sequence[Onerme], netice: Onerme
                ) -> Optional[Dict[str, bool]]:
    """Geçersizse bir karşı örnek verir; geçerliyse ``None``."""
    t = _tablo_kur(list(oncüller) + [netice])
    on = t.maske
    for p in oncüller:
        on &= t.sutun(p)
    kotu = on & ~t.sutun(netice) & t.maske
    if kotu == 0:
        return None
    i = (kotu & -kotu).bit_length() - 1          # en düşük kurulu bit
    return {ad: bool((i >> k) & 1) for ad, k in t.yer.items()}
