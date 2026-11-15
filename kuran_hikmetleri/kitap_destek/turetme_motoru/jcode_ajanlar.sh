#!/usr/bin/env bash
# Kullanım: jcode_ajanlar.sh <kök> tercuman <model> | inceleyici <ad> <model> <mod> <kalan>
# Ajanlar jcode ile OVH AI Endpoints (anahtarsız) üzerinde çalışır; dosya düzenleme araçlarıyla çalışma klasöründeki bölümleri doldurur.
set -u
export PATH="$HOME/.local/bin:$PATH"
KOK="$1"; ROL="$2"
DIR="$(cd "$(dirname "$0")/../../kelime_kaydi/osmanlica/kuranda_var/calisma/$KOK" && pwd)"
cd "$DIR"
okuma="Önce $DIR/USUL.md dosyasını baştan sona oku (usul, biçim, görev ve durum protokolü). Sonra $DIR/KAYNAKLAR/ klasöründeki BÜTÜN dosyaları baştan sona oku; hüküm ve delil yalnız onlardan çıkar."
if [ "$ROL" = "tercuman" ]; then
  MODEL="$3"
  for f in $(ls bolum_*.md | sort); do
    grep -q "^durum: bos" "$f" || continue
    timeout 1500 jcode run --provider-profile ovh --model "$MODEL" --no-update "Sen TERCÜMAN ajansın. $okuma Görevin: $DIR/$f bölüm dosyasını işlemek. Dosyayı oku; durumu 'tercume-yapiliyor' (tercume_eden: tercüman) yap; her satırın hazır 'duz_tercume:' değerini esas alıp (dokunmadan) 'tercüme:' alanını USUL.md'deki ŞERHLİ TERCÜME biçimiyle (kısa Osmanlıca tercüme + ⟨Ne⟩ ⟨Nasıl⟩ ⟨Neden⟩ ⟨Neden 2⟩… ⟨Esas⟩ ⟨Niçin⟩) tek satırda doldur; dosyayı bütün hâliyle kaydet ve 'durum: tercume-tamam' yap. Başlık, '---', '##', 'arapça:', 'bilgi:' ve 'ilave:' alanlarına dokunma; başka dosyaya dokunma; hiçbir satırı boş bırakma." > "../../log_tercuman_${f%.md}.txt" 2>&1
    echo "$(date +%T) tercüman: $f bitti"
  done
else
  AD="$2"; MODEL="$3"; MOD="$4"; KALAN="$5"
  for f in $(ls bolum_*.md | sort); do
    n=$(echo "$f" | sed -E 's/bolum_([0-9]+)_.*/\1/'); n=$((10#$n))
    [ $((n % MOD)) -eq "$KALAN" ] || continue
    while ! grep -q "^durum: tercume-tamam" "$f"; do
      grep -q "^durum: inceleme-tamam" "$f" && continue 2
      sleep 20
    done
    timeout 1500 jcode run --provider-profile ovh --model "$MODEL" --no-update "Sen İNCELEYİCİ ajansın (adın $AD). $okuma Görevin: $DIR/$f bölüm dosyasını incelemek. Durumu 'inceleniyor' (inceleyen: $AD) yap; her satırın 'tercüme:' alanını oku, kaynaklarla karşılaştır ve USUL.md'deki inceleyici görevine göre DOĞRUDAN KAYNAĞINDA düzelt (yanlış gördüğünü yazıldığı yerde değiştir; 'tashih', 'itiraz' veya ⟨Tashih⟩ notu YAZMA) ve ilave sebepleri aynı tercümenin içine, etiket sırasını bozmadan ekle; 'duz_tercume:' ve 'ilave:' alanlarına dokunma; dosyayı bütün hâliyle kaydet ve 'durum: inceleme-tamam' yap. Başka dosyaya dokunma." > "../../log_${AD}_${f%.md}.txt" 2>&1
    echo "$(date +%T) $AD: $f bitti"
  done
fi
