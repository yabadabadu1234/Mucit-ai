"""
Model ailesi basina ayri yapilandirma: yerel dosya yolu (internet YOK, indirme
YOK), sohbet/fonksiyon-cagirma sablonlari, kod cozme (decoding) onerileri.

Her aile icin kullanicinin verdigi resmi README bilgisi buraya birebir
tasindi. Yeni bir model eklendiginde yalnizca bu dosyaya yeni bir giris
eklemek yeterli; ttt_lora.py, arc_loader.py, coz_yurutucu.py hepsi buradan
okur.
"""
import os
from typing import Any, Dict, List, Optional

# Internet erisimi TAMAMEN kapatilir: huggingface_hub/transformers'in HER
# TURLU hub-tarzi cozumlemesi (repo_id dogrulamasi, "dosya var mi" agdan
# sorma, vb.) bu ortam degiskenleriyle devre disi birakilir. Bu dosya,
# harici_llm'deki diger her modulden ONCE import edildigi icin (ttt_lora.py
# dahil hepsi buradan okur) burada set edilmesi transformers ilk kez
# import edilmeden once devreye girer.
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("HF_DATASETS_OFFLINE", "1")
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
os.environ.setdefault("HF_HUB_DISABLE_IMPLICIT_TOKEN", "1")

RWKV = "rwkv"
MAMBA = "mamba"
FALCON_MAMBA = "falcon_mamba"

# ==============================================================================
# YEREL DOSYA YOLLARI — internet KAPALI, model asla indirilmeyecek.
# Kaggle input dizinine yerel olarak eklenmis model klasorlerine isaret eder.
# ==============================================================================
YEREL_MODEL_YOLLARI: Dict[str, str] = {
    # model_indir.py ile indirilen HAM .pth kontrol noktası (transformers
    # config.json TAŞIMIYOR) — bkz. rwkv_native.py, ttt_lora.py bu dosya
    # yolunu görünce otomatik olarak `rwkv` pip paketiyle yükler.
    RWKV: "/kaggle/input/notebooks/ulankaggle/harici-llm/modeller/rwkv/rwkv7-g1i-7.2b-20260805-ctx16384.pth",
    MAMBA: "/kaggle/input/models/ulankaggle/mistral-mamba-codestral-7b-v0-1/transformers/default/1/Mamba-Codestral-7B-v0.1",
    FALCON_MAMBA: "/kaggle/input/falcon-mamba-7b-instruct/transformers/default/1",
}

# Ana model / yedek model sirasi: gonderim_uret.py ana modeli yuklemeyi
# dener, basarisiz olursa (dosya eksik/bozuk, OOM, mimari desteklenmiyor
# vb.) otomatik olarak yedek modele duser.
MODEL_ONCELIK_SIRASI: List[str] = [RWKV, MAMBA]

# ==============================================================================
# LoRA hedef modulleri (mimari basina)
# ==============================================================================
LORA_HEDEF_MODULLERI: Dict[str, List[str]] = {
    RWKV: ["key", "value", "receptance", "output", "gate"],
    MAMBA: ["in_proj", "out_proj", "x_proj", "dt_proj"],
    FALCON_MAMBA: ["in_proj", "out_proj", "x_proj", "dt_proj"],
}

# ==============================================================================
# RWKV-7 boyut tablosu (README'den birebir)
# ==============================================================================
RWKV_BOYUT_TABLOSU: Dict[str, Dict[str, int]] = {
    "0.1B": {"L": 12, "D": 768},
    "0.4B": {"L": 24, "D": 1024},
    "1.5B": {"L": 24, "D": 2048},
    "2.9B": {"L": 32, "D": 2560},
    "7.2B": {"L": 32, "D": 4096},
    "13.3B": {"L": 61, "D": 4096},
}
RWKV_VOCAB_BOYUTU = 65536
RWKV_HEAD_BOYUTU = 64

# ==============================================================================
# DECODING (uretim parametreleri) ONERILERI — README'den birebir
# ==============================================================================
DECODING_ONERILERI: Dict[str, Dict[str, Dict[str, float]]] = {
    RWKV: {
        # Fonksiyon cagirma / agent: deterministik, sicaklik=0
        "fonksiyon_cagirma": {"temp": 0.0, "top_p": 0.0, "penalty": 0.0},
        # not: RWKV pip paketi topp'u temp'ten SONRA uygular
        "sohbet": {"temp": 1.0, "top_p": 0.5, "alpha_presence": 2.0, "alpha_frequency": 0.1, "alpha_decay": 0.99},
        "yaratici": {"temp": 0.6, "top_p": 0.7, "alpha_presence": 2.0, "alpha_frequency": 0.2, "alpha_decay": 0.99},
    },
    MAMBA: {
        "fonksiyon_cagirma": {"temp": 0.0, "top_p": 1.0, "penalty": 0.0},
        "sohbet": {"temp": 0.7, "top_p": 0.9, "penalty": 0.0},
    },
    FALCON_MAMBA: {
        "fonksiyon_cagirma": {"temp": 0.0, "top_p": 1.0, "penalty": 0.0},
        "sohbet": {"temp": 0.7, "top_p": 0.9, "penalty": 0.0},
    },
}

FIM_ONEK_TOKENI = "✿prefix✿"
FIM_SONEK_TOKENI = "✿suffix✿"
FIM_ORTA_TOKENI = "✿middle✿"


def cevap_sonu_isaretleri(model_ailesi: str) -> str:
    """Bir donusun (turn) bittigini isaretleyen ayirici. RWKV pretrain
    verisinde '\\n\\n' 'sohbet turu ayiricisi' olarak kullanildigindan,
    RWKV icin USER_PROMPT icindeki tum '\\n\\n' -> '\\n' donusturulmelidir
    (bkz. rwkv_kullanici_metnini_temizle)."""
    if model_ailesi == RWKV:
        return "\n\n"
    return ""


def rwkv_kullanici_metnini_temizle(metin: str) -> str:
    """README uyarisi: '\\n\\n' RWKV pretrain verisinde sohbet turu ayiricisi
    olarak kullanildigi icin, USER_PROMPT icindeki tum cift satir sonlari
    tek satir sonuna indirilmelidir."""
    while "\n\n" in metin:
        metin = metin.replace("\n\n", "\n")
    return metin


def kullanici_donusu_sar(metin: str, model_ailesi: str) -> str:
    if model_ailesi == RWKV:
        return f"User: {rwkv_kullanici_metnini_temizle(metin)}\n\nAssistant:"
    # Mamba / Falcon-Mamba: standart HF chat sablonuna birakiyoruz,
    # burada yalnizca ham metni donduruyoruz (apply_chat_template
    # cagiran taraf role='user' olarak sarmalayacak).
    return metin


def asistan_donusu_sar(metin: str, model_ailesi: str) -> str:
    if model_ailesi == RWKV:
        return f" {metin}"
    return metin


def rwkv_fonksiyon_cagirma_sistem_promptu(tool_tanimlari_metni: str) -> str:
    """README'deki iki resmi RWKV-7 G1 fonksiyon-cagirma sablonundan
    (duz liste ve JSON-array) JSON-array bicimini kullanir; <think></think>
    (sahte dusunme) ile birlikte."""
    return f"System: Tools:\n{tool_tanimlari_metni}\nReturn only a JSON function call.\n\n"


def rwkv_dusunme_promptu_sar(kullanici_metni: str, mod: str = "fake") -> str:
    """
    mod:
      'fake'  -> '<think></think' (bos dusunme, en yuksek tavsiye edilen)
      'think' -> '<think' (gercek dusunme, zor promptlar icin)
      'kisa'  -> '(think a bit)' + '<think'
      'uzun'  -> '(think a lot)' + '<think'
    """
    temiz = rwkv_kullanici_metnini_temizle(kullanici_metni)
    if mod == "fake":
        return f"User: {temiz}\n\nAssistant: <think></think"
    if mod == "kisa":
        return f"User: {temiz} (think a bit)\n\nAssistant: <think"
    if mod == "uzun":
        return f"User: {temiz} (think a lot)\n\nAssistant: <think"
    return f"User: {temiz}\n\nAssistant: <think"


def rwkv_fim_promptu(onek: str, sonek: str, orta_yer_tutucu: bool = True) -> str:
    """FIM (fill-in-the-middle) sablonu, G1c ve sonrasi icin. Onerilen bicim:
    onek/sonek bos birakilip gercek onek en sona (middle sonrasina) tasinir."""
    if orta_yer_tutucu:
        return f"{FIM_ONEK_TOKENI}{FIM_SONEK_TOKENI}{sonek}{FIM_ORTA_TOKENI}{onek}"
    return f"{FIM_ONEK_TOKENI}{onek}{FIM_SONEK_TOKENI}{sonek}{FIM_ORTA_TOKENI}"


def model_ailesini_belirle(model_id_veya_yol: str) -> str:
    kucuk = model_id_veya_yol.lower()
    if "rwkv" in kucuk:
        return RWKV
    if "falcon" in kucuk and "mamba" in kucuk:
        return FALCON_MAMBA
    if "mamba" in kucuk:
        return MAMBA
    raise ValueError(f"Bilinmeyen model ailesi: {model_id_veya_yol}")


_ORTAM_DEGISKENI_ADLARI = {
    RWKV: "MUCIT_RWKV_YOLU",
    MAMBA: "MUCIT_MAMBA_YOLU",
    FALCON_MAMBA: "MUCIT_FALCON_MAMBA_YOLU",
}


def yerel_model_yolu(model_ailesi: str, dogrula: bool = True) -> str:
    if model_ailesi not in YEREL_MODEL_YOLLARI:
        raise ValueError(
            f"'{model_ailesi}' icin yerel model yolu tanimli degil. "
            f"Internet erisimi kapali oldugundan model indirilemez; "
            f"YEREL_MODEL_YOLLARI sozlugune gercek Kaggle yolunu ekleyin."
        )

    # model_indir.py ile internet-acik ilk calistirmada indirilen modeller,
    # ikinci (internet-kapali) calistirmada Kaggle'in verdigi GERCEK input
    # yoluna monte edilir -- bu yol onceden bilinemez. Ortam degiskeni
    # (MUCIT_RWKV_YOLU / MUCIT_MAMBA_YOLU / MUCIT_FALCON_MAMBA_YOLU) verilirse
    # sabit YEREL_MODEL_YOLLARI sozlugune HIC bakilmadan o kullanilir.
    ortam_degiskeni = _ORTAM_DEGISKENI_ADLARI.get(model_ailesi)
    if ortam_degiskeni and os.environ.get(ortam_degiskeni):
        yol = os.environ[ortam_degiskeni]
    else:
        yol = YEREL_MODEL_YOLLARI[model_ailesi]

    if dogrula and not (os.path.isdir(yol) or os.path.isfile(yol)):
        # transformers, os.path.isdir() False donerse yolu bir "repo_id"
        # sanip anlasilmaz "Repo id must be in the form..." hatasi
        # firlatiyor. Burada erkenden, GERCEKTEN neyin nerede oldugunu
        # gosteren acik bir teshis veriyoruz. Yol bir dosyaya (.pth gibi)
        # da isaret edebilir -- yalnizca dizin degil dosya varligi da
        # kabul edilir.
        ebeveyn = os.path.dirname(yol.rstrip("/"))
        try:
            ebeveyn_icerigi = sorted(os.listdir(ebeveyn)) if os.path.isdir(ebeveyn) else None
        except OSError as e:
            ebeveyn_icerigi = [f"<listelenemedi: {e}>"]
        raise FileNotFoundError(
            f"'{model_ailesi}' modeli icin belirtilen yerel yol GERCEKTE diskte yok: '{yol}'. "
            f"Ebeveyn dizin ('{ebeveyn}') icerigi: {ebeveyn_icerigi}. "
            f"Kaggle dataset/model eki notebook'a doğru şekilde bağlanmamış olabilir; "
            f"sağdaki 'Add Input' panelinden modelin gerçekten bu isimle eklendiğini "
            f"ve tam yolunu (üstteki listeden) doğrulayın, YEREL_MODEL_YOLLARI'nı buna göre düzeltin."
        )

    return yol
