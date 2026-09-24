"""
nefs/suphe.py - Epistemik Tahkik, Tevakkuf ve Şüphe Manifoldu
Nefs-i Müdrike Mimarîsi
"""

import math
import time
from typing import List, Dict, Optional, Any, Tuple
from matematik.temel import KuantumDurum


class Iddia:
    """Bir bilgi, kaziye veya ampirik iddia"""
    def __init__(
        self,
        metin: str,
        durum: KuantumDurum,
        guven: float = 1.0,
        baglam: str = "genel",
        zaman_damgasi: Optional[float] = None
    ):
        self.metin = metin
        self.durum = durum
        self.guven = guven  # mu in [0, 1]
        self.baglam = baglam
        self.zaman = zaman_damgasi or time.time()

    def __repr__(self) -> str:
        return f"<Iddia '{self.metin}' guven={self.guven:.2f} baglam='{self.baglam}'>"


class SupheManifoldu:
    """
    M_şüphe: Termodinamik reaktör ve çatışan iddialar havuzu
    1. Öncelik dogmatizmi yoktur; iki zıt iddiada da güven eşit düşürülür.
    2. Modalite çatallanması ile tenakuz çözülürse hakikat uzayına aktarılır.
    3. Merak motoru (O_sual) çözümsüz iddialar için soru fırlatır.
    4. Liouville sönümlemesi: Zamanla delilsiz kalan şüphe buharlaşır.
    """
    def __init__(self, liouville_gama: float = 0.05):
        self.catismalar: List[Dict[str, Any]] = []
        self.superpozisyon_havuzu: List[Iddia] = []
        self.merak_kancalari: List[str] = []
        self.gama = liouville_gama

    def celiski_tahkiki(
        self,
        iddia_1: Iddia,
        iddia_2: Iddia,
        fitrat_kilitli_mi: bool = True
    ) -> Dict[str, Any]:
        """
        İki iddia arasındaki çatışma tahlili:
        Fıtrat (ağırlıklar) güncellenmez; hata doğrudan hafızadaki iddialara yazılır.
        """
        # İç çarpım ve Fubini-Study mesafesi
        ic = iddia_1.durum.ic_carpim(iddia_2.durum)
        sadakat = abs(ic)**2
        fs = iddia_1.durum.fubini_study_mesafesi(iddia_2.durum)

        # Eğer iki iddia aynı bağlamda birbirini dışlıyorsa (örneğin "içeride" vs "dışarıda")
        # Öncelik dogmatizminin ilgası: Her ikisinin de güveni sönümlenir!
        iddia_1.guven *= (1.0 - 0.5 * sadakat)
        iddia_2.guven *= (1.0 - 0.5 * sadakat)

        # Modalite kontrolü (Bağlam ayrıştırma)
        if iddia_1.baglam != iddia_2.baglam:
            cozum = "Modalite ayrışması: Şartlar farklı olduğu için tenakuz sahtedir; iki iddia da kendi bağlamında meşrudur."
            self.superpozisyon_havuzu.append(iddia_1)
            self.superpozisyon_havuzu.append(iddia_2)
            durum_kodu = "modal_cozuldu"
        else:
            # Hakiki teâruz: Şüphe manifolduna al ve merak kancası at
            kayit = {
                "iddia_1": iddia_1,
                "iddia_2": iddia_2,
                "eklenme_zamani": time.time(),
                "hacim": 1.0
            }
            self.catismalar.append(kayit)
            kanca = f"Teâruz Sualı: '{iddia_1.metin}' ile '{iddia_2.metin}' arasındaki ayrımı doğuracak illet nedir?"
            self.merak_kancalari.append(kanca)
            cozum = "Teâruz tespit edildi. İki iddia şüphe manifolduna alındı; aktif merak kancası fırlatıldı."
            durum_kodu = "suphe_reaktoru"

        return {
            "durum_kodu": durum_kodu,
            "sadakat": round(sadakat, 4),
            "fubini_study": round(fs, 4),
            "iddia_1_yeni_guven": round(iddia_1.guven, 3),
            "iddia_2_yeni_guven": round(iddia_2.guven, 3),
            "cozum": cozum
        }

    def liouville_tasfiyesi(self, gecen_sure: float = 1.0):
        """
        Liouville hacim sönümlemesi: dVol/dt = -gama * Vol
        Zaman aşımına uğrayan mesnetsiz şüpheler buharlaşır.
        """
        kalanlar = []
        for c in self.catismalar:
            c["hacim"] *= math.exp(-self.gama * gecen_sure)
            if c["hacim"] > 0.05:
                kalanlar.append(c)
        self.catismalar = kalanlar

    def tevakkuf_havuzuna_ekle(self, hipotez: Iddia):
        """Acele hüküm vermeden süperpozisyonda bekletme"""
        self.superpozisyon_havuzu.append(hipotez)

    def ozet(self) -> Dict[str, Any]:
        return {
            "aktif_catisma_sayisi": len(self.catismalar),
            "tevakkuf_havuzu_sayisi": len(self.superpozisyon_havuzu),
            "merak_kancalari": self.merak_kancalari[-5:]
        }
