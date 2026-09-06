"""SÖYLEMEK -- ya motorun ürettiği, ya sükût.

Nazırlık katının altıncı ve son fiili. **Yeni riyaziye yoktur.**

    cevap = soyle(gorev, nefs=motor)

===================================================================
PADİŞAHIN FERMANI: ARC'Yİ MOTOR ÇÖZER, BAŞKA HİÇBİR ŞEY DEĞİL
===================================================================

Bu dosya evvelce ``idrak/cozucu.py``yi çağırıyordu: elle yazılmış ARC
kâideleri (yerçekimi, bakışım onarımı, delik rengi, döşeme, kırpma,
renk eşlemesi). O dosya tasfiye edildi ve sebebi tektir:

    Çözen motor değildi. Çözen, o dosyaya elle yazılmış tahminlerdi.
    Motor kenarda duruyor, cevabı kâide cebri veriyor, netice ise
    "model ARC'yi çözdü" diye okunuyordu. Bu bir gösteriştir.

Kütük H133'te bunun tersi bir hüküm vardı: dil modeli yolu kapatılmış,
"padişah tam da olmamaya yemin ettiği şeyi yapıyordu: bir dil modeli"
denmişti. **O hüküm iptal edildi.** Bu proje bir dil modeli projesidir;
ARC de dil modeliyle çözülecektir. H133'ün cebri (``0,95¹⁰⁰ ≈ 0,006``)
yanlış değildi -- fakat o, motoru terk etmenin değil, motoru
**büyütmenin** gerekçesidir: 8 belirteçlik pencere ve 16 sembollük
sözlük bir kusurdur, dil modeli olmak kusur değildir.

O hâlde söylemek şudur: bağlamı kur, motoru koştur, belirteç belirteç
üret. Sükût yine mümkündür ve yine bir hükümdür (H10) -- fakat artık
sükûtu da motor verir (``adayin_tuttugu``un ``sukut`` alanı), elle
yazılmış bir şart değil.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import numpy as np

from .gor import Manzara, gor
from .musahede import gorev_dizisi, ortu

__all__ = ["Cevap", "soyle"]


@dataclass
class Cevap:
    """SÖYLENEN -- yahut susulan.

    ``sukut`` doğruysa ``izgara`` boştur ve ``sebep`` niçin
    susulduğunu söyler. Sükût bir başarısızlık değil bir **hüküm**dür.
    """

    gorev: str = ""
    sukut: bool = True
    sebep: str = ""
    kural: Optional[str] = None
    izgara: Optional[List[np.ndarray]] = None
    aday_sayisi: int = 0
    tikaniklik: Optional[float] = None
    belirtec: Optional[List[int]] = None
    guven: float = 0.0
    #: Kuantum Zeno budamasıyla kesilen mantık kolu sayısı. Hafıza
    #: verilmezse **tam sıfırdır**; yâni tesir kapatılabilir ve ölçü
    #: kırmızı yanabilir (H90).
    budanan: int = 0


def _buda(P: np.ndarray, hafiza) -> tuple:
    """KUANTUM ZENO BUDAMASI -- cerhedilmiş kola girilirse kes.

    Zabıt (`Ham Veriden Kuantum Hafızasına`, V. fasıl):

        𝒦 = Tr( ρ_Hafıza · |ψ⟩⟨ψ| )

    Bu iç çarpım ``O(1)``dir; model 10.000 adımı geriye taramaz. Eğer
    örtüşen kayıt **cerh** (``T=0``) damgalı ise, o mantık kolu daha
    döngü tamamlanmadan kesilir: ilgili belirteçlerin genliği sıfırlanır.

    ``hafiza`` verilmezse hiçbir şey olmaz ve ``P`` **birebir** aynen
    döner. Tesir kapatılabilir olmalıdır, yoksa ölçülemez (H90).
    """
    if hafiza is None:
        return P, 0
    # Belirteç lifi üstündeki genlik: ``√P``. Hafıza kayıtları da bu
    # tabanda tutulur, o yüzden iç çarpım doğrudan alınır.
    maske = hafiza.zeno(np.sqrt(np.asarray(P, float)))
    if maske is None:
        return P, 0
    kesik = int(np.count_nonzero(~maske))
    if kesik == 0 or kesik >= P.size:
        # Hepsini kesmek sükût değil, çöküştür: o hâlde budama yapılmaz
        # ve bu gizlenmez -- sayı sıfır döner.
        return P, 0
    Q = np.where(maske, P, 0.0)
    top = float(Q.sum())
    assert top > 0.0, "Zeno budaması dağılımı tamamen söndürdü"
    return Q / top, kesik


def _sec(P: np.ndarray, ayna=None) -> int:
    """BİR BELİRTEÇ SEÇ -- **zar atmadan**.

    ===================================================================
    KÖR SICAKLIK İMHA EDİLDİ (zabıt: yarı yansıtıcı ayna, IV.1)
    ===================================================================

    Burada evvelce şu vardı::

        t = int(rastgele.choice(len(P), p=P))    # ← İMHA EDİLDİ

    Yâni klasik LLM'lerin ``temperature`` kumarı: softmax çıktısına
    dışarıdan bir zar. Zabıtın hükmü açıktır -- *"bu işlem kör bir
    kumar zarından ibarettir; sıcaklığı artırdığınız an model saçmalar
    ve halüsinasyona boğulur."*

    Yerine gelen şey gürültü **eklemez**, durumu bir ışın bölücüden
    geçirir: bir porta modelin o anki mana durumu, öteki porta
    matematiksel vakum konur. Çıkan kıvılcım durumun **kendi faz
    uzayından** doğar, dışarıdan serpiştirilmez. Sonra yine ``argmax``
    alınır -- yâni seçim belirlenimcidir ve aynı girdi aynı çıktıyı
    verir.

    ``ayna`` yoksa hiçbir şey olmaz ve ``argmax(P)`` döner: ölçü
    kapatılabilir, dolayısıyla kırmızı yanabilir (H90).
    """
    if ayna is None:
        return int(np.argmax(P))
    from .ayna import kivilcim
    Q = kivilcim(P, ayna)
    assert Q.size == P.size and np.all(np.isfinite(Q)), "kıvılcım bozuk"
    return int(np.argmax(Q))


def _uret_qudit(baglam: List[int], n: int, pencere: int, sozluk: int,
                teta=None, d: int = 256, ayna=None, hafiza=None) -> tuple:
    """QUDİT hattı: ``nefs/qyazmac.py`` -- **SVD yok, MPS yok**.

    Eski hat 126 kübitlik bir MPS zinciriydi ve her kapı bir SVD
    istiyordu (ileri geçiş başına ~8500). Burada durum tek parça
    ``ℂ^d``dir, **tam** tutulur ve kapılar Kronecker lifleri üstünde
    küçük dizeylerle vurulur.

    Ölçüldü: ``d=256``te 1401 belirteç/sn, eski hattın **127 katı**;
    üniterlik ``2,2e−16``da korunuyor.
    """
    from .qyazmac import QuditYazmac, QuditAyar
    lif = (4, 8, 8) if d == 256 else (16, 16, 16)
    q = QuditYazmac(QuditAyar(d=d, lif=lif))
    bag = list(baglam)
    cikti: List[int] = []
    bedel = 0.0
    budanan = 0
    sukutlar: List[float] = []
    for _ in range(n):
        pen = (bag[-pencere:] if len(bag) >= pencere
               else [0] * (pencere - len(bag)) + bag)
        P = np.asarray(q.uret(pen, teta=teta, sozluk=int(sozluk)), float)
        P = np.clip(P.reshape(-1), 1e-12, None)
        P = P / P.sum()
        # Sükût quditte de MOTORDAN gelir: sükût sektörünün ağırlığı.
        sukutlar.append(float(np.ravel(q.alan_degeri("sukut"))[0]))
        # KUANTUM ZENO BUDAMASI -- hafızada cerhedilmiş bir yola
        # girilmişse, döngü **tamamlanmadan** o kol kesilir.
        P, kesik = _buda(P, hafiza)
        budanan += kesik
        t = _sec(P, ayna)
        bedel -= float(np.log(P[t]))
        cikti.append(t)
        bag.append(t)
    return cikti, bedel, sukutlar, budanan


def _uret(nefs, baglam: List[int], n: int, pencere: int, sozluk: int,
          ayna=None, hafiza=None) -> tuple:
    """Bir dizi üret; ``(belirteçler, toplam −log P, sükûtlar)`` döndür.

    ``ayna`` verilirse dağılım evvela yarı yansıtıcı aynadan geçirilir
    (``nefs/ayna.py``), verilmezse doğrudan ``argmax`` alınır. **Zar
    atılmaz** -- bkz. ``_sec``.
    """
    from .qegitim import adayin_tuttugu
    bag = list(baglam)
    cikti: List[int] = []
    bedel = 0.0
    budanan = 0
    sukutlar: List[float] = []
    for _ in range(n):
        pen = (bag[-pencere:] if len(bag) >= pencere
               else [0] * (pencere - len(bag)) + bag)
        P, o = adayin_tuttugu(nefs, (), sozluk=int(sozluk), ne="koş",
                              baglam=pen)
        P = np.asarray(P, float).reshape(-1)
        P = np.clip(P, 1e-12, None)
        P = P / P.sum()
        sukutlar.append(float(o.get("sukut", 0.0)))
        P, kesik = _buda(P, hafiza)
        budanan += kesik
        t = _sec(P, ayna)
        bedel -= float(np.log(P[t]))
        cikti.append(t)
        bag.append(t)
    return cikti, bedel, sukutlar, budanan


def soyle(gorev=None, manzara=None, tikaniklik_bak: bool = False,
          nefs=None, pencere: int = 8, sozluk: int = 16,
          azami_uret: int = 0, sukut_esigi: float = 0.8,
          usul: str = "açgözlü", aday: int = 8, tohum: int = 0,
          motor: str = "mps", qudit_d: int = 256, teta=None,
          hafiza=None, ne: str = "cevap") -> Any:
    """SÖYLEMEK -- görevden ``Cevap``, yahut sükût. **Motorla.**

    İki kapı vardır ve her biri susturabilir:

    1. ``gor`` -- kalıp bulunamadıysa (``Manzara.sukut``) çıktının kaç
       satır kaç sütun olacağı bilinmiyor demektir; üretime girilmez.
    2. ``adayin_tuttugu`` -- motorun kendi **sükût** alanı eşiği
       aşarsa model bilmediğini söyler. Bu bir şart değil bir ölçümdür.

    ``nefs`` verilmezse motor yoktur ve **sükût edilir**. Motorsuz
    cevap vermek, tasfiye edilen kâide cebrine geri dönmek olurdu.

    ==============  ==================================================
    ``ne``          döndürdüğü
    ==============  ==================================================
    ``cevap``       ``Cevap`` -- söylenen yahut sükût
    ``sukut_mu``    yalnız ``bool`` (ucuz)
    ==============  ==================================================
    """
    if gorev is None:
        raise ValueError("söylemek için bir görev lâzım")
    if manzara is None:
        manzara = gor(gorev)

    def _bitir(c: "Cevap"):
        if ne == "sukut_mu":
            return c.sukut
        if ne != "cevap":
            raise ValueError("söyleme kipi bilinmiyor: %r" % (ne,))
        return c

    if manzara.sukut:
        return _bitir(Cevap(
            gorev=gorev.ad, sukut=True,
            sebep="kalıp bilinmiyor -- çıktının ebadı kestirilemedi"))

    if motor == "mps" and nefs is None:
        return _bitir(Cevap(
            gorev=gorev.ad, sukut=True,
            sebep="motor verilmedi -- kâide cebriyle cevap vermek yasak"))
    if motor not in ("mps", "qudit"):
        raise ValueError("motor bilinmiyor: %r" % (motor,))

    tik = None
    if tikaniklik_bak:
        # ``except`` kaldırıldı (ferman): tıkanıklık ölçülemiyorsa bu
        # sessizce ``None``a düşecek bir şey değil, ölçünün kendisinin
        # kırılmasıdır ve görülmelidir.
        tik = float(ortu(gorev, ne="tıkanıklık")["H1"])
        assert np.isfinite(tik), "tıkanıklık ölçüsü sonlu değil"

    dizi, hedef = gorev_dizisi(gorev, hedef_indis=0)
    assert len(dizi) > 0 and len(hedef) > 0, (
        "bağlam yahut hedef BOŞ döndü -- boş bir şeyle üretime girilmez")

    h = [int(x) % int(sozluk) for x in hedef]
    if 0 < int(azami_uret) < len(h):
        return _bitir(Cevap(gorev=gorev.ad, sukut=True, tikaniklik=tik,
                            sebep="hedef hadde sığmıyor (%d belirteç)"
                                  % len(h)))

    baglam = [int(x) % int(sozluk) for x in dizi]

    def _cek(ayna=None):
        if motor == "qudit":
            return _uret_qudit(baglam, len(h), pencere, sozluk,
                               teta=teta, d=int(qudit_d), ayna=ayna,
                               hafiza=hafiza)
        return _uret(nefs, baglam, len(h), pencere, sozluk, ayna=ayna,
                     hafiza=hafiza)

    if usul == "açgözlü":
        # Açgözlü çözme: her adımda argmax. Yerel olarak en iyidir,
        # dizi olarak DEĞİL.
        uretilen, bedel, sukutlar, budanan = _cek()
    elif usul == "ara":
        # =============================================================
        # ARAMA NAZIRLIĞI BURADA İŞ GÖRÜR (nefs/ara.py)
        # =============================================================
        # Açgözlü çözme her adımda en iyisini seçer; DİZİ olarak en
        # iyisini seçmez. Doğru ölçüt dizinin **toplam** ``−log P``
        # bedelidir ve onu asgarîye indirmek bir ARAMA meselesidir.
        # Bu, dil modelinin kendi meselesidir -- elle yazılmış bir ARC
        # kâidesi değil: kehanet modelin **kendi** dağılımıdır.
        #
        # ``ara`` Dürr--Høyer ile ``O(√N)``da asgarîyi bulur ve
        # işaretli sayısını (``K``) bilmek istemez.
        from .ara import ara
        from .ayna import AynaAyari
        # ADAY ÇEŞİTLİLİĞİ ZARDAN DEĞİL, AYNA AÇISINDAN GELİR.
        # Evvelce her aday ``rastgele.choice`` ile çekiliyordu: aynı
        # tohumla bile aday sırası zarın hâline bağlıydı ve iki koşu
        # arasındaki farkın sebebi ölçülemezdi. Şimdi ``k``ıncı aday
        # ``θ_k`` açısıyla aynadan geçirilmiş durumun argmaxıdır --
        # belirlenimci, tekrarlanabilir ve **niçin farklı olduğu
        # söylenebilir**: kıvılcım o kadar açıldı.
        n_ad_istenen = max(1, int(aday))
        adaylar = [_cek()]
        for k in range(1, n_ad_istenen):
            adaylar.append(_cek(AynaAyari(
                teta=(np.pi / 4) * k / n_ad_istenen,
                sikma_fazi=2.0 * np.pi * k / n_ad_istenen,
                tohum=int(tohum) + k)))
        bedeller = np.array([a[1] for a in adaylar], float)
        n_ad = len(adaylar)
        tam = 1
        while tam < n_ad:
            tam *= 2
        if tam > n_ad:                        # Grover yazmacı 2^n ister
            bedeller = np.concatenate(
                [bedeller, np.full(tam - n_ad, bedeller.max() + 1e3)])
        j = int(ara(bedeller, ne="en_iyi", yol="dürr")["x"])
        assert 0 <= j < len(bedeller), "arama aralık dışı indis verdi: %d" % j
        uretilen, bedel, sukutlar, budanan = adaylar[j if j < n_ad else 0]
    else:
        raise ValueError("çözme usulü bilinmiyor: %r" % (usul,))

    guvenler = [float(np.exp(-bedel / max(len(h), 1)))]

    # **SÜKÛTU MOTOR VERİR.** Ortalama sükût alanı eşiği aşarsa model
    # bilmediğini söylüyor demektir ve söylenmez. Eşik ayarlanabilir
    # ve kapatılabilir (H90); elle yazılmış bir kâide değildir.
    ort_sukut = float(np.mean(sukutlar)) if sukutlar else 1.0

    # ══════════════════════════════════════════════════════════════
    #  ŞÜPHE MANİFOLDU ÇIKARIMDA (nefs/suphe.py)
    # ══════════════════════════════════════════════════════════════
    #
    # **SÜKÛTUN İKİNCİ SEBEBİ: TEÂRUZ.** Sükût alanı "bilmiyorum"u
    # ölçer; teâruz ise başka bir hâldir: model **iki zıddı da aynı
    # kuvvette** taşıyor demektir (``μ ← μ·(1 − |⟨ψ_P|ψ_¬P⟩|)``).
    # Orada hüküm vermek, yazı-tura atıp "biliyorum" demektir.
    #
    # Bu satır, ``main/cikarim.py``nin *"şüphe manifoldu çıkarımda iş
    # görür"* iddiasının **karşılığıdır**. Evvelce o iddia yazılmış
    # fakat manifold yalnız mizanda koşuyordu; ölçüldü (çıkarımda
    # ``teâruz 0``) ve bağlandı -- iddia edilen şey koşturulur, yoksa
    # iddia silinir (ferman 5).
    from .qegitim import belirtecleri_kodla
    from .suphe import SupheAyari, suphe_manifoldu
    _E = belirtecleri_kodla(list(uretilen)[-int(pencere):] or [0],
                            nefs.ayar.veri_lifi, int(sozluk))
    _q = nefs.idrak_et(_E)
    _sp = suphe_manifoldu([np.asarray(_q.y.psi[0], complex)],
                          [1.0 - 2.0 * ort_sukut],
                          yakin=np.array([1.0 - ort_sukut]),
                          ayar=SupheAyari(acik=1))
    if int(_sp["tevakkuf"]) > 0:
        return _bitir(Cevap(
            gorev=gorev.ad, sukut=True, tikaniklik=tik,
            belirtec=uretilen, guven=float(np.mean(guvenler or [0.0])),
            budanan=int(budanan),
            sebep="TEÂRUZ: yakîn %.3f -- tez ile antitez denk kuvvette"
                  % float(_sp["μ"][0])))

    if ort_sukut > float(sukut_esigi):
        return _bitir(Cevap(
            gorev=gorev.ad, sukut=True, tikaniklik=tik,
            belirtec=uretilen, guven=float(np.mean(guvenler or [0.0])),
            budanan=int(budanan),
            sebep="motorun sükût alanı %.3f > %.3f"
                  % (ort_sukut, float(sukut_esigi))))

    return _bitir(Cevap(
        gorev=gorev.ad, sukut=False, sebep="",
        kural="motor (belirteç üretimi)",
        izgara=[np.asarray(uretilen, int)],
        belirtec=uretilen,
        guven=float(np.mean(guvenler or [0.0])),
        budanan=int(budanan),
        aday_sayisi=0, tikaniklik=tik))
