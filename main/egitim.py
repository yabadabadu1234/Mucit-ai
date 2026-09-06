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
# **FERMAN 1-H -- TEK MOTOR: TÂLİM DE KONUŞUR.** ``hazineden_yukle`` ve
# ``hafizayi_yukle`` evvelce yalnız ``main/cikarim.py``deydi; o hâlde
# tâlim, öğrendiğiyle **hiç konuşmuyordu** ve doğru konuşup
# konuşmadığı ancak ayrı bir koşuda anlaşılıyordu. İki kapı arasındaki
# meşru tek fark eniyilemenin koşup koşmamasıdır.
from main.cikarim import hazineden_yukle, hafizayi_yukle, padisah  # noqa: E402
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
# ``Tableau``, ``palmer_i`` ve ``gf_carp`` buradan **kesildi**: üçü de
# ithal ediliyor fakat tahtta hiç çağrılmıyordu (ferman 1-C/b: ithal
# etmek bağlamak değildir). ``palmer_i``nin iddiası -- ``i²=−1``,
# transandantal faz yok -- artık ``palmer_olcu`` ile **sınanıyor**;
# evvelce rapor onu her koşuda yazıyor, kimse ölçmüyordu.
from nefs.galois import (GaloisAyari, tableau_kur,         # noqa: E402
                         sbox_bukme, sbox_olcu, palmer_olcu)
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
# ``matchgate_mi`` buradan kesildi ve **koştuğu yere kondu**:
# ``flo_evrimi`` artık kendi ürettiği kapıları onunla sınıyor. Evvelce
# taht onu ithal ediyor, hiç çağırmıyordu; yâni "bu kapılar
# matchgate'tir" iddiası, sınayan fonksiyon elde dururken sınanmıyordu.
from nefs.matchgate import MatchgateAyari, flo_evrimi     # noqa: E402
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
# **ALTI UZVUN DÖRDÜ ARA KATA BAĞLANDI, İTHALLERİ KESİLDİ.**
# ``tenakuz``, ``rust``, ``tabakali_mizan`` ve ``usul_kos``/
# ``suphe_manifoldu`` mizanın **içinde** koşar; tahtta yalnız adları
# duruyordu ve ferman 1-C(b) buna "isim eklemek" der. Ayarları
# ``mizan_ayari`` ile geçer, hesapları ``*_beyani`` ile sorulur.
# Tahtta kalan üç isim, tahtın **fiilen çağırdığı** üç şeydir.
# ══════════════════════════════════════════════════════════════════
#  ÖLÇEK -- **USUL FERMANI: DOSYA HENÜZ YOKKEN**
# ══════════════════════════════════════════════════════════════════
#
# Padişahın hükmü: *"bulacağın bütün sabit ayarları tek veya çok az
# formüle en optimize şekilde bağla, mümkün olduğunca cömert ol."*
#
# ``EgitimAyari``de altmışa yakın elle yazılmış sayı vardı. Her biri bir
# zamanlar ölçülmüştü, fakat ölçüldüğü şart değişince sayı yerinde
# kaldı: yâni sabitler, geçmiş bir ölçümün **mumyasıydı**. Artık üç kök
# ve üç formül var; gerisi türetiliyor.
#
#   KÖK 1  sozluk   -- veriden gelir, tayin edilmez.
#   KÖK 2  comert   -- padişahın tek kabzası: 0 = darboğaz, 1 = donanımın
#                      izin verdiği azamî. Cömertlik burada ayarlanır.
#   KÖK 3  donanım  -- ``nefs/donanim.py`` yoklar (ferman 5-B).
#
#   FORMÜL 1 (YAPI)    lif yapısı, hüküm lifi, yığın -- **önbellekten**.
#   FORMÜL 2 (BÜTÇE)   çağrı × örnek × pencere = ölçülen hız × süre haddi
#   FORMÜL 3 (DENGE)   λ ağırlıkları -- kefeler ölçülür, elle yazılmaz.
from nefs.olcek import Kok, olcek, denge, olcek_beyani  # noqa: E402
# ══════════════════════════════════════════════════════════════════
#  KEYFİYET VE MÜNASEBET -- **USUL FERMANI: DOSYALAR HENÜZ YOKKEN**
# ══════════════════════════════════════════════════════════════════
#
# **FERMAN 1-I:** *"O veri için hata sıfırlanana kadar devam etmelisin,
# sonra yeni veri getirmelisin. Böylece bir süre sonra tüm veriler için
# müşterek bir münasebet haritası oluşacak."*
#
# **FERMAN 1-J:** *"Eşik koyarken sabit bir değer koymayacaksın, bir
# fonksiyona bağlı olacak o eşik. Yâni kemiyete değil keyfiyete, o
# keyfiyetin ne nispete eriştiğini ölçen bir fonksiyon vasıtasıyla."*
#
#   nefs/keyfiyet.py   ÜÇ KAT'Î HUDUT ölçülür ve tek nispete iner:
#                        1. TENAKUZ      (parite alarmı, ω taklası)
#                        2. KISIRDÖNGÜ   (kanonik adres kapanışı)
#                        3. MANTIKSIZLIK (kod uzayı dışına taşma)
#                      Eşik bir sayı değil, bu üç hududun temizlik
#                      nispetini ölçen fonksiyonun **kendisidir**.
#   nefs/munasebet.py  Bir örneğin hududu temizlenene kadar üstünde
#                      durulur; temizlenince yeni örnek gelir ve
#                      aradaki bağ **müşterek münasebet haritasına**
#                      işlenir.
from nefs.keyfiyet import (KeyfiyetAyari, keyfiyet,      # noqa: E402
                           keyfiyet_beyani)
from nefs.munasebet import (MunasebetAyari, munasebet_kos,  # noqa: E402
                            munasebet_beyani)
# ══════════════════════════════════════════════════════════════════
#  KÜLLİYAT -- HARİCÎ VERİ (main/kulliyat.py)
# ══════════════════════════════════════════════════════════════════
#
# Padişahın emri: *"Kodu öyle yaz ki gidip oradan veri çekip burada
# eğitime katsın ama dosyaları repoya tümden koymasın."* Külliyat
# ``depo/kulliyat/`` altına çekilir (depoya girmez) ve tâlime katılır.
from main.kulliyat import (kulliyat_cek, kulliyat_verisi,   # noqa: E402
                           kulliyat_beyani)  # noqa: E402
from nefs.usul import usul_beyani                         # noqa: E402
from nefs.suphe import suphe_beyani                       # noqa: E402
# **FERMAN 1-G:** raporun yeri taht değil, kendi uzvudur.
from tanilama.beyan import (talim_beyani,                 # noqa: E402
                            kaggle_beyani)

#: Ağırlıkların yattığı dizin. ``main/cikarim.py`` buradan okur.
HAZINE_DIZINI = os.environ.get("MUCIT_HAZINE", "depo/hazine")

__all__ = ["EgitimAyari", "DAR", "ORTA", "AZAMI",
           "KISA_CPU", "AZAMI_KAGGLE",
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
    """**ÜÇ KÖK, ÜÇ FORMÜL.** Gerisi türetilir (``nefs/olcek.py``).

    ===================================================================
    NİÇİN SABİT KALMADI
    ===================================================================

    Burada altmışa yakın elle yazılmış sayı vardı. Her birinin yanında
    bir ölçüm şerhi duruyordu ve o şerhler doğruydu -- fakat ölçüldüğü
    şart değişince sayı yerinde kaldı. Yâni sabitler, geçmiş bir ölçümün
    **mumyasıydı**: ``pencere=512`` bir kere ölçülmüştü, ``ornek=24``
    başka bir turda, ``cevrim_sayisi=8`` zabıttan; hiçbiri artık aynı
    donanımı, aynı sözlüğü, aynı bütçeyi tarif etmiyordu.

    Artık her yapısal sayının **bir formülü** var ve o formül ya
    donanımı yokluyor ya fermanın haddini okuyor ya da kefeyi ölçüyor.

    ===================================================================
    ELLE EZME HAKKI SAKLI
    ===================================================================

    Aşağıdaki türetilen alanların hepsi ``0`` (yahut ``0.0``) ile
    gelir ve ``0`` demek **"ölçekten türet"** demektir. Sıfırdan büyük
    bir sayı verilirse o kullanılır ve sebebi çağıranın sorumluluğudur.
    Bu, kodda zaten olan ``yigin_dilimi`` idiomunun bütün ayara
    yayılmış hâlidir.
    """
    ad: str = "kısa"
    # ══════════════════════════════════════════════════════════════
    #  KÖK 1 -- SÖZLÜK (veriden gelir, tayin edilmez)
    # ══════════════════════════════════════════════════════════════
    sozluk: int = 16
    # ══════════════════════════════════════════════════════════════
    #  KÖK 2 -- CÖMERTLİK (padişahın tek kabzası)
    # ══════════════════════════════════════════════════════════════
    #: ``0`` → darboğaz (en küçük koşan hâl), ``1`` → donanımın izin
    #: verdiği azamî. Aradaki her sayı, bütün ölçüleri beraberce açar.
    #: **Cömertlik burada ayarlanır ve tek yerdedir.**
    comert: float = 0.5
    # ══════════════════════════════════════════════════════════════
    #  KÖK 3 -- TOHUM
    # ══════════════════════════════════════════════════════════════
    tohum: int = 0

    # ══════════════════════════════════════════════════════════════
    #  TÜRETİLENLER -- hepsi ``0`` = "ölçekten türet"
    # ══════════════════════════════════════════════════════════════
    # ── FORMÜL 1 (YAPI): önbellekten ────────────────────────────────
    #: Veri lifi: belirtecin oturduğu qudit seviyesi. ``2^⌈log₂ sözlük⌉``.
    #: **Bu bir kübit sayısı DEĞİLDİR** -- eski adı ``veri_lifi``ydi
    #: ve o ad ikili kodlamadan kalmaydı.
    veri_lifi: int = 0
    #: Hüküm lifi: küllî alanların oturduğu seviye. ``karo²``.
    hukum_lifi: int = 0
    #: Kronecker karosu. Üç karo L1'e sığacak şekilde **ölçülür**.
    karo: int = 0
    #: Satır başına yerel hüküm yuvası (eski ``yerel_yuva``).
    yerel_yuva: int = 1
    #: **PARAMETRE GENİŞLİĞİ** -- padişahın hükmü: *"galois gibi dar bir
    #: uzay kullandığımız için mutlaka fazla sayıda parametre
    #: kullanmalısın."* Her meleke evvelce ``n_sabit`` açı sahibi
    #: oluyor, o açılar ``np.resize`` ile duraklara **devrolarak**
    #: yayılıyordu; yâni 20 durak 8 açının tekrarıydı. Genişlik, bir
    #: melekenin kendi açı dilimini kaç kat büyüteceğini söyler:
    #: devir daha geç başlar, ayrı durak ayrı parametre alır.
    #: ``0`` = ölçekten türet (``nefs/olcek.py`` Formül 2'nin bütçe
    #: payı: eniyileyici kaç yön arayabiliyorsa o kadar parametre).
    parametre_genisligi: int = 0
    #: Yazmacın yığın dilimi -- ``nefs/onbellek.py`` × cömertlik.
    yigin_dilimi: int = 0
    # ── FORMÜL 2 (BÜTÇE): ölçülen hız × süre haddi ──────────────────
    ornek_sayisi: int = 0
    pencere: int = 0
    talim_tur: int = 0
    altuzay_ornek: int = 0
    cevrim_sayisi: int = 0
    #: Muhakeme çevrimi kaç adımlıdır. **3 alt hadde sabittir ve bu
    #: keyfî değildir**: iki adımlı çevrim inşa gereği daima ``U=I``
    #: verir (ölçüldü), Berry fazı alan ister, alan da üç köşe.
    cevrim_boyu: int = 3
    degerlendirme_gorevi: int = 0
    dogrulama_sayisi: int = 0
    kademe_gorevi: int = 0
    azami_uret: int = 0
    #: Arama yarıçapı -- ``ogrenme/optimize.py``ye gider.
    yaricap: float = 0.0
    #: Blok koordinat inişi: 0 = kapalı (bütün yönler her turda).
    blok: int = 0
    #: Tâlim saat haddi. ``0`` = fermanın ``AZAMI_SANIYE``si × cömertlik.
    azami_talim_saati: float = 0.0
    # ── FORMÜL 3 (DENGE): kefeler ölçülür ───────────────────────────
    #
    # **λ'LAR ARTIK ELLE YAZILMIYOR.** Evvelce ``lam_cevrim=1.0``,
    # ``lam_monogami=0.5``, ``lam_tip=0.75``, ``lam_engel=0.6``,
    # ``lam_tenakuz=0.4``, ``lam_kategori=0.5``, ``lam_nokta=0.25``
    # yazıyordu. Yedi sayı, yedi ayrı sezgi. Halbuki bir kefenin
    # ağırlığının **tek meşru manası** şudur: mizanda hangi kefenin ne
    # kadar söz hakkı olacağı. O da ölçülür::
    #
    #     λ_i = paylaşım_i / (kefe_i'nin tâlim başındaki ölçülen değeri)
    #
    # Böylece her kefe, tâlimin **başında** ilan edilen payı kadar
    # katkı verir; büyük sayılı bir kefe küçüklerini ezmez. Paylaşımlar
    # aşağıda ve **toplamı 1'dir** -- yâni ayarlanan şey ağırlık değil,
    # **söz hakkıdır**.
    #: ``0`` = dengeden türet. Elle bir λ verilirse o kullanılır.
    lam_cevrim: float = 0.0
    lam_monogami: float = 0.0
    #: ``γ`` -- TİP MİZANI (ℒ_Hodge). Eski adı ``lam_hodge``ydi;
    #: dengede ``tip`` diye geçiyor ve iki isim iki kaynak demekti.
    lam_tip: float = 0.0
    lam_engel: float = 0.0
    lam_tenakuz: float = 0.0
    lam_kategori: float = 0.0
    lam_nokta: float = 0.0
    # ══════════════════════════════════════════════════════════════
    #  DONANIMDAN GELENLER (ferman 5-B) -- elle yazılmaz
    # ══════════════════════════════════════════════════════════════
    #: ``GF(2^galois_us)``. **8, GFNI donanım komutunun cismidir**;
    #: bir tercih değil, komutun kendisidir (``vgf2p8affineinvqb``).
    galois_us: int = 0
    #: Stabilizer tableau'nun **kübit** sayısı. **BURADA "KÜBİT" DOĞRU
    #: KELİMEDİR**: Gottesman-Knill tablosu tarifi gereği kübit üstünde
    #: kuruludur ve bu, quditin yerine geçen bir şey değil, onun ayrık
    #: denetçisidir. Sayı donanımdan gelir: bir ``uint64`` kelimesi.
    tableau_n: int = 0
    #: Ayrık faz grubu ``Z_m``. ``m = veri_lifi``: yazmaç ile faz
    #: polinomu **aynı** grupta olmalıdır, yoksa polinom başka bir fazı
    #: tarif eder (ölçüldü: yazmaç Z₁₆, polinom Z₈ iken faz ikiye
    #: bölünüyordu).
    faz_mertebesi: int = 0
    #: FLO Majorana modu ve kapı sayısı -- çevrim bütçesinden.
    flo_modu: int = 0
    flo_kapisi: int = 0
    #: Siklotomik indirgemenin cismi ve tabanı. ``us = galois_us``;
    #: taban 3 (zabıt: ``x³``), derece ölçülür (12 çıktı).
    siklotomik_us: int = 0
    siklotomik_taban: int = 3
    siklotomik_derece: int = 12
    #: Faz polinomunun beklenen azamî derecesi (CNOT-Dihedral haddi).
    faz_derecesi: int = 3
    #: TDD kanonik denetçisinin çekirdeği ve toleransı.
    tdd_cekirdek: int = 0
    tdd_tolerans: float = 1e-7
    #: Stabilizer rank mertebesi. ``0`` = kapalı.
    stab_mertebe: int = 0
    #: Klasik gölge örneği. ``0`` = KAPALI (tam ölçüm koşar).
    golge_ornegi: int = 0
    golge_haddi: float = 0.05
    #: GPU akış haddi (zabıtın **iddiası**, ölçü değil) ve genleşme.
    gpu_akis_haddi: float = 1000.0
    gpu_genlesmesi: int = 8
    # ══════════════════════════════════════════════════════════════
    #  KAPILAR -- hepsi kapatılabilir (ferman 5)
    # ══════════════════════════════════════════════════════════════
    #: **HIZ GEÇİDİ SERT Mİ?** ``1`` = had tutmazsa tâlim başlamaz.
    #:
    #: Bu anahtar bir kaçamak değil, bir **ilandır**. Evvelce tâlim
    #: ``depo/`` altındaki bir koşturucudan başlatılıyor ve o koşturucu
    #: ``gecit``i yumuşak kipe **maymuncuklayarak** geçiyordu -- yâni
    #: haddin aşıldığı tahtın dışında, görünmez bir yerde kararlaşıyordu.
    #: Ferman 1-L o koşturucuyu imha etti (yalnız taht koşar); o hâlde
    #: karar tahta taşındı ve **rapora girer**: hangi profilin haddi
    #: gözardı ettiği ve o an ölçülen hızın ne olduğu yazılır.
    hiz_geciti: int = 1
    #: Canlı kütük aralığı (saniye). ``0`` = sussun. Tâlim saatler
    #: sürebilir; padişah akışı görmeden beklemesin diye hızölçer
    #: koşarken bildirir (``tanilama/hizolcer.py``).
    canli_saniye: float = 20.0
    sadakat_acik: int = 1
    parite_lifi: int = 2
    usul_acik: int = 1
    usul_haddi: float = 0.0
    usul_seferi: int = 0
    #: **KEYFİYET TURU** (ferman 1-I): bir küme üstünde azamî kaç tur
    #: durulacak. Bu bir eşik değil **bütçedir**; eşik ``nefs/keyfiyet.py``
    #: içinde bir fonksiyondur.
    keyfiyet_turu: int = 0
    suphe_acik: int = 1
    rust_muayene: int = 1
    sbox_acik: int = 1
    # ══════════════════════════════════════════════════════════════
    #  TAŞIYICI -- ferman 7'nin tayin ettiği yol
    # ══════════════════════════════════════════════════════════════
    #: ``c`` = kapı bandı + C çekirdeği; ``numpy`` = kıyas yolu.
    hat: str = "c"
    #: Bandın azamî boyu; ``0`` = çekirdeğin kendi ölçüsü.
    hat_bandi: int = 0
    #: ``galois`` = GF(2⁸) + stabilizer tableau. Ferman 7.
    motor: str = "galois"
    #: ``complex64`` bellek trafiğini yarıya indirir (zabıt 2, 4. usul).
    genlik_tipi: str = "complex64"
    # ══════════════════════════════════════════════════════════════
    #  ZAMAN SABİTLERİ -- sönüm ve geçiş; boyutsuz, ölçekten bağımsız
    # ══════════════════════════════════════════════════════════════
    #
    # Bunlar donanıma da sözlüğe de bağlı değildir: hepsi **boyutsuz
    # nispetlerdir** (tur nispetiyle geçiş ortası, sönüm hızı, eşik).
    # Türetecek bir formülleri yoktur ve olduğu gibi durmaları doğrudur;
    # fakat hepsi **kapatılabilir** ve raporda görünür.
    rust_t0: float = 0.5
    rust_tau: float = 0.15
    rust_kapanis: float = 0.5
    hafiza_kapasitesi: int = 0
    hafiza_yazma: float = 0.05
    hafiza_sonumu: float = 0.02
    suphe_sonumu: float = 0.05
    zeno_esigi: float = 0.35
    zeno_tepe: float = 0.9
    hafiza_ayniyet: float = 0.98
    hafiza_buhar: float = 1e-4
    tenakuz_eps: float = 1e-5
    dislama_tau: float = 8.0
    ayna_teta: float = 0.2617993877991494        # π/12
    ayna_r: float = 0.35
    ayna_tur: int = 0
    qudit_qsvt: int = 0
    qudit_derece: int = 0
    qudit_yon: int = 0
    #: Kademe kademe yerel üniter harmanı (eski ``harman_kademesi``).
    harman_kademesi: int = 0

    def __post_init__(self) -> None:
        """**SIFIR OLAN HER ALAN ÖLÇEKTEN DOLDURULUR.**

        Elle verilen (sıfırdan büyük) hiçbir alana dokunulmaz: ezme
        hakkı saklıdır ve hangi alanın elle verildiği ``elle`` kümesinde
        durur -- rapor onu yazar, yâni "bu sayı türetilmedi" gizlenmez.
        """
        o = olcek(Kok(sozluk=int(self.sozluk), comert=float(self.comert),
                      tohum=int(self.tohum)))
        self.olcek_dokumu = o
        self.elle = tuple(sorted(
            k for k in o if getattr(self, k, None) not in (0, 0.0, None)))
        for k, v in o.items():
            if getattr(self, k, None) in (0, 0.0):
                setattr(self, k, v)

    #: ``__post_init__``in doldurduğu döküm -- rapor buradan okur.
    olcek_dokumu: Dict[str, object] = field(default_factory=dict)
    elle: Tuple[str, ...] = ()

    @property
    def lif_yapisi(self) -> Tuple[int, ...]:
        """``(veri_lifi, karo, karo)`` -- ``d = ∏``. Ayrı alan DEĞİL.

        Evvelce hem ``lif_yapisi`` hem ``veri_lifi`` hem
        ``hukum_lifi`` ayrı ayrı yazılıydı ve birbirini tutup tutmadığı
        hiçbir yerde denetlenmiyordu. Artık tek kaynak var: yapı
        formülü. Tutarsızlık **imkânsız**.
        """
        return (int(self.veri_lifi), int(self.karo), int(self.karo))

    @property
    def d(self) -> int:
        """Quditin boyu: ``veri_lifi × karo × karo``."""
        return int(self.veri_lifi) * int(self.karo) ** 2

    def qayar(self):
        from nefs.zihin_durumu import QAyar
        import numpy as _np
        tip = {"complex64": _np.complex64,
               "complex128": _np.complex128}[str(self.genlik_tipi)]
        return QAyar(veri_lifi=int(self.veri_lifi),
                     yerel_yuva=int(self.yerel_yuva),
                     harman_kademesi=int(self.harman_kademesi),
                     tohum=int(self.tohum),
                     yigin=self.yigin(), tip=tip,
                     motor=str(self.motor),
                     hukum_lifi=int(self.hukum_lifi),
                     lif_yapisi=self.lif_yapisi,
                     faz_mertebesi=int(self.faz_mertebesi),
                     hat=str(self.hat), hat_bandi=int(self.hat_bandi),
                     sadakat_acik=int(self.sadakat_acik),
                     parite_lifi=int(self.parite_lifi),
                     parametre_genisligi=int(self.parametre_genisligi))

    def yigin(self) -> int:
        """Yazmacın yığın dilimi -- veriden büyük olamaz."""
        return max(1, min(int(self.yigin_dilimi), int(self.ornek_sayisi)))


# =====================================================================
#  ÜÇ PROFİL = TEK KABZANIN ÜÇ DEĞERİ
# =====================================================================
#
# Evvelce üç profil, üç ayrı sabit yığınıydı: ``KISA_CPU`` on bir sayı
# veriyordu, ``ORTA`` dokuz, ``AZAMI_KAGGLE`` on dört. Otuz dört sayı,
# üç ayrı sezgi -- ve ikisi **kırıktı** (``veri_lifi=6`` ve ``12``
# yazıyordu; ``sozluk=16`` oraya sığmaz, çağrılsalardı düşerlerdi).
#
# Artık üçü de aynı formülün üç noktasıdır. Değişen tek şey
# **cömertliktir**; gerisini donanım, ferman ve ölçü tayin eder.

#: **DAR** -- en küçük koşan hâl. Ölçüm ve teşhis içindir.
#:
#: **HIZ GEÇİDİ BU PROFİLDE YUMUŞAKTIR VE SEBEBİ YAZILIDIR.** Had
#: ``tanilama/hiz_teftisi.py:HAD`` = 1 000 000 belirteç/sn'dir; bu
#: makinede ölçülen ~90 000'dir, yâni on bir kat eksiktir. Padişahın
#: bu husustaki emri sarihtir: *"Hız hedefinin zaten gerisindeyiz ama
#: bari eğitim yapmışken konuşabilen bir model elde ettiğimizi
#: görelim."* O hâlde teşhis profili koşar, **fakat ölçülen hız
#: raporda aynen yazılır ve kırmızı yanar**. ``ORTA`` ve ``AZAMÎ``de
#: geçit **serttir**: umumi tâlim hız garantisi olmadan başlamaz.
DAR = EgitimAyari(ad="dar", comert=0.15, hiz_geciti=0)

#: **ORTA** -- bu makinenin dengeli hâli. Varsayılan.
ORTA = EgitimAyari(ad="orta", comert=0.5)

#: **AZAMÎ** -- donanımın izin verdiği tavan. Padişahın "mümkün
#: olduğunca cömert ol" hükmünün karşılığı budur: ``comert = 1``
#: demek "elinden geleni ardına koyma" demektir ve **hududu artık
#: benim sezgim değil, ölçülen önbellek ve ilan edilen süre haddidir.**
AZAMI = EgitimAyari(ad="azamî", comert=1.0)

#: Eski adlar -- çağrı yerleri kırılmasın diye aynı nesneyi işaret
#: eder. ``KISA_CPU`` artık ``DAR``dır; ``AZAMI_KAGGLE`` ``AZAMI``.
KISA_CPU = DAR
AZAMI_KAGGLE = AZAMI

#: Ayar adından profile -- komut satırı için.
PROFILLER: Dict[str, EgitimAyari] = {
    "dar": DAR, "kısa": DAR, "kisa": DAR, "orta": ORTA,
    "azamî": AZAMI, "azami": AZAMI}


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
#  SÜREÇ HAVUZU İMHA EDİLDİ -- ÖLÇÜLDÜ, ÜÇ YERDEN KIRIKTI
# =====================================================================
#
# Burada ``_ISCI``, ``_isci_kur`` ve ``_isci_kayip`` duruyordu ve
# ``kulli_kayip_talimi`` bir ``multiprocessing`` havuzu kuruyordu.
# **Hiçbir profilde koşmamıştı**: ``surec`` varsayılan ``0``, kod ise
# ``ayar.surec or 1`` diyordu, o hâlde daima ``1`` çıkıyor ve havuz hiç
# kurulmuyordu. Ölü kod, kırıklığını da saklıyordu.
#
# ÖLÇÜLDÜ (sahte kayıpla, KISA_CPU profili):
#
#     kayip_p çağrısı  : 16
#     yığın dağılımı   : 12 çağrı × 1 satır, 3 çağrı × 3, 1 çağrı × 9
#     toplam satır     : 30
#
# Yâni çağrıların **dörtte üçü tek satırlıktır** ve paralelleşemez;
# 4 çekirdekle en iyi hâlde 30 satır 18 satırlık zamana iner (~1,67×).
# Bedeli ise üç kırıktır ve üçü de sessizdi:
#
#   1. **İŞÇİ BAŞKA BİR KAYIP HESAPLIYORDU.** ``_isci_kayip``
#      ``hafiza=_ISCI.get("hafıza")`` diyordu ve o daima ``None``dı
#      (``_ISCI["hafıza"] = None`` yazılıydı). Hafıza kayba giriyor
#      (rüşt, tevakkuf, Zeno); o hâlde paralel yol ile seri yol **aynı
#      parametrede farklı sayı** veriyordu. İki yol yan yana durdukça
#      hangisinin koştuğu belirsizdir (ferman 1-E).
#   2. **İŞÇİ KADEME PARAMETRELERİNİ AÇMIYORDU.** Ana yol
#      ``kademe_parametreleri_ac`` ile 318'i 324'e çıkarıyor, işçi
#      açmıyordu: ``nefs.yukle(p)`` boy uyuşmazlığıyla düşerdi.
#   3. **7/24 SAYAÇLARI FORK'U GEÇMEZ.** ``sadakat``/``şüphe``/``usul``
#      sayaçları çocuk süreçte artar, ebeveyne dönmez; tahtın
#      "bu uzuv hiç koşmadı" ``assert``i paralel kipte **yanlışlıkla**
#      ateşlerdi.
#
# Üçüncüsü tamir edilebilir, ikincisi de; fakat birincisi tabiatı gereği
# tamir edilemez: hafıza sıralı ve hâllidir, parçalanamaz. O hâlde
# kökünden kesildi (ferman 2-B) ve ``surec`` ayarı da beraberinde.


def mizan_ayari(a: EgitimAyari) -> "MizanAyari":
    """Tâlim ayarından mizan ayarı -- **tek kaynak**, iki nüsha değil."""
    return MizanAyari(
        zeno_tepe=float(a.zeno_tepe), lam_engel=float(a.lam_engel),
        ayna_tur=int(a.ayna_tur), ayna_teta=float(a.ayna_teta),
        ayna_r=float(a.ayna_r),
        lam_cevrim=float(a.lam_cevrim), lam_monogami=float(a.lam_monogami),
        lam_tip=float(a.lam_tip), cevrim_boyu=int(a.cevrim_boyu),
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
                       gorevler: Optional[Sequence] = None) -> Dict[str, object]:
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
    kapi = gecit(sert=bool(int(ayar.hiz_geciti)), hiz_ayari=ayar)
    hepsi = list(gorevler) if gorevler is not None else \
        gorevleri_getir("training")
    # **İMTİHAN BÖLÜMLEMESİ** -- ezberi ve sızıntıyı engeller.
    egitim_gorevleri, dogrulama = gorevleri_getir(ne="böl", gorevler=
        hepsi, dogrulama=int(ayar.dogrulama_sayisi), tohum=ayar.tohum)
    # ── VERİ: ARC + KÜLLİYAT ──────────────────────────────────────
    # **Tek motor tek veriyle beslenmez.** ARC muhakemeyi, külliyat
    # lisanı öğretir; ikisi aynı belirteç uzayında aynı mizana girer.
    # Pay **formüldür, sabit değil**: ARC elinden geleni verir (azamî
    # yarısı), kalanı külliyat doldurur. Külliyat tükenmez, ARC tükenir.
    arc_veri = ornekler(egitim_gorevleri,
                        azami=max(1, int(ayar.ornek_sayisi) // 2),
                        pencere=ayar.pencere, sozluk=ayar.sozluk,
                        tohum=ayar.tohum)
    # **KÜLLİYAT EVVELÂ ÇEKİLİR.** Evvelce ``kulliyat_cek`` yalnız
    # ``kulliyat_beyani``nin içinden, yâni **rapor vaktinde** koşuyordu:
    # tâlim, henüz inmemiş bir külliyattan veri okumaya çalışıyor ve
    # sessizce boş dönüyordu. Çekme, okumadan **evvel** olmalıdır.
    kul_dokum = kulliyat_cek()
    kul_veri = kulliyat_verisi(
        sozluk=int(ayar.sozluk), pencere=int(ayar.pencere),
        azami=max(0, int(ayar.ornek_sayisi) - len(arc_veri)),
        tohum=int(ayar.tohum))
    veri = list(arc_veri) + list(kul_veri)
    assert veri, "tâlim verisi BOŞ"

    nefs = QNefs(ayar.tohum, ayar.qayar())
    nefs.idrak_et(np.zeros((2, ayar.veri_lifi)))
    # Kademe parametreleri ``d`` sabitlenmeden EVVEL açılmalıdır; boyut
    # ortada değişirse tâlim kendi öğrendiğini siler (H39).
    kademe_parametresi = kademe_parametreleri_ac(nefs.p)
    d = len(nefs)
    p0 = nefs.vektor()
    kademe_gorevleri = list(egitim_gorevleri)[:int(ayar.kademe_gorevi)]

    # **HATA FONKSİYONU MÎZÂN-I KÜLLÎ'DİR** (nefs/kulli_mizan.py).
    # Tabakalı mizan + mizanın kendi kefeleri; hiçbiri veriye kör
    # teslimiyet değildir:
    #   Nokta     -- kısmî Born, **son basamak**, küçük ağırlıkla
    #   Uzay      -- Uhlmann sadakati (kör NLL DEĞİL)
    #   Kategori  -- funktör kompozisyonu; etiketsiz, kendini denetler
    #   Tip       -- Δ|Ψ⟩ = 0; harmonik hüküm
    #   Çevrim    -- Wilson holonomisi; manayı bilmeden tenakuz bulur
    #   Tenakuz   -- log-bariyer × eş-zamanlı dışlama
    #   Gedik     -- kapanmayan seferin epistemik borcu
    #   Monogami  -- CKW eşitsizliği; sahte illetleri budar
    #   Engel     -- CIM; taban durumuna oturamayan gerilim
    mzn = mizan_ayari(ayar)
    # ══════════════════════════════════════════════════════════════
    #  FORMÜL 3 -- DENGE: λ'LAR BURADA **ÖLÇÜLÜR**
    # ══════════════════════════════════════════════════════════════
    #
    # Yedi ``λ`` elle yazılıydı; yedi ayrı sezgi. Artık tâlimin
    # **başında** mizan bir kere dökülür ve her kefeye ilan edilen
    # payı kadar söz hakkı verecek ağırlık hesaplanır
    # (``nefs/olcek.py:denge``). Büyük sayılı bir kefe küçüklerini
    # ezmez; ayarlanan şey katsayı değil, **paydır**.
    #
    # Bu bir ölçüm çağrısıdır ve bedeli bir kayıp çağrısıdır -- yâni
    # ilan edilen bütçeden düşer, gizli değildir.
    #
    # ══════════════════════════════════════════════════════════════
    #  DENGE **HER TURDA** YENİDEN ÖLÇÜLÜR -- ÖLÇÜLMÜŞ SEBEBİYLE
    # ══════════════════════════════════════════════════════════════
    #
    # Evvelce ``denge`` yalnız **bir kere**, ``p₀``da çağrılıyordu ve
    # λ'lar koşu boyunca donuyordu. Ölçüldü ve kusur buydu: kefelerin
    # büyüklük mertebesi eniyileme ilerledikçe değişir (meselâ çevrim
    # kefesi düşerken tenakuz kefesi yükselir); λ donunca ilan edilen
    # **söz hakkı** bozulur ve bir kefe ötekileri ezmeye başlar.
    # Netice ölçülmüştü: küme küme eniyileme her kümeyi mahallî olarak
    # iyileştirirken küllî kayıp ``0,160367 → 0,342040`` **yükseliyordu**.
    #
    # Artık denge bir **çağrıdır**, bir sabit değil: münasebet döngüsü
    # her turun başında bunu çağırır, kefeler o anki hâlleriyle ölçülür
    # ve pay yeniden dağıtılır. Elle verilmiş λ'lara hiç dokunulmaz --
    # hangilerinin elle verildiği **ilk kalibrasyondan evvel** tesbit
    # edilir, yoksa ilk atamadan sonra hepsi "elle verilmiş" görünürdü.
    LAM_ADLARI = ("lam_cevrim", "lam_monogami", "lam_tip", "lam_engel",
                  "lam_tenakuz", "lam_kategori", "lam_nokta")
    _elle_lam = tuple(a for a in LAM_ADLARI
                      if float(getattr(ayar, a, 0.0)) != 0.0)
    #: Mizan ayarının **tek nüshası**; denge onu yerinde yeniler.
    _mzn = {"a": mzn}

    def _dengele(dokum) -> Dict[str, float]:
        """Kefeleri ölç, payı yeniden dağıt, mizan ayarını **yenile**."""
        lam = denge(dokum)
        for ad, deger in lam.items():
            if ad == "frenlenen" or ad in _elle_lam:
                continue
            setattr(ayar, ad, float(deger))
        _mzn["a"] = mizan_ayari(ayar)
        return lam

    ilk_kefeler = kulli_mizan(nefs, veri, p0, ayar.sozluk, ayar=mzn,
                              kademe_gorevleri=kademe_gorevleri,
                              ne="döküm")
    olculen_lam = _dengele(ilk_kefeler)
    mzn = _mzn["a"]
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
    # **HAD BAĞLANDI.** Evvelce ``had=None`` geçiyordu ve rapor "had
    # konmadı (ölçü yalnız görülüyor)" diyordu -- yâni ana hattaki
    # hızölçer **hiç kırmızı yanamıyordu**. Halbuki had ortadadır ve
    # ``gecit()`` onu koşudan evvel zaten uyguluyor; koşarken de aynı
    # haddin uygulanmaması, ölçüyü seyirlik yapmaktı (ferman 5).
    from tanilama.hiz_teftisi import HAD as _HIZ_HADDI
    olcer = Hizolcer(belirtec_basina=len(veri) * int(ayar.pencere),
                     had=float(_HIZ_HADDI), ad="küllî mizan",
                     canli_saniye=float(ayar.canli_saniye))
    hizolcer_bagla(olcer)

    #: Münasebet döngüsünün o an üstünde durduğu küme. Kayıp **bütün
    #: veriye değil, bu kümeye** bakar; ferman 1-I'in ta kendisi.
    _kume: Dict[str, Sequence] = {"v": list(veri)}
    _seyir: List[Dict[str, float]] = []

    def kayip_p(P: np.ndarray) -> np.ndarray:
        P = np.atleast_2d(np.asarray(P, float))
        out = np.empty(P.shape[0], float)
        kume = list(_kume["v"])
        for i, p in enumerate(P):
            _sayac["çağrı"] += 1
            with olcer.saat(len(kume) * int(ayar.pencere)):
                t = kulli_mizan(nefs, kume, p, ayar.sozluk, ayar=_mzn["a"],
                                hafiza=hafiza, adim=_sayac["çağrı"],
                                kademe_gorevleri=kademe_gorevleri)
            out[i] = float(t["kayıp"])
            _seyir.append({"V": float(t["kayıp"])})
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
        # **GCL nokta sayısı da ölçekten**: yön sayısı kadar nokta.
        gcl_nokta_sayisi=max(8, int(ayar.altuzay_ornek)),
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
    # ══════════════════════════════════════════════════════════════
    #  FERMAN 1-I -- BİR VERİ, HUDUDU TEMİZLENENE KADAR
    # ══════════════════════════════════════════════════════════════
    #
    # Evvelce burada tek satır vardı: ``hoca_egit(kayip_p, p0, opt)``.
    # Bütün veri tek kayba toplanıyor, eniyileyici o **ortalamayı**
    # düşürüyordu. Ölçüldü ve sebebi buydu: 30 kayıp çağrısında eğim
    # yalnız ``−0,32``. Düşen şey ortalamaydı; bir örneğin tenakuzu
    # öteki 511'in içinde kayboluyordu.
    #
    # Artık örnekler **küme küme** alınır ve her küme kendi hududu
    # (tenakuz · kısırdöngü · mantıksızlık) temizlenene kadar üstünde
    # durulur. Küme boyu uydurulmaz: **yazmacın yığınıdır** -- bir küme
    # tam bir yazmaç geçişidir, ne eksik ne fazla.
    def _eniyile(p_, kume):
        """Bir küme üstünde kısa bir eniyileme turu."""
        o = OptimizeAyari(
            ad=ayar.ad, tur=1, yaricap=float(ayar.yaricap),
            gcl_nokta_sayisi=max(8, int(ayar.altuzay_ornek)),
            yon_sayisi=int(ayar.altuzay_ornek), blok=int(ayar.blok),
            sesli=False, tohum=ayar.tohum)
        o.tunel_acik = True
        o.vekil_acik = False
        o.bütçe_denetimi = False
        n0 = _sayac["çağrı"]
        _kume["v"] = list(kume)
        rr = hoca_egit(kayip_p, np.asarray(p_, float), o)
        return np.asarray(rr["p"], float), _sayac["çağrı"] - n0

    def _olc(p_, kume):
        """O kümenin mizan dökümü -- keyfiyet buradan okunur."""
        return kulli_mizan(nefs, list(kume), np.asarray(p_, float),
                           ayar.sozluk, ayar=_mzn["a"], hafiza=hafiza,
                           adim=_sayac["çağrı"],
                           kademe_gorevleri=kademe_gorevleri, ne="döküm")

    mun = munasebet_kos(
        veri, p0, _eniyile, _olc,
        # **DENGE HER TURDA** (yukarıdaki ``_dengele``): münasebet
        # döngüsü her turun başında kefeleri ölçer ve payı yeniden
        # dağıtır. ``None`` verilirse λ'lar donar ve eski hâl geri
        # gelir -- yâni bu anahtar da kapatılabilir ve kırmızı yanar.
        dengele=_dengele,
        # **KÜME BOYU BÜTÇEDEN ÇIKAR, UYDURULMAZ.** Bir küme, hududu
        # temizlenebilecek kadar küçük olmalı; fakat kaç küme olacağını
        # bütçe tayin eder: her küme azamî ``keyfiyet_turu`` tur alır,
        # elde ``çağrı`` kadar tur var, o hâlde::
        #
        #     küme sayısı ≈ çağrı / keyfiyet_turu
        #     obek        = len(veri) · keyfiyet_turu / çağrı
        #
        # Ve obek yazmacın yığınını aşamaz (bir küme bir geçiştir).
        # Ölçüldü: bu kural konmadan önce ``obek = yığın = 1024`` çıktı
        # ve bütün veri **tek küme** oldu -- yâni münasebet döngüsü eski
        # usule geri dönmüştü, ferman 1-I fiilen koşmuyordu.
        ayar=MunasebetAyari(
            acik=1,
            # Küme boyu = yığın. Ölçekte tek sayı olarak türetildi.
            obek=int(ayar.yigin()),
                            azami_tur=int(ayar.keyfiyet_turu),
                            n_v=int(ayar.veri_lifi)),
        keyfiyet_ayari=KeyfiyetAyari(acik=1,
                                     azami_tur=int(ayar.keyfiyet_turu)))
    _kume["v"] = list(veri)
    p_son = np.asarray(mun["p"], float)
    # ── V_İLK İLE V_SON **AYNI MİZANDA** ÖLÇÜLÜR ──────────────────
    # λ artık her turda yenilendiği için tâlim başındaki mizan ile
    # sonundaki mizan **aynı fonksiyon değildir**. İkisini kıyaslamak
    # iki ayrı cetvelle ölçüp "kısaldı" demek olurdu. O hâlde ``p₀``
    # son λ ile **yeniden ölçülür**: bedeli bir kayıp çağrısıdır ve
    # ilan edilmiştir.
    _ilk = kulli_mizan(nefs, veri, p0, ayar.sozluk, ayar=_mzn["a"],
                       hafiza=hafiza, adim=_sayac["çağrı"],
                       kademe_gorevleri=kademe_gorevleri)
    _son = kulli_mizan(nefs, veri, p_son, ayar.sozluk, ayar=_mzn["a"],
                       hafiza=hafiza, adim=_sayac["çağrı"],
                       kademe_gorevleri=kademe_gorevleri)
    mzn = _mzn["a"]
    r = {"p": p_son, "V_ilk": float(_ilk["kayıp"]),
         "V_son": float(_son["kayıp"]),
         "kayıp_çağrısı": int(_sayac["çağrı"]), "seyir": _seyir,
         "günlük": [], "düşen_uzuv": {}}

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
    q_son = nefs.idrak_et(np.zeros((ayar.yigin(), 2, ayar.veri_lifi)))
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
    #
    # **"0 = KAPALI" ARTIK HAKİKATEN KAPALI.** Evvelce burada
    # ``max(32, int(ayar.golge_ornegi) or 128)`` yazıyordu: ``0``
    # verilince ``or`` onu 128'e çeviriyordu, yâni anahtar kapanmıyordu.
    # Kapanmayan bir anahtar, ölçünün kırmızı yanamaması demektir
    # (ferman 5). Şimdi ``0`` verilince gölge hiç alınmaz ve rapor
    # "KAPALI" der; tam ölçüm zaten aşağıda koşuyor ve kıyas kalır.
    goz = [q_son.y.sektor(ad) for ad, _ in q_son.ayar.kulli_alanlar]
    K = int(ayar.golge_ornegi)
    t_g = time.perf_counter()
    if K > 0:
        golge_ham = golge_al(psi_son, GolgeAyari(
            ornek=K, had=float(ayar.golge_haddi), tohum=int(ayar.tohum)))
        golge = kestir(golge_ham, goz, tahkik=True)
        golge["açık"] = True
    else:
        golge = {"kestirim": np.zeros(len(goz)), "gözlenebilir": len(goz),
                 "örnek": 0, "açık": False}
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
    # **PALMER İDDİASI SINANIR.** Rapor her koşuda "transandantal faz
    # YOK" yazıyordu; o iddia burada, durumun kendi boyunda ölçülür.
    palmer = palmer_olcu(n=int(psi_son.size), tohum=int(ayar.tohum))
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
    #
    # **ASIL DURUMUN ÜSTÜNDE, VEKİLİN DEĞİL.** Evvelce buraya ``tab``
    # (Tableau) veriliyordu; o ise ``tableau_n = 64`` elemanlık bir
    # nicelenmiş vekildir. 4096 genlikli durumun paritesini 64 baytlık
    # bir özetten yoklamak, ölçüyü ölçtüğü şeyden koparmaktı. Yoklama
    # ``psi_son``un kendisi üstünde yapılır.
    son_sadakat = sadakat_uygula(psi_son.copy(), SadakatAyari(
        acik=int(ayar.sadakat_acik), parite_lifi=int(ayar.parite_lifi),
        lif_yapisi=tuple(ayar.lif_yapisi)))

    # ══════════════════════════════════════════════════════════════
    #  FERMAN 1-H -- TÂLİM DE KONUŞUR (tek motor)
    # ══════════════════════════════════════════════════════════════
    #
    # *"Hazine + hafıza yükle → söyle sadece çıkarımda olamaz. Eğitimde
    # de mutlaka olacaktır ki doğru konuşup konuşmadığı tespit
    # edilebilsin, konuşacak bir hafızası oluşsun."*
    #
    # Hazine **evvela yazılır** (aşağıda), sonra buradan **geri
    # yüklenir** ve motor konuşturulur. Geri yükleme şart: yazılan ile
    # yüklenen aynı değilse "aynı ağırlıkla konuştu" demek yalan olur.
    # İki kapı arasındaki tek fark, burada eniyilemenin bitmiş
    # olmasıdır -- motor aynı motordur.
    nefs.yukle(p_yildiz)
    _konusma = [padisah(g, nefs=nefs, ayar=ayar, hafiza=hafiza)
                for g in list(dogrulama)[:int(ayar.kademe_gorevi)]]
    konusma = {
        "görev": len(_konusma),
        "konuşan": sum(1 for c in _konusma if not c["sükût"]),
        "susan": sum(1 for c in _konusma if c["sükût"]),
        "budanan": sum(int(c.get("budanan", 0)) for c in _konusma),
        "sebep": [c["sebep"] for c in _konusma if c["sükût"]][:3],
        "belirteç": [list(c["belirteç"] or [])[:12] for c in _konusma][:2],
        "güven": (float(np.mean([c["güven"] for c in _konusma]))
                  if _konusma else 0.0)}

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
         "V_son": float(r["V_son"]), "veri_lifi": int(ayar.veri_lifi),
         "sözlük": int(ayar.sozluk), "pencere": int(ayar.pencere),
         "yerel_yuva": int(ayar.yerel_yuva), "karo": int(ayar.karo),
         "hüküm_lifi": int(ayar.hukum_lifi), "d": int(ayar.d),
         "cömert": float(ayar.comert),
         "harman_kademesi": int(ayar.harman_kademesi),
         "tohum": int(ayar.tohum),
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
            "palmer": palmer,
            "faz_polinomu": fazp, "gpu_akışı": akis, "siklotomik": sik,
            "sadakat": sad, "son_sadakat": son_sadakat,
            "konuşma": konusma, "münasebet": munasebet_beyani(),
            "keyfiyet": keyfiyet_beyani(),
            "külliyat": {"arc": len(arc_veri), "külliyat": len(kul_veri),
                         "döküm": kul_dokum},
            "ölçek": ayar.olcek_dokumu, "elle_verilen": ayar.elle,
            "denge": olculen_lam, "ilk_kefeler": ilk_kefeler,
            "usul": usl, "şüphe": sup,
            # Hızölçer koşunun **tamamını** gördü; geçitteki tek
            # yoklama değil, her kayıp çağrısı.
            "hızölçer": hizolcer_beyani(),
            "çekirdek": cekirdek_beyani(),
            "mizan": kefeler, "veri_cetveli": cetvel,
            "hafıza": hafiza.beyan(), "rüşt": float(kefeler["α_rüşt"]),
            "veri": len(veri),
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

    * ``"tâlim"``  -- ``kos``: **tek hat**. (Evvelce "iki hattın tek
      hatta terkibi" yazıyordu; ikinci hat -- meclis -- imha edildi ve
      şerhi düzeltmemek olmayan bir hattı işaret etmek olurdu.)
    * ``"sabit"``  -- ``tanilama/sabit_teftisi.py``: elle tayin edilmiş
      bütün sabitlerin listesi. Hangisi ayara bağlı, hangisi koda gömülü,
      hangisi hiç okunmuyor -- ``ast`` ile çıkarılır.
    * ``"mizan"``  -- ``nefs/kulli_mizan.py``: hata fonksiyonunun kendisi.
      Bütün kefeler (Nokta, Uzay≡Rezonans, Kategori, Tip≡Hodge,
      Çevrim, Tenakuz, Monogami, Engel) ayrı ayrı ölçülür ve verinin
      etiketsiz dört kampa ayrılması gösterilir. **Kök budur.**
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
