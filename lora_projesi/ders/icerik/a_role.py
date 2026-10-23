import cizim as CZ
from icerik.yardim import *

ID = 'role'
BASLIK = '9. Röle: 12 voltluk lambayı açıp kapatmak'
OZET = 'Küçük bir işlemci çıkışıyla amper mertebesinde bir yükü sürmek: transistör sürücü, röle bobini, sönüm diyodu ve kontak akım yolu.'
REFS = ['K1', 'Q2', 'R37', 'R38', 'D7', 'J6']


def sema(v):
    c = CZ.Cizim('Alıcı röle sürücüsü', 1000, 480, v.parca)
    c.bolge(10, 8, 980, 462, 'RÖLE  —  işlemci çıkışı → transistör → bobin;  kontak → lamba')
    K = c.kutu('K1', 330, 100, [(2, 'bobin +'), (5, 'bobin −')], [(1, 'ortak'), (3, 'açık kontak')], genislik=150, baslik='SRD-12VDC-SL-A', pinaralik=30)
    kx2, ky2 = K['2']; kx5, ky5 = K['5']
    c.ray('+12V', 110, ky2); c.tel((110, ky2), (200, ky2), (kx2, ky2)); c.nokta(200, ky2)
    c.diyot('D7', 200, 220, 270, 'schottky')
    c.tel((200, ky2), (200, 160))
    c.tel((kx5, ky5), (250, ky5), (250, 220), (250, 270)); c.nokta(250, 220)
    c.tel((200, 220), (250, 220))
    c.etiket('ROLE_L', 250, 190, 'sag') if False else None
    Qd = c.npn('Q2', 210, 300)
    c.tel((250, 270), (Qd['C'][0], Qd['C'][1]))
    c.toprak(*Qd['E'])
    c.etiket('ROLE_L', 262, 250, 'sag') if False else None
    c.direnc('R37', 80, 300, 0)
    c.etiket('ROLE_CTL', 80, 300, 'sol')
    c.tel((140, 300), (170, 300), (210, 300)); c.nokta(170, 300)
    c.etiket('Q2_B', 170, 300, 'yukari')
    r = c.direnc('R38', 170, 300, 90); c.toprak(*r['b'])
    # kontak tarafi
    kx1, ky1 = K['1']; kx3, ky3 = K['3']
    c.tel((kx1, ky1), (540, ky1)); c.etiket('+12V_IN', 540, ky1, 'sag')
    c.not_(640, ky1 - 6, '← klemens girişinden doğrudan (sigortasız, korumasız)', 'start')
    J = c.kutu('J6', 720, 140, [(1, '+ lamba'), (2, '− lamba')], [], genislik=100, baslik='LAMBA klemensi', pinaralik=30)
    c.tel((kx3, ky3), (560, ky3), (J['1'][0], ky3 if False else J['1'][1])) if False else None
    c.tel((kx3, ky3), (560, ky3), (560, J['1'][1]), (J['1'][0], J['1'][1])); c.etiket('LAMBA_SW', 560, ky3, 'yukari')
    c.tel(J['2'], (J['2'][0] - 20, J['2'][1])); c.toprak(J['2'][0] - 20, J['2'][1])
    c.not_(40, 40, 'Bobin akımı transistörden, lamba akımı kontaktan geçer: iki devre birbirinden elektriksel olarak ayrıdır.', 'start')
    c.isaret(1, 180, 120); c.isaret(2, 300, 330); c.isaret(3, 390, 100); c.isaret(4, 650, 150)
    return c


def uret(ver, ctx):
    v = ver
    c = sema(v)
    hata = c.denetle(v.aglar)
    assert not hata, hata
    rl = sim_veri('sim_role')['role']
    h = ['<h1>%s</h1><p class="ozet">%s</p>' % (BASLIK, OZET)]
    h.append(kutu('not', '<ul><li>Neden bir işlemci ayağı bir rölenin bobinini doğrudan süremez?</li><li>NPN transistörle anahtarlama: taban direnci, aşağı çekme direnci, doyma. Hesabını yap.</li><li>Sönüm (flyback) diyodu nedir, neden olmazsa transistör ölür?</li><li>Kontak akımını ve iz genişliğini kendin hesapla.</li></ul>', 'Bu bölümde öğreneceklerin:'))
    h.append('<h2>1. Büyük resim</h2><p>İşlemci ayağı ancak onlarca mA verebilir ve 3,3 V’tur. Lamba ise 12 V ve belki 3 A ister. Aradaki köprü bir <b>röledir</b>: içinde bir elektromıknatıs bobini (küçük akım, 12 V) ve ona bağlı mekanik bir kontak (büyük akım) vardır; iki devre birbirinden elektriksel olarak ayrıdır. '
             'Bobini de ayak doğrudan sürmez: bobin 12 V ve yaklaşık 30 mA çeker; ayak 3,3 V’tur. Araya bir NPN transistör girer: ayaktan çok küçük bir taban akımı, bobin akımını açar-kapar.</p>')
    h.append('<h2>2. Şema</h2>' + sema_kutusu(c))
    h.append(isaretli(['<b>Sönüm diyodu (D7, SS14).</b> Bobin, akım kesilirken akımı sürdürmeye çalışır ve yüksek bir ters gerilim üretir; diyot bu akıma bir yol verir ve gerilimi kenetler. Diyot olmasa transistör çıkışta yüzlerce volt görüp bozulur.',
                       '<b>Sürücü transistör (Q2, MMBT2222A), taban direnci (R37: 1 kΩ), aşağı çekme (R38: 10 kΩ).</b> İşlemci ayağı yüksek olunca R37 üzerinden taban akımı akar, transistör doyar ve bobinin eksi ucunu toprağa bağlar: bobin enerjilenir. Ayak alçak ya da boşta (açılışta) iken R38 tabanı toprakta tutar: röle çekmez.',
                       '<b>Röle (K1).</b> Bobin 12 V ve yaklaşık 400 Ω’dur. Kontak bu kartta “normalde açık”tır (lamba kapalı); bobin enerjilenince kontak kapanır.',
                       '<b>Lamba klemensi (J6).</b> Kontağın bir ucu klemens girişinin kendisinden (+12V_IN) beslenir, diğer ucu lambaya (LAMBA_SW) gider.']))
    h.append('<h2>3. Hesaplar</h2>')
    ib = (3.3 - 0.7) / 1000 - 0.7 / 10000
    h.append('<h3>3.1 Bobin akımı</h3><p>I<sub>bobin</sub> = V / R = 12 V / 400 Ω = <b>30 mA</b>; güç = V × I = 0,36 W. (Parça: Songle SRD-12VDC-SL-A; 400 Ω ve 10 A kontak akımı genel bilgidir, veri sayfası bu çalışmada okunmadı. [[bilgi]] [[dogrulanmadi]])</p>')
    h.append('<h3>3.2 Taban akımı ve doyma</h3><p>Ayak yüksekte iken taban akımı I<sub>B</sub> ≈ (3,3 − 0,7)/1 kΩ − 0,7/10 kΩ = <b>%s mA</b>. Bobin akımı 30 mA olduğundan gereken “zorlanmış akım kazancı” 30/%s ≈ %s: gerçek akım kazancının (≥ 100 [[bilgi]]) çok altındadır, yani transistör <b>sert doyma</b>dadır ve toplayıcı–yayıcı gerilimi çok küçüktür.</p>' % (sayi(ib * 1e3, 3), sayi(ib * 1e3, 3), sayi(0.03 / ib, 3)))
    h.append(hesap('ohm', [2.6, 1000]))
    h.append('<h3>3.3 Benzetim (genel modellerle) [[tahmin]]</h3><p>Aşağıdaki grafik, bobini 400 Ω + 80 mH olarak modelleyen bir ngspice benzetiminden alınmıştır: kapı 1 ms’de 3,3 V olur, 5 ms’de düşer.</p>')
    h.append(grafik(rl['t_ms'], [('Ayak (V)', rl['vg'], '#43a047'), ('Toplayıcı (V)', rl['vc'], '#e53935')], 'zaman (ms)', 'gerilim (V)', cizgiler=[(12, '+12 V')]))
    h.append(grafik(rl['t_ms'], [('Bobin akımı (A)', rl['ic'], '#1e88e5')], 'zaman (ms)', 'akım (A)'))
    h.append('<p>Sonuçlar: bobin akımı en çok <b>29,8 mA</b>, doyma gerilimi V<sub>CE,sat</sub> = <b>62 mV</b> ve kesilirken toplayıcının tepe gerilimi <b>12,2 V</b> (12 V + diyot düşümü): transistör kesilirken 12,2 V’u kolayca taşır. Diyot olmasaydı, L·dI/dt çok büyük bir sivri uç yapardı. (Modeller genel; gerçek 2N2222 ve SS14 parametreleri veri sayfasından doğrulanmalı. [[dogrulanmadi]])</p>')
    h.append('<h3>3.4 Kontak akımı ve iz genişliği</h3><p>Lamba akımını bilmiyoruz; teklifte yoktu. Çalışma varsayımı 3 A (36 W). Röle kontağı genel olarak 10 A (28 V DC’ye kadar) taşır [[bilgi]] [[dogrulanmadi]]; ama akkor telli lambada ilk anda akım 10 katına çıkabilir [[bilgi]]: 30 A, bu kontak için fazla olabilir. Lamba türü (LED/akkor) öğrenilmeden röle ve iz değerleri kesinleşmez.</p>')
    h.append(hesap('iz', [3, 10, 35, 1]))
    h.append(iz_taramasi(v, [('LAMBA_SW', 3.0, 'lamba (varsayım)'), ('+12V_IN', 3.0, 'kontak girişi (varsayım)'), ('ROLE_L', 0.03, 'bobin')]))
    h.append(kutu('not', 'Lamba hattı karta 1,4 mm genişlikte ve viyasız çizildi (önceki 0,4 mm yetersizdi). Akım 3 A’i aşarsa genişlik yeniden hesaplanmalıdır; tablodaki ölçü bunu kendiliğinden gösterir.', 'Giderildi'))
    h.append('<h2>4. Parça kartları</h2><div class="kartlar">' + ''.join(v.kart_html(r) for r in REFS) + '</div>')
    h.append('<h2>5. Uç durumlar</h2><table><tr><th>Durum</th><th>Ne olur?</th></tr>'
             '<tr><td>İşlemci açılıyor (ayak belirsiz)</td><td>R38 tabanı toprakta tutar: röle çekmez, lamba yanmaz. IO38 bir açılış (strapping) ayağı değildir. [[ds]]</td></tr>'
             '<tr><td>Röle çekili, 12 V çöktü</td><td>Bobin gerilimi düşünce kontak bırakır; lamba söner.</td></tr>'
             '<tr><td>Bobin kesilirken</td><td>Diyot akımı sürdürür; bırakma ≈ mekanik süre (birkaç ms) + diyot nedeniyle biraz uzun. [[bilgi]]</td></tr>'
             '<tr><td>Kontak yapışması</td><td>Aşırı ilk akım kontağı kaynatabilir; lamba cinsi öğrenilince boyutlandırılır.</td></tr>'
             '<tr><td>Lamba kısa devre</td><td>Lamba hattı sigortasız ve korumasızdır: 12 V girişten kontağa gider; lambanın kendi sigortası şart. (Karttaki PTC lamba akımını görmez.)</td></tr></table>')
    h.append('<h2>6. Kartta nerede?</h2>' + pano_kutusu(v, REFS, [(1, 'K1'), (2, 'Q2'), (3, 'D7'), (4, 'J6')], 'Röle ve lamba klemensi kart kenarında; yüksek akım izleri kısa ve geniş olmalı, sinyal izlerinden uzak.'))
    h.append('<h2>7. Kaynaklar</h2><ul class="kaynak"><li>Benzetim: <code>simulasyon/role_surucu.cir</code> (ngspice; genel modeller).</li><li>Songle SRD, MMBT2222A, SS14 veri sayfaları bu çalışmada okunmadı; sayılar genel bilgidir.</li></ul>')
    return ''.join(h)
