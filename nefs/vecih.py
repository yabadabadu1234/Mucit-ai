"""
nefs/vecih.py - Vech Mahiyetinin Mertebe Tahkiki, Tür İzolasyonu ve Diziden Kaide İstihracı
Nefs-i Müdrike Mimarîsi
"""

import math
import cmath
from enum import Enum
from typing import List, Dict, Optional, Tuple, Any
from matematik.temel import KuantumDurum, lie_komutator, HAS_NUMPY


class MertebeSeviyesi(int, Enum):
    """
    1. KADEME: Mertebe Seviyeleri (ell in {0, 1, 2, 3})
    ell = 0: Nokta (Ayrık gösterge / isim)
    ell = 1: Uzay (Sürekli manifold / metrik mesafe)
    ell = 2: Kategori (Morfizm / poset / rol ve yetki)
    ell = 3: Tip (Univalent evren / sigma-bağımlı / derunî ilke)
    """
    NOKTA = 0
    UZAY = 1
    KATEGORI = 2
    TIP = 3


class UzayTuru(str, Enum):
    HIPERBOLIK_POINCARE = "hiperbolik_poincare"  # K < 0 (Agacsi hiyerarsi)
    OKLID = "oklid_duzlemi"                      # K = 0 (Lineer toplanabilir eksen)
    LIE_MANIFOLDU = "lie_cartan_torus"           # K > 0 (Dongusel fazlar ve donmeler)


class KategoriTuru(str, Enum):
    POSET = "poset_kismi_siralama"               # Tek yonlu sira / amir-memur
    HEYTING = "heyting_sezgisel_kafes"           # Sartlar ve istisnalar
    DAG = "yonlu_nedensellik_cizgesi"            # Fail-illet-netice akisi (BGCM)


class TipTuru(str, Enum):
    SIGMA_BAGIMLI = "sigma_bagimli_tip"          # Ic ice teleskopik lif
    YUKSEK_INDUKTIF = "hit_dongulu_tip"          # S^1 veya torus homotopi yollari
    UNIVALENT_EVREN = "univalent_evren"          # Esdegerlik = Esitlik (Voevodsky)


class Vecih:
    """
    Bir Vech (İtibar / Modal Lens / Ayar Sektörü)
    """
    def __init__(
        self,
        ad: str,
        mertebe: MertebeSeviyesi,
        tur: str,
        anahtar_kelimeler: List[str],
        boyut: int = 16
    ):
        self.ad = ad
        self.mertebe = mertebe
        self.tur = tur
        self.anahtar_kelimeler = anahtar_kelimeler
        self.boyut = boyut

    def __repr__(self) -> str:
        return f"<Vecih '{self.ad}' ell={self.mertebe.value} tur={self.tur}>"


class VecihSpektrumu:
    """
    Nesnenin Ontolojik Lif Demeti: |A> = sum_v |A^(v)> (x) |v>
    Ve girdi dizisinden Y_m en uygun vechin secimi:
    v* = argmax [ G_gaye * K_tenasup * D_insikak ]
    """
    def __init__(self, vecihler: Optional[List[Vecih]] = None):
        self.vecihler = vecihler or self._varsayilan_vecihler()

    def _varsayilan_vecihler(self) -> List[Vecih]:
        return [
            Vecih("isim", MertebeSeviyesi.NOKTA, "ayrik_etiket", ["ad", "unvan", "etiket", "harf", "kelime"]),
            Vecih("maas", MertebeSeviyesi.UZAY, UzayTuru.OKLID.value, ["maas", "para", "ucret", "lira", "miktar", "hesap", "fiyat"]),
            Vecih("boyut_sayi", MertebeSeviyesi.UZAY, UzayTuru.OKLID.value, ["sayi", "adet", "uzunluk", "ebat", "hacim", "boy"]),
            Vecih("geometrik_donme", MertebeSeviyesi.UZAY, UzayTuru.LIE_MANIFOLDU.value, ["dondur", "simetri", "aci", "yon", "faz", "d4", "ayna"]),
            Vecih("rutbe", MertebeSeviyesi.KATEGORI, KategoriTuru.POSET.value, ["rutbe", "amir", "memur", "makam", "terfi", "yetki", "sirket"]),
            Vecih("nedensellik", MertebeSeviyesi.KATEGORI, KategoriTuru.DAG.value, ["cunku", "illet", "sebep", "netice", "dolayisiyla", "sonuc"]),
            Vecih("takva", MertebeSeviyesi.TIP, TipTuru.SIGMA_BAGIMLI.value, ["takva", "ihlas", "niyet", "deruni", "nefis", "muhasebe", "ahlak"]),
            Vecih("hakikat", MertebeSeviyesi.TIP, TipTuru.UNIVALENT_EVREN.value, ["burhan", "delil", "kanun", "kulliyat", "hukum", "adalet"])
        ]

    def gaye_cekimi(self, vecih: Vecih, metin_dizisi: List[str]) -> float:
        """G_gaye(v | Y): Dizideki terimlerin bu veche teleolojik akisi"""
        puan = 0.0
        for kelime in metin_dizisi:
            k_low = kelime.lower()
            for anahtar in vecih.anahtar_kelimeler:
                if anahtar in k_low or k_low in anahtar:
                    puan += 1.0
        return 1.0 + puan

    def tenasup_agi(self, vecih: Vecih, metin_dizisi: List[str]) -> float:
        """K_tenasup(v | Y): Rezonans ve cagrısim kuvveti"""
        if not metin_dizisi:
            return 1.0
        eslesen = 0
        for kelime in metin_dizisi:
            if any(a in kelime.lower() for a in vecih.anahtar_kelimeler):
                eslesen += 1
        return 0.5 + (eslesen / max(1, len(metin_dizisi)))

    def insikak_kuvveti(self, vecih: Vecih, nesne_a: Any, nesne_b: Any) -> float:
        """D_insikak(v | A, B) = 1 - |<A^(v) | B^(v)>|^2"""
        if nesne_a == nesne_b:
            return 0.05  # Ayrişmazlarin ayniyeti (Leibniz)
        return 0.95

    def vecih_sec(
        self,
        metin_dizisi: List[str],
        nesne_a: Any = None,
        nesne_b: Any = None
    ) -> Tuple[Vecih, Dict[str, float]]:
        """
        v* = argmax [ G_gaye * K_tenasup * D_insikak ]
        """
        en_iyi_skor = -1.0
        en_iyi_vecih = self.vecihler[0]
        skorlar = {}

        for v in self.vecihler:
            g = self.gaye_cekimi(v, metin_dizisi)
            k = self.tenasup_agi(v, metin_dizisi)
            d = self.insikak_kuvveti(v, nesne_a, nesne_b)
            skor = g * k * d
            skorlar[v.ad] = round(skor, 3)
            if skor > en_iyi_skor:
                en_iyi_skor = skor
                en_iyi_vecih = v

        return en_iyi_vecih, skorlar

    def tomita_takesaki_zit_vecih(self, vecih: Vecih) -> Vecih:
        """
        J-aynası: J M_v J = M_v' (Madde <-> Mana zıt kutup dengelemesi)
        """
        eslesmeler = {
            "maas": "takva",
            "takva": "maas",
            "rutbe": "hakikat",
            "hakikat": "rutbe",
            "isim": "nedensellik",
            "nedensellik": "isim",
            "boyut_sayi": "geometrik_donme",
            "geometrik_donme": "boyut_sayi"
        }
        hedef_ad = eslesmeler.get(vecih.ad, "hakikat")
        for v in self.vecihler:
            if v.ad == hedef_ad:
                return v
        return vecih

    def diziden_kaide_istihraci(self, metin_dizisi: List[str], vecih: Vecih) -> Dict[str, Any]:
        """
        Fasıl IV: 3. Kademe - Kaidelerin diziden bizzat istihracı
        1. Metrik kaidesi (Fisher yaklaşma maliyeti)
        2. Komütatör kaidesi ([X_a, X_b] sıra direnci)
        3. Sol Kan Uzantısı (Geçişlilik / Evrensel Kural)
        """
        m = len(metin_dizisi)
        sira_duyarliligi = False
        if vecih.mertebe in [MertebeSeviyesi.KATEGORI, MertebeSeviyesi.TIP]:
            sira_duyarliligi = True

        gecisli_kural = "x R y ve y R z => x R z (Transitive)" if sira_duyarliligi else "x ~ y (Symmetric)"
        
        return {
            "vecih": vecih.ad,
            "mertebe": vecih.mertebe.name,
            "tur": vecih.tur,
            "komutatif_mi": not sira_duyarliligi,
            "kan_uzantisi_kurali": gecisli_kural,
            "metrik_turu": "Oklid ds^2 = sum dx_i^2" if vecih.tur == UzayTuru.OKLID.value else "Fubini-Study / Berry Akisi"
        }
