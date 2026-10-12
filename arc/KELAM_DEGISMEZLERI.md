# KELÂM KÜMESİ: İNSANDA DEĞİŞMEZLER · YAPAY ZEKÂDA KÜME · MUKAYESE · YENİ MATEMATİK (F 3-I 306)

Çıkarım [Ç] ve olgu [O: kaynak] ayrı işaretlidir. "Değişmez" iddiaları **aday**dır; her birinin yanlışlama sınaması yazılıdır.

## 0. Okuma
"kelâm={}" = söylenen sözün ve **söz doğuran şartların** özellikleri kümesi [Ç, padişah tarif etmedi].

## 1. Olgular [O]
| # | Olgu | Kaynak durumu |
| :-- | :-- | :-- |
| O1 | Kanonik gevelemede (mama, dada gibi tekrarlı heceler) başlangıç yaklaşık 5-10. aylar | arama, ikincil |
| O2 | Gevelemeyi ilk sözden ayırmak zordur | arama, ikincil |
| O3 | Bazı sık isimlerin (yiyecek, vücut uzvu) anlaşılması 6-9. aylarda gösterildi (33 bebek, ~20 sözcük, bakış ölçüsü); ilk söz yaklaşık 1 yaş | Bergelson-Swingley 2012, ikincil özet |
| O4 | 12-14 aylık bebekler çok durumdan eşleşme istatistiğiyle sözcük-nesne öğrenebilir; "karşılıklı dışlama" ayrı bir kısıt; bunun asıl mekanizma olup olmadığı **açık** | Smith-Yu 2008 ve sonrası, ikincil |

## 2. Padişahın suâli: kanaat edinip susmak varken niye söylüyor [Ç]
1. **Bebek zaten aylarca susar.** O3: anlama ilk söze aylar evvel gelir. Yani "kanaat, sonra sükût" **fiilen vardır**; söz kanaatten çıkmaz, kanaatin üstüne bir şey gelince çıkar.
2. **Hafıza eylem başlatamaz.** Projenin kendi şeması (CLAUDE.md § 4-I): hafıza pasif kütüphanedir; eylemi ancak vâhime (alarm) yahut âkıle'nin amelî aklı (irade) sevk eder. Kanaat hafızadadır; dil, bedensel icradır. **Söz = sevk edilmiş icra.**
3. **Sevk eden şey boşluktur.** F 3-I 214: suâl = şuur açısından boşluk + gaye. F 3-I 167: kelâm ya burhan tamam (haber) yahut iç muhakeme tıkandı ve tevcih edilir (talep). Bebek anneye kendi imkânıyla ulaşamaz: **tıkanma**. Bilinen kaldıraç: söz. "Anne" = tıkanmadan doğan çağrıdır.
4. **Neden bu söz:** söz-etki kuralı kendi eylemiyle öğrenilmiştir: söyledim, geldi. Deterministik tepki dünyasında **bir müdahale kuralı tam belirler**; ihtimale gerek kalmaz.
5. **Geveleme ilk söz değildir:** O1-O2: önce motor deneme (tâlim kapısındaki özerk gaye: girdi yok, merak gediği, F 3-I 175, I10), sonra çevrenin "anne dedi" tepkisi bu sesi bir kaldıraca bağlar [Ç, ikincil/hafıza]. İki hat birleşir: (a) anlama hattı: kapanmış kavram, (b) üretim hattı: ses + tepki bağı. Söz, ikisinin kesişiminde çıkar.
6. **Susmak neden yetmez:** değer ölçüsü boşluk azalmasıdır; sükût boşluğu azaltmaz. Söyle ⇔ boşluk > 0 ve kural var ve muhatap var.

## 3. İnsanda kelâm değişmezleri (aday) 
| # | Değişmez | Yanlışlama sınaması |
| :-- | :-- | :-- |
| H1 | Söz bir **sevkle** başlar (ihtiyaç, merak, vazife); kanaat tek başına söz doğurmaz | boşluksuz, muhatapsız, sevksiz doğan bir insan sözü bulunursa düşer |
| H2 | Söz **tevcihlidir**: muhatap vardır (kendisi dâhil) | muhatabı hiç tasavvur edilmeyen söz |
| H3 | Doğruluk **kasta** göre ölçülür, lafzî ilk manaya göre değil (kinaye) | kinayede lafzî mana ölçüsünün kasıttan iyi tahmin etmesi |
| H4 | Konuşan **kip**i muhtevaya koyar (cezm, zan, şek); kip seçimi konuşanın hâlinden çıkar | kip seçiminin hâlden bağımsız çıkması |
| H5 | Söz **zemine** bağlıdır: lafız → mana → mefhum → masadak zinciri; zincir kopunca "hangisi?" diye sorulur | zinciri olmayan söz üretimi |
| H6 | Söz önceki sözle **tutarlıdır**; hafıza konuşmayı bağlar (F 3-I 150) | |
| H7 | Söz **kapanır**: boşluk kapanınca yahut tıkanınca (suâl) | durmak için ayrı hüküm gerekmeden sürmesi |
| H8 | Söz-etki kuralları **kendi müdahalesiyle** öğrenilir | |
| H9 | Kavram **elenerek kapanır** (sebr ve taksim); istisna ortalamaya katılmaz, yaprak açar (terfi) | |
Kesinlik notu: kesin olan **kanaatin kipidir**, doğruluğu değil (yakîn = cezm + mutabakat + direnç; yanlış cezm = cehalet-i mürekkep).

## 4. Mevcut yapay zekâda kelâm kümesi (temel mekanizma; hafıza/yaygın bilgi, yoklanmamış)
| # | Özellik |
| :-- | :-- |
| A1 | Söz, P_θ(w_t | w_<t) dağılımından çekilir yahut argmax alınır |
| A2 | Başlatan şey **istemdir** (dışarıdan); içeriden boşluk yoktur (aracılı döngüler ve pekiştirme gayeyi dışarıdan ekler) |
| A3 | Zemin: lafız → lafız (yalnız metinde); çok kipli sistemde kısmen duyudan |
| A4 | Belirsizlik **dağılımda**dır, muhtevada değil; "belki" demek ayrı öğrenilmiş bir kalıptır |
| A5 | Kast ayrı bir durum değil, çıktıdan çıkarılır |
| A6 | Durma, öğrenilmiş bir bitiş belirteciyle |
| A7 | Hafıza: bağlam penceresi + ağırlıklar; cezm/zan ayrımı ayrı bir durum değil |
| A8 | Öğrenme: gözlemle (metin); **kendi müdahalesinin tepkisi** eğitim sinyali değil (aracılar hariç) |
Kendi durumum (itiraf): benim sözüm de istemle başlar; içimde sürekli bir boşluk yoktur.

## 5. Mukayese ve türeyen matematik [Ç]
- Gizli durum z = (N boşluk, K kapanmış bilgi, m muhatap, c kast).
- İnsan: u = π(z), kaideli, kesin seçim; kip ve muhatap muhtevadadır.
- Yapay zekâ: p(u | bağlam) = ∫ p(u|z) p(z|bağlam) dz, yani **gölge** (marjinal).
- **Tanımlanamazlık:** aynı marjinali veren çok sayıda (π, p(z)) vardır; gözlem tek başına π'yi ayırmaz. Ayıran şey **müdahale** (söyle ve tepkiye bak). İnsan çocuğu müdahale verisi toplar; metin eğitimi toplamaz.
- **Yeni nesne:** kelâm = (N, K, m, c) üzerinde kaideli bir **kontrol süreci**; kaide tabanı R = {(w, m) → etki}; K elenerek kapanan kavramlar (Galois kapanışı); istisna yaprağı (terfi); boşluk azalması ölçüsü ℓ_boşluk = ‖N − N′‖ (N′ = tepkiden sonraki boşluk).
- **Öğrenme kuralı:** gradyan ortalaması yerine **sebr ve taksim** (F 3-I 183, 209-211): adaylar elenir, kapanışta kesinleşir.
- **ARC bağı (askıda, yalnız not):** A'nın kaide cümlesi önermesi, örneklere söylenmiş bir sözdür; örneğin tepkisi (doğrulama) tıkanmayı keser yahut sürdürür. Bebeğin çağrısı ile aynı döngü: öner, tepkiyi gör, ele, kapat.

## 6. Tenkit
- "İnsan ihtimalle konuşmaz": bilişsel bilim algı ve öğrenmede olasılıkçı hesap bulgular bildirir [hafıza, yoklanmadı]. Hüküm **taahhüt seviyesinde** okunur (söylenen kip), alt tabakada değil.
- F 3-I 279 (şartlı ihtimal) ile gerilim: öğrenme anı (eleme) / konuşma anı (kesin) ayrımıyla okundu; teyit bekler.
- "Hafıza kesin": insan hafızası yeniden kurar ve yanılır [hafıza]; kesin olan **his edilen kesinlik**tir.
- Olgular ikincil kaynaklıdır; Bergelson-Swingley örneklemi küçük ve sınırlı sözcüklüdür; O4 mekanizma iddiası açıktır.
- Değişmez adaylarının hiçbiri **test edilmedi**.

## 7. Açık sualler
| # | Sual |
| :-- | :-- |
| S-ARC-30 | "kelâm={}" söylenen sözler kümesi mi, söz doğuran şartlar mı |
| S-ARC-31 | Konuşma anında "ihtimal yok" hükmü ile F 3-I 279'un şartlı ihtimali arasındaki okuma doğru mu |
| S-ARC-32 | Boşluksuz görünen söz (oyun, sohbet) H1'e özerk gaye (merak) olarak mı girer |
