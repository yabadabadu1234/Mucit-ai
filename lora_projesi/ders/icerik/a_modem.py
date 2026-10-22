import cizim as CZ
from icerik.yardim import *

ID = 'modem'
BASLIK = '8. 4G modem: SIM7600, seviye çevirici, SIM kart ve antenler'
OZET = 'Hücresel modemi güvenle açıp kapatmak, 1,8 voltluk seri hattı 3,3 voltluk işlemciye bağlamak, SIM kartı korumak ve anten devresini kurmak.'
REFS = ['U10', 'U8', 'Q3', 'Q4', 'R31', 'R32', 'R33', 'R34', 'C44', 'C45', 'C46', 'C47', 'C48', 'C42', 'C43', 'J7', 'U12', 'C49', 'R35', 'C50', 'C51', 'J4', 'R36', 'J8', 'TP1', 'TP2', 'TP3']


def sema_cekirdek(v):
    c = CZ.Cizim('Modem çekirdeği', 1200, 640, v.parca)
    c.bolge(10, 8, 1180, 622, 'SIM7600SA  —  besleme, denetim uçları, seri hat ve seviye çevirici')
    sol = [(['38', '39', '62', '63'], 'VBAT'), (3, 'PWRKEY'), (4, 'RESET'), (15, 'VDD_1V8'), (85, 'BOOT_CFG0')]
    sag = [(71, 'TXD'), (68, 'RXD'), (49, 'STATUS'), (12, 'USB_DN'), (13, 'USB_DP'), (20, 'USIM_VDD'), (18, 'USIM_RST'), (19, 'USIM_CLK'), (17, 'USIM_DATA'), (82, 'MAIN_ANT'), (59, 'AUX_ANT')]
    gnd = ['1', '2', '5', '10', '14', '37', '40', '41', '43', '57', '58', '60', '61', '64', '65', '77', '78', '80', '81']
    P = c.kutu('U10', 330, 100, sol, sag, alt=[(gnd, 'GND (19 uç)')], genislik=170, baslik='SIM7600SA', pinaralik=26)
    for k, ag in (('38', 'VBAT_MOD'), ('3', 'PWRKEY'), ('4', 'MODEM_RESET')):
        x, y = P[k]; c.tel((x, y), (x - 45, y)); c.etiket(ag, x - 45, y, 'sol')
    x, y = P['15']; c.tel((x, y), (x - 45, y)); c.ray('+1V8', x - 45, y)
    c.toprak(*P['1'])
    Q = c.kutu('U8', 790, 100, [(2, 'A1'), (3, 'A2'), (4, 'A3'), (5, 'A4')], [(13, 'B1'), (12, 'B2'), (11, 'B3'), (10, 'B4')], ust=[(1, 'VCCA'), (8, 'OE'), (14, 'VCCB')], alt=[(7, 'GND')],
               genislik=170, baslik='TXB0104PW', pinaralik=26)
    for k_u, k_q, ag in (('71', '2', 'M_TXD'), ('68', '3', 'M_RXD'), ('49', '4', 'M_STATUS')):
        y = P[k_u][1]
        c.tel((P[k_u][0], y), (630, y), Q[k_q]); c.etiket(ag, 630, y, 'yukari')
    xa, ya = Q['5']; c.tel((xa, ya), (xa - 25, ya)); c.toprak(xa - 25, ya)
    xb, yb = Q['10']; c.tel((xb, yb), (xb + 25, yb)); c.toprak(xb + 25, yb)
    for k, ag, nt in (('13', 'MODEM_RXD_H', 'işlemci IO5'), ('12', 'MODEM_TXD_H', 'IO4'), ('11', 'MODEM_STATUS', 'IO1')):
        x, y = Q[k]; c.tel((x, y), (x + 40, y)); c.etiket(ag, x + 40, y, 'sag'); c.not_(x + 150, y + 4, nt, 'start')
    for k, ray in (('1', '+1V8'), ('8', '+1V8'), ('14', '+3V3')):
        x, y = Q[k]; c.tel((x, y), (x, y - 20)); c.ray(ray, x, y - 20)
    c.toprak(*Q['7'])
    # test noktalari
    for ref, k, yy in (('TP2', '12', 154), ('TP3', '13', 180)):
        x, y = P[k]
        c.kutu(ref, 585, y - 13, [(1, ref)], [], genislik=44, pinaralik=13, baslik_yok=True)
        c.tel((x, y), (570, y))
    y85 = P['85'][1]
    c.kutu('TP1', 170, y85 - 13, [], [(1, 'TP1')], genislik=44, pinaralik=13, baslik_yok=True)
    c.tel((P['85'][0], y85), (229, y85))
    # sim ve anten etiketleri
    for k, ag in (('20', 'USIM_VDD'), ('18', 'USIM_RST'), ('19', 'USIM_CLK'), ('17', 'USIM_DATA'), ('82', 'MODEM_ANT'), ('59', 'MODEM_AUX')):
        x, y = P[k]; c.tel((x, y), (x + 45, y)); c.etiket(ag, x + 45, y, 'sag')
    c.not_(x + 135, P['20'][1] + 4, '→ SIM kart (devre C)', 'start'); c.not_(x + 135, P['82'][1] + 4, '→ anten devresi (devre C)', 'start')
    by = 460
    c.ray('+1V8', 80, by); c.kondansator('C42', 80, by, 90); c.toprak(80, by + 60)
    c.ray('+3V3', 200, by); c.kondansator('C43', 200, by, 90); c.toprak(200, by + 60)
    c.not_(40, by + 100, 'Seviye çevirici ve modem 1,8 V uçlarının süzgeçleri', 'start')
    c.not_(40, 62, 'TP1–TP3: ölçüm noktaları (BOOT_CFG0, USB D−, USB D+); modem USB’si şimdilik işlemciye bağlı değil.', 'start')
    c.isaret(1, 290, 76); c.isaret(2, 600, 40); c.isaret(3, 860, 20); c.isaret(4, 80, by + 90)
    return c


def sema_surucu(v):
    c = CZ.Cizim('Modem açma-kapama sürücüleri', 1220, 420, v.parca)
    c.bolge(10, 8, 1200, 402, 'MODEM AÇMA/SIFIRLAMA SÜRÜCÜLERİ ve BESLEME KONDANSATÖRLERİ')
    for x0, q, rb, rbb, cc, ctl, net, nt in ((160, 'Q3', 'R31', 'R32', 'C44', 'MODEM_PWRKEY_CTL', 'PWRKEY', 'PWRKEY: ≥ 100 ms alçak = aç'),
                                            (600, 'Q4', 'R33', 'R34', 'C45', 'MODEM_RST_CTL', 'MODEM_RESET', 'RESET: 50–500 ms alçak = sıfırla')):
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
    for i, ref in enumerate(('C46', 'C47', 'C48')):
        r = c.kondansator(ref, 960 + 80 * i, 150, 90); c.etiket('VBAT_MOD', *r['a'], 'sag'); c.toprak(*r['b'])
    c.not_(950, 250, 'Modem besleme süzgeçleri', 'start')
    c.isaret(1, 240, 130); c.isaret(2, 410, 250); c.isaret(3, 680, 130)
    return c


def sema_sim_anten(v):
    c = CZ.Cizim('SIM kart ve anten devreleri', 1100, 580, v.parca)
    c.bolge(10, 8, 1080, 562, 'SIM KART (ESD korumalı) ve ANTEN DEVRELERİ')
    U = c.kutu('U12', 380, 60, [(5, 'IO4'), (1, 'IO1'), (3, 'IO2'), (4, 'IO3'), (6, 'IO5', 'nc')], [], alt=[(2, 'GND')], genislik=130, baslik='ESDA6V1-5SC6', pinaralik=26)
    for k, ag in (('5', 'USIM_VDD'), ('1', 'USIM_RST'), ('3', 'USIM_CLK'), ('4', 'USIM_DATA')):
        x, y = U[k]; c.tel((x, y), (x - 40, y)); c.etiket(ag, x - 40, y, 'sol')
    c.toprak(*U['2'])
    J = c.kutu('J7', 760, 60, [(1, 'VCC'), (2, 'RST'), (3, 'CLK'), (7, 'I/O'), (5, 'GND'), (6, 'VPP', 'nc')], [], genislik=140, baslik='microSIM yuvası', pinaralik=26)
    for k, ag in (('1', 'USIM_VDD'), ('2', 'USIM_RST'), ('3', 'USIM_CLK'), ('7', 'USIM_DATA')):
        x, y = J[k]; c.tel((x, y), (x - 40, y)); c.etiket(ag, x - 40, y, 'sol')
    c.toprak(*J['5'])
    r = c.kondansator('C49', 120, 100, 90); c.etiket('USIM_VDD', *r['a'], 'sag'); c.toprak(*r['b'])
    c.not_(60, 190, 'SIM besleme süzgeci', 'start')
    ay = 340
    for y, ant_in, r_ref, ant_out, j_ref, c1, c2 in ((ay, 'MODEM_ANT', 'R35', 'ANT_4G', 'J4', 'C50', 'C51'), (ay + 130, 'MODEM_AUX', 'R36', 'ANT_AUX', 'J8', None, None)):
        c.etiket(ant_in, 100, y, 'sol')
        c.tel((100, y), (170, y), (200, y))
        c.direnc(r_ref, 200, y, 0)
        c.tel((260, y), (300, y), (370, y))
        if c1:
            c.nokta(170, y); c.nokta(300, y)
            c.kondansator(c1, 170, y, 90); c.toprak(170, y + 60)
            c.kondansator(c2, 300, y, 90); c.toprak(300, y + 60)
        J2 = c.kutu(j_ref, 385, y - 26, [(1, 'iç iletken')], [], alt=[(2, 'dış kılıf')], genislik=110, baslik='u.FL', pinaralik=26)
        # J2'nin pin x=330, y = y
        c.toprak(*J2['2'])
    c.etiket('ANT_4G', 335, ay, 'yukari'); c.etiket('ANT_AUX', 335, ay + 130, 'yukari')
    c.not_(560, ay - 10, 'Ana anten: π (pi) uyum devresi — C50, R35 (0 Ω), C51. C50 ve C51 varsayılan olarak takılmaz (DNP).', 'start')
    c.not_(560, ay + 10, 'Anten satıcısı değer verirse takılır; yoksa R35 bir köprü gibi kalır.', 'start')
    c.not_(560, ay + 130, 'Yardımcı anten: R36 ve J8 varsayılan olarak takılmaz; istenirse eklenir.', 'start')
    c.isaret(1, 560, 50); c.isaret(2, 120, ay - 30); c.isaret(3, 230, ay - 36)
    return c


def uret(ver, ctx):
    v = ver
    cs = [sema_cekirdek(v), sema_surucu(v), sema_sim_anten(v)]
    for k in cs:
        hata = k.denetle(v.aglar)
        assert not hata, (k.ad, hata)
    h = ['<h1>%s</h1><p class="ozet">%s</p>' % (BASLIK, OZET)]
    h.append(kutu('not', '<ul><li>Bir hücresel modem kart üzerinde neleri ister: besleme, açma ucu, sıfırlama, seri hat, SIM, anten.</li><li>Neden 1,8 voltluk bir seri hat 3,3 volta doğrudan bağlanmaz? Seviye çevirici nasıl çalışır?</li>'
                  '<li>Açma tuşunu bir transistörle nasıl taklit ederiz?</li><li>Veri sayfası okuyarak tasarımdaki bir hatayı bulmak: bu bölümde gerçek bir tane bulundu ve düzeltildi.</li></ul>', 'Bu bölümde öğreneceklerin:'))
    h.append('<h2>1. Büyük resim</h2><p>SIM7600SA, SIMCom’un LTE kategori 1 hücresel modem modülüdür; bir telefon hattı üzerinden internete çıkar. Kart bu modülü bir <i>çevre birimi</i> olarak kullanır: ESP32, modemi seri hat üzerinden AT komutlarıyla yönetir. Modemin dört temel isteği vardır: (1) <b>güçlü besleme</b> (3. bölüm), (2) <b>açma ve sıfırlama uçları</b>, (3) <b>1,8 V seri hat</b>, (4) <b>SIM ve anten</b>.</p>')
    h.append(kutu('uyari', 'Bu bölümdeki modem özellikleri SIMCom <b>SIM7600E/E-H</b> donanım belgesinden okunmuştur (SA/SA-H belgesi bulunamadı). Uç numaraları ve elektriksel değerler aynı aileden olduğu için aynı varsayıldı; <b>SA/SA-H uç düzeni sipariş öncesi kendi belgesiyle teyit edilmelidir</b>. [[dogrulanmadi]]', 'Önemli sınır'))
    h.append('<h2>2. Devre A — Modem çekirdeği</h2>' + sema_kutusu(cs[0]))
    h.append(isaretli(['<b>Modem (U10).</b> Sol tarafta besleme ve denetim uçları, sağda seri hat, USB, SIM ve antenler. 19 toprak ucunun hepsi toprağa bağlıdır (RF performansı için gerekli).',
                       '<b>Test noktaları (TP2, TP3).</b> Modemin USB D− ve D+ uçları işlemciye bağlanmadı; tanı için ölçüm noktası olarak çıkarıldı. Modem USB’si 90 Ω ±%10 fark empedansında çizilmelidir. [[ds]]',
                       '<b>Seviye çevirici (U8, TXB0104).</b> Modemin 1,8 voltluk seri hattını işlemcinin 3,3 voltuna çevirir. A tarafı 1,8 V’a (VCCA), B tarafı 3,3 V’a (VCCB) bağlıdır; VCCA ≤ VCCB olmalıdır. OE ucu etkinleştirmedir (yüksek = açık).',
                       '<b>Süzgeçler (C42: 1,8 V; C43: 3,3 V).</b> Seviye çeviricinin iki besleme ucuna 100 nF.']))
    h.append('<h3>Seviye çevirici neden gerekli?</h3><p>Modemin UART’ı 1,8 V’tur; veri sayfası, 3,3 V’luk bir devreye bağlamak için seviye çevirici istemeye açıkça belirtir ve TXB0108’i önerir. [[ds]] ESP32’nin giriş yüksek eşiği 0,75 × 3,3 = 2,475 V’tur [[ds]]; modemin 1,8 V’luk “1” seviyesi (yaklaşık 1,8 V) bu eşiğin altında kalır ve doğrudan bağlansa işlemci bunu “1” olarak okuyamazdı. Ters yönde de ESP32’nin 3,3 V çıkışı modemin 1,8 V girişine zarar verebilir. TXB0104 iki yönlü, otomatik yönlü bir çeviricidir; hat başına yön ayarı gerekmez. [[ds]]</p>')
    h.append(kutu('uyari', '<b>Veri sayfasından bulunan hata ve düzeltme.</b> TXB0104 veri sayfası (§5.3 dipnot 1): “Kullanılmayan bir G/Ç çiftinin A ve B tarafı <i>aynı durumda tutulmalıdır</i>: ikisi de VCCI’de ya da ikisi de GND’de.” Tasarımın ilk hâlinde kullanılmayan A4 (5. uç) ve B4 (10. uç) açıkta bırakılmıştı; bu, şartı çiğner (ucu havada bırakmak çıkışın salınmasına ya da gereksiz akıma yol açabilir). <b>Düzeltme:</b> iki uç da toprağa bağlandı (şemada gösterilen budur). Bu değişiklik alıcı kartının bağlantı listesine işlendi; kartın yönlendirmesi yeniden üretilince iki uç için iz eklenir. Ayrıca veri sayfası, yüksek empedans garantisi için OE’nin yer yerine bir <i>aşağı çekme direnciyle</i> toprağa bağlanmasını önerir; bu kartta OE doğrudan 1,8 V’a bağlıdır: modem kapalıyken VCCA = 0 olduğundan çıkışlar zaten yüksek empedanslıdır (VCC yalıtımı özelliği) [[ds]], bu nedenle ek direnç şart görülmedi. [[tahmin]]', 'Bulgu'))
    h.append('<h2>3. Devre B — Açma/sıfırlama sürücüleri</h2>' + sema_kutusu(cs[1]))
    h.append(isaretli(['<b>PWRKEY sürücüsü (Q3, R31, R32, C44).</b> Modem, PWRKEY ucu yaklaşık 100–500 ms boyunca alçak (≤ 0,5 V) tutulunca açılır; uç içeride 1,8 V’a çekilidir. [[ds]] Biz ucu, bir NPN transistörün toplayıcısına bağlayarak işlemciden <i>toprağa çekeriz</i>: işlemci tabana yüksek verirse transistör iletir ve PWRKEY alçalır. R31 (1 kΩ) taban akımını sınırlar; R32 (10 kΩ) taban boşta iken transistörü kapalı tutar; C44 gürültüyü ve statik boşalmayı süzer (veri sayfası 100 nF önerir). [[ds]]',
                       '<b>RESET sürücüsü (Q4, R33, R34, C45).</b> Aynı devre, RESET ucu için: 50–500 ms alçak = acil sıfırlama. [[ds]]',
                       '<b>VBAT süzgeçleri (C46, C47: 100 nF; C48: 10 µF).</b> Modem VBAT ayaklarına en yakın yüksek frekans kondansatörleri (SIMCom önerisi 0,1/1 µF, ayaklara yakın). [[ds]]']))
    h.append('<h3>Hesap: transistör sürücüsü</h3>')
    i_b = (3.3 - 0.7) / 1000 - 0.7 / 10000
    h.append('<p>İşlemci çıkışı 3,3 V iken taban akımı: I<sub>B</sub> ≈ (3,3 − 0,7)/1 kΩ − 0,7/10 kΩ = <b>%s mA</b> (taban–yayıcı gerilimi ≈ 0,7 V varsayımı). 2N2222 sınıfı bir transistörün akım kazancı ≥ 100 olduğundan toplayıcı akımı birkaç mA’ya kadar kolayca doyar; PWRKEY ucundan akan akım µA mertebesindedir, yani transistör <i>sert doyma</i>da çalışır ve toplayıcı–yayıcı gerilimi ≈ 0,06–0,2 V olur: bu, modemin “alçak” eşiği olan 0,5 V’un altındadır. [[ds]] [[tahmin]] Benzetim: <code>simulasyon/role_surucu.cir</code> aynı tipte bir sürücüyü (röle için) doğrular: V<sub>CEsat</sub> = 62 mV (genel model). [[tahmin]]</p>' % sayi(i_b * 1e3, 3))
    h.append(hesap('ohm', [2.6, 1000]))
    h.append('<h3>Açılış sırası</h3><table><tr><th>Olay</th><th>Süre</th><th>Kaynak</th></tr>'
             '<tr><td>PWRKEY alçak darbesi</td><td>100–500 ms</td><td>[[ds]] tablo 8</td></tr>'
             '<tr><td>STATUS ucunun yükselmesi (hazır)</td><td>≈ 12–13 s sonra</td><td>[[ds]] tablo 8</td></tr>'
             '<tr><td>UART hazır</td><td>≈ 11–12 s</td><td>[[ds]]</td></tr>'
             '<tr><td>Kapatma için PWRKEY alçak</td><td>≥ 2,5 s</td><td>[[ds]] tablo 9</td></tr>'
             '<tr><td>RESET alçak darbesi</td><td>50–500 ms (tipik 100)</td><td>[[ds]] tablo 10</td></tr></table>')
    h.append('<h2>4. Devre C — SIM kart ve antenler</h2>' + sema_kutusu(cs[2]))
    h.append(isaretli(['<b>SIM yuvası (J7) ve ESD koruması (U12, ESDA6V1-5SC6).</b> SIM kart sıkça dışarıdan dokunulan bir arayüzdür. Koruma dizisi dört hatta (besleme, sıfırlama, saat, veri) konur ve yuvaya <b>yakın</b> olmalıdır. [[ds]] VPP ucu bağlı değildir.',
                       '<b>SIM besleme süzgeci (C49: 100 nF).</b> Veri sayfasında önerilir. Veri (USIM_DATA) hattı modem içinde 10 kΩ ile USIM_VDD’ye çekilidir; dışarıdan direnç gerekmez. Saat hattının yükselme/düşme süresi 40 ns’den kısa olmalıdır (kısa ve temiz iz). [[ds]]',
                       '<b>Ana anten (π devresi: C50, R35, C51 ve J4).</b> SIMCom antenin ayarlanması ve sertifikasyon için bir RF konnektörü ve uyum devresi ister; R değerleri 0 Ω, C’ler varsayılan olarak boş (anten satıcısı değer verince takılır). Hat 50 Ω olmalı ve anten kaybı 700–960 MHz’de < 0,5 dB, 1710–2170 MHz’de < 0,9 dB, 2300–2650 MHz’de < 1,2 dB olmalıdır. [[ds]] İkinci (yardımcı) anten, özellikle yüksek TDD bantlarında duyarlılık için tavsiye edilir; bu kartta isteğe bağlı olarak bırakıldı (R36, J8 takılmaz). [[ds]]']))
    h.append('<h2>5. Parça kartları</h2><div class="kartlar">' + ''.join(v.kart_html(r) for r in ['U10', 'U8', 'Q3', 'R31', 'C44', 'C46', 'J7', 'U12', 'R35', 'C50', 'J4']) + '</div>')
    h.append('<h2>6. Uç durumlar</h2><table><tr><th>Durum</th><th>Ne olur?</th></tr>'
             '<tr><td>Modem açılmadı</td><td>PWRKEY’in alçak kaldığı süre kısa ya da besleme 3,4 V altında. 12 s beklenmeden STATUS’a bakmak yanıltır.</td></tr>'
             '<tr><td>Besleme darbede çöktü</td><td>VBAT 3,4 V altına inerse RF performansı bozulur; 3. bölümdeki çıkış kondansatörü ve 2 mm’lik iz kuralı bununla ilgilidir. [[ds]]</td></tr>'
             '<tr><td>Modem kapalı, işlemci açık</td><td>VCCA = 0 olduğundan seviye çevirici çıkışları yüksek empedansa geçer; işlemcinin RX hattı yüzer: yazılım içte aşağı çekme kullanmalı.</td></tr>'
             '<tr><td>SIM kart çıkarıldı</td><td>SIM algılama ucu bağlı olmadığından modem durumu AT komutlarıyla öğrenir.</td></tr>'
             '<tr><td>Çalışma sıcaklığı</td><td>−30…+80 °C dışında uyarı, −40…+85 °C dışında modem kendiliğinden kapanır. [[ds]]</td></tr></table>')
    h.append(kutu('uyari', 'Ölçülen bir sorun: SIMCom, VBAT iz genişliğini <b>2 mm’den geniş</b> ister [[ds]]; karttaki <code>VBAT_MOD</code> izleri 0,4 mm çizilmiştir. Bu, alıcı kartının açık işidir (iz denetim tablosu 3. bölümde).', 'Açık iş'))
    h.append('<h2>7. Kartta nerede?</h2>' + pano_kutusu(v, ['U10', 'U8', 'Q3', 'Q4', 'C46', 'C47', 'C48', 'J7', 'U12', 'J4', 'R35'], [(1, 'U10'), (2, 'U8'), (3, 'J7'), (4, 'J4')], 'Modem kartın alt tarafında; SIM yuvası arka yüzde, anten konnektörleri kenara yakın.'))
    h.append('<h2>8. Kaynaklar</h2><ul class="kaynak"><li>SIMCom SIM7600E/E-H Hardware Design V1.02: §3.1 (besleme), §3.2 (açma/kapama/sıfırlama), §3.3 (UART), §3.5 (USIM), §4.2 (anten) okundu. SA/SA-H için aynı ailenin değerleri varsayıldı.</li>'
             '<li>TI TXB0104 veri sayfası: pinler ve §5.3 dipnot 1 (kullanılmayan G/Ç) okundu.</li></ul>')
    return ''.join(h)
