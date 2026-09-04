"""FITRAT ÇİPİ -- nedensellik, illiyet ve oyun dengesi.

KÜME 7'nin üçüncü karargâhı (kütük H226). Altı dosya --
``fitrat/ayrisma.py``, ``karsi_olgusal.py``, ``serbest_enerji.py``,
``denge.py``, ``tevafuk.py``, ``havuz.py`` -- burada birleşti. Terkip
üç adımda yapıldı: (a) her dosya kendi içinde, (b) birleştirme,
(c) birleşik gövdede bir daha. Asılları
``yedek/kume7_asillari/fitrat/`` altında şahittir.

**Kök problem.** *"Bu, şunun sebebi mi?"* suâlinin dört ayrı cevap
makinesi vardı -- graf teorik ayrışma, karşıolgusal hesap,
varyasyonel serbest enerji ve oyun dengesi -- ve birbirleriyle
konuşmuyorlardı.

**Çipin beş odası.**

1. **Graf teorik illiyet** -- ``Cizge`` (çevrimsizlik ``__post_init__``
   ile mühürlü), Bayes-Ball ``O(V+E)`` d-ayrışması, yol sayımıyla
   bağımsız ikinci şahit, arka kapı / ön kapı ölçütleri, B-ayrışması.
2. **Karşıolgusal hesap** -- üç pas (abduction → action → prediction),
   budayarak müdahale ``do(X=x)``, NOTEARS çevrimsizlik değişmezi
   ``h(A) = tr(e^{A∘A}) − d`` ve gradyanı, örtük değişkenlerin
   doğurduğu sahte bağıntı, locus üstünde Newton düzeltmeli yürüme.
3. **Varyasyonel serbest enerji** -- ``F = −ELBO ≥ −ln p(x)``, tam
   ayrışım ``F = kesinsizlik + karmaşıklık(KL)``, koordinat inişi,
   Gauss kapalı biçimi.
4. **Çok failli denge** -- damped Newton kök bulucu, spektral yarıçap
   ile kararlılık, en iyi karşılık iterasyonu, örtük fonksiyon
   teoremiyle hassasiyet türevi, Cournot kapalı çözümüyle mihenk.
5. **Tevâfuk ve şahitlik** -- şartlı bağımsızlık ağırlıklı konsensüs,
   fazla sayma oranı, muteber şahit sayısı; şüphe havuzu ve
   karantina hükmü.
"""
from __future__ import annotations

import itertools
import math
import numpy as np
from collections import deque
from dataclasses import dataclass
from dataclasses import dataclass, field
from enum import Enum
from typing import (Dict, FrozenSet, Iterable, List, Optional, Sequence, Set,
                    Tuple)
from typing import Callable, Dict, List, Optional, Sequence, Tuple
from typing import Dict, List, Optional, Sequence, Tuple


# ====================================================================
#  fitrat/ayrisma.py
# ====================================================================

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




KIP_DYOL, KIP_ARKA = "d_yol", "arka_kapı"
KIP_ON, KIP_B = "ön_kapı", "b"


def tesir_kapali_mi(g=None, X=None, Y=None, Z: Iterable[str] = (),
                    M: Iterable[str] = (), cizgeler=None,
                    ne: str = "d") -> bool:
    """TESİR BURADAN GEÇEBİLİR Mİ -- **tek terkip** (kütük H226).

    Küme: ``d_ayrik_mi``, ``d_ayrik_yollarla``, ``arka_kapi_mi``,
    ``on_kapi_mi``, ``b_ayrik_mi``. Beş isim, tek suâlin beş ölçütü
    idi: *bu küme, tesirin geçtiği yolları kapatıyor mu?* Ayrı ayrı
    dururken ölçütlerin **birbirini nasıl kullandığı** görünmüyordu;
    hâlbuki arka kapı da ön kapı da d-ayrışmanın üstüne kuruludur.

    ==============  ==================================================
    ``ne``          hangi ölçüt
    ==============  ==================================================
    ``d``           ``X ⫫_d Y | Z`` -- Bayes toplarıyla, ``O(V+E)``
    ``d_yol``       aynı suâle **bağımsız** cevap: bütün yolları
                    dolaşarak. Üstel zamanlıdır ve yalnız Bayes
                    toplarının **sağlaması** için vardır; ikisi her
                    çizgede uyuşmak zorundadır.
    ``arka_kapı``   verilen küme ``(X,Y)`` için arka kapı ölçütünü
                    sağlıyor mu (orada ona **şart kümesi** ``Z`` denir)
    ``ön_kapı``     verilen küme ``(X,Y)`` için ön kapı ölçütünü
                    sağlıyor mu (orada ona **aracı kümesi** ``M`` denir)
    ``b``           ``X ⫫ Y | Z`` **bütün** ortamlarda -- ``cizgeler``
    ==============  ==================================================

    Bir hesap ile onun bağımsız şahidini aynı kapıya koymak kasıtlıdır:
    ``d`` ile ``d_yol`` ayrı isimler taşırken biri ötekinin sağlaması
    olduğu ancak şerhten anlaşılıyordu; şimdi tek ``ne``nin iki değeri.
    """
    if ne == "d":
        Xs, Ys, Zs = set(X), set(Y), set(Z)
        ortak = (Xs | Ys) & Zs
        if ortak:
            raise ValueError(f"X, Y ve Z ayrık olmalı; ortak: {sorted(ortak)}")
        if Xs & Ys:
            raise ValueError("X ile Y ayrık olmalı")
        return not (_erisilenler(g, Xs, Zs) & Ys)
    if ne == "d_yol":
        Xs, Ys, Zs = set(X), set(Y), set(Z)
        for x in Xs:
            for y in Ys:
                for yol in _yollar(g, x, y):
                    if _yol_acik_mi(g, yol, Zs):
                        return False
        return True
    if ne == "arka_kapı":
        Zs = set(Z)
        if Zs & g.nesil({X}):
            return False
        if X in Zs or Y in Zs:
            return False
        return tesir_kapali_mi(_oku_cikarilmis(g, {X}), [X], [Y], Zs)
    if ne == "ön_kapı":
        # Dördüncü argüman **verilen kümedir**: arka kapıda ona şart
        # kümesi (``Z``), ön kapıda aracı kümesi (``M``) denir. Terkipte
        # ikisi aynı yerdedir; ``M`` boşsa ``Z``den okunur.
        M = M or Z
        Ms = set(M)
        if X in Ms or Y in Ms:
            return False
        # 1: X'ten çıkan bütün yönlü yollar M'den geçmeli.
        if not _yonlu_yollar_kesiliyor_mu(g, X, Y, Ms):
            return False
        # 2: X → M arka kapısı yok (boş kümeyle kapanıyor).
        if not all(tesir_kapali_mi(_oku_cikarilmis(g, {X}), [X], [m])
                   for m in Ms):
            return False
        # 3: M → Y arka kapıları X ile kapanıyor.
        for m in Ms:
            if not tesir_kapali_mi(_oku_cikarilmis(g, {m}), [m], [Y], {X}):
                return False
        return True
    if ne == "b":
        return all(tesir_kapali_mi(g, X, Y, Z) for g in cizgeler)
    raise ValueError("ayrışma ölçütü bilinmiyor: %r" % (ne,))


def butun_ayrismalar(g: Cizge, azami_z: int = 2
                     ) -> List[Tuple[str, str, FrozenSet[str]]]:
    """Çizgenin ima ettiği bütün ``X ⫫ Y | Z`` (``|Z| ≤ azami_z``)."""
    sonuc = []
    for x, y in itertools.combinations(g.dugumler, 2):
        kalan = [d for d in g.dugumler if d not in (x, y)]
        for k in range(azami_z + 1):
            for Z in itertools.combinations(kalan, k):
                if tesir_kapali_mi(g, [x], [y], Z):
                    sonuc.append((x, y, frozenset(Z)))
    return sonuc


def _oku_sokulmus(g: Cizge, X: Set[str]) -> Cizge:
    """``X``e **giren** okları silinmiş çizge (``G_X̲``)."""
    yeni = tuple((a, b) for a, b in g.kenarlar if b not in X)
    return Cizge(g.dugumler, yeni)


def _oku_cikarilmis(g: Cizge, X: Set[str]) -> Cizge:
    """``X``ten **çıkan** okları silinmiş çizge (``G_X̄``)."""
    yeni = tuple((a, b) for a, b in g.kenarlar if a not in X)
    return Cizge(g.dugumler, yeni)




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
            if tesir_kapali_mi(g, X, Y, Z, ne=KIP_ARKA):
                sonuc.append(frozenset(Z))
    return sonuc




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


def _rapor_fitrat_ayrisma() -> str:
    s: List[str] = []

    s.append("=== Üç temel yapı ===")
    zincir = Cizge(("A", "B", "C"), (("A", "B"), ("B", "C")))
    catal = Cizge(("A", "B", "C"), (("B", "A"), ("B", "C")))
    carpis = Cizge(("A", "B", "C"), (("A", "B"), ("C", "B")))
    for ad, g in (("zincir A→B→C", zincir), ("çatal  A←B→C", catal),
                  ("çarpışma A→B←C", carpis)):
        bos = tesir_kapali_mi(g, ["A"], ["C"])
        sart = tesir_kapali_mi(g, ["A"], ["C"], ["B"])
        s.append(f"  {ad:16s} A⫫C = {str(bos):5s}   A⫫C|B = {sart}")
    s.append("  dikkat: çarpışmada şarta bağlamak bağımsızlığı BOZUYOR —")
    s.append("  diğer ikisinde kuruyor. İşaret tersine dönüyor.")

    s.append("\n=== Çarpışmanın nesli de açar ===")
    g2 = Cizge(("A", "B", "C", "D"), (("A", "B"), ("C", "B"), ("B", "D")))
    s.append(f"  A⫫C     = {tesir_kapali_mi(g2, ['A'], ['C'])}")
    s.append(f"  A⫫C | D = {tesir_kapali_mi(g2, ['A'], ['C'], ['D'])}"
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
        if tesir_kapali_mi(g, [x], [y], Z) != tesir_kapali_mi(g, [x], [y], Z, ne=KIP_DYOL):
            uyusmazlik += 1
    s.append(f"  {deneme} rastgele sorgu — Bayes topları ile yol sayımı"
             f" arasında uyuşmazlık: {uyusmazlik}")

    s.append("\n=== Arka kapı ===")
    # X ← Z → Y, X → Y : Z karıştırıcı
    g3 = Cizge(("X", "Y", "Z"), (("Z", "X"), ("Z", "Y"), ("X", "Y")))
    s.append(f"  karıştırıcılı çizgede Z uygun mu? {tesir_kapali_mi(g3, 'X', 'Y', ['Z'], ne=KIP_ARKA)}")
    s.append(f"  hiçbir şeye bağlanmamak?          {tesir_kapali_mi(g3, 'X', 'Y', [], ne=KIP_ARKA)}")
    s.append(f"  bütün uygun kümeler: "
             + ", ".join("{" + ",".join(sorted(z)) + "}" if z else "∅"
                         for z in arka_kapi_kumeleri(g3, "X", "Y")))
    # X → M → Y, Z ardıl (X'in nesli): şarta bağlanmamalı
    g4 = Cizge(("X", "M", "Y"), (("X", "M"), ("M", "Y")))
    s.append(f"  ardıla (M) bağlanmak uygun mu? {tesir_kapali_mi(g4, 'X', 'Y', ['M'], ne=KIP_ARKA)}"
             "   (hayır — X'in nesli)")

    s.append("\n=== Ön kapı (gözlenmemiş karıştırıcı varken) ===")
    # U gözlenmemiş: U→X, U→Y, X→M→Y
    g5 = Cizge(("U", "X", "M", "Y"),
               (("U", "X"), ("U", "Y"), ("X", "M"), ("M", "Y")))
    s.append(f"  M ön kapıyı sağlıyor mu? {tesir_kapali_mi(g5, 'X', 'Y', M=['M'], ne=KIP_ON)}")
    gozlenen = [z for z in arka_kapi_kumeleri(g5, "X", "Y") if "U" not in z]
    s.append(f"  U'suz arka kapı kümesi var mı? "
             f"{'evet: ' + str(gozlenen) if gozlenen else 'yok'}")
    s.append("  → arka kapı kapanmıyor ama ön kapı açık; ikisi ayrı âlet.")

    s.append("\n=== B-ayrışması: ortamlar arası ortak ===")
    # Ortamlar Z→Y kenarında ayrışıyor; Z→X→Y omurgası ikisinde de sabit.
    o1 = Cizge(("X", "Y", "Z"), (("Z", "X"), ("X", "Y"), ("Z", "Y")))
    o2 = Cizge(("X", "Y", "Z"), (("Z", "X"), ("X", "Y")))
    s.append("  omurga Z→X→Y ikisinde de var; ortam-1'de fazladan Z→Y var.")
    s.append(f"  ortam-1'de Z⫫Y|X = {tesir_kapali_mi(o1, ['Z'], ['Y'], ['X'])}"
             "   (fazla kenar yüzünden kapanmıyor)")
    s.append(f"  ortam-2'de Z⫫Y|X = {tesir_kapali_mi(o2, ['Z'], ['Y'], ['X'])}")
    s.append(f"  B-ayrık mı (ikisinde birden)? "
             f"{tesir_kapali_mi(cizgeler=[o1, o2], X=['Z'], Y=['Y'], Z=['X'], ne=KIP_B)}"
             "   → tek ortamda tutan ayrışma hüküm doğurmaz")
    o3 = Cizge(("X", "Y", "Z", "W"),
               (("Z", "X"), ("X", "Y"), ("W", "Y")))
    o4 = Cizge(("X", "Y", "Z", "W"),
               (("Z", "X"), ("X", "Y"), ("W", "Y"), ("W", "X")))
    s.append(f"  Z⫫W (iki ayrı ortamda): {tesir_kapali_mi(o3, ['Z'], ['W'])},"
             f" {tesir_kapali_mi(o4, ['Z'], ['W'])}"
             f" → B-ayrık={tesir_kapali_mi(cizgeler=[o3, o4], X=['Z'], Y=['W'], ne=KIP_B)}")
    ortak = ortak_ayrismalar([o3, o4])
    s.append(f"  son iki ortamın ortak ayrışmaları: "
             + (", ".join(f"{x}⫫{y}|{{{','.join(sorted(z)) or '∅'}}}"
                          for x, y, z in ortak) or "yok"))
    return "\n".join(s)



# ====================================================================
#  fitrat/karsi_olgusal.py
# ====================================================================

class YapisalModel:
    """``X_i = f_i(pa_i, u_i)`` — topolojik sırada çözülür.

    ``denklemler[d]``: ``(ebeveyn_değerleri: Dict[str,float], u: float)
    -> float``.  Toplamsal gürültü şart değildir; şart olmadığı için
    abduction'ın ne zaman tekilleştiği ayrıca sınanabiliyor.
    """

    def __init__(self, cizge: Cizge,
                 denklemler: Dict[str, Callable[[Dict[str, float], float],
                                                float]]):
        eksik = set(cizge.dugumler) - set(denklemler)
        if eksik:
            raise ValueError("denklemi olmayan düğüm: %s" % sorted(eksik))
        self.g = cizge
        self.f = denklemler
        self.sira = self._topolojik()

    def _topolojik(self) -> List[str]:
        derece = {d: len(self.g.ebeveyn[d]) for d in self.g.dugumler}
        hazir = [d for d in self.g.dugumler if derece[d] == 0]
        sira: List[str] = []
        while hazir:
            d = hazir.pop(0)
            sira.append(d)
            for c in sorted(self.g.cocuk[d]):
                derece[c] -= 1
                if derece[c] == 0:
                    hazir.append(c)
        return sira

    def coz(self, u: Dict[str, float],
            sabit: Optional[Dict[str, float]] = None) -> Dict[str, float]:
        """``Sol(G, u)`` — ``sabit``teki düğümler zorlanır (müdahale)."""
        sabit = sabit or {}
        X: Dict[str, float] = {}
        for d in self.sira:
            if d in sabit:
                X[d] = float(sabit[d])
                continue
            pa = {p: X[p] for p in self.g.ebeveyn[d]}
            X[d] = float(self.f[d](pa, u.get(d, 0.0)))
        return X


def budayarak_mudahale(g: Cizge, dugum: str) -> Cizge:
    """``do(X_k)`` — ``X_k``ye **giren** okları sil (``G_ampüte``).

    Çıkan okları silmek yanlış olurdu: müdahale nedeni koparır,
    neticeyi değil.
    """
    return Cizge(g.dugumler,
                 tuple((a, b) for a, b in g.kenarlar if b != dugum))


def abduction(M: YapisalModel, gozlem: Dict[str, float],
              cozucu_tur: int = 80) -> Dict[str, float]:
    """1. pas: gözlemden ``u``yu geri çıkar.

    Toplamsal gürültüde ``u_i = X_i − f_i(pa_i, 0)`` doğrudan; genel
    hâlde ``f_i(pa_i, u) = X_i`` tek değişkenli denklemi sayısal
    olarak çözülür (kesme yöntemi, ``u ∈ [−10³, 10³]``).  Çözüm
    bulunamazsa **NaN** dönülür; sessizce sıfır koymak, 3. pasın
    çıktısını sahte kılardı.
    """
    u: Dict[str, float] = {}
    for d in M.sira:
        pa = {p: gozlem[p] for p in M.g.ebeveyn[d]}
        hedef = gozlem[d]

        def r(v):
            return M.f[d](pa, v) - hedef

        a, b = -1e3, 1e3
        ra, rb = r(a), r(b)
        if ra == 0.0:
            u[d] = a
        elif rb == 0.0:
            u[d] = b
        elif ra * rb > 0:
            u[d] = float("nan")          # kök yok ya da tek değil
        else:
            for _ in range(cozucu_tur):
                m = 0.5 * (a + b)
                rm = r(m)
                if ra * rm <= 0:
                    b, rb = m, rm
                else:
                    a, ra = m, rm
            u[d] = 0.5 * (a + b)
    return u


def abduction_degismezi(M: YapisalModel, gozlem: Dict[str, float]
                        ) -> Dict[str, object]:
    """Formül 46.5: ``Sol(G_orijinal, u) == Y_göz`` mi?

    Bu, 1. pasın sağlamasıdır.  Bozuksa 3. pasın çıktısına
    **güvenilemez**; o yüzden :func:`karsiolgusal` bunu önce koşuyor.
    """
    u = abduction(M, gozlem)
    if any(math.isnan(v) for v in u.values()):
        return {"u": u, "sağlanıyor": False, "hata": float("inf"),
                "sebep": "abduction tekil: bazı u çözülemedi"}
    tekrar = M.coz(u)
    hata = max(abs(tekrar[d] - gozlem[d]) for d in gozlem)
    return {"u": u, "yeniden_çözüm": tekrar, "hata": float(hata),
            "sağlanıyor": bool(hata < 1e-8), "sebep": ""}


def karsiolgusal(M: YapisalModel, gozlem: Dict[str, float],
                 mudahale: Dict[str, float]) -> Dict[str, object]:
    """Üç pası birlikte koş; değişmez bozuksa **hüküm verme**."""
    d = abduction_degismezi(M, gozlem)
    if not d["sağlanıyor"]:
        return {"geçerli": False, "sebep": d.get("sebep") or
                "abduction değişmezi bozuk (hata %.3e)" % d["hata"],
                "abduction_hatası": d["hata"], "u": d["u"]}
    u = d["u"]
    g2 = M.g
    for k in mudahale:
        g2 = budayarak_mudahale(g2, k)
    M2 = YapisalModel(g2, M.f)
    Y = M2.coz(u, sabit=mudahale)
    delta = math.sqrt(sum((Y[k] - gozlem[k]) ** 2 for k in gozlem))
    return {"geçerli": True, "u": u, "karşıolgusal": Y,
            "Δ_cf": delta, "abduction_hatası": d["hata"],
            "budanan_kenar": [e for e in M.g.kenarlar
                              if e not in g2.kenarlar]}


def abduction_tekil_mi(M: YapisalModel, gozlem: Dict[str, float]
                       ) -> Dict[str, object]:
    """Hangi düğümde ``u`` geri çıkarılamıyor? — kutuplu tanı."""
    u = abduction(M, gozlem)
    tekil = sorted(d for d, v in u.items() if math.isnan(v))
    return {"tekil_düğümler": tekil, "tekil_mi": bool(tekil), "u": u}


def _matris_ustel(M: np.ndarray, tur: int = 200) -> np.ndarray:
    """``exp(M)`` — ölçekle-kare-al + Taylor (``scipy`` yok)."""
    M = np.asarray(M, float)
    n = max(int(np.ceil(np.log2(max(np.abs(M).sum(axis=1).max(), 1e-30)))) + 4,
            0)
    A = M / (2.0 ** n)
    S = np.eye(A.shape[0])
    T = np.eye(A.shape[0])
    for k in range(1, tur):
        T = T @ A / k
        S = S + T
        if np.abs(T).max() < 1e-18:
            break
    for _ in range(n):
        S = S @ S
    return S


def notears_h(A: np.ndarray) -> float:
    """``h(A) = tr(exp(A∘A)) − d`` — ``0`` ⟺ çevrimsiz."""
    A = np.asarray(A, float)
    return float(np.trace(_matris_ustel(A * A)) - A.shape[0])


def notears_gradyan(A: np.ndarray) -> np.ndarray:
    """``∂h/∂A = 2 (exp(A∘A))ᵀ ∘ A`` (Formül 45.3) — kaynak doğru yazmış."""
    A = np.asarray(A, float)
    return 2.0 * _matris_ustel(A * A).T * A


def cevrimsiz_mi_h_ile(A: np.ndarray, esik: float = 1e-8
                       ) -> Dict[str, object]:
    """``h(A) ≤ esik`` (Formül 45.5) ile kombinatorik sayımı kıyasla."""
    A = np.asarray(A, float)
    B = (np.abs(A) > 0).astype(int)
    # Kahn: kombinatorik hakikat
    derece = B.sum(axis=0).tolist()
    kuyruk = [i for i, k in enumerate(derece) if k == 0]
    say = 0
    while kuyruk:
        i = kuyruk.pop()
        say += 1
        for j in np.nonzero(B[i])[0]:
            derece[j] -= 1
            if derece[j] == 0:
                kuyruk.append(int(j))
    h = notears_h(A)
    return {"h": h, "h_diyor_ki": bool(abs(h) <= esik),
            "kombinatorik": bool(say == B.shape[0]), "eşik": esik}


def ortuk_sahte_baginti(n: int = 4000, a: float = 1.0, b: float = 1.0,
                        tohum: int = 0) -> Dict[str, float]:
    """``X ← L → Y``: ``L`` gözlenmezse ``X`` ile ``Y`` bağıntılı görünür.

    Üç okuma yan yana: (1) ham bağıntı, (2) ``L``ye koşullanmış kısmî
    bağıntı, (3) ``do(L = sabit)`` altındaki bağıntı.  İkisi de sahte
    bağıntıyı **keser**; ilki kesmez.
    """
    r = np.random.default_rng(tohum)
    L = r.normal(size=n)
    X = a * L + r.normal(size=n)
    Y = b * L + r.normal(size=n)

    def kor(u, v):
        return float(np.corrcoef(u, v)[0, 1])

    # L'ye koşullama = doğrusal artıklar üzerinden kısmî bağıntı
    ex = X - L * (X @ L) / (L @ L)
    ey = Y - L * (Y @ L) / (L @ L)
    Ld = np.zeros(n)                              # do(L = 0)
    Xd = a * Ld + r.normal(size=n)
    Yd = b * Ld + r.normal(size=n)
    return {"ham_bağıntı": kor(X, Y), "kısmî_bağıntı": kor(ex, ey),
            "do_L_altında": kor(Xd, Yd),
            "kuramsal_ham": a * b / math.sqrt((a * a + 1) * (b * b + 1))}


def locus_izdusumu(J: np.ndarray) -> np.ndarray:
    """``P = I − Jᵀ(JJᵀ)⁻¹J`` — ``ker(dφ)``ye dik izdüşüm.

    ``JJᵀ`` tekilse (kısıtlar bağımlıysa) sözde ters kullanılır:
    ``inv`` çağırmak orada patlardı.
    """
    J = np.atleast_2d(np.asarray(J, float))
    return np.eye(J.shape[1]) - J.T @ np.linalg.pinv(J @ J.T) @ J


def locus_uzerinde_yurut(phi: Callable[[np.ndarray], np.ndarray],
                         jac: Callable[[np.ndarray], np.ndarray],
                         hedef_grad: Callable[[np.ndarray], np.ndarray],
                         x0: np.ndarray, adim: float = 0.05,
                         tur: int = 200, duzelt: bool = True
                         ) -> Dict[str, object]:
    """``S = {φ = 0}`` üzerinde inişi yürüt.

    ``duzelt=False`` iken salt teğet izdüşümü kullanılır: ikinci
    mertebeden **kayma** birikir ve nokta locus'tan çıkar.  ``True``
    iken her adımdan sonra bir Newton düzeltmesi
    (``x ← x − J⁺φ(x)``) yapılır ve kayma bastırılır.  İkisi
    kıyaslanıyor.
    """
    x = np.asarray(x0, float).copy()
    ihlal, deger = [], []
    for _ in range(tur):
        J = np.atleast_2d(jac(x))
        x = x - adim * (locus_izdusumu(J) @ hedef_grad(x))
        if duzelt:
            J = np.atleast_2d(jac(x))
            x = x - np.linalg.pinv(J) @ np.atleast_1d(phi(x))
        ihlal.append(float(np.abs(np.atleast_1d(phi(x))).max()))
        deger.append(x.copy())
    return {"x": x, "ihlal_seyri": ihlal, "son_ihlal": ihlal[-1],
            "azamî_ihlal": float(max(ihlal)), "yol": deger}


def _ornek_model() -> YapisalModel:
    """``Z → X → Y``, ``Z → Y`` — toplamsal gürültü."""
    g = Cizge(("Z", "X", "Y"), (("Z", "X"), ("X", "Y"), ("Z", "Y")))
    return YapisalModel(g, {
        "Z": lambda pa, u: u,
        "X": lambda pa, u: 2.0 * pa["Z"] + u,
        "Y": lambda pa, u: 3.0 * pa["X"] - 1.0 * pa["Z"] + u,
    })


def _rapor_fitrat_karsi_olgusal() -> str:
    s = []
    M = _ornek_model()
    goz = M.coz({"Z": 0.5, "X": -0.2, "Y": 1.3})

    s.append("=== Karşıolgusal 3-pas ===")
    s.append("  model: Z→X, X→Y, Z→Y;  X = 2Z+u_X,  Y = 3X−Z+u_Y")
    s.append("  gözlem: " + ", ".join("%s=%.4f" % (k, goz[k])
                                      for k in ("Z", "X", "Y")))
    d = abduction_degismezi(M, goz)
    s.append("  1. pas (abduction): u = " +
             ", ".join("%s=%.4f" % (k, d["u"][k]) for k in ("Z", "X", "Y")))
    s.append("  Formül 46.5 değişmezi: Sol(G, u) == Y_göz mü? %s "
             "(hata %.2e)" % (d["sağlanıyor"], d["hata"]))
    for x in (-2.0, 0.0, 2.0):
        r = karsiolgusal(M, goz, {"X": x})
        s.append("  do(X=%+.1f): Y=%+.4f  (gözlemde %+.4f)   Δ_cf=%.4f   "
                 "budanan kenar=%s"
                 % (x, r["karşıolgusal"]["Y"], goz["Y"], r["Δ_cf"],
                    r["budanan_kenar"]))
    s.append("  Kapalı form: do(X=x) altında Y = 3x − Z + u_Y")
    for x in (-2.0, 0.0, 2.0):
        s.append("    x=%+.1f → %+.4f" % (x, 3 * x - goz["Z"] + d["u"]["Y"]))
    s.append("  Z gözlemden GELİYOR (müdahale onu koparmıyor); asıl")
    s.append("  karşıolgusallık burada: kişiye özgü u korunuyor.")

    s.append("\n=== Müdahale çıkan oku DEĞİL giren oku siler ===")
    g2 = budayarak_mudahale(M.g, "X")
    s.append("  do(X) sonrası kenarlar: %s" % (list(g2.kenarlar),))
    s.append("  X→Y duruyor (netice), Z→X gitti (sebep). Tersi olsaydı")
    s.append("  müdahalenin hiçbir tesiri kalmazdı.")

    s.append("\n=== Abduction ne zaman TEKİL kalır? ===")
    g = Cizge(("A", "B"), (("A", "B"),))
    iyi = YapisalModel(g, {"A": lambda pa, u: u,
                           "B": lambda pa, u: pa["A"] + u})
    kotu = YapisalModel(g, {"A": lambda pa, u: u,
                            "B": lambda pa, u: pa["A"] + u * u})
    for ad, mm in (("toplamsal  u", iyi), ("u² (tek yönlü)", kotu)):
        gg = mm.coz({"A": 1.0, "B": 2.0})
        t = abduction_tekil_mi(mm, gg)
        s.append("  %s: gözlem B=%.3f  tekil mi? %-5s  tekil düğüm=%s"
                 % (ad, gg["B"], t["tekil_mi"], t["tekil_düğümler"]))
    gg = {"A": 1.0, "B": 0.5}       # B < A: u² = −0.5, kök YOK
    t = abduction_tekil_mi(kotu, gg)
    s.append("  u² modelinde B=0.5 (yani u²=−0.5) istenirse: tekil mi? %s %s"
             % (t["tekil_mi"], t["tekil_düğümler"]))
    r = karsiolgusal(kotu, gg, {"A": 3.0})
    s.append("  bu hâlde karşıolgusal hüküm VERİLMİYOR: geçerli=%s (%s)"
             % (r["geçerli"], r["sebep"]))
    s.append("  Kaynağın 'denklem tekil kalıyor' dediği hâl budur; şartı")
    s.append("  yazmıyordu — gürültü doğrusal olmayan biçimde girerse.")

    s.append("\n=== NOTEARS h(A): çevrimsizlik değişmezi ===")
    ornekler = [
        ("üçgen DAG", np.array([[0, 1, 1], [0, 0, 1], [0, 0, 0.]])),
        ("2-çevrim", np.array([[0, 1, 0], [1, 0, 0], [0, 0, 0.]])),
        ("3-çevrim", np.array([[0, 1, 0], [0, 0, 1], [1, 0, 0.]])),
        ("öz-döngü", np.array([[0.3, 0, 0], [0, 0, 0], [0, 0, 0.]])),
        ("boş", np.zeros((3, 3))),
    ]
    for ad, A in ornekler:
        c = cevrimsiz_mi_h_ile(A)
        s.append("  %-10s h(A)=%.6e   h diyor ki=%-5s  kombinatorik=%-5s  "
                 "uyuşuyor: %s"
                 % (ad, c["h"], c["h_diyor_ki"], c["kombinatorik"],
                    c["h_diyor_ki"] == c["kombinatorik"]))
    s.append("  Gradyan sağlaması (Formül 45.3, sonlu farkla):")
    r2 = np.random.default_rng(0)
    for _ in range(3):
        A = r2.normal(size=(4, 4)) * 0.4
        G = notears_gradyan(A)
        S = np.zeros_like(A)
        h_ = 1e-6
        for i, j in itertools.product(range(4), repeat=2):
            Ap, Am = A.copy(), A.copy()
            Ap[i, j] += h_
            Am[i, j] -= h_
            S[i, j] = (notears_h(Ap) - notears_h(Am)) / (2 * h_)
        s.append("    azamî bağıl fark = %.2e"
                 % float(np.abs(G - S).max() / max(np.abs(S).max(), 1e-30)))

    s.append("\n=== Örtük değişken: sahte bağıntı ===")
    for a, b in ((1.0, 1.0), (2.0, 0.5), (1.0, 0.0)):
        o = ortuk_sahte_baginti(a=a, b=b, tohum=1)
        s.append("  a=%.1f b=%.1f: ham=%+.4f (kuram %+.4f)  "
                 "L'ye koşullu=%+.4f  do(L)=%+.4f"
                 % (a, b, o["ham_bağıntı"], o["kuramsal_ham"],
                    o["kısmî_bağıntı"], o["do_L_altında"]))
    s.append("  Ham bağıntı kuramsal değeri tutuyor; koşullama ve do(L)")
    s.append("  ikisi de sahte yolu kesiyor. b=0'da zaten bağıntı yok.")

    s.append("\n=== Denge lokusu: teğet izdüşümü yetiyor mu? ===")
    # φ(x) = ‖x‖² − 1 (birim çember), hedef: x₀'ı küçült
    def phi(x):
        return np.array([float(x @ x) - 1.0])

    def jac(x):
        return 2.0 * x[None, :]

    def grad(x):
        return np.array([1.0, 0.0])

    # Başlangıç (1,0) OLMAZ: orada gradyan tamamen normal yönde, teğet
    # izdüşümü sıfır verir ve hiçbir şey kımıldamaz (ölçüldü: ihlal 0,
    # varılan nokta yine (1,0)).  Genel bir noktadan başlanıyor.
    x0 = np.array([math.cos(0.4), math.sin(0.4)])
    for adim in (0.05, 0.2, 0.5):
        a_ = locus_uzerinde_yurut(phi, jac, grad, x0, adim=adim, duzelt=False)
        b_ = locus_uzerinde_yurut(phi, jac, grad, x0, adim=adim, duzelt=True)
        s.append("  adım=%.2f  düzeltmesiz azamî ihlal=%.2e   "
                 "düzeltmeli=%.2e   varılan x=(%+.4f,%+.4f)"
                 % (adim, a_["azamî_ihlal"], b_["azamî_ihlal"],
                    b_["x"][0], b_["x"][1]))
    s.append("  Teğet izdüşümü tek başına YETMİYOR: ikinci mertebeden")
    s.append("  kayma birikiyor ve adım büyüdükçe ihlal büyüyor.")
    s.append("  Newton düzeltmesiyle nokta locus'ta kalıyor ve")
    s.append("  x₀ = −1 asgarîsine varıyor (‖x‖=1 üzerinde doğru cevap).")
    return "\n".join(s)


# ====================================================================
#  fitrat/serbest_enerji.py
# ====================================================================

EPS_LOG = 1e-300          # logaritma tabanı: sıfırın logu alınmasın


@dataclass(frozen=True)
class AyrikModel:
    """``K`` gizli hâl, ``N`` gözlem değeri.

    ``pz``: ``(K,)`` önsel.  ``pxz``: ``(K, N)`` şartlı olabilirlik.
    İkisi de satır bazında toplamı 1 olmak zorundadır; kurulurken
    **denetlenir** — normalize edilmemiş bir tablo bütün büyüklükleri
    sessizce bozar.
    """
    pz: np.ndarray
    pxz: np.ndarray

    def __post_init__(self) -> None:
        object.__setattr__(self, "pz", np.asarray(self.pz, float))
        object.__setattr__(self, "pxz", np.asarray(self.pxz, float))
        if self.pz.ndim != 1 or self.pxz.ndim != 2:
            raise ValueError("pz (K,), pxz (K,N) olmalı")
        if self.pxz.shape[0] != self.pz.size:
            raise ValueError("pz ile pxz'nin K'sı uyuşmuyor")
        if abs(self.pz.sum() - 1.0) > 1e-10:
            raise ValueError("pz toplamı 1 değil")
        if np.any(np.abs(self.pxz.sum(axis=1) - 1.0) > 1e-10):
            raise ValueError("pxz satır toplamları 1 değil")
        if np.any(self.pz < 0) or np.any(self.pxz < 0):
            raise ValueError("olasılıklar negatif olamaz")

    @property
    def K(self) -> int:
        return self.pz.size

    @property
    def N(self) -> int:
        return self.pxz.shape[1]

    def ortak(self, x: int) -> np.ndarray:
        """``p(x, z)`` — ``z`` üzerinde vektör."""
        return self.pz * self.pxz[:, x]


def kl(q: np.ndarray, p: np.ndarray) -> float:
    """``D_KL(q‖p) = Σ q ln(q/p)``.

    ``q_i = 0`` olan terimler ``0 ln 0 = 0`` kabulüyle atlanır (limit
    doğrudur).  ``q_i > 0`` iken ``p_i = 0`` ise KL sonsuzdur ve
    ``inf`` döner — büyük bir sayıyla değiştirilmez, çünkü o hâlde
    sınır da anlamını yitirir ve bunun görünmesi gerekir.
    """
    q = np.asarray(q, float)
    p = np.asarray(p, float)
    m = q > 0
    if np.any(p[m] <= 0):
        return float("inf")
    return float(np.sum(q[m] * (np.log(q[m]) - np.log(p[m]))))


def kanit_log(model: AyrikModel, x: int) -> float:
    """``ln p(x)`` — kapalı form (küçük ayrık modelde toplayarak)."""
    return float(np.log(model.ortak(x).sum()))


def ardil(model: AyrikModel, x: int) -> np.ndarray:
    """Tam ardıl ``p(z|x)`` — ELBO'nun sıkı olduğu tek nokta."""
    o = model.ortak(x)
    return o / o.sum()


def elbo(model: AyrikModel, q: np.ndarray, x: int) -> float:
    """``E_q[ln p(x,z) − ln q(z)]``."""
    q = np.asarray(q, float)
    if abs(q.sum() - 1.0) > 1e-9:
        raise ValueError("q normalize değil")
    o = model.ortak(x)
    m = q > 0
    if np.any(o[m] <= 0):
        return float("-inf")
    return float(np.sum(q[m] * (np.log(o[m]) - np.log(q[m]))))


def serbest_enerji(model: AyrikModel, q: np.ndarray, x: int) -> float:
    """``F = −ELBO``.  Sınır: ``F ≥ −ln p(x)``."""
    return -elbo(model, q, x)


def serbest_enerji_ayrisimi(model: AyrikModel, q: np.ndarray, x: int
                            ) -> Dict[str, float]:
    """``F = kesinsizlik + karmaşıklık`` ayrışımı ve sağlaması."""
    q = np.asarray(q, float)
    m = q > 0
    kesinsizlik = -float(np.sum(q[m] * np.log(np.maximum(model.pxz[m, x],
                                                         EPS_LOG))))
    karmasiklik = kl(q, model.pz)
    F = serbest_enerji(model, q, x)
    return {
        "kesinsizlik": kesinsizlik,
        "karmaşıklık": karmasiklik,
        "toplam": kesinsizlik + karmasiklik,
        "F": F,
        "ayrışım_sapması": abs(kesinsizlik + karmasiklik - F),
    }


def sinir_dogrula(model: AyrikModel, x: int, deneme: int = 2000,
                  tohum: int = 0) -> Dict[str, object]:
    """``F ≥ −ln p(x)`` sınırını rastgele ``q``larda tartar.

    Ayrıca **eşitlik ancak ardılda** iddiasını sınar: en küçük boşluk
    veren ``q``, tam ardıla ne kadar yakın?
    """
    r = np.random.default_rng(tohum)
    surpriz = -kanit_log(model, x)
    p_zx = ardil(model, x)
    en_kucuk = float("inf")
    en_kucuk_q: Optional[np.ndarray] = None
    ihlal = 0
    for _ in range(deneme):
        q = r.dirichlet(np.ones(model.K))
        F = serbest_enerji(model, q, x)
        bosluk = F - surpriz
        if bosluk < -1e-12:
            ihlal += 1
        if bosluk < en_kucuk:
            en_kucuk, en_kucuk_q = bosluk, q
    F_ardil = serbest_enerji(model, p_zx, x)
    return {
        "sürpriz −ln p(x)": surpriz,
        "ihlal_sayısı": ihlal,
        "en_küçük_boşluk": en_kucuk,
        "ardılda_boşluk": F_ardil - surpriz,
        "en_iyi_q'nun_ardıla_KL'i": kl(en_kucuk_q, p_zx),
        "boşluk = KL(q‖p(z|x)) mi?": abs(en_kucuk - kl(en_kucuk_q, p_zx)),
    }


def koordinat_inisi(model: AyrikModel, x: int, adim: int = 50,
                    tohum: int = 0) -> Dict[str, object]:
    """``F``yi ``q`` üzerinde azaltmak, ardıla yakınsamalı.

    Kapalı çözümü bilinen bir hâlde gradyan inişine gerek yoktur:
    ``F``nin ``q`` üzerindeki asgarisi doğrudan ``q ∝ p(x,z)``dir.
    Yine de iteratif iniş yazılır ki **yakınsadığı yer** bağımsız
    olarak doğrulanabilsin.
    """
    r = np.random.default_rng(tohum)
    q = r.dirichlet(np.ones(model.K))
    o = model.ortak(x)
    tarih: List[float] = []
    for _ in range(adim):
        tarih.append(serbest_enerji(model, q, x))
        # F(q) = −Σq ln o + Σ q ln q ; ∂F/∂q_k = −ln o_k + ln q_k + 1
        # Lagrange ile normalize edilmiş sabit nokta: q ∝ o (yumuşatılmış)
        hedef = o / o.sum()
        q = 0.5 * q + 0.5 * hedef        # sönümlü, tek adımda atlamasın
        q = q / q.sum()
    tarih.append(serbest_enerji(model, q, x))
    return {
        "son_F": tarih[-1],
        "sürpriz": -kanit_log(model, x),
        "ardıla_KL": kl(q, ardil(model, x)),
        "azalıyor_mu": all(tarih[i] >= tarih[i + 1] - 1e-12
                           for i in range(len(tarih) - 1)),
        "tarih": tarih,
    }


def gauss_kl(m1: float, s1: float, m2: float, s2: float) -> float:
    """``D_KL(N(m₁,s₁²) ‖ N(m₂,s₂²))`` — kapalı form.

    .. math::  \\ln\\frac{s_2}{s_1} + \\frac{s_1^2 + (m_1-m_2)^2}{2s_2^2}
               - \\frac12
    """
    if s1 <= 0 or s2 <= 0:
        raise ValueError("standart sapmalar pozitif olmalı")
    return float(np.log(s2 / s1) + (s1 ** 2 + (m1 - m2) ** 2)
                 / (2 * s2 ** 2) - 0.5)


def gauss_serbest_enerji(x: float, m_q: float, s_q: float,
                         m_p: float, s_p: float, s_g: float
                         ) -> Dict[str, float]:
    """Doğrusal Gauss modelinde ``F`` ve kapalı ``−ln p(x)``.

    Model: ``z ~ N(m_p, s_p²)``, ``x | z ~ N(z, s_g²)``.  O hâlde
    ``x ~ N(m_p, s_p² + s_g²)`` (kapalı) ve tam ardıl da Gauss'tur.

    ``F = E_q[−ln p(x|z)] + KL(q‖p(z))`` doğrudan hesaplanır:
    ``E_q[(x−z)²] = (x − m_q)² + s_q²``.
    """
    kesinsizlik = (0.5 * np.log(2 * np.pi * s_g ** 2)
                   + ((x - m_q) ** 2 + s_q ** 2) / (2 * s_g ** 2))
    karmasiklik = gauss_kl(m_q, s_q, m_p, s_p)
    F = float(kesinsizlik + karmasiklik)
    s_x = np.sqrt(s_p ** 2 + s_g ** 2)
    surpriz = float(0.5 * np.log(2 * np.pi * s_x ** 2)
                    + (x - m_p) ** 2 / (2 * s_x ** 2))
    # Tam ardıl: hassasiyetler toplanır
    tau = 1 / s_p ** 2 + 1 / s_g ** 2
    m_ardil = (m_p / s_p ** 2 + x / s_g ** 2) / tau
    s_ardil = np.sqrt(1 / tau)
    return {
        "F": F, "sürpriz": surpriz, "boşluk": F - surpriz,
        "KL(q‖ardıl)": gauss_kl(m_q, s_q, m_ardil, s_ardil),
        "ardıl_ortalama": float(m_ardil), "ardıl_sapma": float(s_ardil),
    }


def _rapor_fitrat_serbest_enerji() -> str:
    s: List[str] = []
    model = AyrikModel(
        pz=np.array([0.2, 0.5, 0.3]),
        pxz=np.array([[0.7, 0.2, 0.1],
                      [0.1, 0.6, 0.3],
                      [0.3, 0.3, 0.4]]),
    )
    x = 1

    s.append("=== Ayrık model, x=1 ===")
    s.append(f"  ln p(x)   = {kanit_log(model, x):.10f}")
    s.append(f"  tam ardıl = {np.array2string(ardil(model, x), precision=6)}")

    s.append("\n=== Sınır: F ≥ −ln p(x) ===")
    r = sinir_dogrula(model, x, deneme=5000, tohum=1)
    s.append(f"  sürpriz −ln p(x)      = {r['sürpriz −ln p(x)']:.10f}")
    s.append(f"  5000 rastgele q'da ihlal = {r['ihlal_sayısı']}")
    s.append(f"  en küçük boşluk       = {r['en_küçük_boşluk']:.3e}")
    s.append(f"  ardılda boşluk        = {r['ardılda_boşluk']:.3e}"
             "   (sıfır olmalı — sınır orada sıkı)")
    s.append(f"  boşluk = KL(q‖p(z|x)) özdeşliğinin sapması = "
             f"{r['boşluk = KL(q‖p(z|x)) mi?']:.3e}")

    s.append("\n=== Ayrışım: F = kesinsizlik + karmaşıklık ===")
    for ad, q in (("tam ardıl", ardil(model, x)),
                  ("düz q", np.ones(3) / 3),
                  ("keskin q", np.array([0.98, 0.01, 0.01]))):
        a = serbest_enerji_ayrisimi(model, q, x)
        s.append(f"  {ad:10s} kesinsizlik={a['kesinsizlik']:.6f}"
                 f"  karmaşıklık={a['karmaşıklık']:.6f}"
                 f"  F={a['F']:.6f}  sapma={a['ayrışım_sapması']:.2e}")

    s.append("\n=== Koordinat inişi ardıla varıyor mu? ===")
    ki = koordinat_inisi(model, x, adim=60, tohum=7)
    s.append(f"  son F={ki['son_F']:.10f}  sürpriz={ki['sürpriz']:.10f}")
    s.append(f"  ardıla KL = {ki['ardıla_KL']:.3e}"
             f"   F her adımda azaldı mı? {ki['azalıyor_mu']}")

    s.append("\n=== Gauss hâli (kapalı formüllerle) ===")
    for ad, (mq, sq) in (("q = ardıl", (None, None)),
                         ("q = önsel", (0.0, 1.0)),
                         ("q = kaymış", (2.0, 0.3))):
        if mq is None:
            g0 = gauss_serbest_enerji(1.5, 0.0, 1.0, 0.0, 1.0, 0.5)
            mq, sq = g0["ardıl_ortalama"], g0["ardıl_sapma"]
        g = gauss_serbest_enerji(1.5, mq, sq, 0.0, 1.0, 0.5)
        s.append(f"  {ad:10s} F={g['F']:.8f} sürpriz={g['sürpriz']:.8f}"
                 f" boşluk={g['boşluk']:.3e} KL(q‖ardıl)={g['KL(q‖ardıl)']:.3e}")
    s.append("  → boşluk ile KL(q‖ardıl) her satırda aynı sayı; bu,"
             " sınırın ispatındaki özdeşliğin kendisidir.")
    return "\n".join(s)



# ====================================================================
#  fitrat/denge.py
# ====================================================================

EPS_MAKINE = np.finfo(float).eps   # makine hassasiyeti


_H3 = EPS_MAKINE ** (1.0 / 3.0)


@dataclass(frozen=True)
class Oyun:
    """``n`` failli bir oyun.

    ``F(x, θ)`` birinci mertebe şartlarını verir; içsel dengede sıfırdır.
    ``n`` fail sayısı, ``p`` parametre sayısıdır.
    """
    n: int
    p: int
    F: Callable[[np.ndarray, np.ndarray], np.ndarray]
    ad: str = ""

    def artik(self, x: np.ndarray, teta: np.ndarray) -> float:
        """Birinci mertebe şartlarının ihlali — dengede sıfır."""
        return float(np.linalg.norm(self.F(np.asarray(x, float),
                                           np.asarray(teta, float))))


def merkezi_jakobi(g: Callable[[np.ndarray], np.ndarray],
                   x: np.ndarray) -> np.ndarray:
    """``g``'nin ``x``teki Jacobi'si, merkezî farkla (hata ``O(h²)``).

    Her koordinat için adım ayrı ölçeklenir: ``h_j = ε^{1/3}·max(1,|x_j|)``.
    Sabit bir ``h`` kullanmak, büyük ve küçük koordinatların bir arada
    bulunduğu hâllerde birinde kesme, diğerinde yuvarlama hatası doğurur.
    """
    x = np.asarray(x, float)
    g0 = np.asarray(g(x), float)
    J = np.empty((g0.size, x.size))
    for j in range(x.size):
        h = _H3 * max(1.0, abs(x[j]))
        arti = x.copy(); arti[j] += h
        eksi = x.copy(); eksi[j] -= h
        # Fiilî adım, kayan noktada yuvarlandıktan sonraki farktır:
        gercek = arti[j] - eksi[j]
        J[:, j] = (np.asarray(g(arti), float)
                   - np.asarray(g(eksi), float)) / gercek
    return J


def newton_koku(g: Callable[[np.ndarray], np.ndarray],
                x0: np.ndarray,
                tol: float = 1e-11,
                azami_adim: int = 100
                ) -> Tuple[np.ndarray, bool, int, float]:
    """``g(x) = 0`` için sönümlü Newton.

    Sönüm (line search) şart: sönümsüz Newton uzak başlangıçlarda
    ıraksayabilir.  Adım, artık normunu **düşürene** kadar yarılanır;
    hiçbir yarılama düşürmüyorsa durulur ve ``yakinsadi=False`` döner —
    yakınsamamış bir sonuç yakınsamış gibi sunulmaz.

    Dönen: ``(x, yakınsadı, adım sayısı, son artık)``.
    """
    x = np.array(x0, float)
    art = float(np.linalg.norm(g(x)))
    for k in range(azami_adim):
        if art < tol:
            return x, True, k, art
        J = merkezi_jakobi(g, x)
        try:
            adim = np.linalg.solve(J, -np.asarray(g(x), float))
        except np.linalg.LinAlgError:
            adim = -np.linalg.lstsq(J, np.asarray(g(x), float), rcond=None)[0]
        t = 1.0
        for _ in range(40):
            yeni = x + t * adim
            yeni_art = float(np.linalg.norm(g(yeni)))
            if yeni_art < art:
                break
            t *= 0.5
        else:
            return x, False, k, art        # hiçbir sönüm düşürmedi
        x, art = yeni, yeni_art
    return x, art < tol, azami_adim, art


def denge_bul(oyun: Oyun, teta: Sequence[float],
              x0: Optional[Sequence[float]] = None,
              tol: float = 1e-11) -> Dict[str, object]:
    """Oyunun içsel dengesini bul ve hâlini bildir."""
    teta = np.asarray(teta, float)
    if teta.size != oyun.p:
        raise ValueError(f"θ boyu {oyun.p} olmalı, {teta.size} verildi")
    baslangic = np.zeros(oyun.n) if x0 is None else np.asarray(x0, float)
    g = lambda x: oyun.F(x, teta)
    x, tamam, adim, art = newton_koku(g, baslangic, tol)
    return {"x": x, "yakınsadı": tamam, "adım": adim, "artık": art,
            "θ": teta}


def spektral_yaricap(M: np.ndarray) -> float:
    """``ρ(M) = max |λ_i|`` — özdeğerlerin azamî mutlak değeri."""
    return float(np.max(np.abs(np.linalg.eigvals(np.asarray(M, float)))))


def kararli_mi(oyun: Oyun, x: np.ndarray, teta: Sequence[float]
               ) -> Dict[str, object]:
    """En iyi karşılık dinamiğinin yerel kararlılığı.

    ``F(x)=0`` sisteminin ``ẋ = F(x)`` akışı olarak kararlılığı,
    ``∂_x F``in özdeğerlerinin **reel kısımlarının negatifliğine**
    bakar (Lyapunov).  Ayrıca en iyi karşılık **iterasyonunun**
    (ayrık zaman) kararlılığı için ``ρ(I + ∂_xF)`` değil, sabit nokta
    dönüşümünün Jacobi'si gerekir; ikisi ayrı sorulardır ve burada
    ikisi de ayrı ayrı bildirilir, biri diğerinin yerine geçmez.
    """
    teta = np.asarray(teta, float)
    J = merkezi_jakobi(lambda z: oyun.F(z, teta), np.asarray(x, float))
    ozd = np.linalg.eigvals(J)
    return {
        "∂ₓF": J,
        "özdeğerler": ozd,
        "akış_kararlı": bool(np.all(ozd.real < -1e-12)),
        "azamî_reel_kısım": float(np.max(ozd.real)),
        "tekil_mi": bool(abs(np.linalg.det(J)) < 1e-12),
    }


def en_iyi_karsilik_iterasyonu(
        en_iyi: Callable[[np.ndarray], np.ndarray],
        x0: Sequence[float], azami: int = 500,
        tol: float = 1e-12) -> Dict[str, object]:
    """``x ← EnİyiKarşılık(x)`` sabit nokta iterasyonu.

    Yakınsarsa dengedir; yakınsamazsa **yakınsamadı** denir.  Ayrıca son
    adımdaki büzülme oranı ölçülür: ``<1`` ise yerel büzülme vardır.
    """
    x = np.asarray(x0, float)
    farklar: List[float] = []
    for k in range(azami):
        y = np.asarray(en_iyi(x), float)
        f = float(np.linalg.norm(y - x))
        farklar.append(f)
        x = y
        if f < tol:
            return {"x": x, "yakınsadı": True, "adım": k + 1,
                    "farklar": farklar,
                    "son_oran": (farklar[-1] / farklar[-2]
                                 if len(farklar) > 1 and farklar[-2] > 0
                                 else 0.0)}
    return {"x": x, "yakınsadı": False, "adım": azami, "farklar": farklar,
            "son_oran": (farklar[-1] / farklar[-2]
                         if len(farklar) > 1 and farklar[-2] > 0 else None)}


def ortuk_fonksiyon_turevi(oyun: Oyun, x: np.ndarray,
                           teta: Sequence[float],
                           tekillik_esigi: float = 1e-10
                           ) -> Optional[np.ndarray]:
    """``∂x*/∂θ = −(∂ₓF)⁻¹ ∂_θF`` — ya da şart sağlanmıyorsa ``None``.

    Örtük fonksiyon teoreminin şartı ``∂ₓF``in tersinir olmasıdır.
    Tekilse denge parametreye göre türevlenebilir bir fonksiyon olmak
    zorunda **değildir**; o hâlde bir sayı uydurmak yerine ``None``
    döndürülür.  Tekillik, koşul sayısıyla ölçülür (determinantla
    değil — determinant ölçekle birlikte patlar).
    """
    x = np.asarray(x, float)
    teta = np.asarray(teta, float)
    Fx = merkezi_jakobi(lambda z: oyun.F(z, teta), x)
    if 1.0 / max(np.linalg.cond(Fx), 1e-300) < tekillik_esigi:
        return None
    Ft = merkezi_jakobi(lambda t: oyun.F(x, t), teta)
    return -np.linalg.solve(Fx, Ft)


def hassasiyet_sonlu_farkla(oyun: Oyun, teta: Sequence[float],
                            x0: Optional[Sequence[float]] = None,
                            h: float = 1e-5) -> np.ndarray:
    """Aynı hassasiyeti dengeyi **yeniden çözerek** hesaplar.

    Örtük fonksiyon teoremiyle çıkanla karşılaştırmak içindir: iki
    bağımsız yol aynı sayıya varmalıdır.  Pahalıdır (her parametre için
    iki tam Newton çözümü), o yüzden asıl yol teoremdir.
    """
    teta = np.asarray(teta, float)
    taban = denge_bul(oyun, teta, x0)["x"]
    D = np.empty((oyun.n, oyun.p))
    for j in range(oyun.p):
        arti = teta.copy(); arti[j] += h
        eksi = teta.copy(); eksi[j] -= h
        xa = denge_bul(oyun, arti, taban)["x"]
        xe = denge_bul(oyun, eksi, taban)["x"]
        D[:, j] = (xa - xe) / (arti[j] - eksi[j])
    return D


def cournot(n: int) -> Oyun:
    """``n`` firmalı doğrusal Cournot oyunu.

    Ters talep ``P(Q) = a − b·Q``, maliyet ``c_i·x_i``.  Fayda
    ``u_i = (a − b·Σx)·x_i − c_i x_i``, birinci mertebe şartı:

    .. math::  F_i = a - b\\Bigl(\\sum_j x_j\\Bigr) - b x_i - c_i = 0

    FOC'ları toplayınca ``Q = (na − Σc)/(b(n+1))``, geri koyunca genel
    kapalı çözüm çıkar:

    .. math::  x_i^\\star = \\frac{a - (n+1)c_i + \\sum_j c_j}{b(n+1)}

    Simetrik hâlde (``c_i = c``) bu ``x* = (a−c)/(b(n+1))``e iner.  Bu, sayısal çözümün sağlaması için
    kullanılır — beklenen cevabı bağımsız olarak bilmek şarttır.

    θ = (a, b, c₀, …, c_{n−1}), yani ``p = n + 2``.
    """
    def F(x: np.ndarray, teta: np.ndarray) -> np.ndarray:
        a, b = teta[0], teta[1]
        c = teta[2:]
        Q = float(np.sum(x))
        return a - b * Q - b * x - c

    return Oyun(n=n, p=n + 2, F=F, ad=f"Cournot({n})")


def cournot_kapali_cozum(n: int, a: float, b: float, c: float) -> float:
    """Simetrik Cournot dengesi — kalemle çıkarılan cevap."""
    return (a - c) / (b * (n + 1))


def _rapor_fitrat_denge() -> str:
    s: List[str] = []
    n, a, b, c = 4, 10.0, 1.0, 2.0
    oyun = cournot(n)
    teta = np.array([a, b] + [c] * n)

    s.append("=== Cournot dengesi (n=4, a=10, b=1, c=2) ===")
    r = denge_bul(oyun, teta)
    beklenen = cournot_kapali_cozum(n, a, b, c)
    s.append(f"  sayısal x* = {np.array2string(r['x'], precision=10)}")
    s.append(f"  kapalı  x* = {beklenen:.10f}")
    s.append(f"  azamî fark = {np.max(np.abs(r['x'] - beklenen)):.3e}"
             f"   ({r['adım']} Newton adımı, artık {r['artık']:.2e})")

    s.append("\n=== Kararlılık ===")
    k = kararli_mi(oyun, r["x"], teta)
    s.append(f"  ∂ₓF özdeğerlerinin azamî reel kısmı = "
             f"{k['azamî_reel_kısım']:.6f}")
    s.append(f"  akış kararlı mı? {k['akış_kararlı']}   tekil mi? {k['tekil_mi']}")

    s.append("\n=== En iyi karşılık iterasyonu ===")
    def en_iyi(x):
        # x_i = (a − c_i − b·Σ_{j≠i} x_j) / (2b)
        Q = float(np.sum(x))
        return (a - c - b * (Q - x)) / (2 * b)
    it = en_iyi_karsilik_iterasyonu(en_iyi, np.zeros(n))
    s.append(f"  eşzamanlı: yakınsadı={it['yakınsadı']}"
             f" son oran={it['son_oran']:.6f}")
    s.append("  IRAKSIYOR — ve bu bir kusur değil, oyunun kendi hâlidir:")
    s.append("  eşzamanlı en iyi karşılığın Jacobi'si −(n−1)/2·(1−I) yapısında,")
    s.append(f"  spektral yarıçapı (n−1)/2 = {(n - 1) / 2:.1f} > 1 (n≥4 için).")
    s.append("  Newton bu yüzden lazım; yahut sönüm konur:")
    for kappa in (0.5, 0.3):
        sonumlu = lambda x, k=kappa: (1 - k) * x + k * en_iyi(x)
        its = en_iyi_karsilik_iterasyonu(sonumlu, np.zeros(n))
        fark = (np.max(np.abs(its["x"] - r["x"]))
                if its["yakınsadı"] else float("nan"))
        s.append(f"    κ={kappa}: yakınsadı={its['yakınsadı']}"
                 f" adım={its['adım']} oran={its['son_oran']:.4f}"
                 f" Newton'dan fark={fark:.2e}")

    s.append("\n=== Hassasiyet: ∂x*/∂θ ===")
    D = ortuk_fonksiyon_turevi(oyun, r["x"], teta)
    Dsf = hassasiyet_sonlu_farkla(oyun, teta)
    s.append(f"  örtük fonksiyon teoremi ∂x*/∂a = {D[0, 0]:.10f}")
    s.append(f"  sonlu farkla            ∂x*/∂a = {Dsf[0, 0]:.10f}")
    s.append(f"  kapalı çözümden 1/(b(n+1)) = "
             f"{1.0 / (b * (n + 1)):.10f}")
    s.append(f"  iki sayısal yolun azamî farkı = "
             f"{np.max(np.abs(D - Dsf)):.3e}")
    s.append(f"  kendi maliyetine göre ∂x*_0/∂c_0 = {D[0, 2]:.10f}"
             f"   kapalı −n/(b(n+1)) = {-n / (b * (n + 1)):.10f}")

    # Asimetrik hâl: kapalı çözüm x_i = (a − n c_i + Σ_j c_j) / (b(n+1))
    s.append("\n=== Asimetrik maliyetler — kapalı çözümle sağlama ===")
    cc = np.array([1.0, 2.0, 3.0, 4.0])
    teta2 = np.concatenate(([a, b], cc))
    r2 = denge_bul(oyun, teta2)
    # FOC'lar toplanınca Q = (na − Σc)/(b(n+1)); geri koyunca:
    #   x_i = [a − (n+1)c_i + Σc] / (b(n+1))
    kapali = (a - (n + 1) * cc + np.sum(cc)) / (b * (n + 1))
    s.append(f"  sayısal = {np.array2string(r2['x'], precision=8)}")
    s.append(f"  kapalı  = {np.array2string(kapali, precision=8)}")
    s.append(f"  azamî fark = {np.max(np.abs(r2['x'] - kapali)):.3e}")
    D2 = ortuk_fonksiyon_turevi(oyun, r2["x"], teta2)
    s.append(f"  ∂x*_0/∂c_0 = {D2[0, 2]:.10f}"
             f"   kapalı −n/(b(n+1)): {-n / (b * (n + 1)):.10f}")
    s.append(f"  ∂x*_0/∂c_1 = {D2[0, 3]:.10f}"
             f"   kapalı 1/(b(n+1)): {1.0 / (b * (n + 1)):.10f}")

    s.append("\n=== Tekil hâl: teoremin şartı sağlanmazsa ===")
    tekil = Oyun(n=2, p=1, F=lambda x, t: np.array([x[0] + x[1] - t[0],
                                                    x[0] + x[1] - t[0]]))
    s.append("  ∂ₓF tekil (iki denklem aynı) → "
             f"{ortuk_fonksiyon_turevi(tekil, np.array([0.5, 0.5]), [1.0])}")
    s.append("  (sayı uydurulmadı; şart sağlanmadığı bildirildi)")
    return "\n".join(s)



# ====================================================================
#  fitrat/tevafuk.py
# ====================================================================

def _pearson(u: np.ndarray, v: np.ndarray) -> float:
    """Sabit değişkende 0 döner — sıfıra bölmek yerine 'bağıntı yok'."""
    u = np.asarray(u, float); v = np.asarray(v, float)
    if u.size < 2:
        return 0.0
    du, dv = u - u.mean(), v - v.mean()
    payda = np.sqrt(float(du @ du) * float(dv @ dv))
    if payda < 1e-15:
        return 0.0
    return float(du @ dv / payda)


def sartli_bagintisi(dk: np.ndarray, dl: np.ndarray,
                     H: np.ndarray) -> float:
    """``ρ(d_k, d_l | H)`` — hüküm katmanlarında ağırlıklı ortalama.

    ``H`` ikili (0/1) olduğundan şartlı bağıntı, iki katmanda ayrı ayrı
    hesaplanıp katman büyüklüğüyle ağırlıklandırılır.  Bu, kısmî
    bağıntı (partial correlation) formülüne göre daha doğrudandır ve
    ``H``in ikili olduğu hâlde tam sonucu verir; kısmî bağıntı ise
    doğrusallık farz eder.

    Bir katmanda 2'den az örnek varsa o katman **atlanır** (ağırlığı
    sıfırdır); iki örnekten bağıntı uydurulmaz.
    """
    dk = np.asarray(dk, float); dl = np.asarray(dl, float)
    H = np.asarray(H)
    toplam, agirlik = 0.0, 0.0
    for h in (0, 1):
        m = H == h
        n = int(m.sum())
        if n < 3:
            continue
        toplam += n * _pearson(dk[m], dl[m])
        agirlik += n
    return toplam / agirlik if agirlik > 0 else 0.0


def cift_uyusmasi(dk: np.ndarray, dl: np.ndarray) -> float:
    """``a(d_k, d_l)`` — iki delil aynı yöne mi işaret ediyor?

    Ham Pearson bağıntısı kullanılır: ``+1`` tam uyuşma, ``−1`` tam
    zıtlık, ``0`` alâkasızlık.
    """
    return _pearson(dk, dl)


def tevafuk_olcusu(deliller: Sequence[np.ndarray], H: np.ndarray
                   ) -> Dict[str, object]:
    """Şartlı-bağımsızlıkla ağırlıklandırılmış tevâfuk.

    ``m < 2`` ise tevâfuk tanımsızdır (tek şahit kendisiyle tevâfuk
    etmez); ``None`` döner, sıfır değil — ikisi ayrı şeydir.
    """
    m = len(deliller)
    if m < 2:
        return {"tevafuk": None, "çift_sayısı": 0, "çiftler": [],
                "sebep": "en az iki delil lazım"}
    H = np.asarray(H)
    ciftler: List[Dict[str, float]] = []
    toplam = 0.0
    for k in range(m):
        for l in range(k + 1, m):           # k < l : her çift BİR kere
            a = cift_uyusmasi(deliller[k], deliller[l])
            rho = sartli_bagintisi(deliller[k], deliller[l], H)
            w = 1.0 - abs(rho)
            toplam += w * a
            ciftler.append({"k": k, "l": l, "uyuşma": a,
                            "artık_bağıntı": rho, "ağırlık": w,
                            "katkı": w * a})
    n_cift = m * (m - 1) // 2
    return {
        "tevafuk": toplam / n_cift,
        "ağırlıksız_tevafuk": sum(c["uyuşma"] for c in ciftler) / n_cift,
        "çift_sayısı": n_cift,
        "çiftler": ciftler,
    }


def log_olabilirlik_orani(d: np.ndarray, H: np.ndarray,
                          duzeltme: float = 0.5) -> float:
    """``ln Λ = ln[P(d=1|H)/P(d=1|¬H)]`` — ikili delil için.

    ``duzeltme`` Jeffreys düzeltmesidir (her hücreye ½): örneklem
    küçükken sıfır hücre ``ln 0 = −∞`` verir ve bir şahit tek başına
    hükmü kesinleştirir.  Düzeltme bunu engeller ve **taraf tutmaz**
    (her iki hücreye de aynı miktarda eklenir).
    """
    d = np.asarray(d).astype(int)
    H = np.asarray(H).astype(int)
    p1 = (float(np.sum(d[H == 1])) + duzeltme) / (float(np.sum(H == 1))
                                                  + 2 * duzeltme)
    p0 = (float(np.sum(d[H == 0])) + duzeltme) / (float(np.sum(H == 0))
                                                  + 2 * duzeltme)
    return float(np.log(p1 / p0))


def bayes_yigma(deliller: Sequence[np.ndarray], H: np.ndarray,
                onsel_oran: float = 1.0) -> Dict[str, object]:
    """Bağımsızlık farzıyla log-oranların toplanması."""
    lo = [log_olabilirlik_orani(d, H) for d in deliller]
    return {"log_Λ'lar": lo, "toplam": float(np.sum(lo)),
            "ardıl_log_oran": float(np.log(onsel_oran) + np.sum(lo))}


def fazla_sayma(deliller: Sequence[np.ndarray], H: np.ndarray
                ) -> Dict[str, object]:
    """Bağımsızlık farzı ne kadar fazla saydırıyor?

    Ölçüt: bütün delillerin toplamı ile, **birbiriyle en az bağıntılı**
    tek delilin katkısının karşılaştırılması değil — bu yanıltırdı.
    Bunun yerine tevâfuk ağırlıklarının ortalaması alınır: ağırlık 1'e
    ne kadar yakınsa yığma o kadar meşrudur.  Ağırlıklı toplam,
    fiilen "kaç bağımsız şahide denk geldiğini" verir.
    """
    t = tevafuk_olcusu(deliller, H)
    if t["tevafuk"] is None:
        return {"muteber_şahit_sayısı": float(len(deliller)),
                "sebep": t["sebep"]}
    y = bayes_yigma(deliller, H)
    ort_agirlik = float(np.mean([c["ağırlık"] for c in t["çiftler"]]))
    m = len(deliller)
    # m şahidin fiilî sayısı: tam bağımsızsa m, tam bağımlıysa 1.
    muteber = 1.0 + (m - 1.0) * ort_agirlik
    return {
        "şahit_sayısı": m,
        "ortalama_ağırlık": ort_agirlik,
        "muteber_şahit_sayısı": muteber,
        "ham_toplam_logΛ": y["toplam"],
        "düzeltilmiş_logΛ": y["toplam"] * muteber / m,
        "fazla_sayma_oranı": m / muteber if muteber > 0 else float("inf"),
    }


def sahit_uret(n: int, m: int, dogruluk: float, ortak_kaynak: float,
               tohum: int = 0) -> Tuple[np.ndarray, List[np.ndarray]]:
    """``m`` şahit üret; ``ortak_kaynak`` bağımlılığın şiddeti.

    Her şahit, olasılık ``dogruluk`` ile hükmü doğru bildirir.  Ayrıca
    ``ortak_kaynak`` olasılığıyla, kendi gözlemi yerine **ortak bir
    gürültü kaynağını** bildirir — bu, "hepsi aynı dedikoduyu duymuş"
    hâlidir ve şahitler arasında hüküm verildikten sonra da kalan bir
    bağıntı doğurur.

    ``ortak_kaynak = 0`` iken şahitler ``H`` verildiğinde şartlı
    bağımsızdır; ``1`` iken hepsi tek bir şahide iner.
    """
    r = np.random.default_rng(tohum)
    H = r.integers(0, 2, n)
    ortak = r.integers(0, 2, n)
    deliller = []
    for _ in range(m):
        kendi = np.where(r.random(n) < dogruluk, H, 1 - H)
        ortak_mi = r.random(n) < ortak_kaynak
        deliller.append(np.where(ortak_mi, ortak, kendi))
    return H, deliller


def _rapor_fitrat_tevafuk() -> str:
    s: List[str] = []
    n, m = 4000, 5

    s.append("=== Tevâfuk: bağımsız şahitler v ortak kaynaklı şahitler ===")
    s.append(f"  n={n} müşahede, m={m} şahit, her birinin doğruluğu 0.80")
    s.append("")
    s.append("  ortak_kaynak   tevafuk  ağırlıksız  ort.ağırlık"
             "  muteber şahit  fazla sayma")
    for ok in (0.0, 0.2, 0.5, 0.8, 1.0):
        H, D = sahit_uret(n, m, 0.80, ok, tohum=42)
        t = tevafuk_olcusu(D, H)
        f = fazla_sayma(D, H)
        s.append(f"    {ok:.1f}          {t['tevafuk']:+.4f}   "
                 f"{t['ağırlıksız_tevafuk']:+.4f}      "
                 f"{f['ortalama_ağırlık']:.4f}        "
                 f"{f['muteber_şahit_sayısı']:.3f}         "
                 f"{f['fazla_sayma_oranı']:.3f}")
    s.append("")
    s.append("  Ağırlıksız tevâfuk TEKDÜZE DEĞİL: önce düşüyor (0→0.2),")
    s.append("  sonra 1'e tırmanıyor. Sebebi ölçülebilir: az miktarda ortak")
    s.append("  kaynak, şahitlerin bir kısmını H ile alâkasız bir işarete")
    s.append("  çevirdiği için önce uyuşmayı SEYRELTİYOR; kaynak baskın")
    s.append("  hâle gelince ise şahitler birbirinin kopyası oluyor.")
    s.append("  Ağırlıklı ölçü ve muteber şahit sayısı ise tekdüze düşüyor —")
    s.append("  aranan da budur: ham uyuşma yanıltır, artık bağıntı yanıltmaz.")

    s.append("\n=== Bayes yığma fazla sayıyor mu? ===")
    for ok in (0.0, 0.8):
        H, D = sahit_uret(n, m, 0.80, ok, tohum=7)
        f = fazla_sayma(D, H)
        s.append(f"  ortak_kaynak={ok}: ham Σlog Λ = {f['ham_toplam_logΛ']:.4f}"
                 f"  düzeltilmiş = {f['düzeltilmiş_logΛ']:.4f}"
                 f"  (muteber {f['muteber_şahit_sayısı']:.2f}/{m} şahit)")

    s.append("\n=== Sınır hâlleri ===")
    H, D = sahit_uret(n, 1, 0.8, 0.0, tohum=1)
    s.append(f"  tek şahitte tevâfuk = {tevafuk_olcusu(D, H)['tevafuk']}"
             "   (sıfır değil — TANIMSIZ)")
    H, D = sahit_uret(n, 2, 0.8, 0.0, tohum=1)
    t = tevafuk_olcusu(D, H)
    s.append(f"  iki bağımsız şahit: çift sayısı = {t['çift_sayısı']}"
             f"  tevafuk = {t['tevafuk']:+.4f}")
    # Birbirinin tam zıddı iki şahit
    H2 = np.array([0, 1] * 500)
    d1 = H2.copy(); d2 = 1 - H2
    t2 = tevafuk_olcusu([d1, d2], H2)
    s.append(f"  tam zıt iki şahit: uyuşma = "
             f"{t2['çiftler'][0]['uyuşma']:+.1f}"
             f"  tevafuk = {t2['tevafuk']:+.4f}")
    return "\n".join(s)



# ====================================================================
#  fitrat/havuz.py
# ====================================================================

def logsumexp(a: Sequence[float]) -> float:
    """``ln Σ exp(a_i)`` — azamî terim dışarı alınarak.

    ``m = max a``; ``ln Σ e^{a_i} = m + ln Σ e^{a_i − m}``.  Üsler artık
    ``≤ 0`` olduğundan taşma imkânsız; en az bir terim tam olarak
    ``e^0 = 1`` olduğundan alttan taşma da toplamı sıfırlayamaz.
    Hepsi ``−inf`` ise netice ``−inf``tir (boş toplam değil, imkânsız
    hâl).
    """
    arr = [float(x) for x in a]
    if not arr:
        return float("-inf")
    m = max(arr)
    if m == float("-inf"):
        return float("-inf")
    return m + math.log(sum(math.exp(x - m) for x in arr))


def log_normalize(log_a: Sequence[float]) -> List[float]:
    """Log uzayında normalize: ``log_a − logsumexp(log_a)``."""
    z = logsumexp(log_a)
    if z == float("-inf"):
        raise ValueError("bütün hipotezler imkânsız — havuz çökmüş")
    return [float(x) - z for x in log_a]


class Hukum(Enum):
    KABUL = "kabul"
    RED = "red"
    KARANTINA = "karantina"


@dataclass
class Hipotez:
    """Bir izah adayı.

    ``log_olabilirlik(d)`` delilin bu hipotez altındaki log
    olasılığını verir.  ``iddiayi_dogrular``: bu izah doğruysa asıl
    iddia da doğru mu?
    """
    ad: str
    log_onsel: float
    log_olabilirlik: Callable[[object], float]
    iddiayi_dogrular: bool = False
    log_ardil: float = field(default=0.0, init=False)

    @property
    def ardil(self) -> float:
        return math.exp(self.log_ardil)


@dataclass
class Havuz:
    """Şüphe uzayı ve onun üzerindeki hüküm mekanizması.

    ``esik``: en yüksek hipotezin ardılı için asgarî değer.
    ``fark_esigi``: birinci ile ikinci arasındaki asgarî **log-oran**
    (nat cinsinden; ``ln 3 ≈ 1.1`` "üç katı" demektir).
    """
    hipotezler: List[Hipotez]
    esik: float = 0.7
    fark_esigi: float = math.log(3.0)
    tarih: List[Dict[str, object]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if len(self.hipotezler) < 2:
            raise ValueError("şüphe uzayı en az iki izah içermeli — "
                             "tek hipotezli havuz şüphe değil, kabuldür")
        if not 0.0 < self.esik <= 1.0:
            raise ValueError("eşik ∈ (0,1]")
        self._normalize()

    def _normalize(self) -> None:
        logs = log_normalize([h.log_onsel for h in self.hipotezler]
                             if not self.tarih
                             else [h.log_ardil for h in self.hipotezler])
        for h, l in zip(self.hipotezler, logs):
            h.log_ardil = l

    # --- güncelleme ---------------------------------------------------
    def delil_ekle(self, delil: object, etiket: str = "") -> Dict[str, object]:
        """Tek bir delille Bayes güncellemesi — hep log uzayında."""
        ham = [h.log_ardil + h.log_olabilirlik(delil)
               for h in self.hipotezler]
        if logsumexp(ham) == float("-inf"):
            raise ValueError(f"delil {etiket!r} bütün izahları imkânsız "
                             "kıldı — şüphe uzayı eksik kurulmuş")
        for h, l in zip(self.hipotezler, log_normalize(ham)):
            h.log_ardil = l
        kayit = {
            "delil": etiket or repr(delil),
            "ardıllar": {h.ad: h.ardil for h in self.hipotezler},
            "hüküm": self.hukum()[0].value,
        }
        self.tarih.append(kayit)
        return kayit

    def deliller_ekle(self, deliller: Sequence[object],
                      etiketler: Optional[Sequence[str]] = None
                      ) -> List[Dict[str, object]]:
        et = etiketler or [f"d{i}" for i in range(len(deliller))]
        return [self.delil_ekle(d, e) for d, e in zip(deliller, et)]

    # --- hüküm --------------------------------------------------------
    def siralama(self) -> List[Hipotez]:
        return sorted(self.hipotezler, key=lambda h: -h.log_ardil)

    def ayrisma(self) -> float:
        """Birinci ile ikinci arasındaki log-oran."""
        s = self.siralama()
        return s[0].log_ardil - s[1].log_ardil

    def hukum(self) -> Tuple[Hukum, Dict[str, object]]:
        """Kabul / red / karantina — iki şartın ikisi de aranır."""
        s = self.siralama()
        bas, ikinci = s[0], s[1]
        ayr = bas.log_ardil - ikinci.log_ardil
        gerekce = {
            "en_yüksek": bas.ad,
            "ardıl": bas.ardil,
            "ikinci": ikinci.ad,
            "ikincinin_ardılı": ikinci.ardil,
            "ayrışma_log_oranı": ayr,
            "eşik_sağlandı": bas.ardil >= self.esik,
            "ayrışma_sağlandı": ayr >= self.fark_esigi,
        }
        if not (gerekce["eşik_sağlandı"] and gerekce["ayrışma_sağlandı"]):
            return Hukum.KARANTINA, gerekce
        return (Hukum.KABUL if bas.iddiayi_dogrular else Hukum.RED), gerekce

    # --- şüphe uzayını genişletme ------------------------------------
    def izah_ekle(self, h: Hipotez, pay: float = 0.1) -> None:
        """Sonradan akla gelen bir izahı havuza al.

        Yeni izaha ihtimal kütlesinin ``pay`` kadarı verilir, kalanı
        mevcutlar arasında **oranları korunarak** paylaştırılır.  Böylece
        yeni bir ihtimalin akla gelmesi, eski deliller yeniden işlenmeden
        de hükmü gevşetebilir — ki doğrusu budur: şüphe uzayı eksikse
        varılan kesinlik sahtedir.
        """
        if not 0.0 < pay < 1.0:
            raise ValueError("pay ∈ (0,1)")
        kalan = math.log1p(-pay)
        for eski in self.hipotezler:
            eski.log_ardil += kalan
        h.log_ardil = math.log(pay)
        self.hipotezler.append(h)
        self.tarih.append({"delil": f"[yeni izah: {h.ad}]",
                           "ardıllar": {x.ad: x.ardil
                                        for x in self.hipotezler},
                           "hüküm": self.hukum()[0].value})

    def ozet(self) -> str:
        s = self.siralama()
        h, g = self.hukum()
        satir = [f"  {x.ad:24s} {x.ardil:.6f}" for x in s]
        satir.append(f"  → hüküm: {h.value.upper()}"
                     f"   (ardıl {g['ardıl']:.3f} eşik {self.esik},"
                     f" ayrışma {g['ayrışma_log_oranı']:.3f}"
                     f" eşik {self.fark_esigi:.3f})")
        return "\n".join(satir)


def _bernoulli(p: float) -> Callable[[object], float]:
    """``d=1`` iken ``ln p``, ``d=0`` iken ``ln(1−p)``."""
    lp, lq = math.log(p), math.log1p(-p)
    return lambda d: lp if d else lq


def _havuz_kur() -> Havuz:
    """İddia: 'şu âlet bozuk'. Üç izah."""
    return Havuz([
        Hipotez("âlet bozuk", math.log(0.2), _bernoulli(0.9), True),
        Hipotez("ölçen beceriksiz", math.log(0.3), _bernoulli(0.6), False),
        Hipotez("her şey yolunda", math.log(0.5), _bernoulli(0.1), False),
    ], esik=0.7, fark_esigi=math.log(3.0))


def _rapor_fitrat_havuz() -> str:
    s: List[str] = []

    s.append("=== Şüphe uzayı: 'âlet bozuk' iddiası ===")
    h = _havuz_kur()
    s.append("  başlangıç (önseller):")
    s.append(h.ozet())

    s.append("\n  deliller birer birer (1 = anormal okuma):")
    for i, d in enumerate([1, 1, 1, 1, 1]):
        k = h.delil_ekle(d, f"okuma{i+1}")
        bas = max(k["ardıllar"].items(), key=lambda t: t[1])
        s.append(f"    {k['delil']:9s} → en yüksek {bas[0]:18s}"
                 f" {bas[1]:.6f}   hüküm: {k['hüküm']}")
    s.append(h.ozet())

    s.append("\n=== Karantina: deliller ayrıştırmıyorsa ===")
    h2 = Havuz([
        Hipotez("A", math.log(0.5), _bernoulli(0.55), True),
        Hipotez("B", math.log(0.5), _bernoulli(0.45), False),
    ], esik=0.7, fark_esigi=math.log(3.0))
    h2.deliller_ekle([1, 1, 0, 1, 0, 1])
    s.append(h2.ozet())
    s.append("  → birinci sırada olmak hüküm için yetmiyor; ayrışma şart.")

    s.append("\n=== Yeni bir izah akla gelirse kesinlik gevşer ===")
    h3 = _havuz_kur()
    h3.deliller_ekle([1] * 6)
    hh, gg = h3.hukum()
    s.append(f"  altı delilden sonra: {hh.value}"
             f"  (ardıl {gg['ardıl']:.6f})")
    h3.izah_ekle(Hipotez("başka bir âlet karıştı", math.log(0.1),
                         _bernoulli(0.95), False), pay=0.35)
    hh2, gg2 = h3.hukum()
    s.append(f"  yeni izah eklenince: {hh2.value}"
             f"  (en yüksek {gg2['en_yüksek']} {gg2['ardıl']:.6f},"
             f" ayrışma {gg2['ayrışma_log_oranı']:.4f})")
    s.append("  → şüphe uzayı eksikken varılan kesinlik sahteydi.")

    s.append("\n=== Log uzayı olmasa ne olurdu? ===")
    hh4 = _havuz_kur()
    hh4.deliller_ekle([1] * 400)
    s.append(f"  400 delil sonrası ardıllar (log uzayında):"
             f" {[f'{x.ardil:.3e}' for x in hh4.siralama()]}")
    s.append("  aynı hesap ham çarpımla, hipotez hipotez:")
    for ad, onsel, p in (("âlet bozuk", 0.2, 0.9),
                         ("ölçen beceriksiz", 0.3, 0.6),
                         ("her şey yolunda", 0.5, 0.1)):
        ham = onsel * (p ** 400)
        s.append(f"    {ad:18s} {onsel}·{p}^400 = {ham:.3e}"
                 f"  {'← SIFIRA düştü' if ham == 0.0 else ''}")
    s.append("  n=400'de üç terimden yalnız BİRİ sıfırlandı; payda hâlâ")
    s.append("  sağlam. Ham çarpımın fiilen çöktüğü yeri arayalım —")
    s.append("  tahmin etmeyip ölçerek:")
    kirilma = None
    for n in range(100, 40001, 20):
        payda = 0.2 * 0.9 ** n + 0.3 * 0.6 ** n + 0.5 * 0.1 ** n
        if payda == 0.0:
            kirilma = n
            break
    s.append(f"    payda ilk defa n≈{kirilma} civarında sıfırlanıyor"
             f"  (0.2·0.9^{kirilma} = {0.2 * 0.9 ** kirilma:.3e})")
    s.append(f"    n={kirilma}'de log uzayındaki ardıl ise tam:")
    hh5 = _havuz_kur()
    hh5.deliller_ekle([1] * kirilma)
    s.append("      " + ", ".join(f"{x.ad}={x.ardil:.6e}"
                                  for x in hh5.siralama()))
    s.append("  Yani ham çarpım birkaç yüz delilde değil, birkaç binde")
    s.append("  çöküyor; ama çöktüğünde ardıl 0/0 = NaN oluyor ve hiçbir")
    s.append("  uyarı vermiyor. Log uzayında böyle bir sınır yok.")

    s.append("\n=== Sınır hâlleri ===")
    try:
        Havuz([Hipotez("tek", 0.0, _bernoulli(0.5), True)])
    except ValueError as e:
        s.append(f"  tek hipotezli havuz reddedildi: {e}")
    h5 = Havuz([Hipotez("A", math.log(0.5), lambda d: float("-inf"), True),
                Hipotez("B", math.log(0.5), lambda d: float("-inf"), False)])
    try:
        h5.delil_ekle(1, "imkânsız")
    except ValueError as e:
        s.append(f"  bütün izahları imkânsız kılan delil: {e}")
    return "\n".join(s)



# ====================================================================
#  Çipin toplu raporu
# ====================================================================
BOLUMLER = (
    ("AYRIŞMA -- Bayes-Ball, arka kapı, ön kapı", "_rapor_fitrat_ayrisma"),
    ("KARŞIOLGUSAL -- üç pas, NOTEARS, locus",
     "_rapor_fitrat_karsi_olgusal"),
    ("SERBEST ENERJİ -- F = −ELBO ≥ −ln p(x)",
     "_rapor_fitrat_serbest_enerji"),
    ("DENGE -- damped Newton, spektral yarıçap, IFT", "_rapor_fitrat_denge"),
    ("TEVÂFUK -- şartlı bağımsızlık, fazla sayma", "_rapor_fitrat_tevafuk"),
    ("HAVUZ -- şüphe uzayı ve karantina hükmü", "_rapor_fitrat_havuz"),
)


def rapor() -> str:                            # pragma: no cover
    """Beş odanın ölçümü, sırayla."""
    s = []
    for baslik, fn in BOLUMLER:
        s.append("")
        s.append("=" * 70)
        s.append("  " + baslik)
        s.append("=" * 70)
        s.append(globals()[fn]())
    return "\n".join(s)


if __name__ == "__main__":                     # pragma: no cover
    print(rapor())
