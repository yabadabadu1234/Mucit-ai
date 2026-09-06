"""MÎZÂN-I KÜLLÎ -- modelin minimize edeceği yegâne şey.

    TABAKALI MİZAN (zabıt): L = L_nokta + α·L_uzay + β·L_kategori + γ·L_tip",
         "  L_uzay ≡ ℒ_Rezonans (Uhlmann), L_tip ≡ ℒ_Hodge -- terkip, tabela değil.",
         "  Yanına mizanın kendi kefeleri: λ₁ℒ_Çevrim + λ_t ℒ_Tenakuz + λ₂ℒ_Monogami + λ₄ℒ_Engel
                                                    + λ₄ℒ_Engel

===================================================================
NİÇİN BU DOSYA VAR: KÖK OLMADAN AĞAÇ OLMAZ
===================================================================

Padişahın teşhisi:

    *"Biz sürekli sanki elimizde konuşabilen bir model varmış da
    düşünmesini artırmaya çalışıyormuş gibi davranıyoruz. Hâlbuki şu an
    sadece bir durumumuz var... Hata fonksiyonunu belirledik ama kuantum
    ilhamlı olmadı, çok avantajlı bir fonksiyon olmadı. Hata fonksiyonu
    olmadan aradaki dalgayı nasıl çevireceğimizi düşünmenin manası yok,
    çünkü biz öyle çevirmeliyiz ki zaten o hata fonksiyonunu optimize
    etmeli. Kök olmadan ağaç olmaz."*

Bu dosya o köktür. Evvelki ``tabakali_mizan`` **imha edildi**: dört
terimliydi ve kör NLL'den iyiydi, fakat kuantumun kendi hadiselerinden
mülhem değildi; morfizmi dışarıdan istiyor, kategori terimini elle
verilen bir sözlükten okuyordu.

===================================================================
DÖRT KEFE -- HER BİRİ KUANTUMUN BİR HADİSESİ
===================================================================

**1. ℒ_Rezonans -- UHLMANN SADAKATİ (kör NLL DEĞİL).**

    ℒ_Rezonans = 1 − ( Tr √( √ρ_veri · ρ(Θ) · √ρ_veri ) )²

Veri bir *kural* değil, dışarıdan gelen **zayıf bir uyarımdır**. Model
verinin ana frekansıyla rezonansa girer, faz gürültüsünü taklit etmek
için kendini yırtmaz.

*Bunun NLL'den farkı lafzî değildir ve ölçülebilir:* ``ρ_veri`` belirteç
tabanında köşegen olsa bile ``√ρ σ √ρ`` matrisinin özdeğerleri ``σ``nın
**köşegen-dışı** elemanlarına bağlıdır. Yâni koherans sadakati etkiler.
``−log P`` ise yalnız köşegeni görür, faz kare alınırken buharlaşır.

**2. ℒ_Çevrim -- WİLSON HOLONOMİSİ (manayı bilmeden tenakuz).**

    U_C = U_{Z→X} · U_{Y→Z} · U_{X→Y}
    ω_C = Re Tr(U_C) / n          ∈ [−1, 1]
    ℒ_Çevrim = Σ_C ReLU(−ω_C)²

Bebek paradoksunun çözümü budur: iki cümlenin sözlük manasını bilmenize
gerek yoktur. Dağda yürürken pusulanızın ne olduğunu bilmeseniz de,
kapalı bir tur atıp ibrenin 180° ters döndüğünü görürseniz o arazide
topolojik bir yırtık olduğunu **ispatlamış** olursunuz.

Üç hal, ``ω`` ile birbirinden **kat'î** ayrılır (zabıtın icmal tablosu):

====================  =============  ==========  ==================
hal                   ``ω_C``        ``s_yol``   ceza
====================  =============  ==========  ==================
meşru teemmül         (−1, 1) arası  > 0         **YOK** (zenginleşme)
kısır döngü           ≈ +1           = 0         YOK (tevakkuf, budanır)
kuantum engellenmesi  arada          > 0         YOK (taban bulunamadı)
hakiki tenakuz        ω < 0, → −1    > 0         **FIRLAR**
====================  =============  ==========  ==================

``s_yol`` çevrim boyunca **katedilen** Fubini-Study yoludur, kapanış
mesafesi değildir. Sebebi ölçümdür ve ``holonomi``nin şerhinde yazılıdır:
kapanış mesafesi bu inşada yapısal olarak sıfır çıkar ve hiçbir şey
ayırmaz (üç halde de 0,000000 ölçüldü). Katedilen yol ise ayırır:
kısır döngüde 0,0000, üç dik hâlde 4,7124, parite taklasında 3,1416.

**Kuantum engellenmesi (frustration)** dördüncü haldir ve üçgen kafesli
antiferromıknatısın ta kendisidir: her köşe ötekilerle zıt olmak ister,
fakat üçü birden dikleşemez ve sistem taban durumuna oturamaz. Ceza
verilmez -- engellenme bir safsata değil, henüz çözülmemiş bir
gerilimdir; ``ℒ_Hodge`` onu ayrıca görür.

Dönmek yasak değildir; dönmek aklın fıtratıdır. Cezalandırılan döngünün
kendisi değil, **kendi başladığı aksiyomu inkâr eden parite taklasıdır**.
``ReLU(−ω)²`` tam da bunu yapar: ``ω = +1``de sıfır, ``ω ≈ 0``da sıfır,
yalnız ``ω < 0``da uyanır ve ``ω = −1``de 1 olur.

**3. ℒ_Monogami -- DOLANIKLIK MONOGAMİSİ (sahte illetleri budar).**

Klasik korelasyon sınırsızca dağıtılabilir; kuantum dolanıklığı
dağıtılamaz (Coffman-Kundu-Wootters). Klasik LLM'lerin en büyük kusuru
"her şeyi her şeyle ilişkili sanmaktır" (yoğun dikkat). Monogami
kanunu, sisteme bir neticeye **tek bir muhkem illet** bulmayı zorlar.

    ℒ_Monogami = ReLU( Σ_A w_A·𝒞²(V:A) − 𝒞²(V:hepsi) )

**HUDUT, AÇIKÇA:** bizim hüküm alanlarımız qudite ⊗ ile değil ⊕ ile
(süperseçim sektörü olarak) girer. Onun için buradaki, CKW'nin kendisi
değil **doğrudan-toplam mukabilidir** ve bir teorem olarak garanti
edilmez -- tam da bu yüzden ihlâl edilebilir, dolayısıyla bir kayıp
terimi olabilir. Garantili olsaydı sıfır sabit olurdu ve hiçbir şey
öğretmezdi.

**4. ℒ_Hodge -- HARMONİK TABAN (44 melekenin tasdik zırhı).**

    ℒ_Hodge = ⟨Ψ| Δ |Ψ⟩,   Δ = D − W  (PSD, çünkü W ≥ 0)

``W`` elle yazılmaz: **verinin kendi eş-zamanlılık çizgesidir**. Aynı
bağlamda geçen belirteçler arasında kenar vardır. ``⟨Ψ|Δ|Ψ⟩ =
½Σ W_ij|ψ_i − ψ_j|²`` olduğundan bu terim ancak durum eş-zamanlı
kavramlar üstünde **pürüzsüz** olduğunda sıfırlanır. Yırtık varsa
fırlar.

===================================================================
RÜŞT ÇİZELGESİ -- KÖR TERAZİDE HÜKÜM VERİLMEZ
===================================================================

    α(t) = σ( (t/T − t₀) / τ ) ∈ [0, 1]

Zabıt (*Tabula Rasa Krizi*): başlangıçta ağırlıklar rastgeledir; kendi
faz açıları rastgele dağılmış bir sistem iki veri arasındaki farkın π
(tenakuz) mi 0 (uyum) mu olduğunu **tartamaz**. O hâlde:

* ``α → 0`` **BEBEKLİK**: tenakuz cezası doğrudan **fıtrata**
  (ağırlıklara) akar. Terazi kalibre edilir; zıtlıklar dikleşir.
* ``α → 1`` **RÜŞT**: fıtrat kilitlenir, tenakuz **hafızaya** fatura
  edilir (``nefs/hafiza.py``). Ağırlık gevşetilip "demek ki bir insan
  aynı anda hem içeride hem dışarıda olabilirmiş" denmez.

Bu bir aç-kapa anahtarı değil, adyabatik bir faz geçişidir.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from .ayna import AynaAyari, halka
from .hafiza import CERH, TASDIK, TEVAKKUF, Hafiza
from .tdd import esit_mi, kanonik_adres

__all__ = ["MizanAyari", "uhlmann", "givens", "holonomi",
           "holonomi_yigin", "engellenme", "kulli_mizan", "mizan_cetveli",
           "rapor"]


@dataclass
class MizanAyari:
    """Mizanın bütün ölçüleri **tek yerde**; hiçbiri koda gömülü değil."""

    lam_cevrim: float = 1.0
    lam_monogami: float = 0.5
    lam_tip: float = 0.75   # ℒ_Hodge; ``denge()`` ölçer
    #: λ₄ kuantum engellenmesi (bkz. ``_engellenme``).
    lam_engel: float = 0.6
    #: Aynanın (Coherent Ising Machine) ölçüleri -- engellenme onunla
    #: ölçülür. ``nefs/ayna.py``.
    ayna_tur: int = 24
    ayna_teta: float = 0.2617993877991494
    ayna_r: float = 0.35
    #: **QSVT HODGE SÜZGECİ** (``nefs/qudit.py:suz``). Bu üçü evvelce
    #: ``main/egitim.py``de ayara konmuş fakat hiçbir yere geçmiyordu.
    #: Artık ``ℒ_Hodge`` süzülmüş durumda ölçülür: Chebyshev polinomu
    #: harmonik olmayan bileşeni bastırır ve geriye kalan enerji hakiki
    #: tenakuzdur. ``qsvt = 0`` ile kapatılabilir -- ölçü kırmızı yanar.
    #: **KLASİK GÖLGELER** (``nefs/golge.py``). ``0`` = kapalı: bütün
    #: sektör ağırlıkları tam hesaplanır. ``>0`` ise ``K`` gölge örneği
    #: alınır ve hata haddi aşılırsa **tam ölçüme dönülür** -- sessizce
    #: değil, dökümde ``gölge_düştü`` diye yazılır.
    golge_ornegi: int = 0
    golge_haddi: float = 0.05
    qsvt: int = 16
    qudit_derece: int = 8
    qudit_yon: int = 8
    #: Muhakeme çevriminin boyu. **En az 3 olmalıdır** ve bu keyfî
    #: değildir: iki adımlı bir çevrim (``a → b → a``) inşa gereği
    #: daima birim matris verir (ölçüldü), yâni holonomi taşımaz.
    #: Berry fazı alan ister; alan da en az üç köşe ister.
    cevrim_boyu: int = 3
    cevrim_sayisi: int = 8
    rust_t0: float = 0.5
    rust_tau: float = 0.15
    # ── ZABITLARIN ALTI UZVU (bkz. main/egitim.py'deki şerhler) ─────
    #: ``nefs/sadakat.py`` -- 7/24 zemin. Sıfırlanınca tenakuz alarmı
    #: sönmez ve rapor kırmızı yanar.
    sadakat_acik: int = 1
    parite_lifi: int = 2
    #: ``nefs/tenakuz.py`` -- log-bariyer × eş-zamanlı dışlama.
    lam_tenakuz: float = 0.4
    tenakuz_eps: float = 1e-5
    dislama_tau: float = 8.0
    #: ``nefs/tabakali_mizan.py`` -- funktör kompozisyonu ve kısmî Born.
    lam_kategori: float = 0.5
    lam_nokta: float = 0.25
    #: ``nefs/usul.py`` -- mantık yürütme seferi (7/24 DEĞİL).
    usul_acik: int = 1
    usul_haddi: float = 0.0
    usul_seferi: int = 4
    #: ``nefs/suphe.py`` -- teâruz, modalite, merak, Liouville.
    suphe_acik: int = 1
    suphe_sonumu: float = 0.05
    #: ``nefs/rust.py`` -- muayene kapısı.
    rust_kapanis: float = 0.5
    rust_muayene: int = 1
    #: ``|ω| > 1 − kenar`` ise hal saftır (tam kısır yahut tam tenakuz).
    kenar: float = 0.05
    zeno_esigi: float = 0.35
    #: **KANONİK DENETÇİNİN ÇEKİRDEĞİ** (``nefs/tdd.py``). Zabıt TDD'yi
    #: hesap motoru olmaktan çıkardı ve tek vazife bıraktı: *"mantık
    #: kilitlendiğinde kanonik adres eşitliğini (O(1)) kontrol eden
    #: haricî bir denetçi"*. Mantığın kilitlendiği yer burasıdır: bir
    #: muhakeme çevrimi kendi ışınına döndüyse kısırdır. Evvelce bu
    #: ``yol < 1e-9`` diye bir eşikle tayin ediliyordu; şimdi **adres
    #: kıyasıyla** kat'î olarak tayin edilir (çekirdek lif boyuna eşit
    #: veya ondan büyükse kıyas tamdır, elek değil).
    tdd_cekirdek: int = 16
    #: Cerh kaydının hangi belirteçleri kestiği (evvelce ``hafiza``da
    #: gömülüydü). **ZABIT: KORUNACAK (0,9).**
    zeno_tepe: float = 0.9
    #: Tâlimin toplam kayıp çağrısı kestirimi -- rüşt çizelgesinin paydası.
    toplam_adim: int = 200
    tohum: int = 0

    def __post_init__(self) -> None:
        assert int(self.cevrim_boyu) >= 3, (
            "çevrim boyu en az 3 olmalı: iki adımlı çevrim daima U=I "
            "verir ve holonomi taşımaz (ölçüldü)")
        assert int(self.cevrim_sayisi) >= 1, "en az bir çevrim taranmalı"
        assert 0.0 < float(self.kenar) < 0.5, "kenar (0, 0.5) olmalı"


# ══════════════════════════════════════════════════════════════════
#  0. RÜŞT -- **KÖR TAKVİM İMHA EDİLDİ** (bkz. nefs/rust.py)
# ══════════════════════════════════════════════════════════════════
#
# Burada ``rust(adim, ayar)`` duruyordu ve yalnız bir takvimdi:
# ``α(t) = σ((t/T − t₀)/τ)``. Vakit gelince fıtratı kilitliyordu --
# topolojisi yırtık bir dimağı da. Vakit bir olgunluk delili değildir.
#
# Yerine **hibrit rüşt kilidi** geldi (``nefs/rust.py:rust_kilidi``):
# takvim ile muayenenin çarpımı. Eski usul aynı turda kesildi (ferman
# 1-E: iki yol yan yana durdukça hangisinin koştuğu belirsizdir).


# ══════════════════════════════════════════════════════════════════
#  1. REZONANS -- UHLMANN SADAKATİ
# ══════════════════════════════════════════════════════════════════
def uhlmann(rho: np.ndarray, sigma: np.ndarray) -> float:
    """``F(ρ,σ) = (Tr √(√ρ σ √ρ))²`` -- Uhlmann kuantum sadakati.

    ``eigvalsh``/``eigh`` kullanılır ve bu bir **kesme değil ölçümdür**:
    hiçbir tekil değer atılmaz, matris küçültülmez. Yasak olan SVD ile
    **sıkıştırmaktı**; kare kök almak sıkıştırma değildir.
    """
    R = np.asarray(rho, complex)
    S = np.asarray(sigma, complex)
    assert R.shape == S.shape and R.ndim == 2, (
        "sadakat için iki aynı boyda yoğunluk matrisi lâzım")
    w, V = np.linalg.eigh(0.5 * (R + R.conj().T))
    w = np.clip(w.real, 0.0, None)
    kok = (V * np.sqrt(w)) @ V.conj().T
    M = kok @ S @ kok
    e = np.linalg.eigvalsh(0.5 * (M + M.conj().T)).real
    F = float(np.sum(np.sqrt(np.clip(e, 0.0, None))) ** 2)
    return float(np.clip(F, 0.0, 1.0))


# ══════════════════════════════════════════════════════════════════
#  2. ÇEVRİM -- WİLSON HOLONOMİSİ
# ══════════════════════════════════════════════════════════════════
def givens(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """``|a⟩ ↦ |b⟩`` götüren **asgarî** üniter (iki boyutlu Givens).

    Morfizm dışarıdan verilmez; sistemin kendi iki durumundan **inşa
    edilir**. İki durumun gerdiği düzlemde bir ``SU(2)`` dönmesi, o
    düzlemin dışında birimdir -- yâni gereksiz hiçbir dönme yapılmaz.
    Bu, iki kavram arasındaki *en ucuz* geçiştir ve yol boyunca biriken
    faz tam da bu yüzden manalıdır: fazla dönme yoktur, biriken şey
    geometrinin kendisidir.
    """
    a = np.asarray(a, complex).reshape(-1)
    b = np.asarray(b, complex).reshape(-1)
    assert a.size == b.size and a.size >= 2, "Givens için aynı boyda iki hâl"
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    assert na > 0 and nb > 0, "sıfır hâl arasında morfizm kurulamaz"
    a = a / na
    b = b / nb
    c = complex(np.vdot(a, b))            # ⟨a|b⟩
    dik = b - c * a
    s = float(np.linalg.norm(dik))
    n = a.size
    if s < 1e-12:
        # İki hâl aynı ışın: morfizm yalnız bir faz. Birim DEĞİL --
        # fazı atmak holonomiyi kör ederdi.
        faz = c / abs(c) if abs(c) > 0 else 1.0 + 0j
        return np.eye(n, dtype=complex) * faz
    e2 = dik / s
    U = np.eye(n, dtype=complex)
    # ``span{a, e2}`` düzleminde SU(2); dışarıda birim.
    P = np.stack([a, e2], axis=1)          # (n, 2) dik sütunlar
    R = np.array([[c, -np.conj(s)], [s, np.conj(c)]], dtype=complex)
    U = U - P @ P.conj().T + P @ R @ P.conj().T
    return U


def holonomi(hal: Sequence[np.ndarray]) -> Tuple[np.ndarray, float, float]:
    """Kapalı çevrimin Wilson operatörü, ``ω`` izi ve Fubini-Study hacmi.

    ``(U_C, ω, ds²_FS)`` döner:

    * ``ω  = Re Tr(U_C)/n`` -- üç hali ayıran tek sayı.
    * ``s_yol = Σ_k arccos|⟨h_k|h_{k+1}⟩|`` -- çevrim boyunca **katedilen**
      Fubini-Study yolu.

    **ÖLÇEREK DÜZELTİLDİ.** Evvelce burada zabıtın yazdığı kapanış
    mesafesi vardı: ``ds²_FS = 1 − |⟨Ψ|U_C|Ψ⟩|²``. Ölçüldü ve **üç
    halin üçünde de tam sıfır** çıktı; yâni ölçü hiçbir şey ayırmıyordu.
    Sebebi inşanın kendisiydi: Givens morfizmleri her hâli bir
    sonrakine **tam** götürdüğü için ``U_C|h₀⟩ = |h₀⟩`` yapısal olarak
    sağlanır ve kapanış mesafesi zorunlu olarak sıfırdır.

    Zabıtın kastettiği şey kapanış değil, **katedilen hacimdi**:
    *"katedilen geometrik hacim Vol_FS = 0 olduğu için zihnin motoru bu
    döngüyü boş salınım olarak etiketler."* Yol uzunluğu tam da odur:
    kısır döngüde (aynı hâl tekrar tekrar) sıfırdır, meşru teemmülde
    pozitiftir. Formülü zorlamak yerine ölçüyü mânâya uydurdum.
    """
    H = [np.asarray(h, complex).reshape(-1) for h in hal]
    assert len(H) >= 3, (
        "kapalı çevrim en az üç köşe ister; iki köşe daima U=I verir")
    n = H[0].size
    U = np.eye(n, dtype=complex)
    for i in range(len(H)):
        U = givens(H[i], H[(i + 1) % len(H)]) @ U
    omega = float(np.real(np.trace(U)) / n)
    yol = 0.0
    for i in range(len(H)):
        a = H[i] / (np.linalg.norm(H[i]) or 1.0)
        b = H[(i + 1) % len(H)]
        b = b / (np.linalg.norm(b) or 1.0)
        yol += float(math.acos(float(np.clip(abs(np.vdot(a, b)), 0.0, 1.0))))
    return U, float(np.clip(omega, -1.0, 1.0)), float(yol)


def holonomi_yigin(H: np.ndarray, idx: np.ndarray
                   ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """``C`` çevrimin holonomisi **tek hamlede** -- Python döngüsü yok.

    ===================================================================
    ZABITIN 2. AMELİYESİ (Qudit Kapasitesi ve Hız Tahkiki)
    ===================================================================

    Zabıt der ki:

        *"8 adet Wilson çevrimi tek tek sıralı bir döngüde
        hesaplanıyorsa, tensör çekirdekleri paralel çalışamaz...
        8 çevrimin transfer matrisleri tek bir tensör bloğunda
        toplanır: [8, B, d, d]."*

    Burada icra edilen budur. ``H`` bütün hâller ``(m, n)``, ``idx``
    ise ``(C, boy)`` köşe indisleridir. Bütün Givens dönmeleri
    ``(C, n, n)`` bloğunda toplu kurulur ve çarpım tek ``einsum``
    zinciriyle alınır.

    **YOĞUN ``n×n`` KURULMASININ SEBEBİ YAZILIDIR:** holonominin izi
    ``Re Tr(U_C)/n`` istenir; iz, matrisin kendisini ister. ``n`` burada
    belirteç lifidir (16), ``d`` (4096) değil -- yâni blok ``(8,16,16)``
    kadardır, 2048 sayı. Zabıtın ``[8, B, d, d]`` tarifi ``d``yi
    quditin tamamı sayarsa 8·4096² olurdu ve o **kurulmuyor**.
    """
    H = np.asarray(H, complex)
    idx = np.asarray(idx, int)
    C, boy = idx.shape
    n = H.shape[1]
    assert boy >= 3, "kapalı çevrim en az üç köşe ister"
    # Köşeleri normalize et: (C, boy, n)
    K = H[idx]
    K = K / np.maximum(np.linalg.norm(K, axis=-1, keepdims=True), 1e-300)
    U = np.broadcast_to(np.eye(n, dtype=complex), (C, n, n)).copy()
    yol = np.zeros(C, float)
    for t in range(boy):
        A = K[:, t, :]                                   # (C, n)
        Bv = K[:, (t + 1) % boy, :]                      # (C, n)
        c = np.einsum('ci,ci->c', A.conj(), Bv)          # ⟨a|b⟩
        yol += np.arccos(np.clip(np.abs(c), 0.0, 1.0))
        dik = Bv - c[:, None] * A
        sn = np.linalg.norm(dik, axis=-1)                # (C,)
        e2 = dik / np.maximum(sn, 1e-300)[:, None]
        # Düzlem içi SU(2); düzlem dışı birim. Aynı ışında ise yalnız faz.
        P0 = np.einsum('ci,cj->cij', A, A.conj())
        P1 = np.einsum('ci,cj->cij', e2, e2.conj())
        X01 = np.einsum('ci,cj->cij', A, e2.conj())
        X10 = np.einsum('ci,cj->cij', e2, A.conj())
        G = (c[:, None, None] * P0 - sn[:, None, None] * X01
             + sn[:, None, None] * X10
             + np.conj(c)[:, None, None] * P1)
        birim = np.broadcast_to(np.eye(n, dtype=complex), (C, n, n))
        Gt = birim - P0 - P1 + G
        # Aynı ışın (sn≈0): morfizm yalnız bir fazdır, birim DEĞİL.
        ayni = sn < 1e-12
        if np.any(ayni):
            faz = np.where(np.abs(c) > 0, c / np.maximum(np.abs(c), 1e-300),
                           1.0 + 0j)
            # **FAZ ÇEVRİMİN KENDİ IŞINA VURULUR, BÜTÜN LİFE DEĞİL.**
            # Evvelce ``birim * faz`` yazıyordu: ``n`` boyutun tamamına
            # bir **küme fazı**. Küme fazı fizikî olarak gözlenemez
            # (``|ψ⟩`` ile ``e^{iφ}|ψ⟩`` aynı hâldir), o hâlde onu
            # holonomiye yazmak, ölçülemeyen bir şeyi ölçüye sokmaktı.
            # Doğrusu izdüşümlü hâlidir: faz yalnız ``a``nın ışınında.
            Gt = np.where(ayni[:, None, None],
                          birim + (faz[:, None, None] - 1.0) * P0, Gt)
        U = np.einsum('cij,cjk->cik', Gt, U)
    # ══════════════════════════════════════════════════════════════
    #  ω, ÇEVRİMİN FİİLEN DÖNDÜĞÜ AÇIDIR -- LİFİN TAMAMI DEĞİL
    # ══════════════════════════════════════════════════════════════
    #
    # **BURASI YAPISAL OLARAK KIRIKTI VE ÖLÇÜLDÜ.** Evvelce
    # ``ω = Re Tr(U_C)/n`` yazıyordu. Her Givens yalnız **iki** boyutta
    # döner ve kalan ``n−2`` boyutta birimdir; o hâlde
    # ``Tr(U_C) ≥ n − 4`` ve ``ω ≥ 1 − 4/n``. Ölçüldü (200 rastgele
    # çevrim)::
    #
    #     n= 4   ω ∈ [+0,032, +0,979]
    #     n= 8   ω ∈ [+0,517, +0,962]
    #     n=16   ω ∈ [+0,772, +0,952]      ← ana hattın lifi
    #     n=32   ω ∈ [+0,897, +0,970]
    #
    # Ana hatta ``n = 16``dır: ``ω`` **asla 0,75'in altına inemiyordu.**
    # Neticesi, tek bir paydanın öldürdüğü bir zincirdir:
    #
    #     tenakuz sınıfı (ω < −0,95)      → yapısal olarak İMKÂNSIZ
    #     sekiz çevrimin sekizi           → daima "kısır"
    #     ℒ_Çevrim, ℒ_Tenakuz             → daima 0
    #     hafızaya CERH kaydı             → hiç düşmez
    #     Zeno budaması (çıkarımda)       → daima 0
    #     nefs/usul.py'nin bütün seferi   → gedik yok, hiç açılmaz
    #
    # Ölçüler yeşil yanıyordu çünkü **hiçbir şey ölçmüyorlardı.**
    # Raporun kırmızı yanma sınaması da bunu göremiyordu: orası elle
    # kurulmuş **üç boyutlu** bir hâl kullanır ve küçük ``n``de seyreltme
    # yoktur. Münafıklığın gizlendiği boşluk tam olarak oydu.
    #
    # DOĞRUSU: ``U_C`` üniterdir ve özdeğerleri ya ``1``dir (çevrimin
    # hiç dokunmadığı yönler) ya da ``e^{±iθ}``dır (fiilen döndüğü
    # düzlemler). Ölçülmesi gereken **dönülen açıdır**, dokunulmamış
    # yönlerin sayısı değil::
    #
    #     ω = ortalama Re λ  ,  λ ∈ spec(U_C) ve |λ − 1| > tol
    #     hiç dönmemişse ω = +1  (kısır: çevrim hiçbir yere varmadı)
    #
    # Bu, lif boyundan **tamamen bağımsızdır**: aynı çevrim ``n=16``da da
    # ``n=256``da da aynı ``ω``yı verir. Ve haddi hakikaten ``[−1, +1]``
    # dir: parite taklası ``a→b→−a`` tam ``−1`` verir (evvelce ``−0,5``
    # görünüyordu; o da aynı seyreltmenin küçük hâliydi).
    # DOĞRUSU: ``U_C``, çevrimin köşelerinin gerdiği altuzayın
    # **dışında birimdir** -- hiçbir Givens oraya dokunmaz. O hâlde::
    #
    #     S = span{a, b, c, …}   (boyut r ≤ çevrim boyu)
    #     U_C = I_{S⊥} ⊕ V       ,      ω = Re Tr(V) / r
    #
    # Dokunulmamış ``n − r`` yön ölçüye **hiç girmez** ve ``ω`` lif
    # boyundan tamamen bağımsız olur. ``r`` bir varsayım değil,
    # **ölçülür**: QR'ın ``R`` köşegeni sıfıra çökmüşse o yön
    # altuzayda yoktur (köşeler eşdoğrusal olabilir -- kısır çevrimin
    # tarifi tam da budur).
    Kq = np.transpose(K, (0, 2, 1))                  # (C, n, boy)
    Q, R = np.linalg.qr(Kq)                          # (C, n, boy)
    kose = np.abs(np.diagonal(R, axis1=1, axis2=2))  # (C, boy)
    var = kose > 1e-9                                # hangi yön hakikî
    r_etkin = np.maximum(var.sum(axis=1), 1)
    Qc = Q * var[:, None, :]
    om = np.real(np.einsum('cni,cnm,cmi->c', Qc.conj(), U, Qc)) / r_etkin
    return U, np.clip(om, -1.0, 1.0), yol


def _cevrimleri_tara(haller: Sequence[np.ndarray], ayar: MizanAyari,
                     baglamlar: Optional[Sequence[Sequence[int]]] = None,
                     hedefler: Optional[Sequence[int]] = None,
                     n_v: int = 0) -> Dict[str, Any]:
    """Yığından kapalı çevrimler seç, hepsini sınıflandır ve cezala.

    ``baglamlar``/``hedefler`` verilirse ``L_Tenakuz`` de burada ölçülür:
    log-bariyer holonominin izini ister, iz de ``U_C``yi -- ikisi de
    zaten burada kuruluyor, ikinci kere kurmak israf olurdu (ferman 3).
    """
    m = len(haller)
    a = ayar
    if m < int(a.cevrim_boyu):
        return {"ceza": 0.0, "meşru": 0, "kısır": 0, "tenakuz": 0,
                "engel": 0, "çevrim": [], "ω": [], "indis": [],
                "bariyer": {"ceza": 0.0, "azamî": 0.0, "ham_azamî": 0.0,
                            "tavan": 0.0, "dışlama_ortalama": 0.0,
                            "çevrim": 0}}
    r = np.random.default_rng(int(a.tohum))
    ceza = 0.0
    say = {"meşru": 0, "kısır": 0, "tenakuz": 0, "engel": 0}
    kayit: List[Tuple[float, float, float]] = []
    omegalar: List[float] = []
    # **ZABITIN 2. AMELİYESİ: ÇEVRİMLER VEKTÖRİZE EDİLDİ.**
    # Evvelce sekiz çevrimin köşeleri Python döngüsünde tek tek
    # seçiliyordu. Şimdi indisler **tek hamlede** çekilir ve holonomiler
    # yığın halinde kurulur; ``holonomi_yigin`` içinde bütün Givens
    # dönmeleri toplu ``einsum``la çarpılır.
    idx_hepsi = np.stack([
        r.choice(m, size=int(a.cevrim_boyu), replace=False)
        for _ in range(int(a.cevrim_sayisi))])          # (C, boy)
    H = np.stack([np.asarray(h, complex).reshape(-1) for h in haller])
    U_hepsi, om_hepsi, yol_hepsi = holonomi_yigin(H, idx_hepsi)
    # ── KANONİK DENETÇİ: ÇEVRİM KENDİ IŞININA MI DÖNDÜ ──────────────
    # Zabıtın TDD'ye bıraktığı tek vazife. Başlangıç köşesi ``a`` ile
    # holonominin götürdüğü ``U_C a`` **aynı adreste** ise çevrim
    # hiçbir yere varmamıştır: kısırdır. Bu bir eşik değil, kıyastır.
    A0 = H[idx_hepsi[:, 0]]
    A0 = A0 / np.maximum(np.linalg.norm(A0, axis=-1, keepdims=True), 1e-300)
    A1 = np.einsum('cij,cj->ci', U_hepsi, A0)
    cek = int(a.tdd_cekirdek)
    # **TDD DENETÇİSİ NE SÖYLÜYORSA O YAZILIR.** Zabıtın ona verdiği
    # tek vazife kanonik adres eşitliğidir ve o eşitlik burada
    # **yapısal bir kimliktir**, bir hüküm değil: Givens taşıması
    # kapanmayı garanti eder. Denetçi bunu teyit eder (bir sağlama
    # toplamıdır); kısırlık hükmü ``ω``dan verilir.
    kapali = [esit_mi(kanonik_adres(A0[c], cekirdek=cek),
                      kanonik_adres(A1[c], cekirdek=cek))
              for c in range(idx_hepsi.shape[0])]
    tdd_kimlik = bool(all(kapali))
    for c_no in range(int(a.cevrim_sayisi)):
        idx = [int(i) for i in idx_hepsi[c_no]]
        koseler = [haller[i] for i in idx]
        om = float(om_hepsi[c_no])
        yol = float(yol_hepsi[c_no])
        omegalar.append(om)
        # **CEZA YALNIZ PARİTE TAKLASINA.** Dönmek yasak değildir;
        # cezalandırılan, kendi başladığı aksiyomu inkâr eden ``ω < 0``
        # taklasıdır. ``ω = +1`` (kısır) ve ``ω ≈ 0`` (meşru) sıfır ceza alır.
        c = float(max(0.0, -om) ** 2)
        ceza += c
        # KUANTUM ENGELLENMESİ (frustration): üçgen kafesli
        # antiferromıknatısın ta kendisi. Her köşe ötekilerle zıt olmak
        # ister (karşılıklı dışlama), fakat üçü birden dikleşemez ve
        # sistem taban durumuna oturamaz.
        ort = []
        for i in range(len(koseler)):
            for j in range(i + 1, len(koseler)):
                u = koseler[i] / (np.linalg.norm(koseler[i]) or 1.0)
                v = koseler[j] / (np.linalg.norm(koseler[j]) or 1.0)
                ort.append(float(abs(np.vdot(u, v))))
        engelli = bool(ort) and max(ort) < 0.5
        if om < -1.0 + a.kenar:
            say["tenakuz"] += 1
        elif om > 1.0 - a.kenar:
            # **KISIRLIK ARTIK ω'DAN OKUNUR, TDD ADRESİNDEN DEĞİL.**
            #
            # Evvelce burada ``kapali[c_no]`` vardı: ``U_C·a`` ile ``a``
            # aynı kanonik adreste mi? Ölçüldü ve **yapısal olarak daima
            # evet** çıktı: 200 rastgele çevrimin 200'ü "kapalı",
            # ``‖U_C·a − a‖`` azamî ``6,3e−16``. Sebebi inşadır --
            # Givens taşıması ``a → b → c → a`` diye kurulur, o hâlde
            # ``U_C·a = a`` **daima** sağlanır.
            #
            # Neticesi: her çevrim kısır sayılıyordu. ``ℒ_Çevrim`` sıfır,
            # ``meşru`` sıfır, keyfiyet nispeti sıfır (çarpımda bir
            # çarpan sıfırsa netice sıfır) -- ve o yüzden münasebet
            # döngüsü hiçbir kümeyi temizleyemiyordu. Tek bir yapısal
            # sabitin öldürdüğü zincir buydu.
            #
            # Doğrusu: kısırlık **holonominin birim olmasıdır**. Çevrim
            # döndü fakat hiçbir yere varmadıysa ``U_C`` kendi
            # altuzayında birimdir, yâni ``ω → +1``. Bu, dönüş
            # adresinden değil **katedilen dönmeden** okunur.
            # **BİR ÇEVRİM BİR KERE SAYILIR.** Burada ``say["kısır"]``
            # **iki kere** artıyordu: kısırlık ``ω``ya taşınırken eski
            # (kanonik adres) satırı silinmemiş, yenisi üstüne
            # yazılmıştı. Netice, ölçünün kendisini bozuyordu --
            # ``çevrim`` paydası ``meşru + kısır + tenakuz + engel``
            # olduğu için kısır hem paya hem paydaya çift giriyor ve
            # ``nispet_kısır = 1 − kısır/çevrim`` yanlış çıkıyordu.
            # Sayılan şey çevrimdir; bir çevrim bir tanedir.
            say["kısır"] += 1
        elif engelli:
            say["engel"] += 1
        else:
            say["meşru"] += 1
        kayit.append((om, yol, c))
    n_c = max(1, int(a.cevrim_sayisi))
    # ══════════════════════════════════════════════════════════════
    #  L_TENAKUZ -- LOG BARİYER × DIŞLAMA (nefs/tenakuz.py)
    # ══════════════════════════════════════════════════════════════
    #
    # Yukarıdaki ``ceza`` ham ``max(0,−ω)²``dir: sonludur, fakat tam
    # taklaya yaklaşan bir çevrimle hafif eğik bir çevrim arasında
    # neredeyse hiç ayrım yapmaz (kare fonksiyonu orada yatıktır).
    # Log-bariyer o ayrımı keskinleştirir ve ``ε`` freniyle ıraksamaz.
    #
    # ``S_dışlama`` her çevrimin **kendi köşelerinin hedeflerinden**
    # okunur: çevrim, veride hiç beraber görülmemiş kavramları
    # birbirine bağlıyorsa cezası ağırdır.
    from .tenakuz import TenakuzAyari, dislama_dizeyi, log_bariyer
    ta = TenakuzAyari(lam=float(a.lam_tenakuz), eps=float(a.tenakuz_eps),
                      tau=float(a.dislama_tau))
    if baglamlar is not None and hedefler is not None and int(n_v) > 0:
        S = dislama_dizeyi(baglamlar, int(n_v), ta)
        h = np.asarray(list(hedefler), np.int64) % int(n_v)
        cift = np.empty(idx_hepsi.shape[0], float)
        for c_no in range(idx_hepsi.shape[0]):
            t = h[idx_hepsi[c_no]]
            # Çevrimin bütün köşe ikilileri: A ile B hiç beraber
            # görülmemişse S≈1, sık görülmüşse S≈0.
            alt = [float(S[int(t[i]), int(t[j])])
                   for i in range(t.size) for j in range(i + 1, t.size)]
            cift[c_no] = float(np.mean(alt)) if alt else 1.0
    else:
        cift = np.ones(idx_hepsi.shape[0], float)
    bariyer = log_bariyer(U_hepsi, cift, ta)
    return {"ceza": ceza / n_c, "çevrim": kayit, "ω": omegalar,
            "indis": [[int(i) for i in r] for r in idx_hepsi],
            "bariyer": bariyer, "tdd_kimlik": tdd_kimlik, **say}


# ══════════════════════════════════════════════════════════════════
#  3. MONOGAMİ -- CKW'nin doğrudan-toplam mukabili
# ══════════════════════════════════════════════════════════════════
def _monogami(M3: np.ndarray, sektorler: Sequence[Tuple[int, int]]
              ) -> Tuple[float, float, float]:
    """``(Σ ceza, Σ Σ_A w_A 𝒞²(V:A), Σ 𝒞²(V:hepsi))`` -- **bütün yığın**.

    ``M3`` durumun lifli görünümüdür: ``(S, n_veri, n_hüküm)``. Hüküm
    alanları ise **düz** ``d`` indisinde ``[i:j)`` aralıklarıdır.

    **NİÇİN YIĞIN HÂLİNDE.** Ölçüldü: bu terim örnek başına ayrı ayrı
    çağrılıyordu (512 çağrı, 0,49 sn -- küllî mizanın altıda biri) ve
    her çağrıda on bir sektör maskesi **yeniden** kuruluyordu; halbuki
    maskeler örnekten bağımsızdır ve bir kere kurulur. Yığınla hem
    maskeler bir kere kurulur, hem ``ρ_A`` çarpımları tek yığın GEMM'e
    iner. Netice birebir aynıdır: aynı toplamın başka sırayla alınması.

    **ÖLÇEREK BULUNAN HATA.** Evvelce ``M[:, i:j]`` yazılmıştı, yâni
    sektör aralığı hüküm lifinin sütunu sanılmıştı. Ölçüldü: sektörler
    ``(0,332) … (3652,4096)`` idi, hüküm lifi ise **256** sütunluk.
    Yâni bir sektör bütün sütunları kapsıyor, ötekiler boş dönüyordu;
    netice olarak eşitsizliğin iki yanı **birebir aynı** çıkıyordu
    (1,7775 = 1,7775, ceza 1,1e−15). Kayıp terimi sabit sıfırdı ve
    hiçbir şey öğretmiyordu.

    Doğrusu: düz indis ``k = v·n_h + h``dir; sektör bu ızgarada bir
    **maske**dir ve satırları da sütunları da kesebilir.
    """
    M = np.asarray(M3, complex)
    assert M.ndim == 3 and M.size > 0, "lifli yığın (S, n_v, n_h) olmalı"
    S, n_v, n_h = M.shape
    d = n_v * n_h
    top = np.sum(np.abs(M) ** 2, axis=(1, 2))
    assert float(np.min(top)) > 0.0, "durum BOŞ -- monogami ölçülemez"
    M = M / np.sqrt(top)[:, None, None]

    Mc = M.conj()

    def _saflik(X: np.ndarray, Xc: np.ndarray) -> np.ndarray:
        """``Tr ρ²`` -- ``ρ = XX†``, yığın **BLAS** çarpımıyla.

        ``einsum`` DEĞİL: ölçüldü, ``np.einsum('svh,swh->svw')`` BLAS'a
        inmiyor ve tek başına 0,62 sn yiyordu. ``matmul`` aynı hesabı
        yığın ``zgemm`` olarak yapar. ``Tr(g²)`` ise ``16×16``dır,
        orada einsum ucuzdur.
        """
        g = np.matmul(X, Xc.swapaxes(1, 2))
        return np.real(np.einsum('svw,swv->s', g, g))

    C2_hepsi = np.maximum(0.0, 2.0 * (1.0 - _saflik(M, Mc)))

    # ── MASKE DEĞİL, DİLİM ─────────────────────────────────────────
    # Sektör düz indiste **ardışık** bir aralıktır ve sektörler
    # birbirini takip eder. O hâlde her sektör için bütün diziyi
    # maskelemek (``np.where``, sektör başına üç tam geçiş; ölçüldü
    # 0,79 sn) israftır. Tek tampon kurulur, yalnız sektörün dilimi
    # yazılır, ölçüldükten sonra **yalnız o dilim** sıfırlanır.
    # Bütün sektörler boyunca yazılan toplam eleman ``2d``dir.
    F = M.reshape(S, d)
    Fc = Mc.reshape(S, d)
    g2 = np.abs(F) ** 2
    A = np.zeros((S, d), complex)
    Ac = np.zeros((S, d), complex)
    Av = A.reshape(S, n_v, n_h)
    Avc = Ac.reshape(S, n_v, n_h)
    toplam = np.zeros(S, float)
    for (i, j) in sektorler:
        assert 0 <= i < j <= d, (
            "sektör düz indisin dışında: (%d,%d) ∉ [0,%d]" % (i, j, d))
        w = np.sum(g2[:, i:j], axis=1)
        var = w > 1e-15
        if not np.any(var):
            continue
        A[:, i:j] = F[:, i:j]
        Ac[:, i:j] = Fc[:, i:j]
        # Sektörün dokunduğu **satır kuşağı**: ``v = düz // n_h``. Kuşak
        # dışındaki satırlar tamamen sıfırdır; ``g = XX†``de sıfır satır
        # ve sıfır sütun verirler, ``Tr(g²)``ye hiçbir şey katmazlar.
        # O hâlde çarpım da onları dolaşmaz (16 satır yerine 2-3).
        v0, v1 = i // n_h, (j - 1) // n_h
        saf = (_saflik(Av[:, v0:v1 + 1], Avc[:, v0:v1 + 1])
               / np.maximum(w, 1e-300) ** 2)
        A[:, i:j] = 0.0
        Ac[:, i:j] = 0.0
        toplam += np.where(var, w * np.maximum(0.0, 2.0 * (1.0 - saf)), 0.0)
    return (float(np.sum(np.maximum(0.0, toplam - C2_hepsi))),
            float(np.sum(toplam)), float(np.sum(C2_hepsi)))


# ══════════════════════════════════════════════════════════════════
#  3b. ENGELLENME -- KUANTUM FRUSTRATION (nefs/ayna.py'nin HALKASI)
# ══════════════════════════════════════════════════════════════════
def engellenme(H: np.ndarray, ayar: Optional[MizanAyari] = None
               ) -> Dict[str, Any]:
    """``ℒ_Engel`` -- sistem taban durumuna oturabiliyor mu?

    ===================================================================
    AYNANIN ANA AKIŞTAKİ FİİLÎ İŞİ BURASIDIR
    ===================================================================

    Zabıt (*Küllî Kuantum Mizânı*, III. fasıl, 1. hadise):

        *"Üçgen kafesli antiferromanyetlerde s₁ ile s₂ zıt olmak ister,
        s₂ ile s₃ zıt olmak ister. Fakat bu durumda s₃ ile s₁ aynı
        olmak zorunda kalır ve sistem kilitlenir... Eğer metin
        safsataysa, sistemdeki spinler hiçbir zaman taban durumuna
        oturamaz; sürekli mikroskobik bir gerilim dalgası yayar."*

    Bu bir **kombinatorik kriz**tir: ``2^m`` diziliş arasından gerilimi
    asgarîye indireni bulmak. Zabıtın ikinci vazifesi tam da bunun
    içindi -- *"iki ayna arasına kapalı bir optik döngü (Coherent Ising
    Machine)... doğru olan tek mana tepesi lazerin osilasyona başlaması
    gibi bir anda tepeye fırlar."*

    O hâlde çiftlenim ``J_ij = Re⟨h_i|h_j⟩`` kurulur ve dizilişi
    **``nefs/ayna.py:halka``** bulur. Sonra tatmin edilmeyen bağların
    ağırlık payı ceza olur::

        ℒ_Engel = 1 − Σ max(0, J_ij·s_i·s_j) / Σ|J_ij|

    Sıfır = bütün bağlar tatmin (taban durumuna oturuldu).
    Bir     = hiçbir bağ tatmin edilemiyor (tam engellenme).

    ``lam_engel = 0`` ile kapatılabilir ve kapatılınca kefe kaybolur --
    yâni tesir ölçülebilir (H90).
    """
    a = ayar or MizanAyari()
    H = np.asarray(H, complex)
    m = H.shape[0]
    if m < 3:
        return {"ceza": 0.0, "bağ": 0, "toplam": 0, "spin": None,
                "doyum": 0.0}
    Hn = H / np.maximum(np.linalg.norm(H, axis=-1, keepdims=True), 1e-300)
    J = np.real(Hn @ Hn.conj().T)
    np.fill_diagonal(J, 0.0)
    olcek = float(np.sum(np.abs(J)))
    if olcek <= 0.0:
        return {"ceza": 0.0, "bağ": 0, "toplam": 0, "spin": None,
                "doyum": 0.0}
    # ``ne="döküm"`` istenir ve bu tercih **kasıtlıdır**: döküm yolu
    # ``ogrenme/morse.py``nin Banchoff sayımını (kaç mana öbeği kaldı)
    # ve ``kuantum/eniyileme.py``nin bağımsız kesim şahidini de
    # koşturur. ``çözüm`` yolu ikisini de atlar ve o iki modül ana
    # akışta hiç iş görmemiş olurdu.
    h = halka(J, AynaAyari(teta=float(a.ayna_teta), r=float(a.ayna_r),
                           tur=int(a.ayna_tur), tohum=int(a.tohum)),
              ne="döküm")
    s = np.asarray(h["spin"], int)
    tatmin = J * np.outer(s, s)
    kazanc = float(np.sum(np.maximum(tatmin, 0.0)))
    ceza = float(np.clip(1.0 - kazanc / olcek, 0.0, 1.0))
    bag = int(np.count_nonzero(tatmin < 0) // 2)
    top = int(np.count_nonzero(J) // 2)
    return {"ceza": ceza, "bağ": bag, "toplam": top, "spin": s,
            "doyum": float(h.get("bedel", 0.0)),
            "öbek": int(h.get("öbek", 0)),
            "şahit_nispeti": float(h.get("şahit_nispeti", 0.0)),
            "kilitlendi": bool(h.get("kilitlendi", False))}


# ══════════════════════════════════════════════════════════════════
#  4. HODGE -- verinin kendi eş-zamanlılık çizgesi
# ══════════════════════════════════════════════════════════════════
def _laplasyen(baglamlar: Sequence[Sequence[int]], n: int) -> np.ndarray:
    """``Δ = D − W``; ``W`` = eş-zamanlılık sayımı. **PSD garantili.**"""
    W = np.zeros((n, n), float)
    for bag in baglamlar:
        t = sorted({int(x) % n for x in bag})
        for a in range(len(t)):
            for b in range(a + 1, len(t)):
                W[t[a], t[b]] += 1.0
                W[t[b], t[a]] += 1.0
    m = float(W.max())
    if m > 0:
        W /= m
    D = np.diag(W.sum(axis=1))
    return D - W


# ══════════════════════════════════════════════════════════════════
#  5. MÎZÂN-I KÜLLÎ
# ══════════════════════════════════════════════════════════════════
def _ileri(nefs, veri, sozluk: int) -> Dict[str, Any]:
    """İleri geçiş -- **YIĞIN HALİNDE**, örnek örnek değil.

    ===================================================================
    NİÇİN YIĞIN: ÖLÇÜLEN 97 000 KATLIK FARK
    ===================================================================

    Evvelce her örnek için ayrı bir ``idrak_et`` çağrılıyordu. 41
    melekenin vurduğu ~300 000 kapı, örnek başına **baştan** vuruluyordu;
    halbuki kapılar örnekten bağımsızdır ve durum zaten ``(B, d)``
    şeklindedir. Yâni aynı iş B kere tekrar ediliyordu.

    Yığınla aynı kapı bütün örneklere **tek geçişte** vurulur. Ölçüldü
    (``tanilama/hiz_teftisi.py``)::

        B=1   L=8      62 belirteç/sn
        B=128 L=4096  ~175 000 belirteç/sn

    Yığın boyu ``nefs``in kendi ayarından okunur; veri ondan büyükse
    dilimlenir, küçükse **son örnek tekrarlanır ve fazlası atılır** --
    sessizce değil, dilim uzunluğu kadar netice alınır.
    """
    from .qegitim import belirtecleri_kodla
    haller: List[np.ndarray] = []
    lifliler: List[np.ndarray] = []
    hedefler: List[int] = []
    baglamlar: List[Sequence[int]] = []
    sektor: List[Tuple[int, int]] = []
    veri = list(veri)
    B = max(1, int(getattr(nefs.ayar, "yigin", 1)))
    kubit = int(nefs.ayar.veri_lifi)
    for bas in range(0, len(veri), B):
        dilim = veri[bas:bas + B]
        # **GENİŞLİK TABANDIR** (ferman 1-N): gelen dizi basamak
        # akışıdır, belirteç akışı değil. ``kubit`` = veri lifi = taban.
        E = np.stack([belirtecleri_kodla(list(bag), kubit, kubit)
                      for bag, _h in dilim])
        if E.shape[0] < B:
            E = np.concatenate(
                [E, np.repeat(E[-1:], B - E.shape[0], axis=0)], axis=0)
        q = nefs.idrak_et(E)
        assert q.y.B == B, (
            "yazmaç yığını %d, istenen %d -- ayar ile veri uyuşmuyor"
            % (q.y.B, B))
        # ── LİF YAPISI ARTIK ÜÇ KARO (zabıt Yol 3: [16,16,16]) ──────
        # Mizan **iki** eksen ister: veri lifi ve hükmün tamamı. Yazmaç
        # ise hükmü karolara böldü. Düz bellek dizilimi aynı olduğu için
        # ``(B, n_v, −1)`` görünümü hükmü tek eksende toplar; ayrı bir
        # ayar alanına hâcet yoktur, yapı yazmacın kendisinden okunur.
        n_v = int(q.y.ayar.lif[0])
        M_hepsi = np.asarray(q.y.psi, complex).reshape(B, n_v, -1)
        assert M_hepsi.size > 0, "ileri geçiş BOŞ durum verdi"
        # Belirteç lifi üstündeki hâl: indirgenmiş yoğunluğun baş
        # özvektörü. (Ölçümdür, kesme değildir: hiçbir bileşen atılmaz.)
        rho = np.einsum('bvh,bwh->bvw', M_hepsi, M_hepsi.conj())
        rho = 0.5 * (rho + np.conj(np.swapaxes(rho, -1, -2)))
        _w, V = np.linalg.eigh(rho)
        for t, (bag, hedef) in enumerate(dilim):
            lifliler.append(M_hepsi[t])
            haller.append(np.asarray(V[t][:, -1], complex))
            # **HEDEF BİR BASAMAKTIR** ve ``[0, taban)`` aralığındadır.
            # Evvelce ``% sozluk`` alınıyordu; sözlük artık 200 019 ve
            # o mod, hedefi yazmacın taşıyamayacağı bir sayıda
            # bırakırdı. Basamak akışında hedef zaten aralıktadır;
            # ``assert`` onu **denetler**, sessizce kırpmaz.
            hb = int(hedef)
            assert 0 <= hb < int(kubit), (
                "hedef basamak taşıyıcının dışında: %d ∉ [0,%d) -- veri "
                "katmanı tip vektörüne çevirmemiş olabilir (ferman 1-N)"
                % (hb, kubit))
            hedefler.append(hb)
            baglamlar.append(list(bag))
        if not sektor:
            sektor = [q.y.sektor(ad) for ad, _ in q.ayar.kulli_alanlar]
    assert haller, "BOŞ veriyle mizan kurulamaz"
    assert len(haller) == len(veri), (
        "ileri geçiş %d örnek aldı, %d netice verdi -- örnek kayboldu"
        % (len(veri), len(haller)))
    return {"hal": haller, "lifli": lifliler, "hedef": hedefler,
            "bağlam": baglamlar, "sektör": sektor}


def kulli_mizan(nefs, veri, p=None, sozluk: int = 16,
                ayar: Optional[MizanAyari] = None,
                hafiza: Optional[Hafiza] = None, adim: int = 0,
                kademe_gorevleri=None, ne: str = "toplam"
                ) -> Dict[str, Any]:
    """``ℒ_Küllî = ℒ_Rezonans + λ₁ℒ_Çevrim + λ₂ℒ_Monogami + λ₃ℒ_Hodge``.

    ``ne="toplam"`` yalnız ``kayıp``; ``ne="döküm"`` dört kefeyi ayrı
    ayrı ve çevrim sınıflarının sayımını da verir.

    ``hafiza`` verilirse rüşt çizelgesi işler: tenakuz cezasının
    ``α`` payı ağırlıklardan **çekilir** ve hafızaya nakşedilir.
    """
    a = ayar or MizanAyari()
    if p is not None:
        nefs.yukle(np.asarray(p, float))
    veri = list(veri)
    assert veri, "BOŞ veriyle mizan kurulamaz"
    ileri = _ileri(nefs, veri, sozluk)

    # ── 1. REZONANS (Uhlmann) ─────────────────────────────────────
    n_v = ileri["lifli"][0].shape[0]
    rho_model = np.zeros((n_v, n_v), complex)
    for M in ileri["lifli"]:
        w = float(np.sum(np.abs(M) ** 2)) or 1.0
        rho_model += (M @ M.conj().T) / w
    rho_model /= len(ileri["lifli"])
    say = np.zeros(n_v, float)
    for t in ileri["hedef"]:
        say[int(t) % n_v] += 1.0
    say /= say.sum()
    rho_veri = np.diag(say).astype(complex)
    F = uhlmann(rho_veri, rho_model)
    L_rez = float(1.0 - F)

    # ── 2. ÇEVRİM (Wilson holonomisi) + L_TENAKUZ ─────────────────
    cv = _cevrimleri_tara(ileri["hal"], a, ileri["bağlam"],
                          ileri["hedef"], n_v)
    L_cev = float(cv["ceza"])
    L_ten = float(cv["bariyer"]["ceza"])

    # ── 3. MONOGAMİ (CKW'nin ⊕ mukabili) ──────────────────────────
    mono, mono_sol, mono_sag = _monogami(
        np.stack(ileri["lifli"]), ileri["sektör"])
    n_o = len(ileri["lifli"])
    L_mon = float(mono / n_o)

    # ── 3b. ENGELLENME (nefs/ayna.py'nin halkası FİİLEN KOŞAR) ────
    eng = engellenme(np.stack([np.asarray(h, complex).reshape(-1)
                               for h in ileri["hal"]]), a)
    L_eng = float(eng["ceza"])

    # ── 4. HODGE (verinin eş-zamanlılık çizgesi) ──────────────────
    D = _laplasyen(ileri["bağlam"], n_v)
    psi = np.zeros(n_v, complex)
    for h in ileri["hal"]:
        psi += h
    nrm = float(np.linalg.norm(psi))
    assert nrm > 0.0, "yığın hâli sıfıra çöktü -- Hodge ölçülemez"
    psi /= nrm
    # **QSVT HODGE SÜZGECİ FİİLEN KOŞAR** (``nefs/qudit.py:suz``).
    # Ham ``⟨Ψ|Δ|Ψ⟩`` bütün pürüzü sayar; halbuki pürüzün bir kısmı
    # yüksek frekanslı gürültüdür, tenakuz değil. QSVT süzgeci
    # Chebyshev polinomuyla harmonik bileşeni (``Δ``nın çekirdeğini)
    # ayırır; **artan** kısım hakiki tenakuzdur.
    #
    # ``qsvt = 0`` ile kapatılır ve ham enerji ölçülür -- fark
    # görülebilsin diye ikisi de dönüyor.
    L_ham = float(np.real(np.vdot(psi, D @ psi)))
    if int(a.qsvt) > 0 and psi.size >= 4:
        from .qudit import QuditAyari, suz
        qa = QuditAyari(d=int(psi.size), qsvt=int(a.qsvt),
                        derece=int(a.qudit_derece), yon=int(a.qudit_yon))
        harmonik = np.asarray(suz(D, psi, qa), complex).reshape(-1)
        artik = psi - harmonik
        nrm_a = float(np.linalg.norm(artik))
        L_hod = (float(np.real(np.vdot(artik, D @ artik))) / (nrm_a ** 2)
                 if nrm_a > 1e-12 else 0.0)
    else:
        L_hod = L_ham
    assert L_hod >= -1e-9, (
        "Hodge enerjisi NEGATİF çıktı (%.6f) -- Laplasyen PSD değil, "
        "ceza ödüle dönmüş demektir" % L_hod)
    L_hod = max(0.0, L_hod)

    # ══════════════════════════════════════════════════════════════
    #  TABAKALI MİZANIN İKİ YENİ KEFESİ (nefs/tabakali_mizan.py)
    # ══════════════════════════════════════════════════════════════
    #
    # Öteki iki mertebe **zaten yukarıdadır**: ``L_uzay ≡ L_rez``
    # (Uhlmann) ve ``L_tip ≡ L_hod`` (Hodge). Aynı şeyi ikinci isimle
    # yazmak terkip değil ikilemedir (ferman 3).
    from .tabakali_mizan import kategori_kaybi, nokta_kaybi
    kat = kategori_kaybi(ileri["hal"], azami=int(a.cevrim_sayisi) * 4,
                         tohum=int(a.tohum))
    nok = nokta_kaybi(ileri["lifli"], ileri["hedef"], n_v)
    L_kat = float(kat["kayıp"])
    L_nok = float(nok["kayıp"])

    # ══════════════════════════════════════════════════════════════
    #  ŞÜPHE MANİFOLDU (nefs/suphe.py)
    # ══════════════════════════════════════════════════════════════
    #
    # Teâruz, modal dallanma, Liouville sönümü ve merak kancası.
    # Neticesi kullanılır: tevakkuf eden örnekler ``hafıza``ya
    # ``TEVAKKUF`` hükmüyle yazılır (aşağıda).
    from .suphe import SupheAyari, suphe_manifoldu
    sup = suphe_manifoldu(
        ileri["hal"], cv["ω"],
        ayar=SupheAyari(acik=int(a.suphe_acik), sonum=float(a.suphe_sonumu),
                        kip_kenari=float(a.kenar) * 5.0,
                        parite_lifi=int(a.parite_lifi)))

    # ══════════════════════════════════════════════════════════════
    #  MANTIK YÜRÜTME SEFERİ (nefs/usul.py) -- 7/24 DEĞİL
    # ══════════════════════════════════════════════════════════════
    #
    # Kalp yoklar; yalnız karanlık çevrimler için sefer açılır.
    from .usul import UsulAyari, usul_kos
    usl = usul_kos(ileri["hal"], cv["indis"], cv["ω"],
                   UsulAyari(acik=int(a.usul_acik), had=float(a.usul_haddi),
                             sefer=int(a.usul_seferi)))

    # ══════════════════════════════════════════════════════════════
    #  RÜŞT KİLİDİ -- TAKVİM **VE** MUAYENE (nefs/rust.py)
    # ══════════════════════════════════════════════════════════════
    from .rust import RustAyari, rust_kilidi, topolojik_yirtik
    ra = RustAyari(t0=float(a.rust_t0), tau=float(a.rust_tau),
                   kapanis=float(a.rust_kapanis),
                   muayene=int(a.rust_muayene),
                   toplam_adim=int(a.toplam_adim))
    yirtik = topolojik_yirtik(ileri["bağlam"], n_v)
    kilit = rust_kilidi(int(adim), float(yirtik["dF_dec"]),
                        int(yirtik["h1"]), ra)
    alfa = float(kilit["α"])
    # Bebeklikte (α→0) tenakuz cezasının tamamı fıtrata akar; rüştte
    # (α→1) fıtrattan çekilip hafızaya nakşedilir.
    fitrata = (1.0 - alfa) * L_cev
    hafizaya = alfa * L_cev
    if hafiza is not None and cv["çevrim"]:
        for (om, ds, _c), hidx in zip(
                cv["çevrim"], range(len(cv["çevrim"]))):
            hukum = (CERH if om < -1.0 + a.kenar else
                     TEVAKKUF if om > 1.0 - a.kenar else TASDIK)
            # **ŞÜPHENİN NETİCESİ BURADA KULLANILIR.** Rapora yazılıp
            # bırakılsaydı bağlanmış olmazdı (ferman 1-C/b). Yakîn
            # tevakkuf eşiğinin altına inmişse hüküm **TASDİK
            # OLAMAZ**: teâruz hâlinde mühür vurmak, delilsiz zannı
            # hafızaya hakikat diye nakşetmek olurdu.
            j = hidx % len(ileri["hal"])
            mu = sup.get("μ")
            if (hukum == TASDIK and mu is not None and len(mu) > j
                    and float(mu[j]) < 0.35):
                hukum = TEVAKKUF
            hafiza.yaz(ileri["hal"][j], omega=om, hukum=hukum)
    # ── Lan_K: SEFERİN DOĞURDUĞU HÜKÜM ZİHNE MAL EDİLİR ────────────
    # Zabıt: *"Çıktı: sağlamlaştırılmış, genişletilmiş ve zihne mal
    # edilmiş yeni bilgi tensörü."* Hafıza bu mimaride müdrikenin
    # kalıcı yüzüdür: hazineye yazılır ve çıkarımda Zeno budamasını
    # besler. Sefer bir hüküm doğurduysa oraya **TASDİK** ile girer --
    # zira hadd-i evsatı tasfiye edilmiş ve burhânı alınmıştır.
    if hafiza is not None:
        for _j, _netice in usl.get("netice", ()):
            hafiza.yaz(_netice, omega=1.0, hukum=TASDIK)

    # ══════════════════════════════════════════════════════════════
    #  TABAKALI TERKİP -- ZABITIN BİRLEŞİK KAYIP FONKSİYONU
    # ══════════════════════════════════════════════════════════════
    #
    #     L_toplam = L_nokta + α·L_uzay + β·L_kategori + γ·L_tip
    #
    # ``α = 1``dir ve bir katsayı değil **çıpadır**: ``L_uzay`` mizanın
    # veriye bağlandığı tek yerdir (``L_rez``, Uhlmann). ``γ`` zaten
    # ``lam_tip``, ``β`` ise ``lam_kategori``.
    #
    # Mizanın kendi kefeleri (çevrim, tenakuz, monogami, engel) bunun
    # **üstüne** binmez, yanına gelir: onlar hükmün iç tutarlılığını,
    # tabakalı mizan ise hükmün dış hizasını ölçer.
    #
    # **SEFERİN NETİCESİ MİZANA GİRER.** Evvelce ``usul_kos`` çağrılıyor,
    # neticesi yalnız rapora yazılıyordu: sefer koşuyor fakat hiçbir şeyi
    # değiştirmiyordu. Ferman 1-C(b): bağlamak, neticenin **kullanılması**
    # demektir. Kapanmayan gedik bir epistemik borçtur ve bedavaysa
    # mantık yürütmenin tâlime hiçbir tesiri olmaz.
    L_gedik = float(a.lam_cevrim) * float(usl["borç"])
    kayip = (float(a.lam_nokta) * L_nok                     # 0. nokta
             + L_rez                                        # 1. uzay (α=1)
             + float(a.lam_kategori) * L_kat                # 2. kategori
             + float(a.lam_tip) * L_hod                   # 3. tip
             + float(a.lam_cevrim) * fitrata
             + float(a.lam_tenakuz) * L_ten
             + L_gedik
             + float(a.lam_monogami) * L_mon
             + float(a.lam_engel) * L_eng)
    assert np.isfinite(kayip), "mizan sonlu değil"

    if ne == "toplam":
        return {"kayıp": float(kayip)}
    if ne != "döküm":
        raise ValueError("mizan kipi bilinmiyor: %r" % (ne,))
    return {"kayıp": float(kayip), "rezonans": L_rez, "sadakat": F,
            # ── tabakalı mizan ────────────────────────────────────
            "nokta": L_nok, "nokta_isabet": float(nok["isabet"]),
            "kategori": L_kat, "kategori_ihlâl": int(kat["ihlâl"]),
            "kategori_deneme": int(kat["deneme"]),
            # ── L_Tenakuz ─────────────────────────────────────────
            "tenakuz_bariyer": L_ten,
            "tenakuz_azamî": float(cv["bariyer"]["azamî"]),
            "tenakuz_tavan": float(cv["bariyer"]["tavan"]),
            "dışlama_ortalama": float(cv["bariyer"]["dışlama_ortalama"]),
            # ── rüşt kilidi ───────────────────────────────────────
            "rüşt_takvim": float(kilit["takvim"]),
            "rüşt_muayene": float(kilit["muayene"]),
            "dF_dec": float(yirtik["dF_dec"]), "h1": int(yirtik["h1"]),
            # ── sefer ve şüphe ────────────────────────────────────
            "sefer": int(usl["sefer"]), "gedik": int(usl["gedik"]),
            "sefer_kapanan": int(usl["kapanan"]),
            "gedik_borcu": float(usl["borç"]), "L_gedik": float(L_gedik),
            "tevakkuf": int(sup["tevakkuf"]),
            "çevrim": L_cev, "çevrim_fıtrata": float(fitrata),
            "çevrim_hafızaya": float(hafizaya),
            "monogami": L_mon, "monogami_sol": float(mono_sol / n_o),
            "monogami_sağ": float(mono_sag / n_o),
            "hodge": L_hod, "hodge_ham": L_ham, "engel": L_eng,
            "engel_bağ": int(eng["bağ"]), "engel_toplam": int(eng["toplam"]),
            "engel_öbek": int(eng.get("öbek", 0)),
            "engel_şahidi": float(eng.get("şahit_nispeti", 0.0)),
            "α_rüşt": float(alfa),
            "meşru": int(cv["meşru"]), "kısır": int(cv["kısır"]),
            "tenakuz": int(cv["tenakuz"]), "engel": int(cv["engel"]),
            "ihlâl": int(mono_sol > mono_sag),
            "ω_ortalama": float(np.mean(cv["ω"])) if cv["ω"] else 0.0,
            "örnek": len(veri)}


# ══════════════════════════════════════════════════════════════════
#  6. VERİ KENDİNİ DÖRDE AYIRIYOR MU? (zabıt V. fasıl)
# ══════════════════════════════════════════════════════════════════
def mizan_cetveli(nefs, veri, p=None, sozluk: int = 16,
                  ayar: Optional[MizanAyari] = None) -> Dict[str, int]:
    """Veriyi **etiketsiz** dört kampa ayır: hakikat/tenakuz/şüpheli/gürültü.

    ==========  ==========  ==========  ==========  =================
    parça       Rezonans    Çevrim      Hodge       hüküm
    ==========  ==========  ==========  ==========  =================
    hakikat     düşük       0           0           tasdik
    tenakuz     yüksek      ≠ 0         yüksek      cerh
    şüpheli     düşük       0           orta        tevakkuf
    gürültü     yüksek      0           0           tecrit
    ==========  ==========  ==========  ==========  =================

    Eşikler yığının **kendi medyanıdır**, dışarıdan verilen bir sabit
    değil: ayrım nispîdir ve veri değişince eşik de değişir.
    """
    a = ayar or MizanAyari()
    if p is not None:
        nefs.yukle(np.asarray(p, float))
    veri = list(veri)
    assert veri, "BOŞ veri tasnif edilemez"
    ileri = _ileri(nefs, veri, sozluk)
    n_v = ileri["lifli"][0].shape[0]
    D = _laplasyen(ileri["bağlam"], n_v)

    rez: List[float] = []
    hod: List[float] = []
    cev: List[float] = []
    m = len(ileri["hal"])
    for i, (M, h, t) in enumerate(zip(ileri["lifli"], ileri["hal"],
                                      ileri["hedef"])):
        w = float(np.sum(np.abs(M) ** 2)) or 1.0
        rho = (M @ M.conj().T) / w
        hedef = np.zeros((n_v, n_v), complex)
        hedef[int(t) % n_v, int(t) % n_v] = 1.0
        rez.append(1.0 - uhlmann(hedef, rho))
        hh = h / (np.linalg.norm(h) or 1.0)
        hod.append(float(np.real(np.vdot(hh, D @ hh))))
        if m >= int(a.cevrim_boyu):
            idx = [(i + k) % m for k in range(int(a.cevrim_boyu))]
            _, om, _yol = holonomi([ileri["hal"][j] for j in idx])
            cev.append(float(max(0.0, -om)))
        else:
            cev.append(0.0)

    r_esik = float(np.median(rez))
    h_esik = float(np.median(hod))
    c_esik = float(a.kenar)
    out = {"hakikat": 0, "tenakuz": 0, "şüpheli": 0, "gürültü": 0}
    for r_, c_, h_ in zip(rez, cev, hod):
        if c_ > c_esik:
            out["tenakuz"] += 1
        elif r_ > r_esik and h_ <= h_esik:
            out["gürültü"] += 1
        elif r_ <= r_esik and h_ > h_esik:
            out["şüpheli"] += 1
        else:
            out["hakikat"] += 1
    assert sum(out.values()) == len(veri), "tasnif toplamı tutmuyor"
    return out


# ══════════════════════════════════════════════════════════════════
#  7. RAPOR -- her iddianın kendi sayısı, kırmızı yanabilir
# ══════════════════════════════════════════════════════════════════
def rapor(profil: str = "kısa") -> str:                  # pragma: no cover
    """Mizan fiilen ayırıyor mu -- **ölç**, iddia etme."""
    import time

    from main.egitim import PROFILLER
    from nefs.melekeler import QNefs
    from nefs.musahede import gorevleri_getir
    from nefs.qegitim import ornekler

    ayar = PROFILLER.get(profil, PROFILLER["kısa"])
    a = MizanAyari(tohum=ayar.tohum, cevrim_sayisi=12)
    g = list(gorevleri_getir("training"))[:12]
    veri = ornekler(g, azami=int(ayar.ornek_sayisi), pencere=ayar.pencere,
                    sozluk=ayar.sozluk, tohum=ayar.tohum)
    nefs = QNefs(ayar.tohum, ayar.qayar())
    nefs.idrak_et(np.zeros((2, ayar.veri_lifi)))
    haf = Hafiza(kapasite=64)

    t0 = time.perf_counter()
    d = kulli_mizan(nefs, veri, nefs.vektor(), ayar.sozluk, ayar=a,
                    hafiza=haf, adim=0, ne="döküm")
    sure = time.perf_counter() - t0
    cet = mizan_cetveli(nefs, veri, nefs.vektor(), ayar.sozluk, ayar=a)

    # --- ÖLÇÜ KIRMIZI YANABİLİYOR MU? Parite taklası ELLE kurulur.
    n = 8
    r = np.random.default_rng(0)
    e = np.eye(n, dtype=complex)
    # Üç dik hâl: a → b → c → a. Dik hâllerde holonomi aşikâr değildir.
    _, om_dik, yol_dik = holonomi([e[0], e[1], e[2]])
    # Aynı hâl üç kere: kısır döngü, U = I beklenir.
    _, om_kisir, yol_kisir = holonomi([e[0], e[0], e[0]])
    # Parite taklası: a → b → −a. Başladığı aksiyomu inkâr eden çevrim.
    # **ESKİ SINAMA BİR KÜME FAZIYDI.** Burada ``[a, b, −a]`` çevrimi
    # "parite taklası" diye sınanıyordu. Halbuki ``|−a⟩`` ile ``|a⟩``
    # **aynı fizikî hâldir** (küme fazı gözlenemez); o hâlde o çevrim
    # üç köşeli değil iki köşelidir ve kod zaten "iki adımlı çevrim
    # daima birim verir" diyor. Yâni bayrak sınama, ölçülemeyen bir şeyi
    # ölçüyordu ve ``ω``nın seyreltmesini de gizliyordu.
    #
    # Yerine **ölçünün cevap verip vermediği** sınanır: çevrim açıldıkça
    # ``ω`` düşmeli. ``θ = 0``da kısır (+1), ``θ`` büyüdükçe iner.
    _ac = [0.0, 0.25 * math.pi, 0.5 * math.pi]
    _egri = []
    for _th in _ac:
        _c, _s = math.cos(_th), math.sin(_th)
        _b = _c * e[0] + _s * e[1]
        _d = math.cos(2 * _th) * e[0] + math.sin(2 * _th) * e[1]
        _egri.append(float(holonomi([e[0], _b, _d])[1]))
    U_par, om_par, yol_par = holonomi([e[0], e[1], -e[0]])
    # ══════════════════════════════════════════════════════════════
    #  YENİ KEFELER KIRMIZI YANABİLİYOR MU? (ferman 5)
    # ══════════════════════════════════════════════════════════════
    #
    # Ana akışta bu üç kefe sıfır çıkıyor (bütün çevrimler kısır) ve
    # sıfır bir kefe hiçbir şey ölçmüyor da olabilir. Onun için elle
    # kurulmuş bir **tenakuz** verilir ve yanıp yanmadığı ölçülür.
    from .tenakuz import TenakuzAyari, log_bariyer
    from .tabakali_mizan import kategori_kaybi
    from .rust import RustAyari, rust_kilidi
    _ta = TenakuzAyari(eps=float(a.tenakuz_eps), tau=float(a.dislama_tau))
    # (1) Tam takla ``U_C ≈ −I``: bariyer tavana yaklaşmalı.
    _bar_par = log_bariyer(U_par[None, :, :], np.ones(1), _ta)
    _bar_bir = log_bariyer(np.eye(U_par.shape[0], dtype=complex)[None],
                           np.ones(1), _ta)
    # (2) Kategori: **kasten geçişsiz** üç hâl. Rastgele üç dik vektörde
    #     ``givens(a,c) ≠ givens(b,c)·givens(a,b)`` olmalıdır.
    _rk = np.random.default_rng(7)
    _dik = np.linalg.qr(_rk.normal(size=(8, 8))
                        + 1j * _rk.normal(size=(8, 8)))[0]
    _kat_kirmizi = kategori_kaybi([_dik[:, 0], _dik[:, 1], _dik[:, 2]],
                                  azami=1, tohum=0)
    _kat_yesil = kategori_kaybi([_dik[:, 0], _dik[:, 0], _dik[:, 0]],
                                azami=1, tohum=0)
    # (3) Rüşt: yırtık varken kilit tutuyor mu (aynı vakitte)?
    _ra = RustAyari(t0=float(a.rust_t0), tau=float(a.rust_tau),
                    kapanis=float(a.rust_kapanis), muayene=1,
                    toplam_adim=int(a.toplam_adim))
    _rust_saglam = rust_kilidi(a.toplam_adim, 0.0, 0, _ra)
    _rust_yirtik = rust_kilidi(a.toplam_adim, 0.0, 2, _ra)
    # (4) SEFER: ana akışta hiç açılmıyor (bütün çevrimler kısır, ω=+1)
    #     ve bu **doğru** davranıştır -- fakat "hiç açılmıyor" ile
    #     "açılamıyor" ayrı şeydir. Elle bir gedik verilir.
    from .usul import UsulAyari, usul_beyani, usul_kos, usul_sifirla
    _u_once = usul_beyani()["sefer"]
    _ua = UsulAyari(acik=1, had=0.0, sefer=2)
    _gedikli = usul_kos([_dik[:, i] for i in range(4)],
                        [[0, 1, 2], [1, 2, 3]], [-0.9, +0.9], _ua)
    _kapali = usul_kos([_dik[:, i] for i in range(4)],
                       [[0, 1, 2]], [-0.9], UsulAyari(acik=0))
    # (5) SADAKAT: kapı kapanınca yırtık sektör duruyor mu?
    from .sadakat import SadakatAyari, sadakat_uygula
    _yirtik_hal = np.ones(64, complex) / 8.0
    _sa = SadakatAyari(parite_lifi=1, lif_yapisi=(8, 8))
    _sad_acik = sadakat_uygula(_yirtik_hal.copy(),
                               SadakatAyari(acik=1, parite_lifi=1,
                                            lif_yapisi=(8, 8)))
    _sad_kapali = sadakat_uygula(_yirtik_hal.copy(),
                                 SadakatAyari(acik=0, parite_lifi=1,
                                              lif_yapisi=(8, 8)))

    s = ["=== MÎZÂN-I KÜLLÎ (nefs/kulli_mizan.py) ===", "",
         "  TABAKALI MİZAN (zabıt): L = L_nokta + α·L_uzay + β·L_kategori + γ·L_tip",
         "  L_uzay ≡ ℒ_Rezonans (Uhlmann), L_tip ≡ ℒ_Hodge -- terkip, tabela değil.",
         "  Yanına mizanın kendi kefeleri: λ₁ℒ_Çevrim + λ_t ℒ_Tenakuz + λ₂ℒ_Monogami + λ₄ℒ_Engel",
         "", "  --- KEFELER (%d örnek, %.2f sn) ---" % (d["örnek"], sure),
         "    ℒ_Rezonans (Uhlmann)  : %.6f   (sadakat F = %.6f)"
         % (d["rezonans"], d["sadakat"]),
         "    ℒ_Çevrim   (Wilson)   : %.6f   ω̄ = %+.4f"
         % (d["çevrim"], d["ω_ortalama"]),
         "        meşru %d | kısır %d | tenakuz %d | engel %d"
         % (d["meşru"], d["kısır"], d["tenakuz"], d["engel"]),
         "    ℒ_Monogami (CKW ⊕)    : %.6f   (Σ_A %.4f vs hepsi %.4f)"
         % (d["monogami"], d["monogami_sol"], d["monogami_sağ"]),
         "    ℒ_Hodge    (Δ|Ψ⟩=0)   : %.6f" % d["hodge"],
         "    ℒ_Tenakuz  (log bar.) : %.6f   azamî %.4f / tavan %.4f"
         % (d["tenakuz_bariyer"], d["tenakuz_azamî"], d["tenakuz_tavan"]),
         "        S_dışlama ortalaması %.4f" % d["dışlama_ortalama"],
         "    ℒ_Kategori (funktör)  : %.6f   ihlâl %d/%d"
         % (d["kategori"], d["kategori_ihlâl"], d["kategori_deneme"]),
         "    ℒ_Nokta    (kısmî Born): %.6f   tepe isabeti %.4f"
         % (d["nokta"], d["nokta_isabet"]),
         "    ─────────────────────────────────────",
         "    ℒ_Küllî               : %.6f" % d["kayıp"],
         "",
         "  --- RÜŞT KİLİDİ: TAKVİM **VE** MUAYENE (nefs/rust.py) ---",
         "    ölçülen ‖dF‖² = %.6f   ‖H¹‖ = %d  (kapanmamış delik)"
         % (d["dF_dec"], d["h1"]),
         "    takvim σ(·) = %.4f   muayene exp(·) = %.4f   α = %.4f"
         % (d["rüşt_takvim"], d["rüşt_muayene"], d["α_rüşt"]),
         "    → tenakuzun %%%.1f'i FITRATA, %%%.1f'i HAFIZAYA"
         % (100 * (1 - d["α_rüşt"]), 100 * d["α_rüşt"]),
         "    kör takvim olsaydı α = %.4f olurdu (fark: muayene kapısı)"
         % d["rüşt_takvim"],
         "",
         "  --- ÖLÇÜ KIRMIZI YANABİLİYOR MU? (elle kurulan üç hal) ---",
         "    üç dik hâl (engellenme): ω = %+.6f  yol = %.4f   %s"
         % (om_dik, yol_dik,
            "yol katedildi" if yol_dik > 1e-9 else "⚠ YOL SIFIR"),
         "    aynı hâl üç kere       : ω = %+.6f  yol = %.4f   %s"
         % (om_kisir, yol_kisir,
            "KISIR (doğru)" if yol_kisir < 1e-9 else "⚠ KISIR GÖRÜLMEDİ"),
         "    ω LİF BOYUNDAN BAĞIMSIZ MI (evvelce ω ≥ 1−4/n idi):",
         "      çevrim açıldıkça ω: θ=0 → %+.4f | θ=π/4 → %+.4f | "
         "θ=π/2 → %+.4f   %s"
         % (_egri[0], _egri[1], _egri[2],
            "CEVAP VERİYOR" if (_egri[0] > _egri[1] > _egri[2])
            else "⚠ CEVAPSIZ"),
         "      (eski 'parite taklası a→b→−a' sınaması KALDIRILDI: "
         "|−a⟩ ile |a⟩ aynı fizikî hâldir, o bir küme fazıydı; ω = %+.4f)"
         % om_par,
         "    L_Tenakuz bariyeri     : U=I → %.6f | U≈−I → %.6f  "
         "(tavan %.4f)   %s"
         % (_bar_bir["ceza"], _bar_par["ceza"], _bar_par["tavan"],
            "YANDI" if _bar_par["ceza"] > 10 * _bar_bir["ceza"] + 1e-6
            else "⚠ YANMADI"),
         "    L_Kategori             : eş hâl → %.3e | dik üçlü → %.6f   %s"
         % (_kat_yesil["kayıp"], _kat_kirmizi["kayıp"],
            "YANDI" if _kat_kirmizi["kayıp"] > 1e-6
            and _kat_yesil["kayıp"] < 1e-9 else "⚠ YANMADI"),
         "    Rüşt kilidi (t=T)      : yırtıksız α = %.4f | ‖H¹‖=2 iken "
         "α = %.4f   %s"
         % (_rust_saglam["α"], _rust_yirtik["α"],
            "KİLİTLENDİ" if _rust_yirtik["α"] < 0.01 * _rust_saglam["α"]
            else "⚠ KİLİTLENMEDİ"),
         "    Sefer (nefs/usul.py)   : gedikli → %d sefer | kapı kapalı "
         "→ %d sefer   %s"
         % (_gedikli["sefer"], _kapali["sefer"],
            "AÇILDI" if _gedikli["sefer"] > 0 and _kapali["sefer"] == 0
            else "⚠ AÇILMADI"),
         "    Sadakat (nefs/sadakat.py): açık → alarm %d→%d | kapalı → "
         "alarm %d→%d   %s"
         % (_sad_acik["alarm_önce"], _sad_acik["alarm_sonra"],
            _sad_kapali["alarm_önce"], _sad_kapali["alarm_sonra"],
            "SÖNDÜRDÜ" if _sad_acik["alarm_sonra"] == 0
            and _sad_kapali["alarm_sonra"] == 1 else "⚠ SÖNDÜREMEDİ"),
         "",
         "  --- VERİ KENDİNİ DÖRDE AYIRDI MI? (etiketsiz) ---",
         "    hakikat %d | tenakuz %d | şüpheli %d | gürültü %d"
         % (cet["hakikat"], cet["tenakuz"], cet["şüpheli"], cet["gürültü"]),
         "",
         "  --- HAFIZA (ağırlık değil, hadise) ---",
         "    %r" % (haf.beyan(),)]
    return "\n".join(s)


if __name__ == "__main__":                               # pragma: no cover
    import sys
    print(rapor(sys.argv[1] if len(sys.argv) > 1 else "kısa"))
