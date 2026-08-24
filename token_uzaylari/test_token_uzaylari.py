"""token_uzaylari test takımı.

Geometride "çalışıyor gibi görünmek" ucuzdur: bir işaret hatası bütün
tabloyu tutarlı ama yanlış kılar.  Bu yüzden burada ölçüt hep
**bağımsız olarak bilinen cevaba** göre:

* düz uzayda bütün eğrilik tam sıfır
* ``r`` yarıçaplı kürede ``K = 1/r²``, ``R = 2/r²``
* hiperbolik düzlemde ``K = −1``
* Riemann'ın dört simetrisi
* Laplace–Beltrami'nin iki ayrı hesabı
* zincir kaidesi (funktoryellik)
* B-spline'da birliğin bölünmesi, yerellik, kapalı form türev

Çalıştırma: ``python3 -m pytest token_uzaylari/test_token_uzaylari.py -q``
"""

from __future__ import annotations

import numpy as np
import pytest

from token_uzaylari import kan_spline as ks
from token_uzaylari import manifold as mf
from token_uzaylari import morfizm as mo


# ══════════════════════════════════════════════════════════════════════
#  1. Manifold — bilinen eğrilikler
# ══════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("n", [1, 2, 3, 4])
def test_duz_uzayda_her_sey_sifir(n):
    d = mf.duz_metrik(n)
    x = np.linspace(0.2, 1.4, n)
    assert np.max(np.abs(d.christoffel(x))) < 1e-12
    assert np.max(np.abs(d.riemann(x))) < 1e-12
    assert abs(d.skaler_egrilik(x)) < 1e-12


@pytest.mark.parametrize("r", [0.5, 1.0, 2.0, 3.0])
def test_kurede_K_bir_bolu_r_kare(r):
    k = mf.kure_metrigi(r)
    for p in ([1.0, 0.4], [0.8, 2.0], [2.0, 1.1]):
        K = k.kesit_egriligi(np.array(p), [1.0, 0.0], [0.0, 1.0])
        assert K == pytest.approx(1.0 / r ** 2, rel=1e-5), p
        assert k.skaler_egrilik(np.array(p)) == pytest.approx(
            2.0 / r ** 2, rel=1e-5)


def test_hiperbolik_duzlemde_K_eksi_bir():
    h = mf.hiperbolik_metrik()
    for p in ([0.0, 1.0], [2.0, 0.5], [-1.0, 3.0], [0.5, 1.3]):
        K = h.kesit_egriligi(np.array(p), [1.0, 0.0], [0.0, 1.0])
        assert K == pytest.approx(-1.0, rel=1e-5), p
        assert h.skaler_egrilik(np.array(p)) == pytest.approx(-2.0, rel=1e-5)


def test_kesit_egriligi_isaret_konvansiyonu_sabit():
    """Kürede POZİTİF, hiperbolikte NEGATİF — ikisi aynı formülle."""
    kK = mf.kure_metrigi(1.0).kesit_egriligi(np.array([1.0, 0.4]),
                                             [1.0, 0.0], [0.0, 1.0])
    hK = mf.hiperbolik_metrik().kesit_egriligi(np.array([0.5, 1.3]),
                                               [1.0, 0.0], [0.0, 1.0])
    assert kK > 0 and hK < 0


def test_paralel_vektorlerde_kesit_tanimsiz():
    k = mf.kure_metrigi(1.0)
    K = k.kesit_egriligi(np.array([1.0, 0.4]), [1.0, 0.0], [2.0, 0.0])
    assert np.isnan(K)


@pytest.mark.parametrize("ad,m,p", [
    ("küre", mf.kure_metrigi(1.0), [1.0, 0.4]),
    ("küre-r2", mf.kure_metrigi(2.0), [0.8, 1.7]),
    ("hiperbolik", mf.hiperbolik_metrik(), [0.5, 1.3]),
    ("düz", mf.duz_metrik(3), [0.2, -0.4, 1.0]),
])
def test_riemann_simetrileri(ad, m, p):
    r = mf.riemann_simetrileri(m, p, tol=1e-5)
    assert r["hepsi_sağlanıyor"] is True, (ad, r)


def test_christoffel_alt_indislerde_simetrik():
    """Levi-Civita burulmasızdır: ``Γ^k_{ij} = Γ^k_{ji}``."""
    for m, p in ((mf.kure_metrigi(1.0), [1.0, 0.4]),
                 (mf.hiperbolik_metrik(), [0.5, 1.3])):
        G = m.christoffel(np.array(p))
        assert np.max(np.abs(G - np.transpose(G, (0, 2, 1)))) < 1e-9


def test_ricci_simetrik():
    for m, p in ((mf.kure_metrigi(1.0), [1.0, 0.4]),
                 (mf.hiperbolik_metrik(), [0.5, 1.3])):
        R = m.ricci(np.array(p))
        olcek = max(float(np.max(np.abs(R))), 1e-30)
        assert np.max(np.abs(R - R.T)) / olcek < 1e-6


def test_laplace_beltrami_iki_yol_uyusuyor():
    f = lambda z: float(np.sin(z[0]) * np.exp(0.3 * z[1]))
    for m, p in ((mf.duz_metrik(2), [0.4, 0.9]),
                 (mf.kure_metrigi(1.0), [1.0, 0.4]),
                 (mf.hiperbolik_metrik(), [0.5, 1.3])):
        a = m.laplace_beltrami(f, np.array(p))
        b = m.laplace_beltrami_christoffel(f, np.array(p))
        assert abs(a - b) < 1e-4, (m.ad, a, b)


def test_duz_uzayda_laplace_beltrami_alelade_laplasyene_iniyor():
    f = lambda z: float(np.sin(z[0]) * np.exp(0.3 * z[1]))
    p = np.array([0.4, 0.9])
    tam = (-np.sin(p[0]) + 0.09 * np.sin(p[0])) * np.exp(0.3 * p[1])
    assert mf.duz_metrik(2).laplace_beltrami(f, p) == pytest.approx(
        tam, abs=1e-5)


def test_sabit_fonksiyonun_laplasyeni_sifir():
    for m, p in ((mf.kure_metrigi(1.0), [1.0, 0.4]),
                 (mf.hiperbolik_metrik(), [0.5, 1.3])):
        assert abs(m.laplace_beltrami(lambda z: 3.7, np.array(p))) < 1e-6


def test_bozuk_metrik_reddediliyor():
    asimetrik = mf.Metrik(2, lambda x: np.array([[1.0, 0.3], [0.0, 1.0]]))
    with pytest.raises(ValueError):
        asimetrik.denetle([0.0, 0.0])
    negatif = mf.Metrik(2, lambda x: np.diag([1.0, -1.0]))
    with pytest.raises(ValueError):
        negatif.denetle([0.0, 0.0])
    # Küre kutupta dejenere:
    with pytest.raises(ValueError):
        mf.kure_metrigi(1.0).denetle([0.0, 0.0])


def test_konformal_metrik_duzle_ayni_esik():
    """``φ ≡ 0`` iken konformal metrik düz metriğe inmeli."""
    k = mf.konformal_metrik(2, lambda x: 0.0)
    p = np.array([0.3, -0.5])
    assert np.max(np.abs(k.G(p) - np.eye(2))) < 1e-14
    assert abs(k.skaler_egrilik(p)) < 1e-8


# ══════════════════════════════════════════════════════════════════════
#  2. Morfizm — funktoryellik
# ══════════════════════════════════════════════════════════════════════

@pytest.fixture
def ikili():
    phi = mo.Morfizm(2, 3, lambda x: np.array([x[0] ** 2 + x[1],
                                               np.sin(x[0]) * x[1],
                                               np.exp(0.3 * x[0])]), "φ")
    psi = mo.Morfizm(3, 2, lambda y: np.array([y[0] * y[2],
                                               np.tanh(y[1] + y[0])]), "ψ")
    return phi, psi


def test_zincir_kaidesi(ikili):
    phi, psi = ikili
    for x in ([0.7, -0.4], [-0.3, 1.1], [1.2, 0.6]):
        f = mo.funktoryellik_olc(psi, phi, x)
        assert f["zincir_kaidesi_sapması"] < 1e-8, x


def test_cekme_sirasi_tersine_donuyor(ikili):
    phi, psi = ikili
    f = mo.funktoryellik_olc(psi, phi, [0.7, -0.4])
    assert f["çekme_sapması"] < 1e-8
    assert f["çekme_büyüklüğü"] > 1e-3, "sağlama boş olmasın"
    assert "tip hatası" in str(f["ters_sıra"])


def test_itme_ve_cekme_dogru_uzaylarda(ikili):
    phi, _ = ikili
    x = [0.7, -0.4]
    assert phi.itme(x, [1.0, 0.5]).size == 3       # hedefte
    assert phi.cekme(x, [0.2, -0.7, 1.3]).size == 2  # kaynakta
    with pytest.raises(ValueError):
        phi.cekme(x, [1.0, 0.5])                   # yanlış boy
    with pytest.raises(ValueError):
        phi.itme(x, [1.0, 0.5, 0.2])


def test_bileske_boyut_denetimi(ikili):
    phi, psi = ikili
    with pytest.raises(ValueError):
        mo.bileske(phi, phi)                        # 3 ≠ 2


def test_cekilmis_metrik_JtJ(ikili):
    phi, _ = ikili
    x = [0.7, -0.4]
    G = phi.metrik_cek(mf.duz_metrik(3), x)
    J = phi.dphi(x)
    assert np.max(np.abs(G - J.T @ J)) < 1e-12
    assert np.max(np.abs(G - G.T)) < 1e-12
    assert np.min(np.linalg.eigvalsh(G)) > 0


def test_izometri_ve_konformallik_ayirt_ediliyor():
    duz2 = mf.duz_metrik(2)
    noktalar = [[0.3, 0.5], [-0.8, 1.2], [1.5, -0.3]]
    donme = mo.Morfizm(2, 2, lambda z: np.array([
        np.cos(0.7) * z[0] - np.sin(0.7) * z[1],
        np.sin(0.7) * z[0] + np.cos(0.7) * z[1]]))
    olcek = mo.Morfizm(2, 2, lambda z: 2.5 * z)
    egri = mo.Morfizm(2, 2, lambda z: np.array([z[0] ** 2, z[1]]))

    assert mo.izometri_mi(donme, duz2, duz2, noktalar)["izometri"] is True
    assert mo.konformal_mi(donme, duz2, duz2, noktalar)["konformal"] is True

    assert mo.izometri_mi(olcek, duz2, duz2, noktalar)["izometri"] is False
    k = mo.konformal_mi(olcek, duz2, duz2, noktalar)
    assert k["konformal"] is True
    assert np.allclose(k["λ_değerleri"], 6.25, rtol=1e-6)

    assert mo.izometri_mi(egri, duz2, duz2, noktalar)["izometri"] is False
    assert mo.konformal_mi(egri, duz2, duz2, noktalar)["konformal"] is False


def test_carpim_morfizminin_jakobisi_blok_kosegen():
    a = mo.Morfizm(2, 2, lambda z: np.array([z[0] ** 2, z[0] * z[1]]))
    b = mo.Morfizm(3, 2, lambda z: np.array([z[0] + z[2], np.sin(z[1])]))
    c = mo.carpim_morfizmi(a, b)
    p = np.array([0.4, -0.6, 1.1, 0.2, -0.9])
    Jc = c.dphi(p)
    assert Jc.shape == (4, 5)
    assert np.max(np.abs(Jc[:2, 2:])) < 1e-12
    assert np.max(np.abs(Jc[2:, :2])) < 1e-12
    assert np.max(np.abs(Jc[:2, :2] - a.dphi(p[:2]))) < 1e-12
    assert np.max(np.abs(Jc[2:, 2:] - b.dphi(p[2:]))) < 1e-12


def test_cekilmis_metrik_ile_egrilik_hesaplanabiliyor():
    """Kürenin çekilmiş metriği yine kürenin eğriliğini vermeli."""
    kure = mf.kure_metrigi(1.0)
    ozdes = mo.Morfizm(2, 2, lambda z: z.copy(), "id")
    cekilmis = ozdes.cekilmis_metrik(kure)
    p = np.array([1.0, 0.4])
    assert cekilmis.skaler_egrilik(p) == pytest.approx(2.0, rel=1e-4)


# ══════════════════════════════════════════════════════════════════════
#  3. B-spline KAN
# ══════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("G,k", [(5, 0), (5, 1), (5, 3), (10, 3),
                                 (8, 2), (20, 4)])
def test_birligin_bolunmesi(G, k):
    d = ks.dugum_dizisi(G, k)
    t = np.linspace(-1.0, 1.0, 501)
    assert ks.birligin_bolunmesi_sapmasi(t, d, k) < 1e-12


@pytest.mark.parametrize("G,k", [(5, 1), (5, 3), (10, 3), (8, 2)])
def test_temel_negatif_olmuyor(G, k):
    d = ks.dugum_dizisi(G, k)
    B = ks.bspline_temeli(np.linspace(-1.7, 1.7, 801), d, k)
    assert np.min(B) > -1e-12


def test_temel_sayisi_G_arti_k():
    for G, k in ((5, 3), (10, 2), (7, 4)):
        d = ks.dugum_dizisi(G, k)
        assert ks.bspline_temeli(np.array([0.0]), d, k).shape[1] == G + k
        assert d.size == G + 2 * k + 1


@pytest.mark.parametrize("k", [0, 1, 2, 3, 4])
def test_yerellik_destek_k_arti_bir_aralik(k):
    """Derece ``k`` B-spline'ı tam ``k+1`` aralıkta sıfırdan farklı."""
    G = 10
    d = ks.dugum_dizisi(G, k)
    t = np.linspace(-1.75, 1.75, 4001)
    B = ks.bspline_temeli(t, d, k)
    i = B.shape[1] // 2
    destek = t[B[:, i] > 1e-12]
    h = 2.0 / G
    genislik = destek.max() - destek.min()
    assert genislik / h == pytest.approx(k + 1, abs=0.02)


def test_turev_kapali_form_sayisal_farkla_uyusuyor():
    for G, k in ((8, 3), (12, 2), (6, 4)):
        d = ks.dugum_dizisi(G, k)
        # Örnek noktaları düğümlerden KASTEN kaydırılır.  ``B'_{i,k}``
        # düğümlerde ``k−1`` kere türevlenebilirdir; k=2'de türev orada
        # köşelidir ve merkezî fark köşenin iki yanını alıp O(1) hata
        # verir.  Bu, kapalı formun değil referansın kusurudur — o yüzden
        # karşılaştırma türevin sürekli olduğu noktalarda yapılır.
        # Her düğüm aralığının içinden üç nokta: kesirler 1/4, 1/2, 3/4.
        h_dugum = 2.0 / G
        t = np.array([-1.0 + (i + f) * h_dugum
                      for i in range(G) for f in (0.25, 0.5, 0.75)])
        assert np.min(np.abs(t[:, None] - d[None, :])) > 0.1 * h_dugum
        T = ks.bspline_turev_temeli(t, d, k)
        h = 1e-6
        sayisal = (ks.bspline_temeli(t + h, d, k)
                   - ks.bspline_temeli(t - h, d, k)) / (2 * h)
        assert np.max(np.abs(T - sayisal)) < 1e-7, (G, k)


def test_derece_sifirda_turev_sifir():
    d = ks.dugum_dizisi(5, 0)
    T = ks.bspline_turev_temeli(np.linspace(-0.9, 0.9, 20), d, 0)
    assert np.max(np.abs(T)) == 0.0


def test_gecersiz_dugum_parametreleri():
    with pytest.raises(ValueError):
        ks.dugum_dizisi(0, 3)
    with pytest.raises(ValueError):
        ks.dugum_dizisi(5, -1)
    with pytest.raises(ValueError):
        ks.dugum_dizisi(5, 3, alt=1.0, ust=-1.0)


def test_kubik_spline_kubigi_tam_temsil_ediyor():
    """Taban kapalıyken kübik uydurma makine hassasiyetine yakın olmalı."""
    t = np.linspace(-1, 1, 400)
    kenar = ks.BSplineKenar(5, 3, w_taban=0.0)
    artik = kenar.uydur(t, t ** 3 - t)
    assert artik < 1e-7


def test_uydurma_izgara_siklastikca_iyilesiyor():
    t = np.linspace(-1, 1, 400)
    y = np.sin(3 * t)
    onceki = float("inf")
    for G in (5, 10, 20, 40):
        a = ks.BSplineKenar(G, 3).uydur(t, y)
        assert a < onceki
        onceki = a
    assert onceki < 1e-6


def test_dugum_dizisi_disinda_temel_tam_sifir():
    kenar = ks.BSplineKenar(8, 3)
    disarida = np.array([-3.0, -2.0, 2.0, 3.0])
    assert np.max(np.abs(kenar.temel(disarida))) < 1e-12
    # Ama φ sıfır değil — taban terimi sayesinde:
    assert np.max(np.abs(kenar(disarida))) > 0.1


def test_yanlis_katsayi_sayisi_reddediliyor():
    with pytest.raises(ValueError):
        ks.BSplineKenar(5, 3, c=np.zeros(3))


def test_kenar_turevi_sayisal_turevle_uyusuyor():
    t = np.linspace(-1, 1, 300)
    kenar = ks.BSplineKenar(10, 3)
    kenar.uydur(t, np.sin(3 * t))
    p = np.linspace(-0.8, 0.8, 41)
    h = 1e-6
    sayisal = (kenar(p + h) - kenar(p - h)) / (2 * h)
    assert np.max(np.abs(kenar.turev(p) - sayisal)) < 1e-6


def test_katman_paylasimli_temel_naifle_ayni_netice():
    """Hızlanma neticeyi değiştirmemeli — asıl şart budur."""
    r = np.random.default_rng(0)
    X = r.uniform(-0.9, 0.9, (300, 6))
    kat = ks.KANKatmani(6, 5, G=8, k=3)
    Y = kat.ileri(X)
    sig = 1.0 / (1.0 + np.exp(-X))
    naif = np.zeros((X.shape[0], 5))
    for i in range(6):
        B = ks.bspline_temeli(X[:, i], kat.dugumler, kat.k)
        for j in range(5):
            naif[:, j] += (B @ (kat.C[i, j] * kat.W_spline[i, j])
                           + X[:, i] * sig[:, i] * kat.W_taban[i, j])
    assert np.max(np.abs(Y - naif)) < 1e-12


def test_katman_girdi_sekli_denetleniyor():
    kat = ks.KANKatmani(4, 3)
    with pytest.raises(ValueError):
        kat.ileri(np.zeros((10, 5)))


def test_katman_parametre_sayisi():
    kat = ks.KANKatmani(3, 4, G=5, k=3)
    assert kat.parametre_sayisi == 3 * 4 * (5 + 3) + 3 * 4 + 3 * 4


def test_kan_yigini_calisiyor():
    ag = ks.KAN([4, 8, 8, 2], G=6, k=3, tohum=1)
    r = np.random.default_rng(0)
    Z = ag(r.uniform(-0.8, 0.8, (50, 4)))
    assert Z.shape == (50, 2)
    assert np.all(np.isfinite(Z))
    assert ag.parametre_sayisi == sum(k.parametre_sayisi for k in ag.katmanlar)


def test_kan_en_az_iki_boyut_istiyor():
    with pytest.raises(ValueError):
        ks.KAN([4])


# ══════════════════════════════════════════════════════════════════════
#  4. Raporlar
# ══════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("modul", [mf, mo, ks])
def test_rapor_uretiliyor(modul):
    m = modul.rapor()
    assert isinstance(m, str) and len(m) > 200
