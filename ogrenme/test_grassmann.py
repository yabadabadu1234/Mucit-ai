"""``ogrenme.grassmann`` sınamaları — K25 ve K26 tashihlerinin tartılması."""

from __future__ import annotations

import math

import numpy as np
import pytest

from ogrenme import grassmann as gr


def _r(d, k, tohum):
    return gr._rastgele(d, k, tohum)


def _dondur(Y, tohum):
    Q, _ = np.linalg.qr(np.random.default_rng(tohum).normal(
        size=(Y.shape[1], Y.shape[1])))
    return Y @ Q


# ── izdüşüm ──────────────────────────────────────────────────────────

@pytest.mark.parametrize("d,k", [(6, 2), (8, 3), (12, 5)])
def test_izdusum_simetrik_idempotent_izi_k(d, k):
    P = gr.izdusum(_r(d, k, 0))
    assert np.abs(P - P.T).max() < 1e-13
    assert np.abs(P @ P - P).max() < 1e-13
    assert float(np.trace(P)) == pytest.approx(k)


@pytest.mark.parametrize("tohum", range(5))
def test_izdusum_taban_secimine_bagimsiz(tohum):
    Y = _r(9, 4, tohum)
    assert gr.alt_uzay_hatasi(Y, _dondur(Y, tohum + 100)) < 1e-13
    # ama taban normu sıfır DEĞİL — yanlış ölçütün şahidi
    assert np.linalg.norm(Y - _dondur(Y, tohum + 100)) > 0.1


# ── asal açılar ve mesafe ────────────────────────────────────────────

def test_ayni_alt_uzay_mesafesi_sifir():
    Y = _r(10, 3, 1)
    assert gr.grassmann_mesafesi(Y, _dondur(Y, 2)) < 1e-7
    assert float(gr.asal_acilar(Y, Y).max()) < 1e-7


def test_dik_alt_uzaylar_pi_bolu_iki():
    Y1 = np.eye(6)[:, :2]
    Y2 = np.eye(6)[:, 2:4]
    th = gr.asal_acilar(Y1, Y2)
    assert np.allclose(th, math.pi / 2)
    assert gr.grassmann_mesafesi(Y1, Y2) == pytest.approx(
        math.sqrt(2) * math.pi / 2)


def test_mesafe_bakisimli_ve_ucgen_esitsizligi():
    A, B, C = _r(9, 3, 11), _r(9, 3, 12), _r(9, 3, 13)
    dab = gr.grassmann_mesafesi(A, B)
    assert dab == pytest.approx(gr.grassmann_mesafesi(B, A), abs=1e-12)
    assert dab <= gr.grassmann_mesafesi(A, C) + gr.grassmann_mesafesi(C, B) + 1e-12


@pytest.mark.parametrize("tohum", range(4))
def test_mesafe_donmeye_degismez(tohum):
    A, B = _r(10, 4, 40 + tohum), _r(10, 4, 50 + tohum)
    d0 = gr.grassmann_mesafesi(A, B)
    d1 = gr.grassmann_mesafesi(_dondur(A, 7), _dondur(B, 8))
    assert d1 == pytest.approx(d0, abs=1e-11)


# ── K26: Exp / Log ───────────────────────────────────────────────────

@pytest.mark.parametrize("olcek", [0.05, 0.2, 0.5, 0.9])
def test_arctan_log_gidis_donusu_kapatiyor(olcek):
    Y = _r(8, 3, 0)
    H = np.random.default_rng(7).normal(size=(8, 3))
    H = H - Y @ (Y.T @ H)
    H = H / np.linalg.norm(H, 2) * (olcek * math.pi / 2)
    Yt = gr.exp_haritasi(Y, H)
    assert gr.gidis_donus_hatasi(Y, Yt, gr.log_haritasi) < 1e-13


@pytest.mark.parametrize("olcek,alt", [(0.05, 1e-5), (0.2, 1e-3), (0.5, 0.5)])
def test_arcsin_log_gidis_donusu_KAPATMIYOR(olcek, alt):
    """K26'nın şahidi: kaynaktaki arcsin biçimi hatalıdır."""
    Y = _r(8, 3, 0)
    H = np.random.default_rng(7).normal(size=(8, 3))
    H = H - Y @ (Y.T @ H)
    H = H / np.linalg.norm(H, 2) * (olcek * math.pi / 2)
    Yt = gr.exp_haritasi(Y, H)
    assert gr.gidis_donus_hatasi(Y, Yt, gr.log_haritasi_arcsin) > alt


def test_iz_olcutu_yanlis_log_u_yakalamiyor():
    """Kaynaktaki ``Tr(Exp(Log)) = Tr(G₂)`` ölçütü zayıftır."""
    Y1, Y2 = _r(8, 3, 0), _r(8, 3, 1)
    kotu = gr.exp_haritasi(Y1, gr.log_haritasi_arcsin(Y1, Y2))
    assert float(np.trace(gr.izdusum(kotu))) == pytest.approx(3.0)
    assert float(np.trace(gr.izdusum(Y2))) == pytest.approx(3.0)
    assert gr.alt_uzay_hatasi(kotu, Y2) > 0.5      # ama alt uzay YANLIŞ


@pytest.mark.parametrize("tohum", range(4))
def test_log_normu_mesafeye_esit(tohum):
    A, B = _r(10, 4, 10 + tohum), _r(10, 4, 20 + tohum)
    assert float(np.linalg.norm(gr.log_haritasi(A, B))) == pytest.approx(
        gr.grassmann_mesafesi(A, B), abs=1e-10)


@pytest.mark.parametrize("tohum", range(4))
def test_geodezik_dogrusal_ve_ucgeni_kapatiyor(tohum):
    A, B = _r(10, 4, 10 + tohum), _r(10, 4, 20 + tohum)
    g = gr.grassmann_geodezigi(A, B)
    assert g["doğrusallık_hatası"] < 1e-12
    assert g["üçgen_kapanma_hatası"] < 1e-12


def test_exp_dikey_bileseni_gormezden_geliyor():
    """Dikey bileşen tabanı döndürür, alt uzayı değiştirmez."""
    Y = _r(9, 3, 3)
    H = np.random.default_rng(4).normal(size=(9, 3))
    Hy = H - Y @ (Y.T @ H)
    D = Y @ np.random.default_rng(5).normal(size=(3, 3))   # saf dikey
    assert gr.alt_uzay_hatasi(gr.exp_haritasi(Y, Hy),
                              gr.exp_haritasi(Y, Hy + D)) < 1e-12


# ── Karcher ortalaması ───────────────────────────────────────────────

def test_karcher_oklitten_iyi_ve_taban_bagimsiz():
    kume = [_r(9, 3, 30 + i) for i in range(6)]
    m = gr.grassmann_ortalamasi(kume)
    ok = gr.dik_taban(sum(kume) / len(kume))
    kare_ok = sum(gr.grassmann_mesafesi(ok, Y) ** 2 for Y in kume)
    assert m["artık"] < 1e-12
    assert m["kare_mesafe_toplamı"] < kare_ok

    kume2 = [_dondur(Y, 200 + i) for i, Y in enumerate(kume)]
    m2 = gr.grassmann_ortalamasi(kume2)
    assert gr.alt_uzay_hatasi(m["ortalama"], m2["ortalama"]) < 1e-12
    # Öklit ortalaması taban seçimine BAĞLI — şahit
    ok2 = gr.dik_taban(sum(kume2) / len(kume2))
    assert gr.alt_uzay_hatasi(ok, ok2) > 0.1


def test_karcher_tek_noktada_kendisi():
    Y = _r(8, 2, 9)
    m = gr.grassmann_ortalamasi([Y, _dondur(Y, 3)])
    assert gr.alt_uzay_hatasi(m["ortalama"], Y) < 1e-10


def test_karcher_yakinsamasi_dogrusal():
    kume = [_r(9, 3, 30 + i) for i in range(6)]
    s = gr.grassmann_ortalamasi(kume)["artık_seyri"]
    oran = [s[i + 1] / s[i] for i in range(3, 20)]
    assert 0.6 < min(oran) and max(oran) < 0.95     # doğrusal, kuadratik değil


# ── K25: Tikhonov ────────────────────────────────────────────────────

def _uc_bilesenli():
    A = np.zeros((9, 9))
    for blok in ([0, 1, 2], [3, 4], [5, 6, 7, 8]):
        for i in blok:
            for j in blok:
                if i != j:
                    A[i, j] = 1.0
    return A


def test_betti0_bilesen_sayisini_veriyor():
    assert gr.betti0_tayftan(_uc_bilesenli())["β₀"] == 3
    tek = np.ones((5, 5)) - np.eye(5)
    assert gr.betti0_tayftan(tek)["β₀"] == 1


@pytest.mark.parametrize("eps", [1e-3, 1e-6])
def test_tikhonov_cekirdegi_yok_ediyor(eps):
    t = gr.tikhonov_cekirdegi_yok_eder(_uc_bilesenli(), eps)
    assert t["β₀_düzenlemesiz"] == 3
    assert t["çekirdek_düzenlemeli"] == 0        # K25'in özü
    assert t["ε'a_eşit_özdeğer"] == 3
    assert t["kayma_hatası"] < 1e-13


def test_normalize_laplasyen_tayfi_sifir_iki_arasinda():
    e = np.linalg.eigvalsh(gr.normalize_laplasyen(_uc_bilesenli()))
    assert e.min() > -1e-12
    assert e.max() < 2 + 1e-12
