import cizim as CZ
from icerik.yardim import *

ID = 'modem'
BASLIK = '8. 4G modem: A7670SA, seviye çevirici, SIM kart ve anten'
OZET = 'Hücresel modemi güvenle açıp kapatmak, 1,8 voltluk seri hattı 3,3 voltluk işlemciye bağlamak, SIM kartı ve açma uçlarını elektrostatik boşalmadan korumak ve anten devresini kurmak.'
REFS = ['U10', 'U8', 'Q3', 'Q4', 'R31', 'R32', 'R33', 'R34', 'C44', 'C45', 'C46', 'C47', 'C48', 'C52', 'C53', 'C54', 'C42', 'C43', 'J7', 'U12', 'U13', 'U14', 'R39', 'R40', 'R41', 'C49', 'R35', 'C50', 'C51', 'J4', 'TP1', 'TP2', 'TP3', 'TP4', 'TP5']

GND_UC = [2, 17, 18, 29, 39, 45, 46, 54, 58, 59, 61, 62, 63, 64, 65] + list(range(69, 89))


def sema_cekirdek(v):
    c = CZ.Cizim('Modem çekirdeği', 1200, 700, v.parca)
    c.bolge(10, 8, 1180, 682, 'A7670SA  —  besleme, denetim uçları, seri hat ve seviye çevirici')
    sol = [([55, 56, 57], 'VBAT'), (1, 'PWRKEY'), (16, 'RESET'), (15, 'VDD_1V8'), (6, 'USB_BOOT')]
    sag = [(9, 'TXD'), (10, 'RXD'), (66, 'STATUS'), (28, 'USB_DM'), (27, 'USB_DP'), (24, 'VBUS'), (23, 'UART_LOG_TX'), (30, 'SIM_VDD'), (33, 'SIM_RST'), (32, 'SIM_CLK'), (31, 'SIM_DATA'), (60, 'RF_ANT')]
    P = c.kutu('U10', 330, 100, sol, sag, alt=[(GND_UC, 'GND (35 uç)')], genislik=170, baslik='A7670SA', pinaralik=26)
    for k, ag in (('55', 'VBAT_MOD'), ('1', 'PWRKEY'), ('16', 'MODEM_RESET')):
        x, y = P[k]; c.tel((x, y), (x - 45, y)); c.etiket(ag, x - 45, y, 'sol')
    x, y = P['15']; c.tel((x, y), (x - 45, y)); c.ray('+1V8', x - 45, y)
    c.toprak(*P['2'])
    Q = c.kutu('U8', 790, 100, [(2, 'A1'), (3, 'A2'), (4, 'A3'), (5, 'A4')], [(13, 'B1'), (12, 'B2'), (11, 'B3'), (10, 'B4')], ust=[(1, 'VCCA'), (8, 'OE'), (14, 'VCCB')], alt=[(7, 'GND')],
               genislik=170, baslik='TXB0104PW', pinaralik=26)
    for k_u, k_q, ag in (('9', '2', 'M_TXD'), ('10', '3', 'M_RXD'), ('66', '4', 'M_STATUS')):
        y = P[k_u][1]
        c.tel((P[k_u][0], y), (630, y), Q[k_q]); c.etiket(ag, 630, y, 'yukari')
    xa, ya = Q['5']; c.tel((xa, ya), (xa - 25, ya)); c.toprak(xa - 25, ya)
    xb, yb = Q['10']; c.tel((xb, yb), (xb + 25, yb)); c.toprak(xb + 25, yb)
    for k, ag, nt in (('13', 'MODEM_RXD_H', 'işlemci IO5'), ('12', 'MODEM_TXD_H', 'IO4'), ('11', 'MODEM_STATUS', 'IO1')):
        x, y = Q[k]; c.tel((x, y), (x + 40, y)); c.etiket(ag, x + 40, y, 'sag'); c.not_(x + 150, y + 4, nt, 'start')
    for k, ray in (('1', '+1V8'), ('8', '+1V8'), ('14', '+3V3')):
        x, y = Q[k]; c.tel((x, y), (x, y - 20)); c.ray(ray, x, y - 20)
    c.toprak(*Q['7'])
    for ref, k in (('TP2', '28'), ('TP3', '27'), ('TP4', '24'), ('TP5', '23')):
        x, y = P[k]
        c.kutu(ref, 585, y - 13, [(1, ref)], [], genislik=44, pinaralik=13, baslik_yok=True)
        c.tel((x, y), (570, y))
    y6 = P['6'][1]
    c.kutu('TP1', 170, y6 - 13, [], [(1, 'TP1')], genislik=44, pinaralik=13, baslik_yok=True)
    c.tel((P['6'][0], y6), (229, y6))
    for k, ag in (('30', 'USIM_VDD'), ('33', 'USIM_RST_M'), ('32', 'USIM_CLK_M'), ('31', 'USIM_DATA_M'), ('60', 'MODEM_ANT')):
        x, y = P[k]; c.tel((x, y), (x + 45, y)); c.etiket(ag, x + 45, y, 'sag')
    c.not_(x + 135, P['30'][1] + 4, '→ SIM kart (devre C)', 'start'); c.not_(x + 135, P['60'][1] + 4, '→ anten devresi (devre C)', 'start')
    by = 520
    c.ray('+1V8', 80, by); c.kondansator('C42', 80, by, 90); c.toprak(80, by + 60)
    c.ray('+3V3', 200, by); c.kondansator('C43', 200, by, 90); c.toprak(200, by + 60)
    c.not_(40, by + 100, 'Seviye çevirici ve modem 1,8 V uçlarının süzgeçleri', 'start')
    c.not_(40, 62, 'TP1–TP5: ölçüm noktaları (USB_BOOT, USB D−, USB D+, USB VBUS, log çıkışı); modem USB’si işlemciye bağlı değil.', 'start')
    c.isaret(1, 290, 76); c.isaret(2, 600, 40); c.isaret(3, 860, 20); c.isaret(4, 80, by + 90)
    return c


def sema_surucu(v):
    c = CZ.Cizim('Modem açma-kapama sürücüleri', 1420, 520, v.parca)
    c.bolge(10, 8, 1400, 502, 'MODEM AÇMA/SIFIRLAMA SÜRÜCÜLERİ, ESD KORUMASI ve BESLEME KONDANSATÖRLERİ')
    for x0, q, rb, rbb, cc, ctl, net, nt in ((160, 'Q3', 'R31', 'R32', 'C44', 'MODEM_PWRKEY_CTL', 'PWRKEY', 'PWRKEY: alçak darbe = aç'),
                                            (600, 'Q4', 'R33', 'R34', 'C45', 'MODEM_RST_CTL', 'MODEM_RESET', 'RESET: alçak darbe = sıfırla')):
        yb = 200
        c.etiket(ctl, x0, yb, 'sol')
        c.tel((x0, yb), (x0 + 20, yb))
        c.direnc(rb, x0 + 20, yb, 0)
        c.tel((x0 + 80, yb), (x0 + 100, yb), (x0 + 120, yb))
        c.etiket(q + '_B', x0 + 100, yb, 'yukari')
        Qd = c.npn(q, x0 + 120, yb)
        r = c.direnc(rbb, x0 + 100, yb, 90)
        c.toprak(*r['b'])
        c.toprak(*Qd['E'])
        c.tel(Qd['C'], (Qd['C'][0], Qd['C'][1] - 30)); c.etiket(net, Qd['C'][0], Qd['C'][1] - 30, 'sag')
        r = c.kondansator(cc, x0 + 290, yb - 60, 90); c.etiket(net, *r['a'], 'sag'); c.toprak(*r['b'])
        c.not_(x0 - 80, 340, nt, 'start')
    for i, ref in enumerate(('C46', 'C47', 'C48', 'C52', 'C53', 'C54')):
        r = c.kondansator(ref, 960 + 70 * i, 150, 90); c.etiket('VBAT_MOD', *r['a'], 'sag'); c.toprak(*r['b'])
    c.not_(950, 250, 'Modem besleme süzgeçleri (33 pF, 10 pF, 100 nF, 100 nF, 1 µF, 10 µF)', 'start')
    U = c.kutu('U13', 1000, 330, [(1, 'IO1'), (3, 'IO2')], [(6, 'IO1'), (4, 'IO2')], ust=[(5, 'VBUS')], alt=[(2, 'GND')], genislik=130, baslik='USBLC6 (PWRKEY, RESET)', pinaralik=26)
    for k, ag in (('1', 'PWRKEY'), ('3', 'MODEM_RESET')):
        x, y = U[k]; c.tel((x, y), (x - 30, y)); c.etiket(ag, x - 30, y, 'sol')
    for k, ag in (('6', 'PWRKEY'), ('4', 'MODEM_RESET')):
        x, y = U[k]; c.tel((x, y), (x + 30, y)); c.etiket(ag, x + 30, y, 'sag')
    x, y = U['5']; c.tel((x, y), (x, y - 20)); c.ray('VBAT_MOD', x, y - 20)
    c.toprak(*U['2'])
    c.isaret(1, 240, 130); c.isaret(2, 410, 250); c.isaret(3, 680, 130); c.isaret(4, 1065, 300)
    return c


def sema_sim_anten(v):
    c = CZ.Cizim('SIM kart ve anten devreleri', 1300, 640, v.parca)
    c.bolge(10, 8, 1280, 622, 'SIM KART (seri direnç + ESD koruma) ve ANTEN DEVRESİ')
    U = c.kutu('U12', 380, 60, [(1, 'IO1'), (3, 'IO2')], [(6, 'IO1'), (4, 'IO2')], ust=[(5, 'VBUS')], alt=[(2, 'GND')], genislik=130, baslik='USBLC6 (RST, CLK)', pinaralik=26)
    for k, ag in (('1', 'USIM_RST'), ('3', 'USIM_CLK')):
        x, y = U[k]; c.tel((x, y), (x - 40, y)); c.etiket(ag, x - 40, y, 'sol')
    for k, ag in (('6', 'USIM_RST'), ('4', 'USIM_CLK')):
        x, y = U[k]; c.tel((x, y), (x + 40, y)); c.etiket(ag, x + 40, y, 'sag')
    x, y = U['5']; c.tel((x, y), (x, y - 20)); c.ray('USIM_VDD', x, y - 20)
    c.toprak(*U['2'])
    W = c.kutu('U14', 380, 230, [(1, 'IO1'), (3, 'IO2', 'nc')], [(6, 'IO1'), (4, 'IO2', 'nc')], ust=[(5, 'VBUS')], alt=[(2, 'GND')], genislik=130, baslik='USBLC6 (DATA)', pinaralik=26)
    x, y = W['1']; c.tel((x, y), (x - 40, y)); c.etiket('USIM_DATA', x - 40, y, 'sol')
    x, y = W['6']; c.tel((x, y), (x + 40, y)); c.etiket('USIM_DATA', x + 40, y, 'sag')
    x, y = W['5']; c.tel((x, y), (x, y - 20)); c.ray('USIM_VDD', x, y - 20)
    c.toprak(*W['2'])
    J = c.kutu('J7', 860, 60, [(1, 'VCC'), (2, 'RST'), (3, 'CLK'), (7, 'I/O'), (5, 'GND'), (6, 'VPP', 'nc')], [], genislik=140, baslik='microSIM yuvası', pinaralik=26)
    for k, ag in (('1', 'USIM_VDD'), ('2', 'USIM_RST'), ('3', 'USIM_CLK'), ('7', 'USIM_DATA')):
        x, y = J[k]; c.tel((x, y), (x - 40, y)); c.etiket(ag, x - 40, y, 'sol')
    c.toprak(*J['5'])
    r = c.kondansator('C49', 120, 100, 90); c.etiket('USIM_VDD', *r['a'], 'sag'); c.toprak(*r['b'])
    c.not_(60, 190, 'SIM besleme süzgeci', 'start')
    for i, (rr, am, ag) in enumerate((('R39', 'USIM_RST_M', 'USIM_RST'), ('R40', 'USIM_CLK_M', 'USIM_CLK'), ('R41', 'USIM_DATA_M', 'USIM_DATA'))):
        y = 400 + 50 * i
        c.etiket(am, 60, y, 'sol'); c.tel((60, y), (100, y)); c.direnc(rr, 100, y, 0); c.tel((160, y), (200, y)); c.etiket(ag, 200, y, 'sag')
    c.not_(40, 380, 'Modemden gelen SIM hatları 22 Ω’la ayrılır (modem tarafı: _M)', 'start')
    ox, ay = 520, 440
    c.etiket('MODEM_ANT', ox + 100, ay, 'sol')
    c.tel((ox + 100, ay), (ox + 170, ay), (ox + 200, ay))
    c.direnc('R35', ox + 200, ay, 0)
    c.tel((ox + 260, ay), (ox + 300, ay), (ox + 370, ay))
    c.nokta(ox + 170, ay); c.nokta(ox + 300, ay)
    c.kondansator('C50', ox + 170, ay, 90); c.toprak(ox + 170, ay + 60)
    c.kondansator('C51', ox + 300, ay, 90); c.toprak(ox + 300, ay + 60)
    J2 = c.kutu('J4', ox + 385, ay - 26, [(1, 'iç iletken')], [], alt=[(2, 'dış kılıf')], genislik=110, baslik='u.FL', pinaralik=26)
    c.toprak(*J2['2'])
    c.etiket('ANT_4G', ox + 335, ay, 'yukari')
    c.not_(ox + 40, ay - 60, 'Ana anten: π (pi) uyum devresi — C50, R35 (0 Ω), C51. C50 ve C51 varsayılan olarak takılmaz (DNP).', 'start')
    c.not_(ox + 40, ay - 42, 'Anten satıcısı değer verirse takılır; yoksa R35 bir köprü gibi kalır. Yardımcı anten yoktur.', 'start')
    c.isaret(1, 560, 50); c.isaret(2, 120, 370); c.isaret(3, ox + 230, ay - 36)
    return c


def uret(ver, ctx):
    v = ver
    cs = [sema_cekirdek(v), sema_surucu(v), sema_sim_anten(v)]
    for k in cs:
        hata = k.denetle(v.aglar)
        assert not hata, (k.ad, hata)
    h = ['<h1>%s</h1><p class="ozet">%s</p>' % (BASLIK, OZET)]
    h.append(kutu('not', '<ul><li>Bir hücresel modem kart üzerinde neleri ister: besleme, açma ucu, sıfırlama, seri hat, SIM, anten.</li><li>Neden 1,8 voltluk bir seri hat 3,3 volta doğrudan bağlanmaz? Seviye çevirici nasıl çalışır?</li>'
                  '<li>Açma tuşunu bir transistörle nasıl taklit ederiz ve neden iç çekmeli uçlara küçük kondansatör konur?</li><li>SIM hatları ve açma uçları neden elektrostatik boşalmaya karşı korunur?</li></ul>', 'Bu bölümde öğreneceklerin:'))
    h.append('<h2>1. Büyük resim</h2><p>A7670SA, SIMCom’un LTE kategori 1 hücresel modem modülüdür (24 × 24 mm, 88 pedli); bir telefon hattı üzerinden internete çıkar. [[ds]] Kart bu modülü bir <i>çevre birimi</i> olarak kullanır: ESP32, modemi seri hat üzerinden AT komutlarıyla yönetir. Modemin dört temel isteği vardır: (1) <b>güçlü besleme</b> (3. bölüm), (2) <b>açma ve sıfırlama uçları</b>, (3) <b>1,8 V seri hat</b>, (4) <b>SIM ve anten</b>.</p>')
    h.append(kutu('not', 'Bu bölümdeki uç numaraları, değerler ve zamanlamalar SIMCom <b>A7670 Series Hardware Design V1.00</b> (2020-06-09) belgesinden okunmuştur; belgenin tablo 1’i A7670SA için GSM 850/900/1800/1900 ve LTE-FDD B1/B2/B3/B4/B5/B7/B8/B28/B66’yı verir (B20 ve TDD yok). [[ds]] Satıcının sattığı <b>LASC / LASE / FASE / MASC</b> son eklerinin ne anlama geldiği SIMCom belgelerinde yazılı değildir; sipariş öncesi satıcıya yazılı sorulmalıdır. [[dogrulanmadi]]', 'Kaynak ve sınır'))
    h.append('<h2>2. Devre A — Modem çekirdeği</h2>' + sema_kutusu(cs[0]))
    h.append(isaretli(['<b>Modem (U10).</b> Sol tarafta besleme ve denetim uçları, sağda seri hat, USB, SIM ve anten. 35 toprak pedinin hepsi toprağa bağlıdır (RF performansı ve ısı için gerekli); kullanılmayan uçlar (GPIO, PCM, I²C vb.) belgenin “kullanılmıyorsa açık bırak” kuralı gereği bağlanmadı. [[ds]]',
                       '<b>Test noktaları (TP1–TP5).</b> SIMCom USB_BOOT, UART_LOG_TX ve (USB bağlantısı yoksa) USB_VBUS, USB_DP, USB_DM için test noktası ayrılmasını ister. [[ds]] Modem USB’si işlemciye bağlı değil; USB hatları 90 Ω ±%10 fark empedansında çizilmelidir. [[ds]] Not: belge ayrıca bir de VDD_1V8 (belgede “VDD_EXT”) test noktası ister; bu kartta ayrı bir test noktası yok, +1V8 hattı C42 pedinden ölçülebilir. [[dogrulanmadi]]',
                       '<b>USB_BOOT (pin 6).</b> Modül açılmadan önce bu uç yüksek (1,8 V) bırakılırsa modül normal başlamaz; bu yüzden uca çekme direnci konmadı, yalnız test noktası var. [[ds]]',
                       '<b>Seviye çevirici (U8, TXB0104).</b> Modemin 1,8 voltluk seri hattını işlemcinin 3,3 voltuna çevirir. A tarafı 1,8 V’a (VCCA), B tarafı 3,3 V’a (VCCB) bağlıdır; VCCA ≤ VCCB olmalıdır. OE ucu etkinleştirmedir (yüksek = açık).',
                       '<b>Süzgeçler (C42: 1,8 V; C43: 3,3 V).</b> Seviye çeviricinin iki besleme ucuna 100 nF.']))
    h.append('<h3>Seviye çevirici neden gerekli?</h3><p>Modemin UART’ı 1,8 V’tur (belge tablo 5 ve tablo 6). [[ds]] Mutlak azami giriş gerilimi 2,1 V’tur; ESP32’nin 3,3 V çıkışı modemin girişine doğrudan bağlanırsa sınırın üstüne çıkar. [[ds]] Ters yönde, ESP32’nin giriş yüksek eşiği 0,75 × 3,3 = 2,475 V’tur [[ds]]; modemin 1,8 V’luk “1” seviyesi bu eşiğin altında kalır ve işlemci bunu “1” okuyamaz. SIMCom iki çözüm gösterir: transistörlü basit çevirici (115200 bit/sn üstü hızlarda önerilmez) ve entegre seviye çevirici. [[ds]] Bu kart TXB0104 kullanır: iki yönlü, otomatik yönlü, hat başına yön ayarı gerekmez. [[ds]]</p>')
    h.append(kutu('uyari', '<b>Veri sayfasından bulunan hata ve düzeltme.</b> TXB0104 veri sayfası (§5.3 dipnot 1): “Kullanılmayan bir G/Ç çiftinin A ve B tarafı <i>aynı durumda tutulmalıdır</i>: ikisi de VCCI’de ya da ikisi de GND’de.” Tasarımın ilk hâlinde kullanılmayan A4 (5. uç) ve B4 (10. uç) açıkta bırakılmıştı; bu şartı çiğner. <b>Düzeltme:</b> iki uç da toprağa bağlandı (şemada gösterilen budur). Veri sayfası ayrıca, yüksek empedans garantisi için OE’nin toprağa bir <i>aşağı çekme direnciyle</i> bağlanmasını önerir; bu kartta OE doğrudan 1,8 V’a bağlıdır: modem kapalıyken VCCA = 0 olduğundan çıkışlar yüksek empedansa geçer, ek direnç şart görülmedi. [[tahmin]]', 'Bulgu'))
    h.append('<h2>3. Devre B — Açma/sıfırlama sürücüleri ve besleme kondansatörleri</h2>' + sema_kutusu(cs[1]))
    h.append(isaretli(['<b>PWRKEY sürücüsü (Q3, R31, R32, C44).</b> Modem, PWRKEY ucu alçak (≤ 0,5 V) tutulunca açılır; uç içeride 50 kΩ ile VBAT’a çekilidir, bu yüzden dışarıdan çekme direnci gerekmez. Açma darbesinin tipik süresi 50 ms’dir. [[ds]] Biz ucu bir NPN transistörün toplayıcısına bağlayarak işlemciden <i>toprağa çekeriz</i>: işlemci tabana yüksek verirse transistör iletir ve PWRKEY alçalır. R31 (1 kΩ) taban akımını sınırlar; R32 (10 kΩ) taban boşta iken transistörü kapalı tutar. <b>C44 yalnız 1 nF’tır:</b> SIMCom, PWRKEY ya da RESET ucuna 10 nF’ın üstünde kondansatör bağlanmamasını ister; aksi hâlde modül VBAT gelince kendiliğinden açılabilir. [[ds]]',
                       '<b>RESET sürücüsü (Q4, R33, R34, C45).</b> Aynı devre RESET ucu için. Belge sıfırlama darbesini 1,5 s önerir ve RESET’in yalnız acil durumda kullanılmasını ister; PWRKEY ve RESET aynı anda alçak tutulmaz. [[ds]]',
                       '<b>VBAT süzgeçleri (C52 33 pF, C53 10 pF, C46 ve C47 100 nF, C54 1 µF, C48 10 µF).</b> SIMCom RF başarımı için VBAT’ın yanında 33 pF / 10 pF / 0,1 µF / 1 µF seramik dörtlüsünü önerir. [[ds]]',
                       '<b>ESD koruması (U13, USBLC6-2SC6).</b> PWRKEY ve RESET uçları insan elinin ulaşabileceği kenara yakındır; SIMCom bu uçlara TVS konmasını ister. [[ds]] Dizinin besleme ucu VBAT_MOD’a bağlıdır; bu uçların mutlak azami gerilimi 4,7 V olduğundan 4,0 V’luk VBAT güvenlidir. [[ds]]']))
    h.append('<h3>Hesap: transistör sürücüsü</h3>')
    i_b = (3.3 - 0.7) / 1000 - 0.7 / 10000
    h.append('<p>İşlemci çıkışı 3,3 V iken taban akımı: I<sub>B</sub> ≈ (3,3 − 0,7)/1 kΩ − 0,7/10 kΩ = <b>%s mA</b> (taban–yayıcı gerilimi ≈ 0,7 V varsayımı). 2N2222 sınıfı bir transistörün akım kazancı ≥ 100 olduğundan toplayıcı akımı birkaç mA’ya kadar kolayca doyar; PWRKEY ucundan akan akım µA mertebesindedir (50 kΩ’luk çekme), yani transistör <i>sert doyma</i>da çalışır ve toplayıcı–yayıcı gerilimi ≈ 0,06–0,2 V olur: bu, modemin “alçak” eşiği olan 0,5 V’un altındadır. [[ds]] [[tahmin]] Benzetim: <code>simulasyon/role_surucu.cir</code> aynı tipte bir sürücüyü (röle için) doğrular: V<sub>CEsat</sub> = 62 mV (genel model). [[tahmin]]</p>' % sayi(i_b * 1e3, 3))
    h.append(hesap('ohm', [2.6, 1000]))
    h.append('<h3>Açılış sırası</h3><table><tr><th>Olay</th><th>Süre</th><th>Kaynak</th></tr>'
             '<tr><td>PWRKEY alçak darbesi (açma)</td><td>tipik 50 ms</td><td>[[ds]] tablo 9</td></tr>'
             '<tr><td>STATUS ucunun yükselmesi (hazır)</td><td>tipik 11,2 s</td><td>[[ds]] tablo 9</td></tr>'
             '<tr><td>UART hazır</td><td>tipik 11,2 s</td><td>[[ds]] tablo 9</td></tr>'
             '<tr><td>USB hazır</td><td>tipik 9 s</td><td>[[ds]] tablo 9</td></tr>'
             '<tr><td>Kapatma için PWRKEY alçak</td><td>en az 2,5 s</td><td>[[ds]] tablo 10</td></tr>'
             '<tr><td>Kapatma sonrası yeniden açmadan önce bekleme</td><td>en az 2 s</td><td>[[ds]] tablo 10</td></tr>'
             '<tr><td>RESET alçak darbesi</td><td>tipik 1,5 s</td><td>[[ds]] tablo 11</td></tr></table>')
    h.append('<h2>4. Devre C — SIM kart ve anten</h2>' + sema_kutusu(cs[2]))
    h.append(isaretli(['<b>SIM yuvası (J7), 22 Ω seri dirençler (R39–R41) ve ESD koruması (U12, U14: USBLC6-2SC6).</b> SIM kart sıkça dışarıdan dokunulan bir arayüzdür. SIMCom’un referans devresinde RST, CLK ve DATA hatlarında 22 Ω seri direnç vardır; ESD koruması yuvaya yakın olmalıdır. [[ds]] Belgenin önerdiği ESDA6V1W5 yerine bu kartta USBLC6-2SC6 kullanıldı (hat başına en çok 3,5 pF; SIM hattı için yeterince küçük). [[tahmin]] VPP ucu bağlı değildir. [[ds]]',
                       '<b>SIM besleme süzgeci (C49: 100 nF).</b> Belgede önerilir. Veri (USIM_DATA) hattı modül içinde 4,7 kΩ ile USIM_VDD’ye çekilidir; dışarıdan direnç gerekmez. USIM_CLK’nin yükselme/düşme süresi çok önemlidir (kısa ve temiz iz). [[ds]]',
                       '<b>Ana anten (π devresi: C50, R35, C51 ve J4).</b> SIMCom antenin ayarlanması ve sertifikasyon için bir RF konnektörü ve uyum devresi ister; R değerleri 0 Ω, C’ler varsayılan olarak boş (anten satıcısı değer verince takılır). Hat 50 Ω olmalı ve anten ile modül arası toplam kayıp 700–960 MHz’de < 0,5 dB, 1710–2170 MHz’de < 0,9 dB, 2300–2650 MHz’de < 1,2 dB olmalıdır. [[ds]] A7670SA’da tek (ana) anten vardır; yardımcı anten ucu yoktur. [[ds]]']))
    h.append('<h2>5. Parça kartları</h2><div class="kartlar">' + ''.join(v.kart_html(r) for r in ['U10', 'U8', 'Q3', 'R31', 'C44', 'C46', 'J7', 'U12', 'U13', 'R39', 'R35', 'C50', 'J4']) + '</div>')
    h.append('<h2>6. Uç durumlar</h2><table><tr><th>Durum</th><th>Ne olur?</th></tr>'
             '<tr><td>Modem açılmadı</td><td>PWRKEY’in alçak kaldığı süre kısa ya da besleme 3,4 V altında. Tipik 11 s beklenmeden STATUS’a bakmak yanıltır. [[ds]]</td></tr>'
             '<tr><td>Besleme darbede çöktü</td><td>VBAT 3,4 V altına inerse RF performansı bozulur ve modül kapanabilir; GSM gönderme darbesi 577 µs boyunca 2,8 A’e çıkar. [[ds]] 3. bölümdeki kondansatörler ve çeviricinin hızı bununla ilgilidir.</td></tr>'
             '<tr><td>Modem kapalı, işlemci açık</td><td>VCCA = 0 olduğundan seviye çevirici çıkışları yüksek empedansa geçer; işlemcinin RX hattı yüzer: yazılım içte aşağı çekme kullanmalı.</td></tr>'
             '<tr><td>SIM kart çıkarıldı</td><td>SIM algılama ucu (SIM_DET) bağlı olmadığından modem durumu AT komutlarıyla öğrenir.</td></tr>'
             '<tr><td>VBAT’ı bağlantıyı keserek kapatmak</td><td>Belge, VBAT’ı koparmadan önce modülün PWRKEY ya da AT+CPOF ile kapatılmasını ister; aksi hâlde flaş zarar görebilir. [[ds]]</td></tr>'
             '<tr><td>Çalışma sıcaklığı</td><td>−30…+80 °C dışında uyarı verir, −40…+85 °C dışında modül kendiliğinden kapanır. [[ds]]</td></tr></table>')
    h.append(kutu('uyari', 'Ölçülen bir sapma: SIMCom, VBAT iz genişliğini <b>en az 2 mm</b> ister [[ds]]; karttaki <code>VBAT_MOD</code> yolu bobinden modüle 41 mm boyunca 1,0 mm, geri kalanında 0,4 mm’dir. Karttan hesaplanan direnç bobinden modülün VBAT pedlerine 18–19 mΩ’dur; 2,8 A’de ≈ 52 mV düşer (3. bölüm benzetimi). Belgenin 300 mV’luk düşüm bütçesinin altındadır, fakat iz genişliği öneriye uymaz. [[tahmin]]', 'Açık sapma'))
    h.append('<h2>7. Kartta nerede?</h2>' + pano_kutusu(v, ['U10', 'U8', 'Q3', 'Q4', 'C46', 'C47', 'C48', 'J7', 'U12', 'U13', 'U14', 'J4', 'R35'], [(1, 'U10'), (2, 'U8'), (3, 'J7'), (4, 'J4')], 'Modem kartın alt tarafında; SIM yuvası arka yüzde, anten konnektörü kenara yakın.'))
    h.append('<h2>8. Kaynaklar</h2><ul class="kaynak"><li>SIMCom A7670 Series Hardware Design V1.00 (2020-06-09): tablo 1 (bantlar), tablo 3 ve 6 (uçlar), §3.1 (besleme, 2,8 A, 300 µF, 2 mm), §3.2 (açma/kapama/sıfırlama, tablo 9–11), §3.3 (UART), §3.4 (USB, USB_BOOT), §3.5 (SIM, 22 Ω), §4.2 (anten), §5.1–5.2 (sınırlar) — bu çalışmada okundu.</li>'
             '<li>TI TXB0104 veri sayfası: pinler ve §5.3 dipnot 1 (kullanılmayan G/Ç) okundu.</li></ul>')
    return ''.join(h)
