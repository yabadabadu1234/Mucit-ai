import os
import sys
import json
import logging

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s][%(name)s][%(levelname)s] %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger('LocalRunner')

MUCIT_ROOT = "/home/user/Mucit-ai/mucit_ai_esas"
for p in [MUCIT_ROOT, os.path.join(MUCIT_ROOT, "mucit_ai"), os.path.join(MUCIT_ROOT, "kulli_gpu")]:
    if p not in sys.path:
        sys.path.insert(0, p)

VERISETLERI_LISTESI = [
    "/home/user/Mucit-ai/local_run/kendi_egitim_metni.txt",
    "/tmp/char-rnn-test/data/tinyshakespeare",
]

MANIFEST_PATH = "/home/user/Mucit-ai/local_run/verisetleri_manifest.json"
CONFIG_PATH = "/home/user/Mucit-ai/local_run/config.json"
CKPT_DIR = "/home/user/Mucit-ai/local_run/checkpoints"

def manifest_olustur():
    manifest_data = {"verisetleri": VERISETLERI_LISTESI}
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2, ensure_ascii=False)
    logger.info(f"Manifest dosyasi kaydedildi: {MANIFEST_PATH}")

if __name__ == "__main__":
    logger.info("MUCIT AI YEREL DUZ CALISMA (CPU) BASLATILIYOR")
    os.makedirs(CKPT_DIR, exist_ok=True)
    manifest_olustur()

    from main_egitim_dongusu import Main_EgitimYurutucu
    Main_EgitimYurutucu(konfig_yolu=CONFIG_PATH, manifest_yolu=MANIFEST_PATH)

    logger.info("MUCIT AI YEREL EGITIMI TAMAMLANDI")
