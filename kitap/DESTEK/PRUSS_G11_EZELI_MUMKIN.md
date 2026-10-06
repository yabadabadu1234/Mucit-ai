# G11: ezelî mümkinin çıplak varlığı -- iki yolun birlikte denenmesi

Padişah: "İkisini de dene." Soru (önceki dosya `PRUSS_G10_ISTISNA.md`, b.6): **ezelî bir mümkin açıklamasız var olabilir mi?** İki yol: **(1)** varlık köprüsünü (`k_tercihsiz`) ezelî mümkin için temellendirmek; **(2)** ezelî mümkinin tanımından bir imkânsızlık aramak. Akıl yürütme **Claude'undur.** Sonuç: **ikisi de burhan getirmedi ve aynı noktada birleşti; yan ürün olarak veritabanında gizli bir ilke bulundu ve düzeltildi.**

## 0. Önceki dosyaya düzeltme (nakz, 3-I 179 ruhu)

`PRUSS_G10_ISTISNA.md` b.4 ve b.6 "ezelî mümkinin çıplak varlığı ancak varlık köprüsüyle (`k_tercihsiz`) çürür" dedi. **Eksikti.** Ezelî mümkinin çıplak varlığını çürüten **iki** klasik ilke vardır ve biri yeter:
- **varlık ilkesi** (mûcidsiz icâd muhaldir; Sadrüşşerîa, Güldü 2022 s.590-592),
- **hâl ilkesi** (tahsis: belirli hâl bir muhassıs ister; Cüveynî'den beri tahsis delili, Güldü s.584).
Veritabanında bu ikisi `Q03.c2/U03` ve `Q03.c2/U07` olarak zaten ayrı yazılıdır. Kök zayıf halka "tek" değil, **"veya"**dır.

## 1. Yol 2: tanımdan imkânsızlık

**Önsav (karşı model, taslak):** `mümkin`, `vâcib`, `ezelî` ve `açıklamasız` tanımlarından **tek başına** çelişki çıkmaz.
*Model:* iki dünya `{w, w'}`; alan `{X}`; `X` yalnız `w`'de vardır (öyleyse varlığı da yokluğu da mümkündür, yani `t_mumkin` sağlanır); `X` ezelîdir (başlangıcı yoktur); `X` vâcib değildir (yokluğu `w'`de gerçekleşir); açıklama ilişkisi **boştur** (`X`'in açıklaması yoktur). Tanımların hiçbiri bu modeli yasaklamaz. □

**Sonuç:** çelişkiyi doğuracak ilke tanımın içinde değildir. Modeli dışlayan **asgari ilke** şudur:
```
MP (varlık): her mümkin var ise, kendisi dışında bir var edicisi vardır
HP (hâl)  : mümkin hâller arasından birinin gerçekleşmesi bir muhassıs ister
```
`E2b` (ezelî çıplak mümkin) ⟹ ⊥ **ancak** `MP ∨ HP` ile. Yani tanım yolu **ilkeye geri döner**; bu, tereccuh bilâ müreccih ilkesidir. Not: tanımdan imkânsızlık yolu **kapanmadı**, "tanımlar yetmez" olarak sonuçlandı.

### Yan ürün: gizli ilke (veritabanı hatası)

Öncül listesini bu ilkeyi taşıyan başka öncül var mı diye taradım. `k_sebep_istemez` öncülünün **eski metni** "Sebep ihtiyacı mümkine mahsustur; Vâcib'de sebep sorusu tanımına aykırıdır" idi ve **yakîn, zayıf işaretsiz** durdu. "Mümkine mahsustur" ibaresi "her mümkin sebep ister" yönünü **gizlice yakîn öncül** olarak taşıyordu ve 15 sıfat hücresinin (`Q10.*.c2`) çürütmesi buna dayanıyordu. Yani tartışmalı ilke, zayıf halka sayımından **kaçmıştı.**

**Düzeltme:** öncül yalnız Vâcib için bırakıldı ("Vâcib'in vücûbunun ayrı bir sebebi aranmaz"); mümkin yönü, **zayıf işaretli** `k_tercihsiz_hal` olarak 15 ispata açıkça eklendi.

| Ölçü | Önce | Sonra |
| :-- | :-- | :-- |
| Hücre durumu: KAT'Î / KAT'Î-ŞARTLI | 49 / 33 | **37 / 45** |
| `Q10.hayat/ilim/kudret/irade/semi/basar/kelam/tekvin/hikmet/adalet/rahmet/sidk.c2` | KAT'Î | **KAT'Î-ŞARTLI** (12 hücre) |
| Hâl kanadı (`sebep-ilkesi-hal`) kalkınca düşen hücre | 18 | **30** |
| Sebep ilkesinin üç kanadı birlikte kalkınca | 26 hücre, 9 felsefe | **38 hücre, 9 felsefe** |

(Kıdem, bekâ ve gınâ c2 hücreleri değişmedi: doğru kardeşin ispatlarından da çürütüldükleri için zayıf halkasız yol vardır.)

Bu, kitabın "yakîn" iddiasının önceki sürümde **olduğundan güçlü** göründüğünü gösterir; düzeltme kitabı dürüstleştirdi.

## 2. Yol 1: varlık köprüsünü temellendirme denemesi

`MP`'yi daha temel öncüllerden türetmeye çalışan adaylar ve tavanları:

| # | Aday türetme | Durumu | Tavan |
| :-- | :-- | :-- | :-- |
| A1 | **Analitik:** "icâd mûcid ister" (fiil, fâil ister) | "Başlama" ile "ihdas edilme" ayrıdır (Hume); ezelî mümkinde başlama yok, ihdas iddiası zaten ilkenin kendisi | Tutmaz |
| A2 | **Simetri kırılması:** varlık ile yokluk eşit nisbetliyse varlığın ağır basması bir simetri kırılmasıdır; fizikte kırılma için kırıcı (neden, şans düzeneği) bulunur (Curie ilkesi, 1894; **hafızadan, yoklanmadı**) | Yerel tecrübe; bütüne ancak tekdüzelik köprüsüyle taşınır (G8'e yaslanır) | zan-ı gâlib (veritabanı: `Q03.c2/U14`, istikrâ olduğundan **zan**) |
| A3 | **Pruss'un epistemik delili** (şanssız hipotez a priori reddedilir) | Zaten kayıtlı; G1-G2 sınırlarıyla | zan-ı gâlib |
| A4 | **Tarihî mutabakat:** kelâm (tahsis, kayyûmiyet) da felsefe (İbn Sînâ: mümkin vâcib bi-ğayrihidir) de ezelî mümkinin müreccih istediğinde birleşir (Güldü 2022, s.584-586) | İcmâ'dır, burhan değil; modern hasım "ezelî çıplak evren" der (Russell) ve bunu iki gelenekten de kopar | burhan değil |
| A5 | **Retorsion (bilgi kanadı):** sebepsizlik kabul edilirse ilmî açıklamanın temeli kalmaz | Küllî sebepsizlik savunana vurur, yerel inkârcıyı kuşatmaz | zan-ı gâlib |

Hiçbiri `MP`'nin **burhanını** vermez. `MP`, ancak **evvelî** sayılırsa burhan olur ve "evveliyyât" iddiası tartışmalıdır (V.0 tenkit).

## 3. İki yolun birleştiği nokta

Yol 2 `MP ∨ HP`'yi, Yol 1 aynı ilkenin dayanak adaylarını verdi. Yani **iki yol aynı yerde birleşti:** **tereccuh bilâ müreccih** (eşit nisbetli iki taraftan birinin sebepsiz ağır basması). Ne tanımdan, ne tecrübeden, ne tarihten burhan çıkmadı.

## 4. Veritabanı

- `k_sebep_istemez` düzeltildi (gizli ilke temizlendi); `Q10.*.c2` ispatlarına `k_tercihsiz_hal` eklendi.
- Yeni öncül `k_simetri_kirilma` (zayıf, aile `curie`); yeni ispat `Q03.c2/U14` (zan).
- Sayılar: 89 önerme, 343 ispat, 1287 kombinasyon satırı; hücre durumu KAT'Î 37 · KAT'Î-ŞARTLI 45 · ZAN-I GÂLİB 21 · İHTİLAFLI 6.

## 5. Hüküm

**Burhan gelmedi.** "Ezelî mümkin açıklamasız var olabilir mi?" sorusu, kesinlik ölçeğinin **evvelî** seviyesinde bir iddiaya (tereccuh bilâ müreccih muhaldir) bağlı kalıyor. Dürüst iki yol var: (i) bu ilkeyi **evvelî** diye ilan edip muhataba tenbih ve ilzamla yaklaşmak (kitabın Kısım I usulü); (ii) ilkeyi **zayıf halka olarak açıkça yazmak** (şimdiki durum). Kitap (ii) ile devam ediyor. Bu denemeden çıkan somut kazanç: **gizli ilke temizlendi, veritabanı dürüstleşti.**
