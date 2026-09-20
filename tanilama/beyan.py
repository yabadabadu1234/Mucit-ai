from __future__ import annotations

from typing import Dict, Optional

__all__ = ["talim_beyani", "cikarim_beyani", "kaggle_beyani",
           "sifir_beyani", "devam_metni", "netice_derle", "faz_borcu_metni"]


def faz_borcu_metni(b: Dict[str, object]) -> str:
    if not b:
        return ("  FAZ DEFTERİ: ölçü YOK -- yazmaç yoklanmadı, "
                "kırmızı yanıyor (ferman 5)")
    return "\n".join([
        "  FAZ SÜREKLİ TEMSİLDE (exp/sin/cos, ayrıklaştırma YOK)",
        "    yazmaca indirilen faz çağrısı  : %d"
        % int(b.get("indirme", 0)),
        "    biriken faz büyüklüğü ortalama : %.6f rad"
        % float(b.get("toplam_faz_ortalama", 0.0)),
        "    biriken faz büyüklüğü azamî    : %.6f rad"
        % float(b.get("toplam_faz_azamî", 0.0)),
        "    borç/kalıntı kavramı YOK: her faz çağrısı doğrudan "
        "exp(-iθ) ile tam uygulanır."])


def netice_derle(Z: Dict[str, object]) -> Dict[str, object]:
    import time
    from kuantum.devre import devre_beyani
    from main.kulliyat import kulliyat_dokumu
    from nefs.belirtec import belirtec_beyani
    from nefs.casimir import casimir_beyani
    from nefs.hafiza import tertip_beyani
    from matematik.sonsuz_mertebeler_teorisi import hendese_beyani, lif_beyani
    from nefs.keyfiyet import keyfiyet_beyani
    from nefs.kulli_mizan import fock_beyani, hamiltonyen_beyani
    from kuantum.mahalli_yazmac import mahalli_beyani, uzunluk_beyani
    from nefs.mihenk import safha_beyani
    from nefs.mukayese import (cozum_beyani, mukayese_melekesi_beyani,
                               omur_beyani, vecih_beyani)
    from nefs.munasebet import munasebet_beyani
    from kuantum.nqs import nqs_beyani
    from kuantum.parametre_yazmaci import kenet_beyani, parametre_beyani
    from kuantum.qcekirdek import cekirdek_beyani
    from kuantum.qyazmac import sektor_beyani, senet_beyani
    from nefs.sadakat import sadakat_devre_beyani
    from nefs.veri_kapisi import kapi_beyani
    from ogrenme.mecz import mecz_beyani
    from tanilama.hizolcer import hizolcer_beyani

    ayar = Z["ayar"]
    hendese = Z["hendese"]
    nefs = Z["nefs"]
    kefeler = Z["kefeler"]
    r = Z["r"]
    return {"ayar": ayar.ad, "parametre": Z["d"],
            "devam": Z["devam"], "imleç": Z["imlec"],
            "geçit": Z["kapi"], "ders": Z["ders"], "hazine": Z["kayit"],
            "lif": lif_beyani(Z["harita"]),
            "hendese": hendese, "hendese_beyanı": hendese_beyani(),
            "safha": safha_beyani(),
            "dhr": Z["dhr"], "casimir_beyanı": casimir_beyani(),
            "parite_lifi": int(ayar.parite_lifi),
            "mertebe_tayfı": {
                ad: float(p) for ad, p in
                zip(hendese["katman"], hendese["tayf"])},
            "lif_demeti": [float(x) for x in hendese["asansör"]["demet"]],
            "büzülme": float(hendese["asansör"]["büzülme"]),
            "hodge": hendese["hodge"], "Ω_cebiri": hendese["Ω_cebiri"],
            "tdd": Z["tdd"], "stabilizer": Z["stab"], "gölge": Z["golge"],
            "flo": Z["flo"],
            "sadakat": Z["sad"], "son_sadakat": Z["son_sadakat"],
            "sadakat_devresi": sadakat_devre_beyani(),
            "mukayese": Z["mukayese"],
            "mukayese_melekesi": mukayese_melekesi_beyani(),
            "vecih": vecih_beyani(),
            "vecih_ömrü": omur_beyani(),
            "devre": devre_beyani(),
            "hamiltonyen": hamiltonyen_beyani(),
            "çözüm_uzayı": cozum_beyani(),
            "fock": fock_beyani(),
            "sektör": sektor_beyani(), "senet": senet_beyani(),
            "hafıza_tertibi": tertip_beyani(),
            "küme_kapanışı": Z["kume_kapanisi"],
            "mihenk": Z["nobet"].beyan(Z["p_yildiz"]),
            "eniyileme": mecz_beyani(),
            "faz_borcu": Z["q_son"].y.faz_borcu(),
            "konuşma": Z["konusma"], "münasebet": munasebet_beyani(),
            "keyfiyet": keyfiyet_beyani(),
            "külliyat": {"arc": len(Z["arc_veri"]),
                         "külliyat": len(Z["kul_veri"]),
                         "döküm": kulliyat_dokumu()},
            "belirteç": belirtec_beyani(str(ayar.kodlama)),
            "ölçek": ayar.olcek_dokumu, "elle_verilen": ayar.elle,
            "denge": Z["olculen_lam"], "ilk_kefeler": Z["ilk_kefeler"],
            "usul": Z["usl"], "şüphe": Z["sup"],
            "hızölçer": hizolcer_beyani(),
            "çekirdek": cekirdek_beyani(),
            "parametre_yazmacı": parametre_beyani(
                getattr(nefs, "pq", None)),
            "kenetlenme": kenet_beyani(),
            "mahallî_yazmaç": mahalli_beyani(),
            "uzunluk_katmanı": uzunluk_beyani(),
            "veri_kapısı": kapi_beyani(),
            "kan_nqs": nqs_beyani(getattr(nefs, "kan", None)),
            "tur_genliği": Z["_tur"],
            "mizan": kefeler, "veri_cetveli": Z["cetvel"],
            "hafıza": Z["hafiza"].beyan(),
            "rüşt": float(kefeler["α_rüşt"]),
            "veri": len(Z["veri"]),
            "V_ilk": float(r["V_ilk"]), "V_son": float(r["V_son"]),
            "süre_sn": time.perf_counter() - Z["t0"],
            "kayıp_çağrısı": int(r.get("kayıp_çağrısı", 0)),
            "seyir": r.get("seyir", []),
            "değerlendirme": Z["deg"],
            "tâlim_günlüğü": r.get("günlük", []),
            "düşen_uzuv": r.get("düşen_uzuv", {}),
            "kademe_görevi": len(Z["kademe_gorevleri"]),
            "kademe_parametresi": Z["kademe_parametresi"],
            "p": Z["p_yildiz"]}


def _bayt(n) -> str:
    n = float(n or 0)
    for birim in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024.0 or birim == "TB":
            return "%.1f %s" % (n, birim)
        n /= 1024.0
    return "%.1f TB" % n


def _cikarim_devresi(d: Dict[str, object]) -> str:
    from nefs.sadakat import sadakat_devre_metni
    return sadakat_devre_metni(d.get("sadakat_devresi"))


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
    if kulli and kulli.get("hendese"):
        from matematik.sonsuz_mertebeler_teorisi import hendese_metni
        s += [hendese_metni(kulli.get("hendese"),
                            kulli.get("hendese_beyanı")), ""]
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
        from ogrenme.mecz import mecz_metni
        from nefs.belirtec import belirtec_metni
        from nefs.munasebet import munasebet_metni
        from nefs.keyfiyet import keyfiyet_metni
        from tanilama.hizolcer import hiz_metni
        from main.kulliyat import kulliyat_beyani
        from kuantum.parametre_yazmaci import parametre_metni, kenet_metni
        from kuantum.nqs import nqs_metni, tur_metni
        from kuantum.mahalli_yazmac import mahalli_metni, uzunluk_metni
        from nefs.veri_kapisi import kapi_metni
        from nefs.mukayese import mukayese_melekesi_metni
        from nefs.hafiza import tertip_metni
        from nefs.mukayese import omur_metni, vecih_metni
        from kuantum.devre import devre_metni
        from nefs.mukayese import cozum_metni
        from nefs.kulli_mizan import fock_metni, hamiltonyen_metni
        from kuantum.qyazmac import sektor_metni
        from nefs.sadakat import sadakat_devre_metni
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
              devre_metni(kulli.get("devre") or {}), "",
              cozum_metni(kulli.get("çözüm_uzayı") or {}), "",
              hamiltonyen_metni(kulli.get("hamiltonyen") or {}), "",
              fock_metni(kulli.get("fock") or {}), "",
              sektor_metni(kulli.get("sektör") or {}), "",
              nqs_metni(kulli.get("kan_nqs") or {}), "",
              tur_metni(kulli.get("tur_genliği")), "",
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
              sadakat_devre_metni(kulli.get("sadakat_devresi")),
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
              "      0. TDD -- yalnız KANONİK DENETÇİ (hesap motoru DEĞİL)",
              "         çekirdek %d eleman → adres %s   %d bayt"
              % (kulli["tdd"]["çekirdek"], kulli["tdd"]["adres"],
                 kulli["tdd"]["bayt"]),
              "      1. Stabilizer rank (nefs/kararname.py)",
              "         χ_stab = %d   örtüşme %.4f   Clifford'a yakın: %s"
              % (kulli["stabilizer"]["chi"],
                 kulli["stabilizer"]["örtüşme"],
                 kulli["stabilizer"]["clifforda_yakın"]),
              "      2. Klasik gölgeler (nefs/golge.py)",
              ("         KAPALI (golge_ornegi=0): bütün sektörler TAM "
               "ölçüldü -- anahtar hakikaten kesiyor"
               if not kulli["gölge"].get("açık") else
               "         K=%d gölge → %d gözlenebilir, azamî hata %.4f"
               % (kulli["gölge"]["örnek"], kulli["gölge"]["gözlenebilir"],
                  kulli["gölge"]["azamî_hata"])),
              "         tam ölçüme nispeten hız: %.1f×"
              % kulli["gölge"]["hız"]]
        f = kulli["flo"]
        s += ["",
              "    NON-CLIFFORD ÇIKMAZI -- MATCHGATE/FLO (zabıt):",
              "      İTİRAZ TESCİLLİ: Bravyi-Gosset, χ_stab ~ 2^(0,468·t);",
              "      %d kapıda saf kübit tablosu %.3e kola ayrılırdı."
              % (f["kapı"], f["kübit_dallanması"]),
              "      MATCHGATE/FLO (nefs/matchgate.py)",
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
              "%.1f× hızlı)" % (f["kapı_sn"], f["hız"])]
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
              "2-25× hızlı, çift C'de 6,9×)"]
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
        _cikarim_devresi(d),
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
