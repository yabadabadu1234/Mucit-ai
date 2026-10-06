# İSPAT AĞI VERİTABANI -- İLK SÜRÜM (3-I 237)

**Padişahın sözü (yalnız bu kadar, 3-I 237):** veritabanını oluşturmaya başla; Allah hakkında ispatlanacaklar (Vâcib bir varlığın olup olamayacağı, kesin olup olmadığı, sayısı, zâtî sıfatları, neden zorunlu olduğu, her birinin olmaması hâlinde olacaklar, ispatlar yapılınca çürüyen ve çürümeyen felsefeler); çürümeyen felsefe bırakmayacak şekilde suâl ve ihtimaller genişletilecek; önce ispat usulleri öğretilecek, sonra listedeki teçhizatın kullanıldığı gösterilecek, her ispatta azamî kombinasyon yapılacak, hiçbir teçhizat seçilip bırakılmayacak, her kombinasyon veritabanında net görünecek.

**Claude çıkarımları (padişahın sözü değil):** teçhizat = Kısım I usul listesi (U01–U32; U33–U35 kabul edilmemiş adaylardır, matrise girmez) · azamî kombinasyon = bir hücrede kullanılan usullerin bütün boş olmayan alt kümeleri · "olmaması hâlinde olacaklar" = hücre doğru olmasaydı çıkacak imkânsız sonuç.

## Dosyalar (`kitap/ISPAT_AGI/`)

| Dosya | İş |
| :-- | :-- |
| `veri_usul.py` | 35 usul kaydı: tanım, nasıl yapılır, şart, hudut, safsata, katiyet tavanı, misal |
| `veri_onerme.py` | 68 önerme (evveliyyât, müşâhede, tanım, mantık, türetilmiş); zayıf halkalar `zayif` ve `aile` ile işaretli |
| `veri_soru.py` | 33 suâl (Q18 zemin, Q00 sebep ilkesi, Q01–Q09, Q11–Q17, 15 sıfat suâli Q10.*), 109 hücre, 42 felsefe, 25 "olmasaydı" kaydı |
| `veri_ispat.py` | Elle yazılmış 159 doğrudan ispat kaydı (hücre, usul, öncül listesi, özet) |
| `kural.py` | Bir usulün bir hücrede **neden yapılamayacağını** söyleyen kurallar |
| `motor.py` | Katmanlı hesap, türetilmiş ispatlar, kombinasyon, matris, felsefe durumu |
| `insa.py` | Kontroller, SQLite, JSON, HTML üretimi |
| `sablon.html` | HTML şablonu |
| `ispat_agi.sqlite` · `ispat_agi.json` · `ispat_agi.html` | Üretilen veritabanı ve sunum (kitaba link) |

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

## Sayılar (ilk sürüm)

| Ölçü | Değer |
| :-- | :-- |
| Suâl · hücre · önerme · usul (kabul edilmiş) · felsefe | 33 · 109 · 68 · 32 · 42 |
| İspat kaydı (doğrudan · sibr · dışlama · alt suâl) | 159 · 22 · 140 · 1 = 322 |
| Hücre durumu | KAT'Î 49 · KAT'Î-ŞARTLI 33 · ZAN-I GÂLİB 21 · İHTİLAFLI 6 (hiç ispatsız DOĞRU/YANLIŞ hücre yok) |
| Matris (3488 satır) | YAPILAMAZ 2002 · KULLANILDI 297 · YAPILMADI 585 · SINIFLANMADI 429 · KOMBİNE 78 · HUDUT 54 · ÖNCÜL 36 · AÇIK 7 |
| Kombinasyon satırı | 1085 (yeterli 937, asgarî 202) |
| Felsefe | ÇÜRÜTÜLDÜ kat'î 23 · kat'î fakat şartlı 14 · zannî 3 · İHTİLAFLI 1 · UYUMLU 1 · **koşulsuz ÇÜRÜMEDİ 0** |

## Dürüstlük notları (F 2-A 32, 5)

1. **Bütün ispatlar taslaktır ve hafızadandır.** Kaynak yoklanmadı (3-I 230); her önermenin kaynağı okunmadan "kat'î" yazılan şey yalnız **iç tutarlılık** bakımındandır, kitabın nihaî hükmü değildir.
2. **"Kat'î-şartlı" kat'î değildir.** Vâcib'in varlığı (Q02.c1) dâhil **bütün** ispat yolları en az **sebep-ilkesi** ailesine (tercihsiz tercih, hâdisin muhdisi) dayanır; Q02.c1'in hiçbir alt kümesi bu aileden bağımsız değildir (kombinasyon tablosunda "ortak zayıf halka: sebep-ilkesi"). Bu ilkeyi kabul etmeyen muhatap için ağ şunu verir: Q02.c1 düşer; **F01 (katı ateizm) ÇÜRÜMEDİ olur**, F02 ve F08 zanna iner, diğer yedi felsefe (F23, F25, F26, F29, F30, F31, F32) zan-ı gâlibe iner (Zayıf halkalar sayfası).
3. **Çürümeyen felsefe bırakmama hedefi bu sürümde koşulludur.** Listelenen 42 felsefeden koşulsuz `ÇÜRÜMEDİ` olan yoktur (hepsi en az bir yanlış hücreye bağlıdır ve o hücre bir ispatla çürütülmüştür); fakat bu, yukarıdaki zayıf halkalar kabul edilmeden doğru değildir. Ayrıca felsefe listesi **istikrâîdir** (sayarak kurulmuştur): hücreler aklî hasırla kapalıdır, yeni bir felsefe mevcut hücrelerden birine düşer, ama bu düşüşü her yeni felsefe için ayrıca yoklamak lâzımdır.
4. **Kısmî çürütmeler:** Q09.c2 (zorunlu sudûr) ve Q16.c1 (tesadüf) için gerçek, tam kapsamlı bir ispat yazılmadı; Q09.c2 yalnız Q13.c1'e (âlemin hudûsu, zayıf halkalı) ve Q09.c4'ün ispatına bağlanarak çürür; Q16.c1 yalnız zan-ı gâlib düzeyindedir. Sudûrcu felsefecilerin akıllar silsilesi cevabı yoklanmadı.
5. **İHTİLAFLI hücreler (6):** Q05.c4, Q13.c3 ve dört sıfat (semi', basar, kelâm, tekvîn) hücresi kelâm içi ihtilaflıdır; kitap onları ne iddia eder ne çürütür; veritabanı onlara doğru hükmü vermez (I9). F33 (Mu'tezile) bu yüzden `İHTİLAFLI`.
6. **Açık iş:** 585 hücre × usul çifti `YAPILMADI`dır (usulün şartı mümkün, kayıt yazılmamış); çoğu U03, U28, U17, U01 (isbat usulleri) ve U02, U09, U27, U29'un 15 sıfat hücresindeki karşılıklarıdır. Bunlar **sayılır ve gizlenmez**, ispat kaydı yazıldıkça düşer. Ayrıca 429 `SINIFLANMADI` hücre–Fârâbî sınıfı çifti vardır (ispatlar enne/lime ve dört sebep sınıflarına yalnız bir kısmında etiketli).
7. **`YAPILAMAZ` kuralları Claude'un hükmüdür** (özellikle U26 ilzam ve U27/U29 için "kayıtlı felsefe yok"); `kural.py`de yazılıdır, yoklanabilir.
8. **Felsefe eşlemeleri yaklaşıktır:** F05, F16, F17, F30, F31 (Budizm, Teslis, Spinoza/Advaita, Vedânta, Tao) kendi kaynaklarından okunmadan eşlenmiştir; hücrelerdeki not "kaynak okunmadan ilzam yazılmaz" der.
9. **İkinci bir motor yoktur:** türetmeler yalnız `motor.py`dedir (F 2-B 42 ruhu); veri dosyalarında hesap yoktur.
10. **Python betikleri bu depoda `kitap/` altındadır ve tahtın (F 1-L) parçası değildir;** veritabanını kurmak için `python3 insa.py` koşturulmuştur.

## Ölçü sağlığı (F 3-B 27-B)

`insa.py` her kuruluşta şunları sayar ve hepsi tamam çıkmıştır: bulunamayan kimlik 0 · zemine bağlanamayan ispat 0 · `kapsam_cerhi` atfı eksik hücre 0 · ispatsız veya yalnız kısmî DOĞRU/YANLIŞ hücre 0 · İHTİLAFLI hücreye hasırla doğru hükmü 0 · matris satırı 3488 = 109 × 32 · kombinasyon 1085 = Σ(2ⁿ−1). **Ayırt testi:** bir zayıf aile kaldırıldığında bağlı hücrelerin durumu fiilen düşer (sebep-ilkesi 28 hücre, kemâl 11, ibadet tanımı 4, terkip 1); etkisiz çıkan beş aile (ihkam, özdeşlik, zaman, zât–vücûd, zorunluluk de dicto) başka ispatlarla ayaktadır ve bu da sayılıdır.

## Padişaha sorulacak tetabuk (3-A 13)

Fihrist S35'tedir.
