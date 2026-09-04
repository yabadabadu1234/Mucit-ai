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

from matematik import geometri as ks
from matematik import geometri as mf
from matematik import geometri as mo


# ══════════════════════════════════════════════════════════════════════
#  1. Manifold — bilinen eğrilikler
# ══════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("n", [1, 2, 3, 4])
def test_duz_uzayda_her_sey_sifir(n):
    d = mf.hazir_metrik("düz", n=n)
    x = np.linspace(0.2, 1.4, n)
    assert np.max(np.abs(d.christoffel(x))) < 1e-12
    assert np.max(np.abs(d.riemann(x))) < 1e-12
    assert abs(d.skaler_egrilik(x)) < 1e-12


@pytest.mark.parametrize("r", [0.5, 1.0, 2.0, 3.0])
def test_kurede_K_bir_bolu_r_kare(r):
    k = mf.hazir_metrik("küre", r=r)
    for p in ([1.0, 0.4], [0.8, 2.0], [2.0, 1.1]):
        K = k.kesit_egriligi(np.array(p), [1.0, 0.0], [0.0, 1.0])
        assert K == pytest.approx(1.0 / r ** 2, rel=1e-5), p
        assert k.skaler_egrilik(np.array(p)) == pytest.approx(
            2.0 / r ** 2, rel=1e-5)


def test_hiperbolik_duzlemde_K_eksi_bir():
    h = mf.hazir_metrik("hiperbolik")
    for p in ([0.0, 1.0], [2.0, 0.5], [-1.0, 3.0], [0.5, 1.3]):
        K = h.kesit_egriligi(np.array(p), [1.0, 0.0], [0.0, 1.0])
        assert K == pytest.approx(-1.0, rel=1e-5), p
        assert h.skaler_egrilik(np.array(p)) == pytest.approx(-2.0, rel=1e-5)


def test_kesit_egriligi_isaret_konvansiyonu_sabit():
    """Kürede POZİTİF, hiperbolikte NEGATİF — ikisi aynı formülle."""
    kK = mf.hazir_metrik("küre", r=1.0).kesit_egriligi(np.array([1.0, 0.4]),
                                             [1.0, 0.0], [0.0, 1.0])
    hK = mf.hazir_metrik("hiperbolik").kesit_egriligi(np.array([0.5, 1.3]),
                                               [1.0, 0.0], [0.0, 1.0])
    assert kK > 0 and hK < 0


def test_paralel_vektorlerde_kesit_tanimsiz():
    k = mf.hazir_metrik("küre", r=1.0)
    K = k.kesit_egriligi(np.array([1.0, 0.4]), [1.0, 0.0], [2.0, 0.0])
    assert np.isnan(K)


@pytest.mark.parametrize("ad,m,p", [
    ("küre", mf.hazir_metrik("küre", r=1.0), [1.0, 0.4]),
    ("küre-r2", mf.hazir_metrik("küre", r=2.0), [0.8, 1.7]),
    ("hiperbolik", mf.hazir_metrik("hiperbolik"), [0.5, 1.3]),
    ("düz", mf.hazir_metrik("düz", n=3), [0.2, -0.4, 1.0]),
])
def test_riemann_simetrileri(ad, m, p):
    r = mf.riemann_simetrileri(m, p, tol=1e-5)
    assert r["hepsi_sağlanıyor"] is True, (ad, r)


def test_christoffel_alt_indislerde_simetrik():
    """Levi-Civita burulmasızdır: ``Γ^k_{ij} = Γ^k_{ji}``."""
    for m, p in ((mf.hazir_metrik("küre", r=1.0), [1.0, 0.4]),
                 (mf.hazir_metrik("hiperbolik"), [0.5, 1.3])):
        G = m.christoffel(np.array(p))
        assert np.max(np.abs(G - np.transpose(G, (0, 2, 1)))) < 1e-9


def test_ricci_simetrik():
    for m, p in ((mf.hazir_metrik("küre", r=1.0), [1.0, 0.4]),
                 (mf.hazir_metrik("hiperbolik"), [0.5, 1.3])):
        R = m.ricci(np.array(p))
        olcek = max(float(np.max(np.abs(R))), 1e-30)
        assert np.max(np.abs(R - R.T)) / olcek < 1e-6


def test_laplace_beltrami_iki_yol_uyusuyor():
    f = lambda z: float(np.sin(z[0]) * np.exp(0.3 * z[1]))
    for m, p in ((mf.hazir_metrik("düz", n=2), [0.4, 0.9]),
                 (mf.hazir_metrik("küre", r=1.0), [1.0, 0.4]),
                 (mf.hazir_metrik("hiperbolik"), [0.5, 1.3])):
        a = m.laplace_beltrami(f, np.array(p))
        b = m.laplace_beltrami_christoffel(f, np.array(p))
        assert abs(a - b) < 1e-4, (m.ad, a, b)


def test_duz_uzayda_laplace_beltrami_alelade_laplasyene_iniyor():
    f = lambda z: float(np.sin(z[0]) * np.exp(0.3 * z[1]))
    p = np.array([0.4, 0.9])
    tam = (-np.sin(p[0]) + 0.09 * np.sin(p[0])) * np.exp(0.3 * p[1])
    assert mf.hazir_metrik("düz", n=2).laplace_beltrami(f, p) == pytest.approx(
        tam, abs=1e-5)


def test_sabit_fonksiyonun_laplasyeni_sifir():
    for m, p in ((mf.hazir_metrik("küre", r=1.0), [1.0, 0.4]),
                 (mf.hazir_metrik("hiperbolik"), [0.5, 1.3])):
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
        mf.hazir_metrik("küre", r=1.0).denetle([0.0, 0.0])


def test_konformal_metrik_duzle_ayni_esik():
    """``φ ≡ 0`` iken konformal metrik düz metriğe inmeli."""
    k = mf.hazir_metrik("konformal", n=2, olcek=lambda x: 0.0)
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
    G = phi.metrik_cek(mf.hazir_metrik("düz", n=3), x)
    J = phi.dphi(x)
    assert np.max(np.abs(G - J.T @ J)) < 1e-12
    assert np.max(np.abs(G - G.T)) < 1e-12
    assert np.min(np.linalg.eigvalsh(G)) > 0


def test_izometri_ve_konformallik_ayirt_ediliyor():
    duz2 = mf.hazir_metrik("düz", n=2)
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
    kure = mf.hazir_metrik("küre", r=1.0)
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


# ══════════════════════════════════════════════════════════════════════
#  5. FNO — ızgaradan bağımsızlık
# ══════════════════════════════════════════════════════════════════════

from matematik import geometri as fn
from matematik import geometri as kn
from matematik import geometri as yp


@pytest.mark.parametrize("N", [16, 17, 63, 64, 128, 257])
def test_parseval(N):
    v = fn.yeniden_ornekle(fn._ornek_alan, N)
    assert fn.parseval_sapmasi(v) < 1e-13


def test_kesme_kipi_band_sinirli_alanda_kucuk():
    x = np.linspace(0, 1, 256, endpoint=False)
    tek = np.sin(2 * np.pi * x)[:, None]
    assert fn.kesme_kipi(tek, 1e-12) == 1
    # Beyaz gürültüde kesilecek kuyruk yok:
    g = np.random.default_rng(0).normal(0, 1, (256, 1))
    assert fn.kesme_kipi(g, 1e-2) > 100


def test_kesme_kipi_bos_sinyalde_sifir():
    assert fn.kesme_kipi(np.zeros((32, 2))) == 0


def test_fno_izgaradan_bagimsiz_evrisim_degil():
    """Asıl iddia: FNO'nun çekirdeği KİP cinsinden, evrişiminki piksel."""
    f = fn.SpektralKatman(2, 3, k_kesme=8, tohum=1)
    e = fn.EvrisimKatmani(2, 3, yari_genislik=4, tohum=1)
    for Nk, Ni in ((32, 64), (64, 256)):
        a = fn.izgaradan_bagimsizlik(f, fn._ornek_alan, Nk, Ni)
        b = fn.izgaradan_bagimsizlik(e, fn._ornek_alan, Nk, Ni)
        assert a["bağıl_fark"] < 1e-12, (Nk, Ni, a)
        assert b["bağıl_fark"] > 1e-2, (Nk, Ni, b)


def test_izgara_kat_degilse_kiyas_reddediliyor():
    f = fn.SpektralKatman(2, 2, 4)
    with pytest.raises(ValueError):
        fn.izgaradan_bagimsizlik(f, fn._ornek_alan, 30, 64)


def test_yigindaki_sapmanin_sebebi_ortusme():
    """Doğrusal aktivasyonda makine hassasiyeti; tanh'ta örtüşme."""
    dogrusal = fn.FNO([2, 8, 8, 1], k_kesme=12, tohum=2)
    for kat in dogrusal.katmanlar:
        kat.aktivasyon = lambda z: z
    tanhli = fn.FNO([2, 8, 8, 1], k_kesme=12, tohum=2)
    a = fn.izgaradan_bagimsizlik(dogrusal, fn._ornek_alan, 64, 256)
    b = fn.izgaradan_bagimsizlik(tanhli, fn._ornek_alan, 64, 256)
    assert a["bağıl_fark"] < 1e-12
    assert b["bağıl_fark"] > a["bağıl_fark"] * 1e6


def test_kip_sayisi_izgaradan_fazla_istenirse():
    kat = fn.SpektralKatman(2, 2, k_kesme=40, tohum=0)
    for N in (8, 16, 64, 128):
        assert kat.kullanilan_kip(N) == min(41, N // 2 + 1)
        y = kat.ileri(fn.yeniden_ornekle(fn._ornek_alan, N))
        assert y.shape == (N, 2) and np.all(np.isfinite(y))


def test_fno_girdi_kanali_denetleniyor():
    with pytest.raises(ValueError):
        fn.SpektralKatman(2, 3, 4).ileri(np.zeros((32, 5)))
    with pytest.raises(ValueError):
        fn.SpektralKatman(2, 3, -1)
    with pytest.raises(ValueError):
        fn.FNO([4])


def test_rfft_tam_fft_ile_ayni():
    v = fn.yeniden_ornekle(fn._ornek_alan, 128)
    Vr = np.fft.rfft(v, axis=0)
    Vf = np.fft.fft(v, axis=0)[:Vr.shape[0]]
    assert np.max(np.abs(Vr - Vf)) < 1e-12


# ══════════════════════════════════════════════════════════════════════
#  6. Kan genişlemeleri
# ══════════════════════════════════════════════════════════════════════

@pytest.fixture
def ok_kat():
    return kn.ok_kategorisi()


@pytest.fixture
def F_ok(ok_kat):
    return kn.Funktor(ok_kat,
                      {"0": frozenset({"x", "y"}), "1": frozenset({"p"})},
                      {("id", "0"): {"x": "x", "y": "y"},
                       ("id", "1"): {"p": "p"},
                       "u": {"x": "p", "y": "p"}}, ad="F")


def test_kategori_aksiyomlari_denetleniyor():
    with pytest.raises(ValueError):
        kn.Kategori(("a",), (("id", "a"), "kacak"),
                    {("id", "a"): "a", "kacak": "a"},
                    {("id", "a"): "a", "kacak": "a"},
                    {}, {"a": ("id", "a")})


def test_funktor_denetimi(F_ok, ok_kat):
    assert F_ok.funktoryel_mi()[0] is True
    bozuk = kn.Funktor(ok_kat,
                       {"0": frozenset({"x"}), "1": frozenset({"p", "q"})},
                       {("id", "0"): {"x": "x"},
                        ("id", "1"): {"p": "q", "q": "p"},
                        "u": {"x": "p"}})
    ok, sebep = bozuk.funktoryel_mi()
    assert ok is False and "birim" in sebep


def test_lan_ve_ran_id_boyunca_F_yi_veriyor(F_ok, ok_kat):
    idA = kn.Funktor(ok_kat, {a: a for a in ok_kat.nesneler},
                     {f: f for f in ok_kat.oklar}, hedef=ok_kat, ad="id")
    for b in ok_kat.nesneler:
        assert kn.lan(idA, F_ok, b)["sınıf_sayısı"] == len(F_ok.nes[b])
        assert kn.ran(idA, F_ok, b)["eleman_sayısı"] == len(F_ok.nes[b])


def test_lan_sola_eslenik(ok_kat):
    """|Nat(Lan_K F, G)| = |Nat(F, G∘K)| — sayılarak."""
    T = kn.sonlu_kategori(("*",), [], ad="1")
    F0 = kn.Funktor(T, {"*": frozenset({"a", "b"})},
                    {("id", "*"): {"a": "a", "b": "b"}}, ad="F0")
    Gler = [
        kn.Funktor(ok_kat, {"0": frozenset({"p"}), "1": frozenset({"p"})},
                   {("id", "0"): {"p": "p"}, ("id", "1"): {"p": "p"},
                    "u": {"p": "p"}}),
        kn.Funktor(ok_kat, {"0": frozenset({"x", "y"}),
                            "1": frozenset({"p"})},
                   {("id", "0"): {"x": "x", "y": "y"},
                    ("id", "1"): {"p": "p"}, "u": {"x": "p", "y": "p"}}),
        kn.Funktor(ok_kat, {"0": frozenset({"x"}),
                            "1": frozenset({"p", "q"})},
                   {("id", "0"): {"x": "x"},
                    ("id", "1"): {"p": "p", "q": "q"}, "u": {"x": "q"}}),
    ]
    toplam = 0
    for hedef in ("0", "1"):
        K = kn.Funktor(T, {"*": hedef}, {("id", "*"): ("id", hedef)},
                       hedef=ok_kat, ad=f"K{hedef}")
        assert K.funktoryel_mi()[0]
        LanF = kn.lan_funktor(K, F0)
        assert LanF.funktoryel_mi()[0], LanF.funktoryel_mi()[1]
        for G in Gler:
            sol = kn.dogal_donusumler(LanF, G)
            sag = kn.dogal_donusumler(F0, kn.bileske_funktor(G, K))
            assert sol == sag, (hedef, sol, sag)
            toplam += sol
    assert toplam > 6, "sağlama boş olmasın"


def test_monoid_kategorisi_ve_kaydirma_etkisi():
    M = kn.monoid_kategorisi(3)
    tasiyici = frozenset(range(3))
    FM = kn.Funktor(M, {"*": tasiyici},
                    {("m", i): {x: (x + i) % 3 for x in range(3)}
                     for i in range(3)})
    assert FM.funktoryel_mi()[0]
    idM = kn.Funktor(M, {"*": "*"}, {f: f for f in M.oklar}, hedef=M)
    L = kn.lan(idM, FM, "*")
    assert L["ham_eleman"] == 9      # 3 ok × 3 eleman
    assert L["sınıf_sayısı"] == 3    # ≅ F(*)
    assert kn.ran(idM, FM, "*")["eleman_sayısı"] == 3


def test_birlestir_bul():
    bb = kn.birlestir_bul()
    for i in range(1000):
        bb.ekle(i)
    for i in range(999):
        bb.birlestir(i, i + 1)
    assert len(bb.siniflar()) == 1
    bb2 = kn.birlestir_bul()
    for i in range(1000):
        bb2.ekle(i)
    for i in range(0, 998, 2):
        bb2.birlestir(i, i + 2)
    assert len(bb2.siniflar()) == 501
    assert bb2.birlestir(0, 2) is False   # zaten aynı sınıfta


def test_cevrimli_serbest_kategori_reddediliyor():
    with pytest.raises(ValueError):
        kn.sonlu_kategori(("a", "b"),
                          [("f", "a", "b"), ("g", "b", "a")])


def test_lan_yanlis_tipte_funktoru_reddediyor(ok_kat, F_ok):
    with pytest.raises(ValueError):
        kn.lan(F_ok, F_ok, "0")          # F: A→Set, K olamaz


# ══════════════════════════════════════════════════════════════════════
#  7. Glue köprüsü
# ══════════════════════════════════════════════════════════════════════

def test_ua_sinirda_cokuyor():
    from matematik import tip_teorisi as L
    from matematik import tip_teorisi as S
    Z = S.Tamsayi()
    for e in (L.ozdeslik_denkligi(Z), L.ardil_denkligi()):
        r = yp.ua_sinirda_cokuyor_mu(Z, Z, e)
        assert r["her_ikisi"] is True


def test_ua_ardil_boyunca_tasima_bir_arttiriyor():
    assert yp.ardil_tasima_olc()["eşit"] is True


def test_token_denkligi_tersinir():
    noktalar = [[0.3, -0.5, 1.2, 0.8], [1.0, 0.0, -0.4, 2.1]]
    d = yp.permutasyon_denkligi([2, 0, 3, 1])
    assert d.denklik_mi(noktalar) is True
    assert d.gidis_donus(noktalar)["ileri_sonra_geri"] == 0.0


def test_gecersiz_permutasyon_reddediliyor():
    with pytest.raises(ValueError):
        yp.permutasyon_denkligi([0, 0, 1])


def test_tekil_dizey_denklik_degil():
    with pytest.raises(np.linalg.LinAlgError):
        yp.dogrusal_denklik(np.array([[1.0, 2.0], [2.0, 4.0]]))
    with pytest.raises(ValueError):
        yp.dogrusal_denklik(np.zeros((2, 3)))


def test_tersinirlik_ile_izometri_ayri_seyler():
    """×2 tersinirdir ama izometri DEĞİLDİR — ölçüt ayırt etmeli."""
    noktalar = [[0.3, -0.5, 1.2, 0.8], [1.0, 0.0, -0.4, 2.1]]
    olcek = yp.dogrusal_denklik(np.diag([2.0, 2.0, 2.0, 2.0]))
    k = yp.kayipsizlik_karnesi(olcek, noktalar)
    assert k["tersinir"] is True
    assert k["izometri"] is False
    assert k["|det|"] == pytest.approx(16.0)

    donme = np.array([[np.cos(0.7), -np.sin(0.7), 0, 0],
                      [np.sin(0.7), np.cos(0.7), 0, 0],
                      [0, 0, np.cos(0.3), -np.sin(0.3)],
                      [0, 0, np.sin(0.3), np.cos(0.3)]])
    kd = yp.kayipsizlik_karnesi(yp.dogrusal_denklik(donme), noktalar)
    assert kd["tersinir"] is True and kd["izometri"] is True
    assert kd["|det|"] == pytest.approx(1.0, abs=1e-9)


@pytest.mark.parametrize("modul", [fn, kn, yp])
def test_yeni_modul_raporlari(modul):
    m = modul.rapor()
    assert isinstance(m, str) and len(m) > 200
