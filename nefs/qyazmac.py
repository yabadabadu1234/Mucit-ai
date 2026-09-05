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

import numpy as np

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
    #: Satır başına yerel hüküm yuvası (eski ``QAyar.yerel_kubit``).
    yerel_kubit: int = 1
    tip: object = np.complex128
    tohum: int = 0

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
                 n_satir: int = 2, satir_kubiti: int = 4) -> None:
        self.ayar = ayar or QuditAyar()
        a = self.ayar
        self._n_satir = int(n_satir)
        self._satir_kubiti = int(satir_kubiti)
        r = np.random.default_rng(int(a.tohum))
        self.B = int(a.yigin)
        self.d = int(a.d)
        # Başlangıç: **düzgün süperpozisyon**, keyfî bir gürültü değil.
        # Aynı tohum daima aynı durumu verir (stokastiklik yasak).
        self.psi = np.full((self.B, self.d), 1.0 / np.sqrt(self.d),
                           dtype=a.tip)
        self._sadakat_log = 0.0
        self._kapi = 0
        self.iz = Iz()
        # Bağ tavanı ve kanoniklik MPS mefhumlarıdır; quditte **yoktur**.
        # İmza uyumu için duruyorlar ve okunduklarında bunu söylerler.
        self.bag_tavan = 0
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
        return self._n_satir * (self._satir_kubiti
                                + int(self.ayar.yerel_kubit)) + self.d

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

    def blok_dagilimi(self, bas: int, kac: int) -> np.ndarray:
        """``bas``tan ``kac`` yuvanın ortak dağılımı -- lif üstünde tam."""
        k, alt = self._lif_no(int(bas))
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

    def mera_kur(self, *a, **k) -> None:
        self.iz.not_dus("mera_kur", "qudit lif üniterleri kullanılır")

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
        """``k``ıncı life ``G`` uygula -- Kronecker, ``O(B·d·d_k)``.

        Yoğun ``d×d`` dizey **kurulmaz**. Bu, ``nefs/hizli.py``nin
        birinci tedbiridir ve orada ölçüldü: yoğunla fark ``2,3e−13``,
        duvar saati ``289×``.
        """
        lif = tuple(self.ayar.lif)
        if not 0 <= int(k) < len(lif):
            raise ValueError("lif %d yok; %d lif var" % (k, len(lif)))
        G = np.asarray(G)
        if G.shape != (lif[k], lif[k]):
            raise ValueError("kapı %s olmalı, %s verildi"
                             % ((lif[k], lif[k]), G.shape))
        T = self.lifli
        T = np.moveaxis(T, k + 1, -1)
        sekil = T.shape
        T = (T.reshape(-1, lif[k]) @ G.T).reshape(sekil)
        self.psi = np.moveaxis(T, -1, k + 1).reshape(self.B, self.d)
        self._kapi += 1

    def faz(self, teta) -> None:
        """Cartan köşegeni: ``|Ψ⟩ ← e^{−iθ·h} ⊙ |Ψ⟩``. ``O(d)``.

        Matris çarpımı yoktur; zabıtın üçüncü tedbiri budur
        (``O(d²) → O(d)``, 4096×).
        """
        from .hizli import faz_cevir
        self.psi = faz_cevir(self.psi, teta)
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
        i, j = self.sektor(ad)
        v = np.sum(np.abs(self.psi[:, i:j]) ** 2, axis=1)
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
        fakat faz **atılmaz**: ``tabakali_mizan`` onu ayrıca görür.
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
        """Eski yuva indisini ``(lif, alt)`` adresine çevir.

        Eski zincirde ``veri(i,j)``, ``yerel(i)``, ``kulli(ad,j)`` hep
        tek bir tam sayı yuvaydı. Quditte satırlar ayrı liflerdir,
        hüküm alanları ise **hüküm lifinin sektörleridir**.
        """
        y = int(yuva)
        ns, sk = self._n_satir, self._satir_kubiti
        satir_yuva = sk + int(self.ayar.yerel_kubit)
        if y < ns * satir_yuva:
            return (y // satir_yuva, y % satir_yuva)
        return (ns, y - ns * satir_yuva)                 # hüküm lifi

    def veri(self, i: int, j: int) -> int:
        return int(i) * (self._satir_kubiti + int(self.ayar.yerel_kubit)) + int(j)

    def yerel(self, i: int) -> int:
        return self.veri(i, self._satir_kubiti)

    def kulli(self, ad: str, j: int = 0) -> int:
        """Küllî alanın ``j``inci yuvası -- artık **sektör** indisi."""
        i, _ = self.sektor(ad)
        return self._n_satir * (self._satir_kubiti
                                + int(self.ayar.yerel_kubit)) + i + int(j)

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
        """Tek yuvaya ``2×2`` kapı -- lif içine gömülerek."""
        k, alt = self._lif_no(yuva)
        n = self.ayar.lif[k]
        self.lif_kapisi(k, self._gomulu(n, alt, G))

    def tek_yigin(self, yuvalar: Sequence[int], G) -> None:
        """``m`` yuvaya ``m`` kapı. Aynı life düşenler **bileşir**."""
        G = np.asarray(G)
        if G.ndim == 2:
            G = np.broadcast_to(G, (len(yuvalar), 2, 2))
        birik: Dict[int, np.ndarray] = {}
        for y, g in zip(yuvalar, G):
            k, alt = self._lif_no(int(y))
            n = self.ayar.lif[k]
            M = self._gomulu(n, alt, g)
            birik[k] = M if k not in birik else M @ birik[k]
        for k, M in birik.items():
            self.lif_kapisi(k, M)

    def cift(self, yuva: int, G: np.ndarray) -> None:
        """Komşu çifte ``4×4`` kapı."""
        self.uzak_cift(int(yuva), int(yuva) + 1, G)

    def uzak_cift(self, i: int, j: int, G: np.ndarray) -> None:
        """İki yuvaya ``4×4`` kapı -- **takas yok, MPO yok, SVD yok**.

        Eski hatta uzak çift ya takas ağıyla (dolaşıklığı sürükler) ya
        da MPO ile (her yuvada bir SVD) vuruluyordu. Quditte iki yuva
        ya aynı liftedir -- o zaman kapı o lifin içinde bir ``SU(n)``
        elemanıdır -- ya da iki ayrı liftedir; o zaman iki lif
        birleştirilip **tek** einsum ile vurulur. İkisinde de kesme
        yoktur, dolayısıyla sadakat kaybı **sıfırdır**.
        """
        G = np.asarray(G, complex).reshape(4, 4)
        ki, ai = self._lif_no(int(i))
        kj, aj = self._lif_no(int(j))
        lif = tuple(self.ayar.lif)
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
        for yuva, Wk in W.items():
            Wk = np.asarray(Wk)
            k, alt = self._lif_no(int(yuva))
            n = lif[k]
            # ``(D,2,2,D)`` MPO tensöründen tek kübitlik etkiyi al:
            # sınır vektörleriyle kapatılınca geriye ``2×2`` kalır.
            if Wk.ndim == 4:
                G = Wk[0, :, :, 0]
            elif Wk.ndim == 2 and Wk.shape == (2, 2):
                G = Wk
            else:
                continue
            iz = np.trace(np.asarray(G, complex))
            if abs(iz) < 1e-30 and not np.any(G):
                continue
            self.lif_kapisi(k, self._gomulu(n, alt, G))
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
        durumun kendisi fazıyla duruyor ve ``tabakali_mizan`` onu
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
