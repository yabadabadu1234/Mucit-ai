"""
KÜLLÎ DİMAĞ -- YEREL VE GENEL TÂLİM MOTORU (PADİŞAH TÂLİM)
Dosya: main/egitim.py

Vazifesi:
  Girdi verilerini (lisan, kod, 2D ızgara) ``tiktoken`` ve 2D izafî
  komşulukla okur; HDTF ikili ağaç katlamasıyla QTT süperpozisyonuna
  alır; 44 meleke ve dörtlü topolojik zırhlı ``Ĥ_Dimağ`` operatörünü
  QSVT dinamik Gibbs, STA karşıt-adiyabatik sürüş ve GCL/FCT kapalı
  formunda eğitir.

===================================================================
AKIŞ -- ŞEMANIN BABLARI, TEK HATTA
===================================================================

    BAB VI   TAKSİMAT  22.000.000 sanal kübit **tek** zincirde
                       (`nefs/taksimat.py`)
    BAB I    |D⟩       2D izafî bağlam + tiktoken (`nefs/lisan.py`),
                       HDTF katlaması (`kuantum/katlama.py`)
    BAB VII  |m⟩       44 meleke → Ĥ_Dimağ (`nefs/melekeler.py`)
    BAB IV   ZIRH      Sheaf / Betti / Kohomoloji / Homotopi
                       (`ogrenme/zirh.py`)
    BAB V    QSVT      Gibbs soğutması, statik faz cetveli
                       (`kuantum/qsvt.py`)
    BAB VI   STA       Karşıt-adiyabatik sürüş (`ogrenme/sta.py`)
    BAB V.5  FCT       GCL düğümlerinde kapalı form, κ = 1
                       (`ogrenme/fct.py`)

===================================================================
İKİ TÂLİM VARDIR VE İKİSİ AYRI ŞEYDİR -- KARIŞTIRILMAZ
===================================================================

1. **Küllî tâlim** (bu dosyanın ``KulliDalgaTalimMotoru``su): bütün
   veriyi tek dalgaya katlayıp ``Ĥ_Dimağ``ın 44 meleke parametresini
   eğitir. Neticesi diske mühürlenir.
2. **Görev tâlimi** (`main/cikarim.py`nin ``dalga_kur``u): tek bir
   ARC görevinin şahitlerinden o göreve mahsus ağırlık çıkarır.

**Ölçülmüş hakikat, saklamıyorum:** ARC görevlerini fiilen çözen
şimdilik **ikincisidir** (``3618c87e``, sırf ağırlıktan, birebir).
Küllî tâlimin ARC çözümüne katkısı **ölçülmemiştir**; ölçülmemiş bir
katkıyı varmış gibi göstermek kullanıcının C hükmünün ihlâli olurdu.
Bu dosya küllî tâlimi koşturur ve ölçüsünü basar; çözdüğünü iddia
etmez.
"""
from __future__ import annotations

import os
import sys
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from idrak import arc
from kuantum.katlama import hiyerarsik_ikili_agac_katlama
from kuantum.qsvt import qsvt_gibbs_sogutma, statik_faz_tablosu_oku
from nefs.lisan import IzafiMevki2D, tiktoken_2d_kodla
from nefs.melekeler import KulliMelekeManifoldu, melekeleri_kur
from ogrenme.fct import (gauss_chebyshev_lobatto_dugumleri,
                         hizli_chebyshev_donusumu)
from ogrenme.sta import karsit_adiyabatik_surus
from ogrenme.zirh import DortluTopolojikZirh

__all__ = ["TalimAyarlari", "KulliDalgaTalimMotoru", "ana_talim_kosusu",
           "gorev_talimi"]


@dataclass
class TalimAyarlari:
    """Tâlim motorunun analitik ve donanımsal ölçüleri."""
    sanal_kubit_sayisi: int = 22_000_000
    bag_boyutu_chi: int = 16
    qsvt_derecesi: int = 32          # cetveldeki derece; arama yasak
    beta_maksimum: float = 4.0       # cetvelde mühürlü β
    gcl_nokta_sayisi: int = 128
    lambda_mizan: float = 0.035
    ogrenme_orani: float = 0.01


class KulliDalgaTalimMotoru:
    """Tek akış, tek ferman: belirlenimci kuantum dalga tâlimi."""

    def __init__(self, ayarlar: Optional[TalimAyarlari] = None) -> None:
        self.ayar = ayarlar or TalimAyarlari()
        self.meleke_manifoldu = melekeleri_kur(meleke_sayisi=44)
        self.topolojik_zirh = DortluTopolojikZirh()
        self.izafi_mevki = IzafiMevki2D()
        self.faz_tablosu = statik_faz_tablosu_oku(
            derece=self.ayar.qsvt_derecesi, beta=self.ayar.beta_maksimum)
        self.gcl_dugumleri = gauss_chebyshev_lobatto_dugumleri(
            M=self.ayar.gcl_nokta_sayisi)

    # -- BAB I: veri durumu ---------------------------------------------
    def veri_durumu_hazirla(self, ham_veriler: Sequence[Dict[str, object]]
                            ) -> Dict[str, object]:
        """Veri kümesini HDTF ikili ağaç katlamasıyla QTT'ye al.

        Dönen sözlükte ``kesme`` vardır ve **saklanmaz**: HDTF sadakati
        ``L`` büyüdükçe sabit ``χ``de düşer (ölçülmüş kaide
        ``χ ≈ 2√L``). Kesme değeri o kaybın kendisidir.
        """
        t0 = time.perf_counter()
        vektorler: List[np.ndarray] = []
        for v in ham_veriler:
            if "izgara" in v:
                vek = self.izafi_mevki.durum_vektoru_kur(
                    np.asarray(v["izgara"], dtype=int))
            else:
                vek = tiktoken_2d_kodla(str(v.get("metin", "")))
            if np.asarray(vek).size:
                vektorler.append(np.asarray(vek, float).reshape(-1))
        if not vektorler:
            raise ValueError("katlanacak veri yok")

        cek, kesme, kademe = hiyerarsik_ikili_agac_katlama(
            vektorler, bag_boyutu=self.ayar.bag_boyutu_chi,
            sanal_kubit=self.ayar.sanal_kubit_sayisi)
        sure = time.perf_counter() - t0
        print("  [HDTF] %d veri parçası %.3f sn'de QTT'ye katlandı "
              "(kademe %d, kesme %.4e)."
              % (len(vektorler), sure, kademe, kesme), flush=True)
        return {"cekirdek": cek, "kesme": float(kesme),
                "kademe": int(kademe), "süre_sn": sure,
                "parca": len(vektorler)}

    # -- BAB III-VI: tek makro dalga adımı ------------------------------
    def talim_adimi_icra_et(self, durum: Dict[str, object]
                            ) -> Dict[str, float]:
        """Bab III, IV, V, VI gereğince tek makro QSVT dalga adımı."""
        t0 = time.perf_counter()

        # 1. 44 meleke Lie cebri ve 20 mertebeli Ĥ_Dimağ
        H_dimag = self.meleke_manifoldu.hamiltonyen_uret()

        # 2. Dörtlü topolojik zırh
        H_zirhli, zirh_raporu = self.topolojik_zirh.tatbik_et(H_dimag)

        # 3. Mizan dengesi (normalize BGCM)
        mizan = self.meleke_manifoldu.bgcm_mizan_enerjisi()
        H_toplam = H_zirhli + self.ayar.lambda_mizan * mizan * np.eye(
            H_zirhli.shape[0])

        # 4. QSVT dinamik Gibbs soğutması
        cek = durum["cekirdek"]
        v = np.asarray(cek[0], float).reshape(-1)
        v = v[:H_toplam.shape[0]] if v.size >= H_toplam.shape[0] else \
            np.pad(v, (0, H_toplam.shape[0] - v.size))
        sogutulmus = qsvt_gibbs_sogutma(v, H_toplam, self.faz_tablosu,
                                        beta_maks=self.ayar.beta_maksimum)

        # 5. Tıkanma varsa STA karşıt-adiyabatik sürüşü
        surus = False
        if float(zirh_raporu.get("kohomoloji_tikaniklik", 0.0)) > 0.4:
            sogutulmus = karsit_adiyabatik_surus(sogutulmus, H_toplam,
                                                 sure_tau=1.0)
            surus = True
            print("  [STA] Kohomolojik tıkanıklık teşhis edildi; bariyer "
                  "O(1) zamanda tünellendi.", flush=True)

        # 6. GCL düğümlerinde FCT kapalı form katsayı intâcı (κ ≡ 1)
        ornek = np.interp(self.gcl_dugumleri,
                          np.linspace(-1.0, 1.0, len(sogutulmus)),
                          np.asarray(sogutulmus, float).reshape(-1))
        katsayi = hizli_chebyshev_donusumu(ornek)
        self.meleke_manifoldu.katsayilari_guncelle(
            katsayi, oran=self.ayar.ogrenme_orani)

        return {"adim_suresi_sn": time.perf_counter() - t0,
                "topolojik_kayip": float(zirh_raporu.get("toplam_kayip", 0.0)),
                "sheaf": float(zirh_raporu.get("sheaf_uyumsuzluk", 0.0)),
                "betti_delik": float(zirh_raporu.get("betti_delik_sayisi", 0.0)),
                "kohomoloji_hata": float(
                    zirh_raporu.get("kohomoloji_tikaniklik", 0.0)),
                "homotopi": float(zirh_raporu.get("homotopi_burulma", 0.0)),
                "bgcm_mizan": float(mizan),
                "sta_surusu": float(surus),
                "hdtf_kesme": float(durum.get("kesme", 0.0))}

    def agirliklari_kaydet(self, dosya_yolu: str) -> None:
        """Öğrenilen meleke Lie parametrelerini diske mühürle."""
        dizin = os.path.dirname(dosya_yolu)
        if dizin:
            os.makedirs(dizin, exist_ok=True)
        np.save(dosya_yolu, self.meleke_manifoldu.parametreler_vektoru())
        print("  [MÜHÜR] 44 meleke ağırlığı kaydedildi: %s"
              % dosya_yolu, flush=True)


# =====================================================================
#  GÖREV TÂLİMİ -- ARC görevini fiilen çözen hat
# =====================================================================
def gorev_talimi(gorev, devir: int = 120):
    """Tek bir görevin şahitlerinden o göreve mahsus dalgayı çıkar.

    Küllî tâlimden **ayrı** bir iştir ve ayrı olduğu söyleniyor: küllî
    tâlim 44 meleke parametresini eğitir, bu ise o görevin ``W``sini.
    ARC'de fiilen ölçülmüş çözüm bu hattan gelmiştir.
    """
    from main.cikarim import dalga_kur
    cift = [(np.asarray(a, int), np.asarray(b, int))
            for a, b in getattr(gorev, "egitim", [])]
    return dalga_kur(cift, devir=int(devir))


def ana_talim_kosusu(model_cikis_yolu: str = "depo/kulli_dimag_agirlik.npy",
                     kume: str = "training", ornek: int = 30,
                     cevrim: int = 3) -> str:
    """Küllî tâlimi koştur ve **ölçüsünü** bas."""
    print("=== KÜLLÎ DİMAĞ: BELİRLENİMCİ DALGA TÂLİMİ ===", flush=True)
    motor = KulliDalgaTalimMotoru()

    gorevler = arc.yukle_hepsi(kume)[:int(ornek)]
    ham = [{"izgara": g.egitim[0][0]} for g in gorevler if g.egitim]
    durum = motor.veri_durumu_hazirla(ham)

    satir = []
    for c in range(int(cevrim)):
        n = motor.talim_adimi_icra_et(durum)
        satir.append(n)
        print("  [ÇEVRİM %d] %.4f sn | zırh %.6f | sheaf %.4f | betti %.0f "
              "| koho %.4f | mizan %.6f"
              % (c + 1, n["adim_suresi_sn"], n["topolojik_kayip"],
                 n["sheaf"], n["betti_delik"], n["kohomoloji_hata"],
                 n["bgcm_mizan"]), flush=True)
    motor.agirliklari_kaydet(model_cikis_yolu)

    ilk, son = satir[0], satir[-1]
    s = ["", "=== KÜLLÎ TÂLİM NETİCESİ ===", "",
         "  veri parçası    : %d" % durum["parca"],
         "  HDTF kademe     : %d" % durum["kademe"],
         "  HDTF kesme      : %.4e  (χ=%d'de kayıp -- saklanmıyor)"
         % (durum["kesme"], motor.ayar.bag_boyutu_chi),
         "  zırh kaybı      : %.6f → %.6f"
         % (ilk["topolojik_kayip"], son["topolojik_kayip"]),
         "  BGCM mizanı     : %.6f → %.6f"
         % (ilk["bgcm_mizan"], son["bgcm_mizan"]),
         "  STA sürüşü      : %d çevrimde tetiklendi"
         % int(sum(x["sta_surusu"] for x in satir)),
         "",
         "  HAD: küllî tâlimin ARC çözümüne katkısı ÖLÇÜLMEMİŞTİR.",
         "  Fiilen çözen hat `gorev_talimi`dir (bkz. main/cikarim.py)."]
    return "\n".join(s)


if __name__ == "__main__":                               # pragma: no cover
    cikis = sys.argv[1] if len(sys.argv) > 1 else \
        "depo/kulli_dimag_agirlik.npy"
    print(ana_talim_kosusu(cikis))
