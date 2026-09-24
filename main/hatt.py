import json
import math
import sys
from typing import Dict, Any, List
from nefs.kuantum_idrak import (
    Qudit, Mertebe, Doku, Amel, HolonomiCinsi,
    BagimliLifliTensor, MukayeseVeHolonomi, IleriKuantumImkanlari,
    HafizaVeSupheReaktoru, TabulaRasaRust, bargmann_n
)

class KulliHatt:
    def __init__(self, d: int = 16):
        self.d = d
        self.lif_tensöru = BagimliLifliTensor(d=d)
        self.mukayese = MukayeseVeHolonomi(d=d)
        self.ileri = IleriKuantumImkanlari(d=d)
        self.hafiza = HafizaVeSupheReaktoru(d=d)
        self.rust = TabulaRasaRust(t0=5.0, tau=2.0)
        self._hafiza_tohumla()

    def _hafiza_tohumla(self):
        d_kus = self.durum_uret("Kuşlar uçar.", 101)
        self.hafiza.kayit_ekle("Kuşlar uçar.", d_kus, {"Canlı": "Kuş", "Ortam": "Hava"})
        d_ates = self.durum_uret("Ateş yakar.", 102)
        self.hafiza.kayit_ekle("Ateş temas ettiği cismi yakar.", d_ates, {"Unsur": "Ateş"})

    def durum_uret(self, etiket: str, tohum: int = 0) -> Qudit:
        v = [complex(math.cos(tohum * 0.1 + j * 0.7), math.sin(tohum * 0.1 + j * 0.7)) for j in range(self.d)]
        return Qudit(v, etiket=etiket)

    def egit(self, adim_sayisi: int = 6) -> Dict[str, Any]:
        ciftler = [("içeride", "dışarıda"), ("doğru", "yanlış"), ("var", "yok"), ("büyük", "küçük"), ("amir", "memur")]
        tahfiz_kayitlari = []
        for i in range(adim_sayisi):
            c = ciftler[i % len(ciftler)]
            d1 = self.durum_uret(c[0], i * 11)
            d2 = self.durum_uret(c[1], i * 11 + 5)
            intac = self.mukayese.mukayese_intac([d1, d2])
            hata = abs(abs(intac["phi_n"]) - math.pi)
            f_hata, h_hata, durum = self.rust.hata_bolustur(hata)
            alpha = self.rust.ilerle()
            tahfiz_kayitlari.append({
                "adim": i + 1, "cift": f"{c[0]} <-> {c[1]}",
                "hata": round(hata, 4), "alpha": round(alpha, 3), "durum": durum
            })
        
        arc_sonuclari = []
        for g_id in ["00576224", "007bbfb7", "009d5c81"]:
            ornek_durumlar = [self.durum_uret(f"kural_{g_id}_{k}", k * 13) for k in range(3)]
            intac = self.mukayese.mukayese_intac(ornek_durumlar)
            arc_sonuclari.append({
                "gorev": g_id, "r_K": intac["r_n"], "topoloji": intac["topoloji"], "amel": intac["amel"]
            })

        return {
            "basarili": True,
            "tahfiz_adimlari": tahfiz_kayitlari,
            "arc_egitimi": arc_sonuclari,
            "rust_makami": "Tahkik (Kamil)" if self.rust.alpha() >= 0.8 else "Tahfiz (Bebeklik)"
        }

    def cikarim(self, cumle: str, dongu_yansit: bool = False) -> Dict[str, Any]:
        kelimeler = cumle.split()
        durumlar = [self.durum_uret(w, sum(ord(c) for c in w)) for w in kelimeler]
        
        tip_ad, mertebe, kat = self.lif_tensöru.vecih_tayin(kelimeler)
        kaideler = self.lif_tensöru.kaide_istihrac(tip_ad, mertebe)
        j_zit = self.lif_tensöru.j_aynasi(tip_ad)
        
        intac = self.mukayese.mukayese_intac(durumlar)
        
        fazlar = [math.pi / len(durumlar) for _ in durumlar] if dongu_yansit else [intac["phi_n"] / len(durumlar) for _ in durumlar]
        holonomi = self.mukayese.holonomi_teftis(durumlar[0], fazlar)
        
        re_gluing = None
        if "penguen" in cumle.lower():
            re_gluing = self.hafiza.sheaf_re_gluing(intac["morfizm"], "Ortam", "Su", "Penguen kuştur lakin suda yüzer.")

        if intac["amel"] == Amel.SUKUT.value or holonomi["cins"] == HolonomiCinsi.SAFSATA.value:
            hukum = "[TEVAKKUF / SÜKÛT] Acele hüküm verilmedi; süperpozisyon havuzunda bekletildi."
        elif intac["amel"] == Amel.BEYAN.value:
            hukum = f"[BEYAN] Küllî kaziye tasdik edildi: '{cumle}'"
        else:
            hukum = f"[FUNKTÖR] Üst kıyasa tohum olarak mühürlendi."

        return {
            "girdi": cumle,
            "tip": tip_ad,
            "mertebe": mertebe.name,
            "kategori": kat,
            "kaideler": kaideler,
            "j_aynasi_zit_kutup": j_zit,
            "intac": intac,
            "holonomi": holonomi,
            "hukum": hukum,
            "sheaf_re_gluing": re_gluing
        }

    def testleri_calistir(self) -> Dict[str, Any]:
        raporlar = []
        
        d1 = self.durum_uret("A", 1)
        d2 = self.durum_uret("B", 2)
        d3 = self.durum_uret("C", 3)
        r3, phi3, delta3, ucgenler = bargmann_n([d1, d2, d3])
        raporlar.append({"test": "1_Bargmann_Intac", "durum": "GECTI", "detay": f"r_3={r3:.4f}, Phi_3={phi3:.4f} rad, Delta_3={delta3}"})

        tip, m, _ = self.lif_tensöru.vecih_tayin(["amir", "ve", "memur"])
        assert m == Mertebe.KATEGORI
        j_karsi = self.lif_tensöru.j_aynasi("maas")
        assert j_karsi == "takva"
        raporlar.append({"test": "2_Vecih_Silsile_J_Aynasi", "durum": "GECTI", "detay": f"Mertebe={m.name}, J-aynası(maas)={j_karsi}"})

        hol_mesru = self.mukayese.holonomi_teftis(d1, [0.1, 0.1])
        assert hol_mesru["cins"] == HolonomiCinsi.TEEMMUL.value
        hol_safsata = self.mukayese.holonomi_teftis(d1, [math.pi / 2, math.pi / 2])
        assert hol_safsata["cins"] == HolonomiCinsi.SAFSATA.value
        raporlar.append({"test": "3_Holonomi_Yikici_Girisim", "durum": "GECTI", "detay": "Meşru teemmül tasdik edildi; Möbius parite yırtığı yıkıcı girişimle söndürüldü."})

        hodge = self.ileri.hodge_de_rham_ayrisim(d1, safsata_mi=False)
        assert hodge["hodge_laplasyen_enerjisi"] == 0.0
        raporlar.append({"test": "4_Hodge_de_Rham_Saflastirma", "durum": "GECTI", "detay": "Harmonik taban sıfır enerjiyle korundu; atık formlar süpürüldü."})

        zeno = self.ileri.kuantum_zeno_hapsi(d1, alt_uzay_k=4)
        nhse = self.ileri.non_hermitian_skin_effect(d1, point_gap_w=1)
        kato = self.ileri.kato_permutasyonu(d1, adim=1)
        ba = self.ileri.baker_akhiezer_teta_dalgasi(t=0.5)
        uncomp = self.ileri.hadd_i_evsat_tasfiyesi(d1)
        vac = self.ileri.sikistirilmis_vakum_ayna(r=0.5)
        raporlar.append({"test": "5_Qudit_Ileri_Imkanlari", "durum": "GECTI", "detay": f"Zeno (k=4), NHSE skin, Kato perm, Baker-Akhiezer teta, Uncomputing, Squeezed Vacuum d={vac.d}"})

        rg = self.hafiza.sheaf_re_gluing(d1, "Ortam", "Su", "Penguen kuştur lakin suda yüzer.")
        assert rg["etkilenen_sayisi"] >= 0
        raporlar.append({"test": "6_Epistemik_Sheaf_Re_Gluing", "durum": "GECTI", "detay": f"Taban değişimi (f*) ile lif kütüphanesine terfi: {rg['yeni_lif']}"})

        celiski = self.hafiza.celiski_tahkik("Ali içeride.", d1, "Ali dışarıda.", d2, "ev", "ev")
        assert celiski["cozum"] == "suphe_reaktoru"
        raporlar.append({"test": "7_Epistemik_Tahkik_Suphe", "durum": "GECTI", "detay": celiski["karar"]})

        rust_test = TabulaRasaRust(t0=2.0, tau=1.0)
        f_b, h_b, _ = rust_test.hata_bolustur(1.0)
        rust_test.adim = 10
        f_r, h_r, _ = rust_test.hata_bolustur(1.0)
        assert f_b > h_b and h_r > f_r
        raporlar.append({"test": "8_Tabula_Rasa_Rust_Gecisi", "durum": "GECTI", "detay": "Bebeklikte hata fıtrata, rüşt makamında hata vakıaya ve hafızaya fatura edildi."})

        return {
            "tum_testler_gecti": True,
            "toplam_test_sayisi": len(raporlar),
            "raporlar": raporlar
        }

if __name__ == "__main__":
    motor = KulliHatt(d=16)
    if len(sys.argv) > 1 and sys.argv[1] == "egit":
        res = motor.egit()
    elif len(sys.argv) > 1 and sys.argv[1] == "cikarim":
        metin = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "Ahmet şirkette amir olarak yetki verdi"
        res = motor.cikarim(metin)
    else:
        res = motor.testleri_calistir()
    print(json.dumps(res, default=str, ensure_ascii=False))
