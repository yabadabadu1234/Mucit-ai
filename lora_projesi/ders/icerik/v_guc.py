import html
import cizim as CZ
from icerik.yardim import *

ID = 'guc'
BASLIK = '1. Besleme: iki pilden sabit 3,3 volt'
OZET = 'Pil gerilimi değişirken kartın ihtiyaç duyduğu sabit 3,3 voltu nasıl üretiriz? Yükselten-düşüren çevirici, VEYA diyotları, giriş ve çıkış kondansatörleri.'
REFS = ['BT1', 'SW1', 'D1', 'D2', 'C1', 'C2', 'U2', 'L1', 'C3', 'C4']


def sema(v):
    O = 50
    c = CZ.Cizim('Verici besleme şeması', 1130, 360, v.parca)
    c.bolge(10, 8, 1110, 346, 'BESLEME  —  pil ve USB 5 V girişinden sabit 3,3 V')
    ry = 100 + O
    # pil
    c.pil('BT1', 80, 160 + O, 90)
    c.tel((80, 160 + O), (80, ry), (170, ry))
    c.etiket('VBAT_RAW', 125, ry - 6, 'yukari')
    c.tel((80, 220 + O), (80, 240 + O))
    c.toprak(80, 240 + O)
    # anahtar
    c.dugme('SW1', 170, ry, 0)
    c.tel((230, ry), (300, ry))
    c.etiket('VBAT_SW', 265, ry - 6, 'yukari')
    # D1, D2
    c.diyot('D1', 300, ry, 0, 'schottky')
    c.diyot('D2', 300, ry - 55, 0, 'schottky')
    c.tel((360, ry), (410, ry))
    c.tel((360, ry - 55), (410, ry - 55), (410, ry))
    c.tel((255, ry - 55), (300, ry - 55))
    c.etiket('VBUS', 250, ry - 61, 'sol')
    c.nokta(410, ry)
    c.tel((410, ry), (450, ry), (560, ry), (610, ry), (625, ry))
    c.etiket('VIN', 430, ry - 6, 'yukari')
    c.kondansator('C1', 450, ry, 90)
    c.kondansator('C2', 560, ry, 90)
    c.toprak(450, ry + 60); c.toprak(560, ry + 60)
    c.nokta(450, ry); c.nokta(560, ry)
    c.tel((610, ry), (610, ry + 20), (610, ry + 40))
    c.nokta(610, ry)
    c.tel((610, ry + 20), (625, ry + 20)); c.tel((610, ry + 40), (625, ry + 40)); c.nokta(610, ry + 20)
    c.tel((625, ry + 60), (590, ry + 60)); c.toprak(590, ry + 60)
    pin = c.kutu('U2', 640, ry - 20, [(5, 'VIN'), (8, 'VINA'), (6, 'EN'), (7, 'PS/SYNC')], [(1, 'VOUT'), (10, 'FB')],
                 ust=[(4, 'L1'), (2, 'L2')], alt=[(9, 'GND'), (3, 'PGND'), (11, 'PGND/EP')], genislik=180, baslik='TPS63031')
    bx1, bx2 = pin['4'][0], pin['2'][0]
    c.tel((bx1, pin['4'][1]), (bx1, ry - 75))
    c.tel((bx2, pin['2'][1]), (bx2, ry - 75))
    c.bobin('L1', bx1, ry - 75, 0)
    c.etiket('L1N', bx1 - 6, ry - 48, 'sol'); c.etiket('L2N', bx2 + 6, ry - 48, 'sag')
    gy = pin['9'][1] + 25
    c.tel((pin['9'][0], pin['9'][1]), (pin['9'][0], gy), (pin['3'][0], gy), (pin['11'][0], gy))
    c.tel((pin['3'][0], pin['3'][1]), (pin['3'][0], gy))
    c.tel((pin['11'][0], pin['11'][1]), (pin['11'][0], gy))
    c.nokta(pin['3'][0], gy)
    c.toprak(pin['3'][0], gy)
    # cikis
    c.tel((835, ry), (860, ry))
    c.tel((835, ry + 20), (860, ry + 20), (860, ry))
    c.nokta(860, ry)
    c.tel((860, ry), (920, ry), (1030, ry), (1090, ry))
    c.kondansator('C3', 920, ry, 90); c.kondansator('C4', 1030, ry, 90)
    c.nokta(920, ry); c.nokta(1030, ry)
    c.toprak(920, ry + 60); c.toprak(1030, ry + 60)
    c.ray('+3V3', 1090, ry)
    c.isaret(1, 52, ry + 80); c.isaret(2, 215, ry - 38); c.isaret(3, 385, ry + 25); c.isaret(4, 505, ry + 100)
    c.isaret(5, 760, ry + 125); c.isaret(6, bx2 + 50, ry - 100); c.isaret(7, 975, ry + 100)
    return c


def uret(ver, ctx):
    v = ver
    c = sema(v)
    hata = c.denetle(v.aglar)
    assert not hata, hata
    h = []
    h.append('<h1>%s</h1><p class="ozet">%s</p>' % (BASLIK, OZET))
    h.append(kutu('not', '<ul><li>Pil gerilimi neden sabit değildir ve elektronik neden sabit gerilim ister?</li>'
                  '<li>Yükselten-düşüren (buck-boost) çevirici nasıl çalışır, neden bu kartta tercih edildi?</li>'
                  '<li>Bobin, giriş ve çıkış kondansatörlerinin değerini sen nasıl seçersin? Hesaplar.</li>'
                  '<li>Neden iki diyot var, bedeli nedir?</li>'
                  '<li>Kartta nerede durmalılar?</li></ul>', 'Bu bölümde öğreneceklerin:'))
    h.append('<h2>1. Büyük resim</h2>')
    h.append('<p>Kartın iki besleme kaynağı olabilir: iki adet AAA pil veya USB-C’den gelen 5 volt. İşlemci (ESP32-S3) ile telsiz modülünün (RFM95W) ihtiyacı ise <b>sabit 3,3 volttur</b>. '
             'Alkali bir AAA pil yeni iken yaklaşık 1,5 volt verir, boşalırken 1,0 volt ve altına düşer. İki hücre seri bağlanınca toplam gerilim '
             'yeni pilde yaklaşık 3,0–3,2 volt, boş pilde yaklaşık 1,8–2,0 volt olur [[bilgi]]. Yani giriş gerilimi bazen 3,3 voltun <i>üstünde</i>, çoğunlukla <i>altındadır</i>. '
             'Düşüren (buck) çevirici yalnız indirebilir, yükselten (boost) çevirici yalnız çıkarabilir; ikisini birden yapan <b>yükselten-düşüren çevirici</b> gerekir. '
             'Bu işi tek çip (TPS63031) yapar.</p>')
    h.append(formul('Pil gerilimi (2 hücre): 3,2 V … 1,8 V   →   çevirici   →   sabit 3,3 V'))
    h.append('<h2>2. Şema</h2><p>Aşağıdaki şema bu bölümün gerçek şemasıdır: parçalar, değerler ve bağlantılar tasarım dosyasındaki bağlantı listesinden çıkarılmış ve çizim, o listeyle makine tarafından karşılaştırılmıştır (kısa devre ya da kopukluk olsaydı bu sayfa üretilmezdi). '
             'Bir parçaya tıklarsan aşağıdaki kartı açılır.</p>')
    h.append(sema_kutusu(c))
    h.append(isaretli([
        '<b>Pil (BT1, 2 × AAA).</b> Artı ucu ağ adı <code>VBAT_RAW</code>’dır. Eksi ucu toprak (GND). Yuvanın içine iki pil seri girer.',
        '<b>Ana anahtar (SW1).</b> Pili devreden ayırır. Kaydırmalı anahtar olduğu için pilli cihazda uzun süre depoda kalınca tüketim sıfırlanır. Kapalıyken çevirici hiç beslenmez.',
        '<b>VEYA diyotları (D1, D2).</b> Çeviriciye giriş iki kaynaktan gelebilir: pil (D1 üzerinden) ve USB (D2 üzerinden). Diyotlar akımın tek yöne akmasını sağlar; yüksek gerilimli kaynak devreyi besler, diğeri geri beslenmez. Bedeli: her diyotta yaklaşık 0,2–0,4 volt düşüm. Aşağıda hesaplanır.',
        '<b>Giriş kondansatörleri (C1: 10 µF, C2: 100 nF).</b> Çevirici bobin akımını çok hızlı açıp kapatır; giriş hattı kısa süreli akım ister. Yakındaki kondansatör bu akımı verir. Büyük olan (C1) düşük frekansı, küçük olan (C2) yüksek frekansı karşılar.',
        '<b>Çevirici çipi (U2, TPS63031).</b> Dört anahtar içerir. <code>EN</code> (etkinleştirme) ve <code>VINA</code> (denetim besleme) uçları <code>VIN</code>’e bağlıdır: çip, giriş gelir gelmez çalışır. <code>PS/SYNC</code> toprakta: güç tasarruf kipi açık, hafif yükte verim yüksek, çıkış dalgalanması biraz fazla.',
        '<b>Bobin (L1, 1,5 µH).</b> Çipin <code>L1</code> ve <code>L2</code> uçları arasındadır. Enerji önce bobine yüklenir, sonra çıkışa aktarılır. Değeri veri sayfasından alınmıştır.',
        '<b>Çıkış kondansatörleri (C3, C4: 2 × 10 µF).</b> Çıkışı yumuşatır, ani yük değişiminde gerilimin düşmesini önler. FB ucu çıkışın kendisine bağlıdır (sabit 3,3 V sürümünün şartı).',
    ]))
    h.append('<h2>3. Çalışma ilkesi: yükselten-düşüren çevirici</h2>')
    h.append('<p>Çipin içinde dört anahtar (alan etkili transistör) ve dışarıda bir bobin vardır. Bobin, içinden geçen akımı değiştirmemeye çalışan bir parçadır; '
             'akımı artırmak için gerilim uygulanır ve enerji bobinin manyetik alanında depolanır. Anahtarlar bu enerjiyi iki yönde kullanır:</p>'
             '<ul><li><b>Giriş çıkıştan yüksekse (düşürme):</b> bir anahtar bobini girişe bağlar, sonra bırakır; bobin akımı çıkışa verir. Bağlı kalma oranı (görev oranı, <i>D</i>) çıkış/giriş kadardır.</li>'
             '<li><b>Giriş çıkıştan düşükse (yükseltme):</b> bobin önce toprağa bağlanıp enerji toplar, sonra girişle seri hâle gelip çıkışı giriş + bobin gerilimine çıkarır. Bu durumda görev oranı <i>D = (Çıkış − Giriş) / Çıkış</i> olur.</li></ul>'
             '<p>Veri sayfası, çipin giriş çıkışa yakınken bile (en kritik nokta) dört anahtarın tamamını sürekli anahtarlamadığını, yalnız bir anahtarı aktif ve birini doğrultucu yaptığını, diğer ikisinin ise sürekli açık ve sürekli kapalı kaldığını anlatır; böylece kayıp azalır. [[ds]]</p>')
    h.append('<h2>4. Bunu sıfırdan nasıl tasarlarsın?</h2>')
    h.append('<h3>Adım 1 — İhtiyacı yaz</h3>'
             '<table><tr><th>Büyüklük</th><th>Değer</th><th>Kaynak</th></tr>'
             '<tr><td>Giriş aralığı (pil)</td><td>1,8 … 3,2 V</td><td>2 alkali hücre [[bilgi]]</td></tr>'
             '<tr><td>Giriş aralığı (USB)</td><td>4,5 … 5,5 V</td><td>USB özelliği [[bilgi]]</td></tr>'
             '<tr><td>Çıkış</td><td>3,3 V</td><td>İşlemci ve telsiz modülü besleme gerilimi</td></tr>'
             '<tr><td>Çıkış akımı (en kötü)</td><td>≈ 0,3 A</td><td>Telsiz gönderirken ≈ 0,12 A + işlemci ≈ 0,05–0,1 A + pay [[tahmin]]</td></tr></table>')
    h.append('<h3>Adım 2 — Çip seç</h3><p>Aranan: giriş aralığı 1,8–5,5 V’u kapsasın, çıkış 3,3 V, ≥ 0,3 A, düşük hareketsiz akım. TPS63031: giriş 1,8–5,5 V, sabit 3,3 V çıkış, hareketsiz akım tipik 25 µA, düşürme modunda 800 mA, yükseltme modunda 500 mA (giriş > 2,4 V). [[ds]] Hepsi şartı sağlar. '
             'Ancak giriş 1,8 V’a yakınken çıkış akımı daha düşüktür: Veri sayfası Şekil 2, giriş geriliminin düşük olduğu yerde azami çıkış akımının belirgin biçimde azaldığını gösterir; bu yüzden yüke göre aşağıdaki hesabı yaparız. [[ds]]</p>')
    h.append('<h3>Adım 3 — Bobin tepe akımını hesapla (veri sayfası denklem 2 ve 3)</h3>')
    h.append(formul('D = (V<sub>çıkış</sub> − V<sub>giriş</sub>) / V<sub>çıkış</sub>'))
    h.append(formul('I<sub>tepe</sub> = I<sub>çıkış</sub> / (η × (1 − D)) + V<sub>giriş</sub> × D / (2 × f × L)'))
    h.append('<p>Burada η verim (veri sayfası 0,90 varsaymayı önerir), f anahtarlama frekansı (tipik 2,4 MHz), L bobin değeridir. Hesap, <b>boşaldığı için en kötü</b> giriş gerilimiyle (burada 1,8 V) yapılır. Aşağıdaki hesap makinesi bu bölümün değerleriyle dolu gelir; değerleri değiştirip dene.</p>')
    L = v.deg('L1') * 1e6
    h.append(hesap('yukselten', [1.8, 3.3, 0.3, 0.9, 2.4, round(L, 3)]))
    D = (3.3 - 1.8) / 3.3
    I = 0.3 / (0.9 * (1 - D)) + 1.8 * D / (2 * 2.4e6 * L * 1e-6)
    h.append('<p><b>Elle hesap:</b> D = (3,3 − 1,8)/3,3 = %s. Birinci terim 0,3 / (0,9 × %s) = %s A. İkinci terim 1,8 × %s / (2 × 2,4·10⁶ × %s·10⁻⁶) = %s A. Toplam I<sub>tepe</sub> = <b>%s A</b>. '
             'Veri sayfası, bobinin doyma akımının bunun %%20 fazlası olmasını önerir: <b>%s A</b>. Ortalama anahtar akım sınırı tipik 1,0 A olduğundan, 1,8 V giriş ve 0,3 A yükte çip sınıra %%%s kadar yaklaşır; bu yüzden boş pilde yük artarsa çıkış çökmeye başlar. [[ds]] [[tahmin]]</p>' % (
                 sayi(D), sayi(1 - D), sayi(0.3 / (0.9 * (1 - D))), sayi(D), sayi(L), sayi(1.8 * D / (2 * 2.4e6 * L * 1e-6)), sayi(I), sayi(I * 1.2), sayi(I / 1.0 * 100, 3)))
    h.append(kutu('uyari', 'BOM’da bobin “Coilcraft LPS3015-152 eşdeğeri”dir; bu parçanın doyma akımı bu çalışmada <b>okunmadı</b>. Hesaplanan en az doyma akımı %s A’dır. Sipariş öncesi seçilen bobinin veri sayfasında Isat ≥ %s A olduğu ve DCR değeri doğrulanmalıdır. [[dogrulanmadi]]' % (sayi(I * 1.2), sayi(I * 1.2)), 'Doğrulama borcu'))
    h.append('<h3>Adım 4 — Kondansatörleri seç</h3><ul>'
             '<li><b>Giriş:</b> veri sayfası en az 4,7 µF öneriyor, VIN ve PGND uçlarına olabildiğince yakın. Bu kartta C1 = 10 µF. [[ds]]</li>'
             '<li><b>Denetim besleme (VINA):</b> 0,1 µF (üst sınır 0,22 µF). Bu kartta C2 = 100 nF, VIN ağı üzerindedir; VINA ve VIN aynı ağ olduğundan elektriksel olarak VINA’ya da hizmet eder. Veri sayfasındaki C3 doğrudan VINA–GND arasındadır; bizde kondansatör VIN ağına konmuştur, yerleşimde ikisinin de ucuna yakın durması şart. [[ds]]</li>'
             '<li><b>Çıkış:</b> önerilen nominal 10 µF, üst sınır yoktur; tipik uygulama 2 × 10 µF. Bu kartta C3 + C4 = 20 µF ve 3,3 V hattında ayrıca işlemci ve telsiz yakınında C5 (22 µF), C9 (10 µF) ve küçük kondansatörler vardır. [[ds]]</li></ul>')
    h.append(hesap('kondgerilim', [10, 6.3, 3.3, 1]))
    h.append(kutu('ipucu', 'Seramik kondansatörde gerilim arttıkça kapasite düşer. 10 µF 6,3 V parça 3,3 V altında yarıya inebilir; bu yüzden veri sayfasının önerdiği 10 µF, “etiketteki” değil “gerilim altındaki etkin” değerdir. Tasarımda marj bırak: bizim C3 + C4 + diğerleri toplamı tipik önerinin birkaç katıdır.', 'İpucu'))
    h.append('<h3>Adım 5 — Giriş kaynaklarını birleştir ve bedelini hesapla</h3>'
             '<p>Pil ve USB aynı çeviriciye girer. Doğrudan bağlansalar, USB bağlıyken 5 volt pile akardı (alkali pil şarj edilemez; bu tehlikelidir). İki Schottky diyot (D1, D2) yeterlidir: aynı noktaya (<code>VIN</code>) girerler, yüksek gerilimli olan kazanır, diğeri ters kutuplanıp kapanır.</p>')
    h.append('<p>Bedel: diyotta gerilim düşer. Aşağıdaki tablo, çeviricinin gereksinimleriyle pil gerilimini birleştirir (D1 üzerindeki ileri düşüm V<sub>f</sub> = 0,3 V varsayıldı [[tahmin]]):</p>')
    vf = 0.3
    satir = ''
    for hucre in (1.6, 1.5, 1.3, 1.1, 1.0, 0.95, 0.9):
        vb = 2 * hucre
        vin = vb - vf
        durum = 'çalışır' if vin >= 2.0 else ('başlayamayabilir, çalışmaya devam eder' if vin >= 1.6 else 'durur')
        satir += '<tr><td>%s V</td><td>%s V</td><td>%s V</td><td>%s</td></tr>' % (sayi(hucre), sayi(vb), sayi(vin), durum)
    h.append('<table><tr><th>Hücre gerilimi</th><th>İki hücre</th><th>Çeviriciye giren (D1 sonrası)</th><th>Durum</th></tr>%s</table>' % satir)
    h.append('<p>Kural (veri sayfası): <b>başlama</b> girişi tipik 1,8 V (en çok 2,0 V); çalışırken <b>düşük gerilim kilidi</b> 1,4–1,6 V. [[ds]] '
             'Yani diyot bu kartta, pil boşalırken kullanılabilir enerjinin son bölümünü keser: başlamak için en kötü durumda pil çıkışı 2,0 + 0,3 = 2,3 V (hücre başına 1,15 V) ister; bir kez çalıştıktan sonra pil 1,6 + 0,3 = 1,9 V’a (hücre başına 0,95 V) kadar indirilebilir. '
             'Bu bir tasarım ödünüdür: basit ve sağlam, fakat pili tam kullanmaz. Düzeltme adayı: D1 yerine düşük dirençli P kanallı transistörle “ideal diyot” kurmak (alıcı kartındaki ters bağlantı koruması gibi). Bu seçenek teklifte ayrıca öne sürülmedi; takasın bedeli karmaşıklıktır.</p>')
    h.append(alistirma('Bir deneyde pil çıkışını güç kaynağıyla taklit ediyorsun ve D1 yerine 0,25 V düşümlü bir diyot var. Hücre başına hangi gerilimde cihaz <b>kesin başlar</b>? (Başlama girişinin en çok 2,0 V olduğunu kullan.)',
                       'Çeviriciye en az 2,0 V gerekir. Pil çıkışı = 2,0 + 0,25 = 2,25 V. Hücre başına 2,25 / 2 = <b>1,125 V</b>. Bunun altında “başlamayabilir” bölgesine girersin.'))
    h.append('<h3>Adım 6 — Pil ömrünü hesapla</h3><p>Düğmeler uykudan uyandırır; cihaz çoğu zaman derin uykudadır (işlemci ≈ 8 µA [[bilgi]], çevirici hareketsiz akım 25 µA tipik [[ds]], telsiz uykuda 1 µA’nın altı [[bilgi]]). Toplam uyku akımı ≈ 35 µA seviyesindedir [[tahmin]]; bunun büyük bölümünü çevirici verir.</p>')
    h.append(hesap('pil', [1000, 35, 60, 100, 0.85]))
    h.append('<p class="kaynak">Not: Bu hesap bir tahmindir. “Basış başına enerji” alanına cihazın uyanıp telsiz gönderdiği süre boyunca çektiği ortalama akımın saniyeyle çarpımı (mAs) yazılır: örneğin 0,12 A akım 0,5 s sürerse 60 mAs. Gerçek değer ölçümle bulunur.</p>')
    h.append('<h2>5. Parça kartları</h2><p>Aşağıdaki kartlar bu bölümdeki her parçayı anlatır. Şemada bir parçaya tıklamak onu açar.</p><div class="kartlar">')
    for r in REFS:
        h.append(v.kart_html(r))
    h.append('</div>')
    h.append('<h2>6. Bağlantılar (ağlar)</h2>' + ag_tablosu(v, ['VBAT_RAW', 'VBAT_SW', 'VBUS', 'VIN', 'L1N', 'L2N', '+3V3', 'GND'], {
        'VBAT_RAW': 'Pilin artı ucu, anahtarın girişi', 'VBAT_SW': 'Anahtardan sonra pil gerilimi', 'VBUS': 'USB-C 5 V (2. bölüm)',
        'VIN': 'Diyotlardan sonra, çeviricinin girişi', 'L1N': 'Çip–bobin bağlantısı 1', 'L2N': 'Çip–bobin bağlantısı 2',
        '+3V3': 'Sabit 3,3 V çıkış (bütün kart)', 'GND': 'Sıfır volt referansı (bütün kart)'}))
    h.append('<h2>7. Uç durumlar ve arıza hâlleri</h2><table><tr><th>Durum</th><th>Ne olur?</th><th>Neden</th></tr>'
             '<tr><td>Pil yuvası boş, USB takılı</td><td>Cihaz USB’den çalışır; D1 kapalı.</td><td>D2 iletimde, D1 ters kutuplu.</td></tr>'
             '<tr><td>Pil takılı, USB’den 5 V gelir</td><td>Gerilim yüksek olan (USB) kazanır; pilden akım çekilmez (pilin gerilimi daha düşük).</td><td>Diyot VEYA kapısı. Pil taze iken ≈ 3 V < 5 V − 0,3 V.</td></tr>'
             '<tr><td>Anahtar kapalı, USB takılı</td><td>Cihaz USB’den çalışır.</td><td>Anahtar yalnız pil koluna bağlıdır; USB kolu D2 ile doğrudan girer.</td></tr>'
             '<tr><td>Pil çok boş (≈ 1,8 V)</td><td>Çıkış 3,3 V kalır ama akım sınırı düşer; telsiz gönderimi sırasında çıkış çökebilir ve işlemci yeniden başlayabilir.</td><td>Bobin tepe akımı ≈ 0,73 A (0,3 A yükte); sınır 0,9–1,3 A.</td></tr>'
             '<tr><td>Çıkış kısa devre</td><td>Çip akımı sınırlar (ortalama ≈ 1 A), sıcaklık 140 °C’ı aşarsa durur.</td><td>Veri sayfası §8.4.1 ve §8.3.3. [[ds]]</td></tr>'
             '<tr><td>Piller ters takıldı</td><td>Çeviriciye gerilim ulaşmaz; cihaz çalışmaz ama zarar görmez.</td><td>D1 ters yönde kapanır (40 V’a kadar) ve ters pil gerilimi çipe girmez. Bu, diyotun ikinci faydasıdır. [[bilgi]]</td></tr>'
             '<tr><td>Çıkış kondansatörleri çok büyük</td><td>Başlangıçta yumuşak başlatma akımı sınırlar; problem çıkmaz.</td><td>Veri sayfası: “çıkış kapasitesi için üst sınır yoktur”. [[ds]]</td></tr></table>')
    h.append('<h2>8. Kartta nerede durmalı?</h2>')
    d1 = mesafe(v, 'C1', 'U2'); d2 = mesafe(v, 'L1', 'U2'); d3 = mesafe(v, 'C3', 'U2'); d4 = mesafe(v, 'C4', 'U2')
    h.append('<p>Veri sayfasının yerleşim kuralları: (1) giriş kondansatörü, çıkış kondansatörü ve bobin çipe <b>mümkün olduğunca yakın</b>; (2) güç yolları <b>geniş ve kısa</b>; (3) güç toprağı (PGND) ve denetim toprağı (GND) ayrı tutulur, çipe yakın tek bir noktada birleştirilir; (4) geri besleme bağlantısı kısa tutulur. [[ds]]</p>')
    h.append('<p>Bizim kartta çipin merkezine olan mesafeler (parça merkezlerinden ölçüldü): C1 ≈ %s mm, L1 ≈ %s mm, C3 ≈ %s mm, C4 ≈ %s mm.</p>' % tuple(sayi(x, 3) for x in (d1, d2, d3, d4)))
    h.append(pano_kutusu(v, REFS, [(1, 'BT1'), (2, 'SW1'), (3, 'D1'), (4, 'C1'), (5, 'U2'), (6, 'L1'), (7, 'C3')],
                         'Kırmızı numaralar şemadaki numaralarla aynıdır. Vurgulanan parçalar bu bölümün parçalarıdır; solukluk diğer bölümleri gösterir.'))
    h.append(alistirma('Çevirici ile bobin arası 3 mm yerine 15 mm olsaydı ne bozulurdu? İki sebep say.',
                       '(1) Anahtarlama düğümündeki (L1/L2) geniş, hızlı gerilim sıçraması uzun bir iz üzerinde anten gibi yayılır; girişim (EMI) artar. (2) İz induktansı ve direnci bobinle seri girer: akım yükselme hızı ve verim değişir, çip kararsız çalışabilir. Veri sayfası bunun için “geniş ve kısa” der. [[ds]]'))
    h.append('<h2>9. Bu bölümde kullanılan kaynaklar</h2><ul class="kaynak"><li>TI TPS63030/TPS63031 veri sayfası SLVS696D (bu çalışmada baştan sona okundu; yerleşim, hesap ve özellik sayıları buradan).</li>'
             '<li>Alkali hücre gerilimi, MLCC davranışı, Schottky düşümü: genel mühendislik bilgisi; üretici belgeleriyle doğrulanmadı.</li></ul>')
    return ''.join(h)
