# mizan — mantık usulleri motoru

Risalelerdeki mantık bahislerinin **çalışan** karşılığı. Bu modülde hiçbir
hüküm elle yazılmamıştır: geçerli kıyas darbları sayılarak, çerçeve
karşılıkları 512 çerçeve taranarak, klasik/sezgisel ayrımı ispat araması
yapılarak **türetilir**. Kütüphane kendi iddialarının sağlamasını kendisi
yapar.

| modül | satır | ne yapar |
|---|---:|---|
| `onerme.py` | 326 | hash-consed formül düğümleri + bit-paralel doğruluk tablosu |
| `kiyas.py` | 311 | kıyas darbları, 256 monadik modelle tam karar |
| `cikarim.py` | 459 | Hilbert denetçisi, klasik LK, sezgisel G4ip |
| `kiplik.py` | 396 | Kripke çerçeveleri, K/T/4/5/B/D, deontik kipler, LTL |
| `cokdegerli.py` | 368 | t-normlar, kalıntılar, üç değerli mantıklar, syādvāda |
| `altyapisal.py` | 491 | yapısal kuralı açılıp kapanan hesap, relevans, kuantum mantık |
| `istikra.py` | 470 | Laplace ardışıklığı, ICP, temsil, Nyāya, Stoa, Mill |
| `munazara.py` | 312 | men'/nakz/muâraza oyunu, Gazâlî yakîn mîzânı |
| `test_mizan.py` | 480 | 84 test — sözleşme / riyâzî hüviyet / çapraz sağlama |

## Ölçülen neticeler

Aşağıdakilerin hepsi bu depoda çalıştırılarak elde edildi; hiçbiri
ezberden yazılmadı.

**Kıyas.** 4 şekil × 64 darb = 256 terkip tarandı. Varlık faraziyesi
olmadan **15**, üç terimin de boş olmadığı farz edilirse **24** darb
geçerli; fark tam olarak **9**. Her darbın asgari ihtiyacı ayrıca
hesaplandı: Barbari/Celaront/Camestros/Cesaro/Camenos **S**'nin,
Darapti/Felapton/Fesapo **M**'nin, **Bamalip ise P**'nin boş olmamasını
ister. (Son madde T79 tashihinin makine sağlamasıdır.)

**Çıkarım.** LK ile doğruluk tablosu **3000 rastgele formülde** birebir
uyuştu (315'i totoloji, 0.06 s). Aynı örneklemde G4ip'in ispatladığı
**203** formülün **203'ü** LK'de de ispatlandı — LJ ⊆ LK ölçüldü,
varsayılmadı. Peirce, üçüncü
hâlin imtinâı, ¬¬A→A ve De Morgan(→) klasikte geçerli sezgiselde değil;
A→¬¬A, ex falso, modus tollens, De Morgan(←) ikisinde de geçerli.

**Kiplik.** 3 dünyalı **512 çerçevenin tamamı** tarandı; altı karşılığın
altısı da **tam isabetli** (şartı sağlayan her çerçevede geçerli, sağlamayan
hiçbirinde değil): K 512/512, T 64/64, 4 171/171, 5 39/39, B 64/64,
D 343/343. D, seri çerçevelerde çelişkili ödevi **0** vakada bırakıyor;
seri olmayanlarda 169 vakada bırakıyor.

**Çok değerli.** Dokuz t-normun dokuzu da bütün aksiyomları sağlıyor.
Dört kalıntı çiftinde **0 ihlal**. T89'un sağlaması: Łukasiewicz imâsı
`⊗ = max(0, a+b−1)` ile kalıntı özdeşliğini sağlıyor, `⊗ = min` ile
**1330 yerde bozuluyor** — ilk ihlal `(0.05, 0.05, 0.0)`. LP'de
`A, ¬A ⊨ B` **yanlış** (belirlenmiş değerler `{b,1}`), yalnız `{1}`
belirlenmişse doğru; tanık `(A,B) = (b,0)`. Syādvāda'nın 7 modu tam ve
tekrarsız (`2³−1`).

**Yapısal-altı.** `A ⊸ (B ⊸ A)` yalnız zayıflatma varken, `A ⊸ (A⊗A)`
yalnız büzülme varken ispatlanıyor; `A ⊗ (A⊸B) ⊢ B` dördünde de. Kuantum
mantıkta ℝ² üzerinde `A∧(B∨C)` boyut 1, `(A∧B)∨(A∧C)` boyut 0 — dağılma
kırılıyor; ama `(A∧B)∨(A∧C) ≤ A∧(B∨C)` eşitsizliği **daima** sağlanıyor
ve ortomodüler kanun 200 rastgele denemede **0 ihlal** veriyor. (T93.)

**İstikrâ.** Laplace kaidesi n=1000'de 0.999002 veriyor; hiçbir sonlu
`n` için 1'e ulaşmıyor — "eksik istikrâ yakîn vermez" hükmünün nicel
karşılığı. ICP iki ayrışık ortamda sahte yordayıcıyı eleyip `{X0}`
veriyor; ortamlar ayrışmazsa **hüküm vermiyor** (usulün kendisi budur,
kusuru değil). Temsilde sirke şaraba kaba benzerlikte daha yakın (0.75 v
0.40) ama illette hüküm nebîze geçiyor, sirkeye geçmiyor. Stoa'nın beş
anapodeiktosunun beşi de doğruluk tablosuyla doğrulandı.

**Münâzara.** Men' edilen öncülün yakîni sıfırlanıyor, müstakil delille
ispat edilince geri geliyor; tekrâr-ı men' reddediliyor; geçerli kıyas
nakzedilemiyor, geçersiz olan nakzedilip şâhidi gösteriliyor.

## Formüllerin kuruluşuna dair üç not

**Doğruluk sütunu katlanarak üretilir.** `k`. değişkenin sütunu
`sonuc |= sonuc << genişlik` ile ikişer katlanır. Naif tekrar `n=20, k=0`
için 524 288 büyük tam sayı işlemi ister; katlama `n−k` işlem ister.
Netice birebir aynıdır ve `n = 1..8` için bit bit kaba kuvvetle
karşılaştırılarak sınanır (`test_degisken_sutunu_kaba_kuvvetle_birebir_ayni`).

**Yakîn mîzânında minimum kullanılır, çarpım değil.**
`Yakîn(Q) = min_i Yakîn(P_i) · 𝟙[şekil geçerli]`. Minimum idempotenttir:
aynı öncülü iki kere saymak neticeyi zayıflatmaz ve **zincirin uzunluğu
tek başına yakîni düşürmez**. Çarpım seçilseydi kat'î öncüllerden kurulu
uzun bir ispat da kaçınılmaz olarak sıfıra giderdi — bu, mîzânın tartmak
istediği şey değildir.

**Derinlik sınırı bir bütçedir.** `altyapisal.Hesap` içindeki ispat
araması derinlikle sınırlıdır; "ispatlanamaz" hükmü ancak o bütçe altında
geçerlidir. Bu yüzden olumsuz sonuçlar **kalan bütçeye göre**
anahtarlanır, olumlu sonuçlar ise bütçesiz saklanır (bulunmuş ispat her
bütçede ispattır). `test_onbellek_hukmu_degistirmiyor` bunu paylaşımlı ve
taze önbellekleri karşılaştırarak sınar.

## Hız ve bellek

`python3 -m mizan.<ad>` tam raporlarının süreleri:

| modül | süre |
|---|---:|
| `kiyas` | 0.030 s |
| `cikarim` | 0.027 s |
| `kiplik` | 0.198 s |
| `cokdegerli` | 0.054 s |
| `altyapisal` | 0.229 s |
| `istikra` | 0.044 s |
| `munazara` | 0.042 s |

Test takımının tamamı **0.76 s**. Yorumlayıcı dahil azamî yerleşik bellek
~10 MB; `altyapisal` numpy yüklediği için ~33 MB'a çıkar (bu numpy'nin
kendi maliyetidir, modülün veri yapılarının değil).

Hızın kaynağı üç yerdedir ve üçü de doğruluktan taviz vermez:

1. **Bit paralelliği** — bir formülün 2ⁿ değerlemedeki doğruluğu tek bir
   büyük tam sayıda taşınır; her mantık bağlacı düğüm başına **bir**
   bigint işlemidir. Değerlemeler üzerinde döngü yoktur.
2. **Hash-consing** — yapısal paylaşım; eşitlik `is` ile O(1), ve
   memoizasyon düğüm kimliğiyle anahtarlanır. `ve(A,B) is ve(A,B)`.
3. **Değişmez ardışıklara memoizasyon** — LK'nin bütün kuralları tersinir
   olduğundan geri izleme yoktur; çözülmüş her ardışık saklanır.

## Çalıştırma

```
python3 -m mizan.kiyas          # ve diğer yedi modül
python3 -m pytest mizan/test_mizan.py -q
```
