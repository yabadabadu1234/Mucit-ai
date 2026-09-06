"""
ÖLÇEK -- BÜTÜN YAPISAL SAYILARIN TEK KAYNAĞI

===================================================================
PADİŞAHIN HÜKMÜ
===================================================================

    "Bulacağın bütün sabit ayarları tek veya çok az formüle en optimize
    şekilde bağla, mümkün olduğunca cömert ol."

``main/egitim.py``de altmışa yakın elle yazılmış sayı vardı. Her birinin
yanında bir ölçüm şerhi duruyordu ve o şerhler **doğruydu** -- fakat
ölçüldüğü şart değişince sayı yerinde kaldı. Sabitler, geçmiş bir
ölçümün mumyasıydı: ``pencere=512`` bir turda ölçülmüştü, ``ornek=24``
başkasında, ``cevrim_sayisi=8`` zabıttan gelmişti; hiçbiri artık aynı
donanımı, aynı sözlüğü, aynı bütçeyi tarif etmiyordu.

===================================================================
ÜÇ KÖK
===================================================================

    KÖK 1  sozluk   Veriden gelir. Tayin edilmez, sayılır.
    KÖK 2  comert   Padişahın **tek kabzası**. 0 → darboğaz,
                    1 → donanımın izin verdiği azamî.
    KÖK 3  donanım  ``nefs/donanim.py`` fiilen yoklar (ferman 5-B).

===================================================================
ÜÇ FORMÜL
===================================================================

**FORMÜL 1 -- YAPI (önbellekten).**

Zabıtın hükmü: durum L1'de dönmeli, ``4096×4096`` GEMM olmamalı. O
hâlde lif yapısı bir tercih değil, bir **önbellek denklemidir**::

    V = 2^⌈log₂ sözlük⌉                     (veri lifi; ikinin kuvveti
                                             şart -- parite maskesi bir
                                             bit aralığıdır)
    3·K²·bayt ≤ L1d · doluluk               (üç karo L1'e sığsın)
    K = 2^⌊½ log₂(L1d·doluluk / (3·bayt))⌋
    lif = (V, K, K)   ,   hüküm lifi = K²   ,   d = V·K²

``doluluk`` cömertlikle açılır (0,25 → 0,90): cömert olmak, önbelleğin
daha çoğunu istemektir; hududu koyan yine ölçülen L1'dir.

Yığın da aynı cinstendir, yalnız bir mertebe yukarıda: durum şeridi
``(B, d)`` **L3**'e sığmalıdır::

    B = clamp( L3 · doluluk / (d · bayt) , 1 , örnek )

**FORMÜL 2 -- BÜTÇE (ölçülen hız × ilan edilen süre).**

Fermanın haddi bellidir: tâlim toplamda ``AZAMI_SANIYE``yi aşmayacak.
Bir tâlim koşusunun işlediği belirteç sayısı ise şudur::

    toplam_belirteç = çağrı × örnek × pencere
    çağrı           = talim_tur × altuzay_ornek

O hâlde bütçe **tek denklemdir**::

    çağrı × örnek × pencere  =  ölçülen_hız × AZAMI_SANIYE × comert

``ölçülen_hız`` uydurulmaz: bu modülde bir **mikro yoklama** ile
ölçülür (küçük bir yazmaçta kapı vurup saniyede kaç belirteç işlendiğine
bakılır) ve önbelleklenir. Haddin kendisini (1 000 000 belirteç/sn)
kullanmak yanlış olurdu: makinenin koşamayacağı bir plan yazmak, tam da
fermanın yasakladığı şeydir.

Bütçenin dağıtımı da ilan edilir ve gizli değildir::

    çağrı   = (1 + ⌊8·comert⌉) × (8 + ⌊56·comert⌉)
    kalan   = bütçe / çağrı
    örnek = pencere = 2^⌊½ log₂ kalan⌋      (log'da eşit bölüşüm)

Sonra ``örnek`` yığına, ``pencere`` de sözlüğe göre yuvarlanır.

**FORMÜL 3 -- DENGE (kefeler ölçülür).**

Yedi ``λ`` vardı ve yedisi de elle yazılmıştı. Bir kefe ağırlığının tek
meşru manası, o kefenin mizanda ne kadar **söz hakkı** olacağıdır::

    λ_i = pay_i / (kefe_i'nin tâlim başındaki ölçülen değeri + ε)

Paylar toplamı 1'dir. Böylece büyük sayılı bir kefe küçüklerini ezmez
ve ayarlanan şey bir katsayı değil, **söz hakkıdır**. Ölçüm
``denge()``de yapılır ve mizanın ilk çağrısından okunur.

===================================================================
NE TÜRETİLMEZ VE NİÇİN
===================================================================

Boyutsuz nispetler türetilmez ve türetilmemelidir: ``rust_t0`` (geçişin
ortası, tur nispetiyle), ``rust_tau``, sönüm hızları, eşikler. Bunların
donanımla da sözlükle de alâkası yoktur; bir formüle bağlamak, olmayan
bir bağı uydurmak olurdu.

``cevrim_boyu = 3`` de türetilmez: iki adımlı çevrim inşa gereği daima
``U = I`` verir (ölçüldü) ve Berry fazı alan ister, alan da üç köşe.
Bu bir ayar değil, bir **teoremdir**.
"""
from __future__ import annotations

import math
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Sequence, Tuple

import numpy as np

__all__ = ["Kok", "olcek", "denge", "olcek_beyani", "hiz_yoklamasi"]


@dataclass(frozen=True)
class Kok:
    """Üç kök. Ölçeğin tamamı bunlardan çıkar."""

    #: Veriden gelir; tayin edilmez.
    sozluk: int = 16
    #: Padişahın tek kabzası: 0 = darboğaz, 1 = donanımın azamîsi.
    comert: float = 0.5
    tohum: int = 0

    def __post_init__(self) -> None:
        assert int(self.sozluk) >= 2, "sözlük en az iki belirteç olmalı"
        assert 0.0 <= float(self.comert) <= 1.0, (
            "cömertlik [0,1] aralığında olmalı; verilen %r" % (self.comert,))


#: Mikro yoklamanın önbelleği. Yoklama bir kere koşar; her ayar
#: kurulduğunda tekrar koşsaydı ``EgitimAyari()`` pahalı olurdu.
_HIZ: Dict[Tuple[int, int], float] = {}


def _ikinin_kuvveti(x: float, en_az: int = 1) -> int:
    """``2^⌊log₂ x⌋`` -- aşağı yuvarlayarak ikinin kuvveti."""
    v = max(float(x), 1.0)
    return int(max(en_az, 1 << int(math.floor(math.log2(v)))))


def _yukari_kuvvet(x: int) -> int:
    """``2^⌈log₂ x⌉`` -- yukarı yuvarlayarak ikinin kuvveti."""
    v = max(int(x), 1)
    return int(1 << int(math.ceil(math.log2(v))))


def hiz_yoklamasi(d: int, bayt: int = 8, tohum: int = 0) -> float:
    """**MİKRO YOKLAMA** -- bu makine saniyede kaç belirteç işliyor?

    Bütçe formülünün paydası budur ve **uydurulmaz**. Haddin kendisini
    (1 000 000 belirteç/sn) kullanmak yanlış olurdu: makinenin
    koşamayacağı bir plan yazmak, fermanın yasakladığı şeydir.

    Yoklama, ana akışın fiilen yaptığı işi taklit eder: ``(B, d)``
    şeridine ardışık karo kapıları vurmak. Tam kayıp çağrısı koşulmaz
    (o saniyeler alır); ölçülen, **kapı başına maliyettir** ve belirteç
    sayısına o oranla çevrilir.
    """
    anahtar = (int(d), int(bayt))
    hazir = _HIZ.get(anahtar)
    if hazir is not None:
        return hazir
    from .donanim import onbellekler
    tip = np.complex64 if int(bayt) == 8 else np.complex128
    B = 8
    r = np.random.default_rng(int(tohum))
    psi = (r.normal(size=(B, int(d))) + 1j * r.normal(size=(B, int(d))))
    psi = np.asarray(psi, tip)
    K = _ikinin_kuvveti(math.sqrt(max(int(d) // 2, 4)), 4)
    G = np.asarray(r.normal(size=(K, K)) + 1j * r.normal(size=(K, K)), tip)
    # Isınma: ilk vuruş tahsis ve önbellek doldurma yükünü taşır.
    T = psi.reshape(B, -1, K)
    for _ in range(3):
        T = (T @ G.T).reshape(B, -1, K)
    n = 24
    t0 = time.perf_counter()
    for _ in range(n):
        T = (T @ G.T).reshape(B, -1, K)
    sure = max(time.perf_counter() - t0, 1e-9)
    kapi_sn = float(n * B) / sure                 # saniyede kaç satır-kapı
    # Bir belirteç, ana akışta ~kapı_yogunlugu kadar karo kapısı yer.
    # Bu sayı ölçümle bulundu: 105 833 kapı / (512 örnek × 512 pencere)
    # ≈ 0,404 kapı/belirteç. Yâni bir belirteç yarım karo kapısından
    # ucuzdur; pahalı olan, kapının ``d`` genlik üstünde koşmasıdır ve
    # o zaten yukarıdaki ölçüme dâhildir.
    kapi_yogunlugu = 0.404
    hiz = kapi_sn / kapi_yogunlugu
    ob = onbellekler()
    assert hiz > 0.0, "hız yoklaması sıfır verdi -- ölçü bir şey ölçmüyor"
    _HIZ[anahtar] = hiz
    return hiz


def olcek(kok: Optional[Kok] = None) -> Dict[str, Any]:
    """**BÜTÜN YAPISAL SAYILAR, ÜÇ FORMÜLDEN.**

    Dönen sözlüğün her anahtarı ``EgitimAyari``de bir alandır ve
    ``__post_init__`` sıfır olanları buradan doldurur.
    """
    k = kok or Kok()
    from .donanim import cekirdek_sayisi, onbellekler
    from .zihin_durumu import QAyar

    c = float(k.comert)
    bayt = 8                                    # complex64
    ob = onbellekler()
    L1 = int(ob.get("L1d") or 32768)
    L2 = int(ob.get("L2") or (1 << 20))
    L3 = int(ob.get("L3") or (32 << 20))

    # ══════════════════════════════════════════════════════════════
    #  FORMÜL 1 -- YAPI (önbellekten)
    # ══════════════════════════════════════════════════════════════
    V = max(2, _yukari_kuvvet(int(k.sozluk)))
    # Cömertlik önbelleğin ne kadarını istediğimizdir: 0,25 → 0,90.
    doluluk = 0.25 + 0.65 * c
    K = _ikinin_kuvveti(math.sqrt(L1 * doluluk / (3.0 * bayt)), 4)
    # Hüküm lifi bütün küllî alanları taşımalı; taşımıyorsa karo büyür.
    yuva = sum(n for _, n in QAyar.kulli_alanlar)
    while K * K < yuva:
        K *= 2
    hukum = K * K
    d = V * K * K
    # Yığın: durum şeridi ``(B, d)`` L3'e sığsın.
    #
    # **BURASI İKİNCİ KERE YAZILMAZ.** ``nefs/onbellek.py:yigin_sec``
    # bu hesabı zaten yapıyor ve **ölçülmüş bir payla** yapıyor (L3'ün
    # %20'si; L3 paylaşımlıdır, durum tek sakini değildir). Kendi
    # payımı uydurup ``doluluk``la çarpsaydım ölçüden ayrılırdım:
    # denendi ve ölçüldü -- ``doluluk=0,35`` B=256 verdi, halbuki
    # ölçülen tavan 128'dir (B=128: 61 660 belirteç/sn, B=256: 58 248).
    # Cömertlik burada **tavanı aşmaz**, yalnız tavana kadar açar.
    from .onbellek import yigin_sec
    tip = np.complex64 if bayt == 8 else np.complex128
    B_tavan = int(yigin_sec(d, tip)["B"])
    # **CÖMERTLİK YIĞINI KÜÇÜLTMEZ.** Denendi ve ölçüldü: cömertlikle
    # ölçekleyince ``comert=0,15`` B=32 verdi ve hız düştü. Sebebi
    # bellidir -- küçük yığın **daima** daha yavaştır (aynı kapı daha
    # az örneğe amorti edilir). Yığın bir bütçe kalemi değil, donanımın
    # tayin ettiği **tavandır**; ona kadar çıkmamak için sebep yok.
    B = int(max(1, B_tavan))

    # ══════════════════════════════════════════════════════════════
    #  FORMÜL 2 -- BÜTÇE (ölçülen hız × ilan edilen süre)
    # ══════════════════════════════════════════════════════════════
    from tanilama.hiz_teftisi import AZAMI_SANIYE
    hiz = hiz_yoklamasi(d, bayt, int(k.tohum))
    butce = float(hiz) * float(AZAMI_SANIYE) * max(c, 1e-3)
    tur = 1 + int(round(8.0 * c))
    yon = 8 + int(round(56.0 * c))
    cagri = max(1, tur * yon)
    kalan = max(butce / float(cagri), 4.0)
    kenar = _ikinin_kuvveti(math.sqrt(kalan), 2)
    # Örnek yığından küçük olmasın (yığın boşa gitmesin), pencere de
    # sözlükten küçük olmasın (bağlam belirteci taşımalı).
    ornek = int(max(kenar, B))
    pencere = int(max(kenar, V))
    # Bütçe aşıldıysa fazlalık pencereden kesilir: yığın donanım
    # ölçüsüdür, pencere ise bütçe ölçüsü.
    while float(cagri) * ornek * pencere > butce and pencere > V:
        pencere //= 2

    # ══════════════════════════════════════════════════════════════
    #  TÜREVLER -- hepsi yukarıdaki üç sayıdan
    # ══════════════════════════════════════════════════════════════
    return {
        # yapı
        "veri_lifi": V, "karo": K, "hukum_lifi": hukum,
        "yigin_dilimi": B,
        # bütçe
        "ornek_sayisi": ornek, "pencere": pencere,
        "talim_tur": tur, "altuzay_ornek": yon,
        #: Çevrim sayısı veri lifinin yarısı kadar: her belirteç
        #: seviyesine ortalama bir çevrim düşsün.
        "cevrim_sayisi": int(max(2, (V // 2) * max(1, int(round(2 * c))))),
        #: Değerlendirme ve doğrulama: bütçenin görev cinsinden karşılığı.
        "degerlendirme_gorevi": int(max(2, round(8 + 112 * c))),
        "dogrulama_sayisi": int(max(4, round(20 + 180 * c))),
        "kademe_gorevi": int(max(1, round(1 + 7 * c))),
        "azami_uret": int(max(8, _ikinin_kuvveti(pencere / 16.0, 8))),
        #: Arama yarıçapı: cömertlik açtıkça arama genişler.
        "yaricap": float(1.5 + 2.5 * c),
        #: **FREN CÖMERTLİKLE KISILMAZ.** Bu bir bütçe değil, bir
        #: emniyet frenidir: koşu fermanın ``AZAMI_SANIYE``sini aşarsa
        #: durur. Cömertlikle ölçeklenirse küçük profil kendi frenine
        #: takılır (ölçüldü: comert=0,15'te fren 90 sn'ye iniyor ve
        #: 104 sn'lik koşuyu reddediyordu). İşin hacmini cömertlik
        #: zaten ``çağrı × örnek × pencere`` ile tayin ediyor.
        "azami_talim_saati": float(AZAMI_SANIYE / 3600.0),
        # donanımdan gelenler
        #: GFNI komutunun cismi. Bir tercih değil, komutun kendisi.
        "galois_us": 8,
        #: Bir ``uint64`` kelimesi -- tableau tek komutta evrilsin.
        "tableau_n": 64,
        #: Faz grubu yazmaçla **aynı** olmalı: ``Z_{veri_lifi}``.
        "faz_mertebesi": V,
        "siklotomik_us": 8,
        #: FLO: Majorana modu çevrim sayısının üç katı (her çevrim bir
        #: köşe çifti), kapı sayısı yığın kadar.
        "flo_modu": int(max(4, 3 * max(2, V // 2))),
        "flo_kapisi": int(max(8, B)),
        #: TDD denetçisinin çekirdeği: bir karo satırı.
        "tdd_cekirdek": int(K),
        #: Stabilizer rank mertebesi: karo satırının yarısı.
        "stab_mertebe": int(max(2, K // 2)),
        #: Sefer bütçesi: çevrimlerin yarısı.
        "usul_seferi": int(max(1, max(2, V // 2) // 2)),
        #: Hafıza kapasitesi: yığın kadar hadise taşınsın.
        "hafiza_kapasitesi": int(max(16, B)),
        #: Ayna turu ve QSVT derecesi: karo satırıyla ölçekli.
        "ayna_tur": int(max(4, K + K // 2)),
        "qudit_qsvt": int(K),
        "qudit_derece": int(max(2, K // 2)),
        "qudit_yon": int(max(2, K // 2)),
        #: Harman kademesi: **her life bir kademe**.
        #:
        #: Evvelce ``K.bit_length()−1`` denemiştim (K=16 için 4) ve
        #: ölçüldü: eski elle yazılmış 3'e nispetle çağrı süresi
        #: 2,59 → 2,73 sn (%5 pahalı), kazanç ise ölçülmedi. Harmanın
        #: manası "kademe kademe yerel üniterle karıştırmak"tır ve
        #: kademe sayısının tabiî ölçüsü **lif sayısıdır**: her kademe
        #: bir lifin ölçeğini ötekilere taşır. Bit sayısı değil.
        "harman_kademesi": 3,
        # ölçüler (rapor için)
        "d": d, "L1d": L1, "L2": L2, "L3": L3, "yigin_tavani": B_tavan,
        "doluluk": doluluk, "ölçülen_hız": hiz, "bütçe": butce,
        "çağrı": cagri, "çekirdek": int(cekirdek_sayisi()),
        "belirteç": float(cagri) * ornek * pencere,
    }


#: **SÖZ HAKLARI.** Toplamı 1'dir ve ayarlanan şey budur: bir kefenin
#: mizanda ne kadar söz hakkı olacağı. Katsayı değil, paydır.
#:
#: Uzay (rezonans) mizanın **çıpasıdır** ve payı en büyüktür: veriye
#: bağlanan tek kefe odur. Nokta (kısmî Born) en küçüktür ve öyle
#: olmalıdır -- büyütülürse mizan bir softmax taklidine iner.
PAYLAR: Dict[str, float] = {
    "uzay": 0.28,        # ℒ_Rezonans -- çıpa, λ = 1 (bölünmez)
    "tip": 0.18,         # ℒ_Hodge
    "kategori": 0.14,    # ℒ_Kategori (funktör)
    "cevrim": 0.12,      # ℒ_Çevrim (Wilson)
    "tenakuz": 0.12,     # ℒ_Tenakuz (log bariyer)
    "monogami": 0.08,    # ℒ_Monogami (CKW)
    "engel": 0.05,       # ℒ_Engel (CIM)
    "nokta": 0.03,       # ℒ_Nokta -- son basamak, küçük kalır
}


def denge(kefeler: Dict[str, float], taban: float = 0.05,
          tavan: float = 8.0) -> Dict[str, float]:
    """**FORMÜL 3 -- λ'LAR ÖLÇÜLÜR, ELLE YAZILMAZ.**

    ``kefeler`` mizanın tâlim başındaki ham dökümüdür. Her kefe için::

        λ_i = (pay_i / pay_uzay) · çıpa / kefe_i

    Yâni ``ℒ_Rezonans`` çıpa alınır (``λ = 1``) ve öteki kefeler ona
    **nispetle** ölçeklenir; böylece her kefe ilan edilen payı kadar
    katkı verir. Büyük sayılı bir kefe küçüklerini ezmez.

    ===================================================================
    İKİ FREN -- VE İKİSİ DE ÖLÇÜMLE KONDU
    ===================================================================

    Ham hâliyle bu formül **ıraksar** ve ölçüldü: tâlim başında
    ``ℒ_Tenakuz = 0,0063`` çıktı (çevrimlerin hepsi kısırdı, bariyer
    daha yanmamıştı) ve ``λ_tenakuz = 48,34`` oldu. Yâni henüz hiçbir
    şey ölçmemiş bir kefe, tâlimin tamamını yutacak ağırlığı aldı.
    Bu, ``1/v`` ağırlıklandırmasının bilinen tuzağıdır: **küçük olan
    kefe, önemli olan kefe değildir** -- çoğu zaman yalnız henüz
    yanmamış olandır.

    İki fren konur ve ikisi de beyan edilir:

    1. **TABAN** -- kefe, çıpanın ``taban`` katından küçükse "henüz
       yanmamış" sayılır ve ölçek ona göre alınır. Sıfıra bölüp
       sonsuz ağırlık üretmek yasaktır (ferman 5).
    2. **TAVAN** -- hiçbir λ, payının ``tavan`` katından fazlasını
       alamaz. Kefeler yandıkça ölçü kendiliğinden yerine oturur;
       tavan yalnız ilk adımdaki ıraksamayı keser.

    Frenlenen kefeler ``frenlenen`` anahtarında **isimleriyle** döner:
    hangi ağırlığın ölçüyle, hangisinin frenle konduğu gizlenmez.
    """
    cipa = float(kefeler.get("rezonans", 0.0))
    pay_u = float(PAYLAR["uzay"])
    o: Dict[str, float] = {}
    frenlenen = []
    esle = {"cevrim": "çevrim", "tenakuz": "tenakuz_bariyer",
            "monogami": "monogami", "engel": "engel", "tip": "hodge",
            "kategori": "kategori", "nokta": "nokta"}
    esik = max(float(taban) * cipa, 1e-9)
    for ad, anahtar in esle.items():
        v = abs(float(kefeler.get(anahtar, 0.0)))
        nispet = float(PAYLAR[ad]) / pay_u
        if v < esik:
            # Henüz yanmamış kefe: ölçek çıpadan değil, payından gelir.
            lam = nispet
            frenlenen.append(ad + "(taban)")
        else:
            lam = nispet * cipa / v
        if lam > nispet * float(tavan):
            lam = nispet * float(tavan)
            frenlenen.append(ad + "(tavan)")
        o["lam_" + ad] = float(lam)
    o["frenlenen"] = frenlenen          # type: ignore[assignment]
    return o


def olcek_beyani(kok: Kok, o: Optional[Dict[str, Any]] = None) -> str:
    """Ölçeğin kendi beyanı -- **formülleriyle beraber** (ferman 1-G)."""
    d = o or olcek(kok)
    return "\n".join([
        "=== ÖLÇEK -- ÜÇ KÖK, ÜÇ FORMÜL (nefs/olcek.py) ===", "",
        "  KÖK 1  sözlük  = %d      (veriden)" % kok.sozluk,
        "  KÖK 2  cömert  = %.2f    (padişahın tek kabzası)" % kok.comert,
        "  KÖK 3  donanım : L1d %d B | L2 %d B | L3 %d B | %d çekirdek"
        % (d["L1d"], d["L2"], d["L3"], d["çekirdek"]),
        "",
        "  FORMÜL 1 -- YAPI (önbellekten)",
        "    V = 2^⌈log₂ sözlük⌉                      = %d" % d["veri_lifi"],
        "    3·K²·bayt ≤ L1d·%.2f  →  K              = %d"
        % (d["doluluk"], d["karo"]),
        "    lif = (V, K, K)   hüküm lifi = K²        = %d"
        % d["hukum_lifi"],
        "    d = V·K²                                 = %d" % d["d"],
        "    B = yigin_sec(d)  (donanım tavanı, kısılmaz)  = %d  [tavan %d]"
        % (d["yigin_dilimi"], d["yigin_tavani"]),
        "",
        "  FORMÜL 2 -- BÜTÇE (ölçülen hız × süre haddi)",
        "    ölçülen hız (mikro yoklama)              = %.0f belirteç/sn"
        % d["ölçülen_hız"],
        "    bütçe = hız × AZAMİ_SANİYE × cömert      = %.3e belirteç"
        % d["bütçe"],
        "    çağrı = tur × yön = %d × %d              = %d"
        % (d["talim_tur"], d["altuzay_ornek"], d["çağrı"]),
        "    örnek × pencere = bütçe/çağrı            = %d × %d"
        % (d["ornek_sayisi"], d["pencere"]),
        "    fiilî yük = çağrı × örnek × pencere      = %.3e belirteç"
        % d["belirteç"],
        "    bütçeye sığdı mı                         : %s"
        % ("evet" if d["belirteç"] <= d["bütçe"] else "HAYIR ⚠"),
        "",
        "  FORMÜL 3 -- DENGE (λ'lar mizanın ilk çağrısından ölçülür)",
        "    söz hakları: %s"
        % "  ".join("%s %.2f" % (a, p) for a, p in sorted(
            PAYLAR.items(), key=lambda x: -x[1])),
        "    toplam pay = %.2f  (1 olmalı)" % sum(PAYLAR.values()),
    ])
