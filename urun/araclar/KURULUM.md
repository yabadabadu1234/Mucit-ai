# GEZİNME ORTAMI KURULUMU

**Durum (2026-11-18):** İki katman çalışıyor ve denendi.
1. **Başsız tarayıcı** (`gez.js`): sayfayı açar, ekran görüntüsü ve metin alır. Hazır gelir, kurulum gerekmez.
2. **Sanal masaüstü** (`masaustu.sh`): Xvfb + Openbox + gerçek (başlıklı) Chrome; ekran görüntüsü alınır, fare ve klavye kullanılır. Form doldurma ve tıklama burada yapılır. İlk kurulumda 4 paket yüklenir.

## Başlangıç kurulum komutu (ortam ayarına eklenecek)

```bash
set -e
apt-get update -qq
apt-get install -y -qq xdotool openbox scrot x11-utils
chmod +x /home/user/Mucit-ai/urun/araclar/masaustu.sh
node -e "require('playwright'); console.log('playwright hazır')"
```

Xvfb, `import` (ImageMagick) ve `google-chrome` ortamda zaten vardır. `playwright install` çalıştırılmaz.

## Kullanım

```bash
cd /home/user/Mucit-ai/urun/araclar
./masaustu.sh baslat "https://adres"   # masaüstünü ve Chrome'u açar
./masaustu.sh resim /tmp/ekran.png     # ekran görüntüsü
./masaustu.sh tikla 640 400            # tıklar
./masaustu.sh yaz "metin"              # yazar
./masaustu.sh tus Return               # tuşa basar
./masaustu.sh durdur
node gez.js "https://adres" /tmp/sayfa.png /tmp/sayfa.txt   # başsız, hızlı okuma
```

Mouser veri merkezi erişimini reddeder (403). Çerez ve abonelik pencereleri formu örter; önce kapatılır.
