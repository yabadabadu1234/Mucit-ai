#!/usr/bin/env bash
# Çalışma klasöründe bir bölümün durumu 'tercume-tamam' veya 'inceleme-tamam' olur olmaz denetler ve özet satırı basar.
D="$1"; S=/tmp/izle_denetle_durum; mkdir -p $S
while true; do
  for f in $(ls "$D"/bolum_*.md | sort); do
    b=$(basename $f); d=$(grep -m1 "^durum:" $f | sed 's/durum: //')
    case "$d" in tercume-tamam|inceleme-tamam) ;; *) continue;; esac
    [ -f "$S/$b.$d" ] && continue
    touch "$S/$b.$d"
    python3 "$(dirname "$0")/osmanlica_denetle.py" "$D" $b | python3 -c "
import sys,json
r=json.load(sys.stdin)
print('DENETİM',r['bolum'],r['durum'],'satır',r['satir'],'boş',r['bos_tercume'],'aynı-kısa',len(r['ayni_kisa_tercume']),'düzle-aynı',r.get('duz_ile_ayni',0),'etiket',r['etiket_dagilimi'],'SORUN',{k:v[0] for k,v in r['sorunlar'].items()},flush=True)
"
  done
  sleep 15
done
