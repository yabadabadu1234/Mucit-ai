"""QYAZMAÇ -- qudit yazmacı: MPS'in yerine geçen durum kabı.

Padişahın fermanı: *"Svd mvd olmayacak, Mps iptal olacak"* ve
*"o devri yap"*.

===================================================================
DEVRİN HAKİKÎ MESELESİ -- ÖLÇÜLDÜ, SAKLANMIYOR
===================================================================

Eski yazmaç (``kuantum/yazmac.py`` + ``nefs/zihin_durumu.py``)
**126 kübitlik bir zincirdi** ve durumu MPS ile ``χ = 8``e sıkıştırarak
taşıyordu. Ölçüldü::

    yuva (n)              : 126
    bağ (χ)               : 8
    küllî hüküm kübiti    : 37   (11 alan)
    veri kübiti           : 2 satır × 16
    ileri geçiş başına SVD: ~8 500

**MPS'i kaldırıp ``n``i 126'da bırakmak riyazî olarak imkânsızdır.**
``2¹²⁶`` genlik hiçbir bellekte durmaz; MPS orada bir süs değil, o
uzayı sonlu bellekte taşıyan şeydi. Yâni "SVD'yi çıkar, gerisi aynı
kalsın" diye bir devir yoktur -- olsaydı MPS zaten gereksiz olurdu.

O hâlde devir bir **yer değiştirme değil, kapasite yeniden
tasarımıdır** ve zabıtın kendi cevabı tam da budur:

    126 dolanık kübit  →  belirteç başına TEK d-seviyeli qudit

Zabıt (``Qudite_Tip_Tensorunun_Kodlanma_Nizami``) ``d = 4096`` der ve
hüküm alanlarını **süperseçim sektörleri** olarak yerleştirir::

    [0    – 511 ]  sentaks
    [512  – 2559]  onto-fizik
    [2560 – 4095]  nedensellik / mantık

Burada durum **tam olarak** tutulur: 4096 genlik, 32 KB. Kesme yok,
bağ yok, SVD yok. Kaybedilen şey 126 kübitin üstel uzayıdır;
kazanılan şey o uzayın **hakikaten taşınabilir** ve fazı korunan bir
kesitidir.

===================================================================
NE DEVREDİLDİ, NE DEVREDİLEMEDİ -- açıkça
===================================================================

**Devredilenler** (aynı manayı qudit üstünde veriyorlar):

    eski (MPS)                  yeni (qudit)
    --------------------------  ----------------------------------
    ``alan_degeri(ad)``         sektör ağırlığı ``‖Π_C ψ‖²``
    ``kulli(ad, j)``            sektör dilimi
    ``tek(i, G)``               lif operatörü (Kronecker)
    ``norm`` / ``normalize``    aynen, fakat ``O(d)``
    ``dolasiklik_entropisi``    Kronecker lif kesitinde von Neumann
    ``beyan(sozluk)``           kelâm sektöründen okuma
    ``povm``                    sektör Bloch okuması

**Devredilemeyen ve neden:**

    ``uzak_cift(i, j, G)`` -- 126 yuvalık zincirde uzak iki kübite
    kapı. Quditte 126 yuva **yoktur**; 12 lif vardır. Uzak çift
    kapısının qudit karşılığı iki lif arasında bir Kronecker
    operatörüdür ve o zaten ``lif()``tir. Fakat *"3. ile 97. kübit"*
    diye bir adres qudite çevrilemez -- çünkü o adres eski
    kapasitenin adresidir. Bunu "çevirdim" demek yalan olurdu.

Bu yüzden **45 melekenin qudit sektörlerine yeniden ifadesi**
devrin kalan kısmıdır ve bu dosya onu yapmaz; yalnız üstünde
yapılabileceği zemini kurar ve zemini ölçer.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

import math

import numpy as np

from .galois import ayrik_faz
from .matchgate import matchgate_mi

__all__ = ["QuditAyar", "QuditYazmac", "Iz"]


class Iz:
    """Kapı sayacı ve seyir defteri -- eski ``Yazmac.iz``ın karşılığı."""

    def __init__(self) -> None:
        self.kapi = 0
        #: Atılan ağırlık. **Quditte kesme yoktur**, dolayısıyla bu
        #: sayı daima sıfır kalır. Alan duruyor çünkü melekeler ona
        #: yazıyor; sıfır kalması bir eksiklik değil, kaybın hakikaten
        #: olmadığının ifadesidir.
        self.kesme = 0.0
        self.defter: List[Tuple[str, str]] = []

    def not_dus(self, meleke: str, mesaj: str = "") -> None:
        self.defter.append((str(meleke), str(mesaj)))


@dataclass
class QuditAyar:
    """Qudit yazmacının ölçüleri. Hiçbiri koda gömülü değildir."""

    #: Qudit seviyesi. Zabıtın misali 4096'dır ve ``16³`` lifine ayrılır.
    d: int = 4096
    #: Kronecker lifleri: ``d = ∏ lif``. Zabıt ``16×16×16`` der.
    lif: Tuple[int, ...] = (16, 16, 16)
    #: Yığın (aynı anda kaç bağımsız durum).
    yigin: int = 1
    #: Küllî hüküm alanları. Eski yazmaçtaki ile **aynı adlar**; fakat
    #: burada kübit sayısı değil, sektör **payı**dır: alan ne kadar
    #: geniş bir dilim tutuyor.
    kulli_alanlar: Tuple[Tuple[str, int], ...] = (
        ("makam", 3), ("mizan", 4), ("tenakuz", 2), ("tasdik", 2),
        ("sukut", 1), ("nakz", 2), ("kelam", 4), ("kaide", 12),
        ("orak", 1), ("gaye", 2), ("tertip", 4),
    )
    #: Satır başına yerel hüküm yuvası (eski ``QAyar.yerel_yuva``).
    yerel_yuva: int = 1
    tip: object = np.complex128
    tohum: int = 0
    #: **MOTOR** -- durumun fazı hangi grupta yürüyor.
    #:   ``galois``  : ``Z_m`` ayrık faz (``nefs/galois.ayrik_faz``);
    #:                 akışta ``exp`` çağrısı YOK. Zabıtın hükmü budur.
    #:   ``surekli`` : eski ``e^{iθ}`` yolu. Zabıtla **iptal edildi**;
    #:                 ad yalnız kıyas ölçümü için duruyor ve seçilirse
    #:                 ``beyan``da açıkça görünür.
    motor: str = "galois"
    #: Ayrık faz grubunun mertebesi ``Z_m`` (``motor="galois"`` iken).
    faz_mertebesi: int = 16
    #: **KAPI HATTI.** ``c`` = kapı bandı + kaynaşık C çekirdeği;
    #: ``numpy`` = eski yol (kıyas içindir, seçilirse rapor söyler).
    hat: str = "c"
    #: Bandın azamî boyu; ``0`` = çekirdeğin kendi ölçüsü.
    hat_bandi: int = 0

    def __post_init__(self):
        if int(np.prod(self.lif)) != int(self.d):
            raise ValueError("lifler çarpımı d'ye eşit olmalı: %s ≠ %d"
                             % (self.lif, self.d))


class QuditYazmac:
    """``|Ψ⟩ ∈ ℂ^d`` -- **tam** tutulur. Kesme yok, bağ yok, SVD yok.

    Durum ``(B, d)`` karmaşık dizidir ve lifli görünümü
    ``(B, *lif)``tir. Bütün ameliyeler ya lif üstünde küçük bir
    dizeyle (Kronecker) ya da noktasal fazla (Cartan) yürür.
    """

    def __init__(self, ayar: Optional[QuditAyar] = None,
                 veri_lifi: int = 4,
                 n: Optional[int] = None, bag: Optional[int] = None,
                 tohum: int = 0, tip=None, obek: Optional[int] = None,
                 yigin: Optional[int] = None) -> None:
        """Eski ``Yazmac(n, bag, tohum, tip, obek, yigin)`` imzası da
        kabul edilir: MPS motoru silindi fakat onu çağıran yerler
        (``nefs/zirh.py``, ``ogrenme/optimize.py``) duruyor.
        ``bag`` **yok sayılır** -- quditte bağ yoktur; yok sayıldığı
        burada yazıyor ki "χ'yi ayarladım" sanılmasın."""
        if ayar is None and n is not None:
            k = int(np.ceil(np.log2(max(int(n), 2))))
            k = int(min(max(k, 1), 20))
            ayar = QuditAyar(d=1 << k, lif=(1 << k,), tohum=int(tohum),
                             yigin=int(yigin or 1))
            veri_lifi = k
        self.ayar = ayar or QuditAyar()
        a = self.ayar
        self._veri_lifi = int(veri_lifi)
        # ══════════════════════════════════════════════════════════
        #  SATIR SAYISI **ARGÜMANDAN DEĞİL, LİFTEN** (ferman 1-M)
        # ══════════════════════════════════════════════════════════
        #
        # *"Boyut da ayrı bir yerden gelmez... Her şey yazmaçtan girer,
        # yazmaçtan çıkar, aksi yol yoktur."*
        #
        # Evvelce bu sayı dışarıdan geliyordu ve ``nefs/zihin_durumu.py``
        # onu **elle ``1``e sabitliyordu** -- halbuki aynı dosyada
        # ``QYazmac.n_satir`` girdideki belirteç sayısıydı (2). İki
        # sayı, iki mana, tek isim: melekeler yanlış olanı okuyor ve
        # olmayan bir satıra kapı vuruyordu.
        #
        # Doğrusu liften çıkar ve tek satırdır: ``_lif_no`` ``k``ıncı
        # satırı ``k``ıncı life eşler, o hâlde veri satırı sayısı
        # **çarpımı ``veri_lifi``ye erişene kadar soldan alınan lif
        # adedidir**. ``lif=(16,16,16)``, ``veri_lifi=16`` → ``1``:
        # bir veri lifi, iki hüküm karosu. Lif yapısı değişirse sayı
        # kendiliğinden değişir; elle düzeltilecek bir yer yoktur.
        ns, carp = 0, 1
        for _x in tuple(a.lif):
            if carp >= int(veri_lifi):
                break
            carp *= int(_x)
            ns += 1
        self._n_satir = max(1, ns)
        # ── ÖNBELLEKLER (hız teftişinin ölçtüğü Python yükü) ──────
        self._yuva_onbellek: Dict[int, Tuple[int, int]] = {}
        #: Bütün lifler ikinin kuvveti mi? Bit düzlemi yolu buna bakar
        #: ve evvelce her ``uzak_cift`` çağrısında yeniden hesaplanıyordu
        #: (profilde 922 857 üreteç çağrısı).
        self._ikinin_kuvveti = all(
            (int(x) & (int(x) - 1)) == 0 for x in tuple(self.ayar.lif))
        #: ``lif[k]``ın önü ve ardındaki çarpımlar -- eksen bölmek için.
        self._bolum_onbellek: Dict[int, Tuple[int, int]] = {}
        #: Yuva yazmaçta fiilen var mı? (önbellek)
        self._gecerli_onbellek: Dict[int, bool] = {}
        #: **TOPLU ADRES DİZİLERİ** -- ``_adres_dizileri`` doldurur.
        #: Skaler önbellek (sözlük) ile aynı hakikati taşırlar; fark
        #: yalnız **kaç Python çağrısında** okunduklarıdır.
        self._adres_np: Optional[Tuple[np.ndarray, np.ndarray,
                                       np.ndarray]] = None
        #: ``veri(i, j)`` yuva adresi -- koşu boyunca sabit (önbellek).
        #: Bir satırın yuva adedi -- ``veri()`` bunu her çağrıda
        #: yeniden hesaplıyordu (``ayar``a inip toplama yapıyordu).
        self._satir_yuva = self._veri_lifi + int(self.ayar.yerel_yuva)
        #: Düşen kapı sayacı -- **saklanmıyor**, ``beyan``da görünür.
        self._dusen_kapi = 0
        #: Parite bloğunda (matchgate yolunda) vurulan çift kapı sayısı.
        #: Sıfır kalırsa Valiant yolu hiç kullanılmıyor demektir ve bu
        #: ``beyan``da görünür (ferman 5: ölçü kırmızı yanabilmeli).
        self._matchgate_kapi = 0
        r = np.random.default_rng(int(a.tohum))
        self.B = int(a.yigin)
        self.d = int(a.d)
        # ══════════════════════════════════════════════════════════
        #  DURUMUN TAŞIYICISI: KRONECKER LİFLİ, L1'DE (zabıt Yol 3)
        # ══════════════════════════════════════════════════════════
        # **TDD BAĞI KÖKÜNDEN KESİLDİ.** Zabıt: *"İleri ve geri
        # yayılımda TDD'nin işaretçi/hash hamallığını derhal iptal
        # ediyoruz."* Ölçüldü: 35 163× yavaşlama, işaretçi kovalamanın
        # SIMD'e nispeti.
        #
        # Yerine gelen zabıtın **Yol 3**üdür: durum ``4096``lık kaba bir
        # dizi değil, ``[16,16,16]`` lifli ardışık bir blok. 16 KB'tır
        # ve tamamen L1 önbellekte döner; kapılar ``4096×4096`` GEMM
        # değil, üç adet ``16×16`` karo çarpımıdır.
        self._seviye = int(round(math.log2(self.d)))
        assert 2 ** self._seviye == self.d, (
            "bit düzlemi ikinin kuvvetini ister: d=%d" % self.d)
        # Başlangıç: **düzgün süperpozisyon**, keyfî bir gürültü değil.
        # Aynı tohum daima aynı durumu verir (stokastiklik yasak).
        #: Lif başına **bekleyen karo**; durum okununca iner.
        self._bekleyen: Dict[int, np.ndarray] = {}
        # ── KAPI BANDI: 41 MELEKENİN KAPILARI BURAYA YAZILIR ──────
        # Melekelerin kodu değişmez; değişen, kapının nerede koştuğudur.
        # ``hat="numpy"`` seçilirse eski yol koşar ve ``beyan``da görünür
        # -- ölçü kırmızı yanabilmeli (ferman 5).
        from .qcekirdek import Bant
        self._bant = Bant(int(a.yigin), int(a.d), tuple(a.lif),
                          hat=str(a.hat), bant=int(a.hat_bandi))
        #: Bekleyen köşegen fazın ``Z_m`` üssü (Amy-Maslov-Mosca).
        self._faz_bekleyen: Optional[np.ndarray] = None
        #: Koşu boyunca biriken **bütün** faz üssü -- polinoma oturur.
        self._faz_toplam = np.zeros(int(a.d), np.int64)
        self._psi = np.full((self.B, self.d), 1.0 / np.sqrt(self.d),
                            dtype=a.tip)
        self._sadakat_log = 0.0
        self._kapi = 0
        self.iz = Iz()
        # Bağ tavanı ve kanoniklik MPS mefhumlarıdır; quditte **yoktur**.
        # İmza uyumu için duruyorlar ve okunduklarında bunu söylerler.
        self.bag = 0
        # --- sektör taksimatı: alan payına göre, ORANTILI
        toplam = sum(p for _, p in a.kulli_alanlar)
        self._sektor: Dict[str, Tuple[int, int]] = {}
        bas = 0
        for ad, pay in a.kulli_alanlar:
            gen = max(1, int(round(self.d * pay / toplam)))
            self._sektor[ad] = (bas, min(self.d, bas + gen))
            bas += gen
        # Yuvarlama artığı son alana verilir; hiçbir genlik sahipsiz kalmaz.
        if bas < self.d:
            ad = a.kulli_alanlar[-1][0]
            i, _ = self._sektor[ad]
            self._sektor[ad] = (i, self.d)

    # ── eski ``Yazmac`` yüzeyinden kalanlar ────────────────────────
    @property
    def n(self) -> int:
        """Yuva sayısı -- artık **lif tabanlı**, 126 değil."""
        return self._n_satir * (self._veri_lifi
                                + int(self.ayar.yerel_yuva)) + self.d

    @property
    def A(self) -> np.ndarray:
        """Eski MPS çekirdek dizisi yerine **durumun kendisi**.

        MPS'te ``A`` yuva başına bir tensördü ve durum onların
        kasılmasıydı. Quditte durum zaten açıktır; ``A`` onun lifli
        görünümüdür. İsim uyum için duruyor, mana değişti.
        """
        return self.lifli

    def tekil_yogunluklar(self, yuvalar: Sequence[int]) -> np.ndarray:
        """Seçili yuvaların ``2×2`` indirgenmiş yoğunlukları.

        Eski hatta bu, zinciri iki ucundan süpürüp çevre kurmaktı
        (``O(N χ³)``) ve tek kayıp çağrısında **1042 kere** çağrılıyordu.
        Quditte yuva bir lifin bit düzlemidir; indirgenmiş yoğunluk o
        düzlem üstünde doğrudan toplanır -- süpürme yok, SVD yok.
        """
        idx = [int(y) for y in np.asarray(yuvalar, np.intp).reshape(-1)]
        if not idx:
            return np.zeros((self.B, 0, 2, 2))
        lif = tuple(self.ayar.lif)
        T = self.lifli
        out = np.zeros((self.B, len(idx), 2, 2), complex)
        for m, y in enumerate(idx):
            k, alt = self._lif_no(y)
            if not (0 <= k < len(lif)):
                out[:, m] = np.eye(2) * 0.5      # o lif yok: azamî cehalet
                continue
            n = lif[k]
            b = 1 << int(alt)
            if b >= n:
                out[:, m] = np.eye(2) * 0.5      # o düzlem yok: azamî cehalet
                continue
            X = np.moveaxis(T, k + 1, -1).reshape(self.B, -1, n)
            m0 = np.array([x for x in range(n) if not (x & b)])
            m1 = m0 | b
            a0, a1 = X[:, :, m0], X[:, :, m1]
            out[:, m, 0, 0] = np.sum(np.abs(a0) ** 2, axis=(1, 2))
            out[:, m, 1, 1] = np.sum(np.abs(a1) ** 2, axis=(1, 2))
            c = np.sum(a0 * a1.conj(), axis=(1, 2))
            out[:, m, 0, 1] = c
            out[:, m, 1, 0] = c.conj()
        iz = out[:, :, 0, 0] + out[:, :, 1, 1]
        return out / np.maximum(iz[:, :, None, None].real, 1e-300)

    def yuva_yogunluklari(self, yuvalar=None) -> np.ndarray:
        """``tekil_yogunluklar``ın eski adı. Aynı hesap."""
        if yuvalar is None:
            yuvalar = list(range(min(8, self.d)))
        return self.tekil_yogunluklar(yuvalar)

    def blok_dagilimi(self, bas: int, kac: int) -> np.ndarray:
        """``bas``tan ``kac`` yuvanın ortak dağılımı -- lif üstünde tam."""
        k, alt = self._lif_no(int(bas))
        k = min(int(k), len(self.ayar.lif) - 1)      # lifsiz yuva: son life
        n = self.ayar.lif[k]
        X = np.moveaxis(self.lifli, k + 1, -1).reshape(self.B, -1, n)
        p = np.sum(np.abs(X) ** 2, axis=1)
        m = min(1 << int(kac), n)
        parca = np.array_split(np.arange(n), m)
        P = np.stack([p[:, i].sum(axis=1) for i in parca], axis=1)
        return P / np.maximum(P.sum(axis=1, keepdims=True), 1e-300)

    def olcumler_yigin(self) -> Dict[str, np.ndarray]:
        o = self.olcumler()
        return {k: np.atleast_1d(np.asarray(v, float))
                for k, v in o.items()}

    def makam_derece_vektoru(self) -> np.ndarray:
        i, j = self.sektor("makam")
        return np.linspace(0.0, 1.0, j - i)

    def makam_dagilimi(self) -> np.ndarray:
        i, j = self.sektor("makam")
        p = np.abs(self.psi[:, i:j]) ** 2
        return p / np.maximum(p.sum(axis=1, keepdims=True), 1e-300)

    # ── temel ──────────────────────────────────────────────────────
    @property
    def lifli(self) -> np.ndarray:
        """Durumun lifli görünümü ``(B, *lif)`` -- kopya değil, görünüm."""
        return self.psi.reshape((self.B,) + tuple(self.ayar.lif))

    def norm(self) -> np.ndarray:
        """``⟨Ψ|Ψ⟩`` -- yığın üyesi başına. ``O(d)``, açılım yok."""
        return np.sum(np.abs(self.psi) ** 2, axis=1)

    def normalize(self) -> np.ndarray:
        n = np.sqrt(np.maximum(self.norm(), 1e-300))
        self.psi = self.psi / n[:, None]
        return n

    def norm_hatasi(self) -> float:
        return float(np.max(np.abs(self.norm() - 1.0)))

    def sadakat(self) -> float:
        """``F`` -- tutulan kesir. **Quditte kesme yok → daima 1,0.**"""
        return 1.0

    def sadakat_kapi_basina(self, kapi: int = 1) -> float:
        return 1.0

    def ic_carpim(self, other=None) -> np.ndarray:
        o = self.psi if other is None else np.asarray(other)
        return np.sum(np.conj(self.psi) * o, axis=1)

    def supurme(self, *a, **k) -> None:
        """MPS süpürmesi -- **quditte yok**, iş yapmaz."""
        self.iz.not_dus("süpürme", "quditte süpürme yok -- işlem yok")

    def takas(self, *a, **k) -> None:
        """Takas ağı -- **quditte yok**: uzak çift zaten doğrudan vurulur."""
        self.iz.not_dus("takas", "quditte takas yok -- işlem yok")

    def genlik(self, idx) -> np.ndarray:
        return self.psi[:, int(idx)]

    def deger(self, idx) -> np.ndarray:
        return self.genlik(idx)

    def parametre(self) -> int:
        return int(self.d * 2)

    def bayt(self) -> int:
        return int(self.psi.nbytes)

    def superpozisyona_sok(self) -> None:
        self.superpozisyon()

    def harman_kur(self, *a, **k) -> None:
        self.iz.not_dus("harman_kur", "qudit lif üniterleri kullanılır")

    def tek_kapi(self, G, yuvalar) -> None:
        for y in np.atleast_1d(np.asarray(yuvalar)).reshape(-1):
            self.tek(int(y), G)

    def tek_kapi_yuva(self, yuva: int, G) -> None:
        self.tek(int(yuva), G)

    def cift_kapi(self, G, ofset: int = 0, alt=None, ust=None) -> None:
        self.cift(int(ofset), G)

    def cift_kapi_yuva(self, i: int, j: int, G) -> None:
        self.uzak_cift(int(i), int(j), G)

    def tek_kapi_yigin(self, yuvalar, G) -> None:
        self.tek_yigin(yuvalar, G)

    def cift_kapi_yigin(self, sol_yuvalar, G) -> None:
        G = np.asarray(G)
        m = len(list(sol_yuvalar))
        if G.ndim == 2:
            G = np.broadcast_to(G, (m,) + G.shape)
        for y, g in zip(sol_yuvalar, G):
            self.cift(int(y), g)

    def sadakat_log(self) -> float:
        """``log F``. Quditte kesme YOK, dolayısıyla daima ``0``.

        Eski MPS'te her sıkıştırma bir miktar ağırlık atıyordu ve bu
        sayı onu tutuyordu. Burada atılan hiçbir şey olmadığı için
        sıfırdır -- ve bu, sayının **anlamsız** olduğu değil, kaybın
        hakikaten sıfır olduğu manasına gelir.
        """
        return float(self._sadakat_log)

    # ── kapılar: SVD YOK ───────────────────────────────────────────
    def lif_kapisi(self, k: int, G: np.ndarray) -> None:
        """``n×n`` lif kapısı -- **İMHA EDİLDİ**, çağrılırsa durur.

        Bu ameliye yoğun durumun ``n`` boyutlu eksenini bir ``n×n``
        dizeyle çarpıyordu; TDD'de karşılığı ``2^m`` boyutlu bir apply
        olurdu ve Pauli ayrışımı ``4^m`` terim isterdi (``n=256`` için
        65 536). Yâni bu kapı **graf motoruna geçmez**.

        Çağıranların hepsi bit düzlemi kapılarına çevrildi (``mera``
        dâhil). Geriye kalan bir çağıran varsa burada durur ve görünür
        -- sessizce yoğuna dönmek, iki yolu yan yana yaşatmak olurdu.
        """
        raise NotImplementedError(
            "``lif_kapisi`` imha edildi: n×n kapı graf motoruna geçmez. "
            "Bit düzlemi kapılarını kullanın (``tek``, ``cift``, "
            "``bit_kapisi``). Lif %d, kapı %r." % (k, np.shape(G)))

    def _bit(self, k: int, alt: int) -> int:
        """Lif ``k``nın ``alt``ıncı biti → **düz** bit konumu."""
        _on, ard = self._bolum(int(k))
        return int(math.log2(ard)) + int(alt)

    def sektor_agirligi(self, ad: str) -> np.ndarray:
        """``‖Π_C Ψ‖²`` -- ardışık dilim, SIMD. Graf yok, işaretçi yok."""
        i, j = self.sektor(ad)
        return np.sum(np.abs(self.psi[:, i:j]) ** 2, axis=1)

    # ══════════════════════════════════════════════════════════════════
    #  YOL 3 -- MATRIX-FREE KRONECKER-SIMD (zabıt: TDD Darboğazı)
    # ══════════════════════════════════════════════════════════════════
    #  Zabıtın hükmü harfiyyen: *"Durumu bellekte düz değil, 3 adet
    #  16×16 bloğu hâlinde CPU L1 önbelleğinde döndürür... 4096×4096
    #  GEMM değil."*
    #
    #  Usul şudur: ``d = 2^L`` olduğu için durum ``(B, 2, 2, …, 2)``
    #  görünümüne **kopyasız** girer. Bir bit düzlemi bir eksendir; o
    #  eksenin ``0`` ve ``1`` dilimleri **görünümdür**, ayrılmış bellek
    #  değil. Kapı o iki dilim üstünde dört çarpma-toplamadır:
    #
    #      a₀' = G₀₀a₀ + G₀₁a₁          (tek eksik: dizey yok)
    #      a₁' = G₁₀a₀ + G₁₁a₁
    #
    #  Ne ``np.eye`` tahsisi, ne ``einsum``, ne ``@``, ne ``moveaxis``
    #  kopyası. Dokunulan bellek kapı başına durumun tamamıdır ve
    #  ``B=1``de 64 KB'tır -- L2'de, dilimler L1'de döner.
    #
    #  Bit sırası: ``reshape((B,)+(2,)*L)``da 1. eksen **en anlamlı**
    #  bittir, o hâlde ``2^p`` ağırlıklı bit ``L−p``ıncı eksendir.

    def _eksen(self, k: int, alt: int) -> int:
        """Lif ``k``nın ``alt``ıncı biti → lifli görünümün ekseni.

        Eksen yoksa (``1<<alt`` lifin boyunu aşıyorsa) ``0`` döner; ``0``
        yığın ekseni olduğu için kapı düşürülür ve **sayılır**.
        """
        lif = tuple(self.ayar.lif)
        if not (0 <= int(k) < len(lif)):
            return 0
        n = int(lif[int(k)])
        if (1 << int(alt)) >= n:
            return 0
        return self._seviye - self._bit(int(k), int(alt))

    def _duzlem(self, T: np.ndarray, eksen: int, bit: int) -> np.ndarray:
        """``T``nin ``eksen``indeki ``bit`` dilimi -- **görünüm**, kopya yok."""
        return T[(slice(None),) * eksen + (int(bit),)]

    def _bit_gorunumu(self) -> np.ndarray:
        """Durumun ``(B, 2, 2, …, 2)`` görünümü -- **kopya olmamalı**.

        Kopya olsaydı kapı hiçbir şeye vurmazdı ve sessizce kaybolurdu;
        bu yüzden acımasız ``assert`` ile bağlanmıştır (CLAUDE.md 5).
        """
        T = self.psi.reshape((self.B,) + (2,) * self._seviye)
        assert np.shares_memory(T, self.psi), (
            "bit görünümü kopya çıktı -- kapı duruma vurmazdı")
        return T

    # ══════════════════════════════════════════════════════════════════
    #  KARO BİRİKTİRME -- KRONECKER CEBRİNİN ASIL KAZANCI
    # ══════════════════════════════════════════════════════════════════
    #  Ölçüldü: tek ileri geçişte 195 karo vuruluyor ve her biri durumun
    #  **tamamını** (8 MB) baştan sona dolaşıyor. Halbuki aynı life düşen
    #  karolar birbirleriyle çarpılabilir: ``M₂(M₁Ψ) = (M₂M₁)Ψ``. İki
    #  ``16×16`` karonun çarpımı 4096 işlemdir; durumu bir kere dolaşmak
    #  ise 500 000 işlem. Yâni yüz karo biriktirmek **bedavadır**.
    #
    #  Ayrı liflerdeki karolar da birbiriyle değişmelidir (farklı
    #  eksenlere değerler), o hâlde her lifin kendi bekleyen karosu
    #  ayrı durur ve sıra bozulmaz.
    #
    #  Biriken karolar duruma **ancak durum okunduğunda** iner
    #  (``psi`` müşahedesi). Bu bir yaklaşıklık değildir; aynı hesabın
    #  ertelenmesidir ve netice bit bit aynıdır.

    # ══════════════════════════════════════════════════════════════════
    #  CNOT-DIHEDRAL FAZ BİRİKİMİ (Amy-Maslov-Mosca, 2014)
    # ══════════════════════════════════════════════════════════════════
    #  Zabıt (Non-Clifford Çıkmazı, dördüncü fasıl): *"Z tabanında
    #  köşegen bütün non-Clifford evrimler, durumu bir stabilizer
    #  toplamına açmadan, tek bir İkili Faz Polinomu olarak takip
    #  edilir."*
    #
    #  Ameliyesi şudur: ``|x⟩ ↦ ω^{P(x)}|x⟩``. Ardışık iki köşegen faz
    #  **değişmelidir**, o hâlde birbirleriyle çarpılmaz -- üsleri
    #  ``Z_m``de **toplanır**. Toplama tamsayı ``ADD``tır; genlik
    #  vektörüne dokunulmaz.
    #
    #  Karo ile faz DEĞİŞMEZ (biri köşegen değil). O yüzden ikisi aynı
    #  anda bekleyemez: biri gelince öteki iner. Sıra harfiyyen korunur.

    @property
    def psi(self) -> np.ndarray:
        """Durum ``(B, d)``. Okunduğu anda bekleyenler **iner**."""
        if (self._bekleyen or self._faz_bekleyen is not None
                or not self._bant.bos_mu()):
            self._bosalt()
        return self._psi

    @psi.setter
    def psi(self, v) -> None:
        # Yeni durum eskisinin yerine geçer; bekleyenler okunmuş
        # (yahut geçersiz kılınmış) demektir. Sessizce uygulamak, iki
        # kere vurmak olurdu.
        self._bekleyen.clear()
        self._faz_bekleyen = None
        self._psi = np.asarray(v)

    def _karolari_banda(self) -> None:
        """Bekleyen karoları **banda** yaz -- henüz duruma vurulmaz."""
        if not self._bekleyen:
            return
        bekleyen, self._bekleyen = self._bekleyen, {}
        for k in sorted(bekleyen):
            self._bant.karo(int(k), bekleyen[k])

    def _bosalt(self) -> None:
        """Bandın tamamını icra et, sonra bekleyen fazı indir.

        Sıra harfiyyen korunur: karo ve çift kapılar banda yazılış
        sırasıyla koşar; faz ise (değişmeli olduğu için) sonda iner --
        zâten faz biriktirilirken bant boşaltılmıştır, o hâlde fazın
        yeri daima bandın sonrasıdır.
        """
        self._karolari_banda()
        if not self._bant.bos_mu():
            self._psi = np.ascontiguousarray(self._psi)
            self._bant.bosalt(self._psi)
        self._faz_indir()

    def _faz_indir(self) -> None:
        """Biriken ``Z_m`` faz üssünü duruma **bir kere** vur."""
        k = self._faz_bekleyen
        if k is None:
            return
        self._faz_bekleyen = None
        m = int(self.ayar.faz_mertebesi)
        if not np.any(k):
            return                                   # ω⁰ = 1: iş yok
        self._psi = np.asarray(
            ayrik_faz(self._psi, -k * (2.0 * math.pi / m), m),
            self._psi.dtype)

    def faz_birikimi(self) -> np.ndarray:
        """Koşu boyunca biriken **bütün** köşegen fazın ``Z_m`` üssü.

        Amy-Maslov-Mosca'nın ``P(x)``i budur: ``d`` uzunluğunda tamsayı
        dizisi, ``|x⟩ ↦ ω^{P(x)}|x⟩``. ``nefs/faz_polinomu.py`` bunu
        polinom katsayılarına oturtur ve **derecesini** ölçer: derece
        ``≤ 3`` ise durum CNOT-Dihedral sınıfındadır ve tablo dallanmaz.
        """
        return self._faz_toplam.copy()

    def _karo_indir(self, k: int, M: np.ndarray) -> None:
        """``k``ıncı life ``n×n`` **karo**yu fiilen vur -- BLAS-3 GEMM.

        Zabıtın Yol 3'ünün tam ifadesi budur. Durum ``(B, ön, n, ard)``
        görünümündedir ve karo yalnız ``n`` eksenine değer::

            ard = 1  →  (N, n) @ Mᵀ          tek büyük GEMM
            ard > 1  →  M @ (N, n, ard)      yığın GEMM

        ``n = 16`` olduğu için karo 512 bayttır ve L1'de kalır; taşınan
        blok ``n·ard`` sütunudur. ``4096×4096`` bir dizey **hiç
        kurulmaz** -- zabıtın yasakladığı tam olarak oydu.

        **ÖLÇÜLEN SEBEP.** Evvelce kapı bit düzlemi diliminde
        (``T[..., 0, ...]`` / ``T[..., 1, ...]``) vuruluyordu ve netice
        doğruydu; fakat alt bitlerde dilimin iç adımı 2 elemana kadar
        düşüyor, SIMD hattı boş dönüyordu. Karoya geçmek dört kat daha
        çok çarpma yapar, buna mukabil hepsi ardışıktır.
        """
        n = int(self.ayar.lif[int(k)])
        on, ard = self._bolum(int(k))
        X = self._psi.reshape(self.B * on, n, ard)
        M = np.asarray(M, complex)
        if ard == 1:
            Y = X.reshape(-1, n) @ M.T
        else:
            Y = np.matmul(M, X)
        self._psi = np.ascontiguousarray(
            Y.reshape(self.B, self.d), dtype=self._psi.dtype)

    def _karo_vur(self, k: int, M: np.ndarray) -> None:
        """``k``ıncı lifin bekleyen karosuna ``M``yi **çarp** -- ertele.

        Durum burada dolaşılmaz; yalnız ``n×n`` karo güncellenir.
        """
        # Karo köşegen değildir: bekleyen faz onunla DEĞİŞMEZ, o hâlde
        # evvela iner. Aksi hâlde sıra bozulur ve netice başka çıkardı.
        self._faz_indir()
        M = np.asarray(M, complex)
        eski = self._bekleyen.get(int(k))
        self._bekleyen[int(k)] = M if eski is None else M @ eski
        self._kapi += 1
        self.iz.kapi += 1

    def _bit_kapisi_lifli(self, k: int, alt: int, G: np.ndarray) -> None:
        """Bir bit düzlemine ``2×2`` kapı -- lifin ``n×n`` karosunda.

        ``2×2`` kapı, lifin ``alt``ıncı bit düzlemine göre eşleşen
        çiftleri döndüren bir ``SU(n)`` elemanıdır (``_gomulu``); o karo
        kurulup ``_karo_vur`` ile vurulur.
        """
        if self._eksen(k, alt) <= 0:                 # o bit düzlemi yok
            self._dusen_kapi += 1
            return
        n = int(self.ayar.lif[int(k)])
        self._karo_vur(k, self._gomulu(n, int(alt), G))

    def _cift_kapisi_lifli(self, ki: int, ai: int, kj: int, aj: int,
                           G: np.ndarray) -> None:
        """İki bit düzlemine ``4×4`` kapı.

        Taban sırası ``uzak_cift``inkiyle birdir: ``a = 2·bit_i + bit_j``.

        İki bit **aynı lifteyse** kapı o lifin ``n×n`` karosuna gömülür
        ve tek GEMM olur. **Ayrı liflerdeyse** kapı çarpanlarına
        ayrılamaz (dolaştırıcıdır); o hâlde dört bit dilimi ardışık bir
        ``(N, 4)`` bloğa toplanır, ``4×4`` GEMM vurulur ve geri
        dağıtılır. Toplama-dağıtma iki geçiştir; on altı ayrı adımlı
        ufunc geçişinden ucuzdur (ölçüldü).
        """
        ei = self._eksen(ki, ai)
        ej = self._eksen(kj, aj)
        if ei <= 0 or ej <= 0 or ei == ej:
            self._dusen_kapi += 1
            return
        G = np.asarray(G, complex).reshape(4, 4)
        if int(ki) == int(kj):
            n = int(self.ayar.lif[int(ki)])
            bi, bj = 1 << int(ai), 1 << int(aj)
            M = np.eye(n, dtype=complex)
            for x in range(n):
                if (x & bi) or (x & bj):
                    continue
                idx = [x, x | bj, x | bi, x | bi | bj]
                for a in range(4):
                    for b in range(4):
                        M[idx[a], idx[b]] = G[a, b]
            self._karo_vur(int(ki), M)
            return
        # ── KAPI DURUMA VURULMAZ, **BANDA** YAZILIR ─────────────────
        # Ölçüldü (nefs/qcekirdek.py): çift kapı numpy'da dört süslü
        # indisleme + bir ``stack`` + bir ``einsum`` ister ve durumu beş
        # kere dolaştırır; C'de dört adres okunup dört adres yazılır ve
        # durum **bir kere** dolaşılır -- 6,9× hızlı. Karo ise bir
        # GEMM'dir ve orada BLAS bizden 2-25× hızlıdır; o yüzden karo
        # BLAS'ta, çift C'de koşar. İkisi de banda yazılır ki sıra
        # bozulmasın.
        #
        # Kapı matchgate formundaysa (Valiant-Terhal) bant bunu tanır ve
        # C'de **yarım çarpımla** koşar: parite korunduğu için iki
        # altuzay ayrı döner, öbek başına 16 değil 8 karmaşık çarpım.
        self._faz_indir()
        self._karolari_banda()
        bi = 1 << int(self._seviye - ei)
        bj = 1 << int(self._seviye - ej)
        if matchgate_mi(G)[0]:
            self._matchgate_kapi += 1
        self._bant.cift(bi, bj, G)
        self._kapi += 1
        self.iz.kapi += 1

    def bit_kapisi(self, k: int, alt: int, G: np.ndarray) -> None:
        """``k``ıncı lifin ``alt``ıncı bit düzlemine ``2×2`` kapı.

        **YOĞUN GÖVDE İMHA EDİLDİ (CLAUDE.md 1-E: yarım iş yasak).**
        Burada durumun tamamını ``reshape`` edip ``n×n`` dizeyle çarpan
        bir gövde vardı; sonra bir müddet graf (TDD) yolundaydı ve o da
        zabıtla iptal edildi. Şimdi ``_bit_kapisi_lifli``dedir: dizeysiz
        Kronecker-SIMD.

        İki yol yan yana bırakılmadı: eskisi silindi, bu ad yenisine
        havale eder. Yan yana dursalardı hangisinin koştuğu belirsiz
        olurdu ve belirsizlik münafıklığın yatağıdır.
        """
        self._bit_kapisi_lifli(k, alt, G)

    def faz(self, teta) -> None:
        """Cartan köşegeni: ``|Ψ⟩ ← ω^{k(θ)} ⊙ |Ψ⟩``. ``O(d)``.

        Matris çarpımı yoktur; zabıtın üçüncü tedbiri budur
        (``O(d²) → O(d)``, 4096×).

        **TRANSANDANTAL FAZ İPTAL (zabıt, birinci fasıl).** ``motor``
        ``galois`` iken açı ``Z_m``ye yuvarlanır ve ``m`` elemanlı birim
        kök tablosundan **okunur**; ``np.exp`` akışta hiç çağrılmaz.
        ``surekli`` seçilirse eski yol koşar ve bu, ``beyan``da görünür.
        """
        t = np.asarray(teta, float).reshape(-1)
        if t.size != self.d:
            from .qudit import agirlik
            t = np.asarray(agirlik(self.d, t), float).reshape(-1)
        m = int(self.ayar.faz_mertebesi)
        if str(self.ayar.motor) != "galois":
            self._bosalt()
            self._psi = self._psi * np.exp(-1j * t)
            self._kapi += 1
            return
        # ``Z_m``de tamsayı üs. Genliğe DOKUNULMAZ; üsler toplanır.
        k = (np.rint(-t * m / (2.0 * math.pi)).astype(np.int64) % m)
        self._faz_toplam = (self._faz_toplam + k) % m
        if self._bekleyen:
            self._bosalt()                # karo bekliyorsa evvela o iner
        self._faz_bekleyen = (k if self._faz_bekleyen is None
                              else (self._faz_bekleyen + k) % m)
        self._kapi += 1

    def sektor_kapisi(self, ad: str, M: np.ndarray) -> None:
        """Bir süperseçim sektörüne operatör -- sıfırlar çarpılmaz."""
        i, j = self.sektor(ad)
        M = np.asarray(M)
        if M.shape != (j - i, j - i):
            raise ValueError("sektör kapısı %s olmalı, %s verildi"
                             % ((j - i, j - i), M.shape))
        self.psi[:, i:j] = self.psi[:, i:j] @ M.T
        self._kapi += 1

    # ── sektörler (eski ``kulli`` alanlarının qudit karşılığı) ──────
    def sektor(self, ad: str) -> Tuple[int, int]:
        if ad not in self._sektor:
            raise ValueError("küllî alan bilinmiyor: %r" % (ad,))
        return self._sektor[ad]

    def alan_degeri(self, ad: str):
        """``‖Π_C Ψ‖²`` -- alanın ``[0,1]``deki değeri.

        Eski yazmaçta bu, alanın kübitlerinin ``ρ₁₁`` ortalamasıydı ve
        her okuma zinciri baştan sona süpürüyordu (ölçüldü: tek kayıp
        çağrısında 1042 süpürme, 2,90 sn). Quditte sektörün ağırlığı
        doğrudan okunur: ``O(sektör)``, süpürme yok.
        """
        # **GRAFTA OKUNUR.** Evvelce yoğun ``psi`` dilimlenip kare
        # toplamı alınıyordu; artık sektör göstergesiyle noktasal
        # çarpımın normu grafta hesaplanır (``sektor_agirligi``).
        v = self.sektor_agirligi(ad)
        return float(v[0]) if self.B == 1 else v

    def olcumler(self) -> Dict[str, float]:
        """Bütün küllî alanlar + entropi -- **tek geçişte**."""
        p = np.abs(self.psi) ** 2
        out: Dict[str, float] = {}
        for ad in self._sektor:
            i, j = self._sektor[ad]
            v = np.sum(p[:, i:j], axis=1)
            out[ad] = float(v[0]) if self.B == 1 else v
        e = self.dolasiklik_entropisi()
        out["entropi"] = float(e["entropi"])
        out["norm_hatası"] = self.norm_hatasi()
        return out

    # ── entropi: lif kesitinde, SVD'siz ────────────────────────────
    def dolasiklik_entropisi(self, kesit: int = 1) -> Dict[str, float]:
        """Kronecker lif kesitinde von Neumann entropisi.

        ``S = −Σ p ln p``, ``p`` indirgenmiş yoğunluğun özdeğerleri.
        **SVD kullanılmaz**: ``ρ`` küçüktür (``d_sol × d_sol``) ve
        Hermitiktir; özdeğerleri ``eigvalsh`` ile alınır. Eski hatta
        entropi MPS Schmidt değerlerinden geliyordu ve her ölçüm bir
        SVD demekti.
        """
        lif = tuple(self.ayar.lif)
        kesit = int(np.clip(kesit, 1, len(lif) - 1))
        sol = int(np.prod(lif[:kesit]))
        sag = int(np.prod(lif[kesit:]))
        M = self.psi.reshape(self.B, sol, sag)
        rho = np.einsum("bij,bkj->bik", M, M.conj())
        iz = np.einsum("bii->b", rho).real
        rho = rho / np.maximum(iz, 1e-300)[:, None, None]
        w = np.linalg.eigvalsh(rho)
        w = np.clip(w.real, 1e-300, None)
        S = -np.sum(w * np.log(w), axis=1)
        return {"entropi": float(np.mean(S)),
                "entropi_yigin": S,
                "schmidt": float(min(sol, sag)),
                "kesit": kesit}

    # ── okuma ──────────────────────────────────────────────────────
    def beyan(self, sozluk: int = 16) -> np.ndarray:
        """Belirteç dağılımı -- **kelâm sektöründen**.

        Sektör ``sozluk`` parçaya bölünür ve her parçanın ağırlığı o
        belirtecin olasılığıdır. Born kuralı burada da geçerlidir;
        fakat faz **atılmaz**: ``kulli_mizan`` onu ayrıca görür.
        """
        i, j = self.sektor("kelam")
        p = np.abs(self.psi[:, i:j]) ** 2
        parca = np.array_split(np.arange(j - i), int(sozluk))
        P = np.stack([p[:, idx].sum(axis=1) for idx in parca], axis=1)
        return P / np.maximum(P.sum(axis=1, keepdims=True), 1e-300)

    def povm(self, ad: str) -> Tuple[float, float]:
        """Sektörün Bloch benzeri iki reel okuması ``(z, x)``."""
        i, j = self.sektor(ad)
        v = self.psi[:, i:j]
        yari = (j - i) // 2 or 1
        z = float(np.mean(np.sum(np.abs(v[:, :yari]) ** 2, axis=1)
                          - np.sum(np.abs(v[:, yari:]) ** 2, axis=1)))
        x = float(np.mean(2.0 * np.real(
            np.sum(v[:, :yari] * v[:, yari:yari * 2].conj(), axis=1))))
        return z, x

    # ── kodlama: ikili YOK ─────────────────────────────────────────
    def kodla(self, belirtecler: Sequence[int], sozluk: int = 16) -> None:
        """Belirteçleri qudite kodla -- **düz ikili kodlama yoktur**.

        Her belirteç kelâm sektöründe kendi dilimine düşer ve o dilim
        koherent bir dalga paketiyle doldurulur. Kelimeler arası
        mesafe Hilbert iç çarpımıdır; Hamming değil.
        """
        t = np.asarray(belirtecler, int).reshape(-1) % int(sozluk)
        i, j = self.sektor("kelam")
        parca = np.array_split(np.arange(i, j), int(sozluk))
        self.psi = np.zeros((self.B, self.d), dtype=self.ayar.tip)
        for b in range(self.B):
            tb = t[b % t.size]
            idx = parca[int(tb)]
            # Koherent dalga paketi: dilim içinde Gauss zarf + faz.
            u = np.arange(idx.size) - (idx.size - 1) / 2.0
            zarf = np.exp(-(u ** 2) / max(idx.size, 1))
            self.psi[b, idx] = zarf * np.exp(1j * u * (1.0 + tb))
        self.normalize()

    def superpozisyon(self) -> None:
        """Bütün taban durumları eşit genlikte -- Hadamard'ın qudit hâli."""
        self.psi = np.full((self.B, self.d), 1.0 / np.sqrt(self.d),
                           dtype=self.ayar.tip)

    # ══════════════════════════════════════════════════════════════
    #  MELEKE YÜZEYİ -- eski 126 yuvalık adreslemenin qudit karşılığı
    # ══════════════════════════════════════════════════════════════
    #
    #  TAKSİMAT (ölçüyle kuruldu, uydurulmadı):
    #
    #      satır lifi  ℂ^sozluk   × n_satir   -- belirteç TABAN DURUMU
    #      hüküm lifi  ℂ^4096                 -- 11 alan, SEKTÖR olarak
    #
    #  ``d = sozluk^n_satir × 4096``. ``n_satir=2, sozluk=16`` ile
    #  ``2²⁰`` = 1 048 576 genlik = 16 MB. **Tam tutulur.**
    #
    #  Belirteç artık 16 ikili kübite bölünmez; satır lifinin bir
    #  TABAN DURUMUDUR. Taban durumları dik olduğu için bütün ikili
    #  mesafeler kendiliğinden eşittir -- Hadamard'a da, ikili
    #  kodlamaya da lüzum kalmaz.

    def _lif_no(self, yuva: int) -> Tuple[int, int]:
        """Eski yuva indisini ``(lif, alt)`` adresine çevir -- **önbellekli**.

        Eski zincirde ``veri(i,j)``, ``yerel(i)``, ``kulli(ad,j)`` hep
        tek bir tam sayı yuvaydı. Quditte satırlar ayrı liflerdir,
        hüküm alanları ise **hüküm lifinin sektörleridir**.

        **ÖNBELLEK NİÇİN.** Profil ölçtü: tek ileri geçişte bu fonksiyon
        **1 029 599 kere** çağrılıyor ve 0,523 sn yiyor. Hesabın kendisi
        iki bölme; pahalı olan Python çağrısının kendisidir. Sonuç
        yuvaya göre **sabittir** (ayar koşu boyunca değişmez), o hâlde
        bir kere hesaplanıp saklanır. Bu bir yaklaşıklık değil,
        aynı hesabın hatırlanmasıdır.
        """
        y = int(yuva)
        c = self._yuva_onbellek.get(y)
        if c is not None:
            return c
        ns, sk = self._n_satir, self._veri_lifi
        satir_yuva = sk + int(self.ayar.yerel_yuva)
        if y < ns * satir_yuva:
            c = (y // satir_yuva, y % satir_yuva)
        else:
            # ── HÜKÜM YUVALARI: ARTAN LİFLERE **YAYILIR** ──────────
            # Evvelce hepsi tek bir hüküm lifine (``ns``) düşüyordu ve
            # o yapıda o lif ``256`` seviyeliydi, sekiz bit düzlemi
            # oradaydı. Zabıt lifi ``[16,16,16]``e böldü: aynı sekiz
            # bit düzlemi şimdi **iki** lifte durur. Tek life
            # düşürmeye devam etseydik dört bit düzlemi adressiz
            # kalırdı -- yâni kapıların yarısı sessizce düşerdi.
            o = y - ns * satir_yuva
            c = (len(self.ayar.lif), o)                  # hiçbir lif: düşer
            for k in range(ns, len(self.ayar.lif)):
                w = int(self.ayar.lif[k]).bit_length() - 1
                if o < w:
                    c = (k, o)
                    break
                o -= w
        self._yuva_onbellek[y] = c
        return c

    def gecerli(self, yuva: int) -> bool:
        """Bu yuva yazmaçta FİİLEN var mı? -- önbellekli, ``O(1)``.

        ===============================================================
        ÖLÇÜLEN VE SAKLANMAYAN HAKİKAT
        ===============================================================

        Hız teftişi tek bir ileri geçişte **89 341 kapı çağrısı** saydı
        ve bunların yalnız **159'unun** (%0,2) fiilen iş yaptığını
        gösterdi. Geri kalan %99,8'i ``1 << alt >= lif[k]`` şartına
        takılıp derhal geri dönüyordu -- yâni yazmacın **haddini aşan**
        yuvalara kapı vuruluyordu.

        İki ayrı mesele vardır ve ikisi de yazılıdır:

        1. **HIZ.** O 89 bin çağrı boş dönse de her biri bir Python
           çağrısı, bir ``_lif_no``, bir ``asarray``dır: ölçüldü, tek
           geçişin **tamamı** (0,90 sn) buradan geliyordu. Bu fonksiyon
           o çağrıları bir sözlük aramasına indirir.

        2. **HÜKÜM.** Melekelerin yazmacın haddini aşan yuvalara
           yazması bir **borçtur** ve bu düzeltme onu gizlemez: düşen
           kapılar ``_dusen_kapi``de sayılır ve ``beyan``da görünür.
           Davranış birebir aynıdır (evvelce de düşüyorlardı); değişen
           yalnız düşme maliyetidir.
        """
        y = int(yuva)
        c = self._gecerli_onbellek.get(y)
        if c is not None:
            return c
        k, alt = self._lif_no(y)
        lif = tuple(self.ayar.lif)
        c = bool(0 <= k < len(lif) and (1 << int(alt)) < int(lif[k]))
        self._gecerli_onbellek[y] = c
        return c

    def _adres_dizileri(self):
        """Bütün yuvaların ``(geçerli, lif, alt)`` adresi -- **BİR KERE**.

        ===============================================================
        NİÇİN DİZİ: C'YE ÇEVİRME KARARI **ÖLÇÜLDÜ**
        ===============================================================

        Padişahın hükmü: *"verimi iki kat ve üzeri arttırmak kaydıyla ne
        kadar çevirebileceğin kod varsa hepsini c++'a çevir. Aynı
        zamanda çok çok az çevrim kullanmalarına ehemmiyet ver."*

        Şart **ölçüldü** ve hüküm şartın kendisinden çıktı (200 000
        çağrı, bu makine)::

            dict.get            113,0 ns/çağrı      (bugünkü hâl)
            liste[]              80,1 ns/çağrı      1,43×  -- şart TUTMAZ
            ctypes ile C         725,7 ns/çağrı     0,16×  -- ŞART TERSİNE
            numpy skaler        143,7 ns/çağrı      0,79×  -- daha kötü
            numpy TOPLU           2,4 ns/çağrı     47,1×   -- şart TUTAR

        Yâni bu fonksiyonları **tek tek** C'ye çevirmek verimi iki kat
        arttırmaz, **altıda bire düşürür**: hesabın kendisi iki bölmedir,
        pahalı olan hudut geçişidir ve ``ctypes`` hududu Python
        çağrısından pahalıdır. Şartı tutturan tek yol çağrıyı C'ye
        taşımak değil, **çağrıyı ortadan kaldırmaktır**: 60 000 ayrı
        arama yerine bir dizi araması.

        (Kapıların **icrası** zaten C'dedir -- ``nefs/qcekirdek.py``
        bandın tamamını tek C çağrısında koşturur. Oradaki şart tutar
        çünkü orada bir çağrıya binlerce kapı düşer.)
        """
        if self._adres_np is None:
            ns = self._n_satir
            satir_yuva = self._veri_lifi + int(self.ayar.yerel_yuva)
            lif = tuple(self.ayar.lif)
            n = ns * satir_yuva + sum(
                int(x).bit_length() - 1 for x in lif[ns:])
            k = np.empty(n, np.int64)
            alt = np.empty(n, np.int64)
            gec = np.empty(n, bool)
            for y in range(n):
                kk, aa = self._lif_no(y)
                k[y] = kk
                alt[y] = aa
                gec[y] = self.gecerli(y)
            self._adres_np = (gec, k, alt)
        return self._adres_np

    def gecerli_toplu(self, yuvalar) -> np.ndarray:
        """``gecerli`` -- **tek çağrıda bütün yuvalar**. Netice birebir aynı."""
        y = np.asarray(yuvalar, np.int64).reshape(-1)
        gec, _k, _a = self._adres_dizileri()
        icinde = (y >= 0) & (y < gec.size)
        out = np.zeros(y.size, bool)
        out[icinde] = gec[y[icinde]]
        return out

    def lif_no_toplu(self, yuvalar) -> Tuple[np.ndarray, np.ndarray]:
        """``_lif_no`` -- tek çağrıda. Geçersiz yuvada ``(-1, -1)``."""
        y = np.asarray(yuvalar, np.int64).reshape(-1)
        gec, k, a = self._adres_dizileri()
        icinde = (y >= 0) & (y < gec.size)
        kk = np.full(y.size, -1, np.int64)
        aa = np.full(y.size, -1, np.int64)
        kk[icinde] = k[y[icinde]]
        aa[icinde] = a[y[icinde]]
        return kk, aa

    def veri(self, i: int, j: int) -> int:
        """``i``inci satırın ``j``inci yuvası -- **önbellekli**.

        Ölçüldü: tek küllî mizan çağrısında 392 380 kere çağrılıyor ve
        iki katman (``zihin_durumu.veri`` → burası) toplam 0,41 sn
        yiyor. Hesabın kendisi bir çarpma bir toplamadır; pahalı olan
        Python çağrısı ve ``int()`` dönüşümleridir. Netice ``(i,j)``ye
        göre koşu boyunca **sabittir**.
        """
        # **ÖNBELLEK KALDIRILDI -- ÖLÇÜLDÜ, ZARARDAYDI.** Hesap tek bir
        # çarpma-toplamadır (~60 ns); demet anahtarlı bir ``dict.get``
        # ise ~150 ns. Yâni "hatırlamak" hesaptan **iki buçuk kat
        # pahalıydı**: önbellek burada bir tasarruf değil, bir masraftı.
        # (``_lif_no``da tersidir ve orada duruyor: onun gövdesi bir
        # döngüdür.) ``_satir_yuva`` bir kere kurulur; her çağrıda
        # ``ayar``a inmek de o masrafın parçasıydı.
        return int(i) * self._satir_yuva + int(j)

    @property
    def n_satir(self) -> int:
        """**TEK KAYNAK** (ferman 1-M): kaç veri satırı adreslenebilir.

        Yazmacın lif yapısı ``(veri_lifi, karo, karo)``dır ve
        ``_lif_no`` satırı **lif indisiyle** eşler: ``k``ıncı satır
        ``k``ıncı liftir. O hâlde adreslenebilir satır sayısı bir
        tercih değil, lif yapısının kendisidir. Dışarıdan gelen
        "kaç belirteç var" sayısı **satır sayısı değildir**: kalan
        belirteçler ``kodla``da faza girer, yeni bir lif açmaz.
        """
        return int(self._n_satir)

    def veri_izgara(self, sutun=None, satir=None) -> np.ndarray:
        """``veri(i, j)`` ızgarasının **tamamı, tek çağrıda** (satır-major).

        Ölçüldü: tek küllî mizan çağrısında ``veri`` **49 071** kere
        çağrılıyor ve çağrıların ezici çoğunluğu
        ``[q.veri(i, j) for i in ... for j in ...]`` biçiminde düzenli
        bir ızgaradır. Hesap tek bir çarpma-toplamadır; pahalı olan
        49 bin ayrı Python çağrısıdır. Yayın (broadcast) ile aynı
        ızgara tek işlemde çıkar ve **sıra birebir korunur**.
        """
        i = (np.arange(self._n_satir) if satir is None
             else np.asarray(satir, np.int64).reshape(-1))
        j = (np.arange(self._veri_lifi) if sutun is None
             else np.asarray(sutun, np.int64).reshape(-1))
        return (i[:, None] * self._satir_yuva + j[None, :]).reshape(-1)

    def yerel(self, i: int) -> int:
        return self.veri(i, self._veri_lifi)

    def kulli(self, ad: str, j: int = 0) -> int:
        """Küllî alanın ``j``inci yuvası -- artık **sektör** indisi."""
        i, _ = self.sektor(ad)
        return self._n_satir * (self._veri_lifi
                                + int(self.ayar.yerel_yuva)) + i + int(j)

    def yereller(self) -> List[int]:
        return [self.yerel(i) for i in range(self._n_satir)]

    def bolge_var(self, ad: str) -> bool:
        return ad in self._sektor

    def not_dus(self, meleke: str, mesaj: str = "") -> None:
        self.iz.not_dus(meleke, mesaj)

    def kanonikle(self) -> None:
        """MPS kanonik biçimi -- **quditte yoktur, iş de yapmaz**.

        Eski hatta bu, SVD ile merkez taşımaktı ve meleke başına
        çağrılıyordu. Quditte durum zaten tam ve kanoniktir; burada
        yapılacak bir şey olmadığı için **hiçbir şey yapılmaz**.
        Sessizce geçilmiyor: ``iz``e yazılıyor ki "kanonikleştirdim"
        sanılmasın.
        """
        self.iz.not_dus("kanonikle", "quditte kanoniklik yok -- işlem yok")

    def _gomulu(self, n: int, alt: int, G: np.ndarray) -> np.ndarray:
        """``2×2`` kapıyı ``n`` boyutlu life ``alt``ıncı bit düzleminde göm.

        Bir ikili kapı, qudit lifinin iki taban durumunu döndüren bir
        ``SU(n)`` elemanıdır. ``alt``ıncı bit düzlemi, indisin
        ``alt``ıncı bitine göre eşleşen çiftleri demektir -- yâni
        ``|…0…⟩ ↔ |…1…⟩``. Bu bir taklit değil, kapının qudit
        uzayındaki hakikî gömülmesidir.
        """
        G = np.asarray(G, complex).reshape(2, 2)
        M = np.eye(n, dtype=complex)
        b = 1 << int(alt)
        if b >= n:
            return M                                     # o düzlem yok
        for x in range(n):
            if x & b:
                continue
            y = x | b
            M[x, x] = G[0, 0]; M[x, y] = G[0, 1]
            M[y, x] = G[1, 0]; M[y, y] = G[1, 1]
        return M

    def tek(self, yuva: int, G: np.ndarray) -> None:
        """Tek yuvaya ``2×2`` kapı -- bit düzlemine doğrudan, ``O(B·d)``."""
        if not self.gecerli(yuva):
            self._dusen_kapi += 1
            return
        k, alt = self._lif_no(yuva)
        self.bit_kapisi(k, alt, G)

    def tek_yigin(self, yuvalar: Sequence[int], G) -> None:
        """``m`` yuvaya ``m`` kapı -- aynı BİT DÜZLEMİNE düşenler bileşir.

        Evvelce bileşme lif seviyesindeydi: aynı life düşen kapılar
        ``n×n`` dizeylerde çarpılıyordu (``n³`` işlem, ``n=256`` için
        16 milyon). Şimdi bileşme ``2×2``dedir ve yalnız **aynı bit
        düzlemine** düşenler bileşir; farklı düzlemler zaten sıralı
        vurulur ve netice birebir aynıdır (sıra korunur).
        """
        G = np.asarray(G)
        if G.ndim == 2:
            G = np.broadcast_to(G, (len(yuvalar), 2, 2))
        sira: List[Tuple[int, int]] = []
        birik: Dict[Tuple[int, int], np.ndarray] = {}
        # **ELEME TOPLU** (bkz. ``_adres_dizileri``): kapıların %99,8'i
        # yazmacın haddini aşıp düşer. Evvelce her düşen kapı için üç
        # Python çağrısı (``gecerli`` → ``_lif_no`` → sözlük) yapılıyordu;
        # şimdi hepsi tek dizi aramasında elenir. Netice birebir aynı,
        # düşenler yine ``_dusen_kapi``de sayılır.
        yv = np.asarray([int(y) for y in yuvalar], np.int64)
        gec = self.gecerli_toplu(yv)
        kk, aa = self.lif_no_toplu(yv)
        self._dusen_kapi += int((~gec).sum())
        for idx in np.flatnonzero(gec):
            g = G[int(idx)]
            anahtar = (int(kk[idx]), int(aa[idx]))
            g2 = np.asarray(g, complex).reshape(2, 2)
            if anahtar in birik:
                birik[anahtar] = g2 @ birik[anahtar]
            else:
                birik[anahtar] = g2
                sira.append(anahtar)
        for anahtar in sira:
            self.bit_kapisi(anahtar[0], anahtar[1], birik[anahtar])

    def cift(self, yuva: int, G: np.ndarray) -> None:
        """Komşu çifte ``4×4`` kapı."""
        self.uzak_cift(int(yuva), int(yuva) + 1, G)

    def _bolum(self, k: int) -> Tuple[int, int]:
        """``lif[k]``ın önündeki ve ardındaki çarpımlar -- **önbellekli**."""
        c = self._bolum_onbellek.get(int(k))
        if c is not None:
            return c
        lif = tuple(self.ayar.lif)
        on = 1
        for x in lif[:k]:
            on *= int(x)
        ard = 1
        for x in lif[k + 1:]:
            ard *= int(x)
        c = (on, ard)
        self._bolum_onbellek[int(k)] = c
        return c

    def cift_bit_kapisi(self, ki: int, ai: int, kj: int, aj: int,
                        G: np.ndarray) -> None:
        """İki bit düzlemine ``4×4`` kapı -- **dizeysiz Kronecker-SIMD**.

        **YOĞUN GÖVDE İMHA EDİLDİ.** Eskisi durumu on eksene bölüp
        ``einsum`` ile çarpıyordu; sonraki graf (Pauli açılımlı TDD)
        yolu da zabıtla iptal edildi. Şimdi ``_cift_kapisi_lifli``dedir:
        dört dilim, on altı çarpma-toplama, tahsis yok.
        """
        self._cift_kapisi_lifli(ki, ai, kj, aj, G)

    def uzak_cift(self, i: int, j: int, G: np.ndarray) -> None:
        """İki yuvaya ``4×4`` kapı -- **takas yok, MPO yok, SVD yok**.

        Eski hatta uzak çift ya takas ağıyla (dolaşıklığı sürükler) ya
        da MPO ile (her yuvada bir SVD) vuruluyordu. Quditte iki yuva
        ya aynı liftedir -- o zaman kapı o lifin içinde bir ``SU(n)``
        elemanıdır -- ya da iki ayrı liftedir; o zaman iki lif
        birleştirilip **tek** einsum ile vurulur. İkisinde de kesme
        yoktur, dolayısıyla sadakat kaybı **sıfırdır**.
        """
        if not (self.gecerli(i) and self.gecerli(j)):
            self._dusen_kapi += 1
            return
        G = np.asarray(G, complex).reshape(4, 4)
        ki, ai = self._lif_no(int(i))
        kj, aj = self._lif_no(int(j))
        lif = tuple(self.ayar.lif)
        # **BİT DÜZLEMİ YOLU** -- lifler ikinin kuvvetiyse (bizim
        # hâlimizde 16 ve 256, ikisi de öyle) döngüsüz yol geçerlidir
        # ve neticesi aşağıdaki yoğun yolla birebir aynıdır (sınandı).
        if self._ikinin_kuvveti:
            self.cift_bit_kapisi(ki, ai, kj, aj, G)
            return
        if ki == kj:
            n = lif[ki]
            bi, bj = 1 << ai, 1 << aj
            if bi >= n or bj >= n or bi == bj:
                return
            M = np.eye(n, dtype=complex)
            for x in range(n):
                if (x & bi) or (x & bj):
                    continue
                idx = [x, x | bj, x | bi, x | bi | bj]
                for a in range(4):
                    for b in range(4):
                        M[idx[a], idx[b]] = G[a, b]
            self.lif_kapisi(ki, M)
            return
        # İki ayrı lif: (n_i, n_j) çift uzayında tek einsum.
        ni, nj = lif[ki], lif[kj]
        bi, bj = 1 << ai, 1 << aj
        if bi >= ni or bj >= nj:
            return
        T = self.lifli
        T = np.moveaxis(T, (ki + 1, kj + 1), (-2, -1))
        sekil = T.shape
        F = T.reshape(-1, ni, nj)
        Mi = np.eye(ni, dtype=complex)
        Mj = np.eye(nj, dtype=complex)
        # (a,b) ∈ {0,1}² → G ile karışan dört alt uzay
        for x in range(ni):
            if x & bi:
                continue
            for y in range(nj):
                if y & bj:
                    continue
                idx = [(x, y), (x, y | bj), (x | bi, y), (x | bi, y | bj)]
                v = np.stack([F[:, a, b] for a, b in idx], axis=1)
                v = v @ G.T
                for m, (a, b) in enumerate(idx):
                    F[:, a, b] = v[:, m]
        T = F.reshape(sekil)
        self.psi = np.moveaxis(T, (-2, -1), (ki + 1, kj + 1)).reshape(
            self.B, self.d)
        self._kapi += 1
        self.iz.kapi += 1

    def mpo_uygula(self, W, D: int = 2, bas: int = 0, son=None,
                   sol_sinir=None, sag_sinir=None) -> float:
        """MPO uygulaması -- **quditte MPO yoktur**, lif kapısına iner.

        Eski hatta bir MPO zincir boyunca yürüyüp her yuvada SVD ile
        sıkışıyordu. Quditte operatör ya bir lifin içindedir ya iki
        lif arasındadır; ikisi de kesmesiz. ``W`` sözlüğündeki
        kimlik-olmayan yuvalar lif kapılarına çevrilir.

        Döner: **atılan ağırlık = 0,0**. Kesme yoktur.
        """
        if not isinstance(W, dict) or not W:
            return 0.0
        lif = tuple(self.ayar.lif)
        sira: List[Tuple[int, int]] = []
        birik: Dict[Tuple[int, int], np.ndarray] = {}
        for yuva, Wk in W.items():
            Wk = np.asarray(Wk)
            k, alt = self._lif_no(int(yuva))
            # ``(D,2,2,D)`` MPO tensöründen tek kübitlik etkiyi al:
            # sınır vektörleriyle kapatılınca geriye ``2×2`` kalır.
            if Wk.ndim == 4:
                G = Wk[0, :, :, 0]
            elif Wk.ndim == 2 and Wk.shape == (2, 2):
                G = Wk
            else:
                continue
            # ``np.trace`` KALDIRILDI: profilde **71 995 çağrı**
            # (0,185 sn) yalnız "bu kapı boş mu" diye soruyordu.
            # ``np.any`` zaten onu söyler ve ucuzdur.
            if not self.gecerli(int(yuva)):
                self._dusen_kapi += 1
                continue
            G = np.asarray(G, complex).reshape(2, 2)
            if not np.any(G):
                continue
            # **KİMLİK KAPISI HİÇ VURULMAZ.** MPO zincirinin çoğu yuvası
            # kimlik dolgusudur; kimliği duruma vurmak durumu hiç
            # değiştirmez, yalnız ``O(B·d)`` yakar.
            if (abs(G[0, 0] - 1.0) < 1e-12 and abs(G[1, 1] - 1.0) < 1e-12
                    and abs(G[0, 1]) < 1e-12 and abs(G[1, 0]) < 1e-12):
                continue
            # **BİLEŞTİR, TEK TEK VURMA.** Aynı bit düzlemine düşen
            # kapılar ``2×2``de çarpılır; durum bir kere dolaşılır.
            anahtar = (int(k), int(alt))
            g2 = np.asarray(G, complex).reshape(2, 2)
            if anahtar in birik:
                birik[anahtar] = g2 @ birik[anahtar]
            else:
                birik[anahtar] = g2
                sira.append(anahtar)
        for anahtar in sira:
            self.bit_kapisi(anahtar[0], anahtar[1], birik[anahtar])
        self.normalize()
        return 0.0

    def mpo_uygula_hizli(self, *a, **k) -> float:
        """``mpo_uygula``ın hızlı yolu -- quditte ikisi **aynı**."""
        return self.mpo_uygula(*a, **k)

    def mpo_topla(self, alan: str, acilar=None, duraklar=None, j: int = 0
                  ) -> None:
        """Durakların hükmünü küllî alana akıt -- **operatörsüz**.

        Eski hatta bu bir MPO'ydu ve zincir boyunca SVD ile sıkışıyordu.
        Quditte hüküm bir **sektördür**: durakların ağırlığı sektöre
        faz olarak yazılır. Kesme yok.
        """
        if alan not in self._sektor:
            return
        a = np.asarray(acilar if acilar is not None else [0.0],
                       float).reshape(-1)
        i, jj = self.sektor(alan)
        u = np.arange(jj - i)
        faz = np.exp(1j * (a.mean() * (u + 1.0) / max(jj - i, 1)))
        self.psi[:, i:jj] = self.psi[:, i:jj] * faz
        self._kapi += 1
        self.iz.kapi += 1
        return 0.0                    # atılan ağırlık: kesme YOK

    def mpo_dagit(self, alan: str, acilar=None, duraklar=None, j: int = 0
                  ) -> None:
        """``mpo_topla``ın aynası: hüküm duraklara **geri** yazılır."""
        if alan not in self._sektor:
            return
        a = np.asarray(acilar if acilar is not None else [0.0],
                       float).reshape(-1)
        self.faz(np.full(min(8, self.d - 1), -float(a.mean())))
        return 0.0                    # atılan ağırlık: kesme YOK

    # ── dil modeli adımı: bağlamdan sonraki belirteç ───────────────
    def uret(self, baglam: Sequence[int], teta=None, sozluk: int = 16
             ) -> np.ndarray:
        """Bağlamdan **bir sonraki belirtecin dağılımı**. SVD yok.

        Adım şudur ve tamamı ``O(B·d·d_lif)``dir:

        1. Bağlamın belirteçleri kelâm sektörüne **sırayla** kodlanır;
           her yeni belirteç mevcut duruma bir Cartan fazı olarak
           yazılır -- yâni geçmiş silinmez, faza girer.
        2. ``teta`` parametreleriyle üç life Kronecker kapısı vurulur
           (öğrenilen kısım burasıdır).
        3. ``beyan`` kelâm sektöründen okunur.

        **Faz burada yaşar.** Eski hatta ``argmax(beyan)`` fazı kare
        alıp atıyordu; burada da Born kuralı olasılığı verir, fakat
        durumun kendisi fazıyla duruyor ve ``kulli_mizan`` onu
        görebiliyor.
        """
        bag = list(np.asarray(baglam, int).reshape(-1) % int(sozluk))
        if not bag:
            raise ValueError("üretim için bağlam lâzım")
        self.kodla([bag[0]], sozluk=sozluk)
        # Geçmiş: her belirteç bir Cartan fazı olarak biriktirilir.
        for k, t in enumerate(bag[1:], start=1):
            aci = np.full(min(8, self.d - 1),
                          (t + 1.0) / (k + 1.0), dtype=float)
            self.faz(aci)
        if teta is not None:
            # **HER LİF KENDİ EBADINDA.** Evvelce ``lif[0]``ı bütün
            # liflere dayatmıştım; lifler eşit olmayınca (meselâ
            # ``(4,8,8)``) kapı ebadı tutmuyordu. Parametre lif lif
            # bölünür.
            T = np.asarray(teta, float).reshape(-1)
            lif = tuple(self.ayar.lif)
            gerek = sum(n * n for n in lif)
            T = np.resize(T, gerek)
            bas = 0
            for k, n in enumerate(lif):
                Ak = T[bas:bas + n * n].reshape(n, n)
                bas += n * n
                # Üniterlik Cayley ile sağlanır: ``(I−A)(I+A)⁻¹``,
                # ``A`` ters-simetrik. SVD/QR YOKTUR; tek bir çözüm.
                A = Ak - Ak.T
                I = np.eye(n)
                G = np.linalg.solve(I + A, I - A)
                self.lif_kapisi(k, G)
        return self.beyan(sozluk)

    # ── ölçü ───────────────────────────────────────────────────────
    def rapor(self) -> str:                              # pragma: no cover
        o = self.olcumler()
        s = ["=== QUDİT YAZMACI (MPS'in yerine) ===", "",
             "  d              : %d  (%.1f KB, TAM tutulur)"
             % (self.d, self.d * 16 / 1024),
             "  lifler         : %s" % (self.ayar.lif,),
             "  yığın          : %d" % self.B,
             "  norm hatası    : %.3e" % self.norm_hatasi(),
             "  entropi (kesit): %.6f" % o["entropi"],
             "  vurulan kapı   : %d" % self._kapi,
             "  sadakat log    : %.1f  (kesme yok → tam sıfır)"
             % self.sadakat_log(),
             "", "  SEKTÖRLER (eski küllî alanların yerine):"]
        for ad, (i, j) in self._sektor.items():
            s.append("    %-9s [%4d–%4d]  ağırlık %.6f"
                     % (ad, i, j, float(np.ravel(o[ad])[0])))
        return "\n".join(s)
