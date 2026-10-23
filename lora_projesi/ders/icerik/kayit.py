import os, re, html, importlib
from icerik.yardim import *

VERICI_BOLUMLER = ['v_guc', 'v_usb', 'v_islemci', 'v_dugme', 'v_lora']
ALICI_BOLUMLER = ['a_giris', 'a_cev33', 'a_cevmodem', 'a_usb', 'a_islemci', 'a_lora', 'a_eth', 'a_modem', 'a_role']


def nav_kur(bolumler):
    nav = [('Başlangıç', [('index.html', 'Giriş ve yol haritası'), ('temel/index.html', 'Temel bilgiler'), ('hesap.html', 'Hesap makineleri'), ('sozluk.html', 'Sözlük'), ('kaynak.html', 'Kaynaklar ve güven düzeyi')])]
    for kart, liste in bolumler.items():
        nav.append((kart, [(('%s/%s.html' % (kart.split()[0].lower(), mod.ID)), mod.BASLIK) for mod in liste]))
    return nav


def uret(cikti, ver, sayfa, icerik_dizin):
    bolumler = {}
    for ad, adlar in (('verici', VERICI_BOLUMLER), ('alici', ALICI_BOLUMLER)):
        bolumler[ad + ' kartı'] = [importlib.import_module('icerik.' + m) for m in adlar]
    nav = []
    from icerik import temel
    nav.append(('Temel bilgiler', [('temel/index.html', 'Temel bilgiler: içindekiler')] + [('temel/%s.html' % i, b) for i, b, o, f in temel.SAYFALAR]))
    nav.append(('Başlangıç', [('index.html', 'Giriş ve yol haritası'), ('hesap.html', 'Hesap makineleri'), ('sozluk.html', 'Sözlük'), ('kaynak.html', 'Kaynaklar ve güven düzeyi')]))
    nav.append(('Verici kartı', [('verici/index.html', 'Verici: genel bakış'), ('verici/tam.html', 'Tam tasarım gezgini')] + [('verici/%s.html' % m.ID, m.BASLIK) for m in bolumler['verici kartı']]))
    nav.append(('Alıcı kartı', [('alici/index.html', 'Alıcı: genel bakış'), ('alici/tam.html', 'Tam tasarım gezgini')] + [('alici/%s.html' % m.ID, m.BASLIK) for m in bolumler['alici kartı']]))

    def yaz(yol, baslik, govde, derinlik, aciklama='', genis=False):
        p = os.path.join(cikti, yol)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, 'w', encoding='utf-8').write(sayfa(baslik, govde, derinlik, nav, yol, aciklama, genis))

    from icerik import gezgin
    toplanan = {}
    for kart, ad in (('verici kartı', 'verici'), ('alici kartı', 'alici')):
        for m in bolumler[kart]:
            govde = m.uret(ver[ad], None)
            toplanan.setdefault(ad, []).append((m.ID, m.BASLIK, govde))
            yaz('%s/%s.html' % (ad, m.ID), m.BASLIK, govde, 1, m.OZET)
    for ad in ('verici', 'alici'):
        v = ver[ad]
        sirala = lambda r: (re.match(r'[A-Z]+', r).group(), int(re.search(r'\d+', r).group()) if re.search(r'\d+', r) else 0)
        kartlar = ''.join(v.kart_html(r) for r in sorted(v.d['parcalar'], key=sirala))
        yaz('%s/tam.html' % ad, gezgin.BASLIK[ad] + ': tam tasarım gezgini', gezgin.sayfa_html(v, ad, toplanan[ad], kartlar), 1, 'Tasarımın tamamı: şema, kart, parçalar, ağlar', genis=True)
    temel.uret(yaz)
    yaz('index.html', 'Giriş', giris(bolumler), 0, 'Elektronik tasarımı sıfırdan öğreten ders sitesi')
    yaz('verici/index.html', 'Verici: genel bakış', kart_giris('verici', bolumler['verici kartı']), 1)
    yaz('alici/index.html', 'Alıcı: genel bakış', kart_giris('alici', bolumler['alici kartı']), 1)
    yaz('hesap.html', 'Hesap makineleri', hesap_sayfasi(), 0)
    yaz('sozluk.html', 'Sözlük', sozluk(), 0)
    yaz('kaynak.html', 'Kaynaklar ve güven düzeyi', kaynak(), 0)


def giris(bolumler):
    return ('<h1>Elektronik tasarımı sıfırdan, kendi elinle yapabilmek için</h1>'
            '<p>Bu site, iki gerçek kartın (uzaktan kumanda ve alıcı) tasarımını <b>baştan sona, hesabıyla, nedeniyle ve uç durumlarıyla</b> öğretmek için yazıldı. '
            'Amaç tasarımı sana tanıtmak değil; her bölümü okuduktan sonra aynı parçayı <b>kendi başına, boş sayfadan</b> tasarlayabilmen.</p>'
            + kutu('not', 'Her sayfa şunları içerir: işlenen ilke · gerçek şema (makine tarafından bağlantı listesiyle doğrulanmış) · adım adım tasarım · her sayı için hesap makinesi · her parçanın kartı '
                   '(ne işe yarar, neyden yapılmış, uç durumları, kime bağlı) · kartta yeri (zoom yapılabilir) · alıştırmalar.', 'Sayfaların yapısı')
            + '<h2>Güven düzeyi etiketleri</h2><p>Bir bilginin nereden geldiği her yerde işaretlidir:</p><ul>'
            '<li>[[ds]] — üreticinin veri sayfasında bu çalışmada okundu.</li><li>[[bilgi]] — genel mühendislik bilgisi; bu çalışmada bir belgeden doğrulanmadı.</li>'
            '<li>[[tahmin]] — hesap ya da varsayım.</li><li>[[dogrulanmadi]] — sipariş ya da ölçüm öncesi kontrol edilmesi gereken.</li></ul>'
            '<h2>Yol haritası</h2><ol><li><a href="temel/index.html">Temel bilgiler</a> (dokuz kısa ders): Ohm yasasından üretim dosyalarına; kartlara geçmeden önce okumanı öneririm.</li><li><a href="verici/index.html">Verici kartı</a> (daha basit): besleme, USB, işlemci, düğmeler, telsiz.</li>'
            '<li><a href="alici/index.html">Alıcı kartı</a> (daha zengin): 12 V giriş koruması, iki çevirici, Ethernet, 4G modem, röle.</li>'
            '<li>Her kartın <b>tam tasarım gezgini</b> (<a href="verici/tam.html">verici</a>, <a href="alici/tam.html">alıcı</a>): bütün şema, kartın iki yüzü, parça ve ağ dizini; öğrendiklerini bütün üstünde dene.</li>'
            '<li><a href="hesap.html">Hesap makineleri</a>: bölücü, geri besleme, bobin, hat empedansı, iz genişliği, pil ömrü…</li><li><a href="kaynak.html">Kaynaklar ve güven düzeyi</a>: hangi belge okundu, hangisi okunmadı.</li></ol>')


def kart_giris(ad, liste):
    if ad == 'verici':
        t = ('<h1>Verici kartı: genel bakış</h1><p>İki AAA pille ya da USB-C ile çalışan, altı düğmeli uzaktan kumanda kartı. Düğmeye basılınca uyanır, LoRa telsiziyle alıcıya mesaj yollar ve yeniden uyur.</p>')
    else:
        t = ('<h1>Alıcı kartı: genel bakış</h1><p>12 V ile çalışan; telsiz mesajını alıp interneti Ethernet ya da 4G ile kullanan ve bir röleyle lamba süren kart.</p>')
    t += kutu('ipucu', '<a href="tam.html"><b>Tam tasarım gezgini</b></a>: bütün şema, kartın iki yüzü, bütün parçalar ve ağlar tek sayfada; arama, tıklayarak izleme, denetim sayıları ve açık sorular.', 'Tasarımın tamamı')
    t += '<h2>Bölümler</h2><ol>' + ''.join('<li><a href="%s.html">%s</a> — %s</li>' % (m.ID, html.escape(m.BASLIK), html.escape(m.OZET)) for m in liste) + '</ol>'
    if not liste:
        t += '<p class="kaynak">Bu kartın bölümleri hazırlanıyor.</p>'
    return t


def hesap_sayfasi():
    ad = ['bolucu', 'geribesleme', 'led', 'rc', 'bobin', 'yukselten', 'ohm', 'pil', 'mikroserit', 'iz', 'dalga', 'izdirenc', 'kondgerilim', 'baglanti']
    return '<h1>Hesap makineleri</h1><p>Her biri tarayıcıda çalışır. Varsayılan değerler kartlardaki değerlerdir; kendi değerini yaz.</p>' + ''.join(hesap(a) for a in ad)


def sozluk():
    from uret import KISALTMA
    ref = [('R', 'Direnç (Resistor)'), ('C', 'Kondansatör (Capacitor)'), ('L', 'Bobin (Inductor; “L” harfi endüktans sembolünden)'), ('D', 'Diyot (Diode)'), ('Q', 'Transistör (Q: sembolde kullanılan harf)'),
           ('U', 'Tümleşik devre, çip (Unit)'), ('J', 'Konnektör / jak (Jack)'), ('K', 'Röle (Kontak: “K” harfi)'), ('F', 'Sigorta (Fuse)'), ('Y', 'Kristal (osilatör)'),
           ('SW', 'Düğme ya da anahtar (Switch)'), ('BT', 'Pil (Battery)'), ('TP', 'Test noktası (Test Point)'), ('H', 'Montaj deliği (Hole)')]
    return ('<h1>Sözlük</h1><p>Sitede geçen yabancı kökenli ve kısaltılmış her terimin Türkçe açıklaması. Bir terim her sayfada ilk geçtiği yerde üzerine gelince de açıklanır.</p>'
            '<h2>Parça kodları (şemada R1, C7, U3 gibi görülen harfler)</h2><table><tr><th>Harf</th><th>Anlamı</th></tr>' + ''.join('<tr><td><b>%s</b></td><td>%s</td></tr>' % (a, html.escape(b)) for a, b in ref) + '</table><p>Harfi izleyen sayı yalnızca sıra numarasıdır: R1, R2… kartta o türden kaçıncı parça olduğunu söyler.</p>'
            '<h2>Kısaltmalar ve yabancı terimler</h2><table><tr><th>Terim</th><th>Açılımı ve anlamı</th></tr>' + ''.join('<tr><td><b>%s</b></td><td>%s</td></tr>' % (k, html.escape(v)) for k, v in sorted(KISALTMA.items(), key=lambda x: x[0].lower())) + '</table>')


def kaynak():
    satir = [
        ('TI TPS63031 (SLVS696D) — verici çevirici', 'Baştan sona okundu'),
        ('TI TPS62933 (SLUSEA4D) — alıcı çeviriciler', 'Özellikler, ayak tablosu, mutlak azami değerler, tavsiye edilen koşullar, elektriksel özellikler tablosu okundu; uygulama ve yerleşim bölümleri okunmadı'),
        ('Espressif ESP32-S3-WROOM-1 v1.8', 'Ayak tablosu ve strapping bölümleri okundu; geri kalanı okunmadı'),
        ('Ai-Thinker Ra-01H Specification V1', 'Baştan sona okundu (ayak tablosu, ana parametreler, elektriksel özellikler); ölçü çizimi yok — ayak izi Ra-01/Ra-02 kılavuzundan'),
        ('SIMCom A7670 Series Hardware Design V1.00', 'Baştan sona okundu: bantlar, ayak tablosu, besleme, açma/kapama, UART, USB, SIM, anten, elektriksel sınırlar; akım tablosunun çoğu belgede “TBD”'),
        ('SIMCom A7670SA ürün özeti (LCSC’deki belge)', 'Okundu; LASC/LASE/FASE/MASC son eklerinin anlamı yazılı değil'),
        ('TI LM66100 (SLVSEZ8A)', 'Pinler, açık direnç ve CE bağlantısı okundu'),
        ('WIZnet W5500 v1.1.0', 'SPI davranışı ve referans devre için kullanıldı'),
        ('Hanrun HR911105A (RJ45) kısa belge', 'Okundu (iki sayfa)'),
        ('AO3401A, SMBJ15A, 1812L200, AP2112K, SRD-12VDC, SS14, USBLC6-2SC6, bobinlerin doyma akımı (SRP7028A tablosu kısmen okundu)', 'Veri sayfaları okunmadı; bu parçalar için yazılan değerler genel bilgidir [[bilgi]] ve sipariş öncesi kontrol edilmelidir [[dogrulanmadi]]'),
        ('Mikroşerit hat hesabı (Hammerstad), IPC-2221 iz akımı, FSPL', 'Standart formüller; yazılımla çalışır, üretici katman dizilimi bilinmediği için [[tahmin]]'),
    ]
    return ('<h1>Kaynaklar ve güven düzeyi</h1><p>Bu sayfa “ne okundu, ne okunmadı”yı açık söyler. Okunmayan bir belgeden çıkan sayı sitede yalnızca [[bilgi]] ya da [[dogrulanmadi]] etiketiyle yer alır.</p>'
            '<table><tr><th>Belge</th><th>Bu çalışmada</th></tr>' + ''.join('<tr><td>%s</td><td>%s</td></tr>' % (a, b) for a, b in satir) + '</table>')
