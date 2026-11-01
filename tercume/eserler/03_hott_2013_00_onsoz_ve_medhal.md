# Tahavvül-i Muttasıl Tip Nazariyesi: Riyâziyâtın Vahdet Esasları

## Önsöz ve Medhal

**Vahdet Esasları Programı (The Univalent Foundations Program)**

*[İleri Tetkikler Enstitüsü (Institute for Advanced Study), Princeton, 2013.]*

---

> **Künye ve nüsha.** Aslın unvanı: *Homotopy Type Theory: Univalent Foundations of Mathematics.* İngilizce. Müellif: The Univalent Foundations Program, Institute for Advanced Study, Princeton, 2013. Bu tercümeye esas alınan asıl: kitabın LaTeX kaynağı, <https://github.com/HoTT/book>, dosyalar `preface.tex` ve `introduction.tex` (Teşrîn-i sânî 2026'da alınan nüsha).
>
> **Lisans.** Aslı *Creative Commons Atıf-Aynı Lisansla Paylaş 3.0 Umûmî* (Creative Commons Attribution-ShareAlike 3.0 Unported) lisansıyla neşredilmiştir: <http://creativecommons.org/licenses/by-sa/3.0/>. Bu tercüme de **aynı lisansla** neşredilir. Atıf: The Univalent Foundations Program, *Homotopy Type Theory: Univalent Foundations of Mathematics*, Institute for Advanced Study, 2013; Osmanlıca tercümesi, Mucit-AI tercüme heyeti, 2026. Tercümede aslın metni değiştirilmeden nakledilmiştir; değişiklik yalnız lisanın değişmesidir ve düsturların kelimeyle yazılmasıdır.
>
> Düsturlarda harf yazılmamıştır; aslın işaretlerinin hangi kelimelerle karşılandığı sondaki **İsimler cedveli**ndedir. Aslın kaynak gösterdiği eserlerin numaraları `[Russell 1908]` gibi müellif ve yıl ile yazılmıştır.

---

## Önsöz

### İleri Tetkikler Enstitüsünde Vahdet Esasları Hususî Senesi

Riyâziyâtın Vahdet Esaslarına dair bir Hususî Sene, 2012-13'te İleri Tetkikler Enstitüsünün Riyâziyât Mektebinde, Steve Awodey, Thierry Coquand ve Vladimir Voevodsky tarafından tertip edilerek yapıldı. Resmî iştirakçiler şu zevattı:

Peter Aczel, Benedikt Ahrens, Thorsten Altenkirch, Steve Awodey, Bruno Barras, Andrej Bauer, Yves Bertot, Marc Bezem, Thierry Coquand, Eric Finster, Daniel Grayson, Hugo Herbelin, André Joyal, Dan Licata, Peter Lumsdaine, Assia Mahboubi, Per Martin-Löf, Sergey Melikhov, Alvaro Pelayo, Andrew Polonsky, Michael Shulman, Matthieu Sozeau, Bas Spitters, Benno van den Berg, Vladimir Voevodsky, Michael Warren, Noam Zeilberger.

Bundan başka, iştirakleri hiç de daha az kıymetli olmayan şu talebeler de vardı:

Carlo Angiuli, Anthony Bordg, Guillaume Brunerie, Chris Kapulkin, Egbert Rijke, Kristina Sojakova.

Ayrıca, talebe ziyaretçiler de dahil olmak üzere, Hususî Seneye katkıları aynı derecede elzem olan şu kısa ve uzun müddetli ziyaretçiler vardı:

Jeremy Avigad, Cyril Cohen, Robert Constable, Pierre-Louis Curien, Peter Dybjer, Martín Escardó, Kuen-Bang Hou, Nicola Gambino, Richard Garner, Georges Gonthier, Thomas Hales, Robert Harper, Martin Hofmann, Pieter Hofstra, Joachim Kock, Nicolai Kraus, Nuo Li, Zhaohui Luo, Michael Nahas, Erik Palmgren, Emily Riehl, Dana Scott, Philip Scott, Sergei Soloviev.

### Bu kitap hakkında

Bir kitap yazmaya niyet etmemiştik. Elinizdeki eser, makine ile denetlenebilen sûrî bir ispatı tamamlamak üzere, bir insanın okuyup anlayabileceği yeni bir "gayr-ı sûrî tip nazariyesi" üslûbu geliştirmek için yaptığımız müşterek gayretlerden doğmuştur. Vahdet esasları, bir hâsib ispat muâvininde icra edilebilecek bir riyâziyât esası fikrine sıkı sıkıya bağlıdır. Böyle bir sûrîleştirme bu kitabın bir cüz'ü olmamakla beraber, burada arz edilen malzemenin çoğu filhakika evvelâ bir ispat muâvini içinde tamamen sûrîleştirilmiş bir zeminde yapılmış, ve ancak sonradan, önünüzde bulduğunuz takdime varmak için "gayr-ı sûrîleştirilmiştir" — bu, sûrîleştirilmiş riyâziyâttaki alışılmış hâlin şayan-ı dikkat bir tersine çevrilmesidir.

Yukarıda adları sayılan zevatın her biri Hususî Seneye — ve böylece bu kitaba — fikirler, sözler yahut fiiller sûretinde bir şey katmıştır. Sene boyunca hâkim olan müşterek çalışma ruhu hakikaten fevkalâdeydi.

Hususî bir teşekkür, İleri Tetkikler Enstitüsüne borçludur; o olmasaydı bu kitabın asla vücuda gelmeyeceği âşikârdır. Enstitü, riyâziyâtın bu yeni şubesinin yaratılması için ideal bir zemin olduğunu ispat etti: teşvik edici, samimî ve destekleyici. Bu müstesnâ havanın bir izi bu kitabın sahifelerinde ve bu yeni tetkik sahasının gelecekteki inkişâfında kalsın.

*Vahdet Esasları Programı*
*İleri Tetkikler Enstitüsü*
*Princeton, Nisan 2013*

---

## Medhal

*Tahavvül-i muttasıl tip nazariyesi*, birkaç ayrı sahanın cihetlerini şaşırtıcı bir tarzda birleştiren yeni bir riyâziyât şubesidir. Bu nazariye, *tahavvül-i muttasıl nazariyesi* ile *tip nazariyesi* arasında yakın zamanda keşfedilmiş bir irtibata dayanır. Tahavvül-i muttasıl nazariyesi cebrî hendese-i vaz'iyye ile tecânüs cebrinden neşet etmiştir ve yüksek makûleler nazariyesiyle münasebeti vardır; tip nazariyesi ise riyâzî mantığın ve nazarî hâsibât ilminin bir şubesidir. Bu ikisi arasındaki irtibatlar şu an yoğun bir tetkikin merkezinde olmakla beraber, bunların tam anlaşılması daha çok vakit ve daha çok zahmetli çalışma isteyecek bir mevzûun ancak başlangıcı olduğu gittikçe daha açık görünmektedir. Bu mevzû, kürelerin tahavvül-i muttasıl zümreleri, tip denetimi hârizmîleri ve zayıf nihâyetsiz zümremsilerin tarifi gibi birbirinden görünüşte pek uzak meselelere dokunur.

Tahavvül-i muttasıl tip nazariyesi, riyâziyâtın en temel esasına da yeni fikirler getirir. Bir taraftan Voevodsky'nin ince ve güzel *vahdet mütearifesi* vardır. Vahdet mütearifesi bilhassa şunu gerektirir ki, temâsül eden bünyeler aynı sayılabilir; riyâziyeciler bu prensibi, alışılmış esasların "resmî" akîdeleriyle telif edilemez olmasına rağmen, iş günlerinde memnuniyetle kullanagelmişlerdir. Diğer taraftan, tahavvül-i muttasıl nazariyesinin bazı temel fezâlarının ve inşalarının — küreler, üstüvâneler, kat'lar, mahallîleştirmeler ve saire — doğrudan, mantıkî tavsiflerini veren *yüksek istikrâî tipler* vardır. Bu iki fikrin ikisini de klasik mecmûalar nazariyesi esaslarında doğrudan yakalamak imkânsızdır; fakat tahavvül-i muttasıl tip nazariyesinde birleştirildiklerinde, büsbütün yeni bir cins "tahavvül-i muttasıl tiplerinin mantığı"na imkân verirler.

Bu, dahilî bir tahavvül-i muttasıl muhtevası olan, riyâziyâtın nesnelerine dair "lâyetegayyer" bir telakkî taşıyan — ve çalışan riyâziyeciye amelî bir yardımcı olabilecek elverişli makine tatbikatı bulunan — yeni bir riyâziyât esasları telakkîsine işaret eder. Bu, *Vahdet Esasları* programıdır. Elinizdeki kitap, vahdet esaslarının temellerinin ilk muntazam takdimi ve bu yeni muhakeme üslûbunun bir misaller mecmûası olmak üzere tasarlanmıştır — fakat okuyucunun herhangi bir sûrî mantığı bilmesini yahut öğrenmesini, ya da herhangi bir hâsib ispat muâvinini kullanmasını gerektirmeden.

Tekrar edelim ki tahavvül-i muttasıl tip nazariyesi genç bir sahadır ve vahdet esasları hâlâ inşa hâlinde olan bir iştir. Bu kitap, tamamlanmış bir binanın cilâlanmış bir takdimi olarak değil, sahanın yalnız bir kısmının, yazıldığı vakitte çekilmiş bir "enstantanesi" olarak telakkî edilmelidir. Aşağıda kısaca bahsedeceğimiz üzere, tahavvül-i muttasıl tip nazariyesinin henüz tam anlaşılmamış birçok cihetleri vardır — ve bazılarına burada hiç dokunulmamıştır bile. Nihaî nazariye hemen hemen kat'î olarak tam bu kitapta tarif edilen gibi görünmeyecektir; fakat elbette *en az* onun kadar kudretli ve kuvvetli olacaktır; binâenaleyh inanıyoruz ki vahdet esasları, riyâziyecilerin çoğunun yaptığı sûrîleştirilmemiş riyâziyâtın "zımnî esası" olarak, nihayet mecmûalar nazariyesine kābil-i amel bir bedel hâline gelecektir.

### Tip nazariyesi

Tip nazariyesi aslında Bertrand Russell tarafından [Russell 1908], o vakit tetkik altında bulunan riyâziyâtın mantıkî esaslarındaki mütenâkızları önlemek için bir vasıta olarak icat edildi. Sonraki birkaç on yıl içinde birçok kimse tarafından, bilhassa onu kendi *lambda hesabı* ile birleştiren Church tarafından [Church 1940; Church 1941] daha da inkişâf ettirildi. Klasik riyâziyâtın esası olarak umûmiyetle kabul edilmemekle beraber — mecmûalar nazariyesi daha mûtat olduğu için — tip nazariyesinin, bilhassa hâsibât ilminde ve programlama lisanları nazariyesinde sayısız tatbiki vardır [Pierce]. Per Martin-Löf [Martin-Löf 1972; 1973; 1979; 1984], başkalarıyla beraber, Church'ün tip nizâmının "tahmîlî" bir tadilini geliştirdi; buna bugün umûmiyetle bağımlı, inşâî, hadsî yahut sadece *Martin-Löf tip nazariyesi* denir. Burada ele aldığımız nizâmın esası budur; bu nizâm aslında inşâî riyâziyâtın sûrîleştirilmesi için sıkı bir çerçeve olarak tasarlanmıştı. Aşağıda "tip nazariyesi" sözünü çoğu zaman hususiyle bu nizâmı ve benzerlerini göstermek için kullanacağız; ancak bir mevzû olarak tip nazariyesi çok daha geniştir (tip nazariyesinin tarihi için bakınız [Kamareddine ve diğerleri; Sommaruga]).

Tip nazariyesinde, mecmûalar nazariyesinin aksine, nesneler, programlama lisanlarında kullanılan veri tiplerine benzer, asıl ve iptidâî bir *tip* mefhûmu ile sınıflandırılır. İncelikle tertip edilmiş bu tipler, sınıflandırılan nesnelerin tafsilâtlı tariflerini ifade etmek için kullanılabilir ve bu nesneler hakkında muhakeme prensiplerine yol açar. Pek basit bir misal alalım: birinci tip ile ikinci tipin hâsıl-ı zarb tipinin nesnelerinin "(birinci unsur, ikinci unsur)" şeklinde olduğu bilinir; binâenaleyh onların nasıl inşa edileceği ve nasıl ayrıştırılacağı kendiliğinden bilinir. Bunun gibi, birinci tipten ikinci tipe giden tâbi tipinin bir nesnesi, birinci tipin nesneleriyle mukayyed ikinci tipten bir nesneden elde edilebilir ve birinci tipten bir mütehavvil kıymetinde hesap edilebilir. Bütün nesnelerin bu katı tarzda önceden kestirilebilen davranışı (mecmûalar nazariyesinin, gayr-ı mütecânis mecmûalara izin veren daha serbest teşekkül prensiplerinin aksine), tip nazariyesinin hâsib programlarının sıhhatini tahkikte yaygın olarak kullanılmasına yol açan cihetlerinden biridir. Tiplerin inşasına bağlı açık muhakeme prensipleri, aynı zamanda riyâziyâtı sûrîleştirmek ve sûrîleştirilmiş ispatların sıhhatini tahkik etmek için kullanılan bugünkü *hâsib ispat muâvinleri*nin de esasını teşkil eder. Tip nazariyesinin bu cihetine aşağıda tekrar döneceğiz.

Bununla beraber tip nazariyesini riyâzî bir nokta-i nazardan anlamaktaki bir müşkül daima şu olmuştur ki, temel *tip* mefhûmu *mecmûa* mefhûmundan, tam olarak ifade edilmesi güç olan cihetlerle farklıdır. İnanıyoruz ki tipleri garip mecmûalar olarak (belki klasik mantık kullanılmadan inşa edilmiş mecmûalar olarak) değil, tahavvül-i muttasıl nazariyesinin nokta-i nazarından bakılan fezâlar olarak telakkî etmek yeni fikri, mühim bir ileri adımdır. Bilhassa bu fikir, bir tipin unsurlarının müsâvâtı mefhûmunun bir mecmûanın unsurlarınınkinden nasıl farklı olduğunu anlamak meselesini halleder.

Tahavvül-i muttasıl nazariyesinde fezâlarla ve onlar arasındaki muttasıl tatbiklerle, tahavvül-i muttasıla kadar, meşgul olunur. Birinci fezâdan ikinci fezâya giden bir **birinci tatbik** ile bir **ikinci tatbik** çifti arasında bir *tahavvül-i muttasıl*, birinci fezâ ile sıfırdan bire kadar olan vâhid aralığın hâsıl-ı zarbından ikinci fezâya giden, ve her nokta için "tahavvül(nokta, 0) = birinci tatbik(nokta)" ile "tahavvül(nokta, 1) = ikinci tatbik(nokta)" şartlarını sağlayan muttasıl bir **tahavvül** tatbikidir. Bu tahavvül, birinci tatbikin ikinci tatbike bir "muttasıl şekil değiştirmesi" olarak düşünülebilir. Birinci fezâ ile ikinci fezâya, aralarında gidip gelen muttasıl tatbikler bulunursa ve bunların terkipleri ayrı ayrı ayniyet tatbiklerine tahavvül-i muttasılca müsavi ise, yâni bu iki fezâ "tahavvül-i muttasıla kadar" temâsül ediyorlarsa, *tahavvül-i muttasılca mütekâfi* denir. Tahavvül-i muttasılca mütekâfi fezâların cebrî lâyetegayyerleri aynıdır (meselâ tecânüs, yahut asıl zümre) ve bunlara aynı *tahavvül-i muttasıl tipine* sahiptir denir.

### Tahavvül-i muttasıl tip nazariyesi

Tahavvül-i muttasıl tip nazariyesi, tip nazariyesini tahavvül-i muttasıl nokta-i nazarından tefsir eder. Tahavvül-i muttasıl tip nazariyesinde tipleri (tahavvül-i muttasıl nazariyesinde tetkik edildiği mânâda) "fezâlar" yahut yüksek zümremsiler olarak, mantıkî inşaları da (meselâ birinci tip ile ikinci tipin hâsıl-ı zarbını) bu fezâlar üzerinde tahavvül-i muttasılca lâyetegayyer inşalar olarak telakkî ederiz. Bu sûretle, fezâları, evvelâ noktalar mecmûası hendese-i vaz'iyyesini (yahut onun yerini tutan herhangi bir terkibî bedeli, meselâ basît mecmûalar nazariyesini) geliştirmek zorunda kalmadan doğrudan işleyebiliriz. Bu nokta-i nazarı kısaca izah etmek için, evvelâ tip nazariyesinin temel mefhûmunu, yâni **hadd**in bir **tip**ten olduğunu düşünelim; bu şöyle yazılır:

> hadd : tip.

Bu ifade an'anevî olarak şuna yakın bir şey diye düşünülür:

> "hadd, tip mecmûasının bir unsurudur".

Fakat tahavvül-i muttasıl tip nazariyesinde onu bunun yerine şöyle düşünürüz:

> "hadd, tip fezâsının bir noktasıdır".

Bunun gibi, tip nazariyesinde birinci tipten ikinci tipe giden her tâbi, birinci fezâdan ikinci fezâya giden muttasıl bir tatbik olarak telakkî edilir.

Şunu tebarüz ettirmeliyiz ki bu "fezâlar" vaz'î olarak değil, sırf tahavvül-i muttasıl cihetinden ele alınır. Meselâ bir tipin "açık cüz'î mecmûası" yahut bir tipin unsurlarından bir tevâlînin "tekārübü" mefhûmu yoktur. Yalnız noktalar arasındaki tarîkler ve tarîkler arasındaki tahavvül-i muttasıllar gibi, tahavvül-i muttasıl nazariyesinin başka nümûnelerinde de (meselâ basît mecmûalarda) mânâsı olan "tahavvül-i muttasılî" mefhûmlarımız vardır. Binâenaleyh tipleri *nihâyetsiz zümremsiler* olarak ele aldığımızı söylemek daha doğru olurdu; bu, tahavvül-i muttasıl nazariyesinin, vaz'î fezâlarla, basît mecmûalarla yahut tahavvül-i muttasıl nazariyesinin başka herhangi bir nümûnesiyle takdim edilebilen "lâyetegayyer nesneleri"nin adıdır. Bununla beraber, diğer vaz'î mefhûmların tatbik edilemeyeceğini hatırladığımız müddetçe, bazan "fezâ" ve "tarîk" gibi vaz'î kelimeleri kullanmak elverişlidir.

(Bu nesneler için *tahavvül-i muttasıl tipi* tabirini kullanmak da cazip gelir; bu tabir, "tahavvül-i muttasılî olarak bakılan bir tip (tip nazariyesindeki mânâda)" ile "tahavvül-i muttasıl nazariyesinin nokta-i nazarından mülâhaza edilen bir fezâ" şeklindeki çift tefsiri ima eder. Sonraki mânâ, "tahavvül-i muttasıl tipi"nin, tahavvül-i muttasılca tekâfü'e göre fezâların bir *tekâfü' sınıfı* olarak klasik mânâsından biraz farklıdır; ancak "bu iki fezânın tahavvül-i muttasıl tipi aynıdır" gibi ibarelerin mânâsını muhafaza eder.)

Tipleri mecmûalar olarak değil de bünyeli nesneler olarak tefsir etmek fikrinin uzun bir mazisi vardır ve tip nazariyesinin muhtelif muammalı cihetlerini aydınlattığı bilinir. Meselâ tipleri desteler olarak tefsir etmek, tip nazariyesi mantığının hadsî tabiatını izah etmeye yardım eder; onları kısmî tekâfü' münasebetleri yahut "sahalar" olarak tefsir etmek ise onun hesabî cihetlerini izah etmeye yardım eder. Bu tefsir aynı zamanda bünyeli nesneleri tetkik etmek için tip nazariyesi muhakemesini kullanabileceğimiz mânâsına gelir ve makûlî mantığın zengin sahasına yol açar. Tahavvül-i muttasılî tefsir de bu aynı kalıba uyar: tip nazariyesinde *ayniyet*in (yahut müsâvâtın) tabiatını aydınlatır ve tahavvül-i muttasıl nazariyesinin tetkikinde tip nazariyesi muhakemesini kullanmamıza izin verir.

Tahavvül-i muttasıl tefsirinin anahtar yeni fikri şudur: aynı tipten iki nesne arasındaki mantıkî ayniyet mefhûmu ("birinci nesne = ikinci nesne"), tip fezâsında birinci noktadan ikinci noktaya bir **tarîk**in vücudu olarak anlaşılabilir. Bu aynı zamanda şu demektir: birinci tipten ikinci tipe giden iki tâbi, tahavvül-i muttasılca mütekâfi iseler aynı sayılabilir; zîrâ bir tahavvül-i muttasıl, birinci tipin her noktası için bir tane olmak üzere, ikinci tip içinde birinci tâbinin o noktadaki kıymetinden ikinci tâbinin o noktadaki kıymetine giden tarîklerin (muttasıl) bir ailesinden ibarettir. Tip nazariyesinde her tip için, o tipin iki nesnesinin aynîleştirmelerinin (eskiden biraz muammalı olan) bir **ayniyet tipi** vardır; tahavvül-i muttasıl tip nazariyesinde bu, vâhid aralıktan o tipe giden bütün muttasıl tatbiklerin *tarîk fezâsı*ndan başka bir şey değildir. Bu sûretle, birinci noktanın ikinci noktaya ayniyet tipinden bir **tarîk** haddi, tip fezâsında birinci noktadan ikinci noktaya bir tarîki temsil eder.

Tahavvül-i muttasıl tip nazariyesi fikri 2006 civarında Awodey ile Warren'ın [Awodey ve Warren] ve Voevodsky'nin [Voevodsky] birbirinden müstakil çalışmalarında doğdu; fakat Hofmann ile Streicher'ın daha evvelki zümremsi tefsirinden [Hofmann ve Streicher] ilham almıştı. Filhakika yüksek buudlu makûleler nazariyesinin (bilhassa zayıf nihâyetsiz zümremsiler nazariyesinin), Grothendieck'in teklif ettiği gibi, tahavvül-i muttasıl nazariyesiyle sıkı sıkıya bağlı olduğu bugün bilinmektedir ve bu, her iki sınıftan riyâziyeciler tarafından yoğun bir şekilde tetkik edilmektedir. Awodey–Warren ve Voevodsky'nin asıl mânâ nümûneleri, tahavvül-i muttasıl nazariyesinden iyi bilinen ve bugün yüksek makûleler nazariyesinde de kullanılan mefhûmları ve usulleri kullanır; meselâ Quillen nümûne makûleleri ve Kan basît mecmûaları.

Bilhassa Voevodsky, tip nazariyesinin Kan basît mecmûalarında bir tefsirini inşa etti ve bu tefsirin, *vahdet* adını verdiği, daha ileri ve hayatî bir hassayı sağladığını fark etti. Bu hassa tip nazariyesinde daha evvel hiç mülâhaza edilmemişti (ancak Church'ün kaziyyeler için genişlik prensibinin bunun pek hususî bir hâli olduğu anlaşılmıştır; Hofmann ile Streicher da "kâinat genişliği" adı altında başka bir hususî hâlini mülâhaza etmişlerdi). Vahdeti tip nazariyesine yeni bir mütearife sûretinde eklemenin, çoğu tabiî, sadeleştirici ve ikna edici olan geniş tesirli neticeleri vardır. Vahdet mütearifesi, tip nazariyesinin tahavvül-i muttasılî görüşünü daha da kuvvetlendirir; zîrâ basît nümûnede ve ona yakın diğer nümûnelerde doğrudur, tiplerin mecmûalar olarak görülmesinde ise sakıt olur.

### Vahdet esasları

Pek kısaca, vahdet mütearifesinin temel fikri şöyle izah edilebilir. Tip nazariyesinde unsurları bizzat tipler olan bir tipe sahip olunabilir; böyle bir tipe *kâinat* denir. Kâinatın hadleri olan tiplere umûmiyetle *küçük* tipler denir. Her tip gibi kâinatın da, küçük tipler arasındaki "birinci tip = ikinci tip" ayniyet münasebetini ifade eden bir ayniyet tipi vardır. Tipleri fezâlar olarak düşünürsek, kâinat, noktaları fezâlar olan bir fezâdır; onun ayniyet tipini anlamak için şunu sormalıyız: kâinat içindeki fezâlar arasında birinci fezâdan ikinci fezâya bir tarîk nedir? Vahdet mütearifesi der ki, böyle tarîkler (kabaca) yukarıda izah edildiği gibi tahavvül-i muttasıl tekâfü'lerine tekabül eder. Biraz daha dakik olarak: herhangi iki (küçük) birinci tip ile ikinci tip verilince, birinci tipin ikinci tiple aynîleştirmelerinin iptidâî "birinci tip = ikinci tip" tipine ilâveten, birinci tipten ikinci tipe tekâfü'lerin tarif edilmiş "birinci tip ≃ ikinci tip" tipi vardır. Herhangi bir nesne üzerindeki ayniyet tatbiki bir tekâfü' olduğu için, kanonik bir tatbik vardır:

> (birinci tip = ikinci tip) → (birinci tip ≃ ikinci tip).

Vahdet mütearifesi, bu tatbikin kendisinin bir tekâfü' olduğunu beyan eder. Fazla sadeleştirme tehlikesini göze alarak bunu kısaca şöyle ifade edebiliriz:

> **Vahdet Mütearifesi:** (birinci tip = ikinci tip) ≃ (birinci tip ≃ ikinci tip).

Başka bir tabirle, ayniyet tekâfü'e mütekâfidir. Bilhassa "mütekâfi tipler aynıdır" denebilir. Bununla beraber bu ibare biraz yanıltıcıdır; zîrâ tekâfü' mefhûmunu ayniyetle örtüşmek üzere *çökerten* bir çeşit "iskeletlik" şartı gibi gelebilir; halbuki hakikatte vahdet, ayniyet mefhûmunu (değişmeyen) tekâfü' mefhûmuyla örtüşmek üzere *genişletmek* hakkındadır.

Tahavvül-i muttasıl nokta-i nazarından vahdet şunu gerektirir: aynı tahavvül-i muttasıl tipindeki fezâlar kâinat içinde bir tarîkle birbirine bağlıdır; bu, (küçük) fezâlar için bir sınıflandırıcı fezâ sezişine uygundur. Mantıkî nokta-i nazardan ise bu, köklü olarak yeni bir fikirdir: temâsül eden şeylerin aynı sayılabileceğini söyler! Riyâziyeciler elbette temâsül eden bünyeleri amelde aynı saymaya alışkındır; fakat bunu umûmiyetle, işin içindeki nesnelerin "hakikaten" aynı olmadığını bilerek, "işaretin sû-i istimâli" ile, yahut başka bir gayr-ı sûrî vasıta ile yaparlar. Fakat bu yeni esas tertibinde böyle bünyeler sûrî olarak aynî kılınabilir; mantıkî mânâda ki, birini içine alan her hassa yahut inşa ötekine de tatbik olunur. Filhakika aynîleştirme artık açıkça yapılır ve hassalar ile inşalar onun boyunca muntazaman nakledilebilir. Bundan başka, böyle aynîleştirmelerin yapılabildiği muhtelif tarzlar da bizzat bir bünye teşkil eder ki onu hesaba katmak mümkündür (ve katmak lâzımdır!).

Böylece hulâsaten, kâinatın birinci tip ve ikinci tip noktaları (yâni küçük tipler) için, vahdet mütearifesi şu üç mefhûmu aynîleştirir:

- (mantıkî) birinci tipin ve ikinci tipin bir aynîleştirmesi: tarîk : birinci tip = ikinci tip;
- (vaz'î) kâinatta birinci tipten ikinci tipe bir tarîk;
- (tahavvül-i muttasılî) birinci tip ile ikinci tip arasında bir tekâfü': tarîk : birinci tip ≃ ikinci tip.

### Yüksek istikrâî tipler

Tip nazariyesinin klasik üstünlüklerinden biri, istikrâ ile tarif edilmiş bünyelerle çalışmak için basit ve tesirli usulleridir. İstikrâ ile tarif edilmiş en basit âdi olmayan bünye tabiî adetlerdir; bunlar sıfırdan ve ardıl tâbisinden istikrâ ile meydana gelir. Bu beyandan, tabiî adetleri tavsif eden riyâzî istikrâ prensibi hârizmî bir tarzda çıkarılabilir. Daha umûmî istikrâî tarifler, her biri tekabül eden bir "istikrâ prensibi" ile tavsif edilen listeleri ve her nevi iyi temellenmiş ağaçları ihtiva eder. Bu, bazı programlama lisanlarında kullanılan veri bünyelerinin çoğunu kapsar; tip nazariyesinin sonrakiler hakkında sûrî muhakemede faydası da buradandır. Pek umûmî bir mânâda telakkî edilirse, istikrâî tarifler, birinci tipten ve ikinci tipten birinci tip ile ikinci tipin munfasıl ictimâına giden iki idhâl tatbiki tarafından "istikrâ ile" meydana getirilmiş sayılabilecek munfasıl ictimâ gibi misalleri de ihtiva eder. Bu hâlde "istikrâ prensibi", munfasıl ictimâı tavsif eden "hâllere ayırarak ispat"tır.

Tahavvül-i muttasıl nazariyesinde, yalnız bir *noktalar* topluluğuyla değil, *tarîklerin* ve yüksek tarîklerin topluluklarıyla da meydana getirilen "istikrâ ile tarif edilmiş fezâları" mülâhaza etmek tabiîdir. Klasik olarak böyle fezâlara *CW mürekkebleri* denir. Meselâ dâire, tek bir nokta ile o noktadan kendisine giden tek bir tarîk tarafından meydana getirilir. Bunun gibi iki buudlu küre, tek bir **merkez noktası** ile o noktadaki sâbit tarîkten kendisine giden tek bir iki buudlu tarîk tarafından meydana getirilir; simit sathı ise tek bir nokta, o noktadan kendisine giden **birinci tarîk** ile **ikinci tarîk** diye iki tarîk ve "birinci tarîk ∙ ikinci tarîk"ten "ikinci tarîk ∙ birinci tarîk"e giden iki buudlu bir tarîk tarafından meydana getirilir.

Tahavvül-i muttasıl tip nazariyesinde tarîklerin ayniyetlerle aynîleştirilmesini kullanarak, bu çeşit "istikrâ ile tarif edilmiş fezâlar", tip nazariyesinde, tabiî adetler ve munfasıl ictimâ gibi klasik misallere tamamen benzer şekilde "istikrâ prensipleri" ile tavsif edilebilir. Bundan doğan *yüksek istikrâî tipler*, küreler gibi tanıdık fezâlar hakkında muhakeme etmenin doğrudan, "mantıkî" bir yolunu verir; bunlar (vahdet ile beraber) tahavvül-i muttasıl nazariyesinin tanıdık delillerini, meselâ kürelerin tahavvül-i muttasıl zümrelerinin hesabını, sırf sûrî bir tarzda icra etmek için kullanılabilir. Bundan doğan ispatlar, klasik tahavvül-i muttasıl nazariyesi fikirleriyle klasik tip nazariyesi fikirlerinin bir izdivacıdır ve her iki ilme yeni bir basîret kazandırır.

Bundan başka, bu buz dağının ancak görünen ucudur: tahavvül-i muttasıl nazariyesinin birçok mücerred inşası, meselâ tahavvül-i muttasıl mukābil-nihâyetleri, ta'lîkler, Postnikov kuleleri, mahallîleştirme, tetmîm ve tayflaştırma, yüksek istikrâî tipler olarak da ifade edilebilir. Bunların çoğu klasik olarak Quillen'in "küçük nesne delili" kullanılarak inşa edilir; bu delil, bir fezânın nihâyetsiz bir CW mürekkebi takdimini hârizmî olarak tavsif etmenin mütenâhî bir yolu sayılabilir; tıpkı "sıfır ve ardıl"ın tabiî adetlerin nihâyetsiz mecmûasının mütenâhî bir hârizmî tavsifi olması gibi. Küçük nesne delili ile hâsıl edilen fezâlar meşhur derecede girift ve anlaşılması güçtür; tip nazariyesi yaklaşımı ise, münasip "istikrâ prensibi"ne doğrudan erişim vererek herhangi bir açık inşa ihtiyacını atlattığı için, muhtemelen çok daha basittir. Böylece vahdet ile yüksek istikrâî tiplerin birleşmesi, tahavvül-i muttasıl nazariyesinin amelinde bir nevi inkılâp imkânına işaret eder.

### Vahdet esaslarında mecmûalar

Vahdet esaslarının nihayet riyâziyâtın "tamamına" esas olabileceğini iddia ettik; fakat şimdiye kadar yalnız tahavvül-i muttasıl nazariyesinden bahsettik. Elbette riyâziyâtı sûrîleştirmek için tip nazariyesinin, yeni tahavvül-i muttasıl tip nazariyesi hususiyetleri olmaksızın kullanıldığı birçok muayyen misal vardır; meselâ Feit–Thompson tek mertebe kaziyyesinin yakın zamanda Coq'ta sûrîleştirilmesi [Gonthier ve diğerleri].

Fakat an'anevî görüş, riyâziyâtın mecmûalar nazariyesi üzerine kurulduğudur; şu mânâda ki bütün riyâzî nesneler ve inşalar, Zermelo–Fraenkel mecmûalar nazariyesi gibi bir nazariyeye kodlanabilir. Bununla beraber artık iyice yerleşmiştir ki, hakikî mecmûalar nazariyesinin dışındaki riyâziyâtın çoğu için, Zermelo–Fraenkel nazariyesindeki mecmûaların girift, tabakalı mensubiyet bünyesi hakikaten lüzumsuzdur: Lawvere'in Mecmûalar Makûlesinin Unsurî Nazariyesi [Lawvere] gibi daha "bünyevî" bir nazariye kâfidir.

Vahdet esaslarında temel nesneler mecmûalar değil "tahavvül-i muttasıl tipleri"dir; fakat mecmûalar gibi davranan bir tipler sınıfını *tarif edebiliriz*. Tahavvül-i muttasılî olarak bunlar, her muttasıl bileşeni nokta gibi büzülebilen fezâlar, yâni munfasıl bir fezâya tahavvül-i muttasılca mütekâfi olanlar olarak düşünülebilir. Böyle "mecmûalar"ın makûlesinin Lawvere'in mütearifelerini (yahut nazariyenin tafsilâtına göre onlara yakın mütearifeleri) sağladığı bir kaziyyedir. Böylece Mecmûalar Makûlesinin Unsurî Nazariyesine benzer bir nazariyede temsil edilebilen her çeşit riyâziyât (ki tecrübenin gösterdiğine göre esas itibarıyla riyâziyâtın tamamıdır) vahdet esaslarında da aynı derecede iyi temsil edilebilir.

Bu, vahdet esaslarının riyâziyâtın mevcut esasları kadar iyi olduğu iddiasını destekler. Vahdet esaslarında çalışan bir riyâziyeci, mecmûalardan tanıdık bir tarzda bünyeler inşa edebilir; daha umûmî tahavvül-i muttasıl tipleri ise ihtiyaç duyulana kadar esasın arka planında bekler. Bu sebepten bu kitaptaki tatbikatın çoğu, vahdet esaslarının mevcut esas nizâmlarından onu ayıran *yeni* bir şey katabildiği sahalar olarak seçilmiştir.

Şaşırtıcı olmayarak tahavvül-i muttasıl nazariyesi ve makûleler nazariyesi bunlardan ikisidir; fakat belki daha az âşikâr olanı, vahdet esaslarının mecmûalar nazariyesi ve hakîkî tahlîl gibi mevzûlarda bile yeni ve alâka çekici bir şey arz etmesidir. Meselâ vahdet mütearifesi temâsül eden bünyeleri aynîleştirmemize, yüksek istikrâî tipler ise nesnelerin umûmî hassalarıyla doğrudan tavsifine imkân verir. Böylece umûmiyetle keyfî seçilmiş temsilcilere yahut mütenâhîyi aşan tekrarlı inşalara başvurmaktan kaçınabiliriz. Filhakika Zermelo–Fraenkel mecmûalar nazariyesinin tetkik nesneleri bile, vahdet esaslarının mecmûaları içinde böyle istikrâî bir umûmî hassa ile tavsif edilebilir.

### Gayr-ı sûrî tip nazariyesi

Klasik riyâziyecinin tip nazariyesini öğrenmeye kalkıştığında sık karşılaştığı bir müşkül, onun umûmiyetle tamamen yahut kısmen sûrîleştirilmiş bir istidlâl nizâmı olarak takdim edilmesidir. İspat nazariyesi tetkikleri için pek faydalı olan bu üslûp, tatbikî, gayr-ı sûrî muhakemede kullanmak için pek elverişli değildir. Çalışan riyâziyecilerin çoğuna, hattâ riyâziyâtın esaslarıyla alâkadar olabilecek olanlara bile tanıdık değildir. Elinizdeki eserin gayelerinden biri, vahdet esaslarında riyâziyât yapmanın, hem sıkı ve dakik olan hem de gündelik riyâziyâtın lisanına ve takdim üslûbuna daha yakın olan gayr-ı sûrî bir üslûbunu geliştirmektir.

Bugünkü riyâziyâtta riyâzî nesneler umûmiyetle, prensip itibarıyla — farz olunduğuna göre — Zermelo–Fraenkel ve ihtiyar mütearifesi gibi unsurî bir mecmûalar nazariyesi nizâmında sûrîleştirilebilecek bir tarzda inşa edilir ve onlar hakkında öyle muhakeme edilir — hiç değilse yeteri kadar ustalık ve sabır verilirse. Çoğu kere bu imkânın farkında olmaya bile lüzum yoktur; zîrâ o, büyük ölçüde bir ispatın "tamamen sıkı" olması şartıyla örtüşür (bütün riyâziyecilerin tahsil ve tecrübe ile sezgiyle anlamaya vardığı mânâda). Fakat "gayr-ı sûrî mecmûalar nazariyesi"nin birkaç cihetine dikkat etmeyi öğrenmek lâzımdır: mecmûa olamayacak kadar büyük yahut şekilsiz toplulukların kullanılması; ihtiyar mütearifesi ve ona mütekâfi olanlar; hattâ (lisans talebeleri için) hulf ile ispat usulü; ve saire. Tahavvül-i muttasıl tip nazariyesi gibi yeni bir esas nizâmını gayr-ı sûrî muhakemenin *zımnî sûrî esası* olarak benimsemek, insanın bazı sezgilerini ve âdetlerini ayarlamasını gerektirecektir. Elinizdeki metin bu "yeni nevi riyâziyât"ın bir misali olmak üzere tasarlanmıştır; bu riyâziyât hâlâ gayr-ı sûrîdir, fakat yine yeteri kadar ustalık ve sabır verilirse, artık prensip itibarıyla Zermelo–Fraenkel ve ihtiyar mütearifesi yerine tahavvül-i muttasıl tip nazariyesinde sûrîleştirilebilir.

Şunu tebarüz ettirmeye değer ki bu yeni nizâmda böyle bir sûrîleştirmenin hakikî amelî faydaları olabilir. Tip nazariyesinin sûrî nizâmı hâsib nizâmlarına elverişlidir ve mevcut ispat muâvinlerinde icra edilmiştir. Bir ispat muâvini, yalnız muteber muhakeme adımlarına izin vererek, kullanıcıya tamamen sûrî bir ispatın inşasında rehberlik eden bir hâsib programıdır. Bir derece otomatiklik de sağlar, mevcut kaziyyeler için kütüphaneleri tarayabilir ve hattâ hâsıl olan (inşâî) ispatlardan adedî hârizmîler çıkarabilir.

İnanıyoruz ki vahdet esasları programının bu ciheti onu esaslara dair diğer yaklaşımlardan ayırır ve çalışan riyâziyeciye muhtemelen yeni bir amelî fayda sağlar. Filhakika daha eski tip nazariyelerine dayanan ispat muâvinleri, dört renk kaziyyesi ve Feit–Thompson kaziyyesi gibi ehemmiyetli riyâzî ispatları sûrîleştirmek için zaten kullanılmıştır. Vahdet esaslarının hâsib tatbikleri şu an (nazariyenin kendisi gibi) inşa hâlindedir. Bununla beraber, şu an mevcut tatbikleri bile (ki çoğu Coq ve Agda gibi mevcut ispat muâvinlerinde yapılmış küçük tadillerdir) yalnız bilinen ispatların sûrîleştirilmesinde değil, yenilerinin keşfinde de kıymetlerini göstermişlerdir. Filhakika bu kitapta tarif edilen ispatların çoğu aslında *evvelâ* bir ispat muâvininde tamamen sûrîleştirilmiş bir şekilde yapılmış, ve ancak şimdi ilk defa "gayr-ı sûrîleştirilmektedir" — sûrî ve gayr-ı sûrî riyâziyât arasındaki alışılmış münasebetin bir tersine dönmesi.

Riyâziyecilerin kendi makalelerinin sıhhatini, bir ispat muâvininde sûrîleştirilmiş vahdet esasları nizâmı içinde çalışarak tahkik edebilecekleri, ve bunu yapmanın kendi makalelerini TeX ile dizmek kadar tabiî hâle geleceği, pek uzak olmayan bir gelecek tasavvur edilebilir. Prensip itibarıyla bu, başka herhangi bir esas nizâmı için de aynı derecede doğru olabilirdi; fakat elinizdeki eserin ve onun sûrî karşılığının şahitlik ettiği gibi, bunun vahdet esaslarıyla amelen daha erişilebilir olduğuna inanıyoruz.

### İnşâîlik

Klasik esaslar ile tip nazariyesi arasındaki en çarpıcı farklardan biri, riyâzî beyanların, hattâ onların ispatlarının birinci sınıf riyâzî nesneler hâline geldiği *ispatın ehemmiyeti* fikridir. Tip nazariyesinde riyâzî beyanları, aynı zamanda hem riyâzî inşalar hem riyâzî iddialar olarak telakkî edilebilen tiplerle temsil ederiz; bu telakkî *tip olarak kaziyyeler* diye de bilinir. Buna göre bir "hadd : tip" ifadesini hem tipin bir unsuru (yahut tahavvül-i muttasıl tip nazariyesinde tip fezâsının bir noktası), hem de aynı zamanda tip kaziyyesinin bir ispatı olarak telakkî edebiliriz. Bir misal alalım: birinci tip ile ikinci tip diye mecmûalarımız (munfasıl fezâlarımız) olduğunu farz edelim ve "birinci tip ikinci tiple temâsül eder" beyanını düşünelim. Tip nazariyesinde bu şöyle ifade edilebilir:

> Temâsül(birinci tip, ikinci tip) :≡ Σ (gidiş : birinci tip → ikinci tip) Σ (dönüş : ikinci tip → birinci tip) ( (Π (birinci unsur : birinci tip) dönüş(gidiş(birinci unsur)) = birinci unsur) × (Π (ikinci unsur : ikinci tip) gidiş(dönüş(ikinci unsur)) = ikinci unsur) ).

Buradaki Σ, Π ve × tip kurucularını sırasıyla "vardır ki", "her biri için" ve "ve" diye okumak, "birinci tip ile ikinci tip temâsül eder"in mûtat ifadesini verir; diğer taraftan onları mecmû'lar ve hâsıl-ı zarblar olarak okumak, birinci tip ile ikinci tip arasındaki *bütün temâsüllerin tipini* verir! Birinci tip ile ikinci tipin temâsül ettiğini ispat etmek için "ispat : Temâsül(birinci tip, ikinci tip)" diye bir ispat inşa edilir; bu da birinci tip ile ikinci tip arasında bir temâsül inşa etmekle, yâni gidiş ve dönüş tâbilerinden bir çifti, terkiplerinin ayrı ayrı ayniyet tatbikleri olduğunun *ispatları* ile beraber göstermekle aynıdır. Sonraki ispatlar da kendi sıralarında münasip nevilerden tahavvül-i muttasıllardan başka bir şey değildir. Bu sûretle, *bir kaziyyeyi ispat etmek, muayyen bir tipin bir unsurunu inşa etmekle aynı şeydir.* Bilhassa "birinci tip ve ikinci tip" şeklinde bir beyanı ispat etmek, birinci tipi ispat etmek ve ikinci tipi ispat etmek, yâni birinci tip ile ikinci tipin hâsıl-ı zarb tipinin bir unsurunu vermektir. Ve birinci tipin ikinci tipi gerektirdiğini ispat etmek, birinci tipten ikinci tipe giden tâbi tipinin bir unsurunu, yâni birinci tipten ikinci tipe bir tâbi (birinci tipin ispatlarının ikinci tipin ispatlarına bir tatbikini tayin eden) bulmaktır.

Tip olarak kaziyyeler mantığı esnektir ve birçok çeşitlemeyi destekler; meselâ kaziyyeleri temsil etmek için tiplerin yalnız bir alt sınıfını kullanmak gibi. Tahavvül-i muttasıl tip nazariyesinde, bütün tipler nizâmının, tıpkı klasik tahavvül-i muttasıl nazariyesindeki fezâlar gibi, yüksek tahavvül-i muttasıl bünyelerinin mevcut olduğu yahut çöktüğü buudlara göre "tabakalara ayrılmış" olmasından doğan böyle tabiî alt sınıflar vardır. Bilhassa Voevodsky, *buud-sayısı tahavvül-i muttasıl tiplerinin*, yâni o buudun üstünde âdi olmayan hiçbir tahavvül-i muttasıl malûmatı bulunmayan fezâlara tekabül eden tiplerin sırf tip nazariyesine ait bir tarifini bulmuştur. (Sıfır-tipler, yukarıda Lawvere'in mütearifelerini sağladığı söylenen "mecmûalar"dır.) Bundan başka, yüksek istikrâî tiplerle bir tipi umûmî olarak buud-sayısı tipine "kat'" edebiliriz; klasik tahavvül-i muttasıl nazariyesinde bu, onun buud-sayısıncı Postnikov kesiti olurdu. Mantık için bilhassa ehemmiyetli olan, *mahz kaziyyeler* dediğimiz eksi bir tahavvül-i muttasıl tipleri hâlidir. Klasik olarak her eksi bir tipi ya boştur ya büzülebilir; bu ihtimalleri sırasıyla "yanlış" ve "doğru" hakikat kıymetleri olarak tefsir ederiz.

Bütün tipleri kaziyye olarak kullanmak, mantığın pek "inşâî" bir telakkîsini verir; bu hususta daha fazlası için bakınız [Kolmogorov; Troelstra ve van Dalen]. Meselâ bir şeyin var olduğuna dair her ispat, böyle bir nesneyi fiilen bulmaya yetecek malûmatı beraberinde taşır; ve "birinci tip yahut ikinci tip"in doğru olduğuna dair her ispat, ya birinci tipin doğru olduğunun bir ispatıdır ya da ikinci tipin doğru olduğunun bir ispatıdır. Böylece her ispattan kendiliğinden bir hârizmî çıkarabiliriz; bu, hâsib programlamaya tatbikatta pek faydalı olabilir.

Diğer taraftan ise bu mantık, riyâziyâttaki vücut ispatlarının an'anevî anlayışından ayrılır. Bilhassa ihtiyar mütearifesi ve imtinâ'-ı vasat kanunu gibi bazı mühim klasik muhakeme prensiplerini sadakatle temsil etmez. Bunlar için, yalnız eksi bir tahavvül-i muttasıl tiplerinin kaziyyeleri temsil ettiği "eksi bir kat'lı" mantığı kullanmamız lâzımdır.

Daha muayyen olarak, bir taraftan *ihtiyar mütearifesini* düşünelim: "eğer birinci tipin her birinci unsuru için ikinci tipin, münasebet(birinci unsur, ikinci unsur) olacak şekilde bir ikinci unsuru varsa, birinci tipin her birinci unsuru için münasebet(birinci unsur, seçici(birinci unsur)) olacak şekilde birinci tipten ikinci tipe bir seçici tâbi vardır." Sırf tip olarak kaziyyeler mefhûmundaki "vardır", bu beyanı sadece ispat edilebilir kılacak kadar kuvvetlidir — fakat mûtat ihtiyar mütearifesinin bütün neticelerine sahip değildir. Bununla beraber eksi bir kat'lı mantıkta bu beyan kendiliğinden doğru değildir; klasik mecmûalar nazariyesindeki karşılığıyla aynı çeşit neticelere sahip kuvvetli bir farzdır.

Diğer taraftan *imtinâ'-ı vasat kanununu* düşünelim: "her tip için, ya o tip ya da o tipin nakîzi." Bunu sırf tip olarak kaziyyeler mantığında tefsir etmek, vahdet mütearifesiyle mütenâkız olan bir beyan verir. Zîrâ "tip"i ispat etmek onun bir unsurunu göstermek demek olduğundan, bu farz, boş olmayan her tipten bir unsur seçmenin yeknesak bir yolunu verirdi — bir çeşit Hilbert seçme âmili. Vahdet, böyle bir seçme âmilinin tipten seçtiği unsurun tipin bütün zâtî tekâfü'leri altında değişmez olması gerektiğini gerektirir; zîrâ bunlar zâtî ayniyetlerle aynîleştirilir ve her ameliye ayniyete riayet etmelidir; fakat bazı tiplerin sâbit noktası olmayan zâtî temâsülleri olduğu açıktır; meselâ iki unsurlu bir tipin unsurlarını yer değiştirebiliriz. Bununla beraber "eksi bir kat'lı imtinâ'-ı vasat kanunu", kendiliğinden doğru olmamakla beraber, klasik riyâziyâttakilerin çoğu aynı neticelerle tenâkuzsuz olarak farz edilebilir.

Başka bir tabirle, sırf tip olarak kaziyyeler mantığı yukarıda bahsedilen kuvvetli hârizmî mânâda "inşâî" iken, varsayılan eksi bir kat'lı mantık başka bir mânâda "inşâî"dir (yâni Heyting'in "hadsî" adı altında sûrîleştirdiği mantığın mânâsında); ve sonrakine, "klasik" denebilecek bir mantık elde etmek için ihtiyar ve imtinâ'-ı vasat mütearifelerini serbestçe ekleyebiliriz. Böylece tahavvül-i muttasıl tip nazariyesi hem inşâî hem klasik mantık telakkîleriyle, ve daha birçoklarıyla telif edilebilir. Filhakika tahavvül-i muttasıl nokta-i nazarı, klasik ve inşâî mantığın, muhtelif nizâmlardan bir tayfın iki ucu olarak, aralarında nihâyetsiz adette ihtimalle (eksi birden büyük ve nihâyetsizden küçük buud-sayıları için tahavvül-i muttasıl tipleri) yan yana var olabileceğini gösterir. "Buud-sayısı kat'lı imtinâ'-ı vasat kanunu"ndan ve "buud-sayısı kat'lı ihtiyar mütearifesi"nden bahsedebiliriz; nihâyetsiz kat'lı ihtiyar mütearifesi ispat edilebilir, nihâyetsiz kat'lı imtinâ'-ı vasat kanunu vahdetle mütenâkızdır; eksi bir kat'lı ihtiyar ve eksi bir kat'lı imtinâ'-ı vasat ise klasik riyâziyecilerin tanıdığı şekillerdir (bu sebepten çoğu hâlde, bir kat derecesi verilmediğinde eksi bir derecesini farz etmek münasiptir). Filhakika yalnız *bazı* tiplerin böyle daha ileri "klasik" prensipleri sağladığı, umûmiyetle tiplerin ise "inşâî" kaldığı faydalı nizâmlar bile kurulabilir.

Şunu tebarüz ettirmeye değer ki vahdet esasları inşâî yahut hadsî mantığın kullanılmasını *gerektirmez*. İmtinâ'-ı vasat kanununa ve ihtiyar mütearifesine dayanan klasik riyâziyâtın çoğu, sadece bu iki prensibin (kendi münasip, eksi bir kat'lı şekilleriyle) doğru olduğu farz edilerek vahdet esaslarında icra edilebilir. Bununla beraber tip nazariyesi, birkaç sebepten, bu prensiplerden lüzumsuz oldukları yerde kaçınmayı teşvik eder.

Her şeyden evvel her riyâziyeci bilir ki bir kaziyye daha az farzla ispat edildiğinde daha kuvvetlidir, zîrâ daha çok misale tatbik olunur. İhtiyar mütearifesi ve imtinâ'-ı vasat ile durum farklı değildir: tip nazariyesi, ihtiyar ve imtinâ'-ı vasat gibi klasiklik prensiplerinin sakıt olmaya meyilli olduğu deste toposlarındakiler gibi birçok alâka çekici "mi'yâr dışı" nümûneyi kabul eder. Tahavvül-i muttasıl tip nazariyesi, [Toën ve Vezzosi; Rezk; Lurie]'de tetkik edilenler gibi yüksek toposlarda benzer nümûneleri kabul eder. Böylece bu prensipleri kullanmaktan kaçınırsak, ispat ettiğimiz kaziyyeler bütün bu nümûnelerin içinde muteber olacaktır.

İkinci olarak, tip nazariyesinin ilâve meziyetlerinden biri hesap edilebilir karakteridir. Tip nazariyesi riyâziyât için bir esas olmasına ilâveten, hesabın sûrî bir nazariyesidir ve kudretli bir programlama lisanı olarak ele alınabilir. Bu nokta-i nazardan nizâmın kaideleri, mecmûalar nazariyesinin mütearifeleri gibi keyfî olarak seçilemez: aralarında bütün ispatların program olarak "icra edilmesine" izin veren bir ahenk bulunmalıdır. Tahavvül-i muttasıl tip nazariyesinin getirdiği vahdet ve yüksek istikrâî tipler gibi yeni prensipleri bu nokta-i nazardan henüz tam anlamış değiliz; fakat ana hatlar belirmektedir; meselâ bakınız [Licata ve Harper]. Bununla beraber ihtiyar ve imtinâ'-ı vasat gibi prensiplerin hesap edilebilirliğe esasen zıt olduğu uzun zamandır bilinmektedir; zîrâ onlar, bazı şeylerin, onları hesap etmenin hiçbir yolunu vermeden, var olduğunu çıplakça iddia ederler. Böylece tip nazariyesinin bir hesap nazariyesi olarak karakterini muhafaza etmek için onlardan kaçınmak zarurîdir.

Bereket versin, inşâî muhakeme göründüğü kadar güç değildir. Bazı hâllerde, sadece bazı tarifleri yeniden ifade etmekle, bir kaziyye inşâî kılınabilir ve ispatı daha zarif olur. Bundan başka, vahdet esaslarında bu daha sık vuku buluyor görünmektedir. Meselâ:

1. Mecmûalar nazariyesi esaslarında, tahavvül-i muttasıl nazariyesinin ve makûleler nazariyesinin muhtelif yerlerinde, mütenâhîyi aşan inşaları icra etmek için ihtiyar mütearifesine ihtiyaç vardır. Fakat yüksek istikrâî tiplerle bu inşaları doğrudan ve inşâî olarak kodlayabiliriz. Bilhassa sekizinci babdaki "terkibî" tahavvül-i muttasıl nazariyesinin hiçbir cüz'ü imtinâ'-ı vasat yahut ihtiyar mütearifesi gerektirmez.
2. Mecmûalar nazariyesi esaslarında "tamamen sâdık ve esasen örten her funktor bir makûleler tekâfü'üdür" beyanı ihtiyar mütearifesine mütekâfidir. Fakat vahdet mütearifesiyle bu sadece *doğrudur*; bakınız dokuzuncu bab.
3. Mecmûalar nazariyesinde, mecmûaların ve iyi tertip edilmiş mecmûaların temâsül sınıflarını kanonik olarak temsil eden "adet-i aslî" ve "adet-i tertîbî" mefhûmlarını elde etmek için, belki ihtiyar mütearifesini yahut temel mütearifesini içine alan muhtelif dolambaçlı yollar gerekir. Fakat vahdet ve yüksek istikrâî tiplerle, kâinatı kat' ederek böyle temsilcileri doğrudan elde edebiliriz; bakınız onuncu bab.
4. Mecmûalar nazariyesi esaslarında hakîkî adetlerin Cauchy tevâlîlerinin tekâfü' sınıfları olarak tarifi, iyi davranması için ya imtinâ'-ı vasat kanununu ya da (sayılabilir) ihtiyar mütearifesini gerektirir. Fakat yüksek istikrâî tiplerle bu tarifin iyi davranan ve hiçbir ihtiyar prensibine başvurmayan bir şeklini verebiliriz; bakınız on birinci bab.

Elbette bu sadeleşmeler, yeni usullerin nihayette hakikaten inşâî olmayacağının delili olarak da alınabilir. Bununla beraber tekrar tebarüz ettiririz ki okuyucunun bu kitabı okumak için inşâîlikle ilgilenmesine yahut onun için endişe etmesine lüzum yoktur. Mesele şudur ki yukarıdaki misallerin hepsinde, verdiğimiz nazariye şekli, imtinâ'-ı vasat ve ihtiyar mütearifesinin mevcut farz edilip edilmemesinden müstakil olarak, kendine has üstünlüklere sahiptir. İnşâîlik, elde edilirse, ilâve bir kazanç olacaktır.

Vahdet, yüksek istikrâî tipler, ihtiyar ve imtinâ'-ı vasat gibi yeni prensiplerin eklenmesine dair bu müzakereden sonra, hâsıl olan nizâmın adem-i tenâkuzunu muhafaza edip etmediği merak edilebilir. (Tip nazariyesinin mecmûalar nazariyesine nisbetle asıl meziyetlerinden biri, adem-i tenâkuzunun ispat nazariyesi vasıtalarıyla görülebilmesiydi.) Her esas nizâmında olduğu gibi adem-i tenâkuz izâfî bir suâldir: "neye nisbetle tenâkuzsuz?" Kısa cevap şudur ki bu kitapta mülâhaza edilen bütün inşaların ve mütearifelerin, Voevodsky sayesinde [Kapulkin, Lumsdaine ve Voevodsky], Kan mürekkebleri makûlesinde bir nümûnesi vardır (yüksek istikrâî tipler için bakınız [Lumsdaine ve Shulman]). Böylece Zermelo–Fraenkel ve ihtiyar mütearifesine nisbetle (iç içe vahdetli kâinatlara ihtiyacımız olduğu kadar erişilmez adet-i aslî ile) tenâkuzsuz oldukları bilinmektedir. Bu adem-i tenâkuzun daha an'anevî olarak tip nazariyesine ait bir izahını vermek inşa hâlinde bir iştir (meselâ bakınız [Licata ve Harper; Coquand]).

Tip nazariyesi ameliyelerine dair muhtelif nokta-i nazarları aşağıdaki cedvelde hulâsa ediyoruz.

**Tip nazariyesi ameliyelerine dair nokta-i nazarların mukayesesi**

| Tipler | Mantık | Mecmûalar | Tahavvül-i muttasıl |
| :-- | :-- | :-- | :-- |
| tip | kaziyye | mecmûa | fezâ |
| hadd : tip | ispat | unsur | nokta |
| aileden tip(mütehavvil) | mahmûl | mecmûalar ailesi | lifleme |
| aileden hadd(mütehavvil) : aileden tip(mütehavvil) | şartlı ispat | unsurlar ailesi | kesit |
| boş tip, birim tip | yanlış, doğru | boş mecmûa, boş mecmûayı ihtiva eden mecmûa | boş fezâ, tek nokta |
| birinci tip + ikinci tip | birinci tip yahut ikinci tip | munfasıl ictimâ | mukābil-hâsıl-ı zarb |
| birinci tip × ikinci tip | birinci tip ve ikinci tip | çiftler mecmûası | hâsıl-ı zarb fezâsı |
| birinci tip → ikinci tip | birinci tip ikinci tipi gerektirir | tâbiler mecmûası | tâbi fezâsı |
| Σ (mütehavvil : birinci tip) aileden tip(mütehavvil) | birinci tipin bir mütehavvili vardır ki aileden tip(mütehavvil) | munfasıl mecmû' | küllî fezâ |
| Π (mütehavvil : birinci tip) aileden tip(mütehavvil) | birinci tipin her mütehavvili için aileden tip(mütehavvil) | hâsıl-ı zarb | kesitler fezâsı |
| birinci tipin ayniyet tipi | müsâvât (=) | birinci tipin her unsurunun kendisiyle çiftlerinin mecmûası | tarîk fezâsı |

### Açık meseleler

Riyâziyâtın bu yeni şubesine katkıda bulunmak isteyenler için, birçok alâka çekici açık suâl bulunduğunu bilmek teşvik edici olabilir.

Bunların belki en âcili, Voevodsky'nin [Voevodsky, kâinat çok şekilliliği] içinde ortaya koyduğu, Vahdet Mütearifesinin "inşâîliği" meselesidir. Tip nazariyesinin temel nizâmı Gentzen'in tabiî istidlâlinin bünyesini takip eder. Mantıkî rabıtalar idhâl kaideleriyle tarif edilir ve hesap kaideleriyle meşrûlaştırılan ihraç kaidelerine sahiptir. Bu kalıbı takip ederek ve aslında Gödel'in Dialectica tefsirini tahlîl etmek için tasarlanmış olan Tait'in hesap edilebilirlik usulünü kullanarak, tip nazariyesi için *mi'yârîleşme* hassası gösterilebilir. Bu da kendi sırasında tip denetiminin karar verilebilirliği (tip denetimi ispat denetimine tekabül ettiği için hayatî bir hassadır ve "bir ispatı gördüğümüzde tanıyabilmemiz" gerektiği ileri sürülebilir) ve tabiî adetler tipinin her kapalı haddinin bir rakama irca olunduğu, "kanoniklik hassası" denilen hassa gibi mühim hassaları gerektirir. Bu son hassa ve idhâl ve ihraç kaidelerinin yeknesak bünyesi, tip nazariyesi tâbi genişliği mütearifesi yahut vahdet mütearifesi gibi bir mütearife ile genişletildiğinde kaybolur. Voevodsky, vahdet mütearifesiyle genişletilmiş tip nazariyesi için bu kanoniklik suâline bağlı dakik bir riyâzî tahmin ifade etmiştir: tabiî adetler tipinden kapalı bir hadd verildiğinde, bir rakam ve bu haddin bu rakama müsavi olduğunun bir ispatını — ki bu müsâvât ispatı bizzat vahdet mütearifesini kullanabilir — bulmak her zaman mümkün müdür? Daha umûmî olarak mühim bir mesele, vahdet mütearifesinin inşâî bir meşrûlaştırmasını vermenin mümkün olup olmadığıdır. Ya yüksek istikrâî tipler gibi, tahavvül-i muttasıl ile ilham edilmiş başka inşalar eklenirse? Bu suâller şu an açık kalmaktadır; gerçi cevaplar bulmaya çalışmak için usuller şu an geliştirilmektedir.

Başka bir temel mesele, tabiî adetler gibi, esasen mecmûa olan (yâni munfasıl fezâlar olan), yalnız âdi tarîkler ihtiva eden tiplerle çalışmanın müşkülüdür. Şu an tahavvül-i muttasıl tip nazariyesi fezâları hakikaten ancak tahavvül-i muttasılca tekâfü'e kadar tavsif edebilir; bu da şu demektir ki bu "munfasıl fezâlar" munfasıl fezâlara ancak *tahavvül-i muttasılca mütekâfi* olabilir. Tip nazariyesi bakımından bu şu demektir ki, aksiyete (yansımaya) müsavi olup ona *hükmen* müsavi olmayan birçok tarîk vardır ("hükmen" sözünün mânâsı için bakınız birinci babdaki "tipler ve mecmûalar" bahsi). Bu tahavvül-i muttasılca lâyetegayyerliğin üstünlükleri olmakla beraber, bu "mânâsız" ayniyet hadleri delillere ve inşalara lüzumsuz giriftlikler sokar; binâenaleyh onları ortadan kaldırmanın yahut çökertmenin muntazam bir yolunun bulunması elverişli olurdu.

Daha hususî, fakat ehemmiyeti hiç de daha az olmayan bir mesele, tahavvül-i muttasıl tip nazariyesi ile yüksek makûleler nazariyesi ve tahavvül-i muttasıl nazariyesinin kesişiminde şu an yapılmakta olan *yüksek toposlar* hakkındaki tetkikler arasındaki münasebettir. Her iki mevzûa aşina olanlar arasında, bunların sıkı sıkıya bağlı olduğuna dair gittikçe artan bir kanaat vardır. Meselâ vahdetli bir kâinat mefhûmu bir nesne sınıflandırıcısı mefhûmuyla örtüşmeli, yüksek istikrâî tipler ise mahallî takdim edilebilirliğin "unsurî" bir aksi olmalıdır. Daha umûmî olarak, tıpkı hadsî yüksek mertebe mantığın âdi bir-toposların "dahilî lisanı" olması gibi, tahavvül-i muttasıl tip nazariyesi de (nihâyetsiz, bir)-toposların "dahilî lisanı" olmalıdır. Bu umûmî mutabakata rağmen tafsilât henüz işlenmemiştir — bilhassa tutarlılık ve katılık suâllerinin ele alınması lâzımdır — ve bunu yapmak şüphesiz her iki mefhûma dair daha ileri basîretlere yol açacaktır.

Fakat yapılacak işin açık ara en geniş sahası, gündelik riyâziyâtın bu yeni nizâmda devam eden sûrîleştirilmesidir. Temel tahavvül-i muttasıl nazariyesinden ve makûleler nazariyesinden bazı vakıaların sûrîleştirilmesindeki yakın zamandaki muvaffakiyetler teşvik edici olmuştur; bunların bazıları sekizinci ve dokuzuncu bablarda tarif edilmiştir. Fakat açıktır ki daha yapılacak çok iş vardır.

Tahavvül-i muttasıl tip nazariyesi cemiyeti <http://homotopytypetheory.org> adresinde bir internet sahifesi ve müşterek bir günlük ile bir müzakere elektronik mektup listesi idare etmektedir. Yeni gelenlere her zaman hoş geldiniz denir!

### Bu kitap nasıl okunmalı

Bu kitap iki cüze ayrılmıştır. Birinci cüz, "Esaslar", tahavvül-i muttasıl tip nazariyesinin temel mefhûmlarını geliştirir. Bu, muayyen mevzûların inkişâfının üzerine bina edildiği ve vahdet esasları yaklaşımını anlamak için lâzım olan riyâzî esastır. Bir programcı için bu "kütüphane kodu"dur. Vahdet esasları yeni ve farklı bir nevi riyâziyât olduğundan, temel mefhûmlarına alışmak biraz zaman alır; bu sebepten birinci cüz oldukça geniştir.

İkinci cüz, "Riyâziyât", vahdet esaslarıyla riyâziyâtın dört ayrı sahasında yapabileceğimiz yeni şeylerden bazılarını göstermek için birinci cüzün temel mefhûmları üzerine bina eden dört babdan ibarettir: tahavvül-i muttasıl nazariyesi (sekizinci bab), makûleler nazariyesi (dokuzuncu bab), mecmûalar nazariyesi (onuncu bab) ve hakîkî tahlîl (on birinci bab). İkinci cüzdeki bablar, ara sıra biri ötekinde ispat edilmiş bir yardımcı kaziyyeyi kullansa da, birbirinden aşağı yukarı müstakildir.

Vahdet esaslarını ciddî olarak anlamak ve onda çalışabilmek isteyen bir okuyucu, nihayet birinci cüzün çoğunu okuyup anlamak zorunda kalacaktır. Bununla beraber, sadece vahdet esaslarının bir tadına bakmak ve neler yapabileceğini görmek isteyen bir okuyucu, ikinci cüzdeki "asıl maksada" varmadan evvel iki yüz sahifeden fazlasını işlemek zorunda kalmaktan anlaşılır bir şekilde çekinebilir. Bereket versin, ikinci cüzdeki babları okumak için birinci cüzün hepsi lâzım değildir. İkinci cüzdeki her bab, mevzûunun kısa bir umûmî manzarası, vahdet esaslarının ona katacakları ve birinci cüzden lâzım olan zemin ile başlar; böylece cesur okuyucu en sevdiği mevzûa ait münasip baba hemen geçebilir. İkinci cüzdeki bir yahut daha fazla babı bundan daha derinden anlamak isteyen, fakat birinci cüzün hepsini okumaya hazır olmayanlar için burada birinci cüzün kısa bir hulâsasını, hangi kısımlarının ikinci cüzdeki hangi bablar için lâzım olduğuna dair kayıtlarla beraber veriyoruz.

Birinci bab, herhangi bir tahavvül-i muttasıl tefsirinden evvel, tip nazariyesinin temel mefhûmları hakkındadır. Martin-Löf tip nazariyesine aşina bir okuyucu, kullandığımız nazariyenin hususiyetlerini almak için onu çabucak gözden geçirebilir. Bununla beraber, tip nazariyesinde tecrübesi olmayan okuyucuların birinci babı okumaları lâzım olacaktır; zîrâ tip nazariyesi ile mecmûalar nazariyesi gibi başka esaslar arasında birçok ince fark vardır.

İkinci bab, tip nazariyesine dair tahavvül-i muttasıl nokta-i nazarını, bu görüşü destekleyen temel mefhûmlarla beraber tanıtır ve birinci babdaki tip nazariyesinin her bileşeninin tahavvül-i muttasılî davranışını tarif eder. Aynı zamanda tahavvül-i muttasıl tip nazariyesinin iki temel yeniliğinden birincisi olan *vahdet mütearifesini* tanıtır. Böylece oldukça temeldir ve herkesi, bilhassa müsâvât bahsinden tekâfü'ler bahsine kadar olan kısımları okumaya teşvik ediyoruz.

Üçüncü bab, mantığı tahavvül-i muttasıl tip nazariyesinde nasıl temsil ettiğimizi ve onun klasik mantıkla olduğu kadar inşâî ve hadsî mantıkla da irtibatını tarif eder. Burada imtinâ'-ı vasat kanununu, ihtiyar mütearifesini ve kaziyyevî yeniden boyutlandırma mütearifesini (gerçi kitabın geri kalanında bunların hiçbirini çoğunlukla farz etmemiz gerekmez), ve aynı zamanda an'anevî mantığı temsil etmek için elzem olan *kaziyyevî kat'*ı tarif ederiz. Bu bab onuncu ve on birinci bablar için elzem zemindir, dokuzuncu bab için daha az mühimdir, sekizinci bab için ise o kadar lüzumlu değildir.

Dördüncü ve beşinci bablar iki hususî mevzûu tafsilâtıyla tetkik eder: tekâfü'ler (ve alâkalı mefhûmlar) ve umûmîleştirilmiş istikrâî tarifler. Bunlar kendi başlarına mühim mevzûlar olmakla ve tahavvül-i muttasıl tip nazariyesinin daha derin anlaşılmasını sağlamakla beraber, çoğunlukla ikinci cüz için lüzumlu değildir. Dördüncü babdan ancak birkaç yardımcı kaziyye burada orada kullanılır; beşinci babdaki Boole ve tabiî adetler, kat'î müsbet istikrâ ve umûmîleştirmeler bahislerindeki umûmî müzakereler ise altıncı bab için lâzım olan sezişi sağlamakta faydalıdır. Umûmîleştirmeler bahsinde müzakere edilen umûmîleştirilmiş istikrâî tarif çeşitleri onuncu ve on birinci babların birkaç yerinde de kullanılır.

Altıncı bab, tahavvül-i muttasıl tip nazariyesinin ikinci temel yeniliğini — *yüksek istikrâî tipleri* — birçok misalle tanıtır. Yüksek istikrâî tipler sekizinci babın asıl tetkik nesnesidir ve bazı hususî olanları onuncu ve on birinci bablarda mühim roller oynar. Dokuzuncu bab için o kadar lüzumlu değildir; gerçi bir misal Rezk tamamlaması bahsinde kullanılır.

Nihayet yedinci bab, buud-sayısı tahavvül-i muttasıl tiplerini ve buud-sayısı muttasıl tipler gibi alâkalı mefhûmları müzakere eder. Bu mefhûmlar sekizinci bab için mühimdir, fakat ikinci cüzün geri kalanında o kadar mühim değildir; gerçi bazı yardımcı kaziyyelerin eksi bir hâli, onuncu babdaki kuyu sıralı tipler ve ön-topos bahsinde kullanılır.

Bu, birinci cüzü tamamlar. Yukarıda bahsedildiği gibi ikinci cüz, her biri vahdet esaslarının hususî bir mevzûa neler arz edebileceğini tarif eden, büyük ölçüde birbiriyle alâkasız dört babdan ibarettir.

İkinci cüzdeki bablardan sekizinci bab (Tahavvül-i muttasıl nazariyesi) belki en köklü olanıdır. Vahdet esaslarının, tahavvül-i muttasıl tiplerinin vaz'î fezâlar yahut başka bir mecmûalar nazariyesi nümûnesi kullanılarak inşa edilmek yerine temel nesneler (yâni tipler) olduğu, tahavvül-i muttasıl nazariyesine pek farklı bir "terkibî" yaklaşımı vardır. Bu, cebrî hendese-i vaz'iyyedeki klasik kaziyyeler için yeni ispat üslûplarına imkân verir; bunlardan, dâirenin birinci tahavvül-i muttasıl zümresinin tam adetler olmasından Freudenthal ta'lîk kaziyyesine kadar bir numûne arz ediyoruz.

Dokuzuncu babda (Makûleler nazariyesi), vahdet mütearifesinin *müsâvât temâsüldür* prensibine bağlı kalarak bazı temel (bir-)makûleler nazariyesi geliştiriyoruz. Bunun, bütün tariflerin ve inşaların makûleler tekâfü'ü altında kendiliğinden lâyetegayyer olmasını temin eden hoş bir tesiri vardır: filhakika mütekâfi tipler nasıl müsavi ise, mütekâfi makûleler de müsavidir. (Bunun yüksek makûleler nazariyesiyle ve yüksek topos nazariyesiyle de irtibatları vardır.)

Onuncu bab (Mecmûalar nazariyesi), vahdet esaslarında mecmûaları tetkik eder. Mecmûalar makûlesi mûtat hassalarına sahiptir; binâenaleyh tahavvül-i muttasılî yahut yüksek makûlî bünyelere ihtiyaç duymayan her riyâziyât için bir esas sağlar. Ayrıca vahdetin adet-i aslîleri ve adet-i tertîbîleri biraz daha hoş kıldığını ve yüksek istikrâî tiplerin, Zermelo–Fraenkel mecmûalar nazariyesinin mûtat mütearifelerini sağlayan birikimli bir silsile-i merâtib hâsıl ettiğini müşahede ediyoruz.

On birinci babda (Hakîkî adetler), Dedekind hakîkî adetlerinin inşasını hulâsa ediyor, sonra yüksek istikrâî tiplerin, inşâî riyâziyâtta Cauchy hakîkî adetlerine bağlı bazı meselelerden kaçınan bir tarifine imkân verdiğini müşahede ediyoruz. Sonra Conway'in fevkü'l-hakîkî adetlerine benzer bir yaklaşımın taslağını çiziyoruz.

Bu kitaptaki her bab, mümkün olduğu kadar, tarihî mülâhazaları, edebiyata atıfları ve neticelerin sahiplerine nisbetini toplayan bir Notlar bahsiyle biter. Okuyucunun vahdet esaslarında riyâziyât yapmaya aşinalık kazanmasına yardım etmek için her babın sonuna Temrinler de koyduk.

Nihayet hatırlatalım ki bu kitap, pek çok kimsenin büyük çaplı bir müşterek gayreti olarak yazılmıştır. Istılahta ve işarette tutarlılığa ermek ve riyâziyâtı mantıkî olarak akan doğru bir sıraya koymak için elimizden geleni yaptık; fakat bazı kusurların kalmış olması pek muhtemeldir. Böyle her uygunsuzluk için okuyucunun affını diler, gelecek tab' için ıslah tekliflerini memnuniyetle karşılarız.

---

## İsimler cedveli (düsturlardaki kelimeler)

Sağdaki sütun aslındaki işaretin **adını** verir; düsturların kendisinde harf kullanılmamıştır. Σ (mecmû'), Π (hâsıl-ı zarb), × (zarb), + (cem'), → (tâbi tipi), = (ayniyet), ≃ (tekâfü'), :≡ (tarif ile müsâvât) ve ∙ (tarîklerin terkibi) ameliye işaretleri olduğu için bırakılmıştır.

| Tercümedeki isim | Mânâsı | Aslındaki işaretin adı |
| :-- | :-- | :-- |
| hadd | bir tipin haddi (unsuru, noktası, ispatı) | Latin küçük "a" |
| tip; birinci tip, ikinci tip | tipler | Latin büyük "a", "be" |
| birinci tatbik, ikinci tatbik | fezâlar arasında muttasıl tatbikler | Latin küçük "ef", "ge" |
| birinci fezâ, ikinci fezâ | vaz'î fezâlar | Latin büyük "iks", "ye" |
| tahavvül | iki tatbik arasındaki tahavvül-i muttasıl | Latin büyük "haş" |
| nokta | birinci fezânın noktası | Latin küçük "iks" |
| tarîk | ayniyet tipinin bir haddi; noktalar arasında yol | Latin küçük "pe" |
| ayniyet tipi | bir tipin iki nesnesinin aynîleştirmelerinin tipi | "Id", altında tipin adı |
| kâinat | tiplerin tipi | çift çizgili Latin büyük "u" |
| merkez noktası | iki buudlu kürenin tek noktası | Latin küçük "be" |
| birinci tarîk, ikinci tarîk | simit sathının iki tarîki | Latin küçük "pe", "kû" |
| Temâsül | temâsüller tipi | "Iso" |
| gidiş, dönüş | temâsülün iki tâbisi | Latin küçük "ef", "ge" |
| birinci unsur, ikinci unsur | birinci tipin ve ikinci tipin unsurları | Latin küçük "iks", "ye" |
| münasebet | ihtiyar mütearifesindeki münasebet | Latin büyük "er" |
| seçici | ihtiyar mütearifesinin verdiği tâbi | Latin küçük "ef" |
| aileden tip(mütehavvil) | birinci tipin bir unsuruna bağlı tipler ailesi | Latin büyük "be", parantez içinde "iks" |
| aileden hadd(mütehavvil) | o ailenin bir kesiti | Latin küçük "be", parantez içinde "iks" |
| boş tip, birim tip | sıfır ve bir unsurlu tipler | "0", "1" |
| buud-sayısı | tahavvül-i muttasıl tipinin buudu | Latin küçük "en" |
| eksi bir | mahz kaziyyelerin buudu | "−1" |
| dâirenin birinci tahavvül-i muttasıl zümresi = tam adetler | sekizinci babın ilk kaziyyesi | "π₁(S¹) = ℤ" |

---

## Istılah cedveli

Esas: aynı depodaki `lugat/kok_istilahlar.tsv` (dal `claude/project-thread-jvwo8g`). Orada bulunmayanlar **teklif** diye işaretlenmiştir. Bu cedvel, aynı kitabın diğer bablarını tercüme edenler için de esastır.

| İngilizce | Bu tercümedeki karşılık | Dayanak |
| :-- | :-- | :-- |
| homotopy | tahavvül-i muttasıl | lügat, teklif |
| type / term | tip / hadd | teklif ("hadd" mantığın kadîm ıstılahıdır) |
| type theory | tip nazariyesi | teklif |
| univalence / univalence axiom | vahdet / vahdet mütearifesi | teklif ("axiom" = mütearife, kadîm) |
| univalent foundations | vahdet esasları | teklif |
| equivalence / equivalent | tekâfü' / mütekâfi | teklif |
| identity / identification | ayniyet / aynîleştirme | lügat ("identity" = ayniyet), teklif |
| equality | müsâvât | kadîm |
| isomorphism / isomorphic | temâsül / temâsül eden | lügat, teklif |
| path / path space | tarîk / tarîk fezâsı | teklif; "space" = fezâ, kadîm |
| space / point | fezâ / nokta | lügat, kadîm |
| continuous map | muttasıl tatbik | lügat ("continuous" = muttasıl), "tatbik" teklif |
| groupoid / ∞-groupoid | zümremsi / nihâyetsiz zümremsi | teklif ("group" = zümre, kadîm) |
| higher inductive type | yüksek istikrâî tip | lügat ("induction" = istikrâ), teklif |
| universe / small type | kâinat / küçük tip | teklif |
| set / set theory | mecmûa / mecmûalar nazariyesi | lügat, teklif |
| category / category theory | makûle / makûleler nazariyesi | lügat, teklif |
| topos / sheaf | topos / deste | lügat, teklif |
| homology / homological algebra | tecânüs / tecânüs cebri | lügat, teklif |
| algebraic topology | cebrî hendese-i vaz'iyye | lügat ("topology" = hendese-i vaz'iyye), teklif |
| proof assistant | ispat muâvini | teklif |
| computer | hâsib | lügat, teklif |
| algorithm | hârizmî | lügat, teklif |
| formal / informal | sûrî / gayr-ı sûrî | lügat, kadîm |
| constructive / intuitionistic | inşâî / hadsî | "hadsî" lügat, teklif; "inşâî" teklif |
| proposition / mere proposition | kaziyye / mahz kaziyye | lügat, kadîm; "mahz" teklif |
| truncation / truncated | kat' / kat'lı | teklif |
| axiom of choice | ihtiyar mütearifesi | teklif |
| law of excluded middle | imtinâ'-ı vasat kanunu | teklif |
| consistency / consistent | adem-i tenâkuz / tenâkuzsuz | lügat, kadîm |
| contradiction (paradox) | mütenâkız | kadîm |
| predicative | tahmîlî | teklif |
| simplicial set | basît mecmûa | teklif |
| model category | nümûne makûlesi | teklif |
| fibration / section / total space | lifleme / kesit / küllî fezâ | teklif |
| coproduct / product | mukābil-hâsıl-ı zarb / hâsıl-ı zarb | teklif; hâsıl-ı zarb kadîm |
| disjoint union / disjoint sum | munfasıl ictimâ / munfasıl mecmû' | lügat ("discrete" = munfasıl), teklif |
| contractible | büzülebilir | teklif |
| colimit | mukābil-nihâyet | lügat, teklif |
| suspension | ta'lîk | teklif |
| localization / completion / spectrification | mahallîleştirme / tetmîm / tayflaştırma | teklif |
| invariant | lâyetegayyer | teklif |
| CW complex | CW mürekkebi | teklif ("complex" = mürekkeb, lügat) |
| cardinal / ordinal number | adet-i aslî / adet-i tertîbî | lügat, kadîm |
| real numbers / surreal numbers | hakîkî adetler / fevkü'l-hakîkî adetler | lügat, teklif |
| sequence | tevâlî | lügat, teklif |
| convergence | tekārüb | lügat, kadîm |
| normalization / canonicity | mi'yârîleşme / kanoniklik | lügat ("standard" = mi'yâr), teklif |
| functor / fully faithful / essentially surjective | funktor / tamamen sâdık / esasen örten | teklif |
| proof by contradiction | hulf ile ispat | kadîm |
| predicate | mahmûl | kadîm |
