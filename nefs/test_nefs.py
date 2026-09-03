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

from . import melekeler as akil
from . import melekeler as beyan
from . import melekeler as idrak
from . import melekeler as murakabe
from .melekeler import AKIS, KULLI_SIRA, Nefs, sira_gecerli_mi
from .melekeler import melekeler, sicil
from .melekeler import Durum, Parametreler, ehlilestir, tevafuk, devirler


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
    assert d.makam in ("Yakîn", "Zann-ı gālib", "Zan", "Şek", "Vehim")
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
           "from nefs.melekeler import Nefs;"
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

    assert devirler("betti", A(4, [])) == (4, 0)                    # 4 nokta
    assert devirler("betti", A(4, [(0, 1), (1, 2), (2, 3)])) == (1, 0)   # yol
    assert devirler("betti", A(4, [(0, 1), (1, 2), (2, 3), (3, 0)])) == (1, 1)  # çevrim
    assert devirler("betti", A(6, [(0, 1), (1, 2), (2, 0),
                                      (3, 4), (4, 5), (5, 3)])) == (2, 2)  # iki üçgen


def test_normalize_laplasyen():
    A = np.array([[0., 1., 0.], [1., 0., 1.], [0., 1., 0.]])
    L = devirler("laplasyen", A)
    assert np.allclose(np.diag(L), 1.0)
    oz = np.linalg.eigvalsh(L)
    assert oz.min() > -1e-9 and oz.max() < 2 + 1e-9   # spektrum [0,2]
    assert abs(oz.min()) < 1e-9                        # bağlantılı → 0 özdeğeri


def test_asiklik_olcutu():
    """``h(A) = Tr(exp(A∘A)) − d``: DAG'da tam 0, devirde pozitif."""
    dag = np.array([[0., .8, .5], [0., 0., .7], [0., 0., 0.]])
    assert abs(devirler("ihlâl", dag)) < 1e-12
    devir = dag.copy()
    devir[2, 0] = 0.6
    assert devirler("ihlâl", devir) > 1e-6


def test_illet_kesfi_dag_uretiyor():
    d = Nefs(0).idrak_et(_E(0))
    assert d.A_neden is not None
    assert abs(devirler("ihlâl", d.A_neden)) < 1e-9
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
    h0 = tevafuk("çekirdek", x, bagimsiz)
    h1 = tevafuk("çekirdek", x, bagimli)
    assert h0 < 0.002, h0
    assert h1 > 5 * h0, (h0, h1)


def test_tenakuz_kendisiyle_celismiyor():
    """Ters simetrik çekirdek ⟹ ``SᵢᵀWSᵢ = 0``: hiçbir önerme kendisiyle
    çelişmez."""
    d = Nefs(0).idrak_et(_E(0))
    assert d.olcum.al("tenakuz.köşegen") < 1e-9


def test_makam_parcalanisi_tam_ve_ayrik():
    """**Beş** makam ``[0,1]``i TAM ve AYRIK örter (H158).

    Evvelce dörttü ve ``0,5+ε``–``1−ε`` arasının tamamı ``Zan``dı;
    mîzânın cetvelindeki ``zann-ı gālib`` (0,75) yoktu. Eksik zararsız
    değildi: ARC'nin istikrâ yakîni ortalaması 0,8025, yani **her
    görev** tam o mertebeye düşüyor ve model hepsine "Zan" diyerek
    kendi delilinin kuvvetini eksik beyan ediyordu.
    """
    beklenen = {"Yakîn", "Zann-ı gālib", "Zan", "Şek", "Vehim"}
    gorulen = set()
    for P in np.linspace(0.0, 1.0, 20001):
        m = murakabe.makam_tayin(float(P))
        assert m in beklenen, (P, m)
        gorulen.add(m)
    assert gorulen == beklenen, gorulen
    # sınırlar: monotonluk (P büyüdükçe makam gerilemez)
    duzen = {"Vehim": 0, "Şek": 1, "Zan": 2, "Zann-ı gālib": 3, "Yakîn": 4}
    dizi = [duzen[murakabe.makam_tayin(float(P))]
            for P in np.linspace(0, 1, 5001)]
    assert all(dizi[i] <= dizi[i + 1] for i in range(len(dizi) - 1))
    # Eşik mîzânın cetvelinden gelmeli, elle konmuş olmamalı.
    from mizan.munazara import MERTEBELER
    assert murakabe.ZANN_I_GALIB_ESIGI in [e for e, _ in MERTEBELER]
    # Ve ARC'nin fiilen düştüğü derece artık kendi adını alıyor.
    assert murakabe.makam_tayin(0.8025) == "Zann-ı gālib"


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
    assert abs(tevafuk("ayna", simetrik) - 1.0) < 1e-12
    assert abs(tevafuk("ayna", ters_simetrik) - 0.0) < 1e-12
    h = tevafuk("ayna", A)
    assert 0.0 <= h <= 1.0
    # ölçek değişmezliği
    assert abs(tevafuk("ayna", 1000 * A) - h) < 1e-9


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
    from nefs.melekeler import kan_temeli

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
    import nefs.melekeler as idrak
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
    from main.cikarim import padisah

    class _Gorev:
        def __init__(self, egitim, sinama):
            self.ad = "sınama"
            self.egitim = egitim
            self.sinama = sinama

    rng = np.random.default_rng(0)
    sahit = []
    for _ in range(4):
        g = rng.integers(0, 5, size=(3, 4))
        sahit.append((g, g.T.copy()))
    sin_g = rng.integers(0, 5, size=(3, 4))

    # --- YEŞİL: devrik görevi, ŞABLON OLMADAN çözülmeli
    r = padisah(_Gorev(sahit, [(sin_g, sin_g.T.copy())]), devir=200)
    assert not r["sükût"], r.get("sebep")
    assert np.array_equal(r["cevap"][0], sin_g.T), r["cevap"][0]
    assert r["d4"] == "devrik", r["d4"]
    assert r["şahit_isabeti"] == 1.0, r["şahit_isabeti"]
    # cevap bir tablodan değil AĞIRLIKTAN geldi
    assert r["ağırlık"] > 0

    # --- KIRMIZI: bir şahidi boz, padişah SUSMALI
    bozuk = list(sahit)
    bozuk[2] = (bozuk[2][0], rng.integers(0, 5, size=(4, 3)))
    r2 = padisah(_Gorev(bozuk, [(sin_g, sin_g.T.copy())]), devir=200)
    assert r2["sükût"], \
        "bozuk şahitle hâlâ konuşuyor — ölçüt kırmızı yanamıyor"


def test_kaide_eksik_istikra_yakin_vermez():
    """``tam_istikra_mi``nin hükmü mîzânda fiilen işliyor mu?

    Rakibi elenmemiş bir kâide, BÜTÜN misallerde tutsa bile **Yakîn'e
    çıkmamalı**. Yakîn istikrâdan değil **tekliğin ispatından** gelir.
    Burada girdi kare seçilir; o zaman ``aynı`` ile ``devrik`` ebatta
    ayırt edilemez ve teklik ispatlanamaz.

    **ŞART DARALTILDI, GEVŞETİLMEDİ (kütük H161).** Evvelce
    ``makam == "Zan"`` yazıyordu; H161'de beşinci mertebe (``zann-ı
    gālib``) makama girince bu hâl oraya çıktı -- derece 0,833 ve
    rükünlerin ikisi ispatlanmış. Sınamanın **maksadı** o değildi:
    maksat *"eksik istikrâ Yakîn vermez"*tir ve o şart aynen duruyor.
    Belli bir mertebe adını şart koşmak, sınanan hükmü değil onun bir
    tesadüfünü şart koşmak olurdu.

    Gevşetme olmadığının şahidi aşağıdadır: mertebenin **Yakîn'in
    altında** ve ``Şek``in **üstünde** olduğu ayrıca sınanır, yani
    aralık iki taraftan da kapalıdır.
    """
    from main.cikarim import hendese_adaylari
    from mizan.istikra import tam_istikra_mi

    assert not tam_istikra_mi(50, 50)       # eksik istikrâ 1 vermez

    rng = np.random.default_rng(1)
    kare = []
    for _ in range(4):
        g = rng.integers(0, 5, size=(3, 3))   # KARE → ebat kanunu belirsiz
        kare.append((g, g.copy()))
    adaylar = hendese_adaylari(kare)
    # ASIL ŞART: şahitler kanunu TAYİN ETMİYORSA teklik iddia edilemez.
    # Kare girdide ``H→H``, ``H→W`` ve ``H→3`` şahitlerde ayırt edilemez.
    assert len(adaylar) > 1, [str(h) for h in adaylar]
    for h in adaylar:                       # hepsi şahitleri TAM tutuyor
        for g, c in kare:
            assert h.ebat(g.shape) == c.shape, (str(h), g.shape)

    # ...ve iki taraftan kapalı: ebat DEĞİŞEN şahitler kanunu tayin
    # edince rakip kalmamalı. Yalnız "birden çok aday var" denseydi,
    # ölçü hiçbir zaman yeşil yanamazdı.
    ayrik = []
    for h, w in ((2, 5), (3, 4), (6, 2)):
        g = rng.integers(0, 5, size=(h, w))
        ayrik.append((g, g.copy()))
    tek = hendese_adaylari(ayrik)
    assert len(tek) == 1, [str(x) for x in tek]
    assert str(tek[0]) == "H→H, W→W", str(tek[0])




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


def test_iki_olcek_hakikaten_iki():
    """Dosya 5: sağîr ölçek, kebîrin zaten bildiğini mi söylüyor?

    İki ölçekli mimarinin bedeli vardır; kazancı ispatlanmalıdır.
    Ölçüt Grassmann asal açılarıdır ve **kırmızı yanabilir**: açılar
    sıfıra yakın çıksaydı ikinci ölçek gereksiz demekti.
    """
    from idrak import arc

    from .iki_olcek import olcek_acilari, sagir_uydur

    g = arc.yukle_hepsi("training")[:10]
    artiklar = []
    for gv in g:
        r = sagir_uydur(gv)
        assert r.get("kuruldu"), r
        assert r["psd"], ("çekirdek PSD değil -- temsil teoremi geçersiz", r)
        artiklar.append(r["azamî_artık"])
    # **Şart ORTANCAYA konur ve sebebi ölçüldü.** Her görevde artık
    # sıfıra inmez: 14 sayılık kaba tarif bazı görevlerde iki ayrı
    # çiftte AYNI çıkar, Gram dizeyi tekilleşir (koşul ~5e6) ve kapalı
    # form enterpolasyon yerine ortalamaya düşer. Bu `ogrenme/rkhs.py`nin
    # kusuru değil benim tarifimin kusurudur ve borç olarak durur;
    # sınamayı her göreve zorlamak, o borcu ölçütle örtmek olurdu.
    assert float(np.median(artiklar)) < 1e-2, artiklar

    o = olcek_acilari(g)
    assert o["yeterli_mi"], o
    assert o["azamî_açı"] > 0.1, ("iki ölçek aynı alt uzayı geriyor", o)


def test_cech_tikanikligi_sukutu_ARTIRIYOR():
    """Dosya 3: ``H¹ ≠ 0`` olan görevde model susuyor mu? (kütük H125)

    Tıkanıklık "cevap yanlış" değil, "bu örtüde küllî cevap YOK"
    demektir; doğru karşılık susmaktır (H10/H16).

    **Ölçüt kör değildir:** kapı kapalıyken bağ menfî çıkıyordu (model
    tıkanıkta daha ÇOK konuşuyordu). İki koşu da sınanır ki düzeltmenin
    fiilen bir şey değiştirdiği görülsün.
    """
    from .operad import cech_tikanikligi, tikaniklik_sukut_bagi

    kapali = tikaniklik_sukut_bagi(60, kapi=False)
    acik = tikaniklik_sukut_bagi(60, kapi=True)
    assert kapali["yeterli_mi"] and acik["yeterli_mi"]
    assert acik["korelasyon"] > 0.15, acik
    assert acik["sukut_tıkanıkta"] > kapali["sukut_tıkanıkta"], (kapali, acik)

    # Kozikıl şartı: ikili uyuşma denklik kurduğu için üçlüler tutmalı.
    from idrak import arc
    for gv in arc.yukle_hepsi("training")[:40]:
        c = cech_tikanikligi(gv)
        assert c["üçlü_tutarlı"], (gv, c)


def test_makam_kodlamasi_epistemik_komsulugu_koruyor():
    """Makam merdiveni tek kübitlik dönmeyle gezilebiliyor mu? (H127/H158)

    `mizan/munazara.py` epistemik sırayı veriyor: ``vehim < şek < zan <
    zann-ı gālib < yakîn``. İki şart:

    1. Ardışık iki basamak arasındaki Hamming mesafesi 1 olmalı, yoksa
       𝒪₃₂'nin tek kübitlik kontrollü dönmeleri o geçişi yapamaz.
    2. Beş mertebenin **hepsi** bir basamağa düşmeli. İki kübitte
       düşmüyordu: ``zann-ı gālib`` temsil edilemiyordu (H129).

    **Ölçüt kör değildir:** eski sıra da, iki kübitlik yazmaç da
    sınanır ve ikisinin de kırmızı yandığı gösterilir.
    """
    from .mantik import ESKI_SIRA, GRAY_SIRA, eksik_mertebeler, \
        komsuluk_denetimi
    from .zihin_durumu import MAKAM_ADLARI, makam_kubit_manasi, makam_merdiveni

    y = komsuluk_denetimi()                     # yürürlükteki yazmaç
    assert y["kırık_geçiş"] == 0, y
    assert y["monoton"], y                      # yukarı çıkmak düşürmemeli
    assert y["kol_tutarlı"], y                  # makam₀=1 → üst yarı
    assert y["mertebe_sayısı"] == len(MAKAM_ADLARI) == 5, y
    assert y["basamak"] == 8, y

    # Eski sıra kırmızı yanmalı -- yoksa sınama bir şey ispat etmez.
    e = komsuluk_denetimi(ESKI_SIRA, 2)
    assert e["kırık_geçiş"] == 2 and not e["kol_tutarlı"], e
    # H127'nin iki kübitlik tashihi komşuluğu düzeltmişti ama beşinci
    # mertebeyi getirememişti; ikisi ayrı kusurdur ve ayrı sınanır.
    g = komsuluk_denetimi(GRAY_SIRA, 2)
    assert g["kırık_geçiş"] == 0 and g["kol_tutarlı"], g
    assert g["mertebe_sayısı"] == 4, g

    # H129'un borcu KAPANDI: yürürlükteki yazmaçta eksik mertebe yok.
    assert eksik_mertebeler() == [], eksik_mertebeler()
    # ...ve ölçüt kör değil: iki kübitte hâlâ eksik çıkıyor.
    assert [ad for _, ad in eksik_mertebeler(2)] == ["zann-ı gālib"]

    # Kübitlerin manası ŞERHTE DEĞİL, hesapta: makam₀ üst yarı,
    # makam₁ orta dörtlü, makam₂ ara basamaklar.
    man = makam_kubit_manasi(3)
    assert man[0] == (4, 5, 6, 7), man
    assert man[1] == (2, 3, 4, 5), man
    assert man[2] == (1, 2, 5, 6), man
    m = makam_merdiveni(3)
    assert all(bin(m[i] ^ m[i + 1]).count("1") == 1
               for i in range(len(m) - 1)), m


def test_padisahin_eli_HER_MODULE_uzaniyor():
    """Beylik kalmadı mı? (kütük H123)

    Bu sınama divanın **çürümesini** engeller: yeni bir modül eklenip
    divana yazılmazsa `tanilama/nizam.py` onu beylik sayar ve burası
    kırmızı yanar. Yani divan bir kere doldurulup unutulacak bir liste
    değil, **korunan** bir nizamdır.

    Ölçüt divanın kendi sayımı DEĞİLDİR -- o kendi kendini onaylardı.
    Ölçüt, divanı hiç tanımayan `tanilama/nizam.py`nin ``ast`` ile
    yaptığı bağımsız erişilebilirlik hesabıdır.
    """
    from tanilama.nizam import (GIRISLER, modulleri_tara, padisahin_eli,
                                tabiiyet)

    tab = tabiiyet(modulleri_tara())
    tebaa = padisahin_eli(GIRISLER, tab)
    beylik = sorted(set(tab) - set(tebaa))
    assert not beylik, ("padişaha bağlanmamış modül var: %s" % beylik[:20])


def test_gaye_alani_ARTIK_YASIYOR_ve_sukutu_bastiriyor():
    """Dosya 4: `gaye` alanı yazılıyor ve sükût eşiği çalışıyor mu?

    H108 gaye'nin "hükümle dolaştırıldığını" söylüyordu; ölçüldü ve
    alan tam ``|0⟩``daydı -- hiç yazılmamıştı (kütük H122). Burada iki
    şey sınanır:

    1. Gaye kapalıyken alan ``|0⟩``, açıkken **değil** -- yani sınama
       kör değil, kapatınca kırmızı yanıyor.
    2. Gaye girdiye göre **değişiyor** -- yani sabit bir süs değil.

    **İki şey kasten sınanmıyor ve sebebi ölçümdür.** Bir borcu
    sınamayla örtmek, örtmenin en kötü şeklidir:

    * *Nakzın gayeyi zayıflatması* icra edilemedi -- korelasyon
      ``+0,89``da kaldı (bkz. `nefs/gaye.py`).
    * *``ε_durgun`` sükûtu bastırması* **kararlı değil**: gaye-sükût
      korelasyonu satır sayısına göre ``+0,63 / −0,89 / +0,46``
      arasında zıplıyor. Yani tesir gürültünün üstünde değil. Bir
      tohumda menfî çıkanı seçip "çalışıyor" demek, ölçümü hükme
      uydurmak olurdu.

    İkisi de kütükte borç olarak durur (H122).
    """
    from .melekeler import QNefs
    from .zihin_durumu import QAyar

    def kos(acik, tohum):
        E = np.random.default_rng(200 + tohum).normal(size=(5, 12))
        q = QNefs(0, QAyar(bag=16, tohum=0), gaye=acik).idrak_et(E)
        d = {}
        for ad in ("gaye", "sukut"):
            _, kac = q._alan[ad]
            R = np.asarray(q.y.tekil_yogunluklar(
                [q.kulli(ad, j) for j in range(kac)]), float)[0]
            d[ad] = float(R[:, 1, 1].mean())
        return d

    kapali = kos(False, 0)
    assert kapali["gaye"] < 1e-6, ("gaye kapalıyken yazılmamalı", kapali)

    g, s = [], []
    for t in range(6):
        r = kos(True, t)
        g.append(r["gaye"])
        s.append(r["sukut"])
    assert max(g) > 1e-3, ("gaye açıkken alan hâlâ ölü", g)
    # Sabit bir süs değil: girdiye göre gerçekten değişiyor.
    assert float(np.std(g)) > 1e-3, ("gaye girdiye göre değişmiyor", g)


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
    from .melekeler import QNefs
    from .zihin_durumu import QAyar

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

    Bu, `kuantum/yazmac.py`nin kapı usulünü değiştiren ölçümün ta
    kendisidir; sabit kalması için daimî sınamaya konur. Hedef
    ``diag(1,1,−1,−1)`` bir **π dönmesidir** ve ``SO(4)``tedir --
    yani meşru bir meleke kapısıdır. Reel yazmaçta yegâne faz π
    olduğuna göre (H98), bu kapıyı öğrenememek doğrudan bir kabiliyet
    eksiğidir.
    """
    from kuantum import yazmac as MY

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
    from .zihin_durumu import QAyar, QYazmac

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
    """41 melekenin hepsinin sınıfı yazılı mı, ve sınıf **ölçülüyor** mu?

    Bu sınamanın evvelki hâli şunu iddia ediyordu::

        max(çözücü tavanı) < min(kurucu tavanı)

    yani "çözücülük dar bir χ tavanıyla temin edilir". **H149'da bu
    nakzedildi:** ölçüldü ki 𝒪₂₄'ün tavanı 1'di ve dalganın
    ``8,7e-12``sini bırakıyordu; tavan kalkınca ``0,548`` kalıyor ve
    entropi yine ``ln 4``e düşüyordu. Yani daralmanın manası **kapının
    kendisinde**, üniter olarak vardı; tavan yalnız genliği yok
    ediyordu. Dar tavan çözücülük değil, sakatlamaymış.

    O hâlde tavan sırası bir taahhüt olamaz. Yerine geçen taahhüt
    (H149 + `nefs/nizam.py`) **ölçülebilir** olandır: sınıf, melekenin
    dolaşıklığa tesirinin **cihetini** taahhüt eder ve bu ``ΔS`` ile
    yüzleştirilir. Burada denetlenen üç şeydir:

    1. cetvel tam ve sınıflar mâlûm kümeden;
    2. ilân edilen her sınıfın bir cihet karşılığı var (yoksa taahhüt
       ölçüsüz kalır, tam da H88'in kusuru);
    3. ölçü **kör değil**: taahhüt edilen bölgede sıfır, dışında
       müsbet -- ve bilhassa ``ΔS = 0`` hiçbir sınıfı kurtarmaz. Bu
       son şart H157'nin dersidir: ilk yazdığımda ölçüt yalnız
       *işarete* bakıyordu, sıfır da hiçbir cihete ters düşmediği için
       hiç çözmeyen 𝒪₅ Tecrit tam not alıyordu.
    """
    from .nizam import NIZAM_BANDI, SINIF_CIHETI, sinif_ihlali
    from .melekeler import nizam_cetveli

    cetvel = nizam_cetveli()
    # **41 → 44 (kütük H213).** `nefs/dimag.py` ``MELEKE_SAYISI = 44``
    # diyor ve ``KANONIK_CETVEL`` 𝒪₄₂/𝒪₄₃/𝒪₄₄'ü ``d₁₀``a tescil
    # ediyordu; akış ise 41'de bitiyordu. Üçü ``QAKIS``a girdi.
    assert len(cetvel) == 44, len(cetvel)
    kurucu = [c for c in cetvel if c[2] == "kurucu"]
    cozucu = [c for c in cetvel if c[2] == "çözücü"]
    assert kurucu and cozucu
    for no, ad, sinif, chi in cetvel:
        assert sinif in ("kurucu", "koruyucu", "çözücü"), (no, sinif)
        assert sinif in SINIF_CIHETI, (no, sinif)   # taahhüt ölçülebilir
        assert chi is None or chi >= 1, (no, chi)

    # Bölgenin içi sıfır, dışı müsbet.
    assert sinif_ihlali("kurucu", +0.7) == 0.0
    assert sinif_ihlali("kurucu", -0.7) > 0.1
    assert sinif_ihlali("çözücü", -0.7) == 0.0
    assert sinif_ihlali("çözücü", +0.7) > 0.1
    assert sinif_ihlali("koruyucu", 0.5 * NIZAM_BANDI) == 0.0
    assert sinif_ihlali("koruyucu", 20.0 * NIZAM_BANDI) > 0.1
    # H157'nin asıl şartı: hiçbir şey yapmamak da ihlâldir.
    for sinif in ("kurucu", "çözücü"):
        assert sinif_ihlali(sinif, 0.0) > 0.0, sinif
        assert sinif_ihlali(sinif, -0.0) > 0.0, sinif
    # ...ve eksiklik ölçüsü sıfırda **düz değil**, eğimlidir: eğitim
    # ona yol bulabilsin. (İşaret ölçüsü tam burada düzdü.)
    c = SINIF_CIHETI["çözücü"]
    assert sinif_ihlali("çözücü", -0.01) < sinif_ihlali("çözücü", 0.0), c


def test_taksimat_ceridenin_kendi_sayisini_veriyor():
    """22 milyonluk şema, kendi toplamında **birebir** çıkıyor mu?

    Bir nispet cetveli en azından kendi sayısını yeniden üretmelidir;
    üretemiyorsa ölçekten bağımsız olduğu iddiası boştur. Ayrıca
    ancillanın bir **artık** olduğu burada ispatlanır: ceride onu
    müstakil bir hükümle vermez, üç ikinin kuvvetinden geriye kalandır.
    """
    from kuantum.kubit_taksimati import (CERIDE_TAKSIMAT, CERIDE_TOPLAM,
                               ANCILLA_ARTIK, taksim)
    assert sum(CERIDE_TAKSIMAT.values()) == CERIDE_TOPLAM
    assert ANCILLA_ARTIK() == CERIDE_TAKSIMAT["ancilla"]
    t = taksim(CERIDE_TOPLAM)
    for ad, kac in CERIDE_TAKSIMAT.items():
        assert t[ad] == kac, (ad, t[ad], kac)
    # küçük ölçekte de nispet korunur ve toplam tutar
    k = taksim(1000)
    assert sum(v for a, v in k.items() if a != "hukum") == 1000
    assert k["ancilla"] > k["veri"] > k["parametre"] > k["meleke"]


def test_eklem_paralel_degil_ve_KIRMIZIYA_donebiliyor():
    """*"Tek ve paralel olmayan, yek vücut çok uzuvlu"* -- ölçülüyor mu?

    Dört bölge dört ayrı model olsaydı aralarındaki kesitte entropi
    **tam sıfır** olurdu. Bu sınama iki şeyi birden ister (H90):

    1. Dimağ operatörü tatbik edilmeden ölçü **KIRMIZI** yanmalı --
       yanmıyorsa ölçü bir şey ölçmüyor demektir.
    2. Tatbik edildikten sonra dört sınırın dördü de dirilmeli.
    """
    import numpy as np
    from nefs.zihin_durumu import QAyar, QYazmac

    q = QYazmac(5, QAyar(bolge_ac=True))
    assert q.bolge_var("meleke") and q.bolge_var("parametre")
    q.kodla(np.random.default_rng(0).normal(size=(5, 8)))
    q.superpozisyon()
    q.mera()
    once = q.eklem_olcusu()
    assert len(once["kesit"]) == 4, once["kesit"]
    assert not once["eklemli"], once            # KIRMIZI olabiliyor
    q.dimag()
    sonra = q.eklem_olcusu()
    assert sonra["eklemli"], sonra
    assert sonra["kopuk"] == [], sonra

    # ...ve bölgeler kapatılınca şema uygulanmamış olur; ölçü bunu görür.
    q2 = QYazmac(5, QAyar(bolge_ac=False))
    assert len(q2.eklem_olcusu()["kesit"]) == 1


def test_ttkan_kendi_sahasinda_tam_yabanci_sahada_degil():
    """TT-KAN'ın hakkı da haddi de ölçülüyor mu?

    * **Hakkı:** Kronecker çarpımı tam TT'dir; hata makine
      hassasiyetinde olmalıdır. Olmuyorsa kusur ceridede değil bizim
      kodumuzdadır ve TT'yi yabancı sahada denemiş oluruz.
    * **Haddi:** ceridenin ``278.528 FLOP`` hesabı çekirdek eleman
      sayısıdır; yoğun (ya da dolaşık) vektöre hakikî TT-MVM bundan çok
      daha pahalıdır ve ``16⁴`` ölçeğinde yoğun çarpmayı bile geçer.
    """
    from nefs.ttkan import (kiyas, tt_flop, yogun_flop, ceride_flop)
    r = kiyas(n=8, d=3, rank=8)
    assert r["hata_kronecker"] < 1e-10, r["hata_kronecker"]
    assert r["bag_kronecker"] == (1, 1, 1, 1), r["bag_kronecker"]
    # sıkıştırma HAFIZADA hakikîdir
    assert r["eleman_tt"] * 10 < r["eleman_yogun"], r
    # ...fakat HESAPTA değil: 16⁴'te TT-MVM yoğunu geçer.
    assert tt_flop(16, 4, 16) > yogun_flop(4096), (tt_flop(16, 4, 16),
                                                   yogun_flop(4096))
    # ceridenin sayısı yeniden üretiliyor (iddia doğru anlaşılmış mı)
    assert ceride_flop(16, 4, 16) == 278_528


def test_ikmal_fikralari_ucu_de_KIRMIZIYA_donebiliyor():
    """Ceridenin İkmâl Fıkraları: her biri reddedebiliyor mu?

    Bir emniyet kilidi hiçbir şeyi reddedemiyorsa kilit değildir.
    Üçünün de kırmızıya döndüğü **fiilen** gösterilir.
    """
    import numpy as np
    from akis.ikmal import (lions_konsantrasyonu, bochner_suzgeci,
                            cayley_hatasi, cayley_cekilmesi,
                            postnikov_indisi)
    rng = np.random.default_rng(0)

    # Lions: tek yığın tıkız, iki uzak yığın ikilenme, yayık dağılma
    tek = rng.normal(size=(80, 2)) * 0.3
    assert lions_konsantrasyonu(tek, np.ones(80))["hâl"] == "tıkız"
    iki = np.vstack([rng.normal(size=(40, 2)) * 0.3,
                     rng.normal(size=(40, 2)) * 0.3 + 40.0])
    assert lions_konsantrasyonu(iki, np.ones(80))["hâl"] == "ikilenme"
    yayik = rng.normal(size=(200, 2)) * 200.0
    assert lions_konsantrasyonu(yayik, np.ones(200))["hâl"] == "dağılma"

    # Bochner: f = ½‖x‖²'de N = n iken KESKİN (artık ≈ 0), N < n iken kırık
    def kare(z):
        z = np.asarray(z, float)
        return 0.5 * float(z @ z)

    x = np.array([0.7, -0.3, 0.5])
    r = bochner_suzgeci(kare, x, N=None)
    assert r["kabul"], r
    assert abs(r["artık"]) < 1e-6, r          # Bochner burada eşitliktir
    r1 = bochner_suzgeci(kare, x, N=1.0)
    assert not r1["kabul"], r1                 # KIRMIZI

    # Cayley: dikliği makine hassasiyetinde korumalı
    X = np.linalg.qr(rng.normal(size=(8, 3)))[0]
    xi = rng.normal(size=(8, 3))
    xi = xi - X @ (X.T @ xi)
    h = cayley_hatasi(X, xi)
    assert h["diklik_hatası"] < 1e-12, h
    # ...ve sıfır yönde kimlik olmalı
    assert np.allclose(cayley_cekilmesi(X, np.zeros_like(X)), X, atol=1e-12)

    # Postnikov vekili: tıkanıksızda sıçrama ÜRETMEMELİ
    assert postnikov_indisi([[1, 0, 0]] * 3)["tıkanık"] is False
    t = postnikov_indisi([[1, 0, 0], [1, 2, 0], [1, 0, 0]])
    assert (t["mertebe"], t["derece"]) == (1, 1), t


def test_ceride_uc_kapali_form_babi():
    """FCT κ = 1,0, STA sadakati, Fubini ölçek yönünü yok ediyor mu?

    Üçü de ceridenin **kendi iddiasıdır** ve üçü de burada sayıyla
    denetlenir; her birinin yanında kırmızıya dönen bir kıyas durur.
    """
    import math
    import numpy as np
    from kuantum.ceride import (fct_tasarimi, fct_katsayilari,
                                fct_degerlendir, gcl_dugumleri,
                                esaralikli_tasarim, sta_kosusu,
                                fubini_study, fubini_dogrulamasi)

    # --- FCT: XᵀX = I TAM, κ = 1,0; eş aralıkta κ patlar (kırmızı)
    for M in (8, 32):
        X, w, d = fct_tasarimi(M)
        G = X.T @ X
        assert np.linalg.norm(G - np.eye(M + 1)) < 1e-12, M
        assert abs(np.linalg.cond(G) - 1.0) < 1e-9, M
    assert np.linalg.cond(esaralikli_tasarim(32).T
                          @ esaralikli_tasarim(32)) > 1e6
    M = 24
    x = gcl_dugumleri(M)
    f = np.exp(-3.0 * x ** 2) * np.cos(4.0 * x)
    assert np.max(np.abs(fct_degerlendir(fct_katsayilari(f, M), x, M)
                         - f)) < 1e-12

    # --- STA: sürüşsüz sadakat τ ile ÇÖKMELİ, sürüşle 1'de kalmalı
    yavas = sta_kosusu(40.0, sta=False)["sadakat"]
    hizli = sta_kosusu(0.5, sta=False)["sadakat"]
    assert yavas > 0.99, yavas          # adiyabatik hadde doğru
    assert hizli < 0.5, hizli           # hızlı geçişte çöküyor (kırmızı)
    for tau in (40.0, 2.0, 0.5):
        r = sta_kosusu(tau, sta=True)
        assert r["sadakat"] > 0.999, (tau, r)
        assert r["θ̇_uçta"] == 0.0, r    # Ĥ_CD(0) = Ĥ_CD(τ) = 0

    # --- Fubini-Study: PSD, ve ölçek yönünü YOK ETMELİ
    def dalga(th):
        a, b = float(th[0]), float(th[1])
        return np.array([math.cos(a) * math.cos(b),
                         math.cos(a) * math.sin(b), math.sin(a), 0.0])

    r = fubini_dogrulamasi(dalga, np.array([0.4, 0.9]))
    assert r["psd"], r

    def olcekli(th):
        return (1.0 + 0.5 * float(th[2])) * dalga(th[:2])

    g3 = fubini_study(olcekli, np.array([0.4, 0.9, 0.0]))
    assert abs(float(g3[2, 2])) < 1e-8, g3   # izdüşüm terimi çalışıyor


def test_gomme_genlik_kodlamasi_ve_35_kubit():
    """4096 boyut 12 kübitte mi, ve χ≤16 iddiası ölçülüyor mu?"""
    import numpy as np
    from nefs.gomme import (kubit_sayisi, genlik_gom, genlik_coz,
                            qtt_bag_ihtiyaci, gomme_hatasi, YazmacOlcusu)
    assert kubit_sayisi(4096) == 12
    o = YazmacOlcusu()
    assert (o.kubit_yigin, o.kubit_yer, o.kubit_mana) == (11, 12, 12)
    assert o.kubit == 35 and o.token == 8_388_608
    rng = np.random.default_rng(0)
    v = rng.normal(size=4096)
    psi, nrm = genlik_gom(v)
    assert abs(float(psi @ psi) - 1.0) < 1e-12
    assert np.allclose(genlik_coz(psi, nrm), v, atol=1e-9)
    # χ = 16 iddiası VERİYE BAĞLI: düzgünde tutuyor, rastgelede tutmuyor
    duz, _ = genlik_gom(np.sin(np.linspace(0, 6, 4096))
                        * np.exp(-np.linspace(0, 3, 4096)))
    assert gomme_hatasi(duz, 12, 16) < 1e-9
    assert gomme_hatasi(psi, 12, 16) > 0.5      # KIRMIZI olabiliyor
    assert max(qtt_bag_ihtiyaci(psi, 12)) == 64


def test_zirh_dordu_de_KIRMIZIYA_donebiliyor():
    """Gaye ölçüsü: dördü de sıfırken L=0, biri bozukken L büyük."""
    import math
    import numpy as np
    from kuantum.tda import vietoris_rips
    from nefs.zirh import (betti_kaybi, koho_kaybi, sheaf_uyumsuzlugu,
                           homotopi_kaybi, zirh_kaybi, sheaf_izdusumu)
    from nefs.zihin_durumu import donme

    aci = np.linspace(0, 2 * math.pi, 8, endpoint=False)
    cember = np.stack([np.cos(aci), np.sin(aci)], axis=1)
    Dc = np.sqrt(((cember[:, None] - cember[None]) ** 2).sum(2))
    assert betti_kaybi(vietoris_rips(Dc, 0.9, azami_boyut=2), 1)["kayıp"] == 1.0

    rng = np.random.default_rng(0)
    iki = np.vstack([rng.normal(size=(6, 2)) * 0.2,
                     rng.normal(size=(6, 2)) * 0.2 + 10.0])
    Di = np.sqrt(((iki[:, None] - iki[None]) ** 2).sum(2))
    assert koho_kaybi(vietoris_rips(Di, 0.8, azami_boyut=1), 0)["kayıp"] == 1.0
    assert koho_kaybi(vietoris_rips(Di, 16.0, azami_boyut=1), 0)["kayıp"] == 0.0

    a = np.array([1.0, 2.0, 3.0])
    assert sheaf_uyumsuzlugu(a, a) == 0.0
    assert sheaf_uyumsuzlugu(a, a + 0.5) > 0.0
    # uyum tamken izdüşüm KİMLİĞE gitmeli (hiçbir şey söndürmemeli)
    assert np.allclose(sheaf_izdusumu(a, a), np.eye(3), atol=1e-6)

    assert homotopi_kaybi([donme(0.4), donme(-0.4)])["kayıp"] < 1e-12
    assert homotopi_kaybi([donme(0.4), donme(0.1)])["kayıp"] > 0.1

    # Küllî kayıp: dördü sıfırken TAM sıfır (kaydırma doğru mu)
    assert abs(zirh_kaybi()["kayıp"]) < 1e-12
    assert zirh_kaybi()["çelişkisiz"]
    # ...ve tek bir ihlâl düz ortalamadan (0,25) ÇOK daha ağır cezalanmalı
    tek = zirh_kaybi(betti=1.0)["kayıp"]
    assert tek > 0.5, tek
    assert not zirh_kaybi(betti=1.0)["çelişkisiz"]


def test_ttkan_rank1_ceridenin_sayisini_TAM_veriyor():
    """χ_v = 1 yolunda ceridenin 278.528'i birebir çıkıyor mu?

    H175'te TT'yi χ_v = 16'lık bir MPS vektörüne bağlamıştım; padişahın
    ihtarı üzerine rank-1 yolu kuruldu. Bu sınama o tashihi kilitler.
    """
    import numpy as np
    from nefs.ttkan import (TTDizey, tt_carp_rank1, ceride_flop,
                            rank1_ayristir)
    rng = np.random.default_rng(0)
    n, d, r = 16, 4, 16
    cek, r0 = [], 1
    for k in range(d):
        r1 = 1 if k == d - 1 else r
        cek.append(rng.normal(size=(r0, n, n, r1)))
        r0 = r1
    tt = TTDizey(cekirdek=cek, n=n, D=n ** d)
    _, f = tt_carp_rank1(tt, [rng.normal(size=n) for _ in range(d)])
    assert f == ceride_flop(16, 4, 16) == 278_528, f

    # rank-1 yol CEBİRSEL OLARAK TAM: küçük ölçekte yoğunla örtüşmeli
    n2, d2 = 4, 4
    cek2, r0 = [], 1
    for k in range(d2):
        r1 = 1 if k == d2 - 1 else 4
        cek2.append(rng.normal(size=(r0, n2, n2, r1)))
        r0 = r1
    tt2 = TTDizey(cekirdek=cek2, n=n2, D=n2 ** d2)
    M = tt2.yogun()
    a = [rng.normal(size=n2) for _ in range(d2)]
    h, _ = tt_carp_rank1(tt2, a)
    Y = h[0]
    for c in h[1:]:
        Y = np.tensordot(Y, c, axes=([-1], [0]))
    v = a[0]
    for x in a[1:]:
        v = np.multiply.outer(v, x)
    assert np.allclose(Y.ravel(), M @ v.ravel(), atol=1e-10)

    # ...fakat rastgele bir vektör rank-1 DEĞİLDİR; sayı bunu söylüyor
    _, hata = rank1_ayristir(rng.normal(size=4096), n=16, d=3)
    assert hata > 0.9, hata


def test_qsp_faz_tablosu_CEVRIMDISI_ve_dogru():
    """FAZ 0: faz açıları koşumda aranmıyor, tablodan çekiliyor mu?

    Padişahın 2. kat'î kuralı: *"QSP açısını runtime'da arama."*
    Üç şey birden denetlenir: (a) tablo var ve doğru, (b) tabloda
    olmayan β **hata veriyor** (sessizce aramıyor), (c) artık yalnız
    uydurma düğümlerinde değil, ızgarada da küçük.
    """
    import math
    import numpy as np
    from kuantum.ceride import (GIBBS_FAZ_TABLOSU, GIBBS_DERECE,
                                gibbs_fazlari, gibbs_cift, qsp_degeri,
                                qsp_faz_bul)
    assert GIBBS_DERECE == 32
    assert sorted(GIBBS_FAZ_TABLOSU) == [1.0, 2.0, 4.0, 8.0]
    izgara = np.linspace(-1.0, 1.0, 201)
    for b, ph in GIBBS_FAZ_TABLOSU.items():
        assert len(ph) == (GIBBS_DERECE + 2) // 2, (b, len(ph))
        f = gibbs_cift(b)
        artik = max(abs(qsp_degeri(ph, GIBBS_DERECE, t) - f(t))
                    for t in izgara)
        assert artik < 1e-10, (b, artik)     # ızgarada da, düğümde değil
    # tabloda olmayan β: sessizce arama YOK, hata var
    try:
        gibbs_fazlari(3.0)
        assert False, "tabloda olmayan β hata vermeliydi"
    except KeyError:
        pass
    # bulucu kendisi de doğru: T_d tam temsil edilebilir
    T = np.polynomial.chebyshev.Chebyshev.basis(4)
    _, art, _ = qsp_faz_bul(lambda t: float(T(t)), 4)
    assert art < 1e-9, art


def test_dimag_41_meleke_URETEC_ve_muvazene_KIRMIZIYA_donuyor():
    """41 meleke katman değil üreteç mi, ve muvazene ölçüsü ısırıyor mu?

    Padişahın küllî esası: *"41 Meleke, arka arkaya dizilen 41 klasik
    gizli katman DEĞİLDİR; tek bir Hamiltonyenin paralel koordinat
    eksenleridir."* Üç şart denetlenir.
    """
    import numpy as np
    from nefs.melekeler import (MELEKE_SAYISI, MERTEBE_SAYISI, KANONIK_CETVEL,
                            EKSIK_MELEKELER,
                            melekelerin_dondurucusu, H_toplam,
                            DimagAyari)

    # 1) divanın KANONİK cetveli harfiyen tutmalı, boş mertebe olmamalı
    cet = melekelerin_dondurucusu(np.zeros(MELEKE_SAYISI), 12)["cetvel"]
    assert len(cet) == MELEKE_SAYISI
    for no, m in KANONIK_CETVEL.items():
        assert cet[no] == m, (no, cet[no], m)
    # cetvelde 39 meleke var; eksik ikisi AYRICA işaretli durmalı
    # divan 09-KÜLLÎ-TEŞKİLAT celsesinde borcu kapattı: cetvel 44 tam
    assert len(KANONIK_CETVEL) == MELEKE_SAYISI == 44
    assert EKSIK_MELEKELER == {}, EKSIK_MELEKELER
    assert cet[9] == 4 and cet[21] == 12          # tasdik edilen ikisi
    assert cet[42] == cet[43] == cet[44] == 19    # umum, talim, tahsil
    for m in range(MERTEBE_SAYISI):
        assert any(v == m for v in cet.values()), m

    # 2) üreteçler ANTİSİMETRİK: exp(θT) tam ortogonal olsun
    bir = melekelerin_dondurucusu(np.ones(MELEKE_SAYISI), 12)
    for a in (0, 5, 40):
        T = bir["üreteç"][a]             # θ=1 iken üretecin kendisi
        assert np.allclose(T, -T.T)
        assert abs(np.trace(T)) < 1e-12

    # bir mertebenin Hamiltonyeni TEK dizeydir, katman yığını değil
    H, uy = bir["Ĥ"][7], bir["üyeler"][7]
    assert H.shape == (12, 12) and np.allclose(H, -H.T)
    assert sorted(uy) == [18, 23]        # k=7 mantık ve dedüksiyon

    # 3) BGCM: tek meleke uyanıkken TAM sıfır, 41'i birden büyük
    t0 = np.zeros(MELEKE_SAYISI)
    t0[0] = 1.0
    b0 = melekelerin_dondurucusu(t0, 12)["bgcm"]
    assert b0["kayıp"] == 0.0 and b0["muvazeneli"]
    rng = np.random.default_rng(0)
    b1 = melekelerin_dondurucusu(rng.normal(size=MELEKE_SAYISI), 12)["bgcm"]
    assert b1["kayıp"] > 1.0 and not b1["muvazeneli"]      # KIRMIZI
    # **NORMALİZE hâli [0,1]de kalmalı** -- θ ne kadar azarsa azsın
    for olc in (0.05, 1.0, 5.0, 50.0, 500.0):
        bb = melekelerin_dondurucusu(
            olc * rng.normal(size=MELEKE_SAYISI), 12)["bgcm"]
        assert 0.0 <= bb["kayıp_norm"] <= 1.0, (olc, bb["kayıp_norm"])

    # Ĥ_toplam üç kalemi ayrı ayrı raporlamalı; hiçbiri gizlenmemeli
    r = H_toplam(0.05 * rng.normal(size=MELEKE_SAYISI),
                 rng.normal(size=(16, 3)), H_arc=np.eye(16) * 0.3,
                 ayar=DimagAyari(D=16))
    assert set(r["kalem"]) == {"ARC", "meleke", "BGCM"}
    assert r["kalem"]["ARC"] > 0 and r["kalem"]["meleke"] > 0
    assert r["dolu_mertebe"] == MERTEBE_SAYISI
    assert r["H"].shape == (16, 16)


def test_gomme_qtt_cekirdegi_chi8_ve_muhurlenen_ayrisim():
    """Emir 2 ve 3: χ=8 QTT çekirdeği, n=2 d=12 mühürlü mü?"""
    import numpy as np
    from nefs.gomme import (QTT_TABAN, QTT_KADEME, QTT_BAG,
                            qtt_parametre_sayisi, qtt_gomme,
                            qtt_sadakat_cetveli)
    assert (QTT_TABAN, QTT_KADEME, QTT_BAG) == (2, 12, 8)
    assert QTT_TABAN ** QTT_KADEME == 4096
    assert qtt_parametre_sayisi() == 1536

    rng = np.random.default_rng(0)
    # yapılı veride χ=8 TAM temsil eder; rastgelede ETMEZ (kırmızı)
    duz = np.sin(np.linspace(0, 6, 4096)) * np.exp(-np.linspace(0, 3, 4096))
    _, sad, par = qtt_gomme(duz, chi=8)
    assert sad > 0.999999, sad
    assert par < 4096, par                      # sıkıştırma hakikî
    _, sad_r, _ = qtt_gomme(rng.normal(size=4096), chi=8)
    assert sad_r < 0.3, sad_r                   # KIRMIZI olabiliyor
    # χ = 1 (rank-1) yasaklandı: yapılı veride bile yetmiyor
    _, sad1, par1 = qtt_gomme(duz, chi=1)
    assert par1 == 24 and sad1 < sad, (par1, sad1, sad)


def test_ic_bag_serpistirilmis_QTT_izafi_operatorleri_TAM_tasiyor():
    """H193'ün nakzı: doğru sırayla mikro-QTT bizim operatörlerimizi taşır.

    Üç şart birden denetlenir:
      1. Gidiş-dönüş **tam** (sıralama tersinir).
      2. Bizim fiilen kullandığımız operatörler (öteleme, bantlı,
         Laplasyen) küçük ``r`` ile makine hassasiyetinde taşınıyor ve
         aynı bütçedeki düz kırpmadan **açıkça iyi**.
      3. Rastgele çekirdek **taşınmıyor** -- kırmızı hâlâ mümkün.
    """
    import math
    import numpy as np
    from kuantum.yazmac import (qtt_cekirdek_ayristir, qtt_cekirdek_ac,
                             kapali_form_kiyasi, acik_parametre)

    chi = 32
    T = np.zeros((chi, chi))
    for i in range(chi):
        T[(i + 1) % chi, i] = 1.0
    oteleme = np.stack([T, T.T], axis=1)

    # 1) gidiş-dönüş tam
    cek, _, _ = qtt_cekirdek_ayristir(oteleme, r=64)
    assert np.allclose(qtt_cekirdek_ac(cek, chi, 2), oteleme, atol=1e-10)

    # 2) izafî öteleme küçük r ile TAM; düz kırpma aynı bütçede çuvallıyor
    r = kapali_form_kiyasi(oteleme, rler=(4,))
    c = r["cetvel"][0]
    assert c["hata_qtt"] < 1e-12, c
    assert c["hata_düz"] > 0.5, c
    assert c["qtt_daha_iyi"], c
    assert c["parametre"] * 10 < acik_parametre(chi, 2), c   # 10 kat sıkı

    # bantlı ve Laplasyen de aynı
    A = np.zeros((chi, chi))
    for i in range(chi):
        for j in range(max(0, i - 2), min(chi, i + 3)):
            A[i, j] = math.exp(-abs(i - j))
    for G in (np.stack([A, A.T], axis=1),
              np.stack([np.diag(np.full(chi, 2.0))
                        + np.diag(np.full(chi - 1, -1.0), 1)
                        + np.diag(np.full(chi - 1, -1.0), -1)] * 2, axis=1)):
        c = kapali_form_kiyasi(G, rler=(4,))["cetvel"][0]
        assert c["hata_qtt"] < 1e-12 and c["qtt_daha_iyi"], c

    # 3) rastgele çekirdek TAŞINMIYOR -- ölçü kırmızıya dönebiliyor
    rng = np.random.default_rng(0)
    c = kapali_form_kiyasi(rng.normal(size=(chi, 2, chi)),
                           rler=(16,))["cetvel"][0]
    assert c["hata_qtt"] > 0.3 and not c["qtt_daha_iyi"], c


def test_lisan_tiktoken_yerel_tablodan_ve_izafi_mevki():
    """tiktoken depodaki tablodan okunuyor mu, izafî mevki öteleme-değişmez mi?"""
    import numpy as np
    from nefs.lisan import (kodlayici, izafi_operator, izgara_kodla,
                            OZEL_BELIRTECLER)

    k = kodlayici()
    assert k.kaynak in ("o200k_yerel", "tiktoken", "bayt"), k.kaynak
    if k.kaynak == "o200k_yerel":
        assert k.taban_sozluk > 190_000, k.taban_sozluk
        for m in ("kırmızı kare sağa kayar", "def solve(g): return g[::-1]"):
            assert k.coz(k.kodla(m)) == m, m
    assert k.sozluk == k.taban_sozluk + len(OZEL_BELIRTECLER)

    # izafî operatörler TAM ortogonal ve tersi kendi eşleniği
    nx, ny = 5, 4
    D = izafi_operator(nx, ny, 1, 0)
    assert np.allclose(D.T @ D, np.eye(nx * ny), atol=1e-12)
    assert np.allclose(D @ izafi_operator(nx, ny, -1, 0),
                       np.eye(nx * ny), atol=1e-12)

    # aynı örüntü ızgaranın HER YERİNDE aynı kodlanmalı
    A = np.zeros((6, 6), int); A[1, 1] = 3; A[1, 2] = 5
    B = np.zeros((6, 6), int); B[4, 3] = 3; B[4, 4] = 5
    ka = [x.kod() for x in izgara_kodla(A)["izafi"] if x.merkez == 3][0]
    kb = [x.kod() for x in izgara_kodla(B)["izafi"] if x.merkez == 3][0]
    assert ka == kb, (ka, kb)


# Koşturucu dosyanın SONUNDA durur: aksi hâlde kendisinden sonra
# tarif edilen sınamalar `globals()` taramasına girmez ve sessizce
# koşulmaz. Ölçüldü: kâide sınamaları eklendiği hâlde sayı 41 kalmıştı.
if __name__ == "__main__":
    raise SystemExit(main())
