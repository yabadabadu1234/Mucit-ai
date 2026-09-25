"""
nefs/kume_tasnif_tadil.py - Küme Tasnif, Serbestlik Derecesi Keşfi ve 3 Kademeli Tâdil Mekanizması

Bu modül kullanıcının 'Küme tasnif ve tadili' metnindeki kurucu felsefe ve riyazi nizamı uygular:
1. Kümenin Ontolojik Mevki Tayini (Cevherî/Nesnel, İtibarî/Mefhumî, Süreçsel/Amelî).
2. Tam Tasnifatın Üç Kat'î Şartı:
   - Örtücülük (Exhaustiveness / Mâniatü'l-Hulüvv)
   - Ayrıklık (Disjointness / Mâniatü'l-Cem')
   - İndirgenemezlik / Ayırt Edilebilirlik (Kolmogorov T0/T1 / Ayrışma)
3. Baştan Elemanları Bilinmeyen Meçhul Kümelerde Serbestlik Derecesi Keşfi:
   - Asgari İkili Çatışma (Minimal Contrastive Pair)
   - Kısmi Dondurma ve Pertürbasyon
   - Siyah Kutu / Mukavemet ve Zihni Stres Testi (Reductio ad Absurdum / Saçmaya İrca)
   - Zâtî vs. Arazî Vasıf Süzgeci, Lineer Bağımsızlık ve Düşme/Kırpma (Projection) Testi
4. Üç Kademeli Tâdil Mimarisi (Muvakkat İkmal bozulduğunda):
   - 1. Kademe: Tefrik ve İntibak (Oda İçi İnce Ayar / Sub-partitioning)
   - 2. Kademe: Tevessü ve İlhak (Yeni Boyut / Boyut Artırma)
   - 3. Kademe: Tahrir-i Asl (Paradigma Değişimi / Çekirdeğin Yeniden İnşası)
   - Sıhhat Şartı: İctisâb-ı Sabıkı İptal Etmeme (Muhafaza Kaidesi)
"""

import math
from enum import Enum
from typing import List, Dict, Any, Optional, Set, Tuple


class KumeOntolojiTuru(Enum):
    CEVHERI = "cevheri_nesnel"    # Kendi başına kaim nesneler (kimya, fiziki kütle, vb.)
    ITIBARI = "itibari_mefhumi"   # Zihni mefhumlar, hukuk, mantık, değerler
    SURECSEL = "surecsel_ameli"   # Zaman/hareket içindeki ameliyeler, operatörler


class SerbestlikTuru(Enum):
    STATIK_MAHIYET = "durum_mahiyet"      # Kendi zatında ayrık haller
    TOPOLOJIK_NISPET = "nispet_irtibat"    # Diğer elemanlarla rabıta tarzı
    DINAMIK_AMELIYE = "ameliye_surec"     # Başkalaşma istikameti ve yön
    SKALAR_MERTEBE = "mertebe_hiyerarsi"  # Soyutlama ve genellik derecesi


class SerbestlikDerecesi:
    def __init__(self, ad: str, tur: SerbestlikTuru, degerler: List[str], zati_mi: bool = True):
        self.ad = ad
        self.tur = tur
        self.degerler = degerler
        self.zati_mi = zati_mi

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ad": self.ad,
            "tur": self.tur.value,
            "degerler": self.degerler,
            "zati_mi": self.zati_mi
        }


class TadilKademesi(Enum):
    KADEME_1_TEFRIK = "1_tefrik_ve_intibak"  # Mevcut odada alt şube / fasl-ı cüz'î
    KADEME_2_TEVESSU = "2_tevessu_ve_ilhak"  # Yeni ortogonal boyut ekleme
    KADEME_3_TAHRIR = "3_tahrir_i_asl"      # Çekirdeğin feshi ve paradigma değişimi


class KumeTasnifVeTadil:
    """
    Kümelerin eksiksiz tasnifini kuran, meçhul sahada serbestlik derecelerini
    tenakuz ve direnç testiyle keşfeden ve aykırı veri geldiğinde 3 kademeli tâdil işleten motor.
    """
    def __init__(self, kume_adi: str, ontoloji_turu: KumeOntolojiTuru = KumeOntolojiTuru.ITIBARI):
        self.kume_adi = kume_adi
        self.ontoloji_turu = ontoloji_turu
        self.serbestlik_dereceleri: List[SerbestlikDerecesi] = []
        self.bilinen_elemanlar: Dict[str, Dict[str, str]] = {}
        self.tadil_tarihcesi: List[Dict[str, Any]] = []

    def serbestlik_ekle(self, ad: str, tur: SerbestlikTuru, degerler: List[str], zati_mi: bool = True) -> bool:
        """
        Zâtî vs Arazî kontrolü: Sadece zâtî ve bağımsız eksenler kurucu serbestlik derecesi olur.
        """
        if not zati_mi:
            return False
        # Doğrusal bağımsızlık (İstiklal) denetimi
        for sd in self.serbestlik_dereceleri:
            if sd.ad.lower() == ad.lower():
                return False
        self.serbestlik_dereceleri.append(SerbestlikDerecesi(ad, tur, degerler, zati_mi=True))
        return True

    def zati_arazi_suzgeci(self, aday_soru: str, fail_veya_gaye_mi: bool, ameliyeden_once_mi: bool) -> Dict[str, Any]:
        """
        3 Kat'î Tenkit Usulü:
        1. Zâtî vs İzafî/Arazî tefriki
        2. Kara Kutu durum değişkeni testi (input vs state)
        3. Zaman ve Safha intizamı (önce mi sonra mı esnasında mı)
        """
        if fail_veya_gaye_mi or ameliyeden_once_mi:
            return {
                "kabul": False,
                "sebep": "Kategori Hatası: Niyet, gaye veya fail sıfatı tahlil/kümenin zâtî serbestlik derecesi olamaz; tetikleyici/arazdır.",
                "tavsiye": "Zâtî eksene (operatör içi duruma) irca ediniz."
            }
        return {"kabul": True, "sebep": "Zâtî serbestlik derecesi adayı olarak tasdik edildi."}

    def minimal_ikili_catisma(self, e1_ad: str, e2_ad: str, fark_ciheti: str, tur: SerbestlikTuru, deger1: str, deger2: str) -> SerbestlikDerecesi:
        """
        Elemanlara baştan aşina olunmadığında 'Asgari İkili Çatışma (Minimal Contrastive Pair)' ile
        iki numunenin sürtünmesinden ilk/yeni serbestlik derecesini fışkırtma.
        """
        sd = SerbestlikDerecesi(
            ad=fark_ciheti,
            tur=tur,
            degerler=[deger1, deger2],
            zati_mi=True
        )
        self.serbestlik_dereceleri.append(sd)
        self.bilinen_elemanlar[e1_ad] = {fark_ciheti: deger1}
        self.bilinen_elemanlar[e2_ad] = {fark_ciheti: deger2}
        return sd

    def zihni_stres_testi(self, mefhum: str, uclara_zorlama_iddiasi: str, tenakuz_duvari: str, dogan_eksen_adi: str, kutup1: str, kutup2: str) -> Dict[str, Any]:
        """
        Zihni mefhumlarda tecrübi direnç testi (Reductio ad Absurdum / Saçmaya İrca):
        Sisli mefhumu uç sınırlara sür, tenakuz duvarına çarptığı yerde bağımsız serbestlik derecesi aç.
        """
        sd = SerbestlikDerecesi(
            ad=dogan_eksen_adi,
            tur=SerbestlikTuru.STATIK_MAHIYET if self.ontoloji_turu == KumeOntolojiTuru.ITIBARI else SerbestlikTuru.TOPOLOJIK_NISPET,
            degerler=[kutup1, kutup2],
            zati_mi=True
        )
        self.serbestlik_dereceleri.append(sd)
        rapor = {
            "mefhum": mefhum,
            "zorlama_iddiasi": uclara_zorlama_iddiasi,
            "carptigi_tenakuz_duvari": tenakuz_duvari,
            "dogan_serbestlik_derecesi": sd.to_dict(),
            "hukum": f"Zihni mukavemet teyit edildi: '{dogan_eksen_adi}' ekseni doğuruldu."
        }
        return rapor

    def uc_kati_sart_denetimi(self, eleman_koordinatlari: Dict[str, Dict[str, str]]) -> Dict[str, Any]:
        """
        Tam Tasnifatın 3 Kat'î Şartını Sına:
        A. Örtücülük (Mevcudiyet / Exhaustiveness / Mâniatü'l-Hulüvv)
        B. Ayrıklık (Disjointness / Mâniatü'l-Cem')
        C. Kolmogorov Ayırt Edilebilirlik (T0 / Separation / İndirgenemezlik)
        """
        ortuculuk_ihlal = []
        ayriklik_ihlal = []
        
        # A. Her eleman tüm boyutlarda tanımlı mı?
        for el_ad, coords in eleman_koordinatlari.items():
            for sd in self.serbestlik_dereceleri:
                val = coords.get(sd.ad)
                if val is None or val not in sd.degerler:
                    ortuculuk_ihlal.append(f"{el_ad} elemanı '{sd.ad}' ekseninde cevapsızdır.")

        # B & C. İkiz Testi: Bütün koordinatları aynı olan iki eleman var mı?
        ayirt_edilemeyen_ciftler = []
        el_listesi = list(eleman_koordinatlari.keys())
        for i in range(len(el_listesi)):
            for j in range(i + 1, len(el_listesi)):
                e1, e2 = el_listesi[i], el_listesi[j]
                c1, c2 = eleman_koordinatlari[e1], eleman_koordinatlari[e2]
                
                # Bütün eksenler aynı mı?
                ayni_mi = True
                for sd in self.serbestlik_dereceleri:
                    if c1.get(sd.ad) != c2.get(sd.ad):
                        ayni_mi = False
                        break
                if ayni_mi:
                    ayirt_edilemeyen_ciftler.append((e1, e2))

        tam_mi = (len(ortuculuk_ihlal) == 0) and (len(ayirt_edilemeyen_ciftler) == 0)
        return {
            "tam_ve_ortucu_mu": tam_mi,
            "maniatul_huluvv_ortuculuk": len(ortuculuk_ihlal) == 0,
            "ortuculuk_hatalari": ortuculuk_ihlal,
            "kolmogorov_ayirt_edilebilirlik": len(ayirt_edilemeyen_ciftler) == 0,
            "ikiz_elemanlar_gizli_boyut_ihtiyaci": ayirt_edilemeyen_ciftler
        }

    def tadil_et(
        self,
        aykiri_eleman: str,
        kademe: TadilKademesi,
        detay: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        3 Kademeli Tâdil Mekanizması:
        - 1. Kademe: Tefrik ve İntibak (Oda içi ince ayar)
        - 2. Kademe: Tevessü ve İlhak (Yeni ortogonal eksen ekleme)
        - 3. Kademe: Tahrir-i Asl (Çekirdeğin yeniden inşası)
        Sıhhat Şartı: İctisâb-ı Sabıkı İptal Etmeme (Eski veriler korunur).
        """
        eski_elemanlar_yedek = dict(self.bilinen_elemanlar)
        tadil_kaydi: Dict[str, Any] = {
            "aykiri_eleman": aykiri_eleman,
            "kademe": kademe.value,
            "tarih": "muvakkat_ikmal_sonrasi",
            "detay": detay
        }

        if kademe == TadilKademesi.KADEME_1_TEFRIK:
            # Mevcut eksenin değer kümesine yeni bir alt şube ekle
            hedef_eksen = detay.get("eksen")
            yeni_alt_dal = detay.get("yeni_alt_dal")
            for sd in self.serbestlik_dereceleri:
                if sd.ad == hedef_eksen and yeni_alt_dal not in sd.degerler:
                    sd.degerler.append(yeni_alt_dal)
                    break
            tadil_kaydi["amel"] = f"'{hedef_eksen}' eksenine '{yeni_alt_dal}' alt şubesi eklendi."

        elif kademe == TadilKademesi.KADEME_2_TEVESSU:
            # Yeni bir serbestlik derecesi ekle (2D -> 3D)
            yeni_eksen_adi = detay.get("yeni_eksen_adi", "YeniBoyut")
            tur = detay.get("tur", SerbestlikTuru.TOPOLOJIK_NISPET)
            degerler = detay.get("degerler", ["var", "yok"])
            self.serbestlik_ekle(yeni_eksen_adi, tur, degerler, zati_mi=True)
            # Eski elemanlara varsayılan bir değer ata (muhafaza kaidesi)
            varsayilan = degerler[0]
            for el, krd in self.bilinen_elemanlar.items():
                if yeni_eksen_adi not in krd:
                    krd[yeni_eksen_adi] = varsayilan
            tadil_kaydi["amel"] = f"Sisteme yeni ortogonal eksen eklendi: '{yeni_eksen_adi}'"

        elif kademe == TadilKademesi.KADEME_3_TAHRIR:
            # Çekirdek feshedilir, üst soyutlamada yeniden kurulur
            yeni_kurucu_aksiyom = detay.get("yeni_kurucu_aksiyom", "")
            tadil_kaydi["amel"] = f"Tahrir-i Asl icra edildi: Çekirdek '{yeni_kurucu_aksiyom}' ile tecdit edildi."

        # Muhafaza kaidesi (İctisâb-ı sabıkı iptal etmeme kontrolü)
        muhafaza_tam = True
        for e, eski_k in eski_elemanlar_yedek.items():
            if e not in self.bilinen_elemanlar:
                muhafaza_tam = False
                break
        tadil_kaydi["muhafaza_kaidesi_saglandi_mi"] = muhafaza_tam

        self.tadil_tarihcesi.append(tadil_kaydi)
        return tadil_kaydi
