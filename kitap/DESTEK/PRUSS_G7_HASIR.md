# G7: yokluk hükmünün destek türlerinin hasırı -- sayımdan mantıksal ikileme

Padişah: "Dene." Önceki deneme (`PRUSS_G2_IKILEM.md`) cezmî nefyin dört desteğini **saymıştı** (bulamama, istikrâ, imkânsızlık, sadelik) ve sayımın tamlığını gösterememişti (G7). Bu denemede sayım bırakılıp **mantıksal bir ikilem** kuruldu. Akıl yürütme **Claude'undur**. Sonuç: **G7 sayımdan ikileme çevrildi; sayıma bağımlılık yalnız "çıkarımsız kabul" kolunun üçlüsüne (duyu, akıl, haber) indi; katiyet zan-ı gâlib, burhan değil.**

## 1. İkilem (nefy–isbât)

`N` = cezmî nefy ("Vâcib yoktur", yani "evren dışında açıklama yoktur"). `N`'nin desteği:

1. **Ya çıkarımsız kabul edilir** (hiçbir şeyden çıkarılmadan inanılır).
2. **Ya çıkarımla kurulur.** Bu hâlde öncül kümesi `P`:
   - 2a. `P ⊨ N` (öncüller hükmü gerektirir), ya da
   - 2b. `P ⊭ N` (gerektirmez).

Bu üç hâl (1, 2a, 2b) birbirinin tümleyenidir; ikinci düzeyde de aynı: gerektirir / gerektirmez. Hasır **mantıksaldır**, destek türlerini saymaya dayanmaz.

## 2. Her kolun sınavı

**Kol 1 (çıkarımsız):**
- *Duyu:* duyu yalnız âlemin içindekini gözlemler; âlem dışında bir şeyin yokluğu müşahede edilmez (I.4.3.5).
- *Haber:* haber yeni destek üretmez, kaynağının desteğini devralır; devralınan destek bu ikilemin kollarından biridir (I.4.5, V.1.2.5).
- *Akıl (evvelî):* "bütün istisnadır" hükmü aşikâr değildir; bu, kolun 2b'deki köprü sınavıyla birlikte ele alınır.
Sonuç: kol 1 `N` için destek **sağlamaz**.

**Kol 2a (gerektirir):** `P`, `N`'yi gerektiriyorsa `P`'nin içinde şu iki şeyden biri vardır:
- Vâcib kavramı çelişkilidir, ya da kesin bir olguyla bağdaşmaz: **Q01 hücrelerinde çürütüldü** (veritabanı: `Q01.c1`, `Q01.c3`).
- `P`, dışa dair bir yokluk hükmü taşır: bu **sorunun cevabını öncül yapmaktır** (kısırdöngü).
Sonuç: kol 2a **düşer**.

**Kol 2b (gerektirmez):** `P ∧ B ⊨ N` yapan bir **köprü öncül** `B` gerekir (çıkarımın eksik öncülü). `B`, iç gözleme dayanan bir çıkarımı dışa taşıyan bir ilkedir; kendisi gözlemle desteklenemez, çünkü gözlem içeridedir. Öyleyse `B` ya delilsiz bir postulattır ya başka bir köprüye dayanır (gerileme). Hasmın elindeki tek tecrübî köprü adayı **tekdüzeliktir** (iç olayların açıklanmış olması dışa ve bütüne taşınır). Bu köprü:
- "bütün de açıklanmıştır" sonucunu **destekler** (`¬N`),
- "bütün istisnadır" sonucunu **desteklemez**.
`N` için gereken köprü ise "açıklanmışlık yalnız parçalara mahsustur, bütün istisnadır"dır: **evvelî değildir** (karşıtı tutarlıdır) ve lehine **delil gösterilmemiştir.** Sonuç: kol 2b'de `N` ancak **delilsiz bir istisna postulatıyla** ayakta kalır.

## 3. Simetri notu (dürüstlük)

"Karşıtı tutarlıdır" sınavı **iki tarafa da vurur:** sebep ilkesinin karşıtı da tutarlıdır (Hume). Bu yüzden "evvelî değil" tek başına `N`'yi çürütmez. Fark şudur: bizim tarafta (i) Pruss'un delili (zan-ı gâlib) ve (ii) hasmın kendi tekdüzeliğinin **yönü** vardır; karşı tarafta ikisi de yoktur. Bu fark **zan-ı gâlib** düzeyindedir ve `k_istisna_delilsiz` öncülü bu yüzden zayıf işaretlidir.

## 4. Veritabanında ölçülen

Yeni öncüller: `k_destek_ikilik`, `k_gaybi_hiss_yok`, `k_haber_devir` (üçü yakîn, mantıksal), `k_tekduzelik_aciklama` (zayıf, aile `tekduzelik`), `k_istisna_delilsiz` (zayıf, aile `istisna`). Yeni ispat: `Q02.c2/U08` (sibr ve taksim); `Q01.c1` ve `Q01.c3` hücrelerine dayanır. Katiyeti **ZAN-I GÂLİB**.

| Deney (hepsinde sebep ilkesi + `yokluk-egilim` + `kureselleme` kalkmış) | Q02.c1 | Q02.c2 | F01 |
| :-- | :-- | :-- | :-- |
| Hiçbiri daha kalkmamış | zan-ı gâlib | zan-ı gâlib | zan-ı gâlibe çürütülmüş |
| Eski sayım yolunun aileleri de kalkar (`destek-hasir`, `muhatap-kabulu`, `sadelik`) | zan-ı gâlib | zan-ı gâlib | zan-ı gâlibe çürütülmüş |
| Yeni ikilem yolunun aileleri de kalkar (`tekduzelik`, `istisna`) | zan-ı gâlib | zan-ı gâlib | zan-ı gâlibe çürütülmüş |
| **Her iki yolun aileleri de kalkar** | İSPATSIZ | İSPATSIZ | ÇÜRÜMEDİ |

Yani cezmî nefyin çürütülmesi artık **iki ayrı zayıf aile kümesine** dayanıyor ve her biri tek başına zemini taşıyor; ikisi birden düşerse zemin düşüyor. İki yol aynı kavramsal yapıyı paylaşıyor (hasmın destek arayışı), bu yüzden bağımsızlıkları **aile düzeyinde gerçek, kavram düzeyinde kısmîdir.**

## 5. Sınırlar

1. **G8:** hasım "tekdüzelik yalnız iç alanda geçerlidir" diyebilir. Bu da bir istisna köprüsüdür ve aynı delilsizliğe düşer; fakat hasım bu adımı kabul etmeyebilir.
2. **G9:** kol 1'deki üçlü (duyu, akıl, haber) klasik sayımdır; sayım artık **yalnız bu kolda** kalmıştır. Dördüncü bir çıkarımsız kaynak (ilham, iç tecrübe) gösterilirse **güvenilirliği gösterilmelidir**; gösterilmedikçe cezmî nefye destek olmaz.
3. **Simetri (b.3):** fark zan-ı gâlib düzeyindedir.
4. **Tevakkuf çürütülmez** (önceki dosya, b.5.1); ikilem yalnız cezmî nefyi eler.
5. **Burhan değildir:** üç zayıf aile ailesi kümesi (tekdüzelik, istisna, `k_zorunluluk_dicto` aracılığıyla Q01.c3) ve müsellem öncüller zan-ı gâlibe tavan koyar.

## 6. Hüküm

Padişahın "burhan seviyesinde ispatlanacak" kanaati dört denemeden sonra şu noktada: rastgelelik itirazı çözüldü (çıplak şans açıklamadır); cezmî nefy için **iki ayrı yol** elenmiştir; sayım bağımlılığı çıkarımsız kolun üçlüsüne indi. **Burhana ulaşılmadı.** Burhan için kalan iş: `k_tekduzelik_aciklama` ve `k_istisna_delilsiz` öncüllerinin zayıflığını ortadan kaldırmak, yani "bütün istisnadır" ilkesinin **imkânsız** (çelişkili) olduğunu göstermek; bunun yapılıp yapılamayacağı **bilinmiyor.** Denenecek yol: istisna ilkesinin kendi uygulanışında çelişkiye düştüğünü (açıklanmışlığı parçalara veren şeyin kendisi parçası olmayan bir bütün açıklaması gerektirdiği) göstermek.

**Güncelleme:** son açık iş (istisna ilkesinin çelişkililiği) denendi: `PRUSS_G10_ISTISNA.md` (çelişki türetilemedi; kök zayıf halka ezelî mümkinin çıplak varlığına indi).
