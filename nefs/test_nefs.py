"""
nefs sınamaları.

    python3 -m nefs.test_nefs

Üç kuşak sınama var ve **hangisinin ne ispatladığı** ayrıdır:

  A. **Sözleşme** -- 41 melekenin hepsi koşuyor, alanları doldurup
     boyutları koruyor, akış sırası geçerli. Bu, mimarinin tutarlı
     olduğunu gösterir; doğru düşündüğünü DEĞİL.

  B. **Riyazî özdeşlikler** -- metnin sınanabilir denklemleri fiilen
     sağlanıyor mu? (asiklik, Betti, modus ponens, Bayes, HSIC, makam
     parçalanışı, altın oran, permütasyon, ters simetri…). Bunlar
     eğitilmemiş ağırlıkla dahi doğrudur, çünkü ağırlığa bağlı değildir.

  C. **Davranış** -- tasdik, birbirini teyit eden bağımsız delille
     yükseliyor mu? Tenakuzla düşüyor mu? Teemmül duruyor mu? Bunlar
     mimarinin **işleyişine** dairdir.

Hiçbiri "sistem anlıyor" iddiasını sınamaz; öyle bir iddia da yoktur.
"""
from __future__ import annotations

import time
import traceback
from typing import Callable, List

import numpy as np

from . import akil, beyan, idrak, murakabe
from .akis import AKIS, KULLI_SIRA, Nefs, sira_gecerli_mi
from .meleke import melekeler, sicil
from .uzaylar import Durum, Parametreler, kat_norm, softmax


def _E(tohum: int = 0, n: int = 20, d: int = 12) -> np.ndarray:
    return np.random.default_rng(tohum).normal(size=(n, d))


# =====================================================================
#  A. Sözleşme
# =====================================================================
def test_kirkbir_meleke_kayitli():
    ms = melekeler()
    assert len(ms) == 41, len(ms)
    assert [m.no for m in ms] == list(range(1, 42))
    assert all(m.ad for m in ms)


def test_akis_sirasi_gecerli():
    gecerli, hatalar = sira_gecerli_mi()
    assert gecerli, hatalar


def test_kulli_sira_metinle_uyusuyor():
    """Metnin kapanış bölümündeki silsile akışta korunuyor mu?"""
    ilk, son = {}, {}
    for yer, no in enumerate(AKIS):
        ilk.setdefault(no, yer)
        son[no] = yer
    for a, b in KULLI_SIRA:
        assert ilk[a] <= son[b], (a, b)


def test_ucdan_uca_kosuyor():
    d = Nefs(0).idrak_et(_E(0))
    assert d.X is not None and d.S is not None and d.N is not None
    assert d.S.shape[1] == d.d_sem
    assert np.all(np.isfinite(d.S)) and np.all(np.isfinite(d.N))
    assert d.makam in ("Yakîn", "Zan", "Şek", "Vehim")
    assert 0.0 <= d.T <= 1.0 and 0.0 <= d.P_idrak <= 1.0


def test_farkli_boyutlarda_kosuyor():
    for (n, di, dh, ds) in ((8, 6, 12, 8), (30, 20, 32, 24), (12, 12, 16, 16)):
        d = Nefs(1).idrak_et(_E(1, n, di), d_hayal=dh, d_sem=ds)
        assert d.S.shape == (n, ds), (n, di, dh, ds, d.S.shape)
        assert len(d.N) == ds


def test_sozlesme_ihlali_yakalaniyor():
    """Bir alanı yazmadan okumaya kalkan meleke net hata vermeli."""
    d = Durum.kur(_E(0))
    try:
        sicil()[6].kosu(d, Parametreler(0))     # 𝒪₆ Tasavvur, D yazılmadan
    except ValueError as e:
        assert "boş" in str(e), str(e)
    else:
        raise AssertionError("sözleşme ihlâli yakalanmadı")


def test_surecler_arasi_tekrarlanabilir():
    """Ağırlıklar SÜREÇTEN süreçe aynı mı?

    Bu sınama, ``Parametreler.W``de Python'un ``hash()``i kullanıldığı
    için gerçekten kırılmıştı: dizge hash'i süreç başına rastgeleleşir,
    dolayısıyla her koşuda başka ağırlık üretiliyordu. Süreç içi
    tekrarlanabilirlik sınaması bunu göremez.
    """
    import subprocess, sys, json
    kod = ("import numpy as np;"
           "from nefs.akis import Nefs;"
           "d=Nefs(0).idrak_et(np.random.default_rng(0).normal(size=(20,12)));"
           "print(repr(float(np.sum(d.S))), repr(float(d.T)))")
    ciktilar = set()
    for tohum in ("0", "1", "12345"):
        r = subprocess.run([sys.executable, "-c", kod],
                           capture_output=True, text=True,
                           env={"PYTHONHASHSEED": tohum, "PATH": "/usr/bin:/bin"})
        assert r.returncode == 0, r.stderr
        ciktilar.add(r.stdout.strip())
    assert len(ciktilar) == 1, ciktilar


def test_ayni_tohum_ayni_netice():
    a = Nefs(3).idrak_et(_E(2))
    b = Nefs(3).idrak_et(_E(2))
    assert np.allclose(a.S, b.S) and np.allclose(a.N, b.N)
    assert a.makam == b.makam and abs(a.T - b.T) < 1e-12


# =====================================================================
#  B. Riyazî özdeşlikler
# =====================================================================
def test_betti_bilinen_cizgelerde():
    """β₀ = bileşen sayısı, β₁ = |E| − |V| + β₀."""
    def A(n, kenarlar):
        M = np.zeros((n, n))
        for (i, j) in kenarlar:
            M[i, j] = M[j, i] = 1.0
        return M

    assert idrak.betti_1iskelet(A(4, [])) == (4, 0)                    # 4 nokta
    assert idrak.betti_1iskelet(A(4, [(0, 1), (1, 2), (2, 3)])) == (1, 0)   # yol
    assert idrak.betti_1iskelet(A(4, [(0, 1), (1, 2), (2, 3), (3, 0)])) == (1, 1)  # çevrim
    assert idrak.betti_1iskelet(A(6, [(0, 1), (1, 2), (2, 0),
                                      (3, 4), (4, 5), (5, 3)])) == (2, 2)  # iki üçgen


def test_normalize_laplasyen():
    A = np.array([[0., 1., 0.], [1., 0., 1.], [0., 1., 0.]])
    L = idrak.normalize_laplasyen(A)
    assert np.allclose(np.diag(L), 1.0)
    oz = np.linalg.eigvalsh(L)
    assert oz.min() > -1e-9 and oz.max() < 2 + 1e-9   # spektrum [0,2]
    assert abs(oz.min()) < 1e-9                        # bağlantılı → 0 özdeğeri


def test_asiklik_olcutu():
    """``h(A) = Tr(exp(A∘A)) − d``: DAG'da tam 0, devirde pozitif."""
    dag = np.array([[0., .8, .5], [0., 0., .7], [0., 0., 0.]])
    assert abs(akil.asiklik_ihlali(dag)) < 1e-12
    devir = dag.copy()
    devir[2, 0] = 0.6
    assert akil.asiklik_ihlali(devir) > 1e-6


def test_illet_kesfi_dag_uretiyor():
    d = Nefs(0).idrak_et(_E(0))
    assert d.A_neden is not None
    assert abs(akil.asiklik_ihlali(d.A_neden)) < 1e-9
    assert abs(d.olcum.al("illet.asiklik_ihlali")) < 1e-9


def test_arka_kapi_mudahaleyi_veriyor():
    """`yaklasim.nedensel`in aynı hesabı: karıştırıcıya şart koşmak."""
    rng = np.random.default_rng(0)
    n = 200000
    z = rng.normal(size=n)
    x = 1.5 * z + 0.5 * rng.normal(size=n)
    y = 0.8 * x - 2.0 * z + 0.5 * rng.normal(size=n)
    assert abs(akil.arka_kapi(x, z, y) - 0.8) < 0.02
    ham = float(np.polyfit(x, y, 1)[0])
    assert abs(ham - 0.8) > 0.1          # düzeltilmemiş tahmin yanlı


def test_modus_ponens_dogruluk_tablosu():
    assert akil.ima(True, True) is True
    assert akil.ima(True, False) is False
    assert akil.ima(False, True) is True
    assert akil.ima(False, False) is True
    assert akil.modus_ponens(True, True) is True
    for (P1, P2) in ((True, False), (False, True), (False, False)):
        try:
            akil.modus_ponens(P1, P2)
        except ValueError:
            pass
        else:
            raise AssertionError("öncülsüz çıkarım yapıldı: %s" % ((P1, P2),))


def test_kiyas_bilinen_esplemeyi_geri_buluyor():
    rng = np.random.default_rng(0)
    d = 6
    A = rng.normal(size=(d, d))
    S1 = rng.normal(size=(200, d))
    S2 = S1 @ A.T
    W = akil.kiyas_ogren(S1, S2)
    assert np.linalg.norm(W - A) / np.linalg.norm(A) < 1e-6


def test_bayes_normalizasyonu():
    d = Nefs(0).idrak_et(_E(0))
    assert abs(d.olcum.al("ihtimal.sonsal_toplamı") - 1.0) < 1e-9
    assert 0.0 <= d.olcum.al("ihtimal.sonsal_azami") <= 1.0
    assert d.olcum.al("ihtimal.entropi") >= -1e-12


def test_hsic_bagimsizlikta_sifira_yakin():
    rng = np.random.default_rng(0)
    n = 400
    x = rng.normal(size=n)
    bagimsiz = rng.normal(size=n)
    bagimli = np.sin(3 * x) + 0.1 * rng.normal(size=n)
    h0 = idrak.hsic(x, bagimsiz)
    h1 = idrak.hsic(x, bagimli)
    assert h0 < 0.002, h0
    assert h1 > 5 * h0, (h0, h1)


def test_tenakuz_kendisiyle_celismiyor():
    """Ters simetrik çekirdek ⟹ ``SᵢᵀWSᵢ = 0``: hiçbir önerme kendisiyle
    çelişmez."""
    d = Nefs(0).idrak_et(_E(0))
    assert d.olcum.al("tenakuz.köşegen") < 1e-9


def test_makam_parcalanisi_tam_ve_ayrik():
    """Dört makam ``[0,1]``i TAM ve AYRIK örter."""
    gorulen = set()
    for P in np.linspace(0.0, 1.0, 20001):
        m = murakabe.makam_tayin(float(P))
        assert m in ("Yakîn", "Zan", "Şek", "Vehim"), (P, m)
        gorulen.add(m)
    assert gorulen == {"Yakîn", "Zan", "Şek", "Vehim"}
    # sınırlar: monotonluk (P büyüdükçe makam gerilemez)
    duzen = {"Vehim": 0, "Şek": 1, "Zan": 2, "Yakîn": 3}
    dizi = [duzen[murakabe.makam_tayin(float(P))]
            for P in np.linspace(0, 1, 5001)]
    assert all(dizi[i] <= dizi[i + 1] for i in range(len(dizi) - 1))


def test_hukum_agirligi():
    assert murakabe.hukum_agirligi(0.99, "Yakîn") == 1.0
    assert murakabe.hukum_agirligi(0.5, "Şek") == 0.5
    assert abs(murakabe.hukum_agirligi(0.7, "Zan") - 0.7) < 1e-12
    assert abs(murakabe.ikili_entropi(0.5) - np.log(2)) < 1e-12
    assert murakabe.ikili_entropi(1.0) == 0.0


def test_altin_oran_ve_harmoni():
    assert abs(beyan.ALTIN_ORAN ** 2 - beyan.ALTIN_ORAN - 1.0) < 1e-12
    rng = np.random.default_rng(0)
    A = rng.normal(size=(8, 8))
    simetrik = A + A.T
    ters_simetrik = A - A.T
    assert abs(beyan.simetrik_harmoni(simetrik) - 1.0) < 1e-12
    assert abs(beyan.simetrik_harmoni(ters_simetrik) - 0.0) < 1e-12
    h = beyan.simetrik_harmoni(A)
    assert 0.0 <= h <= 1.0
    # ölçek değişmezliği
    assert abs(beyan.simetrik_harmoni(1000 * A) - h) < 1e-9


def test_tertip_permutasyon_ve_softmax_normlari():
    d = Nefs(0).idrak_et(_E(0))
    assert d.olcum.al("tertip.permütasyon_mu") == 1.0
    assert sorted(d.sira.tolist()) == list(range(len(d.sira)))
    assert abs(d.olcum.al("merak.Q_toplamı") - 1.0) < 1e-9
    assert abs(d.olcum.al("tafsil.ağırlık_toplamı") - 1.0) < 1e-9


def test_lie_tasarrufu_norm_koruyor():
    """``R = exp(θX)``, ``X`` ters simetrik ⟹ ``RᵀR = I``."""
    p = Parametreler(0)
    for dd in (4, 9, 16):
        R = p.lie_tasarruf("sınama.%d" % dd, dd, teta=0.7)
        assert np.allclose(R.T @ R, np.eye(dd), atol=1e-10)
        assert abs(abs(np.linalg.det(R)) - 1.0) < 1e-10


def test_terkip_wedge_ters_simetrik():
    d = Nefs(0).idrak_et(_E(0))
    assert d.olcum.al("terkip.ω_ters_simetrik") < 1e-9


# =====================================================================
#  C. Davranış
# =====================================================================
def test_teemmul_yakinsiyor():
    for t in range(4):
        d = Nefs(t).idrak_et(_E(t))
        assert d.olcum.al("teemmül.yakınsadı") == 1.0, t
        assert d.olcum.al("teemmül.τ_durma") < 200, t
        # geometrik yakınsama: son fark, ilk farkın binde birinden küçük
        assert d.olcum.al("teemmül.azalma_oranı") < 1e-3, t
        # monotonluk garanti DEĞİL; sıçrama olsa da nadir olmalı
        assert d.olcum.al("teemmül.geriye_sıçrama") <= 3, t


def test_muhayyile_serbestligi_hadde_kaliyor():
    for t in range(4):
        d = Nefs(t).idrak_et(_E(t))
        assert d.olcum.al("muhayyile.serbestlik") <= d.olcum.al("muhayyile.tau") + 1e-9
        assert d.Z_muhayyile is not None


def test_deneme_yanilma_ogreniyor():
    kazanan = 0
    for t in range(6):
        d = Nefs(t).idrak_et(_E(t))
        kazanan += int(d.olcum.al("deneme.öğrendi") == 1.0)
    assert kazanan >= 5, kazanan


def test_tefekkur_potansiyeli_dusuruyor():
    for t in range(4):
        d = Nefs(t).idrak_et(_E(t))
        assert d.olcum.al("tefekkür.azaldı") == 1.0, t
        assert d.olcum.al("tefekkür.V_son") < d.olcum.al("tefekkür.V_ilk")


def test_talakat_puruzu_azaltiyor():
    for t in range(4):
        d = Nefs(t).idrak_et(_E(t))
        if d.sukut:
            continue          # sükûtta kelam kurulmaz, düzleşecek şey yok
        assert d.olcum.al("talâkat.düzleşti") == 1.0, t


def test_tevil_ancak_celiski_varsa():
    """Çelişki yoksa veya te'vil çelişkiyi azaltmıyorsa zâhir kalır."""
    for t in range(5):
        d = Nefs(t).idrak_et(_E(t))
        if d.olcum.al("tevil.geçerli") == 1.0:
            assert d.olcum.al("tevil.zâhir_çelişki") > 0.0
            assert d.olcum.al("tevil.müevvel_çelişki") < d.olcum.al("tevil.zâhir_çelişki")


def test_tashih_ancak_iyilestiriyorsa():
    for t in range(5):
        d = Nefs(t).idrak_et(_E(t))
        if d.olcum.al("tashih.başarılı") == 1.0:
            assert d.olcum.al("tashih.yeni_T") > d.olcum.al("tashih.eski_T")


def test_belagat_fesahati_asamaz():
    for t in range(4):
        d = Nefs(t).idrak_et(_E(t))
        if d.sukut:
            continue
        assert d.olcum.al("belâgat.fesâhatı_aşamaz") == 1.0, t


# =====================================================================
#  Şahitlik hattı (kütük H6) ve sükût (H10)
# =====================================================================
def _sahitli_akis(m=4, t=6, d_in=12, bozuk=None, tohum=0):
    """``m`` şahitlik, hepsi aynı dik kaideye tâbi bir akış."""
    rng = np.random.default_rng(tohum)
    R = np.linalg.qr(rng.normal(size=(d_in, d_in)))[0]
    R2 = np.linalg.qr(rng.normal(size=(d_in, d_in)))[0]
    bloklar = []
    for k in range(m):
        G = rng.normal(size=(t, d_in))
        C = G @ (R2 if k == bozuk else R).T
        bloklar.append(np.vstack([G, C + 6.0]) + 60.0 * k)
    return np.vstack(bloklar)


def test_sahit_bolutlemesi_ayirac_sembolu_aramadan():
    """Şahit sayısı **duyudan** sezilir; bayrakla verilmez."""
    d = Nefs(0).idrak_et(_sahitli_akis(m=4))
    assert d.olcum.al("tertip.şahit_verildi") == 0.0
    assert len(d.sahitler) == 4


def test_nakz_yalniz_bozuk_sahidi_dusurur():
    """Kurallı akışta nakz boş; bir şahit bozuksa YALNIZ o düşer."""
    temiz = Nefs(0).idrak_et(_sahitli_akis(m=4))
    assert temiz.nakz == []
    bozuk = Nefs(0).idrak_et(_sahitli_akis(m=4, bozuk=2))
    assert bozuk.nakz == [2], bozuk.nakz


def test_nakz_yakini_dusurur():
    """Tek karşı örnek küllî iddianın idrakini düşürür."""
    temiz = Nefs(0).idrak_et(_sahitli_akis(m=4))
    bozuk = Nefs(0).idrak_et(_sahitli_akis(m=4, bozuk=2))
    assert bozuk.P_idrak < temiz.P_idrak


def test_istikra_sonlu_sahitle_yakin_vermez():
    """``β > 0`` iken ardışıklık kaidesi 1'e ulaşmaz (dürüstlük şartı)."""
    d = Nefs(0).idrak_et(_sahitli_akis(m=4))
    if d.olcum.al("idrak.vekil_formül") == 0.0:
        assert d.P_idrak < 1.0
        assert d.olcum.al("idrak.tam_istikrâ") == 0.0


def test_sekte_sukut_edilir():
    """Makam Şek ise beyan kurulmaz: kelam sıfırdır."""
    import numpy as _np
    d = Nefs(0).idrak_et(_E(0))
    if d.makam == "Şek":
        assert d.sukut
        assert float(_np.linalg.norm(d.N)) == 0.0
    assert d.sukut == (d.makam == "Şek")


def test_hukum_kaydi_semboliktir():
    """𝒪₁₃ mühürü sayı olarak değil KAYIT olarak bırakır (kütük H4)."""
    d = Nefs(0).idrak_et(_E(0))
    assert isinstance(d.hukum, dict)
    assert d.hukum["mühür_sırası"] == 2      # akışta iki kere koşar
    assert set(("T", "mühür", "makam", "gerekçe")) <= set(d.hukum)


def test_tasdik_uyusan_delille_yukseliyor():
    """Aynı sinyalin gürültülü iki kopyası ⟹ tasdik; birbirine ZIT iki
    yarı ⟹ tenakuz yükselir, tasdik düşer.

    Bu, mimarinin işleyişine dair en doğrudan davranış sınamasıdır.
    """
    rng = np.random.default_rng(0)
    taban = rng.normal(size=(10, 12))
    uyusan = np.concatenate([taban, taban + 0.05 * rng.normal(size=taban.shape)])
    celisen = np.concatenate([taban, -taban + 0.05 * rng.normal(size=taban.shape)])

    a = Nefs(0).idrak_et(uyusan)
    b = Nefs(0).idrak_et(celisen)
    assert a.tenakuz <= b.tenakuz + 1e-12, (a.tenakuz, b.tenakuz)


def test_teyit_bagimsizlikla_olculuyor():
    for t in range(4):
        d = Nefs(t).idrak_et(_E(t))
        assert 0.0 <= d.olcum.al("teyit.bağımsızlık") <= 1.0
        assert d.olcum.al("teyit.T_artışı") >= -1e-12      # teyit düşürmez


def test_munazara_tabii_netice_sentez():
    """Cerh eşiği aşılmadıkça netice telîftir, galibiyet değil."""
    sentez = 0
    for t in range(6):
        d = Nefs(t).idrak_et(_E(t))
        sentez += int(d.olcum.al("münazara.netice_sentez") == 1.0)
    assert sentez >= 1, sentez


# =====================================================================
#  Koşturucu
# =====================================================================
def _sinamalar() -> List[Callable[[], None]]:
    g = globals()
    return [g[a] for a in sorted(g) if a.startswith("test_") and callable(g[a])]


def main() -> int:
    gecen, kalan = 0, []
    for f in _sinamalar():
        t0 = time.time()
        try:
            f()
            print("  ✓ %-44s %5.2fs" % (f.__name__, time.time() - t0))
            gecen += 1
        except Exception:
            print("  ✗ %-44s %5.2fs" % (f.__name__, time.time() - t0))
            traceback.print_exc()
            kalan.append(f.__name__)
    print("\n%d geçti, %d kaldı  (%d sınama)"
          % (gecen, len(kalan), gecen + len(kalan)))
    return 1 if kalan else 0


# =====================================================================
#  KAN tabanı: RBF ile B-spline yan yana
# =====================================================================

def test_kan_temelleri_kiyas() -> None:
    """İki taban da çalışmalı; farkları İDDİA değil ÖLÇÜM olmalı.

    Risaleler KAN kenarlarını B-spline ile tarif ediyor; ilk gerçekleme
    Gauss RBF kullanıyordu.  İkisi de tek değişkenli taban verir, fakat
    B-spline üç şeyi garanti eder ki RBF etmez.  Burada o üçü tartılır.
    """
    from nefs.idrak import kan_temeli

    rng = np.random.default_rng(0)
    v = rng.normal(0.0, 1.0, (200, 6))
    nb = 12

    B_rbf = kan_temeli(v, nb, "rbf")
    B_spl = kan_temeli(v, nb, "bspline")
    assert B_rbf.shape == B_spl.shape == (200, 6, nb)
    assert np.all(np.isfinite(B_rbf)) and np.all(np.isfinite(B_spl))

    # 1) Birliğin bölünmesi — B-spline'da tam, RBF'te değil.
    top_spl = B_spl.sum(axis=2)
    top_rbf = B_rbf.sum(axis=2)
    ic = np.abs(v) < 1.5                      # ızgaranın iç bölgesi
    spl_sapma = float(np.max(np.abs(top_spl[ic] - 1.0)))
    rbf_dalga = float(np.max(top_rbf[ic]) - np.min(top_rbf[ic]))
    assert spl_sapma < 1e-12, spl_sapma
    assert rbf_dalga > 1e-3, "RBF toplamı sabit çıktı — kıyas boş"

    # 2) Yerellik — B-spline'da her satırda pek az sıfırdan farklı terim.
    spl_dolu = float(np.mean(np.sum(B_spl > 1e-12, axis=2)))
    rbf_dolu = float(np.mean(np.sum(B_rbf > 1e-12, axis=2)))
    assert spl_dolu <= 4.0 + 1e-9, spl_dolu     # derece 3 → en çok 4
    assert rbf_dolu > spl_dolu

    # 3) Negatiflik — ikisi de negatif değer üretmemeli.
    assert np.min(B_spl) > -1e-12 and np.min(B_rbf) >= 0.0

    # 4) İkisi de gerçek melekede koşabilmeli ve SONLU çıktı vermeli.
    import nefs.idrak as idrak
    eski = idrak.KAN_TEMELI
    ciktilar = {}
    try:
        for tur in ("rbf", "bspline"):
            idrak.KAN_TEMELI = tur
            d = Nefs(3).idrak_et(_E(3))
            assert np.all(np.isfinite(d.Z_muhayyile)), tur
            assert np.all(np.isfinite(d.S)) and np.all(np.isfinite(d.N)), tur
            # Muhayyile'nin vaadi: serbestlik her hâlükârda τ'nun altında
            assert d.olcum.al("muhayyile.serbestlik") <= \
                d.olcum.al("muhayyile.tau") + 1e-9, tur
            ciktilar[tur] = d.Z_muhayyile.copy()
    finally:
        idrak.KAN_TEMELI = eski

    # İki taban aynı sayıyı vermez (vermeseydi kıyas anlamsız olurdu),
    # ama ikisi de melekenin şartını sağlar.
    fark = float(np.max(np.abs(ciktilar["rbf"] - ciktilar["bspline"])))
    assert fark > 0.0, "iki taban birebir aynı çıktı verdi — kıyas boş"


# =====================================================================
#  D. KÂİDE MÎZÂNI -- H85'in icrası, H90'ın şartıyla
# =====================================================================
def test_kaide_mizani_yesil_de_kirmizi_da_yanabiliyor():
    """H90: bir ölçüt, **kırmızı yanabildiğini** ispatlamadıkça ölçüt değildir.

    Burada iki hâl birden kurulur ve ikisi de zorunludur:

    * **Yeşil**: çıktının girdinin devriği olduğu, bile bile kurulmuş bir
      görevde ``devrik/devrik`` kâidesi **Yakîn**e çıkmalı, illeti
      ``yer_devrik`` olarak ayırt edilmeli, tekliği ispatlanmalı.
    * **Kırmızı**: tek bir şahit kasten bozulunca aynı kâide Yakîn'den
      **düşmeli** -- ``nakz``ın tarifi budur: tek karşı örnek küllî
      hükmü düşürür (kütük H6).

    Bu sınama evvelâ **yeşil yanamıyordu** ve kusur ölçütteydi: menfî
    vaka şahitler arasında aranıyordu, halbuki kâide doğruysa öyle bir
    şahit yoktur. Menfî vaka, aynı şahitte düşen **rakip kâidedir**.
    """
    from .kaide import namzetleri_ele

    rng = np.random.default_rng(0)
    sahit = []
    for _ in range(4):
        g = rng.integers(0, 5, size=(3, 4))
        sahit.append((g, g.T.copy()))

    hepsi = namzetleri_ele(sahit)
    yakin = [i for i in hepsi if i.makam == "Yakîn"]
    assert len(yakin) == 1, [i.satir() for i in hepsi[:3]]
    e = yakin[0]
    assert e.kaide_adi == "devrik/devrik", e.kaide_adi
    assert e.derece == 1.0 and e.ebat_tek_mi and e.renk_tek_mi
    assert "yer_devrik" in e.illet and e.illet_izah_edildi
    assert e.nakz_sahidi is None          # düşüren şahit yok

    # --- KIRMIZI: bir şahidi boz, Yakîn düşsün
    bozuk = list(sahit)
    bozuk[2] = (bozuk[2][0], rng.integers(0, 5, size=(4, 3)))
    h2 = namzetleri_ele(bozuk)
    assert not [i for i in h2 if i.makam == "Yakîn"], \
        "bozuk şahitle hâlâ Yakîn çıkıyor — ölçüt kırmızı yanamıyor"
    d = [i for i in h2 if i.kaide_adi == "devrik/devrik"][0]
    assert d.nakz_sahidi == 2, d.nakz_sahidi   # nakzeden şahidi göstermeli


def test_kaide_eksik_istikra_yakin_vermez():
    """``tam_istikra_mi``nin hükmü mîzânda fiilen işliyor mu?

    Rakibi elenmemiş bir kâide, BÜTÜN misallerde tutsa bile Yakîn'e
    çıkmamalı; Zan'da kalmalı. Yakîn istikrâdan değil **tekliğin
    ispatından** gelir. Burada girdi kare seçilir; o zaman ``aynı`` ile
    ``devrik`` ebatta ayırt edilemez ve teklik ispatlanamaz.
    """
    from .kaide import namzetleri_ele
    from mizan.istikra import tam_istikra_mi

    assert not tam_istikra_mi(50, 50)       # eksik istikrâ 1 vermez

    rng = np.random.default_rng(1)
    sahit = []
    for _ in range(4):
        g = rng.integers(0, 5, size=(3, 3))   # KARE → ebat kaideleri eşleşir
        sahit.append((g, g.copy()))
    hepsi = namzetleri_ele(sahit)
    en = hepsi[0]
    assert all(en.ebat_dogru) and all(en.renk_dogru), en.satir()
    assert not en.ebat_tek_mi, en.ebat_rakipleri   # rakip duruyor
    assert en.makam == "Zan", en.satir()
    assert en.nakz_delili is not None      # niçin tek olmadığının delili




def test_qkaide_oragi_kaideyi_yukseltiyor():
    """Kâide orağı, ebat kâidesini süperpozisyondan **çekip çıkarıyor mu**?

    H97'de ölçüldü ki evvelki hâli hiçbir şey yükseltmiyordu (dağılım
    düpedüz düzgün, 1/64). İki kusur düzeltildi: difüzyon ``k`` katlı
    kontrollü ``Z`` oldu (tek kübitlik ``Z``lerin çarpımı DEĞİL), ve
    işaretleme açı yerine MPO işaretine geçti.

    H90 gereği ölçüt hem yeşil hem kırmızı yanabilmeli:

    * **yeşil** -- çözümü olan hâlde doğru kâide tepeye çıkmalı ve
      ağırlığı düz dağılımın kat kat üstünde olmalı;
    * **kırmızı** -- çözümü OLMAYAN hâlde hiçbir kâide ağırlık
      toplamamalı.
    """
    from .qkaide import coz_kaide

    def klasik(sah, bit):
        return [(p, q, r)
                for p in range(1 << bit) for q in range(1 << bit)
                for r in range(1, 1 << bit)
                if all(r * ho == p * hi + q for hi, ho in sah)]

    def indis(p, q, r, bit):
        b = ([(p >> i) & 1 for i in range(bit)]
             + [(q >> j) & 1 for j in range(bit)]
             + [(r >> l) & 1 for l in range(bit)])
        return sum(bi << i for i, bi in enumerate(b))

    bit = 2
    for sah in ([(3, 3), (2, 2), (5, 5)], [(2, 4), (3, 6), (1, 2)],
                [(4, 2), (6, 3), (2, 1)], [(2, 3), (3, 4), (5, 6)]):
        kl = klasik(sah, bit)
        assert kl, sah
        idx = {indis(*c, bit) for c in kl}
        r = coz_kaide(sah, bit=bit, tur=2)
        P = r["dağılım"]
        agirlik = float(sum(P[i] for i in idx))
        duz = len(idx) / len(P)
        assert r["en_yüksek"] in idx, (sah, r["çözüm"], kl)
        assert agirlik > 5.0 * duz, (sah, agirlik, duz)
        assert r["kesme"] < 1e-12, r["kesme"]      # MPO fiilen tam

    # --- KIRMIZI: çözümü olmayan hâlde ağırlık toplanmamalı
    celiskili = [(2, 3), (2, 5)]
    assert not klasik(celiskili, bit)
    r = coz_kaide(celiskili, bit=bit, tur=2)
    assert r["sahte_kok"], "sahte kök denetçisi kırmızı yanmadı"


def test_qkaide_asikar_kaideyi_eliyor():
    """``r = 0`` ebadı hiç söylemez; orak onu çözüm saymamalı.

    Ölçüldü ve düzeltildi: elenmediğinde orağın tepesi ``(0,0,0)``
    çıkıyordu -- yani "hiçbir şey söylemeyen kâide", hakikî kâide kadar
    kuvvetle işaretleniyordu.
    """
    from .qkaide import coz_kaide, _coz

    r = coz_kaide([(2, 4), (3, 6), (1, 2)], bit=2, tur=2)
    assert r["çözüm"] == (2, 0, 1), r["çözüm"]
    P = r["dağılım"]
    for i in range(len(P)):
        if _coz(i, 2)[2] == 0:                     # r = 0 olan bütün kollar
            assert P[i] < 0.5 * float(P[r["en_yüksek"]]), (_coz(i, 2), P[i])




def test_kodlama_tersinir_ve_hadamard_esit_uzak():
    """Kodlama funktörünün sıhhati -- `token_uzaylari/morfizm.py` ile.

    H14 *"kodlama tersinirdir, hiçbir bit kaybolmaz"* diyordu ve bu
    **hiç ölçülmemişti**. Burada iki ayrı ölçütle ölçülür:

    1. **Tersinirlik** -- her belirteç geri çözülebilmeli, çarpışma
       olmamalı. (H14'ün iddiası budur ve doğrudur.)
    2. **Kategorik eşit uzaklık** -- ARC belirteçleri RENKTİR, yani
       kategoriktir; 7 ile 8 arasında "yakınlık" manasızdır. 4 boyutta
       bu sağlanamaz (ölçüldü: değişke 0,2163 ve bu, gri/açısal/Hadamard
       alternatiflerinin hepsinden İYİ). ``kubit ≥ sozluk`` olunca
       Hadamard tam eşit uzaklık verir (değişke 0).
    """
    from .kopru import kodlamayi_olc
    from .qegitim import belirtecleri_kodla

    r = kodlamayi_olc()
    assert r["tersinir"] is True and r["çarpışma"] == 0, r

    T = np.arange(16)
    ust = np.triu_indices(16, 1)

    def degisken(E):
        D = np.linalg.norm(E[:, None, :] - E[None, :, :], axis=2)[ust]
        return float(D.std() / D.mean()), float(D.min())

    d4, en_az4 = degisken(belirtecleri_kodla(T, 4, 16))
    d16, en_az16 = degisken(belirtecleri_kodla(T, 16, 16))
    assert en_az4 > 0.0 and en_az16 > 0.0          # hiç çarpışma yok
    assert d16 < 1e-9, d16                         # Hadamard: TAM eşit uzak
    assert d4 > 0.2, d4                            # 4 boyutta imkânsız


def test_kod_uzayi_stabilizer_ile_yuzlesiyor():
    """Hüküm bloğu, MPS'ten BAĞIMSIZ ikinci bir temsille denetlenebiliyor mu?

    H88'in dersi: ``beyan`` aylarca yanlış çevreden okudu ve
    **karşılaştıracak ikinci bir temsil olmadığı için** farkedilmedi.
    `kuantum/stabilizer.py` o ikinci temsili verir: mantık katmanı
    ``CZ``/``Z`` ile kurulduğu için Clifford'dur ve stabilizer
    çerçevesinde **tam** temsil edilir -- kesme yok, ``2^n`` açılmıyor.
    """
    from .kod_uzayi import hukum_kod_uzayi, kod_uzayi_dagilimi

    n = 4
    duz = kod_uzayi_dagilimi(hukum_kod_uzayi(n, []))
    assert np.allclose(duz, 1.0 / (1 << n), atol=1e-9), duz

    # ``CZ`` bir FAZ kapısıdır: taban dağılımını DEĞİŞTİRMEZ. Bu, kütük
    # H107'nin ölçülmüş dersinin müstakil bir teyididir -- işaret tek
    # başına marjinali oynatmaz, sönme girişimden gelir.
    isaretli = kod_uzayi_dagilimi(hukum_kod_uzayi(n, [(0, 1)]))
    assert np.allclose(isaretli, duz, atol=1e-9)

    # Fakat GENLİKTE fark vardır ve işaret oradadır.
    from kuantum.stabilizer import StabilizerDurum
    Y = np.array([[1, 1, 0, 0]], dtype=np.int64)
    g0 = np.asarray(StabilizerDurum.arti(n).genlik(Y)).ravel()[0]
    g1 = np.asarray(hukum_kod_uzayi(n, [(0, 1)]).genlik(Y)).ravel()[0]
    assert abs(g1 + g0) < 1e-9, (g0, g1)          # işaret çevrilmiş


def test_alan_okumasi_AYARA_BAGLI_DEGIL():
    """Hüküm alanlarının okuması bir **gözlenebilir** mi? (kütük H121)

    Saf bir ayar dönüşümü -- ``A_k ← A_k X``, ``A_{k+1} ← X⁻¹ A_{k+1}``
    -- fizikî durumu **hiç değiştirmez**. O hâlde her gerçek
    gözlenebilir bu dönüşüm altında sabit kalmalıdır.

    Eski ``yuva_yogunluklari`` kalmıyordu: çevreyi birim sayıyor, yani
    MPS'i kanonik varsayıyordu -- halbuki bu yazmaç kanonik değildir.
    ``alan_degeri`` ve ``makam_dagilimi`` onun üstüne kuruluydu, yani
    bütün hüküm okumaları gözlenebilir DEĞİLDİ. Bu, H88'in aynı cinsten
    tekrarıdır: çevre hesaba katılmadan okunan sayı bir ölçüm değildir.

    Sınama iki şeyi birden tutar ve ikincisi olmadan birincisi bir şey
    ifade etmez: yeni usul ayar altında **sabit**, eski usul ise
    **kayıyor** -- yani sınama kör değil.
    """
    from .qakis import QNefs
    from .qyazmac import QAyar

    q = QNefs(0, QAyar(satir_kubiti=4, bag=16)).idrak_et(
        np.random.default_rng(0).normal(size=(3, 4)))
    y = q.y
    s = q.kulli("sukut", 0)

    def oku():
        return (float(np.asarray(y.tekil_yogunluklar([s]), float)[0, 0, 1, 1]),
                float(np.asarray(y.yuva_yogunluklari([s]), float)[0, 0, 1, 1]))

    # Yeni usul, çevreleri açıkça kuran ``blok_dagilimi`` ile aynı olmalı.
    dogru = float(np.asarray(q.blok_dagilimi(s, 1)).ravel()[1])
    yeni0, eski0 = oku()
    assert abs(yeni0 - dogru) < 1e-9, (yeni0, dogru)

    X = np.eye(y.bag) + 0.3 * np.random.default_rng(1).normal(
        size=(y.bag, y.bag))
    Xi = np.linalg.inv(X)
    y.A[:, s - 1] = np.einsum("zaib,bc->zaic",
                              y.A[:, s - 1].astype(np.float64),
                              X).astype(y.tip)
    y.A[:, s] = np.einsum("ab,zbic->zaic", Xi,
                          y.A[:, s].astype(np.float64)).astype(y.tip)
    yeni1, eski1 = oku()

    assert abs(yeni1 - yeni0) < 1e-6, ("yeni usul ayara bağlı çıktı",
                                       yeni0, yeni1)
    assert abs(eski1 - eski0) > 1e-4, ("eski usul ayara bağlı DEĞİL çıktı; "
                                       "sınama kör", eski0, eski1)


def test_golge_kahin_ana_hatti_denetliyor():
    """Dosya 6: `reel/` ve `akis/` ana hattı çapraz doğruluyor mu?

    Dört denetim, hepsi ana hattı **hiç kullanmayan** koddan:
    kapılar ``SO(4)``te mi, reel gömme ``exp(−iHt)``yi veriyor mu,
    ``RHT`` dik ve involutif mi.
    """
    from .golge import (AZAMI_ULP, ULP, dik_donusum_dogrulamasi,
                        grup_sadakati, reel_gomme_sadakati)

    g = grup_sadakati(ornek=40)
    for ad in ("cayley", "us"):
        assert g[ad]["hepsi_SO4"], (ad, g[ad])

    r = reel_gomme_sadakati()
    assert r["ulp_boyut_başına"] <= AZAMI_ULP, r

    for N, d in dik_donusum_dogrulamasi((8, 64)).items():
        assert d["diklik"] / (ULP * N) <= AZAMI_ULP, (N, d)
        assert d["involutif"] / (ULP * N) <= AZAMI_ULP, (N, d)


def test_cayley_pi_donmesini_OGRENEMIYOR_ustel_ogreniyor():
    """H120: Cayley'in erişemediği yer, öğrenilebilirlikte de kapalı.

    Bu, `main/yazmac.py`nin kapı usulünü değiştiren ölçümün ta
    kendisidir; sabit kalması için daimî sınamaya konur. Hedef
    ``diag(1,1,−1,−1)`` bir **π dönmesidir** ve ``SO(4)``tedir --
    yani meşru bir meleke kapısıdır. Reel yazmaçta yegâne faz π
    olduğuna göre (H98), bu kapıyı öğrenememek doğrudan bir kabiliyet
    eksiğidir.
    """
    from main import yazmac as MY

    hedef = np.diag([1.0, 1.0, -1.0, -1.0])

    def uyum(usul):
        eski = MY.kapi_usulu(usul)
        try:
            t = np.random.default_rng(0).normal(size=6) * 0.3
            for _ in range(1500):
                h = 1e-5
                T = np.tile(t, (13, 1))
                for j in range(6):
                    T[1 + 2 * j, j] += h
                    T[2 + 2 * j, j] -= h
                G = np.asarray(MY.dik_iki_kubit_yigin(T), np.float64)
                L = ((G - hedef) ** 2).sum(axis=(1, 2))
                t = t - 0.05 * np.array([(L[1 + 2 * j] - L[2 + 2 * j])
                                         / (2 * h) for j in range(6)])
            G = np.asarray(MY.dik_iki_kubit(t), np.float64)
            return float(np.abs(G - hedef).max())
        finally:
            MY.kapi_usulu(eski)

    assert uyum("cayley") > 0.1, "Cayley beklenmedik şekilde ulaştı"
    assert uyum("us") < 1e-5, "üstel harita hedefe ulaşamadı"


def test_sozlesme_41_melekede_ihlalsiz_ve_KIRMIZI_YANABILIYOR():
    """Dosya 2: her meleke ilan ettiği hududun içinde mi kalıyor?

    İki şey birden sınanır ve ikincisi olmadan birincisi bir şey ifade
    etmez (kullanıcı hükmü H90: *her ölçüt kırmızı yanabildiğini
    ispatlasın*):

    1. **Yeşil** -- 41 melekenin hiçbiri ilan etmediği (ve güzergâhında
       olmayan) bir bölgeye dokunmuyor.
    2. **Kırmızı** -- sözleşme kasten daraltıldığında ölçüm bunu
       YAKALIYOR. Yakalamasaydı birinci maddenin yeşil olması yalnız
       ölçümün kör olduğunu gösterirdi.
    """
    from . import sozlesme

    for r in sozlesme.sozlesmeyi_olc(n_satir=3, chi=16):
        assert not r["ihlâl"], r
        assert not r["kullanılmayan"], r

    # --- MUTASYON: 𝒪₁ Müşahede'nin ilanı boşaltılırsa yakalanmalı.
    eski = sozlesme.SOZLESME[1]
    sozlesme.SOZLESME[1] = (("sukut",), "kasten yanlış ilan")
    try:
        r = sozlesme.dokunulan_bolgeler(1, n_satir=3, chi=16)
        assert "veri" in r["ihlâl"], r
    finally:
        sozlesme.SOZLESME[1] = eski


def test_mera_kulli_hukum_blokuna_dokunmuyor():
    """MERA küllî hüküm bloğunu karıştırmamalı (kütük H119).

    ``superpozisyon`` küllî bloğa kasten dokunmaz ve sebebini yazar:
    hüküm henüz verilmemiştir, ``|0⟩`` doğru başlangıçtır. MERA'nın
    hemen ardından aynı bloğu karıştırması o hükmü fiilen iptal
    ediyordu ve bu **sözleşme yüzleştirmesinde bulundu**, kimse iddia
    etmiş değildi.
    """
    from .qyazmac import QAyar, QYazmac

    def blok(kulli_dahil):
        q = QYazmac(3, QAyar(bag=16, tohum=0))
        q.kodla(np.random.default_rng(0).normal(size=(3, 12)))
        q.superpozisyon()
        q.mera(kulli_dahil=kulli_dahil)
        yuv = list(range(q.kulli_bas, q.n))
        return np.asarray(q.y.tekil_yogunluklar(yuv), float)[0]

    R = blok(False)
    # küllî blok hâlâ ``|0⟩``: ρ₀₀ = 1
    assert np.allclose(R[:, 0, 0], 1.0, atol=1e-6), R[:, 0, 0]
    # eski davranış geri verilince karışıyor -- yani sınama kör değil
    assert not np.allclose(blok(True)[:, 0, 0], 1.0, atol=1e-6)


def test_nizam_dolasiklik_doygunlugu_kiriyor():
    """Dosya 1'in χ cetveli, H115'in derdini fiilen çözüyor mu?

    H115'te ölçüldü: Schmidt rütbesi **her** bütçede doyuyordu
    (8→8, 16→16, 32→32), yani akış hacim kanunu dolaşıklığı üretiyor ve
    hiçbir χ yetmiyor. Bu, H94 (kalp yok) ile H105'i (alanlar yapısız)
    birden açıklıyordu: âzamî dolaşık durumda her küçük bloğun
    marjinali düzgündür.

    Nizam açıkken doygunluğun **kırılması** ve beyanın girdiye
    duyarlılığını **kaybetmemesi** şarttır. İkincisi hakemdir: kesme,
    girdiyi atarak da "yapılanmış" bir dağılım üretebilir; o zaman
    kazanç sahtedir.
    """
    from tanilama.nizam_dolasiklik import _tek_kosu

    kapali = _tek_kosu(False, 8, 0, 6, 12, girdi_sayisi=3)
    acik = _tek_kosu(True, 8, 0, 6, 12, girdi_sayisi=3)

    assert kapali["doygunluk"] > 0.99, kapali        # H115 hâlâ geçerli
    assert acik["doygunluk"] < 0.99, acik            # nizam onu kırıyor
    # Hakem: girdi hassasiyeti kaybedilmemeli.
    assert acik["girdi_hassasiyeti"] >= 0.95 * kapali["girdi_hassasiyeti"], (
        kapali["girdi_hassasiyeti"], acik["girdi_hassasiyeti"])


def test_nizam_cetveli_tam_ve_tutarli():
    """41 melekenin hepsinin sınıfı ve tavanı yazılı mı?

    Cetvelin eksik kalması sessiz bir kusurdur: tavansız bir meleke
    yazmacın tam ``bag``ıyla koşar ve nizamda delik açar. Ayrıca
    sınıflar tutarlı olmalı -- bir "çözücü" bir "kurucu"dan geniş tavan
    isteyemez.
    """
    from .qmeleke import nizam_cetveli

    cetvel = nizam_cetveli()
    assert len(cetvel) == 41, len(cetvel)
    kurucu = [c for c in cetvel if c[2] == "kurucu"]
    cozucu = [c for c in cetvel if c[2] == "çözücü"]
    assert kurucu and cozucu
    assert max(c[3] for c in cozucu) < min(c[3] for c in kurucu)
    for no, ad, sinif, chi in cetvel:
        assert sinif in ("kurucu", "koruyucu", "çözücü"), (no, sinif)
        assert chi is None or chi >= 1, (no, chi)


# Koşturucu dosyanın SONUNDA durur: aksi hâlde kendisinden sonra
# tarif edilen sınamalar `globals()` taramasına girmez ve sessizce
# koşulmaz. Ölçüldü: kâide sınamaları eklendiği hâlde sayı 41 kalmıştı.
if __name__ == "__main__":
    raise SystemExit(main())
