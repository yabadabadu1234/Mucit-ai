"""``hesap`` paketi sınamaları — M23, M24, M25/M26, M27."""

from __future__ import annotations

import math
from fractions import Fraction

import numpy as np
import pytest

from matematik import geometri as ga
from matematik import geometri as pa
from matematik import geometri as sa


# ══════════════════════════════════════════════════════════════════════
#  1. Galois halkası — kaynak DOĞRU
# ══════════════════════════════════════════════════════════════════════

def test_kok2_ve_i_tam():
    assert ga.KOK2 * ga.KOK2 == ga.Z8(2, 0, 0, 0, 0)
    assert ga.I_BIRIMI * ga.I_BIRIMI == -ga.BIR
    assert ga.KOK2.kayan().real == pytest.approx(math.sqrt(2))
    assert abs(ga.KOK2.kayan().imag) < 1e-15


def test_zeta_sekizinci_kuvveti_bir():
    z = ga.BIR
    for _ in range(8):
        z = z * ga.ZETA
    assert z == ga.BIR


def test_halka_cebri_tutarlı():
    a, b = ga.Z8(1, 2, -1, 3, 1), ga.Z8(-2, 0, 4, 1, 2)
    assert (a + b).kayan() == pytest.approx(a.kayan() + b.kayan())
    assert (a * b).kayan() == pytest.approx(a.kayan() * b.kayan())
    assert (a - b).kayan() == pytest.approx(a.kayan() - b.kayan())
    assert a.norm_kare().kayan().real == pytest.approx(abs(a.kayan()) ** 2)


@pytest.mark.parametrize("n", [10, 50, 200, 500])
def test_clifford_T_normu_TAM_bir(n):
    """Halkada kapalı: ``‖v‖²`` tamsayı aritmetiğinde tam 1."""
    dizi = list(np.random.default_rng(n).choice(
        ["H", "T", "S", "X", "Z"], size=n))
    t = ga.tam_devre(dizi)
    assert t["norm_kare_tam_bir_mi"]
    assert t["norm_kare"] == ga.BIR


@pytest.mark.parametrize("n", [10, 100, 500])
def test_tam_devre_float_devreyle_uyusuyor(n):
    dizi = list(np.random.default_rng(n + 1).choice(
        ["H", "T", "S", "X", "Z"], size=n))
    assert np.abs(ga.tam_devre(dizi)["kayan"]
                  - ga.kayan_devre(dizi)).max() < 1e-12


def test_T8_tam_olarak_birim():
    """Float'ta eşik gerekir, tam aritmetikte cevap kesindir."""
    dizi = ["H"] + ["T"] * 8 + ["H"]
    t = ga.tam_devre(dizi)
    assert t["durum"][0] == ga.BIR and t["durum"][1] == ga.SIFIR
    f = ga.kayan_devre(dizi)
    assert not (f[0] == 1.0 and f[1] == 0.0)      # float'ta TAM eşit değil
    assert np.abs(f - np.array([1.0, 0.0])).max() < 1e-14


def test_float32_hatasi_float64ten_buyuk():
    dizi = list(np.random.default_rng(9).choice(
        ["H", "T", "S", "X", "Z"], size=2000))
    f64 = ga.kayan_devre(dizi, np.complex128)
    f32 = ga.kayan_devre(dizi, np.complex64)
    h64 = abs(float(np.vdot(f64, f64).real) - 1.0)
    h32 = abs(float(np.vdot(f32, f32).real) - 1.0)
    assert h32 > 1000 * h64


def test_kapilar_uniter():
    for K in (ga.z8_kapi("H"), ga.z8_kapi("T"), ga.z8_kapi("S"), ga.z8_kapi("X"),
              ga.z8_kapi("Z")):
        M = ga.z8_kayan(K)
        assert np.abs(M.conj().T @ M - np.eye(2)).max() < 1e-14


# ══════════════════════════════════════════════════════════════════════
#  2. p-adik (M23, M24, M25)
# ══════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("p", [2, 3, 5])
def test_ultrametrik_hic_ihlal_edilmiyor(p):
    r = pa.ultrametrik_ihlali(p, 5000)
    assert r["ihlal"] == 0
    assert r["izoseles_tam_mı"]           # |x|≠|y| iken EŞİTLİK


def test_p_norm_bilinen_degerler():
    assert pa.p_norm(Fraction(12), 2) == Fraction(1, 4)      # 12 = 2²·3
    assert pa.p_norm(Fraction(1, 8), 2) == 8
    assert pa.p_norm(Fraction(3, 5), 2) == 1
    assert pa.p_norm(0, 2) == 0
    assert pa.p_degeri(Fraction(0), 3) is None


def test_p_tam_mi():
    assert pa.p_tam_mi(Fraction(3, 5), 2)
    assert not pa.p_tam_mi(Fraction(1, 2), 2)
    assert pa.p_tam_mi(Fraction(1, 2), 3)


def test_M23_p_adik_toplam_normalizasyon_degil():
    """Normalize durumlarda p-adik toplam 1 çıkmıyor."""
    k = pa.normalizasyon_kiyasi(2)
    for d in k:
        assert d["arşimet_bir_mi"]                 # hepsi normalize
    assert any(not d["p_adik_bir_mi"] for d in k)  # ama p-adik toplam 1 değil
    yarim = [d for d in k if d["durum"] == "(½,½,½,½)"][0]
    assert yarim["p_adik"] == 16


def test_M23_p_adik_toplam_uniter_altinda_korunmuyor():
    u = pa.uniter_altinda_korunuyor_mu(2, 200)
    assert u["dönüşüm_dik_mi"]
    assert u["arşimet_korunan"] == 200          # arşimet HER ZAMAN korunuyor
    assert u["p_adik_korunan"] < 200            # p-adik korunmuyor


def test_M24_float_hatasi_rasyonelde_de_var():
    f = pa.float_hatasi_rasyonelde()
    assert f["0.1+0.2==0.3"] is False
    assert abs(f["0.1+0.2-0.3"]) > 0
    assert f["on_kere_bir_mi"] is False
    assert f["tam_aritmetikte"] == 1.0          # tam aritmetikte sorun yok


def test_p_adik_yakinsama_arsimetin_tersi():
    y = pa.p_adik_yakinsama(2, 10)
    assert y["arşimet_büyüyor_mu"]
    assert y["p_adik_küçülüyor_mu"]
    f = y["p_adik_ardışık_fark"]
    assert f == sorted(f, reverse=True)


# ══════════════════════════════════════════════════════════════════════
#  3. Saklama (M27)
# ══════════════════════════════════════════════════════════════════════

def test_keyfi_durum_gercekten_imkansiz():
    """İtiraz KEYFÎ durum için doğrudur."""
    assert not sa.keyfi_durum_maliyeti(100)["evren_atomundan_fazla_mı"]
    assert sa.keyfi_durum_maliyeti(300)["evren_atomundan_fazla_mı"]
    assert sa.keyfi_durum_maliyeti(300)["log10_katsayı_sayısı"] == \
        pytest.approx(300 * math.log10(2), rel=1e-9)


@pytest.mark.parametrize("N", [64, 256, 1024])
def test_M27_kararlayici_400_kubitin_otesinde_kosuyor(N):
    """Yapılı sınıfta N>400 sıradan bir hesap."""
    st = sa.Kararlayici(N)
    for i in range(N):
        st.H(i)
    for i in range(N - 1):
        st.CNOT(i, i + 1)
    assert st.bellek_bayt() < 10e6                # 10 MB'tan az
    o = st.olc(0, tohum=0)
    assert o["netice"] in (0, 1)
    m = sa.kararlayici_maliyeti(N)
    assert m["log10_bayt"] < 8                    # keyfî: 10^{0.3N}
    assert m["keyfî_log10_bayt"] > m["log10_bayt"]


def test_kararlayici_bell_baglantisi():
    """Doğruluk sağlaması: |Φ⁺⟩'de iki ölçüm hep eşit."""
    for t in range(50):
        st = sa.Kararlayici(2).H(0).CNOT(0, 1)
        a = st.olc(0, tohum=t)
        b = st.olc(1, tohum=t)
        assert a["belirli_mi"] is False           # ilki rastgele
        assert b["belirli_mi"] is True            # ikincisi belirli
        assert a["netice"] == b["netice"]


def test_kararlayici_H_iki_kere_birim():
    st = sa.Kararlayici(3)
    x0, z0, r0 = st.x.copy(), st.z.copy(), st.r.copy()
    st.H(1).H(1)
    assert np.array_equal(st.x, x0) and np.array_equal(st.z, z0)
    assert np.array_equal(st.r, r0)


def test_kararlayici_sifir_durumu_belirli():
    st = sa.Kararlayici(4)
    o = st.olc(2)
    assert o["belirli_mi"] is True
    assert o["netice"] == 0
    st.X(2)
    assert st.olc(2)["netice"] == 1


@pytest.mark.parametrize("N,chi", [(6, 1), (8, 3), (10, 4)])
def test_mps_normu_tam_vektorle_uyusuyor(N, chi):
    m = sa.MPS.rastgele(N, chi, tohum=2).normalize()
    v = m.tam_vektor()
    assert m.norm_kare() == pytest.approx(1.0, abs=1e-10)
    assert float(np.vdot(v, v).real) == pytest.approx(1.0, abs=1e-10)


def test_mps_carpim_durumu_dolasiksiz():
    m = sa.MPS.carpim_durumu([0.3, 1.1, 2.0])
    v = m.tam_vektor()
    assert float(np.vdot(v, v).real) == pytest.approx(1.0, abs=1e-12)
    assert m.bellek_sayi() == 6                   # χ=1: 3 kubit × 2


def test_mps_buyuk_N_de_tam_vektor_reddediliyor():
    with pytest.raises(ValueError):
        sa.MPS.rastgele(24, 2).tam_vektor()


def test_M27_hacim_yasasinda_MPS_keyfiye_geri_donuyor():
    """Dürüstlük şartı: bedava sonsuzluk yok."""
    for N in (20, 40, 80):
        m = sa.mps_maliyeti(N, 2 ** (N // 2))
        assert m["log10_bayt"] > m["keyfî_log10_bayt"] - 3
    # düşük χ'de ise çok ucuz
    m = sa.mps_maliyeti(400, 32)
    assert m["log10_bayt"] < 8
    assert m["keyfî_log10_bayt"] > 100
