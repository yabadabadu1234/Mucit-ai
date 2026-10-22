import math
import cizim as CZ
from icerik.yardim import *

ID = 'eth'
BASLIK = '7. Ethernet: W5500 ve RJ45 (kabloyla internet)'
OZET = 'Bir ağ kablosundan internete çıkmak: W5500 çipinin besleme, referans, kristal ve hat devreleri; bütünleşik mıknatıslı RJ45 ile bağlantısı; her bir yardımcı parçanın nedeni.'
REFS = ['U9', 'J3', 'Y1', 'L3', 'R26', 'C37', 'C38', 'R14', 'R18', 'R20', 'R21', 'C25', 'C27', 'R23', 'R24', 'C41', 'C28', 'C34', 'R27', 'C39']


def sema_cip(v):
    c = CZ.Cizim('Alıcı Ethernet çipi', 1040, 540, v.parca)
    c.bolge(10, 8, 1020, 522, 'W5500  —  SPI arayüzü, referanslar ve hat uçları')
    sol = [(32, 'SCSn'), (33, 'SCLK'), (34, 'MISO'), (35, 'MOSI'), (36, 'INTn'), (37, 'RSTn')]
    sag = [(1, 'TXN'), (2, 'TXP'), (5, 'RXN'), (6, 'RXP'), (25, 'LINKLED'), (27, 'ACTLED'), (10, 'EXRES1'), (20, 'TOCAP'), (22, '1V2O'), (30, 'XI'), (31, 'XO')]
    P = c.kutu('U9', 440, 80, sol, sag, ust=[([4, 8, 11, 15, 17, 21], 'AVDD'), (28, 'VDD'), ([43, 44, 45], 'PMODE')],
               alt=[([3, 9, 14, 16, 19, 29, 48, 23], 'GND')], genislik=240, baslik='W5500', pinaralik=26)
    adlar = {32: ('ETH_CS', 'işlemci IO9'), 33: ('SPI_SCK', 'IO12'), 34: ('SPI_MISO', 'IO13'), 35: ('SPI_MOSI', 'IO11'), 36: ('ETH_INT', 'IO16'), 37: ('ETH_RST', 'IO17')}
    for no, (ag, ac) in adlar.items():
        x, y = P[str(no)]
        c.tel((x, y), (x - 45, y)); c.etiket(ag, x - 45, y, 'sol'); c.not_(x - 165, y + 4, ac + ' →', 'end')
    sag_adlar = {1: 'W_TXN', 2: 'W_TXP', 5: 'W_RXN', 6: 'W_RXP', 25: 'W_LINKLED', 27: 'W_ACTLED', 10: 'EXRES1', 20: 'TOCAP', 22: '1V2O', 30: 'XI', 31: 'XO'}
    notlar = {1: '→ RJ45 (devre C)', 2: '', 5: '', 6: '', 25: '→ RJ45 LED', 27: '→ RJ45 LED', 10: '→ 12,4 kΩ', 20: '→ 4,7 µF', 22: '→ 10 nF', 30: '→ kristal', 31: '→ kristal'}
    for no, ag in sag_adlar.items():
        x, y = P[str(no)]
        c.tel((x, y), (x + 45, y)); c.etiket(ag, x + 45, y, 'sag')
        if notlar[no]:
            c.not_(x + 155, y + 4, notlar[no], 'start')
    xa, ya = P['4']; c.tel((xa, ya), (xa, ya - 20)); c.ray('+3V3A', xa, ya - 20)
    xv, yv = P['28']; c.tel((xv, yv), (xv, yv - 20)); c.ray('+3V3', xv, yv - 20)
    xp, yp = P['43']; c.tel((xp, yp), (xp, yp - 20)); c.ray('+3V3', xp, yp - 20)
    xg, yg = P['3']; c.toprak(xg, yg)
    c.not_(40, 520, 'Bağlanmayan: 7 (DNC), 12, 13, 18 (VBG, açık kalmalı), 24 (SPDLED), 26 (DUPLED), 38–42 (içeriden aşağı çekili), 46, 47', 'start')
    by = 330
    r = c.direnc('R26', 60, by, 90); c.etiket('EXRES1', *r['a'], 'sag'); c.toprak(*r['b'])
    r = c.kondansator('C37', 160, by, 90); c.etiket('1V2O', *r['a'], 'sag'); c.toprak(*r['b'])
    r = c.kondansator('C38', 260, by, 90); c.etiket('TOCAP', *r['a'], 'sag'); c.toprak(*r['b'])
    c.ray('+3V3', 350, by); r = c.direnc('R29', 350, by, 90); c.etiket('ETH_INT', *r['b'], 'sag')
    c.not_(40, by + 100, 'Çip referansları ve kesme yukarı çekmesi', 'start')
    c.isaret(1, 395, 100); c.isaret(2, 40, by + 30); c.isaret(3, 330, by + 30)
    return c


def sema_guc(v):
    c = CZ.Cizim('Alıcı Ethernet güç süzgeci ve kristal', 1040, 460, v.parca)
    c.bolge(10, 8, 1020, 442, 'W5500 BESLEMESİ (analog ve sayısal ayrı) ve 25 MHz KRİSTAL')
    ry = 110
    c.ray('+3V3', 50, ry)
    c.tel((50, ry), (110, ry), (190, ry), (230, ry))
    c.kondansator('C35', 110, ry, 90); c.kondansator('C36', 190, ry, 90)
    c.toprak(110, ry + 60); c.toprak(190, ry + 60); c.nokta(110, ry); c.nokta(190, ry)
    c.boncuk('L3', 230, ry, 0)
    xs = [350 + 80 * i for i in range(7)]
    c.tel((290, ry), (xs[0], ry), *[(x, ry) for x in xs[1:]], (xs[-1] + 50, ry))
    for ref, x in zip(['C28', 'C29', 'C30', 'C31', 'C32', 'C33', 'C34'], xs):
        c.kondansator(ref, x, ry, 90); c.toprak(x, ry + 60); c.nokta(x, ry)
    c.ray('+3V3A', xs[-1] + 50, ry)
    c.not_(110, ry - 60, 'L3 ferrit boncuk: sayısal hattın gürültüsü analog beslemeye girmez', 'start')
    ky = 330
    c.tel((60, ky), (120, ky), (200, ky)); c.etiket('XI', 60, ky, 'sol'); c.nokta(120, ky)
    c.kristal('Y1', 200, ky, 0, pinler=('1', '3'))
    c._pin('Y1', '2', 230, ky + 60); c._pin('Y1', '4', 230, ky + 60)
    c.toprak(230, ky + 60); c.tel((230, ky + 14), (230, ky + 60)) if False else None
    c.katman['tel'].append('<path class="pinuc" stroke-dasharray="4 4" d="M230 %s V%s"/>' % (ky + 10, ky + 60))
    c.tel((260, ky), (340, ky), (420, ky)); c.nokta(340, ky)
    c.kondansator('C39', 120, ky, 90); c.toprak(120, ky + 60)
    c.kondansator('C40', 340, ky, 90); c.toprak(340, ky + 60)
    c.direnc('R28', 480, ky, 180)
    c.etiket('XO', 480, ky, 'sag')
    c.direnc('R27', 180, ky - 70, 0)
    c.tel((120, ky), (120, ky - 70), (180, ky - 70))
    c.tel((240, ky - 70), (480, ky - 70), (480, ky))
    c.not_(560, ky - 60, 'R27 (1 MΩ): kristal yükselteçine ters besleme ile yön verir', 'start')
    c.not_(560, ky - 40, 'R28 (0 Ω): sürücü çıkışını kristalden ayıran yer; gerekirse değeri değiştirilir', 'start')
    c.not_(560, ky - 20, 'C39, C40 (18 pF): kristalin “yük kondansatörleri”', 'start')
    c.isaret(1, 70, ry + 40); c.isaret(2, 275, ry - 25); c.isaret(3, 230, ky + 36)
    return c


def sema_phy(v):
    c = CZ.Cizim('Alıcı Ethernet hat devreleri ve RJ45', 1100, 600, v.parca)
    c.bolge(10, 8, 1080, 582, 'ETHERNET HATTI  —  W5500 uçları, hat devreleri ve bütünleşik mıknatıslı RJ45')
    c.kutu('J3', 880, 40, [(1, 'TD+'), (2, 'TD−'), (4, 'TCT'), (3, 'RD+'), (6, 'RD−'), (5, 'RCT'), (10, 'LED-K 1'), (11, 'LED-K 2'), ([9, 12], 'LED-A'), (8, 'GND'), ('SH', 'kılıf')], [],
           genislik=110, baslik='RJ45 HR911105A', pinaralik=30)
    ex = 865
    for y, w, rsi, ag in ((70, 'W_TXN', 'R14', 'TD_P'), (100, 'W_TXP', 'R15', 'TD_N')):
        c.etiket(w, 110, y, 'sol'); c.tel((110, y), (160, y))
        c.direnc(rsi, 160, y, 0)
        c.tel((220, y), (280, y), (ex, y)); c.etiket(ag, 280, y, 'yukari')
    c.tel((ex, 130), (800, 130)); c.etiket('TCT', 800, 130, 'sol')
    for y, w, r1, a1, c1, a2 in ((160, 'W_RXN', 'R16', 'RX_A', 'C25', 'RD_P'), (190, 'W_RXP', 'R17', 'RX_B', 'C26', 'RD_N')):
        c.etiket(w, 110, y, 'sol'); c.tel((110, y), (160, y))
        c.direnc(r1, 160, y, 0)
        c.tel((220, y), (250, y), (300, y)); c.etiket(a1, 250, y, 'yukari')
        c.kondansator(c1, 300, y, 0)
        c.tel((360, y), (420, y), (ex, y)); c.etiket(a2, 420, y, 'yukari')
    c.tel((ex, 220), (800, 220)); c.etiket('RCT', 800, 220, 'sol')
    for y, w, rr, ag in ((250, 'W_LINKLED', 'R24', 'LNK_K'), (280, 'W_ACTLED', 'R25', 'ACT_K')):
        c.etiket(w, 560, y, 'sol'); c.tel((560, y), (680, y))
        c.direnc(rr, 680, y, 0)
        c.tel((740, y), (790, y), (ex, y)); c.etiket(ag, 790, y, 'yukari')
    c.tel((ex, 310), (820, 310)); c.ray('+3V3', 820, 310)
    c.tel((ex, 340), (830, 340)); c.toprak(830, 340)
    c.tel((ex, 370), (830, 370)); c.etiket('SHELL', 830, 370, 'sol')
    c.not_(40, 30, 'W5500’ten gelen uçlar soldan girer; RJ45’in içindeki mıknatıslar (transformatörler) soketin içindedir.', 'start')
    by = 440
    for x, ref, ust, alt in ((60, 'R18', '+3V3A', 'TD_P'), (160, 'R19', '+3V3A', 'TD_N'), (260, 'R20', '+3V3A', 'TCT')):
        c.ray(ust, x, by); r = c.direnc(ref, x, by, 90); c.etiket(alt, *r['b'], 'sag')
    r = c.kondansator('C24', 360, by, 90); c.etiket('TCT', *r['a'], 'sag'); c.toprak(*r['b'])
    r = c.direnc('R21', 460, by, 90); c.etiket('RX_A', *r['a'], 'sag'); c.etiket('RX_M', *r['b'], 'sag')
    r = c.direnc('R22', 560, by, 90); c.etiket('RX_B', *r['a'], 'sag'); c.etiket('RX_M', *r['b'], 'sag')
    r = c.kondansator('C27', 660, by, 90); c.etiket('RX_M', *r['a'], 'sag'); c.toprak(*r['b'])
    r = c.direnc('R23', 760, by, 90); c.etiket('RX_M', *r['a'], 'sag'); c.etiket('RCT', *r['b'], 'sag')
    r = c.kondansator('C41', 880, by, 90); c.etiket('SHELL', *r['a'], 'sag'); c.toprak(*r['b'])
    c.not_(40, by + 100, 'Gönderme hattı sonlandırması ve orta uç', 'start'); c.not_(440, by + 100, 'Alma hattı sonlandırması ve orta uç (Bob Smith)', 'start'); c.not_(860, by + 100, 'Kılıf', 'start')
    c.isaret(1, 130, 50); c.isaret(2, 330, 135); c.isaret(3, 330, 215); c.isaret(4, 780, 395); c.isaret(5, 1000, 330)
    return c


def uret(ver, ctx):
    v = ver
    cs = [sema_cip(v), sema_guc(v), sema_phy(v)]
    for k in cs:
        hata = k.denetle(v.aglar)
        assert not hata, (k.ad, hata)
    X = v.deg('R26')
    h = ['<h1>%s</h1><p class="ozet">%s</p>' % (BASLIK, OZET)]
    h.append(kutu('not', '<ul><li>Bir ağ kablosunda bilgi nasıl taşınır? Fark çifti, transformatör ve sonlandırma.</li><li>Hazır bir ağ çipinin (W5500) çevresine hangi yardımcı parçalar gerekir ve her biri neden?</li>'
                  '<li>Analog ve sayısal beslemeyi ferrit boncukla nasıl ayırırsın?</li><li>Kristal yük kondansatörü hesabı: neden 18 pF yazılı, gerçek yük kaç?</li></ul>', 'Bu bölümde öğreneceklerin:'))
    h.append('<h2>1. Büyük resim</h2><p>W5500, “donanımla yazılmış TCP/IP” yığınını, Ethernet denetleyicisini ve fiziksel katmanı (PHY) tek yongada taşır; işlemci yalnızca SPI üzerinden komut yollar. 8 bağımsız soket ve 32 KB tampon bellek vardır. [[ds]] '
             'Bu yüzden ESP32’nin yazılımı ağ yığınını taşımak zorunda kalmaz. Çipin dışarıya verdiği şey <b>iki fark çiftidir</b> (gönder ve al); bunlar bir mıknatıs (transformatör) üzerinden RJ45 soketine ve oradan kabloya gider. Bu kartta mıknatıslar RJ45 soketinin içinde hazırdır (HR911105A). WIZnet’in resmî referans devresi bire bir izlenmiştir.</p>')
    h.append('<h2>2. Devre A — Çip, SPI ve referanslar</h2>' + sema_kutusu(cs[0]))
    h.append(isaretli(['<b>W5500 (U9).</b> Solda işlemciden gelen SPI hattı (seçim, saat, veri çıkışı, veri girişi), kesme çıkışı (INTn) ve sıfırlama (RSTn). Sağda gönderme/alma fark çiftleri, ışık çıkışları, referans uçları ve kristal. Üstte besleme uçları: AVDD (analog), VDD (sayısal), PMODE (kip seçimi).',
                       '<b>Referans parçaları.</b> EXRES1 ucu 12,4 kΩ %1 dirençle analog toprağa bağlanır: çipin iç analog devrelerinin akım kaynağını ayarlar; TOCAP ucu 4,7 µF ister; 1V2O ucu çipin kendi 1,2 V iç düzenleyicisinin çıkışıdır ve 10 nF ister. [[ds]]',
                       '<b>Yukarı çekme (R29, 10 kΩ).</b> INTn çıkışı alçak seviyede kesme demektir; boştaki seviyeyi yüksek tutar.']))
    h.append('<h3>Çip uçlarının görevleri ve bu karttaki yeri</h3><table><tr><th>Uç</th><th>Ad</th><th>Bu kartta</th><th>Veri sayfasına göre</th></tr>'
             '<tr><td>4, 8, 11, 15, 17, 21</td><td>AVDD</td><td>+3V3A (süzülmüş)</td><td>Analog 3,3 V besleme [[ds]]</td></tr>'
             '<tr><td>28</td><td>VDD</td><td>+3V3</td><td>Sayısal 3,3 V [[ds]]</td></tr>'
             '<tr><td>3, 9, 14, 16, 19, 29, 48</td><td>AGND/GND</td><td>Toprak</td><td>Analog ve sayısal toprak [[ds]]</td></tr>'
             '<tr><td>23</td><td>RSVD</td><td>Toprak</td><td>“GND’ye bağlanmalı” [[ds]]</td></tr>'
             '<tr><td>43, 44, 45</td><td>PMODE2..0</td><td>3,3 V (111)</td><td>111: tüm kipler, otomatik müzakere açık [[ds]]</td></tr>'
             '<tr><td>10</td><td>EXRES1</td><td>12,4 kΩ → toprak</td><td>%1 direnç şart [[ds]]</td></tr>'
             '<tr><td>18</td><td>VBG</td><td>Açık</td><td>“Boşta kalmalı” [[ds]]</td></tr>'
             '<tr><td>7</td><td>DNC</td><td>Açık</td><td>Bağlama [[ds]]</td></tr>'
             '<tr><td>24, 26</td><td>SPDLED, DUPLED</td><td>Açık</td><td>Hız ve çift yön ışıkları kullanılmadı</td></tr>'
             '<tr><td>25, 27</td><td>LINKLED, ACTLED</td><td>RJ45 ışıklarına</td><td>Bağlantı kurulu / etkinlik; alçakta = açık [[ds]]</td></tr>'
             '<tr><td>38–42</td><td>RSVD</td><td>Açık</td><td>İçeriden aşağı çekili [[ds]]</td></tr></table>')
    h.append('<h2>3. Devre B — Besleme süzgeçleri ve kristal</h2>' + sema_kutusu(cs[1]))
    h.append(isaretli(['<b>Sayısal taraf (C35 10 µF, C36 100 nF).</b> 3,3 V hattından VDD için.',
                       '<b>Ferrit boncuk (L3) ve analog taraf (C28–C33: altı adet 100 nF; C34: 10 µF).</b> Sayısal devrenin anahtarlama gürültüsünün analog katmana (PHY) bulaşmaması için boncuk ve her AVDD ucuna yakın bir 100 nF.',
                       '<b>Kristal (Y1, 25 MHz) ve yardımcıları.</b> Çip içindeki bir yükselteç dışarıdaki kristalle salınım üretir. 1 MΩ geri besleme direnci yükselteci çalışma noktasına getirir; iki 18 pF kondansatör kristalin yük kapasitesini oluşturur; 0 Ω seri direnç gerekirse sürücü gücünü azaltmak için değiştirilebilir.']))
    h.append('<h3>Kristal yük kapasitesi hesabı</h3>')
    h.append('<p>Kristalin istediği toplam yük: C<sub>L</sub> = 18 pF (veri sayfası tablosu) ve frekans toleransı ±30 ppm. [[ds]] Devrede görülen yük, iki yük kondansatörünün seri bağlanmasıyla artı kart ve çip “serseri” kapasitesidir:</p>')
    h.append(formul('C<sub>L,gerçek</sub> = C<sub>1</sub> × C<sub>2</sub> / (C<sub>1</sub> + C<sub>2</sub>) + C<sub>serseri</sub> = 18×18/(18+18) + C<sub>serseri</sub> = 9 pF + C<sub>serseri</sub>'))
    h.append('<p>Serseri kapasite tipik 3–5 pF olduğundan gerçek yük ≈ <b>12–14 pF</b> bulunur [[tahmin]], yani istenen 18 pF’ın altında. Kristal yük kapasitesi küçük olunca frekans nominalin biraz <i>üstünde</i> salınır; sapma ppm düzeyinde ve genellikle onlarca ppm’dir [[tahmin]]. 100 Mbit/sn Ethernet 25 MHz referansta ±50 ppm sınırı arar [[bilgi]]; WIZnet referans devresi aynı değerleri kullandığı için üretici bu değerleri kabul etmiştir, ancak <b>sahada frekans ölçülmedi</b>. İyileştirme: gerçek serseri kapasite ölçülüp C39/C40 ≈ 2 × (18 − C<sub>serseri</sub>) ≈ 26–30 pF’a ayarlanabilir. [[dogrulanmadi]]</p>')
    h.append(alistirma('Serseri kapasite 4 pF ise 18 pF yük için her bir yük kondansatörü kaç pF olmalı?', 'C<sub>L</sub> = C/2 + C<sub>serseri</sub> ⟹ 18 = C/2 + 4 ⟹ C = 28 pF (standart değer: 27 pF).'))
    h.append('<h2>4. Devre C — Hat devreleri ve RJ45</h2>' + sema_kutusu(cs[2]))
    h.append(isaretli(['<b>Seri dirençler (R14–R17, 0 Ω).</b> Çip ile hat arasında deneme sırasında değer takılabilen yerler; şimdilik tel gibi.',
                       '<b>Gönderme sonlandırması (R18, R19: 49,9 Ω; R20: 10 Ω; C24: 22 nF).</b> TD+ ve TD− iki ucunu 3,3 V’a 49,9 Ω’la çeker; çip bu çıkışları akım olarak sürer ve bu dirençler hattın karşılığını (yükü) oluşturur. Orta uç (TCT) 10 Ω ile beslemeye bağlıdır, 22 nF ile süzülür.',
                       '<b>Alma hattı (C25, C26: 6,8 nF; R21, R22: 49,9 Ω; C27: 10 nF).</b> Alma fark çifti iki 6,8 nF ile bağlanır (DC ayrıştırma); 49,9 Ω’lar hattı sonlandırır ve orta noktada (RX_M) 10 nF ile toprağa süzülür.',
                       '<b>Bob Smith sonlandırması (R23, 0 Ω; RCT).</b> Mıknatısın alma tarafı orta ucu da bu noktaya bağlıdır: ortak kip gürültüsünü ve ışımayı azaltır.',
                       '<b>RJ45 kılıfı (C41: 1 nF, 2 kV).</b> Soketin metal kılıfını yüksek gerilime dayanıklı bir kondansatörle toprağa bağlar: ağ kablosundan gelen yüksek frekanslı gürültüyü akıtır ama düşük frekansta kart toprağıyla kılıf arasında yalıtım bırakır.']))
    h.append('<h3>Ethernet hatları neden fark çiftidir? Nasıl okursun?</h3><p>100 Mbit/sn Ethernet’te bilgi iki fark çiftiyle taşınır: biri göndermek, biri almak için. Fark çifti, iki hatta ters yönde aynı işaret demektir; alıcı yalnız <i>farkı</i> okur, bu yüzden iki hatta birden binen gürültü (ortak kip) silinir. İkisi de karttaki izlerde aynı uzunlukta ve yan yana yürümelidir. İzler 100 Ω’luk farksal empedanslı çift olarak tasarlanır [[bilgi]]. Kablo ve kart arasında transformatör (mıknatıs) bulunur: 1500 V’a yakın galvanik yalıtım sağlar [[bilgi]] ve iki tarafın toprak potansiyelini ayırır.</p>')
    # olculer
    satir = ''
    for ag in ('W_TXN', 'W_TXP', 'TD_P', 'TD_N', 'W_RXN', 'W_RXP', 'RX_A', 'RX_B', 'RD_P', 'RD_N'):
        satir += '<tr><td><code>%s</code></td><td>%s mm</td><td>%s</td></tr>' % (ag, sayi(iz_uzunlugu(v, ag), 3), viya_sayisi(v, ag))
    h.append('<h3>Karttaki ölçüler (yalnız bakır izler)</h3><table><tr><th>Ağ</th><th>İz uzunluğu</th><th>Delikli geçit</th></tr>%s</table>' % satir)
    h.append('<p>Gönderme çiftinde uzunluk farkı ≈ <b>%s mm</b> (W_TXN − W_TXP), alma çiftinde ≈ <b>%s mm</b>. 100 Mbit/sn (125 Mbaud MLT-3) için birkaç mm’lik fark sorun olmaz; asıl şart izlerin kısa ve yan yana olmasıdır. [[bilgi]]</p>' % (
        sayi(abs(iz_uzunlugu(v, 'W_TXN') - iz_uzunlugu(v, 'W_TXP')), 3), sayi(abs(iz_uzunlugu(v, 'W_RXN') - iz_uzunlugu(v, 'W_RXP')), 3)))
    h.append('<h2>5. Akım ve çalışma şartları</h2><table><tr><th>Büyüklük</th><th>Değer</th><th>Kaynak</th></tr>'
             '<tr><td>Besleme gerilimi</td><td>2,97 … 3,3 … 3,63 V</td><td>[[ds]] §5.3</td></tr>'
             '<tr><td>Akım (100 Mbit/sn bağlantı)</td><td>128 mA tipik; 132 mA gönderirken</td><td>[[ds]] §5.4</td></tr>'
             '<tr><td>Güç</td><td>≈ 3,3 V × 0,132 A = %s W</td><td>hesap</td></tr>'
             '<tr><td>Kapalı güç kipi (PHY down)</td><td>13 mA</td><td>[[ds]] §5.4</td></tr>'
             '<tr><td>Girişin yüksek eşiği</td><td>≥ 2,0 V (5,5 V’a kadar dayanır)</td><td>[[ds]] §5.3</td></tr>'
             '<tr><td>SPI hızı</td><td>en çok 80 MHz kuramsal; 33,3 MHz garantili</td><td>[[ds]] §5.5.4</td></tr>'
             '<tr><td>Sıfırlama</td><td>RSTn en az 500 µs alçak, sonra ≤ 1 ms PLL kilidi</td><td>[[ds]] §5.5.1</td></tr>'
             '<tr><td>MDIX</td><td>Otomatik çapraz algılama yok; karşı uç otomatik algılıyorsa her kablo çalışır</td><td>[[ds]] §5.5.6</td></tr></table>' % sayi(3.3 * 0.132, 3))
    h.append('<p>Bu kartın 3,3 V hattı yükü: W5500 ≈ 0,13 A + ESP32-S3 (Wi-Fi kapalı) ≈ 0,05–0,1 A + LoRa gönderirken ≈ 0,12 A + modem mantığı = ≈ 0,3–0,4 A; 3,3 V çeviricisinin tasarım payı (0,5 A) bunu karşılar. [[tahmin]]</p>')
    h.append('<h2>6. Parça kartları</h2><div class="kartlar">' + ''.join(v.kart_html(r) for r in REFS) + '</div>')
    h.append('<h2>7. Uç durumlar</h2><table><tr><th>Durum</th><th>Ne olur?</th></tr>'
             '<tr><td>Kablo takılı değil</td><td>LINKLED yüksek (kapalı); çip bağlantı arar, güç ≈ 65 mA tipik. [[ds]]</td></tr>'
             '<tr><td>Kablo takıldı ama karşı uç otomatik müzakere ediyor</td><td>PMODE 111 olduğundan çip hız (10/100) ve çift yönü kendisi seçer. [[ds]]</td></tr>'
             '<tr><td>Kablo kısa devre / ESD</td><td>Mıknatıs ve kılıf kondansatörü ilk savunmadır; bu kartta ayrıca bir TVS dizisi yok.</td></tr>'
             '<tr><td>3,3 V hattı çökerse</td><td>PLL kilit bozulur, bağlantı düşer ve yeniden kurulur; yazılım RSTn ile sıfırlamalıdır.</td></tr>'
             '<tr><td>SPI hattı paylaşımı</td><td>W5500’ün MISO’su SCSn yükseldiğinde yüksek empedans olur (veri sayfası). LoRa modülü de kendi NSS’i yükselince MISO’yu bırakır; iki çip aynı SPI hattını güvenle paylaşır. [[ds]]</td></tr></table>')
    h.append('<h2>8. Kartta nerede?</h2><p>Kurallar: kristal çipe en yakın; EXRES1 direnci ve TOCAP kondansatörü ucun hemen yanında; her AVDD ucuna yakın 100 nF; RJ45 kart kenarında; hat izleri kısa ve yan yana. Aşağıda ölçülen uzaklıklar:</p><p>' +
             ', '.join('%s %s mm' % (r, sayi(mesafe(v, 'U9', r), 3)) for r in ('Y1', 'R26', 'C38', 'C37', 'L3', 'J3', 'C28', 'C34')) + '.</p>')
    h.append(pano_kutusu(v, ['U9', 'J3', 'Y1', 'L3', 'R26', 'C37', 'C38', 'R14', 'R15', 'R16', 'R17', 'R18', 'R19', 'R20', 'R21', 'R22', 'C25', 'C26', 'C27', 'R23', 'R24', 'R25', 'C41', 'C28', 'C29', 'C30', 'C31', 'C32', 'C33', 'C34', 'C39', 'C40', 'R27', 'R28'],
                         [(1, 'U9'), (2, 'Y1'), (3, 'J3')], 'Ethernet bölümü: çip, kristal, hat devreleri ve RJ45.'))
    h.append('<h2>9. Kaynaklar</h2><ul class="kaynak"><li>WIZnet W5500 veri sayfası v1.1.0: §1.1 pin tanımları, §5.1–5.5 elektriksel özellikler, kristal ve SPI zamanlaması, transformatör özellikleri, MDIX notu okundu. WIZnet referans şemaları (mıknatıslı/mıknatıssız) önceki oturumda incelendi.</li>'
             '<li>HanRun HR911105A veri sayfası bu çalışmada okunmadı; sayılar WIZnet referansından ve genel bilgidendir. [[dogrulanmadi]]</li></ul>')
    return ''.join(h)
