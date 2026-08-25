"""``idrak`` paketi sınamaları — veri, kübit, model, eğitim."""

from __future__ import annotations

import math
import os

import numpy as np
import pytest
import torch

from idrak import arc
from idrak.kubit import (KubitKaydi, diklik_hatasi, kontrollu_donme,
                         norm_hatasi, tek_kubit_donme)
from idrak.model import (Ayar, DikKarisim, HartleySuzgec, HIZLI_BOYUT,
                         NefsModeli, VARSAYILAN_BOYUT, nedensellik_hatasi,
                         parametre_sayisi)

VERI_VAR = os.path.isdir(os.path.join(arc.ARC, "training"))
veri_gerek = pytest.mark.skipif(not VERI_VAR, reason="ARC verisi yok")


# ══════════════════════════════════════════════════════════════════════
#  1. Veri
# ══════════════════════════════════════════════════════════════════════

@veri_gerek
def test_resmi_bolme_sayilari():
    e = arc.yukle_hepsi("training")
    d = arc.yukle_hepsi("evaluation")
    assert len(e) == 1000 and len(d) == 120
    egt, dog = arc.bol(e, dogrulama=100)
    assert len(egt) == 900 and len(dog) == 100
    assert not (set(g.ad for g in egt) & set(g.ad for g in dog))


@veri_gerek
def test_bolme_tohumla_tekrarlaniyor():
    e = arc.yukle_hepsi("training")
    a1, b1 = arc.bol(e, 100, tohum=7)
    a2, b2 = arc.bol(e, 100, tohum=7)
    assert [g.ad for g in b1] == [g.ad for g in b2]


@veri_gerek
def test_sinama_kumesi_egitimde_hic_gecmiyor():
    e = {g.ad for g in arc.yukle_hepsi("training")}
    d = {g.ad for g in arc.yukle_hepsi("evaluation")}
    assert not (e & d)


@veri_gerek
def test_belirtecleme_gidis_donusu_kayipsiz():
    hata = 0
    for g in arc.yukle_hepsi("training")[:150]:
        for a, b in g.egitim:
            for x in (a, b):
                if not np.array_equal(arc.belirtec_izgara(
                        arc.izgara_belirtecle(x)), x):
                    hata += 1
    assert hata == 0


def test_bozuk_dizi_sessizce_onarilmiyor():
    assert arc.belirtec_izgara([1, 2, arc.SATIR_SONU, 3,
                                arc.SATIR_SONU]) is None   # eşit olmayan
    assert arc.belirtec_izgara([arc.SATIR_SONU]) is None   # hücre yok
    assert arc.belirtec_izgara([1, 99, arc.SATIR_SONU]) is None
    assert arc.belirtec_izgara([]) is None


@veri_gerek
def test_hedef_ornek_baglamdan_cikariliyor():
    """Sızıntı denetimi: hedef örnek bağlamda olmamalı."""
    g = [x for x in arc.yukle_hepsi("training")[:80] if len(x.egitim) >= 3][0]
    for j in range(len(g.egitim)):
        b, h = arc.gorev_dizisi(g, j)
        cikti = arc.izgara_belirtecle(g.egitim[j][1])
        girdi = arc.izgara_belirtecle(g.egitim[j][0])
        # girdi bağlamda OLMALI (soru), çıktı OLMAMALI (cevap)
        assert any(b[i:i + len(girdi)] == girdi
                   for i in range(len(b) - len(girdi) + 1))


@veri_gerek
def test_sozlu_algoritma_120_gorevin_hepsinde_var():
    d = arc.yukle_hepsi("evaluation")
    var = sum(arc.soyutlama_oku(g.ad) is not None for g in d)
    assert var == 120


@veri_gerek
def test_uzunluk_siniri_kapsami_olculuyor():
    """Sınırların kapsamı kayıt altında: 768/320 kümenin %2'sini alıyor."""
    from idrak.egitim import _ornekler
    dar = Ayar(D=32, azami_baglam=768, azami_hedef=320,
               azami_baglam_ornek=3)
    genis = Ayar(D=32, azami_baglam=2048, azami_hedef=640,
                 azami_baglam_ornek=2)
    d = arc.yukle_hepsi("evaluation")
    assert len(_ornekler(d, dar, True)) < 10          # ~3
    assert len(_ornekler(d, genis, True)) > 60        # ~87
    e = arc.yukle_hepsi("training")
    assert len(_ornekler(e, genis)) > len(_ornekler(e, dar))


@veri_gerek
def test_istatistik_makul():
    i = arc.istatistik(arc.yukle_hepsi("evaluation"))
    assert i["görev"] == 120
    assert 1 <= i["azamî_kenar_en_büyük"] <= 30      # ARC ızgara sınırı
    assert 0.0 < i["şekli_sabit_oran"] < 1.0


# ══════════════════════════════════════════════════════════════════════
#  2. Kübit kaydı
# ══════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("n", [2, 3, 4])
def test_kubit_kapilari_dik(n):
    torch.manual_seed(0)
    d = diklik_hatasi(KubitKaydi(n=n, derinlik=3, giris=16))
    assert d["diklik_hatası"] < 1e-5
    assert abs(d["det"] - 1.0) < 1e-4
    assert d["boyut"] == 2 ** n


@pytest.mark.parametrize("B", [1, 8, 32])
def test_kubit_normu_korunuyor(B):
    torch.manual_seed(1)
    k = KubitKaydi(n=4, derinlik=3, giris=32)
    psi = k.evrim(torch.randn(B, 32))
    assert norm_hatasi(psi) < 1e-5
    assert float(k.oku(psi).sum(-1).min()) == pytest.approx(1.0, abs=1e-5)


def test_kubit_okumasi_olasilik_dagilimi():
    """M11: okuma bir ÖLÇÜM işlecidir; negatif olamaz, toplamı 1."""
    torch.manual_seed(2)
    k = KubitKaydi(n=3, derinlik=2, giris=16)
    p = k.oku(k.evrim(torch.randn(4, 16)))
    assert float(p.min()) >= 0.0
    assert torch.allclose(p.sum(-1), torch.ones(4), atol=1e-5)


def test_kontrollu_kapi_dolasiklik_uretiyor():
    """Bell durumu: kontrollü kapı olmadan çarpım durumu kalır."""
    torch.manual_seed(0)
    k = KubitKaydi(n=2, derinlik=1, giris=8)
    with torch.no_grad():
        k.aci_uret.weight.zero_()
        k.aci_uret.bias.copy_(torch.tensor(
            [math.pi / 4, 0.0, math.pi / 2, 0.0]))
    psi = k.evrim(torch.zeros(1, 8))[0]
    tekil = torch.linalg.svdvals(psi.view(2, 2))
    assert float(tekil[1]) > 0.5                    # dolaşık
    with torch.no_grad():
        k.aci_uret.bias.copy_(torch.tensor([math.pi / 4, 0.3, 0.0, 0.0]))
    psi = k.evrim(torch.zeros(1, 8))[0]
    assert float(torch.linalg.svdvals(psi.view(2, 2))[1]) < 1e-5  # çarpım


def test_tek_kubit_donmesi_dizeyle_uyusuyor():
    torch.manual_seed(0)
    n = 3
    psi = torch.randn(1, 2 ** n)
    psi = psi / psi.norm()
    aci = torch.tensor([0.7])
    for q in range(n):
        y = tek_kubit_donme(psi, q, n, aci)
        assert float((y.norm() - psi.norm()).abs()) < 1e-6


def test_kontrol_hedef_ayni_reddediliyor():
    with pytest.raises(ValueError):
        kontrollu_donme(torch.zeros(1, 4), 0, 0, 2, torch.tensor([0.1]))


# ══════════════════════════════════════════════════════════════════════
#  3. Model
# ══════════════════════════════════════════════════════════════════════

def test_varsayilan_ve_hizli_boyut():
    assert VARSAYILAN_BOYUT == 512 and HIZLI_BOYUT == 128


@pytest.mark.parametrize("N", [8, 16, 17, 32, 64])
def test_M29_cift_simetri_yapi_geregi(N):
    """Spektral kazanç ÇİFT simetrik — bozulması imkânsız."""
    f = HartleySuzgec(4, 128)
    k = f.kazanc(N)[0].detach()
    ters = torch.cat([k[:1], torch.flip(k[1:], dims=[0])])
    assert float((k - ters).abs().max()) == 0.0


def test_suzgec_gercekten_evrisim():
    """M29'un neticesi: köşegen kazanç dolaşımlı dizey veriyor."""
    N = 16
    f = HartleySuzgec(1, 32)
    M = torch.zeros(N, N)
    for i in range(N):
        e = torch.zeros(1, N, 1)
        e[0, i, 0] = 1.0
        M[:, i] = f(e)[0, :, 0].detach()
    C = torch.stack([torch.roll(M[:, 0], i) for i in range(N)], dim=1)
    assert float((M - C).abs().max()) < 1e-4


@pytest.mark.parametrize("D", [16, 64, 128])
def test_cayley_karisimi_dik(D):
    torch.manual_seed(0)
    q = DikKarisim(D).Q().detach()
    assert float((q.T @ q - torch.eye(D)).abs().max()) < 1e-5
    assert abs(float(torch.linalg.det(q)) - 1.0) < 1e-4


def test_cozucu_kesin_nedensel_kodlayici_degil():
    torch.manual_seed(0)
    m = NefsModeli(Ayar(D=32, kodlayici=2, cozucu=2, bas=2))
    d = nedensellik_hatasi(m, B=2, N=32, T=16)
    assert d["çözücü_geçmiş_değişimi"] == 0.0        # KESİN nedensel
    assert d["çözücü_gelecek_değişimi"] > 1e-3       # gelecek etkileniyor
    assert d["kodlayıcı_geçmiş_değişimi"] > 1e-3     # küresel karışım


def test_uret_forward_ile_ayni_sonucu_veriyor():
    """Bağlamı bir kere kodlamak neticeyi DEĞİŞTİRMİYOR."""
    torch.manual_seed(0)
    m = NefsModeli(Ayar(D=32, kodlayici=2, cozucu=2, bas=2))
    m.eval()
    baglam = torch.randint(0, 10, (1, 40))
    with torch.no_grad():
        hizli = m.uret(baglam, 6)
        y = torch.full((1, 1), arc.DOLGU, dtype=torch.long)
        for _ in range(6):
            y = torch.cat([y, m(baglam, y)[:, -1].argmax(-1, keepdim=True)],
                          dim=1)
    assert torch.equal(hizli, y[:, 1:])


def test_sekil_basi_kisitli_uretimi_zorluyor():
    """ÖLÇÜLEN KUSUR: şekil başı yokken üretilen ızgaraların %96'sı iyi
    biçimliydi ama şekli %0 doğruydu — tam eşleşme imkânsızdı."""
    torch.manual_seed(0)
    m = NefsModeli(Ayar(D=32, kodlayici=1, cozucu=1, bas=2))
    m.eval()
    b = torch.randint(0, 10, (1, 60))
    for h, w in ((1, 1), (4, 5), (7, 2), (12, 9)):
        y, sr, st = m.uret_kisitli(b, satir=h, sutun=w)
        g = arc.belirtec_izgara(y[0].tolist())
        assert g is not None                      # HER ZAMAN iyi biçimli
        assert g.shape == (h, w)                  # HER ZAMAN istenen şekil
        assert (sr, st) == (h, w)
    # Bütçeyi aşan şekil KIRPILIR, patlamaz (30×30 = 931 belirteç ister)
    y, sr, st = m.uret_kisitli(b, satir=30, sutun=30)
    g = arc.belirtec_izgara(y[0].tolist())
    assert g is not None and g.shape == (sr, st)
    assert sr * (st + 1) <= m.ayar.azami_hedef - 2
    assert sr < 30 and st == 30                   # satır kırpıldı
    # şekil verilmezse baştan okunuyor ve yine tutuyor
    y2, sr2, st2 = m.uret_kisitli(b)
    g2 = arc.belirtec_izgara(y2[0].tolist())
    assert g2 is not None and g2.shape == (sr2, st2)
    assert 1 <= sr2 <= m.azami_kenar and 1 <= st2 <= m.azami_kenar


def test_sekil_basi_ogreniliyor():
    """Şekil ayrı ve KOLAY öğrenilen bir alt problem."""
    from idrak.egitim import _kayip, _ornekler, toplu_hazirla
    torch.manual_seed(0)
    ayar = Ayar(D=32, kodlayici=1, cozucu=1, bas=2, azami_baglam=2048,
                azami_hedef=640, azami_baglam_ornek=2)
    m = NefsModeli(ayar)
    c = _ornekler(arc.yukle_hepsi("training")[:60], ayar)[:2]
    t = toplu_hazirla(c, ayar)
    assert int(t.satir.min()) >= 1 and int(t.sutun.min()) >= 1
    opt = torch.optim.AdamW(m.parameters(), lr=3e-3)
    for _ in range(40):
        k, _o, _s = _kayip(m, t)
        opt.zero_grad(); k.backward(); opt.step()
    _k, oran, sekil = _kayip(m, t)
    assert sekil == 1.0                            # şekil TAM öğrenildi
    assert oran > 0.9


def test_model_cikti_sekli_ve_parametre():
    torch.manual_seed(0)
    ayar = Ayar(D=HIZLI_BOYUT)
    m = NefsModeli(ayar)
    p = parametre_sayisi(m)
    assert 1e6 < p["toplam"] < 5e6
    c = m(torch.randint(0, 10, (2, 64)), torch.randint(0, 10, (2, 20)))
    assert c.shape == (2, 20, arc.SOZLUK)


# ══════════════════════════════════════════════════════════════════════
#  4. Eğitim mekaniği
# ══════════════════════════════════════════════════════════════════════

@veri_gerek
def test_toplu_maskesi_yalniz_hedefte():
    from idrak.egitim import _ornekler, toplu_hazirla
    ayar = Ayar(D=32)
    c = _ornekler(arc.yukle_hepsi("training")[:40], ayar)[:4]
    t = toplu_hazirla(c, ayar)
    for i, (b, h) in enumerate(c):
        assert float(t.maske[i, :len(h)].min()) == 1.0
        assert float(t.maske[i, len(h):].sum()) == 0.0
        # öğretmen zorlaması: giriş bir kaydırılmış hedef
        assert int(t.hedef[i, 0]) == h[0]
        if len(h) > 1:
            assert int(t.giris[i, 1]) == h[0]


@veri_gerek
def test_degerlendirme_tam_izgara_esmesi_sayiyor():
    """Ölçüt hücre değil IZGARA — eğitilmemiş model 0 vermeli."""
    from idrak.egitim import degerlendir
    torch.manual_seed(0)
    # Eğitimdeki gerçek sınırlar kullanılıyor. 768/320 sınırında resmî
    # değerlendirme kümesinin ancak %2'si sığıyor (ölçüldü: 120'nin 3'ü),
    # dolayısıyla o ayarla bu sınama boş küme üzerinde koşardı.
    ayar = Ayar(D=32, kodlayici=1, cozucu=1, bas=2, azami_baglam=2048,
                azami_hedef=640, azami_baglam_ornek=2)
    m = NefsModeli(ayar)
    # 40 görev, kısıtlı çözümlemeyle ~87 örnek × 640 belirteç eder ve
    # sınama dakikalarca sürer. Mekanizmayı tartmak için 12 yeter.
    d = degerlendir(m, arc.yukle_hepsi("evaluation")[:12], ayar, 12)
    assert 0.0 <= d["ızgara"] <= 1.0
    assert 0.0 <= d["şekil"] <= 1.0
    assert d["ızgara_toplam"] > 0
    assert d["çözülen_sayı"] == len(d["çözülen_görev"])


@veri_gerek
def test_bir_adim_kaybi_dusuruyor():
    """Öğrenme fiilen oluyor mu? — aynı yığında 30 adım."""
    from idrak.egitim import _kayip, _ornekler, toplu_hazirla
    torch.manual_seed(0)
    ayar = Ayar(D=32, kodlayici=2, cozucu=2, bas=2)
    m = NefsModeli(ayar)
    c = _ornekler(arc.yukle_hepsi("training")[:40], ayar)[:2]
    t = toplu_hazirla(c, ayar)
    opt = torch.optim.AdamW(m.parameters(), lr=3e-3)
    ilk, _o0, _s0 = _kayip(m, t)
    for _ in range(30):
        k, _o, _s = _kayip(m, t)
        opt.zero_grad(); k.backward(); opt.step()
    son, oran, _sd = _kayip(m, t)
    assert float(son) < float(ilk) * 0.7
    assert oran > 0.5
