"""ogrenme test takımı.

Ölçüt yine bağımsız bilinen cevaba göre: PSD'lik, temsil teoreminin
en iyilik şartı, Eckart–Young'ın kapalı form hatası, zincir kuralının
sayısal türevle sağlaması, ve çözünürlükten bağımsızlık.

Çalıştırma: ``python3 -m pytest ogrenme/test_ogrenme.py -q``
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from ogrenme import izgara as iz
from ogrenme import operator as op
from ogrenme import rkhs as rk


# ══════════════════════════════════════════════════════════════════════
#  1. RKHS
# ══════════════════════════════════════════════════════════════════════

CEKIRDEKLER = {
    "gauss": rk.gauss_cekirdegi(0.5),
    "laplace": rk.laplace_cekirdegi(1.0),
    "matern-1/2": rk.matern_cekirdegi(1.0, 0.5),
    "matern-3/2": rk.matern_cekirdegi(1.0, 1.5),
    "matern-5/2": rk.matern_cekirdegi(1.0, 2.5),
    "polinom-3": rk.polinom_cekirdegi(3),
}


@pytest.mark.parametrize("ad", sorted(CEKIRDEKLER))
def test_cekirdekler_psd(ad):
    r = rk.psd_mi(CEKIRDEKLER[ad], deneme=15)
    assert r["psd_görünüyor"], (ad, r["en_küçük_özdeğer"])


@pytest.mark.parametrize("ad", sorted(CEKIRDEKLER))
def test_cekirdekler_simetrik(ad):
    K = CEKIRDEKLER[ad]
    X = np.random.default_rng(0).normal(size=(12, 3))
    G = np.asarray(K(X, X), float)
    assert np.max(np.abs(G - G.T)) < 1e-10, ad


def test_salinimli_faz_cekirdegi_psd_degil():
    """K24: temsil teoremi orada geçersizdir."""
    def faz(X, Y):
        return np.cos(np.atleast_2d(X) @ np.atleast_2d(Y).T * 3.0
                      + np.sum(np.atleast_2d(X), axis=1)[:, None])
    r = rk.psd_mi(faz)
    assert r["psd_görünüyor"] is False
    assert r["en_küçük_özdeğer"] < -0.1


def test_kare_mesafe_negatif_olmuyor():
    """Açılım yerine doğrudan fark — çok yakın noktalarda bile."""
    X = np.array([[1e8, 1e8], [1e8 + 1e-6, 1e8]])
    D = rk._kare_mesafe(X, X)
    assert np.all(D >= 0.0)
    assert np.max(np.abs(D - D.T)) < 1e-12
    # Gauss çekirdeği 1'i AŞMAMALI:
    assert np.max(rk.gauss_cekirdegi(1.0)(X, X)) <= 1.0 + 1e-15


def test_cekirdek_parametreleri_denetleniyor():
    for f in (rk.gauss_cekirdegi, rk.laplace_cekirdegi):
        with pytest.raises(ValueError):
            f(0.0)
        with pytest.raises(ValueError):
            f(-1.0)
    with pytest.raises(ValueError):
        rk.matern_cekirdegi(1.0, 0.7)      # kapalı formu yok
    with pytest.raises(ValueError):
        rk.matern_cekirdegi(-1.0, 1.5)
    with pytest.raises(ValueError):
        rk.polinom_cekirdegi(0)
    with pytest.raises(ValueError):
        rk.polinom_cekirdegi(2, c=-1.0)


def test_rkhs_uydurma_ve_kosul_sayisi():
    rng = np.random.default_rng(0)
    X = rng.uniform(-2, 2, (50, 1))
    y = np.sin(2 * X[:, 0])
    onceki_kosul = 0.0
    for lam in (1e-1, 1e-3, 1e-6):
        m = rk.RKHS(rk.gauss_cekirdegi(0.5), lam).uydur(X, y)
        # λ küçüldükçe koşul sayısı BÜYÜR:
        assert m.kosul > onceki_kosul
        onceki_kosul = m.kosul
        # Eğitim noktalarında iyi uyuyor:
        assert np.sqrt(np.mean((m(X).ravel() - y) ** 2)) < 0.2


def test_rkhs_negatif_lambda_reddediliyor():
    X = np.zeros((3, 1)); y = np.zeros(3)
    with pytest.raises(ValueError):
        rk.RKHS(rk.gauss_cekirdegi(1.0), -1.0).uydur(X, y)


def test_rkhs_uydurmadan_cagirmak_hata():
    m = rk.RKHS(rk.gauss_cekirdegi(1.0))
    with pytest.raises(ValueError):
        m(np.zeros((2, 1)))
    with pytest.raises(ValueError):
        m.norm_karesi()


def test_rkhs_normu_negatif_olamaz():
    """K19: ``αᵀKα`` skalerdir ve K PSD olduğundan ≥ 0."""
    rng = np.random.default_rng(1)
    for _ in range(10):
        X = rng.uniform(-2, 2, (30, 2))
        y = rng.normal(size=30)
        m = rk.RKHS(rk.gauss_cekirdegi(0.4), 1e-4).uydur(X, y)
        assert m.norm_karesi() >= -1e-12


def test_temsil_teoremi_en_iyilik():
    rng = np.random.default_rng(2)
    X = rng.uniform(-2, 2, (30, 1))
    y = np.sin(2 * X[:, 0])
    for lam in (1e-1, 1e-2, 1e-4):
        r = rk.temsil_teoremi_sagmasi(rk.gauss_cekirdegi(0.5), X, y, lam)
        assert r["en_iyi_mi"] is True, lam
        assert r["artmayan_sapma"] == 0


def test_medyan_genislik():
    X = np.array([[0.0], [1.0], [2.0], [3.0]])
    g = rk.medyan_genislik(X)
    assert g > 0 and math.isfinite(g)
    # Tek nokta: köşegen dışlandığı için sıfıra bölme YOK
    assert rk.medyan_genislik(np.array([[1.0]])) == 1.0
    # Bütün noktalar aynıysa da patlamıyor:
    assert math.isfinite(rk.medyan_genislik(np.zeros((5, 2))))


def test_nystrom_hatasi_ve_sinirlari():
    rng = np.random.default_rng(3)
    X = rng.uniform(-2, 2, (200, 2))
    K = rk.gauss_cekirdegi(rk.medyan_genislik(X))
    r5 = rk.nystrom(K, X, 5, tohum=0)
    r80 = rk.nystrom(K, X, 80, tohum=0)
    # Çok az iniş noktası belirgin hata verir:
    assert r5["bağıl_hata"] > r80["bağıl_hata"]
    # m = N iken hata küçüktür ama SIFIR DEĞİLDİR: kırpma eşiğine
    # yakın özdeğerlerin tersi büyütme yapar.  Ölçüldü: atılan özdeğer
    # kütlesi 6e-14 iken hata 5.2e-5 — yani yaklaşım hatası değil,
    # KOŞULLANMA hatası.
    rN = rk.nystrom(K, X, 200, tohum=0)
    assert rN["bağıl_hata"] < 1e-3
    assert rN["bağıl_hata"] < r80["bağıl_hata"]
    G = rk.gram(K, X)
    oz = np.sort(np.linalg.eigvalsh(G))[::-1]
    atilan = float(np.sqrt(np.sum(oz[rN["kullanılan_rütbe"]:] ** 2))
                   / np.linalg.norm(G, "fro"))
    assert atilan < 1e-10
    assert rN["bağıl_hata"] > 100 * atilan, (
        "hata atılan kütleden geliyor görünüyor — gerekçe yeniden tartılmalı")
    for r in (r5, r80, rN):
        assert r["yaklaşık"].shape == (200, 200)
        assert 0 < r["kullanılan_rütbe"] <= r["m"]


def test_nystrom_gecersiz_m():
    X = np.zeros((10, 1))
    K = rk.gauss_cekirdegi(1.0)
    for m in (0, 11, -1):
        with pytest.raises(ValueError):
            rk.nystrom(K, X, m)


def test_nystrom_yaklasimi_simetrik_ve_psd():
    rng = np.random.default_rng(4)
    X = rng.uniform(-1, 1, (60, 2))
    r = rk.nystrom(rk.gauss_cekirdegi(1.0), X, 20, tohum=1)
    A = r["yaklaşık"]
    assert np.max(np.abs(A - A.T)) < 1e-10
    assert np.min(np.linalg.eigvalsh((A + A.T) / 2)) > -1e-8


# ══════════════════════════════════════════════════════════════════════
#  2. DeepONet ve FINO
# ══════════════════════════════════════════════════════════════════════

def _sensor_ve_u(m=32, n=200, tohum=0):
    sensor = np.linspace(0, 1, m)
    r = np.random.default_rng(tohum)
    a, b = r.normal(size=(n, 4)), r.normal(size=(n, 4))
    kip = np.arange(1, 5)[:, None]
    U = a @ np.cos(2 * np.pi * kip * sensor) + b @ np.sin(2 * np.pi * kip * sensor)
    return sensor, U


def test_deeponet_antiturevi_ogreniyor():
    sensor, U = _sensor_ve_u()
    Y = np.linspace(0, 1, 41)
    H = np.stack([np.interp(Y, sensor, op.ornek_operator(u, sensor))
                  for u in U])
    m = op.DeepONet(m=32, p=16, gizli=40, tohum=0).uydur(U, Y, H, tur=12)
    _, Us = _sensor_ve_u(n=50, tohum=99)
    Hs = np.stack([np.interp(Y, sensor, op.ornek_operator(u, sensor))
                   for u in Us])
    bagil = np.linalg.norm(m(Us, Y) - Hs) / np.linalg.norm(Hs)
    assert bagil < 0.2, bagil


def test_deeponet_cikti_izgarasindan_bagimsiz():
    """Asıl vaat: gövde ``y``ye SÜREKLİ bağlı."""
    sensor, U = _sensor_ve_u()
    Y = np.linspace(0, 1, 41)
    H = np.stack([np.interp(Y, sensor, op.ornek_operator(u, sensor))
                  for u in U])
    m = op.DeepONet(m=32, p=12, gizli=30, tohum=0).uydur(U, Y, H, tur=8)
    for M in (81, 161):
        Yi = np.linspace(0, 1, M)
        r = op.cozunurluk_bagimsizligi(
            m, lambda s: _sensor_ve_u(n=3, tohum=7)[1], sensor, Y, Yi)
        assert r["bağıl_fark"] < 1e-9, (M, r)


def test_cozunurluk_kiyasi_kapsamayan_izgarayi_reddediyor():
    sensor, U = _sensor_ve_u(n=10)
    Y = np.linspace(0, 1, 41)
    H = np.stack([np.interp(Y, sensor, op.ornek_operator(u, sensor))
                  for u in U])
    m = op.DeepONet(m=32, p=4, gizli=8, tohum=0).uydur(U, Y, H, tur=2)
    with pytest.raises(ValueError):
        op.cozunurluk_bagimsizligi(
            m, lambda s: U[:1], sensor, Y, np.linspace(0, 1, 40))


def test_deeponet_gecersiz_girdi():
    with pytest.raises(ValueError):
        op.DeepONet(m=0)
    with pytest.raises(ValueError):
        op.DeepONet(m=4, p=0)
    m = op.DeepONet(m=4, p=2, gizli=4)
    with pytest.raises(ValueError):
        m._dal_ozn(np.zeros((3, 5)))
    with pytest.raises(ValueError):
        m.uydur(np.zeros((3, 4)), np.zeros(5), np.zeros((3, 6)))


def test_fino_eckart_young():
    """Kesilmiş SVD en iyi düşük rütbeli yaklaşımdır; hata kapalı formda."""
    rng = np.random.default_rng(5)
    for sekil in ((20, 20), (30, 18)):
        R = rng.normal(size=sekil)
        for rut in (1, 3, 8):
            d = op.fino_ayristir(R, rut)
            assert abs(d["hata_frobenius"] - d["kapalı_form_hata"]) < 1e-9
            # Rastgele bir başka rütbe-r yaklaşımı DAHA İYİ olamaz:
            A = rng.normal(size=(sekil[0], rut))
            B = rng.normal(size=(rut, sekil[1]))
            assert (np.linalg.norm(A @ B - R, "fro")
                    >= d["hata_frobenius"] - 1e-9)


def test_fino_hata_rutbeyle_dusuyor():
    rng = np.random.default_rng(6)
    R = rng.normal(size=(24, 24))
    onceki = float("inf")
    for rut in (1, 2, 4, 8, 16, 24):
        d = op.fino_ayristir(R, rut)
        assert d["bağıl_hata"] <= onceki + 1e-12
        onceki = d["bağıl_hata"]
    assert onceki < 1e-12          # tam rütbede hata sıfır


def test_fino_uygula_tam_dizeyle_ayni():
    """Birleşme özelliği: ``(UV)v = U(Vv)``."""
    rng = np.random.default_rng(7)
    R = np.exp(-np.add.outer(np.arange(32), np.arange(32)) / 8.0)
    for rut in (2, 4, 8):
        d = op.fino_ayristir(R, rut)
        v = rng.normal(size=32)
        assert np.max(np.abs(op.fino_uygula(d["U"], d["V"], v)
                             - d["yaklaşık"] @ v)) < 1e-10


def test_fino_gecersiz_girdi():
    with pytest.raises(ValueError):
        op.fino_ayristir(np.zeros(5), 1)
    with pytest.raises(ValueError):
        op.fino_ayristir(np.zeros((4, 4)), 0)
    with pytest.raises(ValueError):
        op.fino_ayristir(np.zeros((4, 4)), 5)


def test_spektral_rutbe_bagil_esikle():
    """Ölçek değişince rütbe DEĞİŞMEMELİ."""
    R = np.exp(-np.add.outer(np.arange(32), np.arange(32)) / 6.0)
    for eps in (1e-2, 1e-6):
        assert op.spektral_rutbe(R, eps) == op.spektral_rutbe(1000 * R, eps)
    assert op.spektral_rutbe(np.zeros((4, 4))) == 0
    # Birim dizey tam rütbe ister:
    assert op.spektral_rutbe(np.eye(6), 1e-9) == 6


def test_l2_norm_cozunurlukten_bagimsiz():
    """K30: ölçek çarpanı NORMA girer."""
    f = lambda z: np.sin(2 * np.pi * z)
    normlar = []
    for N in (64, 256, 1024, 4096):
        x = np.linspace(0, 1, N, endpoint=False)
        normlar.append(op.l2_norm(f(x)))
    assert max(normlar) - min(normlar) < 1e-9
    assert normlar[0] == pytest.approx(1 / math.sqrt(2), abs=1e-9)


def test_ornek_operator_antiturev():
    x = np.linspace(0, 1, 400)
    u = np.cos(2 * np.pi * x)
    G = op.ornek_operator(u, x)
    tam = np.sin(2 * np.pi * x) / (2 * np.pi)
    assert np.max(np.abs(G - tam)) < 1e-5
    assert G[0] == pytest.approx(0.0)


# ══════════════════════════════════════════════════════════════════════
#  3. Adaptif ızgara ve sembolik kapanış
# ══════════════════════════════════════════════════════════════════════

def test_dugumler_yapi_geregi_sirali():
    rng = np.random.default_rng(0)
    for _ in range(50):
        s = rng.normal(0, 5.0, int(rng.integers(2, 12)))
        t = iz.artislardan_dugum(-1.0, s)
        assert iz.dugum_gecerli_mi(t), s
        assert np.all(np.diff(t) > 0)
    # Aşırı uçlarda bile:
    for deger in (-1000.0, -1e6, 700.0):
        t = iz.artislardan_dugum(0.0, [deger] * 4)
        assert iz.dugum_gecerli_mi(t), deger
        assert np.all(np.isfinite(t))


def test_dugum_epsilon_denetleniyor():
    with pytest.raises(ValueError):
        iz.artislardan_dugum(0.0, [1.0], eps=0.0)
    with pytest.raises(ValueError):
        iz.artislardan_dugum(0.0, [1.0], eps=-1.0)


def test_artis_gradyani_sayisal_turevle_uyusuyor():
    """Kuyruk toplamı şart; naif hâl katkının çoğunu düşürüyor."""
    rng = np.random.default_rng(1)
    for _ in range(20):
        n = int(rng.integers(2, 7))
        s = rng.normal(0, 1.0, n)
        w = rng.normal(size=n + 1)

        def L(sv):
            return float(np.sum(w * iz.artislardan_dugum(0.0, sv)))

        g = iz.artis_gradyani(w, s)
        h = 1e-6
        say = np.array([(L(s + h * np.eye(n)[i]) - L(s - h * np.eye(n)[i]))
                        / (2 * h) for i in range(n)])
        assert np.max(np.abs(say - g)) < 1e-6 * max(1.0, np.max(np.abs(g)))


def test_naif_gradyan_yanlis():
    """Kaynaktaki yazılış ölçülebilir biçimde sapıyor."""
    s = np.array([0.1, -0.3, 0.5])
    w = np.array([1.0, 2.0, 3.0, 4.0])
    g = iz.artis_gradyani(w, s)
    naif = np.exp(s) * w[1:]
    assert np.max(np.abs(g - naif) / np.abs(g)) > 0.5


def test_artis_gradyani_boyut_denetimi():
    with pytest.raises(ValueError):
        iz.artis_gradyani([1.0, 2.0], [0.0, 0.0])


@pytest.mark.parametrize("G,k", [(5, 2), (5, 3), (8, 3), (10, 4), (6, 5)])
def test_bukulme_dizeyi_simetrik_psd(G, k):
    S = iz.bukulme_dizeyi(G, k)
    assert S.shape == (G + k, G + k)
    assert np.max(np.abs(S - S.T)) < 1e-9
    assert np.min(np.linalg.eigvalsh(S)) > -1e-8


@pytest.mark.parametrize("k", [0, 1])
def test_dusuk_derecede_bukulme_sifir(k):
    """Sabit ve doğrusal parçaların bükülmesi yoktur."""
    S = iz.bukulme_dizeyi(6, k)
    assert np.max(np.abs(S)) == 0.0


def test_bukulme_dogrusallari_cezalandirmiyor():
    """``S``nin çekirdeği tam olarak sabit ve doğrusal fonksiyonlar."""
    from token_uzaylari.kan_spline import bspline_temeli, dugum_dizisi
    G, k = 8, 3
    S = iz.bukulme_dizeyi(G, k)
    d = dugum_dizisi(G, k)
    x = np.linspace(-1, 1, 400)
    B = bspline_temeli(x, d, k)
    for hedef in (np.ones_like(x), x, 2.5 * x - 1.0):
        c, *_ = np.linalg.lstsq(B, hedef, rcond=None)
        assert iz.bukulme_enerjisi(c, S) < 1e-10
    # x² CEZALANIYOR:
    c, *_ = np.linalg.lstsq(B, x ** 2, rcond=None)
    assert iz.bukulme_enerjisi(c, S) > 1.0
    # Çekirdek boyutu tam 2:
    oz = np.linalg.eigvalsh(S)
    assert int(np.sum(np.abs(oz) < 1e-9)) == 2


def test_bukulme_gecersiz_derece():
    with pytest.raises(ValueError):
        iz.bukulme_dizeyi(5, -1)


def test_duzenleme_asiri_uydurmayi_engelliyor():
    """Az veri + çok düğüm: düzenleme sınama hatasını düşürmeli."""
    rng = np.random.default_rng(0)
    xr = np.linspace(-1, 1, 30)
    yr = 1.0 / (1.0 + 25 * xr ** 2) + 0.08 * rng.normal(size=30)
    xt = np.linspace(-1, 1, 500)
    yt = 1.0 / (1.0 + 25 * xt ** 2)
    from token_uzaylari.kan_spline import bspline_temeli, dugum_dizisi
    Bt = bspline_temeli(xt, dugum_dizisi(28, 3), 3)
    hatalar = {}
    for lam in (0.0, 1e-4, 1.0):
        r = iz.duzenli_uydur(xr, yr, 28, 3, lam)
        hatalar[lam] = float(np.sqrt(np.mean((Bt @ r["c"] - yt) ** 2)))
    assert hatalar[1e-4] < hatalar[0.0] / 10      # düzenleme kurtarıyor
    assert hatalar[1e-4] < hatalar[1.0]           # aşırı λ de bozuyor


def test_bukulme_enerjisi_negatif_olamaz():
    rng = np.random.default_rng(2)
    S = iz.bukulme_dizeyi(8, 3)
    for _ in range(30):
        c = rng.normal(size=S.shape[0])
        assert iz.bukulme_enerjisi(c, S) >= -1e-12


def test_bagintili_olcut_sabitte_sifir():
    x = np.linspace(0, 1, 50)
    assert iz.bagintili_olcut(np.ones_like(x), np.sin(x)) == 0.0
    assert iz.bagintili_olcut(x, x) == pytest.approx(1.0)
    assert iz.bagintili_olcut(x, -x) == pytest.approx(-1.0)


def test_sembolik_kapanis_dogru_adayi_buluyor():
    x = np.linspace(-1.5, 1.5, 300)
    for ad, phi in (("sin(3x)", np.sin(3 * x)),
                    ("x^2", 2.5 * x ** 2 - 1.0),
                    ("x^3", -0.7 * x ** 3 + 2.0)):
        r = iz.sembolik_kapanis(x, phi)
        assert r["kabul"] is True, ad
        assert r["en_iyi"]["ad"] == ad, (ad, r["en_iyi"]["ad"])
        assert r["en_iyi"]["bağıl_artık"] < 1e-9


def test_sembolik_kapanis_uymayani_reddediyor():
    """Kütüphanede olmayan bir şey ZORLANMIYOR."""
    x = np.linspace(-1.5, 1.5, 300)
    phi = np.sin(3 * x) * np.exp(-x ** 2) + 0.3 * x ** 3
    r = iz.sembolik_kapanis(x, phi)
    assert r["kabul"] is False
    assert r["en_iyi"]["bağıl_artık"] > 0.1


def test_sadelik_cezasinin_bedeli_olculuyor():
    """μ=0 doğru cevabı verir; μ>0 sade olanı öne alabilir."""
    rng = np.random.default_rng(3)
    x = np.linspace(-1.5, 1.5, 300)
    phi = np.tanh(x) + 0.01 * rng.normal(size=x.size)
    assert iz.sembolik_kapanis(x, phi, mu=0.0)["en_iyi"]["ad"] == "tanh(x)"
    assert iz.sembolik_kapanis(x, phi, mu=0.02)["en_iyi"]["ad"] == "x"
    # Ama KABUL edilmiyor — ceza sıralamayı bozuyor, kabulü bozmuyor:
    assert iz.sembolik_kapanis(x, phi, mu=0.02)["kabul"] is False


def test_sembolik_kutuphane_sonlu_degerler():
    x = np.linspace(-1.5, 1.5, 50)
    for ad, f, uzunluk in iz.SEMBOL_KUTUPHANESI:
        v = np.asarray(f(x), float)
        assert np.all(np.isfinite(v)), ad
        assert uzunluk >= 1


@pytest.mark.parametrize("modul", [rk, op, iz])
def test_rapor_uretiliyor(modul):
    m = modul.rapor()
    assert isinstance(m, str) and len(m) > 200
