#!/bin/sh
# A3 PDF birleştirici. Kullanım: sh a3_birlestir.sh [sayfa_klasörü] [çıktı.pdf]
# Sayfalar JPEG olarak beklenir. Her çalıştırmada PDF üzerine yazılır.
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
GIRIS="$(cd "${1:-$DIR/sayfalar}" && pwd)"
CIKTI="$(cd "$(dirname "${2:-$DIR/../kuran_hikmetleri_a3.pdf}")" && pwd)/$(basename "${2:-$DIR/../kuran_hikmetleri_a3.pdf}")"
rm -f "$CIKTI"
python3 "$DIR/a3_pdf_yaz.py" "$GIRIS" "$CIKTI"
