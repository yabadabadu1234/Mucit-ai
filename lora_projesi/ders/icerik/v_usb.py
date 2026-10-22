import cizim as CZ
from icerik.yardim import *

ID = 'usb'
BASLIK = '2. USB-C: programlama, 5 volt ve koruma'
OZET = 'USB-C soketinin uçları ne işe yarar, iki direnç neden 5,1 kΩ, veri hatları neden iki uçtan alınır, statik elektrikten nasıl korunur.'
REFS = ['J1', 'R9', 'R10', 'U3']


def sema(v, r1='R9', r2='R10', esd='U3'):
    c = CZ.Cizim('USB-C şeması', 1000, 410, v.parca)
    c.bolge(10, 8, 980, 392, 'USB-C  —  güç, tanıtım dirençleri ve veri hatları')
    P = c.kutu('J1', 60, 60, [], [(['A4', 'B4', 'A9', 'B9'], 'VBUS'), ('A5', 'CC1'), ('B5', 'CC2'), (['A6', 'B6'], 'D+'), (['A7', 'B7'], 'D−'),
                                   (['A1', 'B1', 'A12', 'B12', 'S1'], 'GND / kılıf')], genislik=140, baslik='USB-C soket', pinaralik=40)
    ex = 215
    yv, y1, y2, yp, ym, yg = [P[k][1] for k in ('A4', 'A5', 'B5', 'A6', 'A7', 'A1')]
    Q = c.kutu(esd, 440, yp - 40, [(1, 'I/O1'), (3, 'I/O2')], [(6, 'I/O1'), (4, 'I/O2')], ust=[(5, 'VBUS')], alt=[(2, 'GND')], genislik=150, baslik='USBLC6-2SC6', pinaralik=40)
    c.ic_bag((esd, '1'), (esd, '6')); c.ic_bag((esd, '3'), (esd, '4'))
    # VBUS
    c.tel((ex, yv), (330, yv), (Q['5'][0], yv), (Q['5'][0], Q['5'][1]))
    c.etiket('VBUS', 330, yv - 6, 'yukari')
    c.not_(520, yv - 8, 'D2 diyoduna gider (1. bölüm)', 'start')
    # CC dirençleri
    c.direnc(r1, ex, y1, 0)
    c.tel((ex + 60, y1), (ex + 85, y1)); c.toprak(ex + 85, y1)
    c.direnc(r2, ex, y2, 0)
    c.tel((ex + 60, y2), (ex + 85, y2)); c.toprak(ex + 85, y2)
    # veri hatlari
    c.tel((ex, yp), (300, yp), (Q['1'][0], yp))
    c.etiket('USB_DP', 300, yp, 'yukari')
    c.tel((ex, ym), (300, ym), (Q['3'][0], ym))
    c.etiket('USB_DM', 300, ym, 'yukari')
    c.tel((Q['6'][0], yp), (760, yp)); c.tel((Q['4'][0], ym), (760, ym))
    c.etiket('USB_DP', 760, yp, 'sag'); c.etiket('USB_DM', 760, ym, 'sag')
    c.not_(840, yp + 4, '→ işlemci IO20 (D+)', 'start'); c.not_(840, ym + 4, '→ işlemci IO19 (D−)', 'start')
    c.tel((ex, yg), (245, yg)); c.toprak(245, yg)
    c.toprak(Q['2'][0], Q['2'][1])
    c.not_(60, 392, 'Gerçek soketin A ve B satırı uçları ayrı ayrı lehimlenir; kartta aynı ağa bağlanır. Koruma çipinde 1–6 ve 3–4 uçları içeriden bağlıdır (kesikli çizgi).', 'start')
    c.isaret(1, 40, 100); c.isaret(2, ex + 130, y1 + 20); c.isaret(3, Q['5'][0] + 40, Q['5'][1] + 10); c.isaret(4, 370, yp - 24)
    return c


def uret(ver, ctx):
    v = ver
    c = sema(v)
    hata = c.denetle(v.aglar)
    assert not hata, hata
    h = ['<h1>%s</h1><p class="ozet">%s</p>' % (BASLIK, OZET)]
    h.append(kutu('not', '<ul><li>USB-C soketinde hangi uç ne iş yapar?</li><li>Neden iki adet 5,1 kΩ direnç gerekir? Gerilim bölücü olarak hesabı.</li>'
                  '<li>Veri hatları neden iki ayrı uçtan alınır?</li><li>Statik elektrik koruması nereye, neden oraya konur?</li><li>Kart üzerinde USB izleri nasıl olmalı?</li></ul>', 'Bu bölümde öğreneceklerin:'))
    h.append('<h2>1. Büyük resim</h2><p>Bu kartta USB-C iki iş yapar: (1) bilgisayara bağlanıp işlemciyi programlamak (ESP32-S3’ün yerleşik USB’si doğrudan D+ ve D− uçlarına bağlanır; ek bir çevirici çip yoktur), '
             '(2) 5 volt vermek: bu 5 volt D2 diyodu üzerinden çeviriciye girer (1. bölüm). Kart yalnız <i>cihaz</i> tarafıdır: bilgisayardan güç <i>alır</i>, başkasına güç vermez.</p>')
    h.append('<h2>2. Şema</h2>')
    h.append(sema_kutusu(c))
    h.append(isaretli([
        '<b>USB-C soketi (J1).</b> 16 uçlu USB 2.0 sürümü: dört VBUS (5 V), iki CC (yapılandırma), D+ ve D− birer çift (soket ters takılabildiği için her iki satırda da vardır), beş toprak ucu (A1, B1, A12, B12 ve kılıf S1). Boşta kalan iki uç SBU1 ve SBU2’dir (bu kartta kullanılmaz).',
        '<b>CC dirençleri (R9, R10: 5,1 kΩ).</b> Kaynak (bilgisayar/şarj aleti) CC hattından cihazın var olduğunu ve ne tür cihaz olduğunu anlar. 5,1 kΩ toprağa çekilen direnç “ben bir tüketiciyim (sink), 5 V ver” demektir. İki ayrı direnç gerekir, çünkü fiş hangi yönde takılırsa takılsın yalnız CC1 ya da CC2’den biri kabloya ulaşır.',
        '<b>Koruma (U3, USBLC6-2SC6).</b> Soket ile işlemci arasındaki veri hatlarını statik boşalmadan korur. Sok­ete mümkün olduğunca yakın durur. VBUS ucu bağlıdır: koruma bu uçtan da yararlanır.',
        '<b>Veri hatları.</b> Her iki satırdaki D+ uçları (A6, B6) tek ağ <code>USB_DP</code>, D− uçları (A7, B7) tek ağ <code>USB_DM</code>’dir. Şemada bu hatlar korumaya yan yana (paralel) bağlı çizildi; yerleşimde koruma çipinin içinden geçirilir (1→6, 3→4).']))
    h.append('<h2>3. Hesap: CC hattındaki gerilim bölücü</h2>')
    h.append('<p>Kaynak CC hattına bir <b>yukarı çekme akımı/direnci (Rp)</b> verir; cihazın 5,1 kΩ’u (Rd) toprağa çeker. Ortadaki gerilim bir bölücüdür: <i>V<sub>CC</sub> = 5 V × Rd / (Rp + Rd)</i>. Kaynağın Rp değeri, kaynağın verebileceği akımı bildirir [[bilgi]]:</p>'
             '<table><tr><th>Kaynağın duyurduğu</th><th>Rp</th><th>V<sub>CC</sub> (Rd = 5,1 kΩ)</th></tr>'
             '<tr><td>Varsayılan USB akımı (500/900 mA)</td><td>56 kΩ</td><td>%s V</td></tr>'
             '<tr><td>1,5 A</td><td>22 kΩ</td><td>%s V</td></tr><tr><td>3 A</td><td>10 kΩ</td><td>%s V</td></tr></table>' % (
                 sayi(5 * 5.1 / (56 + 5.1), 3), sayi(5 * 5.1 / (22 + 5.1), 3), sayi(5 * 5.1 / (10 + 5.1), 3)))
    h.append(hesap('bolucu', [5, 56000, 5100]))
    h.append('<p>Bu kartta <b>5 V’tan en çok 500 mA</b> çekeceğimizi varsayıyoruz (bilgisayar portu için güvenli varsayılan). Kart yalnız 3,3 V’ta ≈ 0,3 A hattı kurduğu için, 5 V tarafında verimle ≈ 0,2 A’den az çeker. [[tahmin]]</p>')
    h.append(alistirma('Rd olarak 5,1 kΩ yerine 10 kΩ koysaydın, 56 kΩ’luk bir kaynakta V<sub>CC</sub> kaç volt olurdu ve ne olabilirdi?',
                       'V<sub>CC</sub> = 5 × 10 / (56 + 10) = %s V. Kaynak bu gerilimi “cihaz var” aralığının dışında görebilir (Rd toleransı ±%%20, değer aralığının dışı) ve 5 V vermeyebilirsin. Tanıtım direnci standarttır; değiştirme.' % sayi(5 * 10 / 66, 3)))
    h.append('<h2>4. Veri hatları ve koruma</h2>')
    dp = iz_uzunlugu(v, 'USB_DP'); dm = iz_uzunlugu(v, 'USB_DM')
    h.append('<p>USB 2.0 tam hızda (12 Mbit/sn) D+ ve D− bir <b>fark çifti</b>dir; özellik, çiftin farksal empedansının 90 Ω olmasını ister [[bilgi]]. Tam hızda kısa iz (birkaç cm) ve iki hattın aynı uzunlukta olması yeterlidir. '
             'Bizim kartta ölçülen iz uzunlukları (yalnız bakır izler, delikler ve ped içleri hariç): USB_DP ≈ <b>%s mm</b>, USB_DM ≈ <b>%s mm</b>, fark ≈ %s mm; delikli geçit sayıları %d ve %d.</p>' % (
                 sayi(dp, 3), sayi(dm, 3), sayi(abs(dp - dm), 3), viya_sayisi(v, 'USB_DP'), viya_sayisi(v, 'USB_DM')))
    h.append(kutu('ipucu', 'Koruma çipi (U3) konnektörden (J1) %s mm uzaktadır. Kural: koruma, boşalma enerjisini kartın içine girmeden toprağa akıtabilsin diye soketin hemen yanında olmalı; boşalma akımı korumadan <i>önce</i> bakırda yol almamalıdır.' % sayi(mesafe(v, 'J1', 'U3'), 3), 'Ölçü'))
    h.append('<h2>5. Parça kartları</h2><div class="kartlar">' + ''.join(v.kart_html(r) for r in REFS) + '</div>')
    h.append('<h2>6. Bağlantılar</h2>' + ag_tablosu(v, ['VBUS', 'CC1', 'CC2', 'USB_DP', 'USB_DM'], {'VBUS': '5 V giriş', 'CC1': 'Kablo yönü/tanıtım 1', 'CC2': 'Kablo yönü/tanıtım 2', 'USB_DP': 'Veri +', 'USB_DM': 'Veri −'}))
    h.append('<h2>7. Uç durumlar</h2><table><tr><th>Durum</th><th>Ne olur?</th></tr>'
             '<tr><td>Kablo ters takılı</td><td>CC1 yerine CC2 kabloya ulaşır; iki direnç olduğu için çalışır. D+ ve D− iki satırdan da alındığı için veri de çalışır.</td></tr>'
             '<tr><td>A→C kablo ile bilgisayara takıldı</td><td>CC hattı kablodan gelen 56 kΩ ile çekilir; 5 V verilir. Bu kart için en yaygın durum.</td></tr>'
             '<tr><td>C→C kablo ve şarj aleti</td><td>CC dirençleri bulunduğu için kaynak 5 V verir; dirençler olmazsa güç hiç gelmez.</td></tr>'
             '<tr><td>Fiş takılırken ani akım</td><td>USB 2.0 belirtimi cihaz tarafındaki kapasiteyi 10 µF ile sınırlar [[bilgi]]; kartın VIN ağındaki C1 10 µF ve C2 0,1 µF’dır, sınırdadır. Çıkış tarafı çeviricinin yumuşak başlatmasıyla ayrılmıştır.</td></tr>'
             '<tr><td>Fiş takılırken gerilim aşımı</td><td>Uzun kablonun endüktansı ve kondansatör rezonans yapıp VBUS’ta 5 V’un üstüne (tipik 2 katına kadar) çıkarabilir [[tahmin]]; çevirici girişi mutlak 7 V’a dayanır [[ds]]. TVS konmadı; risk düşük ama sıfır değildir.</td></tr>'
             '<tr><td>Programlama kipi</td><td>Birinci düğme (IO0) basılıyken USB takılırsa işlemci indirme kipine girer (3. bölüm).</td></tr></table>')
    h.append('<h2>8. Kartta nerede?</h2>' + pano_kutusu(v, REFS, [(1, 'J1'), (2, 'R9'), (3, 'U3')], 'USB soketi kartın üst kenarında, antenden uzakta, kısa veri izleri için işlemciye bakar biçimde durur.'))
    h.append('<h2>9. Kaynaklar</h2><ul class="kaynak"><li>ESP32-S3-WROOM-1 veri sayfası v1.8 (yerleşik USB tam hız cihaz denetleyicisi: IO19 = D−, IO20 = D+; USB Serial/JTAG indirme).</li>'
             '<li>USB-C CC dirençleri, Rp değerleri, 10 µF kuralı: USB Type-C ve USB 2.0 belirtimleri; bu çalışmada belirtimin kendisi okunmadı (genel bilgi).</li>'
             '<li>USBLC6-2SC6 veri sayfası bu çalışmada okunmadı.</li></ul>')
    return ''.join(h)
