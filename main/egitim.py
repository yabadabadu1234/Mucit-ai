import json
import glob
import math
import os
import sys
import time
from typing import Dict, Any, List, Optional
from nefs.kuantum_idrak import (
    Qudit, Mertebe, Doku, Amel, HolonomiCinsi,
    BagimliLifliTensor, MukayeseVeHolonomi, IleriKuantumImkanlari,
    HafizaVeSupheReaktoru, TabulaRasaRust, TomitaTakesakiTodaGT,
    KuantumMantikDevresi, BirMilyonQuditZirhi, bargmann_n
)
from main.kulliyat import (
    Kaynak, tum_kulliyat_getir, release_varligi_indir,
    kulliyat_ornekleri_uret
)


class EgitimHatti:
    def __init__(
        self,
        d: int = 16,
        mod: str = "dar",
        dongu: int = 5,
        azami_gorev: int = 4,
        kapi_sayisi: int = 51,
        t0: float = 4.0,
        tau: float = 1.5,
        include_releases: bool = True,
        secili_verisetleri: Optional[List[str]] = None
    ):
        self.d = d
        self.mod = mod
        self.kapi_sayisi = kapi_sayisi
        self.include_releases = include_releases
        self.secili_verisetleri = secili_verisetleri
        self._mod_ayarla(mod, dongu, azami_gorev, kapi_sayisi, t0, tau)
        
        self.lif_tensöru = BagimliLifliTensor(d=d)
        self.mukayese = MukayeseVeHolonomi(d=d)
        self.ileri = IleriKuantumImkanlari(d=d)
        self.hafiza = HafizaVeSupheReaktoru(d=d)
        self.rust = TabulaRasaRust(t0=self.t0, tau=self.tau)
        self.tt_toda_gt = TomitaTakesakiTodaGT(d=d)
        self.mantik = KuantumMantikDevresi(d=d)
        self.veri_zirhi = BirMilyonQuditZirhi(N=1048576, q=64)
        self.parametre_zirhi = BirMilyonQuditZirhi(N=1048576, q=64)
        
        self.zitliklar = [
            ("içeride", "dışarıda"),
            ("var", "yok"),
            ("doğru", "yanlış"),
            ("amir", "memur"),
            ("hakikat", "safsata"),
            ("adalet", "zulüm"),
            ("ilim", "cehl"),
            ("nizam", "kaos"),
            ("sebep", "netice"),
            ("cevher", "araz"),
            ("bütün", "parça"),
            ("suret", "mana"),
            ("hareket", "sükun"),
            ("kuvve", "fiil"),
            ("gayb", "şahadet"),
            ("külli", "cüz'i"),
            ("vücut", "adem"),
            ("tenzih", "teşbih"),
            ("vahdet", "kesret"),
            ("tasdik", "inkar")
        ]

    def _mod_ayarla(self, mod: str, dongu: int, azami_gorev: int, kapi_sayisi: int, t0: float, tau: float):
        if mod == "dar":
            self.mod_ad = "Dar Bütçeli (Hafif / Hızlı)"
            self.dongu = 5
            self.azami_gorev = 4
            self.kapi_sayisi = 51
            self.t0 = 4.0
            self.tau = 1.5
            self.azami_kulliyat_kaynak = 3
        elif mod == "dengeli":
            self.mod_ad = "Dengeli (Standart Tekâmül)"
            self.dongu = 12
            self.azami_gorev = 10
            self.kapi_sayisi = 51
            self.t0 = 8.0
            self.tau = 2.0
            self.azami_kulliyat_kaynak = 6
        elif mod == "kulliyet":
            self.mod_ad = "Küllî (İleri Tahkik & Rüşt)"
            self.dongu = 20
            self.azami_gorev = 20
            self.kapi_sayisi = 102
            self.t0 = 12.0
            self.tau = 2.5
            self.azami_kulliyat_kaynak = 12
        elif mod == "ozel":
            self.mod_ad = "Özel Parametrik"
            self.dongu = max(1, min(50, dongu))
            self.azami_gorev = max(1, min(50, azami_gorev))
            self.kapi_sayisi = max(10, min(200, kapi_sayisi))
            self.t0 = t0
            self.tau = max(0.5, tau)
            self.azami_kulliyat_kaynak = 8
        else:
            self.mod_ad = f"Standart ({mod})"
            self.dongu = dongu
            self.azami_gorev = azami_gorev
            self.t0 = t0
            self.tau = tau
            self.azami_kulliyat_kaynak = 4

    def log(self, seviye: str, mesaj: str):
        zaman = time.strftime("%H:%M:%S")
        sys.stderr.write(f"[{zaman}] [{seviye}] {mesaj}\n")
        sys.stderr.flush()

    def durum_uret(self, etiket: str, tohum: int = 0) -> Qudit:
        v = [complex(math.cos(tohum * 0.15 + j * 0.65), math.sin(tohum * 0.15 + j * 0.65)) for j in range(self.d)]
        return Qudit(v, etiket=etiket)

    def safha_1_tahfiz(self) -> List[Dict[str, Any]]:
        self.log("KUANTUM", f"Safha-1 (Tahfîz) başlatıldı. Mod: '{self.mod_ad}', Toplam Döngü: {self.dongu}")
        rapor = []
        for i in range(self.dongu):
            c1, c2 = self.zitliklar[i % len(self.zitliklar)]
            d1 = self.durum_uret(c1, i * 7)
            d2 = self.durum_uret(c2, i * 7 + 3)
            
            intac = self.mukayese.mukayese_intac([d1, d2])
            rho_mod = self.tt_toda_gt.tomita_moduler_akis(d1.rho(), t=0.1 * (i + 1))
            hata = abs(abs(intac["phi_n"]) - math.pi)
            fitrat_h, hafiza_h, makam = self.rust.hata_bolustur(hata)
            alpha = self.rust.ilerle()
            
            basla_idx = (i * 2) % self.veri_zirhi.N
            self.veri_zirhi.aktif_yerlestir([d1, d2], baslangic=basla_idx)
            
            p1 = self.durum_uret(f"param_{c1}", int(alpha * 100) + i)
            p2 = self.durum_uret(f"param_{c2}", int((1.0 - alpha) * 100) + i + 1)
            self.parametre_zirhi.aktif_yerlestir([p1, p2], baslangic=basla_idx)
            
            fs_mesafe = self.veri_zirhi.fubini_study_mesafe(self.parametre_zirhi)
            kan_psi = self.veri_zirhi.kan_genlik_hesapla(theta=0.785 + i * 0.05)
            tetabuk_adim = self.veri_zirhi.kapi_51_tetabuk(self.kapi_sayisi)
            
            self.log(
                "TAHFIZ",
                f"Adım {i+1}/{self.dongu}: Kutup '{c1} <-> {c2}' | Hata={hata:.4f} (Fıtrat={fitrat_h:.3f}, Hafıza={hafiza_h:.3f}) | α={alpha:.3f} | {makam}"
            )
            self.log(
                "ZIRH",
                f"Zırh Rezervasyonu: {len(self.veri_zirhi.aktif_pencere)} aktif / {self.veri_zirhi.N - len(self.veri_zirhi.aktif_pencere):,} seyirci | d_FS={fs_mesafe:.4f} | Devre Sadakati={tetabuk_adim['sadakat']:.4f}"
            )
            
            rapor.append({
                "adim": i + 1,
                "kutup": f"{c1} <-> {c2}",
                "hata": round(hata, 4),
                "fitrat_hata": round(fitrat_h, 4),
                "hafiza_hata": round(hafiza_h, 4),
                "alpha_rust": round(alpha, 3),
                "makam": makam,
                "tomita_iz": round(sum(rho_mod[j][j].real for j in range(self.d)), 3),
                "zirh_aktif_qudit": len(self.veri_zirhi.aktif_pencere),
                "zirh_seyirci_qudit": self.veri_zirhi.N - len(self.veri_zirhi.aktif_pencere),
                "fubini_study_mesafe": round(fs_mesafe, 4),
                "kan_genlik_norm": round(abs(kan_psi), 4),
                "kapi_51_sadakat": tetabuk_adim["sadakat"]
            })
        return rapor

    def safha_2_tahkik_arc(self) -> List[Dict[str, Any]]:
        dosyalar = sorted(glob.glob("idrak/veri/arc_agi_2/evaluation/*.json"))[:self.azami_gorev]
        self.log("KUANTUM", f"Safha-2 (Tahkik ARC) başlatıldı. {len(dosyalar)} görev dosyası işlenecek.")
        rapor = []
        for idx_dosya, f_yol in enumerate(dosyalar):
            g_id = os.path.splitext(os.path.basename(f_yol))[0]
            with open(f_yol, "r") as f:
                veri = json.load(f)
            
            egitim_ciftleri = veri.get("train", [])
            k_durumlar = []
            for idx, cift in enumerate(egitim_ciftleri[:3]):
                g_boyut = len(cift.get("input", []))
                c_boyut = len(cift.get("output", []))
                d_cift = self.durum_uret(f"{g_id}_cift_{idx}", g_boyut * 10 + c_boyut)
                k_durumlar.append(d_cift)
            
            if len(k_durumlar) < 2:
                continue
            
            basla_arc = (100 + idx_dosya * 8) % self.veri_zirhi.N
            self.veri_zirhi.aktif_yerlestir(k_durumlar, baslangic=basla_arc)
            param_arc = [self.durum_uret(f"param_arc_{g_id}_{m}", m * 19 + idx_dosya) for m in range(len(k_durumlar))]
            self.parametre_zirhi.aktif_yerlestir(param_arc, baslangic=basla_arc)
            
            fs_arc = self.veri_zirhi.fubini_study_mesafe(self.parametre_zirhi)
            kan_arc = self.veri_zirhi.kan_genlik_hesapla(theta=0.55 + idx_dosya * 0.1)
            
            intac = self.mukayese.mukayese_intac(k_durumlar)
            hipotez_skorlari = [abs(k_durumlar[0].ic(kd)) for kd in k_durumlar]
            sirali_skorlar = self.tt_toda_gt.toda_lax_sirala(hipotez_skorlari)
            gt_dallanma = self.tt_toda_gt.gelfand_tsetlin_branching("varlik")
            sadakat = self.mantik.mantiga_sadakat_denetimi(intac["morfizm"].rho())
            
            self.log(
                "TAHKIK",
                f"ARC Görev {idx_dosya+1}/{len(dosyalar)} [{g_id}]: {len(egitim_ciftleri)} çift | r_K={intac['r_n']:.4f}, Phi_K={intac['phi_n']:.4f} | Sadakat={sadakat} | Toda En İyi={sirali_skorlar[0]:.4f}"
            )
            
            rapor.append({
                "gorev": g_id,
                "cift_sayisi": len(egitim_ciftleri),
                "r_K": intac["r_n"],
                "phi_K": intac["phi_n"],
                "topoloji": intac["topoloji"],
                "amel": intac["amel"],
                "toda_sirali_skorlar": [round(s, 4) for s in sirali_skorlar],
                "gt_alt_sektor": gt_dallanma[0]["alt"],
                "mantiga_sadakat": sadakat,
                "zirh_aktif_qudit": len(self.veri_zirhi.aktif_pencere),
                "zirh_fubini_study": round(fs_arc, 4),
                "kan_genlik_norm": round(abs(kan_arc), 4)
            })
        return rapor

    def safha_3_kulliyat_ve_release(self) -> List[Dict[str, Any]]:
        tum_kaynaklar = tum_kulliyat_getir()
        
        if self.secili_verisetleri:
            secili_kume = set(self.secili_verisetleri)
            islenecek_kaynaklar = [k for k in tum_kaynaklar if k.ad in secili_kume or k.sahip_isim in secili_kume]
        else:
            # Dengeli külli numune seçimi: Lügat, Kadîm Türkçe, Yek Kitap, Release ve Riyaziye/ARC dengelenir
            lugatlar = [k for k in tum_kaynaklar if k.kategori == "lugat"]
            kadim = [k for k in tum_kaynaklar if k.kategori in ["kadim_turkce", "yek_kitap"]]
            releases = [k for k in tum_kaynaklar if k.kategori in ["release_koprusu", "ozel_release"]]
            digerleri = [k for k in tum_kaynaklar if k.kategori in ["arc", "riyaziye", "kelam"]]
            
            secilen: List[Kaynak] = []
            # Her kategoriden orantılı al
            if lugatlar:
                secilen.extend(lugatlar[:max(1, self.azami_kulliyat_kaynak // 4)])
            if kadim:
                secilen.extend(kadim[:max(1, self.azami_kulliyat_kaynak // 4)])
            if releases:
                secilen.extend(releases[:max(1, self.azami_kulliyat_kaynak // 3)])
            if digerleri:
                secilen.extend(digerleri[:max(1, self.azami_kulliyat_kaynak // 4)])
            
            # Kalan kontenjanı doldur
            for k in tum_kaynaklar:
                if len(secilen) >= self.azami_kulliyat_kaynak:
                    break
                if k not in secilen:
                    secilen.append(k)
            islenecek_kaynaklar = secilen[:self.azami_kulliyat_kaynak]

        self.log(
            "RELEASE",
            f"Safha-3 (Külliyat & GitHub Release Tâlimi) başlatıldı. Toplam {len(islenecek_kaynaklar)} veriseti boru hattına bağlanıyor."
        )

        rapor = []
        for idx_k, kaynak in enumerate(islenecek_kaynaklar):
            if kaynak.surum or kaynak.varlik or kaynak.kategori in ["release_koprusu", "ozel_release"]:
                self.log(
                    "RELEASE",
                    f"[{idx_k+1}/{len(islenecek_kaynaklar)}] GitHub Release varlığı tetikleniyor: '{kaynak.ad}' ({kaynak.surum or 'release'}/{kaynak.varlik or 'mucit'}) | Pay: {kaynak.pay}"
                )
            else:
                self.log(
                    "KULLIYAT",
                    f"[{idx_k+1}/{len(islenecek_kaynaklar)}] Külliyat kaynağı boru hattında: '{kaynak.ad}' ({kaynak.sahip_isim}) | Pay: {kaynak.pay}"
                )

            yerel_yol = release_varligi_indir(kaynak, log_cb=self.log)
            
            ornekler = kulliyat_ornekleri_uret(kaynak, adet=3)
            k_durumlar = []
            for io, ornek in enumerate(ornekler):
                tohum = (idx_k + 1) * 31 + io * 17
                d = self.durum_uret(f"{kaynak.ad[:12]}_{io}", tohum=tohum)
                k_durumlar.append(d)

            baslangic_idx = (500 + idx_k * 12) % self.veri_zirhi.N
            self.veri_zirhi.aktif_yerlestir(k_durumlar, baslangic=baslangic_idx)
            
            param_durumlar = [self.durum_uret(f"param_rel_{idx_k}_{m}", m * 23 + idx_k) for m in range(len(k_durumlar))]
            self.parametre_zirhi.aktif_yerlestir(param_durumlar, baslangic=baslangic_idx)

            intac = self.mukayese.mukayese_intac(k_durumlar)
            fs_mesafe = self.veri_zirhi.fubini_study_mesafe(self.parametre_zirhi)
            kan_genlik = self.veri_zirhi.kan_genlik_hesapla(theta=0.62 + idx_k * 0.08)
            tetabuk = self.veri_zirhi.kapi_51_tetabuk(self.kapi_sayisi)
            
            skorlar = [abs(k_durumlar[0].ic(kd)) for kd in k_durumlar]
            sirali = self.tt_toda_gt.toda_lax_sirala(skorlar)
            sadakat = self.mantik.mantiga_sadakat_denetimi(intac["morfizm"].rho())
            
            rust_alpha = self.rust.ilerle()

            self.log(
                "BORUHATTI",
                f"'{kaynak.ad}' işlendi: Boyut={kaynak.boyut_bayt:,} bayt | r_K={intac['r_n']:.4f} | d_FS={fs_mesafe:.4f} | Sadakat={sadakat} | α={rust_alpha:.3f}"
            )

            rapor.append({
                "veriseti_ad": kaynak.ad,
                "sahip_isim": kaynak.sahip_isim,
                "kategori": kaynak.kategori,
                "surum": kaynak.surum,
                "varlik": kaynak.varlik,
                "yerel_yol": yerel_yol,
                "pay": kaynak.pay,
                "ornek_sayisi": kaynak.ornek_sayisi,
                "r_K": intac["r_n"],
                "phi_K": intac["phi_n"],
                "topoloji": intac["topoloji"],
                "fubini_study_mesafe": round(fs_mesafe, 4),
                "kan_genlik_norm": round(abs(kan_genlik), 4),
                "kapi_51_sadakat": tetabuk["sadakat"],
                "mantiga_sadakat": sadakat,
                "toda_en_iyi": round(sirali[0], 4)
            })

        return rapor

    def calistir(self) -> Dict[str, Any]:
        self.log("BASLAT", f"Küllî Eğitim Hattı uyarılıyor... Mod: {self.mod_ad} | 2N Serbestlik: {self.veri_zirhi.mahalli_serbestlik:,}")
        tahfiz = self.safha_1_tahfiz()
        tahkik = self.safha_2_tahkik_arc()
        
        kulliyat_rapor = []
        if self.include_releases:
            kulliyat_rapor = self.safha_3_kulliyat_ve_release()

        seyirci = self.veri_zirhi.seyirci_analizi()
        tetabuk = self.veri_zirhi.kapi_51_tetabuk(self.kapi_sayisi)
        kenet = self.parametre_zirhi.cift_yazmac_kenet(self.veri_zirhi)
        fs_final = self.veri_zirhi.fubini_study_mesafe(self.parametre_zirhi)
        kan_final = self.veri_zirhi.kan_genlik_hesapla()
        
        rust_makam = "Tahkik (Kamil Hâkim)" if self.rust.alpha() >= 0.8 else ("Tekâmül" if self.rust.alpha() >= 0.3 else "Tahfiz (Bebeklik)")
        self.log("SONUC", f"Eğitim nihayete erdi. Rüşt Makamı: {rust_makam} (α={self.rust.alpha():.3f}) | 1M Qudit Çift Yazmaç Kenet Sadakati: {kenet['nihai_kenet_sadakati']}")
        
        return {
            "basarili": True,
            "mod": self.mod,
            "mod_ad": self.mod_ad,
            "parametreler": {
                "dongu": self.dongu,
                "azami_gorev": self.azami_gorev,
                "kapi_sayisi": self.kapi_sayisi,
                "t0": self.t0,
                "tau": self.tau,
                "include_releases": self.include_releases,
                "secili_verisetleri": self.secili_verisetleri
            },
            "bir_milyon_qudit_zirhi": {
                "toplam_qudit": seyirci["toplam_qudit"],
                "taban_q": seyirci["taban_q"],
                "kapasite": seyirci["kapasite"],
                "mahalli_serbestlik": seyirci["mahalli_serbestlik"],
                "aktif_qudit": seyirci["aktif_qudit"],
                "seyirci_qudit": seyirci["seyirci_qudit"],
                "seyirci_sadakati": seyirci["seyirci_ic_carpim_norm"],
                "fubini_study_mesafe": round(fs_final, 4),
                "kan_genlik_norm": round(abs(kan_final), 4),
                "kapi_51_tetabuk": tetabuk,
                "cift_yazmac_kenet": kenet
            },
            "tahfiz_adimlari": tahfiz,
            "tahkik_arc": tahkik,
            "kulliyat_ve_release_egitimi": kulliyat_rapor,
            "nihai_rust_makami": rust_makam,
            "nihai_alpha": round(self.rust.alpha(), 4)
        }


def egitimi_baslat(
    mod: str = "dar",
    dongu: int = 5,
    azami_gorev: int = 4,
    kapi_sayisi: int = 51,
    t0: float = 4.0,
    tau: float = 1.5,
    include_releases: bool = True,
    secili_verisetleri: Optional[List[str]] = None
) -> Dict[str, Any]:
    motor = EgitimHatti(
        d=16,
        mod=mod,
        dongu=dongu,
        azami_gorev=azami_gorev,
        kapi_sayisi=kapi_sayisi,
        t0=t0,
        tau=tau,
        include_releases=include_releases,
        secili_verisetleri=secili_verisetleri
    )
    return motor.calistir()


if __name__ == "__main__":
    mod_arg = sys.argv[1] if len(sys.argv) > 1 else "dar"
    dongu_arg = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    gorev_arg = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    kapi_arg = int(sys.argv[4]) if len(sys.argv) > 4 else 51
    t0_arg = float(sys.argv[5]) if len(sys.argv) > 5 else 4.0
    tau_arg = float(sys.argv[6]) if len(sys.argv) > 6 else 1.5
    inc_rel = sys.argv[7].lower() in ["true", "1", "evet"] if len(sys.argv) > 7 else True
    
    sonuc = egitimi_baslat(
        mod=mod_arg,
        dongu=dongu_arg,
        azami_gorev=gorev_arg,
        kapi_sayisi=kapi_arg,
        t0=t0_arg,
        tau=tau_arg,
        include_releases=inc_rel
    )
    print(json.dumps(sonuc, default=str, ensure_ascii=False, indent=2))
