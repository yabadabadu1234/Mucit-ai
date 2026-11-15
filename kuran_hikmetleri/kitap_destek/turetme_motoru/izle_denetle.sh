#!/usr/bin/env bash
# Bir bölüm 'tercume-tamam' veya 'inceleme-tamam' durumunda KALIP kapıdan da geçtikten sonra denetlenir:
# durum iki ardışık yoklamada aynı olmalı ve bölüm dosyasının adını taşıyan jcode/kapı süreci koşmamalı.
D="$1"; S=/tmp/izle_denetle_durum; mkdir -p $S
while true; do
  for f in $(ls "$D"/bolum_*.md | sort); do
    b=$(basename $f); d=$(grep -m1 "^durum:" $f | sed 's/durum: //')
    case "$d" in tercume-tamam|inceleme-tamam) ;; *) rm -f "$S/$b.son"; continue;; esac
    pgrep -f "jcode-linux-x86_64.bin run.*$b|osmanlica_kapi.py.*$b" >/dev/null && { rm -f "$S/$b.son"; continue; }
    [ "$(cat "$S/$b.son" 2>/dev/null)" = "$d" ] || { echo "$d" > "$S/$b.son"; continue; }
    [ -f "$S/$b.$d.denetlendi" ] && continue
    touch "$S/$b.$d.denetlendi"
    python3 "$(dirname "$0")/osmanlica_denetle.py" "$D" $b | python3 -c "
import sys,json
r=json.load(sys.stdin)
print('DENETİM(kapı sonrası)',r['bolum'],r['durum'],'satır',r['satir'],'boş',r['bos_tercume'],'aynı-kısa',len(r['ayni_kisa_tercume']),'etiket',r['etiket_dagilimi'],'SORUN',{k:v[0] for k,v in r['sorunlar'].items()},flush=True)
"
  done
  sleep 15
done
