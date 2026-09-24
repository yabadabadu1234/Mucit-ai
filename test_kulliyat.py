"""
test_kulliyat.py - Bütünleşik Doğrulama ve Teftiş Testleri
10 Faslın Riyazî ve Fikrî Kanunlarının Otomatik Doğrulanması
"""

import math
import sys
from matematik.temel import (
    KuantumDurum,
    bargmann_3_nokta,
    bargmann_n_nokta,
    hilbert_schmidt_ic_carpim,
    lie_komutator,
    rastgele_kuantum_durum
)
from nefs.mukayese import MukayeseMotoru, OntoMertebe, GeometrikDoku, AmeliVech
from nefs.vecih import VecihSpektrumu, MertebeSeviyesi
from nefs.mertebe_kesfi import MertebeKesfi
from nefs.holonomi import HolonomiAnalizoru, DevridaimCinsi
from nefs.suphe import SupheManifoldu, Iddia
from nefs.hafiza import TopolojikHafizaKovani
from nefs.rust import RustFazi


def test_1_intac_ve_bargmann():
    print("[TEST 1] n-li Bargmann ve İntaç Manifoldu...")
    motor = MukayeseMotoru(d=16)

    d1 = KuantumDurum([complex(1, 0), complex(0, 0)], etiket="p1")
    d2 = KuantumDurum([complex(0, 1), complex(0, 0)], etiket="p2")
    d3 = KuantumDurum([complex(1, 0), complex(0, 0)], etiket="p3")

    r3, phi3, delta3, ucgenler = bargmann_n_nokta([d1, d2, d3])
    assert r3 >= 0.0, "Rezonans negatif olamaz"

    intac = motor.nli_mukayese([d1, d2, d3], mertebe=OntoMertebe.MEZO_KIYAS)
    assert intac.topoloji in [GeometrikDoku.POSET, GeometrikDoku.DONGUSEL, GeometrikDoku.DIPOL, GeometrikDoku.KAFES]
    assert intac.amel in [AmeliVech.BEYAN, AmeliVech.FUNKTOR, AmeliVech.TERTIP, AmeliVech.SUKUT]
    print("  -> Başarılı: İntaç Manifoldu 4 bileşeniyle üretildi.")


def test_2_vecih_tayini_ve_j_aynasi():
    print("[TEST 2] Vecih Spektrumu, Mertebe ve J-Aynası...")
    spektrum = VecihSpektrumu()

    # Rütbe cümlesi
    vecih_rutbe, _ = spektrum.vecih_sec(["şirkette", "amir", "ve", "memur", "terfisi"])
    assert vecih_rutbe.ad == "rutbe"
    assert vecih_rutbe.mertebe == MertebeSeviyesi.KATEGORI

    # Takva cümlesi
    vecih_takva, _ = spektrum.vecih_sec(["deruni", "ihlas", "ve", "takva", "muhasebesi"])
    assert vecih_takva.ad == "takva"
    assert vecih_takva.mertebe == MertebeSeviyesi.TIP

    # J-Aynası: Madde kutbundan mana kutbuna köprü
    zit_vecih = spektrum.tomita_takesaki_zit_vecih(vecih_rutbe)
    assert zit_vecih.ad == "hakikat"
    print("  -> Başarılı: Vecih doğru izole edildi ve J-aynası köprüsü kuruldu.")


def test_3_otomatik_mertebe_kesfi():
    print("[TEST 3] Otomatik Mertebe ve Kalıcı Sinir (Persistent Nerve)...")
    kesfedici = MertebeKesfi(d=16)

    durumlar = [rastgele_kuantum_durum(16, etiket=f"d_{i}", tohum=i+10) for i in range(4)]
    aktif_mertebeler = kesfedici.aktif_mertebeleri_kesfet(durumlar)
    assert len(aktif_mertebeler) > 0

    poligonlar = kesfedici.kalici_sinir_poligonlari(durumlar, azami_n=3)
    assert isinstance(poligonlar, dict)
    print("  -> Başarılı: Aktif mertebeler ve kalıcı sinir halkaları keşfedildi.")


def test_4_holonomi_ve_yikici_girisim():
    print("[TEST 4] Wilson Döngüleri, Devridaim ve Yıkıcı Girişim...")
    analizor = HolonomiAnalizoru(d=16)
    d0 = rastgele_kuantum_durum(16, tohum=99)

    # 1. Meşru teemmül (Wilczek-Zee): Phi = 0.5 rad
    sonuc_mesru = analizor.cevirim_tahlil_et(d0, [0.25, 0.25])
    assert sonuc_mesru["devridaim_cinsi"] == DevridaimCinsi.MESRU_TEEMMUL.value
    assert not sonuc_mesru["dalga_sondu_mu"]

    # 2. Hakiki Safsata (Möbius yırtığı): Phi = pi
    sonuc_safsata = analizor.cevirim_tahlil_et(d0, [math.pi / 2.0, math.pi / 2.0])
    assert sonuc_safsata["devridaim_cinsi"] == DevridaimCinsi.HAKIKI_SAFSATA.value
    assert sonuc_safsata["dalga_sondu_mu"]
    print("  -> Başarılı: Meşru teemmül korundu; hakiki tenakuz yıkıcı girişimle söndürüldü.")


def test_5_hafiza_re_gluing():
    print("[TEST 5] Epistemik Refactoring ve Sheaf Re-Gluing...")
    hafiza = TopolojikHafizaKovani()
    d_kus = rastgele_kuantum_durum(16, tohum=1)
    hafiza.ekle("Kuşlar uçar.", d_kus, lif_koordinati={"Canlı": "Kuş", "Ortam": "Hava"})

    motor = MukayeseMotoru(d=16)
    d_penguen = rastgele_kuantum_durum(16, tohum=2)
    intac = motor.nli_mukayese([d_kus, d_penguen])

    tertip = hafiza.yeniden_tertitle(
        intac=intac,
        yeni_lif_anahtari="Hareket_Ortami",
        yeni_lif_degeri="Su",
        yeni_kaziye_metni="Penguen suda yüzer."
    )
    assert tertip["islem"] == "topolojik_re_gluing"
    assert len(hafiza.kayitlar) == 2
    print("  -> Başarılı: Hafıza silinmedi; taban değişimi (f*) ile lifli saraya aktarıldı.")


def test_6_tabula_rasa_ve_rust():
    print("[TEST 6] Tabula Rasa ve Adyabatik Rüşt Geçişi...")
    rust = RustFazi(t0=10.0, tau=3.0)

    # Başlangıçta (Bebeklik): Hata fıtrata akar
    fitrat_1, hafiza_1, _ = rust.hata_dagitimi(1.0)
    assert fitrat_1 > hafiza_1

    # 25 adım sonra (Rüşt): Fıtrat kilitlenir, hata hafızaya akar
    for _ in range(25):
        rust.adim_ilerlet()
    fitrat_2, hafiza_2, _ = rust.hata_dagitimi(1.0)
    assert hafiza_2 > fitrat_2
    print("  -> Başarılı: Adyabatik faz geçişi ile fıtrat kilitlendi, terazi dokunulmaz kılındı.")


if __name__ == "__main__":
    test_1_intac_ve_bargmann()
    test_2_vecih_tayini_ve_j_aynasi()
    test_3_otomatik_mertebe_kesfi()
    test_4_holonomi_ve_yikici_girisim()
    test_5_hafiza_re_gluing()
    test_6_tabula_rasa_ve_rust()
    print("\n==========================================")
    print("  KÜLLİYAT TESTLERİNİN HEPSİ BAŞARIYLA GEÇTİ!")
    print("==========================================")
