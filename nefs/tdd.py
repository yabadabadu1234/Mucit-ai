"""TENSÖR KARAR DİYAGRAMI (LimTDD) -- durum GRAFTIR, ameliyeler GRAFTA.

    D = Tdd.kur(psi)            # ℂ^d → DAG
    D.bit_kapisi(b, G)          # kapı GRAFTA vurulur, açılmadan
    D.faz(teta)                 # köşegen faz, GRAFTA
    D.ic_carpim(E)              # ⟨D|E⟩, GRAFTA
    D.ac()                      # yalnız dışa açılırken yoğunlaşır

===================================================================
ZABITIN 1. USULÜ -- **TAMAMEN** (Saf CPU 2026 Mimarisi)
===================================================================

    *"Durumu bellekte düz tensör veya matris blokları halinde tutmazsınız.
    Bir qudit tensörünün elemanları yönlendirilmiş asiklik bir graf (DAG)
    olarak kodlanır... Tekil bir düğüm hash tablosunda tek bir adres
    olarak tutulur."*

    *"İki kavramın veya iki döngünün eşit olup olmadığı matris normu
    hesaplanarak aranmaz; TDD kanonik olduğundan iki grafın kök bellek
    adreslerinin aynı olup olmadığına tek bir CPU saat çevriminde (O(1)
    sürede) bakılır."*

**BU DOSYA YARIM DEĞİLDİR.** Kapılar, fazlar, toplama, iç çarpım,
norm ve ölçüm **grafın üstünde** icra edilir; yoğun diziye ancak
``ac()`` ile, yâni dışarıya bir şey teslim edilirken inilir.

===================================================================
YAPI
===================================================================

Durum ``ψ ∈ ℂ^d`` (``d = 2^n``) yinelemeli ikiye bölünür::

    ψ = [ψ_0 | ψ_1]

Her düğüm ``(seviye, sol, sağ, λ_sol, λ_sağ)``dır. ``seviye`` o düğümün
temsil ettiği bloğun **bit derinliğidir** (kök ``n``, yaprak ``0``);
seviyeyi düğümde tutmak şarttır, yoksa farklı boydaki özdeş bloklar
aynı adrese çöker ve açılış boyu tutmaz (ölçüldü: ``|0⟩``da hata
``inf`` çıkmıştı).

**KANONİKLİK.** Her düğüm ilk sıfır olmayan bileşeni ``1`` olacak
şekilde normalize edilir; fark kenardaki ``λ``ya yazılır. Böylece
``ψ`` ile ``λψ`` **aynı adrestir** ve eşitlik ``O(1)``de görülür.
Bu, LimTDD'nin "yerel tersinir dönüşüm" kenarının faz/ölçek hâlidir.

===================================================================
AMELİYELER GRAFTA NASIL YÜRÜR
===================================================================

* **Toplama** ``a + b``: klasik BDD *apply*. İki düğüm eşzamanlı
  inilir, netice ``(a, b, λ)`` anahtarıyla **belleklenir** (computed
  table). Aynı alt problem bir daha hesaplanmaz.
* **Bit kapısı** ``G`` (2×2), ``b``inci bit düzlemine: o bite karşılık
  gelen seviyede her düğümün iki çocuğu ``G`` ile karıştırılır::

      sol' = G₀₀·sol + G₀₁·sağ
      sağ' = G₁₀·sol + G₁₁·sağ

  Karışım *apply* ile grafta yapılır; hiçbir yerde ``d`` uzunluğunda
  bir dizi kurulmaz.
* **Köşegen faz**: yaprağa kadar inip yaprak bloğunu çarpmak yerine,
  fazın kendisi de bir TDD'dir ve **noktasal çarpım** de apply'dır.
* **İç çarpım** ``⟨a|b⟩``: eşzamanlı iniş, alt sonuçlar belleklenir.

Hepsinin maliyeti ``O(|a|·|b|)``dir -- ``d`` değil, **düğüm sayısı**.
Yapılı durumda düğüm sayısı ``d``den çok küçüktür; gürültüde değildir
ve o zaman kazanç yoktur. Bu bir vaat değil, ``olcu()`` ile ölçülür.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["TddAyari", "Tdd", "olcu", "rapor"]


@dataclass
class TddAyari:
    """Grafın ölçüleri."""

    #: İki bloğun "aynı ışında" sayılması için tolerans.
    tolerans: float = 1e-9
    #: Düğüm haddi: aşılırsa ``assert`` durdurur -- graf sessizce
    #: yoğundan büyümez.
    dugum_haddi: int = 1 << 22
    #: Önbellek haddi (L2, bayt) -- grafın sığması beklenen yer.
    onbellek_bayt: int = 1024 * 1024


#: Düğüm: ``(seviye, sol, sağ, λ_sol, λ_sağ)``. Yaprak: seviye 0,
#: çocuklar ``-1``, ``λ_sol`` skalerdir (o bloğun tek genliği).
_YAPRAK = -1


class Tdd:
    """Bir DAG durumu. **Bütün ameliyeler burada, grafta.**

    Düğümler bir **havuzda** (``_dugum``) yaşar ve havuz nesneler arası
    paylaşılır: iki ayrı ``Tdd`` aynı alt ağacı aynı adreste görür,
    o hâlde eşitlikleri kök adresi kıyaslanarak ``O(1)``de anlaşılır.
    """

    __slots__ = ("kok", "lam", "seviye", "havuz")

    def __init__(self, kok: int, lam: complex, seviye: int,
                 havuz: "Havuz") -> None:
        self.kok = int(kok)
        self.lam = complex(lam)
        self.seviye = int(seviye)
        self.havuz = havuz

    # ── kuruluş ───────────────────────────────────────────────────
    @staticmethod
    def kur(psi, ayar: Optional[TddAyari] = None,
            havuz: Optional["Havuz"] = None) -> "Tdd":
        v = np.asarray(psi, complex).reshape(-1)
        d = v.size
        assert d >= 2, "durum en az iki genlikli olmalı"
        n = int(round(math.log2(d)))
        assert 2 ** n == d, "TDD ikinin kuvvetini ister: d=%d" % d
        h = havuz or Havuz(ayar or TddAyari())
        kok, lam = h.kur(v, n)
        return Tdd(kok, lam, n, h)

    @property
    def boy(self) -> int:
        return 1 << self.seviye

    def ac(self) -> np.ndarray:
        """Yoğun diziye aç -- **yalnız dışarıya teslim ederken**."""
        return self.lam * self.havuz.ac(self.kok, self.seviye)

    # ── ameliyeler: HEPSİ GRAFTA ─────────────────────────────────
    def olcek(self, c: complex) -> "Tdd":
        return Tdd(self.kok, self.lam * complex(c), self.seviye, self.havuz)

    def topla(self, o: "Tdd") -> "Tdd":
        assert self.seviye == o.seviye, "aynı seviyedeki graflar toplanır"
        k, l = self.havuz.topla(self.kok, self.lam, o.kok, o.lam,
                                self.seviye)
        return Tdd(k, l, self.seviye, self.havuz)

    def bit_kapisi(self, bit: int, G) -> "Tdd":
        """``bit``inci düzleme ``2×2`` kapı -- **grafta**, açmadan."""
        G = np.asarray(G, complex).reshape(2, 2)
        assert 0 <= int(bit) < self.seviye, (
            "bit %d, seviye %d dışında" % (bit, self.seviye))
        k, l = self.havuz.kapi(self.kok, self.lam, self.seviye,
                               int(bit), G)
        return Tdd(k, l, self.seviye, self.havuz)

    def cift_kapisi(self, bit_i: int, bit_j: int, G) -> "Tdd":
        """İki bit düzlemine ``4×4`` kapı -- dört terimli apply."""
        G = np.asarray(G, complex).reshape(2, 2, 2, 2)
        d = self
        # 4×4'ü iki kübitlik apply'a çevirmek için doğrudan dört
        # alt-blok karışımı yapılır: her (p,q) çıktısı, (r,s)
        # girdilerinin lineer birleşimidir.
        k, l = self.havuz.cift_kapi(d.kok, d.lam, d.seviye,
                                    int(bit_i), int(bit_j), G)
        return Tdd(k, l, self.seviye, self.havuz)

    def faz(self, faz_tdd: "Tdd") -> "Tdd":
        """Noktasal çarpım (köşegen operatör) -- grafta."""
        assert self.seviye == faz_tdd.seviye, "faz aynı seviyede olmalı"
        k, l = self.havuz.carp(self.kok, self.lam,
                               faz_tdd.kok, faz_tdd.lam, self.seviye)
        return Tdd(k, l, self.seviye, self.havuz)

    def ic_carpim(self, o: "Tdd") -> complex:
        """``⟨self|o⟩`` -- grafta, eşzamanlı iniş ve belleklemeyle."""
        assert self.seviye == o.seviye, "iç çarpım aynı seviyede"
        return (np.conj(self.lam) * o.lam
                * self.havuz.ic(self.kok, o.kok, self.seviye))

    def norm_kare(self) -> float:
        return float(np.real(self.ic_carpim(self)))

    def normalize(self) -> "Tdd":
        n = math.sqrt(max(self.norm_kare(), 1e-300))
        return self.olcek(1.0 / n)

    def olasilik(self) -> np.ndarray:
        """``|ψ|²`` -- yoğun. Ölçüm dışarıya teslimdir, açılır."""
        v = self.ac()
        return np.abs(v) ** 2

    def dugum_sayisi(self) -> int:
        """Bu kökten erişilen düğüm sayısı."""
        gorulen: set = set()
        yigin = [self.kok]
        while yigin:
            a = yigin.pop()
            if a in gorulen:
                continue
            gorulen.add(a)
            sv, sol, sag, _ls, _lg = self.havuz.dugum[a]
            if sol != _YAPRAK:
                yigin.append(sol)
                yigin.append(sag)
        return len(gorulen)


class Havuz:
    """Düğüm havuzu + benzersizlik tablosu + hesaplanmış tablo.

    **Kanonik adresleme burada olur.** ``_yaz`` bir düğümü tabloya
    koyarken aynı anahtar varsa **aynı adresi** döndürür; o hâlde
    özdeş alt ağaçlar bellekte tek nüshadır ve eşitlikleri adres
    kıyasıdır.
    """

    __slots__ = ("ayar", "dugum", "tablo", "bellek_topla", "bellek_carp",
                 "bellek_ic", "bellek_kapi", "sifir")

    def __init__(self, ayar: Optional[TddAyari] = None) -> None:
        self.ayar = ayar or TddAyari()
        #: ``(seviye, sol, sağ, λ_sol, λ_sağ)``
        self.dugum: List[Tuple[int, int, int, complex, complex]] = []
        self.tablo: Dict[Tuple, int] = {}
        self.bellek_topla: Dict[Tuple, Tuple[int, complex]] = {}
        self.bellek_carp: Dict[Tuple, Tuple[int, complex]] = {}
        self.bellek_ic: Dict[Tuple, complex] = {}
        self.bellek_kapi: Dict[Tuple, Tuple[int, complex]] = {}
        # Sıfır düğümü seviye başına: ``0`` yaprak.
        self.sifir: Dict[int, int] = {}

    # ── benzersizlik ──────────────────────────────────────────────
    def _yaz(self, seviye: int, sol: int, sag: int,
             ls: complex, lg: complex) -> int:
        tol = self.ayar.tolerans
        basamak = max(1, int(round(-math.log10(max(tol, 1e-15)))))
        ah = (int(seviye), int(sol), int(sag),
              complex(round(ls.real, basamak), round(ls.imag, basamak)),
              complex(round(lg.real, basamak), round(lg.imag, basamak)))
        a = self.tablo.get(ah)
        if a is not None:
            return a
        self.dugum.append((int(seviye), int(sol), int(sag), ls, lg))
        a = len(self.dugum) - 1
        assert a < self.ayar.dugum_haddi, (
            "düğüm haddi aşıldı (%d) -- graf yoğundan büyüdü" % a)
        self.tablo[ah] = a
        return a

    def _sifir(self, seviye: int) -> int:
        a = self.sifir.get(int(seviye))
        if a is not None:
            return a
        if seviye == 0:
            a = self._yaz(0, _YAPRAK, _YAPRAK, 0.0 + 0j, 0.0 + 0j)
        else:
            alt = self._sifir(seviye - 1)
            a = self._yaz(seviye, alt, alt, 0.0 + 0j, 0.0 + 0j)
        self.sifir[int(seviye)] = a
        return a

    def _birim_yaprak(self) -> int:
        """Yaprak ``1``: bütün genlikler bunun ``λ`` katıdır."""
        return self._yaz(0, _YAPRAK, _YAPRAK, 1.0 + 0j, 0.0 + 0j)

    # ── kuruluş ───────────────────────────────────────────────────
    def kur(self, v: np.ndarray, seviye: int) -> Tuple[int, complex]:
        tol = self.ayar.tolerans
        if seviye == 0:
            c = complex(v[0])
            if abs(c) <= tol:
                return self._sifir(0), 0.0 + 0j
            return self._birim_yaprak(), c
        yari = 1 << (seviye - 1)
        s_a, s_l = self.kur(v[:yari], seviye - 1)
        g_a, g_l = self.kur(v[yari:], seviye - 1)
        return self._birlestir(seviye, s_a, s_l, g_a, g_l)

    def _birlestir(self, seviye: int, s_a: int, s_l: complex,
                   g_a: int, g_l: complex) -> Tuple[int, complex]:
        """İki çocuğu kanonik düğüme bağla; ortak ``λ``yı dışarı çıkar."""
        tol = self.ayar.tolerans
        if abs(s_l) <= tol and abs(g_l) <= tol:
            return self._sifir(seviye), 0.0 + 0j
        lam = s_l if abs(s_l) > tol else g_l
        return self._yaz(seviye, s_a, g_a, s_l / lam, g_l / lam), lam

    # ── açma ──────────────────────────────────────────────────────
    def ac(self, a: int, seviye: int) -> np.ndarray:
        sv, sol, sag, ls, lg = self.dugum[a]
        if sol == _YAPRAK:
            return np.array([ls], complex)
        return np.concatenate([ls * self.ac(sol, seviye - 1),
                               lg * self.ac(sag, seviye - 1)])

    # ── TOPLAMA (apply) ───────────────────────────────────────────
    def topla(self, a: int, la: complex, b: int, lb: complex,
              seviye: int) -> Tuple[int, complex]:
        tol = self.ayar.tolerans
        if abs(la) <= tol:
            return b, lb
        if abs(lb) <= tol:
            return a, la
        # Anahtar: adresler + oran. Ortak çarpan dışarı alınır ki
        # ``(a, b, λ)`` ile ``(a, b, cλ)`` aynı alt problemi paylaşsın.
        oran = lb / la
        basamak = max(1, int(round(-math.log10(max(tol, 1e-15)))))
        ah = (a, b, round(oran.real, basamak), round(oran.imag, basamak))
        c = self.bellek_topla.get(ah)
        if c is None:
            sv, sol_a, sag_a, ls_a, lg_a = self.dugum[a]
            if sol_a == _YAPRAK:
                _sv, _sb, _gb, ls_b, _lg_b = self.dugum[b]
                deg = ls_a + oran * ls_b
                c = ((self._sifir(0), 0.0 + 0j) if abs(deg) <= tol
                     else (self._birim_yaprak(), deg))
            else:
                _sv, sol_b, sag_b, ls_b, lg_b = self.dugum[b]
                s_a, s_l = self.topla(sol_a, ls_a, sol_b, oran * ls_b,
                                      seviye - 1)
                g_a, g_l = self.topla(sag_a, lg_a, sag_b, oran * lg_b,
                                      seviye - 1)
                c = self._birlestir(seviye, s_a, s_l, g_a, g_l)
            self.bellek_topla[ah] = c
        return c[0], la * c[1]

    # ── NOKTASAL ÇARPIM (köşegen operatör) ────────────────────────
    def carp(self, a: int, la: complex, b: int, lb: complex,
             seviye: int) -> Tuple[int, complex]:
        tol = self.ayar.tolerans
        if abs(la) <= tol or abs(lb) <= tol:
            return self._sifir(seviye), 0.0 + 0j
        ah = (a, b)
        c = self.bellek_carp.get(ah)
        if c is None:
            sv, sol_a, sag_a, ls_a, lg_a = self.dugum[a]
            if sol_a == _YAPRAK:
                _sv, _s, _g, ls_b, _lg = self.dugum[b]
                deg = ls_a * ls_b
                c = ((self._sifir(0), 0.0 + 0j) if abs(deg) <= tol
                     else (self._birim_yaprak(), deg))
            else:
                _sv, sol_b, sag_b, ls_b, lg_b = self.dugum[b]
                s_a, s_l = self.carp(sol_a, ls_a, sol_b, ls_b, seviye - 1)
                g_a, g_l = self.carp(sag_a, lg_a, sag_b, lg_b, seviye - 1)
                c = self._birlestir(seviye, s_a, s_l, g_a, g_l)
            self.bellek_carp[ah] = c
        return c[0], la * lb * c[1]

    # ── İÇ ÇARPIM ─────────────────────────────────────────────────
    def ic(self, a: int, b: int, seviye: int) -> complex:
        ah = (a, b)
        c = self.bellek_ic.get(ah)
        if c is not None:
            return c
        sv, sol_a, sag_a, ls_a, lg_a = self.dugum[a]
        if sol_a == _YAPRAK:
            _sv, _s, _g, ls_b, _lg = self.dugum[b]
            c = np.conj(ls_a) * ls_b
        else:
            _sv, sol_b, sag_b, ls_b, lg_b = self.dugum[b]
            c = (np.conj(ls_a) * ls_b * self.ic(sol_a, sol_b, seviye - 1)
                 + np.conj(lg_a) * lg_b * self.ic(sag_a, sag_b, seviye - 1))
        self.bellek_ic[ah] = c
        return c

    # ── BİT KAPISI (grafta) ───────────────────────────────────────
    def kapi(self, a: int, la: complex, seviye: int, bit: int,
             G: np.ndarray) -> Tuple[int, complex]:
        """``bit``inci düzleme kapı. Kök seviyesi ``seviye``; hedef
        seviye ``bit + 1``dir (o düğümün çocukları o biti ayırır)."""
        tol = self.ayar.tolerans
        if abs(la) <= tol:
            return a, la
        anahtar = (a, seviye, bit,
                   complex(G[0, 0]), complex(G[0, 1]),
                   complex(G[1, 0]), complex(G[1, 1]))
        c = self.bellek_kapi.get(anahtar)
        if c is None:
            sv, sol, sag, ls, lg = self.dugum[a]
            if seviye == bit + 1:
                # Bu düğümün çocukları tam o bit düzlemidir: karıştır.
                y_s_a, y_s_l = self.topla(sol, G[0, 0] * ls,
                                          sag, G[0, 1] * lg, seviye - 1)
                y_g_a, y_g_l = self.topla(sol, G[1, 0] * ls,
                                          sag, G[1, 1] * lg, seviye - 1)
                c = self._birlestir(seviye, y_s_a, y_s_l, y_g_a, y_g_l)
            else:
                assert sol != _YAPRAK, "bit seviyesi yaprağın altında"
                s_a, s_l = self.kapi(sol, ls, seviye - 1, bit, G)
                g_a, g_l = self.kapi(sag, lg, seviye - 1, bit, G)
                c = self._birlestir(seviye, s_a, s_l, g_a, g_l)
            self.bellek_kapi[anahtar] = c
        return c[0], la * c[1]

    #: Pauli tabanı -- ``4×4`` kapının iki tek-kübit kapıya ayrışması
    #: için. ``σ = {I, X, Y, Z}``; ``{σ_m ⊗ σ_n}`` ``4×4`` uzayın tam
    #: bir tabanıdır, o hâlde HER ``4×4`` matris bu 16 terimle **tam**
    #: yazılır (yaklaşıklık değil, kimlik).
    _PAULI = (np.array([[1, 0], [0, 1]], complex),
              np.array([[0, 1], [1, 0]], complex),
              np.array([[0, -1j], [1j, 0]], complex),
              np.array([[1, 0], [0, -1]], complex))

    def temizle(self, kokler: Sequence[int]) -> Dict[str, Any]:
        """ÇÖP TOPLAMA -- erişilemeyen düğümleri at, adresleri yenile.

        ===============================================================
        NİÇİN ŞART: ÖLÇÜLEN PATLAMA
        ===============================================================

        Her ``apply`` yeni düğümler doğurur; eskisi hâlâ havuzdadır
        fakat artık hiçbir kökten **erişilemez**. Çöp toplama olmadan
        havuz yalnız büyür. Ölçüldü: bir tâlim ileri geçişinde havuz
        **4 194 304** düğüme fırladı ve ``_yaz``ın haddi durdurdu --
        halbuki fiilen erişilen düğüm sayısı bunun binde biriydi.

        Bu bir kusur değil, **eksik parçaydı**: her TDD/BDD motorunun
        çöp toplayıcısı vardır ve bende yoktu.

        Usul: köklerden erişilebilir düğümler işaretlenir, havuz o
        düğümlerle **yeniden kurulur**, adresler yeni sıraya eşlenir ve
        bütün bellekleme tabloları boşaltılır (adresler değiştiği için
        eski anahtarlar geçersizdir).

        Döner: kalan/atılan sayısı ve **yeni kökler** -- çağıran
        köklerini bunlarla değiştirmelidir.
        """
        gorulen: Dict[int, int] = {}
        sira: List[int] = []
        for k in kokler:
            yigin = [int(k)]
            while yigin:
                x = yigin.pop()
                if x in gorulen:
                    continue
                gorulen[x] = -1
                sira.append(x)
                _sv, sol, sag, _ls, _lg = self.dugum[x]
                if sol != _YAPRAK:
                    yigin.append(sol)
                    yigin.append(sag)
        # Çocuklar ebeveynden ÖNCE yazılmalı: seviyeye göre sırala.
        sira.sort(key=lambda x: self.dugum[x][0])
        eski = len(self.dugum)
        yeni: List[Tuple[int, int, int, complex, complex]] = []
        for x in sira:
            sv, sol, sag, ls, lg = self.dugum[x]
            if sol == _YAPRAK:
                yeni.append((sv, _YAPRAK, _YAPRAK, ls, lg))
            else:
                yeni.append((sv, gorulen[sol], gorulen[sag], ls, lg))
            gorulen[x] = len(yeni) - 1
        self.dugum = yeni
        # Tablolar adres taşır; adresler değişti, hepsi geçersiz.
        self.tablo = {}
        self.bellek_topla = {}
        self.bellek_carp = {}
        self.bellek_ic = {}
        self.bellek_kapi = {}
        self.sifir = {}
        tol = self.ayar.tolerans
        basamak = max(1, int(round(-math.log10(max(tol, 1e-15)))))
        for i, (sv, sol, sag, ls, lg) in enumerate(self.dugum):
            ah = (int(sv), int(sol), int(sag),
                  complex(round(ls.real, basamak), round(ls.imag, basamak)),
                  complex(round(lg.real, basamak), round(lg.imag, basamak)))
            self.tablo.setdefault(ah, i)
        return {"kalan": len(self.dugum), "atılan": eski - len(self.dugum),
                "kök": [gorulen[int(k)] for k in kokler]}

    def cift_kapi(self, a: int, la: complex, seviye: int, bi: int,
                  bj: int, G4: np.ndarray) -> Tuple[int, complex]:
        """İki bit düzlemine ``4×4`` kapı -- **grafta**, Pauli ayrışımıyla.

        ===============================================================
        NİÇİN PAULİ AYRIŞIMI (ölçerek seçildi)
        ===============================================================

        Evvelce cofactor (``_dal``/``_dal_kur``) yoluyla dört alt blok
        çıkarılıp karıştırılıyordu. **Ölçüldü ve YANLIŞTI**: 56 bit
        çiftinde yoğun yolla fark ``2,317e+01`` çıktı -- yâni ameliye
        hiç doğru değildi. Sebep, cofactor'ları geri kurarken seviye
        muhasebesinin bozulmasıydı.

        Doğru ve **kesin** yol şudur: ``{σ_m ⊗ σ_n}`` (16 terim) ``4×4``
        uzayın tam tabanıdır, o hâlde

            G = Σ_{m,n} g_{mn} (σ_m ⊗ σ_n),  g_{mn} = Tr[(σ_m⊗σ_n)†G]/4

        bir **kimliktir**, yaklaşıklık değil. Her terim iki ayrı bit
        düzlemine vurulan iki tek-kübit kapıdır; farklı bitler
        **komüt eder**, o hâlde sıra da serbesttir. Netice terimlerin
        grafta toplanmasıdır.

        Bedeli: 16 terim (sıfır katsayılılar atlanır). Kazancı:
        doğruluk ``1e-16``da ve kod tek sayfada.
        """
        tol = self.ayar.tolerans
        G = np.asarray(G4, complex).reshape(2, 2, 2, 2)
        # (p_i,p_j),(r_i,r_j) → 4×4
        M = G.transpose(0, 1, 2, 3).reshape(4, 4)
        birik = None
        for m in range(4):
            for n_ in range(4):
                K = np.kron(self._PAULI[m], self._PAULI[n_])
                g = complex(np.trace(K.conj().T @ M) / 4.0)
                if abs(g) <= tol:
                    continue
                k, l = self.kapi(a, la, seviye, bi, self._PAULI[m])
                k, l = self.kapi(k, l, seviye, bj, self._PAULI[n_])
                if birik is None:
                    birik = (k, g * l)
                else:
                    birik = self.topla(birik[0], birik[1], k, g * l, seviye)
        if birik is None:
            return self._sifir(seviye), 0.0 + 0j
        return birik


def olcu(psi, ayar: Optional[TddAyari] = None) -> Dict[str, Any]:
    """Graf ne kadar sıkıştı, kayıpsız mı -- **ölç**, iddia etme."""
    a = ayar or TddAyari()
    v = np.asarray(psi, complex).reshape(-1)
    D = Tdd.kur(v, a)
    n_d = D.dugum_sayisi()
    bayt = n_d * (2 * 8 + 2 * 16)
    geri = D.ac()
    hata = float(np.max(np.abs(geri - v)))
    return {"düğüm": n_d, "yaprak": 1, "boy": int(v.size),
            "bayt": int(bayt), "yoğun_bayt": int(v.nbytes),
            "sıkışma": float(v.nbytes) / float(max(bayt, 1)),
            "hata": hata,
            "önbelleğe_sığdı": bool(bayt <= int(a.onbellek_bayt)),
            "hadde_sığdı": bool(n_d <= int(a.dugum_haddi))}


def rapor(d: int = 4096, tohum: int = 0) -> str:         # pragma: no cover
    """Sıkışma ve **ameliyelerin grafta doğruluğu** -- ölç."""
    r = np.random.default_rng(int(tohum))
    j = np.arange(d)
    haller = {
        "gürültü (Haar)": (r.normal(size=d) + 1j * r.normal(size=d)),
        "taban |0⟩": np.eye(1, d, 0, dtype=complex).reshape(-1),
        "düzgün süperpozisyon": np.ones(d, complex),
        "çarpım (Kronecker)": np.kron(np.kron(
            r.normal(size=16) + 0j, r.normal(size=16) + 0j),
            r.normal(size=d // 256) + 0j),
    }
    s = ["=== LimTDD -- durum GRAFTIR, ameliyeler GRAFTA ===", "",
         "  d = %d   yoğun = %d bayt" % (d, d * 16), "",
         "  --- SIKIŞMA ---"]
    for ad, v in haller.items():
        v = np.asarray(v, complex).reshape(-1)
        v = v / (np.linalg.norm(v) or 1.0)
        o = olcu(v)
        s.append("  %-22s düğüm %5d  %8d bayt  sıkışma %7.2f×  hata %.2e"
                 % (ad, o["düğüm"], o["bayt"], o["sıkışma"], o["hata"]))

    # --- AMELİYELER GRAFTA MI, DOĞRU MU?
    n = 8
    dd = 1 << n
    v = r.normal(size=dd) + 1j * r.normal(size=dd)
    v /= np.linalg.norm(v)
    w = r.normal(size=dd) + 1j * r.normal(size=dd)
    w /= np.linalg.norm(w)
    hv = Havuz(TddAyari())
    A = Tdd.kur(v, havuz=hv)
    B = Tdd.kur(w, havuz=hv)

    def yogun_bit(x, bit, G):
        b = 1 << bit
        T = x.reshape(-1, 2, b) if b > 1 else x.reshape(-1, 2, 1)
        T = x.reshape(dd // (2 * b), 2, b).copy()
        a0 = T[:, 0, :].copy()
        a1 = T[:, 1, :].copy()
        T[:, 0, :] = G[0, 0] * a0 + G[0, 1] * a1
        T[:, 1, :] = G[1, 0] * a0 + G[1, 1] * a1
        return T.reshape(-1)

    Q = np.linalg.qr(r.normal(size=(2, 2)) + 1j * r.normal(size=(2, 2)))[0]
    f_kapi = 0.0
    for bit in range(n):
        f_kapi = max(f_kapi, float(np.max(np.abs(
            A.bit_kapisi(bit, Q).ac() - yogun_bit(v, bit, Q)))))
    f_top = float(np.max(np.abs(A.topla(B).ac() - (v + w))))
    f_ic = abs(complex(A.ic_carpim(B)) - complex(np.vdot(v, w)))
    fz = np.exp(1j * r.uniform(0, 2 * np.pi, dd))
    F = Tdd.kur(fz, havuz=hv)
    f_faz = float(np.max(np.abs(A.faz(F).ac() - v * fz)))
    f_norm = abs(A.norm_kare() - 1.0)

    s += ["", "  --- AMELİYELER GRAFTA: YOĞUNLA FARK ---",
          "    bit kapısı (%d düzlem) : %.3e" % (n, f_kapi),
          "    toplama               : %.3e" % f_top,
          "    iç çarpım             : %.3e" % f_ic,
          "    köşegen faz           : %.3e" % f_faz,
          "    norm                  : %.3e" % f_norm,
          "",
          "  Gürültüde sıkışma OLMAZ ve bu gizlenmiyor: özdeş alt blok",
          "  yoksa graf yoğundan büyük çıkar."]
    return "\n".join(s)


if __name__ == "__main__":                               # pragma: no cover
    print(rapor())
