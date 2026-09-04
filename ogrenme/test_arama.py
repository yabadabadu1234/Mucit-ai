"""``arama`` paketi sınamaları — M18, M19, M20, M21, M22."""

from __future__ import annotations

import math

import numpy as np
import pytest

from nefs import zirh as bu        # holonomi (Wilson ilmeği)
from nefs import melekeler as gp   # GRAPE optimal kontrol
from ogrenme import optimize as tn # WKB tünel
from ogrenme import optimize as gr


# ══════════════════════════════════════════════════════════════════════
#  1. Grover / Dürr–Høyer (M18)
# ══════════════════════════════════════════════════════════════════════

def test_esit_superpozisyon_normlu():
    p = gr.esit_superpozisyon(1024)
    assert float(np.vdot(p, p).real) == pytest.approx(1.0)


@pytest.mark.parametrize("gamma", [0.3, 1.0, 3.0])
def test_faz_kehaneti_uniter(gamma):
    """Kaynak DOĞRU."""
    f = np.random.default_rng(0).normal(size=64)
    d = gr.faz_kehaneti(f, gamma)
    assert np.abs(np.abs(d) ** 2 - 1).max() < 1e-12


def test_esik_kehaneti_isaretleri():
    f = np.array([0.1, 0.5, 0.9])
    s = gr.esik_kehaneti(f, 0.5)
    assert list(s) == [-1.0, 1.0, 1.0]


def test_difuzyon_uniter_ve_ortalama_yansimasi():
    r = np.random.default_rng(0)
    p = r.normal(size=32) + 1j * r.normal(size=32)
    p /= np.linalg.norm(p)
    d = gr.difuzyon(p)
    assert float(np.linalg.norm(d)) == pytest.approx(1.0, abs=1e-12)
    assert np.abs(gr.difuzyon(d) - p).max() < 1e-12      # involutif


@pytest.mark.parametrize("K", [1, 4, 16, 64])
def test_grover_optimum_turda_yuksek_basari(K):
    N = 1024
    m = gr.en_iyiyi_ara(ne="tur", N=N, K=K)
    e = gr.en_iyiyi_ara(ne="eğri", N=N, K=K, azami_tur=m)
    assert e[m] > 0.95
    assert e[0] == pytest.approx(K / N, rel=1e-9)


@pytest.mark.parametrize("K", [1, 16])
def test_M18_fazla_donmek_zarar(K):
    """Şahit: başarı m ile tekdüze artmıyor."""
    N = 1024
    m = gr.en_iyiyi_ara(ne="tur", N=N, K=K)
    e = gr.en_iyiyi_ara(ne="eğri", N=N, K=K, azami_tur=2 * m)
    assert e[2 * m] < 0.1                # iki katı turda ÇÖKÜYOR
    assert e[m] > 0.95


def test_M18_yanlis_K_varsayimi_basariyi_dusuruyor():
    """K=1 varsayıp K=64 ile koşmak."""
    N = 1024
    f = np.random.default_rng(0).random(N)
    esik = np.sort(f)[64]
    kotu = gr.en_iyiyi_ara(f, ne="grover", esik=esik, m=gr.en_iyiyi_ara(ne="tur", N=N, K=1))
    iyi = gr.en_iyiyi_ara(f, ne="grover", esik=esik, m=gr.en_iyiyi_ara(ne="tur", N=N, K=64))
    assert kotu["K"] == 64
    assert kotu["başarı_olasılığı"] < 0.2
    assert iyi["başarı_olasılığı"] > 0.9


@pytest.mark.parametrize("n", [6, 8, 10])
def test_durr_hoyer_K_bilinmeden_asgariyi_buluyor(n):
    N = 2 ** n
    basari = 0
    sorgular = []
    for t in range(10):
        f = np.random.default_rng(100 + t).random(N)
        d = gr.en_iyiyi_ara(f, ne="dürr", tohum=t)
        basari += d["bulundu_mu"]
        sorgular.append(d["sorgu"])
    assert basari == 10
    assert float(np.mean(sorgular)) < 8 * math.sqrt(N)


def test_durr_hoyer_seyri_tekduze_iniyor():
    f = np.random.default_rng(3).random(512)
    d = gr.en_iyiyi_ara(f, ne="dürr", tohum=1)
    degerler = [x[2] for x in d["seyir"]]
    assert degerler == sorted(degerler, reverse=True)
    assert d["f"] == pytest.approx(d["asgarî"])


# ══════════════════════════════════════════════════════════════════════
#  2. Adiyabatik (M19)
# ══════════════════════════════════════════════════════════════════════

def _tek_asgari(n=4, tohum=5):
    f = np.random.default_rng(tohum).random(2 ** n)
    f[3] = -1.0
    return f


def test_M19_sonlu_T_de_basari_tam_1_degil():
    f = _tek_asgari()
    for T in (1.0, 16.0, 256.0):
        a = gr.en_iyiyi_ara(f, ne="adiyabatik", T=T)
        assert a["tam_1_mi"] is False
        assert a["1_e_uzaklık"] > 0


def test_adiyabatik_basari_T_ile_artiyor():
    f = _tek_asgari()
    b = [gr.en_iyiyi_ara(f, ne="adiyabatik", T=T)["başarı"] for T in (1, 4, 16, 64, 256)]
    assert b == sorted(b)
    assert b[-1] > 0.99
    assert b[0] < 0.3


def test_tayf_araligi_pozitif():
    t = gr.tayf_araligi_asgari(_tek_asgari())
    assert t["g_min"] > 0
    assert 0.0 <= t["s_min"] <= 0.95


def test_baslangic_hamiltonyeninin_temel_durumu_arti():
    n = 3
    H0 = gr._baslangic_H(n)
    e, V = np.linalg.eigh(H0)
    assert e[0] == pytest.approx(-n)
    arti = np.full(2 ** n, 2 ** (-n / 2.0))
    assert abs(abs(V[:, 0] @ arti) - 1.0) < 1e-12


# ══════════════════════════════════════════════════════════════════════
#  3. WKB tünelleme (M20)
# ══════════════════════════════════════════════════════════════════════

def test_wkb_kapali_formla_uyusuyor():
    """Sabit engel: ``γ = (2/ħ)L√(2m(V−E))``."""
    V0, E, L, m = 1.0, 0.2, 3.0, 1.0
    g = tn.kuyudan_cik(ne="tünel", V=lambda x: np.full_like(x, V0),
                       E=E, x1=0.0, x2=L, m=m)["γ"]
    assert g == pytest.approx(2.0 * L * math.sqrt(2 * m * (V0 - E)), rel=1e-9)


def test_M20_gecirgenlik_ussel_kucuk_deneme_ussel_buyuk():
    c = tn.kuyudan_cik(ne="bedel", genislikler=(1, 2, 4, 8))
    T = [d["T"] for d in c]
    deneme = [d["beklenen_deneme"] for d in c]
    assert T == sorted(T, reverse=True)          # tekdüze azalıyor
    assert deneme == sorted(deneme)              # tekdüze artıyor
    assert deneme[-1] / deneme[0] > 1e6          # ÜSTEL, O(1) değil
    for d in c:
        assert d["T"] == pytest.approx(math.exp(-d["γ"]))


def test_engel_altinda_gamma_sifir():
    """``V < E`` bölgesinde katkı yok."""
    g = tn.kuyudan_cik(ne="tünel", V=lambda x: np.full_like(x, 0.1),
                       E=0.5, x1=0.0, x2=5.0)["γ"]
    assert g == pytest.approx(0.0, abs=1e-12)
    assert math.exp(-(g)) == pytest.approx(1.0)


# ══════════════════════════════════════════════════════════════════════
#  4. Wilson holonomisi (M21)
# ══════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("aki", [0.25, 0.37, 0.5, 0.7])
def test_M21_duz_baglanti_trivial_olmayan_holonomi(aki):
    d = bu.aharonov_bohm(8, aki)
    assert d["F_yerel_sıfır_mı"]
    assert d["yüz_var_mı"] is False
    assert d["holonomi_trivial_mi"] is False
    assert d["|W−1|"] > 1e-3


@pytest.mark.parametrize("aki", [0.0, 1.0, 2.0, -3.0])
def test_tam_sayi_akida_holonomi_trivial(aki):
    d = bu.aharonov_bohm(8, aki)
    assert d["holonomi_trivial_mi"]


def test_holonomi_akiya_bagli_kenar_sayisina_degil():
    for N in (4, 8, 32, 128):
        d = bu.aharonov_bohm(N, 0.37)
        assert d["holonomi"] == pytest.approx(
            complex(np.exp(2j * math.pi * 0.37)), abs=1e-12)


def test_holonomi_carpimsal():
    a = [0.3, -0.7, 1.1]
    b = [0.2, 0.5]
    assert bu.holonomi(list(a) + list(b)) == pytest.approx(
        bu.holonomi(a) * bu.holonomi(b))


# ══════════════════════════════════════════════════════════════════════
#  5. GRAPE (M22)
# ══════════════════════════════════════════════════════════════════════

def _sistem(n=4):
    def herm(sd):
        A = (np.random.default_rng(sd).normal(size=(n, n))
             + 1j * np.random.default_rng(sd + 99).normal(size=(n, n)))
        return A + A.conj().T
    psi0 = np.zeros(n, complex); psi0[0] = 1
    hedef = np.zeros(n, complex); hedef[n - 1] = 1
    return herm(1), [herm(2), herm(3)], psi0, hedef


@pytest.mark.parametrize("M", [10, 20, 40])
def test_tam_frechet_gradyani_sonlu_farkla_uyusuyor(M):
    H0, Hk, psi0, hedef = _sistem()
    om = [np.full(M, 0.3), np.full(M, -0.2)]
    j, k = M // 3, 0
    sf = gp.sonlu_fark_gradyani(H0, Hk, om, psi0, hedef, 1.0)[k][j]
    tam = gp.tam_gradyan(H0, Hk, om, psi0, hedef, 1.0)[k][j]
    assert tam == pytest.approx(sf, abs=1e-8)


def test_M22_grape_gradyani_yaklasik_ve_hata_dt_kare():
    """Şahit: kaynağın eşitliği yaklaşımdır, hata ``O(Δt²)``."""
    H0, Hk, psi0, hedef = _sistem()
    oran = []
    for M in (10, 20, 40, 80, 160):
        om = [np.full(M, 0.3), np.full(M, -0.2)]
        j, k = M // 3, 0
        sf = gp.sonlu_fark_gradyani(H0, Hk, om, psi0, hedef, 1.0)[k][j]
        g = gp.grape_gradyani(H0, Hk, om, psi0, hedef, 1.0)[k][j]
        oran.append(abs(g - sf) / (1.0 / M) ** 2)
        if M == 10:
            assert abs(g - sf) > 1e-3            # yaklaşım, eşitlik değil
    # fark/Δt² sabitleniyor → hata tam olarak O(Δt²)
    assert max(oran[1:]) / min(oran[1:]) < 1.5


def test_genel_expm_ozayrisimla_uyusuyor():
    r = np.random.default_rng(0)
    M = r.normal(size=(5, 5)) + 1j * r.normal(size=(5, 5))
    M = M + M.conj().T
    lam, V = np.linalg.eigh(M)
    assert np.abs(gp._genel_expm(M) - (V * np.exp(lam)) @ V.conj().T).max() \
        < 1e-9


def test_grape_sadakati_yukseltiyor():
    H0, Hk, psi0, hedef = _sistem()
    d = gp.grape_kos(H0, Hk, psi0, hedef, 1.0, M=40, tur=200)
    assert d["sadakat"] > 0.99
    assert d["tekdüze_mi"]
    assert d["seyir"][0] < 0.1


def test_sadakat_0_ve_1_arasinda():
    H0, Hk, psi0, hedef = _sistem()
    r = np.random.default_rng(0)
    for _ in range(5):
        om = [r.normal(size=20), r.normal(size=20)]
        F = gp.sadakat(H0, Hk, om, psi0, hedef, 1.0)
        assert 0.0 <= F <= 1.0
