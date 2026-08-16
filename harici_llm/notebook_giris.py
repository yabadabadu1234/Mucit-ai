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

HARICI_LLM_KOKU = "/kaggle/working/Mucit-ai/harici_llm"
if HARICI_LLM_KOKU not in sys.path:
    sys.path.insert(0, HARICI_LLM_KOKU)

import torch
from gonderim_uret import coklu_gpu_submission_uret, submission_uret

SUBMISSION_YOLU = "/kaggle/working/submission.json"
COGALTMA_N = 16          # her bulmaca icin TTT'de kac augment ornegi uretilecek
TTT_ADIM_SAYISI = 20     # her bulmaca icin kac LoRA ince-ayar adimi atilacak
AZAMI_GPU = 4            # birden fazla GPU varsa: modelin GPU başına bağımsız kopyasıyla round-robin paralel çözüm (bkz. coklu_gpu.py)

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
    gpu_sayisi = torch.cuda.device_count() if torch.cuda.is_available() else 0
    print(f"[notebook_giris] CUDA erisilebilir mi: {torch.cuda.is_available()} (GPU sayısı: {gpu_sayisi})")
    print("[notebook_giris] Model: rwkv (RWKV-7 G1) — tek model, yedek yok")
    print(f"[notebook_giris] YARISMA={YARISMA}")

    if gpu_sayisi > 1:
        print(
            f"[notebook_giris] {gpu_sayisi} GPU tespit edildi -- modelin GPU başına BAĞIMSIZ bir kopyasıyla "
            f"round-robin (tek süreçten boru hattı, CPU-seviyesinde senkron bariyer YOK) paralel çözüm modu "
            f"kullanılıyor (bkz. coklu_gpu.py). NOT: bu yol salt-çıkarımdır, görev-başına TTT burada yok."
        )
        submission = coklu_gpu_submission_uret(
            cikti_yolu=SUBMISSION_YOLU, yarisma=YARISMA, azami_gpu=AZAMI_GPU,
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
