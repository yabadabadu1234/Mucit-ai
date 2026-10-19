#!/bin/sh
# A3 PDF birleştirici. Kullanım: sh a3_birlestir.sh [sayfa_klasörü] [çıktı.pdf]
# Her çalıştırmada eski A3 sayfaları silinir ve PDF üzerine yazılır.
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
export MAGICK_TEMPORARY_PATH="$DIR/.magick_tmp"
mkdir -p "$MAGICK_TEMPORARY_PATH"
GIRIS="$(cd "${1:-$DIR/sayfalar}" && pwd)"
CIKTI="$(cd "$(dirname "${2:-$DIR/../kuran_hikmetleri_a3.pdf}")" && pwd)/$(basename "${2:-$DIR/../kuran_hikmetleri_a3.pdf}")"
ARA="$DIR/sayfalar_a3"
rm -rf "$ARA" && mkdir -p "$ARA"
for f in "$GIRIS"/p*.jpg "$GIRIS"/p*.png; do [ -e "$f" ] || continue
  convert -limit memory 2GiB -limit map 4GiB -limit disk 40GiB "$f" -background white -gravity north -extent 2246x3175 "$ARA/$(basename "$f")"
done
rm -f "$CIKTI"
convert -limit memory 2GiB -limit map 4GiB -limit disk 40GiB "$ARA"/p* -units PixelsPerInch -density 192 "$CIKTI"
rm -rf "$ARA" "$MAGICK_TEMPORARY_PATH"
echo "PDF: $CIKTI"
