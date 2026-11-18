# GEZİNME ORTAMI KURULUMU

**Hülâsa:** Bu ortamda Chromium ve Playwright **hazır gelmektedir**; ayrıca bir şey kurmak gerekmez (2026-11-18'de sayfa açılıp ekran görüntüsü alınarak denendi). Gerçek bir masaüstü ekranı yoktur; gezinme, başsız (headless) tarayıcıyla sayfayı açıp **ekran görüntüsü** ve **metin** almaktır. Görüntüyü ben okuyabilirim.

## Başlangıç kurulum komutu (ortam ayarına eklenecek)

```bash
# Tarayıcıyı kurmaz, yalnız hazır olduğunu denetler. "playwright install" ÇALIŞTIRMAYIN:
# hazır tarayıcı başka sürümü bulamaz.
set -e
cd /home/user/Mucit-ai
node -e "require('playwright'); console.log('playwright hazır')"
test -x /opt/pw-browsers/chromium || ls /opt/pw-browsers | head -3
```

## Kullanım

```bash
cd /home/user/Mucit-ai/urun/araclar
node gez.js "https://adres" /tmp/sayfa.png /tmp/sayfa.txt
```

- `sayfa.png`: bütün sayfanın ekran görüntüsü; `sayfa.txt`: sayfanın metni.
- Bazı siteler veri merkezi erişimini reddeder; Mouser (403) böyledir. Waveshare, samm, robotsepeti, e-paperdisplay ve E Ink mağazası açılmaktadır.
- Ödeme, giriş, form gönderme gibi işlemler yapılmaz.
