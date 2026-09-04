"""``idrak.sekil`` sınamaları — ispatlı şekil kestirimi ya da sükût."""

from __future__ import annotations

import os
from fractions import Fraction

import numpy as np
import pytest

from nefs import musahede as sk
from nefs.musahede import ARC, gorevleri_getir

VERI_VAR = os.path.isdir(os.path.join(ARC, "training"))
veri_gerek = pytest.mark.skipif(not VERI_VAR, reason="ARC verisi yok")


def _c(gs, cs):
    return [(np.zeros(a, dtype=np.int64), np.zeros(b, dtype=np.int64))
            for a, b in zip(gs, cs)]


# ══════════════════════════════════════════════════════════════════════
#  Kipler
# ══════════════════════════════════════════════════════════════════════

def test_ayni_sekil_oran_bir_olarak_bulunuyor():
    k = sk.kalip(_c([(3, 4), (5, 2), (7, 7)], [(3, 4), (5, 2), (7, 7)]), ne="şekil")
    assert k.ad == "oran|oran"
    assert k.satir[1] == Fraction(1) and k.sutun[1] == Fraction(1)
    assert k.kestir(np.zeros((9, 11))) == (9, 11)


def test_olcekleme_orani_tam_kesirle():
    k = sk.kalip(_c([(2, 3), (4, 1)], [(6, 9), (12, 3)]), ne="şekil")
    assert k.satir[1] == Fraction(3) and k.sutun[1] == Fraction(3)
    assert k.kestir(np.zeros((5, 5))) == (15, 15)


def test_kucultme_orani():
    k = sk.kalip(_c([(6, 6), (9, 3)], [(2, 2), (3, 1)]), ne="şekil")
    assert k.satir[1] == Fraction(1, 3)
    assert k.kestir(np.zeros((12, 6))) == (4, 2)


def test_devrik_capraz_kiple_yakalaniyor():
    k = sk.kalip(_c([(3, 5), (2, 7)], [(5, 3), (7, 2)]), ne="şekil")
    assert k.ad == "capraz|capraz"
    assert k.kestir(np.zeros((4, 9))) == (9, 4)


def test_sabit_sekil():
    k = sk.kalip(_c([(3, 5), (2, 7), (9, 1)], [(1, 1), (1, 1), (1, 1)]), ne="şekil")
    assert k.ad == "sabit|sabit"
    assert k.kestir(np.zeros((30, 30))) == (1, 1)


def test_oran_sabitten_once_tercih_ediliyor():
    """Girdiler aynı boyutta iken hem sabit hem oran tutar; genelleyen oran."""
    k = sk.kalip(_c([(2, 2), (2, 2)], [(2, 2), (2, 2)]), ne="şekil")
    assert k.ad == "oran|oran"
    assert k.kestir(np.zeros((5, 5))) == (5, 5)      # sabit olsa (2,2) derdi


# ══════════════════════════════════════════════════════════════════════
#  Sükût — kaide yoksa uydurma yok
# ══════════════════════════════════════════════════════════════════════

def test_kaide_yoksa_None():
    assert sk.kalip(_c([(3, 3), (4, 4)], [(5, 2), (1, 9)]),
                             ne="şekil") is None


def test_bos_gosterimde_None():
    assert sk.kalip([], ne="şekil") is None


def test_tam_sayi_cikmayan_oran_susuyor():
    """1/3 kaidesi 4 satırlık girdide tam sayı vermez → kestirim yok."""
    k = sk.kalip(_c([(6, 6), (9, 9)], [(2, 2), (3, 3)]), ne="şekil")
    assert k is not None
    assert k.kestir(np.zeros((4, 6))) is None


def test_ARC_sinirini_asan_kestirim_susuyor():
    k = sk.kalip(_c([(2, 2), (3, 3)], [(8, 8), (12, 12)]), ne="şekil")
    assert k.kestir(np.zeros((4, 4))) == (16, 16)
    assert k.kestir(np.zeros((10, 10))) is None      # 40 > 30


def test_kayan_nokta_yuvarlamasi_sahte_kaide_uretmiyor():
    """Oranlar Fraction ile tam tutuluyor; 7/3 ≠ 2.333… kabulü yok."""
    k = sk.kalip(_c([(3, 3), (6, 6)], [(7, 7), (14, 14)]), ne="şekil")
    assert k.satir[1] == Fraction(7, 3)
    assert k.kestir(np.zeros((3, 3))) == (7, 7)
    assert k.kestir(np.zeros((4, 4))) is None        # 28/3 tam değil


# ══════════════════════════════════════════════════════════════════════
#  Resmî küme üzerinde — iddia edilen sayılar
# ══════════════════════════════════════════════════════════════════════

@veri_gerek
def test_egitim_kumesinde_kapsam_ve_isabet():
    d = sk.kalip(ne="kapsam", gorevler=gorevleri_getir("training"))
    assert d["kapsam"] > 0.80
    assert d["isabet_kapsayınca"] > 0.99


@veri_gerek
def test_degerlendirme_kumesinde_de_tutuyor():
    """Çözücünün yenildiği kümede bile ŞEKİL kaidesi ayakta."""
    d = sk.kalip(ne="kapsam", gorevler=gorevleri_getir("evaluation"))
    assert d["kapsam"] > 0.65
    assert d["isabet_kapsayınca"] > 0.95


@veri_gerek
def test_kaide_sinir_aginin_sekil_basindan_kat_kat_iyi():
    """Ölçülen kıyas: şekil başı doğrulamada 0.027 idi."""
    d = sk.kalip(ne="kapsam", gorevler=gorevleri_getir("evaluation"))
    isabet = d["kapsam"] * d["isabet_kapsayınca"]     # sükût = yanlış say
    assert isabet > 0.6
