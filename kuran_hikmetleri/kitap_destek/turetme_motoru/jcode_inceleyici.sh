#!/usr/bin/env bash
# Boru hattı inceleyicisi: tercüman bir bölümü bitirir bitirmez, boşta olan HER inceleyici onu alır (mkdir kilidiyle).
# Kullanım: jcode_inceleyici.sh <kök> <ad> <model>
set -u
export PATH="$HOME/.local/bin:$PATH"
KOK="$1"; AD="$2"; MODEL="$3"
DIR="$(cd "$(dirname "$0")/../../kelime_kaydi/osmanlica/kuranda_var/calisma/$KOK" && pwd)"
KILIT="/tmp/jcode_kilit"
cd "$DIR"
okuma="Önce $DIR/USUL.md dosyasını baştan sona oku (usul, biçim, görev ve durum protokolü). Sonra $DIR/KAYNAKLAR/ klasöründeki BÜTÜN dosyaları baştan sona oku; hüküm ve delil yalnız onlardan çıkar."
while true; do
  bitmedi=0; aldi=0
  for f in $(ls bolum_*.md | sort); do
    grep -q "^durum: inceleme-tamam" "$f" && continue
    bitmedi=1
    grep -q "^durum: tercume-tamam" "$f" || continue
    mkdir "$KILIT/$f" 2>/dev/null || continue
    aldi=1
    ek=""
    for tur in 1 2 3; do
      timeout 1500 jcode run --provider-profile ovh --model "$MODEL" --no-update "$ek Sen İNCELEYİCİ ajansın (adın $AD). $okuma Görevin: $DIR/$f bölüm dosyasını incelemek. Durumu 'inceleniyor' (inceleyen: $AD) yap; her satırın 'tercüme:' alanını oku, kaynaklarla karşılaştır ve USUL.md'deki inceleyici görevine göre DOĞRUDAN KAYNAĞINDA düzelt (yanlış gördüğünü yazıldığı yerde değiştir; 'tashih', 'itiraz' veya ⟨Tashih⟩ notu YAZMA), sebepleri en umumî sebebe çıkar, ilave sebepleri aynı tercümenin içine hâlin iktizasına göre uygun etiketlerle ekle; Arapça alıntıları kaynaktan harfi harfine doğrula; 'duz_tercume:' ve 'ilave:' alanlarına dokunma; dosyayı bütün hâliyle kaydet ve 'durum: inceleme-tamam' yap. Başka dosyaya dokunma." >> "../../log_${AD}_${f%.md}.txt" 2>&1
      hata=$(python3 "$(dirname "$0")/osmanlica_kapi.py" "$DIR" "$f") && break
      ek="KAPI GERİ ÇEVİRDİ (deneme $tur): $hata. Önce bunları düzelt, sonra bölümü bütün hâliyle yeniden kaydet ve durumu tamam yap. "
      sed -i "s/^durum: .*/durum: inceleniyor/" "$f"
    done
    python3 "$(dirname "$0")/osmanlica_kapi.py" "$DIR" "$f" >/dev/null || sed -i "s/^durum: .*/durum: kapi-gecmedi/" "$f"
    echo "$(date +%T) $AD: $f bitti"
    break
  done
  [ "$bitmedi" = 0 ] && break
  [ "$aldi" = 1 ] || sleep 10
done
