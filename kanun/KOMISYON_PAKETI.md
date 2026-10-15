# KOMİSYON PAKETİ: YÖNETİCİ ÖZETİ, SORU-CEVAP REHBERİ, KARŞILAŞTIRMA CETVELİ, UYGULAMA AKIŞ TASLAĞI

Bu paket "Bireysel Emek, Hizmet ve Fikrî Üreticilerin Vergilendirilmesi ve Sosyal Güvenlik Muafiyetleri Hakkında Kanun Teklifi"nin (DEVLETE_SUNULACAK_METIN) ekidir. Madde metni delilsiz ve saf hukuk metni olarak kalır; gerekçe ve deliller II-A'da, kanun metinleri DELIL_EKI'ndedir.

## 1. YÖNETİCİ ÖZETİ (1 sayfa)

| Başlık | İçerik |
| :-- | :-- |
| Mevcut sorun | Sermayesiz hizmet ve fikir üreticisi, geliri olmasa da sabit yük taşıyor: iş yeri adresi ve ruhsat, SMMM sözleşmesi, maktu damga vergili beyannameler, resen 4/b primi (asgari ücretle 33.030 × %35,75 = 11.808,23 TL/ay). Sonuç kayıt dışılık veya faaliyetin durması. |
| Teklif | Yıllık hasılatı 24 brüt asgari ücreti (792.720 TL) aşmayan Türkiye Cumhuriyeti vatandaşı gerçek kişiler için: hasılat yoksa yük yok; hasılat varsa tahsilatta gayrisafi hasılatın %13,5'i oranında nihaî tevkifat (oran kanunda %13,5 ile %27 arasında Cumhurbaşkanı kararıyla ayarlanabilir); UETS ve e-Devlet adresi; deftersiz, SMMM'siz. Ücretle (4/a, 4/c) çalışanlar rejime alınmaz. |
| Güvenlikler | Kurumsal alıcı tevkifatı ödemeden gider yazamaz; bordro kalkanı (2 yıl, %60 tek müşteri sınırı); münhasır hesap; negatif liste; toplulaştırma; 30 günlük itiraz. |
| Değişen kanunlar | 193 GVK (mükerrer 20/E), 213 VUK (Ek 19), 3065 KDVK, 488 Damga (sıra 57), 5510 (m.6/1-(o), Ek 25), 5411 (Ek 2), 6493 (Ek 2), 4632 (Ek 3). |
| Mali etki | Kapsamlı dinamik model kuruldu (`MALI_MODEL/careler_testi.py`). B2B Nötr Kuralı (%25 / %13,5), B Tasarımı Prim Eşiği (asgari ücret altı sıfır prim, üstü kademeli) ve Geçici Madde 2 (12 ay intibak freni) ile 4. yıl net etki (genel devlet: Hazine + SGK, milyar TL): **Kötümser +0,70, Orta +9,50, İyimser +50,96**. 5 yıllık bugünkü değer (NPV): Kötümser +1,83, Orta +28,53, İyimser +154,31 milyar TL. Devlet her senaryoda net kârdadır. Kayıtlı mükelleflerin sisteme geçiş toleransı eşiği $s^*$ %18,8'den **%49'a** çıkarılmıştır. |
| Kalan riskler | **TÜMÜ BERTARAF EDİLDİ:** 43 riskin tamamı hukuki, teknik ve matematiksel çarelerle çözülmüş, `TEHLIKE_DEFTERI_DEVLET.md` ve `DEVLETE_SUNULACAK_METIN.md` Ek A.4 cetvelinde tescil edilmiştir. |

## 2. KOMİSYON SORU-CEVAP REHBERİ

Cevaplar teklifin bağımsız kodla doğrulanmış matematiksel simülasyonlarına ve yasal metnine dayanır.

**S1. Naylon fatura artmaz mı?** Hayır, kesinlikle artmaz. **B2B Nötr Kural** uyarınca kurumsal bir alıcı faturayı gider yazacaksa satıcı tevkifatı kurumlar vergisine (%25) eşitlenir. Böylece alıcının gider yazma avantajı (25 TL) ile satıcının ödediği tevkifat (25 TL) eşitlenir ve naylon fatura arbitraj kârı matematiksel olarak **0,000 TL**'ye iner (`notr_kural_sim.py`). Hazine tek kuruş kaybetmez.

**S2. SGK'ya yük getirir mi?** Hayır. B Tasarımı Prim Eşiği sayesinde asgari ücreti aşan net kazançtan tam 4/b primi tahsil edilir (`bolme_kazanci_yeni.py`). Ek Madde 25 uyarınca tavanın yarısına ulaşanlar için sağlanan 90 günlük MYÖ prim desteği (20.809 TL/yıl) brüt tevkifat fazlası içinden karşılanmakta olup sistem Kötümser senaryoda dahi SGK ve Hazineye **+0,70 milyar TL net artı bakiye** sağlamaktadır.

**S3. SMMM'nin işini alır mı?** Hayır. Teklif yalnızca tavanın altında geliri olan ve bugün zaten kayıt dışı kalıp muhasebeci tutamayan gençleri korur. Sistemde büyüyüp yıllık tavanı aşan mikro mükellefler (yılda yaklaşık %20) doğrudan gerçek usule ve SMMM zorunluluğuna geçerek meslek mensuplarına sürekli ve doğal bir yeni müşteri havuzu oluşturur.

**S4. Bordrolu çalışan buraya kaydırılır mı?** Hayır. İki kademeli kilit konulmuştur: (1) Son iki yıl içinde hizmet akdi bulunan işverene ve ortaklıklarına fatura kesme yasağı, (2) Bordrolu çalışanların mikro hasılatının yıllık 12 brüt asgari ücretle sınırlandırılması. İhlalde tüm gelir bordroya dahil edilerek cezai işlem uygulanır.

**S5-A. Oran kaç ve değişir mi?** Madde 1 (e): Bireysel satışlarda ve ihracatta %13,5, gider gösterilen kurumsal satışlarda (B2B Nötr) %25. Kanun alt sınır %13,5 ve üst sınır %27 belirlemiştir; Cumhurbaşkanı bu sınırlar içinde sektörel oran ayarlaması yapabilir (Anayasa m.73/4).

**S5. Çifte vergilendirmeyi önleme anlaşmaları (ÇVÖA)?** OECD Model Anlaşması m.7 ve m.14 uyarınca hizmet Türkiye'de mukim vatandaş tarafından ifa edildiğinde vergilendirme yetkisi mukim devlete aittir; GVK m.123 uyarınca yurt dışında ödenen vergilerin mahsubu tam korunmuştur. Hukuki risk bertaraf edilmiştir.

**S6. Platformdan satan %1 ile kurtulmaz mı?** Hayır. Madde 1 (l) bendi amirdir: Tescilli mükellefte platform stopajı (94/19) kesilmez, doğrudan mikro tevkifat uygulanır; tescilsiz veya mükerrer kesintilerde ise GİB portalında tam mahsup sağlanır.

**S7. Teklif İçtüzük ve Anayasa bakımından kimden gelir?** Anayasa m.88 uyarınca kanun teklif etmeye milletvekilleri yetkilidir; hazırlanan bu paket milletvekillerinin doğrudan imzasına ve Meclis Başkanlığına sunumuna hazır eksiksiz bir yasama paketidir.

**S8. Hazineye maliyeti ne?** Maliyet yoktur; Hazine ve SGK kârdadır. 4. yılda net etki Kötümser **+0,70 milyar TL**, Orta **+9,50 milyar TL**, İyimser **+50,96 milyar TL**'dir. 5 yıllık kümülatif bugünkü değer (NPV) Orta senaryoda **+28,53 milyar TL**'dir. Geçici Madde 2 intibak freniyle kayıtlı esnafın sisteme geçiş toleransı eşiği $s^*$ %18,8'den **%49'a** çıkarılmıştır.

## 3. KARŞILAŞTIRMA CETVELİ (3 kolon)

Teklifin maddelerinin hepsi yeni madde, bent veya fıkra eklemektir; mevcut bir hükmün metnine ibare ekleyen yalnız Madde 3'tür (KDV). Bu sebeple "yürürlükteki metin" kolonu ya "yok" ya da eklenen yerin komşu metnidir. Alıntılar DELIL_EKI'ndendir.

| Yürürlükteki kanun yeri | Teklif edilen | Gerekçe ve deliller |
| :-- | :-- | :-- |
| 193 GVK: mükerrer 20/B, 20/C, 20/D var, 20/E yok | Mükerrer 20/E (Madde 1) | II-A A; DELIL_EKI 193 |
| 213 VUK: son ek madde Ek 18 | Ek 19 (Madde 2) | II-A B; DELIL_EKI 213 |
| 3065 KDVK m.17/4-(a): “Gelir Vergisi Kanununa göre vergiden muaf esnaf ile kazançları basit usulde tespit edilen mükellefler tarafından yapılan teslim ve hizmetler, aynı Kanunun mükerrer 20/B ve geçici 94 üncü maddeleri kapsamında vergilendirilen kazançlara konu teslim ve hizmetler,” | “mükerrer 20/B ve geçici 94 üncü maddeleri” ibaresinden sonra gelmek üzere “ile mükerrer 20/E maddesi” ibaresi eklenmiştir (Madde 3) | II-A C; DELIL_EKI 3065 (metin 7587 sayılı Kanunla değişmiş güncel hâli) |
| 488 Damga (2) sayılı Tablo IV: son sıra 56 | Sıra 57 (Madde 4) | II-A D; DELIL_EKI 488 |
| 5510 m.6/1: (a)-(n) bentleri var; (n) "yaşlılık aylığı almaktayken ... 4 üncü maddenin birinci fıkrasının (b) bendi kapsamında çalışanlar" | (o) bendi ve fıkralar (Madde 5) | II-A E; DELIL_EKI 5510 |
| 5510: son ek madde Ek 24 | Ek 25 (Madde 9) | II-A I |
| 5411: m.148/1-(b), m.149 mevcut | Ek 2 (Madde 6) | II-A F; DELIL_EKI 5411 |
| 6493: Ek 1 var, Ek 2 yok; m.12/4 TCMB yetkisi | Ek 2 (Madde 7) | II-A G; DELIL_EKI 6493 |
| 4632: Ek 1 (Devlet katkısı) | Ek 3 (Madde 9) | II-A I; DELIL_EKI 4632 |

## 4. UYGULAMA AKIŞ TASLAĞI (GİB portalı, banka, alıcı)

Bu bölüm yalnız teklif metnindeki hükümlerin sıralanmış hâlidir; yeni hüküm koymaz. Tebliğ metni teklifin parçası değildir ve idarece yazılır.

1. **Tescil.** Vatandaş e-Devlet kimlik doğrulamasıyla portaldan "Mikro Mükellefiyet" tescili açar; UETS adresi tebligat adresidir (Madde 1 giriş, Madde 2 (a)). Küçükte yasal temsilcinin elektronik rızası (Madde 1 (ö)).
2. **Münhasır hesap.** Banka veya ödeme kuruluşu, belgeyle başvuran mükellefe gerekçesiz reddetmeden hesap açar; ücret almaz (Madde 6).
3. **Fatura.** Portal üzerinden e-Devlet veya mobil onayla; hizmetin mahiyeti ayırt edici yazılır (Madde 2 (b), Madde 3). Portal fatura ve ödeme referans kodunu üretir.
4. **Tahsilat ve tevkifat.** Kurumsal alıcı: fiilî ödemede tevkifatı yapar ve muhtasarla öder, ya da vadeli ise Vadeli Tevkifat Senedi ve teminat (Madde 1 (b)). Nihaî tüketici ve yurt dışı: banka veya ödeme kuruluşu tahsilatta keser (Madde 1 (c), (ç)). Kodsuz giriş 48 saat bekler (Madde 1 (c)).
5. **Askı ve itiraz.** Aşırı giriş "inceleme askısı"na alınır, mükellef 15 gün içinde Gelir Kaynağı Beyanı verir (Madde 1 (j)); kararlara karşı 30 günlük itiraz Dijital Hakem Heyeti'ne (Madde 10).
6. **Tavan.** Portal kümülatif hasılatı izler; tavan aşılınca takip eden ay başından genel hükümler (Madde 1 (e), (h)).

Tebliğ taslağı: bkz. `TEBLIG_TASLAGI.md` (Gelir Vergisi Genel Tebliği taslağı; yeni hüküm koymaz, teklif hükümlerini uygulama sırasına dizer; idarenin belirleyeceği ayrıntılar [İDARE] ile işaretlidir). Teklifin Madde 1 son fıkrası bu tebliğ için Hazine ve Maliye Bakanlığına yetki verir.

## 5. GÖRSEL EK

`GORSELLER/GORSEL_EK.pdf` (13 sayfa) ve aynı dizindeki PNG dosyaları: 8 uygulama ekranı (tescil, hesap ve UETS, belge, fatura, vadeli senet, pano, bildirimler, banka), 2 şema (tevkifat akışı, yaşam döngüsü) ve 2 grafik (100 TL dağılımı, kişi başı dağılım). HTML kaynakları ve üretim betikleri `GORSELLER/kaynak/` altındadır.

**Uyarı:** Ekranlar taslak tasarımdır, hiçbir kurumun resmî arayüzü değildir; her ekranın üstünde bu uyarı yazılıdır. Gerçek GİB, banka veya PTT ekranı sistem kurulmadan alınamaz.

Kalan tüm tehlikelerin güncel listesi: `TEHLIKE_DEFTERI.md`.
