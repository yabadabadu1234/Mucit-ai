"""
Kaggle notebook giris hucresi.

Ana model: RWKV-7 G1 (tek model -- Mamba yedeği indirme listesinden çıkarıldı)
  yol: MUCIT_RWKV_YOLU ortam değişkeni veya model_yapilandirmalari.YEREL_MODEL_YOLLARI

Internet KAPALI olduğundan model yalnızca yerel Kaggle input yolundan
okunur, hiçbir model indirilmez.
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
    "/kaggle/input/notebooks/ulankaggle/harici-llm/modeller/paketler",
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
        f"'rwkv' zaten kurulu değilse RWKV yükleme başarısız olur (yedek model yok, çalıştırma durur). "
        f"model_indir.py'yi internet açıkken çalıştırıp bu klasörü de girdi olarak eklediğinizden emin olun."
    )

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
