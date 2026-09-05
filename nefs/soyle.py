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


def _uret_qudit(baglam: List[int], n: int, pencere: int, sozluk: int,
                teta=None, d: int = 256, rastgele=None) -> tuple:
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
    sukutlar: List[float] = []
    for _ in range(n):
        pen = (bag[-pencere:] if len(bag) >= pencere
               else [0] * (pencere - len(bag)) + bag)
        P = np.asarray(q.uret(pen, teta=teta, sozluk=int(sozluk)), float)
        P = np.clip(P.reshape(-1), 1e-12, None)
        P = P / P.sum()
        # Sükût quditte de MOTORDAN gelir: sükût sektörünün ağırlığı.
        sukutlar.append(float(np.ravel(q.alan_degeri("sukut"))[0]))
        t = (int(rastgele.choice(len(P), p=P)) if rastgele is not None
             else int(np.argmax(P)))
        bedel -= float(np.log(P[t]))
        cikti.append(t)
        bag.append(t)
    return cikti, bedel, sukutlar


def _uret(nefs, baglam: List[int], n: int, pencere: int, sozluk: int,
          rastgele=None) -> tuple:
    """Bir dizi üret; ``(belirteçler, toplam −log P, sükûtlar)`` döndür.

    ``rastgele`` verilirse dağılımdan **örneklenir**, verilmezse
    ``argmax`` alınır (açgözlü).
    """
    from .qegitim import adayin_tuttugu
    bag = list(baglam)
    cikti: List[int] = []
    bedel = 0.0
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
        t = (int(rastgele.choice(len(P), p=P)) if rastgele is not None
             else int(np.argmax(P)))
        bedel -= float(np.log(P[t]))
        cikti.append(t)
        bag.append(t)
    return cikti, bedel, sukutlar


def soyle(gorev=None, manzara=None, tikaniklik_bak: bool = False,
          nefs=None, pencere: int = 8, sozluk: int = 16,
          azami_uret: int = 0, sukut_esigi: float = 0.8,
          usul: str = "açgözlü", aday: int = 8, tohum: int = 0,
          motor: str = "mps", qudit_d: int = 256, teta=None,
          ne: str = "cevap") -> Any:
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
        try:
            tik = float(ortu(gorev, ne="tıkanıklık")["H1"])
        except Exception:                    # pragma: no cover
            tik = None

    from .qegitim import adayin_tuttugu
    try:
        dizi, hedef = gorev_dizisi(gorev, hedef_indis=0)
    except Exception as exc:                 # pragma: no cover
        return _bitir(Cevap(gorev=gorev.ad, sukut=True, tikaniklik=tik,
                            sebep="bağlam kurulamadı: %s"
                                  % type(exc).__name__))

    h = [int(x) % int(sozluk) for x in hedef]
    if 0 < int(azami_uret) < len(h):
        return _bitir(Cevap(gorev=gorev.ad, sukut=True, tikaniklik=tik,
                            sebep="hedef hadde sığmıyor (%d belirteç)"
                                  % len(h)))

    baglam = [int(x) % int(sozluk) for x in dizi]

    def _cek(rast=None):
        if motor == "qudit":
            return _uret_qudit(baglam, len(h), pencere, sozluk,
                               teta=teta, d=int(qudit_d), rastgele=rast)
        return _uret(nefs, baglam, len(h), pencere, sozluk, rastgele=rast)

    if usul == "açgözlü":
        # Açgözlü çözme: her adımda argmax. Yerel olarak en iyidir,
        # dizi olarak DEĞİL.
        uretilen, bedel, sukutlar = _cek()
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
        r = np.random.default_rng(int(tohum))
        adaylar = [_cek()]
        for _ in range(max(0, int(aday) - 1)):
            adaylar.append(_cek(r))
        bedeller = np.array([a[1] for a in adaylar], float)
        n_ad = len(adaylar)
        tam = 1
        while tam < n_ad:
            tam *= 2
        if tam > n_ad:                        # Grover yazmacı 2^n ister
            bedeller = np.concatenate(
                [bedeller, np.full(tam - n_ad, bedeller.max() + 1e3)])
        try:
            j = int(ara(bedeller, ne="en_iyi", yol="dürr")["x"])
        except Exception:                     # pragma: no cover
            j = int(np.argmin(bedeller))
        uretilen, bedel, sukutlar = adaylar[j if j < n_ad else 0]
    else:
        raise ValueError("çözme usulü bilinmiyor: %r" % (usul,))

    guvenler = [float(np.exp(-bedel / max(len(h), 1)))]

    # **SÜKÛTU MOTOR VERİR.** Ortalama sükût alanı eşiği aşarsa model
    # bilmediğini söylüyor demektir ve söylenmez. Eşik ayarlanabilir
    # ve kapatılabilir (H90); elle yazılmış bir kâide değildir.
    ort_sukut = float(np.mean(sukutlar)) if sukutlar else 1.0
    if ort_sukut > float(sukut_esigi):
        return _bitir(Cevap(
            gorev=gorev.ad, sukut=True, tikaniklik=tik,
            belirtec=uretilen, guven=float(np.mean(guvenler or [0.0])),
            sebep="motorun sükût alanı %.3f > %.3f"
                  % (ort_sukut, float(sukut_esigi))))

    return _bitir(Cevap(
        gorev=gorev.ad, sukut=False, sebep="",
        kural="motor (belirteç üretimi)",
        izgara=[np.asarray(uretilen, int)],
        belirtec=uretilen,
        guven=float(np.mean(guvenler or [0.0])),
        aday_sayisi=0, tikaniklik=tik))
