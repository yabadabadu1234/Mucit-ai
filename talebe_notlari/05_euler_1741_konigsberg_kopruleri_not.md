# Talebe Notu — Euler 1741, Königsberg Köprüleri

> **Kaynak:** [tercume/eserler/05_euler_1741_konigsberg_kopruleri.md](../tercume/eserler/05_euler_1741_konigsberg_kopruleri.md).
> **Usûl:** Tercüme parça parça okunmuş, her parça okunur okunmaz damıtılmıştır; notun babları o parçaların sırasını takip eder.
> **İşaretler:** ⟹ "bundan şu lâzım gelir" · ⟸ "çünkü" · **[N]** not sahibinin ilâvesidir, tercümede yoktur · **[M…]** mütercim kaydına atıftır.
> **Düstur kaidesi:** Düsturlarda harf yoktur, kelime vardır. Euler'in arazi harfleri burada da **ad** ile yazılmıştır: Ada, Birinci kıyı, İkinci kıyı, Şark arazisi. Aslın harfleriyle karşılaştırma cedveli sondadır.

---

## Bab 1 — Künye ve meselenin doğuşu (aslın § 1 – § 3)

**Künye.** Euler, *Solutio problematis ad geometriam situs pertinentis* ("Hendese-i vaz'a taalluk eden bir meselenin halli"), Latince; Eneström fihristinde 53 numara. Petersburg İmparatorluk İlimler Akademisi Mecmûası, sekizinci cilt (1736 senesi için), neşri 1741, sahife 128–140, Levha VIII. Nüsha: Biodiversity Heritage Library taraması, Internet Archive `commentariiacade08impe`; metin harf tanımadan okunup sahife resmi ve mütercimin bilgisiyle düzeltilmiştir. Müellif 1783'te vefat etti ⟹ telif düşmüş, her memlekette açık. Aslında **tek bir düstur yoktur**; Euler bütün hesabı kelimeyle söyler.

**İlliyet zinciri:**

1. Hendesenin iki cüz'ü vardır: **kemmiyet hendesesi** (ölçü ve hesap, asırlardır işlenmiş) ve **vaz' hendesesi** (yalnız konum ve konumun hassaları; ne ölçüye ne hesaba muhtaç). İkincisinin adını ilk koyan *Leibniz*'dir: *geometria situs*.
2. Fakat Leibniz **hangi meselenin** bu cüz'e ait olduğunu ve **hangi usûlle** çözüleceğini tarif etmemiştir ⟹ cüz'ün adı var, numûnesi yok.
3. Königsberg meselesi hendeseye benzer, fakat ne kemmiyet tayini ister ne hesapla çözülür ⟹ Euler onu vaz' hendesesine nisbet eder ve **ilk numûne** olarak arz eder. *(Risâlenin tarihî kıymeti buradan doğar: bir sahanın tarifi ilk defa misalle doldurulur.)*
4. **Mesele (hususî):** Kneiphof adası (Ada) nehrin iki koluyla çevrilidir; kollar yedi köprüyle örtülüdür. Her köprüden **bir kere ve yalnız bir kere** geçen bir yol tertip edilebilir mi? Halk arasında kimi inkâr, kimi şüphe ediyor; **tasdik eden yok**.
5. **Mesele (umûmî):** Euler hususîden umûmîye sıçrar: nehrin şekli, kolları ve köprü sayısı **ne olursa olsun**, böyle bir yolun var olup olmadığını bulmak. ⟸ Hususî cevap tek bir şehri doyurur; umûmî cevap bütün şehirleri.
6. **Reddedilen yol — tam sayım:** Bütün yolları tek tek saymak cevabı verirdi, fakat üç kusuru vardır:
   - terkiplerin sayısı pek büyüktür ⟹ zahmetlidir;
   - köprü çoğalınca **hiç kullanılamaz**;
   - sualde **sorulmayan** pek çok şeyi de bulur ⟹ güçlüğün asıl sebebi budur.
7. ⟹ Euler'in aradığı usûlün şartı: **yolun varlığından fazlasını söylemeyen** usûl. ⟸ Fazlasını söylemeyen usûlün daha basit olacağından şüphelenmiştir.

> **Cevher:** *Suale tam cevap veren fakat suali aşmayan usûl, en basit usûldür.* Euler'in bütün risâlesi bu tek düşüncenin tatbikidir: yolu bulmaya çalışmaz, yolun **imkânını** tartar.

**Hatırda tutulacak:** Şekiller aslındaki VIII numaralı levhadadır; tercümede henüz çizilmemiştir [M2].

---

## Bab 2 — Yürüyüşü harf silsilesine çevirmek (aslın § 4 – § 7)

**İlliyet zinciri:**

1. **Kodlama:** Nehirle ayrılmış her araziye bir ad verilir. Bir köprü geçişi iki adla yazılır: *çıkılan arazi, varılan arazi* (Adadan Birinci kıyıya geçiş ⟹ "Ada · Birinci kıyı").
2. **Kaynaştırma:** Ardışık iki geçişte ortadaki ad ortaktır ⟸ birinci geçişte varılan arazi, ikinci geçişte çıkılan arazinin ta kendisidir ⟹ ortak ad bir kere yazılır ("Ada · Birinci kıyı · Şark arazisi" iki geçiştir, üç addır).
3. ⟹ **Birinci kanun:**

   > **yazılan ad sayısı = geçilen köprü sayısı + 1**

   Dört köprü beş ad ister; yedi köprü **sekiz ad** ister.
4. **Hangi köprüden geçildiği unutulur:** İki arazi arasında birden fazla köprü varsa, hangisinden geçildiği silsilede görünmez ve görünmesine lüzum yoktur ⟸ sorulan şey yalnız *her köprünün bir kere kullanılmasıdır*; bu da ancak **komşuluk sayılarıyla** tartılır.
5. **Königsberg'in komşuluk sayıları** (§ 6'dan; [M2]'deki birleşme cedveli):

   | Arazi çifti | Aralarındaki köprü | Silsilede yan yana gelme sayısı |
   | :-- | :-- | :-- |
   | Ada – Birinci kıyı | 2 | 2 |
   | Ada – İkinci kıyı | 2 | 2 |
   | Ada – Şark arazisi | 1 | 1 |
   | Birinci kıyı – Şark arazisi | 1 | 1 |
   | İkinci kıyı – Şark arazisi | 1 | 1 |
   | **mecmû'** | **7** | **7** |

6. ⟹ **Mesele irca edildi:** dört addan sekiz adlık öyle bir silsile kurmak ki her çift tam emredilen kadar yan yana gelsin. Köprü, nehir, şehir kayboldu; **geriye yalnız bir harf silsilesi kaldı**. *(Bu, mekânî bir meseleyi mekândan soyup terkîbî bir meseleye çevirmektir; vaz' hendesesinin ilk hamlesi budur.)*
7. **Tertip sırası:** Silsileyi kurmaya uğraşmadan **evvel**, kurulabilir olup olmadığı tartılmalıdır ⟸ imkânsız olduğu gösterilirse bütün emek boşa gider. ⟹ Euler, bu ve benzeri **bütün** sualler için silsilenin imkânını ayırt eden bir **kaide** arar.

> **Cevher:** *Mekân kaybolur, sayılar kalır.* Bir yol, ad silsilesidir; bir köprü, silsilede yan yana gelen iki addır; mesele, o silsilenin **uzunluğu** ile her adın **tekrar sayısı** arasındaki münasebete iner.

**[N] Bugünkü dille:** Araziler düğüm, köprüler kenar, yol da kenarlardan geçen bir yürüyüştür. Euler henüz "çizge" kelimesini bilmez; fakat kodlaması çizgenin ta kendisidir.

---

## Bab 3 — Tek arazinin kaidesi, Königsberg'in hükmü ve altı adımlı ameliye (aslın § 8 – § 14)

**İlliyet zinciri:**

1. **Bakış daraltılır:** Bütün şehir yerine **tek bir araziye** bakılır ⟸ silsilede bir adın kaç kere geçeceği yalnız o araziye açılan köprülere bağlıdır; köprülerin öbür ucunun nereye gittiği hükmü değiştirmez (§ 10: köprüler tek bir kıyıdan da gelse, muhtelif yerlerden de gelse kaide aynıdır).
2. **Tek köprü:** Araziye bir köprü açılıyorsa, yolcu ya geçişten evvel oradadır ya sonra oraya varır ⟹ arazinin adı **bir** kere yazılır.
3. **Tek sayıda köprü:** Üç köprü ⟹ ad **iki** kere; beş köprü ⟹ **üç** kere; ve bu, yolun oradan başlayıp başlamamasına bağlı **değildir**. ⟹ [M3]:

   > **tek köprülü arazide adın tekrar sayısı = (köprü sayısı + 1) ÷ 2**

4. **Königsberg'in hükmü (§ 9):**

   | Arazi | Açılan köprü | Adın tekrarı |
   | :-- | :-- | :-- |
   | Ada | 5 | 3 |
   | Birinci kıyı | 3 | 2 |
   | İkinci kıyı | 3 | 2 |
   | Şark arazisi | 3 | 2 |
   | **mecmû'** | | **9** |

   Silsile yedi köprü için **sekiz** ad ister (Bab 2'deki birinci kanun); tekrarların mecmû'u ise **dokuz**dur ⟹ **dokuz ad sekiz yere sığmaz** ⟹ Königsberg'de böyle bir yol **yoktur**. Euler'in bütün burhânı bu tek sayı farkıdır [M4].
5. **Bütün arazileri tek olan her şehir (§ 10):** tekrarların mecmû'u = köprü sayısı + 1 ise yol "yapılabilir"; fazla ise **asla** yapılamaz.
6. **Çift sayıda köprü (§ 11 – § 12):** Burada başlangıç noktası hükme girer:
   - İki köprü, yol **o araziden başlıyor** ⟹ ad iki kere (çıkış için bir, dönüş için bir).
   - İki köprü, yol **başka yerden başlıyor** ⟹ ad bir kere (tek yazılış hem varışı hem çıkışı gösterir).
   - Dört köprü ⟹ başlarsa üç, başlamazsa iki. Altı köprü ⟹ başlarsa dört, başlamazsa üç.
   - ⟹ **Umûmî:**

     > **çift köprülü arazide adın tekrarı = köprü sayısı ÷ 2** (yol orada başlamıyorsa)
     > **çift köprülü arazide adın tekrarı = (köprü sayısı ÷ 2) + 1** (yol orada başlıyorsa)

7. **Kaidelerin birleşmesi (§ 13):** Yol ancak **bir** araziden başlar ⟹ her arazi için: tek ise (köprü + 1) ÷ 2, çift ise köprü ÷ 2 alınır; sonra:
   - mecmû' = köprü sayısı + 1 ⟹ yol vardır, **tek köprülü** bir araziden başlanır;
   - mecmû' = köprü sayısı ⟹ yol vardır, **çift köprülü** bir araziden başlanır ⟸ başlangıç arazisinin tekrarı bir artar ve mecmû' tamamlanır.
8. **Altı adımlı ameliye (§ 14):**
   1. Su ile ayrılmış her araziye ad ver.
   2. Köprülerin sayısını al, **bir ekle**, cedvelin başına yaz.
   3. Adları alt alta yaz; her birinin yanına açılan köprü sayısını koy.
   4. Çift sayılı adları **yıldız**la işaretle.
   5. Çiftlerin yarısını, teklerin bir artırılmışının yarısını yanlarına yaz.
   6. Bu son sütunu topla. Mecmû' başa yazılandan **bir eksik** ise yol vardır ve **yıldızlı** araziden başlar; **müsâvî** ise yol vardır ve **yıldızsız** araziden başlar; **fazla** ise yol yoktur.

   Königsberg: başa 8 yazılır; son sütun 3 + 2 + 2 + 2 = 9 > 8 ⟹ geçiş **asla** yapılamaz.

> **Cevher:** *Bir adın kaç kere yazılacağını, o araziye açılan köprülerin teklik-çiftliği ile yolun orada başlayıp başlamadığı tayin eder; bütün adların tekrarları toplanınca silsilenin boyunu aşmamalıdır.* Burhan, bir **sığma** burhânıdır.

**[N] Bütün hâlleri tek düsturda toplamak.** Euler'in dört ayrı hükmü şu tek münasebetin hâlleridir:

> **adın tekrar sayısı = (açılan köprü sayısı + o arazide bulunan yol ucu sayısı) ÷ 2**

⟸ Silsilenin ortasındaki her yazılış iki köprü harcar (biri varış, biri çıkış); yolun başı yahut sonu olan yazılış yalnız bir köprü harcar. Bir yolun **iki ucu** vardır (başlangıç ve son). Tek köprülü arazide bölme tam çıksın diye yol ucu sayısı tek, yâni **bir** olmak zorundadır ⟹ Euler'in "başlansın başlanmasın (köprü + 1) ÷ 2" hükmü buradan çıkar. Çift köprülü arazide yol ucu sayısı ya sıfırdır ya ikidir; Euler'in "orada başlarsa bir fazla" dediği hâlde yol orada **başlar ve orada biter** (iki uç). Bütün adlar toplanınca:

> **tekrarların mecmû'u = (2 × köprü sayısı + 2) ÷ 2 = köprü sayısı + 1**

ki bu, Bab 2'deki birinci kanunun ta kendisidir. Bu terkip tercümede yoktur; Euler'in hükümlerinden çıkarılmıştır.

---

## Bab 4 — İkinci misal: on beş köprü, altı arazi (aslın § 15)

**Şekil:** Su ile çevrili iki ada (aslın birinci ve ikinci arazisi); bu suya dört nehir dökülür; adaları çeviren su ve nehirler üzerinde **on beş köprü**. Su ile ayrılmış **altı arazi** vardır. Bu misalde arazilerin hususî adı yoktur; burada aslın sırasıyla **Birinci arazi … Altıncı arazi** denmiştir (birinci ve ikinci araziler iki adadır).

| Arazi | Açılan köprü | Yıldız | Adın tekrarı |
| :-- | :-- | :-- | :-- |
| Birinci arazi (ada) | 8 | yıldızlı | 4 |
| İkinci arazi (ada) | 4 | yıldızlı | 2 |
| Üçüncü arazi | 4 | yıldızlı | 2 |
| Dördüncü arazi | 3 | — | 2 |
| Beşinci arazi | 5 | — | 3 |
| Altıncı arazi | 6 | yıldızlı | 3 |
| **mecmû'** | **30** | | **16** |

**Hüküm:** başa 15 + 1 = 16 yazılır; son sütun 16 eder ⟹ **müsâvî** ⟹ yol vardır ve **yıldızsız** bir araziden, yâni Dördüncü yahut Beşinci araziden başlar.

**Euler'in verdiği yol** (adlar arasında geçilen köprüler; köprüler aslın küçük harfleriyle anılır, zîrâ onlar burada kemmiyet değil köprü adıdır):

> Beşinci —a— Altıncı —b— İkinci —c— Altıncı —d— Birinci —e— Altıncı —f— Üçüncü —g— Birinci —h— Üçüncü —i— Dördüncü —k— Birinci —m— Beşinci —n— Birinci —p— İkinci —o— Beşinci —l— Dördüncü

**Yoklama** [M5]: on altı ad (köprü + 1); on beş köprü, hiçbiri tekrar etmez (aslın harf dizisinde "j" yoktur); Birinci dört, İkinci iki, Üçüncü iki, Dördüncü iki, Beşinci üç, Altıncı üç defa geçer ⟹ cedvelin tekrar sütununun aynısı. Yol yıldızsız Beşinci'den başlar, öbür yıldızsız Dördüncü'de biter. **[N]** Not sahibi bu sayımı yol satırı üzerinde yeniden yapmış ve doğru bulmuştur; açılan köprülerin mecmû'u 30 = 2 × 15 olduğunu da yoklamıştır.

**Dikkat:** Harf tanıma bu yol satırını bozmuştu; satır mütercimin bilgisinden yazılmıştır ve sahife resmiyle harf harf karşılaştırılması **henüz yapılmamıştır**. Cedvelin son satırının harfi de taramada okunamamış; altıncı arazinin olduğu metinden ve mecmû'un tutmasından anlaşılmıştır [M5].

---

## Bab 5 — Kısa yol: tek köprülü arazilerin sayısı (aslın § 16 – § 20)

**İlliyet zinciri:**

1. **Müşahede (§ 16):** Bütün arazilerin açılan köprü sayıları toplanınca **köprü sayısının iki katı** çıkar ⟸ her köprü iki araziyi birleştirir ve her ikisinin hesabında birer kere sayılır.

   > **açılan köprülerin mecmû'u = 2 × köprü sayısı**

2. ⟹ (§ 17) Bu mecmû' **çifttir** ⟹ tek köprülü arazilerin sayısı **tek olamaz** (bir, üç, beş … olamaz) ⟹ tek köprülü araziler ya hiç yoktur ya **çift sayıdadır**. Königsberg'de dört tane (bütün araziler), ikinci misalde iki tane (Dördüncü ve Beşinci).
3. ⟹ (§ 18) Başa yazılan sayı = (açılan köprülerin mecmû'u + 2) ÷ 2 = köprü sayısı + 1.
4. **Hiç tek köprülü arazi yoksa:** yarıların mecmû'u = köprü sayısı = başa yazılandan bir eksik ⟹ yol **daima** vardır ve **hangi araziden** başlanırsa başlansın olur ⟸ her arazi çift köprülüdür, başlangıç neresi olsa "yıldızlı" şartı tutar. Misal: Königsberg'de **her köprüden iki kere** geçmek mümkündür ⟸ her köprü güya ikiye bölünür, bütün araziler çift köprülü olur.
5. **Tam iki tek köprülü arazi varsa (§ 19):** tekler bir artırılıp yarılandığı için mecmû'a iki yarım, yâni bir eklenir ⟹ mecmû' = köprü sayısı + 1 = başa yazılan ⟹ yol **daima** vardır ve tek köprülü arazilerden birinden başlar.
6. **Dört, altı, sekiz … tek köprülü arazi varsa:** mecmû' başa yazılanı **bir, iki, üç …** kadar aşar ⟹ yol **yoktur**.

   > **aşma miktarı = (tek köprülü arazi sayısı ÷ 2) − 1**

7. **Nihaî kaide (§ 20):**

   | Tek köprülü arazi sayısı | Hüküm |
   | :-- | :-- |
   | ikiden fazla | Yol **kat'iyetle yoktur** |
   | tam iki | Yol vardır; o ikisinden birinde başlar (öbüründe biter) |
   | sıfır | Yol vardır; **her** araziden başlanabilir |

> **Cevher:** *Bütün mesele tek bir sayıya iner: kaç arazinin köprü sayısı tektir?* Uzun cedvele bile lüzum kalmaz. Ve bu sayının tek olamayışı, "her köprünün iki ucu vardır" gibi apaçık bir hakikatten çıkar.

**[N] Bugünkü adlarıyla:** § 16'daki müşahede bugün "**el sıkışma kaziyyesi**" diye bilinir (düğüm derecelerinin mecmû'u kenar sayısının iki katıdır). § 20 bugün "**Euler yolu kaziyyesi**"dir [M6].

---

## Bab 6 — Yolun kendisini bulmak (aslın § 21)

1. Kaide yolun **varlığını** söyler, **şeklini** söylemez ⟹ ayrı bir sual kalır.
2. Euler'in tarifi: iki arazi arasındaki köprüleri, mümkün oldukça **ikişer ikişer zihnen kaldır** ⟹ köprü sayısı çoğu kere pek azalır ⟸ çift olarak kaldırılan köprüler hiçbir arazinin teklik-çiftliğini değiştirmez **[N: sebebin bu cümlesi not sahibinindir]**.
3. Kalan az köprüde yolu ara ⟹ kolayca bulunur.
4. Kaldırılan köprüleri geri koy ⟹ yolu "pek bozmaz"; dikkat eden derhal görür.
5. Euler fazlasını tavsiyeye lüzum görmez.

> **Dikkat [M6]:** Euler kaidenin **lüzum** tarafını (tek köprülü arazi ikiden fazla ⟹ yol yok) tam ispat etmiştir. **Kifâyet** tarafını (şart tutunca yol mutlaka vardır) § 18 – § 19'da "daima" diye **hükmeder**, § 21'de yalnız tarif eder; kat'î ispatını 1873'te **Carl Hierholzer** neşretmiştir (mütercimin bilgisi).

---

## Bab 7 — Tenkit ve gizli şartlar [N]

Bu bab tamamen not sahibinindir; talebenin Euler'i okurken düşmemesi gereken çukurları gösterir.

1. **Gizli şart: arazilerin birbirine bağlı olması.** Euler'in "daima yapılabilir" hükümleri, bütün arazilerin köprülerle **tek bir bütün** teşkil ettiğini zımnen farz eder. Şehir iki ayrı parçadan ibaretse (bir parçadan öbürüne hiç köprü yoksa), her arazi çift köprülü olsa bile yol yoktur. Bugünkü kaziyye bu sebeple "**bağlı** çizgede" diye söylenir. Bu şart risâlede yoktur, mütercim kayıtlarında da yoktur.
2. **§ 10'daki "yapılabilir" hükmü:** Bütün arazileri tek olan bir şehirde mecmû'un köprü + 1'e müsâvî olması, ancak **tam iki arazi** bulunduğunda mümkündür (Bab 5, 5. madde ile karşılaştır). Euler orada kifâyeti henüz ispatsız söyler.
3. **İspatın gücü ile zaafı ayrı tartılmalı:** "Yoktur" hükmü bir **sayım** ile kesinleşir; "vardır" hükmü bir **inşa** ister. Euler birincisini verir, ikincisine yol tarif eder.
4. **Harf meselesi [M1]:** Tercümede arazi adları harfle bırakılmıştır, zîrâ Euler'in usûlü bizzat "geçişleri harflerle yazmak"tır. Bu notta Padişahın kaidesi mûcibince adlar kelimeye çevrilmiştir; usûlün mânâsı değişmemiştir, çünkü usûlde mühim olan **adın kendisi değil, tekrarının sayısıdır**.

---

## Bab 8 — Kendini yoklama sualleri

1. Euler neden bütün yolları saymayı reddeder? *(Üç sebep: zahmet, büyük meselelerde imkânsızlık, sorulmayanı da bulmak.)*
2. Dokuz köprülü bir yol kaç adla yazılır? *(On.)*
3. Yedi köprülü bir arazinin adı yolda kaç kere geçer? *(Dört; başlangıçtan bağımsız.)*
4. Altı köprülü bir arazinin adı kaç kere geçer? *(Yol orada başlıyorsa dört, başlamıyorsa üç.)*
5. Tek köprülü arazilerin sayısı neden tek olamaz? *(Açılan köprülerin mecmû'u, köprü sayısının iki katı olduğu için çifttir.)*
6. Königsberg'de bir köprü yıkılsa yol mümkün olur mu? **[N]** *(Ada ile Şark arazisini birleştiren köprü yıkılırsa Ada dört, Şark arazisi iki köprülü olur; geriye iki tek köprülü arazi, Birinci ve İkinci kıyı kalır ⟹ yol vardır, kıyılardan birinde başlar. Hangi köprü yıkılırsa yıkılsın, iki arazinin teklik hâli değişir; dört tek köprülüden ikisi çifte dönerse yol doğar.)*
7. Euler'in neyi ispat etmediğini söyleyin. *(Kifâyet tarafı; ayrıca bağlılık şartını zikretmez.)*

---

## Ek — Adlar ve ıstılahlar

**Arazi adları** (yalnız aslıyla karşılaştırma için):

| Bu notta | Aslında | Ne olduğu [M2] |
| :-- | :-- | :-- |
| Ada | büyük harf "A" | Kneiphof adası; beş köprü |
| Birinci kıyı | büyük harf "B" | nehrin bir kıyısı; üç köprü |
| İkinci kıyı | büyük harf "C" | nehrin öbür kıyısı; üç köprü |
| Şark arazisi | büyük harf "D" | nehrin iki kolu arasındaki doğu arazisi; üç köprü |
| Birinci … Altıncı arazi | büyük harf "A" … "F" | § 15 misalinin altı arazisi |

**Königsberg köprüleri** [M2]: Ada ile Birinci kıyı arasında iki köprü (aslın "a" ve "b"si), Ada ile İkinci kıyı arasında iki (aslın "c" ve "d"si), Ada ile Şark arazisi arasında bir ("e"), Birinci kıyı ile Şark arazisi arasında bir ("f"), İkinci kıyı ile Şark arazisi arasında bir ("g").

**Istılahlar** (tercümenin cedvelinden): hendese-i vaz' (Latincesi geometria situs; bugün topoloji; teklif) · kemmiyet (nicelik; kadîm) · kemmiyetler hesabı · mesele (problem) · arazi (bölge; teklif) · geçiş · yol · harf silsilesi (silsile, lügat 11F27) · terkip (kombinasyon; lügat bab 05) · çift sayı / tek sayı · mecmû' (toplam; lügat 11B13) · kaide (kural) · ameliye (işlem). **[N]** Bugünkü karşılıklar için lügatin esas ıstılahları: çizge ⟶ "rabıta şekli" (teklif), düğüm ⟶ "re's" (kadîm), kenar ⟶ "dıl'" (kadîm).
