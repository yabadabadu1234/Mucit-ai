import sys
import time
from typing import Any, Dict, List, Optional

import torch

from model_yapilandirmalari import (
    DECODING_ONERILERI,
    LORA_HEDEF_MODULLERI,
    RWKV,
    asistan_donusu_sar,
    kullanici_donusu_sar,
    yerel_model_yolu,
)


def _guven_kodu_gerekli_mi(hata: Exception) -> bool:
    metin = str(hata).lower()
    return "trust_remote_code" in metin or "does not recognize this architecture" in metin


def _repo_id_dogrulama_hatasi_mi(hata: Exception) -> bool:
    return "repo id must be in the form" in str(hata).lower()


def _hub_tarzi_hata_mi(hata: Exception) -> bool:
    return _guven_kodu_gerekli_mi(hata) or _repo_id_dogrulama_hatasi_mi(hata)


def _cache_parametre_uyumsuzlugunu_duzelt(model: Any) -> Any:
    """HATA (kullanıcının Kaggle'da checkpoint'in KENDİ kaynağından
    grep'lediği KESİN kanıt -- "NemotronH requires an initialized
    NemotronHHybridDynamicCache ... None was provided" uyarısının GERÇEK
    kök nedeni): checkpoint'in modeling_nemotron_h.py'si (kendi yorumunda
    da itiraf ettiği gibi) `prepare_inputs_for_generation`'ı Jamba'nın
    kodundan KOPYALAMIŞ ama YENİDEN ADLANDIRMAYI UNUTMUŞ -- dönen sözlüğe
    `"past_key_values": <hazır cache nesnesi>` koyuyor, ama `forward()`
    parametreyi `cache_params` adıyla bekliyor. `forward`'ın `**kwargs`'ı
    bu yanlış adlı değeri sessizce yutup ATIYOR, `cache_params` HİÇ
    ulaşmıyor, cache asla kullanılmıyor (~20 kat yavaşlama). Native
    transformers>=5.3.0 nemotron_h'yi bu checkpoint'in mimarisini
    (düz "mlp" katmanları) desteklemediği için KULLANAMIYORUZ (bkz. 0.
    kademedeki not) -- yani checkpoint'in KENDİ (bug'lı) kodunda
    kalmak ZORUNDAYIZ. Çözüm: kaynağa dokunmadan, model NESNESİNİN
    `prepare_inputs_for_generation`'ını burada saracak şekilde
    monkeypatch'liyoruz -- dönen sözlükte "past_key_values" varken
    "cache_params" YOKSA, anahtarı DOĞRU isme taşıyoruz. `forward`
    imzasında GERÇEKTEN `cache_params` parametresi olup `past_key_values`
    OLMAYAN modellerde (bu spesifik kopyala-yapıştır hatasının izi)
    devreye girer; standart modellerde (forward zaten `past_key_values`
    bekliyorsa) HİÇBİR ŞEY DEĞİŞTİRMEZ."""
    try:
        import inspect

        forward_imzasi = inspect.signature(model.forward)
        parametreler = forward_imzasi.parameters
        if "cache_params" in parametreler and "past_key_values" not in parametreler:
            _orijinal_pig = model.prepare_inputs_for_generation

            def _yamali_prepare_inputs_for_generation(*args: Any, **kwargs: Any) -> Dict[str, Any]:
                girdi = _orijinal_pig(*args, **kwargs)
                if isinstance(girdi, dict) and "past_key_values" in girdi and "cache_params" not in girdi:
                    girdi["cache_params"] = girdi.pop("past_key_values")
                return girdi

            model.prepare_inputs_for_generation = _yamali_prepare_inputs_for_generation
            print(
                "[ttt_lora] cache parametre adı uyumsuzluğu (past_key_values vs cache_params) tespit "
                "edildi ve monkeypatch ile düzeltildi -- cache artık GERÇEKTEN kullanılacak (~20 kat "
                "hız kazancı beklenir)."
            )
    except Exception as _yama_hatasi:
        print(f"[ttt_lora] cache parametre uyumsuzluğu düzeltmesi denendi ama başarısız oldu (yoksayılıp devam edilecek): {_yama_hatasi}")
    return model


def temel_model_yukle(model_ailesi: str, veri_tipi: torch.dtype = torch.bfloat16) -> Any:
    """Model DAIMA yerel dosya yolundan yuklenir; internet erisimi kapali
    oldugundan `local_files_only=True` her zaman zorunludur. Ayrica
    model_yapilandirmalari.py, bu modul import edilmeden ONCE
    HF_HUB_OFFLINE / TRANSFORMERS_OFFLINE ortam degiskenlerini ayarlar --
    huggingface_hub/transformers'in HER TURLU hub-tarzi cozumlemesi
    (agdan dosya var mi sormasi dahil) boylece tamamen kapatilir.

    Dort kademeli yukleme (her biri bir onceki basarisiz olursa devreye
    girer):
      1) AutoModelForCausalLM.from_pretrained(trust_remote_code=False)
      2) ozel_kod_kaydi.ozel_kodu_manuel_kaydet: config.json'daki
         auto_map'i okuyup Config/Model siniflarini DOGRUDAN .py
         dosyasindan importlib ile yukleyip Auto*'ya kaydeder, sonra
         YINE trust_remote_code=False ile from_pretrained dener.
      3) ozel_kod_kaydi.dogrudan_yukle: from_pretrained'e HIC
         dokunmadan -- config.json ve safetensors/bin agirlik
         dosyalarini DOGRUDAN diskten okuyup modeli elle kurar. Bu,
         huggingface_hub'in repo_id dogrulamasi dahil hicbir kod
         yoluna girmeyen, en dip seviye yerel yukleme yoludur.
      4) yalnizca ucu de basarisiz olursa, son care trust_remote_code=True.

    Yol HAM bir .pth kontrol noktasiysa (transformers config.json
    tasimiyorsa -- model_indir.py'nin BlinkDL/rwkv7-g1'den indirdigi
    dosya tam olarak boyle), yukaridaki dort kademe hic denenmez;
    dogrudan `rwkv` pip paketiyle native yuklenir (bkz. rwkv_native.py)."""
    yol = yerel_model_yolu(model_ailesi)

    if model_ailesi == RWKV:
        from rwkv_native import native_rwkv_yukle, rwkv_ham_pth_mi
        if rwkv_ham_pth_mi(yol):
            return native_rwkv_yukle(yol, veri_tipi=veri_tipi)

    from transformers import AutoConfig, AutoModelForCausalLM

    # HATA (kullanıcının açık talebi -- "NemotronH requires an initialized
    # NemotronHHybridDynamicCache ... hiçbir log yok, takılı mı kaldı"):
    # bu bir donma DEĞİL -- transformers'ın BİLİNEN bir hatası (GitHub
    # issue #34739): modeling_nemotron_h.py'de prepare_inputs_for_
    # generation() ile forward() arasında bir parametre adı UYUŞMAZLIĞI
    # (past_key_values vs cache_params) var, cache HİÇ kullanılamıyor,
    # model HER yeni token için TÜM diziyi baştan yeniden hesaplıyor
    # (~20 kat yavaşlama). Bu, transformers>=5.3.0'da KÜTÜPHANENİN
    # KENDİSİNDE düzeltildi -- AMA trust_remote_code=True kullanılırsa,
    # kütüphanenin düzeltilmiş native kodu yerine modelin REPOSUNDAKİ
    # ESKİ/bug'lı modeling_nemotron_h.py cache'e indirilip KULLANILIYOR,
    # düzeltmeyi tamamen eziyor. Bizim 2/3/4. kademelerimiz (trust_remote_
    # code=True / manuel .py kaydı) tam olarak bu tuzağa düşüyordu.
    #
    # Kökten çözüm -- "0. kademe": config.json'un model_type'ı transformers'ın
    # KENDİ CONFIG_MAPPING'inde (native, kütüphaneye GÖMÜLÜ) zaten
    # kayıtlıysa, auto_map'i (dolayısıyla trust_remote_code gereksinimini)
    # TAMAMEN YOK SAYIP doğrudan o native sınıfı kullanıyoruz -- bu, ilgili
    # GitHub issue'sunun önerdiği "bayrağı kaldır, kütüphanenin native
    # implementasyonuna bırak" çözümünün BİREBİR karşılığı. model_type
    # native olarak TANINMIYORSA (transformers eski/model henüz
    # birleştirilmemiş) bu kademe sessizce atlanır, eski 1-4 kademe zinciri
    # DEĞİŞMEDEN devam eder.
    try:
        import json as _json
        import os as _os

        from ozel_kod_kaydi import agir_kernel_bayraklarini_yumusat
        from transformers.models.auto.configuration_auto import CONFIG_MAPPING

        with open(_os.path.join(yol, "config.json"), "r", encoding="utf-8") as _f:
            _ham_config = _json.load(_f)
        _model_turu = _ham_config.get("model_type")

        # HATA (kullanıcının açık talebi -- "NemotronHHybridDynamicCache ...
        # None was provided" uyarısı 0. kademe DEVREDEYKEN bile devam
        # ediyordu, ama bu metin transformers'ın v5.3.0 KAYNAĞINDA hiç
        # yok): bu, native koda değil, HÂLÂ checkpoint'in ESKİ/bug'lı
        # modeling_nemotron_h.py'sine dokunulduğunu gösteriyor -- muhtemel
        # sebep, AYNI Python sürecinde (kernel yeniden başlatılmadan) daha
        # önce yapılmış bir trust_remote_code=True/manuel kayıt denemesinin
        # bıraktığı KÜRESEL sys.modules/Auto* kayıt kalıntısı. Kökten
        # çözüm olarak, 0. kademe native sınıfı zorlamadan HEMEN ÖNCE bu
        # model_type'a ait olası eski dinamik-modül kalıntılarını sys.
        # modules'tan proaktif olarak temizliyoruz -- kernel yeniden
        # başlatılmasa bile bu süreçte YENİ bir 0. kademe denemesi eski
        # kalıntıyla çakışmasın diye.
        for _kalinti_adi in list(sys.modules):
            if "transformers_modules" in _kalinti_adi and _model_turu and _model_turu.replace("_", "") in _kalinti_adi.lower().replace("_", ""):
                del sys.modules[_kalinti_adi]
                print(f"[ttt_lora] 0. kademe: ESKİ dinamik-modül kalıntısı sys.modules'tan temizlendi: {_kalinti_adi}")

        if _model_turu in CONFIG_MAPPING:
            print(
                f"[ttt_lora] 0. kademe: model_type='{_model_turu}' transformers'ın KENDİ (native, "
                f"kütüphaneye gömülü) sınıfında kayıtlı -- auto_map/trust_remote_code TAMAMEN atlanıp "
                f"doğrudan native sınıf kullanılacak (bilinen cache/performans hatalarının düzeltmesi "
                f"YALNIZCA bu yolda geçerlidir)."
            )
            _native_config_verisi = {k: v for k, v in _ham_config.items() if k != "auto_map"}
            _native_config_verisi = agir_kernel_bayraklarini_yumusat(_native_config_verisi)
            # HATA (kullanıcının açık talebi -- "KeyError: '-'" kökten çöz):
            # nemotron_h checkpoint'inin config.json'undaki hybrid_override_
            # pattern alanı katmanlar arasına "-" koyuyor (ör. "M-M-M-M*-...").
            # ÖNCEKİ İKİ DÜZELTME DE YANLIŞTI: "-"yi silmek katman sayısını
            # (52->28) bozuyordu; "-"yi tamamen belirsiz sayıp 0. kademeyi
            # iptal etmek de KENDİ İÇİNDE bir başka regresyona (küresel Auto*
            # kayıt kirlenmesi) yol açtı. GERÇEK ANLAM artık checkpoint'in
            # KENDİ configuration_nemotron_h.py'sinden (kullanıcının Kaggle'da
            # doğrudan grep'lediği kaynak) KANITLANDI:
            #   layers_block_type[i] = "mamba" if pattern[i]=="M" else
            #                           "attention" if pattern[i]=="*" else "mlp"
            # yani "-" (M/*'DAN FARKLI HER KARAKTER) -> "mlp" (düz MLP-only
            # katman, ne Mamba2 ne attention). transformers'ın NATIVE
            # NemotronHConfig._pattern_to_list'i ise yalnızca {"M","E","*"}
            # tanıyor, "mlp" düşüşünü (else dalını) DESTEKLEMİYOR -- bu
            # yüzden pattern STRING'i native koda hiç verilmiyor; bunun
            # yerine checkpoint'in KENDİ (kanıtlanmış doğru) mantığıyla
            # layers_block_type LİSTESİ burada elle hesaplanıp DOĞRUDAN
            # geçiriliyor -- native config, layers_block_type açıkça
            # verildiğinde hybrid_override_pattern'i zaten hiç okumuyor
            # (transformers kaynağından ayrıca doğrulandı).
            _ham_pattern = _native_config_verisi.get("hybrid_override_pattern")
            if isinstance(_ham_pattern, str):
                _native_config_verisi["layers_block_type"] = [
                    "mamba" if karakter == "M" else "attention" if karakter == "*" else "mlp"
                    for karakter in _ham_pattern
                ]
            _native_config = CONFIG_MAPPING[_model_turu](**_native_config_verisi)
            return AutoModelForCausalLM.from_pretrained(
                yol, config=_native_config, dtype=veri_tipi, device_map="cuda",
                trust_remote_code=False, local_files_only=True,
            )
    except Exception as _sifirinci_hata:
        print(f"[ttt_lora] 0. kademe (native sınıf zorlama) uygulanamadı: {_sifirinci_hata}")
        # HATA (kullanıcının gerçek Kaggle logunda görülen İKİNCİ, DAHA
        # KÖTÜ regresyon -- "MISSING"/"UNEXPECTED" onlarca anahtar, katman
        # 1-27 ile 28-51 arası tipler birbirine karışmış): 0. kademe
        # başarısız olup 2. kademeye (ozel_kodu_manuel_kaydet) düşüldüğünde,
        # bu kademenin config.json'daki auto_map'i okuyup ESKİ/checkpoint-içi
        # Config/Model sınıflarını transformers'ın KÜRESEL Auto* kayıt
        # defterlerine (AutoConfig.register/AutoModelForCausalLM.register)
        # kaydetmesi, transformers'ın KENDİ trust_remote_code=True dinamik
        # modül önbelleğiyle (~/.cache/huggingface/modules/...) ÇAKIŞIP 4.
        # kademenin (trust_remote_code=True) DAHA ÖNCE (tier 0 hiç yokken)
        # TEMİZ ÇALIŞAN halinden FARKLI, BOZUK bir sonuç üretmesine yol
        # açmış görünüyor -- kesin mekanizma doğrulanamadı ama gözlem NET:
        # tier 0 eklenmeden ÖNCE tek başına trust_remote_code=True TÜM
        # ağırlıkları (311/311, MISSING/UNEXPECTED YOK) sorunsuz yüklemişti.
        # Bu yüzden 0. kademe HANGİ SEBEPLE olursa olsun başarısız olunca
        # (yalnızca belirli bir hata metniyle SINIRLI TUTMADAN -- bu
        # kısayolun genel bir güvenlik önlemi olması gerekiyor), 2/3.
        # kademelerin (küresel kayıt defterini kirletme riski taşıyan)
        # HİÇBİRİNE uğramadan DOĞRUDAN 4. kademeye (temiz, kanıtlanmış
        # trust_remote_code=True) atlıyoruz.
        print(
            "[ttt_lora] 0. kademe başarısız olduğu için, küresel Auto* kayıt defterini kirletme riski "
            "taşıyan 1-3. kademeler ATLANIP doğrudan kanıtlanmış temiz trust_remote_code=True yoluna "
            "geçiliyor."
        )
        return _cache_parametre_uyumsuzlugunu_duzelt(AutoModelForCausalLM.from_pretrained(
            yol, dtype=veri_tipi, device_map="cuda",
            trust_remote_code=True, local_files_only=True,
        ))

    def _yumusatilmis_config(guven_kodu: bool) -> Optional[Any]:
        # HATA (kullanıcının açık talebi -- "mamba-ssm is required ...
        # başkası için de yapıyorsa kökten çöz"): bazı trust_remote_code
        # mimarileri (Nemotron-H gibi) config.json'da use_mamba_kernels=
        # True taşır ve model KURULURKEN mamba_ssm/causal_conv1d import
        # edilemezse ImportError fırlatır. Burada AutoConfig ÖNCEDEN
        # yüklenip agir_kernel_bayraklarini_yumusat ile yumuşatılır, sonra
        # from_pretrained'e config=... olarak AÇIKÇA verilir -- from_
        # pretrained kendi config'ini içeride YENİDEN okumaz. Config
        # yüklemenin kendisi başarısız olursa (ör. bu tier zaten hub-tarzı
        # bir hatayla karşılaşacaksa) None döner, çağıran eski davranışa
        # (config=None, from_pretrained kendi config'ini okur) düşer.
        try:
            from ozel_kod_kaydi import agir_kernel_bayraklarini_yumusat
            config = AutoConfig.from_pretrained(yol, trust_remote_code=guven_kodu, local_files_only=True)
            for anahtar, deger in agir_kernel_bayraklarini_yumusat(config.to_dict()).items():
                if hasattr(config, anahtar):
                    setattr(config, anahtar, deger)
            return config
        except Exception:
            return None

    try:
        return AutoModelForCausalLM.from_pretrained(
            yol, config=_yumusatilmis_config(False), dtype=veri_tipi, device_map="cuda",
            trust_remote_code=False, local_files_only=True,
        )
    except Exception as ilk_hata:
        if not _hub_tarzi_hata_mi(ilk_hata):
            raise
        print(f"[ttt_lora] 1. kademe (from_pretrained) başarısız: {ilk_hata}")

    from ozel_kod_kaydi import dogrudan_yukle, ozel_kodu_manuel_kaydet

    try:
        ozel_kodu_manuel_kaydet(yol)
        return _cache_parametre_uyumsuzlugunu_duzelt(AutoModelForCausalLM.from_pretrained(
            yol, config=_yumusatilmis_config(False), dtype=veri_tipi, device_map="cuda",
            trust_remote_code=False, local_files_only=True,
        ))
    except Exception as ikinci_hata:
        print(f"[ttt_lora] 2. kademe (manuel kayıt + from_pretrained) başarısız: {ikinci_hata}")

    try:
        return _cache_parametre_uyumsuzlugunu_duzelt(dogrudan_yukle(yol, veri_tipi=veri_tipi))
    except Exception as ucuncu_hata:
        print(f"[ttt_lora] 3. kademe (dogrudan_yukle) başarısız: {ucuncu_hata}")

    return _cache_parametre_uyumsuzlugunu_duzelt(AutoModelForCausalLM.from_pretrained(
        yol, config=_yumusatilmis_config(True), dtype=veri_tipi, device_map="cuda",
        trust_remote_code=True, local_files_only=True,
    ))


def tokenizer_yukle(model_ailesi: str) -> Any:
    yol = yerel_model_yolu(model_ailesi)

    if model_ailesi == RWKV:
        from rwkv_native import native_rwkv_tokenizer_yukle, rwkv_ham_pth_mi
        if rwkv_ham_pth_mi(yol):
            return native_rwkv_tokenizer_yukle()

    from transformers import AutoTokenizer

    try:
        tok = AutoTokenizer.from_pretrained(yol, trust_remote_code=False, local_files_only=True)
    except Exception as ilk_hata:
        if not _hub_tarzi_hata_mi(ilk_hata):
            raise
        print(f"[ttt_lora] tokenizer 1. kademe başarısız: {ilk_hata}")

        from ozel_kod_kaydi import ozel_kodu_manuel_kaydet
        try:
            ozel_kodu_manuel_kaydet(yol)
            tok = AutoTokenizer.from_pretrained(yol, trust_remote_code=False, local_files_only=True)
        except Exception as ikinci_hata:
            print(f"[ttt_lora] tokenizer 2. kademe başarısız: {ikinci_hata}")
            tok = AutoTokenizer.from_pretrained(yol, trust_remote_code=True, local_files_only=True)

    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    return tok


def lora_adaptoru_kur(base_model: Any, model_ailesi: str, r: int = 8, alpha: int = 16, dropout: float = 0.05) -> Any:
    from rwkv_native import RWKVUyumluModel

    if isinstance(base_model, RWKVUyumluModel):
        # `rwkv` pip paketinin agirliklari (self.w) standart nn.Linear
        # alt-moduller DEGIL, duz bir tensor sozlugu; peft.get_peft_model
        # target_modules eslesmesini nn.Module agac gezintisiyle yapar ve
        # bu yapida CALISMAZ. Bunun yerine RWKV toplulugunun kendi PEFT
        # yontemi olan STATE-TUNING kullanilir: agirliklara dokunmadan,
        # yalnizca ogrenilebilir bir baslangic RNN durumu egitilir.
        from rwkv_state_tuning import RWKVDurumAyarlayici, state_egitimi_calisir_mi_dogrula

        durum_ayarlayici = RWKVDurumAyarlayici(base_model)
        try:
            state_egitimi_calisir_mi_dogrula(durum_ayarlayici)
        except RuntimeError as autograd_hatasi:
            # `rwkv` pip paketinin forward_one/forward_seq'i KENDI
            # KAYNAĞINDA torch.no_grad() ile sarmalı (yalnızca çıkarım
            # için yazılmış, gradyan akışına izin vermiyor) -- bu durumda
            # state-tuning hiçbir zaman çalışamaz. TTT'siz devam etmek,
            # tüm çalıştırmayı çökertmekten iyidir: çıkarım/MCTS dallanma
            # etkilenmeden çalışır, yalnızca görev-başına ince ayar yok.
            print(
                "[ttt_lora] UYARI: state-tuning autograd doğrulaması başarısız "
                f"({autograd_hatasi}). `rwkv` pip paketi bu strateji altında yalnızca "
                "çıkarım içindir (forward'ları no_grad ile sarmalı). TTT bu model için "
                "DEVRE DIŞI bırakılıyor; çıkarım/değerlendirme etkilenmeden çalışacak."
            )
            return base_model

        print(
            "[ttt_lora] native RWKV (.pth) için state-tuning devreye alındı "
            f"({sum(p.numel() for p in durum_ayarlayici.durum_parametreleri)} öğrenilebilir "
            f"state parametresi) — autograd doğrulaması geçti, TTT bu model için AKTİF."
        )
        return durum_ayarlayici

    from peft import LoraConfig, get_peft_model

    hedef_moduller = LORA_HEDEF_MODULLERI[model_ailesi]

    peft_config = LoraConfig(
        r=r,
        lora_alpha=alpha,
        target_modules=hedef_moduller,
        lora_dropout=dropout,
        bias="none",
        task_type="CAUSAL_LM",
    )
    return get_peft_model(base_model, peft_config)


def adaptoru_sifirla(lora_model: Any) -> None:
    if hasattr(lora_model, "durum_ayari"):
        lora_model.sifirla()
        return
    with torch.no_grad():
        for isim, parametre in lora_model.named_parameters():
            if "lora_A" in isim:
                torch.nn.init.kaiming_uniform_(parametre, a=5 ** 0.5)
            elif "lora_B" in isim:
                torch.nn.init.zeros_(parametre)


_TAMAMLAMA_ISARETLERI = {
    RWKV: ("Assistant:", "\n\n"),
    "mamba": ("Output:\n", "\n\n"),
    "falcon_mamba": ("Output:\n", "\n\n"),
}


def _tamamlama_araliklarini_bul(metin: str, baslangic_isareti: str, bitis_isareti: str) -> List[Any]:
    araliklar = []
    idx = 0
    while True:
        b = metin.find(baslangic_isareti, idx)
        if b == -1:
            break
        b_icerik = b + len(baslangic_isareti)
        e = metin.find(bitis_isareti, b_icerik)
        e = e if e != -1 else len(metin)
        araliklar.append((b_icerik, e))
        idx = e
    return araliklar


def _tamamlama_sadece_etiketleri_olustur(
    tokenizer: Any, metin: str, model_ailesi: str, input_ids: List[int], offsetler: Optional[List[Any]]
) -> Optional[List[int]]:
    """arc_solver.py'deki QwenDataCollatorForCompletionOnlyLM'in genel
    hali: USER_TOKEN_ID/ASSISTANT_TOKEN_ID gibi TEK bir tokenizer'a
    (Qwen) sabitlenmis token ID'leri yerine, metindeki 'Assistant:'/
    'Output:\\n' gibi donus isaretlerinin KARAKTER araliklarini bulup,
    hizli tokenizer'in offset_mapping'i ile bu araliklarin disinda kalan
    (yani kullanicinin/girdinin oldugu) tum tokenlari -100 ile maskeler.
    Yalnizca modelin URETMESI gereken asistan/cikti kismindan gradyan
    alinir. offset_mapping desteklenmeyen (yavas) bir tokenizer icin
    None doner; cagiran taraf bu durumda tam-dizi kaybina duser."""
    if offsetler is None:
        return None

    isaretler = _TAMAMLAMA_ISARETLERI.get(model_ailesi)
    if isaretler is None:
        return None

    tamamlama_araliklari = _tamamlama_araliklarini_bul(metin, *isaretler)
    if not tamamlama_araliklari:
        return None

    etiketler: List[int] = []
    for i, (tok_b, tok_e) in enumerate(offsetler):
        icinde_mi = any(a_b <= tok_b < a_e for a_b, a_e in tamamlama_araliklari)
        etiketler.append(input_ids[i] if icinde_mi else -100)

    if all(e == -100 for e in etiketler):
        return None
    return etiketler


def gorev_ozelinde_ince_ayar(
    lora_model: Any,
    tokenizer: Any,
    egitim_metinleri: List[str],
    model_ailesi: Optional[str] = None,
    ogrenme_orani: float = 2e-4,
    adim_sayisi: int = 20,
    azami_token: int = 1024,
    tamamlama_sadece: bool = True,
) -> List[float]:

    if not egitim_metinleri:
        return []

    cihaz = next(lora_model.parameters()).device
    optimizer = torch.optim.AdamW(
        (p for p in lora_model.parameters() if p.requires_grad), lr=ogrenme_orani
    )

    lora_model.train()
    kayip_gecmisi: List[float] = []
    n = len(egitim_metinleri)
    for adim in range(adim_sayisi):
        metin = egitim_metinleri[adim % n]

        etiketler_tensoru = None
        if tamamlama_sadece and model_ailesi is not None:
            try:
                kodlama = tokenizer(
                    metin, return_tensors=None, truncation=True, max_length=azami_token,
                    return_offsets_mapping=True,
                )
                etiketler = _tamamlama_sadece_etiketleri_olustur(
                    tokenizer, metin, model_ailesi, kodlama["input_ids"], kodlama.get("offset_mapping")
                )
                if etiketler is not None:
                    girdiler = {"input_ids": torch.tensor([kodlama["input_ids"]], dtype=torch.long, device=cihaz)}
                    etiketler_tensoru = torch.tensor([etiketler], dtype=torch.long, device=cihaz)
            except TypeError:
                pass  # tokenizer offset_mapping desteklemiyor -> tam-dizi kaybina duselim

        if etiketler_tensoru is None:
            girdiler = tokenizer(
                metin, return_tensors="pt", truncation=True, max_length=azami_token
            ).to(cihaz)
            etiketler_tensoru = girdiler["input_ids"]

        ciktilar = lora_model(**girdiler, labels=etiketler_tensoru)
        kayip = ciktilar.loss

        optimizer.zero_grad(set_to_none=True)
        kayip.backward()
        torch.nn.utils.clip_grad_norm_(
            (p for p in lora_model.parameters() if p.requires_grad), max_norm=1.0
        )
        optimizer.step()

        kayip_gecmisi.append(float(kayip.detach().item()))

    lora_model.eval()
    return kayip_gecmisi


def rwkv_tek_mesaji_sar(mesaj: Dict[str, str]) -> str:
    """Tek bir mesaji (rol/icerik) RWKV metin sablonuna sarar. `rwkv_oturum.
    RWKVSohbetOturumu` (bkz. o dosya) bunu, HER turde TUM gecmisi yeniden
    metne cevirmek yerine yalnizca YENI eklenen mesaji islemek icin kullanir
    -- `_rwkv_mesajlari_metne_sar` ile AYNI sarma mantigi (tek mesajlik
    ozel durumu), tek kaynaktan (bu fonksiyon) beslenir."""
    rol, icerik = mesaj["role"], mesaj["content"]
    if rol == "system":
        return icerik if icerik.startswith("System:") else f"System: {icerik}"
    if rol == "user" or rol == "tool":
        return kullanici_donusu_sar(icerik, RWKV)
    if rol == "assistant":
        return asistan_donusu_sar(icerik, RWKV)
    return ""


def _rwkv_mesajlari_metne_sar(mesajlar: List[Dict[str, str]]) -> str:
    return "".join(rwkv_tek_mesaji_sar(mesaj) for mesaj in mesajlar)


def mesajlari_metne_donustur(tokenizer: Any, model_ailesi: str, mesajlar: List[Dict[str, str]]) -> str:
    if model_ailesi == RWKV:
        return _rwkv_mesajlari_metne_sar(mesajlar)
    if hasattr(tokenizer, "apply_chat_template"):
        return tokenizer.apply_chat_template(mesajlar, tokenize=False, add_generation_prompt=True)
    return "\n".join(f"{m['role']}: {m['content']}" for m in mesajlar) + "\nassistant:"


def uretim_ayarlarini_al(model_ailesi: str, tokenizer: Any, preset: str = "fonksiyon_cagirma") -> Dict[str, Any]:
    """DECODING_ONERILERI'nden do_sample/temperature/top_p/pad_token_id/
    repetition_penalty türetir -- hem uret_sohbet() (tam-yeniden-işleme
    yolu) hem de rwkv_oturum.RWKVSohbetOturumu (artımlı/tek-kez-işleme
    yolu, bkz. coz_yurutucu._tek_deneme_uret) AYNI karar mantığını
    kullanır."""
    ayar = DECODING_ONERILERI[model_ailesi][preset]
    ornekleme = ayar["temp"] > 0.0
    sonuc: Dict[str, Any] = {"do_sample": ornekleme, "pad_token_id": tokenizer.pad_token_id}
    if ornekleme:
        sonuc["temperature"] = ayar["temp"]
        if ayar.get("top_p", 0.0) > 0.0:
            sonuc["top_p"] = ayar["top_p"]
    if ayar.get("repetition_penalty", 1.0) > 1.0:
        sonuc["repetition_penalty"] = ayar["repetition_penalty"]
    return sonuc


def uret_sohbet(
    lora_model: Any,
    tokenizer: Any,
    model_ailesi: str,
    mesajlar: List[Dict[str, str]],
    azami_yeni_token: int = 768,
    preset: str = "fonksiyon_cagirma",
) -> str:
    cihaz = next(lora_model.parameters()).device
    ayar = DECODING_ONERILERI[model_ailesi][preset]

    girdi_metni = mesajlari_metne_donustur(tokenizer, model_ailesi, mesajlar)
    girdiler = tokenizer(girdi_metni, return_tensors="pt").to(cihaz)

    ornekleme = ayar["temp"] > 0.0

    baslangic = time.time()
    print(
        f"[ttt_lora] uret_sohbet: {girdiler['input_ids'].shape[1]} girdi tokeni, "
        f"azami {azami_yeni_token} yeni token üretilecek (prompt-işleme dahil, uzun sürebilir)..."
    )
    with torch.no_grad():
        uretim_kwargs: Dict[str, Any] = dict(
            **girdiler,
            max_new_tokens=azami_yeni_token,
            do_sample=ornekleme,
            pad_token_id=tokenizer.pad_token_id,
        )
        if ornekleme:
            uretim_kwargs["temperature"] = ayar["temp"]
            if ayar.get("top_p", 0.0) > 0.0:
                uretim_kwargs["top_p"] = ayar["top_p"]
        if ayar.get("alpha_presence"):
            uretim_kwargs["repetition_penalty"] = 1.0 + ayar["alpha_presence"] / 10.0
        elif ayar.get("repetition_penalty", 1.0) > 1.0:
            uretim_kwargs["repetition_penalty"] = ayar["repetition_penalty"]

        cikti_idler = lora_model.generate(**uretim_kwargs)

    uretilen = cikti_idler[0][girdiler["input_ids"].shape[1]:]
    gecen = time.time() - baslangic
    print(f"[ttt_lora] uret_sohbet: {len(uretilen)} token üretildi ({gecen:.1f} sn, {len(uretilen) / max(gecen, 1e-6):.2f} token/sn).")
    return tokenizer.decode(uretilen, skip_special_tokens=True)
