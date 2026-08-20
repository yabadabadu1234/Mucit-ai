"""
Derin cozum: transformers'in trust_remote_code=True dinamik modul
cozumleyicisi (get_cached_module_file) yerel bir yolu bile once
huggingface_hub.utils.validate_repo_id() ile "repo_id" gibi dogrulamaya
calisiyor; cok sayida "/" iceren gercek yerel klasor yollari (bizim
Kaggle yollarimiz) bu regex'i geçemedigi icin
"Repo id must be in the form 'repo_name' or 'namespace/repo_name'"
hatasi firlatiyor -- internet KAPALI oldugu icin bu hicbir sekilde hub'a
gitmeden de olmuyor.

Cozum: hub-tarzi cozumlemeyi tamamen atlayip, config.json'daki auto_map
alanindan hangi .py dosyasinin hangi sinifi tasidigini okuyup, o dosyayi
dogrudan importlib ile (hicbir hub/repo_id kavramina dokunmadan) yukleyip
AutoConfig.register / AutoModelForCausalLM.register / AutoTokenizer.register
ile transformers'a KAYDEDIYORUZ. Bu kayittan sonra from_pretrained
trust_remote_code=False ile cagrilabilir; artik ozel kod icin herhangi bir
dinamik/hub cozumlemesi devreye girmez.
"""
import importlib.machinery
import importlib.util
import json
import os
import sys
from typing import Any, Dict, Optional, Tuple, Type

_KAYITLI_MODEL_TURLERI: set = set()

# HATA (kullanıcının açık talebi -- "mamba-ssm is required by the Mamba
# model but cannot be imported ... başkası için de yapıyorsa kökten çöz"):
# bazı trust_remote_code mimarileri (Nemotron-H gibi) config.json'da
# use_mamba_kernels=True taşır ve model KURULURKEN (construction, forward
# DEĞİL) bu bayrak True'yken mamba_ssm/causal_conv1d import edilemezse
# ImportError fırlatır -- resmi transformers'ın kendi Mamba/Mamba2/
# FalconMamba sınıflarının aksine (onlar sessizce yavaş/saf-PyTorch yoluna
# düşer, hata vermez). Kök çözüm: bu bayrakları paket eksikse model
# KURULMADAN ÖNCE burada kapatıp modelin kendi yavaş yoluna düşmesini
# SAĞLAMAK -- yeni bir mimaride benzer bir "ağır isteğe bağlı kernel"
# bayrağı çıkarsa tek yapılması gereken bu sözlüğe bir satır eklemek,
# yükleme zincirinin geri kalanına DOKUNMADAN her model ailesi için
# otomatik olarak devreye girer.
_AGIR_KERNEL_BAYRAKLARI: Dict[str, Tuple[str, ...]] = {
    "use_mamba_kernels": ("mamba_ssm", "causal_conv1d"),
}


def _paketler_mevcut_mu(paket_adlari: Tuple[str, ...]) -> bool:
    import importlib
    for paket in paket_adlari:
        try:
            importlib.import_module(paket)
        except ImportError:
            return False
    return True


def agir_kernel_bayraklarini_yumusat(config_verisi: Dict[str, Any]) -> Dict[str, Any]:
    """`config_verisi` (config.json'dan okunmuş ham sözlük ya da
    `AutoConfig.to_dict()` çıktısı) içindeki _AGIR_KERNEL_BAYRAKLARI'ndan
    her biri True İSE ve gerektirdiği paketler bu ortamda kurulu DEĞİLSE,
    o bayrağı False'a zorlar (kopyası üzerinde -- girdi değiştirilmez).
    Bayrak hiç yoksa (RWKV/GRANITE4/LFM25 gibi bunu hiç taşımayan
    mimariler) hiçbir şey değişmez."""
    config_verisi = dict(config_verisi)
    for bayrak, paketler in _AGIR_KERNEL_BAYRAKLARI.items():
        if config_verisi.get(bayrak) and not _paketler_mevcut_mu(paketler):
            print(
                f"[ozel_kod_kaydi] {'/'.join(paketler)} kurulu değil -- config.{bayrak}=False'a "
                f"zorlanıyor, model kendi yavaş/saf-PyTorch yoluna düşecek (daha yavaş ama ÇALIŞIR)."
            )
            config_verisi[bayrak] = False
    return config_verisi


def _config_oku(yol: str) -> Dict[str, Any]:
    config_yolu = os.path.join(yol, "config.json")
    if not os.path.isfile(config_yolu):
        raise FileNotFoundError(f"config.json bulunamadı: {config_yolu}")
    with open(config_yolu, "r", encoding="utf-8") as f:
        return json.load(f)


def _paket_adi(yol: str) -> str:
    return f"_ozel_kod_paket_{abs(hash(yol)) % 10**8}"


def _sentetik_paketi_kaydet(yol: str) -> str:
    """HATA (kullanıcının açık talebi -- "attempted relative import with
    no known parent package", ardından "module has no attribute
    NemotronHForCausalLM" -- kökten çöz): Nemotron-H'nin (ve büyük
    ihtimalle benzer başka trust_remote_code mimarilerinin) modeling
    dosyası, kendi dizinindeki diğer dosyaları GÖRECELİ import ediyor
    (`from .configuration_nemotron_h import ...`) -- transformers'ın
    RESMİ trust_remote_code yükleyicisi (get_cached_module_file) bunu,
    dosyaları GERÇEK bir paket klasörüne KOPYALAYIP __init__.py ekleyerek
    çözer. Biz repo_id doğrulaması yüzünden o yolu kullanamıyoruz (bkz.
    dosya başındaki not), ama AYNI sonucu kopyalamadan da elde edebiliriz:
    `yol` dizinini sys.modules'a __path__'i o dizine işaret eden SENTETİK
    bir paket olarak kaydedersek, Python'ın KENDİ import makinesi o
    dizindeki `.py` dosyalarını normal alt-modül olarak bulup GÖRECELİ
    importları KENDİSİ çözer -- elle hiçbir ek iş gerekmez."""
    paket_adi = _paket_adi(yol)
    if paket_adi not in sys.modules:
        paket = importlib.util.module_from_spec(
            importlib.machinery.ModuleSpec(paket_adi, loader=None, is_package=True)
        )
        paket.__path__ = [yol]
        sys.modules[paket_adi] = paket
    return paket_adi


def _dosyadan_sinif_yukle(yol: str, referans: str) -> Type:
    """referans formatı: 'modeling_rwkv7.Rwkv7ForCausalLM' gibi
    'dosya_adi.SinifAdi'. Dosyayı doğrudan yerel yoldan, hiçbir
    hub/repo_id kavramına dokunmadan importlib ile yükler -- ama
    _sentetik_paketi_kaydet sayesinde dosyanın KENDİ İÇİNDEKİ göreceli
    importlar (aynı dizindeki başka bir dosyadan) da çalışır."""
    if "." not in referans:
        raise ValueError(f"Beklenmeyen auto_map referansı: {referans!r}")
    modul_dosya_adi, sinif_adi = referans.rsplit(".", 1)
    modul_yolu = os.path.join(yol, f"{modul_dosya_adi}.py")
    if not os.path.isfile(modul_yolu):
        raise FileNotFoundError(
            f"Özel kod dosyası bulunamadı: {modul_yolu}. "
            f"'{yol}' dizininin içeriğini kontrol edin (dosya adı auto_map ile eşleşmiyor olabilir)."
        )

    paket_adi = _sentetik_paketi_kaydet(yol)
    tam_modul_adi = f"{paket_adi}.{modul_dosya_adi}"
    if tam_modul_adi in sys.modules:
        return getattr(sys.modules[tam_modul_adi], sinif_adi)

    spec = importlib.util.spec_from_file_location(tam_modul_adi, modul_yolu, submodule_search_locations=[])
    if spec is None or spec.loader is None:
        raise ImportError(f"'{modul_yolu}' için import spec oluşturulamadı.")
    modul = importlib.util.module_from_spec(spec)
    modul.__package__ = paket_adi
    sys.modules[tam_modul_adi] = modul
    setattr(sys.modules[paket_adi], modul_dosya_adi, modul)

    onceki_dizin = list(sys.path)
    if yol not in sys.path:
        sys.path.insert(0, yol)
    try:
        spec.loader.exec_module(modul)
    except BaseException:
        # HATA (kullanıcının gerçek Kaggle logunda görülen İKİNCİ hata --
        # "module has no attribute NemotronHForCausalLM" -- bu, BİRİNCİ
        # denemenin (relative-import hatasıyla) YARIM kalmış modülünün
        # sys.modules'ta KALIP bir SONRAKİ (dogrudan_yukle) denemesinde
        # "zaten yüklü" sanılıp AYNEN geri döndürülmesinden kaynaklanıyordu.
        # Artık başarısız bir exec_module SONRASI yarım modül sys.modules'
        # tan SİLİNİYOR -- bir sonraki deneme SIFIRDAN, temiz başlıyor.
        sys.modules.pop(tam_modul_adi, None)
        raise
    finally:
        sys.path[:] = onceki_dizin

    return getattr(modul, sinif_adi)


def ozel_kodu_manuel_kaydet(yol: str) -> Tuple[Optional[Type], Optional[Type]]:
    """config.json'daki auto_map'i okuyup Config/Model sınıflarını
    doğrudan dosyadan yükler ve transformers'ın Auto* kayıt defterine
    ekler. Döner: (ConfigSinifi_or_None, ModelSinifi_or_None).

    Bu fonksiyon çağrıldıktan sonra `AutoModelForCausalLM.from_pretrained(
    yol, trust_remote_code=False, local_files_only=True)` artık hub-tarzı
    hiçbir çözümlemeye ihtiyaç duymadan doğrudan çalışabilir."""
    from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer

    config_verisi = _config_oku(yol)
    auto_map = config_verisi.get("auto_map", {})
    if not auto_map:
        raise RuntimeError(
            f"'{yol}' içindeki config.json 'auto_map' alanı taşımıyor; "
            f"bu model özel kod gerektirmiyor olabilir (trust_remote_code=False zaten yeterli)."
        )

    model_turu = config_verisi.get("model_type")

    ConfigSinifi: Optional[Type] = None
    config_referansi = auto_map.get("AutoConfig")
    if config_referansi:
        ConfigSinifi = _dosyadan_sinif_yukle(yol, config_referansi)
        if model_turu and model_turu not in _KAYITLI_MODEL_TURLERI:
            try:
                AutoConfig.register(model_turu, ConfigSinifi)
                _KAYITLI_MODEL_TURLERI.add(model_turu)
            except ValueError:
                # zaten kayıtlı (aynı süreçte tekrar çağrılmış olabilir)
                _KAYITLI_MODEL_TURLERI.add(model_turu)

    ModelSinifi: Optional[Type] = None
    model_referansi = (
        auto_map.get("AutoModelForCausalLM")
        or auto_map.get("AutoModel")
    )
    if model_referansi:
        ModelSinifi = _dosyadan_sinif_yukle(yol, model_referansi)
        if ConfigSinifi is not None:
            try:
                AutoModelForCausalLM.register(ConfigSinifi, ModelSinifi)
            except ValueError:
                pass

    tokenizer_referansi = auto_map.get("AutoTokenizer")
    if tokenizer_referansi:
        # auto_map["AutoTokenizer"] bazen [hizli, yavas] iki elemanli liste olur
        tek_referans = tokenizer_referansi[0] if isinstance(tokenizer_referansi, list) else tokenizer_referansi
        if tek_referans:
            TokenizerSinifi = _dosyadan_sinif_yukle(yol, tek_referans)
            if ConfigSinifi is not None:
                try:
                    AutoTokenizer.register(ConfigSinifi, slow_tokenizer_class=TokenizerSinifi)
                except ValueError:
                    pass

    return ConfigSinifi, ModelSinifi


def _agirlik_dosyalarini_bul(yol: str) -> Tuple[str, list]:
    """Sharded/tekil safetensors ya da .bin agirlik dosyalarini, hicbir
    hub/index-cozumleme cagrisi yapmadan, DOGRUDAN dizin listelemesiyle
    bulur. Doner: (bicim, [dosya_yollari])."""
    dosyalar = set(os.listdir(yol))

    if "model.safetensors.index.json" in dosyalar:
        with open(os.path.join(yol, "model.safetensors.index.json"), "r", encoding="utf-8") as f:
            index = json.load(f)
        parcalar = sorted(set(index.get("weight_map", {}).values()))
        return "safetensors", [os.path.join(yol, p) for p in parcalar]

    if "model.safetensors" in dosyalar:
        return "safetensors", [os.path.join(yol, "model.safetensors")]

    if "pytorch_model.bin.index.json" in dosyalar:
        with open(os.path.join(yol, "pytorch_model.bin.index.json"), "r", encoding="utf-8") as f:
            index = json.load(f)
        parcalar = sorted(set(index.get("weight_map", {}).values()))
        return "bin", [os.path.join(yol, p) for p in parcalar]

    if "pytorch_model.bin" in dosyalar:
        return "bin", [os.path.join(yol, "pytorch_model.bin")]

    raise FileNotFoundError(
        f"'{yol}' içinde model.safetensors(.index.json) ya da pytorch_model.bin(.index.json) "
        f"bulunamadı. Dizindeki dosyalar: {sorted(dosyalar)}"
    )


def dogrudan_yukle(yol: str, veri_tipi: Any = None) -> Any:
    """`AutoModelForCausalLM.from_pretrained` HİÇ çağrılmadan, config.json
    ve ağırlık dosyaları DOĞRUDAN diskten okunup model bu şekilde kurulur.
    huggingface_hub'ın repo_id doğrulaması dahil hiçbir kod yolu devreye
    girmez -- bu, "internet aramasını ve huggingface'i tamamen iptal et"
    talebinin harfiyen karşılandığı, en dip seviye yükleme yoludur."""
    import torch

    config_verisi = agir_kernel_bayraklarini_yumusat(_config_oku(yol))
    auto_map = config_verisi.get("auto_map", {})

    ConfigSinifi: Optional[Type] = None
    config_referansi = auto_map.get("AutoConfig")
    if config_referansi:
        ConfigSinifi = _dosyadan_sinif_yukle(yol, config_referansi)

    ModelSinifi: Optional[Type] = None
    model_referansi = auto_map.get("AutoModelForCausalLM") or auto_map.get("AutoModel")
    if model_referansi:
        ModelSinifi = _dosyadan_sinif_yukle(yol, model_referansi)

    if ConfigSinifi is None or ModelSinifi is None:
        # ozel kod yoksa (auto_map bos), transformers'in kendi yerlesik
        # sinifini model_type uzerinden CONFIG_MAPPING/MODEL_MAPPING'den
        # hub'a hic dokunmadan bulur.
        from transformers.models.auto.configuration_auto import CONFIG_MAPPING
        from transformers.models.auto.modeling_auto import MODEL_FOR_CAUSAL_LM_MAPPING

        model_turu = config_verisi.get("model_type")
        if ConfigSinifi is None:
            ConfigSinifi = CONFIG_MAPPING[model_turu]
        if ModelSinifi is None:
            ModelSinifi = MODEL_FOR_CAUSAL_LM_MAPPING[type(ConfigSinifi())]

    config = ConfigSinifi(**config_verisi)

    model = ModelSinifi(config)

    bicim, agirlik_dosyalari = _agirlik_dosyalarini_bul(yol)
    tam_state_dict: Dict[str, Any] = {}
    if bicim == "safetensors":
        from safetensors.torch import load_file
        for dosya in agirlik_dosyalari:
            tam_state_dict.update(load_file(dosya))
    else:
        for dosya in agirlik_dosyalari:
            tam_state_dict.update(torch.load(dosya, map_location="cpu"))

    eksik, fazla = model.load_state_dict(tam_state_dict, strict=False)
    if eksik:
        print(f"[ozel_kod_kaydi] Uyarı: state_dict'te eksik {len(eksik)} anahtar (ör. {eksik[:3]})")
    if fazla:
        print(f"[ozel_kod_kaydi] Uyarı: state_dict'te fazla {len(fazla)} anahtar (ör. {fazla[:3]})")

    if veri_tipi is not None:
        model = model.to(veri_tipi)
    if torch.cuda.is_available():
        model = model.to("cuda")

    return model
