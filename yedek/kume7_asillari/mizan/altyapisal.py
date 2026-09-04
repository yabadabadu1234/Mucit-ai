"""
Yapısal-altı mantıklar (doğrusal, affine, sıkı), relevans ve kuantum.

**Yapısal kurallar bir tercih değil, bir KAYNAK muhasebesidir.** Gentzen'in
üç yapısal kuralı -- zayıflatma, büzülme, değişme -- kaldırıldığında
öncüller "kullanılabilir kaynak" hâline gelir:

    zayıflatma yok  ⟹  her öncül KULLANILMALI
    büzülme yok     ⟹  her öncül EN FAZLA BİR KERE kullanılmalı

Bu dosya, iki kuralın varlığını **anahtarlanabilir** kılar ve farkı
gösterir: aynı ardışığın hangi kural açıkken ispatlanıp hangisi
kapalıyken ispatlanamadığı ölçülür. Kaynak metinlerin "affine: zayıflatma
var, büzülme yok / sıkı: büzülme var, zayıflatma yok" tarifi böylece
sözden çıkıp sınanır hâle gelir.

**Kuantum mantık** tarafında T93'ün tashihi doğrudan uygulanır: dağılma
"her zaman bozulur" değildir; her ortolatiste

    (A∧B) ∨ (A∧C)  ≤  A ∧ (B∨C)

DÂİMA geçerlidir, ters yön ise genelde geçersizdir. İkisi de gerçek alt
uzaylarda hesaplanır.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Dict, FrozenSet, List, Optional, Sequence, Set, Tuple

import numpy as np

# =====================================================================
#  Doğrusal mantık formülleri (çarpımsal parça: ⊗, ⊸, 1)
# =====================================================================
ATOM, BIR, TENSOR, LOLLIPOP, ILE, ARTI = range(6)


class DFormul:
    """Doğrusal mantık formülü (hash'lenebilir, değişmez)."""

    __slots__ = ("etiket", "ad", "altlar", "_hash")

    def __init__(self, etiket: int, ad: Optional[str],
                 altlar: Tuple["DFormul", ...]) -> None:
        self.etiket = etiket
        self.ad = ad
        self.altlar = altlar
        self._hash = hash((etiket, ad, altlar))

    def __hash__(self) -> int:
        return self._hash

    def __eq__(self, o: object) -> bool:
        return (isinstance(o, DFormul) and o.etiket == self.etiket
                and o.ad == self.ad and o.altlar == self.altlar)

    def __repr__(self) -> str:
        e = self.etiket
        if e == ATOM:
            return self.ad or "?"
        if e == BIR:
            return "1"
        s = {TENSOR: "⊗", LOLLIPOP: "⊸", ILE: "&", ARTI: "⊕"}[e]
        return "(%r %s %r)" % (self.altlar[0], s, self.altlar[1])


def atom(ad: str) -> DFormul:
    return DFormul(ATOM, ad, ())


def bir() -> DFormul:
    return DFormul(BIR, None, ())


def tensor(a: DFormul, b: DFormul) -> DFormul:
    return DFormul(TENSOR, None, (a, b))


def lollipop(a: DFormul, b: DFormul) -> DFormul:
    return DFormul(LOLLIPOP, None, (a, b))


def ile(a: DFormul, b: DFormul) -> DFormul:
    return DFormul(ILE, None, (a, b))


def arti(a: DFormul, b: DFormul) -> DFormul:
    return DFormul(ARTI, None, (a, b))


# --- çoklu küme (multiset) bağlamı ------------------------------------
Baglam = Tuple[DFormul, ...]           # sıralı ve tekrarlı; değişme serbest


def _duzenle(g: Sequence[DFormul]) -> Baglam:
    """Değişme kuralı DÂİMA açık olduğundan bağlam kanonik sıralanır.

    Bu bir kısaltma değil, değişmenin kendisidir: sıralama, çoklu kümeyi
    tek bir kanonik temsile indirger ve bellekleme anahtarı yapar.
    """
    return tuple(sorted(g, key=repr))


def _bolmeler(g: Baglam) -> List[Tuple[Baglam, Baglam]]:
    """Bağlamı iki parçaya ayıran BÜTÜN bölmeler.

    ``⊗R`` ve ``⊸L`` kuralları kaynağı paylaştırır; hangi paylaştırmanın
    işe yarayacağı önceden bilinemez, hepsi denenir. Bölme sayısı
    ``2^{|Γ|}``dır ve küçük formüllerde tüketilebilir.
    """
    n = len(g)
    sonuc = []
    for maske in range(1 << n):
        sol = tuple(g[i] for i in range(n) if (maske >> i) & 1)
        sag = tuple(g[i] for i in range(n) if not (maske >> i) & 1)
        sonuc.append((_duzenle(sol), _duzenle(sag)))
    return sonuc


class Hesap:
    """Yapısal kuralları anahtarlanabilir ardışık hesap.

    ``zayiflatma``: kullanılmayan öncül atılabilir.
    ``buzulme``   : bir öncül birden çok kere kullanılabilir.

    Dört bileşim dört mantık verir:

        (yok, yok)     → doğrusal (linear)
        (var, yok)     → affine
        (yok, var)     → sıkı / relevans-benzeri
        (var, var)     → sezgisel (yapısal kurallar tam)
    """

    def __init__(self, zayiflatma: bool = False, buzulme: bool = False,
                 azami_derinlik: int = 14) -> None:
        self.zayiflatma = zayiflatma
        self.buzulme = buzulme
        self.azami = azami_derinlik
        # olumsuz: (bağlam, hedef) → o hükmün verildiği EN BOL bütçe
        self._onbellek: Dict[Tuple[Baglam, DFormul], int] = {}
        # olumlu: bütçeden bağımsız, ispatı bulunmuş ardışıklar
        self._olumlu: set = set()

    def ispatlanabilir(self, g: Sequence[DFormul], hedef: DFormul) -> bool:
        return self._coz(_duzenle(g), hedef, 0)

    def _coz(self, g: Baglam, hedef: DFormul, d: int) -> bool:
        if d > self.azami:
            return False
        # Derinlik sınırı bir BÜTÇEdir: "kanıtlanamaz" hükmü yalnız o bütçe
        # altında geçerlidir; daha bol bütçeyle başarabilirdi.  Bu yüzden
        # olumsuz sonuç kalan bütçeye göre anahtarlanır.  Olumlu sonuç ise
        # bütçeden bağımsızdır (bulunmuş ispat her bütçede ispattır), o
        # sebeple ayrı ve bütçesiz bir kümede saklanır — hem doğru hem ucuz.
        kalan = self.azami - d
        if (g, hedef) in self._olumlu:
            return True
        onb = self._onbellek.get((g, hedef))
        if onb is not None and onb >= kalan:
            return False
        sonuc = self._coz_iç(g, hedef, d)
        if sonuc:
            self._olumlu.add((g, hedef))
        elif onb is None or kalan > onb:
            self._onbellek[(g, hedef)] = kalan
        return sonuc

    def _coz_iç(self, g: Baglam, hedef: DFormul, d: int) -> bool:
        # --- eksen (identity) ----------------------------------------
        if len(g) == 1 and g[0] == hedef:
            return True
        if self.zayiflatma and hedef in g:
            return True
        # --- 1 ---------------------------------------------------------
        if hedef.etiket == BIR and len(g) == 0:
            return True
        if hedef.etiket == BIR and self.zayiflatma:
            return True
        for i, f in enumerate(g):
            if f.etiket == BIR:
                kalan = _duzenle(g[:i] + g[i + 1:])
                if self._coz(kalan, hedef, d + 1):
                    return True

        # --- sağ kuralları --------------------------------------------
        he = hedef.etiket
        if he == LOLLIPOP:
            a, b = hedef.altlar
            if self._coz(_duzenle(g + (a,)), b, d + 1):
                return True
        if he == TENSOR:
            a, b = hedef.altlar
            for sol, sag in _bolmeler(g):
                if self._coz(sol, a, d + 1) and self._coz(sag, b, d + 1):
                    return True
        if he == ILE:
            a, b = hedef.altlar
            if self._coz(g, a, d + 1) and self._coz(g, b, d + 1):
                return True
        if he == ARTI:
            a, b = hedef.altlar
            if self._coz(g, a, d + 1) or self._coz(g, b, d + 1):
                return True

        # --- sol kuralları --------------------------------------------
        for i, f in enumerate(g):
            kalan = _duzenle(g[:i] + g[i + 1:])
            e = f.etiket
            if e == TENSOR:
                a, b = f.altlar
                if self._coz(_duzenle(kalan + (a, b)), hedef, d + 1):
                    return True
            elif e == LOLLIPOP:
                a, b = f.altlar
                for sol, sag in _bolmeler(kalan):
                    if (self._coz(sol, a, d + 1)
                            and self._coz(_duzenle(sag + (b,)), hedef, d + 1)):
                        return True
            elif e == ILE:
                a, b = f.altlar
                if (self._coz(_duzenle(kalan + (a,)), hedef, d + 1)
                        or self._coz(_duzenle(kalan + (b,)), hedef, d + 1)):
                    return True
            elif e == ARTI:
                a, b = f.altlar
                if (self._coz(_duzenle(kalan + (a,)), hedef, d + 1)
                        and self._coz(_duzenle(kalan + (b,)), hedef, d + 1)):
                    return True

        # --- yapısal kurallar (anahtarlı) ------------------------------
        if self.buzulme:
            for i, f in enumerate(g):
                if self._coz(_duzenle(g + (f,)), hedef, d + 1):
                    return True
        if self.zayiflatma:
            for i in range(len(g)):
                if self._coz(_duzenle(g[:i] + g[i + 1:]), hedef, d + 1):
                    return True
        return False


HESAPLAR = {
    "doğrusal": Hesap(False, False),
    "affine": Hesap(True, False),
    "sıkı": Hesap(False, True),
    "sezgisel": Hesap(True, True),
}


def yapisal_hassasiyet() -> List[Dict[str, object]]:
    """Aynı ardışığın dört mantıktaki ispatlanabilirliği.

    Beklenen ve sınanan olgular:

      * ``A ⊸ (B ⊸ A)`` ZAYIFLATMA ister -- doğrusal ve sıkıda çıkmaz.
      * ``A ⊸ (A ⊗ A)`` BÜZÜLME ister -- doğrusal ve affinede çıkmaz.
      * ``A ⊗ (A ⊸ B) ⊢ B`` yapısal kural İSTEMEZ -- dördünde de çıkar.
    """
    A, B = atom("A"), atom("B")
    ornekler = [
        ("A ⊸ (B ⊸ A)   [zayıflatma ister]", (), lollipop(A, lollipop(B, A))),
        ("A ⊸ (A ⊗ A)   [büzülme ister]", (), lollipop(A, tensor(A, A))),
        ("A ⊗ (A⊸B) ⊢ B [yapısal kural İSTEMEZ]",
         (tensor(A, lollipop(A, B)),), B),
        ("A ⊗ B ⊢ A     [zayıflatma ister]", (tensor(A, B),), A),
        ("A ⊢ A & A     [yapısal kural İSTEMEZ]", (A,), ile(A, A)),
        ("A ⊢ A ⊕ B     [yapısal kural İSTEMEZ]", (A,), arti(A, B)),
    ]
    sonuc = []
    for ad, g, h in ornekler:
        kayit: Dict[str, object] = {"ardışık": ad}
        for mad, hes in HESAPLAR.items():
            kayit[mad] = hes.ispatlanabilir(g, h)
        sonuc.append(kayit)
    return sonuc


# =====================================================================
#  Relevans mantığı: değişken paylaşımı
# =====================================================================
def _degiskenler(f: DFormul) -> FrozenSet[str]:
    if f.etiket == ATOM:
        return frozenset({f.ad})                            # type: ignore[arg-type]
    k: Set[str] = set()
    for a in f.altlar:
        k |= _degiskenler(a)
    return frozenset(k)


def degisken_paylasimi(f: DFormul) -> Optional[bool]:
    """``A → B`` biçimindeki bir formülde ``A`` ile ``B`` değişken paylaşıyor mu?

    Relevans mantığı ``R``nin taşıyıcı hususiyeti şudur: ``A → B`` bir
    teoremse ``A`` ile ``B`` en az bir önerme değişkenini paylaşır. Bu,
    "maddî gerektirme paradoksu"nun (``A → (B → A)``) niçin reddedildiğini
    açıklar: orada ``B`` ile ``A`` alâkasızdır.
    """
    if f.etiket != LOLLIPOP:
        return None
    a, b = f.altlar
    return bool(_degiskenler(a) & _degiskenler(b))


def relevans_paradokslari() -> List[Dict[str, object]]:
    A, B = atom("A"), atom("B")
    ornekler = [
        # Paylaşım ölçütü GEREK şarttır, YETER şart değildir: paylaşım
        # sağlansa da formül doğrusalda ispatlanamayabilir.  Üç örnek tam
        # olarak bu üç hâli ayırt etmek için seçildi.
        ("özdeşlik    A ⊸ A            [paylaşır, doğrusal da ispatlar]",
         lollipop(A, A)),
        ("modus ponens A ⊗ (A⊸B) ⊸ B   [paylaşır, doğrusal da ispatlar]",
         lollipop(tensor(A, lollipop(A, B)), B)),
        ("paradoks    A ⊸ (B ⊸ A)      [paylaşır ama doğrusal REDDEDER]",
         lollipop(A, lollipop(B, A))),
        ("paradoks    B ⊸ (A ⊸ A)      [PAYLAŞMAZ; ölçüt tek başına keser]",
         lollipop(B, lollipop(A, A))),
    ]
    sonuc = []
    for ad, f in ornekler:
        sonuc.append({
            "formül": ad,
            "değişken_paylaşımı": degisken_paylasimi(f),
            "doğrusalda_ispatlanabilir": HESAPLAR["doğrusal"].ispatlanabilir((), f),
            "sezgiselde_ispatlanabilir": HESAPLAR["sezgisel"].ispatlanabilir((), f),
        })
    return sonuc


# =====================================================================
#  Kuantum mantık: Hilbert uzayının kapalı alt uzayları
# =====================================================================
class AltUzay:
    """``ℝⁿ``in bir alt uzayı; ortonormal taban ile temsil edilir."""

    __slots__ = ("n", "T")

    def __init__(self, n: int, uretecler: np.ndarray) -> None:
        self.n = n
        if uretecler.size == 0:
            self.T = np.zeros((n, 0))
        else:
            U, s, _ = np.linalg.svd(uretecler.reshape(n, -1), full_matrices=False)
            r = int(np.sum(s > 1e-10))
            self.T = U[:, :r]

    @property
    def boyut(self) -> int:
        return self.T.shape[1]

    def izdusum(self) -> np.ndarray:
        if self.boyut == 0:
            return np.zeros((self.n, self.n))
        return self.T @ self.T.T

    # -- kafes işlemleri ----------------------------------------------
    def ve(self, o: "AltUzay") -> "AltUzay":
        """Kesişim: iki izdüşümün de sabit bıraktığı vektörler."""
        M = np.vstack([np.eye(self.n) - self.izdusum(),
                       np.eye(self.n) - o.izdusum()])
        _, s, Vt = np.linalg.svd(M)
        cekirdek = Vt[np.sum(s > 1e-10):].T
        return AltUzay(self.n, cekirdek)

    def veya(self, o: "AltUzay") -> "AltUzay":
        """Toplamın kapanışı (sonlu boyutta toplamın kendisi)."""
        return AltUzay(self.n, np.hstack([self.T, o.T]))

    def degil(self) -> "AltUzay":
        """Dik tümleyen."""
        if self.boyut == 0:
            return AltUzay(self.n, np.eye(self.n))
        _, s, Vt = np.linalg.svd(self.T.T)
        r = int(np.sum(s > 1e-10))
        return AltUzay(self.n, Vt[r:].T)

    def icinde_mi(self, o: "AltUzay") -> bool:
        """``self ≤ o``?"""
        if self.boyut == 0:
            return True
        return bool(np.allclose(o.izdusum() @ self.T, self.T, atol=1e-8))

    def esit_mi(self, o: "AltUzay") -> bool:
        return self.icinde_mi(o) and o.icinde_mi(self)

    def __repr__(self) -> str:
        return "AltUzay(boyut=%d)" % self.boyut


def dogru_uzay(n: int, v: Sequence[float]) -> AltUzay:
    return AltUzay(n, np.array(v, dtype=float).reshape(n, 1))


def dagilma_kirilir() -> Dict[str, object]:
    """**T93'ün fiilî sağlaması.**

    ``ℝ²``de ``A = ⟨e₁⟩``, ``B = ⟨e₂⟩``, ``C = ⟨e₁+e₂⟩``:

        B ∨ C = ℝ²,  A ∧ (B∨C) = A          (boyut 1)
        A ∧ B = 0,   A ∧ C = 0,  toplam = 0  (boyut 0)

    Yani dağılma bozulur. Fakat her ortolatiste geçerli olan
    ``(A∧B) ∨ (A∧C) ≤ A ∧ (B∨C)`` eşitsizliği SAĞLANIR -- kaynak
    metindeki "``≠``" işareti bunu gizliyordu.
    """
    A = dogru_uzay(2, [1.0, 0.0])
    B = dogru_uzay(2, [0.0, 1.0])
    C = dogru_uzay(2, [1.0, 1.0])
    sol = A.ve(B.veya(C))
    sag = (A.ve(B)).veya(A.ve(C))
    return {
        "A∧(B∨C) boyutu": sol.boyut,
        "(A∧B)∨(A∧C) boyutu": sag.boyut,
        "eşit_mi": sol.esit_mi(sag),
        "eşitsizlik (A∧B)∨(A∧C) ≤ A∧(B∨C)": sag.icinde_mi(sol),
    }


def dagilma_uyumlu_halde() -> Dict[str, object]:
    """Uyumlu (birbirine dik yahut kapsayan) alt uzaylarda dağılma SAĞLANIR.

    Bu, "``≠``" yazmanın niçin yanlış olduğunun ikinci yüzüdür: bozulma
    genel değil, husûsîdir.
    """
    A = dogru_uzay(3, [1.0, 0.0, 0.0])
    B = dogru_uzay(3, [0.0, 1.0, 0.0])
    C = dogru_uzay(3, [0.0, 0.0, 1.0])
    sol = A.ve(B.veya(C))
    sag = (A.ve(B)).veya(A.ve(C))
    return {"dik üçlüde eşit_mi": sol.esit_mi(sag),
            "iki tarafın da boyutu": (sol.boyut, sag.boyut)}


def ortomoduler_kanun(deneme: int = 200, n: int = 4,
                      tohum: int = 0) -> Dict[str, object]:
    """``A ≤ B ⟹ B = A ∨ (B ∧ A^⊥)``.

    Rastgele iç içe alt uzay çiftlerinde sınanır; kuantum mantığını
    ortolatisten ayıran kanun budur ve dağılmanın yerini tutar.
    """
    rng = np.random.default_rng(tohum)
    ihlal = 0
    denenen = 0
    for _ in range(deneme):
        k = int(rng.integers(1, n))
        Bt = rng.normal(size=(n, k + 1))
        B = AltUzay(n, Bt)
        A = AltUzay(n, B.T[:, :max(1, k - 1)] if B.boyut >= 2 else B.T)
        if not A.icinde_mi(B):
            continue
        denenen += 1
        sag = A.veya(B.ve(A.degil()))
        if not B.esit_mi(sag):
            ihlal += 1
    return {"denenen": denenen, "ihlal": ihlal, "kanun_geçerli": ihlal == 0}


# =====================================================================
#  Rapor
# =====================================================================
def rapor() -> str:
    satir = ["=== yapısal-altı mantıklar ===",
             "%-42s %-9s %-8s %-6s %s"
             % ("ardışık", "doğrusal", "affine", "sıkı", "sezgisel")]
    for k in yapisal_hassasiyet():
        satir.append("%-42s %-9s %-8s %-6s %s"
                     % (k["ardışık"], k["doğrusal"], k["affine"],
                        k["sıkı"], k["sezgisel"]))
    satir.append("")
    satir.append("Relevans: değişken paylaşımı ölçütü")
    for k in relevans_paradokslari():
        satir.append("  %-44s paylaşım=%s  doğrusal=%s"
                     % (k["formül"], k["değişken_paylaşımı"],
                        k["doğrusalda_ispatlanabilir"]))
    satir.append("")
    d = dagilma_kirilir()
    satir.append("Kuantum mantık (ℝ²):")
    satir.append("  A∧(B∨C) boyut=%d   (A∧B)∨(A∧C) boyut=%d   eşit=%s"
                 % (d["A∧(B∨C) boyutu"], d["(A∧B)∨(A∧C) boyutu"], d["eşit_mi"]))
    satir.append("  DÂİMA geçerli eşitsizlik sağlanıyor: %s"
                 % d["eşitsizlik (A∧B)∨(A∧C) ≤ A∧(B∨C)"])
    u = dagilma_uyumlu_halde()
    satir.append("  uyumlu (dik) üçlüde dağılma sağlanıyor: %s" % u["dik üçlüde eşit_mi"])
    o = ortomoduler_kanun()
    satir.append("  ortomodüler kanun: %d denemede %d ihlal → %s"
                 % (o["denenen"], o["ihlal"], o["kanun_geçerli"]))
    return "\n".join(satir)


if __name__ == "__main__":
    print(rapor())
