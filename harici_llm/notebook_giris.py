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
from gonderim_uret import submission_uret

SUBMISSION_YOLU = "/kaggle/working/submission.json"
COGALTMA_N = 16          # her bulmaca icin TTT'de kac augment ornegi uretilecek
TTT_ADIM_SAYISI = 20     # her bulmaca icin kac LoRA ince-ayar adimi atilacak

if __name__ == "__main__":
    print(f"[notebook_giris] CUDA erisilebilir mi: {torch.cuda.is_available()}")
    print("[notebook_giris] Model: rwkv (RWKV-7 G1) — tek model, yedek yok")

    submission = submission_uret(
        model_ailesi=None,  # None -> MODEL_ONCELIK_SIRASI'ndaki (yalnızca rwkv) modeli dener
        cikti_yolu=SUBMISSION_YOLU,
        cogaltma_n=COGALTMA_N,
        ttt_adim_sayisi=TTT_ADIM_SAYISI,
    )

    print(f"[notebook_giris] Bitti. {len(submission)} görev için {SUBMISSION_YOLU} yazıldı.")
