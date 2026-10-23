import cizim as CZ
from icerik.yardim import *
from icerik import v_usb

ID = 'usb'
BASLIK = '4. USB-C ve USB’den gelen 3,3 volt (programlama güvencesi)'
OZET = 'Aynı USB-C girişi, bu kartta ek bir görev daha taşır: 12 volt yokken bile kartı 3,3 voltla beslemek. Doğrusal düzenleyici, ideal diyot (LM66100) ve sınırları.'
REFS = ['J1', 'R8', 'R9', 'U7', 'U11', 'C17', 'C18', 'U15']


def sema_ldo(v):
    c = CZ.Cizim('USB’den 3,3 V', 1000, 340, v.parca)
    c.bolge(10, 8, 980, 322, 'USB 5 V → AP2112K (düşük farklı doğrusal düzenleyici) → LM66100 ideal diyot → +3V3')
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
    yo = P['5'][1]
    c.tel(P['5'], (470, yo), (560, yo), (600, yo))
    c.etiket('+3V3_USB', 500, yo, 'yukari'); c.nokta(560, yo)
    r = c.kondansator('C18', 560, yo, 90); c.toprak(*r['b'])
    Q = c.kutu('U15', 700, yo - 26, [(1, 'VIN'), (3, 'CE')], [(6, 'VOUT'), (5, 'ST')], alt=[(2, 'GND'), (4, 'NC', 'nc')], genislik=110, baslik='LM66100', pinaralik=26)
    c.tel((600, yo), (600, Q['1'][1]), Q['1'])
    c.tel(Q['3'], (Q['3'][0] - 30, Q['3'][1])); c.ray('+3V3', Q['3'][0] - 30, Q['3'][1])
    c.tel(Q['6'], (Q['6'][0] + 40, Q['6'][1])); c.ray('+3V3', Q['6'][0] + 40, Q['6'][1])
    c.toprak(*Q['5']); c.toprak(*Q['2'])
    c.not_(120, 280, 'EN ucu VBUS’a bağlı: 5 V gelince çip kendiliğinden açılır.', 'start')
    c.not_(480, 270, 'U15: USB’den gelen 3,3 V yalnız 12 V yokken kartı besler', 'start')
    c.isaret(1, 200, 100); c.isaret(2, 430, 100); c.isaret(3, 660, 110)
    return c


def uret(ver, ctx):
    v = ver
    c1 = v_usb.sema(v, 'R8', 'R9', 'U7'); c2 = sema_ldo(v)
    for k in (c1, c2):
        hata = k.denetle(v.aglar)
        assert not hata, (k.ad, hata)
    h = ['<h1>%s</h1><p class="ozet">%s</p>' % (BASLIK, OZET)]
    h.append(kutu('not', '<ul><li>USB-C bağlantısı ve koruması (verici bölümüyle aynı: önce onu oku).</li><li>Doğrusal düzenleyici (LDO) nasıl çalışır, ne zaman anahtarlamalı çeviriciye tercih edilir?</li><li>İki kaynağı diyotla birleştirmenin bedeli ve ideal diyodun bunu nasıl küçülttüğü.</li><li>Gerçek bir sınır: AP2112K’nın akımı (en çok 600 mA) ve ısınması.</li></ul>', 'Bu bölümde öğreneceklerin:'))
    h.append('<h2>1. Büyük resim</h2><p>Bu kartın asıl beslemesi 12 volttur. USB-C ise programlama içindir; fakat sahada 12 volt olmadan da yazılım yüklemek isteriz. Bu yüzden USB’nin 5 voltu bir <b>doğrusal düzenleyici</b> (AP2112K-3.3) ile 3,3 volta indirilir ve bir <b>ideal diyotla</b> (U15, LM66100) kartın 3,3 V hattına verilir. 12 volt varken 3,3 V hattı TPS62933 çeviricisinden gelir ve ideal diyot geri akımı keser: iki kaynak birbirini bozmaz.</p>')
    h.append('<h2>2. Şema A — USB-C ve koruma</h2>' + sema_kutusu(c1))
    h.append('<p>Bu devre, vericideki USB devresiyle aynıdır (R8/R9 = CC dirençleri, U7 = USBLC6-2SC6); ayrıntılı açıklama <a href="../verici/usb.html">verici 2. bölümde</a>.</p>')
    h.append('<h2>3. Şema B — USB’den gelen 3,3 V</h2>' + sema_kutusu(c2))
    h.append(isaretli(['<b>Giriş kondansatörü (C17: 1 µF) ve düzenleyici (U11).</b> 5 V girişi alır, 3,3 V verir. EN (etkinleştirme) ucu VBUS’a bağlıdır: 5 V gelince çalışır.',
                       '<b>Çıkış kondansatörü (C18: 1 µF).</b> Doğrusal düzenleyicinin kararlılığı için çıkışta kondansatör gerekir; ESR değeri parça veri sayfasına göre seçilmelidir (seramik uygundur). [[bilgi]] [[dogrulanmadi]]',
                       '<b>İdeal diyot (U15: LM66100).</b> CE ucu çıkışa (+3V3) bağlıdır: çıkış girişten yüksekse MOSFET kapanır ve akım geri gitmez; açıkken direnci yaklaşık 91 mΩ olduğundan gerilim düşümü Schottky diyodun (0,3 V) yanında ihmal edilebilir (0,3 A’de ≈ 30 mV). [[ds]]']))
    h.append('<h2>4. Doğrusal düzenleyici nasıl çalışır?</h2><p>İçinde bir geçiş transistörü vardır; giriş–çıkış farkı bu transistörün üzerinde düşer ve <b>ısıya</b> dönüşür: P = (V<sub>giriş</sub> − V<sub>çıkış</sub>) × I. Bu kartta 5 V → 3,3 V: 1,7 V × akım. Anahtarlamalı çeviriciden daha basit, gürültüsüz ve ucuzdur; yalnız verimi V<sub>çıkış</sub> / V<sub>giriş</sub> = %s’dir. [[bilgi]]</p>' % sayi(3.3 / 5 * 100, 3) + '<p>Kartın ESP32 ve LoRa’sı USB’den ≈ 0,15–0,3 A çeker; ısı = 1,7 V × 0,25 A ≈ <b>%s W</b>. Küçük bir SOT-23-5 kılıf için yüksek değildir fakat sınırdadır: bu yüzden düzenleyici yalnız programlama/deneme için düşünülmüştür, kalıcı USB çalışması için değildir. [[tahmin]]</p>' % sayi(1.7 * 0.25, 3))
    h.append(hesap('ohm', [1.7, 6.8]))
    h.append(kutu('not', '<b>Önceki sürümde ne vardı?</b> USB yolunda 0,35 V düşüren bir Schottky diyot (SS14) vardı; USB ile kartın 3,3 V hattı ≈ 2,9 V’a iniyor, ESP32-S3’ün 3,0 V alt sınırının ve W5500’ün 2,97 V sınırının altında kalıyordu. Veri sayfalarını okuyunca bu bulundu ve diyot LM66100 ile değiştirildi: düşüm ≈ 30 mV, hat ≈ 3,27 V. [[tahmin]] Geriye kalan sınır: AP2112K’nın çıkış toleransı ve ısınması (aşağıda).', 'Düzeltilen kusur'))
    h.append(alistirma('12 V yokken USB’den çalışan karta 0,3 A ek akım bindi. LM66100 üzerinde ne kadar gerilim düşer, hat yaklaşık kaç volt olur?', 'Açık direnç ≈ 0,091 Ω: 0,3 A × 0,091 Ω ≈ 27 mV. Düzenleyici 3,3 V verirse hat ≈ 3,27 V olur; ESP32-S3’ün 3,0 V alt sınırının üstündedir.'))
    h.append('<h2>5. Parça kartları</h2><div class="kartlar">' + ''.join(v.kart_html(r) for r in REFS) + '</div>')
    h.append('<h2>6. Uç durumlar</h2><table><tr><th>Durum</th><th>Ne olur?</th></tr>'
             '<tr><td>12 V ve USB aynı anda</td><td>3,3 V ana hat çeviriciden gelir; USB 3,3 V’u ideal diyodun girişindedir ve çıkış ondan yüksek ya da eşitken U15 akım vermez. Güç kaynağı 12 V’tur.</td></tr>'
             '<tr><td>Yalnız USB</td><td>Kart ≈ 3,27 V ile çalışır; modem beslemesi (12 V) olmadığından modem kapalıdır. AP2112K’nın en çok 600 mA vermesi nedeniyle Ethernet ve telsiz birlikte yüklenirse sınır yaklaşılır. [[bilgi]]</td></tr>'
             '<tr><td>12 V var, USB yok</td><td>+3V3 hattından düzenleyici çıkışına geri akım U15 ile engellenir (CE ucu çıkışa bağlı). [[ds]]</td></tr>'
             '<tr><td>USB’ye 5 V’un üstü</td><td>Düzenleyici girişi en çok 6 V kabul eder (genel bilgi); USB 5 V ± %5’tir. [[bilgi]] [[dogrulanmadi]]</td></tr></table>')
    h.append('<h2>7. Kartta nerede?</h2>' + pano_kutusu(v, REFS, [(1, 'J1'), (2, 'U7'), (3, 'U11'), (4, 'U15')], 'USB soketi kart kenarında; düzenleyici ve ideal diyot sokete yakın.'))
    h.append('<h2>8. Kaynaklar</h2><ul class="kaynak"><li>ESP32-S3-WROOM-1 veri sayfası v1.8 (besleme 3,0–3,6 V).</li><li>TI LM66100 veri sayfası SLVSEZ8A (pinler, açık direnç, CE bağlantısı) — bu çalışmada okundu. AP2112K ve USBLC6 veri sayfaları bu bölüm için okunmadı; sayılar genel bilgidir.</li></ul>')
    return ''.join(h)
