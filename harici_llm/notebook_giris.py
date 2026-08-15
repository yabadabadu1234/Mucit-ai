"""
Kaggle notebook giris hucresi.

Ana model: RWKV-7 G1
  /kaggle/input/models/ulankaggle/rwkv-7/transformers/default/1/rwkv7-g1
Yedek model: Mamba-Codestral-7B-v0.1
  /kaggle/input/models/ulankaggle/mistral-mamba-codestral-7b-v0-1/transformers/default/1/Mamba-Codestral-7B-v0.1

Bu hucre ana modeli yuklemeyi dener; dosya eksik/bozuksa, mimari
desteklenmiyorsa ya da VRAM yetmiyorsa OTOMATIK olarak yedek modele duser.
Internet KAPALI oldugundan iki model de yalnizca yukaridaki yerel Kaggle
input yollarindan okunur, hicbir model indirilmez.
"""
import os
import sys

HARICI_LLM_KOKU = "/kaggle/working/Mucit-ai/harici_llm"
if HARICI_LLM_KOKU not in sys.path:
    sys.path.insert(0, HARICI_LLM_KOKU)

# arac-cagirma ve TTT icin gerekli paketler (internetsiz ortamda onceden
# kurulu olmalari beklenir; Kaggle "Add-ons > Internet" KAPALI kalmalidir).
import torch
from gonderim_uret import submission_uret

SUBMISSION_YOLU = "/kaggle/working/submission.json"
COGALTMA_N = 16          # her bulmaca icin TTT'de kac augment ornegi uretilecek
TTT_ADIM_SAYISI = 20     # her bulmaca icin kac LoRA ince-ayar adimi atilacak

if __name__ == "__main__":
    print(f"[notebook_giris] CUDA erisilebilir mi: {torch.cuda.is_available()}")
    print("[notebook_giris] Ana model: rwkv (RWKV-7 G1) | Yedek model: mamba (Mamba-Codestral-7B-v0.1)")

    submission = submission_uret(
        model_ailesi=None,  # None -> once ana modeli (rwkv) dener, olmazsa yedege (mamba) duser
        cikti_yolu=SUBMISSION_YOLU,
        cogaltma_n=COGALTMA_N,
        ttt_adim_sayisi=TTT_ADIM_SAYISI,
    )

    print(f"[notebook_giris] Bitti. {len(submission)} görev için {SUBMISSION_YOLU} yazıldı.")
