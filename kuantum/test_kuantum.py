"""kuantum test takımı.

Ölçüt yine bağımsız bilinen cevaba göre: Pauli cebri, bilinen kapı
özdeşlikleri, QFT'nin kapalı formu, tam temsil edilen fazda QPE'nin
kesinliği, Trotter mertebeleri, bilinen şekillerin Betti sayıları.

Bir de **hızlanmanın neticeyi değiştirmediği** ayrıca sınanıyor:
eksen görünümüyle kapı uygulamak ile tam dizey kurmak birebir aynı
durumu vermeli.

Çalıştırma: ``python3 -m pytest kuantum/test_kuantum.py -q``
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from kuantum import devre as dv
from kuantum import kapilar as kp
from kuantum import tda


# ══════════════════════════════════════════════════════════════════════
#  1. Kapılar
# ══════════════════════════════════════════════════════════════════════

def test_pauli_komutasyon_ve_antikomutasyon():
    eps = {("X", "Y"): "Z", ("Y", "Z"): "X", ("Z", "X"): "Y"}
    for (a, b), c in eps.items():
        assert np.allclose(kp.komutator(kp.PAULI[a], kp.PAULI[b]),
                           2j * kp.PAULI[c])
        # ters sıra işaret değiştirmeli:
        assert np.allclose(kp.komutator(kp.PAULI[b], kp.PAULI[a]),
                           -2j * kp.PAULI[c])
    for a in "XYZ":
        for b in "XYZ":
            bekle = 2 * kp.I2 if a == b else np.zeros((2, 2))
            assert np.allclose(
                kp.antikomutator(kp.PAULI[a], kp.PAULI[b]), bekle), (a, b)


KAPILAR = {
    "I": kp.I2, "X": kp.X, "Y": kp.Y, "Z": kp.Z, "H": kp.H,
    "S": kp.S_, "Sdg": kp.Sdg, "T": kp.T_, "Tdg": kp.Tdg,
    "Rx": kp.Rx(1.1), "Ry": kp.Ry(-0.7), "Rz": kp.Rz(2.3),
    "U1": kp.U1(0.7), "U2": kp.U2(0.3, 0.9), "U3": kp.U3(0.4, 0.5, 0.6),
    "CNOT": kp.CNOT, "CZ": kp.CZ, "SWAP": kp.SWAP, "iSWAP": kp.iSWAP,
    "CRx": kp.CRx(0.8), "CRz": kp.CRz(0.8),
    "RXX": kp.RXX(0.6), "RYY": kp.RYY(0.6), "RZZ": kp.RZZ(0.6),
    "Toffoli": kp.TOFFOLI, "Fredkin": kp.FREDKIN,
}


@pytest.mark.parametrize("ad", sorted(KAPILAR))
def test_butun_kapilar_uniter(ad):
    assert kp.uniter_mi(KAPILAR[ad]), ad


@pytest.mark.parametrize("n", [1, 2, 3, 4])
def test_molmer_sorensen_uniter(n):
    assert kp.uniter_mi(kp.molmer_sorensen(n, 0.7, 0.2))


def test_molmer_sorensen_cift_n_de_ghz():
    """Ölçülen kaide: MS(π/2) çift ``n``de tam GHZ veriyor."""
    for n in (2, 4, 6):
        U = kp.molmer_sorensen(n, np.pi / 2, 0.0)
        v = np.zeros(2 ** n, dtype=complex); v[0] = 1
        c = U @ v
        assert np.count_nonzero(np.abs(c) > 1e-9) == 2, n
        assert abs(abs(c[0]) ** 2 - 0.5) < 1e-9
        assert abs(abs(c[-1]) ** 2 - 0.5) < 1e-9
    for n in (3, 5):
        U = kp.molmer_sorensen(n, np.pi / 2, 0.0)
        v = np.zeros(2 ** n, dtype=complex); v[0] = 1
        assert np.count_nonzero(np.abs(U @ v) > 1e-9) > 2, n


@pytest.mark.parametrize("ad,A,B", [
    ("H²=I", kp.H @ kp.H, kp.I2),
    ("HXH=Z", kp.H @ kp.X @ kp.H, kp.Z),
    ("HZH=X", kp.H @ kp.Z @ kp.H, kp.X),
    ("HYH=-Y", kp.H @ kp.Y @ kp.H, -kp.Y),
    ("S²=Z", kp.S_ @ kp.S_, kp.Z),
    ("T²=S", kp.T_ @ kp.T_, kp.S_),
    ("X=iRx(π)", kp.X, 1j * kp.Rx(np.pi)),
    ("CNOT²=I", kp.CNOT @ kp.CNOT, np.eye(4)),
    ("SWAP²=I", kp.SWAP @ kp.SWAP, np.eye(4)),
    ("Toffoli²=I", kp.TOFFOLI @ kp.TOFFOLI, np.eye(8)),
    ("Fredkin²=I", kp.FREDKIN @ kp.FREDKIN, np.eye(8)),
    ("iSWAP²=diag", kp.iSWAP @ kp.iSWAP,
     np.diag([1, -1, -1, 1]).astype(complex)),
])
def test_kapi_ozdeslikleri(ad, A, B):
    assert kp.esdeger_mi(A, B), ad


def test_swap_uc_cnot_ile():
    ters = kp.yerlestir(kp.CNOT, [1, 0], 2)
    assert kp.esdeger_mi(kp.SWAP, kp.CNOT @ ters @ kp.CNOT)


def test_donme_kapilari_grup_teskil_ediyor():
    for R in (kp.Rx, kp.Ry, kp.Rz):
        a, b = 0.6, 1.3
        assert kp.esdeger_mi(R(a) @ R(b), R(a + b))
        assert kp.esdeger_mi(R(a) @ R(-a), kp.I2)
        # 2π dönme −I verir (spinor işareti):
        assert kp.esdeger_mi(R(2 * np.pi), -kp.I2)
        assert kp.esdeger_mi(R(4 * np.pi), kp.I2)


def test_U3_her_SU2_kapisini_veriyor():
    """Rastgele SU(2) kapıları U₃ ile (küresel faz kadarıyla) yazılabilir."""
    rng = np.random.default_rng(0)
    for _ in range(20):
        teta = rng.uniform(0, np.pi)
        fi, lam = rng.uniform(0, 2 * np.pi, 2)
        U = kp.U3(teta, fi, lam)
        assert kp.uniter_mi(U)
        assert abs(abs(np.linalg.det(U)) - 1.0) < 1e-12


# --- K7 tashihi: U1 ile Rz -------------------------------------------

@pytest.mark.parametrize("lam", [0.3, 0.7, np.pi / 2, 2.4, np.pi])
def test_U1_Rz_kuresel_faz(lam):
    u, r = kp.U1(lam), kp.Rz(lam)
    assert not kp.esdeger_mi(u, r)                       # eşit DEĞİL
    assert kp.esdeger_mi(u, r, kuresel_faz_serbest=True)  # faz kadar
    assert kp.esdeger_mi(u, kp.faz(lam / 2) * r)          # tam ilişki


@pytest.mark.parametrize("lam", [0.7, 2.4])
def test_kontrol_altinda_fark_olculebilir(lam):
    c1, c2 = kp.kontrollu(kp.U1(lam)), kp.kontrollu(kp.Rz(lam))
    assert not kp.esdeger_mi(c1, c2)
    # Küresel faz serbestliği bile kurtarmıyor:
    assert not kp.esdeger_mi(c1, c2, kuresel_faz_serbest=True)
    assert np.max(np.abs(c1 - c2)) > 0.1


# --- yerleştirme ------------------------------------------------------

def test_kubit_sirasi_q0_en_anlamli():
    v01 = np.eye(4)[1].astype(complex)      # |01⟩
    v10 = np.eye(4)[2].astype(complex)      # |10⟩
    assert np.allclose(kp.CNOT @ v01, v01)          # kontrol 0 → değişmez
    assert np.allclose(kp.CNOT @ v10, np.eye(4)[3])  # kontrol 1 → hedef döner


def test_yerlestirme_uniter_ve_dogru():
    n = 4
    for kubitler, U in (([0], kp.H), ([2], kp.X), ([0, 1], kp.CNOT),
                        ([1, 3], kp.CNOT), ([3, 1], kp.CNOT),
                        ([0, 2, 3], kp.TOFFOLI)):
        G = kp.yerlestir(U, kubitler, n)
        assert G.shape == (2 ** n, 2 ** n)
        assert kp.uniter_mi(G), kubitler
    # Takas edilmiş CNOT = SWAP·CNOT·SWAP
    assert kp.esdeger_mi(kp.yerlestir(kp.CNOT, [1, 0], 2),
                         kp.SWAP @ kp.CNOT @ kp.SWAP)


def test_yerlestirme_gecersiz_girdiyi_reddediyor():
    with pytest.raises(ValueError):
        kp.yerlestir(kp.CNOT, [0], 3)          # boyut uyuşmuyor
    with pytest.raises(ValueError):
        kp.yerlestir(kp.CNOT, [0, 0], 3)       # tekrarlı kübit
    with pytest.raises(ValueError):
        kp.yerlestir(kp.H, [5], 3)             # kayıt dışı


def test_esdeger_mi_olcutu_ayirt_ediyor():
    assert kp.esdeger_mi(kp.X, kp.X)
    assert not kp.esdeger_mi(kp.X, kp.Y)
    assert kp.esdeger_mi(kp.X, 1j * kp.X, kuresel_faz_serbest=True)
    assert not kp.esdeger_mi(kp.X, 1j * kp.X)
    # Ölçek (birim olmayan çarpan) faz sayılmamalı:
    assert not kp.esdeger_mi(kp.X, 2.0 * kp.X, kuresel_faz_serbest=True)


# ══════════════════════════════════════════════════════════════════════
#  2. Devre ve durum
# ══════════════════════════════════════════════════════════════════════

def test_hizlandirma_neticeyi_degistirmiyor():
    """Eksen görünümü ile tam dizey BİREBİR aynı durumu vermeli."""
    rng = np.random.default_rng(1)
    for n in (3, 5, 8):
        v = rng.normal(size=2 ** n) + 1j * rng.normal(size=2 ** n)
        v /= np.linalg.norm(v)
        for U, q in ((kp.H, [0]), (kp.X, [n - 1]), (kp.CNOT, [0, n - 1]),
                     (kp.CNOT, [n - 1, 0]),
                     (kp.TOFFOLI, [0, 1, n - 1])):
            d1 = dv.Durum(n, v.copy()).uygula(U, q)
            d2 = dv.Durum(n, v.copy()).uygula_tam_dizey(U, q)
            assert np.max(np.abs(d1.v - d2.v)) < 1e-12, (n, q)


def test_durum_normu_korunuyor():
    rng = np.random.default_rng(2)
    d = dv.Durum(5)
    for _ in range(30):
        q = list(rng.choice(5, 2, replace=False))
        d.uygula(kp.CNOT, q)
        d.uygula(kp.H, [int(rng.integers(5))])
    assert abs(d.norm - 1.0) < 1e-12


def test_durum_gecersiz_girdiyi_reddediyor():
    with pytest.raises(ValueError):
        dv.Durum(3, np.zeros(4))
    d = dv.Durum(3)
    with pytest.raises(ValueError):
        d.uygula(kp.CNOT, [0])
    with pytest.raises(ValueError):
        d.uygula(kp.H, [7])
    with pytest.raises(ValueError):
        dv.Durum(2, np.zeros(4)).normalize()


def test_devre_uniter_olmayan_kapiyi_reddediyor():
    d = dv.Devre(2)
    with pytest.raises(ValueError):
        d.ekle(np.array([[1, 1], [0, 1]], dtype=complex), [0], "kesme")


def test_olcum_dagilimi_toplami_bir():
    rng = np.random.default_rng(3)
    v = rng.normal(size=16) + 1j * rng.normal(size=16)
    d = dv.Durum(4, v).normalize()
    for kubitler in ([0], [1, 2], [0, 1, 2, 3]):
        p = dv.olcum_dagilimi(d, kubitler)
        assert p.size == 2 ** len(kubitler)
        assert abs(p.sum() - 1.0) < 1e-12
        assert np.all(p >= -1e-15)


# --- QFT --------------------------------------------------------------

@pytest.mark.parametrize("n", [1, 2, 3, 4, 5])
def test_qft_devresi_dizeyle_ayni(n):
    D = dv.qft_devresi(n).dizey()
    assert np.max(np.abs(D - dv.qft_dizeyi(n))) < 1e-12, n
    assert kp.uniter_mi(D)


@pytest.mark.parametrize("n", [2, 3, 4])
def test_qft_swapsiz_yanlis_ama_uniter(n):
    """Bit sırasını çevirmeyi unutmak SESSİZ bir hatadır."""
    D = dv.qft_devresi(n, ters_cevir=False).dizey()
    assert kp.uniter_mi(D)                    # üniter kalıyor
    assert np.max(np.abs(D - dv.qft_dizeyi(n))) > 0.1   # ama yanlış


@pytest.mark.parametrize("n", [1, 2, 3, 4])
def test_qft_ters_dizeyi(n):
    Q = dv.qft_dizeyi(n)
    assert np.max(np.abs(dv.iqft_dizeyi(n) @ Q - np.eye(2 ** n))) < 1e-12


def test_qft_kosegen_degil():
    """K8 tashihi: köşegen bir operatör süperpozisyon üretemez."""
    for n in (2, 3, 4):
        Q = dv.qft_dizeyi(n)
        assert np.max(np.abs(Q - np.diag(np.diag(Q)))) > 0.1
        e0 = np.eye(2 ** n)[0].astype(complex)
        assert np.count_nonzero(np.abs(Q @ e0) > 1e-12) == 2 ** n


def test_walsh_hadamard():
    for n in (1, 2, 3):
        W = dv.walsh_hadamard(n)
        assert kp.uniter_mi(W)
        # (−1)^{x·y} tanımıyla karşılaştır:
        N = 2 ** n
        M = np.zeros((N, N))
        for x in range(N):
            for y in range(N):
                M[y, x] = (-1) ** bin(x & y).count("1")
        assert np.max(np.abs(W - M / np.sqrt(N))) < 1e-12


# --- QPE --------------------------------------------------------------

@pytest.mark.parametrize("pay,m", [(1, 2), (3, 3), (5, 3), (11, 4), (7, 5)])
def test_qpe_tam_temsil_edilen_fazda_kesin(pay, m):
    """``φ = pay/2^m`` ise netice TEK ve olasılığı 1 olmalı."""
    fi = pay / 2 ** m
    U = np.diag([np.exp(2j * np.pi * fi), 1.0]).astype(complex)
    r = dv.faz_kestirimi(U, np.array([1.0, 0.0]), m)
    assert r["φ_tahmini"] == pytest.approx(fi, abs=1e-12)
    assert r["en_olası_olasılık"] == pytest.approx(1.0, abs=1e-9)


def test_qpe_temsil_edilemeyen_fazda_yakinsiyor():
    fi = 1 / 3
    U = np.diag([np.exp(2j * np.pi * fi), 1.0]).astype(complex)
    onceki = 1.0
    for m in (4, 6, 8, 10):
        r = dv.faz_kestirimi(U, np.array([1.0, 0.0]), m)
        hata = abs(r["φ_tahmini"] - fi)
        assert hata < onceki, m
        assert r["en_olası_olasılık"] > 0.4, m   # baskın kalıyor
        onceki = hata
    assert onceki < 1e-3


def test_qpe_gecersiz_girdiyi_reddediyor():
    with pytest.raises(ValueError):
        dv.faz_kestirimi(np.array([[1, 1], [0, 1]], dtype=complex),
                         np.array([1.0, 0.0]), 3)


# --- Trotter ----------------------------------------------------------

def test_trotter_mertebeleri():
    A = np.array([[1.0, 0.4], [0.4, -0.6]])
    B = np.array([[0.2, -0.9], [-0.9, 0.5]])
    t = 1.0
    tam = dv._uexp(A + B, t)
    h1 = [float(np.max(np.abs(dv.trotter(A, B, t, n) - tam)))
          for n in (8, 16, 32, 64)]
    h2 = [float(np.max(np.abs(dv.suzuki2(A, B, t, n) - tam)))
          for n in (8, 16, 32, 64)]
    # 1. mertebe: n iki katına çıkınca hata ~2× düşer
    for a, b in zip(h1, h1[1:]):
        assert 1.8 < a / b < 2.2, h1
    # 2. mertebe: ~4×
    for a, b in zip(h2, h2[1:]):
        assert 3.6 < a / b < 4.4, h2
    # ve 2. mertebe her n'de daha iyi:
    assert all(x < y for x, y in zip(h2, h1))


def test_trotter_degisen_operatorlerde_tam():
    """``[A,B] = 0`` ise Trotter hatası SIFIR olmalı."""
    A = np.diag([1.0, 2.0, 3.0])
    B = np.diag([0.5, -1.0, 2.0])
    assert np.allclose(kp.komutator(A, B), 0)
    tam = dv._uexp(A + B, 1.3)
    assert np.max(np.abs(dv.trotter(A, B, 1.3, 1) - tam)) < 1e-12


def test_trotter_gecersiz_n():
    A = np.eye(2); B = np.eye(2)
    with pytest.raises(ValueError):
        dv.trotter(A, B, 1.0, 0)
    with pytest.raises(ValueError):
        dv.suzuki2(A, B, 1.0, 0)


def test_hadamard_testi_dogru_beklenen_degeri_veriyor():
    rng = np.random.default_rng(5)
    for _ in range(10):
        psi = rng.normal(size=2) + 1j * rng.normal(size=2)
        psi /= np.linalg.norm(psi)
        U = np.linalg.qr(rng.normal(size=(2, 2))
                         + 1j * rng.normal(size=(2, 2)))[0]
        re = dv.hadamard_testi(U, psi)
        im = dv.hadamard_testi(U, psi, sanal=True)
        tam = complex(np.vdot(psi, U @ psi))
        assert abs(complex(re, im) - tam) < 1e-10


# ══════════════════════════════════════════════════════════════════════
#  3. TDA
# ══════════════════════════════════════════════════════════════════════

def _mesafe(P):
    d = P[:, None, :] - P[None, :, :]
    return np.sqrt(np.sum(d * d, axis=2))


def _cember(n, r=1.0):
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    return np.stack([r * np.cos(t), r * np.sin(t)], axis=1)


def test_sinir_operatoru_kare_sifir():
    """``∂_k ∘ ∂_{k+1} = 0`` — homolojinin temel şartı."""
    rng = np.random.default_rng(0)
    for tohum in range(5):
        P = np.random.default_rng(tohum).normal(size=(9, 3))
        K = tda.vietoris_rips(_mesafe(P), 2.4, azami_boyut=3)
        for k in (1, 2, 3):
            B1 = tda.sinir_operatoru(K, k)
            B2 = tda.sinir_operatoru(K, k + 1)
            if B1.size and B2.size:
                assert np.max(np.abs(B1 @ B2)) < 1e-12, (tohum, k)


def test_laplasyen_simetrik_ve_psd():
    P = np.random.default_rng(1).normal(size=(8, 2))
    K = tda.vietoris_rips(_mesafe(P), 1.6, azami_boyut=2)
    for k in (0, 1):
        D = tda.kombinatoryal_laplasyen(K, k)
        if D.size == 0:
            continue
        assert np.max(np.abs(D - D.T)) < 1e-12
        assert np.min(np.linalg.eigvalsh(D)) > -1e-9


@pytest.mark.parametrize("ad,P,eps,b0,b1", [
    ("3 ayrık", np.array([[0., 0.], [10., 0.], [0., 10.]]), 0.5, 3, 0),
    ("çember", _cember(16), 0.5, 1, 1),
    ("çember-24", _cember(24), 0.35, 1, 1),
    ("dolu üçgen", np.array([[0., 0.], [1., 0.], [0.5, 0.87]]), 1.5, 1, 0),
    ("tek nokta", np.array([[0., 0.]]), 1.0, 1, 0),
])
def test_bilinen_sekillerde_betti(ad, P, eps, b0, b1):
    K = tda.vietoris_rips(_mesafe(P), eps, azami_boyut=2)
    assert tda.betti(K, 0) == b0, (ad, "β₀")
    assert tda.betti(K, 1) == b1, (ad, "β₁")


def test_iki_ayri_cember():
    P = np.vstack([_cember(12), _cember(12) + np.array([10.0, 0.0])])
    K = tda.vietoris_rips(_mesafe(P), 0.6, azami_boyut=2)
    assert tda.betti(K, 0) == 2
    assert tda.betti(K, 1) == 2


def test_euler_karakteristigi_betti_ile_uyusuyor():
    """``χ = Σ(−1)^k β_k`` — simpleks sayımı ile homoloji uyuşmalı."""
    for P, eps in ((_cember(16), 0.5),
                   (np.array([[0., 0.], [1., 0.], [0.5, 0.87]]), 1.5),
                   (np.random.default_rng(2).normal(size=(8, 2)), 1.5)):
        K = tda.vietoris_rips(_mesafe(P), eps, azami_boyut=2)
        chi_sayim = tda.euler_karakteristigi(K)
        chi_betti = sum((-1) ** k * tda.betti(K, k) for k in (0, 1, 2))
        assert chi_sayim == chi_betti, (chi_sayim, chi_betti)


def test_tikhonov_cekirdegi_yok_ediyor():
    """K25: ``Δ+εI``in çekirdeği boştur; β eşikli sayımla okunur."""
    K = tda.vietoris_rips(_mesafe(_cember(16)), 0.5, azami_boyut=2)
    D = tda.kombinatoryal_laplasyen(K, 0)
    oz = np.linalg.eigvalsh(D)
    assert int(np.sum(np.abs(oz) < 1e-9)) == 1        # β₀ = 1
    for eps in (1e-9, 1e-6, 1e-3):
        oz_e = np.linalg.eigvalsh(D + eps * np.eye(D.shape[0]))
        assert int(np.sum(np.abs(oz_e) < 1e-12)) == 0  # çekirdek YOK
        assert int(np.sum(oz_e <= eps + 1e-9)) == 1    # eşikli sayım: 1


def test_vietoris_rips_gecersiz_girdi():
    with pytest.raises(ValueError):
        tda.vietoris_rips(np.zeros((3, 4)), 1.0)


def test_barkod_ve_kalicilik_suzgeci():
    P = _cember(24) + 0.03 * np.random.default_rng(3).normal(size=(24, 2))
    esikler = np.linspace(0.05, 2.2, 40)
    c0 = tda.barkod(_mesafe(P), esikler, k=0)
    c1 = tda.barkod(_mesafe(P), esikler, k=1)
    assert len(c0) == 24                        # her nokta bir bileşen
    assert len(c1) >= 1                         # çemberin deliği
    # Uzun süzgeç kısa çubukları eliyor:
    assert len(tda.kalicilik_suzgeci(c0, 0.5)) < len(c0)
    # Hakiki delik süzgeçten geçiyor:
    assert len(tda.kalicilik_suzgeci(c1, 0.5)) >= 1
    assert max(d - b for b, d in c1) > 1.0


def test_bottleneck_bilinen_haller():
    A = [(0.0, 1.0), (0.2, 0.9)]
    assert tda.bottleneck(A, A) == pytest.approx(0.0)
    assert tda.bottleneck([], []) == pytest.approx(0.0)
    # Boş barkodla: en uzun çubuğun yarısı
    assert tda.bottleneck(A, []) == pytest.approx(0.5)
    # Bir çubuk uzatıldı:
    assert tda.bottleneck(A, [(0.0, 1.3), (0.2, 0.9)]) == pytest.approx(0.3)
    # Köşegene yakın bir çubuk eklendi:
    assert tda.bottleneck(A, A + [(0.5, 0.52)]) == pytest.approx(0.01)


def test_bottleneck_metrik_aksiyomlari():
    """Simetri ve üçgen eşitsizliği — ölçülerek."""
    rng = np.random.default_rng(7)

    def rastgele_barkod(n):
        b = rng.uniform(0, 1, n)
        return [(float(x), float(x + rng.uniform(0.05, 0.8))) for x in b]

    for _ in range(30):
        A = rastgele_barkod(int(rng.integers(1, 5)))
        B = rastgele_barkod(int(rng.integers(1, 5)))
        C = rastgele_barkod(int(rng.integers(1, 5)))
        ab = tda.bottleneck(A, B)
        assert ab == pytest.approx(tda.bottleneck(B, A))     # simetri
        ac, cb = tda.bottleneck(A, C), tda.bottleneck(C, B)
        assert ab <= ac + cb + 1e-9, (ab, ac, cb)            # üçgen


def test_kahan_hatasi_N_ile_buyumuyor():
    """K32: baş terim ``N``den bağımsız."""
    from fractions import Fraction
    eps = np.finfo(float).eps
    hatalar = []
    for N in (1_000, 10_000, 100_000):
        rng = np.random.default_rng(N)
        xs = rng.normal(0, 1, N) * 10.0 ** rng.integers(-8, 8, N)
        tam = float(sum(Fraction(float(x)) for x in xs))
        olcek = float(np.sum(np.abs(xs)))
        h = abs(tda.kahan_toplam(xs) - tam) / olcek
        hatalar.append(h)
        assert h <= 4 * eps, (N, h / eps)
    # N 100 kat artarken hata artmıyor:
    assert hatalar[-1] <= max(hatalar[0], 4 * eps)


def test_kahan_bilinen_zor_halde():
    """``[1, ε, −1, ε, …]`` — naif toplama ε'ları kaybeder."""
    eps = 1e-16
    xs = []
    for _ in range(1000):
        xs += [1.0, eps, -1.0, eps]
    naif = 0.0
    for x in xs:
        naif += x
    beklenen = 2000 * eps
    assert tda.kahan_toplam(xs) == pytest.approx(beklenen, rel=1e-9)
    assert abs(naif - beklenen) > beklenen * 0.5   # naif çuvallıyor


@pytest.mark.parametrize("modul", [kp, dv, tda])
def test_rapor_uretiliyor(modul):
    m = modul.rapor()
    assert isinstance(m, str) and len(m) > 200
