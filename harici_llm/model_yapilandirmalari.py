"""
Model ailesi basina ayri yapilandirma: yerel dosya yolu (internet YOK, indirme
YOK), sohbet/fonksiyon-cagirma sablonlari, kod cozme (decoding) onerileri.

Her aile icin kullanicinin verdigi resmi README bilgisi buraya birebir
tasindi. Yeni bir model eklendiginde yalnizca bu dosyaya yeni bir giris
eklemek yeterli; ttt_lora.py, arc_loader.py, coz_yurutucu.py hepsi buradan
okur.
"""
import os
from typing import Dict, List, Optional

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

# `rwkv` pip paketinin KENDI kaynagi (rwkv/model.py) modul yuklenirken
# `RWKV_V7_ON` ortam degiskenini kontrol edip, yalnizca '1' ise modul
# sonunda `RWKV = RWKV_x070` atamasi yaparak RWKV-7'yi DOGRU tanıyan
# sinifi devreye sokuyor (self.n_head/self.head_size'i
# temp_z['blocks.0.att.r_k'].shape'ten dogru turetiyor). Bu degisken
# `rwkv.model` ilk import edildiginde OKUNUYOR (modul-seviyesi kod, bir
# kez calisir); bu yuzden en erken import edilen bu dosyada, herhangi
# bir `from rwkv...` cagrisindan once ayarlanmasi sarttir. Ayarlanmazsa
# paket sessizce ESKI (RWKV-7'yi TANIMAYAN v4/5/6) yukleyiciye duser ve
# ilk forward() cagrisinda 'args has no attribute n_head' hatasi verir.
os.environ.setdefault("RWKV_V7_ON", "1")

RWKV = "rwkv"
MAMBA = "mamba"
FALCON_MAMBA = "falcon_mamba"
# RWKV-7'ye "muvakkaten deneme" adayları (bkz. rwkv_alternatives_survey.md)
# -- ikisi de RWKV gibi HAM (yalnızca pretrain) değil, GERÇEK talimat/ajan
# ayarlı checkpoint'lerle geliyor, ve ikisi de standart `transformers`
# mimarisiyle uyumlu (RWKV'nin aksine `rwkv` pip paketi gibi özel bir
# yükleyiciye İHTİYAÇ DUYMuyorlar) -- bu yüzden aşağıdaki tüm generic
# `transformers`/`peft` yolu (ttt_lora.py, coz_yurutucu.py) MAMBA/
# FALCON_MAMBA ile AYNI ŞEKİLDE bu ikisi için de çalışır, ek kod gerekmez.
GRANITE4 = "granite4"
LFM25 = "lfm25"

# ==============================================================================
# YEREL DOSYA YOLLARI — internet KAPALI, model asla indirilmeyecek.
# Kaggle input dizinine yerel olarak eklenmis model klasorlerine isaret eder.
# ==============================================================================
YEREL_MODEL_YOLLARI: Dict[str, str] = {
    # model_indir.py ile indirilen HAM .pth kontrol noktası (transformers
    # config.json TAŞIMIYOR) — bkz. rwkv_native.py, ttt_lora.py bu dosya
    # yolunu görünce otomatik olarak `rwkv` pip paketiyle yükler.
    # NOT: bu yol yalnizca bir BASLANGIC tahminidir -- Kaggle her
    # yuklemede farkli bir ic klasor yapisi uretebiliyor. Bu yuzden
    # yerel_model_yolu(), bu yol GERCEKTE yoksa /kaggle/input altinda
    # ayni dosya adini ARAR (bkz. _kaggle_input_altinda_ara); asagidaki
    # deger sadece hicbir ortam degiskeni verilmemisse ilk denenecek yol.
    RWKV: "/kaggle/input/notebooks/ulankaggle/harici-llm/modeller/rwkv/rwkv7-g1i-7.2b-20260805-ctx16384.pth",
    MAMBA: "/kaggle/input/models/ulankaggle/mistral-mamba-codestral-7b-v0-1/transformers/default/1/Mamba-Codestral-7B-v0.1",
    FALCON_MAMBA: "/kaggle/input/falcon-mamba-7b-instruct/transformers/default/1",
    # NOT: bu iki yol yalnizca BASLANGIC TAHMINIDIR -- asagida verilen
    # indirme kodunun hangi klasor adini KULLANDIGINA gore Kaggle dataset
    # olusturulduktan sonra GERCEK yol degisebilir (bkz. yerel_model_yolu'nun
    # /kaggle/input altinda dosya adiyla ARAMA yaptigi mekanizma -- RWKV
    # icin de ayni sekilde calisir, sabit yol yanlissa otomatik bulunur).
    # Kullanıcının açık talebiyle GERÇEK yol -- granite-4.1-8b, DAHA ÖNCEKİ
    # granite-4-0-h-small tahmininin YERİNE (farklı model, farklı yol).
    GRANITE4: "/kaggle/input/notebooks/ulankaggle/indir-hbm/granite-4.1-8b",
    LFM25: "/kaggle/input/lfm2-5-2-6b/transformers/default/1",
}

# Ana model sirasi: Mamba, model_indir.py'nin indirme listesinden
# CIKARILDI (kullanici talebiyle) -- yedek olarak da denenmiyor, cunku
# offline calistirmada yerel dosyasi zaten bulunmayacak. Yalnizca RWKV.
# GRANITE4/LFM25 bu sıraya BİLEREK eklenmedi -- kullanıcı bunları AYRI
# notebook'larda, model_ailesi PARAMETRESİ AÇIKÇA VERİLEREK (RWKV'nin
# yedeğe düşme zincirine karışmadan, tek başına) çalıştıracak.
MODEL_ONCELIK_SIRASI: List[str] = [RWKV]

# ==============================================================================
# LoRA hedef modulleri (mimari basina)
# ==============================================================================
# NOT (DÜRÜSTLÜK PAYI): GRANITE4/LFM25 için aşağıdaki modül adları, bu
# oturumdaki araştırma raporunun (rwkv_alternatives_survey.md) anlattığı
# mimari BİLGİSİNDEN türetilmiş EN İYİ TAHMİNlerdir -- gerçek ağırlıklar bu
# ortamda indirilemediği için `print(model)` ile GERÇEK alt-modül adlarına
# karşı DOĞRULANAMADI. İlk pilot çalıştırmada mutlaka önce
# `print(model)` çıktısına bakıp, buradaki isimlerin gerçek modülle
# eşleştiğini teyit edin -- eşleşmezse peft sessizce SIFIR modülü
# adapte eder (hata vermez, LoRA etkisiz kalır), bu yüzden TTT'nin
# gerçekten kayıp azalttığını (gorev_ozelinde_ince_ayar'ın döndürdüğü
# kayıp geçmişinin GERÇEKTEN düştüğünü) ilk çalıştırmada MUTLAKA kontrol
# edin.
LORA_HEDEF_MODULLERI: Dict[str, List[str]] = {
    RWKV: ["key", "value", "receptance", "output", "gate"],
    MAMBA: ["in_proj", "out_proj", "x_proj", "dt_proj"],
    FALCON_MAMBA: ["in_proj", "out_proj", "x_proj", "dt_proj"],
    # DÜZELTME (kullanıcının IBM'in resmi mimari dokümantasyonunu
    # paylaşmasıyla DOĞRULANDI): granite-4.1-8b, ÖNCEKİ tahminin varsaydığı
    # gibi Granite 4.0 hibrit (Mamba-2 + azınlık transformer) DEĞİL --
    # standart YOĞUN (dense) decoder-only transformer (GQA + RoPE + SwiGLU
    # MLP + RMSNorm, HF transformers'taki Llama/Mistral tarzı klasik
    # mimariyle AYNI aile). Bu yüzden Mamba-2 LoRA olgunluğu endişesi
    # (aşağıdaki eski not) BU MODEL İÇİN GEÇERSİZ -- q/k/v/o_proj standart
    # GQA attention projeksiyon adlarıdır, HF'nin kendi Llama-tarzı
    # implementasyonlarında (Granite dahil) BİREBİR bu isimlerle geçer.
    # Yine de gerçek ağırlık bu ortamda `print(model)` ile GÖRÜLEMEDİĞİ
    # için ilk pilotta doğrulama önerisi (yukarıdaki genel not) geçerliliğini
    # korur.
    GRANITE4: ["q_proj", "k_proj", "v_proj", "o_proj"],
    # LFM2.5 (LIV: kısa evrişim + azınlık GQA attention): araştırma
    # raporunun bulduğu resmi Liquid TRL/leap-finetune dokümantasyonu, konvol-
    # üsyon (sabit-hafıza) katmanlarını da AÇIKÇA LoRA hedefi olarak
    # gösteriyordu -- bu yüzden burada hem attention hem konvolüsyon
    # projeksiyon adları tahmin edildi. Gerçek modül ağacı indirilip
    # `print(model)` ile görülünce KESİNLEŞTİRİLMELİ.
    LFM25: ["q_proj", "k_proj", "v_proj", "out_proj", "in_proj"],
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
# ==============================================================================
# DECODING (uretim parametreleri) ONERILERI — README'den birebir
# ==============================================================================
DECODING_ONERILERI: Dict[str, Dict[str, Dict[str, float]]] = {
    RWKV: {
        # Fonksiyon cagirma / agent: kullanici talebiyle temp=1.0 (gercek
        # ornekleme/sampling, do_sample=True) -- ONCEKI temp=0.0 (greedy/
        # argmax) tamamen DETERMINISTIKTI: rastgelelik SIFIRDI, bu yuzden
        # bir kez yozlasmis bir tekrar donguesune girdi mi hicbir sans
        # payi olmadan SONSUZA DEK o dongude kalirdi (kullanicinin gercek
        # Kaggle transkriptinde dogrudan gozlemlenen davranis). repetition_
        # penalty, ornekleme ACIKKEN de zaten uretilmis tokenlerin
        # olasiligini dusurup ayni tekrara SAPLANMAYI ayrica zorlastirir.
        "fonksiyon_cagirma": {"temp": 1.0, "top_p": 0.0, "penalty": 0.0, "repetition_penalty": 1.3},
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
    # GRANITE4/LFM25: RWKV'de temp=0.0 (tam greedy) yozlaşmış döngüye
    # yakalanınca SIFIR kaçış şansı bırakıyordu (bkz. gerçek Kaggle
    # transkripti) -- ikisi de zaten talimat-ayarlı, döngüye daha dirençli
    # olması BEKLENEN modeller olsa da, aynı dersle temkinli davranılıyor:
    # hafif örnekleme + repetition_penalty açık bırakıldı. İlk pilotta
    # gerçek döngü oranı ölçülüp gerekirse ayarlanmalı.
    GRANITE4: {
        "fonksiyon_cagirma": {"temp": 0.7, "top_p": 0.9, "penalty": 0.0, "repetition_penalty": 1.15},
        "sohbet": {"temp": 0.7, "top_p": 0.9, "penalty": 0.0},
    },
    LFM25: {
        "fonksiyon_cagirma": {"temp": 0.7, "top_p": 0.9, "penalty": 0.0, "repetition_penalty": 1.15},
        "sohbet": {"temp": 0.7, "top_p": 0.9, "penalty": 0.0},
    },
}

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


_ORTAM_DEGISKENI_ADLARI = {
    RWKV: "MUCIT_RWKV_YOLU",
    MAMBA: "MUCIT_MAMBA_YOLU",
    FALCON_MAMBA: "MUCIT_FALCON_MAMBA_YOLU",
    GRANITE4: "MUCIT_GRANITE4_YOLU",
    LFM25: "MUCIT_LFM25_YOLU",
}


def _kaggle_input_altinda_ara(dosya_adi: str, kok: str = "/kaggle/input", azami_derinlik: int = 8) -> Optional[str]:
    """Sabit-kodlanmis yol GERCEKTE diskte yoksa, ayni dosya adini
    /kaggle/input altinda TARAR. Kaggle'in her yuklemede farkli bir ic
    klasor yapisi (tek/cift 'modeller' ic ice gecmesi, zip'in nasil acildigi
    vb.) uretmesi -- ayni betigin farkli calistirmalarinda bile -- yol
    tahmininin kirilgan oldugunu gosterdi; bu yuzden sabit yol yerine
    GERCEK dosya sistemine bakan bir arama tercih edilir."""
    if not os.path.isdir(kok):
        return None
    kok_derinlik = kok.rstrip("/").count("/")
    for dizin_yolu, alt_dizinler, dosyalar in os.walk(kok):
        if dizin_yolu.count("/") - kok_derinlik > azami_derinlik:
            alt_dizinler[:] = []
            continue
        if dosya_adi in dosyalar:
            return os.path.join(dizin_yolu, dosya_adi)
    return None


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
        # Sabit-kodlanmis/ortam degiskenli yol yoksa, PES ETMEDEN ONCE
        # ayni dosya adini /kaggle/input altinda ara -- Kaggle'in her
        # yuklemede farkli klasor ic ice gecmesi uretmesi karsisinda tek
        # gercekten guvenilir yontem bu.
        dosya_adi = os.path.basename(yol.rstrip("/"))
        if dosya_adi:
            bulunan = _kaggle_input_altinda_ara(dosya_adi)
            if bulunan:
                print(
                    f"[model_yapilandirmalari] '{yol}' bulunamadı ama aynı dosya adı "
                    f"('{dosya_adi}') /kaggle/input altında farklı bir yolda bulundu ve "
                    f"kullanılıyor: {bulunan}"
                )
                return bulunan

        ebeveyn = os.path.dirname(yol.rstrip("/"))
        try:
            ebeveyn_icerigi = sorted(os.listdir(ebeveyn)) if os.path.isdir(ebeveyn) else None
        except OSError as e:
            ebeveyn_icerigi = [f"<listelenemedi: {e}>"]
        raise FileNotFoundError(
            f"'{model_ailesi}' modeli icin belirtilen yerel yol GERCEKTE diskte yok: '{yol}' "
            f"(ve /kaggle/input altında aynı dosya adıyla arama da sonuçsuz kaldı). "
            f"Ebeveyn dizin ('{ebeveyn}') icerigi: {ebeveyn_icerigi}. "
            f"Kaggle dataset/model eki notebook'a doğru şekilde bağlanmamış olabilir; "
            f"sağdaki 'Add Input' panelinden modelin gerçekten bu isimle eklendiğini "
            f"ve tam yolunu (üstteki listeden) doğrulayın, YEREL_MODEL_YOLLARI'nı buna göre düzeltin."
        )

    return yol
