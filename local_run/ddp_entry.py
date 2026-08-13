import json
import os
import sys

MUCIT_ROOT = os.environ.get("MUCIT_ROOT", "/kaggle/working/Mucit-ai/mucit_ai_esas")
for p in [MUCIT_ROOT, os.path.join(MUCIT_ROOT, "mucit_ai"), os.path.join(MUCIT_ROOT, "kulli_gpu")]:
    if p not in sys.path:
        sys.path.insert(0, p)

CONFIG_PATH = os.environ.get("MUCIT_CONFIG", "/kaggle/working/config.json")
MANIFEST_PATH = os.environ.get("MUCIT_MANIFEST", "/kaggle/working/verisetleri_manifest.json")
DUNYA_BOYUTU = int(os.environ.get("MUCIT_DUNYA", "4"))

def rank_egitimi(yerel_rank: int, dunya: int) -> None:
    import torch
    import dagitik_egitim

    cihaz = dagitik_egitim.dagitik_kur(yerel_rank, dunya)

    import main_egitim_dongusu as M

    M.SESSIZ_URETIM_MODU = True
    M.kur_logging_sistemi(yerel_rank=yerel_rank)

    try:
        M.Main_EgitimYurutucu(
            konfig_yolu=CONFIG_PATH,
            manifest_yolu=MANIFEST_PATH,
            zorunlu_cihaz=str(cihaz),
        )
    finally:
        dagitik_egitim.dagitik_kapat()

if __name__ == "__main__":
    import torch

    if not torch.cuda.is_available():
        raise SystemExit("CUDA yok; ddp_entry.py yalnizca cok GPU'lu makinede calisir.")

    gorunen = torch.cuda.device_count()
    if gorunen < DUNYA_BOYUTU:
        raise SystemExit(
            f"MUCIT_DUNYA={DUNYA_BOYUTU} istendi fakat {gorunen} GPU gorunuyor. "
            f"MUCIT_DUNYA={gorunen} ile calistirin."
        )

    print(f"[DDP] {DUNYA_BOYUTU} surec baslatiliyor, her rank icin bir GPU.")
    torch.multiprocessing.spawn(rank_egitimi, args=(DUNYA_BOYUTU,), nprocs=DUNYA_BOYUTU, join=True)
