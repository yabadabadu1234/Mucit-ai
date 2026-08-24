"""İstikrâ — tümevarım, temsil (analoji) ve tam-olmayan çıkarım kipleri.

Bu modül *tümdengelim dışı* akıl yürütmeleri hesaplanabilir hâle getirir.
Her biri için ölçüt açıkça yazılır; hiçbiri "geçerli" diye damgalanmaz,
her birine bir **derece** biçilir ve derecenin nereden geldiği gösterilir.

Dört başlık:

1. **Laplace ardışıklık kaidesi** — n denemede k başarı görüldüğünde
   bir sonrakinin ihtimali.  Beta(α, β) önselinin ardıl beklentisi:

   .. math::  P(X_{n+1}=1 \\mid k, n) = \\frac{k+\\alpha}{n+\\alpha+\\beta}

   α=β=1 (düz önsel) hâlinde meşhur ``(k+1)/(n+2)`` çıkar.  Kaide
   **tam istikrâyı vermez**: n→∞ iken 1'e yaklaşır ama asla ulaşmaz;
   bu, "eksik istikrâ yakîn vermez" hükmünün nicel karşılığıdır.

2. **Değişmezlik yoluyla istikrâ (ICP tarzı)** — bir yordayıcı kümesi
   ancak *bütün ortamlarda* aynı ilişkiyi veriyorsa kabul edilir; kabul
   edilenlerin **kesişimi** alınır.  Kesişim boşsa hüküm verilmez.

3. **Temsil / analoji** — ``a`` ile ``b`` paylaşılan vasıflarda benzeşiyorsa
   ``a``nın hükmü ``b``ye taşınır.  Taşımanın gücü, *illetle alâkalı*
   vasıfların benzerliğidir; alâkasız vasıf benzerliği gücü artırmaz.

4. **Nyāya beş uzuvlu çıkarım** ve **Stoacı beş anapodeiktos** — klasik
   şemaların birebir tatbiki; ikincisi tümdengelimseldir ve
   :mod:`mizan.onerme` doğruluk tablosuyla *sağlaması yapılır*.
"""

from __future__ import annotations

import itertools
import math
from dataclasses import dataclass, field
from typing import (Callable, Dict, FrozenSet, Iterable, List, Optional,
                    Sequence, Set, Tuple)

from .onerme import Onerme, deg, degil, ise, ve, veya, gecerli_mi

__all__ = [
    "ardisiklik_kaidesi", "ardisiklik_dizisi", "tam_istikra_mi",
    "Ortam", "degismez_kumeler", "degismez_kesisim",
    "Nesne", "benzerlik", "temsil_gucu", "temsil_hukmu",
    "NyayaCikarim", "nyaya_degerlendir",
    "ANAPODEIKTOI", "anapodeiktos_dogrula", "butun_anapodeiktoslari_dogrula",
    "mill_uyusma", "mill_ayrilik", "mill_birlesik", "mill_esdegisim",
]


# ══════════════════════════════════════════════════════════════════════
#  1. Laplace ardışıklık kaidesi
# ══════════════════════════════════════════════════════════════════════

def ardisiklik_kaidesi(k: int, n: int, alfa: float = 1.0,
                       beta: float = 1.0) -> float:
    """``P(X_{n+1}=1 | k başarı / n deneme)`` — Beta(α,β) önseliyle.

    Türetme: önsel ``p ~ Beta(α,β)``, gözlem ``k ~ Binom(n,p)``.  Beta
    binom için eşlenik olduğundan ardıl ``Beta(k+α, n−k+β)``, onun da
    beklentisi ``(k+α)/(n+α+β)``.  Bir sonraki denemenin başarı ihtimali
    tam olarak bu beklentidir (Bernoulli'nin ortalaması parametresidir).

    ``α=β=1``: Laplace'ın ``(k+1)/(n+2)`` kaidesi.
    """
    if n < 0 or k < 0 or k > n:
        raise ValueError("0 ≤ k ≤ n olmalı")
    if alfa <= 0 or beta <= 0:
        raise ValueError("α, β > 0 olmalı")
    return (k + alfa) / (n + alfa + beta)


def ardisiklik_dizisi(n_azami: int, alfa: float = 1.0,
                      beta: float = 1.0) -> List[float]:
    """Hep-başarı hâlinde (k=n) ihtimalin n=0..n_azami boyunca seyri."""
    return [ardisiklik_kaidesi(n, n, alfa, beta)
            for n in range(n_azami + 1)]


def tam_istikra_mi(k: int, n: int, alfa: float = 1.0,
                   beta: float = 1.0) -> bool:
    """Eksik istikrâ hiçbir sonlu ``n`` için yakîn (=1) vermez.

    ``β > 0`` olduğu sürece ``(k+α)/(n+α+β) < 1``; ancak ``k=n`` ve
    ``β→0`` sınırında 1'e ulaşılır ki bu da "hiç aksi olamaz" demek olan
    bir önsel koymaktır — yani istikrâdan değil, önselden gelen yakîndir.
    """
    return ardisiklik_kaidesi(k, n, alfa, beta) >= 1.0


# ══════════════════════════════════════════════════════════════════════
#  2. Değişmezlik yoluyla istikrâ (ICP tarzı)
# ══════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class Ortam:
    """Bir gözlem ortamı: yordayıcı değerleri ve netice.

    ``X``: her satır bir müşahede, her sütun bir yordayıcı.
    ``y``: aynı uzunlukta netice dizisi.
    """
    ad: str
    X: Tuple[Tuple[float, ...], ...]
    y: Tuple[float, ...]

    def __post_init__(self) -> None:
        if len(self.X) != len(self.y):
            raise ValueError("X satır sayısı y ile uyuşmuyor")


def _en_kucuk_kareler(X: Sequence[Sequence[float]],
                      y: Sequence[float],
                      sutunlar: Sequence[int]) -> Tuple[List[float], float]:
    """Seçili sütunlarla sabit terimli EKK; (katsayılar, artık varyansı).

    Normal denklemler ``(AᵀA)β = Aᵀy`` Gauss eliminasyonuyla çözülür.
    Tekil hâlde küçük bir Tikhonov terimi (1e-12) eklenir — bu yalnız
    sayısal tekilliği açar, kat sayıları maddî olarak değiştirmez.
    """
    m = len(y)
    p = len(sutunlar) + 1
    A = [[1.0] + [X[i][j] for j in sutunlar] for i in range(m)]
    G = [[sum(A[i][r] * A[i][c] for i in range(m)) for c in range(p)]
         for r in range(p)]
    b = [sum(A[i][r] * y[i] for i in range(m)) for r in range(p)]
    for r in range(p):
        G[r][r] += 1e-12
    # Gauss — kısmî pivotlama
    for c in range(p):
        piv = max(range(c, p), key=lambda r: abs(G[r][c]))
        if abs(G[piv][c]) < 1e-14:
            continue
        G[c], G[piv] = G[piv], G[c]
        b[c], b[piv] = b[piv], b[c]
        for r in range(p):
            if r == c:
                continue
            f = G[r][c] / G[c][c]
            if f:
                for k in range(c, p):
                    G[r][k] -= f * G[c][k]
                b[r] -= f * b[c]
    beta = [b[r] / G[r][r] if abs(G[r][r]) > 1e-14 else 0.0 for r in range(p)]
    artik = [y[i] - sum(beta[r] * A[i][r] for r in range(p)) for i in range(m)]
    var = sum(e * e for e in artik) / max(1, m - p)
    return beta, var


def _kabul_mu(ortamlar: Sequence[Ortam], sutunlar: Sequence[int],
              tolerans: float) -> bool:
    """Bu yordayıcı kümesi BÜTÜN ortamlarda aynı ilişkiyi mi veriyor?

    Ölçüt: ortamların birleşiminde uydurulan katsayılarla her ortamın
    artıkları, o ortamın kendi içinde uydurulmuş artıklarından belirgin
    biçimde kötü olmamalı.  ``tolerans`` bağıl bir eşiktir.
    """
    hepsi_X = tuple(itertools.chain.from_iterable(o.X for o in ortamlar))
    hepsi_y = tuple(itertools.chain.from_iterable(o.y for o in ortamlar))
    beta, _ = _en_kucuk_kareler(hepsi_X, hepsi_y, sutunlar)
    for o in ortamlar:
        _, kendi_var = _en_kucuk_kareler(o.X, o.y, sutunlar)
        artik = []
        for i in range(len(o.y)):
            satir = [1.0] + [o.X[i][j] for j in sutunlar]
            artik.append(o.y[i] - sum(beta[r] * satir[r]
                                      for r in range(len(beta))))
        ortak_var = sum(e * e for e in artik) / max(1, len(artik))
        if ortak_var > (kendi_var + 1e-9) * (1.0 + tolerans):
            return False
    return True


def degismez_kumeler(ortamlar: Sequence[Ortam], n_yordayici: int,
                     tolerans: float = 0.5) -> List[FrozenSet[int]]:
    """Bütün ortamlarda değişmez kalan yordayıcı kümelerinin listesi."""
    kabul: List[FrozenSet[int]] = []
    for r in range(n_yordayici + 1):
        for alt in itertools.combinations(range(n_yordayici), r):
            if _kabul_mu(ortamlar, alt, tolerans):
                kabul.append(frozenset(alt))
    return kabul


def degismez_kesisim(ortamlar: Sequence[Ortam], n_yordayici: int,
                     tolerans: float = 0.5) -> FrozenSet[int]:
    """Kabul edilen kümelerin **kesişimi** — ICP'nin verdiği hüküm.

    Kesişim boşsa hiçbir yordayıcı hakkında hüküm verilmez.  Bu bir
    kusur değil, usulün kendisidir: değişmezlik delili yoksa illet
    isnadı da yoktur.
    """
    kabul = degismez_kumeler(ortamlar, n_yordayici, tolerans)
    if not kabul:
        return frozenset()
    kesisim = set(kabul[0])
    for k in kabul[1:]:
        kesisim &= k
    return frozenset(kesisim)


# ══════════════════════════════════════════════════════════════════════
#  3. Temsil (analoji)
# ══════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class Nesne:
    ad: str
    vasiflar: FrozenSet[str]


def benzerlik(a: Nesne, b: Nesne) -> float:
    """Jaccard: ``|A∩B| / |A∪B|``.  Boş-boş hâlinde 1 (ikisi de aynı)."""
    birlesim = a.vasiflar | b.vasiflar
    if not birlesim:
        return 1.0
    return len(a.vasiflar & b.vasiflar) / len(birlesim)


def temsil_gucu(a: Nesne, b: Nesne, illet_vasiflari: Iterable[str]) -> float:
    """Analojinin gücü = **illetle alâkalı** vasıflardaki uyuşma oranı.

    Ölçüt kasten yalnız ``illet_vasiflari`` üzerinden hesaplanır: alâkasız
    vasıflarda benzeşmek analojiyi kuvvetlendirmez.  Uyuşma, her illet
    vasfı için "ikisinde de var" veya "ikisinde de yok" hâlleridir —
    yani vasfın müşterek *değeri*, sadece müşterek varlığı değil.
    """
    illet = list(dict.fromkeys(illet_vasiflari))
    if not illet:
        return 0.0
    uyan = sum(1 for v in illet
               if (v in a.vasiflar) == (v in b.vasiflar))
    return uyan / len(illet)


def temsil_hukmu(asil: Nesne, fer: Nesne, illet_vasiflari: Iterable[str],
                 asil_hukmu: bool, esik: float = 1.0
                 ) -> Tuple[Optional[bool], float]:
    """Asıldaki hükmü fer'e taşı — ancak illet tam intibak ederse.

    Dönen: ``(hüküm veya None, güç)``.  Güç eşiğin altındaysa hüküm
    **verilmez** (``None``); klasik usulde de illetin fer'de tahakkuku
    şart koşulur, kısmî benzerlik hüküm doğurmaz.
    """
    g = temsil_gucu(asil, fer, illet_vasiflari)
    return (asil_hukmu if g >= esik else None), g


# ══════════════════════════════════════════════════════════════════════
#  4a. Nyāya beş uzuvlu çıkarım
# ══════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class NyayaCikarim:
    """pratijñā / hetu / udāharaṇa / upanaya / nigamana.

    ``sapaksa``: hetu'nun da sādhya'nın da bulunduğu müsbet misaller.
    ``vipaksa``: sādhya'nın bulunmadığı menfî misaller — hetu bunların
    **hiçbirinde** bulunmamalıdır (vyatireka).
    """
    paksa: str            # mevzu ("şu dağ")
    sadhya: str           # isbat edilecek ("ateş var")
    hetu: str             # delil ("duman var")
    sapaksa: FrozenSet[str]
    vipaksa: FrozenSet[str]
    hetu_paksada: bool = True
    hetunun_bulundugu: FrozenSet[str] = frozenset()


def nyaya_degerlendir(c: NyayaCikarim) -> Dict[str, object]:
    """Hetu'nun beş şartını (pañca-rūpa) tek tek dener.

    1. pakṣadharmatā — hetu mevzuda bulunmalı.
    2. sapakṣa-sattva — hetu en az bir müsbet misalde bulunmalı.
    3. vipakṣa-asattva — hetu hiçbir menfî misalde bulunmamalı.
    4. abādhita — netice başka bir kat'î delille çürütülmemiş olmalı.
    5. asatpratipakṣa — eşit kuvvette bir karşı-delil bulunmamalı.

    4 ve 5 dışsal şartlardır; burada girdi olarak alınır, uydurulmaz.
    Hüküm ancak ilk üçü sağlanınca verilir.
    """
    s1 = c.hetu_paksada
    s2 = bool(c.sapaksa & c.hetunun_bulundugu) or (
        not c.hetunun_bulundugu and bool(c.sapaksa))
    s3 = not (c.vipaksa & c.hetunun_bulundugu)
    hata: Optional[str] = None
    if not s1:
        hata = "asiddha (hetu mevzuda yok)"
    elif not s3:
        hata = "savyabhicāra (hetu menfî misalde de var — ıttırad bozuk)"
    elif not s2:
        hata = "sapakṣa'da müsbet misal yok"
    return {
        "pakṣadharmatā": s1,
        "sapakṣa_sattva": s2,
        "vipakṣa_asattva": s3,
        "geçerli": bool(s1 and s2 and s3),
        "hata": hata,
        "nigamana": (f"{c.paksa}: {c.sadhya}" if (s1 and s2 and s3) else None),
    }


# ══════════════════════════════════════════════════════════════════════
#  4b. Stoacı beş anapodeiktos — tümdengelimsel, sağlaması yapılır
# ══════════════════════════════════════════════════════════════════════

def _stoa_semalari() -> List[Tuple[str, List[Onerme], Onerme]]:
    A, B = deg("A"), deg("B")
    return [
        ("1. modus ponens        : A→B, A ⊢ B",
         [ise(A, B), A], B),
        ("2. modus tollens       : A→B, ¬B ⊢ ¬A",
         [ise(A, B), degil(B)], degil(A)),
        ("3. bağdaşmazlık        : ¬(A∧B), A ⊢ ¬B",
         [degil(ve(A, B)), A], degil(B)),
        ("4. ayırıcı (tam)       : A⊻B, A ⊢ ¬B",
         [ve(veya(A, B), degil(ve(A, B))), A], degil(B)),
        ("5. ayırıcı (kalan)     : A⊻B, ¬A ⊢ B",
         [ve(veya(A, B), degil(ve(A, B))), degil(A)], B),
    ]


ANAPODEIKTOI: List[Tuple[str, List[Onerme], Onerme]] = _stoa_semalari()


def anapodeiktos_dogrula(oncul: Sequence[Onerme], netice: Onerme) -> bool:
    """Şemayı doğruluk tablosuyla dene — iddia değil, ölçüm."""
    return gecerli_mi(list(oncul), netice)


def butun_anapodeiktoslari_dogrula() -> List[Tuple[str, bool]]:
    return [(ad, anapodeiktos_dogrula(o, n)) for ad, o, n in ANAPODEIKTOI]


# ══════════════════════════════════════════════════════════════════════
#  5. Mill'in usulleri — illet arayışının hesaplanabilir hâli
# ══════════════════════════════════════════════════════════════════════

Vaka = Tuple[FrozenSet[str], bool]   # (mevcut âmiller, netice oldu mu)


def mill_uyusma(vakalar: Sequence[Vaka]) -> FrozenSet[str]:
    """Uyuşma usulü: neticenin olduğu BÜTÜN vakalarda ortak olan âmiller."""
    musbet = [a for a, n in vakalar if n]
    if not musbet:
        return frozenset()
    ortak = set(musbet[0])
    for a in musbet[1:]:
        ortak &= a
    return frozenset(ortak)


def mill_ayrilik(vakalar: Sequence[Vaka]) -> FrozenSet[str]:
    """Ayrılık usulü: neticenin OLMADIĞI hiçbir vakada bulunmayan âmiller.

    Uyuşmadan farkı: burada eleme menfî vakalarla yapılır.  Netice
    yokken de bulunan bir âmil illet olamaz.
    """
    menfi_birlesim: Set[str] = set()
    for a, n in vakalar:
        if not n:
            menfi_birlesim |= a
    musbet_birlesim: Set[str] = set()
    for a, n in vakalar:
        if n:
            musbet_birlesim |= a
    return frozenset(musbet_birlesim - menfi_birlesim)


def mill_birlesik(vakalar: Sequence[Vaka]) -> FrozenSet[str]:
    """Birleşik usul: hem her müsbette var, hem hiçbir menfîde yok."""
    return mill_uyusma(vakalar) & mill_ayrilik(vakalar)


def mill_esdegisim(olcumler: Sequence[Tuple[float, float]]) -> float:
    """Eş değişim usulü: Pearson bağıntı katsayısı.

    Sıfıra bölünmeyi önlemek için değişkenlerden biri sabitse 0 döner —
    "birlikte değişme yok" hükmü, uydurma bir sayı değil.
    """
    n = len(olcumler)
    if n < 2:
        return 0.0
    mx = sum(x for x, _ in olcumler) / n
    my = sum(y for _, y in olcumler) / n
    sxy = sum((x - mx) * (y - my) for x, y in olcumler)
    sxx = sum((x - mx) ** 2 for x, _ in olcumler)
    syy = sum((y - my) ** 2 for _, y in olcumler)
    if sxx < 1e-15 or syy < 1e-15:
        return 0.0
    return sxy / math.sqrt(sxx * syy)


# ══════════════════════════════════════════════════════════════════════
#  Gösterim
# ══════════════════════════════════════════════════════════════════════

def _gosterim() -> str:
    s: List[str] = []
    s.append("=== Laplace ardışıklık kaidesi (hep başarı) ===")
    d = ardisiklik_dizisi(10)
    s.append("  n :  " + "  ".join(f"{n:5d}" for n in range(11)))
    s.append("  P :  " + "  ".join(f"{p:.3f}" for p in d))
    s.append(f"  n=1000 → {ardisiklik_kaidesi(1000, 1000):.6f}"
             f"   yakîn mi? {tam_istikra_mi(1000, 1000)}")

    s.append("\n=== Değişmezlik yoluyla istikrâ ===")
    # X0 hakiki illet (y = 2·X0 her ortamda); X1 sahte: 1. ortamda y ile
    # aynı yönde, 2.'de ters yönde gider.  Ortamlar ayrıca y aralığında da
    # ayrışır — ayrışmasalardı boş küme de kabul edilirdi ve ölçüt hiçbir
    # şeyi elemezdi (ICP'nin gücü ortam farkından gelir).
    o1 = Ortam("ortam-1",
               tuple((float(i), float(i)) for i in range(8)),
               tuple(2.0 * i for i in range(8)))
    o2 = Ortam("ortam-2",
               tuple((float(i), float(-i)) for i in range(10, 18)),
               tuple(2.0 * i for i in range(10, 18)))
    kabul = degismez_kumeler([o1, o2], 2)
    s.append("  kabul edilen kümeler: "
             + ", ".join("{" + ",".join(f"X{j}" for j in sorted(k)) + "}"
                         if k else "{}" for k in kabul))
    kes = degismez_kesisim([o1, o2], 2)
    s.append("  kesişim (hüküm): "
             + ("{" + ",".join(f"X{j}" for j in sorted(kes)) + "}"
                if kes else "boş — hüküm verilmez"))

    s.append("\n=== Temsil (analoji) ===")
    hamr = Nesne("şarap", frozenset({"üzümden", "sıvı", "sarhoş_edici", "kırmızı"}))
    nbz = Nesne("nebîz", frozenset({"hurmadan", "sıvı", "sarhoş_edici"}))
    sirke = Nesne("sirke", frozenset({"üzümden", "sıvı", "kırmızı"}))
    for fer in (nbz, sirke):
        h, g = temsil_hukmu(hamr, fer, ["sarhoş_edici"], True)
        s.append(f"  {fer.ad:6s} illet gücü={g:.2f}  hüküm={h}"
                 f"   (kaba benzerlik={benzerlik(hamr, fer):.2f})")
    s.append("  dikkat: sirke şaraba KABA benzerlikte daha yakın olabilir,"
             " illette değil.")

    s.append("\n=== Nyāya beş uzuv ===")
    iyi = NyayaCikarim("dağ", "ateş var", "duman var",
                       frozenset({"mutfak"}), frozenset({"göl"}),
                       True, frozenset({"mutfak"}))
    kotu = NyayaCikarim("dağ", "ateş var", "hava var",
                        frozenset({"mutfak"}), frozenset({"göl"}),
                        True, frozenset({"mutfak", "göl"}))
    for ad, c in (("sahih", iyi), ("savyabhicāra", kotu)):
        r = nyaya_degerlendir(c)
        s.append(f"  {ad:14s} geçerli={r['geçerli']}  hata={r['hata']}")

    s.append("\n=== Stoacı beş anapodeiktos (tablo sağlaması) ===")
    for ad, ok in butun_anapodeiktoslari_dogrula():
        s.append(f"  {ad:38s} {ok}")

    s.append("\n=== Mill usulleri ===")
    vakalar: List[Vaka] = [
        (frozenset({"a", "b", "c"}), True),
        (frozenset({"a", "d", "e"}), True),
        (frozenset({"b", "d", "f"}), False),
        (frozenset({"c", "e", "f"}), False),
    ]
    s.append(f"  uyuşma  = {sorted(mill_uyusma(vakalar))}")
    s.append(f"  ayrılık = {sorted(mill_ayrilik(vakalar))}")
    s.append(f"  birleşik= {sorted(mill_birlesik(vakalar))}")
    s.append("  eş değişim r = "
             f"{mill_esdegisim([(1,2),(2,4),(3,6),(4,8)]):.3f}"
             "  (sabit değişkende) "
             f"{mill_esdegisim([(1,5),(2,5),(3,5)]):.3f}")
    return "\n".join(s)


if __name__ == "__main__":
    print(_gosterim())
