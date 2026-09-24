import json
import math
import sys
from typing import Dict, Any, List
from nefs.kuantum_idrak import (
    Qudit, Mertebe, Doku, Amel, HolonomiCinsi,
    BagimliLifliTensor, MukayeseVeHolonomi, IleriKuantumImkanlari,
    HafizaVeSupheReaktoru, TabulaRasaRust, TomitaTakesakiTodaGT,
    KuantumMantikDevresi, BirMilyonQuditZirhi, bargmann_n
)

class CikarimHatti:
    def __init__(self, d: int = 16):
        self.d = d
        self.lif_tensöru = BagimliLifliTensor(d=d)
        self.mukayese = MukayeseVeHolonomi(d=d)
        self.ileri = IleriKuantumImkanlari(d=d)
        self.hafiza = HafizaVeSupheReaktoru(d=d)
        self.tt_toda_gt = TomitaTakesakiTodaGT(d=d)
        self.mantik = KuantumMantikDevresi(d=d)
        self.veri_zirhi = BirMilyonQuditZirhi(N=1048576, q=64)
        self.parametre_zirhi = BirMilyonQuditZirhi(N=1048576, q=64)
        self._hafiza_tohumla()

    def _hafiza_tohumla(self):
        d_kus = self.durum_uret("Kuşlar uçar.", 101)
        self.hafiza.kayit_ekle("Kuşlar uçar.", d_kus, {"Canlı": "Kuş", "Ortam": "Hava"})
        d_ates = self.durum_uret("Ateş yakar.", 102)
        self.hafiza.kayit_ekle("Ateş temas ettiği cismi yakar.", d_ates, {"Unsur": "Ateş"})

    def durum_uret(self, etiket: str, tohum: int = 0) -> Qudit:
        v = [complex(math.cos(tohum * 0.15 + j * 0.65), math.sin(tohum * 0.15 + j * 0.65)) for j in range(self.d)]
        return Qudit(v, etiket=etiket)

    def cikarim(self, girdi: str) -> Dict[str, Any]:
        kelimeler = girdi.split()
        durumlar = [self.durum_uret(w, sum(ord(c) for c in w)) for w in kelimeler]
        
        tip_ad, mertebe, kat = self.lif_tensöru.vecih_tayin(kelimeler)
        kaideler = self.lif_tensöru.kaide_istihrac(tip_ad, mertebe)
        j_zit = self.lif_tensöru.j_aynasi(tip_ad)
        
        intac = self.mukayese.mukayese_intac(durumlar)
        
        tenakuz_var = ("doğru" in girdi.lower() and "yanlış" in girdi.lower()) or "hem doğru hem yanlış" in girdi.lower()
        faz_adimi = (math.pi / max(1, len(durumlar))) if tenakuz_var else (intac["phi_n"] / max(1, len(durumlar)))
        fazlar = [faz_adimi for _ in durumlar]
        holonomi = self.mukayese.holonomi_teftis(durumlar[0], fazlar)
        
        sadakat = self.mantik.mantiga_sadakat_denetimi(intac["morfizm"].rho())
        
        s = self.durum_uret("Sokrates", 1)
        m = self.durum_uret("Insan", 2)
        p = self.durum_uret("Fani", 3)
        barbara = self.mantik.silojizma_barbara(s, m, p)
        
        munfasila = self.mantik.munfasila_bell_cikarim(durumlar[0], durumlar[-1], p_var_mi=True)
        nyaya = self.mantik.nyaya_pancavayava("Dağda ateş vardır", "Duman olduğu için", "Mutfak gibi")
        modal = self.mantik.modal_kripke_teftis(durumlar[0])
        lukasiewicz = self.mantik.lukasiewicz_surekli_cikarim(0.85, 0.90)
        
        toda_sirali = self.tt_toda_gt.toda_lax_sirala([0.3, 0.9, 0.1, 0.7])
        gt_sektor = self.tt_toda_gt.gelfand_tsetlin_branching("canli")
        tomita_rho = self.tt_toda_gt.tomita_moduler_akis(durumlar[0].rho(), t=0.2)
        
        re_gluing = None
        if "penguen" in girdi.lower():
            re_gluing = self.hafiza.sheaf_re_gluing(intac["morfizm"], "Ortam", "Su", "Penguen kuştur lakin suda yüzer.")
        
        self.veri_zirhi.aktif_yerlestir(durumlar, baslangic=0)
        param_durumlar = [self.durum_uret(f"param_{k}", (k + 1) * 31) for k in range(len(durumlar))]
        self.parametre_zirhi.aktif_yerlestir(param_durumlar, baslangic=0)
        seyirci_analiz = self.veri_zirhi.seyirci_analizi()
        tetabuk_51 = self.veri_zirhi.kapi_51_tetabuk(51)
        kenet_raporu = self.parametre_zirhi.cift_yazmac_kenet(self.veri_zirhi)
        fs_cikarim = self.veri_zirhi.fubini_study_mesafe(self.parametre_zirhi)
        kan_cikarim = self.veri_zirhi.kan_genlik_hesapla(theta=0.785)

        if tetabuk_51["sadakat"] < 0.90:
            hukum = f"[ZIRH İHLALİ] 1 Milyon Qudit zırhında 51 kapı sadakat eşiği aşılamadı ({tetabuk_51['sadakat']})."
        elif holonomi["cins"] == HolonomiCinsi.SAFSATA.value or intac["amel"] == Amel.SUKUT.value:
            hukum = "[CERH VE SÜKÛT] Möbius parite yırtığı (e^{iπ} = -I) ve yıkıcı girişim: Dalga sıfırlandı, teemmül durduruldu."
        elif intac["amel"] == Amel.BEYAN.value:
            hukum = f"[BURHÂN VE BEYAN] Kaziye tasdik edildi: '{girdi}'"
        else:
            hukum = f"[FUNKTÖRYEL KIYAS] Sol Kan Uzantısı ile zihne mühürlendi."

        return {
            "girdi": girdi,
            "vecih": {"tip": tip_ad, "mertebe": mertebe.name, "kategori": kat, "j_aynasi": j_zit},
            "kaideler": kaideler,
            "bir_milyon_qudit_zirhi": {
                "toplam_qudit": seyirci_analiz["toplam_qudit"],
                "taban_q": seyirci_analiz["taban_q"],
                "kapasite": seyirci_analiz["kapasite"],
                "mahalli_serbestlik": seyirci_analiz["mahalli_serbestlik"],
                "aktif_qudit": seyirci_analiz["aktif_qudit"],
                "seyirci_qudit": seyirci_analiz["seyirci_qudit"],
                "seyirci_ic_carpim_norm": seyirci_analiz["seyirci_ic_carpim_norm"],
                "fubini_study_mesafe": round(fs_cikarim, 4),
                "kan_genlik_norm": round(abs(kan_cikarim), 4),
                "kapi_51_tetabuk": tetabuk_51,
                "cift_yazmac_kenet": kenet_raporu,
                "temsil_nizami": "Seyirci Qudit Dekuplajı & Faktörize Mahalli Zırh (Sıfır Kesme)"
            },
            "intac_manifoldu": {
                "topoloji": intac["topoloji"],
                "amel": intac["amel"],
                "r_n": intac["r_n"],
                "phi_n": intac["phi_n"],
                "swap_p0": intac["swap_p0"],
                "swap_p1": intac["swap_p1"]
            },
            "holonomi_devridaim": {
                "cins": holonomi["cins"],
                "norm": holonomi["norm"],
                "toplam_faz": holonomi["toplam_faz"],
                "hodge_enerjisi": holonomi["hodge"],
                "hukum": holonomi["hukum"]
            },
            "mantiga_sadakat_gauge": sadakat,
            "kuantum_mantik_usulleri": {
                "barbara_aaa1": barbara["hukum"],
                "munfasila_bell": munfasila["hukum"],
                "nyaya_5_adim": nyaya["nigamana"],
                "modal_kripke": modal["hukum"],
                "lukasiewicz_v_ima": lukasiewicz["v_ima"]
            },
            "ileri_cebir": {
                "toda_lax_sirali": toda_sirali,
                "gt_alt_sektor": gt_sektor[0]["alt"],
                "tomita_moduler_iz": round(sum(tomita_rho[j][j].real for j in range(self.d)), 3)
            },
            "sheaf_re_gluing": re_gluing,
            "nihai_hukum": hukum
        }

def cikarimi_calistir(metin: str = "") -> Dict[str, Any]:
    motor = CikarimHatti(d=16)
    hedef = metin if metin else "Ahmet şirkette amir olarak Mehmet'e yetki verdi"
    return motor.cikarim(hedef)

if __name__ == "__main__":
    girdi_metin = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Penguen bir kuştur fakat suda yüzer"
    sonuc = cikarimi_calistir(girdi_metin)
    print(json.dumps(sonuc, default=str, ensure_ascii=False, indent=2))
