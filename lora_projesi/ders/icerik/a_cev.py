"""TPS62933 ile 12 V'tan sabit gerilim ureten iki cevirici bolumunun ortak yapisi (3,3 V ve modem 3,8 V)."""
import math
import cizim as CZ
from icerik.yardim import *
from deger import sayi as dsayi, bicim


def _parca_degeri(v, ref):
    return v.deg(ref)


def sema(v, c):
    cevre = c['sema_genislik']
    cz = CZ.Cizim(c['ad'] + ' şeması', cevre, 520, v.parca)
    cz.bolge(10, 8, cevre - 20, 502, c['bolge_baslik'])
    ic = c['ic']
    sol = [(2, 'EN'), (3, 'VIN')] if c.get('en') else [(3, 'VIN'), (2, 'EN', 'nc'), (1, 'RT', 'nc')]
    sag = [(6, 'BST'), (5, 'SW'), (8, 'FB'), (7, 'SS')]
    P = cz.kutu(ic, 300, 110, sol, sag, alt=[(4, 'GND')], genislik=160, baslik='TPS62933', pinaralik=30)
    ry = P['3'][1]
    # giris
    cz.ray('+12V', 60, ry)
    cz.tel((60, ry), (140, ry), (220, ry), (285, ry))
    cz.kondansator(c['cin'], 140, ry, 90); cz.kondansator(c['cin_hf'], 220, ry, 90)
    cz.toprak(140, ry + 60); cz.toprak(220, ry + 60); cz.nokta(140, ry); cz.nokta(220, ry)
    if c.get('en'):
        cz.tel((P['2'][0], P['2'][1]), (250, P['2'][1])); cz.etiket('MODEM_EN', 250, P['2'][1], 'sol')
    cz.toprak(P['4'][0], P['4'][1])
    # BST, SW, bobin
    ybst, ysw, yfb, yss = P['6'][1], P['5'][1], P['8'][1], P['7'][1]
    cz.tel((P['6'][0], ybst), (500, ybst))
    cz.kondansator(c['cbst'], 500, ybst, 0)
    cz.tel((560, ybst), (560, ysw))
    cz.tel((P['5'][0], ysw), (560, ysw), (620, ysw))
    cz.nokta(560, ysw)
    cz.bobin(c['L'], 620, ysw, 0)
    cz.tel((680, ysw), (720, ysw))
    cz.etiket(c['sw_net'], 580, ysw + 22, 'sag')
    # cikis rayi
    xs = c.get('xs') or [740 + 90 * i for i in range(len(c['cout']))]
    cz.tel((680, ysw), (xs[0] - 20, ysw))
    pts = [(xs[0] - 20, ysw)] + [(x, ysw) for x in xs] + [(xs[-1] + 70, ysw)]
    cz.tel(*pts)
    for i, (ref, x) in enumerate(zip(c['cout'], xs)):
        kut = ref in c.get('kutuplu', [])
        dy = 34 if i % 2 else 0
        if ref.startswith('D'):
            cz.diyot(ref, x, ysw + 60, 270, 'zener', yazi_dy=dy)
        else:
            cz.kondansator(ref, x, ysw, 90, kutuplu=kut, yazi_dy=dy)
        cz.toprak(x, ysw + 60); cz.nokta(x, ysw)
    cz.ray(c['out_net'], xs[-1] + 70, ysw)
    cz.etiket(c['out_net'], 735, ysw - 8, 'yukari')
    # FB ve SS etiketleri
    cz.tel((P['8'][0], yfb), (520, yfb)); cz.etiket(c['fb_net'], 520, yfb, 'sag')
    cz.tel((P['7'][0], yss), (520, yss)); cz.etiket(c['ss_net'], 520, yss, 'sag')
    by = 330
    # bolucu
    cz.ray(c['out_net'], 640, by)
    cz.direnc(c['rt'], 640, by, 90)
    cz.tel((640, by + 60), (640, by + 66), (640, by + 72)); cz.etiket(c['fb_net'], 640, by + 66, 'sag')
    cz.direnc(c['rb'], 640, by + 72, 90); cz.toprak(640, by + 132)
    cz.not_(580, by + 160, 'Çıkış gerilimi bölücüsü', 'start')
    # yumusak baslatma
    cz.tel((780, by + 66), (780, by + 72)); cz.etiket(c['ss_net'], 780, by + 66, 'sag')
    cz.kondansator(c['css'], 780, by + 72, 90); cz.toprak(780, by + 132)
    cz.not_(740, by + 160, 'Yumuşak başlatma', 'start')
    if c.get('en'):
        cz.ray('+3V3', 80, by); cz.direnc('R6', 80, by, 90)
        cz.tel((80, by + 60), (80, by + 66), (80, by + 72)); cz.etiket('MODEM_EN', 80, by + 66, 'sag')
        cz.direnc('R7', 250, by + 72, 180)
        cz.tel((190, by + 72), (80, by + 72))
        cz.etiket('MODEM_EN_CTL', 250, by + 72, 'sag')
        cz.not_(50, by + 125, 'Etkinleştirme: işlemci IO2 ile açıp kapatır', 'start')
    cz.not_(40, 70, c['sema_not'], 'start')
    return cz, P


def bolum_html(v, c):
    ic = c['ic']
    Rt, Rb = v.deg(c['rt']), v.deg(c['rb'])
    L = v.deg(c['L'])
    f = 500e3
    vref = 0.8
    vout = vref * (1 + Rt / Rb)
    # tolerans: referans 792..808 mV (25 C) ve direncler %1
    vmin = 0.792 * (1 + (Rt * 0.99) / (Rb * 1.01)); vmax = 0.808 * (1 + (Rt * 1.01) / (Rb * 0.99))
    css = v.deg(c['css']); tss = css * vref / 5.5e-6
    cout_nom = sum(v.deg(r) for r in c['cout'] if r.startswith('C'))
    vin, vinx = 12.0, 15.0
    D = vout / vin
    dI = (vout / vinx) * (vinx - vout) / (L * f)
    dI12 = (vout / vin) * (vin - vout) / (L * f)
    iy = c['iyuk']
    ipk = iy + dI / 2; irms = math.sqrt(iy ** 2 + dI ** 2 / 12)
    ton = D / f
    cin_rms = iy * math.sqrt((vout / vin) * (vin - vout) / vin)
    cond = iy ** 2 * (D * 0.076 + (1 - D) * 0.032)
    h = []
    h.append('<h1>%s</h1><p class="ozet">%s</p>' % (c['baslik'], c['ozet']))
    h.append(kutu('not', '<ul><li>Düşüren (buck) çevirici bir bobinle gerilimi nasıl indirir? Formülünü kendin çıkar.</li><li>Çıkış gerilimini belirleyen iki direncin değerini hesapla ve toleransın sonucu nasıl oynattığını gör.</li>'
                  '<li>Bobin, çıkış kondansatörü, giriş kondansatörü, yumuşak başlatma kondansatörü, bootstrap kondansatörü: her birini veri sayfasındaki denklemle seç.</li><li>%s</li></ul>' % c['ozel_ogren'], 'Bu bölümde öğreneceklerin:'))
    h.append('<h2>1. Büyük resim</h2><p>%s</p>' % c['buyuk_resim'])
    h.append('<h2>2. Şema</h2>')
    cz, P = sema(v, c)
    hata = cz.denetle(v.aglar)
    assert not hata, hata
    h.append(sema_kutusu(cz))
    h.append(isaretli(c['isaretler']))
    h.append('<h2>3. Düşüren çevirici nasıl çalışır?</h2>')
    h.append('<p>İçeride iki anahtar (alan etkili transistör) vardır: üst anahtar girişi bobine bağlar, alt anahtar bobinin ucunu toprağa bağlar. Bu çip her ikisini de içinde taşır (üst 76 mΩ, alt 32 mΩ [[ds]]). Üst anahtar kapalıyken (açık süresi <i>t<sub>ON</sub></i>) bobine <i>V<sub>giriş</sub> − V<sub>çıkış</sub></i> gerilimi uygulanır ve akımı doğrusal artar; '
             'üst anahtar kapanınca alt anahtar açılır, bobin akımı <i>−V<sub>çıkış</sub></i> eğimiyle azalır. Kararlı durumda bobin akımının ortalaması yükteki akıma eşittir ve bobin gerilimi bir periyotta ortalama sıfırdır (volt·saniye dengesi):</p>')
    h.append(formul('(V<sub>giriş</sub> − V<sub>çıkış</sub>) × t<sub>ON</sub> = V<sub>çıkış</sub> × t<sub>OFF</sub>   ⟹   D = t<sub>ON</sub> / T = V<sub>çıkış</sub> / V<sub>giriş</sub>'))
    h.append(formul('ΔI<sub>L</sub> = (V<sub>giriş</sub> − V<sub>çıkış</sub>) × D / (f × L)   (bobin akımı dalgalanması, tepeden tepeye)'))
    h.append('<p>Bu kartta: V<sub>giriş</sub> = 12 V, V<sub>çıkış</sub> = %s V ⟹ D = %s, açık süre t<sub>ON</sub> = D / f = %s ns. Çipin en küçük açık süresi 70 ns’dir [[ds]]; %s ns bunun üstündedir, dolayısıyla çip frekansını kısmadan çalışır.</p>' % (sayi(vout, 4), sayi(D, 3), sayi(ton * 1e9, 3), sayi(ton * 1e9, 3)))
    # dalga bicimi grafigi (analitik)
    N = 3; pts = 60
    tt = []; il = []; vs = []
    T = 1 / f
    ilow = iy - dI12 / 2
    for k in range(N * pts + 1):
        t = k / pts * T
        ph = (t % T) / T
        if ph < D:
            i = ilow + (vin - vout) / L * (ph * T)
            vsw = vin
        else:
            i = ilow + dI12 - vout / L * ((ph - D) * T)
            vsw = 0
        tt.append(t * 1e6); il.append(i); vs.append(vsw)
    h.append(grafik(tt, [('Bobin akımı (A)', il, '#1e88e5')], 'zaman (µs)', 'akım (A)'))
    h.append(grafik(tt, [('SW gerilimi (V)', vs, '#e53935')], 'zaman (µs)', 'gerilim (V)'))
    h.append('<p class="kaynak">Üstteki iki grafik bu bölümün gerçek değerleriyle (L = %s µH, f = 500 kHz, V<sub>giriş</sub> = 12 V, V<sub>çıkış</sub> = %s V, yük %s A) yukarıdaki denklemlerden hesaplanmıştır; ölçüm değildir. [[tahmin]]</p>' % (sayi(L * 1e6), sayi(vout, 4), sayi(iy)))
    h.append('<h2>4. Bunu sıfırdan nasıl tasarlarsın? (veri sayfası TPS62933, §10.2)</h2>')
    h.append('<h3>Adım 1 — İhtiyaçlar</h3><table><tr><th>Büyüklük</th><th>Değer</th><th>Kaynak</th></tr>%s</table>' % c['ihtiyac_satirlari'])
    h.append('<h3>Adım 2 — Çıkış gerilimi bölücüsü (denklem 1)</h3>')
    h.append(formul('V<sub>çıkış</sub> = V<sub>REF</sub> × (1 + R<sub>üst</sub> / R<sub>alt</sub>),   V<sub>REF</sub> = 0,8 V'))
    h.append('<p>Veri sayfası R<sub>alt</sub> = 10 kΩ ve R<sub>üst</sub> için %s önerir (en çok yüzde 1 toleranslı dirençler). [[ds]] Bu kartta R<sub>üst</sub> = %s (%s), R<sub>alt</sub> = %s ⟹ V<sub>çıkış</sub> = 0,8 × (1 + %s) = <b>%s V</b>.</p>' % (
        'tablo 10-2’de 3,3 V için 31,3 kΩ' if abs(vout - 3.3) < 0.2 else 'gerekli değeri denklem 1’den', bicim(Rt, 'Ω'), c['rt'], bicim(Rb, 'Ω'), sayi(Rt / Rb, 4), sayi(vout, 4)))
    h.append(hesap('geribesleme', [0.8, Rt, Rb]))
    h.append('<p><b>Tolerans:</b> referans gerilimi 25 °C’de 792–808 mV (tüm sıcaklıkta 784–816 mV) [[ds]]; dirençler %%1 ise çıkış gerilimi en kötü durumda <b>%s … %s V</b> aralığında değişir (referansın 25 °C değeri ve direnç toleransları birlikte). Bu, yükün (<i>%s</i>) kabul edeceği aralıkla kıyaslanmalıdır. %s</p>' % (sayi(vmin, 4), sayi(vmax, 4), c['yuk'], c['tolerans_yorum'](vmin, vmax)))
    h.append('<h3>Adım 3 — Anahtarlama frekansı</h3><p>RT ucu boşta bırakıldığında frekans 500 kHz’tir (450–550 kHz); toprağa bağlanırsa 1,2 MHz; bir direnç bağlanırsa 200 kHz–2,2 MHz arası ayarlanır. [[ds]] Yüksek frekans küçük bobin ve kondansatör demektir, ama anahtarlama kaybı ve ısı artar. 500 kHz verim ile boyut arasında dengelidir: veri sayfasındaki 3,3 V tavsiyesi (tablo 10-2) 500 kHz ve 4,7 µH’dir. [[ds]]</p>')
    h.append('<h3>Adım 4 — Bobin (denklem 15–18)</h3>')
    h.append(hesap('bobin', [vinx, vout, 500, L * 1e6]))
    h.append('<p>Kartta L = %s µH. En kötü giriş %s V (TVS’in bekleme gerilimi) için ΔI<sub>L</sub> = %s A; 12 V’ta %s A. Yük akımı %s A ise bobin tepe akımı I<sub>tepe</sub> = I + ΔI/2 = <b>%s A</b>, etkin değer I<sub>RMS</sub> = √(I² + ΔI²/12) = %s A. %s</p>' % (
        sayi(L * 1e6), sayi(vinx), sayi(dI, 3), sayi(dI12, 3), sayi(iy), sayi(ipk, 3), sayi(irms, 3), c['bobin_yorum'](ipk, irms, dI)))
    h.append(kutu('uyari', 'Veri sayfası: bobinin doyma akımı <b>en az</b> tam yükteki tepe akım kadar, <b>ideali</b> yüksek taraf anahtar akım sınırı (en çok 5,8 A; tipik 5 A) kadar olmalıdır. Bu kartın bobin şartı “Isat ≥ 5 A”dır: tipik sınıra yetişir, en kötü sınır olan 5,8 A’in altındadır. Kısa devrede bobinin doymaması için 6 A ve üzeri Isat’lı bir parça daha güvenlidir. Seçilen parçanın gerçek Isat ve DCR değerleri sipariş öncesi veri sayfasından doğrulanmalıdır. [[ds]] [[dogrulanmadi]]', 'Doğrulama borcu'))
    h.append('<h3>Adım 5 — Çıkış kondansatörü (denklem 19–21)</h3>')
    ripple = 0.4 * iy / (8 * f * cout_nom * 0.5)  # DC kayma ile yaridan hesap
    h.append('<p>Kartta çıkıştaki toplam anma kapasitesi %s µF (%s). Gerilim altında seramik kapasite düşer; yarıya düştüğünü varsayarsak etkin ≈ %s µF. Veri sayfasının 3,3 V / 500 kHz için önerisi: tipik etkin 40 µF, en az 15 µF. [[ds]] Kapasitif gerilim dalgalanması ΔV<sub>C</sub> = ΔI<sub>L</sub> / (8·f·C) = %s / (8 × 500·10³ × %s·10⁻⁶) ≈ <b>%s mV</b> (ESR payı ayrı eklenir). [[tahmin]] %s</p>' % (
        sayi(cout_nom * 1e6, 3), ', '.join(c['cout']), sayi(cout_nom * 1e6 / 2, 3), sayi(dI12, 3), sayi(cout_nom / 2 * 1e6, 3), sayi(dI12 / (8 * f * cout_nom / 2) * 1e3, 3), c['cout_yorum'](cout_nom, tss)))
    h.append('<h3>Adım 6 — Giriş kondansatörleri (denklem 22)</h3><p>Üst anahtar her periyotta girişten darbeli akım çeker. Giriş kondansatörünün etkin (RMS) akımı: I<sub>CIN,RMS</sub> = I × √[(V<sub>çıkış</sub>/V<sub>giriş</sub>) × (V<sub>giriş</sub> − V<sub>çıkış</sub>)/V<sub>giriş</sub>] = %s × √(%s × %s) = <b>%s A</b> (12 V ve %s A yük için). Veri sayfası 10 µF seramik + 0,1 µF ve gerekirse bir hacimli kondansatör ister. [[ds]] Bu kartta C-bulk %s, C-küçük %s; ayrıca 12 V girişte 220 µF elektrolitik vardır (1. bölüm).</p>' % (
        sayi(iy), sayi(D, 3), sayi(1 - D, 3), sayi(cin_rms, 3), sayi(iy), c['cin'], c['cin_hf']))
    h.append('<h3>Adım 7 — Yumuşak başlatma ve bootstrap</h3><p>Yumuşak başlatma süresi <i>t<sub>SS</sub> = C<sub>SS</sub> × V<sub>REF</sub> / I<sub>SS</sub></i> (I<sub>SS</sub> = 5,5 µA tipik [[ds]]): %s nF × 0,8 V / 5,5 µA = <b>%s ms</b>. Aşırı yükte çip “hıçkırık (hiccup)” moduna girerse kapalı kalma süresi 10,5 × t<sub>SS</sub> = %s ms olur. En az 6,8 nF gerekir (SS ucu boşta bırakılamaz). [[ds]]</p>' % (sayi(css * 1e9, 3), sayi(tss * 1e3, 3), sayi(10.5 * tss * 1e3, 3)))
    h.append('<p>Bootstrap kondansatörü (BST–SW arası, %s) üst anahtarın kapısını sürmek için gerekli yükseltilmiş gerilimi sağlar; veri sayfası 100 nF seramik, X5R ya da daha iyi ve en az 16 V ister. [[ds]] Kartta 100 nF 25 V.</p>' % c['cbst'])
    h.append('<h3>Adım 8 — Kayıp ve verim hakkında bir fikir</h3><p>İletim kaybı (yalnız çipin anahtarları): P ≈ I² × (D × 76 mΩ + (1 − D) × 32 mΩ) = %s² × (%s × 0,076 + %s × 0,032) = <b>%s W</b>. Bobin DCR’ı, anahtarlama kaybı ve hareketsiz akım ayrıca eklenir; ısı bir kart sorunu değil bir tasarım parametresidir ama burada çok düşüktür. [[tahmin]]</p>' % (sayi(iy), sayi(D, 3), sayi(1 - D, 3), sayi(cond, 3)))
    h.append('<h2>5. Parça kartları</h2><div class="kartlar">' + ''.join(v.kart_html(r) for r in c['refs']) + '</div>')
    h.append('<h2>6. Uç durumlar</h2><table><tr><th>Durum</th><th>Ne olur?</th></tr>%s</table>' % c['uc_satirlari'])
    h.append('<h2>7. Yerleşim kuralları (veri sayfası §12.1) ve karttaki ölçümler</h2><ul>'
             '<li>Bobin, giriş ve çıkış kondansatörleri ve çip <b>aynı katmanda</b> ve birbirine yakın. [[ds]]</li>'
             '<li>VIN ve GND ucuna 0,1 µF kondansatör <b>mümkün olduğunca yakın</b>: EMI için kilit. [[ds]]</li>'
             '<li>SW izi <b>kısa ve geniş</b>. [[ds]]</li><li>Geri besleme bölücüsü FB ucuna yakın ve anahtarlama izlerinden uzak; çıkıştan ayrı bir iz alınır. [[ds]]</li></ul>')
    ref = c['ic']
    h.append('<p>Ölçülen merkez uzaklıkları (çipe): %s.</p>' % ', '.join('%s %s mm' % (r, sayi(mesafe(v, ref, r), 3)) for r in [c['cin'], c['cin_hf'], c['L'], c['css'], c['rt'], c['rb']]))
    h.append('<p>İz genişlikleri (kartta ölçülen): SW ağı <code>%s</code> %s mm, çıkış ağı <code>%s</code> %s mm.</p>' % (c['sw_net'], ', '.join(sayi(w) for w in iz_genislikleri(v, c['sw_net'])), c['out_net'], ', '.join(sayi(w) for w in iz_genislikleri(v, c['out_net']))))
    h.append(pano_kutusu(v, c['refs'], [(i + 1, r) for i, r in enumerate(c['isaret_ref'])], 'Çip, bobin ve kondansatörler birbirine yakındır; geri besleme bölücüsü çipin FB ucuna yakın durmalıdır.'))
    h.append('<h2>8. Kaynaklar</h2><ul class="kaynak"><li>TI TPS62933 veri sayfası SLUSEA4D: §7–§9 (pinler, elektriksel özellikler, §9.3 işlev), §10.2 (tasarım adımları, denklemler 14–23), §12.1 (yerleşim) bu çalışmada okundu.</li><li>%s</li></ul>' % c['kaynak_ek'])
    return ''.join(h)
