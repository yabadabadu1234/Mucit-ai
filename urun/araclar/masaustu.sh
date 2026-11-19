#!/usr/bin/env bash
# Sanal masaüstü: Xvfb + Openbox + Chrome (başlıklı). Kullanım:
#   masaustu.sh baslat [adres]   masaüstünü ve tarayıcıyı açar
#   masaustu.sh resim dosya.png  ekran görüntüsü alır
#   masaustu.sh tikla X Y        fareyi götürüp tıklar
#   masaustu.sh yaz "metin"      klavyeden yazar
#   masaustu.sh tus Return       tuşa basar
#   masaustu.sh durdur
set -u
export DISPLAY=:99
EKRAN=1366x900x24
case "${1:-}" in
  baslat)
    pgrep -x Xvfb >/dev/null || (Xvfb :99 -screen 0 $EKRAN >/dev/null 2>&1 &)
    sleep 1
    pgrep -x openbox >/dev/null || (openbox >/dev/null 2>&1 &)
    sleep 1
    (google-chrome --no-sandbox --user-data-dir=/tmp/chrome-masaustu \
       --window-position=0,0 --window-size=1366,900 \
       --no-first-run --disable-gpu "${2:-about:blank}" >/dev/null 2>&1 &)
    sleep 4
    ;;
  resim)  import -window root "${2:-ekran.png}" ;;
  tikla)  xdotool mousemove "$2" "$3" click 1 ;;
  yaz)    xdotool type --delay 40 -- "$2" ;;
  tus)    xdotool key "$2" ;;
  durdur) pkill -f chrome-masaustu; pkill openbox; pkill Xvfb ;;
  *) echo "Kullanım: masaustu.sh baslat|resim|tikla|yaz|tus|durdur"; exit 2 ;;
esac
