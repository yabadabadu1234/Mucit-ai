"""
nefs/mukayese.py - Mukayese Neticesinin İntacı, Küllî Tertip ve n-li Bargmann Motoru
Nefs-i Müdrike Mimarîsi
"""

import math
import cmath
from enum import Enum
from typing import List, Dict, Tuple, Optional, Any
from matematik.temel import KuantumDurum, bargmann_n_nokta, hilbert_schmidt_ic_carpim


class GeometrikDoku(str, Enum):
    """
    Fasıl II: 4 Geometrik Doku
    A. POSET / Agac: Tek yonlu icerme, sirali hiyerarsi
    B. DONGUSEL / Holonomi: Esit haklara sahip kutuplarin Univalence simetri halkasi (Phi ~ 0)
    C. DIPOL / Moduler Cift: Zıt kutup gerilimi (Phi = pi, J-aynasi)
    D. KAFES / Cizge: Coklu sartlarin kesistigi Heyting kafesi veya yonlu cizge
    """
    POSET = "poset_agac"
    DONGUSEL = "univalence_halkasi"
    DIPOL = "moduler_dipol"
    KAFES = "heyting_kafesi"


class AmeliVech(str, Enum):
    """
    Fasıl II: 4. Bilesen - Ameli Vech (Pragmatik)
    """
    BEYAN = "beyan_telaffuz"        # Disariya kelam et (Tasdik T -> 1)
    FUNKTOR = "funktor_tohum"      # Baska bir mukayeseye girdi kil (Morfizm |sigma>)
    TERTIP = "tertip_refactor"     # Zihnin kendi hafizasini yeniden tertiple
    SUKUT = "sukut_tevakkuf"       # Tevakkuf ve superpozisyon havuzunda beklet


class OntoMertebe(str, Enum):
    """
    5 Onto-geometrik Mertebe
    """
    MIKRO_SENTAKS = "1_mikro_sentaks"       # Cümle içi gramer halkası (n in [3, 8])
    MEZO_KIYAS = "2_mezo_kiyas"             # n-adımlı Sorites / Bürhân zinciri
    MAKRO_IZGARA = "3_makro_izgara"         # ARC ızgara içi nesneler ve topoloji
    MAKRO_NUMUNE = "4_makro_numune"         # ARC eğitim örnekleri küllî kaidesi (K çift)
    META_ISTISNA = "5_meta_istisna"         # Şartlanmalar ve istisna faz yırtığı


class IntacManifoldu:
    """
    R_çıktı(Y) = < K_topoloji, Delta_spektrum, P_tertip, M_amel >
    Mukayese ciktisi sadece bir kayip skateri degildir; 4 bilesenli bir intac tensorudur.
    """
    def __init__(
        self,
        topoloji: GeometrikDoku,
        rezonans: float,
        berry_fazi: float,
        tertip: Dict[str, Any],
        amel: AmeliVech,
        morfizm_durumu: Optional[KuantumDurum] = None,
        istisnalar: Optional[List[int]] = None
    ):
        self.topoloji = topoloji
        self.rezonans = rezonans              # r_n in [0, 1]
        self.berry_fazi = berry_fazi          # Phi_n in (-pi, pi]
        self.tertip = tertip                  # Poset/Kafes iliskileri, esdegerlik lifleri
        self.amel = amel                      # Beyan, Funktor, Tertip, Sukut
        self.morfizm_durumu = morfizm_durumu  # |sigma_Y> (2-Kategori icin nesnelestirilmis durum)
        self.istisnalar = istisnalar or []    # Simplisiyal faz yirtigi olan indisler

    def to_dict(self) -> Dict[str, Any]:
        return {
            "topoloji": self.topoloji.value,
            "rezonans_r_n": round(self.rezonans, 4),
            "berry_fazi_rad": round(self.berry_fazi, 4),
            "berry_fazi_derece": round(math.degrees(self.berry_fazi), 2),
            "amel": self.amel.value,
            "tertip_ozet": self.tertip.get("ozet", ""),
            "istisna_indisleri": self.istisnalar,
            "tenakuz_var_mi": abs(abs(self.berry_fazi) - math.pi) < 0.25
        }

    def __repr__(self) -> str:
        return (f"<IntacManifoldu topoloji={self.topoloji.name} r={self.rezonans:.3f} "
                f"Phi={self.berry_fazi:.3f}rad amel={self.amel.name}>")


class MukayeseMotoru:
    """
    Küllî Mukayese Motoru: Xi(Y)
    Verilen kuantum durumlari uzerinde n-li Bargmann invaryantini hesaplar,
    topolojik dokuyu kesfeder ve Intac Manifoldu uretir.
    """
    def __init__(self, d: int = 16):
        self.d = d

    def nli_mukayese(
        self,
        durumlar: List[KuantumDurum],
        mertebe: OntoMertebe = OntoMertebe.MEZO_KIYAS,
        esik_tenakuz: float = 2.8,  # pi'ye yakin faz
        esik_uyum: float = 0.35     # 0'a yakin faz
    ) -> IntacManifoldu:
        n = len(durumlar)
        if n < 2:
            raise ValueError("Mukayese icin en az 2 durum gereklidir!")

        r_n, phi_n, delta_n, ucgen_fazlari = bargmann_n_nokta(durumlar)

        # 1. Topolojik Dokunun Tespiti
        # n = 2 ve faz ~ pi ise -> DIPOL
        # n >= 3 ve faz ~ 0 -> DONGUSEL (Univalence)
        # faz ~ pi veya -pi -> DIPOL / TENAKUZ
        # Eger asimetrik gecisler veya tek yonlu siralama varsa -> POSET / KAFES
        istisnalar = []
        if n == 2:
            if abs(phi_n) > esik_tenakuz:
                topoloji = GeometrikDoku.DIPOL
            else:
                topoloji = GeometrikDoku.POSET
        else:
            # Simplisiyal ucgen fazlarini tara (Istisna / Faz yirtigi tespiti)
            for idx, uf in enumerate(ucgen_fazlari):
                if abs(uf) > 1.2:  # 70 dereceden fazla sapan ucgen
                    istisnalar.append(idx + 1)

            if abs(phi_n) <= esik_uyum:
                topoloji = GeometrikDoku.DONGUSEL
            elif abs(abs(phi_n) - math.pi) <= 0.4:
                topoloji = GeometrikDoku.DIPOL
            elif len(istisnalar) > 0:
                topoloji = GeometrikDoku.KAFES
            else:
                topoloji = GeometrikDoku.POSET

        # 2. Ameli Vechin Tayini (Beyan, Sukut, Funktor, Tertip)
        if abs(abs(phi_n) - math.pi) <= 0.35 and r_n > 0.4:
            # Hakiki tenakuz: Acele beyan yok, tevakkuf veya tenakuz damgasi
            amel = AmeliVech.SUKUT
        elif r_n > 0.85 and abs(phi_n) <= esik_uyum:
            # Sarsilmaz tasdik: Beyan edilebilir
            amel = AmeliVech.BEYAN
        elif mertebe in [OntoMertebe.MAKRO_NUMUNE, OntoMertebe.META_ISTISNA]:
            # Hafizayi yeniden tertiplemeye medar
            amel = AmeliVech.TERTIP
        else:
            # Ust mukayeseye funktoryel tohum
            amel = AmeliVech.FUNKTOR

        # 3. Morfizm Durumu Uretimi (Reification)
        # Tum durumlari d boyutlu tekil bir |sigma_Y> durumuna projekte et
        morfizm_vektoru = [complex(0.0) for _ in range(self.d)]
        for k, dur in enumerate(durumlar):
            agirlik = cmath.exp(1j * (k * phi_n / max(1, n)))
            for j in range(min(self.d, dur.d)):
                morfizm_vektoru[j] += dur.v[j] * agirlik
        morfizm_durumu = KuantumDurum(morfizm_vektoru, etiket=f"morfizm_n{n}")

        tertip_detay = {
            "eleman_sayisi": n,
            "mertebe": mertebe.value,
            "ucgen_faz_sayisi": len(ucgen_fazlari),
            "ozet": f"n={n} halka rezonansi r={r_n:.3f}, faz={phi_n:.3f} rad"
        }

        return IntacManifoldu(
            topoloji=topoloji,
            rezonans=r_n,
            berry_fazi=phi_n,
            tertip=tertip_detay,
            amel=amel,
            morfizm_durumu=morfizm_durumu,
            istisnalar=istisnalar
        )

    def yuksek_mertebe_mukayese_2_bargmann(
        self,
        intac_1: IntacManifoldu,
        intac_2: IntacManifoldu
    ) -> float:
        """
        Fasıl III: 2-Bargmann Poligonu (Mukayeselerin Mukayesesi / Analoji)
        Tr(rho_Y * rho_Z)
        Iki ayri olayin geometrisi ayni mantik yapisini paylasiyorsa -> 1.0 cikar.
        """
        if not intac_1.morfizm_durumu or not intac_2.morfizm_durumu:
            return 0.0
        rho1 = intac_1.morfizm_durumu.yogunluk_matrisi()
        rho2 = intac_2.morfizm_durumu.yogunluk_matrisi()
        return hilbert_schmidt_ic_carpim(rho1, rho2)

    def kontrollu_dongusel_swap_testi(
        self,
        durumlar: List[KuantumDurum]
    ) -> Tuple[float, float]:
        """
        Fasıl V: n-li SWAP Testi (C-CYCLE)
        P(0) = (1 + Re(Delta_n)) / 2
        P(1) = (1 - Re(Delta_n)) / 2
        """
        r_n, phi_n, delta_n, _ = bargmann_n_nokta(durumlar)
        re_delta = delta_n.real
        p0 = max(0.0, min(1.0, 0.5 * (1.0 + re_delta)))
        p1 = max(0.0, min(1.0, 0.5 * (1.0 - re_delta)))
        return p0, p1
