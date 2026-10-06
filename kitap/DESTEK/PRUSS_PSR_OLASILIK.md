# Pruss, "The Principle of Sufficient Reason and Probability" -- cevherler ve formüller

Kaynak: Alexander R. Pruss, *The Principle of Sufficient Reason and Probability*, Oxford Studies in Metaphysics (yayımlanacak); 17 sayfa. **Padişahın yüklediği PDF baştan sona okundu** (3-A 25-B; metin PyMuPDF ile çıkarıldı). Yazar çağdaş bir analitik filozoftur; makale **tâlî kaynaktır**. Atıflar makalenin kendi sayfa numarasıdır (s.1-17).

**Metin çıkarma notu:** PDF metninde üst ve alt çizgiler (ölçü uzantıları) ile üst indisler düştü; aşağıda hangi yerin bu yüzden yeniden kurulduğu işaretlendi.

## 1. Makalenin tezi, tek paragraf

Sıklıktan şansa çıkarımın (frekans → chance) geçerli olması, **sebepsiz (açıklamasız) hipotezlerin deneyle ayırt edilemeyen bir hipotez sınıfı** olduğunu gösterir; bu sınıfın öncülü keyfî olmadan düşük tutulamaz; öyleyse **a priori** reddedilmelidir: yerel sebep ilkesi. Yerel ilke küçük dünyalara uygulanınca küresel sonuçlara götürür; öyleyse küresel ilke gerekir. Hüküm cümlesi (s.13): "Açıklama olmayan yerde şans da yoktur."

## 2. İlkenin tanımı ve belirsizlikçilikle bağı (s.1)

```
PSR := □ ∀p ( p mümkin-doğru ise ∃ p'nin bir açıklaması )
        (necessarily every contingent truth has an explanation)
```

- Açıklama **belirleyici olmak zorunda değildir**; olasılıkçı ve düşük olasılıklı açıklama da açıklamadır (Salmon 1989; Jeffrey 1969). Bu, kuantum rastgeleliği itirazını PSR'nin **dışında** bırakır ve kitabın V.1.4.27'siyle (kanunlu rastgelelik) aynı yoldur.
- Rescher'in misali (s.1): uçak kazası araştırmacıları açıklamayı bulamadıklarından **açıklama yoktur** sonucunu çıkarmaz. Kitabın V.1.4.26'sının (bilgisizlikten yokluğa geçilmez) bağımsız teyididir.
- Yerel / küresel: bir LED'in yanması yerel; sonsuz bir olaylar gerisi veya koca evrenin bütün hâli yerel değildir (kesin tanım zordur).

## 3. Formüller ve tanımlar

### 3.1 Sıklıktan şansa (s.2)

```
Cp      : "paranın yazı gelme şansı p'dir" hipotezi
Örnek   : 1000 bağımsız atışta ≈ 750 yazı  ⟹  p ≈ 3/4
Büyük sayılar kanunu (BSK): n bağımsız ve aynı dağılımlı şanslı denemede
        sonucun sıklığı sonucun şansına yakın çıkması muhtemeldir.
Cp (p ≈ 3/4) altında ≈750 muhtemel; Cp (p uzak) altında ≈750 muhtemel değil.
```

### 3.2 Dart modeli (s.2-3)

```
Dart, daire biçimli hedefe düzgün rastgele atılır; hedef alanı T.
A ⊆ hedef işaretli bölge. Dart A'ya düşerse "yazı", düşmezse "tura".
Şans(yazı) = alan(A) / T          Cp ⟺ alan(A) = p·T
A ölçülemez ise alanı yoktur (sıfır alan değil: Lebesgue ölçüsü atayamaz).
Çerçeveleme: A1 ⊆ A ⊆ A2, A1 ve A2 ölçülebilir,
             alan(A1) = 0.74·T,  alan(A2) = 0.76·T
             ⟹ A'ya düşme sıklığı beklenen aralık ≈ [0.74, 0.76]
```

### 3.3 Doyurulmuş ölçülemez küme (s.3-4 ve Ek)

```
A ⊆ Ω doyurulmuş ölçülemezdir (saturated nonmeasurable) ⟺
   A'nın bütün ölçülebilir alt kümelerinin ölçüsü 0
   ve  bütün ölçülebilir üst kümelerinin ölçüsü 1
   (eşdeğeri: A'nın tümleyeninin bütün ölçülebilir alt kümelerinin ölçüsü 0).
Varlığı: Seçim Aksiyomu (AC) altında (Halperin 1951).
Çerçeveleme: ölçülebilir alt küme alanı 0, ölçülebilir üst küme alanı T
             ⟹ yalnız boş bilgi: sıklık ∈ [0, 1]
Pruss (2013), Teorem 1.3: I ⊊ [0,1] boş olmayan aralık ise
             {limit sıklık ∈ I} olayı da doyurulmuş ölçülemezdir.
Sonuç: sonsuz sayıda bağımsız denemede dahi sıklık hakkında olasılıkça bir şey söylenemez.
```

### 3.4 Bayes ve aralık değerli olasılık (s.5-6)

```
H : atışlar adil ve bağımsız        N : atışlar bağımsız doyurulmuş ölçülemez
E : n atışlık gözlem dizisi (örnek n=7: YTYYYTY)
P(E|H) = (1/2)^n          P(E|N) = [0, 1]  (aralık)

P(H|E) = P(E|H)·P(H) / ( P(E|H)·P(H) + P(E|N)·P(N) )

Üst uç  (P(E|N)=0 konur):  P(E|H)P(H) / (P(E|H)P(H) + 0·P(N)) = 1
Alt uç  (P(E|N)=1 konur):  P(E|H)P(H) / (P(E|H)P(H) + 1·P(N))  ≤  (1/2)^n / P(N)

⟹  P(H|E) aralığı  [ (1/2)^n / P(N) , 1 ]  aralığını kapsar.
n → ∞ iken alt uç 0'a gider (P(N) > 0 ve sonsuz küçük değilse):
   Bayesçi IRAKSAMA — delil biriktikçe H'nin aralığı [0,1]'e yayılır.
```

Dipnot 4: aralık değerli olasılık, bir **olasılık fonksiyonu ailesi** sayılıp Bayes teoremi her üyeye uygulanarak sağlamlaştırılır; ailenin üyeleri yalnız P(E|N) değerinde ayrılır.

### 3.5 Sebepsiz hipotez ve üç şık (s.7-8)

```
Bir parayı atış: "hiçbir açıklama yok" hipotezi H0.
Tek keyfî olmayan atama: simetri / ilgisizlik ilkesi ⟹ Şans(yazı | H0) = 1/2,
   ve her sabit n'li dizi için 2^(−n).  Bu, aynı tahmini yapan
   "bağımsız 1/2 şanslı atışlar" hipoteziyle ayırt edilemez.
Üç şık (olasılık çerçevesi içinde):
   (a) H0 altında kesin sayı çıkar  ⟹ aynı sayıyı veren açıklayıcı şans hipotezinden ayırt edilemez
   (b) hiç olasılık çıkmaz          ⟹ doyurulmuş ölçülemez; sıklık hakkında hiçbir tahmin yok
   (c) aralık [a,b] çıkar:  BSK'ya göre limit sıklık hemen hemen kesin [a,b] içindedir
         ve daha fazlası söylenemez (Pruss 2013, Teorem 1.3);
         H0 en iyi tam aralık [0,1] verir (ileri sürülmüştür, gösterilmemiştir).
```

### 3.6 Ters çevirme (s.9-10)

Gözlem hipotez üzerinde olasılıksızsa hipotezi zayıflatıyor sayılırsa, sebepsiz hipotez için hem E hem değili E zayıflatma delili olur. Bu **ancak hipotez imkânsızsa** çelişkisizdir. (Dipnot 6: imkânsızlık, E'den başlayan ve değili E'den başlayan ayrı iki argümanla gösterilebilir.)

### 3.7 Aykırı yerçekimi örneği (s.8)

```
Newton:  F = G·m1·m2 / r²
Aykırı:  F = G·m1·m2 / r²  +  10^(−100)
Deneyle ayırt edilemez; öncül yine de düşük tutulur, aksi hâlde Newton kuvveti sonuçlanamazdı.
Pruss'un karşılaştırması: sebepsiz hipotez "daha sade"dir, bu yüzden benzetme tam oturmaz;
   fakat iki durumda da düşük öncülün tek gerekçesi "yoksa bilim yapılamazdı" olur.
```

## 4. Yerelden küresele (s.10-13)

- **Ceviz dünyası** (s.10): sonlu geçmişli, bütün mümkin bileşeni tek ve değişmeyen sıradan bir ceviz ile parçalarından ibaret dünya. Yerel ilke cevize uygulanınca cevizin açıklaması cevizin parçalarından olamaz; dışarıda mümkin bir şey yoksa açıklama **zorunlu bir varlık veya zorunlu bir ilke** olmalıdır.
- **S5:** `◇□p ⟹ □p` (zorunlu olması mümkün olan zorunludur). Ceviz dünyasında zorunlu olan, gerçek dünyada da zorunludur. Bu adım S5'e dayanır; S5'i reddetmek de ağır bir metafizik taahhüttür.
- **van Inwagen itirazı** (s.10-11): bütün mümkin doğruların bağlacının açıklaması ya mümkindir (o zaman kendi kendini açıklar) ya zorunludur (zorunlu mümkini açıklayamaz). Pruss: "açıklama, açıklananı gerektirir" ilkesi olasılıkçı açıklamada reddedildiğinden mesele yalnız **van Inwagen İlkesi (VIP)**: zorunlu bir doğru mümkin bir doğruyu açıklayamaz.
- **Dipnot 8:** zorunlu varlığın sonsuz geriye mümkin hâller dizisi olarak kurulması yerel ilkeyi doyurur fakat ek taahhüt ister ve "mümkin dünyada yalnız cevizle sonlu sayıda başka mümkin hâl" sezgisine ters düşer.
- **Zimmerman'ın önerisi** (s.11): yerellik evren büyüklüğüne göre alınırsa ceviz tek başına iken açıklama ister, çok şeyin biri iken istemez; bu makul değildir.
- **Küresel olasılıklar** (s.12-13): başlangıcı olmayan fakat sonlu geçmişli evren (zaman aralığı `{t : t > 0}`; Grünbaum 1993) yerel ilkeye girmez. Russell'ın beş dakikalık evreni ve "bir dakika geriye uzanan ışık konisi" hipotezi, şans ve sadelikle Büyük Patlama hipotezinden ayrılamaz.
- Dipnot 9: Hume (Dialogues, IX) sonsuz nedensel gerinin üyeleriyle açıklandığını savunur; Pruss (2006, §3.1.4) **topun sonsuz uçuşu** düşünce deneyiyle bunu makul bulmaz (kendi kitabı **okunmadı**).

## 5. PSR'ye uyan sapkın hipotezler (s.13)

Zorunlu bir varlık "bilim düşmanı" ise ve görünüşü yanıltan bir evren yaratıyorsa, kısıtlı PSR buna engel olmaz. Pruss bunu **sadelikle** ayırır: bilim düşmanı hipotezinde serbest parametreler çoktur ("ne kadar düşman, hangi bakımdan, ne kadar güçlü"); bilim sever tarafta literatürde **kanonik** bir hipotez vardır: azamî güç, azamî bilgi ve her güzel şeyi güzelliği oranında seven mükemmel varlık (teist hipotez). Buna ek olarak **olasılıkçı değerci hipotez**: evrenin ortaya çıkma şansı değeriyle orantılıdır.

## 6. Sonuç (s.13-14)

```
Açıklama olmayan yerde şans yoktur.
Şans olmayan yerde keyfî olmayan olasılık zordur.
Sadelik ve ilgisizlik her durumu kurtarmaz.
⟹ yalnız yerel değil, küresel bir PSR gerekir.
```

Ek: şansın klasik olasılık aksiyomlarına bağlı kalmaması gerekebilir (gerekçeye göre hareket eden fâilin eğilimi sayıya dökülemez; "bütün mümkin dünyalar kümesi" olmayabilir, Pruss 2001). Fakat "açıklama olmayan yerde şans yoktur ve şans doğurmayan hipotezler a priori reddedilir" ana hükmü sürer.

## 7. Ek: teoremler (s.14-16)

```
Teorem 1 (AC varsayımıyla): [0,1)'in doyurulmuş ölçülemez alt kümelerinin sayısı
         = [0,1)'in bütün alt kümelerinin sayısı  (= 2^c).
Önsav 1: S doyurulmuş ölçülemez ve S Δ B Lebesgue ölçüsü 0 ise B de doyurulmuş ölçülemezdir.
         (Δ simetrik fark: (S−B) ∪ (B−S))
Teorem 1'in kanıtı: Cantor üçte-bir kümesi C ⊆ [0,1) ölçüsü 0'dır ve |C| = c.
         Bir doyurulmuş ölçülemez S sabitlenir (Halperin 1951); C'nin her A alt kümesi için
         S_A := (S − C) ∪ A  kurulur; S_A Δ S ⊆ C olduğundan Önsav 1 ile S_A de doyurulmuş
         ölçülemezdir; S_A'ların sayısı C'nin alt kümelerinin sayısı kadardır.
Sonuç:   doyurulmuş ölçülemez kümelerin sayısı = [0,1)'in ölçülebilir alt kümelerinin sayısı.
         (⟹ doyurulmuş ölçülemez hipotezlere "az sayıdadır" diye düşük öncül verilemez; s.5)
Model:   bağımsız olaylar E1,…,En çarpım uzayında  Ek = { ⟨ω1,…,ωn⟩ : ωk ∈ Uk }.
         N(ω) = #{ k : ω ∈ Ek }  (gerçekleşen olay sayısı).
Teorem 2: E1,…,En doyurulmuş ölçülemez; J ⊆ {0,…,n} boş olmayan öz altküme ise
         N_J = { ω : N(ω) ∈ J } da doyurulmuş ölçülemezdir.
         ⟹ gerçekleşen olay sayısı hakkında olasılıkça önemsiz olmayan hiçbir şey söylenemez.
Kanıt çizgisi: Ψk = 1_{Uk};  (Yk)_* = 0,  (Yk)^* = 1 (minimal ölçülemez majorant ve maksimal minorant,
         Pruss 2013, Önerme 1.2);  P_k ve P^k, P'yi genişleten ve P_k(Uk)=0, P^k(Uk)=1 olan
         ölçülerdir (Pruss 2013, Lemma 1.5).
         j ∈ J için Q = P^1 ⊗…⊗ P^j ⊗ P_{j+1} ⊗…⊗ P_n  ⟹  Q(N_J) = 1.
         ℓ ∉ J için R = P^1 ⊗…⊗ P^ℓ ⊗ P_{ℓ+1} ⊗…⊗ P_n  ⟹  R(N_J) = 0.
         P'nin biri 0, öbürü 1 veren iki genişlemesi olduğundan N_J doyurulmuş ölçülemezdir
         (Pruss 2015, Lemma 2.3).
```

**Basım kusurları (çıkarım; kaynakla karşılaştırılmadı):**
1. Teorem 1'in kanıtında basılı `S_A = (S − A) ∪ A` ifadesi `S`'e eşittir; anlam gereği `(S − C) ∪ A` olmalıdır (yukarıdaki yazım).
2. Teorem 2'nin kanıtında "`R(Ek) = 1` eğer `k ≤ ℓ`, aksi hâlde `R(Ek) = 1`" yazılıdır; ikincisi `0` olmalıdır.
3. PDF'te üst ve alt çizgi bilgisi düştüğü için `P_k` (alt) ve `P^k` (üst) ayrımı yukarıda anlamdan kuruldu.

## 8. Kitaba haritalama

| Pruss | Kitap |
| :-- | :-- |
| PSR olasılıkçı açıklamayla bağdaşır | V.1.4.27 (kanunlu rastgelelik) |
| Rescher: kazada açıklama aranır, yok denmez | V.1.4.26 |
| "Açıklama olmayan yerde şans da yoktur" | V.1.4.38 örnekleyici cevabının biçimsel dayanağı |
| Sebepsiz hipotez a priori reddedilir | veritabanı: `p_apriori_ret`, `Q00.c2/U07#2` |
| Bayesçi ıraksama | veritabanı: `t_bayes_aralik` |
| Ceviz dünyası, S5 | **henüz veritabanında yok** (sonuç "zorunlu varlık veya ilke", Vâcib değil) |
| Mükemmel varlık = kanonik hipotez | V.2'ye aittir, V.1'e girmez |

## 9. Tenkit: bu delil burhan seviyesine nereden yükselir, nerede yükselmez

Padişahın kanaati: "burhan seviyesinde ispatlanacak". Ölçümüz: veritabanında bu yol **ZAN-I GÂLİB** çıkıyor, çünkü iki öncül zayıf sayıldı. Boşluklar:

- **G1 (`p_sebepsiz_sans_yok`, şık c):** sebepsiz hipotezin "en fazla [0,1]" vermesi **ileri sürülmüştür, gösterilmemiştir.** Teklif (çıkarım, Pruss söylemiyor): dar aralık `[a,b]` veren bir hipotez bir **kanun** ileri sürmüş olur; "neden `[a,b]`" sorusunun cevabı kanundur ve kanun açıklamadır; böylece (c) şıkkı sebepsizliğe değil kanunlu rastgeleliğe iner. Bu yapılırsa G1 teoreme çevrilebilir. Henüz yapılmadı.
- **G2 (`p_apriori_ret`):** hasmın "bilim yapılabilsin diye düşük öncül" yolu Pruss'ça tatmin edici bulunmaz fakat **çürütülmez** (s.8-9: "iki tatminsiz durumdansa biri iyidir"). Bu bir tercih gerekçesidir, çürütme değildir. Burhan için bu yolun kendi kendini yıktığı veya kendi gerekçesini istediği gösterilmelidir; gösterilmedi.
- **G3 (çerçeve):** üç şık, klasik veya aralıklı olasılık çerçevesi içinde hasırdır; Pruss s.14'te çerçevenin gevşetilebileceğini kendisi ekler. Çerçeve dışı hasım hasırla kuşatılmaz.
- **G4 (AC):** Teorem 1-2 Seçim Aksiyomuna dayanır; genel "sebepsiz hipotez" kolu (b. 2.3) bu aksiyomdan bağımsız kurulur fakat G1'e yaslanır.
- **G5 (küreselleme):** S5, ceviz dünyasının mümkünlüğü ve ilkenin metafizik zorunlu sayılması gerekir; sonuç **"zorunlu varlık veya zorunlu ilke"**dir. Kitabın `Q02.c1`'i (varlığı zâtından olan Vâcib) için bu **tek başına yetmez**; "ilke" kolunun varlık kolundan ayrılması ayrı delil ister.
- **G6 (sapkın hipotezler):** bilim düşmanı zorunlu varlık sadelikle elenir; sadelik **zan** verir.

Dürüst hüküm: bu makale, sebep ilkesine karşı **kuvvetli bir ilzam** ve **biçimsel bir teorem zinciri** verir; zinciri **burhan** yapmak için G1 ve G2'nin kapatılması gerekir. Bu iş açıktır ve kapatılabilir olup olmadığı **bilinmiyor.**

**Güncelleme:** G1 ve G2 için deneme yapıldı; sonuç `PRUSS_G1_G2_DENEME.md`dedir (G1 daraltılmış hâliyle kapandı, G2 kapanmadı).
