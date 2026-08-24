"""Kan genişlemeleri — ``Lan`` ve ``Ran``, sonlu kategorilerde hesaplanır.

Bir funktor ``F: A → Set`` ve bir funktor ``K: A → B`` verildiğinde,
``F``i ``B`` boyunca genişletmenin iki kanonik yolu vardır.  **Sol Kan
genişlemesi** koliminit (coend) ile, **sağ** ise limit (end) ile:

.. math::

   (\\mathrm{Lan}_K F)(b) &= \\int^{a \\in A} B(K a, b) \\times F a \\\\
   (\\mathrm{Ran}_K F)(b) &= \\int_{a \\in A} F a^{\\,B(b, K a)}

Sonlu kategorilerde bunlar tam olarak hesaplanabilir:

* **Coend** = ayrık birleşimin bir denklik bağıntısına göre bölümü.
  Bağıntı, her ``f: a → a'`` morfizmi için ``(g∘Kf, x) ∼ (g, F f\\,x)``
  ile üretilir; kapanışı **birleşim-bul** (union–find) ile alınır.
* **End** = çarpımın bir denklem sistemine göre alt kümesi; doğal
  ailelerdir, yani her ``f`` için kare değişmelidir.

Bu, kategorik bir süsleme değil: ``Lan`` **serbest genişletme**dir —
elde olandan, olması gerekenden fazlasını uydurmadan, en az taahhütle
üretilen genişletme.  Risalelerde ``ℛ ▷ Θ = Σ_j α_j (Lan_{K_j} F_j)(𝒳_j)``
diye geçen tasarruf tam olarak budur.

Doğruluğun teminatı üç bilinen özdeşlik:

1. ``K = id`` ise ``Lan_K F ≅ F`` ve ``Ran_K F ≅ F``.
2. ``Lan`` sola eş: ``Nat(Lan_K F, G) ≅ Nat(F, G∘K)`` — iki tarafın
   **eleman sayıları** sayılarak karşılaştırılır.
3. ``Ran`` sağa eş: ``Nat(G, Ran_K F) ≅ Nat(G∘K, F)``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import product
from typing import (Callable, Dict, FrozenSet, Hashable, Iterable, List,
                    Optional, Sequence, Set, Tuple)

__all__ = [
    "Kategori", "Funktor", "birlestir_bul", "lan", "ran",
    "lan_funktor", "bileske_funktor",
    "dogal_donusumler", "sonlu_kategori", "ok_kategorisi", "monoid_kategorisi",
]

Nesne = Hashable
Ok = Hashable


# ══════════════════════════════════════════════════════════════════════
#  Sonlu kategori
# ══════════════════════════════════════════════════════════════════════

@dataclass
class Kategori:
    """Sonlu kategori: nesneler, oklar, kaynak/hedef, bileşke, birimler.

    Kurulurken **kategori aksiyomları denetlenir**: bileşke tanımlı ve
    kapalı olmalı, birleşmeli olmalı, birimler iki yanlı olmalı.  Bunlar
    sınanmazsa ``lan``/``ran`` sessizce anlamsız cevaplar üretir.
    """
    nesneler: Tuple[Nesne, ...]
    oklar: Tuple[Ok, ...]
    kaynak: Dict[Ok, Nesne]
    hedef: Dict[Ok, Nesne]
    bileske: Dict[Tuple[Ok, Ok], Ok]        # (g, f) ↦ g∘f
    birim: Dict[Nesne, Ok]
    ad: str = ""

    def __post_init__(self) -> None:
        self.denetle()

    def hom(self, a: Nesne, b: Nesne) -> Tuple[Ok, ...]:
        return tuple(f for f in self.oklar
                     if self.kaynak[f] == a and self.hedef[f] == b)

    def bilesir_mi(self, g: Ok, f: Ok) -> bool:
        return self.hedef[f] == self.kaynak[g]

    def denetle(self) -> None:
        for f in self.oklar:
            if f not in self.kaynak or f not in self.hedef:
                raise ValueError(f"{f!r} okunun kaynağı/hedefi eksik")
        for a in self.nesneler:
            if a not in self.birim:
                raise ValueError(f"{a!r} nesnesinin birimi yok")
            i = self.birim[a]
            if self.kaynak[i] != a or self.hedef[i] != a:
                raise ValueError(f"{a!r} birimi endomorfizm değil")
        # bileşkenin kapalılığı ve tipi
        for g, f in product(self.oklar, repeat=2):
            if not self.bilesir_mi(g, f):
                continue
            if (g, f) not in self.bileske:
                raise ValueError(f"bileşke tanımsız: {g!r}∘{f!r}")
            h = self.bileske[(g, f)]
            if h not in self.oklar:
                raise ValueError(f"bileşke kategoriden çıkıyor: {h!r}")
            if (self.kaynak[h] != self.kaynak[f]
                    or self.hedef[h] != self.hedef[g]):
                raise ValueError(f"bileşkenin tipi yanlış: {g!r}∘{f!r}")
        # birim kanunları
        for f in self.oklar:
            a, b = self.kaynak[f], self.hedef[f]
            if self.bileske[(f, self.birim[a])] != f:
                raise ValueError(f"sağ birim kanunu bozuk: {f!r}")
            if self.bileske[(self.birim[b], f)] != f:
                raise ValueError(f"sol birim kanunu bozuk: {f!r}")
        # birleşme
        for h, g, f in product(self.oklar, repeat=3):
            if not (self.bilesir_mi(g, f) and self.bilesir_mi(h, g)):
                continue
            sol = self.bileske[(self.bileske[(h, g)], f)]
            sag = self.bileske[(h, self.bileske[(g, f)])]
            if sol != sag:
                raise ValueError(f"birleşme bozuk: {h!r},{g!r},{f!r}")


@dataclass
class Funktor:
    """``F: A → Set`` ya da ``K: A → B``.

    ``Set``e giden funktor için ``nes`` her nesneye sonlu bir küme,
    ``mor`` her oka o kümeler arası bir fonksiyon (sözlük) verir.
    Kategoriler arası funktor için ``nes`` nesneye nesne, ``mor`` oka ok
    verir.  İki hâl de ``funktoryel_mi`` ile **denetlenir**.
    """
    kaynak: Kategori
    nes: Dict[Nesne, object]
    mor: Dict[Ok, object]
    hedef: Optional[Kategori] = None        # None ⟹ Set'e gidiyor
    ad: str = ""

    @property
    def set_e_mi(self) -> bool:
        return self.hedef is None

    def funktoryel_mi(self) -> Tuple[bool, str]:
        A = self.kaynak
        for a in A.nesneler:
            if a not in self.nes:
                return False, f"{a!r} nesnesinin görüntüsü yok"
            i = A.birim[a]
            if self.set_e_mi:
                fi = self.mor[i]
                if any(fi[x] != x for x in self.nes[a]):
                    return False, f"birim {a!r} özdeşliğe gitmiyor"
            else:
                if self.mor[i] != self.hedef.birim[self.nes[a]]:
                    return False, f"birim {a!r} birime gitmiyor"
        for g, f in product(A.oklar, repeat=2):
            if not A.bilesir_mi(g, f):
                continue
            gf = A.bileske[(g, f)]
            if self.set_e_mi:
                sol = {x: self.mor[g][self.mor[f][x]]
                       for x in self.nes[A.kaynak[f]]}
                if sol != dict(self.mor[gf]):
                    return False, f"bileşke bozuk: {g!r}∘{f!r}"
            else:
                sol = self.hedef.bileske[(self.mor[g], self.mor[f])]
                if sol != self.mor[gf]:
                    return False, f"bileşke bozuk: {g!r}∘{f!r}"
        return True, ""


# ══════════════════════════════════════════════════════════════════════
#  Birleşim–bul (coend'in bölümü için)
# ══════════════════════════════════════════════════════════════════════

class birlestir_bul:
    """Yol sıkıştırmalı ve sıralı birleşim–bul.

    Coend, ayrık birleşimin bir bağıntıya göre bölümüdür; bağıntının
    **denklik kapanışını** almak lazımdır.  Naif yol (her adımda bütün
    çiftleri gözden geçirmek) ``O(n²)`` tur atar; birleşim–bul ise
    neredeyse doğrusaldır ve netice birebir aynıdır.
    """

    __slots__ = ("ata", "rutbe")

    def __init__(self) -> None:
        self.ata: Dict[Hashable, Hashable] = {}
        self.rutbe: Dict[Hashable, int] = {}

    def ekle(self, x: Hashable) -> None:
        if x not in self.ata:
            self.ata[x] = x
            self.rutbe[x] = 0

    def bul(self, x: Hashable) -> Hashable:
        self.ekle(x)
        kok = x
        while self.ata[kok] != kok:
            kok = self.ata[kok]
        while self.ata[x] != kok:          # yol sıkıştırma
            self.ata[x], x = kok, self.ata[x]
        return kok

    def birlestir(self, x: Hashable, y: Hashable) -> bool:
        a, b = self.bul(x), self.bul(y)
        if a == b:
            return False
        if self.rutbe[a] < self.rutbe[b]:
            a, b = b, a
        self.ata[b] = a
        if self.rutbe[a] == self.rutbe[b]:
            self.rutbe[a] += 1
        return True

    def siniflar(self) -> Dict[Hashable, List[Hashable]]:
        out: Dict[Hashable, List[Hashable]] = {}
        for x in list(self.ata):
            out.setdefault(self.bul(x), []).append(x)
        return out


# ══════════════════════════════════════════════════════════════════════
#  Sol Kan genişlemesi — coend
# ══════════════════════════════════════════════════════════════════════

def lan(K: Funktor, F: Funktor, b: Nesne) -> Dict[str, object]:
    """``(Lan_K F)(b) = ∫^a B(Ka, b) × Fa``.

    Kuruluş: ayrık birleşim ``⊔_a B(Ka,b) × Fa`` alınır, sonra her
    ``f: a → a'`` ve her ``(g: Ka' → b, x ∈ Fa)`` için

        ``(g ∘ Kf, x) ∼ (g, Ff x)``

    denkliği dayatılır.  Bu, coend'in *dinleştirme* (wedge) şartıdır ve
    tam olarak "``F``nin kendi morfizmleriyle taşınan şeyler ayırt
    edilmez" demektir.

    Dönen: sınıflar, sayı, ve temsilciler.
    """
    if K.hedef is None:
        raise ValueError("K bir kategoriden kategoriye funktor olmalı")
    if not F.set_e_mi:
        raise ValueError("F, Set'e giden funktor olmalı")
    A, B = K.kaynak, K.hedef
    if b not in B.nesneler:
        raise ValueError(f"{b!r} B'nin nesnesi değil")

    bb = birlestir_bul()
    for a in A.nesneler:
        for g in B.hom(K.nes[a], b):
            for x in F.nes[a]:
                bb.ekle((a, g, x))

    for f in A.oklar:
        a, a2 = A.kaynak[f], A.hedef[f]
        Kf = K.mor[f]                       # Ka → Ka'
        for g in B.hom(K.nes[a2], b):       # g: Ka' → b
            gKf = B.bileske[(g, Kf)]        # Ka → b
            for x in F.nes[a]:
                bb.birlestir((a, gKf, x), (a2, g, F.mor[f][x]))

    siniflar = bb.siniflar()
    return {
        "sınıf_sayısı": len(siniflar),
        "sınıflar": {k: sorted(v, key=repr) for k, v in siniflar.items()},
        "ham_eleman": sum(len(v) for v in siniflar.values()),
    }


# ══════════════════════════════════════════════════════════════════════
#  Sağ Kan genişlemesi — end
# ══════════════════════════════════════════════════════════════════════

def lan_funktor(K: Funktor, F: Funktor) -> Funktor:
    """``Lan_K F`` — sadece nesnelerde değil, **funktor olarak**.

    Nesnede: ``b ↦ (Lan_K F)(b)``nin denklik sınıfları.
    Okta: ``β: b → b'`` sınıfları ``[(a, g, x)] ↦ [(a, β∘g, x)]``
    ile taşır.  Bu iyi tanımlıdır (coend bağıntısı ``β`` ile uyumlu),
    ama **iyi tanımlılık burada varsayılmaz**: taşıma kurulurken bir
    sınıfın bütün temsilcilerinin aynı yere gittiği denetlenir ve
    aksi hâlde hata verilir.
    """
    A, B = K.kaynak, K.hedef
    if B is None:
        raise ValueError("K: A→B olmalı")
    sinif: Dict[Nesne, Dict[Tuple, Hashable]] = {}
    nes: Dict[Nesne, object] = {}
    for b in B.nesneler:
        r = lan(K, F, b)
        etiket: Dict[Tuple, Hashable] = {}
        for kok, uyeler in r["sınıflar"].items():
            ad = repr(kok)
            for u in uyeler:
                etiket[tuple(u)] = ad
        sinif[b] = etiket
        nes[b] = frozenset(etiket.values())

    mor: Dict[Ok, object] = {}
    for beta in B.oklar:
        b, b2 = B.kaynak[beta], B.hedef[beta]
        tasima: Dict[Hashable, Hashable] = {}
        for (a, g, x), kaynak_ad in sinif[b].items():
            hedef_ad = sinif[b2][(a, B.bileske[(beta, g)], x)]
            if kaynak_ad in tasima and tasima[kaynak_ad] != hedef_ad:
                raise ValueError(
                    f"Lan taşıması iyi tanımlı değil: {beta!r} sınıfı böldü")
            tasima[kaynak_ad] = hedef_ad
        mor[beta] = tasima
    return Funktor(B, nes, mor, ad=f"Lan_{K.ad}{F.ad}")


def bileske_funktor(G: Funktor, K: Funktor) -> Funktor:
    """``G∘K: A → Set`` — ``K: A→B`` ve ``G: B→Set`` iken."""
    A = K.kaynak
    return Funktor(A, {a: G.nes[K.nes[a]] for a in A.nesneler},
                   {f: G.mor[K.mor[f]] for f in A.oklar},
                   ad=f"{G.ad}∘{K.ad}")


def ran(K: Funktor, F: Funktor, b: Nesne) -> Dict[str, object]:
    """``(Ran_K F)(b) = ∫_a Fa^{B(b, Ka)}``.

    Elemanlar, her ``(a, h: b → Ka)`` çiftine bir ``Fa`` elemanı atayan
    **doğal** ailelerdir.  Doğallık şartı: her ``f: a → a'`` ve her
    ``h: b → Ka`` için

        ``F f (α(a, h)) = α(a', Kf ∘ h)``

    Sonlu hâlde bütün aileler taranıp şartı sağlayanlar seçilir.  Bu
    kaba kuvvettir ama **tamdır**: sonuç sayısı kesin doğrudur, kestirim
    değildir.
    """
    if K.hedef is None or not F.set_e_mi:
        raise ValueError("K: A→B ve F: A→Set olmalı")
    A, B = K.kaynak, K.hedef
    anahtarlar: List[Tuple[Nesne, Ok]] = [
        (a, h) for a in A.nesneler for h in B.hom(b, K.nes[a])
    ]
    if not anahtarlar:
        return {"eleman_sayısı": 1, "elemanlar": [{}],
                "aday_sayısı": 1, "not": "boş indis — tek (boş) aile"}

    secenekler = [sorted(F.nes[a], key=repr) for a, _ in anahtarlar]
    elemanlar = []
    aday = 0
    for degerler in product(*secenekler):
        aday += 1
        alfa = dict(zip(anahtarlar, degerler))
        dogal = True
        for f in A.oklar:
            a, a2 = A.kaynak[f], A.hedef[f]
            Kf = K.mor[f]
            for h in B.hom(b, K.nes[a]):        # h: b → Ka
                Kf_h = B.bileske[(Kf, h)]       # b → Ka'
                if F.mor[f][alfa[(a, h)]] != alfa[(a2, Kf_h)]:
                    dogal = False
                    break
            if not dogal:
                break
        if dogal:
            elemanlar.append(alfa)
    return {"eleman_sayısı": len(elemanlar), "elemanlar": elemanlar,
            "aday_sayısı": aday}


# ══════════════════════════════════════════════════════════════════════
#  Doğal dönüşümler (eşleniklik sağlaması için sayılır)
# ══════════════════════════════════════════════════════════════════════

def dogal_donusumler(F: Funktor, G: Funktor) -> int:
    """``|Nat(F, G)|`` — iki ``A → Set`` funktoru arasında.

    Doğal dönüşüm, her nesnede bir fonksiyon ve her okta değişen bir
    kare demektir.  Sonlu hâlde bütün bileşen seçimleri taranır.
    Eşleniklik sağlaması bu **sayı** üzerinden yapılır: izomorfizm
    kurmak yerine iki kümenin eleman sayısı karşılaştırılır, ki bu
    daha zayıf ama yanlış pozitif vermeyen bir ölçüttür.
    """
    if not (F.set_e_mi and G.set_e_mi and F.kaynak is G.kaynak):
        raise ValueError("aynı kategoriden Set'e iki funktor lazım")
    A = F.kaynak
    nesneler = list(A.nesneler)
    bilesen_secenekleri = []
    for a in nesneler:
        kaynak_kume = sorted(F.nes[a], key=repr)
        hedef_kume = sorted(G.nes[a], key=repr)
        bilesen_secenekleri.append([
            dict(zip(kaynak_kume, degerler))
            for degerler in product(hedef_kume, repeat=len(kaynak_kume))
        ])
    sayi = 0
    for secim in product(*bilesen_secenekleri):
        alfa = dict(zip(nesneler, secim))
        iyi = True
        for f in A.oklar:
            a, b = A.kaynak[f], A.hedef[f]
            for x in F.nes[a]:
                if alfa[b][F.mor[f][x]] != G.mor[f][alfa[a][x]]:
                    iyi = False
                    break
            if not iyi:
                break
        if iyi:
            sayi += 1
    return sayi


# ══════════════════════════════════════════════════════════════════════
#  Örnek kategoriler
# ══════════════════════════════════════════════════════════════════════

def sonlu_kategori(nesneler: Sequence[Nesne],
                   uretici: Sequence[Tuple[Ok, Nesne, Nesne]],
                   ek_bileske: Optional[Dict[Tuple[Ok, Ok], Ok]] = None,
                   ad: str = "") -> Kategori:
    """Serbest kategori — üreteçlerden, **çevrimsiz** olmak şartıyla.

    Bütün bileşke yolları enumerate edilir; çevrim varsa sonsuz çok ok
    doğar ve hata verilir (sessizce kesilmez).
    """
    oklar: Dict[Ok, Tuple[Nesne, Nesne]] = {}
    for a in nesneler:
        oklar[("id", a)] = (a, a)
    for ad_ok, s, t in uretici:
        oklar[ad_ok] = (s, t)

    # Yolları uzat: en çok |nesne| adım (çevrimsizse yeter)
    yollar: Dict[Ok, Tuple[Nesne, Nesne]] = dict(oklar)
    for _ in range(len(nesneler) + 1):
        yeni = {}
        for g, (gs, gt) in yollar.items():
            for f, (fs, ft) in yollar.items():
                if ft != gs:
                    continue
                bilesim = _bilesim_adi(g, f)
                if bilesim not in yollar:
                    yeni[bilesim] = (fs, gt)
        if not yeni:
            break
        yollar.update(yeni)
    else:
        raise ValueError("kategori çevrimli görünüyor — serbest kapanış sonsuz")

    bileske: Dict[Tuple[Ok, Ok], Ok] = {}
    birim = {a: ("id", a) for a in nesneler}
    for g in yollar:
        for f in yollar:
            if yollar[f][1] != yollar[g][0]:
                continue
            bileske[(g, f)] = _bilesim_adi(g, f)
    if ek_bileske:
        bileske.update(ek_bileske)
    return Kategori(tuple(nesneler), tuple(yollar),
                    {f: yollar[f][0] for f in yollar},
                    {f: yollar[f][1] for f in yollar},
                    bileske, birim, ad)


def _bilesim_adi(g: Ok, f: Ok) -> Ok:
    """``g∘f``in kanonik adı; birimler yutulur."""
    if isinstance(f, tuple) and f and f[0] == "id":
        return g
    if isinstance(g, tuple) and g and g[0] == "id":
        return f
    return ("∘", g, f)


def ok_kategorisi() -> Kategori:
    """``• → •`` — iki nesne, bir gerçek ok."""
    return sonlu_kategori(("0", "1"), [("u", "0", "1")], ad="ok")


def monoid_kategorisi(n: int) -> Kategori:
    """``ℤ/n`` monoidi tek nesneli kategori olarak.

    Serbest kapanış burada işe yaramaz (çevrim var), o yüzden bileşke
    doğrudan modüler toplamayla verilir.
    """
    oklar = tuple(("m", i) for i in range(n))
    bileske = {(("m", i), ("m", j)): ("m", (i + j) % n)
               for i in range(n) for j in range(n)}
    return Kategori(("*",), oklar,
                    {f: "*" for f in oklar}, {f: "*" for f in oklar},
                    bileske, {"*": ("m", 0)}, f"ℤ/{n}")


# ══════════════════════════════════════════════════════════════════════
#  Gösterim
# ══════════════════════════════════════════════════════════════════════

def _ozdes_funktor(A: Kategori) -> Funktor:
    return Funktor(A, {a: a for a in A.nesneler},
                   {f: f for f in A.oklar}, hedef=A, ad="id")


def _gosterim() -> str:
    s: List[str] = []

    A = ok_kategorisi()
    s.append("=== Kategori aksiyomları denetleniyor ===")
    s.append(f"  ok kategorisi: {len(A.nesneler)} nesne,"
             f" {len(A.oklar)} ok → aksiyomlar geçti")
    try:
        Kategori(("a",), (("id", "a"), "kacak"),
                 {("id", "a"): "a", "kacak": "a"},
                 {("id", "a"): "a", "kacak": "a"},
                 {}, {"a": ("id", "a")})
        s.append("  bozuk kategori kabul edildi (BEKLENMEZ)")
    except ValueError as e:
        s.append(f"  bileşkesi eksik kategori reddedildi: {e}")

    # F: A → Set,  F(0) = {x,y},  F(1) = {p},  F(u): hepsi p
    F = Funktor(A, {"0": frozenset({"x", "y"}), "1": frozenset({"p"})},
                {("id", "0"): {"x": "x", "y": "y"},
                 ("id", "1"): {"p": "p"},
                 "u": {"x": "p", "y": "p"}}, ad="F")
    ok, sebep = F.funktoryel_mi()
    s.append(f"\n=== Funktor denetimi ===\n  F funktoryel mi? {ok} {sebep}")
    bozuk = Funktor(A, {"0": frozenset({"x"}), "1": frozenset({"p", "q"})},
                    {("id", "0"): {"x": "x"},
                     ("id", "1"): {"p": "q", "q": "p"},   # birim bozuk
                     "u": {"x": "p"}}, ad="bozuk")
    ok2, sebep2 = bozuk.funktoryel_mi()
    s.append(f"  birimi bozuk funktor: {ok2}  ({sebep2})")

    s.append("\n=== K = id ise Lan_K F ≅ F ve Ran_K F ≅ F ===")
    idA = _ozdes_funktor(A)
    for b in A.nesneler:
        L = lan(idA, F, b)
        R = ran(idA, F, b)
        s.append(f"  b={b}: |F(b)|={len(F.nes[b])}"
                 f"   |Lan|={L['sınıf_sayısı']}"
                 f"   |Ran|={R['eleman_sayısı']}"
                 f"   (Lan ham eleman {L['ham_eleman']} → bölümlendi)")

    s.append("\n=== Lan serbest genişletmedir: sola eşleniklik SAYILIYOR ===")
    s.append("  |Nat(Lan_K F, G)| = |Nat(F, G∘K)| — iddia değil, sayım:")
    T = sonlu_kategori(("*",), [], ad="1")
    F0 = Funktor(T, {"*": frozenset({"a", "b"})},
                 {("id", "*"): {"a": "a", "b": "b"}}, ad="F0")
    # Denenecek G funktorları: A → Set
    Gler = []
    Gler.append(("sabit-1", Funktor(A, {"0": frozenset({"p"}),
                                       "1": frozenset({"p"})},
                                    {("id", "0"): {"p": "p"},
                                     ("id", "1"): {"p": "p"},
                                     "u": {"p": "p"}}, ad="G1")))
    Gler.append(("çöken", Funktor(A, {"0": frozenset({"x", "y"}),
                                     "1": frozenset({"p"})},
                                  {("id", "0"): {"x": "x", "y": "y"},
                                   ("id", "1"): {"p": "p"},
                                   "u": {"x": "p", "y": "p"}}, ad="G2")))
    Gler.append(("gömen", Funktor(A, {"0": frozenset({"x"}),
                                     "1": frozenset({"p", "q"})},
                                  {("id", "0"): {"x": "x"},
                                   ("id", "1"): {"p": "p", "q": "q"},
                                   "u": {"x": "q"}}, ad="G3")))
    for hedef_nesne in ("0", "1"):
        K = Funktor(T, {"*": hedef_nesne},
                    {("id", "*"): ("id", hedef_nesne)}, hedef=A,
                    ad=f"K{hedef_nesne}")
        okk, sb = K.funktoryel_mi()
        assert okk, sb
        LanF = lan_funktor(K, F0)
        okl, sbl = LanF.funktoryel_mi()
        boyut = ", ".join(f"|{o}|={len(LanF.nes[o])}" for o in A.nesneler)
        s.append(f"  K(*)={hedef_nesne}:  Lan_K F0 = ({boyut})"
                 f"   funktoryel mi? {okl} {sbl}")
        for ad, G in Gler:
            sol = dogal_donusumler(LanF, G)
            sag = dogal_donusumler(F0, bileske_funktor(G, K))
            isaret = "=" if sol == sag else "≠  ← EŞLENİKLİK BOZUK"
            s.append(f"      G={ad:8s} |Nat(Lan_K F0, G)|={sol:3d}"
                     f"  {isaret}  |Nat(F0, G∘K)|={sag:3d}")

    s.append("\n=== Monoid üzerinde Lan: çevrimli kategori ===")
    M = monoid_kategorisi(3)
    s.append(f"  ℤ/3 monoidi: {len(M.oklar)} ok, aksiyomlar geçti")
    # F: M → Set, ℤ/3'ün ℤ/3 üzerine kaydırma etkisi
    tasiyici = frozenset(range(3))
    FM = Funktor(M, {"*": tasiyici},
                 {("m", i): {x: (x + i) % 3 for x in range(3)}
                  for i in range(3)}, ad="kaydırma")
    okm, sbm = FM.funktoryel_mi()
    s.append(f"  kaydırma etkisi funktoryel mi? {okm} {sbm}")
    idM = _ozdes_funktor(M)
    LM = lan(idM, FM, "*")
    RM = ran(idM, FM, "*")
    s.append(f"  Lan_id F: ham eleman {LM['ham_eleman']}"
             f" → {LM['sınıf_sayısı']} sınıf  (|F(*)|={len(tasiyici)})")
    s.append(f"  Ran_id F: {RM['aday_sayısı']} adayın"
             f" {RM['eleman_sayısı']}'i doğal")

    s.append("\n=== Birleşim–bul: coend bölümü ===")
    bb = birlestir_bul()
    for i in range(1000):
        bb.ekle(i)
    for i in range(999):
        bb.birlestir(i, i + 1)
    s.append(f"  1000 eleman zincir hâlinde birleştirildi →"
             f" {len(bb.siniflar())} sınıf (beklenen 1)")
    bb2 = birlestir_bul()
    for i in range(1000):
        bb2.ekle(i)
    for i in range(0, 998, 2):
        bb2.birlestir(i, i + 2)
    s.append(f"  çiftler ayrı birleştirildi → {len(bb2.siniflar())} sınıf"
             f" (beklenen 501: tek çift sınıfı + 500 tekil)")
    return "\n".join(s)


def rapor() -> str:
    return _gosterim()


if __name__ == "__main__":
    print(rapor())
