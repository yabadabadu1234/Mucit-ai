"""
nefs/mertebe_kesfi.py - Otomatik Mertebe Keşfi ve Çok Ölçekli n-li Mukayese Spektrumu
Nefs-i Müdrike Mimarîsi
"""

import math
import itertools
from typing import List, Dict, Set, Tuple, Optional, Any
from matematik.temel import KuantumDurum, bargmann_n_nokta
from nefs.vecih import MertebeSeviyesi


class MertebeKesfi:
    """
    Diziden otomatik mertebe (ell) ve n-li mukayese halkalarinin tespiti
    Xi(Y) Küllî Mukayese Spektrumu Tensörü
    """
    def __init__(self, d: int = 16, esik_taban: float = 0.05, esik_bag: float = 0.2):
        self.d = d
        self.esik_taban = esik_taban
        self.esik_bag = esik_bag

    def aktif_mertebeleri_kesfet(
        self,
        durumlar: List[KuantumDurum]
    ) -> List[MertebeSeviyesi]:
        """
        Lambda_Y = { ell in L | Tr(Pi_ell(Y)^2) > eps ve Rank(Pi_ell) >= 2 }
        """
        if len(durumlar) < 2:
            return [MertebeSeviyesi.NOKTA]

        aktif: List[MertebeSeviyesi] = []

        # Her mertebe icin durumlarin ic carpim ve varyans profiline bak
        n = len(durumlar)
        farklar = []
        for i in range(n):
            for j in range(i + 1, n):
                fs = durumlar[i].fubini_study_mesafesi(durumlar[j])
                farklar.append(fs)

        ortalama_fs = sum(farklar) / max(1, len(farklar))

        # 1. Nokta mertebesi: Tum elemanlar ayrık/farklı mı?
        aktif.append(MertebeSeviyesi.NOKTA)

        # 2. Uzay mertebesi: Sürekli metrik mesafe 0 ile 1 arasında yayılıyor mu?
        if ortalama_fs > self.esik_taban:
            aktif.append(MertebeSeviyesi.UZAY)

        # 3. Kategori mertebesi: Asimetrik ve sıralı yönlülük var mı?
        if n >= 3 and ortalama_fs > 0.15:
            aktif.append(MertebeSeviyesi.KATEGORI)

        # 4. Tip mertebesi: Kapalı çevrimde üst homotopi fazı birikiyor mu?
        if n >= 3:
            r_n, phi_n, _, _ = bargmann_n_nokta(durumlar)
            if r_n > self.esik_bag and abs(phi_n) > 0.1:
                aktif.append(MertebeSeviyesi.TIP)

        return aktif

    def kalici_sinir_poligonlari(
        self,
        durumlar: List[KuantumDurum],
        azami_n: int = 5
    ) -> Dict[int, List[Dict[str, Any]]]:
        """
        Omega_ell(n; Y): Persistent Nerve icinde r_n >= tau olan meşru alt-poligonlar
        """
        m = len(durumlar)
        sonuclar: Dict[int, List[Dict[str, Any]]] = {}

        for n in range(2, min(azami_n + 1, m + 1)):
            poligonlar = []
            # Alt kümeleri tara (kombinasyon)
            for indisler in itertools.combinations(range(m), n):
                alt_durumlar = [durumlar[idx] for idx in indisler]
                r_n, phi_n, delta_n, ucgenler = bargmann_n_nokta(alt_durumlar)

                if r_n >= self.esik_bag:
                    poligonlar.append({
                        "indisler": list(indisler),
                        "etiketler": [d.etiket for d in alt_durumlar],
                        "r_n": round(r_n, 4),
                        "phi_n": round(phi_n, 4),
                        "delta_n": delta_n,
                        "ucgen_fazlari": [round(x, 4) for x in ucgenler]
                    })
            if poligonlar:
                sonuclar[n] = poligonlar

        return sonuclar

    def kulli_spektrum_ozeti(
        self,
        durumlar: List[KuantumDurum]
    ) -> Dict[str, Any]:
        """
        Xi(Y) Küllî Mukayese Spektrumu
        """
        aktif_mertebeler = self.aktif_mertebeleri_kesfet(durumlar)
        poligonlar = self.kalici_sinir_poligonlari(durumlar)

        toplam_halka = sum(len(v) for v in poligonlar.values())

        return {
            "durum_sayisi": len(durumlar),
            "aktif_mertebeler": [m.name for m in aktif_mertebeler],
            "halka_sayisi_toplam": toplam_halka,
            "mertebeler_n_detayi": {
                f"n_{n}": len(plist) for n, plist in poligonlar.items()
            },
            "poligonlar": poligonlar
        }
