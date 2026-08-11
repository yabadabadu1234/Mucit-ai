#!/usr/bin/env bash
set -euo pipefail

KAGGLE_DATASET_SLUG="${KAGGLE_DATASET_SLUG:-ulankaggle/mucid-i-dahi}"
KAGGLE_KERNEL_SLUG="${KAGGLE_KERNEL_SLUG:-ulankaggle/mucit-ai-egitim}"
GITHUB_REPO="${GITHUB_REPO:-https://github.com/yabadabadu1234/Mucit-ai.git}"
GITHUB_BRANCH="${GITHUB_BRANCH:-claude/logits-device-mismatch-f4a9uk}"
WORKDIR="$(mktemp -d)"
KERNEL_TITLE="Mucit AI Egitim Otomatik Kosu"

echo "== 1/5 GitHub'dan en guncel kod cekiliyor =="
git clone --depth 1 --branch "$GITHUB_BRANCH" "$GITHUB_REPO" "$WORKDIR/repo"

echo "== 2/5 Kaggle dataset guncelleniyor: $KAGGLE_DATASET_SLUG =="
DATASET_DIR="$WORKDIR/dataset_upload"
mkdir -p "$DATASET_DIR"
cp -r "$WORKDIR/repo/mucit_ai_esas" "$DATASET_DIR/"
cat > "$DATASET_DIR/dataset-metadata.json" <<EOF
{
  "title": "mucid-i-dahi",
  "id": "$KAGGLE_DATASET_SLUG",
  "licenses": [{"name": "CC0-1.0"}]
}
EOF
kaggle datasets version -p "$DATASET_DIR" -m "otomatik guncelleme $(date -u +%Y-%m-%dT%H:%M:%SZ)" -r zip

echo "== 3/5 Kernel dosyasi hazirlaniyor =="
KERNEL_DIR="$WORKDIR/kernel_upload"
mkdir -p "$KERNEL_DIR"
cp "$WORKDIR/repo/local_run/entry.py" "$KERNEL_DIR/kaggle_entry.py" 2>/dev/null || true
cat > "$KERNEL_DIR/kaggle_entry.py" <<'PYEOF'
import os
import sys
import json
import logging

logging.basicConfig(level=logging.INFO, format='[%(asctime)s][%(name)s][%(levelname)s] %(message)s', stream=sys.stdout)
logger = logging.getLogger('KaggleMasterRunner')

def setup_kaggle_sys_path():
    candidate_paths = []
    if os.path.exists("/kaggle/input"):
        for root, dirs, files in os.walk("/kaggle/input"):
            if "kontratlar.py" in files or "kulli_gpu" in dirs:
                candidate_paths.append(root)
    for path in candidate_paths:
        if path not in sys.path:
            sys.path.insert(0, path)
            logger.info(f"Modul arama yoluna eklendi: {path}")

setup_kaggle_sys_path()

VERISETLERI_LISTESI = [
    "/kaggle/input/datasets/thedevastator/ai4math-mathematical-qa-dataset",
    "/kaggle/input/datasets/nazmuddhohaansary/islamweb-fatwas",
    "/kaggle/input/datasets/alizahidraja/quran-nlp",
    "/kaggle/input/datasets/yousefabuz17/islamic-data",
    "/kaggle/input/datasets/organizations/Cornell-University/arxiv",
]

MANIFEST_PATH = "/kaggle/working/verisetleri_manifest.json"

def manifest_olustur():
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump({"verisetleri": VERISETLERI_LISTESI}, f, indent=2, ensure_ascii=False)
    logger.info(f"Manifest kaydedildi: {MANIFEST_PATH}")

if __name__ == "__main__":
    manifest_olustur()
    from main_egitim_dongusu import Main_EgitimYurutucu
    Main_EgitimYurutucu(manifest_yolu=MANIFEST_PATH)
    from kulli_gpu.nvme_takas_yoneticisi import NvmeTakasYoneticisi
    NvmeTakasYoneticisi().temizle()
    logger.info("MUCIT AI EGITIMI TAMAMLANDI")
PYEOF

cat > "$KERNEL_DIR/kernel-metadata.json" <<EOF
{
  "id": "$KAGGLE_KERNEL_SLUG",
  "title": "$KERNEL_TITLE",
  "code_file": "kaggle_entry.py",
  "language": "python",
  "kernel_type": "script",
  "is_private": true,
  "enable_gpu": true,
  "enable_internet": true,
  "dataset_sources": ["$KAGGLE_DATASET_SLUG"],
  "competition_sources": [],
  "kernel_sources": []
}
EOF

echo "== 4/5 Kernel push ediliyor ve GPU'da calistiriliyor =="
kaggle kernels push -p "$KERNEL_DIR"

echo "== 5/5 Calisma bitene kadar bekleniyor =="
while true; do
  STATUS=$(kaggle kernels status "$KAGGLE_KERNEL_SLUG" | grep -oP '"\K[a-zA-Z]+(?=")' | head -1 || echo "unknown")
  echo "durum: $STATUS"
  if [[ "$STATUS" == "complete" || "$STATUS" == "error" ]]; then
    break
  fi
  sleep 30
done

echo "== Log indiriliyor =="
OUT_DIR="$WORKDIR/output"
kaggle kernels output "$KAGGLE_KERNEL_SLUG" -p "$OUT_DIR"
LOG_FILE=$(find "$OUT_DIR" -iname "*.log" | head -1)
if [[ -n "$LOG_FILE" ]]; then
  echo "== LOG: $LOG_FILE =="
  cat "$LOG_FILE"
else
  echo "== log dosyasi bulunamadi, tum kernel ciktisi $OUT_DIR altinda =="
  ls -la "$OUT_DIR"
fi

echo "Klasor: $WORKDIR"
