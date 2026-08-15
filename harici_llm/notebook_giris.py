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
import subprocess
import sys

HARICI_LLM_KOKU = "/kaggle/working/Mucit-ai/harici_llm"
if HARICI_LLM_KOKU not in sys.path:
    sys.path.insert(0, HARICI_LLM_KOKU)

# `rwkv` pip paketi PyPI'de var ama internet KAPALI oldugundan normal
# `pip install rwkv` calismaz. model_indir.py'nin internet-acik
# calistirmada `pip download` ile indirdigi wheel'leri, buradaki yerel
# klasorden --no-index ile (aga hic dokunmadan) kuruyoruz. Klasor yolu,
# ikinci calistirmada Kaggle'in verdigi gercek input yoluna gore
# MUCIT_PAKETLER_YOLU ortam degiskeniyle degistirilebilir.
PAKETLER_YOLU = os.environ.get(
    "MUCIT_PAKETLER_YOLU",
    "/kaggle/input/notebooks/ulankaggle/harici-llm/paketler",
)
if os.path.isdir(PAKETLER_YOLU):
    print(f"[notebook_giris] pip paketleri yerel klasörden (internetsiz) kuruluyor: {PAKETLER_YOLU}")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--no-index", "--find-links", PAKETLER_YOLU, "rwkv"],
        check=True,
    )
else:
    print(
        f"[notebook_giris] UYARI: pip paket klasörü bulunamadı: {PAKETLER_YOLU}. "
        f"'rwkv' zaten kurulu değilse RWKV yükleme başarısız olur (Mamba yedeğe düşülür). "
        f"model_indir.py'yi internet açıkken çalıştırıp bu klasörü de girdi olarak eklediğinizden emin olun."
    )

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
