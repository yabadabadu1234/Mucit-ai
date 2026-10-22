import math
import cizim as CZ
from icerik.yardim import *

ID = 'islemci'
BASLIK = '5. İşlemci: ayak atamaları ve ortak SPI hattı'
OZET = 'Alıcıda ESP32-S3’ün 21 ayağının görevi: modem, Ethernet, LoRa, röle, düğme ve ışıklar. Üç çipin tek SPI hattını paylaşması ve seçim hatları.'
REFS = ['U1', 'R10', 'C19', 'C20', 'C21', 'SW1', 'R11', 'R12', 'D5', 'R13', 'D6']

SAG = [(27, 'IO0', 'DUGME', 'düğme (aşağıda)'), (39, 'IO1', 'MODEM_STATUS', 'modem durumu'), (38, 'IO2', 'MODEM_EN_CTL', 'modem çeviricisi etkin'),
       (4, 'IO4', 'MODEM_TXD_H', 'modem seri: işlemci gönderir'), (5, 'IO5', 'MODEM_RXD_H', 'modem seri: işlemci alır'), (6, 'IO6', 'MODEM_PWRKEY_CTL', 'modem açma'), (7, 'IO7', 'MODEM_RST_CTL', 'modem sıfırlama'),
       (12, 'IO8', 'LORA_DIO0', 'LoRa kesme 0'), (8, 'IO15', 'LORA_DIO1', 'LoRa kesme 1'), (18, 'IO10', 'LORA_NSS', 'LoRa seçim'), (22, 'IO14', 'LORA_RESET', 'LoRa sıfırlama'),
       (17, 'IO9', 'ETH_CS', 'Ethernet seçim'), (9, 'IO16', 'ETH_INT', 'Ethernet kesme'), (10, 'IO17', 'ETH_RST', 'Ethernet sıfırlama'),
       (19, 'IO11', 'SPI_MOSI', 'ORTAK SPI veri girişi'), (20, 'IO12', 'SPI_SCK', 'ORTAK SPI saat'), (21, 'IO13', 'SPI_MISO', 'ORTAK SPI veri çıkışı'),
       (31, 'IO38', 'ROLE_CTL', 'röle sürücü'), (32, 'IO39', 'LED1_CTL', 'yeşil LED'), (33, 'IO40', 'LED2_CTL', 'kırmızı LED'), (14, 'IO20', 'USB_DP', 'USB D+'), (13, 'IO19', 'USB_DM', 'USB D−')]


def sema(v):
    c = CZ.Cizim('Alıcı işlemci', 1060, 940, v.parca)
    c.bolge(10, 8, 1040, 922, 'İŞLEMCİ  —  ESP32-S3-WROOM-1: ayak atamaları')
    sag = [(n, ad) for n, ad, ag, ac in SAG]
    sol = [(2, '3V3'), (3, 'EN'), ([1, 40, 41], 'GND')]
    P = c.kutu('U1', 400, 50, sol, sag, genislik=170, baslik='ESP32-S3-WROOM-1', pinaralik=28)
    y3, ye, yg = P['2'][1], P['3'][1], P['1'][1]
    c.tel((385, y3), (330, y3)); c.ray('+3V3', 330, y3)
    c.tel((385, ye), (330, ye)); c.etiket('EN', 330, ye, 'sol')
    c.tel((385, yg), (330, yg)); c.toprak(330, yg)
    for n, ad, ag, ac in SAG:
        x, y = P[str(n)]
        c.tel((x, y), (x + 35, y)); c.etiket(ag, x + 35, y, 'sag'); c.not_(x + 215, y + 4, '← ' + ac, 'start')
    by = 410
    r = c.direnc('R10', 60, by, 90); c.ray('+3V3', 60, by); c.etiket('EN', *r['b'], 'sag')
    r = c.kondansator('C19', 150, by + 60, 90); c.etiket('EN', *r['a'], 'sag'); c.toprak(*r['b'])
    c.ray('+3V3', 250, by); c.kondansator('C20', 250, by, 90); c.toprak(250, by + 60)
    c.ray('+3V3', 330, by); c.kondansator('C21', 330, by, 90); c.toprak(330, by + 60)
    c.not_(40, by + 150, 'Sıfırlama gecikmesi ve besleme süzgeçleri', 'start')
    by2 = 620
    c.ray('+3V3', 60, by2); c.direnc('R11', 60, by2, 90)
    r2 = c.dugme('SW1', 60, by2 + 60, 90); c.toprak(*r2['b'])
    c.etiket('DUGME', 60, by2 + 60, 'sag')
    c.etiket('LED1_CTL', 160, 790, 'sol')
    rr = c.direnc('R12', 160, 790, 0)
    c.tel((220, 790), (250, 790))
    c.led('D5', 250, 790, 0)
    c.tel((310, 790), (330, 790)); c.toprak(330, 790)
    c.etiket('LED2_CTL', 160, 850, 'sol')
    c.direnc('R13', 160, 850, 0)
    c.tel((220, 850), (250, 850))
    c.led('D6', 250, 850, 0)
    c.tel((310, 850), (330, 850)); c.toprak(330, 850)
    c.not_(40, 905, 'Düğme (IO0 = indirme kipi düğmesi) ve iki durum ışığı', 'start')
    c.isaret(1, 380, 70); c.isaret(2, 40, by + 40); c.isaret(3, 40, by2 + 40)
    return c


def uret(ver, ctx):
    v = ver
    c = sema(v)
    hata = c.denetle(v.aglar)
    assert not hata, hata
    h = ['<h1>%s</h1><p class="ozet">%s</p>' % (BASLIK, OZET)]
    h.append(kutu('not', '<ul><li>Bir işlemcinin ayaklarını sistematik olarak nasıl atarsın? (Alıcıda 21 sinyal.)</li><li>Üç çipin tek SPI hattını paylaşması: seçim hattı, yüksek empedanslı çıkış, saat hızı.</li><li>ESP32-S3’te JTAG ayaklarının GPIO olarak kullanılması: ne anlama gelir?</li></ul>', 'Bu bölümde öğreneceklerin:'))
    h.append('<h2>1. Büyük resim</h2><p>Alıcıdaki işlemci, vericideki ile aynı modüldür (ESP32-S3-WROOM-1); farkı çevresidir: modem, Ethernet çipi ve LoRa modülü aynı SPI hattında; modem ayrıca seri hat, açma, sıfırlama, durum ve etkinleştirme hatlarıyla bağlanır; röle ve iki ışık eklidir. Sıfırlama devresinin hesabı ve açılış (strapping) uçlarının kuralları <a href="../verici/islemci.html">verici 3. bölümde</a> anlatıldı; burada ayak atamasına odaklanılır.</p>')
    h.append('<h2>2. Şema</h2>' + sema_kutusu(c))
    h.append(isaretli(['<b>İşlemci (U1)</b> ve 22 kullanılan ayak. Sol tarafta besleme, EN ve toprak. Sağ tarafta işlevlerine göre kümelenmiş hatlar.', '<b>Sıfırlama ve besleme süzgeçleri (R10 = 10 kΩ, C19 = 1 µF; C20 = 22 µF, C21 = 100 nF).</b> Aynı değerler ve aynı hesap (τ = 10 ms).', '<b>Düğme (SW1 + R11) ve iki LED (D5 yeşil, D6 kırmızı).</b> R11 = 10 kΩ yukarı çekme; LED dirençleri 470 Ω. Düğme IO0’dadır: basılı iken açılış programlama kipine girer.']))
    h.append('<h2>3. Ayak atama tablosu</h2><table><tr><th>Ayak</th><th>Ad</th><th>Ağ</th><th>Görev</th><th>Neden bu ayak?</th></tr>')
    neden = {27: 'IO0: indirme kipi düğmesi; RTC ayağı.', 39: 'RTC ayağı: modem durumundan işlemci uyandırılabilir.', 38: 'Genel amaçlı; açılış seviyesi önemli değil (R6 modemi varsayılan açık tutar).',
             4: 'Genel amaçlı UART ayakları (bir UART denetleyicisine bağlanır).', 5: 'Genel amaçlı UART ayakları.', 6: 'Genel amaçlı; transistörü sürer.', 7: 'Genel amaçlı; transistörü sürer.',
             12: 'RTC ayağı: kesmeyle uyandırma.', 8: 'RTC ayağı.', 18: 'FSPICS0: SPI2 varsayılan seçim ayağı. [[ds]]', 22: 'Genel.', 17: 'Ayrı seçim hattı.', 9: 'Ethernet kesmesi.', 10: 'Ethernet sıfırlama.',
             19: 'FSPID (MOSI): SPI2 varsayılan. [[ds]]', 20: 'FSPICLK: SPI2 varsayılan. [[ds]]', 21: 'FSPIQ (MISO): SPI2 varsayılan. [[ds]]', 31: 'FSPIWP; genel amaçlı kullanılır.', 32: 'MTCK (JTAG): GPIO olarak kullanıldı.', 33: 'MTDO (JTAG): GPIO olarak kullanıldı.', 14: 'Yerleşik USB D+. [[ds]]', 13: 'Yerleşik USB D−. [[ds]]'}
    for n, ad, ag, ac in SAG:
        h.append('<tr><td>%s</td><td>%s</td><td><code>%s</code></td><td>%s</td><td>%s</td></tr>' % (n, ad, ag, ac, neden.get(n, '')))
    h.append('</table>')
    h.append('<h2>4. Ortak SPI hattı</h2><p>Üç çip (LoRa RFM95W, Ethernet W5500 ve işlemci) iki ayrı seçim hattıyla aynı SPI saat/veri hatlarını paylaşır: bir çip seçilince (NSS/SCSn düşük) diğerinin MISO çıkışı <b>yüksek empedansa</b> geçer, bu yüzden hatta çakışma olmaz. W5500 için bu veri sayfasında açıkça yazılıdır (SCSn yüksek iken MISO yüksek empedans). [[ds]] LoRa modülü için aynı davranış SX127x ailesinin standart özelliğidir [[bilgi]] (RFM95W veri sayfasında SPI zamanlaması verilmiştir; çıkış yüksek empedansı açıkça yazılı değildir; yazılım hatta aynı anda yalnız bir çipi seçmelidir).</p>')
    h.append('<p>Hız: W5500 33,3 MHz garantili, 80 MHz kuramsal [[ds]]; SX1276 SPI’ı en çok 10 MHz’e kadar [[bilgi]]. Aynı saat hattı iki çip için farklı hızda kullanılacaksa yazılım çipe göre saat hızını ayarlar (SPI işlem başına “cihaz” ayarı). İz uzunlukları:</p><table><tr><th>Ağ</th><th>İz uzunluğu</th><th>Delikli geçit</th></tr>')
    for ag in ('SPI_SCK', 'SPI_MOSI', 'SPI_MISO', 'LORA_NSS', 'ETH_CS'):
        h.append('<tr><td><code>%s</code></td><td>%s mm</td><td>%d</td></tr>' % (ag, sayi(iz_uzunlugu(v, ag), 3), viya_sayisi(v, ag)))
    h.append('</table>')
    h.append(kutu('uyari', 'Dürüst not: IO39 (MTCK) ve IO40 (MTDO) ESP32-S3’te JTAG ayaklarıdır ve bu kartta LED sürmek için GPIO olarak kullanıldı. USB üzerinden JTAG zaten yerleşik olduğu için kullanım serbesttir; ancak bu ayaklarla donanım JTAG hata ayıklaması yapılamaz. [[ds]]', 'Not'))
    h.append('<h2>5. Parça kartları</h2><div class="kartlar">' + ''.join(v.kart_html(r) for r in ['U1', 'R10', 'SW1', 'R11', 'R12', 'D5']) + '</div>')
    h.append('<h2>6. Kartta nerede?</h2>' + pano_kutusu(v, REFS, [(1, 'U1'), (2, 'R10'), (3, 'SW1')], 'İşlemci kartın üst kenarına dayanır: kart anteni (modülün bir ucu) boş alana bakar.'))
    h.append('<h2>7. Kaynaklar</h2><ul class="kaynak"><li>ESP32-S3-WROOM-1 veri sayfası v1.8 (ayaklar tablo 3-1, strapping tablo 4-1).</li><li>W5500 veri sayfası v1.1.0 (SPI davranışı).</li></ul>')
    return ''.join(h)
