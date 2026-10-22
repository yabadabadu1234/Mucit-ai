import cizim as CZ
from icerik.yardim import *

ID = 'dugme'
BASLIK = '4. Düğmeler ve durum ışığı'
OZET = 'Bir düğme bir mikrodenetleyiciye nasıl bağlanır? Yukarı çekme direncinin değeri, uyandırma, LED akımı hesabı.'
REFS = ['SW2', 'R2', 'SW3', 'R3', 'SW4', 'R4', 'SW5', 'R5', 'SW6', 'R6', 'SW7', 'R7', 'R8', 'D3']


def sema(v):
    c = CZ.Cizim('Verici düğmeler ve LED', 1000, 330, v.parca)
    c.bolge(10, 8, 980, 312, 'DÜĞMELER (6 adet, her biri bir uyandırma ayağında) ve DURUM LED’i')
    for i in range(6):
        x = 70 + i * 135
        ag = 'BTN%d' % (i + 1)
        r, sw = 'R%d' % (i + 2), 'SW%d' % (i + 2)
        c.ray('+3V3', x, 100)
        c.direnc(r, x, 100, 90)
        c.tel((x, 160), (x, 170), (x, 180))
        c.etiket(ag, x, 170, 'sag')
        c.dugme(sw, x, 180, 90)
        c.toprak(x, 240)
    c.etiket('LED_CTL', 880, 100, 'yukari')
    c.direnc('R8', 880, 100, 90)
    c.led('D3', 880, 160, 90)
    c.toprak(880, 220)
    c.not_(560, 300, 'Etiket adları işlemcinin ilgili ayağına gider (3. bölüm)', 'start')
    c.isaret(1, 36, 130); c.isaret(2, 36, 210); c.isaret(3, 850, 130)
    return c


def uret(ver, ctx):
    v = ver
    c = sema(v)
    hata = c.denetle(v.aglar)
    assert not hata, hata
    Rp = v.deg('R2'); Rl = v.deg('R8')
    h = ['<h1>%s</h1><p class="ozet">%s</p>' % (BASLIK, OZET)]
    h.append(kutu('not', '<ul><li>Bir düğmeyi mantık seviyesine çevirmenin standart yolu ve neden böyle yapılır.</li><li>Yukarı çekme direncinin değerini nasıl seçersin (akım, hız, gürültü dengesi)?</li><li>LED direncini hesapla.</li><li>Uyku modunda düğmeyle uyanma nasıl çalışır?</li></ul>', 'Bu bölümde öğreneceklerin:'))
    h.append('<h2>1. Büyük resim</h2><p>Bir düğme yalnızca iki ucu birbirine değdiren bir anahtardır. İşlemci ise <b>gerilim</b> okur: 0 ya da 3,3 volt. Düğmeyi okunur kılmak için bir ucu toprağa, diğer ucu hem işlemci ayağına hem de bir <b>yukarı çekme direncine</b> (pull-up) bağlarız. '
             'Basılmamışken direnç ayağı 3,3 V’a çeker (“1”); basılınca düğme ayağı toprağa kısa devre eder (“0”). Direnç yoksa basılmamış düğmenin ayağı <i>havada</i> kalır ve rastgele gürültü okur.</p>')
    h.append('<h2>2. Şema</h2>' + sema_kutusu(c))
    h.append(isaretli(['<b>Yukarı çekme dirençleri (R2–R7: 100 kΩ).</b> Her düğme hattı 3,3 V’a bir dirençle bağlıdır.',
                       '<b>Düğmeler (SW2–SW7).</b> Basılınca hattı toprağa bağlar. Ağ adları BTN1…BTN6; işlemcinin RTC (uyandırma yapabilen) ayaklarına gider.',
                       '<b>LED (D3) ve direnci (R8: 470 Ω).</b> İşlemci ayağı (IO7) LED’i süren çıkış olarak yapılandırılır. Direnç akımı sınırlar.']))
    h.append('<h2>3. Hesap: yukarı çekme direnci kaç olmalı?</h2>')
    h.append('<p>Bir tarafta <b>akım</b>, diğer tarafta <b>gürültü ve hız</b> vardır. Düğme basılıyken yukarı çekme direncinden toprağa sürekli akım akar: <i>I = V / R</i>.</p>')
    h.append(hesap('ohm', [3.3, Rp]))
    h.append('<p>R = 100 kΩ için basılı kalma akımı %s µA’dır [[tahmin]]. Düğmeler çoğu zaman basılı olmadığı için uyku akımına etkisi yoktur: basılmayan düğmenin hattında akım akmaz (işlemci girişinin kaçak akımı en çok 50 nA’dır; bu 100 kΩ’da yalnızca %s mV düşüm demektir) [[ds]]. '
             'Direnç küçük (10 kΩ) olsaydı gürültüye karşı daha sağlam olur ama basılı akımı 330 µA olurdu; çok büyük (1 MΩ) olsaydı hat kapasitesi nedeniyle yükselme süresi (τ = RC) uzar ve gürültüye açık olur. 100 kΩ pilli cihazlar için yaygın bir uzlaşmadır. [[bilgi]]</p>' % (
                 sayi(3.3 / Rp * 1e6, 3), sayi(Rp * 50e-9 * 1e3, 3)))
    h.append('<p>İşlemcinin kendi içinde de yaklaşık 45 kΩ’luk zayıf yukarı çekme direnci vardır; açılırsa dışarıdaki dirençle paralel olur (≈ 31 kΩ) [[ds]]. Dışarıya direnç koymanın nedeni, uyku modunda içerideki dirençlerin kapanabilmesi ve değerin <i>bizim</i> denetimimizde olmasıdır.</p>')
    h.append('<h3>Giriş eşikleri</h3><p>İşlemcinin giriş eşikleri 3,3 V için: yüksek ≥ %s V, alçak ≤ %s V. [[ds]] Basılı düğme hattı yaklaşık 0 V’ta (anahtar direnci birkaç ohm; 100 kΩ ile bölününce ihmal edilir), basılmamış hat yaklaşık 3,3 V’tadır; iki durum eşiklerden çok uzaktadır.</p>' % (sayi(0.75 * 3.3, 4), sayi(0.25 * 3.3, 3)))
    h.append('<h2>4. Hesap: LED direnci</h2>')
    h.append('<p>LED bir direnç gibi davranmaz; yaklaşık sabit bir ileri gerilim (<i>V<sub>f</sub></i>) düşer. Akımı sınırlayan direncin değeri: <i>R = (V<sub>besleme</sub> − V<sub>f</sub>) / I</i>.</p>')
    h.append(hesap('led', [3.3, 2.0, 2.0]))
    ilk = (3.3 - 2.0) / Rl
    h.append('<p>Kartta R8 = %s Ω. V<sub>f</sub> = 2,0 V varsayımıyla (yeşil LED için tipik; parça veri sayfası okunmadı [[dogrulanmadi]]) akım (3,3 − 2,0) / %s = <b>%s mA</b>’dir. İşlemci ayağı bundan çok daha fazlasını verebilir (veri sayfası: 40 mA tipik, V<sub>OH</sub> ≥ 2,64 V’ta) [[ds]], yani direnç, LED’i korumak içindir. Pilli bir cihazda LED akımı küçük tutulur: ≈ 3 mA bile görünür ışık verir; LED yalnız kısa bir yanıp sönme için açılır.</p>' % (sayi(Rl), sayi(Rl), sayi(ilk * 1e3, 3)))
    h.append('<h2>5. Uyandırma</h2><p>Derin uykuda işlemcinin çoğu kapalıdır; yalnız “RTC” bölgesindeki ayaklar giriş seviyesini izler ve gerekirse işlemciyi uyandırır. ESP32-S3’te IO0–IO21 arası ayaklar bu gruptadır [[ds]]. Düğmelerin altısı bu ayaklara bağlı (IO0, IO1, IO2, IO4, IO5, IO6) olduğu için <b>herhangi bir düğme basılınca uyanma</b> mümkündür. '
             'Uyandırma için yazılımda “seviye düşünce uyan” (örneğin <code>ext1</code> alçak seviye) ayarlanır; bu iş yazılımdır ve bu teslimata dahil değildir. [[bilgi]]</p>')
    h.append(kutu('uyari', 'Derin uykuda uyandırma ayağının seviyesini <b>dış direnç</b> tutmalıdır (içerideki yukarı çekme direnci uykuda kapalı olabilir). Bu yüzden R2–R7 yalnız “süs” değil, uyandırmanın <i>şartıdır</i>.', 'Önemli'))
    h.append('<h2>6. Uç durumlar</h2><table><tr><th>Durum</th><th>Ne olur?</th></tr>'
             '<tr><td>Kontak sıçraması</td><td>Mekanik kontak basılınca birkaç ms çınlar (açıp kapar). Yazılım bir kez algılayıp sonrası yok saymalı; donanımla RC süzgeci de yapılabilir (burada konmadı).</td></tr>'
             '<tr><td>Birden fazla düğmeye aynı anda basma</td><td>Her düğmenin kendi ayağı olduğu için hepsi ayrı okunur; matris tarama gerekmez.</td></tr>'
             '<tr><td>Elle dokunurken statik boşalma</td><td>Düğmenin metal gövdesi boşalma alır; işlemci ayağında ek koruma yok. İşlemci ayakları HBM ±2000 V’a dayanıklı olduğu söylenir, ama gerçek ESD daha sert olabilir [[ds]]; yüksek güvenlik için ayağa seri 100 Ω ve küçük bir ESD diyodu konabilir.</td></tr>'
             '<tr><td>IO0 düğmesi (BTN1) açılışta basılı</td><td>İşlemci indirme kipine girer (3. bölüm). Kullanıcı yanlışlıkla basılı tutarak cihazı açarsa program çalışmaz; bu bilinçli bir takas.</td></tr>'
             '<tr><td>LED ayağı yüksek, LED sürekli yanık</td><td>3 mA × 3,3 V ≈ 9 mW sürekli; pil ömrünü azaltır. Yazılım LED’i kısa süre yakmalı.</td></tr></table>')
    h.append('<h2>7. Parça kartları</h2><div class="kartlar">' + ''.join(v.kart_html(r) for r in ['SW2', 'R2', 'R8', 'D3']) + '</div><p class="kaynak">SW3–SW7 ve R3–R7, SW2 ve R2 ile aynıdır.</p>')
    h.append('<h2>8. Kartta nerede?</h2>' + pano_kutusu(v, REFS, [(1, 'R2'), (2, 'SW2'), (3, 'D3')], 'Düğmeler kullanıcının parmağına göre iki sütun hâlinde sıralıdır; LED çalışma durumunu görünür yerde verir.'))
    h.append('<h2>9. Kaynaklar</h2><ul class="kaynak"><li>ESP32-S3-WROOM-1 veri sayfası v1.8 (tablo 6-3 giriş eşikleri, kaçak akım ve çekme dirençleri; RTC ayakları).</li><li>Düğme, kontak sıçraması, LED ileri gerilimi: genel mühendislik bilgisi.</li></ul>')
    return ''.join(h)
