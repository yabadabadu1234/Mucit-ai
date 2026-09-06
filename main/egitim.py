"""
KÜLLÎ DİMAĞ -- TÂLİM MOTORU (PADİŞAH TÂLİMİ)
Dosya: main/egitim.py

===================================================================
TEK HAT VARDIR -- MECLİS İMHA EDİLDİ
===================================================================

Evvelce burada **iki** tâlim hattı yan yana duruyordu:

1. ``kulli_kayip_talimi``  -- Mîzân-ı Küllî ile 44 QMelekeyi eniyiler.
2. ``dalga_talimi_kos``    -- 44 melekeyi bir "meclise" toplar,
   ``hamiltonyen_uret`` ile tek ``Ĥ_Dimağ``a indirger, QSVT ile soğutur.

Padişahın emri üç kısımdı ve icra edildi:

    (1) *"Evvela klasik bütün melekeleri imha edeceksin."*
        ``nefs/melekeler.py``deki 41 klasik ``Meleke`` sınıfı ve
        onların koşturucusu (``Nefs``, ``Durum``, ``AKIS``) imha edildi.
    (2) *"Sonra kalan kuantum melekelerini meclise sokan mekanizmayı
        derdest edip imha edeceksin, tamamen bozacaksın, ana akıştan
        çıkarıp sileceksin."*
        ``KulliMelekeManifoldu``, ``H_toplam``, ``melekelerin_dondurucusu``,
        ``bgcm_mizan_enerjisi``, ``melekeleri_kur`` ve buradaki
        ``KulliDalgaTalimMotoru``/``dalga_talimi_kos`` imha edildi.
    (3) *"Sonra zabıtlarda tarif edilen melekelerin formüllerini uygun
        hâle getirip ana akışa uygun şekilde bağlayacaksın."*
        Altı uzuv, umumiden hususiye, aşağıda bağlandı.

**İkinci hattın öğrenmediği ölçülmüştü ve saklanmamıştı:** zırh kaybı
üç çevrimde ``104,653426``da sabit kalıyordu. Meclis, melekeyi bir
katsayıya indirip ne okuduğunu ne yazdığını görünmez kılıyordu.

===================================================================
ZABITLARIN ALTI UZVU -- İKİSİ AYRI ŞEYDİR, KARIŞTIRILMAZ
===================================================================

    MANTIĞA SADAKAT (nefs/sadakat.py)     7/24 zemin. Bir meleke değil,
                                          varlık şartı. Gradyanı yok.
    MANTIK YÜRÜTME  (nefs/usul.py)        Aktif sefer. Kalp gedik
                                          hissedince açılır, kapanır.

    L_TENAKUZ       (nefs/tenakuz.py)     Log-bariyer × eş-zamanlı dışlama
    RÜŞT KİLİDİ     (nefs/rust.py)        Takvim × topolojik muayene
    TABAKALI MİZAN  (nefs/tabakali_mizan.py)  L_kategori + L_nokta
    ŞÜPHE           (nefs/suphe.py)       Teâruz, modalite, merak, sönüm

===================================================================
BLAS ÇEKİRDEK İNTİZAMI
===================================================================

Gerekçesi ölçüldü: küçük matrislerde BLAS iş parçacığı maliyeti hesabın
kendisini gömüyor (72×100'lük bir mesele için 60 devir 11,96 sn; tek
iplikte ve ters ön-hesapla 0,0029 sn). Çoklu süreçte ise iplikler
birbirinin çekirdeğini kırar.
"""
from __future__ import annotations

# --- BLAS ÇEKİRDEK İNTİZAMI: ``numpy``dan ÖNCE tek ipliğe sabitlenir.
#
# **Bu, `kulli_egitim.py`den alınmadı -- orada yoktu; buraya yeni
# kondu.** Gerekçesi bu turda ölçüldü: küçük matrislerde BLAS iş
# parçacığı maliyeti hesabın kendisini gömüyor (72×100'lük bir mesele
# için 60 devir 11,96 sn; tek iplikte ve ters ön-hesapla 0,0029 sn).
# Çoklu süreçte ise iplikler birbirinin çekirdeğini kırar.
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

import json                                              # noqa: E402
import sys                                               # noqa: E402
import time                                              # noqa: E402
from dataclasses import dataclass, field                 # noqa: E402
from typing import Dict, Optional, Sequence, Tuple       # noqa: E402

import numpy as np                                       # noqa: E402

from nefs.musahede import gorevleri_getir                                    # noqa: E402
from ogrenme.optimize import OptimizeAyari               # noqa: E402
from ogrenme.optimize import hoca_egit                   # noqa: E402
from main import hazine                             # noqa: E402
# ── MÎZÂN-I KÜLLÎ VE KUANTUM HAFIZASI ──────────────────────────────
# **USUL FERMANI (docs/zabit/USUL_UMUMIDEN_HUSUSIYE.md):** bu iki satır
# modüller HENÜZ YOKKEN yazıldı. Çağrı evvel yazılır, uzuv sonra; böylece
# bağlanmamış bir dosya yazmak imkânsız olur.
# ``rust`` ithal ediliyor fakat çağrılmıyordu -- kaldırıldı. Rüşt
# çizelgesi ``kulli_mizan``ın kendi içinde işler ve neticesi
# ``kefeler["α_rüşt"]`` ile buraya döner.
from nefs.kulli_mizan import (MizanAyari, kulli_mizan,   # noqa: E402
                              mizan_cetveli)
from nefs.hafiza import Hafiza                           # noqa: E402
# ── ZABIT 2'NİN KALAN ÜÇ USULÜ (Saf CPU 2026 Mimarisi) ────────────
# **USUL FERMANI:** üçünün de çağrısı, dosyalar YOKKEN buraya yazıldı.
#   1. usul  LimTDD    -- durumu DAG olarak sıkıştır (nefs/tdd.py)
#   2. usul  Stabilizer-- Clifford çerçevesinde tableau (nefs/kararname.py)
#   3. usul  Gölgeler  -- O(log M) ölçüm (nefs/golge.py)
# ── ZABIT: 1 GB/S GALOIS-CLIFFORD MOTORU ──────────────────────────
# **USUL FERMANI:** çağrılar dosya YOKKEN yazıldı.
#
#   nefs/galois.py   -- GF(2⁸) cismi, Stabilizer Tableau (XOR/AND),
#                       Palmer 2-bit rotasyonu. Sürekli Hilbert İPTAL.
#   nefs/tdd.py      -- artık HESAP MOTORU DEĞİL, yalnız kanonik
#                       DENETÇİ: çevrim kapanışında O(1) adres eşitliği.
from nefs.galois import (GaloisAyari, Tableau,            # noqa: E402
                         palmer_i, tableau_kur, gf_carp,
                         sbox_bukme, sbox_olcu)
from nefs.tdd import TddAyari, kanonik_adres              # noqa: E402
# ── ZABIT: NON-CLIFFORD VE STABILIZER RANK ÇIKMAZININ ÇÖZÜMÜ ──────
# **USUL FERMANI:** bu iki satır modüller HENÜZ YOKKEN yazıldı.
#
# İtiraz haklıdır ve tescillidir: Bravyi-Gosset (2016) gereğince saf
# kübit tablosuna tek bir non-Clifford kapı vurulursa stabilizer rank
# ``χ_stab ~ 2^{0,468 t}`` ile patlar. Zabıt bunu inkâr etmez; üç
# ispatlı çare koyar ve **üçü de burada koşar**:
#
#   1. nefs/matchgate.py     Valiant-Terhal-DiVincenzo FLO düalitesi.
#                            Sürekli açılı kapı kübitte non-Clifford,
#                            Majorana kovaryansında SO(2N) Givens: χ=1.
#   2. nefs/galois.py:sbox   Rijndael otomorfizmi x↦x²⁵⁴. Gayri-lineerlik
#                            transandantal değil cebrîdir; dallanma yok.
#   3. nefs/faz_polinomu.py  Amy-Maslov-Mosca CNOT-Dihedral teoremi.
#                            Köşegen fazlar tek Z_m tamsayı polinomunda.
from nefs.matchgate import (MatchgateAyari, flo_evrimi,   # noqa: E402
                            matchgate_mi)
from nefs.faz_polinomu import FazAyari, faz_oturt         # noqa: E402
# ── ZABIT: DERECE-12 FAZ PATLAMASI VE 1 GB/S DARBOĞAZI ────────────
# **USUL FERMANI:** bu satır modül HENÜZ YOKKEN yazıldı.
#
# Ölçümümüz kendi iddiamızı yere serdi: biriken fazın derecesi 12
# çıktı, yâni CNOT-Dihedral sınıfının dışında. Zabıtın hükmü:
# *"CNOT-Dihedral iddiasını resmî olarak iptal ediyoruz... yerine
# Galois Siklotomik Koset İndirgemesini koyuyoruz. Böylece derece 12,
# x³'ün iki ardışık Frobenius karesi olarak tek çevrimlik donanım
# komutuna iner."*
from nefs.siklotomik import (SiklotomikAyari,             # noqa: E402
                             koset_indirge, iz_esitligi)
# ── 41 MELEKENİN TAŞINDIĞI HAT VE KALICI HIZÖLÇER ─────────────────
# **USUL FERMANI:** bu iki satır modüller HENÜZ YOKKEN yazıldı.
#
#   nefs/qcekirdek.py    -- melekelerin vurduğu bütün kapılar bir
#                           **kapı bandına** yazılır ve bandın tamamı
#                           TEK C çağrısında icra edilir. Meleke
#                           kodları değişmez; değişen, kapının nerede
#                           koştuğudur.
#   tanilama/hizolcer.py -- hızölçer ana hatta KALICI olarak bağlanır:
#                           her küllî mizan çağrısı saatlenir, belirteç
#                           sayılır. Koşu sonunda değil, koşarken ölçer.
from nefs.qcekirdek import cekirdek_beyani                 # noqa: E402
from tanilama.hizolcer import (Hizolcer, hizolcer_bagla,   # noqa: E402
                               hizolcer_beyani)
# ── ZABIT: 1 TB/S GPU AKIŞI (4× L4 VRAM DOYUMU) ───────────────────
# **USUL FERMANI:** bu satır modül HENÜZ YOKKEN yazıldı.
#
# Zabıt iki dünyayı bıçakla ayırır ve ikisini karıştırmayı yasaklar:
#   HARİCÎ AKIŞ (PCIe)  -- kart başına 31,5 GB/s; dördü 126 GB/s.
#                          Dışarıdan 1 TB/s ham veri fırlatmak
#                          **fiziken imkânsızdır**.
#   DÂHİLÎ AKIŞ (VRAM)  -- 4×300 = 1200 GB/s. Durum VRAM'de yerleşikse
#                          yahut orada üretiliyorsa 1 TB/s mümkündür.
#
# O hâlde dört motor: (1) warp-seviyesi symplectic bitmask,
# (2) tek geçişli kaynaşık çekirdek (ara bellek YOK), (3) GPU-yerel
# bitstream genleşmesi (tohum girer, dalga açılır), (4) 4 kart arası
# P2P sınır kilidi (temas yalnız sınır dizeyi).
from nefs.gpu_akis import GpuAyari, gpu_akisi              # noqa: E402
from nefs.kararname import kararname                      # noqa: E402
from nefs.golge import (GolgeAyari, golge_al,             # noqa: E402
                        kestir)
# ══════════════════════════════════════════════════════════════════
#  ZABITLARIN ALTI UZVU -- **USUL FERMANI: DOSYALAR HENÜZ YOKKEN**
# ══════════════════════════════════════════════════════════════════
#
# Padişahın emri üç kısımdır: (1) klasik melekelerin imhası, (2) kalan
# kuantum melekelerini "meclise" sokan mekanizmanın imhası, (3) zabıtlarda
# tarif edilen melekelerin formüllerinin **ana akışa bağlanması**.
#
# Üçüncü kısım burada başlar ve umumiden hususiye gider: aşağıdaki altı
# satır, altı dosyanın hiçbiri yokken yazıldı. Yazılmayan koşmaz; çağrısı
# evvel yazılmayan dosya da yazılmaz (ferman 1).
#
#   nefs/sadakat.py   MANTIĞA SADAKAT -- bir meleke DEĞİL, sistemin
#                     varlık şartı. Her ileri geçişte parite alarmı
#                     yoklanır ve tenakuz Zeno sıfırlamasıyla söner.
#                     (zabıt: *Mantık ile Mantık Yürütme Arasındaki
#                     Ontolojik Ayrım*, 1. fasıl)
#   nefs/tenakuz.py   L_TENAKUZ -- log-bariyer × eş-zamanlı dışlama.
#                     ``−ln((Tr(I+Re U_C)+ε)/(2d+ε)) · S_dışlama(A,B)``
#                     Ayrık çevrim cezası sonsuza ıraksamaz; dışlama
#                     dizeyi hiç beraber görülmemiş kavram çiftlerine
#                     cezayı **ağırlaştırır**.
#   nefs/rust.py      HİBRİT RÜŞT KİLİDİ -- takvim ile muayenenin
#                     çarpımı: ``σ((t−t₀)/τ) · exp(−(‖dF‖²+‖H¹‖²)/σ²)``.
#                     Yalnız çizelgeye bakan rüşt, topolojisi yırtık bir
#                     dimağı da rüşte erdirirdi.
#   nefs/tabakali_mizan.py
#                     TABAKALI MİZAN -- kör NLL'nin yerine dört mertebe.
#                     Yeni olan iki kefe buradadır: ``L_kategori``
#                     (funktör kompozisyonu, etiketsiz) ve ``L_nokta``
#                     (kısmî Born). ``L_uzay`` ile ``L_tip`` YENİ DEĞİL:
#                     ikisi mizanda zaten vardır (bkz. ``kulli_mizan``).
#   nefs/usul.py      MANTIK YÜRÜTME SEFERİ -- 7/24 koşmaz. Kalp bir
#                     epistemik gedik hissedince Tertip bir M_usul
#                     manifoldu seçer, hadd-i evsat U_M† ile tasfiye
#                     edilir, netice Lan_K ile müdrikeye taşınır.
#   nefs/suphe.py     ŞÜPHE MANİFOLDU -- teâruz (``μ ← μ(1−|⟨ψ_P|ψ_¬P⟩|)``),
#                     modal dallanma, merak kancası ve Liouville sönümü.
from nefs.sadakat import (SadakatAyari, sadakat_uygula,   # noqa: E402
                          sadakat_beyani)
from nefs.tenakuz import (TenakuzAyari, log_bariyer,      # noqa: E402
                          dislama_dizeyi)
from nefs.rust import (RustAyari, rust_kilidi,            # noqa: E402
                       topolojik_yirtik)
from nefs.tabakali_mizan import (kategori_kaybi,          # noqa: E402
                                 nokta_kaybi)
from nefs.usul import UsulAyari, usul_beyani              # noqa: E402
from nefs.suphe import SupheAyari, suphe_beyani           # noqa: E402
# **FERMAN 1-G:** raporun yeri taht değil, kendi uzvudur.
from tanilama.beyan import (talim_beyani,                 # noqa: E402
                            kaggle_beyani)

#: Ağırlıkların yattığı dizin. ``main/cikarim.py`` buradan okur.
HAZINE_DIZINI = os.environ.get("MUCIT_HAZINE", "depo/hazine")

__all__ = ["EgitimAyari", "KISA_CPU", "ORTA", "AZAMI_KAGGLE",
           "tek_iplik_zorla", "gecit", "ogreniyor_mu",
           "kulli_kayip_talimi", "muhurle", "kos", "HAZINE_DIZINI"]


def tek_iplik_zorla() -> Dict[str, str]:
    """BLAS ipliğini 1'e sabitle; **hangi değişkenlerin konduğunu döndür**.

    ``numpy`` yüklendikten sonra çağrılırsa **geç kalmıştır** ve bu
    sessizce geçilmez: dönen sözlükte ``geç`` alanı doğru olur. Modül
    başındaki ayar asıl olandır; bu fonksiyon alt süreçler içindir.
    """
    ad = ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS",
          "NUMEXPR_NUM_THREADS")
    for a in ad:
        os.environ[a] = "1"
    return {"değişken": ",".join(ad), "geç": "numpy" in sys.modules}


# =====================================================================
#  HİYERARŞİK TÂLİM AYARLARI -- `kulli_egitim.py`den zerk edildi
# =====================================================================
@dataclass
class EgitimAyari:
    """Yazmaç, veri, dalga ve donanım ölçüleri **tek yerde**.

    Kullanıcı hükmü: *"modelin tüm parametrelerini en genel eğitim için
    mümkün olan hududun en sonuna kadar açmanı istiyorum."* Hiçbiri
    koda gömülü değildir.
    """
    ad: str = "kısa"
    # --- yazmaç (nefsin kendisi)
    #: **FERMANLA DEĞİŞTİ: 4 → 16.** İkili kodlama dalı imha edilince
    #: (``nefs/qegitim.py``) kategorik kodlama ``kubit ≥ sozluk``
    #: ŞARTINA bağlandı: 16 belirteci 4 boyutta eşit uzaklıkta dizmek
    #: imkânsızdır ve o imkânsızlığı ikili kodlamayla örtmek tam da
    #: yasaklanan şeydi. 16'da bütün ikili mesafeler eşittir (5,657;
    #: değişke 0,0000) -- yâni fiilen bir qudit tabanı.
    #:
    #: **BEDELİ SAKLANMIYOR:** yazmaç genişler ve eski MPS motoru
    #: yavaşlar. O motor zaten fermanla iptaldir; bedel onun tasfiyesini
    #: geciktirmenin bedelidir, bu şartın değil.
    satir_kubiti: int = 16
    yerel_kubit: int = 1
    bag: int = 16                    # χ
    mera_kademe: int = 3
    # --- veri
    ornek_sayisi: int = 4
    pencere: int = 8
    sozluk: int = 16
    degerlendirme_gorevi: int = 4
    dogrulama_sayisi: int = 100
    kademe_gorevi: int = 2
    azami_uret: int = 32
    yaricap: float = 2.5
    # --- arama (FCT kapalı formu + blok koordinat inişi)
    #
    # **ÖLÜ AYARLAR KALDIRILDI (ferman).** ``bit``, ``nqs_gizli``,
    # ``nqs_derece``, ``zincir``, ``oran``, ``kademe``, ``lam``,
    # ``azami_kubit``, ``sanal_kubit_sayisi`` bu dosyada bir tek yerde
    # bile okunmuyordu: ne ``OptimizeAyari``ye geçiyor, ne ``qayar``a,
    # ne rapora. Bir ayarın var olup okunmaması, onun ayarlanabildiği
    # yalanını söyler.
    ornek: int = 24
    talim_tur: int = 3
    altuzay_ornek: int = 24
    #: Blok koordinat inişi: 0 = kapalı (bütün yönler her turda).
    blok: int = 0
    # **ŞEMANIN QSVT/FCT AYARLARI KESİLDİ (ferman 2-B).** ``cevrim``,
    # ``gorev``, ``qsvt_derecesi``, ``beta_maksimum``, ``gcl_nokta_sayisi``,
    # ``lambda_mizan``, ``ogrenme_orani`` yalnız ``KulliDalgaTalimMotoru``
    # tarafından okunuyordu. O motor -- kuantum melekelerini "meclise"
    # sokan mekanizma -- fermanla imha edildi; ayarları da aynı turda
    # kökünden kesildi. Ayarın var olup okunmaması, ayarlanabildiği
    # yalanını söyler.
    # --- MÎZÂN-I KÜLLÎ (nefs/kulli_mizan.py) -- dört kefenin ağırlıkları
    #: ``ℒ_Küllî = ℒ_Rezonans + λ₁ℒ_Çevrim + λ₂ℒ_Monogami + λ₃ℒ_Hodge``
    #:
    #: **KÖR NLL BURADA YOKTUR VE OLMAYACAKTIR.** Padişahın hükmü:
    #: *"loss = CrossEntropyLoss() satırı modelin katilidir."* Veriye
    #: bağlanma tek yerdedir ve o da kör değildir: Uhlmann kuantum
    #: sadakati (``ℒ_Rezonans``). Veri bir kural değil, dışarıdan gelen
    #: **zayıf bir uyarımdır**; modelden verinin faz gürültüsünü taklit
    #: etmesi değil, ana frekansıyla rezonansa girmesi istenir.
    # ══════════════════════════════════════════════════════════════
    #  ZABITIN NİHAÎ AYAR CETVELİ (Qudit Kapasitesi ve Hız Tahkiki)
    # ══════════════════════════════════════════════════════════════
    #  A grubu (HIZ) değişti, B ve C grubu (HÜKÜM) **DOKUNULMADI**:
    #
    #    ornek_sayisi (B)   128 → 512     GPU/CPU doygunluğu
    #    Ayna.tur           400 → 16      analitik kararlı durum
    #    QuditAyari.qsvt     64 → 16      Chebyshev kalıntısı 1e−7 altı
    #    cevrim_sayisi        8 → 8       fakat DÖNGÜ KALKTI (vektörize)
    #
    #  **ÖLÇÜMÜN ZABITTAN AYRILDIĞI YER, AÇIKÇA.** Zabıt 1,06 sn'lik
    #  adımın payını "Ayna %50-60, QSVT %20-25, çevrim %15" diye
    #  kestiriyor. Bu ortamda ölçtüm ve öyle çıkmadı: ``ayna`` tâlim
    #  hattında hiç çağrılmıyor (yalnız ``nefs/soyle.py``nin arama
    #  kipinde), ``qsvt`` de kayıp yolunda görünmüyor. Profilin tamamı
    #  ``idrak_et``te: 41 meleke ve onların vurduğu kapılar.
    #  Zabıtın **hükmü** yine de icra edildi (değerler indirildi ve
    #  döngüler kaldırıldı); yalnız kazancın nereden geleceği hakkında
    #  ölçüm başka söylüyor ve o da yazılıdır. Hüküm uygulanır, ölçü
    #  gizlenmez.
    lam_cevrim: float = 1.0        # λ₁ Wilson holonomisi (tenakuz)
    lam_monogami: float = 0.5      # λ₂ CKW dolanıklık monogamisi
    lam_hodge: float = 0.75        # λ₃ Hodge tenakuzsuzluğu
    #: λ₄ **KUANTUM ENGELLENMESİ** (Geometric Quantum Frustration).
    #: Zabıt (*Küllî Kuantum Mizânı*, III. fasıl, 1. hadise): üçgen
    #: kafesli antiferromıknatısta ``s₁`` ile ``s₂`` zıt olmak ister,
    #: ``s₂`` ile ``s₃`` zıt olmak ister, fakat o zaman ``s₃`` ile
    #: ``s₁`` aynı olmak zorunda kalır ve sistem taban durumuna
    #: **oturamaz**. Metin safsataysa mikroskobik bir gerilim dalgası
    #: yayılır; bu kefe onu ölçer.
    #:
    #: Gerilimi ölçen uzuv ``nefs/ayna.py:halka``dır -- Coherent Ising
    #: Machine. **Aynanın ana akıştaki fiilî işi budur**; evvelce
    #: yalnız adı geçiyordu ve hiçbir yerde çağrılmıyordu.
    lam_engel: float = 0.6
    #: Muhakeme çevrimi kaç adımlıdır (``X → Y → Z → X``).
    cevrim_boyu: int = 3
    #: Taranacak azamî kapalı çevrim sayısı. **Zabıt: 8 KALIR, fakat
    #: Python döngüsü kalkar** -- sekiz holonomi tek tensör bloğunda
    #: toplu hesaplanır (``nefs/kulli_mizan.py:_cevrimleri_tara``).
    cevrim_sayisi: int = 8
    # ══════════════════════════════════════════════════════════════
    #  MANTIĞA SADAKAT -- 7/24 (nefs/sadakat.py)
    # ══════════════════════════════════════════════════════════════
    #
    # Zabıt (*Mantık ile Mantık Yürütme Arasındaki Ontolojik Ayrım*):
    # *"Mantığa sadakat bir meleke değildir; sistemin varlık şartıdır.
    # Bütün melekelerin 7/24, her adımda ve her uzayda uymak zorunda
    # olduğu sarsılmaz kanundur."*
    #
    # O hâlde bu bir **kayıp terimi değildir**: kaybın gradyanı ihlâli
    # *pahalı* yapar, *imkânsız* yapmaz. Sadakat, ihlâli imkânsız yapan
    # bir alt-uzay şartıdır ve her ileri geçişte icra edilir:
    #
    #     Tenakuz_Alarmı = popcount(X ∧ Z ∧ PARİTE_MASKESİ) > 0
    #     alarm varsa    : X ← X ⊕ (X ∧ Z ∧ PARİTE_MASKESİ)   (Zeno)
    #
    # Sürekli ``e^{iπ} = −1`` yıkıcı girişimi yerine ayrık taşıyıcıda
    # tam karşılığı budur (ferman 7-D): faz döndürmek yok, biti düşürmek
    # var. Gradyan yoktur, dolayısıyla tâlim bunu "öğrenmek" zorunda
    # değildir -- zaten koşamaz.
    #: ``0`` = sadakat kapısı KAPALI. Kapatılınca tenakuz alarmı söner
    #: mi diye ölçülür (ferman 5: kapatılamayan tedbir ölçülemez).
    sadakat_acik: int = 1
    #: Parite maskesinin oturduğu lif. ``lif_yapisi`` üç karodur
    #: ``(16,16,16)``; hükmün taşındığı karo budur.
    parite_lifi: int = 2
    # ══════════════════════════════════════════════════════════════
    #  L_TENAKUZ -- LOG BARİYER × EŞ-ZAMANLI DIŞLAMA (nefs/tenakuz.py)
    # ══════════════════════════════════════════════════════════════
    #
    # Ham ``−ln(Tr(I + Re U_C))`` biçimi, holonomi tam taklaya
    # (``U_C → −I``) yaklaşınca **ıraksar** ve tek bir çevrim bütün
    # mizanı yutar. Kat'î hüküm (*Sayısal Olarak Kararlı Log-Bariyer*)::
    #
    #     L_Tenakuz = −ln((Tr(I + Re U_C) + ε) / (2d + ε)) · S_dışlama(A,B)
    #     S_dışlama(A,B) = exp(−(Birlikte_Görülme(A,B) + 10⁻⁴) / τ_pencere)
    #
    # Payda ``2d + ε`` normalize eder (argüman ``(0, 1]``de kalır, log
    # daima ``≥ 0``); ``ε`` ıraksamayı **sonlu** bir tavana bağlar.
    # ``S_dışlama`` ise cezayı manalandırır: hiç beraber görülmemiş iki
    # kavramın çelişmesi ağır, sık beraber görülenlerin gerilimi hafiftir.
    lam_tenakuz: float = 0.4
    #: ``ε`` -- ıraksama freni. Tavan ``ln((2d+ε)/ε)``dır ve sonludur.
    tenakuz_eps: float = 1e-5
    #: ``τ_pencere`` -- dışlamanın sönüm boyu. Büyüdükçe dışlama düzleşir
    #: (her çift eşit); ``0`` YASAKTIR.
    dislama_tau: float = 8.0
    # ══════════════════════════════════════════════════════════════
    #  TABAKALI MİZAN (nefs/tabakali_mizan.py)
    # ══════════════════════════════════════════════════════════════
    #
    # Zabıt (*Quditte Negatif Olabilirlik Yanılgısı*)::
    #
    #     L_toplam = L_nokta + α·L_uzay + β·L_kategori + γ·L_tip
    #
    # **TERKİP, TABELA DEĞİL (ferman 3).** Dört mertebenin ikisi mizanda
    # **zaten vardır** ve yenisi yazılmadı, aynı oldukları ispat edildi:
    #
    #     L_uzay = 1 − |⟨Φ_hedef|Ψ⟩|²   ≡  ℒ_Rezonans (Uhlmann sadakati)
    #     L_tip  = ⟨Ψ|Δ_Hodge|Ψ⟩        ≡  ℒ_Hodge
    #
    # O hâlde ``α`` yeni bir katsayı değildir: ``ℒ_Rezonans``ın kendi
    # ağırlığıdır ve o **1**dir (mizanın çıpası). ``γ`` de ``lam_hodge``.
    # Hakikaten yeni olan iki kefe aşağıdadır.
    #: ``β`` -- **KATEGORİ MİZANI**: ``‖M_{g∘f} − M_g·M_f‖²_F``. Dışarıdan
    #: etiket istemez; sistemin kendi morfizmlerinin kendini denetlemesidir
    #: (self-supervised categorical coherence). ``0`` = kapalı.
    lam_kategori: float = 0.5
    #: **NOKTA MİZANI**: ``−ln Tr(P_hedef ρ)`` -- kısmî Born hizalaması.
    #: Bu **kör NLL DEĞİLDİR** ve olmasına da izin verilmez: üç geometrik
    #: zırh (uzay, kategori, tip) kilitlendikten sonra, yalnız son basamak
    #: olarak ve **küçük** bir ağırlıkla girer. Ağırlık büyütülürse mizan
    #: bir softmax taklidine iner; onun için sayısı burada, görünürde.
    lam_nokta: float = 0.25
    # ══════════════════════════════════════════════════════════════
    #  MANTIK YÜRÜTME SEFERİ (nefs/usul.py) -- 7/24 KOŞMAZ
    # ══════════════════════════════════════════════════════════════
    #
    # Zabıt: *"Zihin sürekli Aristo kıyası kurmaz... Ne zaman ki zihinde
    # bir karanlık nokta, örtülü bir gaye veya şüpheli bir dâvâ belirir;
    # işte o an Zihnin Kalbi Tertip melekesine emir verir ve Mantık
    # Yürütme Seferi başlatılır."*
    #
    # Gedik ölçülür, tahmin edilmez: bir muhakeme çevriminin holonomisi
    # ``ω < usul_haddi`` ise o çevrim karanlıktadır. Sefer yalnız o
    # çevrimler için açılır; hepsi için açılırsa mimari yine "her an boş
    # yere mantık kapısı çalıştıran kör bir hesap makinesi" olur.
    #: ``0`` = sefer hiç açılmaz. Kapatılınca istihrac sayısı sıfırlanır.
    usul_acik: int = 1
    #: Gediğin eşiği. ``ω`` bunun altındaysa çevrim şüphelidir.
    usul_haddi: float = 0.0
    #: Bir kayıp çağrısında açılacak azamî sefer. Sefer pahalıdır
    #: (manifold + uncompute + Lan_K); bütçesi burada ilan edilir.
    usul_seferi: int = 4
    # ══════════════════════════════════════════════════════════════
    #  ŞÜPHE MANİFOLDU (nefs/suphe.py)
    # ══════════════════════════════════════════════════════════════
    #
    # Teâruz (``P`` ile ``¬P`` denk kuvvette): ``μ ← μ·(1 − |⟨ψ_P|ψ_¬P⟩|)``.
    # İki kol birbirini tam örtüyorsa yakîn sıfırlanır; hüküm verilmez,
    # **tevakkuf** edilir. Merak kancası şüpheyi seferin gayesine çevirir;
    # Liouville sönümü delilsiz kuru zannı zamanla buharlaştırır.
    #: ``0`` = şüphe manifoldu kapalı: model her hâlde hüküm verir.
    suphe_acik: int = 1
    #: Liouville sönümü ``γ_şüphe``: delilsiz zannın buharlaşma hızı.
    suphe_sonumu: float = 0.05
    # ══════════════════════════════════════════════════════════════
    #  RÜŞT KİLİDİ -- ÇİZELGE **VE** MUAYENE (nefs/rust.py)
    # ══════════════════════════════════════════════════════════════
    #
    # **ESKİ USUL İMHA EDİLDİ (ferman 1-E: yarım iş yasak).** Evvelce
    # rüşt yalnız bir takvimdi: ``α(t) = σ((t − t₀)/τ)``. O takvim,
    # topolojisi yırtık -- yâni ``H¹ ≠ 0``, mantıkta kapanmamış deliği
    # olan -- bir dimağı da vakti gelince rüşte erdiriyordu. Vakit bir
    # olgunluk delili değildir.
    #
    # Kat'î hüküm (**Asenkron Eşik-Korumalı Hibrit Rüşt Fonksiyonu**)::
    #
    #     α_rüşt(t) = σ((t − t₀)/τ) · exp(−(‖dF(t)‖²_DEC + ‖H¹(U;F)‖²)
    #                                      / σ²_kapanış)
    #
    # Birinci çarpan **takvimdir** (aşağıdaki ``rust_t0``/``rust_tau``),
    # ikincisi **muayenedir**: ayrık dış türevin artığı ile birinci
    # kohomolojinin boyu. İkisi de sıfıra inmedikçe üs sıfıra inmez ve
    # ``α`` kilitli kalır. Yâni vakit gelse de yırtık kapanmadıkça
    # fıtrat serbest bırakılmaz.
    rust_t0: float = 0.5           # geçişin ortası (tur nispetiyle)
    rust_tau: float = 0.15         # geçişin genişliği
    #: ``σ_kapanış`` -- muayene kapısının genişliği. Küçüldükçe kapı
    #: sertleşir: en ufak yırtıkta ``α`` sıfırlanır. ``0`` YASAKTIR
    #: (sıfıra bölme); kapıyı **kapatmak** için ``rust_muayene=0`` denir
    #: ve o zaman eski kör takvim geri gelir -- ölçü kırmızı yanar.
    rust_kapanis: float = 0.5
    #: Muayene kapısı açık mı? ``0`` = yalnız takvim (eski kör hâl).
    #: Ferman 5: kapatılabilen bir tedbirin faydası ölçülebilir.
    rust_muayene: int = 1
    # --- KUANTUM ASOSİYATİF HAFIZA (nefs/hafiza.py)
    #: **AĞIRLIK HAFIZA DEĞİLDİR.** Ağırlık fıtrattır, gramerdir,
    #: reflekstir. Tecrübe edilen safsatalar ve meşru teemmüller ayrı
    #: bir yoğunluk operatöründe (``ρ_Hafıza``) saklanır.
    hafiza_kapasitesi: int = 256
    #: Kraus yazma oranı ``ε``: ``ρ ← (1−ε)ρ + ε|Φ⟩⟨Φ|``.
    hafiza_yazma: float = 0.05
    #: Liouville sönümü ``γ``: delilsiz kuru zan zamanla buharlaşır.
    hafiza_sonumu: float = 0.02
    #: Zeno budaması eşiği: hafızada cerhedilmiş bir yolla örtüşme bunu
    #: aşarsa döngü **tamamlanmadan** kesilir.
    #: **ZABIT: KORUNACAK** -- "safsata budama hassasiyetidir;
    #: gevşetilirse zekâ düşer."
    zeno_esigi: float = 0.35
    #: Hafızadaki cerh kaydının hangi belirteçleri kestiği: kaydın kendi
    #: tepe genliğinin bu nispetini aşanlar. **ZABIT: KORUNACAK (0,9).**
    #: Evvelce ``nefs/hafiza.py``de gömülüydü; ferman gereği ayara
    #: bağlandı, **değeri değişmedi**.
    zeno_tepe: float = 0.9
    #: Aynı hatıranın tekrar sayılmaması için örtüşme eşiği (gömülüydü).
    hafiza_ayniyet: float = 0.98
    #: Hafızadan buharlaşma eşiği ``μ`` (gömülüydü).
    hafiza_buhar: float = 1e-4
    # --- AYNA (nefs/ayna.py) -- zabıtın A grubu
    #: **ZABIT: 400 → 16; ÖLÇÜM 24 dedi** (bkz. nefs/ayna.py:tur).
    #: kararlı durum döngü kurmadan da bulunur (analitik/Padé).
    ayna_tur: int = 24
    #: Işın bölücü açısı -- kör sıcaklığın yerini alan ölçü.
    ayna_teta: float = 0.2617993877991494        # π/12
    #: Sıkıştırma.
    ayna_r: float = 0.35
    # --- QUDİT ÇEKİRDEĞİ (nefs/qudit.py) -- zabıtın A grubu
    #: **ZABIT: 64 → 16.** "16. dereceden sonra Chebyshev kalıntı hatası
    #: zaten 1e−7 altına iner; 64 fuzulidir."
    #:
    #: Bu üçü evvelce ayara konmuş fakat **hiçbir yere geçmiyordu** --
    #: ``nefs/qudit.py``nin kendi varsayılanları koşuyordu. Artık
    #: ``mizan_ayari`` ile ``ℒ_Hodge``un QSVT süzgecine gider
    #: (``nefs/qudit.py:suz``): harmonik bileşen Chebyshev polinomuyla
    #: ayrılır ve tenakuz enerjisi **süzülmüş** durumda ölçülür.
    qudit_qsvt: int = 16
    #: KAN-Chebyshev derecesi.
    qudit_derece: int = 8
    #: Cartan yön sayısı (``θ`` boyutu).
    qudit_yon: int = 8
    #: **Genlik tipi.** Zabıt 2 (Saf CPU Mimarisi, 4. usul): durum
    #: L2/L3 önbelleğinden akan bir veri nehri gibi geçmeli.
    #: ``complex64`` bellek trafiğini yarıya indirir.
    genlik_tipi: str = "complex64"
    # ══════════════════════════════════════════════════════════════
    #  ZABIT: 1 GB/S -- AYRIK KUANTUM MEKANİĞİ
    # ══════════════════════════════════════════════════════════════
    #
    # **HÜKÜM 1 (zabıt, birinci fasıl):** *"Sürekli Hilbert uzayında
    # (ℂ^d), kayan nokta sayılarıyla, matris çarpımlarıyla ve
    # trigonometrik fazlarla kalarak 1 GB/s hızına ulaşmak fizikî bir
    # imkânsızlıktır."*  Belirteç başına bütçe **16 saat çevrimidir**;
    # tek bir ``cos(θ)`` 15-30 çevrim yer.
    #
    # O hâlde durum artık sürekli genlik vektörü DEĞİLDİR.
    # ══════════════════════════════════════════════════════════════
    #  41 MELEKENİN KOŞTUĞU HAT
    # ══════════════════════════════════════════════════════════════
    #
    # **ZABIT (Derece-12 ve 1 GB/s, 1. ameliyat):** *"1 GB/s hız
    # hedefinde Python `for` döngüsü KULLANILAMAZ. Ana akış motoru saf
    # C ile yazılır ve tek parça derlenir; Python sadece başlatma
    # anında devreye girer, akış başladığında kontrolü tamamen C
    # çekirdeğine bırakır."*
    #
    # Melekelerin **kodu değişmez**: yine ``q.tek(i, G)`` derler.
    # Değişen, o çağrının nereye gittiğidir: kapı artık duruma
    # vurulmaz, bir **banda** yazılır; bant dolunca yahut durum
    # okununca tamamı tek C çağrısında icra edilir.
    #:   ``c``     -- kaynaşık C çekirdeği (nefs/qcekirdek.py)
    #:   ``numpy`` -- eski yol. **Kıyas içindir**; seçilirse rapor
    #:                onu söyler ve hız ölçüsü kırmızı yanar.
    hat: str = "c"
    #: Kapı bandının azamî boyu. ``0`` = donanımdan tayin (L2'ye sığsın).
    #: Bant dolunca kendiliğinden boşalır; netice sıraya bağlıdır ve
    #: bant boyu neticeyi **değiştirmez** (sıra korunur).
    hat_bandi: int = 0
    #: Motorun cinsi:
    #:   ``galois``    -- GF(2⁸) + Stabilizer Tableau (XOR/AND bitmask)
    #:   ``kronecker`` -- matrix-free [16,16,16] lifli SIMD akışı
    #: İkisi de sürekli ``ℂ^4096`` yoğun diziyi **iptal eder**.
    motor: str = "galois"
    #: Kronecker lif yapısı. **Zabıt (TDD Darboğazı, Yol 3): kesin
    #: çözüm ``[16,16,16]``dır** -- 3 adet 16×16 karo, 16 KB, tamamen
    #: L1 önbellekte. ``4096×4096`` GEMM değil.
    lif_yapisi: Tuple[int, ...] = (16, 16, 16)
    #: Galois cisminin mertebesi: ``GF(2^galois_us)``. 8 seçildi çünkü
    #: GFNI donanım komutları ``GF(2⁸)`` üstünde çalışır.
    galois_us: int = 8
    #: Stabilizer tableau'nun kübit sayısı (``2N`` bit satırı).
    tableau_n: int = 64
    # ══════════════════════════════════════════════════════════════
    #  ZABIT: NON-CLIFFORD ÇIKMAZININ ÜÇ ÇARESİ
    # ══════════════════════════════════════════════════════════════
    #
    # **İTİRAZ HAKLIDIR (zabıt, birinci fasıl).** Gottesman-Knill'in
    # haddi kat'îdir ve Bravyi-Gosset (2016) onu sayıya döker: ``t``
    # adet non-Clifford kapıdan sonra ``χ_stab ~ 2^{0,468 t}``. Yâni
    # yalnız "tableau kurdum" demek 16 çevrimlik bütçeyi beşinci adımda
    # çökertir. Zabıt bunu inkâr etmez, üç ayrı kapıdan dolaşır.
    #
    #: **1. ÇARE -- MATCHGATE / FLO.** Majorana modu sayısı ``N``;
    #: kovaryans ``2N × 2N`` antisimetrik reel dizeydir. Sürekli açılı
    #: kapı burada **dallanmaz**, yalnız dört satır/sütunda döner.
    #: ``0`` = kapalı; kapatılırsa χ ölçüsü kırmızı yanar (ferman 5).
    flo_modu: int = 24
    #: FLO evriminde kaç sürekli açılı matchgate vurulacak. Zabıtın
    #: iddiası: ``t`` ne olursa olsun ``χ_stab = 1`` kalır. İddia bu
    #: sayıyla sınanır -- büyütülünce de 1 kalmalıdır.
    flo_kapisi: int = 64
    #: **2. ÇARE -- GALOIS S-BOX.** Gayri-lineerlik ``x ↦ M·x²⁵⁴ + b``
    #: (Rijndael). ``0`` = kapalı: bükme kimlik olur ve gayri-lineerlik
    #: ölçüsü (diferansiyel tekdüzelik) kırmızı yanar.
    sbox_acik: int = 1
    #: **3. ÇARE -- CNOT-DIHEDRAL FAZ POLİNOMU.** Faz grubu ``Z_m``.
    #: Amy-Maslov-Mosca teoremi ``m = 8`` (T kapısı mertebesi) için
    #: yazılıdır; ``m`` ikinin kuvveti olduğu sürece hüküm değişmez,
    #: yalnız faz incelir.
    #:
    #: **BU SAYI İKİ YERE BİRDEN GİDER VE GİTMELİDİR**: yazmaç fazı
    #: bu grupta biriktirir (``QuditYazmac.faz``), polinom da bu grupta
    #: oturur (``faz_oturt``). Evvelce ayrışmışlardı -- yazmaç ``Z_16``,
    #: polinom ``Z_8`` -- ve o hâlde polinom, biriken üssü ikiye bölüp
    #: **başka bir fazı** tarif ediyordu. 16 seçildi: faz hatası
    #: ``π/16 = 0,196`` radyan, ``π/8 = 0,393`` değil.
    faz_mertebesi: int = 16
    #: Faz polinomunun azamî derecesi. Teorem ``≤ 3`` der (Reed-Muller
    #: mertebesi); daha yüksek dereceli bir faz CNOT-Dihedral sınıfının
    #: dışına düşer ve bu **ölçülüp raporlanır**, örtülmez.
    faz_derecesi: int = 3
    # ══════════════════════════════════════════════════════════════
    #  ZABIT: 1 TB/S GPU AKIŞI
    # ══════════════════════════════════════════════════════════════
    #
    # **FERMAN 5-B: BURADA DONANIM SAYISI YOKTUR.** Evvelce burada
    # ``gpu_karti=4``, ``gpu_vram_bandi=300``, ``gpu_pcie_bandi=31.5``,
    # ``gpu_tops=485`` yazıyordu. Dördü de **elle yazılmıştı** ve
    # zabıttan kopyalanmıştı; bu makinede hiçbiri ölçülmemişti. Padişahın
    # hükmü kat'îdir: *"Gpu için ayarları kendin tayin edip simülasyonda
    # gözümü boyamayacaksın, tüm ayarları otomatik ölçen fonksiyonlarla
    # belirleyeceksin."* Dördü de kesildi.
    #
    # Kart adedi, VRAM bandı, PCIe bandı, önbellek, SIMD genişliği,
    # tamsayı bandı -- hepsi ``nefs/donanim.py``de **yoklanarak** bulunur.
    # Ölçülemeyen ``None``dur ve ona dayanan iddia kurulmaz.
    #
    # Aşağıda kalan iki sayı donanım ölçüsü DEĞİLDİR:
    #: **HEDEF** -- zabıtın koyduğu had, GB/s. Bu bir iddiadır ve öyle
    #: raporlanır; ölçülen akış onun yanında ayrı sütunda durur.
    gpu_akis_haddi: float = 1000.0
    # ══════════════════════════════════════════════════════════════
    #  ZABIT: DERECE-12 FAZ -- SİKLOTOMİK KOSET İNDİRGEMESİ
    # ══════════════════════════════════════════════════════════════
    #
    # **CNOT-DİHEDRAL İDDİASI İPTAL** (CLAUDE.md 7-B). Ölçüldü: ana
    # akışta biriken fazın Reed-Muller derecesi 12; Amy-Maslov-Mosca
    # ``≤ 3`` ister. İddia düştü ve yerine siklotomik koset geldi.
    #
    #: İndirgemenin yürüdüğü cisim ``GF(2^us)``. Frobenius
    #: (``x ↦ x²``) burada **lineerdir**; bütün mesele odur.
    siklotomik_us: int = 8
    #: Taban üs. Zabıt ``x³`` der: ``12 = 3·4`` ve ``4 = 2²``, o hâlde
    #: ``x¹² = ((x³)²)²``. Kaç kare alınacağı ``derece``den çıkar.
    siklotomik_taban: int = 3
    #: Hangi dereceye kadar indirgeme aranacak. ``faz_derecesi``
    #: (CNOT-Dihedral haddi) DEĞİLDİR: o iptal edildi. Bu, ölçülen
    #: derecedir ve ölçüm 12 dedi.
    siklotomik_derece: int = 12
    #: **USUL SEÇİMİ** -- bitstream genleşme katsayısı (3. motor).
    #: Zabıt 8 der (125 GB/s × 8 = 1000 GB/s). Bu bir donanım ölçüsü
    #: değil, sıkıştırma tasarımıdır; **fiilen elde edilen** kat
    #: ölçülür ve tutmuyorsa öyle yazılır.
    gpu_genlesmesi: int = 8
    # --- ZABIT 2: SAF CPU 2026 USULLERİ
    #: **1. USUL -- LimTDD: HESAP MOTORU OLMAKTAN ÇIKARILDI.**
    #:
    #: Zabıt (TDD Darboğazının Riyazî İspatı) kat'îdir: rastgele
    #: tensörde iki alt bloğun kolinye olma olasılığı **sıfırdır**
    #: (Lebesgue ölçüsü), o hâlde hiçbir düğüm birleşmez ve graf tam
    #: ağaç olarak açılır. Ölçtüğümüz **35 163× yavaşlama**, işaretçi
    #: kovalamanın SIMD'e nispetidir ve bir kodlama kusuru değildir.
    #:
    #: Zabıtın hükmü: *"İleri ve geri yayılımda TDD'nin işaretçi/hash
    #: hamallığını derhal iptal ediyoruz. TDD'yi bir hesaplama motoru
    #: olarak değil; sadece mantık kilitlendiğinde kanonik adres
    #: eşitliğini (O(1)) kontrol eden haricî bir denetçi olarak
    #: tutuyoruz."*
    #:
    #: Bu alan artık denetçinin çekirdek boyudur: çevrim kapanışında
    #: durumun yalnız bu kadar elemanı hashlenir.
    tdd_cekirdek: int = 16
    #: Özdeşlik toleransı: iki alt blok bu farkla aynı sayılır.
    tdd_tolerans: float = 1e-7
    #: **2. USUL -- QUDİT STABILIZER RANK.** Durumun Clifford çerçevesine
    #: ne kadar yakın olduğu (``χ_stab``) ölçülür; küçükse durum bit
    #: seviyesinde tableau ile taşınabilir. ``0`` = kapalı.
    stab_mertebe: int = 8
    #: **3. USUL -- KLASİK GÖLGELER.** ``K`` gölge örneği ile ``M``
    #: gözlenebilirin beklentisi ``O(log M)``de kestirilir. ``0`` =
    #: kapalı (bütün ölçümler tam yapılır).
    golge_ornegi: int = 0
    #: Gölge kestiriminin kabul edilen azamî hatası; aşılırsa tam ölçüme
    #: dönülür ve bu **sessiz değildir**, dökümde yazılır.
    golge_haddi: float = 0.05
    #: Yazmacın yığın dilimi. ``0`` = donanımdan tayin et
    #: (``nefs/onbellek.py``). Elle bir sayı verilirse o kullanılır ve
    #: sebebi çağıranın sorumluluğundadır.
    yigin_dilimi: int = 0
    # --- donanım
    surec: int = 0                   # 0 = donanımdan tayin et
    tohum: int = 0
    #: **TÂLİM SAAT HADDİ (kütük H212).** ``ogrenme/hoca.py``nin bütçe
    #: freni bu haddi okur: ``tur × d × düğüm`` çağrısının kestirilen
    #: süresi bunu aşarsa koşu **başlamaz**, ``RuntimeError`` verir.
    #:
    #: Sessiz bir sabit değil, profilde **ilan edilen** bir ölçüdür ve
    #: sebebi ölçümdür: aynı fren ``AZAMI_KAGGLE``ı 1 saatlik varsayılan
    #: hadde reddediyordu (d=264, tur=3, düğüm=4097 → 3,24 milyon çağrı
    #: ≈ 18 saat). O profil zaten kasten uzun koşudur; haddi profilin
    #: kendisi söylemelidir, fren değil.
    azami_talim_saati: float = 1.0

    def qayar(self):
        from nefs.zihin_durumu import QAyar
        # **YIĞIN YAZMACA GEÇER.** Evvelce geçmiyordu ve yazmaç daima
        # ``B=1`` kuruluyordu: 41 melekenin 300 000 kapısı her örnek
        # için baştan vuruluyordu. Hız teftişi bunu ölçtü.
        import numpy as _np
        tip = {"complex64": _np.complex64,
               "complex128": _np.complex128}[str(self.genlik_tipi)]
        return QAyar(satir_kubiti=self.satir_kubiti,
                     yerel_kubit=self.yerel_kubit, bag=self.bag,
                     mera_kademe=self.mera_kademe, tohum=self.tohum,
                     yigin=self.yigin(), tip=tip,
                     motor=str(self.motor),
                     lif_yapisi=tuple(self.lif_yapisi),
                     # Faz grubu **tek kaynaktan**: yazmaç ile faz
                     # polinomu aynı ``Z_m``de olmalı, yoksa polinom
                     # başka bir fazı tarif eder.
                     faz_mertebesi=int(self.faz_mertebesi),
                     # 41 melekenin kapıları bu hatta koşar.
                     hat=str(self.hat), hat_bandi=int(self.hat_bandi))

    def yigin(self) -> int:
        """Yazmacın YIĞIN DİLİMİ -- elle değil, **donanımdan**.

        **``ornek_sayisi`` ile yığın dilimi ayrı şeylerdir** ve evvelce
        karıştırılıyordu: birincisi kaç örnek işleneceğidir (veri),
        ikincisi tek geçişte kaçının yazmaca sığacağıdır (donanım).
        Aynı sayı tutulunca ``ornek_sayisi``yi büyütmek yazmacı
        önbellekten taşırıyordu -- ölçüldü: B=512'de hız 61 312'den
        41 980'e **düşüyor**.

        ``yigin_dilimi > 0`` ise o kullanılır (elle ezme hakkı saklı);
        değilse ``nefs/onbellek.py`` donanımdan hesaplar.
        """
        if int(self.yigin_dilimi) > 0:
            return int(self.yigin_dilimi)
        import numpy as _np
        from nefs.onbellek import yigin_sec
        from nefs.zihin_durumu import QAyar as _QA
        d = int(self.satir_kubiti) * int(_QA.hukum_lifi)
        tip = {"complex64": _np.complex64,
               "complex128": _np.complex128}[str(self.genlik_tipi)]
        B = int(yigin_sec(d, tip)["B"])
        return max(1, min(B, int(self.ornek_sayisi)))


#: **CPU'da koşan kısa hâl.** ``B = ornek_sayisi`` bu ortam için
#: ölçülerek seçildi (kütük H151)::
#:
#:      B    kayıp sn   parametre yayılımı   veri gürültüsü
#:      2      1,73          0,0191               —
#:      4      2,96          0,0066            0,0013
#:      8      5,51          0,0045            0,0019
#:     16     10,55          0,0058            0,0007
#:     32     20,35          0,0051            0,0018
#:
#: B büyüdükçe parametre yayılımı **düşüyor** (σ/√B). B=4'ten sonra
#: ölçülebilir kazanç yok, maliyet doğrusal artıyor. Delil budur: B=4.
#: **ÖLÇÜLEREK DEĞİŞTİ (hız teftişi).** ``ornek_sayisi`` artık yazmacın
#: **yığın boyudur** ve 4 değil 64'tür; ``pencere`` 8 değil 512'dir.
#: Sebebi ölçümdür -- aynı kayıp, aynı netice, farklı hız::
#:
#:      B    L      belirteç/sn
#:      4    8            215
#:     64  512         43 859
#:    128  512         61 660      ← seçilen (tavan)
#:    256  512         58 248
#:    512  512         32 646      (bellek doyumu)
#:
#: Kayıp değişti çünkü veri değişti (daha uzun bağlam, daha çok örnek),
#: hesabın kendisi değil: B=4/L=8'de iki hat **birebir** aynı sayıyı
#: veriyor (2,888511).
KISA_CPU = EgitimAyari(ad="kısa-CPU", ornek_sayisi=512, pencere=512,
                       ornek=3, talim_tur=1,
                       altuzay_ornek=6, degerlendirme_gorevi=8,
                       dogrulama_sayisi=20, bag=8)

#: Orta hâl -- tek makinede saatler.
#: **KIRIK PROFİL DÜZELTİLDİ.** ``satir_kubiti=6`` yazıyordu; halbuki
#: ikili kodlama imha edilince ``satir_kubiti`` **seviye sayısı** oldu
#: ve ``sozluk=16`` belirteci 6 seviyeye sığmaz. Yâni bu profil
#: çağrılsaydı düşerdi -- koşmayan bir profil, olmayan bir profildir.
ORTA = EgitimAyari(ad="orta", satir_kubiti=16, bag=32,
                   ornek_sayisi=256, pencere=512,
                   degerlendirme_gorevi=40,
                   azami_uret=120, dogrulama_sayisi=100,
                   ornek=128, azami_talim_saati=6.0)

#: **Kaggle azamî hâli.** 4 cihaz, ~84 GB VRAM. Ceridenin taksimatı::
#:
#:     Veri yazmacı : B = 2048 dizi × L_bağlam = 4096 belirteç
#:                  = 8.388.608 belirteç / adım
#:
#: **HUDUT -- açıkça:** bu ayar bu ortamda KOŞMAMIŞTIR ve koştuğu iddia
#: edilmiyor. Burada GPU yoktur (``torch`` kurulu değil); 8,4 milyon
#: belirteçlik yığın bu makinenin belleğine sığmaz.
#: **``satir_kubiti=12`` de kırıktı**, aynı sebeple 16'ya çekildi.
AZAMI_KAGGLE = EgitimAyari(
    ad="azamî-Kaggle", satir_kubiti=16, yerel_kubit=1, bag=256,
    mera_kademe=5, ornek_sayisi=2048, pencere=4096,
    sozluk=16, degerlendirme_gorevi=120, dogrulama_sayisi=100,
    azami_uret=0, yaricap=3.0, ornek=4096,
    azami_talim_saati=24.0)

#: Ayar adından profile -- komut satırı için.
PROFILLER: Dict[str, EgitimAyari] = {
    "kısa": KISA_CPU, "kisa": KISA_CPU, "orta": ORTA,
    "azamî": AZAMI_KAGGLE, "azami": AZAMI_KAGGLE}


# =====================================================================
#  TÂLİM GEÇİDİ -- koşmadan EVVEL dimağın akdi ve illeti denetlenir
# =====================================================================
def gecit(sert: bool = True, hiz_ayari=None) -> Dict[str, object]:
    """TÂLİME GİRMEDEN EVVEL İKİ ŞART -- akit ve illet.

    Bir tâlim koşusu saatler sürer. Koşunun sonunda "sebep çizgesinde
    çevrim varmış" yahut "sözleşmedeki meleke kodda yokmuş" demek,
    saatleri çöpe atmak demektir. Bu geçit ikisini de **koşudan evvel**
    ve **saniyeler içinde** ölçer:

    **``nefs/akit.py`` İMHA EDİLDİ (ferman).** O denetim "meleke şu
    modülü bildiriyor, ``nefs/`` içinde ithal ediliyor mu" diye
    soruyordu. İthal edilmek **iş görmek değildir**; aynı yalanın
    kardeşiydi ve yeşil yandığı hâlde hiçbir şey ispat etmiyordu.

    1. ``nefs/illet.py`` -- SEBEP ÇİZGESİ SAĞLAM MI?

       (a) **ZAMAN AÇILIMLI** çizge çevrimsiz olmalı. Alan seviyesindeki
           çizgede çevrim beklenir ve kusur değildir (``makam`` ile
           ``mizan`` birbirini besler; akış devridaimlidir) -- ölçüldü:
           10 alan, 58 kenar, 6 çevrim. Orada çevrim aramak yanlış
           soruydu. Doğru soru zaman açılımındadır: ``alan@t`` bir
           **sonraki** adımı etkiler, o hâlde orada çevrim çıkarsa bir
           adım kendi geleceğine bağlı demektir ve bu imkânsızdır.
       (b) ``kelam``, ``veri``den **yalnız hüküm üzerinden** beslenmeli.
           Ölçünün adı ``hüküm_şartıyla_ayrık``tır. ``şartsız_ayrık``
           DEĞİLDİR ve olmamalıdır: kelamın veriden hiç etkilenmemesi
           modelin girdiyi hiç görmemesi demek olurdu.

    3. ``tanilama/hiz_teftisi.py`` -- **BELİRTEÇ/SN HADDİ TUTUYOR MU?**
       Ferman: *"hız konusunda garanti elde etmeden umumi eğitim
       başlatma."* Bir tâlim koşusunun ne kadar süreceği, koşmadan
       evvel tek bir kayıp çağrısı ölçülerek bilinir. Had
       ``tanilama/hiz_teftisi.py:HAD``dır ve orada yazılıdır.

    ``sert`` doğruysa ihlâl ``assert`` ile koşuyu **durdurur**. Yumuşak
    kipte yalnız raporlanır; o kip ölçüyü görmek içindir, geçmek için
    değil.
    """
    from nefs.illet import (alan_cizgesi, cevrimler, kelam_ayrismasi,
                            zaman_cizgesi)

    dug, ken, kabul = alan_cizgesi()
    assert dug, "sebep çizgesi BOŞ -- illet ölçüsü bir şey ölçmüyor"
    alan_cevrimi = cevrimler(dug, ken)
    zg, _yer = zaman_cizgesi()
    zaman_cevrimi = cevrimler(list(zg.dugumler), list(zg.kenarlar))
    ayrisma = kelam_ayrismasi()

    o: Dict[str, object] = {
        "alan": len(dug), "kenar": len(ken),
        "alan_çevrimi": len(alan_cevrimi),
        "zaman_düğümü": len(zg.dugumler),
        "zaman_çevrimi": [list(c) for c in zaman_cevrimi],
        "kelam_ayrıştı": bool(ayrisma.get("hüküm_şartıyla_ayrık", False)),
        "kelam_dökümü": ayrisma,
    }
    if hiz_ayari is not None:
        from tanilama.hiz_teftisi import AZAMI_SANIYE, HAD, olc
        h = olc(hiz_ayari)
        o["belirteç_sn"] = float(h["belirteç_sn"])
        o["hız_haddi"] = float(HAD)
        o["hız_geçti"] = bool(h["belirteç_sn"] >= HAD)
        o["kayıp_süresi"] = float(h["kayıp_süresi"])
        o["en_pahalı_uzuv"] = (h["tek_meleke"][0][0]
                               if h["tek_meleke"] else "?")
        # **TÂLİM SÜRESİ HADDİ FİİLEN DENETLENİR.** ``AZAMI_SANIYE``
        # evvelce ithal ediliyor fakat **hiç kullanılmıyordu**: padişahın
        # "toplam en fazla 10 dakika" hükmü kodda yalnız bir sayı olarak
        # duruyor, hiçbir şeyi durdurmuyordu. Kestirim tek kayıp
        # çağrısının ölçülen süresinden çıkar::
        #
        #     kestirilen = kayıp_süresi × (tur × yön + HAD yoklaması)
        #
        # Yön sayısı ``altuzay_ornek``, tur ``talim_tur``tur; ikisi de
        # ayardadır ve hocanın bütçesini onlar tayin eder.
        cagri = max(1, int(hiz_ayari.talim_tur)
                    * max(1, int(hiz_ayari.altuzay_ornek)))
        o["kestirilen_saniye"] = float(h["kayıp_süresi"]) * cagri
        o["süre_haddi"] = float(AZAMI_SANIYE)
        o["süre_geçti"] = bool(o["kestirilen_saniye"] <= AZAMI_SANIYE)
    if sert:
        assert not zaman_cevrimi, (
            "ZAMAN AÇILIMLI SEBEP ÇİZGESİNDE ÇEVRİM VAR -- bir adım "
            "kendi geleceğine bağlı: %r" % (zaman_cevrimi[:3],))
        assert ayrisma.get("kurulabilir", False), (
            "zaman çizgesi kurulamadı -- illet ölçüsü boş: %r" % (ayrisma,))
        assert ayrisma.get("hüküm_şartıyla_ayrık", False), (
            "KELAM VERİDEN DOĞRUDAN BESLENİYOR -- hüküm atlanabiliyor. "
            "Bu, ezberin açık kapısıdır. Döküm: %r" % (ayrisma,))
        if "belirteç_sn" in o:
            from tanilama.hiz_teftisi import AZAMI_SANIYE, HAD
            assert o["süre_geçti"], (
                "TÂLİM SÜRESİ HADDİ AŞILIYOR -- TÂLİM BAŞLAMAZ.\n"
                "  kestirilen: %.1f sn   had: %.0f sn\n"
                "  (bir kayıp çağrısı %.4f sn × %d çağrı)\n"
                "  Ferman: eğitim hızını toplamda en fazla 10 dakikaya "
                "indirmelisin."
                % (o["kestirilen_saniye"], AZAMI_SANIYE,
                   o["kayıp_süresi"],
                   int(o["kestirilen_saniye"] / max(1e-9, o["kayıp_süresi"]))))
            assert o["hız_geçti"], (
                "HIZ HADDİ TUTMUYOR -- TÂLİM BAŞLAMAZ.\n"
                "  ölçülen : %.1f belirteç/sn\n"
                "  had     : %.0f belirteç/sn  (%.0f kat eksik)\n"
                "  bir kayıp çağrısı: %.4f sn   en pahalı uzuv: %s\n"
                "  Ferman: hız garantisi elde etmeden umumi tâlim "
                "başlatılmaz." % (o["belirteç_sn"], HAD,
                                  HAD / max(1e-9, o["belirteç_sn"]),
                                  o["kayıp_süresi"], o["en_pahalı_uzuv"]))
    return o


def ogreniyor_mu(seyir: Sequence[float], lam: float = 1e-3
                 ) -> Dict[str, object]:
    """SEYİR EĞRİSİ DÜŞÜYOR MU -- gürültüye bakmadan (``ogrenme/izgara.py``).

    Kaybın son iki adımına bakıp "düştü" demek gürültüyü hüküm
    sanmaktır. Doğru soru eğrinin **eğilimidir** ve eğilim, gürültülü
    bir örneklemden ancak düzenlenmiş bir uydurmayla çıkarılır::

        min_c ‖Bc − y‖² + λ·cᵀSc

    ``S`` bükülme dizeyidir (``∫B''B''``); ``λ`` eğriyi yumuşatır. Bu
    tam olarak ``ogrenme/izgara.py``nin ``duzenli_uydur``udur ve
    burada süs değil hükümdür: ``eğim ≥ 0`` ise **tâlim öğrenmiyor**
    ve netice öyle yazılır.

    Bağıntı ölçütü (``bagintili_olcut``) ikinci şahittir: sabit bir
    eğri hiçbir zaman kazanamaz (payda sıfırsa 0 döner).
    """
    y = np.asarray(list(seyir), float).reshape(-1)
    assert y.size >= 2, "seyir eğrisi için en az iki nokta lâzım"
    assert np.all(np.isfinite(y)), "seyirde NaN/Inf var"
    from ogrenme.izgara import bagintili_olcut, duzenli_uydur

    t = np.linspace(-1.0, 1.0, y.size)
    G = max(2, min(8, y.size // 3))
    k = 3 if y.size > 5 else 1
    u = duzenli_uydur(t, y, G, k, lam=float(lam))
    tahmin = np.asarray(u["B"], float) @ np.asarray(u["c"], float)
    # **``n`` SERİNİN BOYUNU AŞAMAZ.** Evvelce ``max(2, y.size // 4)``
    # yazıyordu ve iki noktalı bir seyirde ``tahmin[-3]`` isteniyordu:
    # ``IndexError``. İki nokta ``talim_tur=1`` profilinde tabiîdir --
    # yâni bu hat, geçit açıldığı gün **düşerdi**. Ölçülüp düzeltildi.
    n = max(1, min(y.size - 1, y.size // 4))
    egim = float((tahmin[-1] - tahmin[-1 - n]) / (t[-1] - t[-1 - n]))
    bag = float(bagintili_olcut(t, y))
    # İKİ ŞAHİT BİRDEN. Yalnız eğime bakmak yetmez: sabit bir seyirde
    # eğim ``−2,5e−16`` çıkıyor (ölçüldü) ve kayan nokta gürültüsünü
    # "öğreniyor" diye okumak tam da örtmek olurdu. ``bagintili_olcut``
    # sabit eğride paydası sıfır olduğu için **tam 0** döner ve o kapıyı
    # kapatır.
    return {"eğim": egim, "artık": float(u["artık"]),
            "bükülme": float(u["bükülme"]), "bağıntı": bag,
            "öğreniyor": bool(egim < 0.0 and bag < 0.0),
            "toplam_düşüş": float(y[0] - y[-1])}


# =====================================================================
#  SÜREÇ HAVUZU -- kübit ileri geçişi paraleldir
# =====================================================================
_ISCI: Dict[str, object] = {}


def _isci_kur(ayar: EgitimAyari, veri, kademe=None) -> None:
    from nefs.melekeler import QNefs
    tek_iplik_zorla()
    _ISCI["nefs"] = QNefs(ayar.tohum, ayar.qayar())
    _ISCI["veri"] = veri
    _ISCI["ayar"] = ayar
    _ISCI["kademe"] = list(kademe or [])
    _ISCI["nefs"].idrak_et(np.zeros((2, ayar.satir_kubiti)))


def _isci_kayip(p: np.ndarray) -> float:
    """İşçi de **aynı** mizanı hesaplar; ayrı kayıp mukayeseyi bozardı."""
    a: EgitimAyari = _ISCI["ayar"]        # type: ignore[assignment]
    t = kulli_mizan(_ISCI["nefs"], _ISCI["veri"], p,   # type: ignore
                    a.sozluk, ayar=mizan_ayari(a),
                    hafiza=_ISCI.get("hafıza"),
                    kademe_gorevleri=_ISCI.get("kademe"))
    return float(t["kayıp"])


def mizan_ayari(a: EgitimAyari) -> "MizanAyari":
    """Tâlim ayarından mizan ayarı -- **tek kaynak**, iki nüsha değil."""
    return MizanAyari(
        zeno_tepe=float(a.zeno_tepe), lam_engel=float(a.lam_engel),
        ayna_tur=int(a.ayna_tur), ayna_teta=float(a.ayna_teta),
        ayna_r=float(a.ayna_r),
        lam_cevrim=float(a.lam_cevrim), lam_monogami=float(a.lam_monogami),
        lam_hodge=float(a.lam_hodge), cevrim_boyu=int(a.cevrim_boyu),
        # ``motor`` ve ``lif_yapisi`` mizana **geçmez**: ikisi de
        # yazmacın ölçüsüdür ve oraya ``qayar()`` ile gider. Mizan lif
        # yapısını yazmacın kendisinden okur (``_ileri``). Buraya da
        # koymak, aynı ölçünün iki nüshası olurdu (CLAUDE.md 2-B).
        tdd_cekirdek=int(a.tdd_cekirdek),
        golge_ornegi=int(a.golge_ornegi), golge_haddi=float(a.golge_haddi),
        qsvt=int(a.qudit_qsvt), qudit_derece=int(a.qudit_derece),
        qudit_yon=int(a.qudit_yon),
        cevrim_sayisi=int(a.cevrim_sayisi),
        # ── ZABITLARIN ALTI UZVU MİZANA BURADAN GEÇER ──────────────
        # Bunlar birer "isim" değildir: her biri mizanın içinde fiilen
        # çağrılan bir fonksiyonun ölçüsüdür ve hepsi kapatılabilir
        # (kapatılınca ilgili sayı sıfırlanır ve rapor kırmızı yanar).
        sadakat_acik=int(a.sadakat_acik), parite_lifi=int(a.parite_lifi),
        lam_tenakuz=float(a.lam_tenakuz), tenakuz_eps=float(a.tenakuz_eps),
        dislama_tau=float(a.dislama_tau),
        lam_kategori=float(a.lam_kategori), lam_nokta=float(a.lam_nokta),
        usul_acik=int(a.usul_acik), usul_haddi=float(a.usul_haddi),
        usul_seferi=int(a.usul_seferi),
        suphe_acik=int(a.suphe_acik), suphe_sonumu=float(a.suphe_sonumu),
        rust_t0=float(a.rust_t0),
        rust_tau=float(a.rust_tau), rust_kapanis=float(a.rust_kapanis),
        rust_muayene=int(a.rust_muayene), zeno_esigi=float(a.zeno_esigi),
        # Rüşt çizelgesinin paydası tâlimin kendi bütçesidir; elle
        # yazılmış bir sabit değildir. Bütçe değişince geçiş de kayar.
        toplam_adim=max(1, int(a.talim_tur) * max(1, int(a.altuzay_ornek))),
        tohum=int(a.tohum))


# =====================================================================
#  TEK HAT -- KÜLLÎ KAYIP TÂLİMİ (44 QMeleke fiilen eniyilenir)
# =====================================================================
def kulli_kayip_talimi(ayar: EgitimAyari = KISA_CPU,
                       gorevler: Optional[Sequence] = None,
                       paralel: bool = True) -> Dict[str, object]:
    """44 QMelekeyi Mîzân-ı Küllî ile ölçüp motorla eniyile.

    **ARTIK TEK HAT BUDUR.** Evvelce yanında ikinci bir hat vardı
    (``dalga_talimi_kos`` / ``KulliDalgaTalimMotoru``): 44 melekeyi bir
    "meclise" toplayıp 44 skalere indiriyor, ``hamiltonyen_uret`` ile
    tek bir ``Ĥ_Dimağ`` kuruyor ve o Hamiltonyeni QSVT ile soğutuyordu.
    Padişahın emriyle o mekanizma **tamamen imha edildi**: meclis
    melekeyi meleke olmaktan çıkarıyordu -- her biri bir katsayıya
    iniyor, ne okuduğu ne yazdığı belli olmuyordu. Üstelik ölçülmüştü:
    o hattın zırh kaybı üç çevrimde ``104,653426``da **hiç
    kıpırdamıyordu**; yâni öğrenmiyordu.

    Adam/SGD yoktur: motor ``ogrenme/optimize.py``dir (dalga, had
    ölçümü, vekil yüzey, durgunluk, tünelleme, denge...).
    """
    from nefs.kulli_kayip import kademe_parametreleri_ac
    from nefs.melekeler import QNefs
    from nefs.qegitim import degerlendir, ornekler

    t0 = time.perf_counter()
    # **GEÇİT KOŞUDAN EVVEL.** Saatler süren bir tâlimin sonunda
    # "akit tutmuyormuş" demek saatleri çöpe atmaktır.
    kapi = gecit(sert=True, hiz_ayari=ayar)
    hepsi = list(gorevler) if gorevler is not None else \
        gorevleri_getir("training")
    # **İMTİHAN BÖLÜMLEMESİ** -- ezberi ve sızıntıyı engeller.
    egitim_gorevleri, dogrulama = gorevleri_getir(ne="böl", gorevler=
        hepsi, dogrulama=int(ayar.dogrulama_sayisi), tohum=ayar.tohum)
    veri = ornekler(egitim_gorevleri, azami=ayar.ornek_sayisi,
                    pencere=ayar.pencere, sozluk=ayar.sozluk,
                    tohum=ayar.tohum)

    nefs = QNefs(ayar.tohum, ayar.qayar())
    nefs.idrak_et(np.zeros((2, ayar.satir_kubiti)))
    # Kademe parametreleri ``d`` sabitlenmeden EVVEL açılmalıdır; boyut
    # ortada değişirse tâlim kendi öğrendiğini siler (H39).
    kademe_parametresi = kademe_parametreleri_ac(nefs.p)
    d = len(nefs)
    p0 = nefs.vektor()
    kademe_gorevleri = list(egitim_gorevleri)[:int(ayar.kademe_gorevi)]

    havuz = None
    surec = ayar.surec or 1
    if paralel and surec > 1:
        import multiprocessing as mp
        havuz = mp.get_context("fork").Pool(
            surec, initializer=_isci_kur,
            initargs=(ayar, veri, kademe_gorevleri))
        _ISCI["hafıza"] = None      # her işçi kendi hafızasını kurar

    # **HATA FONKSİYONU MÎZÂN-I KÜLLÎ'DİR** (nefs/kulli_mizan.py).
    #
    #     ℒ_Küllî = ℒ_Rezonans + λ₁ℒ_Çevrim + λ₂ℒ_Monogami + λ₃ℒ_Hodge
    #
    # Dördü de kuantumun kendi hadiselerinden mülhemdir ve hiçbiri
    # veriye kör teslimiyet değildir:
    #   Rezonans  -- Uhlmann sadakati (kör NLL DEĞİL)
    #   Çevrim    -- Wilson holonomisi; manayı bilmeden tenakuz bulur
    #   Monogami  -- CKW eşitsizliği; sahte illetleri budar
    #   Hodge     -- Δ|Ψ⟩ = 0; harmonik hüküm
    mzn = mizan_ayari(ayar)
    hafiza = Hafiza(kapasite=int(ayar.hafiza_kapasitesi),
                    yazma=float(ayar.hafiza_yazma),
                    sonum=float(ayar.hafiza_sonumu),
                    zeno_esigi=float(ayar.zeno_esigi),
                    zeno_tepe=float(ayar.zeno_tepe),
                    ayniyet=float(ayar.hafiza_ayniyet),
                    buhar=float(ayar.hafiza_buhar), tohum=int(ayar.tohum))
    _sayac = {"çağrı": 0}
    # ── HIZÖLÇER ANA HATTA **KALICI** BAĞLANIR ────────────────────
    # Evvelce hız yalnız ``gecit()``te, koşudan EVVEL, tek bir yoklama
    # çağrısıyla ölçülüyordu. O bir kestirimdir: koşunun kendisi başka
    # türlü davranabilir (önbellek ısınır, yığın dolar, hafıza büyür).
    # Ferman: *"hızölçeri ana hatta kalıcı olarak bağla."* Artık **her**
    # küllî mizan çağrısı saatlenir ve belirteç sayılır; hız koşarken
    # bilinir, sonradan tahmin edilmez.
    olcer = Hizolcer(belirtec_basina=len(veri) * int(ayar.pencere),
                     had=None, ad="küllî mizan")
    hizolcer_bagla(olcer)

    def kayip_p(P: np.ndarray) -> np.ndarray:
        P = np.atleast_2d(np.asarray(P, float))
        if havuz is not None:
            return np.array(list(havuz.map(_isci_kayip, list(P))))
        out = np.empty(P.shape[0], float)
        for i, p in enumerate(P):
            _sayac["çağrı"] += 1
            with olcer.saat():
                t = kulli_mizan(nefs, veri, p, ayar.sozluk, ayar=mzn,
                                hafiza=hafiza, adim=_sayac["çağrı"],
                                kademe_gorevleri=kademe_gorevleri)
            out[i] = float(t["kayıp"])
        return out

    # **`nefs/talim.py` ilga edildi; motor `ogrenme/optimize.py`dir.**
    # Bilinen bir yüzeyde ölçülerek karşılaştırıldı (d=24 ağırlıklı
    # karesel, V(p₀)=73,3498, asgarî 0)::
    #
    #     divanın taslak adımı   73,3498 → 73,3498   (SIFIR kazanç)
    #     eski nefs/talim        73,3498 → 72,5763
    #     ogrenme/optimize       73,3498 →  0,5410   ← seçilen
    #
    # Eski tâlimin kazancı %1; yeni motorunki 135 kat. Kübit kodlaması
    # (Gri kod) da kalktı: yeni motor sürekli uzayda çalışır.
    opt = OptimizeAyari(
        ad=ayar.ad, tur=ayar.talim_tur, yaricap=ayar.yaricap,
        gcl_nokta_sayisi=max(8, int(ayar.ornek)),
        yon_sayisi=int(ayar.altuzay_ornek), blok=int(ayar.blok),
        sesli=True, tohum=ayar.tohum)
    # **HOCA (kütük H212, H223'te motora eridi).** Üç uzuv da bu hatta
    # lâzımdır ve artık motorun kendi ayarındadır:
    #   TÜNEL  -- durgunluk düşüp HAD zorlayıcı bulamadığında STA
    #             karşıt-adiyabatik sürüşü (H29'un çift şartı).
    #   VEKİL  -- kapalı (varsayılan): küllî kayıp çağrısı pahalıdır,
    #             RKHS yüzeyi ancak aday çoğaldığında değer.
    #   BÜTÇE  -- ``d`` büyürse koşu SESSİZCE günlere yayılmasın diye
    #             peşinen reddeder (idrak/model.py dersi, H209).
    opt.tunel_acik = True
    opt.vekil_acik = False
    opt.bütçe_denetimi = True
    opt.azami_saniye = float(ayar.azami_talim_saati) * 3600.0
    try:
        r = hoca_egit(kayip_p, p0, opt)
    finally:
        if havuz is not None:
            havuz.close()
            havuz.join()

    p_yildiz = np.asarray(r["p"], float)
    assert p_yildiz.size == d, (
        "tâlim %d parametre aldı, %d döndürdü" % (d, p_yildiz.size))
    assert np.all(np.isfinite(p_yildiz)), "tâlim NaN/Inf parametre döndürdü"
    nefs.yukle(p_yildiz)
    # **AYNA ÇIKARIMDA DA FİİLEN KOŞAR.** Değerlendirme evvelce
    # ``argmax(P)`` diyordu -- yâni kör seçim. Kıvılcım (vakum
    # uyarılması) buraya bağlandı; ``ayna=None`` verilirse eski kör
    # yol geri gelir ve fark ölçülebilir (H90).
    from nefs.ayna import AynaAyari
    ayna = AynaAyari(teta=float(ayar.ayna_teta), r=float(ayar.ayna_r),
                     tur=int(ayar.ayna_tur), tohum=int(ayar.tohum))
    deg = degerlendir(nefs, dogrulama, azami=ayar.degerlendirme_gorevi,
                      pencere=ayar.pencere, sozluk=ayar.sozluk,
                      azami_uret=ayar.azami_uret, ayna=ayna)

    # --- ÖĞRENİYOR MU? (ogrenme/izgara.py -- düzenli uydurma)
    ham_seyir = [float(x["V"]) for x in (r.get("seyir") or [])
                 if isinstance(x, dict) and "V" in x]
    ders = (ogreniyor_mu([float(r["V_ilk"])] + ham_seyir)
            if ham_seyir else
            {"öğreniyor": bool(r["V_son"] < r["V_ilk"]), "eğim": 0.0,
             "bağıntı": 0.0, "artık": 0.0, "bükülme": 0.0,
             "toplam_düşüş": float(r["V_ilk"] - r["V_son"])})

    # --- ZABIT 2'NİN ÜÇ USULÜ: DURUM NE KADAR SIKIŞIYOR?
    #
    # Tâlim bittikten sonra öğrenilmiş durum bir kere kurulur ve üç
    # usul onun üstünde **fiilen** koşar. Neticeleri hazineye yazılır:
    # bir sonraki koşu, durumun hangi temsille taşınacağını bunlardan
    # bilir. Kazanç yoksa sayı öyle çıkar ve saklanmaz.
    q_son = nefs.idrak_et(np.zeros((ayar.yigin(), 2, ayar.satir_kubiti)))
    psi_son = np.asarray(q_son.y.psi[0], complex)
    # **GALOIS TABLEAU: durumun ayrık temsili** (nefs/galois.py).
    # Sürekli genlik vektörü iptal; durum GF(2⁸) elemanları ve
    # stabilizer bitmask olarak taşınır.
    ga = GaloisAyari(us=int(ayar.galois_us), n=int(ayar.tableau_n),
                     tohum=int(ayar.tohum))
    tab = tableau_kur(psi_son, ga)
    # **TDD ARTIK YALNIZ DENETÇİ**: çekirdek hashlenir, kanonik adres
    # alınır. O(1) eşitlik için; hesap için değil.
    tdd = kanonik_adres(psi_son, cekirdek=int(ayar.tdd_cekirdek),
                        ayar=TddAyari(tolerans=float(ayar.tdd_tolerans)))
    stab = kararname(psi_son, mertebe=int(ayar.stab_mertebe))
    # **GÖLGE ARTIK KESTİRİM DE YAPIYOR.** Evvelce yalnız ``golge_al``
    # çağrılıyor, ``kestir`` hiç çağrılmıyordu; halbuki gölgenin
    # **manası** kestirimdir -- örnek almak tek başına bir ölçüm
    # değildir. Rapor da olmayan anahtarları (``örnek``,
    # ``gözlenebilir``, ``azamî_hata``) okuyordu ve geçit açıldığı gün
    # ``KeyError`` ile düşerdi. Ferman 1-C(b)'nin tarif ettiği
    # münafıklığın ta kendisiydi: çağrılmayan bir fonksiyonun neticesi
    # raporlanıyordu. Ölçüldü ve düzeltildi.
    #
    # Gözlenebilirler **uydurulmaz**: yazmacın kendi hüküm alanlarıdır.
    golge_ham = golge_al(psi_son, GolgeAyari(
        ornek=max(32, int(ayar.golge_ornegi) or 128),
        had=float(ayar.golge_haddi), tohum=int(ayar.tohum)))
    goz = [q_son.y.sektor(ad) for ad, _ in q_son.ayar.kulli_alanlar]
    t_g = time.perf_counter()
    golge = kestir(golge_ham, goz, tahkik=True)
    golge["gölge_sn"] = time.perf_counter() - t_g
    # Tam ölçüm: bütün sektör ağırlıkları doğrudan. Hız kıyası ölçülür,
    # iddia edilmez.
    t_t = time.perf_counter()
    _P = np.abs(psi_son) ** 2
    _P = _P / max(float(_P.sum()), 1e-300)
    _tam = np.array([float(_P[i:j].sum()) for (i, j) in goz])
    golge["tam_sn"] = time.perf_counter() - t_t
    golge["hız"] = float(golge["tam_sn"] / max(golge["gölge_sn"], 1e-12))
    golge.setdefault("azamî_hata",
                     float(np.max(np.abs(golge["kestirim"] - _tam)))
                     if _tam.size else 0.0)
    # ══════════════════════════════════════════════════════════════
    #  NON-CLIFFORD ÇIKMAZININ ÜÇ ÇARESİ -- ÜÇÜ DE FİİLEN KOŞAR
    # ══════════════════════════════════════════════════════════════
    #
    # **1. ÇARE -- MATCHGATE/FLO (Valiant-Terhal-DiVincenzo).**
    # Tâlimin bulduğu parametreler sürekli açılardır ve kübit tabanında
    # non-Clifford'durlar. Aynı açılar Majorana kovaryansına taşınır;
    # orada her biri dört satır/sütunda tek bir SO(2N) Givens dönmesidir
    # ve stabilizer rank **1**de kalır. İddia burada sınanır: ``kapı``
    # sayısı büyütülünce de χ 1 kalmalıdır.
    flo = flo_evrimi(p_yildiz, MatchgateAyari(
        mod=int(ayar.flo_modu), kapi=int(ayar.flo_kapisi),
        tohum=int(ayar.tohum)))
    # **2. ÇARE -- GALOIS S-BOX (Rijndael otomorfizmi).** Gayri-lineerlik
    # sürekli bir B-spline değil, ``x ↦ M·x²⁵⁴ + b (mod P)`` cebrî
    # dönüşümüdür. Tableau'nun genlik baytları bundan geçirilir;
    # dönüşümün gayri-lineerliği ayrıca **ölçülür** (diferansiyel
    # tekdüzelik ve Walsh tepe değeri), iddia edilmez.
    sb = sbox_bukme(tab, acik=bool(int(ayar.sbox_acik)))
    sb_olcu = sbox_olcu(us=int(ayar.galois_us))
    # **3. ÇARE -- CNOT-DIHEDRAL FAZ POLİNOMU (Amy-Maslov-Mosca).**
    # Yazmaç koşu boyunca köşegen fazları genliğe tek tek vurmaz;
    # ``Z_m``de tamsayı olarak biriktirir (``faz_birikimi``). O birikim
    # burada bir faz polinomuna oturtulur ve **derecesi ölçülür**:
    # derece ≤ 3 ise durum CNOT-Dihedral sınıfındadır ve tablo
    # dallanmaz. Derece büyükse o da yazılır, örtülmez.
    fazp = faz_oturt(q_son.y.faz_birikimi(),
                     FazAyari(mertebe=int(ayar.faz_mertebesi),
                              derece=int(ayar.faz_derecesi)))
    # **SİKLOTOMİK KOSET İNDİRGEMESİ.** ``fazp["derece"]`` 3'ü aşarsa
    # -- ki ölçüm 12 dedi -- CNOT-Dihedral iddiası düşer. Düşen iddia
    # yerine boşluk konmaz: derece siklotomik kosete indirgenir ve
    # ``Tr(α·x^d) = Tr(α^{2^{-k}}·x^taban)`` eşitliği **sınanır**.
    sik = koset_indirge(int(fazp["derece"]), SiklotomikAyari(
        us=int(ayar.siklotomik_us), taban=int(ayar.siklotomik_taban),
        derece=int(ayar.siklotomik_derece)))
    sik["iz_eşitliği"] = iz_esitligi(SiklotomikAyari(
        us=int(ayar.siklotomik_us), taban=int(ayar.siklotomik_taban),
        derece=int(ayar.siklotomik_derece)))
    # ══════════════════════════════════════════════════════════════
    #  ZABIT: 1 TB/S GPU AKIŞI -- DÖRT MOTOR FİİLEN KOŞAR
    # ══════════════════════════════════════════════════════════════
    # Dört motorun hepsi burada koşar ve **ölçülür**. GPU yoksa aynı
    # cebir ``numpy``da koşar; o zaman rapor "GPU YOK" der ve 1 TB/s
    # iddiası **kırmızı yanar** (ferman 5). İlan edilen donanım
    # sayıları (VRAM, PCIe, TOPS) ayardadır ve ölçülmüş gibi
    # gösterilmez -- çatı çizgisi onlardan hesaplanır, ölçümden değil.
    # Ayardan geçen **yalnız iki sayı**: hedef had (bir iddia) ve
    # genleşme katsayısı (bir tasarım). Kart adedi, VRAM, PCIe, SIMD
    # genişliği, kelime boyu, dilim sayısı ve sınır baytı buraya
    # yazılmaz -- ``nefs/donanim.py`` onları **yoklayarak** bulur.
    akis = gpu_akisi(psi_son, tab, GpuAyari(
        had=float(ayar.gpu_akis_haddi),
        genlesme=int(ayar.gpu_genlesmesi), tohum=int(ayar.tohum)))
    # ══════════════════════════════════════════════════════════════
    #  ZABITLARIN ALTI UZVU -- KOŞTUKLARI YERDEN HESAP SORULUYOR
    # ══════════════════════════════════════════════════════════════
    #
    # **İSİM EKLEMEK BAĞLAMAK DEĞİLDİR (ferman 1-C/b).** Aşağıdaki üç
    # ``beyan`` çağrısı bir rapor süsü değil, bir **denetimdir**: altı
    # uzuv da mizanın içinde, her kayıp çağrısında koşar; koşmadıysa
    # sayaçları sıfır kalır ve buradaki ``assert`` koşuyu **durdurur**.
    # Yâni "bağladım" demenin bedeli var.
    sad = sadakat_beyani()
    usl = usul_beyani()
    sup = suphe_beyani()
    assert int(sad["çağrı"]) > 0, (
        "MANTIĞA SADAKAT HİÇ KOŞMADI -- ``nefs/sadakat.py`` ana akışta "
        "çağrılmıyor demektir. Sadakat 7/24 koşmalıdır; koşmuyorsa "
        "sistem mantık dışına taşabiliyor.")
    assert int(sup["çağrı"]) > 0, (
        "ŞÜPHE MANİFOLDU HİÇ KOŞMADI -- ``nefs/suphe.py`` bağlanmamış.")
    # Sefer 7/24 koşmaz (zabıt: kalp gedik hissedince açılır), o hâlde
    # ``sefer`` sayısına assert konmaz; fakat **yoklama** sayısına konur:
    # kalbin hiç yoklamaması, kapının hiç çalınmaması demektir.
    assert int(usl["yoklama"]) > 0, (
        "MANTIK YÜRÜTME KAPISI HİÇ YOKLANMADI -- ``nefs/usul.py`` "
        "bağlanmamış. Sefer açılmayabilir; yoklanmaması başka şeydir.")
    # **SON DURUM MANTIK ALT-UZAYINDA MI?** Tâlimin bulduğu ağırlıkla
    # kurulan durumun paritesi burada, tahtın kendi elinde yoklanır.
    # Neticesi kullanılır: alarm sönmediyse rapor onu yazar.
    son_sadakat = sadakat_uygula(tab, SadakatAyari(
        acik=int(ayar.sadakat_acik), parite_lifi=int(ayar.parite_lifi),
        lif_yapisi=tuple(ayar.lif_yapisi)))

    # --- MİZANIN DÖRT KEFESİ AYRI AYRI (hangisi kırmızı, görünsün)
    kefeler = kulli_mizan(nefs, veri, p_yildiz, ayar.sozluk, ayar=mzn,
                          hafiza=hafiza, adim=_sayac["çağrı"],
                          kademe_gorevleri=kademe_gorevleri, ne="döküm")
    # --- VERİ KENDİ KENDİNİ DÖRDE AYIRDI MI? (zabıt V. fasıl)
    #     Hakikat / Yanlış / Şüpheli / Kuru gürültü -- etiketsiz.
    cetvel = mizan_cetveli(nefs, veri, p_yildiz, ayar.sozluk, ayar=mzn)

    # --- HAZİNE: ağırlıklar safetensors olarak kaydedilir (main/hazine.py)
    # **FITRAT İLE HADİSE AYNI DOSYADA, AYRI TENSÖRLERDE.** ``p``
    # ağırlıktır (fıtrat); ``hafıza.*`` tecrübedir (hadise). İkisini
    # ayrı tensörlerde tutmak, ayrı şeyler olduklarını dosyanın
    # kendisinde görünür kılar.
    kayit = hazine.koy(
        os.path.join(HAZINE_DIZINI, "dimag_%s" % ayar.ad),
        dict({"p": p_yildiz}, **hafiza.hazineye()),
        {"ayar": ayar.ad, "parametre": d, "V_ilk": float(r["V_ilk"]),
         "V_son": float(r["V_son"]), "satır_kübiti": int(ayar.satir_kubiti),
         "sözlük": int(ayar.sozluk), "pencere": int(ayar.pencere),
         "yerel_kübit": int(ayar.yerel_kubit), "bağ": int(ayar.bag),
         "mera_kademe": int(ayar.mera_kademe), "tohum": int(ayar.tohum),
         "öğreniyor": bool(ders["öğreniyor"]),
         "mizan": {k: v for k, v in kefeler.items()
                   if isinstance(v, (int, float))},
         "veri_cetveli": cetvel,
         "hafıza_kapasitesi": int(ayar.hafiza_kapasitesi),
         "hafıza_yazma": float(ayar.hafiza_yazma),
         "hafıza_sönümü": float(ayar.hafiza_sonumu),
         "zeno_eşiği": float(ayar.zeno_esigi)})

    return {"ayar": ayar.ad, "parametre": d,
            "geçit": kapi, "ders": ders, "hazine": kayit,
            "tdd": tdd, "stabilizer": stab, "gölge": golge,
            "galois": tab.beyan(),
            "flo": flo, "sbox": sb, "sbox_ölçü": sb_olcu,
            "faz_polinomu": fazp, "gpu_akışı": akis, "siklotomik": sik,
            "sadakat": sad, "son_sadakat": son_sadakat,
            "usul": usl, "şüphe": sup,
            # Hızölçer koşunun **tamamını** gördü; geçitteki tek
            # yoklama değil, her kayıp çağrısı.
            "hızölçer": hizolcer_beyani(),
            "çekirdek": cekirdek_beyani(),
            "mizan": kefeler, "veri_cetveli": cetvel,
            "hafıza": hafiza.beyan(), "rüşt": float(kefeler["α_rüşt"]),
            "veri": len(veri), "süreç": surec,
            "V_ilk": float(r["V_ilk"]), "V_son": float(r["V_son"]),
            "süre_sn": time.perf_counter() - t0,
            "kayıp_çağrısı": int(r.get("kayıp_çağrısı", 0)),
            "seyir": r.get("seyir", []),
            "değerlendirme": deg,
            "tâlim_günlüğü": r.get("günlük", []),
            "düşen_uzuv": r.get("düşen_uzuv", {}),
            "kademe_görevi": len(kademe_gorevleri),
            "kademe_parametresi": kademe_parametresi,
            "p": p_yildiz}


# =====================================================================
#  MECLİS MEKANİZMASI İMHA EDİLDİ -- padişahın ikinci emri
# =====================================================================
#
# Burada 175 satırlık ``KulliDalgaTalimMotoru`` ve ``dalga_talimi_kos``
# duruyordu. Yaptıkları iş şuydu:
#
#     melekeleri_kur(44) → KulliMelekeManifoldu
#         → hamiltonyen_uret()      44 melekeyi 44 katsayıya indirger
#         → bgcm_mizan_enerjisi()   o katsayılardan tek skaler
#         → H_toplam = H_zırhlı + λ·mizan·I
#         → qsvt_gibbs_sogutma(v, H_toplam, ...)
#         → katsayilari_guncelle(...)
#
# Yâni **meclis**: her meleke bir sandalyeye, her sandalye bir sayıya
# indiriliyor; sonra o sayılar toplanıp tek bir Hamiltonyen kuruluyordu.
# Bir melekenin ne okuduğu, ne yazdığı, hangi lifte durduğu bu terkipte
# **kayboluyordu**. Padişahın emri kat'îdir: *"kalan kuantum melekelerini
# meclise sokan mekanizmayı derdest edip imha edeceksin, tamamen
# bozacaksın, ana akıştan çıkarıp sileceksin."*
#
# İmha edilenler (ferman 2-B: fazlalık kökünden kesilir):
#
#     main/egitim.py   KulliDalgaTalimMotoru, dalga_talimi_kos,
#                      ``kos``un 1. HAT bloğu ve rapor faslı,
#                      cevrim/gorev/qsvt_derecesi/beta_maksimum/
#                      gcl_nokta_sayisi/lambda_mizan/ogrenme_orani ayarları
#     nefs/melekeler.py  KulliMelekeManifoldu, H_toplam, DimagAyari,
#                      melekelerin_dondurucusu, zirh_projektorleri,
#                      melekeleri_kur
#
# Yerine bir şey konmadı: **meclise hâcet yoktu.** 44 QMeleke zaten
# ``QNefs.idrak_et``te tek tek koşuyor ve her biri yazmacın kendi
# lifine vuruyor. Meclis o koşunun üstüne kurulmuş ikinci bir yoldu ve
# iki yol yan yana durdukça hangisinin koştuğu belirsizdi (ferman 1-E).


def muhurle(cikti_yolu: str, netice: Dict[str, object]) -> None:
    """Telemetriyi ``.olcum.json`` olarak mühürle.

    Evvelce bu iş ``KulliDalgaTalimMotoru.kaydet``teydi ve orada ayrıca
    ``.parametre.npy`` yazılıyordu -- yâni **ağırlık iki ayrı yere**
    yazılıyordu: hazineye (safetensors) ve bir ``.npy``ye. İkincisi
    kimse tarafından okunmuyordu. Meclisle beraber o da kesildi;
    ağırlığın tek yeri hazinedir (``main/hazine.py``).
    """
    dizin = os.path.dirname(cikti_yolu)
    if dizin:
        os.makedirs(dizin, exist_ok=True)
    with open(cikti_yolu + ".olcum.json", "w", encoding="utf-8") as f:
        json.dump({k: v for k, v in netice.items() if k != "p"},
                  f, ensure_ascii=False, indent=2, default=float)
    print("  [MÜHÜR] Ölçümler kaydedildi: %s.olcum.json" % cikti_yolu,
          flush=True)


# =====================================================================
def kos(ayar_adi: str = "kısa", cikti: Optional[str] = None,
        kulli_kayip_ile: bool = True) -> str:
    """Tâlimi koştur. **Burada tek satır rapor metni yoktur (ferman 1-G).**

    Taht bir nazırlık katıdır: uzvu kurar, çağırır, neticesini beyan
    uzvuna verir. Metnin nasıl yazılacağını ``tanilama/beyan.py`` bilir.
    """
    ayar = PROFILLER.get(ayar_adi, KISA_CPU)
    tek_iplik_zorla()
    kulli: Optional[Dict[str, object]] = None
    if kulli_kayip_ile:
        # ``except`` KALDIRILDI (ferman). Evvelce bu hat düşerse bir satır
        # basılıp koşu devam ediyordu: tâlimin ASIL hattı çökmüşken netice
        # yine de basılıyordu.
        kulli = kulli_kayip_talimi(ayar)
        assert kulli and kulli.get("hazine"), (
            "küllî kayıp hattı BOŞ döndü -- hazineye bir şey yazılmadı")
    if cikti and kulli:
        muhurle(cikti, kulli)
    return talim_beyani(ayar, kulli)



#: ``taht`` kipleri. Padişahın **tek** girişi budur; yanında ikinci bir
#: ``__main__`` bırakmak paralel devlettir. KÜME 9'a kadar dört ayrı taht
#: vardı (``main.egitim``, ``main.cikarim``, ``main.kaggle_egitim``,
#: ``main.kaggle_cikarim``) ve erişilebilirlik hesabı dördünü de "giriş"
#: sayıyordu. O hesap fermanla İMHA EDİLDİ: ithal edilmek iş görmek
#: değildir. Taht yine tektir, fakat artık bunu bir sınama değil kodun
#: kendisi söyler.
KIPLER: Tuple[str, ...] = ("tâlim", "mizan", "sabit", "kaggle", "veri")


def taht(ne: str = "tâlim", *arg: str) -> str:
    """Tek hâkimin tek kapısı: bütün icra buradan dağıtılır.

    ``ne`` kipi:

    * ``"tâlim"``  -- ``kos``: iki hattın tek hatta terkibi (H230).
    * ``"sabit"``  -- ``tanilama/sabit_teftisi.py``: elle tayin edilmiş
      bütün sabitlerin listesi. Hangisi ayara bağlı, hangisi koda gömülü,
      hangisi hiç okunmuyor -- ``ast`` ile çıkarılır.
    * ``"mizan"``  -- ``nefs/kulli_mizan.py``: hata fonksiyonunun kendisi.
      Dört kefe (Rezonans, Çevrim, Monogami, Hodge) ayrı ayrı ölçülür ve
      verinin etiketsiz dört kampa ayrılması gösterilir. **Kök budur.**
    * ``"kaggle"`` -- ``main/kaggle_egitim.py`` + ``main/kaggle_cikarim.py``.
      Bunlar ayrı birer taht DEĞİL, tahtın koşum kipidir.
    * ``"veri"``   -- ``main/veri.py``: belirteçleri 500 MB'lık,
      64 bayta hizalı, mmap'lenebilir parçalara dizer ve Kaggle'a
      umumi veri kümesi olarak gönderir. Hem Kaggle'da hem burada.
    **``teftiş`` kipi İMHA EDİLDİ.** ``tanilama/divan.py`` bir isim
    listesiydi: her modülü ithal edip "eksik mi" diye bakıyordu. İthal
    edilebilmek iş görmek değildir; o tablo, bağlanmamış bir dosyayı
    da "tebaa" gösteriyordu.

    Buradaki hiçbir dal yeni matematik yazmaz; hepsi mevcut uzuvların
    çağrısıdır. Yeni bir formül yazarsa bu kapı nazırlık olmaktan çıkar,
    çip olur.
    """
    ne = str(ne)
    if ne == "kaggle":
        from main.kaggle_egitim import kaggle_talimini_baslat
        from main.kaggle_cikarim import kaggle_teslimat_dosyasi_uret
        from ogrenme.kaggle_donanim import ayar_sec
        veri = arg[0] if arg else "/kaggle/input"
        # Profil elle yazılmaz: **donanımdan okunur.** ``ayar_sec``
        # bu oturuma kadar hiçbir yerden çağrılmıyordu (yetim ölçüldü),
        # dolayısıyla 84 GB'lık makinede de "kısa" profil koşuyordu.
        prof = ayar_sec()
        t = kaggle_talimini_baslat(veri)
        # **FERMAN 1-G:** metin burada kurulmaz, beyan uzvuna havale edilir.
        return kaggle_beyani(prof, t, kaggle_teslimat_dosyasi_uret)
    if ne == "sabit":
        # **ELLE TAYİN EDİLEN HER SABİT GÖRÜNÜR OLMALI.** Padişahın
        # hükmü: *"elle tayin ettiğin tüm sabit değişkenleri mutlaka bir
        # fonksiyona bağlamak ya da değerini değiştirmek üzere evvela
        # bana liste halinde sunmak."* Bu kip o listeyi koddan **ast**
        # ile çıkarır; hafızadan yazılmaz, dolayısıyla eksik olamaz.
        from tanilama.sabit_teftisi import rapor as sabit_raporu
        return sabit_raporu(*(arg[:1] or ()))
    if ne == "mizan":
        # Mîzân-ı Küllî'yi **tâlim koşturmadan** ölç: dört kefe ayrı ayrı,
        # ve verinin kendini dörde ayırması (hakikat/tenakuz/şüpheli/
        # gürültü). Kök burasıdır; kök tutmadan ağacı büyütmenin manası
        # yoktur.
        from nefs.kulli_mizan import rapor as mizan_raporu
        return mizan_raporu(arg[0] if arg else "kısa")
    if ne == "veri":
        # Veri dönüştürücü: hem Kaggle hem burası. Ayrı bir taht
        # değil, tahtın kipi.
        from main.veri import rapor as veri_raporu
        return veri_raporu(*(arg[:1] or ("training",)))
    if ne == "tâlim":
        ad = arg[0] if arg else "kısa"
        yol = arg[1] if len(arg) > 1 else "depo/kulli_dimag_talim"
        return kos(ad, yol)
    raise ValueError("bilinmeyen kip %r; kipler: %s" % (ne, ", ".join(KIPLER)))


if __name__ == "__main__":                               # pragma: no cover
    if len(sys.argv) > 1 and sys.argv[1] in KIPLER:
        print(taht(sys.argv[1], *sys.argv[2:]))
    else:
        print(taht("tâlim", *sys.argv[1:]))
