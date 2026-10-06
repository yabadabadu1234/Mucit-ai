# Pruss makalesinin iki boşluğunu kapatma denemesi (G1 ve G2)

Padişah: "Dene bakayım ikisini" (G1 ve G2 için). Boşluklar `PRUSS_PSR_OLASILIK.md` b.9'dadır. Aşağıdaki akıl yürütme **benimdir** (Pruss yazmıyor); kaynakla bağı her adımda gösterilir. Sonuç: **G1 daraltılmış hâliyle kapandı, G2 kapanmadı; nakze indi.**

## G1: "açıklamasız hipotez en fazla [0,1] verir" (Pruss b.2.3, s.7-8)

Pruss bunu üç şıkla (kesin sayı · hiç olasılık · aralık) söyler fakat "aralık" şıkkında yalnız `[0,1]` kalacağını **ileri sürer**. Denenen çözüm, kavramı tanımlamaktır.

**Tanım 1 (şans):** şans, bir sürecin (düzenek ve kanunun) eğilimidir (Pruss s.2'nin kendi tanımı). Sonuç olayına dar bir olasılık aralığı `I = [a,b] ≠ [0,1]` veren hipotez, o sürecin eğilimi hakkında bir ifade taşır.

**Tanım 2 (açıklamasız):** hipotez `H`, sonuç hakkında hiçbir eğilim ileri sürmüyorsa açıklamasızdır. Olasılıkçı açıklama açıklama sayılır (Pruss s.1; Salmon 1989; Jeffrey 1969); bu yüzden eğilim ileri süren hipotez açıklamasız **değildir**.

**Önsav (G1, tahlilî):** `H` açıklamasızsa ve `E` önemsiz olmayan bir sonuç olayıysa `P(E|H) = [0,1]`.
*Kanıt:* `P(E|H) ⊆ I`, `I ≠ [0,1]` olsaydı `H` sonuç hakkında bir kısıt, yani bir eğilim ileri sürmüş olurdu (Tanım 1); bu Tanım 2'ye aykırıdır. Öyleyse tek kısıt totolojidir: `[0,1]`. □

Bu bir **tahlildir**: tanımın açılımıdır. Gerçek iddia, Tanım 2'nin hasmın "sebepsiz" dediği şeyi yakalayıp yakalamadığıdır. Üç hasım tipi tek tek sınandı:

| Hasım tipi | Ne ileri sürer | Tanım 2'ye girer mi | Sonuç |
| :-- | :-- | :-- | :-- |
| (i) **Çıplak şans** (kuantum): "bireysel sonuç rastgeledir, şansı vardır" | eğilim | **Hayır** | Açıklama sunmuştur; Pruss'un yerel ilkesini **ihlal etmez** (PSR olasılıkçı açıklamayla bağdaşır). Rastgelelik itirazı bu delile muhtaç değil, onunla çelişmez |
| (ii) **Çıplak düzenlilik** (Hume'cu): "sıklığın limiti `[a,b]`'dedir, açıklaması yoktur" | eğilim yok, desen var | Evet | *Önsav:* her sonlu başlangıç parçası her limit sıklıkla bağdaşır (bir sonlu diziyi, limiti istenen `p ∈ [0,1]` olan sonsuz diziye uzatabiliriz). Bu yüzden `H` sonlu gözleme **olasılık vermez**, aralığı `[0,1]`'dir. Sonlu gözlemden limite geçmek için temsil edicilik varsayımı gerekir ve o da bir eğilim ileri sürmektir, yani (i)'e döner |
| (iii) **Çıplak varlık** ("evren, mümkinler bütünü müreccihsiz vardır") | hiçbir şey | Evet | Yokluktan varlık için süreç ve düzenek yoktur, eğilim yoktur: aralık `[0,1]` (b. aşağıdaki küresel adım) |

**Sonuç G1:** kapandı, fakat **iddia daraldı**: Pruss'un delili yalnız **şanssız** hipotezleri eler. Çıplak şansı (kuantum) ve onun açıklamasız bırakılan *kendi şans değerini* **elemez**; bunun için küresel ilke gerekir (aşağıda). Bu, rastgelelik itirazı için **iyi haberdir**: itirazı savunan kimse eğilim ileri sürüyor, yani açıklama kabul ediyor (V.1.4.27 biçimsel dayanak buldu).

**Küresel adım (G1'in Vâcib'e dönük kolu):** yokluk bir süreç değildir; süreç olmayan yerde eğilim (şans) yoktur; öyleyse "mümkinler bütünü müreccihsizdir" hipotezi şanssızdır ve aralığı `[0,1]` kalır. Bu, kitabın V.1.4.38'indeki örnekleyici cevabının biçimsel hâlidir. **Zayıf öncül:** "yokluk eğilim taşımaz" (`k_yoktan_sanssiz`); fizik vakumunu "hiçbir şey" sayan hasım bunu reddeder. Vakum bir fizik durumudur (V.1.4.29), fakat bu ayrımı hasım kabul etmeyebilir.

## G2: "düşük öncül yolu kapatılmamıştır" (Pruss s.8-9)

Hasmın yolu: "sebepsiz hipotezlere, bilim yapılabilsin diye, çok düşük öncül veririm." Denenen çözüm, **eşdeğerlik** (parite) argümanıdır.

1. Düşük öncülün tek gerekçesi: aksi hâlde deneyle ayırt edilemeyen hipotezler arasında seçim keyfî olur ve bilim kurulamaz (Pruss s.8-9).
2. Pruss s.12-13'e göre bu gerekçe **küresel** sebepsiz hipotezler için de aynen geçerlidir: sebepsiz bir evrende Büyük Patlama hipotezini beş dakikalık evrene veya bir dakikalık geriye ışık konisine tercih için şans veya sadelik gösterilemez; sadelik ikincisini birincisinden önce eler. (`p_esdegerlik_kureselleme`, zan-ı gâlib.)
3. Öyleyse hasım yolu yerelde kabul edip küreselde reddederse **kendi gerekçesini terk eder**; küreselde de kabul ederse çıplak evrene düşük öncül vermiş olur (kendi ölçüsüyle).
4. **Nakz (U27, muhatabın kabulü kadar):** itirazını Büyük Patlama'ya (V.1.4.1) ve kuantuma (V.1.4.3) dayandıran hasım, küresel ve yerel bilimsel çıkarımı **kabul etmiştir**; bu çıkarımı temelsiz bırakan sebepsiz hipotezlere düşük öncül vermek zorundadır.

**Sonuç G2: kapanmadı.** Sebep: düşük öncül sıfır demek imkânsız demek değildir ve hasım "küresel tarihî çıkarımı da bırakıyorum" diyerek **tutarlı kalabilir**. Bu hâlde delil onu **çürütmez**; yalnız itiraz kaynağını (Büyük Patlama ve kuantum çıkarımlarını) elinden alır. Bu bir ilzamdır (hasmın kendi ölçüsüyle), burhan (hasım kabul etse de etmese de bağlayıcı) değildir.

## Veritabanında ölçülen

Yeni öncüller: `t_sans_egilim` (tanım, yakîn), `k_yoktan_sanssiz` (zayıf, aile `yokluk-egilim`), `p_esdegerlik_kureselleme` (zan-ı gâlib, zayıf, aile `kureselleme`). Yeni ispat: `Q03.c2/U27` (nakz), katiyet **ZAN-I GÂLİB**.

| Deney: sebep ilkesinin üç kanadını (varlık, hâl, bilgi) birlikte kaldır | Q02.c1 · Q02.c2 · Q03.c2 | F01 (katı ateizm) |
| :-- | :-- | :-- |
| Pruss ispatları **yokken** (önceki ölçüm) | KAT'Î-ŞARTLI → **İSPATSIZ** | **ÇÜRÜMEDİ** |
| Pruss ispatları **varken** (bu ölçüm) | KAT'Î-ŞARTLI → **ZAN-I GÂLİB** | zan-ı gâlibe çürütülmüş |
| Üç kanat **ve** `kureselleme` ailesi de kaldırılırsa | → İSPATSIZ | ÇÜRÜMEDİ |
| Üç kanat **ve** `yokluk-egilim` ailesi de kaldırılırsa | → İSPATSIZ | ÇÜRÜMEDİ |

Yani Pruss çizgisi sebep ilkesine bağımlılığı kaldırmıyor, fakat ilke reddedilince ağın **zemin katını İSPATSIZ'dan zan-ı gâlibe** çıkarıyor. Bu çizgi de iki zayıf aileye (`yokluk-egilim`, `kureselleme`) dayanıyor; onlar düşünce zemin yine düşüyor.

## Hüküm

- Pruss'un makalesi **burhan değildir**, fakat sebep ilkesine karşı kitabın elindeki **en güçlü biçimsel ilzamdır**; üç zayıf nokta kaldı: `k_yoktan_sanssiz` (vakum ayrımı), `p_esdegerlik_kureselleme` (hasım küresel tarihî çıkarımdan vazgeçebilir), `p_sebepsiz_sans_yok` (eski G1 öncülü, Tanım 2'ye bağlı hâlde).
- Burhana çıkarmak için gereken: "çıkarım yöntemini bırakan hasım" kolunun kapatılması. Bu kolun kapanıp kapanmayacağı **bilinmiyor**; denenecek yol: bu hasmın itiraz yapabilmek için kullandığı en az bir çıkarımı (cümlesinin bir şeyi göstermesi) bırakamayacağını göstermek (ilzam, U26). Henüz yazılmadı.

**Güncelleme:** "çıkarımı bırakan hasım" kolu ayrıca denendi: `PRUSS_G2_IKILEM.md` (cezmî nefy elendi, tevakkuf kaldı; zan-ı gâlib).
