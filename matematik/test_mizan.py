"""mizan test takımı.

Üç kat:

* **Sözleşme** — kurucuların ve veri yapılarının vaat ettiği şeyler
  (hash-consing, önbellek doğruluğu, sınır hâlleri).
* **Riyâzî hüviyet** — ispatı bilinen özdeşlikler; bunlar geçmezse
  modülün hesabı yanlıştır, tercih meselesi değildir.
* **Çapraz sağlama** — aynı hakikate iki ayrı yoldan varıp sonuçları
  karşılaştırmak (tablo ↔ LK, kıyas ↔ önerme mantığı, t-norm ↔ kalıntı).

Çalıştırma:  ``python3 -m pytest mizan/test_mizan.py -q``
"""

from __future__ import annotations

import itertools
import random

import pytest

from matematik import mizan as alt
from matematik import mizan
cikarim = cokdegerli = istikra = kiplik = kiyas = munazara = mizan
from matematik.mizan import (Tablo, deg, degil, denk_mi, dogru, gecerli_mi, ise,
                          karsi_ornek, tablo_boyu, totoloji_mi, tutarli_mi, ve,
                          veya, xor, yanlis, ancak)

A, B, C, D = deg("A"), deg("B"), deg("C"), deg("D")


# ══════════════════════════════════════════════════════════════════════
#  1. Önerme: hash-consing ve bit-paralel tablo
# ══════════════════════════════════════════════════════════════════════

def test_hash_consing_ayni_nesneyi_verir():
    assert ve(A, B) is ve(A, B)
    assert degil(ve(A, B)) is degil(ve(A, B))
    assert ve(A, B) is not ve(B, A)      # sıra farkı ayrı düğümdür


def test_hash_consing_alt_formulu_paylasir():
    once = tablo_boyu()
    f = ve(ise(A, B), ise(A, B))
    sonra = tablo_boyu()
    # ise(A,B) zaten kurulmuş olabilir; yeni düğüm sayısı en çok 1 (VE).
    assert sonra - once <= 1
    assert f.altlar[0] is f.altlar[1]


def test_degisken_sutunu_kaba_kuvvetle_birebir_ayni():
    """Katlamalı sütun üretimi, tanımın kendisiyle bit bit karşılaştırılır."""
    for n in range(1, 9):
        adlar = [f"v{i}" for i in range(n)]
        t = Tablo(adlar)
        for k in range(n):
            hesap = t.sutun(deg(t.degiskenler[k]))
            # Tanım: satır j'de v_k'nin değeri, j'nin ilgili biti.
            kaba = 0
            for j in range(1 << n):
                if (j >> k) & 1:
                    kaba |= 1 << j
            assert hesap == kaba, f"n={n} k={k}"


def test_totoloji_ve_tutarlilik_sinir_halleri():
    assert totoloji_mi(dogru())
    assert not totoloji_mi(yanlis())
    assert tutarli_mi(dogru())
    assert not tutarli_mi(yanlis())
    assert totoloji_mi(veya(A, degil(A)))
    assert not tutarli_mi(ve(A, degil(A)))


def test_de_morgan_ve_ceviri_ozdeslikleri():
    assert denk_mi(degil(ve(A, B)), veya(degil(A), degil(B)))
    assert denk_mi(degil(veya(A, B)), ve(degil(A), degil(B)))
    assert denk_mi(ise(A, B), veya(degil(A), B))
    assert denk_mi(xor(A, B), ve(veya(A, B), degil(ve(A, B))))
    assert denk_mi(ancak(A, B), degil(xor(A, B)))


def test_karsi_ornek_gercekten_karsi_ornektir():
    """Verilen değerlendirme öncülleri doğrulayıp neticeyi yalanlamalı."""
    onc, net = [ise(A, B), B], A          # tâlîyi vaz' — geçersiz
    ko = karsi_ornek(onc, net)
    assert ko is not None
    # Elle yerine koy:
    a, b = ko["A"], ko["B"]
    assert ((not a) or b) and b           # öncüller doğru
    assert not a                          # netice yanlış


def test_gecerli_kiyasta_karsi_ornek_yoktur():
    assert karsi_ornek([ise(A, B), A], B) is None


# ══════════════════════════════════════════════════════════════════════
#  2. Kıyas — 256 modelle tam karar
# ══════════════════════════════════════════════════════════════════════

def test_gecerli_darb_sayisi_15_ve_24():
    varliksiz = kiyas.gecerli_darblar()
    varlikli = kiyas.gecerli_darblar(bos_olmayan=(kiyas.S, kiyas.M, kiyas.P))
    assert len(varliksiz) == 15
    assert len(varlikli) == 24
    assert set(varliksiz) < set(varlikli)


def test_yirmi_dort_darbin_hepsinin_adi_var():
    varlikli = kiyas.gecerli_darblar(bos_olmayan=(kiyas.S, kiyas.M, kiyas.P))
    for sekil, darb in varlikli:
        assert (sekil, darb) in kiyas.DARB_ADI, (sekil, darb)


def test_barbara_gecerli_varlik_faraziyesi_istemez():
    assert kiyas.gecerli_mi(1, "AAA")
    assert kiyas.asgari_varlik_faraziyesi(1, "AAA") == frozenset()


def test_bamalip_P_terimini_ister():
    """T79'un tashihi: Bamalip'in ihtiyacı S veya M değil, **P**'dir."""
    assert not kiyas.gecerli_mi(4, "AAI")
    assert kiyas.gecerli_mi(4, "AAI", bos_olmayan=(kiyas.P,))
    assert kiyas.asgari_varlik_faraziyesi(4, "AAI") == frozenset({kiyas.P})


def test_darapti_M_ister_barbari_S_ister():
    assert kiyas.asgari_varlik_faraziyesi(3, "AAI") == frozenset({kiyas.M})
    assert kiyas.asgari_varlik_faraziyesi(1, "AAI") == frozenset({kiyas.S})


def test_gecersiz_darbin_karsi_modeli_vardir():
    for sekil, darb in kiyas.butun_darblar():
        if not kiyas.gecerli_mi(sekil, darb):
            assert kiyas.karsi_model(sekil, darb) is not None


# ══════════════════════════════════════════════════════════════════════
#  3. Çıkarım — Hilbert, LK, G4ip
# ══════════════════════════════════════════════════════════════════════

def test_ozdeslik_turetimi_denetlenir():
    """A→A'nın beş satırlık Hilbert ispatı denetçiden geçmeli."""
    assert cikarim.hilbert_denetle(cikarim.ozdeslik_turetimi(A)) is ise(A, A)


def test_hilbert_denetci_totolojiyi_bedava_kabul_etmez():
    """Denetçi 'totoloji mi' diye bakmaz, ŞEMA ÖRNEĞİ mi diye bakar."""
    peirce = ise(ise(ise(A, B), A), A)     # totoloji, ama aksiyom örneği değil
    assert totoloji_mi(peirce)
    with pytest.raises(cikarim.HilbertHatasi):
        cikarim.hilbert_denetle([("aks", peirce)])


@pytest.mark.parametrize("ad,f,klasik,sezgisel", [
    ("Peirce", ise(ise(ise(A, B), A), A), True, False),
    ("üçüncü hâlin imtinâı", veya(A, degil(A)), True, False),
    ("çift nefyin kaldırılması", ise(degil(degil(A)), A), True, False),
    ("A→¬¬A", ise(A, degil(degil(A))), True, True),
    ("ex falso", ise(ve(A, degil(A)), B), True, True),
    ("modus tollens", ise(ve(ise(A, B), degil(B)), degil(A)), True, True),
])
def test_klasik_sezgisel_ayrimi(ad, f, klasik, sezgisel):
    assert cikarim.lk_ispatlanabilir([], [f]) is klasik, ad
    assert cikarim.sezgisel_ispatlanabilir([], f) is sezgisel, ad


def test_sezgisel_ispatlanabilir_ise_klasik_de_ispatlanabilir():
    """LJ ⊆ LK — rastgele formüllerde ölçülür, varsayılmaz."""
    rast = random.Random(20260824)
    atomlar = [A, B, C]
    for _ in range(300):
        f = _rastgele_formul(rast, atomlar, 3)
        if cikarim.sezgisel_ispatlanabilir([], f):
            assert cikarim.lk_ispatlanabilir([], [f]), f


def _rastgele_formul(r, atomlar, derinlik):
    if derinlik == 0 or r.random() < 0.3:
        return r.choice(atomlar)
    k = r.choice(("degil", "ve", "veya", "ise"))
    if k == "degil":
        return degil(_rastgele_formul(r, atomlar, derinlik - 1))
    s = _rastgele_formul(r, atomlar, derinlik - 1)
    t = _rastgele_formul(r, atomlar, derinlik - 1)
    return {"ve": ve, "veya": veya, "ise": ise}[k](s, t)


def test_lk_ile_dogruluk_tablosu_capraz_saglama():
    """Aynı hakikate iki ayrı yol: ispat araması ve tablo. Uyuşmalılar."""
    rast = random.Random(11)
    atomlar = [A, B, C]
    totoloji_sayisi = 0
    for _ in range(600):
        f = _rastgele_formul(rast, atomlar, 3)
        t = totoloji_mi(f)
        totoloji_sayisi += t
        assert cikarim.lk_ispatlanabilir([], [f]) is t, f
    assert totoloji_sayisi > 0, "hiç totoloji denenmemiş — sağlama boş"


def test_lk_oncullu_sekanslarda_da_uyusur():
    rast = random.Random(7)
    atomlar = [A, B, C]
    for _ in range(200):
        onc = [_rastgele_formul(rast, atomlar, 2) for _ in range(2)]
        net = _rastgele_formul(rast, atomlar, 2)
        assert cikarim.lk_ispatlanabilir(onc, [net]) is gecerli_mi(onc, net)


# ══════════════════════════════════════════════════════════════════════
#  4. Kiplik — çerçeve karşılıkları
# ══════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("ad", ["K", "T", "4", "5", "B", "D"])
def test_cerceve_karsiliklari_tam_isabet(ad):
    """Her şema, karşılık gelen şartı sağlayan çerçevelerde TAM olarak geçerli.

    'Tam isabet' iki yönlüdür: şartlı çerçevelerin hepsinde geçerli **ve**
    şartsızların hiçbirinde geçerli değil.  Tek yön yeterli olsaydı
    ``⊤`` da her şemayı 'doğrulardı'.
    """
    r = kiplik.karsilik_dogrula(ad, n=3)
    assert r["karşılık_tam"] is True
    assert r["ayrık_örnek"] == []          # tek bir ayrık çerçeve bile yok
    assert r["aksiyom_geçerli"] == r["şartı_sağlayan"] > 0
    assert r["çerçeve_sayısı"] == 512


def test_uc_dunyada_512_cerceve():
    assert len(kiplik.butun_cerceveler(3)) == 512


def test_dual_ozdeslikleri():
    for ad, ok in kiplik.dual_ozdeslikleri(3).items():
        assert ok, ad


def test_deontik_D_celisen_vecibeyi_engeller():
    r = kiplik.deontik_tutarlilik(3)
    assert r["seri_çerçevede_çelişkili_ödev"] == 0
    assert r["seri_olmayanda_çelişkili_ödev"] > 0
    assert r["D_çelişkili_ödevi_engelliyor"] is True
    assert r["Pm_ve_F_dualleri"] is True


def test_ltl_ozdeslikleri():
    for ad, ok in kiplik.ltl_ozdeslikleri(L=6, deneme=300, tohum=3).items():
        assert ok, ad


# ══════════════════════════════════════════════════════════════════════
#  5. Çok değerli — t-norm, kalıntı, LP
# ══════════════════════════════════════════════════════════════════════

TNORMLAR = {
    "Łukasiewicz": cokdegerli.t_lukasiewicz,
    "Gödel": cokdegerli.t_godel,
    "çarpım": cokdegerli.t_carpim,
    "nilpotent-min": cokdegerli.t_nilpotent_minimum,
    "Schweizer–Sklar p=2": cokdegerli.t_schweizer_sklar(2.0),
    "Schweizer–Sklar p=-1": cokdegerli.t_schweizer_sklar(-1.0),
    "Yager p=2": cokdegerli.t_yager(2.0),
    "Dombi p=1": cokdegerli.t_dombi(1.0),
    "zayıf (drastic)": cokdegerli.t_zayif,
}


@pytest.mark.parametrize("ad", sorted(TNORMLAR))
def test_tnorm_aksiyomlari(ad):
    r = cokdegerli.tnorm_aksiyomlari(TNORMLAR[ad], n=11)
    for aksiyom, ok in r.items():
        if isinstance(ok, bool):            # sayısal alanlar hüküm değil
            assert ok, f"{ad}: {aksiyom}"
    assert r["t-normu"] is True


@pytest.mark.parametrize("ad,T,I", [
    ("Łukasiewicz", cokdegerli.t_lukasiewicz, cokdegerli.i_lukasiewicz),
    ("Gödel", cokdegerli.t_godel, cokdegerli.i_godel),
    ("çarpım", cokdegerli.t_carpim, cokdegerli.i_carpim),
    ("nilpotent-min", cokdegerli.t_nilpotent_minimum,
     cokdegerli.i_nilpotent_minimum),
])
def test_kalinti_ozdesligi(ad, T, I):
    """``a⊗b ≤ c ⟺ a ≤ (b→c)`` — t-norm ile imâ aynı cebirden mi?"""
    r = cokdegerli.kalinti_saglaniyor_mu(T, I, n=15)
    assert r["sağlanıyor"] is True, f"{ad}: {r['ilk_ihlal']}"
    assert r["ihlal_sayısı"] == 0


def test_lukasiewicz_imasi_min_ile_bozulur():
    """T89: Łukasiewicz imâsının eşi ``min`` değil, ``max(0,a+b−1)``'dir."""
    r = cokdegerli.lukasiewicz_min_ile_bozulur(n=21)
    assert r["⊗ = max(0,a+b−1) ile kalıntı sağlanıyor"] is True
    assert r["⊗ = min ile kalıntı sağlanıyor"] is False
    assert r["min ile ihlal sayısı"] > 0
    assert r["min ile ilk ihlal (a,b,c)"] is not None


def test_lp_patlamaz_ama_secilen_degerlere_bagli():
    r = cokdegerli.lp_patlamiyor()
    assert r["LP'de A,¬A ⊨ B"] is False          # patlamıyor
    assert r["klasik belirlenmişle A,¬A ⊨ B"] is True   # klasikte patlıyor
    assert r["önemsizleşmiyor"] is True
    assert r["tanık (A,B) değerleri"] is not None


def test_syadvada_yedi_mod_tam_ve_tekrarsiz():
    r = cokdegerli.syadvada_tamlik()
    assert r["mod_sayısı"] == 7 == r["2³−1"]
    assert r["tam_ve_tekrarsız"] is True
    assert len(cokdegerli.syadvada_modlari()) == 2 ** 3 - 1


# ══════════════════════════════════════════════════════════════════════
#  6. Yapısal-altı ve kuantum
# ══════════════════════════════════════════════════════════════════════

def test_yapisal_kural_hassasiyeti():
    X, Y = alt.atom("A"), alt.atom("B")
    zayif = alt.lollipop(X, alt.lollipop(Y, X))     # zayıflatma ister
    buzul = alt.lollipop(X, alt.tensor(X, X))       # büzülme ister
    ne_ne = alt.lollipop(alt.tensor(X, alt.lollipop(X, Y)), Y)

    assert alt.HESAPLAR["doğrusal"].ispatlanabilir((), zayif) is False
    assert alt.HESAPLAR["affine"].ispatlanabilir((), zayif) is True
    assert alt.HESAPLAR["sıkı"].ispatlanabilir((), zayif) is False

    assert alt.HESAPLAR["doğrusal"].ispatlanabilir((), buzul) is False
    assert alt.HESAPLAR["sıkı"].ispatlanabilir((), buzul) is True
    assert alt.HESAPLAR["affine"].ispatlanabilir((), buzul) is False

    for h in alt.HESAPLAR.values():
        assert h.ispatlanabilir((), ne_ne) is True


def test_onbellek_hukmu_degistirmiyor():
    """Bütçeye göre anahtarlanan önbellek, önbelleksiz hesapla aynı olmalı."""
    X, Y = alt.atom("A"), alt.atom("B")
    ornekler = [
        alt.lollipop(X, X),
        alt.lollipop(X, alt.lollipop(Y, X)),
        alt.lollipop(X, alt.tensor(X, X)),
        alt.lollipop(alt.tensor(X, alt.lollipop(X, Y)), Y),
        alt.lollipop(X, alt.ile(X, X)),
        alt.lollipop(X, alt.arti(X, Y)),
    ]
    for zay, buz in itertools.product((False, True), repeat=2):
        taze = [alt.Hesap(zay, buz) for _ in ornekler]   # her biri boş önbellek
        ortak = alt.Hesap(zay, buz)                      # önbellek paylaşımlı
        for h, f in zip(taze, ornekler):
            assert h.ispatlanabilir((), f) is ortak.ispatlanabilir((), f)


def test_degisken_paylasimi_gerek_ama_yeter_degil():
    X, Y = alt.atom("A"), alt.atom("B")
    paylasan_ama_ispatsiz = alt.lollipop(X, alt.lollipop(Y, X))
    assert alt.degisken_paylasimi(paylasan_ama_ispatsiz) is True
    assert alt.HESAPLAR["doğrusal"].ispatlanabilir((), paylasan_ama_ispatsiz) is False
    paylasmayan = alt.lollipop(Y, alt.lollipop(X, X))
    assert alt.degisken_paylasimi(paylasmayan) is False


def test_kuantum_dagilma_kirilir_ama_esitsizlik_daima_gecerli():
    r = alt.dagilma_kirilir()
    assert r["eşit_mi"] is False
    assert r["eşitsizlik (A∧B)∨(A∧C) ≤ A∧(B∨C)"] is True
    assert r["A∧(B∨C) boyutu"] > r["(A∧B)∨(A∧C) boyutu"]


def test_kuantum_uyumlu_halde_dagilma_geri_gelir():
    assert alt.dagilma_uyumlu_halde()["dik üçlüde eşit_mi"] is True


def test_ortomoduler_kanun_ihlalsiz():
    r = alt.ortomoduler_kanun(deneme=120, n=4, tohum=5)
    assert r["ihlal"] == 0
    assert r["denenen"] == 120
    assert r["kanun_geçerli"] is True


def test_altuzay_sinir_halleri():
    import numpy as np
    sifir = alt.AltUzay(3, np.zeros((3, 0)))
    tam = sifir.degil()
    assert sifir.boyut == 0 and tam.boyut == 3
    assert sifir.icinde_mi(tam) and not tam.icinde_mi(sifir)
    assert tam.degil().boyut == 0
    v = alt.dogru_uzay(3, [1.0, 0.0, 0.0])
    assert v.esit_mi(v.degil().degil())


# ══════════════════════════════════════════════════════════════════════
#  7. İstikrâ
# ══════════════════════════════════════════════════════════════════════

def test_ardisiklik_kaidesi_laplace_degeri():
    assert istikra.ardisiklik_kaidesi(0, 0) == pytest.approx(0.5)
    assert istikra.ardisiklik_kaidesi(1, 1) == pytest.approx(2 / 3)
    assert istikra.ardisiklik_kaidesi(5, 10) == pytest.approx(0.5)


def test_eksik_istikra_hicbir_sonlu_n_icin_yakin_vermez():
    for n in (1, 10, 100, 10_000, 10 ** 9):
        assert istikra.ardisiklik_kaidesi(n, n) < 1.0
        assert istikra.tam_istikra_mi(n, n) is False


def test_ardisiklik_dizisi_artan_ve_bire_yakinsar():
    d = istikra.ardisiklik_dizisi(50)
    assert all(d[i] < d[i + 1] for i in range(len(d) - 1))
    assert d[-1] < 1.0 and d[-1] > 0.95


def test_ardisiklik_gecersiz_girdiyi_reddeder():
    with pytest.raises(ValueError):
        istikra.ardisiklik_kaidesi(3, 2)
    with pytest.raises(ValueError):
        istikra.ardisiklik_kaidesi(1, 1, alfa=0.0)


def test_icp_sahte_yordayiciyi_eler():
    o1 = istikra.Ortam("1", tuple((float(i), float(i)) for i in range(8)),
                       tuple(2.0 * i for i in range(8)))
    o2 = istikra.Ortam("2", tuple((float(i), float(-i)) for i in range(10, 18)),
                       tuple(2.0 * i for i in range(10, 18)))
    assert istikra.degismez_kesisim([o1, o2], 2) == frozenset({0})


def test_icp_ortamlar_ayrismazsa_hukum_vermez():
    """ICP'nin gücü ortam farkından gelir; fark yoksa hüküm de yoktur."""
    ayni = tuple((float(i), float(i)) for i in range(8))
    y = tuple(2.0 * i for i in range(8))
    o1 = istikra.Ortam("1", ayni, y)
    o2 = istikra.Ortam("2", ayni, y)
    assert istikra.degismez_kesisim([o1, o2], 2) == frozenset()


def test_temsil_illete_bakar_kaba_benzerlige_degil():
    hamr = istikra.Nesne("şarap", frozenset({"üzümden", "sıvı",
                                             "sarhoş_edici", "kırmızı"}))
    nbz = istikra.Nesne("nebîz", frozenset({"hurmadan", "sıvı",
                                            "sarhoş_edici"}))
    sirke = istikra.Nesne("sirke", frozenset({"üzümden", "sıvı", "kırmızı"}))
    # Kaba benzerlikte sirke daha yakın:
    assert istikra.benzerlik(hamr, sirke) > istikra.benzerlik(hamr, nbz)
    # İllette ise hüküm tersine döner:
    h1, g1 = istikra.temsil_hukmu(hamr, nbz, ["sarhoş_edici"], True)
    h2, g2 = istikra.temsil_hukmu(hamr, sirke, ["sarhoş_edici"], True)
    assert (h1, g1) == (True, 1.0)
    assert h2 is None and g2 == 0.0


def test_temsil_illetsiz_guc_sifir():
    n = istikra.Nesne("x", frozenset({"a"}))
    assert istikra.temsil_gucu(n, n, []) == 0.0


def test_nyaya_savyabhicara_yakalanir():
    iyi = istikra.NyayaCikarim("dağ", "ateş", "duman",
                               frozenset({"mutfak"}), frozenset({"göl"}),
                               True, frozenset({"mutfak"}))
    kotu = istikra.NyayaCikarim("dağ", "ateş", "hava",
                                frozenset({"mutfak"}), frozenset({"göl"}),
                                True, frozenset({"mutfak", "göl"}))
    asiddha = istikra.NyayaCikarim("dağ", "ateş", "duman",
                                   frozenset({"mutfak"}), frozenset({"göl"}),
                                   False, frozenset({"mutfak"}))
    assert istikra.nyaya_degerlendir(iyi)["geçerli"] is True
    assert istikra.nyaya_degerlendir(kotu)["geçerli"] is False
    assert "savyabhicāra" in istikra.nyaya_degerlendir(kotu)["hata"]
    assert "asiddha" in istikra.nyaya_degerlendir(asiddha)["hata"]


def test_bes_anapodeiktos_tablo_ile_dogrulanir():
    sonuc = istikra.butun_anapodeiktoslari_dogrula()
    assert len(sonuc) == 5
    for ad, ok in sonuc:
        assert ok, ad


def test_mill_usulleri():
    vakalar = [
        (frozenset({"a", "b", "c"}), True),
        (frozenset({"a", "d", "e"}), True),
        (frozenset({"b", "d", "f"}), False),
        (frozenset({"c", "e", "f"}), False),
    ]
    assert istikra.mill_uyusma(vakalar) == frozenset({"a"})
    assert istikra.mill_ayrilik(vakalar) == frozenset({"a"})
    assert istikra.mill_birlesik(vakalar) == frozenset({"a"})


def test_mill_esdegisim_sabit_degiskende_sifir():
    assert istikra.mill_esdegisim([(1, 5), (2, 5), (3, 5)]) == 0.0
    assert istikra.mill_esdegisim([(1, 2), (2, 4), (3, 6)]) == pytest.approx(1.0)
    assert istikra.mill_esdegisim([(1, -2), (2, -4), (3, -6)]) == pytest.approx(-1.0)


# ══════════════════════════════════════════════════════════════════════
#  8. Münâzara
# ══════════════════════════════════════════════════════════════════════

def test_gazali_mizani_en_zayif_oncul():
    assert munazara.yakin_gazali([1.0, 0.6, 0.9], True) == pytest.approx(0.6)
    assert munazara.yakin_gazali([1.0, 1.0], False) == 0.0
    assert munazara.yakin_gazali([], True) == 0.0


def test_mizan_idempotent_zincir_uzunlugu_yakini_dusurmez():
    kati = [((1.0, 1.0), True)] * 50
    assert munazara.yakin_zinciri(kati) == pytest.approx(1.0)
    zayif_halka = [((1.0,), True), ((0.6,), True), ((1.0,), True)]
    assert munazara.yakin_zinciri(zayif_halka) == pytest.approx(0.6)


def test_mertebe_adlari():
    assert munazara.mertebe_adi(1.0) == "yakîn"
    assert munazara.mertebe_adi(0.8) == "zann-ı gālib"
    assert munazara.mertebe_adi(0.5) == "zan"
    assert munazara.mertebe_adi(0.3) == "şek"
    assert munazara.mertebe_adi(0.0) == "vehim"
    with pytest.raises(ValueError):
        munazara.mertebe_adi(1.5)


def test_men_dusurur_ispat_geri_getirir():
    m = munazara.Munazara((ise(A, B), A), B, (0.9, 0.8))
    assert m.hukum()["yakîn"] == pytest.approx(0.8)
    assert m.men_et(1)[0] is True
    assert m.hukum()["yakîn"] == 0.0
    assert m.hukum()["gālip"] == "muteriz"
    assert m.ispat_et(1, [ve(A, C)]) is True
    assert m.hukum()["yakîn"] == pytest.approx(0.8)
    assert m.hukum()["gālip"] == "müddeî"


def test_tekrar_i_men_reddedilir():
    m = munazara.Munazara((ise(A, B), A), B, (1.0, 1.0))
    assert m.men_et(0)[0] is True
    ok, sebep = m.men_et(0)
    assert ok is False and "tekrâr" in sebep


def test_men_olmayan_oncule_yapilmaz():
    m = munazara.Munazara((A,), A, (1.0,))
    assert m.men_et(5)[0] is False
    assert m.men_et(None)[0] is False


def test_ispat_gecersiz_delille_kabul_edilmez():
    m = munazara.Munazara((ise(A, B), A), B, (1.0, 1.0))
    m.men_et(1)
    assert m.ispat_et(1, [C]) is False      # C'den A çıkmaz
    assert m.hukum()["yakîn"] == 0.0


def test_gecerli_kiyas_nakzedilemez_gecersiz_edilir():
    saglam = munazara.Munazara((ise(A, B), A), B, (1.0, 1.0))
    bozuk = munazara.Munazara((ise(A, B), B), A, (1.0, 1.0))
    assert saglam.nakz_et()[0] is False
    mumkun, sahit = bozuk.nakz_et()
    assert mumkun is True and sahit is not None


def test_muaraza_davayi_sakit_eder():
    m = munazara.Munazara((ise(A, B), A), B, (1.0, 1.0))
    assert m.muaraza_et([C]) is False
    assert m.hukum()["yakîn"] == pytest.approx(1.0)
    assert m.muaraza_et([degil(B)]) is True
    assert m.hukum()["yakîn"] == 0.0
    assert m.hukum()["gālip"] == "muteriz"


def test_munazara_yakin_sayisi_uyusmazsa_reddeder():
    with pytest.raises(ValueError):
        munazara.Munazara((A, B), B, (1.0,))


# ══════════════════════════════════════════════════════════════════════
#  9. Raporlar çalışıyor mu (duman testi)
# ══════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("modul", [kiyas, cikarim, kiplik, cokdegerli, alt])
def test_rapor_uretiliyor(modul):
    m = modul.rapor()
    assert isinstance(m, str) and len(m) > 100
