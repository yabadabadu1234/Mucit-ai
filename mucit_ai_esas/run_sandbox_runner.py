

import os
import sys
import json
import logging

logging.basicConfig(level=logging.INFO, format='[%(asctime)s][%(name)s][%(levelname)s] %(message)s')
logger = logging.getLogger('SandboxRunner')


try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    BASE_DIR = os.path.abspath(os.getcwd())
for path in [BASE_DIR, os.path.join(BASE_DIR, "mucit_ai"), os.path.join(BASE_DIR, "kulli_gpu"), os.path.join(BASE_DIR, "cpp_driver")]:
    if os.path.exists(path) and path not in sys.path:
        sys.path.insert(0, path)

MANIFEST_PATH = os.path.join(BASE_DIR, "verisetleri_manifest.json")
SAMPLE_DATASET_DIR = os.path.join(BASE_DIR, "sample_dataset")


def manifest_olustur():
    manifest_data = {
        "verisetleri": [
            SAMPLE_DATASET_DIR
        ],
        "olusturulma_zamani": "local_sandbox"
    }
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2, ensure_ascii=False)
    logger.info(f"Yerel veri kümeleri manifest dosyası kaydedildi: {MANIFEST_PATH}")


if __name__ == "__main__":
    logger.info("================================================================================")
    logger.info("YEREL SANDBOX BİLİŞSEL KANVAS TOPOLOJİK REKÜRENS EĞİTİMİ BAŞLATILIYOR")
    logger.info("================================================================================")

    
    manifest_olustur()

    
    try:
        import kulli_gpu
    except (ImportError, ModuleNotFoundError):
        if BASE_DIR not in sys.path:
            sys.path.insert(0, BASE_DIR)
        import kulli_gpu
    driver = kulli_gpu.baslat()
    logger.info("[Külli_GPU Driver] Sanal Sürücü Başarıyla Başlatıldı.")

    
    from main_egitim_dongusu import Main_EgitimYurutucu

    Main_EgitimYurutucu(manifest_yolu=MANIFEST_PATH)
