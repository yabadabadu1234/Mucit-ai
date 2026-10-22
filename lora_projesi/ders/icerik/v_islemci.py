import math
import cizim as CZ
from icerik.yardim import *

ID = 'islemci'
BASLIK = '3. İşlemci: sıfırlama, besleme süzgeçleri ve ayak atamaları'
OZET = 'ESP32-S3 modülü: sıfırlama devresinin zaman hesabı, açılış (strapping) uçları, hangi ayağın hangi işe verildiği ve neden.'
REFS = ['U1', 'R1', 'C7', 'C5', 'C6']


def sema(v):
    c = CZ.Cizim('Verici işlemci şeması', 1000, 600, v.parca)
    c.bolge(10, 8, 980, 582, 'İŞLEMCİ  —  ESP32-S3-WROOM-1: besleme, sıfırlama ve ayak atamaları')
    y0 = 50
    sag = [(27, 'IO0'), (4, 'IO4'), (38, 'IO2'), (5, 'IO5'), (39, 'IO1'), (6, 'IO6'), (7, 'IO7'),
           (18, 'IO10'), (19, 'IO11'), (20, 'IO12'), (21, 'IO13'), (22, 'IO14'), (12, 'IO8'), (17, 'IO9'), (14, 'IO20'), (13, 'IO19')]
    sol = [(2, '3V3'), (3, 'EN'), ([1, 40, 41], 'GND')]
    P = c.kutu('U1', 400, y0, sol, sag, genislik=170, baslik='ESP32-S3-WROOM-1', pinaralik=28)
    # sol uclar
    y3, ye, yg = P['2'][1], P['3'][1], P['1'][1]
    c.tel((385, y3), (330, y3)); c.ray('+3V3', 330, y3)
    c.tel((385, ye), (330, ye)); c.etiket('EN', 330, ye, 'sol')
    c.tel((385, yg), (330, yg)); c.toprak(330, yg)
    # sag uclar -> etiket
    adlar = {27: 'BTN1', 4: 'BTN2', 38: 'BTN3', 5: 'BTN4', 39: 'BTN5', 6: 'BTN6', 7: 'LED_CTL', 18: 'LORA_NSS', 19: 'LORA_MOSI', 20: 'LORA_SCK',
             21: 'LORA_MISO', 22: 'LORA_RESET', 12: 'LORA_DIO0', 17: 'LORA_DIO1', 14: 'USB_DP', 13: 'USB_DM'}
    hedef = {27: 'düğme 1 (4. bölüm)', 4: 'düğme 2', 38: 'düğme 3', 5: 'düğme 4', 39: 'düğme 5', 6: 'düğme 6', 7: 'durum LED’i',
             18: 'LoRa: seçim', 19: 'LoRa: veri girişi', 20: 'LoRa: saat', 21: 'LoRa: veri çıkışı', 22: 'LoRa: sıfırlama', 12: 'LoRa: kesme 0', 17: 'LoRa: kesme 1',
             14: 'USB-C D+ (2. bölüm)', 13: 'USB-C D− (2. bölüm)'}
    for no, ad in adlar.items():
        x, y = P[str(no)]
        c.tel((x, y), (x + 35, y))
        c.etiket(ad, x + 35, y, 'sag')
        c.not_(x + 135, y + 4, '← ' + hedef[no], 'start')
    # reset blogu (sol alt)
    by = 330
    c.ray('+3V3', 60, by)
    c.direnc('R1', 60, by, 90)
    c.tel((60, by + 60), (60, by + 65), (60, by + 70))
    c.etiket('EN', 60, by + 65, 'sag')
    c.kondansator('C7', 60, by + 70, 90)
    c.toprak(60, by + 130)
    c.not_(36, by + 160, 'Sıfırlama gecikmesi', 'start')
    # besleme suzgecleri
    c.ray('+3V3', 190, by); c.kondansator('C5', 190, by, 90); c.toprak(190, by + 60)
    c.ray('+3V3', 280, by); c.kondansator('C6', 280, by, 90); c.toprak(280, by + 60)
    c.not_(180, by + 160, 'Besleme süzgeçleri', 'start')
    c.not_(40, 578, 'Bağlanmayan ayaklar: IO3, IO15–IO18, IO21, IO35–IO42, IO45–IO48, RXD0, TXD0', 'start')
    c.isaret(1, 380, y0 + 10); c.isaret(2, 36, by + 35); c.isaret(3, 205, by + 95)
    return c


def uret(ver, ctx):
    v = ver
    c = sema(v)
    hata = c.denetle(v.aglar)
    assert not hata, hata
    R = v.deg('R1'); C = v.deg('C7'); tau = R * C
    t_vih = tau * math.log(1 / (1 - 0.75))
    h = ['<h1>%s</h1><p class="ozet">%s</p>' % (BASLIK, OZET)]
    h.append(kutu('not', '<ul><li>İşlemci modülü içinde ne var, kartın sana bırakmadığı işler hangileri?</li><li>EN ucundaki direnç–kondansatör sıfırlama devresinin zamanını hesaplayacaksın.</li>'
                  '<li>Açılışta seviyesi önemli olan ayaklar (strapping) hangileri ve bu kart onlara ne yaptı?</li><li>Bir mikrodenetleyicinin ayaklarını sen nasıl atarsın? Kuralları öğren.</li></ul>', 'Bu bölümde öğreneceklerin:'))
    h.append('<h2>1. Büyük resim</h2><p>ESP32-S3-WROOM-1 bir <b>modüldür</b>: işlemci yongası, flash bellek, 40 MHz kristal, anten uyumlama devresi ve kart üstü anten, 18,0 × 25,5 × 3,1 mm’lik bir metal kalkan altında hazır gelir. [[ds]] '
             'Bizim işimiz modüle <b>besleme vermek</b>, <b>sıfırlama devresi kurmak</b> ve <b>ayakları görevlendirmektir</b>. Kristal ve flash bağlantısı modülün içinde bittiği için bunlarla uğraşmayız; ama anten çevresini boş bırakmak bizim işimizdir (aşağıda).</p>')
    h.append('<h2>2. Şema</h2>' + sema_kutusu(c))
    h.append(isaretli([
        '<b>Modül (U1).</b> Sağ tarafta işlevlerine göre sıralanmış 16 kullanılan ayak ve hedefleri; sol tarafta besleme (3V3), sıfırlama (EN) ve toprak. Modülün 41 ayağından %d’i bağlanmadı (şemanın altında yazılı).' % sum(1 for q in v.parca['U1'].pinler.values() if not q['ag']),
        '<b>Sıfırlama devresi (R1 = 10 kΩ, C7 = 1 µF).</b> EN ucu <b>asla boşta bırakılmamalıdır</b> (veri sayfası). Direnç EN’i 3,3 V’a çeker; kondansatör EN’in yavaş yükselmesini sağlar: açılışta besleme tam oturmadan çip başlamasın.',
        '<b>Besleme süzgeçleri (C5 = 22 µF, C6 = 100 nF).</b> İşlemci Wi-Fi ya da yoğun işlem yaparken akımı çok hızlı değiştirir; yakındaki kondansatörler bu akımı sağlar. Büyük olan düşük frekansı, küçük olan yüksek frekansı karşılar.']))
    h.append('<h2>3. Hesap: sıfırlama devresinin süresi</h2>')
    h.append('<p>EN ucu, çipin giriş eşiklerine göre davranır: <b>yüksek sayılmak için ≥ 0,75 × VDD</b>, <b>düşük (sıfırlama) sayılmak için ≤ 0,25 × VDD</b> olmalıdır. VDD = 3,3 V için eşikler %s V ve %s V’tur. [[ds]] '
             'Besleme açılınca R1 üzerinden C7 dolar: <i>V<sub>EN</sub>(t) = VDD × (1 − e<sup>−t/τ</sup>)</i>. τ = R × C = %s kΩ × %s µF = <b>%s ms</b>. '
             'EN’in yüksek eşiğe (%s V) ulaşma süresi: t = −τ × ln(1 − 0,75) = <b>%s ms</b>.</p>' % (
                 sayi(0.75 * 3.3, 4), sayi(0.25 * 3.3, 3), sayi(R / 1e3), sayi(C * 1e6), sayi(tau * 1e3), sayi(0.75 * 3.3, 4), sayi(t_vih * 1e3, 3)))
    h.append(hesap('rc', [R, C * 1e6]))
    h.append('<p>Veri sayfası, EN’in açılmadan önce besleme kanalının en az 50 µs önceden oturmuş olmasını ister (t<sub>STBL</sub>). [[ds]] %s ms ≫ 50 µs; şartı büyük marjla sağlar. '
             'Çipin sıfırlanması içinse EN’in en az 50 µs boyunca ≤ %s V’ta tutulması gerekir (t<sub>RST</sub>). [[ds]] Bu karta bir düğmeyle EN’i toprağa çekmek konmadı; sıfırlama güç kesilip verilerek ya da yazılımla yapılır.</p>' % (sayi(t_vih * 1e3, 3), sayi(0.25 * 3.3, 3)))
    h.append(alistirma('C7’yi 100 nF yapsaydın EN’in yükselme süresi ne olurdu? Bunun açılışta bir riski var mıdır?',
                       'τ = 10 kΩ × 0,1 µF = 1 ms → t = 1,386 ms. Çip 50 µs’yi aşan bu süre içinde de rahat sıfırlanır, fakat besleme 1,4 ms’den uzun sürede oturan bir çeviriciyle (pil bitmek üzere iken yumuşak başlatma) EN erken yükselip çip yeterli gerilim olmadan başlatılabilir. 1 µF bu yüzden daha güvenli.'))
    h.append('<h2>4. Açılış (strapping) uçları</h2>')
    h.append('<p>Bazı ayakların açılıştaki seviyesi, çipin nasıl başlayacağını belirler. Veri sayfasına göre: [[ds]]</p>'
             '<table><tr><th>Ayak</th><th>Varsayılan (bağlı değilse)</th><th>Ne belirler?</th><th>Bu kartta</th></tr>'
             '<tr><td>IO0 (27)</td><td>zayıf yukarı çekme (≈ 45 kΩ) → 1</td><td>0 (ve IO46 = 0) ise <b>indirme kipi</b>; 1 ise flash’tan başlar</td><td>Birinci düğme: basılıysa 0. Düğme dışında R2 = 100 kΩ yukarı çekme.</td></tr>'
             '<tr><td>IO3 (15)</td><td>boşta</td><td>JTAG kaynağı (yalnız eFuse ayarlıysa)</td><td>Bağlı değil; varsayılan eFuse değerinde yok sayılır.</td></tr>'
             '<tr><td>IO45 (26)</td><td>zayıf aşağı çekme → 0</td><td>Flash besleme gerilimi (3,3 V)</td><td>Bağlı değil; bu modülde 3,3 V flash için doğru.</td></tr>'
             '<tr><td>IO46 (16)</td><td>zayıf aşağı çekme → 0</td><td>İndirme kipi (IO0 ile) ve ROM mesajları</td><td>Bağlı değil.</td></tr></table>')
    h.append(kutu('ipucu', 'Programlama kipine girmek için: birinci düğmeye <b>basılı tut</b>, USB-C’yi tak (ya da sıfırla), sonra bırak. IO0 = 0 ve IO46 = 0 (varsayılan) olduğundan çip indirme kipinde açılır. [[ds]]', 'Kullanım'))
    h.append('<h2>5. Ayak atama kuralları</h2><p>Bu kartta ayaklar şu kurallarla verildi:</p><ol>'
             '<li><b>Uyandırma gerekenler RTC ayaklarına.</b> Derin uykuda yalnız “RTC” denen ayaklar uyandırma yapabilir; veri sayfasına göre IO0–IO21 bu gruptadır. [[ds]] Altı düğme IO0, IO1, IO2, IO4, IO5, IO6’ya bağlandı.</li>'
             '<li><b>Strapping uçlarından kaçın, kaçınamıyorsan etkisini bil.</b> IO0 düğme olarak kullanıldı (bilinçli: indirme kipi için); IO3, IO45, IO46 bağlanmadı.</li>'
             '<li><b>Yerleşik USB’yi sabit ayaklara bağla.</b> IO19 = D−, IO20 = D+; başka yere alınamaz. [[ds]]</li>'
             '<li><b>Hızlı veri hattını (SPI) gruplayıp yakın tut.</b> LoRa SPI için IO10 (seçim), IO11 (veri giriş), IO12 (saat), IO13 (veri çıkış) kullanıldı; bunlar çipin SPI2 denetleyicisinin varsayılan ayaklarıdır (IO10 = FSPICS0, IO11 = FSPID, IO12 = FSPICLK, IO13 = FSPIQ). [[ds]]</li>'
             '<li><b>JTAG ayakları (IO39–IO42) ve UART0 (TXD0/RXD0) boş bırakıldı.</b> Hata ayıklamak için kullanılabilir; USB zaten programlamayı sağlar.</li></ol>')
    h.append('<h2>6. Akım ve besleme şartları</h2><table><tr><th>Büyüklük</th><th>Değer</th><th>Kaynak</th></tr>'
             '<tr><td>Besleme gerilimi</td><td>3,0 … 3,6 V (tipik 3,3 V)</td><td>[[ds]] tablo 6-2</td></tr>'
             '<tr><td>Dış beslemenin verebilmesi gereken akım</td><td>≥ 0,5 A</td><td>[[ds]] tablo 6-2</td></tr>'
             '<tr><td>Wi-Fi gönderirken tepe akım</td><td>355 mA (802.11b, 20,5 dBm)</td><td>[[ds]] tablo 6-4</td></tr>'
             '<tr><td>Derin uyku (RTC bellek ve RTC çevre birimleri açık)</td><td>8 µA</td><td>[[ds]] tablo 6-7</td></tr>'
             '<tr><td>Giriş yüksek/alçak eşiği</td><td>0,75 × VDD / 0,25 × VDD</td><td>[[ds]] tablo 6-3</td></tr></table>')
    h.append(kutu('uyari', 'Veri sayfası, dış beslemenin <b>en az 0,5 A</b> verebilmesini ister. Bu kartın çeviricisi (TPS63031) yükseltme modunda 500 mA verir ve düşük pil geriliminde daha azını verir (1. bölüm). Bu yüzden kart <b>Wi-Fi ya da Bluetooth açık kullanım için tasarlanmadı</b>; yalnız düğme + LoRa için, kısa işlemci çalışması varsayıldı. Wi-Fi eklenirse besleme yeniden hesaplanmalıdır. [[tahmin]]', 'Dürüst sınır'))
    h.append('<h2>7. Parça kartları</h2><div class="kartlar">' + ''.join(v.kart_html(r) for r in REFS) + '</div>')
    h.append('<h2>8. Anten bölgesi ve yerleşim</h2><p>Modülün kart anteni bir köşesindedir; çevresinde bakır, iz ve parça <b>bulunmamalı</b> ve modül kart kenarına öyle yerleştirilmelidir ki anten kartın dışına taşsın ya da boş bir bölgeye bakmalıdır (veri sayfasındaki “keepout” bölgesi). [[ds]] Altındaki toprak ayağı (41) lehimlenmeli ve altına ısıl delikler (via) konmalıdır.</p>')
    kon = v.d['konum']['U1']
    h.append('<p>Bizim kartta modülün merkezi (%s, %s) mm’dedir, kart <b>%s × %s mm</b>’dir. Modülün anten ucu karta göre dışa dönüktür; altta ve yanda hiçbir parça yoktur (aşağıdaki görünümde kontrol et).</p>' % (
        sayi(kon['x'], 4), sayi(kon['y'], 4), sayi(v.d['kart']['g'], 4), sayi(v.d['kart']['y_'], 4)))
    h.append(pano_kutusu(v, REFS, [(1, 'U1'), (2, 'R1'), (3, 'C5')], 'Anten bölgesi: modülün kart anteni tarafındaki bakırsız bölgeye bak.'))
    h.append('<h2>9. Kaynaklar</h2><ul class="kaynak"><li>ESP32-S3-WROOM-1 / -1U veri sayfası v1.8: tablolar 3-1, 4-1, 4-3, 4-6, 6-2, 6-3, 6-4, 6-7 ve §11 (yerleşim) bu çalışmada okundu.</li></ul>')
    return ''.join(h)
