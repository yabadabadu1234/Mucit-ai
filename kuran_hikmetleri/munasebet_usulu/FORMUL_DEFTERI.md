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
