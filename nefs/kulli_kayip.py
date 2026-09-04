"""KÜLLÎ KAYIP ÇİPİ -- ölçü funktörü, kademe hiyerarşisi ve küllî kayıp.

KÜME 5'in tevhidi (kütük H224). Altı dosya -- ``nefs/olcu.py``,
``nefs/sozlesme.py``, ``nefs/kademeler.py``, ``nefs/mudrike.py``,
``nefs/tesir.py``, ``nefs/kulli_kayip.py`` -- burada birleşti. Terkip
üç adımda yapıldı, padişahın usulü gereği: (a) evvelâ her dosya **kendi
içinde** terkip edildi, (b) sonra dosyalar birleştirildi, (c) sonra
birleşik gövdede **bir daha** terkip edildi. Hiçbir cevher seçilip imha
edilmedi; asılları ``yedek/kume5_asillari/`` altında şahittir.

**Kök problem.** Çok mertebeli, kuantum tabanlı ve sembolik bir zihinde
hatalar **farklı uzaylarda** doğar: tenakuz, kopuk adacık, mîzân
dengesi, sükût ihlâli, sadakat kesmesi, istikrâ yakîni. Bunları elle
uydurulmuş katsayılarla toplamak (``0.25·mîzân − 0.1·entropi + kayıp``)
metre ile kilogramı toplamaktır. Ölçü funktörü ``F_S : S → 𝔐`` her
uzayı müşterek bir mertebe uzayına çeker; birleştirme ondan sonra
meşrudur.

**Çipin beş bölümü.**

1. **Ölçü funktörü ve mertebe köprüsü** -- ``mertebe``:
   ``[alt, üst]`` ve ``buyugu_iyi`` cihetiyle ``[0,1]``e dönüşüm
   (1 = yakîn, 0 = vehim), morfizm eşlemesi ve funktör kaidelerinin
   **sayısal sınaması**.
2. **44 meleke hatası ve sözleşme muhasebesi** -- ``olcumlu_idrak``,
   ``bolge_degeri``, ``sozunde_mi``. Öğrenilebilir hata kayba
   girer; **yapısal kusur (MPO kesmesi) girmez**, ayrı raporlanır
   (H154).
3. **Altı kademeli zihinsel hiyerarşi** -- ``Kademeler``: İdrak →
   Tasavvur → Muhakeme → İspat → Tasdik → Beyan, ve **Bırak-Birini
   (LOO)** notlandırması (Doğru 1.00 / Sükût 0.25 / Yanlış 0.00).
   Faaliyet notu yasaktır (H45): "çalıştım/konuştum"a puan verilmez.
4. **Müdrike iç muhakemesi** -- ``suz``: vazife nevi →
   tesadüf mü → örtü kapanıyor mu → kâide/dalga → yakîn → beyan yahut
   **sebebi yazılı** sükût.
5. **Dinamik LogSumExp küllî toplayıcı** -- ``zayif_halka``:
   zayıf halka prensibi ve ``√n`` aktif uzuv hedefleyen dinamik ``β``.

Ayrıca **tesir teşhisi** (``eksilt``): bir meleke düşünce
neticede ne değişir -- yapısal zaruret / tesirli / tesirsiz ayrımı.
"""
from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import (Any, Callable, Dict, Iterable, List, Optional,
                    Sequence, Tuple)

import numpy as np

from matematik.mizan import ardisiklik_kaidesi
from matematik.mizan import mertebe_adi
from .melekeler import (AKIS, Durum, Nefs, QParametre, melekeler,
                        qmelekeler, qsicil)
from .zihin_durumu import QAyar, QYazmac, donme


# ════════════════════════════════════════════════════════════════════
#  nefs/olcu.py
# ════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class OlcuUzayi:
    """Bir ölçünün yaşadığı uzay.

    ``buyugu_iyi`` **cihet**tir ve funktörün monotonluğunu tayin eder:
    entropi büyüdükçe iyidir (dolaşıklık zenginliktir), tenakuz
    büyüdükçe kötüdür. Cihet yazılmazsa toplam manasını yitirir --
    nitekim eski kayıpta entropi eksi işaretle toplanıyordu ve o eksi
    işaret, cihetin koda gömülmüş hâliydi.
    """
    ad: str
    alt: float
    ust: float
    buyugu_iyi: bool
    tahmini_ust: bool = False

    def gecerli_mi(self) -> bool:
        return float(self.ust) > float(self.alt)


MERTEBE_UZAYI = OlcuUzayi("mertebe", 0.0, 1.0, True)


def _mertebeler() -> Dict[str, float]:
    """Merdiven **mizan**dan alınır, burada tekrar yazılmaz.

    Tekrar yazılsaydı iki nüsha olurdu ve biri değişince diğeri sessizce
    yalan söylerdi.
    """
    try:
        # `mizan/munazara.py` merdiveni ``((eşik, ad), …)`` olarak tutar
        # -- eşik önce, ad sonra. Ters çevirip ``ad → eşik`` veriyoruz;
        # ``dict(MERTEBELER)`` doğrudan alınsaydı anahtar sayı, değer
        # dizgi olurdu ve karşılaştırmalar sessizce ters dönerdi.
        from matematik.mizan import MERTEBELER
        return {str(ad): float(esik) for esik, ad in MERTEBELER}
    except Exception:                                    # noqa: BLE001
        return {"vehim": 0.0, "şek": 0.25, "zan": 0.5,
                "zann-ı gālib": 0.75, "yakîn": 1.0}


UZAYLAR: Dict[str, OlcuUzayi] = {
    "tenakuz": OlcuUzayi("tenakuz", 0.0, 1.0, False),
    "nakz": OlcuUzayi("nakz", 0.0, 1.0, False),
    "tasdik": OlcuUzayi("tasdik", 0.0, 1.0, True),
    "sukut": OlcuUzayi("sukut", 0.0, 1.0, False),
    "gaye": OlcuUzayi("gaye", 0.0, 1.0, True),
    "mizan": OlcuUzayi("mizan", 0.0, 1.0, True),
    "makam": OlcuUzayi("makam", 0.0, 1.0, True),
    "kelam": OlcuUzayi("kelam", 0.0, 1.0, True),
    "kesme_hakiki": OlcuUzayi("kesme_hakiki", 0.0, 1.0, False),
    "norm_hatası": OlcuUzayi("norm_hatası", 0.0, 1.0, False),
    # ``−log P`` sınırsızdır; haddi sözlük büyüklüğünden gelir:
    # tekdüze dağılımda ``log(sözlük)``. Ondan kötüsü "tesadüften
    # beter"dir ve kırpılır. Bu bir tahmin değil, hesaplanmış hadd.
    "capraz_entropi": OlcuUzayi("capraz_entropi", 0.0, float(np.log(16.0)),
                                False),
    "hucre_isabeti": OlcuUzayi("hucre_isabeti", 0.0, 1.0, True),
    "tam_cozum": OlcuUzayi("tam_cozum", 0.0, 1.0, True),
}


def mertebe(x=None, S=None, ne: str = "ileri", m: float = 0.0,
                    f=None, T=None, tohum: int = 0, n: int = 64,
                    ad: str = "", ust=None):
    """HER ÖLÇÜYÜ AYNI MERDİVENE ÇEVİRMEK -- **tek terkip** (kütük H224).

    Küme: ``uzay`` + ``funktor`` + ``funktor_tersi`` + ``morfizm_funktoru``
    + ``funktor_dogrula`` + ``mertebele``. Altısı tek funktörün --
    ``F_S : S → 𝔐``in -- ayrı veçheleridir: uzayı bul, elemanı çevir,
    geri çevir, morfizmi çevir, kaideyi sına, neticeyi adlandır.

    ==============  ==================================================
    ``ne``          döndürdüğü
    ==============  ==================================================
    ``uzay``        adı bilinen ölçü uzayı; bilinmiyorsa **tahminî**
    ``ileri``       ``F_S(x)`` -- daima 1 = yakîn, 0 = vehim
    ``geri``        ``F_S⁻¹(m)`` -- morfizm eşlemesinin gerektirdiği
    ``morfizm``     ``F(f) = F_T ∘ f ∘ F_S⁻¹``
    ``doğrula``     ``F(id) = id`` ve ``F(g∘f) = F(g)∘F(f)`` sınaması
    ``adlandır``    sürekli mertebeyi merdivenin basamağına adlandır
    ==============  ==================================================

    Funktörün asıl tarifi **morfizm eşlemesidir**; eleman eşlemesi onun
    husûsî hâlidir. İleri eşleme monotondur: ``buyugu_iyi`` ise artan,
    değilse azalan. Monotonluk morfizm kaidesinin şartıdır ve
    ``doğrula`` kipinde fiilen sınanır -- sınanmayan bir funktör
    iddiası, elle konmuş katsayının süslü hâlidir.

    ``adlandır`` **yalnız rapor içindir**; kayıpta kullanılmaz.

    Haddi olmayan (``gecerli_mi`` düşen) bir uzayda hüküm verilmez:
    ileri eşleme orta mertebeyi (``0.5``) döndürür.
    """
    if ne == "uzay":
        if ad in UZAYLAR and ust is None:
            return UZAYLAR[ad]
        if ust is None:
            return OlcuUzayi(ad, 0.0, 1.0, False, tahmini_ust=True)
        return OlcuUzayi(ad, 0.0, float(ust), False,
                         tahmini_ust=ad not in UZAYLAR)

    def ileri(v, U):
        if not U.gecerli_mi():
            return 0.5              # had yok: hüküm yok, orta mertebe
        u = (float(v) - U.alt) / (U.ust - U.alt)
        u = float(np.clip(u, 0.0, 1.0))
        return u if U.buyugu_iyi else 1.0 - u

    def geri(v, U):
        if not U.gecerli_mi():
            return U.alt
        u = float(np.clip(v, 0.0, 1.0))
        if not U.buyugu_iyi:
            u = 1.0 - u
        return U.alt + u * (U.ust - U.alt)

    if ne == "ileri":
        return ileri(x, S)
    if ne == "geri":
        return geri(m, S)
    if ne == "morfizm":
        return lambda z: ileri(f(geri(z, S)), T)
    if ne == "adlandır":
        k, _ = min(_mertebeler().items(),
                   key=lambda kv: abs(kv[1] - float(m)))
        return k
    if ne != "doğrula":
        raise ValueError("funktör kipi bilinmiyor: %r" % (ne,))
    rng = np.random.default_rng(tohum)
    S = OlcuUzayi("S", -2.0, 5.0, True)
    T = OlcuUzayi("T", 0.0, 3.0, False)
    U = OlcuUzayi("U", 1.0, 9.0, True)
    m = rng.uniform(0.0, 1.0, size=n)

    # 1) birim kaidesi
    birim = mertebe(ne="morfizm", f=lambda x: x, S=S, T=S)
    hata_birim = float(np.max(np.abs([birim(v) - v for v in m])))

    # 2) terkip kaidesi -- iki monoton eşleme
    def f(x: float) -> float:            # S → T, artan
        return 0.0 + 3.0 * (x + 2.0) / 7.0

    def g(x: float) -> float:            # T → U, artan
        return 1.0 + 8.0 * x / 3.0

    sol = mertebe(ne="morfizm", f=lambda x: g(f(x)), S=S, T=U)
    sag_f = mertebe(ne="morfizm", f=f, S=S, T=T)
    sag_g = mertebe(ne="morfizm", f=g, S=T, T=U)
    hata_terkip = float(np.max(np.abs(
        [sol(v) - sag_g(sag_f(v)) for v in m])))

    # 3) **TERKİP KAİDESİ ZATEN AŞİKÂRDIR -- ve bunu saklamak yanlış olurdu.**
    #
    # İlk yazışımda buraya "monoton olmayan bir eşleme terkip kaidesini
    # bozmalı" diye bir körlük sınaması koymuştum ve ÖLÇÜLDÜ: bozmuyor.
    # Sebebi cebrîdir ve sınamanın değil benim hatamdı::
    #
    #     F(g)∘F(f) = (F_U∘g∘F_T⁻¹)∘(F_T∘f∘F_S⁻¹) = F_U∘(g∘f)∘F_S⁻¹ = F(g∘f)
    #
    # ``F_T⁻¹∘F_T`` sadeleşir; yani terkip kaidesi ``f`` ve ``g`` **ne
    # olursa olsun** sağlanır. O hâlde terkip sınaması bir şey ispat
    # etmez ve "funktör olduğunu sınadım" demenin dayanağı olamaz.
    #
    # Bu inşada **yük taşıyan** hususiyet başkadır: ``F_S``in
    # **sıra koruması**. 𝒮 ve 𝔐 birer sıralı kümedir (hata büyüdükçe
    # mertebe düşer); funktörün manalı olması, o sıranın korunmasına
    # bağlıdır. Sınanan da odur ve burada körlük hakikîdir: cihet ters
    # çevrilirse sıra bozulur ve kırmızı yanar.
    x = np.sort(rng.uniform(S.alt, S.ust, size=n))
    mert = np.asarray([mertebe(v, S) for v in x])
    sira_korunuyor = bool(np.all(np.diff(mert) >= -1e-12))

    S_ters = OlcuUzayi("S_ters", S.alt, S.ust, not S.buyugu_iyi)
    mert_ters = np.asarray([mertebe(v, S_ters) for v in x])
    sira_bozuluyor = bool(np.all(np.diff(mert_ters) <= 1e-12)
                          and np.ptp(mert_ters) > 1e-6)

    return {"birim_hatası": hata_birim,
            "terkip_hatası": hata_terkip,
            "terkip_aşikâr_mı": True,
            "sıra_korunuyor": sira_korunuyor,
            "cihet_ters_çevrilince_bozuluyor": sira_bozuluyor,
            "funktör_mü": (hata_birim < 1e-9 and hata_terkip < 1e-9
                           and sira_korunuyor),
            "ölçüt_kör_değil": sira_korunuyor and sira_bozuluyor}


@dataclass
class Olcum:
    """Bir uzuvun **kendi uzayındaki** ham hatası.

    ``kaynak`` melekenin numarası yahut kademenin adıdır; ``agirlik``
    bir kalibrasyon sabiti değil, o uzvun kaç kere sayılacağıdır.
    """
    kaynak: str
    deger: float
    uzay: OlcuUzayi
    agirlik: float = 1.0

    def mertebe(self) -> float:
        return mertebe(self.deger, self.uzay)

    def eksik(self) -> float:
        """Yakînden uzaklık: müşterek uzaydaki **kayıp** payı."""
        return self.agirlik * (1.0 - self.mertebe())


BETA: float = 8.0


DINAMIK_BETA: bool = False


HEDEF_USSU: float = 0.5


def zayif_halka(x=None, beta=None, ne: str = "asgarî",
                             olcumler=None, hedef_us=None):
    """ZAYIF HALKAYA GÖRE TOPLAMAK -- **tek terkip** (kütük H224).

    Küme: ``yumusak_asgari`` + ``_katilan_uzuv`` + ``dinamik_beta`` +
    ``kulli_toplam``. Dördü **tek çekirdeğin** -- kaydırmalı
    log-sum-exp'in -- ayrı okunuşudur; işaret ve kaydırma değişir,
    formül değişmez::

        yumuşak(x; ±β) = ±(1/β)·[ log Σ exp(±β·xᵢ) − log n ]

    ==============  ==================================================
    ``ne``          döndürdüğü
    ==============  ==================================================
    ``asgarî``      yığının **en zayıf üyesine** göre birleşim (−β)
    ``azamî``       uzuvların **en zayıfına** göre küllî kayıp (+β)
    ``katılan``     kaç uzuv fiilen hükme katılıyor (perpleksite)
    ``beta``        ``√n`` aktif uzuv hedefleyen dinamik ``β``
    ==============  ==================================================

    **NİÇİN ORTALAMA DEĞİL.** Bir organ ölçüsü yığında ``B`` üye
    üzerinde okunur. Evvelce ortalaması alınıyordu ve ölçüldü (kütük
    H151): ``B`` büyüdükçe parametre yayılımı **düşüyor** -- yani yığını
    büyütmek, tam da eniyilenen işareti söndürüyordu (``σ/√B``). Bu,
    kütük H145'in bir kademe yukarısıdır: orada 105 uzuv ortalanıyordu,
    burada ``B`` veri.

    Hüküm aynıdır ve manevîdir: **bir yığında tek bir veride düşen
    parametre yakîn sayılamaz.** Netice en zayıf üyesi kadar sağlamdır;
    üyeleri ortalamak, kötü üyeyi iyilerin arkasına saklamaktır.

    ``β → 0`` ortalamaya, ``β → ∞`` tam uca gider. ``log n``
    çıkarılması **şarttır**: çıkarılmazsa uzuv sayısı arttıkça kayıp
    kendiliğinden büyür ve "daha çok uzuv bağlamak" cezalandırılırdı.
    """
    if ne == "asgarî":
        a = np.asarray(x, float).reshape(-1)
        if a.size == 0:
            return 0.0
        if a.size == 1:
            return float(a[0])
        b = float(max(beta if beta is not None else BETA, 1e-6))
        z = -b * a
        m = float(np.max(z))
        return float(-(m + np.log(np.sum(np.exp(z - m)))
                       - np.log(a.size)) / b)

    if ne == "katılan":
        eksikler = np.asarray(x, float)
        z = beta * eksikler
        z = z - float(np.max(z))
        w = np.exp(z)
        t = float(np.sum(w))
        if t <= 0.0:
            return float(eksikler.size)
        w = w / t
        nz = w > 0.0
        H = float(-np.sum(w[nz] * np.log(w[nz])))
        return float(np.exp(H))

    if ne == "beta":
        eksikler = x
        e = np.asarray(eksikler, float).reshape(-1)
        n = e.size
        if n <= 1:
            return float(BETA)
        if float(np.ptp(e)) < 1e-12:
            # Bütün uzuvlar eşit: ``β``nın hiçbir tesiri yok, en ucuzu.
            return float(alt)
        hedef = float(n) ** float(np.clip(HEDEF_USSU, 0.0, 1.0))
        hedef = float(np.clip(hedef, 1.0 + 1e-9, n - 1e-9))
        lo, hi = float(alt), float(ust)
        # ``_katilan_uzuv`` ``β``da azalandır; ikili arama tektir.
        if zayif_halka(e, lo, ne="katılan") <= hedef:
            return lo
        if zayif_halka(e, hi, ne="katılan") >= hedef:
            return hi
        for _ in range(48):
            orta = 0.5 * (lo + hi)
            if zayif_halka(e, orta, ne="katılan") > hedef:
                lo = orta
            else:
                hi = orta
        return 0.5 * (lo + hi)

    if ne != "azamî":
        raise ValueError("toplama kipi bilinmiyor: %r" % (ne,))
    if not olcumler:
        return {"kayıp": 0.0, "ortalama_mertebe": 1.0, "uzuv": 0,
                "en_zayıf": None, "tahminî_hadli": 0}
    eksikler = [o.eksik() for o in olcumler]
    mert = [o.mertebe() for o in olcumler]
    en_zayif = min(olcumler, key=lambda o: o.mertebe())
    n = len(eksikler)
    # **DİNAMİK β (ceride hükmü).** ``beta`` verilmezse ölçünün kendi
    # dağılımından tayin edilir; sabit ``β`` verilirse eski davranış
    # aynen durur ve kıyas edilebilir (H90).
    if beta is None:
        beta = zayif_halka(eksikler, ne="beta") if DINAMIK_BETA else BETA
    b = float(max(beta, 1e-6))
    try:
        from matematik.fitrat import logsumexp
        yumusak = (float(logsumexp([b * e for e in eksikler]))
                   - float(np.log(n))) / b
    except Exception:                                    # noqa: BLE001
        z = b * np.asarray(eksikler, float)
        yumusak = float(z.max() + np.log(np.exp(z - z.max()).sum())
                        - np.log(n)) / b
    return {"kayıp": float(np.clip(yumusak, 0.0, 1.0)),
            "β": b,
            "katılan_uzuv": zayif_halka(
                np.asarray(eksikler, float), b, ne="katılan"),
            "azamî_eksik": float(max(eksikler)),
            "ortalama_eksik": float(np.mean(eksikler)),
            "ortalama_mertebe": float(np.mean(mert)),
            "uzuv": n,
            "en_zayıf": (en_zayif.kaynak, float(en_zayif.mertebe())),
            "tahminî_hadli": sum(1 for o in olcumler if o.uzay.tahmini_ust)}




# ════════════════════════════════════════════════════════════════════
#  nefs/sozlesme.py
# ════════════════════════════════════════════════════════════════════

ESIK: float = 1e-6


BOLGELER: Tuple[str, ...] = (
    "veri", "yerel", "makam", "mizan", "tenakuz", "tasdik", "sukut",
    "nakz", "kelam", "kaide", "orak", "gaye", "tertip",
    # --- ceride taksimatı (kütük H213). 𝒪₄₄ Tahsil ``parametre``
    # bölgesine dokunur; bu üçü listede olmadığı sürece sözleşme
    # ölçüsü oraya **kör**dü: meleke yazıyor, ölçü görmüyordu.
    "meleke_b", "parametre", "ancilla",
)


SOZLESME: Dict[int, Tuple[Tuple[str, ...], str]] = {
    1:  (("veri",), "öz-dikkat: yalnız veri kübitleri"),
    2:  (("veri",), "hayal: satırın son veri kübitini aralar"),
    3:  (("veri",), "muhayyile: satır içi atlamalı çiftler"),
    4:  (("veri", "yerel"), "satırı kendi yerel hükmüne bağlar"),
    5:  (("veri",), "tecrit: fırça katmanının tersi"),
    6:  (("veri", "yerel"),
         "MERA kademesi satır bölgesine vurur; küllî bloğa DOKUNMAZ (H119)"),
    7:  (("yerel", "tasdik"), "mana: yerel hükümler tasdike akar"),
    8:  (("veri",), "tahlil: kübit başına dönme"),
    9:  (("veri",), "terkip: ters yönlü fırça"),
    10: (("veri",), "tezat: işaret çevirme"),
    11: (("yerel", "tenakuz"), "çelişki küllî tenakuz alanına akar"),
    12: (("yerel",), "tenkit: yerel hükmü bastırır"),
    13: (("tasdik",), "tasdik mührü: yalnız tasdik alanı"),
    14: (("tasdik", "mizan"), "gaye: tasdiki mîzâna bağlar"),
    15: (("nakz",), "merak: nakz alanını süperpozisyona sokar"),
    16: (("veri",), "keşif hamleleri"),
    17: (("mizan",), "önsel mîzâna yazılır"),
    18: (("veri",), "kıyas: komşu satırların veri kübitleri"),
    19: (("veri",), "temsil: dik ve tersinir"),
    20: (("veri",), "teşbih: ilk iki satır"),
    21: (("veri", "yerel", "makam"), "tefekkür: 20 mertebe, makama akar"),
    22: (("veri",), "illet: yönlü, satırdan satıra"),
    23: (("yerel", "nakz"), "mantık: nakz birikimi"),
    24: (("yerel",), "ispat: yerel hükümler zinciri"),
    25: (("veri",), "teemmül: aynı fırça, birkaç tur"),
    26: (("yerel",), "temkin: küçük açı"),
    27: (("veri",), "tetkik"),
    28: (("veri",), "tashih: tetkikin tersi"),
    29: (("veri",), "teyit: satırın iki ucu"),
    30: (("yerel", "tasdik"), "tahkik: ikinci yoldan tasdike"),
    31: (("veri", "mizan"), "tedebbür: ileri sarım + mîzân"),
    32: (("nakz", "tenakuz", "tasdik", "makam", "sukut"),
         "makam üç kaynaktan çevrilir, sükût kapısı açılır"),
    33: (("tasdik", "tenakuz", "nakz", "mizan"), "muhakeme: meclis"),
    34: (("yerel", "makam"), "tafsil: makam yerellere dağılır"),
    35: (("veri",), "tefsir: siyak ve sibak"),
    36: (("tenakuz", "tasdik"), "te'vil: çelişki şartıyla"),
    # --- BEYAN KAPISI (kullanıcı kat'î kararı / kütük H131):
    # dördü de ham veriden KOPARILDI; mana yalnız hükümden akar.
    37: (("yerel", "tasdik", "kelam"),
         "fesâhat: mana YEREL HÜKÜMden kelama akar; tasdik mührü şart"),
    38: (("tasdik", "kelam"), "talâkat: akıcılık tasdikten, veriden değil"),
    39: (("makam", "tasdik", "kelam"), "belâgat: makam ve tasdik kelama"),
    40: (("makam", "kelam"), "sanat: altın açı, yalnız hüküm ve kelamda"),
    41: (("mizan", "makam", "sukut", "kelam"), "münazara + sükût kapısı"),
    # --- 𝒪₄₂–𝒪₄₄ TEŞKİLÂT (kütük H213). Üçü de akışa yeni girdi;
    # sözleşmeleri kendi tariflerinden çıkarıldı, ölçümden değil.
    42: (("yerel", "mizan", "tenakuz"),
         "umumileştirme: bütün duraklardan AYNI açıyla mîzâna (kesişim), "
         "araz tenakuza"),
    43: (("kelam",),
         "talim: kelamı kademe kademe keskinleştirir (τ monoton azalan)"),
    44: (("mizan", "parametre"),
         "tahsil: mîzân kontrollü Gibbs sönümü + γ kimlik payı, "
         "parametre bölgesine"),
}


def sozunde_mi(no: int = 0, n_satir: int = 4, chi: int = 32,
                        tohum: int = 0, esik: float = ESIK,
                        ne: str = "dokundu") -> object:
    """TAAHHÜT EDİLEN BÖLGEYE Mİ DOKUNDU -- **tek terkip** (kütük H224).

    Küme: ``_bolge_yuvalari`` + ``_guzergah`` + ``_yogunluklar`` +
    ``_hazirla`` + ``dokunulan_bolgeler`` + ``sozlesmeyi_olc``. Altısı
    tek amelin durakları idi ve dördü yalnız beşincisi için vardı.

    ``ne="dokundu"`` bir melekeyi ölçer; ``ne="hepsi"`` 44'ünü tek tek
    yüzleştirir. Bu bir **ölçümdür, iddia değil**: melekenin sözleşmesi
    ne derse desin, dokunduğu bölgeler yoğunluk farkından okunur.

    **HEDEF ile GÜZERGÂH niçin ayrı.** İlk yüzleştirmede 41 melekenin
    16'sı "ihlâl" verdi ve hepsinin sebebi tekti: MPS bir **zincirdir**;
    uzak iki kübite dokunmanın iki yolu vardır ve ikisi de aradan
    geçer --

    * **takas ağı** kübitleri fiilen yürütür; geçtiği her kesitte SVD
      budaması yapılır,
    * **MPO** kübit oynatmaz fakat ``bas``tan ``son``a bütün aralığı
      yeniden sıkıştırır.

    İkisi de cebren kimliktir; fakat **kesme üniter değildir**, o yüzden
    aradaki kübitlerin yoğunluğu bir parça oynar. Yani meleke o
    bölgelere *manen* dokunmaz, *fiilen* dokunur. Bu bir kusur değil
    MPS'in tabiatıdır ve gizlenmemelidir. İhlâl, **güzergâhın da**
    dışına çıkmaktır -- ve o hâlâ kırmızı yanabilir: meselâ zincirin sağ
    ucundaki ``tertip``e dokunan bir veri melekesi yakalanır. Güzergâh
    **ilandan** türetilir, ölçümden değil; ölçümden türetilseydi
    sözleşme kendi kendini onaylar ve hiçbir şey ispat etmezdi.

    **BAŞLANGIÇ DOLAŞIK KURULUR.** Çarpım durumunda ölçüm iş görmez:
    birçok kapı ``|0⟩`` üzerinde hiçbir şey yapmaz ve meleke dokunduğu
    hâlde dokunmamış görünür. Onun için gerçek akışın başlangıcı
    kurulur: kodla → süperpozisyon → MERA.

    **KÜLLÎ BLOK UYANDIRILIR -- ve sebebi ölçülmüştür.** İlk
    yüzleştirmede 𝒪₃₂, 𝒪₃₃, 𝒪₃₄ ve 𝒪₃₉ ilan ettikleri küllî alanlara
    "hiç dokunmamış" göründü. Sebep melekeler değil, ölçümün kendisiydi:
    akışın başında küllî blok ``|0⟩``dadır ve **kontrolü ``|0⟩`` olan
    bir kontrollü dönme hiçbir şey yapmaz**. Yani meleke atıl değildi,
    ölçüm onu hiç ateşlememişti. Sözleşme melekenin DAYANAĞINI (support)
    tarif eder, filanca koşudaki tesirini değil; o hâlde blok, hiçbir
    alanı ``|0⟩``da bırakmayan cüzî bir dönmeyle uyandırılır. Bu, akışın
    davranışını değiştirmez -- yalnız ölçüm burada yapılır.
    """
    if ne == "hepsi":
        return [sozunde_mi(m.no, n_satir, chi, tohum, esik)
                for m in qmelekeler()]
    if ne != "dokundu":
        raise ValueError("sözleşme ölçüsünün kipi bilinmiyor: %r" % (ne,))

    def bolge_yuvalari(q):
        """Her bölgenin zincirdeki kübit yerleri."""
        d = {"veri": [q.veri(i, j) for i in range(q.n_satir)
                      for j in range(q.ayar.satir_kubiti)],
             "yerel": q.yereller()}
        for a, kac in q.ayar.kulli_alanlar:
            d[a] = [q.kulli(a, j) for j in range(kac)]
        # ceride taksimatı: bölge açıksa yuvaları da ölçüye girer.
        for a, anahtar in (("meleke", "meleke_b"),
                           ("parametre", "parametre"),
                           ("ancilla", "ancilla")):
            if q.bolge_var(a):
                bas, kac = q.taksimat.bolge[a]
                d[anahtar] = list(range(bas, bas + kac))
        return d

    def yogunluklar(q):
        return np.asarray(q.y.tekil_yogunluklar(list(range(q.n))), float)[0]

    # --- dolaşık başlangıç
    rng = np.random.default_rng(tohum)
    q = QYazmac(n_satir, QAyar(bag=int(chi), tohum=tohum))
    q.kodla(rng.normal(size=(n_satir, 12)))
    q.superpozisyon()
    q.mera()
    for a, kac in q.ayar.kulli_alanlar:
        for j in range(kac):
            q.tek(q.kulli(a, j), donme(0.4))
    p = QParametre(tohum)

    once = yogunluklar(q)
    qsicil()[int(no)].kosu(q, p)
    sonra = yogunluklar(q)
    sapma = np.max(np.abs(sonra - once), axis=(1, 2))     # kübit başına

    yuv = bolge_yuvalari(q)
    olculen, en_buyuk = [], {}
    for a in BOLGELER:
        if not yuv.get(a):
            continue
        sv = float(np.max(sapma[np.asarray(yuv[a], np.intp)]))
        en_buyuk[a] = sv
        if sv > esik:
            olculen.append(a)

    ilan = set(SOZLESME[int(no)][0])
    hepsi_yuva = []
    for a in ilan:
        hepsi_yuva += yuv.get(a, [])
    if not hepsi_yuva:
        guz = set(ilan)
    else:
        bas, son = min(hepsi_yuva), max(hepsi_yuva)
        guz = {a for a, y in yuv.items()
               if y and any(bas <= i <= son for i in y)}

    return {
        "no": int(no),
        "ilan": tuple(sorted(ilan)),
        "güzergâh": tuple(sorted(guz - ilan)),
        "ölçülen": tuple(sorted(olculen)),
        "ihlâl": tuple(sorted(set(olculen) - guz)),
        "kullanılmayan": tuple(sorted(ilan - set(olculen))),
        "sapma": en_buyuk,
        "sadakat": float(q.y.sadakat()),
    }




# ════════════════════════════════════════════════════════════════════
#  nefs/kademeler.py
# ════════════════════════════════════════════════════════════════════

Izgara = np.ndarray


KADEME_VARSAYILAN: Dict[str, Tuple[float, float, float]] = {
    # anahtar                    (varsayılan, alt, üst)
    "kademe.idrak.nesne":        (1.0,  1.0,  8.0),   # asgarî bileşen ebadı
    "kademe.muhakeme.derinlik":  (2.0,  1.0,  4.0),   # terkip derinliği
    "kademe.tasdik.müphem":      (0.5,  0.1,  1.0),   # müphemlik cezası
    "kademe.tasdik.tevafuk":     (0.6,  0.2,  1.0),   # tek şahitli tevâfuk
    "kademe.tasdik.taban":       (0.5,  0.1,  1.0),   # hüküm ağırlığı tabanı
    "kademe.beyan.eşik":         (0.55, 0.05, 0.95),  # konuşma eşiği
}


def kademe_parametreleri_ac(p) -> int:
    """Kademelerin yerlerini düz vektörde **peşinen** aç; sayısını döndür.

    Zaruridir: ``QParametre.al`` bir anahtarı **ilk istendiğinde** tahsis
    eder, yani kademe sayıları ancak ilk kademe koşusunda vektöre
    girerdi. Eğitim motoru ise boyutu (``d``) baştan sabitler; boyut
    ortada değişirse motor kendi öğrendiğini siler -- kütük H39'da
    ölçülmüş kusurun ta kendisi. Onun için yerler eğitim başlamadan
    açılır.
    """
    n = 0
    for anahtar in KADEME_VARSAYILAN:
        try:
            p.al(anahtar, 1) if hasattr(p, "al") else p.v(anahtar, 1)
            n += 1
        except Exception:                                # noqa: BLE001
            pass
    return n


MERTEBE_NOTU: Dict[str, float] = {"doğru": 1.0, "sükût": 0.25,
                                  "yanlış": 0.0}


K_UZAY: Dict[str, OlcuUzayi] = {
    "idrak": OlcuUzayi("idrak", 0.0, 1.0, True),
    "tasavvur": OlcuUzayi("tasavvur", 0.0, 1.0, True),
    "muhakeme": OlcuUzayi("muhakeme", 0.0, 1.0, True),
    "ispat": OlcuUzayi("ispat", 0.0, 1.0, True),
    "tasdik": OlcuUzayi("tasdik_kademe", 0.0, 1.0, True),
    "beyan": OlcuUzayi("beyan", 0.0, 1.0, True),
}


@dataclass
class Idrak:
    """1. kademenin çıktısı: ızgaradan **görülen** şey."""
    ciftler: List[Tuple[Izgara, Izgara]]
    girdiler: List[Izgara]
    nesne_sayisi: List[int] = field(default_factory=list)
    olcu: Optional[Tuple[int, int]] = None      # kestirilen çıktı ölçüsü
    olcu_sebebi: str = ""
    sekil_kaidesi: Optional[str] = None
    ayni_sekil: bool = False


@dataclass
class Hal:
    """2. kademenin çıktısı: müşterek özellik uzayındaki temsil."""
    ozellik: np.ndarray
    kademe_sayisi: int = 0
    spektral_rutbe: int = 0
    kabalastirma_kaybi: float = 1.0


@dataclass
class Namzet:
    """3. kademenin çıktısı: kaide adayları, **sıralı**."""
    kaideler: List[object] = field(default_factory=list)
    aranan: int = 0


@dataclass
class Ispat:
    """4. kademenin çıktısı: ispattan sağ çıkanlar."""
    kaideler: List[object] = field(default_factory=list)
    elenen: int = 0
    gerekce: str = ""


@dataclass
class Yakin:
    """5. kademenin çıktısı: mertebe."""
    deger: float = 0.0
    istikra: float = 0.0
    muphem: bool = False
    tevafuk: float = 0.0


class Kademeler:
    """Altı kademe; her biri bir öncekinin çıktısını yer.

    ``muhakeme`` sırasında her kademe kendi hatasını ``self.olcumler``e
    yazar; o liste `nefs/kulli_kayip.py`ye verilir ve **eğitime girer**.
    """

    def __init__(self, p=None) -> None:
        self.olcumler: List[Olcum] = []
        self.eksik: Dict[str, str] = {}
        self.gunluk: List[str] = []
        #: Melekelerin açılarıyla **aynı** düz vektör (``QParametre``).
        #: ``None`` ise varsayılanlar kullanılır ve kademe eğitilmez.
        self.p = p
        #: 5. kademenin ilan ettiği yakîn; ``capraz_not`` onu hakikatle
        #: yüzleştirip ayar (calibration) notunu koyar.
        self.yakin_ilani: float = 0.0

    # -- öğrenilen sayılar --------------------------------------------
    def _par(self, anahtar: str) -> float:
        """Öğrenilen bir kademe sayısı -- haddine sıkıştırılmış.

        Ham parametre ``ℝ``dedir; ``tanh`` ile ``[-1,1]``e, oradan
        ``[alt, üst]``a taşınır. **Sıfır ham değer tam olarak
        varsayılanı verir**: ``tanh(0) = 0`` ve haritalama varsayılanın
        etrafında kurulur. Yani eğitilmemiş bir model, H156'dan evvelki
        modelin **birebir aynısıdır** -- yeni tertip, eskisini sessizce
        değiştirerek işe başlamaz.
        """
        var, alt, ust = KADEME_VARSAYILAN[anahtar]
        if self.p is None:
            return float(var)
        try:
            ham = float(np.asarray(self.p.al(anahtar, 1), float).ravel()[0]) \
                if hasattr(self.p, "al") else float(self.p.v(anahtar, 1)[0])
        except Exception:                                # noqa: BLE001
            return float(var)
        t = float(np.tanh(ham))
        # varsayılanın iki yanına ayrı ayrı esner ki sıfır = varsayılan
        return float(var + t * ((ust - var) if t >= 0.0 else (var - alt)))

    def _olc(self, ad: str, deger: float) -> None:
        self.olcumler.append(Olcum("kademe.%s" % ad, float(deger),
                                   K_UZAY[ad]))

    def _dene(self, ad: str, f):
        try:
            return f()
        except Exception as e:                           # noqa: BLE001
            self.eksik[ad] = "%s: %s" % (type(e).__name__, str(e)[:60])
            return None

    # -- 1. İDRAK: Görev → İdrak -------------------------------------
    def idrak(self, gorev) -> Idrak:
        """Izgaradan **görüleni** çıkar: nesne, ölçü, şekil kaidesi.

        Ölçü kestirimi **iki müstakil şahitten** alınır (`nefs/boyut.py`
        ve `idrak/sekil.py`); ikisi uyuşmuyorsa bu bir bilgidir ve 5.
        kademede yakîni düşürür. Tek şahitle yetinmek, ihtilâfı hiç
        görmemek olurdu.
        """
        ciftler = [(np.asarray(a, np.int64), np.asarray(b, np.int64))
                   for a, b in getattr(gorev, "egitim", [])]
        girdiler = [np.asarray(a, np.int64)
                    for a, _ in getattr(gorev, "sinama", [])]
        I = Idrak(ciftler, girdiler)
        if not ciftler:
            self._olc("idrak", 0.0)
            return I
        I.ayni_sekil = all(a.shape == b.shape for a, b in ciftler)

        esik_nesne = int(round(self._par("kademe.idrak.nesne")))

        def _nesne():
            from idrak.cozucu import _bilesenler
            # Arka plan rengi. Evvelce `nefs/kaideler.py`den geliyordu;
            # o dosya padişahın fermanıyla **silinmiştir** ve sabit
            # burada durur -- ARC'de arka plan ezici çoğunlukla 0'dır.
            ARKA = 0
            # **Öğrenilen eşik:** ``esik_nesne`` hücreden küçük bileşen
            # nesne sayılmaz. ARC'de tek hücrelik lekeler bazen gürültü,
            # bazen asıl işarettir; hangisi olduğu göreve göre değişir ve
            # elle konacak bir sayı değildir.
            # ``_bilesenler`` ``(renk, maske, kutu)`` döndürür; bileşenin
            # ebadı maskenin dolu hücre sayısıdır.
            return [sum(1 for _renk, maske, _kutu in _bilesenler(a, ARKA)
                        if int(maske.sum()) >= esik_nesne)
                    for a, _ in ciftler]
        I.nesne_sayisi = self._dene("idrak.cozucu", _nesne) or []

        def _mubser():
            from .musahede import devinim_olc, bak
            return devinim_olc(bak(ciftler[0][0]),
                               bak(ciftler[0][1]))
        self._dene("nefs.mubser", _mubser)

        def _boyut():
            from .musahede import kalip
            b, sebep = kalip(ciftler, girdiler[0] if girdiler
                                    else ciftler[0][0])
            return (None if b is None else tuple(int(x) for x in b)), sebep
        r = self._dene("nefs.boyut", _boyut)
        if r is not None:
            I.olcu, I.olcu_sebebi = r

        def _sekil():
            from .musahede import kalip
            k = kalip(ciftler, ne="şekil")
            return None if k is None else str(k)
        I.sekil_kaidesi = self._dene("idrak.sekil", _sekil)

        # İdrakın hatası: **belirsizlik**. Ölçü bilinmiyor ve nesne
        # ayrıştırılamıyorsa görülen şey yoktur.
        h = 0.0
        h += 0.5 if I.olcu is not None else 0.0
        h += 0.3 if I.nesne_sayisi and min(I.nesne_sayisi) > 0 else 0.0
        h += 0.2 if I.sekil_kaidesi is not None else 0.0
        self._olc("idrak", h)
        self.gunluk.append(
            "1. İDRAK: %d çift, %s, ölçü %s (%s), şekil kaidesi %s"
            % (len(ciftler), "aynı şekilli" if I.ayni_sekil
               else "şekil değişiyor", I.olcu, I.olcu_sebebi or "—",
               "var" if I.sekil_kaidesi else "yok"))
        return I

    # -- 2. TASAVVUR: İdrak → Hâl ------------------------------------
    def tasavvur(self, I: Idrak) -> Hal:
        """Görüleni **müşterek bir özellik uzayına** taşı.

        Üç ölçek beraber: sağîr (yerel), kebîr (küllî) ve tayf. Tek
        ölçekte bakmak, ARC'de en sık yapılan hatadır -- desen bir
        ölçekte görünüp diğerinde kaybolur.
        """
        H = Hal(np.zeros(0))
        if not I.ciftler:
            self._olc("tasavvur", 0.0)
            return H
        A = I.ciftler[0][0]

        def _iki_olcek():
            from .musahede import iki_olcegin_acisi

            class _G:
                ad, kaynak = "kademe", "kademe"
                egitim = I.ciftler
                sinama: List = []
            X, _Y = gorev_ozellikleri(_G())
            return np.asarray(X, float).reshape(-1)
        oz = self._dene("nefs.iki_olcek", _iki_olcek)

        def _kule():
            from .kule import kaba, kule_kur
            k = kule_kur(np.asarray(A, float))
            _y, _n, kayip = kaba(np.asarray(A, float))
            return len(k), float(kayip)
        r = self._dene("nefs.kule", _kule)
        if r is not None:
            H.kademe_sayisi, H.kabalastirma_kaybi = r

        def _rutbe():
            from ogrenme.operator import spektral_rutbe
            return int(spektral_rutbe(np.asarray(A, float)))
        H.spektral_rutbe = self._dene("ogrenme.operator", _rutbe) or 0

        def _tayf():
            from matematik.geometri import spektral_enerji
            return np.asarray(spektral_enerji(
                np.asarray(A, float).reshape(-1)[:64]), float).reshape(-1)
        tayf = self._dene("token_uzaylari.fno", _tayf)

        parcalar = [p for p in (oz, tayf) if p is not None and p.size]
        H.ozellik = (np.concatenate(parcalar) if parcalar
                     else np.zeros(1, float))
        # Tasavvurun hatası: kabalaştırmada **kaybedilen** bilgi.
        self._olc("tasavvur", 1.0 - float(np.clip(H.kabalastirma_kaybi,
                                                  0.0, 1.0)))
        self.gunluk.append(
            "2. TASAVVUR: özellik %d boyut, kule %d kademe, spektral "
            "rütbe %d, kabalaştırma kaybı %.3f"
            % (H.ozellik.size, H.kademe_sayisi, H.spektral_rutbe,
               H.kabalastirma_kaybi))
        return H

    # -- 3. MUHAKEME: Hâl → Namzet -----------------------------------
    def muhakeme(self, I: Idrak, H: Hal, derinlik: Optional[int] = None
                 ) -> Namzet:
        """Hâlden **namzet** üret -- artık şablon taramasıyla değil, dalgayla.

        **MİMARÎ DEĞİŞİKLİĞİ (padişahın TEK-ANA-KOD fermanı).** Evvelce
        burada `nefs/kaideler.py`nin ``kaide_ara``sı çağrılıyordu: elle
        yazılmış atomların ``|A|^d`` terkibinde arama. O dosya ve ona
        hizmet eden aileler **silinmiştir**.

        Yerine `main/cikarim.py`in dalgası geçer: ebat kanunu şahitlerden
        çözülür, renk ise ``softmax(W·φ)`` ağırlıklarından okunur.
        Namzet listesi bu sebeple ya boştur ya **tek** unsurludur --
        dalga bir tanedir, kütükten seçilen bir liste değil.

        ``derinlik`` artık aramanın derinliği değil **talim devridir**;
        ismi kademe cetvelinde durduğu için korunmuştur ve öğrenilir.
        """
        N = Namzet()
        if not I.ciftler:
            self._olc("muhakeme", 0.0)
            return N
        if derinlik is None:
            derinlik = int(round(self._par("kademe.muhakeme.derinlik")))

        def _ara():
            from main.cikarim import dalga_kur

            # **ÖLÇÜLEN VE DÜZELTİLEN KUSUR -- kendi açtığım kusur.**
            # Buraya tam ``dalga_kur`` aramasını bağlamıştım: hendese ×
            # D₄ × yarıçap, üstelik her aday için bırak-birini turları.
            # Halbuki bu kademe **kayıp içinde** koşar ve kayıp da
            # eniyileyici tarafından yüzlerce kere çağrılır. Ölçüldü:
            # ``main.egitim kısa`` imtihanı 17 CPU-dakikada tek satır
            # basamadı; kayıp çağrısı başına ~18 sn.
            #
            # Kademenin ihtiyacı **bir namzet**tir, en iyi namzet değil.
            # Onun için burada aramanın bütçesi kısılır: az aday, kısa
            # devir. Nihaî hüküm zaten `main/cikarim.py`de tam bütçeyle
            # verilir; buradaki ucuz hâl yalnız kademeye rey verir.
            d = dalga_kur(I.ciftler, devir=40, azami_aday=2,
                          loo_devir=20)
            if d is None:
                return []

            class _DalgaKaidesi:
                """Dalgayı kademe hattının beklediği yüze büründürür.

                ``hipotez`` ağırlık sayısıdır: dalga da serbest bilgi
                taşır ve H134'ün delil/hipotez tartısı ona da işler.
                Bunu sıfır yazmak, dalgayı ezber cezasından muaf
                tutmak olurdu.
                """
                ad = "dalga/%s/%s" % (d.hendese, d.d4)
                boy = 1
                hipotez = int(d.W.size)

                def __call__(self, g):
                    r = d.oku(g)
                    return None if r is None else r[0]

            return [_DalgaKaidesi()]
        N.kaideler = self._dene("main.main", _ara) or []
        N.aranan = len(N.kaideler)
        # **ÖLÇÜ DEĞİŞTİ (kütük H160).** Evvelce ``1 if N.kaideler``
        # yazıyordu, yani bir *faaliyet* ölçüsüydü ve **oynanabilirdi**:
        # aramayı genişlet, daima bir aday bul, ölçü 1 olsun. Ölçü artık
        # 4. kademeye devredilmiştir; muhakemenin kendi notu, bulduğu
        # adayların **ispattan sağ çıkma nispetidir** ve o nispet ancak
        # ispat koştuktan sonra bilinir. Burada yalnız aday üretilir.
        self.gunluk.append("3. MUHAKEME: %d kaide bütün gösterimleri "
                           "tutuyor (derinlik %d)" % (N.aranan, derinlik))
        return N

    # -- 4. İSPAT: Namzet → İspat ------------------------------------
    def ispat(self, I: Idrak, N: Namzet) -> Ispat:
        """Adayları **ele**: gösterime uymak delil değildir.

        İki elek beraber:

        * **bırak-birini istikrâsı** -- kaide görmediği bir gösterimi
          bilebiliyor mu (`nefs/kaideler.capraz_gecerli`),
        * **sınamaya uzanma** -- kaide sınama girdisinde bir cevap
          üretebiliyor mu; üretemiyorsa ispatı yoktur, sükût vardır.

        İkisi de kütük H136'nın hükmüdür ve ölçülerek konmuştur.
        """
        S = Ispat(list(N.kaideler))
        if not N.kaideler:
            self._olc("ispat", 0.0)
            return S
        onceki = len(S.kaideler)
        if I.girdiler:
            def _uzanan():
                return [k for k in S.kaideler
                        if all(k(g) is not None for g in I.girdiler)]
            u = self._dene("ispat.uzanma", _uzanan)
            if u is not None:
                S.kaideler = u
        S.elenen = onceki - len(S.kaideler)
        if S.elenen:
            S.gerekce = "%d kaide sınamaya uzanmıyor" % S.elenen

        def _mantik():
            # Hüküm cebri: "kaide var VE ispatı var" bir çıkarımdır ve
            # `mizan` onu **totoloji olarak** tasdik etmelidir.
            from matematik.mizan import (deg, aksiyom,
                                         hukum)
            return bool(hukum(
                aksiyom(deg("K"), deg("İ"), no=1), ne="totoloji"))
        self._dene("mizan.cikarim", _mantik)

        # **ÖLÇÜ DEĞİŞTİ (kütük H160).** Evvelce ``1 if S.kaideler``
        # idi; yine bir faaliyet ölçüsü ve yine oynanabilir. Şimdi
        # ölçülen şey **arama ile ispatın uyuşmasıdır**:
        #
        #     muhakeme notu = ayakta kalan / aranan   (aramanın isabeti)
        #     ispat    notu = ayakta kalan var mı     × o nispet
        #
        # Yani yüz aday üretip doksan dokuzu elenen bir arama, tek aday
        # üretip onu ayakta tutan aramadan **kötüdür**. Occam'ın kayba
        # giren hâli budur ve derinliği büyütmenin bedeli buradadır --
        # aksi hâlde eğitim derinliği sonuna kadar açardı.
        nispet = (float(len(S.kaideler)) / float(max(onceki, 1))
                  if onceki else 0.0)
        self._olc("muhakeme", nispet)
        self._olc("ispat", nispet if S.kaideler else 0.0)
        self.gunluk.append("4. İSPAT: %d aday → %d ayakta (%s), isabet %.2f"
                           % (onceki, len(S.kaideler),
                              S.gerekce or "eleme yok", nispet))
        return S

    # -- 5. TASDİK: İspat → Yakîn ------------------------------------
    def tasdik(self, I: Idrak, S: Ispat) -> Yakin:
        """Ayakta kalandan **mertebe** çıkar.

        Üç kaynak çarpılır ve hiçbiri elle konmuş bir katsayı değildir:

        * **istikrâ** -- `mizan/istikra.py`nin ardışıklık kaidesi:
          ``n`` gösterimden ``n``i tutan bir kaideye ne kadar güvenilir,
        * **müphemlik** -- ayakta kalan kaideler AYNI cevabı mı veriyor,
        * **tevâfuk** -- `fitrat/tevafuk.py`: iki müstakil ölçü şahidi
          (`nefs/boyut.py` ve `idrak/sekil.py`) birbirini tutuyor mu.
        """
        Y = Yakin()
        self.yakin_ilani = 0.0
        if not S.kaideler:
            # Not konmaz: ``tasdik`` artık bir ayar ölçüsüdür ve ayar
            # ancak bir iddia varken ölçülebilir (bkz. ``capraz_not``).
            return Y

        def _istikra():
            from matematik.mizan import ardisiklik_kaidesi
            n = len(I.ciftler)
            return float(ardisiklik_kaidesi(n, n))
        Y.istikra = self._dene("mizan.istikra", _istikra) or 0.5

        if I.girdiler and len(S.kaideler) > 1:
            imzalar = set()
            for k in S.kaideler[:8]:
                o = k(I.girdiler[0])
                if o is not None:
                    imzalar.add(o.tobytes() + bytes(o.shape))
            Y.muphem = len(imzalar) > 1

        # İki müstakil ölçü şahidinin teyidi (1. kademeden gelir).
        # Tek şahitle kalınca ne kadar güvenileceği **öğrenilir**.
        tam_sahit = (I.olcu is not None and I.sekil_kaidesi is not None)
        Y.tevafuk = 1.0 if tam_sahit else self._par("kademe.tasdik.tevafuk")

        def _makam():
            # **Kaynak `mizan/munazara.py`dir (kütük H215).** Evvelce
            # `nefs/murakabe.py`den alınıyordu ve o nüsha cetvelden
            # 7/13 sapıyordu (H214): 0,95'te "Yakîn" diyip ağırlığı
            # 1,0000 veriyor, yani model kesin olmadığı yerde kesinlik
            # iddia ediyordu. Artık cetvelin kendisinden okunur.
            from matematik.mizan import hukum_agirligi, makam_tayin
            p = float(Y.istikra)
            return float(hukum_agirligi(p, makam_tayin(p)))
        agirlik = self._dene("mizan.munazara", _makam)

        muphem_cezasi = self._par("kademe.tasdik.müphem")
        taban = self._par("kademe.tasdik.taban")
        Y.deger = float(np.clip(
            Y.istikra * (muphem_cezasi if Y.muphem else 1.0) * Y.tevafuk
            * (1.0 if agirlik is None
               else float(np.clip(agirlik, taban, 1.0))),
            0.0, 1.0))
        # **ÖLÇÜ DEĞİŞTİ (kütük H160): tasdik bir AYAR ölçüsüdür.**
        # Evvelce ``self._olc("tasdik", Y.deger)`` yazıyordu, yani
        # *"yakînin yüksek olsun"* diyordu -- oynanabilir ve **yanlış**:
        # bir modelin iyi olması yüksek yakîn ilan etmesi değil, ilan
        # ettiği yakînin **hakikate uyması**dır. Fazla iddia da eksik
        # iddia da kusurdur. Not ``beyan``da, bırak-birini hakikatiyle
        # yüzleştikten sonra konur (bkz. ``capraz_not``).
        self.yakin_ilani = float(Y.deger)
        self.gunluk.append(
            "5. TASDİK: istikrâ %.3f, %s, tevâfuk %.2f → yakîn %.3f"
            % (Y.istikra, "müphem" if Y.muphem else "müphem değil",
               Y.tevafuk, Y.deger))
        return Y

    # -- 6. BEYAN: Yakîn → Cevap -------------------------------------
    def beyan(self, I: Idrak, S: Ispat, Y: Yakin,
              esik: Optional[float] = None
              ) -> Optional[List[Optional[Izgara]]]:
        """Yakîn eşiği aşarsa **konuş**, aşmazsa sus.

        Sükût bir kusur değil kabiliyettir (H10/H16) -- fakat sebebi
        söylenebiliyorsa. Sebep ``günlük``tedir.

        Cevabın ölçüsü 1. kademenin kestirdiği ölçüyle **yüzleştirilir**:
        iki müstakil hesap uyuşmuyorsa konuşulmaz. Bu, beyan kapısının
        (H131) kademeli hâlidir: kelâm ancak hükümden akar.

        ``esik`` verilmezse **öğrenilir** (``kademe.beyan.eşik``). Eşiği
        oynatmak notu tek başına yükseltemez: not, konuşup konuşmamaya
        değil **bırak-birinide isabet edip etmemeye** bakar
        (``capraz_not``).
        """
        if esik is None:
            esik = self._par("kademe.beyan.eşik")
        if not S.kaideler or Y.deger < esik:
            # **Not burada KONMAZ (kütük H160).** Evvelce ``0.0``
            # yazılıyordu, yani susmak daima kusur sayılıyordu ve model
            # susmamayı öğrenirdi -- H45'te tam olarak bu ölçüldü
            # ("sükût 140 → 0; bilmeden konuşmayı öğrendi"). Sükût bir
            # kabiliyettir (H10) ve notu ``capraz_not``ta, hakikatle
            # yüzleştikten sonra konur: şek mertebesi (0,25).
            self.gunluk.append(
                "6. BEYAN: sükût -- %s"
                % ("kaide yok" if not S.kaideler
                   else "yakîn %.3f < eşik %.2f" % (Y.deger, esik)))
            return None
        k = S.kaideler[0]
        cevap = [k(g) for g in I.girdiler]
        if I.olcu is not None:
            for c in cevap:
                if c is not None and tuple(c.shape) != tuple(I.olcu):
                    self.gunluk.append(
                        "6. BEYAN: sükût -- kaide %s veriyor, ölçü "
                        "kestirimi %s diyor; iki hesap uyuşmuyor"
                        % (tuple(c.shape), tuple(I.olcu)))
                    return None
        self.gunluk.append("6. BEYAN: konuşuyorum -- kaide %s, yakîn %.3f"
                           % (getattr(k, "ad", "?"), Y.deger))
        return cevap

    # -- BIRAK-BİRİNİ NOTU: beyan ve tasdik burada tartılır -----------
    def capraz_not(self, gorev) -> None:
        """Son gösterim çifti saklanıp **hakikatle** yüzleştirilir.

        Bu, ``kademe.beyan`` ve ``kademe.tasdik`` notlarının **yegâne**
        kaynağıdır ve sebebi H90'dır: bir ölçüt kırmızı yanabilmelidir.
        *"Konuştum"* notu kırmızı yanamaz -- eşiği sıfıra çekmek onu
        daima yeşil yapar. *"Sakladığım çifti bildim mi"* notu ise
        oynanamaz: bilmek için hakikaten bilmek gerekir.

        Notlar `mizan/munazara.py`nin mertebe cetvelinden okunur::

            doğru bildi    → 1,00  yakîn
            sustu          → 0,25  şek     (iki taraf müsâvî)
            yanlış söyledi → 0,00  vehim   (mercûh taraf)

        Sıralamanın teşviki tam da matluptur: eşiği düşürüp hep konuşmak
        ancak **dörtte birden fazla** isabet ediyorsan kazandırır.

        ``tasdik`` notu bir **ayar** ölçüsüdür: ``1 − |ilan edilen yakîn
        − fiilî isabet|``. Yani yüksek yakîn ilan edip yanılmak da,
        doğru bilip düşük yakîn ilan etmek de cezalanır. Modelin
        *"bilmediğini bilmesi"* şartı (H10) burada sayıya döner.

        Gösterim çifti ikiden azsa bırak-birini kurulamaz; o zaman not
        **konmaz** (uydurulmuş bir not, notsuzluktan kötüdür).
        """
        ciftler = [(np.asarray(a), np.asarray(b))
                   for a, b in getattr(gorev, "egitim", [])]
        if len(ciftler) < 2:
            self.gunluk.append(
                "ÇAPRAZ: %d gösterim -- bırak-birini kurulamaz, not yok"
                % len(ciftler))
            return
        sakli_g, sakli_c = ciftler[-1]

        class _G:                      # saklanan çift olmadan aynı görev
            ad = getattr(gorev, "ad", "?")
            kaynak = getattr(gorev, "kaynak", "?")
            egitim = ciftler[:-1]
            sinama = [(sakli_g, sakli_c)]

        # **Özyineleme kesilir:** iç koşu kendi çapraz notunu almaz.
        ic = Kademeler(self.p)
        I2 = ic.idrak(_G())
        H2 = ic.tasavvur(I2)
        N2 = ic.muhakeme(I2, H2)
        S2 = ic.ispat(I2, N2)
        Y2 = ic.tasdik(I2, S2)
        C2 = ic.beyan(I2, S2, Y2)
        ilan = float(getattr(ic, "yakin_ilani", 0.0))

        if C2 is None or not C2 or C2[0] is None:
            hâl, isabet = "sükût", 0.0
        else:
            c = np.asarray(C2[0])
            if c.shape == sakli_c.shape and bool(np.array_equal(c, sakli_c)):
                hâl, isabet = "doğru", 1.0
            else:
                hâl, isabet = "yanlış", 0.0
        self._olc("beyan", MERTEBE_NOTU[hâl])
        # Ayar: ilan edilen yakîn ile fiilî isabetin farkı. Sükûtta
        # "isabet" tanımsızdır; o hâlde ayar da ölçülmez -- susan model
        # bir iddiada bulunmamıştır, iddiasının tutup tutmadığı
        # sorulamaz. Bu, notu uydurmamak içindir.
        if hâl != "sükût":
            self._olc("tasdik", 1.0 - abs(ilan - isabet))
        self.gunluk.append(
            "ÇAPRAZ: saklanan çift → %s (not %.2f), ilan edilen yakîn "
            "%.3f" % (hâl, MERTEBE_NOTU[hâl], ilan))


def kademeleri_kos(gorev, derinlik: Optional[int] = None,
                   esik: Optional[float] = None, p=None,
                   capraz: bool = True) -> Dict[str, object]:
    """Altı kademeyi **sırayla** koştur; her biri bir öncekini yer.

    ``p`` verilirse kademelerin sayıları o düz vektörden **öğrenilir**
    (melekelerin açılarıyla aynı defter). ``capraz=False`` bırak-birini
    notunu kapatır -- pahalıdır (boru hattı bir kere daha koşar) ve
    yalnız eğitim ölçütü için lâzımdır; kapatılamayan bir tedbirin
    faydası ölçülemez (H90).
    """
    K = Kademeler(p)
    I = K.idrak(gorev)
    H = K.tasavvur(I)
    N = K.muhakeme(I, H, derinlik)
    S = K.ispat(I, N)
    Y = K.tasdik(I, S)
    C = K.beyan(I, S, Y, esik)
    if capraz:
        K.capraz_not(gorev)
    return {"idrak": I, "hal": H, "namzet": N, "ispat": S, "yakîn": Y,
            "cevap": C, "sükût": C is None, "ölçümler": K.olcumler,
            "günlük": K.gunluk, "eksik": K.eksik}




# ════════════════════════════════════════════════════════════════════
#  nefs/mudrike.py
# ════════════════════════════════════════════════════════════════════

VAZIFE_NEVILERI: Tuple[str, ...] = ("bulmaca", "kelâm", "boş")


YAKIN_ESIGI: float = 0.5


def suz(gorev, yakin_esigi: float = YAKIN_ESIGI,
                  derinlik: int = 2, dalga: bool = False, nefs=None,
                  ne: str = "çevrim", ciftler=None, chi: int = 8,
                  tohum: int = 0) -> Dict[str, object]:
    """MESELEYİ İÇİNDEN GEÇİRMEK -- **tek terkip** (kütük H224).

    Küme: ``vazife_nevi`` + ``tesaduf_olcusu`` + ``dalga_hukmu`` +
    ``mudrike``. Dördü **tek çevrimin** adımlarıydı ve üçü yalnız
    dördüncüsü için vardı; ayrı isim taşımaları altı adımlık muhakemeyi
    dört ayrı şey gibi gösteriyordu.

    ==============  ==================================================
    ``ne``          hangi adım
    ==============  ==================================================
    ``vazife``      1. adım -- *"benden ne isteniyor?"*
    ``tesadüf``     2. adım -- *"rastgele olsa cevap bulur muydum?"*
    ``dalga``       44 melekenin bu göreve dair hükmü: sükût ve makam
    ``çevrim``      altı adımın tamamı -- ya cevap ya **sebebi yazılı**
                    sükût
    ==============  ==================================================

    **1. adım.** Bayrağa bakılmaz; **verinin şekline** bakılır. Ardışık
    girdi--çıktı çiftleri varsa bu bir bulmacadır: birileri bir dönüşüm
    gösteriyor ve aynısını istiyor. Yoksa vazife kelâmdır.

    **2. adım.** İki ölçü, ikisi de ``[0,1]``de ve ikisi de **yüksek =
    yapılı**: ``renk_yapısı`` (renk dağılımının düzgünden sapması --
    tam düzgün bir ızgarada hiçbir renk bir şey söylemez) ve
    ``şekil_bağı`` (çıktı şekli girdi şeklinden kestirilebiliyor mu).
    **Bu bir "rastgele mi" testi DEĞİLDİR ve öyle olduğu iddia
    edilmiyor**: hakikî rastgelelik ispatlanamaz (Kolmogorov). Ölçülen
    şey daha mütevazıdır -- *elimde bu ızgaradan cevap çıkarmaya
    yetecek bir düzen var mı?* Yoksa cevap aramak beyhudedir.

    **Dalga niçin var: cevaba fiilen girmeliydi, girmiyordu.** Padişahın
    çıkarımı evvelce yalnız ``beyan``ın ``argmax``ıydı; 44 melekenin
    kurduğu hüküm alanları (``sukut``, ``makam``, ``tasdik``) cevaba
    **hiç dokunmuyordu**. Kütük H92: paralel hat yasak -- dalga ile
    kaide cebri iki ayrı motor olamaz. Buradaki bağ şudur: dalga
    **kaideyi bulmaz** (onu cebir bulur), fakat **yakîni tartar**. Akış
    susmaya meyilliyse yakîn düşer, makam yüksekse yükselir. Yani dalga,
    hükmün mertebesini tayin eden meclistir -- tam da 𝒪₃₂ ve 𝒪₃₃'ün
    tarifi.
    """
    if ne == "vazife":
        ciftler = list(getattr(gorev, "egitim", []) or [])
        sinama = list(getattr(gorev, "sinama", []) or [])
        if not ciftler:
            return {"nev": "boş", "gerekçe": "gösterim çifti yok",
                    "çift": 0}
        ikili = all(hasattr(a, "shape") and hasattr(b, "shape")
                    for a, b in ciftler)
        if ikili and len(ciftler) >= 2:
            return {"nev": "bulmaca", "çift": len(ciftler),
                    "sınama": len(sinama),
                    "gerekçe": "%d gösterim çifti var: bir dönüşüm "
                               "gösteriliyor ve aynısı isteniyor"
                               % len(ciftler)}
        return {"nev": "kelâm", "çift": len(ciftler), "sınama": len(sinama),
                "gerekçe": "girdi–çıktı çifti yok; vazife söz söylemek"}

    if ne == "tesadüf":
        if not ciftler:
            return {"renk_yapısı": 0.0, "şekil_bağı": 0.0, "yapı": 0.0}
        sapmalar = []
        for a, b in ciftler:
            for g in (a, b):
                g = np.asarray(g)
                if g.size == 0:
                    continue
                _v, s = np.unique(g, return_counts=True)
                p = s / s.sum()
                k = max(len(p), 2)
                # düzgünden toplam değişinti; ``k`` renkli düzgün = 0
                sapmalar.append(0.5 * float(np.abs(p - 1.0 / k).sum())
                                + (1.0 - len(p) / 10.0) * 0.5)
        renk = float(np.clip(np.mean(sapmalar) if sapmalar else 0.0, 0, 1))

        ayni = sum(1 for a, b in ciftler if a.shape == b.shape)
        sabit = len({b.shape for _a, b in ciftler}) == 1
        kat = sum(1 for a, b in ciftler
                  if a.shape[0] and a.shape[1]
                  and (b.shape[0] % a.shape[0] == 0
                       and b.shape[1] % a.shape[1] == 0))
        n = len(ciftler)
        sekil = max(ayni / n, kat / n, 1.0 if sabit else 0.0)
        return {"renk_yapısı": renk, "şekil_bağı": float(sekil),
                "yapı": float(0.5 * renk + 0.5 * sekil)}

    if ne == "dalga":
        try:
            from .musahede import iki_olcegin_acisi
            from .musahede import ortu
            from .melekeler import QNefs
            from .zihin_durumu import MAKAM_ADLARI, QAyar

            X, Y = iki_olcegin_acisi(gorev, ne="öznitelik")
            if len(X) == 0:
                return None
            E = np.concatenate([X, Y], axis=1)
            c = ortu(gorev)
            q = (nefs or QNefs(tohum, QAyar(bag=int(chi), tohum=tohum))
                 ).idrak_et(E, tikaniklik=float(c["H1"]))
            _, ks = q._alan["sukut"]
            sk = float(np.asarray(q.y.tekil_yogunluklar(
                [q.kulli("sukut", j) for j in range(ks)]), float)[0][:, 1, 1].mean())
            from .mantik import MAKAM_MERTEBE
            P = np.atleast_1d(np.asarray(q.makam_dagilimi(), float)).ravel()
            mk = float(sum(P[i] * MAKAM_MERTEBE[ad]
                           for i, ad in enumerate(MAKAM_ADLARI)))
            return {"sukut": sk, "makam_yakini": mk}
        except Exception:                                    # noqa: BLE001
            return None

    if ne != "çevrim":
        raise ValueError("müdrike kipi bilinmiyor: %r" % (ne,))

    from .musahede import ortu

    dusunce: List[str] = []

    # --- 1. VAZİFE NEVİ
    v = suz(gorev, ne="vazife")
    dusunce.append("Benden ne isteniyor? %s → bu bir %s."
                   % (v["gerekçe"], v["nev"]))
    if v["nev"] != "bulmaca":
        return {"nev": v["nev"], "cevap": None, "sükût": True,
                "sebep": "bulmaca değil", "muhakeme": dusunce,
                "yakîn": 0.0}

    ciftler = list(gorev.egitim)

    # --- 2. TESADÜF MÜ?
    t = suz(gorev, ne="tesadüf", ciftler=ciftler)
    dusunce.append("Renkler rastgele dizilmiş gibi mi? renk yapısı %.3f, "
                   "şekil bağı %.3f → yapı %.3f."
                   % (t["renk_yapısı"], t["şekil_bağı"], t["yapı"]))
    if t["yapı"] < 0.15:
        dusunce.append("Rastgele olsaydı cevabı nereden bulacaktım? "
                       "Bulamazdım. Yapı yok; sormak beyhude.")
        return {"nev": "bulmaca", "cevap": None, "sükût": True,
                "sebep": "yapı yok", "muhakeme": dusunce, "yakîn": 0.0,
                "tesadüf": t}
    dusunce.append("Demek ki rastgele değil: bir düzen var, "
                   "o hâlde bir kaide de olmalı.")

    # --- 3. ÖRTÜ KAPANIYOR MU?  (**VETO DEĞİL, İŞARET**)
    #
    # **ÖLÇÜLEN VE DÜZELTİLEN TASARIM HATASI (kütük H132).** Bu adım
    # evvelce bir **kapı**ydı: ``H¹ ≠ 0`` ise hemen susuluyordu.
    # Ölçüldü ve ZARAR VERİYORDU: tıkanık sayılan 17 görevin **3'ünde**
    # kaide arama bir kaide buluyor ve o kaide sınamayı **tam** çözüyordu.
    # Yani veto, çözülebilen görevleri atıyordu.
    #
    # Hata mantıkîdir: benim Čech'im tam kohomoloji değil onun **sonlu
    # gölgesidir** (yamaların mahallî ŞEKİL kaidesi uyuşuyor mu). O
    # gölge kaba; şekil kaidesi ayrı düşen iki gösterim pekâlâ aynı
    # küllî kaideye tâbi olabilir.
    #
    # Doğrusu şudur ve daha kuvvetlidir: **bütün gösterimleri tutan bir
    # kaide bulmak, örtünün kapandığının kendisidir** -- küllî kesit
    # fiilen elde edilmiştir. O hâlde tıkanıklık bir veto değil, bir
    # **ihtiyat işareti**dir: yakîni düşürür, sözü kesmez.
    c = ortu(gorev)
    dusunce.append("Bütün örnekler aynı kaideye mi bakıyor? "
                   "yama %d, uyuşmayan çift %d (H¹=%d)."
                   % (c["yama"], c.get("uyuşmayan_çift", 0), c["H1"]))
    if c["H1"]:
        dusunce.append("Yamaların şekil kaidesi ayrı düşüyor. Bu beni "
                       "susturmaz -- bütün gösterimleri tutan bir kaide "
                       "bulursam örtü zaten kapanmış olur; fakat "
                       "ihtiyatlı olurum.")

    # --- 4a. ÖĞRENİLEN NAKIŞ -- şablondan ÖNCE (ferman: şablon ilgā)
    #
    # **Niçin şablondan önce.** Padişahın fermanı şuydu: *"kaide.py
    # içindeki sabit kütükler ilgā edilmiştir; Python for döngüleriyle
    # şablon tarama ilkelliği yasaklanmıştır."* İtham doğruydu:
    # ``kaide.py``nin 705. satırı ``for e in EBAT_KUTUGU for r in
    # RENK_KUTUGU`` idi, yani 11×7 el yazması ihtimalin taranması.
    #
    # `nefs/nakis.py` o kütüğün yerine geçer ve hiçbir şablon taşımaz:
    # ebat kanunu ``aH·H+bH`` şahitlerden **çözülür**, renk ise izafî
    # komşuluk bağlamından **öğrenilir**. Şablon sayısı sabit 77 idi;
    # öğrenilen bağlam sayısı görevden göreve değişir.
    #
    # **ÖLÇÜLDÜ, İDDİA EDİLMİYOR.** Nakış tek başına training'de 400
    # görevin 6'sını TAM çözer, evaluation'da 0'ını. Evaluation'da
    # 120 görevin 74'ünde hiçbir soyutlama kademesi fonksiyonel
    # değildir: cevap yerel pencerenin dışına bağlıdır. Bu bir arıza
    # değil, yerel nakşın **ilân edilmiş haddi**dir -- ve şablon
    # kütüğünün oradaki hâli de sükûttur.
    try:
        from main.cikarim import padisah as _padisah
        dw = _padisah(gorev)
    except Exception as exc:                             # noqa: BLE001
        dw = {"sükût": True, "sebep": "dalga hatası: %s" % type(exc).__name__}
    if not dw.get("sükût"):
        n = len(ciftler)
        yakin = float(ardisiklik_kaidesi(n, n))
        if c["H1"]:
            yakin *= 0.8
        # **Güven yakîne fiilen giriyor.** Dalga her hücrede bir olasılık
        # verir; ortalama en yüksek olasılık düşükse dalga kararsızdır ve
        # bu saklanmaz. Süs bir alan değil, hükmü değiştiren bir çarpandır.
        yakin *= float(np.clip(dw.get("güven", 1.0), 0.3, 1.0))
        dusunce.append(
            "Hiçbir şablona bakmadan, şahitlerden bir dalga öğrendim: "
            "ebat kanunu %s, taşıyıcı D₄=%s, %d ağırlık; şahit isabeti "
            "%.4f, sınamada güven %.4f, zırh cezası %.4f."
            % (dw["hendese"], dw["d4"], dw["ağırlık"],
               dw["şahit_isabeti"], dw["güven"], dw["zırh"]))
        if yakin >= yakin_esigi:
            dusunce.append("Yakînim %s; öğrendiğim ağırlıklardan "
                           "konuşuyorum." % mertebe_adi(yakin))
            return {"nev": "bulmaca", "cevap": list(dw["cevap"]),
                    "sükût": False, "sebep": None, "muhakeme": dusunce,
                    "yakîn": yakin, "kaide": "dalga/%s" % dw["d4"],
                    "kaide_sayısı": 1, "müphem": False, "tesadüf": t,
                    "kaynak": "dalga"}
        dusunce.append("Dalga kuruldu fakat yakînim (%.3f) eşiğin altında; "
                       "kademelere devam ediyorum." % yakin)
    else:
        dusunce.append("Dalga tutmadı: %s." % dw.get("sebep"))

    # --- 4. KÂİDE -- artık **kademelerden** geliyor
    #
    # **MİMARÎ DEĞİŞİKLİĞİ.** Evvelce burada doğrudan ``kaide_ara``
    # çağrılıyordu; yani çıkarım kendi boru hattını kuruyor, eğitim
    # başka bir şey eniyiliyordu. İkisinin ayrı düşmesi, eğitimin
    # öğrettiği şeyin çıkarımda kullanılmaması demektir.
    #
    # Şimdi ikisi de `nefs/kademeler.py`nin **aynı** altı kademesini
    # koşturur: idrak → tasavvur → muhakeme → ispat → tasdik → beyan.
    # Kademelerin ölçüleri `nefs/kulli_kayip.py` yoluyla eğitime de
    # girer; yani bu boru hattı hem konuşur hem öğrenir.
    kad = kademeleri_kos(gorev, derinlik=derinlik, esik=yakin_esigi)
    dusunce += kad["günlük"]
    K = list(kad["ispat"].kaideler)
    kademe_olcumleri = kad["ölçümler"]
    if kad["eksik"]:
        dusunce.append("Kademelerde düşen uzuv: %s"
                       % ", ".join(sorted(kad["eksik"])))
    if not K:
        dusunce.append("Hiçbir kaide bütün gösterimleri tutmuyor. "
                       "Tutmayan bir kaideyle cevap vermek, tam eşleşme "
                       "ölçütünü sahte kılardı.")
        return {"nev": "bulmaca", "cevap": None, "sükût": True,
                "sebep": "kaide bulunamadı", "muhakeme": dusunce,
                "yakîn": 0.0, "tesadüf": t,
                "ölçümler": kademe_olcumleri}

    # **SÖZ VEREBİLİR MİYİM?** Bir kaide gösterimleri tutup sınama
    # girdisinde ``None`` dönebilir (görülmemiş bağlam). Evvelce ilk
    # kaide alınır ve ``None`` cevap olarak **söylenirdi**; ölçüldü:
    # ``0ca9ddb6`` ve ``025d127b`` böyle "konuşup boş" çıkıyordu. Susmak
    # kabiliyettir, boş konuşmak değil. Onun için cevap üretebilen ilk
    # kaide öne alınır; hiçbiri üretemiyorsa sükût **sebebiyle** edilir.
    girdiler_on = [np.asarray(a, np.int64)
                   for a, _ in getattr(gorev, "sinama", [])] or []
    if girdiler_on:
        konusabilen = [k for k in K
                       if all(k(g) is not None for g in girdiler_on)]
        if not konusabilen:
            dusunce.append(
                "%d kaide gösterimleri tutuyor fakat hiçbiri sınama "
                "girdisinde cevap üretmiyor -- görmediğim bir hâl var. "
                "Ezberlediğim tablo oraya uzanmıyor; susuyorum." % len(K))
            return {"nev": "bulmaca", "cevap": None, "sükût": True,
                    "sebep": "kaide sınamaya uzanmıyor",
                    "muhakeme": dusunce, "yakîn": 0.0, "tesadüf": t}
        if len(konusabilen) < len(K):
            dusunce.append("%d kaidenin %d'i sınama girdisinde cevap "
                           "üretebiliyor; yalnız onları tartıyorum."
                           % (len(K), len(konusabilen)))
        K = konusabilen

    # --- 5. YAKÎN
    n = len(ciftler)
    istikra = float(ardisiklik_kaidesi(n, n))
    girdiler = [a for a, _ in getattr(gorev, "sinama", [])] or []
    muphem = False
    if girdiler and len(K) > 1:
        for g in girdiler:
            cevaplar = []
            for k in K[:8]:
                r = k(np.asarray(g, np.int64))
                cevaplar.append(None if r is None else r.tobytes()
                                + bytes(r.shape))
            if len({c for c in cevaplar if c is not None}) > 1:
                muphem = True
                break
    # **DELİL / HİPOTEZ ORANI (kütük H134).** Öğrenilen bir tablo,
    # delilden büyükse istikrâ değil ezberdir. Delil = gösterimlerde
    # görülen hücre sayısı; hipotez = tablonun girdi sayısı. Oran
    # küçüldükçe yakîn düşer ve model susar.
    delil = sum(int(np.asarray(a).size) for a, _ in ciftler)
    hip = int(getattr(K[0], "hipotez", 0))
    kanit = 1.0 if hip <= 0 else float(
        np.clip(delil / (4.0 * hip), 0.25, 1.0))
    # Tıkanıklık **ihtiyat** olarak girer: sözü kesmez, yakîni düşürür.
    ihtiyat = 0.8 if c["H1"] else 1.0
    yakin = istikra * (0.5 if muphem else 1.0) * ihtiyat * kanit

    # **MECLİS.** Kod tabanının bütün modülleri burada padişahın
    # hükmüne fiilen girer (`nefs/meclis.py`). İki mertebe ayrı ayrı
    # hesaplanır -- görevin verisiyle hesap yapan **uzuv**lar ve kendi
    # varsayımını sınayan **hakem**ler -- ve neticeleri tek bir ihtiyat
    # çarpanına iner. Bu, "içe aktardım" demenin değil, modülün hükmü
    # **değiştirmesi**nin yeridir: bir modülün hesabı bozulursa buradan
    # yakîn düşer ve padişah susar.
    try:
        from .meclis import meclis
        mec = meclis(ciftler, girdiler)
        yakin *= float(mec["ihtiyat"])
        dusunce.append(
            "Meclisi topluyorum: %d uzuv (rey %.3f), %d hakem (rey %.3f), "
            "%d düşen → ihtiyat %.3f, yakînim %.3f."
            % (len(mec["uzuv_rey"]), mec["uzuv"], len(mec["hakem_rey"]),
               mec["hakem"], len(mec["eksik"]), mec["ihtiyat"], yakin))
        # **Ölçü hükmü uzuvdan geliyor**: `nefs/boyut.py` çıktı ölçüsünü
        # kestirdiyse ve kaidenin verdiği cevap ona uymuyorsa, iki
        # müstakil hesap birbirini yalanlıyor demektir; yakîn düşer.
        kes = mec["bilgi"].get("kestirilen_ölçü")
        if kes is not None and girdiler:
            deneme = K[0](np.asarray(girdiler[0], np.int64))
            if deneme is not None and tuple(deneme.shape) != tuple(kes):
                yakin *= 0.5
                dusunce.append(
                    "Fakat ölçü kestirimi %s diyor, kaidem %s veriyor -- "
                    "iki müstakil hesap uyuşmuyor; yakînimi yarıya "
                    "indiriyorum." % (tuple(kes), tuple(deneme.shape)))
    except Exception as exc:                             # noqa: BLE001
        dusunce.append("Meclis toplanamadı (%s); ihtiyatsız devam "
                       "ediyorum." % type(exc).__name__)
    if hip > 0:
        dusunce.append("Bu kaide %d girdilik bir tablo öğrendi; "
                       "delilim %d hücre → delil/hipotez sağlamlığı %.3f."
                       % (hip, delil, kanit))
    # **DALGA HÜKMÜ.** 41 meleke kaideyi bulmaz fakat yakîni tartar
    # (𝒪₃₂ Şek-Zan-Yakîn, 𝒪₃₃ Muhakeme). Akış susmaya meyilliyse yakîn
    # düşer. Bu, dalganın cevaba FİİLEN girdiği yerdir; evvelce hiç
    # girmiyordu ve o bir paralel hat kusuruydu (H92).
    dh = (suz(gorev, ne="dalga", nefs=nefs)
          if dalga else None)
    if dh is not None:
        yakin *= float(np.clip(1.0 - 0.5 * dh["sukut"], 0.3, 1.0))
        dusunce.append("Dalganın hükmü: sükût eğilimi %.3f, makam yakîni "
                       "%.3f → yakînim %.3f'e ayarlandı."
                       % (dh["sukut"], dh["makam_yakini"], yakin))
    dusunce.append("Yakînim ne mertebede? %d gösterimden ardışıklık "
                   "kaidesi %.3f; tutan kaideler %s%s → yakîn %.3f (%s)."
                   % (n, istikra,
                      "AYRI cevaplar veriyor (müphem)" if muphem
                      else "aynı cevabı veriyor",
                      "; örtü tıkanıklığı ihtiyatı" if c["H1"] else "",
                      yakin, mertebe_adi(yakin)))
    if yakin < yakin_esigi:
        dusunce.append("Yakîn eşiğin (%.2f) altında; susuyorum."
                       % yakin_esigi)
        return {"nev": "bulmaca", "cevap": None, "sükût": True,
                "sebep": "yakîn eşiğin altında", "muhakeme": dusunce,
                "yakîn": yakin, "tesadüf": t, "kaide": K[0].ad}

    # --- 6. BEYAN
    kural = K[0]
    cevap = [kural(np.asarray(g, np.int64)) for g in girdiler]
    dusunce.append("Kaide: %s. Yakînim %s; konuşuyorum."
                   % (kural.ad, mertebe_adi(yakin)))
    return {"nev": "bulmaca", "cevap": cevap, "sükût": False,
            "sebep": None, "muhakeme": dusunce, "yakîn": yakin,
            "kaide": kural.ad, "kaide_sayısı": len(K),
            "müphem": muphem, "tesadüf": t}




# ════════════════════════════════════════════════════════════════════
#  nefs/tesir.py
# ════════════════════════════════════════════════════════════════════

@dataclass
class Iz:
    """Bir melekenin bir koşudaki izi."""
    sira: int
    no: int
    ad: str
    sure_ms: float
    yazdigi: Tuple[str, ...]
    degisen: Tuple[str, ...]      # fiilen DEĞİŞEN alanlar (bildirdiği değil)


def _parmak_izi(d: Durum, alan: str) -> Any:
    """Bir alanın karşılaştırılabilir özeti (şerhi ``eksilt``de)."""
    v = getattr(d, alan, None)
    if v is None:
        return None
    if isinstance(v, np.ndarray):
        return (v.shape, float(np.sum(v * v)), float(np.sum(v)))
    if isinstance(v, (int, float, bool, str)):
        return v
    if isinstance(v, (list, tuple)):
        return repr(v)[:400]
    if isinstance(v, dict):
        return repr(sorted(v.items(), key=lambda kv: kv[0]))[:400]
    return repr(v)[:400]


_IZLENEN = ("X", "Z_hayal", "H_hayal", "Z_muhayyile", "sira", "U_k", "D",
            "S", "S_kebir", "K_vahime", "mu_mana", "parcalar",
            "tekil_degerler", "tenakuz", "G", "G_kebir", "Q_sual",
            "A_neden", "burhan", "M", "T", "P_idrak", "makam", "N",
            "sahitler", "kaideler", "kaide", "nakz", "sahit_agirliklari",
            "muteber_sahit", "tevafuk", "ispat", "hukum", "sukut",
            "tezat_kutbu", "w_kesit")


def eksilt(E=None, tohum: int = 0, sira: Sequence[int] = AKIS,
                    ne: str = "tesir", d: "Durum" = None,
                    sonuc: Sequence["Tesir"] = (), m: int = 4, t: int = 6,
                    d_in: int = 12, bozuk: Optional[int] = None):
    """BU MELEKE DÜŞSE NE DEĞİŞİR -- **tek terkip** (kütük H224).

    Küme: ``icra_izi`` + ``netice_ozeti`` + ``tesir_olc`` +
    ``tesir_tablosu`` + ``yapili_girdi``. Beşi tek amelin durakları idi:
    kurallı bir girdi hazırla, akışı koştur ve her adımda fiilen ne
    değiştiğini kaydet, neticenin karşılaştırılabilir yüzünü çıkar, her
    melekeyi sırayla düşürüp temelle yüzleştir, ve neticeyi tablola.

    ==============  ==================================================
    ``ne``          döndürdüğü
    ==============  ==================================================
    ``girdi``       şahitli, **kurallı** girdi -- rastgele gürültü değil
    ``iz``          ``(Durum, [Iz])`` -- adım adım fiilen ne değişti
    ``netice``      neticenin karşılaştırılabilir bütün yüzleri
    ``tesir``       ``(temel, [Tesir])`` -- her melekeyi düşürüp ölç
    ``tablo``       tesirli / tesirsiz / yapısal ayrımı
    ==============  ==================================================

    **Bildirilen ``yazar`` ile fiilen değişen alanın farkı mühimdir:**
    sözleşme "yazacağım" der, iz "yazdı" der. İkisi ayrıştığında ya
    sözleşme dar ya meleke gizli tesir ediyor demektir.

    **Girdi niçin kurallı.** Rastgele girdide bazı melekelerin yapacak
    işi yoktur (çelişki yok, kaide yok) ve "tesirsiz" ölçülürler. Bu,
    onların boş olduğunu değil, ölçünün sorduğu sualin o girdide
    anlamsız olduğunu gösterir; onun için hassasiyet iki girdide birden
    ölçülür. ``bozuk`` verilirse o şahit başka bir kurala tâbidir ve
    nakz onu yakalamalıdır.
    """
    if ne == "girdi":
        rng = np.random.default_rng(tohum)
        R = np.linalg.qr(rng.normal(size=(d_in, d_in)))[0]
        R2 = np.linalg.qr(rng.normal(size=(d_in, d_in)))[0]
        bloklar = []
        for k in range(m):
            G = rng.normal(size=(t, d_in))
            C = G @ (R2 if k == bozuk else R).T
            bloklar.append(np.vstack([G, C + 6.0]) + 60.0 * k)
        return np.vstack(bloklar)

    def netice(dd):
        N = dd.N if dd.N is not None else np.zeros(1)
        return {
            "N": np.asarray(N, float).copy(),
            "makam": dd.makam,
            "sukut": bool(dd.sukut),
            "nakz": tuple(dd.nakz) if dd.nakz is not None else None,
            "mühür": bool((dd.hukum or {}).get("mühür", False)),
            "T": float(dd.T),
            "P_idrak": float(dd.P_idrak),
        }

    if ne == "netice":
        return netice(d)

    if ne == "tablo":
        tesirsiz = [x.no for x in sonuc if not x.tesirli]
        yapisal = [x.no for x in sonuc if x.kirildi]
        tesirli = [x.no for x in sonuc if x.tesirli and not x.kirildi]
        return {"toplam": len(sonuc), "tesirsiz": tesirsiz,
                "yapısal": yapisal, "tesirli": tesirli,
                "tesirsiz_oranı": len(tesirsiz) / max(len(sonuc), 1)}

    if ne == "iz":
        nefs = Nefs(tohum, sira)
        dd = Durum.kur(E)
        izler: List[Iz] = []
        onceki = {a: _parmak_izi(dd, a) for a in _IZLENEN}
        for yer, no in enumerate(sira):
            mm = nefs.s[no]
            t0 = time.perf_counter()
            mm.kosu(dd, nefs.p)
            dt = (time.perf_counter() - t0) * 1e3
            simdi = {a: _parmak_izi(dd, a) for a in _IZLENEN}
            degisen = tuple(a for a in _IZLENEN if simdi[a] != onceki[a])
            onceki = simdi
            izler.append(Iz(yer, no, mm.ad, dt, tuple(mm.yazar), degisen))
        return dd, izler

    if ne != "tesir":
        raise ValueError("tesir ölçüsünün kipi bilinmiyor: %r" % (ne,))

    nefs = Nefs(tohum)
    temel = netice(nefs.idrak_et(E))
    cikti: List[Tesir] = []
    for mm in melekeler():
        eksik = tuple(x for x in AKIS if x != mm.no)
        tt = Tesir(no=mm.no, ad=mm.ad)
        try:
            dd = Nefs(tohum, eksik).idrak_et(E)
        except Exception as e:                    # sözleşme denetimi vs.
            tt.kirildi = True
            tt.sebep = "%s: %s" % (type(e).__name__, str(e)[:90])
            cikti.append(tt)
            continue
        o = netice(dd)
        a, b = temel["N"], o["N"]
        if a.shape == b.shape:
            tt.dN = float(np.linalg.norm(a - b))
        else:
            tt.dN = float(np.linalg.norm(a) + np.linalg.norm(b))
        tt.makam_degisti = o["makam"] != temel["makam"]
        tt.sukut_degisti = o["sukut"] != temel["sukut"]
        tt.nakz_degisti = o["nakz"] != temel["nakz"]
        tt.muhur_degisti = o["mühür"] != temel["mühür"]
        tt.dP = abs(o["P_idrak"] - temel["P_idrak"])
        cikti.append(tt)
    return temel, cikti


@dataclass
class Tesir:
    """Bir melekenin düşürülmesinin neticeye tesiri."""
    no: int
    ad: str
    kirildi: bool = False
    sebep: str = ""
    dN: float = 0.0
    makam_degisti: bool = False
    sukut_degisti: bool = False
    nakz_degisti: bool = False
    muhur_degisti: bool = False
    dP: float = 0.0

    @property
    def tesirli(self) -> bool:
        if self.kirildi:
            return True         # yapısal zaruret de bir tesirdir
        return (self.dN > 1e-12 or self.makam_degisti or self.sukut_degisti
                or self.nakz_degisti or self.muhur_degisti or self.dP > 1e-12)

    @property
    def hal(self) -> str:
        if self.kirildi:
            return "YAPISAL"
        return "tesirli" if self.tesirli else "TESİRSİZ"




# ════════════════════════════════════════════════════════════════════
#  nefs/kulli_kayip.py
# ════════════════════════════════════════════════════════════════════

VERI_ORNEK: int = 8


def bolge_degeri(q, ad: str) -> Optional[float]:
    """BİR BÖLGEDEN NE OKUNUYOR -- **tek terkip** (kütük H224).

    Küme: ``_veri_yuvalari`` + ``bolge_degeri``. Birincisi yalnız
    ikincisi için vardı ve tek satırlık bir liste kuruyordu.

    Bir bölgenin zayıf okuması, ``[0,1]``. Küllî alanlar ``alan_degeri``
    ile okunur -- tek kübitlik zayıf ölçüm. ``yerel`` ve ``veri`` için
    POVM dağılımının birleşimi alınır; ikisi de bir "hüküm alanı" değil
    bir **kübit kümesidir**, o yüzden tek bir sayı ancak birleştirmeyle
    doğar ve bu açıkça yazılır.

    Yığın ekseni **yumuşak asgarî** ile birleşir, ortalamayla değil:
    bir yığında tek bir veride düşen parametre yakîn sayılamaz.
    """
    try:
        if ad == "yerel":
            y = q.yereller()
            if not y:
                return None
            return zayif_halka(q.povm(y))
        if ad == "veri":
            y = [q.veri(i, j) for i in range(q.n_satir)
                 for j in range(q.ayar.satir_kubiti)][:VERI_ORNEK]
            if not y:
                return None
            return zayif_halka(q.povm(y))
        return zayif_halka(q.alan_degeri(ad))
    except Exception:                                    # noqa: BLE001
        return None


def olcumlu_idrak(nefs, E: np.ndarray, meleke_olcumu: bool = True,
                  sinif_olcumu: bool = True):
    """Akışı koştur ve **her melekeden sonra** onun alanını oku.

    ``QNefs.idrak_et``in aynısını yapar; farkı, melekeler arasında
    eğitim ölçütü için zayıf okuma almasıdır. Akışın kendisi bundan
    haberdar değildir ve kararları değişmez (H31 yerinde durur).

    Dönen: ``(q, okumalar, dS)``:

    * ``okumalar[no][bölge]`` -- melekenin ilan ettiği alanın okuması,
    * ``dS[no]`` -- melekenin dolaşıklığa tesiri (`nefs/nizam.py`),
      sınıf taahhüdünün yüzleştirildiği ölçü.
    """
    from ogrenme.optimize import gaye_kos
    from .melekeler import bec_faz_kilidi
    from .zihin_durumu import QYazmac
    from .zirh import vicdan

    E = np.asarray(E, float)
    B = E.shape[0] if E.ndim == 3 else 1
    ayar = nefs.ayar
    if B != ayar.yigin:
        from dataclasses import replace
        ayar = replace(ayar, yigin=B)
    q = QYazmac(E.shape[-2], ayar)
    q.kodla(E)
    q.superpozisyon()
    q.mera()

    def _entropi() -> float:
        try:
            return float(np.mean(np.asarray(q.olcumler()["entropi"], float)))
        except Exception:                                # noqa: BLE001
            return float("nan")

    okumalar: Dict[int, Dict[str, float]] = {}
    #: ``ΔS`` -- melekenin dolaşıklığa tesiri (`nefs/nizam.py`).
    dS: Dict[int, float] = {}
    for no in nefs.sira:
        onceki_sadakat = (float(q.y.sadakat_log())
                          if meleke_olcumu else 0.0)
        S_once = _entropi() if sinif_olcumu else 0.0
        nefs.s[no].kosu(q, nefs.p)
        if nefs.sadakat:
            vicdan(q, nefs.p, ne="işaret")
        if sinif_olcumu:
            fark = _entropi() - S_once
            # Aynı meleke sırada iki kere geçebilir; tesirleri toplanır.
            dS[int(no)] = dS.get(int(no), 0.0) + (
                0.0 if fark != fark else fark)
        if meleke_olcumu:
            ilan = SOZLESME.get(int(no), ((), ""))[0]
            d: Dict[str, float] = {}
            for ad in ilan:
                if ad in ("veri", "yerel"):
                    # **VERİ BİR HÜKÜM ALANI DEĞİLDİR.** Evvelce buranın
                    # POVM ortalaması alınıp "büyüğü iyi" sayılıyordu ve
                    # ÖLÇÜLDÜ: ``𝒪₁.veri`` her parametrede tam ``0,000``
                    # çıkıyor, yani doymuş bir en-kötü uzuv olarak
                    # yumuşak azamîyi tek başına ele geçiriyor ve kaybı
                    # yine sabitliyordu. Kusur melekede değil benim
                    # ölçümümdeydi: veri kübitleri girdiyi taşır, hüküm
                    # taşımaz; onlara "büyüğü iyi" demek keyfîdir.
                    #
                    # Doğru ölçü melekenin **ne kadar bilgi attığı**dır:
                    # kesme. Yönü tartışmasızdır (az atmak iyidir),
                    # parametreye bağlıdır, ve her meleke için tanımlıdır.
                    continue
                v = bolge_degeri(q, ad)
                if v is not None:
                    d[ad] = v
            # Veri/yerel ilan eden melekeler **kesmeden** ölçülür: o
            # geçişte sadakatin ne kadar düştüğü. Böylece 41 melekenin
            # hepsi ölçülür ve hiçbiri doymuş bir sabit değildir.
            # **LOG UZAYINDA**: ``sadakat()`` çarpımsaldır ve 1814
            # kapıdan sonra ``4e-12``ye iner, yani oranı da manasızlaşır.
            # Melekenin o geçişte attığı nispî ağırlık log farkındadır.
            # Log farkını ``[0,1]``e **kırpmak** yanlıştı ve ölçüldü:
            # düşüş çoğu melekede 1'i aştığı için kırpma doyuyor,
            # ``𝒪₁.kesme`` sabit ``0`` çıkıyor ve yumuşak azamîyi yine
            # tek başına ele geçiriyordu. Kırpma bir had değil, haddi
            # olmayan bir sayıyı hadde zorlamaktır.
            #
            # Doğru hâl melekenin **kendi tuttuğu kesir**dir:
            # ``exp(−düşüş) ∈ (0,1]``. Hiçbir keyfî üst sınır gerekmez,
            # doymaz, ve yönü tartışmasızdır -- çok tutan iyidir.
            dus = max(0.0, onceki_sadakat - float(q.y.sadakat_log()))
            d["kesme"] = float(np.exp(-dus))
            # Aynı meleke sırada iki kere geçebilir (QAKIS'te 13 böyle);
            # son okuma değil **en kötüsü** tutulur: bir melekenin iki
            # geçişinden birinde bozması, bozmadığı manasına gelmez.
            eski = okumalar.get(int(no))
            okumalar[int(no)] = d if eski is None else {
                k: min(v, eski.get(k, v)) for k, v in d.items()}
    if nefs.sadakat:
        q.iz.kesme += vicdan(q, ne="usul")
    if nefs.gaye:
        q.iz.kesme += gaye_kos(q, nefs.p)
    if nefs.sadakat:
        vicdan(q, ne="intaç")
    bec_faz_kilidi(q)
    q.iz.kesme_hakiki = float(max(0.0, 1.0 - q.y.sadakat()))
    q.y.normalize()
    return q, okumalar, dS


def meleke_olcumleri(okumalar: Dict[int, Dict[str, float]]
                     ) -> List[Olcum]:
    """41 melekenin hatasını ``Olcum`` listesine çevir.

    Her meleke, **ilan ettiği her bölge için** ayrı bir ölçü verir ve
    ağırlığı bölge sayısına bölünür: dört bölge ilan eden bir meleke,
    tek bölge ilan edenden dört kat ağır basmaz. Aksi hâlde sözleşmeyi
    geniş yazmak, kayıpta ağırlık kazanmanın yolu olurdu.
    """
    out: List[Olcum] = []
    for no, d in sorted(okumalar.items()):
        if not d:
            continue
        w = 1.0 / float(len(d))
        for ad, v in sorted(d.items()):
            # ``kesme`` artık **tutulan kesir**tir: büyüğü iyi.
            if ad == "kesme":
                S = OlcuUzayi("tutulan_kesir", 0.0, 1.0, True)
            else:
                S = UZAYLAR.get(ad)
            if S is None:
                S = OlcuUzayi(ad, 0.0, 1.0, True, tahmini_ust=True)
            out.append(Olcum("𝒪%d.%s" % (no, ad), float(v), S, w))
    return out


def kulli_kayip(nefs, veri: Sequence[Tuple[List[int], int]],
                p: Optional[np.ndarray] = None, sozluk: int = 16,
                meleke_olcumu: bool = True,
                kademe_olcumleri: Optional[Sequence[Olcum]] = None,
                kademe_gorevleri: Optional[Sequence] = None,
                azami_veri: int = 0) -> Dict[str, object]:
    """``ℒ`` -- bütün uzuvların hatası, funktörle müşterek uzayda.

    Toplananlar:

    1. **41 meleke**, her biri kendi sözleşmesine göre (yukarıdaki şerh),
    2. **küllî alanlar** -- akış sonundaki tenakuz/nakz/tasdik/sükût…,
    3. **kesme** -- dalganın attığı bilgi (``kesme_hakiki``),
    4. **kademeler** -- verilirse altı kademenin kendi ölçüleri
       (`nefs/kademeler.py`).

    Hepsi ``nefs/olcu.py``nin funktörüyle mertebeye iner ve orada
    toplanır. Elle konmuş ``0,25``/``0,1`` katsayıları **yoktur**:
    uzaylar arası intibak artık funktörle sağlanıyor.
    """
    from .qegitim import belirtecleri_kodla

    if p is not None:
        nefs.yukle(p)
    if not len(veri):
        return {"kayıp": 0.0, "uzuv": 0}

    # **MELEKE ÖLÇÜMÜ KAÇ VERİDE YAPILIR.** Ölçüldü: dört veri
    # örneğinde bir kayıp çağrısı 7,7 sn sürüyor ve bunun tamamına
    # yakını meleke başına zayıf okumalardır (41 meleke × ~2 alan ×
    # veri sayısı). Melekenin hatası **melekeye** aittir, veriye
    # değil; o hâlde ilk ``meleke_ornegi`` veride ölçmek yeter ve
    # kalan veriler yine küllî alan ile kesme ölçüsünü verir.
    # Bu bir kısaltmadır ve gizlenmiyor: ``meleke_ornegi`` büyütülünce
    # ölçüm zenginleşir, bedeli de doğrusal artar.
    # =================================================================
    # VERİ **YIĞIN HÂLİNDE** KOŞULUR (kütük H151)
    # =================================================================
    #
    # Evvelce veri örnekleri tek tek döngüyle akıştan geçiriliyordu.
    # Hâlbuki `kuantum/yazmac.py` yazmacı zaten **yığın** taşıyor
    # (``yigin`` ekseni) ve ``QNefs.idrak_et`` ``(B, n, d)`` şeklinde
    # girdi kabul ediyor. Ölçüldü (CPU, χ=16, aynı donanım):
    #
    #     B= 1  yığın  1,01 sn   tek tek  1,01 sn   hızlanma 1,00×
    #     B= 4  yığın  2,71 sn   tek tek  4,05 sn   hızlanma 1,49×
    #     B=16  yığın 10,00 sn   tek tek 16,09 sn   hızlanma 1,61×
    #     B=32  yığın 19,47 sn   tek tek 32,86 sn   hızlanma 1,69×
    #
    # Örnek başına maliyet 1,014 → 0,608 sn'ye iniyor ve B büyüdükçe
    # düşmeye devam ediyor: kapı kurulumu, MPO inşası ve süpürme yığın
    # üyeleri arasında **paylaşılıyor**. Yani B'yi büyütmek yalnız daha
    # çok veri işlemek değil, **veri başına daha ucuz** işlemektir --
    # kullanıcı hükmü buydu ve ölçüm onu doğruladı.
    #
    # Meleke ölçümü yığının tamamında **bir kere** alınır: melekenin
    # hatası melekeye aittir, tek bir veri örneğine değil. Böylece
    # ``meleke_ornegi`` kısaltmasına da lüzum kalmadı.
    veri = list(veri)
    if azami_veri:
        veri = veri[:int(azami_veri)]
    hepsi: List[Olcum] = []
    E_yigin = np.stack([belirtecleri_kodla(b, nefs.ayar.satir_kubiti,
                                           sozluk) for b, _h in veri])
    q, okumalar, dS = olcumlu_idrak(nefs, E_yigin, meleke_olcumu)
    if meleke_olcumu:
        hepsi += meleke_olcumleri(okumalar)
    # **SINIF TAAHHÜDÜ ÖĞRENİLEBİLİR KAYBA GİRER** (`nefs/nizam.py`).
    # Meleke "çözücüyüm" dediği için değil, FİİLEN çözdüğü için
    # çözücü olmalıdır. ΔS açılarla değişir, yani bu ölçü hakikaten
    # öğrenilebilir -- kesme gibi yapısal değil.
    if dS:
        from .zirh import taahhude_yuzlestir
        from .melekeler import qsicil
        sic = qsicil()
        for no, d in sorted(dS.items()):
            m = sic.get(int(no))
            if m is None:
                continue
            hepsi.append(Olcum(
                "𝒪%d.nizam" % no, 1.0 - taahhude_yuzlestir(m.SINIF, d),
                OlcuUzayi("nizam_uyumu", 0.0, 1.0, True)))
    o = q.olcumler()
    for ad, _kac in q.ayar.kulli_alanlar:
        if ad in o and ad in UZAYLAR:
            hepsi.append(Olcum("alan.%s" % ad,
                               zayif_halka(o[ad]), UZAYLAR[ad]))
    # **Kapı başına** tutulan kesir (bkz. `kuantum/yazmac.py::sadakat`).
    hepsi.append(Olcum(
        "kesme", float(q.y.sadakat_kapi_basina(max(q.iz.kapi, 1))),
        OlcuUzayi("kapı_başına_sadakat", 0.0, 1.0, True)))
    # =================================================================
    # KADEME ÖLÇÜLERİ DE KAYBA GİRMİYOR (kütük H156)
    # =================================================================
    #
    # H154'ün aynı hatası başka yerde tekrarlanmıştı. Altı kademe
    # (`nefs/kademeler.py`) **dalga parametrelerine hiç bağlı
    # değildir**: idrak nesne ayrıştırır, muhakeme ``kaide_ara``
    # koşturur, tasdik istikrâ hesaplar -- hiçbiri melekelerin
    # açılarını kullanmaz. O hâlde kademe ölçüleri her parametrede
    # **aynı sayıdır**.
    #
    # Ölçüldü (5 parametre, aynı kayıp):
    #
    #     kademesiz : V(p₀)=0,5758   yayılım 0,2176
    #     kademeli  : V(p₀)=0,7978   yayılım 0,0118   ← 18 kat seyreltme
    #
    # 44 uzvun 24'ü sabitse, kaybın yarısından fazlası kımıldamıyor
    # demektir; yumuşak azamî de o sabit tabana oturuyor ve arama
    # körleşiyor.
    #
    # =================================================================
    # VE BU BORÇ KAPANDI (kütük H160): kademeler artık PARAMETRELİ
    # =================================================================
    #
    # H156'nın hükmü şuydu: *"Kademelerin eğitilebilmesi için kendi
    # parametrelerinin olması ve o parametrelerin `nefs/talim.py`ye
    # verilmesi gerekir -- henüz yok ve iddia edilmiyor."*
    #
    # Artık var. `nefs/kademeler.py` altı kademenin elle konmuş
    # sayılarını (beyan eşiği, müphemlik cezası, tevâfuk, muhakeme
    # derinliği, nesne eşiği, hüküm tabanı) **melekelerin açılarıyla
    # aynı düz vektörden** alıyor. O hâlde kademe ölçüleri artık
    # parametrede sabit değildir ve öğrenilebilir kayba **girer**.
    #
    # ``kademe_gorevleri`` verilirse kademeler her kayıp çağrısında o
    # görevlerde yeniden koşar (parametre değiştiği için mecburdur).
    # ``kademe_olcumleri`` eski yoldur: bir kere hesaplanmış sabit
    # ölçüler; onlar **yalnız raporlanır**, kayba girmez -- zira
    # parametreden bağımsızdırlar ve H156'nın körlüğünü geri getirirler.
    kademe_hepsi: List[Olcum] = []
    if kademe_gorevleri:
        for g in kademe_gorevleri:
            try:
                kademe_hepsi += list(
                    kademeleri_kos(g, p=nefs.p)["ölçümler"])
            except Exception:                            # noqa: BLE001
                continue
        hepsi += kademe_hepsi
    if kademe_olcumleri:
        kt = zayif_halka(olcumler=list(kademe_olcumleri), ne="azamî")
        _kademe_ozet = {"kademe_kayıp": kt["kayıp"],
                        "kademe_en_zayıf": kt["en_zayıf"],
                        "kademe_uzuv": kt["uzuv"]}
    elif kademe_hepsi:
        kt = zayif_halka(olcumler=list(kademe_hepsi), ne="azamî")
        _kademe_ozet = {"kademe_kayıp": kt["kayıp"],
                        "kademe_en_zayıf": kt["en_zayıf"],
                        "kademe_uzuv": kt["uzuv"]}
    else:
        _kademe_ozet = {}

    # =================================================================
    # ÖĞRENİLEBİLİR HATA ile YAPISAL KUSUR AYRILDI (kütük H154)
    # =================================================================
    #
    # Padişah koşturuldu ve kayıp yine kımıldamadı (0,8379 → 0,8376,
    # 170 çağrı). Sebep arandı: yumuşak azamîyi ele geçiren uzuv
    # ``𝒪₂₄.kesme``ydi (tutulan kesir 0,0046, yani eksik ~0,995).
    #
    # Fakat **bir kapının ne kadar kestiği, açı parametreleriyle
    # değişmez.** Kesme; menzilin uzunluğundan, MPO'nun zinciri baştan
    # sona sıkıştırmasından ve χ'den doğar -- yani **mimarînin
    # vasfıdır**, melekenin öğrenebileceği bir şey değil. Onu kayba
    # koymak, öğrenciye çözemeyeceği bir soruyu sorup notunu ona
    # bağlamaktır: not sabitlenir, öğrenme durur.
    #
    # O hâlde ölçüler ikiye ayrılır:
    #
    #   ÖĞRENİLEBİLİR -- hüküm alanlarının okumaları (tasdik, tenakuz,
    #       nakz, makam, sükût, kelâm, mizan, gaye) ve kademe ölçüleri.
    #       Bunlar açı parametreleriyle fiilen değişir; kayıp bunlardır.
    #
    #   YAPISAL -- kesme/sadakat. Kayba **girmez**; ayrıca raporlanır
    #       ve tamiri tasarımladır (nitekim H148/H149'da χ tavanları
    #       kaldırılarak 𝒪₂₄'ün tuttuğu 5,3e-07'den 0,0046'ya çıktı).
    #
    # Yapısalı gizlemiyoruz -- ``yapısal`` anahtarında sayılıyor ve en
    # kötüsü adıyla veriliyor. Gizleseydik, mimarî kusuru ölçüsüz
    # bırakmış olurduk.
    ogrenilebilir = [o for o in hepsi if not o.kaynak.endswith(".kesme")
                     and o.kaynak != "kesme"]
    yapisal = [o for o in hepsi if o.kaynak.endswith(".kesme")
               or o.kaynak == "kesme"]
    t = zayif_halka(olcumler=ogrenilebilir, ne="azamî")
    t.update(_kademe_ozet)
    if yapisal:
        yt = zayif_halka(olcumler=yapisal, ne="azamî")
        t["yapısal_kayıp"] = yt["kayıp"]
        t["yapısal_en_zayıf"] = yt["en_zayıf"]
        t["yapısal_uzuv"] = yt["uzuv"]
    t["meleke_sayısı"] = len({o.kaynak.split(".")[0] for o in hepsi
                              if o.kaynak.startswith("𝒪")})
    return t



# ====================================================================
#  KÜME 8: ezber mi, öğrenme mi
# ====================================================================

def lan(x: np.ndarray, xs: np.ndarray, ys: np.ndarray, L: float) -> np.ndarray:
    """Sol Kan genişletmesi: ``supᵢ [yᵢ − L|x−xᵢ|]``."""
    return np.max(ys[None, :] - L * np.abs(x[:, None] - xs[None, :]), axis=1)


def ran(x: np.ndarray, xs: np.ndarray, ys: np.ndarray, L: float) -> np.ndarray:
    """Sağ Kan genişletmesi: ``infᵢ [yᵢ + L|x−xᵢ|]``."""
    return np.min(ys[None, :] + L * np.abs(x[:, None] - xs[None, :]), axis=1)


def kan_ozellikleri(
    n: int = 12, L: float = 3.0, tohum: int = 0
) -> Dict[str, object]:
    """Üç iddia sınanır:

    1. ``Lan f`` ve ``Ran f`` örnek noktalarında ``f`` ile aynıdır (birim eş).
    2. İkisi de ``L``-Lipschitz'tir.
    3. Her ``L``-Lipschitz genişleme ikisinin ARASINDADIR (evrensel hususiyet).
    """
    rng = np.random.default_rng(tohum)
    xs = np.sort(rng.uniform(0, 1, n))
    hedef = lambda t: np.sin(2 * np.pi * t)          # Lipschitz sabiti 2π
    L = max(L, 2 * np.pi)
    ys = hedef(xs)

    izgara = np.linspace(0, 1, 1001)
    a, b = lan(izgara, xs, ys, L), ran(izgara, xs, ys, L)

    # 1. örnek noktalarda tam oturma
    oturma = float(
        max(np.max(np.abs(lan(xs, xs, ys, L) - ys)), np.max(np.abs(ran(xs, xs, ys, L) - ys)))
    )
    # 2. Lipschitz sabiti (ayrık)
    h = izgara[1] - izgara[0]
    lip = float(max(np.max(np.abs(np.diff(a))), np.max(np.abs(np.diff(b)))) / h)
    # 3. arada olma: hedefin kendisi L-Lipschitz bir genişlemedir
    g = hedef(izgara)
    arada = bool(np.all(a <= g + 1e-9) and np.all(g <= b + 1e-9))
    return {
        "L": L,
        "ornekte_tam_oturma_hatasi": oturma,
        "olculen_lipschitz": lip,
        "lipschitz_asilmadi": bool(lip <= L * (1 + 1e-6)),
        "hedef_arada": arada,
        "lan_ran_araligi_ortalama": float(np.mean(b - a)),
    }


def ezber_mi(xs=None, ys=None, t=None, ne: str = "kıyas",
             olcek: float = 0.03, lam: float = 1e-8, n: int = 40,
             gurultu: float = 0.25, tohum: int = 0):
    """EZBER Mİ, ÖĞRENME Mİ -- **tek terkip** (kütük H227).

    Küme: ``rbf_gram``, ``cekirdek_sirt``, ``ezber_kiyasi``,
    ``sobolev_kiyasi``. Dördü tek suâlin parçalarıydı: **model
    ezberliyor mu, yoksa genelliyor mu?** Ve cevabın tamamı tek
    sayıdadır -- düzenlileme katsayısı ``λ``:

        ``λ → 0``   eğitimde sıfır hata, sınamada patlama  → **EZBER**
        ``λ`` büyük eğitimde daha kötü, sınamada daha iyi  → **ÖĞRENME**

    Küllî kaybın bilmesi gereken şey tam olarak budur ve şimdiye kadar
    bilmiyordu.

    ==================  ==============================================
    ``ne``              döndürdüğü
    ==================  ==============================================
    ``gram``            RBF Gram dizeyi ``exp(−‖x−z‖²/2σ²)``
    ``uydur``           ``min_g Σ(g(xᵢ)−yᵢ)² + λ‖g‖²_H`` çözümü (fonksiyon)
    ``kıyas``           ``λ=10⁻⁸`` ile ``λ=10⁻¹``: ezber ile öğrenme
                        yan yana; koşul sayısı da raporlanır
    ``sobolev``         değer+türev uydurmak türev hatasını düşürüyor mu
    ==================  ==============================================

    İki ihtiyat kaydı -- ikisi de ölçüm sırasında ortaya çıktı:

    * **``λ = 0`` sayısal olarak ERİŞİLEBİLİR DEĞİLDİR.** Gram dizeyinin
      koşul sayısı burada ~10⁸--10¹⁷. Bu yüzden "tam aradeğerleme"
      yerine ``λ = 10⁻⁸`` alınır ve koşul sayısı **raporlanır** --
      erişilemeyen bir hâl erişilmiş gibi sunulmaz.
    * **Gürültü, gereken Lipschitz sabitini patlatır.** Kan
      genişletmesinin veriye tam oturması için ``L``, VERİNİN Lipschitz
      sabitinden küçük olmamalı; gürültülü veri hedefin ``2π``sini
      fazlasıyla aşar (burada ~4,5·10³). Yâni "tam oturma" bedava
      değildir: genişletme dikenleşir. Ezberin sebebi tam budur.
    """
    if ne == "gram":
        d2 = (np.asarray(xs, float)[:, None] - np.asarray(ys, float)[None, :]) ** 2
        return np.exp(-0.5 * d2 / (olcek * olcek))

    if ne == "uydur":
        xs_, ys_ = xs, ys
        K = ezber_mi(xs_, xs_, olcek=olcek, ne="gram")
        A = K + lam * np.eye(len(xs_))
        alfa = np.linalg.solve(A, ys_)
        return lambda t: ezber_mi(t, xs_, olcek=olcek, ne="gram") @ alfa

    if ne == "kıyas":
        rng = np.random.default_rng(tohum)
        hedef = lambda t: np.sin(2 * np.pi * t)
        xs = np.sort(rng.uniform(0, 1, n))
        ys = hedef(xs) + gurultu * rng.normal(size=n)
        xt = np.linspace(0.02, 0.98, 500)
        yt = hedef(xt)

        L_veri = float(np.max(np.abs(np.diff(ys) / np.diff(xs))))
        kan_orta = 0.5 * (lan(xt, xs, ys, L_veri) + ran(xt, xs, ys, L_veri))
        kan_egitim = 0.5 * (lan(xs, xs, ys, L_veri) + ran(xs, xs, ys, L_veri))

        g0 = ezber_mi(xs, ys, olcek=olcek, lam=1e-8, ne="uydur")
        g1 = ezber_mi(xs, ys, olcek=olcek, lam=1e-1, ne="uydur")

        def hata(tahmin: np.ndarray, dogru: np.ndarray) -> float:
            return float(np.sqrt(np.mean((tahmin - dogru) ** 2)))

        kayit = {
            "gurultu_seviyesi": gurultu,
            "verinin_lipschitz_sabiti": L_veri,
            "hedefin_lipschitz_sabiti": 2 * np.pi,
            "gram_kosul_sayisi": float(np.linalg.cond(ezber_mi(xs, xs, olcek=olcek, ne="gram"))),
            "kan_egitim_hatasi": hata(kan_egitim, ys),
            "kan_sinama_hatasi": hata(kan_orta, yt),
            "cekirdek_lam0_egitim": hata(g0(xs), ys),
            "cekirdek_lam0_sinama": hata(g0(xt), yt),
            "cekirdek_sirt_egitim": hata(g1(xs), ys),
            "cekirdek_sirt_sinama": hata(g1(xt), yt),
        }
        kayit["kan_tam_oturuyor"] = bool(kayit["kan_egitim_hatasi"] < 1e-9)
        kayit["gurultu_lipschitzi_patlatti"] = bool(L_veri > 100 * 2 * np.pi)
        # ezber: eğitimde gürültüden çok daha iyi, sınamada çok daha kötü
        kayit["ezber_gorunuyor"] = bool(
            kayit["cekirdek_lam0_egitim"] < 0.5 * gurultu
            and kayit["cekirdek_lam0_sinama"] > 4.0 * gurultu
        )
        kayit["duzenlileme_sinamayi_iyilestirdi"] = bool(
            kayit["cekirdek_sirt_sinama"] < kayit["cekirdek_lam0_sinama"]
            and kayit["cekirdek_sirt_sinama"] < kayit["kan_sinama_hatasi"]
        )
        kayit["duzenlileme_egitimi_kotulestirdi"] = bool(
            kayit["cekirdek_sirt_egitim"] > kayit["cekirdek_lam0_egitim"]
        )
        return kayit

    if ne == "sobolev":
        # Aslının imzası AYRI varsayılanlar taşıyordu; tek kapıya
        # girerken onlar geri konur -- yoksa ölçüm sessizce değişir
        # (H223'te ölçülen kusurun aynısı).
        if (n, gurultu, olcek, lam, tohum) == (40, 0.25, 0.03, 1e-8, 0):
            n, gurultu, olcek, lam, tohum = 14, 0.05, 0.25, 1e-6, 3
        rng = np.random.default_rng(tohum)
        hedef = lambda t: np.sin(2 * np.pi * t)
        turev = lambda t: 2 * np.pi * np.cos(2 * np.pi * t)
        xs = np.sort(rng.uniform(0, 1, n))
        ys = hedef(xs) + gurultu * rng.normal(size=n)
        ds = turev(xs) + gurultu * rng.normal(size=n)

        def dK(x: np.ndarray, z: np.ndarray) -> np.ndarray:
            """``∂/∂x k(x,z)``."""
            return -(x[:, None] - z[None, :]) / (olcek * olcek) * ezber_mi(x, z, olcek=olcek, ne="gram")

        K = ezber_mi(xs, xs, olcek=olcek, ne="gram")
        # (a) yalnız değer
        a_deger = np.linalg.solve(K + lam * np.eye(n), ys)
        # (b) değer + türev (en küçük kareler)
        A = np.vstack([K, dK(xs, xs)])
        b = np.concatenate([ys, ds])
        a_sob = np.linalg.lstsq(A.T @ A + lam * np.eye(n), A.T @ b, rcond=None)[0]

        xt = np.linspace(0.05, 0.95, 400)
        def hata(v, d):
            return float(np.sqrt(np.mean((v - d) ** 2)))

        deger_h = hata(ezber_mi(xt, xs, olcek=olcek, ne="gram") @ a_deger, hedef(xt))
        deger_t = hata(dK(xt, xs) @ a_deger, turev(xt))
        sob_h = hata(ezber_mi(xt, xs, olcek=olcek, ne="gram") @ a_sob, hedef(xt))
        sob_t = hata(dK(xt, xs) @ a_sob, turev(xt))
        return {
            "yalniz_deger__deger_hatasi": deger_h,
            "yalniz_deger__turev_hatasi": deger_t,
            "sobolev__deger_hatasi": sob_h,
            "sobolev__turev_hatasi": sob_t,
            "turev_iyilesti": bool(sob_t < deger_t),
        }

    raise ValueError("ezber suâlinin kipi bilinmiyor: %r" % (ne,))


def _rapor_ezber() -> str:
    s = ["=== genisletme ==="]
    k = kan_ozellikleri()
    s.append("Kan gen.  oturma hatası=%.2e  ölçülen Lip=%.3f ≤ L=%.3f → %s  hedef arada=%s"
             % (k["ornekte_tam_oturma_hatasi"], k["olculen_lipschitz"], k["L"],
                k["lipschitz_asilmadi"], k["hedef_arada"]))
    e = ezber_mi(ne="kıyas")
    s.append("ezber     Kan: eğitim=%.2e sınama=%.4f | λ=1e-8: eğitim=%.4f sınama=%.4g | sırt: eğitim=%.4f sınama=%.4f"
             % (e["kan_egitim_hatasi"], e["kan_sinama_hatasi"],
                e["cekirdek_lam0_egitim"], e["cekirdek_lam0_sinama"],
                e["cekirdek_sirt_egitim"], e["cekirdek_sirt_sinama"]))
    s.append("          gürültü=%.2f  verinin Lip=%.3g (hedefinki %.3g)  Gram koşul=%.2e"
             % (e["gurultu_seviyesi"], e["verinin_lipschitz_sabiti"],
                e["hedefin_lipschitz_sabiti"], e["gram_kosul_sayisi"]))
    s.append("          Kan tam oturuyor=%s  ezber görünüyor=%s  düzenlileme sınamayı iyileştirdi=%s"
             % (e["kan_tam_oturuyor"], e["ezber_gorunuyor"],
                e["duzenlileme_sinamayi_iyilestirdi"]))
    b = ezber_mi(ne="sobolev")
    s.append("Sobolev   yalnız değer: f=%.4f f'=%.4f | Sobolev: f=%.4f f'=%.4f | türev iyileşti=%s"
             % (b["yalniz_deger__deger_hatasi"], b["yalniz_deger__turev_hatasi"],
                b["sobolev__deger_hatasi"], b["sobolev__turev_hatasi"], b["turev_iyilesti"]))
    return "\n".join(s)

def rapor() -> str:                                     # pragma: no cover
    """KENDİNİ GÖSTERME -- **tek terkip** (kütük H224).

    Küme: altı dosyanın ``rapor()``ları. Her bölüm **kendi kapanışında**
    koşar; H223'te ölçülmüştü ki tek gövdede toplanınca yerel isimler
    (``n``, ``tur``, ``tohum``) birbirini eziyor ve ölçüm **fiilen
    değişiyor**. O kusur burada baştan engellendi.
    """
    s: List[str] = ["KÜLLÎ KAYIP ÇİPİ -- Küme 5 tevhidi"]

    def _rapor_nefs_olcu() -> List[str]:
        s: List[str] = []
        d = mertebe(ne="doğrula")
        s += ["=== ÖLÇÜ FUNKTORU -- ayrı uzaylardan müşterek uzaya ===",
             "",
             "Müşterek uzay `mizan/munazara.py`nin merdivenidir:",
             "  " + "  <  ".join("%s %.2f" % (k, v) for k, v in
                                 sorted(_mertebeler().items(),
                                        key=lambda kv: kv[1])),
             "",
             "FUNKTÖR KAİDELERİ (iddia değil, sınanmış):",
             "  F(id) = id            hata %.2e" % d["birim_hatası"],
             "  F(g∘f) = F(g)∘F(f)    hata %.2e   ← AŞİKÂR, delil DEĞİL"
             % d["terkip_hatası"],
             "",
             "  Terkip kaidesi bu inşada cebren sağlanır (F_T⁻¹∘F_T",
             "  sadeleşir), o yüzden hiçbir şey ispat etmez. Yük taşıyan",
             "  hususiyet SIRA KORUMASIDIR ve sınanan odur:",
             "    sıra korunuyor mu            : %s" % d["sıra_korunuyor"],
             "    cihet ters çevrilince bozuluyor mu: %s"
             % d["cihet_ters_çevrilince_bozuluyor"],
             "    → ölçüt kör değil            : %s" % d["ölçüt_kör_değil"],
             "  funktör mü                     : %s" % d["funktör_mü"],
             "",
             "TANIMLI UZAYLAR (had ve cihet):"]
        for ad in sorted(UZAYLAR):
            S = UZAYLAR[ad]
            s.append("  %-16s [%.3f, %.3f]  %s%s"
                     % (S.ad, S.alt, S.ust,
                        "büyüğü iyi" if S.buyugu_iyi else "küçüğü iyi",
                        "  (haddi TAHMİNÎ)" if S.tahmini_ust else ""))
        s += ["",
              "Eski kayıptaki 0,25 ve 0,1 gibi elle konmuş katsayılar",
              "KALKMIŞTIR: uzaylar arası intibak artık funktörle sağlanıyor,",
              "katsayıyla değil. Katsayı bir ölçü değil, ölçüsüzlüğün örtüsüdür."]
        return s

    s.append("")
    s.append("=" * 70)
    s.append("  ÖLÇÜ FUNKTÖRÜ -- S → 𝔐 mertebe köprüsü")
    s.append("=" * 70)
    s += _rapor_nefs_olcu()

    def _rapor_nefs_sozlesme() -> List[str]:
        s: List[str] = []
        n_satir = 4
        chi = 32
        tohum = 0
        o = sozunde_mi(n_satir=n_satir, chi=chi, tohum=tohum, ne="hepsi")
        s += ["=== SADAKAT SÖZLEŞMESİ (Dosya 2) -- yüzleştirme ===",
             "",
             "Her meleke dokunacağı bölgeleri İLAN eder; ölçüm dalganın",
             "kendisine bakıp fiilen dokunduğunu bulur. İkisi ayrı düşerse",
             "sözleşme ihlâl edilmiştir. Eşik = %.0e." % ESIK,
             "",
             "  𝒪   meleke              ihlâl / kullanılmayan"]
        ihlal_sayisi = 0
        bos_sayisi = 0
        sic = qsicil()
        for r in o:
            no = int(r["no"])
            ih, ku = r["ihlâl"], r["kullanılmayan"]
            if ih:
                ihlal_sayisi += 1
            if ku:
                bos_sayisi += 1
            isaret = "İHLÂL: " + ",".join(ih) if ih else ""
            if ku:
                isaret += ("  " if isaret else "") + "boş ilan: " + ",".join(ku)
            s.append("  %-3d %-20s %s" % (no, sic[no].ad, isaret or "✓"))
        s += ["",
              "%d melekede hudut ihlâli, %d melekede kullanılmayan ilan."
              % (ihlal_sayisi, bos_sayisi),
              "",
              "İHLÂL: meleke ilan etmediği bir bölgeye dokunmuş -- ya şerhi",
              "yanlış ya kapısı. KULLANILMAYAN İLAN: meleke ilan ettiği bir",
              "bölgeye HİÇ dokunmamış; sözleşme olduğundan geniş, yani",
              "denetlemiyor. İkincisi ihlâl kadar ağır değildir fakat bir",
              "gevşekliktir ve sayılır."]
        return s

    s.append("")
    s.append("=" * 70)
    s.append("  SÖZLEŞME -- taahhüt edilen bölgeye mi dokundu")
    s.append("=" * 70)
    s += _rapor_nefs_sozlesme()

    def _rapor_nefs_kademeler() -> List[str]:
        s: List[str] = []
        kume = "training"
        n = 3
        from .musahede import gorevleri_getir

        s += ["=== ALTI KADEME -- girdi/çıktı zinciri ===", ""]
        for g in gorevleri_getir(kume)[:int(n)]:
            r = kademeleri_kos(g)
            t = zayif_halka(olcumler=r["ölçümler"], ne="azamî")
            s.append("--- %s ---" % g.ad)
            s += ["  " + x for x in r["günlük"]]
            s.append("  kademe kaybı %.4f  (ortalama mertebe %.3f = %s)"
                     % (t["kayıp"], t["ortalama_mertebe"],
                        mertebe(ne="adlandır", m=t["ortalama_mertebe"])))
            if r["eksik"]:
                s.append("  DÜŞEN UZUV: %s" % ", ".join(sorted(r["eksik"])))
            s.append("")
        s += ["Kademe k'nın çıktısı kademe k+1'in girdisidir; bir modül o",
              "zincirde halka ise uzuvdur. Yan tarafta rey veren modül uzuv",
              "değildir ve bu dosya o farkın kendisidir."]
        return s

    s.append("")
    s.append("=" * 70)
    s.append("  ALTI KADEME -- LOO notlandırması")
    s.append("=" * 70)
    s += _rapor_nefs_kademeler()

    def _rapor_nefs_mudrike() -> List[str]:
        s: List[str] = []
        kume = "training"
        n = 120
        derinlik = 2
        dalga = False
        from .musahede import gorevleri_getir

        g = gorevleri_getir(kume)[:int(n)]
        coz = cevap = yanlis = 0
        sebepler: Dict[str, int] = {}
        ornek_muhakeme: List[str] = []
        for gv in g:
            r = suz(gv, derinlik=derinlik, dalga=dalga)
            if r["sükût"]:
                sebepler[r["sebep"]] = sebepler.get(r["sebep"], 0) + 1
                if not ornek_muhakeme and r["sebep"] == "kaide bulunamadı":
                    ornek_muhakeme = list(r["muhakeme"])
                continue
            cevap += 1
            ok = True
            for (a, b), c in zip(gv.sinama, r["cevap"]):
                if c is None or c.shape != b.shape or not np.array_equal(c, b):
                    ok = False
            coz += ok
            yanlis += (not ok)
            if ok and len(ornek_muhakeme) < 2:
                ornek_muhakeme = list(r["muhakeme"])

        s += ["=== MÜDRİKE ÇEVRİMİ -- %s (%d görev) ===" % (kume, len(g)),
             "",
             "  konuştu      : %d" % cevap,
             "  TAM ÇÖZDÜ    : %d  (%%%.1f)" % (coz, 100.0 * coz / max(len(g), 1)),
             "  yanlış cevap : %d" % yanlis,
             "  sustu        : %d" % (len(g) - cevap),
             "",
             "  SÜKÛT SEBEPLERİ:"]
        for k, v in sorted(sebepler.items(), key=lambda x: -x[1]):
            s.append("    %-26s %d" % (k, v))
        if ornek_muhakeme:
            s += ["", "  BİR MUHAKEME ÖRNEĞİ (modelin kendi kendine düşündüğü):"]
            s += ["    " + x for x in ornek_muhakeme]
        s += ["",
              "Cevap verince isabet: %s"
              % ("%.1f%%" % (100.0 * coz / cevap) if cevap else "—"),
              "Susmak bir kusur değil kabiliyettir (H10/H16) -- fakat",
              "sebebi söylenebiliyorsa. Yukarıdaki döküm o sebeplerdir."]
        return s

    s.append("")
    s.append("=" * 70)
    s.append("  MÜDRİKE -- meseleyi içinden geçirmek")
    s.append("=" * 70)
    s += _rapor_nefs_mudrike()

    def _rapor_nefs_tesir() -> List[str]:
        s: List[str] = []
        tohum = 0
        n = 40
        d_in = 12
        ayrinti = True
        # ASIL ÖLÇÜM yapılandırılmış girdide yapılır. Rastgele gürültüde
        # model -- doğru olarak -- **susar** (makam Şek → sükût), o hâlde
        # ``N`` zaten sıfırdır ve ``‖ΔN‖`` hiçbir melekeyi ayırt edemez;
        # o girdideki "tesirsiz" sayısı sükûtun gölgesidir, melekelerin
        # hâli değil. Rastgele girdi yine de raporlanır, fakat ikinci
        # sırada ve bu kayıtla.
        E = eksilt(ne="girdi", tohum=tohum)

        d, izler = eksilt(E, tohum, ne="iz")
        satir = ["=== Kademe 5: icra izi ===",
                 "adım: %d   şahit: %d   makam: %s   sükût: %s"
                 % (len(izler), len(d.sahitler or []), d.makam, d.sukut)]
        sessiz = [iz for iz in izler if not iz.degisen]
        satir.append("hiçbir alanı değiştirmeyen adım: %d/%d  %s"
                     % (len(sessiz), len(izler), [iz.no for iz in sessiz]))
        gizli = [iz for iz in izler
                 if set(iz.degisen) - set(iz.yazdigi) - {"tenakuz", "T",
                                                         "P_idrak", "makam",
                                                         "muteber_sahit",
                                                         "tevafuk", "sukut"}]
        satir.append("sözleşmesinde olmayan alanı değiştiren adım: %d  %s"
                     % (len(gizli), [(iz.no, tuple(set(iz.degisen)
                                                   - set(iz.yazdigi)))
                                     for iz in gizli]))

        temel, sonuc = eksilt(E, tohum)
        t = eksilt(ne="tablo", sonuc=sonuc)
        satir += ["", "=== Kademe 5: hassasiyet (bir meleke düşerse) ===",
                  "temel: ‖N‖=%.6f  makam=%s  sükût=%s  P=%.4f"
                  % (float(np.linalg.norm(temel["N"])), temel["makam"],
                     temel["sukut"], temel["P_idrak"]),
                  "tesirli: %d   yapısal zaruret: %d   TESİRSİZ: %d / %d"
                  % (len(t["tesirli"]), len(t["yapısal"]),
                     len(t["tesirsiz"]), t["toplam"])]
        satir.append("tesirsiz melekeler: %s" % t["tesirsiz"])

        if ayrinti:
            satir += ["", "%-4s %-18s %-10s %10s %8s %s"
                      % ("𝒪", "ad", "hâl", "‖ΔN‖", "ΔP", "değişen hüküm")]
            satir.append("-" * 82)
            for x in sorted(sonuc, key=lambda z: (-z.dN, z.no)):
                hukumler = ",".join(
                    a for a, v in (("makam", x.makam_degisti),
                                   ("sükût", x.sukut_degisti),
                                   ("nakz", x.nakz_degisti),
                                   ("mühür", x.muhur_degisti)) if v) or "—"
                satir.append("%-4d %-18s %-10s %10.5f %8.4f %s"
                             % (x.no, x.ad, x.hal, x.dN, x.dP,
                                hukumler if not x.kirildi else x.sebep))

        # --- ikinci ölçümler
        ikinciler = [("bir şahit bozuk", eksilt(ne="girdi", bozuk=2, tohum=tohum)),
                     ("rastgele gürültü (model susar; ölçü ayırt etmez)",
                      np.random.default_rng(tohum).normal(size=(n, d_in)))]
        for etiket, E2 in ikinciler:
            d2 = Nefs(tohum).idrak_et(E2)
            temel2, sonuc2 = eksilt(E2, tohum)
            t2 = eksilt(ne="tablo", sonuc=sonuc2)
            satir += ["", "=== yapılandırılmış girdi: %s ===" % etiket,
                      "şahit=%d  nakz=%s  müteber=%.2f  P=%.4f  makam=%s  sükût=%s"
                      % (len(d2.sahitler or []), d2.nakz, d2.muteber_sahit,
                         d2.P_idrak, d2.makam, d2.sukut),
                      "tesirli: %d   yapısal: %d   TESİRSİZ: %d / %d  → %s"
                      % (len(t2["tesirli"]), len(t2["yapısal"]),
                         len(t2["tesirsiz"]), t2["toplam"], t2["tesirsiz"])]
        return "\n".join(satir)
        return s

    s.append("")
    s.append("=" * 70)
    s.append("  TESİR -- bu meleke düşse ne değişir")
    s.append("=" * 70)
    s += _rapor_nefs_tesir()

    def _rapor_nefs_kulli_kayip() -> List[str]:
        s: List[str] = []
        n = 2
        from .musahede import gorevleri_getir

        from main.egitim import KISA_CPU
        from .melekeler import QNefs
        from .qegitim import ornekler

        ayar = KISA_CPU
        nefs = QNefs(ayar.tohum, ayar.qayar())
        nefs.idrak_et(np.zeros((2, ayar.satir_kubiti)))
        veri = ornekler(gorevleri_getir("training")[:6], azami=int(n),
                        pencere=ayar.pencere, sozluk=ayar.sozluk)
        t = kulli_kayip(nefs, veri, sozluk=ayar.sozluk)
        s += ["=== KÜLLÎ KAYIP -- 41 melekenin hepsi sayılıyor mu? ===",
             "",
             "  toplanan uzuv ölçüsü : %d" % t["uzuv"],
             "  ayrı meleke sayısı   : %d  ← 41 olmalı" % t["meleke_sayısı"],
             "  ortalama mertebe     : %.4f" % t["ortalama_mertebe"],
             "  KAYIP (1 − mertebe)  : %.4f" % t["kayıp"],
             "  en zayıf uzuv        : %s" % (t["en_zayıf"],),
             "  haddi tahminî ölçü   : %d" % t["tahminî_hadli"],
             "",
             "Eskiden kayıp BEŞ sayı okuyordu ve otuz altı melekenin eğitim",
             "sinyali sıfırdı. Yukarıdaki 'ayrı meleke sayısı' o borcun",
             "kapanıp kapanmadığının ölçüsüdür; iddia değil sayımdır."]
        return s

    s.append("")
    s.append("=" * 70)
    s.append("  KÜLLÎ KAYIP -- funktöryel birleşim")
    s.append("=" * 70)
    s += _rapor_nefs_kulli_kayip()
    return "\n".join(s)


if __name__ == "__main__":                              # pragma: no cover
    print(rapor())
