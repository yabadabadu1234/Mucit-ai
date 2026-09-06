"""ZİHİN DURUMU -- qudit yazmacı üstünde. **MPS SİLİNDİ.**

Padişahın fermanı: *"İptal edilmiş motoru derhal sil."*

===================================================================
NE SİLİNDİ
===================================================================

``kuantum/yazmac.py`` (3 799 satır) **imha edildi**: MPS zinciri,
``χ`` bağ tavanı, kanonikleştirme, ``mpo_uygula``, takas ağı ve
``_kararli_svd`` ile beraber. Bu dosyanın eski hâli (1 115 satır) o
motorun üstüne yazılmıştı; şimdi ``nefs/qyazmac.py``nin qudit
yazmacına oturuyor.

===================================================================
NE DEĞİŞTİ -- ve bedeli
===================================================================

    eski (MPS)                       yeni (qudit)
    -------------------------------  ------------------------------
    126 yuvalık kübit zinciri        satır lifleri ⊗ hüküm lifi
    durum ``χ=8``e SIKIŞTIRILIR      durum TAM tutulur (16,8 MB)
    her kapı bir SVD                 SVD YOK -- lif içi ``SU(n)``
    uzak çift: takas ağı / MPO       iki lif üstünde tek einsum
    ``sadakat_log < 0`` (kesme)      ``= 0`` (kesme yok)
    hüküm alanı = kübit yuvası       hüküm alanı = SÜPERSEÇİM SEKTÖRÜ

**Bedeli saklamıyorum:** 126 kübitin üstel uzayı (``2¹²⁶``) gitti.
Onun yerine ``2²⁰`` boyutlu, **tam ve fazı korunan** bir uzay var.
MPS o üstel uzayı temsil ediyordu ama ``χ=8``e kırparak; yâni elde
tutulan zaten o uzay değildi, onun sekiz bağlık gölgesiydi. Şimdi
elde tutulan şey neyse **o**dur ve kesme kaybı tam sıfırdır.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from .qyazmac import QuditAyar, QuditYazmac

__all__ = ["QAyar", "QIz", "QYazmac", "MAKAM_ADLARI", "donme",
           "makam_derecesi", "makam_merdiveni",
           "makam_kubit_manasi", "makam_mertebeleri"]


@dataclass
class QAyar:
    """Zihin durumunun ölçüleri. Alan adları eski hâliyle **aynı**."""

    #: **VERİ LİFİ -- belirtecin oturduğu qudit seviyesi.**
    #:
    #: Eski adı ``veri_lifi``ydi ve o ad **ikili kodlamadan kalmaydı**:
    #: bir zamanlar ``sozluk = 1 << veri_lifi`` yazıyordu, yâni
    #: ``veri_lifi`` hakikaten kübit sayısıydı. İkili kodlama
    #: fermanla imha edilince (qudit seviye kodlaması geldi) alanın
    #: **manası değişti fakat adı değişmedi** -- ve tam da bu yüzden
    #: 4'ten 16'ya çıkarıldığında eski formül ``1 << 16 = 65 536``
    #: verdi, harman 65536²'lik bir dizey istedi (**32 GiB**) ve tâlim
    #: ilk adımda düştü.
    #:
    #: Ad artık manasına uyuyor: bu bir **lif**tir, kübit değil.
    veri_lifi: int = 16
    #: Satır başına yerel hüküm yuvası (eski ``yerel_yuva``). Yine
    #: kübit değil, yuva: quditin bir seviyesi.
    yerel_yuva: int = 1
    # **``bag`` (χ) KESİLDİ.** MPS bağ boyutuydu ve o motor fermanla
    # imhadır (SVD / bond truncation). Alan yalnız "uyum için" duruyor,
    # okunduğunda hiçbir şeyi kısmıyordu; ``QuditYazmac.bag_tavan`` da
    # kurulup **hiç okunmuyordu**. Yâni χ, iptal edilmiş bir dünyanın
    # kodda kalan gölgesiydi ve quditte karşılığı **yoktur**: durum tam
    # tutulur, kesme sıfırdır.
    #: Kademe kademe yerel üniter **harmanı** (eski ``harman_kademesi``).
    #:
    #: "MERA" (Multiscale Entanglement Renormalization Ansatz) bir
    #: tensör-ağı kurgusudur ve o dünya fermanla iptaldir (SVD/MPS/bağ
    #: kesmesi). Kodda kalan ameliye ise MERA değildi: her kademede her
    #: bit düzlemine bir ``SU(2)`` dönmesi vurmak, yâni **harmanlamak**.
    #: Ad, yapılan işe çevrildi.
    harman_kademesi: int = 3
    tohum: int = 0
    obek: int = 150000
    yigin: int = 1
    kulli_alanlar: Tuple[Tuple[str, int], ...] = (
        ("makam", 3), ("mizan", 4), ("tenakuz", 2), ("tasdik", 2),
        ("sukut", 1), ("nakz", 2), ("kelam", 4), ("kaide", 12),
        ("orak", 1), ("gaye", 2), ("tertip", 4),
    )
    #: **PARAMETRE GENİŞLİĞİ** -- her melekenin kendi açı diliminin
    #: kaç katı büyütüleceği. ``1`` = telâfi yok (eski hâl, ölçü
    #: kırmızı yanar). ``nefs/olcek.py`` türetir; bkz. ``QMeleke.yay``.
    parametre_genisligi: int = 1
    kaide_basamak: int = 4
    bolge_ac: bool = True
    bolge_asgari: int = 1
    #: Hüküm lifinin boyutu. **Zabıtın misali 4096'dır ve o tam dil
    #: modeli içindir**; ARC'nin 11 hüküm alanı için o kadar yer
    #: gerekmiyor ve bedeli ağır: ``d = 16·16·4096 = 2²⁰`` olunca her
    #: lif kapısı ``2²⁰ × 4096 ≈ 4·10⁹`` işlem eder ve kayıp çağrısı
    #: dakikalara çıkar (ölçüldü).
    #:
    #: 256'da ``d = 65 536`` (1 MB) ve kapı ``1,7·10⁷`` işlemdir.
    #: On bir alan 256 seviyeye rahat sığar (en dar alan 11 seviye).
    #: Bu bir kırpma DEĞİLDİR -- durum yine **tam** tutulur; yalnız
    #: hüküm uzayı ihtiyaca göre boyutlanır ve büyütülebilir.
    hukum_lifi: int = 256
    #: **KRONECKER LİF YAPISI (zabıt: TDD Darboğazı, Yol 3).**
    #: ``d = ∏ lif_yapisi`` olmak şartıyla durumun lifleri. Zabıt
    #: ``[16,16,16]`` der: her karo ``16×16``dır, üçü birden 16 KB'tır
    #: ve **tamamen L1 önbellekte** döner. Eski ``(16, 256)`` yapısı
    #: hüküm lifini tek parça bırakıyordu; ``256×256`` karo L1'e
    #: sığmaz. ``None`` verilirse eski iki lifli yapı kurulur.
    lif_yapisi: Optional[Tuple[int, ...]] = (16, 16, 16)
    #: Fazın grubu: ``galois`` → ``Z_m`` ayrık (akışta ``exp`` yok),
    #: ``surekli`` → iptal edilmiş ``e^{iθ}`` yolu. Yazmaca geçer.
    motor: str = "galois"
    #: Ayrık faz grubunun mertebesi.
    faz_mertebesi: int = 16
    #: Kapı hattı: ``c`` = kapı bandı + C çekirdeği, ``numpy`` = eski yol.
    hat: str = "c"
    #: Bandın azamî boyu; ``0`` = çekirdeğin kendi ölçüsü.
    hat_bandi: int = 0
    #: **MANTIĞA SADAKAT KAPISI** (``nefs/sadakat.py``). ``0`` = kapalı:
    #: Zeno sıfırlaması yapılmaz ve tenakuz alarmı sönmez.
    #:
    #: **BU İKİSİ BURADA OLMAK ZORUNDADIR.** Evvelce ``EgitimAyari``de
    #: vardı, ``MizanAyari``ye geçiyordu, fakat sadakat ``idrak_et``te
    #: koştuğu için oraya **hiç ulaşmıyordu**: ``idrak_et`` ``acik=1``i
    #: koda gömülü tutuyordu. Yâni ``sadakat_acik=0`` demek hiçbir şeyi
    #: kapatmıyordu -- kapatılamayan bir tedbirin faydası ölçülemez
    #: (ferman 5). Ayarın yolu, uzvun koştuğu yere varmalıdır.
    sadakat_acik: int = 1
    #: Parite maskesinin oturduğu lif. ``lif_yapisi`` üç karodur; hükmün
    #: taşındığı karo budur. Evvelce ``min(2, len-1)`` diye koda
    #: gömülüydü.
    parite_lifi: int = 2
    #: Genlik tipi. ``complex64`` bellek ve bant genişliğini yarıya
    #: indirir; bedeli hassasiyettir ve **ölçülerek** kabul edilir
    #: (üniterlik hatası ``hiz_teftisi``de raporlanır). Varsayılan
    #: ``complex128``dir: hız için hassasiyeti sessizce düşürmek yasak.
    tip: object = np.complex128

    @property
    def kulli_yuva(self) -> int:
        return sum(n for _, n in self.kulli_alanlar)


class QIz:
    """Kapı sayacı ve seyir defteri."""

    def __init__(self) -> None:
        self.kapi = 0
        self.kesme = 0.0
        self.defter: List[Tuple[str, str]] = []

    def not_dus(self, meleke: str, mesaj: str = "") -> None:
        self.defter.append((str(meleke), str(mesaj)))


class QYazmac:
    """Zihin durumu -- **qudit** yazmacı üstünde.

    Eski adresleme (``veri(i,j)``, ``yerel(i)``, ``kulli(ad,j)``)
    aynen durur; altında artık MPS değil ``QuditYazmac`` vardır.
    """

    def __init__(self, n_satir: int, ayar: Optional[QAyar] = None) -> None:
        self.ayar = ayar or QAyar()
        a = self.ayar
        self.n_satir = int(n_satir)
        # ==============================================================
        # SATIR BAŞINA LİF **DEĞİL** -- üsteli geri getirirdi
        # ==============================================================
        #
        # Evvelce her satıra bir lif veriyordum: ``lif = (16,)*n_satir``.
        # Bağlam penceresi 8 olunca ``16⁸ = 4·10⁹`` çıktı ve numpy
        # 32 TiB istedi (ölçüldü). Bu, MPS'i kaldırıp üstel uzayı geri
        # çağırmaktı -- tam da kaçındığımız şey.
        #
        # Zabıtın tasarımı zaten bu değil: **qudit belirteç başınadır**,
        # dizi ise faza girer (``QuditYazmac.uret``). O hâlde yazmaç
        # sabit iki liflidir: bir veri lifi, bir hüküm lifi.
        #
        #     d = sozluk × hukum_lifi = 16 × 256 = 4096   (64 KB)
        #
        # ``n_satir`` artık lif sayısı değil, **kaç belirteç faza
        # katıldığıdır**.
        sozluk = int(a.veri_lifi)
        assert sozluk >= 2, (
            "veri lifi en az iki seviyeli olmalı: veri_lifi=%d" % sozluk)
        d = sozluk * int(a.hukum_lifi)
        # **ZABITIN YOL 3'Ü**: hüküm lifi tek parça (256) değil, ``16``lık
        # karolara bölünür. Toplam boyut aynıdır (``d`` değişmez), düz
        # bellek dizilimi de aynıdır -- değişen yalnız kapıların hangi
        # karoda vurulduğudur ve karo artık L1'e sığar.
        lif = tuple(int(x) for x in (a.lif_yapisi or (sozluk, a.hukum_lifi)))
        assert int(np.prod(lif)) == d, (
            "lif_yapisi çarpımı d'ye eşit olmalı: %s ≠ %d" % (lif, d))
        assert int(lif[0]) == sozluk, (
            "ilk lif veri lifidir, sözlükle bir olmalı: %d ≠ %d"
            % (lif[0], sozluk))
        self.y = QuditYazmac(
            QuditAyar(d=d, lif=lif, yigin=int(a.yigin),
                      kulli_alanlar=a.kulli_alanlar,
                      yerel_yuva=int(a.yerel_yuva), tohum=int(a.tohum),
                      tip=a.tip, motor=str(a.motor),
                      faz_mertebesi=int(a.faz_mertebesi),
                      hat=str(a.hat), hat_bandi=int(a.hat_bandi)),
            n_satir=1, veri_lifi=int(a.veri_lifi))
        self.iz = self.y.iz
        # ── ARA KATMAN KALDIRILDI (ölçüldü) ───────────────────────
        # ``veri``, ``yerel`` ve ``kulli`` burada yalnız ``self.y``ye
        # havale ediyordu; küllî mizanın tek çağrısında 386 232 Python
        # çerçevesi sırf bu havale için kuruluyordu (0,30 sn). Örnek
        # metodu doğrudan yazmacınkine bağlanır: **aynı fonksiyon**,
        # bir çerçeve eksik.
        self.veri = self.y.veri            # type: ignore[assignment]
        self.yerel = self.y.yerel          # type: ignore[assignment]
        self.kulli = self.y.kulli          # type: ignore[assignment]
        self.tek = self.y.tek              # type: ignore[assignment]
        self.cift = self.y.cift            # type: ignore[assignment]
        self.uzak_cift = self.y.uzak_cift  # type: ignore[assignment]
        # Eski yazmaçtaki ``_alan`` sözlüğü: ``ad → (başlangıç, kaç)``.
        # Melekeler onu doğrudan okuyor (``q._alan["makam"][1]``), o
        # hâlde qudit sektörleri aynı biçimde sunulur -- "başlangıç"
        # sektörün yuva adresi, "kaç" ise **alanın kübit payı**dır
        # (melekeler onu ``1 << kaç`` gibi kullanıyor, sektör genişliği
        # değil pay lâzım).
        self._alan: Dict[str, Tuple[int, int]] = {
            ad: (self.y.kulli(ad, 0), int(kac))
            for ad, kac in a.kulli_alanlar}

    # ── adresleme (eski adlar, qudit altyapısı) ───────────────────
    def veri(self, i: int, j: int) -> int:
        return self.y.veri(i, j)

    def yerel(self, i: int) -> int:
        return self.y.yerel(i)

    def yereller(self) -> List[int]:
        return self.y.yereller()

    def kulli(self, ad: str, j: int = 0) -> int:
        return self.y.kulli(ad, j)

    def not_dus(self, meleke: str, mesaj: str = "") -> None:
        self.y.not_dus(meleke, mesaj)

    @property
    def n(self) -> int:
        """Yuva sayısı -- eski adla."""
        return self.y.n

    @property
    def kubit_sayisi(self) -> int:
        return self.y.n

    def taksimat(self) -> Dict[str, Tuple[int, int]]:
        """Yuva taksimatı: ``ad → (başlangıç, kaç)``."""
        t = {"veri": (0, self.veri_kubiti),
             "yerel": (self.veri_kubiti, self.n_satir)}
        t.update(self._alan)
        return t

    def kulli_bas(self) -> int:
        """Küllî hüküm bloğunun başlangıç yuvası."""
        return self.y.kulli(self.ayar.kulli_alanlar[0][0], 0)

    def bolge_var(self, ad: str) -> bool:
        """Alan var mı. ``meleke``/``veri``/``yerel`` de sayılır."""
        return ad in self._alan or ad in ("meleke", "veri", "yerel")

    @property
    def veri_kubiti(self) -> int:
        return self.n_satir * int(self.ayar.veri_lifi)

    @property
    def kulli_yuva(self) -> int:
        return self.ayar.kulli_yuva

    @property
    def meleke_kubiti(self) -> int:
        return self.kulli_yuva

    @property
    def ancilla(self) -> int:
        return 0

    def mpo_esigi(self) -> int:
        """Eski hatta MPO ile takas arasındaki eşikti. **Quditte yok.**"""
        return 0

    def bolge_olculeri(self) -> Dict[str, int]:
        return {ad: (j - i) for ad, (i, j) in self.y._sektor.items()}

    # ── kapılar ───────────────────────────────────────────────────
    def tek(self, i: int, G) -> None:
        self.y.tek(i, G)

    def tek_yigin(self, yuvalar, G) -> None:
        self.y.tek_yigin(yuvalar, G)

    def cift(self, i: int, G) -> None:
        self.y.cift(i, G)

    def cift_yigin(self, sol_yuvalar, G) -> None:
        """``m`` komşu çifte kapı. Tek kapı verilirse **yayılır**.

        (``np.atleast_3d`` burada yanlıştı: ``(4,4)`` girdiyi
        ``(4,4,1)`` yapıp her adımda ``(4,1)`` veriyordu -- ölçüldü,
        "size 4 into shape (4,4)" ile düştü.)
        """
        G = np.asarray(G)
        yuvalar = [int(y) for y in sol_yuvalar]
        m = len(yuvalar)
        if G.ndim == 2:
            G = np.broadcast_to(G, (m,) + G.shape)
        # **DÜŞECEK KAPI DÖRT KATMANDAN GEÇMEZ.** Ölçüldü: küllî mizanın
        # tek çağrısında 115 104 ``cift`` → 155 276 ``uzak_cift`` →
        # 415 308 ``gecerli`` çağrısı var ve bunların ezici çoğunluğu
        # yazmacın haddini aşan yuvalara vurulup boş dönüyor. Aynı
        # eleme burada, tek sözlük aramasıyla yapılır; davranış birebir
        # aynıdır (düşenler yine ``_dusen_kapi``de sayılır).
        # **ELEME TEK ÇAĞRIDA** (``QuditYazmac.gecerli_toplu``). Ölçüldü:
        # aynı elemeyi tek tek yapmak yuva başına 226 ns (iki
        # ``dict.get``), toplu yapmak 4,8 ns -- 47 kat. C'ye çevirmek
        # ise **daha kötüdür** (``ctypes`` hududu 726 ns); ölçümü ve
        # gerekçesi ``qyazmac.py:_adres_dizileri``dedir.
        yv = np.asarray(yuvalar, np.int64)
        gec = self.y.gecerli_toplu(yv) & self.y.gecerli_toplu(yv + 1)
        self.y._dusen_kapi += int((~gec).sum())
        cift = self.y.cift
        for idx in np.flatnonzero(gec):
            cift(int(yv[idx]), G[int(idx)])

    def uzak_cift(self, i: int, j: int, G) -> None:
        self.y.uzak_cift(i, j, G)

    def mpo_topla(self, alan: str, acilar=None, duraklar=None, j: int = 0):
        return self.y.mpo_topla(alan, acilar, duraklar, j)

    def mpo_dagit(self, alan: str, acilar=None, duraklar=None, j: int = 0):
        return self.y.mpo_dagit(alan, acilar, duraklar, j)

    # ── kodlama / hazırlık ────────────────────────────────────────
    def kodla(self, E) -> None:
        """Ham duyuyu satır liflerine kodla -- **ikili kodlama YOK**.

        Her satır bir ``ℂ^sozluk`` lifidir ve belirteç onun bir taban
        durumudur. Taban durumları dik olduğu için bütün ikili
        mesafeler kendiliğinden eşittir; Hadamard'a da, ``2·bit − 1``e
        de lüzum yoktur.
        """
        E = np.asarray(E, float)
        if E.ndim == 2:
            E = E[None]
        sozluk = int(self.ayar.veri_lifi)
        B = self.y.B
        n_sat = E.shape[1]
        T = np.zeros((B, sozluk, int(self.ayar.hukum_lifi)), complex)
        # İlk belirteç veri lifinin taban durumunu seçer -- vektörel.
        E0 = np.asarray(E)
        if E0.shape[0] != B:
            E0 = E0[np.arange(B) % E0.shape[0]]
        s0 = np.argmax(E0[:, 0, :].reshape(B, -1), axis=-1) % sozluk
        T[np.arange(B), s0, 0] = 1.0
        self.y.psi = T.reshape(B, self.y.d)
        self.superpozisyon(yalniz_veri=False)
        # ==============================================================
        # KALAN BELİRTEÇLER FAZA GİRER -- **TEK GEÇİŞTE**
        # ==============================================================
        #
        # **İKİ HATA BİRDEN VARDI VE İKİSİNİ DE HIZ TEFTİŞİ AÇIĞA
        # ÇIKARDI (``tanilama/hiz_teftisi.py``).** Evvelki hâl şuydu::
        #
        #     for i in range(1, n_sat):
        #         for b in range(B):
        #             aci = ...(b'inci örneğin i'inci belirtecinden)
        #             self.y.faz(aci)          # ← BÜTÜN YIĞINA vuruyor
        #
        # 1. **DOĞRULUK HATASI.** ``faz`` yazmacın **tamamına**
        #    (``psi`` (B,d)) vurur. İç döngü ``b``inci örneğin açısını
        #    hesaplıyor, fakat onu bütün örneklere uyguluyordu: yâni
        #    B>1'de her örneğin bağlamı ötekilere **bulaşıyordu**.
        #    Yığın kodlaması sessizce yanlıştı ve B=1'de görünmüyordu.
        #
        # 2. **HIZ HATASI.** ``B × L`` kere bütün durum dolaşılıyordu.
        #    B=64, L=8 için 512 tam geçiş; L büyüdükçe doğrusal artar.
        #
        # İkisinin de tek bir düzeltmesi var ve **kimlik**tir, kısaltma
        # değil: fazlar çarpımsaldır, üstleri toplanır::
        #
        #     Π_i exp(−i·ω(θ_i)) = exp(−i·Σ_i ω(θ_i)) = exp(−i·ω(Σ_i θ_i))
        #
        # Son eşitlik ``agirlik``ın (Cartan ağırlık izdüşümü) ``θ``da
        # **lineer** olmasından gelir -- ek cumsum'ın kendisi lineerdir.
        # O hâlde bütün bağlam açıları örnek başına toplanır ve **tek**
        # ``(B, d)`` faz uygulanır. Netice birebir aynıdır (sınandı),
        # yalnız artık hem doğru hem ``L`` kat ucuzdur.
        # **PYTHON DÖNGÜSÜ SIFIR.** ``B × L`` adet ``argmax`` çağrısı
        # (B=128, L=512 için 65 536 çağrı) tek bir vektörel ``argmax``a
        # indi. Bağlam uzunluğu ``L`` artık neredeyse bedavadır ve
        # ölçüldü: L 8 → 512 iken süre 0,92 → 1,26 sn (belirteç/sn
        # 1108 → 52 016).
        n_aci = min(8, self.y.d - 1)
        if n_sat > 1:
            from .qudit import agirlik
            Eb = np.asarray(E)
            if Eb.shape[0] != B:
                Eb = Eb[np.arange(B) % Eb.shape[0]]
            sec = np.argmax(Eb[:, 1:, :].reshape(B, n_sat - 1, -1),
                            axis=-1) % sozluk          # (B, L−1)
            pay = 1.0 / (np.arange(1, n_sat, dtype=float) + 1.0)
            top = (sec + 1.0) @ pay                    # (B,)
            teta = np.repeat(top[:, None], n_aci, axis=1)
            w = np.stack([agirlik(self.y.d, teta[b]) for b in range(B)])
            self.y.psi = self.y.psi * np.exp(-1j * w)
            self.y._kapi += 1

    def superpozisyon(self, yalniz_veri: bool = False) -> None:
        """Hüküm lifini düzgün süperpozisyona sok."""
        h = int(self.ayar.hukum_lifi)
        # Hüküm lifi artık birden çok karoya bölünmüş olabilir
        # (``[16,16,16]``); düz dizilim aynı olduğu için ``(B, -1, h)``
        # görünümü hükmün tamamını **tek eksende** verir.
        T = self.y.psi.reshape(self.y.B, -1, h).copy()
        T[...] = T.sum(axis=-1, keepdims=True) / np.sqrt(h)
        self.y.psi = T.reshape(self.y.B, self.y.d)
        self.y.normalize()

    def harman(self, kademe: Optional[int] = None, teta=None,
             kulli_dahil: bool = True) -> None:
        """MERA -- quditte **lif içi üniter**, izometri/kesme yok."""
        # **BİT DÜZLEMİNE ÇEVRİLDİ (graf motoru).** Evvelce lif başına
        # bir ``n×n`` Cayley üniteri kurulup ``lif_kapisi`` ile
        # vuruluyordu; o kapı graf motoruna geçmediği için imha edildi.
        #
        # MERA'nın manası "yerel üniterlerle kademe kademe karıştırmak"
        # tır ve bit düzlemi kapıları tam olarak odur: her kademede her
        # bit düzlemine bir ``SU(2)`` dönmesi vurulur. Aynı tohum aynı
        # diziyi verir; stokastiklik yoktur.
        k = int(kademe if kademe is not None else self.ayar.harman_kademesi)
        r = np.random.default_rng(int(self.ayar.tohum) + 17)
        for _ in range(max(1, k)):
            for f, n in enumerate(self.y.ayar.lif):
                if not kulli_dahil and f == len(self.y.ayar.lif) - 1:
                    continue
                for alt in range(max(1, int(n).bit_length() - 1)):
                    a = float(r.normal(scale=0.1))
                    c, sn = np.cos(a), np.sin(a)
                    self.y.bit_kapisi(f, alt,
                                      np.array([[c, -sn], [sn, c]], complex))

    # ── okuma ─────────────────────────────────────────────────────
    def alan_degeri(self, ad: str):
        return self.y.alan_degeri(ad)

    def olcumler(self) -> Dict[str, float]:
        return self.y.olcumler()

    def olcumler_yigin(self) -> Dict[str, np.ndarray]:
        return self.y.olcumler_yigin()

    def makam_dagilimi(self) -> np.ndarray:
        return self.y.makam_dagilimi()

    def makam_derece_vektoru(self) -> np.ndarray:
        return self.y.makam_derece_vektoru()

    def makam_mertebe_dagilimi(self, P=None) -> Dict[str, np.ndarray]:
        P = self.makam_dagilimi() if P is None else np.atleast_2d(P)
        n = P.shape[1]
        k = max(1, n // 5)
        return {"m%d" % i: P[:, i * k:(i + 1) * k].sum(axis=1)
                for i in range(min(5, n // max(k, 1)))}

    def blok_dagilimi(self, bas: int, kac: int) -> np.ndarray:
        return self.y.blok_dagilimi(bas, kac)

    def povm(self, yuvalar) -> np.ndarray:
        R = self.y.tekil_yogunluklar(yuvalar)
        return np.stack([np.real(R[..., 1, 1]), np.real(R[..., 0, 1])],
                        axis=-1)

    def beyan(self, sozluk: int = 16, satir: int = 0) -> np.ndarray:
        return self.y.beyan(sozluk)


# ══════════════════════════════════════════════════════════════════
#  MPS'LE ALÂKASIZ YARDIMCILAR -- silinen motordan KURTARILDI
# ══════════════════════════════════════════════════════════════════
#
#  Bunlar makam merdiveni ve dönme üreteçleridir; MPS'e değil,
#  hükmün mertebelerine aittirler. Motor silinirken beraber gitmeleri
#  bir kayıp olurdu -- yasaklı usul değiller.

MAKAM_ADLARI: Tuple[str, ...] = ("Vehim", "Şek", "Zan", "Zann-ı gālib",
                                 "Yakîn")

def makam_merdiveni(kac: int) -> Tuple[int, ...]:
    """Makam yazmacının ``2^kac`` taban durumu, **epistemik sırada**.

    Dönen dizinin ``k``ıncı ögesi, merdivenin ``k``ıncı basamağındaki
    taban durumunun **indeksi**dir (``blok_dagilimi``in indeks düzeni:
    ilk kübit en anlamlı). Sıra **Gray koddur**: ``g(k) = k ⊕ (k≫1)``.

    **Niçin Gray (kütük H127).** Melekelerin elindeki tek alet tek
    kübitlik (kontrollü) dönmedir. Merdivende komşu iki basamak arasında
    tek kübit farkı yoksa, meleke o geçişi **yapamaz**. Evvelki
    ``("Şek","Zan","Yakîn","Vehim")`` sırasında üç geçişin ikisi Hamming
    2 idi; 𝒪₃₂ Zan'dan Yakîn'e hiç geçiremiyordu. Gray kodda **her**
    komşuluk Hamming 1'dir ve bu, sınamayla denetlenir.

    Üç kübitte merdiven ``000 001 011 010 110 111 101 100``tür ve
    kübitlerin manası ölçülebilir hâle gelir (bkz. ``makam_kubit_manasi``).
    """
    n = 1 << int(kac)
    return tuple(k ^ (k >> 1) for k in range(n))

def makam_derecesi(kac: int) -> np.ndarray:
    """Merdivenin her **basamağına** düşen yakîn derecesi, ``[0,1]``de.

    ``derece(k) = k / (2^kac − 1)``: en alt basamak 0 (vehm-i mutlak),
    en üst 1 (yakîn-i kat'î), arası düzgün bölünmüş. Basamak sayısı
    mertebe sayısından çok olabilir; olması da matluptur, zira mertebe
    bir **eşiktir**, bir nokta değil.
    """
    n = 1 << int(kac)
    return np.arange(n, dtype=float) / max(n - 1, 1)

def makam_mertebeleri(kac: int) -> Tuple[str, ...]:
    """Her basamağın hangi mertebeye düştüğü -- eşiklerden okunur.

    Eşik **alt sınırdır ve dâhildir** (`mizan/munazara.py` ile aynı
    kaide): derecesi ``d`` olan basamak, ``d``yi aşmayan en yüksek
    eşiğin mertebesindedir. Üç kübitte netice::

        basamak  0    1    2    3    4    5    6      7
        derece   .000 .143 .286 .429 .571 .714 .857  1.000
        mertebe  Vehim Vehim Şek  Şek  Zan  Zan  Zann-ı g.  Yakîn

    Dağılım eşit değildir ve **eşitlenmemiştir**: eşikler mîzânın
    cetvelinden gelir, oraya uydurulmaz. ``Yakîn``in yalnız tek
    basamağı olması cetvelin kendi hükmüdür -- *"kat'î; aksi muhal"*.
    """
    d = makam_derecesi(kac)
    out: List[str] = []
    for x in d:
        i = 0
        for j, e in enumerate(MAKAM_ESIKLERI):
            if x + 1e-12 >= e:
                i = j
        out.append(MAKAM_ADLARI[i])
    return tuple(out)

def makam_kubit_manasi(kac: int) -> Dict[int, Tuple[int, ...]]:
    """Her makam kübiti ``|1⟩`` iken merdivenin hangi basamakları açık.

    **İddia edilmez, hesaplanır.** Üç kübitte netice şudur ve manası
    şerhte değil burada durur::

        kübit 0 → basamak 4,5,6,7   = üst yarı  (Zan ve üstü)
        kübit 1 → basamak 2,3,4,5   = orta dörtlü (kararsızlık kuşağı)
        kübit 2 → basamak 1,2,5,6   = ara basamaklar (ince ayar)

    Yani ``makam₀`` hükmün **cihetidir**, ``makam₁`` kararsızlık
    kuşağıdır, ``makam₂`` ince ayardır. 𝒪₃₂ açılarını buna göre
    yöneltir; sınama bu tabloyu fiilen denetler.
    """
    merd = makam_merdiveni(kac)
    out: Dict[int, Tuple[int, ...]] = {}
    for b in range(int(kac)):
        vurgu = 1 << (int(kac) - 1 - b)          # ilk kübit en anlamlı
        out[b] = tuple(k for k, idx in enumerate(merd) if idx & vurgu)
    return out

def donme(teta: float) -> np.ndarray:
    """``R(θ) = [[cos,−sin],[sin,cos]]`` -- reel tek kübitlik dönme.

    Reel cebirde faz işarettir (bkz. ``kuantum/yazmac.py``); ``e^{iθ}``
    yerine ``SO(2)`` dönmesi taşınır. Dik olduğu için normu korur.
    """
    c, s = math.cos(float(teta)), math.sin(float(teta))
    return np.array([[c, -s], [s, c]], dtype=np.float64)

def faz_z() -> np.ndarray:
    """``σ_z`` -- işaret çevirme. Yıkıcı girişimi kuran kapı."""
    return np.array([[1.0, 0.0], [0.0, -1.0]], dtype=np.float64)

def degil_x() -> np.ndarray:
    """``σ_x`` -- ``|0⟩ ↔ |1⟩``. Menfî kontrolü kurmak için sarmalayıcı.

    Reel yazmaçta ``X`` bir **permütasyondur**; karmaşık faza ihtiyaç
    duymaz ve olduğu gibi tatbik edilir (kütük H98). Menfî kontrollü bir
    kapı, kontrol kübitini ``X`` ile sarmakla kurulur::

        X_c · CU(c,t) · X_c   ≡   kontrol |0⟩ iken uygulanan kapı
    """
    return np.array([[0.0, 1.0], [1.0, 0.0]], dtype=np.float64)

def kontrollu_donme(teta: float) -> np.ndarray:
    """``CR(θ)``: kontrol ``|1⟩`` iken hedefe ``R(θ)``.

    İki kübitlik indeks düzeni ``2i+j``dir (``i`` kontrol, ``j`` hedef) --
    ``main.yazmac._cift_kapi_dilim``deki düzenle aynı. Dik bir dizeydir;
    dolayısıyla dolaşıklığı kurar ve normu korur.
    """
    R = donme(teta)
    G = np.eye(4, dtype=np.float64)
    G[2:, 2:] = R
    return G
