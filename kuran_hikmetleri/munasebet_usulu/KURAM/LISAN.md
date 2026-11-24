# ÜSTTEN BAKIŞ LİSANI

## Girizgâh

Bu lisan, Kur'ân-ı Kerîm'e **üstten bakmak** içindir: bir sûreyi, bir kısmı yahut bütün mushafı tek bakışta okumak; nerede ne söylendiğini, söylenenlerin birbirine nasıl bağlandığını görmek; istenirse yaklaşıp tek âyete inmek. Lisanın dört parçası vardır: **harfler** (kayıt cinsleri), **cümle** (atom ve bağ), **yükseklik** (kaç basamak yukarıdan bakıldığı), **okunuş**. Lisan gerçekten bu işi görüyor mu sualine ancak sûreler yazılıp okunarak bakılır; bu yüzden sonda iki sûre lisanla yazılmıştır.

## 1. Harfler

| Harf | Söylediği | Yazılışı |
| :-- | :-- | :-- |
| ⟐ | kasem (yemin) | `⟐(Asr)` |
| ↑! | hüküm bildirmek | `↑!(…)` |
| ∀ ∃ | her, bir | `∀x∈İnsan` |
| ¬ | nefy | `¬∃x.Doğur(Allah→x)` |
| ∖ | istisna (…den ayrı) | `İnsan ∖ Mümin` |
| ∧ | ve | `hüve ∧ Ahad` |
| {} | vasıf | `Allah{Samed}` |
| ⟨⟩ | örtük (metinde söylenmeyen ama okunan) | `⟨Allah → Peygamber⟩` |
| ⊢ | delil olur | `⟐(Asr) ⊢ …` |
| O(…) | emir | `O(Söyle(Peygamber))` |

## 2. Cümle

**Atom** bir âyetin bir parçasıdır: `(âyet, nereden, nereye, ad, yazılış, örtük)`.
**Bağ** iki atom veya âyet arasındadır; adı dokuz bağdan biridir:

| Bağ | Mana |
| :-- | :-- |
| Ta'lîl | sebep göstermek |
| Tefrî' | dallandırmak |
| Tafsîl | açmak |
| İcmâl | toplamak (tafsîlin tersi) |
| Mukâbele | karşılıklı koymak |
| İstidlâl | delil getirmek |
| Takyîd | sınırlamak, şart koşmak |
| Temsîl | misalle anlatmak |
| Te'kîd | pekiştirmek |

Her bağın derecesi "hikmet ihtimali"dir; murâd-ı ilâhî diye yazılmaz.

## 3. Yükseklik

| Basamak | Neye bakılır | Gösterim |
| :-: | :-- | :-- |
| 0 | atom (âyet parçası) | harflerle |
| 1 | âyet | atomların toplamı |
| 2 | kısım | âyetlerin bağlarla toplanmış hâli |
| 3 | sûre | kısımların tek cümlesi |
| 4 | mushaf | sûrelerin tek cümlesi |

Yukarı çıkmak **toplamak** (katla), aşağı inmek **açmaktır**. Her üst basamak kendi altındakilerin izini taşır; yukarıdan görülen şeyin hangi âyetlerden geldiği her an sorulabilir.

## 4. Okunuş

Üstten okuyan önce en üst cümleyi okur, sonra merak ettiği dala iner. Her dalın yanında bağ adı vardır; bağ adı o iki parçanın neden yan yana durduğunu söyler.

## 5. Yazılmış iki sûre

### Asr (103)
```
SÛRE 103
  ⟐(Asr)                                   ← âyet 1
     ⊢ İstidlâl ⟶ ↑!( ∀x∈İnsan . Hüsran(x) )   ← âyet 2
        Takyîd ⟶ İnsan ∖ Mümin               ← âyet 3
                 { İman ∧ SalihAmel ∧ TevasiHak ∧ TevasiSabr }
```
Tek bakışta okunuş: *kasem, insanın hüsrânda olduğuna delil; hüsrândan ayrılanlar dört vasıfla sınırlı.*

### İhlâs (112)
```
SÛRE 112
  O(Söyle(Peygamber))   ⟨Allah → Peygamber⟩        ← âyet 1
     hüve[Allah] ∧ Ahad(Allah)
       Tafsîl ⟶ Allah{Samed}                        ← âyet 2
         Tefrî' ⟶ ¬∃x.Doğur(Allah→x)  ∧  ¬∃y.Doğur(y→Allah)   ← âyet 3
           Te'kîd ⟶ ¬∃x.Küfüv(x, Allah)    ⟨Allah ≇ x⟩      ← âyet 4
```
Tek bakışta okunuş: *emir; Allah ahaddır; ahadlık samedlikle açılır; samedlik doğurmamak ve doğmamakla dallanır; hepsi küfüvsüzlükle pekiştirilir.*

## 6. Dosyalar

`kuram.py` lisanın ayrıştırıcısı ve toplama işlemleri, `kuram_ornek.py` iki sûrenin atom ve bağ kayıtları.
