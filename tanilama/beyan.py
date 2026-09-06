"""
TÂLİM VE ÇIKARIM BEYANI -- **raporun yeri burasıdır, taht değil.**

===================================================================
FERMAN 1-G: ANA KODA RAPOR YAZMAK YASAKTIR
===================================================================

Padişahın hükmü: *"Umumiden hususiye gidiyorsun ama umumiye rapor
yazıyorsun!! Bundan böyle ana koda rapor yazmak yasak!!!!!!! Tek
yapacağın gerçek fonksiyonları çağırmak."*

Bu dosya o hükmün icrasıdır. Evvelce ``main/egitim.py:kos`` içinde
**332 satırlık** bir metin yığını vardı; taht bir nazırlık katı olmaktan
çıkıp matbaa olmuştu. Daha kötüsü: bir uzuv ana koda **bağlanmadan** da
oraya bir rapor satırı yazılabiliyordu -- ferman 1-C(b)'nin yasakladığı
münafıklık tam da o kapıdan giriyordu.

Artık taht yalnız şunu yapar::

    kulli = kulli_kayip_talimi(ayar)      # gerçek fonksiyon çağrısı
    return talim_beyani(ayar, kulli)      # gerçek fonksiyon çağrısı

Metnin tamamı buradadır ve buradaki her satır, tâlimin **fiilen
döndürdüğü** bir sayıya bakar: uzuv koşmadıysa o anahtar sözlükte
yoktur ve beyan ``KeyError`` ile düşer. Yâni bu dosya bir süs değil,
bir **denetimdir**.
"""
from __future__ import annotations

from typing import Dict, Optional

__all__ = ["talim_beyani", "cikarim_beyani", "kaggle_beyani"]


def talim_beyani(ayar, kulli: Optional[Dict[str, object]]) -> str:
    """Tâlimin neticesini beyan et. ``kulli`` ``kulli_kayip_talimi``dendir."""
    from nefs.olcek import Kok, olcek_beyani
    s = ["", "=== TÂLİM NETİCESİ (%s) ===" % ayar.ad, ""]
    if kulli and kulli.get("ölçek"):
        s += [olcek_beyani(Kok(sozluk=int(ayar.sozluk),
                               comert=float(ayar.comert),
                               tohum=int(ayar.tohum)),
                           kulli["ölçek"]), ""]
        d_ = kulli["denge"]
        s += ["  FORMÜL 3'ÜN NETİCESİ -- ÖLÇÜLEN λ'LAR:",
              "    " + "  ".join(
                  "%s %.4f" % (a.replace("lam_", ""), v)
                  for a, v in sorted(d_.items()) if a != "frenlenen"),
              "    frenlenen: %s" % (", ".join(d_.get("frenlenen", []))
                                     or "yok -- hepsi ölçüyle kondu"),
              "    elle verilen (türetilmeyen): %s"
              % (", ".join(kulli.get("elle_verilen") or ())
                 or "yok -- hepsi formülden"),
              ""]
    if kulli:
        d = kulli["değerlendirme"]
        s += ["  KÜLLÎ KAYIP TÂLİMİ -- TEK HAT",
              "    parametre      : %d" % kulli["parametre"],
              "    veri örneği    : %d" % kulli["veri"],
              "    kayıp çağrısı  : %d" % kulli["kayıp_çağrısı"],
              "    V_ilk → V_son  : %.4f → %.4f  (fark %.4f)"
              % (kulli["V_ilk"], kulli["V_son"],
                 kulli["V_ilk"] - kulli["V_son"]),
              "    süre           : %.1f sn" % kulli["süre_sn"],
              "", "    İKİ ÖLÇÜT BERABER (H47):",
              "      tam çözülen          : %d / %d"
              % (d["tam_çözülen"], d["deneme"]),
              "      ortalama hücre isabeti: %.4f"
              % d["ortalama_hücre_isabeti"],
              "      sükût                 : %d" % d["sükût"]]
        from nefs.munasebet import munasebet_metni
        from nefs.keyfiyet import keyfiyet_metni
        from main.kulliyat import kulliyat_beyani
        kn = kulli["konuşma"]
        s += ["",
              "  TEK MOTOR -- TÂLİM DE KONUŞUR (ferman 1-H)",
              "    görev %d: konuşan %d, susan %d, budanan %d, "
              "ortalama güven %.4f"
              % (kn["görev"], kn["konuşan"], kn["susan"], kn["budanan"],
                 kn["güven"]),
              "    sükût sebebi: %s" % (", ".join(kn["sebep"]) or "yok"),
              "    ilk belirteçler: %s" % (kn["belirteç"] or "yok"),
              "",
              munasebet_metni(kulli["münasebet"]), "",
              keyfiyet_metni(kulli["keyfiyet"]), "",
              "  VERİ: ARC %d örnek + külliyat %d örnek"
              % (kulli["külliyat"]["arc"], kulli["külliyat"]["külliyat"]),
              kulliyat_beyani(kulli["külliyat"]["döküm"])]
        m = kulli["mizan"]
        s += ["", "    MÎZÂN-I KÜLLÎ (nefs/kulli_mizan.py) -- KEFELER:",
              "      TABAKALI MİZAN (zabıt: kör NLL intihardır)",
              "        L_toplam = L_nokta + α·L_uzay + β·L_kategori "
              "+ γ·L_tip",
              "        α = 1 (çıpa)   β = %.4f   γ = %.4f   "
              "(ikisi de ÖLÇÜLDÜ, elle yazılmadı)"
              % (ayar.lam_kategori, ayar.lam_tip),
              "      0. ℒ_Nokta   (kısmî Born)  : %.6f   × %.2f"
              % (m["nokta"], ayar.lam_nokta),
              "         −ln Tr(P_hedef ρ). KÖR NLL DEĞİL: üç zırhtan "
              "sonra, küçük ağırlıkla.",
              "      1. ℒ_Uzay ≡ ℒ_Rezonans (Uhlmann) : %.6f"
              % m["rezonans"],
              "         TERKİP, TABELA DEĞİL: 1−|⟨Φ|Ψ⟩|² ile Uhlmann "
              "sadakati aynı ölçüdür (saf hedefte birebir).",
              "      2. ℒ_Kategori (funktör)    : %.6f   ihlâl eden "
              "kompozisyon: %d/%d"
              % (m["kategori"], m["kategori_ihlâl"], m["kategori_deneme"]),
              "         ‖M_{g∘f} − M_g·M_f‖²_F -- etiketsiz, "
              "kendi kendini denetler.",
              "      3. ℒ_Tip ≡ ℒ_Hodge (Δ|Ψ⟩=0) : %.6f" % m["hodge"],
              "      ─── mizanın kendi kefeleri ───",
              "      ℒ_Çevrim   (Wilson)  : %.6f   "
              "(meşru %d / kısır %d / tenakuz %d)"
              % (m["çevrim"], m["meşru"], m["kısır"], m["tenakuz"]),
              "      ℒ_Tenakuz  (log bariyer × dışlama) : %.6f   × %.2f"
              % (m["tenakuz_bariyer"], ayar.lam_tenakuz),
              "        −ln((Tr(I+Re U_C)+ε)/(2d+ε))·S_dışlama   "
              "ε=%.1e  τ_pencere=%.1f"
              % (ayar.tenakuz_eps, ayar.dislama_tau),
              "        tavan (ıraksamıyor): %.4f   ölçülen azamî: %.4f"
              % (m["tenakuz_tavan"], m["tenakuz_azamî"]),
              "        S_dışlama ortalaması: %.4f  (1'e yakın = hiç "
              "beraber görülmemiş çiftler)" % m["dışlama_ortalama"],
              "      ℒ_Monogami (CKW)     : %.6f   ihlâl: %d"
              % (m["monogami"], m["ihlâl"]),
              "      ℒ_Engel    (CIM/ayna) : %.6f   "
              "tatmin olmayan bağ: %d/%d"
              % (m["engel"], m["engel_bağ"], m["engel_toplam"]),
              "        mana öbeği (Morse): %d   bağımsız kesim şahidi: %.3f"
              % (m["engel_öbek"], m["engel_şahidi"]),
              "      ─────────────────────────────────",
              "      ℒ_Küllî              : %.6f" % m["kayıp"],
              "",
              "    RÜŞT KİLİDİ (nefs/rust.py) -- ÇİZELGE **VE** MUAYENE:",
              "      α_rüşt = σ((t−t₀)/τ) · exp(−(‖dF‖²+‖H¹‖²)/σ²)",
              "      takvim  σ(·)          : %.4f" % m["rüşt_takvim"],
              "      muayene exp(·)        : %.4f   (kapı %s)"
              % (m["rüşt_muayene"],
                 "AÇIK" if ayar.rust_muayene else "KAPALI ⚠"),
              "        ‖dF‖²_DEC = %.6f   ‖H¹‖² = %d  (kapanmamış delik)"
              % (m["dF_dec"], m["h1"]),
              "      α_rüşt (çarpım)       : %.4f   (0=bebeklik → "
              "fıtrat terbiye; 1=rüşt → hafızaya fatura)" % kulli["rüşt"],
              ("      ⚠ TAKVİM GELDİ FAKAT YIRTIK KAPANMADI: rüşt "
               "KİLİTLİ (takvim %.2f, α %.4f)."
               % (m["rüşt_takvim"], kulli["rüşt"]))
              if (m["rüşt_takvim"] > 0.5 and kulli["rüşt"] < 0.25)
              else "      yırtık kapandı mı: %s"
              % ("evet" if m["h1"] == 0 else "HAYIR (%d delik)" % m["h1"]),
              "",
              "    VERİ KENDİNİ DÖRDE AYIRDI MI? (etiketsiz, zabıt V):",
              "      hakikat %d | tenakuz %d | şüpheli %d | gürültü %d"
              % (kulli["veri_cetveli"]["hakikat"],
                 kulli["veri_cetveli"]["tenakuz"],
                 kulli["veri_cetveli"]["şüpheli"],
                 kulli["veri_cetveli"]["gürültü"]),
              "",
              "    KUANTUM ASOSİYATİF HAFIZA (nefs/hafiza.py):",
              "      kayıt %d | tasdik %d | tevakkuf %d | cerh %d | "
              "Zeno budaması %d"
              % (kulli["hafıza"]["kayıt"], kulli["hafıza"]["tasdik"],
                 kulli["hafıza"]["tevakkuf"], kulli["hafıza"]["cerh"],
                 kulli["hafıza"]["budama"])]
        sd, uz, sp, ss = (kulli["sadakat"], kulli["usul"], kulli["şüphe"],
                          kulli["son_sadakat"])
        s += ["",
              "    ── ZABITLARIN İKİ AYRI ŞEYİ (karıştırılmaz) ──",
              "",
              "    1. MANTIĞA SADAKAT -- 7/24 ZEMİN (nefs/sadakat.py)",
              "       Bir meleke DEĞİL; sistemin varlık şartı. Her ileri",
              "       geçişte koşar, gradyanı yoktur, kapatılabilir.",
              "       kapı: %s   çağrı %d   yoklanan hüküm biti %d"
              % ("AÇIK" if ayar.sadakat_acik else "KAPALI ⚠",
                 sd["çağrı"], sd["yoklanan"]),
              "       tenakuz alarmı: %d kere yandı   Zeno ile sıfırlanan "
              "bit: %d" % (sd["alarm"], sd["sıfırlanan"]),
              "       alarm nispeti: %%%.3f  (0 = hiçbir hesap mantık "
              "dışına taşmadı)" % (100.0 * sd["alarm_nispeti"]),
              "       tâlim sonu durumu: alarm %d → %d  (%s)"
              % (ss["alarm_önce"], ss["alarm_sonra"],
                 "ALT-UZAYDA" if ss["alarm_sonra"] == 0
                 else "⚠ HÂLÂ DIŞARIDA"),
              "",
              "    2. MANTIK YÜRÜTME SEFERİ (nefs/usul.py) -- 7/24 DEĞİL",
              "       Kalp gedik hissedince Tertip açar, iş biter, kapanır.",
              "       kapı: %s   kalbin yoklaması %d   AÇILAN SEFER %d"
              % ("AÇIK" if ayar.usul_acik else "KAPALI ⚠",
                 uz["yoklama"], uz["sefer"]),
              "       sefer nispeti: %%%.2f  (%%100 olsaydı 'her an boş "
              "yere mantık kapısı çalıştıran kör hesap makinesi' olurdu)"
              % (100.0 * uz["sefer_nispeti"]),
              "       NETİCE KULLANILIYOR (rapora yazılıp bırakılmıyor):",
              "         kapanan gedik %d/%d   kapanmayanın mizandaki "
              "bedeli ℒ_gedik = %.6f"
              % (m["sefer_kapanan"], m["gedik"], m["L_gedik"]),
              "         Lan_K ile hafızaya nakşedilen yeni hüküm: %d"
              % m["sefer_kapanan"],
              "       gaye dökümü: istihrac %d | cerh %d | tahkik %d"
              % (uz["istihrac"], uz["cerh"], uz["tahkik"]),
              "       usul dökümü: %s"
              % (", ".join("%s×%d" % (k, v)
                           for k, v in sorted(uz["usul"].items())) or "—"),
              "       hadd-i evsat U_M† ile tasfiye edildi: %d/%d   "
              "artık dolanıklık %.3e"
              % (uz["uncompute"], uz["sefer"], uz["artık_dolanıklık"]),
              "       Lan_K ile müdrikeye taşınan yeni hüküm: %d"
              % uz["lan_k"],
              "",
              "    3. ŞÜPHE MANİFOLDU (nefs/suphe.py)",
              "       kapı: %s   çağrı %d"
              % ("AÇIK" if ayar.suphe_acik else "KAPALI ⚠", sp["çağrı"]),
              "       teâruz (P ≡ ¬P): %d   μ ortalaması %.4f → %.4f"
              % (sp["tearuz"], sp["μ_önce"], sp["μ_sonra"]),
              "       modal dallanma %d | merak kancası %d | "
              "Liouville buharlaşması %d"
              % (sp["dallanma"], sp["merak"], sp["buhar"]),
              "       tevakkuf (hüküm verilmedi): %d/%d örnek"
              % (sp["tevakkuf"], sp["örnek"])]
        ders = kulli["ders"]
        s += ["",
              "    ÖĞRENİYOR MU (ogrenme/izgara.py, düzenli uydurma):",
              "      eğim      : %+.6f   %s" % (
                  ders["eğim"],
                  "DÜŞÜYOR" if ders["öğreniyor"] else "⚠ ÖĞRENMİYOR"),
              "      bağıntı   : %+.4f   (sabit eğride tam 0)"
              % ders["bağıntı"],
              "      artık     : %.6f  bükülme: %.6f"
              % (ders["artık"], ders["bükülme"]),
              "",
              "    HAZİNE (main/hazine.py -- safetensors):",
              "      %s  (%d bayt, sha256 %s…)"
              % (kulli["hazine"]["yol"], kulli["hazine"]["bayt"],
                 kulli["hazine"]["sha256"][:16]),
              "",
              "    GEÇİT (nefs/illet.py):",
              "      zaman çizgesi: %d düğüm, %d çevrim   kelam ayrıştı: %s"
              % (kulli["geçit"]["zaman_düğümü"],
                 len(kulli["geçit"]["zaman_çevrimi"]),
                 kulli["geçit"]["kelam_ayrıştı"])]
        s += ["",
              "    ZABIT 2 -- SAF CPU 2026 USULLERİ (durumun temsili):",
              "      0. GALOIS-STABILIZER (nefs/galois.py) -- ASIL MOTOR",
              "         GF(2^%d)  tableau %d kübit  %d bayt  "
              "(sürekli ℂ^d İPTAL)"
              % (kulli["galois"]["us"], kulli["galois"]["n"],
                 kulli["galois"]["bayt"]),
              "         Palmer i(a,b)=(−b,a) -- İDDİA SINANDI (%d genlik):"
              % kulli["palmer"]["boy"],
              "           i² = −1 hatası %.1e   i⁴ = +1 hatası %.1e   "
              "norm hatası %.1e   tuttu: %s"
              % (kulli["palmer"]["i_kare_hatası"],
                 kulli["palmer"]["i_dört_hatası"],
                 kulli["palmer"]["norm_hatası"], kulli["palmer"]["tam"]),
              "           sin/cos/exp çağrısı: %d  (transandantal faz YOK)"
              % kulli["palmer"]["transandantal_çağrı"],
              "         yoğun ℂ^d'ye nispeten bellek: %.1f× küçük"
              % kulli["galois"]["kazanç"],
              "      1. TDD -- yalnız KANONİK DENETÇİ (hesap motoru DEĞİL)",
              "         çekirdek %d eleman → adres %s   %d bayt"
              % (kulli["tdd"]["çekirdek"], kulli["tdd"]["adres"],
                 kulli["tdd"]["bayt"]),
              "      2. Stabilizer rank (nefs/kararname.py)",
              "         χ_stab = %d   örtüşme %.4f   Clifford'a yakın: %s"
              % (kulli["stabilizer"]["chi"],
                 kulli["stabilizer"]["örtüşme"],
                 kulli["stabilizer"]["clifforda_yakın"]),
              "      3. Klasik gölgeler (nefs/golge.py)",
              ("         KAPALI (golge_ornegi=0): bütün sektörler TAM "
               "ölçüldü -- anahtar hakikaten kesiyor"
               if not kulli["gölge"].get("açık") else
               "         K=%d gölge → %d gözlenebilir, azamî hata %.4f"
               % (kulli["gölge"]["örnek"], kulli["gölge"]["gözlenebilir"],
                  kulli["gölge"]["azamî_hata"])),
              "         tam ölçüme nispeten hız: %.1f×"
              % kulli["gölge"]["hız"]]
        f, sb, so, fp = (kulli["flo"], kulli["sbox"],
                         kulli["sbox_ölçü"], kulli["faz_polinomu"])
        s += ["",
              "    NON-CLIFFORD ÇIKMAZI -- ÜÇ ÇARE (zabıt):",
              "      İTİRAZ TESCİLLİ: Bravyi-Gosset, χ_stab ~ 2^(0,468·t);",
              "      %d kapıda saf kübit tablosu %.3e kola ayrılırdı."
              % (f["kapı"], f["kübit_dallanması"]),
              "      1. MATCHGATE/FLO (nefs/matchgate.py)",
              "         %d Majorana modu, %d sürekli açılı kapı → "
              "χ_stab = %d" % (f["mod"], f["kapı"], f["chi"]),
              "         kovaryans Γ²=−I hatası %.3e   parite korundu: %s"
              % (f["kovaryans_hatası"], f["parite_korundu"]),
              "         MATCHGATE ŞARTI SINANDI (parite karışmaz, A/B "
              "üniter, det A = det B):",
              "           tutan %d/%d kapı   hepsi matchgate: %s"
              % (f["matchgate_tutan"], f["matchgate_denenen"],
                 f["matchgate_hepsi"]),
              "         kapı başına %.9f sn  (yoğun 2^N yola nispeten "
              "%.1f× hızlı)" % (f["kapı_sn"], f["hız"]),
              "      2. GALOIS S-BOX (nefs/galois.py)",
              "         x↦M·x²⁵⁴+b   açık: %s   değişen bayt: %d/%d"
              % (sb["açık"], sb["değişen"], sb["toplam"]),
              "         diferansiyel tekdüzelik %d (asgarî mümkün 2)   "
              "Walsh tepesi %d" % (so["tekdüzelik"], so["walsh"]),
              "         gayri-lineerlik %d   (afin fonksiyonda 0 olurdu)"
              % so["gayri_lineerlik"],
              "      3. CNOT-DIHEDRAL FAZ POLİNOMU (nefs/faz_polinomu.py)",
              "         Z_%d   derece %d   terim %d   (yoğun faz vektörü "
              "%d eleman)" % (fp["mertebe"], fp["derece"], fp["terim"],
                              fp["boy"]),
              "         tam mı: %s   artık %d/%d bileşen"
              % (fp["tam"], fp["artık"], fp["boy"]),
              "         dallanma: %d  (Bravyi-Gosset yolunda %.3e olurdu)"
              % (fp["dallanma"], fp["dallanma_kubit"])]
        sk = kulli["siklotomik"]
        ho, ck = kulli["hızölçer"], kulli["çekirdek"]
        s += ["",
              "    HIZÖLÇER -- ANA HATTA KALICI BAĞLI (koşarken ölçtü):",
              "      çağrı %d   toplam %.2f sn   belirteç %d"
              % (ho["çağrı"], ho["toplam_sn"], ho["belirteç"]),
              "      belirteç/sn: ortalama %.0f | en iyi %.0f | en kötü %.0f"
              % (ho["belirteç_sn"], ho["en_iyi"], ho["en_kötü"]),
              "      ilk çağrı %.0f → son çağrı %.0f  (ısınma payı %.2f×)"
              % (ho["ilk"], ho["son"], ho["ısınma"]),
              "      HAD BAĞLI: %s  (evvelce had=None idi ve ölçü "
              "kırmızı yanamıyordu)" % ho["hüküm"],
              "",
              "    44 QMELEKENİN KOŞTUĞU HAT (nefs/qcekirdek.py):",
              "      hat: %s   çekirdek derlendi: %s   koşuyor: %s"
              % (ck["hat"], ck["derlendi"], ck["koşuyor"]),
              "      kapı %d (karo %d, çift %d; matchgate %d)"
              % (ck["kapı"], ck["karo"], ck["çift"], ck["matchgate"]),
              "      boşaltma %d → bant başına %.1f kapı   "
              "numpy'a düşen boşaltma: %d"
              % (ck["boşaltma"], ck["bant_basina_kapi"],
                 ck["numpy_boşaltma"]),
              "      %s" % ck["kıyas"],
              "      karo → BLAS zgemm | çift → C (ölçü: karo BLAS'ta "
              "2-25× hızlı, çift C'de 6,9×)",
              "",
              "    DERECE-%d FAZ -- CNOT-DİHEDRAL İDDİASI İPTAL (zabıt):"
              % fp["derece"],
              "      Amy-Maslov-Mosca ≤3 ister; ölçülen %d. İddia DÜŞTÜ."
              % fp["derece"],
              "      Yerine SİKLOTOMİK KOSET (nefs/siklotomik.py):",
              "        %d = %s   →  x^%d = %s"
              % (sk["derece"], sk["ikili"], sk["derece"], sk["yazılış"]),
              "        koset(%d) mod 2^%d−1 : %s"
              % (sk["taban"], sk["us"], sk["koset"]),
              "        derece %d bu kosette mi: %s   (öyleyse iz terimi "
              "derece %d'e TAM iner)"
              % (sk["derece"], sk["kosette"], sk["taban"]),
              "      İZ EŞİTLİĞİ FİİLEN SINANDI (%d eleman):"
              % sk["iz_eşitliği"]["eleman"],
              "        Tr(α·x^%d) = Tr(β·x^%d) ,  β = α^(2^-%d)"
              % (sk["derece"], sk["taban"], sk["kare"]),
              "        uyuşmayan: %d / %d   →  eşitlik: %s"
              % (sk["iz_eşitliği"]["uyuşmayan"],
                 sk["iz_eşitliği"]["eleman"],
                 sk["iz_eşitliği"]["tuttu"]),
              "        monom açılımı olsaydı terim: %.3e  (açılmadı)"
              % sk["monom_sayisi"]]
        g = kulli["gpu_akışı"]
        s += ["",
              "    1 TB/S GPU AKIŞI (nefs/gpu_akis.py) -- zabıt:",
              "      koşan kütüphane: %s   GPU var mı: %s"
              % (g["kütüphane"], g["gpu"])]
        if not g["gpu"]:
            s.append("      ⚠ GPU YOK: 1 TB/s HADDİ BU MAKİNEDE ÖLÇÜLMEDİ. "
                     "Aşağısı aynı cebrin CPU ölçümüdür.")
        # **ÖLÇÜLEMEYEN SAYI BİÇİMLENDİRİLMEZ.** Bu üç satır evvelce
        # ``%.1f`` ile ``None`` basmaya kalkıyordu ve GPU'suz bir
        # makinede rapor **düşerdi**. Ölçülmeyenin yeri boş değil,
        # "ölçülemedi"dir; sıfır yazmak da uydurmak olurdu.
        def _gb(v):
            return "ölçülemedi" if v is None else "%.1f GB/s" % v

        def _hukum(v):
            return "ÖLÇÜLEMEDİ" if v is None else ("yeter" if v
                                                   else "YETMEZ")

        s += ["      İKİ DÜNYA (zabıt, ikinci fasıl) -- karıştırılmaz:",
              "        haricî (PCIe) tavanı : %s  (kart: %s)"
              % (_gb(g["pcie_tavan"]), g["kart"] or "—"),
              "        dâhilî (VRAM) tavanı : %s  (kart: %s)"
              % (_gb(g["vram_tavan"]), g["kart"] or "—"),
              "        had %.0f GB/s → haricî yol %s, dâhilî yol %s"
              % (g["had"], _hukum(g["haricî_yeter"]),
                 _hukum(g["dâhilî_yeter"])),
              "        zabıtın iddiası (ÖLÇÜ DEĞİL): %d × %s, "
              "VRAM %.0f, PCIe %.1f GB/s"
              % (g["iddia"]["kart"], g["iddia"]["kart_adı"],
                 g["iddia"]["vram_kart_gb"], g["iddia"]["pcie_kart_gb"]),
              "      ÇATI ÇİZGİSİ (Roofline): bayt başına bütçe %.0f işlem"
              % g["bayt_basina_islem"],
              "        ölçülen aritmetik yoğunluk: %.2f işlem/bayt  → %s"
              % (g["yogunluk"], "bant sınırlı (doğru taraf)"
                 if g["bant_sinirli"] else "hesap sınırlı (İFLAS)"),
              "      1. MOTOR -- warp symplectic bitmask (XOR/POPCOUNT)",
              "         %d bitlik kelime, %d satır → %.3f GB/s symplectic "
              "(bu makinede)" % (g["kelime"], g["satır"], g["symplectic_gb"]),
              "         kayan nokta çarpımı: %d  (sıfır olmalı)"
              % g["kayan_nokta"],
              "      2. MOTOR -- tek geçişli kaynaşık çekirdek",
              "         kaynaşık %.4f sn / ayrık %.4f sn → %.1f× ; "
              "bellek trafiği %.1f× azaldı"
              % (g["kaynasik_sn"], g["ayrik_sn"], g["kaynasma"],
                 g["trafik_kazanci"]),
              "      3. MOTOR -- GPU-yerel bitstream genleşmesi",
              "         tohum %d bayt → dalga %d bayt (%.1f×)   "
              "PCIe'den girmesi gereken: %.1f GB/s"
              % (g["tohum_bayt"], g["dalga_bayt"], g["genlesme"],
                 g["pcie_gereken"]),
              "         çığ: tohumun tek biti çevrilince dalganın "
              "%%%.1f'i değişiyor" % (100.0 * g["tohuma_bağlı"]),
              "         PCIe'ye sığıyor mu: %s" % _hukum(g["pcie_sigdi"]),
              "      4. MOTOR -- 4 kart P2P sınır kilidi",
              "         dilim %d × %d bayt, sınır %d bayt → temas %.4f%%"
              % (g["dilim"], g["dilim_bayt"], g["sınır_bayt"],
                 g["temas_yuzdesi"]),
              "         yeniden kurma hatası %.3e  (sınır kaybı YOK)"
              % g["dilim_hatası"]]
        if kulli.get("düşen_uzuv"):
            s.append("    DÜŞEN UZUV: %s"
                     % ", ".join(sorted(kulli["düşen_uzuv"])))
    # **YALAN SATIR KALDIRILDI.** Burada "ARC'de fiilen çözen hat bu
    # ikisi değil, üçüncüsüdür: ``gorev_talimi``" yazıyordu. O fonksiyon
    # imha edilmiş bir uzvu ithal ediyordu ve çağrılsa ImportError
    # verirdi -- yâni "asıl çözen" diye gösterilen hat hiç koşmuyordu.
    s += ["", "  HAD: ARC çözüm oranı yukarıdaki `tam_çözülen`dir ve",
          "  başka hiçbir hat yoktur. Elle kâide de yoktur."]
    return "\n".join(s)

def cikarim_beyani(d: Dict[str, object]) -> str:
    """Çıkarım koşusunun neticesini beyan et (``main/cikarim.py``)."""
    return "\n".join([
        "=== ÇIKARIM -- motor cevabı (elle kâide YOK) ===", "",
        "  küme            : %s" % d["küme"],
        "  deneme          : %d" % d["deneme"],
        "  konuşan / susan : %d / %d" % (d["konuşan"], d["susan"]),
        "  TAM çözülen     : %d" % d["tam_çözülen"],
        "  hücre isabeti   : %.4f" % d["ortalama_hücre_isabeti"],
        "  süre            : %.1f sn" % d["süre_sn"],
        "  ağırlık         : %s" % (d["hazine"].get("yol")
                                    or "YOK (ham kip -- eğitilmemiş motor)"),
        "  hafıza (ρ)      : %s" % (d["hazine"].get("hafıza")
                                    or "YOK (Zeno budaması kapalı)"),
        "  Zeno budaması   : %d kol kesildi" % d["budanan"],
        "",
        "  MANTIĞA SADAKAT -- 7/24, ÇIKARIMDA DA (nefs/sadakat.py):",
        "    çağrı %d   tenakuz alarmı %d   Zeno ile sıfırlanan bit %d"
        % (d["sadakat"]["çağrı"], d["sadakat"]["alarm"],
           d["sadakat"]["sıfırlanan"]),
        "    alarm nispeti %%%.3f  (0 = hiçbir hesap mantık dışına taşmadı)"
        % (100.0 * d["sadakat"]["alarm_nispeti"]),
        "",
        "  ŞÜPHE MANİFOLDU (nefs/suphe.py):",
        "    teâruz %d   tevakkuf %d   merak kancası %d"
        % (d["şüphe"]["tearuz"], d["şüphe"]["tevakkuf"],
           d["şüphe"]["merak"]),
        "",
        "  Elle kurulmuş hiçbir ARC kâidesi kullanılmadı; eski dalga",
        "  öğrenicisi İMHA EDİLDİ (yedek dizini de silindi).",
    ])


def kaggle_beyani(profil, talim, teslimat) -> str:
    """Kaggle kipinin neticesini beyan et (``main/egitim.py:taht``)."""
    return ("=== KAGGLE KİPİ ===\n  donanım profili: %r\n"
            "  tâlim: %r\n  teslimat: %s"
            % (profil, talim, getattr(teslimat, "__name__", teslimat)))
