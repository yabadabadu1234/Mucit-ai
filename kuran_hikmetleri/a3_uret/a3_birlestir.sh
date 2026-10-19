#!/bin/sh
# Ön koşul: a3_render.js çalıştırılmış ve PNG'ler a3_uret/sayfalar/ içinde olmalı.
# Kullanım: sh a3_uret/a3_birlestir.sh [çıktı.pdf]
set -e
cd "$(dirname "$0")"
CIKTI="${1:-../kuran_hikmetleri_a3.pdf}"
mkdir -p sayfalar_a3
for f in sayfalar/p*.png; do
  convert "$f" -background white -gravity north -extent 2246x3175 "sayfalar_a3/$(basename "$f")"
done
convert sayfalar_a3/p*.png -units PixelsPerInch -density 192 "$CIKTI"
echo "PDF: $CIKTI"
