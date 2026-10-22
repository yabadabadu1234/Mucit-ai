from icerik import a_cev
import deger

ID = 'cev33'
BASLIK = '2. 3,3 volt çevirici (12 V → 3,3 V, düşüren)'
OZET = 'Kartın işlemci, telsiz ve Ethernet çipini besleyen 3,3 voltu TPS62933 ile nasıl üretirsin? Bobin, kondansatör ve direnç seçimi, veri sayfası denklemleriyle.'
REFS = ['U5', 'C3', 'C4', 'C5', 'C6', 'L1', 'R2', 'R3', 'C7', 'C8', 'C9']

CFG = dict(
    id=ID, baslik=BASLIK, ozet=OZET, ad='3,3 V çevirici', ic='U5', cin='C3', cin_hf='C4', cbst='C5', css='C6', L='L1', rt='R2', rb='R3',
    cout=['C7', 'C8', 'C9'], sw_net='SW_3V3', out_net='+3V3', fb_net='FB_3V3', ss_net='SS_3V3', sema_genislik=1040,
    bolge_baslik='3,3 V ÇEVİRİCİ  —  TPS62933: 12 V → 3,3 V, 500 kHz', iyuk=0.5, yuk='ESP32-S3 (3,0–3,6 V), RFM95W (1,8–3,7 V), W5500 (≈ 3,3 V)', refs=REFS,
    sema_not='EN ucu boşta (çip kendiliğinden etkin), RT ucu boşta (500 kHz).',
    isaret_ref=['U5', 'L1', 'C3', 'C5', 'C6', 'R2', 'C7'],
    ozel_ogren='Hiç kontrol ucu bağlanmayan (EN, RT boşta) bir çevirici nasıl çalışır?',
    buyuk_resim='Kartın üç ana yükü (işlemci, LoRa modülü, Ethernet çipi) 3,3 V ister; kaynak ise 12 V’tur. Gerilimi 12 V’tan 3,3 V’a indirmenin iki yolu vardır: bir doğrusal düzenleyici (LDO) fazla gerilimi <i>ısıya çevirir</i> (burada (12 − 3,3) × 0,5 A ≈ 4,4 W), düşüren anahtarlamalı çevirici ise aynı enerjiyi bobinde geçici depolayıp aktararak verimi %85–95 mertebesine çıkarır [[bilgi]]. Bu yüzden anahtarlamalı çevirici seçildi: TPS62933, 3,8–30 V giriş, 3 A, entegre iki anahtar, 500 kHz. [[ds]]',
    isaretler=['<b>Çip (U5, TPS62933).</b> Üst ve alt anahtarlar, akım algılama, referans ve iç telafi dahil. VIN 12 V’a bağlı; EN ve RT boş.',
               '<b>Bobin (L1, 4,7 µH).</b> SW ucu ile çıkış arasında; akım dalgalanmasını belirler.',
               '<b>Giriş kondansatörleri (C3: 10 µF, C4: 100 nF).</b> Üst anahtarın darbeli akımını karşılar; 100 nF yüksek frekansı (EMI) süzer.',
               '<b>Bootstrap kondansatörü (C5: 100 nF).</b> BST ile SW arasında; üst anahtarın kapısı için yükseltilmiş gerilim kaynağı.',
               '<b>Yumuşak başlatma (C6: 33 nF).</b> SS ucunun kondansatörü; çıkışın yavaş yükselme süresini belirler.',
               '<b>Geri besleme bölücüsü (R2: 31,6 kΩ, R3: 10 kΩ).</b> Çıkışı çipin 0,8 V’luk referansıyla kıyaslayan dirençler.',
               '<b>Çıkış kondansatörleri (C7, C8: 22 µF; C9: 10 µF).</b> Çıkış dalgalanmasını ve ani yük değişimini yumuşatır.'],
    ihtiyac_satirlari='<tr><td>Giriş</td><td>12 V (en çok 15 V sürekli; TVS 24,4 V’ta kenetler)</td><td>1. bölüm</td></tr><tr><td>Çıkış</td><td>3,3 V</td><td>Yükler</td></tr><tr><td>Yük akımı</td><td>≈ 0,5 A (tasarım payı; çipin gücü 3 A)</td><td>[[tahmin]] ESP32 + LoRa + W5500 + modem mantığı</td></tr><tr><td>Frekans</td><td>500 kHz</td><td>[[ds]] RT boşta</td></tr><tr><td>Yumuşak başlatma</td><td>≈ 5 ms</td><td>[[ds]] tablo 10-1</td></tr>',
    tolerans_yorum=lambda a, b: 'İşlemcinin kabul aralığı 3,0–3,6 V [[ds]]: bu aralığın içinde kalındığı görülür.',
    bobin_yorum=lambda ipk, irms, dI: 'Tepe akım, çipin yüksek taraf akım sınırının (en az 4,2 A) çok altındadır; dolayısıyla bobin, bu yükte rahat çalışır.',
    cout_yorum=lambda cout, tss: 'Toplam anma kapasitesi veri sayfasının önerdiği tipik değerin üzerindedir; marj vardır. [[ds]]',
    uc_satirlari='<tr><td>Çıkış kısa devre</td><td>Çip, tepe ve vadi akım sınırlarıyla korunur; çıkış %65’in altına inerse 256 µs sonra “hıçkırık” moduna girer: 10,5 × t<sub>SS</sub> kadar kapanıp yeniden dener. [[ds]]</td></tr>'
                 '<tr><td>Giriş 3,8 V’un altına iner</td><td>Düşük gerilim kilidi (yükselen 3,6 / düşen 3,3 V) çipi durdurur. [[ds]] Bu kartta giriş 12 V’tur; sorun olmaz.</td></tr>'
                 '<tr><td>Giriş 24 V’a darbe</td><td>TVS 24,4 V’ta kenetler; çip 30 V’a (mutlak 32 V) dayanır. [[ds]]</td></tr>'
                 '<tr><td>Hafif yük</td><td>Çip darbe frekansı modulasyonuna (PFM) geçer: verim yüksek, çıkış dalgalanması biraz büyük, frekans değişken. [[ds]]</td></tr>'
                 '<tr><td>Isı</td><td>Çip 165 °C’ta kapanır, 30 °C histerezisle geri açılır. [[ds]]</td></tr>',
    kaynak_ek='Bobin ve kondansatör parça numaraları (Bourns SRN6028 sınıfı bobin, 22 µF 10 V 1206 seramik) bu çalışmada veri sayfasından doğrulanmadı.',
    kutuplu=[],
)


def uret(ver, ctx):
    return a_cev.bolum_html(ver, CFG)
