"""akis test takımı.

Ölçüt bağımsız bilinen cevaba göre: MCF'nin çember kapalı çözümü,
Fokker–Planck'ın kütle korunumu ve durağan hâli, Jacobi özdeşliği,
grup üyeliği, Morse bağıntısı ve stereografik izdüşümün tersi.

Çalıştırma: ``python3 -m pytest akis/test_akis.py -q``
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from akis import hacim as hc
from akis import lie as li
from akis import tikiz as tk


def _cember(n, r):
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    return hc.Egri(np.stack([r * np.cos(t), r * np.sin(t)], axis=1))


# ══════════════════════════════════════════════════════════════════════
#  1. Ortalama eğrilik akışı
# ══════════════════════════════════════════════════════════════════════

def test_egri_gecersiz_girdiyi_reddediyor():
    with pytest.raises(ValueError):
        hc.Egri(np.zeros((2, 2)))          # 3'ten az köşe
    with pytest.raises(ValueError):
        hc.Egri(np.zeros((5, 3)))          # düzlem değil


def test_cember_alan_ve_uzunluk():
    for r in (0.5, 1.0, 2.0):
        e = _cember(400, r)
        assert e.alan() == pytest.approx(math.pi * r * r, rel=1e-4)
        assert e.uzunluk() == pytest.approx(2 * math.pi * r, rel=1e-4)


def test_cember_egrilik_bir_bolu_r():
    """``|H| = 1/r`` ve merkeze doğru."""
    for r in (0.5, 1.0, 3.0):
        e = _cember(400, r)
        H = e.egrilik_vektoru()
        assert np.allclose(np.linalg.norm(H, axis=1), 1.0 / r, rtol=1e-3)
        # merkeze doğru: H · x < 0
        assert np.all(np.sum(H * e.x, axis=1) < 0)


@pytest.mark.parametrize("T", [0.05, 0.15, 0.30, 0.45])
def test_mcf_cember_kapali_cozumle_uyusuyor(T):
    e = _cember(200, 1.0)
    r = hc.mcf_kos(e, T)
    olculen = math.sqrt(r["egri"].alan() / math.pi)
    assert olculen == pytest.approx(hc.cember_kapali_cozum(1.0, T),
                                    rel=2e-3), T


def test_cember_kapali_cozum_sinirlari():
    assert hc.cember_kapali_cozum(1.0, 0.0) == pytest.approx(1.0)
    assert hc.cember_kapali_cozum(2.0, 2.0) == pytest.approx(0.0, abs=1e-12)
    with pytest.raises(ValueError):
        hc.cember_kapali_cozum(1.0, 0.6)      # çökmüş
    with pytest.raises(ValueError):
        hc.cember_kapali_cozum(0.0, 0.1)


def test_mcf_alani_azaltiyor():
    """MCF alanı HER ZAMAN azaltır (``d/dt A = −∫|H|²``)."""
    rng = np.random.default_rng(0)
    egriler = [
        _cember(120, 1.0),
        hc.Egri(np.stack([1.6 * np.cos(np.linspace(0, 2 * np.pi, 120,
                                                   endpoint=False)),
                          0.6 * np.sin(np.linspace(0, 2 * np.pi, 120,
                                                   endpoint=False))],
                         axis=1)),
        hc.Egri(_cember(120, 1.0).x + 0.05 * rng.normal(size=(120, 2))),
    ]
    for e in egriler:
        r = hc.mcf_kos(e, 0.15)
        a = r["alanlar"]
        assert a[-1] < a[0]
        assert all(a[i] <= a[i - 1] + 1e-12 for i in range(1, len(a)))


def test_mcf_uyarlamali_adim_sabitten_iyi():
    """Sabit ``dt`` çöküşe yakın CFL'i ihlal eder; ölçülüyor."""
    T = 0.45
    e1 = _cember(200, 1.0)
    uyarlamali = math.sqrt(hc.mcf_kos(e1, T)["egri"].alan() / math.pi)
    e2 = _cember(200, 1.0)
    h0 = e2.uzunluk() / e2.n
    sabit = math.sqrt(hc.mcf_kos(e2, T, dt=0.2 * h0 * h0)["egri"].alan()
                      / math.pi)
    kapali = hc.cember_kapali_cozum(1.0, T)
    assert abs(uyarlamali - kapali) < abs(sabit - kapali) / 10


# ══════════════════════════════════════════════════════════════════════
#  2. Fokker–Planck ve log-yoğunluk
# ══════════════════════════════════════════════════════════════════════

def _kurulum(N=256):
    h = 2 * np.pi / N
    x = np.arange(N) * h
    f = 2.0 * np.cos(x) + 0.5 * np.cos(2 * x)
    rho0 = np.ones(N) / (2 * np.pi)
    return h, x, f, rho0


def test_fokker_planck_kutle_koruyor():
    h, x, f, rho0 = _kurulum()
    for T in (0.5, 2.0, 8.0):
        r = hc.fokker_planck_kos(rho0, f, h, T)
        assert r["kütle_sapması"] < 1e-14, T
        assert r["negatif_var_mı"] is False


def test_fokker_planck_duragan_hale_yakinsiyor():
    h, x, f, rho0 = _kurulum()
    sapmalar = [hc.fokker_planck_kos(rho0, f, h, T)["durağan_sapma"]
                for T in (0.5, 2.0, 8.0)]
    assert all(a > b for a, b in zip(sapmalar, sapmalar[1:]))
    assert sapmalar[-1] < 1e-3


def test_log_yogunluk_fokker_planck_ile_ayni():
    """F 52.4 doğru: iki denklem aynı çözüme gidiyor."""
    h, x, f, rho0 = _kurulum()
    dt = 0.2 * h * h
    u = np.log(rho0)
    for _ in range(4000):
        u = hc.log_yogunluk_adimi(u, f, h, dt)
    rho_log = np.exp(u)
    rho_log = rho_log / (np.sum(rho_log) * h)
    assert np.all(rho_log > 0)          # yapı gereği pozitif
    rho_fp = hc.fokker_planck_kos(rho0, f, h, 4000 * dt)["rho"]
    rho_fp = rho_fp / (np.sum(rho_fp) * h)
    assert float(np.sum(np.abs(rho_log - rho_fp)) * h) < 1e-3


def test_gibbs_hacim_kapali_formla_uyusuyor():
    """``d/dt Vol = −2∫‖∇f‖²e^{−f}`` — sıfır DEĞİL."""
    h, x, f, _ = _kurulum()
    for ff in (2.0 * np.cos(x), np.cos(x) + 0.5 * np.cos(2 * x),
               0.7 * np.sin(3 * x)):
        olculen = hc.gibbs_hacim_degisimi(ff, h)
        kapali = -2.0 * float(np.sum(hc._merkezi_fark(ff, h) ** 2
                                     * np.exp(-ff)) * h)
        assert olculen == pytest.approx(kapali, rel=1e-3)
        assert olculen < 0                       # kesin negatif
    # Sabit f: sıfır
    assert hc.gibbs_hacim_degisimi(np.zeros(256), h) == pytest.approx(0.0)


# ══════════════════════════════════════════════════════════════════════
#  3. K23: eyer noktası
# ══════════════════════════════════════════════════════════════════════

def test_eyer_olcutu_asgariyi_gecirmiyor():
    asgari = np.diag([1.0, 2.0, 3.0])
    eyer = np.diag([-1.0, 2.0, 3.0])
    azami = np.diag([-1.0, -2.0, -3.0])
    # Eski ölçüt (λ_max > 0) asgarîyi de geçirir:
    assert np.max(np.linalg.eigvalsh(asgari)) > 0
    # Doğru ölçüt geçirmiyor:
    assert hc.eyer_mi(asgari) is False
    assert hc.eyer_mi(eyer) is True
    assert hc.eyer_mi(azami) is False
    assert hc.morse_indisi(asgari) == 0
    assert hc.morse_indisi(eyer) == 1
    assert hc.morse_indisi(azami) == 3


def test_kacis_yonu_alcaltiyor():
    H = np.diag([-1.0, 2.0, 3.0])
    v = hc.kacis_yonu(H)
    assert float(v @ H @ v) < 0
    yukselen = np.linalg.eigh(H)[1][:, -1]
    assert float(yukselen @ H @ yukselen) > 0


def test_eyer_olcutu_simetriklestiriyor():
    """Simetrik olmayan girdide de doğru davranmalı."""
    H = np.array([[-1.0, 5.0], [0.0, 2.0]])
    assert hc.eyer_mi(H) is True
    assert hc.morse_indisi(H) == 1


# ══════════════════════════════════════════════════════════════════════
#  4. Lie
# ══════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("n", [2, 3, 5, 8])
def test_jacobi_dizey_komutatorunde_teorem(n):
    rng = np.random.default_rng(n)
    for _ in range(20):
        X, Y, Z = (rng.normal(size=(n, n)) for _ in range(3))
        olcek = max(np.linalg.norm(X) * np.linalg.norm(Y)
                    * np.linalg.norm(Z), 1e-300)
        assert li.jacobi_hatasi(X, Y, Z) / olcek < 1e-13


def test_so3_yapi_sabitleri_levi_civita():
    L = li.so3_uretecleri()
    f = li.yapi_sabitleri(L)
    for a in range(3):
        for b in range(3):
            for c in range(3):
                assert abs(complex(f[a, b, c]).real
                           - li._levi_civita(a, b, c)) < 1e-12
    assert li.yapi_sabiti_jacobi_hatasi(f) < 1e-12


@pytest.mark.parametrize("n", [2, 3, 4])
def test_sun_boyutu_ve_jacobi(n):
    T = li.sun_uretecleri(n)
    assert len(T) == n * n - 1
    for t in T:
        assert np.max(np.abs(t + t.conj().T)) < 1e-12   # anti-Hermitesel
        assert abs(complex(np.trace(t))) < 1e-12        # izsiz
    f = li.yapi_sabitleri(T)
    assert li.yapi_sabiti_jacobi_hatasi(f) < 1e-10


def test_keyfi_yapi_sabiti_jacobiyi_saglamiyor():
    """Yapı sabitleriyle verilen cebirde Jacobi bir KISITTIR."""
    keyfi = np.random.default_rng(0).normal(size=(3, 3, 3))
    assert li.yapi_sabiti_jacobi_hatasi(keyfi) > 1.0


def test_sun_gecersiz_n():
    with pytest.raises(ValueError):
        li.sun_uretecleri(1)


def test_yapi_sabitleri_lie_cebri_olmayani_reddediyor():
    """Braket tabanın dışına çıkıyorsa hata verilmeli."""
    rng = np.random.default_rng(1)
    kotu = [rng.normal(size=(4, 4)) for _ in range(2)]
    with pytest.raises(ValueError):
        li.yapi_sabitleri(kotu)


def test_so_izdusumu_dik():
    """Simetrik ile antisimetrik parçalar Frobenius'ta diktir."""
    rng = np.random.default_rng(2)
    M = rng.normal(size=(5, 5))
    A = li.so_izdusumu(M)
    S = M - A
    assert np.max(np.abs(A + A.T)) < 1e-12
    assert np.max(np.abs(S - S.T)) < 1e-12
    assert abs(float(np.sum(A * S))) < 1e-12


@pytest.mark.parametrize("olcek", [0.1, 1.0, 5.0])
def test_uslu_harita_gruba_goturuyor(olcek):
    rng = np.random.default_rng(3)
    A = li.so_izdusumu(rng.normal(size=(5, 5))) * olcek
    E = li.uslu_harita(A)
    assert li.so_n_mi(E)
    assert np.max(np.abs(E - li.uslu_harita(A, "seri"))) < 1e-9


def test_seri_buyuk_normda_gruptan_cikiyor():
    rng = np.random.default_rng(4)
    A = li.so_izdusumu(rng.normal(size=(5, 5))) * 25.0
    assert li.so_n_mi(li.uslu_harita(A, "ozayrisim"))
    assert not li.so_n_mi(li.uslu_harita(A, "seri"))


def test_uslu_harita_gecersiz_yontem():
    with pytest.raises(ValueError):
        li.uslu_harita(np.zeros((2, 2)), "başka")


def test_grup_adimi_grupta_kaliyor():
    rng = np.random.default_rng(5)
    X = li.en_yakin_dik(rng.normal(size=(4, 4)))
    if np.linalg.det(X) < 0:
        X[:, 0] *= -1
    assert li.so_n_mi(X)
    naif = X.copy()
    for _ in range(10):
        g = rng.normal(size=(4, 4))
        X = li.grup_adimi(X, g, 0.1)
        naif = naif - 0.1 * g
        assert li.so_n_mi(X, tol=1e-10)
    assert not li.so_n_mi(naif)


def test_so_n_mi_yansimayi_eliyor():
    Q = np.diag([1.0, 1.0, -1.0])
    assert np.max(np.abs(Q.T @ Q - np.eye(3))) < 1e-15    # O(3)'te
    assert li.so_n_mi(Q) is False                          # SO(3)'te DEĞİL
    assert li.so_n_mi(np.eye(3)) is True


def test_en_yakin_dik_en_iyi():
    """Kutup ayrışımı Frobenius'ta EN İYİ dik yaklaşımdır (K28)."""
    rng = np.random.default_rng(6)
    M = li.en_yakin_dik(rng.normal(size=(5, 5))) \
        + 0.08 * rng.normal(size=(5, 5))
    Q = li.en_yakin_dik(M)
    assert np.max(np.abs(Q.T @ Q - np.eye(5))) < 1e-12
    d = np.linalg.norm(Q - M, "fro")
    for _ in range(300):
        R = li.en_yakin_dik(rng.normal(size=(5, 5)))
        assert np.linalg.norm(R - M, "fro") >= d - 1e-9
    # Simetrikleştirme dikliği GETİRMİYOR:
    S = (M + M.T) / 2
    assert np.max(np.abs(S.T @ S - np.eye(5))) > 0.1


# ══════════════════════════════════════════════════════════════════════
#  5. Tıkız
# ══════════════════════════════════════════════════════════════════════

def test_zorlayicilik_kure_asgarisiyle():
    assert tk.zorlayici_mi(lambda x: float(x @ x), 3)["zorlayıcı_görünüyor"]
    assert tk.zorlayici_mi(lambda x: float(x @ x) ** 2 - float(x @ x),
                           3)["zorlayıcı_görünüyor"]
    # Tek yönde artan: ORTALAMA aldatır, ASGARÎ aldatmaz
    r = tk.zorlayici_mi(lambda x: float(x[0]) ** 2, 3)
    assert r["zorlayıcı_görünüyor"] is False
    assert not tk.zorlayici_mi(lambda x: -float(x @ x),
                               3)["zorlayıcı_görünüyor"]
    assert not tk.zorlayici_mi(lambda x: float(x[0]),
                               3)["zorlayıcı_görünüyor"]


def test_baslangic_seviyesi_bos_kume_vermiyor():
    f = lambda x: float(x @ x) - 3.0
    for x0 in ([2.0, -1.0], [0.0, 0.0], [10.0, 10.0]):
        r0 = tk.baslangic_seviyesi(f, np.array(x0))
        assert f(np.array(x0)) <= r0


def test_alt_seviye_sinirlilik_ve_bosluk():
    f = lambda x: float(x @ x) - 3.0
    for r, bos in ((3.0, False), (0.0, False), (-2.9, False), (-3.5, True)):
        d = tk.alt_seviye_tikiz_mi(f, r, 2)
        assert d["sınırlı"] is True
        assert d["nokta_bulundu"] is (not bos), (r, bos)
    # Zorlayıcı olmayan: sınırsız
    assert tk.alt_seviye_tikiz_mi(lambda x: float(x[0]), 0.0,
                                  2)["sınırlı"] is False


def test_barriyer_kirpmasiz_kesin_reddediyor():
    assert math.isinf(tk.barriyer([-0.5, 1.0]))
    assert math.isinf(tk.barriyer([0.0, 1.0]))
    assert math.isfinite(tk.barriyer([-0.5, 1.0], eps=1e-8))
    assert tk.barriyer([1.0, 1.0]) == pytest.approx(0.0)
    assert tk.barriyer([math.e, 1.0]) == pytest.approx(-1.0)
    # İçeride kırpma fark etmiyor:
    assert tk.barriyer([0.1, 0.5]) == pytest.approx(
        tk.barriyer([0.1, 0.5], eps=1e-8))


def test_barriyerli_hedef():
    assert tk.barriyerli_hedef(1.0, [1.0], 0.0) == pytest.approx(1.0)
    assert math.isinf(tk.barriyerli_hedef(1.0, [-1.0], 0.5))
    with pytest.raises(ValueError):
        tk.barriyerli_hedef(1.0, [1.0], -0.1)


def test_ic_nokta_yolu_kisiti_ihlal_etmiyor():
    hedef = lambda x: float(x[0] + x[1])
    kisit = lambda x: np.array([x[0], x[1], 1.0 - x[0] - x[1]])
    r = tk.ic_nokta_yolu(hedef, kisit, np.array([0.3, 0.3]),
                         tau0=1.0, azalma=0.25, tur=8, ic_adim=600)
    for tau, x, fx, mg in r["yol"]:
        assert mg > 0, (tau, x)               # kısıt hiç ihlal edilmedi
    # Çözüme (0,0) yaklaşıyor:
    assert r["yol"][-1][2] < 1e-3
    assert np.max(np.abs(r["x"])) < 1e-3


def test_ic_nokta_gecersiz_baslangic():
    hedef = lambda x: float(x[0])
    kisit = lambda x: np.array([x[0]])
    with pytest.raises(ValueError):
        tk.ic_nokta_yolu(hedef, kisit, np.array([-1.0]))


def test_kritik_noktalar_ve_morse_bagintisi():
    """``f = x⁴ − 2x² + y²``: iki asgarî, bir eyer; Σ(−1)^k M_k = χ(ℝ²) = 1."""
    def grad(v):
        x, y = v
        return np.array([4 * x ** 3 - 4 * x, 2 * y])

    def hess(v):
        x, y = v
        return np.array([[12 * x ** 2 - 4, 0.0], [0.0, 2.0]])

    baslangiclar = [[a, b] for a in (-1.5, -0.3, 0.0, 0.3, 1.5)
                    for b in (-1.0, 0.0, 1.0)]
    kn = tk.kritik_noktalar(grad, hess, baslangiclar)
    assert len(kn) == 3, [k["x"] for k in kn]
    indisler = sorted(k["indis"] for k in kn)
    assert indisler == [0, 0, 1]
    assert all(not k["dejenere"] for k in kn)
    mb = tk.morse_bagintisi(indisler, 2)
    assert mb["M"] == [2, 1, 0]
    assert mb["alterne_toplam"] == 1        # χ(ℝ²)


def test_morse_bagintisi_gecersiz_indis():
    with pytest.raises(ValueError):
        tk.morse_bagintisi([3], 2)
    with pytest.raises(ValueError):
        tk.morse_bagintisi([-1], 2)


def test_esitlik_imkansiz_dizilimi_eliyor():
    """K27: ``≥`` geçirir, ``=`` geçirmez."""
    chi = 1
    sahte = tk.morse_bagintisi([0] * 5, 2)
    assert sahte["alterne_toplam"] >= chi        # ≥ ölçütü GEÇİYOR
    assert sahte["alterne_toplam"] != chi        # = ölçütü ELİYOR


def test_stereografik_gidis_donus():
    rng = np.random.default_rng(0)
    for _ in range(500):
        x = rng.normal(size=3) * 10 ** rng.uniform(-3, 3)
        p = tk.kure_izdusumu(x)
        assert abs(float(np.linalg.norm(p)) - 1.0) < 1e-12   # küre üstünde
        assert np.max(np.abs(tk.ters_kure_izdusumu(p) - x)) \
            < 1e-6 * max(1.0, float(np.max(np.abs(x))))


def test_sonsuz_kuzey_kutbuna_gidiyor():
    for R in (1e2, 1e4, 1e8):
        p = tk.kure_izdusumu(np.array([R, 0.0]))
        assert p[-1] > 1 - 1e-3
    assert tk.kure_izdusumu(np.zeros(2))[-1] == pytest.approx(-1.0)


def test_kuzey_kutbu_reddediliyor():
    with pytest.raises(ValueError):
        tk.ters_kure_izdusumu(np.array([0.0, 0.0, 1.0]))


@pytest.mark.parametrize("modul", [hc, li, tk])
def test_rapor_uretiliyor(modul):
    m = modul.rapor()
    assert isinstance(m, str) and len(m) > 200
