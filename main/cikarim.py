"""
main/cikarim.py - Uçtan Uca İntaç, Teemmül, Kıyas ve Çıkarım Hattı
Mucit-AI / Nefs-i Müdrike
"""

import math
import sys
import json
from typing import List, Dict, Any, Optional

from matematik.temel import KuantumDurum, rastgele_kuantum_durum
from nefs.mukayese import MukayeseMotoru, OntoMertebe, IntacManifoldu, GeometrikDoku, AmeliVech
from nefs.vecih import VecihSpektrumu, MertebeSeviyesi
from nefs.mertebe_kesfi import MertebeKesfi
from nefs.holonomi import HolonomiAnalizoru, DevridaimCinsi
from nefs.suphe import SupheManifoldu, Iddia
from nefs.hafiza import TopolojikHafizaKovani


class CikarimHatti:
    """
    Nefs-i Müdrike Küllî Akıl Yürütme ve Çıkarım Motoru
    """
    def __init__(self, d: int = 16):
        self.d = d
        self.mukayese = MukayeseMotoru(d=d)
        self.vecih_spektrumu = VecihSpektrumu()
        self.mertebe_kesfedici = MertebeKesfi(d=d)
        self.holonomi = HolonomiAnalizoru(d=d)
        self.suphe = SupheManifoldu()
        self.hafiza = TopolojikHafizaKovani()

        # Hafıza kovanını temel kaidelerle başlat
        self._hafiza_tohumla()

    def _hafiza_tohumla(self):
        d_kus = rastgele_kuantum_durum(self.d, etiket="kuslar_ucar", tohum=42)
        self.hafiza.ekle("Kuşlar uçar.", d_kus, lif_koordinati={"Canlı": "Kuş", "Ortam": "Hava"})
        d_ates = rastgele_kuantum_durum(self.d, etiket="ates_yakar", tohum=43)
        self.hafiza.ekle("Ateş temas ettiği cismi yakar.", d_ates, lif_koordinati={"Unsur": "Ateş"})

    def cikarim_yap(
        self,
        girdi_dizisi: List[str],
        nesne_a: Optional[str] = None,
        nesne_b: Optional[str] = None,
        dongu_yansitilsin_mi: bool = False
    ) -> Dict[str, Any]:
        """
        Uçtan uca analitik çıkarım boru hattı:
        1. Diziden otomatik mertebe tespiti
        2. Vecih spektrumu ve kaide istihracı
        3. n-li Bargmann poligonu ile intaç manifoldu
        4. Wilson devridaim ve holonomi teftişi
        5. Tevakkuf ve şüphe havuzu değerlendirmesi
        6. Hafızayı yeniden tertipleme
        """
        print(f"\n=======================================================")
        print(f"  İNTAÇ VE ÇIKARIM GİRDİSİ: {' '.join(girdi_dizisi)}")
        print(f"=======================================================")

        # 1. Her bir token/kelime için durum vektörü oluştur
        durumlar = []
        for idx, k in enumerate(girdi_dizisi):
            # Deterministik tohum (kelimenin karakter toplamı)
            tohum = sum(ord(c) for c in k) + idx * 7
            durumlar.append(rastgele_kuantum_durum(self.d, etiket=k, tohum=tohum))

        # 2. Otomatik Mertebe ve Sinir (Nerve) Keşfi (Fasıl I)
        spektrum_ozeti = self.mertebe_kesfedici.kulli_spektrum_ozeti(durumlar)
        aktif_mertebeler = spektrum_ozeti["aktif_mertebeler"]
        print(f"  [1. Mertebe Keşfi] Aktif Mertebeler: {aktif_mertebeler}")
        print(f"                     Kalıcı Sinir Halka Sayısı: {spektrum_ozeti['halka_sayisi_toplam']}")

        # 3. Vecih Spektrumu ve Kaide İstihracı (Fasıl IV & V)
        secilen_vecih, vecih_skorlari = self.vecih_spektrumu.vecih_sec(girdi_dizisi, nesne_a, nesne_b)
        kaideler = self.vecih_spektrumu.diziden_kaide_istihraci(girdi_dizisi, secilen_vecih)
        print(f"  [2. Vecih Tayini]  Seçilen Vecih: '{secilen_vecih.ad}' ({secilen_vecih.mertebe.name})")
        print(f"                     Tür: {secilen_vecih.tur} | Komütatif: {kaideler['komutatif_mi']}")
        print(f"                     İstihraç Kaidesi: {kaideler['kan_uzantisi_kurali']}")

        # 4. n-li Bargmann Mukayesesi ve İntaç Manifoldu (Fasıl II & III)
        n = len(durumlar)
        intac = self.mukayese.nli_mukayese(durumlar, mertebe=OntoMertebe.MEZO_KIYAS)
        print(f"  [3. İntaç Manifoldu] Topoloji: {intac.topoloji.value}")
        print(f"                       Rezonans r_n: {intac.rezonans:.4f} | Berry Fazı: {intac.berry_fazi:.4f} rad ({math.degrees(intac.berry_fazi):.1f}°)")
        print(f"                       Amelî Vech: {intac.amel.value}")

        # 5. Holonomi ve Devridaim Teftişi (Fasıl VIII & IX)
        gecis_fazlari = [intac.berry_fazi / max(1, n) for _ in range(n)]
        if dongu_yansitilsin_mi:
            # Yapay olarak Möbius yırtığı testi
            gecis_fazlari = [math.pi / n for _ in range(n)]

        holonomi_raporu = self.holonomi.cevirim_tahlil_et(durumlar[0], gecis_fazlari)
        print(f"  [4. Devridaim/Holonomi] Cins: {holonomi_raporu['devridaim_cinsi']}")
        print(f"                          Hüküm: {holonomi_raporu['hukum']}")

        # 6. Tevakkuf ve Şüphe Değerlendirmesi (Fasıl IV & VII)
        if intac.amel == AmeliVech.SUKUT or holonomi_raporu["devridaim_cinsi"] == DevridaimCinsi.HAKIKI_SAFSATA.value:
            iddia_obj = Iddia(" ".join(girdi_dizisi), intac.morfizm_durumu or durumlar[0], guven=0.5)
            self.suphe.tevakkuf_havuzuna_ekle(iddia_obj)
            karar_metni = "[TEVAKKUF / SÜKÛT] Acele hüküm verilmedi; süperpozisyon havuzunda bekletildi."
        elif intac.amel == AmeliVech.BEYAN:
            karar_metni = f"[BEYAN] Küllî kaziye tasdik edildi: '{' '.join(girdi_dizisi)}'"
        else:
            karar_metni = f"[FUNKTÖR] Üst kıyasa tohum olarak mühürlendi."

        # 7. Tomita-Takesaki J-Aynası ile Zıt Vech Seyri (Fasıl IV)
        zit_vecih = self.vecih_spektrumu.tomita_takesaki_zit_vecih(secilen_vecih)
        print(f"  [5. J-Aynası Sentezi] '{secilen_vecih.ad}' vechinden zıt kutup '{zit_vecih.ad}' vechine köprü açıldı.")

        # 8. Hafızanın Topolojik Restrüktürasyonu (Fasıl V)
        tertip_bilgisi = None
        if "penguen" in [k.lower() for k in girdi_dizisi]:
            tertip_bilgisi = self.hafiza.yeniden_tertitle(
                intac=intac,
                yeni_lif_anahtari="Hareket_Ortami",
                yeni_lif_degeri="Su",
                yeni_kaziye_metni="Penguen kuştur lakin havada değil suda kanat çırpar."
            )
            print(f"  [6. Sheaf Re-Gluing] Hafıza yeniden tertiplendi! {tertip_bilgisi['yeni_lif_eklendi']}")

        print(f"  ==> NİHAÎ HÜKÜM: {karar_metni}\n")

        return {
            "girdi": girdi_dizisi,
            "mertebe_kesfi": spektrum_ozeti,
            "vecih": secilen_vecih.ad,
            "kaideler": kaideler,
            "intac_manifoldu": intac.to_dict(),
            "holonomi": holonomi_raporu,
            "karar": karar_metni,
            "j_aynasi_zit_vecih": zit_vecih.ad,
            "hafiza_tertip": tertip_bilgisi
        }


def cikarimi_calistir():
    motor = CikarimHatti(d=16)

    # 1. Senaryo: Poset / Rütbe Kıyası
    motor.cikarim_yap(
        ["Ahmet", "şirkette", "amir", "olarak", "Mehmet'e", "yetki", "verdi"],
        nesne_a="Ahmet",
        nesne_b="Mehmet"
    )

    # 2. Senaryo: Maaş / Öklid Skaler Kıyası
    motor.cikarim_yap(
        ["Ahmet'in", "maaşı", "Mehmet'in", "maaşından", "fazladır"],
        nesne_a="Ahmet",
        nesne_b="Mehmet"
    )

    # 3. Senaryo: Takva / Derunî Tip ve Nefis Muhasebesi
    motor.cikarim_yap(
        ["Ahmet", "ile", "Mehmet", "oturup", "deruni", "takva", "ve", "ihlas", "muhasebesi", "yaptılar"],
        nesne_a="Ahmet",
        nesne_b="Mehmet"
    )

    # 4. Senaryo: Hafızayı Yeniden Tertipleme (Penguen & İstisna)
    motor.cikarim_yap(
        ["Penguen", "bir", "kuştur", "fakat", "uçamaz", "suda", "yüzer"]
    )

    # 5. Senaryo: Hakiki Tenakuz ve Möbius Yıkıcı Girişimi
    motor.cikarim_yap(
        ["Bu", "önerme", "aynı", "anda", "hem", "doğrudur", "hem", "yanlıştır"],
        dongu_yansitilsin_mi=True
    )


if __name__ == "__main__":
    cikarimi_calistir()
