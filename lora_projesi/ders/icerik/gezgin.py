import re, json, html, math
import pano as PN
from icerik.yardim import *

BASLIK = {'verici': 'Verici', 'alici': 'Alıcı'}

SORULAR = {
    'verici': [
        ('Anten hattının 50 Ω olması', 'Hat genişliği 0,40 mm, altındaki yalıtkan (prepreg) kalınlığı 0,21 mm varsayıldı. Üreticinin gerçek katman dizilimi bilinmeden 50 Ω kesin değildir.', 'Karar sizde: siparişten önce üreticiden katman dizilimini isteyeceğiz ve hesabı o değerle yenileyeceğim.'),
        ('Pil ömrü', 'Uyku akımı veri sayfalarından toplandı (yaklaşık 40–50 µA); gerçek ölçüm yok.', 'Çözüm ancak prototip ölçümüyle olur.'),
    ],
    'alici': [
        ('W5500 kristal hatları', 'XI yaklaşık 19,5 mm, XO yaklaşık 20,9 mm; veri sayfası kristalin çipe yakın olmasını ister. Hesaplanan yük kayması ≈ 2 ppm (Ethernet sınırı ±50 ppm).', 'Prototipte ağ bağlantısı denenmeli; sorun çıkarsa W5500 çevresi yeniden yerleştirilir.'),
        ('Ethernet çiftlerinin uzunluğu', 'TX çifti 2,1 mm, RX çifti 2,8 mm farklı (≈ 12 ve 17 ps; sembol süresi 8000 ps). Hangi iz parçalarının hangi çifti oluşturduğu ağ adlarından okundu.', 'Hızda sorun beklenmez; WIZnet “eşit uzunluk” der, tam eşitlenmesini ister misiniz?'),
        ('A7670SA son ekleri ve stok', 'LASC / LASE / FASE / MASC farkı SIMCom belgelerinde yazılı değil; LCSC’de LASE’den 1, LASC’den 97 adet görüldü (100 takım gerekir).', 'Hangi son ek? Satıcıya yazılı soru sorulacak; ayak izi hepsi için aynıdır.'),
        ('Ra-01H ayak izi', 'Ra-01H belgesinde ölçü çizimi yok; pad ölçüleri aynı boyuttaki Ra-01 kılavuzundan alındı.', 'Üretimden önce Ai-Thinker’e teyit ettirilecek.'),
        ('Lamba akımı', 'Teklifte yoktu; 2 A varsayıldı (iz 0,8 mm).', 'Gerçek akım kaç amper?'),
        ('Modem besleme hattı', 'VBAT_MOD 41 mm boyunca 1,0 mm, geri kalanında 0,4 mm (SIMCom ≥ 2 mm ister); bobinden modül pedlerine hesaplanan direnç 18–19 mΩ. 2,8 A patlama benzetimi çeviricinin döngü bant genişliğine bağlı: 20 kHz’de 3,54 V, 10 kHz’de 2,9 V (alt sınır 3,4 V).', 'Prototipte VBAT patlaması osiloskopla ölçülmeli.'),
        ('Dört katman dizilimi', 'Katman kalınlıkları varsayım.', 'Üretici seçilince doğrulanacak.'),
    ],
}

BULUNAN = {
    'verici': [
        'LORA_DIO0 izi, LoRa modülünün DIO1 ayağına 0,1486 mm yaklaşıyordu (sınır 0,15 mm; önceki RFM95W’li çizimde): iz yeniden çizildi, kural denetimi temizlendi.',
    ],
    'alici': [
        'TXB0104 seviye çeviricisinin kullanılmayan A4/B4 girişleri boştaydı: toprağa bağlandı, şema ve kart güncellendi.',
        'USB tek başına çalışırken Schottky diyot (SS14) yüzünden +3V3 hattı ≈ 2,9 V’a iniyordu (ESP32-S3 alt sınırı 3,0 V): LM66100 ideal diyot kondu.',
        'İlk seçilen güç bobininin doyma akımı (2,7 A) modemin 2,8 A’lik darbesi için yetersizdi: Bourns SRP7028A-4R7M (Isat ≈ 10 A) kondu.',
        'SIM hatlarındaki 50 pF’lık ESD dizisi SIMCom’un 60 pF sınırına çok yakındı ve 22 Ω seri dirençler yoktu: USBLC6-2SC6 (≈ 3,5 pF) ve R39–R41 (22 Ω) eklendi; PWRKEY/RESET uçlarına da USBLC6 kondu.',
        'W5500’ün +3V3 ayakları, iç katmandaki sinyal izleriyle büyük +3V3 düzleminden kopmuş küçük bir adaya iniyordu: ada ile düzlem arasına köprü viyası eklendi (bağlantısız ayak 2 → 0).',
        'Yönlendirici bazı toprak viyalarını iç katman izlerinin üstüne yerleştirmişti (51 açıklık ihlali): viyalar iç katman izlerinden kaçınacak biçimde yeniden yerleştirildi.',
        'SIM yuvasının alt yüz yasak alanına giren bir toprak izi çekildi.',
    ],
}


def _yerles(ogeler, MAXW, BOS=70, BAS=54):
    x = y = satir_h = 0.0
    W = 0.0
    yer = []
    for bid, bbas, w, h, ic in ogeler:
        if x + w > MAXW and x > 0:
            x = 0.0; y += satir_h + BOS; satir_h = 0.0
        yer.append((x, y))
        x += w + BOS
        W = max(W, x - BOS)
        satir_h = max(satir_h, h + BAS)
    return yer, max(W, 100), y + satir_h


def _sema_tuvali(bolumler):
    ogeler = []
    for bid, bbas, h in bolumler:
        say = 0
        toplam = len(re.findall(r'<svg class="sema" xmlns="[^"]*" viewBox="0 0 [\d.]+ [\d.]+"', h))
        for m in re.finditer(r'<svg class="sema" xmlns="[^"]*" viewBox="0 0 ([\d.]+) ([\d.]+)"[^>]*>(.*?)</svg>', h, re.S):
            say += 1
            ad = bbas + (' (şekil %d/%d)' % (say, toplam) if toplam > 1 else '')
            ogeler.append((bid, ad, float(m.group(1)), float(m.group(2)), m.group(3)))
    BOS, BAS = 70, 54
    en = None
    for MAXW in range(1500, 9000, 100):
        yer, W, H = _yerles(ogeler, MAXW)
        skor = abs(W / H - 1.55)
        if en is None or skor < en[0]:
            en = (skor, MAXW)
    yer, W, H = _yerles(ogeler, en[1])
    govde = []
    for (bid, ad, w, h, ic), (x, y) in zip(ogeler, yer):
        govde.append('<a href="%s.html"><text class="tamb" x="%s" y="%s">%s</text></a>' % (bid, x + 6, y + 30, html.escape(ad)))
        govde.append('<svg x="%s" y="%s" width="%s" height="%s" viewBox="0 0 %s %s" overflow="hidden">%s</svg>' % (x, y + BAS, w, h, w, h, ic))
    return ('<svg class="sema tamsema pz" id="sema-svg" viewBox="0 0 %s %s" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Tam şema">%s</svg>' % (round(W), round(H), ''.join(govde))), len(ogeler)


def _veri_json(ver):
    d = ver.d
    izuz = {}; gen = {}; kat = {}; viya = {}
    for t in d['izler']:
        x1, y1, x2, y2 = t['p']
        a = t['ag']
        izuz[a] = izuz.get(a, 0.0) + math.hypot(x2 - x1, y2 - y1)
        gen.setdefault(a, set()).add(t['w'])
        kat.setdefault(a, set()).add(t['k'])
    for v in d['viyalar']:
        viya[v['ag']] = viya.get(v['ag'], 0) + 1
    aglar = {}
    for ag, l in d['aglar'].items():
        aglar[ag] = {'pin': sorted([[r, str(n)] for r, n in l]), 'uz': round(izuz.get(ag, 0.0), 1), 'gen': sorted(gen.get(ag, [])), 'kat': sorted(kat.get(ag, [])), 'viya': viya.get(ag, 0)}
    parcalar = {}
    for r, p in d['parcalar'].items():
        k = d['konum'].get(r, {})
        parcalar[r] = {'d': p['deger'], 'fp': (p['fp'] or '').split(':')[-1], 'm': p['mpn'], 's': p['sembol'], 'g': p['grup'], 'dnp': bool(p['dnp']),
                       'yuz': 'arka' if k.get('arka') else 'ön', 'x': k.get('x'), 'y': k.get('y'), 'a': k.get('donme'),
                       'p': {no: [pin['ad'], pin['ag']] for no, pin in p['pinler'].items()}}
    return json.dumps({'parcalar': parcalar, 'aglar': aglar}, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')


def _tablolar(ver):
    d = ver.d
    sirala = lambda r: (re.match(r'[A-Z]+', r).group(), int(re.search(r'\d+', r).group()) if re.search(r'\d+', r) else 0)
    p = ['<table class="gz-tablo" id="tab-parca"><thead><tr><th>Ad</th><th>Değer</th><th>Kılıf</th><th>Yüz</th><th>Konum (mm)</th><th>Parça no / not</th></tr></thead><tbody>']
    for r in sorted(d['parcalar'], key=sirala):
        pr = d['parcalar'][r]; k = d['konum'].get(r, {})
        p.append('<tr data-ref="%s"><td><b>%s</b></td><td>%s</td><td><code>%s</code></td><td>%s</td><td>%s, %s</td><td>%s%s</td></tr>' % (
            html.escape(r), html.escape(r), html.escape(pr['deger']), html.escape((pr['fp'] or '').split(':')[-1]), 'arka' if k.get('arka') else 'ön', k.get('x', ''), k.get('y', ''),
            html.escape(pr['mpn'] or ''), ' · takılmaz (DNP)' if pr['dnp'] else ''))
    p.append('</tbody></table>')
    n = ['<table class="gz-tablo" id="tab-ag"><thead><tr><th>Ağ</th><th>Ayak</th><th>İz uzunluğu</th><th>İz genişliği</th><th>Viya</th><th>Ayaklar</th></tr></thead><tbody>']
    izuz = {}; gen = {}; viya = {}
    for t in d['izler']:
        x1, y1, x2, y2 = t['p']
        izuz[t['ag']] = izuz.get(t['ag'], 0.0) + math.hypot(x2 - x1, y2 - y1)
        gen.setdefault(t['ag'], set()).add(t['w'])
    for v in d['viyalar']:
        viya[v['ag']] = viya.get(v['ag'], 0) + 1
    for ag in sorted(d['aglar']):
        l = sorted([(r, str(no)) for r, no in d['aglar'][ag]], key=lambda q: (sirala(q[0]), q[1]))
        kisa = ', '.join('%s.%s' % q for q in l[:10]) + (' …(+%d)' % (len(l) - 10) if len(l) > 10 else '')
        n.append('<tr data-ag="%s"><td><b>%s</b></td><td>%d</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
            html.escape(ag), html.escape(ag), len(l), ('%s mm' % sayi(izuz[ag], 3)) if ag in izuz else '—', ', '.join(sayi(w) for w in sorted(gen[ag])) + ' mm' if ag in gen else '—', viya.get(ag, '—'), html.escape(kisa)))
    n.append('</tbody></table>')
    return ''.join(p), ''.join(n)


def _denetim(ver, ad):
    den = ver.d.get('denetim', {})
    d = ver.d
    uzun = lambda g: sum(math.hypot(t['p'][2] - t['p'][0], t['p'][3] - t['p'][1]) for t in d['izler'] if t['ag'] == g)
    kat = {}
    for t in d['izler']:
        kat[t['k']] = kat.get(t['k'], 0) + 1
    h = ['<h3>Ölçülen sayılar (her güncellemede yeniden ölçülür)</h3><table><tr><th>Ölçü</th><th>Değer</th></tr>']
    sat = [('Kart ölçüsü', '%s × %s mm, dört katman' % (sayi(d['kart']['g'], 4), sayi(d['kart']['y_'], 4))),
           ('Parça sayısı (ayak izi)', '%d' % len(d['konum'])), ('Ağ sayısı', '%d' % len(d['aglar'])),
           ('Bakır iz parçası', ', '.join('%s: %d' % (k, v) for k, v in sorted(kat.items()))), ('Delikli geçit (viya)', '%d' % len(d['viyalar']))]
    if den:
        sat += [('KiCad kural denetimi: hata', '<b>%d</b> %s' % (den['drc_hata'], '' if not den['drc_hata'] else str(den['drc_hata_turleri']))),
                ('KiCad kural denetimi: uyarı', '%d (%s)' % (den['drc_uyari'], ', '.join('%s: %d' % kv for kv in sorted(den['drc_uyari_turleri'].items())))),
                ('Bağlantısız ayak', '<b>%s</b>' % den['bagli_olmayan_ayak']),
                ('Kart ile şemanın ayak karşılaştırması', '%d ayaktan <b>%d</b> uyuşmazlık' % (den['pad_toplam'], den['pad_uyusmayan']))]
    for a, b in sat:
        h.append('<tr><td>%s</td><td>%s</td></tr>' % (a, b))
    h.append('</table>')
    h.append('<p>Uyarıların çoğu kütüphane parçasının kart dosyasındaki hâli ile kütüphanedeki hâlinin farklı olması (<code>lib_footprint_issues</code>) ve serigrafi çakışmalarıdır; üretimi engellemez, yalnızca baskı yazılarının okunurluğunu etkileyebilir. Hata sıfır olmadan kart üretime gönderilmez.</p>')
    h.append('<h3>Bu çalışmada bulunup düzeltilen kusurlar</h3><ul>' + ''.join('<li>%s</li>' % html.escape(x) for x in BULUNAN[ad]) + '</ul>')
    h.append('<h3>Kendi başıma çözemediğim ya da karara bağlı kalanlar (soru)</h3><table><tr><th>Konu</th><th>Durum</th><th>Soru / karar</th></tr>' + ''.join('<tr><td><b>%s</b></td><td>%s</td><td>%s</td></tr>' % (html.escape(a), html.escape(b), html.escape(c)) for a, b, c in SORULAR[ad]) + '</table>')
    return ''.join(h)


def sayfa_html(ver, ad, bolumler, kartlar_html):
    d = ver.d
    tuval, n_sema = _sema_tuvali(bolumler)
    kart = PN.pano_gezgin(d)
    ptab, ntab = _tablolar(ver)
    veri = _veri_json(ver)
    opts = ''.join('<option value="%s">' % html.escape(x) for x in sorted(list(d['parcalar']) + list(d['aglar'])))
    h = []
    h.append('<h1>%s kartı: tam tasarım gezgini</h1>' % BASLIK[ad])
    h.append('<p class="ozet">Tasarımın tamamı tek sayfada: bütün şema, kartın iki yüzü, bütün parçalar ve bütün bağlantılar. Bir parçaya ya da bir tele tıkla; şemada ve kartta birlikte işaretlenir, sağ üstte nedir, neye bağlıdır yazılır. Arama kutusuna <code>U1</code>, <code>R10</code> ya da <code>SPI_SCK</code> yaz.</p>')
    h.append('<div id="gezgin" class="gezgin" data-kart="%s">' % ad)
    h.append('<div class="gz-ust"><input id="gz-ara" list="gz-liste" placeholder="Parça ya da ağ ara (örn. U1, C12, +3V3, SPI_SCK) ve Enter\'a bas" autocomplete="off"><datalist id="gz-liste">%s</datalist>'
             '<button data-sekme="sema" class="aktif">Tam şema</button><button data-sekme="kart">Kart (iki yüz)</button><button data-sekme="parca">Parçalar (%d)</button><button data-sekme="ag">Ağlar (%d)</button><button data-sekme="denetim">Denetim ve sorular</button></div>' % (opts, len(d['parcalar']), len(d['aglar'])))
    h.append('<div class="gz-govde"><div class="gz-sol">')
    h.append('<section class="gz-sekme" id="sekme-sema"><p class="kaynak">Şema %d çizimden oluşur (her biri bağlantı listesiyle makine tarafından doğrulanmıştır; bütün parçalar bulunur). Başlığa tıklarsan o bölümün dersine gidersin. Tekerlek: yakınlaş. Sürükle: kaydır. Çift tıklama: tümünü göster.</p>%s</section>' % (n_sema, tuval))
    h.append('<section class="gz-sekme gizli" id="sekme-kart">'
             '<div class="panokontrol"><button data-yuz="on" class="aktif">Ön yüz</button><button data-yuz="arka">Arka yüz (ayna)</button>'
             '<label><input type="checkbox" data-gk="FCu" checked> Üst bakır</label><label><input type="checkbox" data-gk="In2"> İç 2 izleri</label><label><input type="checkbox" data-gk="BCu"> Alt bakır</label>'
             '<label><input type="checkbox" data-gk="viya" checked> Delikli geçit</label><label><input type="checkbox" data-gk="pad" checked> Ayaklar</label>'
             '<label><input type="checkbox" data-gk="ipekF" checked> Serigrafi</label><label><input type="checkbox" data-gk="avlu"> Parça sınırı</label><label><input type="checkbox" data-gk="ref" checked> Parça adları</label>'
             '<button data-sifirla="kart">Tüm kart</button></div>'
             '<div class="panoalan">%s</div>'
             '<p class="kaynak">Bakır dökümleri (toprak ve +3V3 düzlemleri) çizilmez; iç katmanlarda yalnızca izler gösterilir. Kart: %s × %s mm.</p></section>' % (kart, sayi(d['kart']['g'], 4), sayi(d['kart']['y_'], 4)))
    h.append('<section class="gz-sekme gizli" id="sekme-parca"><input class="gz-filtre" data-hedef="tab-parca" placeholder="Süz: ad, değer, kılıf…">%s</section>' % ptab)
    h.append('<section class="gz-sekme gizli" id="sekme-ag"><input class="gz-filtre" data-hedef="tab-ag" placeholder="Süz: ağ adı ya da parça…">%s</section>' % ntab)
    h.append('<section class="gz-sekme gizli" id="sekme-denetim">%s</section>' % _denetim(ver, ad))
    h.append('</div><aside class="gz-bilgi" id="gz-bilgi"><p class="kaynak">Bir parça ya da tel seç. Burada adı, değeri, kılıfı, kartta nerede olduğu, ayakları ve kime bağlı olduğu ve parçanın öğretici kartı görünür.</p></aside></div>')
    h.append('<script type="application/json" id="gezgin-veri">%s</script>' % veri)
    h.append('<div hidden id="kartlar-gizli">%s</div></div>' % kartlar_html)
    h.append('<script src="../varlik/gezgin.js"></script>')
    return ''.join(h)
