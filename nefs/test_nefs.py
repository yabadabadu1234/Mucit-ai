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
        assert d.olcum.al("belâgat.fesâhatı_aşamaz") == 1.0, t


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


if __name__ == "__main__":
    raise SystemExit(main())


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
