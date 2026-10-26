# Formül defteri

Kayıt: CLAUDE.md § 3-I 334 ve 335. Formüller kaynaktan **sayfa görüntüsü olarak** okundu ve sayfadan doğrulandı. Harf ve kısaltma yazılmaz; her değişkenin yerine bir kelime konur. Kaynaktaki harf, kelimenin ilk geçtiği yerde bir defa parantezle gösterilir.

## 1. Grosz ve Sidner 1986: *Dikkat, Maksat ve Söylemin Yapısı* (Computational Linguistics 12(3): 175–204)

### 1-A. Kelime cetveli

| Osmanlıca kelime | Mânâsı | Kaynaktaki harf veya kısaltma |
| :-- | :-- | :-- |
| **Mütekellim** | Söze başlayan, söylemi yürüten taraf | ICP |
| **Muhatap** | Sözü alan, öbür taraf | OCP |
| **Söyleyen** ve **Dinleyen** | Bir bağıntıda iki tarafı genel olarak gösterir; Mütekellim ve Muhatap bunun hususî hâlidir | CP₁ ve CP₂ |
| **Kazıyye** | Doğruluğuna inandırılmak istenen önerme | p |
| **Delil** | Kazıyyeyi destekleyen önerme; her bir delil sırayla alınır | q_i |
| **Deliller Mecmuu** | Bütün delillerin "ve" ile birleşmesi | q₁ ∧ … ∧ q_n |
| **Fiil** | Yapılmasına çalışılan asıl iş | A |
| **Cüz-i Fiil** | Asıl işin bir parçası olan iş; her biri sırayla alınır | a_i |
| **Cüzler Mecmuu** | Bütün cüz-i fiillerin "ve" ile birleşmesi | a₁ ∧ … ∧ a_n |
| **Murâd eder** | Bir şeyin olmasını kasteder, niyet eder | Intend |
| **Tasdik eder** | Bir önermeyi doğru sayar | Believe |
| **İcra eder** | Bir işi yapar | Do |
| **Teyid eder** | Delillerin kazıyyeyi desteklediğini gösterir (bağıntı kısmîdir) | Supports |
| **Tevlid eder** | Cüz-i fiillerin asıl fiili doğurduğunu gösterir (bağıntı kısmîdir) | Generates |
| **Hâkimdir** | Bir maksat, öbürüne hâkimdir (hâkimiyet bağıntısı) | DOM |
| **Takaddüm eder** | Bir maksat, öbüründen evvel yerine gelmelidir | SP |
| **Maksat** | Söylem parçasının gayesi: söyleyenin muhatabın tanımasını murâd ettiği niyet | DSP |
| **Asıl Maksat** | Bütün söylemin gayesi | DP |

### 1-B. Formüller

**F1. Maksat, iki hâlde (s. 199, 201; sayfadan doğrulandı).**

- İnandırma hâli: `Murâd eder(Mütekellim, Tasdik eder(Muhatap, Kazıyye))`
- Yaptırma hâli: `Murâd eder(Mütekellim, Murâd eder(Muhatap, İcra eder(Fiil)))`

**F2. Hâkimiyet ve takaddüm (s. 179; sayfadan doğrulandı; kaynakta söz ile tarif).**

- `Birinci Maksat, İkinci Maksat'a hâkimdir` ⟺ İkinci Maksat'ın yerine gelmesi, Birinci Maksat'ın yerine gelmesinin bir parçasıdır.
- `Birinci Maksat, İkinci Maksat'tan takaddüm eder` ⟺ Birinci Maksat, İkinci Maksat'tan evvel yerine gelmelidir.

**F3. İnandırma hâlinin kuruluşu (s. 200; sayfadan doğrulandı).** Her bir delil için:

```
Murâd eder( Mütekellim,
    Tasdik eder(Muhatap, Kazıyye)
  ve Tasdik eder(Muhatap, Delil)
  ve Tasdik eder(Muhatap, Teyid eder(Kazıyye, Deliller Mecmuu)) )
```

**F4. İnandırma hâlinde denklik (s. 200; sayfadan doğrulandı).** Her bir delil için:

```
[  Murâd eder(Söyleyen, Tasdik eder(Dinleyen, Kazıyye))
 ve Murâd eder(Söyleyen, Tasdik eder(Dinleyen, Delil))
 ve Tasdik eder(Söyleyen, Teyid eder(Kazıyye, Deliller Mecmuu)) ]
        ⟺
Hâkimdir( Murâd eder(Söyleyen, Tasdik eder(Dinleyen, Kazıyye)),
          Murâd eder(Söyleyen, Tasdik eder(Dinleyen, Delil)) )
```

**F5. Yaptırma hâlinin kuruluşu (s. 201; sayfadan doğrulandı).** Her bir cüz-i fiil için:

```
  Murâd eder(Mütekellim, Murâd eder(Muhatap, İcra eder(Fiil)))
ve Murâd eder(Muhatap, İcra eder(Cüz-i Fiil))
ve Tasdik eder(Muhatap, Tasdik eder(Mütekellim, Tevlid eder(Fiil, Cüzler Mecmuu)))
```

**F6. Yaptırma hâlinde denklik (s. 201; sayfadan doğrulandı).** Her bir cüz-i fiil için:

```
[  Murâd eder(Söyleyen, Murâd eder(Dinleyen, İcra eder(Fiil)))
 ve Murâd eder(Söyleyen, Murâd eder(Dinleyen, İcra eder(Cüz-i Fiil)))
 ve Tasdik eder(Söyleyen, Tevlid eder(Fiil, Cüzler Mecmuu)) ]
        ⟺
Hâkimdir( Murâd eder(Söyleyen, Murâd eder(Dinleyen, İcra eder(Fiil))),
          Murâd eder(Söyleyen, Murâd eder(Dinleyen, İcra eder(Cüz-i Fiil))) )
```

**F7. Söylem kifayeti (s. 200; sayfadan doğrulandı; kaynakta söz ile tarif).** Mütekellim, söylenenlerin ve Muhatabın bildiği veya bulabileceği diğer malûmatın birlikte Asıl Maksat'a **yeteceğine** inanır. Mantıkî kifayet veya fiil tamamlığı şart değildir; maksat ağacı tam olmak zorunda değildir.

**F8. Yığın işlemleri (s. 180, 196–198; kaynakta söz ve şekil ile tarif).**

- **İtme:** yeni maksat, hemen evvelki parçanın maksadına hâkim değil, onun tarafından hâkim olunuyorsa yeni bir dikkat yeri yığının üstüne konur.
- **Çıkarma:** yeni maksat, yığında daha aşağıda duran bir maksadın hâkimiyeti altındaysa üstteki yerler atılır.
- **Tamamlama:** maksat yerine geldiyse onun yeri yığından atılır.
- **Sağ sınır:** yeni maksat yalnız yığında duran maksatlarca hâkim olunabilir.

**F9. Kesinti türleri (s. 192–195; kaynakta söz ile tarif).**

- **Sert kesinti:** parçanın maksadı, evvelki hiçbir maksadın hâkimiyeti altında değildir ve hiçbirinden takaddüm etmez.
- **Geri dolgu:** parçanın maksadı, kesilen parçanın maksadından takaddüm eder ve başka bir maksadın hâkimiyeti altındadır.
- **Sapma:** sert kesinti ki iki tarafta da öne çıkan bir şey vardır.

### 1-C. Usulde yeri

Bkz. `USUL_MANA_ONCELIKLI.md` § 12-E. Formüller bu defterdeki kelimelerle oraya da yazılmıştır.

## 2. Wu, Mangla, Durrett ve Li 2023: *QUDEVAL, Tartışma Altındaki Suallerin Ayrıştırılmasının Değerlendirilmesi* (arXiv:2310.14520v2; sayfa görüntüsünden okundu, s. 1–9, 13)

### 2-A. Kelime cetveli

| Osmanlıca kelime | Mânâsı | Kaynaktaki harf |
| :-- | :-- | :-- |
| **Sual** | Okuyanın o yerde soracağı sual | Q |
| **Çıpa Cümle** | Sualin doğduğu yer, öndeki bir cümle | S_k |
| **Cevap Cümle** | Sualin cevabını taşıyan cümle | S_a |
| **Bağlam** | Çıpa cümleye kadar olan bütün cümleler | C_Q = S₁, …, S_k |
| **Tahmin** | Ayrıştırıcının ürettiği; sualin ve çıpanın başına şapka konur | Q̂, k̂ |
| **Kenar** | Üçlü: sual, çıpa, cevap | (Q, S_k, S_a) |

### 2-B. Tarifler

**Q1. Kenar (s. 3).** `Kenar = (Sual, Çıpa Cümle, Cevap Cümle)`. Ayrıştırma işi: her cevap cümle için sual üretmek ve çıpanın yerini tahmin etmek.

**Q2. Ölçü işlevi (s. 6).** `Hüküm(Cevap Cümle, Tahmin Çıpa, Tahmin Sual, Bağlam) → Etiket`. Dört ölçünün her biri kendi etiket kümesine hükmeder.

**Q3. Dört ölçü ve etiketleri (s. 3–4; sayfadan doğrulandı).**

| Ölçü | Etiketler |
| :-- | :-- |
| **Dil kalitesi** | geçer / geçmez (geçmeyende öteki üç ölçü atlanır) |
| **Cevap uygunluğu** | **doğrudan ve açık** · **odaksız** (cevap cümlede var, odağı değil) · **cevaplamaz** |
| **Verilmişlik** | **yeni mefhum yok** · **cevap sızıntısı** (sualde, bağlamda olmayıp yalnız cevap cümlede geçen mefhum) · **uydurma** (ne bağlamda ne cevap cümlede olan mefhum) |
| **Çıpa alâkası** | **tam dayanır** · **kısmen dayanır** · **dayanmaz** |
| *İlâve kusurlar* | tekrar (cevabı çıpada zaten var) · fazla umumî ("ne oldu sonra?") |

**Q4. Kural tabanlı verilmişlik (s. 7, s. 12).** Sualin lemmalanmış içerik kelimeleri bağlamda yoksa: yalnız cevap cümlede geçiyorsa `cevap sızıntısı`, değilse `uydurma`; hiçbiri yoksa `yeni mefhum yok`.

**Q5. Kural tabanlı çıpa alâkası (s. 7).** Sualin odağı (en büyük isim öbeği) çıpa cümlede aranır: tamamı varsa `tam dayanır`, hiçbiri yoksa `dayanmaz`, aradaysa `kısmen`. Ölçü yedeği: sual ile çıpa arasında BLEU-1 benzerliği (`0,05` üstü tam, `0,01–0,05` kısmen, altı dayanmaz; s. 13).

### 2-C. Sayılar (sayfadan doğrulandı)

| Ölçü | Etiketleyiciler arası Krippendorff α | İnsan üst sınırı (ikili F1) | En iyi otomatik ölçünün makro F1'i |
| :-- | :-- | :-- | :-- |
| Dil | 0,56 | 0,78 | — |
| Cevap uygunluğu | 0,52 | 0,61 | 0,60 (GPT-4 ile cevap bulma) |
| Verilmişlik | 0,48 | 0,60 | 0,37 (kural tabanlı) |
| Çıpa alâkası | 0,51 | 0,60 | 0,57 (GPT-4 puanı) |

İnsan yazımı sualler (DCQA) makine sualinden iyi: cevap uygunluğunda doğrudan cevap %71,4 (makinede %43–91), verilmişlikte yeni mefhum yok %85,7, çıpa alâkasında tam dayanma %80,3 (Tablo 1). Kaynaklı ölçüler (BLEU, BERTScore, ROUGE) sual kalitesini ayırt etmez: en iyisi bile rastgeleden az farklı (Tablo 5); kaynaksız ölçüler daha iyidir.

## 3. Ko, Dalton, Simmons, Fisher, Durrett ve Li 2022: *Söylemi Anlama, Cümle Bağlarını Temsil Eden Bir Sual-Cevap Çatısı* (DCQA; arXiv:2111.00701v4; sayfa görüntüsünden okundu, s. 1–8)

Formül yoktur; usul ve sayılar vardır.

**D1. Veri toplama usulü (s. 2–4).** Evvelâ **cevap cümle** verilir; etiketleyici o cümle için **sual yazar** ve sualin doğduğu **çıpa cümleyi** seçer. Şartlar: (a) sual açık uçlu olur, yer/kişi/zaman veya evet-hayır ile cevaplanamaz; (b) sual yalnız öndeki cümleleri okuyana anlaşılır olur; (c) cevap cümlede **ilk defa geçen** bilgiye gönderme yapmaz, yalnız cevap cümlede geçen ifadeleri kopyalamaz. Bu üç şart QUDEVAL'in verilmişlik ölçüsünün yazım tarafıdır.

**D2. Cevap bulma işi (s. 4).** Verilen: bağlam, çıpa, sual. İstenen: cevap cümle.

**D3. Sayılar (sayfadan doğrulandı).**

| Ölçü | Değer |
| :-- | :-- |
| Aynı cevap cümleye iki etiketleyicinin yazdığı sualler: benzerlik 4–5 | %41,8 |
| Benzerlik 1–2 (anlamca ayrı) | %40,7 |
| Benzerlik 5 iken çıpada uyum | %69,8 |
| İnsanın cevap bulma doğruluğu | %72,2 |
| "Hemen sonraki cümle" tahmini | %40 |
| Longformer modeli | %67,2 |
| Çıpa verilmezken | %43,5 (düşüş 23,7 puan) |
| Önceki bağlam çıkarılınca | %66,4 (düşüş küçük) |
| Cevap, çıpadan 1 cümle uzakta / 2–4 / 5 ve fazla | %48,8 / 24,2 / 27,0 (DCQA) |

**Usulde yeri:** § 3-I 332 sınamasında üç şey gelir: (1) **sual yazım şartları** D1 (a)–(c) gaye sualine uygulanır; (2) **taban:** "hemen sonraki âyet" tahmini %40 ile kıyas edilir (Fâtiha'da gaye sualinin cevabını hep bir sonraki âyet saymak bir taban ölçüdür); (3) **insan üst sınırı** %72,2 ve sual benzerliği %41,8: aynı âyet için iki insanın yazdığı sualler dörtte iki kadar benzer; bu yüzden tek bir "doğru sual" aranmaz, sual **kümesi** kabul edilir.
