# Ders Notu — Euler 1741, Königsberg Köprüleri Meselesi

> **Kaynak:** [tercume/eserler/05_euler_1741_konigsberg_kopruleri.md](../tercume/eserler/05_euler_1741_konigsberg_kopruleri.md) — Euler, *Solutio problematis ad geometriam situs pertinentis*, Petersburg İlimler Akademisi Mecmûası, sekizinci cilt, 1741, sahife 128–140 (Eneström fihristinde 53 numara).
>
> **Bu not nasıl okunur?** Euler risâlesinde tek bir düstur yazmamış, her kaideyi kelimelerle söylemiştir. Bu notta Euler'in **her kaidesi bir düstur hâlinde** yazılmış, yanına Euler'in kendi cümlesi (bend numarasıyla) konmuş, sonra düsturun **nereden çıktığı** adım adım gösterilmiş ve **bir misal üzerinde hesaplanmıştır**. Düsturlarda harf yoktur, kelime vardır.
>
> **[N]** ile işaretli yerler not sahibinin izahıdır, Euler'de yoktur.

---

## 1. Mesele nedir?

**Şehir:** Königsberg'de Pregel nehri, Kneiphof adasını çevreler ve iki kola ayrılır. Nehirle birbirinden ayrılmış **dört arazi** vardır:

| Arazi | Euler'in harfi | Kendisine açılan köprü sayısı |
| :-- | :-- | :-- |
| Ada (Kneiphof) | A | 5 |
| Birinci kıyı | B | 3 |
| İkinci kıyı | C | 3 |
| Şark arazisi (iki kolun arası) | D | 3 |

**Köprüler** (yedi tane; § 6'dan ve mütercim kaydı [M2]'den):

| Köprü | Birleştirdiği araziler |
| :-- | :-- |
| a, b | Ada – Birinci kıyı |
| c, d | Ada – İkinci kıyı |
| e | Ada – Şark arazisi |
| f | Birinci kıyı – Şark arazisi |
| g | İkinci kıyı – Şark arazisi |

**Sual (§ 2):** Bir kimse yolunu öyle tertip edebilir mi ki **her köprüden bir kere ve yalnız bir kere** geçsin?

**Euler'in umûmîleştirmesi (§ 2):** Nehrin şekli, kolları ve köprülerin sayısı **ne olursa olsun**, böyle bir yolun var olup olmadığını bulmak.

**Niçin bütün yolları saymıyor? (§ 3)** Saymak cevabı verirdi; fakat (1) terkiplerin sayısı pek büyüktür, (2) köprü çoğalınca hiç yapılamaz, (3) sorulmayan pek çok şeyi de bulur. Euler, yolun **yalnız var olup olmadığını** söyleyen, fazlasını söylemeyen bir usul arar. Ve şunu tahmin eder: fazlasını söylemeyen usul daha basit olacaktır.

---

## 2. İlk tarif: arazinin "derecesi"

**[N]** Bütün hesap tek bir sayının etrafında döner. Ona bu notta **derece** diyoruz:

$$\text{derece}(\text{arazi}) = \text{o araziye açılan köprülerin sayısı}$$

Euler bu sayıya bir ad vermez, her defasında "o araziye açılan köprülerin sayısı" der. Biz kısaltmak için değil, düsturu okunur kılmak için ona bir ad veriyoruz.

Königsberg'de: derece(Ada) = 5, derece(Birinci kıyı) = 3, derece(İkinci kıyı) = 3, derece(Şark arazisi) = 3.

---

## 3. Birinci kanun: yolu harflerle yazmak ve harf sayısı

### Euler'in kodlaması (§ 4)

Bir köprüden geçiş, iki arazinin adıyla yazılır: **çıkılan arazi, varılan arazi**. Adadan Birinci kıyıya geçen yolcu için: "A B".

Ardışık iki geçişte ortadaki arazi ortaktır: Adadan Birinci kıyıya, oradan Şark arazisine giden yolcu "A B" ve "B D" yazmaz, **"A B D"** yazar. Çünkü ortadaki B hem birinci geçişte varılan, hem ikinci geçişte çıkılan arazidir.

### Kanun (§ 5)

> Euler: "Yolcu kaç köprüden geçerse geçsin, onun gidişi, köprülerin sayısından bir fazla olan bir sayıda harfle gösterilecektir."

$$\boxed{\;\text{silsiledeki harf sayısı} = \text{geçilen köprü sayısı} + 1\;}$$

### Niçin böyledir?

- Yolcu yola çıkarken bir harf yazılır: bulunduğu arazinin harfi. Henüz hiç köprü geçilmemiştir: **0 köprü, 1 harf.**
- Her köprü geçişinde **bir** yeni harf eklenir: varılan arazinin harfi. (Çıkılan arazinin harfi zaten yazılmıştır.)
- O hâlde her köprü harf sayısını bir artırır; başlangıçta bir harf vardır.

$$\text{harf sayısı} = 1 + \underbrace{1 + 1 + \cdots + 1}_{\text{köprü sayısı kadar}} = \text{köprü sayısı} + 1$$

### Misal (§ 5)

"A B D C" yolu: A'dan B'ye, B'den D'ye, D'den C'ye. Üç köprü, dört harf. ✔

### Königsberg'e tatbik

Yedi köprünün her birinden bir kere geçilecekse:

$$\text{harf sayısı} = 7 + 1 = 8$$

**Mesele şuna dönüştü (§ 7):** A, B, C, D harflerinden **sekiz harflik** bir silsile kurulabilir mi ki her arazi çifti, aralarındaki köprü sayısı kadar yan yana gelsin? Hangi köprüden geçildiğinin silsilede görünmesine lüzum yoktur (§ 6), çünkü sorulan şey yalnız her köprünün bir kere kullanılmasıdır.

Euler'in tertip sırası (§ 7): silsileyi kurmaya uğraşmadan **evvel**, kurulabilir olup olmadığı tartılır. İmkânsızsa bütün emek boşa gider.

---

## 4. İkinci kanun: bir arazinin harfi silsilede kaç kere geçer?

Euler burada şehrin tamamını bırakıp **tek bir araziye** bakar (§ 8). Çünkü bir harfin kaç kere yazılacağı yalnız o araziye açılan köprülere bağlıdır; o köprülerin öbür ucu nereye giderse gitsin hüküm değişmez (§ 10).

### 4-A. Derecesi tek olan arazi (§ 8)

> Euler: "Eğer köprülerin sayısı herhangi bir tek sayı ise, o zaman o sayıya bir eklenirse, yarısı, A harfinin kaç defa vâki olması gerektiğini verecektir."

$$\boxed{\;\text{harfin tekrar sayısı} = \frac{\text{derece} + 1}{2}\qquad(\text{derece tek ise})\;}$$

**Euler'in basamakları:**

| Derece | Euler'in hükmü | Düsturla |
| :-- | :-- | :-- |
| 1 | "A harfinin bir kere vâki olması lâzımdır" | (1 + 1) ÷ 2 = 1 |
| 3 | "A harfi iki kere vâki olacaktır" | (3 + 1) ÷ 2 = 2 |
| 5 | "A harfi üç kere vâki olmalıdır" | (5 + 1) ÷ 2 = 3 |

**Niçin? [N]** Silsilede A harfinin her yazılışına bakalım:

- A harfi silsilenin **ortasında** yazılmışsa, yolcu oraya bir köprüyle gelmiş ve bir köprüyle çıkmıştır: o yazılış **iki** köprü harcar.
- A harfi silsilenin **başında** (yolcu oradan yola çıkmıştır) yahut **sonunda** (yolcu orada durmuştur) yazılmışsa, o yazılış **bir** köprü harcar.

Derece tek ise, köprüler ikişer ikişer tükenemez; bir köprü artar ⟹ A harfi yolun **bir ucunda** bulunmak zorundadır (ya başında ya sonunda). O hâlde:

$$\text{derece} = 2 \times (\text{ortadaki yazılışlar}) + 1 \quad\Longrightarrow\quad \text{ortadaki yazılışlar} = \frac{\text{derece} - 1}{2}$$

$$\text{tekrar sayısı} = \text{ortadaki yazılışlar} + 1 = \frac{\text{derece} - 1}{2} + 1 = \frac{\text{derece} + 1}{2}$$

Bu hesap yolun A'dan başlayıp başlamamasına bağlı değildir. Euler de öyle der: "ister yolunu başlangıçta A'dan tertip etmiş olsun, ister olmasın".

### 4-B. Königsberg'in hükmü (§ 9)

$$\text{tekrar}(\text{Ada}) = \frac{5 + 1}{2} = 3, \qquad \text{tekrar}(\text{Birinci kıyı}) = \frac{3 + 1}{2} = 2$$

$$\text{tekrar}(\text{İkinci kıyı}) = \frac{3 + 1}{2} = 2, \qquad \text{tekrar}(\text{Şark arazisi}) = \frac{3 + 1}{2} = 2$$

$$\text{tekrarların mecmû'u} = 3 + 2 + 2 + 2 = 9$$

Fakat birinci kanuna göre silsile **sekiz** harftir. Dokuz harf sekiz yere sığmaz:

$$\boxed{\;9 > 8 \quad\Longrightarrow\quad \text{Königsberg'de böyle bir yol yoktur.}\;}$$

> Euler (§ 9): "Buradan aşikârdır ki Königsberg'in yedi köprüsünden böyle bir geçiş tertip edilemez."

Euler'in bütün burhânı bu tek mukayesedir [M4].

### 4-C. Bütün arazileri tek dereceli her şehir (§ 10)

$$\sum_{\text{her arazi}} \frac{\text{derece} + 1}{2} \;\;\text{ile}\;\; \text{köprü sayısı} + 1 \;\;\text{mukayese edilir:}$$

- **Müsâvî** ise: yol yapılabilir.
- **Büyük** ise: yol **asla** yapılamaz.

### 4-D. Derecesi çift olan arazi (§ 11 – § 12)

Burada başlangıç noktası hükme girer.

> Euler (§ 12): "köprülerin sayısı çift ise, başlangıç A arazisinden alınmadığı takdirde, o sayının yarısı A harfinin vâki olması gereken defaların sayısını verir; yolun başlangıcı bizzat A arazisinden alındığı takdirde ise, yarının bir artırılmışı …"

$$\boxed{\;\text{tekrar sayısı} = \frac{\text{derece}}{2}\quad(\text{yol orada başlamıyorsa})\;}$$

$$\boxed{\;\text{tekrar sayısı} = \frac{\text{derece}}{2} + 1\quad(\text{yol orada başlıyorsa})\;}$$

**Euler'in basamakları:**

| Derece | Yol orada başlıyor | Yol başka yerde başlıyor |
| :-- | :-- | :-- |
| 2 | 2 (bir çıkış, bir dönüş) | 1 (tek yazılış hem varış hem çıkış) |
| 4 | 3 | 2 |
| 6 | 4 | 3 |

**Niçin? [N]** Derece çift ise köprüler ikişer ikişer tükenebilir:

- Yol orada **ne başlıyor ne bitiyorsa**, her yazılış ortadadır ve iki köprü harcar: tekrar = derece ÷ 2.
- Yol orada **başlıyorsa**, baştaki yazılış bir köprü harcar; geriye tek sayıda köprü kalır, o hâlde yol orada **bitmek de** zorundadır (sondaki yazılış da bir köprü harcar). İki uç yazılışı + ortadakiler:

$$\text{derece} = 1 + 1 + 2 \times (\text{ortadakiler}) \Longrightarrow \text{tekrar} = 2 + \frac{\text{derece} - 2}{2} = \frac{\text{derece}}{2} + 1$$

### 4-E. Dört hâli birleştiren tek düstur [N]

Yukarıdaki dört hükmün hepsi şu tek münasebetten çıkar:

$$\boxed{\;\text{tekrar sayısı} = \frac{\text{derece} + \text{o arazideki yol ucu sayısı}}{2}\;}$$

Burada **yol ucu sayısı** 0, 1 yahut 2'dir (yol orada başlamıyor ve bitmiyorsa 0; ya başlıyor ya bitiyorsa 1; hem başlıyor hem bitiyorsa 2).

| Derece | Yol ucu sayısı | Düstur | Euler'in hükmü |
| :-- | :-- | :-- | :-- |
| tek | 1 (zorunlu) | (derece + 1) ÷ 2 | § 8 |
| çift | 0 | derece ÷ 2 | § 12, başlamıyorsa |
| çift | 2 | (derece + 2) ÷ 2 = derece ÷ 2 + 1 | § 12, başlıyorsa |

Bölmenin tam çıkması için **derece + yol ucu sayısı** çift olmalıdır. Tek dereceli arazide bu yüzden yol ucu tek olmak zorundadır: bir.

---

## 5. Altı adımlı ameliye (§ 13 – § 14)

Euler, yol tek bir araziden başlayabileceği için (§ 13) şu ameliyeyi kurar:

1. Su ile ayrılmış her araziye bir harf ver.
2. Köprü sayısını al, **bir ekle**, cedvelin başına yaz:
   $$\text{baş sayısı} = \text{köprü sayısı} + 1$$
3. Harfleri alt alta yaz; her birinin yanına **derecesini** yaz.
4. Derecesi çift olan harfleri **yıldız**la işaretle.
5. Her birinin yanına **yarı sayısını** yaz:
   $$\text{yarı sayısı} = \begin{cases} \dfrac{\text{derece}}{2} & \text{derece çift ise} \\[2mm] \dfrac{\text{derece} + 1}{2} & \text{derece tek ise} \end{cases}$$
6. Yarı sayılarını topla ve baş sayısıyla karşılaştır:

| Netice | Hüküm |
| :-- | :-- |
| mecmû' = baş sayısı − 1 | Yol vardır; **yıldızlı** (çift dereceli) bir araziden başlanır |
| mecmû' = baş sayısı | Yol vardır; **yıldızsız** (tek dereceli) bir araziden başlanır |
| mecmû' > baş sayısı | Yol **yoktur** |

**Niçin "bir eksik" ise yıldızlıdan başlanır?** Çünkü 5. adımda çift dereceli arazilere "yol orada başlamıyor" farzıyla derece ÷ 2 yazıldı. Yol bir yıldızlı araziden başlarsa, o arazinin tekrarı bir artar (§ 12) ve eksik olan bir kapanır (§ 13: "bu tarzda defaların sayısı bir artırılmalıdır").

### Königsberg ile ameliye (§ 14)

$$\text{baş sayısı} = 7 + 1 = 8$$

| Arazi | Derece | Yıldız | Yarı sayısı |
| :-- | :-- | :-- | :-- |
| A (Ada) | 5 | — | 3 |
| B (Birinci kıyı) | 3 | — | 2 |
| C (İkinci kıyı) | 3 | — | 2 |
| D (Şark arazisi) | 3 | — | 2 |
| **mecmû'** | | | **9** |

$$9 > 8 \Longrightarrow \text{yol yoktur.}$$

---

## 6. Çözülmüş ikinci misal: on beş köprü, altı arazi (§ 15)

**Şekil:** Su ile çevrili iki ada (A ve B), bu suya dökülen dört nehir, **on beş köprü**, su ile ayrılmış **altı arazi** (A, B, C, D, E, F).

$$\text{baş sayısı} = 15 + 1 = 16$$

| Arazi | Derece | Yıldız | Yarı sayısı | Hesap |
| :-- | :-- | :-- | :-- | :-- |
| A | 8 | ✱ | 4 | 8 ÷ 2 |
| B | 4 | ✱ | 2 | 4 ÷ 2 |
| C | 4 | ✱ | 2 | 4 ÷ 2 |
| D | 3 | — | 2 | (3 + 1) ÷ 2 |
| E | 5 | — | 3 | (5 + 1) ÷ 2 |
| F | 6 | ✱ | 3 | 6 ÷ 2 |
| **mecmû'** | **30** | | **16** | |

$$\text{mecmû'} = 16 = \text{baş sayısı} \Longrightarrow \text{yol vardır ve yıldızsız bir araziden (D yahut E) başlar.}$$

**Euler'in verdiği yol** (büyük harfler araziler, aralarındaki küçük harfler geçilen köprüler):

$$\text{E}\;a\;\text{F}\;b\;\text{B}\;c\;\text{F}\;d\;\text{A}\;e\;\text{F}\;f\;\text{C}\;g\;\text{A}\;h\;\text{C}\;i\;\text{D}\;k\;\text{A}\;m\;\text{E}\;n\;\text{A}\;p\;\text{B}\;o\;\text{E}\;l\;\text{D}$$

**Yolu yoklayalım (talebe bu yoklamayı kendi eliyle yapmalıdır):**

1. Büyük harflerin sayısı: 16 = 15 + 1. Birinci kanun ✔
2. Küçük harfler: a, b, c, d, e, f, g, h, i, k, m, n, p, o, l = 15 tane, hiçbiri tekrar etmiyor (aslın dizisinde "j" yoktur). Her köprü bir kere ✔
3. Her harfin tekrarı:

| Arazi | Silsiledeki yerleri (1'den 16'ya) | Tekrar | Cedveldeki yarı sayısı | Düsturla tahkik |
| :-- | :-- | :-- | :-- | :-- |
| A | 5, 8, 11, 13 | 4 | 4 | çift derece, yol ucu 0: 8 ÷ 2 = 4 ✔ |
| B | 3, 14 | 2 | 2 | 4 ÷ 2 = 2 ✔ |
| C | 7, 9 | 2 | 2 | 4 ÷ 2 = 2 ✔ |
| D | 10, 16 | 2 | 2 | tek derece, yol ucu 1 (son): (3 + 1) ÷ 2 = 2 ✔ |
| E | 1, 12, 15 | 3 | 3 | tek derece, yol ucu 1 (baş): (5 + 1) ÷ 2 = 3 ✔ |
| F | 2, 4, 6 | 3 | 3 | 6 ÷ 2 = 3 ✔ |

4. Yol yıldızsız E'den başlar, öbür yıldızsız D'de biter ✔

Mütercim bu satırı Internet Archive nüshasının 137. sahifesindeki matbu yolla harf harf karşılaştırmış, aynı bulmuştur [M5].

---

## 7. Kısa yol: tek dereceli arazilerin sayısı (§ 16 – § 20)

### 7-A. Derecelerin mecmû'u (§ 16)

> Euler: "bütün köprü sayıları birlikte toplanınca, köprülerin bütün sayısının iki katıdır … zîrâ her köprü birleştirdiği iki arazinin her birine nisbet olunur."

$$\boxed{\;\sum_{\text{her arazi}} \text{derece} = 2 \times \text{köprü sayısı}\;}$$

**Niçin?** Dereceleri toplarken her köprüyü, iki ucundaki arazilerin her birinin hesabında birer kere sayarız. O hâlde her köprü mecmû'a tam **iki** katkı yapar.

**Tahkik:** Königsberg: 5 + 3 + 3 + 3 = 14 = 2 × 7 ✔. İkinci misal: 8 + 4 + 4 + 3 + 5 + 6 = 30 = 2 × 15 ✔.

**[N]** Bu hakikat bugün "**el sıkışma kaziyyesi**" diye anılır: bir mecliste herkesin kaç kişiyle el sıkıştığı toplanırsa, toplam el sıkışma sayısının iki katı çıkar.

### 7-B. Tek dereceli araziler çift sayıdadır (§ 17)

Derecelerin mecmû'u çifttir (bir sayının iki katıdır). Çift sayıların mecmû'u daima çifttir; tek sayılardan ise ancak **çift adedi** toplanırsa çift çıkar. O hâlde:

$$\boxed{\;\text{tek dereceli arazilerin sayısı daima çifttir} \quad (0, 2, 4, 6, \ldots)\;}$$

> Euler (§ 17): "herhangi bir araziye açılan köprü sayıları arasında yalnız birinin tek olması mümkün değildir; üçünün tek olması da, beşinin de, ve saire."

Königsberg'de dört tek dereceli arazi vardır (A, B, C, D); ikinci misalde iki (D, E).

### 7-C. Baş sayısı derecelerden nasıl çıkar? (§ 18)

$$\text{baş sayısı} = \text{köprü sayısı} + 1 = \frac{\sum \text{derece}}{2} + 1 = \frac{\sum \text{derece} + 2}{2}$$

### 7-D. Yarı sayılarının mecmû'u nedir? [N, § 18 – § 19'un hesabı]

Tek dereceli arazilerin sayısına **tek sayısı** diyelim. 5. adımda çiftlerin yarısı, teklerin ise bir fazlasının yarısı alınmıştı. Her tek arazi, kendi derecesinin yarısından **yarım fazla** almış olur:

$$\sum \text{yarı sayısı} = \sum \frac{\text{derece}}{2} + \frac{\text{tek sayısı}}{2} = \text{köprü sayısı} + \frac{\text{tek sayısı}}{2}$$

Bunu baş sayısıyla karşılaştıralım:

$$\sum \text{yarı sayısı} - \text{baş sayısı} = \frac{\text{tek sayısı}}{2} - 1$$

Şimdi üç hâl:

| Tek sayısı | Fark | Ameliyenin hükmü | Euler |
| :-- | :-- | :-- | :-- |
| 0 | 0 ÷ 2 − 1 = **− 1** (bir eksik) | yol var, yıldızlıdan başla; bütün araziler yıldızlı ⟹ **her araziden** başlanabilir | § 18 |
| 2 | 2 ÷ 2 − 1 = **0** (müsâvî) | yol var, yıldızsızdan (iki tek araziden birinden) başla | § 19 |
| 4, 6, 8, … | **1, 2, 3, …** (aşar) | yol **yoktur** | § 19 |

> Euler (§ 19): "ikinci sütunda dört yahut altı yahut sekiz ve saire tek sayı bulunursa, o zaman üçüncü sütunun sayılarının mecmû'u başa yazılan sayıdan büyük olacak ve onu bir, yahut iki, yahut üç ve saire kadar aşacaktır."

Königsberg: tek sayısı = 4 ⟹ fark = 4 ÷ 2 − 1 = 1 ⟹ mecmû' baş sayısını **bir** aşar (9 = 8 + 1) ✔.

**Bir misal daha (§ 18):** Königsberg'de her köprüden **iki kere** geçmek mümkündür. Çünkü her köprü "güya ikiye bölünür"; her derece iki katına çıkar ve çift olur ⟹ tek sayısı = 0 ⟹ yol vardır.

### 7-E. Nihaî kaide (§ 20)

$$\boxed{\begin{array}{ll} \text{tek sayısı} > 2 & \Longrightarrow \text{yol kat'iyetle yoktur} \\ \text{tek sayısı} = 2 & \Longrightarrow \text{yol vardır; o iki araziden birinde başlar, öbüründe biter} \\ \text{tek sayısı} = 0 & \Longrightarrow \text{yol vardır; her araziden başlanabilir} \end{array}}$$

Artık uzun cedvele lüzum kalmamıştır: yalnız **kaç arazinin derecesi tek** olduğunu saymak kâfidir.

**[N] Niçin "o iki araziden birinde başlar, öbüründe biter"?** 4-E'deki tek düsturdan: tek dereceli bir arazide yol ucu sayısı bir olmak zorundadır. İki tek arazi varsa yolun iki ucu (başı ve sonu) tam o iki arazidedir.

---

## 8. Yolu fiilen bulmak (§ 21)

Kaide yolun **var olduğunu** söyler; **nasıl** gidileceğini söylemez. Euler'in tarifi:

1. İki arazi arasındaki köprüleri, mümkün olduğu kadar, **ikişer ikişer zihnen kaldır**.
2. Kalan az köprü üzerinde yolu ara; kolayca bulunur.
3. Kaldırılan köprüleri geri koy; bulunan yolu "pek bozmazlar".

**Niçin ikişer? [N]** Aynı iki arazi arasındaki iki köprüyü kaldırmak, o iki arazinin her birinin derecesini **iki** azaltır; derecenin tek yahut çift oluşu değişmez. O hâlde tek sayısı, yâni yolun var olup olmadığı hükmü, kaldırmadan sonra da aynı kalır. Geri koyarken: yolun o iki araziden birine uğradığı yerde "öbür araziye git, hemen geri dön" diye iki köprü eklenir.

**Misal [N]:** Königsberg'de her köprüyü iki kere geçen yol (7-D'deki misal). Önce her köprünün ikinci nüshasını zihnen kaldır; geriye asıl yedi köprü kalır. Sonra yukarıdaki "git, geri dön" eklemesini her köprü için yap. Talebe bu yolu kendisi yazmalıdır (cevap Bab 10'dadır).

---

## 9. Euler neyi ispat etti, neyi etmedi? [N]

| Hüküm | Euler'de | İzah |
| :-- | :-- | :-- |
| Tek sayısı ikiden fazla ise yol **yoktur** | **tam ispat** (§ 9 – § 19) | Bir sığma burhânıdır: yarı sayıların mecmû'u, silsilenin boyunu aşar. |
| Tek sayısı 0 yahut 2 ise yol **vardır** | **hüküm**, ispatsız (§ 18 – § 19 "daima"); § 21'de yalnız tarif | Kat'î ispatı 1873'te **Carl Hierholzer** neşretti [M6]. |
| **Gizli şart:** bütün araziler köprülerle tek bir bütün teşkil etmeli | **zikredilmez** | Şehir köprüyle birbirine bağlanmayan iki parçadan ibaretse, bütün dereceler çift olsa bile yol yoktur. Bugünkü kaziyye bu yüzden "**bağlı** çizgede" diye söylenir. Mütercim bu şartı [M6]'ya eklemiştir. |

**Bugünkü dille [M6]:** araziler **düğüm**, köprüler **kenar**, derece **düğümün derecesi**dir; § 20 "**Euler yolu kaziyyesi**"dir. Bu risâle çizgeler nazariyesinin ve hendese-i vaz'iyyenin (topolojinin) ilk metni sayılır. Leibniz'in adını koyduğu fakat misalini vermediği *geometria situs* (§ 1) ilk numûnesini burada bulmuştur: ölçü ve hesap yoktur, yalnız **hangi şeyin hangisine bağlı olduğu** vardır.

---

## 10. Çalışma sualleri ve cevapları

1. **Dokuz köprülü bir yol kaç harfle yazılır?**
   Birinci kanun: 9 + 1 = **10**.

2. **Derecesi 7 olan arazinin harfi kaç kere geçer?**
   Tek derece: (7 + 1) ÷ 2 = **4**; yolun nereden başladığına bakılmaz.

3. **Derecesi 6 olan arazinin harfi kaç kere geçer?**
   Yol orada başlamıyorsa 6 ÷ 2 = **3**; başlıyorsa 6 ÷ 2 + 1 = **4** (o zaman yol orada biter de).

4. **Derecelerin 3, 3, 4, 4, 5, 5 olduğu bir şehirde yol var mıdır?**
   Tek dereceliler: 3, 3, 5, 5 ⟹ tek sayısı = 4 > 2 ⟹ **yoktur**. Tahkik: köprü sayısı = (3 + 3 + 4 + 4 + 5 + 5) ÷ 2 = 12; baş sayısı = 13; yarı sayıları 2 + 2 + 2 + 2 + 3 + 3 = 14; fark = 14 − 13 = 1 = 4 ÷ 2 − 1 ✔.

5. **Königsberg'de bir tek köprü yıkılsa yol doğar mı?**
   Hangi köprü yıkılırsa yıkılsın, iki ucundaki arazinin derecesi birer azalır ve tekten çifte döner. Dört tek araziden ikisi çifte dönünce tek sayısı = 2 ⟹ yol **vardır** ve kalan iki tek araziden birinde başlar. Misal: e köprüsü (Ada – Şark arazisi) yıkılırsa derece(Ada) = 4, derece(Şark) = 2; tekler Birinci ve İkinci kıyıdır. Bir yol: B a A c C g D f B b A d C (her köprü bir kere; 6 köprü, 7 harf ✔).

6. **Königsberg'de her köprüden iki kere geçen bir yol yazınız (Bab 8).**
   Her köprü iki nüsha sayılınca köprü sayısı 14, bütün dereceler çift olur (Ada 10, Birinci kıyı 6, İkinci kıyı 6, Şark 6) ⟹ tek sayısı = 0 ⟹ yol vardır ve her araziden başlanabilir. Birinci kanuna göre yol 14 + 1 = **15 harfle** yazılır. Bir cevap:
   **A a B b A c C d A e D f B a A b B f D g C c A d C g D e A**
   Yoklama: köprüler sırasıyla a, b, c, d, e, f, a, b, f, g, c, d, g, e ⟹ 14 köprü; a, b, c, d, e, f, g her biri **iki kere** ✔; harf sayısı 15 ✔; Ada'nın harfi A, 10 ÷ 2 + 1 = **6** kere geçer (başladığı için bir fazla) ve yol yine A'da biter ✔.

7. **Euler neyi ispat etmemiştir?**
   Yolun **var olduğu** tarafını (Hierholzer 1873) ve arazilerin birbirine **bağlı** olması şartını zikretmemiştir.

---

## Ek — Istılahlar

| Latince | Bugünkü Türkçe | Tercümedeki karşılık |
| :-- | :-- | :-- |
| geometria situs | konum geometrisi (topoloji) | hendese-i vaz' |
| quantitas | nicelik | kemmiyet |
| problema | problem | mesele |
| regio | bölge | arazi |
| series litterarum | harf dizisi | harf silsilesi |
| combinatio | kombinasyon | terkip |
| numerus par / impar | çift / tek sayı | çift sayı / tek sayı |
| summa | toplam | mecmû' |
| regula | kural | kaide |
| operatio | işlem | ameliye |
| [N] gradus | derece | derece (bu notun adı; Euler'de yok) |
