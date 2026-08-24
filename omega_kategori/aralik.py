"""
Aralık (I) cebri ve yüz (face / kofibrasyon) kafesi.

CCHM kübik tip teorisinin zeminidir. İki AYRI kafes vardır ve bunları
birbirine karıştırmak, kübik çekirdek yazarken yapılan en yaygın hatadır:

  1) Aralık I: ``{i, ~i}`` üreteçleri üzerine kurulu SERBEST DE MORGAN
     CEBRİ'dir. Burada ``i ∧ ~i = 0`` DEĞİLDİR -- tümleyen (complement)
     kanunu yoktur. Yalnızca dağılma ve De Morgan (``~(a∧b) = ~a ∨ ~b``)
     kanunları geçerlidir. Normal form: yutma (absorption) altında
     indirgenmiş bir DNF, yani literal kümelerinden oluşan bir antizincir.

  2) Yüz kafesi (kofibrasyonlar): ``(i=0)`` ve ``(i=1)`` atomlarından
     kurulur ve BURADA ``(i=0) ∧ (i=1) = ⊥`` olur. Kan işlemlerinin
     üzerinde tanımlandığı "kenar şartları" bu kafeste yaşar.

İkisi arasındaki köprü ``aralik_esitligi(r, epsilon)`` fonksiyonudur:
bir aralık ifadesinin 0'a yahut 1'e eşit olma şartını yüz kafesine indirger.
"""
from __future__ import annotations

from typing import Dict, FrozenSet, Iterable, List, Tuple

# Bir literal: (degisken_adi, pozitif_mi).  (i, True) = i,  (i, False) = ~i
Literal = Tuple[str, bool]
# Bir cümle (clause): literallerin ÇARPIMI (meet)
Cumle = FrozenSet[Literal]


def _antizincire_indir(cumleler: Iterable[Cumle]) -> FrozenSet[Cumle]:
    """Yutma kanunu: ``A ∨ (A ∧ B) = A``.

    Bir cümle, başka bir cümlenin üst kümesiyse gereksizdir (daha zayıftır)
    ve atılır. Geriye kapsama sıralamasına göre bir ANTİZİNCİR kalır; bu,
    serbest dağılmalı kafesin kanonik normal formudur.

    Hız: bu fonksiyon çekirdeğin en sıcak noktasıdır (ölçüldü). Uzunluğa
    göre sıralanınca her hakiki alt küme DAHA ÖNCE gelir, dolayısıyla
    yalnız önek taranır; eşit uzunlukta iki farklı cümle birbirinin alt
    kümesi olamaz.
    """
    kume = {frozenset(c) for c in cumleler}
    if len(kume) <= 1:
        return frozenset(kume)
    kalan = sorted(kume, key=len)
    sonuc: List[Cumle] = []
    for c in kalan:
        for d in sonuc:
            if d <= c:
                break
        else:
            sonuc.append(c)
    return frozenset(sonuc)


class Aralik:
    """Serbest De Morgan cebrinin bir elemanı; DNF (cümlelerin birleşimi)."""

    __slots__ = ("cumleler",)

    def __init__(self, cumleler: Iterable[Cumle]) -> None:
        self.cumleler: FrozenSet[Cumle] = _antizincire_indir(cumleler)

    # ---- kurucular -----------------------------------------------------
    @staticmethod
    def degisken(ad: str) -> "Aralik":
        return Aralik([frozenset({(ad, True)})])

    @staticmethod
    def _literal(ad: str, pozitif: bool) -> "Aralik":
        return Aralik([frozenset({(ad, pozitif)})])

    # ---- kafes işlemleri ------------------------------------------------
    def ve(self, obur: "Aralik") -> "Aralik":
        """Meet (∧). Dağıtarak DNF'de kalır."""
        return Aralik(a | b for a in self.cumleler for b in obur.cumleler)

    def veya(self, obur: "Aralik") -> "Aralik":
        """Join (∨)."""
        return Aralik(self.cumleler | obur.cumleler)

    def degil(self) -> "Aralik":
        """De Morgan involüsyonu (~). ``~(⋁ᵢ ⋀ⱼ lᵢⱼ) = ⋀ᵢ ⋁ⱼ ~lᵢⱼ``."""
        sonuc = BIR
        for cumle in self.cumleler:
            if not cumle:          # boş çarpım = 1  =>  ~1 = 0
                return SIFIR
            ayrik = SIFIR
            for (ad, pozitif) in cumle:
                ayrik = ayrik.veya(Aralik._literal(ad, not pozitif))
            sonuc = sonuc.ve(ayrik)
        return sonuc               # boş birleşim = 0  =>  ~0 = 1

    # ---- yerine koyma ---------------------------------------------------
    def yerine_koy(self, atama: Dict[str, "Aralik"]) -> "Aralik":
        """``i ↦ r`` aralık ikamesi. Değişkenler eşzamanlı değiştirilir."""
        # erken çıkış: ikame bu ifadeye hiç dokunmuyorsa kopya üretme
        if not atama or not (self.degiskenler() & atama.keys()):
            return self
        sonuc = SIFIR
        for cumle in self.cumleler:
            carpim = BIR
            for (ad, pozitif) in cumle:
                deger = atama.get(ad)
                if deger is None:
                    deger = Aralik.degisken(ad)
                carpim = carpim.ve(deger if pozitif else deger.degil())
            sonuc = sonuc.veya(carpim)
        return sonuc

    def degiskenler(self) -> FrozenSet[str]:
        return frozenset(ad for cumle in self.cumleler for (ad, _) in cumle)

    # ---- tanıma ---------------------------------------------------------
    def sifir_mi(self) -> bool:
        return len(self.cumleler) == 0

    def bir_mi(self) -> bool:
        return frozenset() in self.cumleler

    # ---- protokol -------------------------------------------------------
    def __eq__(self, obur: object) -> bool:
        return isinstance(obur, Aralik) and self.cumleler == obur.cumleler

    def __hash__(self) -> int:
        return hash(self.cumleler)

    def __repr__(self) -> str:
        if self.sifir_mi():
            return "0"
        if self.bir_mi():
            return "1"
        def cumle_yaz(c: Cumle) -> str:
            parcalar = sorted(("%s" % ad) if p else ("~%s" % ad) for (ad, p) in c)
            return "∧".join(parcalar)
        return "∨".join(sorted(cumle_yaz(c) for c in self.cumleler))


SIFIR = Aralik([])                    # 0  (boş birleşim)
BIR = Aralik([frozenset()])           # 1  (boş çarpım içeren birleşim)

# NOT: Bir ara ``ve``/``veya``/``degil``/``yerine_koy`` işlemleri belleğe
# alınmıştı (hash-consing fikri). ÖLÇÜM bunu reddetti: hız aynı kaldı,
# tepe bellek 20 MB'dan 1281 MB'a çıktı. Kaldırıldı. Kazanç, önbellekten
# değil, ``_antizincire_indir``in algoritmasından ve ``yerine_koy``un
# erken çıkışından geliyor.


# =====================================================================
#  Yüz kafesi (kofibrasyonlar)
# =====================================================================
# Bir yüz: {(i, False), (j, True)} = "(i=0) ∧ (j=1)".
# Aynı değişken hem 0 hem 1 ise yüz çelişkilidir ve düşer.
Yuz = FrozenSet[Tuple[str, bool]]


def _yuz_celiskili_mi(yuz: Yuz) -> bool:
    gorulen: Dict[str, bool] = {}
    for (ad, deger) in yuz:
        if ad in gorulen and gorulen[ad] != deger:
            return True
        gorulen[ad] = deger
    return False


class Kofibrasyon:
    """Yüz kafesinin bir elemanı: yüzlerin (conjunctive face) birleşimi."""

    __slots__ = ("yuzler",)

    def __init__(self, yuzler: Iterable[Yuz]) -> None:
        temiz = [frozenset(y) for y in yuzler if not _yuz_celiskili_mi(frozenset(y))]
        self.yuzler: FrozenSet[Yuz] = _antizincire_indir(temiz)

    # ---- kurucular -----------------------------------------------------
    @staticmethod
    def atom(ad: str, deger: bool) -> "Kofibrasyon":
        """``(ad = 1)`` eğer deger True ise, aksi hâlde ``(ad = 0)``."""
        return Kofibrasyon([frozenset({(ad, deger)})])

    # ---- kafes işlemleri ------------------------------------------------
    def ve(self, obur: "Kofibrasyon") -> "Kofibrasyon":
        return Kofibrasyon(a | b for a in self.yuzler for b in obur.yuzler)

    def veya(self, obur: "Kofibrasyon") -> "Kofibrasyon":
        return Kofibrasyon(self.yuzler | obur.yuzler)

    # ---- tanıma ---------------------------------------------------------
    def bos_mu(self) -> bool:
        """⊥ mü? (hiçbir yüzde sağlanmıyor)"""
        return len(self.yuzler) == 0

    def dogru_mu(self) -> bool:
        """⊤ mü? (her yerde sağlanıyor)"""
        return frozenset() in self.yuzler

    def kapsiyor_mu(self, yuz: Yuz) -> bool:
        """Verilen yüz üzerinde bu kofibrasyon sağlanıyor mu?

        Yüz bir "kısıt bağlamı"dır; kofibrasyonun cümlelerinden biri onun
        alt kümesiyse (yani o cümlenin şartları zaten dayatılmışsa) sağlanır.
        """
        yuz = frozenset(yuz)
        return any(c <= yuz for c in self.yuzler)

    def yerine_koy(self, atama: Dict[str, Aralik]) -> "Kofibrasyon":
        """Yüzlere aralık ikamesi uygular; ``(i=ε)[i↦r]`` = ``(r=ε)``."""
        if not atama:
            return self
        sonuc = YANLIS
        for yuz in self.yuzler:
            carpim = DOGRU
            for (ad, deger) in yuz:
                r = atama.get(ad)
                if r is None:
                    carpim = carpim.ve(Kofibrasyon.atom(ad, deger))
                else:
                    carpim = carpim.ve(aralik_esitligi(r, deger))
            sonuc = sonuc.veya(carpim)
        return sonuc

    def __eq__(self, obur: object) -> bool:
        return isinstance(obur, Kofibrasyon) and self.yuzler == obur.yuzler

    def __hash__(self) -> int:
        return hash(self.yuzler)

    def __repr__(self) -> str:
        if self.bos_mu():
            return "⊥"
        if self.dogru_mu():
            return "⊤"
        def yuz_yaz(y: Yuz) -> str:
            return "∧".join(sorted("(%s=%d)" % (ad, 1 if d else 0) for (ad, d) in y))
        return "∨".join(sorted(yuz_yaz(y) for y in self.yuzler))


YANLIS = Kofibrasyon([])              # ⊥
DOGRU = Kofibrasyon([frozenset()])    # ⊤


def aralik_esitligi(r: Aralik, deger: bool) -> Kofibrasyon:
    """Aralık kafesinden yüz kafesine köprü: ``(r = deger)`` şartı.

    ``r = ⋁ₖ ⋀ₗ lit`` olmak üzere:
      * ``r = 1``  ⟺  ⋁ₖ ⋀ₗ (lit = 1)
      * ``r = 0``  ⟺  ⋀ₖ ⋁ₗ (lit = 0)
    ve ``(i = 1) = atom(i, True)``, ``(~i = 1) = atom(i, False)``.
    """
    if deger:  # r = 1
        sonuc = YANLIS
        for cumle in r.cumleler:
            carpim = DOGRU
            for (ad, pozitif) in cumle:
                carpim = carpim.ve(Kofibrasyon.atom(ad, pozitif))
            sonuc = sonuc.veya(carpim)
        return sonuc
    # r = 0
    sonuc = DOGRU
    for cumle in r.cumleler:
        ayrik = YANLIS
        for (ad, pozitif) in cumle:
            ayrik = ayrik.veya(Kofibrasyon.atom(ad, not pozitif))
        sonuc = sonuc.ve(ayrik)
    return sonuc


def yuzu_atamaya_cevir(yuz: Yuz) -> Dict[str, Aralik]:
    """Bir yüzü, aralık değişkenleri için somut bir ikameye çevirir."""
    return {ad: (BIR if deger else SIFIR) for (ad, deger) in yuz}
