"""Ayrışma — yönlü çizgelerde d-ayrışması ve arka kapı ölçütü.

Bir yönlü çevrimsiz çizgede (DAG) ``X ⫫ Y | Z`` sorusunun **grafik**
cevabı d-ayrışmasıdır.  Tanım: ``X`` ile ``Y`` arasındaki her yol
``Z`` tarafından *kapatılmışsa* ikisi d-ayrıktır.  Bir yol üzerindeki
``a → b → c``, ``a ← b → c`` (zincir ve çatal) düğümü ``b ∈ Z`` ise
kapatır; ``a → b ← c`` (çarpışma, collider) ise tam tersi — ``b`` **ve
bütün nesli** ``Z`` dışındaysa kapatır.

Çarpışma kaidesi meselenin can alıcı yeridir ve sezgiye aykırıdır:
şarta bağlamak bağımsızlığı **doğurmaz**, aksine bozar.  Bu modül
d-ayrışmasını Bayes toplarıyla (``bayes-ball``) ``O(V+E)`` zamanda
hesaplar ve neticeyi **bağımsız bir yoldan**, yani bütün yolları tek
tek dolaşarak sağlar.

Ayrıca:

* **Arka kapı ölçütü** — ``Z``, ``(X,Y)`` çifti için arka kapıyı
  kapatıyorsa ``P(y | do(x)) = Σ_z P(y | x,z) P(z)`` ile tahmin edilir.
  Şartlar: (i) ``Z`` içinde ``X``in hiçbir nesli yok, (ii) ``Z``,
  ``X``e **giren** oktan başlayan bütün yolları kapatıyor.
* **B-ayrışması** — birden çok ortamda (bloklarda) *aynı anda* geçerli
  olan ayrışmalar; ortamlar arasında değişen kenarlar bir müdahale
  düğümüyle temsil edilir ve ayrışma o genişletilmiş çizgede aranır.
"""

from __future__ import annotations

import itertools
from collections import deque
from dataclasses import dataclass, field
from typing import (Dict, FrozenSet, Iterable, List, Optional, Sequence, Set,
                    Tuple)

__all__ = [
    "Cizge", "d_ayrik_mi", "d_ayrik_yollarla", "butun_ayrismalar",
    "arka_kapi_mi", "arka_kapi_kumeleri", "on_kapi_mi",
    "b_ayrik_mi", "ortak_ayrismalar",
]


# ══════════════════════════════════════════════════════════════════════
#  Çizge
# ══════════════════════════════════════════════════════════════════════

@dataclass
class Cizge:
    """Yönlü çevrimsiz çizge.

    ``kenarlar``: ``(ebeveyn, çocuk)`` çiftleri.  Kurulurken çevrimsizlik
    **denetlenir**; çevrimli bir çizgede d-ayrışması tanımlı değildir ve
    sessizce yanlış cevap vermektense hata verilir.
    """
    dugumler: Tuple[str, ...]
    kenarlar: Tuple[Tuple[str, str], ...]
    ebeveyn: Dict[str, Set[str]] = field(default_factory=dict, repr=False)
    cocuk: Dict[str, Set[str]] = field(default_factory=dict, repr=False)

    def __post_init__(self) -> None:
        self.dugumler = tuple(dict.fromkeys(self.dugumler))
        self.ebeveyn = {d: set() for d in self.dugumler}
        self.cocuk = {d: set() for d in self.dugumler}
        for a, b in self.kenarlar:
            if a not in self.ebeveyn or b not in self.ebeveyn:
                raise ValueError(f"bilinmeyen düğüm: {a}→{b}")
            self.cocuk[a].add(b)
            self.ebeveyn[b].add(a)
        if self._cevrim_var_mi():
            raise ValueError("çizge çevrimli — d-ayrışması tanımsız")

    def _cevrim_var_mi(self) -> bool:
        """Kahn topolojik sıralaması; hepsi tükenmezse çevrim vardır."""
        derece = {d: len(self.ebeveyn[d]) for d in self.dugumler}
        kuyruk = deque(d for d, k in derece.items() if k == 0)
        sayi = 0
        while kuyruk:
            d = kuyruk.popleft()
            sayi += 1
            for c in self.cocuk[d]:
                derece[c] -= 1
                if derece[c] == 0:
                    kuyruk.append(c)
        return sayi != len(self.dugumler)

    def nesil(self, kume: Iterable[str]) -> Set[str]:
        """``kume`` ve bütün nesli (kendisi dâhil)."""
        yigin = list(kume)
        gorulen: Set[str] = set(yigin)
        while yigin:
            d = yigin.pop()
            for c in self.cocuk[d]:
                if c not in gorulen:
                    gorulen.add(c)
                    yigin.append(c)
        return gorulen

    def ata(self, kume: Iterable[str]) -> Set[str]:
        """``kume`` ve bütün ataları (kendisi dâhil)."""
        yigin = list(kume)
        gorulen: Set[str] = set(yigin)
        while yigin:
            d = yigin.pop()
            for e in self.ebeveyn[d]:
                if e not in gorulen:
                    gorulen.add(e)
                    yigin.append(e)
        return gorulen

    def komsular(self, d: str) -> Set[str]:
        return self.ebeveyn[d] | self.cocuk[d]


# ══════════════════════════════════════════════════════════════════════
#  d-ayrışması — Bayes topları, O(V+E)
# ══════════════════════════════════════════════════════════════════════

def _erisilenler(g: Cizge, X: Set[str], Z: Set[str]) -> Set[str]:
    """``X``ten ``Z`` verildiğinde d-bağlantılı olan bütün düğümler.

    Yürüyüş, düğüm değil **(düğüm, geliş yönü)** çiftleri üzerinde
    yapılır; çünkü bir düğümden devam edilip edilemeyeceği oraya
    yukarıdan mı aşağıdan mı gelindiğine bağlıdır.  Bu ayrım
    yapılmazsa çarpışma kaidesi doğru işlemez.

    ``yon = 0``: düğüme bir çocuğundan gelindi (yani ok yukarı bakıyor).
    ``yon = 1``: düğüme bir ebeveyninden gelindi (ok aşağı bakıyor).
    """
    # Şarta bağlananların atalarından herhangi biri, açılmış bir
    # çarpışma düğümü olabilir.
    zin_atalari = g.ata(Z)

    ziyaret: Set[Tuple[str, int]] = set()
    # Başlangıç düğümleri HER İKİ yöne de gidebilmeli: X'in kendi
    # ebeveynlerine çıkan yol (X ← Z → Y çatalı) da bir yoldur.  Bunun
    # için ``yon=0`` ("çocuğundan gelindi") ile tohumlanır; o dal hem
    # ebeveynlere hem çocuklara açılır.  ``yon=1`` ile tohumlamak
    # ebeveynlere çıkışı kapatır ve bütün karıştırıcıları görünmez kılar.
    kuyruk = deque((x, 0) for x in X)
    for x in X:
        ziyaret.add((x, 0))
    erisilen: Set[str] = set(X)

    while kuyruk:
        d, yon = kuyruk.popleft()
        erisilen.add(d)
        if yon == 1:
            # Düğüme ebeveyninden gelindi: d, bir zincirin ortası.
            if d not in Z:
                for c in g.cocuk[d]:          # zincir devam eder
                    if (c, 1) not in ziyaret:
                        ziyaret.add((c, 1)); kuyruk.append((c, 1))
            # d ∈ Z ise ok kapanır; ayrıca "çarpışma" olarak da bakılır:
            if d in zin_atalari:
                for e in g.ebeveyn[d]:        # çarpışma açık
                    if (e, 0) not in ziyaret:
                        ziyaret.add((e, 0)); kuyruk.append((e, 0))
        else:
            # Düğüme çocuğundan gelindi: d, çatalın tepesi.
            if d not in Z:
                for e in g.ebeveyn[d]:
                    if (e, 0) not in ziyaret:
                        ziyaret.add((e, 0)); kuyruk.append((e, 0))
                for c in g.cocuk[d]:
                    if (c, 1) not in ziyaret:
                        ziyaret.add((c, 1)); kuyruk.append((c, 1))
    return erisilen


def d_ayrik_mi(g: Cizge, X: Iterable[str], Y: Iterable[str],
               Z: Iterable[str] = ()) -> bool:
    """``X ⫫_d Y | Z``?  Bayes toplarıyla, ``O(V+E)``."""
    Xs, Ys, Zs = set(X), set(Y), set(Z)
    ortak = (Xs | Ys) & Zs
    if ortak:
        raise ValueError(f"X, Y ve Z ayrık olmalı; ortak: {sorted(ortak)}")
    if Xs & Ys:
        raise ValueError("X ile Y ayrık olmalı")
    return not (_erisilenler(g, Xs, Zs) & Ys)


# ══════════════════════════════════════════════════════════════════════
#  Bağımsız sağlama: bütün yolları tek tek dolaş
# ══════════════════════════════════════════════════════════════════════

def _yollar(g: Cizge, x: str, y: str) -> List[List[str]]:
    """``x`` ile ``y`` arasındaki bütün **yönsüz** basit yollar."""
    sonuc: List[List[str]] = []
    yol = [x]
    ustunde = {x}

    def yuru(d: str) -> None:
        if d == y:
            sonuc.append(list(yol))
            return
        for k in g.komsular(d):
            if k in ustunde:
                continue
            ustunde.add(k); yol.append(k)
            yuru(k)
            yol.pop(); ustunde.discard(k)

    yuru(x)
    return sonuc


def _yol_acik_mi(g: Cizge, yol: Sequence[str], Z: Set[str]) -> bool:
    """Yolun her ara düğümü açık mı?

    ``a → b ← c`` çarpışmasında ``b`` veya nesli ``Z``de olmalı;
    diğer iki hâlde ``b`` ``Z``de olmamalı.
    """
    zin_atalari = g.ata(Z)
    for i in range(1, len(yol) - 1):
        onc, orta, son = yol[i - 1], yol[i], yol[i + 1]
        carpisma = (onc in g.ebeveyn[orta]) and (son in g.ebeveyn[orta])
        if carpisma:
            if orta not in zin_atalari:
                return False
        else:
            if orta in Z:
                return False
    return True


def d_ayrik_yollarla(g: Cizge, X: Iterable[str], Y: Iterable[str],
                     Z: Iterable[str] = ()) -> bool:
    """Aynı soruya **bağımsız** cevap: bütün yolları dolaşarak.

    Üstel zamanlıdır; sadece Bayes toplarının sağlaması için vardır.
    İkisi her çizgede uyuşmak zorundadır (``test_ayrisma`` bunu rastgele
    çizgelerde sınar).
    """
    Xs, Ys, Zs = set(X), set(Y), set(Z)
    for x in Xs:
        for y in Ys:
            for yol in _yollar(g, x, y):
                if _yol_acik_mi(g, yol, Zs):
                    return False
    return True


def butun_ayrismalar(g: Cizge, azami_z: int = 2
                     ) -> List[Tuple[str, str, FrozenSet[str]]]:
    """Çizgenin ima ettiği bütün ``X ⫫ Y | Z`` (``|Z| ≤ azami_z``)."""
    sonuc = []
    for x, y in itertools.combinations(g.dugumler, 2):
        kalan = [d for d in g.dugumler if d not in (x, y)]
        for k in range(azami_z + 1):
            for Z in itertools.combinations(kalan, k):
                if d_ayrik_mi(g, [x], [y], Z):
                    sonuc.append((x, y, frozenset(Z)))
    return sonuc


# ══════════════════════════════════════════════════════════════════════
#  Arka kapı ve ön kapı
# ══════════════════════════════════════════════════════════════════════

def _oku_sokulmus(g: Cizge, X: Set[str]) -> Cizge:
    """``X``e **giren** okları silinmiş çizge (``G_X̲``)."""
    yeni = tuple((a, b) for a, b in g.kenarlar if b not in X)
    return Cizge(g.dugumler, yeni)


def _oku_cikarilmis(g: Cizge, X: Set[str]) -> Cizge:
    """``X``ten **çıkan** okları silinmiş çizge (``G_X̄``)."""
    yeni = tuple((a, b) for a, b in g.kenarlar if a not in X)
    return Cizge(g.dugumler, yeni)


def arka_kapi_mi(g: Cizge, X: str, Y: str, Z: Iterable[str]) -> bool:
    """``Z`` ``(X,Y)`` için arka kapı ölçütünü sağlıyor mu?

    İki şart:

    1. ``Z``de ``X``in nesli olmamalı — aksi hâlde neticeye giden yolun
       kendisine şarta bağlanmış olur (yol üstü değişken tuzağı).
    2. ``X``ten **çıkan** oklar silindiğinde ``Z``, ``X`` ile ``Y``yi
       d-ayırmalı; yani geriye kalan bütün arka yollar kapanmalı.

    Sağlanıyorsa ``P(y|do(x)) = Σ_z P(y|x,z)P(z)``.
    """
    Zs = set(Z)
    if Zs & g.nesil({X}):
        return False
    if X in Zs or Y in Zs:
        return False
    return d_ayrik_mi(_oku_cikarilmis(g, {X}), [X], [Y], Zs)


def arka_kapi_kumeleri(g: Cizge, X: str, Y: str, azami: int = 3
                       ) -> List[FrozenSet[str]]:
    """Arka kapıyı kapatan bütün ``Z`` kümeleri (``|Z| ≤ azami``).

    Boş küme de aday olarak denenir: bazı çizgelerde karıştırıcı yoktur
    ve hiçbir şeye şarta bağlanmamak doğru cevaptır.
    """
    adaylar = [d for d in g.dugumler if d not in (X, Y)]
    sonuc = []
    for k in range(azami + 1):
        for Z in itertools.combinations(adaylar, k):
            if arka_kapi_mi(g, X, Y, Z):
                sonuc.append(frozenset(Z))
    return sonuc


def on_kapi_mi(g: Cizge, X: str, Y: str, M: Iterable[str]) -> bool:
    """``M`` ``(X,Y)`` için ön kapı ölçütünü sağlıyor mu?

    Üç şart:

    1. ``M``, ``X``ten ``Y``ye giden bütün yönlü yolları kesiyor.
    2. ``X``ten ``M``ye arka kapı yok.
    3. ``M``den ``Y``ye giden bütün arka kapılar ``X`` tarafından
       kapatılıyor.

    Ön kapı, arka kapının **kapatılamadığı** (gözlenmemiş karıştırıcı
    olan) hâllerde işe yarar; bu yüzden ikisi birbirinin yedeği değil,
    ayrı âletlerdir.
    """
    Ms = set(M)
    if X in Ms or Y in Ms:
        return False
    # 1: X'ten çıkan bütün yönlü yollar M'den geçmeli.
    if not _yonlu_yollar_kesiliyor_mu(g, X, Y, Ms):
        return False
    # 2: X → M arka kapısı yok (boş kümeyle kapanıyor).
    if not all(d_ayrik_mi(_oku_cikarilmis(g, {X}), [X], [m], ()) for m in Ms):
        return False
    # 3: M → Y arka kapıları X ile kapanıyor.
    for m in Ms:
        if not d_ayrik_mi(_oku_cikarilmis(g, {m}), [m], [Y], {X}):
            return False
    return True


def _yonlu_yollar_kesiliyor_mu(g: Cizge, x: str, y: str, M: Set[str]) -> bool:
    """``x``ten ``y``ye giden her **yönlü** yol ``M``den geçiyor mu?"""
    yigin = [x]
    gorulen = {x}
    while yigin:
        d = yigin.pop()
        for c in g.cocuk[d]:
            if c in M:
                continue                 # bu yol kesildi
            if c == y:
                return False             # M'ye uğramadan Y'ye varıldı
            if c not in gorulen:
                gorulen.add(c); yigin.append(c)
    return True


# ══════════════════════════════════════════════════════════════════════
#  B-ayrışması: ortamlar arası ortak ayrışma
# ══════════════════════════════════════════════════════════════════════

def b_ayrik_mi(cizgeler: Sequence[Cizge], X: Iterable[str],
               Y: Iterable[str], Z: Iterable[str] = ()) -> bool:
    """``X ⫫ Y | Z`` **bütün** ortamlarda geçerli mi?

    Bir ortamda bile açılıyorsa hüküm verilmez.  Bu, değişmezliğin
    grafik karşılığıdır: ortamlar arası dayanıklı olmayan bir ayrışma,
    ortamın kendi tesadüfüdür.
    """
    return all(d_ayrik_mi(g, X, Y, Z) for g in cizgeler)


def ortak_ayrismalar(cizgeler: Sequence[Cizge], azami_z: int = 2
                     ) -> List[Tuple[str, str, FrozenSet[str]]]:
    """Bütün ortamlarda ortak olan ayrışmaların **kesişimi**."""
    if not cizgeler:
        return []
    kumeler = [set(butun_ayrismalar(g, azami_z)) for g in cizgeler]
    ortak = kumeler[0]
    for k in kumeler[1:]:
        ortak &= k
    return sorted(ortak, key=lambda t: (t[0], t[1], sorted(t[2])))


# ══════════════════════════════════════════════════════════════════════
#  Gösterim
# ══════════════════════════════════════════════════════════════════════

def _gosterim() -> str:
    s: List[str] = []

    s.append("=== Üç temel yapı ===")
    zincir = Cizge(("A", "B", "C"), (("A", "B"), ("B", "C")))
    catal = Cizge(("A", "B", "C"), (("B", "A"), ("B", "C")))
    carpis = Cizge(("A", "B", "C"), (("A", "B"), ("C", "B")))
    for ad, g in (("zincir A→B→C", zincir), ("çatal  A←B→C", catal),
                  ("çarpışma A→B←C", carpis)):
        bos = d_ayrik_mi(g, ["A"], ["C"])
        sart = d_ayrik_mi(g, ["A"], ["C"], ["B"])
        s.append(f"  {ad:16s} A⫫C = {str(bos):5s}   A⫫C|B = {sart}")
    s.append("  dikkat: çarpışmada şarta bağlamak bağımsızlığı BOZUYOR —")
    s.append("  diğer ikisinde kuruyor. İşaret tersine dönüyor.")

    s.append("\n=== Çarpışmanın nesli de açar ===")
    g2 = Cizge(("A", "B", "C", "D"), (("A", "B"), ("C", "B"), ("B", "D")))
    s.append(f"  A⫫C     = {d_ayrik_mi(g2, ['A'], ['C'])}")
    s.append(f"  A⫫C | D = {d_ayrik_mi(g2, ['A'], ['C'], ['D'])}"
             "   (D, B'nin çocuğu — yine de açıyor)")

    s.append("\n=== İki usul birbirini sağlıyor mu? ===")
    import random
    rast = random.Random(20260824)
    uyusmazlik = 0
    deneme = 0
    for _ in range(300):
        n = rast.randint(3, 6)
        adlar = tuple(f"v{i}" for i in range(n))
        kenar = tuple((adlar[i], adlar[j])
                      for i in range(n) for j in range(i + 1, n)
                      if rast.random() < 0.45)
        g = Cizge(adlar, kenar)
        x, y = rast.sample(adlar, 2)
        kalan = [d for d in adlar if d not in (x, y)]
        k = rast.randint(0, len(kalan))
        Z = rast.sample(kalan, k)
        deneme += 1
        if d_ayrik_mi(g, [x], [y], Z) != d_ayrik_yollarla(g, [x], [y], Z):
            uyusmazlik += 1
    s.append(f"  {deneme} rastgele sorgu — Bayes topları ile yol sayımı"
             f" arasında uyuşmazlık: {uyusmazlik}")

    s.append("\n=== Arka kapı ===")
    # X ← Z → Y, X → Y : Z karıştırıcı
    g3 = Cizge(("X", "Y", "Z"), (("Z", "X"), ("Z", "Y"), ("X", "Y")))
    s.append(f"  karıştırıcılı çizgede Z uygun mu? {arka_kapi_mi(g3, 'X', 'Y', ['Z'])}")
    s.append(f"  hiçbir şeye bağlanmamak?          {arka_kapi_mi(g3, 'X', 'Y', [])}")
    s.append(f"  bütün uygun kümeler: "
             + ", ".join("{" + ",".join(sorted(z)) + "}" if z else "∅"
                         for z in arka_kapi_kumeleri(g3, "X", "Y")))
    # X → M → Y, Z ardıl (X'in nesli): şarta bağlanmamalı
    g4 = Cizge(("X", "M", "Y"), (("X", "M"), ("M", "Y")))
    s.append(f"  ardıla (M) bağlanmak uygun mu? {arka_kapi_mi(g4, 'X', 'Y', ['M'])}"
             "   (hayır — X'in nesli)")

    s.append("\n=== Ön kapı (gözlenmemiş karıştırıcı varken) ===")
    # U gözlenmemiş: U→X, U→Y, X→M→Y
    g5 = Cizge(("U", "X", "M", "Y"),
               (("U", "X"), ("U", "Y"), ("X", "M"), ("M", "Y")))
    s.append(f"  M ön kapıyı sağlıyor mu? {on_kapi_mi(g5, 'X', 'Y', ['M'])}")
    gozlenen = [z for z in arka_kapi_kumeleri(g5, "X", "Y") if "U" not in z]
    s.append(f"  U'suz arka kapı kümesi var mı? "
             f"{'evet: ' + str(gozlenen) if gozlenen else 'yok'}")
    s.append("  → arka kapı kapanmıyor ama ön kapı açık; ikisi ayrı âlet.")

    s.append("\n=== B-ayrışması: ortamlar arası ortak ===")
    # Ortamlar Z→Y kenarında ayrışıyor; Z→X→Y omurgası ikisinde de sabit.
    o1 = Cizge(("X", "Y", "Z"), (("Z", "X"), ("X", "Y"), ("Z", "Y")))
    o2 = Cizge(("X", "Y", "Z"), (("Z", "X"), ("X", "Y")))
    s.append("  omurga Z→X→Y ikisinde de var; ortam-1'de fazladan Z→Y var.")
    s.append(f"  ortam-1'de Z⫫Y|X = {d_ayrik_mi(o1, ['Z'], ['Y'], ['X'])}"
             "   (fazla kenar yüzünden kapanmıyor)")
    s.append(f"  ortam-2'de Z⫫Y|X = {d_ayrik_mi(o2, ['Z'], ['Y'], ['X'])}")
    s.append(f"  B-ayrık mı (ikisinde birden)? "
             f"{b_ayrik_mi([o1, o2], ['Z'], ['Y'], ['X'])}"
             "   → tek ortamda tutan ayrışma hüküm doğurmaz")
    o3 = Cizge(("X", "Y", "Z", "W"),
               (("Z", "X"), ("X", "Y"), ("W", "Y")))
    o4 = Cizge(("X", "Y", "Z", "W"),
               (("Z", "X"), ("X", "Y"), ("W", "Y"), ("W", "X")))
    s.append(f"  Z⫫W (iki ayrı ortamda): {d_ayrik_mi(o3, ['Z'], ['W'])},"
             f" {d_ayrik_mi(o4, ['Z'], ['W'])}"
             f" → B-ayrık={b_ayrik_mi([o3, o4], ['Z'], ['W'])}")
    ortak = ortak_ayrismalar([o3, o4])
    s.append(f"  son iki ortamın ortak ayrışmaları: "
             + (", ".join(f"{x}⫫{y}|{{{','.join(sorted(z)) or '∅'}}}"
                          for x, y, z in ortak) or "yok"))
    return "\n".join(s)


def rapor() -> str:
    return _gosterim()


if __name__ == "__main__":
    print(rapor())
