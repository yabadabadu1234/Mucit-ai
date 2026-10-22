import cizim as CZ
from icerik.yardim import *

ID = 'giris'
BASLIK = '1. 12 volt giriş: sigorta, ters bağlantı ve aşırı gerilim koruması'
OZET = 'Bir 12 voltluk sisteme girişte neler ters gidebilir ve bunu tek bir kondansatör, bir transistör, iki diyot ve bir sigortayla nasıl çözeriz.'
REFS = ['J5', 'F1', 'Q1', 'R1', 'D1', 'D2', 'C1', 'C2']


def sema(v):
    c = CZ.Cizim('Alıcı 12 V giriş koruması', 1000, 420, v.parca)
    c.bolge(10, 8, 980, 402, '12 V GİRİŞ KORUMASI  —  sigorta → ters bağlantı → aşırı gerilim → depo kondansatörü')
    ry = 150
    P = c.kutu('J5', 30, 120, [], [(1, '+12 V'), (2, 'GND')], genislik=80, baslik='12 V GİRİŞ', pinaralik=30)
    c.tel((125, ry), (190, ry), (230, ry)); c.etiket('+12V_IN', 125, ry - 10, 'sag')
    c.tel((125, ry + 30), (140, ry + 30)); c.toprak(140, ry + 30)
    c.sigorta('F1', 230, ry, 0)
    c.tel((290, ry), (390, ry)); c.etiket('+12V_F', 320, ry - 10, 'sag')
    Q = c.pmos('Q1', 420, ry + 40, 90, ayna=True, yazi=(-12, -16), yazi_hiza='end')
    c.tel((Q['S'][0], Q['S'][1]), (560, ry), (680, ry), (760, ry), (870, ry), (950, ry))
    c.nokta(560, ry)
    c.etiket('+12V', 500, ry - 10, 'sag')
    gy = Q['G'][1]
    c.tel(Q['G'], (420, gy + 40), (560, gy + 40)); c.etiket('KAPI_P', 414, gy + 34, 'sol')
    c.direnc('R1', 420, gy + 40, 90)
    c.toprak(420, gy + 100)
    c.diyot('D1', 560, gy + 40, 270, 'zener')
    c.tel((560, gy + 40 - 60), (560, ry))
    c.nokta(420, gy + 40)
    c.diyot('D2', 680, 250, 270, 'tvs', k_pin='2')
    c.tel((680, 250 - 60), (680, ry)); c.nokta(680, ry); c.toprak(680, 250)
    c.kondansator('C1', 760, ry, 90, kutuplu=True); c.toprak(760, ry + 60); c.nokta(760, ry)
    c.kondansator('C2', 870, ry, 90); c.toprak(870, ry + 60); c.nokta(870, ry)
    c.ray('+12V', 950, ry)
    c.not_(790, ry + 100, '→ iki çeviriciye (2. ve 3. bölüm)', 'start')
    c.tel((190, ry), (190, ry + 80)); c.etiket('+12V_IN', 190, ry + 96, 'asagi')
    c.not_(130, ry + 130, '→ röle kontağı (9. bölüm), sigortasız', 'start')
    c.isaret(1, 45, ry - 10); c.isaret(2, 260, ry - 45); c.isaret(3, 470, ry + 40); c.isaret(4, 610, ry + 40); c.isaret(5, 720, ry + 100); c.isaret(6, 800, ry - 45)
    return c


def uret(ver, ctx):
    v = ver
    c = sema(v)
    hata = c.denetle(v.aglar)
    assert not hata, hata
    dr = sim_veri('sim_giris')['giris_darbe']
    h = ['<h1>%s</h1><p class="ozet">%s</p>' % (BASLIK, OZET)]
    h.append(kutu('not', '<ul><li>12 voltluk bir girişte karşılaşılan üç tehlike: aşırı akım, ters bağlama, gerilim darbesi.</li><li>P kanallı alan etkili transistörle “neredeyse kayıpsız” ters bağlantı koruması nasıl çalışır?</li>'
                  '<li>TVS diyodu, kendini kendine koruyan zener diyodu ve kendini toparlayan sigorta nasıl seçilir?</li><li>Hangi sınırlar bu tasarımda dar? (Dürüst denetim tablosu)</li></ul>', 'Bu bölümde öğreneceklerin:'))
    h.append('<h2>1. Büyük resim</h2><p>12 voltluk sistemler kuruluma ve kabloya bağlıdır; insan eli ya da başka bir cihaz hata yapar. Üç şey olabilir: (1) <b>ters bağlama</b> (artı ile eksi karışır), (2) <b>aşırı akım</b> (kısa devre), (3) <b>gerilim darbesi</b> (bobinli yük kesilince, aynı hattaki bir motor çalışınca birkaç yüz mikrosaniye süren ve 30–40 V’a çıkan sıçramalar [[bilgi]]). '
             'Giriş devresi bunların hiçbirinde karta zarar vermemeli ve normal çalışırken az enerji harcamalıdır.</p>')
    h.append('<h2>2. Şema</h2>' + sema_kutusu(c))
    h.append(isaretli(['<b>Giriş klemensi (J5).</b> Vidalı klemens; artı ucu <code>+12V_IN</code>, eksi ucu toprak.',
                       '<b>Kendini toparlayan sigorta (F1, 2 A).</b> Aşırı akımda ısınıp direnci birden artarak akımı keser; akım kalkınca soğuyup eski hâline döner. Kart akımı için seri girişte durur.',
                       '<b>Ters bağlantı koruyucu transistör (Q1, AO3401A, P kanallı).</b> Kaynağı (S) kart tarafına, savağı (D) girişe bakar. Normal çalışmada kapı toprağa bağlı olduğundan kapı–kaynak gerilimi −10 V civarına gider ve transistör iletir (düşük direnç). Giriş ters bağlanırsa kapı–kaynak gerilimi ≈ 0 olur, transistör iletmez ve gövde diyodu ters yönde kalır: akım geçmez.',
                       '<b>Kapı direnci (R1, 100 kΩ) ve zener diyot (D1, 10 V).</b> R1 kapıyı toprağa çeker (iletim için). D1, kapı–kaynak gerilimini 10 V ile sınırlar: giriş 12 V’tan büyük olduğunda kapı oksidi aşırı zorlanmasın diye.',
                       '<b>Aşırı gerilim koruyucu (D2, SMBJ15A, tek yönlü TVS).</b> 15 V’un üstünde iletime geçip darbeyi toprağa akıtır ve hattı sınırlar.',
                       '<b>Depo kondansatörleri (C1: 220 µF elektrolitik, C2: 100 nF).</b> Çeviricilerin darbeli akım ihtiyacını karşılar; C1 aynı zamanda kablo endüktansı nedeniyle oluşan sıçramaları yumuşatır.']))
    h.append('<h2>3. Ters bağlantı koruması nasıl çalışır?</h2>')
    h.append('<p>Klasik yol, seri bir diyottur: akım tek yönde geçer, ama diyodun üzerinde sürekli yaklaşık 0,3–0,7 V düşer: 1 A’de 0,5 W ısınır. P kanallı transistör, aynı işi <i>açık bir anahtar gibi</i> yapar: iletirken direnci yalnızca on miliohm düzeyindedir. '
             'Çalışma: transistör, kapı gerilimi kaynak gerilimine göre yeterince <b>negatifse</b> (P kanal) iletir. Normalde kaynak ≈ +12 V, kapı R1 ile 0 V’ta: V<sub>GS</sub> = −12 V → iletir (D1 bunu −10 V’ta tutar). '
             'Ters bağlanınca girişteki “eksi” savağa gelir; kaynak (kart tarafı) 0 V’ta kalır ve kapı ile aynı seviyededir: V<sub>GS</sub> ≈ 0 → kapalı. Gövde diyodu da bu yönde ters kutuplanmıştır: akım geçmez.</p>')
    h.append('<h3>Benzetim sonuçları (genel modellerle) [[tahmin]]</h3>'
             '<table><tr><th>Senaryo</th><th>Sonuç</th></tr>'
             '<tr><td>12 V giriş, 1 A yük, kaynak direnci 0,1 Ω, PTC 0,15 Ω</td><td>Çıkış 11,70 V; kapı–kaynak −9,90 V; transistör üzerinde yalnız 50 mV (≈ 50 mΩ); toplam düşüm 0,30 V (çoğu kaynak ve sigortada).</td></tr>'
             '<tr><td>Ters bağlama (−12 V)</td><td>Çıkış −0,08 V (yani ≈ 0); girişten çekilen akım ≈ 22 pA (ihmal edilir).</td></tr>'
             '<tr><td>5 ms’lik 36 V darbe (kaynak direnci 2 Ω)</td><td>Çıkış en çok 20,3 V; TVS akımı en çok 6,1 A; kapı–kaynak en çok −9,94 V.</td></tr></table>')
    h.append(grafik(dr['t_ms'], [('Giriş', dr['vin'], '#e53935'), ('Çıkış (korunan)', dr['vout'], '#1e88e5'), ('Kapı–kaynak', dr['vgs'], '#43a047')], 'zaman (ms)', 'gerilim (V)', cizgiler=[(15, 'TVS 15 V')]))
    h.append('<p class="kaynak">Grafik: <code>simulasyon/giris_koruma_3_darbe.cir</code> dosyasının ngspice çıktısıdır (yerelde koşturuldu, sonuçlar JSON olarak siteye girdi). Modeller genel, üretici modeli değildir; AO3401A’nın gerçek Rds(on) ve eşik gerilimi veri sayfasından doğrulanmalıdır. [[dogrulanmadi]]</p>')
    h.append('<h2>4. Hesaplar</h2><h3>4.1 Zener ve kapı gerilimi</h3><p>Zener, kapı oksidini korur; AO3401A için kapı–kaynak mutlak sınır genellikle ±12 V’tur [[bilgi]] (veri sayfası bu çalışmada okunmadı [[dogrulanmadi]]). 10 V’luk zener, sınırın altında bir marj bırakır; 12 V girişte kapı −10 V’a çekilir.</p>')
    h.append('<h3>4.2 R1 değeri</h3><p>R1 yalnız kapıyı çeker; akım yoktur (kapı yalıtılmıştır). Büyük olursa kapı kapasitesiyle birlikte açılış gecikmesi uzar (τ = R·C); küçük olursa zener hattında gereksiz akım akar: 12 V’ta zener iletirken akım = (12 − 10) / 100 kΩ = <b>%s µA</b>. 100 kΩ iki ucu dengeler. [[tahmin]]</p>' % sayi(2 / 100e3 * 1e6, 3))
    h.append(hesap('ohm', [2, 100000]))
    h.append('<h3>4.3 TVS seçimi</h3><p>Normal çalışma gerilimi 12 V’un (taşımalı 14 V’a kadar) üzerindeki en küçük “bekleme” gerilimli TVS seçilir: SMBJ15A’nın bekleme gerilimi 15 V, delinme gerilimi yaklaşık 16,7–18,5 V, 24,4 V’ta kenetlenme (darbe akımı 24,6 A’de) olarak yayımlanır [[bilgi]] [[dogrulanmadi]]. Kenetlenme gerilimi, kartın <b>dayanma sınırının altında</b> kalmalıdır. Karttaki en düşük sınır:</p>'
             '<table><tr><th>Parça</th><th>Mutlak sınır</th><th>TVS kenetlenmesi 24,4 V ile</th></tr>'
             '<tr><td>TPS62933 (U5, U6) giriş</td><td>32 V [[ds]]</td><td>marj 7,6 V — yeterli</td></tr>'
             '<tr><td>C3, C10 (10 µF 25 V seramik)</td><td>25 V</td><td>marj 0,6 V — <b>çok dar</b>; ayrıca seramik gerilim altında kapasite kaybeder</td></tr>'
             '<tr><td>C1 (220 µF 25 V elektrolitik)</td><td>25 V</td><td>marj 0,6 V — <b>çok dar</b></td></tr>'
             '<tr><td>Q1 (AO3401A) savak–kaynak</td><td>−30 V (tipik) [[bilgi]]</td><td>marj ≈ 5,6 V</td></tr></table>')
    h.append(kutu('uyari', 'Dürüst bulgu: kenetlenme gerilimi (≈ 24,4 V) 25 V’luk kondansatörlerin sınırına dayanıyor. Gerçek darbede genelde kenetlenmeye tam ulaşılmaz ve 25 V’luk parçalar kısa süreli aşımı kaldırabilir, ama bu marjla ideal bir tasarım yapılmaz. İyileştirme: 12 V hat kondansatörlerini 35 V (elektrolitik) ve 50 V (seramik) yapmak ya da TVS’i SMBJ14A gibi daha alçak kenetlenmeli parçayla değiştirmek. Bu iyileştirme teklifte kayıtlı değildir; öneri olarak sunulur. [[tahmin]]', 'Bulgu'))
    h.append('<h3>4.4 Sigorta (PTC) ve akım</h3><p>1812L200 gibi 2 A tutma akımlı bir parça yaygındır [[bilgi]] [[dogrulanmadi]]. Kart akımı: üç ayrı yük, hepsi 12 V hattından beslenen çeviriciler üzerinden: (a) 3,3 V hattı ≈ 0,3 A × 3,3 V / (12 V × 0,9) ≈ 0,09 A; (b) modem tepe akımı 2 A × 3,8 V / (12 V × 0,9) ≈ <b>0,70 A</b>; (c) röle bobini 12 V / 400 Ω = 0,03 A. Toplam en kötü ≈ 0,85 A: 2 A’lik tutma akımının altında, marjlı. [[tahmin]] '
             'Lamba akımı (3 A varsayımı) röle kontağından <b>doğrudan klemens girişinden</b> alınır; F1’den geçmez. Bu bilinçli bir tercihtir (lamba, kartın korumasına yük bindirmesin), ancak lamba hattı <b>sigortasız</b> kalır: lambanın kendi sigortası şarttır.</p>')
    h.append(hesap('iz', [3, 10, 35, 1]))
    h.append('<h2>5. Kart üzerinde denetim: iz genişlikleri</h2><p>Aşağıdaki tablo, kart dosyasındaki gerçek iz genişliklerini, hattın beklenen akımına göre IPC-2221 yaklaşımı ile kıyaslar. Bu bir <b>denetim ölçüsüdür</b>: tutmayan satır kırmızı yanar. (Akımlar varsayımdır; lamba akımı teklifte bilinmiyor, 3 A varsayıldı.)</p>'
             + iz_taramasi(v, [('+12V_IN', 3.0, 'lamba kontağına giden hat (3 A varsayım)'), ('LAMBA_SW', 3.0, 'lamba çıkışı (3 A varsayım)'), ('+12V_F', 0.85, 'sigorta sonrası kart akımı'), ('+12V', 0.85, 'kart içi 12 V dağıtımı'), ('ROLE_L', 0.03, 'röle bobini')]))
    h.append(kutu('uyari', 'Alıcı kartının yol çizimi <b>bitmedi</b>: otomatik yönlendirici bu hatları 0,3–0,4 mm çizdi; lamba hattı için gereken ≈ 1,4 mm elle genişletilecek. Bu tablo o işin neden açık olduğunu gösterir; kırmızı satırlar kapanmadan alıcı kartı üretime gönderilmez.', 'Açık iş'))
    h.append('<h2>6. Parça kartları</h2><div class="kartlar">' + ''.join(v.kart_html(r) for r in REFS) + '</div>')
    h.append('<h2>7. Uç durumlar</h2><table><tr><th>Durum</th><th>Ne olur?</th></tr>'
             '<tr><td>Giriş ters bağlandı</td><td>Q1 kapalı, hiçbir yere akım gitmez; sigorta atmaz. Röle kontağındaki lamba hattı ise <b>korumasızdır</b>: lamba ters beslenebilir (lambanın türüne göre sorun yok ya da var).</td></tr>'
             '<tr><td>Giriş 36 V’a darbeli sıçradı</td><td>TVS iletir, çıkış ≈ 20 V’a sınırlanır; çeviriciler 32 V’a dayanır. [[ds]]</td></tr>'
             '<tr><td>Kısa devre çıkışta</td><td>Sigorta ısınıp direncini artırır (yüzlerce ms içinde); akım düşer. Akım kalkınca soğuyup geri döner.</td></tr>'
             '<tr><td>Giriş 12 V’ta düşük (örneğin 9 V)</td><td>V<sub>GS</sub> = −9 V; AO3401A eşik gerilimi (tipik −0,9 V) üstünde, iletir. Kapı zeneri 10 V altında iletmez, kapı doğrudan kaynağı izler.</td></tr>'
             '<tr><td>Çok hızlı gerilim yükselmesi</td><td>Kapı kapasitesi ve R1 gecikme yaratır; kısa süre transistör kısmen iletir ve gövde diyodu akımı taşır (0,6–0,7 V düşüm). Zararsızdır.</td></tr></table>')
    h.append('<h2>8. Kartta nerede?</h2>' + pano_kutusu(v, REFS, [(1, 'J5'), (2, 'F1'), (3, 'Q1'), (4, 'D2'), (5, 'C1')], 'Giriş klemensi kart kenarında; koruma parçaları klemense yakın, kablonun kartla ilk buluştuğu yerde olmalı.'))
    h.append('<h2>9. Kaynaklar</h2><ul class="kaynak"><li>TPS62933 veri sayfası SLUSEA4D: mutlak sınır (VIN 32 V) okundu.</li><li>AO3401A, SMBJ15A, 1812L200 veri sayfaları bu çalışmada okunmadı; sayılar genel bilgidir ve sipariş öncesi doğrulanmalıdır.</li><li>Benzetim: <code>simulasyon/*.cir</code> (ngspice, genel modeller).</li></ul>')
    return ''.join(h)
