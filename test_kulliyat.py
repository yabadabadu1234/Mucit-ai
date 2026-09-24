import math
import sys
from nefs.kuantum_idrak import (
    Qudit, Mertebe, Doku, Amel, HolonomiCinsi,
    BagimliLifliTensor, MukayeseVeHolonomi, IleriKuantumImkanlari,
    HafizaVeSupheReaktoru, TabulaRasaRust, TomitaTakesakiTodaGT,
    KuantumMantikDevresi, BirMilyonQuditZirhi, bargmann_n
)
from main.kulliyat import tum_kulliyat_getir, release_varligi_indir, Kaynak


def test_1_bargmann_intac():
    muk = MukayeseVeHolonomi(16)
    d1 = Qudit([complex(1, 0), complex(0, 0)], "d1")
    d2 = Qudit([complex(0, 1), complex(0, 0)], "d2")
    d3 = Qudit([complex(1, 0), complex(0, 0)], "d3")
    r, phi, delta, ucgenler = bargmann_n([d1, d2, d3])
    assert r >= 0.0
    intac = muk.mukayese_intac([d1, d2, d3])
    assert intac["topoloji"] in [Doku.POSET.value, Doku.DONGUSEL.value, Doku.DIPOL.value, Doku.KAFES.value, "univalence_halkasi"]


def test_2_vecih_silsile_j():
    lif = BagimliLifliTensor(16)
    tip, m, kat = lif.vecih_tayin(["amir", "memur", "terfi"])
    assert m == Mertebe.KATEGORI
    assert lif.j_aynasi("maas") == "takva"


def test_3_wilson_holonomi_girisim():
    muk = MukayeseVeHolonomi(16)
    d0 = Qudit([complex(1, 0), complex(0, 0)], "d0")
    h_mesru = muk.holonomi_teftis(d0, [0.1, 0.1])
    assert h_mesru["cins"] == HolonomiCinsi.TEEMMUL.value
    h_safsata = muk.holonomi_teftis(d0, [math.pi / 2, math.pi / 2])
    assert h_safsata["cins"] == HolonomiCinsi.SAFSATA.value
    assert h_safsata["norm"] < 1e-4


def test_4_ileri_qudit_ve_hodge():
    ileri = IleriKuantumImkanlari(16)
    d0 = Qudit([complex(1, 0), complex(0, 0)], "d0")
    hodge = ileri.hodge_de_rham_ayrisim(d0, False)
    assert hodge["hodge_laplasyen_enerjisi"] == 0.0
    zeno = ileri.kuantum_zeno_hapsi(d0, 4)
    nhse = ileri.non_hermitian_skin_effect(d0, 1)
    kato = ileri.kato_permutasyonu(d0, 1)
    ba = ileri.baker_akhiezer_teta_dalgasi(0.5)
    vac = ileri.sikistirilmis_vakum_ayna(0.5)
    assert vac.d == 16


def test_5_hafiza_sheaf_suphe():
    haf = HafizaVeSupheReaktoru(16)
    d1 = Qudit([complex(1, 0), complex(0, 0)], "d1")
    d2 = Qudit([complex(0, 1), complex(0, 0)], "d2")
    haf.kayit_ekle("Kuş uçar", d1, {"Ortam": "Hava"})
    rg = haf.sheaf_re_gluing(d1, "Ortam", "Su", "Penguen suda yüzer")
    assert rg["yeni_id"] > 0
    celiski = haf.celiski_tahkik("A", d1, "B", d2, "ev", "ev")
    assert celiski["cozum"] == "suphe_reaktoru"


def test_6_tabula_rasa_rust():
    r = TabulaRasaRust(t0=2.0, tau=1.0)
    fb, hb, _ = r.hata_bolustur(1.0)
    assert fb > hb
    r.adim = 10
    fr, hr, _ = r.hata_bolustur(1.0)
    assert hr > fr


def test_7_tomita_toda_gt():
    tt = TomitaTakesakiTodaGT(16)
    d0 = Qudit([complex(1, 0), complex(0, 0)], "d0")
    rho_mod = tt.tomita_moduler_akis(d0.rho(), t=0.5)
    assert abs(sum(rho_mod[i][i].real for i in range(len(rho_mod))) - 1.0) < 1e-4
    sirali = tt.toda_lax_sirala([0.2, 0.9, 0.4])
    assert sirali[0] >= sirali[1] >= sirali[2]
    gt = tt.gelfand_tsetlin_branching("varlik")
    assert len(gt) > 0


def test_8_kuantum_mantik_ve_sadakat():
    man = KuantumMantikDevresi(16)
    s = Qudit([complex(1, 0)], "s")
    m = Qudit([complex(1, 0)], "m")
    p = Qudit([complex(1, 0)], "p")
    barbara = man.silojizma_barbara(s, m, p)
    assert barbara["sadakat_korundu"]
    assert barbara["hadd_i_evsat_tasfiye"] is not None
    munf = man.munfasila_bell_cikarim(s, p, p_var_mi=True)
    assert munf["usul"] == "Munfasila_Kiyas"
    nyaya = man.nyaya_pancavayava("Ateş", "Duman", "Mutfak")
    assert "mühürlendi" in nyaya["nigamana"]
    modal = man.modal_kripke_teftis(s)
    assert modal["imkan_elmas"]


def test_9_bir_milyon_qudit_zirhi():
    zirh_veri = BirMilyonQuditZirhi(N=1048576, q=64)
    zirh_param = BirMilyonQuditZirhi(N=1048576, q=64)
    assert zirh_veri.N == 1048576
    assert zirh_veri.mahalli_serbestlik == 2097152
    d1 = Qudit([complex(1, 0), complex(0, 0)], "d1")
    d2 = Qudit([complex(0, 1), complex(0, 0)], "d2")
    zirh_veri.aktif_yerlestir([d1, d2], baslangic=0)
    zirh_param.aktif_yerlestir([d1, d2], baslangic=0)
    analiz = zirh_veri.seyirci_analizi()
    assert analiz["aktif_qudit"] == 2
    assert analiz["seyirci_qudit"] == 1048574
    assert analiz["seyirci_ic_carpim_norm"] == 1.0
    tetabuk = zirh_veri.kapi_51_tetabuk(51)
    assert tetabuk["kapi_adedi"] == 51
    assert tetabuk["seyirci_dokunulmayan"] == 1048576 - 102
    kenet = zirh_param.cift_yazmac_kenet(zirh_veri)
    assert kenet["ortak_aktif_boyut"] == 2
    assert kenet["seyirci_eslesme"] == 1.0
    fs = zirh_veri.fubini_study_mesafe(zirh_param)
    assert fs < 1e-5
    kan_psi = zirh_veri.kan_genlik_hesapla()
    assert abs(abs(kan_psi) - 1.0) < 1e-4
    v_seyirci = zirh_veri.durum_oku(999999)
    assert v_seyirci.etiket == "seyirci_vakum_999999"


def test_10_kulliyat_ve_release_hatti():
    katalog = tum_kulliyat_getir()
    assert len(katalog) >= 40
    releases = [k for k in katalog if k.kategori == "release_koprusu"]
    assert len(releases) >= 8
    # Test release downloading / streaming pipeline
    test_rel = releases[0]
    yol = release_varligi_indir(test_rel)
    assert yol is not None


if __name__ == "__main__":
    test_1_bargmann_intac()
    test_2_vecih_silsile_j()
    test_3_wilson_holonomi_girisim()
    test_4_ileri_qudit_ve_hodge()
    test_5_hafiza_sheaf_suphe()
    test_6_tabula_rasa_rust()
    test_7_tomita_toda_gt()
    test_8_kuantum_mantik_ve_sadakat()
    test_9_bir_milyon_qudit_zirhi()
    test_10_kulliyat_ve_release_hatti()
    print("ALL_TESTS_PASSED")
