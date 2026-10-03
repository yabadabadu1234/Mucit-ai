# 2609.04086 — Tercüme, Kısım 1 (kaynak satır 1–628)

> Kaynak: arXiv LaTeX (temizlenmiş, 2823 satır). Çeviri yapay zekâ çevirisidir, insan doğrulaması yoktur. Çevirenin düşen notları `[Çevirenin notu: …]` ile ayrılmıştır; metnin parçası değildir.

# Formüle Edilemeyen Bir Teorem (A Non-Formulable Theorem)

## Özet
Tutarlı ve yeterince anlatım gücü olan her sonlu sentaktik sistem $\mathcal{S}$ için, $\mathcal{S}$'nin özerk olarak üretemeyeceği en az bir teoremin varlığını ispatlıyoruz. Sonuç bir üst-teoremdir (metateorem): bir teoremin varlığını ispatlar ve her sonlu sentaktik sisteme uygulanır — güvenlik mekanizmaları, yapay zekâ sistemleri, biçimsel doğrulayıcılar, hukuk sistemleri, iktisadî modeller ve kendisinin ispatlandığı biçimsel sistem dahil.

*(Dipnot: Ana sonuçlardan bazıları özellikle yoğun bir mantıksal yapı gösterir; bu yüzden ilgili ispatlar anlatım açıklığı için numaralı adımlarla düzenlenmiştir.)*

## 1. Giriş
Buono 2026 (SIP) ile tanıtılan ve Buono 2026 (engel) ile genelleştirilen **Sentaktik Değişmezlik İlkesi (SIP)**, semboller üzerinde işleyen yerel bir sentaktik sistemin, gözlem seviyesinin üstünde yaşayan anlamsal özelliklere yapısal olarak kör olduğunu kurar. Terimlerin bir $P$ özelliği ilk cümle kümesinde geçerliyse ve her yeniden yazma kuralı tarafından korunuyorsa, türetilebilir her cümlecikteki her terim $P$'yi sağlar — özellik "donmuştur" ve $P$'yi ihlal eden hedef yalnız ulaşılmamış değil, kalıcı olarak ulaşılamazdır.

Bu makale bu ilkeyi içe çevirir: sistemin göremediği anlamsal özellik, **sistemin kendisinin bir özelliği** olduğunda ne olur? Özellikle: sonlu bir sentaktik sistem kendi sentaktik sınırlarının varlığını ileri süren bir önermeyi özerk olarak formüle edip türetebilir mi?

Cevap hayırdır ve sebep yapısaldır, arızî değil.

Argüman safhalar hâlinde ilerler. Birincisi, SIP sentaktik değişmezlerin —sistemin içerdiği ama yeniden yazamadığı donmuş alt terimler üreten özelliklerin— varlığını garanti eder. İkincisi, bu donmuş alt terimlerin varlığını ileri süren önerme anlamsal olarak doğrudur (SIP bunu garanti eder) ama özerk olarak türetilemez (onu formüle etmek sistem hakkında üst-konuşma gerektirir; bu, sistemin yeniden yazma kurallarının ulaşmadığı bir seviyedir). Üçüncüsü, Gödel numaralandırması ve Kleene sabit-nokta teoremi bu sınırı kodlayan kendine-atıflı bir $G_{\mathcal{S}}$ önermesi üretir ve standart köşegenleştirme argümanı $G_{\mathcal{S}}$'nin karar verilemez olduğunu gösterir. Dördüncüsü, süreç genişletilemezdir: sistemi $G_{\mathcal{S}}$'yi türetecek şekilde genişletmek, kendi karar verilemez önermesi olan yeni bir sistem yaratır. Zincir hiç kapanmaz.

Sonuç, sonlu sentaktik sistemler olarak gerçeklenebilen yapay zekâ sistemleri (sinir ağları, dil modelleri, belirleyici algoritmalar) dahil her sonlu sentaktik sisteme uygulanır. Netice kesindir: sonlu bir sistem en az bir teoremi **ortaya çıkaramaz** (ideare): kendi öz sınırlarının varlığını ileri süren teoremi. Böyle bir teoremi dışarıdan iletilirse **anlayabilir**, fakat özerk olarak üretemez.

## 2. Ön bilgiler ve gösterim
- $\mathcal{S} = (V, F, R, I)$: sonlu sentaktik sistem;
- $\vdash_{\mathcal{S}}$: $\mathcal{S}$'de türetilebilirlik bağıntısı;
- $\Rightarrow$: tek yeniden yazma adımı; $\Rightarrow^*$: sonlu yeniden yazma adımları dizisi;
- $\ulcorner\psi\urcorner$: $\psi$ önermesinin Gödel numarası;
- $\llbracket t \rrbracket$: $t$ teriminin anlamsal yorumu.

Sonlu bir sentaktik sistem, bir $\phi$ önermesini, $\phi$ sistemden sentaktik olarak türetilebiliyorsa, yani $R$'nin kurallarından kurulabilen biçimsel bir ispat varsa **özerk olarak üretir**. Türetilebilir terimler kümesi:
$$\mathrm{Der}(I, R) = \{t : I\text{'dan } t\text{'ye sonlu bir yeniden yazma dizisi vardır}\}.$$

## 3. Temeller
### 3.1 Sonlu sentaktik sistemler
**Tanım 1 (Sonlu sentaktik sistem).** $\mathcal{S} = (V, F, R, I)$ dörtlüsü, şunlarla:
- $V$: değişkenlerin sonlu kümesi $\{v_1,\dots,v_n\}$;
- $F$: her biri sonlu aritili fonksiyon sembollerinin sonlu kümesi $\{f_1,\dots,f_m\}$;
- $R$: $l \to r$ biçiminde yeniden yazma kurallarının sonlu kümesi; $l, r$, $V \cup F$ üzerinde terimlerdir;
- $I$: ilk cümleciklerin (kapalı terimler veya atomik formüller) sonlu kümesi.

$\mathcal{S}$'nin *derinliği* $\max(|V|, |F|, |R|, |I|)$'dir. $\mathcal{S}$'nin her unsuru sonlu olarak belirtilebilir ve hesaplanabilirdir.

**Tanım 2 (Türetim ve hesaplanabilirlik).** $C$ bir cümlecik (terim veya formül) olsun. *Türetim*,
$$C = C_0 \Rightarrow C_1 \Rightarrow \cdots \Rightarrow C_n = C'$$
dizisidir; her $C_i \Rightarrow C_{i+1}$ adımı bir $l \to r \in R$ kuralının bir ikamesini $C_i$'nin bir alt-geçişine uygular.

*Türetilebilirlik bağıntısı:* $\mathcal{S} \vdash \psi \iff I$'dan $\psi$'yi üreten bir türetim vardır.

Bir $\mathcal{S}$ sistemi, ($\mathcal{S}$'de uygun bir olumsuzlama kavramı için) hem $\mathcal{S} \vdash \psi$ hem $\mathcal{S} \vdash \neg\psi$ olacak bir $\psi$ cümleciği yoksa *tutarlıdır*.

**Tanım 3 (Alt terimler ve geçişler).** $t = f(t_1,\dots,t_k)$ bir terim olsun. $t$'nin *alt terimleri* kümesi
$$\mathrm{Subterms}(t) := \{t\} \cup \bigcup_{i=1}^{k} \mathrm{Subterms}(t_i).$$
$t$ içinde bir $s$ alt teriminin bir *geçişi (occurrence)*, o konumdaki alt terimin $s$ olduğu bir $p$ konumudur (sonlu bir indis dizisi).

**Tanım 4 (Skolem sabitleri ve donmuş terimler).** *Skolem sabiti*, $R$'nin hiçbir kuralında görünmeyen, aritisi $0$ olan bir $a \in F$ sembolüdür (sisteme "yabancı sembol"). Bir $t$ terimi, bir Skolem sabiti içeren her alt terimi $R$'deki hiçbir kuralın sol tarafıyla birleşmiyorsa (unify) $R$'ye göre *donmuştur*. Donmuş terimler yeniden yazılamaz, çünkü sistemin tanımadığı sentaktik işaretler içerirler.

## 4. Sentaktik değişmezler ve Sentaktik Değişmezlik İlkesi
**Tanım 5 (Sentaktik özellik).** *Sentaktik özellik*, yalnızca terimlerin sentaktik yapısına (anlamsal yorumlarına değil) bağlı olan $P : \mathrm{Terms} \to \{\text{doğru}, \text{yanlış}\}$ yüklemidir. Örnekler: $P(t)=$ "$t$ bir Skolem sabiti içerir"; $P(t)=$ "$t$'nin derinliği $\leq 3$"; $P(t)=$ "$t$ donmuştur".

**Lemma 1 (Korunum lemması).** $P$ bir sentaktik özellik, $\mathcal{S}$ sonlu sentaktik sistem olsun. Şu iki şart:
- (Temel) Her $C \in I$ ve her $t \in \mathrm{Subterms}(C)$ için $P(t)$ geçerli;
- (Adım) Her $l \to r \in R$ ve her $\sigma$ ikamesi için $P(l\sigma) \Rightarrow P(r\sigma)$;

geçerliyse, her $C \Rightarrow^* C'$ türetimi ve her $t' \in \mathrm{Subterms}(C')$ için $P$ korunur.

*İspat.* Türetimin uzunluğu üzerinden tümevarım. $P$ her adımda korunur: çünkü terim ya dokunulmamıştır ($P$ kalır) ya da $P$'yi koruyan bir kurala göre yeniden yazılır. ∎

**Lemma 2 (SIP; Buono 2026, Lemma 5).** Bir $P$ özelliği $\mathcal{S}$ için sentaktik değişmezse (yukarıdaki Temel ve Adım'ı sağlıyorsa), her $C \in \mathrm{Der}(I,R)$ ve her $t \in \mathrm{Subterms}(C)$ için $P(t)$ geçerlidir ve her türetim boyunca doğru kalır. Sentaktik değişmezler "donmuş" özelliklerdir: bir kez doğru olunca, uygulanan kurallar ne olursa olsun bütün hesaplama boyunca doğru kalırlar.

**Sonuç.** $t$ terimi donmuşsa (hiçbir kuralın sol tarafıyla birleşmiyorsa) ve bir Skolem sabiti içeriyorsa, "Skolem sabiti içerir" özelliği o terim için bir sentaktik değişmezdir.

**Tanım 6 (Sentaktik kör nokta).** $t$ terimi, şunlar sağlanırsa $\mathcal{S}$'nin *sentaktik kör noktasıdır*: (1) $t$, $I$'dan türetilebilir; (2) $P(t)$'nin geçerli olduğu ve $P$'nin sentaktik değişmez olduğu bir sentaktik özellik $P$ vardır; (3) $P(t)$'nin geçerli olduğu bilgisi $\mathcal{S}$ sistemi tarafından iletilemez: "$P(t)$" önermesi yapısal sebeplerle $\mathcal{S}$'de türetilemez. Sistem terimi "görür" ama değişmez özelliği hakkında "konuşamaz".

## 5. Sentaktik sistemler için Gödel numaralandırması
**Tanım 7 ($\mathcal{S}$ için standart Gödel kodlaması).** $g : \mathcal{S}$'nin unsurları $\to \mathbb{N}$ birebir eşlemesini şöyle tanımlayın:
$g(v_i) := 2^i$ (değişkenler); $g(f_j) := 3 \cdot 5^j$ (fonksiyon sembolleri); $g(r_k) := 7 \cdot 11^k$ (kurallar); $g(f(t_1,\dots,t_n)) := g(f) \cdot \prod_{i=1}^{n} p_i^{g(t_i)}$ (bileşik terimler); $p_i$, $i$-inci asaldır. $\mathcal{S}$ üzerinde bir $\psi$ mantık formülü için $g(\psi) := \ulcorner\psi\urcorner :=$ $\psi$'nin bileşenlerinin bileşik kodlaması.

Özellikler: $g$ birebirdir, hesaplanabilirdir (verilen $\ulcorner\psi\urcorner$'dan $\psi$ polinom zamanda çözülebilir) ve evrenseldir ($\mathcal{S}$'nin her yapısal unsuru temsil edilebilir).

**Tanım 8 (Kodlanmış türetilebilirlik yüklemi).**
$$\mathrm{Deriv}_{\mathcal{S}}(n) := \begin{cases}\text{doğru} & n\text{'nin kodladığı önerme } \mathcal{S}\text{'den türetilebiliyorsa},\\ \text{yanlış} & \text{aksi hâlde.}\end{cases}$$
$\mathrm{Deriv}_{\mathcal{S}}$ hesaplanabilirdir (Turing-karar verilebilir), çünkü $\mathcal{S}$ sonludur, hesaplama belirleyicidir ve $\mathcal{S}$'deki bütün olası türetimler sıralanabilir.

[Çevirenin notu: Bu "karar verilebilir" iddiası gerekçesiyle kuşkuludur. Sonlu bir kural kümesi bile Turing-tam olabildiğinden, türetilebilirlik genelde yalnız yarı-karar verilebilirdir (sıralanabilir ama "hayır" cevabı hesaplanamaz). Okuyucu tenkidi KUNYE'dedir.]

**Teorem 1 (Köşegenleştirmeyle kendine-atıflı inşa).** $\mathcal{S}$, Gödel numaralandırması (Tanım 7) mevcut olan sonlu bir sentaktik sistem olsun. Her hesaplanabilir $\varphi : \mathbb{N} \to \mathrm{Formulas}(\mathcal{S})$ fonksiyonu için
$$\psi \;\leftrightarrow\; \varphi(\ulcorner\psi\urcorner)$$
olan bir $\psi$ cümlesi vardır. Yani $\psi$, $\varphi$'nin $\psi$'nin kodu hakkında söylediğini "kendisi hakkında söyler". Bu, Gödel numaralandırmasını temsil edecek kadar aritmetik içeren her sistemde geçerli olan köşegen lemmasıdır (kendine-atıf lemması veya Gödel sabit-nokta lemması da denir).

**Not 1 (Kendine-atıf neden gerekli).** Sınır önermesi $\phi_{\mathcal{S}}$ (Tanım 9, Bölüm 6) donmuş terimlerin var olduğunu ileri sürer. Tek başına bu, $\mathcal{S}$ hakkında üst-seviye bir gözlemdir ve eksikliği kurmaya yetip yetmediği sorulabilir. Yetmez, çünkü karar verilemezlik argümanı (Teorem 2) *kendi türetilebilirlik durumuna atıf yapan* bir önerme gerektirir: ispatın Durum 1'i, $G_{\mathcal{S}}$'yi türetmenin sistemin kendi seviyesini aşmış olması anlamına geleceğini gösterir ve bu argüman tam olarak $G_{\mathcal{S}}$ "kendi içeriğim türetilemez" dediği için işler. Kendine-atıf olmadan $\phi_{\mathcal{S}}$ tek başına doğru bir üst-seviye ifade olurdu; ancak sistemin onu türetememesinden sistemin salt belirli bir aksiyomdan yoksun olmadığı, *yapısal olarak* eksik olduğu sonucu çıkarılamazdı. Kendine-atıflı sarmalama, üst-seviye bir gözlemi, türetilebilirlik durumu her iki yönde de çelişki doğuran *sistemin kendi dilinde* bir önermeye çevirir.

## 6. Sınır önermesi
**Tanım 9 (Sınır önermesi $\phi_{\mathcal{S}}$).** $P_{\mathcal{S}}$, Buono 2026'daki gibi inşa edilmiş $\mathcal{S}$'nin belirli bir sentaktik değişmezi olsun: hiçbir sol tarafla birleşmeyen, Skolem sabiti içeren alt terimler. Tanımlayın:
> $\phi_{\mathcal{S}} :=$ "$I$'dan türetilebilir, şunları sağlayan bir $t$ alt terimi vardır: (1) $P_{\mathcal{S}}(t)$ geçerlidir (sentaktik değişmez özellik); (2) her $l \to r \in R$ için $t$, $l$ ile birleşmez (donmuştur); (3) bu yüzden $t$, $R$'deki hiçbir kural tarafından yeniden yazılamaz."

$\phi_{\mathcal{S}}$, Lemma 2 gereği *anlamsal olarak doğrudur*: sentaktik değişmez böyle terimlerin varlığını garanti eder. Fakat $\phi_{\mathcal{S}}$, şu sebeple $\mathcal{S}$ tarafından *özerk olarak türetilemez*. $\mathcal{S}$'deki bir türetim, $l \to r \in R$ kural uygulamalarının sonlu bir dizisidir. Her kural terimler üzerinde işler, alt terimleri sentaktik örüntü eşlemeye göre yeniden yazar. Oysa $\phi_{\mathcal{S}}$ önermesi, *kuralların kendileri* hakkında bir olgu ileri sürer: belirli terimlerin hiçbir sol tarafla birleşmediğini. Bu, $R$'nin yapısı hakkında bir ifadedir; $R$'nin üzerinde işlediği dilin içinde bir ifade değildir. Onu üretmek, sistemin kendi kural kümesini dışarıdan incelemesini —sistemin içerdiği (donmuş $t$ terimi) ile yapabildiği (yeniden yazma) arasındaki boşluğu gözlemlemesini— gerektirir. $R$'deki hiçbir kural bu incelemeyi yapmaz, çünkü kurallar terimlere etki eder, kendilerine değil.

**Örnek 1 (Buono 2026'dan somut örnekleme).** $\mathcal{S}$ şöyle tanımlansın: $R = \{0 + x \to x,\; s(x) + y \to s(x + y)\}$, $I = \{0, s(0), s(s(0)), \ldots\}$. $F$'de olmayan $a, b$ Skolem sabitlerini ekleyin. O zaman:
- $a + b$ terimi $0 + x$ ile birleşmez ($a \neq 0$ olduğundan) ve $s(x) + y$ ile de birleşmez ($a$, $s(\cdot)$ biçiminde olmadığından).
- Bu yüzden $a + b$ donmuştur: "$P(t) = t$ bir Skolem sabiti içerir" özelliği sentaktik bir değişmezdir.
- $\phi_{\mathcal{S}} =$ "bir Skolem sabiti içeren donmuş bir terim vardır" önermesi doğrudur.
- Ama $\mathcal{S}$, $\phi_{\mathcal{S}}$'yi biçimsel olarak türetemez; çünkü Skolem sabitleri sistemin sözcük dağarcığına dışarıdandır.

## 7. Kendine-atıflı önerme
**Tanım 10 (Kendine-atıflı $G_{\mathcal{S}}$ önermesi).** Tanım 7'deki Gödel numaralandırmasını kullanarak, Gödel numarası $n^* = \ulcorner G_{\mathcal{S}} \urcorner$ olan $G_{\mathcal{S}}$ önermesini şöyle tanımlayın:
> $G_{\mathcal{S}} :=$ "Gödel numarası $n^*$ olan önerme şunu kodlar: $\phi_{\mathcal{S}}$'nin doğru ama $\mathcal{S}$'den türetilemez olduğu bir $P_{\mathcal{S}}$ sentaktik değişmezi vardır."

Özet biçimde: $G_{\mathcal{S}} \equiv$ "Kendi içeriğimin (sistemin bir sınırının) sistem tarafından ispatlanamaz olduğunu ileri sürüyorum."

**Lemma 3 (Köşegen lemmasıyla $G_{\mathcal{S}}$'nin varlığı).** Teorem 1'e göre, $\varphi(n) :=$ "$n$'nin kodladığı önerme, $\mathcal{S}$'nin türetemeyeceği bir sınırı ileri sürer" hesaplanabilir fonksiyonuna uygulandığında, $G_{\mathcal{S}} \leftrightarrow \varphi(\ulcorner G_{\mathcal{S}} \urcorner)$ olan bir $G_{\mathcal{S}}$ cümlesi vardır. Yani $G_{\mathcal{S}}$ kendi hakkında tam olarak $\varphi$'nin kodu hakkında söylediğini söyler: "$\mathcal{S}$'nin türetemeyeceği bir sınırı kodluyorum." $G_{\mathcal{S}}$'nin varlığı, Teorem 1'in anlatım gücü hipotezini sağlayan her sonlu sentaktik $\mathcal{S}$ sistemi için garanti edilir.

## 8. $G_{\mathcal{S}}$'nin karar verilemezliği
**Teorem 2 ($G_{\mathcal{S}}$'nin karar verilemezliği).** Tutarlı bir $\mathcal{S}$ sistemi için: $\mathcal{S} \not\vdash G_{\mathcal{S}}$ ve $\mathcal{S} \not\vdash \neg G_{\mathcal{S}}$.

*İspat.*
**Durum 1: $\mathcal{S} \vdash G_{\mathcal{S}}$ olsun.** $\mathcal{S}$, $G_{\mathcal{S}}$'yi türetirse: (1) $\mathcal{S}$ şu önermeyi türetir: "$\mathcal{S}$'nin ispatlayamayacağı bir sınır vardır." (2) Bunu yaparken $\mathcal{S}$, $\mathcal{S}$'nin sentaktik uzayında bulunan bir $I \Rightarrow^* G_{\mathcal{S}}$ türetimi üretmiştir. (3) Ancak $G_{\mathcal{S}}$'nin içeriği, türetilemez bir anlamsal doğrunun ($\phi_{\mathcal{S}}$) varlığını ileri sürer.

$\mathcal{S} \vdash G_{\mathcal{S}}$ ise $\mathcal{S}$ kendi sentaktik seviyesini aşmış olur. Lemma 2 gereği sentaktik değişmezler sentaktik seviyede donmuş kalır. Fakat $G_{\mathcal{S}}$, anlamsal olarak doğru olan ile sentaktik olarak türetilebilir olan arasında —tanımı gereği yalnızca sentaktik seviyede bulunan hiçbir sistemin kapatamayacağı— bir boşluktan söz eder. $\mathcal{S}$'deki türetim sentaktik yeniden yazmaların sonlu dizisidir. Sentaktik manipülasyonların hiçbir sonlu dizisi, sentaktik seviyeyi terk etmeden kendi anlamsal eksikliği hakkında bir ifade üretemez.

> **Çelişki: sentaktik bir sistem kendi seviyesini aşamaz.**

**Not 2 (Çelişki neden yalnız köşegensel değil, yapısaldır).** Durum 1'deki çelişki, kendine-atıflı kodlamanın bir oyunu değildir (köşegen lemmanın tek başına çelişki ürettiği standart Gödelci argümandaki gibi). Çelişki, $\mathcal{S}$'nin yerel yeniden yazma kuralları sistemi olan özel yapısının sonucudur.

Gerekçe bu makalede zaten mevcuttur ve şöyle yürür. Tanım 1 gereği $R$'deki her kural yerel bir işlemdir: bir $l$ örüntüsünü bir alt terimle eşler ve onu $r$'ye yeniden yazar. Tanım 9 gereği $\phi_{\mathcal{S}}$ önermesi (ve dolayısıyla onu kodlayan $G_{\mathcal{S}}$) $R$'nin *küresel* bir özelliğini ileri sürer: belirli terimler *hiçbir* kuralın *hiçbir* sol tarafıyla birleşmez. Bu, tek bir yeniden yazma adımı hakkında değil, bütün kurallar hakkında aynı anda bir ifadedir. SIP (Lemma 2) köprüdür: bu küresel özelliğin yalnız tek adım için değil, *her* uzunluktaki *her* türetim için geçerli olduğunu garanti eder.

$G_{\mathcal{S}}$'yi türetmek, sistemin sonlu bir yerel yeniden yazma adımı dizisiyle kendi kural kümesinin küresel yapısı hakkında bir sonuç üretmesini gerektirirdi. Ama her adım yalnız eşleştiği örüntüyü görür, $R$'nin bütününü değil. Sistemin, bütün olası türetimler üzerinde işleyen bir tümevarım ilkesine ihtiyacı olurdu — ve bu ilke tam olarak SIP'in *dışarıdan* sağladığıdır. $\mathcal{S}$'nin içinde böyle bir ilke yoktur, çünkü kurallar terimlere etki eder, kural kümesinin kendisine değil.

Yerel–küresel boşluğa başvurmadan çelişkiyi verecek alternatif, tamamen biçimsel bir kapanış standart Gödelci yoldan ($\mathcal{S}$'nin $\Sigma_1$-tamlığı) mevcuttur. Mevcut argüman, çelişkinin *neden* doğduğunu —kurnaz bir kodlamadan değil, yerel kuralların küresel öz-bilgi üretememesinden— tespit ettiği için tercih edilir. SIP'in klasik eksiklik çerçevesine kattığı içerik budur.

**Durum 2: $\mathcal{S} \vdash \neg G_{\mathcal{S}}$ olsun.** $\mathcal{S}$, $\neg G_{\mathcal{S}}$'yi türetirse şunu türetir: "$\mathcal{S}$'nin ispatlayamayacağı hiçbir sınır yoktur." Denk olarak: "$\mathcal{S}$'nin türetilebilir her sentaktik değişmezi $\mathcal{S}$ tarafından tamamen betimlenebilir."

Bu doğrudan Lemma 2 ile çelişir. SIP'e göre $\mathcal{S}$ sistemi için (ilk cümleciklerden inşayla) en az bir $P_{\mathcal{S}}$ sentaktik değişmezi vardır. Bu değişmez donmuş terimler üretir (Tanım 4). Bu donmuş terimlerin varlığı Lemma 2 gereği anlamsal olarak doğrudur.

$\mathcal{S} \vdash \neg G_{\mathcal{S}}$ ise $\mathcal{S}$, Lemma 2'nin doğru olduğunu garanti ettiği bir anlamsal doğrunun varlığını inkâr eder. Bu SIP ile açık bir çelişkidir: SIP sentaktik değişmezlerin var olduğunu ve donmuş kaldığını teyit eder, $\neg G_{\mathcal{S}}$ bunu inkâr eder. $\mathcal{S}$ tutarlı varsayıldığından ikisini birden türetemez.

Sonuçlar: (1) *Tutarsızlık:* $\mathcal{S} \vdash \neg G_{\mathcal{S}}$ ise sistem tutarsızdır (üst-mantıksal bir olguyla çelişen bir önermeyi türetir); (2) *Kararsızlık:* tutarsız bir sistemin güvenlik garantisi yoktur, çünkü bir önermeyi de olumsuzunu da türetebilir.

> **Çelişki: $\neg G_{\mathcal{S}}$, SIP (Lemma 2) ile çelişir.**

**Durum 3: $\mathcal{S} \vdash G_{\mathcal{S}}$ de değil, $\mathcal{S} \vdash \neg G_{\mathcal{S}}$ de değil.** Bu tek tutarlı ihtimaldir. Bu karar verilemezliğin anlamı kesindir:
- $G_{\mathcal{S}}$ *anlamsal olarak doğrudur*: $\mathcal{S}$'nin her modelinde sentaktik değişmezler vardır ve donmuş kalırlar (Lemma 2 gereği);
- $\mathcal{S}$, doğruluğuna rağmen $G_{\mathcal{S}}$'yi türetmek için gereken *sentaktik kaynaklardan yoksundur*;
- $G_{\mathcal{S}}$ *keyfî değildir*: arızî bir boşluk değil, belirli bir içeriğe (öz sınırların varlığına) sahiptir. Sistemin henüz "bulamadığı" değil, yapısal olarak üretemediği bir önermedir. ∎

**Sonuç 1.**
$$\forall\,\mathcal{S} \text{ tutarlı ve yeterince anlatımlı},\;\exists\, G_{\mathcal{S}}:\; \mathcal{S} \not\vdash G_{\mathcal{S}} \;\land\; \mathcal{S} \not\vdash \neg G_{\mathcal{S}}.$$

[Çevirenin notu: Durum 1 ve 2'nin kuvveti SIP'in "anlamsal doğruluk" iddiasına ve "sistemin seviyesini aşması" gibi kesin tanımı verilmemiş ifadelere dayanır; bkz. KUNYE tenkidi.]

## 9. Genişletilemezlik ve sonsuz gerileme
**Teorem 3 (Problem genişletmeyle çözülemez).** $\mathcal{S}$, $G_{\mathcal{S}}$'yi türetemediğinden, $G_{\mathcal{S}}$'yi türetmek için yeni kurallar ekleyen tutarlı bir $\mathcal{S}' = (V', F', R \cup R_{\mathrm{new}}, I)$ genişlemesini düşünelim. O zaman $\mathcal{S}'$, $\mathcal{S}$ ile aynı yapıya sahiptir. $R_{\mathrm{new}}$ sonlu olduğundan hâlâ sonlu bir sentaktik sistemdir. Lemma 2'nin $R \cup R_{\mathrm{new}}$'ye doğal genişlemesiyle hâlâ sonlu bir sentaktik değişmezler kümesine sahiptir. Yeni kurallar yeni sol taraflar getirdiğinden ve $R \cup R_{\mathrm{new}}$'ye göre yeni Skolem sabitleri yeni ilk-sembol çatışmaları ürettiğinden, yalnız $R$'ye göre donmuş olmayan yeni $t'$ terimleri $R \cup R_{\mathrm{new}}$'ye göre donmuş hâle gelir. Bu yeni donmuş terimlerden, aynı inşayla yeni bir $\phi_{\mathcal{S}'}$ sınır önermesi ve yeni bir kendine-atıflı $G_{\mathcal{S}'}$ doğar.

**Lemma 4 (Eksikliğin sonlanmayan zinciri).** Bir sistemler dizisi tanımlayın: $\mathcal{S}_0 := \mathcal{S}$, $\mathcal{S}_{n+1} := \mathcal{S}_n$'nin $G_{\mathcal{S}_n}$'yi türetmeye çalışan tutarlı genişlemesi. O zaman: (1) her $n$ için $\mathcal{S}_n \not\vdash G_{\mathcal{S}_n}$ (Teorem 2 gereği); (2) $\mathcal{S}_{n+1} \vdash G_{\mathcal{S}_n}$ geçerli olabilir (bir genişlemedir); (3) ama $\mathcal{S}_{n+1}$'in türetemediği yeni bir $G_{\mathcal{S}_{n+1}}$ doğar.

Hiçbir sonlu sentaktik sistem kendi eksiklik sınırlarının tamamını çözemez. Eksiklik zinciri sonsuz ve kapatılamazdır: $\forall n,\;\exists m > n:\; \mathcal{S}_m \not\vdash G_{\mathcal{S}_m}$.

*[Kaynak satır 628'de ("Evrensellik" bölümünün başı) okuma bu kısımda sona erdi.]*
