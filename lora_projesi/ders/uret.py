#!/usr/bin/env python3
"""Ders sitesini uretir: python3 uret.py  ->  ders/site/ . Yalniz standart kutuphane kullanir (GitHub Actions'ta calisir)."""
import os, sys, json, re, shutil, importlib, html
from types import SimpleNamespace
K = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, K)
import cizim, pano, deger
from icerik import parca_bilgi

CIKTI = os.path.join(K, 'site')
YAYIN_TARIHI = os.environ.get('YAYIN_ZAMANI', '')

ROZET = {'ds': ('ds', 'Veri sayfasından okundu'), 'bilgi': ('bilgi', 'Genel mühendislik bilgisi'), 'tahmin': ('tahmin', 'Hesap / varsayım'),
         'dogrulanmadi': ('dogrulanmadi', 'Doğrulanmadı')}

KISALTMA = {
    'MOSFET': 'Alan etkili transistör (Metal Oxide Semiconductor Field Effect Transistor)',
    'LDO': 'Düşük gerilim farkıyla çalışan doğrusal gerilim düzenleyici (Low Dropout)',
    'ESD': 'Statik elektrik boşalması (Electrostatic Discharge)',
    'TVS': 'Geçici gerilim bastırıcı diyot (Transient Voltage Suppressor)',
    'SPI': 'Seri çevresel arayüz (Serial Peripheral Interface)',
    'UART': 'Evrensel eşzamansız seri haberleşme (Universal Asynchronous Receiver Transmitter)',
    'USB': 'Evrensel seri veri yolu (Universal Serial Bus)',
    'ESR': 'Eşdeğer seri direnç (Equivalent Series Resistance)',
    'PWM': 'Darbe genişlik kiplemesi (Pulse Width Modulation)',
    'UVLO': 'Düşük gerilim kilidi (Undervoltage Lockout)',
    'DCR': 'Doğru akım direnci (DC Resistance)',
    'PCB': 'Baskı devre kartı (Printed Circuit Board)',
    'LoRa': 'Uzun menzilli, düşük hızlı telsiz tekniği (Long Range)',
    'GND': 'Toprak / sıfır volt referansı (Ground)',
    'EMI': 'Elektromanyetik girişim (Electromagnetic Interference)',
    'MLCC': 'Çok katmanlı seramik kondansatör (Multilayer Ceramic Capacitor)',
    'BOM': 'Malzeme listesi (Bill of Materials)',
    'PTC': 'Pozitif sıcaklık katsayılı direnç (Positive Temperature Coefficient)',
    'RF': 'Telsiz frekansı (Radio Frequency)',
    'FSPL': 'Serbest uzay yol kaybı (Free Space Path Loss)',
    'DRC': 'Tasarım kuralı denetimi (Design Rule Check)',
    'ERC': 'Elektriksel kural denetimi (Electrical Rule Check)',
    'IPC': 'Elektronik üretim standartları kuruluşu (Institute for Printed Circuits); IPC-2221 iz genişliği formülünü verir',
    'SMD': 'Yüzey montaj parça (Surface Mount Device)',
    'HASL': 'Sıcak hava ile kalay kaplama (Hot Air Solder Leveling)',
    'ENIG': 'Nikel–altın kaplama (Electroless Nickel Immersion Gold)',
    'LTE': 'Dördüncü nesil cep telefonu şebekesi (Long Term Evolution)',
    'SIM': 'Abone kimlik kartı (Subscriber Identity Module)',
    'PFM': 'Darbe frekansı kiplemesi (Pulse Frequency Modulation): hafif yükte anahtarlama sıklığını azaltır',
    'PHY': 'Ethernet fiziksel katmanı (Physical Layer)',
    'TCP': 'İletim denetim protokolü (Transmission Control Protocol)',
    'DC': 'Doğru akım / sabit gerilim (Direct Current); zamanla değişmeyen. “DC bias”: kondansatöre uygulanan sabit gerilim',
    'AC': 'Alternatif akım (Alternating Current); yönü ve değeri zamanla değişen',
    'X5R': 'Sınıf 2 seramik kondansatör türü: −55…+85 °C, kapasite sıcaklıkla en çok ±%15 sapar',
    'X7R': 'Sınıf 2 seramik kondansatör türü: −55…+125 °C, kapasite sıcaklıkla en çok ±%15 sapar',
    'C0G': 'Sınıf 1 seramik: kapasite sıcaklık ve gerilimle neredeyse değişmez; küçük değerli (pF–nF); NP0 ile aynı şey',
    'NP0': '“Negatif-Pozitif Sıfır”: C0G’nin eski adı; sıcaklıkla kapasite kayması sıfıra yakın',
    'Y5V': 'Kötü kalite seramik türü: sıcaklık ve gerilimle kapasite çok değişir; tercih edilmez',
    'E24': 'Direnç değer dizisi (her ondalıkta 24 değer): %5 toleranslı dirençler',
    'E96': 'Direnç değer dizisi (her ondalıkta 96 değer): %1 toleranslı dirençler',
    'RJ45': 'Ethernet kablosunun 8 uçlu standart fişi / soketi',
    'LED': 'Işık yayan diyot (Light Emitting Diode)',
    'SMA': 'Telsiz anteni için vidalı koaksiyel konnektör (SubMiniature version A)',
    'NPN': 'Bipolar transistör türü: taban akımı toplayıcıdan emetöre akımı denetler (“N-P-N” yarı iletken dizilişi)',
    'JTAG': 'Çip içini gözlemleme ve hata ayıklama arayüzü (Joint Test Action Group)',
    'RTC': 'Gerçek zaman saati (Real Time Clock); derin uykuda çalışan düşük güçlü bölüm',
    'GPIO': 'Genel amaçlı giriş/çıkış ayağı (General Purpose Input/Output)',
    'MISO': 'SPI’da uydu çipten efendiye veri hattı (Master In Slave Out)',
    'MOSI': 'SPI’da efendiden uydu çipe veri hattı (Master Out Slave In)',
    'SCK': 'SPI saat hattı (Serial Clock)',
    'NSS': 'SPI uydu seçme hattı (Not Slave Select): düşük düzeyde çip seçilir; CS ile aynı',
    'CS': 'Çip seçme (Chip Select)',
    'SS': 'Çeviricilerde yumuşak başlatma (Soft Start); SPI’da ise uydu seçme',
    'EN': 'Etkinleştir ucu (Enable); yüksek düzeyde çip çalışır',
    'VIN': 'Giriş gerilimi ucu (Voltage Input)',
    'VBUS': 'USB kablosunun 5 V besleme teli',
    'VBAT': 'Pil gerilimi hattı (Voltage Battery)',
    'VDD': 'Sayısal devrenin pozitif besleme gerilimi',
    'AVDD': 'Analog bölümün besleme gerilimi',
    'AGND': 'Analog toprak (Analog Ground)',
    'PGND': 'Güç toprağı (Power Ground): çeviricinin yüksek akımlı toprak dönüşü',
    'CC': 'USB-C’de yapılandırma kanalı (Configuration Channel): 5,1 kΩ dirençle cihaz olduğunu bildirir',
    'SW': 'Çeviricide anahtarlama ucu (Switch node); ayrıca düğme/anahtar parça kodu',
    'FB': 'Geri besleme ucu (Feedback); çıkış gerilimi bölücüyle buraya getirilir',
    'BST': 'Bootstrap: üst anahtarın kapısını sürmek için gerilim yükselten kondansatör ucu',
    'RESET': 'Sıfırlama: çipi başlangıç durumuna döndürür',
    'PWRKEY': 'Modemin açma/kapama tuşu ucu (Power Key)',
    'RMS': 'Etkin (efektif) değer (Root Mean Square): ısıtma etkisi bakımından eşdeğer sabit akım',
    'SOT': 'Küçük çerçeveli transistör kılıfı (Small Outline Transistor)',
    'SOD': 'Küçük çerçeveli diyot kılıfı (Small Outline Diode)',
    'LQFP': 'İnce, dört kenarından bacaklı yüzey montaj kılıfı (Low-profile Quad Flat Package)',
    'TSSOP': 'İnce küçültülmüş çerçeveli çok bacaklı kılıf (Thin Shrink Small Outline Package)',
    'LCC': 'Bacaksız, kenarında lehim pedleri olan modül kılıfı (Leadless Chip Carrier)',
    'WSON': 'Çok ince, bacaksız küçük kılıf (Very-very thin Small Outline No-lead)',
    'PSRAM': 'Yalancı statik bellek (Pseudo-Static RAM): ek çalışma belleği',
    'ROM': 'Yalnız okunur bellek (Read-Only Memory)',
    'PLL': 'Faz kilitli döngü (Phase-Locked Loop): bir frekanstan başka frekans üretir',
    'MDIX': 'Ethernet’te gönderme/alma çiftlerini otomatik değiştirme (Medium Dependent Interface Crossover)',
    'TX': 'Gönderme (Transmit)',
    'RX': 'Alma (Receive)',
    'TXD': 'Seri hat gönderme teli (Transmit Data)',
    'RXD': 'Seri hat alma teli (Receive Data)',
    'UDP': 'Bağlantısız veri paketi protokolü (User Datagram Protocol)',
    'MAC': 'Ethernet’te ortam erişim denetimi (Media Access Control); ayrıca cihaz donanım adresi',
    'GSM': 'Eski nesil cep telefonu şebekesi (Global System for Mobile Communications)',
    'DNP': 'Takılmayacak parça (Do Not Populate)',
    'SMT': 'Yüzey montaj teknolojisi (Surface Mount Technology)',
    'DFM': 'Üretilebilirlik denetimi (Design For Manufacturing)',
    'HBM': 'Elektrostatik boşalma deney modeli: insan vücudu (Human Body Model)',
    'AAA': 'İnce çubuk pil boyu (“üçlü A”)',
    'IO': 'Giriş/çıkış (Input/Output); “IO8” = işlemcinin 8 numaralı giriş/çıkış ayağı',
    'DIO': 'LoRa modülünün sayısal giriş/çıkış ayağı (Digital Input/Output); kesme için kullanılır',
    'SF': 'LoRa’da yayılma çarpanı (Spreading Factor); yüksek = uzun menzil, düşük hız',
    'VSWR': 'Gerilim duran dalga oranı: anten uyumsuzluğunun ölçüsü; 1,0 mükemmel',
    'EVM': 'Üreticinin deney kartı (Evaluation Module)',
    'FL': 'u.FL: çok küçük, dar telsiz koaksiyel konnektörü',
    'TI': 'Texas Instruments: çip üreticisi',
    'MHz': 'Megahertz: saniyede bir milyon salınım',
    'GHz': 'Gigahertz: saniyede bir milyar salınım',
    'KB': 'Kilobayt (bin bayt)',
    'MB': 'Megabayt (bir milyon bayt)',
    'JSON': 'Veriyi metin olarak yazma biçimi (JavaScript Object Notation)',
    'SYNC': 'Eşzamanlama (Synchronization)',
    'OE': 'Çıkış etkinleştirme (Output Enable)',
    'RC': 'Direnç + kondansatör devresi; zaman sabiti τ = R·C',
    'RT': 'TPS62933’te anahtarlama frekansını ayarlayan uç',
    'CLK': 'Saat işareti (Clock)',
    'CE': 'Çip etkinleştirme (Chip Enable)',
    'INT': 'Kesme (Interrupt): çipin işlemciye “bana bak” demesi',
    'PMODE': 'W5500’de çalışma kipini seçen uçlar',
    'UART0': 'İşlemcinin 0 numaralı seri hat denetleyicisi',
    'SBU': 'USB-C’de yan bant kullanım ucu (Sideband Use); bu kartta kullanılmaz',
    'IP': 'İnternet protokolü (Internet Protocol)',
    'FR': 'FR-4: cam elyaf takviyeli epoksi, standart kart malzemesi (Flame Retardant)',
    'PEDOT': 'İletken polimer malzeme; polimer kondansatörde elektrolit yerine kullanılır',
    'SA': 'A7670SA adındaki “SA” son eki; SIMCom belgelerinde açılımı yazılı değil (bant listesi belgeden okundu)',
    'ANT': 'Anten ucu (Antenna)',
    'TD': 'Ethernet’te gönderme çifti (Transmit Data)',
    'RD': 'Ethernet’te alma çifti (Receive Data)',
    'IC': 'Tümleşik devre (Integrated Circuit): çip',
    'A7670': 'SIMCom’un 4G (LTE Cat 1) modem modül ailesi',
}


def rozetle(t):
    def f(m):
        k, ad = ROZET[m.group(1)]
        return '<span class="rozet %s" title="%s">%s</span>' % (k, ad, ad.split(' ')[0] if k != 'ds' else 'Veri sayfası')
    return re.sub(r'\[\[(ds|bilgi|tahmin|dogrulanmadi)\]\]', f, t)


def kisalt(sayfa_html):
    """Her kisaltmayi sayfada ilk gectigi yerde <abbr> ile aciklar (etiketlerin icine dokunmaz)."""
    goruldu = set()
    parcalar = re.split(r'(<[^>]+>)', sayfa_html)
    icerde = 0
    for i, p in enumerate(parcalar):
        if p.startswith('<'):
            if re.match(r'<(script|style|svg|code|abbr|a |a>|title|h1|h2|h3)', p):
                icerde += 1
            elif re.match(r'</(script|style|svg|code|abbr|a|title|h1|h2|h3)>', p):
                icerde = max(0, icerde - 1)
            continue
        if icerde:
            continue
        for k, a in KISALTMA.items():
            if k in goruldu:
                continue
            m = re.search(r'(?<![A-Za-z0-9_])' + re.escape(k) + r'(?![A-Za-z0-9_])', p)
            if m:
                p = p[:m.start()] + '<abbr title="%s">%s</abbr>' % (html.escape(a), k) + p[m.end():]
                goruldu.add(k)
        parcalar[i] = p
    return ''.join(parcalar)


class Veri:
    def __init__(self, ad):
        self.ad = ad
        self.d = json.load(open(os.path.join(K, 'veri', ad + '.json')))
        self.parca = {r: SimpleNamespace(**p) for r, p in self.d['parcalar'].items()}
        self.aglar = {}
        for ag, l in self.d['aglar'].items():
            self.aglar[ag] = {(a, str(b)) for a, b in l}

    def deg(self, ref):
        return deger.sayi(self.parca[ref].deger)

    def ag_pinleri(self, ag):
        return sorted(self.aglar.get(ag, []))

    def kart_html(self, ref):
        p = self.d['parcalar'][ref]
        sinif = parca_bilgi.sinif_bul(ref, p)
        b = parca_bilgi.SINIFLAR.get(sinif) if sinif else None
        konum = self.d['konum'].get(ref)
        h = ['<div class="pkart" id="kart-%s"><h4>%s — %s</h4>' % (ref, ref, html.escape(p['deger']))]
        h.append('<div class="alt">%s</div>' % html.escape(b['ad'] if b else p['sembol']))
        if p['mpn']:
            h.append('<div class="alt">Parça numarası: <code>%s</code></div>' % html.escape(p['mpn']))
        h.append('<div class="alt">Kılıf: <code>%s</code>%s</div>' % (html.escape((p['fp'] or '').split(':')[-1]), (
            ' · kartta kapladığı alan ≈ %s × %s mm' % (str(konum['g']).replace('.', ','), str(konum['y_']).replace('.', ',')) if konum else '')))
        if p['dnp']:
            h.append('<div class="uyari">Bu parça varsayılan olarak <b>takılmaz</b> (DNP). Yalnızca ihtiyaç doğarsa takılır.</div>')
        if b:
            h.append('<dl><dt>Ne işe yarar?</dt><dd>%s</dd><dt>Neyden yapılmıştır?</dt><dd>%s</dd>' % (b['ne'], b['yapi']))
            h.append('<dt>Önemli özellikleri</dt><dd><ul>%s</ul></dd>' % ''.join('<li>%s</li>' % x for x in b['ozellik']))
            h.append('<dt>Uç durumlar ve tuzaklar</dt><dd><ul>%s</ul></dd></dl>' % ''.join('<li>%s</li>' % x for x in b['uc']))
        else:
            h.append('<p class="kaynak">Bu parça için ayrıntılı kart henüz yazılmadı.</p>')
        # baglantilar
        satir = []
        for no, pin in sorted(p['pinler'].items(), key=lambda x: (len(x[0]), x[0])):
            if not pin['ag']:
                continue
            digerleri = sorted({r for (r, n) in self.aglar.get(pin['ag'], []) if r != ref})
            kisa = ', '.join(digerleri[:8]) + (' …(+%d)' % (len(digerleri) - 8) if len(digerleri) > 8 else '')
            satir.append('<tr><td>%s</td><td>%s</td><td><b>%s</b></td><td>%s</td></tr>' % (no, html.escape(pin['ad'] or ''), html.escape(pin['ag']), kisa))
        if satir:
            h.append('<details><summary>Ayakları ve kime bağlı olduğu (%d ayak)</summary><table><tr><th>No</th><th>Ayak adı</th><th>Ağ</th><th>Aynı ağdaki parçalar</th></tr>%s</table></details>' % (len(satir), ''.join(satir)))
        h.append('</div>')
        return rozetle(''.join(h))


def sayfa(baslik, govde, yol_derinlik, nav, simdi, aciklama='', genis=False):
    r = '../' * yol_derinlik
    yan = []
    for grup, ogeler in nav:
        yan.append('<h4>%s</h4>' % html.escape(grup))
        for (slug, ad) in ogeler:
            yan.append('<a href="%s%s"%s>%s</a>' % (r, slug, ' class="simdi"' if slug == simdi else '', html.escape(ad)))
    ust = ('<header class="ust"><b>LoRa Tasarım Dersi</b><nav><a href="%sindex.html">Giriş</a><a href="%stemel/index.html">Temel bilgiler</a>'
           '<a href="%sverici/index.html">Verici</a><a href="%salici/index.html">Alıcı</a><a href="%shesap.html">Hesap makineleri</a><a href="%ssozluk.html">Sözlük</a><a href="%skaynak.html">Kaynaklar</a></nav></header>') % ((r,) * 7)
    govde = kisalt(rozetle(govde))
    return ('<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>%s — LoRa Tasarım Dersi</title><meta name="description" content="%s"><link rel="stylesheet" href="%svarlik/stil.css"></head><body%s>%s'
            '<div class="kap"><aside class="yan">%s</aside><main>%s</main></div>'
            '<footer>Bu sayfa her güncellemede otomatik üretilir. %s Tasarım verisi: <code>lora_projesi/ders/veri/*.json</code>. '
            'Sayılar tasarımın bağlantı listesinden ve yazılmış hesap kodundan çıkar; el ile yazılmış sayı yoktur, olanlar etiketlidir.</footer>'
            '<script src="%svarlik/uygulama.js"></script></body></html>') % (html.escape(baslik), html.escape(aciklama), r, ' class="genis"' if genis else '', ust, ''.join(yan), govde, YAYIN_TARIHI, r)


def main():
    if os.path.exists(CIKTI):
        shutil.rmtree(CIKTI)
    os.makedirs(os.path.join(CIKTI, 'varlik'))
    for f in os.listdir(os.path.join(K, 'varlik')):
        shutil.copy(os.path.join(K, 'varlik', f), os.path.join(CIKTI, 'varlik', f))
    ver = {ad: Veri(ad) for ad in ('verici', 'alici')}
    import icerik.kayit as kayit
    kayit.uret(CIKTI, ver, sayfa, os.path.join(K, 'icerik'))
    print('site hazir:', CIKTI)


if __name__ == '__main__':
    main()
