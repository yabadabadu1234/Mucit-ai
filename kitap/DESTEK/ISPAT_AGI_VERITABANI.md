# İSPAT AĞI VERİTABANI (3-I 237, 238)

**Padişahın sözü (yalnız bu kadar, 3-I 237):** veritabanını oluşturmaya başla; Allah hakkında ispatlanacaklar (Vâcib bir varlığın olup olamayacağı, kesin olup olmadığı, sayısı, zâtî sıfatları, neden zorunlu olduğu, her birinin olmaması hâlinde olacaklar, ispatlar yapılınca çürüyen ve çürümeyen felsefeler); çürümeyen felsefe bırakmayacak şekilde suâl ve ihtimaller genişletilecek; önce ispat usulleri öğretilecek, sonra listedeki teçhizatın kullanıldığı gösterilecek, her ispatta azamî kombinasyon yapılacak, hiçbir teçhizat seçilip bırakılmayacak, her kombinasyon veritabanında net görünecek.

**Padişahın teyidi (3-I 238):** teçhizat = Kısım I usul listesi (U01–U32; U33–U35 kabul edilmemiş adaylardır, matrise girmez) · "olmaması hâlinde olacaklar" üç okumadır ve üçü de kabul: hücre doğru olmasaydı çıkacak imkânsız sonuç, **hiç var olmasaydı**, ispatlananlardan herhangi birinin aksi (bütün münhasır ihtimaller) doğru olsaydı · azamî kombinasyon = A-B ile de, C-D ile de, B-C ve A-D ile de ispat: **kaç yoldan ispat oluyorsa hepsi görünür**; yalnız veritabanı içindir, kitaba sığmaz.

**Claude çıkarımı (padişahın sözü değil):** "yol" iki ölçüyle sayılır: (1) bir hücrenin kullandığı usullerin alt kümeleri, (2) dayanılan hücrelerin ispatları üzerinden **türetme ağacı** (her ispat, öncülü olan hücrenin her ispatıyla ayrı ayrı sayılır).

## Dosyalar (`kitap/ISPAT_AGI/`)

| Dosya | İş |
| :-- | :-- |
| `veri_usul.py` | 35 usul kaydı: tanım, nasıl yapılır, şart, hudut, safsata, katiyet tavanı, misal |
| `veri_onerme.py` | 101 önerme (evveliyyât, müşâhede, tanım, mantık, türetilmiş); zayıf halkalar `zayif` ve `aile` ile işaretli |
| `veri_soru.py` | 33 suâl (Q18 zemin, Q00 sebep ilkesi, Q01–Q09, Q11–Q17, 15 sıfat suâli Q10.*), 109 hücre, 42 felsefe, 25 "olmasaydı" kaydı, **sıfat tasnifi** (6 zâtî, 8 sübûtî, 4 fiilî) |
| `veri_ispat.py` | Elle yazılmış 173 doğrudan ispat kaydı (hücre, usul, öncül listesi, özet) |
| `kural.py` | Bir usulün bir hücrede **neden yapılamayacağını** söyleyen kurallar |
| `motor.py` | Katmanlı hesap, türetilmiş ispatlar, kombinasyon, matris, felsefe durumu |
| `insa.py` | Kontroller, SQLite, JSON, HTML üretimi |
| `sablon.html` | HTML şablonu |
| `harita.js` | HTML’deki ağ haritası (canvas, pan ve zoom, görünen kısmı çizer) |
| `ispat_agi.sqlite` · `ispat_agi.json` · `ispat_agi.html` | Üretilen veritabanı ve sunum (kitaba link); elle yazılmaz, `insa.py` üretir |

Yeniden kurmak: `python3 insa.py` (kontroller kırmızıysa çıktıda KIRMIZI görünür).

## Hesap kaideleri

1. **Öncül türleri:** `önerme` (kimlikle), `H:hücre` (o hücrenin hükmü, herhangi bir ispatla ayakta), `D:hücre` (yalnız doğrudan ispatlarla), `P:ispat` (belirli bir ispat).
2. **Katiyet** = ispatın usul tavanı, öncüllerinin katiyeti ve dayandığı hücrelerin katiyetinin en küçüğü (zincir kaidesi, I.3.5.5). Yakîn öncül zayıf halka taşıyorsa ispat **KAT'Î-ŞARTLI**dır ve şart yazılır.
3. **Katmanlı zemin:** bir ispat ancak dayandığı hücrelerde kendinden önceki katmanda ispat varsa atanır. Böylece kendi kendini destekleyen (çemberli) ispat atanamaz. Atanamayan ispat sayısı kontrolde yazılır (bu sürümde 0).
4. **Türetilen ispatlar (usul U08 ve mirasçıları):**
   - *sibr:* doğru hücre, kardeş bütün hücrelerin doğrudan çürütmelerinden türer; suâlde İHTİLAFLI hücre varsa türemez (kitap o hücreyi iddia etmez); istikrâî hasırlı suâlde katiyet zanla sınırlanır.
   - *dışlama:* doğru kardeşin her doğrudan ispatı, yanlış hücreye aynı usulle bir çürütme olarak yazılır (kardeş ispatı P: ile bağlanır; tenbih sayılmaz).
   - *alt suâl:* Q02.c2 ("hiçbir vâcib yoktur") Q03'ün beş hücresinin ayrı ayrı çürütülmesinden çürür.
5. **Kısmî ispat:** yalnız bir alt durumu kapsayan ispat `kısmî` işaretlenir; hücrenin hükmünü taşımaz, başka ispata dayanak olmaz, kombinasyonda ayrıca sayılır (4 kayıt).
6. **Tenbih** (U32) delil değildir: katiyeti sıfır, dayanak olamaz, dışlamayla yayılmaz.
7. **Kombinasyon:** bir hücrenin kullandığı usullerin her alt kümesi için: en yüksek katiyet, zayıf halka yok mu, **ortak zayıf halka** (en yüksek katiyetteki bütün ispatların ortak ailesi), kısmî sayısı. `yeterli` = hücrenin ulaşabildiği en iyi hâle çıkaran küme; `asgarî` = hiçbir alt kümesi yeterli olmayan; `azamî` = bütün usuller.
8. **Matris durumları (hücre × usul):** `KULLANILDI` · `KOMBİNE` (U16) · `HUDUT` (U30: zayıf halka veya kısmî kapsam var) · `ÖNCÜL` (U12, U13 yalnız öncül sağladı) · `YAPILAMAZ` (kuralla, sebebiyle) · `YAPILMADI` (usulün şartı mümkün, kayıt henüz yazılmadı: **açık iş**) · `SINIFLANMADI` (U19–U25: ispat Fârâbî sınıfına etiketlenmedi) · `AÇIK` (hasır kardeşlerden biri bağsız).
9. **Felsefe durumu** elle yazılmaz: felsefenin iddia ettiği yanlış hücrelerden en güçlü çürütmenin katiyetinden okunur. Hiçbiri çürütülmemişse `ÇÜRÜMEDİ`; yalnız İHTİLAFLI hücre tutuyorsa `İHTİLAFLI (iddia edilmez)`; doğru cevapla uyumluysa `UYUMLU`.
10. **Zayıf halka düşerse (ne_olur):** her zayıf aile ve öncül için ağ yeniden hesaplanır; düşen hücreler ve durumu değişen felsefeler yazılır.

## Sayılar

| Ölçü | Değer |
| :-- | :-- |
| Suâl · hücre · önerme · usul (kabul edilmiş) · felsefe | 33 · 109 · 101 · 32 · 42 |
| İspat kaydı (doğrudan · sibr · dışlama · alt suâl) | 173 · 25 · 154 · 1 = 353 |
| Hücre durumu | KAT'Î 37 · KAT'Î-ŞARTLI 47 · ZAN-I GÂLİB 19 · İHTİLAFLI 6 (ispatsız DOĞRU/YANLIŞ hücre yok) |
| Matris (3488 satır) | YAPILAMAZ 1969 · KULLANILDI 317 · YAPILMADI 575 · SINIFLANMADI 429 · KOMBİNE 88 · HUDUT 66 · ÖNCÜL 37 · AÇIK 7 |
| Kombinasyon satırı (usul alt kümesi) | 1321 |
| Türetme ağacı sayısı | hücre başına 0 ile 274 arası (en çok Q02.c2: 274, Q02.c1: 273, Q17.c1: 270) |
| “Olmasaydı” satırı | 147: hücre doğru olmasaydı 25 · hiç var olmasaydı 20 · aksi doğru olsaydı 102 |
| Felsefe | ÇÜRÜTÜLDÜ kat'î 23 · kat'î fakat şartlı 14 · zannî 3 · İHTİLAFLI 1 · UYUMLU 1 · **koşulsuz ÇÜRÜMEDİ 0** |

## Sıfat tasnifi (padişahın sorusu, 3-I 238)

Padişahın saydığı altı zâtî sıfat (vücûd, kıdem, bekâ, vahdâniyyet, kıyâm bi-nefsihî, muhâlefetün li'l-havâdis) tasnifin birinci sınıfıdır. Sübûtî sıfatlar Mâtürîdî sayımında **sekizdir** (hayat, ilim, semi', basar, kudret, irade, kelâm, tekvîn); Eş'arî sayımında tekvîn kudret ve iradeye döndüğü için yedidir. Padişahın altı sübûtî sayımında semi' ve basar yoktu. Hikmet, adâlet, rahmet ve sıdk **fiil sıfatları**dır ve sübûtî sayıya girmez; veritabanı bu dördünü kitabın V.2.4 ve V.5 köprüsü için açmıştır. Veritabanındaki "15 sıfat suâli" sıfat sayısı değil suâl sayısıdır: üç zâtî (kıdem, bekâ, gınâ) + sekiz sübûtî + dört fiilî; vücûd, vahdâniyyet ve muhâlefet ayrı suâllerde durur (Q02, Q04+Q05, Q06–Q08). Sayımlar ve mezhep notları (Senûsî yirmi sayımı, Mu'tezile, Cehmiyye, Selefiyye) **hafızadandır, yoklanmadı**; HTML'de "Sıfat tasnifi" sekmesi ve kitapta `V.2.5` yaprakları bunu gösterir.

## Dürüstlük notları (F 2-A 32, 5)

1. **Bütün ispatlar taslaktır ve hafızadandır.** Kaynak yoklanmadı (3-I 230); her önermenin kaynağı okunmadan "kat'î" yazılan şey yalnız **iç tutarlılık** bakımındandır, kitabın nihaî hükmü değildir.
2. **"Kat'î-şartlı" kat'î değildir.** Vâcib'in varlığı (Q02.c1) dâhil **bütün** ispat yolları en az **sebep-ilkesi** ailesine (üç kanat: varlık, hâl, bilgi; tercihsiz tercih, hâdisin muhdisi) dayanır; Q02.c1'in hiçbir alt kümesi bu aileden bağımsız değildir (kombinasyon tablosunda "ortak zayıf halka: sebep-ilkesi"). Bu ilkeyi kabul etmeyen muhatap için ağ şunu verir: Q02.c1 düşer; **F01 (katı ateizm) ÇÜRÜMEDİ olur**, F02 ve F08 zanna iner, diğer yedi felsefe (F23, F25, F26, F29, F30, F31, F32) zan-ı gâlibe iner (Zayıf halkalar sayfası).
3. **Çürümeyen felsefe bırakmama hedefi bu sürümde koşulludur.** Listelenen 42 felsefeden koşulsuz `ÇÜRÜMEDİ` olan yoktur (hepsi en az bir yanlış hücreye bağlıdır ve o hücre bir ispatla çürütülmüştür); fakat bu, yukarıdaki zayıf halkalar kabul edilmeden doğru değildir. Ayrıca felsefe listesi **istikrâîdir** (sayarak kurulmuştur): hücreler aklî hasırla kapalıdır, yeni bir felsefe mevcut hücrelerden birine düşer, ama bu düşüşü her yeni felsefe için ayrıca yoklamak lâzımdır.
4. **Kısmî çürütmeler:** Q09.c2 (zorunlu sudûr) ve Q16.c1 (tesadüf) için gerçek, tam kapsamlı bir ispat yazılmadı; Q09.c2 yalnız Q13.c1'e (âlemin hudûsu, zayıf halkalı) ve Q09.c4'ün ispatına bağlanarak çürür; Q16.c1 yalnız zan-ı gâlib düzeyindedir. Sudûrcu felsefecilerin akıllar silsilesi cevabı yoklanmadı.
5. **İHTİLAFLI hücreler (6 çıplak, +1 ispatlı):** Q05.c4, Q13.c3 ve dört sıfat (semi', basar, kelâm, tekvîn) hücresi kelâm içi ihtilaflıdır; hikmet hücresi de ihtilaflı işaretlidir fakat zan-ı gâlib düzeyinde bir ispat kaydı vardır; kitap onları ne iddia eder ne çürütür; veritabanı onlara doğru hükmü vermez (I9). F33 (Mu'tezile) bu yüzden `İHTİLAFLI`.
6. **Açık iş:** 583 hücre × usul çifti `YAPILMADI`dır (usulün şartı mümkün, kayıt yazılmamış); çoğu U03, U28, U17, U01 (isbat usulleri) ve U02, U09, U27, U29'un 15 sıfat hücresindeki karşılıklarıdır. Bunlar **sayılır ve gizlenmez**, ispat kaydı yazıldıkça düşer. Ayrıca 429 `SINIFLANMADI` hücre–Fârâbî sınıfı çifti vardır (ispatlar enne/lime ve dört sebep sınıflarına yalnız bir kısmında etiketli).
7. **`YAPILAMAZ` kuralları Claude'un hükmüdür** (özellikle U26 ilzam ve U27/U29 için "kayıtlı felsefe yok"); `kural.py`de yazılıdır, yoklanabilir.
8. **Felsefe eşlemeleri yaklaşıktır:** F05, F16, F17, F30, F31 (Budizm, Teslis, Spinoza/Advaita, Vedânta, Tao) kendi kaynaklarından okunmadan eşlenmiştir; hücrelerdeki not "kaynak okunmadan ilzam yazılmaz" der.
9. **İkinci bir motor yoktur:** türetmeler yalnız `motor.py`dedir (F 2-B 42 ruhu); veri dosyalarında hesap yoktur.
10. **Python betikleri bu depoda `kitap/` altındadır ve tahtın (F 1-L) parçası değildir;** veritabanını kurmak için `python3 insa.py` koşturulmuştur.

## Ölçü sağlığı (F 3-B 27-B)

`insa.py` her kuruluşta şunları sayar ve hepsi tamam çıkmıştır: bulunamayan kimlik 0 · zemine bağlanamayan ispat 0 · `kapsam_cerhi` atfı eksik hücre 0 · ispatsız veya yalnız kısmî DOĞRU/YANLIŞ hücre 0 · İHTİLAFLI hücreye hasırla doğru hükmü 0 · matris satırı 3488 = 109 × 32 · kombinasyon 1111 = Σ(2ⁿ−1). **Ayırt testi:** bir zayıf aile kaldırıldığında bağlı hücrelerin durumu fiilen düşer (sebep-ilkesi ailesinin bütünü 28 hücre (üç kanada ayrılınca: hâl 18, varlık 0 çünkü varlık ve hâl kanadı birbirinden bağımsız yollar taşır, ikisi birden 26; ayrıntı DESTEK/SEBEP_ILKESI_ARASTIRMA.md), kemâl 14, ibadet tanımı 4, terkip 1); etkisiz çıkan aileler (ihkam, özdeşlik, zaman, zât–vücûd, zorunluluk de dicto, sebep-ilkesi-varlik ve Pruss ispatının iki ailesi sebepsiz-sans ve apriori-ret) başka ispatlarla ayaktadır ve bu da sayılıdır.

## Padişaha sorulacak tetabuk (3-A 13)

Fihrist S35'tedir.


## Harita (HTML, 3-I 238)

Harita bir **canvas**tır; dünya alanı yaklaşık 18 000 × 12 800 birimdir. Her karede yalnız görünen alan çizilir: düğümler 400 birimlik ızgaradan sorgulanır, kenarlar yalnız görünen ispat düğümlerinden çıkar ve ekran uzunluğunun %90'ını aşanlar (varsayılan modda) çizilmez. Yakınlaştıkça kıta → hücre → ispat → öncül metni açılır. Bir düğüme tıklanınca **odak** açılır: dayanakları mavi, türevleri turuncu oklarla gösterilir (derinlik 1, 2, 3 veya hepsi), gerisi söner. Ağ düzeni: solda öncül kıtası (tür sütunları), sağda her suâl bir kıta, kıtada hücre kareleri, altında ispat daireleri (renk = usul grubu, kesik çizgi = türetilmiş, ortası boş = kısmî). Hücre sayfasında "kaç yoldan ispat oluyor" ve "olmaması hâlinde olacaklar" kutuları ağ haritasına bağlanır.

## Düzeltme kaydı (G11)

`k_sebep_istemez` öncülünün eski metni "her mümkin sebep ister" yönünü yakîn öncül olarak gizlice taşıyordu ve 15 sıfat hücresinin çürütmesi buna dayanıyordu; bu sürümde yalnız Vâcib için bırakıldı, mümkin yönü zayıf işaretli `k_tercihsiz_hal` olarak açıkça eklendi. Hücre durumu KAT'Î 49 → 37, KAT'Î-ŞARTLI 33 → 45. Bu sürümden önce yazılan yukarıdaki "Dürüstlük notları" sayıları (28 hücre, 14 kemâl vb.) o tarihe aittir; güncel ölçüm `ispat_agi.json` içindedir. Ayrıntı: `PRUSS_G11_EZELI_MUMKIN.md`.

## Düzeltme kaydı (3-I 240)

Nizam delili (`U17`, `U25`) yalnız ilimli ve iradeli bir fâile işaret eder; hücre metni "Vâcib" dediği hâlde fâil–Vâcib köprüsü yazılı değildi. `k_fail_vacib` açıkça eklendi (8 ispat, varlık ilkesi ailesine). İlke farz edildiğinde sayılar değişmedi; ilkesiz harita `ISPAT_YONU_ALTERNATIFLERI.md`dedir.

## Düzeltme kaydı (3-I 242: Mâtürîdî okumasından türetilen kayıtlar)

"1 okuyup 10 yeni üret" hükmüyle Arş (V.2.16), tevhid (V.2.6), ihtiyar (V.2.14) ve adlandırma farkı (V.1.3.M.144) okumalarından **11 yeni önerme** ve **10 yeni doğrudan ispat** eklendi (`veri_onerme.py` ve `veri_ispat.py` sonunda "3-I 242" başlığıyla). Yeni ispatlar: **Q07.c3** (mekânlı Vâcib) için dört kayıt: ezelden mi sonradan mı ikilemi (U07), sınırlı ⇒ mümkin ⇒ Vâcib değil (U07, imkân–vücûb çekirdeğine indirgenmiş), kuşatma üçlüsü (U07, **kısmî**: eşitlik şıkkı kayıtlı değil), el kaldırma yön delilinin ters çevrilmesi (U29, **kısmî**: yalnız yön delilini kapsar; ilk sürümde kısmî işaretlenmeyip hücreyi tek başına ispatlıyor göründüğü için düzeltildi); **Q13.c2** için adlandırma farkı ilzamı (U27); **Q09.c2** için sudûr itirazı (U07, **kısmî**); **Q10.irade.c1** için çeşitlilik ve tabiatla iş yapanın tek türlülüğü (U17); **Q04.c2** için gizleme (bilgi) argümanı (U07).

**Sayılar:** ispat 343 → 353; önerme 90 → 101; hücre durumu KAT'Î-ŞARTLI 45 → 47, ZAN-I GÂLİB 21 → 19 (Q07.c3 ve Q07.c2 zan-ı gâlibden kat'î-şartlıya çıktı; şart `k_sinirli_mumkin`, yani sebep-ilkesi hâl kanadı); kombinasyon 1287 → 1321; açık iş (`YAPILMADI`) 580 → 575. Matris, kombinasyon ve kimlik kontrolleri tamam çıktı.

**Yeni zayıf aileler (adıyla):** `alem-parca` (âlem hâdisse her parçası hâdistir), `mekan-degisim` (mekâna girmek hâl değişimidir; Mâtürîdî Kâ'bî'ye karşı bunu zâtta zorunlu görmez, V.2.16.68), `sudur-cesitlilik` (tek özellikli illetten çeşitli sonuç çıkmaz; alıcı farkı itirazı açık), `gizleme-gucu` (gizleme gücü kemâldir; hasım mantıkî imkânsızı yapamamanın eksiklik olmadığını söyler), ve `mekan` ailesine eklenen `k_kusatma_muhtac`. **Bu beş zayıf ailenin hiçbiri hücre durumunu düşürmez** (ayırt testinin "etkisiz" sayısı 17 → 22); bu, ağın başka ispatlarla ayakta olduğunu gösterir ve ölçünün bu aileler için ayırt etmediği anlamına gelir; sayı gizlenmedi.

**Okuma notu:** Önceki "açık iş" notu ("sudûr itirazı veritabanında yok") kısmen yanlıştı: Q09.c2'de zorunlu sudûrun tek değişmez sonuç vermesine dair ispat zaten vardı; yeni kayıt "çeşitli ve zıt özellikli sonuç" kanadını ayrı ve **kısmî** olarak ekler. **DB'de hücresi olmayan** Mâtürîdî malzemesi (hâdis mükevven ve "neden sonradan" ikilemi, V.2.11.5–7) bir itiraz–cevap zinciridir ve ayrı hücre açılmadan yazılmadı; açık iştir.
