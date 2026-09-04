"""``reel`` paketi sınamaları — M9-M16, M28-M30."""

from __future__ import annotations

import math

import numpy as np
import pytest

from matematik import geometri as ha
from matematik import geometri as km
from matematik import geometri as me


# ══════════════════════════════════════════════════════════════════════
#  1. Hartley
# ══════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("N", [4, 8, 16, 64, 256])
def test_rht_dik_simetrik_involutif(N):
    """Kaynak DOĞRU: RHT dik, simetrik ve kendi tersi."""
    H = ha.hartley(N=N, ne="dizey")
    assert np.abs(H.T @ H - np.eye(N)).max() < 1e-12
    assert np.abs(H @ H - np.eye(N)).max() < 1e-12
    assert np.abs(H - H.T).max() < 1e-12


@pytest.mark.parametrize("N", [8, 64, 512, 1024])
def test_hizli_rht_dizeyle_ayni(N):
    x = np.random.default_rng(0).normal(size=N)
    assert np.abs(ha.hartley(N=N, ne="dizey") @ x - ha.hartley(x)).max() < 1e-10


@pytest.mark.parametrize("N", [16, 64])
def test_rht_kendi_tersi(N):
    x = np.random.default_rng(1).normal(size=N)
    assert np.abs(ha.hartley(ha.hartley(x)) - x).max() < 1e-11


@pytest.mark.parametrize("N", [8, 16, 64])
def test_hartley_evrisim_kaidesi_dogru(N):
    """M29: doğru kaide çarpım değildir."""
    r = np.random.default_rng(2)
    f, g = r.normal(size=N), r.normal(size=N)
    sol = ha.hartley(ha.evrisim(f, g))
    F, G = ha.hartley(f), ha.hartley(g)
    assert np.abs(sol - ha.hartley_evrisim(F, G)).max() < 1e-10


@pytest.mark.parametrize("N", [8, 16, 64])
def test_naif_carpim_kaidesi_YANLIS(N):
    """M29 şahidi: naif çarpım gerçekten tutmuyor."""
    r = np.random.default_rng(2)
    f, g = r.normal(size=N), r.normal(size=N)
    sol = ha.hartley(ha.evrisim(f, g))
    F, G = ha.hartley(f), ha.hartley(g)
    assert np.abs(sol - ha.hartley_evrisim(F, G, naif=True)).max() > 1.0


def test_kosegen_suzgec_ancak_cift_simetrikse_evrisim():
    """M29: RHT'de köşegen çarpan tek başına evrişim değildir."""
    N = 8
    H = ha.hartley(N=N, ne="dizey")
    r = np.random.default_rng(1).normal(size=N)
    assert ha.dolasimli_hata(H.T @ np.diag(r) @ H) > 0.1
    rc = ha.cift_simetrik_yap(r)
    assert ha.dolasimli_hata(H.T @ np.diag(rc) @ H) < 1e-12
    # kıyas: QFT'de her r için evrişim
    F = np.fft.fft(np.eye(N), axis=0) / math.sqrt(N)
    assert ha.dolasimli_hata((F.conj().T @ np.diag(r) @ F).real) < 1e-12


def test_cift_simetrik_yap_idempotent():
    r = np.random.default_rng(3).normal(size=16)
    a = ha.cift_simetrik_yap(r)
    assert np.abs(ha.cift_simetrik_yap(a) - a).max() < 1e-14


def test_spektral_suzgec_yuksek_kipi_bastiriyor():
    N = 256
    t = np.arange(N)
    x = (np.sin(2 * math.pi * 3 * t / N)
         + 0.5 * np.sin(2 * math.pi * 61 * t / N))
    r = (np.minimum(t, N - t) <= 8).astype(float)
    y = ha.spektral_suzgec(x, r)
    F = np.fft.rfft(y)
    assert abs(F[61]) < 1e-9
    assert abs(F[3]) > 1.0


# ══════════════════════════════════════════════════════════════════════
#  2. Karmaşık gömme (M28)
# ══════════════════════════════════════════════════════════════════════

def _hermitesel(N, tohum):
    r = np.random.default_rng(tohum)
    A = r.normal(size=(N, N)); A = A + A.T
    B = r.normal(size=(N, N)); B = B - B.T
    return A + 1j * B


@pytest.mark.parametrize("N", [2, 3, 5])
def test_J_kare_eksi_birim(N):
    J = km.J_dizeyi(N)
    assert np.abs(J @ J + np.eye(2 * N)).max() == 0.0


@pytest.mark.parametrize("N", [2, 3, 5])
def test_HR_simetrik_ve_J_ile_komut_ediyor(N):
    """Kaynağın blok biçimi DOĞRU — cos/sin kapalı biçimi buna dayanıyor."""
    HR = km.reel_hamiltonyen(_hermitesel(N, N))
    J = km.J_dizeyi(N)
    assert np.abs(HR - HR.T).max() < 1e-12
    assert np.abs(J @ HR - HR @ J).max() < 1e-12


def test_hermitesel_olmayan_reddediliyor():
    with pytest.raises(ValueError):
        km.reel_hamiltonyen(np.array([[0.0, 1.0], [0.0, 0.0]]))


@pytest.mark.parametrize("t", [0.2, 0.6, 1.5, 3.0])
def test_M28_dogru_isaret_exp_eksi_iHt_veriyor(t):
    N = 3
    H = _hermitesel(N, 7)
    psi = np.random.default_rng(1).normal(size=N) + 1j * \
        np.random.default_rng(2).normal(size=N)
    lam, V = np.linalg.eigh(H)
    ref = (V * np.exp(-1j * lam * t)) @ (V.conj().T @ psi)
    got = km.karmasik_coz(km.reel_evrim(H, t) @ km.reel_goem(psi))
    assert np.abs(got - ref).max() < 1e-12


@pytest.mark.parametrize("t", [0.6, 1.5, 3.0])
def test_M28_kaynagin_isareti_YANLIS(t):
    """Şahit: ``+J·H_ℝ`` zamanı tersine çeviriyor."""
    N = 3
    H = _hermitesel(N, 7)
    psi = np.random.default_rng(1).normal(size=N) + 1j * \
        np.random.default_rng(2).normal(size=N)
    lam, V = np.linalg.eigh(H)
    ref = (V * np.exp(-1j * lam * t)) @ (V.conj().T @ psi)
    kotu = km.karmasik_coz(km.kaynak_isaretiyle_evrim(H, t)
                           @ km.reel_goem(psi))
    assert np.abs(kotu - ref).max() > 0.5
    # ama exp(+iHt) ile uyuşuyor: işaret hatası, başka bir şey değil
    ters = (V * np.exp(+1j * lam * t)) @ (V.conj().T @ psi)
    assert np.abs(kotu - ters).max() < 1e-12


def test_diklik_denetimi_isaret_hatasini_yakalamiyor():
    """İki işaret de SO(2N)'de — diklik sınaması yetersiz bir ölçüt."""
    H = _hermitesel(3, 7)
    for U in (km.reel_evrim(H, 0.6), km.kaynak_isaretiyle_evrim(H, 0.6)):
        d = km.so_2n_mi(U)
        assert d["SO_da_mı"]
        assert d["det"] == pytest.approx(1.0, abs=1e-10)


@pytest.mark.parametrize("t", [0.2, 1.0, 2.5])
def test_cos_sin_kapali_bicimi_dogru(t):
    """Kaynağın kapalı biçimi geçerli (doğru işaretle)."""
    H = _hermitesel(4, 11)
    assert np.abs(km.reel_evrim_cos_sin(H, t) - km.reel_evrim(H, t)).max() \
        < 1e-12


def test_gomme_gidis_donusu():
    v = np.random.default_rng(0).normal(size=5) + 1j * \
        np.random.default_rng(1).normal(size=5)
    assert np.abs(km.karmasik_coz(km.reel_goem(v)) - v).max() == 0.0


# ══════════════════════════════════════════════════════════════════════
#  3. Meleke kapıları
# ══════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("D", [me.HIZLI_BOYUT, 64])
def test_kirkbir_kapi_ve_hepsi_dik(D):
    K = me.meleke_kapilari(D)
    assert len(K) == 41
    rap = me.diklik_raporu(K)
    assert rap["dik_olanlarda_azamî"] < 1e-12
    assert rap["dik_olmayan"] == []


def test_varsayilan_ve_hizli_boyut():
    assert me.VARSAYILAN_BOYUT == 512
    assert me.HIZLI_BOYUT == 128


def test_carpanli_uygulama_tam_dizeyle_ayni():
    D = 64
    K = me.meleke_kapilari(D)
    x = np.random.default_rng(3).normal(size=D)
    M = np.eye(D)
    for k in K:
        M = k.dizey() @ M
    assert np.abs(me.zincir_uygula(K, x) - M @ x).max() < 1e-11


@pytest.mark.parametrize("tohum", range(4))
def test_M9_householder_butun_durumu_negatiflemiyor(tohum):
    r = np.random.default_rng(tohum)
    d = 8
    v = r.normal(size=d); v /= np.linalg.norm(v)
    U = me.kapi_kur("yansıma", v=v)
    psi = r.normal(size=d); psi /= np.linalg.norm(psi)
    assert np.linalg.norm(U(psi) + psi) > 0.5          # −Ψ DEĞİL
    assert np.linalg.norm(U(psi)) == pytest.approx(1.0)  # norm korunuyor
    # paralel hâlde gerçekten −Ψ
    assert np.linalg.norm(U(v) + v) < 1e-12


def test_M9_genlik_ancak_izdusumle_siliniyor():
    r = np.random.default_rng(0)
    d = 8
    v = r.normal(size=d); v /= np.linalg.norm(v)
    psi = r.normal(size=d); psi /= np.linalg.norm(psi)
    U, P = me.kapi_kur("yansıma", v=v), me.kapi_kur("silme", v=v)
    assert abs(v @ U(psi)) > 1e-6                 # yansımada bileşen KALIYOR
    assert abs(v @ P(psi)) < 1e-12                # izdüşümde siliniyor
    assert np.linalg.norm(P(psi)) < 1.0           # ama norm düşüyor (üniter değil)
    assert P.dik is False


def test_M11_kok_p_kosegeni_uniter_degil():
    P = np.array([0.4, 0.3, 0.2, 0.1])
    M = me.kapi_kur("ölçüm", P=P)
    A = M.dizey()
    assert M.dik is False
    assert np.abs(A.T @ A - np.eye(4)).max() > 0.5
    assert np.abs(A.T @ A - np.diag(P)).max() < 1e-12   # AᵀA = diag(P)


def test_M13_so2_uniter_ve_uc_aralik():
    for th in (0.02, 0.5, math.pi / 4):
        G = me.kapi_kur("so2", theta=th, D=2).dizey()
        assert np.abs(G.T @ G - np.eye(2)).max() < 1e-14
    sek = me.kapi_kur("so2", theta=math.pi / 4, D=2).dizey() @ np.array([1.0, 0.0])
    assert sek[0] ** 2 == pytest.approx(0.5)
    yakin = me.kapi_kur("so2", theta=0.02, D=2).dizey() @ np.array([1.0, 0.0])
    assert yakin[0] ** 2 > 0.999


@pytest.mark.parametrize("D", [8, 16, 32])
def test_M14_grup_komutatoru_cebirde_degil(D):
    g = me.grup_komutatoru_cebirde_mi(D)
    assert g["grup_yatkın_sapması"] > 0.1 * g["grup_komutatörü_normu"]
    assert g["üreteç_yatkın_sapması"] < 1e-10       # üreteçler so(D)'de


def test_M16_carpim_usteli_ancak_komut_edende_esit():
    c = me.carpim_trotter_farki()
    assert c["genel_fark"] > 0.1
    assert c["komut_eden_fark"] < 1e-12


def test_M30_genel_isaret_olculemez():
    m = me.genel_isaret_olculemez()
    assert m["genel_işaret_farkı"] < 1e-14
    assert m["alt_uzay_işareti_farkı"] > 0.1


def test_permutasyon_ve_kosegen_dik():
    D = 16
    r = np.random.default_rng(0)
    for k in (me.kapi_kur("permütasyon", perm=r.permutation(D)),
              me.kapi_kur("işaret", isaret=r.choice([-1.0, 1.0], size=D))):
        M = k.dizey()
        assert np.abs(M.T @ M - np.eye(D)).max() < 1e-14


def test_givens_zinciri_dik():
    D = 12
    r = np.random.default_rng(1)
    ciftler = [(0, 1), (2, 3), (1, 4), (5, 9)]
    G = me.kapi_kur("givens", aci=r.uniform(0, 6, 4), ciftler=ciftler, D=D)
    M = G.dizey()
    assert np.abs(M.T @ M - np.eye(D)).max() < 1e-13


def test_hartley_kapisi_involutif():
    D = 32
    K = me.kapi_kur("hartley", D=D)
    x = np.random.default_rng(0).normal(size=D)
    assert np.abs(K(K(x)) - x).max() < 1e-11
