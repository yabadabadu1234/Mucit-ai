import math
import cizim as CZ
from icerik.yardim import *

ID = 'lora'
BASLIK = '5. LoRa telsiz modülü ve anten bağlantısı'
OZET = 'RFM95W modülü: besleme, SPI bağlantısı, anten hattı. Telsiz bağlantı bütçesi ve 50 Ω’luk hat hesabı.'
REFS = ['U4', 'C8', 'C9', 'J2']


def sema(v, adlar=None, hedef=None, kond=('C8', 'C9')):
    c = CZ.Cizim('LoRa şeması', 1000, 400, v.parca)
    c.bolge(10, 8, 980, 382, 'LoRa TELSİZ  —  RFM95W-915S2 ve anten çıkışı')
    y0 = 90
    sol = [(2, 'MISO'), (3, 'MOSI'), (4, 'SCK'), (5, 'NSS'), (6, 'RESET'), (14, 'DIO0'), (15, 'DIO1')]
    P = c.kutu('U4', 400, y0, sol, [(9, 'ANT')], ust=[(13, '3.3V')], alt=[([1, 8, 10], 'GND')], genislik=160, baslik='RFM95W-915S2', pinaralik=26)
    adlar = adlar or {2: 'LORA_MISO', 3: 'LORA_MOSI', 4: 'LORA_SCK', 5: 'LORA_NSS', 6: 'LORA_RESET', 14: 'LORA_DIO0', 15: 'LORA_DIO1'}
    hedef = hedef or {2: 'işlemci IO13', 3: 'IO11', 4: 'IO12', 5: 'IO10', 6: 'IO14', 14: 'IO8', 15: 'IO9'}
    for no, ad in adlar.items():
        x, y = P[str(no)]
        c.tel((x, y), (x - 40, y))
        c.etiket(ad, x - 40, y, 'sol')
        c.not_(x - 150, y + 4, hedef[no] + ' →', 'end')
    x3, y3 = P['13']
    c.tel((x3, y3), (x3, y3 - 20)); c.ray('+3V3', x3, y3 - 20)
    xg, yg = P['1']
    c.toprak(xg, yg)
    # anten hatti ve SMA
    xa, ya = P['9']
    J = c.kutu('J2', 760, y0, [(1, 'iç iletken')], [], alt=[(2, 'dış kılıf')], genislik=130, baslik='SMA', pinaralik=26)
    c.tel((xa, ya), (700, ya), (J['1'][0], J['1'][1]))
    c.etiket('ANT_RF', 660, ya - 4, 'yukari')
    c.not_(590, ya + 30, '50 Ω’luk tek düz hat', 'start')
    c.toprak(J['2'][0], J['2'][1])
    # besleme kondansatorleri
    for i, (ref, x) in enumerate(((kond[0], 640), (kond[1], 740))):
        c.ray('+3V3', x, 300); c.kondansator(ref, x, 300, 90); c.toprak(x, 360)
    c.not_(600, 255, 'Besleme süzgeçleri (modüle yakın)', 'start')
    c.not_(40, 40, 'Bağlanmayan: DIO2, DIO3, DIO4, DIO5 (pimler 16, 11, 12, 7)', 'start')
    c.isaret(1, x3 + 40, y3 - 20); c.isaret(2, 940, 330); c.isaret(3, 560, ya - 24); c.isaret(4, 830, ya + 30)
    return c


def uret(ver, ctx):
    v = ver
    c = sema(v)
    hata = c.denetle(v.aglar)
    assert not hata, hata
    z, ee = mikroserit(0.4, 0.21, 0.035, 4.4)
    w_ant = iz_genislikleri(v, 'ANT_RF'); l_ant = iz_uzunlugu(v, 'ANT_RF'); via_ant = viya_sayisi(v, 'ANT_RF')
    h = ['<h1>%s</h1><p class="ozet">%s</p>' % (BASLIK, OZET)]
    h.append(kutu('not', '<ul><li>LoRa nedir, neden uzağa gider ve bunun bedeli nedir?</li><li>Modülün hangi ayağı ne iş yapar, kaçı bağlı, kaçı değil, neden?</li>'
                  '<li>Telsiz bağlantı bütçesini kendin hesapla: gönderme gücü, anten, duyarlılık, menzil.</li><li>Anten hattı neden 50 Ω olur? Hattın genişliğini kendin hesapla.</li></ul>', 'Bu bölümde öğreneceklerin:'))
    h.append('<h2>1. Büyük resim</h2><p>LoRa, bilgiyi “yayılı tayf” tekniğiyle çok yavaş ama çok sağlam gönderen bir kiplemedir: sinyal gürültünün altında bile ayıklanabildiği için <b>çok uzak</b> mesafeden alınabilir. Karşılığında hız düşüktür (bu modülde 0,018–37,5 kbit/sn). [[ds]] '
             'Düğmeye basma gibi birkaç bayt’lık mesajlar için tam uygundur. RFM95W, Semtech’in SX1276 yongasını içeren hazır bir modüldür; 868/915 MHz bandı için olan sürümdür. [[ds]] Bu kartta 915 MHz kullanılır.</p>')
    h.append('<h2>2. Şema</h2>' + sema_kutusu(c))
    h.append(isaretli(['<b>Besleme (3.3V ucu).</b> Veri sayfası işletim aralığını 1,8–3,7 V verir; +20 dBm çıkış için 2,4–3,7 V şartı vardır. Kart 3,3 V verir. [[ds]]',
                       '<b>Besleme süzgeçleri (C8 = 100 nF, C9 = 10 µF).</b> Telsiz gönderirken akımı aniden 120 mA’e çıkarır; modülün hemen yanındaki kondansatörler bu darbeyi karşılar, 3,3 V hattı çökmez.',
                       '<b>SPI hattı (MISO, MOSI, SCK, NSS).</b> İşlemci modülü bu dört telle yönetir (4 telli seri çevresel arayüz). RESET (sıfırlama) ve DIO0/DIO1 (modülden işlemciye “paket geldi/gönderildi” kesmesi) ayrı hatlardır.',
                       '<b>Anten çıkışı (ANT) ve SMA (J2).</b> Modülün anten ayağı, 50 Ω’luk bir bakır hat ile kart kenarındaki SMA konnektörüne gider. Hat <i>tek düz</i> olmalı: köşe, delikli geçit ve yan dal yok.']))
    h.append('<h2>3. Modülün ayakları</h2><table><tr><th>Ayak</th><th>Ad</th><th>Bu kartta</th><th>Neden</th></tr>'
             '<tr><td>1, 8, 10</td><td>GND</td><td>Toprak</td><td>Üç toprak ayağı da bağlanır; toprağın düşük empedanslı olması için.</td></tr>'
             '<tr><td>2–5</td><td>MISO, MOSI, SCK, NSS</td><td>İşlemci SPI</td><td>Komut ve veri taşıma</td></tr>'
             '<tr><td>6</td><td>RESET</td><td>İşlemci IO14</td><td>Donanım sıfırlama: 100 µs’lik düşük darbe, sonra 5 ms bekle. [[ds]]</td></tr>'
             '<tr><td>9</td><td>ANT</td><td>SMA’ya</td><td>Radyo girişi/çıkışı</td></tr>'
             '<tr><td>13</td><td>3.3V</td><td>+3V3</td><td>Besleme</td></tr>'
             '<tr><td>14, 15</td><td>DIO0, DIO1</td><td>İşlemci IO8, IO9</td><td>Kesme çıkışları: işlemcinin uykudan uyanıp telsizi yoklamadan olayı öğrenmesi için.</td></tr>'
             '<tr><td>7, 11, 12, 16</td><td>DIO5, DIO3, DIO4, DIO2</td><td>Bağlı değil</td><td>Bu görev için gerekli değil; boş bırakmak sorun değildir (yazılımla yapılandırılan çıkışlar).</td></tr></table>')
    h.append('<h2>4. Telsiz bağlantı bütçesi (menzil hesabı)</h2>')
    h.append('<p>Bir telsiz bağlantısı çalışır eğer: <b>gönderilen güç + anten kazançları − yol kaybı ≥ alıcının duyarlılığı + güvenlik payı</b>. Veri sayfası: [[ds]]</p>'
             '<ul><li>Çıkış gücü: en çok +20 dBm (100 mW); +17 dBm’de akım 87 mA, +20 dBm’de 120 mA.</li>'
             '<li>Duyarlılık (125 kHz bant genişliği): SF7 için −123 dBm, SF12 için −136 dBm; bant genişliği 62,5 kHz ve SF12’de −139 dBm.</li>'
             '<li>Alıcı akımı ≈ 10,3 mA (915 MHz, 125 kHz bant), uyku akımı 0,2 µA tipik (en çok 1 µA).</li></ul>'
             '<p>Serbest uzayda yol kaybı: <i>FSPL(dB) = 32,44 + 20·log₁₀(km) + 20·log₁₀(MHz)</i>. 915 MHz’de 1 km için %s dB.</p>' % sayi(32.44 + 20 * math.log10(915), 5))
    h.append(hesap('baglanti', [20, 2, 2, -136, 10, 915]))
    h.append(kutu('uyari', 'Serbest uzay menzili <b>üst sınırdır</b>. Bina, yer yansıması, ağaç, vücut, anten yüksekliği ve kablo kayıpları gerçek menzili birkaç kata kadar düşürür. Teklif öncesinde sorulan “kumanda sinyalinin hedef menzili” bu yüzden <b>sahada ölçülerek</b> doğrulanır; bu çalışmada ölçülmedi. [[dogrulanmadi]]', 'Dürüst sınır'))
    h.append(kutu('uyari', 'Veri sayfası, +20 dBm çıkışta <b>görev oranını en çok %1</b> ve anten portunda VSWR’yi en çok 3:1 olarak sınırlar (−40…+85 °C aralığı için; sıcaklık işletim aralığı tablo 50’de −20…+70 °C verilir). Anten takılmadan gönderme yapılmamalıdır. [[ds]]', 'Kullanım şartı'))
    h.append(alistirma('Gönderme gücü 14 dBm, iki anten 0 dBi, duyarlılık −136 dBm, 10 dB pay: serbest uzay menzili kaç km? (915 MHz)',
                       'Toplam: 14 + 0 + 0 + 136 − 10 = 140 dB izinli kayıp. Uzaklık: 10^((140 − 32,44 − 59,23) / 20) = 10^2,416 ≈ <b>260 km</b> (serbest uzay). Gerçekte çok daha kısa.'))
    h.append('<h2>5. Anten hattı: neden 50 Ω?</h2>')
    h.append('<p>Yüksek frekansta bir iz “tel” değil <b>iletim hattıdır</b>: sinyalin dalga boyu hattın boyuyla kıyaslanabilir olur (915 MHz’de boşlukta 32,8 cm; çeyrek dalga ≈ 8,2 cm) ve hattın <b>karakteristik empedansı</b> önemli hâle gelir. Kaynak, hat ve yük aynı empedansta (50 Ω) ise güç yansımadan aktarılır. Empedans, iz genişliği (w), izle altındaki toprak düzlemi arası dielektrik kalınlığı (h) ve dielektrik sabitine (ε<sub>r</sub>) bağlıdır.</p>')
    h.append(hesap('mikroserit', [0.4, 0.21, 0.035, 4.4]))
    h.append('<p>Bu kart dört katmanlıdır; anten izi üst katmanda, hemen altındaki ikinci katman (iç katman 1) kesintisiz toprak düzlemidir. Varsayılan istif (JLC04161H-7628: üst ile iç katman 1 arası yaklaşık 0,21 mm ön emdirilmiş cam elyaf, ε<sub>r</sub> ≈ 4,4) için 0,4 mm’lik iz <b>≈ %s Ω</b> verir (etkin ε<sub>r</sub> ≈ %s). [[tahmin]] '
             'Üretici istifi ve ε<sub>r</sub> değeri sipariş öncesinde teyit edilmelidir; ±%%10 sapma beklenir. [[dogrulanmadi]]</p>' % (sayi(z, 3), sayi(ee, 3)))
    h.append('<p>Kart dosyasındaki gerçek anten hattı: iz genişliği %s mm, toplam uzunluk ≈ <b>%s mm</b>, delikli geçit sayısı <b>%d</b>.</p>' % (
        ', '.join(sayi(w) for w in w_ant), sayi(l_ant, 3), via_ant))
    h.append('<h2>6. Parça kartları</h2><div class="kartlar">' + ''.join(v.kart_html(r) for r in REFS) + '</div>')
    h.append('<h2>7. Uç durumlar</h2><table><tr><th>Durum</th><th>Ne olur?</th></tr>'
             '<tr><td>Anten takılı değil</td><td>Yansıyan güç çıkış katına döner; VSWR çok yüksek olur, çıkış katı zarar görebilir. Veri sayfası VSWR ≤ 3:1 şartı koyar. [[ds]]</td></tr>'
             '<tr><td>3,3 V hattında çökme</td><td>Gönderme anında hat 2,4 V’un altına inerse +20 dBm çıkış çalışmaz; C8/C9 çökmeyi önler.</td></tr>'
             '<tr><td>Çalışma sıcaklığı</td><td>Modülün işletim aralığı −20…+70 °C’tır [[ds]]; soğuk depoda ya da sıcak araçta kullanılırsa dışarıdadır.</td></tr>'
             '<tr><td>Besleme açılışı</td><td>Güç verildikten sonra SPI’ya başlamadan önce 10 ms beklenmelidir. [[ds]]</td></tr>'
             '<tr><td>2,4 GHz ve 915 MHz’in karışması</td><td>İşlemci Wi-Fi/Bluetooth kullanırsa 2,4 GHz’de yayın yapar; 915 MHz’i doğrudan bozmaz, fakat harmonikler ve besleme gürültüsü için ayrı süzgeç gerekebilir. [[tahmin]]</td></tr></table>')
    h.append('<h2>8. Kartta nerede?</h2><p>Modül ile SMA arasındaki hat <b>mümkün olan en kısa ve düz</b> olmalı. Altında toprak düzlemi kesilmemeli; yanında 2–3 iz genişliği kadar boşluk ve toprak delikleri (via çiti) iyi olur.</p>' + pano_kutusu(v, REFS, [(1, 'U4'), (2, 'C8'), (3, 'J2')], 'SMA kart kenarında; modül ona en yakın bölgededir.'))
    h.append('<p>Ölçülen uzaklık: modül merkezi ile SMA arası ≈ <b>%s mm</b>.</p>' % sayi(mesafe(v, 'U4', 'J2'), 3))
    h.append('<h2>9. Kaynaklar</h2><ul class="kaynak"><li>HopeRF RFM95/96/97/98(W) veri sayfası V1.0 (SparkFun’un kopyası): §1.3–1.4 pinler; tablo 49–51 sınırlar ve akımlar; tablo 55–56 LoRa duyarlılıkları; §5.4.3 +20 dBm koşulları; §7.2 sıfırlama — bu çalışmada okundu.</li>'
             '<li>Mikroşerit formülü: Hammerstad yaklaşımı (genel mühendislik bilgisi); kart istifi varsayımdır.</li></ul>')
    return ''.join(h)
