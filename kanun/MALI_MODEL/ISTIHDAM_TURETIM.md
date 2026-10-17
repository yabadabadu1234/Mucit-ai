# İSTİHDAM YAPISI: DOLAYLI TÜRETİM VE SINIRLAR (2025)

Doğrudan çapraz tablo (işteki durum × sektör) indirilemedi: TÜİK veri portalındaki indirme bağlantıları bu ortamdan "Erişim engellendi" (403) döndürdü; `tr/statistical-themes` sayfası JavaScript ile yükleniyor, bağlantı listesi yok. Aşağıdaki rakamlar verilen oranlardan ve ikincil kaynaklardan türetilmiştir.

## Girdiler
- E = toplam istihdam = 32,507 milyon (TÜİK Ağustos 2026, kullanıcı verisi; ikincil 2025 yıllık: 32,566 milyon)
- u = ücretsiz aile işçisi oranı = %8,5 (SBB OİK 2025)
- k = kendi hesabına çalışan oranı = %16 (SBB OİK 2025)
- Kadın payı f: u = 0,183·f + 0,040·(1−f) ⇒ **f = (0,085−0,040)/(0,183−0,040) = 0,315**
- Kendi hesabına kontrol: k = 0,197·(1−f) + 0,091·f = **0,164** (verilen %16 ile uyumlu, fark %0,4)
- Tarım T = %14,0 → 4,55 milyon (TÜİK 2025, ikincil); tarım dışı = E − T = 27,96 milyon
- Sektör toplamı: 59,0 + 20,2 + 14,0 + 6,8 = 100,0 ✓

## Türetilen büyüklükler
| Büyüklük | Formül | Değer |
|:--|:--|--:|
| Ücretsiz aile işçisi | u·E | **2,763 milyon** |
| Kadın ücretsiz aile işçisi | 0,183·f·E | 1,88 milyon |
| Erkek ücretsiz aile işçisi | 0,040·(1−f)·E | 0,89 milyon |
| Kendi hesabına (serbest) | k·E | **5,201 milyon** |
| Serbest + ücretsiz aile | (k+u)·E | 7,964 milyon |

## Sınırlar (tarım payı için)
Tarım ve tarım dışı kırılımı doğrudan veri yok; yalnızca sınırlar türetilebilir:
- Ücretsiz aile işçisinin tarımdaki payı: **en fazla 2,763 milyon** (tümü tarımda olsa bile). Tarım dışında ücretsiz aile işçisi: **en az 0**, **en fazla 2,763 milyon**.
- Kendi hesabına çalışanın tarımdaki payı: **en fazla 4,55 milyon**; en az 0.
- Dolayısıyla serbest + ücretsiz aile havuzunun tarım dışı payı **en az 0**, **en fazla 7,96 milyon**. Bu aralık geniş; bu havuz için tarım payı hakkında hüküm çıkmaz.

## Tutarsızlık (işaretlendi)
Ücretli çalışan sayısı: SGK esaslı "16 milyonu geçti" (Ekim 2025, [gzt](https://www.gzt.com/foto-galeri/gundem/tuik-ucretli-calisan-sayisini-acikladi-turkiyede-ucretli-calisan-sayisi-ne-kadar-oldu-ekonomi-haberleri-2047830)). Toplam − ücretli − serbest − ücretsiz aile = 32,5 − 16,0 − 5,2 − 2,8 ≈ **8,5 milyon** açık kalıyor. Bu, işverenler (yaklaşık 1 milyon olduğu bilinen bir büyüklük) için fazla büyük. Olası açıklamalar: kayıt dışı ücretli çalışanın SGK dışında kalması (ücretli toplamı 16 milyondan büyük olur), veya ücretsiz aile ve serbest oranlarının farklı paydaya (örn. yalnızca istihdam edilenin bir alt kümesi) göre verilmesi. Tek başına çözülemez; TÜİK tablosu gerekli.

## Modele etkisi
- Serbest + ücretsiz aile havuzu ≈ 7,96 milyon (KALIBRASYON_ANALOG.md §5 ile tutarlı).
- Tarım payı, havuzu 0 ile 7,96 milyon arasında değiştirir; N kalibrasyonu bu nedenle tarım kırılımına bağlı değildir, sadece havuzun üst sınırı ile ilgilidir.
- Tutarsızlık, "ücretli" havuzunu kullanmadığımız sürece N'yi etkilemez; ancak kayıt dışı ücretli çalışanlar mikro mükellefiyete geçebileceği için (kendi hesabına dönüşüm) asıl risk bu açıklıktadır.

## Gerekli veri
TÜİK HİA 2025 "istihdam edilenlerin işteki duruma ve sektöre göre" çapraz tablosu (ücretli / işveren / kendi hesabına / ücretsiz aile × tarım / sanayi / inşaat / hizmet). Dosya indirilip `kanun/MALI_MODEL/veri/` altına konursa bu dosya o rakamlarla güncellenir.
