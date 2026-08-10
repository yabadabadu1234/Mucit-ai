#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
YEREL SANDBOX EĞİTİM VE SÜREKLİ HİYERARŞİK CHECKPOINT RUNNER
(run_sandbox_runner.py)
================================================================================
Bu betik; yerel sandbox ortamında çalıştırıldığında eğitilecek yerel test veriseti
yollarını './verisetleri_manifest.json' dosyası olarak kaydeder.

Ardından 'kulli_gpu' sanal sürücüsünü başlatır ve 'main_egitim_dongusu.py'
modülündeki 'Main_EgitimYurutucu' sürecini başlatır.
================================================================================
"""

import os
import sys
import json
import logging

logging.basicConfig(level=logging.INFO, format='[%(asctime)s][%(name)s][%(levelname)s] %(message)s')
logger = logging.getLogger('SandboxRunner')

# 1. Dizin Yollarını sys.path'e Ekle
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
    """Yerel çalışma dizininde verisetleri_manifest.json dosyasını yazar."""
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

    # 1. Manifest Dosyasını Yaz
    manifest_olustur()

    # 2. Küllî GPU Sanal Sürücüsünü Başlat
    try:
        import kulli_gpu
    except (ImportError, ModuleNotFoundError):
        if BASE_DIR not in sys.path:
            sys.path.insert(0, BASE_DIR)
        import kulli_gpu
    driver = kulli_gpu.baslat()
    logger.info("[Külli_GPU Driver] Sanal Sürücü Başarıyla Başlatıldı.")

    # 3. Ana Eğitim Yürütücüsünü Çağır
    from main_egitim_dongusu import Main_EgitimYurutucu

    Main_EgitimYurutucu(manifest_yolu=MANIFEST_PATH)
