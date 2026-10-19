#!/bin/sh
# A3 PDF birleştirici. Kullanım: sh a3_birlestir.sh [sayfa_klasörü] [çıktı.pdf]
# Her çalıştırmada eski A3 sayfaları silinir ve PDF üzerine yazılır.
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
GIRIS="$(cd "${1:-$DIR/sayfalar}" && pwd)"
CIKTI="$(cd "$(dirname "${2:-$DIR/../kuran_hikmetleri_a3.pdf}")" && pwd)/$(basename "${2:-$DIR/../kuran_hikmetleri_a3.pdf}")"
ARA="$DIR/sayfalar_a3"
rm -rf "$ARA" && mkdir -p "$ARA"
for f in "$GIRIS"/p*.png; do
  convert "$f" -background white -gravity north -extent 2246x3175 "$ARA/$(basename "$f")"
done
rm -f "$CIKTI"
convert "$ARA"/p*.png -units PixelsPerInch -density 192 "$CIKTI"
rm -rf "$ARA"
echo "PDF: $CIKTI"
