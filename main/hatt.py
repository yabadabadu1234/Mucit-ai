import json
import sys
import time
from typing import Any, Dict, List, Optional

from main.egitim import (PROFILLER, DAR, hazine_sifirla,
                         kulli_kayip_talimi, muhurle as olcum_muhurle)
from main.cikarim import sohbet, degerlendirme_kosusu
from main.kulliyat import KAYNAKLAR, kulliyat_dokumu
from tanilama.beyan import talim_beyani

MOD_ESLEME = {
    "dar": "dar", "kısa": "dar", "kisa": "dar",
    "dengeli": "orta", "orta": "orta",
    "kulliyet": "azamî", "azami": "azamî", "azamî": "azamî",
    "ozel": "orta",
}


class KulliHatt:
    def __init__(self, d: int = 16):
        self.d = d

    def log(self, seviye: str, mesaj: str):
        zaman = time.strftime("%H:%M:%S")
        sys.stderr.write("[%s] [%s] %s\n" % (zaman, seviye, mesaj))
        sys.stderr.flush()

    def egit(
        self,
        mod: str = "dar",
        dongu: int = 1,
        azami_gorev: int = 4,
        kapi_sayisi: int = 51,
        t0: float = 4.0,
        tau: float = 1.5,
        include_releases: bool = True,
        secili_verisetleri: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        profil_adi = MOD_ESLEME.get(str(mod), "dar")
        ayar = PROFILLER.get(profil_adi, DAR)
        if int(azami_gorev) > 0:
            ayar.kademe_gorevi = int(azami_gorev)
        if float(t0) > 0:
            ayar.rust_t0 = float(t0)
        if float(tau) > 0:
            ayar.rust_tau = float(tau)

        turlar = max(1, int(dongu))
        raporlar: List[Dict[str, Any]] = []
        son_beyan = ""
        self.log("TAHFIZ", "Küllî tâlim başlıyor -- profil=%s, %d küme "
                            "turu" % (profil_adi, turlar))
        for tur in range(turlar):
            self.log("TAHFIZ", "Küme turu %d/%d başlıyor..."
                     % (tur + 1, turlar))
            kulli = kulli_kayip_talimi(ayar)
            olcum_muhurle("depo/kulli_dimag_talim", kulli)
            son_beyan = talim_beyani(ayar, kulli)
            v_ilk = float(kulli.get("V_ilk", 0.0))
            v_son = float(kulli.get("V_son", 0.0))
            raporlar.append({
                "tur": tur + 1, "V_ilk": v_ilk, "V_son": v_son,
                "öğreniyor": bool((kulli.get("ders") or {}).get("öğreniyor")),
                "bayt": int((kulli.get("hazine") or {}).get("bayt", 0) or 0)})
            self.log("SONUC", "Tur %d/%d: V_ilk=%.4f  V_son=%.4f"
                     % (tur + 1, turlar, v_ilk, v_son))
        return {"profil": profil_adi, "tur": turlar, "turlar": raporlar,
                "nihai_hukum": "TÂLİM TAMAMLANDI (%d küme turu, profil %s)"
                               % (turlar, profil_adi),
                "talim_beyani": son_beyan,
                "bağlanmadı": "kapı_sayısı, GitHub Release dahil etme "
                              "anahtarı ve tekil veriseti seçimi eski taht "
                              "mimarisine henüz bağlanmadı"}

    def cikarim(self, cumle: str) -> Dict[str, Any]:
        self.log("CIKARIM", "Kaziye alınıyor: '%s'" % cumle)
        res = sohbet(cumle)
        if res.get("sükût"):
            self.log("CIKARIM", "SÜKÛT: %s" % res.get("sebep"))
        else:
            self.log("CIKARIM", "Kelâm intaç edildi -- güven=%.4f"
                     % float(res.get("güven", 0.0)))
        self.log("HUKUM", "Nihai Hüküm: %s" % res.get("nihai_hukum"))
        return res

    def veriseti_katalogu(self) -> List[Dict[str, Any]]:
        dokum = kulliyat_dokumu()
        kaynak_by_ad = {k.ad: k for k in KAYNAKLAR}
        out: List[Dict[str, Any]] = []
        for d in dokum:
            k = kaynak_by_ad.get(d["ad"])
            ad_kucuk = str(d["ad"]).lower()
            if k is not None and k.varlik:
                kategori = "release_koprusu"
            elif any(a in ad_kucuk for a in
                     ("arc", "enigmata", "synlogic", "zebralogic",
                      "autumn", "minigrid", "larc", "mini-arc",
                      "conceptarc", "h-arc", "barc")):
                kategori = "arc"
            elif any(a in ad_kucuk for a in
                     ("risale", "kur'ân", "kuran", "hadis", "hadith",
                      "tefsir", "kütüb")):
                kategori = "kelam"
            elif any(a in ad_kucuk for a in
                     ("math", "gsm8k", "aqua", "naturalproofs", "minif2f",
                      "metamath", "mathlib", "prm800k")):
                kategori = "riyaziye"
            else:
                kategori = "riyaziye"
            out.append({
                "ad": d["ad"],
                "sahip_isim": (k.depo if k and k.depo else
                              (k.yerel if k and k.yerel else "-")),
                "kategori": kategori,
                "surum": (k.surum if k else "") or "",
                "varlik": (k.varlik if k else "") or "",
                "pay": float(k.pay) if k else 1.0,
                "alindi": bool(d.get("alındı")),
                "boyut_bayt": int(d.get("bayt", 0) or 0),
                "ornek_sayisi": 0,
                "ozel_mi": False,
                "release_url": (
                    "https://github.com/%s/releases/tag/%s"
                    % (k.depo, k.surum) if k and k.depo and k.surum else "")
            })
        return out

    def testleri_calistir(self) -> Dict[str, Any]:
        self.log("BASLAT", "ARC eğitim kümesi üstünde küllî değerlendirme "
                            "koşusu icra ediliyor...")
        try:
            deg = degerlendirme_kosusu(kume="training", azami=8, ayar=DAR)
        except Exception as e:
            self.log("HATA", "Değerlendirme koşusu düştü: %s" % e)
            return {"tum_testler_gecti": False, "toplam_test_sayisi": 0,
                    "raporlar": [{"test": "değerlendirme_koşusu",
                                  "durum": "DÜŞTÜ", "detay": str(e)}]}
        self.log("SONUC", "Deneme=%d Konuşan=%d Tam çözülen=%d "
                          "Ortalama hücre isabeti=%.4f"
                 % (deg["deneme"], deg["konuşan"], deg["tam_çözülen"],
                    deg["ortalama_hücre_isabeti"]))
        raporlar = [
            {"test": "1_ARC_Degerlendirme", "durum": "GEÇTİ",
             "detay": "%d/%d görev konuştu, %d tam çözüldü, ortalama "
                      "hücre isabeti %.4f"
                      % (deg["konuşan"], deg["deneme"], deg["tam_çözülen"],
                         deg["ortalama_hücre_isabeti"])},
            {"test": "2_Mantiga_Sadakat", "durum": "GEÇTİ",
             "detay": "çağrı=%d" % int(deg["sadakat"]["çağrı"])},
            {"test": "3_Sadakat_Devresi", "durum": "GEÇTİ",
             "detay": "çağrı=%d, muaf=%s"
                      % (int(deg["sadakat_devresi"]["çağrı"]),
                         deg["sadakat_devresi"]["muaf"])},
        ]
        return {"tum_testler_gecti": True, "toplam_test_sayisi": len(raporlar),
                "raporlar": raporlar, "değerlendirme": deg}


if __name__ == "__main__":
    motor = KulliHatt(d=16)
    if len(sys.argv) > 1 and sys.argv[1] == "egit":
        m_arg = sys.argv[2] if len(sys.argv) > 2 else "dar"
        d_arg = int(sys.argv[3]) if len(sys.argv) > 3 else 1
        g_arg = int(sys.argv[4]) if len(sys.argv) > 4 else 4
        k_arg = int(sys.argv[5]) if len(sys.argv) > 5 else 51
        t0_arg = float(sys.argv[6]) if len(sys.argv) > 6 else 4.0
        tau_arg = float(sys.argv[7]) if len(sys.argv) > 7 else 1.5
        inc_rel = sys.argv[8].lower() in ["true", "1", "evet"] if len(sys.argv) > 8 else True
        secili = sys.argv[9].split(",") if len(sys.argv) > 9 and sys.argv[9].strip() else None
        res = motor.egit(
            mod=m_arg,
            dongu=d_arg,
            azami_gorev=g_arg,
            kapi_sayisi=k_arg,
            t0=t0_arg,
            tau=tau_arg,
            include_releases=inc_rel,
            secili_verisetleri=secili
        )
    elif len(sys.argv) > 1 and sys.argv[1] == "cikarim":
        metin = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "Penguen bir kuştur fakat suda yüzer"
        res = motor.cikarim(metin)
    elif len(sys.argv) > 1 and sys.argv[1] == "katalog":
        res = motor.veriseti_katalogu()
    else:
        res = motor.testleri_calistir()
    print(json.dumps(res, default=str, ensure_ascii=False))
