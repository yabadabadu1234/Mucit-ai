# Talebe Notu — Riemann 1859, Muayyen Bir Kemmiyetten Küçük A'dâd-ı Evveliyyenin Adedi

> **Kaynak:** [tercume/eserler/11_riemann_1859_adad_i_evveliyye.md](../tercume/eserler/11_riemann_1859_adad_i_evveliyye.md).
> **İşaretler:** ⟹ "bundan şu lâzım gelir" · ⟸ "çünkü" · **[N]** not sahibinin ilâvesidir, tercümede yoktur · **[M…]** mütercim kaydına atıftır.
> **Düstur kaidesi:** Düsturlarda harf yoktur, kelime vardır. Adlar tercümenin **İsimler cedveli** ile aynıdır, ki talebe notla tercüme arasında gidip gelebilsin; cedvel bu notun sonunda da vardır. Hesap işaretleri (cem', tarh, zarb, taksim, kuvvet, tamâmî ∫, mecmû' ∑, hâsıl-ı zarb ∏) ve rakamlar kalır.

---

## Bab 0 — Bir bakışta bütün risâle

**Gaye:** Bir **hudut**tan küçük a'dâd-ı evveliyyenin adedini, takrîbî değil, **tam** bir düsturla vermek.

**Yolun iskeleti (altı halka):**

1. *Euler köprüsü:* a'dâd-ı evveliyye üzerinde bir hâsıl-ı zarb = bütün tam a'dâd üzerinde bir mecmû'. Bu, evvelîlerden tahlîle geçilen kapıdır. Böylece Zeta tâbisi doğar.
2. *Yayma:* Zeta tâbisini, düsturunun mütekārib olmadığı yerlere de **tamâmî yoluyla** yaymak ⟹ Zeta bütün mürekkeb düzlemde tanımlı olur (bir tek noktada sonsuzlaşır).
3. *Ayna:* Zeta, mütehavvil ile (1 − mütehavvil) arasında bir **aynalık** taşır; ayna çizgisi hakîkî cüz'ü ½ olan doğrudur.
4. *Tekmîl-zeta ve cezrleri:* Aynalığı açık gösteren, hiçbir yerde sonsuzlaşmayan **Tekmîl-zeta** tâbisi kurulur; bütün mühim bilgi onun **cezrlerindedir**. Riemann bu cezrlerin hepsinin ayna çizgisinde olmasını "pek muhtemel" görür: **Riemann farziyesi**.
5. *Tersine çevirme:* Zeta'nın logaritmasından, evvelîleri kuvvetleriyle beraber sayan **Kuvvet-adedi** tâbisi Fourier kaziyyesiyle geri alınır.
6. *Sarîh düstur:* Kuvvet-adedi = Logaritmik-tamâmî − (cezrlere bağlı dalgalar) + (küçük cüz'ler); Möbius tersine çevirmesiyle **Evvelî-adedi** bulunur.

> **Cevher-i küll:** *Evvelîlerin düzensiz görünen dağılışı, Zeta'nın cezrlerinin ördüğü dalgaların toplamıdır.* Logaritmik-tamâmî "ortalama sıklık"tır; her cezr bir **dalga** ekler; evvelîlerin yer yer sıklaşıp seyrekleşmesi bu dalgaların eseridir.

---

## Bab 1 — Künye ve mukaddime (tercümenin başı, aslın ilk sahifesi)

- **Asıl:** *Ueber die Anzahl der Primzahlen unter einer gegebenen Grösse*, Almanca. Berlin Kraliyet Prusya İlimler Akademisi Aylık Zabıtları (*Monatsberichte*), Teşrîn-i sânî 1859, sahife 671–680.
- **Tercümenin esası:** *Bernhard Riemann's Gesammelte Mathematische Werke und Wissenschaftlicher Nachlass*, Heinrich Weber neşri, Richard Dedekind iştirakiyle, Leipzig, Teubner, 1892, sahife 145–153; bunun David R. Wilkins (Trinity College, Dublin) tarafından 1998'de yapılmış harfi harfine dizgisi.
- **Telif:** Müellif 1866'da vefat etti ⟹ her memlekette açık.
- **Vesile:** Akademi Riemann'ı **muhabir âza** seçmiştir; Riemann şükrânını bir tetkik arz ederek gösterir. Mevzûyu seçmesinin sebebi: *Gauss* ile *Dirichlet*'nin bu mevzûya uzun müddet gösterdiği alâka.
- **[N] Tarihî yer:** Riemann'ın nazariye-i a'dâda dair **tek** risâlesidir; on sahifeden ibarettir; bugünkü tahlîlî nazariye-i a'dâdın kurucu metni sayılır.

---

## Bab 2 — Euler köprüsü: Zeta tâbisinin doğuşu

**Euler'in tesbiti** (Riemann'ın hareket noktası):

> ∏ [her evvelî için] 1 ÷ (1 − 1 ÷ evvelî üssü mütehavvil) = ∑ [her adet için] 1 ÷ adet üssü mütehavvil

- Sol taraf yalnız **evvelîler** üzerindedir; sağ taraf **bütün tam a'dâd** üzerindedir.
- **[N] Sebep:** Soldaki her mazrûb bir hendesî silsiledir: 1 + evvelî üssü (eksi mütehavvil) + evvelî üssü (eksi 2 × mütehavvil) + … Bunlar çarpılınca her tam adet, evvelî mazrûblarına **tek bir tarzda** ayrıldığı için sağ tarafta **bir ve yalnız bir kere** çıkar. Euler köprüsünün dayanağı, tam a'dâdın evvelîlere tek tarzda ayrılmasıdır. Riemann bunu söylemez; malûm sayar.
- İki tarafın ortak kıymetine **Zeta(mütehavvil)** denir; mütehavvil **mürekkeb**dir.
- **Kusur:** İki ifade de ancak **hakîkî cüz > 1** iken mütekāribdir. ⟹ Zeta'yı her yerde muteber kılan bir ifade lâzımdır. Riemann bunun "kolayca bulunabileceğini" söyler.

---

## Bab 3 — Yayma: Zeta'yı bütün düzleme genişletmek

**Birinci adım: Gauss-zarbı tamâmîsi** [M1]

> ∫ [sıfırdan sonsuza] Neper üssü (− adet × kemmiyet) × kemmiyet üssü (mütehavvil − 1) × d kemmiyet = Gauss-zarbı(mütehavvil − 1) ÷ adet üssü mütehavvil

Gauss-zarbı, faktöriyelin kesirli ve mürekkeb kıymetlere yayılmışıdır: tam adet için Gauss-zarbı(adet) = 1 × 2 × 3 × … × adet. Bugünkü "gamma tâbisi" bunun bir adım kaydırılmışıdır.

⟹ bütün adetler üzerinden toplanınca (hendesî silsile ile):

> Gauss-zarbı(mütehavvil − 1) × Zeta(mütehavvil) = ∫ [sıfırdan sonsuza] kemmiyet üssü (mütehavvil − 1) ÷ (Neper üssü kemmiyet − 1) × d kemmiyet

Bu da hâlâ yalnız hakîkî cüz > 1 iken muteberdir.

**İkinci adım: sonsuzdan sonsuza dolaşan yol** [M2]

Tamâmî, müsbet hakîkî mihver boyunca **sonsuzdan gelip sıfırı müsbet istikamette dolaşan ve yine sonsuza dönen** yol üzerinden alınır (bugünkü adı: Hankel yolu). Yolun içinde sıfır olmalı, tâbinin **başka hiçbir inkıtâ' noktası** olmamalıdır.

- Eksi kemmiyetin kuvveti çok kıymetlidir: (− kemmiyet) üssü (mütehavvil − 1) = Neper üssü [(mütehavvil − 1) × logaritma(− kemmiyet)]; logaritma, menfî kemmiyet için **hakîkî** olacak şekilde tayin edilir.
- Yolun gidiş kolunda bu logaritmaya − dâire-nisbeti × mevhûm-vâhid, dönüş kolunda + dâire-nisbeti × mevhûm-vâhid eklenir **[N: bu izah not sahibinindir]** ⟹ iki kol birbirini götürmez; tercümedeki (Neper üssü (− dâire-nisbeti × mütehavvil × mevhûm-vâhid) − Neper üssü (dâire-nisbeti × mütehavvil × mevhûm-vâhid)) **fark mazrûbu** doğar, ki − 2 × mevhûm-vâhid × ceyb(dâire-nisbeti × mütehavvil)'dir:

> 2 × ceyb(dâire-nisbeti × mütehavvil) × Gauss-zarbı(mütehavvil − 1) × Zeta(mütehavvil) = mevhûm-vâhid × ∫ [sonsuzdan sonsuza] (− kemmiyet) üssü (mütehavvil − 1) ÷ (Neper üssü kemmiyet − 1) × d kemmiyet

**Neticeler** (⟸ sağ taraf **her** mürekkeb mütehavvil için mütenâhî ve tek kıymetlidir):

1. Zeta **tek kıymetlidir**.
2. Zeta, **1 müstesnâ**, bütün mütenâhî mütehavvillerde mütenâhîdir. *(1'de sonsuzlaşır; [N] bu, bütün tam a'dâdın terslerinin mecmû'unun ıraksak olmasının, yâni evvelîlerin sonsuz çokluğunun tahlîlî yüzüdür.)*
3. Zeta, mütehavvil **menfî bir çift adet** olduğunda **sıfır** olur. *(Bunlara bugün "âdî sıfırlar" denir.)* **[N]** Riemann sebebini açmaz; tam adet mütehavvillerde yol tamâmîsi sıfır etrafındaki tek bir kalıntıya iner ve oradaki emsaller (Bernoulli a'dâdı) tek sıralılarda sıfırdır.

> **Cevher:** *Mütekārib olmayan bir silsileyi bırakıp, aynı kıymeti veren ve her yerde muteber olan bir **tamâmî** bulmak.* Yayma işi budur; Zeta artık silsileden değil, tamâmîden tanınır.

---

## Bab 4 — Ayna: tâbiî muâdele [M3]

**Yol:** Hakîkî cüz **menfî** iken yol dışarıya doğru, bütün öbür mürekkeb kıymetleri kuşatacak şekilde (menfî istikamette) genişletilir ⟸ mikyâsı sonsuz büyük kıymetler üzerindeki tamâmî orada sonsuz küçüktür. Bu geniş sahanın içinde tâbi yalnız **kemmiyet = ± 2 × dâire-nisbeti × mevhûm-vâhid'in tam katları** noktalarında munkatı'dır ⟹ tamâmî, bu noktalar etrafındaki küçük tamâmîlerin mecmû'udur. Her birinin kıymeti:

> (− adet × 2 × dâire-nisbeti × mevhûm-vâhid) üssü (mütehavvil − 1) × (− 2 × dâire-nisbeti × mevhûm-vâhid)

⟹

> 2 × ceyb(dâire-nisbeti × mütehavvil) × Gauss-zarbı(mütehavvil − 1) × Zeta(mütehavvil) = (2 × dâire-nisbeti) üssü mütehavvil × ∑ [her adet için] adet üssü (mütehavvil − 1) × [(− mevhûm-vâhid) üssü (mütehavvil − 1) + mevhûm-vâhid üssü (mütehavvil − 1)]

Sağdaki mecmû', **Zeta(1 − mütehavvil)**'dir ⟹ Zeta(mütehavvil) ile Zeta(1 − mütehavvil) birbirine bağlanır. Gauss-zarbı'nın malûm hassalarıyla en temiz şekli:

> **Gauss-zarbı(mütehavvil ÷ 2 − 1) × dâire-nisbeti üssü (− mütehavvil ÷ 2) × Zeta(mütehavvil)**, mütehavvil yerine (1 − mütehavvil) konunca **değişmez**.

- **Ayna çizgisi:** hakîkî cüz'ü **½** olan mütehavviller ⟸ mütehavvil ile (1 − mütehavvil) bu çizgiye göre birbirinin aynasıdır.
- ⟹ Hakîkî cüz > 1 sahasında bilinen her şey, aynalıkla hakîkî cüz < 0 sahasına taşınır. Bilinmeyen tek şerit, hakîkî cüz'ü **0 ile 1 arası**dır. **[N]** Bugün buna "kritik şerit" denir.

---

## Bab 5 — İkinci burhan: Jacobi-mecmûu ile aynalığı apaçık göstermek

**Fikir:** Aynalık "beni sevk etti": silsilenin her haddine Gauss-zarbı(mütehavvil − 1) yerine **Gauss-zarbı(mütehavvil ÷ 2 − 1)** sokulur.

> (1 ÷ adet üssü mütehavvil) × Gauss-zarbı(mütehavvil ÷ 2 − 1) × dâire-nisbeti üssü (− mütehavvil ÷ 2) = ∫ [sıfırdan sonsuza] Neper üssü (− adet × adet × dâire-nisbeti × kemmiyet) × kemmiyet üssü (mütehavvil ÷ 2 − 1) × d kemmiyet

**Jacobi-mecmûu** tarif edilir [M4'te "teta mecmû'u"]:

> Jacobi-mecmûu(kemmiyet) = ∑ [adet birden sonsuza] Neper üssü (− adet × adet × dâire-nisbeti × kemmiyet)

⟹

> Gauss-zarbı(mütehavvil ÷ 2 − 1) × dâire-nisbeti üssü (− mütehavvil ÷ 2) × Zeta(mütehavvil) = ∫ [sıfırdan sonsuza] Jacobi-mecmûu(kemmiyet) × kemmiyet üssü (mütehavvil ÷ 2 − 1) × d kemmiyet

**Jacobi'nin tahvil düsturu** (Jacobi, *Fundamenta nova theoriae functionum ellipticarum*, Königsberg 1829, sahife 184) [M4]:

> 2 × Jacobi-mecmûu(kemmiyet) + 1 = kemmiyet üssü (− ½) × [2 × Jacobi-mecmûu(1 ÷ kemmiyet) + 1]

Tamâmî **1'de ikiye bölünür**; sıfırdan bire kadar olan kısım, tahvil düsturuyla birden sonsuza taşınır ⟹

> Gauss-zarbı(mütehavvil ÷ 2 − 1) × dâire-nisbeti üssü (− mütehavvil ÷ 2) × Zeta(mütehavvil) = 1 ÷ [mütehavvil × (mütehavvil − 1)] + ∫ [birden sonsuza] Jacobi-mecmûu(kemmiyet) × [kemmiyet üssü (mütehavvil ÷ 2 − 1) + kemmiyet üssü (− (1 + mütehavvil) ÷ 2)] × d kemmiyet

**Neden aynalık apaçıktır? [N]** Mütehavvil yerine (1 − mütehavvil) konunca: 1 ÷ [mütehavvil × (mütehavvil − 1)] değişmez; köşeli parantezdeki iki üs **yer değiştirir**. ⟹ Sağ taraf aynen kalır. Birinci burhanda hesapla bulunan ayna, burada düsturun **şeklinden** okunur.

> **Cevher:** *Zeta'nın aynalığı, Jacobi-mecmûunun kemmiyet ile (1 ÷ kemmiyet) arasındaki aynalığının yansımasıdır.* Biri öbürünün sûretidir.

---

## Bab 6 — Tekmîl-zeta: sonsuzlukları temizlenmiş, aynalığı tam tâbi

**Tarif:** Mütehavvil = ½ + irtifâ × mevhûm-vâhid konur (⟹ irtifâ hakîkî iken mütehavvil tam ayna çizgisi üzerindedir) ve:

> Tekmîl-zeta(irtifâ) = Gauss-zarbı(mütehavvil ÷ 2) × (mütehavvil − 1) × dâire-nisbeti üssü (− mütehavvil ÷ 2) × Zeta(mütehavvil)

**[N] Neden bu mazrûblar?** Gauss-zarbı(mütehavvil ÷ 2) = (mütehavvil ÷ 2) × Gauss-zarbı(mütehavvil ÷ 2 − 1) olduğundan Tekmîl-zeta, Bab 5'teki ifadenin **mütehavvil × (mütehavvil − 1) ÷ 2** ile zarbıdır ⟹ 1 ÷ [mütehavvil × (mütehavvil − 1)] haddindeki iki sonsuzluk (sıfırda ve birde) **silinir**; Zeta'nın birdeki sonsuzluğu da (mütehavvil − 1) ile silinir. Geriye her yerde mütenâhî bir tâbi kalır.

**İki ifadesi:**

> Tekmîl-zeta(irtifâ) = ½ − (irtifâ × irtifâ + ¼) × ∫ [birden sonsuza] Jacobi-mecmûu(kemmiyet) × kemmiyet üssü (− ¾) × ceyb-i tamâm(½ × irtifâ × logaritma(kemmiyet)) × d kemmiyet

> Tekmîl-zeta(irtifâ) = 4 × ∫ [birden sonsuza] {d [kemmiyet üssü (3 ÷ 2) × (d Jacobi-mecmûu(kemmiyet) ÷ d kemmiyet)] ÷ d kemmiyet} × kemmiyet üssü (− ¼) × ceyb-i tamâm(½ × irtifâ × logaritma(kemmiyet)) × d kemmiyet

**Hassaları:**

1. Bütün mütenâhî irtifâlarda **mütenâhîdir**.
2. **İrtifâ × irtifâ**'nın kuvvetlerine göre pek süratle mütekārib bir silsileye açılır ⟸ ceyb-i tamâm çift tâbidir. ⟹ Tekmîl-zeta(irtifâ) = Tekmîl-zeta(− irtifâ); bu, aynalığın irtifâ dilindeki şeklidir.
3. **[N]** Hakîkî irtifâ için hakîkî kıymet alır ⟹ ayna çizgisi üzerindeki cezrler, hakîkî bir tâbinin **işaret değiştirdiği** yerlerdir; sayılabilir, gözle görülebilir.

---

## Bab 7 — Cezrler nerededir, kaç tanedir? Ve farziye [M5]

**Nerede olamazlar:**

> logaritma Zeta(mütehavvil) = − ∑ [her evvelî için] logaritma(1 − evvelî üssü (− mütehavvil))

hakîkî cüz > 1 iken mütenâhîdir (⟹ orada Zeta sıfır olamaz); Tekmîl-zeta'nın öbür mazrûbları da orada sıfır olmaz. Aynalıkla aynı hüküm hakîkî cüz < 0 için de doğrudur. ⟹ Tekmîl-zeta ancak **irtifânın mevhûm cüz'ü − ½ ile + ½ arasında** iken sıfır olabilir. *(Yâni Zeta'nın âdî olmayan sıfırları yalnız 0 < hakîkî cüz < 1 şeridindedir.)*

**Kaç tanedir:** Hakîkî cüz'ü 0 ile **hudut-irtifâ** arasında olan cezrlerin adedi takrîben:

> cezr adedi ≈ (hudut-irtifâ ÷ (2 × dâire-nisbeti)) × logaritma(hudut-irtifâ ÷ (2 × dâire-nisbeti)) − hudut-irtifâ ÷ (2 × dâire-nisbeti)

⟸ d logaritma Tekmîl-zeta tamâmîsi, bu sahanın etrafında müsbet istikamette dolaşınca, (1 ÷ hudut-irtifâ) mertebesinden bir kesir farkıyla, [hudut-irtifâ × logaritma(hudut-irtifâ ÷ (2 × dâire-nisbeti)) − hudut-irtifâ] × mevhûm-vâhid eder; bu tamâmî ise sahadaki cezr adedinin 2 × dâire-nisbeti × mevhûm-vâhid ile zarbıdır. *(Bir tâbinin logaritmasının türevi etrafta dolaşınca cezrleri sayar.)*

**Üç cümle, üç derece:**

| Riemann'ın cümlesi | Derecesi |
| :-- | :-- |
| "Bu hudutlar dâhilinde **takrîben bu kadar hakîkî cezr** bulunur." | Riemann'ın iddiası; burhan vermez. **[N]** Bugün de ispatlı değildir; Hardy 1914'te ayna çizgisinde **sonsuz çok** cezr olduğunu ispat etmiştir. |
| "**Bütün cezrlerin hakîkî olması pek muhtemeldir.**" | **Riemann farziyesi.** Tarihte ilk ve tek beyanı budur. 2026'da hâlâ ne ispat ne nakz edilmiştir [M5]. |
| "Kat'î bir burhan arzu olunurdu; birkaç sathî ve neticesiz teşebbüsten sonra **şimdilik bıraktım**, zîrâ yakın maksadım için lüzumu yok gibi görünüyordu." | Riemann'ın kendi itirafı. |

- **Tercüme köprüsü [M5]:** irtifâ hakîkî ⟺ mütehavvil = ½ + irtifâ × mevhûm-vâhid'in hakîkî cüz'ü **tam ½** ⟹ "bütün cezrler hakîkî" = "Zeta'nın âdî olmayan bütün sıfırları ayna çizgisindedir".
- **[N] Ehemmiyetli incelik:** Riemann'ın **yakın maksadı** (sarîh düstur) farziyeye muhtaç **değildir**. Farziye, düsturun hata payını küçültür (Bab 12). Talebe, farziyeyi düsturun şartı sanmamalıdır.
- **[N]** Cezr sayımı düsturunu kat'î olarak von Mangoldt ispat etmiştir (1905); fark, Riemann'ın dediği gibi 1 ÷ hudut-irtifâ mertebesinde değil, **logaritma(hudut-irtifâ)** mertebesinde kalabilir. Riemann'ın "kesir farkı" cümlesi bu bakımdan fazla iyimserdir.

---

## Bab 8 — Tekmîl-zeta'yı cezrlerinin hâsıl-ı zarbı olarak yazmak

> logaritma Tekmîl-zeta(irtifâ) = ∑ [her cezr için] logaritma(1 − irtifâ × irtifâ ÷ (cezr × cezr)) + logaritma Tekmîl-zeta(0)

**Gerekçe zinciri:**

1. İrtifâ büyüklüğündeki cezrlerin **kesâfeti**, irtifâ ile ancak logaritma(irtifâ ÷ (2 × dâire-nisbeti)) gibi artar ⟹ sağdaki mecmû' **mütekāribdir**.
2. Bu mecmû', sonsuz irtifâ için ancak **irtifâ × logaritma(irtifâ)** gibi büyür.
3. ⟹ logaritma Tekmîl-zeta ile arasındaki fark, irtifâ × irtifâ'nın bir tâbisidir; bu tâbi mütenâhî irtifâda muttasıl ve mütenâhîdir ve **irtifâ × irtifâ'ya taksim edilince sonsuzda sıfıra gider**.
4. ⟹ Fark bir **sâbit**tir; irtifâ = 0 konarak tayin edilir.

**[N]** Bu gerekçe kısa ve eksiktir; kat'î burhânını Hadamard 1893'te mütenâhî mertebeden tam tâbiler nazariyesiyle vermiştir. Talebe bu babı "doğru netice, eksik burhan" diye bellemelidir.

> **Cevher:** *Bir kesîrü'l-hudûd cezrlerinden nasıl kurulursa, Tekmîl-zeta da cezrlerinden öyle kurulur.* Tâbi, cezrlerinin bilgisine tamamen iner.

---

## Bab 9 — Saymaya geçiş: Evvelî-adedi ve Kuvvet-adedi

**Evvelî-adedi(hudut)** [M6]: huduttan küçük evvelîlerin adedi. Hudut bir evvelî ise **½ fazlası** alınır ⟹ sıçrama noktalarında:

> Evvelî-adedi(hudut) = [Evvelî-adedi(hudut + 0) + Evvelî-adedi(hudut − 0)] ÷ 2

⟸ **[N]** Fourier tersine çevirmesi sıçrama noktalarında daima iki tarafın vasatîsini verir (Bab 10); sayım tâbisi baştan buna uygun tarif edilir ki düstur her noktada **tam** tutsun.

**logaritma Zeta'nın açılışı:** Euler hâsıl-ı zarbının logaritması alınır ve logaritma(1 − küçük) silsilesi açılır:

> logaritma Zeta(mütehavvil) = ∑ evvelî üssü (− mütehavvil) + ½ × ∑ evvelî üssü (− 2 × mütehavvil) + ⅓ × ∑ evvelî üssü (− 3 × mütehavvil) + …

**Her kuvveti tamâmî ile yazmak** [M7]:

> evvelî üssü (− mütehavvil) = mütehavvil × ∫ [evvelîden sonsuza] kemmiyet üssü (− mütehavvil − 1) × d kemmiyet

ve evvelînin murabbaı, mükâabı için de aynı şekilde. *(Tercümenin esas aldığı dizgide burada "d mütehavvil" yazılıdır; mânâca doğrusu "d kemmiyet"tir. Bu farkın hangi baskıda doğduğu yoklanamamıştır [M7].)*

**Kuvvet-adedi** tarif edilir:

> Kuvvet-adedi(hudut) = Evvelî-adedi(hudut) + ½ × Evvelî-adedi(hudut üssü ½) + ⅓ × Evvelî-adedi(hudut üssü ⅓) + …

**[N] Sebep:** Bir kemmiyet, evvelînin "adet"inci kuvvetini aşar ⟺ evvelî, kemmiyetin "adet"inci kökünden küçüktür. ⟹ Tamâmîlerin hepsi toplanınca her kemmiyet noktasında, ondan küçük evvelî kuvvetleri, adet'inci kuvvet (1 ÷ adet) ağırlıkla sayılmış olur. Bu da tam Kuvvet-adedi'dir.

⟹ **Köprü muâdelesi:**

> logaritma Zeta(mütehavvil) ÷ mütehavvil = ∫ [birden sonsuza] Kuvvet-adedi(kemmiyet) × kemmiyet üssü (− mütehavvil − 1) × d kemmiyet

Mütehavvil = hakîkî-cüz + mevhûm-cüz × mevhûm-vâhid ve hakîkî-cüz > 1 iken muteberdir.

> **Cevher:** *Sayım tâbisi (evvelîleri kuvvetleriyle beraber sayan) ile Zeta'nın logaritması, bir tamâmî dönüşümünün iki yüzüdür.* Biri bilinirse öbürü geri alınabilir.

---

## Bab 10 — Fourier ile geri almak

**Umûmî kalıp:**

> Sûret(mütehavvil) = ∫ [sıfırdan sonsuza] Asıl(kemmiyet) × kemmiyet üssü (− mütehavvil) × d logaritma(kemmiyet)

Asıl hakîkî ve Sûret(hakîkî-cüz + mevhûm-cüz × mevhûm-vâhid) = Sûret-hakîkî(mevhûm-cüz) + mevhûm-vâhid × Sûret-mevhûm(mevhûm-cüz) olsun ⟹ muâdele ikiye ayrılır:

> Sûret-hakîkî(mevhûm-cüz) = ∫ [sıfırdan sonsuza] Asıl(kemmiyet) × kemmiyet üssü (− hakîkî-cüz) × ceyb-i tamâm(mevhûm-cüz × logaritma(kemmiyet)) × d logaritma(kemmiyet)

> mevhûm-vâhid × Sûret-mevhûm(mevhûm-cüz) = − mevhûm-vâhid × ∫ [sıfırdan sonsuza] Asıl(kemmiyet) × kemmiyet üssü (− hakîkî-cüz) × ceyb(mevhûm-cüz × logaritma(kemmiyet)) × d logaritma(kemmiyet)

İkisi de [ceyb-i tamâm(mevhûm-cüz × logaritma(nokta)) + mevhûm-vâhid × ceyb(mevhûm-cüz × logaritma(nokta))] × d mevhûm-cüz ile zarb edilip eksi sonsuzdan artı sonsuza tamâmlanır ⟹ Fourier kaziyyesi mûcibince ikisinin sağında da **dâire-nisbeti × Asıl(nokta) × nokta üssü (− hakîkî-cüz)** çıkar [M8]. Cem' edilip mevhûm-vâhid × nokta üssü hakîkî-cüz ile zarb edilince:

> 2 × dâire-nisbeti × mevhûm-vâhid × Asıl(nokta) = ∫ [hakîkî-cüz − sonsuz × mevhûm-vâhid'den hakîkî-cüz + sonsuz × mevhûm-vâhid'e] Sûret(mütehavvil) × nokta üssü mütehavvil × d mütehavvil

Tamâmî, **hakîkî cüz sâbit** tutularak dikey bir doğru üzerinden alınır. Sıçrama noktalarında **iki tarafın vasatîsini** verir; Kuvvet-adedi de öyle tarif edildiğinden (Bab 9):

> Kuvvet-adedi(nokta) = [1 ÷ (2 × dâire-nisbeti × mevhûm-vâhid)] × ∫ [hakîkî-cüz − sonsuz × mevhûm-vâhid'den hakîkî-cüz + sonsuz × mevhûm-vâhid'e] (logaritma Zeta(mütehavvil) ÷ mütehavvil) × nokta üssü mütehavvil × d mütehavvil

**Mütercimin tashihi [M8]:** Dizgide iki yerde "hakîkî-cüz" yerine sıfırların harfi görünür; hesabın gidişi hakîkî-cüz'ü ister. İki harf birbirine pek benzediği için dizgide karışmış olması muhtemeldir.

**[N] Bugünkü adıyla:** Bu kalıp bugün "**Mellin dönüşümü ve tersi**" diye bilinir; Fourier kaziyyesinin logaritmik ölçekte okunuşudur.

---

## Bab 11 — Sarîh düstur: her haddi tek kalıpla hesaplamak [M9, M10]

**İkame:** Bab 4 – Bab 8'den:

> logaritma Zeta(mütehavvil) = (mütehavvil ÷ 2) × logaritma(dâire-nisbeti) − logaritma(mütehavvil − 1) − logaritma Gauss-zarbı(mütehavvil ÷ 2) + ∑ [her cezr için] logaritma(1 + (mütehavvil − ½) üssü 2 ÷ (cezr × cezr)) + logaritma Tekmîl-zeta(0)

**Mâni:** Ayrı ayrı haddlerin tamâmîleri sonsuza uzayınca mütekārib olmaz. ⟹ **Cüz cüz tamâmlama** ile önce şu şekle sokulur:

> Kuvvet-adedi(hudut) = − [1 ÷ (2 × dâire-nisbeti × mevhûm-vâhid)] × [1 ÷ logaritma(hudut)] × ∫ [dikey doğru] {d [logaritma Zeta(mütehavvil) ÷ mütehavvil] ÷ d mütehavvil} × hudut üssü mütehavvil × d mütehavvil

**Gauss-zarbı haddinin açılışı:** Son-adet sonsuza giderken:

> − logaritma Gauss-zarbı(mütehavvil ÷ 2) = hadd [∑ (adet birden son-adete) logaritma(1 + mütehavvil ÷ (2 × adet)) − (mütehavvil ÷ 2) × logaritma(son-adet)]

⟹ türevi alınınca logaritma(son-adet) haddi düşer; Gauss-zarbı haddi de **adet başına bir logaritma(1 + mütehavvil ÷ (2 × adet))** haddine ayrılır.

**[N] Birleştirici bakış (risâlenin en zarif hamlesi):** Bütün haddler, logaritma Tekmîl-zeta(0) müstesnâ, **aynı kalıba** girer: logaritma(1 − mütehavvil ÷ umûmî-cezr). Umûmî-cezr'in yerine konan üç cins:

| Cins | Umûmî-cezr | Nereden gelir | Netice haddi |
| :-- | :-- | :-- | :-- |
| Birdeki sonsuzluk | 1 | − logaritma(mütehavvil − 1) | **+ Logaritmik-tamâmî(hudut)** (haddin önündeki eksi yüzünden cezrlerin aksine müsbet) |
| Âdî sıfırlar | − 2 × adet | Gauss-zarbı haddi | ∫ [huduttan sonsuza] 1 ÷ (kemmiyet üssü 2 − 1) × d kemmiyet ÷ (kemmiyet × logaritma(kemmiyet)) |
| Âdî olmayan sıfırlar | ½ ± cezr × mevhûm-vâhid | cezrler mecmû'u | − Logaritmik-tamâmî(hudut üssü umûmî-cezr) |

logaritma Tekmîl-zeta(0) haddi ise 1 ÷ (mütehavvil × mütehavvil) ile çarpılı olduğundan doğrudan **logaritma Tekmîl-zeta(0)** verir.

**Tek kalıbın hesabı:**

> d [(1 ÷ mütehavvil) × logaritma(1 − mütehavvil ÷ umûmî-cezr)] ÷ d umûmî-cezr = 1 ÷ [(umûmî-cezr − mütehavvil) × umûmî-cezr]

Mütehavvilin hakîkî cüz'ü umûmî-cezrinkinden büyük iken:

> − [1 ÷ (2 × dâire-nisbeti × mevhûm-vâhid)] × ∫ [dikey doğru] hudut üssü mütehavvil × d mütehavvil ÷ [(umûmî-cezr − mütehavvil) × umûmî-cezr] = hudut üssü umûmî-cezr ÷ umûmî-cezr

ve bu da umûmî-cezr'in hakîkî cüz'ü **menfî** ise ∫ [sonsuzdan hududa] kemmiyet üssü (umûmî-cezr − 1) × d kemmiyet, **müsbet** ise ∫ [sıfırdan hududa] kemmiyet üssü (umûmî-cezr − 1) × d kemmiyet'tir. Umûmî-cezr üzerinden geri tamâmlanınca:

- menfî hâlde: ∫ [sonsuzdan hududa] kemmiyet üssü (umûmî-cezr − 1) ÷ logaritma(kemmiyet) × d kemmiyet + sâbit,
- müsbet hâlde: ∫ [sıfırdan hududa] kemmiyet üssü (umûmî-cezr − 1) ÷ logaritma(kemmiyet) × d kemmiyet + sâbit.

**Sâbitin düşmesi [M9]:** Birinci hâlde sâbit, umûmî-cezr'in hakîkî cüz'ü menfî tarafta sonsuz kılınarak tayin olunur. İkinci hâlde sıfırdan hududa tamâmî, yolun **kavsi** (bugün "argüman") müsbet yahut menfî mürekkeb kıymetlerden geçmesine göre **2 × dâire-nisbeti × mevhûm-vâhid** kadar farklı kıymet alır; birinci yol, umûmî-cezr'deki mevhûm-vâhid emsali müsbet sonsuza, ikinci yol menfî sonsuza giderken sonsuz küçük olur. ⟹ Sâbitin düşmesi için logaritma(1 − mütehavvil ÷ umûmî-cezr) sol tarafta buna göre tayin edilir.

**Netice — Riemann'ın sarîh düsturu [M10]:**

> **Kuvvet-adedi(hudut) = Logaritmik-tamâmî(hudut) − ∑ [her cezr için] [Logaritmik-tamâmî(hudut üssü (½ + cezr × mevhûm-vâhid)) + Logaritmik-tamâmî(hudut üssü (½ − cezr × mevhûm-vâhid))] + ∫ [huduttan sonsuza] [1 ÷ (kemmiyet üssü 2 − 1)] × d kemmiyet ÷ (kemmiyet × logaritma(kemmiyet)) + logaritma Tekmîl-zeta(0)**

- Logaritmik-tamâmî(hudut) = ∫ [sıfırdan hududa] d kemmiyet ÷ logaritma(kemmiyet), **birdeki tekillik etrafında esas kıymet** mânâsında [M10].
- Mecmû'da cezr yerine **müsbet** (yahut müsbet hakîkî cüz'lü) bütün cezrler, **büyüklük sırasıyla** konur.
- **Sıra şarttır:** Bu sırada silsile, mevhûm-cüz sınırsız büyürken ilgili dikey tamâmînin yaklaştığı hadd kıymetine mutabıktır; **sıra değiştirilirse silsile her keyfî hakîkî kıymeti alabilir**. *(**[N]** Silsile mutlak değil, şartlı mütekāribdir; Riemann bunu açıkça ihtar eder.)*

**[N] Sâbit hakkında ihtar:** Mütercim kaydı [M10] "bugünkü umûmî kabule göre logaritma Tekmîl-zeta(0) = − logaritma(2)" der. Bu cümle titizlikle okunmalıdır: Riemann'ın Tekmîl-zeta(0)'ı **irtifâ = 0**, yâni mütehavvil = ½ noktasındaki kıymettir ve takriben **0,497**'dir; ½ değildir. Sarîh düsturun doğru sâbiti ise **− logaritma(2)**'dir, ki bu ½'nin logaritmasıdır ve Tekmîl-zeta'nın mütehavvil = 0 (yahut 1) noktasındaki kıymetinden gelir. Yâni Riemann'ın yazdığı sâbit (logaritma 0,497 ≈ − 0,699) ile doğrusu (− logaritma 2 ≈ − 0,693) birbirine çok yakın fakat **ayrıdır**; bu, Riemann'ın küçük bir sürçmesi olarak bilinir (Edwards'ın *Riemann's Zeta Function*, 1974, kitabında kaydedildiğini hatırlıyorum; sahifesini yoklamadım). Bu ihtar tercümeye değil, mütercim kaydının ilk ifadesine yönelikti; tercüme Riemann'ın yazdığını doğru nakletmiştir. Mütercim [M10]'u bu tenbih üzerine tashih etmiştir.

**[N]** Sarîh düsturun kat'î burhânını von Mangoldt 1895'te vermiştir.

---

## Bab 12 — Evvelî-adedi'ni geri almak ve kesâfet [M11]

**Möbius tersine çevirmesi:**

> Kuvvet-adedi(hudut) = ∑ [her adet için] (1 ÷ adet) × Evvelî-adedi(hudut üssü (1 ÷ adet))

münasebeti tersine çevrilir:

> **Evvelî-adedi(hudut) = ∑ [her murabbasız için] (− 1) üssü mazrûb-sayısı × (1 ÷ murabbasız) × Kuvvet-adedi(hudut üssü (1 ÷ murabbasız))**

- **Murabbasız:** 1'den başka hiçbir murabbaa taksim olunmayan adet (1, 2, 3, 5, 6, 7, 10, 11 …; 4, 8, 9, 12 … **girmez**).
- **Mazrûb-sayısı:** o adedin evvelî mazrûblarının adedi.
- (− 1) üssü mazrûb-sayısı, bugünkü **Möbius tâbisi**nin kıymetidir [M11].

**Kesâfet:** Cezr mecmû'u mütenâhî adette kesilir ve türev alınırsa (hudut büyüdükçe süratle sönen bir cüz' hâriç):

> 1 ÷ logaritma(hudut) − 2 × ∑ [her cezr için] ceyb-i tamâm(cezr × logaritma(hudut)) × hudut üssü (− ½) ÷ logaritma(hudut)

Bu, şunların **mecmû'unun** takrîbî kesâfetidir: hudut civarındaki evvelîlerin kesâfeti + evvelî **murabbaların** kesâfetinin yarısı + evvelî **mükâabların** kesâfetinin üçte biri + … *(Kuvvet-adedi'nin türevi olduğu için.)*

- **1 ÷ logaritma(hudut):** ortalama kesâfet. *(**[N]** Bir kemmiyet civarında rastgele seçilen bir adedin evvelî olma ihtimali takriben 1 ÷ logaritma(kemmiyet).)*
- **Her cezr bir dalga:** ceyb-i tamâm(cezr × logaritma(hudut)) logaritmik ölçekte bir **titreşimdir**; genliği hudut üssü (− ½) ile söner. ⟹ Evvelîlerin yer yer sıklaşıp seyrekleşmesi, bu titreşimlerin üst üste binmesidir.
- **[N] Farziye burada devreye girer:** Bir cezrin hakîkî cüz'ü ½ olmayıp daha büyük olsaydı, o dalganın genliği hudut üssü (− ½)'den yavaş sönerdi ⟹ düzensizlik daha büyük olurdu. **Riemann farziyesi = bütün dalgalar mümkün olan en hızlı sönüşle söner** = evvelîlerin dağılışı mümkün olan en muntazam hâldedir.

---

## Bab 13 — Gauss'un takrîbi neden fazla verir? Ve sayımların hükmü [M12]

**Malûm takrîb:** Evvelî-adedi(hudut) ≈ Logaritmik-tamâmî(hudut).

**Riemann'ın teşhisi:** Bu takrîb ancak **hudut üssü ½ mertebesine kadar** doğrudur ve **biraz fazla** verir ⟸ Evvelî-adedi'nin **devrî olmayan** haddleri (hudut ile sonsuza artmayanlar bırakılırsa):

> Logaritmik-tamâmî(hudut) − ½ × Logaritmik-tamâmî(hudut üssü ½) − ⅓ × Logaritmik-tamâmî(hudut üssü ⅓) − ⅕ × Logaritmik-tamâmî(hudut üssü ⅕) + ⅙ × Logaritmik-tamâmî(hudut üssü ⅙) − ⅐ × Logaritmik-tamâmî(hudut üssü ⅐) + …

**[N] Emsallerin sırrı:** Emsaller, Möbius tâbisinin (1 ÷ murabbasız) ile zarbıdır: 2 ⟶ − ½; 3 ⟶ − ⅓; 4 murabbasız değil ⟶ **yok**; 5 ⟶ − ⅕; 6 = 2 × 3 iki mazrûblu ⟶ **+ ⅙**; 7 ⟶ − ⅐. **Fazla vermenin illeti** ikinci haddir: − ½ × Logaritmik-tamâmî(hudut üssü ½), takriben hudut kökü ÷ logaritma(hudut) kadar bir **eksiltme**. Gauss'un takrîbi bu haddi bilmediği için fazla verir.

**Sayımlar:** *Gauss* ve *Goldschmidt* üç milyona kadar saymıştır: evvelî adedi **birinci yüz binden itibaren daima** Logaritmik-tamâmî'den küçük çıkmış; fark, dalgalanarak **tedricen artmıştır**. Evvelîlerin yer yer sıklaşıp seyrekleşmesi de dikkati çekmiş, fakat **bir kanuniyet bulunamamıştır**.

**Riemann'ın teklifi:** Yeni sayımlarda **devrî haddlerin** (cezr dalgalarının) tesiri ayrı ayrı takip edilsin.

**Kuvvet-adedi daha muntazamdır:** Daha **birinci yüz içinde** ortalama olarak **Logaritmik-tamâmî(hudut) + logaritma Tekmîl-zeta(0)** ile açıkça mutabıktır.

**Sonraki tarih [M12]:** Riemann'ın naklettiği "daima küçük" müşahedesi üç milyona kadar doğrudur. Fakat 1914'te **Littlewood**, farkın işaretinin **sonsuz defa değiştiğini** ispat etmiştir; ilk değişim yeri pek büyüktür ve kesin bilinmemektedir (mütercimin bilgisi). **[N] İlliyet:** − ½ × Logaritmik-tamâmî(hudut üssü ½) eksiltmesi ile cezr dalgaları **aynı mertebededir** (ikisi de hudut kökü civarı); dalgalar bazen üst üste binip bu eksiltmeyi bastırır ⟹ işaret döner. Riemann'ın bu teşhisi, Littlewood neticesinin tohumunu da taşır.

---

## Bab 14 — Riemann ne ispat etti, ne iddia etti? [N]

| Hüküm | Riemann'da | Bugünkü hâli (not sahibinin bilgisi) |
| :-- | :-- | :-- |
| Zeta'nın bütün düzleme yayılması, birde tek sonsuzluk | ispatlı | ispatlı |
| Tâbiî muâdele (aynalık) | iki burhanla ispatlı | ispatlı |
| Âdî olmayan sıfırlar 0 < hakîkî cüz < 1 şeridinde | kısa gerekçe | ispatlı |
| Cezr sayımı (hudut-irtifâ'ya kadar) | iddia, gerekçe taslağı | von Mangoldt 1905, hata logaritmik mertebede |
| Takriben bu kadar cezr ayna çizgisinde | iddia | **açık**; Hardy 1914: sonsuz çok cezr çizgide |
| Bütün cezrler ayna çizgisinde | "pek muhtemel" | **açık: Riemann farziyesi** |
| Tekmîl-zeta'nın cezrler üzerinden hâsıl-ı zarbı | eksik gerekçe | Hadamard 1893 |
| Sarîh düstur | burhan taslağı | von Mangoldt 1895 |
| Sâbitin logaritma Tekmîl-zeta(0) oluşu | yazılı | küçük sürçme; doğrusu − logaritma 2 |
| Evvelî-adedi ÷ (hudut ÷ logaritma hudut) → 1 | Riemann söylemez | Hadamard ve de la Vallée Poussin 1896 (bu risâlenin yolundan) |

---

## Bab 15 — Kendini yoklama sualleri

1. Euler hâsıl-ı zarbı neden yalnız hakîkî cüz > 1 iken muteberdir ve bu kusur nasıl giderilir? *(Silsile ancak orada mütekāribdir; sonsuzdan sonsuza yol tamâmîsi her yerde muteberdir.)*
2. Zeta hangi noktada sonsuzlaşır, hangi noktalarda sıfır olur? *(Birde sonsuz; menfî çift adetlerde sıfır; ayrıca 0 – 1 şeridindeki cezrlerde.)*
3. Ayna çizgisi nedir, neden oradadır? *(Hakîkî cüz ½; mütehavvil ile 1 − mütehavvil'in ortası.)*
4. Tekmîl-zeta'da (mütehavvil − 1) ve Gauss-zarbı(mütehavvil ÷ 2) mazrûbları ne işe yarar? *(Sıfırdaki ve birdeki sonsuzlukları siler.)*
5. Riemann farziyesi, sarîh düsturun şartı mıdır? *(Hayır; düstur farziyesiz doğrudur. Farziye hata payını tayin eder.)*
6. Kuvvet-adedi'nin Evvelî-adedi'nden farkı nedir ve neden ona ihtiyaç vardır? *(Evvelî kuvvetlerini 1 ÷ kuvvet ağırlığıyla sayar; logaritma Zeta ile doğrudan tamâmî münasebeti onundur.)*
7. Sıçrama noktalarında neden yarım değer alınır? *(Fourier tersine çevirmesi orada iki tarafın vasatîsini verir.)*
8. Logaritmik-tamâmî neden fazla verir? *(− ½ × Logaritmik-tamâmî(hudut kökü) haddini bilmez.)*
9. Cezrler mecmû'unun sırası neden mühimdir? *(Silsile şartlı mütekāribdir; sıra değişince her hakîkî kıymeti alabilir.)*
10. Littlewood neticesi Riemann'ın teşhisiyle nasıl bağdaşır? *(Eksiltme haddi ile cezr dalgaları aynı mertebede; dalgalar zaman zaman eksiltmeyi aşar.)*

---

## Ek 1 — İsimler cedveli (tercümenin aynısı)

| Bu notta | Mânâsı | Aslındaki işaretin adı |
| :-- | :-- | :-- |
| mütehavvil | Zeta'nın mürekkeb mütehavvili | Latin "es" |
| hakîkî-cüz | mütehavvilin hakîkî cüz'ü | Latin "a" |
| mevhûm-cüz | mütehavvilin mevhûm cüz'ünün emsali | Latin "be" |
| evvelî | bütün a'dâd-ı evveliyye üzerinde gezen adet | Latin "pe" |
| adet | bütün tam a'dâd üzerinde gezen adet | Latin "en" |
| son-adet | hâsıl-ı zarbın kesildiği son adet | Latin "em" |
| murabbasız | murabbaa bölünmeyen adet | Latin "em" |
| mazrûb-sayısı | murabbasızın evvelî mazrûb adedi | Yunan "mü" |
| kemmiyet | tamâmlama mütehavvili | Latin "iks" |
| hudut | evvelîlerin sayıldığı hudut | Latin "iks" |
| nokta | Fourier tersine çevirmesinde bakılan yer | Latin "ye" |
| irtifâ | Tekmîl-zeta'nın mütehavvili | Latin "te" |
| hudut-irtifâ | cezrlerin sayıldığı irtifâ haddi | Latin büyük "te" |
| cezr | Tekmîl-zeta'nın sıfırları | Yunan "alfa" |
| umûmî-cezr | herhangi bir cezri temsil eden yardımcı ad | Yunan "beta" |
| Zeta | zeta tâbisi | Yunan "zeta" |
| Gauss-zarbı | Gauss'un hâsıl-ı zarb tâbisi (bugün gamma'nın kaydırılmışı) | Yunan büyük "pî" |
| Jacobi-mecmûu | teta mecmû'u | Yunan "psi" |
| Tekmîl-zeta | tamamlanmış zeta | Yunan "ksi" |
| Evvelî-adedi | huduttan küçük evvelîlerin sayısı | Latin büyük "ef" |
| Kuvvet-adedi | evvelî kuvvetlerini ağırlıkla sayan tâbi | Latin "ef" |
| Logaritmik-tamâmî | logaritmik tamâmî | "Li" |
| Sûret, Sûret-hakîkî, Sûret-mevhûm | Fourier çiftinin sûret tarafı ve iki cüz'ü | Latin "ge", "ge bir", "ge iki" |
| Asıl | Fourier çiftinin asıl tarafı | Latin "he" |
| Neper | tabiî logaritmanın esası | Latin "e" |
| dâire-nisbeti | muhîtin kutra nisbeti | Yunan "pî" |
| mevhûm-vâhid | murabbaı eksi bir olan vâhid | Latin "i" |
| logaritma, ceyb, ceyb-i tamâm | logaritma, sinüs, kosinüs | "log", "sin", "cos" |

**[N] Dikkat:** Aslında aynı harf iki ayrı vazifede kullanılır ("iks" hem tamâmlama mütehavvili hem hudut; "em" hem son-adet hem murabbasız). Tercüme bunları vazifelerine göre ayrı kelimelerle karşılamıştır; bu, aslı okurken talebeyi şaşırtabilecek bir düğümü çözer.

## Ek 2 — Istılahlar (tercümenin cedvelinden, dayanaklarıyla)

adet-i evvelî, cem'i a'dâd-ı evveliyye (asal sayı; lügat 11A41) · tâbi (fonksiyon; lügat 11M) · mürekkeb mütehavvil (karmaşık değişken; lügat 11F68) · hakîkî cüz (reel kısım; lügat 11M20) · mevhûm cüz (sanal kısım; teklif) · mütekārib (yakınsak; teklif, lügat 11N37 yakınında) · tamâmî, tamâmlama (integral, integrasyon; lügat 11S80) · cüz cüz tamâmlama (kısmî integrasyon; teklif) · silsile (seri; lügat 11F27) · hâsıl-ı zarb (çarpım; lügat 11H46) · cezr (kök; lügat 11A07) · muâdele (denklem; lügat 11D) · mazrûb, evvelî mazrûb (çarpan, asal çarpan; lügat 11A51) · kesâfet (yoğunluk; lügat 11B05) · takrîb düstûru (yaklaşıklık formülü; lügat 11J, 00A22) · Fourier kaziyyesi (lügat 11H60) · inkıtâ', munkatı' (süreksizlik; teklif) · muttasıl (sürekli; lügat 11K41) · mütenâhî / nihâyetsiz (sonlu / sonsuz; lügat 11T) · tek kıymetli / çok kıymetli (teklif) · mikyâs (mutlak değer; teklif) · kemmiyet sahası (büyüklük bölgesi; teklif) · müştakk (türev; teklif) · hadd kıymeti (limit; teklif) · sâbit (teklif) · hadd (terim; teklif) · murabba / mükâab (kare / küp; lügat 11R11, 11R16) · devrî (periyodik; lügat 11K70) · vasatî kıymet (ortalama; lügat 11H60) · kavis (argüman; teklif, [M9]) · ceyb / ceyb-i tamâm (sinüs / kosinüs; kadîm).
