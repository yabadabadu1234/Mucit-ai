"""Parca siniflarinin ogretici bilgisi. Etiketler: [[ds]] veri sayfasindan okundu, [[bilgi]] genel muhendislik bilgisi (kaynak okunmadi),
[[tahmin]] hesap/varsayim, [[dogrulanmadi]] sahada ya da uretici belgesiyle dogrulanmasi gereken."""

SINIFLAR = {
'direnc': dict(
    ad='Direnç (kalın film, yüzey montajlı)',
    ne='Akımın geçişine belirli bir zorluk koyar; gerilimi bölmek, akımı sınırlamak, bir hattı yukarı ya da aşağı çekmek için kullanılır.',
    yapi='Alümina (alüminyum oksit seramik) bir tabanın üstüne rutenyum oksit içeren cam hamuru baskılanır, lazerle kesilerek değeri ayarlanır, üstü cam bir kaplamayla örtülür; uçlarda nikel üstüne kalay kaplı gümüş terminaller bulunur. [[bilgi]]',
    ozellik=['Değer serisi: yüzde 1 tolerans E96 serisi, yüzde 5 tolerans E24 serisi (örnek: 10k, 11k, 12k…).[[bilgi]]',
             '0603 kılıf (1,6 × 0,8 mm) için tipik anma gücü 0,1 W; 0805 için 0,125 W; 1206 için 0,25 W. Gerçek parçanın değeri üreticinin veri sayfasından okunur.[[bilgi]]',
             'Sıcaklık katsayısı tipik ±100 milyonda bir/°C düzeyindedir; hassas bölücülerde önemlidir.[[bilgi]]'],
    uc=['Güç sınırı: P = V²/R. 12 V altında 100 kΩ: 1,44 mW, rahat; 12 V altında 470 Ω: 306 mW, 0603 için fazla.',
        'Çok büyük değerlerde (1 MΩ ve üstü) yüzey kirliliği ve nem sızıntı yapar; ölçüm devrelerinde sorun olur.',
        'Sıfır ohm direnç: bir köprü (jumper) gibidir; ihtiyaç halinde söküp ayar yapmak için konur, akım sınırı vardır.']),
'kond_seramik': dict(
    ad='Çok katmanlı seramik kondansatör',
    ne='Elektrik yükünü depolar; ani akım ihtiyacını karşılar (ayrıştırma), gerilim dalgalanmasını yumuşatır (süzme), doğru akımı geçirmeyip değişen işareti geçirir (bağlama).',
    yapi='Barium titanat (BaTiO₃) seramik ince katmanları ile nikel elektrotlar üst üste dizilir; uçlarda bakır–nikel–kalay terminal vardır. Yüzlerce katman, küçük bir kutuda büyük kapasite sağlar. [[bilgi]]',
    ozellik=['Sınıf 1 (C0G / NP0): kapasite çok kararlıdır, değer küçüktür (pF–nF); kristal yükleri ve radyo devreleri için.[[bilgi]]',
             'Sınıf 2 (X5R: −55…+85 °C, X7R: −55…+125 °C, kapasite sapması ±%15 sıcaklıkla): küçük kutuda büyük değer verir ama gerilim altında kapasitesi düşer.[[bilgi]]',
             'Eşdeğer seri direnci (ESR) çok düşüktür (birkaç mΩ); anahtarlamalı çeviricilerde bu iyi bir şeydir.[[bilgi]]'],
    uc=['DC kayma (DC bias): 10 µF 6,3 V, 0603 kutuda, 3,3 V altında kapasite yarıdan aza düşebilir. Bu yüzden veri sayfası etkin kapasiteyi (gerilim altında) tanımlar. [[bilgi]] Tam sayıyı parçanın üretici eğrisinden okumak gerekir. [[dogrulanmadi]]',
        'Mikrofonik/piezo etkisi: seramik titreşimde gerilim üretir, ses çıkarabilir (büyük kondansatörlerde, 1 kHz civarında anahtarlamada).',
        'Kart eğilmesi seramiği çatlatır: kondansatörü kart kenarına ve vida deliğine yakın koyma; çatlak kısa devre yapar.',
        'Sıcaklık: X5R en fazla 85 °C; kalın bir pil sıcaklığında sorun değildir.',
        'Dielektrik sınıfı (X5R/X7R) malzeme listesinde yazılmalıdır; yazılmazsa satın alma Y5V gibi kötü bir sınıf alabilir. [[tahmin]]']),
'kond_elektrolit': dict(
    ad='Alüminyum elektrolitik kondansatör',
    ne='Büyük kapasite gerektiğinde (yüzlerce mikrofarad) enerji deposu olarak çalışır; kutupludur.',
    yapi='Aşındırılmış alüminyum folyo üzerinde ince bir alüminyum oksit tabaka dielektriktir; elektrolit sıvısı ile ıslatılmış kağıt ara tabakası vardır. Ters bağlanırsa oksit çözülür ve gaz çıkar. [[bilgi]]',
    ozellik=['Kutuplu: artı uç eksiden yüksek gerilimde olmalıdır.[[bilgi]]','Ömrü sıcaklıkla azalır: sıcaklık 10 °C artınca ömür yarıya iner (kaba kural).[[bilgi]]'],
    uc=['Anma gerilimi, çalışma geriliminin en az 1,5–2 katı olmalıdır; 12 V hat için 25 V seçilir.',
        'Kart eğilirse ve kapak açık çıkarsa dışarı sıvı kaçırabilir; 105 °C sınıfı tercih edilir.']),
'kond_polimer': dict(
    ad='Polimer alüminyum kondansatör',
    ne='Elektrolitik kondansatörün katı polimer elektrolitli türüdür: ESR çok düşük, ömrü uzun, sıvısı yoktur.',
    yapi='Alüminyum folyo üzerinde oksit dielektrik; elektrolit yerine iletken polimer (örneğin PEDOT) kullanılır.[[bilgi]]',
    ozellik=['Çok düşük ESR: akım darbelerinde gerilim düşüşü azdır (modem gibi 2 A tepe çeken yüklere uygundur).[[bilgi]]'],
    uc=['Anma gerilimi aşılırsa kısa devreye gidebilir; marj bırakılır.','Kutupludur.']),
'bobin': dict(
    ad='Güç bobini (ferrit/metal tozlu, ekranlı)',
    ne='Akım değişimine direnir; anahtarlamalı çeviricilerde enerjiyi geçici olarak manyetik alanda depolar ve çıkışa aktarır.',
    yapi='Bir manyetik çekirdek (ferrit veya metal tozu) etrafına sarılmış bakır tel; ekranlı tipte çekirdek tel sargıyı çevreler ve yayılan manyetik alanı azaltır.[[bilgi]]',
    ozellik=['L: indüktans (µH). Doyma akımı Isat: indüktansın yüzde 20–30 düştüğü akım. Isıl akım Irms: parçayı 40 °C ısıtan akım. DCR: doğru akım direnci (verimi belirler).[[bilgi]]',
             'Çekirdek doyarsa bobin bir telden farksız kalır, akım hızla artar ve çevirici çipini zorlar.[[bilgi]]'],
    uc=['Tepe akım Isat’ı aşarsa çevirici kısa devre gibi davranıp çipi sınırlama moduna sokar.',
        'Akım dalgalanmasını büyük bobin azaltır ama yük değişimine yavaş yanıt verir.',
        'Bobinin altında ve çevresinde sinyal izi geçirme: manyetik alan gürültü bağlar.']),
'boncuk': dict(
    ad='Ferrit boncuk',
    ne='Yüksek frekanslı gürültüyü ısıya çevirerek keser, doğru akımı geçirir; bir besleme hattını bir bölümden ayırmak için kullanılır.',
    yapi='Manyetik ferrit malzemeden kalın filmle yapılmış, direnç gibi görünen bir parçadır; düşük frekansta tel, yüksek frekansta (örneğin 100 MHz) dirençtir.[[bilgi]]',
    ozellik=['"120R @100MHz": 100 MHz’de 120 Ω empedans gösterir; DC direnci küçüktür.[[bilgi]]'],
    uc=['Doğru akım yüklenirse empedansı düşer (doyma); akım değeri kontrol edilir.','Kondansatörle birlikte alçak geçiren süzgeç kurar; rezonans sorun olabilir.']),
'sigorta_ptc': dict(
    ad='Kendini toparlayan sigorta (polimerik pozitif sıcaklık katsayılı direnç)',
    ne='Aşırı akımda ısınıp direnci birden yükselerek akımı keser; akım kalkıp soğuyunca eski hâline döner.',
    yapi='İletken karbon parçacıklı bir polimer; ısınınca polimer genleşir, parçacıklar birbirinden ayrılır ve direnç yüzlerce kat artar. [[bilgi]]',
    ozellik=['"Tutma akımı" (hold) altında sürekli akım geçer; "kesme akımı" (trip) üstünde açar; açma süresi akıma bağlıdır.[[bilgi]]'],
    uc=['Açıkken bile az bir akım geçirir (yüzlerce mA’ya kadar kaçak olabilir), tam kesmez.','Sıcak ortamda tutma akımı düşer (derating).','Yüksek gerilimli bir kısa devreyi tek başına kesemeyebilir; gerilim anma değerine bakılır.']),
'diyot_schottky': dict(
    ad='Schottky diyot',
    ne='Akımı tek yönde geçirir; ileri gerilim düşümü silisyum PN diyottan çok daha küçüktür.',
    yapi='Metal–yarı iletken eklemi kullanılır; taşıyıcılar çoğunluk taşıyıcılarıdır, depolanmış yük yok denecek kadar azdır, bu yüzden çok hızlı kapanır. [[bilgi]]',
    ozellik=['SS14: 40 V ters gerilim, 1 A ortalama akım, SMA kılıf; ileri düşüm yaklaşık 0,3–0,5 V (akıma bağlı).[[bilgi]] Parçanın veri sayfası bu çalışmada okunmadı. [[dogrulanmadi]]'],
    uc=['Ters kaçak akımı sıcaklıkla hızla artar (silisyum diyoda göre yüksektir).','İleri düşüm düşük akımda bile 0,2–0,3 V olabilir; pilli devrede pil gerilimini azaltır.']),
'diyot_zener': dict(
    ad='Zener diyot',
    ne='Ters yönde belirli bir gerilimde iletime geçer ve gerilimi o değerde sabitler; sınırlayıcı ve referans olarak kullanılır.',
    yapi='Yüksek katkılı PN eklemi; ters gerilim belirli bir değere ulaşınca Zener/çığ olayı ile iletim başlar. [[bilgi]]',
    ozellik=['Düşük akım ve düşük güç içindir (SOD-123 kılıfta tipik 500 mW).[[bilgi]]'],
    uc=['Zener gerilimi akıma ve sıcaklığa bağlıdır; kesin referans için uygun değildir.','Sürekli güç = Vz × I; kılıfın sınırını aşma.']),
'diyot_tvs': dict(
    ad='Geçici gerilim bastırıcı diyot (TVS)',
    ne='Aşırı gerilim darbesinde (yıldırım, endüktif yük atması) iletime geçerek darbeyi toprağa akıtır ve korunan devreyi sınırlar.',
    yapi='Büyük alanlı, çığ bölgesinde çalışan PN eklemi; çok yüksek anlık güç taşıyacak şekilde üretilir.[[bilgi]]',
    ozellik=['SMBJ15A: tek yönlü, 15 V ters bekleme gerilimi; sınırlama gerilimi bunun üstündedir (veri sayfasında verilir).[[bilgi]] [[dogrulanmadi]]'],
    uc=['Bekleme geriliminin üstündeki sürekli gerilimde ısınıp bozulur.','Darbe enerjisi sınırlıdır: kısa süreli darbe içindir, sürekli aşırı gerilim için değildir.']),
'led': dict(
    ad='Işık yayan diyot (LED)',
    ne='Akım geçince ışık verir; durum göstergesi olarak kullanılır.',
    yapi='Yarı iletken PN eklemi; elektron–boşluk birleşmesinde foton yayar. Rengi malzemeye bağlıdır: yeşil/kırmızı LED’lerde ileri düşüm yaklaşık 2 V’tur. [[bilgi]]',
    ozellik=['Akım sınırı ayrı bir dirençle yapılır; LED’in kendisi akımı sınırlamaz.[[bilgi]]'],
    uc=['Yüksek parlaklıklı LED 1–2 mA’da bile görünür; pilli devrelerde akım küçük tutulur.','Ters gerilime dayanıklılığı çok düşüktür (birkaç volt).']),
'transistor_npn': dict(
    ad='NPN transistör (MMBT2222A)',
    ne='Küçük bir taban akımı ile büyük bir toplayıcı akımını anahtarlar; bu kartta bir röleyi ya da modem düğmesini sürer.',
    yapi='Silisyumdan üç katmanlı (N–P–N) yapı; taban akımı toplayıcı akımını kontrol eder.[[bilgi]]',
    ozellik=['Doyma durumunda toplayıcı–yayıcı gerilimi küçüktür (yük akımının onda biri taban akımı verilirse, sayılar veri sayfasından).[[bilgi]]'],
    uc=['Tabanda seri direnç yoksa taban–yayıcı eklemi aşırı akım çeker.','Taban boşta kalırsa gürültüyle iletime girebilir; bu yüzden tabandan toprağa direnç konur.','Endüktif yük (röle bobini) kesilince ters gerilim üretir; yük diyodu şarttır.']),
'mosfet_p': dict(
    ad='P kanallı alan etkili transistör (MOSFET)',
    ne='Kapı gerilimiyle kontrol edilen bir anahtardır; ters gerilim koruması için ideal diyot gibi kullanılır.',
    yapi='Silisyum üzerinde yalıtılmış kapı (kapı oksidi) ile kanal oluşturulur. P kanalda kaynak (source) savaktan (drain) daha yüksek gerilimdedir ve kapı kaynağın altına çekilince iletir.[[bilgi]]',
    ozellik=['Kapı–kaynak gerilimi sınırı tipik ±12 V’tur (AO3401A için kontrol edilmeli).[[dogrulanmadi]]'],
    uc=['Giriş ters bağlanırsa gövde diyodu da ters olur ve akım geçmez; kapı gerilimi kaynak gerilimini izleyip kaynağa Zener ile sınırlanır.','Giriş 12 V’tan fazlaysa kapı oksidi zorlanır; Zener bu yüzden vardır.']),
'konnektor_usbc': dict(
    ad='USB Type-C soket (16 uçlu, USB 2.0)',
    ne='Programlama ve beslemeye yarayan bağlantı noktasıdır.',
    yapi='Metal kılıflı, iki satırlı 24 uçlu soketin USB 2.0’a indirgenmiş 16 uçlu sürümü: iki VBUS, iki CC, iki D+/D−, yer uçları.[[bilgi]]',
    ozellik=['CC1 ve CC2 uçlarının her biri 5,1 kΩ ile toprağa bağlanırsa cihaz "tüketici (sink)" olarak tanınır ve kaynak 5 V verir.[[bilgi]]',
             'Fişin yönü tersinir olduğundan D+ iki ucu (A6/B6) ve D− iki ucu (A7/B7) kartta birbirine bağlanır.[[bilgi]]'],
    uc=['CC dirençleri takılmazsa C-C kablo ile güç gelmez.','Gövde (SHIELD) bağlantısı: topraklama doğrudan ya da dirençle yapılır; burada doğrudan toprağa alındı.']),
'esd_usb': dict(
    ad='USB hattı için çok küçük kapasiteli ESD koruma (USBLC6-2SC6)',
    ne='USB veri hatlarına dokunmakla gelen statik elektrik boşalmasını (ESD) toprağa akıtır.',
    yapi='Hat başına iki diyot (toprağa ve besleme hattına) ve bir Zener içeren, düşük kapasiteli bir diyot dizisi.[[bilgi]]',
    ozellik=['Hat kapasitesi birkaç pF düzeyindedir; USB tam hızı (12 Mbit/sn) etkilenmez.[[bilgi]] [[dogrulanmadi]]'],
    uc=['Koruma parçası konnektöre en yakın yerleştirilmelidir; aksi hâlde boşalma akımı kartın içinden geçer.','Besleme ucu (VBUS) bağlı olmalı, aksi hâlde sınırlama gerilimi değişir.']),
'anahtar_kayar': dict(
    ad='Kaydırmalı anahtar',
    ne='Pili devreden çıkarıp takar; elle yapılan genel açma-kapama.',
    yapi='Metal kontaklı mekanik anahtar; kayan bir parça kontakları köprüler.[[bilgi]]',
    ozellik=['Kontak akım ve gerilim sınırı vardır; 3 V pil devresi için sorun değildir.[[bilgi]]','Bu karttaki parça tek kutuplu çift konumlu (SPDT) olup ortak ve bir uç kullanılır; boşta kalan uç bağlı değildir.'],
    uc=['Kontak direnci birkaç ohm-mili düzeyindedir, zamanla oksitlenirse artar.','Yüksek ani akımlı çeviriciler anahtar kontağını ısıtabilir.']),
'dugme': dict(
    ad='Dokunmatik (basmalı) düğme',
    ne='Basılınca iki ucunu kısa devre eder; mikrodenetleyiciye "bastım" sinyali verir.',
    yapi='Yaylı bir metal kubbe, basılınca altındaki iki kontağı köprüler.[[bilgi]]',
    ozellik=['Bırakılınca hat bir direnç ile yukarı çekilir (R2–R7: 100 kΩ), basılınca toprağa iner.[[bilgi]]'],
    uc=['Kontak sıçraması: basılınca birkaç milisaniye gürültü olur; yazılımla ya da donanımla ayıklanır.','Statik boşalma düğme gövdesinden girer; hat üzerine seri direnç ve küçük kondansatör eklenebilir (burada eklenmedi).']),
'sma': dict(
    ad='Kenara monte SMA anten konnektörü',
    ne='Telsiz anten çıkışıdır; 50 Ω’luk hattı dış antene bağlar.',
    yapi='Altın kaplı iç iletken ve metal gövde; kart kenarına oturan sürüm, sinyal pedini doğrudan hat ucuna getirir.[[bilgi]]',
    ozellik=['Empedans 50 Ω; kart tarafındaki hat da 50 Ω olmalıdır.[[bilgi]]'],
    uc=['Konnektör bacağıyla hat arasında kopukluk sinyali yansıtır; kenar montajda ped ile iz aynı genişlikte ya da yumuşak geçişli olmalıdır.','Antensiz çalıştırma radyo çıkış katına zarar verebilir: yük yok iken verici açma.']),
'ufl': dict(
    ad='u.FL (mini koaksiyel) anten konnektörü',
    ne='Modem anteni için küçük bir koaksiyel bağlantıdır; ince kabloyla (pigtail) SMA’ya geçilir.',
    yapi='Yaylı iç kontaklı, üstten geçmeli minyatür koaksiyel konnektör.[[bilgi]]',
    ozellik=['Takılıp sökülme sayısı sınırlıdır (tipik 30 civarı).[[bilgi]]'],
    uc=['Geçici kullanım için; sürekli titreşimde kablo sabitlenmelidir.']),
'bornier': dict(
    ad='Vidalı klemens (5,08 mm adımlı)',
    ne='Kalın kabloları vidalayarak karta bağlar (12 V giriş, lamba çıkışı).',
    yapi='Bakır alaşımlı kontak ve vidalı sıkıştırıcı; plastik gövde.[[bilgi]]',
    ozellik=['Anma akımı bu tipte genellikle 8–10 A düzeyindedir; gerçek parçanın verisine bakılır.[[bilgi]] [[dogrulanmadi]]'],
    uc=['Vidalı bağlantı titreşimle gevşer; tel ucu kalaylanmamalı (ezilir), pabuç ya da yaylı uç kullan.']),
'tps63031': dict(
    ad='Tek bobinli yükselten-düşüren çevirici (TPS63031)',
    ne='Pil gerilimi 3,3 V’un altına da üstüne de çıksa çıkışı sabit 3,3 V tutar.',
    yapi='Dört içsel N kanallı MOSFET anahtar ve ortak bir bobin: giriş çıkıştan yüksekse düşüren, düşükse yükselten gibi çalışır. [[ds]]',
    ozellik=['Giriş 1,8–5,5 V; sabit 3,3 V çıkış (TPS63031); anahtarlama frekansı tipik 2,4 MHz; hareketsiz akım 25 µA tipik. [[ds]]',
             'Düşürme modunda 800 mA (VIN = 3,6–5,5 V), yükseltme modunda 500 mA (VIN > 2,4 V) çıkış akımı. [[ds]]',
             'Ortalama anahtar akım sınırı: 900 / 1000 / 1300 mA (en az/tipik/en çok). [[ds]]',
             'PS/SYNC ucu toprakta iken "güç tasarrufu" modu açık, yüksekte iken kapalı. [[ds]]',
             'Kapalı (EN düşük) iken yük giriş hattından ayrılır, kaçak 0,1 µA tipik. [[ds]]'],
    uc=['Boş pilde (giriş 1,8 V) yükseltme modunda çıkış akımı düşer: Bölüm "Hesap" içindeki tepe akım denklemiyle 300 mA yük için bobin tepe akımı yaklaşık 0,73 A bulunur (ve bobin doyma akımı en az 0,87 A olmalıdır).[[ds]]',
        'Başlama gerilimi (start-up) 1,6–2,0 V; çalışırken düşük gerilim kilidi (UVLO) 1,4–1,6 V. Başlamak çalışmayı sürdürmekten daha fazla gerilim ister. [[ds]]',
        'Aşırı sıcaklıkta (140 °C) durur, 20 °C histerezisle yeniden başlar. [[ds]]',
        'GND (denetim yeri) ve PGND (güç yeri) ayrı uçlardır ve kartta tek noktada birleşmelidir. [[ds]]']),
'esp32s3': dict(
    ad='ESP32-S3-WROOM-1 (Wi-Fi ve Bluetooth LE işlemci modülü)',
    ne='Kartın beyni: düğmeleri okur, telsiz modülünü SPI üzerinden yönetir, USB üzerinden programlanır.',
    yapi='Espressif ESP32-S3 yongası, flash bellek, kristal ve kart üzerinde anten bir metal kalkan altında tek modül olarak lehimlenir. [[bilgi]]',
    ozellik=['3,0–3,6 V besleme; çift çekirdek 240 MHz; yerleşik USB tam hız cihaz denetleyicisi (IO19=D−, IO20=D+).[[bilgi]]',
             'N4: 4 MB flash, yonga üstü ek bellek (PSRAM) yok.[[bilgi]]',
             'Kart anteninin çevresi ve altı bakır, bileşen ve iz içermemelidir (anten keepout alanı); modül kart kenarında olmalıdır.[[bilgi]]'],
    uc=['Açılışta bazı uçların seviyesi modun seçilmesini sağlar (strapping): IO0 düşük → programlama kipi. Bu uçlara bağlanan devrenin açılışta yanlış seviye vermesi cihazı açamaz hâle getirir.',
        'EN ucu düşük = sıfırlama; RC süzgeci (10 kΩ + 1 µF) açılışta ≈ 10 ms gecikme verir (τ = 10 ms).',
        'Wi-Fi vericisi açıkken akım 300–400 mA’ya çıkabilir; bu kartta Wi-Fi kullanılmadığı varsayıldı. [[tahmin]]']),
'ra01h': dict(
    ad='Ra-01H (Ai-Thinker, LoRa telsiz modülü, SX1276 yongalı)',
    ne='915 MHz bandında uzun menzilli, düşük hızlı mesaj gönderir ve alır.',
    yapi='Semtech SX1276 yongası, kristal ve süzgeç 17 × 16 × 3,2 mm’lik bir modül üzerinde; kenarlarında 16 yarım delikli (kastel) pad vardır; SPI ile kontrol edilir. [[ds]]',
    ozellik=['803–930 MHz; besleme 1,8–3,6 V (tipik 3,3 V); en çok +19 dBm çıkış, çıkış akımı en çok 105 mA. [[ds]]',
             '915 MHz’de ortalama akım: gönderme 97 mA, alma 12,15 mA, bekleme (standby) 1,5 mA. [[ds]]',
             'SPI ucları SCK/MISO/MOSI/NSS; sıfırlama RESET; kesme DIO0 ve DIO1; antene ANT ucu (pin 1); üç GND ucu (2, 9, 16). [[ds]]'],
    uc=['ANT ucu 50 Ω hat ile SMA’ya gitmelidir; anten takılı değilken gönderme yapılmaz.','Besleme dalgalanması vericide çıkış spektrumunu bozar; çıkışa yakın 10 µF + 100 nF gerekir.',
        'Bu kartın ayak izi, aynı boyuttaki Ra-01/Ra-02 kılavuzunun çizimine göre kuruldu; Ra-01H belgesinde ölçü çizimi yoktur: üretimden önce Ai-Thinker’e teyit ettirilmelidir. [[dogrulanmadi]]']),
'tps62933': dict(
    ad='TPS62933 (3 A senkron düşüren çevirici)',
    ne='12 V’u geri besleme bölücüsüyle belirlenen düşük gerilime (bu kartta 3,3 V ve 4,0 V) verimli biçimde indirir.',
    yapi='Çipin içinde iki güç transistörü (üst anahtar 76 mΩ, alt anahtar 32 mΩ), denetim devresi ve yumuşak başlatma vardır; dışarıdan bobin, giriş/çıkış kondansatörleri, 100 nF bootstrap kondansatörü, SS kondansatörü ve geri besleme bölücüsü istenir. Dahili kompanzasyon vardır: dışarıdan kontrol döngüsü parçası gerekmez. [[ds]]',
    ozellik=['Giriş 3,8–30 V (mutlak azami 32 V), çıkış 0,8–22 V, sürekli çıkış akımı 3 A. [[ds]]',
             'Referans 0,8 V ±%1 (25 °C): V<sub>çıkış</sub> = 0,8 × (1 + R<sub>üst</sub>/R<sub>alt</sub>). [[ds]]',
             'RT ucu açık bırakılırsa anahtarlama ≈ 500 kHz, toprağa bağlanırsa ≈ 1,2 MHz; bir direnç bağlanarak 200 kHz–2,2 MHz ayarlanır. [[ds]]',
             'Boşta kalma akımı 12 µA (anahtarlamasız), kapalıyken 2 µA; hafif yükte darbe frekansı modülasyonu (PFM) ve yayılı spektrum (EMI azaltır). [[ds]]',
             'Yüksek taraf akım sınırı ≈ 5 A (4,2–5,8), düşük taraf ≈ 3,8 A; çıkış gerilimi %65’in altına düşerse hıçkırık (hiccup) kipine girer; çıkış %115’i aşarsa aşırı gerilim koruması; sıcaklık 165 °C’de durdurur. [[ds]]'],
    uc=['SS ucuna en az 6,8 nF seramik kondansatör bağlanmalı (≈ 1 ms yumuşak başlatma) ve uç asla havada bırakılmamalı. [[ds]]',
        'EN: yükselen eşik ≈ 1,21 V; bağlanmadan bırakılırsa çip açık kalır; harici bölücü ile giriş düşük-gerilim kilidi ayarlanabilir. EN azami 5,5 V önerilir; 12 V’tan doğrudan sürmek yerine bölücü kullanılır. [[ds]]',
        'En küçük açık kalma süresi 70 ns, en küçük kapalı kalma 140 ns: 12 V → 3,3 V’ta görev oranı 0,275, 500 kHz’de açık süre 550 ns: sorun yok; ama 30 V → 0,8 V gibi aşırı dönüşümde frekans düşürülmelidir. [[ds]]',
        'Giriş kondansatörleri VIN ucu ile GND arasına çipe doğrudan bağlanır; yol uzarsa anahtarlama kenarları giriş hattında zil çalar. [[ds]]',
        'Isıl direnç değeri (112 °C/W) yalnızca parçaları kendi arasında karşılaştırmak içindir; gerçek ısınma kart bakırına bağlıdır (TI kendi 2 katmanlı EVM kartında 60 °C/W ölçmüştür). [[ds]]',
        'Bobin tepe akımı doyma akımının altında kalmalı; modem rayındaki 2 A’lik darbeler bu yüzden hesaplanır (bobin kartına bakın).']),
'w5500': dict(
    ad='W5500 (donanım TCP/IP Ethernet çipi)',
    ne='Ethernet (10/100 Mb/s) bağlantısını işlemci yerine kendisi yürütür: TCP, UDP, IP protokollerini donanımda çalıştırır; işlemci ona SPI ile yalnız veri verir.',
    yapi='Tek yonga: MAC, PHY (fiziksel katman), 8 soket, 32 KB iç tampon, içte 1,2 V düzenleyici. [[bilgi]]',
    ozellik=['3,3 V besleme; SPI en çok 80 MHz kuramsal, 33,3 MHz garantili.[[ds]] Giriş uçlarının 5 V’a dayanıklı olduğu bilgisi hafızadandır.[[bilgi]]',
             'Dış parçalar: 25 MHz kristal, EXRES1’e 12,4 kΩ %1 direnç, 1V2O ve TOCAP uçlarına kondansatör, TX/RX fark çiftleri için ayrı besleme süzgeçleri.[[ds]]',
             'RJ45 konnektöründeki yerleşik trafo (magnetics) hattı yalıtır; çipin TXP/TXN, RXP/RXN uçları doğrudan buna gider.[[bilgi]]'],
    uc=['EXRES1 direnci %1 olmalı; yanlış değer akım referansını ve Ethernet çıkış seviyesini bozar.',
        'Analog besleme (+3V3A) bir ferrit boncuk ile süzülür; dijital gürültü PHY’ye geçmemeli.',
        'Kristal yük kapasitesi hesabı: C<sub>yük</sub> = C1·C2/(C1+C2) + C<sub>kaçak</sub>; kristal veri sayfasındaki yük değeriyle eşleşmezse frekans kayar.',
        'Fark çiftlerinin (TX, RX) izleri aynı uzunlukta ve birbirine yakın tutulmalıdır.']),
'a7670': dict(
    ad='A7670SA (SIMCom, 4G LTE Cat 1 modem modülü)',
    ne='Kartı cep telefonu şebekesine bağlar; internet için veri bağlantısı sağlar. İşlemci ile seri hatla (UART, AT komutları) konuşur.',
    yapi='Tek bir LGA (alt yüzünde lehim pedleri olan) 24 × 24 mm, 88 pedli modül: baseband işlemcisi, RF, güç yönetimi, SIM arayüzü. [[ds]]',
    ozellik=['LTE-FDD B1/B2/B3/B4/B5/B7/B8/B28/B66 ve GSM 850/900/1800/1900; Cat 1 (10 Mbit/sn aşağı, 5 Mbit/sn yukarı). Şili’de kullanılan bantlar (B28, B7, B4, B2, B66, B5) listededir. [[ds]]',
             'Besleme 3,4–4,2 V (tipik 3,8 V); gönderirken kısa süreli yaklaşık 2,8 A çeker; belge en az 300 µF önerir: bu yüzden ayrı çevirici ve 330 µF polimer kondansatör kullanıldı. [[ds]]',
             'Seri hat mantık düzeyi 1,8 V: işlemcinin 3,3 V’uyla arada seviye çevirici gerekir. [[ds]]',
             'Açma: PWRKEY ayağı belirli süre düşük tutulur; sıfırlama: RESET ayağı; ikisi de modül içinde 50 kΩ ile VBAT’a çekilidir ve en çok 10 nF yük kabul eder. [[ds]]'],
    uc=['LASC/LASE/FASE/MASC son eklerinin farkı SIMCom belgelerinde yazılı değildir; satın almadan önce satıcıya yazılı sorulmalıdır. [[dogrulanmadi]]',
        'Besleme çökerse modem şebekeden düşer ve yeniden açılması gerekir: modem rayına ayrı çevirici ve büyük kondansatör bu nedenle konuldu.',
        'Ana anten izi 50 Ω olmalı, Ethernet ve LoRa hatlarından uzak durmalı. Belgedeki iki “yasak alan” karesi üst katmanda bakırsız bırakılmıştır.',
        'SIM kartı kısa devre ve elektrostatik yüke karşı korunmalıdır: SIM hatlarına ESD koruma çipi (USBLC6) ve 22 Ω seri direnç konur.']),
'lm66100': dict(
    ad='LM66100 (ideal diyot, TI)',
    ne='İki beslemeyi (12 V’tan gelen 3,3 V ve USB’den gelen 3,3 V) birleştirirken geri akımı keser ve Schottky diyottan çok daha az gerilim düşürür.',
    yapi='İçinde bir P kanallı MOSFET ve geri akımı algılayan denetim devresi vardır; CE ucu VOUT’a bağlandığında geri akım engellenir. [[ds]]',
    ozellik=['Açık direnç yaklaşık 91 mΩ (3,6 V’ta), yani 0,3 A’de yaklaşık 30 mV düşüm. [[ds]]','ST ucu durum çıkışıdır; bu kartta toprağa bağlıdır. [[ds]]'],
    uc=['Giriş–çıkış ters kutuplanırsa MOSFET kapanır ve akım geri gitmez; yalnız CE ucunun doğru bağlanması gerekir. [[ds]]']),
'ap2112': dict(
    ad='AP2112K-3.3 (doğrusal düzenleyici, LDO)',
    ne='USB’nin 5 V’unu 3,3 V’a çevirir; kart yalnız USB ile programlanırken 12 V olmadan çalışmasını sağlar.',
    yapi='Bir güç transistörü (pass element) ve hata yükselteci; giriş-çıkış farkını ısıya çevirir. [[bilgi]]',
    ozellik=['600 mA sınıfı, düşük kalıcı akım (iki üç düzine µA).[[bilgi]]','Girişte ve çıkışta küçük seramik kondansatör ister.[[bilgi]]'],
    uc=['Isı: P = (5 − 3,3) × I. 300 mA’de 0,5 W: SOT-23-5 kılıfı için sınırda; bu yüzden yalnız USB ile programlama sırasında kullanılır. [[tahmin]]',
        'Besleme hem 12 V çeviriciden hem de USB’den gelirse bir diyotla veya kapıyla ayrılmalı ki akım geri akmasın.']),
'role': dict(
    ad='SRD-12VDC-SL-A (elektromekanik röle)',
    ne='Küçük akımla (bobin) büyük akımı (kontak) açıp kapatır; lamba gibi yükü işlemciden yalıtılmış biçimde sürer.',
    yapi='Bobin demir çekirdeği çeker, bir mıknatıs/yay sistemi kontağı hareket ettirir. Normalde açık (NO) kontak bobin enerjilenince kapanır. [[bilgi]]',
    ozellik=['Bobin 12 V, yaklaşık 400 Ω, ≈ 30 mA; kontak yaklaşık 10 A anma (yük türüne göre değişir).[[bilgi]]','Çekme/bırakma süresi onlarca milisaniye, ömür yüz bin mertebesi anahtarlama.[[bilgi]]'],
    uc=['Kapanırken bobin ters gerilim tepesi üretir: flyback diyodu (SS14) şarttır.',
        'Kontak akımı yüksekse iz kalın olmalı (bkz. “iz genişliği”); bu kartta lamba akımı 12 V klemensten direkt kontağa gider.',
        'Kontağın yüke bağlı gerilim ve akım anma değerleri alternatif ve doğru akım için farklıdır; doğru akım anma değeri düşüktür (ark söndürmek zordur). [[bilgi]]']),
'rj45': dict(
    ad='HR911105A (RJ45 konnektör, yerleşik trafolu)',
    ne='Ethernet kablosunun girdiği soket; içindeki trafo ve LED’ler konnektörle bir arada.',
    yapi='Plastik gövde içinde 8 temas ucu, iki çift için yalıtım trafosu (1:1) ve iki LED. Kılıf toprağa bağlanır. [[bilgi]]',
    ozellik=['Trafo, kablodan gelen toprak potansiyel farklarını ve darbeleri çipten ayırır.[[bilgi]]','Orta uçlar (center tap) 3,3 V’a bobin/direnç ile bağlanır; bu kartta W5500 referans devresi izlendi.[[bilgi]]'],
    uc=['Kılıf ucunu toprağa doğrudan değil, yüksek gerilimli bir kondansatörle (genellikle 1 nF/2 kV) bağlamak yaygındır; bu kartta karşılığı vardır (C41). [[bilgi]]',
        'Fark çiftlerinin altından toprak düzlemini kesme; çiftler kısa ve eşit uzunlukta olmalı.']),
'simsoket': dict(
    ad='Mikro-SIM kart yuvası',
    ne='SIM kartın modemle temas ettiği yuva.',
    yapi='Metal kontak telleri ve plastik gövde; 6 kontak (C1–C7). [[bilgi]]',
    ozellik=['Kart arka yüzde ve modülün altındadır: SIM hatları kısa olsun diye.'],
    uc=['Nano-SIM için adaptör gerekir; ilk planda nano yuva vardı, kütüphanede micro bulunduğu için değişti.']),
'kristal': dict(
    ad='Kristal (25 MHz)',
    ne='W5500’ün zaman tabanını üretir: çipin içindeki yükselteç kristali titreştirir.',
    yapi='Kuvars plaka iki elektrot arasında; mekanik titreşim elektriksel rezonansa dönüşür. [[bilgi]]',
    ozellik=['İki yük kondansatörü (C39, C40) rezonans frekansını belirler.'],
    uc=['Yük kapasitesi uyumsuzsa frekans kayar; Ethernet bağlantısı 100 ppm gibi sapmaları tolere eder ama yine hesaplanmalıdır.[[bilgi]]','Kristal çipe çok yakın, altı toprak, çevresinde yüksek akım izi olmamalı.']),
'txb0104': dict(
    ad='TXB0104 (4 bit, iki yönlü seviye çevirici)',
    ne='İşlemcinin 3,3 V mantığı ile modemin 1,8 V mantığı arasında sinyalleri çevirir.',
    yapi='Her kanalda iki yöne de çalışan sürücü ve yön algılama devresi; yön pini yoktur. [[bilgi]]',
    ozellik=['A tarafı düşük gerilim (burada 1,8 V), B tarafı yüksek (3,3 V); OE ucu çıkışları açar/kapatır.[[bilgi]]'],
    uc=['Kullanılmayan kanalın A4/B4 uçları boş bırakılamaz: yüzer girişler hatalı yön algılar; toprağa bağlanır (bu çalışmada düzeltildi).',
        'Yön algılama zayıf sürücülerle yapılır: hat üzerinde 10 kΩ’dan küçük yukarı/aşağı çekme direnci varsa kanal bozulabilir. [[bilgi]]',
        'Seri hat hızlarında (115 kb/s) sorun çıkarmaz.']),
'testpad': dict(
    ad='Test noktası',
    ne='Üretimden sonra ölçüm probunu değmek için çıplak bakır pad.',
    yapi='Lehim maskesinde açıklık bırakılmış tek bakır alan.',
    ozellik=['Alıcıda: USB_BOOT, VDD_1V8, UART_LOG_TX, modem USB VBUS/DP/DM.'],
    uc=['USB hatlarındaki test pad’i kök bırakılırsa küçük bir “dal” oluşur; uzunluğu kısa tutulur.']),

}

def sinif_bul(ref, p):
    sem = p['sembol']; deg = p['deger']; fp = p['fp'] or ''
    if sem.startswith('Device:R') and not sem.startswith('Device:R_'):
        return 'direnc'
    if sem == 'Device:C':
        return 'kond_seramik'
    if sem == 'Device:C_Polarized':
        return 'kond_polimer' if 'polimer' in deg else 'kond_elektrolit'
    if sem == 'Device:L':
        return 'bobin'
    if sem == 'Device:FerriteBead':
        return 'boncuk'
    if sem == 'Device:Polyfuse':
        return 'sigorta_ptc'
    if sem in ('Diode:SS14',):
        return 'diyot_schottky'
    if sem == 'Device:D_Zener':
        return 'diyot_zener'
    if sem.startswith('Diode:SMAJ') or sem.startswith('Diode:SMBJ'):
        return 'diyot_tvs'
    if sem == 'Device:LED':
        return 'led'
    if sem == 'Device:Q_NPN_BEC':
        return 'transistor_npn'
    if sem == 'Transistor_FET:AO3401A':
        return 'mosfet_p'
    if sem.startswith('Connector:USB_C'):
        return 'konnektor_usbc'
    if sem == 'Power_Protection:USBLC6-2SC6':
        return 'esd_usb'
    if sem == 'Switch:SW_SPDT':
        return 'anahtar_kayar'
    if sem == 'Switch:SW_Push':
        return 'dugme'
    if sem == 'Connector:Conn_Coaxial':
        return 'ufl' if 'U.FL' in fp else 'sma'
    if sem == 'Connector:Screw_Terminal_01x02':
        return 'bornier'
    if sem.startswith('Regulator_Switching:TPS63031'):
        return 'tps63031'
    if sem.startswith('RF_Module:ESP32-S3'):
        return 'esp32s3'
    if sem == 'Ozel:Ra-01H': return 'ra01h'
    if sem == 'Ozel:LM66100': return 'lm66100'
    if sem.startswith('Regulator_Switching:TPS62933'): return 'tps62933'
    if sem.startswith('Interface_Ethernet:W5500'): return 'w5500'
    if sem.startswith('Simcom:A7670'): return 'a7670'
    if sem.startswith('Regulator_Linear:AP2112'): return 'ap2112'
    if sem.startswith('Relay:'): return 'role'
    if sem.startswith('Connector:RJ45'): return 'rj45'
    if sem == 'Connector:SIM_Card': return 'simsoket'
    if sem == 'Device:Crystal_GND24': return 'kristal'
    if sem.startswith('Logic_LevelTranslator'): return 'txb0104'
    if sem == 'Connector:TestPoint': return 'testpad'
    return None
