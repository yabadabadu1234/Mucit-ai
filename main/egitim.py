"""
main/egitim.py - Fıtrat Kalibrasyonu, ARC-AGI-2 ve Küllî Mukayese Eğitimi
Mucit-AI / Nefs-i Müdrike
"""

import os
import sys
import json
import math
import glob
from typing import List, Dict, Any, Optional

from matematik.temel import KuantumDurum, rastgele_kuantum_durum
from nefs.mukayese import MukayeseMotoru, OntoMertebe, IntacManifoldu
from nefs.vecih import VecihSpektrumu
from nefs.mertebe_kesfi import MertebeKesfi
from nefs.rust import RustFazi
from nefs.hafiza import TopolojikHafizaKovani
from nefs.suphe import SupheManifoldu, Iddia


class EgitimHatti:
    """
    Nefs-i Müdrike Küllî Eğitim Hattı
    1. Bebeklik Safhası: Fıtrat Kalibrasyonu (Zıtlık ve Lie simetrilerini öğrenme)
    2. Rüşt Safhası: ARC-AGI-2 numuneleri üzerinde K-çifti Bargmann poligonu ile küllî kural eğitimi
    """
    def __init__(self, d: int = 16):
        self.d = d
        self.mukayese = MukayeseMotoru(d=d)
        self.vecih_spektrumu = VecihSpektrumu()
        self.mertebe_kesfedici = MertebeKesfi(d=d)
        self.rust = RustFazi(t0=5.0, tau=2.0)
        self.hafiza = TopolojikHafizaKovani()
        self.suphe = SupheManifoldu()

        # Sözlük ve durum haritası (Fıtrat durumları)
        self.durum_defteri: Dict[str, KuantumDurum] = {}

    def _durum_al_veya_uret(self, etiket: str, tohum: Optional[int] = None) -> KuantumDurum:
        if etiket not in self.durum_defteri:
            self.durum_defteri[etiket] = rastgele_kuantum_durum(self.d, etiket=etiket, tohum=tohum)
        return self.durum_defteri[etiket]

    def bebeklik_fitrat_kalibrasyonu(self, adim_sayisi: int = 6) -> List[Dict[str, Any]]:
        """
        1. Safha: Bebeklik / Tabula Rasa Terbiyesi
        Model zıtlıkları (içeride vs dışarıda) ve geometrik simetrileri öğrenir.
        Hata doğrudan fıtrata ve ağırlıklara akar.
        """
        print("\n=== [1. SAFHA: TAHFÎZ - FITRATIN TERBİYESİ VE KALİBRASYONU] ===")
        zit_ciftler = [
            ("içeride", "dışarıda"),
            ("doğru", "yanlış"),
            ("var", "yok"),
            ("büyük", "küçük"),
            ("aydınlık", "karanlık"),
            ("amir", "memur")
        ]

        kayitlar = []
        for i in range(adim_sayisi):
            cift = zit_ciftler[i % len(zit_ciftler)]
            d1 = self._durum_al_veya_uret(cift[0], tohum=i * 10 + 1)
            d2 = self._durum_al_veya_uret(cift[1], tohum=i * 10 + 2)

            # İkili mukayese
            intac = self.mukayese.nli_mukayese([d1, d2], mertebe=OntoMertebe.MEZO_KIYAS)

            # İki zıt kavramın fazı pi'ye yaklaştırılmalıdır (Möbius zıtlığı)
            hedef_faz = math.pi
            faz_hatasi = abs(abs(intac.berry_fazi) - hedef_faz)

            # Rüşt katsayısına göre hatayı bölüştür
            fitrat_hata, hafiza_hata, durum_aciklama = self.rust.hata_dagitimi(faz_hatasi)

            # Ağırlıkları (vektör fazını) hedefe doğru bük
            alpha = self.rust.adim_ilerlet()

            # Fıtratı eğit (Zıt kutup durumunu güncelle)
            if not self.rust.alpha() >= 0.8:
                # İkinci durumun fazını d1'e göre -1 yönüne kaydır
                yeni_v = [-x for x in d1.v]
                self.durum_defteri[cift[1]] = KuantumDurum(yeni_v, etiket=cift[1])

            adim_kaydi = {
                "adim": i + 1,
                "cift": cift,
                "topoloji": intac.topoloji.value,
                "faz_hatasi": round(faz_hatasi, 4),
                "fitrat_hatasi": round(fitrat_hata, 4),
                "hafiza_hatasi": round(hafiza_hata, 4),
                "alpha_rust": round(alpha, 3),
                "durum": durum_aciklama
            }
            kayitlar.append(adim_kaydi)
            print(f"  Adım {i+1} | Çift: {cift[0]} <-> {cift[1]} | Faz Hatası: {faz_hatasi:.4f} | {durum_aciklama}")

        return kayitlar

    def arc_kulliyat_egitimi(self, azami_gorev: int = 5) -> List[Dict[str, Any]]:
        """
        2. Safha: ARC-AGI-2 Küllî Numune ve Kural Eğitimi
        Eğitim çiftleri K-nokta Bargmann poligonuna sokulur.
        Ortak kural tasdiki ve istisna tespiti yapılır.
        """
        print(f"\n=== [2. SAFHA: TAHKİK - ARC-AGI-2 KÜLLÎ NUMUNE VE MÎZÂN EĞİTİMİ] ===")
        arc_yolu = "idrak/veri/arc_agi_2/training"
        gorev_dosyalari = sorted(glob.glob(os.path.join(arc_yolu, "*.json")))

        if not gorev_dosyalari:
            print("  [İkaz] ARC eğitim dosyaları bulunamadı, yapay numunelerle eğitilecek.")
            gorev_verileri = [
                {
                    "id": "sentetik_01",
                    "train": [
                        {"input": [[1, 0], [0, 1]], "output": [[0, 1], [1, 0]]},
                        {"input": [[2, 0], [0, 2]], "output": [[0, 2], [2, 0]]},
                        {"input": [[3, 0], [0, 3]], "output": [[0, 3], [3, 0]]}
                    ]
                }
            ]
        else:
            gorev_verileri = []
            for fp in gorev_dosyalari[:azami_gorev]:
                with open(fp, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    data["id"] = os.path.basename(fp).replace(".json", "")
                    gorev_verileri.append(data)

        raporlar = []
        for gorev in gorev_verileri:
            g_id = gorev["id"]
            train_ciftler = gorev.get("train", [])
            K = len(train_ciftler)

            # Her numune çifti için bir kural kuantum durumu oluştur
            kural_durumlari = []
            for idx, cift in enumerate(train_ciftler):
                girdi = cift.get("input", [])
                cikti = cift.get("output", [])
                girdi_hacim = sum(len(row) for row in girdi)
                cikti_hacim = sum(len(row) for row in cikti)
                fark_orani = (cikti_hacim - girdi_hacim) / max(1, girdi_hacim)

                # Numune kural durumunu üret
                faz = math.atan2(cikti_hacim, max(1, girdi_hacim))
                v = [complex(math.cos(faz * (j + 1)), math.sin(faz * (j + 1))) for j in range(self.d)]
                kural_durumlari.append(KuantumDurum(v, etiket=f"{g_id}_cift_{idx}"))

            # K numunenin ortak K-Bargmann poligonu (Fasıl I & III)
            intac = self.mukayese.nli_mukayese(kural_durumlari, mertebe=OntoMertebe.MAKRO_NUMUNE)

            # Vecih spektrumu analizi
            ornek_metin = ["izgara", "dondur", "simetri", "renk", "adet", "kural"]
            secilen_vecih, vecih_skorlari = self.vecih_spektrumu.vecih_sec(ornek_metin)

            # Hafızaya küllî kural olarak mühürle veya yeniden tertiple
            if intac.amel == intac.amel.BEYAN or intac.rezonans > 0.7:
                tertip_sonucu = self.hafiza.ekle(
                    icerik=f"ARC Görev {g_id}: K={K} numuneli küllî kural tasdik edildi.",
                    durum=intac.morfizm_durumu or kural_durumlari[0],
                    lif_koordinati={"vecih": secilen_vecih.ad, "gorev": g_id}
                )
                hukum = "Küllî kanun tasdik edildi; hafıza kovanına mühürlendi."
            else:
                tertip_sonucu = self.hafiza.yeniden_tertitle(
                    intac=intac,
                    yeni_lif_anahtari="istisna_modalite",
                    yeni_lif_degeri=f"gorev_{g_id}",
                    yeni_kaziye_metni=f"ARC Görev {g_id}: Şartlı ve istisnalı kural manifoldu."
                )
                hukum = "İstisna veya şartlanma tespit edildi; hafıza yeniden tertiplendi (Sheaf Re-gluing)."

            # Mîzân Kefe Kayıpları
            l_sadakat = round(1.0 - intac.rezonans, 4)
            l_tenakuz = round(abs(intac.berry_fazi) if intac.topoloji == intac.topoloji.DIPOL else 0.0, 4)
            l_dizi = round(20.0 + l_sadakat * 2.5, 3)

            rapor = {
                "gorev_id": g_id,
                "numune_sayisi_K": K,
                "rezonans_r_K": round(intac.rezonans, 4),
                "berry_fazi_rad": round(intac.berry_fazi, 4),
                "topolojik_doku": intac.topoloji.value,
                "secilen_vecih": secilen_vecih.ad,
                "mizan_kefeleri": {
                    "l_dizi": l_dizi,
                    "l_sadakat": l_sadakat,
                    "l_tenakuz": l_tenakuz
                },
                "hukum": hukum
            }
            raporlar.append(rapor)
            print(f"  Görev: {g_id} (K={K}) | r_K: {intac.rezonans:.3f} | Vech: {secilen_vecih.ad} | {hukum}")

        return raporlar


def egitimi_baslat():
    hattı = EgitimHatti(d=16)
    bebeklik_ozet = hattı.bebeklik_fitrat_kalibrasyonu(adim_sayisi=6)
    arc_ozet = hattı.arc_kulliyat_egitimi(azami_gorev=5)

    print("\n=== EĞİTİM TAMAMLANDI ===")
    print(f"Bebeklik Adımları: {len(bebeklik_ozet)}")
    print(f"ARC Görevleri İncelendi: {len(arc_ozet)}")
    print(f"Hafıza Kovanındaki Kayıtlar: {len(hattı.hafiza.kayitlar)}")
    print(f"Rüşt Durumu: {hattı.rust.ozet()}")


if __name__ == "__main__":
    egitimi_baslat()
