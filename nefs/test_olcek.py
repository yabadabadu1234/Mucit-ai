"""``olcek.hiz`` sınamaları — M31, M32, M33, M34."""

from __future__ import annotations

import math

import pytest

from nefs import hiz


# ══════════════════════════════════════════════════════════════════════
#  L4 raporu DOĞRU — yeniden hesaplanıyor
# ══════════════════════════════════════════════════════════════════════

def test_net_guc():
    assert hiz.cati(ne="güç") == pytest.approx(629.2e12, rel=1e-6)


@pytest.mark.parametrize("D,flop", [(4096, 1.51e9), (2048, 0.377e9),
                                    (1024, 0.0944e9), (512, 0.0236e9)])
def test_flop_token_raporla_uyusuyor(D, flop):
    assert hiz.cati(D=D, ne="flop") == pytest.approx(flop, rel=2e-3)


@pytest.mark.parametrize("D,metin_MB", [(4096, 1.67), (2048, 6.67),
                                        (1024, 26.68), (512, 106.72)])
def test_l4_metin_hizi_raporla_uyusuyor(D, metin_MB):
    """Raporun bütün aritmetiği doğru — birebir tutuyor."""
    assert hiz.cati(D=D, ne="hız")["metin_MB_sn"] == pytest.approx(metin_MB,
                                                             rel=2e-3)


@pytest.mark.parametrize("D,tensor_GB", [(4096, 3.41), (2048, 6.83),
                                         (1024, 13.66), (512, 27.32)])
def test_l4_tensor_hizi_raporla_uyusuyor(D, tensor_GB):
    assert hiz.cati(D=D, ne="hız")["tensör_GB_sn"] == pytest.approx(tensor_GB,
                                                              rel=2e-3)


def test_flop_katsayisi_dokumdan_geliyor():
    """82 (41 meleke) + 4 (RHT) + 2 (KAN) + 2 (Hodge) = 90."""
    assert hiz.FLOP_KATSAYISI == 82 + 4 + 2 + 2


def test_throughput_D_kare_ile_ters_orantili():
    a, b = hiz.cati(D=512, ne="hız"), hiz.cati(D=1024, ne="hız")
    assert a["token_sn"] / b["token_sn"] == pytest.approx(4.0, rel=1e-9)


# ══════════════════════════════════════════════════════════════════════
#  M34: çatı modeli / yığın şartı
# ══════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("D", [512, 4096])
def test_M34_B1_de_yogunluk_bir_ve_bellek_bagli(D):
    c = hiz.cati(D=D, B=1)
    assert c["yoğunluk"] == pytest.approx(1.0, rel=0.05)
    assert c["bellek_bağlı_mı"]
    assert c["tepe_gücün_kaçta_biri"] > 100      # ölçülen ~524


@pytest.mark.parametrize("D", [512, 4096])
def test_M34_buyuk_yiginda_flop_bagli(D):
    assert hiz.cati(D=D, B=4096)["bellek_bağlı_mı"] is False


@pytest.mark.parametrize("D", [512, 4096])
def test_M34_yigin_esigi(D):
    e = hiz.cati(D=D, ne="eşik")
    assert e > 1
    assert hiz.cati(D=D, B=e)["bellek_bağlı_mı"] is False
    assert hiz.cati(D=D, B=e // 2)["bellek_bağlı_mı"] is True


def test_aritmetik_yogunluk_B_ile_artiyor():
    y = [hiz.cati(D=512, B=B, ne="yoğunluk") for B in (1, 8, 64, 512, 4096)]
    assert y == sorted(y)
    assert y[0] < 2 and y[-1] > 1000


# ══════════════════════════════════════════════════════════════════════
#  M31/M32: aritmetik
# ══════════════════════════════════════════════════════════════════════

def test_M31_log_kare_400_degil():
    a = hiz.log_aritmetigi(1e12)
    assert a["log2_kare"] == pytest.approx(1589.1, rel=1e-3)
    assert a["risale_log2_kare"] == 400.0
    # hiçbir taban 400 vermiyor
    for anahtar in ("log2_kare", "log10_kare", "ln_kare"):
        assert abs(a[anahtar] - 400.0) > 100.0


def test_M32_sikistirma_orani_1e28_degil():
    a = hiz.log_aritmetigi(1e12)
    assert a["N3_bolu_log2kare"] == pytest.approx(6.293e32, rel=1e-3)
    assert a["N3_bolu_log2kare"] / a["risale_K"] > 1e4
    # N² alınsaydı da 1e28 çıkmıyor
    assert abs(math.log10(a["N2_bolu_log2kare"]) - 28.0) > 1.0


# ══════════════════════════════════════════════════════════════════════
#  M33: boyut denetimi
# ══════════════════════════════════════════════════════════════════════

def test_M33_carpim_gercek_donanimla_mertebelerce_celisiyor():
    d = hiz.esdegers_hiz_boyut_denetimi()
    assert d["mertebe_farkı_D512"] > 30
    assert d["mertebe_farkı_D4096"] > 30
    # aynı külliyattaki L4 raporu ile kıyas
    assert d["gerçek_D512_bayt_sn"] == pytest.approx(1.067e8, rel=1e-2)


def test_M33_iki_belge_ayni_kulliyatta_celisiyor():
    """Bir külliyatta 22+ mertebe çelişki açıkça giderilmelidir."""
    risale = 1e18 * 1e9              # 10^18 GB/sn → bayt/sn
    rapor512 = hiz.cati(D=512, ne="hız")["metin_MB_sn"] * 1e6
    rapor4096 = hiz.cati(D=4096, ne="hız")["metin_MB_sn"] * 1e6
    assert math.log10(risale / rapor512) == pytest.approx(19.0, abs=0.5)
    assert math.log10(risale / rapor4096) == pytest.approx(20.8, abs=0.5)
    # formül harfiyen uygulanırsa fark daha da büyük
    d = hiz.esdegers_hiz_boyut_denetimi()
    assert d["mertebe_farkı_D512"] == pytest.approx(37.0, abs=1.0)


# ══════════════════════════════════════════════════════════════════════
#  Yerel ölçüm
# ══════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("D", [128, 512])
def test_yerel_olcum_flop_sayisi_dogru(D):
    m = hiz.yerel_olcum(D, B=1, tekrar=1)
    assert m["FLOP"] == pytest.approx(2.0 * D * D * 41)
    assert m["FLOP_sn"] > 0
    assert m["süre_ms"] > 0
    assert m["sonlu_mu"]          # float32 taşmıyor (ölçek 1/√D)


def test_yerel_olcumde_yigin_token_hizini_artiriyor():
    """Çatı etkisi bu CPU'da da görünüyor."""
    a = hiz.yerel_olcum(512, B=1, tekrar=2)
    b = hiz.yerel_olcum(512, B=64, tekrar=2)
    assert b["token_sn"] > 3 * a["token_sn"]
    assert b["GFLOP_sn"] > a["GFLOP_sn"]
