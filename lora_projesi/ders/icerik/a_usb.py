import cizim as CZ
from icerik.yardim import *
from icerik import v_usb

ID = 'usb'
BASLIK = '4. USB-C ve USB’den gelen 3,3 volt (programlama güvencesi)'
OZET = 'Aynı USB-C girişi, bu kartta ek bir görev daha taşır: 12 volt yokken bile kartı 3,3 voltla beslemek. Doğrusal düzenleyici, Schottky diyot ve sınırları.'
REFS = ['J1', 'R8', 'R9', 'U7', 'U11', 'C17', 'C18', 'D4']


def sema_ldo(v):
    c = CZ.Cizim('USB’den 3,3 V', 1000, 340, v.parca)
    c.bolge(10, 8, 980, 322, 'USB 5 V → AP2112K (düşük farklı doğrusal düzenleyici) → Schottky diyot → +3V3')
    c.ray('VBUS', 70, 150)
    c.tel((70, 150), (130, 150), (230, 150))
    c.nokta(130, 150)
    r = c.kondansator('C17', 130, 150, 90); c.toprak(*r['b'])
    P = c.kutu('U11', 260, 120, [(1, 'IN'), (3, 'EN')], [(5, 'OUT')], alt=[(2, 'GND'), (4, 'NC', 'nc')], genislik=130, baslik='AP2112K-3.3', pinaralik=30)
    # IN ve EN ayni VBUS
    c.tel(P['1'], (230, P['1'][1])); c.tel((230, P['1'][1]), (230, P['3'][1]), P['3'])
    c.tel((130, 150), (130, 150))
    c.tel((230, 150), (230, 180)) if False else None
    c.toprak(*P['2'])
    c.tel(P['5'], (470, P['5'][1]), (560, P['5'][1]), (640, P['5'][1]))
    c.etiket('+3V3_USB', 500, P['5'][1], 'yukari'); c.nokta(560, P['5'][1])
    r = c.kondansator('C18', 560, P['5'][1], 90); c.toprak(*r['b'])
    c.diyot('D4', 640, P['5'][1], 0, 'schottky')
    c.tel((700, P['5'][1]), (780, P['5'][1])); c.ray('+3V3', 780, P['5'][1])
    c.not_(120, 280, 'EN ucu VBUS’a bağlı: 5 V gelince çip kendiliğinden açılır.', 'start')
    c.not_(500, 235, 'D4: USB’den gelen 3,3 V yalnız 12 V yokken kartı besler', 'start')
    c.isaret(1, 200, 100); c.isaret(2, 430, 100); c.isaret(3, 660, 110)
    return c


def uret(ver, ctx):
    v = ver
    c1 = v_usb.sema(v, 'R8', 'R9', 'U7'); c2 = sema_ldo(v)
    for k in (c1, c2):
        hata = k.denetle(v.aglar)
        assert not hata, (k.ad, hata)
    h = ['<h1>%s</h1><p class="ozet">%s</p>' % (BASLIK, OZET)]
    h.append(kutu('not', '<ul><li>USB-C bağlantısı ve koruması (verici bölümüyle aynı: önce onu oku).</li><li>Doğrusal düzenleyici (LDO) nasıl çalışır, ne zaman anahtarlamalı çeviriciye tercih edilir?</li><li>İki kaynağı diyotla birleştirmenin bedeli: voltaj düşümü ve ne olur.</li><li>Gerçek bir sınır: bu devre USB ile ESP32’yi alt gerilim sınırında bırakır.</li></ul>', 'Bu bölümde öğreneceklerin:'))
    h.append('<h2>1. Büyük resim</h2><p>Bu kartın asıl beslemesi 12 volttur. USB-C ise programlama içindir; fakat sahada 12 volt olmadan da yazılım yüklemek isteriz. Bu yüzden USB’nin 5 voltu bir <b>doğrusal düzenleyici</b> (AP2112K-3.3) ile 3,3 volta indirilir ve bir Schottky diyotla (D4) kartın 3,3 V hattına verilir. 12 volt varken 3,3 V hattı TPS62933 çeviricisinden gelir ve diyot ters kutuplanıp kapanır: iki kaynak birbirini bozmaz.</p>')
    h.append('<h2>2. Şema A — USB-C ve koruma</h2>' + sema_kutusu(c1))
    h.append('<p>Bu devre, vericideki USB devresiyle aynıdır (R8/R9 = CC dirençleri, U7 = USBLC6-2SC6); ayrıntılı açıklama <a href="../verici/usb.html">verici 2. bölümde</a>.</p>')
    h.append('<h2>3. Şema B — USB’den gelen 3,3 V</h2>' + sema_kutusu(c2))
    h.append(isaretli(['<b>Giriş kondansatörü (C17: 1 µF) ve düzenleyici (U11).</b> 5 V girişi alır, 3,3 V verir. EN (etkinleştirme) ucu VBUS’a bağlıdır: 5 V gelince çalışır.',
                       '<b>Çıkış kondansatörü (C18: 1 µF).</b> Doğrusal düzenleyicinin kararlılığı için çıkışta kondansatör gerekir; ESR değeri parça veri sayfasına göre seçilmelidir (seramik uygundur). [[bilgi]] [[dogrulanmadi]]',
                       '<b>Schottky diyot (D4).</b> USB’den gelen 3,3 V yalnız ana 3,3 V hattı ondan düşükken akım verir.']))
    h.append('<h2>4. Doğrusal düzenleyici nasıl çalışır?</h2><p>İçinde bir geçiş transistörü vardır; giriş–çıkış farkı bu transistörün üzerinde düşer ve <b>ısıya</b> dönüşür: P = (V<sub>giriş</sub> − V<sub>çıkış</sub>) × I. Bu kartta 5 V → 3,3 V: 1,7 V × akım. Anahtarlamalı çeviriciden daha basit, gürültüsüz ve ucuzdur; yalnız verimi V<sub>çıkış</sub> / V<sub>giriş</sub> = %s’dir. [[bilgi]]</p>' % sayi(3.3 / 5 * 100, 3) + '<p>Kartın ESP32 ve LoRa’sı USB’den ≈ 0,15–0,3 A çeker; ısı = 1,7 V × 0,25 A ≈ <b>%s W</b>. Küçük bir SOT-23-5 kılıf için yüksek değildir fakat sınırdadır: bu yüzden düzenleyici yalnız programlama/deneme için düşünülmüştür, kalıcı USB çalışması için değildir. [[tahmin]]</p>' % sayi(1.7 * 0.25, 3))
    h.append(hesap('ohm', [1.7, 6.8]))
    h.append(kutu('uyari', '<b>Dürüst sınır — USB ile çalışmada 3,3 V hattı alt sınırda.</b> Düzenleyici çıkışı 3,3 V (±%2) olsa bile diyot düşümü (≈ 0,2–0,3 V [[tahmin]]) nedeniyle kartın 3,3 V hattı ≈ <b>3,0–3,1 V</b> olur. ESP32-S3’ün besleme alt sınırı 3,0 V’tur. [[ds]] Yani USB ile besleme çalışır fakat <b>marjsızdır</b>: yük akımı artınca (LoRa gönderirken, Ethernet) hat 3,0 V’un altına inebilir. İyileştirme: D4 yerine düşük dirençli P kanallı transistörle “ideal diyot” ya da yalnız programlama için yeterli olduğunu kabul etmek. Bu kart için kabul: USB yalnız yazılım yüklemek içindir; Ethernet/telsiz gerçek çalışması 12 V ile yapılır.', 'Dürüst sınır'))
    h.append(alistirma('12 V yokken USB’den çalışan karta LoRa +20 dBm gönderirken 120 mA ekstra akım bindi; D4’te düşüm 0,35 V’a çıktı. Kartın 3,3 V hattı yaklaşık kaç volt olur ve neden sorun?', 'Düzenleyici 3,3 V’ta kalırsa (maksimum akıma kadar) kart hattı 3,3 − 0,35 = 2,95 V olur; bu ESP32-S3’ün 3,0 V alt sınırının altındadır: sıfırlanma ya da dengesiz çalışma olur.'))
    h.append('<h2>5. Parça kartları</h2><div class="kartlar">' + ''.join(v.kart_html(r) for r in REFS) + '</div>')
    h.append('<h2>6. Uç durumlar</h2><table><tr><th>Durum</th><th>Ne olur?</th></tr>'
             '<tr><td>12 V ve USB aynı anda</td><td>3,3 V ana hat 3,3 V; USB hattı diyot sonrası ≈ 3,0 V: D4 kapalı, USB hiçbir akım katmaz. Güç kaynağı 12 V’tur.</td></tr>'
             '<tr><td>Yalnız USB</td><td>Kart 3,0–3,1 V ile çalışır (yukarıdaki sınır); modem beslemesi (12 V) olmadığından modem kapalıdır.</td></tr>'
             '<tr><td>12 V var, USB yok</td><td>+3V3 hattından düzenleyici çıkışına geri akım D4 ile engellenir.</td></tr>'
             '<tr><td>USB’ye 5 V’un üstü</td><td>Düzenleyici girişi en çok 6 V kabul eder (genel bilgi); USB 5 V ± %5’tir. [[bilgi]] [[dogrulanmadi]]</td></tr></table>')
    h.append('<h2>7. Kartta nerede?</h2>' + pano_kutusu(v, REFS, [(1, 'J1'), (2, 'U7'), (3, 'U11'), (4, 'D4')], 'USB soketi kart kenarında; düzenleyici ve diyot sokete yakın.'))
    h.append('<h2>8. Kaynaklar</h2><ul class="kaynak"><li>ESP32-S3-WROOM-1 veri sayfası v1.8 (besleme 3,0–3,6 V).</li><li>AP2112K, SS14 ve USBLC6 veri sayfaları bu çalışmada okunmadı; sayılar genel bilgidir.</li></ul>')
    return ''.join(h)
