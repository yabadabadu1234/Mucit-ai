from __future__ import annotations

from typing import Dict, Optional

__all__ = ["talim_beyani", "cikarim_beyani", "kaggle_beyani",
           "sifir_beyani", "devam_metni"]


def _bayt(n) -> str:
    n = float(n or 0)
    for birim in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024.0 or birim == "TB":
            return "%.1f %s" % (n, birim)
        n /= 1024.0
    return "%.1f TB" % n


def devam_metni(devam: Dict[str, object],
                imlec: Dict[str, object]) -> str:
    s = ["  TÂLİM HÂLİ -- TEK DOSYA, DEVAM ESAS (ferman 1-Y)"]
    if devam.get("yüklendi"):
        s += ["    hazine    : DEVAM EDİLDİ  (%s, %s)"
              % (devam.get("yol"), _bayt(devam.get("bayt"))),
              "    tur       : %d. tur  (kaldığı kayıp %s)"
              % (int(devam.get("tur", 0) or 0) + 1,
                 ("%.4f" % float(devam["kaldığı_kayıp"]))
                 if devam.get("kaldığı_kayıp") is not None else "—")]
    else:
        s += ["    hazine    : YOK -- rastgele p₀ ile İLK TUR",
              "    sebep     : %s" % (devam.get("sebep") or "—")]
    if imlec:
        s += ["    İMLEÇ -- külliyatın hangi baytında kalındı:"]
        for ad in sorted(imlec):
            v = imlec[ad] or {}
            s += ["      %-46s %s / %s  (%%%.2f, %d. devir)"
                  % (ad[:46], _bayt(v.get("bayt")),
                     _bayt(v.get("boy_bayt")),
                     100.0 * float(v.get("nispet", 0.0)),
                     int(v.get("devir", 0) or 0))]
    else:
        s += ["    İMLEÇ     : yok -- külliyat okunmadı"]
    return "\n".join(s + [""])


def sifir_beyani(o: Dict[str, object]) -> str:
    if o.get("vardı"):
        return ("\n=== TÂLİM HAZİNESİ SIFIRLANDI ===\n\n"
                "  silinen : %s  (%s)\n"
                "  Sonraki tâlim rastgele p₀ ile ve imleç sıfırdan "
                "başlar.\n" % (o.get("yol"), _bayt(o.get("bayt"))))
    return ("\n=== SIFIRLANACAK BİR ŞEY YOK ===\n\n"
            "  aranan : %s\n  Hazine zaten yok; sonraki tâlim ilk "
            "turdur.\n" % (o.get("yol"),))


def talim_beyani(ayar, kulli: Optional[Dict[str, object]]) -> str:
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
        s += [devam_metni(kulli.get("devam") or {},
                          kulli.get("imleç") or {}),
              "  KÜLLÎ KAYIP TÂLİMİ -- TEK HAT",
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
        from nefs.mukayese import mukayese_metni
        from nefs.galois import faz_borcu_metni
        from ogrenme.mecz import mecz_metni
        from nefs.belirtec import belirtec_metni
        from nefs.munasebet import munasebet_metni
        from nefs.keyfiyet import keyfiyet_metni
        from tanilama.hizolcer import hiz_metni
        from main.kulliyat import kulliyat_beyani
        from nefs.parametre_yazmaci import parametre_metni, kenet_metni
        from nefs.nqs import nqs_metni
        from nefs.mahalli_yazmac import mahalli_metni, uzunluk_metni
        from nefs.veri_kapisi import kapi_metni
        from nefs.mukayese import mukayese_melekesi_metni
        from nefs.hafiza import tertip_metni
        from nefs.mukayese import omur_metni, vecih_metni
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
              (kulli.get("mihenk") or {}).get("metin", ""), "",
              faz_borcu_metni(kulli.get("faz_borcu") or {}), "",
              mecz_metni(kulli.get("eniyileme") or {}), "",
              belirtec_metni(kulli.get("belirteç") or {}), "",
              mukayese_metni(kulli.get("mukayese") or {}), "",
              munasebet_metni(kulli["münasebet"]), "",
              str(kulli.get("lif") or ""), "",
              hiz_metni(), "",
              keyfiyet_metni(kulli["keyfiyet"]), "",
              parametre_metni(kulli.get("parametre_yazmacı") or {}), "",
              kenet_metni(kulli.get("kenetlenme") or {}), "",
              mahalli_metni(kulli.get("mahallî_yazmaç") or {}), "",
              uzunluk_metni(kulli.get("uzunluk_katmanı") or {}), "",
              kapi_metni(kulli.get("veri_kapısı") or {}), "",
              mukayese_melekesi_metni(
                  kulli.get("mukayese_melekesi") or {}), "",
              tertip_metni(kulli.get("hafıza_tertibi") or {}), "",
              vecih_metni(kulli.get("vecih") or {}), "",
              omur_metni(kulli.get("vecih_ömrü") or {}), "",
              nqs_metni(kulli.get("kan_nqs") or {}), "",
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
              "      0. ℒ_Nokta   (kısmî Born = −ln P) : %.6f   × %.2f"
              % (m["nokta"], ayar.lam_nokta),
              "         İKİ CİNS, TEK FORMÜL (ferman 1-R): %s"
              % ("  ".join("%s %s" % (k, ("%.4f" % v)
                                      if isinstance(v, float) else v)
                           for k, v in sorted(
                               (m.get("nokta_cins") or {}).items()))
                 or "cins yok -- veri katmanı üçlü vermiyor"),
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
              "      ℒ_Lif (münasebet sadakati) : %.6f   × %.2f"
              % (m["lif"], ayar.lam_lif),
              "        1−ρ_Spearman( ‖bağlam_i−bağlam_j‖ , "
              "−ln|⟨hal_i|hal_j⟩| ) -- %s"
              % ("%d örnek, %d çift"
                 % (int((m.get("lif_dökümü") or {}).get("örnek", 0)),
                    int((m.get("lif_dökümü") or {}).get("çift", 0)))
                 if not (m.get("lif_dökümü") or {}).get("sebep")
                 else str((m["lif_dökümü"])["sebep"])),
              "        durum örnekleri ayırmazsa KIRMIZI yanar "
              "(kefe 1,0'a oturur).",
              "      ─── ferman 1-S: imha edilen iki hata "
              "fonksiyonunun cevheri ───",
              "      ℒ_Meleke kanadı (MECLİS YOK -- ferman 1-U): %.6f"
              % m["meleke"],
              "        %d meleke AYRI AYRI kefe; en kötü: %s (%.4f)"
              % (m["meleke_sayısı"], m["meleke_en_zayıf"],
                 m["meleke_en_kötü_hata"]),
              "        kesme (YAPISAL, kayba GİRMEZ): kapı başına "
              "tutulan kesir %.6f" % m["kesme_yapısal"],
              "      ℒ_Zırh kanadı (beşi AYRI kefe): %.6f   × %.2f"
              % (m["zırh"], ayar.lam_zirh),
              "        sheaf %.4f | Betti %.4f | koho %.4f | "
              "homotopi %.4f | nizam %.4f"
              % (m["zırh_sheaf"], m["zırh_betti"], m["zırh_koho"],
                 m["zırh_homotopi"], m["zırh_nizam"]),
              "        nizam İKİ fonksiyonda da vardı, BİR KEZ sayıldı "
              "(zırhın beşinci ihlâli).",
              "        eski τ-softmax terkibi olsaydı: %.6f  "
              "(KIYAS; kayba GİRMEZ -- ferman 1-U)" % m["zırh_softmax"],
              "        meleke ölçümü: %s"
              % ("AÇIK" if ayar.meleke_olcumu
                 else "KAPALI ⚠ -- iki kanat da sıfır"),
              "      ─────────────────────────────────",
              "    HATA VEKTÖRÜ (ferman 1-V -- türev almıyoruz):",
              "      bileşen sayısı        : %d   (skaler DEĞİL)"
              % m["bileşen"],
              "      en büyük beş artık    : %s"
              % "  ".join(
                  "%s %.4f" % (m["artık_adı"][i], m["artık"][i])
                  for i in sorted(range(len(m["artık"])),
                                  key=lambda k: -m["artık"][k])[:5]),
              "      toplama YALNIZ burada: eniyileyici sıralama ister.",
              "      ℒ_Küllî = Σ artık     : %.6f" % m["kayıp"],
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
              "       GELEN taşma  : %%%.3f  (zemin kaç kere müdahale "
              "etmek zorunda kaldı)" % (100.0 * sd["alarm_nispeti"]),
              "       KALAN taşma  : %%%.3f  ← MANTIKSIZLIK HUDUDU "
              "BUDUR (0 = hiçbir hesap mantık dışına taşmış KALMADI)"
              % (100.0 * sd["artık_nispeti"]),
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
    s += ["", "  HAD: ARC çözüm oranı yukarıdaki `tam_çözülen`dir ve",
          "  başka hiçbir hat yoktur. Elle kâide de yoktur."]
    return "\n".join(s)

def cikarim_beyani(d: Dict[str, object]) -> str:
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
    d = (talim or {}).get("değerlendirme") or {}
    t = teslimat or {}
    return "\n".join([
        "=== KAGGLE KİPİ -- TAHTIN KENDİ KİPİ (ayrı hat YOK) ===", "",
        "  donanım profili : %s   (ölçüldü, elle seçilmedi -- ferman 5-B)"
        % getattr(profil, "ad", profil),
        "  tâlim parametre : %s   V_ilk → V_son: %.4f → %.4f"
        % ((talim or {}).get("parametre", "?"),
           float((talim or {}).get("V_ilk", 0.0)),
           float((talim or {}).get("V_son", 0.0))),
        "  tâlim ölçütü    : tam çözülen %s/%s   hücre isabeti %.4f"
        % (d.get("tam_çözülen", "?"), d.get("deneme", "?"),
           float(d.get("ortalama_hücre_isabeti", 0.0))),
        "",
        "  TESLİMAT (cevabı ``padisah`` üretti, GİRDİ değil)",
        "    görev        : %s" % t.get("görev", "?"),
        "    konuşan      : %s        susan: %s"
        % (t.get("konuşan", "?"), t.get("susan", "?")),
        "    çözülemeyen  : %s   (ızgara ayrıştırılamadı = YANLIŞ CEVAP, "
        "ferman 1-P)" % t.get("çözülemeyen", "?"),
        "    yazılan dosya: %s  (%s bayt)"
        % (t.get("yol", "?"), t.get("bayt", "?"))])
