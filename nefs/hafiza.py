"""
nefs/hafiza.py - Topolojik Hafıza Restrüktürasyonu ve Sheaf Re-gluing
Nefs-i Müdrike Mimarîsi
"""

import math
from typing import List, Dict, Any, Optional, Tuple
from matematik.temel import KuantumDurum, hilbert_schmidt_ic_carpim
from nefs.mukayese import IntacManifoldu


class HafizaKaydi:
    """Bir hafıza kovanı kaydı / lifi"""
    def __init__(
        self,
        kimlik: int,
        icerik: str,
        durum: KuantumDurum,
        lif_koordinati: Dict[str, str],
        guven: float = 1.0
    ):
        self.kimlik = kimlik
        self.icerik = icerik
        self.durum = durum
        self.lif_koordinati = lif_koordinati  # Örn: {"Canlı": "Kuş", "Ortam": "Hava"}
        self.guven = guven

    def __repr__(self) -> str:
        return f"<HafizaKaydi #{self.kimlik} '{self.icerik}' koord={self.lif_koordinati}>"


class TopolojikHafizaKovani:
    """
    Küllî Hafıza Kovanı ve Epistemik Refactoring Motoru
    "Mantıksızlık olsa çiz üstünü der geçerdin, burada yeniden tertipleme var!"
    """
    def __init__(self, esik_alaka: float = 0.3):
        self.kayitlar: List[HafizaKaydi] = []
        self.esik_alaka = esik_alaka
        self.sayac = 0

    def ekle(
        self,
        icerik: str,
        durum: KuantumDurum,
        lif_koordinati: Optional[Dict[str, str]] = None,
        guven: float = 1.0
    ) -> HafizaKaydi:
        self.sayac += 1
        koord = lif_koordinati or {"katman": "varsayilan"}
        kayit = HafizaKaydi(self.sayac, icerik, durum, koord, guven)
        self.kayitlar.append(kayit)
        return kayit

    def alaka_taramasi(self, intac: IntacManifoldu) -> List[Tuple[HafizaKaydi, float]]:
        """
        1. Adım: Alâka Tespiti (Resonance Harvesting)
        A_alaka(k) = Tr(rho_hafiza^(k) * Pi_R) >= tau
        """
        if not intac.morfizm_durumu:
            return []

        rho_r = intac.morfizm_durumu.yogunluk_matrisi()
        alakali: List[Tuple[HafizaKaydi, float]] = []

        for k in self.kayitlar:
            rho_k = k.durum.yogunluk_matrisi()
            skor = hilbert_schmidt_ic_carpim(rho_k, rho_r)
            if skor >= self.esik_alaka:
                alakali.append((k, skor))

        return alakali

    def yeniden_tertitle(
        self,
        intac: IntacManifoldu,
        yeni_lif_anahtari: str,
        yeni_lif_degeri: str,
        yeni_kaziye_metni: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        2, 3 ve 4. Adımlar:
        - Ungluing (Sheaf Decoupling)
        - Base Change / Lif Değişimi (f*)
        - Re-gluing (Yeni faz ahengine bağlama)
        """
        alakali_kayitlar = self.alaka_taramasi(intac)
        etkilenen_sayisi = len(alakali_kayitlar)

        # 3. Adım: Taban Değişimi (Base Change)
        # İlgili kayıtların lif koordinatına yeni boyut ekle
        for kayit, skor in alakali_kayitlar:
            kayit.lif_koordinati[yeni_lif_anahtari] = yeni_lif_degeri
            # Faz ayarı (U_tertip rotasyonu)
            kayit.guven = min(1.0, kayit.guven * (1.0 + 0.1 * skor))

        # Yeni istisna / rafine kayıt varsa ekle
        yeni_kayit_obj = None
        if yeni_kaziye_metni and intac.morfizm_durumu:
            yeni_kayit_obj = self.ekle(
                icerik=yeni_kaziye_metni,
                durum=intac.morfizm_durumu,
                lif_koordinati={yeni_lif_anahtari: f"istisna_{yeni_lif_degeri}"},
                guven=1.0
            )

        return {
            "islem": "topolojik_re_gluing",
            "etkilenen_kayit_sayisi": etkilenen_sayisi,
            "yeni_lif_eklendi": f"{yeni_lif_anahtari} = {yeni_lif_degeri}",
            "yeni_kayit_kimlik": yeni_kayit_obj.kimlik if yeni_kayit_obj else None,
            "toplam_hafiza_boyutu": len(self.kayitlar)
        }
