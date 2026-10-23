import math
import cizim as CZ
from icerik.yardim import *

ID = 'lora'
BASLIK = '5. LoRa telsiz modülü ve anten bağlantısı'
OZET = 'Ra-01H modülü: besleme, SPI bağlantısı, anten hattı. Telsiz bağlantı bütçesi ve 50 Ω’luk hat hesabı.'
REFS = ['U4', 'C8', 'C9', 'J2']


def sema(v, adlar=None, hedef=None, kond=('C8', 'C9')):
    c = CZ.Cizim('LoRa şeması', 1000, 400, v.parca)
    c.bolge(10, 8, 980, 382, 'LoRa TELSİZ  —  Ra-01H (SX1276) ve anten çıkışı')
    y0 = 90
    sol = [(13, 'MISO'), (14, 'MOSI'), (12, 'SCK'), (15, 'NSS'), (4, 'RESET'), (5, 'DIO0'), (6, 'DIO1')]
    P = c.kutu('U4', 400, y0, sol, [(1, 'ANT')], ust=[(3, 'VDD')], alt=[([2, 9, 16], 'GND')], genislik=160, baslik='Ra-01H', pinaralik=26)
    adlar = adlar or {13: 'LORA_MISO', 14: 'LORA_MOSI', 12: 'LORA_SCK', 15: 'LORA_NSS', 4: 'LORA_RESET', 5: 'LORA_DIO0', 6: 'LORA_DIO1'}
    hedef = hedef or {13: 'işlemci IO13', 14: 'IO11', 12: 'IO12', 15: 'IO10', 4: 'IO14', 5: 'IO8', 6: 'IO9'}
    for no, ad in adlar.items():
        x, y = P[str(no)]
        c.tel((x, y), (x - 40, y))
        c.etiket(ad, x - 40, y, 'sol')
        c.not_(x - 150, y + 4, hedef[no] + ' →', 'end')
    x3, y3 = P['3']
    c.tel((x3, y3), (x3, y3 - 20)); c.ray('+3V3', x3, y3 - 20)
    xg, yg = P['2']
    c.toprak(xg, yg)
    # anten hatti ve SMA
    xa, ya = P['1']
    J = c.kutu('J2', 760, y0, [(1, 'iç iletken')], [], alt=[(2, 'dış kılıf')], genislik=130, baslik='SMA', pinaralik=26)
    c.tel((xa, ya), (700, ya), (J['1'][0], J['1'][1]))
    c.etiket('ANT_RF', 660, ya - 4, 'yukari')
    c.not_(590, ya + 30, '50 Ω’luk tek düz hat', 'start')
    c.toprak(J['2'][0], J['2'][1])
    # besleme kondansatorleri
    for i, (ref, x) in enumerate(((kond[0], 640), (kond[1], 740))):
        c.ray('+3V3', x, 300); c.kondansator(ref, x, 300, 90); c.toprak(x, 360)
    c.not_(600, 255, 'Besleme süzgeçleri (modüle yakın)', 'start')
    c.not_(40, 40, 'Bağlanmayan: DIO2, DIO3, DIO4, DIO5 (pimler 7, 8, 10, 11)', 'start')
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
             'Düğmeye basma gibi birkaç bayt’lık mesajlar için tam uygundur. Ra-01H (Ai-Thinker), Semtech’in SX1276 yongasını içeren 17 × 16 mm’lik hazır bir modüldür; 803–930 MHz aralığını destekler. [[ds]] Bu kartta 915 MHz kullanılır. Hız bu modülde en çok 300 kbit/sn’dir. [[ds]]</p>')
    h.append('<h2>2. Şema</h2>' + sema_kutusu(c))
    h.append(isaretli(['<b>Besleme (3.3V ucu).</b> Ai-Thinker belgesi işletim aralığını 1,8–3,6 V (tipik 3,3 V) verir. Kart 3,3 V verir. [[ds]]',
                       '<b>Besleme süzgeçleri (C8 = 100 nF, C9 = 10 µF).</b> Telsiz gönderirken akımı aniden yaklaşık 97 mA’e (915 MHz ortalama; en çok 105 mA) çıkarır; modülün hemen yanındaki kondansatörler bu darbeyi karşılar, 3,3 V hattı çökmez.',
                       '<b>SPI hattı (MISO, MOSI, SCK, NSS).</b> İşlemci modülü bu dört telle yönetir (4 telli seri çevresel arayüz). RESET (sıfırlama) ve DIO0/DIO1 (modülden işlemciye “paket geldi/gönderildi” kesmesi) ayrı hatlardır.',
                       '<b>Anten çıkışı (ANT) ve SMA (J2).</b> Modülün anten ayağı, 50 Ω’luk bir bakır hat ile kart kenarındaki SMA konnektörüne gider. Hat <i>tek düz</i> olmalı: köşe, delikli geçit ve yan dal yok.']))
    h.append('<h2>3. Modülün ayakları</h2><table><tr><th>Ayak</th><th>Ad</th><th>Bu kartta</th><th>Neden</th></tr>'
             '<tr><td>2, 9, 16</td><td>GND</td><td>Toprak</td><td>Üç toprak ayağı da bağlanır; toprağın düşük empedanslı olması için.</td></tr>'
             '<tr><td>12–15</td><td>SCK, MISO, MOSI, NSS</td><td>İşlemci SPI</td><td>Komut ve veri taşıma</td></tr>'
             '<tr><td>4</td><td>RESET</td><td>İşlemci IO14</td><td>Donanım sıfırlama (SX1276 yonga belgesine göre 100 µs’lik düşük darbe, sonra 5 ms bekleme; Ai-Thinker belgesi bunu ayrıca vermez). [[bilgi]]</td></tr>'
             '<tr><td>1</td><td>ANT</td><td>SMA’ya</td><td>Radyo girişi/çıkışı</td></tr>'
             '<tr><td>3</td><td>VDD</td><td>+3V3</td><td>Besleme</td></tr>'
             '<tr><td>5, 6</td><td>DIO0, DIO1</td><td>İşlemci IO8, IO9</td><td>Kesme çıkışları: işlemcinin uykudan uyanıp telsizi yoklamadan olayı öğrenmesi için.</td></tr>'
             '<tr><td>7, 8, 10, 11</td><td>DIO2, DIO3, DIO4, DIO5</td><td>Bağlı değil</td><td>Bu görev için gerekli değil; boş bırakmak sorun değildir (yazılımla yapılandırılan çıkışlar).</td></tr></table>')
    h.append('<h2>4. Telsiz bağlantı bütçesi (menzil hesabı)</h2>')
    h.append('<p>Bir telsiz bağlantısı çalışır eğer: <b>gönderilen güç + anten kazançları − yol kaybı ≥ alıcının duyarlılığı + güvenlik payı</b>. Veri sayfası: [[ds]]</p>'
             '<ul><li>Çıkış gücü: en çok +19 dBm, çıkış akımı en çok 105 mA; 915 MHz’de ortalama gönderme akımı 97 mA. [[ds]]</li>'
             '<li>Duyarlılık: “en çok −140 dBm’e kadar” (Ai-Thinker belgesi; hangi yayılma faktörü ve bant genişliği için olduğu yazılı değil). Aşağıdaki hesapta ihtiyatla −136 dBm kullanılır. [[ds]]</li>'
             '<li>Alıcı akımı 12,15 mA, bekleme (standby) akımı 1,5 mA (915 MHz). Belge uyku akımını yazmaz; SX1276 yonga belgesinde tipik 0,2 µA’dir. [[bilgi]]</li></ul>'
             '<p>Serbest uzayda yol kaybı: <i>FSPL(dB) = 32,44 + 20·log₁₀(km) + 20·log₁₀(MHz)</i>. 915 MHz’de 1 km için %s dB.</p>' % sayi(32.44 + 20 * math.log10(915), 5))
    h.append(hesap('baglanti', [19, 2, 2, -136, 10, 915]))
    h.append(kutu('uyari', 'Serbest uzay menzili <b>üst sınırdır</b>. Bina, yer yansıması, ağaç, vücut, anten yüksekliği ve kablo kayıpları gerçek menzili birkaç kata kadar düşürür. Teklif öncesinde sorulan “kumanda sinyalinin hedef menzili” bu yüzden <b>sahada ölçülerek</b> doğrulanır; bu çalışmada ölçülmedi. [[dogrulanmadi]]', 'Dürüst sınır'))
    h.append(kutu('uyari', 'Anten takılmadan gönderme yapılmamalıdır: çıkış gücü anten yoksa yansıyıp çıkış katına döner (genel mühendislik bilgisi). Ra-01H belgesi görev oranı ve VSWR sınırı vermez; yüksek güçte gönderimde düzenleyici (Şili) sınırlarına ayrıca uyulmalıdır. [[bilgi]]', 'Kullanım şartı'))
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
             '<tr><td>Anten takılı değil</td><td>Yansıyan güç çıkış katına döner; VSWR çok yüksek olur, çıkış katı zarar görebilir. Ra-01H belgesi VSWR sınırı vermez; yonga üreticisi (Semtech) ve RFM95W veri sayfası ≤ 3:1 ister. [[bilgi]]</td></tr>'
             '<tr><td>3,3 V hattında çökme</td><td>Gönderme anında hat modülün alt sınırı olan 1,8 V’a değil, ESP32’nin 3,0 V sınırına yaklaşırsa işlemci sıfırlanır; C8/C9 çökmeyi önler.</td></tr>'
             '<tr><td>Çalışma sıcaklığı</td><td>Ai-Thinker belgesi çalışma sıcaklığını −20…+85 °C (tablo 1.1), önerilen çalışma koşullarında −40…+85 °C verir; iki tablo çelişir, dar olan esas alınmalıdır. [[ds]]</td></tr>'
             '<tr><td>Besleme açılışı</td><td>Güç verildikten sonra SPI’ya başlamadan önce kısa bir süre (SX1276 için 10 ms) beklenmelidir. [[bilgi]]</td></tr>'
             '<tr><td>2,4 GHz ve 915 MHz’in karışması</td><td>İşlemci Wi-Fi/Bluetooth kullanırsa 2,4 GHz’de yayın yapar; 915 MHz’i doğrudan bozmaz, fakat harmonikler ve besleme gürültüsü için ayrı süzgeç gerekebilir. [[tahmin]]</td></tr></table>')
    h.append('<h2>8. Kartta nerede?</h2><p>Modül ile SMA arasındaki hat <b>mümkün olan en kısa ve düz</b> olmalı. Altında toprak düzlemi kesilmemeli; yanında 2–3 iz genişliği kadar boşluk ve toprak delikleri (via çiti) iyi olur.</p>' + pano_kutusu(v, REFS, [(1, 'U4'), (2, 'C8'), (3, 'J2')], 'SMA kart kenarında; modül ona en yakın bölgededir.'))
    h.append('<p>Ölçülen uzaklık: modül merkezi ile SMA arası ≈ <b>%s mm</b>.</p>' % sayi(mesafe(v, 'U4', 'J2'), 3))
    h.append('<h2>9. Kaynaklar</h2><ul class="kaynak"><li>Ai-Thinker Ra-01H Specification V1 (2019): pin tablosu 2.2, ana parametreler tablo 1.1, elektriksel parametreler — bu çalışmada okundu. Ayak izi ölçüleri aynı boyuttaki Ra-01/Ra-02 kullanım kılavuzunun Şekil 6’sından alındı; Ra-01H belgesinde ölçü çizimi yoktur. [[dogrulanmadi]]</li>'
             '<li>Mikroşerit formülü: Hammerstad yaklaşımı (genel mühendislik bilgisi); kart istifi varsayımdır.</li></ul>')
    return ''.join(h)
