#!/usr/bin/env bash
# Boru hattı tercümanı: boşta olan her tercüman, henüz kimsenin almadığı 'bos' bölümü mkdir kilidiyle alır.
# Kullanım: jcode_tercuman.sh <kök> <ad> <model>
set -u
export PATH="$HOME/.local/bin:$PATH"
KOK="$1"; AD="$2"; MODEL="$3"
DIR="$(cd "$(dirname "$0")/../../kelime_kaydi/osmanlica/kuranda_var/calisma/$KOK" && pwd)"
KILIT="/tmp/jcode_kilit_t"
cd "$DIR"
okuma="Önce $DIR/USUL.md dosyasını baştan sona oku (usul, biçim, görev ve durum protokolü). Sonra $DIR/KAYNAKLAR/ klasöründeki BÜTÜN dosyaları baştan sona oku; hüküm ve delil yalnız onlardan çıkar."
for f in $(ls bolum_*.md | sort); do
  grep -q "^durum: bos" "$f" || continue
  mkdir "$KILIT/$f" 2>/dev/null || continue
  timeout 1500 jcode run --provider-profile ovh --model "$MODEL" --no-update "Sen TERCÜMAN ajansın (adın $AD). $okuma Görevin: $DIR/$f bölüm dosyasını işlemek. Dosyayı oku; durumu 'tercume-yapiliyor' (tercume_eden: $AD) yap; her satırın hazır 'duz_tercume:' değerini esas alıp (dokunmadan) 'tercüme:' alanını USUL.md'deki ŞERHLİ TERCÜME biçimiyle (kısa Osmanlıca tercüme + hâlin iktizasına göre gerekli etiketli şerh kısımları; etiketlerin sırası ve sayısı serbest; her sebep en umumî sebebe çıkarılmış; Arapça alıntılar kaynaktan harfi harfine) tek satırda doldur; dosyayı bütün hâliyle kaydet ve 'durum: tercume-tamam' yap. Başlık, '---', '##', 'arapça:', 'bilgi:', 'duz_tercume:' ve 'ilave:' alanlarına dokunma; başka dosyaya dokunma; hiçbir satırı boş bırakma." > "../../log_${AD}_${f%.md}.txt" 2>&1
  echo "$(date +%T) $AD: $f bitti"
done
