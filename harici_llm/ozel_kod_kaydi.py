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
import importlib.util
import json
import os
import sys
from typing import Any, Dict, Optional, Tuple, Type

_KAYITLI_MODEL_TURLERI: set = set()


def _config_oku(yol: str) -> Dict[str, Any]:
    config_yolu = os.path.join(yol, "config.json")
    if not os.path.isfile(config_yolu):
        raise FileNotFoundError(f"config.json bulunamadı: {config_yolu}")
    with open(config_yolu, "r", encoding="utf-8") as f:
        return json.load(f)


def _dosyadan_sinif_yukle(yol: str, referans: str) -> Type:
    """referans formatı: 'modeling_rwkv7.Rwkv7ForCausalLM' gibi
    'dosya_adi.SinifAdi'. Dosyayı doğrudan yerel yoldan, hiçbir
    hub/repo_id kavramına dokunmadan importlib ile yükler."""
    if "." not in referans:
        raise ValueError(f"Beklenmeyen auto_map referansı: {referans!r}")
    modul_dosya_adi, sinif_adi = referans.rsplit(".", 1)
    modul_yolu = os.path.join(yol, f"{modul_dosya_adi}.py")
    if not os.path.isfile(modul_yolu):
        raise FileNotFoundError(
            f"Özel kod dosyası bulunamadı: {modul_yolu}. "
            f"'{yol}' dizininin içeriğini kontrol edin (dosya adı auto_map ile eşleşmiyor olabilir)."
        )

    benzersiz_modul_adi = f"_ozel_kod_{modul_dosya_adi}_{abs(hash(yol)) % 10**8}"
    if benzersiz_modul_adi in sys.modules:
        return getattr(sys.modules[benzersiz_modul_adi], sinif_adi)

    spec = importlib.util.spec_from_file_location(benzersiz_modul_adi, modul_yolu)
    if spec is None or spec.loader is None:
        raise ImportError(f"'{modul_yolu}' için import spec oluşturulamadı.")
    modul = importlib.util.module_from_spec(spec)
    sys.modules[benzersiz_modul_adi] = modul

    onceki_dizin = list(sys.path)
    if yol not in sys.path:
        sys.path.insert(0, yol)
    try:
        spec.loader.exec_module(modul)
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
