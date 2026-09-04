"""fitrat test takımı.

Ölçüt yine üç kat: sözleşme, riyâzî hüviyet, çapraz sağlama.  Bu
modülde çapraz sağlama bilhassa mühim, çünkü hemen her büyüklüğün
**iki** hesabı var:

* denge → Newton ↔ kapalı çözüm; örtük fonksiyon teoremi ↔ sonlu fark
* ayrışma → Bayes topları ↔ bütün yolları dolaşma
* serbest enerji → ELBO boşluğu ↔ ``KL(q‖p(z|x))``
* havuz → log uzayı ↔ ham çarpım (henüz taşmadığı bölgede)

Çalıştırma: ``python3 -m pytest fitrat/test_fitrat.py -q``
"""

from __future__ import annotations

import math
import random

import numpy as np
import pytest

from fitrat import ayrisma, denge, havuz, serbest_enerji, tevafuk


# ══════════════════════════════════════════════════════════════════════
#  1. Denge
# ══════════════════════════════════════════════════════════════════════

def test_cournot_simetrik_kapali_cozumle_ayni():
    n, a, b, c = 4, 10.0, 1.0, 2.0
    oyun = denge.cournot(n)
    r = denge.denge_bul(oyun, [a, b] + [c] * n)
    assert r["yakınsadı"]
    beklenen = denge.cournot_kapali_cozum(n, a, b, c)
    assert np.allclose(r["x"], beklenen, atol=1e-10)


@pytest.mark.parametrize("n", [2, 3, 5, 8])
def test_cournot_asimetrik_kapali_cozumle_ayni(n):
    """``x_i = [a − (n+1)c_i + Σc] / (b(n+1))`` — FOC'lar toplanarak."""
    a, b = 20.0, 1.5
    cc = np.linspace(1.0, 3.0, n)
    oyun = denge.cournot(n)
    r = denge.denge_bul(oyun, np.concatenate(([a, b], cc)))
    kapali = (a - (n + 1) * cc + cc.sum()) / (b * (n + 1))
    assert r["yakınsadı"]
    assert np.allclose(r["x"], kapali, atol=1e-9)


def test_denge_artik_sifir():
    oyun = denge.cournot(3)
    teta = np.array([10.0, 1.0, 2.0, 2.0, 2.0])
    r = denge.denge_bul(oyun, teta)
    assert oyun.artik(r["x"], teta) < 1e-10


def test_teta_boyu_denetleniyor():
    with pytest.raises(ValueError):
        denge.denge_bul(denge.cournot(3), [1.0, 2.0])


def test_ortuk_fonksiyon_teoremi_sonlu_farkla_uyusur():
    """İki bağımsız yol aynı hassasiyeti vermeli."""
    n = 4
    oyun = denge.cournot(n)
    teta = np.array([10.0, 1.0, 1.0, 2.0, 3.0, 4.0])
    r = denge.denge_bul(oyun, teta)
    D = denge.ortuk_fonksiyon_turevi(oyun, r["x"], teta)
    Dsf = denge.hassasiyet_sonlu_farkla(oyun, teta)
    assert D is not None
    assert np.max(np.abs(D - Dsf)) < 1e-6


def test_hassasiyet_kapali_turevle_uyusur():
    """``∂x_i/∂c_i = −n/(b(n+1))``, ``∂x_i/∂c_j = 1/(b(n+1))``."""
    n, b = 4, 1.0
    oyun = denge.cournot(n)
    teta = np.array([10.0, b, 1.0, 2.0, 3.0, 4.0])
    r = denge.denge_bul(oyun, teta)
    D = denge.ortuk_fonksiyon_turevi(oyun, r["x"], teta)
    assert D[0, 2] == pytest.approx(-n / (b * (n + 1)), abs=1e-8)
    assert D[0, 3] == pytest.approx(1.0 / (b * (n + 1)), abs=1e-8)
    assert D[0, 0] == pytest.approx(1.0 / (b * (n + 1)), abs=1e-8)


def test_tekil_jakobide_sayi_uydurulmuyor():
    tekil = denge.Oyun(n=2, p=1,
                       F=lambda x, t: np.array([x[0] + x[1] - t[0]] * 2))
    assert denge.ortuk_fonksiyon_turevi(tekil, np.array([0.5, 0.5]),
                                        [1.0]) is None


def test_merkezi_jakobi_bilinen_turevle_uyusur():
    g = lambda x: np.array([x[0] ** 2 * x[1], np.sin(x[0]) + x[1] ** 3])
    x = np.array([1.3, -0.7])
    J = denge.merkezi_jakobi(g, x)
    tam = np.array([[2 * x[0] * x[1], x[0] ** 2],
                    [np.cos(x[0]), 3 * x[1] ** 2]])
    assert np.max(np.abs(J - tam)) < 1e-9


def test_cournot_dengesi_akis_olarak_kararli():
    oyun = denge.cournot(4)
    teta = np.array([10.0, 1.0, 2.0, 2.0, 2.0, 2.0])
    r = denge.denge_bul(oyun, teta)
    k = denge.kararli_mi(oyun, r["x"], teta)
    assert k["akış_kararlı"] is True
    assert k["tekil_mi"] is False


def test_eszamanli_en_iyi_karsilik_n4te_iraksiyor():
    """Bu bir kusur değil: ρ = (n−1)/2 = 1.5 > 1."""
    a, b, c, n = 10.0, 1.0, 2.0, 4
    en_iyi = lambda x: (a - c - b * (float(np.sum(x)) - x)) / (2 * b)
    it = denge.en_iyi_karsilik_iterasyonu(en_iyi, np.zeros(n), azami=200)
    assert it["yakınsadı"] is False


def test_sonumlu_en_iyi_karsilik_newtonla_ayni_yere_variyor():
    a, b, c, n = 10.0, 1.0, 2.0, 4
    en_iyi = lambda x: (a - c - b * (float(np.sum(x)) - x)) / (2 * b)
    sonumlu = lambda x: 0.5 * x + 0.5 * en_iyi(x)
    it = denge.en_iyi_karsilik_iterasyonu(sonumlu, np.zeros(n))
    r = denge.denge_bul(denge.cournot(n), [a, b] + [c] * n)
    assert it["yakınsadı"] is True
    assert np.max(np.abs(it["x"] - r["x"])) < 1e-10


def test_spektral_yaricap():
    assert denge.spektral_yaricap(np.diag([0.3, -0.9, 0.5])) == pytest.approx(0.9)


# ══════════════════════════════════════════════════════════════════════
#  2. Ayrışma
# ══════════════════════════════════════════════════════════════════════

def test_uc_temel_yapi():
    zincir = ayrisma.Cizge(("A", "B", "C"), (("A", "B"), ("B", "C")))
    catal = ayrisma.Cizge(("A", "B", "C"), (("B", "A"), ("B", "C")))
    carpis = ayrisma.Cizge(("A", "B", "C"), (("A", "B"), ("C", "B")))
    assert ayrisma.d_ayrik_mi(zincir, ["A"], ["C"]) is False
    assert ayrisma.d_ayrik_mi(zincir, ["A"], ["C"], ["B"]) is True
    assert ayrisma.d_ayrik_mi(catal, ["A"], ["C"]) is False
    assert ayrisma.d_ayrik_mi(catal, ["A"], ["C"], ["B"]) is True
    # Çarpışma tersine: şarta bağlamak AÇIYOR.
    assert ayrisma.d_ayrik_mi(carpis, ["A"], ["C"]) is True
    assert ayrisma.d_ayrik_mi(carpis, ["A"], ["C"], ["B"]) is False


def test_carpismanin_nesli_de_acar():
    g = ayrisma.Cizge(("A", "B", "C", "D"),
                      (("A", "B"), ("C", "B"), ("B", "D")))
    assert ayrisma.d_ayrik_mi(g, ["A"], ["C"]) is True
    assert ayrisma.d_ayrik_mi(g, ["A"], ["C"], ["D"]) is False


def test_iki_usul_rastgele_cizgelerde_uyusuyor():
    """Bayes topları ile bütün yolları dolaşma — 500 sorgu."""
    r = random.Random(20260824)
    for _ in range(500):
        n = r.randint(3, 6)
        adlar = tuple(f"v{i}" for i in range(n))
        kenar = tuple((adlar[i], adlar[j])
                      for i in range(n) for j in range(i + 1, n)
                      if r.random() < 0.45)
        g = ayrisma.Cizge(adlar, kenar)
        x, y = r.sample(adlar, 2)
        kalan = [d for d in adlar if d not in (x, y)]
        Z = r.sample(kalan, r.randint(0, len(kalan)))
        assert (ayrisma.d_ayrik_mi(g, [x], [y], Z)
                is ayrisma.d_ayrik_yollarla(g, [x], [y], Z)), (kenar, x, y, Z)


def test_bitisik_dugumler_hicbir_sartla_ayrilmaz():
    r = random.Random(5)
    for _ in range(100):
        n = r.randint(3, 6)
        adlar = tuple(f"v{i}" for i in range(n))
        kenar = tuple((adlar[i], adlar[j])
                      for i in range(n) for j in range(i + 1, n)
                      if r.random() < 0.4)
        if not kenar:
            continue
        g = ayrisma.Cizge(adlar, kenar)
        a, b = kenar[0]
        kalan = [d for d in adlar if d not in (a, b)]
        Z = r.sample(kalan, r.randint(0, len(kalan)))
        assert ayrisma.d_ayrik_mi(g, [a], [b], Z) is False


def test_cevrimli_cizge_reddediliyor():
    with pytest.raises(ValueError):
        ayrisma.Cizge(("A", "B"), (("A", "B"), ("B", "A")))


def test_ortusen_kumeler_reddediliyor():
    g = ayrisma.Cizge(("A", "B", "C"), (("A", "B"),))
    with pytest.raises(ValueError):
        ayrisma.d_ayrik_mi(g, ["A"], ["B"], ["A"])
    with pytest.raises(ValueError):
        ayrisma.d_ayrik_mi(g, ["A"], ["A"])


def test_arka_kapi_karistiriciyi_buluyor():
    g = ayrisma.Cizge(("X", "Y", "Z"), (("Z", "X"), ("Z", "Y"), ("X", "Y")))
    assert ayrisma.arka_kapi_mi(g, "X", "Y", ["Z"]) is True
    assert ayrisma.arka_kapi_mi(g, "X", "Y", []) is False
    assert ayrisma.arka_kapi_kumeleri(g, "X", "Y") == [frozenset({"Z"})]


def test_arka_kapi_ardila_baglanmayi_reddediyor():
    g = ayrisma.Cizge(("X", "M", "Y"), (("X", "M"), ("M", "Y")))
    assert ayrisma.arka_kapi_mi(g, "X", "Y", ["M"]) is False
    # Karıştırıcı yoksa boş küme doğru cevaptır:
    assert ayrisma.arka_kapi_mi(g, "X", "Y", []) is True


def test_on_kapi_gozlenmemis_karistiricida_calisiyor():
    g = ayrisma.Cizge(("U", "X", "M", "Y"),
                      (("U", "X"), ("U", "Y"), ("X", "M"), ("M", "Y")))
    assert ayrisma.on_kapi_mi(g, "X", "Y", ["M"]) is True
    gozlenen = [z for z in ayrisma.arka_kapi_kumeleri(g, "X", "Y")
                if "U" not in z]
    assert gozlenen == [], "U gözlenmeden arka kapı kapanmamalı"


def test_on_kapi_yonlu_yol_kesilmiyorsa_reddediyor():
    # X → Y doğrudan da gidiyor; M bütün yolları kesmiyor.
    g = ayrisma.Cizge(("X", "M", "Y"),
                      (("X", "M"), ("M", "Y"), ("X", "Y")))
    assert ayrisma.on_kapi_mi(g, "X", "Y", ["M"]) is False


def test_b_ayrisma_tek_ortamda_tutani_kabul_etmiyor():
    o1 = ayrisma.Cizge(("X", "Y", "Z"), (("Z", "X"), ("X", "Y"), ("Z", "Y")))
    o2 = ayrisma.Cizge(("X", "Y", "Z"), (("Z", "X"), ("X", "Y")))
    assert ayrisma.d_ayrik_mi(o2, ["Z"], ["Y"], ["X"]) is True
    assert ayrisma.d_ayrik_mi(o1, ["Z"], ["Y"], ["X"]) is False
    assert ayrisma.b_ayrik_mi([o1, o2], ["Z"], ["Y"], ["X"]) is False


def test_ortak_ayrismalar_kesisim():
    o3 = ayrisma.Cizge(("X", "Y", "Z", "W"),
                       (("Z", "X"), ("X", "Y"), ("W", "Y")))
    o4 = ayrisma.Cizge(("X", "Y", "Z", "W"),
                       (("Z", "X"), ("X", "Y"), ("W", "Y"), ("W", "X")))
    ortak = set(ayrisma.ortak_ayrismalar([o3, o4]))
    assert ortak <= set(ayrisma.butun_ayrismalar(o3))
    assert ortak <= set(ayrisma.butun_ayrismalar(o4))
    assert ("Z", "W", frozenset()) in ortak


# ══════════════════════════════════════════════════════════════════════
#  3. Serbest enerji
# ══════════════════════════════════════════════════════════════════════

@pytest.fixture
def model():
    return serbest_enerji.AyrikModel(
        pz=np.array([0.2, 0.5, 0.3]),
        pxz=np.array([[0.7, 0.2, 0.1],
                      [0.1, 0.6, 0.3],
                      [0.3, 0.3, 0.4]]))


def test_normalize_olmayan_tablo_reddediliyor():
    with pytest.raises(ValueError):
        serbest_enerji.AyrikModel(np.array([0.3, 0.3]),
                                  np.array([[0.5, 0.5], [0.5, 0.5]]))
    with pytest.raises(ValueError):
        serbest_enerji.AyrikModel(np.array([0.5, 0.5]),
                                  np.array([[0.5, 0.6], [0.5, 0.5]]))


def test_sinir_hicbir_q_icin_ihlal_edilmiyor(model):
    for x in range(model.N):
        r = serbest_enerji.sinir_dogrula(model, x, deneme=2000, tohum=x)
        assert r["ihlal_sayısı"] == 0


def test_sinir_ancak_ardilda_siki(model):
    x = 1
    p_zx = serbest_enerji.ardil(model, x)
    surpriz = -serbest_enerji.kanit_log(model, x)
    assert serbest_enerji.serbest_enerji(model, p_zx, x) == pytest.approx(
        surpriz, abs=1e-12)
    # Başka her q'da boşluk kesinlikle pozitif:
    for q in (np.ones(3) / 3, np.array([0.8, 0.1, 0.1])):
        assert serbest_enerji.serbest_enerji(model, q, x) > surpriz + 1e-9


def test_bosluk_tam_olarak_KL_q_ardil(model):
    """ELBO ispatının özdeşliği: ``F + ln p(x) = KL(q‖p(z|x))``."""
    r = np.random.default_rng(3)
    p_zx = serbest_enerji.ardil(model, 2)
    surpriz = -serbest_enerji.kanit_log(model, 2)
    for _ in range(200):
        q = r.dirichlet(np.ones(3))
        bosluk = serbest_enerji.serbest_enerji(model, q, 2) - surpriz
        assert bosluk == pytest.approx(serbest_enerji.kl(q, p_zx), abs=1e-10)


def test_ayrisim_kimligi(model):
    r = np.random.default_rng(11)
    for x in range(model.N):
        for _ in range(50):
            q = r.dirichlet(np.ones(3))
            a = serbest_enerji.serbest_enerji_ayrisimi(model, q, x)
            assert a["ayrışım_sapması"] < 1e-10


def test_kl_sinir_halleri():
    assert serbest_enerji.kl(np.array([0.5, 0.5]),
                             np.array([0.5, 0.5])) == pytest.approx(0.0)
    # q_i = 0 olan terim atlanır (0 ln 0 = 0)
    assert serbest_enerji.kl(np.array([1.0, 0.0]),
                             np.array([0.5, 0.5])) == pytest.approx(math.log(2))
    # q_i > 0 iken p_i = 0 → sonsuz
    assert serbest_enerji.kl(np.array([0.5, 0.5]),
                             np.array([1.0, 0.0])) == float("inf")


def test_koordinat_inisi_ardila_variyor_ve_azaliyor(model):
    for tohum in range(5):
        ki = serbest_enerji.koordinat_inisi(model, 1, adim=80, tohum=tohum)
        assert ki["azalıyor_mu"] is True
        assert abs(ki["ardıla_KL"]) < 1e-12
        assert ki["son_F"] == pytest.approx(ki["sürpriz"], abs=1e-10)


def test_gauss_kl_kapali_form():
    # Aynı dağılım → 0
    assert serbest_enerji.gauss_kl(1.0, 2.0, 1.0, 2.0) == pytest.approx(0.0)
    # Elle: KL(N(0,1)‖N(0,2²)) = ln2 + (1+0)/8 − 0.5
    assert serbest_enerji.gauss_kl(0.0, 1.0, 0.0, 2.0) == pytest.approx(
        math.log(2) + 1 / 8 - 0.5)
    with pytest.raises(ValueError):
        serbest_enerji.gauss_kl(0.0, 0.0, 0.0, 1.0)


def test_gauss_bosluk_KL_ile_ayni():
    r = np.random.default_rng(4)
    for _ in range(200):
        x = float(r.normal(0, 2))
        mq, sq = float(r.normal(0, 2)), float(abs(r.normal(0, 1)) + 0.05)
        g = serbest_enerji.gauss_serbest_enerji(x, mq, sq, 0.0, 1.0, 0.5)
        assert g["boşluk"] >= -1e-9
        assert g["boşluk"] == pytest.approx(g["KL(q‖ardıl)"], abs=1e-9)


def test_gauss_ardil_hassasiyet_toplami():
    """Ardıl hassasiyeti ``1/s_p² + 1/s_g²``, ortalaması ağırlıklı."""
    g = serbest_enerji.gauss_serbest_enerji(1.5, 0.0, 1.0, 0.0, 1.0, 0.5)
    tau = 1 / 1.0 ** 2 + 1 / 0.5 ** 2
    assert g["ardıl_sapma"] == pytest.approx(math.sqrt(1 / tau))
    assert g["ardıl_ortalama"] == pytest.approx((0.0 / 1.0 + 1.5 / 0.25) / tau)


# ══════════════════════════════════════════════════════════════════════
#  4. Tevâfuk
# ══════════════════════════════════════════════════════════════════════

def test_tek_sahitte_tevafuk_tanimsiz():
    H, D = tevafuk.sahit_uret(200, 1, 0.8, 0.0, tohum=1)
    assert tevafuk.tevafuk_olcusu(D, H)["tevafuk"] is None


def test_cift_sayisi_k_kucuk_l():
    H, D = tevafuk.sahit_uret(300, 5, 0.8, 0.0, tohum=1)
    t = tevafuk.tevafuk_olcusu(D, H)
    assert t["çift_sayısı"] == 5 * 4 // 2 == len(t["çiftler"])
    # Her çift bir kere, hiçbiri kendisiyle:
    ciftler = {(c["k"], c["l"]) for c in t["çiftler"]}
    assert len(ciftler) == 10
    assert all(k < l for k, l in ciftler)


def test_ortak_kaynak_arttikca_muteber_sahit_azaliyor():
    """Ağırlıklı ölçünün tekdüze olması aranan hassasiyettir."""
    onceki = float("inf")
    for ok in (0.0, 0.2, 0.5, 0.8, 1.0):
        H, D = tevafuk.sahit_uret(4000, 5, 0.80, ok, tohum=42)
        m = tevafuk.fazla_sayma(D, H)["muteber_şahit_sayısı"]
        assert m <= onceki + 1e-9, f"ortak_kaynak={ok} tekdüzeliği bozdu"
        onceki = m
    assert onceki == pytest.approx(1.0, abs=0.05)   # tam bağımlı → tek şahit


def test_bagimsiz_sahitlerde_muteber_sayi_tama_yakin():
    H, D = tevafuk.sahit_uret(4000, 5, 0.80, 0.0, tohum=42)
    f = tevafuk.fazla_sayma(D, H)
    assert f["muteber_şahit_sayısı"] > 4.8
    assert f["fazla_sayma_oranı"] < 1.05


def test_tam_zit_sahitler_eksi_bir():
    H = np.array([0, 1] * 500)
    t = tevafuk.tevafuk_olcusu([H.copy(), 1 - H], H)
    assert t["tevafuk"] == pytest.approx(-1.0)


def test_sabit_degiskende_baginti_sifir():
    H = np.array([0, 1] * 50)
    sabit = np.ones(100, int)
    t = tevafuk.tevafuk_olcusu([sabit, sabit.copy()], H)
    assert t["tevafuk"] == pytest.approx(0.0)


def test_log_olabilirlik_orani_isareti():
    """Hükümle uyumlu şahit pozitif, zıt şahit negatif log-oran verir."""
    r = np.random.default_rng(0)
    H = r.integers(0, 2, 2000)
    iyi = np.where(r.random(2000) < 0.9, H, 1 - H)
    kotu = 1 - iyi
    assert tevafuk.log_olabilirlik_orani(iyi, H) > 1.5
    assert tevafuk.log_olabilirlik_orani(kotu, H) < -1.5


def test_jeffreys_duzeltmesi_sonsuzu_engelliyor():
    H = np.array([0, 0, 1, 1])
    mukemmel = H.copy()             # düzeltmesiz ln(1/0) = +inf olurdu
    assert math.isfinite(tevafuk.log_olabilirlik_orani(mukemmel, H))


# ══════════════════════════════════════════════════════════════════════
#  5. Havuz
# ══════════════════════════════════════════════════════════════════════

def _bern(p):
    lp, lq = math.log(p), math.log1p(-p)
    return lambda d: lp if d else lq


def _kur(esik=0.7, fark=math.log(3.0)):
    return havuz.Havuz([
        havuz.Hipotez("bozuk", math.log(0.2), _bern(0.9), True),
        havuz.Hipotez("beceriksiz", math.log(0.3), _bern(0.6), False),
        havuz.Hipotez("yolunda", math.log(0.5), _bern(0.1), False),
    ], esik=esik, fark_esigi=fark)


def test_logsumexp_dogru_ve_tasmiyor():
    assert havuz.logsumexp([0.0]) == pytest.approx(0.0)
    assert havuz.logsumexp([0.0, 0.0]) == pytest.approx(math.log(2))
    # Ham exp bunlarda taşardı:
    assert havuz.logsumexp([1000.0, 1000.0]) == pytest.approx(1000 + math.log(2))
    assert havuz.logsumexp([-1000.0, -1000.0]) == pytest.approx(
        -1000 + math.log(2))
    assert havuz.logsumexp([]) == float("-inf")
    assert havuz.logsumexp([float("-inf")] * 3) == float("-inf")


def test_log_normalize_toplami_bir():
    ln = havuz.log_normalize([-3.0, -1.0, -700.0])
    assert sum(math.exp(x) for x in ln) == pytest.approx(1.0)


def test_tek_hipotezli_havuz_reddediliyor():
    with pytest.raises(ValueError):
        havuz.Havuz([havuz.Hipotez("tek", 0.0, _bern(0.5), True)])


def test_onseller_normalize_ediliyor():
    h = havuz.Havuz([havuz.Hipotez("a", math.log(2.0), _bern(0.5), True),
                     havuz.Hipotez("b", math.log(2.0), _bern(0.5), False)])
    assert sum(x.ardil for x in h.hipotezler) == pytest.approx(1.0)


def test_log_uzayi_ham_carpimla_ayni_taşmayan_bolgede():
    """Log uzayının netice DEĞİŞTİRMEDİĞİ, taşmadan önce ölçülür."""
    h = _kur()
    n = 50
    h.deliller_ekle([1] * n)
    ham = np.array([0.2 * 0.9 ** n, 0.3 * 0.6 ** n, 0.5 * 0.1 ** n])
    ham = ham / ham.sum()
    log = np.array([x.ardil for x in h.hipotezler])
    assert np.max(np.abs(np.sort(log) - np.sort(ham))) < 1e-12


def test_hukum_iki_sarti_birden_ariyor():
    # Yüksek ardıl ama zayıf ayrışma → karantina
    h = havuz.Havuz([havuz.Hipotez("A", math.log(0.5), _bern(0.55), True),
                     havuz.Hipotez("B", math.log(0.5), _bern(0.45), False)],
                    esik=0.5, fark_esigi=math.log(3.0))
    h.deliller_ekle([1, 1, 0, 1, 0, 1])
    hh, g = h.hukum()
    assert g["eşik_sağlandı"] is True
    assert g["ayrışma_sağlandı"] is False
    assert hh is havuz.Hukum.KARANTINA


def test_yeterli_delille_kabule_variyor():
    h = _kur()
    h.deliller_ekle([1] * 6)
    hh, g = h.hukum()
    assert hh is havuz.Hukum.KABUL
    assert g["en_yüksek"] == "bozuk"


def test_zit_delil_redde_gotururuyor():
    h = _kur()
    h.deliller_ekle([0] * 10)
    hh, g = h.hukum()
    assert hh is havuz.Hukum.RED
    assert g["en_yüksek"] == "yolunda"


def test_yeni_izah_kesinligi_gevsetiyor():
    h = _kur()
    h.deliller_ekle([1] * 6)
    assert h.hukum()[0] is havuz.Hukum.KABUL
    h.izah_ekle(havuz.Hipotez("başka âlet", math.log(0.1), _bern(0.95), False),
                pay=0.35)
    assert h.hukum()[0] is havuz.Hukum.KARANTINA
    assert sum(x.ardil for x in h.hipotezler) == pytest.approx(1.0)


def test_izah_ekleme_eski_oranlari_koruyor():
    h = _kur()
    h.deliller_ekle([1] * 3)
    once = [x.ardil for x in h.hipotezler]
    h.izah_ekle(havuz.Hipotez("yeni", 0.0, _bern(0.5), False), pay=0.25)
    sonra = [x.ardil for x in h.hipotezler[:-1]]
    # Oranlar sabit kalmalı, hepsi aynı katsayıyla küçülmeli:
    oranlar = [s / o for s, o in zip(sonra, once)]
    assert max(oranlar) - min(oranlar) < 1e-12
    assert oranlar[0] == pytest.approx(0.75)


def test_butun_izahlari_imkansiz_kilan_delil_hata_veriyor():
    h = havuz.Havuz([havuz.Hipotez("A", math.log(0.5),
                                   lambda d: float("-inf"), True),
                     havuz.Hipotez("B", math.log(0.5),
                                   lambda d: float("-inf"), False)])
    with pytest.raises(ValueError):
        h.delil_ekle(1, "imkânsız")


def test_tarih_kaydi_tutuluyor():
    h = _kur()
    h.deliller_ekle([1, 1, 1], ["a", "b", "c"])
    assert [k["delil"] for k in h.tarih] == ["a", "b", "c"]
    assert all("hüküm" in k for k in h.tarih)


# ══════════════════════════════════════════════════════════════════════
#  6. Raporlar (duman testi)
# ══════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("modul", [denge, ayrisma, serbest_enerji,
                                   tevafuk, havuz])
def test_rapor_uretiliyor(modul):
    m = modul.rapor()
    assert isinstance(m, str) and len(m) > 200
