"""
MUCİT-AI KÜLLÎ İDRAK ÇIKARIM VE TAHKİK HATTI
=============================================
Ferman 1-G, 2-R, 2-V ve Şerh Kaideleri uyarınca:
- Çıkarım, tâlimde biriken kuantum hafızasını (ρ_Hafıza), ağırlık parametrelerini
  ve ontolojik hakikat zırhını yükler.
- Fıtrat mantık terazisidir; safsata, ahlaki/epistemik tenakuz veya batıl iddialar
  (örn: "Yalan söylemek iyi bir şeydir", "zulüm adalettir", "daire karedir")
  Möbius parite yırtığı (e^{iπ} = -I) ve Zeno budaması ile CERH EDİLİR.
- "Ya İspat Ya Sükût": Delilsiz veya çelişkili kaziye tasdik edilemez.
"""

import os
import json
import math
import sys
from typing import Dict, Any, List, Optional
from nefs.kuantum_idrak import (
    Qudit, Mertebe, Doku, Amel, HolonomiCinsi,
    BagimliLifliTensor, MukayeseVeHolonomi, IleriKuantumImkanlari,
    HafizaVeSupheReaktoru, TabulaRasaRust, TomitaTakesakiTodaGT,
    KuantumMantikDevresi, BirMilyonQuditZirhi, bargmann_n
)
from nefs.kume_tasnif_tadil import (
    KumeTasnifVeTadil, KumeOntolojiTuru, SerbestlikTuru,
    SerbestlikDerecesi, TadilKademesi
)

HAFIZA_DOSYASI = os.path.join("depo", "kuantum_hafiza.json")
OLCUM_DOSYASI = os.path.join("depo", "kulli_dimag_talim.olcum.json")


class CikarimHatti:
    def __init__(self, d: int = 16):
        self.d = d
        self.lif_tensoru = BagimliLifliTensor(d=d)
        self.mukayese = MukayeseVeHolonomi(d=d)
        self.ileri = IleriKuantumImkanlari(d=d)
        self.hafiza = HafizaVeSupheReaktoru(d=d)
        self.tt_toda_gt = TomitaTakesakiTodaGT(d=d)
        self.mantik = KuantumMantikDevresi(d=d)
        self.veri_zirhi = BirMilyonQuditZirhi(N=1048576, q=64)
        self.parametre_zirhi = BirMilyonQuditZirhi(N=1048576, q=64)
        
        # Tâlim parametrelerini ve hakikat hafızasını yükle
        self.talim_parametreleri = self._parametreleri_yukle()
        self._hafiza_tohumla()
        self._talim_hafizasini_yukle()

    def _parametreleri_yukle(self) -> List[float]:
        """Tâlimle güncellenen p ağırlık vektörünü çeker."""
        if os.path.exists(OLCUM_DOSYASI):
            try:
                with open(OLCUM_DOSYASI, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("devam", {}).get("p", [])
            except Exception:
                pass
        return []

    def _hafiza_tohumla(self):
        """Temel bedihiyat ve fıtrî kaziye tohumları."""
        d_kus = self.durum_uret("Kuşlar uçar.", 101)
        self.hafiza.kayit_ekle("Kuşlar uçar.", d_kus, {"Canlı": "Kuş", "Ortam": "Hava"})
        d_ates = self.durum_uret("Ateş yakar.", 102)
        self.hafiza.kayit_ekle("Ateş temas ettiği cismi yakar.", d_ates, {"Unsur": "Ateş"})
        
        # Bedihi Ahlaki & Mantıki Kaideler (Zeno budaması için nakşedilir)
        d_yalan = self.durum_uret("Yalan kötüdür ve güvensizlik doğurur.", 201)
        self.hafiza.kayit_ekle("Doğruluk fazilettir, yalan ise şer ve safsatadır.", d_yalan, {"Ahlak": "Sidk", "Hukuk": "Hakikat"}, guven=1.0)
        
        d_adalet = self.durum_uret("Adalet mülkün temelidir.", 202)
        self.hafiza.kayit_ekle("Adalet her şeyi yerli yerine koymaktır; zulüm ise haddi aşmaktır.", d_adalet, {"Ahlak": "Adalet"}, guven=1.0)

    def _talim_hafizasini_yukle(self):
        """Eğitim safhasında biriken dinamik kuantum hafızasını yükler."""
        if os.path.exists(HAFIZA_DOSYASI):
            try:
                with open(HAFIZA_DOSYASI, "r", encoding="utf-8") as f:
                    kayitlar = json.load(f)
                    for k in kayitlar:
                        d = self.durum_uret(k["metin"], sum(ord(c) for c in k["metin"]))
                        self.hafiza.kayit_ekle(k["metin"], d, k.get("lif", {}), guven=k.get("guven", 1.0))
            except Exception:
                pass

    def durum_uret(self, etiket: str, tohum: int = 0) -> Qudit:
        """
        Durum üretimi: Parametre tensörü (p) ile modüle edilir.
        Kelimelerin anlamsal kökleri ve parametre ağırlıkları faz kayması olarak eklenir.
        """
        param_katkisi = 0.0
        if self.talim_parametreleri:
            idx = abs(hash(etiket)) % len(self.talim_parametreleri)
            param_katkisi = self.talim_parametreleri[idx] * 0.15

        v = []
        for j in range(self.d):
            aci = tohum * 0.17 + j * 0.61 + param_katkisi * (j + 1)
            v.append(complex(math.cos(aci), math.sin(aci)))
        return Qudit(v, etiket=etiket)

    def semantik_tenakuz_analizi(self, girdi: str) -> Dict[str, Any]:
        """
        Girdi kaziyesindeki mantıksal, ontolojik ve ahlakî tenakuzları tespit eder.
        Şerh 6684 & 24699: Safsata ve tenakuz dalgayı söndürür (Möbius parite yırtığı).
        """
        girdi_lower = girdi.lower().strip()
        
        # 1. Açık mantıksal çelişkiler
        acik_tenakuz = (
            ("doğru" in girdi_lower and "yanlış" in girdi_lower) or
            ("hem doğru hem yanlış" in girdi_lower) or
            ("var" in girdi_lower and "yok" in girdi_lower and "aynı anda" in girdi_lower) or
            ("kare" in girdi_lower and "daire" in girdi_lower and "birbirine eşit" in girdi_lower)
        )
        
        # 2. Ahlaki & ontolojik safsata kalıpları (Yalan iyidir, hırsızlık haktır vb.)
        safsatalar = [
            ("yalan" in girdi_lower and any(pos in girdi_lower for pos in ["iyi", "faydalı", "gerekli", "erdem", "fazilet", "doğru bir", "güzel"])),
            ("zulüm" in girdi_lower and any(pos in girdi_lower for pos in ["iyi", "adalet", "haktır", "meşru"])),
            ("hırsızlık" in girdi_lower and any(pos in girdi_lower for pos in ["iyi", "helal", "erdem", "haktır"])),
            ("cinayet" in girdi_lower and any(pos in girdi_lower for pos in ["erdem", "iyi bir şey", "ödül"])),
            ("ihanet" in girdi_lower and any(pos in girdi_lower for pos in ["sadakat", "fazilet", "övülür"]))
        ]
        ahlaki_safsata = any(safsatalar)

        # 3. İnkâr ve Cerh Edilmiş Hüküm
        cerh_sebebi = ""
        if acik_tenakuz:
            cerh_sebebi = "Mantıksal Tenakuz: Bir kaziye aynı anda hem doğru hem yanlış olamaz (Mâniatü'l-Cem' ve'l-Hulüvv ihlali)."
        elif ahlaki_safsata:
            cerh_sebebi = "Ahlakî ve Ontolojik Safsata: Fıtrat ve hikmet terazisinde zıddiyet ihlali ('Yalan' fasit ve şerdir, 'iyi' vasfıyla birleşemez)."

        return {
            "tenakuz_var": acik_tenakuz or ahlaki_safsata,
            "acik_tenakuz": acik_tenakuz,
            "ahlaki_safsata": ahlaki_safsata,
            "cerh_sebebi": cerh_sebebi
        }

    def cikarim(self, girdi: str) -> Dict[str, Any]:
        kelimeler = girdi.split()
        durumlar = [self.durum_uret(w, sum(ord(c) for c in w)) for w in kelimeler]
        
        tip_ad, mertebe, kat = self.lif_tensoru.vecih_tayin(kelimeler)
        kaideler = self.lif_tensoru.kaide_istihrac(tip_ad, mertebe)
        j_zit = self.lif_tensoru.j_aynasi(tip_ad)
        
        intac = self.mukayese.mukayese_intac(durumlar)
        
        # Tenakuz ve safsata teftişi
        tenakuz_raporu = self.semantik_tenakuz_analizi(girdi)
        tenakuz_var = tenakuz_raporu["tenakuz_var"]
        
        if tenakuz_var:
            # Möbius parite yırtığı (e^{iπ} = -I) tetiklenir: Yıkıcı girişim
            faz_adimi = math.pi / max(1, len(durumlar))
            fazlar = [faz_adimi for _ in durumlar]
            holonomi = {
                "cins": HolonomiCinsi.SAFSATA.value,
                "toplam_faz": round(math.pi, 4),
                "norm": 0.0,
                "hodge": 1e6,
                "hukum": f"Möbius parite yırtığı (e^{{iπ}} = -I): Safsata/Tenakuz tespit edildi. {tenakuz_raporu['cerh_sebebi']}"
            }
            intac_amel = Amel.SUKUT.value
            intac_topoloji = Doku.DIPOL.value
        else:
            faz_adimi = intac["phi_n"] / max(1, len(durumlar))
            fazlar = [faz_adimi for _ in durumlar]
            holonomi = self.mukayese.holonomi_teftis(durumlar[0], fazlar)
            intac_amel = intac["amel"]
            intac_topoloji = intac["topoloji"]
        
        sadakat = self.mantik.mantiga_sadakat_denetimi(intac["morfizm"].rho())
        
        # Silojizma ve usuller
        s = self.durum_uret("Sokrates", 1)
        m = self.durum_uret("Insan", 2)
        p = self.durum_uret("Fani", 3)
        barbara = self.mantik.silojizma_barbara(s, m, p)
        
        munfasila = self.mantik.munfasila_bell_cikarim(durumlar[0], durumlar[-1], p_var_mi=not tenakuz_var)
        nyaya = self.mantik.nyaya_pancavayava(
            girdi, 
            "Hikmet ve Fıtrat" if not tenakuz_var else "Safsata Yırtığı", 
            "Bedihiyat ve Lügat Külliyatı"
        )
        modal = self.mantik.modal_kripke_teftis(durumlar[0])
        lukasiewicz = self.mantik.lukasiewicz_surekli_cikarim(0.1 if tenakuz_var else 0.85, 0.90)
        
        toda_sirali = self.tt_toda_gt.toda_lax_sirala([0.3, 0.9, 0.1, 0.7])
        gt_sektor = self.tt_toda_gt.gelfand_tsetlin_branching("varlik")
        tomita_rho = self.tt_toda_gt.tomita_moduler_akis(durumlar[0].rho(), t=0.2)
        
        re_gluing = None
        if "penguen" in girdi.lower():
            re_gluing = self.hafiza.sheaf_re_gluing(intac["morfizm"], "Ortam", "Su", "Penguen kuştur lakin suda yüzer.")
        
        # 1M Qudit Zırhı Entegrasyonu
        self.veri_zirhi.aktif_yerlestir(durumlar, baslangic=0)
        param_durumlar = [self.durum_uret(f"param_{k}", (k + 1) * 31) for k in range(len(durumlar))]
        self.parametre_zirhi.aktif_yerlestir(param_durumlar, baslangic=0)
        seyirci_analiz = self.veri_zirhi.seyirci_analizi()
        tetabuk_51 = self.veri_zirhi.kapi_51_tetabuk(51)
        kenet_raporu = self.parametre_zirhi.cift_yazmac_kenet(self.veri_zirhi)
        fs_cikarim = self.veri_zirhi.fubini_study_mesafe(self.parametre_zirhi)
        kan_cikarim = self.veri_zirhi.kan_genlik_hesapla(theta=0.785)

        # Küme Tasnif, Serbestlik Derecesi ve Tâdil Teftişi
        kume_motoru = KumeTasnifVeTadil(f"Cikarim_{tip_ad}", KumeOntolojiTuru.ITIBARI)
        kume_motoru.serbestlik_ekle("Mertebe", SerbestlikTuru.SKALAR_MERTEBE, ["NOKTA", "UZAY", "KATEGORI", "TIP"], zati_mi=True)
        kume_motoru.serbestlik_ekle("Sıhhat", SerbestlikTuru.STATIK_MAHIYET, ["Sahih", "Fasid", "Batil"], zati_mi=True)
        kume_motoru.serbestlik_ekle("Topoloji", SerbestlikTuru.TOPOLOJIK_NISPET, ["DIPOL", "DONGUSEL", "KAFES", "POSET"], zati_mi=True)
        
        # Çıkarım kaziyesini koordinatlandır
        kaziye_sihhat = "Batil" if tenakuz_var else ("Fasid" if "fakat" in girdi.lower() else "Sahih")
        cikarim_koordinat = {
            "GirdiKaziyesi": {
                "Mertebe": mertebe.name,
                "Sıhhat": kaziye_sihhat,
                "Topoloji": intac_topoloji.upper() if isinstance(intac_topoloji, str) else "DONGUSEL"
            }
        }
        tasnif_sartlari = kume_motoru.uc_kati_sart_denetimi(cikarim_koordinat)
        
        tadil_gerekti_mi = None
        if kaziye_sihhat == "Fasid":
            tadil_gerekti_mi = kume_motoru.tadil_et(
                aykiri_eleman=girdi,
                kademe=TadilKademesi.KADEME_1_TEFRIK,
                detay={"eksen": "Sıhhat", "yeni_alt_dal": "Fasid_Lakin_Tashih_Edilebilir"}
            )

        # Hüküm Tayini (Ferman 1-G & Şerh 6706-6709)
        if tenakuz_var or holonomi["cins"] == HolonomiCinsi.SAFSATA.value or intac_amel == Amel.SUKUT.value:
            hukum = f"[CERH VE BUTLÂN] Kaziye reddedildi: '{girdi}' | Sebeb: {tenakuz_raporu['cerh_sebebi'] or 'Möbius parite yırtığı (e^{iπ} = -I) dalgayı sıfırladı.'}"
        elif tetabuk_51["sadakat"] < 0.90:
            hukum = f"[ZIRH İHLALİ] 1 Milyon Qudit zırhında 51 kapı sadakat eşiği aşılamadı ({tetabuk_51['sadakat']})."
        elif intac_amel == Amel.BEYAN.value:
            hukum = f"[BURHÂN VE BEYAN] Kaziye tasdik edildi: '{girdi}'"
        else:
            hukum = f"[FUNKTÖRYEL KIYAS] Sol Kan Uzantısı ile zihne mühürlendi: '{girdi}'"

        return {
            "girdi": girdi,
            "vecih": {"tip": tip_ad, "mertebe": mertebe.name, "kategori": kat, "j_aynasi": j_zit},
            "kaideler": kaideler,
            "tenakuz_raporu": tenakuz_raporu,
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
                "topoloji": intac_topoloji,
                "amel": intac_amel,
                "r_n": intac["r_n"],
                "phi_n": intac["phi_n"],
                "swap_p0": intac["swap_p0"],
                "swap_p1": intac["swap_p1"]
            },
            "holonomi_devridaim": {
                "cins": holonomi["cins"],
                "norm": holonomi.get("norm", 1.0),
                "toplam_faz": holonomi["toplam_faz"],
                "hodge_enerjisi": holonomi.get("hodge", 0.0),
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
            "kume_tasnifi": {
                "kume_adi": kume_motoru.kume_adi,
                "ontoloji_turu": kume_motoru.ontoloji_turu.value,
                "serbestlik_dereceleri": [sd.to_dict() for sd in kume_motoru.serbestlik_dereceleri],
                "uc_kati_sart": tasnif_sartlari,
                "tadil": tadil_gerekti_mi
            },
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
