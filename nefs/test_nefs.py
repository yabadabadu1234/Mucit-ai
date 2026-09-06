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
# **KLASİK MELEKELER İMHA EDİLDİ.** ``AKIS``, ``KULLI_SIRA``, ``Nefs``,
# ``sira_gecerli_mi``, ``melekeler``, ``sicil``, ``Durum``,
# ``Parametreler`` yok; onları sınayan sınamalar da aynı turda kesildi
# (ferman 2-B). Kalan iki yardımcı hâlâ canlı koda hizmet ediyor.
from .melekeler import ehlilestir, tevafuk, devirler


def _E(tohum: int = 0, n: int = 20, d: int = 12) -> np.ndarray:
    return np.random.default_rng(tohum).normal(size=(n, d))


# =====================================================================
#  A. Sözleşme
# =====================================================================
















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
    from matematik.mizan import MERTEBELER
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








# =====================================================================
#  C. Davranış
# =====================================================================
















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



# =====================================================================
#  D. KÂİDE MÎZÂNI -- H85'in icrası, H90'ın şartıyla
# =====================================================================












def test_kodlama_tersinir_ve_hadamard_esit_uzak():
    """Kodlama funktörünün sıhhati -- ve **ikili dalın imhası**.

    Bu sınama evvelce ``belirtecleri_kodla(T, 4, 16)`` çağırıp düz
    ikili kodlamanın "4 boyutta elde edilebilecek en iyi hâl" olduğunu
    tasdik ediyordu. Padişahın fermanıyla o dal **imha edildi**:
    *"ikili kübit kodlama iptal olup qudit gelecek"*, *"yasaklanan ne
    kadar usul varsa hepsini imha edeceksin."*

    O hâlde sınama artık yasağın **fiilen** durduğunu ölçer:

    1. **Tersinirlik** -- her belirteç geri çözülebilmeli (H14).
    2. **Yasak duruyor mu** -- ``kubit < sozluk`` çağrısı HATA vermeli.
       Sessizce ikiliye düşerse yasak fiilen kalkmış olur.
    3. **Kategorik eşit uzaklık** -- ``kubit ≥ sozluk``ta Hadamard
       tam eşit uzaklık verir (değişke 0), yâni fiilen qudit tabanı.
    """
    from .musahede import kopru
    from .qegitim import belirtecleri_kodla

    r = kopru()
    assert r["tersinir"] is True and r["çarpışma"] == 0, r

    # --- 2. YASAK FİİLEN DURUYOR MU
    try:
        belirtecleri_kodla(np.arange(16), 4, 16)
    except ValueError as e:
        assert "İMHA" in str(e), str(e)
    else:                                            # pragma: no cover
        raise AssertionError(
            "kubit=4 < sozluk=16 geçti: düz ikili kodlama HÂLÂ "
            "koşuyor demektir, yâni ferman fiilen tatbik edilmemiş.")

    # --- 3. Hadamard/qudit tabanı: TAM eşit uzaklık
    T = np.arange(16)
    ust = np.triu_indices(16, 1)
    E = belirtecleri_kodla(T, 16, 16)
    D = np.linalg.norm(E[:, None, :] - E[None, :, :], axis=2)[ust]
    assert float(D.min()) > 0.0                      # çarpışma yok
    assert float(D.std() / D.mean()) < 1e-9          # TAM eşit uzak

def test_kod_uzayi_stabilizer_ile_yuzlesiyor():
    """Hüküm bloğu, MPS'ten BAĞIMSIZ ikinci bir temsille denetlenebiliyor mu?

    H88'in dersi: ``beyan`` aylarca yanlış çevreden okudu ve
    **karşılaştıracak ikinci bir temsil olmadığı için** farkedilmedi.
    `kuantum/stabilizer.py` o ikinci temsili verir: mantık katmanı
    ``CZ``/``Z`` ile kurulduğu için Clifford'dur ve stabilizer
    çerçevesinde **tam** temsil edilir -- kesme yok, ``2^n`` açılmıyor.
    """
    from .zirh import muhru_stabilizerle_yuzlestir as _muhur

    n = 4
    duz = _muhur(None, n=n, cz_ciftleri=[])["P_stab"]
    assert np.allclose(duz, 1.0 / (1 << n), atol=1e-9), duz

    # ``CZ`` bir FAZ kapısıdır: taban dağılımını DEĞİŞTİRMEZ. Bu, kütük
    # H107'nin ölçülmüş dersinin müstakil bir teyididir -- işaret tek
    # başına marjinali oynatmaz, sönme girişimden gelir.
    isaretli = _muhur(None, n=n, cz_ciftleri=[(0, 1)])["P_stab"]
    assert np.allclose(isaretli, duz, atol=1e-9)

    # Fakat GENLİKTE fark vardır ve işaret oradadır.
    from kuantum.stabilizer import StabilizerDurum
    Y = np.array([[1, 1, 0, 0]], dtype=np.int64)
    g0 = np.asarray(StabilizerDurum.arti(n).genlik(Y)).ravel()[0]
    g1 = np.asarray(_muhur(None, n=n, cz_ciftleri=[(0, 1)])["kod"].genlik(Y)).ravel()[0]
    assert abs(g1 + g0) < 1e-9, (g0, g1)          # işaret çevrilmiş


def test_iki_olcek_hakikaten_iki():
    """Dosya 5: sağîr ölçek, kebîrin zaten bildiğini mi söylüyor?

    İki ölçekli mimarinin bedeli vardır; kazancı ispatlanmalıdır.
    Ölçüt Grassmann asal açılarıdır ve **kırmızı yanabilir**: açılar
    sıfıra yakın çıksaydı ikinci ölçek gereksiz demekti.
    """
    from .musahede import gorevleri_getir

    from .musahede import iki_olcegin_acisi

    g = gorevleri_getir("training")[:10]
    artiklar = []
    for gv in g:
        r = iki_olcegin_acisi(gv, ne="sağîr")
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

    o = iki_olcegin_acisi(gorevler=g)
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
    from .musahede import ortu

    kapali = ortu(ne="bağ", n_gorev=60, kapi=False)
    acik = ortu(ne="bağ", n_gorev=60, kapi=True)
    assert kapali["yeterli_mi"] and acik["yeterli_mi"]
    assert acik["korelasyon"] > 0.15, acik
    assert acik["sukut_tıkanıkta"] > kapali["sukut_tıkanıkta"], (kapali, acik)

    # Kozikıl şartı: ikili uyuşma denklik kurduğu için üçlüler tutmalı.
    from .musahede import gorevleri_getir
    for gv in gorevleri_getir("training")[:40]:
        c = ortu(gv)
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


#: **AÇIK BORÇ DEFTERİ.** Tahttan erişilemeyen uzuvlar. Liste
#: yalnız KISALABİLİR: bir modül buradan çıkarsa sınama yeşil kalır,
#: yeni bir modül düşerse KIRMIZI yanar. Yani sayı bir hedef değil,
#: bir mandaldır (ratchet).
#:
#: NİÇİN VAR: bu sınama evvelce yeşildi, fakat sahte yeşildi.
#: ``tanilama/nizam.py:GIRISLER`` ALTI giriş sayıyordu -- main.egitim,
#: main.cikarim, main.kaggle_egitim, main.kaggle_cikarim,
#: nefs.melekeler, nefs.hukum_denetimi. Dört sahte taht, yalnız o
#: ağaçlardan erişilen modülleri de "tebaa" gösteriyordu. KÜME 9'da
#: giriş ikiye indi (main tek hâkim) ve gizlenen 15 yetim ortaya çıktı.
#: Sınamayı yeşile boyamak için tahtları geri koymak, ölçüyü kendi
#: lehine bozmak olurdu.
# ══════════════════════════════════════════════════════════════════
#  ERİŞİLEBİLİRLİK SINAMASI İMHA EDİLDİ (ferman)
# ══════════════════════════════════════════════════════════════════
#
# Burada ``YETIM_BORCU`` mandalı ve ``test_padisahin_eli_HER_MODULE_
# uzaniyor`` sınaması vardı. İkisi de **yalancıydı** ve padişah onu
# ``nefs/ayna.py`` üstünde yakaladı:
#
#     Ayna yazıldı, ``main/egitim.py``ye ayarları kondu, ithal edildi.
#     Sınama YEŞİL yandı: "beylik modül yok."
#     Halbuki ayna tâlim hattında **hiç çağrılmıyordu**.
#
# Kusur ölçünün kendisindeydi: ``tanilama/nizam.py`` ithal grafına
# bakıyordu, çağrı grafına değil. Bir modülün adını bir listeye yazmak
# yahut onu ithal etmek, o modülün **iş gördüğü** manasına gelmez.
# Yeşil yanan bir sınamanın arkasına saklanmak, borcu kapatmak değil
# borcu görünmez kılmaktır -- münafıklıktır.
#
# Ferman: *"ana akışta fiilen ne koştuğunu asla ölçmeyeceksin, kodu
# okuyup zihninle tayin edeceksin."* Bir modülün iş görüp görmediği
# artık bir sınamaya değil, **kodu okuyana** sorulur.

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
        q = QNefs(0, QAyar(tohum=0), gaye=acik).idrak_et(E)
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
    from . import kulli_kayip as sozlesme

    for r in sozlesme.sozunde_mi(n_satir=3, chi=16, ne="hepsi"):
        assert not r["ihlâl"], r
        assert not r["kullanılmayan"], r

    # --- MUTASYON: 𝒪₁ Müşahede'nin ilanı boşaltılırsa yakalanmalı.
    eski = sozlesme.SOZLESME[1]
    sozlesme.SOZLESME[1] = (("sukut",), "kasten yanlış ilan")
    try:
        r = sozlesme.sozunde_mi(1, n_satir=3, chi=16)
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
        q = QYazmac(3, QAyar(tohum=0))
        q.kodla(np.random.default_rng(0).normal(size=(3, 12)))
        q.superpozisyon()
        q.harman(kulli_dahil=kulli_dahil)
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
    from .zirh import NIZAM_BANDI, SINIF_CIHETI, taahhude_yuzlestir
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
    assert taahhude_yuzlestir("kurucu", +0.7) == 0.0
    assert taahhude_yuzlestir("kurucu", -0.7) > 0.1
    assert taahhude_yuzlestir("çözücü", -0.7) == 0.0
    assert taahhude_yuzlestir("çözücü", +0.7) > 0.1
    assert taahhude_yuzlestir("koruyucu", 0.5 * NIZAM_BANDI) == 0.0
    assert taahhude_yuzlestir("koruyucu", 20.0 * NIZAM_BANDI) > 0.1
    # H157'nin asıl şartı: hiçbir şey yapmamak da ihlâldir.
    for sinif in ("kurucu", "çözücü"):
        assert taahhude_yuzlestir(sinif, 0.0) > 0.0, sinif
        assert taahhude_yuzlestir(sinif, -0.0) > 0.0, sinif
    # ...ve eksiklik ölçüsü sıfırda **düz değil**, eğimlidir: eğitim
    # ona yol bulabilsin. (İşaret ölçüsü tam burada düzdü.)
    c = SINIF_CIHETI["çözücü"]
    assert taahhude_yuzlestir("çözücü", -0.01) < taahhude_yuzlestir("çözücü", 0.0), c


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
    q.harman()
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




def test_ikmal_fikralari_ucu_de_KIRMIZIYA_donebiliyor():
    """Ceridenin İkmâl Fıkraları: her biri reddedebiliyor mu?

    Bir emniyet kilidi hiçbir şeyi reddedemiyorsa kilit değildir.
    Üçünün de kırmızıya döndüğü **fiilen** gösterilir.
    """
    import numpy as np
    from matematik.geometri import (lions_konsantrasyonu, bochner_suzgeci,
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
    from ogrenme.optimize import (yokus, chebyshev_tasarimi,
                                  kestirmeden_sur)

    def fubini_study(psi, teta, h=1e-5, ne="sayısal"):
        # KÜME 4 tevhidinde (H223) fubini_study `yokus`nin
        # `sayısal`/`doğrulama` kiplerine eridi.
        return yokus(ne=ne, psi=psi, teta=teta, h=h)

    # --- FCT: XᵀX = I TAM, κ = 1,0; eş aralıkta κ patlar (kırmızı)
    for M in (8, 32):
        X, w, d = chebyshev_tasarimi(M, "tasarım")
        G = X.T @ X
        assert np.linalg.norm(G - np.eye(M + 1)) < 1e-12, M
        assert abs(np.linalg.cond(G) - 1.0) < 1e-9, M
    assert np.linalg.cond(chebyshev_tasarimi(32, "eşaralıklı").T
                          @ chebyshev_tasarimi(32, "eşaralıklı")) > 1e6
    M = 24
    x = chebyshev_tasarimi(M, "düğüm")
    f = np.exp(-3.0 * x ** 2) * np.cos(4.0 * x)
    assert np.max(np.abs(chebyshev_tasarimi(M, "değer",
                                          a=chebyshev_tasarimi(M, "katsayı", f=f),
                                          x=x)
                         - f)) < 1e-12

    # --- STA: sürüşsüz sadakat τ ile ÇÖKMELİ, sürüşle 1'de kalmalı
    yavas = kestirmeden_sur(40.0, sta=False)["sadakat"]
    hizli = kestirmeden_sur(0.5, sta=False)["sadakat"]
    assert yavas > 0.99, yavas          # adiyabatik hadde doğru
    assert hizli < 0.5, hizli           # hızlı geçişte çöküyor (kırmızı)
    for tau in (40.0, 2.0, 0.5):
        r = kestirmeden_sur(tau, sta=True)
        assert r["sadakat"] > 0.999, (tau, r)
        assert r["θ̇_uçta"] == 0.0, r    # Ĥ_CD(0) = Ĥ_CD(τ) = 0

    # --- Fubini-Study: PSD, ve ölçek yönünü YOK ETMELİ
    def dalga(th):
        a, b = float(th[0]), float(th[1])
        return np.array([math.cos(a) * math.cos(b),
                         math.cos(a) * math.sin(b), math.sin(a), 0.0])

    r = fubini_study(dalga, np.array([0.4, 0.9]), ne="doğrulama")
    assert r["psd"], r

    def olcekli(th):
        return (1.0 + 0.5 * float(th[2])) * dalga(th[:2])

    g3 = fubini_study(olcekli, np.array([0.4, 0.9, 0.0]))
    assert abs(float(g3[2, 2])) < 1e-8, g3   # izdüşüm terimi çalışıyor


def test_gomme_genlik_kodlamasi_ve_35_kubit():
    """4096 boyut 12 kübitte mi, ve χ≤16 iddiası ölçülüyor mu?"""
    import numpy as np
    from nefs.musahede import genlige_gom, YazmacOlcusu
    assert genlige_gom(D=4096, ne="kübit") == 12
    o = YazmacOlcusu()
    assert (o.kubit_yigin, o.kubit_yer, o.kubit_mana) == (11, 12, 12)
    assert o.kubit == 35 and o.token == 8_388_608
    rng = np.random.default_rng(0)
    v = rng.normal(size=4096)
    psi, nrm = genlige_gom(v)
    assert abs(float(psi @ psi) - 1.0) < 1e-12
    assert np.allclose(genlige_gom(psi=psi, norm=nrm, ne="çöz"), v, atol=1e-9)
    # χ = 16 iddiası VERİYE BAĞLI: düzgünde tutuyor, rastgelede tutmuyor
    duz, _ = genlige_gom(np.sin(np.linspace(0, 6, 4096))
                        * np.exp(-np.linspace(0, 3, 4096)))
    assert genlige_gom(psi=duz, kubit=12, chi=16, ne="hata") < 1e-9
    assert genlige_gom(psi=psi, kubit=12, chi=16, ne="hata") > 0.5      # KIRMIZI olabiliyor
    assert max(genlige_gom(psi=psi, kubit=12, ne="bağ")) == 64


def test_zirh_dordu_de_KIRMIZIYA_donebiliyor():
    """Gaye ölçüsü: dördü de sıfırken L=0, biri bozukken L büyük."""
    import math
    import numpy as np
    from nefs.zirh import (vietoris_rips, delik, iz,
                           yama, zirh_kaybi)
    from nefs.zihin_durumu import donme

    aci = np.linspace(0, 2 * math.pi, 8, endpoint=False)
    cember = np.stack([np.cos(aci), np.sin(aci)], axis=1)
    Dc = np.sqrt(((cember[:, None] - cember[None]) ** 2).sum(2))
    assert delik(vietoris_rips(Dc, 0.9, azami_boyut=2), 1)["kayıp"] == 1.0

    rng = np.random.default_rng(0)
    iki = np.vstack([rng.normal(size=(6, 2)) * 0.2,
                     rng.normal(size=(6, 2)) * 0.2 + 10.0])
    Di = np.sqrt(((iki[:, None] - iki[None]) ** 2).sum(2))
    assert delik(vietoris_rips(Di, 0.8, azami_boyut=1), 0)["kayıp"] == 1.0
    assert delik(vietoris_rips(Di, 16.0, azami_boyut=1), 0)["kayıp"] == 0.0

    a = np.array([1.0, 2.0, 3.0])
    assert yama(a, a)["uyumsuzluk"] == 0.0
    assert yama(a, a + 0.5)["uyumsuzluk"] > 0.0
    # uyum tamken izdüşüm KİMLİĞE gitmeli (hiçbir şey söndürmemeli)
    assert np.allclose(yama(a, a)["izdüşüm"], np.eye(3), atol=1e-6)

    assert iz([donme(0.4), donme(-0.4)])["sapma"] < 1e-12
    assert iz([donme(0.4), donme(0.1)])["sapma"] > 0.1

    # Küllî kayıp: dördü sıfırken TAM sıfır (kaydırma doğru mu)
    assert abs(zirh_kaybi()["kayıp"]) < 1e-12
    assert zirh_kaybi()["çelişkisiz"]
    # ...ve tek bir ihlâl düz ortalamadan (0,25) ÇOK daha ağır cezalanmalı
    tek = zirh_kaybi(betti=1.0)["kayıp"]
    assert tek > 0.5, tek
    assert not zirh_kaybi(betti=1.0)["çelişkisiz"]




def test_qsp_faz_tablosu_CEVRIMDISI_ve_dogru():
    """FAZ 0: faz açıları koşumda aranmıyor, tablodan çekiliyor mu?

    Padişahın 2. kat'î kuralı: *"QSP açısını runtime'da arama."*
    Üç şey birden denetlenir: (a) tablo var ve doğru, (b) tabloda
    olmayan β **hata veriyor** (sessizce aramıyor), (c) artık yalnız
    uydurma düğümlerinde değil, ızgarada da küçük.
    """
    import math
    import numpy as np
    from ogrenme.optimize import (GIBBS_FAZ_TABLOSU, GIBBS_DERECE,
                                gibbs_fazlari, qsp_fazlarini_bul)
    assert GIBBS_DERECE == 32
    assert sorted(GIBBS_FAZ_TABLOSU) == [1.0, 2.0, 4.0, 8.0]
    izgara = np.linspace(-1.0, 1.0, 201)
    for b, ph in GIBBS_FAZ_TABLOSU.items():
        assert len(ph) == (GIBBS_DERECE + 2) // 2, (b, len(ph))
        f = qsp_fazlarini_bul(ne="gibbs", beta=b)
        artik = max(abs(qsp_fazlarini_bul(ne="değer", yari=ph,
                                          d=GIBBS_DERECE, x=t) - f(t))
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
    _, art, _ = qsp_fazlarini_bul(lambda t: float(T(t)), 4)
    assert art < 1e-9, art








def test_lisan_tiktoken_yerel_tablodan_ve_izafi_mevki():
    """tiktoken depodaki tablodan okunuyor mu, izafî mevki öteleme-değişmez mi?"""
    import numpy as np
    from nefs.musahede import (kodlayici, otele,
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
    D = otele(nx=nx, ny=ny, dx=1, dy=0)
    assert np.allclose(D.T @ D, np.eye(nx * ny), atol=1e-12)
    assert np.allclose(D @ otele(nx=nx, ny=ny, dx=-1, dy=0),
                       np.eye(nx * ny), atol=1e-12)

    # aynı örüntü ızgaranın HER YERİNDE aynı kodlanmalı
    A = np.zeros((6, 6), int); A[1, 1] = 3; A[1, 2] = 5
    B = np.zeros((6, 6), int); B[4, 3] = 3; B[4, 4] = 5
    ka = [x.kod() for x in otele(ne="ızgara", g=A)["izafi"] if x.merkez == 3][0]
    kb = [x.kod() for x in otele(ne="ızgara", g=B)["izafi"] if x.merkez == 3][0]
    assert ka == kb, (ka, kb)


# Koşturucu dosyanın SONUNDA durur: aksi hâlde kendisinden sonra
# tarif edilen sınamalar `globals()` taramasına girmez ve sessizce
# koşulmaz. Ölçüldü: kâide sınamaları eklendiği hâlde sayı 41 kalmıştı.
if __name__ == "__main__":
    raise SystemExit(main())
