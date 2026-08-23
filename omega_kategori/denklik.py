"""
Glue tipleri için Kan hesabı ve bu çekirdeğin AÇIK BOŞLUKLARI.

Bu dosya iki işi yapar:

  1) Glue hesabının GERÇEKTEN İŞLEYEN parçalarını verir:
     ``∀i.φ`` (bir kofibrasyonun ``i``den bağımsız en büyük parçası) ve
     büzülebilirlikten kısmî elemanı tamamlama (``lifi_tamamla``).
     Bunlar CCHM'nin ``comp Glue`` kuralının yapı taşlarıdır.

  2) Henüz İMÂL EDİLMEMİŞ iki kuralı, sessizce yanlış cevap vermek yerine
     ``EksikKural`` diye AÇIKÇA yükseltir:
       * ``comp^i U`` (bir tip çizgisinin Glue'ya çevrilmesi) --
         ``cizgi_denkligi``: bir tip çizgisinden denklik üretmek, taşımanın
         denklik olduğunun İSPATINI gerektirir.
       * ``comp^i (Glue ...)`` -- CCHM (2018) §6.2'deki uzun kural.

     Bunların yokluğunun tek somut neticesi şudur: ``ua`` teşkil edilir,
     tip denetiminden geçer, uçları TANIMSAL olarak doğrudur; fakat
     ``ua`` boyunca TAŞIMA indirgenmez. Yani tümel değişmezlik burada
     ifade edilebilir ve aksiyom olarak kullanılabilir, LAKİN hesaplanmaz.
     Bu boşluk ``turetimler.bosluklar()`` kütüğünde de kayıtlıdır.
"""
from __future__ import annotations

from typing import List, Optional, Sequence, Tuple

from .aralik import BIR, DOGRU, SIFIR, YANLIS, Aralik, Kofibrasyon
from . import cekirdek as K
from . import sozdizim as S
from .sozdizim import Terim, Yuz


class EksikKural(NotImplementedError):
    """Bu çekirdekte henüz imâl edilmemiş bir indirgeme kuralı."""


# =====================================================================
#  ∀i.φ  --  bir kofibrasyonun i'den bağımsız en büyük parçası
# =====================================================================
def her_i_icin(kof: Kofibrasyon, ad: str) -> Kofibrasyon:
    """``∀ad. kof``:  ``ad``i kısıtlamayan yüzlerin birleşimi.

    ``kof``un ``ad``den bağımsız EN BÜYÜK alt kofibrasyonudur; CCHM'nin
    Glue hesabında ``δ = ∀i.φ`` diye geçen niceleyicidir.
    """
    return Kofibrasyon([y for y in kof.yuzler
                        if all(a != ad for (a, _) in y)])


# =====================================================================
#  Büzülebilirlikten kısmî elemanı tamamlama
# =====================================================================
def buzukten_tamamla(X: Terim, buzuk: Terim, kof: Kofibrasyon,
                     dallar: Sequence[Tuple[Yuz, Terim]]) -> Terim:
    """``buzuk : isContr X`` ve ``kof`` üzerinde kısmî bir ``X`` elemanı
    verildiğinde, o kısmî elemanı genişleten TAM bir ``X`` elemanı üretir.

    İnşa: merkez ``c = buzuk.1``, büzme ``h = buzuk.2``; netice
    ``hcomp^j [ dallar ↦ h(dal) @ j ] c``.
    """
    c = K.birinci(buzuk)
    h = K.ikinci(buzuk)
    j = K.taze("j")
    j_ar = Aralik.degisken(j)
    yeni = [(y, K.yol_uygula(K.uygula(h, govde), j_ar))
            for (y, govde) in dallar]
    return K.hkomp(X, j, yeni, c)


def lifi_tamamla(A: Terim, B: Terim, e: Terim, b: Terim,
                 dallar: Sequence[Tuple[Yuz, Terim]]) -> Terim:
    """``e : Equiv A B``, ``b : B`` ve ``fiber (e.1) b`` üzerinde kısmî bir
    eleman verildiğinde tam bir lif elemanı üretir."""
    from .kutuphane import lif
    f = K.birinci(e)
    X = lif(A, B, f, b)
    buzuk = K.uygula(K.ikinci(e), b)
    return buzukten_tamamla(X, buzuk, Kofibrasyon([y for (y, _) in dallar]),
                            dallar)


# =====================================================================
#  Henüz imâl edilmemiş kurallar
# =====================================================================
def cizgi_denkligi(ad: str, cizgi: Terim) -> Terim:
    """``(λ ad. cizgi)`` tip çizgisinden ``Denklik cizgi(0) cizgi(1)``.

    İmâl edilmedi: taşımanın bir denklik olduğunun (``isEquiv``) nesne
    dilinde ispatını gerektirir.
    """
    raise EksikKural(
        "cizgi_denkligi (lineToEquiv) imâl edilmedi: bir tip çizgisinden "
        "denklik üretmek, taşımanın denklik olduğunun ispatını gerektirir. "
        "Bunun yokluğunda 'comp^i U' indirgenmez. "
        "Ayrıntı: omega_kategori.turetimler.bosluklar()")


def komp_yapistir(ad: str, A: S.Yapistir, dallar, u0: Terim,
                  baglam=None) -> Terim:
    """``comp^ad (Glue ...) [dallar] u0``.

    İmâl edilmedi: CCHM (2018) §6.2'deki kural.
    """
    raise EksikKural(
        "comp^i (Glue ...) imâl edilmedi (CCHM 2018 §6.2). Bunun neticesi: "
        "'ua' teşkil edilir ve uçları tanımsal doğrudur, fakat 'ua' boyunca "
        "TAŞIMA indirgenmez. "
        "Ayrıntı: omega_kategori.turetimler.bosluklar()")
