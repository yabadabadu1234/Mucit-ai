"""
Kaggle notebook giris hucresi.

Ana model: RWKV-7 G1 (tek model -- Mamba yedeği indirme listesinden çıkarıldı)
  yol: MUCIT_RWKV_YOLU ortam değişkeni veya model_yapilandirmalari.YEREL_MODEL_YOLLARI

Internet KAPALI olduğundan model yalnızca yerel Kaggle input yolundan
okunur, hiçbir model indirilmez.

Gerekli pip paketleri (rwkv, peft, ninja...) artık bu dosya TARAFINDAN
KURULMUYOR — Kaggle notebook'unun "Install dependencies" bölümüne
eklenmeleri gerekir (bkz. model_indir.py başındaki liste); o bölüm
notebook kodu çalışmadan önce, internet açık/kapalı fark etmeksizin
kurulum yapar.
"""
import sys

# NOT: bu yol, reponun Kaggle'da NEREYE mount edildiğine göre değişir --
# "/kaggle/working/Mucit-ai/harici_llm" (bir hücrede git clone edildiyse)
# ya da "/kaggle/input/datasets/<kullanici>/<dataset-adi>/<repo>/harici_llm"
# (bir Kaggle Dataset olarak eklendiyse) olabilir. Kendi ortamınıza göre
# TEK satırı güncelleyin; kod bu yol dışında hiçbir şeye dokunmaz.
HARICI_LLM_KOKU = "/kaggle/working/Mucit-ai/harici_llm"
if HARICI_LLM_KOKU not in sys.path:
    sys.path.insert(0, HARICI_LLM_KOKU)

import torch
from gonderim_uret import coklu_gpu_submission_uret, submission_uret
from gpu_tespit import kullanilabilir_gpu_indeksleri

SUBMISSION_YOLU = "/kaggle/working/submission.json"
COGALTMA_N = 16          # her bulmaca icin TTT'de kac augment ornegi uretilecek
TTT_ADIM_SAYISI = 20     # her bulmaca icin kac LoRA ince-ayar adimi atilacak
AZAMI_GPU = 4            # birden fazla GPU varsa: modelin GPU başına bağımsız kopyasıyla round-robin paralel çözüm (bkz. coklu_gpu.py)
B_BOYUTU = 128           # her GPU'nun AYNI ANDA (tek batched adım zinciriyle) bakacağı görev sayısı için BAŞLANGIÇ tahmini -- gerçek değer vram_izleyici ile çalışma sırasında otomatik ayarlanır

# YARISMA=True  -> gercek yarisma test kumesi (arc-agi_test_challenges.json),
#                  cevaplar bilinmiyor, submission.json yarismaya gonderilir.
# YARISMA=False -> DENEME modu: cevaplari BILINEN degerlendirme kumesi
#                  (arc-agi_evaluation_challenges.json + _solutions.json)
#                  kullanilir; coz_yurutucu'nun cozdugu HER gorevden hemen
#                  sonra dogru mu yanlis mi oldugu VE submit_answer'in
#                  gercekten basariyla cagrilip cagrilmadigi (bos yer
#                  tutucuya dusup dusmedigi) hem konsola hem
#                  konusma_transkriptleri.jsonl'e loglanir.
YARISMA = True

if __name__ == "__main__":
    gorulen_gpu_sayisi = torch.cuda.device_count() if torch.cuda.is_available() else 0
    print(f"[notebook_giris] torch.cuda.is_available()={torch.cuda.is_available()} , torch.cuda.device_count()={gorulen_gpu_sayisi}")
    print("[notebook_giris] Model: rwkv (RWKV-7 G1) — tek model, yedek yok")
    print(f"[notebook_giris] YARISMA={YARISMA}")

    # ÖNEMLİ: torch.cuda.device_count()/is_available() yalnızca GPU'nun
    # GÖRÜNDÜĞÜNÜ söyler, GERÇEKTEN kullanılabildiğini DEĞİL (Kaggle'da
    # görünüp arka planda erişilemeyen/donan GPU'lar yaşandı). Bu yüzden
    # karar, HER cihazda GERÇEK bir matmul çalıştıran izole bir alt-süreç
    # sınamasından (gpu_tespit.kullanilabilir_gpu_indeksleri) geçer.
    gercek_gpu_indeksleri = kullanilabilir_gpu_indeksleri(azami_gpu=AZAMI_GPU) if gorulen_gpu_sayisi > 0 else []
    print(f"[notebook_giris] Derin sınamadan GEÇEN GPU sayısı: {len(gercek_gpu_indeksleri)} (indeksler: {gercek_gpu_indeksleri})")

    if len(gercek_gpu_indeksleri) >= 1:
        print(
            f"[notebook_giris] {len(gercek_gpu_indeksleri)} GERÇEKTEN kullanılabilir GPU -- her GPU, kendisine "
            f"düşen görevleri TEK TEK değil, B TANESİNİ (VRAM ölçümüyle otomatik keşfedilen güvenli B, bkz. "
            f"vram_izleyici.py, başlangıç tahmini B_BOYUTU={B_BOYUTU}) AYNI ANDA, TEK bir batched adım zinciriyle "
            f"çözüyor (bkz. coklu_gpu.CokluGPUTopluCozucu / coz_yurutucu_toplu.toplu_gorevleri_coz). NOT: bu yol "
            f"salt-çıkarımdır, görev-başına TTT burada yok."
        )
        submission = coklu_gpu_submission_uret(
            cikti_yolu=SUBMISSION_YOLU, yarisma=YARISMA, azami_gpu=AZAMI_GPU, b_boyutu=B_BOYUTU,
        )
    else:
        submission = submission_uret(
            model_ailesi=None,  # None -> MODEL_ONCELIK_SIRASI'ndaki (yalnızca rwkv) modeli dener
            cikti_yolu=SUBMISSION_YOLU,
            cogaltma_n=COGALTMA_N,
            ttt_adim_sayisi=TTT_ADIM_SAYISI,
            yarisma=YARISMA,
        )

    print(f"[notebook_giris] Bitti. {len(submission)} görev için {SUBMISSION_YOLU} yazıldı.")
