from icerik.yardim import *

SAYFALAR = []


def sayfa(id_, baslik, ozet):
    def d(f):
        SAYFALAR.append((id_, baslik, ozet, f))
        return f
    return d


@sayfa('ohm', '1. Gerilim, akım, direnç ve güç', 'Her devrenin dayandığı dört nicelik ve iki denklem; bölücü, LED direnci ve ısınma.')
def _ohm():
    return (
        '<h1>1. Gerilim, akım, direnç ve güç</h1><p class="ozet">Elektronikte hesap edeceğin hemen her şey bu dört niceliğe iner.</p>'
        '<h2>Su borusu benzetmesi</h2><p><b>Gerilim</b> (volt, V) borudaki basınç farkıdır; <b>akım</b> (amper, A) birim zamanda geçen su miktarıdır; <b>direnç</b> (ohm, Ω) borunun darlığıdır. Basınç farkı olmadan akım olmaz; boru daraldıkça aynı basınçta daha az su geçer. [[bilgi]]</p>'
        + formul('Ohm yasası: V = I × R &nbsp;&nbsp;|&nbsp;&nbsp; Güç: P = V × I = I² × R = V² / R')
        + '<h2>Üç kullanım</h2><ol>'
        '<li><b>Akım sınırlama (LED).</b> 3,3 V ile beslenen, 2 V’ta yanan bir LED’i 5 mA ile sürmek için direnç = (3,3 − 2) / 0,005 = 260 Ω; en yakın standart değer 270 Ω.</li>'
        '<li><b>Gerilim bölücü.</b> İki dirençle gerilimin bir kısmı alınır: V<sub>çıkış</sub> = V<sub>giriş</sub> × R2 / (R1 + R2). Bu kartlarda çeviricilerin çıkış gerilimini ayarlayan geri besleme bölücüleri budur. Çıkış bir yük çekerse bölücü bozulur: bölücü akımı yükün akımından en az 10 kat büyük olmalıdır. [[bilgi]]</li>'
        '<li><b>Yukarı/aşağı çekme.</b> Boşta kalan bir giriş ayağı “havada” kalır, rastgele okunur. 10 kΩ ile 3,3 V’a (yukarı çekme) ya da toprağa (aşağı çekme) bağlayınca ayak bilinen bir düzeye gelir. Değer büyükse akım azdır ama gürültüye daha açıktır.</li></ol>'
        '<h2>Isınma: güç nereye gider?</h2><p>Dirençte harcanan güç ısıya dönüşür. 0603 boyutlu bir direncin anma gücü genellikle 0,1 W’tır [[bilgi]] (veri sayfasından doğrulanmalı). 100 Ω’dan 30 mA geçerse P = 0,03² × 100 = 0,09 W: sınırda. Bu yüzden akım yoluna konan dirençlerin gücü <i>her zaman</i> hesaplanır.</p>'
        + hesap('ohm') + hesap('bolucu') + hesap('led')
        + alistirma('12 V’tan 5 mA ile 2,1 V’ta yanan bir LED’i yakmak için direnç ve harcanan güç nedir?', 'R = (12 − 2,1)/0,005 = 1980 Ω → 2 kΩ. Dirençte P = 0,005² × 2000 = 0,05 W. LED 10,5 mW harcar; toplam 60 mW. Çoğu enerji dirençte ısıya gider: bu yüzden büyük gerilimde LED için doğrusal direnç verimsizdir.'))


@sayfa('kondansator', '2. Kondansatör', 'Yük deposu: süzgeç, kapatma, zamanlama. Seramik kondansatörün gerilimle kapasite kaybı.')
def _kond():
    return (
        '<h1>2. Kondansatör</h1><p class="ozet">İki iletken levha arasında yalıtkan: elektrik yükü biriktirir.</p>'
        + formul('Q = C × V &nbsp;&nbsp;|&nbsp;&nbsp; I = C × dV/dt &nbsp;&nbsp;|&nbsp;&nbsp; RC zaman sabiti τ = R × C')
        + '<h2>Ne işe yarar?</h2><ul>'
        '<li><b>Kapatma (decoupling).</b> Bir çip birden akım çekince besleme hattı çöker. Çipin yanındaki kondansatör bu darbeyi yerinden verir. Bu yüzden 100 nF, çipin besleme ayağına <i>en yakın</i> yere konur: iz uzadıkça kablonun bobin etkisi (endüktans) kondansatörü işe yaramaz hale getirir.</li>'
        '<li><b>Süzgeç.</b> Çıkışta dalgalanmayı (ripple) düzleştirir.</li>'
        '<li><b>Zamanlama.</b> RC ile sıfırlama gecikmesi: 10 kΩ × 1 µF = 10 ms. Bu kartlarda işlemcinin EN ayağı bununla gecikir, besleme oturduktan sonra çip başlar.</li></ul>'
        '<h2>Malzeme: seramik, tantal, polimer, elektrolitik</h2>'
        '<table><tr><th>Tür</th><th>Güçlü yanı</th><th>Zayıf yanı</th></tr>'
        '<tr><td>Seramik (MLCC)</td><td>Küçük, çok düşük iç direnç (ESR), yüksek frekansta iyi</td><td>Uygulanan gerilimle kapasitesi düşer (DC bias); ısı ve yaşlanma; titreşimde “ötebilir”</td></tr>'
        '<tr><td>Polimer</td><td>Büyük kapasite, düşük ESR</td><td>Hacimli, pahalı, gerilim sınırı</td></tr>'
        '<tr><td>Tantal</td><td>Küçük hacimde büyük kapasite</td><td>Aşırı gerilimde/ters bağlanınca yanabilir</td></tr>'
        '<tr><td>Elektrolitik</td><td>Çok ucuz, büyük kapasite</td><td>Yüksek ESR, ömür sınırlı, kutuplu</td></tr></table><p>[[bilgi]]</p>'
        '<h2>Uç durum: gerilim altında kapasite kaybı</h2><p>X5R/X7R seramikte anma gerilimine yakın kullanınca etkin kapasite yarıdan aza düşebilir [[bilgi]]; kesin oran parçanın veri sayfasındaki eğriden okunur. 12 V hattında 25 V yerine 16 V’luk kondansatör seçmek sessizce kapasiteyi yarılar. Alıcı kartındaki bölümlerde bu hesap tek tek yapılır.</p>'
        + hesap('rc') + hesap('kondgerilim')
        + alistirma('3,3 V hattına 22 µF seramik koyuyorsun, 6,3 V anma gerilimli. Neden 10 V’luk seçmek daha güvenli?', 'Gerilim anma değerine yakınsa kapasite belirgin düşer ve parça daha çok zorlanır. 10 V’luk parça aynı 3,3 V’ta eğrinin daha yatay yerinde çalışır: etkin kapasite daha yüksektir.'))


@sayfa('bobin', '3. Bobin ve anahtarlamalı çeviriciler', 'Enerjiyi manyetik alanda saklayan parça; buck ve buck-boost çeviricinin çalışması.')
def _bobin():
    return (
        '<h1>3. Bobin ve anahtarlamalı çeviriciler</h1><p class="ozet">Gerilimi kayıpsıza yakın düşürüp yükselten devrelerin kalbi.</p>'
        + formul('V = L × dI/dt &nbsp;&nbsp;|&nbsp;&nbsp; depolanan enerji E = ½ × L × I²')
        + '<p>Bobin akımdaki değişime direnir: akımı aniden değiştirmek isterseniz büyük bir gerilim doğar. Bu özellik hem çeviricide işe yarar hem de rölenin bobininde tehlikelidir (ters gerilim tepesi → flyback diyodu).</p>'
        '<h2>Neden “anahtarlamalı”?</h2><p>12 V’tan 3,3 V’a doğrusal düzenleyici (LDO) ile inmek farkı (8,7 V) ısıya çevirir: 0,5 A’de 4,35 W. Anahtarlamalı çevirici bir transistörü hızla açıp kapatır; bobin enerjiyi alıp verir; ısıya giden pay %5–15’e iner. [[bilgi]]</p>'
        '<h2>Buck (düşüren)</h2><ol><li>Anahtar kapalıyken bobin akımı artar, enerji depolar.</li><li>Anahtar açılınca bobin akımı sürdürür; akım diyot (ya da alt anahtar) üstünden akar.</li><li>Ortalama çıkış gerilimi ≈ V<sub>giriş</sub> × D (D: görev oranı, anahtarın kapalı kaldığı oran).</li></ol>'
        + formul('Bobin dalgalanma akımı: ΔI = (V<sub>giriş</sub> − V<sub>çıkış</sub>) × D / (L × f<sub>anahtarlama</sub>)')
        + '<h2>Bobin seçimi: üç sayı</h2><ul><li><b>Endüktans (µH):</b> ΔI’yı çıkış akımının yaklaşık %20–40’ı yapacak kadar.</li><li><b>Doyma akımı (I<sub>sat</sub>):</b> bobin bu akımda çekirdeği doyar, endüktans çöker, akım kontrolsüz artar. Tepe akım (I<sub>çıkış</sub> + ΔI/2) bunun altında kalmalı.</li><li><b>Isınma akımı (I<sub>rms</sub>):</b> bakır direncinden ısınma sınırı.</li></ul><p>Bobin malzemesi: ferrit çekirdek (yüksek frekans, ucuz), toz demir (yumuşak doyma), koruyuculu (shielded) tür az gürültü yayar. [[bilgi]]</p>'
        + hesap('bobin') + hesap('geribesleme') + hesap('yukselten')
        + '<p>Çeviricinin çıkış gerilimi çoğunlukla bir geri besleme bölücüsüyle ayarlanır: çıkış, iki dirençle bölünüp çipin referans gerilimiyle karşılaştırılır. Alıcı kartındaki 3,3 V ve 3,8 V çıkışları bu yolla seçilmiştir.</p>'
        + alistirma('12 V’tan 3,3 V’a, 0,5 A çekilirken LDO ve buck verimini karşılaştır (buck %90 verimli varsay).', 'LDO: ısı = (12−3,3) × 0,5 = 4,35 W; verim ≈ 3,3/12 = %27,5. Buck: çıkış 1,65 W, giriş ≈ 1,83 W, ısı ≈ 0,18 W. [[tahmin]]'))


@sayfa('yariiletken', '4. Diyot ve transistör', 'Tek yönlü akım, anahtar olarak transistör, röle sürücüsü ve ters bağlanma koruması.')
def _yi():
    return (
        '<h1>4. Diyot ve transistör</h1><p class="ozet">Akımın yönünü ve açılıp kapanmasını denetleyen yarı iletkenler.</p>'
        '<h2>Diyot</h2><p>Akımı bir yönde geçirir (anottan katoda). İleri yönde ≈ 0,3 V (Schottky) – 0,7 V (silisyum) düşürür. Üç kullanım: ters bağlanma koruması, “veya” kapısı (iki beslemeyi birleştirme), sönüm (flyback). Zener diyot ters yönde belli bir gerilimde iletime geçer: gerilim sınırlar. TVS diyot ani aşırı gerilimi (darbe) toprağa akıtır. [[bilgi]]</p>'
        '<h2>Transistör</h2><p><b>NPN (bipolar):</b> taban–emetör arasından küçük akım (≈ 0,7 V’ta) toplayıcı–emetör arasında büyük akımı denetler. Anahtar olarak kullanırken doyuma sokulur: taban akımı, yük akımı / en düşük akım kazancı’nın birkaç katı. Röle bobini 30 mA çekiyorsa ve kazanç ≥ 50 ise taban akımı ≥ 0,6 mA; kartta 2,6 mA verilir (güvenli doyum).</p><p><b>MOSFET:</b> kapı (gate) gerilimi akımı denetler, kapıdan akım akmaz. P-kanallı MOSFET alıcıdaki ters bağlanma korumasında diyottan çok daha az gerilim düşürür (≈ 50 mV, diyotta 0,3–0,7 V).</p>'
        + formul('Doyma: I<sub>taban</sub> ≥ (I<sub>yük</sub> / β<sub>min</sub>) × 2…5 &nbsp;&nbsp;|&nbsp;&nbsp; MOSFET ısınması: P = I² × R<sub>DS(on)</sub>')
        + '<h2>Flyback diyodu</h2><p>Röle bobini akım taşırken transistör kapanırsa bobin akımı sürdürmek ister; diyot olmazsa transistörün toplayıcısında yüzlerce voltluk tepe doğar ve transistör ölür. Diyot bu akıma yol verir. Alıcıdaki benzetim tepeyi ≈ 12,2 V gösterir (12 V + diyot düşümü). [[ds]]</p>'
        + hesap('ohm')
        + alistirma('Bobin 30 mA, β<sub>min</sub> = 100. Taban akımı en az nedir, tabana 3,3 V’tan 1 kΩ koyarsan ne olur?', '0,03/100 = 0,3 mA gerekir. 1 kΩ ile (3,3 − 0,7)/1000 = 2,6 mA verilir: ≈ 9 kat güvenli doyum. Çok fazla taban akımı da israftır; 10 kΩ aşağı çekme ise çip kapalıyken röleyi kapalı tutar.'))


@sayfa('haberlesme', '5. SPI, UART, USB ve diğer yollar', 'Çipler birbiriyle nasıl konuşur: sinyal hatları, hız, seviye uyumu.')
def _hab():
    return (
        '<h1>5. SPI, UART, USB ve diğer yollar</h1><p class="ozet">İşlemci ile çevre çipler arasındaki sayısal konuşma kuralları.</p>'
        '<table><tr><th>Yol</th><th>Hat sayısı</th><th>Kim konuşur?</th><th>Bu kartlarda</th></tr>'
        '<tr><td>SPI</td><td>SCK, MOSI, MISO + her çip için bir CS (seçim)</td><td>Bir efendi (işlemci), çok uydu</td><td>LoRa modülü, W5500</td></tr>'
        '<tr><td>UART</td><td>TX, RX (+ isteğe bağlı akış denetimi)</td><td>İki eşit uç, saat yok; hız önceden kararlaştırılır</td><td>4G modem</td></tr>'
        '<tr><td>USB</td><td>D+, D− (fark çifti), VBUS, GND</td><td>Bir ana (bilgisayar), uydu (kart)</td><td>Programlama</td></tr></table><p>[[bilgi]]</p>'
        '<h2>Seviye uyumu</h2><p>Bir çip 3,3 V mantıkla konuşurken karşısındaki 1,8 V ile konuşuyorsa doğrudan bağlamak karşıdaki çipi yakabilir ya da hiç okunmaz. Aralarına seviye çevirici konur: alıcı kartındaki modem 1,8 V’tur, TXB0104 ile çevrilir. Çift yönlü “otomatik” çeviriciler, hat yüksek dirençle çekilmişse bazen hatayı karıştırır; veri sayfasındaki yük sınırlarına bakılır. [[bilgi]]</p>'
        '<h2>Ortak hat kuralı</h2><p>SPI’da çok çip tek MISO’ya bağlıdır; seçilmeyen çipin çıkışı yüksek empedansa geçmelidir. Bir çip bu kurala uymazsa hat çakışır. W5500 veri sayfasında bu açıkça yazılıdır [[ds]]; her yeni çip için bu satır aranır.</p>'
        '<h2>Hızın bedeli</h2><p>Hız arttıkça kenarlar keskinleşir, iz uzunluğu anten gibi davranır, karşılıklı etkileşim (crosstalk) büyür. Kural: iz uzunluğunu sinyal yükselme süresinin 1/6’sından kısa tut ya da hattı empedansla tasarla. [[bilgi]]</p>'
        + alistirma('SPI saati 20 MHz, hat 60 mm. Sorun olur mu?', 'Saat 20 MHz’te dalga boyu havada 15 m; 60 mm çok küçüktür. Asıl etken kenar hızıdır (nanosaniye). Bu uzunlukta genelde sorun olmaz; ama dönüş yolunu (toprak düzlemini) kesmemek gerekir.'))


@sayfa('rf', '6. Yüksek frekans: anten hattı ve bağlantı bütçesi', '50 Ω’luk hat neden gerekir, mikroşerit hesabı, FSPL ve bağlantı bütçesi.')
def _rf():
    return (
        '<h1>6. Yüksek frekans: anten hattı ve bağlantı bütçesi</h1><p class="ozet">915 MHz’te bir iz artık bir iletim hattıdır.</p>'
        '<p>Frekans yükselince iz, yalnız bir tel değil, uzunluğu dalga boyuyla kıyaslanabilir bir <b>iletim hattı</b> olur. Hat, kaynak ve yükle aynı <b>karakteristik empedansta</b> (genelde 50 Ω) değilse sinyalin bir kısmı geri yansır ve gücün anteni ulaşamayan kısmı ısıya/yansımaya gider. [[bilgi]]</p>'
        '<h2>Mikroşerit hat</h2><p>Dış katmandaki iz ile altındaki sürekli toprak düzlemi 50 Ω’u şunlar belirler: iz genişliği, yalıtkan kalınlığı (prepreg), yalıtkanın dielektrik sabiti (FR-4 için ≈ 4,3–4,5). Dar iz → yüksek empedans. Bu kartta 0,4 mm iz, 0,21 mm prepreg’de ≈ 47,6 Ω hesaplanır [[tahmin]]; gerçek değer üreticinin katman dizilimine bağlıdır [[dogrulanmadi]].</p>'
        + hesap('mikroserit')
        + '<h2>Toprak yolu</h2><p>Dönüş akımı hattın hemen altında, toprak düzleminde akar. O düzlemi yarmak (sinyal izi geçirmek) hat empedansını bozar. Bu yüzden anten hattının altı kesintisiz bırakılır ve etrafına toprak delikleri (via fence) örülür.</p>'
        '<h2>Bağlantı bütçesi (link budget)</h2>'
        + formul('Alınan güç = Gönderilen güç + verici anten kazancı − serbest uzay kaybı + alıcı anten kazancı') + formul('Serbest uzay kaybı (FSPL, dB) = 20·log₁₀(d<sub>km</sub>) + 20·log₁₀(f<sub>MHz</sub>) + 32,44')
        + hesap('baglanti')
        + '<p>Gerçek hayatta engeller, yer yansıması, anten uyumsuzluğu bu bütçeye 10–30 dB ek kayıp getirebilir; bu yüzden payı geniş bırakılır. Menzil sahada ölçülmeden söz verilmez. [[bilgi]]</p>'
        + alistirma('915 MHz’te 2 km için FSPL kaç dB?', '20·log₁₀(2) + 20·log₁₀(915) + 32,44 = 6,02 + 59,23 + 32,44 ≈ 97,7 dB.'))


@sayfa('pcb', '7. Baskı devre kartı: katmanlar, iz genişliği, via, ısı', 'Kart neden 4 katman, iz akımı nasıl hesaplanır, delik ve boşluk kuralları.')
def _pcb():
    return (
        '<h1>7. Baskı devre kartı: katmanlar, iz genişliği, via, ısı</h1><p class="ozet">Şema “ne bağlı”yı söyler; kart “nerede ve nasıl bağlı”yı.</p>'
        '<h2>Katman dizilimi</h2><p>Bu projede dört katman: <b>F.Cu</b> (üst, parçalar + sinyal) · <b>In1</b> (toprak düzlemi) · <b>In2</b> (3,3 V düzlemi) · <b>B.Cu</b> (alt). Toprağı bütün kart boyunca sürekli bir katman yapmak: (1) her sinyalin dönüş yolu belirli ve kısa olur, (2) gürültü azalır, (3) RF hat empedansı tanımlı olur.</p>'
        '<h2>İz genişliği ve akım</h2><p>İz dar ve akım yüksekse ısınır. IPC-2221 yaklaşıklığı: A = (I / (k × ΔT<sup>0,44</sup>))<sup>1/0,725</sup> (alan mil²), dış katman için k = 0,048 [[bilgi]]; genişlik = alan / kalınlık. 1 oz bakır (35 µm) için 1 A ve ΔT = 10 °C yaklaşık 0,3 mm iz gerektirir (aşağıdaki hesap makinesiyle doğrula).</p>'
        + hesap('iz') + hesap('izdirenc')
        + '<h2>Via (delikli geçit)</h2><p>Katmanlar arası bakır delik. Bu kartlarda 0,3 mm delik, 0,6 mm pad (alıcıda 0,25/0,5). Akım yüksekse birden fazla via paralel konur. Toprak parçalarına via, topraktan düzleme en kısa yolu verir.</p>'
        '<h2>Boşluk (clearance)</h2><p>İki bakır arasındaki minimum mesafe: fabrikanın üretim kabiliyetine ve gerilime bağlı. Bu projede 0,14–0,15 mm; fabrikanın kuralı bundan küçük olmamalıdır [[dogrulanmadi]].</p>'
        '<h2>Isı</h2><p>Güç çipleri ısıyı bakır alana ve viaslar üstünden iç düzlemlere verir. Çipin altındaki ısı pad’i bu yüzden toprağa viaslarla bağlanır.</p>'
        + alistirma('3 A akıtan, 1 oz bakır dış katman izinin genişliği kaç mm olmalı (ΔT = 10 °C)?', 'Hesap makinesine 3 A yaz: yaklaşık 1,4 mm çıkar (IPC-2221 dış katman). Bu yüzden lamba akımı klemensten röleye geniş izle ya da bakır alanla taşınır.'))


@sayfa('surec', '8. Sıfırdan tasarım süreci', 'İlanı okuyup parça seçmekten üretim dosyasına kadar sıra.')
def _surec():
    return (
        '<h1>8. Sıfırdan tasarım süreci</h1><p class="ozet">Bu iki kart nasıl ortaya çıktı: adımlar ve her adımda sorulacak sorular.</p>'
        '<ol>'
        '<li><b>İsteği sayılara çevir.</b> “Uzaktan açılsın” → menzil? pil ömrü? boyut? Cevaplanmamış sorular için varsayılanlar yazılır ve müşteriye bildirilir.</li>'
        '<li><b>Blok şeması.</b> Fonksiyonlar kutular olarak çizilir: güç, işlemci, telsiz, arayüz. Her oka ne taşıdığı yazılır.</li>'
        '<li><b>Parça seçimi.</b> Her kutu için bir çip; ölçüt: gereksinim, bulunabilirlik, fiyat, referans devre var mı. Veri sayfası <i>okunur</i>: mutlak azami değerler, tipik devre, ayak tablosu.</li>'
        '<li><b>Güç bütçesi.</b> Her rayın azami akımı toplanır; çevirici ve bobin buna göre seçilir.</li>'
        '<li><b>Şema.</b> Üreticinin referans devresi esas alınır, değerler hesapla kontrol edilir; her net’in adı olur; ayak çakışmaları kontrol edilir (bu sitedeki çizimler bağlantı listesiyle makineyle denetlenir).</li>'
        '<li><b>Benzetim.</b> Kritik kısımlar (röle sürücü, giriş koruması) ngspice ile sınanır.</li>'
        '<li><b>Yerleşim.</b> Önce konnektörler ve çipler, sonra kondansatörler çipin ayağına en yakın.</li>'
        '<li><b>Yol çizimi.</b> Güç ve RF izleri önce, sinyaller sonra; katmanlar ve viaslar.</li>'
        '<li><b>Kural denetimi (DRC).</b> Boşluk, delik, kenar; bağlantısız ayak kalmayacak.</li>'
        '<li><b>Üretim dosyaları.</b> Gerber, delik, malzeme listesi, yerleştirme: bkz. <a href="uretim.html">sonraki sayfa</a>.</li>'
        '<li><b>İlk kartta ölçüm.</b> Gerilim rayları, saat, telsiz menzili; sorunlar bir sonraki sürüme yazılır.</li></ol>'
        + kutu('uyari', 'Bu projede 3–10 adımları yazılımla yapılmıştır; 11. adım (ölçüm) yoktur, çünkü kart üretilmedi. Menzil, anten uyumu ve hücresel bağlantı sahada denenmeden iddia edilmez.', 'Dürüst not'))


@sayfa('uretim', '9. Üretim dosyaları: Gerber, delik, malzeme listesi', 'Fabrikaya giden paketin her dosyası ne işe yarar, nasıl kontrol edilir.')
def _uretim():
    return (
        '<h1>9. Üretim dosyaları</h1><p class="ozet">Üretici KiCad’i değil, bu dosyaları okur.</p>'
        '<table><tr><th>Dosya</th><th>İçerik</th><th>Neye bakılır?</th></tr>'
        '<tr><td>Gerber (.gtl, .gbl, .g1, .g2…)</td><td>Her bakır katmanının resmi</td><td>Katman sayısı, kart kenarı (.gm1), lehim maskesi (.gts/.gbs), serigrafi (.gto/.gbo)</td></tr>'
        '<tr><td>Delik dosyası (.drl)</td><td>Her deliğin yeri ve çapı (kaplamalı/kaplamasız ayrı)</td><td>En küçük delik fabrikanın sınırından büyük mü?</td></tr>'
        '<tr><td>Malzeme listesi (BOM, .csv)</td><td>Her parçanın değeri, kaç tane, hangi referans</td><td>Parça numaraları, stok</td></tr>'
        '<tr><td>Yerleştirme dosyası (pick-and-place)</td><td>Her parçanın x, y, dönüş, yüz</td><td>Dönüş kuralları fabrikadan fabrikaya değişir</td></tr></table>'
        '<h2>Kendi kontrolünü yap</h2><ol><li>Gerber’ları bağımsız bir görüntüleyicide aç, katmanları sırala.</li><li>Kart kenarı kapalı bir çerçeve mi?</li><li>Deliklerin çapı ve sayısı delik dosyasıyla uyumlu mu?</li><li>BOM’daki her referans yerleştirme dosyasında var mı?</li><li>Fabrikanın kendi çevrimiçi DFM (üretilebilirlik) denetimine yükle.</li></ol>'
        '<h2>Kart üretim parametreleri</h2><p>Bu projede: 4 katman, 1,6 mm (varsayım) [[dogrulanmadi]], 1 oz bakır, HASL ya da ENIG kaplama, yeşil maske. Katman kalınlıkları (RF hat için) fabrikaya sorulur ve 50 Ω hesabı o değerle yenilenir.</p>'
        + kutu('ipucu', 'Üretim paketinin ilk açılışında bir kez de bağımsız görüntüleyicide ön ve arka resme bak: şemada olmayan bir şey (ters çevrilmiş parça, eksik delik) göze ilk orada çarpar.', 'Pratik'))


def uret(yaz):
    liste = ''.join('<li><a href="%s.html">%s</a> — %s</li>' % (i, html.escape(b), html.escape(o)) for i, b, o, f in SAYFALAR)
    yaz('temel/index.html', 'Temel bilgiler', '<h1>Temel bilgiler</h1><p class="ozet">Kartları anlamak için gereken kuramın kısa ve hesaplı özeti. Sırayla okumak en iyisidir.</p><ol>' + liste + '</ol>', 1)
    for i, b, o, f in SAYFALAR:
        yaz('temel/%s.html' % i, b, f(), 1, o)
