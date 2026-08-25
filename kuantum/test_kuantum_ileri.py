"""``kuantum.surekli``, ``kuantum.topolojik``, ``kuantum.eniyileme`` sınamaları.

Her sınama bir **iddiayı** tartıyor; birçoğu iddianın tersinin
gerçekten bozulduğunu da gösteriyor (şahit sınamaları).
"""

from __future__ import annotations

import itertools
import math

import numpy as np
import pytest

from kuantum import eniyileme as en
from kuantum import surekli as cv
from kuantum import topolojik as tp


# ══════════════════════════════════════════════════════════════════════
#  1. CV — kesilmiş Fock uzayı
# ══════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("N", [8, 16, 64])
def test_komutator_yalniz_son_satirda_bozuluyor(N):
    r = cv.komutator_sapmasi(N)
    assert r["alt_blok_azamî_sapma"] < 1e-13
    assert r["son_köşegen"].real == pytest.approx(-N)


@pytest.mark.parametrize("N", [10, 30, 80])
def test_uslu_ters_hermityen_uretecte_tam_uniter(N):
    """Kesmede üniterlik BOZULMUYOR — yanlış yazdığım yer."""
    for U in (cv.yer_degistirme(2.5, N), cv.sikistirma(0.8, N),
              cv.kubik_faz(0.3, N)):
        assert cv.uniterlik_sapmasi(U) < 1e-12


def test_uslu_ters_hermityen_olmayani_reddediyor():
    with pytest.raises(ValueError):
        cv.expm(np.array([[1.0, 2.0], [0.0, 1.0]]))


@pytest.mark.parametrize("al", [0.5, 1.0, 2.0])
def test_yer_degistirme_vakumdan_tutarli_durum(al):
    N = 60
    psi = cv.yer_degistirme(al, N) @ cv.vakum(N)
    assert np.abs(psi - cv.tutarli_durum(al, N)).max() < 1e-12
    # Poisson: ⟨n⟩ = |α|²
    assert float(cv.foton_dagilimi(psi) @ np.arange(N)) == pytest.approx(
        al * al, rel=1e-9)


def test_tutarli_durum_belirsizligi_asgari():
    b = cv.kuadratur_belirsizligi(cv.tutarli_durum(1.5, 80))
    assert b["çarpım"] == pytest.approx(0.5, rel=1e-9)


@pytest.mark.parametrize("r,N", [(0.5, 160), (1.0, 320)])
def test_sikistirma_heisenbergte_e_ussu_eksi_r(r, N):
    k = 12
    S = cv.sikistirma(r, N)
    sol = (S.conj().T @ cv.konum(N) @ S)[:k, :k]
    sag = (math.exp(-r) * cv.konum(N))[:k, :k]
    assert np.abs(sol - sag).max() / np.abs(sag).max() < 1e-6


def test_sikistirma_kucuk_N_de_BOZULUYOR():
    """Şahit: kesme yetersizse bağıntı sağlanmaz — 'N fark etmez' değil."""
    k, r, N = 12, 1.5, 40
    S = cv.sikistirma(r, N)
    sol = (S.conj().T @ cv.konum(N) @ S)[:k, :k]
    sag = (math.exp(-r) * cv.konum(N))[:k, :k]
    assert np.abs(sol - sag).max() / np.abs(sag).max() > 1.0


def test_sikistirma_belirsizlik_carpimini_korur():
    b = cv.kuadratur_belirsizligi(cv.sikistirma(1.0, 320) @ cv.vakum(320))
    assert b["çarpım"] == pytest.approx(0.5, rel=1e-6)
    assert b["Δx"] == pytest.approx(math.exp(-1.0) / math.sqrt(2), rel=1e-6)


@pytest.mark.parametrize("th", [0.3, math.pi / 4, 1.2])
def test_isik_bolucu_foton_sayisini_koruyor(th):
    N = 10
    a = cv.yok_et(N)
    I = np.eye(N, dtype=complex)
    Ntop = np.kron(a.conj().T @ a, I) + np.kron(I, a.conj().T @ a)
    B = cv.isik_bolucu(th, 0.4, N)
    psi = np.kron(cv.fock(1, N), cv.fock(0, N))
    out = B @ psi
    assert complex(out.conj() @ (Ntop @ out)).real == pytest.approx(1.0,
                                                                    abs=1e-9)
    p2 = abs(out[np.ravel_multi_index((0, 1), (N, N))]) ** 2
    assert p2 == pytest.approx(math.sin(th) ** 2, abs=1e-9)


@pytest.mark.parametrize("N", [8, 32, 128])
def test_kerr_kosegen_kesme_hatasiz(N):
    assert cv.uniterlik_sapmasi(cv.kerr(0.7, N)) < 1e-14
    assert np.abs(cv.kerr(0.7, N) - np.diag(np.diag(cv.kerr(0.7, N)))).max() == 0


def test_kubik_faz_yakinsamasi_gamma_ile_kotulesir():
    kucuk = cv.kesme_hatasi(lambda n: cv.kubik_faz(0.1, n), 40, alt=6)
    buyuk = cv.kesme_hatasi(lambda n: cv.kubik_faz(2.0, n), 40, alt=6)
    assert kucuk["azamî_fark"] < 1e-12
    assert buyuk["azamî_fark"] > 1e-3


@pytest.mark.parametrize("a,b", [(0.3, 0.7), (1.0, 1.0), (2.5, -0.5)])
def test_kesirsel_fourier_grup_ozelligi(a, b):
    N = 64
    L = cv.kesirsel_fourier(a, N) @ cv.kesirsel_fourier(b, N)
    assert np.abs(L - cv.kesirsel_fourier(a + b, N)).max() < 1e-12


def test_kesirsel_fourier_a1_x_i_p_ye_goturuyor():
    N, k = 64, 32
    F = cv.kesirsel_fourier(1.0, N)
    sol = (F.conj().T @ cv.konum(N) @ F)[:k, :k]
    assert np.abs(sol - cv.momentum(N)[:k, :k]).max() < 1e-12


# ══════════════════════════════════════════════════════════════════════
#  2. Topolojik
# ══════════════════════════════════════════════════════════════════════

def test_fibonacci_F_gercel_simetrik_ve_involutif():
    F = tp.fibonacci_F()
    assert np.abs(F.imag).max() == 0.0
    assert np.abs(F - F.T).max() < 1e-15
    assert np.abs(F @ F - np.eye(2)).max() < 1e-14


@pytest.mark.parametrize("ad", ["F", "R", "B"])
def test_fibonacci_dizeyleri_uniter(ad):
    M = {"F": tp.fibonacci_F(), "R": tp.fibonacci_R(),
         "B": tp.fibonacci_B()}[ad]
    assert np.abs(M.conj().T @ M - np.eye(2)).max() < 1e-14


def test_yang_baxter_saglaniyor():
    s1, s2 = tp.orgu_ureticleri()
    assert tp.yang_baxter_hatasi(s1, s2) < 1e-14


@pytest.mark.parametrize("a,b", [(-3, 3), (-4, 2), (-1, 1)])
def test_yang_baxter_yanlis_fazlarla_BOZULUYOR(a, b):
    """Şahit: R'nin fazları keyfî değil."""
    F = tp.fibonacci_F()
    R = np.diag([np.exp(a * 1j * math.pi / 5), np.exp(b * 1j * math.pi / 5)])
    B = np.linalg.inv(F) @ R @ F
    assert tp.yang_baxter_hatasi(R, B) > 1e-3


def test_orgu_kelimesi_ters_ile_sadelesir():
    U = tp.orgu_kelimesi((1, 2, -2, -1))
    assert np.abs(U - np.eye(2)).max() < 1e-13


def test_orgu_grubu_sonlu_degil_ve_mesafe_iniyor():
    r = tp.orgu_yogunlugu(11)
    n = [x[1] for x in r["seyir"]]
    d = [x[2] for x in r["seyir"]]
    assert n[-1] > 4 * n[len(n) // 2]          # üstel büyüme
    assert d == sorted(d, reverse=True)        # tekdüze inen
    assert d[-1] < 0.1
    # bulunan kelime gerçekten o mesafeyi veriyor mu?
    H = np.array([[1, 1], [1, -1]], dtype=complex) / math.sqrt(2)
    assert tp._hedef_mesafesi(tp.orgu_kelimesi(r["kelime"]), H) == \
        pytest.approx(r["en_iyi_mesafe"], abs=1e-12)


@pytest.mark.parametrize("n", [2, 3, 4])
def test_majorana_antikomutasyonu(n):
    h = tp.antikomutator_hatasi(tp.majorana(n))
    assert h["köşegen_hata"] < 1e-12
    assert h["köşegen_dışı_hata"] < 1e-12
    assert h["hermityenlik_hatası"] < 1e-12


@pytest.mark.parametrize("n", [2, 3, 4])
def test_jw_zinciri_olmadan_BOZULUYOR(n):
    """Şahit: antikomütasyon Z zincirinden geliyor."""
    h = tp.antikomutator_hatasi(tp.jw_zincirsiz_majorana(n))
    assert h["köşegen_dışı_hata"] == pytest.approx(2.0)


@pytest.mark.parametrize("L", [2, 3, 4, 5])
def test_yuzey_kodu_ortak_kenar_0_veya_2(L):
    assert set(tp.YuzeyKodu(L).ortak_kenar_sayilari()) <= {0, 2}


@pytest.mark.parametrize("L", [2, 3, 4, 5])
def test_yuzey_kodu_iki_mantiksal_kubit(L):
    m = tp.YuzeyKodu(L).mantiksal_kubit_sayisi()
    assert m["kubit"] == 2 * L * L
    assert m["bağımsız_dengeleyici"] == 2 * L * L - 2
    assert m["mantıksal_kubit"] == 2


def test_yuzey_kodu_L2_tam_dizeyle_komut_ediyor():
    assert tp.YuzeyKodu(2).komutator_hatasi_tam() == 0.0


def test_gf2_sira_bilinen_ornek():
    M = np.array([[1, 1, 0], [0, 1, 1], [1, 0, 1]], dtype=np.uint8)
    assert tp._gf2_sira(M) == 2          # üçüncü satır ilk ikisinin toplamı
    assert tp._gf2_sira(np.eye(4, dtype=np.uint8)) == 4


# ══════════════════════════════════════════════════════════════════════
#  3. Eniyileme
# ══════════════════════════════════════════════════════════════════════

def test_baslangic_hamiltonyeninin_temel_durumu_arti():
    n = 3
    H0 = en.baslangic_hamiltonyeni(n)
    e, V = np.linalg.eigh(H0)
    assert e[0] == pytest.approx(-n)
    arti = np.full(2 ** n, 2 ** (-n / 2.0))
    assert abs(abs(V[:, 0] @ arti) - 1.0) < 1e-12


def test_maxcut_hamiltonyeni_dogru_kesim_veriyor():
    # üçgen: en iyi kesim 2 kenar
    hc = en.maxcut_hamiltonyeni(3, [(0, 1), (1, 2), (2, 0)])
    assert hc.min() == pytest.approx(-2.0)
    assert hc.max() == pytest.approx(0.0)      # hepsi aynı taraf
    # 4-döngü: en iyi kesim 4
    hc4 = en.maxcut_hamiltonyeni(4, [(0, 1), (1, 2), (2, 3), (3, 0)])
    assert hc4.min() == pytest.approx(-4.0)


def test_adiyabatik_basari_T_ile_artiyor():
    n = 4
    H0 = en.baslangic_hamiltonyeni(n)
    H1 = np.diag(en.maxcut_hamiltonyeni(
        n, [(0, 1), (1, 2), (2, 3), (3, 0)])).astype(complex)
    b = [en.adiyabatik_kos(H0, H1, T)["başarı"]
         for T in (0.5, 2.0, 8.0, 32.0)]
    assert b == sorted(b)
    assert b[-1] > 0.99


def test_adiyabatik_kisa_T_de_basarisiz():
    """Şahit: adiyabatiklik bedava değil."""
    n = 4
    H0 = en.baslangic_hamiltonyeni(n)
    H1 = np.diag(en.maxcut_hamiltonyeni(
        n, [(0, 1), (1, 2), (2, 3), (3, 0)])).astype(complex)
    assert en.adiyabatik_kos(H0, H1, 0.5)["başarı"] < 0.3


def test_tayf_araligi_ucta_kapaniyor():
    n = 4
    H0 = en.baslangic_hamiltonyeni(n)
    H1 = np.diag(en.maxcut_hamiltonyeni(
        n, [(0, 1), (1, 2), (2, 3), (3, 0)])).astype(complex)
    t = en.tayf_araligi(H0, H1)
    assert t["hedef_temel_katlılık"] == 2
    assert t["uç_aralık"] < 1e-9
    assert t["Δ_min"] > 0.0


@pytest.mark.parametrize("nq", [6, 8])
def test_qaoa_kosegen_yol_tam_dizeyle_ayni(nq):
    ke = [(i, (i + 1) % nq) for i in range(nq)]
    h = en.maxcut_hamiltonyeni(nq, ke)
    g, b = np.array([0.4, 0.9]), np.array([0.7, 0.2])
    psi = en.qaoa_durumu(nq, h, g, b)
    Hb = np.zeros((2 ** nq, 2 ** nq), dtype=complex)
    for i in range(nq):
        Hb += en._tek_kubit(en._X, i, nq)
    lam, V = np.linalg.eigh(Hb)
    ps = np.full(2 ** nq, 2 ** (-nq / 2.0), dtype=complex)
    for gg, bb in zip(g, b):
        ps = np.exp(-1j * gg * h) * ps
        ps = (V * np.exp(-1j * bb * lam)) @ (V.conj().T @ ps)
    assert np.abs(psi - ps).max() < 1e-13


def test_qaoa_durumu_normlu():
    h = en.maxcut_hamiltonyeni(5, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)])
    psi = en.qaoa_durumu(5, h, [0.3, 1.1], [0.9, 0.2])
    assert float(np.linalg.norm(psi)) == pytest.approx(1.0, abs=1e-12)


def test_qaoa_p_arttikca_kotulesmiyor():
    n = 4
    hc = en.maxcut_hamiltonyeni(n, [(0, 1), (1, 2), (2, 3), (3, 0),
                                    (0, 2), (1, 3)])
    d = [en.qaoa_eniyile(n, hc, p, tohum=3)["beklenen"] for p in (1, 2)]
    assert d[1] <= d[0] + 1e-6
    assert d[0] < float(hc.mean())          # p=1 bile |+⟩'dan iyi
    assert d[1] == pytest.approx(hc.min(), abs=1e-4)


@pytest.mark.parametrize("k", range(6))
def test_parametre_kaydirma_sonlu_farkla_uyusuyor(k):
    nq = 3
    Hh = np.zeros((8, 8), dtype=complex)
    for i in range(nq):
        Hh += en._tek_kubit(en._Z, i, nq)

    def dev(theta):
        psi = np.zeros(8, dtype=complex)
        psi[0] = 1.0
        for i in range(nq):
            c, sn = math.cos(theta[i] / 2), -1j * math.sin(theta[i] / 2)
            psi = en._tek_kubit(np.array([[c, sn], [sn, c]], dtype=complex),
                                i, nq) @ psi
        for i in range(nq):
            R = np.diag([np.exp(-1j * theta[nq + i] / 2),
                         np.exp(1j * theta[nq + i] / 2)])
            psi = en._tek_kubit(R, i, nq) @ psi
        return float((psi.conj() @ (Hh @ psi)).real)

    th = np.array([0.3, 1.1, 2.2, 0.7, 1.9, 2.8])
    assert en.parametre_kaydirma(dev, th, k) == pytest.approx(
        en._sonlu_fark(dev, th, k), abs=1e-8)


def test_kaydirma_sarti_ihlal_edilince_YANLIS():
    """Şahit: ``G² = I`` şartı süs değil."""
    r = en.kaydirma_sarti_ihlali()
    assert abs(r["kaydırma"] - r["sonlu_fark"]) > 0.5
